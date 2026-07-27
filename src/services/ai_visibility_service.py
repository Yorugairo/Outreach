"""Optional, attributable Observed AI Visibility evidence.

The service deliberately does not score or mutate AI Readiness.  It consumes a
versioned, operator-approved :class:`PromptTopicSet` and dated provider
responses, then exposes only what can be attributed to the sampled prompts.
Preflight is pure bookkeeping; ``collect`` is the only method that can invoke a
paid provider.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

from src.models import PRODUCT_SURFACE_VERSIONS, ProductSurfaceResult


def _payload(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    return dict(value) if isinstance(value, Mapping) else {}


def _domain(value: Any) -> str:
    text = str(value or "").strip().casefold()
    if not text:
        return ""
    if "://" in text:
        text = urlsplit(text).hostname or ""
    return text.rstrip(".").removeprefix("www.")


def _url(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(str(item) for item in value.values() if item is not None)
    if isinstance(value, list):
        return " ".join(_text(item) for item in value)
    return str(value or "")


@dataclass(slots=True)
class AIVisibilityContext:
    market: str | None = None
    location_code: int | None = None
    language_code: str | None = None
    device: str | None = None
    snapshot_date: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "market": self.market,
            "location_code": self.location_code,
            "language_code": self.language_code,
            "device": self.device,
            "snapshot_date": self.snapshot_date,
        }


class AIVisibilityService:
    """Build ``ai-visibility.v1`` from approved prompt observations."""

    VERSION = PRODUCT_SURFACE_VERSIONS["observed_ai_visibility"]
    CALL_CAP = 20
    MAX_TOPICS = 20
    MIN_COMPLETE_COVERAGE_PERCENT = 50.0

    def preflight(
        self,
        topic_set: Any = None,
        *,
        provider_configured: bool = False,
        operator_approved: bool = False,
        allow_paid_api_calls: bool = False,
        existing_evidence: Iterable[Mapping[str, Any]] | None = None,
        call_cap: int | None = None,
        prompt_topic_set: Any = None,
        approval_granted: bool | None = None,
        context: Mapping[str, Any] | AIVisibilityContext | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        """Return a no-network paid-call and cost preflight."""

        topic_set = topic_set if topic_set is not None else prompt_topic_set
        if approval_granted is not None:
            operator_approved = bool(approval_granted)
        topics = self._topics(topic_set)
        approved = self._is_approved(topic_set)
        cap = self.CALL_CAP if call_cap is None else max(0, int(call_cap))
        expected = len(topics)
        requested = self._context(context, topic_set)
        reusable_topic_ids = {
            str(row.get("topic_id") or row.get("prompt_id") or "")
            for row in (existing_evidence or [])
            if isinstance(row, Mapping)
            and self._evidence_matches(row, topic_set, requested)
            and self._has_observation(row)
        }
        reusable = len(reusable_topic_ids.intersection(
            str(topic.get("id") or "") for topic in topics
        ))
        planned = max(0, expected - reusable)
        blocked_reason = None
        if not approved:
            blocked_reason = "Observed AI Visibility requires an operator-approved prompt/topic set."
        elif expected == 0:
            blocked_reason = "Prompt/topic set contains no prompts."
        elif expected > self.MAX_TOPICS:
            blocked_reason = f"Prompt/topic set exceeds the {self.MAX_TOPICS}-prompt cap."
        elif planned > cap:
            blocked_reason = f"Observed AI Visibility preflight exceeds the {cap}-call cap."
        elif context is not None and any(
            value in {None, ""}
            for value in (
                requested.market,
                requested.location_code,
                requested.language_code,
                requested.device,
            )
        ):
            blocked_reason = "Observed AI Visibility requires explicit market, location, language, and device context."
        elif not provider_configured:
            blocked_reason = "DataForSEO credentials are not configured."
        elif not operator_approved or not allow_paid_api_calls:
            blocked_reason = "Explicit operator approval is required before paid AI visibility calls."
        return {
            "surface": "observed_ai_visibility",
            "contract_version": self.VERSION,
            "topic_set_id": self._topic_set_id(topic_set),
            "topic_set_version": self._topic_set_version(topic_set),
            "topic_set_source_sha256": self._topic_set_source_hash(topic_set),
            "vertical_id": _payload(topic_set).get("vertical_id"),
            "approved": approved,
            "provider": "dataforseo",
            "provider_configured": bool(provider_configured),
            "operator_approved": bool(operator_approved),
            "allow_paid_api_calls": bool(allow_paid_api_calls),
            "topic_count": expected,
            "planned_calls": planned,
            "reusable_calls": min(reusable, expected),
            "call_cap": cap,
            "conservative_max_cost_usd": round(planned * 0.02, 6),
            "network_check_performed": False,
            "billing_check_performed": False,
            "status": "ready" if blocked_reason is None else "blocked",
            "blocked_reason": blocked_reason,
        }

    paid_preflight = preflight

    def build(
        self,
        topic_set: Any = None,
        evidence: Iterable[Mapping[str, Any]] | None = None,
        target_domain: str | None = None,
        *,
        context: Mapping[str, Any] | AIVisibilityContext | None = None,
        entity_name: str | None = None,
        prompt_topic_set: Any = None,
        provider_results: Iterable[Mapping[str, Any]] | None = None,
        observations: Iterable[Mapping[str, Any]] | None = None,
        ai_results: Iterable[Mapping[str, Any]] | None = None,
        **_: Any,
    ) -> ProductSurfaceResult:
        """Build metrics from already-collected provider evidence only."""

        topic_set = topic_set if topic_set is not None else prompt_topic_set
        if evidence is None:
            evidence = provider_results if provider_results is not None else observations if observations is not None else ai_results
        topics = self._topics(topic_set)
        requested = self._context(context, topic_set)
        normalized_target = _domain(target_domain)
        rows_by_topic: dict[str, list[dict[str, Any]]] = {}
        evidence_rows = [dict(item) for item in (evidence or []) if isinstance(item, Mapping)]
        for raw in evidence_rows:
            if not isinstance(raw, Mapping):
                continue
            row = dict(raw)
            topic_id = str(row.get("topic_id") or row.get("prompt_id") or row.get("id") or "")
            prompt = str(row.get("prompt") or row.get("keyword") or "").strip()
            if not topic_id:
                topic_id = self._topic_id_for_prompt(topics, prompt)
            if topic_id and self._evidence_matches(row, topic_set, requested):
                rows_by_topic.setdefault(topic_id, []).append(row)

        output_rows: list[dict[str, Any]] = []
        total_mentions = 0
        target_mentions = 0
        total_citations = 0
        target_citations = 0
        target_pages: set[str] = set()
        competitor_mentions: Counter[str] = Counter()
        complete_count = 0
        raw_refs: list[str] = []
        for topic in topics:
            topic_id = str(topic.get("id") or self._topic_id_for_prompt(topics, str(topic.get("prompt"))))
            candidates = rows_by_topic.get(topic_id, [])
            candidate = sorted(candidates, key=lambda item: str(item.get("snapshot_date") or item.get("raw_artifact_ref") or ""))[-1] if candidates else None
            if candidate is not None and not self._has_observation(candidate):
                candidate = None
            if candidate is None:
                output_rows.append({
                    "topic_id": topic_id,
                    "prompt": topic.get("prompt"),
                    "status": "unknown",
                    "target_mentioned": None,
                    "target_cited": None,
                    "distinct_target_pages": None,
                })
                continue
            complete_count += 1
            parsed = self._attribution(candidate, normalized_target, entity_name)
            total_mentions += parsed["total_mentions"]
            target_mentions += parsed["target_mentions"]
            total_citations += parsed["total_citations"]
            target_citations += parsed["target_citations"]
            target_pages.update(parsed["target_pages"])
            competitor_mentions.update(parsed["competitor_mentions"])
            if candidate.get("raw_artifact_ref"):
                raw_refs.append(str(candidate["raw_artifact_ref"]))
            output_rows.append({
                "topic_id": topic_id,
                "prompt": topic.get("prompt"),
                "status": "complete",
                "target_mentioned": parsed["target_mentions"] > 0,
                "target_cited": parsed["target_citations"] > 0,
                "mention_count": parsed["target_mentions"],
                "citation_count": parsed["target_citations"],
                "distinct_target_pages": sorted(parsed["target_pages"]),
                "mentions": parsed["mentions"],
                "citations": parsed["citations"],
                "snapshot_date": candidate.get("snapshot_date"),
                "raw_artifact_ref": candidate.get("raw_artifact_ref"),
            })

        expected = len(topics)
        coverage = complete_count / expected * 100 if expected else 0.0
        context_complete = all(
            value not in {None, ""}
            for value in (
                requested.market,
                requested.location_code,
                requested.language_code,
                requested.device,
                requested.snapshot_date,
            )
        )
        if (
            not self._is_approved(topic_set)
            or not topics
            or not normalized_target
            or not context_complete
            or complete_count == 0
        ):
            status = "unknown"
        elif coverage < self.MIN_COMPLETE_COVERAGE_PERCENT:
            status = "unknown"
        elif complete_count < expected:
            status = "partial"
        else:
            status = "complete"
        # ``total_mentions`` includes target and competitors; competitor
        # counts are already tracked separately, so do not double-count them.
        denominator = target_mentions + sum(competitor_mentions.values())
        metrics: dict[str, Any] = {
            "contract_version": self.VERSION,
            "topic_set_id": self._topic_set_id(topic_set),
            "topic_set_version": self._topic_set_version(topic_set),
            "topic_set_source_sha256": self._topic_set_source_hash(topic_set),
            "vertical_id": _payload(topic_set).get("vertical_id"),
            "context": requested.to_dict(),
            "target_domain": normalized_target,
            "prompt_count": expected,
            "observed_prompt_count": complete_count,
            "prompt_coverage_percent": round(coverage, 4) if status != "unknown" else None,
            "prompt_coverage": round(coverage, 4) if status != "unknown" else None,
            "mention_count": target_mentions if status != "unknown" else None,
            "mentions": target_mentions if status != "unknown" else None,
            "observed_mentions": target_mentions if status != "unknown" else None,
            "citation_count": target_citations if status != "unknown" else None,
            "citations": target_citations if status != "unknown" else None,
            "observed_citations": target_citations if status != "unknown" else None,
            "distinct_cited_pages": len(target_pages) if status != "unknown" else None,
            "distinct_pages": len(target_pages) if status != "unknown" else None,
            "distinct_cited_page_urls": sorted(target_pages) if status != "unknown" else [],
            "share_of_voice_percent": round(target_mentions / denominator * 100, 4) if denominator and status != "unknown" else None,
            "share_of_voice": round(target_mentions / denominator * 100, 4) if denominator and status != "unknown" else None,
            "competitor_mention_counts": dict(competitor_mentions),
            "total_observed_mentions": total_mentions if status != "unknown" else None,
            "total_observed_citations": total_citations if status != "unknown" else None,
            "raw_artifact_refs": sorted(set(raw_refs)),
            "provider_cost_usd": round(sum(float(item.get("provider_cost_usd") or 0.0) for item in evidence_rows), 6),
        }
        warnings: list[str] = []
        if status == "unknown":
            warnings.append("Observed AI evidence is unavailable, sparse, or context-mismatched; visibility remains unknown.")
        elif status == "partial":
            warnings.append("Observed AI evidence is incomplete for one or more approved prompts.")
        warnings.append("Observed AI Visibility is independent evidence and never changes AI Readiness.")
        return ProductSurfaceResult(
            surface="observed_ai_visibility",
            version=self.VERSION,
            status=status,
            score=None,
            completeness_percent=round(coverage, 4),
            evidence_confidence=round(coverage, 4),
            checks=output_rows,
            metrics=metrics,
            warnings=warnings,
        )

    evaluate = build
    build_visibility = build
    calculate_visibility = build

    def collect(
        self,
        topic_set: Any = None,
        provider: Any = None,
        *,
        target_domain: str,
        context: Mapping[str, Any] | AIVisibilityContext | None = None,
        entity_name: str | None = None,
        existing_evidence: Iterable[Mapping[str, Any]] | None = None,
        approved: bool = False,
        allow_paid_api_calls: bool = False,
        provider_configured: bool = False,
        call_cap: int | None = None,
        prompt_topic_set: Any = None,
        **_: Any,
    ) -> ProductSurfaceResult:
        """Collect one bounded provider observation per approved topic."""

        topic_set = topic_set if topic_set is not None else prompt_topic_set
        existing_rows = [dict(item) for item in (existing_evidence or []) if isinstance(item, Mapping)]
        requested = self._context(context, topic_set)
        preflight = self.preflight(
            topic_set,
            provider_configured=provider_configured,
            operator_approved=approved,
            allow_paid_api_calls=allow_paid_api_calls,
            existing_evidence=existing_rows,
            call_cap=call_cap,
            context=requested,
        )
        if preflight["status"] != "ready":
            result = self.build(topic_set, existing_rows, target_domain, context=context, entity_name=entity_name)
            result.metrics["preflight"] = preflight
            return result
        rows = list(existing_rows)
        for topic in self._topics(topic_set):
            topic_id = str(topic.get("id") or self._topic_id_for_prompt(self._topics(topic_set), str(topic.get("prompt"))))
            if any(self._evidence_matches(item, topic_set, requested) and str(item.get("topic_id") or item.get("prompt_id") or "") == topic_id for item in rows):
                continue
            try:
                method = getattr(provider, "collect_ai_visibility", None) or getattr(provider, "collect_ai_overview", None) or getattr(provider, "collect_ai_serp", None)
                if method is None:
                    raise AttributeError("provider does not implement an AI visibility collection method")
                payload = method(
                    str(topic.get("prompt")),
                    location_code=requested.location_code,
                    language_code=requested.language_code or "en",
                    device=requested.device or "desktop",
                    market=requested.market,
                    topic_id=topic_id,
                    topic_set_id=self._topic_set_id(topic_set),
                )
                row = dict(payload) if isinstance(payload, Mapping) else {"status": "unknown"}
            except Exception as exc:
                row = {"status": "unknown", "provider_error": str(exc)}
            row.setdefault("topic_id", topic_id)
            row.setdefault("prompt", topic.get("prompt"))
            row.setdefault("prompt_topic_set_id", self._topic_set_id(topic_set))
            row.setdefault("prompt_topic_set_version", self._topic_set_version(topic_set))
            row.setdefault("market", requested.market)
            row.setdefault("location_code", requested.location_code)
            row.setdefault("language_code", requested.language_code)
            row.setdefault("device", requested.device)
            rows.append(row)
        if requested.snapshot_date is None:
            observed_dates = {
                str(row.get("snapshot_date"))
                for row in rows
                if row.get("snapshot_date")
            }
            if len(observed_dates) == 1:
                requested.snapshot_date = observed_dates.pop()
        result = self.build(
            topic_set,
            rows,
            target_domain,
            context=requested,
            entity_name=entity_name,
        )
        result.metrics["preflight"] = preflight
        result.metrics["provider_call_count"] = max(0, len(rows) - len(existing_rows))
        result.metrics["provider_cost_usd"] = round(sum(float(item.get("provider_cost_usd") or 0.0) for item in rows if isinstance(item, Mapping)), 6)
        return result

    observe = collect
    collect_visibility = collect
    calculate = build

    @staticmethod
    def _topics(topic_set: Any) -> list[dict[str, Any]]:
        payload = _payload(topic_set)
        rows = payload.get("topics") if isinstance(payload.get("topics"), list) else []
        output: list[dict[str, Any]] = []
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping) or not str(row.get("prompt") or "").strip():
                continue
            item = dict(row)
            item.setdefault("id", f"topic-{index + 1}")
            output.append(item)
        return output

    @staticmethod
    def _is_approved(topic_set: Any) -> bool:
        return str(_payload(topic_set).get("state") or "") == "approved"

    @staticmethod
    def _topic_set_id(topic_set: Any) -> str | None:
        value = _payload(topic_set).get("id")
        return str(value) if value else None

    @staticmethod
    def _topic_set_version(topic_set: Any) -> int | None:
        value = _payload(topic_set).get("version")
        return int(value) if isinstance(value, int | float) else None

    @staticmethod
    def _topic_set_source_hash(topic_set: Any) -> str | None:
        value = _payload(topic_set).get("source_sha256")
        return str(value) if value else None

    @staticmethod
    def _topic_id_for_prompt(topics: list[dict[str, Any]], prompt: str) -> str:
        normalized = " ".join(prompt.casefold().split())
        for index, topic in enumerate(topics):
            if " ".join(str(topic.get("prompt") or "").casefold().split()) == normalized:
                return str(topic.get("id") or f"topic-{index + 1}")
        return ""

    @staticmethod
    def _context(value: Mapping[str, Any] | AIVisibilityContext | None, topic_set: Any) -> AIVisibilityContext:
        if isinstance(value, AIVisibilityContext):
            return value
        source = dict(value or {})
        topic_payload = _payload(topic_set)
        source.setdefault("market", topic_payload.get("market"))
        return AIVisibilityContext(
            market=source.get("market"),
            location_code=source.get("location_code"),
            language_code=source.get("language_code"),
            device=source.get("device"),
            snapshot_date=source.get("snapshot_date") or source.get("date"),
        )

    def _evidence_identity_matches(self, row: Mapping[str, Any], topic_set: Any) -> bool:
        set_id = self._topic_set_id(topic_set)
        set_version = self._topic_set_version(topic_set)
        vertical_id = _payload(topic_set).get("vertical_id")
        if row.get("vertical_id") is not None and vertical_id is not None and str(row.get("vertical_id")) != str(vertical_id):
            return False
        observed_set_id = row.get("prompt_topic_set_id") or row.get("topic_set_id")
        observed_version = row.get("prompt_topic_set_version") or row.get("topic_set_version")
        if set_id is not None and str(observed_set_id or "") != set_id:
            return False
        if set_version is not None:
            try:
                if int(observed_version) != set_version:
                    return False
            except (TypeError, ValueError):
                return False
        return True

    def _evidence_matches(self, row: Mapping[str, Any], topic_set: Any, context: AIVisibilityContext) -> bool:
        if not self._evidence_identity_matches(row, topic_set):
            return False
        nested = dict(row)
        if isinstance(row.get("context"), Mapping):
            nested.update(row["context"])
        checks = (("market", context.market), ("location_code", context.location_code), ("language_code", context.language_code), ("device", context.device), ("snapshot_date", context.snapshot_date))
        for key, expected in checks:
            if expected is not None and nested.get(key) != expected:
                return False
        return str(row.get("status") or "complete") in {"complete", "success", "completed"}

    @staticmethod
    def _attribution(row: Mapping[str, Any], target_domain: str, entity_name: str | None) -> dict[str, Any]:
        mentions_raw: list[Any] = []
        citations_raw: list[Any] = []
        for key in ("mentions", "mentioned_entities", "entities", "brands"):
            value = row.get(key)
            if isinstance(value, list):
                mentions_raw.extend(value)
            elif isinstance(value, Mapping):
                mentions_raw.append(value)
        for key in ("citations", "references", "links", "sources"):
            value = row.get(key)
            if isinstance(value, list):
                citations_raw.extend(value)
            elif isinstance(value, Mapping):
                citations_raw.append(value)
        overview = row.get("items") or row.get("results") or row.get("ai_overview") or row.get("result")
        if isinstance(overview, list):
            for item in overview:
                if isinstance(item, Mapping):
                    for key in ("mentions", "mentioned_entities", "entities", "brands"):
                        if isinstance(item.get(key), list):
                            mentions_raw.extend(item[key])
                        elif isinstance(item.get(key), Mapping):
                            mentions_raw.append(item[key])
                    for key in ("citations", "references", "links", "sources"):
                        if isinstance(item.get(key), list):
                            citations_raw.extend(item[key])
                        elif isinstance(item.get(key), Mapping):
                            citations_raw.append(item[key])
                    if item.get("url") or item.get("link"):
                        citations_raw.append({"url": item.get("url") or item.get("link")})
        response_text = _text(row.get("response_text") or row.get("answer") or row.get("markdown") or row.get("text"))
        if isinstance(overview, list):
            response_text = f"{response_text} {_text(overview)}"
        if response_text and target_domain and target_domain in response_text.casefold():
            mentions_raw.append({"domain": target_domain, "source": "response_text"})
        if response_text and entity_name and entity_name.casefold() in response_text.casefold() and not (target_domain and target_domain in response_text.casefold()):
            mentions_raw.append({"name": entity_name, "domain": target_domain, "source": "response_text"})
        mention_rows: list[dict[str, Any]] = []
        target_mentions = 0
        competitor_mentions: Counter[str] = Counter()
        for item in mentions_raw:
            text = _text(item)
            domain = _domain(item.get("domain") or item.get("url") or item.get("website")) if isinstance(item, Mapping) else _domain(text)
            name = str(item.get("name") or item.get("title") or text).strip() if isinstance(item, Mapping) else text.strip()
            is_target = bool(target_domain and (domain == target_domain or target_domain in text.casefold() or (entity_name and entity_name.casefold() in text.casefold())))
            if is_target:
                target_mentions += 1
            elif domain or name:
                competitor_mentions[domain or name.casefold()] += 1
            mention_rows.append({"name": name, "domain": domain or None, "target": is_target, "source": item.get("source") if isinstance(item, Mapping) else None})
        citation_rows: list[dict[str, Any]] = []
        target_citations = 0
        target_pages: set[str] = set()
        for item in citations_raw:
            value = item.get("url") or item.get("link") or item.get("source_url") if isinstance(item, Mapping) else item
            link = _url(value)
            domain = _domain(link)
            is_target = bool(target_domain and domain == target_domain)
            if is_target:
                target_citations += 1
                target_pages.add(AIVisibilityService._page_identity(link))
            citation_rows.append({"url": link, "domain": domain or None, "target": is_target})
        return {
            "mentions": mention_rows,
            "citations": citation_rows,
            "target_mentions": target_mentions,
            "total_mentions": len(mention_rows),
            "target_citations": target_citations,
            "total_citations": len(citation_rows),
            "target_pages": target_pages,
            "competitor_mentions": competitor_mentions,
        }

    @staticmethod
    def _page_identity(value: str) -> str:
        parsed = urlsplit(value)
        if not parsed.hostname:
            return value.rstrip("#")
        path = parsed.path.rstrip("/") or "/"
        domain = parsed.hostname.casefold().rstrip(".").removeprefix("www.")
        return f"https://{domain}{path}"

    @staticmethod
    def _has_observation(row: Mapping[str, Any]) -> bool:
        """Empty provider envelopes are unavailable, not measured zeroes."""

        for key in ("mentions", "mentioned_entities", "entities", "brands", "citations", "references", "links", "sources"):
            if (isinstance(row.get(key), list) and row.get(key)) or isinstance(row.get(key), Mapping):
                return True
        for key in ("response_text", "answer", "markdown", "text"):
            if str(row.get(key) or "").strip():
                return True
        for key in ("items", "results", "ai_overview", "result"):
            if isinstance(row.get(key), list) and row.get(key):
                return True
        return False


def build_ai_visibility(*args: Any, **kwargs: Any) -> ProductSurfaceResult:
    return AIVisibilityService().build(*args, **kwargs)


ObservedAIVisibilityService = AIVisibilityService

__all__ = ["AIVisibilityContext", "AIVisibilityService", "ObservedAIVisibilityService", "build_ai_visibility"]
