import json
from unittest.mock import MagicMock, patch
import pytest
from src.skills.retriever_skill import _rerank_with_jev, retrieve_knowledge_chunks


def test_rerank_with_jev_choice_rubric_and_noise_pruning():
    """Verify Jev 3-way choice rubric grades candidates and prunes noise below threshold."""
    candidates = [
        {
            "chunk_id": "chunk_react_loop",
            "document_name": "ReAct",
            "chunk_content": "ReAct interleaves Thought, Action, and Observation loops to reason over tools.",
            "distance": 0.1,
        },
        {
            "chunk_id": "chunk_react_intro",
            "document_name": "ReAct",
            "chunk_content": "Recent advances in language models have shown promising results across NLP tasks.",
            "distance": 0.3,
        },
        {
            "chunk_id": "chunk_noise_distractor",
            "document_name": "Distractor",
            "chunk_content": "Acoustic emission testing detects high frequency ultrasonic leakage in pipe systems.",
            "distance": 0.8,
        },
    ]

    mock_jev_resp = {
        "answers": {
            "cand_0": {
                "choice": "strong",
                "distribution": {"strong": 0.90, "partial": 0.10, "wrong": 0.0},
            },
            "cand_1": {
                "choice": "partial",
                "distribution": {"strong": 0.20, "partial": 0.70, "wrong": 0.10},
            },
            "cand_2": {
                "choice": "wrong",
                "distribution": {"strong": 0.0, "partial": 0.10, "wrong": 0.90},
            },
        }
    }

    mock_resp_obj = MagicMock()
    mock_resp_obj.__enter__.return_value = mock_resp_obj
    mock_resp_obj.read.return_value = json.dumps(mock_jev_resp).encode("utf-8")

    with patch("urllib.request.urlopen", return_value=mock_resp_obj):
        results = _rerank_with_jev(
            query="ReAct reasoning loops and thought action observations",
            candidates=candidates,
            top_k=4,
            threshold=0.40,
            api_key="mock_key",
        )

    assert results is not None
    # chunk_2 should be dropped by the noise pruning gate because its score is 0.05 < 0.40
    assert len(results) == 2
    assert results[0]["chunk_id"] == "chunk_react_loop"
    assert results[0]["rerank_score"] >= 0.85
    assert results[0]["reranker_engine"] == "jev_system_one"
    assert results[0]["rerank_rubric"] == "strong"

    assert results[1]["chunk_id"] == "chunk_react_intro"
    assert results[1]["rerank_score"] >= 0.50
    assert results[1]["rerank_rubric"] == "partial"


def test_rerank_with_jev_fallback_when_no_key():
    """Verify _rerank_with_jev returns None when no key is configured."""
    with patch.dict("os.environ", {}, clear=True):
        res = _rerank_with_jev(
            query="test query",
            candidates=[{"chunk_id": "c1", "chunk_content": "test"}],
            api_key=None,
        )
        assert res is None
