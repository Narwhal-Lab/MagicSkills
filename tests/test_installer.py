"""Tests for installer behavior."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from magicskills.core.installer import install_skills, upload_skill


def _make_skill(root: Path, name: str) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(f"---\ndescription: {name}\n---\n", encoding="utf-8")
    return skill_dir


def test_install_specific_skill_from_nested_source(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    nested_skills = repo_root / "skills_for_all_agent" / "skills"
    _make_skill(nested_skills, "alpha")
    _make_skill(nested_skills, "beta")

    monkeypatch.chdir(tmp_path)
    installed = install_skills(str(repo_root), skill_name="beta", yes=True)

    assert len(installed) == 1
    assert installed[0].name == "beta"
    assert (tmp_path / ".claude" / "skills" / "beta" / "SKILL.md").exists()
    assert not (tmp_path / ".claude" / "skills" / "alpha").exists()


def test_install_to_custom_target_path(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    _make_skill(source_root, "custom-demo")
    target_root = tmp_path / "target" / "skills"

    installed = install_skills(str(source_root), yes=True, target_root=target_root)

    assert len(installed) == 1
    assert installed[0] == target_root / "custom-demo"
    assert (target_root / "custom-demo" / "SKILL.md").exists()


def test_install_rejects_target_with_scope_flags(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    _make_skill(source_root, "demo")

    with pytest.raises(ValueError, match="target_root cannot be used"):
        install_skills(str(source_root), global_=True, target_root=tmp_path / "target")


def test_upload_skill_to_repo_subdir(tmp_path: Path) -> None:
    local_skill = _make_skill(tmp_path / "local_skills", "gamma")

    remote_repo = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote_repo)], check=True, capture_output=True, text=True)

    seed = tmp_path / "seed"
    seed.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=seed, check=True, capture_output=True, text=True)
    (seed / "skills_for_all_agent" / "skills").mkdir(parents=True, exist_ok=True)
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=seed, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "seed"],
        cwd=seed,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "remote", "add", "origin", str(remote_repo)], cwd=seed, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=seed, check=True, capture_output=True, text=True)

    result = upload_skill(source=str(local_skill), repo=str(remote_repo), branch="main", push=True, yes=True)

    assert result.skill_name == "gamma"
    assert result.committed is True
    assert result.pushed is True

    check_repo = tmp_path / "check"
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", "main", str(remote_repo), str(check_repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert (check_repo / "skills_for_all_agent" / "skills" / "gamma" / "SKILL.md").exists()


def test_upload_skill_rejects_skill_md_file_path(tmp_path: Path) -> None:
    local_skill = _make_skill(tmp_path / "local_skills", "gamma")
    with pytest.raises(ValueError, match="does not accept SKILL.md"):
        upload_skill(source=str(local_skill / "SKILL.md"), repo="owner/repo", push=False)
