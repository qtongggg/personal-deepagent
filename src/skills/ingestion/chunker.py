import re
from typing import List, Optional
from src.skills.ingestion.schemas import DocumentMetadata, IngestionChunk


def _count_words(text: str) -> int:
    return len(text.split())


def chunk_markdown(
    markdown_text: str,
    metadata: DocumentMetadata,
    min_words: int = 10,
    max_words: int = 800,
) -> List[IngestionChunk]:
    """Structurally chunk Markdown by headers, preserving tables and attaching breadcrumbs."""
    if not markdown_text or not markdown_text.strip():
        return []

    lines = markdown_text.split("\n")
    sections = []
    
    current_header_stack = []
    current_lines = []

    def commit_current_section():
        nonlocal current_lines, current_header_stack
        content = "\n".join(current_lines).strip()
        if content:
            path = " > ".join(current_header_stack) if current_header_stack else "/INTRODUCTION"
            sections.append((path, content))
        current_lines = []

    in_table = False

    for line in lines:
        stripped = line.strip()

        # Check if line is part of a markdown table
        if stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 1:
            in_table = True
            current_lines.append(line)
            continue
        elif in_table and stripped == "":
            in_table = False
            current_lines.append(line)
            continue
        else:
            in_table = False

        # Check for markdown header: #, ##, ###, ####
        header_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if header_match:
            commit_current_section()
            level = len(header_match.group(1))
            raw_title = header_match.group(2).strip()
            # Clean markdown bold/italic/header symbols
            title = re.sub(r"^\*+|\*+$", "", raw_title).strip()
            title = re.sub(r"^#+\s*", "", title).strip()

            # If sub-heading is single letter (e.g. 'a', 'b' figure label) and we have parent
            if len(title) <= 2 and level >= 3 and current_header_stack:
                title = f"{current_header_stack[-1]} ({title})"

            # Adjust stack: slice up to level - 1, then append current title
            current_header_stack = current_header_stack[: level - 1]
            current_header_stack.append(title)
        else:
            current_lines.append(line)

    commit_current_section()

    if not sections:
        return []

    # Coalesce undersized sections if words < min_words
    coalesced_sections = []
    for path, content in sections:
        if coalesced_sections and _count_words(coalesced_sections[-1][1]) < min_words:
            prev_path, prev_content = coalesced_sections.pop()
            combined_path = f"{prev_path} & {path}" if prev_path != path else prev_path
            combined_content = f"{prev_content}\n\n{content}"
            coalesced_sections.append((combined_path, combined_content))
        else:
            coalesced_sections.append((path, content))

    if len(coalesced_sections) > 1 and _count_words(coalesced_sections[-1][1]) < min_words:
        last_path, last_content = coalesced_sections.pop()
        prev_path, prev_content = coalesced_sections.pop()
        combined_path = f"{prev_path} & {last_path}" if prev_path != last_path else prev_path
        coalesced_sections.append((combined_path, f"{prev_content}\n\n{last_content}"))

    # Now refine sections according to max_words
    chunks: List[IngestionChunk] = []
    chunk_index = 1

    def _build_chunk(c_index: int, c_path: str, c_body: str) -> IngestionChunk:
        sec_title = c_path.split(">")[-1].strip()
        doc_title = re.sub(r"^[#\s\*]+", "", metadata.title).strip()
        prefix = f"[Document: {doc_title} | Section: {c_path}]\n## {sec_title}\n\n"
        full_body = c_body if c_body.startswith("[Document:") else f"{prefix}{c_body}"
        return IngestionChunk(
            chunk_id=f"{metadata.document_name}_chunk_{c_index:03d}",
            document_name=metadata.document_name,
            header_path=c_path,
            chunk_content=full_body,
            word_count=_count_words(full_body),
        )

    for path, content in coalesced_sections:
        words = _count_words(content)

        if words <= max_words:
            # Fits in one chunk
            chunks.append(_build_chunk(chunk_index, path, content))
            chunk_index += 1
        else:
            # Split oversized section by paragraphs
            paragraphs = content.split("\n\n")
            sub_chunk_lines = []
            sub_count = 0

            for para in paragraphs:
                para_words = _count_words(para)
                if sub_count + para_words > max_words and sub_chunk_lines:
                    sub_content = "\n\n".join(sub_chunk_lines).strip()
                    chunks.append(_build_chunk(chunk_index, path, sub_content))
                    chunk_index += 1
                    sub_chunk_lines = [para]
                    sub_count = para_words
                else:
                    sub_chunk_lines.append(para)
                    sub_count += para_words

            if sub_chunk_lines:
                sub_content = "\n\n".join(sub_chunk_lines).strip()
                chunks.append(_build_chunk(chunk_index, path, sub_content))
                chunk_index += 1

    return chunks

