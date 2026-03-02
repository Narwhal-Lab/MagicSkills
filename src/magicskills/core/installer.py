"""Filesystem-level skill installation and scaffold helpers."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .registry import ALL_SKILLS
from .skills import discover_skills
from .utils import is_directory_or_symlink_to_directory, is_git_url, is_repo_shorthand


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
    push_remote: str | None
    push_branch: str | None
    pr_url: str | None
    pr_created: bool


def _github_repo_slug(repo_source: str) -> str | None:
    """Return `owner/repo` for GitHub sources, else None."""
    value = repo_source.strip()
    if is_repo_shorthand(value):
        return value

    patterns = (
        r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
        r"^(?:git@github\.com:|ssh://git@github\.com/)([^/]+)/([^/]+?)(?:\.git)?/?$",
    )
    for pattern in patterns:
        match = re.match(pattern, value)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
    return None


def _build_pr_url(base_repo: str, base_branch: str, fork_repo: str, fork_branch: str) -> str | None:
    """Build a GitHub compare URL for opening a PR."""
    base_slug = _github_repo_slug(base_repo)
    fork_slug = _github_repo_slug(fork_repo)
    if not base_slug or not fork_slug:
        return None
    fork_owner = fork_slug.split("/", 1)[0]
    return f"https://github.com/{base_slug}/compare/{base_branch}...{fork_owner}:{fork_branch}?expand=1"


def _github_api_token() -> str | None:
    """Get GitHub API token from environment."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token.strip() or None
    return None


def _github_api_request(method: str, path: str, token: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call GitHub REST API and return JSON object."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(
        f"https://api.github.com{path}",
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MagicSkills",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8").strip()
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore").strip()
        raise RuntimeError(f"GitHub API {method} {path} failed: HTTP {exc.code} {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc}") from exc

    if not body:
        return {}
    try:
        data_obj = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"GitHub API {method} {path} returned invalid JSON") from exc
    if not isinstance(data_obj, dict):
        raise RuntimeError(f"GitHub API {method} {path} returned unexpected JSON payload")
    return data_obj


def _create_pr_with_api(
    base_repo: str,
    base_branch: str,
    fork_repo: str,
    fork_branch: str,
    title: str,
    body: str,
    token: str,
) -> str:
    """Create a pull request via GitHub REST API."""
    base_slug = _github_repo_slug(base_repo)
    fork_slug = _github_repo_slug(fork_repo)
    if not base_slug or not fork_slug:
        raise ValueError("automatic PR creation requires GitHub repositories for both repo and fork_repo")
    fork_owner = fork_slug.split("/", 1)[0]
    payload = {
        "title": title,
        "body": body,
        "base": base_branch,
        "head": f"{fork_owner}:{fork_branch}",
    }
    response = _github_api_request("POST", f"/repos/{base_slug}/pulls", token, payload=payload)
    url = str(response.get("html_url", "")).strip()
    if not url:
        raise RuntimeError("GitHub API pull request created but no html_url returned")
    return url


def _auto_fork_repo_url_with_api(base_repo: str, token: str) -> str:
    """Resolve (and create if needed) current user's fork repo URL via GitHub REST API."""
    base_slug = _github_repo_slug(base_repo)
    if not base_slug:
        raise ValueError("auto fork requires a GitHub base repository URL/shorthand")
    owner, repo_name = base_slug.split("/", 1)

    user = _github_api_request("GET", "/user", token)
    login = str(user.get("login", "")).strip()
    if not login:
        raise RuntimeError("failed to resolve current GitHub user via API")

    try:
        _github_api_request("POST", f"/repos/{owner}/{repo_name}/forks", token, payload={})
    except RuntimeError as exc:
        err = str(exc).lower()
        if "already exists" not in err and "name already exists on this account" not in err:
            raise

    for _ in range(10):
        try:
            _github_api_request("GET", f"/repos/{login}/{repo_name}", token)
            return f"https://github.com/{login}/{repo_name}.git"
        except RuntimeError:
            time.sleep(1)
    raise RuntimeError(f"fork repository '{login}/{repo_name}' not ready yet, please retry shortly")


def _create_pr_with_gh(
    base_repo: str,
    base_branch: str,
    fork_repo: str,
    fork_branch: str,
    title: str,
    body: str,
) -> str:
    """Create a pull request via GitHub CLI and return PR URL."""
    base_slug = _github_repo_slug(base_repo)
    fork_slug = _github_repo_slug(fork_repo)
    if not base_slug or not fork_slug:
        raise ValueError("automatic PR creation requires GitHub repositories for both repo and fork_repo")
    fork_owner = fork_slug.split("/", 1)[0]
    head = f"{fork_owner}:{fork_branch}"
    try:
        completed = subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                base_slug,
                "--base",
                base_branch,
                "--head",
                head,
                "--title",
                title,
                "--body",
                body,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        token = _github_api_token()
        if not token:
            raise RuntimeError(
                "`gh` CLI not found. Install `gh` or set GH_TOKEN/GITHUB_TOKEN to auto-create PR."
            ) from exc
        return _create_pr_with_api(
            base_repo=base_repo,
            base_branch=base_branch,
            fork_repo=fork_repo,
            fork_branch=fork_branch,
            title=title,
            body=body,
            token=token,
        )
    except subprocess.CalledProcessError as exc:
        token = _github_api_token()
        if token:
            return _create_pr_with_api(
                base_repo=base_repo,
                base_branch=base_branch,
                fork_repo=fork_repo,
                fork_branch=fork_branch,
                title=title,
                body=body,
                token=token,
            )
        stderr = exc.stderr.strip() if exc.stderr else str(exc)
        raise RuntimeError(f"failed to create PR via gh: {stderr}") from exc

    output = completed.stdout.strip()
    if not output:
        raise RuntimeError("gh pr create succeeded but returned empty output")
    return output.splitlines()[-1].strip()


def _auto_fork_repo_url(base_repo: str) -> str:
    """Resolve (and create if needed) current user's fork repo URL via gh CLI."""
    base_slug = _github_repo_slug(base_repo)
    if not base_slug:
        raise ValueError("auto fork requires a GitHub base repository URL/shorthand")

    owner, repo_name = base_slug.split("/", 1)
    _ = owner
    try:
        user_info = subprocess.run(
            ["gh", "api", "user", "-q", ".login"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        token = _github_api_token()
        if token:
            return _auto_fork_repo_url_with_api(base_repo, token)
        raise RuntimeError(
            "`gh` CLI not found. Install GitHub CLI and run `gh auth login`, "
            "or set GH_TOKEN/GITHUB_TOKEN to enable auto fork+PR upload."
        ) from exc
    except subprocess.CalledProcessError as exc:
        token = _github_api_token()
        if token:
            return _auto_fork_repo_url_with_api(base_repo, token)
        stderr = exc.stderr.strip() if exc.stderr else str(exc)
        raise RuntimeError(f"failed to query GitHub user via gh: {stderr}") from exc

    login = user_info.stdout.strip()
    if not login:
        raise RuntimeError("failed to resolve current GitHub user via gh")

    fork_cmd = ["gh", "repo", "fork", base_slug, "--clone=false", "--remote=false"]
    fork_result = subprocess.run(fork_cmd, capture_output=True, text=True)
    if fork_result.returncode != 0:
        stderr = ((fork_result.stderr or "") + "\n" + (fork_result.stdout or "")).lower()
        if "already exists" not in stderr:
            raw_err = (fork_result.stderr or fork_result.stdout or "").strip()
            raise RuntimeError(f"failed to auto-create fork via gh: {raw_err}")

    return f"https://github.com/{login}/{repo_name}.git"


def _default_push_branch(skill_name: str) -> str:
    """Generate a default unique push branch name."""
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", skill_name.strip()) or "skill"
    return f"magicskills/{safe_name}-{int(time.time())}"


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
    def _resolve_by_name(skill_name: str) -> Path:
        matches = [skill for skill in ALL_SKILLS.skills if skill.name == skill_name]
        if len(matches) > 1:
            candidates = ", ".join(str(skill.base_dir) for skill in matches)
            raise ValueError(
                f"Skill name '{skill_name}' has multiple matches in Allskills. "
                f"Please pass the skill directory path as source. Candidates: {candidates}"
            )
        if len(matches) == 1:
            return matches[0].base_dir
        raise KeyError(skill_name)

    value = source.strip()
    if not value:
        raise ValueError("uploadskill requires a non-empty source")
    if value.lower().endswith("skill.md"):
        raise ValueError("uploadskill does not accept SKILL.md file path; pass skill directory or skill name")

    path_candidate = Path(value).expanduser()
    explicit_path_input = "/" in value or "\\" in value or value.startswith(".") or value.startswith("~")

    try:
        source_dir = _resolve_by_name(value)
    except KeyError:
        discovered = discover_skills(ALL_SKILLS.paths)
        for skill in discovered:
            try:
                ALL_SKILLS.remove_skill(base_dir=skill.base_dir)
            except (KeyError, ValueError):
                pass
            ALL_SKILLS.add_skill(skill)
            resolved_base_dir = skill.base_dir.expanduser().resolve()
            if all(resolved_base_dir != path.expanduser().resolve() for path in ALL_SKILLS.paths):
                ALL_SKILLS.paths.append(skill.base_dir)
        try:
            source_dir = _resolve_by_name(value)
        except KeyError as exc:
            if explicit_path_input:
                if not path_candidate.exists():
                    raise FileNotFoundError(f"Skill directory not found: {path_candidate}") from exc
                if not is_directory_or_symlink_to_directory(path_candidate):
                    raise ValueError(f"uploadskill expects a skill directory path, got file: {path_candidate}") from exc
                source_dir = path_candidate.resolve()
            elif path_candidate.exists():
                if not is_directory_or_symlink_to_directory(path_candidate):
                    raise ValueError(f"uploadskill expects a skill directory path, got file: {path_candidate}") from exc
                source_dir = path_candidate.resolve()
            else:
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
    fork_repo: str | None = None,
    push_branch: str | None = None,
    create_pr: bool = False,
    pr_title: str | None = None,
    pr_body: str | None = None,
) -> UploadResult:
    """Upload one skill directory into target repository subtree and optionally push.

    Push target is fork-only: fork is auto-resolved via gh (or via `fork_repo`).
    """
    source_dir = _resolve_skill_source(source)
    base_branch = branch.strip() or "main"
    source_repo = repo.strip() if repo.strip() else DEFAULT_SKILL_REPO
    source_subdir = Path(subdir) if subdir is not None else DEFAULT_SKILL_SUBDIR
    requested_push_branch = push_branch.strip() if push_branch and push_branch.strip() else _default_push_branch(source_dir.name)
    requested_pr_title = pr_title.strip() if pr_title and pr_title.strip() else None
    requested_pr_body = pr_body if pr_body is not None else ""
    fork_repo_url: str | None = None

    repo_url = source_repo
    repo_path_candidate = Path(source_repo).expanduser()
    if repo_path_candidate.exists():
        repo_url = str(repo_path_candidate)
    elif is_repo_shorthand(source_repo):
        repo_url = f"https://github.com/{source_repo}.git"
    elif not is_git_url(source_repo):
        raise ValueError(f"Unsupported repo source: {source_repo}")

    if fork_repo is not None:
        fork_source = fork_repo.strip()
        if not fork_source:
            raise ValueError("fork_repo cannot be empty")
        fork_path_candidate = Path(fork_source).expanduser()
        if fork_path_candidate.exists():
            fork_repo_url = str(fork_path_candidate)
        elif is_repo_shorthand(fork_source):
            fork_repo_url = f"https://github.com/{fork_source}.git"
        elif is_git_url(fork_source):
            fork_repo_url = fork_source
        else:
            raise ValueError(f"Unsupported fork repo source: {fork_source}")
    if push and fork_repo_url is None:
        fork_repo_url = _auto_fork_repo_url(repo_url)
    if create_pr and not push:
        raise ValueError("create_pr requires push=True")
    if create_pr and fork_repo_url is None:
        raise ValueError("create_pr requires fork_repo")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        workdir = tmp_path / "repo"
        subprocess.run(["git", "clone", "--depth", "1", "--branch", base_branch, repo_url, str(workdir)], check=True)

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
        push_remote: str | None = None
        actual_push_branch: str | None = None
        pr_url: str | None = None
        pr_created = False
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
                assert fork_repo_url is not None
                subprocess.run(["git", "-C", str(workdir), "remote", "add", "fork", fork_repo_url], check=True)
                subprocess.run(
                    ["git", "-C", str(workdir), "push", "fork", f"HEAD:{requested_push_branch}"], check=True
                )
                push_remote = "fork"
                actual_push_branch = requested_push_branch
                pr_url = _build_pr_url(repo_url, base_branch, fork_repo_url, requested_push_branch)
                pushed = True
                if create_pr:
                    title = requested_pr_title or f"feat(skills): upload {source_dir.name}"
                    body = requested_pr_body or "Automated PR created by MagicSkills."
                    pr_url = _create_pr_with_gh(
                        base_repo=repo_url,
                        base_branch=base_branch,
                        fork_repo=fork_repo_url,
                        fork_branch=requested_push_branch,
                        title=title,
                        body=body,
                    )
                    pr_created = True

        return UploadResult(
            skill_name=source_dir.name,
            repo=repo_url,
            branch=base_branch,
            remote_subpath=str(target_rel).replace("\\", "/"),
            committed=committed,
            pushed=pushed,
            push_remote=push_remote,
            push_branch=actual_push_branch,
            pr_url=pr_url,
            pr_created=pr_created,
        )


def _sync_installed_paths_to_allskills(installed: list[Path]) -> None:
    """Add installed skills and their base_dir paths into Allskills."""
    installed_skills = discover_skills(installed)
    known_paths = {path.expanduser().resolve() for path in ALL_SKILLS.paths}

    for skill in installed_skills:
        try:
            ALL_SKILLS.remove_skill(base_dir=skill.base_dir)
        except (KeyError, ValueError):
            pass
        ALL_SKILLS.add_skill(skill)

        base_dir = skill.base_dir
        resolved_base_dir = base_dir.expanduser().resolve()
        if resolved_base_dir not in known_paths:
            ALL_SKILLS.paths.append(base_dir)
            known_paths.add(resolved_base_dir)


def install(
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
        Path(target_root).expanduser()
        if target_root is not None
        else resolve_install_root(global_=global_, universal=universal)
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
        installed = [_copy_skill_dir(skill_dir, resolved_target_root, yes) for skill_dir in skill_dirs]
        _sync_installed_paths_to_allskills(installed)
        return installed

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
            installed = [_copy_skill_dir(skill_dir, resolved_target_root, yes) for skill_dir in skill_dirs]
            _sync_installed_paths_to_allskills(installed)
            return installed

    raise ValueError(f"Unsupported source: {source_value}")


# Backward-compatible alias; prefer `install`.
install_skills = install




def create_skill(name: str, target_root: Path | None = None) -> Path:
    """Create a standard skill scaffold directory layout and register it in Allskills."""
    root = target_root or resolve_install_root(global_=False, universal=False)
    root.mkdir(parents=True, exist_ok=True)
    skill_dir = root / name
    existing_valid_skill = False

    if skill_dir.exists():
        if not is_directory_or_symlink_to_directory(skill_dir):
            raise ValueError(f"Skill path exists and is not a directory: {skill_dir}")
        has_contents = any(skill_dir.iterdir())
        has_skill_md = (skill_dir / "SKILL.md").exists()
        if has_skill_md:
            existing_valid_skill = True
        if has_contents and not has_skill_md:
            raise FileExistsError(
                f"Skill directory already has content but is not a valid skill (missing SKILL.md): {skill_dir}"
            )
    else:
        skill_dir.mkdir(parents=True, exist_ok=False)

    if not existing_valid_skill:
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

    _sync_installed_paths_to_allskills([skill_dir])
    return skill_dir


def delete_skill(name: str | None = None, paths: Iterable[Path | str] | None = None) -> Path:
    """Delete one skill by name and/or explicit directory path.

    Supported modes:
    - name only: resolve from Allskills and delete its base_dir.
    - path only: delete by explicit skill directory path.
    - both name+path: validate path maps to that name in Allskills, then delete path.
    """
    target_path: Path
    target_name: str | None = None
    target_from_paths: Path | None = None
    path_values = list(paths or [])

    if len(path_values) > 1:
        raise ValueError("delete_skill supports at most one path")

    if path_values:
        candidate = Path(path_values[0]).expanduser()
        if not candidate.exists():
            raise FileNotFoundError(f"Skill path not found: {candidate}")
        if not is_directory_or_symlink_to_directory(candidate):
            raise ValueError(f"delete_skill expects a directory path, got: {candidate}")
        target_from_paths = candidate.resolve()

    if name and target_from_paths is not None:
        target_name = name
        matched_name: str | None = None
        for skill in ALL_SKILLS.skills:
            if skill.base_dir.expanduser().resolve() == target_from_paths:
                matched_name = skill.name
                break
        if matched_name is None:
            raise KeyError(f"Skill at path '{target_from_paths}' not found in Allskills")
        if matched_name != name:
            raise ValueError(
                f"Path/name mismatch: path '{target_from_paths}' is skill '{matched_name}', not '{name}'"
            )
        target_path = target_from_paths
    elif name:
        target_name = name
        target_path = _resolve_skill_source(name)
    elif target_from_paths is not None:
        target_path = target_from_paths
    else:
        raise ValueError("delete_skill requires at least one of: name or path")

    shutil.rmtree(target_path)

    try:
        if target_name is None:
            ALL_SKILLS.remove_skill(base_dir=target_path)
        else:
            ALL_SKILLS.remove_skill(name=target_name, base_dir=target_path)
    except (KeyError, ValueError):
        pass

    deleted_resolved = target_path.expanduser().resolve()
    ALL_SKILLS.paths = [path for path in ALL_SKILLS.paths if path.expanduser().resolve() != deleted_resolved]
    return target_path


def show_skill(name: str, paths: Iterable[Path] | None = None, base_dir: Path | str | None = None) -> str:
    """Show one skill's full content from Allskills in beautified format."""
    _ = paths
    return ALL_SKILLS.showskill(name, base_dir=base_dir)
