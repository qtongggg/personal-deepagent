import pytest
from src.skills.ingestion.chunker import chunk_markdown
from src.skills.ingestion.schemas import DocumentMetadata


def test_chunk_markdown_preserves_headers_and_tables():
    md = (
        "# Overview\n"
        "This paper introduces the architecture for global financial stability.\n\n"
        "## Sukuk Structures\n"
        "Current market practices overwhelmingly favor asset-based Sukuk.\n\n"
        "| Structure | Shariah Ruling |\n"
        "|---|---|\n"
        "| Asset-backed | Permissible with true sale |\n"
        "| Asset-based | Beneficial ownership only |\n\n"
        "### Governance Framework\n"
        "Macroprudential buffers are required by central monetary authorities.\n"
    )
    meta = DocumentMetadata(
        document_name="IRP_5_TEST",
        title="Sukuk and Stability",
        year=2020,
    )
    chunks = chunk_markdown(md, meta, min_words=5, max_words=100)
    assert len(chunks) >= 2

    # Check ID formatting
    assert chunks[0].chunk_id.startswith("IRP_5_TEST_chunk_")

    # Check breadcrumb presence
    assert any("Overview > Sukuk Structures" in c.header_path for c in chunks)
    assert any("Governance Framework" in c.header_path for c in chunks)

    # Check table integrity: whole table must remain in single chunk
    table_chunk = next(c for c in chunks if "Asset-backed" in c.chunk_content)
    assert "| Structure | Shariah Ruling |" in table_chunk.chunk_content
    assert "| Asset-based | Beneficial ownership only |" in table_chunk.chunk_content


def test_chunk_markdown_handles_document_without_headers():
    md = (
        "This is an unformatted text without any hash headers.\n"
        "It just contains standard sentences that form a single conceptual chunk."
    )
    meta = DocumentMetadata(document_name="DOC_NO_HEADER", title="Plain Doc")
    chunks = chunk_markdown(md, meta)
    assert len(chunks) == 1
    assert chunks[0].header_path == "/INTRODUCTION"
    assert chunks[0].chunk_id == "DOC_NO_HEADER_chunk_001"

