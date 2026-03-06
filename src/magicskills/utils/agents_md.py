"""AGENTS.md helpers for generating/replacing skills XML sections."""

from __future__ import annotations

import re
from typing import Iterable

from ..type.skill import Skill


SKILL_REGEX = re.compile(r"<skill>[\s\S]*?<name>([^<]+)</name>[\s\S]*?</skill>")


def parse_current_skills(content: str) -> list[str]:
    """Parse skill names already present in AGENTS.md content."""
    return [m.group(1).strip() for m in SKILL_REGEX.finditer(content)]


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
        "- Invoke: `magicskills readskill <path>` (run in your shell)\n"
        "- The skill content will load with detailed instructions\n"
        "- Base directory provided in output for resolving bundled resources\n\n"
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

    html_start = "<!-- SKILLS_TABLE_START -->"
    html_end = "<!-- SKILLS_TABLE_END -->"
    if html_start in content:
        inner = re.sub(r"<skills_system[^>]*>|</skills_system>", "", new_section)
        regex = re.compile(rf"{re.escape(html_start)}[\s\S]*?{re.escape(html_end)}")
        return regex.sub(f"{html_start}\n{inner}\n{html_end}", content)

    return content.rstrip() + "\n\n" + new_section + "\n"


def remove_skills_section(content: str) -> str:
    """Remove skills section from AGENTS.md content."""
    if "<skills_system" in content:
        regex = re.compile(r"<skills_system[^>]*>[\s\S]*?</skills_system>")
        return regex.sub("<!-- Skills section removed -->", content)

    html_start = "<!-- SKILLS_TABLE_START -->"
    html_end = "<!-- SKILLS_TABLE_END -->"
    if html_start in content:
        regex = re.compile(rf"{re.escape(html_start)}[\s\S]*?{re.escape(html_end)}")
        return regex.sub(f"{html_start}\n<!-- Skills section removed -->\n{html_end}", content)

    return content
