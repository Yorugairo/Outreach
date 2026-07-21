from __future__ import annotations

from pathlib import Path

import pytest

from src.config import AppConfig, ApprovalPolicy, DataForSEOSettings
from src.models import InsightRun
from src.orchestrator import InsightRunOrchestrator
from src.repositories.file_repository import FileBackedInsightRepository


def _make_repo(tmp_path: Path) -> FileBackedInsightRepository:
    return FileBackedInsightRepository(tmp_path / "artifacts")


def test_completed_run_records_released_lease_lifecycle(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")

    run = orch.start("python.org", mode="quick", max_pages=1)
    persisted = repo.get_run(run.id)

    assert persisted is not None
    assert persisted.heartbeat_at is not None
    assert persisted.lease_owner is None
    assert persisted.lease_expires_at is None
    validation = orch.validate(run.id)
    assert validation["run_execution_recorded"] is True


def test_orchestrator_recovers_stale_running_run(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = InsightRun(
        id="stale-run",
        seo_target_id="target-1",
        requested_url="https://example.com",
        requested_domain="example.com",
        status="running",
        current_stage="fetching_pages",
        lease_owner="worker-a",
        heartbeat_at="2000-01-01T00:00:00+00:00",
        lease_expires_at="2000-01-01T00:01:00+00:00",
    )
    repo.create_run(run)

    recovered = orch.recover_stale_runs(worker_id="reaper", reason="test stale lease")
    updated = repo.get_run(run.id)
    events = repo.list_stage_events(run.id)

    assert recovered == [run.id]
    assert updated is not None
    assert updated.status == "failed"
    assert updated.lease_owner is None
    assert updated.lease_expires_at is None
    assert "test stale lease" in (updated.error_text or "")
    assert any(event.status == "failed" and event.stage_name == "fetching_pages" for event in events)


def test_paid_dataforseo_enrichment_requires_explicit_approval(tmp_path: Path):
    repo = _make_repo(tmp_path)
    config = AppConfig(
        dataforseo=DataForSEOSettings(login="user", password="pass"),
        approval=ApprovalPolicy(allow_paid_api_calls=False),
    )
    orch = InsightRunOrchestrator(repo, config=config, artifact_root=tmp_path / "artifacts")

    run = orch.start("python.org", mode="quick", max_pages=1)
    persisted = repo.get_run(run.id)
    search_event = [
        event
        for event in repo.list_stage_events(run.id)
        if event.stage_name == "pulling_search_intelligence" and event.status == "completed"
    ][-1]
    validation = orch.validate(run.id)

    assert persisted is not None
    assert persisted.config_snapshot["dataforseo_configured"] is True
    assert persisted.config_snapshot["paid_api_approved"] is False
    assert persisted.input_payload["limits"]["max_dataforseo_calls"] == 0
    assert persisted.input_payload["budget"]["estimated_paid_api_calls"] == 0
    assert search_event.output_summary["configured"] is True
    assert search_event.output_summary["approved"] is False
    assert "approval" in search_event.output_summary["skipped_reason"].lower()
    assert validation["search_intelligence_recorded"] is True
