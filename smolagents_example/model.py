"""Hugging Face smolagents example — progressive skill disclosure.

Usage:
    uv run --with "smolagents[openai]" --with python-dotenv \
        python smolagents_example/model.py --scenario all

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

Note: Uses CodeAgent (prompt-based tool calling) because DeepSeek V3.2
      returns empty choices when the OpenAI `tools` API parameter is used.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from smolagents import CodeAgent, OpenAIServerModel, Tool

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
    name="smolagents_skills",
    skill_list=[skill_a, skill_b],
)


# ── 2. 包装为 smolagents Tool ─────────────────────────────────
class MagicSkillsTool(Tool):
    name = "skill_tool"
    description = my_skills.tool_description
    inputs = {
        "action": {
            "type": "string",
            "description": "The action to perform (listskill / readskill / execskill)",
        },
        "arg": {
            "type": "string",
            "description": "The argument for the action",
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self, skills_instance: Skills) -> None:
        super().__init__()
        self.skills = skills_instance

    def forward(self, action: str, arg: str = "") -> str:
        result = self.skills.skill_tool(action.strip(), arg.strip())
        return json.dumps(result, ensure_ascii=False)


magic_skills_tool = MagicSkillsTool(my_skills)


# ── 2b. 修补 DeepSeek 的 </code 截断问题 ──────────────────────
class PatchedOpenAIServerModel(OpenAIServerModel):
    """Fix DeepSeek V3.2 outputting '</code' without closing '>'."""

    def __call__(self, messages, **kwargs):
        result = super().__call__(messages, **kwargs)
        if hasattr(result, "content") and isinstance(result.content, str):
            result.content = re.sub(r"</code(?!>)", "</code>", result.content)
        return result


def run_once(prompt: str, log_name: str) -> None:
    # ── 3. 构建 agent 并运行 ──────────────────────────────────
    model = PatchedOpenAIServerModel(
        model_id=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_base=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    agent = CodeAgent(
        tools=[magic_skills_tool],
        model=model,
        additional_authorized_imports=["json", "sys", "os", "subprocess", "pathlib"],
        max_steps=50,
    )

    log_file = Path(__file__).parent / log_name
    log_buffer = io.StringIO()
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = TeeWriter(original_stdout, log_buffer)
    sys.stderr = TeeWriter(original_stderr, log_buffer)
    try:
        result = agent.run(prompt)
        print("\n=== final ===")
        print(result)
        log_content = log_buffer.getvalue()
    except BaseException:
        log_content = "[ERROR] Agent run interrupted or failed."
        raise
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







