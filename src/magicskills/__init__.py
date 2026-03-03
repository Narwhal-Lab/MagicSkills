"""Public API surface for MagicSkills.

This module exposes high-level classes/functions and keeps backward-compatible
module aliases for legacy import paths.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Mapping

from .core.installer import create_skill, delete_skill, install, show_skill, upload_skill
from .core.models import ExecResult
from .core.registry import ALL_SKILLS, REGISTRY, SkillsRegistry
from .core.skill import Skill
from .core.skills import Skills

_LEGACY_MODULE_MAP = {
    "skill": "magicskills.core.skill",
    "skills": "magicskills.core.skills",
    "models": "magicskills.core.models",
    "registry": "magicskills.core.registry",
    "installer": "magicskills.core.installer",
    "agents_md": "magicskills.core.agents_md",
    "utils": "magicskills.core.utils",
}

for _legacy_name, _target in _LEGACY_MODULE_MAP.items():
    sys.modules.setdefault(f"{__name__}.{_legacy_name}", importlib.import_module(_target))

__all__ = [
    "Skill",
    "Skills",
    "SkillsRegistry",
    "REGISTRY",
    "SkillTool",
    "DEFAULT_SKILLS_ROOT",
    "ExecResult",
    "Skill_For_All_Agent",
    "ALL_SKILLS",
    "createskills",
    "listskills",
    "deleteskills",
    "syncskills",
    "addskill2skills",
    "deleteskill2skills",
    "deleteskill",
    "changetooldescription",
    "listskill",
    "readskill",
    "execskill",
    "installskill",
    "uploadskill",
    "showskill",
    "createskill",
]

__version__ = "0.1.0"

# Backward-compatible defaults after `agent_tool` package removal.
DEFAULT_SKILLS_ROOT = Path.cwd() / ".claude" / "skills"


class SkillTool:
    """Minimal compatibility wrapper exposing a `handle` method."""

    def __init__(self, name: str | None = None) -> None:
        self.name = name

    def handle(self, payload: Mapping[str, object]) -> dict[str, object]:
        action = str(payload.get("action", ""))
        arg = str(payload.get("arg", ""))
        return Skill_For_All_Agent(action, arg, name=self.name)


def _looks_like_path_input(value: str) -> bool:
    """Return True when input should be treated as a filesystem path."""
    raw = value.strip()
    if not raw:
        return False
    if "/" in raw or "\\" in raw or raw.startswith(".") or raw.startswith("~"):
        return True
    return Path(raw).expanduser().exists()


def _resolve_allskills_target(target: str, *, action: str) -> Skill:
    """Resolve one skill from Allskills by target(name or skill directory path)."""
    raw_target = target.strip()
    if not raw_target:
        raise ValueError(f"{action} requires target: <name-or-path>")

    if _looks_like_path_input(raw_target):
        target_path = Path(raw_target).expanduser().resolve()
        for skill in ALL_SKILLS.skills:
            if skill.path.expanduser().resolve() == target_path:
                return skill
        raise KeyError(f"{action}: skill path not found in Allskills: {target_path}")

    try:
        return ALL_SKILLS.get_skill(raw_target)
    except KeyError as exc:
        message = str(exc)
        if "Multiple skills named" in message:
            raise ValueError(
                f"{action}: skill name '{raw_target}' is duplicated; "
                "pass <skill-directory-path> as target.\n"
                f"{message}"
            ) from exc
        raise


def _resolve_instance_target(instance: Skills, target: str, *, action: str) -> Skill:
    """Resolve one skill from a named collection by target(name or path)."""
    raw_target = target.strip()
    if not raw_target:
        raise ValueError(f"{action} requires target: <name-or-path>")

    if _looks_like_path_input(raw_target):
        target_path = Path(raw_target).expanduser().resolve()
        for skill in instance.skills:
            if skill.path.expanduser().resolve() == target_path:
                return skill
        raise KeyError(f"{action}: skill path not found in skills instance '{instance.name}': {target_path}")

    try:
        return instance.get_skill(raw_target)
    except KeyError as exc:
        message = str(exc)
        if "Multiple skills named" in message:
            raise ValueError(
                f"{action}: skill name '{raw_target}' is duplicated; "
                "pass <skill-directory-path> as target.\n"
                f"{message}"
            ) from exc
        raise


def _remove_skill_from_instance(instance: Skills, *, path: Path, name: str | None = None) -> bool:
    """Try removing one skill by path from a collection."""
    try:
        try:
            instance.remove_skill(name=name, path=path)
        except TypeError:
            instance.remove_skill(name=name, base_dir=path)
    except (KeyError, ValueError):
        return False
    return True


def _prune_instance_paths(instance: Skills) -> None:
    """Drop paths that no longer correspond to any skill base_dir in this instance."""
    keep = {skill.base_dir.expanduser().resolve() for skill in instance.skills}
    instance.paths = [path for path in instance.paths if path.expanduser().resolve() in keep]


def Skill_For_All_Agent(action: str, arg: str = "", name: str | None = None) -> dict[str, object]:
    """Dispatch an action to Allskills or a named skills instance."""
    instance = REGISTRY.get(name) if name else ALL_SKILLS
    return instance.skill_for_all_agent(action, arg)


def createskills(
    name: str,
    skills: list[Skill] | None = None,
    paths: list[str] | None = None,
    tool_description: str | None = None,
    agent_md_path: str | None = None,
) -> Skills:
    """Create and register a named Skills collection."""
    instance = REGISTRY.create(name=name, skills=skills, paths=paths)
    if tool_description:
        instance.change_tool_description(tool_description)
    if agent_md_path:
        instance.agent_md_path = Path(agent_md_path).expanduser().resolve()
    REGISTRY.save_instance(name)
    return instance


def listskills() -> list[str]:
    """List all registered Skills collection names."""
    return REGISTRY.list()


def deleteskills(name: str) -> None:
    """Delete a registered Skills collection by name."""
    REGISTRY.delete(name)


def syncskills(name: str, output_path: str | None = None) -> str:
    """Sync one named collection into AGENTS.md."""
    instance = REGISTRY.get(name)
    return str(instance.syncskills(output_path))


def addskill2skills(name: str, target: str) -> None:
    """Add one skill (resolved from Allskills) into a named Skills collection."""
    instance = REGISTRY.get(name)
    skill = _resolve_allskills_target(target, action="addskill2skills")

    target_base_dir = skill.base_dir.expanduser().resolve()
    known_paths = {path.expanduser().resolve() for path in instance.paths}
    if target_base_dir not in known_paths:
        instance.paths.append(skill.base_dir)

    _remove_skill_from_instance(instance, path=skill.path)
    instance.add_skill(skill)
    REGISTRY.save_instance(name)


def deleteskill2skills(name: str, target: str) -> str:
    """Remove one skill from a named Skills collection without deleting filesystem content."""
    instance = REGISTRY.get(name)
    skill = _resolve_instance_target(instance, target, action="deleteskill2skills")
    removed = _remove_skill_from_instance(instance, path=skill.path, name=skill.name)
    if not removed:
        raise KeyError(f"deleteskill2skills: failed to remove skill '{skill.name}' from '{name}'")
    _prune_instance_paths(instance)
    REGISTRY.save_instance(name)
    return str(skill.path)


def deleteskill(target: str) -> str:
    """Delete one skill by target(name or skill directory path) from filesystem and Allskills."""
    raw_target = target.strip()
    if not raw_target:
        raise ValueError("deleteskill requires target: <name-or-path>")

    if _looks_like_path_input(raw_target):
        target_name = None
        delete_paths = [Path(raw_target).expanduser()]
    else:
        resolved_skill = _resolve_allskills_target(raw_target, action="deleteskill")
        target_name = resolved_skill.name
        delete_paths = [resolved_skill.path]

    deleted_path = delete_skill(target_name, paths=delete_paths)
    resolved_deleted = deleted_path.expanduser().resolve()

    # Physical deletion happened in Allskills. Clean stale references in other collections.
    for collection_name in REGISTRY.list():
        instance = REGISTRY.get(collection_name)
        if instance is ALL_SKILLS:
            continue
        if _remove_skill_from_instance(instance, path=resolved_deleted):
            _prune_instance_paths(instance)
            REGISTRY.save_instance(collection_name)
    return str(deleted_path)


def changetooldescription(name: str, description: str) -> None:
    """Update tool description text for a named Skills collection."""
    instance = REGISTRY.get(name)
    instance.change_tool_description(description)
    REGISTRY.save_instance(name)


def listskill() -> str:
    """List available skills from Allskills as plain text."""
    return ALL_SKILLS.listskill()


def readskill(target: str | Path) -> str:
    """Read one file by path or read SKILL.md by skill name from Allskills."""
    return ALL_SKILLS.readskill(target)


def execskill(
    command: str,
    *,
    no_shell: bool = False,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
) -> ExecResult:
    """Execute one command with merged environments from all skills in Allskills."""
    return ALL_SKILLS.execskill(command, env=env, shell=not no_shell, timeout=timeout, stream=False)


def installskill(
    source: str,
    global_: bool = False,
    universal: bool = False,
    yes: bool = False,
    target: str | None = None,
) -> list[str]:
    """Install skills from source using the same behavior as CLI `install`."""
    paths = install(
        source,
        global_=global_,
        universal=universal,
        yes=yes,
        target_root=Path(target).expanduser() if target else None,
    )
    return [str(path) for path in paths]


def uploadskill(source: str) -> dict[str, object]:
    """Upload one skill with default fork->push->PR workflow."""
    result = upload_skill(source=source, create_pr=True)
    return result.__dict__


def showskill(target: str) -> str:
    """Show one skill's full content from Allskills by name or skill directory path."""
    skill = _resolve_allskills_target(target, action="showskill")
    return show_skill(skill.name, path=skill.path)


def createskill(name: str, root: str | None = None) -> str:
    """Create one skill scaffold and register into Allskills."""
    path = create_skill(name, target_root=Path(root).expanduser() if root else None)
    return str(path)
