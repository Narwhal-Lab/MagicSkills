"""Command-line interface for MagicSkills.

Each subcommand maps to exactly one concrete feature.
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import platform
import shutil
import subprocess
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .command.addskill import addskill as command_addskill
from .command.addskills import addskills as command_addskills
from .command.install import install
from .command.change_cli_description import change_cli_description as command_change_cli_description
from .command.createskill_template import createskill_template as command_createskill_template
from .command.change_tool_description import change_tool_description as command_change_tool_description
from .command.execskill import execskill as command_execskill
from .command.listskill import listskill as command_listskill
from .command.readskill import readskill as command_readskill
from .command.scanskill import scanskill as command_scanskill
from .command.scanskills import scanskills as command_scanskills
from .command.skill_tool import skill_tool as command_skill_tool
from .command.syncskills import syncskills as command_syncskills
from .command.uploadskill import uploadskill as command_uploadskill
from .command.showskill import showskill as command_showskill
from .command.listskills import listskills as command_listskills
from .command.loadskills import loadskills as command_loadskills
from .command.deleteskills import deleteskills as command_deleteskills
from .command.deleteskill import deleteskill as command_deleteskill
from .command.saveskills import saveskills as command_saveskills
from .type.skillsregistry import ALL_SKILLS, REGISTRY
from .type.skills import Skills
from .utils.agents_md import SYNC_MODES
from .utils.utils import normalize_paths


def _is_gh_missing_error(exc: Exception) -> bool:
    """Detect runtime errors caused by missing GitHub CLI."""
    message = str(exc).lower()
    return "gh" in message and "not found" in message


def _is_gh_auth_error(exc: Exception) -> bool:
    """Detect runtime errors caused by unauthenticated GitHub CLI."""
    message = str(exc).lower()
    return (
        "failed to query github user via gh" in message
        or "gh auth login" in message
        or "failed to create pr via gh" in message
    )


def _install_gh_cli() -> None:
    """Install GitHub CLI using best-effort OS package manager commands."""
    if shutil.which("gh"):
        return

    system = platform.system().lower()
    attempts: list[tuple[str, list[list[str]]]] = []
    if system == "linux":
        attempts = [
            ("apt-get", [["apt-get", "update"], ["apt-get", "install", "-y", "gh"]]),
            ("dnf", [["dnf", "install", "-y", "gh"]]),
            ("yum", [["yum", "install", "-y", "gh"]]),
            ("pacman", [["pacman", "-Sy", "--noconfirm", "github-cli"]]),
        ]
    elif system == "darwin":
        attempts = [("brew", [["brew", "install", "gh"]])]
    elif system == "windows":
        attempts = [
            ("winget", [["winget", "install", "--id", "GitHub.cli", "-e", "--source", "winget"]]),
            ("choco", [["choco", "install", "gh", "-y"]]),
        ]
    else:
        raise RuntimeError(f"Unsupported platform for auto-installing gh: {system}")

    failures: list[str] = []
    for binary, commands in attempts:
        if shutil.which(binary) is None:
            continue
        try:
            for command in commands:
                subprocess.run(command, check=True)
            if shutil.which("gh"):
                return
            failures.append(f"{binary}: install command completed but gh still not found")
        except subprocess.CalledProcessError as exc:
            failures.append(f"{binary}: command failed ({exc})")
        except OSError as exc:
            failures.append(f"{binary}: failed to execute ({exc})")

    if failures:
        details = "; ".join(failures)
        raise RuntimeError(f"Failed to auto-install gh. Details: {details}")
    raise RuntimeError("No supported package manager found to auto-install gh")


def _maybe_install_gh_for_upload() -> bool:
    """Prompt user to auto-install gh and return whether upload can be retried."""
    if not sys.stdin.isatty():
        print("GitHub CLI (gh) is missing and session is non-interactive; cannot auto-install.")
        return False

    answer = input("GitHub CLI (gh) is missing. Install now and continue upload? [Y/n] ").strip().lower()
    if answer not in {"", "y", "yes"}:
        return False

    try:
        _install_gh_cli()
    except RuntimeError as exc:
        print(str(exc))
        return False
    return shutil.which("gh") is not None


def _maybe_login_gh_for_upload() -> bool:
    """Prompt user to authenticate gh and return whether upload can be retried."""
    if not sys.stdin.isatty():
        print("GitHub CLI (gh) is not authenticated and session is non-interactive; cannot run `gh auth login`.")
        return False
    if shutil.which("gh") is None:
        print("GitHub CLI (gh) is not installed yet.")
        return False

    answer = input("GitHub CLI is not authenticated. Run `gh auth login` now? [Y/n] ").strip().lower()
    if answer not in {"", "y", "yes"}:
        return _maybe_set_gh_token_for_upload()

    try:
        subprocess.run(["gh", "auth", "login"], check=True)
        subprocess.run(["gh", "api", "user", "-q", ".login"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"`gh auth login` failed: {exc}")
        return _maybe_set_gh_token_for_upload()


def _maybe_set_gh_token_for_upload() -> bool:
    """Prompt user to provide GH_TOKEN for API fallback upload flow."""
    if not sys.stdin.isatty():
        return False
    answer = input("Provide GH_TOKEN now for API fallback? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        return False
    token = input("Paste GH_TOKEN: ").strip()
    if not token:
        print("Empty token. Skip GH_TOKEN fallback.")
        return False
    os.environ["GH_TOKEN"] = token
    return True


def _paths_from_args(values: Iterable[str] | None) -> list[Path] | None:
    """Normalize optional path arguments."""
    if not values:
        return None
    return normalize_paths(values)


def _headers_from_args(values: Iterable[str] | None) -> dict[str, str] | None:
    """Parse repeated KEY:VALUE or KEY=VALUE header args into a mapping."""
    if not values:
        return None
    headers: dict[str, str] = {}
    for raw in values:
        value = str(raw).strip()
        if ":" in value:
            key, _, remainder = value.partition(":")
        elif "=" in value:
            key, _, remainder = value.partition("=")
        else:
            raise SystemExit(f"Invalid --header value: {value}. Use KEY:VALUE or KEY=VALUE.")
        key = key.strip()
        remainder = remainder.strip()
        if not key:
            raise SystemExit(f"Invalid --header value: {value}. Header key cannot be empty.")
        headers[key] = remainder
    return headers


def _looks_like_path_input(value: str) -> bool:
    raw = value.strip()
    if not raw:
        return False
    if "/" in raw or "\\" in raw or raw.startswith(".") or raw.startswith("~"):
        return True
    return Path(raw).expanduser().exists()


def _scan_kwargs_from_args(args: argparse.Namespace) -> dict[str, object]:
    """Build shared AI-Infra-Guard config kwargs from CLI args."""
    return {
        "base_url": args.base_url,
        "model": args.model,
        "api_key": args.api_key,
        "model_base_url": args.model_base_url,
        "prompt": args.prompt,
        "language": args.language,
        "thread": args.thread,
        "poll_interval": args.poll_interval,
        "timeout": args.timeout,
        "headers": _headers_from_args(args.header),
    }


def _add_visible_scan_args(parser: argparse.ArgumentParser) -> None:
    """Expose the small set of scan flags that should stay in primary CLI help."""
    parser.add_argument("--base-url", help="AI-Infra-Guard base URL")
    parser.add_argument("--model", help="Model name used by AI-Infra-Guard scan")
    parser.add_argument("--api-key", dest="api_key", help="Model API key used by AI-Infra-Guard scan")
    parser.add_argument("--token", dest="api_key", help=argparse.SUPPRESS)
    parser.add_argument("--model-base-url", help="Model base URL used by AI-Infra-Guard scan")


def _add_hidden_scan_args(parser: argparse.ArgumentParser) -> None:
    """Keep advanced scan overrides available without advertising them in primary help."""
    parser.add_argument("--prompt", help=argparse.SUPPRESS)
    parser.add_argument("--language", help=argparse.SUPPRESS)
    parser.add_argument("--thread", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--poll-interval", type=float, help=argparse.SUPPRESS)
    parser.add_argument("--timeout", type=float, help=argparse.SUPPRESS)
    parser.add_argument("--header", action="append", help=argparse.SUPPRESS)


def _supports_color_output() -> bool:
    """Best-effort detection for ANSI color support in current terminal."""
    if os.environ.get("NO_COLOR"):
        return False
    term = os.environ.get("TERM", "").lower()
    if term in {"", "dumb"}:
        return False
    return sys.stdout.isatty()


def _paint(text: str, style: str, enabled: bool) -> str:
    """Apply ANSI style when color is enabled."""
    if not enabled:
        return text
    return f"\033[{style}m{text}\033[0m"


def _display_width(text: str) -> int:
    """Estimate terminal cell width for one string."""
    width = 0
    for char in text:
        if unicodedata.combining(char):
            continue
        width += 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
    return width


def _pad_display_width(text: str, width: int) -> str:
    """Pad one string with ASCII spaces up to the requested display width."""
    padding = max(width - _display_width(text), 0)
    return text + (" " * padding)


def _wrap_display_line(text: str, width: int) -> list[str]:
    """Wrap one line based on terminal display width rather than Python character count."""
    if width <= 0:
        return [text]
    if not text:
        return [""]

    chunks: list[str] = []
    current_chars: list[str] = []
    current_width = 0
    last_break_index: int | None = None

    for char in text:
        char_width = 0 if unicodedata.combining(char) else (2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1)
        if current_chars and current_width + char_width > width:
            if last_break_index is not None:
                chunk = "".join(current_chars[: last_break_index + 1]).rstrip()
                remainder_chars = current_chars[last_break_index + 1 :]
                while remainder_chars and remainder_chars[0] == " ":
                    remainder_chars.pop(0)
                chunks.append(chunk or "".join(current_chars[: last_break_index + 1]))
                current_chars = remainder_chars
                current_width = _display_width("".join(current_chars))
                last_break_index = None
                for index, existing in enumerate(current_chars):
                    if existing.isspace() or existing in {"-", "/", "\\"}:
                        last_break_index = index
            else:
                chunks.append("".join(current_chars))
                current_chars = []
                current_width = 0

        current_chars.append(char)
        current_width += char_width
        if char.isspace() or char in {"-", "/", "\\"}:
            last_break_index = len(current_chars) - 1

    if current_chars:
        chunks.append("".join(current_chars).rstrip())
    return chunks or [""]


def _boxed_lines(title: str, rows: list[str], *, width: int, style: str, color: bool) -> list[str]:
    """Render one titled ASCII box with optional color."""
    border = "+" + "-" * (width - 2) + "+"
    output = [
        _paint(border, style, color),
        _paint("|" + _pad_display_width(f" {title} ", width - 2) + "|", style, color),
        _paint(border, style, color),
    ]
    inner_width = width - 4
    for row in rows:
        row_lines = str(row).splitlines() or [""]
        for row_line in row_lines:
            chunks = _wrap_display_line(row_line.expandtabs(4), inner_width)
            for chunk in chunks:
                output.append(f"| {_pad_display_width(chunk, inner_width)} |")
    output.append(_paint(border, style, color))
    return output


def _scan_output_width() -> int:
    """Pick a readable terminal width for scan result rendering."""
    columns = shutil.get_terminal_size(fallback=(96, 24)).columns
    return max(72, min(columns, 112))


def _scan_filename_slug(value: object, *, fallback: str) -> str:
    """Convert a value into a filesystem-friendly slug."""
    raw = str(value).strip().lower()
    if not raw:
        return fallback
    parts: list[str] = []
    previous_was_dash = False
    for char in raw:
        if char.isalnum():
            parts.append(char)
            previous_was_dash = False
        elif not previous_was_dash:
            parts.append("-")
            previous_was_dash = True
    slug = "".join(parts).strip("-")
    return slug or fallback


def _default_scan_save_path(result: dict[str, object]) -> Path:
    """Build a default text output path for saved detailed scan output."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    collection_name = result.get("collection_name")
    if isinstance(collection_name, str) and collection_name.strip():
        slug = _scan_filename_slug(collection_name, fallback="collection")
        filename = f"scanskills-{slug}-{timestamp}.txt"
    else:
        skill_name = _scan_filename_slug(result.get("skill_name", "skill"), fallback="skill")
        session_id = _scan_filename_slug(result.get("session_id", timestamp), fallback=timestamp)
        filename = f"scanskill-{skill_name}-{session_id}.txt"
    return Path.cwd() / filename


def _resolve_scan_color(enabled: bool | None) -> bool:
    """Resolve color output preference, defaulting to terminal auto-detection."""
    return _supports_color_output() if enabled is None else enabled


def _save_scan_result(result: dict[str, object], destination: str | None) -> Path:
    """Persist formatted detailed scan output to a text file."""
    output_path = _default_scan_save_path(result) if destination in {None, ""} else Path(destination).expanduser()
    resolved_path = output_path.resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(_format_saved_scan_output(result), encoding="utf-8")
    return resolved_path


def _nested_scan_result_payload(result: dict[str, object]) -> dict[str, object]:
    """Return the inner `/result` payload body when present."""
    raw_result = result.get("result")
    if not isinstance(raw_result, dict):
        return {}
    nested = raw_result.get("result")
    return nested if isinstance(nested, dict) else {}


def _scalar_text(value: object) -> str | None:
    """Convert simple scalar values to display text."""
    if isinstance(value, (str, int, float)):
        text = str(value).strip()
        return text or None
    return None


_SCAN_RISK_ORDER = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "INFO": 0,
}


def _normalize_scan_level(value: object) -> str | None:
    """Normalize one structured finding level into a stable uppercase label."""
    text = _scalar_text(value)
    if text is None:
        return None
    return text.upper()


def _scan_findings(result: dict[str, object]) -> list[object]:
    """Extract structured findings strictly from `result.results`."""
    payload = _nested_scan_result_payload(result)
    findings = payload.get("results")
    if not isinstance(findings, list):
        return []
    return [item for item in findings if isinstance(item, dict)]


def _scan_findings_count(result: dict[str, object]) -> int | None:
    """Resolve findings count strictly from structured findings."""
    findings = _scan_findings(result)
    return len(findings)


def _scan_risk_levels(result: dict[str, object]) -> list[str]:
    """Return one normalized risk level for each structured finding, preserving duplicates."""
    levels: list[str] = []
    for item in _scan_findings(result):
        if not isinstance(item, dict):
            continue
        level = _normalize_scan_level(item.get("level"))
        if level is not None:
            levels.append(level)
    return levels


def _scan_risk_level(result: dict[str, object]) -> str | None:
    """Aggregate the highest structured risk level for one scan result."""
    best_level: str | None = None
    best_rank = -1
    fallback_level: str | None = None
    for level in _scan_risk_levels(result):
        fallback_level = fallback_level or level
        rank = _SCAN_RISK_ORDER.get(level, -1)
        if rank > best_rank:
            best_rank = rank
            best_level = level
    return best_level or fallback_level


def _scan_report_rows(report: str) -> list[str]:
    """Render one Markdown report into terminal-friendly plain text rows."""

    def flush_paragraph(rows: list[str], paragraph: list[str]) -> None:
        if not paragraph:
            return
        text = " ".join(part.strip() for part in paragraph if part.strip())
        if text:
            rows.append(text)
        paragraph.clear()

    def normalize_list_item(line: str) -> str | None:
        stripped = line.strip()
        for prefix in ("- ", "* ", "+ "):
            if stripped.startswith(prefix):
                body = stripped[len(prefix):].strip()
                return f"- {body}" if body else "-"

        digits = 0
        while digits < len(stripped) and stripped[digits].isdigit():
            digits += 1
        if digits and digits + 1 < len(stripped) and stripped[digits] in {".", ")"} and stripped[digits + 1] == " ":
            body = stripped[digits + 2 :].strip()
            return f"{stripped[:digits]}. {body}" if body else f"{stripped[:digits]}."
        return None

    rows: list[str] = []
    paragraph: list[str] = []
    in_code_block = False
    code_block_label: str | None = None

    for raw_line in report.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if in_code_block:
            if stripped.startswith("```"):
                in_code_block = False
                code_block_label = None
                continue
            rows.append(f"    {line}" if line else "")
            continue

        if stripped.startswith("```"):
            flush_paragraph(rows, paragraph)
            if rows and rows[-1] != "":
                rows.append("")
            in_code_block = True
            code_block_label = stripped[3:].strip() or None
            rows.append(f"[{code_block_label}]" if code_block_label else "[code]")
            continue

        if not stripped:
            flush_paragraph(rows, paragraph)
            if rows and rows[-1] != "":
                rows.append("")
            continue

        if stripped.startswith("#"):
            flush_paragraph(rows, paragraph)
            heading = stripped.lstrip("#").strip()
            if heading:
                if rows and rows[-1] != "":
                    rows.append("")
                rows.append(heading)
            continue

        if stripped.startswith(">"):
            flush_paragraph(rows, paragraph)
            quote = stripped.lstrip(">").strip()
            rows.append(f"> {quote}" if quote else ">")
            continue

        if stripped.startswith("|"):
            flush_paragraph(rows, paragraph)
            rows.append(stripped)
            continue

        list_item = normalize_list_item(stripped)
        if list_item is not None:
            flush_paragraph(rows, paragraph)
            rows.append(list_item)
            continue

        paragraph.append(stripped)

    flush_paragraph(rows, paragraph)

    while rows and rows[0] == "":
        rows.pop(0)
    while rows and rows[-1] == "":
        rows.pop()

    collapsed: list[str] = []
    for row in rows:
        if row == "" and collapsed and collapsed[-1] == "":
            continue
        collapsed.append(row)
    return collapsed


def _scan_preview_lines(result: dict[str, object], *, limit: int = 3) -> list[str]:
    """Render a short preview for the first few structured findings."""
    preview: list[str] = []
    for index, item in enumerate(_scan_findings(result)[:limit], start=1):
        if isinstance(item, dict):
            title = _scalar_text(item.get("title")) or "(untitled finding)"
            severity = _normalize_scan_level(item.get("level"))
            row = f"{index}. {title}"
            if severity is not None:
                row += f" [{severity}]"
            preview.append(row)
        else:
            preview.append(f"{index}. {item}")
    remaining = len(_scan_findings(result)) - len(preview)
    if remaining > 0:
        preview.append(f"... and {remaining} more")
    return preview


def _scan_result_rows(result: dict[str, object]) -> list[str]:
    """Render concise per-finding result rows for one scan."""
    rows: list[str] = []
    for index, item in enumerate(_scan_findings(result), start=1):
        if isinstance(item, dict):
            title = _scalar_text(item.get("title")) or "(untitled finding)"
            severity = _normalize_scan_level(item.get("level"))
            row = f"{index}. {title}"
            if severity is not None:
                row += f" [{severity}]"
            rows.append(row)
        else:
            rows.append(f"{index}. {item}")
    if not rows:
        rows.append("No findings.")
    return rows


def _scan_detailed_finding_rows(result: dict[str, object]) -> list[str]:
    """Render full structured finding details for one scan."""
    rows: list[str] = []
    findings = _scan_findings(result)
    if not findings:
        return ["No detailed findings."]
    for index, item in enumerate(findings, start=1):
        if not isinstance(item, dict):
            if rows:
                rows.append("")
            rows.append(f"{index}. {item}")
            continue

        if rows:
            rows.append("")

        title = _scalar_text(item.get("title")) or "(untitled finding)"
        level = _normalize_scan_level(item.get("level"))
        risk_type = _scalar_text(item.get("risk_type"))
        description = _scalar_text(item.get("description"))
        suggestion = _scalar_text(item.get("suggestion"))

        rows.append(f"{index}. {title}")
        if level is not None:
            rows.append(f"Level: {level}")
        if risk_type is not None:
            rows.append(f"Risk type: {risk_type}")
        if description is not None:
            rows.append("Description:")
            for row in _scan_report_rows(description):
                rows.append(f"  {row}" if row else "")
        if suggestion is not None:
            rows.append("Suggestion:")
            for row in _scan_report_rows(suggestion):
                rows.append(f"  {row}" if row else "")
    return rows


def _scan_summary_rows(result: dict[str, object]) -> list[str]:
    """Build the standard summary rows for one scan result."""
    risk_levels = _scan_risk_levels(result)
    findings_count = _scan_findings_count(result)
    payload = _nested_scan_result_payload(result)
    score = _scalar_text(payload.get("score"))
    model = _scalar_text(payload.get("llm"))
    language = _scalar_text(payload.get("language"))

    rows = [
        f"Skill: {result.get('skill_name', '(unknown)')}",
        f"Path: {result.get('skill_path', '(unknown)')}",
        f"Session ID: {result.get('session_id', '(unknown)')}",
        f"Status: {result.get('status', '(unknown)')}",
    ]
    if score is not None:
        rows.append(f"Score: {score}")
    if findings_count is not None:
        rows.append(f"Findings: {findings_count}")
    if risk_levels:
        rows.append(f"Risk levels: {', '.join(risk_levels)}")
    if model is not None:
        rows.append(f"Model: {model}")
    if language is not None:
        rows.append(f"Language: {language}")
    return rows


def _skills_from_paths(paths: list[Path] | None) -> Skills:
    """Build a Skills collection from custom paths or the default Allskills instance."""
    return Skills(paths=paths) if paths else ALL_SKILLS()


def _registered_skills_or_exit(name: str) -> Skills:
    """Return one registered collection or exit with a CLI-friendly message."""
    try:
        return REGISTRY.get_skills(name)
    except KeyError as exc:
        raise SystemExit(str(exc)) from exc


def _format_install_error(exc: Exception, *, yes: bool) -> str:
    """Render install failures as concise CLI-facing messages."""
    if isinstance(exc, FileExistsError):
        lines = [f"install failed: {exc}"]
        if not yes:
            lines.append("Hint: rerun with -y/--yes to overwrite the existing skill directory.")
        lines.append("Hint: use -t/--target to install into a different directory.")
        return "\n".join(lines)
    if isinstance(exc, subprocess.CalledProcessError):
        command = exc.cmd if isinstance(exc.cmd, str) else " ".join(str(part) for part in exc.cmd)
        return f"install failed: command exited with status {exc.returncode}: {command}"
    return f"install failed: {exc}"


def _serialize_skills_instances(instances: list[Skills]) -> list[dict[str, object]]:
    """Convert named skills collections into JSON-safe payload."""
    payload = []
    for instance in instances:
        payload.append(
            {
                "name": instance.name,
                "skills_count": len(instance.skills),
                "paths": [str(path) for path in instance.paths],
                "tool_description": instance.tool_description,
                "cli_description": instance.cli_description,
                "agent_md_path": str(instance.agent_md_path),
            }
        )
    return payload


def _print_skills_instances(instances: list[Skills], *, json_output: bool) -> None:
    """Render named skills collections in text or JSON form."""
    if json_output:
        print(json.dumps(_serialize_skills_instances(instances), ensure_ascii=False, indent=2))
        return

    color = _supports_color_output()
    width = 96
    if not instances:
        print(
            "\n".join(
                _boxed_lines("MagicSkills Collections", ["No skills instances."], width=width, style="1;36", color=color)
            )
        )
        return

    total_skills = 0
    sections: list[str] = []
    sections.extend(
        _boxed_lines("MagicSkills Collections", [f"Total collections: {len(instances)}"], width=width, style="1;36", color=color)
    )
    for instance in instances:
        name = instance.name
        count = len(instance.skills)
        total_skills += count
        tool_description = inspect.cleandoc(instance.tool_description or "")
        tool_description_lines = tool_description.splitlines() or ["(none)"]
        cli_description = inspect.cleandoc(instance.cli_description or "")
        cli_description_lines = cli_description.splitlines() or ["(none)"]
        rows = [
            f"- name: {name}",
            f"skills: {count}",
            f"agent_md_path: {instance.agent_md_path}",
            f"paths: {', '.join(str(path) for path in instance.paths) if instance.paths else '(none)'}",
            f"tool_description: {tool_description_lines[0]}",
            *[f"  {line}" for line in tool_description_lines[1:]],
            f"cli_description: {cli_description_lines[0]}",
            *[f"  {line}" for line in cli_description_lines[1:]],
        ]
        sections.append("")
        sections.extend(_boxed_lines(f"Collection {name}", rows, width=width, style="1;33", color=color))

    sections.append("")
    sections.extend(
        _boxed_lines(
            "Summary",
            [
                f"Total collections: {len(instances)}",
                f"Total skills across collections: {total_skills}",
            ],
            width=width,
            style="1;35",
            color=color,
        )
    )
    print("\n".join(sections))


def _skill_list_from_args(values: Iterable[str] | None):
    """Resolve optional skill targets from Allskills into concrete Skill objects."""
    if not values:
        return None

    resolved = []
    seen_paths: set[Path] = set()
    for value in values:
        try:
            skill = ALL_SKILLS().get_skill(value)
        except KeyError as exc:
            message = str(exc)
            if "Multiple skills named" in message:
                raise SystemExit(
                    f"addskills: skill target '{value}' is duplicated; pass skill directory path.\n{message}"
                ) from exc
            raise SystemExit(f"addskills: skill target not found: {value}") from exc

        resolved_path = skill.path.expanduser().resolve()
        if resolved_path in seen_paths:
            continue
        seen_paths.add(resolved_path)
        resolved.append(skill)
    return resolved


def cmd_list(args: argparse.Namespace) -> int:
    """List available skills."""
    skills = _registered_skills_or_exit(args.name) if args.name else ALL_SKILLS()
    print(command_listskill(skills))
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    """Read one file by path or by skill name (reads SKILL.md from Allskills)."""
    try:
        print(command_readskill(ALL_SKILLS(), args.path))
    except (KeyError, ValueError, FileNotFoundError, OSError) as exc:
        raise SystemExit(str(exc)) from exc
    return 0


def cmd_exec(args: argparse.Namespace) -> int:
    """Execute one command in current collection context.

    Default behavior streams output directly to the current terminal.
    """
    paths = _paths_from_args(args.paths)
    skills = _skills_from_paths(paths)
    command_parts = list(args.command)
    if command_parts and command_parts[0] == "--":
        command_parts = command_parts[1:]
    command = " ".join(command_parts).strip()
    if not command:
        raise SystemExit("exec requires command after --")
    stream = not args.json
    result = command_execskill(skills, command, shell=not args.no_shell, stream=stream)
    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    return result.returncode


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync skills XML section into AGENTS.md (or custom output)."""
    skills = _registered_skills_or_exit(args.name)
    if not args.yes:
        confirm = input(f"Sync {len(skills.skills)} skills to {args.output or skills.agent_md_path}? [y/N] ")
        if confirm.strip().lower() not in {"y", "yes"}:
            print("Cancelled.")
            return 1
    output = command_syncskills(skills, args.output, mode=args.mode)
    print(f"Synced to {output}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    """Install skills from repo/local source into configured scope."""
    if args.target and (args.global_scope or args.universal):
        raise SystemExit("--target cannot be used with --global or --universal")
    try:
        installed = install(
            args.source,
            global_=args.global_scope,
            universal=args.universal,
            yes=args.yes,
            target_root=args.target,
        )
    except (FileExistsError, FileNotFoundError, ValueError, subprocess.CalledProcessError, OSError) as exc:
        raise SystemExit(_format_install_error(exc, yes=args.yes)) from exc
    for path in installed:
        print(f"Installed: {path}")
    return 0


def cmd_add_skill(args: argparse.Namespace) -> int:
    """Register one skill by target(name or path) into one collection."""
    skills = _registered_skills_or_exit(args.name) if args.name else ALL_SKILLS()
    path = command_addskill(skills, target=args.target, source=args.source)
    print(f"Registered: {path}")
    return 0


def cmd_create_skill_template(args: argparse.Namespace) -> int:
    """Create a standard skill scaffold under one base directory."""
    path = command_createskill_template(args.name, args.base_dir)
    print(f"Created template: {path}")
    return 0


def _configure_add_skill_parser(parser: argparse.ArgumentParser) -> None:
    """Configure args for `addskill`."""
    parser.add_argument("target", help="Skill directory path or skill name from Allskills")
    parser.add_argument("--source", help="Install/discovery source to store in Skill metadata")
    parser.add_argument("--name", help="Target named skills collection (default: Allskills)")
    parser.set_defaults(func=cmd_add_skill)


def cmd_upload_skill(args: argparse.Namespace) -> int:
    """Upload one skill with default fork -> push -> PR workflow."""
    for attempt in range(4):
        try:
            result = command_uploadskill(ALL_SKILLS(), args.source)
            break
        except (KeyError, ValueError, FileNotFoundError) as exc:
            raise SystemExit(str(exc)) from exc
        except RuntimeError as exc:
            if _is_gh_missing_error(exc) and _maybe_install_gh_for_upload():
                continue
            if _is_gh_auth_error(exc) and _maybe_login_gh_for_upload():
                continue
            raise SystemExit(str(exc)) from exc
    print(f"Uploaded: {result.skill_name}")
    print(f"Repo: {result.repo}")
    print(f"Branch: {result.branch}")
    print(f"Target: {result.remote_subpath}")
    print(f"Committed: {result.committed}")
    print(f"Pushed: {result.pushed}")
    if result.push_remote:
        print(f"Push remote: {result.push_remote}")
    if result.push_branch:
        print(f"Push branch: {result.push_branch}")
    if result.pr_url:
        print(f"PR URL: {result.pr_url}")
    if result.pr_created:
        print("PR Created: True")
    return 0


def cmd_delete_skill(args: argparse.Namespace) -> int:
    """Delete skill by one unified target argument: name or path."""
    skills = _registered_skills_or_exit(args.name) if args.name else ALL_SKILLS()
    try:
        path = command_deleteskill(skills, str(args.target))
    except (KeyError, ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc

    print(f"Deleted: {path}")
    return 0


def cmd_show_skill(args: argparse.Namespace) -> int:
    """Show all files/content for one skill from Allskills by name or path target."""
    raw_target = str(args.target).strip()
    if not raw_target:
        raise SystemExit("showskill requires target: <name-or-path>")
    try:
        print(command_showskill(ALL_SKILLS(), raw_target))
    except (KeyError, ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
    return 0


def cmd_add_skills(args: argparse.Namespace) -> int:
    """Create one named skills collection instance."""
    paths = _paths_from_args(args.paths)
    skill_list = _skill_list_from_args(args.skill_list)
    if paths and skill_list:
        raise SystemExit("--paths cannot be used with --skill-list")
    path_values = [str(path) for path in paths] if paths else None
    try:
        instance = command_addskills(
            name=args.name,
            skill_list=skill_list,
            paths=path_values,
            tool_description=args.tool_description,
            cli_description=args.cli_description,
            agent_md_path=args.agent_md_path,
        )
    except (KeyError, ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
    print(f"Created skills instance: {instance.name}")
    print(f"Skills count: {len(instance.skills)}")
    return 0


def cmd_list_skills_instances(args: argparse.Namespace) -> int:
    """List registered named skills collection instances."""
    instances = command_listskills()
    _print_skills_instances(instances, json_output=args.json)
    return 0


def cmd_load_skills(args: argparse.Namespace) -> int:
    """Load registry state from disk and display loaded collections."""
    instances = command_loadskills(args.path)
    _print_skills_instances(instances, json_output=args.json)
    return 0


def cmd_delete_skills_instance(args: argparse.Namespace) -> int:
    """Delete one or more named skills collection instances."""
    try:
        command_deleteskills(*args.names)
    except (KeyError, ValueError) as exc:
        message = exc.args[0] if exc.args else str(exc)
        raise SystemExit(message) from exc
    if len(args.names) == 1:
        print(f"Deleted skills instance: {args.names[0]}")
    else:
        print(f"Deleted skills instances: {', '.join(args.names)}")
    return 0


def cmd_save_skills(args: argparse.Namespace) -> int:
    """Persist registry state to disk."""
    print(command_saveskills(args.path))
    return 0


def cmd_change_tool_description(args: argparse.Namespace) -> int:
    """Update tool description for a named collection."""
    instance = _registered_skills_or_exit(args.name)
    command_change_tool_description(instance, args.description)
    print(f"Updated tool description for skills instance: {args.name}")
    return 0


def cmd_change_cli_description(args: argparse.Namespace) -> int:
    """Update CLI description for a named collection."""
    instance = _registered_skills_or_exit(args.name)
    command_change_cli_description(instance, args.description)
    print(f"Updated CLI description for skills instance: {args.name}")
    return 0


def cmd_skill_tool(args: argparse.Namespace) -> int:
    """Run skill_tool compatible action from CLI."""
    if args.name:
        skills = _registered_skills_or_exit(args.name)
    else:
        skills = ALL_SKILLS()
    result = command_skill_tool(skills, args.action, args.arg)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


def _format_scan_result(
    result: dict[str, object],
    *,
    color: bool | None = None,
    width: int | None = None,
) -> str:
    findings_count = _scan_findings_count(result)

    color = _resolve_scan_color(color)
    width = _scan_output_width() if width is None else width
    sections: list[str] = []

    status_style = "1;32" if findings_count in {None, 0} else "1;33"
    sections.extend(_boxed_lines("Skill Summary", _scan_summary_rows(result), width=width, style=status_style, color=color))

    sections.append("")
    sections.extend(_boxed_lines("Skill Results", _scan_result_rows(result), width=width, style="1;31", color=color))

    return "\n".join(sections)


def _format_scan_details(
    result: dict[str, object],
    *,
    prefix: str = "Skill",
    color: bool | None = None,
    width: int | None = None,
) -> str:
    """Render formatted detailed sections for one scan result."""
    color = _resolve_scan_color(color)
    width = _scan_output_width() if width is None else width
    sections: list[str] = []
    payload = _nested_scan_result_payload(result)
    report = _scalar_text(payload.get("readme"))
    detail_rows = _scan_detailed_finding_rows(result)
    skill_name = str(result.get("skill_name", "(unknown)"))

    report_rows = _scan_report_rows(report or "")
    if report_rows:
        sections.extend(
            _boxed_lines(
                f"{prefix} Report {skill_name}",
                report_rows,
                width=width,
                style="1;36",
                color=color,
            )
        )

    if detail_rows:
        if sections:
            sections.append("")
        sections.extend(
            _boxed_lines(
                f"{prefix} Finding Details {skill_name}",
                detail_rows,
                width=width,
                style="1;31",
                color=color,
            )
        )

    return "\n".join(sections)


def _format_scanskills_result(result: dict[str, object], *, color: bool | None = None, width: int | None = None) -> str:
    color = _resolve_scan_color(color)
    width = _scan_output_width() if width is None else width
    sections: list[str] = []
    items = [item for item in result.get("results", []) if isinstance(item, dict)]
    successful_items = [item for item in items if item.get("ok")]

    total_findings = 0
    skills_with_findings = 0
    scores: list[float] = []
    for item in successful_items:
        findings_count = _scan_findings_count(item)
        if findings_count is not None:
            total_findings += findings_count
            if findings_count > 0:
                skills_with_findings += 1
        payload = _nested_scan_result_payload(item)
        score_value = payload.get("score")
        if isinstance(score_value, (int, float)):
            scores.append(float(score_value))

    summary_rows = [
        f"Collection: {result.get('collection_name', '(unknown)')}",
        f"Total skills: {result.get('total_skills', 0)}",
        f"Succeeded: {result.get('succeeded', 0)}",
        f"Failed: {result.get('failed', 0)}",
        f"Findings across successful scans: {total_findings}",
        f"Skills with findings: {skills_with_findings}",
    ]
    if scores:
        average_score = sum(scores) / len(scores)
        summary_rows.append(f"Average score: {average_score:.1f}")
    sections.extend(_boxed_lines("Skills Summary", summary_rows, width=width, style="1;36", color=color))

    result_rows: list[str] = []
    for item in items:
        skill_name = str(item.get("skill_name", "(unknown)"))
        if item.get("ok"):
            detail_parts = [str(item.get("status", "completed"))]
            payload = _nested_scan_result_payload(item)
            score = _scalar_text(payload.get("score"))
            findings_count = _scan_findings_count(item)
            risk_levels = _scan_risk_levels(item)
            if score is not None:
                detail_parts.append(f"score={score}")
            if findings_count is not None:
                detail_parts.append(f"findings={findings_count}")
            if risk_levels:
                detail_parts.append(f"risks={', '.join(risk_levels)}")
            result_rows.append(f"- {skill_name}: {' | '.join(detail_parts)}")
        else:
            result_rows.append(f"- {skill_name}: failed")

    if result_rows:
        sections.append("")
        sections.extend(_boxed_lines("Skills Results", result_rows, width=width, style="1;35", color=color))

    return "\n".join(sections)


def _format_scanskills_details(
    result: dict[str, object],
    *,
    color: bool | None = None,
    width: int | None = None,
) -> str:
    """Render formatted detailed sections for each successful scan in one collection."""
    color = _resolve_scan_color(color)
    width = _scan_output_width() if width is None else width
    items = [item for item in result.get("results", []) if isinstance(item, dict)]
    successful_items = [item for item in items if item.get("ok")]
    sections: list[str] = []
    for item in successful_items:
        detail = _format_scan_details(item, color=color, width=width)
        if not detail:
            continue
        if sections:
            sections.append("")
        sections.append(detail)
    return "\n".join(sections)


def _format_saved_scan_output(result: dict[str, object]) -> str:
    """Render the text saved by `--save-raw`: summary plus formatted details."""
    width = 112
    if isinstance(result.get("collection_name"), str):
        summary = _format_scanskills_result(result, color=False, width=width)
        details = _format_scanskills_details(result, color=False, width=width)
    else:
        summary = _format_scan_result(result, color=False, width=width)
        details = _format_scan_details(result, color=False, width=width)
    if details:
        return f"{summary}\n\n{details}"
    return summary


def cmd_scan_skill(args: argparse.Namespace) -> int:
    """Scan one skill by skill name or skill directory path."""
    scan_kwargs = _scan_kwargs_from_args(args)
    target: object
    if _looks_like_path_input(args.target):
        target = args.target
    else:
        skills = _registered_skills_or_exit(args.name) if args.name else ALL_SKILLS()
        try:
            target = skills.get_skill(args.target)
        except KeyError as exc:
            raise SystemExit(str(exc)) from exc

    try:
        result = command_scanskill(target, **scan_kwargs)
    except (ValueError, FileNotFoundError, RuntimeError, TimeoutError) as exc:
        raise SystemExit(str(exc)) from exc

    print(_format_scan_result(result))
    if args.details:
        print("")
        print(_format_scan_details(result))
    if args.save_raw is not None:
        saved_path = _save_scan_result(result, args.save_raw)
        print(f"Raw result saved: {saved_path}")
    return 0


def cmd_scan_skills(args: argparse.Namespace) -> int:
    """Scan every skill in one named skills collection."""
    skills = _registered_skills_or_exit(args.name)
    try:
        result = command_scanskills(
            skills,
            **_scan_kwargs_from_args(args),
        )
    except (ValueError, FileNotFoundError, RuntimeError, TimeoutError) as exc:
        raise SystemExit(str(exc)) from exc

    print(_format_scanskills_result(result))
    if args.details:
        print("")
        print(_format_scanskills_details(result))
    if args.save_raw is not None:
        saved_path = _save_scan_result(result, args.save_raw)
        print(f"Raw result saved: {saved_path}")
    return 0 if result.get("ok") else 1


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser with all supported commands."""
    parser = argparse.ArgumentParser(prog="magicskills")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("listskill", help="List skills from Allskills or one named skills collection")
    p_list.add_argument("--name", help="Skills collection name shown by listskills")
    p_list.set_defaults(func=cmd_list)

    p_read = sub.add_parser("readskill", help="Read by file path or skill name")
    p_read.add_argument("path", help="File path or skill name")
    p_read.set_defaults(func=cmd_read)

    p_exec = sub.add_parser("execskill", help="Execute command")
    p_exec.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --")
    p_exec.add_argument("--no-shell", action="store_true", help="Run without shell")
    p_exec.add_argument("--json", action="store_true", help="Output JSON result")
    p_exec.add_argument("--paths", nargs="*", help="Custom skill search paths")
    p_exec.set_defaults(func=cmd_exec)

    p_sync = sub.add_parser("syncskills", help="Sync skills into AGENTS.md")
    p_sync.add_argument("name", help="Skills instance name")
    p_sync.add_argument("-o", "--output", help="Output path (default: AGENTS.md)")
    p_sync.add_argument(
        "--mode",
        default="none",
        choices=SYNC_MODES,
        help="Sync mode: keep original skills block, or render only CLI description",
    )
    p_sync.add_argument("-y", "--yes", action="store_true", help="Non-interactive")
    p_sync.set_defaults(func=cmd_sync)

    p_install = sub.add_parser("install", help="Install skills or skill from source or by skill name")
    p_install.add_argument("source", help="GitHub repo (owner/repo), git URL, local path, or skill name")
    p_install.add_argument("--global", dest="global_scope", action="store_true", help="Install to global scope")
    p_install.add_argument("--universal", action="store_true", help="Install to .agent/skills")
    p_install.add_argument(
        "-t",
        "--target",
        help="Custom install target directory (cannot be used with --global/--universal)",
    )
    p_install.add_argument("-y", "--yes", action="store_true", help="Overwrite without prompt")
    p_install.set_defaults(func=cmd_install)

    p_add = sub.add_parser("addskill", help="Register one skill into one collection")
    _configure_add_skill_parser(p_add)

    p_create_template = sub.add_parser("createskill_template", help="Create a standard skill scaffold")
    p_create_template.add_argument("name", help="Skill name")
    p_create_template.add_argument("base_dir", help="Skills root directory")
    p_create_template.set_defaults(func=cmd_create_skill_template)

    p_upload = sub.add_parser("uploadskill", help="Upload one skill to repository (default settings)")
    p_upload.add_argument("source", help="Skill name (Allskills) or local skill directory path")
    p_upload.set_defaults(func=cmd_upload_skill)

    p_delete = sub.add_parser("deleteskill", help="Delete a skill by one target (name or path)")
    p_delete.add_argument("target", help="Skill name or skill directory path")
    p_delete.add_argument("--name", help="Target named skills collection (default: Allskills)")
    p_delete.set_defaults(func=cmd_delete_skill)

    p_show = sub.add_parser("showskill", help="Show all content for one skill from Allskills")
    p_show.add_argument("target", help="Skill name or skill directory path")
    p_show.set_defaults(func=cmd_show_skill)

    p_add_skills = sub.add_parser("addskills", help="Create a named skills collection")
    p_add_skills.add_argument("name", help="Skills instance name")
    p_add_skills.add_argument(
        "--skill-list",
        nargs="*",
        help="Specific skills (name or skill directory path) for this collection",
    )
    p_add_skills.add_argument("--paths", nargs="*", help="Custom paths for this collection")
    p_add_skills.add_argument("--tool-description", help="Tool description override")
    p_add_skills.add_argument("--cli-description", help="CLI description override")
    p_add_skills.add_argument("--agent-md-path", help="AGENTS.md path override")
    p_add_skills.set_defaults(func=cmd_add_skills)

    p_list_skills = sub.add_parser("listskills", help="List named skills collections")
    p_list_skills.add_argument("--json", action="store_true", help="JSON output")
    p_list_skills.set_defaults(func=cmd_list_skills_instances)

    p_load_skills = sub.add_parser("loadskills", help="Load registry from disk")
    p_load_skills.add_argument("path", nargs="?", help="Optional registry file path")
    p_load_skills.add_argument("--json", action="store_true", help="JSON output")
    p_load_skills.set_defaults(func=cmd_load_skills)

    p_delete_skills = sub.add_parser("deleteskills", help="Delete one or more named skills collections")
    p_delete_skills.add_argument("names", nargs="+", help="One or more skills instance names")
    p_delete_skills.set_defaults(func=cmd_delete_skills_instance)

    p_save_skills = sub.add_parser("saveskills", help="Persist registry to disk")
    p_save_skills.add_argument("path", nargs="?", help="Optional save output path")
    p_save_skills.set_defaults(func=cmd_save_skills)


    p_change_desc = sub.add_parser("changetooldescription", help="Update tool description on a skills collection")
    p_change_desc.add_argument("name", help="Skills instance name")
    p_change_desc.add_argument("description", help="New tool description")
    p_change_desc.set_defaults(func=cmd_change_tool_description)

    p_change_cli_desc = sub.add_parser("changeclidescription", help="Update CLI description on a skills collection")
    p_change_cli_desc.add_argument("name", help="Skills instance name")
    p_change_cli_desc.add_argument("description", help="New CLI description")
    p_change_cli_desc.set_defaults(func=cmd_change_cli_description)

    p_tool = sub.add_parser("skill-tool", help="Run skill_tool action")
    p_tool.add_argument("action", help="Action name")
    p_tool.add_argument("--arg", default="", help="Action argument")
    p_tool.add_argument("--name", help="Use a named skills instance")
    p_tool.set_defaults(func=cmd_skill_tool)

    p_scan = sub.add_parser("scanskill", help="Scan one skill with AI-Infra-Guard")
    p_scan.add_argument("target", help="Skill name or skill directory path")
    p_scan.add_argument("--name", help="Resolve skill name from a named skills collection (default: Allskills)")
    _add_visible_scan_args(p_scan)
    _add_hidden_scan_args(p_scan)
    p_scan.add_argument(
        "--save-raw",
        nargs="?",
        const="",
        help="Save formatted detailed scan output to a file; optionally provide a path",
    )
    p_scan.add_argument("--details", action="store_true", help="Print formatted detailed scan output after the summary")
    p_scan.set_defaults(func=cmd_scan_skill)

    p_scan_all = sub.add_parser("scanskills", help="Scan all skills in a named collection with AI-Infra-Guard")
    p_scan_all.add_argument("name", help="Skills instance name")
    _add_visible_scan_args(p_scan_all)
    _add_hidden_scan_args(p_scan_all)
    p_scan_all.add_argument(
        "--save-raw",
        nargs="?",
        const="",
        help="Save formatted detailed scan output to a file; optionally provide a path",
    )
    p_scan_all.add_argument("--details", action="store_true", help="Print formatted detailed scan output after the summary")
    p_scan_all.set_defaults(func=cmd_scan_skills)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
