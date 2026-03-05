import json
from pathlib import Path
from magicskills.core.registry import ALL_SKILLS
from magicskills.core.skills import Skills

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
from autogen_core.models import ModelFamily
from autogen_agentchat.ui import Console

import asyncio


AUTOGEN_API_KEY = "AUTOGEN_API_KEY"
AUTOGEN_MODEL = "AUTOGEN_MODEL"
AUTOGEN_BASE_URL = "AUTOGEN_BASE_URL"

    
# 1. 创建Skills实例
s1 = ALL_SKILLS.get_skill("pdf")
s2 = ALL_SKILLS.get_skill("explain-code")
my_skills = Skills(name="autogen-skills", skills=[s1, s2])

# 2. 创建技能调用函数
async def magic_skills(action: str, arg: str = "") -> str:
    """AutoGen agent can call skill functions"""
    result = my_skills.skill_for_all_agent(action, arg)
    return json.dumps(result, ensure_ascii=False)

magic_skill_tool = FunctionTool(magic_skills, description=my_skills.tool_description)

if __name__ == "__main__":

    _model_info = {
                    "vision": False,
                    "function_calling": True ,
                    "json_output": True,
                    "family": ModelFamily.R1,
                    "structured_output": True,
            }

    openai_model_client = OpenAIChatCompletionClient(
        model=AUTOGEN_MODEL,
        api_key=AUTOGEN_API_KEY, 
        base_url=AUTOGEN_BASE_URL,
        model_info = _model_info
    )

    agent = AssistantAgent(
        name="assistant",
        model_client=openai_model_client,
        tools=[magic_skill_tool],
        system_message="Use tools to solve tasks.",
    )

    result = asyncio.run(Console(agent.run_stream(task="Use the 'magic_skills' function to list all available skills"), output_stats=True))
    log_file = Path(__file__).parent / "autogen_result.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(str(result.messages))