import pytest
from typing import Any, Dict


def test_skill_registry_discovery():
    """Verify SkillRegistry discovers all 4 modular skills from disk."""
    from src.skills.registry import SkillRegistry

    registry = SkillRegistry()
    skills = registry.list_skills()

    assert "catalog_skill" in skills
    assert "retriever_skill" in skills
    assert "memory_skill" in skills
    assert "ingestion_skill" in skills


def test_skill_registry_manifest_metadata():
    """Verify YAML frontmatter extraction generates compact skill manifest."""
    from src.skills.registry import SkillRegistry

    registry = SkillRegistry()
    manifest = registry.get_skill_manifest()

    assert len(manifest) >= 4
    names = [m["name"] for m in manifest]
    assert "catalog_skill" in names
    assert "retriever_skill" in names

    # Catalog manifest must have description, triggers and tools
    cat_entry = next(m for m in manifest if m["name"] == "catalog_skill")
    assert "DuckDB" in cat_entry["description"] or "catalog" in cat_entry["description"]
    assert "catalog_query" in cat_entry["tools"]
    assert len(cat_entry["triggers"]) > 0


def test_skill_registry_get_spec():
    """Verify getting full SKILL.md specification on-demand."""
    from src.skills.registry import SkillRegistry

    registry = SkillRegistry()
    spec = registry.get_skill_spec("catalog_skill")
    assert "Catalog Skill Specification" in spec

    # Case-insensitive and alias resolution
    spec_alias = registry.get_skill_spec("catalog")
    assert "Catalog Skill Specification" in spec_alias

    # Unknown skill handling
    unknown = registry.get_skill_spec("non_existent_skill")
    assert "Unknown skill" in unknown or "not found" in unknown.lower()


def test_skill_registry_tool_dispatch():
    """Verify dynamic tool retrieval and execution via registry."""
    from src.skills.registry import SkillRegistry

    registry = SkillRegistry()

    # Get tool callable
    tool_fn = registry.get_tool("catalog_query")
    assert tool_fn is not None
    assert callable(tool_fn) or hasattr(tool_fn, "invoke")

    # Execute tool directly through registry
    res = registry.execute_tool("catalog_query", {"query": "SELECT COUNT(*) as count FROM catalog"})
    assert "count" in str(res).lower()
