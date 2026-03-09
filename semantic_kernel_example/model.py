"""Semantic Kernel function-calling example — progressive skill disclosure.

Usage:
    uv run --with semantic-kernel --with python-dotenv \
        python semantic_kernel_example/model.py --scenario all

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
from typing import Any
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import AsyncOpenAI
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import kernel_function

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
    name="semantic_kernel_skills",
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

    # Resolve known script names to absolute paths so commands do not depend on prior `cd`.
    normalized = re.sub(
        r"(^|&&\s*)(python3|python)\s+(save_c\.py|c_2_ast\.py)\b",
        lambda m: f'{m.group(1)}{m.group(2)} "{C2_AST_SCRIPTS / m.group(3)}"',
        normalized,
    )

    # Ensure execskill uses this process interpreter instead of host python3.
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


# ── 2. 包装为 Semantic Kernel plugin ──────────────────────────
def build_skill_tool_plugin(skills: Skills) -> object:
    class MagicSkillsPlugin:
        @kernel_function(
            name="skill_tool",
            description=skills.tool_description,
        )
        async def skill_tool(self, action: str, arg: str = "") -> str:
            fixed_arg = _normalize_exec_arg(arg) if action == "execskill" else arg
            result = skills.skill_tool(action, fixed_arg)
            result = _truncate_readskill_result(result)
            return json.dumps(result, ensure_ascii=False)

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
async def run_once(prompt: str, log_name: str) -> None:
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

    log_lines: list[str] = []
    log_file = Path(__file__).parent / log_name
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







