from __future__ import annotations

import re
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from src.fetchers.http_client import FetchLimits, SafeHTTPClient


class InvalidSitemapError(ValueError):
    """Raised when well-formed XML does not have a supported sitemap root."""


@dataclass(slots=True)
class SitemapDiscoveryResult:
    domain: str
    robots_url: str
    sitemap_urls: list[str] = field(default_factory=list)
    robots_status: int | None = None
    robots_body: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SitemapDocument:
    root_type: str
    urls: list[str] = field(default_factory=list)


class SitemapFetcher:
    def __init__(
        self,
        timeout_seconds: int = 30,
        max_response_bytes: int = 5_000_000,
        http_client: SafeHTTPClient | None = None,
    ):
        self.timeout_seconds = timeout_seconds
        self.http_client = http_client or SafeHTTPClient(
            limits=FetchLimits(
                timeout_seconds=timeout_seconds,
                max_response_bytes=max_response_bytes,
            )
        )
        self._host_scope: str | None = None

    def discover(self, domain: str) -> SitemapDiscoveryResult:
        base = self._normalize_domain(domain)
        robots_url = urllib.parse.urljoin(base, "/robots.txt")
        self._host_scope = urllib.parse.urlsplit(base).hostname
        result = SitemapDiscoveryResult(domain=base, robots_url=robots_url)

        try:
            response = self.http_client.fetch(
                robots_url,
                allowed_hosts={self._host_scope} if self._host_scope else None,
            )
            result.robots_status = response.status
            robots_body = response.body.decode("utf-8", "ignore")
            result.robots_body = robots_body
        except Exception as exc:
            result.errors.append(f"robots_fetch_failed: {exc}")
            robots_body = ""

        discovered = self._extract_sitemaps_from_robots(robots_body)
        if not discovered:
            discovered = [urllib.parse.urljoin(base, "/sitemap.xml")]

        seen: set[str] = set()
        for sitemap_url in discovered:
            if sitemap_url not in seen:
                result.sitemap_urls.append(sitemap_url)
                seen.add(sitemap_url)

        return result

    def fetch_sitemap_urls(self, sitemap_url: str) -> list[str]:
        return self.fetch_sitemap_document(sitemap_url).urls

    def fetch_sitemap_document(self, sitemap_url: str) -> SitemapDocument:
        response = self.http_client.fetch(
            sitemap_url,
            allowed_hosts={self._host_scope} if self._host_scope else None,
        )
        body = response.body.decode("utf-8", "ignore")

        root = ET.fromstring(body)
        namespace = self._namespace(root.tag)
        root_name = self._local_name(root.tag)
        url_tag = f"{{{namespace}}}url" if namespace else "url"
        loc_tag = f"{{{namespace}}}loc" if namespace else "loc"
        sitemap_tag = f"{{{namespace}}}sitemap" if namespace else "sitemap"

        urls: list[str] = []
        if root_name == "urlset":
            for url_node in root.findall(url_tag):
                loc = url_node.find(loc_tag)
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())
        elif root_name == "sitemapindex":
            for sitemap_node in root.findall(sitemap_tag):
                loc = sitemap_node.find(loc_tag)
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())
        else:
            raise InvalidSitemapError(f"invalid sitemap root: {root.tag!r}")
        return SitemapDocument(root_type=root_name, urls=urls)

    @staticmethod
    def _extract_sitemaps_from_robots(robots_body: str) -> list[str]:
        sitemaps: list[str] = []
        for line in robots_body.splitlines():
            match = re.match(r"^\s*Sitemap:\s*(.+?)\s*$", line, re.IGNORECASE)
            if match:
                sitemaps.append(match.group(1).strip())
        return sitemaps

    @staticmethod
    def _normalize_domain(domain: str) -> str:
        if not domain.startswith(("http://", "https://")):
            domain = f"https://{domain}"
        return domain.rstrip("/")

    @staticmethod
    def _namespace(tag: str) -> str | None:
        if tag.startswith("{") and "}" in tag:
            return tag[1:].split("}", 1)[0]
        return None

    @staticmethod
    def _local_name(tag: str) -> str:
        if tag.startswith("{") and "}" in tag:
            return tag.split("}", 1)[1]
        return tag
