# LangChain DeepAgent (Agent with Skills) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone, autonomous Research Agent with Skills using LangChain's `deepagents` package and `LangGraph` that replicates the exact capabilities of the Dify `Agent_memory` / `testing_qt` agent (deterministic catalog querying, vector RAG, Mem0 long-term memory, virtual workspace notes, table pipe sanitization, verbatim URL restoration, and structured references), without any outer workflow.

**Architecture:** A single autonomous DeepAgent instance (`deepagents.create_deep_agent`) equipped with 3 pluggable skills (DuckDB catalog query, Chroma vector retrieval, Mem0 memory) plus built-in planning (`todo`) and virtual workspace filesystem (`write_file`, `read_file`), guided by an authoritative system prompt enforcing 4 operational protocols, and finalized by an invariant post-sanitizer.

**Tech Stack:** Python 3.11+, `deepagents`, `langgraph`, `langchain-core`, `duckdb`, `chromadb`, `mem0ai`, `pydantic`, `pytest`.

**Spec:** `outputs/deepagent_project_blueprint.md`

## Global Constraints

- **Scope Limit**: Build ONLY the autonomous Agent with Skills. Do NOT build an outer workflow orchestrator or multi-node routing graph.
- **Table Pipe Sanitization**: Every Markdown table cell with titles containing `|` must be replaced with `' — '` before formatting to prevent column misalignment (preserving ACI-231 fix).
- **Verbatim URLs**: URLs linking to catalog documents (`https://ifikr.my/resources/...`) must match the catalog CSV character-for-character; no LLM slug fabrication or normalization of Arabic/percent-encoded characters allowed.
- **Unified User ID**: The user ID passed into the agent turn must be strictly forwarded to Mem0 `search_memory` and `add_memory` (defaulting to `"default_user"`).
- **Autonomous Name Persistence**: When a user states their name or role, `add_memory` must trigger immediately in that turn without asking confirmation.
- **Latency Guardrails**: Pure counts, listings, and lexicon definitions must bypass Mem0 and vector search.

## Review Focus

1. **Title with multiple pipes:** A catalog document titled `"IFHUB | October 2022 | Special Report"` must not create 2 extra columns in Markdown tables.
2. **Percent-encoded & Arabic URLs:** A catalog item with URL `https://ifikr.my/resources/shari%ca%bfah-perspective-و/` must not be simplified to ASCII or stripped of `-و/`.
3. **Autonomous User Name Memory:** When user says `"my name is Mah Qing Tong"`, `add_memory` must execute silently without asking confirmation.
4. **Paper Comparison Multi-Hop Execution:** Comparing two research papers (e.g. `IRP 5` and `IRP 11`) must query both catalog metadata and vector chunk content, write drafts to virtual workspace, and commit the research comparison to Mem0.
5. **Zero-Result Handling:** When a catalog filter yields 0 rows, the agent must report 0 explicitly rather than hallucinating plausible publications.

---

### Task 1: Project Scaffolding & Configuration

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `src/config.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Produces: `Settings` object in `src/config.py` exporting `OPENAI_API_KEY`, `MEM0_API_KEY`, `CATALOG_CSV_PATH`, `CHROMA_PERSIST_DIR`, `DEFAULT_MODEL`, `SIMILARITY_THRESHOLD`.

- [ ] **Step 1: Write failing test in `tests/test_config.py`**
```python
def test_settings_load_defaults():
    from src.config import get_settings
    settings = get_settings()
    assert settings.CATALOG_CSV_PATH == "data/catalog.csv"
    assert settings.SIMILARITY_THRESHOLD == 0.4
```
- [ ] **Step 2: Run test to verify it fails**
`pytest tests/test_config.py` -> FAIL
- [ ] **Step 3: Implement `pyproject.toml`, `.env.example`, and `src/config.py`**
Use `pydantic-settings` to parse environment variables with fallback defaults.
- [ ] **Step 4: Run test to verify it passes**
`pytest tests/test_config.py` -> PASS
- [ ] **Step 5: Commit**
`git add pyproject.toml .env.example src/config.py tests/test_config.py && git commit -m "feat: project scaffolding and configuration"`

---

### Task 2: Skill 1 — Deterministic Catalog Tool (DuckDB over CSV)

**Files:**
- Create: `src/skills/catalog_skill.py`
- Create: `data/catalog.csv` (Sample catalog dataset with title, author, year, document_name, source_url)
- Test: `tests/test_catalog_skill.py`

**Interfaces:**
- Consumes: `Settings.CATALOG_CSV_PATH` from `src.config`
- Produces:
  - `query_catalog_sql(sql_query: str) -> List[dict]`
  - `get_catalog_stats(filter_dict: dict) -> dict`
  - `catalog_tool: BaseTool` (LangChain `@tool` callable)

- [ ] **Step 1: Write failing tests in `tests/test_catalog_skill.py`**
```python
def test_catalog_exact_count():
    from src.skills.catalog_skill import query_catalog_sql
    results = query_catalog_sql("SELECT COUNT(*) as count FROM catalog WHERE year = 2020")
    assert isinstance(results, list)
    assert "count" in results[0]

def test_catalog_verbatim_url_preservation():
    from src.skills.catalog_skill import query_catalog_sql
    results = query_catalog_sql("SELECT source_url FROM catalog WHERE document_name = 'IRP 5'")
    assert results[0]["source_url"].startswith("https://ifikr.my/resources/")
```
- [ ] **Step 2: Run test to verify it fails**
`pytest tests/test_catalog_skill.py` -> FAIL
- [ ] **Step 3: Implement `src/skills/catalog_skill.py`**
Initialize DuckDB session querying `catalog.csv`. Add helper for flexible keyword search matching both `title` and `name`. Wrap as LangChain `@tool(name="catalog_query")`.
- [ ] **Step 4: Run test to verify it passes**
`pytest tests/test_catalog_skill.py` -> PASS
- [ ] **Step 5: Commit**
`git add src/skills/catalog_skill.py data/catalog.csv tests/test_catalog_skill.py && git commit -m "feat: deterministic duckdb catalog skill"`

---

### Task 3: Skill 2 — Vector Knowledge Retriever Tool (Chroma / Hybrid)

**Files:**
- Create: `src/skills/retriever_skill.py`
- Create: `scripts/ingest.py`
- Test: `tests/test_retriever_skill.py`

**Interfaces:**
- Consumes: `Settings.CHROMA_PERSIST_DIR`
- Produces:
  - `retrieve_knowledge_chunks(query: str, top_k: int = 5, document_filter: Optional[str] = None) -> List[dict]`
  - `retriever_tool: BaseTool` (LangChain `@tool`)

- [ ] **Step 1: Write failing test in `tests/test_retriever_skill.py`**
```python
def test_retriever_returns_chunk_metadata():
    from src.skills.retriever_skill import retrieve_knowledge_chunks
    chunks = retrieve_knowledge_chunks("Takaful principles", top_k=2)
    assert len(chunks) <= 2
    for chunk in chunks:
        assert "document_name" in chunk
        assert "header_path" in chunk
        assert "chunk_content" in chunk
```
- [ ] **Step 2: Run test to verify it fails**
`pytest tests/test_retriever_skill.py` -> FAIL
- [ ] **Step 3: Implement `src/skills/retriever_skill.py` & mock/local ChromaDB**
Configure Chroma vector store with chunk metadata (`document_name`, `header_path`, `chunk_id`). Wrap in LangChain `@tool(name="knowledge_retriever")`.
- [ ] **Step 4: Run test to verify it passes**
`pytest tests/test_retriever_skill.py` -> PASS
- [ ] **Step 5: Commit**
`git add src/skills/retriever_skill.py scripts/ingest.py tests/test_retriever_skill.py && git commit -m "feat: vector knowledge retriever skill with chunk metadata"`

---

### Task 4: Skill 3 — Long-Term Memory Tool (Mem0 Integration)

**Files:**
- Create: `src/skills/memory_skill.py`
- Test: `tests/test_memory_skill.py`

**Interfaces:**
- Consumes: `Settings.MEM0_API_KEY`, `Settings.SIMILARITY_THRESHOLD`
- Produces:
  - `search_memory(user_id: str, query: str) -> List[dict]`
  - `add_memory(user_id: str, messages: list) -> dict`
  - `search_memory_tool: BaseTool`
  - `add_memory_tool: BaseTool`

- [ ] **Step 1: Write failing test in `tests/test_memory_skill.py`**
```python
def test_memory_filter_below_threshold():
    from src.skills.memory_skill import filter_memories_by_score
    raw = [{"memory": "Prefers Islamic Finance", "score": 0.5}, {"memory": "Irrelevant", "score": 0.2}]
    filtered = filter_memories_by_score(raw, threshold=0.4)
    assert len(filtered) == 1
    assert filtered[0]["memory"] == "Prefers Islamic Finance"
```
- [ ] **Step 2: Run test to verify it fails**
`pytest tests/test_memory_skill.py` -> FAIL
- [ ] **Step 3: Implement `src/skills/memory_skill.py`**
Integrate `mem0ai.MemoryClient`. Add score filtering ($\ge 0.4$) and strict user ID validation. Wrap as LangChain tools with `user_id` context injection.
- [ ] **Step 4: Run test to verify it passes**
`pytest tests/test_memory_skill.py` -> PASS
- [ ] **Step 5: Commit**
`git add src/skills/memory_skill.py tests/test_memory_skill.py && git commit -m "feat: mem0 long-term memory skill with threshold guard"`

---

### Task 5: Post-Synthesis Sanitizer & Output Schemas

**Files:**
- Create: `src/utils/schemas.py`
- Create: `src/utils/sanitizer.py`
- Test: `tests/test_sanitizer.py`

**Interfaces:**
- Produces:
  - `AgentResponse` (Pydantic model: `result: str`, `references: List[ReferenceItem]`, `json_output: dict`)
  - `sanitize_table_pipes(markdown_text: str) -> str`
  - `restore_verbatim_catalog_urls(markdown_text: str, catalog_lookup: dict) -> str`
  - `build_final_response(text: str, observed_chunks: List[dict], catalog_df) -> AgentResponse`

- [ ] **Step 1: Write failing tests in `tests/test_sanitizer.py`**
```python
def test_pipe_sanitization_in_table_titles():
    from src.utils.sanitizer import sanitize_table_pipes
    raw_table = "| Title | Author |\n| IFHUB | Special | Dr. Z |"
    clean = sanitize_table_pipes(raw_table)
    lines = clean.strip().split("\n")
    assert len(lines[1].split("|")) == 4  # empty, Title, Author, empty

def test_url_restoration_arabic_percent_encoding():
    from src.utils.sanitizer import restore_verbatim_catalog_urls
    lookup = {"shariah-perspective": "https://ifikr.my/resources/shari%ca%bfah-perspective-و/"}
    raw = "[Link](https://ifikr.my/resources/shariah-perspective)"
    restored = restore_verbatim_catalog_urls(raw, lookup)
    assert "https://ifikr.my/resources/shari%ca%bfah-perspective-و/" in restored
```
- [ ] **Step 2: Run test to verify it fails**
`pytest tests/test_sanitizer.py` -> FAIL
- [ ] **Step 3: Implement `src/utils/sanitizer.py` and `src/utils/schemas.py`**
Implement pipe sanitization (`\|` $\to$ `—`) and column count balancing. Implement catalog URL lookup restoration. Deduplicate references capped at 25.
- [ ] **Step 4: Run test to verify it passes**
`pytest tests/test_sanitizer.py` -> PASS
- [ ] **Step 5: Commit**
`git add src/utils/schemas.py src/utils/sanitizer.py tests/test_sanitizer.py && git commit -m "feat: post-synthesis sanitizer with pipe and url safeguards"`

---

### Task 6: Autonomous DeepAgent Assembly & Operational Protocols

**Files:**
- Create: `src/prompt.py`
- Create: `src/agent.py`
- Create: `scripts/run_agent.py`
- Test: `tests/test_agent_assembly.py`

**Interfaces:**
- Consumes: Skills from Tasks 2, 3, 4 and Sanitizer from Task 5.
- Produces:
  - `create_deep_research_agent() -> AgentExecutor`
  - `run_agent_turn(query: str, user_id: str = "default_user") -> AgentResponse`

- [ ] **Step 1: Write system prompt in `src/prompt.py`**
Port the exact 4 Operational Protocols from `outputs/agent_memory_prompt.md`:
  - Concept & definition queries (retrieve passages -> verify catalog metadata -> commit memory -> answer).
  - 2-hop comparison protocol (Hop 1 intro chunk -> Hop 2 body dive -> sufficiency gate -> Phase 3.5 memory persistence -> single comparison table matrix).
  - Pure counts/listings (catalog tool only, print verbatim source_url).
  - Autonomous name & identity persistence (immediate `add_memory` without asking confirmation).
- [ ] **Step 2: Implement `src/agent.py` using `deepagents.create_deep_agent`**
Assemble the agent with:
  - Skills: `catalog_tool`, `retriever_tool`, `search_memory_tool`, `add_memory_tool`.
  - Virtual workspace filesystem tools (`write_file`, `read_file`) for intermediate note drafting.
  - To-do list planner tools (`todo_write`, `todo_read`).
- [ ] **Step 3: Write test in `tests/test_agent_assembly.py`**
Verify the agent compiles and exposes the expected tool suite.
- [ ] **Step 4: Run test to verify it passes**
`pytest tests/test_agent_assembly.py` -> PASS
- [ ] **Step 5: Commit**
`git add src/prompt.py src/agent.py scripts/run_agent.py tests/test_agent_assembly.py && git commit -m "feat: autonomous deepagents research agent assembly"`

---

### Task 7: Regression Test Suite & Golden Trace Replay

**Files:**
- Create: `tests/test_agent_e2e.py`
- Create: `scripts/run_all_tests.py`
- Test: Run `python scripts/run_all_tests.py`

**Interfaces:**
- Produces: 3-tier test runner:
  - L1: Static configuration and schema integrity.
  - L2: Skill unit tests (catalog SQL, memory score filter, pipe sanitizer, URL restorer).
  - L3: End-to-end replay of golden queries:
    - Count query: "How many papers on Waqf in 2020?" -> Catalog only, exact count.
    - Identity query: "My name is Mah Qing Tong" -> `add_memory` triggers silently.
    - Comparison query: "Compare IRP 5 and IRP 11" -> Hop 1 + Hop 2 + single table matrix + references.

- [ ] **Step 1: Write golden trace tests in `tests/test_agent_e2e.py`**
- [ ] **Step 2: Implement `scripts/run_all_tests.py` runner**
- [ ] **Step 3: Run regression harness**
`python scripts/run_all_tests.py`
Expected: 100% PASS across all tiers.
- [ ] **Step 4: Commit**
`git add scripts/run_all_tests.py tests/test_agent_e2e.py && git commit -m "feat: regression test suite and golden trace replay"`

---

## Execution Handoff

Plan complete and saved to `outputs/deepagent_implementation_plan.md`.

In your new personal project repository, pass this plan and the blueprint to the Antigravity agent. The agent will execute Task 1 through Task 7 using **superpowers:subagent-driven-development** or **superpowers:executing-plans**.
