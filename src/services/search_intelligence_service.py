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
    if not isinstance(urls, list) or not urls:
        return None
    target_domain = normalize_domain(context.target_domain)
    for url in urls:
        if not isinstance(url, str):
            return None
        host = normalize_domain(urlsplit(url).hostname or "")
        if host != target_domain and not host.endswith(f".{target_domain}"):
            return None
    return float(score)


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
        response = client.get_errors_reference()
        return SearchIntelligenceOutput(
            configured=True,
            skipped_reason="Target-specific search evidence was not collected by the reference connectivity call.",
            payload={
                "status_code": response.get("status_code"),
                "tasks_error": response.get("tasks_error"),
                "raw_excerpt_keys": sorted(response.keys())[:10],
            },
            approved=True,
            requested_context=requested,
        )
