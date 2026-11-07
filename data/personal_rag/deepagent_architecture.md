# PERSONAL DEEPAGENT — SYSTEM ARCHITECTURE & TECHNICAL SPECIFICATION

## Overview & Motivation
**Personal DeepAgent** is an autonomous AI agent system engineered by Mah Qing Tong (QT) to overcome the brittle nature of traditional single-prompt LLM wrappers and naive vector search. It features an autonomous multi-agent graph, a self-correcting RAG ingestion engine with Needle-in-a-Haystack evaluation, deterministic local tool execution, and an async streaming FastAPI backend with Human-in-the-Loop (HITL) safety controls.

---

## 1. Multi-Agent Orchestration Graph (LangGraph)

### Architecture
The core runtime uses a stateful **LangGraph** structure consisting of three coordinated agent nodes:
1. **Dynamic Orchestrator / Planner**:
   - Analyzes user goals, decomposes complex tasks into discrete steps, and selects specialized agent pathways.
   - Enforces a hard **Step-Budget Guardrail** (e.g., maximum 8 tool turns) to prevent infinite loops, tool thrashing, or context blowups.
2. **ReAct Research Agent**:
   - Executes iterative Thought-Action-Observation loops.
   - Connects to the Hybrid RAG engine, system bash, DuckDB catalog, and web search tools.
   - Analyzes intermediate tool results before synthesizing a final answer or pivoting strategy.
3. **Sub-Agent Workers**:
   - Specialized workers spawned for isolated sub-tasks (e.g., executing Python scripts, generating charts, batch document extraction) with sandboxed memory.

---

## 2. Two-Stage Hybrid RAG & Ingestion Engine

### Ingestion & Preprocessing
- **Section-Aware Markdown Parsing**: Converts raw PDFs into structured hierarchical Markdown, preserving document breadcrumbs (`#`, `##`, `###`).
- **Contextual Chunking**: Breaks text into semantic units while injecting document title and section path into the chunk header to preserve global context.
- **Automated Quarantine & Needle Evaluation**:
  - Automatically tests ingested chunks using synthetic Needle-in-a-Haystack retrieval queries.
  - If a section fails retrieval recall, the chunker automatically resizes boundaries and updates contextual breadcrumbs without manual intervention.

### Two-Stage Retrieval
1. **Stage 1 — Hybrid Retrieval (Dense + BM25)**:
   - **Dense Vectors**: ChromaDB cosine similarity search capturing conceptual meaning.
   - **Sparse Lexical**: Rank-BM25 (`BM25Okapi`) scoring exact terms, IDs, and domain nomenclature.
   - **Reciprocal Rank Fusion (RRF)**: Merges dense and sparse score lists into a unified candidate pool.
2. **Stage 2 — Cross-Encoder Reranking**:
   - Runs candidate chunks through **FlashRank** (`ms-marco-TinyBERT-L-2-v2` ONNX).
   - Cross-attends `[query, passage]` pairs directly, filtering out false-positive vector hits.

---

## 3. Deterministic Local Tool Execution & Safety

### Tool Ecosystem
- **System Bash Execution**: Sandboxed command-line execution with real-time output capture and timeout protections.
- **Catalog SQL Skill (DuckDB)**: Fast columnar query engine executing exact SQL queries over structured metadata catalogs, eliminating LLM tally hallucinations.
- **Memory Skill**: Context-aware persistent key-value memory retaining user preferences and conversation facts across sessions.
- **Multi-Engine Search**: Web search fallback for real-time external information retrieval.

### Self-Correction & Error Recovery
- When a tool returns a non-zero exit code or an unexpected output, the agent enters an automatic self-correction loop: inspects error traceback, modifies arguments, and retries with an alternative approach.

---

## 4. Async Streaming Backend & UI Stepper

### FastAPI & Server-Sent Events (SSE)
- Built on **FastAPI** with async generators streaming token chunks, agent thoughts (`thinking` events), and tool execution status (`tool_start`, `tool_end`).
- **Human-in-the-Loop (HITL) Pause Gates**: When sensitive operations are detected, the backend pauses the LangGraph execution thread and emits an `awaiting_approval` event, resuming only when the user sends an approval token.

### Interactive Viewer UI
- Modern dark-mode UI with dynamic step visualization (Planner $\rightarrow$ Tool Execution $\rightarrow$ Synthesis), live token streaming, and citation cards with expandable chunk context.
