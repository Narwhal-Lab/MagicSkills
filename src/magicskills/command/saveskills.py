from ..type.skillsregistry import  REGISTRY
from ..type.skills import Skills
from pathlib import Path

def saveskills(path: str | None = None) -> str:
    """Persist registry state to disk."""
    return str(REGISTRY.saveskills(Path(path).expanduser() if path else None))