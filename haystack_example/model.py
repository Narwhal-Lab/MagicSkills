"""Haystack agent example — progressive skill disclosure.

Usage:
    uv run --with haystack-ai --with python-dotenv \
        python haystack_example/model.py --scenario all

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
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import create_tool_from_function
from haystack.utils import Secret

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


def run_once(prompt: str, log_name: str) -> None:
    # ── 3. 构建 agent 并运行 ──────────────────────────────────
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

    log_file = Path(__file__).parent / log_name
    try:
        result = agent.run(messages=[ChatMessage.from_user(prompt)])
        log_content = json.dumps(result, ensure_ascii=False, indent=2, default=str)
        print(log_content)
    except BaseException:
        log_content = "[ERROR] Agent run interrupted or failed."
        raise
    finally:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_content or "[EMPTY]")


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







