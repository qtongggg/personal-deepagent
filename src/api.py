from collections import Counter
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from scripts.ingest import get_chroma_client
from src.skills.catalog_skill import query_catalog_sql
from src.skills.retriever_skill import retrieve_knowledge_chunks

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Personal DeepAgent API",
    description="Knowledge base, document chunk inspection, and autonomous deep research agent API.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DocumentInfo(BaseModel):
    document_name: str
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[Any] = None
    publisher: Optional[str] = None
    document_type: Optional[str] = None
    source_url: Optional[str] = None
    total_chunks: int = 0


class ChunkInfo(BaseModel):
    chunk_id: str
    document_name: str
    header_path: str
    chunk_content: str
    word_count: int


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/documents", response_model=List[DocumentInfo])
def get_documents() -> List[DocumentInfo]:
    """List all stored documents merging catalog metadata with ChromaDB chunk counts."""
    client = get_chroma_client()
    collection = client.get_or_create_collection("document_knowledge")

    chroma_data = collection.get()
    counts = Counter()
    for meta in chroma_data.get("metadatas", []):
        doc = meta.get("document_name")
        if doc:
            counts[doc] += 1

    catalog_rows = {}
    try:
        raw_catalog = query_catalog_sql("SELECT * FROM catalog")
        for row in raw_catalog:
            doc_name = row.get("document_name")
            if doc_name:
                catalog_rows[doc_name] = row
    except Exception as e:
        logger.warning(f"Could not read catalog.csv: {e}")

    # Combine all document names from both ChromaDB and catalog
    all_names = sorted(list(set(counts.keys()) | set(catalog_rows.keys())))

    documents: List[DocumentInfo] = []
    for name in all_names:
        meta = catalog_rows.get(name, {})
        documents.append(
            DocumentInfo(
                document_name=name,
                title=meta.get("title") or name,
                author=meta.get("author") or "Unknown",
                year=meta.get("year"),
                publisher=meta.get("publisher"),
                document_type=meta.get("document_type"),
                source_url=meta.get("source_url"),
                total_chunks=counts.get(name, 0),
            )
        )

    return documents


@app.get("/api/documents/{document_name}/chunks", response_model=List[ChunkInfo])
def get_document_chunks(document_name: str) -> List[ChunkInfo]:
    """Retrieve all chunks belonging to a specific document."""
    client = get_chroma_client()
    collection = client.get_or_create_collection("document_knowledge")

    results = collection.get(where={"document_name": document_name})
    if not results or not results.get("ids"):
        raise HTTPException(status_code=404, detail=f"Document '{document_name}' not found.")

    chunks: List[ChunkInfo] = []
    for cid, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
        clean_words = len(doc.split())
        chunks.append(
            ChunkInfo(
                chunk_id=cid,
                document_name=meta.get("document_name", document_name),
                header_path=meta.get("header_path", "/"),
                chunk_content=doc,
                word_count=clean_words,
            )
        )

    # Sort chunks deterministically by chunk_id
    chunks.sort(key=lambda c: c.chunk_id)
    return chunks


@app.get("/api/search")
def semantic_search(
    q: str = Query(..., description="Query text"),
    document_name: Optional[str] = Query(None, description="Optional document name filter"),
    top_k: int = Query(5, ge=1, le=25, description="Number of results to retrieve"),
) -> List[Dict[str, Any]]:
    """Perform semantic vector retrieval on the knowledge base."""
    clean_q = q.strip()
    if not clean_q:
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    chunks = retrieve_knowledge_chunks(query=clean_q, top_k=top_k, document_filter=document_name)
    return chunks
