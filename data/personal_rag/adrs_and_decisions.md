# MAH QING TONG (QT) — ARCHITECTURAL DECISION RECORDS (ADR) & HARNESS ENGINEERING

## Harness Engineering Core Principles

### Why Harness Engineering Matters
As AI models become more capable, the primary bottleneck in autonomous software engineering is no longer raw intelligence, but the **engineering harness**:
- The environment boundaries, verification loops, error handling, state persistence, and context discipline surrounding the model.
- An agent without a disciplined harness quickly drifts, hallucinates completion, and makes circular edits.

### The 4 Pillars of QT's Engineering Harness
1. **Persistent State Memory**: Version-controlled `progress.md` (milestone tracker) and `decision.md` (ADR log).
2. **Automated Verification Gates**: Never accept an agent assertion without running deterministic verification commands (`pytest`, syntax check, API probe).
3. **Context Compaction & Budget Guardrails**: Hard step budgets prevent infinite loops and runaway compute costs.
4. **Sandboxed Deterministic Execution**: Using structured databases and code execution rather than trusting the LLM's internal arithmetic.

---

## Architectural Decision Records (ADR-001 to ADR-010)

### ADR-001: Kinetic Full-Bleed Layout vs. Boxy Bento Cards
- **Decision**: Adopted a borderless editorial layout with 1px architectural hairlines (`Pitch Black #050505`, `Crisp White #F7F7F5`, `Signal Orange #FF4D00`).
- **Rationale**: Eliminates generic glassmorphism and allows typography and scroll-driven motion to convey craft and visual hierarchy.

### ADR-002: Proportional Typography (Space Grotesk + JetBrains Mono)
- **Decision**: Standardized headers and metric counters on `Space Grotesk` (`tabular-nums`) paired with `JetBrains Mono` for code, tags, and terminal telemetry.
- **Rationale**: High-contrast, crisp technical readability across mobile and desktop displays.

### ADR-003: FastAPI SSE Streaming Proxy
- **Decision**: Implemented an async FastAPI proxy server with Server-Sent Events (SSE) streaming.
- **Rationale**: Keeps API keys strictly hidden on the server and provides token-by-token streaming with multi-turn conversation persistence.

### ADR-004: 3-Tier Resilient Fallback Architecture
- **Decision**: Built a multi-tier fallback: Tier 1 (Cloud RAG) $\rightarrow$ Tier 2 (Local Python Vector/Markdown RAG) $\rightarrow$ Tier 3 (In-browser JS fallback).
- **Rationale**: Guarantees 100% uptime for portfolio visitors and recruiters regardless of external network or API key status.

### ADR-005: In-Repo Harness Memory (`progress.md` & `decision.md`)
- **Decision**: Maintained live execution progress and ADR logs directly in the repository root and exposed them via CLI slash commands (`/progress`, `/decisions`).
- **Rationale**: Makes Harness Engineering visible to users and recruiters inspecting the live system.

### ADR-006: Staged Git Branching Workflow (`develop` $\rightarrow$ `main`)
- **Decision**: Enforced an active development branch (`develop`) promoting to `main` only after passing strict verification checklists.

### ADR-007: Reasoning Stream Sanitization (<think> Filters)
- **Decision**: Real-time filtering of unclosed `<think>...</think>` tags emitted by reasoning models (e.g. DeepSeek-R1).
- **Rationale**: Prevents internal chain-of-thought tokens from cluttering visitor-facing UI.

### ADR-008: 4-Stage Architecture Pipeline Graphs
- **Decision**: Replaced generic mastery percentage bars with 4-stage architecture pipeline flow diagrams (`STAGE 01 → STAGE 04`).
- **Rationale**: Illustrates engineering workflows (ingestion, indexing, retrieval, synthesis) rather than arbitrary skill scores.

### ADR-009: 3D ASCII Möbius Strip (∞) ⇄ Neural Thinking Wave Canvas
- **Decision**: Rendered an interactive 3D ASCII Möbius strip on HTML5 `<canvas>` that transforms into an undulating thinking wave during agent queries.
- **Rationale**: Living visual metaphor connecting the user input composer to the agent's internal cognitive state.

### ADR-010: Minimalist Home View ⇄ Deep-Dive Details View
- **Decision**: Separated the user interface into a minimalist Claude/ChatGPT-style input view (`#view-home`) and an architectural deep-dive view (`#view-details`).
- **Rationale**: Delivers an uncluttered first impression while allowing technical recruiters to explore in-depth projects.
