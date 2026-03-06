from ..type.skillsregistry import  REGISTRY
from ..type.skills import Skills
from pathlib import Path

def loadskills(path: str | None = None) -> list[Skills]:
    """Load registry state from disk."""
    return REGISTRY.loadskills(Path(path).expanduser() if path else None)