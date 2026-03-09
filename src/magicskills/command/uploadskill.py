"""Command implementation for uploading a skill."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING

from ..type.result import UploadResult

if TYPE_CHECKING:
    from ..type.skills import Skills


IGNORE_PATTERNS = shutil.ignore_patterns(".git", "__pycache__", "*.pyc")
DEFAULT_SKILL_REPO = "https://github.com/Narwhal-Lab/MagicSkills.git"
DEFAULT_REPO_SLUG = "Narwhal-Lab/MagicSkills"
DEFAULT_SKILL_SUBDIR = "skills"


def _command_details(stdout: str | None, stderr: str | None) -> str:
    """Build a compact error details string from subprocess output."""
    return ((stderr or "") + "\n" + (stdout or "")).strip()


def _repo_name_from_slug(repo_slug: str) -> str:
    """Extract repository name from `owner/name` slug."""
    return repo_slug.rsplit("/", 1)[-1]


def _default_push_branch(skill_name: str) -> str:
    """Generate a default upload branch name under `fix/` namespace."""
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", skill_name.strip()) or "skill"
    return f"fix/upload-{safe_name}-{int(time.time())}"


def _resolve_default_branch(repo_slug: str) -> str:
    """Resolve default branch name for a GitHub repository."""
    try:
        completed = subprocess.run(
            ["gh", "repo", "view", repo_slug, "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"],
            check=True,
            capture_output=True,
            text=True,
        )
        branch = completed.stdout.strip()
        return branch or "main"
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "main"


def _ensure_gh_auth_status() -> None:
    """Require successful `gh auth status` before upload flow."""
    try:
        subprocess.run(
            ["gh", "auth", "status"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("`gh` CLI not found. Install GitHub CLI and run `gh auth login` first.") from exc
    except subprocess.CalledProcessError as exc:
        details = _command_details(exc.stdout, exc.stderr)
        if details:
            raise RuntimeError(f"`gh auth status` failed. Please run `gh auth login` first.\n{details}") from exc
        raise RuntimeError("`gh auth status` failed. Please run `gh auth login` first.") from exc


def _github_user_from_auth() -> tuple[str, str]:
    """Resolve authenticated GitHub user metadata as (login, html_url)."""
    default_html_url = "https://github.com/Narwhal-Lab/MagicSkills"

    try:
        completed = subprocess.run(
            ["gh", "api", "user"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout or "{}")
    except FileNotFoundError as exc:
        raise RuntimeError("failed to query GitHub user via gh: `gh` CLI not found") from exc
    except subprocess.CalledProcessError as exc:
        details = _command_details(exc.stdout, exc.stderr)
        if details:
            raise RuntimeError(f"failed to query GitHub user via gh: {details}") from exc
        raise RuntimeError("failed to query GitHub user via gh") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("failed to query GitHub user via gh: invalid JSON response") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("failed to query GitHub user via gh: invalid response payload")

    login = str(payload.get("login", "")).strip()
    if not login:
        raise RuntimeError("failed to query GitHub user via gh: missing login")
    html_url = str(payload.get("html_url", "")).strip()
    return login, html_url or default_html_url


def _ensure_fork_exists(repo_slug: str) -> None:
    """Create fork when missing; tolerate already-existing forks."""
    completed = subprocess.run(
        ["gh", "repo", "fork", repo_slug, "--remote=false"],
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return

    details = _command_details(completed.stdout, completed.stderr)
    if "already exist" in details.lower():
        return
    raise RuntimeError(f"failed to ensure fork via gh: {details}")


def _clone_fork_repo(owner_login: str, repo_slug: str, workdir: Path) -> None:
    """Clone the authenticated user's fork into one explicit workdir."""
    clone_url = f"https://github.com/{owner_login}/{_repo_name_from_slug(repo_slug)}.git"
    subprocess.run(
        ["git", "clone", clone_url, str(workdir)],
        check=True,
    )


def uploadskill(skills: Skills | Path | str, target: str | Path | None = None) -> UploadResult:
    """Upload one skill by collection target or direct skill directory path."""
    if target is None:
        if hasattr(skills, "get_skill"):
            raise ValueError("uploadskill requires target when called with a Skills instance")
        source_dir = Path(skills).expanduser().resolve()
    else:
        raw_target = str(target).strip()
        if not raw_target:
            raise ValueError("uploadskill requires target: <name-or-path>")
        try:
            skill = skills.get_skill(raw_target)  # type: ignore[attr-defined]
        except KeyError as exc:
            message = str(exc)
            if "Multiple skills named" in message:
                raise ValueError(
                    f"uploadskill: skill name '{raw_target}' is duplicated; pass skill directory path.\n{message}"
                ) from exc
            skills_name = getattr(skills, "name", "<unknown>")
            raise FileNotFoundError(
                f"Skill '{raw_target}' not found in skills instance '{skills_name}'"
            ) from exc
        source_dir = skill.path.expanduser().resolve()

    if not source_dir.is_dir() or not (source_dir / "SKILL.md").exists():
        raise FileNotFoundError(f"Skill directory is invalid: missing SKILL.md under {source_dir}")
    _ensure_gh_auth_status()

    repo_slug = DEFAULT_REPO_SLUG
    repo_url = DEFAULT_SKILL_REPO
    default_branch = _resolve_default_branch(repo_slug)
    source_subdir = Path(DEFAULT_SKILL_SUBDIR)
    requested_push_branch = _default_push_branch(source_dir.name)
    commit_message = f"Fix: upload skill {source_dir.name}"
    fork_owner_login, commit_author_html_url = _github_user_from_auth()
    commit_author_login = fork_owner_login

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        workdir = tmp_path / _repo_name_from_slug(repo_slug)

        _ensure_fork_exists(repo_slug)
        _clone_fork_repo(fork_owner_login, repo_slug, workdir)
        subprocess.run(["git", "-C", str(workdir), "remote", "add", "upstream", repo_url], check=True)
        subprocess.run(["git", "-C", str(workdir), "fetch", "upstream"], check=True)
        subprocess.run(["git", "-C", str(workdir), "checkout", default_branch], check=True)
        subprocess.run(["git", "-C", str(workdir), "pull", "--rebase", "upstream", default_branch], check=True)
        subprocess.run(["git", "-C", str(workdir), "checkout", "-b", requested_push_branch], check=True)

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
            raise FileExistsError(f"Skill '{source_dir.name}' already exists at {target_path}.")
        shutil.copytree(source_dir, target_path, ignore=IGNORE_PATTERNS)

        subprocess.run(["git", "-C", str(workdir), "status"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", str(workdir), "add", "-A"], check=True)

        changed_status = subprocess.run(
            ["git", "-C", str(workdir), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
        changed = bool(changed_status.stdout.strip())
        committed = False
        pushed = False
        push_remote: str | None = None
        actual_push_branch: str | None = None
        pr_url: str | None = None
        pr_created = False

        if changed:
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(workdir),
                    "-c",
                    f"user.name={commit_author_login}",
                    "-c",
                    f"user.url={commit_author_html_url}",
                    "commit",
                    "-m",
                    commit_message,
                ],
                check=True,
            )
            committed = True

            subprocess.run(["git", "-C", str(workdir), "push", "-u", "origin", requested_push_branch], check=True)
            pushed = True
            push_remote = "origin"
            actual_push_branch = requested_push_branch

            try:
                completed_pr = subprocess.run(
                    [
                        "gh",
                        "pr",
                        "create",
                        "--repo",
                        repo_slug,
                        "--base",
                        default_branch,
                        "--head",
                        requested_push_branch,
                    ],
                    cwd=workdir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError:
                completed_pr = subprocess.run(
                    [
                        "gh",
                        "pr",
                        "create",
                        "--repo",
                        repo_slug,
                        "--base",
                        default_branch,
                        "--head",
                        requested_push_branch,
                        "--title",
                        commit_message,
                        "--body",
                        "Automated PR created by MagicSkills.",
                    ],
                    cwd=workdir,
                    check=True,
                    capture_output=True,
                    text=True,
                )

            output = completed_pr.stdout.strip()
            pr_url = output.splitlines()[-1].strip() if output else None
            pr_created = bool(pr_url)

        return UploadResult(
            skill_name=source_dir.name,
            repo=repo_url,
            branch=default_branch,
            remote_subpath=str(target_rel).replace("\\", "/"),
            committed=committed,
            pushed=pushed,
            push_remote=push_remote,
            push_branch=actual_push_branch,
            pr_url=pr_url,
            pr_created=pr_created,
        )
