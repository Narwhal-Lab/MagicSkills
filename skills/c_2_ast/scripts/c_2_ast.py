#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from pycparser import parse_file, c_ast


# =========================================================
# 内置最小 fake libc
# =========================================================

FAKE_LIBC_HEADERS = {
    "stdio.h": """
        typedef int FILE;
        int printf(const char *fmt, ...);
        int puts(const char *s);
    """,
    "stdlib.h": """
        void exit(int status);
        void *malloc(unsigned long size);
        void free(void *ptr);
    """,
    "string.h": """
        unsigned long strlen(const char *s);
        char *strcpy(char *dest, const char *src);
    """,
}


def prepare_fake_libc() -> Path:
    tmp_dir = Path(tempfile.mkdtemp(prefix="fake_libc_"))
    for name, content in FAKE_LIBC_HEADERS.items():
        (tmp_dir / name).write_text(content, encoding="utf-8")
    return tmp_dir


# =========================================================
# C -> AST
# =========================================================

def c_file_to_ast(c_file: Path) -> c_ast.FileAST:
    if not c_file.exists():
        raise FileNotFoundError(f"C file not found: {c_file}")

    if c_file.suffix != ".c":
        raise ValueError("Input file must be a .c file")

    fake_libc_dir = prepare_fake_libc()

    ast = parse_file(
        filename=str(c_file),
        use_cpp=True,
        cpp_args=[
            "-E",
            f"-I{fake_libc_dir}",
        ],
    )
    return ast


# =========================================================
# main：最终 return AST
# =========================================================

def main():
    parser = argparse.ArgumentParser(
        description="Parse C file and return AST"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to C source file",
    )

    args = parser.parse_args()
    c_file = Path(args.input).expanduser().resolve()

    ast = c_file_to_ast(c_file)

    # 仍然打印一份（方便 CLI 使用）
    ast.show()
    
    # 👇 你要的：main 最终返回 AST
    return ast


if __name__ == "__main__":
    main()
