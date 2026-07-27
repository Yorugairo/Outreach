from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.robotparser
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
    robots_access: dict[str, bool | None] = field(default_factory=dict)


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
    def __init__(
        self,
        timeout_seconds: int = 30,
        max_sitemaps: int = 100,
        max_pages_per_sitemap: int = 5_000,
    ):
        self.fetcher = SitemapFetcher(timeout_seconds=timeout_seconds)
        self.max_sitemaps = max_sitemaps
        self.max_pages_per_sitemap = max_pages_per_sitemap

    def discover(self, target: SEOTarget, insight_run_id: str) -> tuple[CrawlDiscoveryOutput, list[DiscoveredAsset]]:
        result = self.fetcher.discover(target.normalized_domain)
        robots_access = self._robots_access(result.robots_body, target.normalized_url, result.robots_status)
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
                metadata={"errors": result.errors, "robots_access": robots_access},
            )
        ]
        queue: list[tuple[str, str | None]] = [
            (url, result.robots_url) for url in candidate_sitemap_urls
        ]
        seen_sitemaps: set[str] = set()
        while queue and len(seen_sitemaps) < self.max_sitemaps:
            sitemap_url, discovered_from = queue.pop(0)
            if sitemap_url in seen_sitemaps:
                continue
            seen_sitemaps.add(sitemap_url)
            asset = DiscoveredAsset(
                insight_run_id=insight_run_id,
                asset_type="sitemap",
                url=sitemap_url,
                discovered_from=discovered_from,
                is_primary=discovered_from == result.robots_url,
            )
            assets.append(asset)
            try:
                fetch_document = getattr(self.fetcher, "fetch_sitemap_document", None)
                uses_document_contract = callable(fetch_document) and (
                    type(self.fetcher) is SitemapFetcher
                    or type(self.fetcher).fetch_sitemap_document is not SitemapFetcher.fetch_sitemap_document
                )
                if uses_document_contract:
                    document = fetch_document(sitemap_url)
                    locations = document.urls[: self.max_pages_per_sitemap]
                    if document.root_type == "sitemapindex":
                        for child_url in locations:
                            if child_url not in candidate_sitemap_urls:
                                candidate_sitemap_urls.append(child_url)
                            queue.append((child_url, sitemap_url))
                    else:
                        candidate_page_urls.extend(
                            url for url in locations if self._same_host(url, target.normalized_domain)
                        )
                    asset.metadata = {
                        "validation_status": "validated",
                        "root_type": document.root_type,
                        "location_count": len(document.urls),
                    }
                else:
                    candidate_page_urls.extend(
                        url
                        for url in self.fetcher.fetch_sitemap_urls(sitemap_url)[: self.max_pages_per_sitemap]
                        if self._same_host(url, target.normalized_domain)
                    )
                    asset.metadata = {"validation_status": "validated"}
                validated_sitemap_urls.append(sitemap_url)
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
        if queue:
            result.errors.append(
                f"sitemap_walk_limit_exceeded:max_sitemaps={self.max_sitemaps}"
            )
        return (
            CrawlDiscoveryOutput(
                robots_url=result.robots_url,
                robots_status=result.robots_status,
                sitemap_urls=validated_sitemap_urls,
                candidate_page_urls=self._dedupe(candidate_page_urls),
                errors=result.errors,
                candidate_sitemap_urls=candidate_sitemap_urls,
                robots_access=robots_access,
            ),
            assets,
        )

    @staticmethod
    def _same_host(url: str, target_domain: str) -> bool:
        hostname = (urllib.parse.urlsplit(url).hostname or "").casefold().rstrip(".")
        target = target_domain.casefold().removeprefix("www.").rstrip(".")
        return hostname == target or hostname.endswith(f".{target}")

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

    @staticmethod
    def _robots_access(body: str, url: str, status: int | None) -> dict[str, bool | None]:
        if status != 200 or not body.strip():
            return {name: None for name in ("googlebot", "bingbot", "oai-searchbot")}
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(urllib.parse.urljoin(url, "/robots.txt"))
        parser.parse(body.splitlines())
        return {
            name: parser.can_fetch(user_agent, url)
            for name, user_agent in {
                "googlebot": "Googlebot",
                "bingbot": "bingbot",
                "oai-searchbot": "OAI-SearchBot",
            }.items()
        }
