from __future__ import annotations

from src.models import PageRecord
from src.services.crawl_discovery_service import CrawlDiscoveryOutput
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.technical_seo_health_service import TechnicalSEOHealthService


def _page(
    url: str,
    page_class: str,
    *,
    title: str | None = "Example title",
    description: str | None = "Example description",
    h1: str | None = "Example heading",
    depth: int = 1,
    navigation: bool = True,
    sitemap: bool = True,
    word_count: int = 400,
) -> PageRecord:
    return PageRecord(
        insight_run_id="run-1",
        seo_target_id="target-1",
        url=url,
        canonical_url=url,
        normalized_path="/",
        page_class=page_class,
        fetch_status="fetched",
        http_status=200,
        content_type="text/html",
        title=title,
        meta_description=description,
        h1=h1,
        canonical_status="present",
        indexable=True,
        word_count=word_count,
        internal_links=[],
        ai_evidence={
            "h1_count": 1,
            "heading_hierarchy_valid": True,
            "in_navigation": navigation,
            "in_sitemap": sitemap,
            "json_ld_valid": True,
            "json_ld_visible_alignment": True,
            "json_ld_alignment": [{"type": "Organization", "aligned": True}],
            "entity_names": ["Example Academy"],
            "mobile_viewport": True,
        },
        fetch_metadata={
            "fetched_url": url,
            "crawl_depth": 0 if page_class == "homepage" else depth,
        },
    )


def _crawl(pages: list[PageRecord]) -> CrawlDiscoveryOutput:
    return CrawlDiscoveryOutput(
        robots_url="https://example.com/robots.txt",
        robots_status=200,
        sitemap_urls=["https://example.com/sitemap.xml"],
        candidate_sitemap_urls=["https://example.com/sitemap.xml"],
        candidate_page_urls=[page.url for page in pages],
        robots_access={
            "googlebot": True,
            "bingbot": True,
            "oai-searchbot": True,
        },
    )


def _performance(pages: list[PageRecord]) -> dict:
    return {
        page.id: {
            "source": "crux",
            "status": "good",
            "metrics": {"lcp_ms": 1800, "inp_ms": 120, "cls": 0.05},
            "artifact_ref": f"performance/{page.id}.json",
        }
        for page in pages
    }


def _check(output, check_id: str) -> dict:
    return next(item for item in output.checks if item["check_id"] == check_id)


def test_clean_site_wide_evidence_produces_complete_health_without_touching_legacy_score() -> None:
    pages = [
        _page("https://example.com/", "homepage", title="Home", h1="Home"),
        _page(
            "https://example.com/classes",
            "service",
            title="Classes",
            h1="Classes",
        ),
    ]
    output = TechnicalSEOHealthService().build(
        _crawl(pages),
        PageAnalysisOutput(
            pages=pages,
            discovered_count=2,
            attempted_count=2,
        ),
        page_limit=100,
        attempt_id="attempt-1",
        performance_evidence=_performance(pages),
    )
    assert output.version == "seo-health.v2"
    assert output.score == 100
    assert output.status == "complete"
    assert output.completeness_percent == 100
    assert output.evidence_confidence == 100
    assert output.metrics["legacy_overall_score_affected"] is False
    assert len(output.families) == 5


def test_missing_optional_performance_is_unknown_not_a_score_penalty() -> None:
    pages = [_page("https://example.com/", "homepage")]
    with_performance = TechnicalSEOHealthService().build(
        _crawl(pages),
        PageAnalysisOutput(pages=pages, discovered_count=1, attempted_count=1),
        performance_evidence=_performance(pages),
    )
    without_performance = TechnicalSEOHealthService().build(
        _crawl(pages),
        PageAnalysisOutput(pages=pages, discovered_count=1, attempted_count=1),
    )
    performance = _check(without_performance, "field_page_experience")
    assert performance["status"] == "unknown"
    assert performance["score"] is None
    assert without_performance.score == with_performance.score
    assert without_performance.completeness_percent < with_performance.completeness_percent


def test_issue_density_uses_all_applicable_pages_and_page_importance() -> None:
    pages = [
        _page("https://example.com/", "homepage", title="Home", h1="Home"),
        _page(
            "https://example.com/classes",
            "service",
            title=None,
            description=None,
            h1=None,
        ),
        _page("https://example.com/kids", "service", title="Kids", h1="Kids"),
    ]
    output = TechnicalSEOHealthService().build(
        _crawl(pages),
        PageAnalysisOutput(pages=pages, discovered_count=3, attempted_count=3),
        performance_evidence=_performance(pages),
    )
    metadata = _check(output, "metadata_completeness")
    assert metadata["status"] == "failed"
    assert metadata["affected_page_ids"] == [pages[1].id]
    assert 0 < metadata["weighted_affected_ratio"] < 1
    assert output.families["on_page_template"]["score"] < 100
    assert output.score < 100


def test_capped_collection_reduces_confidence_without_inventing_link_failures() -> None:
    pages = [_page("https://example.com/", "homepage")]
    output = TechnicalSEOHealthService().build(
        _crawl(pages),
        PageAnalysisOutput(
            pages=pages,
            discovered_count=10,
            attempted_count=1,
            capped=True,
        ),
        page_limit=1,
    )
    link_health = _check(output, "internal_link_health")
    assert link_health["status"] == "unknown"
    assert output.score is not None
    assert output.evidence_confidence < output.completeness_percent
    assert "collected site evidence" in " ".join(output.warnings)


def test_conclusive_fetch_and_internal_link_errors_are_scored_but_ambiguous_errors_are_limits() -> None:
    pages = [_page("https://example.com/", "homepage")]
    errors = [
        {
            "source_url": "https://example.com/",
            "target_url": "https://example.com/broken",
            "http_status": 404,
            "failure_kind": "http_error",
            "conclusive": True,
        },
        {
            "source_url": "https://example.com/",
            "target_url": "https://example.com/slow",
            "http_status": None,
            "failure_kind": "inconclusive",
            "conclusive": False,
        },
    ]
    output = TechnicalSEOHealthService().build(
        _crawl(pages),
        PageAnalysisOutput(
            pages=pages,
            errors=errors,
            discovered_count=3,
            attempted_count=3,
        ),
        attempt_id="attempt-1",
        performance_evidence=_performance(pages),
    )
    response = _check(output, "response_eligibility")
    links = _check(output, "internal_link_health")
    assert response["status"] == "failed"
    assert response["evidence_confidence"] < 1
    assert links["status"] == "failed"
    assert links["affected_page_ids"] == [pages[0].id]
