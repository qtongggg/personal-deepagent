import argparse
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.ingest import get_chroma_client
from src.skills.ingestion.chunker import chunk_markdown
from src.skills.ingestion.extractor import extract_metadata
from src.skills.ingestion.parser import parse_pdf_to_clean_markdown


def list_all_documents(collection):
    """List all documents stored in ChromaDB and their chunk counts."""
    data = collection.get()
    if not data or not data["ids"]:
        print("ChromaDB collection 'document_knowledge' is empty.")
        return

    doc_counts = {}
    for meta in data["metadatas"]:
        doc_name = meta.get("document_name", "UNKNOWN")
        doc_counts[doc_name] = doc_counts.get(doc_name, 0) + 1

    print("==================================================")
    print("  STORED DOCUMENTS IN CHROMADB")
    print("==================================================")
    for doc, count in sorted(doc_counts.items()):
        print(f"  * {doc:<25} ({count} chunks)")
    print("==================================================")
    print("\nTo inspect a document's chunks, run:")
    print("  python scripts/inspect_chunks.py <DOCUMENT_NAME>\n")


def inspect_stored_chunks(collection, document_name: str, full: bool = False):
    """Retrieve and display chunks for a specific document from ChromaDB."""
    data = collection.get(where={"document_name": document_name})
    if not data or not data["ids"]:
        print(f"No chunks found for document '{document_name}' in ChromaDB.")
        return

    total = len(data["ids"])
    print(f"\n==================================================")
    print(f"  CHUNKS FOR: {document_name} ({total} Total)")
    print(f"==================================================")

    for i in range(total):
        cid = data["ids"][i]
        meta = data["metadatas"][i]
        hpath = meta.get("header_path", "No header")
        text = data["documents"][i]
        words = len(text.split())

        print(f"\n[{i+1}/{total}] Chunk ID : {cid}")
        print(f"    Section  : {hpath}")
        print(f"    Words    : {words}")
        if full:
            print("    --- Content ---")
            print(text)
            print("    ---------------")
        else:
            preview = text.replace("\n", " ").strip()
            print(f"    Content  : {preview[:140]}...")


def inspect_file_chunking(file_path: str, full: bool = False):
    """Parse a local PDF or Markdown file and display candidate chunks on the fly."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    print(f"Parsing: {file_path} ...")
    if file_path.lower().endswith(".pdf"):
        md = parse_pdf_to_clean_markdown(file_path)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            md = f.read()

    meta = extract_metadata(md[:3000], fallback_slug="DOC_PREVIEW")
    chunks = chunk_markdown(md, meta)

    print(f"\n==================================================")
    print(f"  ON-THE-FLY CHUNKING PREVIEW: {meta.document_name}")
    print(f"  Identified Title: {meta.title}")
    print(f"  Total Chunks    : {len(chunks)}")
    print(f"==================================================")

    for i, c in enumerate(chunks):
        print(f"\n[{i+1}/{len(chunks)}] Chunk ID : {c.chunk_id}")
        print(f"    Section  : {c.header_path}")
        print(f"    Words    : {c.word_count}")
        if full:
            print("    --- Content ---")
            print(c.chunk_content)
            print("    ---------------")
        else:
            preview = c.chunk_content.replace("\n", " ").strip()
            print(f"    Content  : {preview[:140]}...")


def main():
    parser = argparse.ArgumentParser(description="Inspect chunks stored in ChromaDB or preview file chunking.")
    parser.add_argument("document", nargs="?", default=None, help="Document slug (e.g. ARXIV_2610_40589, 'IRP 5')")
    parser.add_argument("--file", default=None, help="Path to local PDF or Markdown to chunk and inspect on the fly")
    parser.add_argument("--full", action="store_true", help="Print full chunk contents instead of preview snippets")
    args = parser.parse_args()

    if args.file:
        inspect_file_chunking(args.file, full=args.full)
        return

    client = get_chroma_client()
    collection = client.get_or_create_collection("document_knowledge")

    if args.document:
        inspect_stored_chunks(collection, args.document, full=args.full)
    else:
        list_all_documents(collection)


if __name__ == "__main__":
    main()
