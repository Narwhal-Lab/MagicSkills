"""Command implementation for deleting one skill from one collection or from Allskills."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from ..type.skillsregistry import ALL_SKILLS, ALL_SKILLS_NAME, REGISTRY
from ..utils.utils import is_directory_or_symlink_to_directory, skill_paths_from_skills

if TYPE_CHECKING:
    from ..type.skills import Skills


def deleteskill(skills: Skills, target: str) -> str:
    """Delete one skill by target(name or path) from one collection.

    - If `skills` is `ALL_SKILLS`, this also deletes the skill directory from filesystem.
    - Then all other collections remove the same skill by recursively calling `deleteskill`.
    """
    raw_target = target.strip()
    if not raw_target:
        raise ValueError("deleteskill requires target: <name-or-path>")

    try:
        resolved_skill = skills.get_skill(raw_target)
    except KeyError as exc:
        message = str(exc)
        if "Multiple skills named" in message:
            raise ValueError(
                f"deleteskill: skill name '{raw_target}' is duplicated; "
                "pass <skill-directory-path> as target.\n"
                f"{message}"
            ) from exc
        raise
    resolved_path = resolved_skill.path.expanduser().resolve()

    is_allskills = skills.name == ALL_SKILLS_NAME
    is_allskills = is_allskills or (skills is ALL_SKILLS)

    # Non-Allskills: only remove from this collection.
    if not is_allskills:
        before_count = len(skills.skill_list)
        skills.skill_list = [
            item
            for item in skills.skill_list
            if item.path.expanduser().resolve() != resolved_path
        ]
        if len(skills.skill_list) == before_count:
            raise KeyError(f"deleteskill: skill not found in skills instance '{skills.name}': {resolved_path}")
        skills.paths = skill_paths_from_skills(skills.skills)
        try:
            REGISTRY.saveskills()
        except KeyError:
            pass
        return str(resolved_path)

    # Allskills: physically delete directory, then remove from all other collections via same command.
    if not resolved_path.exists():
        raise FileNotFoundError(f"Skill path not found: {resolved_path}")
    if not is_directory_or_symlink_to_directory(resolved_path):
        raise ValueError(f"deleteskill expects a directory path, got: {resolved_path}")
    shutil.rmtree(resolved_path)

    before_count = len(skills.skill_list)
    skills.skill_list = [
        item
        for item in skills.skill_list
        if item.path.expanduser().resolve() != resolved_path
    ]
    if len(skills.skill_list) == before_count:
        raise KeyError(f"deleteskill: skill not found in skills instance '{skills.name}': {resolved_path}")
    skills.paths = skill_paths_from_skills(skills.skills)
    resolved_deleted = resolved_path
    try:
        REGISTRY.saveskills()
    except KeyError:
        pass

    for instance in REGISTRY.listskills():
        if instance is skills or instance.name == ALL_SKILLS_NAME:
            continue
        try:
            deleteskill(instance, str(resolved_deleted))
        except (KeyError, ValueError):
            continue
    return str(resolved_deleted)
