from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field

from src.fetchers.page_fetcher import PageFetcher
from src.models import PageRecord, SEOTarget


@dataclass(slots=True)
class PageAnalysisOutput:
    pages: list[PageRecord] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)


class PageAnalysisService:
    def __init__(self, timeout_seconds: int = 30):
        self.fetcher = PageFetcher(timeout_seconds=timeout_seconds)

    def analyze_urls(self, target: SEOTarget, insight_run_id: str, urls: list[str]) -> PageAnalysisOutput:
        output = PageAnalysisOutput()
        seen: set[str] = set()
        for url in urls:
            if url in seen:
                continue
            seen.add(url)
            try:
                fetched = self.fetcher.fetch(url, allowed_host=target.normalized_domain)
                page = PageRecord(
                    insight_run_id=insight_run_id,
                    seo_target_id=target.id,
                    url=fetched.final_url,
                    canonical_url=fetched.canonical_url,
                    normalized_path=urllib.parse.urlparse(fetched.final_url).path or "/",
                    page_class=self._classify(fetched.final_url),
                    fetch_status="fetched",
                    http_status=fetched.http_status,
                    content_type=fetched.content_type,
                    title=fetched.title,
                    meta_description=fetched.meta_description,
                    h1=fetched.h1,
                    robots_meta=fetched.robots_meta,
                    canonical_status="present" if fetched.canonical_url else "missing",
                    indexable=fetched.indexable,
                    word_count=fetched.word_count,
                    schema_types=fetched.schema_types,
                    internal_links=fetched.internal_links,
                    image_assets=fetched.image_assets,
                    fetch_metadata={"fetched_url": fetched.url},
                    fetched_at=None,
                )
                output.pages.append(page)
            except Exception as exc:
                output.errors.append({"url": url, "error": str(exc)})
        return output

    @staticmethod
    def _classify(url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.lower().strip("/")
        if not path:
            return "homepage"
        if any(token in path for token in ["blog", "guide", "resource", "faq"]):
            return "blog_resource"
        if any(token in path for token in ["project", "portfolio", "case-study"]):
            return "project_case_study"
        if any(token in path for token in ["service", "solutions"]):
            return "service"
        if any(token in path for token in ["location", "area", "city"]):
            return "location"
        if any(token in path for token in ["contact", "about"]):
            return "contact_about"
        if any(token in path for token in ["privacy", "terms", "feed", "tag"]):
            return "legal_utility"
        return "unclassified"
