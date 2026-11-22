# Paradigm 2 Skill-Driven Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Personal DeepAgent from an eager tool-bound agent (Paradigm 1) into a modular, on-demand Skill-Driven Agent Harness (Paradigm 2) where the agent dynamically discovers skills from `SKILL.md` manifests, reads operational SOPs just-in-time, and executes decoupled tools and CLI scripts.

**Architecture:** 
Implement an automated `SkillRegistry` that indexes all `src/skills/*/SKILL.md` packages at runtime. Replace monolithic prompt instructions and bloated tool bindings with lightweight meta-tools (`list_available_skills`, `read_skill_spec`, `execute_skill_tool`), while maintaining an eager fallback mode to guarantee 100% backward compatibility across all 59 existing unit tests and FastAPI endpoints.

**Tech Stack:** Python 3.13, LangChain, LangGraph (`deepagents`), DuckDB, ChromaDB, PyYAML, PyTest.

**Spec:** [`AGENT.md`](file:///c:/Users/User/Documents/antigravity/personal-deepagent/AGENT.md) and [`src/skills/*/SKILL.md`](file:///c:/Users/User/Documents/antigravity/personal-deepagent/src/skills/)

---

## Global Constraints

- **Python Version:** Python 3.13 (`.venv\Scripts\python.exe`).
- **Regression Guarantee:** All 59 existing unit tests in `tests/` MUST continue to pass (`pytest` exit code 0).
- **FastAPI Stability:** Endpoints (`/api/chat`, `/api/semantic-search`, `/api/arena/compare`, `/api/ingest`) in `src/api.py` must maintain their response contracts.
- **ATS Resume Integrity:** Never alter the verified 1-page A4 format of `docs/Mah_Qing_Tong_Resume.pdf`.
- **Zero Monolithic Prompt Bloat:** The Paradigm 2 system prompt must be compact (<60 lines), delegating all domain logic and invariants to `SKILL.md` files.

---

## Review Focus (Edge Cases & Failure Modes)

1. **Unknown Skill Query:** When an agent queries an invalid or non-existent skill name, `read_skill_spec` and `execute_skill_tool` must return helpful error messages listing valid skills without raising an unhandled exception.
2. **Missing `SKILL.md` File:** If a skill folder lacks `SKILL.md` or has invalid YAML frontmatter, the registry must log a warning and skip gracefully without crashing the agent startup.
3. **Execution Parameter Type Coercion:** Tool arguments passed as JSON strings or dicts from the LLM must be safely validated and unpacked to avoid signature mismatches.
4. **Concurrent Tool Invocations:** Parallel tool calls (e.g. comparing two papers) must execute safely without mutating shared registry state.
5. **Backward Compatibility Mode:** Existing code calling `run_agent_turn()` without explicit parameters must continue to work seamlessly.

---

## File Structure

- **Create:**
  - `src/skills/registry.py`: Dynamic skill discovery, YAML frontmatter parsing, tool registration, and execution dispatcher.
  - `tests/test_skill_registry.py`: Unit tests for skill discovery, manifest generation, and dynamic tool dispatching.
  - `tests/test_paradigm2_agent.py`: End-to-end ReAct test verifying dynamic discovery, `SKILL.md` inspection, and execution.
- **Modify:**
  - `src/agent.py`: Integrate `SkillRegistry`, add `list_available_skills` and `execute_skill_tool` tools, support both eager and dynamic discovery modes.
  - `src/prompt.py`: Update `SYSTEM_PROMPT` to a lean Paradigm 2 SOP conductor prompt that instructs the agent to discover and follow `SKILL.md` specifications.
  - `src/skills/*/SKILL.md`: Verify YAML frontmatter completeness (`name`, `description`, `triggers`, `tools`, `cli_commands`) across catalog, retriever, memory, and ingestion skills.
  - `README.md`: Document the Paradigm 2 Skill-Driven Harness architecture.

---

## Tasks

### Task 1: Skill Registry & Manifest Engine (`src/skills/registry.py`)

**Files:**
- Create: `src/skills/registry.py`
- Test: `tests/test_skill_registry.py`

- [ ] **Step 1.1: Write failing unit tests for Skill Registry**
  - Create `tests/test_skill_registry.py` testing:
    - Scanning `src/skills/` finds all 4 skills (`catalog_skill`, `retriever_skill`, `memory_skill`, `ingestion_skill`).
    - Parsing YAML frontmatter extracts `name`, `description`, `triggers`, `tools`.
    - `get_skill_manifest()` returns compact metadata (<100 tokens total).
    - `get_skill_spec(skill_name)` returns the markdown body.
    - `get_skill_tool(tool_name)` retrieves the executable callable.
- [ ] **Step 1.2: Run test to confirm failure**
  - Run: `.venv\Scripts\pytest tests/test_skill_registry.py`
- [ ] **Step 1.3: Implement `SkillRegistry`**
  - Implement `SkillRegistry` in `src/skills/registry.py`:
    - Auto-discover subdirectories in `src/skills/` containing `SKILL.md`.
    - Extract YAML frontmatter with `yaml.safe_load`.
    - Register tool callables from underlying skill modules.
    - Provide `list_skills()`, `get_manifest()`, `get_spec()`, and `execute_tool()`.
- [ ] **Step 1.4: Run tests to confirm passing**
  - Run: `.venv\Scripts\pytest tests/test_skill_registry.py`
- [ ] **Step 1.5: Commit Task 1**
  - Run: `git add src/skills/registry.py tests/test_skill_registry.py && git commit -m "feat(skills): implement SkillRegistry with dynamic SKILL.md discovery"`

---

### Task 2: Standardize YAML Frontmatters across `SKILL.md` Files

**Files:**
- Modify: `src/skills/catalog/SKILL.md`
- Modify: `src/skills/retriever/SKILL.md`
- Modify: `src/skills/memory/SKILL.md`
- Modify: `src/skills/ingestion/SKILL.md`

- [ ] **Step 2.1: Audit and enhance frontmatters**
  - Ensure every `SKILL.md` has standard fields:
    - `name`: exact skill identifier
    - `description`: crisp 1-2 sentence overview for the agent's manifest
    - `triggers`: representative user query patterns
    - `tools`: list of tool names provided by this skill
    - `cli_commands`: list of equivalent terminal CLI scripts in `scripts/`
- [ ] **Step 2.2: Verify with SkillRegistry unit tests**
  - Run: `.venv\Scripts\pytest tests/test_skill_registry.py -v`
- [ ] **Step 2.3: Commit Task 2**
  - Run: `git commit -am "docs(skills): standardize YAML frontmatter schemas across all SKILL.md specs"`

---

### Task 3: Meta-Tools & Dynamic Dispatcher in `src/agent.py`

**Files:**
- Modify: `src/agent.py`
- Test: `tests/test_paradigm2_agent.py`

- [ ] **Step 3.1: Write failing test for Paradigm 2 dynamic agent**
  - Create `tests/test_paradigm2_agent.py` testing:
    - Agent can call `list_available_skills()` and see the 4 skills.
    - Agent can call `read_skill_spec("catalog_skill")`.
    - Agent can dynamically invoke `execute_skill_tool("catalog_skill", "catalog_query", {"query": "SELECT COUNT(*) FROM catalog"})`.
- [ ] **Step 3.2: Run test to confirm failure**
  - Run: `.venv\Scripts\pytest tests/test_paradigm2_agent.py`
- [ ] **Step 3.3: Implement Meta-Tools in `src/agent.py`**
  - Add `@tool("list_available_skills")` returning the registry manifest.
  - Update `read_skill_spec` to use `SkillRegistry.get_spec()`.
  - Add `@tool("execute_skill_tool")` to dispatch tool calls to the registry.
  - Update `create_deep_research_agent(mode="hybrid")` supporting:
    - `mode="dynamic"` (Paradigm 2: meta-tools + planning)
    - `mode="hybrid"` / `mode="eager"` (Paradigm 1.5: meta-tools + pre-bound tools for backwards compatibility)
- [ ] **Step 3.4: Verify tests pass**
  - Run: `.venv\Scripts\pytest tests/test_paradigm2_agent.py tests/test_agent_assembly.py`
- [ ] **Step 3.5: Commit Task 3**
  - Run: `git add src/agent.py tests/test_paradigm2_agent.py && git commit -m "feat(agent): implement dynamic skill meta-tools and dispatching"`

---

### Task 4: Lean Paradigm 2 System Prompt & SOP Protocol

**Files:**
- Modify: `src/prompt.py`
- Modify: `AGENT.md`

- [ ] **Step 4.1: Draft Lean System Prompt**
  - Refactor `SYSTEM_PROMPT` to remove hardcoded monolithic SQL and retrieval rules.
  - Embed the **SOP Execution Protocol**:
    1. Reason on intent and check `list_available_skills()`.
    2. Read the specific `SKILL.md` via `read_skill_spec()`.
    3. Follow the invariants and execute the tool via `execute_skill_tool()` (or direct tool call).
    4. Synthesize with verbatim catalog citations and clean markdown tables.
- [ ] **Step 4.2: Update AGENT.md**
  - Synchronize `AGENT.md` at root so dynamic file-reading reflects the Paradigm 2 harness.
- [ ] **Step 4.3: Verify regression tests**
  - Run: `.venv\Scripts\pytest -v`
- [ ] **Step 4.4: Commit Task 4**
  - Run: `git commit -am "feat(prompt): transition system prompt to lean Paradigm 2 SOP conductor"`

---

### Task 5: Full Regression Testing & Production Verification

**Files:**
- Test: All 59+ tests across `tests/`
- Script: `scripts/run_industry_benchmark.py`

- [ ] **Step 5.1: Run complete pytest suite**
  - Run: `.venv\Scripts\pytest -v`
  - Assert 100% pass rate.
- [ ] **Step 5.2: Run HotpotQA Multi-Hop Benchmark**
  - Run: `.venv\Scripts\python.exe scripts/run_industry_benchmark.py --samples 5 --agentic --evaluator jev`
  - Verify 100% Exact Match and 100% Recall maintained.
- [ ] **Step 5.3: Verify 1-page resume generation invariant**
  - Run: `.venv\Scripts\python.exe scripts/generate_1page_resume.py`
  - Verify `Actual PDF Page Count = 1`.
- [ ] **Step 5.4: Update documentation**
  - Update `README.md` and `Agent_Skills_and_Scripts_Architecture_Guide.md` with Paradigm 2 architecture diagram.
- [ ] **Step 5.5: Final commit & push**
  - Run: `git add -A && git commit -m "chore(release): complete transition to Paradigm 2 Skill-Driven Agent Harness" && git push origin dev`
