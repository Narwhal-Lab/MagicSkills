"""Public API surface for MagicSkills.

This module exposes high-level classes/functions and keeps backward-compatible
module aliases for legacy import paths.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from .agent_tool import DEFAULT_SKILLS_ROOT, SkillTool
from .core.installer import (
    DEFAULT_SKILL_REPO,
    DEFAULT_SKILL_SUBDIR,
    create_skill,
    delete_skill,
    install,
    show_skill,
    upload_skill,
)
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
    "deleteskill",
    "changetooldescription",
    "listskill",
    "installskill",
    "uploadskill",
    "showskill",
    "createskill",
]

__version__ = "0.1.0"


def Skill_For_All_Agent(action: str, arg: str = "", name: str | None = None) -> dict[str, object]:
    """Dispatch an action to Allskills or a named skills instance."""
    instance = REGISTRY.get(name) if name else ALL_SKILLS
    return instance.skill_for_all_agent(action, arg)


def createskills(name: str, skills: list[Skill] | None = None, paths: list[str] | None = None) -> Skills:
    """Create and register a named Skills collection."""
    return REGISTRY.create(name=name, skills=skills, paths=paths)


def listskills() -> list[str]:
    """List all registered Skills collection names."""
    return REGISTRY.list()


def deleteskills(name: str) -> None:
    """Delete a registered Skills collection by name."""
    REGISTRY.delete(name)


def syncskills(name: str | None = None, output_path: str | None = None) -> str:
    """Sync one collection (or default collection) into AGENTS.md."""
    instance = REGISTRY.get(name) if name else ALL_SKILLS
    return str(instance.syncskills(output_path))


def addskill2skills(name: str, skill: Skill) -> None:
    """Add one Skill object to a named Skills collection."""
    instance = REGISTRY.get(name)
    instance.add_skill(skill)
    REGISTRY.save_instance(name)


def deleteskill(
    skill_name: str | None = None,
    skills_instance: str | None = None,
    paths: list[str] | None = None,
    base_dir: str | None = None,
) -> str:
    """Delete a skill from a collection or remove it from filesystem."""
    if skills_instance:
        if skill_name is None:
            raise ValueError("deleteskill with skills_instance requires skill_name")
        instance = REGISTRY.get(skills_instance)
        instance.remove_skill(name=skill_name, base_dir=base_dir)
        REGISTRY.save_instance(skills_instance)
        return skill_name
    if base_dir is not None:
        delete_paths = [Path(base_dir).expanduser()]
    else:
        delete_paths = paths
    deleted_path = delete_skill(skill_name, paths=delete_paths)
    return str(deleted_path)


def changetooldescription(name: str, description: str) -> None:
    """Update tool description text for a named Skills collection."""
    instance = REGISTRY.get(name)
    instance.change_tool_description(description)
    REGISTRY.save_instance(name)


def listskill() -> str:
    """List available skills from the default collection as XML text."""
    return ALL_SKILLS.listskill()


def installskill(
    source: str,
    global_: bool = False,
    universal: bool = False,
    yes: bool = False,
    target: str | None = None,
) -> list[str]:
    """Install skills from source and merge installed skills into default collection."""
    paths = install(
        source,
        global_=global_,
        universal=universal,
        yes=yes,
        target_root=Path(target).expanduser() if target else None,
    )
    return [str(p) for p in paths]


def uploadskill(
    source: str,
    repo: str = DEFAULT_SKILL_REPO,
    branch: str = "main",
    subdir: str | None = str(DEFAULT_SKILL_SUBDIR),
    yes: bool = False,
    push: bool = True,
    message: str | None = None,
    fork_repo: str | None = None,
    push_branch: str | None = None,
    create_pr: bool = False,
    pr_title: str | None = None,
    pr_body: str | None = None,
) -> dict[str, object]:
    """Upload one skill from local directory or Allskills to a target repository."""
    result = upload_skill(
        source=source,
        repo=repo,
        branch=branch,
        subdir=subdir,
        yes=yes,
        push=push,
        commit_message=message,
        fork_repo=fork_repo,
        push_branch=push_branch,
        create_pr=create_pr,
        pr_title=pr_title,
        pr_body=pr_body,
    )
    return result.__dict__


def showskill(name: str, paths: list[str] | None = None, base_dir: str | None = None) -> str:
    """Return full readable content for one skill from Allskills."""
    return show_skill(name, paths=paths, base_dir=Path(base_dir).expanduser() if base_dir else None)


def createskill(name: str, root: str | None = None) -> str:
    """Create a skill scaffold directory and register it into default collection."""
    path = create_skill(name, target_root=Path(root).expanduser() if root else None)
    return str(path)
