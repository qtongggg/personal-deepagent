import json
from unittest.mock import MagicMock, patch
import pytest
from src.utils.rag_evaluator import (
    evaluate_answer_relevance_jev,
    evaluate_answer_relevance,
    evaluate_faithfulness_jev,
)


def test_evaluate_answer_relevance_jev_score_primitive():
    """Verify Jev 'score' primitive evaluates continuous answer relevance."""
    mock_jev_resp = {
        "answers": {
            "relevance": {
                "score": 0.92,
                "confidence": 0.98,
                "distribution": {
                    "completely_answers": 0.85,
                    "partially_answers": 0.12,
                    "tangential": 0.03,
                    "irrelevant": 0.0,
                },
            }
        }
    }

    mock_resp_obj = MagicMock()
    mock_resp_obj.__enter__.return_value = mock_resp_obj
    mock_resp_obj.read.return_value = json.dumps(mock_jev_resp).encode("utf-8")

    with patch("urllib.request.urlopen", return_value=mock_resp_obj):
        result = evaluate_answer_relevance_jev(
            query="Compare ReAct vs Reflexion reasoning loops",
            response_text="ReAct interleaves thoughts and actions, whereas Reflexion adds episodic self-critique.",
            api_key="mock_key",
        )

    assert result.score == 0.92
    assert "Jev System-1 score primitive" in result.reasoning


def test_evaluate_faithfulness_jev_choice_diagnosis():
    """Verify evaluate_faithfulness_jev extracts category via choice rubric."""
    mock_jev_resp = {
        "answers": {
            "claim_0": {"noul": 0.95},
            "claim_0_cat": {"choice": "fully_substantiated"},
            "claim_1": {"noul": 0.15},
            "claim_1_cat": {"choice": "unsupported_hallucination"},
        }
    }

    mock_resp_obj = MagicMock()
    mock_resp_obj.__enter__.return_value = mock_resp_obj
    mock_resp_obj.read.return_value = json.dumps(mock_jev_resp).encode("utf-8")

    with patch("urllib.request.urlopen", return_value=mock_resp_obj), \
         patch("src.utils.rag_evaluator.extract_atomic_statements", return_value=["Claim 1", "Claim 2"]):
        result = evaluate_faithfulness_jev(
            response_text="Claim 1. Claim 2.",
            retrieved_contexts=["Context passage supporting claim 1."],
            api_key="mock_key",
        )

    assert result.total_claims == 2
    assert result.supported_claims == 1
    assert result.score == 0.5
    assert len(result.unsupported_claims) == 1
    assert result.unsupported_claims[0].category == "unsupported_hallucination"
