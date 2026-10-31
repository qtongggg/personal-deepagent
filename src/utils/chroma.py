import os
from typing import Optional
import chromadb
from src.config import get_settings


def get_chroma_client(persist_dir: Optional[str] = None) -> chromadb.ClientAPI:
    """Return configured ChromaDB PersistentClient."""
    settings = get_settings()
    target_dir = persist_dir or settings.CHROMA_PERSIST_DIR
    if not os.path.isabs(target_dir):
        target_dir = os.path.abspath(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    return chromadb.PersistentClient(path=target_dir)

