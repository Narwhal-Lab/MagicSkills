"""Shared data models for core operations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .skill import Skill  # Backward-compatible import path.


@dataclass(frozen=True)
class ExecResult:
    command: str
    returncode: int
    stdout: str
    stderr: str


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
