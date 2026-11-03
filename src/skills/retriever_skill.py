import json
from typing import Any, Dict, List, Optional
from langchain_core.tools import tool
from scripts.ingest import get_chroma_client


_CLIENT = None
_COLLECTION = None


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
    if _COLLECTION is None:
        _CLIENT = get_chroma_client()
        _COLLECTION = _CLIENT.get_or_create_collection(collection_name)
    return _COLLECTION


def retrieve_knowledge_chunks(
    query: str,
    top_k: int = 5,
    document_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve semantic document chunks matching a query with section metadata."""
    collection = _get_collection()
    total_count = collection.count()
    if total_count == 0:
        return []

    n_results = max(1, min(top_k, total_count))
    resolved_doc = _resolve_document_name(document_filter) if document_filter else None
    target_filter = resolved_doc or document_filter
    where_filter = {"document_name": target_filter} if target_filter else None

    query_params = {
        "query_texts": [query],
        "n_results": n_results,
    }
    if where_filter:
        query_params["where"] = where_filter

    results = collection.query(**query_params)

    # Resilient fallback: if where filter returned zero results, retry without filter
    if (not results or not results["documents"] or not results["documents"][0]) and where_filter:
        fallback_params = {
            "query_texts": [query],
            "n_results": n_results,
        }
        results = collection.query(**fallback_params)

    chunks: List[Dict[str, Any]] = []
    if not results or not results["documents"] or not results["documents"][0]:
        return chunks

    docs = results["documents"][0]
    metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
    ids = results["ids"][0] if results.get("ids") else [""] * len(docs)
    distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

    for doc, meta, cid, dist in zip(docs, metas, ids, distances):
        meta = meta or {}
        chunks.append({
            "chunk_id": meta.get("chunk_id", cid),
            "document_name": meta.get("document_name", "Unknown"),
            "header_path": meta.get("header_path", "/"),
            "chunk_content": doc,
            "distance": dist,
        })

    return chunks


@tool("knowledge_retriever")
def retriever_tool(
    query: str,
    top_k: int = 5,
    document_filter: Optional[str] = None,
) -> str:
    """Retrieve content chunks from research papers and publications.
    
    Returns relevant passages with section metadata:
    - document_name (e.g. 'IRP 5', 'IRP 11')
    - header_path (e.g. '/INTRODUCTION', 'Maqasid al-Shariah > Structural Challenges')
    - chunk_content (the text passage)

    Use document_filter to restrict retrieval to a specific document (e.g. document_filter='IRP 5').
    """
    try:
        chunks = retrieve_knowledge_chunks(query=query, top_k=top_k, document_filter=document_filter)
        if not chunks:
            return f"No relevant passages found for query '{query}'."
        return json.dumps(chunks, indent=2)
    except Exception as e:
        return f"Error retrieving knowledge chunks: {e}"
