from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

import pytest

from src.models import CommercialFinding, InsightReport, InsightRun, PageRecord, RunStageEvent, SEOTarget
from src.orchestrator import InsightRunOrchestrator
from src.pipeline import DEFAULT_STAGES, InsightRunPipeline
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.crawl_discovery_service import CrawlDiscoveryOutput
from src.services.finding_service import FindingService
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.reporting_service import ReportAssemblyService, ScorecardService
from src.services.search_intelligence_service import SearchIntelligenceOutput


def context(**overrides):
    value = {
        "primary_url": "https://example.com/",
        "target_domain": "example.com",
        "language_code": "en",
        "device": "desktop",
        "location_code": 2840,
        "market": "United States",
    }
    value.update(overrides)
    return value


def crawl(*, valid=None, candidates=None, errors=None):
    return CrawlDiscoveryOutput(
        robots_url="https://example.com/robots.txt",
        robots_status=200,
        sitemap_urls=valid or [],
        candidate_sitemap_urls=candidates or [],
        candidate_page_urls=[],
        errors=errors or [],
    )


def page(url: str, record_id: str, *, title="Title", meta="Description", h1="Heading"):
    return PageRecord(
        id=record_id,
        insight_run_id="run-1",
        seo_target_id="target-1",
        url=url,
        fetch_status="fetched",
        http_status=200,
        indexable=True,
        title=title,
        meta_description=meta,
        h1=h1,
    )


def unknown_search(reason="DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD not configured"):
    return SearchIntelligenceOutput(configured=False, approved=False, skipped_reason=reason, payload={})


def valid_search(**overrides):
    payload = {
        "visibility_score": 72.5,
        "target_domain": "WWW.EXAMPLE.COM.",
        "snapshot_date": "2026-07-22",
        "language_code": "en",
        "device": "desktop",
        "location_code": 2840,
        "market": "United States",
        "source": "rank-tracker",
        "observed_ranking_urls": ["https://shop.example.com/service"],
    }
    payload.update(overrides)
    return SearchIntelligenceOutput(configured=True, approved=True, skipped_reason=None, payload=payload)


def stage_paths():
    return {
        "discovering_sitemaps": "events/crawl.json",
        "fetching_pages": "events/pages.json",
        "pulling_search_intelligence": "events/search.json",
    }


def test_commercial_finding_type_is_required_and_evidence_limits_cannot_route():
    assert {item.name for item in fields(CommercialFinding)} == {
        "id", "finding_type", "category", "title", "observation", "impact",
        "recommended_action", "severity", "effort", "confidence",
        "recommended_services", "service_fit_reason", "evidence_refs",
    }
    base = dict(
        id="finding-1", finding_type="evidence_limit", category="collection",
        title="Unknown", observation="Evidence is incomplete.", impact="A conclusion remains unknown.",
        recommended_action="Recheck the source.", severity="info", effort="discovery_required",
        confidence="high", recommended_services=[], service_fit_reason="No route.",
        evidence_refs=[{"artifact_path": "events/search.json", "field": "output_summary.configured", "reason": "Not configured.", "observed": False}],
    )
    assert CommercialFinding(**base).finding_type == "evidence_limit"
    with pytest.raises(ValueError):
        CommercialFinding(**{**base, "finding_type": "warning"})
    with pytest.raises(ValueError):
        CommercialFinding(**{**base, "recommended_services": ["web_development_rebuild"]})


def test_primary_page_alone_controls_metadata_and_overall_score():
    primary = page("https://example.com/", "primary")
    incomplete_secondary = page("https://example.com/about", "secondary", title=None, meta=None, h1=None)
    args = (crawl(valid=["https://example.com/sitemap.xml"]), unknown_search())
    one = ScorecardService().build(args[0], PageAnalysisOutput(pages=[primary]), args[1], target_context=context())
    many = ScorecardService().build(
        args[0], PageAnalysisOutput(pages=[primary, incomplete_secondary]), args[1], target_context=context()
    )
    assert one.metadata_quality_score == many.metadata_quality_score == 100.0
    assert one.overall_score == many.overall_score
    missing = ScorecardService().build(
        args[0], PageAnalysisOutput(pages=[incomplete_secondary]), args[1], target_context=context()
    )
    assert missing.metadata_quality_score is None
    assert missing.dimension_status["metadata_quality"] == "unknown"


@pytest.mark.parametrize(
    ("crawl_output", "expected_type", "expected_score"),
    [
        (crawl(), "evidence_limit", None),
        (crawl(candidates=["https://example.com/sitemap.xml"], errors=["timeout while fetching sitemap"]), "evidence_limit", None),
        (crawl(candidates=["https://example.com/sitemap.xml"], errors=["sitemap_parse_failed:https://example.com/sitemap.xml: HTTP 404"]), "prospect_issue", 20.0),
        (crawl(candidates=["https://example.com/sitemap.xml"], errors=["sitemap_parse_failed:https://example.com/sitemap.xml: malformed XML"]), "prospect_issue", 20.0),
    ],
)
def test_sitemap_evidence_fails_closed(crawl_output, expected_type, expected_score):
    findings = FindingService().build_findings(
        crawl_output, PageAnalysisOutput(), valid_search(), target_context=context(), stage_artifacts=stage_paths()
    )
    sitemap = next(item for item in findings if item.category == "sitemap_discovery")
    score = ScorecardService().build(crawl_output, PageAnalysisOutput(), valid_search(), target_context=context())
    assert sitemap.finding_type == expected_type
    assert sitemap.recommended_services == (["web_development_rebuild"] if expected_type == "prospect_issue" else [])
    assert score.sitemap_quality_score == expected_score
    assert "found" not in sitemap.observation.lower()


def test_search_validation_is_bound_to_complete_run_context_and_target_urls():
    service = ScorecardService()
    valid = service.build(crawl(valid=["https://example.com/sitemap.xml"]), PageAnalysisOutput(), valid_search(), target_context=context())
    assert valid.search_visibility_score == 72.5
    invalid_payloads = [
        {"target_domain": "other.example"},
        {"snapshot_date": "not-a-date"},
        {"source": ""},
        {"observed_ranking_urls": []},
        {"observed_ranking_urls": ["https://competitor.test/"]},
        {"language_code": "fr"},
        {"device": "mobile"},
        {"location_code": 999},
    ]
    for patch in invalid_payloads:
        output = service.build(
            crawl(valid=["https://example.com/sitemap.xml"]), PageAnalysisOutput(), valid_search(**patch),
            target_context=context(),
        )
        assert output.search_visibility_score is None
        findings = FindingService().build_findings(
            crawl(valid=["https://example.com/sitemap.xml"]), PageAnalysisOutput(), valid_search(**patch),
            target_context=context(), stage_artifacts=stage_paths(),
        )
        warning = next(item for item in findings if item.category == "search_evidence_completeness")
        assert warning.finding_type == "evidence_limit"
        assert warning.recommended_services == []


def test_markdown_separates_evidence_limits_and_humanizes_service_without_credentials():
    target = SEOTarget(input_url="example.com", normalized_url="https://example.com/", normalized_domain="example.com")
    run = InsightRun(seo_target_id=target.id, requested_url=target.normalized_url, requested_domain=target.normalized_domain)
    pages = PageAnalysisOutput(pages=[page(target.normalized_url, "page-1", title=None)])
    score = ScorecardService().build(crawl(valid=["https://example.com/sitemap.xml"]), pages, unknown_search(), target_context=context())
    report = ReportAssemblyService().build_report_v2(
        target, run, crawl(valid=["https://example.com/sitemap.xml"]), pages, unknown_search(), score,
        target_context=context(), stage_artifacts=stage_paths(),
    )
    markdown = report.export_markdown
    assert "Website development / rebuild" in markdown
    assert "Confidence: High" in markdown
    assert "Effort: Medium" in markdown
    assert "## Evidence limits (operator review)" in markdown
    evidence_limits = markdown.split("## Evidence limits (operator review)", 1)[1]
    assert "What remains unknown" in evidence_limits and "How to verify" in evidence_limits
    assert "What is wrong" not in evidence_limits and "What we would fix" not in evidence_limits
    assert "DATAFORSEO_LOGIN" not in markdown and "DATAFORSEO_PASSWORD" not in markdown
    assert all(item["finding_type"] == "prospect_issue" for item in report.key_actions)


def test_v2_markdown_humanizes_every_effort_confidence_and_service_enum():
    target = SEOTarget(
        input_url="example.com",
        normalized_url="https://example.com/",
        normalized_domain="example.com",
    )
    efforts = ("small", "medium", "large", "discovery_required")
    confidences = ("low", "medium", "high", "low")
    services = (
        "web_development_rebuild",
        "profile_management_reputation",
        "pseo_search_architecture",
        "web_development_rebuild",
    )
    findings = [
        {
            "finding_type": "prospect_issue",
            "title": f"Finding {index}",
            "observation": "Observed issue.",
            "impact": "Supported impact.",
            "recommended_action": "Correct the issue.",
            "recommended_services": [service],
            "service_fit_reason": "Supported service fit.",
            "confidence": confidence,
            "effort": effort,
            "evidence_refs": [],
        }
        for index, (effort, confidence, service) in enumerate(zip(efforts, confidences, services), 1)
    ]

    markdown = ReportAssemblyService._markdown_v2(
        target,
        "Executive answer.",
        findings,
        {
            "mode": "quick",
            "limits": {},
            "budget": {},
            "scored_dimensions": [],
            "completeness_percent": 0,
            "warnings": [],
        },
    )

    for label in ("Small", "Medium", "Large", "Discovery required"):
        assert f"- Effort: {label}" in markdown
    for label in ("Low", "Medium", "High"):
        assert f"- Confidence: {label}" in markdown
    for label in (
        "Website development / rebuild",
        "Profile management / reputation",
        "pSEO / search architecture",
    ):
        assert label in markdown
    for raw_token in (*efforts, *set(confidences), *services):
        assert raw_token not in markdown


def test_v1_markdown_sanitizes_unconfigured_search_credential_reason_only_for_display():
    target = SEOTarget(
        input_url="example.com",
        normalized_url="https://example.com/",
        normalized_domain="example.com",
    )
    run = InsightRun(
        seo_target_id=target.id,
        requested_url=target.normalized_url,
        requested_domain=target.normalized_domain,
    )
    search = unknown_search()
    crawl_output = crawl(valid=["https://example.com/sitemap.xml"])
    pages = PageAnalysisOutput(pages=[page(target.normalized_url, "page-1")])
    score = ScorecardService().build(crawl_output, pages, search, target_context=context())

    report = ReportAssemblyService().build_report(target, run, crawl_output, pages, search, score)

    markdown = report.export_markdown
    assert "DATAFORSEO_LOGIN" not in markdown
    assert "DATAFORSEO_PASSWORD" not in markdown
    assert "Target-specific search evidence" in markdown
    assert "not configured" in markdown
    assert report.report_payload["search"]["skipped_reason"] == search.skipped_reason
    search_ref = next(
        ref
        for action in report.key_actions
        if action["source_stage"] == "pulling_search_intelligence"
        for ref in action["evidence_refs"]
    )
    assert search_ref["reason"] == search.skipped_reason


def test_v2_method_and_limits_humanizes_scored_dimension_names():
    target = SEOTarget(
        input_url="example.com",
        normalized_url="https://example.com/",
        normalized_domain="example.com",
    )
    dimensions = (
        "sitemap_quality",
        "metadata_quality",
        "page_coverage",
        "search_visibility",
    )

    markdown = ReportAssemblyService._markdown_v2(
        target,
        "Executive answer.",
        [],
        {
            "mode": "quick",
            "limits": {},
            "budget": {},
            "scored_dimensions": list(dimensions),
            "completeness_percent": 100,
            "warnings": [],
        },
    )

    assert "- Scored dimensions: Sitemap quality, Metadata quality, Page coverage, Search visibility" in markdown
    for raw_token in dimensions:
        assert raw_token not in markdown


def test_finding_ids_ignore_random_page_record_ids():
    kwargs = dict(target_context=context(), stage_artifacts=stage_paths())
    first = FindingService().build_findings(
        crawl(valid=["https://example.com/sitemap.xml"]),
        PageAnalysisOutput(pages=[page("https://example.com/a", "random-a", title=None)]),
        valid_search(), **kwargs,
    )
    second = FindingService().build_findings(
        crawl(valid=["https://example.com/sitemap.xml"]),
        PageAnalysisOutput(pages=[page("https://example.com/a", "random-b", title=None)]),
        valid_search(), **kwargs,
    )
    assert [item.id for item in first] == [item.id for item in second]


def test_stage_event_artifact_path_is_used_and_legacy_fallback_remains(tmp_path: Path):
    repo = FileBackedInsightRepository(tmp_path / "artifacts")
    run = InsightRun(id="run-1", seo_target_id="target-1", requested_url="https://example.com/", requested_domain="example.com")
    repo.create_run(run)
    explicit = RunStageEvent(
        id="event-1", insight_run_id=run.id, stage_name="scoring", status="completed",
        artifact_path="events/event-1.json",
    )
    repo.append_stage_event(explicit)
    assert (tmp_path / "artifacts" / "runs" / run.id / "events" / "event-1.json").exists()
    legacy = RunStageEvent(id="event-2", insight_run_id=run.id, stage_name="scoring", status="completed")
    repo.append_stage_event(legacy)
    assert len(repo.list_stage_events(run.id)) == 2


def _seed_v2_validation(tmp_path: Path):
    repo = FileBackedInsightRepository(tmp_path / "artifacts")
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    run = orch.start("example.com", mode="quick", max_pages=1)
    return repo, orch, run


def test_v2_refs_are_independent_resolvable_and_observed_matches(tmp_path: Path):
    repo, orch, run = _seed_v2_validation(tmp_path)
    report = repo.get_report(run.id, "v2")
    assert report is not None
    for finding in report.report_payload["findings"]:
        for ref in finding["evidence_refs"]:
            assert ref["artifact_path"].startswith(("pages/", "events/"))
            assert "observed" in ref
            assert not ref["artifact_path"].startswith("reports/v2")
    assert orch.validate(run.id)["valid"] is True


@pytest.mark.parametrize("bad_path", ["reports/v2.json", "../run.json", "/tmp/outside.json", "events/missing.json"])
def test_v2_validator_rejects_unsafe_or_unresolvable_evidence_paths(tmp_path: Path, bad_path: str):
    repo, orch, run = _seed_v2_validation(tmp_path)
    report = repo.get_report(run.id, "v2")
    assert report is not None and report.report_payload["findings"]
    report.report_payload["findings"][0]["evidence_refs"][0]["artifact_path"] = bad_path
    repo.save_report(report)
    assert orch.validate(run.id)["report_v2_findings_valid"] is False


def test_v2_validator_rejects_observed_mismatch_and_unsupported_routes(tmp_path: Path):
    repo, orch, run = _seed_v2_validation(tmp_path)
    report = repo.get_report(run.id, "v2")
    assert report is not None and report.report_payload["findings"]
    finding = report.report_payload["findings"][0]
    finding["evidence_refs"][0]["observed"] = "tampered"
    finding["recommended_services"] = ["profile_management_reputation"]
    repo.save_report(report)
    assert orch.validate(run.id)["report_v2_findings_valid"] is False


def test_empty_v2_finding_list_is_valid(tmp_path: Path):
    repo, orch, run = _seed_v2_validation(tmp_path)
    report = repo.get_report(run.id, "v2")
    assert report is not None
    report.report_payload["findings"] = []
    report.report_payload["next_best_action"] = None
    report.report_payload["key_actions"] = []
    report.key_actions = []
    repo.save_report(report)
    assert orch.validate(run.id)["report_v2_findings_valid"] is True


def test_genuinely_legacy_v1_scoring_event_does_not_require_new_semantics(tmp_path: Path):
    repo = FileBackedInsightRepository(tmp_path / "artifacts")
    run = InsightRun(
        id="legacy-run", seo_target_id="target-1", requested_url="https://example.com/", requested_domain="example.com",
        status="completed", current_stage="completed", started_at="2026-07-22T00:00:00+00:00",
        heartbeat_at="2026-07-22T00:00:01+00:00", completed_at="2026-07-22T00:00:02+00:00",
        summary={"overall_score": 50.0},
        input_payload={"limits": {"max_pages": 1, "max_dataforseo_calls": 0}, "budget": {"estimated_paid_api_calls": 0}},
        config_snapshot={"dataforseo_configured": False, "run_limits": {"max_pages": 1}},
    )
    repo.create_run(run)
    for order, stage in enumerate(DEFAULT_STAGES, 1):
        summary = {"overall_score": 50.0, "metrics": {"page_count": 1}} if stage == "scoring" else {}
        if stage == "pulling_search_intelligence":
            summary = {"configured": False, "approved": False, "skipped_reason": "not configured", "payload_keys": []}
        repo.append_stage_event(RunStageEvent(insight_run_id=run.id, stage_name=stage, stage_order=order, status="completed", output_summary=summary))
    repo.save_report(InsightReport(
        insight_run_id=run.id, seo_target_id=run.seo_target_id, report_payload={},
        key_actions=[{"action": "Review", "evidence_refs": [{"artifact_path": "run.json", "field": "summary", "reason": "Legacy evidence"}]}],
        export_markdown="# legacy\n",
    ))
    assert InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts").validate(run.id)["valid"] is True


def test_pipeline_result_path_remains_v1_while_run_advertises_v2(tmp_path: Path):
    repo = FileBackedInsightRepository(tmp_path / "artifacts")
    pipeline = InsightRunPipeline(repo, InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts").config, tmp_path / "artifacts")
    result = pipeline.run("example.com", mode="quick", max_pages=1)
    assert result.report_path is not None and result.report_path.endswith("reports/v1.json")
    assert result.run.summary["primary_report_version"] == "v2"
