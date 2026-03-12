# Claude Code

## Claude Code启动

## 安装magicskills

首先 `git clone https://github.com/Narwhal-Lab/MagicSkills.git`

并执行  `pip install -e .` 指令

![1](png/1.png)

本文的示例 skill 以 **`docx`** 为例


### 安装 skill(之前已经下载过的可以选择跳过)

执行 `magicskills install anthropics/skills -t ~/allskills`

![2](png/2.png)



### 创建skills

执行 `magicskills createskills claudecode --skill-list docx --agent-md-path ./AGENTS.md`

### 生成 AGETNS.md

执行 `magicskills syncskills claudecode --output ./AGENTS.md -y` 指定输出AGENTS.md路径，不指定时候就默认用`createskills`指定的`--agent-md-path ./AGENTS.md`
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
<name>pdf</name>
<description>Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.</description>
<path>C:\Users\13978\allskills\pdf</path>
</skill>

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

输入：请你生成一份自我介绍，保存在 .docx 文档中

### 结果如下

```bash
(MCP) PS D:\Python-learning\pythonProject\MagicSkills\ClaudeCode_example> claude

╭─── Claude Code v2.1.56 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                    │ Tips for getting started                                                                                                     │
│                    Welcome back!                   │ Run /init to create a CLAUDE.md file with instructions for Claude                                                            │
│                                                    │ ─────────────────────────────────────────────────────────────────                                                            │
│                                                    │ Recent activity                                                                                                              │
│                       ▐▛███▜▌                      │ No recent activity                                                                                                           │
│                      ▝▜█████▛▘                     │                                                                                                                              │
│                        ▘▘ ▝▝                       │                                                                                                                              │
│         deepseek-chat · API Usage Billing          │                                                                                                                              │
│ D:\Python-learning\pythonProject\MagicSkills\Clau… │                                                                                                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  /model to try Opus 4.6

❯ 请你生成一份自我介绍，保存在 .docx 文档中                                                                                                                                          
                                            
● Searched for 2 patterns, read 2 files (ctrl+o to expand)                                                                                                                           
                 
● Skill(docx)                                                                                                                                                                        
  ⎿  Initializing…
  ⎿  Error: Unknown skill: docx                                                                                                                                                      
                                                                                                                                                                                     ● Bash(magicskills listskill)                                                                                                                                                        
  ⎿  1. name: algorithmic-art                                                                                                                                                        
        description: Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, gen     
     erative art, algorithmic art, flow fields, or particle systems. Create original algorithmic art rather than copying existing artists' work to avoid copyright violations.       
     … +48 lines (ctrl+o to expand)                                                                                                                                                  
                                                                                                                                                                                     ● Read 1 file (ctrl+o to expand)                                                                                                                                                     
                                                                                                                                                                                     
● Bash(magicskills readskill docx)                                                                                                                                                   
  ⎿  Error: Exit code 1                                                                                                                                                              
     'gbk' codec can't encode character '\u274c' in position 5234: illegal multibyte sequence                                                                                        
                                                                                                                                                                                          'gbk' codec can't encode character '\u274c' in position 5234: illegal multibyte sequence                                                                                        
                                                                                                                                                                                     ● Read 7 files (ctrl+o to expand)                                                                                                                                                    
                                                                                                                                                                                     
● Bash(python --version)                                                                                                                                                             
  ⎿  Python 3.12.12                                                                                                                                                                  
                                                                                                                                                                                     
● Bash(node --version)                                                                                                                                                               
  ⎿  v24.11.1                                                                                                                                                                        
                                                                                                                                                                                     ● Bash(magicskills execskill docx help)                                                                                                                                              
  ⎿  Error: Exit code 1                                                                                                                                                              
     'docx' �����ڲ����ⲿ���Ҳ���ǿ����еĳ���                                                                                                                                            
     ���������ļ���                                                                                                                                                                   
                                                                                                                                                                                     
     'docx' �����ڲ����ⲿ���Ҳ���ǿ����еĳ���                                                                                                                                                 ���������ļ���                                                                                                                                                                   
                                                                                                                                                                                     ● Bash(npm init -y)                                                                                                                                                                  
  ⎿  Wrote to D:\Python-learning\pythonProject\MagicSkills\ClaudeCode_example\package.json:                                                                                          
                                                                                                                                                                                          {                                                                                                                                                                               
     … +12 lines (ctrl+o to expand)                                                                                                                                                  
                                                                                                                                                                                     ● Bash(npm install docx)                                                                                                                                                             
  ⎿  added 22 packages, and audited 23 packages in 7s                                                                                                                                
                                                                                                                                                                                     
     1 package is looking for funding                                                                                                                                                
     … +3 lines (ctrl+o to expand)                                                                                                                                                   
                                                                                                                                                                                     ● Write(generate_intro.js)                                                                                                                                                           
  ⎿  Wrote 133 lines to generate_intro.js                                                                                                                                            
     const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageOrientation } = require('docx');                                                                      const fs = require('fs');                                                                                                                                                       
                                                                                                                                                                                          // 创建文档                                                                                                                                                                     
     const doc = new Document({                                                                                                                                                             styles: {                                                                                                                                                                     
         default: { document: { run: { font: "Arial", size: 24 } } }, // 12pt 默认                                                                                                            paragraphStyles: [                                                                                                                                                                     { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,                                                                                             run: { size: 32, bold: true, font: "Arial" },                                                                                                                                … +123 lines (ctrl+o to expand)                                                                                                                                                 

● Bash(node generate_intro.js)
  ⎿  文档已生成：自我介绍.docx
                                                                                                                                                                                     ● Read 1 file (ctrl+o to expand)    
                                                                                                                                                                                     
● 已成功生成自我介绍文档！                                                                                                                                                           
                           
  生成的文件：                                                                                                                                                                       
  - 自我介绍.docx (9.4KB) - 包含完整自我介绍的 Word 文档                                                                                                                                
  使用的脚本：                                                                                                                                                                       
  - generate_intro.js - 生成文档的 Node.js 脚本                                                                                                                                      
  - package.json - Node.js 项目配置文件
  - node_modules/ - docx 库依赖

  文档包含以下内容：
  - 姓名、职位等基本信息
  - 个人简介
  - 技能专长列表
  - 工作经历
  - 教育背景
  - 联系方式

  您可以直接打开 自我介绍.docx 文件查看内容。如果需要修改文档内容，可以编辑 generate_intro.js 脚本中的文本，然后重新运行 node generate_intro.js。

  是否还需要对文档进行其他调整？
```






## 如果agent应用本身支持skill技能
你只需要将skill下载到该agent寻找skill的路径也可以



## skill-tool 的使用

```
  /model to try Opus 4.6
  ❯ 请你生成一份自我介绍，保存在 .docx 文档中，这个任务要求你“必须”使用 magicskills skill-tool <action> --arg "<arg>" --name claudecode
  指令来辅助你的任务（其中 action 必须要使用 listskill 、readskill、execskill、这三个行为，其中 readskill 使用示例为 “ magicskills              
  skill-tool readskill --name claudecode --arg "<path>" ）
────────────────────────────────────────────────────── ctrl+e to show 48 previous messages ─────────────────────────────────────────────────────

● Write(D:\Python-learning\pythonProject\MagicSkills\ClaudeCode_example\create_intro.js)
  ⎿  Wrote 44 lines to D:\Python-learning\pythonProject\MagicSkills\ClaudeCode_example\create_intro.js
     const { Document, Packer, Paragraph, TextRun, HeadingLevel } = require('docx');
     const fs = require('fs');

     // 创建文档
     const doc = new Document({
       sections: [{
         properties: {
           page: {
             size: {
               width: 12240,   // US Letter width in DXA (8.5 inches)
               height: 15840   // US Letter height in DXA (11 inches)
             },
             margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1 inch margins
           }
         },
         children: [
           new Paragraph({
             heading: HeadingLevel.HEADING_1,
             children: [new TextRun("自我介绍")],
           }),
           new Paragraph({
             children: [new TextRun("姓名：张三")],
           }),
           new Paragraph({
             children: [new TextRun("职业：软件工程师")],
           }),
           new Paragraph({
             children: [new TextRun("技能：Python, JavaScript, Node.js, 文档处理")],
           }),
           new Paragraph({
             children: [new TextRun("经历：拥有5年软件开发经验，专注于后端开发和自动化工具。")],
           }),
           new Paragraph({
             children: [new TextRun("兴趣爱好：阅读、编程、爬山")],
           }),
         ]
       }]
     });

     // 保存文档
     Packer.toBuffer(doc).then((buffer) => {
       fs.writeFileSync("自我介绍.docx", buffer);
       console.log("文档已保存为 自我介绍.docx");
     });
  ⎿  1 PostToolUse hook ran

● Bash(PYTHONUTF8=1 magicskills skill-tool execskill --name claudecode --arg "node --version")
  ⎿  {
       "ok": true,
       "action": "execskill",
       "result": {
         "command": "node --version",
         "returncode": 0,
         "stdout": "v24.11.1\n",
         "stderr": ""
       }
     }

● Bash(PYTHONUTF8=1 magicskills skill-tool execskill --name claudecode --arg "node create_intro.js")
  ⎿  {
       "ok": true,
       "action": "execskill",
       "result": {
         "command": "node create_intro.js",
         "returncode": 1,
         "stdout": "",
         "stderr": "node:internal/modules/cjs/loader:1424\n  throw err;\n  ^\n\nError: Cannot find module 'docx'\nRequire stack:\n-
     D:\\Python-learning\\pythonProject\\MagicSkills\\ClaudeCode_example\\create_intro.js\n    at Module._resolveFilename
     (node:internal/modules/cjs/loader:1421:15)\n    at defaultResolveImpl (node:internal/modules/cjs/loader:1059:19)\n    at
     resolveForCJSWithHooks (node:internal/modules/cjs/loader:1064:22)\n    at Module._load (node:internal/modules/cjs/loader:1227:37)\n        
     at TracingChannel.traceSync (node:diagnostics_channel:328:14)\n    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)\n    at     
     Module.require (node:internal/modules/cjs/loader:1504:12)\n    at require (node:internal/modules/helpers:152:16)\n    at
     Object.<anonymous> (D:\\Python-learning\\pythonProject\\MagicSkills\\ClaudeCode_example\\create_intro.js:1:64)\n    at Module._compile     
     (node:internal/modules/cjs/loader:1761:14) {\n  code: 'MODULE_NOT_FOUND',\n  requireStack: [\n
     'D:\\\\Python-learning\\\\pythonProject\\\\MagicSkills\\\\ClaudeCode_example\\\\create_intro.js'\n  ]\n}\n\nNode.js v24.11.1\n"
       }
     }




● Bash(PYTHONUTF8=1 magicskills skill-tool execskill --name claudecode --arg "npm install -g docx")
  ⎿  {
       "ok": true,
       "action": "execskill",
       "result": {
         "command": "npm install -g docx",
         "returncode": 0,
         "stdout": "\nchanged 22 packages in 3s\n\n1 package is looking for funding\n  run `npm fund` for details\n",
         "stderr": ""
       }
     }

● Bash(PYTHONUTF8=1 magicskills skill-tool execskill --name claudecode --arg "node create_intro.js")
  ⎿  {
       "ok": true,
       "action": "execskill",
       "result": {
         "command": "node create_intro.js",
         "returncode": 1,
         "stdout": "",
         "stderr": "node:internal/modules/cjs/loader:1424\n  throw err;\n  ^\n\nError: Cannot find module 'docx'\nRequire stack:\n-
     D:\\Python-learning\\pythonProject\\MagicSkills\\ClaudeCode_example\\create_intro.js\n    at Module._resolveFilename
     (node:internal/modules/cjs/loader:1421:15)\n    at defaultResolveImpl (node:internal/modules/cjs/loader:1059:19)\n    at
     resolveForCJSWithHooks (node:internal/modules/cjs/loader:1064:22)\n    at Module._load (node:internal/modules/cjs/loader:1227:37)\n        
     at TracingChannel.traceSync (node:diagnostics_channel:328:14)\n    at wrapModuleLoad (node:internal/modules/cjs/loader:245:24)\n    at     
     Module.require (node:internal/modules/cjs/loader:1504:12)\n    at require (node:internal/modules/helpers:152:16)\n    at
     Object.<anonymous> (D:\\Python-learning\\pythonProject\\MagicSkills\\ClaudeCode_example\\create_intro.js:1:64)\n    at Module._compile     
     (node:internal/modules/cjs/loader:1761:14) {\n  code: 'MODULE_NOT_FOUND',\n  requireStack: [\n
     'D:\\\\Python-learning\\\\pythonProject\\\\MagicSkills\\\\ClaudeCode_example\\\\create_intro.js'\n  ]\n}\n\nNode.js v24.11.1\n"
       }
     }




● Bash(PYTHONUTF8=1 magicskills skill-tool execskill --name claudecode --arg "npm install docx")
  ⎿  {
       "ok": true,
       "action": "execskill",
       "result": {
         "command": "npm install docx",
         "returncode": 0,
         "stdout": "\nadded 22 packages in 667ms\n\n1 package is looking for funding\n  run `npm fund` for details\n",
         "stderr": ""
       }
     }

● Bash(PYTHONUTF8=1 magicskills skill-tool execskill --name claudecode --arg "node create_intro.js")
  ⎿  {
       "ok": true,
       "action": "execskill",
       "result": {
         "command": "node create_intro.js",
         "returncode": 0,
         "stdout": "文档已保存为 自我介绍.docx\n",
         "stderr": ""
       }
     }

● Bash(ls -la "自我介绍.docx")
  ⎿  -rw-r--r-- 1 13978 197609 8769  3月 11 01:08 自我介绍.docx

∴ Thinking…

  文件存在，大小 8769 字节。现在，我可能需要清理临时脚本文件。但用户没有要求清理。我可以选择删除 create_intro.js 文件。不过，保留它也没关系。   

  现在，总结一下我所做的：

  1. 使用 magicskills skill-tool listskill --name claudecode 列出可用技能，发现 docx 技能。
  2. 使用 magicskills skill-tool readskill --name claudecode --arg "docx" 读取技能文档（需要设置 PYTHONUTF8=1 以避免编码错误）。
  3. 使用 magicskills skill-tool execskill 执行命令来创建文档：
    - 安装 docx 包（全局和本地）
    - 创建 Node.js 脚本生成自我介绍文档
    - 执行脚本生成 "自我介绍.docx"

  现在，我应该向用户报告任务完成，并说明文档已保存。同时，提醒用户文档的保存位置。让我输出最终结果。

                                                                                                              01:09 AM deepseek-reasoner        
● 我已经按照您的要求，使用 magicskills skill-tool 指令完成了自我介绍文档的生成。以下是完整步骤：

  1. 使用 listskill 列出可用技能

  magicskills skill-tool listskill --name claudecode
  结果：发现 docx 技能，用于创建、编辑 Word 文档。

  2. 使用 readskill 读取技能文档

  PYTHONUTF8=1 magicskills skill-tool readskill --name claudecode --arg "docx"
  成功读取了 docx 技能的详细文档，包含使用 JavaScript 的 docx 包创建文档的方法。

  3. 使用 execskill 执行创建任务

  通过一系列命令完成文档生成：

  1. 检查 Node.js 环境：
  PYTHONUTF8=1 magicskills skill-tool execskill --name claudecode --arg "node --version"
  2. 安装 docx 包：
  PYTHONUTF8=1 magicskills skill-tool execskill --name claudecode --arg "npm install docx"
  3. 创建生成脚本 create_intro.js：
  const { Document, Packer, Paragraph, TextRun, HeadingLevel } = require('docx');
  const fs = require('fs');

  const doc = new Document({
    sections: [{
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      children: [
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("自我介绍")] }),
        new Paragraph({ children: [new TextRun("姓名：张三")] }),
        new Paragraph({ children: [new TextRun("职业：软件工程师")] }),
        new Paragraph({ children: [new TextRun("技能：Python, JavaScript, Node.js, 文档处理")] }),
        new Paragraph({ children: [new TextRun("经历：拥有5年软件开发经验，专注于后端开发和自动化工具。")] }),
        new Paragraph({ children: [new TextRun("兴趣爱好：阅读、编程、爬山")] }),
      ]
    }]
  });

  Packer.toBuffer(doc).then((buffer) => {
    fs.writeFileSync("自我介绍.docx", buffer);
    console.log("文档已保存为 自我介绍.docx");
  });
  4. 执行脚本生成文档：
  PYTHONUTF8=1 magicskills skill-tool execskill --name claudecode --arg "node create_intro.js"
  4. 输出：文档已保存为 自我介绍.docx

  结果

  ✅ 文档已成功生成：自我介绍.docx（8.7 KB）

  文档包含以下内容：
  - 标题：自我介绍
  - 姓名：张三
  - 职业：软件工程师
  - 技能：Python, JavaScript, Node.js, 文档处理
  - 经历：拥有5年软件开发经验，专注于后端开发和自动化工具
  - 兴趣爱好：阅读、编程、爬山

  文件保存在当前目录：D:\Python-learning\pythonProject\MagicSkills\ClaudeCode_example\自我介绍.docx

  已完全按照您的要求使用了 listskill、readskill、execskill 三个行为，并通过 magicskills skill-tool 指令辅助完成任务。
```

