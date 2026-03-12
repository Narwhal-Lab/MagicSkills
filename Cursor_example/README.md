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



## skill-tool的使用

```bash
请你生成一份自我介绍，将结果保存在 .docx 文档中，这个任务要求你阅读 AGETNS.md 文件，使用其中的 docx 技能。你必须在Mcp的conda环境下使用 magicskills skill-tool <action> --arg "<arg>" --name cursor 指令来帮助你完成任务（其中<action>必须使用 listskill 、readskill、execskill这三个行为，其中readskill的使用示例为设置utf-8并执行“magicskills skill-tool readskill --name cursor --arg "<path>"）

我会先读取 Cursor_example/AGENTS.md 里关于可用技能与用法的要求，然后在 MCP 的 conda 环境里按你指定的 magicskills skill-tool listskill/readskill/execskill --name cursor 流程调用 docx 技能，最后生成一份中文自我介绍并保存为 .docx 文件到你的工作区。

接下来我会按 AGENTS.md 的流程：先列出可用技能确认 docx，再读取 docx 的 SKILL.md 用法，最后用它生成并写出你的自我介绍 .docx 文档。

我这边发现当前 PowerShell 找不到 magicskills（不在 PATH/未激活对应 conda 环境）。我先检查本机已有的 conda 环境与 magicskills 安装位置，然后用 conda run 在你说的 MCP conda 环境里执行同样的 skill-tool 指令。

conda info --envs

# conda environments:
#
base                 * D:\Anaconda
Mcp                    D:\Anaconda\envs\Mcp
limu                   D:\Anaconda\envs\limu
shywenc                D:\Anaconda\envs\shywenc

conda run -n Mcp python -c "import sys; print(sys.executable)"
D:\Anaconda\envs\Mcp\python.exe

conda run -n Mcp python -c "import shutil; print(shutil.which('magicskills'))"
D:\Anaconda\envs\Mcp\Scripts\magicskills.EXE

conda run -n Mcp magicskills skill-tool listskill --name cursor --arg ""
usage: magicskills skill-tool [-h] [--arg ARG] [--name NAME] action
magicskills skill-tool: error: argument --arg: expected one argument

ERROR conda.cli.main_run:execute(125): `conda run magicskills skill-tool listskill --name cursor --arg` failed. (See above for error)
conda run -n Mcp magicskills skill-tool listskill --name cursor --arg "-"
{
  "ok": true,
  "action": "listskill",
  "result": "1. name: docx\n   description: Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a 'report', 'memo', 'letter', 'template', or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation.\n   path: C:\\Users\\13978\\allskills\\docx\\SKILL.md"
}

已确认 docx 技能存在且位于 C:\\Users\\13978\\allskills\\docx\\SKILL.md。接下来我会按你要求先用 readskill 读取该技能说明（用 utf-8），再根据说明用 execskill 生成并保存自我介绍 .docx。

chcp 65001 > $null; conda run -n Mcp magicskills skill-tool readskill --name cursor --arg "C:\Users\13978\allskills\docx\SKILL.md"
{
  "ok": true,
  "action": "readskill",
  "result": "---\nname: docx\ndescription: \"Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a 'report', 'memo', 'letter', 'template', or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation.\"\nlicense: Proprietary. LICENSE.txt has complete terms\n---\n\n# DOCX creation, editing, and analysis\n\n## Overview\n\nA .docx file is a ZIP archive containing XML files.\n\n## Quick Reference\n\n| Task | Approach |\n|------|----------|\n| Read/analyze content | `pandoc` or unpack for raw XML |\n| Create new document | Use `docx-js` - see Creating New Documents below |\n| Edit existing document | Unpack 鈫� edit XML 鈫� repack - see Editing Existing Documents below |\n\n### Converting .doc to .docx\n\nLegacy `.doc` files must be converted before editing:\n\n```bash\npython scripts/office/soffice.py --headless --convert-to docx document.doc\n```\n\n### Reading Content\n\n```bash\n# Text extraction with tracked changes\npandoc --track-changes=all document.docx -o output.md\n\n# Raw XML access\npython scripts/office/unpack.py document.docx unpacked/\n```\n\n### Converting to Images\n\n```bash\npython scripts/office/soffice.py --headless --convert-to pdf document.docx\npdftoppm -jpeg -r 150 document.pdf page\n```\n\n### Accepting Tracked Changes\n\nTo produce a clean document with all tracked changes accepted (requires LibreOffice):\n\n```bash\npython scripts/accept_changes.py input.docx output.docx\n```\n\n---\n\n## Creating New Documents\n\nGenerate .docx files with JavaScript, then validate. Install: `npm install -g docx`\n\n### Setup\n```javascript\nconst { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,\n        Header, Footer, AlignmentType, PageOrientation, LevelFormat, ExternalHyperlink,\n        InternalHyperlink, Bookmark, FootnoteReferenceRun, PositionalTab,\n        PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader,\n        TabStopType, TabStopPosition, Column, SectionType,\n        TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,\n        VerticalAlign, PageNumber, PageBreak } = require('docx');\n\nconst doc = new Document({ sections: [{ children: [/* content */] }] });\nPacker.toBuffer(doc).then(buffer => fs.writeFileSync(\"doc.docx\", buffer));\n```\n\n### Validation\nAfter creating the file, validate it. If validation fails, unpack, fix the XML, and repack.\n```bash\npython scripts/office/validate.py doc.docx\n```\n\n### Page Size\n\n```javascript\n// CRITICAL: docx-js defaults to A4, not US Letter\n// Always set page size explicitly for consistent results\nsections: [{\n  properties: {\n    page: {\n      size: {\n        width: 12240,   // 8.5 inches in DXA\n        height: 15840   // 11 inches in DXA\n      },\n      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1 inch margins\n    }\n  },\n  children: [/* content */]\n}]\n```\n\n**Common page sizes (DXA units, 1440 DXA = 1 inch):**\n\n| Paper | Width | Height | Content Width (1\" margins) |\n|-------|-------|--------|---------------------------|\n| US Letter | 12,240 | 15,840 | 9,360 |\n| A4 (default) | 11,906 | 16,838 | 9,026 |\n\n**Landscape orientation:** docx-js swaps width/height internally, so pass portrait dimensions and let it handle the swap:\n```javascript\nsize: {\n  width: 12240,   // Pass SHORT edge as width\n  height: 15840,  // Pass LONG edge as height\n  orientation: PageOrientation.LANDSCAPE  // docx-js swaps them in the XML\n},\n// Content width = 15840 - left margin - right margin (uses the long edge)\n```\n\n### Styles (Override Built-in Headings)\n\nUse Arial as the default font (universally supported). Keep titles black for readability.\n\n```javascript\nconst doc = new Document({\n  styles: {\n    default: { document: { run: { font: \"Arial\", size: 24 } } }, // 12pt default\n    paragraphStyles: [\n      // IMPORTANT: Use exact IDs to override built-in styles\n      { id: \"Heading1\", name: \"Heading 1\", basedOn: \"Normal\", next: \"Normal\", quickFormat: true,\n        run: { size: 32, bold: true, font: \"Arial\" },\n        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } }, // outlineLevel required for TOC\n      { id: \"Heading2\", name: \"Heading 2\", basedOn: \"Normal\", next: \"Normal\", quickFormat: true,\n        run: { size: 28, bold: true, font: \"Arial\" },\n        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },\n    ]\n  },\n  sections: [{\n    children: [\n      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(\"Title\")] }),\n    ]\n  }]\n});\n```\n\n### Lists (NEVER use unicode bullets)\n\n```javascript\n// 鉂� WRONG - never manually insert bullet characters\nnew Paragraph({ children: [new TextRun(\"鈥� Item\")] })  // BAD\nnew Paragraph({ children: [new TextRun(\"\\u2022 Item\")] })  // BAD\n\n// 鉁� CORRECT - use numbering config with LevelFormat.BULLET\nconst doc = new Document({\n  numbering: {\n    config: [\n      { reference: \"bullets\",\n        levels: [{ level: 0, format: LevelFormat.BULLET, text: \"鈥�\", alignment: AlignmentType.LEFT,\n          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },\n      { reference: \"numbers\",\n        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: \"%1.\", alignment: AlignmentType.LEFT,\n          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },\n    ]\n  },\n  sections: [{\n    children: [\n      new Paragraph({ numbering: { reference: \"bullets\", level: 0 },\n        children: [new TextRun(\"Bullet item\")] }),\n      new Paragraph({ numbering: { reference: \"numbers\", level: 0 },\n        children: [new TextRun(\"Numbered item\")] }),\n    ]\n  }]\n});\n\n// 鈿狅笍 Each reference creates INDEPENDENT numbering\n// Same reference = continues (1,2,3 then 4,5,6)\n// Different reference = restarts (1,2,3 then 1,2,3)\n```\n\n### Tables\n\n**CRITICAL: Tables need dual widths** - set both `columnWidths` on the table AND `width` on each cell. Without both, tables render incorrectly on some platforms.\n\n```javascript\n// CRITICAL: Always set table width for consistent rendering\n// CRITICAL: Use ShadingType.CLEAR (not SOLID) to prevent black backgrounds\nconst border = { style: BorderStyle.SINGLE, size: 1, color: \"CCCCCC\" };\nconst borders = { top: border, bottom: border, left: border, right: border };\n\nnew Table({\n  width: { size: 9360, type: WidthType.DXA }, // Always use DXA (percentages break in Google Docs)\n  columnWidths: [4680, 4680], // Must sum to table width (DXA: 1440 = 1 inch)\n  rows: [\n    new TableRow({\n      children: [\n        new TableCell({\n          borders,\n          width: { size: 4680, type: WidthType.DXA }, // Also set on each cell\n          shading: { fill: \"D5E8F0\", type: ShadingType.CLEAR }, // CLEAR not SOLID\n          margins: { top: 80, bottom: 80, left: 120, right: 120 }, // Cell padding (internal, not added to width)\n          children: [new Paragraph({ children: [new TextRun(\"Cell\")] })]\n        })\n      ]\n    })\n  ]\n})\n```\n\n**Table width calculation:**\n\nAlways use `WidthType.DXA` 鈥� `WidthType.PERCENTAGE` breaks in Google Docs.\n\n```javascript\n// Table width = sum of columnWidths = content width\n// US Letter with 1\" margins: 12240 - 2880 = 9360 DXA\nwidth: { size: 9360, type: WidthType.DXA },\ncolumnWidths: [7000, 2360]  // Must sum to table width\n```\n\n**Width rules:**\n- **Always use `WidthType.DXA`** 鈥� never `WidthType.PERCENTAGE` (incompatible with Google Docs)\n- Table width must equal the sum of `columnWidths`\n- Cell `width` must match corresponding `columnWidth`\n- Cell `margins` are internal padding - they reduce content area, not add to cell width\n- For full-width tables: use content width (page width minus left and right margins)\n\n### Images\n\n```javascript\n// CRITICAL: type parameter is REQUIRED\nnew Paragraph({\n  children: [new ImageRun({\n    type: \"png\", // Required: png, jpg, jpeg, gif, bmp, svg\n    data: fs.readFileSync(\"image.png\"),\n    transformation: { width: 200, height: 150 },\n    altText: { title: \"Title\", description: \"Desc\", name: \"Name\" } // All three required\n  })]\n})\n```\n\n### Page Breaks\n\n```javascript\n// CRITICAL: PageBreak must be inside a Paragraph\nnew Paragraph({ children: [new PageBreak()] })\n\n// Or use pageBreakBefore\nnew Paragraph({ pageBreakBefore: true, children: [new TextRun(\"New page\")] })\n```\n\n### Hyperlinks\n\n```javascript\n// External link\nnew Paragraph({\n  children: [new ExternalHyperlink({\n    children: [new TextRun({ text: \"Click here\", style: \"Hyperlink\" })],\n    link: \"https://example.com\",\n  })]\n})\n\n// Internal link (bookmark + reference)\n// 1. Create bookmark at destination\nnew Paragraph({ heading: HeadingLevel.HEADING_1, children: [\n  new Bookmark({ id: \"chapter1\", children: [new TextRun(\"Chapter 1\")] }),\n]})\n// 2. Link to it\nnew Paragraph({ children: [new InternalHyperlink({\n  children: [new TextRun({ text: \"See Chapter 1\", style: \"Hyperlink\" })],\n  anchor: \"chapter1\",\n})]})\n```\n\n### Footnotes\n\n```javascript\nconst doc = new Document({\n  footnotes: {\n    1: { children: [new Paragraph(\"Source: Annual Report 2024\")] },\n    2: { children: [new Paragraph(\"See appendix for methodology\")] },\n  },\n  sections: [{\n    children: [new Paragraph({\n      children: [\n        new TextRun(\"Revenue grew 15%\"),\n        new FootnoteReferenceRun(1),\n        new TextRun(\" using adjusted metrics\"),\n        new FootnoteReferenceRun(2),\n      ],\n    })]\n  }]\n});\n```\n\n### Tab Stops\n\n```javascript\n// Right-align text on same line (e.g., date opposite a title)\nnew Paragraph({\n  children: [\n    new TextRun(\"Company Name\"),\n    new TextRun(\"\\tJanuary 2025\"),\n  ],\n  tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],\n})\n\n// Dot leader (e.g., TOC-style)\nnew Paragraph({\n  children: [\n    new TextRun(\"Introduction\"),\n    new TextRun({ children: [\n      new PositionalTab({\n        alignment: PositionalTabAlignment.RIGHT,\n        relativeTo: PositionalTabRelativeTo.MARGIN,\n        leader: PositionalTabLeader.DOT,\n      }),\n      \"3\",\n    ]}),\n  ],\n})\n```\n\n### Multi-Column Layouts\n\n```javascript\n// Equal-width columns\nsections: [{\n  properties: {\n    column: {\n      count: 2,          // number of columns\n      space: 720,        // gap between columns in DXA (720 = 0.5 inch)\n      equalWidth: true,\n      separate: true,    // vertical line between columns\n    },\n  },\n  children: [/* content flows naturally across columns */]\n}]\n\n// Custom-width columns (equalWidth must be false)\nsections: [{\n  properties: {\n    column: {\n      equalWidth: false,\n      children: [\n        new Column({ width: 5400, space: 720 }),\n        new Column({ width: 3240 }),\n      ],\n    },\n  },\n  children: [/* content */]\n}]\n```\n\nForce a column break with a new section using `type: SectionType.NEXT_COLUMN`.\n\n### Table of Contents\n\n```javascript\n// CRITICAL: Headings must use HeadingLevel ONLY - no custom styles\nnew TableOfContents(\"Table of Contents\", { hyperlink: true, headingStyleRange: \"1-3\" })\n```\n\n### Headers/Footers\n\n```javascript\nsections: [{\n  properties: {\n    page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } // 1440 = 1 inch\n  },\n  headers: {\n    default: new Header({ children: [new Paragraph({ children: [new TextRun(\"Header\")] })] })\n  },\n  footers: {\n    default: new Footer({ children: [new Paragraph({\n      children: [new TextRun(\"Page \"), new TextRun({ children: [PageNumber.CURRENT] })]\n    })] })\n  },\n  children: [/* content */]\n}]\n```\n\n### Critical Rules for docx-js\n\n- **Set page size explicitly** - docx-js defaults to A4; use US Letter (12240 x 15840 DXA) for US documents\n- **Landscape: pass portrait dimensions** - docx-js swaps width/height internally; pass short edge as `width`, long edge as `height`, and set `orientation: PageOrientation.LANDSCAPE`\n- **Never use `\\n`** - use separate Paragraph elements\n- **Never use unicode bullets** - use `LevelFormat.BULLET` with numbering config\n- **PageBreak must be in Paragraph** - standalone creates invalid XML\n- **ImageRun requires `type`** - always specify png/jpg/etc\n- **Always set table `width` with DXA** - never use `WidthType.PERCENTAGE` (breaks in Google Docs)\n- **Tables need dual widths** - `columnWidths` array AND cell `width`, both must match\n- **Table width = sum of columnWidths** - for DXA, ensure they add up exactly\n- **Always add cell margins** - use `margins: { top: 80, bottom: 80, left: 120, right: 120 }` for readable padding\n- **Use `ShadingType.CLEAR`** - never SOLID for table shading\n- **Never use tables as dividers/rules** - cells have minimum height and render as empty boxes (including in headers/footers); use `border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: \"2E75B6\", space: 1 } }` on a Paragraph instead. For two-column footers, use tab stops (see Tab Stops section), not tables\n- **TOC requires HeadingLevel only** - no custom styles on heading paragraphs\n- **Override built-in styles** - use exact IDs: \"Heading1\", \"Heading2\", etc.\n- **Include `outlineLevel`** - required for TOC (0 for H1, 1 for H2, etc.)\n\n---\n\n## Editing Existing Documents\n\n**Follow all 3 steps in order.**\n\n### Step 1: Unpack\n```bash\npython scripts/office/unpack.py document.docx unpacked/\n```\nExtracts XML, pretty-prints, merges adjacent runs, and converts smart quotes to XML entities (`&#x201C;` etc.) so they survive editing. Use `--merge-runs false` to skip run merging.\n\n### Step 2: Edit XML\n\nEdit files in `unpacked/word/`. See XML Reference below for patterns.\n\n**Use \"Claude\" as the author** for tracked changes and comments, unless the user explicitly requests use of a different name.\n\n**Use the Edit tool directly for string replacement. Do not write Python scripts.** Scripts introduce unnecessary complexity. The Edit tool shows exactly what is being replaced.\n\n**CRITICAL: Use smart quotes for new content.** When adding text with apostrophes or quotes, use XML entities to produce smart quotes:\n```xml\n<!-- Use these entities for professional typography -->\n<w:t>Here&#x2019;s a quote: &#x201C;Hello&#x201D;</w:t>\n```\n| Entity | Character |\n|--------|-----------|\n| `&#x2018;` | 鈥� (left single) |\n| `&#x2019;` | 鈥� (right single / apostrophe) |\n| `&#x201C;` | 鈥� (left double) |\n| `&#x201D;` | 鈥� (right double) |\n\n**Adding comments:** Use `comment.py` to handle boilerplate across multiple XML files (text must be pre-escaped XML):\n```bash\npython scripts/comment.py unpacked/ 0 \"Comment text with &amp; and &#x2019;\"\npython scripts/comment.py unpacked/ 1 \"Reply text\" --parent 0  # reply to comment 0\npython scripts/comment.py unpacked/ 0 \"Text\" --author \"Custom Author\"  # custom author name\n```\nThen add markers to document.xml (see Comments in XML Reference).\n\n### Step 3: Pack\n```bash\npython scripts/office/pack.py unpacked/ output.docx --original document.docx\n```\nValidates with auto-repair, condenses XML, and creates DOCX. Use `--validate false` to skip.\n\n**Auto-repair will fix:**\n- `durableId` >= 0x7FFFFFFF (regenerates valid ID)\n- Missing `xml:space=\"preserve\"` on `<w:t>` with whitespace\n\n**Auto-repair won't fix:**\n- Malformed XML, invalid element nesting, missing relationships, schema violations\n\n### Common Pitfalls\n\n- **Replace entire `<w:r>` elements**: When adding tracked changes, replace the whole `<w:r>...</w:r>` block with `<w:del>...<w:ins>...` as siblings. Don't inject tracked change tags inside a run.\n- **Preserve `<w:rPr>` formatting**: Copy the original run's `<w:rPr>` block into your tracked change runs to maintain bold, font size, etc.\n\n---\n\n## XML Reference\n\n### Schema Compliance\n\n- **Element order in `<w:pPr>`**: `<w:pStyle>`, `<w:numPr>`, `<w:spacing>`, `<w:ind>`, `<w:jc>`, `<w:rPr>` last\n- **Whitespace**: Add `xml:space=\"preserve\"` to `<w:t>` with leading/trailing spaces\n- **RSIDs**: Must be 8-digit hex (e.g., `00AB1234`)\n\n### Tracked Changes\n\n**Insertion:**\n```xml\n<w:ins w:id=\"1\" w:author=\"Claude\" w:date=\"2025-01-01T00:00:00Z\">\n  <w:r><w:t>inserted text</w:t></w:r>\n</w:ins>\n```\n\n**Deletion:**\n```xml\n<w:del w:id=\"2\" w:author=\"Claude\" w:date=\"2025-01-01T00:00:00Z\">\n  <w:r><w:delText>deleted text</w:delText></w:r>\n</w:del>\n```\n\n**Inside `<w:del>`**: Use `<w:delText>` instead of `<w:t>`, and `<w:delInstrText>` instead of `<w:instrText>`.\n\n**Minimal edits** - only mark what changes:\n```xml\n<!-- Change \"30 days\" to \"60 days\" -->\n<w:r><w:t>The term is </w:t></w:r>\n<w:del w:id=\"1\" w:author=\"Claude\" w:date=\"...\">\n  <w:r><w:delText>30</w:delText></w:r>\n</w:del>\n<w:ins w:id=\"2\" w:author=\"Claude\" w:date=\"...\">\n  <w:r><w:t>60</w:t></w:r>\n</w:ins>\n<w:r><w:t> days.</w:t></w:r>\n```\n\n**Deleting entire paragraphs/list items** - when removing ALL content from a paragraph, also mark the paragraph mark as deleted so it merges with the next paragraph. Add `<w:del/>` inside `<w:pPr><w:rPr>`:\n```xml\n<w:p>\n  <w:pPr>\n    <w:numPr>...</w:numPr>  <!-- list numbering if present -->\n    <w:rPr>\n      <w:del w:id=\"1\" w:author=\"Claude\" w:date=\"2025-01-01T00:00:00Z\"/>\n    </w:rPr>\n  </w:pPr>\n  <w:del w:id=\"2\" w:author=\"Claude\" w:date=\"2025-01-01T00:00:00Z\">\n    <w:r><w:delText>Entire paragraph content being deleted...</w:delText></w:r>\n  </w:del>\n</w:p>\n```\nWithout the `<w:del/>` in `<w:pPr><w:rPr>`, accepting changes leaves an empty paragraph/list item.\n\n**Rejecting another author's insertion** - nest deletion inside their insertion:\n```xml\n<w:ins w:author=\"Jane\" w:id=\"5\">\n  <w:del w:author=\"Claude\" w:id=\"10\">\n    <w:r><w:delText>their inserted text</w:delText></w:r>\n  </w:del>\n</w:ins>\n```\n\n**Restoring another author's deletion** - add insertion after (don't modify their deletion):\n```xml\n<w:del w:author=\"Jane\" w:id=\"5\">\n  <w:r><w:delText>deleted text</w:delText></w:r>\n</w:del>\n<w:ins w:author=\"Claude\" w:id=\"10\">\n  <w:r><w:t>deleted text</w:t></w:r>\n</w:ins>\n```\n\n### Comments\n\nAfter running `comment.py` (see Step 2), add markers to document.xml. For replies, use `--parent` flag and nest markers inside the parent's.\n\n**CRITICAL: `<w:commentRangeStart>` and `<w:commentRangeEnd>` are siblings of `<w:r>`, never inside `<w:r>`.**\n\n```xml\n<!-- Comment markers are direct children of w:p, never inside w:r -->\n<w:commentRangeStart w:id=\"0\"/>\n<w:del w:id=\"1\" w:author=\"Claude\" w:date=\"2025-01-01T00:00:00Z\">\n  <w:r><w:delText>deleted</w:delText></w:r>\n</w:del>\n<w:r><w:t> more text</w:t></w:r>\n<w:commentRangeEnd w:id=\"0\"/>\n<w:r><w:rPr><w:rStyle w:val=\"CommentReference\"/></w:rPr><w:commentReference w:id=\"0\"/></w:r>\n\n<!-- Comment 0 with reply 1 nested inside -->\n<w:commentRangeStart w:id=\"0\"/>\n  <w:commentRangeStart w:id=\"1\"/>\n  <w:r><w:t>text</w:t></w:r>\n  <w:commentRangeEnd w:id=\"1\"/>\n<w:commentRangeEnd w:id=\"0\"/>\n<w:r><w:rPr><w:rStyle w:val=\"CommentReference\"/></w:rPr><w:commentReference w:id=\"0\"/></w:r>\n<w:r><w:rPr><w:rStyle w:val=\"CommentReference\"/></w:rPr><w:commentReference w:id=\"1\"/></w:r>\n```\n\n### Images\n\n1. Add image file to `word/media/`\n2. Add relationship to `word/_rels/document.xml.rels`:\n```xml\n<Relationship Id=\"rId5\" Type=\".../image\" Target=\"media/image1.png\"/>\n```\n3. Add content type to `[Content_Types].xml`:\n```xml\n<Default Extension=\"png\" ContentType=\"image/png\"/>\n```\n4. Reference in document.xml:\n```xml\n<w:drawing>\n  <wp:inline>\n    <wp:extent cx=\"914400\" cy=\"914400\"/>  <!-- EMUs: 914400 = 1 inch -->\n    <a:graphic>\n      <a:graphicData uri=\".../picture\">\n        <pic:pic>\n          <pic:blipFill><a:blip r:embed=\"rId5\"/></pic:blipFill>\n        </pic:pic>\n      </a:graphicData>\n    </a:graphic>\n  </wp:inline>\n</w:drawing>\n```\n\n---\n\n## Dependencies\n\n- **pandoc**: Text extraction\n- **docx**: `npm install -g docx` (new documents)\n- **LibreOffice**: PDF conversion (auto-configured for sandboxed environments via `scripts/office/soffice.py`)\n- **Poppler**: `pdftoppm` for images\n"
}

conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "python -V"
{
  "ok": true,
  "action": "execskill",
  "result": {
    "command": "python -V",
    "returncode": 0,
    "stdout": "Python 3.12.12\n",
    "stderr": ""
  }
}


conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "node -v"
{
  "ok": true,
  "action": "execskill",
  "result": {
    "command": "node -v",
    "returncode": 0,
    "stdout": "v24.11.1\n",
    "stderr": ""
  }
}

conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "node -e \"try{require('docx');console.log('docx ok')}catch(e){console.error('no docx')}\""
e : �޷�����e����ʶ��Ϊ cmdlet���������ű��ļ�������г�������ơ��������Ƶ�ƴд���������·������ȷ��·����ȷ��Ȼ������һ
�Ρ�
����λ�� C:\Users\13978\AppData\Local\Temp\ps-script-5a7948cf-b5f0-43eb-8fc1-8b77dde8e0d1.ps1:103 �ַ�: 131
+ ... "node -e \"try{require('docx');console.log('docx ok')}catch(e){consol ...
+                                                                 ~
    + CategoryInfo          : ObjectNotFound: (e:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
 
conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "node -e \"try{require('docx');console.log('docx ok')}catch(err){console.error('no docx')}\""
err : �޷�����err����ʶ��Ϊ cmdlet���������ű��ļ�������г�������ơ��������Ƶ�ƴд���������·������ȷ��·����ȷ��Ȼ����
��һ�Ρ�
����λ�� C:\Users\13978\AppData\Local\Temp\ps-script-edee963b-40df-44e0-82f2-bddf5258bf3d.ps1:103 �ַ�: 131
+ ... ode -e \"try{require('docx');console.log('docx ok')}catch(err){consol ...
+                                                               ~~~
    + CategoryInfo          : ObjectNotFound: (err:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
 
conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "node -p \"require.resolve('docx')\""
{
  "ok": true,
  "action": "execskill",
  "result": {
    "command": "node -p \" require.resolve docx \"",
    "returncode": 1,
    "stdout": "",
    "stderr": "[eval]:1\n require.resolve docx \n                 ^^^^\nExpected ';', '}' or <eof>\n\nSyntaxError: Unexpected identifier 'docx'\n    at makeContextifyScript (node:internal/vm:194:14)\n    at compileScript (node:internal/process/execution:388:10)\n    at evalTypeScript (node:internal/process/execution:260:22)\n    at node:internal/main/eval_string:71:3\n\nNode.js v24.11.1\n"
  }
}

我接下来会用最稳妥的方式：先在工作区写一个小的 Node 脚本来检测/生成 .docx（避免 PowerShell 引号转义问题），再通过 execskill 执行它，最终输出到 Cursor_example/自我介绍.docx。

generate_self_intro_docx.js
+164
const fs = require("fs");const path = require("path");async function main() {  const outPath = process.argv[2];  if (!outPath) {
conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "npm -v"
{
  "ok": true,
  "action": "execskill",
  "result": {
    "command": "npm -v",
    "returncode": 0,
    "stdout": "11.6.2\n",
    "stderr": ""
  }
}

conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "npm list -g --depth=0 docx"
{
  "ok": true,
  "action": "execskill",
  "result": {
    "command": "npm list -g --depth=0 docx",
    "returncode": 0,
    "stdout": "C:\\Users\\13978\\AppData\\Roaming\\npm\n`-- docx@9.6.1\n\n",
    "stderr": ""
  }
}

Add-Content : �����ɶ���
����λ�� C:\Users\13978\AppData\Local\Temp\ps-script-4f90dc06-abc8-4c52-8c64-83a5d6c118db.ps1:115 �ַ�: 9
+         Add-Content -Path $OutputFile -Value $Content -Encoding UTF8
+         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidArgument: (C:\Users\13978\...0ab9735b315.txt:String) [Add-Content]��ArgumentExcept
    ion
    + FullyQualifiedErrorId : GetContentWriterArgumentError,Microsoft.PowerShell.Commands.AddContentCommand
 
Add-Content : �����ɶ���
����λ�� C:\Users\13978\AppData\Local\Temp\ps-script-4f90dc06-abc8-4c52-8c64-83a5d6c118db.ps1:115 �ַ�: 9
+         Add-Content -Path $OutputFile -Value $Content -Encoding UTF8
+         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidArgument: (C:\Users\13978\...0ab9735b315.txt:String) [Add-Content]��ArgumentExcept
    ion
    + FullyQualifiedErrorId : GetContentWriterArgumentError,Microsoft.PowerShell.Commands.AddContentCommand
 
Add-Content : �����ɶ���
����λ�� C:\Users\13978\AppData\Local\Temp\ps-script-4f90dc06-abc8-4c52-8c64-83a5d6c118db.ps1:115 �ַ�: 9
+         Add-Content -Path $OutputFile -Value $Content -Encoding UTF8
+         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidArgument: (C:\Users\13978\...0ab9735b315.txt:String) [Add-Content]��ArgumentExcept
    ion
    + FullyQualifiedErrorId : GetContentWriterArgumentError,Microsoft.PowerShell.Commands.AddContentCommand
 
Add-Content : �����ɶ���
����λ�� C:\Users\13978\AppData\Local\Temp\ps-script-4f90dc06-abc8-4c52-8c64-83a5d6c118db.ps1:115 �ַ�: 9
+         Add-Content -Path $OutputFile -Value $Content -Encoding UTF8
+         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidArgument: (C:\Users\13978\...0ab9735b315.txt:String) [Add-Content]��ArgumentExcept
    ion
    + FullyQualifiedErrorId : GetContentWriterArgumentError,Microsoft.PowerShell.Commands.AddContentCommand
 
conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "node \"d:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\generate_self_intro_docx.js\" \"d:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\自我介绍.docx\""
{
  "ok": true,
  "action": "execskill",
  "result": {
    "command": "node \" d:\\\\Python-learning\\\\pythonProject\\\\MagicSkills\\\\Cursor_example\\\\generate_self_intro_docx.js\" \\d:\\\\Python-learning\\\\pythonProject\\\\MagicSkills\\\\Cursor_example\\\\鑷�鎴戜粙缁�.docx\"",
    "returncode": 1,
    "stdout": "",
    "stderr": "node:internal/modules/cjs/loader:1424\n  throw err;\n  ^\n\nError: Cannot find module 'D:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\ d:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\generate_self_intro_docx.js'\n    at Module._resolveFilename (node:internal/modules/cjs/loader:1421:15)\n    at defaultResolveImpl (node:internal/modules/cjs/loader:1059:19)\n    at resolveForCJSWithHooks (node:internal/modules/cjs/loader:1064:22)\n    at Module._load (node:internal/modules/cjs/loader:1227:37)\n    at TracingChannel.traceSync (node:diagnostics_channel:328:14)\n    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)\n    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)\n    at node:internal/main/run_main_module:33:47 {\n  code: 'MODULE_NOT_FOUND',\n  requireStack: []\n}\n\nNode.js v24.11.1\n"
  }
}

conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "powershell -NoProfile -Command \"& { node 'd:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\generate_self_intro_docx.js' 'd:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\self_introduction.docx' }\""
����λ�� C:\Users\13978\AppData\Local\Temp\ps-script-e96351fa-640d-4a34-9985-6d52f09053ae.ps1:103 �ַ�: 105
+ ... skill --name cursor --arg "powershell -NoProfile -Command \"& { node  ...
+                                                                 ~
������ʹ�����(&)��& �������Ϊ����ʹ�ö������ģ�����˫���Ž����������("&")���Խ�����Ϊ�ַ�����һ���ִ��ݡ�
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : AmpersandNotAllowed
 
conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "cmd /c node d:\Python-learning\pythonProject\MagicSkills\Cursor_example\generate_self_intro_docx.js d:\Python-learning\pythonProject\MagicSkills\Cursor_example\self_introduction.docx"
{
  "ok": true,
  "action": "execskill",
  "result": {
    "command": "cmd /c node d:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\generate_self_intro_docx.js d:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\self_introduction.docx",
    "returncode": 3,
    "stdout": "",
    "stderr": "Missing npm package 'docx'. Install it with: npm install -g docx (or add it to the project).\n"
  }
}

conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "cmd /c cd /d d:\Python-learning\pythonProject\MagicSkills\Cursor_example && npm init -y"
{
  "ok": true,
  "action": "execskill",
  "result": {
    "command": "cmd /c cd /d d:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example && npm init -y",
    "returncode": 0,
    "stdout": "Wrote to D:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\package.json:\n\n{\n  \"name\": \"cursor_example\",\n  \"version\": \"1.0.0\",\n  \"description\": \"\",\n  \"main\": \"generate_self_intro_docx.js\",\n  \"scripts\": {\n    \"test\": \"echo \\\"Error: no test specified\\\" && exit 1\"\n  },\n  \"keywords\": [],\n  \"author\": \"\",\n  \"license\": \"ISC\",\n  \"type\": \"commonjs\"\n}\n\n\n\n",
    "stderr": ""
  }
}

conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "cmd /c cd /d d:\Python-learning\pythonProject\MagicSkills\Cursor_example && npm install docx"
{
  "ok": true,
  "action": "execskill",
  "result": {
    "command": "cmd /c cd /d d:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example && npm install docx",
    "returncode": 0,
    "stdout": "\nadded 22 packages, and audited 23 packages in 2s\n\n1 package is looking for funding\n  run `npm fund` for details\n\nfound 0 vulnerabilities\n",
    "stderr": ""
  }
}

conda run -n Mcp magicskills skill-tool execskill --name cursor --arg "cmd /c node d:\Python-learning\pythonProject\MagicSkills\Cursor_example\generate_self_intro_docx.js d:\Python-learning\pythonProject\MagicSkills\Cursor_example\self_introduction.docx"
{
  "ok": true,
  "action": "execskill",
  "result": {
    "command": "cmd /c node d:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\generate_self_intro_docx.js d:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\self_introduction.docx",
    "returncode": 0,
    "stdout": "Wrote: d:\\Python-learning\\pythonProject\\MagicSkills\\Cursor_example\\self_introduction.docx\n",
    "stderr": ""
  }
}

powershell -NoProfile -Command "Test-Path 'd:\Python-learning\pythonProject\MagicSkills\Cursor_example\self_introduction.docx'"
True
已生成并保存的 .docx 文件
输出文件：d:\Python-learning\pythonProject\MagicSkills\Cursor_example\self_introduction.docx
完成方式：已按 Cursor_example/AGENTS.md 要求使用 docx 技能流程，并在 MCP conda 环境（Mcp） 下通过
magicskills skill-tool listskill/readskill/execskill --name cursor --arg "<...>" 执行生成。
相关生成脚本与依赖
生成脚本：Cursor_example/generate_self_intro_docx.js
本地依赖：已在 Cursor_example/ 下安装 docx（用于 Node 生成 .docx
```

