"""Helpers for scanning skill directories with AI-Infra-Guard."""

from __future__ import annotations

import json
import mimetypes
import os
import tempfile
import time
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_AIG_PROMPT = (
    "Scan this uploaded source tree as an Agent Skill package. Focus on risky command execution, "
    "prompt or tool poisoning, secret leakage, data exfiltration, unsafe file access, and other "
    "security issues relevant to reusable agent skills."
)


@dataclass(frozen=True)
class AIInfraGuardConfig:
    """Resolved runtime configuration for one A.I.G scan."""

    base_url: str
    model: str
    token: str
    model_base_url: str | None
    language: str
    thread: int
    prompt: str
    poll_interval: float
    timeout: float
    headers: dict[str, str]


def _normalize_base_url(value: str) -> str:
    normalized = value.strip().rstrip("/")
    if not normalized:
        raise ValueError("AI-Infra-Guard base URL cannot be empty")
    return normalized


def _parse_int(value: str | int | None, *, name: str, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be greater than 0")
    return parsed


def _parse_float(value: str | float | int | None, *, name: str, default: float) -> float:
    if value is None:
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be greater than 0")
    return parsed


def _headers_from_env() -> dict[str, str]:
    raw = os.environ.get("MAGICSKILLS_AIG_HEADERS", "").strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("MAGICSKILLS_AIG_HEADERS must be a JSON object") from exc
    if not isinstance(parsed, dict):
        raise ValueError("MAGICSKILLS_AIG_HEADERS must be a JSON object")
    result: dict[str, str] = {}
    for key, value in parsed.items():
        result[str(key)] = str(value)
    return result


def resolve_ai_infra_guard_config(
    *,
    base_url: str | None = None,
    model: str | None = None,
    token: str | None = None,
    model_base_url: str | None = None,
    prompt: str | None = None,
    language: str | None = None,
    thread: int | None = None,
    poll_interval: float | None = None,
    timeout: float | None = None,
    headers: Mapping[str, str] | None = None,
) -> AIInfraGuardConfig:
    """Resolve scan configuration from explicit args first, then env vars."""
    resolved_base_url = base_url or os.environ.get("MAGICSKILLS_AIG_BASE_URL")
    if not resolved_base_url:
        raise ValueError(
            "AI-Infra-Guard base URL is required. Pass --base-url or set MAGICSKILLS_AIG_BASE_URL."
        )

    resolved_model = model or os.environ.get("MAGICSKILLS_AIG_MODEL")
    if not resolved_model:
        raise ValueError("A.I.G model is required. Pass --model or set MAGICSKILLS_AIG_MODEL.")

    resolved_token = token or os.environ.get("MAGICSKILLS_AIG_TOKEN")
    if not resolved_token:
        raise ValueError("A.I.G model token is required. Pass --token or set MAGICSKILLS_AIG_TOKEN.")

    resolved_model_base_url = model_base_url or os.environ.get("MAGICSKILLS_AIG_MODEL_BASE_URL") or None
    resolved_language = (language or os.environ.get("MAGICSKILLS_AIG_LANGUAGE") or "en").strip() or "en"
    resolved_prompt = (prompt or os.environ.get("MAGICSKILLS_AIG_PROMPT") or DEFAULT_AIG_PROMPT).strip()
    resolved_thread = _parse_int(
        thread if thread is not None else os.environ.get("MAGICSKILLS_AIG_THREAD"),
        name="thread",
        default=4,
    )
    resolved_poll_interval = _parse_float(
        poll_interval if poll_interval is not None else os.environ.get("MAGICSKILLS_AIG_POLL_INTERVAL"),
        name="poll_interval",
        default=10.0,
    )
    resolved_timeout = _parse_float(
        timeout if timeout is not None else os.environ.get("MAGICSKILLS_AIG_TIMEOUT"),
        name="timeout",
        default=600.0,
    )

    resolved_headers = dict(_headers_from_env())
    if headers:
        resolved_headers.update({str(key): str(value) for key, value in headers.items()})

    return AIInfraGuardConfig(
        base_url=_normalize_base_url(resolved_base_url),
        model=resolved_model.strip(),
        token=resolved_token.strip(),
        model_base_url=resolved_model_base_url.strip() if resolved_model_base_url else None,
        language=resolved_language,
        thread=resolved_thread,
        prompt=resolved_prompt,
        poll_interval=resolved_poll_interval,
        timeout=resolved_timeout,
        headers=resolved_headers,
    )


def _request_json(
    method: str,
    url: str,
    *,
    body: bytes | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: float,
) -> dict[str, Any]:
    request_headers = {str(key): str(value) for key, value in (headers or {}).items()}
    req = Request(url, data=body, headers=request_headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"AI-Infra-Guard request failed: {method} {url} -> {exc.code} {exc.reason}: {details}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to connect to AI-Infra-Guard at {url}: {exc.reason}") from exc

    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"AI-Infra-Guard returned non-JSON response for {method} {url}") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(f"AI-Infra-Guard returned invalid JSON payload for {method} {url}")
    return parsed


def _request_json_checked(
    method: str,
    url: str,
    *,
    body: bytes | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: float,
) -> dict[str, Any]:
    payload = _request_json(method, url, body=body, headers=headers, timeout=timeout)
    if payload.get("status") != 0:
        raise RuntimeError(
            f"AI-Infra-Guard request failed for {method} {url}: {payload.get('message', 'unknown error')}"
        )
    return payload


def _create_skill_archive(skill_dir: Path, destination: Path) -> Path:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skill_dir.rglob("*")):
            if path.is_dir():
                continue
            arcname = Path(skill_dir.name) / path.relative_to(skill_dir)
            archive.write(path, arcname=str(arcname))
    return destination


def _encode_multipart_form(field_name: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----MagicSkillsBoundary{uuid.uuid4().hex}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()
    parts = [
        f"--{boundary}\r\n".encode("utf-8"),
        (
            f'Content-Disposition: form-data; name="{field_name}"; filename="{file_path.name}"\r\n'
        ).encode("utf-8"),
        f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def _upload_archive(archive_path: Path, config: AIInfraGuardConfig) -> str:
    body, content_type = _encode_multipart_form("file", archive_path)
    headers = dict(config.headers)
    headers["Content-Type"] = content_type
    payload = _request_json_checked(
        "POST",
        f"{config.base_url}/api/v1/app/taskapi/upload",
        body=body,
        headers=headers,
        timeout=config.timeout,
    )
    data = payload.get("data")
    if not isinstance(data, dict) or not data.get("fileUrl"):
        raise RuntimeError("AI-Infra-Guard upload response is missing data.fileUrl")
    return str(data["fileUrl"])


def _create_scan_task(file_url: str, config: AIInfraGuardConfig) -> str:
    model_payload: dict[str, Any] = {
        "model": config.model,
        "token": config.token,
    }
    if config.model_base_url:
        model_payload["base_url"] = config.model_base_url

    body = json.dumps(
        {
            "type": "mcp_scan",
            "content": {
                "prompt": config.prompt,
                "model": model_payload,
                "thread": config.thread,
                "language": config.language,
                "attachments": file_url,
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")
    headers = dict(config.headers)
    headers["Content-Type"] = "application/json"
    payload = _request_json_checked(
        "POST",
        f"{config.base_url}/api/v1/app/taskapi/tasks",
        body=body,
        headers=headers,
        timeout=config.timeout,
    )
    data = payload.get("data")
    if not isinstance(data, dict) or not data.get("session_id"):
        raise RuntimeError("AI-Infra-Guard task creation response is missing data.session_id")
    return str(data["session_id"])


def _poll_task(session_id: str, config: AIInfraGuardConfig) -> dict[str, Any]:
    deadline = time.monotonic() + config.timeout
    status_url = f"{config.base_url}/api/v1/app/taskapi/status/{session_id}"
    headers = dict(config.headers)
    while True:
        if time.monotonic() > deadline:
            raise TimeoutError(f"Timed out while waiting for AI-Infra-Guard scan task {session_id}")

        payload = _request_json_checked("GET", status_url, headers=headers, timeout=config.timeout)
        data = payload.get("data")
        if not isinstance(data, dict):
            raise RuntimeError("AI-Infra-Guard task status response is missing data object")

        status = str(data.get("status", "")).strip().lower()
        if status == "completed":
            return data
        if status == "failed":
            log = str(data.get("log", "")).strip()
            raise RuntimeError(f"AI-Infra-Guard scan task {session_id} failed: {log or 'no log provided'}")

        time.sleep(config.poll_interval)


def _fetch_task_result(session_id: str, config: AIInfraGuardConfig) -> Any:
    payload = _request_json_checked(
        "GET",
        f"{config.base_url}/api/v1/app/taskapi/result/{session_id}",
        headers=config.headers,
        timeout=config.timeout,
    )
    return payload.get("data")


def _walk_nodes(node: Any) -> Iterable[Any]:
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_nodes(value)


def _find_first_scalar_by_keys(node: Any, keys: set[str]) -> str | None:
    if isinstance(node, dict):
        for key, value in node.items():
            normalized = str(key).replace("-", "").replace("_", "").lower()
            if normalized in keys and isinstance(value, (str, int, float)):
                return str(value)
        for value in node.values():
            found = _find_first_scalar_by_keys(value, keys)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = _find_first_scalar_by_keys(value, keys)
            if found is not None:
                return found
    return None


def _infer_findings_count(node: Any) -> int | None:
    list_keys = {
        "vulnerabilities",
        "findings",
        "issues",
        "risks",
        "alerts",
        "problems",
    }
    scalar_keys = {
        "vulnerabilitycount",
        "findingcount",
        "issuecount",
        "riskcount",
        "alertcount",
    }
    if isinstance(node, dict):
        for key, value in node.items():
            normalized = str(key).replace("-", "").replace("_", "").lower()
            if normalized in list_keys and isinstance(value, list):
                return len(value)
            if normalized in scalar_keys and isinstance(value, int):
                return value
        for value in node.values():
            inferred = _infer_findings_count(value)
            if inferred is not None:
                return inferred
    elif isinstance(node, list):
        for value in node:
            inferred = _infer_findings_count(value)
            if inferred is not None:
                return inferred
    return None


def summarize_scan_result(result: Any) -> dict[str, object]:
    """Extract a lightweight summary from the raw A.I.G result payload."""
    risk_level = _find_first_scalar_by_keys(
        result,
        {
            "risklevel",
            "severity",
            "risk",
            "level",
        },
    )
    findings_count = _infer_findings_count(result)
    return {
        "risk_level": risk_level,
        "findings_count": findings_count,
    }


def scan_skill_directory(
    skill_dir: Path,
    *,
    skill_name: str,
    config: AIInfraGuardConfig,
) -> dict[str, object]:
    """Upload one skill directory to A.I.G, trigger a scan, and fetch the result."""
    resolved_skill_dir = skill_dir.expanduser().resolve()
    with tempfile.TemporaryDirectory(prefix="magicskills-aig-") as tmp:
        archive_path = Path(tmp) / f"{resolved_skill_dir.name}.zip"
        _create_skill_archive(resolved_skill_dir, archive_path)
        file_url = _upload_archive(archive_path, config)
        session_id = _create_scan_task(file_url, config)
        status_data = _poll_task(session_id, config)
        result_data = _fetch_task_result(session_id, config)

    return {
        "ok": True,
        "skill_name": skill_name,
        "skill_path": str(resolved_skill_dir),
        "task_type": "mcp_scan",
        "session_id": session_id,
        "upload_url": file_url,
        "status": str(status_data.get("status", "completed")),
        "task_log": status_data.get("log", ""),
        "summary": summarize_scan_result(result_data),
        "result": result_data,
    }


__all__ = [
    "AIInfraGuardConfig",
    "DEFAULT_AIG_PROMPT",
    "resolve_ai_infra_guard_config",
    "scan_skill_directory",
    "summarize_scan_result",
]
