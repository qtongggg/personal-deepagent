import json
import logging
import re
from datetime import datetime
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from src.utils.models import get_default_model
from src.skills.ingestion.schemas import DocumentMetadata

logger = logging.getLogger(__name__)


def _heuristic_metadata_extraction(
    text: str, fallback_slug: Optional[str] = None, source_url: Optional[str] = None
) -> DocumentMetadata:
    """Fallback rule-based extraction when LLM extraction fails or is unavailable."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    title = lines[0] if lines else "Untitled Document"
    
    # Clean arXiv prefix from title line if present
    if title.lower().startswith("arxiv:") and len(lines) > 1:
        title = lines[1]
    title = re.sub(r"^[#\s\*]+", "", title).strip()

    # Detect year
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
    year = int(year_match.group(1)) if year_match else datetime.now().year

    # Detect arXiv ID from text or source_url
    arxiv_match = re.search(r"arXiv:(\d{4}\.\d{4,5})", text, re.IGNORECASE)
    if not arxiv_match and source_url:
        arxiv_match = re.search(r"(\d{4}\.\d{4,5})", source_url)

    if arxiv_match:
        arxiv_id = arxiv_match.group(1).replace(".", "_")
        slug = f"ARXIV_{arxiv_id}"
        canonical_url = f"https://arxiv.org/abs/{arxiv_match.group(1)}"
    else:
        clean_slug = re.sub(r"[^\w\d_]", "_", title[:25].upper()).strip("_")
        slug = fallback_slug or f"DOC_{clean_slug or 'UNTITLED'}"
        canonical_url = source_url

    author = "Unknown"
    date_pattern = re.compile(r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b", re.IGNORECASE)
    for line in lines[1:6]:
        cleaned_line = re.sub(r"^[#\s\*]+", "", line).strip()
        if any(term in cleaned_line.lower() for term in ["abstract", "arxiv", "http", "doi", "vol"]):
            continue
        if date_pattern.search(cleaned_line):
            continue
        if len(cleaned_line) < 80 and not cleaned_line.endswith("."):
            author = cleaned_line
            break

    return DocumentMetadata(
        document_name=slug,
        title=title,
        author=author,
        year=year,
        publisher="arXiv" if ("arxiv" in text.lower() or (source_url and "arxiv" in source_url.lower())) else "Unknown",
        document_type="Research Paper",
        source_url=canonical_url,
    )


def extract_metadata(
    first_page_text: str,
    fallback_slug: Optional[str] = None,
    source_url: Optional[str] = None,
    model: Optional[BaseChatModel] = None,
) -> DocumentMetadata:
    """Extract structured document metadata from the first page text using LLM with heuristic fallback."""
    active_model = model or get_default_model()

    system_prompt = (
        "Extract scholarly metadata from the following first page of a document.\n"
        "Return a strictly valid JSON object with these keys:\n"
        "- document_name: a short upper-case identifier without spaces (e.g. 'ARXIV_2403_12345' or 'IRP_45')\n"
        "- title: full paper title\n"
        "- author: comma-separated author list or primary organization\n"
        "- year: publication year as integer (e.g. 2024)\n"
        "- publisher: journal, conference, or repository (e.g. 'arXiv', 'INCEIF')\n"
        "- document_type: e.g. 'Research Paper', 'Report', 'Book'\n"
        "- source_url: verbatim link if present or null\n"
        "Return ONLY JSON."
    )

    try:
        response = active_model.invoke([
            HumanMessage(content=f"{system_prompt}\n\nDocument Text:\n{first_page_text[:3000]}")
        ])
        content = response.content
        if isinstance(content, list):
            content = "".join(str(b.get("text", "")) if isinstance(b, dict) else str(b) for b in content)

        # Clean codeblock fences if present
        cleaned_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(content).strip(), flags=re.MULTILINE)
        data = json.loads(cleaned_json)

        return DocumentMetadata(
            document_name=data.get("document_name") or fallback_slug or "DOC_UNKNOWN",
            title=re.sub(r"^[#\s\*]+", "", data.get("title") or "Untitled Document").strip(),
            author=data.get("author") or "Unknown",
            year=int(data.get("year")) if data.get("year") else datetime.now().year,
            publisher=data.get("publisher") or "arXiv",
            document_type=data.get("document_type") or "Research Paper",
            source_url=data.get("source_url") or source_url,
        )
    except Exception as e:
        logger.debug(f"LLM metadata extraction failed ({e}), falling back to heuristic parsing.")
        return _heuristic_metadata_extraction(first_page_text, fallback_slug=fallback_slug, source_url=source_url)
