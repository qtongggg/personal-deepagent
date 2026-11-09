import os
from typing import Optional, Dict
import chromadb
from src.config import get_settings

_CHROMA_CLIENTS: Dict[str, chromadb.ClientAPI] = {}


def get_chroma_client(persist_dir: Optional[str] = None) -> chromadb.ClientAPI:
    """Return configured ChromaDB PersistentClient (cached singleton per path)."""
    settings = get_settings()
    target_dir = persist_dir or settings.CHROMA_PERSIST_DIR
    if not os.path.isabs(target_dir):
        target_dir = os.path.abspath(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    
    global _CHROMA_CLIENTS
    if target_dir not in _CHROMA_CLIENTS:
        _CHROMA_CLIENTS[target_dir] = chromadb.PersistentClient(path=target_dir)
    return _CHROMA_CLIENTS[target_dir]
