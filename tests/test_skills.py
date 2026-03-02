"""Tests for skill discovery and rendering behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from magicskills.core.skill import Skill
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


def test_discover_skills_allows_same_name_with_different_base_dir(tmp_path: Path) -> None:
    root_a = tmp_path / "skills_a"
    root_b = tmp_path / "skills_b"
    (root_a / "same").mkdir(parents=True, exist_ok=True)
    (root_b / "same").mkdir(parents=True, exist_ok=True)
    (root_a / "same" / "SKILL.md").write_text("---\ndescription: same-a\n---\n", encoding="utf-8")
    (root_b / "same" / "SKILL.md").write_text("---\ndescription: same-b\n---\n", encoding="utf-8")

    skills = discover_skills([root_a, root_b])
    assert len(skills) == 2
    assert skills[0].name == "same"
    assert skills[1].name == "same"


def test_listskill_format() -> None:
    fixtures = Path(__file__).parent / "fixtures" / "skills"
    skills = Skills(paths=[fixtures])
    output = skills.listskill()
    assert "name: demo" in output
    assert "description: Demo skill" in output
    assert "path:" in output


def test_readskill_output() -> None:
    fixtures = Path(__file__).parent / "fixtures" / "skills"
    skills = Skills(paths=[fixtures])
    output = skills.readskill(fixtures / "demo" / "SKILL.md")
    assert "description: Demo skill for tests" in output
    assert "# Demo Skill" in output


def test_showskill_output_is_beautified() -> None:
    fixtures = Path(__file__).parent / "fixtures" / "skills"
    skills = Skills(paths=[fixtures])
    output = skills.showskill("demo")
    assert "Skill: demo" in output
    assert "Description: Demo skill" in output
    assert "Files (" in output
    assert "[1/" in output
    assert "SKILL.md" in output


def test_legacy_import_path_still_available() -> None:
    from magicskills.skills import Skills as LegacySkills

    assert LegacySkills is Skills


def test_add_remove_skill_uses_base_dir_for_identity(tmp_path: Path) -> None:
    base_a = tmp_path / "same_a"
    base_b = tmp_path / "same_b"
    base_a.mkdir(parents=True, exist_ok=True)
    base_b.mkdir(parents=True, exist_ok=True)
    (base_a / "SKILL.md").write_text("---\ndescription: same\n---\n", encoding="utf-8")
    (base_b / "SKILL.md").write_text("---\ndescription: same\n---\n", encoding="utf-8")

    skill_a = Skill(
        name="same",
        description="same",
        path=base_a / "SKILL.md",
        base_dir=base_a,
        source=base_a.parent,
    )
    skill_b = Skill(
        name="same",
        description="same",
        path=base_b / "SKILL.md",
        base_dir=base_b,
        source=base_b.parent,
    )

    skills = Skills(skills=[skill_a], paths=[])
    skills.add_skill(skill_b)
    assert len(skills.skills) == 2

    with pytest.raises(ValueError, match="Multiple skills named 'same'"):
        skills.remove_skill(name="same")

    skills.remove_skill(name="same", base_dir=base_a)
    assert len(skills.skills) == 1
    assert skills.skills[0].base_dir == base_b


def test_execskill_includes_all_collection_skill_environments(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "skills"
    a = root / "alpha"
    b = root / "beta"
    a.mkdir(parents=True, exist_ok=True)
    b.mkdir(parents=True, exist_ok=True)
    (a / "SKILL.md").write_text(
        "---\n"
        "description: alpha\n"
        "environment:\n"
        "  ALPHA_KEY: alpha\n"
        "---\n",
        encoding="utf-8",
    )
    (b / "SKILL.md").write_text(
        "---\n"
        "description: beta\n"
        "environment:\n"
        "  BETA_KEY: beta\n"
        "---\n",
        encoding="utf-8",
    )

    captured: dict[str, str] = {}

    class _Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    def _fake_run(*_args, **kwargs):  # noqa: ANN002, ANN003
        env = kwargs.get("env")
        if isinstance(env, dict):
            captured.update(env)
        return _Completed()

    monkeypatch.setattr("magicskills.core.skills.subprocess.run", _fake_run)

    skills = Skills(paths=[root])
    result = skills.execskill("echo ok")

    assert result.returncode == 0
    assert captured.get("ALPHA_KEY") == "alpha"
    assert captured.get("BETA_KEY") == "beta"


def test_execskill_allows_call_env_to_override_collection_env(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "skills"
    a = root / "alpha"
    b = root / "beta"
    a.mkdir(parents=True, exist_ok=True)
    b.mkdir(parents=True, exist_ok=True)
    (a / "SKILL.md").write_text(
        "---\n"
        "description: alpha\n"
        "environment:\n"
        "  SHARED_KEY: from-alpha\n"
        "---\n",
        encoding="utf-8",
    )
    (b / "SKILL.md").write_text(
        "---\n"
        "description: beta\n"
        "environment:\n"
        "  SHARED_KEY: from-beta\n"
        "---\n",
        encoding="utf-8",
    )

    captured: dict[str, str] = {}

    class _Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    def _fake_run(*_args, **kwargs):  # noqa: ANN002, ANN003
        env = kwargs.get("env")
        if isinstance(env, dict):
            captured.update(env)
        return _Completed()

    monkeypatch.setattr("magicskills.core.skills.subprocess.run", _fake_run)

    skills = Skills(paths=[root])
    result = skills.execskill("echo ok", env={"SHARED_KEY": "from-call"})

    assert result.returncode == 0
    assert captured.get("SHARED_KEY") == "from-call"
