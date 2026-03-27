"""Command implementation for scanning all skills in one collection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

from .scanskill import scanskill as command_scanskill
from ..utils.ai_infra_guard import AIInfraGuardConfig, resolve_ai_infra_guard_config

if TYPE_CHECKING:
    from ..type.skills import Skills


def scanskills(
    skills: Skills,
    *,
    config: AIInfraGuardConfig | None = None,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    token: str | None = None,
    model_base_url: str | None = None,
    prompt: str | None = None,
    language: str | None = None,
    thread: int | None = None,
    poll_interval: float | None = None,
    timeout: float | None = None,
    headers: Mapping[str, str] | None = None,
) -> dict[str, object]:
    """Scan every skill in one Skills collection and aggregate the results."""
    resolved_config = config or resolve_ai_infra_guard_config(
        base_url=base_url,
        model=model,
        api_key=api_key,
        token=token,
        model_base_url=model_base_url,
        prompt=prompt,
        language=language,
        thread=thread,
        poll_interval=poll_interval,
        timeout=timeout,
        headers=headers,
    )

    results: list[dict[str, object]] = []
    for skill in skills.skills:
        try:
            results.append(command_scanskill(skill, config=resolved_config))
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "ok": False,
                    "skill_name": skill.name,
                    "skill_path": str(skill.path.expanduser().resolve()),
                    "error": str(exc),
                }
            )

    succeeded = sum(1 for item in results if item.get("ok"))
    failed = len(results) - succeeded
    return {
        "ok": failed == 0,
        "collection_name": skills.name,
        "total_skills": len(results),
        "succeeded": succeeded,
        "failed": failed,
        "results": results,
    }


__all__ = ["scanskills"]
