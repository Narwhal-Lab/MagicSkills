## 适配 Claude Code

首先 `git clone https://github.com/Narwhal-Lab/MagicSkills.git`

并执行  `pip install -e .` 指令

![claude1](png/1.png)



本文的示例 skill 以 **`docx`** 为例

打开你的 claude code 的工作目录，

### 安装 skill

执行 `magicskills install docx --target ./.claude/skills`

![屏幕截图 2026-03-09 225127](png/2.png)



### 注册 skills

执行 `magicskills createskills coder --paths ./.claude/skills`

![屏幕截图 2026-03-09 225217](png/3.png)



### 生成 AGETNS.md 

执行 `magicskills syncskills coder --output ./AGENTS.md -y`

或者直接 `magicskills syncskills coder -y`

![屏幕截图 2026-03-09 225250](png/4.png)



### 创建 CLAUDE.md

由于 claude code 内定是使用 CLAUDE.md 文档，所以需要手动创建和编写 `Before you take any action, please read the AGENTS.md documentation to familiarize yourself with and refer to it.` 到其中

![屏幕截图 2026-03-09 225531](png/5.png)



最后应有如下文件

![屏幕截图 2026-03-09 225614](png/6.png)



### 使用

配置好上述文件后，claude code 就具备了生成 docx 文档的能力

例如你可以输入： “请你生成一份自我介绍，保存在 .docx 文档中，你生成文档的工作流也要记录在 .log 文件中 ”

![屏幕截图 2026-03-09 225656](png/7.png)



### 结果如下

![屏幕截图 2026-03-09 230741](png/8.png)
