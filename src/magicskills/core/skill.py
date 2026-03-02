"""Single skill metadata model."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class Skill:
    """Single skill metadata and resolved filesystem context."""

    name: str
    description: str
    path: Path
    base_dir: Path
    source: Path
    context: str | None = None
    is_global: bool = False
    universal: bool = False
    environment: Mapping[str, str] = field(default_factory=dict)
    frontmatter: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize skill metadata to a JSON-friendly dict."""
        return {
            "name": self.name,
            "description": self.description,
            "context": self.context,
            "global": self.is_global,
            "universal": self.universal,
            "path": str(self.path),
            "baseDir": str(self.base_dir),
            "source": str(self.source),
            "location": "global" if self.is_global else "project",
            "environment": dict(self.environment),
            "frontmatter": dict(self.frontmatter),
        }
