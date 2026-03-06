import json
from magicskills.core.registry import ALL_SKILLS
from magicskills.core.skills import Skills
import os
from pathlib import Path

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import create_tool_from_function


HAYSTACK_MODEL = "HAYSTACK_MODEL"
HAYSTACK_BASE_URL = "HAYSTACK_BASE_URL"
os.environ["OPENAI_API_KEY"] = "HAYSTACK_MODEL_API_KEY"

s1 = ALL_SKILLS.get_skill("pdf")
s2 = ALL_SKILLS.get_skill("explain-code")
my_skills = Skills(name="haystack-skills", skills=[s1, s2])

def magic_skills(action: str, arg: str = "") -> str:
    """MagicSkills unified tool interface"""
    result = my_skills.skill_for_all_agent(action, arg)
    return str(result)

magic_skills_tool = create_tool_from_function(
                        function = magic_skills,
                        name="skill_tool", 
                        description=my_skills.tool_description,
                        outputs_to_string={"source": "documents", "handler": magic_skills}, 
                        outputs_to_state={"documents": {"source": "documents"}}, )


if __name__ == "__main__":
    generator = OpenAIChatGenerator(
        model=HAYSTACK_MODEL,
        api_base_url=HAYSTACK_BASE_URL
    )
    agent = Agent(
        chat_generator=generator,
        tools=[magic_skills_tool],
        max_agent_steps=5
    )

    prompt = "Please use the skill_tool to list all available skills."
    result = agent.run(messages=[ChatMessage.from_user(prompt)])
    print(result['last_message'].text)

    log_file = Path(__file__).parent / "haystack_result.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(result['last_message'].text)