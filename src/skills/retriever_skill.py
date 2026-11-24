import os
import urllib.request
from collections import defaultdict
import json
import logging
from typing import Any, Dict, List, Optional
from langchain_core.tools import tool
from rank_bm25 import BM25Okapi
from flashrank import Ranker, RerankRequest
from scripts.ingest import get_chroma_client

logger = logging.getLogger(__name__)

_CLIENT = None
_COLLECTION = None
_RANKER = None
_BM25_CACHE = {}


def _resolve_document_name(document_filter: str) -> Optional[str]:
    """Resolve a fuzzy title, partial name, or arXiv ID to exact catalog document_name."""
    if not document_filter:
        return None
    try:
        from src.skills.catalog_skill import query_catalog_sql
        escaped = document_filter.replace("'", "''")
        # Exact match
        rows = query_catalog_sql(f"SELECT document_name FROM catalog WHERE lower(document_name) = lower('{escaped}')")
        if rows:
            return rows[0]["document_name"]
        # Substring in title or document_name
        rows = query_catalog_sql(f"SELECT document_name FROM catalog WHERE lower(title) LIKE lower('%{escaped}%') OR lower(document_name) LIKE lower('%{escaped}%')")
        if rows:
            return rows[0]["document_name"]
    except Exception:
        pass
    return None


def _get_collection(collection_name: str = "document_knowledge"):
    global _CLIENT, _COLLECTION
    if _CLIENT is None:
        _CLIENT = get_chroma_client()
    try:
        if _COLLECTION is not None and _COLLECTION.name == collection_name:
            _COLLECTION.count()  # Validate existing handle
            return _COLLECTION
    except Exception:
        _COLLECTION = None
    _COLLECTION = _CLIENT.get_or_create_collection(collection_name)
    return _COLLECTION


def _get_ranker() -> Optional[Ranker]:
    """Lazily load and cache the lightweight FlashRank ONNX cross-encoder."""
    global _RANKER
    if _RANKER is None:
        try:
            _RANKER = Ranker(model_name="ms-marco-TinyBERT-L-2-v2", cache_dir="data/.cache_flashrank")
        except Exception as e:
            logger.warning(f"Could not initialize FlashRank Ranker: {e}")
            _RANKER = None
    return _RANKER


def _get_bm25_for_data(data: Dict[str, Any]) -> Optional[BM25Okapi]:
    """Build or retrieve cached BM25 model for a set of documents."""
    docs = data.get("documents", [])
    if not docs:
        return None
    tokenized_corpus = [doc.lower().split() for doc in docs]
    return BM25Okapi(tokenized_corpus)


def _rerank_with_jev(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = 4,
    threshold: float = 0.40,
    api_key: Optional[str] = None,
) -> Optional[List[Dict[str, Any]]]:
    """Rerank and noise-prune candidates using Jev's System-1 3-way 'choice' rubric.
    
    Evaluates:
      - 'strong': Directly provides empirical evidence, benchmarks, or definitions answering the query.
      - 'partial': Mentions the entity or topic in passing without specific details.
      - 'wrong': Unrelated topic, distractor, or incidental match.
    
    Pruning Gate: Drops candidates with score = P(strong) + 0.5 * P(partial) < threshold.
    """
    key = api_key or os.environ.get("JEV_API_KEY", "").strip()
    if not key:
        try:
            from src.config import get_settings
            key = (get_settings().JEV_API_KEY or "").strip()
        except Exception:
            pass
    if not key:
        return None

    if not candidates:
        return []

    # Limit pool size to top 15 candidates to keep API state concise and fast
    pool = candidates[:15]

    state_parts = [f"USER QUERY: {query.strip()}\n\nCANDIDATE PASSAGES:"]
    questions = {}
    for idx, c in enumerate(pool):
        cid = c.get("chunk_id", f"doc_{idx}")
        doc_name = c.get("document_name", "Doc")
        text_snippet = c.get("chunk_content", "")[:700].strip()
        state_parts.append(f"[{cid}] (from {doc_name}):\n{text_snippet}")

        questions[f"cand_{idx}"] = {
            "type": "choice",
            "options": ["strong", "partial", "wrong"],
            "instructions": f"How well does passage [{cid}] provide factual evidence to answer: '{query[:200]}'? 'strong': directly answers core question with facts/numbers; 'partial': related topic or background without specifics; 'wrong': irrelevant or incidental match."
        }

    payload = {
        "model": "jev-latest",
        "state": "\n\n---\n\n".join(state_parts)[:30000],
        "questions": questions,
    }

    try:
        req = urllib.request.Request(
            "https://api.typesafe.ai/v1/systemone",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        answers = result.get("answers", {})
        scored_candidates = []
        for idx, c in enumerate(pool):
            ans = answers.get(f"cand_{idx}", {})
            probs = ans.get("distribution") or ans.get("choice_probabilities") or {}
            if not probs and "choice" in ans:
                choice_str = ans["choice"]
                probs = {choice_str: 1.0}

            p_strong = float(probs.get("strong", 0.0))
            p_partial = float(probs.get("partial", 0.0))
            p_wrong = float(probs.get("wrong", 0.0))

            if p_strong == 0.0 and p_partial == 0.0 and p_wrong == 0.0:
                choice_str = ans.get("choice", "partial")
                p_strong = 1.0 if choice_str == "strong" else 0.0
                p_partial = 1.0 if choice_str == "partial" else 0.0
                p_wrong = 1.0 if choice_str == "wrong" else 0.0

            calc_score = round(p_strong + 0.5 * p_partial, 3)

            chunk_copy = dict(c)
            chunk_copy["rerank_score"] = calc_score
            chunk_copy["rerank_rubric"] = ans.get("choice", "strong" if calc_score >= 0.7 else "partial")
            chunk_copy["reranker_engine"] = "jev_system_one"

            # Noise pruning gate: drop if score < threshold
            if calc_score >= threshold:
                scored_candidates.append(chunk_copy)

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

        # If pruning was too aggressive and left 0 candidates, return the top from pool with scores
        if not scored_candidates and pool:
            for idx, c in enumerate(pool[:top_k]):
                c_copy = dict(c)
                c_copy["rerank_score"] = 0.35
                scored_candidates.append(c_copy)

        return scored_candidates[:top_k]
    except Exception as e:
        logger.warning(f"Jev decision reranking encountered exception, falling back to FlashRank: {e}")
        return None


def retrieve_knowledge_chunks(
    query: str,
    top_k: int = 4,
    document_filter: Optional[str] = None,
    collection_name: str = "document_knowledge",
    reranker: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve document chunks using a two-stage Hybrid (Dense + BM25) + FlashRank Reranker pipeline."""
    collection = _get_collection(collection_name)
    total_count = collection.count()
    if total_count == 0:
        return []

    resolved_doc = _resolve_document_name(document_filter) if document_filter else None
    target_filter = resolved_doc or document_filter
    where_filter = {"document_name": target_filter} if target_filter else None

    # Candidate pool size for hybrid fusion (stage 1)
    candidate_k = max(top_k * 3, 25)
    candidate_k = min(candidate_k, total_count)

    # -------------------------------------------------------------
    # Stage 1A: Dense Vector Retrieval (ChromaDB)
    # -------------------------------------------------------------
    query_params = {
        "query_texts": [query],
        "n_results": candidate_k,
    }
    if where_filter:
        query_params["where"] = where_filter

    results = collection.query(**query_params)

    # Resilient fallback: if where filter returned zero results, retry without filter
    if (not results or not results["documents"] or not results["documents"][0]) and where_filter:
        fallback_params = {
            "query_texts": [query],
            "n_results": candidate_k,
        }
        results = collection.query(**fallback_params)

    dense_candidates: List[Dict[str, Any]] = []
    dense_id_ranks: Dict[str, int] = {}
    if results and results.get("documents") and results["documents"][0]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        ids = results["ids"][0] if results.get("ids") else [""] * len(docs)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

        for rank, (doc, meta, cid, dist) in enumerate(zip(docs, metas, ids, distances)):
            meta = meta or {}
            chunk_obj = {
                "chunk_id": meta.get("chunk_id", cid),
                "document_name": meta.get("document_name", "Unknown"),
                "header_path": meta.get("header_path", "/"),
                "chunk_content": doc,
                "distance": dist,
            }
            dense_candidates.append(chunk_obj)
            dense_id_ranks[cid] = rank

    # -------------------------------------------------------------
    # Stage 1B: Sparse BM25 Retrieval (Exact Keyword Matching)
    # -------------------------------------------------------------
    bm25_candidates: List[Dict[str, Any]] = []
    bm25_id_ranks: Dict[str, int] = {}

    try:
        if where_filter:
            all_chunks_data = collection.get(where=where_filter)
            if not all_chunks_data or not all_chunks_data.get("ids"):
                all_chunks_data = collection.get()
        else:
            all_chunks_data = collection.get()

        if all_chunks_data and all_chunks_data.get("documents"):
            all_docs = all_chunks_data["documents"]
            all_metas = all_chunks_data["metadatas"] or [{}] * len(all_docs)
            all_ids = all_chunks_data["ids"]

            bm25_model = _get_bm25_for_data(all_chunks_data)
            if bm25_model:
                query_tokens = query.lower().split()
                if query_tokens:
                    bm25_scores = bm25_model.get_scores(query_tokens)
                    ranked_indices = sorted(
                        range(len(bm25_scores)),
                        key=lambda i: bm25_scores[i],
                        reverse=True,
                    )[:candidate_k]

                    for rank, idx in enumerate(ranked_indices):
                        cid = all_ids[idx]
                        meta = all_metas[idx] or {}
                        chunk_obj = {
                            "chunk_id": meta.get("chunk_id", cid),
                            "document_name": meta.get("document_name", "Unknown"),
                            "header_path": meta.get("header_path", "/"),
                            "chunk_content": all_docs[idx],
                            "distance": 0.0,
                            "bm25_score": float(bm25_scores[idx]),
                        }
                        bm25_candidates.append(chunk_obj)
                        bm25_id_ranks[cid] = rank
    except Exception as e:
        logger.warning(f"BM25 retrieval encountered exception, falling back to dense only: {e}")

    # -------------------------------------------------------------
    # Stage 1C: Reciprocal Rank Fusion (RRF)
    # -------------------------------------------------------------
    all_chunks_map: Dict[str, Dict[str, Any]] = {}
    for c in dense_candidates:
        all_chunks_map[c["chunk_id"]] = c
    for c in bm25_candidates:
        if c["chunk_id"] not in all_chunks_map:
            all_chunks_map[c["chunk_id"]] = c

    rrf_scores: Dict[str, float] = defaultdict(float)
    RRF_K = 60
    for cid in all_chunks_map.keys():
        if cid in dense_id_ranks:
            rrf_scores[cid] += 1.0 / (RRF_K + dense_id_ranks[cid] + 1)
        if cid in bm25_id_ranks:
            rrf_scores[cid] += 1.0 / (RRF_K + bm25_id_ranks[cid] + 1)

    sorted_candidate_ids = sorted(
        all_chunks_map.keys(),
        key=lambda cid: rrf_scores[cid],
        reverse=True,
    )[:candidate_k]

    fused_candidates = [all_chunks_map[cid] for cid in sorted_candidate_ids]

    if not fused_candidates:
        return []

    # -------------------------------------------------------------
    # Stage 2: Precision Reranking (Jev Decision Reranker with FlashRank Fallback)
    # -------------------------------------------------------------
    # Use Jev Decision Reranker if explicitly requested or enabled in environment
    should_use_jev = (reranker == "jev") or (reranker is None and os.environ.get("USE_JEV_RERANKER") == "1")
    if should_use_jev:
        jev_reranked = _rerank_with_jev(query=query, candidates=fused_candidates, top_k=top_k)
        if jev_reranked is not None:
            return jev_reranked

    # Fallback / Default: local FlashRank cross-encoder
    ranker = _get_ranker()
    if ranker and len(fused_candidates) > 0:
        try:
            passages = [
                {
                    "id": c["chunk_id"],
                    "text": c["chunk_content"],
                    "meta": c,
                }
                for c in fused_candidates
            ]
            rerank_request = RerankRequest(query=query, passages=passages)
            reranked_results = ranker.rerank(rerank_request)

            final_chunks: List[Dict[str, Any]] = []
            for item in reranked_results[:top_k]:
                chunk = dict(item["meta"])
                chunk["rerank_score"] = float(item.get("score", 0.0))
                final_chunks.append(chunk)

            return final_chunks
        except Exception as e:
            logger.warning(f"FlashRank reranking failed, falling back to RRF candidates: {e}")

    return fused_candidates[:top_k]


@tool("knowledge_retriever")
def retriever_tool(
    query: str,
    top_k: int = 4,
    document_filter: Optional[str] = None,
) -> str:
    """Retrieve content chunks from research papers using Hybrid (Chroma + BM25) search and FlashRank reranking.
    
    Returns high-relevance passages with section metadata:
    - document_name (e.g. 'ICLR_2023_REACT', 'ARXIV_REFLEXION_2023')
    - header_path (e.g. '/INTRODUCTION', '/EXPERIMENTS/ALFWORLD')
    - chunk_content (the text passage)
    - rerank_score (FlashRank cross-encoder relevance score)

    Use document_filter to restrict retrieval to a specific document (e.g. document_filter='ICLR_2023_REACT').
    Defaults to returning top 4 high-precision chunks (4 chunks per paper = 8 total for a 2-paper comparison).
    """
    try:
        chunks = retrieve_knowledge_chunks(query=query, top_k=top_k, document_filter=document_filter)
        if not chunks:
            return f"No relevant passages found for query '{query}'."
        return json.dumps(chunks, indent=2)
    except Exception as e:
        return f"Error retrieving knowledge chunks: {e}"
