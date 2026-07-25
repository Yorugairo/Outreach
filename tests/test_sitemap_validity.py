from __future__ import annotations

import io
import json
import sys
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.fetchers import sitemap_fetcher as sitemap_fetcher_module  # noqa: E402
from src.fetchers.sitemap_fetcher import SitemapDiscoveryResult, SitemapFetcher  # noqa: E402
from src.models import InsightRun, SEOTarget  # noqa: E402
from src.services.crawl_discovery_service import (  # noqa: E402
    CrawlDiscoveryService,
    sitemap_evidence_status,
)
from src.services.page_analysis_service import PageAnalysisOutput  # noqa: E402
from src.services.reporting_service import ReportAssemblyService, ScorecardService  # noqa: E402
from src.services.search_intelligence_service import SearchIntelligenceOutput, TargetContext  # noqa: E402


SITEMAP_URL = "https://example.test/sitemap.xml"
ROBOTS_URL = "https://example.test/robots.txt"
PAGE_URL = "https://example.test/services"
TARGET_CONTEXT = TargetContext(
    primary_url="https://example.test/",
    target_domain="example.test",
    language_code="en",
    device="desktop",
    location_code=None,
    market="United States",
)


@pytest.mark.parametrize(
    ("xml_body", "expected_urls"),
    [
        (
            "<urlset><url><loc>https://example.test/plain</loc></url></urlset>",
            ["https://example.test/plain"],
        ),
        (
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://example.test/namespaced</loc></url></urlset>",
            ["https://example.test/namespaced"],
        ),
        (
            "<sitemapindex><sitemap><loc>https://example.test/child.xml</loc></sitemap></sitemapindex>",
            ["https://example.test/child.xml"],
        ),
        (
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<sitemap><loc>https://example.test/namespaced-child.xml</loc></sitemap></sitemapindex>",
            ["https://example.test/namespaced-child.xml"],
        ),
    ],
)
def test_fetch_sitemap_urls_accepts_exact_supported_roots(monkeypatch, xml_body, expected_urls):
    monkeypatch.setattr(
        sitemap_fetcher_module.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: io.BytesIO(xml_body.encode("utf-8")),
    )

    assert SitemapFetcher().fetch_sitemap_urls(SITEMAP_URL) == expected_urls


@pytest.mark.parametrize(
    "xml_body",
    [
        "<html><body>not a sitemap</body></html>",
        "<feed><entry>arbitrary XML</entry></feed>",
        "<noturlset><url><loc>https://example.test/lookalike</loc></url></noturlset>",
        "<notsitemapindex><sitemap><loc>https://example.test/lookalike.xml</loc></sitemap></notsitemapindex>",
    ],
)
def test_fetch_sitemap_urls_rejects_well_formed_unsupported_or_lookalike_roots(monkeypatch, xml_body):
    monkeypatch.setattr(
        sitemap_fetcher_module.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: io.BytesIO(xml_body.encode("utf-8")),
    )

    with pytest.raises(sitemap_fetcher_module.InvalidSitemapError, match="invalid sitemap root"):
        SitemapFetcher().fetch_sitemap_urls(SITEMAP_URL)


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
        raise urllib.error.HTTPError(sitemap_url, 404, "Not Found", None, None)


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


class _GoneSitemapFetcher(_FailingSitemapFetcher):
    def fetch_sitemap_urls(self, sitemap_url: str) -> list[str]:
        assert sitemap_url == SITEMAP_URL
        raise urllib.error.HTTPError(sitemap_url, 410, "Gone", None, None)


class _MalformedSitemapFetcher(_FailingSitemapFetcher):
    def fetch_sitemap_urls(self, sitemap_url: str) -> list[str]:
        assert sitemap_url == SITEMAP_URL
        raise ET.ParseError("syntax error: line 1, column 0")


class _TransientSitemapFetcher(_FailingSitemapFetcher):
    def fetch_sitemap_urls(self, sitemap_url: str) -> list[str]:
        assert sitemap_url == SITEMAP_URL
        raise OSError("timed out")


class _InvalidRootSitemapFetcher(SitemapFetcher):
    def discover(self, domain: str) -> SitemapDiscoveryResult:
        assert domain == "example.test"
        return SitemapDiscoveryResult(
            domain="https://example.test",
            robots_url=ROBOTS_URL,
            robots_status=200,
            sitemap_urls=[SITEMAP_URL],
        )


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


def test_real_http_404_sitemap_failure_is_a_prospect_issue():
    target = _target()
    service = CrawlDiscoveryService()
    service.fetcher = _FailingSitemapFetcher()

    crawl, assets = service.discover(target, "run-1")

    assert crawl.sitemap_urls == []
    assert crawl.candidate_sitemap_urls == [SITEMAP_URL]
    assert sitemap_evidence_status(crawl) == "prospect_issue"
    assert crawl.errors == [
        f"sitemap_parse_failed:{SITEMAP_URL}:failure_kind=conclusive_http_404: HTTP Error 404: Not Found"
    ]

    sitemap_assets = [asset for asset in assets if asset.asset_type == "sitemap"]
    assert len(sitemap_assets) == 1
    sitemap_asset = sitemap_assets[0]
    assert sitemap_asset.url == SITEMAP_URL
    assert sitemap_asset.metadata == {
        "validation_status": "failed",
        "failure_kind": "conclusive_http_404",
        "validation_error": "HTTP Error 404: Not Found",
    }

    pages = PageAnalysisOutput()
    search = _unconfigured_search()
    scorecard = ScorecardService().build(crawl, pages, search, target_context=TARGET_CONTEXT)
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
    assert report_crawl["errors"] == [
        f"sitemap_parse_failed:{SITEMAP_URL}:failure_kind=conclusive_http_404: HTTP Error 404: Not Found"
    ]

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

    scorecard = ScorecardService().build(
        crawl,
        PageAnalysisOutput(),
        _unconfigured_search(),
        target_context=TARGET_CONTEXT,
    )
    assert scorecard.metrics["sitemap_count"] == 1
    assert scorecard.sitemap_quality_score == 60.0


def test_real_http_410_sitemap_failure_is_a_prospect_issue():
    service = CrawlDiscoveryService()
    service.fetcher = _GoneSitemapFetcher()

    crawl, assets = service.discover(_target(), "run-1")

    assert sitemap_evidence_status(crawl) == "prospect_issue"
    assert crawl.errors == [
        f"sitemap_parse_failed:{SITEMAP_URL}:failure_kind=conclusive_http_410: HTTP Error 410: Gone"
    ]
    sitemap_asset = next(asset for asset in assets if asset.asset_type == "sitemap")
    assert sitemap_asset.metadata == {
        "validation_status": "failed",
        "failure_kind": "conclusive_http_410",
        "validation_error": "HTTP Error 410: Gone",
    }
    scorecard = ScorecardService().build(
        crawl,
        PageAnalysisOutput(),
        _unconfigured_search(),
        target_context=TARGET_CONTEXT,
    )
    assert scorecard.sitemap_quality_score == 20.0


def test_real_parse_error_sitemap_failure_is_a_prospect_issue():
    service = CrawlDiscoveryService()
    service.fetcher = _MalformedSitemapFetcher()

    crawl, assets = service.discover(_target(), "run-1")

    assert sitemap_evidence_status(crawl) == "prospect_issue"
    assert crawl.errors == [
        f"sitemap_parse_failed:{SITEMAP_URL}:failure_kind=malformed_xml: syntax error: line 1, column 0"
    ]
    sitemap_asset = next(asset for asset in assets if asset.asset_type == "sitemap")
    assert sitemap_asset.metadata == {
        "validation_status": "failed",
        "failure_kind": "malformed_xml",
        "validation_error": "syntax error: line 1, column 0",
    }
    scorecard = ScorecardService().build(
        crawl,
        PageAnalysisOutput(),
        _unconfigured_search(),
        target_context=TARGET_CONTEXT,
    )
    assert scorecard.sitemap_quality_score == 20.0


def test_invalid_sitemap_root_is_persisted_as_a_scored_prospect_issue(monkeypatch):
    monkeypatch.setattr(
        sitemap_fetcher_module.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: io.BytesIO(b"<html><body>not a sitemap</body></html>"),
    )
    service = CrawlDiscoveryService()
    service.fetcher = _InvalidRootSitemapFetcher()

    crawl, assets = service.discover(_target(), "run-1")

    assert crawl.sitemap_urls == []
    assert crawl.candidate_sitemap_urls == [SITEMAP_URL]
    assert sitemap_evidence_status(crawl) == "prospect_issue"
    assert crawl.errors == [
        f"sitemap_parse_failed:{SITEMAP_URL}:failure_kind=invalid_sitemap_xml: "
        "invalid sitemap root: 'html'"
    ]
    sitemap_asset = next(asset for asset in assets if asset.asset_type == "sitemap")
    assert sitemap_asset.metadata == {
        "validation_status": "failed",
        "failure_kind": "invalid_sitemap_xml",
        "validation_error": "invalid sitemap root: 'html'",
    }
    scorecard = ScorecardService().build(
        crawl,
        PageAnalysisOutput(),
        _unconfigured_search(),
        target_context=TARGET_CONTEXT,
    )
    assert scorecard.metrics["sitemap_count"] == 0
    assert scorecard.sitemap_quality_score == 20.0


def test_transient_oserror_sitemap_failure_remains_unknown():
    service = CrawlDiscoveryService()
    service.fetcher = _TransientSitemapFetcher()

    crawl, assets = service.discover(_target(), "run-1")

    assert sitemap_evidence_status(crawl) == "unknown"
    assert crawl.errors == [
        f"sitemap_parse_failed:{SITEMAP_URL}:failure_kind=inconclusive: timed out"
    ]
    sitemap_asset = next(asset for asset in assets if asset.asset_type == "sitemap")
    assert sitemap_asset.metadata == {
        "validation_status": "failed",
        "failure_kind": "inconclusive",
        "validation_error": "timed out",
    }
    scorecard = ScorecardService().build(
        crawl,
        PageAnalysisOutput(),
        _unconfigured_search(),
        target_context=TARGET_CONTEXT,
    )
    assert scorecard.sitemap_quality_score is None
