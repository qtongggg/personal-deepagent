import pytest
from src.skills.ingestion.extractor import extract_metadata
from src.skills.ingestion.schemas import DocumentMetadata
from tests.mock_model import MockChatModel


def test_extract_metadata_structured_llm():
    sample_text = (
        "arXiv:2403.12345v1 [cs.AI] 18 Mar 2024\n"
        "Agentic Reasoning in Autonomous Networks\n"
        "Alice Smith, Bob Jones\n"
        "Abstract: This paper presents an autonomous agent framework..."
    )
    mock_model = MockChatModel(responses=[
        '{"document_name": "ARXIV_2403_12345", "title": "Agentic Reasoning in Autonomous Networks", "author": "Alice Smith, Bob Jones", "year": 2024, "document_type": "Research Paper", "source_url": "https://arxiv.org/abs/2403.12345"}'
    ])
    meta = extract_metadata(first_page_text=sample_text, model=mock_model)
    assert meta.document_name == "ARXIV_2403_12345"
    assert meta.title == "Agentic Reasoning in Autonomous Networks"
    assert meta.author == "Alice Smith, Bob Jones"
    assert meta.year == 2024
    assert meta.source_url == "https://arxiv.org/abs/2403.12345"


def test_extract_metadata_fallback_heuristic():
    """Review Focus 1: Heuristic fallback when LLM output is unavailable or non-JSON."""
    sample_text = (
        "Deep Learning for Financial Risk Prediction\n"
        "By Z. Hassan, 2023\n"
        "Abstract: We propose an ensemble architecture."
    )
    # Model returns empty or malformed string
    mock_model = MockChatModel(responses=["Not a json"])
    meta = extract_metadata(first_page_text=sample_text, fallback_slug="DOC_RISK_2023", model=mock_model)
    assert meta.document_name == "DOC_RISK_2023"
    assert "Deep Learning for Financial Risk Prediction" in meta.title
    assert meta.year == 2023


def test_extract_metadata_missing_fields_no_crash():
    """Review Focus 1: Completely missing year or author must have defaults and not crash."""
    sample_text = "Untitled Document\nSome quick notes with no date or author."
    mock_model = MockChatModel(responses=["I cannot parse this"])
    meta = extract_metadata(first_page_text=sample_text, fallback_slug="UNTITLED_NOTES", model=mock_model)
    assert meta.document_name == "UNTITLED_NOTES"
    assert meta.author == "Unknown" or meta.author is None
    assert isinstance(meta.year, int) or meta.year is None

