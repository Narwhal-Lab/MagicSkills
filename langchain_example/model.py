"""LangChain tool example for one Skills instance.

Usage:
    python langchain_example/model.py

Optional dependencies:
    pip install langchain-core pydantic
"""

from __future__ import annotations

import json
from typing import Sequence

from magicskills.core.skills import Skills


def create_skills_instance(name: str = "Askills", paths: Sequence[str] | None = None) -> Skills:
    """Create one Skills instance used by the LangChain tool."""
    return Skills(name=name, paths=paths)


def build_skill_tool(skills: Skills):
    """Build a LangChain StructuredTool that dispatches to `skills.skill_for_all_agent`.

    The returned tool accepts:
      - action: listskill/readskill/execskill/run_command...
      - arg: action payload string
    """
    try:
        from langchain_core.tools import StructuredTool
        from pydantic import BaseModel, Field
    except ImportError as exc:
        raise RuntimeError(
            "LangChain example requires `langchain-core` and `pydantic`. "
            "Install with: pip install langchain-core pydantic"
        ) from exc

    class SkillToolInput(BaseModel):
        action: str = Field(description="Action name, e.g. listskill/readskill/execskill.")
        arg: str = Field(default="", description="Action argument string.")

    def _run(action: str, arg: str = "") -> str:
        result = skills.skill_for_all_agent(action, arg)
        return json.dumps(result, ensure_ascii=False)

    return StructuredTool.from_function(
        func=_run,
        name="Skill_For_All_Agent",
        description=(
            "Dispatch skills actions on one Skills instance. "
            "Use action=listskill/readskill/execskill, and put payload in arg."
        ),
        args_schema=SkillToolInput,
    )


if __name__ == "__main__":
    askills = create_skills_instance()
    tool = build_skill_tool(askills)
    print(tool.invoke({"action": "listskill", "arg": ""}))
