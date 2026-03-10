<div align="center">

<!-- Uncomment the line below after the logo is available -->

 <img src="./image/Logo.png" alt="MagicSkills" width="360" /> 

# 🪄 MagicSkills

**Build skills once, reuse them across every agent.**

Local-first skill infrastructure for multi-agent projects  
Turn scattered `SKILL.md` directories into a reusable, composable, syncable, callable shared capability library

<sub>Initiated and maintained by Narwhal-Lab, Peking University</sub>

[![Python 3.10‑3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://github.com/Narwhal-Lab/MagicSkills)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/Narwhal-Lab/MagicSkills?style=social)](https://github.com/Narwhal-Lab/MagicSkills)

English | [简体中文](./README.md)

[Overview](#overview-en) · [Quick Start](#quick-start-en) · [How It Works](#how-it-works-en) · [CLI](#cli-en) · [Python API](#python-api-en) · [Tips](#tips-en)

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

## 🗺️ Documentation Map

- [How It Works](#how-it-works-en): architecture and object model
- [CLI](#cli-en): command-by-command reference
- [Python API](#python-api-en): object and function reference
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

After installation, the `magicskills` command becomes available:

```bash
magicskills -h
magicskills <command> -h
```

The examples below assume `bash/zsh`; if you use PowerShell, adjust quoting and escaping rules accordingly.

## 📚 CLI Command Overview

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

## 📌 General Conventions

- `Allskills` is the built-in skills collection. `listskill`, `readskill`, `install`, `createskill`, `uploadskill`, `deleteskill`, and `showskill` all operate around it by default.
- Named skills collections are created through `createskills`, and their metadata is stored in `~/.magicskills/collections.json`.
- Many commands accept both a `skill name` and a `skill directory path`. If multiple skills share the same name, you must pass an explicit path.
- The default install directory for `install` depends on the scope.
- Current project default: `./.claude/skills`
- `--global` default: `~/.claude/skills`
- `--universal` current project directory: `./.agent/skills`
- `--global --universal` directory: `~/.agent/skills`
- When `readskill` receives a skill name, it actually reads the `SKILL.md` inside that skill directory.
- For `execskill`, it is recommended to separate CLI args from the command with `--`.

## 📋 `listskill`

**Use case**

You want a quick view of which skills are already registered in the current `Allskills`, along with each skill's basic description.

**Command format**

```bash
magicskills listskill
```

**Parameters**

None.

**Examples**

```bash
magicskills listskill
```

The output lists each skill in order with:

- `name`
- `description`
- `path` (pointing to that skill's `SKILL.md`)

## 📖 `readskill`

**Use case**

You already know a skill name and want to read its `SKILL.md` directly, or you want to use this command to read any local file.

**Command format**

```bash
magicskills readskill <path>
```

**Parameters**

- `<path>`: may be a file path or a skill name in `Allskills`.
- When a skill name is passed, the command reads the `SKILL.md` inside the corresponding skill directory.
- When an explicit path is passed, the target must be a file, not a directory.
- If multiple skills share the same name, you must pass a concrete file path, for example `./skills/demo/SKILL.md`.

**Examples**

Read by skill name:

```bash
magicskills readskill demo
```

Read by `SKILL.md` file path:

```bash
magicskills readskill ./skills/demo/SKILL.md
```

Read any local file:

```bash
magicskills readskill ./AGENTS.md
```

When there is a name collision, use an explicit path:

```bash
magicskills readskill ./vendor-skills/demo/SKILL.md
```

## ▶️ `execskill`

**Use case**

You want to execute a command in the current working directory while keeping the invocation style consistent with the MagicSkills ecosystem. It is also suitable as a unified execution entry point for agents or automation scripts.

**Command format**

```bash
magicskills execskill [--no-shell] [--json] [--paths [PATHS ...]] -- <command>
```

**Parameters**

- `<command>`: the command string to execute. It is recommended to place it after `--`.
- `--no-shell`: disable shell mode. Internally, the command is split with `shlex.split()`, which is better for directly invoking executables and their arguments.
- `--json`: instead of streaming terminal output directly, return JSON containing `command`, `returncode`, `stdout`, and `stderr`.
- `--paths [PATHS ...]`: specify custom skill lookup paths. A temporary `Skills` collection is constructed from those paths before executing the command.

**Examples**

Default streaming execution:

```bash
magicskills execskill -- pwd
```

Return JSON for script consumption:

```bash
magicskills execskill --json -- echo hello
```

Run Python in no-shell mode:

```bash
magicskills execskill --no-shell -- python -c 'print(123)'
```

Run a command in the context of custom skills paths:

```bash
magicskills execskill --paths ./.claude/skills ./vendor-skills -- ls -la
```

## 🔄 `syncskills`

**Use case**

You have already created a named skills collection and want to sync it into an `AGENTS.md` file so the agent can see those skills in its system context.

**Command format**

```bash
magicskills syncskills <name> [-o OUTPUT] [-y]
```

**Parameters**

- `<name>`: the name of the named skills collection
- `-o, --output`: output file path; if omitted, the collection's own `agent_md_path` is used
- `-y, --yes`: skip interactive confirmation and sync immediately

**Examples**

Sync to the collection's default `agent_md_path`:

```bash
magicskills syncskills coder
```

Sync to a specific file:

```bash
magicskills syncskills coder --output ./AGENTS.md
```

Skip confirmation in CI or scripts:

```bash
magicskills syncskills coder -o ./AGENTS.md -y
```

Notes:

- If the target file does not exist, the command creates it first and writes a base `# AGENTS` title.
- If the file already contains a `<skills_system>` block, the command replaces it; otherwise it appends a new block to the end of the file.

## 📦 `install`

**Use case**

You want to install skills into the current project or a global directory. This command supports installing a specific skill from the default repository, or all skills from a local directory or remote Git repository.

**Command format**

```bash
magicskills install <source> [--global] [--universal] [-t TARGET] [-y]
```

**Parameters**

- `<source>`: supports four input forms.
- skill name: such as `demo`. The command clones the default repository `https://github.com/Narwhal-Lab/MagicSkills.git` and installs only the matching skill.
- GitHub short form: such as `owner/repo`. The command converts it to `https://github.com/owner/repo.git` and installs all skill directories in that repository that contain `SKILL.md`.
- Git URL: for example `https://github.com/owner/repo.git` or `git@github.com:owner/repo.git`.
- local path: may be a single skill directory or a root directory containing multiple skills; the command recursively finds all `SKILL.md` files.
- `--global`: switch the install root to the user's Home instead of the current project directory.
- `--universal`: switch the install root from `.claude/skills` to `.agent/skills`.
- `-t, --target`: custom install directory; cannot be used together with `--global` or `--universal`.
- `-y, --yes`: if a skill with the same name already exists in the target directory, overwrite it directly.

**Resolution order**

- If `<source>` exists locally, it is handled as a local path.
- If `<source>` looks like a plain skill name and does not contain `/`, `\\`, `.git`, or a URL prefix, it is handled as a skill name in the default repository.
- All other cases are handled as Git repositories.

**Examples**

Install one skill from the default MagicSkills repository:

```bash
magicskills install demo
```

Batch install from a local skills root:

```bash
magicskills install ./skills
```

Install from a single local skill directory:

```bash
magicskills install ./skills/demo
```

Install from a GitHub short form:

```bash
magicskills install Narwhal-Lab/MagicSkills
```

Install from a full Git URL:

```bash
magicskills install https://github.com/owner/repo.git
```

Install into global `.claude/skills`:

```bash
magicskills install demo --global
```

Install into the current project's `.agent/skills`:

```bash
magicskills install demo --universal
```

Install into a custom directory:

```bash
magicskills install demo --target ./custom-skills
```

Overwrite a skill with the same name:

```bash
magicskills install demo --target ./custom-skills -y
```

Notes:

- Remote installation depends on `git`.
- After installation, the CLI prints the actual directories written to disk.
- The install flow also registers installed skills into the current process `Allskills` collection.

## 🧰 `createskill`

**Use case**

You already wrote a skill directory by hand and only want to register it into `Allskills`, instead of copying it again.

**Command format**

```bash
magicskills createskill <path> [--source SOURCE]
```

**Parameters**

- `<path>`: the skill directory path; the directory must contain `SKILL.md`
- `--source`: optional source info to record for this skill; when omitted, the absolute path of the skill's parent directory is used

**Examples**

Register a local skill directory:

```bash
magicskills createskill ./skills/my-skill
```

Explicitly record the source repository or source directory:

```bash
magicskills createskill ./skills/my-skill --source https://github.com/owner/repo.git
```

Notes:

- The behavior of this command is "register an existing skill", not "generate a skill template".
- `description` is extracted from the `SKILL.md` frontmatter.

## 📤 `uploadskill`

**Use case**

You already prepared a local skill and want to automatically submit it to the default MagicSkills repository and create a Pull Request.

**Command format**

```bash
magicskills uploadskill <source>
```

**Parameters**

- `<source>`: may be a skill name in `Allskills` or a local skill directory path

**Default workflow**

- Validate that the directory resolved from `source` exists and contains `SKILL.md`
- Check whether `gh` is installed and logged in
- `gh repo fork Narwhal-Lab/MagicSkills --clone`
- Pull the upstream default branch and create a new branch such as `fix/upload-<skill>-<timestamp>`
- Copy the skill into `skills/<skill-name>` inside the repository
- Commit, push, and create a PR

**Examples**

Upload by skill name:

```bash
magicskills uploadskill demo
```

Upload by local path:

```bash
magicskills uploadskill ./skills/demo
```

Notes:

- If multiple skills with the same name exist in `Allskills`, you must pass the skill directory path instead.
- In an interactive terminal, if `gh` is missing, the CLI asks whether to try automatic installation; if `gh` is not logged in, it asks whether to run `gh auth login`.
- If `gh auth login` is inconvenient, the CLI will also ask whether to enter a temporary `GH_TOKEN`.
- On success, it outputs fields such as `Repo`, `Branch`, `Target`, `Committed`, `Pushed`, and `PR URL`.

## 🗑️ `deleteskill`

**Use case**

You want to delete a skill completely, not just hide it from a list.

**Command format**

```bash
magicskills deleteskill <target>
```

**Parameters**

- `<target>`: may be a skill name or a skill directory path

**Examples**

Delete by name:

```bash
magicskills deleteskill demo
```

When names collide, delete by path:

```bash
magicskills deleteskill ./skills/demo
```

Notes:

- This CLI command operates on the built-in `Allskills` by default.
- Deletion removes the actual skill directory immediately and does not ask for confirmation a second time.
- After a successful deletion, if other named collections also reference the same skill path, the corresponding entries in those collections are also removed.

## 🔍 `showskill`

**Use case**

You want to fully review a skill package rather than only reading `SKILL.md`. This is useful in code review, submission flows, checking binary files, or verifying script entry points.

**Command format**

```bash
magicskills showskill <target>
```

**Parameters**

- `<target>`: may be a skill name or a skill directory path

**Examples**

View by name:

```bash
magicskills showskill demo
```

View by path:

```bash
magicskills showskill ./skills/demo
```

Notes:

- The output first shows `Skill Overview`, including name, description, skill directory, `base_dir`, `SKILL.md` path, and installation source.
- Then it shows the contents of all files under the skill directory.
- When binary files are encountered, it prints `[binary file omitted: <size> bytes]` instead of raw unreadable data.

## 🧩 `createskills`

**Use case**

You need to create an independent named skills collection for an agent, team, or workflow, then use `syncskills` to generate the matching `AGENTS.md`.

**Command format**

```bash
magicskills createskills <name> [--skill-list [SKILLS ...]] [--paths [PATHS ...]] [--tool-description TEXT] [--agent-md-path PATH]
```

**Parameters**

- `<name>`: the new collection name, which must be unique
- `--skill-list [SKILLS ...]`: explicitly list which skills should enter the collection. Each item may be a skill name or a skill directory path and is resolved from `Allskills`.
- `--paths [PATHS ...]`: include the skills resolved from these paths into the new collection. Common usage patterns:
- pass a specific skill directory, for example `./.claude/skills/demo`
- pass a skills root directory, for example `./.claude/skills`
- `--tool-description`: override the collection's `tool_description` metadata
- `--agent-md-path`: specify which `AGENTS.md` this collection should sync to by default

**Examples**

Create an empty collection:

```bash
magicskills createskills coder
```

Create from an explicit skill list:

```bash
magicskills createskills reviewer --skill-list demo code-review
```

Create from explicit skill paths:

```bash
magicskills createskills reviewer --skill-list ./.claude/skills/code-review
```

Construct a collection from a skills root:

```bash
magicskills createskills coder --paths ./.claude/skills
```

Include only one specific skill:

```bash
magicskills createskills reviewer --paths ./.claude/skills/code-review
```

Specify multiple paths at once:

```bash
magicskills createskills fullstack --paths ./.claude/skills ./vendor-skills
```

Set metadata while creating the collection:

```bash
magicskills createskills coder \
  --paths ./.claude/skills \
  --tool-description "Unified skill tool for coding tasks" \
  --agent-md-path ./agents/coder/AGENTS.md
```

Notes:

- If neither `--skill-list` nor `--paths` is passed, the current version creates an empty named collection.
- `--skill-list` and `--paths` cannot be used together.
- Every item in `--skill-list` must resolve to a unique skill in the current `Allskills`; if names collide, pass the skill directory path instead.
- Every path in `--paths` must resolve to existing skills in the current `Allskills`, or to a parent skills root directory that contains them.
- On success, the command prints the collection name and `Skills count`.

## 🗂️ `listskills`

**Use case**

You want to inspect which named skills collections are currently registered on the machine, or feed that information into scripts.

**Command format**

```bash
magicskills listskills [--json]
```

**Parameters**

- `--json`: output a JSON array; otherwise output a human-readable boxed format

**Examples**

View all collections:

```bash
magicskills listskills
```

Output in JSON:

```bash
magicskills listskills --json
```

Each collection object in JSON output includes:

- `name`
- `skills_count`
- `paths`
- `tool_description`
- `agent_md_path`

## 🧹 `deleteskills`

**Use case**

When a named skills collection is no longer needed, you want to delete only its registration and keep the original skill files.

**Command format**

```bash
magicskills deleteskills <name>
```

**Parameters**

- `<name>`: the name of the named skills collection to delete

**Examples**

Delete a named collection:

```bash
magicskills deleteskills coder
```

Notes:

- `deleteskills` only removes collection registration and does not delete skill directories.
- The built-in `Allskills` collection cannot be deleted.

## ✏️ `changetooldescription`

**Use case**

You want to modify the `tool_description` metadata on a named skills collection so it can later be read via `listskills --json`, the Python API, or external frameworks.

**Command format**

```bash
magicskills changetooldescription <name> <description>
```

**Parameters**

- `<name>`: the name of the named skills collection
- `<description>`: the new tool description text; if it contains spaces, remember to quote it

**Examples**

Update the description:

```bash
magicskills changetooldescription coder "Unified skill tool for coding and review tasks"
```

View it after updating:

```bash
magicskills listskills --json
```

Notes:

- This updates collection metadata.
- It does not change the fixed `AGENTS.md` usage template generated by `syncskills`.

## 🤖 `skill-tool`

**Use case**

When you need a stable CLI wrapper oriented toward agent/tool-call usage, this command is the right fit. It wraps `listskill`, `readskill`, and `execskill` into a unified JSON return structure and uses the process exit code to indicate success or failure.

**Command format**

```bash
magicskills skill-tool <action> [--arg ARG] [--name NAME]
```

**Parameters**

- `<action>`: action name, supporting the following primary actions and aliases
- `listskill`, `list`, `list_metadata`
- `readskill`, `read`, `read_file`
- `execskill`, `exec`, `run_command`
- `--arg ARG`: action argument
- for `listskill`, this can usually be omitted
- for `readskill`, pass a skill name or file path
- for `execskill`, pass a plain command string, a JSON string, or the legacy `name::command` format
- `--name NAME`: specify which named skills collection to use; if omitted, `Allskills` is used by default

**Examples**

List skills in the default collection:

```bash
magicskills skill-tool listskill
```

Read a skill inside a named collection:

```bash
magicskills skill-tool readskill --name coder --arg demo
```

Read an explicit file path:

```bash
magicskills skill-tool readskill --arg ./skills/demo/SKILL.md
```

Execute a plain command string:

```bash
magicskills skill-tool execskill --arg "echo hello"
```

Execute a command via JSON input:

```bash
magicskills skill-tool execskill --arg '{"command":"echo hello"}'
```

Support the legacy `name::command` format:

```bash
magicskills skill-tool execskill --arg 'demo::echo hello'
```

Notes:

- Output is always JSON.
- When `ok` is `true`, the CLI exits with code `0`; otherwise it exits with code `1`.
- When an unknown action is passed, it returns `{"ok": false, "error": "Unknown action: ..."}`.

<a id="python-api-en"></a>
# 🐍 Python API

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

## 🧱 `Skill`

**Use case**

Use this when you need to manually construct a skill metadata object, or serialize skill metadata into another system.

**Constructor signature**

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

**Parameters**

- `name`: the skill name, usually equal to the skill directory name
- `description`: a short description of the skill, usually coming from the `description` field in `SKILL.md` frontmatter
- `path`: the skill directory path
- `base_dir`: the skills root directory that contains the skill
- `source`: source information, such as a local path, Git URL, or repository address
- `is_global`: whether it comes from a global directory
- `universal`: whether it comes from the `.agent/skills` layout

**Available capabilities**

- direct access to dataclass fields
- call `to_dict()` to get a JSON-friendly dictionary

**Examples**

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

## 🧩 `Skills`

**Use case**

Use this when you want to maintain a group of skills in memory and manage listing, reading, execution, syncing, deletion, and related operations in an object-oriented style.

**Constructor signature**

```python
Skills(
    skill_list: Iterable[Skill] | None = None,
    paths: Iterable[Path | str] | None = None,
    tool_description: str | None = None,
    agent_md_path: Path | str | None = None,
    name: str = "all",
)
```

**Parameters**

- `skill_list`: an explicit list of `Skill` objects
- `paths`: a list of skills root directories, or a list of individual skill directories; skills are discovered automatically during construction
- `tool_description`: the tool description text of this collection
- `agent_md_path`: which `AGENTS.md` file this collection should sync to by default
- `name`: the collection name, defaulting to `"all"`

**Notes**

- If `skill_list` and `paths` are both provided, they must resolve to exactly the same skills, otherwise a `ValueError` is raised.
- When only `paths` is provided, directories are scanned automatically for `SKILL.md`.
- When only `skill_list` is provided, `paths` are inferred automatically.
- `agent_md_path` defaults to `AGENTS.md` in the current working directory.

**Common instance methods**

- `get_skill(target)`: retrieve one `Skill` by name or directory path
- `createskill(skill_path, source=None)`
- `deleteskill(target)`
- `listskill()`
- `readskill(target)`
- `uploadskill(target)`
- `showskill(target)`
- `execskill(command, shell=True, timeout=None, stream=False)`
- `change_tool_description(description)`
- `syncskills(output_path=None)`
- `skill_tool(action, arg="")`

These instance methods map one-to-one to the top-level functions described below. If you prefer a functional style, you can use the top-level functions directly.

**Examples**

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

## 🗃️ `SkillsRegistry`

**Use case**

Use this when you need to manage multiple named skills collections and persist them into a JSON file.

**Constructor signature**

```python
SkillsRegistry(store_path: Path | None = None)
```

**Parameters**

- `store_path`: the registry file path; if omitted, it defaults to `~/.magicskills/collections.json`

**Core methods**

- `createskills(name, skill_list=None, paths=None, tool_description=None, agent_md_path=None, save=True)`
- `listskills()`
- `get_skills(name)`
- `deleteskills(name)`
- `loadskills(path=None)`
- `saveskills(path=None)`

If you pass `paths` into `createskills()`, those paths must already be resolvable in the current `Allskills` as concrete skills or skills root directories.

**Examples**

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

## 🏷️ `REGISTRY`

**Use case**

This is the process-level global `SkillsRegistry` singleton. Most named collection operations can be done directly around it.

**Parameters**

None. It is a ready-made object and does not need to be instantiated.

**Examples**

```python
from magicskills import REGISTRY

print([item.name for item in REGISTRY.listskills()])
```

## 🌐 `ALL_SKILLS()`

**Use case**

This is an accessor function that returns the built-in `Allskills` view from the current registry. Many top-level functions work naturally with the result of `ALL_SKILLS()` as their first argument.

**Parameters**

No parameters.

**Notes**

- `ALL_SKILLS()` always resolves the current value from `REGISTRY`.
- If you call `loadskills()` in the same process, calling `ALL_SKILLS()` again returns the refreshed `Allskills` view.

**Examples**

```python
from magicskills import ALL_SKILLS, listskill, readskill

print(listskill(ALL_SKILLS()))
print(readskill(ALL_SKILLS(), "demo"))
```

## 🏠 `DEFAULT_SKILLS_ROOT`

**Use case**

You want the default `.claude/skills` path for the current working directory, so you can reuse it in your own initialization or installation logic.

**Parameters**

None. It is a constant whose value is `Path.cwd() / ".claude" / "skills"`.

**Examples**

```python
from magicskills import DEFAULT_SKILLS_ROOT

print(DEFAULT_SKILLS_ROOT)
```

## 📋 `listskill()`

**Use case**

You want to format the skill list of a `Skills` collection into plain text output.

**Signature**

```python
listskill(skills: Skills) -> str
```

**Parameters**

- `skills`: the `Skills` collection to list

**Return value**

- returns a formatted multi-line string

**Examples**

```python
from magicskills import ALL_SKILLS, listskill

print(listskill(ALL_SKILLS()))
```

## 📖 `readskill()`

**Use case**

Read `SKILL.md` by skill name, or read any text file by file path.

**Signature**

```python
readskill(skills: Skills, target: str | Path) -> str
```

**Parameters**

- `skills`: the target `Skills` collection
- `target`: a skill name, or an explicit file path

**Return value**

- returns the text content of the file

**Examples**

Read by skill name:

```python
from magicskills import ALL_SKILLS, readskill

content = readskill(ALL_SKILLS(), "demo")
print(content)
```

Read by path:

```python
from pathlib import Path
from magicskills import ALL_SKILLS, readskill

content = readskill(ALL_SKILLS(), Path("./skills/demo/SKILL.md"))
print(content)
```

## 🔍 `showskill()`

**Use case**

You want more than `SKILL.md`; you want the metadata and full file contents of the entire skill directory.

**Signature**

```python
showskill(skills: Skills, target: str | Path) -> str
```

**Parameters**

- `skills`: the target `Skills` collection
- `target`: a skill name or a skill directory path

**Return value**

- returns a formatted full display string

**Examples**

```python
from magicskills import ALL_SKILLS, showskill

print(showskill(ALL_SKILLS(), "demo"))
```

## ▶️ `execskill()`

**Use case**

Use this when you want to execute commands via the Python API and receive structured execution results.

**Signature**

```python
execskill(
    skills: Skills,
    command: str,
    shell: bool = True,
    timeout: float | None = None,
    stream: bool = False,
) -> ExecResult
```

**Parameters**

- `skills`: the `Skills` collection required by the current API shape
- `command`: the command string to execute
- `shell`: whether to execute through a shell; default `True`
- `timeout`: timeout in seconds; omit to disable
- `stream`: whether to stream output directly to the current terminal; default `False`

**Return value**

- returns `ExecResult` with fields `command`, `returncode`, `stdout`, and `stderr`
- when `stream=True`, `stdout` and `stderr` are empty strings because the output is already written directly to the terminal

**Examples**

Get a structured result:

```python
from magicskills import ALL_SKILLS, execskill

result = execskill(ALL_SKILLS(), "echo hello", stream=False)
print(result.returncode, result.stdout, result.stderr)
```

Execute in no-shell mode:

```python
from magicskills import ALL_SKILLS, execskill

result = execskill(ALL_SKILLS(), "python -c 'print(123)'", shell=False)
print(result.stdout)
```

Stream execution:

```python
from magicskills import ALL_SKILLS, execskill

execskill(ALL_SKILLS(), "pytest -q", stream=True)
```

With timeout:

```python
from magicskills import ALL_SKILLS, execskill

result = execskill(ALL_SKILLS(), "sleep 1", timeout=2)
print(result.returncode)
```

## 🧱 `createskill_template()`

**Use case**

You need to generate a minimal usable skill skeleton first, and then fill in `SKILL.md`, scripts, and reference files.

**Signature**

```python
createskill_template(name: str, base_dir: Path | str) -> Path
```

**Parameters**

- `name`: the skill name, also used as the directory name
- `base_dir`: the skills root under which the skill should be created

**Return value**

- returns the `Path` of the new skill directory

**Examples**

```python
from magicskills import createskill_template

skill_dir = createskill_template("my-skill", "./skills")
print(skill_dir)
```

This API ensures the following exist:

- `<base_dir>/<name>/`
- `references/`
- `scripts/`
- `assets/`
- a default `SKILL.md`

## 🧰 `createskill()`

**Use case**

You already have an existing skill directory and only want to register it into a `Skills` collection.

**Signature**

```python
createskill(
    skills: Skills,
    skill_path: Path | str,
    source: str | Path | None = None,
) -> Path
```

**Parameters**

- `skills`: the target `Skills` collection
- `skill_path`: the skill directory path, which must contain `SKILL.md`
- `source`: optional source information; if omitted, the absolute path of the parent directory is recorded by default

**Return value**

- returns the registered skill directory `Path`

**Examples**

Register into the built-in `Allskills` view:

```python
from magicskills import ALL_SKILLS, createskill

path = createskill(ALL_SKILLS(), "./skills/demo")
print(path)
```

Explicitly record the source:

```python
from magicskills import ALL_SKILLS, createskill

path = createskill(
    ALL_SKILLS(),
    "./skills/demo",
    source="https://github.com/example/repo.git",
)
print(path)
```

Notes:

- This API registers an existing directory and does not copy files.
- If you register a skill into a non-`Allskills` collection, the same skill is also added to the built-in `Allskills` view.
- If the target collection belongs to the current `REGISTRY`, the registry is saved automatically.

## 📦 `install()`

**Use case**

You want to install skills through the Python API instead of calling the CLI.

**Signature**

```python
install(
    source: str | None = None,
    global_: bool = False,
    universal: bool = False,
    yes: bool = False,
    target_root: Path | str | None = None,
) -> list[Path]
```

**Parameters**

- `source`: a local path, GitHub short form, Git URL, or a skill name in the default repository
- `global_`: whether to use Home as the install base directory
- `universal`: whether to switch the install root to `.agent/skills`
- `yes`: whether to overwrite directly if the target already exists
- `target_root`: custom install directory; cannot be used together with `global_` or `universal`

**Return value**

- returns the list of directories actually written to disk

**Examples**

Install one skill from the default repository:

```python
from magicskills import install

paths = install("demo")
print(paths)
```

Batch install from a local directory:

```python
from magicskills import install

paths = install("./skills", target_root="./custom-skills", yes=True)
print(paths)
```

Install using a GitHub short form:

```python
from magicskills import install

paths = install("owner/repo", global_=True)
print(paths)
```

Notes:

- The resolution order is the same as the CLI: local path first, then default repository skill name, then Git repository.
- After installation, skills are registered into the built-in `Allskills` view and persisted into the current `REGISTRY`.

## 📤 `uploadskill()`

**Use case**

You want to trigger the skill upload, fork, push, and PR workflow directly from Python code.

**Signature**

```python
uploadskill(
    skills: Skills | Path | str,
    target: str | Path | None = None,
) -> UploadResult
```

**Parameters**

- `skills`: two valid forms are supported
- pass a `Skills` object: in this case you must also pass `target`, which identifies a skill by name or path in that collection
- pass a `Path` or `str` path: in this case `target` stays `None`, and the first argument itself is the skill directory
- `target`: used when the first argument is `Skills`, representing a skill name or skill directory path

**Return value**

- returns `UploadResult` with fields `skill_name`, `repo`, `branch`, `remote_subpath`, `committed`, `pushed`, `push_remote`, `push_branch`, `pr_url`, and `pr_created`

**Examples**

Upload by name from the built-in `Allskills` view:

```python
from magicskills import ALL_SKILLS, uploadskill

result = uploadskill(ALL_SKILLS(), "demo")
print(result.pr_url)
```

Upload directly by local path:

```python
from magicskills import uploadskill

result = uploadskill("./skills/demo")
print(result.repo, result.push_branch)
```

**Notes**

- Before running, the same prerequisites as the CLI must be satisfied: `gh` must be installed and authenticated locally, and the target skill directory must contain `SKILL.md`.
- If you pass a `Skills` object and multiple skills have the same name, pass an explicit directory path instead.

## 🗑️ `deleteskill()`

**Use case**

You want to delete a skill from the Python API; when applied to the built-in `Allskills` view, it also deletes the directory on disk.

**Signature**

```python
deleteskill(skills: Skills, target: str) -> str
```

**Parameters**

- `skills`: the target `Skills` collection
- `target`: a skill name or a skill directory path

**Return value**

- returns the resolved path string of the deleted skill

**Examples**

Remove only from a named collection:

```python
from magicskills import REGISTRY, deleteskill

team = REGISTRY.get_skills("coder")
deleted = deleteskill(team, "./skills/demo")
print(deleted)
```

Delete completely from the built-in `Allskills` view:

```python
from magicskills import ALL_SKILLS, deleteskill

deleted = deleteskill(ALL_SKILLS(), "demo")
print(deleted)
```

Notes:

- When you pass a non-`Allskills` collection, the skill is only removed from that collection and not deleted from disk.
- When you pass the built-in `Allskills` view, the actual skill directory is deleted, and matching path references are removed from other named collections as well.

## 🧩 `createskills()`

**Use case**

You want to create a named `Skills` collection and register it into the global `REGISTRY` immediately.

**Signature**

```python
createskills(
    name: str,
    skill_list: list[Skill] | str | None = None,
    paths: list[str] | None = None,
    tool_description: str | None = None,
    agent_md_path: str | None = None,
) -> Skills
```

**Parameters**

- `name`: the collection name
- `skill_list`: may be a list of `Skill` objects, or a single skill name string
- `paths`: a list of skills root paths or individual skill directory paths
- `tool_description`: the tool description text of the collection
- `agent_md_path`: which `AGENTS.md` this collection should sync to by default

**Return value**

- returns the created `Skills` object and persists it into the registry by default

**Examples**

Create an empty collection:

```python
from magicskills import createskills

skills = createskills("coder")
print(skills.name, len(skills.skills))
```

Create by paths:

```python
from magicskills import createskills

# Prerequisite: these skills have already entered the built-in Allskills view via install/createskill
skills = createskills(
    "coder",
    paths=["./.claude/skills"],
    tool_description="Unified skill tool for coding tasks",
    agent_md_path="./agents/coder/AGENTS.md",
)
print(skills.agent_md_path)
```

Create from a single skill name:

```python
from magicskills import createskills

# Prerequisite: the built-in Allskills view can already resolve a skill named demo
skills = createskills("reviewer", skill_list="demo")
print([item.name for item in skills.skills])
```

**Notes**

- If both `paths` and `skill_list` are omitted, an empty collection is created.
- `paths` and string-form `skill_list` both depend on the current built-in `Allskills` view being able to resolve the target skill or its parent skills root.

## 🗂️ `listskills()`

**Use case**

List all named collections currently managed by the global `REGISTRY`.

**Signature**

```python
listskills() -> list[Skills]
```

**Parameters**

None.

**Return value**

- returns a list of `Skills` objects

**Examples**

```python
from magicskills import listskills

for item in listskills():
    print(item.name, len(item.skills))
```

## 🧹 `deleteskills()`

**Use case**

Delete the registration of a named `Skills` collection.

**Signature**

```python
deleteskills(name: str) -> None
```

**Parameters**

- `name`: the name of the named collection to delete

**Examples**

```python
from magicskills import deleteskills

deleteskills("coder")
```

**Notes**

- Only the collection registration is deleted; skill files remain intact.
- `Allskills` cannot be deleted.

## 🔄 `syncskills()`

**Use case**

Sync a `Skills` collection into an `AGENTS.md` file.

**Signature**

```python
syncskills(skills: Skills, output_path: Path | str | None = None) -> Path
```

**Parameters**

- `skills`: the `Skills` collection to sync
- `output_path`: the target file path; if omitted, `skills.agent_md_path` is used

**Return value**

- returns the final written file path as a `Path`

**Examples**

Sync to the collection's default file:

```python
from magicskills import REGISTRY, syncskills

coder = REGISTRY.get_skills("coder")
path = syncskills(coder)
print(path)
```

Sync to a specified file:

```python
from magicskills import REGISTRY, syncskills

coder = REGISTRY.get_skills("coder")
path = syncskills(coder, "./AGENTS.md")
print(path)
```

## 📥 `loadskills()`

**Use case**

Reload the persisted state of the global `REGISTRY` from disk.

**Signature**

```python
loadskills(path: str | None = None) -> list[Skills]
```

**Parameters**

- `path`: optional registry JSON path; if omitted, the current `REGISTRY` store path is used

**Return value**

- returns the list of loaded `Skills`

**Examples**

```python
from magicskills import loadskills

collections = loadskills("./collections.json")
print([item.name for item in collections])
```

## 💾 `saveskills()`

**Use case**

Write the current global `REGISTRY` state back to disk.

**Signature**

```python
saveskills(path: str | None = None) -> str
```

**Parameters**

- `path`: optional output path; if omitted, save to the current `REGISTRY` store path

**Return value**

- returns the written file path as a string

**Examples**

```python
from magicskills import saveskills

saved_path = saveskills("./collections.json")
print(saved_path)
```

## ✏️ `change_tool_description()` / `changetooldescription()`

**Use case**

Modify the `tool_description` metadata on a `Skills` collection.

**Signature**

```python
change_tool_description(skills: Skills, description: str) -> None
changetooldescription(skills: Skills, description: str) -> None
```

**Parameters**

- `skills`: the target `Skills` collection
- `description`: the new description text

**Examples**

```python
from magicskills import REGISTRY, change_tool_description

coder = REGISTRY.get_skills("coder")
change_tool_description(coder, "Unified skill tool for coding and review tasks")
```

Call through the compatibility alias:

```python
from magicskills import REGISTRY, changetooldescription

coder = REGISTRY.get_skills("coder")
changetooldescription(coder, "Unified skill tool")
```

**Notes**

- If the target collection belongs to the current `REGISTRY`, this API automatically persists the modification into the registry.
- This metadata is suitable for external frameworks or your own wrapper layer to read.
- It does not change the fixed `AGENTS.md` usage template produced by `syncskills()`.

## 🤖 `skill_tool()`

**Use case**

You want to reuse a unified agent/tool-call style entry point in Python, rather than dispatching `listskill`, `readskill`, and `execskill` yourself.

**Signature**

```python
skill_tool(skills: Skills, action: str, arg: str = "") -> dict[str, object]
```

**Parameters**

- `skills`: the target `Skills` collection
- `action`: action name, supporting:
- `listskill`, `list`, `list_metadata`
- `readskill`, `read`, `read_file`
- `execskill`, `exec`, `run_command`
- `arg`: action argument
- for `listskill`, it may be empty
- for `readskill`, pass a skill name or file path
- for `execskill`, pass a plain command string, JSON string, or the legacy `name::command` format

**Return value**

- returns a dictionary, typically shaped like `{"ok": True, "action": "...", "result": ...}`
- when the action is unknown or execution fails, returns `{"ok": False, "error": "..."}`

**Examples**

List skills:

```python
from magicskills import ALL_SKILLS, skill_tool

print(skill_tool(ALL_SKILLS(), "listskill"))
```

Read a skill:

```python
from magicskills import ALL_SKILLS, skill_tool

print(skill_tool(ALL_SKILLS(), "readskill", "demo"))
```

Execute a plain command:

```python
from magicskills import ALL_SKILLS, skill_tool

print(skill_tool(ALL_SKILLS(), "execskill", "echo hello"))
```

Execute a JSON-form command:

```python
from magicskills import ALL_SKILLS, skill_tool

print(skill_tool(ALL_SKILLS(), "execskill", '{"command":"echo hello"}'))
```

Execute the legacy command format:

```python
from magicskills import ALL_SKILLS, skill_tool

print(skill_tool(ALL_SKILLS(), "execskill", "demo::echo hello"))
```

<a id="tips-en"></a>
# 💡 Tips

## 🧾 Integration via `AGENTS.md`

It is recommended to first install or maintain all skills under one shared skills root, then select the subset actually needed by a given agent, build a named skills collection from it, and finally sync that collection into the target `AGENTS.md`.

This has several benefits:

- the physical storage location of skills stays unified, making maintenance, upgrades, and debugging easier
- different agents can reuse the same underlying skills while exposing only the subset each one actually needs
- `AGENTS.md` keeps only the skills that the current agent truly needs to see, reducing context noise

The recommended flow is:

1. Install skills into a shared directory, such as `./.claude/skills` or `~/.claude/skills`
2. Use `createskills` to create a named collection that contains only a subset of skills
3. Use `syncskills` to write that collection into the target `AGENTS.md`
4. Let the agent read only that target `AGENTS.md`

Example:

```bash
magicskills install demo --target ./.claude/skills
magicskills createskills coder --paths ./.claude/skills
magicskills syncskills coder --output ./agents/coder/AGENTS.md -y
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
magicskills skill-tool listskill --name coder
magicskills skill-tool readskill --name coder --arg demo
magicskills skill-tool execskill --name coder --arg "echo hello"
```

Python API entrypoint:

```python
skills.skill_tool(action: str, arg: str = "")
```

For example:

```python
from magicskills import ALL_SKILLS, Skills

skill_a = ALL_SKILLS().get_skill("demo")
skill_b = ALL_SKILLS().get_skill("code-review")  # Replace with your own second skill name or path

skills = Skills(
    skill_list=[skill_a, skill_b],
    name="coder",
)

print(skills.skill_tool("listskill"))
print(skills.skill_tool("readskill", "demo"))
print(skills.skill_tool("execskill", "echo hello"))
```

This approach fits two kinds of scenarios:

- the agent supports tool-call / function-call mechanisms, but cannot read `AGENTS.md`
- you want the upper-level program itself to control when to list skills, when to read skills, and when to execute commands

The simplified rule of thumb is:

- for agents that read `AGENTS.md`, prefer `createskills + syncskills`
- for agents that do not read `AGENTS.md`, prefer `skill-tool` or `skills.skill_tool()`

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
