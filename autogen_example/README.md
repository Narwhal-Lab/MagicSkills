# AutoGen Example

## 1. 目标
本示例演示如何把 MagicSkills 的 skill_tool 接入 AutoGen agent，并生成两份完整日志：

- log1.json：不停读文档场景（偏知识学习）
- log2.json：执行场景（把 C 代码转换为 AST）

日志会保留 agent 每一步输出（包含中间 tool 调用与最终回答），格式参考 langgraph_example/log1.json 与 langgraph_example/log2.json。

## 2. 环境准备
在项目根目录执行：

```bash
uv --version
```

确保根目录有 .env（可从 .env.example 复制）：

```bash
cp .env.example .env
```

并填写：

- OPENAI_BASE_URL
- OPENAI_API_KEY
- OPENAI_MODEL

## 3. 运行方式
在项目根目录执行：

```bash
uv run --with autogen-agentchat --with "autogen-ext[openai]" --with python-dotenv python autogen_example/model.py --scenario all
```

可选：只跑单个场景

```bash
uv run --with autogen-agentchat --with "autogen-ext[openai]" --with python-dotenv python autogen_example/model.py --scenario read
uv run --with autogen-agentchat --with "autogen-ext[openai]" --with python-dotenv python autogen_example/model.py --scenario exec
```

## 4. 产物说明
运行完成后，本目录会生成：

- log1.json
- log2.json

验收时请重点检查：

- log1.json 中是否出现多步文档阅读行为（围绕 AST 相关 skill）
- log2.json 中是否出现执行步骤并产出 AST 结果

## 5. 常见问题
- 如果报认证错误：检查 .env 中的 key、base_url、model 是否可用。
- 如果报网络错误：确认当前环境可访问配置的模型服务。
- 如果日志为空：重跑命令并查看终端输出中的异常栈信息。
