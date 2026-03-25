"""Command implementation for scanning one skill with AI-Infra-Guard."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from ..type.skill import Skill
from ..utils.ai_infra_guard import (
    AIInfraGuardConfig,
    resolve_ai_infra_guard_config,
    scan_skill_directory,
)


def _resolve_scan_target(target: Skill | Path | str) -> tuple[str, Path]:
    if isinstance(target, Skill):
        return target.name, target.path.expanduser().resolve()

    raw_target = str(target).strip()
    if not raw_target:
        raise ValueError("scanskill requires a Skill object or skill directory path")

    skill_dir = Path(raw_target).expanduser().resolve()
    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")
    if not skill_dir.is_dir():
        raise ValueError(f"scanskill expects a skill directory, got file: {skill_dir}")
    if not (skill_dir / "SKILL.md").exists():
        raise FileNotFoundError(f"Skill directory is invalid (missing SKILL.md): {skill_dir}")
    return skill_dir.name, skill_dir


def scanskill(
    target: Skill | Path | str,
    *,
    config: AIInfraGuardConfig | None = None,
    base_url: str | None = None,
    model: str | None = None,
    token: str | None = None,
    model_base_url: str | None = None,
    prompt: str | None = None,
    language: str | None = None,
    thread: int | None = None,
    poll_interval: float | None = None,
    timeout: float | None = None,
    headers: Mapping[str, str] | None = None,
) -> dict[str, object]:
    """Scan one skill with AI-Infra-Guard."""
    skill_name, skill_dir = _resolve_scan_target(target)
    resolved_config = config or resolve_ai_infra_guard_config(
        base_url=base_url,
        model=model,
        token=token,
        model_base_url=model_base_url,
        prompt=prompt,
        language=language,
        thread=thread,
        poll_interval=poll_interval,
        timeout=timeout,
        headers=headers,
    )
    return scan_skill_directory(skill_dir, skill_name=skill_name, config=resolved_config)


__all__ = ["scanskill"]
