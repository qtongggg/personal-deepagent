---
name: ingestion_skill
description: Layer 1 Document Parsing, Section-Aware Semantic Chunking, and Automated Ingestion Quality Evaluation pipeline.
triggers:
  - "Ingest document..."
  - "Index PDF..."
  - "Evaluate chunk quality..."
tools:
  - ingest_document_tool
---

# 📥 Ingestion Skill Specification

## 1. Overview
The **Ingestion Skill** implements the Layer 1 Ingestion and Chunking pipeline. It converts raw academic PDFs and Markdown files into high-quality semantic chunks enriched with hierarchical header paths (`header_path`) and audits chunk health before indexing into ChromaDB.

## 2. Ingestion Stages
1. **Parser (`parser.py`)**:
   - Uses PyMuPDF4LLM to convert PDF pages into clean, structure-preserving Markdown with table syntax.
2. **Chunker (`chunker.py`)**:
   - Section-aware semantic chunking with breadcrumb header path preservation (e.g. `METHOD > 3.2 Reasoning Loop`).
   - Token boundaries: Target ~500–800 tokens per chunk with 10% overlap to preserve cross-boundary context.
3. **Layer 1 Quality Evaluator (`evaluator.py`)**:
   - Audits each chunk against production quality invariants:
     - Minimum content density ($\ge 150$ characters).
     - Valid hierarchical header path.
     - Preserved Markdown table formatting (pipe syntax intact).
     - Token count within bounds.
4. **Vector Store Indexing (`pipeline.py`)**:
   - Generates dense embeddings and indexes chunks into ChromaDB with comprehensive document metadata.
