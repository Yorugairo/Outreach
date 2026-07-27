from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Mapping
from urllib.parse import urlsplit

from src.config import AppConfig
from src.dataforseo_client import DataForSEOClient


@dataclass(frozen=True, slots=True)
class TargetContext:
    primary_url: str
    target_domain: str
    language_code: str
    device: str
    location_code: int | None = None
    market: str | None = None
    entity_name: str | None = None
    entity_name_source: str | None = None

    @classmethod
    def from_value(cls, value: TargetContext | Mapping[str, Any]) -> TargetContext:
        if isinstance(value, cls):
            return value
        if not isinstance(value, Mapping):
            raise TypeError("target_context must be TargetContext or a mapping")
        return cls(
            primary_url=str(value.get("primary_url", "")),
            target_domain=str(value.get("target_domain", "")),
            language_code=str(value.get("language_code", "")),
            device=str(value.get("device", "")),
            location_code=value.get("location_code"),
            market=value.get("market"),
            entity_name=value.get("entity_name"),
            entity_name_source=value.get("entity_name_source"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SearchIntelligenceOutput:
    configured: bool
    skipped_reason: str | None
    payload: dict[str, Any]
    approved: bool = False
    requested_context: dict[str, Any] | None = None


SEARCH_OPPORTUNITY_BANDS = (
    (1, 10, "protect_strengthen", "Protect and strengthen"),
    (11, 20, "near_term", "Near-term opportunity"),
    (21, 50, "improvement", "Substantial improvement opportunity"),
    (51, 100, "low_visibility", "Low observed visibility"),
)


def normalize_domain(value: str) -> str:
    candidate = value.strip().casefold().rstrip(".")
    if "://" in candidate:
        candidate = (urlsplit(candidate).hostname or "").casefold().rstrip(".")
    if candidate.startswith("www."):
        candidate = candidate[4:]
    return candidate


def validate_target_search_evidence(
    search: SearchIntelligenceOutput,
    target_context: TargetContext | Mapping[str, Any],
) -> float | None:
    """Single fail-closed gate for target-specific search visibility evidence."""
    context = TargetContext.from_value(target_context)
    payload = search.payload
    score = payload.get("visibility_score")
    if not search.configured or not search.approved:
        return None
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 100:
        return None
    if normalize_domain(str(payload.get("target_domain", ""))) != normalize_domain(context.target_domain):
        return None
    snapshot = payload.get("snapshot_date")
    if not isinstance(snapshot, str):
        return None
    try:
        date.fromisoformat(snapshot)
    except ValueError:
        return None
    if payload.get("language_code") != context.language_code or payload.get("device") != context.device:
        return None
    if context.location_code is not None:
        if payload.get("location_code") != context.location_code:
            return None
    elif not isinstance(payload.get("market"), str) or not payload["market"].strip():
        return None
    if not isinstance(payload.get("source"), str) or not payload["source"].strip():
        return None
    urls = payload.get("observed_ranking_urls")
    if not isinstance(urls, list):
        return None
    target_domain = normalize_domain(context.target_domain)
    for url in urls:
        if not isinstance(url, str):
            return None
        host = normalize_domain(urlsplit(url).hostname or "")
        if host != target_domain and not host.endswith(f".{target_domain}"):
            return None
    snapshots = payload.get("serp_snapshots")
    if snapshots is not None:
        if not isinstance(snapshots, list) or not snapshots:
            return None
        calculated_scores: list[float] = []
        for snapshot_item in snapshots:
            if not isinstance(snapshot_item, Mapping):
                return None
            keyword = snapshot_item.get("keyword")
            rank = snapshot_item.get("rank")
            if not isinstance(keyword, str) or not keyword.strip():
                return None
            if rank is not None and (
                isinstance(rank, bool)
                or not isinstance(rank, int | float)
                or not 1 <= float(rank) <= 100
            ):
                return None
            calculated_scores.append(max(0.0, 101.0 - float(rank or 101)))
        expected_score = round(sum(calculated_scores) / len(calculated_scores), 2)
        if abs(float(score) - expected_score) > 0.01:
            return None
    elif not urls:
        # Compatibility path for pre-query-snapshot search artifacts.
        return None
    return float(score)


def _opportunity_band(rank: int | None) -> tuple[str, str]:
    if rank is None:
        return "not_observed_top_100", "Not observed in sampled top 100"
    for minimum, maximum, band, label in SEARCH_OPPORTUNITY_BANDS:
        if minimum <= rank <= maximum:
            return band, label
    return "invalid", "Invalid observed position"


def build_search_evidence_view(
    search: SearchIntelligenceOutput,
    target_context: TargetContext | Mapping[str, Any],
    *,
    checkpoint_path: str | None = None,
) -> dict[str, Any]:
    """Create the bounded operator/customer view over persisted provider data."""
    context = TargetContext.from_value(target_context)
    payload = search.payload if isinstance(search.payload, dict) else {}
    keyword_entries = payload.get("keywords") if isinstance(payload.get("keywords"), list) else []
    snapshots = payload.get("serp_snapshots") if isinstance(payload.get("serp_snapshots"), list) else []
    keyword_by_name = {
        str(item.get("keyword", "")).strip(): item
        for item in keyword_entries
        if isinstance(item, Mapping) and str(item.get("keyword", "")).strip()
    }
    snapshot_by_keyword = {
        str(item.get("keyword", "")).strip(): item
        for item in snapshots
        if isinstance(item, Mapping) and str(item.get("keyword", "")).strip()
    }
    ordered_keywords = list(keyword_by_name)
    for keyword in snapshot_by_keyword:
        if keyword not in keyword_by_name:
            ordered_keywords.append(keyword)

    target_domain = normalize_domain(context.target_domain)
    def is_target_url(value: Any) -> bool:
        host = normalize_domain(urlsplit(str(value or "")).hostname or "")
        return host == target_domain or host.endswith(f".{target_domain}")

    rows: list[dict[str, Any]] = []
    landscape: list[dict[str, Any]] = []
    for keyword in ordered_keywords:
        keyword_data = keyword_by_name.get(keyword, {})
        snapshot = snapshot_by_keyword.get(keyword)
        rank_value = snapshot.get("rank") if isinstance(snapshot, Mapping) else None
        rank = int(rank_value) if isinstance(rank_value, int | float) and not isinstance(rank_value, bool) else None
        absolute_value = snapshot.get("rank_absolute") if isinstance(snapshot, Mapping) else None
        absolute_rank = (
            int(absolute_value)
            if isinstance(absolute_value, int | float) and not isinstance(absolute_value, bool)
            else None
        )
        results = snapshot.get("results", []) if isinstance(snapshot, Mapping) else []
        target_results = [
            result
            for result in results
            if isinstance(result, Mapping)
            and is_target_url(result.get("url"))
        ]
        ranking_url = next(
            (
                str(item.get("url"))
                for item in sorted(
                    target_results,
                    key=lambda item: int(item.get("rank") or 10_000),
                )
                if item.get("url")
            ),
            None,
        )
        band, band_label = _opportunity_band(rank) if snapshot is not None else ("not_checked", "Not checked")
        row_index = len(rows)
        rows.append(
            {
                "keyword": keyword,
                "search_volume": keyword_data.get("search_volume"),
                "intent": keyword_data.get("intent"),
                "competition": keyword_data.get("competition"),
                "competition_level": keyword_data.get("competition_level"),
                "cpc": keyword_data.get("cpc"),
                "checked": snapshot is not None,
                "observed_rank": rank,
                "observed_absolute_position": absolute_rank,
                "observed_url": ranking_url,
                "opportunity_band": band,
                "opportunity_label": band_label,
                "evidence_ref": (
                    {
                        "artifact_path": checkpoint_path,
                        "field": f"payload.payload.serp_snapshots.{list(snapshot_by_keyword).index(keyword)}",
                        "reason": "Persisted target-specific Google organic SERP sample.",
                        "observed": {
                            "keyword": keyword,
                            "organic_position": rank,
                            "absolute_serp_position": absolute_rank,
                            "url": ranking_url,
                        },
                    }
                    if snapshot is not None and checkpoint_path
                    else None
                ),
            }
        )
        if snapshot is not None:
            top_results = []
            for result in results[:5]:
                if not isinstance(result, Mapping):
                    continue
                result_url = str(result.get("url") or "")
                top_results.append(
                    {
                        "rank": result.get("rank"),
                        "rank_absolute": result.get("rank_absolute"),
                        "domain": normalize_domain(urlsplit(result_url).hostname or ""),
                        "url": result_url,
                        "title": result.get("title"),
                        "is_target": is_target_url(result_url),
                    }
                )
            landscape.append({"keyword": keyword, "results": top_results, "keyword_row": row_index})

    valid_score = validate_target_search_evidence(search, context)
    checked_rows = [row for row in rows if row["checked"]]
    ranked_rows = [row for row in checked_rows if row["observed_rank"] is not None]
    limitations: list[str] = []
    provider_errors = payload.get("provider_errors") if isinstance(payload.get("provider_errors"), list) else []
    if not search.configured:
        status = "not_configured"
        limitations.append("Paid keyword and Google SERP evidence is not configured.")
    elif not search.approved:
        status = "not_approved"
        limitations.append(search.skipped_reason or "Paid search evidence was not approved for this run.")
    elif not rows:
        status = "limited"
        limitations.append("The provider returned no usable keyword evidence.")
    elif not checked_rows:
        status = "limited"
        limitations.append("Keywords were discovered, but no Google organic SERP queries were checked.")
    elif valid_score is None:
        status = "invalid"
        limitations.append("The collected search payload did not pass the target-bound evidence contract.")
    elif provider_errors:
        status = "partial"
        limitations.append(
            f"{len(provider_errors)} provider task(s) failed; affected queries remain unknown and are excluded from scoring."
        )
    else:
        status = "complete"
    if checked_rows:
        limitations.append(
            "Positions are observations from a dated market/device sample; absence means not observed in the sampled top 100, not proof of universal non-ranking."
        )

    raw_refs = payload.get("raw_artifact_refs")
    return {
        "status": status,
        "evidence_state": (
            "keyword_only"
            if rows and not checked_rows
            else "ranking_sample"
            if checked_rows
            else "unavailable"
        ),
        "configured": search.configured,
        "approved": search.approved,
        "skipped_reason": search.skipped_reason,
        "snapshot_date": payload.get("snapshot_date"),
        "market": payload.get("market"),
        "location_code": payload.get("location_code"),
        "language_code": payload.get("language_code"),
        "device": payload.get("device"),
        "source": payload.get("source"),
        "visibility_score": valid_score,
        "keyword_count": len(rows),
        "ranking_checks": len(checked_rows),
        "ranked_count": len(ranked_rows),
        "not_observed_count": len(checked_rows) - len(ranked_rows),
        "provider_call_count": len(raw_refs) if isinstance(raw_refs, list) else 0,
        "provider_errors": provider_errors,
        "keywords": rows,
        "serp_landscape": landscape,
        "limitations": limitations,
    }


def corroborated_external_mentions(search: SearchIntelligenceOutput) -> list[dict[str, Any]]:
    """Filter exact-name candidates through persisted site-topic evidence."""
    payload = search.payload
    mentions = payload.get("external_mentions")
    if not isinstance(mentions, list):
        return []
    topic_terms = payload.get("topic_terms")
    if not isinstance(topic_terms, list) or not topic_terms:
        keywords = payload.get("keywords")
        topic_terms = DataForSEOClient._topic_terms(
            [item for item in keywords or [] if isinstance(item, dict)]
        )
    if not topic_terms:
        # Legacy artifacts did not persist keyword/topic alignment fields.
        return [item for item in mentions if isinstance(item, dict)]
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in mentions:
        if not isinstance(item, dict) or item.get("exact_name_match") is not True:
            continue
        if item.get("topic_match") is True or DataForSEOClient._text_matches_topic(
            f"{item.get('title') or ''} {item.get('snippet') or ''}",
            topic_terms,
        ):
            fingerprint = " ".join(
                str(item.get("title") or item.get("domain") or "").casefold().split()
            )
            if not fingerprint or fingerprint in seen:
                continue
            seen.add(fingerprint)
            output.append(item)
    return output


class SearchIntelligenceService:
    def __init__(self, config: AppConfig, artifact_dir: str | None = None):
        self.config = config
        self.artifact_dir = artifact_dir

    def gather(self, target_context: TargetContext | Mapping[str, Any]) -> SearchIntelligenceOutput:
        requested = TargetContext.from_value(target_context).to_dict()
        if not self.config.dataforseo.configured:
            return SearchIntelligenceOutput(
                configured=False,
                skipped_reason="DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD not configured",
                payload={},
                approved=False,
                requested_context=requested,
            )
        if not self.config.approval.allow_paid_api_calls:
            return SearchIntelligenceOutput(
                configured=True,
                skipped_reason="Paid DataForSEO enrichment requires explicit operator approval",
                payload={},
                approved=False,
                requested_context=requested,
            )
        client = DataForSEOClient(self.config.dataforseo, artifact_dir=self.artifact_dir)
        context = TargetContext.from_value(target_context)
        location_code = context.location_code or self.config.dataforseo.default_location_code
        language_code = context.language_code or self.config.dataforseo.default_language_code
        market = context.market or f"location_code:{location_code}"
        max_paid_calls = self.config.dataforseo.max_paid_calls
        if max_paid_calls < 1:
            return SearchIntelligenceOutput(
                configured=True,
                skipped_reason="DataForSEO paid-call limit is zero",
                payload={},
                approved=False,
                requested_context=requested,
            )
        authority: dict[str, Any]
        try:
            authority = client.collect_offsite_authority(context.target_domain)
        except Exception as exc:
            authority = {
                "status": "unknown",
                "target_domain": context.target_domain,
                "snapshot_date": date.today().isoformat(),
                "source": "dataforseo_backlinks_summary_live",
                "rank_scale": "one_hundred",
                "provider_error": {
                    "status_code": None,
                    "status_message": f"Backlink summary request failed: {type(exc).__name__}",
                    "raw_artifact_ref": getattr(client, "last_raw_artifact", None),
                },
                "raw_artifact_ref": getattr(client, "last_raw_artifact", None),
            }
        remaining_calls = max_paid_calls - 1
        if remaining_calls < 1:
            response = {
                "target_domain": context.target_domain,
                "snapshot_date": date.today().isoformat(),
                "language_code": language_code,
                "device": context.device or "desktop",
                "location_code": location_code,
                "market": market,
                "source": "dataforseo_backlinks_summary_live",
                "keywords": [],
                "serp_snapshots": [],
                "observed_ranking_urls": [],
                "visibility_score": None,
                "provider_errors": [],
                "raw_artifact_refs": [],
            }
        else:
            try:
                # One call is reserved for authority and one for keyword
                # discovery. The remainder is split between rankings and one
                # corroborating brand query.
                mention_limit = 1 if context.entity_name and remaining_calls >= 2 else 0
                response = client.collect_target_search_evidence(
                    context,
                    location_code=location_code,
                    language_code=language_code,
                    device=context.device or "desktop",
                    market=market,
                    keyword_limit=10,
                    serp_limit=min(3, max(0, remaining_calls - 1 - mention_limit)),
                    entity_name=context.entity_name,
                    mention_limit=mention_limit,
                )
            except Exception as exc:
                response = {
                    "target_domain": context.target_domain,
                    "snapshot_date": date.today().isoformat(),
                    "language_code": language_code,
                    "device": context.device or "desktop",
                    "location_code": location_code,
                    "market": market,
                    "source": "dataforseo_backlinks_summary_live",
                    "keywords": [],
                    "serp_snapshots": [],
                    "observed_ranking_urls": [],
                    "visibility_score": None,
                    "provider_errors": [{
                        "operation": "target_search_evidence",
                        "status_code": None,
                        "status_message": f"Search evidence collection failed: {type(exc).__name__}",
                        "raw_artifact_ref": getattr(client, "last_raw_artifact", None),
                    }],
                    "raw_artifact_refs": [],
                }
        response["offsite_authority"] = authority
        authority_ref = authority.get("raw_artifact_ref")
        if authority_ref:
            response.setdefault("raw_artifact_refs", []).insert(0, authority_ref)
        return SearchIntelligenceOutput(
            configured=True,
            skipped_reason=None,
            payload=response,
            approved=True,
            requested_context=requested,
        )
