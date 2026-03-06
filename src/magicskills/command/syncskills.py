"""Command implementation for syncing skills into AGENTS.md."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..utils.agents_md import generate_skills_xml, replace_skills_section
from ..utils.utils import read_text

if TYPE_CHECKING:
    from ..type.skills import Skills


def _absolute_path(value: Path | str) -> Path:
    """Normalize a path-like value to absolute path."""
    return Path(value).expanduser().resolve()


def syncskills(skills: Skills, output_path: Path | str | None = None) -> Path:
    """Sync current skills collection into AGENTS.md content."""
    path = _absolute_path(output_path) if output_path else skills.agent_md_path
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# AGENTS\n", encoding="utf-8")
    content = read_text(path)
    new_section = generate_skills_xml(skills.skill_list, invocation=skills.tool_description)
    updated = replace_skills_section(content, new_section)
    path.write_text(updated, encoding="utf-8")
    return path
