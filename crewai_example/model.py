"""CrewAI agent example — progressive skill disclosure.

Usage:
    uv run --with "crewai[litellm]" --with crewai-tools --with python-dotenv \
        python crewai_example/model.py --scenario all

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from crewai import Agent, Crew, LLM, Task
from crewai.tools import tool
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


class TeeWriter(io.TextIOBase):
    def __init__(self, *writers: io.TextIOBase) -> None:
        self._writers = writers

    def write(self, s: str) -> int:
        for writer in self._writers:
            writer.write(s)
        return len(s)

    def flush(self) -> None:
        for writer in self._writers:
            writer.flush()


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
    name="crewai_skills",
    skill_list=[skill_a, skill_b],
)

C2_AST_SCRIPTS = (ROOT / "skills" / "c_2_ast" / "scripts").resolve()
PYTHON_EXE = Path(sys.executable).resolve()


def _normalize_model_for_litellm(model_name: str) -> str:
    raw = (model_name or "").strip()
    if not raw:
        return raw
    provider_prefixes = (
        "openai/",
        "azure/",
        "anthropic/",
        "gemini/",
        "huggingface/",
        "deepseek/",
        "ollama/",
    )
    if raw.startswith(provider_prefixes):
        return raw
    return f"openai/{raw}"


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


# ── 2. 包装为 CrewAI tool ──────────────────────────────────────
from crewai.tools import BaseTool

class SkillTool(BaseTool):
    name: str = "skill_tool"
    description: str = my_skills.tool_description

    def _run(self, action: str, arg: str = "") -> str:
        fixed_arg = _normalize_exec_arg(arg) if action == "execskill" else arg
        result = my_skills.skill_tool(action, fixed_arg)
        result = _truncate_readskill_result(result)
        return json.dumps(result, ensure_ascii=False)

skill_tool_fn = SkillTool()


# ── 3. 构建 agent 并运行 ──────────────────────────────────────
def run_once(task_prompt: str, log_name: str) -> None:
    model_name = _normalize_model_for_litellm(os.getenv("OPENAI_MODEL", ""))
    llm = LLM(
        model=model_name,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0.1,
    )

    researcher = Agent(
        role="technical researcher",
        goal="Use the available skills to solve the user's task with the minimum necessary steps",
        backstory=(
            "You are a technical expert. Start by discovering available skills, then "
            "read the most relevant skill instructions, and only then execute the "
            "necessary command."
        ),
        tools=[skill_tool_fn],
        verbose=True,
        llm=llm,
        function_calling_llm=llm,
        max_iter=10,
        respect_context_window=True,
    )

    task = Task(
        description=task_prompt,
        agent=researcher,
        expected_output="Agent output with complete tool usage trace.",
    )

    crew = Crew(agents=[researcher], tasks=[task])
    log_file = Path(__file__).parent / log_name
    log_buffer = io.StringIO()
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = TeeWriter(original_stdout, log_buffer)
    sys.stderr = TeeWriter(original_stderr, log_buffer)
    try:
        result = crew.kickoff()
        print("\n=== final ===")
        print(result)
        log_content = log_buffer.getvalue()
    except BaseException:
        log_content = (
            "[ERROR] Agent run interrupted or failed.\n\n"
            + traceback.format_exc()
        )
        print(log_content)
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_content)


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







