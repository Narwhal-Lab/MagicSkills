"""Tests for installer behavior."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from magicskills.core import installer as installer_module
from magicskills.core.installer import create_skill, delete_skill, install, upload_skill


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
    installed = install(str(repo_root), skill_name="beta", yes=True)

    assert len(installed) == 1
    assert installed[0].name == "beta"
    assert (tmp_path / ".claude" / "skills" / "beta" / "SKILL.md").exists()
    assert not (tmp_path / ".claude" / "skills" / "alpha").exists()


def test_install_to_custom_target_path(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    _make_skill(source_root, "custom-demo")
    target_root = tmp_path / "target" / "skills"

    installed = install(str(source_root), yes=True, target_root=target_root)

    assert len(installed) == 1
    assert installed[0] == target_root / "custom-demo"
    assert (target_root / "custom-demo" / "SKILL.md").exists()


def test_install_rejects_target_with_scope_flags(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    _make_skill(source_root, "demo")

    with pytest.raises(ValueError, match="target_root cannot be used"):
        install(str(source_root), global_=True, target_root=tmp_path / "target")


def test_install_adds_installed_skill_base_dir_to_allskills(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "source"
    _make_skill(source_root, "demo")
    target_root = tmp_path / "custom" / "skills"

    class _FakeAllSkills:
        def __init__(self) -> None:
            self.paths: list[Path] = []
            self.skills_added: list[object] = []

        def remove_skill(
            self,
            name: str | None = None,
            path: Path | str | None = None,
            base_dir: Path | str | None = None,
        ) -> None:
            _ = (name, path, base_dir)
            raise KeyError("missing")

        def add_skill(self, skill: object) -> None:
            self.skills_added.append(skill)

    fake = _FakeAllSkills()
    monkeypatch.setattr(installer_module, "ALL_SKILLS", fake)

    install(str(source_root), yes=True, target_root=target_root)

    assert target_root in fake.paths
    assert len(fake.skills_added) == 1
    assert getattr(fake.skills_added[0], "name", None) == "demo"


def test_create_skill_adds_to_allskills(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "skills"

    class _FakeAllSkills:
        def __init__(self) -> None:
            self.paths: list[Path] = []
            self.skills_added: list[object] = []

        def remove_skill(
            self,
            name: str | None = None,
            path: Path | str | None = None,
            base_dir: Path | str | None = None,
        ) -> None:
            _ = (name, path, base_dir)
            raise KeyError("missing")

        def add_skill(self, skill: object) -> None:
            self.skills_added.append(skill)

    fake = _FakeAllSkills()
    monkeypatch.setattr(installer_module, "ALL_SKILLS", fake)

    created = create_skill("demo", target_root=root)

    assert created == root / "demo"
    assert (created / "SKILL.md").exists()
    assert root in fake.paths
    assert len(fake.skills_added) == 1
    assert getattr(fake.skills_added[0], "path", None) == created
    assert getattr(fake.skills_added[0], "base_dir", None) == root


def test_create_skill_rejects_non_skill_non_empty_directory(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    conflict_dir = root / "demo"
    conflict_dir.mkdir(parents=True, exist_ok=True)
    (conflict_dir / "random.txt").write_text("x", encoding="utf-8")

    with pytest.raises(FileExistsError, match="missing SKILL.md"):
        create_skill("demo", target_root=root)


def test_create_skill_existing_valid_skill_does_not_fill_scaffold(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "skills"
    skill_dir = root / "demo"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("---\ndescription: demo\n---\n", encoding="utf-8")

    class _FakeAllSkills:
        def __init__(self) -> None:
            self.paths: list[Path] = []
            self.skills_added: list[object] = []

        def remove_skill(
            self,
            name: str | None = None,
            path: Path | str | None = None,
            base_dir: Path | str | None = None,
        ) -> None:
            _ = (name, path, base_dir)
            raise KeyError("missing")

        def add_skill(self, skill: object) -> None:
            self.skills_added.append(skill)

    fake = _FakeAllSkills()
    monkeypatch.setattr(installer_module, "ALL_SKILLS", fake)

    created = create_skill("demo", target_root=root)

    assert created == skill_dir
    assert not (skill_dir / "references").exists()
    assert not (skill_dir / "scripts").exists()
    assert not (skill_dir / "assets").exists()
    assert root in fake.paths
    assert len(fake.skills_added) == 1


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

    result = upload_skill(source=str(local_skill), repo=str(remote_repo), branch="main", push=False, yes=True)

    assert result.skill_name == "gamma"
    assert result.committed is True
    assert result.pushed is False
    assert result.push_remote is None
    assert result.push_branch is None
    assert result.pr_url is None
    assert result.pr_created is False

    check_repo = tmp_path / "check"
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", "main", str(remote_repo), str(check_repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert not (check_repo / "skills_for_all_agent" / "skills" / "gamma" / "SKILL.md").exists()


def test_upload_skill_auto_resolves_fork_when_missing(tmp_path: Path, monkeypatch) -> None:
    local_skill = _make_skill(tmp_path / "local_skills", "gamma")

    upstream_repo = tmp_path / "upstream.git"
    subprocess.run(["git", "init", "--bare", str(upstream_repo)], check=True, capture_output=True, text=True)

    seed = tmp_path / "seed_upstream_auto"
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
    subprocess.run(["git", "remote", "add", "origin", str(upstream_repo)], cwd=seed, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=seed, check=True, capture_output=True, text=True)

    auto_fork_repo = tmp_path / "auto-fork.git"
    subprocess.run(
        ["git", "clone", "--bare", str(upstream_repo), str(auto_fork_repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    monkeypatch.setattr(installer_module, "_auto_fork_repo_url", lambda base_repo: str(auto_fork_repo))

    result = upload_skill(
        source=str(local_skill),
        repo=str(upstream_repo),
        branch="main",
        push=True,
        yes=True,
        push_branch="feat/upload-auto",
    )

    assert result.pushed is True
    assert result.push_remote == "fork"
    assert result.push_branch == "feat/upload-auto"


def test_upload_skill_rejects_create_pr_without_push(tmp_path: Path) -> None:
    local_skill = _make_skill(tmp_path / "local_skills", "gamma")
    with pytest.raises(ValueError, match="create_pr requires push=True"):
        upload_skill(
            source=str(local_skill),
            repo="owner/repo",
            push=False,
            yes=True,
            create_pr=True,
            fork_repo="fork/repo",
        )


def test_upload_skill_pushes_to_fork_remote(tmp_path: Path) -> None:
    local_skill = _make_skill(tmp_path / "local_skills", "delta")

    upstream_repo = tmp_path / "upstream.git"
    subprocess.run(["git", "init", "--bare", str(upstream_repo)], check=True, capture_output=True, text=True)

    seed = tmp_path / "seed_upstream"
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
    subprocess.run(["git", "remote", "add", "origin", str(upstream_repo)], cwd=seed, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=seed, check=True, capture_output=True, text=True)

    fork_repo = tmp_path / "fork.git"
    subprocess.run(["git", "clone", "--bare", str(upstream_repo), str(fork_repo)], check=True, capture_output=True, text=True)

    result = upload_skill(
        source=str(local_skill),
        repo=str(upstream_repo),
        branch="main",
        push=True,
        yes=True,
        fork_repo=str(fork_repo),
        push_branch="feat/upload-delta",
    )

    assert result.skill_name == "delta"
    assert result.committed is True
    assert result.pushed is True
    assert result.push_remote == "fork"
    assert result.push_branch == "feat/upload-delta"
    assert result.pr_url is None
    assert result.pr_created is False

    check_fork = tmp_path / "check_fork"
    subprocess.run(
        ["git", "clone", "--branch", "feat/upload-delta", str(fork_repo), str(check_fork)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert (check_fork / "skills_for_all_agent" / "skills" / "delta" / "SKILL.md").exists()

    check_upstream = tmp_path / "check_upstream"
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", "main", str(upstream_repo), str(check_upstream)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert not (check_upstream / "skills_for_all_agent" / "skills" / "delta" / "SKILL.md").exists()


def test_upload_skill_rejects_skill_md_file_path(tmp_path: Path) -> None:
    local_skill = _make_skill(tmp_path / "local_skills", "gamma")
    with pytest.raises(ValueError, match="does not accept SKILL.md"):
        upload_skill(source=str(local_skill / "SKILL.md"), repo="owner/repo", push=False)


def test_upload_skill_duplicate_name_requires_directory_path(tmp_path: Path, monkeypatch) -> None:
    first = _make_skill(tmp_path / "skills_a", "dup")
    second = _make_skill(tmp_path / "skills_b", "dup")

    class _SkillRef:
        def __init__(self, name: str, path: Path) -> None:
            self.name = name
            self.path = path
            self.base_dir = path.parent

    class _FakeAllSkills:
        def __init__(self) -> None:
            self.skills = [_SkillRef("dup", first), _SkillRef("dup", second)]
            self.paths: list[Path] = []

        def remove_skill(
            self,
            name: str | None = None,
            path: Path | str | None = None,
            base_dir: Path | str | None = None,
        ) -> None:
            _ = (name, path, base_dir)

        def add_skill(self, skill: object) -> None:
            _ = skill

    monkeypatch.setattr(installer_module, "ALL_SKILLS", _FakeAllSkills())

    with pytest.raises(ValueError, match="Please pass the skill directory path as source"):
        installer_module._resolve_skill_source("dup")


def test_upload_skill_prefers_allskills_name_lookup_before_bare_local_dir(tmp_path: Path, monkeypatch) -> None:
    local_bare = _make_skill(tmp_path, "demo")
    allskills_dir = _make_skill(tmp_path / "allskills", "demo")

    class _SkillRef:
        def __init__(self, name: str, path: Path) -> None:
            self.name = name
            self.path = path
            self.base_dir = path.parent

    class _FakeAllSkills:
        def __init__(self) -> None:
            self.skills = [_SkillRef("demo", allskills_dir)]
            self.paths: list[Path] = []

        def remove_skill(
            self,
            name: str | None = None,
            path: Path | str | None = None,
            base_dir: Path | str | None = None,
        ) -> None:
            _ = (name, path, base_dir)

        def add_skill(self, skill: object) -> None:
            _ = skill

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(installer_module, "ALL_SKILLS", _FakeAllSkills())

    resolved = installer_module._resolve_skill_source("demo")
    assert resolved == allskills_dir
    assert resolved != local_bare


def test_auto_fork_repo_url_falls_back_to_api_when_gh_missing(monkeypatch) -> None:
    def _fake_run(*_args, **_kwargs):  # noqa: ANN002, ANN003
        raise FileNotFoundError("gh")

    monkeypatch.setattr(installer_module.subprocess, "run", _fake_run)
    monkeypatch.setattr(installer_module, "_github_api_token", lambda: "token-1")
    monkeypatch.setattr(
        installer_module,
        "_auto_fork_repo_url_with_api",
        lambda base_repo, token: f"api-fork::{base_repo}::{token}",
    )

    result = installer_module._auto_fork_repo_url("owner/repo")
    assert result == "api-fork::owner/repo::token-1"


def test_auto_fork_repo_url_requires_gh_or_token(monkeypatch) -> None:
    def _fake_run(*_args, **_kwargs):  # noqa: ANN002, ANN003
        raise FileNotFoundError("gh")

    monkeypatch.setattr(installer_module.subprocess, "run", _fake_run)
    monkeypatch.setattr(installer_module, "_github_api_token", lambda: None)

    with pytest.raises(RuntimeError, match="GH_TOKEN/GITHUB_TOKEN"):
        installer_module._auto_fork_repo_url("owner/repo")


def test_auto_fork_repo_url_falls_back_to_api_when_gh_not_authenticated(monkeypatch) -> None:
    def _fake_run(*_args, **_kwargs):  # noqa: ANN002, ANN003
        raise subprocess.CalledProcessError(1, "gh", stderr="please run gh auth login")

    monkeypatch.setattr(installer_module.subprocess, "run", _fake_run)
    monkeypatch.setattr(installer_module, "_github_api_token", lambda: "token-auth")
    monkeypatch.setattr(
        installer_module,
        "_auto_fork_repo_url_with_api",
        lambda base_repo, token: f"api-fork-auth::{base_repo}::{token}",
    )

    result = installer_module._auto_fork_repo_url("owner/repo")
    assert result == "api-fork-auth::owner/repo::token-auth"


def test_create_pr_with_gh_falls_back_to_api_when_gh_missing(monkeypatch) -> None:
    def _fake_run(*_args, **_kwargs):  # noqa: ANN002, ANN003
        raise FileNotFoundError("gh")

    monkeypatch.setattr(installer_module.subprocess, "run", _fake_run)
    monkeypatch.setattr(installer_module, "_github_api_token", lambda: "token-2")
    monkeypatch.setattr(
        installer_module,
        "_create_pr_with_api",
        lambda **kwargs: f"api-pr::{kwargs['base_repo']}::{kwargs['fork_repo']}::{kwargs['token']}",
    )

    result = installer_module._create_pr_with_gh(
        base_repo="owner/repo",
        base_branch="main",
        fork_repo="fork/repo",
        fork_branch="feat/demo",
        title="title",
        body="body",
    )
    assert result == "api-pr::owner/repo::fork/repo::token-2"


def test_create_pr_with_gh_falls_back_to_api_when_gh_not_authenticated(monkeypatch) -> None:
    def _fake_run(*_args, **_kwargs):  # noqa: ANN002, ANN003
        raise subprocess.CalledProcessError(1, "gh", stderr="please run gh auth login")

    monkeypatch.setattr(installer_module.subprocess, "run", _fake_run)
    monkeypatch.setattr(installer_module, "_github_api_token", lambda: "token-pr-auth")
    monkeypatch.setattr(
        installer_module,
        "_create_pr_with_api",
        lambda **kwargs: f"api-pr-auth::{kwargs['base_repo']}::{kwargs['fork_repo']}::{kwargs['token']}",
    )

    result = installer_module._create_pr_with_gh(
        base_repo="owner/repo",
        base_branch="main",
        fork_repo="fork/repo",
        fork_branch="feat/demo",
        title="title",
        body="body",
    )
    assert result == "api-pr-auth::owner/repo::fork/repo::token-pr-auth"


def test_delete_skill_by_name_uses_allskills_and_removes_registry_path(tmp_path: Path, monkeypatch) -> None:
    target = _make_skill(tmp_path / "skills", "demo")

    class _SkillRef:
        def __init__(self, path: Path) -> None:
            self.path = path
            self.base_dir = path.parent

    class _FakeAllSkills:
        def __init__(self) -> None:
            self.paths: list[Path] = [target.parent]
            self.skills: list[object] = [_SkillRef(target)]
            self.remove_calls: list[tuple[str | None, Path | str | None, Path | str | None]] = []

        def remove_skill(
            self,
            name: str | None = None,
            path: Path | str | None = None,
            base_dir: Path | str | None = None,
        ) -> None:
            self.remove_calls.append((name, path, base_dir))
            self.skills = []

        def add_skill(self, skill: object) -> None:
            _ = skill

    fake = _FakeAllSkills()
    monkeypatch.setattr(installer_module, "ALL_SKILLS", fake)

    deleted = delete_skill("demo")

    assert deleted == target.resolve()
    assert not target.exists()
    assert fake.remove_calls == [("demo", target.resolve(), None)]
    assert fake.paths == []


def test_delete_skill_by_path_without_name(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "skills" / "to-delete"
    target.mkdir(parents=True, exist_ok=True)
    (target / "x.txt").write_text("x", encoding="utf-8")

    class _FakeAllSkills:
        def __init__(self) -> None:
            self.paths: list[Path] = [target.parent]
            self.skills: list[object] = []
            self.remove_calls: list[tuple[str | None, Path | str | None, Path | str | None]] = []

        def remove_skill(
            self,
            name: str | None = None,
            path: Path | str | None = None,
            base_dir: Path | str | None = None,
        ) -> None:
            self.remove_calls.append((name, path, base_dir))

    fake = _FakeAllSkills()
    monkeypatch.setattr(installer_module, "ALL_SKILLS", fake)

    deleted = delete_skill(None, paths=[target])

    assert deleted == target.resolve()
    assert not target.exists()
    assert fake.remove_calls == [(None, target.resolve(), None)]
    assert fake.paths == []


def test_delete_skill_by_name_and_path_validates_match(tmp_path: Path, monkeypatch) -> None:
    target = _make_skill(tmp_path / "skills", "demo")

    class _SkillRef:
        def __init__(self, name: str, path: Path) -> None:
            self.name = name
            self.path = path
            self.base_dir = path.parent

    class _FakeAllSkills:
        def __init__(self) -> None:
            self.paths: list[Path] = [target.parent]
            self.skills = [_SkillRef("demo", target)]
            self.remove_calls: list[tuple[str | None, Path | str | None, Path | str | None]] = []

        def remove_skill(
            self,
            name: str | None = None,
            path: Path | str | None = None,
            base_dir: Path | str | None = None,
        ) -> None:
            self.remove_calls.append((name, path, base_dir))
            self.skills = []

    fake = _FakeAllSkills()
    monkeypatch.setattr(installer_module, "ALL_SKILLS", fake)

    deleted = delete_skill("demo", paths=[target])

    assert deleted == target.resolve()
    assert not target.exists()
    assert fake.remove_calls == [("demo", target.resolve(), None)]
    assert fake.paths == []


def test_delete_skill_by_name_and_path_rejects_mismatch(tmp_path: Path, monkeypatch) -> None:
    target = _make_skill(tmp_path / "skills", "demo")

    class _SkillRef:
        def __init__(self, name: str, path: Path) -> None:
            self.name = name
            self.path = path
            self.base_dir = path.parent

    class _FakeAllSkills:
        def __init__(self) -> None:
            self.paths: list[Path] = [target.parent]
            self.skills = [_SkillRef("other", target)]

    fake = _FakeAllSkills()
    monkeypatch.setattr(installer_module, "ALL_SKILLS", fake)

    with pytest.raises(ValueError, match="Path/name mismatch"):
        delete_skill("demo", paths=[target])
    assert target.exists()
