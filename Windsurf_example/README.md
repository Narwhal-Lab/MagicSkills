## 适配 Windsurf

首先 `git clone https://github.com/Narwhal-Lab/MagicSkills.git`

并执行  `pip install -e .` 指令

![1](png/1.png)



本文的示例 skill 以 **`docx`** 为例

打开你的 Windsurf 的工作目录，

### 安装 skill

执行 `magicskills install docx --target ./.agent/skills`

![屏幕截图 2026-03-10 002623](png/2.png)



### 注册 skills

执行 `magicskills createskills windsurf --paths ./.agent/skills`

![屏幕截图 2026-03-10 002721](png/3.png)



### 生成 AGETNS.md

执行 `magicskills syncskills windsurf --output ./AGENTS.md -y`

或者直接 `magicskills syncskills windsurf -y`

![屏幕截图 2026-03-10 002752](png/4.png)



最后应有如下文件

![屏幕截图 2026-03-10 002900](png/5.png)



### 使用

配置好上述文件后，windsurf 就具备了生成 docx 文档的能力

例如你可以输入 ： “请你读取当前目录下的AGENTS.md，生成一份自我介绍，保存在 .docx 文档中，你生成文档的工作流也要记录在 .log 文件中  ”

![屏幕截图 2026-03-10 003010](png/6.png)



### 结果如下

![屏幕截图 2026-03-10 003224](png/7.png)
