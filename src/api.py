from collections import Counter
import logging
import os
from typing import Any, Dict, List, Optional
import urllib.error
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from src.utils.chroma import get_chroma_client
from src.skills.catalog_skill import query_catalog_sql
from src.skills.ingestion.pipeline import download_url_to_temp_file, ingest_pdf_document
from src.skills.ingestion.schemas import IngestionReport
from src.skills.retriever_skill import retrieve_knowledge_chunks

logger = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates", "viewer.html")

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


class IngestRequest(BaseModel):
    source: str
    threshold: float = Field(default=0.8, ge=0.0, le=1.0)


def run_ingestion_sync(source: str, threshold: float = 0.8) -> IngestionReport:
    """Execute synchronous document ingestion from URL or local file path."""
    source_clean = source.strip()
    is_url = source_clean.startswith("http://") or source_clean.startswith("https://")
    if is_url:
        try:
            temp_pdf = download_url_to_temp_file(source_clean)
        except urllib.error.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Failed to download arXiv paper (HTTP {e.code}): {e.reason}")
        except urllib.error.URLError as e:
            raise HTTPException(status_code=400, detail=f"Network error accessing URL: {e.reason}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")

        try:
            return ingest_pdf_document(temp_pdf, source_url=source_clean, threshold=threshold)
        finally:
            if os.path.exists(temp_pdf):
                try:
                    os.remove(temp_pdf)
                except Exception:
                    pass
    else:
        if not os.path.exists(source_clean):
            raise HTTPException(status_code=404, detail=f"Local PDF file not found at: {source_clean}")
        return ingest_pdf_document(source_clean, threshold=threshold)


@app.post("/api/ingest", response_model=IngestionReport)
def ingest_document_endpoint(req: IngestRequest) -> IngestionReport:
    """Ingest an arXiv URL or local PDF paper into ChromaDB and catalog."""
    if not req.source or not req.source.strip():
        raise HTTPException(status_code=400, detail="Document source (URL or path) cannot be empty.")
    try:
        report = run_ingestion_sync(req.source, threshold=req.threshold)
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.get("/", response_class=HTMLResponse)
def get_viewer_page() -> HTMLResponse:
    """Serve the interactive single-page Chunk Studio UI."""
    if not os.path.exists(TEMPLATE_PATH):
        raise HTTPException(status_code=404, detail="Viewer template not found.")
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)


@app.get("/api/documents", response_model=List[DocumentInfo])
def get_documents(only_with_chunks: bool = True) -> List[DocumentInfo]:
    """List stored documents. By default, only returns documents with stored chunks in ChromaDB."""
    client = get_chroma_client()
    collection = client.get_or_create_collection("document_knowledge")

    chroma_data = collection.get()
    counts = Counter()
    for meta in chroma_data.get("metadatas", []):
        meta = meta or {}
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

    # Only list documents that actually have chunks in ChromaDB
    if only_with_chunks:
        all_names = sorted([name for name, count in counts.items() if count > 0])
    else:
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
        meta = meta or {}
        clean_words = len((doc or "").split())
        chunks.append(
            ChunkInfo(
                chunk_id=cid,
                document_name=meta.get("document_name", document_name),
                header_path=meta.get("header_path", "/"),
                chunk_content=doc or "",
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
