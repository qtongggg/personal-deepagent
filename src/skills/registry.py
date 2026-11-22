"""
src/skills/registry.py
Skill Registry for Personal DeepAgent Paradigm 2 Architecture

Dynamically discovers, parses, and dispatches tools and SOPs from `src/skills/*/SKILL.md`.
"""

import logging
import os
from pathlib import Path
import re
from typing import Any, Callable, Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)

# Canonical map of tool names to their implementation import paths
_DEFAULT_TOOL_MAP: Dict[str, str] = {
    "catalog_query": "src.skills.catalog_skill:catalog_tool",
    "knowledge_retriever": "src.skills.retriever_skill:retriever_tool",
    "search_memory": "src.skills.memory_skill:search_memory_tool",
    "add_memory": "src.skills.memory_skill:add_memory_tool",
    "ingest_document_tool": "src.skills.ingestion.pipeline:ingest_document_tool",
}


def _load_tool_by_path(import_path: str) -> Optional[Any]:
    """Dynamically import and return a tool callable from module:attribute path."""
    try:
        module_path, attr_name = import_path.split(":")
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, attr_name)
    except Exception as e:
        logger.warning(f"Could not load tool from '{import_path}': {e}")
        return None


class SkillPackage:
    """Represents a discovered modular skill package."""

    def __init__(
        self,
        name: str,
        folder_path: Path,
        description: str = "",
        triggers: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        cli_commands: Optional[List[str]] = None,
        raw_markdown: str = "",
    ):
        self.name = name
        self.folder_path = folder_path
        self.description = description
        self.triggers = triggers or []
        self.tools = tools or []
        self.cli_commands = cli_commands or []
        self.raw_markdown = raw_markdown

    def to_manifest(self) -> Dict[str, Any]:
        """Return compact metadata dictionary for LLM context injection."""
        return {
            "name": self.name,
            "description": self.description,
            "triggers": self.triggers,
            "tools": self.tools,
            "cli_commands": self.cli_commands,
        }


class SkillRegistry:
    """Registry engine that indexes SKILL.md packages and dispatches tools."""

    def __init__(self, skills_dir: Optional[Path] = None):
        if skills_dir is None:
            # Default to src/skills relative to this file
            skills_dir = Path(__file__).resolve().parent
        self.skills_dir = Path(skills_dir)
        self.packages: Dict[str, SkillPackage] = {}
        self.tools: Dict[str, Any] = {}
        self.scan_skills()

    def scan_skills(self) -> None:
        """Scan skills directory for subdirectories containing SKILL.md."""
        self.packages.clear()
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory does not exist: {self.skills_dir}")
            return

        for item in self.skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    self._parse_and_register_skill(item.name, skill_md)

        # Preload canonical tools
        for tool_name, import_path in _DEFAULT_TOOL_MAP.items():
            if tool_name not in self.tools:
                loaded = _load_tool_by_path(import_path)
                if loaded is not None:
                    self.tools[tool_name] = loaded

    def _parse_and_register_skill(self, dir_name: str, skill_md: Path) -> None:
        """Parse YAML frontmatter and markdown body from SKILL.md."""
        try:
            content = skill_md.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error reading {skill_md}: {e}")
            return

        frontmatter: Dict[str, Any] = {}
        body = content

        # Extract YAML frontmatter enclosed by '---'
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if match:
            yaml_text = match.group(1)
            body = match.group(2)
            try:
                frontmatter = yaml.safe_load(yaml_text) or {}
            except Exception as e:
                logger.warning(f"Error parsing YAML frontmatter in {skill_md}: {e}")

        name = frontmatter.get("name") or dir_name
        description = frontmatter.get("description", "")
        triggers = frontmatter.get("triggers", [])
        tools = frontmatter.get("tools", [])
        cli_commands = frontmatter.get("cli_commands", [])

        pkg = SkillPackage(
            name=name,
            folder_path=skill_md.parent,
            description=description,
            triggers=triggers,
            tools=tools,
            cli_commands=cli_commands,
            raw_markdown=body.strip(),
        )
        self.packages[name.lower()] = pkg
        # Also register directory name alias if different
        if dir_name.lower() != name.lower():
            self.packages[dir_name.lower()] = pkg

    def list_skills(self) -> List[str]:
        """Return sorted list of unique registered skill names."""
        unique_names = sorted({pkg.name for pkg in self.packages.values()})
        return unique_names

    def get_skill_manifest(self) -> List[Dict[str, Any]]:
        """Generate compact manifest of all available skills for prompt injection."""
        unique_pkgs = {pkg.name: pkg for pkg in self.packages.values()}
        return [pkg.to_manifest() for pkg in unique_pkgs.values()]

    def get_skill_spec(self, skill_name: str) -> str:
        """Return full SKILL.md specification and operational rules for a skill."""
        key = str(skill_name).strip().lower()
        # Direct lookup or alias
        if key in self.packages:
            pkg = self.packages[key]
            return f"# Skill: {pkg.name}\n\n{pkg.raw_markdown}"

        # Fuzzy match
        for k, pkg in self.packages.items():
            if key in k or k in key:
                return f"# Skill: {pkg.name}\n\n{pkg.raw_markdown}"

        avail = ", ".join(self.list_skills())
        return f"Unknown skill '{skill_name}'. Available skills: {avail}"

    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Retrieve executable tool instance by name."""
        return self.tools.get(tool_name)

    def get_all_tools(self) -> List[Any]:
        """Return all active tool callables."""
        return list(self.tools.values())

    def execute_tool(self, tool_name: str, args: Any) -> Any:
        """Execute a tool dynamically by name with safe argument handling."""
        tool = self.get_tool(tool_name)
        if tool is None:
            avail = ", ".join(sorted(self.tools.keys()))
            return f"Error: Tool '{tool_name}' not found. Available tools: {avail}"

        try:
            # Handle LangChain BaseTool / @tool
            if hasattr(tool, "invoke"):
                if isinstance(args, dict):
                    return tool.invoke(args)
                elif isinstance(args, str):
                    try:
                        import json
                        parsed_args = json.loads(args)
                        if isinstance(parsed_args, dict):
                            return tool.invoke(parsed_args)
                    except Exception:
                        pass
                    # Single string argument fallback
                    return tool.invoke(args)
                return tool.invoke(args)
            elif callable(tool):
                if isinstance(args, dict):
                    return tool(**args)
                return tool(args)
            else:
                return f"Error: Tool '{tool_name}' is not callable."
        except Exception as e:
            logger.error(f"Execution error in tool '{tool_name}': {e}")
            return f"Execution error in tool '{tool_name}': {e}"


# Singleton registry instance
_GLOBAL_REGISTRY: Optional[SkillRegistry] = None


def get_skill_registry() -> SkillRegistry:
    """Return cached global SkillRegistry instance."""
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = SkillRegistry()
    return _GLOBAL_REGISTRY
