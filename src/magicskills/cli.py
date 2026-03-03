"""Command-line interface for MagicSkills.

Each subcommand maps to exactly one concrete feature.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from .core.installer import (
    create_skill,
    delete_skill,
    install,
    show_skill,
    upload_skill,
)
from .core.registry import ALL_SKILLS, REGISTRY
from .core.skill import Skill
from .core.skills import Skills
from .core.utils import normalize_paths, read_text


def _is_gh_missing_error(exc: Exception) -> bool:
    """Detect runtime errors caused by missing GitHub CLI."""
    message = str(exc).lower()
    return "gh" in message and "not found" in message


def _is_gh_auth_error(exc: Exception) -> bool:
    """Detect runtime errors caused by unauthenticated GitHub CLI."""
    message = str(exc).lower()
    return (
        "failed to query github user via gh" in message
        or "gh auth login" in message
        or "failed to create pr via gh" in message
    )


def _install_gh_cli() -> None:
    """Install GitHub CLI using best-effort OS package manager commands."""
    if shutil.which("gh"):
        return

    system = platform.system().lower()
    attempts: list[tuple[str, list[list[str]]]] = []
    if system == "linux":
        attempts = [
            ("apt-get", [["apt-get", "update"], ["apt-get", "install", "-y", "gh"]]),
            ("dnf", [["dnf", "install", "-y", "gh"]]),
            ("yum", [["yum", "install", "-y", "gh"]]),
            ("pacman", [["pacman", "-Sy", "--noconfirm", "github-cli"]]),
        ]
    elif system == "darwin":
        attempts = [("brew", [["brew", "install", "gh"]])]
    elif system == "windows":
        attempts = [
            ("winget", [["winget", "install", "--id", "GitHub.cli", "-e", "--source", "winget"]]),
            ("choco", [["choco", "install", "gh", "-y"]]),
        ]
    else:
        raise RuntimeError(f"Unsupported platform for auto-installing gh: {system}")

    failures: list[str] = []
    for binary, commands in attempts:
        if shutil.which(binary) is None:
            continue
        try:
            for command in commands:
                subprocess.run(command, check=True)
            if shutil.which("gh"):
                return
            failures.append(f"{binary}: install command completed but gh still not found")
        except subprocess.CalledProcessError as exc:
            failures.append(f"{binary}: command failed ({exc})")
        except OSError as exc:
            failures.append(f"{binary}: failed to execute ({exc})")

    if failures:
        details = "; ".join(failures)
        raise RuntimeError(f"Failed to auto-install gh. Details: {details}")
    raise RuntimeError("No supported package manager found to auto-install gh")


def _maybe_install_gh_for_upload() -> bool:
    """Prompt user to auto-install gh and return whether upload can be retried."""
    if not sys.stdin.isatty():
        print("GitHub CLI (gh) is missing and session is non-interactive; cannot auto-install.")
        return False

    answer = input("GitHub CLI (gh) is missing. Install now and continue upload? [Y/n] ").strip().lower()
    if answer not in {"", "y", "yes"}:
        return False

    try:
        _install_gh_cli()
    except RuntimeError as exc:
        print(str(exc))
        return False
    return shutil.which("gh") is not None


def _maybe_login_gh_for_upload() -> bool:
    """Prompt user to authenticate gh and return whether upload can be retried."""
    if not sys.stdin.isatty():
        print("GitHub CLI (gh) is not authenticated and session is non-interactive; cannot run `gh auth login`.")
        return False
    if shutil.which("gh") is None:
        print("GitHub CLI (gh) is not installed yet.")
        return False

    answer = input("GitHub CLI is not authenticated. Run `gh auth login` now? [Y/n] ").strip().lower()
    if answer not in {"", "y", "yes"}:
        return _maybe_set_gh_token_for_upload()

    try:
        subprocess.run(["gh", "auth", "login"], check=True)
        subprocess.run(["gh", "api", "user", "-q", ".login"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"`gh auth login` failed: {exc}")
        return _maybe_set_gh_token_for_upload()


def _maybe_set_gh_token_for_upload() -> bool:
    """Prompt user to provide GH_TOKEN for API fallback upload flow."""
    if not sys.stdin.isatty():
        return False
    answer = input("Provide GH_TOKEN now for API fallback? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        return False
    token = input("Paste GH_TOKEN: ").strip()
    if not token:
        print("Empty token. Skip GH_TOKEN fallback.")
        return False
    os.environ["GH_TOKEN"] = token
    return True


def _paths_from_args(values: Iterable[str] | None) -> list[Path] | None:
    """Normalize optional path arguments."""
    if not values:
        return None
    return normalize_paths(values)


def _looks_like_path_input(value: str) -> bool:
    """Return True when input should be treated as filesystem path."""
    raw = value.strip()
    if not raw:
        return False
    if "/" in raw or "\\" in raw or raw.startswith(".") or raw.startswith("~"):
        return True
    return Path(raw).expanduser().exists()


def _supports_color_output() -> bool:
    """Best-effort detection for ANSI color support in current terminal."""
    if os.environ.get("NO_COLOR"):
        return False
    term = os.environ.get("TERM", "").lower()
    if term in {"", "dumb"}:
        return False
    return sys.stdout.isatty()


def _paint(text: str, style: str, enabled: bool) -> str:
    """Apply ANSI style when color is enabled."""
    if not enabled:
        return text
    return f"\033[{style}m{text}\033[0m"


def _boxed_lines(title: str, rows: list[str], *, width: int, style: str, color: bool) -> list[str]:
    """Render one titled ASCII box with optional color."""
    border = "+" + "-" * (width - 2) + "+"
    output = [
        _paint(border, style, color),
        _paint("|" + f" {title} ".ljust(width - 2) + "|", style, color),
        _paint(border, style, color),
    ]
    inner_width = width - 4
    for row in rows:
        chunks = [row[i : i + inner_width] for i in range(0, len(row), inner_width)] or [""]
        for chunk in chunks:
            output.append(f"| {chunk.ljust(inner_width)} |")
    output.append(_paint(border, style, color))
    return output


def _skills_from_paths(paths: list[Path] | None) -> Skills:
    """Build a Skills collection from custom paths or the default Allskills instance."""
    return Skills(paths=paths) if paths else ALL_SKILLS


def _resolve_skill_in_collection(
    collection: Skills,
    name: str,
    path: str | None = None,
    command_name: str = "command",
    duplicate_hint: str = "add --path <skill-dir>",
) -> Skill:
    """Resolve one skill from a collection, requiring --path only when duplicate names exist."""
    skill_path = Path(path).expanduser() if path else None
    try:
        try:
            return collection.get_skill(name, path=skill_path)
        except TypeError:
            return collection.get_skill(name, base_dir=skill_path)
    except KeyError as exc:
        message = str(exc)
        if "Multiple skills named" in message and not path:
            raise SystemExit(
                f"{command_name}: skill name '{name}' is duplicated; please {duplicate_hint}.\n{message}"
            ) from exc
        raise SystemExit(message) from exc


def _resolve_allskills_skill(
    name: str,
    path: str | None = None,
    command_name: str = "command",
    duplicate_hint: str = "add --path <skill-dir>",
) -> Skill:
    """Resolve one skill from Allskills, requiring --path only when duplicate names exist."""
    return _resolve_skill_in_collection(
        ALL_SKILLS,
        name=name,
        path=path,
        command_name=command_name,
        duplicate_hint=duplicate_hint,
    )


def _resolve_allskills_skill_by_path(path_value: str, command_name: str = "command") -> Skill:
    """Resolve one skill from Allskills by exact skill directory path."""
    target_path = Path(path_value).expanduser().resolve()
    for skill in ALL_SKILLS.skills:
        if skill.path.expanduser().resolve() == target_path:
            return skill
    raise SystemExit(f"{command_name}: skill path not found in Allskills: {target_path}")


def _remove_skill_from_instance(instance: Skills, *, path: Path, name: str | None = None) -> bool:
    """Try to remove one skill from collection by path (and optional name)."""
    try:
        try:
            instance.remove_skill(name=name, path=path)
        except TypeError:
            instance.remove_skill(name=name, base_dir=path)
    except (KeyError, ValueError):
        return False
    return True


def _prune_instance_paths(instance: Skills) -> None:
    """Drop paths that no longer correspond to any skill base_dir in this instance."""
    keep = {skill.base_dir.expanduser().resolve() for skill in instance.skills}
    instance.paths = [path for path in instance.paths if path.expanduser().resolve() in keep]


def _resolve_skill_target_in_collection(instance: Skills, target: str, command_name: str) -> Skill:
    """Resolve one skill in a named collection by target(name or path)."""
    raw_target = target.strip()
    if not raw_target:
        raise SystemExit(f"{command_name} requires target: <name-or-path>")

    if _looks_like_path_input(raw_target):
        target_path = Path(raw_target).expanduser().resolve()
        for skill in instance.skills:
            if skill.path.expanduser().resolve() == target_path:
                return skill
        raise SystemExit(f"{command_name}: skill path not found in skills instance '{instance.name}': {target_path}")

    return _resolve_skill_in_collection(
        instance,
        raw_target,
        path=None,
        command_name=command_name,
        duplicate_hint="pass <skill-directory-path> as target",
    )


def cmd_list(args: argparse.Namespace) -> int:
    """List available skills."""
    _ = args
    print(ALL_SKILLS.listskill())
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    """Read one file by path or by skill name (reads SKILL.md from Allskills)."""
    raw = str(args.path).strip()
    file_path = Path(raw).expanduser()
    explicit_path = "/" in raw or "\\" in raw or raw.startswith(".") or raw.startswith("~")
    if file_path.exists():
        if not file_path.is_file():
            raise SystemExit(f"readskill expects a file path, got: {file_path}")
    elif explicit_path:
        raise SystemExit(f"readskill path not found: {file_path}")
    else:
        try:
            resolved_skill = ALL_SKILLS.get_skill(raw)
        except KeyError as exc:
            message = str(exc)
            if "Multiple skills named" in message:
                raise SystemExit(
                    f"readskill: skill name '{raw}' is duplicated; please pass file path "
                    f"(for example: <skill-path>/SKILL.md).\n{message}"
                ) from exc
            raise SystemExit(message) from exc
        file_path = resolved_skill.path / "SKILL.md"

    try:
        content = read_text(file_path)
    except UnicodeDecodeError as exc:
        raise SystemExit(f"readskill only supports UTF-8 text files: {file_path}") from exc
    except OSError as exc:
        raise SystemExit(f"readskill failed to read '{file_path}': {exc}") from exc

    resolved = file_path.resolve()
    line_count = len(content.splitlines())
    byte_count = len(content.encode("utf-8"))
    print(f"Reading file: {resolved}")
    print(f"Lines: {line_count}  Bytes: {byte_count}")
    print("-" * 80)
    print(content, end="" if content.endswith("\n") else "\n")
    print("-" * 80)
    return 0


def cmd_exec(args: argparse.Namespace) -> int:
    """Execute one command with merged environments from all skills in this collection.

    Default behavior streams output directly to the current terminal.
    """
    paths = _paths_from_args(args.paths)
    skills = _skills_from_paths(paths)
    command_parts = list(args.command)
    if command_parts and command_parts[0] == "--":
        command_parts = command_parts[1:]
    command = " ".join(command_parts).strip()
    if not command:
        raise SystemExit("exec requires command after --")
    stream = not args.json
    result = skills.execskill(command, shell=not args.no_shell, stream=stream)
    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    return result.returncode


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync skills XML section into AGENTS.md (or custom output)."""
    skills = REGISTRY.get(args.name)
    if not args.yes:
        confirm = input(f"Sync {len(skills.skills)} skills to {args.output or skills.agent_md_path}? [y/N] ")
        if confirm.strip().lower() not in {"y", "yes"}:
            print("Cancelled.")
            return 1
    output = skills.syncskills(args.output)
    print(f"Synced to {output}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    """Install skills from repo/local source into configured scope."""
    if args.target and (args.global_scope or args.universal):
        raise SystemExit("--target cannot be used with --global or --universal")
    installed = install(
        args.source,
        global_=args.global_scope,
        universal=args.universal,
        yes=args.yes,
        target_root=args.target,
    )
    for path in installed:
        print(f"Installed: {path}")
    return 0


def cmd_create_skill(args: argparse.Namespace) -> int:
    """Create one skill scaffold."""
    target_root = Path(args.root).expanduser() if args.root else None
    path = create_skill(args.name, target_root=target_root)
    print(f"Created: {path}")
    return 0


def cmd_upload_skill(args: argparse.Namespace) -> int:
    """Upload one skill with default fork -> push -> PR workflow."""
    for attempt in range(4):
        try:
            result = upload_skill(
                source=args.source,
                create_pr=True,
            )
            break
        except (KeyError, ValueError, FileNotFoundError) as exc:
            raise SystemExit(str(exc)) from exc
        except RuntimeError as exc:
            if _is_gh_missing_error(exc) and _maybe_install_gh_for_upload():
                continue
            if _is_gh_auth_error(exc) and _maybe_login_gh_for_upload():
                continue
            raise SystemExit(str(exc)) from exc
    print(f"Uploaded: {result.skill_name}")
    print(f"Repo: {result.repo}")
    print(f"Branch: {result.branch}")
    print(f"Target: {result.remote_subpath}")
    print(f"Committed: {result.committed}")
    print(f"Pushed: {result.pushed}")
    if result.push_remote:
        print(f"Push remote: {result.push_remote}")
    if result.push_branch:
        print(f"Push branch: {result.push_branch}")
    if result.pr_url:
        print(f"PR URL: {result.pr_url}")
    if result.pr_created:
        print("PR Created: True")
    return 0


def cmd_delete_skill(args: argparse.Namespace) -> int:
    """Delete skill by one unified target argument: name or path."""
    raw_target = str(args.target).strip()
    if not raw_target:
        raise SystemExit("deleteskill requires target: <name-or-path>")
    treat_as_path = _looks_like_path_input(raw_target)

    delete_paths: list[Path]
    target_name: str | None
    if treat_as_path:
        target_name = None
        delete_paths = [Path(raw_target).expanduser()]
    else:
        resolved_skill = _resolve_allskills_skill(
            raw_target,
            path=None,
            command_name="deleteskill",
            duplicate_hint="pass <skill-directory-path> as target",
        )
        delete_paths = [resolved_skill.path]
        target_name = resolved_skill.name
    try:
        path = delete_skill(target_name, paths=delete_paths)
    except (KeyError, ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc

    # If physical deletion happened in Allskills, clean stale references in other collections.
    resolved_deleted = path.expanduser().resolve()
    for collection_name in REGISTRY.list():
        instance = REGISTRY.get(collection_name)
        if instance is ALL_SKILLS:
            continue
        if _remove_skill_from_instance(instance, path=resolved_deleted):
            _prune_instance_paths(instance)
            REGISTRY.save_instance(collection_name)

    print(f"Deleted: {path}")
    return 0


def cmd_delete_skill_from_instance(args: argparse.Namespace) -> int:
    """Remove one skill from a named skills collection only."""
    try:
        instance = REGISTRY.get(args.name)
    except KeyError as exc:
        raise SystemExit(str(exc)) from exc

    skill = _resolve_skill_target_in_collection(instance, args.target, command_name="deleteskill2skills")
    removed = _remove_skill_from_instance(instance, path=skill.path, name=skill.name)
    if not removed:
        raise SystemExit(f"deleteskill2skills: failed to remove skill '{skill.name}' from '{args.name}'")
    _prune_instance_paths(instance)
    REGISTRY.save_instance(args.name)
    print(f"Removed from skills instance '{args.name}': {skill.path}")
    return 0


def cmd_show_skill(args: argparse.Namespace) -> int:
    """Show all files/content for one skill from Allskills by name or path target."""
    raw_target = str(args.target).strip()
    if not raw_target:
        raise SystemExit("showskill requires target: <name-or-path>")
    if _looks_like_path_input(raw_target):
        resolved_skill = _resolve_allskills_skill_by_path(raw_target, command_name="showskill")
    else:
        resolved_skill = _resolve_allskills_skill(
            raw_target,
            path=None,
            command_name="showskill",
            duplicate_hint="pass <skill-directory-path> as target",
        )
    try:
        print(show_skill(resolved_skill.name, path=resolved_skill.path))
    except (KeyError, ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
    return 0


def cmd_create_skills(args: argparse.Namespace) -> int:
    """Create one named skills collection instance."""
    paths = _paths_from_args(args.paths)
    path_values = [str(path) for path in paths] if paths else None
    instance = REGISTRY.create(name=args.name, paths=path_values)
    if args.tool_description:
        instance.change_tool_description(args.tool_description)
    if args.agent_md_path:
        instance.agent_md_path = Path(args.agent_md_path).expanduser().resolve()
    REGISTRY.save_instance(args.name)
    print(f"Created skills instance: {instance.name}")
    print(f"Skills count: {len(instance.skills)}")
    return 0


def cmd_list_skills_instances(args: argparse.Namespace) -> int:
    """List registered named skills collection instances."""
    names = REGISTRY.list()
    if args.json:
        payload = []
        for name in names:
            instance = REGISTRY.get(name)
            payload.append(
                {
                    "name": name,
                    "skills_count": len(instance.skills),
                    "paths": [str(path) for path in instance.paths],
                    "tool_description": instance.tool_description,
                    "agent_md_path": str(instance.agent_md_path),
                }
            )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    color = _supports_color_output()
    width = 96
    if not names:
        print("\n".join(_boxed_lines("MagicSkills Collections", ["No skills instances."], width=width, style="1;36", color=color)))
        return 0

    total_skills = 0
    sections: list[str] = []
    sections.extend(_boxed_lines("MagicSkills Collections", [f"Total collections: {len(names)}"], width=width, style="1;36", color=color))
    for name in names:
        instance = REGISTRY.get(name)
        count = len(instance.skills)
        total_skills += count
        rows = [
            f"- name: {name}",
            f"skills: {count}",
            f"agent_md_path: {instance.agent_md_path}",
            f"paths: {', '.join(str(path) for path in instance.paths) if instance.paths else '(none)'}",
            f"tool_description: {instance.tool_description}",
        ]
        sections.append("")
        sections.extend(_boxed_lines(f"Collection {name}", rows, width=width, style="1;33", color=color))

    sections.append("")
    sections.extend(
        _boxed_lines(
            "Summary",
            [
                f"Total collections: {len(names)}",
                f"Total skills across collections: {total_skills}",
            ],
            width=width,
            style="1;35",
            color=color,
        )
    )
    print("\n".join(sections))
    return 0


def cmd_delete_skills_instance(args: argparse.Namespace) -> int:
    """Delete one named skills collection instance."""
    REGISTRY.delete(args.name)
    print(f"Deleted skills instance: {args.name}")
    return 0


def cmd_add_skill_to_instance(args: argparse.Namespace) -> int:
    """Attach one skill into a named collection by target(name or path)."""
    instance = REGISTRY.get(args.name)
    raw_target = str(args.target).strip()
    if not raw_target:
        raise SystemExit("addskill2skills requires target: <name-or-path>")
    if _looks_like_path_input(raw_target):
        skill = _resolve_allskills_skill_by_path(raw_target, command_name="addskill2skills")
    else:
        skill = _resolve_allskills_skill(
            raw_target,
            path=None,
            command_name="addskill2skills",
            duplicate_hint="pass <skill-directory-path> as target",
        )

    target_base_dir = skill.base_dir.expanduser().resolve()
    known_paths = {path.expanduser().resolve() for path in instance.paths}
    if target_base_dir not in known_paths:
        instance.paths.append(skill.base_dir)
    try:
        try:
            instance.remove_skill(path=skill.path)
        except TypeError:
            instance.remove_skill(base_dir=skill.path)
    except (KeyError, ValueError):
        pass
    instance.add_skill(skill)
    REGISTRY.save_instance(args.name)
    print(f"Added '{skill.name}' to '{args.name}' (path: {skill.path})")
    return 0


def cmd_change_tool_description(args: argparse.Namespace) -> int:
    """Update tool description for a named collection."""
    instance = REGISTRY.get(args.name)
    instance.change_tool_description(args.description)
    REGISTRY.save_instance(args.name)
    print(f"Updated tool description for skills instance: {args.name}")
    return 0


def cmd_skill_for_all_agent(args: argparse.Namespace) -> int:
    """Run Skill_For_All_Agent compatible action from CLI."""
    if args.name:
        skills = REGISTRY.get(args.name)
    else:
        skills = ALL_SKILLS
    result = skills.skill_for_all_agent(args.action, args.arg)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser with all supported commands."""
    parser = argparse.ArgumentParser(prog="magicskills")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("listskill", help="List skills from Allskills")
    p_list.set_defaults(func=cmd_list)

    p_read = sub.add_parser("readskill", help="Read by file path or skill name")
    p_read.add_argument("path", help="File path or skill name")
    p_read.set_defaults(func=cmd_read)

    p_exec = sub.add_parser("execskill", help="Execute command with all skills environments")
    p_exec.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --")
    p_exec.add_argument("--no-shell", action="store_true", help="Run without shell")
    p_exec.add_argument("--json", action="store_true", help="Output JSON result")
    p_exec.add_argument("--paths", nargs="*", help="Custom skill search paths")
    p_exec.set_defaults(func=cmd_exec)

    p_sync = sub.add_parser("syncskills", help="Sync skills into AGENTS.md")
    p_sync.add_argument("name", help="Skills instance name")
    p_sync.add_argument("-o", "--output", help="Output path (default: AGENTS.md)")
    p_sync.add_argument("-y", "--yes", action="store_true", help="Non-interactive")
    p_sync.set_defaults(func=cmd_sync)

    p_install = sub.add_parser("install", help="Install skills or skill from source or by skill name")
    p_install.add_argument("source", help="GitHub repo (owner/repo), git URL, local path, or skill name")
    p_install.add_argument("--global", dest="global_scope", action="store_true", help="Install to global scope")
    p_install.add_argument("--universal", action="store_true", help="Install to .agent/skills")
    p_install.add_argument(
        "-t",
        "--target",
        help="Custom install target directory (cannot be used with --global/--universal)",
    )
    p_install.add_argument("-y", "--yes", action="store_true", help="Overwrite without prompt")
    p_install.set_defaults(func=cmd_install)

    p_create = sub.add_parser("createskill", help="Create skill skeleton")
    p_create.add_argument("name", help="Skill name")
    p_create.add_argument("--root", help="Target skills root directory")
    p_create.set_defaults(func=cmd_create_skill)

    p_upload = sub.add_parser("uploadskill", help="Upload one skill to repository (default settings)")
    p_upload.add_argument("source", help="Skill name (Allskills) or local skill directory path")
    p_upload.set_defaults(func=cmd_upload_skill)

    p_delete = sub.add_parser("deleteskill", help="Delete a skill by one target (name or path)")
    p_delete.add_argument("target", help="Skill name or skill directory path")
    p_delete.set_defaults(func=cmd_delete_skill)

    p_delete_from_instance = sub.add_parser("deleteskill2skills", help="Remove one skill from a named skills collection")
    p_delete_from_instance.add_argument("name", help="Skills instance name")
    p_delete_from_instance.add_argument("target", help="Skill name or skill directory path")
    p_delete_from_instance.set_defaults(func=cmd_delete_skill_from_instance)

    p_show = sub.add_parser("showskill", help="Show all content for one skill from Allskills")
    p_show.add_argument("target", help="Skill name or skill directory path")
    p_show.set_defaults(func=cmd_show_skill)

    p_create_skills = sub.add_parser("createskills", help="Create a named skills collection")
    p_create_skills.add_argument("name", help="Skills instance name")
    p_create_skills.add_argument("--paths", nargs="*", help="Custom paths for this collection")
    p_create_skills.add_argument("--tool-description", help="Tool description override")
    p_create_skills.add_argument("--agent-md-path", help="AGENTS.md path override")
    p_create_skills.set_defaults(func=cmd_create_skills)

    p_list_skills = sub.add_parser("listskills", help="List named skills collections")
    p_list_skills.add_argument("--json", action="store_true", help="JSON output")
    p_list_skills.set_defaults(func=cmd_list_skills_instances)

    p_delete_skills = sub.add_parser("deleteskills", help="Delete a named skills collection")
    p_delete_skills.add_argument("name", help="Skills instance name")
    p_delete_skills.set_defaults(func=cmd_delete_skills_instance)

    p_add_skill = sub.add_parser("addskill2skills", help="Add one skill into a skills collection")
    p_add_skill.add_argument("name", help="Skills instance name")
    p_add_skill.add_argument("target", help="Skill name or skill directory path")
    p_add_skill.set_defaults(func=cmd_add_skill_to_instance)

    p_change_desc = sub.add_parser("changetooldescription", help="Update tool description on a skills collection")
    p_change_desc.add_argument("name", help="Skills instance name")
    p_change_desc.add_argument("description", help="New tool description")
    p_change_desc.set_defaults(func=cmd_change_tool_description)

    p_tool = sub.add_parser("skill-for-all-agent", help="Run Skill_For_All_Agent action")
    p_tool.add_argument("action", help="Action name")
    p_tool.add_argument("--arg", default="", help="Action argument")
    p_tool.add_argument("--name", help="Use a named skills instance")
    p_tool.set_defaults(func=cmd_skill_for_all_agent)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
