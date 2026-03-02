"""Tests for CLI command parsing and registry persistence."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from magicskills import cli as cli_module
from magicskills.cli import (
    build_parser,
    cmd_add_skill_to_instance,
    cmd_delete_skill,
    cmd_list_skills_instances,
    cmd_read,
    cmd_upload_skill,
)
from magicskills.core.registry import SkillsRegistry


def test_cli_has_collection_commands() -> None:
    parser = build_parser()
    args = parser.parse_args(["createskills", "demo", "--paths", "tests/fixtures/skills"])
    assert args.command == "createskills"
    assert args.name == "demo"


def test_registry_persists_instances(tmp_path: Path) -> None:
    store_path = tmp_path / "collections.json"
    fixture_paths = [str(Path(__file__).parent / "fixtures" / "skills")]

    registry = SkillsRegistry(store_path=store_path)
    created = registry.create(name="demo", paths=fixture_paths)
    assert created.name == "demo"

    reloaded = SkillsRegistry(store_path=store_path)
    assert "demo" in reloaded.list()


def test_cli_install_accepts_skill_name_as_source() -> None:
    parser = build_parser()
    args = parser.parse_args(["install", "demo"])
    assert args.command == "install"
    assert args.source == "demo"


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
    assert args_by_name.name == "demo"
    assert args_by_name.path is None

    args_by_path = parser.parse_args(["deleteskill", "--path", "./skills/demo"])
    assert args_by_path.command == "deleteskill"
    assert args_by_path.name is None
    assert args_by_path.path == "./skills/demo"

    args_both = parser.parse_args(["deleteskill", "demo", "--path", "./skills/demo"])
    assert args_both.command == "deleteskill"
    assert args_both.name == "demo"
    assert args_both.path == "./skills/demo"


def test_cli_showskill_accepts_optional_path() -> None:
    parser = build_parser()
    args = parser.parse_args(["showskill", "demo", "--path", "./skills/demo"])
    assert args.command == "showskill"
    assert args.name == "demo"
    assert args.path == "./skills/demo"


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


def test_cmd_addskill2skills_uses_allskills_resolution(tmp_path: Path, monkeypatch) -> None:
    class _SkillRef:
        def __init__(self) -> None:
            self.name = "demo"
            self.base_dir = tmp_path / "skills" / "demo"

    class _Instance:
        def __init__(self) -> None:
            self.paths: list[Path] = []
            self._remove_called = False
            self._add_called = False

        def remove_skill(self, name: str | None = None, base_dir: Path | str | None = None) -> None:
            _ = (name, base_dir)
            self._remove_called = True
            raise KeyError("not found")

        def add_skill(self, _skill: object) -> None:
            self._add_called = True

    class _FakeRegistry:
        def __init__(self) -> None:
            self.instance = _Instance()
            self.saved = False

        def get(self, name: str):
            assert name == "team-a"
            return self.instance

        def save_instance(self, name: str) -> None:
            assert name == "team-a"
            self.saved = True

    class _FakeAllSkills:
        def __init__(self) -> None:
            self.calls: list[tuple[str, Path | None]] = []

        def get_skill(self, name: str, base_dir: Path | None = None):
            self.calls.append((name, base_dir))
            return _SkillRef()

    fake_registry = _FakeRegistry()
    fake_allskills = _FakeAllSkills()
    monkeypatch.setattr(cli_module, "REGISTRY", fake_registry)
    monkeypatch.setattr(cli_module, "ALL_SKILLS", fake_allskills)

    exit_code = cmd_add_skill_to_instance(
        argparse.Namespace(name="team-a", skill_name="demo", path="./skills/demo")
    )
    assert exit_code == 0
    assert fake_allskills.calls == [("demo", Path("./skills/demo").expanduser())]
    assert fake_registry.saved is True


def test_cmd_addskill2skills_requires_path_when_name_duplicated(monkeypatch) -> None:
    class _FakeRegistry:
        def get(self, _name: str):
            return object()

    class _FakeAllSkills:
        def get_skill(self, name: str, base_dir: Path | None = None):
            _ = (name, base_dir)
            raise KeyError("Multiple skills named 'demo' found. Provide base_dir. Candidates: a, b")

    monkeypatch.setattr(cli_module, "REGISTRY", _FakeRegistry())
    monkeypatch.setattr(cli_module, "ALL_SKILLS", _FakeAllSkills())

    with pytest.raises(SystemExit, match="please add --path"):
        cmd_add_skill_to_instance(argparse.Namespace(name="team-a", skill_name="demo", path=None))


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
        def get_skill(self, name: str, base_dir: Path | None = None):
            _ = (name, base_dir)
            raise KeyError("Multiple skills named 'dup' found. Provide base_dir. Candidates: a, b")

    monkeypatch.setattr(cli_module, "ALL_SKILLS", _FakeAllSkills())

    with pytest.raises(SystemExit, match="please add --path"):
        cmd_delete_skill(argparse.Namespace(name="dup", path=None))
