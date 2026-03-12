<div align="center">

<img src="./image/Logo.png" alt="MagicSkills" width="150" />

<br/>
<br/>



# 🪄 MagicSkills: **Build Skills Once, Reuse Them Across Every Agent**

<br/>

**Local-first** skill infrastructure for multi-agent projects

Turn scattered `SKILL.md` directories into a reusable · composable · syncable · callable shared capability library

<br/>

<table>
<tr>
<td align="center"><b>🤖 Agent Apps</b></td>
<td align="center"><b>🧩 Agent Frameworks</b></td>
</tr>
<tr>
<td align="center">Claude Code · Cursor · Windsurf · Aider · Codex<br/><sub>Any agent app that can read `AGENTS.md`</sub></td>
<td align="center">AutoGen · CrewAI · LangChain · LangGraph · Haystack<br/>Semantic Kernel · smolagents · LlamaIndex<br/><sub>Any agent framework with tool / function integration support</sub></td>
</tr>
</table>

<br/>

<sub>Initiated and maintained by Narwhal-Lab, Peking University</sub>
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
  &nbsp;
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" alt="License: MIT"/></a>
  &nbsp;
  <a href="https://github.com/Narwhal-Lab/MagicSkills"><img src="https://img.shields.io/github/stars/Narwhal-Lab/MagicSkills?style=for-the-badge&logo=github" alt="GitHub stars"/></a>
</p>




<br/>
<br/>

English | [简体中文](./README.zh-CN.md)

[Overview](#overview-en) · [Quick Start](#quick-start-en) · [How It Works](#how-it-works-en) · [CLI](./doc/cli.md) · [Python API](./doc/python-api.md) · [Tips](#tips-en)

</div>

---

<a id="overview-en"></a>
## 🧭 Overview

MagicSkills is a local-first skill infrastructure layer for multi-agent projects.

It turns scattered `SKILL.md` directories into something you can:

- install into one shared skill pool
- compose into per-agent `Skills` collections
- sync into `AGENTS.md`
- expose as a tool through one stable API

The core model is simple:

- `Skill`: one concrete skill directory
- `ALL_SKILLS()`: access the current built-in `Allskills` view
- `Skills`: the subset an agent or workflow actually uses
- `SkillsRegistry`: named collections persisted across runs

MagicSkills is most useful when:

- you maintain multiple agents that should reuse one skill library
- you already have `SKILL.md` content but no install/selection workflow
- some agents read `AGENTS.md`, while others need direct tool integration
- you want skill management to stay transparent and file-based

## 🤔 Why MagicSkills

Without a skill layer, multi-agent projects usually drift into one of these states:

- the same skill is copied into multiple agent folders and quickly diverges
- `SKILL.md` exists, but it is still just a document, not an operational unit
- every agent loads too many irrelevant skills
- `AGENTS.md`, prompt glue, and framework tools evolve independently
- changing frameworks means redoing the whole integration

MagicSkills solves that by separating:

- the total installed skill pool
- the subset each agent should actually see
- the persistence layer that stores named collections

<a id="quick-start-en"></a>
## 🚀 Quick Start

The shortest recommended workflow is:

1. Install MagicSkills.
2. Install one or more skills into the local pool.
3. Create a named `Skills` collection for one agent.
4. Sync that collection to `AGENTS.md` or expose it as a tool.

### 1. 📦 Install The Project

From source:

```bash
git clone https://github.com/Narwhal-Lab/MagicSkills.git
cd MagicSkills
python -m pip install -e .
magicskills -h
```

Or from PyPI:

```bash
pip install MagicSkills
magicskills -h
```

### 2. ⬇️ Install Skills

```bash
magicskills install anthropics/skills
```

By default, installed skills are copied into `./.claude/skills/` and then become discoverable from the built-in `Allskills` view.

### 3. 🧩 Create One Agent Collection

```bash
magicskills createskills agent1_skills --skill-list pdf docx --agent-md-path /agent_workdir/AGENTS.md
```

This means:

- resolve `pdf` and `docx` from `Allskills`
- create a named collection called `agent1_skills`
- remember `/agent_workdir/AGENTS.md` as its default sync target

### 4. 🔄 Sync To `AGENTS.md`

```bash
magicskills syncskills agent1_skills
```

If the target file already contains a skills section, it is replaced. If not, a new one is appended.

### 5. 🛠️ Or Use The Tool Interface Directly

For agents that do not read `AGENTS.md`, use the unified CLI tool entrypoint:

```bash
magicskills skill-tool listskill --name agent1_skills
magicskills skill-tool readskill --name agent1_skills --arg pdf
magicskills skill-tool execskill --name agent1_skills --arg "echo hello"
```

## 🐍 Python Example

If you are integrating MagicSkills into an agent framework, keep the Python side minimal:

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

Use `syncskills` if your runtime consumes `AGENTS.md`. Use `skill_tool` or the Python API directly if it does not.

## 🧪 Examples and Ecosystem Integrations

MagicSkills provides integration examples for both agent / IDE products that can directly read `AGENTS.md` and mainstream agent frameworks that integrate through tools or functions.

### Agent / IDEs that can read `AGENTS.md`

- [Claude Code](./ClaudeCode_example/README.md)
- [Cursor](./Cursor_example/README.md)
- [Windsurf](./Windsurf_example/README.md)
- [Aider](./Aider_example/README.md)
- [Codex](./Codex_example/README.md)

### Framework examples via tools / functions

- [AutoGen](./autogen_example/README.md)
- [CrewAI](./crewai_example/README.md)
- [LangChain](./langchain_example/README.md)
- [LangGraph](./langgraph_example/README.md)
- [Haystack](./haystack_example/README.md)
- [Semantic Kernel](./semantic_kernel_example/README.md)
- [smolagents](./smolagents_example/README.md)
- [LlamaIndex](./llamaindex_example/README.md)

## 🗺️ Documentation Map

- [How It Works](#how-it-works-en): architecture and object model
- [CLI](./doc/cli.md): command-by-command reference
- [Python API](./doc/python-api.md): object and function reference
- [Tips](#tips-en): integration guidance

<a id="how-it-works-en"></a>
# ⚙️ How It Works

## 🧠 Core Idea

The core of MagicSkills is not "a pile of commands", but a stable three-layer model for skill management:

- `Skill`: describes one skill directory and its metadata
- `Skills`: describes an operable collection of skills
- `SkillsRegistry`: describes how multiple named `Skills` collections are registered, loaded, and persisted

CLI and Python API are just different entry points to these three layers. Whether you call `readskill`, `install`, `syncskills`, or `skill_tool`, everything eventually goes through the same core objects and command implementations.

From the recommended runtime workflow, MagicSkills is closest to the following chain:

1. Use `install` to install relevant skills into a local skills directory
2. During installation, MagicSkills scans those skill directories, parses `SKILL.md` frontmatter, and constructs `Skill` objects
3. All installed and discovered skills are first aggregated into the built-in `Allskills` view
4. Then you select a subset from that view through `ALL_SKILLS()` or `REGISTRY.get_skills("Allskills")` and compose a specific `Skills` collection for an agent
5. Finally, that named `Skills` collection is registered into `SkillsRegistry`, optionally persisted, and synced to `AGENTS.md`

## 🧱 Skill Layer

In MagicSkills, the minimum requirement for a valid skill is simple: it must be a directory, and that directory must contain `SKILL.md`.

A typical structure looks like this:

```text
demo-skill/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

Where:

- `SKILL.md` is the entry document of the skill and also the metadata source
- `references/`, `scripts/`, and `assets/` are common convention folders, but they are not mandatory

In code, one skill is represented as a `Skill` object. Its core fields include:

- `name`: the skill name, usually the directory name
- `description`: extracted from the `SKILL.md` frontmatter
- `path`: the skill directory path
- `base_dir`: the skills root directory that contains this skill
- `source`: where the skill comes from, such as a local path or Git repository
- `is_global` / `universal`: marks which installation scope it comes from

This layer solves the question "what is a single skill". It does not manage groups of skills and does not handle registry persistence.

Common capabilities around a single skill include:

- `readskill`: read a skill's `SKILL.md`
- `showskill`: inspect the full contents of a skill directory
- `createskill_template`: create a standard skill skeleton
- `createskill`: register an existing skill directory into a collection

## 🧩 Skills Collection Layer

The `Skills` layer solves the problem of organizing multiple skills into one operable working set.

A `Skills` object can be built in two ways:

- pass `skill_list` directly
- pass `paths`, and let the system automatically scan those paths for skill directories

Once constructed, the collection exposes a unified set of higher-level capabilities:

- `listskill()`: list all skills in the collection
- `readskill(target)`: read skill file contents
- `showskill(target)`: display the full skill contents
- `execskill(command, ...)`: run a command and return a structured result
- `uploadskill(target)`: upload a skill through the default repository workflow
- `deleteskill(target)`: remove a skill from the collection; when applied to `Allskills`, it also removes the on-disk directory
- `syncskills(output_path=None)`: write the collection into `AGENTS.md`
- `skill_tool(action, arg="")`: dispatch list/read/exec in a tool-function style

There are two key design points in this layer:

- `Skills` supports both name-based and path-based skill lookup; when names collide, the path is the final disambiguator
- `Skills` is a runtime view, not the installation directory itself; the same skill can be referenced by multiple named collections

One important detail: `execskill()` runs commands in the current process working directory, not automatically inside the skill directory. That means MagicSkills unifies the execution entry point, but does not silently change your runtime context.

## 🗃️ Registry Persistence Layer

The `SkillsRegistry` layer solves the problem of saving and restoring multiple named skills collections.

Its responsibilities include:

- maintaining the global registry singleton `REGISTRY`
- ensuring the built-in collection `Allskills` always exists
- creating, querying, and deleting named skills collections
- writing collection metadata into a JSON file and reloading it later

By default, the registry is stored at:

```text
~/.magicskills/collections.json
```

What is stored there is not the full file contents of each skill, but only the minimum information needed to restore collections:

- `paths`
- `tool_description`
- `agent_md_path`

In other words, the Registry stores "collection configuration" and "skill path references", not full copies of skill contents. The actual skill content remains in the filesystem.

The typical workflow for this layer is:

1. Create a named collection with `createskills`
2. Persist it with `saveskills` or `REGISTRY.saveskills()`
3. Restore those collections with `loadskills`, or through default loading on process startup
4. Sync a specific collection to the target `AGENTS.md` with `syncskills`

So in essence, the Registry layer is the project-level configuration center of MagicSkills. `Skill` defines a single item, `Skills` organizes a working set, and `SkillsRegistry` makes those collections survive across different runtime cycles.

<a id="cli-en"></a>
# 🛠️ CLI

The full CLI reference has moved to [doc/cli.md](./doc/cli.md).
Chinese version: [doc/cli.zh-CN.md](./doc/cli.zh-CN.md).

| Command                   | Use case                                               | Main capability                                                 |
| ------------------------- | ------------------------------------------------------ | --------------------------------------------------------------- |
| `listskill`               | See which skills exist in the current built-in set     | List skill names, descriptions, and `SKILL.md` paths            |
| `readskill`               | Read a skill description or any local text file        | Output content by skill name or file path                       |
| `execskill`               | Run commands in the current working directory          | Supports streaming, JSON output, no-shell mode, custom paths    |
| `syncskills`              | Sync a named skills collection into `AGENTS.md`        | Generate or replace the `<skills_system>` block                 |
| `install`                 | Install skills from local paths, Git repos, or default | Copy skill files and register them into `Allskills`             |
| `createskill`             | Register an existing skill directory into `Allskills`  | Register metadata without copying files                         |
| `uploadskill`             | Submit a local skill to the default MagicSkills repo   | Automate fork, push, and PR flow                                |
| `deleteskill`             | Delete one skill                                       | Delete the skill directory and remove shared references         |
| `showskill`               | Review the full contents of a skill package            | Show metadata and all files inside the skill directory          |
| `createskills`            | Create a named skills collection                       | Build an isolated skill set for an agent or team               |
| `listskills`              | List all named skills collections                      | Human-readable output or JSON output                            |
| `deleteskills`            | Delete a named skills collection                       | Delete only the collection registration, not the skill files    |
| `changetooldescription`   | Modify the collection's `tool_description` metadata    | Update collection description for later querying and integration |
| `skill-tool`              | Invoke skill capabilities in a tool-function style     | Use unified JSON output to dispatch list/read/exec              |

<a id="python-api-en"></a>
# 🐍 Python API

The full Python API reference has moved to [doc/python-api.md](./doc/python-api.md).
Chinese version: [doc/python-api.zh-CN.md](./doc/python-api.zh-CN.md).


If you want to call MagicSkills directly from scripts, tests, agent runtimes, or higher-level frameworks instead of going through the CLI, use the Python API. The content below follows the current `__all__` in `/root/LLK/MagicSkills/src/magicskills/__init__.py`.

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

**Exports**

- types: `Skill`, `Skills`, `SkillsRegistry`
- accessors and constants: `REGISTRY`, `ALL_SKILLS()`, `DEFAULT_SKILLS_ROOT`
- single-skill and execution functions: `listskill`, `readskill`, `showskill`, `execskill`, `createskill`, `createskill_template`, `install`, `uploadskill`, `deleteskill`
- skills collection and registry functions: `createskills`, `listskills`, `deleteskills`, `syncskills`, `loadskills`, `saveskills`
- description and dispatch functions: `change_tool_description`, `changetooldescription`, `skill_tool`

**Usage advice**

- If you already have a `Skills` object, prefer instance methods such as `skills.readskill()`, `skills.execskill()`, and `skills.syncskills()`.
- If you want to directly reuse CLI-equivalent capabilities, top-level functions are more direct.
- `changetooldescription` is a compatibility alias of `change_tool_description`; they are equivalent.

<a id="tips-en"></a>
# 💡 Tips

## 🧾 Integration via `AGENTS.md`

It is recommended to first install or maintain all skills under one shared skills root, then select only the subset a given agent actually needs, build a named skills collection from it, and finally sync that collection into the target `AGENTS.md`.

This has several benefits:

- the physical storage location of skills stays unified, making maintenance, upgrades, and debugging easier
- different agents can reuse the same underlying skills while exposing only the subset each one actually needs
- `AGENTS.md` keeps only the skills that the current agent truly needs to see, reducing context noise

The recommended flow is:

1. Install skills into a shared directory, such as `~/allskills/`, `./.claude/skills`, or `~/.claude/skills`
2. Use `createskills` to create a named collection that contains only a subset of skills
3. Use `syncskills` to write that collection into the target `AGENTS.md`
4. Let the agent read only that target `AGENTS.md`

Example:

```bash
magicskills install anthropics/skills -t ~/allskills/
magicskills createskills agent1_skills --skill-list pdf docx --agent-md-path /agent_workdir/AGENTS.md
magicskills syncskills agent1_skills
```

If you want finer-grained exposure control, install all skills into one shared directory first, then generate different `AGENTS.md` files for different agents through multiple named collections.

## 🔌 Integration without `AGENTS.md`

Some agents or frameworks do not read `AGENTS.md` proactively. In that case, you can expose MagicSkills' unified dispatch interface directly to them instead of relying on document syncing.

CLI entrypoint:

```bash
magicskills skill-tool <action> --arg "<arg>" --name <skills-name>
```

For example:

```bash
magicskills skill-tool listskill --name agent1_skills
magicskills skill-tool readskill --name agent1_skills --arg "<path>"
magicskills skill-tool execskill --name agent1_skills --arg "<command>"
```

Python API entrypoint:

```python
agent1_skills.skill_tool(action: str, arg: str = "")
```

For example:

```python
import json

from langchain_core.tools import tool
from magicskills import ALL_SKILLS, Skills

skill_a = ALL_SKILLS().get_skill("pdf")
skill_b = ALL_SKILLS().get_skill("docx")  # Replace with your own second skill name or path

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

This approach fits two kinds of scenarios:

- the agent supports tool-call / function-call mechanisms, but cannot read `AGENTS.md`
- you want the upper-level program itself to control when to list skills, when to read skills, and when to execute commands

The simplified rule of thumb is:

- for agents that read `AGENTS.md`, prefer `createskills + syncskills`
- for agents that do not read `AGENTS.md`, prefer `skill-tool` or `skills.skill_tool()`

## 🌱 Sharing and Growing the Skill Ecosystem

MagicSkills is not only a local skill management tool. It also aims to support a growing skill ecosystem where reusable capabilities can be accumulated, shared, and installed across projects.

If you have implemented a reusable local skill, you can use `uploadskill` to upload it into this project's `skills/` directory through the default fork / push / PR workflow.  
If you want to reuse skills contributed by others, you can use `install` to download them locally and integrate them into your own agents or workflows.

The recommended flow is:

1. Build a reusable local skill and make sure the directory contains `SKILL.md`
2. Use `uploadskill` to submit that skill into the open-source MagicSkills skill library
3. Other users install those skills with `install` and compose them into their own `Skills` collections or `AGENTS.md`

Example:

```bash
magicskills uploadskill ./skills/my-skill
magicskills install my-skill
```

# ❓ FAQ

### What is the minimum structure of a skill?

At minimum, a skill must satisfy two conditions:

- it is a directory
- the directory contains `SKILL.md`

Folders such as `references/`, `scripts/`, and `assets/` are common conventions, but they are optional.

### Should I use `syncskills` or `skill-tool`?

Choose based on how your agent integrates:

- if your agent reads `AGENTS.md`, prefer `createskills + syncskills`
- if your agent does not read `AGENTS.md` and instead integrates through tool-call / function-call, prefer `skill-tool` or `skills.skill_tool()`

The former is better for document-driven integration; the latter is better for direct programmatic integration.

### Where does `install` put skills by default?

By default, skills are installed into `./.claude/skills/` under the current project.

If you use:

- `--global`, the default becomes `~/.claude/skills`
- `--universal`, the default becomes `./.agent/skills` in the current project
- `--global --universal`, the default becomes `~/.agent/skills`
- `--target`, the explicitly specified directory is used instead

### What should I do when skill names conflict?

Many commands accept either a skill name or a skill path.  
If multiple skills share the same name, stop passing the name and use an explicit path instead, for example:

```bash
magicskills readskill ./skills/demo/SKILL.md
magicskills deleteskill ./skills/demo
```

In short: names are for convenience, paths are for disambiguation.

### Does `execskill` automatically run inside the skill directory?

No. `execskill()` runs in the current process working directory. It does not automatically switch into a skill directory.

This means:

- MagicSkills gives you a unified execution entrypoint
- but it does not silently change your runtime context

If your command depends on a specific directory, `cd` into it yourself in the command, or invoke MagicSkills from the correct working directory.

### How can I share a local skill with others?

If you want to contribute a local skill into the open-source ecosystem, use `uploadskill` to submit it into this project's `skills/` directory. Other users can then download and reuse it with `install`.

A typical flow looks like this:

```bash
magicskills uploadskill ./skills/my-skill
magicskills install my-skill
```

The first command shares the skill; the second reuses it.

# 📋 Requirements

- **Python** 3.10 / 3.11 / 3.12 / 3.13
- **Git** (used to install skills from remote repositories)

---

# 📜 License

[MIT](LICENSE)

---

<div align="center">

**Open-sourced and maintained by [Narwhal-Lab, Peking University](https://github.com/Narwhal-Lab)**

</div>
