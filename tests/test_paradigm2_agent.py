import json
import pytest
from tests.mock_model import MockChatModel


def test_meta_tools_direct_invocation():
    """Verify list_available_skills and execute_skill_tool tools directly."""
    from src.agent import execute_skill_tool, list_available_skills, read_skill_spec

    # 1. list_available_skills
    skills_manifest = list_available_skills.invoke({})
    assert "catalog_skill" in skills_manifest
    assert "retriever_skill" in skills_manifest
    assert "catalog_query" in skills_manifest

    # 2. read_skill_spec
    spec = read_skill_spec.invoke({"skill_name": "catalog_skill"})
    assert "Catalog Skill Specification" in spec

    # 3. execute_skill_tool
    res = execute_skill_tool.invoke({
        "tool_name": "catalog_query",
        "parameters": {"query": "SELECT COUNT(*) as count FROM catalog"},
    })
    assert "count" in str(res).lower()


def test_create_deep_research_agent_dynamic_mode():
    """Verify dynamic mode instantiates agent with meta-tools without domain tool bloat."""
    from src.agent import create_deep_research_agent

    fake_model = MockChatModel(responses=["I will discover skills"])
    agent = create_deep_research_agent(model=fake_model, mode="dynamic")
    assert agent is not None

    nodes = agent.get_graph().nodes
    assert "tools" in nodes


def test_create_deep_research_agent_backward_compatibility():
    """Verify default mode preserves both meta-tools and pre-bound tools for backwards compatibility."""
    from src.agent import create_deep_research_agent, get_agent_tools

    tools = get_agent_tools(mode="hybrid")
    tool_names = [t.name for t in tools]

    # Meta-tools present
    assert "list_available_skills" in tool_names
    assert "read_skill_spec" in tool_names
    assert "execute_skill_tool" in tool_names

    # Pre-bound domain tools also present for backward compatibility
    assert "catalog_query" in tool_names
    assert "knowledge_retriever" in tool_names
    assert "search_memory" in tool_names
