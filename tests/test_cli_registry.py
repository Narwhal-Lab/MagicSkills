"""Tests for CLI command parsing and registry persistence."""

from __future__ import annotations

from pathlib import Path

from magicskills.cli import build_parser
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
    args = parser.parse_args(["uploadskill", "demo", "--no-push", "--json"])
    assert args.command == "uploadskill"
    assert args.source == "demo"
    assert args.no_push is True
    assert args.json is True
