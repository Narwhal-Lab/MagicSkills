"""Command implementation for creating skills."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..type.skill import Skill
from ..utils.utils import (
    detect_location,
    extract_yaml_field,
    is_directory_or_symlink_to_directory,
    read_text,
    skill_paths_from_skills,
)

if TYPE_CHECKING:
    from ..type.skills import Skills


def createskill(
    skills: Skills,
    skill_path: Path | str,
    source: str | Path | None = None,
) -> Path:
    """Register one existing skill directory into this collection."""
    skill_dir = Path(skill_path).expanduser().resolve()
    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")
    if not is_directory_or_symlink_to_directory(skill_dir):
        raise ValueError(f"Skill path exists and is not a directory: {skill_dir}")
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"Skill directory is invalid (missing SKILL.md): {skill_dir}")

    content = read_text(skill_md)
    description = extract_yaml_field(content, "description")
    is_global, universal = detect_location(skill_dir.parent)
    created_source = str(source).strip() if source is not None else ""
    if not created_source:
        created_source = str(skill_dir.parent.expanduser().resolve())
    created_skill = Skill(
        name=skill_dir.name,
        description=description,
        path=skill_dir,
        base_dir=skill_dir.parent,
        source=created_source,
        is_global=is_global,
        universal=universal,
    )

    from ..type.skillsregistry import ALL_SKILLS, REGISTRY

    all_skills = ALL_SKILLS()
    created_skill_path = created_skill.path.expanduser().resolve()
    if all_skills is not skills:
        all_skills.skill_list = [
            item
            for item in all_skills.skill_list
            if item.path.expanduser().resolve() != created_skill_path
        ]
        all_skills.skill_list.append(created_skill)
        all_skills.paths = skill_paths_from_skills(all_skills.skill_list)

    skills.skill_list = [
        item
        for item in skills.skill_list
        if item.path.expanduser().resolve() != created_skill_path
    ]
    skills.skill_list.append(created_skill)
    skills.paths = skill_paths_from_skills(skills.skill_list)
    REGISTRY.saveskills()

    return skill_dir
