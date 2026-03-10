# Codex

## codex启动

cd到Codex_example文件夹
/init 在当前启动codex的目录下初始化一个AGENTS.md文件

MagicSkills/Codex_example/image/image1.png

## 安装magicskills

首先 `git clone https://github.com/Narwhal-Lab/MagicSkills.git`

并执行  `pip install -e .` 指令

本文的示例 skill 以 **`docx`** 为例


### 安装 skill(之前已经下载过的可以选择跳过)

执行 `magicskills install anthropics/skills -t ~/allskills`

MagicSkills/Codex_example/image/image2.png
### 创建skills

执行 `magicskills createskills agent1_skills --skill-list pdf docx --agent-md-path ./AGENTS.md`

### 生成 AGETNS.md

执行 `magicskills syncskills agent1_skills --output ./AGENTS.md -y` 指定输出AGENTS.md路径，不指定时候就默认用`createskills`指定的`--agent-md-path ./AGENTS.md`
此时AGENTS.md会出现如下内容
'''md
<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively.

How to use skills:
- Invoke: `magicskills readskill <path>` (run in your shell)
- The skill content will load with detailed instructions
- Base directory provided in output for resolving bundled resources

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
</usage>

<available_skills>

<skill>
<name>pdf</name>
<description>Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.</description>
<path>/root/allskills/pdf</path>
</skill>

<skill>
<name>docx</name>
<description>Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a 'report', 'memo', 'letter', 'template', or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation.</description>
<path>/root/allskills/docx</path>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>
'''

### 使用
输入请你生成一份自我介绍，保存在 .docx 文档中

### 结果如下


## 如果agent应用本身支持skill技能
你只需要将skill下载到该agent寻找skill的路径也可以