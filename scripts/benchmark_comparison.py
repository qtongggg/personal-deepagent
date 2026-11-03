import argparse
from datetime import datetime
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# Ensure root workspace is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
import tiktoken

from src.agent import create_deep_research_agent
from src.utils.chroma import get_chroma_client
from src.utils.models import get_default_model
from src.utils.sanitizer import build_final_response

logger = logging.getLogger(__name__)


class BenchmarkResult(BaseModel):
    approach: str
    query: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_seconds: float
    response_text: str
    chunks_retrieved: int = 0
    has_table: bool = False
    status: str = "SUCCESS"
    error: Optional[str] = None


class ScenarioComparison(BaseModel):
    scenario_name: str
    query: str
    naive_rag: BenchmarkResult
    deepagent: BenchmarkResult
    token_reduction_pct: float = Field(
        ...,
        description="Percentage reduction in total tokens by DeepAgent compared to Naive RAG",
    )
    speedup_ratio: float = Field(
        ...,
        description="Latency ratio: Naive RAG latency / DeepAgent latency (>1 means DeepAgent is faster)",
    )


def count_tokens(text: str) -> int:
    """Accurately count tokens using tiktoken (cl100k_base), falling back to character approximation."""
    if not text:
        return 0
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(str(text)))
    except Exception:
        return max(1, len(str(text)) // 4)


def run_naive_rag(
    query: str,
    model: Optional[BaseChatModel] = None,
    top_k: int = 5,
    collection_name: str = "document_knowledge",
) -> BenchmarkResult:
    """Execute Standard Naive RAG: single-shot Chroma query with raw concatenated chunks."""
    t0 = time.perf_counter()
    active_model = model or get_default_model()

    # 1. Retrieve top-k chunks from ChromaDB
    docs: List[str] = []
    try:
        client = get_chroma_client()
        collection = client.get_collection(collection_name)
        count = collection.count()
        actual_k = min(top_k, max(1, count))
        res = collection.query(query_texts=[query], n_results=actual_k)
        if res and res.get("documents") and len(res["documents"]) > 0:
            docs = res["documents"][0]
    except Exception as e:
        logger.warning(f"Naive RAG retrieval encountered warning: {e}")
        docs = []

    # 2. Build Naive Prompt: dumps all retrieved chunks into context
    context_str = "\n\n---\n\n".join(docs) if docs else "No relevant documents found."
    naive_prompt = (
        "You are an assistant answering questions using only the retrieved documents.\n\n"
        f"Context Documents:\n{context_str}\n\n"
        f"Question: {query}\n\n"
        "Answer thoroughly and accurately based on the context above. Include citations if available."
    )

    prompt_tokens = count_tokens(naive_prompt)
    raw_output = ""
    completion_tokens = 0
    status = "SUCCESS"
    error_msg = None

    # 3. Execute single LLM call
    try:
        ai_msg = active_model.invoke([HumanMessage(content=naive_prompt)])
        if isinstance(ai_msg, AIMessage):
            if isinstance(ai_msg.content, list):
                raw_output = "".join(
                    b.get("text", "") if isinstance(b, dict) else str(b)
                    for b in ai_msg.content
                )
            else:
                raw_output = str(ai_msg.content)
            
            # Extract live usage_metadata if available from provider
            usage = getattr(ai_msg, "usage_metadata", None)
            if usage and isinstance(usage, dict):
                prompt_tokens = usage.get("input_tokens", prompt_tokens)
                completion_tokens = usage.get("output_tokens", count_tokens(raw_output))
            else:
                completion_tokens = count_tokens(raw_output)
        else:
            raw_output = str(getattr(ai_msg, "content", ai_msg))
            completion_tokens = count_tokens(raw_output)
    except Exception as e:
        status = "ERROR"
        error_msg = str(e)
        raw_output = f"Execution error: {e}"

    latency = time.perf_counter() - t0
    total_tokens = prompt_tokens + completion_tokens
    has_table = "|" in raw_output and ("|---" in raw_output or "|:--" in raw_output or "-|-" in raw_output)

    return BenchmarkResult(
        approach="Standard Naive RAG",
        query=query,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_seconds=round(latency, 3),
        response_text=raw_output,
        chunks_retrieved=len(docs),
        has_table=has_table,
        status=status,
        error=error_msg,
    )


def run_deepagent_benchmark(
    query: str,
    model: Optional[BaseChatModel] = None,
    user_id: str = "benchmark_evaluator",
) -> BenchmarkResult:
    """Execute Personal DeepAgent with Skills: planning, catalog verification, virtual filesystem, and pipe sanitization."""
    t0 = time.perf_counter()
    active_model = model or get_default_model()

    status = "SUCCESS"
    error_msg = None
    raw_output = ""
    chunks_retrieved = 0
    prompt_tokens = 0
    completion_tokens = 0

    try:
        agent = create_deep_research_agent(model=active_model)
        user_prompt = f"[User Context: user_id={user_id}]\n{query}"
        
        # Invoke agent
        state = agent.invoke({"messages": [{"role": "user", "content": user_prompt}]})
        messages = state.get("messages", [])

        # Collect token statistics from messages
        accumulated_input_tokens = 0
        accumulated_output_tokens = 0
        has_usage_metadata = False

        for msg in messages:
            if isinstance(msg, AIMessage):
                usage = getattr(msg, "usage_metadata", None)
                if usage and isinstance(usage, dict):
                    has_usage_metadata = True
                    accumulated_input_tokens += usage.get("input_tokens", 0)
                    accumulated_output_tokens += usage.get("output_tokens", 0)
            if isinstance(msg, ToolMessage) and getattr(msg, "name", "") == "knowledge_retriever":
                try:
                    parsed = json.loads(msg.content)
                    if isinstance(parsed, list):
                        chunks_retrieved += len(parsed)
                except Exception:
                    pass

        # Fallback token counting via tiktoken if live usage metadata is unavailable
        if not has_usage_metadata:
            for msg in messages:
                content = str(getattr(msg, "content", ""))
                if isinstance(msg, AIMessage):
                    accumulated_output_tokens += count_tokens(content)
                    # Include tool call arguments
                    if getattr(msg, "tool_calls", None):
                        accumulated_output_tokens += count_tokens(str(msg.tool_calls))
                else:
                    accumulated_input_tokens += count_tokens(content)

        prompt_tokens = accumulated_input_tokens
        completion_tokens = accumulated_output_tokens

        # Extract raw text from the last AI message
        raw_text = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                if isinstance(msg.content, list):
                    text_parts = [
                        block.get("text", "") if isinstance(block, dict) else str(block)
                        for block in msg.content
                    ]
                    raw_text = "".join(text_parts)
                else:
                    raw_text = str(msg.content)
                break
            elif getattr(msg, "role", "") == "assistant":
                raw_text = str(getattr(msg, "content", ""))
                break

        if not raw_text and messages:
            raw_text = str(messages[-1].content)

        observed_chunks: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ToolMessage) and getattr(msg, "name", "") == "knowledge_retriever":
                try:
                    parsed = json.loads(msg.content)
                    if isinstance(parsed, list):
                        observed_chunks.extend(parsed)
                except Exception:
                    pass

        # Apply post-synthesis pipeline invariants (pipe sanitization, URL restoration)
        agent_response = build_final_response(raw_text, observed_chunks=observed_chunks)
        raw_output = agent_response.result

    except Exception as e:
        status = "ERROR"
        error_msg = str(e)
        raw_output = f"Execution error: {e}"

    latency = time.perf_counter() - t0
    total_tokens = prompt_tokens + completion_tokens
    has_table = "|" in raw_output and ("|---" in raw_output or "|:--" in raw_output or "-|-" in raw_output)

    return BenchmarkResult(
        approach="Personal DeepAgent with Skills",
        query=query,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_seconds=round(latency, 3),
        response_text=raw_output,
        chunks_retrieved=chunks_retrieved,
        has_table=has_table,
        status=status,
        error=error_msg,
    )


def compare_approaches(
    scenario_name: str,
    query: str,
    model: Optional[BaseChatModel] = None,
    naive_model: Optional[BaseChatModel] = None,
    agent_model: Optional[BaseChatModel] = None,
) -> ScenarioComparison:
    """Run both approaches on a scenario and compute relative efficiency metrics."""
    m_naive = naive_model or model
    m_agent = agent_model or model

    naive_res = run_naive_rag(query, model=m_naive)
    agent_res = run_deepagent_benchmark(query, model=m_agent)

    # Calculate token reduction
    if naive_res.total_tokens > 0:
        token_reduction_pct = round(
            ((naive_res.total_tokens - agent_res.total_tokens) / naive_res.total_tokens) * 100, 2
        )
    else:
        token_reduction_pct = 0.0

    # Calculate speedup ratio
    speedup_ratio = (
        round(naive_res.latency_seconds / max(agent_res.latency_seconds, 0.001), 2)
        if naive_res.latency_seconds > 0
        else 1.0
    )

    return ScenarioComparison(
        scenario_name=scenario_name,
        query=query,
        naive_rag=naive_res,
        deepagent=agent_res,
        token_reduction_pct=token_reduction_pct,
        speedup_ratio=speedup_ratio,
    )


def run_benchmark_suite(
    model: Optional[BaseChatModel] = None,
    json_output_path: Optional[str] = None,
    md_output_path: Optional[str] = None,
) -> List[ScenarioComparison]:
    """Execute standard 2-scenario benchmark suite comparing Naive RAG vs DeepAgent."""
    scenarios = [
        (
            "Scenario 1: Direct Factual Query",
            "What is the signal attenuation at 3 meters in the indoor office tests?",
        ),
        (
            "Scenario 2: Multi-Hop Cross-Section Comparison",
            "Compare the physical range results in Section 4 with the acoustic leakage threat assumptions in the Abstract and Methodology.",
        ),
    ]

    results: List[ScenarioComparison] = []
    print("\n" + "=" * 78)
    print("[BENCHMARK] EXECUTING RESEARCH BENCHMARK: Naive Standard RAG vs Personal DeepAgent")
    print("=" * 78)

    for name, q in scenarios:
        print(f"\n>> Running {name}...")
        print(f"  Query: \"{q}\"")
        comp = compare_approaches(scenario_name=name, query=q, model=model)
        results.append(comp)

        print(f"  * Standard Naive RAG   : {comp.naive_rag.total_tokens} tokens | {comp.naive_rag.latency_seconds:.2f}s | {comp.naive_rag.chunks_retrieved} chunks")
        print(f"  * DeepAgent with Skills: {comp.deepagent.total_tokens} tokens | {comp.deepagent.latency_seconds:.2f}s | {comp.deepagent.chunks_retrieved} chunks")
        if comp.token_reduction_pct > 0:
            print(f"  [+] Context Efficiency Gain: DeepAgent saved {comp.token_reduction_pct:.1f}% tokens!")
        else:
            print(f"  [i] Token difference: {comp.token_reduction_pct:.1f}%")

    # Export to JSON
    target_json = json_output_path or "data/benchmark_results.json"
    os.makedirs(os.path.dirname(os.path.abspath(target_json)), exist_ok=True)
    with open(target_json, "w", encoding="utf-8") as f:
        json.dump([r.model_dump() for r in results], f, indent=2, default=str)
    print(f"\n[Artifact] Saved detailed JSON trace to {target_json}")

    # Export to Markdown
    target_md = md_output_path or "data/benchmark_results.md"
    os.makedirs(os.path.dirname(os.path.abspath(target_md)), exist_ok=True)
    md_content = generate_markdown_report(results)
    with open(target_md, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[Artifact] Saved formatted Markdown summary to {target_md}")

    return results


def generate_markdown_report(results: List[ScenarioComparison]) -> str:
    """Generate a clean GitHub-ready Markdown benchmark table and analysis."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Benchmark Report: Personal DeepAgent with Skills vs. Standard Naive RAG",
        "",
        f"*Generated on: {now}*",
        "",
        "## Summary Results",
        "",
        "| Scenario | System | Prompt Tokens | Output Tokens | Total Tokens | Latency (s) | Chunks | Markdown Table? |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for comp in results:
        lines.append(
            f"| **{comp.scenario_name}** | **Standard Naive RAG** | "
            f"{comp.naive_rag.prompt_tokens} | {comp.naive_rag.completion_tokens} | "
            f"**{comp.naive_rag.total_tokens}** | {comp.naive_rag.latency_seconds:.2f}s | "
            f"{comp.naive_rag.chunks_retrieved} | {'Yes' if comp.naive_rag.has_table else 'No'} |"
        )
        lines.append(
            f"| | **DeepAgent with Skills** | "
            f"{comp.deepagent.prompt_tokens} | {comp.deepagent.completion_tokens} | "
            f"**{comp.deepagent.total_tokens}** | {comp.deepagent.latency_seconds:.2f}s | "
            f"{comp.deepagent.chunks_retrieved} | {'Yes' if comp.deepagent.has_table else 'No'} |"
        )

    lines.extend([
        "",
        "## Architectural Advantages",
        "",
        "1. **Context Window Efficiency**: In multi-hop research queries, Standard Naive RAG concatenates 5-10 raw chunks directly into every prompt, quickly exhausting context windows. DeepAgent offloads large text into its virtual filesystem scratchpad (`/workspace/notes.md`), preventing token bloat.",
        "2. **Zero Hallucination on Inventory**: DeepAgent uses deterministic DuckDB catalog tools over `catalog.csv` instead of guessing document metadata.",
        "3. **Structured Citation Integrity**: DeepAgent's post-synthesis pipeline automatically sanitizes markdown pipes (`|` → `—`) to prevent table rendering failures while preserving verbatim reference URLs character-for-character.",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark DeepAgent vs Standard Naive RAG")
    parser.add_argument("--query", type=str, default=None, help="Custom query to benchmark")
    parser.add_argument("--json-output", type=str, default="data/benchmark_results.json", help="Path to save JSON trace")
    parser.add_argument("--md-output", type=str, default="data/benchmark_results.md", help="Path to save Markdown report")
    args = parser.parse_args()

    if args.query:
        print(f"\nBenchmarking single query: {args.query}")
        comp = compare_approaches("Custom Query", args.query)
        print(f"Naive RAG Tokens : {comp.naive_rag.total_tokens} ({comp.naive_rag.latency_seconds:.2f}s)")
        print(f"DeepAgent Tokens : {comp.deepagent.total_tokens} ({comp.deepagent.latency_seconds:.2f}s)")
    else:
        run_benchmark_suite(json_output_path=args.json_output, md_output_path=args.md_output)
