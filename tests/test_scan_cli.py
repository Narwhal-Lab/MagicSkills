from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

import pytest

from magicskills.cli import (
    _boxed_lines,
    _display_width,
    build_parser,
    _format_scan_result,
    _format_scanskills_result,
    _save_scan_result,
    _scan_report_rows,
    _scan_risk_level,
    cmd_scan_skill,
    cmd_scan_skills,
)
from magicskills.utils.ai_infra_guard import AIInfraGuardConfig, resolve_ai_infra_guard_config, _poll_task, summarize_scan_result


def test_scanskill_help_prefers_api_key_and_hides_advanced_flags(capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["scanskill", "-h"])
    output = capsys.readouterr().out

    assert "--api-key" in output
    assert "--token" not in output
    assert "--prompt" not in output
    assert "--language" not in output
    assert "--thread" not in output
    assert "--poll-interval" not in output
    assert "--timeout" not in output
    assert "--header" not in output
    assert "--save-raw" in output
    assert "--details" in output
    assert "--json" not in output


def test_scanskill_parser_accepts_new_and_legacy_api_key_flags() -> None:
    parser = build_parser()

    args = parser.parse_args(["scanskill", "demo-skill", "--api-key", "new-key"])
    assert args.api_key == "new-key"

    legacy_args = parser.parse_args(["scanskill", "demo-skill", "--token", "old-key"])
    assert legacy_args.api_key == "old-key"


def test_resolve_ai_infra_guard_config_prefers_new_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAGICSKILLS_AIG_BASE_URL", "http://localhost:8088")
    monkeypatch.setenv("MAGICSKILLS_AIG_MODEL", "qwen3-max")
    monkeypatch.setenv("MAGICSKILLS_AIG_API_KEY", "new-key")
    monkeypatch.setenv("MAGICSKILLS_AIG_TOKEN", "old-key")

    config = resolve_ai_infra_guard_config()

    assert config.token == "new-key"


def test_poll_task_accepts_done_status() -> None:
    config = AIInfraGuardConfig(
        base_url="http://localhost:8088",
        model="qwen3-max",
        token="secret",
        model_base_url=None,
        language="zh",
        thread=4,
        prompt="scan",
        poll_interval=0.01,
        timeout=1.0,
        headers={},
    )

    with patch(
        "magicskills.utils.ai_infra_guard._request_json_checked",
        return_value={"data": {"status": "done", "log": "ok"}},
    ):
        result = _poll_task("session-1", config)

    assert result["status"] == "done"


def test_format_scan_result_renders_summary_and_structured_results_only() -> None:
    formatted = _format_scan_result(
        {
            "ok": True,
            "skill_name": "test-skill",
            "skill_path": "/root/test-skill",
            "session_id": "session-1",
            "status": "done",
            "task_log": "very noisy raw log",
            "summary": {"findings_count": 0, "risk_level": None},
            "result": {
                "id": "result-1",
                "type": "resultUpdate",
                "timestamp": 1,
                "result": {
                    "score": 100,
                    "language": "Other",
                    "llm": "qwen3-max",
                    "readme": "# Report\n\n## 结论\n未发现任何安全风险。\n建议后续加入代码后重新扫描。\n",
                    "results": [
                        {"title": "危险命令执行", "level": "HIGH"},
                        {"title": "路径遍历", "level": "MEDIUM"},
                    ],
                },
            },
        }
    )

    assert "Skill Summary" in formatted
    assert "Skill Results" in formatted
    assert "Score: 100" in formatted
    assert "Findings: 2" in formatted
    assert "Risk levels: HIGH, MEDIUM" in formatted
    assert "Model: qwen3-max" in formatted
    assert "1. 危险命令执行 [HIGH]" in formatted
    assert "2. 路径遍历 [MEDIUM]" in formatted
    assert "Task log" not in formatted
    assert "Report" not in formatted
    assert "结论" not in formatted


def test_summarize_scan_result_uses_strict_results_schema() -> None:
    summary = summarize_scan_result(
        {
            "id": "result-1",
            "type": "resultUpdate",
            "timestamp": 1,
            "result": {
                "score": 10,
                "level": "LOW",
                "results": [
                    {"title": "first", "level": "MEDIUM"},
                    {"title": "second", "level": "HIGH"},
                ],
            },
        }
    )

    assert summary == {
        "risk_level": "HIGH",
        "findings_count": 2,
    }


def test_summarize_scan_result_ignores_non_results_level_fields() -> None:
    summary = summarize_scan_result(
        {
            "level": "CRITICAL",
            "result": {
                "readme": "risk level: high",
                "results": [],
            },
        }
    )

    assert summary == {
        "risk_level": None,
        "findings_count": 0,
    }


def test_scan_report_rows_merges_soft_wrapped_markdown_lines() -> None:
    rows = _scan_report_rows(
        "# 标题\n\n## 总结\n该Agent\nSkill包实现了复杂的电子表格处理功能。\n\n```python\nprint('x')\n```\n"
    )

    assert rows == [
        "标题",
        "",
        "总结",
        "该Agent Skill包实现了复杂的电子表格处理功能。",
        "",
        "[python]",
        "    print('x')",
    ]


def test_boxed_lines_respect_display_width_for_cjk_text() -> None:
    lines = _boxed_lines(
        "Report",
        ["该Agent Skill包实现了复杂的电子表格处理功能，但包含多个高风险的安全特性。"],
        width=48,
        style="1;36",
        color=False,
    )

    assert all(_display_width(line) <= 48 for line in lines)


def test_format_scanskills_result_renders_collection_summary() -> None:
    formatted = _format_scanskills_result(
        {
            "ok": False,
            "collection_name": "auditset",
            "total_skills": 2,
            "succeeded": 1,
            "failed": 1,
            "results": [
                {
                    "ok": True,
                    "skill_name": "test-skill",
                    "skill_path": "/root/test-skill",
                    "session_id": "session-1",
                    "status": "done",
                    "summary": {"findings_count": 1, "risk_level": "HIGH"},
                    "result": {
                        "result": {
                            "score": 100,
                            "llm": "qwen3-max",
                            "language": "Python",
                            "readme": "# 审计报告\n\n## 结论\n存在高危问题。\n",
                            "results": [
                                {
                                    "title": "动态代码执行",
                                    "level": "HIGH",
                                    "risk_type": "Command Execution",
                                    "description": "## 漏洞详情\n可能导致任意代码执行。\n",
                                    "suggestion": "## 修复建议\n移除动态编译。\n",
                                }
                            ],
                        }
                    },
                },
                {
                    "ok": False,
                    "skill_name": "broken-skill",
                    "skill_path": "/root/broken-skill",
                    "error": "Failed to connect to AI-Infra-Guard",
                },
            ],
        }
    )

    assert "Skills Summary" in formatted
    assert "Findings across successful scans: 1" in formatted
    assert "Skills with findings: 1" in formatted
    assert "- test-skill: done | score=100 | findings=1 | risks=HIGH" in formatted
    assert "Skills Results" in formatted
    assert "- broken-skill: failed" in formatted
    assert "Report test-skill" not in formatted
    assert "Findings test-skill" not in formatted
    assert "Failures" not in formatted


def test_scan_risk_level_uses_structured_finding_levels() -> None:
    risk_level = _scan_risk_level(
        {
            "result": {
                "result": {
                    "results": [
                        {"title": "first", "level": "MEDIUM"},
                        {"title": "second", "level": "HIGH"},
                    ]
                }
            },
        }
    )

    assert risk_level == "HIGH"


def test_save_scan_result_writes_formatted_detailed_output(tmp_path: Path) -> None:
    target_path = tmp_path / "scan-report.txt"
    payload = {
        "ok": True,
        "skill_name": "test-skill",
        "skill_path": "/root/test-skill",
        "session_id": "session-1",
        "status": "done",
        "result": {
            "result": {
                "score": 100,
                "llm": "qwen3-max",
                "language": "Python",
                "readme": "# 审计报告\n\n## 结论\n存在高危问题。\n",
                "results": [
                    {
                        "title": "危险命令执行",
                        "level": "HIGH",
                        "risk_type": "Command Execution",
                        "description": "## 漏洞详情\n可能导致任意代码执行。\n",
                        "suggestion": "## 修复建议\n限制危险命令。\n",
                    }
                ],
            }
        },
    }

    saved_path = _save_scan_result(payload, str(target_path))
    saved_text = saved_path.read_text(encoding="utf-8")

    assert saved_path == target_path.resolve()
    assert "Skill Summary" in saved_text
    assert "Skill Results" in saved_text
    assert "Skill Report test-skill" in saved_text
    assert "Skill Finding Details test-skill" in saved_text
    assert "可能导致任意代码执行。" in saved_text
    assert '"skill_name": "test-skill"' not in saved_text


def test_default_scan_save_path_uses_text_extension() -> None:
    from magicskills.cli import _default_scan_save_path

    single_path = _default_scan_save_path({"skill_name": "test-skill", "session_id": "session-1"})
    collection_path = _default_scan_save_path({"collection_name": "auditset"})

    assert single_path.suffix == ".txt"
    assert collection_path.suffix == ".txt"


def test_cmd_scan_skill_details_prints_formatted_details(capsys: pytest.CaptureFixture[str]) -> None:
    payload = {
        "ok": True,
        "skill_name": "test-skill",
        "skill_path": "/root/test-skill",
        "session_id": "session-1",
        "status": "done",
        "result": {
            "result": {
                "score": 100,
                "readme": "# 审计报告\n\n## 结论\n存在高危问题。\n",
                "results": [
                    {
                        "title": "危险命令执行",
                        "level": "HIGH",
                        "risk_type": "Command Execution",
                        "description": "## 漏洞详情\n可能导致任意代码执行。\n",
                        "suggestion": "## 修复建议\n限制危险命令。\n",
                    }
                ],
            }
        },
    }
    args = SimpleNamespace(
        target="/root/test-skill",
        name=None,
        base_url=None,
        model=None,
        api_key=None,
        model_base_url=None,
        prompt=None,
        language=None,
        thread=None,
        poll_interval=None,
        timeout=None,
        header=None,
        save_raw=None,
        details=True,
    )

    with patch("magicskills.cli.command_scanskill", return_value=payload):
        exit_code = cmd_scan_skill(args)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Skill Summary" in output
    assert "Skill Results" in output
    assert "Skill Report test-skill" in output
    assert "审计报告" in output
    assert "Skill Finding Details test-skill" in output
    assert "1. 危险命令执行" in output
    assert "Level: HIGH" in output
    assert "Risk type: Command Execution" in output
    assert "可能导致任意代码执行。" in output
    assert "限制危险命令。" in output
    assert '"skill_name": "test-skill"' not in output


def test_cmd_scan_skills_details_prints_formatted_details(capsys: pytest.CaptureFixture[str]) -> None:
    payload = {
        "ok": True,
        "collection_name": "auditset",
        "total_skills": 1,
        "succeeded": 1,
        "failed": 0,
        "results": [
            {
                "ok": True,
                "skill_name": "test-skill",
                "skill_path": "/root/test-skill",
                "session_id": "session-1",
                "status": "done",
                "result": {
                    "result": {
                        "score": 100,
                        "readme": "# 审计报告\n\n## 结论\n存在高危问题。\n",
                        "results": [
                            {
                                "title": "危险命令执行",
                                "level": "HIGH",
                                "risk_type": "Command Execution",
                                "description": "## 漏洞详情\n可能导致任意代码执行。\n",
                                "suggestion": "## 修复建议\n限制危险命令。\n",
                            }
                        ],
                    }
                },
            }
        ],
    }
    args = SimpleNamespace(
        name="auditset",
        base_url=None,
        model=None,
        api_key=None,
        model_base_url=None,
        prompt=None,
        language=None,
        thread=None,
        poll_interval=None,
        timeout=None,
        header=None,
        save_raw=None,
        details=True,
    )

    with patch("magicskills.cli._registered_skills_or_exit", return_value=object()):
        with patch("magicskills.cli.command_scanskills", return_value=payload):
            exit_code = cmd_scan_skills(args)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Skills Summary" in output
    assert "Skills Results" in output
    assert "Skill Report test-skill" in output
    assert "Skill Finding Details test-skill" in output
    assert "1. 危险命令执行" in output
    assert "Level: HIGH" in output
    assert "可能导致任意代码执行。" in output
    assert '"collection_name": "auditset"' not in output
