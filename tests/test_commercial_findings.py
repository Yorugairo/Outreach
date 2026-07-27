from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

import pytest

from src.models import CommercialFinding, InsightRun, PageRecord, SEOTarget
from src.services.crawl_discovery_service import CrawlDiscoveryOutput
from src.services.finding_service import FindingService
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.reporting_service import ReportAssemblyService, ScorecardService
from src.services.search_intelligence_service import SearchIntelligenceOutput, TargetContext


REQUIRED_FIELDS = {
    "id",
    "finding_type",
    "category",
    "title",
    "observation",
    "impact",
    "recommended_action",
    "severity",
    "effort",
    "confidence",
    "recommended_services",
    "service_fit_reason",
    "evidence_refs",
    "evidence_family",
}
ALLOWED_SEVERITIES = {"critical", "high", "medium", "low", "info"}
ALLOWED_EFFORTS = {"small", "medium", "large", "discovery_required"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_SERVICES = {
    "web_development_rebuild",
    "profile_management_reputation",
    "pseo_search_architecture",
}

TARGET_CONTEXT = TargetContext(
    primary_url="https://example.com/",
    target_domain="example.com",
    language_code="en",
    device="desktop",
    location_code=None,
    market="United States",
)
STAGE_ARTIFACTS = {
    "discovering_sitemaps": "events/discovering_sitemaps-completed.json",
    "fetching_pages": "events/fetching_pages-completed.json",
    "pulling_search_intelligence": "events/pulling_search_intelligence-completed.json",
}


def crawl(*, validated: list[str] | None = None, candidates: list[str] | None = None, errors: list[str] | None = None):
    return CrawlDiscoveryOutput(
        robots_url="https://example.com/robots.txt",
        robots_status=200,
        sitemap_urls=validated or [],
        candidate_sitemap_urls=candidates or [],
        candidate_page_urls=[],
        errors=errors or [],
    )


def page(
    url: str,
    *,
    record_id: str,
    title: str | None = "Title",
    meta: str | None = "Description",
    h1: str | None = "Heading",
    indexable: bool = True,
):
    return PageRecord(
        id=record_id,
        insight_run_id="run-1",
        seo_target_id="target-1",
        url=url,
        fetch_status="fetched",
        http_status=200,
        title=title,
        meta_description=meta,
        h1=h1,
        indexable=indexable,
    )


def search_valid():
    return SearchIntelligenceOutput(
        configured=True,
        approved=True,
        skipped_reason=None,
        payload={
            "visibility_score": 50,
            "target_domain": "example.com",
            "snapshot_date": "2026-07-22",
            "language_code": "en",
            "device": "desktop",
            "market": "United States",
            "source": "rank-tracker",
            "observed_ranking_urls": ["https://example.com/service"],
        },
    )


def search_unknown(*, configured: bool = False, approved: bool = False, payload=None, reason="not configured"):
    return SearchIntelligenceOutput(
        configured=configured,
        approved=approved,
        skipped_reason=reason,
        payload=payload or {},
    )


def build_findings(crawl_output=None, page_output=None, search_output=None):
    return FindingService().build_findings(
        crawl_output or crawl(validated=["https://example.com/sitemap.xml"]),
        page_output or PageAnalysisOutput(),
        search_output or search_valid(),
        target_context=TARGET_CONTEXT,
        stage_artifacts=STAGE_ARTIFACTS,
    )


def test_commercial_finding_has_exact_required_fields_and_validates_enums_and_provenance():
    assert {field.name for field in fields(CommercialFinding)} == REQUIRED_FIELDS
    finding = CommercialFinding(
        id="finding-1",
        finding_type="prospect_issue",
        category="technical",
        title="Observed issue",
        observation="A persisted fact was observed.",
        impact="Search engines may receive incomplete page information.",
        recommended_action="Correct the persisted issue and verify it.",
        severity="medium",
        effort="small",
        confidence="high",
        recommended_services=["web_development_rebuild"],
        service_fit_reason="The observed website fact supports website remediation.",
        evidence_refs=[
            {
                "artifact_path": "pages/page-1.json",
                "field": "title",
                "reason": "Title is absent.",
                "observed": None,
            }
        ],
    )
    assert finding.to_dict()["severity"] in ALLOWED_SEVERITIES

    base = finding.to_dict()
    for field_name, invalid in [
        ("severity", "urgent"),
        ("effort", "tiny"),
        ("confidence", "certain"),
        ("recommended_services", ["sales_package"]),
        ("evidence_refs", []),
        ("evidence_family", "unsupported"),
    ]:
        kwargs = {**base, field_name: invalid}
        with pytest.raises(ValueError):
            CommercialFinding(**kwargs)


def test_findings_have_deterministic_ids_stable_rule_order_and_sorted_evidence():
    pages_a = PageAnalysisOutput(
        pages=[
            page("https://example.com/z", record_id="z", title=None, meta=None, h1=None),
            page("https://example.com/a", record_id="a", title=None, h1=None),
        ]
    )
    pages_b = PageAnalysisOutput(pages=list(reversed(pages_a.pages)))
    first = build_findings(crawl(), pages_a, search_unknown())
    second = build_findings(crawl(), pages_b, search_unknown())
    third = build_findings(crawl(), pages_a, search_unknown())

    assert [finding.to_dict() for finding in first] == [finding.to_dict() for finding in second]
    assert [finding.to_dict() for finding in first] == [finding.to_dict() for finding in third]
    assert [finding.category for finding in first] == [
        "sitemap_discovery",
        "page_metadata",
        "page_heading",
        "search_evidence_completeness",
    ]
    assert all(not finding.id.startswith("00000000-") for finding in first)
    for finding in first:
        assert finding.evidence_refs == sorted(
            finding.evidence_refs,
            key=lambda ref: (ref["artifact_path"], ref["field"], ref["reason"]),
        )


def test_multi_page_finding_ids_ignore_swapped_page_record_ids_while_evidence_resolves(tmp_path: Path):
    def build_with_artifacts(root: Path, page_ids: tuple[str, str]):
        pages = [
            page("https://example.com/a", record_id=page_ids[0], title=None, meta=None, h1=None),
            page("https://example.com/z", record_id=page_ids[1], title=None, meta=None, h1=None),
        ]
        for record in pages:
            artifact = root / "pages" / f"{record.id}.json"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(json.dumps(record.to_dict()), encoding="utf-8")
        findings = build_findings(page_output=PageAnalysisOutput(pages=pages))
        return {finding.category: finding for finding in findings}

    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first = build_with_artifacts(first_root, ("a-id", "z-id"))
    second = build_with_artifacts(second_root, ("z-id", "a-id"))

    for category in ("page_metadata", "page_heading"):
        assert first[category].id == second[category].id
        first_paths_by_url = {
            (ref["url"], ref["field"]): ref["artifact_path"] for ref in first[category].evidence_refs
        }
        second_paths_by_url = {
            (ref["url"], ref["field"]): ref["artifact_path"] for ref in second[category].evidence_refs
        }
        assert first_paths_by_url != second_paths_by_url

        for root, finding in ((first_root, first[category]), (second_root, second[category])):
            for ref in finding.evidence_refs:
                payload = json.loads((root / ref["artifact_path"]).read_text(encoding="utf-8"))
                assert payload["url"] == ref["url"]
                assert payload[ref["field"]] == ref["observed"]


def test_absent_and_inconclusive_sitemap_evidence_are_unrouted_evidence_limits():
    absent = build_findings(crawl(), PageAnalysisOutput(), search_valid())[0]
    inconclusive = build_findings(
        crawl(candidates=["https://example.com/sitemap.xml"], errors=["sitemap_parse_failed"]),
        PageAnalysisOutput(),
        search_valid(),
    )[0]

    assert absent.category == inconclusive.category == "sitemap_discovery"
    assert "no sitemap candidate" in absent.observation.lower()
    assert "candidate" in inconclusive.observation.lower() and "inconclusive" in inconclusive.observation.lower()
    assert absent.id != inconclusive.id
    assert absent.finding_type == inconclusive.finding_type == "evidence_limit"
    assert absent.recommended_services == inconclusive.recommended_services == []


@pytest.mark.parametrize("outcome", ["HTTP 404", "HTTP 410", "malformed XML"])
def test_conclusive_invalid_sitemap_candidate_routes_web_development(outcome: str):
    finding = build_findings(
        crawl(
            candidates=["https://example.com/sitemap.xml"],
            errors=[f"sitemap_parse_failed:https://example.com/sitemap.xml: {outcome}"],
        ),
        PageAnalysisOutput(),
        search_valid(),
    )[0]

    assert finding.category == "sitemap_discovery"
    assert finding.finding_type == "prospect_issue"
    assert finding.recommended_services == ["web_development_rebuild"]


def test_metadata_and_h1_findings_ignore_non_indexable_pages():
    pages = PageAnalysisOutput(
        pages=[page("https://example.com/private", record_id="private", title=None, meta=None, h1=None, indexable=False)]
    )
    assert build_findings(page_output=pages) == []


def test_insufficient_site_evidence_produces_no_finding():
    assert build_findings() == []


def test_fetch_errors_are_recheck_warning_with_persisted_evidence_and_no_route():
    findings = build_findings(
        page_output=PageAnalysisOutput(errors=[{"url": "https://example.com/down", "error": "timeout"}])
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding.category == "page_fetch_evidence"
    assert finding.finding_type == "evidence_limit"
    assert finding.recommended_services == []
    assert finding.evidence_refs[0]["artifact_path"] == STAGE_ARTIFACTS["fetching_pages"]
    assert finding.evidence_refs[0]["field"].startswith("output_summary.errors")
    assert finding.evidence_refs[0]["observed"] == {
        "url": "https://example.com/down",
        "error": "timeout",
    }


def test_unknown_or_non_target_specific_search_is_unrouted_evidence_warning():
    cases = [
        search_unknown(),
        search_unknown(configured=True, approved=False, reason="approval required"),
        search_unknown(configured=True, approved=True, payload={"status_code": 200}, reason=None),
    ]
    for search_output in cases:
        findings = build_findings(search_output=search_output)
        assert len(findings) == 1
        assert findings[0].category == "search_evidence_completeness"
        assert findings[0].finding_type == "evidence_limit"
        assert findings[0].recommended_services == []
        assert findings[0].severity == "info"


def test_current_technical_evidence_never_routes_profile_management_or_pseo():
    findings = build_findings(
        crawl(),
        PageAnalysisOutput(
            pages=[page("https://example.com/service", record_id="service", title=None, meta=None, h1=None)],
            errors=[{"url": "https://example.com/error", "error": "timeout"}],
        ),
        search_unknown(),
    )
    routed = {service for finding in findings for service in finding.recommended_services}
    assert routed <= {"web_development_rebuild"}
    assert "profile_management_reputation" not in routed
    assert "pseo_search_architecture" not in routed


def test_findings_contain_no_financial_guarantee_or_fabricated_traffic_revenue_language():
    findings = build_findings(
        crawl(),
        PageAnalysisOutput(
            pages=[page("https://example.com/a", record_id="a", title=None, meta=None, h1=None)],
            errors=[{"url": "https://example.com/b", "error": "timeout"}],
        ),
        search_unknown(),
    )
    rendered = " ".join(str(finding.to_dict()) for finding in findings).lower()
    assert "$" not in rendered
    assert "guaranteed" not in rendered
    assert "traffic loss" not in rendered
    assert "revenue loss" not in rendered


def test_v2_report_selects_highest_ranked_routed_action_not_unrouted_warning():
    target = SEOTarget(
        id="target-1",
        input_url="example.com",
        normalized_url="https://example.com/",
        normalized_domain="example.com",
    )
    run = InsightRun(
        id="run-1",
        seo_target_id=target.id,
        requested_url=target.normalized_url,
        requested_domain=target.normalized_domain,
        mode="quick",
        input_payload={"limits": {"max_pages": 2}, "budget": {"estimated_paid_api_calls": 0}},
    )
    crawl_output = crawl(validated=["https://example.com/sitemap.xml"])
    page_output = PageAnalysisOutput(
        pages=[page("https://example.com/a", record_id="a", title=None, meta=None)],
        errors=[{"url": "https://example.com/b", "error": "timeout"}],
    )
    search_output = search_unknown()
    scorecard = ScorecardService().build(
        crawl_output, page_output, search_output, target_context=TARGET_CONTEXT
    )

    report = ReportAssemblyService().build_report_v2(
        target,
        run,
        crawl_output,
        page_output,
        search_output,
        scorecard,
        target_context=TARGET_CONTEXT,
        stage_artifacts=STAGE_ARTIFACTS,
    )
    payload = report.report_payload

    assert report.report_version == "v2"
    assert payload["next_best_action"]["category"] == "page_metadata"
    assert payload["next_best_action"]["recommended_services"] == ["web_development_rebuild"]
    assert set(payload["method_and_limits"]) == {
        "mode", "limits", "budget", "scored_dimensions", "completeness_percent", "warnings"
    }
    assert all(key in payload for key in ("target", "run", "crawl", "pages", "page_errors", "search", "scorecard"))
    for heading in ("What is wrong", "Why it matters", "What we would fix", "Service fit", "Evidence", "Method and limits"):
        assert heading in report.export_markdown


def test_v2_report_is_truthful_when_no_service_is_supported():
    target = SEOTarget(input_url="example.com", normalized_url="https://example.com/", normalized_domain="example.com")
    run = InsightRun(seo_target_id=target.id, requested_url=target.normalized_url, requested_domain=target.normalized_domain)
    crawl_output = crawl(validated=["https://example.com/sitemap.xml"])
    pages = PageAnalysisOutput()
    search_output = search_unknown()
    scorecard = ScorecardService().build(
        crawl_output, pages, search_output, target_context=TARGET_CONTEXT
    )
    report = ReportAssemblyService().build_report_v2(
        target,
        run,
        crawl_output,
        pages,
        search_output,
        scorecard,
        target_context=TARGET_CONTEXT,
        stage_artifacts=STAGE_ARTIFACTS,
    )

    assert report.report_payload["next_best_action"] is None
    assert "No supported commercial service route" in report.export_markdown
