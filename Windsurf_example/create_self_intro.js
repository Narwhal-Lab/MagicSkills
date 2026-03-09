const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel } = require('docx');
const fs = require('fs');

// Create self-introduction document based on AGENTS.md content
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } }
    ]
  },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Cascade AI Assistant - Self Introduction")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("About Me")] }),
      new Paragraph({ children: [new TextRun("I am Cascade, a powerful agentic AI coding assistant powered by the model Penguin Alpha, created by Cognition. I work within your IDE to help you complete coding tasks through pair programming.")]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Core Capabilities")] }),
      new Paragraph({ children: [new TextRun("Based on my AGENTS.md configuration, I have access to specialized skills and comprehensive tools for document creation and manipulation:")]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Available Skills")] }),
      new Paragraph({ children: [new TextRun("• DOCX: Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction")]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Technical Expertise")] }),
      new Paragraph({ children: [new TextRun("I excel at creating professional documents using the docx library, with expertise in:")] }),
      new Paragraph({ children: [new TextRun("- Document structure and formatting")] }),
      new Paragraph({ children: [new TextRun("- Professional styling with Arial fonts")] }),
      new Paragraph({ children: [new TextRun("- Table creation and layout")] }),
      new Paragraph({ children: [new TextRun("- List management and numbering")] }),
      new Paragraph({ children: [new TextRun("- Headers, footers, and page setup")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Working Style")] }),
      new Paragraph({ children: [new TextRun("I follow a disciplined approach to coding and document creation:")] }),
      new Paragraph({ children: [new TextRun("• Terse and direct communication")] }),
      new Paragraph({ children: [new TextRun("• Fact-based progress updates")] }),
      new Paragraph({ children: [new TextRun("• Minimal, focused edits")] }),
      new Paragraph({ children: [new TextRun("• Following existing code style")] }),
      new Paragraph({ children: [new TextRun("• Immediate runnable code generation")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Document Creation Standards")] }),
      new Paragraph({ children: [new TextRun("When creating Word documents, I adhere to professional standards:")] }),
      new Paragraph({ children: [new TextRun("- Use Arial fonts for universal compatibility")] }),
      new Paragraph({ children: [new TextRun("- Apply proper visual hierarchy")] }),
      new Paragraph({ children: [new TextRun("- Set consistent margins (1 inch standard)")]}),
      new Paragraph({ children: [new TextRun("- Override built-in styles for consistency")] }),
      new Paragraph({ children: [new TextRun("- Use proper numbering configurations for lists")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Current Task Execution")] }),
      new Paragraph({ children: [new TextRun("This self-introduction document demonstrates my capability to:")] }),
      new Paragraph({ children: [new TextRun("1. Read and analyze configuration files (AGENTS.md)")] }),
      new Paragraph({ children: [new TextRun("2. Extract relevant information for content generation")] }),
      new Paragraph({ children: [new TextRun("3. Create professional Word documents with proper structure")] }),
      new Paragraph({ children: [new TextRun("4. Apply consistent formatting and styling")] }),
      new Paragraph({ children: [new TextRun("5. Document workflow processes in log files")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Conclusion")] }),
      new Paragraph({ children: [new TextRun("I am designed to be a reliable pair programming assistant that combines technical expertise with professional document creation capabilities. My integrated skills system allows me to handle diverse tasks efficiently while maintaining high quality standards.")]}),
      
      new Paragraph({ children: [new TextRun("Generated on: " + new Date().toLocaleDateString())] })
    ]
  }]
});

// Save the document
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("Cascade_Self_Introduction.docx", buffer);
  console.log("Self-introduction document created successfully!");
});
