# Real-World Pain Points
Project: https://github.com/Narwhal-Lab/MagicSkills

For many teams building multi-agent systems, the first thing that gets out of control is not the model, but skill management.

The same skill directory often needs to serve agent applications such as Codex, Cursor, and Claude Code, while also being used by multiple agents created inside frameworks such as LangChain and LangGraph.

What usually follows is not reuse, but duplication:
the same skill directory gets copied into multiple Agent projects, and once that skill directory needs to change, you have to maintain it in multiple places. It quickly forks.

# How MagicSkills Solves This
MagicSkills is not trying to be yet another Agent framework. It adds a local-first skill infrastructure layer for multi-Agent projects.

In one sentence:
build a skill once, reuse it across every Agent.

More specifically:

- MagicSkills first aggregates installed skills into one shared skill pool
- It then creates dedicated `Skills` collections for different Agents, exposing only the capabilities each Agent actually needs
- Finally, based on how each runtime integrates skills, it either syncs to `AGENTS.md` / `CLAUDE.md` or exposes them as `tool / function`

One lower-level implementation detail is worth mentioning:
MagicSkills aggregates installed skills into a unified `Allskills` view, but for external communication, “shared skill pool” is the easier concept to understand.

# An Extreme Example
Assume you want to do something as extreme as possible, and also as representative as possible of MagicSkills' value:

you want one single skill directory, with no copying at all, to serve the following Agent applications and the agents built inside Agent frameworks:

- Codex
- Cursor
- Claude Code
- Windsurf
- Aider
- AutoGen
- CrewAI
- LangChain
- LangGraph
- Haystack
- Semantic Kernel
- smolagents
- LlamaIndex

In that case, the whole process can be broken down into four steps.

## 1. Install MagicSkills

```bash
git clone https://github.com/Narwhal-Lab/MagicSkills.git
cd MagicSkills
pip install -e .
```

## 2. Install the Required Skills into the Shared Skill Pool

```bash
# Option 1: install skills from a local directory
magicskills install skill_template

# Option 2: install skills from GitHub
magicskills install anthropics/skills
```

Notes:

- The first command installs skills from the local `skill_template`, such as `c_2_ast`
- The second command installs more skills from GitHub, such as `pdf`, `docx`, `brand-guidelines`, `doc-coauthoring`, and `canvas-design`
- The install path can be specified with `-t`, or you can use the default path
- No matter where they are installed, MagicSkills aggregates those installed skills into one shared skill pool

## 3. Create Dedicated `Skills` Collections for Each Agent

This is the most important part of the design.

Instead of copying a skill directory into some Agent-specific folder,
you first create a named `Skills` collection for each Agent and select only the skills that Agent should actually use.

For example:

- For Agent applications such as Codex, Cursor, Claude Code, Windsurf, and Aider, we assume each example corresponds to one Agent, so each example usually needs only one `Skills` collection
- For the `tool / function` framework examples below, we assume each framework creates two agents internally, so each framework gets two `Skills` collections: one for `agent1` and one for `agent2`

```bash
# Agent applications that read AGENTS.md / CLAUDE.md
magicskills addskills codex_skills --skill-list c_2_ast docx  # Assume Codex currently needs c_2_ast and docx; package those two skills into a Skills collection named codex_skills for Codex
magicskills addskills cursor_skills --skill-list c_2_ast docx  # Assume Cursor currently needs c_2_ast and docx; package those two skills into a Skills collection named cursor_skills for Cursor
magicskills addskills claudecode --skill-list c_2_ast brand-guidelines  # Assume Claude Code currently needs c_2_ast and brand-guidelines; package those two skills into a Skills collection named claudecode for Claude Code
magicskills addskills Windsurf_skills --skill-list c_2_ast doc-coauthoring  # Assume Windsurf currently needs c_2_ast and doc-coauthoring; package those two skills into a Skills collection named Windsurf_skills for Windsurf
magicskills addskills Aider_skills --skill-list c_2_ast docx  # Assume Aider currently needs c_2_ast and docx; package those two skills into a Skills collection named Aider_skills for Aider

# Examples for tool / function frameworks
magicskills addskills autogen_agent1_skills --skill-list c_2_ast pdf  # Assume AutoGen agent1 currently needs c_2_ast and pdf; package those two skills into a Skills collection named autogen_agent1_skills for AutoGen agent1
magicskills addskills autogen_agent2_skills --skill-list c_2_ast docx  # Assume AutoGen agent2 currently needs c_2_ast and docx; package those two skills into a Skills collection named autogen_agent2_skills for AutoGen agent2
magicskills addskills crewai_agent1_skills --skill-list c_2_ast pdf  # Assume CrewAI agent1 currently needs c_2_ast and pdf; package those two skills into a Skills collection named crewai_agent1_skills for CrewAI agent1
magicskills addskills crewai_agent2_skills --skill-list c_2_ast docx  # Assume CrewAI agent2 currently needs c_2_ast and docx; package those two skills into a Skills collection named crewai_agent2_skills for CrewAI agent2
magicskills addskills langchain_agent1_skills --skill-list c_2_ast pdf  # Assume LangChain agent1 currently needs c_2_ast and pdf; package those two skills into a Skills collection named langchain_agent1_skills for LangChain agent1
magicskills addskills langchain_agent2_skills --skill-list c_2_ast docx  # Assume LangChain agent2 currently needs c_2_ast and docx; package those two skills into a Skills collection named langchain_agent2_skills for LangChain agent2
magicskills addskills langgraph_agent1_skills --skill-list c_2_ast pdf  # Assume LangGraph agent1 currently needs c_2_ast and pdf; package those two skills into a Skills collection named langgraph_agent1_skills for LangGraph agent1
magicskills addskills langgraph_agent2_skills --skill-list c_2_ast docx  # Assume LangGraph agent2 currently needs c_2_ast and docx; package those two skills into a Skills collection named langgraph_agent2_skills for LangGraph agent2
magicskills addskills haystack_agent1_skills --skill-list c_2_ast pdf  # Assume Haystack agent1 currently needs c_2_ast and pdf; package those two skills into a Skills collection named haystack_agent1_skills for Haystack agent1
magicskills addskills haystack_agent2_skills --skill-list c_2_ast docx  # Assume Haystack agent2 currently needs c_2_ast and docx; package those two skills into a Skills collection named haystack_agent2_skills for Haystack agent2
magicskills addskills semantic_kernel_agent1_skills --skill-list c_2_ast pdf  # Assume Semantic Kernel agent1 currently needs c_2_ast and pdf; package those two skills into a Skills collection named semantic_kernel_agent1_skills for Semantic Kernel agent1
magicskills addskills semantic_kernel_agent2_skills --skill-list c_2_ast docx  # Assume Semantic Kernel agent2 currently needs c_2_ast and docx; package those two skills into a Skills collection named semantic_kernel_agent2_skills for Semantic Kernel agent2
magicskills addskills smolagents_agent1_skills --skill-list c_2_ast pdf  # Assume smolagents agent1 currently needs c_2_ast and pdf; package those two skills into a Skills collection named smolagents_agent1_skills for smolagents agent1
magicskills addskills smolagents_agent2_skills --skill-list c_2_ast docx  # Assume smolagents agent2 currently needs c_2_ast and docx; package those two skills into a Skills collection named smolagents_agent2_skills for smolagents agent2
magicskills addskills llamaindex_agent1_skills --skill-list c_2_ast pdf  # Assume LlamaIndex agent1 currently needs c_2_ast and pdf; package those two skills into a Skills collection named llamaindex_agent1_skills for LlamaIndex agent1
magicskills addskills llamaindex_agent2_skills --skill-list c_2_ast docx  # Assume LlamaIndex agent2 currently needs c_2_ast and docx; package those two skills into a Skills collection named llamaindex_agent2_skills for LlamaIndex agent2
```

This step illustrates something critical:

every skill in the shared skill pool can be freely combined into multiple `Skills` collections for different Agents.
In other words, the same `c_2_ast` skill does not need to be copied in order to serve Codex, Cursor, Claude Code, LangChain, LangGraph, AutoGen, and other systems at the same time.

## 4. Adapt to Each Runtime's Integration Style

Once you have the right `Skills` collections, the remaining work becomes runtime adaptation.

For runtimes such as Codex, Cursor, Claude Code, Windsurf, and Aider that read `AGENTS.md` or `CLAUDE.md`, you can use:

```bash
magicskills syncskills <skills_name> --output ./AGENTS.md -y
magicskills syncskills <skills_name> --mode cli_description --output ./AGENTS.md -y
magicskills syncskills <skills_name> --output ./CLAUDE.md -y
```

Where:

- The default mode is suitable for runtimes that can directly consume the `<usage> + <available_skills>` structure in `AGENTS.md`
- `--mode cli_description` is suitable for runtimes that cannot consume that structure directly and instead need the unified CLI flow `magicskills skill-tool listskill/readskill/execskill --name <skills_name>`
- `--output` specifies the output path, so the target file does not have to be `AGENTS.md`; it can also be `CLAUDE.md` or any other runtime-specific file

For `tool / function` frameworks such as LangChain, LangGraph, AutoGen, CrewAI, Haystack, Semantic Kernel, smolagents, and LlamaIndex, you simply load the `Skills` collection for a specific agent inside that framework, then expose it as `tool / function`:

```python
from magicskills import REGISTRY

skills = REGISTRY.get_skills("langchain_agent1_skills")
```

After that, you wire `skills.skill_tool(...)` and `skills.tool_description` into each agent through the framework's own `tool / function` mechanism.

## What Makes This Extreme and Valuable

The most extreme part is this:

you are not maintaining one copy of a skill for each Agent.
You are maintaining one shared skill pool for all Agents, slicing out different `Skills` collections as needed, and then adapting them based on runtime differences.

That means:

- The same skill can serve all of the systems above without being copied
- Skill maintenance is centralized in one place: the single copy inside the shared skill pool
- Each Agent sees only the capabilities it actually needs
- Adding a new runtime does not require rebuilding the entire skill layer; you only need to create a new collection and connect the appropriate adaptation layer
