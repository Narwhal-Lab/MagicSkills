[返回 README](../README.zh-CN.md) | [English](./cli.md)

<a id="cli-cn"></a>

# 🛠️ CLI 命令

安装完成后会暴露 `magicskills` 命令：

```bash
magicskills -h
magicskills <command> -h
```

下面的示例默认以 `bash/zsh` 为例；如果你使用 PowerShell，请按 PowerShell 的引号和转义规则调整命令。

## 📚 CLI 命令总览

| 命令                      | 使用场景                                     | 主要能力                                                   |
| ------------------------- | -------------------------------------------- | ---------------------------------------------------------- |
| `listskill`             | 查看当前内置技能集合里有哪些 skill           | 列出 skill 名称、描述、`SKILL.md` 路径                   |
| `readskill`             | 读取 skill 说明或任意本地文本文件            | 按 skill 名称或文件路径输出内容                            |
| `execskill`             | 在当前工作目录执行命令                       | 支持流式输出、JSON 输出、无 shell 模式、自定义 skills 路径 |
| `syncskills`            | 把命名 skills 集合同步进 `AGENTS.md`       | 生成或替换 `<skills_system>` 区块                        |
| `install`               | 从本地目录、Git 仓库或默认技能仓库安装 skill | 复制 skill 文件并注册到 `Allskills`                      |
| `addskill`             | 把一个现成的 skill 注册到某个集合中      | 不复制文件，只注册元数据                                   |
| `uploadskill`           | 把本地 skill 提交到默认 MagicSkills 仓库     | 自动走 fork、push、PR 流程                                 |
| `deleteskill`           | 从某个集合中删除一个 skill，或全局删除       | 从命名集合中移除，或从 `Allskills` 删除目录并清理引用      |
| `showskill`             | 审查一个 skill 的完整内容                    | 显示元信息和 skill 目录下所有文件内容                      |
| `addskills`            | 创建一个命名 skills 集合                     | 为 agent 或团队建立独立 skill 集合                         |
| `listskills`            | 查看所有命名 skills 集合                     | 普通文本或 JSON 输出                                       |
| `deleteskills`          | 删除一个命名 skills 集合                     | 只删除集合注册，不删除 skill 文件                          |
| `changetooldescription` | 修改集合的 `tool_description` 元数据       | 更新面向 tool 的描述，便于后续查询与外部集成               |
| `changeclidescription` | 修改集合的 `cli_description` 元数据        | 更新面向 CLI 的描述，便于后续查询与外部集成                |
| `scanskill`            | 用 AI-Infra-Guard 扫描单个 skill            | 扫描一个 skill 并输出格式化结果                            |
| `scanskills`           | 用 AI-Infra-Guard 扫描一个命名集合中的全部 skill | 输出集合级汇总和逐 skill 摘要                         |
| `skill-tool`            | 以 tool function 风格调用 skill 能力         | 用统一 JSON 输出做 list/read/exec 分发                     |

## 📌 通用约定

- `Allskills` 是内置 skills 集合。`listskill`、`readskill`、`install`、`addskill`、`uploadskill`、`deleteskill`、`showskill` 默认都围绕它工作。
- 命名 skills 集合通过 `addskills` 创建，集合元数据保存在 `~/.magicskills/collections.json`。
- 很多命令同时接受 `skill 名称` 和 `skill 目录路径`。如果同名 skill 有多个，必须传显式路径。
- `install` 的默认安装目录由作用域决定。
- 当前项目默认目录：`./.claude/skills`
- `--global` 默认目录：`~/.claude/skills`
- `--universal` 当前项目目录：`./.agent/skills`
- `--global --universal` 目录：`~/.agent/skills`
- `readskill` 读取 skill 名称时，实际读取的是该 skill 目录下的 `SKILL.md`。
- `execskill` 推荐用 `--` 把 CLI 参数和待执行命令分开。

## 📋 `listskill`

**使用场景**

想快速查看当前 `Allskills` 或某个命名 skills 集合里已经注册了哪些 skill，以及每个 skill 的基础说明。

**命令格式**

```bash
magicskills listskill [--name <collection-name>]
```

**参数说明**

- `--name <collection-name>`：列出 `magicskills listskills` 中某个命名 skills 集合里的 skill；不传时使用 `Allskills`。

**功能示例**

```bash
magicskills listskill
magicskills listskill --name coder
```

输出会按顺序列出每个 skill 的：

- `name`
- `description`
- `path`（指向该 skill 的 `SKILL.md`）

## 📖 `readskill`

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

## ▶️ `execskill`

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

## 🔄 `syncskills`

**使用场景**

你已经创建了一个命名 skills 集合，想把它同步到某个 `AGENTS.md` 文件里，让 agent 在系统提示中感知这些 skills。

**命令格式**

```bash
magicskills syncskills <name> [-o OUTPUT] [--mode {none,cli_description}] [-y]
```

**参数说明**

- `<name>`：命名 skills 集合名称。
- `-o, --output`：输出文件路径；不传时使用该集合自己的 `agent_md_path`。
- `--mode`：同步渲染模式。
- `none`：保持原来的 `<usage> + <available_skills>` 结构。
- `cli_description`：只输出 `<usage>`，内容来自集合的 `cli_description`。
- `-y, --yes`：跳过交互确认，直接同步。

**模式选择建议**

- `none`：适合能够根据 `AGENTS.md` 中给出的 skill 信息列表直接发现并使用对应 skill 的 agent
- `cli_description`：适合不能根据 `AGENTS.md` 中给出的 skill 信息列表直接使用 skill、需要通过 `magicskills skill-tool` 的 CLI 说明来使用 skill 的 agent

**功能示例**

同步到集合默认的 `agent_md_path`：

```bash
magicskills syncskills coder
```

同步到指定文件：

```bash
magicskills syncskills coder --output ./AGENTS.md
```

只使用 `cli_description` 同步：

```bash
magicskills syncskills coder --mode cli_description
```

在 CI 或脚本中跳过确认：

```bash
magicskills syncskills coder -o ./AGENTS.md -y
```

补充说明：

- 如果目标文件不存在，命令会先创建文件并写入基础 `# AGENTS` 标题。
- 如果文件里已存在 `<skills_system>` 区块，命令会替换它；否则会把新块追加到文件末尾。
- `none` 是兼容模式，会完整保留之前的 XML 结构。

## 📦 `install`

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

## 🧰 `addskill`

**使用场景**

你已经有一个现成的 skill，只想把它注册进某个集合，而不是重新复制一份。

**命令格式**

```bash
magicskills addskill <target> [--source SOURCE] [--name COLLECTION]
```

**参数说明**

- `<target>`：可以是 skill 目录路径，也可以是内置 `Allskills` 中已可解析的 skill 名称。
- `--source`：可选，给这个 skill 记录来源信息；不传时默认记录 skill 所在父目录的绝对路径。
- `--name`：可选，目标 skills 集合名称；不传时默认注册到内置 `Allskills`。

**功能示例**

注册一个本地 skill 目录：

```bash
magicskills addskill ./skills/my-skill
```

显式记录来源仓库或来源目录：

```bash
magicskills addskill ./skills/my-skill --source https://github.com/owner/repo.git
```

按名称把一个已有 skill 加入某个命名 skills 集合：

```bash
magicskills addskill demo --name reviewer
```

补充说明：

- 这个命令的行为是“注册已有 skill”，不是“生成 skill 模板”。
- 当 `--name` 指向命名集合时，这个 skill 也会同步进入内置 `Allskills`。
- `description` 会从 `SKILL.md` frontmatter 中提取。

## 📤 `uploadskill`

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

## 🗑️ `deleteskill`

**使用场景**

你想把一个 skill 从某个集合里移除，或者从内置 `Allskills` 里彻底删除。

**命令格式**

```bash
magicskills deleteskill <target> [--name COLLECTION]
```

**参数说明**

- `<target>`：可以是 skill 名称，也可以是 skill 目录路径。
- `--name`：可选，目标 skills 集合名称；不传时默认作用于内置 `Allskills`。

**功能示例**

按名称删除：

```bash
magicskills deleteskill demo
```

只从某个命名 skills 集合中移除：

```bash
magicskills deleteskill demo --name reviewer
```

同名 skill 冲突时按路径删除：

```bash
magicskills deleteskill ./skills/demo
```

补充说明：

- 这个 CLI 命令默认作用于内置的 `Allskills`。
- 当作用于 `Allskills` 时，删除会直接移除实际 skill 目录，不会二次确认。
- 当 `--name` 指向命名集合时，只会把 skill 从该集合中移除；skill 目录和 `Allskills` 中的记录都会保留。
- 如果是从 `Allskills` 删除成功，而其他命名集合里也引用了同一路径的 skill，这些集合中的对应项也会一起被剔除。

## 🔍 `showskill`

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

- 输出会先展示 skill 概览，包括名称、描述、skill 目录、base_dir、`SKILL.md` 路径和安装来源。
- 然后会展示 skill 目录下的所有文件内容。
- 如果遇到二进制文件，会显示 `[binary file omitted: <size> bytes]`，不会直接打印乱码。

## 🧩 `addskills`

**使用场景**

你需要给某个 agent、团队或工作流创建一个独立的命名 skills 集合，再配合 `syncskills` 生成对应的 `AGENTS.md`。

**命令格式**

```bash
magicskills addskills <name> [--skill-list [SKILLS ...]] [--paths [PATHS ...]] [--tool-description TEXT] [--cli-description TEXT] [--agent-md-path PATH]
```

**参数说明**

- `<name>`：新集合名称，必须唯一。
- `--skill-list [SKILLS ...]`：显式指定要纳入集合的 skill。每一项都可以是 skill 名称或 skill 目录路径，底层会从 `Allskills` 里解析。
- `--paths [PATHS ...]`：把这些路径对应的 skills 纳入新集合。常见传法有两种。
- 传某个 skill 目录路径，例如 `./.claude/skills/demo`
- 传某个 skills 根目录，例如 `./.claude/skills`
- `--tool-description`：覆盖该集合的 `tool_description` 元数据。
- `--cli-description`：覆盖该集合的 `cli_description` 元数据。
- `--agent-md-path`：指定该集合默认同步到哪个 `AGENTS.md` 文件。

**功能示例**

创建一个空集合：

```bash
magicskills addskills coder
```

按显式 skill 列表创建：

```bash
magicskills addskills reviewer --skill-list demo code-review
```

按显式 skill 路径创建：

```bash
magicskills addskills reviewer --skill-list ./.claude/skills/code-review
```

从一个 skills 根目录构造集合：

```bash
magicskills addskills coder --paths ./.claude/skills
```

只纳入一个具体 skill：

```bash
magicskills addskills reviewer --paths ./.claude/skills/code-review
```

同时指定多个路径：

```bash
magicskills addskills fullstack --paths ./.claude/skills ./vendor-skills
```

创建集合时顺带设置元数据：

```bash
magicskills addskills coder \
  --paths ./.claude/skills \
  --tool-description "Unified skill tool for coding tasks" \
  --cli-description "Use magicskills CLI commands only" \
  --agent-md-path ./agents/coder/AGENTS.md
```

补充说明：

- 不传 `--skill-list` 和 `--paths` 时，当前版本会创建一个空的命名集合。
- `--skill-list` 和 `--paths` 不能同时使用。
- `--skill-list` 中的每一项都必须能在当前 `Allskills` 中解析到唯一 skill；如果名称重复，请改传 skill 目录路径。
- `--paths` 中的路径需要能解析到当前 `Allskills` 里已有的 skills或其上层 skills 根目录。
- 成功后会输出集合名和 `Skills count`。

## 🗂️ `listskills`

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
- `cli_description`
- `agent_md_path`

## 🧹 `deleteskills`

**使用场景**

一个或多个命名 skills 集合已经不用了，你只想删除它们的注册信息，但保留原始 skill 文件。

**命令格式**

```bash
magicskills deleteskills <name> [<name> ...]
```

**参数说明**

- `<name>`：要删除的一个或多个命名 skills 集合名称。

**功能示例**

删除一个命名集合：

```bash
magicskills deleteskills coder
```

一次删除多个命名集合：

```bash
magicskills deleteskills coder reviewer release_skills
```

补充说明：

- `deleteskills` 只删除集合注册信息，不会删除 skill 目录。
- 内置集合 `Allskills` 不能被删除。

## ✏️ `changetooldescription`

**使用场景**

你想调整某个命名 skills 集合上的 `tool_description` 元数据，方便后续通过 `listskills --json`、Python API 或外部框架读取。

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

补充说明：

- 这会更新集合元数据。
- 它不再影响 `syncskills` 的输出；这个字段保留给外部框架或你自己的包装层使用。

## ✏️ `changeclidescription`

**使用场景**

你想调整某个命名 skills 集合上的 `cli_description` 元数据，方便后续通过 `listskills --json`、Python API 或 `syncskills --mode cli_description` 读取。

**命令格式**

```bash
magicskills changeclidescription <name> <description>
```

**参数说明**

- `<name>`：命名 skills 集合名称。
- `<description>`：新的 CLI 描述文本；如果包含空格，记得加引号。

**功能示例**

更新描述：

```bash
magicskills changeclidescription coder "Whenever you receive a task, you must first run magicskills skill-tool listskill --name coder, then use readskill to inspect relevant docs, and finally decide whether to keep reading or run execskill."
```

更新后查看：

```bash
magicskills listskills --json
```

补充说明：

- 这会更新集合元数据。
- 只有在使用 `--mode cli_description` 时，它才会影响 `syncskills` 的输出。

## 🛡️ `scanskill`

**使用场景**

你想通过 AI-Infra-Guard 扫描一个本地 skill 目录，或者一个已经注册过的 skill 名称，并直接获得格式化后的终端结果。

**命令格式**

```bash
magicskills scanskill <target> [--name <collection-name>] [--base-url URL] [--model MODEL] [--api-key KEY] [--model-base-url URL] [--details] [--save-raw [PATH]]
```

**参数说明**

- `<target>`：skill 目录路径，或者一个已经注册的 skill 名称。
- `--name <collection-name>`：当 `<target>` 传的是 skill 名称而不是路径时，从指定命名集合中解析；不传时默认从 `Allskills` 查找。
- `--base-url URL`：AI-Infra-Guard 服务地址。
- `--model MODEL`：AI-Infra-Guard 使用的模型名称。
- `--api-key KEY`：模型服务的 API key。
- `--model-base-url URL`：可选的模型服务 base URL。
- `--details`：在默认摘要后，继续打印同一次扫描的格式化详细结果。
- `--save-raw [PATH]`：把同样的格式化详细结果保存到文本文件中；如果不传路径，默认保存到当前工作目录。

**环境变量**

如果不想每次都重复输入连接参数，可以预先设置：

- `MAGICSKILLS_AIG_BASE_URL`
- `MAGICSKILLS_AIG_MODEL`
- `MAGICSKILLS_AIG_API_KEY`
- `MAGICSKILLS_AIG_MODEL_BASE_URL`

**功能示例**

扫描一个本地 skill 目录：

```bash
magicskills scanskill /root/test-skill \
  --base-url http://localhost:8088 \
  --model qwen3-max \
  --api-key "$OPENAI_API_KEY" \
  --model-base-url "$OPENAI_BASE_URL"
```

从命名集合里按 skill 名称扫描：

```bash
magicskills scanskill xlsx --name haystack_agent2_skills
```

在终端里显示格式化详细结果：

```bash
magicskills scanskill xlsx --details
```

把格式化详细结果保存到当前目录：

```bash
magicskills scanskill xlsx --save-raw
```

把格式化详细结果保存到指定文件：

```bash
magicskills scanskill xlsx --save-raw ./reports/xlsx-scan.txt
```

**输出行为**

- 默认只输出两个盒状区块：`Skill Summary` 和 `Skill Results`。
- `--details` 会继续追加格式化的详细区块，例如 `Skill Report <name>` 和 `Skill Finding Details <name>`。
- `--save-raw` 会把与 `--details` 一致的格式化详细视图保存为纯文本文件，不依赖 `--details` 是否传入。
- `--save-raw` 这个参数名为了兼容性保留了下来，但现在保存的是格式化文本报告，不再是 JSON。
- 扫描命令不再提供 `--json`。

## 🛡️ `scanskills`

**使用场景**

你想扫描某个命名 skills 集合里的全部 skill，先看集合级风险汇总，再按需展开或保存详细结果。

**命令格式**

```bash
magicskills scanskills <name> [--base-url URL] [--model MODEL] [--api-key KEY] [--model-base-url URL] [--details] [--save-raw [PATH]]
```

**参数说明**

- `<name>`：要扫描的命名 skills 集合名称。
- `--base-url URL`：AI-Infra-Guard 服务地址。
- `--model MODEL`：AI-Infra-Guard 使用的模型名称。
- `--api-key KEY`：模型服务的 API key。
- `--model-base-url URL`：可选的模型服务 base URL。
- `--details`：在集合级摘要后，为每个成功扫描的 skill 追加格式化的详细结果。
- `--save-raw [PATH]`：把同样的格式化详细结果保存到文本文件中；如果不传路径，默认保存到当前工作目录。

**功能示例**

扫描一个命名 skills 集合：

```bash
magicskills scanskills haystack_agent2_skills \
  --base-url http://localhost:8088 \
  --model qwen3-max \
  --api-key "$OPENAI_API_KEY" \
  --model-base-url "$OPENAI_BASE_URL"
```

在终端里显示每个 skill 的格式化详细结果：

```bash
magicskills scanskills haystack_agent2_skills --details
```

把格式化详细结果保存到当前目录：

```bash
magicskills scanskills haystack_agent2_skills --save-raw
```

把格式化详细结果保存到指定文件：

```bash
magicskills scanskills haystack_agent2_skills --save-raw ./reports/haystack-agent2-skills.txt
```

**输出行为**

- 默认只输出两个盒状区块：`Skills Summary` 和 `Skills Results`。
- `Skills Results` 故意保持简洁，每个 skill 只占一行摘要。
- `--details` 会继续追加每个成功扫描 skill 的格式化详细区块，风格与 `scanskill --details` 一致。
- `--save-raw` 会把与 `--details` 一致的格式化详细视图保存为纯文本文件，不依赖 `--details` 是否传入。
- `--save-raw` 这个参数名为了兼容性保留了下来，但现在保存的是格式化文本报告，不再是 JSON。

## 🤖 `skill-tool`

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

列出指定命名集合中的 skill：

```bash
magicskills skill-tool listskill --name coder
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
