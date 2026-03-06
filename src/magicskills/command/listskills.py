"""Command implementation for listing named skills collections."""

from __future__ import annotations

from ..type.skillsregistry import REGISTRY
from ..type.skills import Skills


def listskills() -> list[Skills]:
    """List all registered Skills collection names."""
    return REGISTRY.listskills()
