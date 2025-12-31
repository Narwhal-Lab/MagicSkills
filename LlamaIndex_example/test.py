from dotenv import load_dotenv
load_dotenv()
# ---------- 1. 定义工具 ----------
def say_hello(name: str) -> str:
    """向指定的人打招呼"""
    return f"Hello, {name}!"


from llama_index.core.tools import FunctionTool

hello_tool = FunctionTool.from_defaults(
    say_hello,
    name="say_hello",
    description="Say hello to someone by name",
)


# ---------- 2. 使用 Qwen（百炼 OpenAI-like） ----------
import os
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.agent import ReActAgent

llm = OpenAILike(
    model="qwen-plus",
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    is_chat_model=True,
)

# ---------- 3. 创建 Agent ----------
agent = ReActAgent(
    tools=[hello_tool],
    llm=llm,
    verbose=True,
)

# ---------- 4. 正确运行（异步） ----------
import asyncio

async def main():
    response = await agent.run("跟 Tom 打个招呼")
    print(response)

asyncio.run(main())
