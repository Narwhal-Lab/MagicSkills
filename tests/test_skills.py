"""Tests for skill discovery and rendering behavior."""

from __future__ import annotations

from pathlib import Path

from magicskills.core.skills import Skills, discover_skills


def test_discover_skills_fixture() -> None:
    fixtures = Path(__file__).parent / "fixtures" / "skills"
    skills = discover_skills([fixtures])
    assert len(skills) == 1
    skill = skills[0]
    assert skill.name == "demo"
    assert "Demo skill" in skill.description
    assert skill.frontmatter["description"] == "Demo skill"


def test_discover_single_skill_directory_path() -> None:
    skill_dir = Path(__file__).parent / "fixtures" / "skills" / "demo"
    skills = discover_skills([skill_dir])
    assert len(skills) == 1
    assert skills[0].name == "demo"


def test_listskill_format() -> None:
    fixtures = Path(__file__).parent / "fixtures" / "skills"
    skills = Skills(paths=[fixtures])
    output = skills.listskill()
    assert "<available_skills>" in output
    assert "<name>demo</name>" in output


def test_readskill_output() -> None:
    fixtures = Path(__file__).parent / "fixtures" / "skills"
    skills = Skills(paths=[fixtures])
    output = skills.readskill("demo")
    assert "Reading: demo" in output
    assert "File: SKILL.md" in output
    assert "Skill read: demo" in output


def test_legacy_import_path_still_available() -> None:
    from magicskills.skills import Skills as LegacySkills

    assert LegacySkills is Skills
