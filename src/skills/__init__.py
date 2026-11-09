"""Pluggable skills package for DeepAgent."""
from src.skills.catalog_skill import catalog_tool
from src.skills.memory_skill import add_memory_tool, search_memory_tool
from src.skills.retriever_skill import retriever_tool
from src.skills.ingestion.pipeline import ingest_document_tool
from src.skills.browser_tab_skill import browse_and_extract_web_updates

__all__ = [
    "catalog_tool",
    "retriever_tool",
    "search_memory_tool",
    "add_memory_tool",
    "ingest_document_tool",
    "browse_and_extract_web_updates",
]

