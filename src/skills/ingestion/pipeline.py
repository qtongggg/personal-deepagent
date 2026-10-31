import csv
from datetime import datetime
import json
import logging
import os
import re
import tempfile
from typing import Any, Dict, List, Optional
import urllib.request
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import tool
from scripts.ingest import get_chroma_client
from src.config import get_settings
from src.skills.ingestion.chunker import chunk_markdown
from src.skills.ingestion.evaluator import evaluate_chunks
from src.skills.ingestion.extractor import extract_metadata
from src.skills.ingestion.parser import parse_pdf_to_clean_markdown
from src.skills.ingestion.schemas import DocumentMetadata, IngestionChunk, IngestionReport

logger = logging.getLogger(__name__)


def download_url_to_temp_file(url: str) -> str:
    """Download an arXiv or remote PDF to a temporary file."""
    match = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", url)
    pdf_url = f"https://arxiv.org/pdf/{match.group(1)}.pdf" if match else url

    temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    req = urllib.request.Request(
        pdf_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PersonalDeepAgent/1.0"},
    )
    with urllib.request.urlopen(req) as response, open(temp_path, "wb") as out_f:
        out_f.write(response.read())

    return temp_path


def _refine_chunks_for_self_correction(
    chunks: List[IngestionChunk],
    failing_sections: List[str],
    metadata: DocumentMetadata,
) -> List[IngestionChunk]:
    """Adjust chunk boundaries and strengthen contextual breadcrumbs for failing sections without drift."""
    refined = []
    failing_set = set(failing_sections)

    for c in chunks:
        words = len(c.chunk_content.split())
        if c.header_path in failing_set:
            # Case 1: Oversized chunk (> 800 words) -> split at paragraph boundaries
            if words > 800 and "\n\n" in c.chunk_content:
                parts = c.chunk_content.split("\n\n")
                mid = len(parts) // 2
                part_1 = "\n\n".join(parts[:mid]).strip()
                part_2 = "\n\n".join(parts[mid:]).strip()

                prefix = f"[Document: {metadata.title} | Section: {c.header_path}]\n"
                refined.append(
                    IngestionChunk(
                        chunk_id=f"{c.chunk_id}_a",
                        document_name=c.document_name,
                        header_path=c.header_path,
                        chunk_content=part_1 if part_1.startswith("[Document:") else f"{prefix}{part_1}",
                        word_count=len(part_1.split()),
                    )
                )
                refined.append(
                    IngestionChunk(
                        chunk_id=f"{c.chunk_id}_b",
                        document_name=c.document_name,
                        header_path=c.header_path,
                        chunk_content=part_2 if part_2.startswith("[Document:") else f"{prefix}{part_2}",
                        word_count=len(part_2.split()),
                    )
                )
            else:
                # Case 2: Prepend breadcrumb if not already present
                if not c.chunk_content.startswith("[Document:"):
                    enhanced_content = (
                        f"[Document: {metadata.title} | Section: {c.header_path}]\n"
                        f"{c.chunk_content}"
                    )
                else:
                    enhanced_content = c.chunk_content

                refined.append(
                    IngestionChunk(
                        chunk_id=c.chunk_id,
                        document_name=c.document_name,
                        header_path=c.header_path,
                        chunk_content=enhanced_content,
                        word_count=len(enhanced_content.split()),
                    )
                )
        else:
            refined.append(c)

    return refined


def _record_quarantine_log(record: Dict[str, Any], log_path: Optional[str] = None):
    """Persist quarantine diagnostics to disk for auditing."""
    path = log_path or "data/quarantine_log.json"
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    records = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                records = json.load(f)
                if not isinstance(records, list):
                    records = []
        except Exception:
            records = []

    records.append(record)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)


def _append_to_catalog_csv(metadata: DocumentMetadata, catalog_path: Optional[str] = None):
    """Safely append new metadata row to catalog.csv if not already present."""
    settings = get_settings()
    path = catalog_path or settings.CATALOG_CSV_PATH
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    existing_slugs = set()
    file_exists = os.path.exists(path)

    if file_exists:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("document_name"):
                    existing_slugs.add(row["document_name"])

    if metadata.document_name in existing_slugs:
        logger.info(f"Document {metadata.document_name} already registered in catalog.csv.")
        return

    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["document_name", "title", "author", "year", "publisher", "document_type", "source_url"])
        writer.writerow([
            metadata.document_name,
            metadata.title,
            metadata.author or "Unknown",
            metadata.year or "",
            metadata.publisher or "arXiv",
            metadata.document_type or "Research Paper",
            metadata.source_url or "",
        ])


def ingest_markdown_or_pdf(
    pdf_path: Optional[str] = None,
    raw_markdown: Optional[str] = None,
    source_url: Optional[str] = None,
    model: Optional[BaseChatModel] = None,
    threshold: float = 0.8,
    max_iterations: int = 3,
    catalog_csv_path: Optional[str] = None,
    quarantine_log_path: Optional[str] = None,
) -> IngestionReport:
    """Orchestrate the complete parse -> extract -> chunk -> evaluate -> self-correct -> commit pipeline."""
    # 1. Parse content
    if pdf_path:
        markdown_text = parse_pdf_to_clean_markdown(pdf_path)
    elif raw_markdown:
        markdown_text = raw_markdown
    else:
        raise ValueError("Either pdf_path or raw_markdown must be provided.")

    # 2. Extract metadata
    fallback_slug = os.path.splitext(os.path.basename(pdf_path))[0].upper() if pdf_path else None
    metadata = extract_metadata(markdown_text[:3000], fallback_slug=fallback_slug, source_url=source_url, model=model)

    # 3. Initial chunking
    chunks = chunk_markdown(markdown_text, metadata)
    if not chunks:
        return IngestionReport(
            document_metadata=metadata,
            status="ERROR",
            total_chunks=0,
            final_recall_score=0.0,
            quarantine_reason="No substantive chunks could be created from document.",
        )

    # 4. Self-correction loop
    final_eval = None
    iteration = 1

    for it in range(1, max_iterations + 1):
        iteration = it
        eval_result = evaluate_chunks(chunks, model=model, threshold=threshold)
        final_eval = eval_result

        if eval_result.passed:
            break

        if it < max_iterations:
            chunks = _refine_chunks_for_self_correction(chunks, eval_result.failing_sections, metadata)

    # 5. Terminal gate check
    if final_eval and final_eval.passed:
        client = get_chroma_client()
        collection = client.get_or_create_collection("document_knowledge")
        ids = [c.chunk_id for c in chunks]
        documents = [c.chunk_content for c in chunks]
        metadatas = [
            {
                "chunk_id": c.chunk_id,
                "document_name": c.document_name,
                "header_path": c.header_path,
            }
            for c in chunks
        ]
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        _append_to_catalog_csv(metadata, catalog_path=catalog_csv_path)

        return IngestionReport(
            document_metadata=metadata,
            status="SUCCESS",
            total_chunks=len(chunks),
            final_recall_score=final_eval.recall_score,
            iterations_used=iteration,
        )
    else:
        score = final_eval.recall_score if final_eval else 0.0
        quarantine_record = {
            "timestamp": datetime.now().isoformat(),
            "document_name": metadata.document_name,
            "title": metadata.title,
            "final_recall_score": score,
            "threshold": threshold,
            "iterations_used": iteration,
            "total_chunks": len(chunks),
            "failing_sections": list(final_eval.failing_sections) if final_eval else [],
            "diagnostics": final_eval.diagnostic_logs if final_eval else [],
        }
        _record_quarantine_log(quarantine_record, log_path=quarantine_log_path)

        return IngestionReport(
            document_metadata=metadata,
            status="QUARANTINED",
            total_chunks=len(chunks),
            final_recall_score=score,
            iterations_used=iteration,
            quarantine_reason=f"Recall score ({score:.2f}) failed target threshold ({threshold}) after {max_iterations} iterations.",
        )


def ingest_pdf_document(
    source: str,
    source_url: Optional[str] = None,
    model: Optional[BaseChatModel] = None,
    threshold: float = 0.8,
) -> IngestionReport:
    """Ingest a local or remote PDF document into ChromaDB and catalog.csv with agentic verification."""
    is_url = source.startswith("http://") or source.startswith("https://")
    cleanup = False

    if is_url:
        local_path = download_url_to_temp_file(source)
        canonical_url = source_url or source
        cleanup = True
    else:
        local_path = os.path.abspath(source)
        canonical_url = source_url

    try:
        return ingest_markdown_or_pdf(
            pdf_path=local_path,
            source_url=canonical_url,
            model=model,
            threshold=threshold,
        )
    finally:
        if cleanup and os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception:
                pass


@tool("ingest_document")
def ingest_document_tool(file_path_or_url: str) -> str:
    """Ingest a new research PDF document (local path or arXiv URL) into the knowledge base and catalog with autonomous verification."""
    try:
        report = ingest_pdf_document(file_path_or_url)
        return (
            f"Ingestion result for '{report.document_metadata.document_name}': {report.status}. "
            f"Total chunks: {report.total_chunks}, Recall score: {report.final_recall_score:.2f}."
        )
    except Exception as e:
        return f"Error ingesting document '{file_path_or_url}': {e}"
