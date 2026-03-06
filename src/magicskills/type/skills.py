"""Skills collection domain logic.

Includes discovery, read/exec operations, AGENTS.md sync, and tool-style
action dispatch compatible with skill_tool semantics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

from .result import ExecResult
from .skill import Skill
from ..utils.utils import (
    normalize_paths,
    skill_paths_from_skills,
    skill_paths_to_skills,
)

DEFAULT_TOOL_DESCRIPTION = (
    '''Unified skill tool. If you are not sure, you can first use the "listskill"
    function of this tool to search for available skills. Then, determine which skill 
    might be the most useful. After that, try to use the read the SKILL.md file under this 
    skill path to get more detailed information. Finally, based on the content of this 
    file, decide whether to read the documentation in other paths or directly execute 
    the relevant script.
       Input format:
        {
            "action": "<action_name>",
            "arg": "<string argument>"
        }

    Actions:
    - listskill
    - readskill:     arg = file path
    - execskill:   arg = full command string'''
)


def _absolute_path(value: Path | str) -> Path:
    """Normalize a path-like value to absolute path."""
    return Path(value).expanduser().resolve()


def _looks_like_path_input(value: str | Path) -> bool:
    """Return True when target should be treated as filesystem path."""
    if isinstance(value, Path):
        return True
    raw = str(value).strip()
    if not raw:
        return False
    if "/" in raw or "\\" in raw or raw.startswith(".") or raw.startswith("~"):
        return True
    return Path(raw).expanduser().exists()


def _resolved_paths(paths: Iterable[Path | str]) -> list[Path]:
    """Normalize paths for equality checks."""
    return [Path(path).expanduser().resolve() for path in paths]


def _resolved_skill_paths(skills: Iterable[Skill]) -> list[Path]:
    """Normalize skill paths for equality checks."""
    return [skill.path.expanduser().resolve() for skill in skills]


class Skills:
    """A collection of skills with high-level operations."""

    def __init__(
        self,
        skill_list: Iterable[Skill] | None = None,
        paths: Iterable[Path | str] | None = None,
        tool_description: str | None = None,
        agent_md_path: Path | str | None = None,
        name: str = "all",
    ) -> None:
        self.name = name
        self.skill_list = list(skill_list) if skill_list is not None else []
        self.paths = normalize_paths(paths) if paths is not None else []

        if self.skill_list and self.paths:
            paths_from_skills = skill_paths_from_skills(self.skill_list)
            skills_from_paths = skill_paths_to_skills(self.paths)

            if _resolved_paths(paths_from_skills) != _resolved_paths(self.paths):
                raise ValueError("skills and paths do not match")
            if _resolved_skill_paths(skills_from_paths) != _resolved_skill_paths(self.skill_list):
                raise ValueError("skills and paths do not match")
        elif self.skill_list:
            self.paths = skill_paths_from_skills(self.skill_list)
        elif self.paths:
            self.skill_list = skill_paths_to_skills(self.paths)

        self.tool_description = tool_description or DEFAULT_TOOL_DESCRIPTION
        self.agent_md_path = _absolute_path(agent_md_path) if agent_md_path else _absolute_path("AGENTS.md")

    @property
    def skills(self) -> list[Skill]:
        """Return a copy of internal skill list."""
        return list(self.skill_list)

    def get_skill(self, target: str | Path) -> Skill:
        """Get one skill by target(name or skill directory path)."""
        if _looks_like_path_input(target):
            target_path = Path(target).expanduser().resolve()
            for skill in self.skill_list:
                if skill.path.expanduser().resolve() == target_path:
                    return skill
            raise KeyError(f"Skill path '{target_path}' not found")

        name = str(target).strip()
        matches = [skill for skill in self.skill_list if skill.name == name]
        if not matches:
            raise KeyError(f"Skill '{name}' not found")
        if len(matches) > 1:
            options = ", ".join(str(skill.path) for skill in matches)
            raise KeyError(f"Multiple skills named '{name}' found. Provide path. Candidates: {options}")
        return matches[0]

    def createskill(self, skill_path: Path | str, source: str | Path | None = None) -> Path:
        """Create one skill scaffold and register it into this collection."""
        from ..command.createskill import createskill as command_createskill

        return command_createskill(self, skill_path=skill_path, source=source)

    def deleteskill(self, target: str | Path) -> str:
        """Delete one skill by target(name or path) from this collection."""
        from ..command.deleteskill import deleteskill as command_deleteskill

        return command_deleteskill(self, str(target))

    def listskill(self) -> str:
        """Render available skills as simple text list."""
        from ..command.listskill import listskill as command_listskill

        return command_listskill(self)

    def readskill(self, target: str | Path) -> str:
        """Read file content by explicit path or by skill name (reads that skill's SKILL.md)."""
        from ..command.readskill import readskill as command_readskill

        return command_readskill(self, target)

    def uploadskill(self, target: str | Path) -> object:
        """Upload one skill by name or skill directory path using default workflow."""
        from ..command.uploadskill import uploadskill as command_uploadskill

        return command_uploadskill(self, target)

    def showskill(self, target: str | Path) -> str:
        """Show one skill with beautified metadata + full file contents."""
        from ..command.showskill import showskill as command_showskill

        return command_showskill(self, target=target)

    def execskill(
        self,
        command: str,
        env: Mapping[str, str] | None = None,
        shell: bool = True,
        timeout: float | None = None,
        stream: bool = False,
    ) -> ExecResult:
        """Execute shell command in current cwd."""
        from ..command.execskill import execskill as command_execskill

        return command_execskill(
            self,
            command=command,
            env=env,
            shell=shell,
            timeout=timeout,
            stream=stream,
        )

    def change_tool_description(self, description: str) -> None:
        """Update invocation text used in generated XML usage section."""
        from ..command.change_tool_description import change_tool_description as command_change_tool_description

        command_change_tool_description(self, description)

    def syncskills(self, output_path: Path | str | None = None) -> Path:
        """Sync current skills collection into AGENTS.md content."""
        from ..command.syncskills import syncskills as command_syncskills

        return command_syncskills(self, output_path)

    def skill_tool(self, action: str, arg: str = "") -> dict[str, object]:
        """Dispatch action/arg payload for agent tool compatibility."""
        from ..command.skill_tool import skill_tool as command_skill_tool

        return command_skill_tool(self, action, arg)
