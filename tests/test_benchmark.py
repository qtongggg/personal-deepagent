import json
import os
import tempfile
import pytest
from tests.mock_model import MockChatModel


def test_benchmark_suite_imports():
    """Verify benchmark module components can be imported."""
    from scripts.benchmark_comparison import (
        BenchmarkResult,
        ScenarioComparison,
        count_tokens,
        run_naive_rag,
        run_deepagent_benchmark,
        compare_approaches,
        run_benchmark_suite,
    )
    assert BenchmarkResult is not None
    assert ScenarioComparison is not None


def test_count_tokens_utility():
    """Verify token counting utility accurately tokenizes text."""
    from scripts.benchmark_comparison import count_tokens

    assert count_tokens("Hello world") >= 2
    assert count_tokens("") == 0
    long_text = "This is a longer scientific explanation of acoustic side-channel leakage across wireless sensors."
    assert count_tokens(long_text) > 10


def test_naive_rag_benchmark_mock():
    """Verify run_naive_rag executes cleanly with a mock model."""
    from scripts.benchmark_comparison import run_naive_rag

    mock_resp = "In indoor office tests, signal power attenuates by 18 dB at 3 meters."
    mock_model = MockChatModel(responses=[mock_resp])

    result = run_naive_rag(
        query="What is the signal attenuation at 3 meters?",
        model=mock_model,
        top_k=2,
    )

    assert result.approach == "Standard Naive RAG"
    assert result.status == "SUCCESS"
    assert result.prompt_tokens > 0
    assert result.completion_tokens > 0
    assert result.total_tokens == result.prompt_tokens + result.completion_tokens
    assert result.latency_seconds >= 0.0
    assert "18 dB" in result.response_text


def test_deepagent_benchmark_mock():
    """Verify run_deepagent_benchmark executes cleanly with a mock model."""
    from scripts.benchmark_comparison import run_deepagent_benchmark

    mock_resp = "### Analysis\nSignal drops by 18 dB within 3m based on Ghost in the Wireless."
    mock_model = MockChatModel(responses=[mock_resp])

    result = run_deepagent_benchmark(
        query="What is the signal attenuation at 3 meters?",
        model=mock_model,
    )

    assert result.approach == "Personal DeepAgent with Skills"
    assert result.status == "SUCCESS"
    assert result.prompt_tokens > 0
    assert result.completion_tokens > 0
    assert result.latency_seconds >= 0.0
    assert "18 dB" in result.response_text


def test_compare_approaches_mock():
    """Verify compare_approaches pairs Naive RAG and DeepAgent metrics."""
    from scripts.benchmark_comparison import compare_approaches

    mock_naive = MockChatModel(responses=["Naive RAG answer with lots of redundant words."])
    mock_agent = MockChatModel(responses=["DeepAgent concise structured answer."])

    comparison = compare_approaches(
        scenario_name="Direct Lookup",
        query="What is the signal attenuation at 3 meters?",
        naive_model=mock_naive,
        agent_model=mock_agent,
    )

    assert comparison.scenario_name == "Direct Lookup"
    assert comparison.naive_rag.approach == "Standard Naive RAG"
    assert comparison.deepagent.approach == "Personal DeepAgent with Skills"
    assert isinstance(comparison.token_reduction_pct, float)
    assert isinstance(comparison.speedup_ratio, float)


def test_run_benchmark_suite_file_export():
    """Verify run_benchmark_suite saves valid JSON and Markdown files."""
    from scripts.benchmark_comparison import run_benchmark_suite

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "bench.json")
        md_path = os.path.join(tmpdir, "bench.md")

        mock_model = MockChatModel(responses=[
            "Naive answer 1", "Agent answer 1",
            "Naive answer 2", "Agent answer 2",
        ])

        results = run_benchmark_suite(
            model=mock_model,
            json_output_path=json_path,
            md_output_path=md_path,
        )

        assert len(results) == 2
        assert os.path.exists(json_path)
        assert os.path.exists(md_path)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) == 2
            assert "scenario_name" in data[0]
            assert "naive_rag" in data[0]
            assert "deepagent" in data[0]

        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            assert "# Benchmark Report" in md_content
            assert "Standard Naive RAG" in md_content
            assert "Personal DeepAgent with Skills" in md_content
