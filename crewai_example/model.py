"""CrewAI agent example — progressive skill disclosure.

Usage:
    uv run --with "crewai[litellm]" --with crewai-tools --with python-dotenv \
        python crewai_example/model.py

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from crewai import Agent, Crew, LLM, Task
from crewai.tools import tool
from dotenv import load_dotenv

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 1. 组装 Skills ─────────────────────────────────────────────
skill_a = ALL_SKILLS().get_skill("pdf")
skill_b = ALL_SKILLS().get_skill("c_2_ast")

my_skills = Skills(
    name="crewai_skills",
    skill_list=[skill_a, skill_b],
)


# ── 2. 包装为 CrewAI tool ──────────────────────────────────────
from crewai.tools import BaseTool

class SkillTool(BaseTool):
    name: str = "skill_tool"
    description: str = my_skills.tool_description

    def _run(self, action: str, arg: str = "") -> str:
        return json.dumps(my_skills.skill_tool(action, arg), ensure_ascii=False)

skill_tool_fn = SkillTool()



# ── 3. 构建 agent 并运行 ──────────────────────────────────────
if __name__ == "__main__":
    llm = LLM(
        model=os.getenv("OPENAI_MODEL"),
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

    # 任务设计：触发渐进式披露 (listskill → readskill → execskill)
    task = Task(
        description=(
            "Please help me convert the following C code into an AST.\n"
            "First discover what skills are available, then read the relevant "
            "skill instructions, and finally execute the conversion.\n\n"
            "```c\n"
            "#include <stdio.h>\n\n"
            "int main() {\n"
            '    puts(\"Hello from agent\");\n'
            "    return 0;\n"
            "}\n"
            "```"
        ),
        agent=researcher,
        expected_output="The AST output of the provided C code.",
    )

    crew = Crew(agents=[researcher], tasks=[task])
    log_file = Path(__file__).parent / "crewai_result.log"
    try:
        result = crew.kickoff()
        print(result)
        log_content = str(result)
    except BaseException:
        log_content = "[ERROR] Agent run interrupted or failed."
        raise
    finally:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_content)
