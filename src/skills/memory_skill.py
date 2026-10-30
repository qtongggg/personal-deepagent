import json
import logging
from typing import Any, Dict, List, Optional, Union
from langchain_core.tools import tool
from src.config import get_settings

logger = logging.getLogger(__name__)

_CLIENT = None


class LocalInMemoryMemoryClient:
    """Lightweight fallback in-memory memory store when MEM0_API_KEY is not provided."""

    def __init__(self):
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    def search(self, query: str, user_id: str = "default_user") -> List[Dict[str, Any]]:
        user_mems = self._store.get(user_id, [])
        query_words = set(query.lower().split())
        results = []
        for item in user_mems:
            mem_text = item.get("memory", "").lower()
            # Simple keyword overlap scoring for fallback
            overlap = sum(1 for w in query_words if w in mem_text)
            score = round(min(1.0, 0.4 + (0.2 * overlap)), 2) if overlap > 0 else 0.5
            results.append({**item, "score": score})
        return results

    def add(self, messages: Any, user_id: str = "default_user") -> Dict[str, Any]:
        if user_id not in self._store:
            self._store[user_id] = []

        if isinstance(messages, str):
            mem_text = messages
        elif isinstance(messages, list):
            mem_text = " ".join(
                m.get("content", "") if isinstance(m, dict) else str(m)
                for m in messages
            )
        else:
            mem_text = str(messages)

        record = {
            "id": f"mem_{len(self._store[user_id]) + 1}",
            "memory": mem_text,
            "user_id": user_id,
        }
        self._store[user_id].append(record)
        return {"status": "success", "results": [record]}


def get_memory_client():
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT

    settings = get_settings()
    if settings.MEM0_API_KEY and settings.MEM0_API_KEY != "your_mem0_api_key_here":
        try:
            from mem0 import MemoryClient
            _CLIENT = MemoryClient(api_key=settings.MEM0_API_KEY)
            return _CLIENT
        except Exception as e:
            logger.warning(f"Failed to initialize remote Mem0 client: {e}. Falling back to in-memory store.")

    _CLIENT = LocalInMemoryMemoryClient()
    return _CLIENT


def filter_memories_by_score(memories: Any, threshold: float = 0.4) -> List[Dict[str, Any]]:
    """Filter memories that meet or exceed the similarity threshold."""
    if isinstance(memories, dict) and "results" in memories:
        items = memories["results"]
    elif isinstance(memories, list):
        items = memories
    else:
        return []

    return [m for m in items if isinstance(m, dict) and m.get("score", 1.0) >= threshold]


def search_memory(user_id: Optional[str], query: str) -> List[Dict[str, Any]]:
    """Search long-term memory for a user profile, preferences, or past topics."""
    settings = get_settings()
    active_user_id = user_id.strip() if user_id and user_id.strip() else "default_user"
    client = get_memory_client()
    raw = client.search(query, user_id=active_user_id)
    return filter_memories_by_score(raw, threshold=settings.SIMILARITY_THRESHOLD)


def add_memory(user_id: Optional[str], messages: Union[List[Dict[str, Any]], str]) -> Dict[str, Any]:
    """Persist facts, user identity, preferences, or research comparison topics."""
    active_user_id = user_id.strip() if user_id and user_id.strip() else "default_user"
    client = get_memory_client()
    return client.add(messages=messages, user_id=active_user_id)


@tool("search_memory")
def search_memory_tool(query: str, user_id: str = "default_user") -> str:
    """Search long-term memory for user background, preferences, or past research topics.
    
    Bypass this tool for pure counts, catalog listings, or lexicon definitions.
    """
    try:
        memories = search_memory(user_id=user_id, query=query)
        if not memories:
            return f"No memories found for user '{user_id}' matching '{query}'."
        return json.dumps(memories, indent=2)
    except Exception as e:
        return f"Error searching memory: {e}"


@tool("add_memory")
def add_memory_tool(content: str, user_id: str = "default_user") -> str:
    """Commit facts, user identity, preferences, or research comparison topics to long-term memory.
    
    Must be called immediately when the user shares their identity or in Phase 3.5 of paper comparisons.
    """
    try:
        res = add_memory(user_id=user_id, messages=[{"role": "user", "content": content}])
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error adding memory: {e}"
