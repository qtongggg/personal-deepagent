import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List

# Ensure root workspace is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.api import run_ingestion_sync
from src.skills.ingestion.schemas import IngestionReport

logger = logging.getLogger(__name__)

DEFAULT_10_PAPERS = [
    {
        "id": "1",
        "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
        "url": "https://arxiv.org/abs/2302.04761",
    },
    {
        "id": "2",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "url": "https://arxiv.org/abs/2201.11903",
    },
    {
        "id": "3",
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "url": "https://arxiv.org/abs/2305.10601",
    },
    {
        "id": "4",
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "url": "https://arxiv.org/abs/2305.18290",
    },
    {
        "id": "5",
        "title": "Voyager: An Open-Ended Embodied Agent with Large Language Models",
        "url": "https://arxiv.org/abs/2305.16291",
    },
    {
        "id": "6",
        "title": "Self-Refine: Iterative Refinement with Self-Feedback",
        "url": "https://arxiv.org/abs/2303.17651",
    },
    {
        "id": "7",
        "title": "Generative Agents: Interactive Simulacra of Human Behavior",
        "url": "https://arxiv.org/abs/2304.03442",
    },
    {
        "id": "8",
        "title": "HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face",
        "url": "https://arxiv.org/abs/2303.17580",
    },
    {
        "id": "9",
        "title": "Constitutional AI: Harmlessness from AI Feedback",
        "url": "https://arxiv.org/abs/2212.08073",
    },
    {
        "id": "10",
        "title": "AgentBench: Evaluating LLMs as Agents",
        "url": "https://arxiv.org/abs/2308.03688",
    },
]


def ingest_worker(paper_info: Dict[str, str], threshold: float = 0.8) -> Dict[str, Any]:
    """Single worker thread executing full ingestion pipeline for one paper."""
    worker_id = paper_info["id"]
    url = paper_info["url"]
    expected_title = paper_info["title"]
    t0 = time.perf_counter()

    print(f"[Worker #{worker_id}] [*] STARTED: {expected_title} ({url})", flush=True)

    try:
        report: IngestionReport = run_ingestion_sync(url, threshold=threshold)
        elapsed = round(time.perf_counter() - t0, 2)
        status = report.status
        doc_name = report.document_metadata.document_name
        score = report.final_recall_score
        chunks = report.total_chunks

        print(
            f"[Worker #{worker_id}] [+] FINISHED [{status}] {doc_name} ({chunks} chunks, "
            f"recall: {score * 100:.1f}%) in {elapsed}s",
            flush=True,
        )

        return {
            "worker_id": worker_id,
            "url": url,
            "document_name": doc_name,
            "title": report.document_metadata.title,
            "status": status,
            "chunks": chunks,
            "recall_score": score,
            "elapsed_seconds": elapsed,
            "error": None,
        }
    except Exception as e:
        elapsed = round(time.perf_counter() - t0, 2)
        print(f"[Worker #{worker_id}] [!] FAILED ({url}): {e} in {elapsed}s", flush=True)
        return {
            "worker_id": worker_id,
            "url": url,
            "document_name": f"FAILED_{worker_id}",
            "title": expected_title,
            "status": "ERROR",
            "chunks": 0,
            "recall_score": 0.0,
            "elapsed_seconds": elapsed,
            "error": str(e),
        }


def run_parallel_batch_ingestion(
    papers: List[Dict[str, str]],
    max_workers: int = 10,
    threshold: float = 0.8,
    output_summary_path: str = "data/parallel_ingestion_summary.json",
) -> List[Dict[str, Any]]:
    """Execute parallel ingestion of documents using a thread pool of N concurrent workers."""
    t_start = time.perf_counter()
    print("\n" + "=" * 80)
    print(f"[PARALLEL INGESTION] LAUNCHING: {len(papers)} PAPERS WITH {max_workers} CONCURRENT WORKERS")
    print("=" * 80 + "\n", flush=True)

    results: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_paper = {
            executor.submit(ingest_worker, paper, threshold): paper
            for paper in papers
        }

        for future in as_completed(future_to_paper):
            res = future.result()
            results.append(res)

    total_time = round(time.perf_counter() - t_start, 2)
    # Sort results by worker id
    results.sort(key=lambda x: int(x["worker_id"]))

    # Save summary JSON
    os.makedirs(os.path.dirname(os.path.abspath(output_summary_path)), exist_ok=True)
    with open(output_summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "total_documents": len(papers),
                "max_workers": max_workers,
                "total_wallclock_seconds": total_time,
                "results": results,
            },
            f,
            indent=2,
            default=str,
        )

    # Print summary table
    print("\n" + "=" * 80)
    print(f"[PARALLEL INGESTION] COMPLETED IN {total_time}s")
    print("=" * 80)
    print(f"{'ID':<3} | {'Status':<11} | {'Chunks':<6} | {'Recall':<7} | {'Time (s)':<8} | {'Document Name'}")
    print("-" * 80)
    for r in results:
        status_tag = f"[{r['status']}]"
        print(
            f"{r['worker_id']:<3} | {status_tag:<11} | {r['chunks']:<6} | "
            f"{r['recall_score']*100:>5.1f}% | {r['elapsed_seconds']:>8.2f} | {r['document_name']}"
        )
    print("=" * 80 + "\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch parallel document ingestion")
    parser.add_argument("--workers", type=int, default=10, help="Number of concurrent worker threads")
    parser.add_argument("--threshold", type=float, default=0.75, help="Recall evaluation threshold")
    parser.add_argument("--output", type=str, default="data/parallel_ingestion_summary.json", help="Path to save summary JSON")
    args = parser.parse_args()

    run_parallel_batch_ingestion(
        DEFAULT_10_PAPERS,
        max_workers=args.workers,
        threshold=args.threshold,
        output_summary_path=args.output,
    )
