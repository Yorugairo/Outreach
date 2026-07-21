from __future__ import annotations

import gzip
import html
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser


@dataclass(slots=True)
class PageFetchResult:
    url: str
    final_url: str
    http_status: int
    content_type: str | None
    title: str | None
    meta_description: str | None
    h1: str | None
    canonical_url: str | None
    robots_meta: str | None
    schema_types: list[str] = field(default_factory=list)
    internal_links: list[str] = field(default_factory=list)
    image_assets: list[str] = field(default_factory=list)
    word_count: int = 0
    raw_html: str = ""

    @property
    def indexable(self) -> bool:
        if not self.robots_meta:
            return True
        return "noindex" not in self.robots_meta.lower()


class _MetadataParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.in_title = False
        self.in_h1 = False
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.meta_description: str | None = None
        self.canonical_url: str | None = None
        self.robots_meta: str | None = None
        self.internal_links: list[str] = []
        self.image_assets: list[str] = []
        self.schema_types: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
        elif tag == "meta":
            name = (attrs_dict.get("name") or attrs_dict.get("property") or "").lower()
            content = attrs_dict.get("content")
            if name == "description" and content:
                self.meta_description = content.strip()
            if name == "robots" and content:
                self.robots_meta = content.strip()
        elif tag == "link":
            rel = (attrs_dict.get("rel") or "").lower()
            href = attrs_dict.get("href")
            if rel == "canonical" and href:
                self.canonical_url = urllib.parse.urljoin(self.base_url, href.strip())
        elif tag == "a":
            href = attrs_dict.get("href")
            if href:
                absolute = urllib.parse.urljoin(self.base_url, href.strip())
                if urllib.parse.urlparse(absolute).netloc == urllib.parse.urlparse(self.base_url).netloc:
                    self.internal_links.append(absolute)
        elif tag == "img":
            src = attrs_dict.get("src")
            if src:
                self.image_assets.append(urllib.parse.urljoin(self.base_url, src.strip()))

        itemtype = attrs_dict.get("itemtype")
        if itemtype:
            self.schema_types.append(itemtype.strip())

    def handle_endtag(self, tag: str):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False

    def handle_data(self, data: str):
        text = data.strip()
        if not text:
            return
        if self.in_title:
            self.title_parts.append(text)
        if self.in_h1:
            self.h1_parts.append(text)
        self.text_parts.append(text)


class PageFetcher:
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    def fetch(self, url: str) -> PageFetchResult:
        req = urllib.request.Request(url, headers={"User-Agent": "OutreachProgram/0.1"})
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            raw_body = response.read()
            final_url = response.geturl()
            content_type = response.headers.get("content-type")
            content_encoding = (response.headers.get("content-encoding") or "").lower()
            status = response.status

        if content_encoding == "gzip":
            raw_body = gzip.decompress(raw_body)

        body = raw_body.decode("utf-8", "ignore")

        parser = _MetadataParser(final_url)
        parser.feed(body)
        words = re.findall(r"\b\w+\b", html.unescape(body))

        return PageFetchResult(
            url=url,
            final_url=final_url,
            http_status=status,
            content_type=content_type,
            title=self._collapse(parser.title_parts),
            meta_description=parser.meta_description,
            h1=self._collapse(parser.h1_parts),
            canonical_url=parser.canonical_url,
            robots_meta=parser.robots_meta,
            schema_types=self._dedupe(parser.schema_types),
            internal_links=self._dedupe(parser.internal_links),
            image_assets=self._dedupe(parser.image_assets),
            word_count=len(words),
            raw_html=body,
        )

    @staticmethod
    def _collapse(parts: list[str]) -> str | None:
        text = " ".join(parts).strip()
        return text or None

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for value in values:
            if value not in seen:
                out.append(value)
                seen.add(value)
        return out
