"""Command implementation for showing one skill in detail."""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

from ..type.skill import Skill

if TYPE_CHECKING:
    from ..type.skills import Skills


def _supports_color() -> bool:
    """Best-effort detection for ANSI color support."""
    if os.environ.get("NO_COLOR"):
        return False
    term = os.environ.get("TERM", "").lower()
    if term in {"", "dumb"}:
        return False
    return sys.stdout.isatty()


def _read_skill_files(skill_dir: Path) -> list[tuple[str, str]]:
    """Read all files inside one skill directory in deterministic order."""
    files: list[tuple[str, str]] = []
    for file_path in sorted((p for p in skill_dir.rglob("*") if p.is_file()), key=lambda p: p.as_posix()):
        rel_path = str(file_path.relative_to(skill_dir))
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            size = file_path.stat().st_size
            content = f"[binary file omitted: {size} bytes]"
        except OSError as exc:
            content = f"[read error: {exc}]"
        files.append((rel_path, content))
    return files


def _format_show_skill_output(skill: Skill, files: list[tuple[str, str]]) -> str:
    """Format one skill's full content in a styled, readable layout."""
    width = 96
    color = _supports_color()
    lines: list[str] = []

    def paint(text: str, style: str) -> str:
        if not color:
            return text
        return f"\033[{style}m{text}\033[0m"

    def boxed(title: str, rows: list[str], style: str) -> list[str]:
        border = "+" + "-" * (width - 2) + "+"
        out = [paint(border, style)]
        title_text = f" {title} "
        out.append(paint("|" + title_text.ljust(width - 2) + "|", style))
        out.append(paint(border, style))
        for row in rows:
            wrapped = textwrap.wrap(row, width=width - 4) or [""]
            for chunk in wrapped:
                out.append(f"| {chunk.ljust(width - 4)} |")
        out.append(paint(border, style))
        return out

    lines.extend(
        boxed(
            "Skill Overview",
            [
                f"Skill: {skill.name}",
                f"Description: {skill.description}",
                f"Skill directory: {skill.path}",
                f"Skills root (base_dir): {skill.base_dir}",
                f"SKILL.md path: {skill.path / 'SKILL.md'}",
                f"Install source: {skill.source}",
            ],
            "1;36",
        )
    )
    lines.append("")

    lines.extend(boxed("Files", [f"Total files: {len(files)}"], "1;35"))

    divider = paint("-" * width, "90")
    for index, (rel_path, content) in enumerate(files, start=1):
        lines.append("")
        lines.extend(boxed(f"File {index}/{len(files)}: {rel_path}", [], "1;34"))
        lines.append(content if content else "(empty file)")
        lines.append(divider)

    return "\n".join(lines)


def showskill(
    skills: Skills,
    target: str | Path,
) -> str:
    """Show one skill with beautified metadata + full file contents."""
    skill = skills.get_skill(target)
    files = _read_skill_files(skill.path)
    return _format_show_skill_output(skill, files)
