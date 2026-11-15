#!/usr/bin/env python3
"""
scripts/run_rag_eval.py
Automated Production RAG Evaluation Runner (Layer 2 Output & Generation)

Executes the Golden Evaluation Dataset against Personal DeepAgent,
runs the RAG Triad Evaluator (Faithfulness, Relevance, Context Recall, Citations, Tables),
and outputs a rich console scorecard plus machine-readable JSON & Markdown reports.
"""

import argparse
from datetime import datetime
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

# Windows UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from langchain_core.messages import AIMessage, ToolMessage
from src.agent import create_deep_research_agent
from src.utils.models import get_default_model
from src.utils.sanitizer import build_final_response
from src.utils.rag_evaluator import (
    evaluate_faithfulness,
    evaluate_answer_relevance,
    evaluate_context_recall,
    evaluate_citation_accuracy,
    evaluate_table_compliance,
    EvaluationScenarioScore,
    AggregateEvaluationReport,
)

logger = logging.getLogger(__name__)


def count_tokens_fallback(text: str) -> int:
    """Approximate token count if live usage metadata is unavailable."""
    return max(1, len(str(text)) // 4)


def run_single_deepagent_eval(
    scenario: Dict[str, Any],
    model: Optional[Any] = None,
    threshold: float = 0.75,
    evaluator_mode: str = "jev",
) -> EvaluationScenarioScore:
    """Execute DeepAgent on a single scenario and evaluate its output."""
    scenario_id = scenario["id"]
    category = scenario.get("category", "general")
    query = scenario["query"]
    key_claims = scenario.get("key_ground_truth_claims", [])
    requires_table = scenario.get("requires_table", False)

    print(f"\n[Running] Scenario: {scenario_id} ({category})")
    print(f"  Query: \"{query}\"")

    active_model = model or get_default_model()
    agent = create_deep_research_agent(model=active_model)

    t0 = time.perf_counter()
    user_prompt = f"[User Context: user_id=rag_evaluator]\n{query}"

    state = agent.invoke({"messages": [{"role": "user", "content": user_prompt}]})
    latency = round(time.perf_counter() - t0, 2)

    messages = state.get("messages", [])

    # Collect tokens & observed chunks
    prompt_tokens = 0
    completion_tokens = 0
    observed_chunks: List[Dict[str, Any]] = []

    for msg in messages:
        if isinstance(msg, AIMessage):
            usage = getattr(msg, "usage_metadata", None)
            if usage and isinstance(usage, dict):
                prompt_tokens += usage.get("input_tokens", 0)
                completion_tokens += usage.get("output_tokens", 0)
            else:
                completion_tokens += count_tokens_fallback(msg.content)
        elif isinstance(msg, ToolMessage) and getattr(msg, "name", "") == "knowledge_retriever":
            try:
                parsed = json.loads(msg.content)
                if isinstance(parsed, list):
                    observed_chunks.extend(parsed)
            except Exception:
                pass
        else:
            prompt_tokens += count_tokens_fallback(getattr(msg, "content", ""))

    if prompt_tokens == 0:
        prompt_tokens = count_tokens_fallback(query)
    if completion_tokens == 0:
        completion_tokens = count_tokens_fallback(str(messages[-1].content if messages else ""))

    # Extract final text
    raw_text = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            if isinstance(msg.content, list):
                raw_text = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in msg.content)
            else:
                raw_text = str(msg.content)
            break
        elif getattr(msg, "role", "") == "assistant":
            raw_text = str(getattr(msg, "content", ""))
            break

    if not raw_text and messages:
        raw_text = str(messages[-1].content)

    final_resp = build_final_response(raw_text, observed_chunks=observed_chunks)
    response_text = final_resp.result

    # -------------------------------------------------------------
    # Layer 2 Automated Evaluation
    # -------------------------------------------------------------
    chunk_texts = [c.get("chunk_content", "") for c in observed_chunks if isinstance(c, dict)]

    if evaluator_mode == "both":
        # 1. Benchmark Before: Generative LLM
        t_llm0 = time.perf_counter()
        faith_llm = evaluate_faithfulness(response_text, chunk_texts, model=active_model, use_jev=False)
        t_llm = round(time.perf_counter() - t_llm0, 3)

        # 2. Benchmark After: Jev Decision Model
        t_jev0 = time.perf_counter()
        faith_jev = evaluate_faithfulness(response_text, chunk_texts, model=active_model, use_jev=True)
        t_jev = round(time.perf_counter() - t_jev0, 3)

        speedup = round(t_llm / max(t_jev, 0.001), 1)

        print("\n  " + "═" * 70)
        print("  ⚡ EVALUATOR BENCHMARK: BEFORE (Generative LLM) vs AFTER (Jev Decision)")
        print("  " + "─" * 70)
        print(f"  {'Metric':<28} │ {'Before (Generative LLM)':<20} │ {'After (Jev Decision)':<18}")
        print("  " + "─" * 70)
        print(f"  {'Faithfulness Score':<28} │ {faith_llm.score * 100:>19.1f}% │ {faith_jev.score * 100:>17.1f}%")
        print(f"  {'Evaluator Latency':<28} │ {t_llm:>19.2f}s │ {t_jev:>17.3f}s")
        print(f"  {'Evaluator Output Tokens':<28} │ {'~400-600 tokens':>20} │ {'0 tokens (Decision)':>18}")
        print(f"  {'Est. Cost per 1,000 Evals':<28} │ {'~$0.95':>20} │ {'~$0.10':>18}")
        print(f"  {'Latency Speedup Factor':<28} │ {'1.0x (Baseline)':>20} │ {f'{speedup}x FASTER':>18}")
        print("  " + "═" * 70 + "\n")

        faithfulness_res = faith_jev
        eval_latency = t_jev
        eval_engine = "Jev Decision Model"
    else:
        use_jev = (evaluator_mode == "jev")
        t_eval0 = time.perf_counter()
        faithfulness_res = evaluate_faithfulness(response_text, chunk_texts, model=active_model, use_jev=use_jev)
        eval_latency = round(time.perf_counter() - t_eval0, 3)
        eval_engine = "Jev Decision Model" if use_jev and os.environ.get("JEV_API_KEY") else "Generative LLM"

    relevance_res = evaluate_answer_relevance(query, response_text, model=active_model)
    recall_score = evaluate_context_recall(response_text, key_claims, model=active_model)
    citation_score = evaluate_citation_accuracy(response_text)
    table_score = evaluate_table_compliance(response_text, requires_table=requires_table)

    # Weighted Composite Score
    # 35% Faithfulness, 30% Relevance, 20% Recall, 10% Citation, 5% Table
    composite = round(
        (0.35 * faithfulness_res.score)
        + (0.30 * relevance_res.score)
        + (0.20 * recall_score)
        + (0.10 * citation_score)
        + (0.05 * table_score),
        3,
    )

    verdict = "PASS" if composite >= threshold else "FAIL"
    status_icon = "✅" if verdict == "PASS" else "❌"

    unsupported_statements = [u.statement for u in faithfulness_res.unsupported_claims]

    print(f"  {status_icon} Score: {composite:.2f} ({verdict}) | Faithfulness: {faithfulness_res.score*100:.1f}% ({eval_engine}, {eval_latency}s) | Relevance: {relevance_res.score*100:.1f}% | Recall: {recall_score*100:.1f}%")
    if unsupported_statements:
        print(f"     ⚠️ Flagged Unsupported Claims ({len(unsupported_statements)}):")
        for st in unsupported_statements[:2]:
            print(f"       - \"{st[:90]}...\"")

    return EvaluationScenarioScore(
        scenario_id=scenario_id,
        category=category,
        query=query,
        faithfulness=faithfulness_res.score,
        answer_relevance=relevance_res.score,
        context_recall=recall_score,
        citation_accuracy=citation_score,
        table_compliance=table_score,
        composite_score=composite,
        latency_seconds=latency,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        retrieved_chunks_count=len(observed_chunks),
        unsupported_claims=unsupported_statements,
        verdict=verdict,
    )


def generate_markdown_report(report: AggregateEvaluationReport) -> str:
    """Format evaluation results into a clean GitHub Flavored Markdown scorecard."""
    md = rf"""# 📊 Personal DeepAgent: Production RAG Evaluation Scorecard

**Execution Timestamp:** `{report.timestamp}`  
**Evaluator Model:** `{report.model_name}`  
**Test Suite:** `{report.total_scenarios} Scenarios`  
**Overall Status:** **{report.passed_scenarios} / {report.total_scenarios} Passed ({report.pass_rate_pct:.1f}%)**

---

## 🎯 Executive Quality Metrics

| Evaluation Metric | Score | Target Threshold | Production Status |
| :--- | :---: | :---: | :---: |
| **Faithfulness (Zero Hallucination)** | **{report.avg_faithfulness * 100:.1f}%** | $\ge$ 85.0% | {'✅ PASS' if report.avg_faithfulness >= 0.85 else '⚠️ REVIEW'} |
| **Answer Relevance** | **{report.avg_answer_relevance * 100:.1f}%** | $\ge$ 85.0% | {'✅ PASS' if report.avg_answer_relevance >= 0.85 else '⚠️ REVIEW'} |
| **Context Recall (Ground Truth Coverage)** | **{report.avg_context_recall * 100:.1f}%** | $\ge$ 80.0% | {'✅ PASS' if report.avg_context_recall >= 0.80 else '⚠️ REVIEW'} |
| **Citation & Catalog Accuracy** | **{report.avg_citation_accuracy * 100:.1f}%** | 100.0% | {'✅ PASS' if report.avg_citation_accuracy >= 0.99 else '⚠️ REVIEW'} |
| **Structured Table Compliance** | **{report.avg_table_compliance * 100:.1f}%** | 100.0% | {'✅ PASS' if report.avg_table_compliance >= 0.99 else '⚠️ REVIEW'} |
| **Overall Composite Quality Score** | **{report.avg_composite_score * 100:.1f}%** | $\ge$ 75.0% | {'✅ PASS (Production Ready)' if report.avg_composite_score >= 0.75 else '❌ FAIL'} |
| **Average Turn Latency** | **{report.avg_latency_seconds:.2f}s** | $\le$ 15.0s | {'⚡ FAST' if report.avg_latency_seconds <= 15.0 else '🐢 HIGH'} |

---

## 📋 Scenario-by-Scenario Breakdown

| ID | Category | Faithfulness | Relevance | Recall | Citations | Table | Composite | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for s in report.scenario_scores:
        status_badge = "✅ PASS" if s.verdict == "PASS" else "❌ FAIL"
        md += f"| `{s.scenario_id}` | {s.category} | {s.faithfulness*100:.1f}% | {s.answer_relevance*100:.1f}% | {s.context_recall*100:.1f}% | {s.citation_accuracy*100:.0f}% | {s.table_compliance*100:.0f}% | **{s.composite_score*100:.1f}%** | {status_badge} |\n"

    md += """
---

## 🔬 Evaluation Methodology
1. **Faithfulness**: Decomposes agent responses into atomic factual statements and verifies each statement against retrieved chunks.
2. **Answer Relevance**: Evaluates how directly the answer satisfies the user query without drift.
3. **Context Recall**: Verifies presence of key domain claims defined in `data/eval_golden_set.json`.
4. **Citation Accuracy**: Verifies character-for-character catalog URL grounding and pipe-sanitized Markdown table structures.
"""
    return md


def main():
    parser = argparse.ArgumentParser(description="Run Production RAG Evaluation Suite")
    parser.add_argument("--golden-set", default="data/eval_golden_set.json", help="Path to golden set JSON")
    parser.add_argument("--single", default=None, help="Run only a specific scenario ID")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of scenarios")
    parser.add_argument("--threshold", type=float, default=0.75, help="Composite pass threshold (default: 0.75)")
    parser.add_argument(
        "--evaluator",
        choices=["jev", "llm", "both"],
        default=None,
        help="Faithfulness evaluator engine: 'jev' (TypeSafe AI Decision Model), 'llm' (Generative LLM), or 'both' (benchmarked side-by-side).",
    )
    parser.add_argument("--output-json", default="data/eval_report.json", help="Path for JSON output")
    parser.add_argument("--output-md", default="data/eval_report.md", help="Path for Markdown scorecard")
    args = parser.parse_args()

    evaluator_mode = args.evaluator
    if not evaluator_mode:
        evaluator_mode = "jev" if os.environ.get("JEV_API_KEY") else "llm"

    if not os.path.exists(args.golden_set):
        print(f"Error: Golden set not found at {args.golden_set}")
        sys.exit(1)

    with open(args.golden_set, "r", encoding="utf-8") as f:
        golden_data = json.load(f)

    if args.single:
        golden_data = [s for s in golden_data if s["id"] == args.single]
        if not golden_data:
            print(f"Error: Scenario '{args.single}' not found in golden set.")
            sys.exit(1)

    if args.limit:
        golden_data = golden_data[:args.limit]

    eval_label = (
        "Jev System-One Decision Model"
        if evaluator_mode == "jev"
        else ("Comparative Benchmark (Jev vs Generative LLM)" if evaluator_mode == "both" else "Generative LLM")
    )

    print("=" * 72)
    print("   PERSONAL DEEPAGENT: LAYER 2 PRODUCTION RAG EVALUATION HARNESS   ")
    print(f"   Golden Set: {len(golden_data)} Scenarios | Pass Threshold: {args.threshold*100:.0f}%")
    print(f"   Evaluator Engine: {eval_label}")
    print("=" * 72)

    model = get_default_model()
    base_model_name = getattr(model, "model_name", getattr(model, "model", "DeepSeek / Default LLM"))
    full_eval_name = f"{eval_label} ({base_model_name})"

    scenario_scores: List[EvaluationScenarioScore] = []

    for sc in golden_data:
        try:
            score = run_single_deepagent_eval(
                sc, model=model, threshold=args.threshold, evaluator_mode=evaluator_mode
            )
            scenario_scores.append(score)
        except Exception as e:
            print(f"  ❌ Error executing scenario {sc['id']}: {e}")
            scenario_scores.append(
                EvaluationScenarioScore(
                    scenario_id=sc["id"],
                    category=sc.get("category", "error"),
                    query=sc["query"],
                    faithfulness=0.0,
                    answer_relevance=0.0,
                    context_recall=0.0,
                    citation_accuracy=0.0,
                    table_compliance=0.0,
                    composite_score=0.0,
                    latency_seconds=0.0,
                    prompt_tokens=0,
                    completion_tokens=0,
                    retrieved_chunks_count=0,
                    unsupported_claims=[str(e)],
                    verdict="FAIL",
                )
            )

    # Compute aggregates
    total = len(scenario_scores)
    passed = sum(1 for s in scenario_scores if s.verdict == "PASS")
    pass_rate = round((passed / total) * 100, 1) if total > 0 else 0.0

    avg_f = round(sum(s.faithfulness for s in scenario_scores) / total, 3) if total else 0.0
    avg_r = round(sum(s.answer_relevance for s in scenario_scores) / total, 3) if total else 0.0
    avg_c = round(sum(s.context_recall for s in scenario_scores) / total, 3) if total else 0.0
    avg_cit = round(sum(s.citation_accuracy for s in scenario_scores) / total, 3) if total else 0.0
    avg_t = round(sum(s.table_compliance for s in scenario_scores) / total, 3) if total else 0.0
    avg_comp = round(sum(s.composite_score for s in scenario_scores) / total, 3) if total else 0.0
    avg_lat = round(sum(s.latency_seconds for s in scenario_scores) / total, 2) if total else 0.0

    report = AggregateEvaluationReport(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        model_name=full_eval_name,
        total_scenarios=total,
        passed_scenarios=passed,
        pass_rate_pct=pass_rate,
        avg_faithfulness=avg_f,
        avg_answer_relevance=avg_r,
        avg_context_recall=avg_c,
        avg_citation_accuracy=avg_cit,
        avg_table_compliance=avg_t,
        avg_composite_score=avg_comp,
        avg_latency_seconds=avg_lat,
        scenario_scores=scenario_scores,
    )

    # Print summary box
    print("\n" + "=" * 72)
    print("                      EVALUATION SUMMARY SCORECARD                       ")
    print("=" * 72)
    print(f"Total Scenarios Evaluated : {total}")
    print(f"Passed Scenarios          : {passed} / {total} ({pass_rate}%)")
    print(f"Avg Faithfulness (No Hallucination) : {avg_f * 100:.1f}%")
    print(f"Avg Answer Relevance                : {avg_r * 100:.1f}%")
    print(f"Avg Context Recall                  : {avg_c * 100:.1f}%")
    print(f"Avg Citation Accuracy               : {avg_cit * 100:.1f}%")
    print(f"Avg Table Compliance                : {avg_t * 100:.1f}%")
    print(f"Overall Composite Quality Score     : {avg_comp * 100:.1f}%")
    print(f"Avg Latency per Turn                : {avg_lat}s")
    print("=" * 72)

    # Save outputs
    os.makedirs(os.path.dirname(os.path.abspath(args.output_json)), exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)
    print(f"\n[Saved] Detailed JSON metrics saved to: {args.output_json}")

    md_content = generate_markdown_report(report)
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[Saved] Markdown scorecard saved to: {args.output_md}")


if __name__ == "__main__":
    main()
