"""Persistent registry for named Skills collections."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .skill import Skill
from .skills import Skills, discover_skills
from .utils import normalize_paths


REGISTRY_DIRNAME = ".magicskills"
REGISTRY_FILENAME = "collections.json"


def _default_store_path() -> Path:
    """Default per-project path for collection registry storage."""
    return Path.cwd() / REGISTRY_DIRNAME / REGISTRY_FILENAME


class SkillsRegistry:
    """Named Skills collection registry with JSON persistence."""

    def __init__(self, store_path: Path | None = None) -> None:
        self._instances: dict[str, Skills] = {}
        self._store_path = store_path or _default_store_path()
        self._load()

    def _load(self) -> None:
        """Load collections from disk if registry file exists."""
        if not self._store_path.exists():
            return
        try:
            content = self._store_path.read_text(encoding="utf-8")
            payload: dict[str, Any] = json.loads(content)
        except (OSError, json.JSONDecodeError):
            return
        collections = payload.get("collections", {})
        if not isinstance(collections, dict):
            return
        for name, spec in collections.items():
            if not isinstance(name, str) or not isinstance(spec, dict):
                continue
            path_values = spec.get("paths", [])
            tool_description = spec.get("tool_description")
            agent_md_path = spec.get("agent_md_path")
            paths = normalize_paths(path_values) if isinstance(path_values, list) else None
            instance = Skills(
                name=name,
                paths=paths,
                tool_description=tool_description if isinstance(tool_description, str) else None,
                agent_md_path=agent_md_path if isinstance(agent_md_path, str) else None,
            )
            self._instances[name] = instance

    def _serialize(self) -> dict[str, object]:
        """Serialize registry state to JSON-friendly dict."""
        collections: dict[str, dict[str, object]] = {}
        for name, instance in self._instances.items():
            collections[name] = {
                "paths": [str(path) for path in instance.paths],
                "tool_description": instance.tool_description,
                "agent_md_path": str(instance.agent_md_path),
            }
        return {"collections": collections}

    def _save(self) -> None:
        """Persist current registry state to disk."""
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._store_path.write_text(
            json.dumps(self._serialize(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def create(self, name: str, skills: Iterable[Skill] | None = None, paths: Iterable[str] | None = None) -> Skills:
        """Create and register one named Skills collection."""
        if name in self._instances:
            raise ValueError(f"Skills instance '{name}' already exists")
        if skills is None:
            if paths is None:
                instance = Skills(name=name)
            else:
                path_list = normalize_paths(paths)
                instance = Skills(name=name, paths=path_list, skills=discover_skills(path_list))
        else:
            instance = Skills(name=name, skills=list(skills))
        self._instances[name] = instance
        self._save()
        return instance

    def list(self) -> list[str]:
        """List collection names."""
        return sorted(self._instances.keys())

    def get(self, name: str) -> Skills:
        """Get one named collection."""
        if name not in self._instances:
            raise KeyError(f"Skills instance '{name}' not found")
        return self._instances[name]

    def delete(self, name: str) -> None:
        """Delete one named collection and persist change."""
        if name not in self._instances:
            raise KeyError(f"Skills instance '{name}' not found")
        del self._instances[name]
        self._save()

    def save_instance(self, name: str) -> None:
        """Persist registry after in-place mutation of one collection."""
        if name not in self._instances:
            raise KeyError(f"Skills instance '{name}' not found")
        self._save()


REGISTRY = SkillsRegistry()
ALL_SKILLS = Skills(name="Allskills")
