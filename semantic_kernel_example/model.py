"""Semantic Kernel function-calling example — progressive skill disclosure.

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
from typing import Any
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import AsyncOpenAI
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import kernel_function

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 1. 组装 Skills ─────────────────────────────────────────────
skill_a = ALL_SKILLS().get_skill("pdf")
skill_b = ALL_SKILLS().get_skill("c_2_ast")

my_skills = Skills(
    name="semantic_kernel_skills",
    skill_list=[skill_a, skill_b],
)


# ── 2. 包装为 Semantic Kernel plugin ──────────────────────────
def build_skill_tool_plugin(skills: Skills) -> object:
    class MagicSkillsPlugin:
        @kernel_function(
            name="skill_tool",
            description=skills.tool_description,
        )
        async def skill_tool(self, action: str, arg: str = "") -> str:
            return json.dumps(skills.skill_tool(action, arg), ensure_ascii=False)

    return MagicSkillsPlugin()


def _dump_payload(value: Any) -> str:
    if hasattr(value, "model_dump"):
        data = value.model_dump(mode="json")
    else:
        data = value
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def _record_message(log_lines: list[str], header: str, payload: Any) -> None:
    body = _dump_payload(payload)
    print(header)
    print(body)
    log_lines.extend([header, body])


# ── 3. 构建 agent 并运行 ──────────────────────────────────────
async def main() -> None:
    chat_service = OpenAIChatCompletion(
        ai_model_id=os.getenv("OPENAI_MODEL"),
        async_client=AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        ),
    )

    agent = ChatCompletionAgent(
        service=chat_service,
        plugins=[build_skill_tool_plugin(my_skills)],
    )

    prompt = (
        "Please help me convert the following C code into an AST.\n"
        "First discover what skills are available, then read the relevant "
        "skill instructions, and finally execute the conversion.\n\n"
        "```c\n"
        "#include <stdio.h>\n\n"
        "int main() {\n"
        '    puts("Hello from agent");\n'
        "    return 0;\n"
        "}\n"
        "```"
    )

    log_lines: list[str] = []
    log_file = Path(__file__).parent / "semantic_kernel_result.log"
    response_count = 0
    final_text = "[EMPTY]"

    async def on_intermediate_message(message: Any) -> None:
        header = f"\n--- intermediate | {type(message).__name__} ---"
        _record_message(log_lines, header, message)

    try:
        async for response in agent.invoke(
            messages=prompt,
            on_intermediate_message=on_intermediate_message,
        ):
            response_count += 1
            header = f"\n--- final_response | {response_count} ---"
            _record_message(log_lines, header, response.message)
            final_text = str(response.content)

        footer = "\n=== final ==="
        print(footer)
        print(final_text)
        log_lines.extend([footer, final_text])
    finally:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))


if __name__ == "__main__":
    asyncio.run(main())
