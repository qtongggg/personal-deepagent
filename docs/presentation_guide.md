# Personal DeepAgent: High-Impact Technical Presentation Guide

This guide provides a complete **slide-by-slide presentation structure**, **visual assets checklist**, and **exact word-for-word speaker notes** designed for technical interviews, engineering tech talks, or client project showcases.

---

## ⏱️ Recommended Formats
- **Full Technical Showcase:** 10–12 minutes (all 10 slides + live demo).
- **Executive / Interview Pitch:** 5–7 minutes (focus on Slides 1, 2, 3, 4, 8, 9).

---

## 📑 Slide Deck Blueprint & Speaker Script

```text
[1. Hook & Title] ──> [2. The RAG Problem] ──> [3. Head-to-Head Arena] ──> [4. Paradigm 2 Harness] ──> [5. Modular Skills Suite]
        │
        ▼
[6. Tiny Engineering Designs] ──> [7. Deterministic SQL] ──> [8. HotpotQA Benchmark] ──> [9. Jev Decision Model] ──> [10. Conclusion & Q&A]
```

---

### Slide 1: Title & The Core Proposition
- **Title:** **Personal DeepAgent: Autonomous Multi-Hop Research with Skills**
- **Subtitle:** Beyond Naive RAG — Dynamic Skill Discovery, Active Planning, and Deterministic Grounding
- **Presenter:** Mah Qing Tong (QT) — LLM Engineer
- **Visuals on Screen:** Badges (LangChain `deepagents`, LangGraph, Python 3.11+, 66 Tests Passed) + Architecture Hero Diagram.
- **🗣️ Speaker Script (30 seconds):**
  > "Good morning/afternoon. Today I want to show you Personal DeepAgent. 
  > Most enterprise RAG implementations in 2024–2026 are still stuck in what I call the 'Naive RAG trap'—they chunk documents blindly, pull top-5 vector similarities, and dump raw text into a prompt. On multi-document scientific research, that breaks down immediately. 
  > Personal DeepAgent re-architects RAG into an autonomous research harness: it dynamically discovers modular skills, plans multi-hop investigations, offloads working memory to a virtual scratchpad, and combines deterministic DuckDB SQL with hybrid search."

---

### Slide 2: The Core Problem — Why Standard RAG Fails in Production
- **Visuals on Screen:** Split screen: "What people think RAG is" vs. "What actually happens on complex queries".
  1. **Single-Pass Blind Hop**: Misses connected facts across multiple papers.
  2. **The Embedding Tax & Noise**: 8B embedding models fail on exact acronyms and inflate context with distractor chunks.
  3. **The Metadata Hallucination**: Vector DBs guessing inventory counts (±50% error).
  4. **Markdown Table Breakage**: Unescaped pipes (`|`) corrupting comparison tables in UI.
- **🗣️ Speaker Script (45 seconds):**
  > "When we put standard RAG to the test on complex cross-paper comparisons—like comparing ReAct vs. Reflexion—it failed completely. Because it relies on a single vector search, it retrieved only ReAct chunks and literally responded: 'The context does not mention Reflexion at all, so comparison is impossible.'
  > Furthermore, vector databases are probabilistic: when asked 'How many papers were published on Waqf in 2020?', they pull 5 random chunks and hallucinate an estimate. Standard RAG lacks planning, lacks memory, and lacks deterministic computation."

---

### Slide 3: The Live Arena Showcase (Head-to-Head)
- **Visuals on Screen:** Play the animated GIF or high-definition recording from `data/videos/demo_arena_showcase.webm`.
- **Left Column:** Standard Naive RAG (Red/Failed status).
- **Right Column:** Personal DeepAgent (Green/Success with 11-dimension comparison matrix).
- **🗣️ Speaker Script (45 seconds):**
  > "Here is the live head-to-head comparison recorded via headless Chromium in our Web Arena.
  > On the left, Standard Naive RAG fails on the multi-hop query. On the right, Personal DeepAgent decomposes the query:
  > In Hop 1, it investigates ReAct. In Hop 2, it investigates Reflexion. It drafts intermediate notes into a virtual workspace scratchpad, applies a pipe sanitizer, and synthesizes a full 11-dimension comparative matrix covering reasoning loops, HumanEval benchmark scores, and memory buffers—with 100% verified catalog citations."

---

### Slide 4: Paradigm 1 vs. Paradigm 2 (The Architectural Breakthrough)
- **Visuals on Screen:** The Paradigm Comparison Table:
  - **Paradigm 1 (Monolithic / Eager):** 15–20 tool JSON schemas stuffed into every turn's system prompt -> 4,000–8,000 tokens burned -> Frequent LLM tool confusion.
  - **Paradigm 2 (Skill-Driven Harness):** Initial context = **~250 tokens** -> 3 lightweight meta-tools (`list_available_skills`, `read_skill_spec`, `execute_skill_tool`) -> JIT discovery via `SKILL.md` -> **95% token savings & zero tool confusion**.
- **🗣️ Speaker Script (60 seconds):**
  > "A critical architectural decision in this project was transitioning from Paradigm 1 to Paradigm 2.
  > In traditional agent frameworks, developers eagerly bind 15 or 20 tools directly to the model. That burns up to 8,000 tokens per turn before the user even speaks, and LLMs suffer from 'tool confusion'—hallucinating arguments or picking the wrong tool.
  > In Paradigm 2, our agent boots up with an ultra-lean 250-token context. It discovers skills dynamically from `SKILL.md` packages. It reads the exact Standard Operating Procedure (SOP) just-in-time, follows the invariants, and executes cleanly. This decoupled design also powers our Dual-Interface pattern: every capability runs both as an AI `@tool` and as a standalone CLI script in `scripts/`."

---

### Slide 5: The Modular Skills Suite
- **Visuals on Screen:** Matrix of the 4 self-contained skill packages:
  - **`catalog` Skill**: In-process DuckDB SQL over `catalog.csv` (871+ papers) -> sub-10ms exact counts.
  - **`retriever` Skill**: Two-stage Hybrid Fusion (Dense Chroma + Sparse BM25 via RRF) + local FlashRank cross-encoder.
  - **`memory` Skill**: Mem0 autonomous cross-session identity and research interest persistence.
  - **`ingestion` Skill**: PyMuPDF4LLM + Section Chunker + Layer 1 Jev Chunk Health Gate.
- **🗣️ Speaker Script (45 seconds):**
  > "The agent's capabilities are cleanly encapsulated into 4 modular skills. 
  > When asked about publication statistics, it routes to DuckDB. When asked deep conceptual questions, it activates the Hybrid Retriever. It remembers user context cross-session with Mem0 without asking for permission, and every incoming document is gated through our ingestion pipeline before entering ChromaDB."

---

### Slide 6: Production Engineering — The "Tiny Designs"
- **Visuals on Screen:** Code snippets and before/after comparisons for the 3 key Python mechanisms:
  1. **The Python Header Stack (`chunker.py`):** LIFO stack tracking `#`, `##` to build breadcrumb paths (`4. Method > 4.1 Reasoning Loop`) in < 15ms with $0.00 cost.
  2. **Table Preservation State Machine:** `in_table` boolean buffer preventing tables from being chopped in half.
  3. **The Pipe Sanitizer (`sanitizer.py`):** Converts cell pipes `|` -> `—` so Markdown comparison tables never break column alignment.
- **🗣️ Speaker Script (60 seconds):**
  > "What separates production RAG from hobby projects is attention to tiny failure modes. 
  > Instead of spending LLM tokens to summarize chunks, we wrote a pure Python LIFO header stack in `chunker.py`. In under 15 milliseconds and at zero cost, it prepends `[Document: X | Section: Chapter > Subchapter]` to every chunk, completely solving the 'lost in the middle' problem.
  > We also built an in-stream table state machine that treats markdown tables as indivisible units so they're never split across chunk boundaries, and a pipe sanitizer that prevents paper titles like 'ReAct: Reasoning | Acting' from breaking markdown table columns."

---

### Slide 7: Deterministic vs. Probabilistic (The DuckDB SQL Edge)
- **Visuals on Screen:** Side-by-side: Vector Search Hallucination vs. DuckDB ANSI SQL.
  - Query: *"How many papers on Waqf were published in 2020?"*
  - Vector DB: "Based on the 5 chunks retrieved, approximately 5 papers..." ❌
  - DuckDB: `SELECT COUNT(*) FROM catalog WHERE lower(title) LIKE '%waqf%' AND year = 2020` -> Exactly 2 verified papers in 8.2ms. ✅
- **🗣️ Speaker Script (45 seconds):**
  > "Here is a crucial principle I follow: **Never use probabilistic LLMs for deterministic math.**
  > If a user asks for paper counts or publication years, vector search can only guess based on chunk density. Our agent detects counting intent and immediately executes deterministic ANSI SQL directly over `catalog.csv` via DuckDB.
  > This provides mathematical certainty, sub-10ms response times, and character-for-character canonical URLs from the metadata catalog."

---

### Slide 8: Empirical Validation — Stanford HotpotQA Multi-Hop Benchmark
- **Visuals on Screen:** Results Table on official Stanford HotpotQA distractor dataset:
  - **Supporting Fact Recall:** 60.0% (Single-pass) -> **100.0% (DeepAgent)** (**+40.0% Recall Lift** 🚀)
  - **Answer Exact Match (EM):** 60.0% -> **100.0%** (5 / 5 Pass) ✅
  - **Faithfulness:** **94.0%** (Grounded & verifiable)
  - Multi-hop case study: *Kiss and Tell* -> Shirley Temple -> Chief of Protocol.
- **🗣️ Speaker Script (60 seconds):**
  > "To validate this architecture against academic standards, we benchmarked against the official Stanford HotpotQA multi-hop dataset with distractor documents.
  > Single-pass RAG achieved only 60% Recall and 60% Exact Match. DeepAgent scored **100% Exact Match and 100% Fact Recall**—a direct **+40% accuracy lift**.
  > For example, on the query asking for the diplomatic office of the actress from 'Kiss and Tell', single-pass RAG found the actress Shirley Temple but missed her government career. DeepAgent extracted Shirley Temple in Hop 1, autonomously queried her diplomatic biography in Hop 2, and correctly answered: 'Chief of Protocol of the United States'."

---

### Slide 9: Cost & Latency Engineering with Jev Decision Model
- **Visuals on Screen:** Comparison: Generative LLM-as-a-judge vs. Jev (`TypeSafe AI` System-1):
  - **Latency:** 6.53s -> **300ms** (Single-pass parallel forward pass)
  - **Output Token Fees:** $0.56 / 1M -> **$0.00 (100% Free output)**
  - **Total Cost per 1,000 Evals:** ~$0.95 -> **~$0.10 (~90% Cost Reduction)**
  - **Agreement:** 100% agreement on Faithfulness ($P \ge 0.50$).
- **🗣️ Speaker Script (45 seconds):**
  > "For production evaluation, relying on heavy LLMs like GPT-4 as a judge is slow (6.5s) and expensive.
  > We integrated **Jev from TypeSafe AI**, a non-generative System-1 decision model. Instead of generating text, Jev evaluates all atomic claims in parallel using typed boolean `noul` primitives.
  > This runs in sub-500ms, completely eliminates output token fees, and delivers **~90% direct cost savings** with zero evaluator hallucinations."

---

### Slide 10: Conclusion, Testing & Live Demo
- **Visuals on Screen:**
  - 66 of 66 automated tests passing in `pytest`.
  - Links to GitHub repo: `github.com/qtongggg/personal-deepagent`.
  - Live terminal / Web arena invite.
- **🗣️ Speaker Script (30 seconds):**
  > "To summarize: Personal DeepAgent proves that production RAG is an engineering discipline, not just prompt engineering. By combining dynamic skill discovery, active planning, deterministic SQL, and calibrated decision models, we turn brittle RAG into an enterprise-grade research engine.
  > All 66 tests pass in CI/CD, the code is open on GitHub, and I'd be happy to demonstrate the live arena or answer any technical questions."

---

## 💻 Live Demo Commands (If Asked to Run Live)

1. **Web Arena Demo:**
   ```bash
   python scripts/run_server.py
   # Open browser at http://localhost:8000
   ```
2. **Terminal CLI Quick Turn:**
   ```bash
   python scripts/run_agent.py
   ```
3. **Instant Unit Test Verification:**
   ```bash
   pytest tests/test_skill_registry.py tests/test_paradigm2_agent.py -v
   ```
