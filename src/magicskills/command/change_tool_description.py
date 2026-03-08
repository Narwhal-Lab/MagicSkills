"""Command implementation for updating tool description."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.skills import Skills


def change_tool_description(skills: Skills, description: str) -> None:
    """Update invocation text used in generated XML usage section."""
    from ..type.skillsregistry import REGISTRY

    skills.tool_description = description
    REGISTRY.saveskills()
