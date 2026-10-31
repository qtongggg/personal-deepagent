from src.skills.ingestion.schemas import (
    DocumentMetadata,
    IngestionChunk,
    EvaluationProbe,
    EvaluationResult,
    IngestionReport,
)


def test_document_metadata_schema():
    meta = DocumentMetadata(
        document_name="ARXIV_2401_001",
        title="Sample AI Research",
        author="John Doe; Jane Smith",
        year=2024,
        document_type="Research Paper",
        source_url="https://arxiv.org/abs/2401.001",
    )
    assert meta.document_name == "ARXIV_2401_001"
    assert meta.year == 2024
    assert meta.publisher == "arXiv" or meta.publisher is None


def test_ingestion_chunk_schema():
    chunk = IngestionChunk(
        chunk_id="doc1_chunk_001",
        document_name="DOC1",
        header_path="Introduction > Background",
        chunk_content="This is sample content.",
    )
    assert chunk.chunk_id == "doc1_chunk_001"
    assert "Background" in chunk.header_path


def test_evaluation_result_schema():
    eval_res = EvaluationResult(
        total_probes=6,
        successful_retrievals=5,
        recall_score=0.833,
        passed=True,
        failing_sections=[],
    )
    assert eval_res.passed is True
    assert eval_res.recall_score > 0.8

