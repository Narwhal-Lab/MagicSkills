<div align="center">

<img src="./image/Logo.png" alt="MagicSkills" width="300" />

<br/>
<br/>

# 🪄 MagicSkills: **一次构建技能，供每个 Agent 复用**

<br/>

面向多 Agent 项目的**本地优先** skill 基础设施

将分散的 `SKILL.md` 目录沉淀为可复用、可组合、可同步、可调用的共享能力库

<br/>

<table>
<tr>
<td align="center"><b>🤖 Agent 应用</b></td>
<td align="center"><b>🧩 Agent 框架</b></td>
</tr>
<tr>
<td align="center">Claude Code · Cursor · Windsurf · Aider · Codex<br/><sub>任何能读取 `AGENTS.md` 的 Agent 应用</sub></td>
<td align="center">AutoGen · CrewAI · LangChain · LangGraph · Haystack<br/>Semantic Kernel · smolagents · LlamaIndex<br/><sub>任何支持 tool / function 集成的 Agent 框架</sub></td>
</tr>
</table>

<br/>

<sub>由北京大学 Narwhal-Lab 发起并维护</sub>

<p align="center">
  <a href="https://www.pku.edu.cn">
    <img src="./image/image4.png" alt="Peking University" height="42" />
  </a>
  <a href="https://github.com/Narwhal-Lab">
    <img src="./image/image5.png" alt="Narwhal-Lab" height="42" />
  </a>
</p>

<p>
  <a href="https://github.com/Narwhal-Lab/MagicSkills"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10‑3.13"/></a>
   
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" alt="License: MIT"/></a>
   
  <a href="https://github.com/Narwhal-Lab/MagicSkills"><img src="https://img.shields.io/github/stars/Narwhal-Lab/MagicSkills?style=for-the-badge&logo=github" alt="GitHub stars"/></a>
</p>

<br/>
<br/>

 [English](./README.md) | 简体中文

[概览](#overview-cn) · [快速开始](#quick-start-cn) · [工作原理](#how-it-works-cn) · [CLI](./doc/cli.zh-CN.md) · [Python API](./doc/python-api.zh-CN.md) · [使用建议](#tips-cn)

</div>

---

<a id="overview-cn"></a>

## 预览视频
[Watch the demo video](./README-Video.mp4)

## 🧭 概览

MagicSkills 是面向多 Agent 项目的本地优先 skill 基础设施层。

它把分散的 `SKILL.md` 目录整理成一套可以：

- 安装到共享 skill 池
- 按 agent 组合成各自的 `Skills` 集合
- 同步到 `AGENTS.md`
- 通过一个稳定 API 暴露为工具

核心模型很简单：

- `Skill`：一个具体的 skill 目录
- `ALL_SKILLS()`：访问当前内置的 `Allskills` 视图
- `Skills`：某个 agent 或工作流实际使用的 skill 子集
- `REGISTRY`：跨运行持久化的全局命名集合注册表

MagicSkills 特别适合这些场景：

- 你维护多个需要复用同一套 skill 库的 agent
- 你已经有 `SKILL.md` 内容，但还没有安装、选配和同步流程
- 某些 agent 读取 `AGENTS.md`，而另一些 agent 需要直接接入工具

一个很常见的真实场景是：你有一个可复用的共享 skill，而多个不同的 Agent 应用和 Agent 框架都需要使用它。

例如，同一个 `c_2_ast` skill，可能需要同时供 Claude Code、Cursor、Windsurf、Aider、Codex、AutoGen、CrewAI、LangChain、LangGraph、Haystack、Semantic Kernel、smolagents 和 LlamaIndex 使用。

在这种情况下，推荐做法不是把这个 skill 分别复制到每个 agent 项目里，而是把它统一维护在共享 skill 池中，再基于同一份底层 skill 构建一个或多个命名的 `Skills` 集合，并根据目标运行时是读取 `AGENTS.md` 还是通过 tools / functions 接入，用不同方式把这份能力暴露出去。

## 🤔 为什么需要 MagicSkills

没有 skill 层时，多 Agent 项目通常会逐渐滑向以下状态：

- 同一个 skill 被复制到多个 agent 目录中，并很快产生分叉
- `SKILL.md` 明明已经存在，但仍然只是文档，而不是可操作单元
- 每个 agent 都加载了过多无关 skill
- `AGENTS.md`、提示词胶水层和框架工具接口彼此独立演化
- 一旦更换框架，就得把整套集成方式重做一遍

MagicSkills 通过分离以下几层来解决这些问题：

- 总体已安装的 skill 池
- 每个 agent 实际应该看到的 skill 子集
- 负责保存命名集合的持久化层

<a id="quick-start-cn"></a>

## 🚀 快速开始

推荐的最短工作流如下：

1. 安装 MagicSkills。
2. 把一个或多个 skill 安装到本地池中。
3. 为某个 agent 创建一个命名的 `Skills` 集合。
4. 如果运行时会读取 `AGENTS.md`，就把这个集合同步到 `AGENTS.md`。
5. 或者通过 CLI 工具接口暴露这个集合。
6. 或者直接从 Python 暴露这个集合。

### 1. 📦 安装项目

从源码安装：

```bash
git clone https://github.com/Narwhal-Lab/MagicSkills.git
cd MagicSkills
python -m pip install -e .
magicskills -h
```

或者通过 PyPI 安装：

```bash
pip install MagicSkills
magicskills -h
```

### 2. ⬇️ 安装 skill

```bash
# 远程仓库示例
magicskills install anthropics/skills -t ~/allskills

# 本地目录示例（如果你已经 clone 了当前仓库）
magicskills install skill_template -t ~/allskills
```

第一条命令演示的是从 GitHub 仓库安装。第二条命令使用当前仓库里的本地 `skill_template/` 目录，来模拟“你已经把 skill 下载到本地，现在要把它安装进共享目录”的常见场景。

MagicSkills 默认支持四种标准安装位置：

- 当前项目：`./.claude/skills/`
- `--global`：`~/.claude/skills/`
- `--universal`：`./.agent/skills/`
- `--global --universal`：`~/.agent/skills/`

你也可以通过 `-t` / `--target` 显式指定任意路径。

在实际使用里，我们更建议把 skill 统一安装到一个共享目录，比如 `~/allskills`。这样不同 agent 和框架都可以复用同一个本地 skill 池，并且都能从内置的 `Allskills` 视图中发现它们。

### 3. 🧩 创建一个 Agent 集合

这里的 `pdf` 和 `docx` 只是示例 skill 名称。你应该替换成自己当前 `Allskills` 视图里已经存在的 skill。如果你只安装了当前仓库里的本地 `skill_template/`，这里就改成 `c_2_ast`。

```bash
magicskills addskills agent1_skills --skill-list pdf docx --agent-md-path /agent_workdir/AGENTS.md
```

这表示：

- 从 `Allskills` 中找到 `pdf` 和 `docx` 这两个 skill
- 创建一个名为 `agent1_skills` 的命名集合
- 将 `/agent_workdir/AGENTS.md` 记为它的默认同步目标

### 4. 🔄 同步到 `AGENTS.md`

```bash
magicskills syncskills agent1_skills
```

`syncskills` 支持两种同步到 `AGENTS.md` 的模式：

- `none`：保留标准的 `<usage> + <available_skills>` 结构；适合能够根据 `AGENTS.md` 中给出的 skill 信息列表直接发现并使用对应 skill 的 agent
- `cli_description`：只写 `<usage>`，内容来自集合的 `cli_description`；适合不能根据 `AGENTS.md` 中给出的 skill 信息列表直接使用 skill、需要通过 `magicskills skill-tool` 的 CLI 说明来使用 skill 的 agent

示例：

```bash
magicskills syncskills agent1_skills --mode none
magicskills syncskills agent1_skills --mode cli_description
```

如果目标文件已经包含 skills 区块，就会替换；如果没有，就会追加一个新的区块。

### 5. 🛠️ 或直接使用 CLI 工具接口

对于不会读取 `AGENTS.md` 的 agent，可以直接使用统一的 CLI 工具入口：

```bash
magicskills skill-tool listskill --name agent1_skills
magicskills skill-tool readskill --name agent1_skills --arg pdf
magicskills skill-tool execskill --name agent1_skills --arg "echo hello"
```

### 6. 🐍 或直接从 Python 暴露同一套接口

如果你要把 MagicSkills 接入某个 agent 框架，Python 侧通常有两种常见写法。

**方式一：复用已经通过 CLI 创建好的集合**

如果你已经先通过下面这条命令创建过集合：

```bash
magicskills addskills agent1_skills --skill-list pdf docx --agent-md-path /agent_workdir/AGENTS.md
```

那么 Python 里可以直接通过 `REGISTRY.get_skills("agent1_skills")` 复用这个命名集合：

```python
import json

from langchain_core.tools import tool
from magicskills import REGISTRY

agent1_skills = REGISTRY.get_skills("agent1_skills")


@tool("_skill_tool", description=agent1_skills.tool_description)
def _skill_tool(action: str, arg: str = "") -> str:
    return json.dumps(agent1_skills.skill_tool(action, arg), ensure_ascii=False)
```

**方式二：直接在 Python 里构造一个临时集合**

如果你不想依赖预先创建好的注册表项，也可以手动构造 `Skills(...)`：

```python
import json

from langchain_core.tools import tool
from magicskills import ALL_SKILLS, Skills

skill_a = ALL_SKILLS().get_skill("pdf")
skill_b = ALL_SKILLS().get_skill("docx")

agent1_skills = Skills(
    name="agent1_skills",
    skill_list=[skill_a, skill_b],
)


@tool("_skill_tool", description=agent1_skills.tool_description)
def _skill_tool(action: str, arg: str = "") -> str:
    return json.dumps(agent1_skills.skill_tool(action, arg), ensure_ascii=False)
```

第二种写法默认只是当前进程里的临时对象，不会自动写入注册表，因此不会和 CLI 创建的同名集合冲突；只有你显式通过 `REGISTRY` 注册并保存时，它才会变成持久化集合。

如果你的运行时会读取 `AGENTS.md`，用 `syncskills`。如果不会，直接使用 CLI 工具接口或 Python API 即可。

## 🧪 示例与生态集成

MagicSkills 同时提供了两类集成示例：一类是能直接读取 `AGENTS.md` 的 agent / IDE 产品，另一类是通过 tools 或 functions 接入的主流 agent 框架。

### 同一个共享 skill，接入多个 Agent

一个很常见的真实场景是：你有一个可复用的公共 skill，而多个不同的 Agent 应用和 Agent 框架都需要使用它。

例如，同一个 `c_2_ast` skill，可能需要同时供 Claude Code、Cursor、Windsurf、Aider、Codex、AutoGen、CrewAI、LangChain、LangGraph、Haystack、Semantic Kernel、smolagents 和 LlamaIndex 使用。

在这种情况下，推荐做法不是把这个 skill 分别复制到每个 agent 项目里，而是：

1. 先把这个 skill 统一安装或维护在一个共享 skill 池中。
2. 再基于这同一份底层 skill，构建一个或多个命名的 `Skills` 集合。
3. 最后根据目标 agent 的接入方式，用不同形式把这份能力暴露出去。

本仓库里的 examples 展示的正是两条主要接入路径：

- 对于能直接读取 `AGENTS.md` 的 Agent 应用，使用 `addskills + syncskills` 把选定的 skill 子集同步到各自的 `AGENTS.md`
- 对于通过 tools / functions 接入的 Agent 框架，则通过 `magicskills skill-tool` 或 `skills.skill_tool()` 暴露同一份能力集合

所以，虽然这些 examples 面向的是不同的产品和框架，但它们本质上都在演示同一个核心场景：同一个共享 skill，如何在多个不同运行时中被复用。

### 可直接读取 `AGENTS.md` 的 Agent / IDE

- [Claude Code](./ClaudeCode_example/README.md)
- [Cursor](./Cursor_example/README.md)
- [Windsurf](./Windsurf_example/README.md)
- [Aider](./Aider_example/README.md)
- [Codex](./Codex_example/README.md)

### 通过 tools / functions 接入的框架示例

- [AutoGen](./autogen_example/README.md)
- [CrewAI](./crewai_example/README.md)
- [LangChain](./langchain_example/README.md)
- [LangGraph](./langgraph_example/README.md)
- [Haystack](./haystack_example/README.md)
- [Semantic Kernel](./semantic_kernel_example/README.md)
- [smolagents](./smolagents_example/README.md)
- [LlamaIndex](./llamaindex_example/README.md)

## 🗺️ 文档导航

- [工作原理](#how-it-works-cn)：架构与对象模型
- [CLI](./doc/cli.zh-CN.md)：逐条命令参考
- [Python API](./doc/python-api.zh-CN.md)：对象与函数参考
- [使用建议](#tips-cn)：集成指导

<a id="how-it-works-cn"></a>

# ⚙️ 工作原理

## 🧠 核心思想

MagicSkills 的核心不是“一堆命令的集合”，而是一套稳定的三层 skill 管理模型：

- `Skill`：描述单个 skill 目录及其元数据
- `Skills`：描述一个可操作的 skill 集合
- 以 `REGISTRY` 为中心的全局注册表层：描述多个命名 `Skills` 集合如何被注册、加载和持久化

CLI 和 Python API 只是这三层能力的不同入口。无论你调用的是 `readskill`、`install`、`syncskills` 还是 `skill_tool`，最终都会走到同一套核心对象和命令实现。

从推荐的运行时工作流来看，MagicSkills 更接近下面这条链路：

1. 使用 `install` 把相关 skill 安装到本地 skills 目录
2. 安装过程中，MagicSkills 会扫描这些 skill 目录、解析 `SKILL.md` frontmatter，并构造出 `Skill` 对象
3. 所有已安装且被发现的 skill，都会先汇总到内置的 `Allskills` 视图中
4. 然后你再通过 `ALL_SKILLS()` 或 `REGISTRY.get_skills("Allskills")` 从该视图中挑选一个子集，为某个 agent 组合出具体的 `Skills` 集合
5. 最后，这个命名的 `Skills` 集合会被注册到 `REGISTRY` 中，可选地持久化，并同步到 `AGENTS.md`

## 🧱 Skill 层

在 MagicSkills 中，一个有效 skill 的最低要求很简单：它必须是一个目录，并且该目录必须包含 `SKILL.md`。

典型结构如下：

```text
demo-skill/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

其中：

- `SKILL.md` 是 skill 的入口文档，同时也是元数据来源
- `references/`、`scripts/` 和 `assets/` 是常见约定目录，但不是强制要求

在代码中，单个 skill 会被表示为一个 `Skill` 对象。它的核心字段包括：

- `name`：skill 名称，通常就是目录名
- `description`：从 `SKILL.md` frontmatter 中提取
- `path`：skill 目录路径
- `base_dir`：包含该 skill 的 skills 根目录
- `source`：skill 的来源，例如本地路径或 Git 仓库
- `is_global` / `universal`：标记它来自哪种安装范围

这一层解决的是“单个 skill 是什么”的问题。它不管理整组 skill，也不处理注册表持久化。

围绕单个 skill 的常见能力包括：

- `readskill`：读取某个 skill 的 `SKILL.md`
- `showskill`：查看 skill 目录的完整内容
- `createskill_template`：创建标准 skill 骨架
- `addskill`：把一个已有的 skill 注册到某个集合中

## 🧩 Skills 集合层

`Skills` 层解决的是如何把多个 skill 组织成一个可操作的工作集合。

一个 `Skills` 对象可以通过两种方式构建：

- 直接传入 `skill_list`
- 传入 `paths`，由系统自动扫描这些路径下的 skill 目录

构造完成后，这个集合会暴露出一组统一的高层能力：

- `listskill()`：列出集合中的所有 skill
- `readskill(target)`：读取 skill 文件内容
- `showskill(target)`：展示完整 skill 内容
- `execskill(command, ...)`：执行命令并返回结构化结果
- `uploadskill(target)`：通过默认仓库工作流上传一个 skill
- `deleteskill(target)`：从集合中移除某个 skill；如果作用于 `Allskills`，也会删除磁盘上的目录
- `change_tool_description(description)`：更新集合面向 tool 的描述
- `change_cli_description(description)`：更新集合面向 CLI 的描述
- `syncskills(output_path=None, mode="none")`：把当前集合写入 `AGENTS.md`
- `skill_tool(action, arg="")`：以工具函数风格统一分发 list/read/exec

这一层有两个关键设计点：

- `Skills` 同时支持按名称和按路径查找 skill；当名称冲突时，路径是最终的消歧方式
- `Skills` 是一个运行时视图，而不是安装目录本身；同一个 skill 可以被多个命名集合引用

还有一个重要细节：`execskill()` 会在当前进程的工作目录中执行命令，而不会自动切换到 skill 目录。这意味着 MagicSkills 统一了执行入口，但不会悄悄修改你的运行上下文。

## 🗃️ Registry 持久化层

以 `REGISTRY` 为中心的全局注册表层解决的是如何保存和恢复多个命名的 skills 集合。

它的职责包括：

- 维护全局注册表单例 `REGISTRY`
- 确保内置集合 `Allskills` 始终存在
- 创建、查询和删除命名的 skills 集合
- 将集合元数据写入 JSON 文件，并在后续重新加载

默认情况下，注册表存储在：

```text
~/.magicskills/collections.json
```

这里保存的不是每个 skill 的完整文件内容，而只是恢复集合所需的最小信息：

- `paths`
- `tool_description`
- `cli_description`
- `agent_md_path`

换句话说，Registry 保存的是“集合配置”和“skill 路径引用”，而不是 skill 内容的完整副本。真正的 skill 内容仍然保留在文件系统中。

这一层的典型工作流是：

1. 使用 `addskills` 创建一个命名集合
2. 用 `saveskills` 或 `REGISTRY.saveskills()` 持久化它
3. 通过 `loadskills`，或在进程启动时的默认加载逻辑中恢复这些集合
4. 使用 `syncskills` 把某个具体集合写入目标 `AGENTS.md`

所以本质上，Registry 层是 MagicSkills 的项目级配置中心。`Skill` 定义单体，`Skills` 组织工作集，而 `REGISTRY` 让这些集合能跨不同运行周期持续存在。

<a id="cli-cn"></a>

# 🛠️ CLI

完整 CLI 参考文档已迁移至 [doc/cli.zh-CN.md](./doc/cli.zh-CN.md)。
英文版见 [doc/cli.md](./doc/cli.md)。

| 命令                      | 使用场景                                     | 主要能力                                                |
| ------------------------- | -------------------------------------------- | ------------------------------------------------------- |
| `listskill`             | 查看当前内置集合中有哪些 skill               | 列出 skill 名称、描述和 `SKILL.md` 路径               |
| `readskill`             | 读取某个 skill 的说明或任意本地文本文件      | 按 skill 名称或文件路径输出内容                         |
| `execskill`             | 在当前工作目录执行命令                       | 支持流式输出、JSON 输出、no-shell 模式和自定义路径      |
| `syncskills`            | 将一个命名的 skills 集合同步到 `AGENTS.md` | 生成或替换 `<skills_system>` 区块                     |
| `install`               | 从本地路径、Git 仓库或默认来源安装 skill     | 复制 skill 文件并将其注册到 `Allskills`               |
| `addskill`              | 将现有 skill 注册到某个集合中                | 只注册元数据，不复制文件                                |
| `uploadskill`           | 将本地 skill 提交到默认 MagicSkills 仓库     | 自动化执行 fork、push 和 PR 流程                        |
| `deleteskill`           | 从某个集合中删除一个 skill，或全局删除       | 从命名集合中移除，或从 `Allskills` 删除目录并清理引用 |
| `showskill`             | 查看某个 skill 包的完整内容                  | 展示元数据以及 skill 目录中的全部文件                   |
| `addskills`             | 创建一个命名的 skills 集合                   | 为某个 agent 或团队构建隔离的 skill 集                  |
| `listskills`            | 列出所有命名的 skills 集合                   | 输出人类可读格式或 JSON 格式                            |
| `deleteskills`          | 删除一个或多个命名的 skills 集合             | 只删除集合注册信息，不删除 skill 文件                   |
| `changetooldescription` | 修改集合的 `tool_description` 元数据       | 更新面向 tool 的描述，供后续查询和集成使用              |
| `changeclidescription`  | 修改集合的 `cli_description` 元数据        | 更新面向 CLI 的描述，供后续查询和集成使用               |
| `skill-tool`            | 以工具函数风格调用 skill 能力                | 用统一的 JSON 输出分发 list/read/exec                   |

<a id="python-api-cn"></a>

# 🐍 Python API

完整 Python API 参考文档已迁移至 [doc/python-api.zh-CN.md](./doc/python-api.zh-CN.md)。
英文版见 [doc/python-api.md](./doc/python-api.md)。

如果你想直接在脚本、测试、agent 运行时或更高层框架中调用 MagicSkills，而不是通过 CLI，应该使用 Python API。下面的内容与当前 `/root/LLK/MagicSkills/src/magicskills/__init__.py` 中的 `__all__` 保持一致。

```python
from pathlib import Path

from magicskills import (
    ALL_SKILLS,
    REGISTRY,
    Skills,
    listskill,
    readskill,
    execskill,
)
```

**导出项**

- 类型：`Skill`、`Skills`
- 访问器和常量：`REGISTRY`、`ALL_SKILLS()`、`DEFAULT_SKILLS_ROOT`
- 单个 skill 与执行相关函数：`listskill`、`readskill`、`showskill`、`execskill`、`addskill`、`createskill_template`、`install`、`uploadskill`、`deleteskill`
- skills 集合与注册表相关函数：`addskills`、`listskills`、`deleteskills`、`syncskills`、`loadskills`、`saveskills`
- 描述与分发函数：`change_tool_description`、`changetooldescription`、`change_cli_description`、`changeclidescription`、`skill_tool`

**使用建议**

- 如果你已经有一个 `Skills` 对象，优先使用实例方法，例如 `skills.readskill()`、`skills.execskill()` 和 `skills.syncskills()`。
- 如果你想直接复用与 CLI 等价的能力，顶层函数会更直接。
- `changetooldescription` 是 `change_tool_description` 的兼容别名，两者等价。
- `changeclidescription` 是 `change_cli_description` 的兼容别名，两者等价。

<a id="tips-cn"></a>

# 💡 使用建议

## 🧾 通过 `AGENTS.md` 集成

推荐先把所有 skill 安装或维护在同一个共享 skills 根目录下，然后只挑出某个 agent 真正需要的子集，构建一个命名的 skills 集合，最后把这个集合同步进目标 `AGENTS.md`。

这样做有几个好处：

- skill 的物理存储位置保持统一，便于维护、升级和排错
- 不同 agent 可以复用相同的底层 skill，但只暴露各自真正需要的那一部分
- `AGENTS.md` 只保留当前 agent 真正需要看到的 skill，减少上下文噪声

推荐流程如下：

1. 把 skill 安装到一个共享目录，例如 `~/allskills/`、`./.claude/skills` 或 `~/.claude/skills`
2. 使用 `addskills` 创建一个只包含部分 skill 的命名集合
3. 使用 `syncskills` 把该集合写入目标 `AGENTS.md`
4. 根据目标运行时选择同步模式：
   `none` 适合能够根据 `AGENTS.md` 中给出的 skill 信息列表直接使用 skill 的 agent，`cli_description` 适合不能直接使用该列表、需要通过 `magicskills skill-tool` 的 CLI 说明来使用 skill 的 agent
5. 让 agent 只读取这个目标 `AGENTS.md`

示例：

```bash
magicskills install anthropics/skills -t ~/allskills/
magicskills addskills agent1_skills --skill-list pdf docx --agent-md-path /agent_workdir/AGENTS.md
magicskills syncskills agent1_skills
```

如果你希望更细粒度地控制暴露范围，可以先把所有 skill 安装到一个共享目录，再通过多个命名集合为不同 agent 生成不同的 `AGENTS.md` 文件。

## 🔌 不通过 `AGENTS.md` 集成

有些 agent 或框架不会主动读取 `AGENTS.md`。这种情况下，你可以直接把 MagicSkills 的统一分发接口暴露给它们，而不是依赖文档同步。

CLI 入口：

```bash
magicskills skill-tool <action> --arg "<arg>" --name <skills-name>
```

例如：

```bash
magicskills skill-tool listskill --name agent1_skills
magicskills skill-tool readskill --name agent1_skills --arg "<path>"
magicskills skill-tool execskill --name agent1_skills --arg "<command>"
```

Python API 入口：

```python
agent1_skills.skill_tool(action: str, arg: str = "")
```

示例 A，复用已经通过 CLI 创建好的命名集合：

```python
import json

from langchain_core.tools import tool
from magicskills import REGISTRY

agent1_skills = REGISTRY.get_skills("agent1_skills")

print(agent1_skills.skill_tool("listskill"))
print(agent1_skills.skill_tool("readskill", "<path>"))
print(agent1_skills.skill_tool("execskill", "<command>"))

@tool("_skill_tool", description=agent1_skills.tool_description)
def _skill_tool(action: str, arg: str = "") -> str:
    return json.dumps(agent1_skills.skill_tool(action, arg), ensure_ascii=False)
```

示例 B，直接构造一个临时的内存集合：

```python
import json

from langchain_core.tools import tool
from magicskills import ALL_SKILLS, Skills

skill_a = ALL_SKILLS().get_skill("pdf")
skill_b = ALL_SKILLS().get_skill("docx")

agent1_skills = Skills(
    skill_list=[skill_a, skill_b],
    name="agent1_skills",
)

print(agent1_skills.skill_tool("listskill"))
print(agent1_skills.skill_tool("readskill", "<path>"))
print(agent1_skills.skill_tool("execskill", "<command>"))

@tool("_skill_tool", description=agent1_skills.tool_description)
def _skill_tool(action: str, arg: str = "") -> str:
    return json.dumps(agent1_skills.skill_tool(action, arg), ensure_ascii=False)
```

如果 `agent1_skills` 已经通过 CLI 创建过，示例 A 是 Python 侧最直接的接入方式。示例 B 更适合只想在当前进程里临时构造一个集合的场景；它默认不会进入持久化注册表，除非你显式通过 `REGISTRY` 注册并保存。

这种方式适合两类场景：

- agent 支持 tool-call / function-call，但不能读取 `AGENTS.md`
- 你希望由上层程序自己控制何时列出 skill、何时读取 skill、何时执行命令

简单判断就是：

- 会读取 `AGENTS.md` 的 agent，优先使用 `addskills + syncskills`
- 不读取 `AGENTS.md` 的 agent，优先使用 `skill-tool` 或 `skills.skill_tool()`

## 🌱 共享与发展 skill 生态

MagicSkills 不只是一个本地 skill 管理工具。它也希望支持一个可以持续积累、共享和跨项目安装复用的 skill 生态。

如果你已经实现了一个可复用的本地 skill，可以使用 `uploadskill` 把它提交到本项目的 `skills/` 目录，并走默认的 fork / push / PR 工作流。
如果你想复用其他人贡献的 skill，可以使用 `install` 把它们下载到本地，再集成到你自己的 agent 或工作流中。

推荐流程如下：

1. 构建一个可复用的本地 skill，并确保目录中包含 `SKILL.md`
2. 使用 `uploadskill` 把它提交到 MagicSkills 的开源 skill 库
3. 其他用户通过 `install` 安装这些 skill，并把它们组合进自己的 `Skills` 集合或 `AGENTS.md`

示例：

```bash
magicskills uploadskill ./skills/my-skill
magicskills install my-skill
```

## 贡献指南

欢迎提交 Issue 和 Pull Request。

如果是功能想法、工作流建议或较大的行为变更，建议先在 GitHub Discussions 或 Issue 里讨论需求和实现方向，再提交代码。

详细要求见 [CONTRIBUTING.zh-CN.md](./CONTRIBUTING.zh-CN.md)；GitHub 默认识别的英文贡献指南见 [CONTRIBUTING.md](./CONTRIBUTING.md)。你也可以先在 [GitHub Discussions](https://github.com/Narwhal-Lab/MagicSkills/discussions) 发起讨论；仓库同时提供了 [`.github/`](./.github/) 下的 Issue / PR 模板。

# ❓ FAQ

### 一个 skill 的最小结构是什么？

至少需要满足两个条件：

- 它是一个目录
- 目录中包含 `SKILL.md`

像 `references/`、`scripts/` 和 `assets/` 这类目录是常见约定，但都是可选的。

### 我应该用 `syncskills` 还是 `skill-tool`？

根据 agent 的集成方式来选：

- 如果你的 agent 会读取 `AGENTS.md`，优先使用 `addskills + syncskills`
- 如果你的 agent 不读取 `AGENTS.md`，而是通过 tool-call / function-call 集成，优先使用 `skill-tool` 或 `skills.skill_tool()`

前者更适合文档驱动的接入方式；后者更适合程序化直接集成。

### `install` 默认会把 skill 安装到哪里？

默认情况下，skill 会被安装到当前项目下的 `./.claude/skills/`。

如果你使用：

- `--global`，默认目录会变成 `~/.claude/skills`
- `--universal`，默认目录会变成当前项目下的 `./.agent/skills`
- `--global --universal`，默认目录会变成 `~/.agent/skills`
- `--target`，则使用你显式指定的目录

### 同名 skill 冲突时该怎么办？

很多命令既接受 skill 名称，也接受 skill 路径。
如果有多个 skill 同名，就不要再传名称，而是改用显式路径，例如：

```bash
magicskills readskill ./skills/demo/SKILL.md
magicskills deleteskill ./skills/demo
```

简而言之：名称用于方便，路径用于消歧。

### `execskill` 会自动在 skill 目录里执行吗？

不会。`execskill()` 会在当前进程的工作目录中运行，不会自动切换到某个 skill 目录。

这意味着：

- MagicSkills 提供了统一的执行入口
- 但它不会悄悄改变你的运行上下文

如果你的命令依赖某个特定目录，请在命令里自行 `cd` 到该目录，或者在正确的工作目录下调用 MagicSkills。

### 我怎样把本地 skill 分享给别人？

如果你想把本地 skill 贡献到开源生态里，可以使用 `uploadskill` 把它提交到本项目的 `skills/` 目录。之后其他用户就可以通过 `install` 下载并复用它。

典型流程如下：

```bash
magicskills uploadskill ./skills/my-skill
magicskills install my-skill
```

第一条命令负责共享，第二条命令负责复用。

# 📋 环境要求

- **Python** 3.10 / 3.11 / 3.12 / 3.13
- **Git**（用于从远程仓库安装 skill）

---

# 🤝 贡献者

<a href="https://github.com/Narwhal-Lab/MagicSkills/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Narwhal-Lab/MagicSkills" alt="Contributors" />
</a>

---

# ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Narwhal-Lab/MagicSkills&type=Date)](https://star-history.com/#Narwhal-Lab/MagicSkills&Date)

---

# 📜 许可证

[MIT](LICENSE)

---

<div align="center">

**由 [北京大学 Narwhal-Lab](https://github.com/Narwhal-Lab) 开源维护**

</div>
