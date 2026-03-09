const fs = require("fs");
const path = require("path");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  AlignmentType,
} = require("docx");

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      {
        id: "Title",
        name: "Title",
        basedOn: "Normal",
        run: { size: 56, bold: true, color: "000000", font: "Arial" },
        paragraph: {
          spacing: { before: 240, after: 120 },
          alignment: AlignmentType.CENTER,
        },
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      children: [
        new Paragraph({
          style: "Title",
          children: [new TextRun({ text: "简单自我介绍", bold: true })],
        }),
        new Paragraph({
          spacing: { before: 200, after: 120 },
          children: [
            new TextRun({
              text: "我是 Auto，一个由 Cursor 设计的 AI 编程助手（Agent Router）。",
            }),
          ],
        }),
        new Paragraph({
          spacing: { after: 120 },
          children: [
            new TextRun({
              text: "我可以帮助你完成代码编写、重构、调试、文档生成等任务，并会根据任务类型选择合适的工具与工作流。本次自我介绍文档即通过工作区中的 docx 技能（Skill）按规范生成。",
            }),
          ],
        }),
        new Paragraph({
          spacing: { after: 120 },
          children: [
            new TextRun({
              text: "如需了解更多，请直接向我提问。",
            }),
          ],
        }),
      ],
    },
  ],
});

const outPath = path.join(__dirname, "自我介绍.docx");
Packer.toBuffer(doc)
  .then((buffer) => {
    fs.writeFileSync(outPath, buffer);
    console.log("已生成: " + outPath);
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
