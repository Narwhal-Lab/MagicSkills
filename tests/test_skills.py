"""Tests for skill discovery and rendering behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from magicskills.command.deleteskill import deleteskill as command_deleteskill
from magicskills.type.skill import Skill
from magicskills.type.skills import Skills
from magicskills.utils.utils import skill_paths_to_skills


def test_discover_skills_fixture() -> None:
    fixtures = Path(__file__).parent / "fixtures" / "skills"
    skills = skill_paths_to_skills([fixtures])
    assert len(skills) == 1
    skill = skills[0]
    assert skill.name == "demo"
    assert skill.path == fixtures / "demo"
    assert skill.base_dir == fixtures
    assert "Demo skill" in skill.description


def test_discover_single_skill_directory_path() -> None:
    skill_dir = Path(__file__).parent / "fixtures" / "skills" / "demo"
    skills = skill_paths_to_skills([skill_dir])
    assert len(skills) == 1
    assert skills[0].name == "demo"


def test_discover_skills_allows_same_name_with_different_base_dir(tmp_path: Path) -> None:
    root_a = tmp_path / "skills_a"
    root_b = tmp_path / "skills_b"
    (root_a / "same").mkdir(parents=True, exist_ok=True)
    (root_b / "same").mkdir(parents=True, exist_ok=True)
    (root_a / "same" / "SKILL.md").write_text("---\ndescription: same-a\n---\n", encoding="utf-8")
    (root_b / "same" / "SKILL.md").write_text("---\ndescription: same-b\n---\n", encoding="utf-8")

    skills = skill_paths_to_skills([root_a, root_b])
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


def test_readskill_accepts_skill_name() -> None:
    fixtures = Path(__file__).parent / "fixtures" / "skills"
    skills = Skills(paths=[fixtures])
    output = skills.readskill("demo")
    assert "description: Demo skill for tests" in output
    assert "# Demo Skill" in output


def test_readskill_duplicate_name_requires_path(tmp_path: Path) -> None:
    root_a = tmp_path / "skills_a"
    root_b = tmp_path / "skills_b"
    (root_a / "same").mkdir(parents=True, exist_ok=True)
    (root_b / "same").mkdir(parents=True, exist_ok=True)
    (root_a / "same" / "SKILL.md").write_text("---\ndescription: same-a\n---\n", encoding="utf-8")
    (root_b / "same" / "SKILL.md").write_text("---\ndescription: same-b\n---\n", encoding="utf-8")

    skills = Skills(paths=[root_a, root_b])
    with pytest.raises(ValueError, match="please pass an explicit file path"):
        skills.readskill("same")


def test_uploadskill_accepts_skill_name(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "skills"
    skill_dir = root / "demo"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("---\ndescription: demo\n---\n", encoding="utf-8")

    class _Result:
        skill_name = "demo"
        repo = "repo"
        branch = "main"
        remote_subpath = "skills/demo"
        committed = True
        pushed = True
        push_remote = "fork"
        push_branch = "branch"
        pr_url = "url"
        pr_created = True

    captured: dict[str, object] = {}

    def _fake_upload_skill_from_dir(*_args, **kwargs):  # noqa: ANN002, ANN003
        captured.update(kwargs)
        return _Result()

    monkeypatch.setattr("magicskills.command.uploadskill.upload_skill_from_dir", _fake_upload_skill_from_dir)

    skills = Skills(paths=[root])
    result = skills.uploadskill("demo")

    assert getattr(result, "skill_name", None) == "demo"
    assert captured.get("source_dir") == skill_dir.resolve()
    assert captured.get("create_pr") is True


def test_uploadskill_duplicate_name_requires_path(tmp_path: Path) -> None:
    root_a = tmp_path / "skills_a"
    root_b = tmp_path / "skills_b"
    (root_a / "same").mkdir(parents=True, exist_ok=True)
    (root_b / "same").mkdir(parents=True, exist_ok=True)
    (root_a / "same" / "SKILL.md").write_text("---\ndescription: same-a\n---\n", encoding="utf-8")
    (root_b / "same" / "SKILL.md").write_text("---\ndescription: same-b\n---\n", encoding="utf-8")

    skills = Skills(paths=[root_a, root_b])
    with pytest.raises(ValueError, match="duplicated"):
        skills.uploadskill("same")


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


def test_deleteskill_uses_path_for_identity(tmp_path: Path) -> None:
    base_a = tmp_path / "same_a"
    base_b = tmp_path / "same_b"
    base_a.mkdir(parents=True, exist_ok=True)
    base_b.mkdir(parents=True, exist_ok=True)
    (base_a / "SKILL.md").write_text("---\ndescription: same\n---\n", encoding="utf-8")
    (base_b / "SKILL.md").write_text("---\ndescription: same\n---\n", encoding="utf-8")

    skill_a = Skill(
        name="same",
        description="same",
        path=base_a,
        base_dir=base_a.parent,
        source=str(base_a.parent),
    )
    skill_b = Skill(
        name="same",
        description="same",
        path=base_b,
        base_dir=base_b.parent,
        source=str(base_b.parent),
    )

    skills = Skills(skill_list=[skill_a], paths=[])
    skill_b_path = skill_b.path.expanduser().resolve()
    if any(s.path.expanduser().resolve() == skill_b_path for s in skills.skill_list):
        raise ValueError(f"Skill at path '{skill_b.path}' already exists in this collection")
    skills.skill_list.append(skill_b)
    assert len(skills.skills) == 2

    with pytest.raises(ValueError, match="duplicated"):
        command_deleteskill(skills, "same")

    command_deleteskill(skills, str(base_a))
    assert len(skills.skills) == 1
    assert skills.skills[0].path == base_b


def test_execskill_does_not_include_collection_skill_environments(tmp_path: Path, monkeypatch) -> None:
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

    monkeypatch.setattr("magicskills.command.execskill.subprocess.run", _fake_run)

    skills = Skills(paths=[root])
    result = skills.execskill("echo ok")

    assert result.returncode == 0
    assert captured.get("ALPHA_KEY") is None
    assert captured.get("BETA_KEY") is None


def test_execskill_ignores_call_env_argument(tmp_path: Path, monkeypatch) -> None:
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

    monkeypatch.setattr("magicskills.command.execskill.subprocess.run", _fake_run)

    skills = Skills(paths=[root])
    result = skills.execskill("echo ok", env={"SHARED_KEY": "from-call"})

    assert result.returncode == 0
    assert captured.get("SHARED_KEY") is None
