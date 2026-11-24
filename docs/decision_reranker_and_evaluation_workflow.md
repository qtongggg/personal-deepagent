# Architectural Blueprint: System-1 Decision Reranker & The 5-Step Evaluation Workflow

This document records the architectural findings from the Hugging Face research post [*Stop Paying the Embedding Tax: Why Simple BM25 + Seb Beats 8B Vector RAG on Quality, Speed, and Cost*](https://huggingface.co/blog/ironbcc/bm25-seb-rag-retrieval) and outlines the implementation proposal for integrating a **System-1 Decision Reranker** into **Personal DeepAgent**.

---

## 🧭 Part 1: The Core Problem — Why Heuristics Hit a Wall ("Before Seb")

In traditional search and legacy RAG pipelines (such as the WhatsDo case study), candidates are retrieved via keywords/tags and ranked using hand-tuned mathematical formulas (tag overlap + star rating + review count + distance).

### The "Incidental Mention" Failure Modes:
1. **The Cocktail Bar Dilemma**: A query for *"quiet cafe with outdoor seating for working"* ranks a loud nightlife cocktail bar #1 because it has a secondary `"cafe"` tag and 5,000 reviews, beating out genuine quiet neighborhood cafes with 100 reviews.
2. **The Gym vs. Hotel Trap**: A query for *"business hotel with a gym"* ranks CrossFit gyms #1 because `"gym"` is their primary category tag, completely missing the primary entity constraint (*hotel*).
3. **The Event Planner Trap**: A query for *"park to visit"* ranks event planner venues #1 because their descriptions mention *"located near beautiful parks"*.

> **Key Principle**: Keyword search and heuristic formulas treat words mechanically. They cannot distinguish between a **primary entity** and an **incidental mention**. A fast, calibrated decision model is needed to grade candidate intent.

---

## 🛠️ Part 2: The 5-Step Evaluation-Driven Agent Workflow

The workflow illustrated in the article is a disciplined, **Evaluation-First Migration Blueprint** designed for coding agents:

```text
[1. AUDIT & TRIAGE] ──> [2. BUILD EVAL SET] ──> [3. ESTIMATE COST] ──> [4. BATCH INFERENCE] ──> [5. BEFORE / AFTER]
```

1. **Step 1: Audit & Triage**: Keep deterministic fast filters in SQL/BM25 (sub-1ms). Move fuzzy semantic reranking and rubric evaluations to System-1 decisions.
2. **Step 2: Build Eval Set**: Freeze 50–250 real-world queries (`data/eval_golden_set.json` & HotpotQA). Record baseline Recall@k, nDCG@5, latency, and cost *before* altering code.
3. **Step 3: Estimate Cost**: Model candidate token economics at **$0.021 – $0.042 / 1M input tokens** ($0.00 output fees) vs expensive 8B cross-encoders or vector DB hosting ($25–$70/mo).
4. **Step 4: Batch Inference**: Pack 10–20 candidates into a single parallel HTTP call (`seb_decide` / Jev `systemone`). Evaluate using a calibrated 3-way `choice` rubric: `["strong", "partial", "wrong"]`.
5. **Step 5: Before / After**: Re-run the frozen eval set against the new pipeline. Assert statistically significant nDCG lift (e.g. WhatsDo lifted from **0.852 $\to$ 0.973** with 142 wins vs. 11 losses).

---

## 💡 Part 3: Implementation Architecture for Personal DeepAgent

Currently, Personal DeepAgent's `retriever_skill` uses:
- **Stage 1**: Hybrid dense vector (ChromaDB) + sparse lexical (BM25) fused via Reciprocal Rank Fusion (RRF).
- **Stage 2**: Local FlashRank ONNX cross-encoder (`ms-marco-TinyBERT-L-2-v2`).

### Proposed Upgrade: System-1 Decision Reranker with 3-Way Choice Rubric
- **Stage 1 (Unchanged)**: Rapid sub-10ms candidate shortlisting (top 15–20 candidates).
- **Stage 2A (New Decision Reranker)**: If `JEV_API_KEY` (or `SEB_API_KEY`) is present, pack candidates into a single parallel forward pass (~200ms).
- **Relevance Scoring Formula**:
  $$\text{Relevance Score} = P(\text{"strong"}) + 0.5 \times P(\text{"partial"})$$
- **Noise Pruning Gate**: Any candidate with $\text{Score} < 0.40$ is dropped entirely, preventing distractor context pollution.
- **Fail-Open Fallback**: Automatic local fallback to FlashRank if the API times out (> 1.5s) or key is unset.
