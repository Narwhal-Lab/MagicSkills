---
name: c-to-ast
description: Parse C source code into an Abstract Syntax Tree (AST). Use when analyzing C programs, understanding code structure, performing static analysis, or preparing code for further program analysis (e.g., CFG, DFG, vulnerability detection).
---

# C to AST Skill

## Purpose

This Skill converts **C source code** into its **Abstract Syntax Tree (AST)** representation.

Use this Skill when you need to:
- Understand the structure of a C program
- Analyze functions, statements, and expressions
- Prepare C code for static analysis or security analysis
- Transform C code into an intermediate representation (AST)
- Feed structured code information into downstream tools or agents

The AST is generated using a Python-based C parser and printed directly to standard output.

---

## When to Use

Apply this Skill when the user asks to:
- “Parse this C code”
- “Convert this C file to an AST”
- “Show me the AST of this C program”
- “Analyze the structure of this C code”
- “Extract syntax tree / abstract syntax tree from C”

This Skill is especially useful in **compiler frontends**, **program analysis**, and **security research** workflows.

---

## Instructions

Follow these steps strictly and in order:

1. **Navigate to the Skill scripts directory**
   - Change working directory to:
     ```
     skills_for_all_agent/skill/c_2_ast/scripts/
     ```

2. **Handle the input C source**
   - If the user provides a **path to a `.c` file**, use it directly.
   - If the user provides **inline C code as a string**, you must first save it to a C source file using the provided script:
     ```bash
     python3 save_c.py --input "<C code string>" --output <output_dir> --filename <filename>.c
     ```
   - Ensure the generated file has a `.c` extension and is successfully written to disk.

3. **Run the AST extraction script**
   - Convert the C source file to its Abstract Syntax Tree by executing:
     ```bash
     python3 c_2_ast.py --input <path_to_c_file>
     ```

4. **Do not modify the source code**
   - This Skill is strictly read-only.
   - Do not rewrite, reformat, optimize, or otherwise alter the C code.

5. **Return the AST output verbatim**
   - The script prints the AST directly to standard output.
   - Return the output exactly as produced.
   - Do not summarize, paraphrase, or restructure the AST.
   - Preserve indentation, hierarchy, and node ordering.

6. **If parsing fails**
   - Report the exact error message produced by the script.
   - Suggest likely causes, such as:
     - Missing or unsupported header files
     - Unsupported C extensions (e.g., compiler-specific syntax)
     - Invalid or incomplete C syntax

---

## Output Format

The output is a **tree-structured textual AST**, for example:

````

FileAST:
FuncDef:
Decl: main
FuncDecl:
TypeDecl:
IdentifierType: ['int']
Compound:
FuncCall:
ID: puts
ExprList:
Constant: string, "Hello"
Return:
Constant: int, 0

````

This output represents the syntactic structure of the C program and can be consumed by downstream tools.

---

## Additional Resources

For deeper understanding of:
- AST node types
- `pycparser` internal representation
- Meaning of specific syntax tree nodes
- Limitations of the C grammar supported

see the accompanying reference document:

➡️ **[reference.md](reference.md)**

Only read this file **when more detailed or theoretical information is required**.  
For standard AST extraction tasks, this Skill file alone is sufficient.

---

## Notes and Limitations

- The AST follows standard C syntax (C89/C99 subset).
- Some compiler-specific extensions (e.g., GCC attributes) may not be supported.
- Header files are handled using a minimal fake libc environment.
- Macro-heavy or highly platform-specific code may require preprocessing.

---

## Examples

### Example 1: Simple AST extraction

User request:
> Convert this C file to an AST.

Action:
```bash
python3 c_2_AST.py --input example.c
````

Result:

* The AST is printed directly.

---

### Example 2: Security analysis preparation

User request:

> I want to analyze this C program for vulnerabilities.

Action:

* First, extract the AST using this Skill.
* Then, pass the AST to a vulnerability analysis or pattern-matching process.

---

## Best Practices

* Use this Skill **before** any deep code analysis.
* Treat the AST as an intermediate representation.
* Combine with CFG/DFG or semantic analysis for advanced tasks.

---

End of Skill.
