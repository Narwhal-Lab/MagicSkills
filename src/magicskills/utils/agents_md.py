"""AGENTS.md helpers for generating/replacing skills XML sections."""

from __future__ import annotations

import re
from typing import Iterable

from ..type.skill import Skill


SKILL_REGEX = re.compile(r"<skill>[\s\S]*?<name>([^<]+)</name>[\s\S]*?</skill>")
SKILLS_TABLE_START = "<!-- SKILLS_TABLE_START -->"
SKILLS_TABLE_END = "<!-- SKILLS_TABLE_END -->"


def parse_current_skills(content: str) -> list[str]:
    """Parse skill names already present in AGENTS.md content."""
    return [m.group(1).strip() for m in SKILL_REGEX.finditer(content)]


def _extract_marker_body(section: str) -> str | None:
    """Extract content inside the skills table markers."""
    regex = re.compile(
        rf"{re.escape(SKILLS_TABLE_START)}\n?(.*?)\n?{re.escape(SKILLS_TABLE_END)}",
        re.DOTALL,
    )
    match = regex.search(section)
    if not match:
        return None
    return match.group(1).strip("\n")


def generate_skills_xml(skills: Iterable[Skill], invocation: str) -> str:
    """Generate the `<skills_system>` XML block for AGENTS.md."""
    _ = invocation
    skill_tags = []
    for skill in skills:
        skill_tags.append(
            "<skill>\n"
            f"<name>{skill.name}</name>\n"
            f"<description>{skill.description}</description>\n"
            f"<path>{skill.path}</path>\n"
            "</skill>"
        )
    skills_block = "\n\n".join(skill_tags)

    return (
        "<skills_system priority=\"1\">\n\n"
        "## Available Skills\n\n"
        "<!-- SKILLS_TABLE_START -->\n"
        "<usage>\n"
        "When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively.\n\n"
        "How to use skills:\n"
        'Unified skill cli. If you are not sure, you can first use "magicskills listskill " '
        "to search for available skills. Then, determine which skill might be the most useful. "
        'After that, try to use "magicskills readskill <path>" to read the SKILL.md file under '
        "this skill path to get more detailed information. Finally, based on the content of this "
        'file, decide whether to read the documentation in other paths or use '
        '"magicskills execskill <command>" to directly execute the relevant script.\n\n'
        "Usage notes:\n"
        "- Only use skills listed in <available_skills> below\n"
        "- Do not invoke a skill that is already loaded in your context\n"
        "</usage>\n\n"
        "<available_skills>\n\n"
        f"{skills_block}\n\n"
        "</available_skills>\n"
        "<!-- SKILLS_TABLE_END -->\n\n"
        "</skills_system>"
    )


def replace_skills_section(content: str, new_section: str) -> str:
    """Replace existing skills section or append one if missing."""
    if "<skills_system" in content:
        regex = re.compile(r"<skills_system[^>]*>[\s\S]*?</skills_system>")
        return regex.sub(new_section, content)

    if SKILLS_TABLE_START in content:
        inner = _extract_marker_body(new_section)
        if inner is None:
            inner = re.sub(r"<skills_system[^>]*>|</skills_system>", "", new_section).strip("\n")
        regex = re.compile(rf"{re.escape(SKILLS_TABLE_START)}[\s\S]*?{re.escape(SKILLS_TABLE_END)}")
        return regex.sub(f"{SKILLS_TABLE_START}\n{inner}\n{SKILLS_TABLE_END}", content)

    return content.rstrip() + "\n\n" + new_section + "\n"


def remove_skills_section(content: str) -> str:
    """Remove skills section from AGENTS.md content."""
    if "<skills_system" in content:
        regex = re.compile(r"<skills_system[^>]*>[\s\S]*?</skills_system>")
        return regex.sub("<!-- Skills section removed -->", content)

    if SKILLS_TABLE_START in content:
        regex = re.compile(rf"{re.escape(SKILLS_TABLE_START)}[\s\S]*?{re.escape(SKILLS_TABLE_END)}")
        return regex.sub(f"{SKILLS_TABLE_START}\n<!-- Skills section removed -->\n{SKILLS_TABLE_END}", content)

    return content
