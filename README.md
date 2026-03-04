<div align="center">

<!-- 有 Logo 之后取消注释下行 -->
<!-- <img src="./image/logo.png" alt="MagicSkills" width="360" /> -->

# ✨ MagicSkills

**跨平台 AI Agent Skill 管理与工具分发利器**

完全兼容 `SKILL.md` · 支持 `AGENTS.md` 动态同步 · 纯 Python 标准库实现

[![Python 3.10‑3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://github.com/Narwhal-Lab/MagicSkills)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/Narwhal-Lab/MagicSkills?style=social)](https://github.com/Narwhal-Lab/MagicSkills)

[快速开始](#-快速开始) · [安装](#-安装) · [CLI 命令](#-cli-命令) · [Python API](#-作为-agent-的-tool-function) · [开发](#-开发)

</div>

---

## 🎯 MagicSkills

一个跨平台的 Python 3.10/3.11/3.12/3.13 包，用于管理基于 SKILL.md 的 skills，并提供可直接接入 agent 的 tool function。

## ✅ 为什么选择 MagicSkills

- **跨平台** — 兼容 Linux / Windows / macOS
- **标准兼容** — 支持 Claude 风格 `<available_skills>` XML 输出
- **自动同步** — `AGENTS.md` 一键同步（`syncskills`）
- **灵活管理** — 单 skill 操作 + Skills 集合实例管理
- **零依赖** — 纯标准库实现，运行时无第三方依赖
- **多 Agent 友好** — 适配多种 Agent

---

## 💡 核心概念

| 概念 | 说明 |
|------|------|
| **Skill** | 单个 skill 元数据对象（包含 `name`、`description`、`path`、`base_dir`、`source`、`environment` 等） |
| **Skills** | `Skill` 集合管理器（负责发现、读取、执行、同步、增删及 tool dispatch） |

---

## 🚀 快速开始

```bash
magicskills install c_2_ast           # 安装 skill
magicskills list                      # 列出所有 skill
magicskills readskill pdf             # 读取 skill 内容
magicskills execskill pdf -- "python3 scripts/example.py"  # 执行 skill 命令
magicskills syncskills -o AGENTS.md -y                     # 同步到 AGENTS.md
magicskills uploadskill c_2_ast       # 上传 skill 到仓库
magicskills createskill my-skill      # 创建新 skill 骨架
```

---

## 📦 安装

```bash
# 普通安装
pip install MagicSkills

# 开发安装
pip install -e .
```

> **Python 版本要求：** `>=3.10, <3.14`（来自 `pyproject.toml`）

<details>
<summary><strong>按指定解释器安装</strong></summary>

```bash
python3.10 -m pip install MagicSkills
python3.11 -m pip install MagicSkills
python3.12 -m pip install MagicSkills
python3.13 -m pip install MagicSkills
```

</details>

> **注意：** wheel 构建只包含 Python 包代码 `src/magicskills`。
> `src/magicskills/skills/**` 已在 `pyproject.toml` 中排除，不会随 `pip install` 安装。
> Skill 内容应通过 `magicskills install ...` 安装到本地目录。

---

## 🔍 默认搜索路径优先级

| 优先级 | 路径 | 类型 |
|:------:|------|------|
| 1 | `./.agent/skills/` | project universal |
| 2 | `~/.agent/skills/` | global universal |
| 3 | `./.claude/skills/` | project |
| 4 | `~/.claude/skills/` | global |

---

## 🧰 CLI 命令

```bash
magicskills <command> [options]
```

### 单 Skill 操作

| 命令 | 作用 | 可选参数 |
|------|------|----------|
| `listskill` | 列出 `Allskills` 中所有 skill（XML 输出） | — |
| `readskill <name>` | 读取 skill 目录下所有文件内容并格式化输出 | — |
| `execskill <name> -- "<cmd>"` | 在 skill 目录上下文执行命令 | `--no-shell` `--json` `--paths` |
| `showskill <name>` | 查看 skill 元数据 | `--json` `--paths` |
| `createskill <name>` | 创建标准 skill 骨架目录 | `--root` |
| `deleteskill <name>` | 删除指定 skill 目录 | `--paths` |

### 安装 & 上传

<details>
<summary><strong><code>magicskills install &lt;source&gt;</code></strong> — 从 GitHub / Git URL / 本地目录安装 skill</summary>

**参数：** `--global`、`--universal`、`-t/--target`、`-y/--yes`

- `--target` 与 `--global/--universal` 互斥
- 安装完成后，会把 skill 同步到 `Allskills`，并把每个 skill 的 `base_dir` 加入 `Allskills.paths`
- 默认仓库：`Narwhal-Lab/Skills-For-All-Agent`

示例：
```bash
magicskills install anthropics/skills --universal
magicskills install c_2_ast
magicskills install Narwhal-Lab/Skills-For-All-Agent
magicskills install c_2_ast --target ./custom-skills
```

</details>

<details>
<summary><strong><code>magicskills uploadskill &lt;source&gt;</code></strong> — 上传 skill 到目标仓库（默认仓库： Narwhal-Lab/Skills-For-All-Agent，默认子目录：skills_for_all_agent/skills）</summary>

**`<source>` 支持：**
- `Allskills` 中的 skill 名
- 本地 skill 目录路径（目录内须有 `SKILL.md`）

**参数：** `--repo`、`--subdir`、`--branch`、`--message`、`--no-push`、`--yes`、`--json`

示例：
```bash
magicskills uploadskill c_2_ast
magicskills uploadskill ./my-skill
magicskills uploadskill c_2_ast --repo git@github.com:Narwhal-Lab/Skills-For-All-Agent.git
magicskills uploadskill c_2_ast --no-push --json
```

</details>

### Skills 集合实例操作

| 命令 | 作用 | 可选参数 |
|------|------|----------|
| `createskills <instance>` | 创建命名 `Skills` 实例并持久化到注册表 | `--paths` `--tool-description` `--agent-md-path` |
| `listskills` | 列出所有命名实例 | `--json` |
| `deleteskills <instance>` | 删除命名实例（不删磁盘 skill 文件） | — |
| `addskill2skills <instance> <name>` | 把 skill 的 source 路径加入实例的搜索路径 | `--from-paths` |
| `changetooldescription <instance> "<desc>"` | 修改实例的 `tool_description` | — |
| `syncskills` | 把实例 skill 清单同步到 `AGENTS.md` | `-o/--output` `-y/--yes` `--paths` `--name` |
| `skill-for-all-agent <action> --arg "<arg>"` | 通过 CLI 调用 `Skill_For_All_Agent` 入口 | `--name` `--paths` |

> **持久化文件：** `./.magicskills/collections.json`

---

## 🐍 作为 Agent 的 Tool Function

### 方案 1：函数式入口（推荐）

```python
from magicskills import Skill_For_All_Agent

print(Skill_For_All_Agent("listskill", ""))
print(Skill_For_All_Agent("readskill", "pdf"))
print(Skill_For_All_Agent("execskill", "pdf::python3 scripts/example.py"))

# 指定命名 skills 实例（例如 createskills 创建的 team-a）
print(Skill_For_All_Agent("readskill", "pdf", name="team-a"))
```

### 方案 2：对象入口（SkillTool）

```python
from magicskills import SkillTool

tool = SkillTool()
print(tool.handle({"action": "listskill", "arg": ""}))
print(tool.handle({"action": "readskill", "arg": "pdf"}))
print(tool.handle({"action": "execskill", "arg": "pdf::python3 scripts/example.py"}))
```

---

## 📚 公共 Python API

> 以下函数均可从 `magicskills` 直接导入：

| 分类 | 函数 |
|------|------|
| **核心入口** | `Skill_For_All_Agent`（支持 `name=<instance>` 指定实例） |
| **集合管理** | `createskills` · `listskills` · `deleteskills` · `syncskills` · `addskill2skills` · `changetooldescription` |
| **单 Skill** | `listskill` · `showskill` · `createskill` · `deleteskill` · `installskill` · `uploadskill` |

---

## 🧬 SKILL.md 格式

```markdown
---
description: 示例 skill
environment:
  PYTHONPATH: "."
---

这里是详细说明...
```

Skills 采用**按需加载**，保持 Agent 上下文精简高效。

---

## 📂 项目结构

```text
src/magicskills/
├── __init__.py          # 对外 API
├── __main__.py          # python -m magicskills
├── cli.py               # CLI 入口
├── agent_tool/          # SkillTool 封装
└── core/                # 核心业务
    ├── skill.py
    ├── skills.py
    ├── registry.py
    ├── installer.py
    ├── agents_md.py
    ├── models.py
    └── utils.py
```

---

## 🛠 开发

```bash
pytest -q tests
ruff check .
mypy src/magicskills
```

<details>
<summary><strong>打包与发布前检查</strong></summary>

```bash
python -m pip install -U build twine
python -m build
twine check dist/*
```

可选 wheel 验证：
```bash
python -m pip install dist/*.whl
magicskills --help
```

多版本验证（需本机安装对应解释器）：
```bash
python -m pip install -U tox
tox
```

</details>

---

## 📋 环境要求

- **Python** 3.10 / 3.11 / 3.12 / 3.13
- **Git**（用于安装远程仓库中的 skill）

---

## 📜 License

[MIT](LICENSE)

---

<div align="center">

**Built with ❤️ by [Narwhal-Lab](https://github.com/Narwhal-Lab)**

</div>
