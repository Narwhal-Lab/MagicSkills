"""Agent-compatible SkillTool wrapper.

This adapter keeps a small action-based API so LLM agents can call one tool
and dispatch to list/read/exec skill features.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.skills import Skills
from ..core.utils import get_search_dirs

DEFAULT_SKILLS_ROOT = str(Path.cwd() / ".claude" / "skills")


class SkillTool:
    """Single tool facade for agent frameworks."""

    def __init__(self, skills: Skills | None = None) -> None:
        self._skills = skills or Skills()
        self.skills_root: str | None = None

    def set_skills_root(self, root: str) -> None:
        """Override default skill root for this tool instance."""
        self.skills_root = root

    def _skills_for_request(self, arg: str | None = None) -> Skills:
        """Resolve which Skills collection should serve this request."""
        if arg:
            path = Path(arg)
            if path.exists():
                return Skills(paths=[path])
        if self.skills_root:
            path = Path(self.skills_root)
            if path.exists():
                return Skills(paths=[path])
        return self._skills

    def handle(self, payload: dict[str, Any]) -> dict[str, object]:
        """Handle action payload in shape: {'action': str, 'arg': str}."""
        action = str(payload.get("action", "")).strip()
        arg = str(payload.get("arg", "")).strip()

        if action.lower() in {"list_metadata", "listskill", "list"}:
            skills = self._skills_for_request(arg or None)
            return {"ok": True, "action": action, "result": skills.listskill()}

        if action.lower() in {"read_file", "readskill", "read"}:
            skills = self._skills_for_request(None)
            return skills.skill_for_all_agent("readskill", arg)

        if action.lower() in {"run_command", "execskill", "exec"}:
            skills = self._skills_for_request(None)
            return skills.skill_for_all_agent("execskill", arg)

        return {"ok": False, "error": f"Unknown action: {action}"}


def default_search_paths() -> list[str]:
    """Expose default skill search paths for diagnostics."""
    return [str(p) for p in get_search_dirs()]
