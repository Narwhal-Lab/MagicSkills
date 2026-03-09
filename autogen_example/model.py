"""AutoGen agent example — progressive skill disclosure.

Usage:
    uv run --with autogen-agentchat --with "autogen-ext[openai]" --with python-dotenv \
        python autogen_example/model.py --scenario all

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import argparse
import asyncio
import io
import json
import os
import re
import sys
import traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core.models import ModelFamily
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

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
    name="autogen_skills",
    skill_list=[skill_a, skill_b],
)

C2_AST_SCRIPTS = (ROOT / "skills" / "c_2_ast" / "scripts").resolve()
PYTHON_EXE = Path(sys.executable).resolve()


def _normalize_exec_arg(arg: str) -> str:
    normalized = (arg or "").strip()
    if not normalized:
        return normalized

    for pattern in (
        r"skills_for_all_agent/skill/c_2_ast/scripts",
        r"/root/\.agent/skills/c_2_ast/scripts",
        r"/root/LLK/MagicSkills/crewai_example/\.claude/skills/c_2_ast/scripts",
    ):
        normalized = re.sub(pattern, lambda _m: str(C2_AST_SCRIPTS), normalized)

    # Force tool-executed Python commands to use the same interpreter as this process.
    normalized = re.sub(
        r"(^|&&\s*)(python3|python)(\s+)",
        lambda m: f'{m.group(1)}"{PYTHON_EXE}"{m.group(3)}',
        normalized,
    )
    normalized = normalized.replace("ls -la", "dir")
    return normalized


def _truncate_readskill_result(payload: dict[str, object], limit: int = 6000) -> dict[str, object]:
    if payload.get("action") != "readskill" or not payload.get("ok"):
        return payload
    content = payload.get("result")
    if isinstance(content, str) and len(content) > limit:
        payload["result"] = content[:limit] + "\n...[TRUNCATED]..."
    return payload


# ── 2. 包装为 AutoGen FunctionTool ─────────────────────────────
async def skill_tool_fn(action: str, arg: str = "") -> str:
    """Unified skill tool interface for MagicSkills."""
    fixed_arg = _normalize_exec_arg(arg) if action == "execskill" else arg
    result = my_skills.skill_tool(action, fixed_arg)
    result = _truncate_readskill_result(result)
    return json.dumps(result, ensure_ascii=False)


magic_skill_tool = FunctionTool(skill_tool_fn, description=my_skills.tool_description)


# ── 3. 构建 agent 并运行 ──────────────────────────────────────
async def run_once(task: str, log_name: str) -> None:
    model_family = getattr(ModelFamily, "UNKNOWN", ModelFamily.GPT_4O)
    model_client = OpenAIChatCompletionClient(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "family": model_family,
            "structured_output": False,
        },
    )

    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[magic_skill_tool],
        system_message=(
            "You are a helpful assistant that uses tools to complete tasks step by step. "
            "Use the skill_tool tool whenever tool usage is needed. "
            "For knowledge requests, prefer reading skill documents before answering. "
            "Only execute commands when the user task explicitly requires execution. "
            "When all steps are done and you have the final output, end your response with the word TERMINATE."
        ),
        reflect_on_tool_use=False,
    )

    team = RoundRobinGroupChat(
        participants=[agent],
        termination_condition=MaxMessageTermination(30) | TextMentionTermination("TERMINATE"),
    )

    log_file = Path(__file__).parent / log_name
    try:
        result = await Console(team.run_stream(task=task), output_stats=True)
        lines: list[str] = []
        for i, message in enumerate(result.messages):
            header = f"\n--- {i} | {type(message).__name__} ---"
            lines.append(header)
            print(header)
            payload = json.dumps(message.model_dump(), ensure_ascii=False, indent=2, default=str)
            lines.append(payload)
            print(payload)
        log_content = "\n".join(lines)
    except BaseException:
        log_content = (
            "[ERROR] Agent run interrupted or failed.\n\n"
            + traceback.format_exc()
        )
        print(log_content)
    finally:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_content)


async def main() -> None:
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
        await run_once(prompt, log_name)


if __name__ == "__main__":
    asyncio.run(main())







