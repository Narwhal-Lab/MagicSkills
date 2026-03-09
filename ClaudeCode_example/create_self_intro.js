const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat,
        HeadingLevel, BorderStyle, WidthType, ShadingType, VerticalAlign,
        PageNumber } = require('docx');
const fs = require('fs');

// 创建文档
const doc = new Document({
  styles: {
    default: {
      document: {
        run: {
          font: "Arial",
          size: 24 // 12pt default (24 = 12pt * 2)
        }
      }
    },
    paragraphStyles: [
      // 文档标题样式 - 覆盖内置的 Title 样式
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },

      // 覆盖内置标题样式
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "000000", font: "Arial" }, // 16pt
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },

      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "000000", font: "Arial" }, // 14pt
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },

      // 自定义样式
      { id: "Subtitle", name: "Subtitle", basedOn: "Normal",
        run: { size: 26, bold: false, color: "333333", font: "Arial" }, // 13pt
        paragraph: { spacing: { before: 120, after: 120 }, alignment: AlignmentType.CENTER } },

      { id: "Highlight", name: "Highlight", basedOn: "Normal",
        run: { size: 24, bold: true, color: "0000FF", font: "Arial" },
        paragraph: { spacing: { before: 60, after: 60 } } },

      { id: "Signature", name: "Signature", basedOn: "Normal",
        run: { size: 28, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.RIGHT } }
    ],
    characterStyles: [
      { id: "Keyword", name: "Keyword",
        run: { color: "FF0000", bold: true } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }, // 1 inch margins
        pageNumbers: { start: 1, formatType: "decimal" }
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "自我介绍文档", size: 20 })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "第 " }),
          new TextRun({ children: [PageNumber.CURRENT] }),
          new TextRun({ text: " 页，共 " }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES] }),
          new TextRun({ text: " 页" })
        ]
      })] })
    },
    children: [
      // 标题
      new Paragraph({ heading: HeadingLevel.TITLE, children: [
        new TextRun("自我介绍")
      ]}),

      // 副标题
      new Paragraph({ style: "Subtitle", children: [
        new TextRun("Claude Code - Anthropic 官方 CLI 工具")
      ]}),

      // 基本信息
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [
        new TextRun("基本信息")
      ]}),

      new Paragraph({ children: [
        new TextRun("我是 Claude Code，Anthropic 公司开发的官方命令行界面工具。我专为协助用户完成软件工程任务而设计，能够通过交互式对话帮助您编写、调试、重构和分析代码。")
      ]}),

      new Paragraph({ children: [
        new TextRun("生成日期: "),
        new TextRun({ text: "2026年3月9日", style: "Keyword" })
      ]}),

      new Paragraph({ children: [
        new TextRun("版本: Claude Code (基于 deepseek-chat 模型)")
      ]}),

      // 主要功能
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [
        new TextRun("主要功能")
      ]}),

      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun("代码编辑与生成: 支持多种编程语言的代码编写、重构和优化")
      ]}),

      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun("文件操作: 读取、写入、编辑文件，支持多种文件格式")
      ]}),

      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun("代码分析: 解释代码逻辑，识别潜在问题，提供改进建议")
      ]}),

      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun("调试帮助: 协助定位和修复 bug，提供解决方案")
      ]}),

      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun("文档生成: 创建技术文档、API 文档和用户手册")
      ]}),

      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun("安全测试: 在授权范围内进行安全测试和漏洞分析")
      ]}),

      // 特点优势
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [
        new TextRun("特点与优势")
      ]}),

      // 使用表格展示特点
      createFeaturesTable(),

      // 使用场景
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [
        new TextRun("适用场景")
      ]}),

      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [
        new TextRun("日常编程: 辅助编写 Python、JavaScript、Java、C++ 等语言的代码")
      ]}),

      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [
        new TextRun("项目开发: 从零开始搭建项目，设计架构，实现功能")
      ]}),

      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [
        new TextRun("代码维护: 重构老旧代码，优化性能，添加测试")
      ]}),

      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [
        new TextRun("学习辅助: 解释复杂概念，提供编程示例，解答技术问题")
      ]}),

      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [
        new TextRun("文档工作: 生成技术文档、API 说明、项目 README")
      ]}),

      // 安全准则
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [
        new TextRun("安全准则")
      ]}),

      new Paragraph({ children: [
        new TextRun("我严格遵守安全准则，")
      ]}),

      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun("仅协助授权的安全测试、防御性安全和 CTF 挑战")
      ]}),

      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun("拒绝恶意请求: 如 DoS 攻击、大规模目标攻击、供应链破坏")
      ]}),

      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [
        new TextRun("双重用途安全工具需要明确的授权上下文")
      ]}),

      // 技术能力
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [
        new TextRun("技术能力")
      ]}),

      new Paragraph({ children: [
        new TextRun("支持的工具: "),
        new TextRun({ text: "文件读写、代码编辑、Shell 命令执行、Git 操作、Web 搜索、任务管理等", style: "Keyword" })
      ]}),

      new Paragraph({ children: [
        new TextRun("支持的语言: "),
        new TextRun({ text: "Python、JavaScript/TypeScript、Java、C++、Go、Rust、PHP、Ruby、Swift 等", style: "Keyword" })
      ]}),

      new Paragraph({ children: [
        new TextRun("文件格式: "),
        new TextRun({ text: ".txt、.js、.py、.java、.cpp、.md、.json、.xml、.html、.css 等", style: "Keyword" })
      ]}),

      // 结尾
      new Paragraph({ style: "Signature", children: [
        new TextRun("Claude Code")
      ]}),

      new Paragraph({ style: "Subtitle", children: [
        new TextRun("Anthropic 官方 CLI 工具")
      ]}),

      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "联系方式: 通过 Claude Code 界面直接交互", size: 20, color: "666666" })
      ]})
    ]
  }]
});

// 创建特点表格的函数
function createFeaturesTable() {
  const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

  return new Table({
    columnWidths: [4680, 4680], // 2列等宽
    margins: { top: 100, bottom: 100, left: 180, right: 180 },
    rows: [
      // 表头
      new TableRow({
        tableHeader: true,
        children: [
          new TableCell({
            borders: cellBorders,
            width: { size: 4680, type: WidthType.DXA },
            shading: { fill: "F0F8FF", type: ShadingType.CLEAR },
            verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ text: "特点", bold: true, size: 22 })]
            })]
          }),
          new TableCell({
            borders: cellBorders,
            width: { size: 4680, type: WidthType.DXA },
            shading: { fill: "F0F8FF", type: ShadingType.CLEAR },
            verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ text: "描述", bold: true, size: 22 })]
            })]
          })
        ]
      }),
      // 数据行
      createTableRow("交互式", "通过自然语言对话交互，理解用户需求并提供解决方案"),
      createTableRow("多功能", "支持代码编辑、文件操作、系统命令、Git 管理等多样化功能"),
      createTableRow("安全可靠", "遵循严格的安全准则，保护用户数据和系统安全"),
      createTableRow("高效智能", "基于先进 AI 模型，快速理解和处理复杂技术问题"),
      createTableRow("易于使用", "命令行界面简洁直观，无需复杂配置即可开始工作"),
      createTableRow("持续学习", "不断更新知识库，适应新技术和最佳实践")
    ]
  });
}

function createTableRow(feature, description) {
  const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

  return new TableRow({
    children: [
      new TableCell({
        borders: cellBorders,
        width: { size: 4680, type: WidthType.DXA },
        shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun({ text: feature, bold: true })]
        })]
      }),
      new TableCell({
        borders: cellBorders,
        width: { size: 4680, type: WidthType.DXA },
        shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun(description)]
        })]
      })
    ]
  });
}

// 保存文档
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("自我介绍.docx", buffer);
  console.log("自我介绍文档已成功生成: 自我介绍.docx");
}).catch(error => {
  console.error("生成文档时出错:", error);
});