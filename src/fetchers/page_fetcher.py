from __future__ import annotations

import gzip
import html
import json
import re
import urllib.parse
from dataclasses import dataclass, field
from html.parser import HTMLParser

from src.fetchers.http_client import FetchLimits, SafeHTTPClient


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
    ai_evidence: dict[str, object] = field(default_factory=dict)

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
        self.heading_level: int | None = None
        self.heading_parts: list[str] = []
        self.in_paragraph = False
        self.paragraph_parts: list[str] = []
        self.in_nav = 0
        self.excluded_depth = 0
        self.content_depth = 0
        self.ignored_text_depth = 0
        self.author_depth = 0
        self.author_parts: list[str] = []
        self.nav_links: list[str] = []
        self.in_json_ld = False
        self.json_ld_parts: list[str] = []
        self.json_ld_documents: list[object] = []
        self.headings: list[dict[str, object]] = []
        self.first_text_after_headings: list[dict[str, object]] = []
        self.pending_heading: dict[str, object] | None = None
        self.paragraphs: list[str] = []
        self.content_paragraphs: list[str] = []
        self.list_count = 0
        self.table_count = 0
        self.table_header_count = 0
        self.external_citations: list[str] = []
        self.author_names: list[str] = []
        self.published_dates: list[str] = []
        self.og_site_name: str | None = None
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.meta_description: str | None = None
        self.canonical_url: str | None = None
        self.robots_meta: str | None = None
        self.mobile_viewport = False
        self.internal_links: list[str] = []
        self.image_assets: list[str] = []
        self.schema_types: list[str] = []
        self.text_parts: list[str] = []
        self.content_text_parts: list[str] = []
        # Conversion evidence is deliberately limited to visible DOM metadata.
        # It never executes or submits forms and is kept separate from the AI
        # evidence contract so existing consumers remain backward compatible.
        self.anchor_context: dict[str, object] | None = None
        self.conversion_links: list[dict[str, object]] = []
        self.button_context: dict[str, object] | None = None
        self.conversion_buttons: list[str] = []
        self.form_context: dict[str, object] | None = None
        self.conversion_forms: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs):
        attrs_dict = dict(attrs)
        if self.author_depth:
            self.author_depth += 1
        marker = f"{attrs_dict.get('class') or ''} {attrs_dict.get('id') or ''}".casefold()
        if not self.author_depth and any(token in marker for token in ("author", "byline")):
            self.author_depth = 1
            self.author_parts = []
        if tag in {"head", "nav", "header", "footer", "aside", "form"}:
            self.excluded_depth += 1
        if tag in {"main", "article"}:
            self.content_depth += 1
        if tag in {"style", "noscript"} or (
            tag == "script"
            and (attrs_dict.get("type") or "").casefold() != "application/ld+json"
        ):
            self.ignored_text_depth += 1
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
        if tag in {"h1", "h2", "h3"}:
            self.heading_level = int(tag[1])
            self.heading_parts = []
        elif tag == "p":
            self.in_paragraph = True
            self.paragraph_parts = []
        elif tag in {"nav", "header"}:
            self.in_nav += 1
        elif tag in {"ul", "ol", "dl"} and not self.excluded_depth:
            self.list_count += 1
        elif tag == "table" and not self.excluded_depth:
            self.table_count += 1
        elif tag == "th" and not self.excluded_depth:
            self.table_header_count += 1
        elif tag == "script" and (attrs_dict.get("type") or "").casefold() == "application/ld+json":
            self.in_json_ld = True
            self.json_ld_parts = []
        elif tag == "time" and attrs_dict.get("datetime") and not self.excluded_depth:
            self.published_dates.append(str(attrs_dict["datetime"]).strip())
        elif tag == "meta":
            name = (attrs_dict.get("name") or attrs_dict.get("property") or "").lower()
            content = attrs_dict.get("content")
            if name == "description" and content:
                self.meta_description = content.strip()
            if name == "robots" and content:
                self.robots_meta = content.strip()
            if name == "og:site_name" and content:
                self.og_site_name = content.strip()
            if name == "viewport" and content:
                viewport = content.casefold()
                self.mobile_viewport = "width=device-width" in viewport
            if name in {"author", "article:author"} and content:
                self.author_names.append(content.strip())
            if name in {"article:published_time", "article:modified_time", "date", "datepublished", "datemodified"} and content:
                self.published_dates.append(content.strip())
        elif tag == "link":
            rel = (attrs_dict.get("rel") or "").lower()
            href = attrs_dict.get("href")
            if rel == "canonical" and href:
                self.canonical_url = urllib.parse.urljoin(self.base_url, href.strip())
        elif tag == "a":
            href = attrs_dict.get("href")
            if href:
                absolute = urllib.parse.urljoin(self.base_url, href.strip())
                self.anchor_context = {
                    "href": absolute,
                    "parts": [],
                    "excluded": bool(self.excluded_depth),
                }
                if urllib.parse.urlparse(absolute).netloc == urllib.parse.urlparse(self.base_url).netloc:
                    self.internal_links.append(absolute)
                    if self.in_nav:
                        self.nav_links.append(absolute)
                elif (
                    urllib.parse.urlparse(absolute).scheme in {"http", "https"}
                    and not self.excluded_depth
                    and (self.content_depth > 0 or self.in_paragraph)
                ):
                    self.external_citations.append(absolute)
        elif tag == "img":
            src = attrs_dict.get("src")
            if src:
                self.image_assets.append(urllib.parse.urljoin(self.base_url, src.strip()))

        if tag == "button":
            self.button_context = {"parts": [], "excluded": bool(self.excluded_depth)}
            if self.form_context is not None:
                self.form_context["submit_control_count"] = int(self.form_context["submit_control_count"]) + 1
        elif tag == "form":
            action = attrs_dict.get("action") or ""
            self.form_context = {
                "action": urllib.parse.urljoin(self.base_url, str(action).strip()) if action else self.base_url,
                "method": str(attrs_dict.get("method") or "get").casefold(),
                "field_count": 0,
                "submit_control_count": 0,
                # Forms are excluded from main-content text but remain valid
                # conversion evidence when visible in the DOM.
                "excluded": False,
            }
        elif tag in {"input", "select", "textarea"} and self.form_context is not None:
            input_type = str(attrs_dict.get("type") or "").casefold()
            if input_type != "hidden":
                self.form_context["field_count"] = int(self.form_context["field_count"]) + 1
            if input_type in {"submit", "button", "image"}:
                self.form_context["submit_control_count"] = int(self.form_context["submit_control_count"]) + 1

        itemtype = attrs_dict.get("itemtype")
        if itemtype:
            self.schema_types.append(itemtype.strip())

    def handle_endtag(self, tag: str):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        if tag in {"h1", "h2", "h3"} and self.heading_level:
            value = self._collapse(self.heading_parts)
            if value:
                heading = {"level": self.heading_level, "text": value}
                self.headings.append(heading)
                self.pending_heading = heading
            self.heading_level = None
            self.heading_parts = []
        elif tag == "p":
            value = self._collapse(self.paragraph_parts)
            if value:
                self.paragraphs.append(value[:500])
                if not self.excluded_depth:
                    self.content_paragraphs.append(value[:500])
                if self.pending_heading is not None:
                    self.first_text_after_headings.append({
                        "heading": self.pending_heading["text"],
                        "level": self.pending_heading["level"],
                        "text": value[:320],
                    })
                    self.pending_heading = None
            self.in_paragraph = False
            self.paragraph_parts = []
        elif tag == "a" and self.anchor_context is not None:
            href = str(self.anchor_context.get("href") or "")
            text = self._collapse(self.anchor_context.get("parts", [])) or ""
            if href and text:
                self.conversion_links.append({"href": href, "text": text[:200]})
            self.anchor_context = None
        elif tag == "button" and self.button_context is not None:
            text = self._collapse(self.button_context.get("parts", [])) or ""
            if text:
                self.conversion_buttons.append(text[:200])
            self.button_context = None
        elif tag == "form" and self.form_context is not None:
            payload = {
                key: value
                for key, value in self.form_context.items()
                if key != "excluded"
            }
            self.conversion_forms.append(payload)
            self.form_context = None
        elif tag in {"nav", "header"}:
            self.in_nav = max(0, self.in_nav - 1)
        elif tag == "script" and self.in_json_ld:
            raw = "".join(self.json_ld_parts).strip()
            if raw:
                try:
                    self.json_ld_documents.append(json.loads(raw))
                except (TypeError, ValueError):
                    self.json_ld_documents.append({"_invalid": True})
            self.in_json_ld = False
            self.json_ld_parts = []
        if self.author_depth:
            self.author_depth -= 1
            if not self.author_depth:
                author = self._collapse(self.author_parts)
                if author:
                    self.author_names.append(author[:200])
                self.author_parts = []
        if tag in {"head", "nav", "header", "footer", "aside", "form"}:
            self.excluded_depth = max(0, self.excluded_depth - 1)
        if tag in {"main", "article"}:
            self.content_depth = max(0, self.content_depth - 1)
        if tag in {"style", "noscript", "script"} and self.ignored_text_depth:
            self.ignored_text_depth -= 1

    def handle_data(self, data: str):
        text = data.strip()
        if not text:
            return
        if self.ignored_text_depth:
            return
        if self.in_title:
            self.title_parts.append(text)
        if self.in_h1:
            self.h1_parts.append(text)
        if self.heading_level:
            self.heading_parts.append(text)
        if self.in_paragraph:
            self.paragraph_parts.append(text)
        if self.in_json_ld:
            self.json_ld_parts.append(data)
            return
        if self.anchor_context is not None:
            self.anchor_context.setdefault("parts", []).append(text)
        if self.button_context is not None:
            self.button_context.setdefault("parts", []).append(text)
        if self.author_depth:
            self.author_parts.append(text)
        self.text_parts.append(text)
        if not self.excluded_depth:
            self.content_text_parts.append(text)

    @staticmethod
    def _collapse(parts: list[str]) -> str:
        return " ".join(parts).strip()


class PageFetcher:
    def __init__(
        self,
        timeout_seconds: int = 30,
        max_response_bytes: int = 2_000_000,
        http_client: SafeHTTPClient | None = None,
    ):
        self.timeout_seconds = timeout_seconds
        self.http_client = http_client or SafeHTTPClient(
            limits=FetchLimits(
                timeout_seconds=timeout_seconds,
                max_response_bytes=max_response_bytes,
            )
        )

    def fetch(self, url: str, *, allowed_host: str | None = None) -> PageFetchResult:
        allowed_hosts = {allowed_host} if allowed_host else None
        response = self.http_client.fetch(url, allowed_hosts=allowed_hosts)
        raw_body = response.body
        final_url = response.final_url
        content_type = response.headers.get("content-type")
        content_encoding = (response.headers.get("content-encoding") or "").lower()
        status = response.status

        if content_encoding == "gzip":
            raw_body = gzip.decompress(raw_body)

        body = raw_body.decode("utf-8", "ignore")

        parser = _MetadataParser(final_url)
        parser.feed(body)
        words = re.findall(r"\b\w+\b", html.unescape(" ".join(parser.text_parts)))

        ai_evidence = self._ai_evidence(parser)
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
            schema_types=self._dedupe([*parser.schema_types, *ai_evidence.get("json_ld_types", [])]),
            internal_links=self._dedupe(parser.internal_links),
            image_assets=self._dedupe(parser.image_assets),
            word_count=len(words),
            raw_html=body,
            ai_evidence=ai_evidence,
        )

    @staticmethod
    def _ai_evidence(parser: _MetadataParser) -> dict[str, object]:
        question_words = ("what ", "how ", "why ", "when ", "where ", "who ", "can ", "does ", "is ", "are ")
        question_count = sum(
            1 for item in parser.headings
            if str(item["text"]).casefold().startswith(question_words) or str(item["text"]).endswith("?")
        )
        stopwords = {
            "a", "an", "and", "are", "can", "do", "does", "for", "how", "is",
            "of", "our", "the", "to", "we", "what", "when", "where", "who", "why",
            "with", "you", "your",
        }
        direct_answer_blocks: list[dict[str, object]] = []
        for item in parser.first_text_after_headings:
            heading = str(item["heading"]).strip()
            answer = str(item["text"]).strip()
            heading_tokens = {
                token
                for token in re.findall(r"[a-z0-9]+", heading.casefold())
                if len(token) > 2 and token not in stopwords
            }
            answer_tokens = set(re.findall(r"[a-z0-9]+", answer.casefold()))
            question_like = heading.casefold().startswith(question_words) or heading.endswith("?")
            subject_match = bool(heading_tokens & answer_tokens)
            if 40 <= len(answer) <= 320 and (question_like or subject_match):
                direct_answer_blocks.append({
                    "heading": heading[:160],
                    "answer_excerpt": answer[:240],
                    "question_like": question_like,
                    "subject_match": subject_match,
                })
        levels = [int(item["level"]) for item in parser.headings]
        h1_count = sum(1 for level in levels if level == 1)
        hierarchy_valid = (
            h1_count == 1
            and all(current - previous <= 1 for previous, current in zip(levels, levels[1:]))
        )
        entities: list[str] = []
        schema_types: list[str] = []
        schema_nodes: list[dict[str, object]] = []
        invalid = False

        def visit(value: object) -> None:
            nonlocal invalid
            if isinstance(value, list):
                for item in value:
                    visit(item)
            elif isinstance(value, dict):
                if value.get("_invalid"):
                    invalid = True
                raw_type = value.get("@type")
                types = raw_type if isinstance(raw_type, list) else [raw_type] if isinstance(raw_type, str) else []
                schema_types.extend(str(item) for item in types)
                if types:
                    schema_nodes.append(value)
                if any(str(item).casefold() in {"organization", "localbusiness", "sportsactivitylocation"} for item in types):
                    name = value.get("name")
                    if isinstance(name, str) and name.strip():
                        entities.append(name.strip())
                author = value.get("author")
                if isinstance(author, dict) and isinstance(author.get("name"), str):
                    parser.author_names.append(author["name"].strip())
                if any(
                    str(item).casefold() in {"article", "blogposting", "newsarticle", "report", "case study"}
                    for item in types
                ):
                    for date_key in ("datePublished", "dateModified"):
                        if isinstance(value.get(date_key), str):
                            parser.published_dates.append(value[date_key].strip())
                for nested_key in ("@graph", "mainEntity", "itemListElement"):
                    if nested_key in value:
                        visit(value[nested_key])

        for document in parser.json_ld_documents:
            visit(document)
        if parser.og_site_name:
            entities.append(parser.og_site_name)
        visible = " ".join(parser.content_text_parts).casefold()
        schema_alignment: list[dict[str, object]] = []
        for node in schema_nodes:
            raw_types = node.get("@type")
            types = raw_types if isinstance(raw_types, list) else [raw_types]
            node_type = str(types[0]) if types else "Unknown"
            candidate_values = [
                node.get("name"),
                node.get("headline"),
                node.get("description"),
            ]
            matched = [
                str(value)[:160]
                for value in candidate_values
                if isinstance(value, str) and value.strip() and value.strip().casefold() in visible
            ]
            if node_type.casefold() == "faqpage":
                questions = node.get("mainEntity")
                if isinstance(questions, list):
                    matched.extend(
                        str(item.get("name"))[:160]
                        for item in questions
                        if isinstance(item, dict)
                        and isinstance(item.get("name"), str)
                        and item["name"].strip().casefold() in visible
                    )
            schema_alignment.append({
                "type": node_type,
                "aligned": bool(matched),
                "matched_visible_values": matched[:5],
            })
        aligned = bool(schema_alignment) and all(item["aligned"] for item in schema_alignment)
        specific_pattern = re.compile(
            r"(?:[$£€]\s?\d|\b\d+(?:[.,]\d+)?%|\b\d+(?:[.,]\d+)?\s+"
            r"(?:years?|customers?|projects?|locations?|members?|students?|reviews?|"
            r"square feet|sq\.?\s*ft|hours?|days?)\b)",
            re.IGNORECASE,
        )
        specific_excerpts = [
            paragraph[:240]
            for paragraph in parser.content_paragraphs
            if specific_pattern.search(paragraph)
        ][:20]
        social_hosts = {
            "facebook.com", "instagram.com", "linkedin.com", "pinterest.com",
            "tiktok.com", "twitter.com", "x.com", "youtube.com",
        }
        citations = [
            url
            for url in PageFetcher._dedupe(parser.external_citations)
            if not any(
                (urllib.parse.urlsplit(url).hostname or "").casefold().removeprefix("www.") == host
                or (urllib.parse.urlsplit(url).hostname or "").casefold().endswith(f".{host}")
                for host in social_hosts
            )
        ]
        http_words = re.findall(
            r"\b\w+\b",
            html.unescape(" ".join(parser.text_parts)),
        )
        main_words = re.findall(
            r"\b\w+\b",
            html.unescape(" ".join(parser.content_text_parts)),
        )
        conversion_text = html.unescape(" ".join(parser.text_parts))
        conversion_folded = conversion_text.casefold()
        cta_terms = (
            "book", "schedule", "appointment", "request", "quote", "estimate",
            "contact", "call", "join", "sign up", "signup", "start", "trial",
            "get started", "learn more", "apply",
        )
        cta_links: list[dict[str, object]] = []
        for link in parser.conversion_links:
            label = str(link.get("text") or "")
            if any(term in label.casefold() for term in cta_terms):
                cta_links.append({**link, "kind": "cta"})
        for label in parser.conversion_buttons:
            if any(term in label.casefold() for term in cta_terms):
                cta_links.append({"text": label, "kind": "button"})
        phone_numbers = PageFetcher._dedupe(
            re.findall(r"(?:\+?\d[\d().\-\s]{7,}\d)", conversion_text)
        )[:20]
        email_addresses = PageFetcher._dedupe(
            re.findall(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", conversion_text, re.I)
        )[:20]
        def terms_present(terms: tuple[str, ...]) -> list[str]:
            return [term for term in terms if term in conversion_folded][:20]

        offer_terms = terms_present((
            "class", "classes", "program", "service", "repair", "installation",
            "maintenance", "replacement", "emergency", "membership", "lesson",
            "training", "estimate", "quote",
        ))
        schedule_terms = terms_present(("schedule", "book", "appointment", "class times", "timetable"))
        pricing_terms = terms_present(("price", "pricing", "tuition", "membership", "monthly", "cost", "free trial"))
        eligibility_terms = terms_present((
            "beginner", "kids", "children", "adult", "ages", "service area", "licensed", "insured",
        ))
        trust_terms = terms_present((
            "review", "reviews", "testimonial", "testimonials", "licensed", "insured", "certified",
            "years", "members", "students", "projects", "award", "accredited",
        ))
        contact_signals = terms_present(("contact", "call", "email", "phone", "address", "location"))
        return {
            "schema_version": "ai-page-evidence.v2",
            "headings": parser.headings[:100],
            "first_text_after_headings": parser.first_text_after_headings[:100],
            "h1_count": h1_count,
            "heading_hierarchy_valid": hierarchy_valid,
            "direct_answer_count": len(direct_answer_blocks),
            "direct_answer_blocks": direct_answer_blocks[:20],
            "question_heading_count": question_count,
            "list_count": parser.list_count,
            "table_count": parser.table_count,
            "structured_block_count": parser.list_count + parser.table_count,
            "table_header_count": parser.table_header_count,
            "navigation_links": PageFetcher._dedupe(parser.nav_links)[:200],
            "in_navigation": False,
            "external_citation_count": len(citations),
            "external_citations": citations[:50],
            "author_names": PageFetcher._dedupe(parser.author_names)[:20],
            "published_dates": PageFetcher._dedupe(parser.published_dates)[:20],
            "entity_names": PageFetcher._dedupe(entities)[:20],
            "json_ld_types": PageFetcher._dedupe(schema_types)[:50],
            "json_ld_valid": bool(parser.json_ld_documents) and not invalid,
            "json_ld_visible_alignment": aligned,
            "json_ld_alignment": schema_alignment[:50],
            "specific_evidence_count": len(specific_excerpts),
            "specific_evidence_excerpts": specific_excerpts,
            "mobile_viewport": parser.mobile_viewport,
            "http_text_word_count": len(http_words),
            "main_content_word_count": len(main_words),
            "main_content_ratio": (
                round(len(main_words) / len(http_words), 4)
                if http_words
                else 0.0
            ),
            "conversion_evidence_version": "conversion-dom-evidence.v1",
            "conversion_links": parser.conversion_links[:100],
            "cta_links": cta_links[:50],
            "cta_count": len(cta_links),
            "conversion_buttons": parser.conversion_buttons[:50],
            "forms": parser.conversion_forms[:20],
            "form_count": len(parser.conversion_forms),
            "phone_numbers": phone_numbers,
            "email_addresses": email_addresses,
            "offer_signals": offer_terms,
            "schedule_signals": schedule_terms,
            "pricing_signals": pricing_terms,
            "eligibility_signals": eligibility_terms,
            "trust_signals": trust_terms,
            "contact_signals": contact_signals,
        }

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
