"""Tests for AGENTS.md marker replacement helpers."""

from __future__ import annotations

from pathlib import Path

from magicskills.type.skill import Skill
from magicskills.utils.agents_md import generate_skills_xml, replace_skills_section


def test_replace_skills_section_marker_only_does_not_duplicate_markers() -> None:
    content = (
        "# AGENTS\n\n"
        "before\n\n"
        "<!-- SKILLS_TABLE_START -->\n"
        "old content\n"
        "<!-- SKILLS_TABLE_END -->\n\n"
        "after\n"
    )
    skill = Skill(
        name="demo",
        description="demo",
        path=Path("/tmp/demo"),
        base_dir=Path("/tmp"),
        source="/tmp",
    )
    new_section = generate_skills_xml([skill], invocation="")

    updated = replace_skills_section(content, new_section)

    assert updated.count("<!-- SKILLS_TABLE_START -->") == 1
    assert updated.count("<!-- SKILLS_TABLE_END -->") == 1
    assert "<skills_system priority=\"1\">" not in updated
    assert "<available_skills>" in updated


def test_replace_skills_section_appends_full_block_when_no_markers_exist() -> None:
    content = "# AGENTS\n"
    skill = Skill(
        name="demo",
        description="demo",
        path=Path("/tmp/demo"),
        base_dir=Path("/tmp"),
        source="/tmp",
    )
    new_section = generate_skills_xml([skill], invocation="")

    updated = replace_skills_section(content, new_section)

    assert "<skills_system priority=\"1\">" in updated
    assert updated.count("<!-- SKILLS_TABLE_START -->") == 1
    assert updated.count("<!-- SKILLS_TABLE_END -->") == 1
