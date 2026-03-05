import json
import time
from datetime import datetime
from pathlib import Path
from magicskills.core.registry import ALL_SKILLS
from magicskills.core.skills import Skills

from crewai import Agent, Task, Crew
from crewai import LLM

CREWAI_API_KEY = "CREWAI_API_KEY"
CREWAI_MODEL = "CREWAI_MODEL"
CREWAI_BASE_URL = "CREWAI_BASE_URL"

s1 = ALL_SKILLS.get_skill("pdf")
s2 = ALL_SKILLS.get_skill("explain-code")
my_skills = Skills(name="crewai-skills", skills=[s1, s2])

from crewai.tools import tool
@tool("MagicSkill_tool")
def magic_tool(action: str, arg: str = "") -> str:
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
    result = my_skills.skill_for_all_agent(action, arg)
    return json.dumps(result, ensure_ascii=False)

if __name__ == "__main__":
    llm = LLM(
        model=CREWAI_MODEL,
        api_key=CREWAI_API_KEY,
        base_url=CREWAI_BASE_URL,
    )

    researcher = Agent(
        role='technical researcher',
        goal='Research the available tools and choose the one that best suits you',
        backstory='technical expert',
        tools=[magic_tool],
        verbose=True,
        llm=llm
    )

    task1 = Task(
        description='List all available skills using the MagicSkills tool',
        agent=researcher,
        expected_output='Skill list'
    )

    crew = Crew(agents=[researcher], tasks=[task1])
    result = crew.kickoff()
    print(result)

    log_file = Path(__file__).parent / "crewai_result.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(str(result))

