import pytest


def test_retriever_returns_chunk_metadata():
    from src.skills.retriever_skill import retrieve_knowledge_chunks
    chunks = retrieve_knowledge_chunks("Takaful principles", top_k=2)
    assert len(chunks) <= 2
    for chunk in chunks:
        assert "document_name" in chunk
        assert "header_path" in chunk
        assert "chunk_content" in chunk


def test_retriever_filter_by_document():
    from src.skills.retriever_skill import retrieve_knowledge_chunks
    chunks = retrieve_knowledge_chunks("Sukuk structures", top_k=5, document_filter="IRP 5")
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk["document_name"] == "IRP 5"


def test_retriever_tool_execution():
    from src.skills.retriever_skill import retriever_tool
    output = retriever_tool.invoke({"query": "Maqasid Sukuk", "document_filter": "IRP 5"})
    assert "IRP 5" in output
    assert "chunk_content" in output or "document_name" in output


def test_retriever_hybrid_and_rerank_top_4():
    from src.skills.retriever_skill import retrieve_knowledge_chunks
    # Default top_k is 4 (target 4 chunks per paper, 8 total for 2 papers)
    chunks = retrieve_knowledge_chunks("ReAct reasoning and action ALFWorld benchmark")
    assert len(chunks) <= 4
    assert len(chunks) > 0
    # Verify FlashRank rerank score attached
    assert "rerank_score" in chunks[0]
    assert isinstance(chunks[0]["rerank_score"], float)
