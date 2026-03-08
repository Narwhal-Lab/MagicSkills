"""Tests for CLI command parsing and registry persistence."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from magicskills import cli as cli_module
from magicskills.cli import (
    build_parser,
    cmd_create_skills,
    cmd_create_skill_template,
    cmd_delete_skill,
    cmd_list_skills_instances,
    cmd_load_skills,
    cmd_read,
    cmd_save_skills,
    cmd_upload_skill,
)
from magicskills.type.skillsregistry import SkillsRegistry
from magicskills.type.skill import Skill
from magicskills.type.skills import Skills


def test_cli_has_collection_commands() -> None:
    parser = build_parser()
    args = parser.parse_args(["createskills", "demo", "--paths", "tests/fixtures/skills"])
    assert args.command == "createskills"
    assert args.name == "demo"


def test_cli_createskills_accepts_skill_list() -> None:
    parser = build_parser()
    args = parser.parse_args(["createskills", "demo", "--skill-list", "alpha", "beta"])
    assert args.command == "createskills"
    assert args.name == "demo"
    assert args.skill_list == ["alpha", "beta"]


def test_cli_saveskills_accepts_optional_path() -> None:
    parser = build_parser()
    args = parser.parse_args(["saveskills", "./collections.json"])

    assert args.command == "saveskills"
    assert args.path == "./collections.json"
    assert args.func is cmd_save_skills


def test_cli_loadskills_accepts_optional_path_and_json() -> None:
    parser = build_parser()
    args = parser.parse_args(["loadskills", "./collections.json", "--json"])

    assert args.command == "loadskills"
    assert args.path == "./collections.json"
    assert args.json is True
    assert args.func is cmd_load_skills


def test_registry_persists_instances(tmp_path: Path) -> None:
    store_path = tmp_path / "collections.json"
    fixture_paths = [str(Path(__file__).parent / "fixtures" / "skills")]

    registry = SkillsRegistry(store_path=store_path)
    created = registry.createskills(name="demo", paths=fixture_paths)
    assert created.name == "demo"

    reloaded = SkillsRegistry(store_path=store_path)
    assert "demo" in [item.name for item in reloaded.listskills()]


def test_registry_create_normalizes_parent_path_to_skill_directories(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    skill_dir = root / "demo"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("---\ndescription: demo\n---\n", encoding="utf-8")

    registry = SkillsRegistry(store_path=tmp_path / "collections.json")
    created = registry.createskills(name="team-a", paths=[str(root)])

    assert [path.resolve() for path in created.paths] == [skill_dir.resolve()]


def test_registry_create_without_paths_uses_allskills_skill_directories(tmp_path: Path) -> None:
    registry = SkillsRegistry(store_path=tmp_path / "collections.json")

    alpha_dir = tmp_path / "alpha"
    beta_dir = tmp_path / "beta"
    seed_skill_alpha = Skill(
        name="alpha",
        description="alpha",
        path=alpha_dir,
        base_dir=alpha_dir.parent,
        source=str(alpha_dir.parent),
    )
    seed_skill_beta = Skill(
        name="beta",
        description="beta",
        path=beta_dir,
        base_dir=beta_dir.parent,
        source=str(beta_dir.parent),
    )
    registry._instances["Allskills"] = Skills(
        name="Allskills",
        skill_list=[seed_skill_alpha, seed_skill_beta],
        paths=[alpha_dir.parent],
    )

    created = registry.createskills(name="team-b")

    assert [path.resolve() for path in created.paths] == [alpha_dir.resolve(), beta_dir.resolve()]


def test_registry_always_contains_allskills(tmp_path: Path) -> None:
    registry = SkillsRegistry(store_path=tmp_path / "collections.json")
    assert "Allskills" in [item.name for item in registry.listskills()]


def test_registry_disallows_deleting_allskills(tmp_path: Path) -> None:
    registry = SkillsRegistry(store_path=tmp_path / "collections.json")
    with pytest.raises(ValueError, match="built-in"):
        registry.deleteskills("Allskills")


def test_cli_install_accepts_skill_name_as_source() -> None:
    parser = build_parser()
    args = parser.parse_args(["install", "demo"])
    assert args.command == "install"
    assert args.source == "demo"


def test_cli_createskill_template_parsing() -> None:
    parser = build_parser()
    args = parser.parse_args(["createskill_template", "demo", "./skills"])

    assert args.command == "createskill_template"
    assert args.name == "demo"
    assert args.base_dir == "./skills"
    assert args.func is cmd_create_skill_template


def test_cmd_create_skills_resolves_skill_list(monkeypatch) -> None:
    alpha = Skill(
        name="alpha",
        description="alpha",
        path=Path("/tmp/alpha"),
        base_dir=Path("/tmp"),
        source="/tmp",
    )
    beta = Skill(
        name="beta",
        description="beta",
        path=Path("/tmp/beta"),
        base_dir=Path("/tmp"),
        source="/tmp",
    )

    class _FakeAllSkills:
        def __init__(self) -> None:
            self._items = {
                "alpha": alpha,
                "beta": beta,
            }

        def get_skill(self, target: str | Path):
            return self._items[str(target)]

    class _Created:
        name = "demo"
        skills = [alpha, beta]

    captured: dict[str, object] = {}

    def _fake_command_createskills(**kwargs):  # noqa: ANN003
        captured.update(kwargs)
        return _Created()

    monkeypatch.setattr(cli_module, "ALL_SKILLS", _FakeAllSkills())
    monkeypatch.setattr(cli_module, "command_createskills", _fake_command_createskills)

    exit_code = cmd_create_skills(
        argparse.Namespace(
            name="demo",
            skill_list=["alpha", "beta"],
            paths=None,
            tool_description=None,
            agent_md_path=None,
        )
    )

    assert exit_code == 0
    assert captured["skill_list"] == [alpha, beta]
    assert captured["paths"] is None


def test_cmd_create_skills_rejects_skill_list_with_paths() -> None:
    with pytest.raises(SystemExit, match="--paths cannot be used with --skill-list"):
        cmd_create_skills(
            argparse.Namespace(
                name="demo",
                skill_list=["alpha"],
                paths=["./skills"],
                tool_description=None,
                agent_md_path=None,
            )
        )


def test_cli_install_accepts_custom_target() -> None:
    parser = build_parser()
    args = parser.parse_args(["install", "demo", "--target", "./custom-skills"])
    assert args.command == "install"
    assert args.target == "./custom-skills"


def test_cli_uploadskill_parsing() -> None:
    parser = build_parser()
    args = parser.parse_args(["uploadskill", "demo"])
    assert args.command == "uploadskill"
    assert args.source == "demo"


def test_cli_readskill_accepts_file_path_argument() -> None:
    parser = build_parser()
    args = parser.parse_args(["readskill", "./AGENTS.md"])
    assert args.command == "readskill"
    assert args.path == "./AGENTS.md"


def test_cli_deleteskill_accepts_name_or_path() -> None:
    parser = build_parser()
    args_by_name = parser.parse_args(["deleteskill", "demo"])
    assert args_by_name.command == "deleteskill"
    assert args_by_name.target == "demo"

    args_by_path = parser.parse_args(["deleteskill", "./skills/demo"])
    assert args_by_path.command == "deleteskill"
    assert args_by_path.target == "./skills/demo"


def test_cli_showskill_accepts_name_or_path_target() -> None:
    parser = build_parser()
    args_by_name = parser.parse_args(["showskill", "demo"])
    assert args_by_name.command == "showskill"
    assert args_by_name.target == "demo"

    args_by_path = parser.parse_args(["showskill", "./skills/demo"])
    assert args_by_path.command == "showskill"
    assert args_by_path.target == "./skills/demo"


def test_cmd_read_reads_file_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file_path = tmp_path / "demo.txt"
    file_path.write_text("hello\nworld\n", encoding="utf-8")

    exit_code = cmd_read(argparse.Namespace(path=str(file_path)))
    assert exit_code == 0

    output = capsys.readouterr().out
    assert "Reading file:" in output
    assert str(file_path.resolve()) in output
    assert "hello" in output
    assert "world" in output


def test_cmd_read_accepts_skill_name_from_allskills(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch
) -> None:
    skill_dir = tmp_path / "skills" / "demo"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("demo-skill-content\n", encoding="utf-8")

    class _SkillRef:
        path = skill_dir

    class _FakeAllSkills:
        def get_skill(self, target: str | Path):
            if str(target) != "demo":
                raise KeyError(str(target))
            return _SkillRef()

    monkeypatch.setattr(cli_module, "ALL_SKILLS", _FakeAllSkills())

    exit_code = cmd_read(argparse.Namespace(path="demo"))
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Reading file:" in output
    assert "demo-skill-content" in output


def test_cmd_read_duplicate_skill_name_requires_path(monkeypatch) -> None:
    class _FakeAllSkills:
        def get_skill(self, target: str | Path):
            _ = target
            raise KeyError("Multiple skills named 'demo' found. Provide path. Candidates: a, b")

    monkeypatch.setattr(cli_module, "ALL_SKILLS", _FakeAllSkills())
    with pytest.raises(SystemExit, match="please pass file path"):
        cmd_read(argparse.Namespace(path="demo"))


def test_cmd_read_rejects_directory(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="expects a file path"):
        cmd_read(argparse.Namespace(path=str(tmp_path)))


def test_cmd_listskills_output_is_beautified(capsys: pytest.CaptureFixture[str], monkeypatch) -> None:
    class _Instance:
        def __init__(self, name: str, skills_count: int) -> None:
            self.name = name
            self.skills = [object()] * skills_count
            self.agent_md_path = Path(f"/tmp/{name}/AGENTS.md")
            self.paths = [Path(f"/tmp/{name}/skills")]
            self.tool_description = f"tool-{name}"

    class _FakeRegistry:
        def __init__(self) -> None:
            self._items = {
                "alpha": _Instance("alpha", 2),
                "beta": _Instance("beta", 1),
            }

        def list(self) -> list[str]:
            return ["alpha", "beta"]

        def get(self, name: str):
            return self._items[name]

    monkeypatch.setattr(cli_module, "REGISTRY", _FakeRegistry())

    exit_code = cmd_list_skills_instances(argparse.Namespace(json=False))
    assert exit_code == 0

    out = capsys.readouterr().out
    assert "MagicSkills Collections" in out
    assert "- name: alpha" in out
    assert "- name: beta" in out
    assert "Total collections: 2" in out
    assert "Total skills across collections: 3" in out


def test_boxed_lines_handles_multiline_rows() -> None:
    lines = cli_module._boxed_lines("Demo", ["alpha\nbeta gamma"], width=24, style="1;33", color=False)

    assert all("\n" not in line for line in lines)
    assert all(line.startswith(("+", "|")) for line in lines)
    assert any("alpha" in line for line in lines)
    assert any("beta gamma" in line for line in lines)


def test_default_tool_description_is_dedented() -> None:
    description_lines = Skills().tool_description.splitlines()

    assert description_lines[1].startswith("function of this tool")
    assert not description_lines[1].startswith("    function")


def test_cmd_uploadskill_reports_duplicate_name_path_hint(monkeypatch) -> None:
    def _fake_upload_skill(*_args, **_kwargs):  # noqa: ANN002, ANN003
        raise ValueError("Please pass the skill directory path as source")

    monkeypatch.setattr(cli_module, "upload_skill", _fake_upload_skill)

    with pytest.raises(SystemExit, match="Please pass the skill directory path as source"):
        cmd_upload_skill(argparse.Namespace(source="dup"))


def test_cmd_uploadskill_uses_default_fork_pr_flow(monkeypatch) -> None:
    class _Result:
        skill_name = "demo"
        repo = "repo"
        branch = "main"
        remote_subpath = "skills/demo"
        committed = True
        pushed = True
        push_remote = "fork"
        push_branch = "magicskills/demo-1"
        pr_url = "https://example.com/pr/1"
        pr_created = True

    captured: dict[str, object] = {}

    def _fake_upload_skill(*_args, **kwargs):  # noqa: ANN002, ANN003
        captured.update(kwargs)
        return _Result()

    monkeypatch.setattr(cli_module, "upload_skill", _fake_upload_skill)

    exit_code = cmd_upload_skill(argparse.Namespace(source="demo"))
    assert exit_code == 0
    assert captured.get("source") == "demo"
    assert captured.get("create_pr") is True


def test_cmd_uploadskill_retries_after_gh_install(monkeypatch) -> None:
    class _Result:
        skill_name = "demo"
        repo = "repo"
        branch = "main"
        remote_subpath = "skills/demo"
        committed = True
        pushed = True
        push_remote = "fork"
        push_branch = "magicskills/demo-1"
        pr_url = "https://example.com/pr/1"
        pr_created = True

    calls = {"count": 0}

    def _fake_upload_skill(*_args, **_kwargs):  # noqa: ANN002, ANN003
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("`gh` CLI not found. Install GitHub CLI first.")
        return _Result()

    monkeypatch.setattr(cli_module, "upload_skill", _fake_upload_skill)
    monkeypatch.setattr(cli_module, "_maybe_install_gh_for_upload", lambda: True)

    exit_code = cmd_upload_skill(argparse.Namespace(source="demo"))
    assert exit_code == 0
    assert calls["count"] == 2


def test_cmd_uploadskill_exits_when_gh_missing_and_not_installed(monkeypatch) -> None:
    def _fake_upload_skill(*_args, **_kwargs):  # noqa: ANN002, ANN003
        raise RuntimeError("`gh` CLI not found. Install GitHub CLI first.")

    monkeypatch.setattr(cli_module, "upload_skill", _fake_upload_skill)
    monkeypatch.setattr(cli_module, "_maybe_install_gh_for_upload", lambda: False)

    with pytest.raises(SystemExit, match="gh"):
        cmd_upload_skill(argparse.Namespace(source="demo"))


def test_cmd_uploadskill_retries_after_gh_auth_login(monkeypatch) -> None:
    class _Result:
        skill_name = "demo"
        repo = "repo"
        branch = "main"
        remote_subpath = "skills/demo"
        committed = True
        pushed = True
        push_remote = "fork"
        push_branch = "magicskills/demo-1"
        pr_url = "https://example.com/pr/1"
        pr_created = True

    calls = {"count": 0}

    def _fake_upload_skill(*_args, **_kwargs):  # noqa: ANN002, ANN003
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("failed to query GitHub user via gh: please run gh auth login")
        return _Result()

    monkeypatch.setattr(cli_module, "upload_skill", _fake_upload_skill)
    monkeypatch.setattr(cli_module, "_maybe_login_gh_for_upload", lambda: True)

    exit_code = cmd_upload_skill(argparse.Namespace(source="demo"))
    assert exit_code == 0
    assert calls["count"] == 2


def test_cmd_uploadskill_exits_when_gh_auth_not_completed(monkeypatch) -> None:
    def _fake_upload_skill(*_args, **_kwargs):  # noqa: ANN002, ANN003
        raise RuntimeError("failed to query GitHub user via gh: please run gh auth login")

    monkeypatch.setattr(cli_module, "upload_skill", _fake_upload_skill)
    monkeypatch.setattr(cli_module, "_maybe_login_gh_for_upload", lambda: False)

    with pytest.raises(SystemExit, match="gh auth login"):
        cmd_upload_skill(argparse.Namespace(source="demo"))


def test_cmd_deleteskill_requires_path_when_name_duplicated(monkeypatch) -> None:
    class _FakeAllSkills:
        def get_skill(self, target: str | Path):
            _ = target
            raise KeyError("Multiple skills named 'dup' found. Provide path. Candidates: a, b")

    monkeypatch.setattr(cli_module, "ALL_SKILLS", _FakeAllSkills())

    with pytest.raises(SystemExit, match="skill-directory-path"):
        cmd_delete_skill(argparse.Namespace(target="dup"))


def test_cmd_deleteskill_default_prunes_other_collections(monkeypatch, tmp_path: Path) -> None:
    deleted_path = (tmp_path / "skills" / "demo").resolve()
    other_skill_dir = (tmp_path / "skills" / "other").resolve()

    class _Skill:
        def __init__(self, path: Path) -> None:
            self.path = path
            self.base_dir = path.parent

    class _Collection:
        def __init__(self) -> None:
            self.paths = [deleted_path.parent]
            self.skills = [_Skill(other_skill_dir)]
            self.remove_calls: list[Path] = []

        def remove_skill(
            self,
            name: str | None = None,
            path: Path | str | None = None,
            base_dir: Path | str | None = None,
        ) -> None:
            _ = (name, base_dir)
            assert path is not None
            self.remove_calls.append(Path(path).resolve())

    class _FakeRegistry:
        def __init__(self) -> None:
            self.named = _Collection()
            self.saved: list[str] = []

        def list(self) -> list[str]:
            return ["Allskills", "team-a"]

        def get(self, name: str):
            if name == "Allskills":
                return cli_module.ALL_SKILLS
            if name == "team-a":
                return self.named
            raise KeyError(name)

        def save_instance(self, name: str) -> None:
            self.saved.append(name)

    def _fake_delete_skill(name: str | None, paths: list[Path] | None = None) -> Path:
        _ = (name, paths)
        return deleted_path

    fake_registry = _FakeRegistry()
    monkeypatch.setattr(cli_module, "REGISTRY", fake_registry)
    monkeypatch.setattr(cli_module, "delete_skill", _fake_delete_skill)

    exit_code = cmd_delete_skill(argparse.Namespace(target=str(deleted_path)))
    assert exit_code == 0
    assert fake_registry.named.remove_calls == [deleted_path]
    assert fake_registry.saved == ["team-a"]
