"""AutoGen agent example — progressive skill disclosure.

Usage:
    uv run --with autogen-agentchat --with "autogen-ext[openai]" --with python-dotenv \
        python autogen_example/model.py

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import asyncio
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core.models import ModelFamily
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 1. 组装 Skills ─────────────────────────────────────────────
skill_a = ALL_SKILLS.get_skill("pdf")
skill_b = ALL_SKILLS.get_skill("c_2_ast")

my_skills = Skills(
    name="autogen_skills",
    skill_list=[skill_a, skill_b],
)


# ── 2. 包装为 AutoGen FunctionTool ─────────────────────────────
async def skill_tool_fn(action: str, arg: str = "") -> str:
    """Unified skill tool interface for MagicSkills."""
    result = my_skills.skill_tool(action, arg)
    return json.dumps(result, ensure_ascii=False)


magic_skill_tool = FunctionTool(skill_tool_fn, description=my_skills.tool_description)


# ── 3. 构建 agent 并运行 ──────────────────────────────────────
async def main() -> None:
    model_client = OpenAIChatCompletionClient(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.GPT_4O,
            "structured_output": True,
        },
        temperature=0,
    )

    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[magic_skill_tool],
        system_message="Use tools to solve tasks. Always use the skill_tool_fn tool to perform actions. Do not stop until the task is complete.",
        reflect_on_tool_use=True,
    )

    # 任务设计：触发渐进式披露 (listskill → readskill → execskill)
    task = (
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

    log_file = Path(__file__).parent / "autogen_result.log"
    try:
        result = await Console(agent.run_stream(task=task), output_stats=True)
        log_content = str(result.messages)
    except BaseException:
        log_content = "[ERROR] Agent run interrupted or failed."
        raise
    finally:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_content)


if __name__ == "__main__":
    asyncio.run(main())
