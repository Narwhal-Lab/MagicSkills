"""Command implementation for listing skills."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..type.skill import Skill

if TYPE_CHECKING:
    from ..type.skills import Skills


def _format_skill_list(skills: list[Skill]) -> str:
    """Format skills for list output."""
    if not skills:
        return "No skills found."
    ordered = sorted(skills, key=lambda s: (s.name.lower(), s.path.as_posix()))
    lines: list[str] = []
    for index, skill in enumerate(ordered, start=1):
        lines.append(f"{index}. name: {skill.name}")
        lines.append(f"   description: {skill.description}")
        lines.append(f"   path: {skill.path / 'SKILL.md'}")
    return "\n".join(lines)


def listskill(skills: Skills) -> str:
    """Render available skills as simple text list."""
    return _format_skill_list(skills.skill_list)

