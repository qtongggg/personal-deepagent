import os
import sys
from typing import Any, Dict, List, Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chromadb
from src.config import get_settings
from src.utils.chroma import get_chroma_client

DEFAULT_CHUNKS: List[Dict[str, Any]] = [
    {
        "chunk_id": "irp5_chunk_001",
        "document_name": "IRP 5",
        "header_path": "/INTRODUCTION",
        "chunk_content": "This research paper addresses the critical challenges in realizing the higher objectives of Islamic law (Maqasid al-Shariah) within the contemporary Islamic Capital Market, specifically focusing on Sukuk structures and issuance practices.",
    },
    {
        "chunk_id": "irp5_chunk_002",
        "document_name": "IRP 5",
        "header_path": "Maqasid al-Shariah > Structural Challenges in Sukuk",
        "chunk_content": "Current market practices overwhelmingly favor asset-based Sukuk over asset-backed Sukuk. In asset-based structures, investors possess beneficial ownership without true sale recourse, creating divergence between legal form and economic substance.",
    },
    {
        "chunk_id": "irp5_chunk_003",
        "document_name": "IRP 5",
        "header_path": "Recommendations > Realizing Economic Justice",
        "chunk_content": "To achieve genuine Maqasid alignment, the Islamic capital market must transition toward asset-backed structures that embody genuine risk-sharing, equitable wealth distribution, and tangible asset ownership.",
    },
    {
        "chunk_id": "irp11_chunk_001",
        "document_name": "IRP 11",
        "header_path": "/INTRODUCTION",
        "chunk_content": "This study explores Islamic finance as an architectural framework for global financial stability, proposing governance models that mitigate systemic risk through equity-based risk sharing and prohibition of excessive leverage.",
    },
    {
        "chunk_id": "irp11_chunk_002",
        "document_name": "IRP 11",
        "header_path": "Global Stability > Architecture and Governance",
        "chunk_content": "Systemic financial crises originate primarily from credit decoupling and debt multiplication. Islamic finance architecture reinforces financial stability by tying financial claims directly to real sector economic activity.",
    },
    {
        "chunk_id": "irp11_chunk_003",
        "document_name": "IRP 11",
        "header_path": "Governance > Macroprudential Frameworks",
        "chunk_content": "The institutional governance framework requires regulatory harmonization across Shariah boards and central monetary authorities, ensuring countercyclical capital buffers and transparent risk disclosure.",
    },
    {
        "chunk_id": "takaful_chunk_001",
        "document_name": "Takaful Overview",
        "header_path": "Takaful > Core Principles",
        "chunk_content": "Takaful operates on the principles of mutual cooperation (Ta'awun), shared responsibility, and mutual donation (Tabarru'), eliminating Gharar (uncertainty) and Maysir (gambling) inherent in conventional insurance.",
    },
    {
        "chunk_id": "waqf_chunk_001",
        "document_name": "IRP 25",
        "header_path": "Waqf > Microfinance Integration",
        "chunk_content": "Waqf-based microfinance combines perpetual endowment capital with targeted Islamic financing instruments to provide zero-cost or subsidized development funds to underprivileged micro-entrepreneurs.",
    },
]





def seed_knowledge_chunks(client: Optional[chromadb.ClientAPI] = None, collection_name: str = "document_knowledge") -> int:
    client = client or get_chroma_client()
    collection = client.get_or_create_collection(collection_name)

    ids = [c["chunk_id"] for c in DEFAULT_CHUNKS]
    try:
        existing_ids = set(collection.get(ids=ids)["ids"])
    except Exception:
        existing_ids = set()

    missing_chunks = [c for c in DEFAULT_CHUNKS if c["chunk_id"] not in existing_ids]
    if not missing_chunks:
        return collection.count()

    missing_ids = [c["chunk_id"] for c in missing_chunks]
    documents = [c["chunk_content"] for c in missing_chunks]
    metadatas = [
        {
            "document_name": c["document_name"],
            "header_path": c["header_path"],
            "chunk_id": c["chunk_id"],
        }
        for c in missing_chunks
    ]

    collection.upsert(ids=missing_ids, documents=documents, metadatas=metadatas)
    return collection.count()


if __name__ == "__main__":
    count = seed_knowledge_chunks()
    print(f"Ingested {count} chunks into Chroma collection 'document_knowledge'.")
