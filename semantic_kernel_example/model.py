"""Semantic Kernel agent example — progressive skill disclosure.

Usage:
    uv run --with semantic-kernel --with python-dotenv \
        python semantic_kernel_example/model.py

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

from dotenv import load_dotenv
from openai import AsyncOpenAI
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import kernel_function

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 1. 组装 Skills ─────────────────────────────────────────────
skill_a = ALL_SKILLS.get_skill("pdf")
skill_b = ALL_SKILLS.get_skill("c_2_ast")

my_skills = Skills(
    name="semantic_kernel_skills",
    skill_list=[skill_a, skill_b],
)


# ── 2. 包装为 Semantic Kernel Plugin ──────────────────────────
class MagicSkillsPlugin:
    def __init__(self, skills_instance: Skills) -> None:
        self.skills = skills_instance

    @kernel_function(
        name="skill_tool",
        description=my_skills.tool_description,
    )
    async def call_skill_tool(self, action: str, arg: str = "") -> str:
        """Unified skill tool interface for MagicSkills."""
        result = self.skills.skill_tool(action, arg)
        return json.dumps(result, ensure_ascii=False)


# ── 3. 构建 agent 并运行 ──────────────────────────────────────
async def main() -> None:
    chat_service = OpenAIChatCompletion(
        ai_model_id=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        async_client=AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        ),
    )

    agent = ChatCompletionAgent(
        service=chat_service,
        instructions=(
            "You are a helpful assistant. Use the provided tools to solve tasks step by step. "
            "Always use function calls to invoke tools. Never output raw XML or markup. "
            "Complete all steps: listskill, readskill, execskill."
        ),
        plugins=[MagicSkillsPlugin(my_skills)],
    )

    # 任务设计：触发渐进式披露 (listskill → readskill → execskill)
    prompt = (
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

    log_file = Path(__file__).parent / "semantic_kernel_result.log"
    try:
        response = await agent.get_response(messages=prompt)
        print(response.content)
        log_content = str(response.content)
    except BaseException:
        log_content = "[ERROR] Agent run interrupted or failed."
        raise
    finally:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_content)


if __name__ == "__main__":
    asyncio.run(main())
