from __future__ import annotations

from dataclasses import dataclass, field

from src.fetchers.sitemap_fetcher import SitemapFetcher
from src.models import DiscoveredAsset, SEOTarget


@dataclass(slots=True)
class CrawlDiscoveryOutput:
    robots_url: str
    robots_status: int | None
    sitemap_urls: list[str] = field(default_factory=list)
    candidate_page_urls: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    candidate_sitemap_urls: list[str] = field(default_factory=list)


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
                asset.metadata = {"validation_status": "failed", "validation_error": str(exc)}
                result.errors.append(f"sitemap_parse_failed:{sitemap_url}: {exc}")
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
