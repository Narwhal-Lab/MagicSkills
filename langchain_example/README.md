# LangChain Example


## 1. 目标
本示例演示如何把 MagicSkills 的 skill_tool 接入 LangChain agent，并生成两份完整日志：

- log1.json：不停读文档场景（偏知识学习）
- log2.json：执行场景（把 C 代码转换为 AST）

日志会保留 agent 每一步输出（包含中间 tool 调用与最终回答），格式参考 langchain_example/log1.json 与 langchain_example/log2.json。

本示例还展示了 MagicSkills 多 agent 管理的核心特性：为不同 agent 创建独立的 skills 集合，每个 agent 只暴露它所需的工具。


## 2. 安装 magicskills

```bash
git clone https://github.com/Narwhal-Lab/MagicSkills.git
cd MagicSkills
pip install -e .
```


## 3. 安装 skill

以下演示两种安装方式，若 skill 已安装可跳过对应命令。

### 方式一：从本地安装（项目内置模板）

```bash
magicskills install skill_template -t ~/allskills
```

### 方式二：从 GitHub 安装

```bash
magicskills install anthropics/skills -t ~/allskills
```

> `-t ~/allskills` 指定安装目录。
> 说明：如果你只执行方式一的 `skill_template` 安装，通常只会得到 `c_2_ast`。而本示例后续还要使用 `pdf` 和 `docx`，所以如果这两个 skill 还不存在，请执行方式二从 `anthropics/skills` 安装。


## 4. 创建 skills

本示例创建两个 skills 集合，分别对应两个 agent，每个 agent 拥有不同的工具组合：

```bash
magicskills addskills langchain_agent1_skills --skill-list c_2_ast pdf --agent-md-path ./AGENTS.md
magicskills addskills langchain_agent2_skills --skill-list c_2_ast docx --agent-md-path ./AGENTS.md
```我先把当前 pr.md 读一遍，然后把它改成英文版，同时新增一份中文保留稿 pr.zh-CN.md。

- **langchain_agent1_skills**：`c_2_ast` + `pdf`，用于 log1 场景（知识阅读 agent）
- **langchain_agent2_skills**：`c_2_ast` + `docx`，用于 log2 场景（代码执行 agent）


## 5. 生成 AGENTS.md

```bash
magicskills syncskills langchain_agent1_skills --output ./AGENTS.md -y
```


## 6. 环境准备

确保根目录有 `.env`（可从 `.env.example` 复制）：

```bash
cp .env.example .env
```

并填写：

- `OPENAI_BASE_URL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`


## 7. 安装依赖并运行

```bash
pip install -r langchain_example/requirements.txt
```

在项目根目录执行：

```bash
python langchain_example/model.py --scenario all
```

可选：只跑单个场景

```bash
python langchain_example/model.py --scenario read
python langchain_example/model.py --scenario exec
```


## 8. 两个场景的 prompt

### 场景一：了解更多 AST 知识（log1.json）

输入 prompt：

```
我想了解更多 AST 知识。
```

agent 会依次执行：`listskill` → `readskill`（读取 SKILL.md）→ `readskill`（读取 reference.md），通过多步文档阅读获取 AST 相关知识。

### 场景二：转换一段代码为 AST（log2.json）

输入 prompt：

````
请将下面这段 C 代码转换为 AST
```c
#include <stdio.h>

int main() {
    puts("Hello from agent");
    return 0;
}
```
````

agent 会依次执行：`listskill` → `readskill`（读取 SKILL.md）→ `execskill`（运行转换脚本），产出 AST 结果。


## 9. 产物说明
运行完成后，本目录会生成：

- log1.json
- log2.json

验收时请重点检查：

- log1.json 中是否出现多步文档阅读行为（围绕 AST 相关 skill）
- log2.json 中是否出现执行步骤并产出 AST 结果


## 10. 常见问题
- 如果报 `skills collection(s) not found`：请先按第 4 步执行 `addskills` 命令。
- 如果报认证错误：检查 `.env` 中的 key、base_url、model 是否可用。
- 如果报网络错误：确认当前环境可访问配置的模型服务。
- 如果日志为空：重跑命令并查看终端输出中的异常栈信息。
