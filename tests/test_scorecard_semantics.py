from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models import InsightReport, InsightRun, PageRecord, RunStageEvent  # noqa: E402
from src.orchestrator import InsightRunOrchestrator  # noqa: E402
from src.pipeline import DEFAULT_STAGES, InsightRunPipeline  # noqa: E402
from src.repositories.file_repository import FileBackedInsightRepository  # noqa: E402
from src.services.crawl_discovery_service import CrawlDiscoveryOutput  # noqa: E402
from src.services.page_analysis_service import PageAnalysisOutput  # noqa: E402
from src.services.reporting_service import ScorecardService  # noqa: E402
from src.services.search_intelligence_service import SearchIntelligenceOutput, TargetContext  # noqa: E402

DIMENSIONS = {"sitemap_quality", "metadata_quality", "page_coverage", "search_visibility"}


def _context() -> TargetContext:
    return TargetContext(
        primary_url="https://example.com/",
        target_domain="example.com",
        language_code="en",
        device="desktop",
        location_code=None,
        market="United States",
    )


def _build_scorecard(crawl, pages, search, *, target_context: TargetContext | None = None):
    return ScorecardService().build(crawl, pages, search, target_context=target_context or _context())


def _crawl() -> CrawlDiscoveryOutput:
    return CrawlDiscoveryOutput(
        robots_url="https://example.com/robots.txt",
        robots_status=200,
        sitemap_urls=["https://example.com/sitemap.xml"],
        candidate_page_urls=["https://example.com/", "https://example.com/about"],
    )


def _pages() -> PageAnalysisOutput:
    return PageAnalysisOutput(
        pages=[
            PageRecord(
                insight_run_id="run-1",
                seo_target_id="target-1",
                url="https://example.com/",
                fetch_status="fetched",
                title="Home",
                meta_description="Home page",
                h1="Example",
                indexable=True,
            ),
            PageRecord(
                insight_run_id="run-1",
                seo_target_id="target-1",
                url="https://example.com/about",
                fetch_status="fetched",
                title="About",
                meta_description="About page",
                h1="About",
                indexable=True,
            ),
        ]
    )


def _search(*, configured: bool, approved: bool, payload: dict | None = None, reason: str | None = None):
    return SearchIntelligenceOutput(
        configured=configured,
        skipped_reason=reason,
        payload=payload or {},
        approved=approved,
    )


def test_unconfigured_search_is_unknown_and_excluded_from_scoring() -> None:
    scorecard = _build_scorecard(
        _crawl(),
        _pages(),
        _search(configured=False, approved=False, reason="credentials not configured"),
        target_context=_context(),
    )

    assert scorecard.search_visibility_score is None
    assert scorecard.dimension_status["search_visibility"] == "unknown"
    assert "search_visibility" not in scorecard.scored_dimensions


def test_overall_is_mean_of_measured_dimensions_and_completeness_is_50_percent() -> None:
    scorecard = _build_scorecard(
        _crawl(),
        _pages(),
        _search(configured=False, approved=False, reason="credentials not configured"),
        target_context=_context(),
    )

    measured = [
        scorecard.sitemap_quality_score,
        scorecard.metadata_quality_score,
    ]
    assert all(score is not None for score in measured)
    assert scorecard.overall_score == round(sum(measured) / 2, 2)  # type: ignore[arg-type]
    assert scorecard.completeness_percent == 50.0
    assert set(scorecard.scored_dimensions) == DIMENSIONS - {"page_coverage", "search_visibility"}


def test_page_sample_size_is_not_a_site_health_score() -> None:
    pages = _pages()
    one_page_sample = PageAnalysisOutput(pages=pages.pages[:1])
    multiple_page_sample = PageAnalysisOutput(pages=pages.pages)

    one_page_scorecard = _build_scorecard(
        _crawl(),
        one_page_sample,
        _search(configured=False, approved=False, reason="credentials not configured"),
        target_context=_context(),
    )
    multiple_page_scorecard = _build_scorecard(
        _crawl(),
        multiple_page_sample,
        _search(configured=False, approved=False, reason="credentials not configured"),
        target_context=_context(),
    )

    for scorecard in (one_page_scorecard, multiple_page_scorecard):
        assert scorecard.page_coverage_score is None
        assert scorecard.dimension_status["page_coverage"] == "unknown"
        assert "page_coverage" not in scorecard.scored_dimensions
        assert any("sampled page count" in warning.lower() and "run limit" in warning.lower() for warning in scorecard.warnings)
    assert one_page_scorecard.overall_score == multiple_page_scorecard.overall_score


def test_page_fetch_errors_do_not_degrade_primary_page_metadata() -> None:
    pages = _pages()
    scorecard = _build_scorecard(
        _crawl(),
        PageAnalysisOutput(pages=pages.pages, errors=["https://example.com/missing: fetch failed"]),
        _search(configured=False, approved=False, reason="credentials not configured"),
        target_context=_context(),
    )

    assert scorecard.metadata_quality_score == 100.0
    assert scorecard.dimension_status["metadata_quality"] == "valid"
    assert scorecard.page_coverage_score is None
    assert scorecard.dimension_status["page_coverage"] == "unknown"


def test_redirected_primary_request_scores_complete_metadata() -> None:
    redirected_primary = PageRecord(
        insight_run_id="run-1",
        seo_target_id="target-1",
        url="https://www.example.com/",
        fetch_status="fetched",
        title="Home",
        meta_description="Home page",
        h1="Example",
        indexable=True,
        fetch_metadata={"fetched_url": "https://example.com"},
    )

    scorecard = _build_scorecard(
        _crawl(),
        PageAnalysisOutput(pages=[redirected_primary]),
        _search(configured=False, approved=False, reason="credentials not configured"),
    )

    assert scorecard.metadata_quality_score == 100.0
    assert scorecard.dimension_status["metadata_quality"] == "valid"


def test_secondary_request_redirected_to_primary_final_url_leaves_metadata_unknown() -> None:
    redirected_secondary = PageRecord(
        insight_run_id="run-1",
        seo_target_id="target-1",
        url="https://example.com/",
        fetch_status="fetched",
        title="Home",
        meta_description="Home page",
        h1="Example",
        indexable=True,
        fetch_metadata={"fetched_url": "https://example.com/about"},
    )

    scorecard = _build_scorecard(
        _crawl(),
        PageAnalysisOutput(pages=[redirected_secondary]),
        _search(configured=False, approved=False, reason="credentials not configured"),
    )

    assert scorecard.metadata_quality_score is None
    assert scorecard.dimension_status["metadata_quality"] == "unknown"
    assert "metadata_quality" not in scorecard.scored_dimensions


def test_legacy_page_without_requested_url_matches_primary_by_final_url() -> None:
    legacy_primary = PageRecord(
        insight_run_id="run-1",
        seo_target_id="target-1",
        url="https://example.com/",
        fetch_status="fetched",
        title="Home",
        meta_description="Home page",
        h1="Example",
        indexable=True,
    )

    scorecard = _build_scorecard(
        _crawl(),
        PageAnalysisOutput(pages=[legacy_primary]),
        _search(configured=False, approved=False, reason="credentials not configured"),
    )

    assert scorecard.metadata_quality_score == 100.0
    assert scorecard.dimension_status["metadata_quality"] == "valid"


def test_unapproved_search_warns_without_changing_overall_score() -> None:
    service = ScorecardService()
    unconfigured = service.build(
        _crawl(),
        _pages(),
        _search(configured=False, approved=False, reason="credentials not configured"),
        target_context=_context(),
    )
    unapproved = service.build(
        _crawl(),
        _pages(),
        _search(configured=True, approved=False, reason="operator approval required"),
        target_context=_context(),
    )

    assert unapproved.overall_score == unconfigured.overall_score
    assert unapproved.search_visibility_score is None
    assert unapproved.dimension_status["search_visibility"] == "unknown"
    assert any("target-specific search evidence" in warning.lower() for warning in unapproved.warnings)


def test_reference_connectivity_payload_is_not_target_specific_visibility_evidence() -> None:
    scorecard = _build_scorecard(
        _crawl(),
        _pages(),
        _search(
            configured=True,
            approved=True,
            payload={
                "status_code": 20000,
                "tasks_error": 0,
                "raw_excerpt_keys": ["version", "status_code", "tasks_error"],
            },
        ),
    )

    assert scorecard.search_visibility_score is None
    assert scorecard.dimension_status["search_visibility"] == "unknown"
    assert "search_visibility" not in scorecard.scored_dimensions
    assert any("target" in warning.lower() for warning in scorecard.warnings)


@pytest.mark.parametrize(
    ("configured", "approved", "payload"),
    [
        (False, True, {"visibility_score": 82.5, "target_domain": "example.com", "snapshot_date": "2026-07-22"}),
        (True, False, {"visibility_score": 82.5, "target_domain": "example.com", "snapshot_date": "2026-07-22"}),
        (True, True, {"visibility_score": 101, "target_domain": "example.com", "snapshot_date": "2026-07-22"}),
        (True, True, {"visibility_score": 82.5, "target_domain": "", "snapshot_date": "2026-07-22"}),
        (True, True, {"visibility_score": 82.5, "target_domain": "example.com", "snapshot_date": ""}),
    ],
)
def test_target_specific_search_payload_requires_complete_approved_contract(
    configured: bool, approved: bool, payload: dict
) -> None:
    scorecard = _build_scorecard(_crawl(), _pages(), _search(configured=configured, approved=approved, payload=payload))

    assert scorecard.search_visibility_score is None
    assert scorecard.dimension_status["search_visibility"] == "unknown"


def test_target_specific_search_payload_is_valid_when_contract_is_complete() -> None:
    scorecard = _build_scorecard(
        _crawl(),
        _pages(),
        _search(
            configured=True,
            approved=True,
            payload={
                "visibility_score": 82.5,
                "target_domain": "example.com",
                "snapshot_date": "2026-07-22",
                "language_code": "en",
                "device": "desktop",
                "market": "United States",
                "source": "rank-tracker",
                "observed_ranking_urls": ["https://example.com/service"],
            },
        ),
    )

    assert scorecard.search_visibility_score == 82.5
    assert scorecard.dimension_status["search_visibility"] == "valid"
    assert "search_visibility" in scorecard.scored_dimensions
    assert scorecard.completeness_percent == 75.0


def _seed_validation_run(tmp_path: Path, scorecard_summary: dict) -> tuple[InsightRunOrchestrator, str]:
    artifact_root = tmp_path / "artifacts"
    repo = FileBackedInsightRepository(artifact_root)
    run = InsightRun(
        id="run-semantics",
        seo_target_id="target-1",
        requested_url="https://example.com",
        requested_domain="example.com",
        status="completed",
        current_stage="completed",
        started_at="2026-07-22T00:00:00+00:00",
        completed_at="2026-07-22T00:00:10+00:00",
        heartbeat_at="2026-07-22T00:00:09+00:00",
        summary={
            "overall_score": scorecard_summary["overall_score"],
            "report_versions": ["v1", "v2"],
            "primary_report_version": "v2",
        },
        input_payload={
            "limits": {"max_pages": 2, "max_dataforseo_calls": 0},
            "budget": {"estimated_paid_api_calls": 0},
        },
        config_snapshot={
            "dataforseo_configured": False,
            "run_limits": {"max_pages": 2, "max_dataforseo_calls": 0},
        },
    )
    repo.create_run(run)
    for index, stage in enumerate(DEFAULT_STAGES, start=1):
        if stage == "scoring":
            output_summary = {"overall_score": scorecard_summary["overall_score"], "scorecard": scorecard_summary}
        elif stage == "pulling_search_intelligence":
            output_summary = {
                "configured": False,
                "approved": False,
                "skipped_reason": "credentials not configured",
                "payload_keys": [],
            }
        else:
            output_summary = {}
        repo.append_stage_event(
            RunStageEvent(
                insight_run_id=run.id,
                stage_name=stage,
                stage_order=index,
                status="completed",
                created_at=f"2026-07-22T00:00:0{index}+00:00",
                output_summary=output_summary,
            )
        )
    repo.save_report(
        InsightReport(
            insight_run_id=run.id,
            seo_target_id=run.seo_target_id,
            report_payload={},
            report_status="complete",
            key_actions=[
                {
                    "action": "Configure search evidence",
                    "evidence_refs": [
                        {"artifact_path": "run.json", "field": "summary", "reason": "Search is unknown"}
                    ],
                }
            ],
            export_markdown="# report\n",
        )
    )
    repo.save_report(
        InsightReport(
            insight_run_id=run.id,
            seo_target_id=run.seo_target_id,
            report_version="v2",
            report_status="complete",
            report_payload={
                "target": {},
                "run": {},
                "crawl": {},
                "pages": [],
                "page_errors": [],
                "search": {},
                "scorecard": scorecard_summary,
                "findings": [],
                "executive_answer": "No supported commercial finding.",
                "method_and_limits": {},
                "next_best_action": None,
            },
            key_actions=[],
            export_markdown="# v2 report\n",
        )
    )
    return InsightRunOrchestrator(repo, artifact_root=artifact_root), run.id


def test_orchestrator_validation_accepts_unknown_dimensions_with_valid_semantics(tmp_path: Path) -> None:
    scorecard = _build_scorecard(
        _crawl(),
        _pages(),
        _search(configured=False, approved=False, reason="credentials not configured"),
        target_context=_context(),
    )
    orchestrator, run_id = _seed_validation_run(tmp_path, asdict(scorecard))

    validation = orchestrator.validate(run_id)

    assert validation["scorecard_semantics_recorded"] is True
    assert validation["valid"] is True


def test_orchestrator_validation_rejects_malformed_latest_scoring_semantics(tmp_path: Path) -> None:
    scorecard = _build_scorecard(
        _crawl(),
        _pages(),
        _search(configured=False, approved=False, reason="credentials not configured"),
        target_context=_context(),
    )
    orchestrator, run_id = _seed_validation_run(tmp_path, asdict(scorecard))
    orchestrator.repository.append_stage_event(
        RunStageEvent(
            insight_run_id=run_id,
            stage_name="scoring",
            stage_order=5,
            status="completed",
            created_at="2026-07-22T00:01:00+00:00",
            output_summary={
                "scorecard": {
                    **asdict(scorecard),
                    "completeness_percent": 125.0,
                    "dimension_status": {"search_visibility": "mystery"},
                    "scored_dimensions": ["search_visibility", "bogus"],
                }
            },
        )
    )

    validation = orchestrator.validate(run_id)

    assert validation["scorecard_semantics_recorded"] is False
    assert validation["valid"] is False
    assert "completed scoring event has malformed scorecard semantics" in validation["errors"]


def test_scorecard_stage_summary_persists_the_full_dataclass() -> None:
    scorecard = _build_scorecard(
        _crawl(),
        _pages(),
        _search(configured=False, approved=False, reason="credentials not configured"),
        target_context=_context(),
    )

    assert InsightRunPipeline._summarize_scorecard(scorecard)["scorecard"] == asdict(scorecard)
