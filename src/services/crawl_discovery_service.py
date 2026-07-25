from __future__ import annotations

import urllib.error
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from src.fetchers.sitemap_fetcher import InvalidSitemapError, SitemapFetcher
from src.models import DiscoveredAsset, SEOTarget


@dataclass(slots=True)
class CrawlDiscoveryOutput:
    robots_url: str
    robots_status: int | None
    sitemap_urls: list[str] = field(default_factory=list)
    candidate_page_urls: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    candidate_sitemap_urls: list[str] = field(default_factory=list)


def sitemap_evidence_status(crawl: CrawlDiscoveryOutput) -> str:
    """Return valid, prospect_issue, or unknown from persisted crawl evidence."""
    if crawl.sitemap_urls:
        return "valid"
    if not crawl.candidate_sitemap_urls:
        return "unknown"
    markers = (
        "failure_kind=conclusive_http_404",
        "failure_kind=conclusive_http_410",
        "failure_kind=malformed_xml",
        "failure_kind=invalid_sitemap_xml",
        "http 404",
        "http 410",
        "malformed xml",
        "invalid xml",
    )
    return "prospect_issue" if any(
        marker in error.casefold() for error in crawl.errors for marker in markers
    ) else "unknown"


class CrawlDiscoveryService:
    def __init__(self, timeout_seconds: int = 30):
        self.fetcher = SitemapFetcher(timeout_seconds=timeout_seconds)

    def discover(self, target: SEOTarget, insight_run_id: str) -> tuple[CrawlDiscoveryOutput, list[DiscoveredAsset]]:
        result = self.fetcher.discover(target.normalized_domain)
        candidate_sitemap_urls = self._dedupe(result.sitemap_urls)
        validated_sitemap_urls: list[str] = []
        candidate_page_urls: list[str] = []
        assets: list[DiscoveredAsset] = [
            DiscoveredAsset(
                insight_run_id=insight_run_id,
                asset_type="robots_txt",
                url=result.robots_url,
                http_status=result.robots_status,
                is_primary=True,
                metadata={"errors": result.errors},
            )
        ]
        for sitemap_url in candidate_sitemap_urls:
            asset = DiscoveredAsset(
                insight_run_id=insight_run_id,
                asset_type="sitemap",
                url=sitemap_url,
                discovered_from=result.robots_url,
                is_primary=True,
            )
            assets.append(asset)
            try:
                candidate_page_urls.extend(self.fetcher.fetch_sitemap_urls(sitemap_url)[:20])
                validated_sitemap_urls.append(sitemap_url)
                asset.metadata = {"validation_status": "validated"}
            except Exception as exc:
                failure_kind = self._failure_kind(exc)
                asset.metadata = {
                    "validation_status": "failed",
                    "failure_kind": failure_kind,
                    "validation_error": str(exc),
                }
                result.errors.append(
                    f"sitemap_parse_failed:{sitemap_url}:failure_kind={failure_kind}: {exc}"
                )
        return (
            CrawlDiscoveryOutput(
                robots_url=result.robots_url,
                robots_status=result.robots_status,
                sitemap_urls=validated_sitemap_urls,
                candidate_page_urls=self._dedupe(candidate_page_urls),
                errors=result.errors,
                candidate_sitemap_urls=candidate_sitemap_urls,
            ),
            assets,
        )

    @staticmethod
    def _dedupe(urls: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for url in urls:
            if url not in seen:
                out.append(url)
                seen.add(url)
        return out

    @staticmethod
    def _failure_kind(exc: Exception) -> str:
        if isinstance(exc, urllib.error.HTTPError) and exc.code == 404:
            return "conclusive_http_404"
        if isinstance(exc, urllib.error.HTTPError) and exc.code == 410:
            return "conclusive_http_410"
        if isinstance(exc, ET.ParseError):
            return "malformed_xml"
        if isinstance(exc, InvalidSitemapError):
            return "invalid_sitemap_xml"
        return "inconclusive"
