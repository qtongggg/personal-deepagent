import os
import pytest
from scripts.ingest import seed_knowledge_chunks
from src.config import get_settings
from src.utils.chroma import get_chroma_client
import src.skills.retriever_skill as retriever_skill


@pytest.fixture(autouse=True, scope="session")
def setup_test_chroma(tmp_path_factory):
    """Isolate test ChromaDB storage so tests never pollute production .chroma."""
    test_dir = str(tmp_path_factory.mktemp("chroma_test"))
    original_persist = os.environ.get("CHROMA_PERSIST_DIR")
    os.environ["CHROMA_PERSIST_DIR"] = test_dir
    get_settings.cache_clear()

    # Reset retriever_skill singleton state
    retriever_skill._CLIENT = None
    retriever_skill._COLLECTION = None

    # Seed test benchmark chunks into the isolated test directory
    client = get_chroma_client(persist_dir=test_dir)
    seed_knowledge_chunks(client=client, collection_name="document_knowledge")

    yield

    # Teardown
    if original_persist is not None:
        os.environ["CHROMA_PERSIST_DIR"] = original_persist
    else:
        os.environ.pop("CHROMA_PERSIST_DIR", None)
    get_settings.cache_clear()
    retriever_skill._CLIENT = None
    retriever_skill._COLLECTION = None

