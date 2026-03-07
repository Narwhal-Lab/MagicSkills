"""LangChain tool-binding example — progressive skill disclosure.

Usage:
    pip install langchain-openai python-dotenv
    python langchain_example/model.py

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 1. 组装 Skills ─────────────────────────────────────────────
skill_a = ALL_SKILLS.get_skill("pdf")
skill_b = ALL_SKILLS.get_skill("c_2_ast")

my_skills = Skills(
    name="langchain_skills",
    skill_list=[skill_a, skill_b],
)

# ── 2. 包装为 LangChain tool ───────────────────────────────────
@tool("skill_tool", description=my_skills.tool_description)
def _skill_tool(action: str, arg: str = "") -> str:
    return json.dumps(my_skills.skill_tool(action, arg), ensure_ascii=False)


# ── 3. 多轮 tool-calling loop ─────────────────────────────────
def run_once(prompt: str) -> None:
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.0,
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    llm_with_tools = llm.bind_tools([_skill_tool])

    messages: list = [("user", prompt)]
    log_lines: list[str] = []

    while True:
        msg = llm_with_tools.invoke(messages)
        messages.append(msg)

        header = f"[AI] content={msg.content[:200] if msg.content else ''}"
        print(header)
        log_lines.append(header)

        if not getattr(msg, "tool_calls", None):
            break

        for tc in msg.tool_calls:
            tc_info = f"  -> tool_call: {tc['name']}({tc['args']})"
            print(tc_info)
            log_lines.append(tc_info)

            tool_result = _skill_tool.invoke(tc["args"])
            result_info = f"  <- result: {tool_result[:300]}"
            print(result_info)
            log_lines.append(result_info)

            messages.append(ToolMessage(content=tool_result, tool_call_id=tc["id"]))

    print("\n=== final ===")
    print(msg.content)
    log_lines.append(f"\n=== final ===\n{msg.content}")

    log_file = Path(__file__).parent / "langchain_result.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))


if __name__ == "__main__":
    # 任务设计：触发渐进式披露 (listskill → readskill → execskill)
    run_once(
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
