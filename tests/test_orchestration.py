from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.stage_errors import (  # noqa: E402
    FatalStageError,
    RetryableStageError,
    classify_stage_error,
    is_retryable,
)
from src.config import AppConfig, DataForSEOSettings, RetryPolicy  # noqa: E402
from src.models import InsightRun, RunStageEvent  # noqa: E402
from src.repositories.file_repository import FileBackedInsightRepository  # noqa: E402
from src.orchestrator import InsightRunOrchestrator  # noqa: E402


# ---- stage_errors ----

def test_fatal_classification():
    assert isinstance(classify_stage_error(ValueError("invalid target format")), FatalStageError)
    assert not is_retryable(ValueError("bad format"))


def test_retryable_classification():
    assert isinstance(classify_stage_error(ValueError("read timeout occurred")), RetryableStageError)
    assert is_retryable(ValueError("connection reset by peer"))


def test_passthrough_classified():
    exc = RetryableStageError("already classified")
    assert classify_stage_error(exc) is exc


# ---- repository query methods ----

def _make_repo(tmp_path: Path) -> FileBackedInsightRepository:
    return FileBackedInsightRepository(tmp_path / "artifacts")


def _seed_run(repo: FileBackedInsightRepository, run_id: str) -> InsightRun:
    run = InsightRun(
        id=run_id,
        seo_target_id="t1",
        requested_url="https://example.com",
        requested_domain="example.com",
    )
    repo.create_run(run)
    return run


def test_get_run_roundtrip(tmp_path: Path):
    repo = _make_repo(tmp_path)
    run = _seed_run(repo, "run-roundtrip")
    fetched = repo.get_run("run-roundtrip")
    assert fetched is not None
    assert fetched.id == run.id


def test_get_run_missing(tmp_path: Path):
    repo = _make_repo(tmp_path)
    assert repo.get_run("missing") is None


def test_list_runs_orders_newest_first(tmp_path: Path):
    repo = _make_repo(tmp_path)
    _seed_run(repo, "run-a")
    _seed_run(repo, "run-b")
    runs = repo.list_runs(limit=10)
    ids = [r.id for r in runs]
    assert "run-a" in ids and "run-b" in ids


def test_list_stage_events_empty_then_present(tmp_path: Path):
    repo = _make_repo(tmp_path)
    _seed_run(repo, "run-events")
    assert repo.list_stage_events("run-events") == []
    repo.append_stage_event(
        RunStageEvent(
            insight_run_id="run-events",
            stage_name="normalizing_target",
            stage_order=1,
            status="completed",
        )
    )
    assert len(repo.list_stage_events("run-events")) == 1


# ---- orchestrator ----

def test_orchestrator_start_and_status(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("python.org", mode="quick", max_pages=1)
    assert run.status == "completed"
    st = orch.status(run.id)
    assert st["exists"] is True
    assert st["status"] == "completed"
    assert len(st["stages"]) >= 6


def test_orchestrator_validate_completed_run_proves_artifacts(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")

    run = orch.start("python.org", mode="quick", max_pages=1)
    validation = orch.validate(run.id)

    assert validation["exists"] is True
    assert validation["valid"] is True
    assert validation["run_id"] == run.id
    assert validation["status"] == "completed"
    assert validation["report_json_exists"] is True
    assert validation["report_markdown_exists"] is True
    assert validation["summary_has_overall_score"] is True
    assert validation["completed_stage_count"] == 6
    assert validation["search_intelligence_recorded"] is True
    assert validation["errors"] == []


def test_report_json_embeds_final_completed_run_snapshot(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("python.org", mode="quick", max_pages=1)

    report_path = tmp_path / "artifacts" / "runs" / run.id / "reports" / "v1.json"
    report = json.loads(report_path.read_text())
    embedded_run = report["report_payload"]["run"]

    assert embedded_run["status"] == "completed"
    assert embedded_run["current_stage"] == "completed"
    assert embedded_run["summary"]["overall_score"] == run.summary["overall_score"]


def test_report_recommendations_have_artifact_evidence_refs(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("python.org", mode="quick", max_pages=1)

    report_path = tmp_path / "artifacts" / "runs" / run.id / "reports" / "v1.json"
    report = json.loads(report_path.read_text())

    assert report["key_actions"]
    for action in report["key_actions"]:
        assert action["evidence_refs"]
        for ref in action["evidence_refs"]:
            assert ref["artifact_path"]
            assert ref["field"]
            assert ref["reason"]

    validation = orch.validate(run.id)
    assert validation["report_actions_have_evidence_refs"] is True


def test_run_records_operator_limits_and_budget_metadata(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("python.org", mode="quick", max_pages=1)

    persisted = repo.get_run(run.id)
    assert persisted is not None
    assert persisted.input_payload["limits"]["max_pages"] == 1
    assert persisted.input_payload["limits"]["max_dataforseo_calls"] == 0
    assert persisted.input_payload["budget"]["estimated_paid_api_calls"] == 0
    assert persisted.config_snapshot["run_limits"]["max_pages"] == 1
    assert orch.validate(run.id)["run_limits_recorded"] is True


def test_orchestrator_validate_detects_missing_report_artifact(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("python.org", mode="quick", max_pages=1)
    report_md = tmp_path / "artifacts" / "runs" / run.id / "reports" / "v1.md"
    report_md.unlink()

    validation = orch.validate(run.id)

    assert validation["valid"] is False
    assert validation["report_markdown_exists"] is False
    assert "reports/v1.md is missing" in validation["errors"]


def test_orchestrator_resume_repairs_invalid_completed_artifacts(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("python.org", mode="quick", max_pages=1)
    report_md = tmp_path / "artifacts" / "runs" / run.id / "reports" / "v1.md"
    report_md.unlink()
    assert orch.validate(run.id)["valid"] is False

    resumed = orch.resume(run.id, max_pages=1)

    assert resumed.id == run.id
    assert resumed.status == "completed"
    assert report_md.exists()
    assert orch.validate(run.id)["valid"] is True


def test_stage_completion_events_include_artifact_backed_summaries(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("python.org", mode="quick", max_pages=1)
    completed = {
        event.stage_name: event
        for event in repo.list_stage_events(run.id)
        if event.status == "completed"
    }

    fetching = completed["fetching_pages"]
    assert fetching.duration_ms is not None
    assert fetching.output_summary["pages_saved"] >= 1
    assert fetching.output_summary["artifact_paths"]

    search = completed["pulling_search_intelligence"]
    assert search.output_summary["configured"] is False
    assert search.output_summary["skipped_reason"]

    report = completed["assembling_report"]
    assert "reports/v1.json" in report.output_summary["artifact_paths"]
    assert "reports/v1.md" in report.output_summary["artifact_paths"]


def test_orchestrator_status_missing(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    assert orch.status("ghost")["exists"] is False


def test_orchestrator_rerun_stage_completes_same_run(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("python.org", mode="quick", max_pages=1)
    event_count_before = len(repo.list_stage_events(run.id))

    rerun = orch.rerun_stage(run.id, "fetching_pages", max_pages=1)

    assert rerun.id == run.id
    assert rerun.status == "completed"
    assert rerun.attempt_count == run.attempt_count + 1
    assert len(repo.list_stage_events(run.id)) > event_count_before
    assert orch.validate(run.id)["valid"] is True


def test_cli_validate_command_returns_artifact_status(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("python.org", mode="quick", max_pages=1)

    import scripts.run_insight_pipeline as cli

    old_argv = sys.argv
    try:
        sys.argv = [
            "run_insight_pipeline.py",
            "--artifact-root",
            str(tmp_path / "artifacts"),
            "validate",
            run.id,
        ]
        assert cli.main() == 0
    finally:
        sys.argv = old_argv

    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True


def test_cli_legacy_url_shorthand_still_starts_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    import scripts.run_insight_pipeline as cli

    old_argv = sys.argv
    try:
        sys.argv = [
            "run_insight_pipeline.py",
            "--artifact-root",
            str(tmp_path / "artifacts"),
            "python.org",
            "--mode",
            "quick",
            "--max-pages",
            "1",
        ]
        assert cli.main() == 0
    finally:
        sys.argv = old_argv

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "completed"
    assert payload["validation"]["valid"] is True


def test_orchestrator_rerun_unknown_stage(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("python.org", mode="quick", max_pages=1)
    with pytest.raises(ValueError):
        orch.rerun_stage(run.id, "bogus_stage")


# ---- config retry policy ----

def test_retry_policy_defaults():
    policy = RetryPolicy()
    assert policy.max_attempts == 3
    assert policy.base_delay_seconds == 1.0
    assert policy.max_delay_seconds == 10.0


def test_appconfig_has_retry():
    cfg = AppConfig(dataforseo=DataForSEOSettings(login=None, password=None))
    assert isinstance(cfg.retry, RetryPolicy)
