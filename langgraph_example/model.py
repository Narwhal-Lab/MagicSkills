"""LangGraph ReAct agent example — progressive skill disclosure.

Usage:
    uv run --with langchain-openai --with langgraph --with python-dotenv \
        python langgraph_example/model.py --scenario all

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from pathlib import Path

# Windows 终端默认 GBK 编码，遇到 Unicode 特殊字符会崩溃
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 场景配置：log1=不停读 / log2=有执行 ─────────────────────────
SCENARIOS: dict[str, tuple[str, str]] = {
    "read": (
        "log1.json",
        "我想了解很多 AST 知识。",
    ),
    "exec": (
        "log2.json",
        "Please help me convert the following C code into an AST.\n"
        "```c\n"
        "#include <stdio.h>\n\n"
        "int main() {\n"
        '    puts("Hello from agent");\n'
        "    return 0;\n"
        "}\n"
        "```",
    ),
}

# ── 1. 组装 Skills ─────────────────────────────────────────────
def _resolve_required_skills() -> tuple[object, object]:
    all_skills = ALL_SKILLS()
    try:
        return all_skills.get_skill("pdf"), all_skills.get_skill("c_2_ast")
    except KeyError:
        local_skills = Skills(paths=[ROOT / "skills"])
        return local_skills.get_skill("pdf"), local_skills.get_skill("c_2_ast")


skill_a, skill_b = _resolve_required_skills()

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

def run_once(prompt: str, log_name: str) -> None:
    # 任务设计：触发渐进式披露 (listskill → readskill → execskill)
    log_lines: list[str] = []
    log_file = Path(__file__).parent / log_name

    try:
        result = agent.invoke(
            {"messages": [("user", prompt)]},
            {"recursion_limit": 40},
        )

        # ── 4. 打印 & 保存日志 ────────────────────────────────────
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
        log_lines.extend(["\n=== final ===", str(result["messages"][-1].content)])
    finally:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenario",
        choices=["read", "exec", "all"],
        default="all",
        help="Which scenario to run: read (log1), exec (log2), or all.",
    )
    args = parser.parse_args()

    targets = ["read", "exec"] if args.scenario == "all" else [args.scenario]
    for name in targets:
        log_name, prompt = SCENARIOS[name]
        print(f"\n================ {name.upper()} ================\n")
        run_once(prompt, log_name)


if __name__ == "__main__":
    main()






