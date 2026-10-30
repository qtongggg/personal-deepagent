import json
import pytest
from src.agent import run_agent_turn
from src.skills.catalog_skill import get_catalog_stats, query_catalog_sql
from src.skills.memory_skill import add_memory, get_memory_client, search_memory
from src.skills.retriever_skill import retrieve_knowledge_chunks
from src.utils.sanitizer import build_final_response, restore_verbatim_catalog_urls, sanitize_table_pipes
from tests.mock_model import MockChatModel


def test_golden_trace_count_query():
    """L3 Golden Trace: Count query must query catalog deterministically."""
    # Count papers on Waqf in 2020
    results = query_catalog_sql(
        "SELECT COUNT(*) as count FROM catalog WHERE lower(title) LIKE '%waqf%' AND year = 2020"
    )
    assert len(results) == 1
    assert results[0]["count"] == 1

    # Zero result test: count papers on non-existent topic in 1950
    zero_results = query_catalog_sql(
        "SELECT COUNT(*) as count FROM catalog WHERE lower(title) LIKE '%blockchain quantum%' AND year = 1950"
    )
    assert zero_results[0]["count"] == 0

    # Simulate agent turn answering count query
    fake_response = "There is exactly 1 paper on Waqf published in 2020: IRP 25 (https://ifikr.my/resources/irp-25-waqf-microfinance/)."
    mock_model = MockChatModel(responses=[fake_response])

    response = run_agent_turn(
        query="How many papers on Waqf in 2020?",
        user_id="user_scholar",
        model=mock_model,
    )
    assert "1 paper" in response.result
    assert "https://ifikr.my/resources/irp-25-waqf-microfinance/" in response.result


def test_golden_trace_identity_persistence():
    """L3 Golden Trace: Autonomous Name & Identity Persistence without confirmation."""
    user_id = "user_mah_qt"

    # Call add_memory directly or via agent turn
    add_res = add_memory(
        user_id=user_id,
        messages=[{"role": "user", "content": "My name is Mah Qing Tong, PhD researcher at INCEIF"}],
    )
    assert add_res.get("status") == "success" or "results" in add_res

    # Search memory to verify it was stored
    memories = search_memory(user_id=user_id, query="Mah Qing Tong")
    assert len(memories) >= 1
    assert any("Mah Qing Tong" in m.get("memory", "") for m in memories)


def test_golden_trace_comparison_multihop_and_sanitization():
    """L3 Golden Trace: Compare IRP 5 and IRP 11 with multi-hop retrieval and pipe sanitization."""
    # Hop 1: Structural Probe (Intro chunks)
    irp5_intro = retrieve_knowledge_chunks("introduction thesis challenges maqasid sukuk", top_k=2, document_filter="IRP 5")
    irp11_intro = retrieve_knowledge_chunks("introduction thesis global financial stability", top_k=2, document_filter="IRP 11")

    assert len(irp5_intro) >= 1
    assert any(c["header_path"] == "/INTRODUCTION" for c in irp5_intro)
    assert len(irp11_intro) >= 1
    assert any(c["header_path"] == "/INTRODUCTION" for c in irp11_intro)

    # Hop 2: Surgical Deep Dive
    irp5_body = retrieve_knowledge_chunks("structural challenges asset-based sukuk", top_k=2, document_filter="IRP 5")
    irp11_body = retrieve_knowledge_chunks("governance systemic risk buffer", top_k=2, document_filter="IRP 11")

    assert len(irp5_body) >= 1
    assert len(irp11_body) >= 1

    # Phase 3.5: Commit comparison to memory
    add_memory(
        user_id="user_researcher",
        messages=[{"role": "user", "content": "Researched comparison between IRP 5 (Sukuk Maqasid) and IRP 11 (Stability Architecture)"}],
    )

    # Phase 4: Comparative synthesis table with unescaped pipes in title to verify sanitization
    raw_synthesis = (
        "### Comparative Analysis\n\n"
        "| Document | Title | Core Mechanism | Focus Area |\n"
        "|---|---|---|---|\n"
        "| IRP 5 | Challenges | Realizing Maqasid in Sukuk | Asset-backed vs Asset-based | Capital Markets |\n"
        "| IRP 11 | Islamic Finance | Global Stability | Architecture | Macroprudential Governance |\n"
        "| IFHUB Oct 2022 | IFHUB | October 2022 | Special Report | FinTech Innovation | Bulletins |\n\n"
        "### References\n"
        "- [IRP 5](https://ifikr.my/resources/irp-5-challenges-maqasid-sukuk/)\n"
        "- [Digital Assets](https://ifikr.my/resources/shariah-perspective)\n"
    )

    observed_chunks = irp5_intro + irp11_intro + irp5_body + irp11_body
    response = build_final_response(raw_synthesis, observed_chunks=observed_chunks)

    # 1. Pipe Sanitization check:
    # Each row in a 4-column table must split into 6 parts
    for line in response.result.strip().split("\n"):
        if line.startswith("|") and not line.startswith("|---"):
            tokens = line.split("|")
            assert len(tokens) == 6, f"Row misaligned: {line}"

    # 2. Check title pipe replaced with dash
    assert "IFHUB — October 2022 — Special Report" in response.result

    # 3. Verbatim URL restoration check (Arabic and percent encoding)
    assert "https://ifikr.my/resources/shari%ca%bfah-perspective-و/" in response.result

    # 4. Structured references check
    doc_names = [r.document_name for r in response.references]
    assert "IRP 5" in doc_names
    assert "IRP 11" in doc_names
