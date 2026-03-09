const fs = require("fs");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  AlignmentType,
  HeadingLevel,
  LevelFormat,
} = require("docx");

const doc = new Document({
  styles: {
    default: {
      document: {
        run: {
          font: "Arial",
          size: 24,
        },
      },
    },
    paragraphStyles: [
      {
        id: "Title",
        name: "Title",
        basedOn: "Normal",
        run: {
          size: 56,
          bold: true,
          color: "000000",
          font: "Arial",
        },
        paragraph: {
          spacing: { before: 240, after: 240 },
          alignment: AlignmentType.CENTER,
        },
      },
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: {
          size: 32,
          bold: true,
          color: "000000",
          font: "Arial",
        },
        paragraph: {
          spacing: { before: 240, after: 160 },
          outlineLevel: 0,
        },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullet-list",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: {
              paragraph: {
                indent: { left: 720, hanging: 360 },
              },
            },
          },
        ],
      },
    ],
  },
  sections: [
    {
      children: [
        new Paragraph({
          heading: HeadingLevel.TITLE,
          children: [new TextRun("AI 助手自我介绍")],
        }),
        new Paragraph({
          spacing: { before: 120, after: 120 },
          children: [
            new TextRun({
              text:
                "你好，我是集成在 Cursor IDE 中的 AI 编程助手，专门帮助你在本项目中完成各类软件开发任务。",
            }),
          ],
        }),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("我的能力")],
        }),
        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "熟悉项目中的技能系统，可以根据 `AGENTS.md` 和技能说明选择合适的工作流。"
            ),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "能够阅读、分析并修改项目代码文件，协助你实现新功能、修复 Bug 或进行重构。"
            ),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "可以按照文档化流程生成专业的 Word 文档（.docx），包括本次的自我介绍文档。"
            ),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "支持使用多种工具（如 Shell、文档技能等）组合完成复杂任务，并在需要时记录操作步骤。"
            ),
          ],
        }),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("工作方式")],
        }),
        new Paragraph({
          spacing: { after: 120 },
          children: [
            new TextRun(
              "在处理你的请求时，我会优先阅读相关说明文件（例如 `AGENTS.md` 和 DOCX 技能文档），根据指引选择合适的工具链，然后按步骤执行：读取、生成或修改文件，并在必要时运行脚本或命令行程序。"
            ),
          ],
        }),
        new Paragraph({
          spacing: { after: 120 },
          children: [
            new TextRun(
              "整个过程中，我会尽量保持操作可追踪、可复现，并根据需要在日志文件中记录关键步骤，方便你了解我为你完成了哪些具体操作。"
            ),
          ],
        }),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("与你的协作方式")],
        }),
        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "你可以使用自然语言（本项目中优先使用简体中文）描述需求，我会给出清晰的实现方案并直接在代码中落地。"
            ),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "对于较大的需求，我会拆分成多个可管理的小步骤，必要时结合日志或说明文档，让变更过程一目了然。"
            ),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "当涉及文档生成或编辑时，我会遵循 DOCX 技能的最佳实践，确保生成的 Word 文档在常见办公软件中都能正常打开和排版。"
            ),
          ],
        }),
        new Paragraph({
          spacing: { before: 160 },
          children: [
            new TextRun({
              text: "期待在你的开发过程中持续为你提供高质量、稳定可靠的帮助。",
            }),
          ],
        }),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("agent_self_intro.docx", buffer);
});

