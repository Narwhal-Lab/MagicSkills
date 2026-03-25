# 现实痛点
项目地址：https://github.com/Narwhal-Lab/MagicSkills

很多团队做多 Agent，最先失控的不是模型，而是 skill 管理。

同一个 skill 目录，往往既想给 Codex、Cursor、Claude Code 这类 Agent 应用使用，也想给 LangChain、LangGraph 这类框架里创建的多个 agent 使用。

结果往往不是“复用”，而是“复制”：
同一个 skill 目录会被拷贝进多个 Agent 项目里，一旦这个 skill 目录需要更新，就要在多个地方重复维护，最后很快分叉。

# MagicSkills 如何解决
MagicSkills 解决的，不是“再造一个 Agent 框架”，而是给多 Agent 项目补上一层本地优先的 skill 基础设施。

一句话概括就是：
一次构建 skill，供每个 Agent 复用。

具体来说：

- MagicSkills 会先把已安装的 skill 汇总到统一的共享 skill 池中
- 然后为不同 Agent 创建各自的 `Skills` 集合，只暴露它真正需要的能力
- 最后再根据不同运行时的接入方式，选择同步到 `AGENTS.md` / `CLAUDE.md`，或者暴露为 `tool / function`

这里可以补充一句更底层的实现概念：
MagicSkills 会把已安装的 skill 汇总到统一的 `Allskills` 视图中，但对外传播时，更容易理解的说法是“共享 skill 池”。

# 举个最极端的实例
假设你现在要做一件最极端、也最能体现 MagicSkills 价值的事：

你希望同一份 skill 目录，不做任何复制，就同时服务下列 Agent 应用，以及 Agent 框架里搭建好的 agent：

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

这时候，整个过程可以整理成下面四步。

## 1. 先安装 MagicSkills

```bash
git clone https://github.com/Narwhal-Lab/MagicSkills.git
cd MagicSkills
pip install -e .
```

## 2. 把需要的 skill 安装到共享 skill 池

```bash
# 方式一：从本地安装 skill
magicskills install skill_template

# 方式二：从 GitHub 安装 skill
magicskills install anthropics/skills
```

说明：

- 第一条命令会从本地的 `skill_template` 安装 skill，例如 `c_2_ast`
- 第二条命令会从 GitHub 安装更多 skill，例如 `pdf`、`docx`、`brand-guidelines`、`doc-coauthoring`、`canvas-design`
- 安装路径可以通过 `-t` 指定，也可以使用默认路径
- 无论安装到哪里，MagicSkills 都会把这些已安装的 skill 汇总到统一的共享 skill 池中

## 3. 为每个 Agent 创建各自的 `Skills` 集合

这一步是整个设计里最关键的地方。

不是直接把某个 skill 目录复制到某个 Agent 指定使用 skill 的目录下，
而是先为每个 Agent 创建一个命名的 `Skills` 集合，把它真正要使用的 skill 先选出来。

例如：

- 对于 Codex、Cursor、Claude Code、Windsurf、Aider 这类 Agent 应用，这里默认每个 example 对应一个 Agent，因此通常只需要创建一个 `Skills` 集合
- 对于下面这组 `tool / function` 框架示例，这里统一假设每个智能体框架内部都创建了两个 agent，因此每个框架下面都会对应两个 `Skills` 集合，分别给 `agent1` 和 `agent2` 使用

```bash
# 面向读取 AGENTS.md / CLAUDE.md 的 Agent 应用
magicskills addskills codex_skills --skill-list c_2_ast docx  # 假设当前 Codex 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 codex_skills 给 Codex 使用
magicskills addskills cursor_skills --skill-list c_2_ast docx  # 假设当前 Cursor 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 cursor_skills 给 Cursor 使用
magicskills addskills claudecode --skill-list c_2_ast brand-guidelines  # 假设当前 Claude Code 需要的 skill 是 c_2_ast 和 brand-guidelines，将这两个 skill 封装为一个 Skills 集合 claudecode 给 Claude Code 使用
magicskills addskills Windsurf_skills --skill-list c_2_ast doc-coauthoring  # 假设当前 Windsurf 需要的 skill 是 c_2_ast 和 doc-coauthoring，将这两个 skill 封装为一个 Skills 集合 Windsurf_skills 给 Windsurf 使用
magicskills addskills Aider_skills --skill-list c_2_ast docx  # 假设当前 Aider 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 Aider_skills 给 Aider 使用

# 面向 tool / function 框架的 example
magicskills addskills autogen_agent1_skills --skill-list c_2_ast pdf  # 假设当前 AutoGen agent1 需要的 skill 是 c_2_ast 和 pdf，将这两个 skill 封装为一个 Skills 集合 autogen_agent1_skills 给 AutoGen agent1 使用
magicskills addskills autogen_agent2_skills --skill-list c_2_ast docx  # 假设当前 AutoGen agent2 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 autogen_agent2_skills 给 AutoGen agent2 使用
magicskills addskills crewai_agent1_skills --skill-list c_2_ast pdf  # 假设当前 CrewAI agent1 需要的 skill 是 c_2_ast 和 pdf，将这两个 skill 封装为一个 Skills 集合 crewai_agent1_skills 给 CrewAI agent1 使用
magicskills addskills crewai_agent2_skills --skill-list c_2_ast docx  # 假设当前 CrewAI agent2 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 crewai_agent2_skills 给 CrewAI agent2 使用
magicskills addskills langchain_agent1_skills --skill-list c_2_ast pdf  # 假设当前 LangChain agent1 需要的 skill 是 c_2_ast 和 pdf，将这两个 skill 封装为一个 Skills 集合 langchain_agent1_skills 给 LangChain agent1 使用
magicskills addskills langchain_agent2_skills --skill-list c_2_ast docx  # 假设当前 LangChain agent2 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 langchain_agent2_skills 给 LangChain agent2 使用
magicskills addskills langgraph_agent1_skills --skill-list c_2_ast pdf  # 假设当前 LangGraph agent1 需要的 skill 是 c_2_ast 和 pdf，将这两个 skill 封装为一个 Skills 集合 langgraph_agent1_skills 给 LangGraph agent1 使用
magicskills addskills langgraph_agent2_skills --skill-list c_2_ast docx  # 假设当前 LangGraph agent2 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 langgraph_agent2_skills 给 LangGraph agent2 使用
magicskills addskills haystack_agent1_skills --skill-list c_2_ast pdf  # 假设当前 Haystack agent1 需要的 skill 是 c_2_ast 和 pdf，将这两个 skill 封装为一个 Skills 集合 haystack_agent1_skills 给 Haystack agent1 使用
magicskills addskills haystack_agent2_skills --skill-list c_2_ast docx  # 假设当前 Haystack agent2 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 haystack_agent2_skills 给 Haystack agent2 使用
magicskills addskills semantic_kernel_agent1_skills --skill-list c_2_ast pdf  # 假设当前 Semantic Kernel agent1 需要的 skill 是 c_2_ast 和 pdf，将这两个 skill 封装为一个 Skills 集合 semantic_kernel_agent1_skills 给 Semantic Kernel agent1 使用
magicskills addskills semantic_kernel_agent2_skills --skill-list c_2_ast docx  # 假设当前 Semantic Kernel agent2 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 semantic_kernel_agent2_skills 给 Semantic Kernel agent2 使用
magicskills addskills smolagents_agent1_skills --skill-list c_2_ast pdf  # 假设当前 smolagents agent1 需要的 skill 是 c_2_ast 和 pdf，将这两个 skill 封装为一个 Skills 集合 smolagents_agent1_skills 给 smolagents agent1 使用
magicskills addskills smolagents_agent2_skills --skill-list c_2_ast docx  # 假设当前 smolagents agent2 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 smolagents_agent2_skills 给 smolagents agent2 使用
magicskills addskills llamaindex_agent1_skills --skill-list c_2_ast pdf  # 假设当前 LlamaIndex agent1 需要的 skill 是 c_2_ast 和 pdf，将这两个 skill 封装为一个 Skills 集合 llamaindex_agent1_skills 给 LlamaIndex agent1 使用
magicskills addskills llamaindex_agent2_skills --skill-list c_2_ast docx  # 假设当前 LlamaIndex agent2 需要的 skill 是 c_2_ast 和 docx，将这两个 skill 封装为一个 Skills 集合 llamaindex_agent2_skills 给 LlamaIndex agent2 使用
```

这一步说明了一件非常关键的事：

共享 skill 池里的每个 skill 能力，都可以被自由组合成多个不同 Agent 的 `Skills` 集合。
也就是说，同一个 `c_2_ast` skill，不需要复制，就可以同时进入 Codex、Cursor、Claude Code、LangChain、LangGraph、AutoGen 等不同系统各自的能力边界里。

## 4. 再根据不同运行时的使用方式做适配

有了各自的 `Skills` 集合之后，后面的事情就变成运行时适配。

对于 Codex、Cursor、Claude Code、Windsurf、Aider 这类会读取 `AGENTS.md` 或 `CLAUDE.md` 的运行时，可以用：

```bash
magicskills syncskills <skills_name> --output ./AGENTS.md -y
magicskills syncskills <skills_name> --mode cli_description --output ./AGENTS.md -y
magicskills syncskills <skills_name> --output ./CLAUDE.md -y
```

其中：

- 默认模式适合能够直接消费 `AGENTS.md` 中 `<usage> + <available_skills>` 结构的运行时
- `--mode cli_description` 适合不能直接消费该结构、需要通过 `magicskills skill-tool listskill/readskill/execskill --name <skills_name>` 这套统一 CLI 流程来使用 skill 的运行时
- `--output` 用来指定输出路径，因此目标文件不一定只能是 `AGENTS.md`，也可以按运行时要求输出成 `CLAUDE.md` 等文件

对于 LangChain、LangGraph、AutoGen、CrewAI、Haystack、Semantic Kernel、smolagents、LlamaIndex 这类 `tool / function` 框架，则直接在代码里加载针对该框架内某个 agent 的 `Skills` 集合，再暴露为 `tool / function`：

```python
from magicskills import REGISTRY

skills = REGISTRY.get_skills("langchain_agent1_skills")
```

后续再通过各自框架的 `tool / function` 机制，把 `skills.skill_tool(...)` 和 `skills.tool_description` 接到每个 agent 即可。

## 这件事最极端、也最有价值的地方是什么

最极端的地方在于：

你不是在为每个 Agent 单独维护一份 skill，
而是在为所有 Agent 维护同一个底层共享 skill 池，再按需切出各自的 `Skills` 集合，最后根据运行时差异做适配。

这意味着：

- 同一份 skill 无需复制，就能服务上述所有智能体系统
- skill 的维护成本集中在一处，只需要维护共享 skill 池里的那一份
- 每个 Agent 只看到自己真正需要的那组能力
- 新增一个运行时，不需要重写整套 skill，只需要新建集合并接上对应适配层
