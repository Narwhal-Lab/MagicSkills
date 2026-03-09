"""Command implementation for executing shell commands."""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from ..type.result import ExecResult

if TYPE_CHECKING:
    from ..type.skills import Skills


def parse_exec_command(arg: str) -> str:
    """Parse command for execskill/run_command from plain text, JSON, or legacy `name::command`."""
    if not arg:
        raise ValueError("execskill requires a non-empty command")
    trimmed = arg.strip()
    if trimmed.startswith("{"):
        payload = json.loads(trimmed)
        command = payload.get("command")
        if not command:
            raise ValueError("execskill JSON must include 'command'")
        return str(command)
    if "::" in trimmed:
        _, command = trimmed.split("::", 1)
        command = command.strip()
        if not command:
            raise ValueError("execskill legacy arg requires command after '::'")
        return command
    return trimmed


def execskill(
    skills: Skills,
    command: str,
    shell: bool = True,
    timeout: float | None = None,
    stream: bool = False,
) -> ExecResult:
    """Execute shell command in current cwd."""
    if not command.strip():
        raise ValueError("execskill requires a command string")
    _ = skills

    if shell:
        cmd = command
    else:
        cmd = shlex.split(command)
    if stream:
        completed = subprocess.run(
            cmd,
            shell=shell,
            cwd=Path.cwd(),
            timeout=timeout,
        )
        return ExecResult(
            command=command,
            returncode=completed.returncode,
            stdout="",
            stderr="",
        )

    completed = subprocess.run(
        cmd,
        shell=shell,
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return ExecResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
