import pytest


def test_catalog_exact_count():
    from src.skills.catalog_skill import query_catalog_sql
    results = query_catalog_sql("SELECT COUNT(*) as count FROM catalog WHERE year = 2020")
    assert isinstance(results, list)
    assert "count" in results[0]
    assert results[0]["count"] >= 2


def test_catalog_verbatim_url_preservation():
    from src.skills.catalog_skill import query_catalog_sql
    results = query_catalog_sql("SELECT source_url FROM catalog WHERE document_name = 'IRP 5'")
    assert len(results) == 1
    assert results[0]["source_url"] == "https://ifikr.my/resources/irp-5-challenges-maqasid-sukuk/"


def test_catalog_tool_execution():
    from src.skills.catalog_skill import catalog_tool
    output = catalog_tool.invoke({"query": "SELECT document_name, title FROM catalog WHERE year = 2020 ORDER BY document_name"})
    assert "IRP 5" in output
    assert "IRP 8" in output


def test_get_catalog_stats():
    from src.skills.catalog_skill import get_catalog_stats
    stats = get_catalog_stats({"year": 2020})
    assert stats["total_matching"] >= 2
