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
    env_with_skill_context,
    extract_skill_metadata,
    get_search_dirs,
    is_directory_or_symlink_to_directory,
    normalize_paths,
    read_text,
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


def discover_skills(paths: Iterable[Path]) -> list[Skill]:
    """Scan paths and discover unique skills by folder name.

    Each path may be either:
    - a skills root containing multiple skill directories
    - a single skill directory that directly contains SKILL.md
    """
    skills: list[Skill] = []
    seen: set[str] = set()

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
            name = entry.name
            if name in seen:  # 万一有同名的但是内容不同的技能，先遇到的优先，那如果也要加入进去怎么办？
                continue
            skill_md = entry / "SKILL.md"
            if not skill_md.exists():
                continue
            content = read_text(skill_md)
            frontmatter, description, context, environment = extract_skill_metadata(content)
            is_global, universal, location = detect_location(root)
            skills.append(
                Skill(
                    name=name,
                    description=description,
                    path=skill_md,
                    base_dir=entry,
                    source=root,
                    context=context,
                    is_global=is_global,
                    universal=universal,
                    location=location,
                    environment=environment,
                    frontmatter=frontmatter,
                )
            )
            seen.add(name)

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
        self.tool_description = tool_description or "Skill_For_All_Agent(\"readskill <skill-name>\")"
        self.agent_md_path = Path(agent_md_path) if agent_md_path else Path("AGENTS.md")

    @property
    def skills(self) -> list[Skill]:
        """Return a copy of internal skill list."""
        return list(self._skills) # 返回一个复制

    def refresh(self) -> None:
        """Reload skills from configured paths."""
        self._skills = discover_skills(self.paths)

    def get_skill(self, name: str) -> Skill:
        """Get one skill by name or raise KeyError."""
        for skill in self._skills:
            if skill.name == name:
                return skill
        raise KeyError(f"Skill '{name}' not found")

    def add_skill(self, skill: Skill) -> None:
        """Add one skill object into this collection."""
        if any(s.name == skill.name for s in self._skills):
            raise ValueError(f"Skill '{skill.name}' already exists in this collection")
        self._skills.append(skill)

    def remove_skill(self, name: str) -> None:
        """Remove one skill by name from this collection."""
        before = len(self._skills)
        self._skills = [s for s in self._skills if s.name != name]
        if len(self._skills) == before:
            raise KeyError(f"Skill '{name}' not found")

    def listskill(self) -> str:
        """Render available skills as XML block."""
        return generate_skills_xml(self._skills, invocation=self.tool_description)

    def readskill(self, name: str) -> str:
        """Read and format all files under one skill directory."""
        skill = self.get_skill(name)
        files = _read_skill_files(skill.base_dir)
        return SkillReadResult(name=skill.name, base_dir=skill.base_dir, files=files).to_output()

    def execskill(
        self,
        name: str,
        command: str,
        env: Mapping[str, str] | None = None,
        shell: bool = True,
        timeout: float | None = None,
    ) -> ExecResult:
        """Execute shell command inside target skill context."""
        skill = self.get_skill(name)
        merged_env = env_with_skill_context(os.environ.copy(), skill.name, skill.base_dir, skill.path, skill.source)
        if env:
            merged_env.update(env)
        merged_env.update(skill.environment)

        if shell:
            cmd = command
        else:
            cmd = shlex.split(command)
        completed = subprocess.run(
            cmd,
            shell=shell,
            cwd=skill.base_dir,
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
                if arg and Path(arg).exists():
                    return {"ok": True, "action": action, "result": read_text(Path(arg))}
                return {"ok": True, "action": action, "result": self.readskill(arg)}
            if action_lower in {"execskill", "exec", "run_command"}:
                if action_lower == "run_command" and not _has_skill_prefix(arg):
                    result = _exec_plain(arg)
                    return {"ok": True, "action": action, "result": result.__dict__}
                name, command = _parse_exec_arg(arg)
                result = self.execskill(name, command)
                return {"ok": True, "action": action, "result": result.__dict__}
            return {"ok": False, "error": f"Unknown action: {action}"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}


def _parse_exec_arg(arg: str) -> tuple[str, str]:
    """Parse `execskill` arg from `name::command` or JSON."""
    if not arg:
        raise ValueError("execskill requires arg format: <skill-name>::<command> or JSON")
    trimmed = arg.strip()
    if trimmed.startswith("{"):
        payload = json.loads(trimmed)
        name = payload.get("name")
        command = payload.get("command")
        if not name or not command:
            raise ValueError("execskill JSON must include 'name' and 'command'")
        return str(name), str(command)
    if "::" in trimmed:
        name, command = trimmed.split("::", 1)
        return name.strip(), command.strip()
    raise ValueError("execskill requires arg format: <skill-name>::<command> or JSON")


def _has_skill_prefix(arg: str) -> bool:
    """Check if command arg explicitly includes skill prefix format."""
    trimmed = arg.strip()
    return trimmed.startswith("{") or "::" in trimmed


def _exec_plain(command: str) -> ExecResult:
    """Execute plain shell command in current working directory."""
    if not command.strip():
        raise ValueError("run_command requires a command string")
    completed = subprocess.run(
        command,
        shell=True,
        cwd=Path.cwd(),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )
    return ExecResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
