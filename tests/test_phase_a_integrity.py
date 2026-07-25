from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.models import DiscoveredAsset, InsightRun, PageRecord, RunStageEvent, StageCheckpoint
from src.orchestrator import InsightRunOrchestrator
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.crawl_discovery_service import CrawlDiscoveryOutput
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.provenance_service import EvidenceReferenceError, validate_evidence_ref
from src.services.search_intelligence_service import SearchIntelligenceOutput


def test_run_and_stage_event_carry_attempt_identity() -> None:
    run = InsightRun(
        seo_target_id="target-1",
        requested_url="https://example.com/",
        requested_domain="example.com",
    )
    event = RunStageEvent(
        insight_run_id=run.id,
        stage_name="scoring",
        status="completed",
        attempt_id=run.attempt_id,
    )

    assert run.attempt_id
    assert event.attempt_id == run.attempt_id


def test_evidence_reference_resolves_exact_value_for_active_attempt(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    artifact = run_dir / "pages" / "page-1.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        json.dumps({"attempt_id": "attempt-a", "title": "Home"}),
        encoding="utf-8",
    )

    validate_evidence_ref(
        run_dir,
        {
            "artifact_path": "pages/page-1.json",
            "field": "title",
            "reason": "Fetched page title.",
            "observed": "Home",
        },
        expected_attempt_id="attempt-a",
    )


def test_evidence_reference_rejects_report_self_reference(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    reports = run_dir / "reports"
    reports.mkdir(parents=True)
    (reports / "v1.json").write_text(json.dumps({"summary": {"score": 1}}), encoding="utf-8")

    with pytest.raises(EvidenceReferenceError, match="report artifacts cannot be evidence"):
        validate_evidence_ref(
            run_dir,
            {
                "artifact_path": "reports/v1.json",
                "field": "summary.score",
                "reason": "Self-reference.",
                "observed": 1,
            },
            expected_attempt_id="attempt-a",
        )


def test_evidence_reference_rejects_stale_observed_value(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    artifact = run_dir / "events" / "event.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(json.dumps({"attempt_id": "attempt-a", "status": "completed"}), encoding="utf-8")

    with pytest.raises(EvidenceReferenceError, match="observed value does not match"):
        validate_evidence_ref(
            run_dir,
            {
                "artifact_path": "events/event.json",
                "field": "status",
                "reason": "Status.",
                "observed": "failed",
            },
            expected_attempt_id="attempt-a",
        )


def test_evidence_reference_rejects_wrong_attempt(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    artifact = run_dir / "events" / "event.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(json.dumps({"attempt_id": "attempt-a", "status": "completed"}), encoding="utf-8")

    with pytest.raises(EvidenceReferenceError, match="attempt"):
        validate_evidence_ref(
            run_dir,
            {
                "artifact_path": "events/event.json",
                "field": "status",
                "reason": "Status.",
                "observed": "completed",
            },
            expected_attempt_id="attempt-b",
        )


def test_rerun_rotates_attempt_and_report_uses_active_attempt(tmp_path: Path, monkeypatch) -> None:
    repo = FileBackedInsightRepository(tmp_path / "artifacts")
    orchestrator = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")

    def fake_discover(target, run_id):
        return (
            CrawlDiscoveryOutput(
                robots_url="https://example.com/robots.txt",
                robots_status=200,
                sitemap_urls=["https://example.com/sitemap.xml"],
                candidate_page_urls=[],
                candidate_sitemap_urls=["https://example.com/sitemap.xml"],
            ),
            [DiscoveredAsset(insight_run_id=run_id, asset_type="sitemap", url="https://example.com/sitemap.xml")],
        )

    def fake_pages(target, run_id, urls):
        return PageAnalysisOutput(
            pages=[
                PageRecord(
                    insight_run_id=run_id,
                    seo_target_id=target.id,
                    url=target.normalized_url,
                    fetch_status="fetched",
                    http_status=200,
                    indexable=True,
                    title="Home",
                    meta_description="Home",
                    h1="Home",
                )
            ]
        )

    def fake_search(context):
        return SearchIntelligenceOutput(
            configured=False,
            approved=False,
            skipped_reason="not configured",
            payload={},
            requested_context=context.to_dict(),
        )

    monkeypatch.setattr(orchestrator._pipeline.crawl_discovery, "discover", fake_discover)
    monkeypatch.setattr(orchestrator._pipeline.page_analysis, "analyze_urls", fake_pages)
    monkeypatch.setattr(orchestrator._pipeline.search_intelligence, "gather", fake_search)

    first = orchestrator.start("example.com", mode="quick", max_pages=1)
    second = orchestrator.rerun_stage(first.id, "discovering_sitemaps", max_pages=1)

    assert second.attempt_id != first.attempt_id
    report = repo.get_report(second.id, "v2")
    assert report is not None
    assert report.attempt_id == second.attempt_id
    completed = [event for event in repo.list_stage_events(second.id) if event.status == "completed"]
    current_completed = [event for event in completed if event.attempt_id == second.attempt_id]
    assert current_completed
    assert all(event.attempt_id == second.attempt_id for event in current_completed)


def test_report_rerun_reloads_checkpoints_without_network_calls(tmp_path: Path, monkeypatch) -> None:
    repo = FileBackedInsightRepository(tmp_path / "artifacts")
    orchestrator = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    calls = {"discover": 0, "pages": 0, "search": 0}

    def fake_discover(target, run_id):
        calls["discover"] += 1
        return (
            CrawlDiscoveryOutput(
                robots_url="https://example.com/robots.txt",
                robots_status=200,
                sitemap_urls=["https://example.com/sitemap.xml"],
                candidate_page_urls=[],
                candidate_sitemap_urls=["https://example.com/sitemap.xml"],
            ),
            [DiscoveredAsset(insight_run_id=run_id, asset_type="sitemap", url="https://example.com/sitemap.xml")],
        )

    def fake_pages(target, run_id, urls):
        calls["pages"] += 1
        return PageAnalysisOutput(
            pages=[
                PageRecord(
                    insight_run_id=run_id,
                    seo_target_id=target.id,
                    url=target.normalized_url,
                    fetch_status="fetched",
                    http_status=200,
                    indexable=True,
                    title="Home",
                    meta_description="Home",
                    h1="Home",
                )
            ]
        )

    def fake_search(context):
        calls["search"] += 1
        return SearchIntelligenceOutput(
            configured=False,
            approved=False,
            skipped_reason="not configured",
            payload={},
            requested_context=context.to_dict(),
        )

    monkeypatch.setattr(orchestrator._pipeline.crawl_discovery, "discover", fake_discover)
    monkeypatch.setattr(orchestrator._pipeline.page_analysis, "analyze_urls", fake_pages)
    monkeypatch.setattr(orchestrator._pipeline.search_intelligence, "gather", fake_search)
    run = orchestrator.start("example.com", mode="quick", max_pages=1)
    assert calls == {"discover": 1, "pages": 1, "search": 1}

    def fail_network(*args, **kwargs):
        raise AssertionError("network stage was recomputed during report rerun")

    monkeypatch.setattr(orchestrator._pipeline.crawl_discovery, "discover", fail_network)
    monkeypatch.setattr(orchestrator._pipeline.page_analysis, "analyze_urls", fail_network)
    monkeypatch.setattr(orchestrator._pipeline.search_intelligence, "gather", fail_network)

    rerun = orchestrator.rerun_stage(run.id, "assembling_report", max_pages=1)

    assert rerun.status == "completed"
    assert calls == {"discover": 1, "pages": 1, "search": 1}


def test_typed_checkpoint_round_trips_and_rejects_tampering(tmp_path: Path) -> None:
    repo = FileBackedInsightRepository(tmp_path / "artifacts")
    run = InsightRun(
        seo_target_id="target-1",
        requested_url="https://example.com/",
        requested_domain="example.com",
    )
    repo.create_run(run)
    checkpoint = StageCheckpoint.create(
        insight_run_id=run.id,
        attempt_id=run.attempt_id,
        stage_name="scoring",
        payload_type="scorecard",
        payload={"overall_score": 75.0, "scored_dimensions": ["metadata_quality"]},
    )
    repo.save_checkpoint(checkpoint)

    loaded = repo.get_checkpoint(run.id, run.attempt_id, "scoring")
    assert loaded is not None
    assert loaded.payload_type == "scorecard"
    assert loaded.payload["overall_score"] == 75.0

    path = tmp_path / "artifacts" / "runs" / run.id / "checkpoints" / run.attempt_id / "scoring.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["payload"]["overall_score"] = 10.0
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValueError, match="content hash"):
        repo.get_checkpoint(run.id, run.attempt_id, "scoring")
