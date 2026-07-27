from __future__ import annotations

import urllib.parse
import re
from dataclasses import dataclass, field
from typing import Any

from src.fetchers.page_fetcher import PageFetcher
from src.models import PageRecord, SEOTarget


@dataclass(slots=True)
class PageAnalysisOutput:
    pages: list[PageRecord] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    discovered_count: int = 0
    attempted_count: int = 0
    capped: bool = False
    duplicate_aliases: list[dict[str, str]] = field(default_factory=list)


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
                    ai_evidence=fetched.ai_evidence,
                    fetch_metadata={"fetched_url": fetched.url},
                    fetched_at=None,
                )
                output.pages.append(page)
            except Exception as exc:
                message = str(exc)
                match = re.search(r"\b(4\d\d|5\d\d)\b", message)
                status = int(match.group(1)) if match else None
                output.errors.append({
                    "url": url,
                    "error": message,
                    "http_status": status,
                    "failure_kind": "http_error" if status else "inconclusive",
                    "conclusive": bool(
                        status
                        and 400 <= status <= 599
                        and status not in {401, 403, 407, 429}
                    ),
                })
        return output

    def crawl_site(
        self,
        target: SEOTarget,
        insight_run_id: str,
        seed_urls: list[str],
        *,
        max_pages: int = 100,
    ) -> PageAnalysisOutput:
        """Fetch each normalized internal URL once and reuse the evidence."""

        max_pages = max(1, min(int(max_pages), 100))
        queue: dict[str, str] = {}
        discovered_from: dict[str, str] = {}
        discovered_depth: dict[str, int] = {}
        discovered: set[str] = set()
        attempted: set[str] = set()
        resolved_identities: set[str] = set()
        aliases: dict[str, str] = {}
        navigation: set[str] = set()
        sitemap_identities: set[str] = set()
        output = PageAnalysisOutput()

        def add(url: str, source_url: str, depth: int) -> None:
            normalized = self._normalize_internal(url, target.normalized_domain)
            identity = self._url_identity(url, target.normalized_domain)
            if normalized is None or identity is None:
                return
            resolved = aliases.get(identity, identity)
            discovered.add(identity)
            if resolved not in attempted and resolved not in resolved_identities:
                queue.setdefault(resolved, normalized)
                discovered_from.setdefault(resolved, source_url)
                discovered_depth[resolved] = min(
                    depth,
                    discovered_depth.get(resolved, depth),
                )

        add(target.normalized_url, target.normalized_url, 0)
        for url in seed_urls:
            identity = self._url_identity(url, target.normalized_domain)
            if identity:
                sitemap_identities.add(identity)
            add(url, target.normalized_url, 1)
        while queue and len(attempted) < max_pages:
            identity = min(
                queue,
                key=lambda item: self._priority(queue[item], navigation),
            )
            url = queue.pop(identity)
            if identity in attempted or identity in resolved_identities:
                continue
            attempted.add(identity)
            crawl_depth = discovered_depth.get(identity, 0)
            result = self.analyze_urls(target, insight_run_id, [url])
            for error in result.errors:
                error["source_url"] = discovered_from.get(identity, target.normalized_url)
                error["target_url"] = url
            output.errors.extend(result.errors)
            for page in result.pages:
                final_identity = self._url_identity(page.url, target.normalized_domain) or identity
                canonical_identity = (
                    self._url_identity(page.canonical_url, target.normalized_domain)
                    if page.canonical_url
                    else None
                )
                resolved_identity = canonical_identity or final_identity
                for alias in {identity, final_identity, canonical_identity} - {None}:
                    aliases[str(alias)] = resolved_identity
                    if alias != resolved_identity:
                        output.duplicate_aliases.append({
                            "alias": str(alias),
                            "resolved_identity": resolved_identity,
                            "source_url": url,
                        })
                        queue.pop(str(alias), None)
                if resolved_identity in resolved_identities:
                    continue
                resolved_identities.add(resolved_identity)
                page.fetch_metadata.update({
                    "requested_identity": identity,
                    "final_identity": final_identity,
                    "resolved_identity": resolved_identity,
                    "discovered_from": discovered_from.get(identity, target.normalized_url),
                    "crawl_depth": crawl_depth,
                    "redirected": self._url_identity(
                        str(page.fetch_metadata.get("fetched_url") or page.url),
                        target.normalized_domain,
                    )
                    != final_identity,
                })
                output.pages.append(page)
                nav_links = page.ai_evidence.get("navigation_links", [])
                if isinstance(nav_links, list):
                    for link in nav_links:
                        nav_identity = self._url_identity(str(link), target.normalized_domain)
                        if nav_identity:
                            navigation.add(nav_identity)
                            add(str(link), page.url, crawl_depth + 1)
                for link in page.internal_links:
                    add(link, page.url, crawl_depth + 1)
        for page in output.pages:
            identity = self._url_identity(page.url, target.normalized_domain)
            page.ai_evidence["in_navigation"] = identity in navigation
            page.ai_evidence["in_sitemap"] = identity in sitemap_identities
        output.attempted_count = len(attempted)
        output.discovered_count = max(len(discovered), output.attempted_count)
        output.capped = bool(queue)
        return output

    @staticmethod
    def _classify(url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.lower().strip("/")
        if not path:
            return "homepage"
        if any(token in path for token in ["blog", "guide", "resource", "faq", "article"]):
            return "blog_resource"
        if any(token in path for token in ["project", "portfolio", "case-study"]):
            return "project_case_study"
        if any(token in path for token in ["service", "solutions"]) and any(token in path for token in ["location", "area", "city"]):
            return "service_location"
        if any(token in path for token in ["service", "solutions", "classes", "programs"]):
            return "service"
        if any(token in path for token in ["location", "area", "city"]):
            return "location"
        if any(token in path for token in ["contact", "about"]):
            return "contact_about"
        if any(token in path for token in ["privacy", "terms", "feed", "tag"]):
            return "legal_utility"
        return "unclassified"

    @staticmethod
    def _normalize_internal(url: str, target_domain: str) -> str | None:
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme not in {"http", "https"}:
            return None
        host = (parsed.hostname or "").casefold().removeprefix("www.").rstrip(".")
        target = target_domain.casefold().removeprefix("www.").rstrip(".")
        if host != target and not host.endswith(f".{target}"):
            return None
        path = parsed.path or "/"
        if path != "/":
            path = path.rstrip("/")
        query = parsed.query if not any(
            key.casefold().startswith(("utm_", "fbclid", "gclid"))
            for key, _ in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        ) else ""
        return urllib.parse.urlunsplit((parsed.scheme.casefold(), parsed.netloc.casefold(), path, query, ""))

    @staticmethod
    def _url_identity(url: str | None, target_domain: str) -> str | None:
        if not url:
            return None
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme.casefold() not in {"http", "https"}:
            return None
        host = (parsed.hostname or "").casefold().removeprefix("www.").rstrip(".")
        target = target_domain.casefold().removeprefix("www.").rstrip(".")
        if host != target and not host.endswith(f".{target}"):
            return None
        path = parsed.path or "/"
        if path != "/":
            path = path.rstrip("/")
        query_pairs = [
            (key, value)
            for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
            if not key.casefold().startswith(("utm_", "fbclid", "gclid"))
        ]
        query = urllib.parse.urlencode(sorted(query_pairs))
        return urllib.parse.urlunsplit(("", host, path, query, ""))

    @classmethod
    def _priority(cls, url: str, navigation: set[str]) -> tuple[int, str]:
        identity = cls._url_identity(url, urllib.parse.urlsplit(url).hostname or "")
        if identity in navigation:
            return (0, url)
        page_class = cls._classify(url)
        if page_class in {"homepage", "service", "location", "service_location", "contact_about"}:
            return (1, url)
        if page_class in {"blog_resource", "project_case_study"}:
            return (2, url)
        if page_class == "legal_utility":
            return (4, url)
        return (3, url)
