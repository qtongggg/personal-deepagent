# 📋 Personal DeepAgent: Next Phase Production Roadmap & To-Do List

*Last Updated: 2026-11-15 23:42*  
*Current Baseline: 2-Layer RAG Evaluation + Jev Decision Model Integration + Dynamic AGENT.md Harness*

---

## 🎯 High-Priority Roadmap Items

### 1. 🔄 Self-Healing Chunk Ingestion (Automated Boundary Repair)
- [ ] **Healer Module**: Create `src/skills/ingestion/healer.py` that listens to Jev chunk integrity verdicts.
- [ ] **Boundary Shift Algorithm**: When Jev flags a chunk ($P < 0.50$ due to mid-clause cutoffs or fragmented definitions), automatically shift boundaries to the nearest sentence punctuation (`.`, `!`, `?`) or merge with its adjacent sibling chunk.
- [ ] **Re-Audit Loop**: Re-evaluate repaired chunks via Jev until all chunks achieve $P \ge 0.50$ before committing to ChromaDB.
- [ ] **Unit Tests**: Add tests verifying that fragmented text passages are automatically healed.

### 2. ⚡ Live Step-by-Step Thought & Tool Telemetry
- [ ] **Streaming Callbacks**: Implement a custom LangChain `AsyncCallbackHandler` or generator in `src/agent.py` to stream intermediate thoughts and tool dispatch events.
- [ ] **Rich CLI Stepper**: In `scripts/run_agent.py`, display a real-time terminal visual stepper:
  - `[Planning]` Tasks recorded in to-do list
  - `[Hop 1]` Parallel catalog & intro retrieval
  - `[Hop 2]` Parallel surgical dive & FlashRank reranking
  - `[Scratchpad]` Drafting in `/workspace/comparison_notes.md`
  - `[Synthesis]` Final table & citation formatting
- [ ] **SSE API Endpoint**: Expose `/api/chat/stream` in `src/api.py` delivering Server-Sent Events (SSE) so web frontends receive instant (< 1s) telemetry.

### 3. 🤖 GitHub Actions CI/CD Quality Gate
- [ ] **Workflow File**: Create `.github/workflows/rag_eval.yml`.
- [ ] **Automated Test Run**: Trigger on every Pull Request or push to `dev`/`main`.
- [ ] **Jev Automated Evaluation**: Run `python scripts/run_rag_eval.py --evaluator jev`.
- [ ] **PR Scorecard Bot**: Automatically post `data/eval_report.md` as a Markdown comment on the Pull Request.
- [ ] **Quality Threshold Gate**: Fail the pipeline if Composite Score drops below **75%** or Faithfulness drops below **85%**.

### 4. 🧩 Contextual Retrieval (Anthropic-Style Breadcrumb Enrichment)
- [ ] **Context Prepend Hook**: In `src/skills/ingestion/chunker.py`, generate a lightweight 40-word document context header (paper title, authors, year, and primary subject) prepended to each chunk.
- [ ] **Hybrid Search Benchmark**: Re-index sample papers and evaluate retrieval recall improvements on ambiguous queries.

---

## 🛠️ Quick Verification Commands for Tomorrow

```bash
# 1. Run all unit tests
uv run pytest tests/

# 2. Run Layer 1 Ingestion Benchmark (LLM vs Jev)
uv run python scripts/benchmark_ingestion_eval.py

# 3. Run Layer 2 Output Evaluation Suite (Jev Decision Model)
uv run python scripts/run_rag_eval.py --evaluator jev

# 4. Run Side-by-Side Comparative Evaluation Benchmark
uv run python scripts/run_rag_eval.py --single eval_02_react_vs_reflexion --evaluator both
```
