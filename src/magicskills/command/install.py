"""Filesystem-level skill installation and scaffold helpers."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from ..type.skillsregistry import ALL_SKILLS
from ..utils.utils import is_directory_or_symlink_to_directory, is_git_url, is_repo_shorthand

DEFAULT_SKILL_REPO = "https://github.com/Narwhal-Lab/MagicSkills.git"
IGNORE_PATTERNS = shutil.ignore_patterns(".git", "__pycache__", "*.pyc")


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


def _collect_named_skill_dirs(source_dir: Path, skill_name: str) -> list[Path]:
    """Collect one matching skill directory by name under source tree."""
    direct = source_dir / skill_name
    if is_directory_or_symlink_to_directory(direct) and (direct / "SKILL.md").exists():
        return [direct]

    matches: list[Path] = []
    seen: set[Path] = set()
    for skill_md in source_dir.rglob("SKILL.md"):
        entry = skill_md.parent
        if ".git" in entry.parts:
            continue
        if entry.name != skill_name:
            continue
        if not is_directory_or_symlink_to_directory(entry):
            continue
        resolved = entry.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        matches.append(entry)
    if not matches:
        raise FileNotFoundError(f"Skill '{skill_name}' not found under {source_dir}")
    matches.sort(key=lambda p: (len(p.parts), p.as_posix()))
    return matches


def _collect_skill_dirs(source_dir: Path) -> list[Path]:
    """Collect valid skill directories recursively from one source tree."""
    skills: list[Path] = []
    seen: set[Path] = set()
    for skill_md in source_dir.rglob("SKILL.md"):
        entry = skill_md.parent
        if ".git" in entry.parts:
            continue
        if not is_directory_or_symlink_to_directory(entry):
            continue
        resolved = entry.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        skills.append(entry)
    skills.sort(key=lambda p: p.as_posix())
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


def _install_and_sync(
    skill_dirs: list[Path],
    target_root: Path,
    yes: bool,
    source: str | Path | None = None,
) -> list[Path]:
    """Copy discovered skills to target root and sync them into Allskills."""
    from .createskill import createskill as command_createskill

    installed = [_copy_skill_dir(skill_dir, target_root, yes) for skill_dir in skill_dirs]
    for skill_dir in installed:
        command_createskill(
            ALL_SKILLS(),
            skill_path=skill_dir,
            source=source,
        )
    return installed


def install_from_local(  
    source_path: Path | str,
    target_root: Path,
    yes: bool,
) -> list[Path]:
    """Install skills from local filesystem path."""
    resolved_source_path = Path(source_path).expanduser()
    skill_dirs = _collect_skill_dirs(resolved_source_path)
    if not skill_dirs:
        raise FileNotFoundError(f"No SKILL.md found under {resolved_source_path}")
    return _install_and_sync(
        skill_dirs,
        target_root,
        yes,
        source=str(resolved_source_path.resolve()),
    )


def install_from_git(
    source: str,
    target_root: Path,
    yes: bool,
) -> list[Path]:
    """Install skills from git URL or GitHub shorthand."""
    repo_url = source.strip()
    if is_repo_shorthand(repo_url):
        repo_url = f"https://github.com/{repo_url}.git"
    if not is_git_url(repo_url):
        raise ValueError(f"Unsupported source: {source}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subprocess.run(["git", "clone", "--depth", "1", repo_url, str(tmp_path)], check=True)
        skill_dirs = _collect_skill_dirs(tmp_path)
        if not skill_dirs:
            raise FileNotFoundError(f"No SKILL.md found in repo {repo_url}")
        return _install_and_sync(skill_dirs, target_root, yes, source=repo_url)


def install_from_magicskills(
    skill_name: str,
    target_root: Path,
    yes: bool,
) -> list[Path]:
    """Install one named skill from default MagicSkills repository."""
    requested_skill = skill_name.strip()
    if not requested_skill:
        raise ValueError("install_from_magicskills requires a non-empty skill name")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subprocess.run(["git", "clone", "--depth", "1", DEFAULT_SKILL_REPO, str(tmp_path)], check=True)
        skill_dirs = _collect_named_skill_dirs(tmp_path, requested_skill)
        return _install_and_sync(skill_dirs, target_root, yes, source=DEFAULT_SKILL_REPO)


def install(
    source: str | None = None,
    global_: bool = False,
    universal: bool = False,
    yes: bool = False,
    target_root: Path | str | None = None,
) -> list[Path]:
    """Install skills from local path/repo or by skill name from default catalog."""
    if target_root is not None and (global_ or universal):
        raise ValueError("target_root cannot be used with global_/universal flags")

    resolved_target_root = (
        Path(target_root).expanduser()
        if target_root is not None
        else resolve_install_root(global_=global_, universal=universal)
    )
    source_value = source.strip() if source else ""
    if not source_value:
        raise ValueError("install requires a source string (repo/path/git URL or skill name)")

    source_path = Path(source_value).expanduser()
    if source_path.exists():
        return install_from_local(
            source_path,
            target_root=resolved_target_root,
            yes=yes,
        )

    if _looks_like_plain_skill_name(source_value):
        return install_from_magicskills(
            source_value,
            target_root=resolved_target_root,
            yes=yes,
        )

    return install_from_git(
        source_value,
        target_root=resolved_target_root,
        yes=yes,
    )
