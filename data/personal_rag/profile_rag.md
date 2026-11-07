# MAH QING TONG (QT) — PROFILE & RAG ARCHITECTURAL KNOWLEDGE BASE

## Architectural Philosophy & Engineering Standards

### 1. The Death of Naive RAG & Rise of Agentic RAG
Standard naive RAG (top-k vector similarity directly dumped into an LLM context window) fails in production environments due to three fatal flaws:
1. **Semantic Drift & Dilution**: Unrelated context fragments pollute the context window, causing hallucination.
2. **Aggregation & Structured Reasoning Blindness**: Vector databases cannot compute sums, averages, exact record counts, or multi-attribute logical conjunctions (e.g., "Count all Sukuk issued in 2023 with AA rating").
3. **Passive Context Feeding**: Naive RAG cannot self-correct when initial retrieval returns zero or irrelevant hits.

**QT's Solution — Agentic RAG Architecture**:
- **Pre-Chunk Cleaning**: Convert unstructured, messy documents (PDFs, scans, wikis) into standardized Markdown with clear heading breadcrumbs prior to chunking.
- **Hybrid Retrieval**: Combine dense semantic embeddings (capturing conceptual meaning) with sparse BM25 indexing (capturing exact product names, IDs, codes, and terminology).
- **Cross-Encoder Reranking**: Apply a lightweight cross-encoder (e.g., FlashRank ONNX TinyBERT) over the top-k union to score query-document interaction directly rather than relying on independent cosine distances.
- **Deterministic Sandbox Tools**: Give the LLM access to deterministic Python/Pandas sandbox tools or SQL executors for aggregation, filtering, and exact counts rather than asking the LLM to count bullet points.
- **Multi-Hop Reflection**: In multi-step questions, the agent uses first-hop findings to rewrite queries for second-hop deep-dive retrieval.

### 2. Harness Engineering & Context Compaction
In autonomous coding and multi-turn workflows, context window limits and drift degrade model reasoning over time. QT enforces **Harness Engineering**:
- **Persistent State Ledgers**: Using `progress.md` and `decision.md` to keep current milestone status and architectural trade-offs version-controlled in the repository.
- **Step Budgets & Circuit Breakers**: Preventing agent runaway loops by strictly capping tool execution turns (e.g., 8-turn budget with automated fallback).
- **Human-in-the-Loop (HITL) Approval Gates**: Sensitive actions (file mutations, shell execution, external API writes) pause for explicit user confirmation via streaming UI.

---

## Zetrix AI Production Systems Deep-Dive

### 1. INCEIF i-FIKR Islamic Knowledge Agent
- **Problem**: INCEIF's Islamic finance knowledge repository contains 870+ complex regulatory and research papers. Standard vector search hallucinated when users asked for exact numbers of rulings, structured comparisons between jurisdictions, or chronological issuance data.
- **Engineering Solution**:
  - Architected a hybrid agent that first queries a structured catalog via a custom `metadata-dispatcher` (Python/Pandas in a sandbox) to obtain exact counts and metadata subsets.
  - Combines structured metadata filters with vector retrieval over chunked research papers.
  - Result: 100% elimination of tally and date hallucinations on 870+ documents.

### 2. Enterprise Internal Wiki & SOP RAG System
- **Problem**: Raw enterprise SOP documents contained multi-column tables, scanned headers, and nested lists that broke chunk boundaries in naive chunkers.
- **Engineering Solution**:
  - Built an automated pre-cleaning pipeline that normalizes PDFs into hierarchical Markdown before ingestion.
  - Preserved document header paths (`/HR/LEAVE_POLICY/MATERNITY`) in chunk metadata for contextual grounding.
  - Result: Downstream retrieval recall improved by 28%, reducing employee search time from minutes to seconds.

### 3. Property Avatar Booking & Concierge Agent
- **Problem**: Property client needed a conversational concierge that could check calendar availability, book appointments, and handle escalations without dead-ends.
- **Engineering Solution**:
  - Implemented real-time calendar tool integrations with slot validation.
  - Built a seamless Human-in-the-Loop (HITL) turnover protocol that packages conversation context, visitor profile, and intent summary, handing off to human sales representatives when user sentiment or complexity demands it.

---

## NIQ (NielsenIQ) Experience

- **Role**: Data Input Validation Intern (Nov 2024 – Feb 2025).
- **Scope**: Validated large-scale retail and consumer market datasets averaging thousands of records per batch.
- **Impact**:
  - Applied rule-based and logic-driven validation scripts to intercept data anomalies before ingestion into regional analytics pipelines.
  - Collaborated across the Malaysia and Vietnam engineering and operations teams to establish unified data quality benchmarks.

---

## Core Technical Proficiencies & Toolkit

### Agent Frameworks & LLM Orchestration
- **LangGraph**: StateGraph workflows, cyclical ReAct agents, dynamic routing, checkpointing.
- **LangChain**: Tool abstractions, LCEL pipelines, document loaders.
- **Model Context Protocol (MCP)**: Tool and context server integration.
- **Dify Cloud & Self-Hosted**: Chatflows, multi-node agent DAGs, knowledge base configuration.

### Vector Search, Embeddings & Reranking
- **ChromaDB & Qdrant**: Persistent vector indexing, cosine similarity, metadata filtering.
- **FlashRank**: ONNX-based cross-encoder reranking (`ms-marco-TinyBERT-L-2-v2`).
- **Rank-BM25**: Sparse lexical matching (`BM25Okapi`).
- **Embeddings**: `text-embedding-3-large`, `all-MiniLM-L6-v2`.

### Backend & API Architecture
- **FastAPI**: Async REST APIs, dependency injection, Pydantic schemas, middleware.
- **Server-Sent Events (SSE)**: Real-time token-by-token streaming with metadata headers.
- **Database Technologies**: DuckDB (in-process analytics & BM25), PostgreSQL, MongoDB, SQLite.

### Machine Learning & Data Science
- **PyTorch**: Deep neural networks, custom multi-head self-attention mechanisms, RNNs/LSTMs.
- **BERT & Transformers**: Parameter-efficient fine-tuning (Prefix Prompt-Tuning).
