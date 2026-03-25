"""Command-line interface for MagicSkills.

Each subcommand maps to exactly one concrete feature.
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import platform
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Iterable

from .command.addskill import addskill as command_addskill
from .command.addskills import addskills as command_addskills
from .command.install import install
from .command.change_cli_description import change_cli_description as command_change_cli_description
from .command.createskill_template import createskill_template as command_createskill_template
from .command.change_tool_description import change_tool_description as command_change_tool_description
from .command.execskill import execskill as command_execskill
from .command.listskill import listskill as command_listskill
from .command.readskill import readskill as command_readskill
from .command.scanskill import scanskill as command_scanskill
from .command.scanskills import scanskills as command_scanskills
from .command.skill_tool import skill_tool as command_skill_tool
from .command.syncskills import syncskills as command_syncskills
from .command.uploadskill import uploadskill as command_uploadskill
from .command.showskill import showskill as command_showskill
from .command.listskills import listskills as command_listskills
from .command.loadskills import loadskills as command_loadskills
from .command.deleteskills import deleteskills as command_deleteskills
from .command.deleteskill import deleteskill as command_deleteskill
from .command.saveskills import saveskills as command_saveskills
from .type.skillsregistry import ALL_SKILLS, REGISTRY
from .type.skills import Skills
from .utils.agents_md import SYNC_MODES
from .utils.utils import normalize_paths


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


def _headers_from_args(values: Iterable[str] | None) -> dict[str, str] | None:
    """Parse repeated KEY:VALUE or KEY=VALUE header args into a mapping."""
    if not values:
        return None
    headers: dict[str, str] = {}
    for raw in values:
        value = str(raw).strip()
        if ":" in value:
            key, _, remainder = value.partition(":")
        elif "=" in value:
            key, _, remainder = value.partition("=")
        else:
            raise SystemExit(f"Invalid --header value: {value}. Use KEY:VALUE or KEY=VALUE.")
        key = key.strip()
        remainder = remainder.strip()
        if not key:
            raise SystemExit(f"Invalid --header value: {value}. Header key cannot be empty.")
        headers[key] = remainder
    return headers


def _looks_like_path_input(value: str) -> bool:
    raw = value.strip()
    if not raw:
        return False
    if "/" in raw or "\\" in raw or raw.startswith(".") or raw.startswith("~"):
        return True
    return Path(raw).expanduser().exists()


def _scan_kwargs_from_args(args: argparse.Namespace) -> dict[str, object]:
    """Build shared AI-Infra-Guard config kwargs from CLI args."""
    return {
        "base_url": args.base_url,
        "model": args.model,
        "token": args.token,
        "model_base_url": args.model_base_url,
        "prompt": args.prompt,
        "language": args.language,
        "thread": args.thread,
        "poll_interval": args.poll_interval,
        "timeout": args.timeout,
        "headers": _headers_from_args(args.header),
    }


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
    wrapper = textwrap.TextWrapper(
        width=inner_width,
        break_long_words=True,
        break_on_hyphens=False,
        replace_whitespace=False,
        drop_whitespace=False,
    )
    for row in rows:
        row_lines = str(row).splitlines() or [""]
        for row_line in row_lines:
            chunks = wrapper.wrap(row_line.expandtabs(4)) or [""]
            for chunk in chunks:
                output.append(f"| {chunk.ljust(inner_width)} |")
    output.append(_paint(border, style, color))
    return output


def _skills_from_paths(paths: list[Path] | None) -> Skills:
    """Build a Skills collection from custom paths or the default Allskills instance."""
    return Skills(paths=paths) if paths else ALL_SKILLS()


def _registered_skills_or_exit(name: str) -> Skills:
    """Return one registered collection or exit with a CLI-friendly message."""
    try:
        return REGISTRY.get_skills(name)
    except KeyError as exc:
        raise SystemExit(str(exc)) from exc


def _format_install_error(exc: Exception, *, yes: bool) -> str:
    """Render install failures as concise CLI-facing messages."""
    if isinstance(exc, FileExistsError):
        lines = [f"install failed: {exc}"]
        if not yes:
            lines.append("Hint: rerun with -y/--yes to overwrite the existing skill directory.")
        lines.append("Hint: use -t/--target to install into a different directory.")
        return "\n".join(lines)
    if isinstance(exc, subprocess.CalledProcessError):
        command = exc.cmd if isinstance(exc.cmd, str) else " ".join(str(part) for part in exc.cmd)
        return f"install failed: command exited with status {exc.returncode}: {command}"
    return f"install failed: {exc}"


def _serialize_skills_instances(instances: list[Skills]) -> list[dict[str, object]]:
    """Convert named skills collections into JSON-safe payload."""
    payload = []
    for instance in instances:
        payload.append(
            {
                "name": instance.name,
                "skills_count": len(instance.skills),
                "paths": [str(path) for path in instance.paths],
                "tool_description": instance.tool_description,
                "cli_description": instance.cli_description,
                "agent_md_path": str(instance.agent_md_path),
            }
        )
    return payload


def _print_skills_instances(instances: list[Skills], *, json_output: bool) -> None:
    """Render named skills collections in text or JSON form."""
    if json_output:
        print(json.dumps(_serialize_skills_instances(instances), ensure_ascii=False, indent=2))
        return

    color = _supports_color_output()
    width = 96
    if not instances:
        print(
            "\n".join(
                _boxed_lines("MagicSkills Collections", ["No skills instances."], width=width, style="1;36", color=color)
            )
        )
        return

    total_skills = 0
    sections: list[str] = []
    sections.extend(
        _boxed_lines("MagicSkills Collections", [f"Total collections: {len(instances)}"], width=width, style="1;36", color=color)
    )
    for instance in instances:
        name = instance.name
        count = len(instance.skills)
        total_skills += count
        tool_description = inspect.cleandoc(instance.tool_description or "")
        tool_description_lines = tool_description.splitlines() or ["(none)"]
        cli_description = inspect.cleandoc(instance.cli_description or "")
        cli_description_lines = cli_description.splitlines() or ["(none)"]
        rows = [
            f"- name: {name}",
            f"skills: {count}",
            f"agent_md_path: {instance.agent_md_path}",
            f"paths: {', '.join(str(path) for path in instance.paths) if instance.paths else '(none)'}",
            f"tool_description: {tool_description_lines[0]}",
            *[f"  {line}" for line in tool_description_lines[1:]],
            f"cli_description: {cli_description_lines[0]}",
            *[f"  {line}" for line in cli_description_lines[1:]],
        ]
        sections.append("")
        sections.extend(_boxed_lines(f"Collection {name}", rows, width=width, style="1;33", color=color))

    sections.append("")
    sections.extend(
        _boxed_lines(
            "Summary",
            [
                f"Total collections: {len(instances)}",
                f"Total skills across collections: {total_skills}",
            ],
            width=width,
            style="1;35",
            color=color,
        )
    )
    print("\n".join(sections))


def _skill_list_from_args(values: Iterable[str] | None):
    """Resolve optional skill targets from Allskills into concrete Skill objects."""
    if not values:
        return None

    resolved = []
    seen_paths: set[Path] = set()
    for value in values:
        try:
            skill = ALL_SKILLS().get_skill(value)
        except KeyError as exc:
            message = str(exc)
            if "Multiple skills named" in message:
                raise SystemExit(
                    f"addskills: skill target '{value}' is duplicated; pass skill directory path.\n{message}"
                ) from exc
            raise SystemExit(f"addskills: skill target not found: {value}") from exc

        resolved_path = skill.path.expanduser().resolve()
        if resolved_path in seen_paths:
            continue
        seen_paths.add(resolved_path)
        resolved.append(skill)
    return resolved


def cmd_list(args: argparse.Namespace) -> int:
    """List available skills."""
    skills = _registered_skills_or_exit(args.name) if args.name else ALL_SKILLS()
    print(command_listskill(skills))
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    """Read one file by path or by skill name (reads SKILL.md from Allskills)."""
    try:
        print(command_readskill(ALL_SKILLS(), args.path))
    except (KeyError, ValueError, FileNotFoundError, OSError) as exc:
        raise SystemExit(str(exc)) from exc
    return 0


def cmd_exec(args: argparse.Namespace) -> int:
    """Execute one command in current collection context.

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
    result = command_execskill(skills, command, shell=not args.no_shell, stream=stream)
    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    return result.returncode


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync skills XML section into AGENTS.md (or custom output)."""
    skills = _registered_skills_or_exit(args.name)
    if not args.yes:
        confirm = input(f"Sync {len(skills.skills)} skills to {args.output or skills.agent_md_path}? [y/N] ")
        if confirm.strip().lower() not in {"y", "yes"}:
            print("Cancelled.")
            return 1
    output = command_syncskills(skills, args.output, mode=args.mode)
    print(f"Synced to {output}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    """Install skills from repo/local source into configured scope."""
    if args.target and (args.global_scope or args.universal):
        raise SystemExit("--target cannot be used with --global or --universal")
    try:
        installed = install(
            args.source,
            global_=args.global_scope,
            universal=args.universal,
            yes=args.yes,
            target_root=args.target,
        )
    except (FileExistsError, FileNotFoundError, ValueError, subprocess.CalledProcessError, OSError) as exc:
        raise SystemExit(_format_install_error(exc, yes=args.yes)) from exc
    for path in installed:
        print(f"Installed: {path}")
    return 0


def cmd_add_skill(args: argparse.Namespace) -> int:
    """Register one skill by target(name or path) into one collection."""
    skills = _registered_skills_or_exit(args.name) if args.name else ALL_SKILLS()
    path = command_addskill(skills, target=args.target, source=args.source)
    print(f"Registered: {path}")
    return 0


def cmd_create_skill_template(args: argparse.Namespace) -> int:
    """Create a standard skill scaffold under one base directory."""
    path = command_createskill_template(args.name, args.base_dir)
    print(f"Created template: {path}")
    return 0


def _configure_add_skill_parser(parser: argparse.ArgumentParser) -> None:
    """Configure args for `addskill`."""
    parser.add_argument("target", help="Skill directory path or skill name from Allskills")
    parser.add_argument("--source", help="Install/discovery source to store in Skill metadata")
    parser.add_argument("--name", help="Target named skills collection (default: Allskills)")
    parser.set_defaults(func=cmd_add_skill)


def cmd_upload_skill(args: argparse.Namespace) -> int:
    """Upload one skill with default fork -> push -> PR workflow."""
    for attempt in range(4):
        try:
            result = command_uploadskill(ALL_SKILLS(), args.source)
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
    skills = _registered_skills_or_exit(args.name) if args.name else ALL_SKILLS()
    try:
        path = command_deleteskill(skills, str(args.target))
    except (KeyError, ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc

    print(f"Deleted: {path}")
    return 0


def cmd_show_skill(args: argparse.Namespace) -> int:
    """Show all files/content for one skill from Allskills by name or path target."""
    raw_target = str(args.target).strip()
    if not raw_target:
        raise SystemExit("showskill requires target: <name-or-path>")
    try:
        print(command_showskill(ALL_SKILLS(), raw_target))
    except (KeyError, ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
    return 0


def cmd_add_skills(args: argparse.Namespace) -> int:
    """Create one named skills collection instance."""
    paths = _paths_from_args(args.paths)
    skill_list = _skill_list_from_args(args.skill_list)
    if paths and skill_list:
        raise SystemExit("--paths cannot be used with --skill-list")
    path_values = [str(path) for path in paths] if paths else None
    try:
        instance = command_addskills(
            name=args.name,
            skill_list=skill_list,
            paths=path_values,
            tool_description=args.tool_description,
            cli_description=args.cli_description,
            agent_md_path=args.agent_md_path,
        )
    except (KeyError, ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
    print(f"Created skills instance: {instance.name}")
    print(f"Skills count: {len(instance.skills)}")
    return 0


def cmd_list_skills_instances(args: argparse.Namespace) -> int:
    """List registered named skills collection instances."""
    instances = command_listskills()
    _print_skills_instances(instances, json_output=args.json)
    return 0


def cmd_load_skills(args: argparse.Namespace) -> int:
    """Load registry state from disk and display loaded collections."""
    instances = command_loadskills(args.path)
    _print_skills_instances(instances, json_output=args.json)
    return 0


def cmd_delete_skills_instance(args: argparse.Namespace) -> int:
    """Delete one or more named skills collection instances."""
    try:
        command_deleteskills(*args.names)
    except (KeyError, ValueError) as exc:
        message = exc.args[0] if exc.args else str(exc)
        raise SystemExit(message) from exc
    if len(args.names) == 1:
        print(f"Deleted skills instance: {args.names[0]}")
    else:
        print(f"Deleted skills instances: {', '.join(args.names)}")
    return 0


def cmd_save_skills(args: argparse.Namespace) -> int:
    """Persist registry state to disk."""
    print(command_saveskills(args.path))
    return 0


def cmd_change_tool_description(args: argparse.Namespace) -> int:
    """Update tool description for a named collection."""
    instance = _registered_skills_or_exit(args.name)
    command_change_tool_description(instance, args.description)
    print(f"Updated tool description for skills instance: {args.name}")
    return 0


def cmd_change_cli_description(args: argparse.Namespace) -> int:
    """Update CLI description for a named collection."""
    instance = _registered_skills_or_exit(args.name)
    command_change_cli_description(instance, args.description)
    print(f"Updated CLI description for skills instance: {args.name}")
    return 0


def cmd_skill_tool(args: argparse.Namespace) -> int:
    """Run skill_tool compatible action from CLI."""
    if args.name:
        skills = _registered_skills_or_exit(args.name)
    else:
        skills = ALL_SKILLS()
    result = command_skill_tool(skills, args.action, args.arg)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


def _format_scan_result(result: dict[str, object]) -> str:
    summary = result.get("summary")
    risk_level = None
    findings_count = None
    if isinstance(summary, dict):
        risk_level = summary.get("risk_level")
        findings_count = summary.get("findings_count")

    rows = [
        f"Skill: {result.get('skill_name', '(unknown)')}",
        f"Path: {result.get('skill_path', '(unknown)')}",
        f"Session ID: {result.get('session_id', '(unknown)')}",
        f"Status: {result.get('status', '(unknown)')}",
    ]
    if risk_level not in {None, ""}:
        rows.append(f"Risk level: {risk_level}")
    if findings_count is not None:
        rows.append(f"Findings: {findings_count}")
    task_log = str(result.get("task_log", "")).strip()
    if task_log:
        rows.append(f"Task log: {task_log}")
    return "\n".join(rows)


def _format_scanskills_result(result: dict[str, object]) -> str:
    lines = [
        f"Collection: {result.get('collection_name', '(unknown)')}",
        f"Total skills: {result.get('total_skills', 0)}",
        f"Succeeded: {result.get('succeeded', 0)}",
        f"Failed: {result.get('failed', 0)}",
        "",
    ]
    for item in result.get("results", []):
        if not isinstance(item, dict):
            continue
        skill_name = item.get("skill_name", "(unknown)")
        if item.get("ok"):
            summary = item.get("summary")
            risk_level = None
            findings_count = None
            if isinstance(summary, dict):
                risk_level = summary.get("risk_level")
                findings_count = summary.get("findings_count")
            detail_parts = [str(item.get("status", "completed"))]
            if risk_level not in {None, ""}:
                detail_parts.append(f"risk={risk_level}")
            if findings_count is not None:
                detail_parts.append(f"findings={findings_count}")
            lines.append(f"- {skill_name}: {', '.join(detail_parts)}")
        else:
            lines.append(f"- {skill_name}: failed ({item.get('error', 'unknown error')})")
    return "\n".join(lines)


def cmd_scan_skill(args: argparse.Namespace) -> int:
    """Scan one skill by skill name or skill directory path."""
    scan_kwargs = _scan_kwargs_from_args(args)
    target: object
    if _looks_like_path_input(args.target):
        target = args.target
    else:
        skills = _registered_skills_or_exit(args.name) if args.name else ALL_SKILLS()
        try:
            target = skills.get_skill(args.target)
        except KeyError as exc:
            raise SystemExit(str(exc)) from exc

    try:
        result = command_scanskill(target, **scan_kwargs)
    except (ValueError, FileNotFoundError, RuntimeError, TimeoutError) as exc:
        raise SystemExit(str(exc)) from exc

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(_format_scan_result(result))
    return 0


def cmd_scan_skills(args: argparse.Namespace) -> int:
    """Scan every skill in one named skills collection."""
    skills = _registered_skills_or_exit(args.name)
    try:
        result = command_scanskills(
            skills,
            fail_fast=args.fail_fast,
            **_scan_kwargs_from_args(args),
        )
    except (ValueError, FileNotFoundError, RuntimeError, TimeoutError) as exc:
        raise SystemExit(str(exc)) from exc

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(_format_scanskills_result(result))
    return 0 if result.get("ok") else 1


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser with all supported commands."""
    parser = argparse.ArgumentParser(prog="magicskills")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("listskill", help="List skills from Allskills or one named skills collection")
    p_list.add_argument("--name", help="Skills collection name shown by listskills")
    p_list.set_defaults(func=cmd_list)

    p_read = sub.add_parser("readskill", help="Read by file path or skill name")
    p_read.add_argument("path", help="File path or skill name")
    p_read.set_defaults(func=cmd_read)

    p_exec = sub.add_parser("execskill", help="Execute command")
    p_exec.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --")
    p_exec.add_argument("--no-shell", action="store_true", help="Run without shell")
    p_exec.add_argument("--json", action="store_true", help="Output JSON result")
    p_exec.add_argument("--paths", nargs="*", help="Custom skill search paths")
    p_exec.set_defaults(func=cmd_exec)

    p_sync = sub.add_parser("syncskills", help="Sync skills into AGENTS.md")
    p_sync.add_argument("name", help="Skills instance name")
    p_sync.add_argument("-o", "--output", help="Output path (default: AGENTS.md)")
    p_sync.add_argument(
        "--mode",
        default="none",
        choices=SYNC_MODES,
        help="Sync mode: keep original skills block, or render only CLI description",
    )
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

    p_add = sub.add_parser("addskill", help="Register one skill into one collection")
    _configure_add_skill_parser(p_add)

    p_create_template = sub.add_parser("createskill_template", help="Create a standard skill scaffold")
    p_create_template.add_argument("name", help="Skill name")
    p_create_template.add_argument("base_dir", help="Skills root directory")
    p_create_template.set_defaults(func=cmd_create_skill_template)

    p_upload = sub.add_parser("uploadskill", help="Upload one skill to repository (default settings)")
    p_upload.add_argument("source", help="Skill name (Allskills) or local skill directory path")
    p_upload.set_defaults(func=cmd_upload_skill)

    p_delete = sub.add_parser("deleteskill", help="Delete a skill by one target (name or path)")
    p_delete.add_argument("target", help="Skill name or skill directory path")
    p_delete.add_argument("--name", help="Target named skills collection (default: Allskills)")
    p_delete.set_defaults(func=cmd_delete_skill)

    p_show = sub.add_parser("showskill", help="Show all content for one skill from Allskills")
    p_show.add_argument("target", help="Skill name or skill directory path")
    p_show.set_defaults(func=cmd_show_skill)

    p_add_skills = sub.add_parser("addskills", help="Create a named skills collection")
    p_add_skills.add_argument("name", help="Skills instance name")
    p_add_skills.add_argument(
        "--skill-list",
        nargs="*",
        help="Specific skills (name or skill directory path) for this collection",
    )
    p_add_skills.add_argument("--paths", nargs="*", help="Custom paths for this collection")
    p_add_skills.add_argument("--tool-description", help="Tool description override")
    p_add_skills.add_argument("--cli-description", help="CLI description override")
    p_add_skills.add_argument("--agent-md-path", help="AGENTS.md path override")
    p_add_skills.set_defaults(func=cmd_add_skills)

    p_list_skills = sub.add_parser("listskills", help="List named skills collections")
    p_list_skills.add_argument("--json", action="store_true", help="JSON output")
    p_list_skills.set_defaults(func=cmd_list_skills_instances)

    p_load_skills = sub.add_parser("loadskills", help="Load registry from disk")
    p_load_skills.add_argument("path", nargs="?", help="Optional registry file path")
    p_load_skills.add_argument("--json", action="store_true", help="JSON output")
    p_load_skills.set_defaults(func=cmd_load_skills)

    p_delete_skills = sub.add_parser("deleteskills", help="Delete one or more named skills collections")
    p_delete_skills.add_argument("names", nargs="+", help="One or more skills instance names")
    p_delete_skills.set_defaults(func=cmd_delete_skills_instance)

    p_save_skills = sub.add_parser("saveskills", help="Persist registry to disk")
    p_save_skills.add_argument("path", nargs="?", help="Optional save output path")
    p_save_skills.set_defaults(func=cmd_save_skills)


    p_change_desc = sub.add_parser("changetooldescription", help="Update tool description on a skills collection")
    p_change_desc.add_argument("name", help="Skills instance name")
    p_change_desc.add_argument("description", help="New tool description")
    p_change_desc.set_defaults(func=cmd_change_tool_description)

    p_change_cli_desc = sub.add_parser("changeclidescription", help="Update CLI description on a skills collection")
    p_change_cli_desc.add_argument("name", help="Skills instance name")
    p_change_cli_desc.add_argument("description", help="New CLI description")
    p_change_cli_desc.set_defaults(func=cmd_change_cli_description)

    p_tool = sub.add_parser("skill-tool", help="Run skill_tool action")
    p_tool.add_argument("action", help="Action name")
    p_tool.add_argument("--arg", default="", help="Action argument")
    p_tool.add_argument("--name", help="Use a named skills instance")
    p_tool.set_defaults(func=cmd_skill_tool)

    p_scan = sub.add_parser("scanskill", help="Scan one skill with AI-Infra-Guard")
    p_scan.add_argument("target", help="Skill name or skill directory path")
    p_scan.add_argument("--name", help="Resolve skill name from a named skills collection (default: Allskills)")
    p_scan.add_argument("--base-url", help="AI-Infra-Guard base URL")
    p_scan.add_argument("--model", help="Model name used by AI-Infra-Guard scan")
    p_scan.add_argument("--token", help="Model token used by AI-Infra-Guard scan")
    p_scan.add_argument("--model-base-url", help="Model base URL used by AI-Infra-Guard scan")
    p_scan.add_argument("--prompt", help="Custom scan prompt")
    p_scan.add_argument("--language", help="Scan language (default: env or en)")
    p_scan.add_argument("--thread", type=int, help="Concurrent thread count")
    p_scan.add_argument("--poll-interval", type=float, help="Polling interval in seconds")
    p_scan.add_argument("--timeout", type=float, help="Overall scan timeout in seconds")
    p_scan.add_argument(
        "--header",
        action="append",
        help="Optional request header for AI-Infra-Guard API, format KEY:VALUE",
    )
    p_scan.add_argument("--json", action="store_true", help="JSON output")
    p_scan.set_defaults(func=cmd_scan_skill)

    p_scan_all = sub.add_parser("scanskills", help="Scan all skills in a named collection with AI-Infra-Guard")
    p_scan_all.add_argument("name", help="Skills instance name")
    p_scan_all.add_argument("--base-url", help="AI-Infra-Guard base URL")
    p_scan_all.add_argument("--model", help="Model name used by AI-Infra-Guard scan")
    p_scan_all.add_argument("--token", help="Model token used by AI-Infra-Guard scan")
    p_scan_all.add_argument("--model-base-url", help="Model base URL used by AI-Infra-Guard scan")
    p_scan_all.add_argument("--prompt", help="Custom scan prompt")
    p_scan_all.add_argument("--language", help="Scan language (default: env or en)")
    p_scan_all.add_argument("--thread", type=int, help="Concurrent thread count")
    p_scan_all.add_argument("--poll-interval", type=float, help="Polling interval in seconds")
    p_scan_all.add_argument("--timeout", type=float, help="Overall scan timeout in seconds")
    p_scan_all.add_argument(
        "--header",
        action="append",
        help="Optional request header for AI-Infra-Guard API, format KEY:VALUE",
    )
    p_scan_all.add_argument("--fail-fast", action="store_true", help="Stop at the first failed skill scan")
    p_scan_all.add_argument("--json", action="store_true", help="JSON output")
    p_scan_all.set_defaults(func=cmd_scan_skills)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
