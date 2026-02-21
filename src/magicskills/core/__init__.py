"""Core domain layer for MagicSkills."""

from .installer import UploadResult, create_skill, delete_skill, install_skills, show_skill, upload_skill
from .models import ExecResult
from .registry import REGISTRY, SkillsRegistry
from .skill import Skill
from .skills import Skills, discover_skills

__all__ = [
    "Skill",
    "Skills",
    "discover_skills",
    "ExecResult",
    "SkillsRegistry",
    "REGISTRY",
    "install_skills",
    "upload_skill",
    "UploadResult",
    "create_skill",
    "delete_skill",
    "show_skill",
]
