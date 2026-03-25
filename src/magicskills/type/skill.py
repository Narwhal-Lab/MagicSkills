"""Single skill metadata model."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True) # 创建后不可以变
class Skill:
    """Single skill metadata and resolved filesystem context."""

    name: str
    description: str
    # Skill directory path (contains SKILL.md, references/, scripts/, assets/...)
    path: Path
    # Parent directory that contains the skill directory (skills root)
    base_dir: Path
    # Install/discovery source (repo URL or local source path)
    source: str
    is_global: bool = False
    universal: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize skill metadata to a JSON-friendly dict."""
        return {
            "name": self.name,
            "description": self.description,
            "global": self.is_global,
            "universal": self.universal,
            "path": str(self.path),
            "baseDir": str(self.base_dir),
            "source": self.source,
        }

    def scanskill(
        self,
        *,
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
        """Scan this skill directory with AI-Infra-Guard."""
        from ..command.scanskill import scanskill as command_scanskill

        return command_scanskill(
            self,
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
