"""LangChain tool-binding example — progressive skill disclosure.

Usage:
    uv run --with langchain-openai --with python-dotenv \
        python langchain_example/model.py --scenario all

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

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

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
    name="langchain_skills",
    skill_list=[skill_a, skill_b],
)

# ── 2. 包装为 LangChain tool ───────────────────────────────────
@tool("skill_tool", description=my_skills.tool_description)
def _skill_tool(action: str, arg: str = "") -> str:
    return json.dumps(my_skills.skill_tool(action, arg), ensure_ascii=False)


# ── 3. 多轮 tool-calling loop ─────────────────────────────────
def run_once(prompt: str, log_name: str) -> None:
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.0,
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=120,
    )
    llm_with_tools = llm.bind_tools([_skill_tool])

    messages: list = [("user", prompt)]
    log_lines: list[str] = []
    log_file = Path(__file__).parent / log_name
    max_rounds = 15  # 防止 LLM 无限循环

    try:
        for _round in range(max_rounds):
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
        else:
            log_lines.append("\n[WARN] max rounds reached")

        print("\n=== final ===")
        print(msg.content)
        log_lines.append(f"\n=== final ===\n{msg.content}")
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







