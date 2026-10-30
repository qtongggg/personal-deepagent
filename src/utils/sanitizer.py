import re
from typing import Any, Dict, List, Optional
from src.config import get_settings
from src.utils.schemas import AgentResponse, ReferenceItem


def sanitize_table_pipes(markdown_text: str) -> str:
    """Sanitize unescaped pipe characters in markdown table cells to prevent column drift."""
    lines = markdown_text.split("\n")
    sanitized_lines = []
    in_table = False
    expected_cols = 0

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 1:
            tokens = [t.strip() for t in stripped[1:-1].split("|")]
            
            # Check if this is the separator row, e.g. |---|---|
            is_separator = all(re.match(r"^:?-+:?$", t) for t in tokens)

            if not in_table:
                # This is the header row
                in_table = True
                expected_cols = len(tokens)
                sanitized_lines.append(line)
                continue

            if is_separator:
                sanitized_lines.append(line)
                continue

            # Data row
            if len(tokens) > expected_cols:
                extra = len(tokens) - expected_cols
                if expected_cols == 2:
                    # Merge col 0 (Title)
                    merged_title = " — ".join(tokens[: extra + 1])
                    reconstructed = [merged_title] + tokens[extra + 1 :]
                elif expected_cols >= 3:
                    # Document is col 0, Title is col 1
                    col_0 = tokens[0]
                    merged_title = " — ".join(tokens[1 : 2 + extra])
                    remaining = tokens[2 + extra :]
                    reconstructed = [col_0, merged_title] + remaining
                else:
                    reconstructed = [" — ".join(tokens)]
                sanitized_lines.append(f"| {' | '.join(reconstructed)} |")
            else:
                sanitized_lines.append(line)
        else:
            in_table = False
            expected_cols = 0
            sanitized_lines.append(line)

    return "\n".join(sanitized_lines)


def restore_verbatim_catalog_urls(
    markdown_text: str,
    catalog_lookup: Optional[Dict[str, str]] = None,
) -> str:
    """Restore character-for-character verbatim catalog URLs from the lookup."""
    if not catalog_lookup:
        return markdown_text

    result = markdown_text

    def _replace_url(match):
        prefix = match.group(1)
        url = match.group(2)
        suffix = match.group(3)

        for key, verbatim in catalog_lookup.items():
            if key in url or url in verbatim:
                return f"{prefix}{verbatim}{suffix}"
        return match.group(0)

    # Replace markdown links: [text](url)
    pattern = re.compile(r"(\]\()([^)\s]+)(\))")
    result = pattern.sub(_replace_url, result)

    # Also check bare URLs in text
    for key, verbatim in catalog_lookup.items():
        if key.startswith("http"):
            result = result.replace(key, verbatim)

    return result


def _build_default_catalog_lookup() -> Dict[str, Dict[str, Any]]:
    try:
        from src.skills.catalog_skill import query_catalog_sql
        rows = query_catalog_sql("SELECT * FROM catalog")
        return {r["document_name"]: r for r in rows if "document_name" in r}
    except Exception:
        return {}


def build_final_response(
    text: str,
    observed_chunks: Optional[List[Dict[str, Any]]] = None,
    catalog_lookup: Optional[Dict[str, str]] = None,
) -> AgentResponse:
    """Apply pipe sanitization, verbatim URL restoration, and build structured references."""
    settings = get_settings()

    catalog_data = _build_default_catalog_lookup()
    if not catalog_lookup:
        # Build URL lookup mapping slugs and doc names to source_url
        catalog_lookup = {}
        for doc_name, item in catalog_data.items():
            url = item.get("source_url")
            if url:
                catalog_lookup[doc_name] = url
                # Extract slug from url
                slug = url.rstrip("/").split("/")[-1]
                if slug:
                    catalog_lookup[slug] = url

    clean_text = sanitize_table_pipes(text)
    clean_text = restore_verbatim_catalog_urls(clean_text, catalog_lookup)

    references: List[ReferenceItem] = []
    seen_refs = set()

    if observed_chunks:
        for chunk in observed_chunks:
            doc_name = chunk.get("document_name", "Unknown")
            chunk_id = chunk.get("chunk_id", "")
            ref_key = (doc_name, chunk_id)
            if ref_key in seen_refs:
                continue
            seen_refs.add(ref_key)

            cat_item = catalog_data.get(doc_name, {})
            ref = ReferenceItem(
                document_name=doc_name,
                title=cat_item.get("title"),
                author=cat_item.get("author"),
                year=cat_item.get("year"),
                publisher=cat_item.get("publisher"),
                document_type=cat_item.get("document_type"),
                source_url=cat_item.get("source_url"),
                section=chunk.get("header_path"),
                chunk_id=chunk_id,
            )
            references.append(ref)
            if len(references) >= settings.MAX_REFERENCES:
                break

    return AgentResponse(
        result=clean_text,
        references=references,
        json_output={"reference_count": len(references)},
    )
