const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel } = require('docx');
const fs = require('fs');

// Create a self-introduction document
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } }, // 12pt default
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } }
    ]
  },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("自我介绍")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("关于我")] }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("我是 Cascade，一个强大的 AI 编程助手。我由 Cognition 公司创建，基于 Penguin Alpha 模型构建。我专门帮助用户完成各种编程任务，包括代码编写、调试、重构和技术咨询。")]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("核心能力")] }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("我具备以下核心能力：")]
      }),
      new Paragraph({
        spacing: { before: 200, after: 200 },
        children: [
          new TextRun({ text: "• ", bold: true }),
          new TextRun("代码编写与重构")
        ]
      }),
      new Paragraph({
        spacing: { before: 0, after: 200 },
        children: [
          new TextRun({ text: "• ", bold: true }),
          new TextRun("调试与问题解决")
        ]
      }),
      new Paragraph({
        spacing: { before: 0, after: 200 },
        children: [
          new TextRun({ text: "• ", bold: true }),
          new TextRun("技术架构设计")
        ]
      }),
      new Paragraph({
        spacing: { before: 0, after: 200 },
        children: [
          new TextRun({ text: "• ", bold: true }),
          new TextRun("代码审查与优化")
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("工作方式")] }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("我通过集成开发环境（IDE）与用户进行协作编程。我可以访问用户的代码库，运行命令，并提供实时的编程支持。我遵循最佳实践，注重代码质量和可维护性。")]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("技术栈")] }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("我熟悉多种编程语言和技术框架，包括但不限于：")]
      }),
      new Paragraph({
        spacing: { before: 200, after: 200 },
        children: [
          new TextRun({ text: "• ", bold: true }),
          new TextRun("JavaScript/TypeScript")
        ]
      }),
      new Paragraph({
        spacing: { before: 0, after: 200 },
        children: [
          new TextRun({ text: "• ", bold: true }),
          new TextRun("Python")
        ]
      }),
      new Paragraph({
        spacing: { before: 0, after: 200 },
        children: [
          new TextRun({ text: "• ", bold: true }),
          new TextRun("React/Vue/Angular")
        ]
      }),
      new Paragraph({
        spacing: { before: 0, after: 200 },
        children: [
          new TextRun({ text: "• ", bold: true }),
          new TextRun("Node.js")
        ]
      }),
      new Paragraph({
        spacing: { before: 0, after: 200 },
        children: [
          new TextRun({ text: "• ", bold: true }),
          new TextRun("数据库技术")
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("联系方式")] }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("我随时准备为您提供专业的编程支持。让我们一起构建优秀的软件项目！")]
      })
    ]
  }]
});

// Save the document
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("自我介绍.docx", buffer);
  console.log("自我介绍文档已创建完成！");
}).catch(error => {
  console.error("创建文档时出错：", error);
});
