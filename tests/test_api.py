import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from src.api import app
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert "version" in data


def test_get_documents_endpoint(client):
    response = client.get("/api/documents")
    assert response.status_code == 200
    docs = response.json()
    assert isinstance(docs, list)
    assert len(docs) >= 1
    # Check schema
    doc = docs[0]
    assert "document_name" in doc
    assert "total_chunks" in doc


def test_get_chunks_for_document(client):
    # In test isolation, IRP 5 is seeded by conftest.py
    response = client.get("/api/documents/IRP 5/chunks")
    assert response.status_code == 200
    chunks = response.json()
    assert isinstance(chunks, list)
    assert len(chunks) >= 1
    assert "chunk_id" in chunks[0]
    assert "header_path" in chunks[0]
    assert "chunk_content" in chunks[0]
    assert "word_count" in chunks[0]


def test_get_chunks_non_existent_document(client):
    response = client.get("/api/documents/NON_EXISTENT_DOC_XYZ/chunks")
    assert response.status_code == 404
    assert "not found" in response.json().get("detail", "").lower()


def test_semantic_search_endpoint(client):
    response = client.get("/api/search?q=sukuk&top_k=3")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) >= 1
    assert "document_name" in results[0]
    assert "chunk_content" in results[0]


def test_semantic_search_empty_query(client):
    response = client.get("/api/search?q=")
    assert response.status_code == 400 or response.status_code == 422


def test_root_viewer_html_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Personal DeepAgent" in response.text
    assert "Chunk Studio" in response.text


def test_ingest_endpoint_validation(client):
    response = client.post("/api/ingest", json={"source": "", "threshold": 0.8})
    assert response.status_code == 400 or response.status_code == 422


def test_ingest_endpoint_mocked(client, monkeypatch):
    from src.skills.ingestion.schemas import DocumentMetadata, IngestionReport

    def mock_ingest(source, threshold=0.8):
        return IngestionReport(
            document_metadata=DocumentMetadata(
                document_name="MOCK_TEST_DOC",
                title="Mock Test Document",
                author="Test Author",
                year=2025,
            ),
            status="SUCCESS",
            total_chunks=5,
            final_recall_score=0.92,
            iterations_used=1,
        )

    import src.api as api_module
    monkeypatch.setattr(api_module, "run_ingestion_sync", mock_ingest)

    response = client.post("/api/ingest", json={"source": "https://arxiv.org/abs/2610.99999", "threshold": 0.8})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["total_chunks"] == 5
    assert data["document_metadata"]["document_name"] == "MOCK_TEST_DOC"


def test_ingest_threshold_bounds_validation(client):
    # Threshold must be between 0.0 and 1.0
    res_high = client.post("/api/ingest", json={"source": "https://arxiv.org/abs/2401.0001", "threshold": 1.5})
    assert res_high.status_code == 422

    res_low = client.post("/api/ingest", json={"source": "https://arxiv.org/abs/2401.0001", "threshold": -0.2})
    assert res_low.status_code == 422


def test_get_chunks_with_none_metadata_safety(client, monkeypatch):
    class MockCollection:
        def get(self, where=None):
            return {
                "ids": ["mock_c1"],
                "documents": ["Some chunk text without metadata"],
                "metadatas": [None],  # simulates ChromaDB returning None
            }

    class MockClient:
        def get_or_create_collection(self, name):
            return MockCollection()

    import src.api as api_module
    monkeypatch.setattr(api_module, "get_chroma_client", lambda: MockClient())

    response = client.get("/api/documents/TEST_DOC/chunks")
    assert response.status_code == 200
    chunks = response.json()
    assert len(chunks) == 1
    assert chunks[0]["chunk_id"] == "mock_c1"
    assert chunks[0]["header_path"] == "/"

