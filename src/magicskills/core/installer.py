"""Filesystem-level skill installation and scaffold helpers."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .registry import ALL_SKILLS
from .skills import Skills
from .utils import get_search_dirs, is_directory_or_symlink_to_directory, is_git_url, is_repo_shorthand


IGNORE_PATTERNS = shutil.ignore_patterns(".git", "__pycache__", "*.pyc")
DEFAULT_SKILL_REPO = "https://github.com/Narwhal-Lab/Skills-For-All-Agent.git"
DEFAULT_SKILL_SUBDIR = Path("skills_for_all_agent") / "skills"


@dataclass(frozen=True)
class UploadResult:
    """Result metadata for one upload operation."""

    skill_name: str
    repo: str
    branch: str
    remote_subpath: str
    committed: bool
    pushed: bool


def resolve_install_root(global_: bool, universal: bool, cwd: Path | None = None) -> Path:
    """Resolve install directory based on scope and mode flags."""
    base = Path.home() if global_ else (cwd or Path.cwd())
    if universal:
        return base / ".agent" / "skills"
    return base / ".claude" / "skills"


def _looks_like_plain_skill_name(source: str) -> bool:
    """Detect inputs that are likely a skill name, not a repo/path."""
    if not source:
        return False
    if "/" in source or "\\" in source:
        return False
    if source.startswith("git@") or "://" in source or source.endswith(".git"):
        return False
    return True


def _resolve_repo_source_root(repo_root: Path) -> Path:
    """Resolve where skills live inside a cloned repository."""
    for candidate in (repo_root / DEFAULT_SKILL_SUBDIR, repo_root / "skills", repo_root):
        if candidate.exists():
            return candidate
    return repo_root


def _find_skill_dir(source_dir: Path, skill_name: str) -> Path:
    """Find one skill directory by name under source tree."""
    direct = source_dir / skill_name
    if is_directory_or_symlink_to_directory(direct) and (direct / "SKILL.md").exists():
        return direct

    matches: list[Path] = []
    for entry in source_dir.rglob("*"):
        if entry.name != skill_name:
            continue
        if is_directory_or_symlink_to_directory(entry) and (entry / "SKILL.md").exists():
            matches.append(entry)
    if not matches:
        raise FileNotFoundError(f"Skill '{skill_name}' not found under {source_dir}")
    matches.sort(key=lambda p: (len(p.parts), p.as_posix()))
    return matches[0]


def _collect_skill_dirs(source_dir: Path, skill_name: str | None = None) -> list[Path]:
    """Collect valid skill directories from one source directory."""
    if skill_name:
        return [_find_skill_dir(source_dir, skill_name)]
    if (source_dir / "SKILL.md").exists():
        return [source_dir]
    skills: list[Path] = []
    for entry in source_dir.iterdir():
        if is_directory_or_symlink_to_directory(entry) and (entry / "SKILL.md").exists():
            skills.append(entry)
    return skills


def _copy_skill_dir(skill_dir: Path, target_root: Path, yes: bool) -> Path:
    """Copy one skill directory into target root with overwrite policy."""
    target_root.mkdir(parents=True, exist_ok=True)
    target_path = target_root / skill_dir.name
    if target_path.exists():
        if not yes:
            raise FileExistsError(f"Skill '{skill_dir.name}' already exists at {target_path}")
        shutil.rmtree(target_path)
    shutil.copytree(skill_dir, target_path, ignore=IGNORE_PATTERNS)
    return target_path


def _resolve_skill_source(source: str) -> Path:
    """Resolve source from a skill directory path or a skill name in Allskills."""
    value = source.strip()
    if not value:
        raise ValueError("uploadskill requires a non-empty source")
    if value.lower().endswith("skill.md"):
        raise ValueError("uploadskill does not accept SKILL.md file path; pass skill directory or skill name")

    path_candidate = Path(value).expanduser()
    if path_candidate.exists():
        if not is_directory_or_symlink_to_directory(path_candidate):
            raise ValueError(f"uploadskill expects a skill directory path, got file: {path_candidate}")
        source_dir = path_candidate.resolve()
        if not (source_dir / "SKILL.md").exists():
            raise FileNotFoundError(f"Skill directory is missing SKILL.md: {source_dir}")
        return source_dir

    if "/" in value or "\\" in value or value.startswith(".") or value.startswith("~"):
        raise FileNotFoundError(f"Skill directory not found: {path_candidate}")

    ALL_SKILLS.paths = get_search_dirs()
    ALL_SKILLS.refresh()
    try:
        source_dir = ALL_SKILLS.get_skill(value).base_dir
    except KeyError as exc:
        raise FileNotFoundError(f"Skill '{value}' not found in Allskills") from exc
    if not source_dir.is_dir() or not (source_dir / "SKILL.md").exists():
        raise FileNotFoundError(f"Skill '{value}' is invalid: missing SKILL.md under {source_dir}")
    return source_dir


def upload_skill(
    source: str,
    repo: str = DEFAULT_SKILL_REPO,
    branch: str = "main",
    subdir: str | Path | None = None,
    yes: bool = False,
    push: bool = True,
    commit_message: str | None = None,
) -> UploadResult:
    """Upload one skill directory into target repository subtree and optionally push."""
    source_dir = _resolve_skill_source(source)
    source_repo = repo.strip() if repo.strip() else DEFAULT_SKILL_REPO
    source_subdir = Path(subdir) if subdir is not None else DEFAULT_SKILL_SUBDIR

    repo_url = source_repo
    repo_path_candidate = Path(source_repo).expanduser()
    if repo_path_candidate.exists():
        repo_url = str(repo_path_candidate)
    elif is_repo_shorthand(source_repo):
        repo_url = f"https://github.com/{source_repo}.git"
    elif not is_git_url(source_repo):
        raise ValueError(f"Unsupported repo source: {source_repo}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        workdir = tmp_path / "repo"
        subprocess.run(["git", "clone", "--depth", "1", "--branch", branch, repo_url, str(workdir)], check=True)

        target_root = workdir / source_subdir
        target_root.mkdir(parents=True, exist_ok=True)
        target_rel = source_subdir / source_dir.name
        target_path = workdir / target_rel

        resolved_workdir = workdir.resolve()
        resolved_target_path = target_path.resolve(strict=False)
        try:
            resolved_target_path.relative_to(resolved_workdir)
        except ValueError as exc:
            raise ValueError(f"Target path escapes repository root: {target_path}") from exc

        if target_path.exists():
            if not yes:
                raise FileExistsError(
                    f"Skill '{source_dir.name}' already exists at {target_path}. Use --yes to overwrite."
                )
            shutil.rmtree(target_path)
        shutil.copytree(source_dir, target_path, ignore=IGNORE_PATTERNS)

        status = subprocess.run(
            ["git", "-C", str(workdir), "status", "--porcelain", "--", str(target_rel)],
            check=True,
            capture_output=True,
            text=True,
        )
        changed = bool(status.stdout.strip())
        committed = False
        pushed = False
        if changed:
            subprocess.run(["git", "-C", str(workdir), "add", "--", str(target_rel)], check=True)
            message = commit_message or f"feat(skills): upload {source_dir.name}"
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(workdir),
                    "-c",
                    "user.name=MagicSkills",
                    "-c",
                    "user.email=magicskills@local",
                    "commit",
                    "-m",
                    message,
                    "--",
                    str(target_rel),
                ],
                check=True,
            )
            committed = True
            if push:
                subprocess.run(["git", "-C", str(workdir), "push", "origin", branch], check=True)
                pushed = True

        return UploadResult(
            skill_name=source_dir.name,
            repo=repo_url,
            branch=branch,
            remote_subpath=str(target_rel).replace("\\", "/"),
            committed=committed,
            pushed=pushed,
        )


def install_skills(
    source: str | None = None,
    global_: bool = False,
    universal: bool = False,
    yes: bool = False,
    skill_name: str | None = None,
    target_root: Path | str | None = None,
) -> list[Path]:
    """Install skills from local path/repo or by skill name from default catalog."""
    if target_root is not None and (global_ or universal):
        raise ValueError("target_root cannot be used with global_/universal flags")

    resolved_target_root = (
        Path(target_root).expanduser() if target_root is not None else resolve_install_root(global_=global_, universal=universal)
    )
    source_value = source.strip() if source else ""
    requested_skill = skill_name.strip() if skill_name else None

    if not source_value and requested_skill:
        source_value = DEFAULT_SKILL_REPO
    elif source_value and not requested_skill and _looks_like_plain_skill_name(source_value):
        if not Path(source_value).expanduser().exists():
            requested_skill = source_value
            source_value = DEFAULT_SKILL_REPO
    elif not source_value:
        raise ValueError("install requires a source string (repo/path/git URL or skill name)")

    if Path(source_value).expanduser().exists():
        source_path = Path(source_value).expanduser()
        skill_dirs = _collect_skill_dirs(source_path, skill_name=requested_skill)
        if not skill_dirs:
            raise FileNotFoundError(f"No SKILL.md found under {source_path}")
        return [_copy_skill_dir(skill_dir, resolved_target_root, yes) for skill_dir in skill_dirs]

    repo_url = source_value
    if is_repo_shorthand(source_value):
        repo_url = f"https://github.com/{source_value}.git"
    if is_git_url(repo_url):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            subprocess.run(["git", "clone", "--depth", "1", repo_url, str(tmp_path)], check=True)
            source_root = _resolve_repo_source_root(tmp_path)
            skill_dirs = _collect_skill_dirs(source_root, skill_name=requested_skill)
            if not skill_dirs:
                raise FileNotFoundError(f"No SKILL.md found in repo {repo_url}")
            return [_copy_skill_dir(skill_dir, resolved_target_root, yes) for skill_dir in skill_dirs]

    raise ValueError(f"Unsupported source: {source_value}")


def create_skill(name: str, target_root: Path | None = None) -> Path:
    """Create a standard skill scaffold directory layout."""
    root = target_root or resolve_install_root(global_=False, universal=False)
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "assets").mkdir(exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        skill_md.write_text(
            "---\n"
            f"description: {name}\n"
            "---\n\n"
            "# Overview\n\n"
            "Describe the skill here.\n",
            encoding="utf-8",
        )
    return skill_dir


def delete_skill(name: str, paths: Iterable[Path] | None = None) -> Path:
    """Delete one discovered skill directory by name."""
    skills = Skills(paths=paths) if paths is not None else Skills()
    skill = skills.get_skill(name)
    shutil.rmtree(skill.base_dir)
    return skill.base_dir


def show_skill(name: str, paths: Iterable[Path] | None = None) -> dict[str, object]:
    """Return metadata for one discovered skill."""
    skills = Skills(paths=paths) if paths is not None else Skills()
    return skills.get_skill(name).to_dict()
