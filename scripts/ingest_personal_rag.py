import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rank_bm25 import BM25Okapi
from flashrank import Ranker, RerankRequest
from src.utils.chroma import get_chroma_client

PERSONAL_COLLECTION_NAME = "personal_resume_knowledge"
PERSONAL_RAG_DIR = Path(__file__).resolve().parent.parent / "data" / "personal_rag"


def parse_markdown_to_chunks(file_path: Path) -> List[Dict[str, Any]]:
    """Parse a Markdown document into semantic, section-aware chunks."""
    text = file_path.read_text(encoding="utf-8")
    doc_stem = file_path.stem.lower()

    # Determine default category based on filename
    category_map = {
        "resume": "resume",
        "profile_rag": "profile",
        "deepagent_architecture": "architecture",
        "adrs_and_decisions": "decisions",
    }
    default_cat = category_map.get(doc_stem, "general")

    # Split on markdown section headers (## or ###)
    sections = re.split(r"\n(?=#{1,3}\s+)", text)
    chunks = []
    chunk_counter = 1

    current_main_header = ""

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue

        lines = sec.splitlines()
        header_line = lines[0].strip() if lines else ""

        # Track main header
        if header_line.startswith("# ") and not header_line.startswith("## "):
            current_main_header = header_line.lstrip("#").strip()
            # If section only has the H1 title and short intro, we can still index it
            if len(lines) <= 2:
                continue

        is_sub = header_line.startswith("### ")
        title = header_line.lstrip("#").strip()

        # Build clean hierarchical header path
        if is_sub and current_main_header:
            header_path = f"/{current_main_header}/{title}"
        elif current_main_header and current_main_header != title:
            header_path = f"/{current_main_header}/{title}"
        else:
            header_path = f"/{title}"

        # Refine category from content/header
        title_lower = title.lower()
        if any(k in title_lower for k in ["experience", "zetrix", "nielsen", "niq"]):
            category = "experience"
        elif any(k in title_lower for k in ["education", "monash", "degree"]):
            category = "education"
        elif any(k in title_lower for k in ["project", "deepagent", "dify", "f1", "sql", "expense"]):
            category = "projects"
        elif any(k in title_lower for k in ["skill", "stack", "toolkit", "proficienc"]):
            category = "skills"
        elif any(k in title_lower for k in ["adr", "decision", "harness", "principle"]):
            category = "decisions"
        elif any(k in title_lower for k in ["honor", "award", "competition", "leadership"]):
            category = "awards_leadership"
        else:
            category = default_cat

        chunk_id = f"{doc_stem}_chunk_{chunk_counter:03d}"
        chunk_counter += 1

        chunks.append({
            "chunk_id": chunk_id,
            "doc_name": file_path.name,
            "header_path": header_path,
            "category": category,
            "title": title,
            "chunk_content": sec,
        })

    return chunks


def ingest_all_personal_rag_files() -> int:
    """Ingest all markdown files from data/personal_rag into ChromaDB."""
    client = get_chroma_client()
    # Reset/recreate collection for fresh, clean indexing
    try:
        client.delete_collection(PERSONAL_COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=PERSONAL_COLLECTION_NAME,
        metadata={"description": "Mah Qing Tong (QT) Personal Resume & Agent Knowledge Base"},
    )

    all_chunks: List[Dict[str, Any]] = []
    md_files = sorted(PERSONAL_RAG_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {PERSONAL_RAG_DIR}")
        return 0

    for f in md_files:
        file_chunks = parse_markdown_to_chunks(f)
        all_chunks.extend(file_chunks)
        print(f"Parsed {len(file_chunks)} chunks from: {f.name}")

    if not all_chunks:
        print("No chunks generated.")
        return 0

    ids = [c["chunk_id"] for c in all_chunks]
    documents = [c["chunk_content"] for c in all_chunks]
    metadatas = [
        {
            "chunk_id": c["chunk_id"],
            "doc_name": c["doc_name"],
            "header_path": c["header_path"],
            "category": c["category"],
            "title": c["title"],
        }
        for c in all_chunks
    ]

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    count = collection.count()
    print(f"\nSuccessfully indexed {count} chunks into Chroma collection '{PERSONAL_COLLECTION_NAME}'.")
    return count


def test_personal_retriever(query: str, top_k: int = 3):
    """Test retrieval using Dense Chroma + BM25 + FlashRank Reranker."""
    client = get_chroma_client()
    collection = client.get_collection(PERSONAL_COLLECTION_NAME)

    # 1. Fetch all docs for BM25
    all_data = collection.get()
    all_docs = all_data.get("documents", [])
    all_ids = all_data.get("ids", [])
    all_metas = all_data.get("metadatas", [])

    if not all_docs:
        print("Collection is empty!")
        return []

    # 2. Dense search (fetch candidate pool of top 8)
    dense_res = collection.query(query_texts=[query], n_results=min(8, len(all_docs)))
    dense_ids = dense_res.get("ids", [[]])[0]

    # 3. Sparse BM25 scoring
    tokenized_corpus = [doc.lower().split() for doc in all_docs]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)

    # Top BM25 candidates
    bm25_ranked_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:8]
    bm25_ids = [all_ids[i] for i in bm25_ranked_indices]

    # Union candidate IDs
    candidate_id_set = list(dict.fromkeys(dense_ids + bm25_ids))
    candidates = []
    for cid in candidate_id_set:
        idx = all_ids.index(cid)
        candidates.append({
            "id": cid,
            "text": all_docs[idx],
            "meta": all_metas[idx],
        })

    # 4. FlashRank Cross-Encoder Reranker
    try:
        ranker = Ranker(model_name="ms-marco-TinyBERT-L-2-v2", cache_dir="data/.cache_flashrank")
        passages = [{"id": c["id"], "text": c["text"], "meta": c["meta"]} for c in candidates]
        rerank_req = RerankRequest(query=query, passages=passages)
        reranked = ranker.rerank(rerank_req)
        final_results = reranked[:top_k]
    except Exception as e:
        print(f"FlashRank fallback (reason: {e})")
        final_results = candidates[:top_k]

    print(f"\n=======================================================")
    print(f"QUERY: '{query}'")
    print(f"Retrieved Top-{len(final_results)} Reranked Results:")
    for rank, item in enumerate(final_results, 1):
        meta = item.get("meta", {})
        score = item.get("score", "N/A")
        title = str(meta.get('title', 'Unknown')).encode('ascii', errors='replace').decode('ascii')
        path = str(meta.get('header_path', '')).encode('ascii', errors='replace').decode('ascii')
        doc = str(meta.get('doc_name', '')).encode('ascii', errors='replace').decode('ascii')
        print(f"  [{rank}] {title} (Score: {score})")
        print(f"      Path: {path} | Doc: {doc}")
        snippet = str(item.get("text", ""))[:140].replace("\n", " ").encode('ascii', errors='replace').decode('ascii')
        print(f"      Snippet: {snippet}...")
    print(f"=======================================================")
    return final_results


if __name__ == "__main__":
    count = ingest_all_personal_rag_files()
    if count > 0:
        # Run test verification queries
        test_personal_retriever("What did QT build at Zetrix AI?")
        test_personal_retriever("How does Personal DeepAgent architecture work?")
        test_personal_retriever("What is QT's education and degree honours?")
        test_personal_retriever("Why did QT choose Signal Orange and the 3D ASCII Mobius Strip?")
