import csv
import json
import os
import tempfile
import pytest
from src.skills.ingestion.pipeline import ingest_markdown_or_pdf
from src.skills.ingestion.schemas import DocumentMetadata
from tests.mock_model import MockChatModel


def test_pipeline_successful_ingestion(tmp_path, monkeypatch):
    test_catalog = tmp_path / "catalog.csv"
    with open(test_catalog, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["document_name", "title", "author", "year", "publisher", "document_type", "source_url"])

    monkeypatch.setenv("CATALOG_CSV_PATH", str(test_catalog))

    sample_md = (
        "# Autonomous Network Alignment\n\n"
        "## Core Safety Architecture\n"
        "Autonomous agents require countercyclical buffers to prevent catastrophic goal drifting.\n\n"
        "## Shariah Governance Framework\n"
        "The institutional governance framework requires mutual cooperation and ethical oversight.\n"
    )

    # Mock responses: 1 for metadata extraction, 2 for section probes
    meta_json = json.dumps({
        "document_name": "AI_ALIGN_2024",
        "title": "Autonomous Network Alignment",
        "author": "Dr. Sarah Khan",
        "year": 2024,
        "publisher": "arXiv",
        "document_type": "Research Paper",
        "source_url": "https://arxiv.org/abs/2405.9999"
    })
    probes_1 = json.dumps(["How do countercyclical buffers prevent goal drift?", "What is core safety architecture?", "Explain autonomous alignment."])
    probes_2 = json.dumps(["What governance framework is required?", "How does Shariah oversight apply?", "Describe mutual cooperation principles."])

    mock_model = MockChatModel(responses=[meta_json, probes_1, probes_2])

    report = ingest_markdown_or_pdf(
        raw_markdown=sample_md,
        model=mock_model,
        threshold=0.8,
        catalog_csv_path=str(test_catalog)
    )

    assert report.status == "SUCCESS"
    assert report.final_recall_score >= 0.8
    assert report.total_chunks >= 2

    # Verify catalog.csv has the new row
    with open(test_catalog, "r", encoding="utf-8") as f:
        content = f.read()
    assert "AI_ALIGN_2024" in content
    assert "Dr. Sarah Khan" in content


def test_pipeline_quarantine_on_terminal_failure(tmp_path, monkeypatch):
    """Review Focus 5: Terminal failure must quarantine and leave catalog untouched."""
    test_catalog = tmp_path / "catalog_isolated.csv"
    with open(test_catalog, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["document_name", "title", "author", "year", "publisher", "document_type", "source_url"])

    sample_md = "# Bad Section\nFragmented single sentence."

    # Mock probe questions that will fail retrieval (completely mismatched)
    meta_json = json.dumps({
        "document_name": "DOC_FAIL_TEST",
        "title": "Failing Document Test",
        "author": "Tester",
        "year": 2024
    })
    # Probe questions that search for irrelevant topics
    unrelated_probes = json.dumps(["Quantum entanglement in black holes", "Gravitational wave detection", "Dark matter distribution"])
    mock_model = MockChatModel(responses=[meta_json, unrelated_probes, unrelated_probes, unrelated_probes, unrelated_probes])

    report = ingest_markdown_or_pdf(
        raw_markdown=sample_md,
        model=mock_model,
        threshold=0.99, # impossible threshold
        max_iterations=2,
        catalog_csv_path=str(test_catalog)
    )

    assert report.status == "QUARANTINED"
    assert report.final_recall_score < 0.99

    # Verify catalog was NOT modified
    with open(test_catalog, "r", encoding="utf-8") as f:
        content = f.read()
    assert "DOC_FAIL_TEST" not in content

