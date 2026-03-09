"""Tests for skill discovery and rendering behavior."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import magicskills.command.uploadskill as uploadskill_module
import magicskills.type.skillsregistry as skillsregistry_module

from magicskills.command.change_tool_description import change_tool_description as command_change_tool_description
from magicskills.command.createskill import createskill as command_createskill
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


def test_uploadskill_clones_existing_fork_when_fork_already_exists(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "skills"
    skill_dir = root / "demo"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("---\ndescription: demo\n---\n", encoding="utf-8")

    session_dir = tmp_path / "session"
    session_dir.mkdir(parents=True, exist_ok=True)
    workdir = session_dir / "MagicSkills"
    branch_name = "fix/upload-demo"
    calls: list[list[str]] = []

    class _TempDir:
        def __enter__(self) -> str:
            return str(session_dir)

        def __exit__(self, exc_type, exc, tb) -> bool:  # noqa: ANN001, ANN201
            return False

    def _fake_run(
        args: list[str],
        check: bool = False,
        capture_output: bool = False,
        text: bool = False,
        cwd: Path | str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del capture_output, text, cwd
        calls.append(list(args))
        command = list(args)

        if command == ["gh", "api", "user"]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout='{"login":"demo-user","html_url":"https://github.com/demo-user"}',
                stderr="",
            )
        if command == ["gh", "repo", "view", "Narwhal-Lab/MagicSkills", "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"]:
            return subprocess.CompletedProcess(command, 0, stdout="main\n", stderr="")
        if command == ["gh", "repo", "fork", "Narwhal-Lab/MagicSkills", "--remote=false"]:
            return subprocess.CompletedProcess(
                command,
                1,
                stdout="",
                stderr="GraphQL: name already exists on this account",
            )
        if command == ["git", "clone", "https://github.com/demo-user/MagicSkills.git", str(workdir)]:
            workdir.mkdir(parents=True, exist_ok=True)
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command[:3] == ["git", "-C", str(workdir)] and command[3:] in (
            ["remote", "add", "upstream", "https://github.com/Narwhal-Lab/MagicSkills.git"],
            ["fetch", "upstream"],
            ["checkout", "main"],
            ["pull", "--rebase", "upstream", "main"],
            ["checkout", "-b", branch_name],
            ["status"],
            ["add", "-A"],
            ["push", "-u", "origin", branch_name],
        ):
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command[:3] == ["git", "-C", str(workdir)] and command[3:] == ["status", "--porcelain"]:
            return subprocess.CompletedProcess(command, 0, stdout="A  skills/demo/SKILL.md\n", stderr="")
        if command[:3] == ["git", "-C", str(workdir)] and command[3:7] == [
            "-c",
            "user.name=demo-user",
            "-c",
            "user.url=https://github.com/demo-user",
        ]:
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command[:3] == ["gh", "pr", "create"]:
            return subprocess.CompletedProcess(command, 0, stdout="https://example.com/pr/1\n", stderr="")
        if check:
            raise subprocess.CalledProcessError(1, command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(uploadskill_module, "_ensure_gh_auth_status", lambda: None)
    monkeypatch.setattr(uploadskill_module, "_default_push_branch", lambda _name: branch_name)
    monkeypatch.setattr(uploadskill_module.tempfile, "TemporaryDirectory", lambda: _TempDir())
    monkeypatch.setattr(uploadskill_module.subprocess, "run", _fake_run)

    result = uploadskill_module.uploadskill(skill_dir)

    assert result.skill_name == "demo"
    assert result.repo == "https://github.com/Narwhal-Lab/MagicSkills.git"
    assert result.push_remote == "origin"
    assert result.push_branch == branch_name
    assert result.pr_url == "https://example.com/pr/1"
    assert ["gh", "repo", "fork", "Narwhal-Lab/MagicSkills", "--remote=false"] in calls
    assert ["git", "clone", "https://github.com/demo-user/MagicSkills.git", str(workdir)] in calls


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


def test_createskill_persists_registry(tmp_path: Path, monkeypatch) -> None:
    skill_dir = tmp_path / "skills" / "demo"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("---\ndescription: demo\n---\n", encoding="utf-8")

    class _FakeRegistry:
        def __init__(self) -> None:
            self.saved = 0

        def saveskills(self):
            self.saved += 1
            return Path("/tmp/collections.json")

    fake_registry = _FakeRegistry()
    skills = Skills(name="Allskills")
    monkeypatch.setattr("magicskills.type.skillsregistry.REGISTRY", fake_registry)
    monkeypatch.setattr("magicskills.type.skillsregistry.ALL_SKILLS", lambda: skills)

    created = command_createskill(skills, skill_dir)

    assert created == skill_dir
    assert fake_registry.saved == 1
    assert len(skills.skills) == 1
    assert skills.skills[0].name == "demo"


def test_all_skills_function_reads_current_registry(monkeypatch, tmp_path: Path) -> None:
    registry = skillsregistry_module.SkillsRegistry(store_path=tmp_path / "collections.json")
    monkeypatch.setattr(skillsregistry_module, "REGISTRY", registry)

    before = skillsregistry_module.ALL_SKILLS()
    registry.loadskills(tmp_path / "missing.json")
    after = skillsregistry_module.ALL_SKILLS()

    assert before is not after
    assert after is registry.get_skills("Allskills")


def test_change_tool_description_persists_registry(monkeypatch) -> None:
    class _FakeRegistry:
        def __init__(self) -> None:
            self.saved = 0

        def saveskills(self):
            self.saved += 1
            return Path("/tmp/collections.json")

    fake_registry = _FakeRegistry()
    skills = Skills(name="demo")
    monkeypatch.setattr("magicskills.type.skillsregistry.REGISTRY", fake_registry)

    command_change_tool_description(skills, "updated description")

    assert skills.tool_description == "updated description"
    assert fake_registry.saved == 1


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


def test_execskill_rejects_env_argument(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    root.mkdir(parents=True, exist_ok=True)
    skills = Skills(paths=[root])

    with pytest.raises(TypeError):
        skills.execskill("echo ok", env={"SHARED_KEY": "from-call"})  # type: ignore[call-arg]
