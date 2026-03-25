"""Public API surface for MagicSkills."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from .command.addskill import addskill
from .command.addskills import addskills
from .command.change_cli_description import change_cli_description
from .command.change_tool_description import change_tool_description
from .command.createskill_template import createskill_template
from .command.deleteskill import deleteskill
from .command.deleteskills import deleteskills
from .command.execskill import execskill
from .command.install import install
from .command.listskill import listskill
from .command.listskills import listskills
from .command.loadskills import loadskills
from .command.readskill import readskill
from .command.scanskill import scanskill
from .command.scanskills import scanskills
from .command.saveskills import saveskills
from .command.showskill import showskill
from .command.skill_tool import skill_tool
from .command.syncskills import syncskills
from .command.uploadskill import uploadskill
from .type.skill import Skill
from .type.skills import Skills
from .type.skillsregistry import ALL_SKILLS, REGISTRY


__version__ = "1.1.0"

DEFAULT_SKILLS_ROOT = Path.cwd() / ".claude" / "skills"
changeclidescription = change_cli_description
changetooldescription = change_tool_description

__all__ = [
    "addskill",
    "addskills",
    "Skill",
    "Skills",
    "REGISTRY",
    "ALL_SKILLS",
    "DEFAULT_SKILLS_ROOT",
    "change_cli_description",
    "change_tool_description",
    "createskill_template",
    "deleteskill",
    "deleteskills",
    "execskill",
    "install",
    "listskill",
    "listskills",
    "readskill",
    "scanskill",
    "scanskills",
    "showskill",
    "skill_tool",
    "syncskills",
    "uploadskill",
    "loadskills",
    "saveskills",
    "changeclidescription",
    "changetooldescription",
    "install",
]
