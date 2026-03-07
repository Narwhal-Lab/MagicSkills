"""CrewAI agent example — progressive skill disclosure.

Usage:
    pip install crewai crewai-tools python-dotenv
    python crewai_example/model.py

Env vars (put in .env):
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from crewai import Agent, Crew, LLM, Task
from crewai.tools import tool
from dotenv import load_dotenv

from magicskills import ALL_SKILLS, Skills

load_dotenv()

# ── 1. 组装 Skills ─────────────────────────────────────────────
skill_a = ALL_SKILLS.get_skill("pdf")
skill_b = ALL_SKILLS.get_skill("c_2_ast")

my_skills = Skills(
    name="crewai_skills",
    skill_list=[skill_a, skill_b],
)


# ── 2. 包装为 CrewAI tool ──────────────────────────────────────
@tool("skill_tool")
def skill_tool_fn(action: str, arg: str = "") -> str:
    """Unified skill tool. If you are not sure, you can first use the "listskill"
    function of this tool to search for available skills. Then, determine which skill
    might be the most useful. After that, try to use the read the SKILL.md file under this
    skill path to get more detailed information. Finally, based on the content of this
    file, decide whether to read the documentation in other paths or directly execute
    the relevant script.
       Input format:
        {
            "action": "<action_name>",
            "arg": "<string argument>"
        }

    Actions:
    - listskill
    - readskill:     arg = file path
    - execskill:   arg = full command string"""
    result = my_skills.skill_tool(action, arg)
    return json.dumps(result, ensure_ascii=False)


# ── 3. 构建 agent 并运行 ──────────────────────────────────────
if __name__ == "__main__":
    llm = LLM(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )

    researcher = Agent(
        role="technical researcher",
        goal="Research the available tools and choose the one that best suits the task",
        backstory="technical expert",
        tools=[skill_tool_fn],
        verbose=True,
        llm=llm,
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
    result = crew.kickoff()
    print(result)

    log_file = Path(__file__).parent / "crewai_result.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(str(result))
