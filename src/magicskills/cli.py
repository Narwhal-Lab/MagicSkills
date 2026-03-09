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

from .command.install import install
from .command.createskill import createskill as command_createskill
from .command.createskill_template import createskill_template as command_createskill_template
from .command.change_tool_description import change_tool_description as command_change_tool_description
from .command.execskill import execskill as command_execskill
from .command.listskill import listskill as command_listskill
from .command.readskill import readskill as command_readskill
from .command.skill_tool import skill_tool as command_skill_tool
from .command.syncskills import syncskills as command_syncskills
from .command.uploadskill import uploadskill as command_uploadskill
from .command.showskill import showskill as command_showskill
from .command.createskills import createskills as command_createskills
from .command.listskills import listskills as command_listskills
from .command.loadskills import loadskills as command_loadskills
from .command.deleteskills import deleteskills as command_deleteskills
from .command.deleteskill import deleteskill as command_deleteskill
from .command.saveskills import saveskills as command_saveskills
from .type.skillsregistry import ALL_SKILLS, REGISTRY
from .type.skills import Skills
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
        description = inspect.cleandoc(instance.tool_description or "")
        description_lines = description.splitlines() or ["(none)"]
        rows = [
            f"- name: {name}",
            f"skills: {count}",
            f"agent_md_path: {instance.agent_md_path}",
            f"paths: {', '.join(str(path) for path in instance.paths) if instance.paths else '(none)'}",
            f"tool_description: {description_lines[0]}",
            *[f"  {line}" for line in description_lines[1:]],
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
                    f"createskills: skill target '{value}' is duplicated; pass skill directory path.\n{message}"
                ) from exc
            raise SystemExit(f"createskills: skill target not found: {value}") from exc

        resolved_path = skill.path.expanduser().resolve()
        if resolved_path in seen_paths:
            continue
        seen_paths.add(resolved_path)
        resolved.append(skill)
    return resolved


def cmd_list(args: argparse.Namespace) -> int:
    """List available skills."""
    _ = args
    print(command_listskill(ALL_SKILLS()))
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
    skills = REGISTRY.get_skills(args.name)
    if not args.yes:
        confirm = input(f"Sync {len(skills.skills)} skills to {args.output or skills.agent_md_path}? [y/N] ")
        if confirm.strip().lower() not in {"y", "yes"}:
            print("Cancelled.")
            return 1
    output = command_syncskills(skills, args.output)
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
    """Register one existing skill directory into Allskills."""
    skill_path = Path(args.path).expanduser()
    path = command_createskill(ALL_SKILLS(), skill_path=skill_path, source=args.source)
    print(f"Registered: {path}")
    return 0


def cmd_create_skill_template(args: argparse.Namespace) -> int:
    """Create a standard skill scaffold under one base directory."""
    path = command_createskill_template(args.name, args.base_dir)
    print(f"Created template: {path}")
    return 0


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
    try:
        path = command_deleteskill(ALL_SKILLS(), str(args.target))
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


def cmd_create_skills(args: argparse.Namespace) -> int:
    """Create one named skills collection instance."""
    paths = _paths_from_args(args.paths)
    skill_list = _skill_list_from_args(args.skill_list)
    if paths and skill_list:
        raise SystemExit("--paths cannot be used with --skill-list")
    path_values = [str(path) for path in paths] if paths else None
    instance = command_createskills(
        name=args.name,
        skill_list=skill_list,
        paths=path_values,
        tool_description=args.tool_description,
        agent_md_path=args.agent_md_path,
    )
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
    """Delete one named skills collection instance."""
    command_deleteskills(args.name)
    print(f"Deleted skills instance: {args.name}")
    return 0


def cmd_save_skills(args: argparse.Namespace) -> int:
    """Persist registry state to disk."""
    print(command_saveskills(args.path))
    return 0


def cmd_change_tool_description(args: argparse.Namespace) -> int:
    """Update tool description for a named collection."""
    instance = REGISTRY.get_skills(args.name)
    command_change_tool_description(instance, args.description)
    print(f"Updated tool description for skills instance: {args.name}")
    return 0


def cmd_skill_tool(args: argparse.Namespace) -> int:
    """Run skill_tool compatible action from CLI."""
    if args.name:
        skills = REGISTRY.get_skills(args.name)
    else:
        skills = ALL_SKILLS()
    result = command_skill_tool(skills, args.action, args.arg)
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

    p_exec = sub.add_parser("execskill", help="Execute command")
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

    p_create = sub.add_parser("createskill", help="Register one existing skill directory")
    p_create.add_argument("path", help="Skill directory path (must contain SKILL.md)")
    p_create.add_argument("--source", help="Install/discovery source to store in Skill metadata")
    p_create.set_defaults(func=cmd_create_skill)

    p_create_template = sub.add_parser("createskill_template", help="Create a standard skill scaffold")
    p_create_template.add_argument("name", help="Skill name")
    p_create_template.add_argument("base_dir", help="Skills root directory")
    p_create_template.set_defaults(func=cmd_create_skill_template)

    p_upload = sub.add_parser("uploadskill", help="Upload one skill to repository (default settings)")
    p_upload.add_argument("source", help="Skill name (Allskills) or local skill directory path")
    p_upload.set_defaults(func=cmd_upload_skill)

    p_delete = sub.add_parser("deleteskill", help="Delete a skill by one target (name or path)")
    p_delete.add_argument("target", help="Skill name or skill directory path")
    p_delete.set_defaults(func=cmd_delete_skill)

    p_show = sub.add_parser("showskill", help="Show all content for one skill from Allskills")
    p_show.add_argument("target", help="Skill name or skill directory path")
    p_show.set_defaults(func=cmd_show_skill)

    p_create_skills = sub.add_parser("createskills", help="Create a named skills collection")
    p_create_skills.add_argument("name", help="Skills instance name")
    p_create_skills.add_argument(
        "--skill-list",
        nargs="*",
        help="Specific skills (name or skill directory path) for this collection",
    )
    p_create_skills.add_argument("--paths", nargs="*", help="Custom paths for this collection")
    p_create_skills.add_argument("--tool-description", help="Tool description override")
    p_create_skills.add_argument("--agent-md-path", help="AGENTS.md path override")
    p_create_skills.set_defaults(func=cmd_create_skills)

    p_list_skills = sub.add_parser("listskills", help="List named skills collections")
    p_list_skills.add_argument("--json", action="store_true", help="JSON output")
    p_list_skills.set_defaults(func=cmd_list_skills_instances)

    p_load_skills = sub.add_parser("loadskills", help="Load registry from disk")
    p_load_skills.add_argument("path", nargs="?", help="Optional registry file path")
    p_load_skills.add_argument("--json", action="store_true", help="JSON output")
    p_load_skills.set_defaults(func=cmd_load_skills)

    p_delete_skills = sub.add_parser("deleteskills", help="Delete a named skills collection")
    p_delete_skills.add_argument("name", help="Skills instance name")
    p_delete_skills.set_defaults(func=cmd_delete_skills_instance)

    p_save_skills = sub.add_parser("saveskills", help="Persist registry to disk")
    p_save_skills.add_argument("path", nargs="?", help="Optional save output path")
    p_save_skills.set_defaults(func=cmd_save_skills)


    p_change_desc = sub.add_parser("changetooldescription", help="Update tool description on a skills collection")
    p_change_desc.add_argument("name", help="Skills instance name")
    p_change_desc.add_argument("description", help="New tool description")
    p_change_desc.set_defaults(func=cmd_change_tool_description)

    p_tool = sub.add_parser("skill-tool", help="Run skill_tool action")
    p_tool.add_argument("action", help="Action name")
    p_tool.add_argument("--arg", default="", help="Action argument")
    p_tool.add_argument("--name", help="Use a named skills instance")
    p_tool.set_defaults(func=cmd_skill_tool)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
