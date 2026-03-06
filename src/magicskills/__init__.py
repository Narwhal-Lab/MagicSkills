"""Public API surface for MagicSkills."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from .command.change_tool_description import change_tool_description
from .command.createskill import createskill
from .command.createskill_template import createskill_template
from .command.createskills import createskills
from .command.deleteskill import deleteskill
from .command.deleteskills import deleteskills
from .command.execskill import execskill
from .command.install import install
from .command.listskill import listskill
from .command.listskills import listskills
from .command.readskill import readskill
from .command.showskill import showskill
from .command.skill_tool import skill_tool
from .command.syncskills import syncskills
from .command.uploadskill import uploadskill
from .type.skill import Skill
from .type.skills import Skills
from .type.skillsregistry import ALL_SKILLS, REGISTRY, SkillsRegistry


__version__ = "0.1.0"

DEFAULT_SKILLS_ROOT = Path.cwd() / ".claude" / "skills"

__all__ = [
    "Skill",
    "Skills",
    "SkillsRegistry",
    "REGISTRY",
    "ALL_SKILLS",
    "DEFAULT_SKILLS_ROOT",
    "change_tool_description",
    "createskill",
    "createskill_template",
    "createskills",
    "deleteskill",
    "deleteskills",
    "execskill",
    "install",
    "listskill",
    "listskills",
    "readskill",
    "showskill",
    "skill_tool",
    "syncskills",
    "uploadskill",
    "loadskills",
    "saveskills",
    "changetooldescription",
    "install",
]
