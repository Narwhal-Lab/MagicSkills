"""Shared data models for core operations."""

from __future__ import annotations

from dataclasses import dataclass

from .skill import Skill  # Backward-compatible import path.


@dataclass(frozen=True)
class ExecResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
