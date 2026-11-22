---
name: retriever_skill
description: Two-stage Hybrid (Chroma dense embeddings + BM25 sparse keyword) knowledge retrieval with FlashRank cross-encoder reranking.
triggers:
  - "Explain concept..."
  - "Compare paper A and paper B..."
  - "What are the core mechanisms of..."
  - "How does the algorithm work..."
tools:
  - knowledge_retriever
cli_commands:
  - "python scripts/run_industry_benchmark.py --samples 5 --agentic --evaluator jev"
  - "python scripts/benchmark_comparison.py"
---

# 🔍 Retriever Skill Specification

## 1. Overview
The **Retriever Skill** executes semantic search across scientific literature chunks. It uses a high-precision two-stage pipeline:
1. **First-Stage Hybrid Retrieval**: Combines Dense Vector Search (ChromaDB cosine similarity) with Sparse Lexical Search (Rank-BM25) with Reciprocal Rank Fusion (RRF).
2. **Second-Stage Neural Reranking**: Applies a local FlashRank cross-encoder (`ms-marco-TinyBERT-L-2-v2`) to score query-passage interaction and weed out false positives.

## 2. Chunk Structure & Metadata Contract
Every retrieved chunk returned by `knowledge_retriever` adheres to this structured schema:

```json
{
  "document_name": "ICLR_2023_REACT",
  "header_path": "METHOD > 3.1 Reasoning and Action Synergies",
  "chunk_id": "chunk_042",
  "chunk_content": "...text content...",
  "rerank_score": 0.892,
  "source_url": "https://arxiv.org/abs/2210.03629"
}
```

## 3. Operational Protocols & Sufficiency Gates
1. **Parallel 2-Hop Comparison Protocol**:
   - **Hop 1 (Structural Overview)**: Retrieve introductory chunks (`header_path: /INTRODUCTION`) concurrently for all papers being compared.
   - **Hop 2 (Surgical Mechanism Dives)**: Concurrently query specific mechanism, ablation, and benchmark passages for all papers in parallel within the same turn.
2. **Sufficiency Gate**:
   - For comparative queries, ensure at least **3 to 4 substantive chunks per paper** (target 8 chunks total) before concluding retrieval.
3. **Targeted Filtering**:
   - Use `document_filter` (e.g. `'ICLR_2023_REACT'`) when targeting a specific publication to eliminate cross-contamination from unrelated papers.
4. **Virtual Workspace Scratchpad Offloading**:
   - When processing more than 6 chunks, write intermediate notes into `/workspace/comparison_notes.md` via `write_file` to keep the context window lean and prevent token dilution.
