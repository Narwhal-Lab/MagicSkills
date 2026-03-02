# MagicSkills

一个跨平台的 Python 3.10/3.11/3.12/3.13 包，用于管理基于 `SKILL.md` 的 skills，并提供可直接接入 agent 的 tool function。

## 特性
- 兼容 Linux / Windows / macOS
- 支持 Claude 风格 `<available_skills>` 输出
- 支持 `AGENTS.md` 同步（`syncskills`）
- 支持单 skill 操作 + skills 集合实例管理
- 纯标准库实现（运行时无第三方依赖）

## Skill vs Skills
- `Skill`：单个 skill 元数据对象（`name`、`description`、`path`、`base_dir`、`source`、`environment` 等）
- `Skills`：`Skill` 集合管理器（发现、读取、执行、同步、增删、tool dispatch）

## 项目结构
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

## 安装
```bash
# 开发安装
pip install -e .

# 普通安装（发布后）
pip install MagicSkills
```

解释器要求来自 `pyproject.toml`：`>=3.10,<3.14`。

建议按目标解释器安装：
```bash
python3.10 -m pip install MagicSkills
python3.11 -m pip install MagicSkills
python3.12 -m pip install MagicSkills
python3.13 -m pip install MagicSkills
```

## 包含内容说明（重要）
- wheel 构建只包含 Python 包代码：`src/magicskills`
- `src/magicskills/skills/**` 已在 `pyproject.toml` 里排除，不会随 `pip install` 安装
- skill 内容应通过 `magicskills install ...` 安装到本地目录

## 默认搜索路径优先级
1. `./.agent/skills/`（project universal）
2. `~/.agent/skills/`（global universal）
3. `./.claude/skills/`（project）
4. `~/.claude/skills/`（global）

## 快速开始
```bash
magicskills list
magicskills readskill pdf
magicskills execskill pdf -- "python3 scripts/example.py"
magicskills syncskills -o AGENTS.md -y
magicskills install c_2_ast
magicskills uploadskill c_2_ast
magicskills createskill my-skill
```

## CLI 命令
当前代码中的命令集合：

```text
list
readskill
execskill
syncskills
install
createskill
uploadskill
deleteskill
showskill
createskills
listskills
deleteskills
addskill2skills
changetooldescription
skill-for-all-agent
```

### 单 skill 操作
`magicskills list`  
作用：列出 `Allskills` 中所有 skill（XML 输出）。

`magicskills readskill <skill-name>`  
作用：读取该 skill 目录下所有文件内容并格式化输出。

`magicskills execskill <skill-name> -- "<command>"`  
作用：在 skill 目录上下文执行命令。  
参数：`--no-shell`、`--json`、`--paths`

`magicskills showskill <skill-name>`  
作用：查看 skill 元数据。  
参数：`--json`、`--paths`

`magicskills createskill <skill-name>`  
作用：创建标准 skill 骨架目录（`SKILL.md/references/scripts/assets`）。  
参数：`--root`

`magicskills deleteskill <skill-name>`  
作用：删除指定 skill 目录。  
参数：`--paths`

`magicskills install <source>`  
作用：从 GitHub shorthand / git URL / 本地目录安装 skill；也支持直接传 skill 名（默认仓库：`Narwhal-Lab/Skills-For-All-Agent`）。  
参数：`--global`、`--universal`、`-t/--target`、`-y/--yes`  
说明：`--target` 与 `--global/--universal` 互斥。
说明：安装完成后，会把安装得到的 skill 同步到 `Allskills`，并把每个 skill 的 `base_dir` 加入 `Allskills.paths`。

示例：
```bash
magicskills install anthropics/skills --universal
magicskills install c_2_ast
magicskills install Narwhal-Lab/Skills-For-All-Agent
magicskills install c_2_ast --target ./custom-skills
```

`magicskills uploadskill <source>`  
作用：上传 skill 到目标仓库（默认仓库：`Narwhal-Lab/Skills-For-All-Agent`，默认子目录：`skills_for_all_agent/skills`）。  
`<source>` 支持：
- `Allskills` 中 skill 名
- 本地 skill 目录路径（目录内必须有 `SKILL.md`）

不支持：
- `SKILL.md` 文件路径

参数：`--repo`、`--subdir`、`--branch`、`--message`、`--no-push`、`--yes`、`--json`

示例：
```bash
magicskills uploadskill c_2_ast
magicskills uploadskill ./my-skill
magicskills uploadskill c_2_ast --repo git@github.com:Narwhal-Lab/Skills-For-All-Agent.git
magicskills uploadskill c_2_ast --no-push --json
```

### skills 集合实例操作
`magicskills createskills <instance-name>`  
作用：创建命名 `Skills` 实例并持久化到注册表。  
参数：`--paths`、`--tool-description`、`--agent-md-path`

`magicskills listskills`  
作用：列出所有命名实例。  
参数：`--json`

`magicskills deleteskills <instance-name>`  
作用：删除命名实例（不删磁盘 skill 文件）。

`magicskills addskill2skills <instance-name> <skill-name>`  
作用：把该 skill 的 source 路径加入实例的搜索路径并刷新。  
参数：`--from-paths`

`magicskills changetooldescription <instance-name> "<description>"`  
作用：修改实例 `tool_description`。

`magicskills syncskills`  
作用：把实例 skill 清单同步到 `AGENTS.md`（或自定义输出）。  
参数：`-o/--output`、`-y/--yes`、`--paths`、`--name`

`magicskills skill-for-all-agent <action> --arg "<arg>"`  
作用：通过 CLI 调用 `Skill_For_All_Agent` 风格入口。  
参数：`--name`、`--paths`

命名实例持久化文件：`./.magicskills/collections.json`

## 作为 agent 的 tool function
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

## 公共 Python API（`magicskills.__init__`）
可直接调用：
- `Skill_For_All_Agent`（支持 `name=<instance-name>` 指定实例）
- `createskills` / `listskills` / `deleteskills`
- `syncskills` / `addskill2skills` / `changetooldescription`
- `listskill` / `showskill` / `createskill` / `deleteskill`
- `installskill` / `uploadskill`

## SKILL.md 示例
```markdown
---
description: 示例 skill
environment:
  PYTHONPATH: "."
---

这里是详细说明...
```

## 开发
```bash
pytest -q tests
ruff check .
mypy src/magicskills
```

## 打包与发布前检查
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
