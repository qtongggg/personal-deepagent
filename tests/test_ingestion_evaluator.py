import json
import pytest
from src.skills.ingestion.evaluator import evaluate_chunks, generate_section_probes
from src.skills.ingestion.schemas import IngestionChunk
from tests.mock_model import MockChatModel


def test_generate_section_probes():
    chunk = IngestionChunk(
        chunk_id="c1",
        document_name="DOC1",
        header_path="Introduction > Stability",
        chunk_content="This paper proposes macroprudential buffers for systemic stability."
    )
    mock_model = MockChatModel(responses=[
        json.dumps([
            "What buffers does the paper propose?",
            "How is systemic stability achieved?",
            "Explain macroprudential frameworks in the study."
        ])
    ])
    probes = generate_section_probes(chunk, model=mock_model)
    assert len(probes) == 3
    assert probes[0].target_header_path == "Introduction > Stability"
    assert "buffers" in probes[0].query_text


def test_evaluate_chunks_passing_score():
    chunks = [
        IngestionChunk(
            chunk_id="c1",
            document_name="DOC_EVAL_01",
            header_path="/INTRODUCTION",
            chunk_content="Islamic finance serves as an architecture for global financial stability through equity risk-sharing."
        ),
        IngestionChunk(
            chunk_id="c2",
            document_name="DOC_EVAL_01",
            header_path="Governance > Macroprudential",
            chunk_content="Macroprudential buffers require regulatory coordination between central monetary authorities and Shariah boards."
        )
    ]

    # Mock responses for probe generation for each chunk
    probes_chunk_1 = json.dumps([
        "How does Islamic finance ensure financial stability?",
        "What is the role of equity risk-sharing in stability?",
        "Explain the architectural stability framework."
    ])
    probes_chunk_2 = json.dumps([
        "What coordination is needed for macroprudential buffers?",
        "How do central monetary authorities work with Shariah boards?",
        "Describe regulatory harmonization governance."
    ])
    mock_model = MockChatModel(responses=[probes_chunk_1, probes_chunk_2])

    result = evaluate_chunks(chunks, model=mock_model, threshold=0.8)
    assert result.total_probes == 6
    assert result.recall_score >= 0.8
    assert result.passed is True
    assert len(result.failing_sections) == 0

