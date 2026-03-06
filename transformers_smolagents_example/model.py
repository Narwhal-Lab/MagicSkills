import json
from pathlib import Path
from magicskills.core.registry import ALL_SKILLS
from magicskills.core.skills import Skills

from smolagents import Tool
from smolagents import LiteLLMModel
from smolagents import CodeAgent

SMOLAGENTS_MODEL = "SMOLAGENTS_MODEL"
SMOLAGENTS_BASE_URL = "SMOLAGENTS_BASE_URL"
SMOLAGENTS_API_KEY = "SMOLAGENTS_API_KEY"

s1 = ALL_SKILLS.get_skill("pdf")
s2 = ALL_SKILLS.get_skill("explain-code")
my_skills = Skills(name="transformers-agents-skills", skills=[s1, s2])

class MagicSkillsTool(Tool):
    name = "magic_skills"
    description = my_skills.tool_description
    inputs = {
        "action": {
            "type": "string",
            "description": "The action to perform using magic_skills",
        },
        "arg": {
            "type": "string",
            "description": "The argument for the action",
        }
    }
    output_type = "string"

    def __init__(self, skills_instance):
        super().__init__()
        self.skills = skills_instance

    def forward(self, action:str, arg:str) -> str:
        result = self.skills.skill_for_all_agent(action.strip(), arg.strip())
        return json.dumps(result, ensure_ascii=False)

magic_skills_tool = MagicSkillsTool(my_skills)


def main():

    model = LiteLLMModel(
                model_id=SMOLAGENTS_MODEL,
                api_base=SMOLAGENTS_BASE_URL,
                api_key=SMOLAGENTS_API_KEY )

    agent = CodeAgent(
        tools=[magic_skills_tool],
        model=model,
    )

    result = agent.run("Please use the magic_skills to list all available skills.")
    print(result)

    log_file = Path(__file__).parent / "smolagents_result.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(str(result))


if __name__ == "__main__":
    main()