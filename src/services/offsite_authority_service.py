from __future__ import annotations

from datetime import date
from typing import Any, Mapping

from src.services.search_intelligence_service import (
    SearchIntelligenceOutput,
    TargetContext,
    normalize_domain,
)


OFFSITE_AUTHORITY_VERSION = "offsite-authority.v1"
OFFSITE_AUTHORITY_PROVIDER = "DataForSEO"
OFFSITE_AUTHORITY_METRIC_LABEL = "DataForSEO Link Rank"


def _count(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int | float) or value < 0:
        return None
    return int(value)


def _percent(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return round(min(100.0, max(0.0, numerator / denominator * 100)), 2)


def build_offsite_authority_view(
    search: SearchIntelligenceOutput,
    target_context: TargetContext | Mapping[str, Any],
    *,
    checkpoint_path: str | None = None,
) -> dict[str, Any]:
    """Validate and present provider-specific link evidence without scoring the site."""
    context = TargetContext.from_value(target_context)
    payload = search.payload if isinstance(search.payload, dict) else {}
    raw = payload.get("offsite_authority")
    limitations = [
        "DataForSEO Link Rank is a proprietary link-graph metric; it is not Google Domain Authority or an exposed Google PageRank value.",
        "Off-site authority is evidence only and does not change the SEO or AI Readiness scores.",
    ]
    base = {
        "version": OFFSITE_AUTHORITY_VERSION,
        "provider": OFFSITE_AUTHORITY_PROVIDER,
        "metric_label": OFFSITE_AUTHORITY_METRIC_LABEL,
        "status": "unknown",
        "target_domain": context.target_domain,
        "snapshot_date": None,
        "source": None,
        "rank_scale": "one_hundred",
        "link_rank": None,
        "backlinks": None,
        "backlinks_spam_score": None,
        "target_spam_score": None,
        "broken_backlinks": None,
        "broken_pages": None,
        "referring_domains": None,
        "referring_domains_nofollow": None,
        "referring_domains_nofollow_percent": None,
        "referring_main_domains": None,
        "referring_main_domains_nofollow": None,
        "referring_pages": None,
        "referring_pages_nofollow": None,
        "referring_pages_nofollow_percent": None,
        "referring_ips": None,
        "referring_subnets": None,
        "first_seen": None,
        "lost_date": None,
        "top_referring_tlds": {},
        "provider_cost_usd": None,
        "provider_error": None,
        "evidence_ref": None,
        "limitations": limitations,
    }
    if not search.configured:
        limitations.append("Paid backlink evidence is not configured.")
        return base
    if not search.approved:
        limitations.append(search.skipped_reason or "Paid backlink evidence was not approved.")
        return base
    if not isinstance(raw, Mapping):
        limitations.append("No backlink summary was collected for this run.")
        return base

    base["snapshot_date"] = raw.get("snapshot_date")
    base["source"] = raw.get("source")
    base["provider_error"] = raw.get("provider_error")
    target_matches = normalize_domain(str(raw.get("target_domain") or "")) == normalize_domain(context.target_domain)
    try:
        date.fromisoformat(str(raw.get("snapshot_date") or ""))
        valid_date = True
    except ValueError:
        valid_date = False
    valid_source = raw.get("source") == "dataforseo_backlinks_summary_live"
    valid_scale = raw.get("rank_scale") == "one_hundred"
    link_rank = _count(raw.get("link_rank"))
    if link_rank is not None and link_rank > 100:
        link_rank = None

    if raw.get("status") != "complete" or not target_matches or not valid_date or not valid_source or not valid_scale:
        limitations.append("The backlink summary did not pass the target-bound evidence contract.")
        return base

    metric_names = (
        "backlinks",
        "backlinks_spam_score",
        "target_spam_score",
        "broken_backlinks",
        "broken_pages",
        "referring_domains",
        "referring_domains_nofollow",
        "referring_main_domains",
        "referring_main_domains_nofollow",
        "referring_pages",
        "referring_pages_nofollow",
        "referring_ips",
        "referring_subnets",
    )
    for name in metric_names:
        base[name] = _count(raw.get(name))
    base.update(
        {
            "status": "complete" if link_rank is not None else "partial",
            "link_rank": link_rank,
            "first_seen": raw.get("first_seen"),
            "lost_date": raw.get("lost_date"),
            "top_referring_tlds": raw.get("top_referring_tlds") if isinstance(raw.get("top_referring_tlds"), dict) else {},
            "provider_cost_usd": raw.get("provider_cost_usd"),
            "evidence_ref": (
                {
                    "artifact_path": checkpoint_path,
                    "field": "payload.payload.offsite_authority",
                    "reason": "Persisted target-bound DataForSEO Backlinks Summary evidence.",
                }
                if checkpoint_path
                else None
            ),
        }
    )
    base["referring_domains_nofollow_percent"] = _percent(
        base["referring_domains_nofollow"],
        base["referring_domains"],
    )
    base["referring_pages_nofollow_percent"] = _percent(
        base["referring_pages_nofollow"],
        base["referring_pages"],
    )
    if base["status"] == "partial":
        limitations.append("The provider returned backlink counts but no valid 0–100 Link Rank.")
    return base
