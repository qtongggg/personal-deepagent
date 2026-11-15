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
from src.skills.catalog_skill import catalog_tool
from src.skills.ingestion.pipeline import ingest_document_tool
from src.skills.memory_skill import add_memory_tool, search_memory_tool
from src.skills.retriever_skill import retriever_tool
from src.utils.sanitizer import build_final_response
from src.utils.schemas import AgentResponse

from pathlib import Path

logger = logging.getLogger(__name__)

_TODOS: List[str] = []

SKILL_SPEC_MAP = {
    "catalog_skill": "src/skills/catalog/SKILL.md",
    "catalog": "src/skills/catalog/SKILL.md",
    "retriever_skill": "src/skills/retriever/SKILL.md",
    "retriever": "src/skills/retriever/SKILL.md",
    "memory_skill": "src/skills/memory/SKILL.md",
    "memory": "src/skills/memory/SKILL.md",
    "ingestion_skill": "src/skills/ingestion/SKILL.md",
    "ingestion": "src/skills/ingestion/SKILL.md",
}


@tool("read_skill_spec")
def read_skill_spec(skill_name: str) -> str:
    """Read the formal SKILL.md specification for any skill on-demand.
    Available skills: 'catalog_skill', 'retriever_skill', 'memory_skill', 'ingestion_skill'.
    """
    key = str(skill_name).strip().lower()
    rel_path = SKILL_SPEC_MAP.get(key)
    if not rel_path:
        avail = ", ".join(sorted(set(SKILL_SPEC_MAP.keys())))
        return f"Unknown skill '{skill_name}'. Available skills: {avail}"

    root_dir = Path(__file__).resolve().parent.parent
    file_path = root_dir / rel_path
    if not file_path.exists():
        return f"Specification for '{skill_name}' not found at {rel_path}."

    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading specification for '{skill_name}': {e}"


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





def get_agent_tools() -> List[Any]:
    return [
        catalog_tool,
        retriever_tool,
        search_memory_tool,
        add_memory_tool,
        ingest_document_tool,
        todo_write,
        write_to_dos,
        todo_read,
        read_skill_spec,
    ]


def create_deep_research_agent(
    model: Optional[BaseChatModel] = None,
    tools: Optional[List[Any]] = None,
):
    """Compile and assemble the autonomous DeepAgent with its skill suite."""
    active_model = model or get_default_model()
    active_tools = tools if tools is not None else get_agent_tools()

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
) -> AgentResponse:
    """Run an autonomous DeepAgent turn, applying post-synthesis invariants."""
    if agent is None:
        agent = create_deep_research_agent(model=model)

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
