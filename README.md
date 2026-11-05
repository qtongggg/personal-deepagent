# Personal DeepAgent: Autonomous Research Agent with Skills

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangChain deepagents](https://img.shields.io/badge/LangChain-deepagents-green.svg)](https://github.com/langchain-ai/deepagents)
[![LangGraph](https://img.shields.io/badge/State-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade, autonomous multi-hop research agent built using **LangChain's `deepagents`** harness and **`LangGraph`**. 

This agent moves beyond basic RAG by incorporating **active planning (`write_to_dos`)**, a **virtual workspace filesystem (`write_file`, `read_file`)** for scratchpad note drafting, deterministic SQL querying over structured metadata, and long-term user memory via Mem0.

---

## 🎬 Live Arena Demo & Video Walkthrough

Watch the head-to-head comparison where **Standard Naive RAG** fails (misses Reflexion entirely) while **Personal DeepAgent** performs parallel multi-hop retrieval, cross-encoder reranking, and synthesizes an 11-dimension comparative matrix:

> **[▶️ View Arena Showcase Video](data/videos/demo_arena_showcase.webm)** *(Automated Playwright 720p HD recording)*

To run the interactive side-by-side web arena locally:
```
# Start the web arena on http://localhost:8000
python scripts/run_server.py

# Or regenerate the video automatically via Playwright:
python scripts/generate_demo_video.py
```

## 🌟 Key Architecture & Features

```mermaid
flowchart TD
    User(["User Request + User ID"]) --> DeepAgent["LangChain DeepAgent Core Engine"]

    subgraph Harness ["Built-in deepagents Harness"]
        DeepAgent --> Planner["Task & To-Do Planner<br/>todo_write / todo_read"]
        DeepAgent --> VFS["Virtual Workspace Filesystem<br/>write_file / read_file<br/>- notes.md<br/>- comparison_draft.md"]
    end

    subgraph Skills ["Agent Skill Suite"]
        DeepAgent --> Skill1["Skill 1: Master Catalog Tool<br/>DuckDB / Pandas on catalog.csv"]
        DeepAgent --> Skill2["Skill 2: Vector Knowledge Retriever<br/>Chroma / Hybrid Dense + BM25"]
        DeepAgent --> Skill3["Skill 3: Long-Term Memory (Mem0)<br/>search_memory + add_memory"]
    end

    DeepAgent --> Sanitizer["Post-Synthesis Sanitizer"]
    subgraph Safeguards ["Invariant Safeguards"]
        Sanitizer --> PipeSanitizer["Pipe Sanitizer: converts pipe to dash in titles"]
        Sanitizer --> URLVerifier["Verbatim Catalog URL Restorer"]
        Sanitizer --> ReferenceContract["Structured References Contract"]
    end

    Sanitizer --> Output(["Final Scholarly Response with Table & Citations"])
```

1. **Active Task Planning**: The agent maintains a persistent `to_dos` checklist inside its LangGraph state, ensuring disciplined multi-hop execution without skipping steps.
2. **Virtual Filesystem (VFS) Context Management**: Large chunk text is automatically offloaded to virtual scratchpad files (`/workspace/notes.md`) to prevent token window dilution during multi-document comparisons.
3. **Deterministic Catalog Skill**: Uses DuckDB over CSV for zero-hallucination inventory counts and exact metadata verification.
4. **Autonomous Long-Term Memory**: Automatically persists user identity, academic constraints, and investigated research topics into Mem0 without needing explicit trigger words.
5. **Defensive Formatting Guardrails**: Built-in pipe sanitizers (`|` $\to$ `—`) ensure Markdown tables never break column alignment, while verbatim catalog URLs are preserved character-for-character.

---

## 📊 Benchmark: DeepAgent with Skills vs. Standard Naive RAG

How does **Personal DeepAgent with Skills** compare against traditional **Standard Naive RAG** (fixed chunking, top-k vector retrieval, and raw prompt concatenation)?

### 1. Architectural Comparison

```mermaid
flowchart TD
    subgraph NaiveRAG ["Approach A: Standard Naive RAG"]
        Q1["User Query"] --> Ret1["Naive Top-K Retrieval"]
        Ret1 --> BigPrompt["Token-Bloated Context<br/>(Dumps 5-10 raw chunks into prompt)"]
        BigPrompt --> LLM1["Single LLM Call"]
        LLM1 --> Out1["High Token Waste + Table Breakage Risk"]
    end

    subgraph DeepAgent ["Approach B: Personal DeepAgent with Skills"]
        Q2["User Query"] --> Planner["Task Planner (to_dos)"]
        Planner --> CatSkill["DuckDB Catalog Skill (Exact Paper Verification)"]
        Planner --> Ret2["Contextual Vector Retrieval (Breadcrumb Chunks)"]
        Ret2 --> VFS["Virtual Scratchpad (/workspace/notes.md)<br/>Keeps prompt context window lean"]
        VFS --> Synth["Multi-Hop Synthesis with Pipe Sanitizer"]
        Synth --> Out2["Grounded Answer + Clean Tables + Verbatim Citations"]
    end
```

### 2. Live Performance & Accuracy Metrics

Empirically measured against the 16-paper research corpus using DeepSeek (`deepseek-chat`):

| Test Scenario | Approach | Latency | Chunks Found | Multi-Hop Success | Grounding & Synthesis Quality |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Scenario 1: Direct Factual Query**<br>*(Toolformer: External tools & APIs)* | **Standard Naive RAG** | **3.64s** | 5 | N/A | Brief text listing without implementation details or usage ablation tables. |
| | **DeepAgent with Skills** | **10.61s** | 10 *(Top-4 Hybrid + FlashRank)* | N/A | **Comprehensive 4-column API table** (Atlas, BM25, NLLB), filtering thresholds, and verified catalog citation. |
| **Scenario 2: Multi-Hop Cross-Paper Comparison**<br>*(ReAct vs. Reflexion: Reasoning & feedback loops)* | **Standard Naive RAG** | 5.74s | 5 *(Single blind hop)* | FAILED | **Missed Reflexion entirely!** Naive RAG admitted: *"The context does not mention Reflexion at all... direct comparison is not possible."* |
| | **DeepAgent with Skills** | 32.70s *(Parallel Hops)* | 32 *(Top-4 Hybrid + FlashRank)* | SUCCESS | **Full 11-dimension comparative matrix**, HumanEval & ALFWorld benchmark tables, scratchpad notes in /workspace, and verbatim citations! |

> **Key Architectural Takeaway:** Naive RAG fails on multi-hop scientific questions because a single top-5 vector query cannot reliably bridge across multiple independent papers. DeepAgent acts like a senior research scientist: it verifies document inventory with SQL, queries each paper systematically across multiple hops, and synthesizes complete, cited comparison tables without hallucinations.

### 3. Reproduce It Yourself

Anyone can reproduce these benchmarks locally:

```bash
# Run the side-by-side benchmark suite
python scripts/benchmark_comparison.py

# Benchmark a custom research question
python scripts/benchmark_comparison.py --query "What is the physical detection range of acoustic leakage?"
```

Detailed JSON execution traces and Markdown summaries are automatically saved to `data/benchmark_results.json` and `data/benchmark_results.md`.

---

## 📂 Project Structure

```text
personal-deepagent/
├── data/
│   └── catalog.csv               # Grounding master catalog dataset
├── docs/
│   ├── blueprint.md              # Full architectural blueprint & operational protocols
│   └── plan.md                   # 7-Task TDD implementation plan
├── src/
│   ├── config.py                 # Pydantic configuration & environment settings
│   ├── prompt.py                 # System prompt with the 4 operational protocols
│   ├── agent.py                  # Core DeepAgent assembly with to-dos & VFS
│   ├── skills/
│   │   ├── catalog_skill.py      # Skill 1: DuckDB deterministic catalog querying
│   │   ├── retriever_skill.py    # Skill 2: Vector chunk RAG with section metadata
│   │   └── memory_skill.py       # Skill 3: Mem0 user memory search & persistence
│   └── utils/
│       ├── sanitizer.py          # Pipe sanitization & verbatim URL verification
│       └── schemas.py            # Pydantic response models
├── scripts/
│   ├── ingest.py                 # Script to chunk and index documents into Chroma
│   └── run_agent.py              # Interactive CLI turn runner
├── tests/
│   ├── test_config.py            # L1 syntax tests
│   ├── test_catalog_skill.py     # L2 skill unit tests
│   ├── test_memory_skill.py      
│   ├── test_sanitizer.py         
│   └── test_agent_e2e.py         # L3 golden trace evaluation
├── .env.example
├── pyproject.toml
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone & Setup Environment

```bash
git clone https://github.com/your-username/personal-deepagent.git
cd personal-deepagent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment Keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=sk-...
MEM0_API_KEY=m0-...
DEFAULT_MODEL=gpt-4o
```

### 3. Run the Test Suite

```bash
pytest -v
```

---

## 📖 Operational Protocols

The agent follows 4 strict operational protocols:
- **Concept & Definition**: Fast single-hop vector retrieval + catalog metadata verification + autonomous memory commit.
- **2-Hop Paper Comparison**: Hop 1 structural overview (`/INTRODUCTION`) $\to$ Hop 2 surgical body dive $\to$ Virtual scratchpad drafting $\to$ Phase 3.5 `add_memory` $\to$ Cross-Paper Synthesis Matrix table.
- **Pure Counts & Listings**: Catalog tool only (bypasses vector DB and Mem0), returning direct numbers and verified catalog URLs.
- **Autonomous Identity Memory**: Proactively persists user identity (name, role, university, research interests) to Mem0 on first introduction.

---

## 📝 License
MIT License. Free to use and adapt for academic and personal research projects.
