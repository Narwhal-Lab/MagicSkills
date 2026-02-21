"""Command-line interface for MagicSkills.

Each subcommand maps to exactly one concrete feature.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from .core.installer import (
    DEFAULT_SKILL_REPO,
    DEFAULT_SKILL_SUBDIR,
    create_skill,
    delete_skill,
    install_skills,
    show_skill,
    upload_skill,
)
from .core.registry import ALL_SKILLS, REGISTRY
from .core.skills import Skills
from .core.utils import normalize_paths


def _paths_from_args(values: Iterable[str] | None) -> list[Path] | None:
    """Normalize optional path arguments."""
    if not values:
        return None
    return normalize_paths(values)


def _skills_from_paths(paths: list[Path] | None) -> Skills:
    """Build a Skills collection from custom paths or the default Allskills instance."""
    return Skills(paths=paths) if paths else ALL_SKILLS


def cmd_list(args: argparse.Namespace) -> int:
    """List available skills."""
    _ = args
    print(ALL_SKILLS.listskill())
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    """Read all files under one skill directory from Allskills."""
    print(ALL_SKILLS.readskill(args.name))
    return 0


def cmd_exec(args: argparse.Namespace) -> int:
    """Execute one command in the selected skill context."""
    paths = _paths_from_args(args.paths)
    skills = _skills_from_paths(paths)
    command = " ".join(args.command).strip()
    if not command:
        raise SystemExit("exec requires command after --")
    result = skills.execskill(args.name, command, shell=not args.no_shell)
    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    else:
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    return result.returncode


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync skills XML section into AGENTS.md (or custom output)."""
    if args.name:
        skills = REGISTRY.get(args.name)
    else:
        paths = _paths_from_args(args.paths)
        skills = _skills_from_paths(paths)
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
    installed = install_skills(
        args.source,
        global_=args.global_scope,
        universal=args.universal,
        yes=args.yes,
        target_root=args.target,
    )
    ALL_SKILLS.refresh()
    for path in installed:
        print(f"Installed: {path}")
    return 0


def cmd_create_skill(args: argparse.Namespace) -> int:
    """Create one skill scaffold."""
    target_root = Path(args.root).expanduser() if args.root else None
    path = create_skill(args.name, target_root=target_root)
    ALL_SKILLS.refresh()
    print(f"Created: {path}")
    return 0


def cmd_upload_skill(args: argparse.Namespace) -> int:
    """Upload one skill from local directory or Allskills to target repository."""
    result = upload_skill(
        source=args.source,
        repo=args.repo,
        branch=args.branch,
        subdir=args.subdir,
        yes=args.yes,
        push=not args.no_push,
        commit_message=args.message,
    )
    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    else:
        print(f"Uploaded: {result.skill_name}")
        print(f"Repo: {result.repo}")
        print(f"Branch: {result.branch}")
        print(f"Target: {result.remote_subpath}")
        print(f"Committed: {result.committed}")
        print(f"Pushed: {result.pushed}")
    return 0


def cmd_delete_skill(args: argparse.Namespace) -> int:
    """Delete one installed skill from filesystem."""
    paths = _paths_from_args(args.paths)
    path = delete_skill(args.name, paths=paths)
    ALL_SKILLS.refresh()
    print(f"Deleted: {path}")
    return 0


def cmd_show_skill(args: argparse.Namespace) -> int:
    """Show metadata for one skill."""
    paths = _paths_from_args(args.paths)
    data = show_skill(args.name, paths=paths)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(data)
    return 0


def cmd_create_skills(args: argparse.Namespace) -> int:
    """Create one named skills collection instance."""
    paths = _paths_from_args(args.paths)
    path_values = [str(path) for path in paths] if paths else None
    instance = REGISTRY.create(name=args.name, paths=path_values)
    if args.tool_description:
        instance.change_tool_description(args.tool_description)
    if args.agent_md_path:
        instance.agent_md_path = Path(args.agent_md_path)
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

    if not names:
        print("No skills instances.")
        return 0
    for name in names:
        instance = REGISTRY.get(name)
        print(f"{name}\t{len(instance.skills)} skills\t{instance.agent_md_path}")
    return 0


def cmd_delete_skills_instance(args: argparse.Namespace) -> int:
    """Delete one named skills collection instance."""
    REGISTRY.delete(args.name)
    print(f"Deleted skills instance: {args.name}")
    return 0


def cmd_add_skill_to_instance(args: argparse.Namespace) -> int:
    """Attach the source path of a skill into a named collection."""
    instance = REGISTRY.get(args.name)
    source_paths = _paths_from_args(args.from_paths)
    source_skills = _skills_from_paths(source_paths)
    skill = source_skills.get_skill(args.skill_name)

    target_source = skill.source.expanduser().resolve()
    known_sources = {path.expanduser().resolve() for path in instance.paths}
    if target_source not in known_sources:
        instance.paths.append(skill.source)
    instance.refresh()
    REGISTRY.save_instance(args.name)
    print(f"Added '{skill.name}' to '{args.name}' (source path: {skill.source})")
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
        paths = _paths_from_args(args.paths)
        skills = _skills_from_paths(paths)
    result = skills.skill_for_all_agent(args.action, args.arg)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser with all supported commands."""
    parser = argparse.ArgumentParser(prog="magicskills")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("listskill", help="List skills from Allskills")
    p_list.set_defaults(func=cmd_list)

    p_read = sub.add_parser("readskill", help="Read all files for a skill from Allskills")
    p_read.add_argument("name", help="Skill name")
    p_read.set_defaults(func=cmd_read)

    p_exec = sub.add_parser("execskill", help="Execute command in skill environment")
    p_exec.add_argument("name", help="Skill name")
    p_exec.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --")
    p_exec.add_argument("--no-shell", action="store_true", help="Run without shell")
    p_exec.add_argument("--json", action="store_true", help="Output JSON result")
    p_exec.add_argument("--paths", nargs="*", help="Custom skill search paths")
    p_exec.set_defaults(func=cmd_exec)

    p_sync = sub.add_parser("syncskills", help="Sync skills into AGENTS.md")
    p_sync.add_argument("-o", "--output", help="Output path (default: AGENTS.md)")
    p_sync.add_argument("-y", "--yes", action="store_true", help="Non-interactive")
    p_sync.add_argument("--name", help="Use a named skills instance")
    p_sync.add_argument("--paths", nargs="*", help="Custom skill search paths")
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

    p_upload = sub.add_parser("uploadskill", help="Upload one skill to repository")
    p_upload.add_argument("source", help="Skill name (Allskills) or local skill directory path")
    p_upload.add_argument("--repo", default=DEFAULT_SKILL_REPO, help="Target repository")
    p_upload.add_argument("--subdir", default=str(DEFAULT_SKILL_SUBDIR), help="Target subdirectory inside repo")
    p_upload.add_argument("--branch", default="main", help="Target branch")
    p_upload.add_argument("--message", help="Commit message override")
    p_upload.add_argument("--no-push", action="store_true", help="Skip git push")
    p_upload.add_argument("--yes", action="store_true", help="Overwrite if skill exists in target repo")
    p_upload.add_argument("--json", action="store_true", help="JSON output")
    p_upload.set_defaults(func=cmd_upload_skill)

    p_delete = sub.add_parser("deleteskill", help="Delete a skill")
    p_delete.add_argument("name", help="Skill name")
    p_delete.add_argument("--paths", nargs="*", help="Custom skill search paths")
    p_delete.set_defaults(func=cmd_delete_skill)

    p_show = sub.add_parser("showskill", help="Show skill metadata")
    p_show.add_argument("name", help="Skill name")
    p_show.add_argument("--paths", nargs="*", help="Custom skill search paths")
    p_show.add_argument("--json", action="store_true", help="JSON output")
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

    p_add_skill = sub.add_parser("addskill2skills", help="Add a skill source path into a skills collection")
    p_add_skill.add_argument("name", help="Skills instance name")
    p_add_skill.add_argument("skill_name", help="Skill name to add")
    p_add_skill.add_argument("--from-paths", nargs="*", help="Custom source search paths")
    p_add_skill.set_defaults(func=cmd_add_skill_to_instance)

    p_change_desc = sub.add_parser("changetooldescription", help="Update tool description on a skills collection")
    p_change_desc.add_argument("name", help="Skills instance name")
    p_change_desc.add_argument("description", help="New tool description")
    p_change_desc.set_defaults(func=cmd_change_tool_description)

    p_tool = sub.add_parser("skill-for-all-agent", help="Run Skill_For_All_Agent action")
    p_tool.add_argument("action", help="Action name")
    p_tool.add_argument("--arg", default="", help="Action argument")
    p_tool.add_argument("--name", help="Use a named skills instance")
    p_tool.add_argument("--paths", nargs="*", help="Custom skill search paths")
    p_tool.set_defaults(func=cmd_skill_for_all_agent)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
