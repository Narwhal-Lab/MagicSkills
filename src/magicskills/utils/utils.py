"""Low-level utilities for path discovery and SKILL.md frontmatter parsing."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from ..type.skill import Skill
    from ..type.skills import Skills

FRONTMATTER_DELIM = "---"


def is_directory_or_symlink_to_directory(path: Path) -> bool:
    """Check path is directory or a symlink that resolves to directory."""
    if path.is_dir():
        return True
    if path.is_symlink():
        try:
            return path.resolve().is_dir()
        except OSError:
            return False
    return False


def read_text(path: Path) -> str:
    """Read UTF-8 text file."""
    return path.read_text(encoding="utf-8")


def _parse_simple_frontmatter(lines: list[str]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        raw = lines[i].rstrip("\n")
        line = raw.strip()
        i += 1
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_.-]+):\s*(.*)$", line)
        if not m:
            continue
        key = m.group(1)
        rest = m.group(2)
        if rest in ("|", ">"):
            block_lines: list[str] = []
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                block_lines.append(lines[i].lstrip())
                i += 1
            data[key] = "\n".join(block_lines).rstrip()
            continue
        if rest == "":
            # Possible nested mapping
            mapping: dict[str, str] = {}
            j = i
            while j < len(lines) and (lines[j].startswith("  ") or lines[j].startswith("\t")):
                sub = lines[j].strip()
                j += 1
                if not sub or sub.startswith("#"):
                    continue
                m2 = re.match(r"^([A-Za-z0-9_.-]+):\s*(.*)$", sub)
                if m2:
                    mapping[m2.group(1)] = m2.group(2).strip().strip('"').strip("'")
            if mapping:
                data[key] = mapping
                i = j
                continue
        data[key] = rest.strip().strip('"').strip("'")
    return data


def parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse a minimal YAML-like frontmatter block."""
    lines = content.splitlines() # 把整段文本按行切成列表，不保留换行符。
    if not lines: # 如果文本是空的，直接返回空字典。
        return {}
    if lines[0].strip() != FRONTMATTER_DELIM: # 如果第一行不是 ---（frontmatter 开始标记），就认为没有 frontmatter。
        return {}
    try:
        end_idx = lines[1:].index(FRONTMATTER_DELIM) + 1 # 从第二行开始找下一个 ---（结束标记）。+1 是把切片索引换回原始 lines 的索引。
    except ValueError:
        return {}
    fm_lines = lines[1:end_idx]
    return _parse_simple_frontmatter(fm_lines)


def extract_yaml_field(content: str, field: str, fm: dict[str, Any] | None = None) -> str:
    """Extract one scalar field from frontmatter.

    Passing parsed `fm` avoids reparsing the same content repeatedly.
    """
    parsed = fm if fm is not None else parse_frontmatter(content)
    value = parsed.get(field)
    if value is None:
        return ""
    if isinstance(value, dict):
        return ""
    return str(value)


def extract_environment(content: str, fm: dict[str, Any] | None = None) -> dict[str, str]:
    """Extract `environment` mapping from frontmatter.

    Passing parsed `fm` avoids reparsing the same content repeatedly.
    """
    parsed = fm if fm is not None else parse_frontmatter(content)
    env = parsed.get("environment")
    if isinstance(env, dict):
        return {str(k): str(v) for k, v in env.items()}
    return {}


def extract_skill_metadata(content: str) -> tuple[dict[str, Any], str, str | None, dict[str, str]]:
    """Extract frontmatter and key metadata with a single parse pass."""
    fm = parse_frontmatter(content)
    description = extract_yaml_field(content, "description", fm=fm)
    context = extract_yaml_field(content, "context", fm=fm) or None
    environment = extract_environment(content, fm=fm)
    return fm, description, context, environment


def detect_location(source: Path) -> tuple[bool, bool]:
    """Return (is_global, is_universal)."""
    home = Path.home().resolve()
    cwd = Path.cwd().resolve()
    source_resolved = source.expanduser().resolve()

    is_project = str(source_resolved).startswith(str(cwd))
    is_global = not is_project and str(source_resolved).startswith(str(home))
    is_universal = ".agent" in source.parts
    return is_global, is_universal


def normalize_paths(paths: Iterable[Path | str]) -> list[Path]:
    """Normalize user paths with `expanduser`."""
    result: list[Path] = []
    for p in paths:
        path = Path(p).expanduser()
        result.append(path)
    return result


def skill_paths_from_skills(skills: Iterable["Skill"]) -> list[Path]:
    """Build de-duplicated skill-directory paths in stable order."""
    result: list[Path] = []
    seen: set[Path] = set()
    for skill in skills:
        resolved = skill.path.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        result.append(skill.path)
    return result


def skill_paths_to_skills(paths: Iterable[Path | str]) -> list["Skill"]:
    """Resolve skill paths into discovered Skill objects.

    Each path may be either:
    - a skills root containing multiple skill directories
    - a single skill directory that directly contains SKILL.md
    """
    from ..type.skill import Skill

    skills: list[Skill] = []
    seen_paths: set[Path] = set()

    for root in normalize_paths(paths):
        if not root.exists():
            continue

        if (root / "SKILL.md").exists() and is_directory_or_symlink_to_directory(root):
            candidates = [root]
        else:
            candidates = [entry for entry in root.iterdir() if is_directory_or_symlink_to_directory(entry)]

        for entry in candidates:
            resolved_entry = entry.expanduser().resolve()
            if resolved_entry in seen_paths:
                continue

            skill_md = entry / "SKILL.md"
            if not skill_md.exists():
                continue

            content = read_text(skill_md)
            description = extract_yaml_field(content, "description")
            is_global, universal = detect_location(root)
            skills.append(
                Skill(
                    name=entry.name,
                    description=description,
                    path=entry,
                    base_dir=entry.parent,
                    source=str(root),
                    is_global=is_global,
                    universal=universal,
                )
            )
            seen_paths.add(resolved_entry)

    return skills





def is_git_url(source: str) -> bool:
    """Detect git SSH/HTTPS style source string."""
    return source.startswith("git@") or source.startswith("https://") or source.endswith(".git")


def is_repo_shorthand(source: str) -> bool:
    """Detect GitHub shorthand like `owner/repo`."""
    return bool(re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", source))


def expand_env_vars(value: str) -> str:
    """Expand shell-style environment variables in a string."""
    return os.path.expandvars(value)
