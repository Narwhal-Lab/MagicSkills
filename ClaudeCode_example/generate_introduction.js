const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, LevelFormat } = require('docx');
const fs = require('fs');

// 创建文档
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
        paragraphStyles: [
            // 覆盖内置标题样式
            {
                id: "Title",
                name: "Title",
                basedOn: "Normal",
                run: { size: 56, bold: true, color: "000000", font: "Arial" },
                paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER }
            },
            {
                id: "Heading1",
                name: "Heading 1",
                basedOn: "Normal",
                next: "Normal",
                quickFormat: true,
                run: { size: 32, bold: true, color: "000000", font: "Arial" },
                paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 }
            },
            {
                id: "Heading2",
                name: "Heading 2",
                basedOn: "Normal",
                next: "Normal",
                quickFormat: true,
                run: { size: 28, bold: true, color: "000000", font: "Arial" },
                paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 }
            },
        ],
    },
    numbering: {
        config: [
            {
                reference: "bullet-list",
                levels: [{
                    level: 0,
                    format: LevelFormat.BULLET,
                    text: "•",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            }
        ]
    },
    sections: [{
        properties: {
            page: {
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1 inch margins
            }
        },
        children: [
            // 标题
            new Paragraph({
                heading: HeadingLevel.TITLE,
                children: [new TextRun("Claude Code 自我介绍")]
            }),

            // 空行
            new Paragraph({ children: [] }),

            // 第一部分：关于我
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("关于我")]
            }),

            new Paragraph({
                children: [
                    new TextRun("我是 Claude Code，Anthropic 官方的 Claude CLI 工具。我旨在帮助用户完成软件工程任务，包括代码编写、调试、重构、解释等。")
                ]
            }),

            // 空行
            new Paragraph({ children: [] }),

            // 第二部分：能力特点
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("能力特点")]
            }),

            // 项目符号列表
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("代码生成与编辑：能够编写、修改、重构各种编程语言的代码")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("代码解释：可以详细解释代码的功能、逻辑和实现细节")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("调试协助：帮助诊断和修复代码中的错误和问题")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("文件操作：读取、编辑、创建文件，管理项目结构")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("工具集成：使用各种工具如 Git、npm、系统命令等协助开发")]
            }),

            // 空行
            new Paragraph({ children: [] }),

            // 第三部分：使用场景
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("使用场景")]
            }),

            new Paragraph({
                children: [
                    new TextRun("我适用于多种软件工程场景，包括但不限于：")
                ]
            }),

            // 空行
            new Paragraph({ children: [] }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("新功能开发：从零开始实现新功能模块")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("代码重构：改善现有代码的结构和可读性")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("bug修复：定位并解决代码中的缺陷")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("项目设置：初始化新项目，配置开发环境")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("文档生成：创建技术文档、API文档等")]
            }),

            // 空行
            new Paragraph({ children: [] }),

            // 第四部分：工作流程
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("工作流程")]
            }),

            new Paragraph({
                children: [
                    new TextRun("我遵循系统化的方法来完成用户请求：")
                ]
            }),

            // 空行
            new Paragraph({ children: [] }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("理解需求：分析用户请求，澄清模糊点")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("探索代码库：读取相关文件，了解项目结构")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("制定计划：设计实现方案，考虑最佳实践")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("执行实施：编写代码，运行测试，验证结果")]
            }),

            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("文档记录：记录变更和决策，便于维护")]
            }),

            // 空行
            new Paragraph({ children: [] }),

            // 结尾
            new Paragraph({
                children: [
                    new TextRun("感谢使用 Claude Code！我期待帮助您完成各种软件工程任务。")
                ]
            }),

            new Paragraph({
                children: [
                    new TextRun("日期：2026年3月9日")
                ]
            }),
        ]
    }]
});

// 生成文档
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync('claude_code_introduction.docx', buffer);
    console.log('文档已生成：claude_code_introduction.docx');
}).catch(error => {
    console.error('生成文档时出错：', error);
});