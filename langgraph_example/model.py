"""LangGraph ReAct agent example — progressive skill disclosure.

Usage:
    pip install langchain-openai langgraph python-dotenv
    python langgraph_example/model.py

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 1. 组装 Skills ─────────────────────────────────────────────
skill_a = ALL_SKILLS.get_skill("pdf")
skill_b = ALL_SKILLS.get_skill("c_2_ast")

my_skills = Skills(
    name="langgraph_skills",
    skill_list=[skill_a, skill_b],
)

# ── 2. 包装为 LangChain tool ───────────────────────────────────
@tool("skill_tool", description=my_skills.tool_description)
def _skill_tool(action: str, arg: str = "") -> str:
    return json.dumps(my_skills.skill_tool(action, arg), ensure_ascii=False)


# ── 3. 构建 agent 并运行 ──────────────────────────────────────
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=0.0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

agent = create_react_agent(llm, [_skill_tool])

# 任务设计：触发渐进式披露 (listskill → readskill → execskill)
result = agent.invoke({
    "messages": [(
        "user",
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
    )]
})

# ── 4. 打印 & 保存日志 ────────────────────────────────────────
log_lines: list[str] = []
for i, m in enumerate(result["messages"]):
    msg_type = getattr(m, "type", m.__class__.__name__)
    header = f"\n--- {i} | {msg_type} ---"
    print(header)
    log_lines.append(header)

    if getattr(m, "content", None):
        print(m.content)
        log_lines.append(m.content)

    if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
        print("\n[tool_calls]")
        log_lines.append("\n[tool_calls]")
        for tc in m.tool_calls:
            print(tc)
            log_lines.append(str(tc))

    if isinstance(m, ToolMessage):
        print("\n[tool_result]")
        print(m.content)
        log_lines.append("\n[tool_result]")
        log_lines.append(m.content)

print("\n=== final ===")
print(result["messages"][-1].content)

log_file = Path(__file__).parent / "langgraph_result.log"
with open(log_file, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))


