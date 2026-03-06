"""Command implementation for deleting named skills collections."""

from __future__ import annotations

from ..type.skillsregistry import REGISTRY


def deleteskills(name: str) -> None:
    """Delete a registered Skills collection by name."""
    REGISTRY.deleteskills(name)
