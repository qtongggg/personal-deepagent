import logging
import os
import re

logger = logging.getLogger(__name__)

# Patterns for line-level noise filtering
_PAGE_PATTERNS = [
    re.compile(r"^page\s+\d+(\s+of\s+\d+)?\s*$", re.IGNORECASE),
    re.compile(r"^---\s*\d+\s*---\s*$"),
    re.compile(r"^\d{1,4}\s*$"),  # Standalone page number
    re.compile(r"^copyright\s+.*", re.IGNORECASE),
    re.compile(r"^all rights reserved.*", re.IGNORECASE),
    re.compile(r"^arxiv:\d{4}\.\d{4,5}.*$", re.IGNORECASE),
    re.compile(r"^\**start picture.*", re.IGNORECASE),
]


def clean_markdown_text(raw_md: str) -> str:
    """Filter out page numbers, copyright footers, running headers, image tags, references, and excess whitespace."""
    if not raw_md or not raw_md.strip():
        return ""

    # 1. Strip image links, picture tags, and diagram markers
    text = re.sub(r"!\[.*?\]\(.*?\)", "", raw_md)
    text = re.sub(r"<\/?picture>", "", text)
    text = re.sub(r"\**Start picture.*?\**", "", text, flags=re.IGNORECASE)

    # 2. Separate and prune bibliography and back-matter disclosure sections if present
    parts = re.split(
        r"\n(?=#{1,3}\s+\**(?:References|Bibliography|Acknowledgements|Author Contributions|Competing Interests|Data Availability|AI Use Disclosure)\**)",
        text,
        flags=re.IGNORECASE,
    )
    text = parts[0]

    cleaned_lines = []
    lines = text.split("\n")

    for line in lines:
        stripped = line.strip()
        # Skip empty lines for pattern matching
        if not stripped:
            cleaned_lines.append("")
            continue

        # Check if line matches any noise pattern
        if any(pat.match(stripped) for pat in _PAGE_PATTERNS):
            continue

        cleaned_lines.append(line)

    result = "\n".join(cleaned_lines)
    # Collapse 3 or more newlines into 2
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def parse_pdf_to_clean_markdown(pdf_path: str, use_ocr: bool = False) -> str:
    """Parse a PDF document to clean, structured Markdown using pymupdf4llm."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    try:
        import pymupdf4llm
        try:
            raw_md = pymupdf4llm.to_markdown(pdf_path, use_ocr=use_ocr)
        except TypeError:
            raw_md = pymupdf4llm.to_markdown(pdf_path)
    except Exception as e:
        logger.error(f"Error parsing PDF with pymupdf4llm: {e}")
        raise RuntimeError(f"Failed to parse PDF {pdf_path}: {e}")

    return clean_markdown_text(raw_md)

