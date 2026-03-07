"""Hugging Face smolagents example — progressive skill disclosure.

Usage:
    pip install 'smolagents[litellm]' python-dotenv
    python transformers_smolagents_example/model.py

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel, Tool

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 1. 组装 Skills ─────────────────────────────────────────────
skill_a = ALL_SKILLS.get_skill("pdf")
skill_b = ALL_SKILLS.get_skill("c_2_ast")

my_skills = Skills(
    name="smolagents_skills",
    skill_list=[skill_a, skill_b],
)


# ── 2. 包装为 smolagents Tool ─────────────────────────────────
class MagicSkillsTool(Tool):
    name = "skill_tool"
    description = my_skills.tool_description
    inputs = {
        "action": {
            "type": "string",
            "description": "The action to perform (listskill / readskill / execskill)",
        },
        "arg": {
            "type": "string",
            "description": "The argument for the action",
        },
    }
    output_type = "string"

    def __init__(self, skills_instance: Skills) -> None:
        super().__init__()
        self.skills = skills_instance

    def forward(self, action: str, arg: str = "") -> str:
        result = self.skills.skill_tool(action.strip(), arg.strip())
        return json.dumps(result, ensure_ascii=False)


magic_skills_tool = MagicSkillsTool(my_skills)


# ── 3. 构建 agent 并运行 ──────────────────────────────────────
if __name__ == "__main__":
    model = LiteLLMModel(
        model_id=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_base=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    agent = CodeAgent(
        tools=[magic_skills_tool],
        model=model,
    )

    # 任务设计：触发渐进式披露 (listskill → readskill → execskill)
    result = agent.run(
        "Please help me convert the following C code into an AST.\n"
        "First discover what skills are available, then read the relevant "
        "skill instructions, and finally execute the conversion.\n\n"
        "```c\n"
        "#include <stdio.h>\n\n"
        "int main() {\n"
        '    puts(\"Hello from agent\");\n'
        "    return 0;\n"
        "}\n"
        "```"
    )
    print(result)

    log_file = Path(__file__).parent / "smolagents_result.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(str(result))
