import os
import autogen
from dotenv import load_dotenv

load_dotenv()

# ===============================
# 1. Python 工具函数
# ===============================
def say_hello(name: str) -> str:
    print(f"[TOOL CALL] say_hello(name={name})")
    return f"Hello, {name}!"

# ===============================
# 2. 给 LLM 的函数 schema（纯 JSON）
# ===============================
functions = [
    {
        "name": "say_hello",
        "description": "Say hello to someone by name",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The person's name"
                }
            },
            "required": ["name"]
        }
    }
]

# ===============================
# 3. AssistantAgent（Qwen）
# ===============================
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "model": os.getenv("MODEL"),
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key": os.getenv("DASHSCOPE_API_KEY"),
        "temperature": 0,
        "functions": functions,
    },
)


# ===============================
# 4. UserProxyAgent（执行工具）
# ===============================
user = autogen.UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
    max_consecutive_auto_reply=1,
)

user.register_function(
    function_map={
        "say_hello": say_hello
    }
)

# ===============================
# 5. 启动对话
# ===============================
user.initiate_chat(
    assistant,
    message="你是"
)
