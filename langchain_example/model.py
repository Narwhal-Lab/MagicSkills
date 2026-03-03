"""LangChain tool example for one Skills instance.

Usage:
    python langchain_example/model.py

Optional dependencies:
    pip install langchain-core pydantic
"""

from __future__ import annotations

import json
from typing import Sequence
from magicskills.core.registry import ALL_SKILLS
from magicskills.core.skills import Skills

# 选中的 skill（有重名时要传 path）
s1 = ALL_SKILLS.get_skill("pdf")
s2 = ALL_SKILLS.get_skill("c_2_ast", path="/root/LLK/MagicSkills/.agent/skills/c_2_ast")

selected = [s1, s2]
paths = sorted({s.base_dir for s in selected}, key=lambda p: p.as_posix())
my_skills = Skills(name="Askills", skills=selected, paths=paths)


# 第一种方式
import json
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

class SkillInput(BaseModel):
    action: str = Field(...)
    arg: str = Field("")

def skill_tool_fn(action: str, arg: str = "") -> str:
    result = my_skills.skill_for_all_agent(action, arg)
    return json.dumps(result, ensure_ascii=False)

skill_tool1 = StructuredTool.from_function(
    func=my_skills.skill_for_all_agent, #skill_tool_fn,
    name="skill_tool",
    description=my_skills.tool_description,  # 直接用这里
    args_schema=SkillInput,
)

#第二种方式
from langchain_core.tools import tool

@tool("_skill_tool", description=my_skills.tool_description)
def _skill_tool(action: str, arg: str = "") -> str:
    return json.dumps(my_skills.skill_for_all_agent(action, arg), ensure_ascii=False)







# 调用模型
import os
from langchain_openai import ChatOpenAI

def run_once(prompt: str, use_structured: bool = True):

    tool_to_bind = skill_tool1 if use_structured else _skill_tool

    llm = ChatOpenAI(
        model="gpt-4o-mini",   # 或你能用的模型名
        temperature=0.0,
    )

    # 3) 绑定工具：模型将“知道”有一个名为 skill_tool 的工具可用
    llm_with_tools = llm.bind_tools([tool_to_bind])

    # 4) 喂给模型提示词
    msg = llm_with_tools.invoke(prompt)

    # msg 是 AIMessage，里面可能包含 tool_calls
    print("=== LLM raw message ===")
    print(msg)

    # 5) 如果模型发起了 tool_calls，你需要执行工具，并把结果再喂回模型
    #    （LangGraph 通常用 ToolNode 自动做这一步；这里我们手写最小流程）
    if getattr(msg, "tool_calls", None):
        print("\n=== tool_calls ===")
        print(msg.tool_calls)

        # 这里只处理第一个 tool_call（你也可以循环处理多个）
        tc = msg.tool_calls[0]
        name = tc["name"]
        args = tc["args"]

        # 执行工具：StructuredTool / tool 都支持 invoke(dict_args)
        tool_result = tool_to_bind.invoke(args)

        print("\n=== tool_result ===")
        print(tool_result)

        # 把工具结果作为 ToolMessage 发回模型，让它生成最终回答
        # LangChain 会帮你构造 ToolMessage：用 llm_with_tools 再 invoke 一次
        from langchain_core.messages import ToolMessage

        final = llm_with_tools.invoke([
            msg,
            ToolMessage(content=tool_result, tool_call_id=tc["id"]),
        ])

        print("\n=== final answer ===")
        print(final.content)
    else:
        # 没触发工具，直接输出模型回答
        print("\n=== final answer (no tool) ===")
        print(msg.content)


if __name__ == "__main__":
    prompt = """
你是一个会使用工具的助手。
请调用 skill_tool 工具来执行 action="pdf" arg="把 /tmp/a.pdf 每页转成图片，并返回输出目录"。
工具返回后，用一句话总结结果。
""".strip()

    run_once(prompt, use_structured=True)