from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.fetchers.sitemap_fetcher import SitemapDiscoveryResult  # noqa: E402
from src.models import InsightRun, SEOTarget  # noqa: E402
from src.services.crawl_discovery_service import CrawlDiscoveryService  # noqa: E402
from src.services.page_analysis_service import PageAnalysisOutput  # noqa: E402
from src.services.reporting_service import ReportAssemblyService, ScorecardService  # noqa: E402
from src.services.search_intelligence_service import SearchIntelligenceOutput  # noqa: E402


SITEMAP_URL = "https://example.test/sitemap.xml"
ROBOTS_URL = "https://example.test/robots.txt"
PAGE_URL = "https://example.test/services"


class _FailingSitemapFetcher:
    def discover(self, domain: str) -> SitemapDiscoveryResult:
        assert domain == "example.test"
        return SitemapDiscoveryResult(
            domain="https://example.test",
            robots_url=ROBOTS_URL,
            robots_status=200,
            sitemap_urls=[SITEMAP_URL],
        )

    def fetch_sitemap_urls(self, sitemap_url: str) -> list[str]:
        assert sitemap_url == SITEMAP_URL
        raise OSError("404 fixture")


class _SuccessfulSitemapFetcher:
    def discover(self, domain: str) -> SitemapDiscoveryResult:
        assert domain == "example.test"
        return SitemapDiscoveryResult(
            domain="https://example.test",
            robots_url=ROBOTS_URL,
            robots_status=200,
            sitemap_urls=[SITEMAP_URL],
        )

    def fetch_sitemap_urls(self, sitemap_url: str) -> list[str]:
        assert sitemap_url == SITEMAP_URL
        return [PAGE_URL]


def _target() -> SEOTarget:
    return SEOTarget(
        id="target-1",
        input_url="example.test",
        normalized_url="https://example.test",
        normalized_domain="example.test",
    )


def _run(target: SEOTarget) -> InsightRun:
    return InsightRun(
        id="run-1",
        seo_target_id=target.id,
        requested_url=target.normalized_url,
        requested_domain=target.normalized_domain,
    )


def _unconfigured_search() -> SearchIntelligenceOutput:
    return SearchIntelligenceOutput(
        configured=False,
        skipped_reason="not configured in fixture",
        payload={},
    )


def test_failed_sitemap_candidate_is_not_validated_or_scored():
    target = _target()
    service = CrawlDiscoveryService()
    service.fetcher = _FailingSitemapFetcher()

    crawl, assets = service.discover(target, "run-1")

    assert crawl.sitemap_urls == []
    assert crawl.candidate_sitemap_urls == [SITEMAP_URL]
    assert crawl.errors == [f"sitemap_parse_failed:{SITEMAP_URL}: 404 fixture"]

    sitemap_assets = [asset for asset in assets if asset.asset_type == "sitemap"]
    assert len(sitemap_assets) == 1
    sitemap_asset = sitemap_assets[0]
    assert sitemap_asset.url == SITEMAP_URL
    assert sitemap_asset.metadata == {
        "validation_status": "failed",
        "validation_error": "404 fixture",
    }

    pages = PageAnalysisOutput()
    search = _unconfigured_search()
    scorecard = ScorecardService().build(crawl, pages, search)
    assert scorecard.metrics["sitemap_count"] == 0
    assert scorecard.sitemap_quality_score == 20.0

    report = ReportAssemblyService().build_report(
        target,
        _run(target),
        crawl,
        pages,
        search,
        scorecard,
    )
    report_crawl = report.report_payload["crawl"]
    assert report_crawl["sitemap_urls"] == []
    assert report_crawl["candidate_sitemap_urls"] == [SITEMAP_URL]
    assert report_crawl["errors"] == [f"sitemap_parse_failed:{SITEMAP_URL}: 404 fixture"]

    sitemap_action = next(action for action in report.key_actions if action["source_stage"] == "discovering_sitemaps")
    assert sitemap_action["evidence_refs"][0]["reason"] == "No sitemap URLs were validated for this run."

    json.dumps(report.to_dict())
    json.dumps(sitemap_asset.to_dict())


def test_successfully_parsed_sitemap_remains_validated():
    service = CrawlDiscoveryService()
    service.fetcher = _SuccessfulSitemapFetcher()

    crawl, assets = service.discover(_target(), "run-1")

    assert crawl.candidate_sitemap_urls == [SITEMAP_URL]
    assert crawl.sitemap_urls == [SITEMAP_URL]
    assert crawl.candidate_page_urls == [PAGE_URL]

    sitemap_asset = next(asset for asset in assets if asset.asset_type == "sitemap")
    assert sitemap_asset.metadata == {"validation_status": "validated"}
    assert "validation_error" not in sitemap_asset.metadata

    scorecard = ScorecardService().build(crawl, PageAnalysisOutput(), _unconfigured_search())
    assert scorecard.metrics["sitemap_count"] == 1
