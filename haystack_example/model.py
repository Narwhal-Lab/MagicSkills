"""Haystack agent example — progressive skill disclosure.

Usage:
    uv run --with haystack-ai --with python-dotenv \
        python haystack_example/model.py

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import create_tool_from_function
from haystack.utils import Secret

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 1. 组装 Skills ─────────────────────────────────────────────
skill_a = ALL_SKILLS().get_skill("pdf")
skill_b = ALL_SKILLS().get_skill("c_2_ast")

my_skills = Skills(
    name="haystack_skills",
    skill_list=[skill_a, skill_b],
)


# ── 2. 包装为 Haystack tool ────────────────────────────────────
def skill_tool_fn(action: str, arg: str = "") -> str:
    """MagicSkills unified tool interface."""
    result = my_skills.skill_tool(action, arg)
    return json.dumps(result, ensure_ascii=False)


magic_skills_tool = create_tool_from_function(
    function=skill_tool_fn,
    name="skill_tool",
    description=my_skills.tool_description,
)


# ── 3. 构建 agent 并运行 ──────────────────────────────────────
if __name__ == "__main__":
    generator = OpenAIChatGenerator(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=Secret.from_token(os.getenv("OPENAI_API_KEY")),
        timeout=300.0,
    )

    agent = Agent(
        chat_generator=generator,
        tools=[magic_skills_tool],
        max_agent_steps=20,
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

    log_file = Path(__file__).parent / "haystack_result.log"
    try:
        result = agent.run(messages=[ChatMessage.from_user(prompt)])
        last_msg = result.get("last_message")
        log_content = last_msg.text if last_msg and last_msg.text else str(result)
        print(log_content[:2000])
    except BaseException:
        log_content = "[ERROR] Agent run interrupted or failed."
        raise
    finally:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_content or "[EMPTY]")
