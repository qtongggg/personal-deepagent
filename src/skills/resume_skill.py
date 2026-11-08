import os
from typing import Any, Dict, List
from langchain_core.tools import tool
from rank_bm25 import BM25Okapi
from flashrank import Ranker, RerankRequest
from src.utils.chroma import get_chroma_client

COLLECTION_NAME = "personal_resume_knowledge"

@tool
def retrieve_resume_knowledge(query: str) -> str:
    """Search Mah Qing Tong's (QT) official resume for experience, education, skills, and projects.
    Use this tool whenever asked about QT's background, past roles, technical stack, or achievements.
    """
    client = get_chroma_client()
    collection = client.get_collection(COLLECTION_NAME)

    # 1. Fetch all documents from the collection
    all_data = collection.get()
    all_docs = all_data.get("documents", []) # also called the chunks 
    all_ids = all_data.get("ids", [])
    all_metas = all_data.get("metadatas", [])

    if not all_docs:
        return "Resume database is empty"

    # 2. Dense Semantic Search ( Chroma vector search)
    dense_res = collection.query(query_texts=[query], n_results = min(6, len(all_docs))) # this output return as a dict but the ids is a list of list 
    dense_ids = dense_res.get('ids', [[]])[0]

    # 3. Sparse Lexical Search (BM25 keyword scoring) 
    tokenized_corpus = [doc.lower().split() for doc in all_docs]
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:6]
    bm25_ids = [all_ids[i] for i in bm25_indices]

    # 4. Merge candidates (Union of Dense + BM25)
    candidate_ids = list(dict.fromkeys(dense_ids + bm25_ids))
    candidates = []

    for cid in candidate_ids:
        idx = all_ids.index(cid)
        candidates.append({"id": cid, "text": all_docs[idx], "meta": all_metas[idx]})

    # 5. Cross-Encoder Reranking (FlashRank)
    try:
        ranker = Ranker(model_name="ms-marco-TinyBERT-L-2-v2", cache_dir="data/.cache_flashrank")
        passages = [{"id": c["id"], "text": c["text"]} for c in candidates]
        rerank_req = RerankRequest(query=query, passages=passages)
        reranked = ranker.rerank(rerank_req)
        top_passages = reranked[:3]

    except Exception:
        top_passages = candidates[:3]

    # 6. Format the retrieved passages for the LLM 
    context_blocks = []
    for item in top_passages:
        context_blocks.append(item["text"])

    return "\n\n---\n\n".join(context_blocks)