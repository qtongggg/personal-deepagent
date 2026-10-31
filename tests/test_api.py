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
