import json
import logging
from typing import Any, Dict, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
import deepagents

from src.config import get_settings
from src.prompt import SYSTEM_PROMPT
from src.utils.models import get_default_model
from src.skills.registry import get_skill_registry
from src.skills.catalog_skill import catalog_tool
from src.skills.ingestion.pipeline import ingest_document_tool
from src.skills.memory_skill import add_memory_tool, search_memory_tool
from src.skills.retriever_skill import retriever_tool
from src.utils.sanitizer import build_final_response
from src.utils.schemas import AgentResponse

from pathlib import Path

logger = logging.getLogger(__name__)

_TODOS: List[str] = []


@tool("list_available_skills")
def list_available_skills() -> str:
    """List all modular skills available to Personal DeepAgent with triggers and tool names.
    Call this tool when planning tasks or when determining which specialized skill can fulfill the user's intent.
    """
    registry = get_skill_registry()
    manifest = registry.get_skill_manifest()
    lines = ["# Available Modular Skills\n"]
    for s in manifest:
        lines.append(f"### Skill: `{s['name']}`")
        lines.append(f"- **Description**: {s['description']}")
        lines.append(f"- **Tools Provided**: {', '.join(s['tools'])}")
        if s.get("triggers"):
            lines.append(f"- **Sample Triggers**: {', '.join(repr(t) for t in s['triggers'][:3])}")
        if s.get("cli_commands"):
            lines.append(f"- **CLI Command**: `{s['cli_commands'][0]}`")
        lines.append("")
    return "\n".join(lines).strip()


@tool("read_skill_spec")
def read_skill_spec(skill_name: str) -> str:
    """Read the full formal SKILL.md specification and operational rules for any skill on-demand.
    Use this to inspect exact tool schemas, SQL database columns, and invariants before executing actions.
    Available skills include: 'catalog_skill', 'retriever_skill', 'memory_skill', 'ingestion_skill'.
    """
    registry = get_skill_registry()
    return registry.get_skill_spec(skill_name)


@tool("execute_skill_tool")
def execute_skill_tool(tool_name: str, parameters: Any = None) -> str:
    """Dynamically execute a tool discovered from a SKILL.md specification.
    Pass the tool_name (e.g. 'catalog_query', 'knowledge_retriever', 'search_memory') and its parameters.
    """
    registry = get_skill_registry()
    params = parameters or {}
    res = registry.execute_tool(tool_name, params)
    if isinstance(res, (dict, list)):
        return json.dumps(res, indent=2, default=str)
    return str(res)


@tool("todo_write")
def todo_write(todos: Any) -> str:
    """Record or update research plan tasks and to-do items. Pass each task on a new line or as a list."""
    global _TODOS
    if isinstance(todos, list):
        _TODOS = [str(item).strip() for item in todos if str(item).strip()]
    else:
        _TODOS = [item.strip() for item in str(todos).split("\n") if item.strip()]
    return f"Updated todo list with {len(_TODOS)} items."


@tool("write_to_dos")
def write_to_dos(todos: Any) -> str:
    """Record or update research plan tasks and to-do items. Pass each task on a new line or as a list."""
    return todo_write.invoke({"todos": todos})


@tool("todo_read")
def todo_read() -> str:
    """Read the current research to-do list."""
    global _TODOS
    if not _TODOS:
        return "Todo list is currently empty."
    return "\n".join(f"- {item}" for item in _TODOS)





def get_agent_tools(mode: str = "hybrid") -> List[Any]:
    meta_tools = [
        list_available_skills,
        read_skill_spec,
        execute_skill_tool,
        todo_write,
        write_to_dos,
        todo_read,
    ]
    if mode == "dynamic":
        # Pure Paradigm 2: Meta-tools only, zero domain tool schema bloat
        return meta_tools
    else:
        # Hybrid Paradigm 1.5/2: Meta-tools + pre-bound domain tools (100% backward compatible)
        return meta_tools + [
            catalog_tool,
            retriever_tool,
            search_memory_tool,
            add_memory_tool,
            ingest_document_tool,
        ]


def create_deep_research_agent(
    model: Optional[BaseChatModel] = None,
    tools: Optional[List[Any]] = None,
    mode: str = "hybrid",
):
    """Compile and assemble the autonomous DeepAgent with its skill suite."""
    active_model = model or get_default_model()
    active_tools = tools if tools is not None else get_agent_tools(mode=mode)

    agent = deepagents.create_deep_agent(
        model=active_model,
        tools=active_tools,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent


def run_agent_turn(
    query: str,
    user_id: str = "default_user",
    agent: Optional[Any] = None,
    model: Optional[BaseChatModel] = None,
    mode: str = "hybrid",
) -> AgentResponse:
    """Run an autonomous DeepAgent turn, applying post-synthesis invariants."""
    if agent is None:
        agent = create_deep_research_agent(model=model, mode=mode)

    user_prompt = f"[User Context: user_id={user_id}]\n{query}"
    state = agent.invoke({"messages": [{"role": "user", "content": user_prompt}]})

    messages = state.get("messages", [])

    # Extract raw response text from the last AI message
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

    # Collect observed chunks from any knowledge_retriever tool messages
    observed_chunks: List[Dict[str, Any]] = []
    for msg in messages:
        if isinstance(msg, ToolMessage) and getattr(msg, "name", "") == "knowledge_retriever":
            try:
                parsed = json.loads(msg.content)
                if isinstance(parsed, list):
                    observed_chunks.extend(parsed)
            except Exception:
                pass

    return build_final_response(raw_text, observed_chunks=observed_chunks)
