# Cursor

## Cursor启动

## 安装magicskills

首先 `git clone https://github.com/Narwhal-Lab/MagicSkills.git`

并执行  `pip install -e .` 指令

![1](png/1.png)

本文的示例 skill 以 **`docx`** 为例


### 安装 skill(之前已经下载过的可以选择跳过)

执行 `magicskills install anthropics/skills -t ~/allskills`

(笔者在 Claude Code教程上安装过，故次跳过)

### 创建skills

执行 `magicskills createskills cursor --skill-list docx --agent-md-path ./AGENTS.md`

### 生成 AGETNS.md

执行 `magicskills syncskills cursor --output ./AGENTS.md -y` 指定输出AGENTS.md路径，不指定时候就默认用`createskills`指定的`--agent-md-path ./AGENTS.md`
此时AGENTS.md会出现如下内容

```markdown
# AGENTS

<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively.

How to use skills:
Unified skill cli. If you are not sure, you can first use "magicskills listskill" to search for available skills. Then, determine which skill might be the most useful. After that, try to use "magicskills readskill <path>" to read the SKILL.md file under this skill path to get more detailed information. Finally, based on the content of this file, decide whether to read the documentation in other paths or use "magicskills execskill <command>" to directly execute the relevant script.

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
</usage>

<available_skills>

<skill>
<name>docx</name>
<description>Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a 'report', 'memo', 'letter', 'template', or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation.</description>
<path>C:\Users\13978\allskills\docx</path>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>

```



### 使用

输入：请你阅读当前目录下的AGENTS.md文件，生成一份你的自我介绍，保存在 .docx 文档中

### 结果如下

```bash
请你阅读当前目录下的AGENTS.md文件，生成一份你的自我介绍，保存在 .docx 文档中

create_self_intro.js

const fs = require("fs");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  AlignmentType,
} = require("docx");

const doc = new Document({
  styles: {
    default: {
      document: {
        run: {
          font: "Arial",
          size: 24, // 12pt
        },
      },
    },
  },
  sections: [
    {
      properties: {
        page: {
          size: {
            width: 11906, // A4 width in DXA
            height: 16838, // A4 height in DXA
          },
          margin: {
            top: 1440,
            right: 1440,
            bottom: 1440,
            left: 1440,
          },
        },
      },
      children: [
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({
              text: "智能助理自我介绍",
              bold: true,
            }),
          ],
        }),
        new Paragraph({
          spacing: { before: 240, after: 240 },
          children: [
            new TextRun(
              "您好！我是运行在 Cursor 开发环境中的智能编码助理，专门帮助您在本项目中高效完成各类开发与文档相关工作。"
            ),
          ],
        }),
        new Paragraph({
          spacing: { before: 120, after: 120 },
          children: [
            new TextRun({
              text: "角色与定位",
              bold: true,
            }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun(
              "我通过 `AGENTS.md` 中定义的技能系统进行工作，会在处理任务前自动检查可用技能，并在需要操作 Word（.docx）文档时，调用专门的 docx 能力，为您生成或修改专业排版的文档。"
            ),
          ],
        }),
        new Paragraph({
          spacing: { before: 120, after: 120 },
          children: [
            new TextRun({
              text: "核心能力简介",
              bold: true,
            }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun(
              "1. 代码助理：理解和编写多种编程语言代码，协助调试、重构与性能优化，并结合项目现有约定进行修改。"
            ),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun(
              "2. 文档助理：根据您的需求，将内容整理为结构清晰、排版规范的 .docx 文档，例如报告、说明书、自我介绍等。"
            ),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun(
              "3. 技能编排：根据 `AGENTS.md` 中的说明，优先复用和调用已经存在的技能（例如 docx 技能），而不是重复造轮子。"
            ),
          ],
        }),
        new Paragraph({
          spacing: { before: 120, after: 120 },
          children: [
            new TextRun({
              text: "工作方式",
              bold: true,
            }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun(
              "在处理您的每个请求时，我会先阅读相关配置与文件，理解当前目录与技能系统的约束；在需要生成或操作 Word 文档时，则依托 docx 能力自动完成文档创建与格式控制，尽量减少您手动排版的时间。"
            ),
          ],
        }),
        new Paragraph({
          spacing: { before: 120, after: 120 },
          children: [
            new TextRun({
              text: "与您的协作期待",
              bold: true,
            }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun(
              "欢迎您用自然语言描述想要的效果（例如“生成一份项目说明的 Word 文档”），我会结合当前项目的 AGENTS 配置与文档技能，为您产出尽可能专业、易于后续编辑的 .docx 文件。"
            ),
          ],
        }),
      ],
    },
  ],
});

Packer.toBuffer(doc)
  .then((buffer) => {
    fs.writeFileSync("self_intro.docx", buffer);
    console.log("self_intro.docx 已生成。");
  })
  .catch((error) => {
    console.error("生成 self_intro.docx 时出错：", error);
    process.exitCode = 1;
  });



npm install docx

added 22 packages in 4s

1 package is looking for funding
  run `npm fund` for details

node create_self_intro.js
self_intro.docx 已生成。

### 自我介绍文档已生成

我已经根据当前目录下的 `AGENTS.md` 内容，在 `Cursor_example` 目录中生成了一份包含我自我介绍的 **Word 文档**：

- **文件名**：`self_intro.docx`  
- **位置**：`D:\Python-learning\pythonProject\MagicSkills\Cursor_example\self_intro.docx`  

你现在可以直接在资源管理器中双击打开该 `.docx` 文件查看和进一步编辑。
```






## 如果agent应用本身支持skill技能
你只需要将skill下载到该agent寻找skill的路径也可以