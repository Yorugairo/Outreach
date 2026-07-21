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


class CrawlDiscoveryService:
    def __init__(self, timeout_seconds: int = 30):
        self.fetcher = SitemapFetcher(timeout_seconds=timeout_seconds)

    def discover(self, target: SEOTarget, insight_run_id: str) -> tuple[CrawlDiscoveryOutput, list[DiscoveredAsset]]:
        result = self.fetcher.discover(target.normalized_domain)
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
        for sitemap_url in result.sitemap_urls:
            assets.append(
                DiscoveredAsset(
                    insight_run_id=insight_run_id,
                    asset_type="sitemap",
                    url=sitemap_url,
                    discovered_from=result.robots_url,
                    is_primary=True,
                )
            )
            try:
                candidate_page_urls.extend(self.fetcher.fetch_sitemap_urls(sitemap_url)[:20])
            except Exception as exc:
                result.errors.append(f"sitemap_parse_failed:{sitemap_url}: {exc}")
        return (
            CrawlDiscoveryOutput(
                robots_url=result.robots_url,
                robots_status=result.robots_status,
                sitemap_urls=result.sitemap_urls,
                candidate_page_urls=self._dedupe(candidate_page_urls),
                errors=result.errors,
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
