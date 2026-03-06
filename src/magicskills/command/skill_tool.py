"""Command implementation for skill_tool action dispatch."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .execskill import parse_exec_command

if TYPE_CHECKING:
    from ..type.skills import Skills


def skill_tool(skills: Skills, action: str, arg: str = "") -> dict[str, object]:
    """Dispatch action/arg payload for agent tool compatibility."""
    try:
        action_lower = action.lower()
        if action_lower in {"listskill", "list", "list_metadata"}:
            return {"ok": True, "action": action, "result": skills.listskill()}
        if action_lower in {"readskill", "read", "read_file"}:
            return {"ok": True, "action": action, "result": skills.readskill(arg)}
        if action_lower in {"execskill", "exec", "run_command"}:
            command = parse_exec_command(arg)
            result = skills.execskill(command)
            return {"ok": True, "action": action, "result": result.__dict__}
        return {"ok": False, "error": f"Unknown action: {action}"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}
