"""Template helper for ensuring one skill directory exists."""

from __future__ import annotations

from pathlib import Path


def createskill_template(name: str, base_dir: Path | str) -> Path:
    """Build `base_dir/name` and ensure default skill scaffold exists."""
    root = Path(base_dir).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "references").mkdir(exist_ok=True)
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "assets").mkdir(exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        skill_md.write_text(
            "---\n"
            f"name: {name}\n"
            "description:\n"
            "---\n\n"
            "# Overview\n\n"
            "Describe the skill here.\n",
            encoding="utf-8",
        )
    return skill_dir
