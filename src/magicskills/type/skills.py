"""Skills collection domain logic.

Includes discovery, read/exec operations, AGENTS.md sync, and tool-style
action dispatch compatible with skill_tool semantics.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Mapping

from .result import ExecResult
from .skill import Skill
from ..utils.utils import (
    normalize_paths,
    skill_paths_from_skills,
    skill_paths_to_skills,
)

if TYPE_CHECKING:
    from .skillsregistry import SkillsRegistry

DEFAULT_TOOL_DESCRIPTION = inspect.cleandoc(
    """
    Unified skill tool. First use "listskill" to find relevant skills. 
    Then use "readskill" to read the selected skill's SKILL.md or related docs. 
    If needed, use "execskill" to run the command.


    Input format:
    {
        "action": "<action_name>",
        "arg": "<string argument>"
    }

    Actions:
    - listskill
    - readskill: arg = file path
    - execskill: arg = full command string
    """
)

DEFAULT_CLI_DESCRIPTION = inspect.cleandoc(
    """
    Unified skill CLI tool. Whenever you receive a task, you must first run "magicskills skill-tool listskill --name {skills_name}" to view all available skills.
    Then use "magicskills skill-tool readskill --arg <file_path>" to read the selected skill's SKILL.md file by path.
    Based on that documentation, either continue reading more files with "magicskills skill-tool readskill --arg <file_path>" or run the needed command with "magicskills skill-tool execskill --arg <command>".
    """
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
        cli_description: str | None = None,
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
        self.cli_description = cli_description or DEFAULT_CLI_DESCRIPTION
        self.agent_md_path = _absolute_path(agent_md_path) if agent_md_path else _absolute_path("AGENTS.md")
        self._registry: SkillsRegistry | None = None

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

    def addskill(self, target: Path | str, source: str | Path | None = None) -> Path:
        """Register one skill by target(name or path) into this collection."""
        from ..command.addskill import addskill as command_addskill

        return command_addskill(self, target=target, source=source)

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
        shell: bool = True,
        timeout: float | None = None,
        stream: bool = False,
    ) -> ExecResult:
        """Execute shell command in current cwd."""
        from ..command.execskill import execskill as command_execskill

        return command_execskill(
            self,
            command=command,
            shell=shell,
            timeout=timeout,
            stream=stream,
        )

    def change_tool_description(self, description: str) -> None:
        """Update invocation text used in generated XML usage section."""
        from ..command.change_tool_description import change_tool_description as command_change_tool_description

        command_change_tool_description(self, description)

    def change_cli_description(self, description: str) -> None:
        """Update CLI description used in generated XML usage section."""
        from ..command.change_cli_description import change_cli_description as command_change_cli_description

        command_change_cli_description(self, description)

    def syncskills(self, output_path: Path | str | None = None, mode: str = "none") -> Path:
        """Sync current skills collection into AGENTS.md content."""
        from ..command.syncskills import syncskills as command_syncskills

        return command_syncskills(self, output_path, mode=mode)

    def scanskill(
        self,
        target: str | Path,
        *,
        base_url: str | None = None,
        model: str | None = None,
        token: str | None = None,
        model_base_url: str | None = None,
        prompt: str | None = None,
        language: str | None = None,
        thread: int | None = None,
        poll_interval: float | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, object]:
        """Scan one named or path-resolved skill from this collection."""
        from ..command.scanskill import scanskill as command_scanskill

        return command_scanskill(
            self.get_skill(target),
            base_url=base_url,
            model=model,
            token=token,
            model_base_url=model_base_url,
            prompt=prompt,
            language=language,
            thread=thread,
            poll_interval=poll_interval,
            timeout=timeout,
            headers=headers,
        )

    def scanskills(
        self,
        *,
        fail_fast: bool = False,
        base_url: str | None = None,
        model: str | None = None,
        token: str | None = None,
        model_base_url: str | None = None,
        prompt: str | None = None,
        language: str | None = None,
        thread: int | None = None,
        poll_interval: float | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, object]:
        """Scan all skills in this collection with AI-Infra-Guard."""
        from ..command.scanskills import scanskills as command_scanskills

        return command_scanskills(
            self,
            fail_fast=fail_fast,
            base_url=base_url,
            model=model,
            token=token,
            model_base_url=model_base_url,
            prompt=prompt,
            language=language,
            thread=thread,
            poll_interval=poll_interval,
            timeout=timeout,
            headers=headers,
        )

    def skill_tool(self, action: str, arg: str = "") -> dict[str, object]:
        """Dispatch action/arg payload for agent tool compatibility."""
        from ..command.skill_tool import skill_tool as command_skill_tool

        return command_skill_tool(self, action, arg)
