"""Command implementation for reading one skill file."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..utils.utils import read_text

if TYPE_CHECKING:
    from ..type.skills import Skills


def readskill(skills: Skills, target: str | Path) -> str:
    """Read file content by explicit path or by skill name (reads that skill's SKILL.md)."""
    raw = str(target).strip()
    path = Path(raw).expanduser()
    explicit_path = "/" in raw or "\\" in raw or raw.startswith(".") or raw.startswith("~")

    if path.exists():
        if not path.is_file():
            raise ValueError(f"readskill expects a file path, got: {path}")
        return read_text(path)

    if explicit_path:
        raise FileNotFoundError(f"readskill path not found: {path}")

    try:
        skill = skills.get_skill(raw)
    except KeyError as exc:
        message = str(exc)
        if "Multiple skills named" in message:
            raise ValueError(
                f"readskill: skill name '{raw}' is duplicated; please pass an explicit file path "
                f"(for example: <skill-path>/SKILL.md).\n{message}"
            ) from exc
        raise FileNotFoundError(f"readskill target not found: {raw}") from exc
    return read_text(skill.path / "SKILL.md")
