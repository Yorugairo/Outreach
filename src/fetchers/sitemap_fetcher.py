from __future__ import annotations

import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Iterable


@dataclass(slots=True)
class SitemapDiscoveryResult:
    domain: str
    robots_url: str
    sitemap_urls: list[str] = field(default_factory=list)
    robots_status: int | None = None
    errors: list[str] = field(default_factory=list)


class SitemapFetcher:
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    def discover(self, domain: str) -> SitemapDiscoveryResult:
        base = self._normalize_domain(domain)
        robots_url = urllib.parse.urljoin(base, "/robots.txt")
        result = SitemapDiscoveryResult(domain=base, robots_url=robots_url)

        try:
            with urllib.request.urlopen(robots_url, timeout=self.timeout_seconds) as response:
                result.robots_status = response.status
                robots_body = response.read().decode("utf-8", "ignore")
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
        with urllib.request.urlopen(sitemap_url, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8", "ignore")

        root = ET.fromstring(body)
        namespace = self._namespace(root.tag)
        url_tag = f"{{{namespace}}}url" if namespace else "url"
        loc_tag = f"{{{namespace}}}loc" if namespace else "loc"
        sitemap_tag = f"{{{namespace}}}sitemap" if namespace else "sitemap"

        urls: list[str] = []
        if root.tag.endswith("urlset"):
            for url_node in root.findall(url_tag):
                loc = url_node.find(loc_tag)
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())
        elif root.tag.endswith("sitemapindex"):
            for sitemap_node in root.findall(sitemap_tag):
                loc = sitemap_node.find(loc_tag)
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())
        return urls

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
