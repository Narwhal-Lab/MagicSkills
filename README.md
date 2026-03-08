<div align="center">

<!-- 有 Logo 之后取消注释下行 -->

<!-- <img src="./image/Logo.png" alt="MagicSkills" width="360" /> -->

# MagicSkills

**Build skills once. Compose for every agent.**

为多 Agent 场景设计的 Skill 基础设施  
把零散的 `SKILL.md` 升级成可安装、可编排、可同步、可调用的能力系统

统一安装到 `ALL_SKILLS` · 按 Agent 精确组装 `Skills` · 同步到 `AGENTS.md` 或直接暴露为 tool

兼容 `SKILL.md` · 一套 skill 库服务多个 Agent · CLI + Python API · 本地优先、结构透明

[![Python 3.10‑3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://github.com/Narwhal-Lab/MagicSkills)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/Narwhal-Lab/MagicSkills?style=social)](https://github.com/Narwhal-Lab/MagicSkills)

[快速入门](#快速入门) · [What Is MagicSkills](#-what-is-magicskills) · [Why MagicSkills](#why-magicskills) · [How It Works](#how-it-works) · [CLI](#cli) · [Python API](#python-api) · [Tips](#tips)

</div>

---

# 🎯 What Is MagicSkills?

**MagicSkills 是为多 Agent 场景设计的 Skill 基础设施。**

它的目标不是简单存放 `SKILL.md`，而是把分散的 skill 目录变成一套真正可安装、可组合、可同步、可调用的能力基础设施。

借助 MagicSkills，你可以把 skills 按统一方式安装到本地，汇总到 `ALL_SKILLS`，再为不同 agent 挑选需要的子集，组成专属 `Skills`，最后同步到 `AGENTS.md`，或者直接作为 tool function 接入 agent 框架。

换句话说，MagicSkills 做的是这件事：

- 把零散的 `SKILL.md` skill 统一收集起来
- 把“所有 skills”与“某个 agent 需要的 skills”明确区分开
- 把 skill 从静态文档提升为可运行时接入的能力单元
- 让同一套 skill 可以被多个 agent 复用，而不是反复复制

MagicSkills 的核心模型很简单：

- `Skill`：表示一个单独的 skill 目录
- `ALL_SKILLS`：表示当前环境中已安装的全部 skills
- `Skills`：表示某个 agent 或某个场景实际使用的一组 skill
- `SkillsRegistry`：负责管理和持久化命名的 `Skills` 集合

这让 MagicSkills 同时适合两类接入方式：

- **文档同步型 Agent**：把 `Skills` 同步到 `AGENTS.md`
- **工具调用型 Agent**：通过 `skill_tool` 或 Python API 直接接入

**MagicSkills 本质上是在 AI Agent 之上补了一层 skill infrastructure。**

# Why MagicSkills

## 棘手点

大多数 Agent 项目，最后失控的不是模型，而是 skill。

一开始你只有几个 `SKILL.md`，手工维护看起来没问题。但一旦进入多 Agent、多项目、多 skill 的场景，系统很快就会变成这样：

- 同一个 skill 被复制到不同 agent 目录，越改越乱
- `SKILL.md` 明明已经写好了，却只是“文档”，不是“可管理的能力”
- 每个 agent 都在加载一大堆其实根本用不到的 skill
- `AGENTS.md`、tool function、工程脚本之间没有统一入口
- 换一个框架，skill 接入方式就得重写一遍

**MagicSkills 解决的不是“再加一个命令行工具”，而是把 skill 从零散文件，升级成真正可复用的能力基础设施。**

## 它真正厉害的地方

- **把 `SKILL.md` 从静态文档变成可安装、可编排、可调用的能力系统**不是只“存放说明”，而是能真正进入 agent 的运行链路。
- **一套 skill 库，服务多个 Agent**所有 skill 先统一进入 `ALL_SKILLS`，再按不同 agent 选择子集，避免重复维护和能力分叉。
- **每个 Agent 只拿到自己真正需要的 skill**不是把全部 skill 塞给所有 agent，而是按职责拆分，减少上下文噪音，提升可控性。
- **`AGENTS.md` 和 tool function 双入口同时成立**能读 `AGENTS.md` 的 agent 可以直接同步；不读 `AGENTS.md` 的框架也能直接走 `skill_tool`。
- **CLI 管理 + Python API 集成，一条链路打通**从本地安装、集合编排、文档同步，到运行时接入框架，不需要自己拼一堆胶水代码。
- **本地优先、结构透明、没有黑盒**
  skill 是本地目录，集合是显式对象，注册表可落盘，整个系统可查看、可调试、可复用。

## MagicSkills 适合谁

如果你正在做下面这些事，MagicSkills 会非常有价值：

- 你在维护多个 agent，希望它们复用同一批底层 skill
- 你已经有一批 `SKILL.md`，但缺少统一的安装、选择和同步机制
- 你希望 skill 既能进入 `AGENTS.md`，也能变成框架里的 tool
- 你不想把 agent 能力系统做成一堆不可维护的 prompt 拼接

## 一句话总结

**MagicSkills 让你不再“为每个 agent 重写一套 skill”，而是先沉淀一套能力库，再为每个 agent 精确组装它真正需要的部分。**

如果你在做多 Agent，这不是锦上添花的工具。
**这是应该尽早放进工程里的基础设施。**

# 快速入门

下面这段流程展示了 MagicSkills 的推荐闭环：

- 先把 skill 安装到本地目录
- 安装后的 skill 会进入当前进程中的 `ALL_SKILLS`
- 再从 `ALL_SKILLS` 中挑选当前 agent 需要的 skill，组合成一个 `Skills`
- 最后把这个 `Skills` 同步到 `AGENTS.md`，或者以 tool function 的方式接入 agent 框架

## 1. 安装项目

如果你是在本地源码环境中体验项目，最直接的方式是：

```bash
git clone https://github.com/Narwhal-Lab/MagicSkills.git
cd MagicSkills
python -m pip install -e .
magicskills -h
```

也可以直接通过 `pip` 安装：

```bash
pip install MagicSkills
magicskills -h
```

## 2. 下载 skill

```bash
magicskills install anthropics/skills
```

执行完成后，你会得到：

- `anthropics/skills` 仓库中的 skills 会被安装到当前项目下的 `./.claude/skills/`
- 当前进程中的 `ALL_SKILLS` 会持有这些已安装 skill 对应的 `Skill` 实例

## 3. 为某个 agent 选择部分 skill，创建专属 `Skills`

```bash
magicskills createskills agent1_skills --skill-list pdf docx --agent-md-path /agent_workdir/AGENTS.md
```

这条命令表示：

- 从 `ALL_SKILLS` 中选择 `pdf` 和 `docx` 两个 skill
- 创建一个名为 `agent1_skills` 的命名 `Skills` 集合
- 指定这个集合默认同步到 `/agent_workdir/AGENTS.md`

## 4. 生成该 agent 的 `AGENTS.md`

```bash
magicskills syncskills agent1_skills
```

执行后，`agent1_skills` 中的 skill 信息会被同步写入它对应的 `AGENTS.md`。

## 5. 如果该 agent 不读取 `AGENTS.md`

如果你的 agent 不会主动读取 `AGENTS.md`，可以直接使用统一的 CLI tool 入口：

```bash
magicskills skill-tool <action> --arg "<arg>" --name agent1_skills
```

例如：

```bash
magicskills skill-tool listskill --name agent1_skills
magicskills skill-tool readskill --name agent1_skills --arg pdf
magicskills skill-tool execskill --name agent1_skills --arg "echo hello"
```

## 6. 如果你是在 agent 框架中直接使用 Python API

如果你是在 LangChain、LangGraph 或其他 agent 框架中开发，也可以直接通过 Python API 组合 skills，并把 `skill_tool` 暴露成 tool function：

```python
import json
import os

from langchain_core.tools import tool
from magicskills import ALL_SKILLS, Skills

skill_a = ALL_SKILLS.get_skill("pdf")
skill_b = ALL_SKILLS.get_skill("docx")

agent1_skills = Skills(
    skill_list=[skill_a, skill_b],
    name="agent1_skills",
)

print(agent1_skills.skill_tool("listskill"))
print(agent1_skills.skill_tool("readskill", "pdf"))
print(agent1_skills.skill_tool("execskill", "echo hello"))


@tool("_skill_tool", description=agent1_skills.tool_description)
def _skill_tool(action: str, arg: str = "") -> str:
    return json.dumps(agent1_skills.skill_tool(action, arg), ensure_ascii=False)


tools = [_skill_tool]

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL"),
    temperature=0.0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    callbacks=[DebugLLMStart()],
)

agent = create_react_agent(llm, tools)
```

这样有两个好处：

- 对会读取 `AGENTS.md` 的 agent，可以直接走 `createskills + syncskills`
- 对不读取 `AGENTS.md` 的 agent，可以直接走 `skill_tool` 或 Python API 接入

# How It Works

## 核心思想

MagicSkills 的核心不是“把一堆命令堆在一起”，而是把 skill 管理拆成三层稳定模型：

- `Skill`：描述一个单独的 skill 目录及其元数据
- `Skills`：描述一组可操作的 skills 集合
- `SkillsRegistry`：描述多个命名 skills 集合的注册、加载和持久化

CLI 和 Python API 都只是这三层能力的不同入口。无论你执行的是 `readskill`、`install`、`syncskills` 还是 `skill_tool`，最终都会落到同一套核心对象和命令实现上。

从推荐的运行流程看，MagicSkills 更接近下面这条链路：

1. 先通过 `install` 把相关 skill 安装到本地 skills 目录
2. 安装过程中，MagicSkills 会扫描这些 skill 目录，解析 `SKILL.md` frontmatter，并把它们构造成 `Skill`
3. 所有已安装并被发现的 skill，都会先汇总进入内置集合 `ALL_SKILLS`
4. 再从 `ALL_SKILLS` 中挑选一部分 skill，组合成某个具体 agent 要使用的 `Skills` 集合
5. 最后把这个命名的 `Skills` 集合注册进 `SkillsRegistry`，并按需持久化、同步到 `AGENTS.md`

## Skill 层

在 MagicSkills 里，一个 skill 的最小成立条件很简单：它必须是一个目录，并且目录内存在 `SKILL.md`。

典型目录结构如下：

```text
demo-skill/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

其中：

- `SKILL.md` 是 skill 的入口说明文件，也是元数据来源
- `references/`、`scripts/`、`assets/` 是常见约定目录，不是强制要求

代码里，单个 skill 会被表示为一个 `Skill` 对象，核心字段包括：

- `name`：skill 名称，通常就是目录名
- `description`：从 `SKILL.md` frontmatter 中提取
- `path`：该 skill 的目录路径
- `base_dir`：该 skill 所在的 skills 根目录
- `source`：这个 skill 来自哪里，例如本地路径或 Git 仓库
- `is_global` / `universal`：用于标记它来自哪类安装位置

这一层解决的是“单个 skill 是什么”的问题，不负责管理整组 skill，也不负责持久化注册表。

围绕单个 skill 的常见能力有：

- `readskill`：读取某个 skill 的 `SKILL.md`
- `showskill`：查看 skill 目录下的完整文件内容
- `createskill_template`：创建标准 skill 骨架
- `createskill`：把一个已存在的 skill 目录注册进集合

## Skills 集合层

`Skills` 层解决的是“如何把多个 skill 组织成一个可操作的工作集合”。

一个 `Skills` 对象可以通过两种方式构建：

- 直接传入 `skill_list`
- 传入 `paths`，由系统自动扫描这些路径下的 skill 目录

构造完成后，这个集合就拥有统一的高层能力：

- `listskill()`：列出集合里的所有 skill
- `readskill(target)`：读取 skill 文件内容
- `showskill(target)`：展示完整 skill 内容
- `execskill(command, ...)`：执行命令并返回结构化结果
- `uploadskill(target)`：上传 skill 到默认仓库工作流
- `deleteskill(target)`：从集合中移除 skill；如果作用于 `Allskills`，还会删除磁盘目录
- `syncskills(output_path=None)`：把当前集合写入 `AGENTS.md`
- `skill_tool(action, arg="")`：以 tool function 风格统一分发 list/read/exec

这一层有两个关键设计：

- `Skills` 既支持按名称找 skill，也支持按路径找 skill；当名称重复时，路径是最终判定标准
- `Skills` 是运行时视图，不等于安装目录本身；同一个 skill 可以被多个命名集合引用

需要特别注意的是，`execskill()` 当前是在当前进程的工作目录中执行命令，而不是自动切换到 skill 目录执行。这意味着 MagicSkills 统一了执行入口，但不会偷偷改你的运行上下文。

## Registry 持久化层

`SkillsRegistry` 层解决的是“如何保存和恢复多个命名 skills 集合”。

这一层的职责包括：

- 维护全局注册表单例 `REGISTRY`
- 保证内置集合 `Allskills` 一直存在
- 创建、查询、删除命名 skills 集合
- 把集合信息写入 JSON 文件，并在后续重新加载

默认情况下，注册表存储在：

```text
~/.magicskills/collections.json
```

这里保存的不是每个 skill 的完整文件内容，而是集合恢复所需的最小信息：

- `paths`
- `tool_description`
- `agent_md_path`

也就是说，Registry 保存的是“集合配置”和“skill 路径引用”，而不是 skill 内容副本。真正的 skill 内容仍然在文件系统里。

这一层的典型工作流是：

1. 通过 `createskills` 创建一个命名集合
2. 通过 `saveskills` 或 `REGISTRY.saveskills()` 持久化
3. 通过 `loadskills` 或进程启动时的默认加载恢复这些集合
4. 通过 `syncskills` 把某个集合同步到目标 `AGENTS.md`

因此，Registry 层本质上是 MagicSkills 的“项目级配置中心”。`Skill` 定义单体，`Skills` 组织集合，`SkillsRegistry` 负责让这些集合在不同运行周期之间持续存在。

# CLI

安装完成后会暴露 `magicskills` 命令：

```bash
magicskills -h
magicskills <command> -h
```

下面的示例默认以 `bash/zsh` 为例；如果你使用 PowerShell，请按 PowerShell 的引号和转义规则调整命令。

## CLI 命令总览

| 命令                      | 使用场景                                     | 主要能力                                                   |
| ------------------------- | -------------------------------------------- | ---------------------------------------------------------- |
| `listskill`             | 查看当前内置技能集合里有哪些 skill           | 列出 skill 名称、描述、`SKILL.md` 路径                   |
| `readskill`             | 读取 skill 说明或任意本地文本文件            | 按 skill 名称或文件路径输出内容                            |
| `execskill`             | 在当前工作目录执行命令                       | 支持流式输出、JSON 输出、无 shell 模式、自定义 skills 路径 |
| `syncskills`            | 把命名 skills 集合同步进 `AGENTS.md`       | 生成或替换 `<skills_system>` 区块                        |
| `install`               | 从本地目录、Git 仓库或默认技能仓库安装 skill | 复制 skill 文件并注册到 `Allskills`                      |
| `createskill`           | 把一个现成的 skill 目录注册到 `Allskills`  | 不复制文件，只注册元数据                                   |
| `uploadskill`           | 把本地 skill 提交到默认 MagicSkills 仓库     | 自动走 fork、push、PR 流程                                 |
| `deleteskill`           | 删除一个 skill                               | 删除 skill 目录，并从其他集合中剔除同路径 skill            |
| `showskill`             | 审查一个 skill 的完整内容                    | 显示元信息和 skill 目录下所有文件内容                      |
| `createskills`          | 创建一个命名 skills 集合                     | 为 agent 或团队建立独立 skill 集合                         |
| `listskills`            | 查看所有命名 skills 集合                     | 普通文本或 JSON 输出                                       |
| `deleteskills`          | 删除一个命名 skills 集合                     | 只删除集合注册，不删除 skill 文件                          |
| `changetooldescription` | 修改集合的 `tool_description` 元数据       | 更新集合描述，便于后续查询与外部集成                       |
| `skill-tool`            | 以 tool function 风格调用 skill 能力         | 用统一 JSON 输出做 list/read/exec 分发                     |

## 通用约定

- `Allskills` 是内置 skills 集合。`listskill`、`readskill`、`install`、`createskill`、`uploadskill`、`deleteskill`、`showskill` 默认都围绕它工作。
- 命名 skills 集合通过 `createskills` 创建，集合元数据保存在 `~/.magicskills/collections.json`。
- 很多命令同时接受 `skill 名称` 和 `skill 目录路径`。如果同名 skill 有多个，必须传显式路径。
- `install` 的默认安装目录由作用域决定。
- 当前项目默认目录：`./.claude/skills`
- `--global` 默认目录：`~/.claude/skills`
- `--universal` 当前项目目录：`./.agent/skills`
- `--global --universal` 目录：`~/.agent/skills`
- `readskill` 读取 skill 名称时，实际读取的是该 skill 目录下的 `SKILL.md`。
- `execskill` 推荐用 `--` 把 CLI 参数和待执行命令分开。

## `listskill`

**使用场景**

想快速查看当前 `Allskills` 里已经注册了哪些 skill，以及每个 skill 的基础说明。

**命令格式**

```bash
magicskills listskill
```

**参数说明**

无。

**功能示例**

```bash
magicskills listskill
```

输出会按顺序列出每个 skill 的：

- `name`
- `description`
- `path`（指向该 skill 的 `SKILL.md`）

## `readskill`

**使用场景**

你已经知道某个 skill 名称，想直接查看它的 `SKILL.md`；或者你想借这个命令顺手读取任意一个本地文件。

**命令格式**

```bash
magicskills readskill <path>
```

**参数说明**

- `<path>`：可以是文件路径，也可以是 `Allskills` 中的 skill 名称。
- 当传入 skill 名称时，命令会读取对应 skill 目录下的 `SKILL.md`。
- 当传入的是显式路径时，目标必须是文件，不能是目录。
- 如果同名 skill 有多个，必须改传具体文件路径，例如 `./skills/demo/SKILL.md`。

**功能示例**

按 skill 名称读取：

```bash
magicskills readskill demo
```

按 `SKILL.md` 文件路径读取：

```bash
magicskills readskill ./skills/demo/SKILL.md
```

读取任意本地文件：

```bash
magicskills readskill ./AGENTS.md
```

同名 skill 冲突时，改为显式路径：

```bash
magicskills readskill ./vendor-skills/demo/SKILL.md
```

## `execskill`

**使用场景**

你希望在当前工作目录执行一条命令，同时保持调用方式和 MagicSkills 体系一致；也适合给 agent 或自动化脚本暴露统一的执行入口。

**命令格式**

```bash
magicskills execskill [--no-shell] [--json] [--paths [PATHS ...]] -- <command>
```

**参数说明**

- `<command>`：要执行的命令字符串。建议写在 `--` 后面。
- `--no-shell`：关闭 shell 模式，内部会对命令做 `shlex.split()`，更适合直接执行可执行文件及其参数。
- `--json`：不直接流式打印终端输出，而是返回 JSON，字段包含 `command`、`returncode`、`stdout`、`stderr`。
- `--paths [PATHS ...]`：指定自定义 skill 搜索路径，用这些路径构造临时 `Skills` 集合后再执行命令。

**功能示例**

默认流式执行：

```bash
magicskills execskill -- pwd
```

返回 JSON 结果，便于脚本消费：

```bash
magicskills execskill --json -- echo hello
```

无 shell 模式执行 Python：

```bash
magicskills execskill --no-shell -- python -c 'print(123)'
```

在自定义 skills 路径上下文中执行命令：

```bash
magicskills execskill --paths ./.claude/skills ./vendor-skills -- ls -la
```

## `syncskills`

**使用场景**

你已经创建了一个命名 skills 集合，想把它同步到某个 `AGENTS.md` 文件里，让 agent 在系统提示中感知这些 skills。

**命令格式**

```bash
magicskills syncskills <name> [-o OUTPUT] [-y]
```

**参数说明**

- `<name>`：命名 skills 集合名称。
- `-o, --output`：输出文件路径；不传时使用该集合自己的 `agent_md_path`。
- `-y, --yes`：跳过交互确认，直接同步。

**功能示例**

同步到集合默认的 `agent_md_path`：

```bash
magicskills syncskills coder
```

同步到指定文件：

```bash
magicskills syncskills coder --output ./AGENTS.md
```

在 CI 或脚本中跳过确认：

```bash
magicskills syncskills coder -o ./AGENTS.md -y
```

补充说明：

- 如果目标文件不存在，命令会先创建文件并写入基础 `# AGENTS` 标题。
- 如果文件里已存在 `<skills_system>` 区块，命令会替换它；否则会把新块追加到文件末尾。

## `install`

**使用场景**

你想把 skill 安装到当前项目或全局目录中。这个命令既支持安装一个默认仓库里的指定 skill，也支持安装一个本地目录或远程 Git 仓库中的全部 skills。

**命令格式**

```bash
magicskills install <source> [--global] [--universal] [-t TARGET] [-y]
```

**参数说明**

- `<source>`：支持四种输入形式。
- skill 名称：例如 `demo`。命令会克隆默认仓库 `https://github.com/Narwhal-Lab/MagicSkills.git`，只安装同名 skill。
- GitHub 仓库短写：例如 `owner/repo`。命令会转成 `https://github.com/owner/repo.git` 并安装仓库内所有包含 `SKILL.md` 的 skill 目录。
- Git URL：例如 `https://github.com/owner/repo.git` 或 `git@github.com:owner/repo.git`。
- 本地路径：可以是单个 skill 目录，也可以是包含多个 skill 的根目录；命令会递归查找所有 `SKILL.md`。
- `--global`：把安装根目录切到用户 Home，而不是当前项目目录。
- `--universal`：把安装目录从 `.claude/skills` 切到 `.agent/skills`。
- `-t, --target`：自定义安装目录；不能和 `--global` 或 `--universal` 同时使用。
- `-y, --yes`：如果目标目录中已经存在同名 skill，直接覆盖。

**解析顺序**

- 如果 `<source>` 在本地存在，按本地路径处理。
- 如果 `<source>` 看起来像普通 skill 名称且不包含 `/`、`\\`、`.git` 或 URL 前缀，按默认仓库中的 skill 名称处理。
- 其他情况按 Git 仓库处理。

**功能示例**

安装默认 MagicSkills 仓库中的单个 skill：

```bash
magicskills install demo
```

从本地 skills 根目录批量安装：

```bash
magicskills install ./skills
```

从单个本地 skill 目录安装：

```bash
magicskills install ./skills/demo
```

从 GitHub 仓库短写安装：

```bash
magicskills install Narwhal-Lab/MagicSkills
```

从完整 Git URL 安装：

```bash
magicskills install https://github.com/owner/repo.git
```

安装到全局 `.claude/skills`：

```bash
magicskills install demo --global
```

安装到当前项目 `.agent/skills`：

```bash
magicskills install demo --universal
```

安装到自定义目录：

```bash
magicskills install demo --target ./custom-skills
```

覆盖同名 skill：

```bash
magicskills install demo --target ./custom-skills -y
```

补充说明：

- 远程安装依赖 `git`。
- 安装完成后，CLI 会输出每个实际落盘的目录路径。
- 安装流程会把已安装的 skill 注册进当前进程中的 `Allskills` 集合。

## `createskill`

**使用场景**

你已经手写好了一个 skill 目录，只想把它注册进 `Allskills`，而不是重新复制一份。

**命令格式**

```bash
magicskills createskill <path> [--source SOURCE]
```

**参数说明**

- `<path>`：skill 目录路径，目录内必须包含 `SKILL.md`。
- `--source`：可选，给这个 skill 记录来源信息；不传时默认记录 skill 所在父目录的绝对路径。

**功能示例**

注册一个本地 skill 目录：

```bash
magicskills createskill ./skills/my-skill
```

显式记录来源仓库或来源目录：

```bash
magicskills createskill ./skills/my-skill --source https://github.com/owner/repo.git
```

补充说明：

- 这个命令的行为是“注册已有 skill”，不是“生成 skill 模板”。
- `description` 会从 `SKILL.md` frontmatter 中提取。

## `uploadskill`

**使用场景**

你已经在本地准备好了一个 skill，想把它自动提交到默认 MagicSkills 仓库，并创建 Pull Request。

**命令格式**

```bash
magicskills uploadskill <source>
```

**参数说明**

- `<source>`：可以是 `Allskills` 中的 skill 名称，也可以是本地 skill 目录路径。

**默认工作流**

- 校验 `source` 对应目录存在且包含 `SKILL.md`。
- 检查 `gh` 是否已安装、是否已登录。
- `gh repo fork Narwhal-Lab/MagicSkills --clone`
- 拉取上游默认分支并创建新分支，分支名格式类似 `fix/upload-<skill>-<timestamp>`
- 把 skill 复制到仓库内的 `skills/<skill-name>`
- 提交、推送并创建 PR

**功能示例**

按 skill 名称上传：

```bash
magicskills uploadskill demo
```

按本地路径上传：

```bash
magicskills uploadskill ./skills/demo
```

补充说明：

- 如果同名 skill 在 `Allskills` 中有多个，必须改传 skill 目录路径。
- 在交互式终端里，如果 `gh` 缺失，CLI 会询问是否尝试自动安装；如果 `gh` 未登录，会询问是否运行 `gh auth login`。
- 如果 `gh auth login` 不方便执行，CLI 还会询问是否临时输入 `GH_TOKEN`。
- 成功后会输出 `Repo`、`Branch`、`Target`、`Committed`、`Pushed`、`PR URL` 等结果字段。

## `deleteskill`

**使用场景**

你想彻底删除一个 skill，而不只是把它从某个列表里隐藏。

**命令格式**

```bash
magicskills deleteskill <target>
```

**参数说明**

- `<target>`：可以是 skill 名称，也可以是 skill 目录路径。

**功能示例**

按名称删除：

```bash
magicskills deleteskill demo
```

同名 skill 冲突时按路径删除：

```bash
magicskills deleteskill ./skills/demo
```

补充说明：

- 这个 CLI 命令默认作用于内置的 `Allskills`。
- 删除时会直接移除实际 skill 目录，不会二次确认。
- 删除成功后，如果其他命名集合里也引用了同一路径的 skill，这些集合中的对应项也会一起被剔除。

## `showskill`

**使用场景**

你想完整审查一个 skill 包，而不只是看 `SKILL.md`。例如在 code review、提交流程、排查二进制文件或检查脚本入口时很有用。

**命令格式**

```bash
magicskills showskill <target>
```

**参数说明**

- `<target>`：可以是 skill 名称，也可以是 skill 目录路径。

**功能示例**

按名称查看：

```bash
magicskills showskill demo
```

按路径查看：

```bash
magicskills showskill ./skills/demo
```

补充说明：

- 输出会先展示 `Skill Overview`，包括名称、描述、skill 目录、base_dir、`SKILL.md` 路径和安装来源。
- 然后会展示 skill 目录下的所有文件内容。
- 如果遇到二进制文件，会显示 `[binary file omitted: <size> bytes]`，不会直接打印乱码。

## `createskills`

**使用场景**

你需要给某个 agent、团队或工作流创建一个独立的命名 skills 集合，再配合 `syncskills` 生成对应的 `AGENTS.md`。

**命令格式**

```bash
magicskills createskills <name> [--skill-list [SKILLS ...]] [--paths [PATHS ...]] [--tool-description TEXT] [--agent-md-path PATH]
```

**参数说明**

- `<name>`：新集合名称，必须唯一。
- `--skill-list [SKILLS ...]`：显式指定要纳入集合的 skill。每一项都可以是 skill 名称或 skill 目录路径，底层会从 `Allskills` 里解析。
- `--paths [PATHS ...]`：把这些路径对应的 skills 纳入新集合。常见传法有两种。
- 传某个 skill 目录路径，例如 `./.claude/skills/demo`
- 传某个 skills 根目录，例如 `./.claude/skills`
- `--tool-description`：覆盖该集合的 `tool_description` 元数据。
- `--agent-md-path`：指定该集合默认同步到哪个 `AGENTS.md` 文件。

**功能示例**

创建一个空集合：

```bash
magicskills createskills coder
```

按显式 skill 列表创建：

```bash
magicskills createskills reviewer --skill-list demo code-review
```

按显式 skill 路径创建：

```bash
magicskills createskills reviewer --skill-list ./.claude/skills/code-review
```

从一个 skills 根目录构造集合：

```bash
magicskills createskills coder --paths ./.claude/skills
```

只纳入一个具体 skill：

```bash
magicskills createskills reviewer --paths ./.claude/skills/code-review
```

同时指定多个路径：

```bash
magicskills createskills fullstack --paths ./.claude/skills ./vendor-skills
```

创建集合时顺带设置元数据：

```bash
magicskills createskills coder \
  --paths ./.claude/skills \
  --tool-description "Unified skill tool for coding tasks" \
  --agent-md-path ./agents/coder/AGENTS.md
```

补充说明：

- 不传 `--skill-list` 和 `--paths` 时，当前版本会创建一个空的命名集合。
- `--skill-list` 和 `--paths` 不能同时使用。
- `--skill-list` 中的每一项都必须能在当前 `Allskills` 中解析到唯一 skill；如果名称重复，请改传 skill 目录路径。
- `--paths` 中的路径需要能解析到当前 `Allskills` 里已有的 skills或其上层 skills 根目录。
- 成功后会输出集合名和 `Skills count`。

## `listskills`

**使用场景**

你想检查当前机器上已经注册了哪些命名 skills 集合，或者把这些集合信息交给脚本继续处理。

**命令格式**

```bash
magicskills listskills [--json]
```

**参数说明**

- `--json`：以 JSON 数组输出；不传时输出人类可读的盒状文本。

**功能示例**

查看所有集合：

```bash
magicskills listskills
```

以 JSON 形式输出：

```bash
magicskills listskills --json
```

JSON 输出中每个集合对象包含：

- `name`
- `skills_count`
- `paths`
- `tool_description`
- `agent_md_path`

## `deleteskills`

**使用场景**

某个命名 skills 集合已经不用了，你只想删除它的注册信息，但保留原始 skill 文件。

**命令格式**

```bash
magicskills deleteskills <name>
```

**参数说明**

- `<name>`：要删除的命名 skills 集合名称。

**功能示例**

删除一个命名集合：

```bash
magicskills deleteskills coder
```

补充说明：

- `deleteskills` 只删除集合注册信息，不会删除 skill 目录。
- 内置集合 `Allskills` 不能被删除。

## `changetooldescription`

**使用场景**

你想调整某个命名 skills 集合的工具描述文本，方便后续用 `listskills --json` 或外部集成读取。

**命令格式**

```bash
magicskills changetooldescription <name> <description>
```

**参数说明**

- `<name>`：命名 skills 集合名称。
- `<description>`：新的工具描述文本；如果包含空格，记得加引号。

**功能示例**

更新描述：

```bash
magicskills changetooldescription coder "Unified skill tool for coding and review tasks"
```

更新后查看：

```bash
magicskills listskills --json
```

## `skill-tool`

**使用场景**

当你需要一个稳定的、面向 agent/tool-call 的 CLI 包装层时，使用这个命令最合适。它会把 `listskill`、`readskill`、`execskill` 统一成 JSON 返回结构，并用退出码表示成功或失败。

**命令格式**

```bash
magicskills skill-tool <action> [--arg ARG] [--name NAME]
```

**参数说明**

- `<action>`：动作名，支持以下主动作和别名。
- `listskill`、`list`、`list_metadata`
- `readskill`、`read`、`read_file`
- `execskill`、`exec`、`run_command`
- `--arg ARG`：动作参数。
- 对 `listskill` 基本可留空。
- 对 `readskill`，传 skill 名称或文件路径。
- 对 `execskill`，可传普通命令字符串、JSON 字符串，或旧格式 `name::command`。
- `--name NAME`：指定要使用哪个命名 skills 集合；不传时默认使用 `Allskills`。

**功能示例**

列出默认集合中的 skill：

```bash
magicskills skill-tool listskill
```

在指定命名集合里读取某个 skill：

```bash
magicskills skill-tool readskill --name coder --arg demo
```

读取显式文件路径：

```bash
magicskills skill-tool readskill --arg ./skills/demo/SKILL.md
```

执行普通命令字符串：

```bash
magicskills skill-tool execskill --arg "echo hello"
```

以 JSON 参数执行命令：

```bash
magicskills skill-tool execskill --arg '{"command":"echo hello"}'
```

兼容旧格式 `name::command`：

```bash
magicskills skill-tool execskill --arg 'demo::echo hello'
```

补充说明：

- 输出始终是 JSON。
- 当返回中 `ok` 为 `true` 时，CLI 退出码为 `0`；否则退出码为 `1`。
- 传入未知 action 时，会返回 `{"ok": false, "error": "Unknown action: ..."}`。

# Python API

如果你希望在脚本、测试、Agent runtime 或上层框架中直接调用 MagicSkills，而不是走 CLI，那么就使用 Python API。下面的内容以 `/root/LLK/MagicSkills/src/magicskills/__init__.py` 当前 `__all__` 为准。

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

**导出分组**

- 类型：`Skill`、`Skills`、`SkillsRegistry`
- 单例与常量：`REGISTRY`、`ALL_SKILLS`、`DEFAULT_SKILLS_ROOT`
- 单 skill / 执行类函数：`listskill`、`readskill`、`showskill`、`execskill`、`createskill`、`createskill_template`、`install`、`uploadskill`、`deleteskill`
- skills 集合 / 注册表函数：`createskills`、`listskills`、`deleteskills`、`syncskills`、`loadskills`、`saveskills`
- 描述与分发函数：`change_tool_description`、`changetooldescription`、`skill_tool`

**使用建议**

- 如果你已经有 `Skills` 对象，优先调用实例方法，例如 `skills.readskill()`、`skills.execskill()`、`skills.syncskills()`。
- 如果你想直接复用 CLI 同名能力，使用顶层函数更直接。
- `changetooldescription` 是 `change_tool_description` 的兼容别名，两者等价。

## `Skill`

**使用场景**

当你需要手动构造一个 skill 元数据对象，或者想把 skill 元信息序列化给其他系统时使用。

**构造签名**

```python
Skill(
    name: str,
    description: str,
    path: Path,
    base_dir: Path,
    source: str,
    is_global: bool = False,
    universal: bool = False,
)
```

**参数说明**

- `name`：skill 名称，通常等于 skill 目录名。
- `description`：skill 简述，通常来自 `SKILL.md` frontmatter 的 `description`。
- `path`：skill 目录路径。
- `base_dir`：skill 所在的 skills 根目录。
- `source`：来源信息，例如本地路径、Git URL、仓库地址。
- `is_global`：是否来自全局目录。
- `universal`：是否来自 `.agent/skills` 体系。

**可用能力**

- 直接访问 dataclass 字段。
- 调用 `to_dict()` 获得 JSON 友好的字典。

**功能示例**

```python
from pathlib import Path
from magicskills import Skill

skill = Skill(
    name="demo",
    description="Demo skill",
    path=Path("./skills/demo").resolve(),
    base_dir=Path("./skills").resolve(),
    source="https://github.com/example/repo.git",
)

print(skill.name)
print(skill.to_dict())
```

## `Skills`

**使用场景**

当你希望在内存里维护一组 skills，并以面向对象的方式完成列表、读取、执行、同步、删除等操作时使用。

**构造签名**

```python
Skills(
    skill_list: Iterable[Skill] | None = None,
    paths: Iterable[Path | str] | None = None,
    tool_description: str | None = None,
    agent_md_path: Path | str | None = None,
    name: str = "all",
)
```

**参数说明**

- `skill_list`：显式传入的 `Skill` 对象列表。
- `paths`：skills 根目录列表，或单个 skill 目录列表；构造时会自动发现其中的 skill。
- `tool_description`：该集合的 tool 描述文本。
- `agent_md_path`：该集合默认同步到哪个 `AGENTS.md`。
- `name`：集合名称，默认是 `"all"`。

**补充说明**

- 如果同时传 `skill_list` 和 `paths`，两者必须能解析出完全一致的 skills，否则会抛出 `ValueError`。
- 只传 `paths` 时，会自动扫描目录下的 `SKILL.md`。
- 只传 `skill_list` 时，会自动反推出 `paths`。
- `agent_md_path` 默认为当前工作目录下的 `AGENTS.md`。

**常用实例方法**

- `get_skill(target)`：按名称或目录路径拿到单个 `Skill`
- `createskill(skill_path, source=None)`
- `deleteskill(target)`
- `listskill()`
- `readskill(target)`
- `uploadskill(target)`
- `showskill(target)`
- `execskill(command, env=None, shell=True, timeout=None, stream=False)`
- `change_tool_description(description)`
- `syncskills(output_path=None)`
- `skill_tool(action, arg="")`

这些实例方法和下面的同名顶层函数一一对应；如果你更偏好函数式风格，可以直接用顶层函数。

**功能示例**

```python
from magicskills import Skills

skills = Skills(
    paths=["./.claude/skills"],
    name="coder",
    agent_md_path="./agents/coder/AGENTS.md",
)

print(skills.listskill())
print(skills.readskill("demo"))

result = skills.execskill("echo hello", stream=False)
print(result.returncode, result.stdout)

skills.syncskills()
```

## `SkillsRegistry`

**使用场景**

当你需要维护多个命名 skills 集合，并把这些集合持久化到某个 JSON 文件时使用。

**构造签名**

```python
SkillsRegistry(store_path: Path | None = None)
```

**参数说明**

- `store_path`：注册表文件路径；不传时默认使用 `~/.magicskills/collections.json`。

**核心方法**

- `createskills(name, skill_list=None, paths=None, tool_description=None, agent_md_path=None, save=True)`
- `listskills()`
- `get_skills(name)`
- `deleteskills(name)`
- `loadskills(path=None)`
- `saveskills(path=None)`

如果你给 `createskills()` 传 `paths`，这些路径需要先能在当前 `Allskills` 中解析成具体 skill 或 skills 根目录。

**功能示例**

```python
from pathlib import Path
from magicskills import SkillsRegistry

registry = SkillsRegistry(store_path=Path("./collections.json"))
registry.createskills(name="coder")
print([item.name for item in registry.listskills()])

coder = registry.get_skills("coder")
print(coder.agent_md_path)

registry.saveskills()
registry.loadskills()
```

## `REGISTRY`

**使用场景**

这是进程级的全局 `SkillsRegistry` 单例。大多数命名集合操作都可以直接围绕它完成。

**参数说明**

无。它是现成对象，不需要实例化。

**功能示例**

```python
from magicskills import REGISTRY

print([item.name for item in REGISTRY.listskills()])
```

## `ALL_SKILLS`

**使用场景**

这是内置的 `Skills` 集合单例，代表默认 skills 视图。很多顶层函数都适合直接以它作为第一个参数。

**参数说明**

无。它是现成对象，不需要实例化。

**功能示例**

```python
from magicskills import ALL_SKILLS, listskill, readskill

print(listskill(ALL_SKILLS))
print(readskill(ALL_SKILLS, "demo"))
```

## `DEFAULT_SKILLS_ROOT`

**使用场景**

你想拿到当前工作目录默认的 `.claude/skills` 路径，给自己的初始化逻辑或安装逻辑复用。

**参数说明**

无。它是常量，值等于 `Path.cwd() / ".claude" / "skills"`。

**功能示例**

```python
from magicskills import DEFAULT_SKILLS_ROOT

print(DEFAULT_SKILLS_ROOT)
```

## `listskill()`

**使用场景**

想把某个 `Skills` 集合里的技能列表格式化成纯文本输出。

**签名**

```python
listskill(skills: Skills) -> str
```

**参数说明**

- `skills`：要列出的 `Skills` 集合。

**返回值**

- 返回格式化后的多行字符串。

**功能示例**

```python
from magicskills import ALL_SKILLS, listskill

print(listskill(ALL_SKILLS))
```

## `readskill()`

**使用场景**

按 skill 名称读取 `SKILL.md`，或按文件路径读取任意文本文件。

**签名**

```python
readskill(skills: Skills, target: str | Path) -> str
```

**参数说明**

- `skills`：目标 `Skills` 集合。
- `target`：skill 名称，或显式文件路径。

**返回值**

- 返回文件文本内容。

**功能示例**

按 skill 名称读取：

```python
from magicskills import ALL_SKILLS, readskill

content = readskill(ALL_SKILLS, "demo")
print(content)
```

按路径读取：

```python
from pathlib import Path
from magicskills import ALL_SKILLS, readskill

content = readskill(ALL_SKILLS, Path("./skills/demo/SKILL.md"))
print(content)
```

## `showskill()`

**使用场景**

你不只想看 `SKILL.md`，而是想看整个 skill 目录的元信息和所有文件内容。

**签名**

```python
showskill(skills: Skills, target: str | Path) -> str
```

**参数说明**

- `skills`：目标 `Skills` 集合。
- `target`：skill 名称，或 skill 目录路径。

**返回值**

- 返回带格式的完整展示文本。

**功能示例**

```python
from magicskills import ALL_SKILLS, showskill

print(showskill(ALL_SKILLS, "demo"))
```

## `execskill()`

**使用场景**

当你想用 Python API 执行命令，并拿到结构化执行结果时使用。

**签名**

```python
execskill(
    skills: Skills,
    command: str,
    env: Mapping[str, str] | None = None,
    shell: bool = True,
    timeout: float | None = None,
    stream: bool = False,
) -> ExecResult
```

**参数说明**

- `skills`：当前 API 形态要求传入的 `Skills` 集合。
- `command`：要执行的命令字符串。
- `env`：保留参数；当前实现不会把它注入子进程环境。
- `shell`：是否通过 shell 执行；默认 `True`。
- `timeout`：超时时间，单位秒；不传表示不限制。
- `stream`：是否直接把输出流式打印到当前终端；默认 `False`。

**返回值**

- 返回 `ExecResult`，字段有 `command`、`returncode`、`stdout`、`stderr`。
- 当 `stream=True` 时，`stdout` 和 `stderr` 会是空字符串，因为输出已经直接写到终端。

**功能示例**

拿结构化结果：

```python
from magicskills import ALL_SKILLS, execskill

result = execskill(ALL_SKILLS, "echo hello", stream=False)
print(result.returncode, result.stdout, result.stderr)
```

无 shell 模式执行：

```python
from magicskills import ALL_SKILLS, execskill

result = execskill(ALL_SKILLS, "python -c 'print(123)'", shell=False)
print(result.stdout)
```

流式执行：

```python
from magicskills import ALL_SKILLS, execskill

execskill(ALL_SKILLS, "pytest -q", stream=True)
```

带超时：

```python
from magicskills import ALL_SKILLS, execskill

result = execskill(ALL_SKILLS, "sleep 1", timeout=2)
print(result.returncode)
```

## `createskill_template()`

**使用场景**

你需要先生成一个最小可用的 skill 目录骨架，再去补写 `SKILL.md`、脚本和资料文件。

**签名**

```python
createskill_template(name: str, base_dir: Path | str) -> Path
```

**参数说明**

- `name`：skill 名称，也会作为目录名。
- `base_dir`：要在哪个 skills 根目录下创建该 skill。

**返回值**

- 返回新建 skill 目录的 `Path`。

**功能示例**

```python
from magicskills import createskill_template

skill_dir = createskill_template("my-skill", "./skills")
print(skill_dir)
```

这个 API 会确保以下内容存在：

- `<base_dir>/<name>/`
- `references/`
- `scripts/`
- `assets/`
- 默认 `SKILL.md`

## `createskill()`

**使用场景**

你已经有一个现成 skill 目录，只想把它注册到某个 `Skills` 集合里。

**签名**

```python
createskill(
    skills: Skills,
    skill_path: Path | str,
    source: str | Path | None = None,
) -> Path
```

**参数说明**

- `skills`：目标 `Skills` 集合。
- `skill_path`：skill 目录路径，目录内必须包含 `SKILL.md`。
- `source`：可选来源信息；不传时默认记录父目录的绝对路径。

**返回值**

- 返回注册的 skill 目录 `Path`。

**功能示例**

注册到 `ALL_SKILLS`：

```python
from magicskills import ALL_SKILLS, createskill

path = createskill(ALL_SKILLS, "./skills/demo")
print(path)
```

显式记录来源：

```python
from magicskills import ALL_SKILLS, createskill

path = createskill(
    ALL_SKILLS,
    "./skills/demo",
    source="https://github.com/example/repo.git",
)
print(path)
```

补充说明：

- 这个 API 注册的是“已有目录”，不会复制文件。
- 如果你把 skill 注册到某个非 `ALL_SKILLS` 集合，同一 skill 也会同步加入 `ALL_SKILLS`。
- 如果目标集合属于当前 `REGISTRY`，注册表会自动保存。

## `install()`

**使用场景**

你想通过 Python API 直接安装 skill，而不是调用 CLI。

**签名**

```python
install(
    source: str | None = None,
    global_: bool = False,
    universal: bool = False,
    yes: bool = False,
    target_root: Path | str | None = None,
) -> list[Path]
```

**参数说明**

- `source`：本地路径、GitHub 仓库短写、Git URL 或默认仓库中的 skill 名称。
- `global_`：是否使用 Home 作为安装基准目录。
- `universal`：是否把安装根目录切到 `.agent/skills`。
- `yes`：目标已存在时是否直接覆盖。
- `target_root`：自定义安装目录；不能和 `global_`、`universal` 同时使用。

**返回值**

- 返回实际安装落盘的目录列表。

**功能示例**

从默认仓库安装单个 skill：

```python
from magicskills import install

paths = install("demo")
print(paths)
```

从本地目录批量安装：

```python
from magicskills import install

paths = install("./skills", target_root="./custom-skills", yes=True)
print(paths)
```

从 GitHub 仓库短写安装：

```python
from magicskills import install

paths = install("owner/repo", global_=True)
print(paths)
```

补充说明：

- 解析顺序与 CLI 一致：本地路径优先，其次是默认仓库 skill 名称，最后是 Git 仓库。
- 安装完成后会把 skill 注册到 `ALL_SKILLS`，并持久化到当前 `REGISTRY`。

## `uploadskill()`

**使用场景**

你想在 Python 代码里直接触发 skill 上传、fork、push、PR 流程。

**签名**

```python
uploadskill(
    skills: Skills | Path | str,
    target: str | Path | None = None,
) -> UploadResult
```

**参数说明**

- `skills`：有两种合法传法。
- 传 `Skills` 对象：此时必须再传 `target`，表示从该集合中按名称或路径定位 skill。
- 传 `Path` 或 `str` 路径：此时 `target` 保持 `None`，第一参数本身就是 skill 目录。
- `target`：当第一参数是 `Skills` 时使用，表示 skill 名称或 skill 目录路径。

**返回值**

- 返回 `UploadResult`，字段有 `skill_name`、`repo`、`branch`、`remote_subpath`、`committed`、`pushed`、`push_remote`、`push_branch`、`pr_url`、`pr_created`。

**功能示例**

从 `ALL_SKILLS` 按名称上传：

```python
from magicskills import ALL_SKILLS, uploadskill

result = uploadskill(ALL_SKILLS, "demo")
print(result.pr_url)
```

按本地路径直接上传：

```python
from magicskills import uploadskill

result = uploadskill("./skills/demo")
print(result.repo, result.push_branch)
```

**补充说明**

- 运行前需要满足和 CLI 相同的前置条件：本地已安装并认证 `gh`，并且目标 skill 目录存在 `SKILL.md`。
- 如果你传的是 `Skills` 对象且同名 skill 有多个，请改传显式目录路径。

## `deleteskill()`

**使用场景**

你想从 Python API 删除一个 skill；如果作用在 `ALL_SKILLS` 上，会同时删除磁盘目录。

**签名**

```python
deleteskill(skills: Skills, target: str) -> str
```

**参数说明**

- `skills`：目标 `Skills` 集合。
- `target`：skill 名称或 skill 目录路径。

**返回值**

- 返回被删除 skill 的解析后路径字符串。

**功能示例**

只从命名集合里移除：

```python
from magicskills import REGISTRY, deleteskill

team = REGISTRY.get_skills("coder")
deleted = deleteskill(team, "./skills/demo")
print(deleted)
```

从 `ALL_SKILLS` 彻底删除：

```python
from magicskills import ALL_SKILLS, deleteskill

deleted = deleteskill(ALL_SKILLS, "demo")
print(deleted)
```

补充说明：

- 传非 `ALL_SKILLS` 时，只从该集合移除，不删磁盘。
- 传 `ALL_SKILLS` 时，会删除实际 skill 目录，并同步从其他命名集合中剔除同路径 skill。

## `createskills()`

**使用场景**

你想创建一个命名 `Skills` 集合，并立即注册到全局 `REGISTRY` 中。

**签名**

```python
createskills(
    name: str,
    skill_list: list[Skill] | str | None = None,
    paths: list[str] | None = None,
    tool_description: str | None = None,
    agent_md_path: str | None = None,
) -> Skills
```

**参数说明**

- `name`：集合名称。
- `skill_list`：可直接传 `Skill` 列表；也可以传单个 skill 名称字符串。
- `paths`：skills 根目录或 skill 目录路径字符串列表。
- `tool_description`：集合的 tool 描述文本。
- `agent_md_path`：该集合默认同步到哪个 `AGENTS.md`。

**返回值**

- 返回创建后的 `Skills` 对象，并会默认持久化到注册表。

**功能示例**

创建空集合：

```python
from magicskills import createskills

skills = createskills("coder")
print(skills.name, len(skills.skills))
```

按路径创建：

```python
from magicskills import createskills

# 前提：这些 skills 已经通过 install/createskill 进入 ALL_SKILLS
skills = createskills(
    "coder",
    paths=["./.claude/skills"],
    tool_description="Unified skill tool for coding tasks",
    agent_md_path="./agents/coder/AGENTS.md",
)
print(skills.agent_md_path)
```

按单个 skill 名称创建：

```python
from magicskills import createskills

# 前提：ALL_SKILLS 中已经能解析到名为 demo 的 skill
skills = createskills("reviewer", skill_list="demo")
print([item.name for item in skills.skills])
```

**补充说明**

- 不传 `paths` 和 `skill_list` 时，会创建空集合。
- `paths` 和字符串形式的 `skill_list` 都依赖当前 `ALL_SKILLS` 能先解析到对应 skill 或其上层 skills 根目录。

## `listskills()`

**使用场景**

列出全局 `REGISTRY` 当前管理的所有命名集合。

**签名**

```python
listskills() -> list[Skills]
```

**参数说明**

无。

**返回值**

- 返回 `Skills` 对象列表。

**功能示例**

```python
from magicskills import listskills

for item in listskills():
    print(item.name, len(item.skills))
```

## `deleteskills()`

**使用场景**

删除一个命名 `Skills` 集合的注册信息。

**签名**

```python
deleteskills(name: str) -> None
```

**参数说明**

- `name`：要删除的命名集合名称。

**功能示例**

```python
from magicskills import deleteskills

deleteskills("coder")
```

**补充说明**

- 只删除集合注册，不删除 skill 文件。
- `Allskills` 不能被删除。

## `syncskills()`

**使用场景**

把一个 `Skills` 集合同步进 `AGENTS.md` 文件。

**签名**

```python
syncskills(skills: Skills, output_path: Path | str | None = None) -> Path
```

**参数说明**

- `skills`：要同步的 `Skills` 集合。
- `output_path`：目标文件路径；不传时使用 `skills.agent_md_path`。

**返回值**

- 返回最终写入的文件路径 `Path`。

**功能示例**

同步到集合默认文件：

```python
from magicskills import REGISTRY, syncskills

coder = REGISTRY.get_skills("coder")
path = syncskills(coder)
print(path)
```

同步到指定文件：

```python
from magicskills import REGISTRY, syncskills

coder = REGISTRY.get_skills("coder")
path = syncskills(coder, "./AGENTS.md")
print(path)
```

## `loadskills()`

**使用场景**

从磁盘重新加载全局 `REGISTRY` 的持久化状态。

**签名**

```python
loadskills(path: str | None = None) -> list[Skills]
```

**参数说明**

- `path`：可选注册表 JSON 路径；不传则使用当前 `REGISTRY` 的存储路径。

**返回值**

- 返回加载后的 `Skills` 列表。

**功能示例**

```python
from magicskills import loadskills

collections = loadskills("./collections.json")
print([item.name for item in collections])
```

## `saveskills()`

**使用场景**

把当前全局 `REGISTRY` 的状态写回磁盘。

**签名**

```python
saveskills(path: str | None = None) -> str
```

**参数说明**

- `path`：可选输出路径；不传则保存到当前 `REGISTRY` 的存储路径。

**返回值**

- 返回写入文件路径字符串。

**功能示例**

```python
from magicskills import saveskills

saved_path = saveskills("./collections.json")
print(saved_path)
```

## `change_tool_description()` / `changetooldescription()`

**使用场景**

修改某个 `Skills` 集合上的 `tool_description` 元数据。

**签名**

```python
change_tool_description(skills: Skills, description: str) -> None
changetooldescription(skills: Skills, description: str) -> None
```

**参数说明**

- `skills`：目标 `Skills` 集合。
- `description`：新的描述文本。

**功能示例**

```python
from magicskills import REGISTRY, change_tool_description

coder = REGISTRY.get_skills("coder")
change_tool_description(coder, "Unified skill tool for coding and review tasks")
```

用兼容别名调用：

```python
from magicskills import REGISTRY, changetooldescription

coder = REGISTRY.get_skills("coder")
changetooldescription(coder, "Unified skill tool")
```

**补充说明**

- 如果目标集合属于当前 `REGISTRY`，这个 API 会自动把修改持久化到注册表。

## `skill_tool()`

**使用场景**

你想在 Python 里复用 agent/tool-call 风格的统一入口，而不自己手动分发 `listskill`、`readskill`、`execskill`。

**签名**

```python
skill_tool(skills: Skills, action: str, arg: str = "") -> dict[str, object]
```

**参数说明**

- `skills`：目标 `Skills` 集合。
- `action`：动作名，支持：
- `listskill`、`list`、`list_metadata`
- `readskill`、`read`、`read_file`
- `execskill`、`exec`、`run_command`
- `arg`：动作参数。
- 对 `listskill` 可以留空。
- 对 `readskill` 传 skill 名称或文件路径。
- 对 `execskill` 可传普通命令字符串、JSON 字符串，或旧格式 `name::command`。

**返回值**

- 返回字典，典型结构为 `{"ok": True, "action": "...", "result": ...}`。
- 未知 action 或运行失败时，返回 `{"ok": False, "error": "..."}`。

**功能示例**

列出 skills：

```python
from magicskills import ALL_SKILLS, skill_tool

print(skill_tool(ALL_SKILLS, "listskill"))
```

读取 skill：

```python
from magicskills import ALL_SKILLS, skill_tool

print(skill_tool(ALL_SKILLS, "readskill", "demo"))
```

执行普通命令：

```python
from magicskills import ALL_SKILLS, skill_tool

print(skill_tool(ALL_SKILLS, "execskill", "echo hello"))
```

执行 JSON 形式命令：

```python
from magicskills import ALL_SKILLS, skill_tool

print(skill_tool(ALL_SKILLS, "execskill", '{"command":"echo hello"}'))
```

执行旧格式命令：

```python
from magicskills import ALL_SKILLS, skill_tool

print(skill_tool(ALL_SKILLS, "execskill", "demo::echo hello"))
```

# Tips

## 依赖 `AGENTS.md`的接入方式

更推荐把所有 skill 先集中安装或维护到同一个 skills 根目录下，再从中挑选出某个 agent 真正需要的那一部分，组成一个命名 skills 集合，最后把这个集合同步到目标 `AGENTS.md`。

这样做有几个好处：

- skill 的物理存储位置统一，便于维护、升级和排查
- 不同 agent 可以复用同一批底层 skill，但只暴露各自需要的子集
- `AGENTS.md` 只保留当前 agent 真正需要看到的 skills，减少上下文噪音

推荐流程如下：

1. 把 skill 安装到统一目录，例如 `./.claude/skills` 或 `~/.claude/skills`
2. 用 `createskills` 创建一个只包含部分 skill 的命名集合
3. 用 `syncskills` 把这个集合写入目标 `AGENTS.md`
4. 让 agent 只读取这个目标 `AGENTS.md`

示例：

```bash
magicskills install demo --target ./.claude/skills
magicskills createskills coder --paths ./.claude/skills
magicskills syncskills coder --output ./agents/coder/AGENTS.md -y
```

如果你希望更精细地控制暴露范围，可以先把所有 skill 装到统一目录，再通过多个命名集合分别为不同 agent 生成不同的 `AGENTS.md`。

## 不依赖 `AGENTS.md` 的接入方式

有些 agent 或框架不会主动读取 `AGENTS.md`。这种情况下，可以直接把 MagicSkills 的统一分发接口暴露给它，而不是依赖文档同步。

CLI 入口使用：

```bash
magicskills skill-tool <action> --arg "<arg>" --name <skills-name>
```

例如：

```bash
magicskills skill-tool listskill --name coder
magicskills skill-tool readskill --name coder --arg demo
magicskills skill-tool execskill --name coder --arg "echo hello"
```

Python API 入口使用：

```python
skills.skill_tool(action: str, arg: str = "")
```

例如：

```python
from magicskills import ALL_SKILLS, Skills

skill_a = ALL_SKILLS.get_skill("demo")
skill_b = ALL_SKILLS.get_skill("code-review")  # 改成你自己的第二个 skill 名称或路径

skills = Skills(
    skill_list=[skill_a, skill_b],
    name="coder",
)

print(skills.skill_tool("listskill"))
print(skills.skill_tool("readskill", "demo"))
print(skills.skill_tool("execskill", "echo hello"))
```

这种方式适合两类场景：

- agent 有 tool-call / function-call 机制，但没有读取 `AGENTS.md` 的能力
- 你希望由上层程序自己控制何时列出 skill、何时读取 skill、何时执行命令

简化理解就是：

- 读 `AGENTS.md` 的 agent，推荐走 `createskills + syncskills`
- 不读 `AGENTS.md` 的 agent，推荐走 `skill-tool` 或 `skills.skill_tool()`

# FAQ

# 📋 环境要求

- **Python** 3.10 / 3.11 / 3.12 / 3.13
- **Git**（用于安装远程仓库中的 skill）

---

# 📜 License

[MIT](LICENSE)

---

<div align="center">

**Built with ❤️ by [Narwhal-Lab](https://github.com/Narwhal-Lab)**

</div>
