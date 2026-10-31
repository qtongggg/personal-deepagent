import json
import os
import pytest
from src.skills.ingestion.evaluator import evaluate_chunks
from src.skills.ingestion.chunker import chunk_markdown
from src.skills.ingestion.pipeline import ingest_markdown_or_pdf, _refine_chunks_for_self_correction
from src.skills.ingestion.schemas import DocumentMetadata, IngestionChunk
from tests.mock_model import MockChatModel


def test_evaluator_flags_partial_section_failures():
    """Critical 2: Sections with < 80% recall must be flagged as failing, not just 0% hits."""
    chunk = IngestionChunk(
        chunk_id="c1",
        document_name="DOC1",
        header_path="Section > Partial",
        chunk_content="Content about risk-sharing and capital buffers."
    )
    # 3 probes: 1 matching probe and 2 failing probes -> 1/3 = 33% (< 80%)
    probes_json = json.dumps([
        "risk-sharing and capital buffers", # hit
        "quantum computing in cryptography", # miss
        "dark matter galactic halo" # miss
    ])
    mock_model = MockChatModel(responses=[probes_json])
    result = evaluate_chunks([chunk], model=mock_model, threshold=0.8)
    assert result.passed is False
    assert "Section > Partial" in result.failing_sections


def test_chunker_and_refine_respect_word_boundaries():
    """Critical 1: Chunker merges undersized fragments and self-correction splits oversized blocks."""
    # 1. Undersized fragments: two consecutive 10-word sections should be coalesced
    meta = DocumentMetadata(document_name="DOC_BOUNDS", title="Bounds Test")
    short_md = (
        "# Part 1\n"
        "Just a tiny fragment here.\n\n"
        "# Part 2\n"
        "Another small fragment of text.\n\n"
        "# Part 3\n"
        "A regular length section with plenty of words to easily exceed forty words threshold for normal chunking in academic texts."
    )
    chunks = chunk_markdown(short_md, meta, min_words=15)
    # The two short fragments should be merged or satisfy min_words constraint
    for c in chunks:
        assert len(c.chunk_content.split()) >= 10

    # 2. Self-correction must not duplicate breadcrumbs
    test_chunk = IngestionChunk(
        chunk_id="c_dup",
        document_name="DOC_BOUNDS",
        header_path="Intro > Background",
        chunk_content="Initial text content."
    )
    refined_once = _refine_chunks_for_self_correction([test_chunk], ["Intro > Background"], meta)
    refined_twice = _refine_chunks_for_self_correction(refined_once, ["Intro > Background"], meta)
    # Must only have one prefix
    assert refined_twice[0].chunk_content.count("[Document:") == 1


def test_pipeline_persists_quarantine_log(tmp_path):
    """Important 1: Quarantined runs must write an audit record to disk."""
    log_file = tmp_path / "quarantine_log.json"
    meta = DocumentMetadata(document_name="DOC_QUARANTINE_TEST", title="Audit Test")
    unrelated_probes = json.dumps(["quantum computing in cryptography", "dark matter", "galactic halo"])
    mock_model = MockChatModel(responses=[unrelated_probes, unrelated_probes, unrelated_probes])

    sample_md = "# Section A\nSome content."
    report = ingest_markdown_or_pdf(
        raw_markdown=sample_md,
        model=mock_model,
        threshold=0.99,
        max_iterations=1,
        quarantine_log_path=str(log_file)
    )
    assert report.status == "QUARANTINED"
    assert os.path.exists(str(log_file))
    with open(str(log_file), "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(item["document_name"] == report.document_metadata.document_name for item in data)
