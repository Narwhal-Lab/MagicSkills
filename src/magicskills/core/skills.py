"""Skills collection domain logic.

Includes discovery, read/exec operations, AGENTS.md sync, and tool-style
action dispatch compatible with Skill_For_All_Agent semantics.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from .agents_md import generate_skills_xml, replace_skills_section
from .models import ExecResult
from .skill import Skill
from .utils import (
    detect_location,
    extract_skill_metadata,
    get_search_dirs,
    is_directory_or_symlink_to_directory,
    normalize_paths,
    read_text,
)

DEFAULT_TOOL_DESCRIPTION = (
    'Unified skill tool. If you are not sure, you can first use the "list_metadata" '
    "function of this tool to search for available skills. Then, determine which skill "
    "might be the most useful. After that, try to read the SKILL.md file under this "
    "skill path to get more detailed information. Finally, based on the content of this "
    "file, decide whether to read the documentation in other paths or directly execute "
    "the relevant script."
)


@dataclass
class SkillReadResult:
    """Rendered read output that matches expected agent-facing format."""

    name: str
    base_dir: Path
    files: list[tuple[str, str]]

    def to_output(self) -> str:
        parts = [
            f"Reading: {self.name}",
            f"Base directory: {self.base_dir}",
            "",
        ]
        for rel_path, content in self.files:
            parts.append(f"File: {rel_path}")
            parts.append(content)
            parts.append("")
        parts.append(f"Skill read: {self.name}")
        return "\n".join(parts)


def _read_skill_files(base_dir: Path) -> list[tuple[str, str]]:
    """Read all files inside one skill directory in deterministic order."""
    files: list[tuple[str, str]] = []
    for file_path in sorted((p for p in base_dir.rglob("*") if p.is_file()), key=lambda p: p.as_posix()):
        rel_path = str(file_path.relative_to(base_dir))
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            size = file_path.stat().st_size
            content = f"[binary file omitted: {size} bytes]"
        except OSError as exc:
            content = f"[read error: {exc}]"
        files.append((rel_path, content))
    return files


def _format_skill_list(skills: list[Skill]) -> str:
    """Format skills for CLI list output."""
    if not skills:
        return "No skills found."
    ordered = sorted(skills, key=lambda s: (s.name.lower(), s.path.as_posix()))
    lines: list[str] = []
    for index, skill in enumerate(ordered, start=1):
        lines.append(f"{index}. name: {skill.name}")
        lines.append(f"   description: {skill.description}")
        lines.append(f"   path: {skill.path}")
    return "\n".join(lines)


def _format_show_skill_output(skill: Skill, files: list[tuple[str, str]]) -> str:
    """Format one skill's full content in a human-friendly layout."""
    line = "=" * 88
    split = "-" * 88
    lines = [
        line,
        f"Skill: {skill.name}",
        f"Description: {skill.description}",
        f"Base directory: {skill.base_dir}",
        f"SKILL.md path: {skill.path}",
        f"Source path: {skill.source}",
        split,
    ]

    if skill.environment:
        lines.append("Environment:")
        for key, value in sorted(skill.environment.items()):
            lines.append(f"  {key}={value}")
    else:
        lines.append("Environment: (none)")
    lines.append(split)

    lines.append(f"Files ({len(files)}):")
    for index, (rel_path, content) in enumerate(files, start=1):
        lines.append("")
        lines.append(f"[{index}/{len(files)}] {rel_path}")
        lines.append(split)
        lines.append(content if content else "(empty file)")

    lines.append("")
    lines.append(line)
    return "\n".join(lines)


def discover_skills(paths: Iterable[Path]) -> list[Skill]:
    """Scan paths and discover unique skills by resolved base_dir.

    Each path may be either:
    - a skills root containing multiple skill directories
    - a single skill directory that directly contains SKILL.md
    """
    skills: list[Skill] = []
    seen_base_dirs: set[Path] = set()

    for root in paths:
        if not root.exists():
            continue
        candidates: list[Path] = []
        if (root / "SKILL.md").exists() and is_directory_or_symlink_to_directory(root):
            candidates = [root]
        else:
            candidates = [entry for entry in root.iterdir() if is_directory_or_symlink_to_directory(entry)]

        for entry in candidates:
            if not is_directory_or_symlink_to_directory(entry):
                continue
            resolved_entry = entry.expanduser().resolve()
            if resolved_entry in seen_base_dirs:
                continue
            skill_md = entry / "SKILL.md"
            if not skill_md.exists():
                continue
            content = read_text(skill_md)
            frontmatter, description, context, environment = extract_skill_metadata(content)
            is_global, universal = detect_location(root)
            skills.append(
                Skill(
                    name=entry.name,
                    description=description,
                    path=skill_md,
                    base_dir=entry,
                    source=root,
                    context=context,
                    is_global=is_global,
                    universal=universal,
                    environment=environment,
                    frontmatter=frontmatter,
                )
            )
            seen_base_dirs.add(resolved_entry)

    return skills


class Skills:
    """A collection of skills with high-level operations."""

    def __init__(
        self,
        skills: Iterable[Skill] | None = None,
        paths: Iterable[Path | str] | None = None,
        tool_description: str | None = None,
        agent_md_path: Path | str | None = None,
        name: str = "all",
    ) -> None:
        self.name = name  # 该Skills的名字
        self.paths = normalize_paths(paths) if paths is not None else get_search_dirs() # 得到该skills对应的skill的所在路径
        self._skills = list(skills) if skills is not None else discover_skills(self.paths)
        self.tool_description = tool_description or DEFAULT_TOOL_DESCRIPTION
        self.agent_md_path = Path(agent_md_path) if agent_md_path else Path("AGENTS.md")

    @property
    def skills(self) -> list[Skill]:
        """Return a copy of internal skill list."""
        return list(self._skills) # 返回一个复制

    def get_skill(self, name: str, base_dir: Path | str | None = None) -> Skill:
        """Get one skill by name and optional base_dir.

        When multiple skills share the same name, `base_dir` is required.
        """
        if base_dir is not None:
            target_base_dir = Path(base_dir).expanduser().resolve()
            for skill in self._skills:
                if skill.name != name:
                    continue
                if skill.base_dir.expanduser().resolve() == target_base_dir:
                    return skill
            raise KeyError(f"Skill '{name}' not found at base_dir '{target_base_dir}'")

        matches = [skill for skill in self._skills if skill.name == name]
        if not matches:
            raise KeyError(f"Skill '{name}' not found")
        if len(matches) > 1:
            options = ", ".join(str(skill.base_dir) for skill in matches)
            raise KeyError(f"Multiple skills named '{name}' found. Provide base_dir. Candidates: {options}")
        return matches[0]

    def add_skill(self, skill: Skill) -> None:
        """Add one skill object into this collection.

        Uniqueness is based on `base_dir`, not only on name.
        """
        skill_base_dir = skill.base_dir.expanduser().resolve()
        if any(s.base_dir.expanduser().resolve() == skill_base_dir for s in self._skills):
            raise ValueError(f"Skill at base_dir '{skill.base_dir}' already exists in this collection")
        self._skills.append(skill)

    def remove_skill(self, name: str | None = None, base_dir: Path | str | None = None) -> None:
        """Remove one skill by base_dir or by unique name.

        If `name` matches multiple skills, pass `base_dir` to disambiguate.
        """
        if name is None and base_dir is None:
            raise ValueError("remove_skill requires at least one of: name, base_dir")

        if base_dir is not None:
            target_base_dir = Path(base_dir).expanduser().resolve()
            kept: list[Skill] = []
            removed = False
            for skill in self._skills:
                same_base_dir = skill.base_dir.expanduser().resolve() == target_base_dir
                same_name = name is None or skill.name == name
                if same_base_dir and same_name:
                    removed = True
                    continue
                kept.append(skill)
            if not removed:
                if name is None:
                    raise KeyError(f"Skill at base_dir '{target_base_dir}' not found")
                raise KeyError(f"Skill '{name}' not found at base_dir '{target_base_dir}'")
            self._skills = kept
            return

        assert name is not None
        matches = [skill for skill in self._skills if skill.name == name]
        if not matches:
            raise KeyError(f"Skill '{name}' not found")
        if len(matches) > 1:
            options = ", ".join(str(skill.base_dir) for skill in matches)
            raise ValueError(f"Multiple skills named '{name}' found. Provide base_dir. Candidates: {options}")
        target_base_dir = matches[0].base_dir.expanduser().resolve()
        self._skills = [skill for skill in self._skills if skill.base_dir.expanduser().resolve() != target_base_dir]

    def listskill(self) -> str:
        """Render available skills as simple text list."""
        return _format_skill_list(self._skills)

    def readskill(self, file_path: str | Path) -> str:
        """Read only the file content specified by path."""
        path = Path(file_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"readskill path not found: {path}")
        if not path.is_file():
            raise ValueError(f"readskill expects a file path, got: {path}")
        return read_text(path)

    def showskill(self, name: str, base_dir: Path | str | None = None) -> str:
        """Show one skill with beautified metadata + full file contents."""
        skill = self.get_skill(name, base_dir=base_dir)
        files = _read_skill_files(skill.base_dir)
        return _format_show_skill_output(skill, files)

    def _collection_environment(self) -> dict[str, str]:
        """Merge environment mappings from all skills in this collection."""
        merged: dict[str, str] = {}
        for collection_skill in sorted(self._skills, key=lambda s: s.base_dir.as_posix()):
            merged.update(collection_skill.environment)
        return merged

    def execskill(
        self,
        command: str,
        env: Mapping[str, str] | None = None,
        shell: bool = True,
        timeout: float | None = None,
        stream: bool = False,
    ) -> ExecResult:
        """Execute shell command in current cwd with merged collection environment variables."""
        if not command.strip():
            raise ValueError("execskill requires a command string")
        merged_env = os.environ.copy()
        merged_env.update(self._collection_environment())
        if env:
            merged_env.update(env)

        if shell:
            cmd = command
        else:
            cmd = shlex.split(command)
        if stream:
            completed = subprocess.run(
                cmd,
                shell=shell,
                cwd=Path.cwd(),
                env=merged_env,
                timeout=timeout,
            )
            return ExecResult(
                command=command,
                returncode=completed.returncode,
                stdout="",
                stderr="",
            )

        completed = subprocess.run(
            cmd,
            shell=shell,
            cwd=Path.cwd(),
            env=merged_env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return ExecResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    def change_tool_description(self, description: str) -> None:
        """Update invocation text used in generated XML usage section."""
        self.tool_description = description

    def syncskills(self, output_path: Path | str | None = None) -> Path:
        """Sync current skills collection into AGENTS.md content."""
        path = Path(output_path) if output_path else self.agent_md_path
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# AGENTS\n", encoding="utf-8")
        content = read_text(path)
        new_section = generate_skills_xml(self._skills, invocation=self.tool_description)
        updated = replace_skills_section(content, new_section)
        path.write_text(updated, encoding="utf-8")
        return path

    def skill_for_all_agent(self, action: str, arg: str = "") -> dict[str, object]:
        """Dispatch action/arg payload for agent tool compatibility."""
        try:
            action_lower = action.lower()
            if action_lower in {"listskill", "list", "list_metadata"}:
                return {"ok": True, "action": action, "result": self.listskill()}
            if action_lower in {"readskill", "read", "read_file"}:
                return {"ok": True, "action": action, "result": self.readskill(arg)}
            if action_lower in {"execskill", "exec", "run_command"}:
                command = _parse_exec_command(arg)
                result = self.execskill(command)
                return {"ok": True, "action": action, "result": result.__dict__}
            return {"ok": False, "error": f"Unknown action: {action}"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}


def _parse_exec_command(arg: str) -> str:
    """Parse command for execskill/run_command from plain text, JSON, or legacy `name::command`."""
    if not arg:
        raise ValueError("execskill requires a non-empty command")
    trimmed = arg.strip()
    if trimmed.startswith("{"):
        payload = json.loads(trimmed)
        command = payload.get("command")
        if not command:
            raise ValueError("execskill JSON must include 'command'")
        return str(command)
    if "::" in trimmed:
        _, command = trimmed.split("::", 1)
        command = command.strip()
        if not command:
            raise ValueError("execskill legacy arg requires command after '::'")
        return command
    return trimmed
