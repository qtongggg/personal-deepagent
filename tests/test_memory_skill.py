import pytest
from unittest.mock import MagicMock, patch


def test_memory_filter_below_threshold():
    from src.skills.memory_skill import filter_memories_by_score
    raw = [
        {"memory": "Prefers Islamic Finance", "score": 0.5},
        {"memory": "Irrelevant", "score": 0.2},
    ]
    filtered = filter_memories_by_score(raw, threshold=0.4)
    assert len(filtered) == 1
    assert filtered[0]["memory"] == "Prefers Islamic Finance"


def test_search_memory_default_user_id():
    from src.skills.memory_skill import search_memory
    with patch("src.skills.memory_skill.get_memory_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.search.return_value = [
            {"memory": "Researcher interested in Sukuk", "score": 0.85}
        ]
        mock_get_client.return_value = mock_client

        results = search_memory(user_id="", query="Sukuk")
        assert len(results) == 1
        mock_client.search.assert_called_once()
        # Verify user_id defaulted to default_user
        call_kwargs = mock_client.search.call_args.kwargs
        assert call_kwargs.get("user_id") == "default_user"


def test_add_memory_execution():
    from src.skills.memory_skill import add_memory
    with patch("src.skills.memory_skill.get_memory_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.add.return_value = {"results": [{"id": "mem_1", "event": "ADD"}]}
        mock_get_client.return_value = mock_client

        res = add_memory(user_id="user_123", messages=[{"role": "user", "content": "My name is Mah Qing Tong"}])
        assert "results" in res
        mock_client.add.assert_called_once()
        call_kwargs = mock_client.add.call_args.kwargs
        assert call_kwargs.get("user_id") == "user_123"


def test_memory_tools_invocation():
    from src.skills.memory_skill import search_memory_tool, add_memory_tool
    with patch("src.skills.memory_skill.search_memory") as mock_search, \
         patch("src.skills.memory_skill.add_memory") as mock_add:
        mock_search.return_value = [{"memory": "Prefers Sukuk", "score": 0.9}]
        mock_add.return_value = {"status": "success"}

        search_res = search_memory_tool.invoke({"query": "user interest", "user_id": "user_42"})
        assert "Prefers Sukuk" in search_res

        add_res = add_memory_tool.invoke({"content": "User is a researcher at INCEIF", "user_id": "user_42"})
        assert "success" in add_res
