import json
from magicskills.core.registry import ALL_SKILLS
from magicskills.core.skills import Skills
import os
from pathlib import Path

import asyncio
from openai import AsyncOpenAI
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion


SEMANTIC_KERNEL_MODEL = "SEMANTIC_KERNEL_MODEL"
SEMANTIC_KERNEL_BASE_URL = "SEMANTIC_KERNEL_BASE_URL"
SEMANTIC_KERNEL_API_KEY = "SEMANTIC_KERNEL_API_KEY"

s1 = ALL_SKILLS.get_skill("pdf")
s2 = ALL_SKILLS.get_skill("explain-code")
my_skills = Skills(name="semantic-kernel-skills", skills=[s1, s2])


class MagicSkillsPlugin:
    def __init__(self, skills_instance):
        self.skills = skills_instance

    @kernel_function(name="magic_skills",description=my_skills.tool_description)
    async def call_magic_skill(self, action: str, arg: str = "") -> str:
        """调用MagicSkills的统一接口"""
        result = self.skills.skill_for_all_agent(action, arg)
        return json.dumps(result, ensure_ascii=False)


async def main():
    chat_service = OpenAIChatCompletion(
            ai_model_id=SEMANTIC_KERNEL_MODEL,
            async_client = AsyncOpenAI(
                api_key=SEMANTIC_KERNEL_API_KEY,
                base_url=SEMANTIC_KERNEL_BASE_URL,
                ),
        )
    agent = ChatCompletionAgent(
        service=chat_service,
        instructions="You are a helpful assistant.",
        plugins=[MagicSkillsPlugin(my_skills)],
    )

    response = await agent.get_response(messages="Please use the skill_tool to list all available skills.")
    print(response.content)

    log_file = Path(__file__).parent / "semantic_kernel_result.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(str(response.content))


if __name__ == "__main__":
    asyncio.run(main())