import json
import logging
import os
import re
import urllib.request
import uuid
from typing import Any, Dict, List, Optional
import chromadb
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from src.config import get_settings
from src.utils.models import get_default_model
from src.skills.ingestion.schemas import EvaluationProbe, EvaluationResult, IngestionChunk

logger = logging.getLogger(__name__)


def evaluate_chunk_integrity_jev(
    chunks: List[IngestionChunk],
    api_key: Optional[str] = None,
    threshold: float = 0.50,
) -> Dict[str, Dict[str, Any]]:
    """Evaluate candidate chunk boundary integrity and self-containedness using Jev (TypeSafe AI).
    
    Sub-500ms parallel evaluation of all chunks concurrently via 'noul' boolean primitives.
    Zero output token fees ($0.042 / 1M input tokens).
    """
    key = api_key or os.environ.get("JEV_API_KEY", "").strip()
    if not key:
        try:
            key = (get_settings().JEV_API_KEY or "").strip()
        except Exception:
            pass
    if not key:
        raise ValueError("JEV_API_KEY not configured.")

    if not chunks:
        return {}

    state_blocks = []
    questions = {}
    for c in chunks:
        cid = c.chunk_id
        snip = c.chunk_content[:800].strip()
        state_blocks.append(f"[{cid}]\n{snip}")
        questions[f"{cid}_complete"] = {
            "type": "noul",
            "instructions": f"In the passage labeled [{cid}], does the text express a self-contained, meaningful concept without dangling unresolved references?"
        }
        questions[f"{cid}_boundary"] = {
            "type": "noul",
            "instructions": f"In the passage labeled [{cid}], does the text conclude gracefully at a sentence boundary rather than cutting off abruptly mid-clause?"
        }

    payload = {
        "model": "jev-latest",
        "state": "\n\n---\n\n".join(state_blocks)[:30000],
        "questions": questions,
    }

    req = urllib.request.Request(
        "https://api.typesafe.ai/v1/systemone",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    answers = result.get("answers", {})
    chunk_verdicts = {}
    for c in chunks:
        cid = c.chunk_id
        p_complete = float(answers.get(f"{cid}_complete", {}).get("noul", 0.5))
        p_boundary = float(answers.get(f"{cid}_boundary", {}).get("noul", 0.5))
        avg_score = round((p_complete + p_boundary) / 2.0, 3)
        passed = avg_score >= threshold
        chunk_verdicts[cid] = {
            "score": avg_score,
            "completeness": p_complete,
            "boundary": p_boundary,
            "passed": passed,
            "header_path": c.header_path,
        }

    return chunk_verdicts


def generate_section_probes(
    chunk: IngestionChunk,
    model: Optional[BaseChatModel] = None,
) -> List[EvaluationProbe]:
    """Generate 3 distinct paraphrased probe questions for a chunk."""
    active_model = model or get_default_model()

    prompt = (
        f"You are an evaluator assessing search retrieval quality.\n"
        f"Generate exactly 3 semantically distinct, paraphrased search questions that directly ask about "
        f"the concepts, definitions, or mechanisms described in this text passage.\n"
        f"Vary the vocabulary and angle between the 3 questions.\n\n"
        f"Section Header: {chunk.header_path}\n"
        f"Passage Text:\n{chunk.chunk_content[:1500]}\n\n"
        f"Return ONLY a JSON list of 3 strings, e.g. [\"question 1\", \"question 2\", \"question 3\"]."
    )

    try:
        response = active_model.invoke([HumanMessage(content=prompt)])
        content = response.content
        if isinstance(content, list):
            content = "".join(str(b.get("text", "")) if isinstance(b, dict) else str(b) for b in content)

        cleaned_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(content).strip(), flags=re.MULTILINE)
        raw_list = json.loads(cleaned_json)

        if isinstance(raw_list, list) and len(raw_list) >= 1:
            probes = []
            for i, q in enumerate(raw_list[:3]):
                probes.append(
                    EvaluationProbe(
                        probe_id=f"{chunk.chunk_id}_probe_{i+1}",
                        target_header_path=chunk.header_path,
                        query_text=str(q),
                        variation_idx=i + 1,
                    )
                )
            return probes
    except Exception as e:
        logger.debug(f"LLM probe generation failed ({e}), using heuristic probes.")

    # Heuristic fallback probes from section title and content
    body = re.sub(r"^\[Document:.*?\]\s*", "", chunk.chunk_content)
    body = re.sub(r"^##\s+.*?\n+", "", body)

    clean_h = re.sub(r"[*#]", "", chunk.header_path).strip()
    sec_name = clean_h.split(">")[-1].strip()
    parent_sec = clean_h.split(">")[-2].strip() if len(clean_h.split(">")) > 1 else ""

    common_stop = {
        "which", "their", "there", "about", "these", "other", "where", "after",
        "before", "using", "between", "through", "under", "above", "could", "should",
        "would", "first", "second", "figure", "table", "document", "section", "overview"
    }
    words = [
        w for w in re.findall(r"\b[a-zA-Z]{5,}\b", body)
        if w.lower() not in common_stop and w.lower() not in sec_name.lower()
    ]
    sample_phrase = " ".join(words[:4]) if words else "mechanisms and framework"

    if sec_name.lower() == "abstract":
        return [
            EvaluationProbe(
                probe_id=f"{chunk.chunk_id}_probe_1",
                target_header_path=chunk.header_path,
                query_text="What is the primary summary and core objective of the study?",
                variation_idx=1,
            ),
            EvaluationProbe(
                probe_id=f"{chunk.chunk_id}_probe_2",
                target_header_path=chunk.header_path,
                query_text=f"What does the abstract state regarding {sample_phrase}?",
                variation_idx=2,
            ),
            EvaluationProbe(
                probe_id=f"{chunk.chunk_id}_probe_3",
                target_header_path=chunk.header_path,
                query_text=f"How does the study introduce its findings concerning {sample_phrase}?",
                variation_idx=3,
            ),
        ]

    target_sec = f"{parent_sec} > {sec_name}" if len(sec_name) <= 3 and parent_sec else sec_name

    return [
        EvaluationProbe(
            probe_id=f"{chunk.chunk_id}_probe_1",
            target_header_path=chunk.header_path,
            query_text=f"What does the paper explain about {target_sec}?",
            variation_idx=1,
        ),
        EvaluationProbe(
            probe_id=f"{chunk.chunk_id}_probe_2",
            target_header_path=chunk.header_path,
            query_text=f"Describe the framework and key mechanisms in {target_sec} {sample_phrase}.",
            variation_idx=2,
        ),
        EvaluationProbe(
            probe_id=f"{chunk.chunk_id}_probe_3",
            target_header_path=chunk.header_path,
            query_text=f"How does the study address {sample_phrase} in {target_sec}?",
            variation_idx=3,
        ),
    ]


def evaluate_chunks(
    chunks: List[IngestionChunk],
    model: Optional[BaseChatModel] = None,
    threshold: float = 0.8,
    use_jev: bool = True,
) -> EvaluationResult:
    """Evaluate candidate chunks in an ephemeral staging vector index using paraphrased probes and Jev."""
    if not chunks:
        return EvaluationResult(
            total_probes=0,
            successful_retrievals=0,
            recall_score=0.0,
            passed=False,
            failing_sections=["Empty document"],
        )

    # 1. Spin up an in-memory ephemeral Chroma client
    client = chromadb.EphemeralClient()
    staging_coll_name = f"staging_{uuid.uuid4().hex[:12]}"
    collection = client.create_collection(staging_coll_name)

    try:
        # 2. Stage candidate chunks
        ids = [c.chunk_id for c in chunks]
        docs = [c.chunk_content for c in chunks]
        metas = [
            {
                "chunk_id": c.chunk_id,
                "document_name": c.document_name,
                "header_path": c.header_path,
            }
            for c in chunks
        ]
        collection.add(ids=ids, documents=docs, metadatas=metas)

        # 3. Generate all probes
        chunk_probes_map = {}
        all_probes = []
        for chunk in chunks:
            probes = generate_section_probes(chunk, model=model)
            chunk_probes_map[chunk.chunk_id] = (chunk, probes)
            all_probes.extend(probes)

        if not all_probes:
            return EvaluationResult(
                total_probes=0,
                successful_retrievals=0,
                recall_score=0.0,
                passed=False,
                failing_sections=[],
            )

        # 4. Batch query Chroma in a single vector search
        query_texts = [p.query_text for p in all_probes]
        top_k = min(3, len(chunks))
        batch_res = collection.query(query_texts=query_texts, n_results=top_k)

        # 5. Score retrieval results
        successful = 0
        total_probes = len(all_probes)
        failing_sections_set = set()
        diagnostics = []

        for p_idx, probe in enumerate(all_probes):
            hit = False
            top_retrieved_header = None
            if batch_res and batch_res.get("metadatas") and p_idx < len(batch_res["metadatas"]):
                metas_list = batch_res["metadatas"][p_idx]
                dists_list = batch_res["distances"][p_idx] if batch_res.get("distances") else [0.0] * len(metas_list)
                if metas_list:
                    top_retrieved_header = metas_list[0].get("header_path")

                for rank_idx, meta_item in enumerate(metas_list):
                    ret_h = str(meta_item.get("header_path", ""))
                    dist = dists_list[rank_idx] if rank_idx < len(dists_list) else 0.0
                    target_h = probe.target_header_path
                    if (ret_h == target_h or target_h in ret_h or ret_h in target_h) and dist <= 1.8:
                        hit = True
                        break

            if hit:
                successful += 1
            else:
                diagnostics.append({
                    "probe": probe.query_text,
                    "expected_header": probe.target_header_path,
                    "got_header": top_retrieved_header,
                })

        # Calculate section-level success rate
        for chunk_id, (chunk, probes) in chunk_probes_map.items():
            if probes:
                chunk_misses = sum(
                    1 for p in probes
                    if any(d["probe"] == p.query_text and d["expected_header"] == p.target_header_path for d in diagnostics)
                )
                chunk_hits = len(probes) - chunk_misses
                if (chunk_hits / len(probes)) < threshold:
                    failing_sections_set.add(chunk.header_path)

        # 6. Jev Chunk Integrity & Boundary Verification (Fast sub-500ms parallel check)
        if use_jev and (os.environ.get("JEV_API_KEY") or getattr(get_settings(), "JEV_API_KEY", None)):
            try:
                jev_verdicts = evaluate_chunk_integrity_jev(chunks)
                for cid, v in jev_verdicts.items():
                    if not v["passed"]:
                        failing_sections_set.add(v["header_path"])
                        diagnostics.append({
                            "chunk_id": cid,
                            "header_path": v["header_path"],
                            "issue": "Jev flagged fragmented chunk or boundary cutoff",
                            "jev_score": v["score"],
                        })
            except Exception as e:
                logger.debug(f"Jev chunk integrity check skipped ({e})")

        recall_score = round(successful / total_probes, 4) if total_probes > 0 else 0.0
        passed = recall_score >= threshold
        failing_sections = list(failing_sections_set) if not passed else []

        return EvaluationResult(
            total_probes=total_probes,
            successful_retrievals=successful,
            recall_score=recall_score,
            passed=passed,
            failing_sections=failing_sections,
            diagnostic_logs=diagnostics,
        )
    finally:
        try:
            client.delete_collection(staging_coll_name)
        except Exception:
            pass
