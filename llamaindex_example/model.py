"""LlamaIndex ReAct agent example — progressive skill disclosure.

Usage:
    uv run --with llama-index-core --with llama-index-llms-openai-like --with python-dotenv \
        python llamaindex_example/model.py

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
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai_like import OpenAILike

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 1. 组装 Skills ─────────────────────────────────────────────
skill_a = ALL_SKILLS().get_skill("pdf")
skill_b = ALL_SKILLS().get_skill("c_2_ast")

my_skills = Skills(
    name="llamaindex_skills",
    skill_list=[skill_a, skill_b],
)


# ── 2. 包装为 LlamaIndex tool ─────────────────────────────────
def skill_tool_fn(action: str, arg: str = "") -> str:
    """MagicSkills unified tool interface."""
    result = my_skills.skill_tool(action, arg)
    return json.dumps(result, ensure_ascii=False)


skill_tool = FunctionTool.from_defaults(
    fn=skill_tool_fn,
    name="skill_tool",
    description=my_skills.tool_description,
)


# ── 3. 构建 agent 并运行 ──────────────────────────────────────
async def main() -> None:
    llm = OpenAILike(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_BASE_URL"),
        is_chat_model=True,
        is_function_calling_model=True,
    )

    agent = ReActAgent(llm=llm, tools=[skill_tool])

    # 任务设计：触发渐进式披露 (listskill → readskill → execskill)
    log_file = Path(__file__).parent / "llamaindex_result.log"
    try:
        response = await agent.run(
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
        print(response)
        log_content = str(response)
    except BaseException:
        log_content = "[ERROR] Agent run interrupted or failed."
        raise
    finally:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_content)


if __name__ == "__main__":
    asyncio.run(main())
