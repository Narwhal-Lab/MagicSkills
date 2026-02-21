# reference.md

## C Abstract Syntax Tree (AST) Reference

This document provides **detailed reference material** for understanding the **Abstract Syntax Tree (AST)** generated from C source code by the `c_2_AST.py` script.

Read this file **only when deeper knowledge is required**, such as:

* Interpreting specific AST node types
* Writing AST-based analyses or transformations
* Performing vulnerability detection or code pattern matching
* Mapping syntax to semantic structures (CFG / DFG)

---

## 1. What Is a C AST?

An **Abstract Syntax Tree (AST)** is a hierarchical representation of a program’s syntactic structure.

Key properties:

* Represents **syntax**, not runtime behavior
* Ignores formatting, comments, and whitespace
* Encodes structure: declarations, statements, expressions

ASTs are commonly used in:

* Compilers and interpreters
* Static analysis tools
* Security auditing and vulnerability detection
* Program understanding and refactoring tools

---

## 2. AST Format Used in This Skill

This Skill uses **`pycparser`**, a pure-Python C parser that supports a large subset of ISO C.

The AST is represented as a tree of Python objects, printed in a readable textual format using:

```python
ast.show()
```

The root node is always:

```
FileAST
```

---

## 3. High-Level AST Structure

```
FileAST
 ├── Decl
 ├── FuncDef
 │    ├── Decl
 │    ├── ParamList
 │    └── Compound
 └── ...
```

* `FileAST`: Entire translation unit
* Each child corresponds to a **top-level declaration or definition**

---

## 4. Core Node Types (Most Important)

### 4.1 FileAST

**Root node** of the AST.

```text
FileAST:
  ext[0]: FuncDef
  ext[1]: Decl
```

Contains:

* Global variable declarations
* Function definitions
* Type definitions

---

### 4.2 FuncDef (Function Definition)

Represents a full function definition.

```text
FuncDef:
  Decl: main
  ParamList
  Compound
```

Components:

* `Decl`: function signature
* `ParamList`: parameters (may be empty)
* `Compound`: function body

---

### 4.3 Decl (Declaration)

Used for:

* Variables
* Functions
* Parameters

```text
Decl: x
  TypeDecl
  Constant
```

Key attributes:

* `name`: identifier
* `type`: declared type
* `init`: initializer (if any)

---

### 4.4 Type Nodes

Type information is represented hierarchically.

#### TypeDecl

```text
TypeDecl:
  IdentifierType: ['int']
```

#### PtrDecl

```text
PtrDecl:
  TypeDecl
```

#### ArrayDecl

```text
ArrayDecl:
  TypeDecl
  Constant
```

---

### 4.5 Compound (Block)

Represents a `{ ... }` block.

```text
Compound:
  Decl
  Assignment
  Return
```

Used for:

* Function bodies
* Control-flow blocks

---

## 5. Statement Nodes

### 5.1 Assignment

```text
Assignment:
  ID: x
  BinaryOp: +
```

Represents:

```c
x = a + b;
```

---

### 5.2 Return

```text
Return:
  Constant: int, 0
```

Represents:

```c
return 0;
```

---

### 5.3 If

```text
If:
  BinaryOp
  Compound
  Compound
```

Represents:

```c
if (cond) { ... } else { ... }
```

---

### 5.4 While / For

```text
While:
  BinaryOp
  Compound
```

```text
For:
  Assignment
  BinaryOp
  Assignment
  Compound
```

---

## 6. Expression Nodes

### 6.1 ID

```text
ID: x
```

Variable reference.

---

### 6.2 Constant

```text
Constant: int, 42
Constant: string, "hello"
```

Literal values.

---

### 6.3 BinaryOp

```text
BinaryOp: +
  ID: a
  ID: b
```

Represents:

```c
a + b
```

Operators include:
`+ - * / % < > == != && ||`

---

### 6.4 FuncCall

```text
FuncCall:
  ID: puts
  ExprList
```

Represents:

```c
puts("hello");
```

---

## 7. Common Patterns (Analysis-Oriented)

### Function Call Detection

Look for:

```
FuncCall → ID(name)
```

Useful for:

* Detecting dangerous functions (`gets`, `strcpy`)
* API usage analysis

---

### Control Flow Detection

Look for:

* `If`
* `For`
* `While`
* `Switch`

These nodes form the basis of **CFG construction**.

---

### Memory-Related Operations

Relevant nodes:

* `FuncCall` to `malloc`, `free`
* Pointer `PtrDecl`
* Dereference via `UnaryOp: *`

---

## 8. Limitations and Caveats

* Supports **standard C**, not full GCC extensions
* Macro-heavy code may be simplified by preprocessing
* No semantic analysis (types are syntactic, not resolved)
* No symbol resolution across files

For complex builds, preprocessing quality matters.

---

## 9. Typical Downstream Uses

ASTs extracted by this Skill are commonly used for:

* Building **Control Flow Graphs (CFG)**
* Extracting **Data Flow Graphs (DFG)**
* Pattern-based vulnerability detection
* Code similarity and embedding
* Automated refactoring and transformation

---

## 10. Summary

* AST = **structured syntax representation**
* `FileAST` is always the root
* Nodes map closely to C language constructs
* Ideal intermediate form for static analysis and security research

Use this reference as a **lookup guide**, not as required reading for every task.

---

End of reference.
