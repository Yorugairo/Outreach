"""Search Visibility v2 from approved demand and context-bound organic SERPs.

This module deliberately keeps visibility independent from technical, AI, and
conversion scores.  The provider response is treated as a dated sample: a
completed SERP with no target result is a measured zero, while a missing or
context-mismatched SERP remains unknown.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

from src.models import PRODUCT_SURFACE_VERSIONS, ProductSurfaceResult


def _norm(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def _domain(value: Any) -> str:
    text = str(value or "").strip().casefold()
    if "://" in text:
        text = urlsplit(text).hostname or ""
    return text.rstrip(".").removeprefix("www.")


@dataclass(slots=True)
class VisibilityContext:
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


class SearchVisibilityService:
    """Build ``search-visibility.v2`` without changing any other score."""

    VERSION = PRODUCT_SURFACE_VERSIONS["search_visibility"]

    def __init__(self, target_domain: str | None = None) -> None:
        self.target_domain = target_domain

    def build(
        self,
        demand: Any = None,
        organic_evidence: Iterable[Mapping[str, Any]] | None = None,
        target_domain: str | None = None,
        *,
        context: Mapping[str, Any] | VisibilityContext | None = None,
        demand_evidence: Any = None,
        approved_demand: Any = None,
        keyword_set: Any = None,
        market_run: Any = None,
        organic_snapshots: Iterable[Mapping[str, Any]] | None = None,
        **_: Any,
    ) -> ProductSurfaceResult:
        """Build metrics from an approved demand set and SERP snapshots.

        ``demand_evidence``/``keyword_set`` and ``market_run`` aliases make the
        service usable by both the demand importer and the market lifecycle.
        No network call is made here.
        """

        if demand is None:
            demand = demand_evidence if demand_evidence is not None else approved_demand if approved_demand is not None else keyword_set
        if organic_evidence is None and organic_snapshots is not None:
            organic_evidence = organic_snapshots
        if market_run is not None:
            if organic_evidence is None:
                organic_evidence = getattr(market_run, "organic_evidence", None)
            if target_domain is None:
                target_domain = getattr(market_run, "target_domain", None)
            if context is None:
                context = {
                    key: getattr(market_run, key, None)
                    for key in ("market", "location_code", "language_code", "device")
                }

        requested = self._context(context, demand)
        rows, demand_ok, demand_warning = self._demand_rows(demand)
        snapshots = [dict(item) for item in (organic_evidence or []) if isinstance(item, Mapping)]
        normalized_target = _domain(target_domain or self.target_domain)
        warnings: list[str] = []
        if demand_warning:
            warnings.append(demand_warning)
        if not demand_ok:
            return self._result(
                status="unknown",
                rows=[],
                metrics={"context": requested.to_dict(), "target_domain": normalized_target},
                completeness=0.0,
                warnings=warnings or ["Approved demand evidence is unavailable."],
            )
        missing_context = []
        if requested.market is None and requested.location_code is None:
            missing_context.append("market/location")
        for name in ("language_code", "device"):
            if not getattr(requested, name):
                missing_context.append(name)
        if not normalized_target:
            missing_context.append("target_domain")
        if missing_context:
            return self._result(
                status="unknown",
                rows=[],
                metrics={
                    "context": requested.to_dict(),
                    "target_domain": normalized_target,
                },
                completeness=0.0,
                warnings=[
                    "Search Visibility requires explicit "
                    + ", ".join(missing_context)
                    + " context."
                ],
            )

        by_keyword: dict[str, list[dict[str, Any]]] = {}
        for snapshot in snapshots:
            keyword = _norm(snapshot.get("keyword") or snapshot.get("query"))
            if keyword:
                by_keyword.setdefault(keyword, []).append(snapshot)

        output_rows: list[dict[str, Any]] = []
        valid_count = 0
        for row in rows:
            keyword = _norm(row.get("keyword"))
            candidate = self._select_snapshot(by_keyword.get(keyword, []), requested)
            if candidate is None:
                output_rows.append({
                    **row,
                    "keyword": row.get("keyword") or keyword,
                    "rank": None,
                    "observed": False,
                    "evidence_status": "unknown",
                })
                continue
            valid_count += 1
            rank = self._target_rank(candidate, normalized_target)
            output_rows.append({
                **row,
                "keyword": row.get("keyword") or keyword,
                "rank": rank,
                "observed": True,
                "evidence_status": "complete",
                "snapshot_date": candidate.get("snapshot_date"),
                "raw_artifact_ref": candidate.get("raw_artifact_ref"),
            })

        expected = len(output_rows)
        completeness = valid_count / expected * 100 if expected else 0.0
        if valid_count == 0:
            status = "unknown"
        elif valid_count < expected:
            status = "partial"
            warnings.append("Organic evidence is incomplete for one or more approved demand terms.")
        else:
            status = "complete"

        ranks = [int(item["rank"]) for item in output_rows if isinstance(item.get("rank"), int | float)]
        weighted_rows = [item for item in output_rows if item.get("evidence_status") == "complete"]
        weighted_denominator = sum(float(item.get("demand_weight") or 0.0) for item in weighted_rows)
        if weighted_denominator <= 0:
            weighted_denominator = float(len(weighted_rows))
            weights_unknown = True
        else:
            weights_unknown = False
        weighted_visibility = (
            sum(
                (max(0.0, 101.0 - float(item["rank"])) if item.get("rank") is not None else 0.0)
                * (float(item.get("demand_weight") or 0.0) if not weights_unknown else 1.0)
                for item in weighted_rows
            )
            / weighted_denominator
            if weighted_rows and weighted_denominator
            else None
        )
        if weights_unknown and weighted_rows:
            warnings.append("Approved demand volumes were unavailable; weighted visibility uses equal term weights.")
        top3 = sum(1 for item in output_rows if item.get("rank") is not None and item["rank"] <= 3)
        top10 = sum(1 for item in output_rows if item.get("rank") is not None and item["rank"] <= 10)
        top20 = sum(1 for item in output_rows if item.get("rank") is not None and item["rank"] <= 20)
        metrics = {
            "contract_version": self.VERSION,
            "target_domain": normalized_target,
            "context": requested.to_dict(),
            "tracked_keyword_count": expected,
            "evidence_keyword_count": valid_count,
            "tracked_keyword_coverage_percent": round(completeness, 4),
            "tracked_keyword_coverage": round(completeness, 4),
            "top_3_count": top3,
            "top_10_count": top10,
            "top_20_count": top20,
            "top_3_coverage_percent": round(top3 / expected * 100, 4) if expected else 0.0,
            "top_10_coverage_percent": round(top10 / expected * 100, 4) if expected else 0.0,
            "top_20_coverage_percent": round(top20 / expected * 100, 4) if expected else 0.0,
            "top_3_coverage": round(top3 / expected * 100, 4) if expected else 0.0,
            "top_10_coverage": round(top10 / expected * 100, 4) if expected else 0.0,
            "top_20_coverage": round(top20 / expected * 100, 4) if expected else 0.0,
            "weighted_visibility": round(weighted_visibility, 4) if weighted_visibility is not None else None,
            "median_rank": float(median(ranks)) if ranks else None,
            "snapshot_dates": sorted(
                {
                    str(item["snapshot_date"])
                    for item in output_rows
                    if item.get("snapshot_date")
                }
            ),
            "keywords": output_rows,
        }
        return self._result(
            status=status,
            rows=output_rows,
            metrics=metrics,
            completeness=completeness,
            warnings=warnings,
            score=None,
        )

    evaluate = build

    @classmethod
    def from_market_run(cls, market_run: Any, demand: Any) -> ProductSurfaceResult:
        return cls().build(demand, getattr(market_run, "organic_evidence", []), getattr(market_run, "target_domain", None), market_run=market_run)

    @staticmethod
    def _context(value: Mapping[str, Any] | VisibilityContext | None, demand: Any) -> VisibilityContext:
        if isinstance(value, VisibilityContext):
            return value
        source: Mapping[str, Any] = value or {}
        if not source and isinstance(demand, Mapping):
            source = demand
        if not source and isinstance(demand, Iterable) and not isinstance(demand, (str, bytes)):
            first = next(iter(demand), None)
            if isinstance(first, Mapping):
                source = first
        if not source and demand is not None:
            source = {key: getattr(demand, key, None) for key in ("market", "location_code", "language_code", "device")}
        return VisibilityContext(
            market=source.get("market"),
            location_code=source.get("location_code"),
            language_code=source.get("language_code"),
            device=source.get("device"),
            snapshot_date=source.get("snapshot_date") or source.get("date"),
        )

    @staticmethod
    def _demand_rows(demand: Any) -> tuple[list[dict[str, Any]], bool, str | None]:
        if demand is None:
            return [], False, "Approved demand evidence is unavailable."
        state = getattr(demand, "state", None)
        if state is None and isinstance(demand, Mapping):
            state = demand.get("state")
        if state is not None and state != "approved":
            return [], False, "Search Visibility requires approved demand evidence."
        if hasattr(demand, "rows") and hasattr(demand, "groups"):
            rows = list(getattr(demand, "rows") or [])
            groups = list(getattr(demand, "groups") or [])
            approved_ids = {
                item_id
                for group in groups
                if (getattr(group, "status", None) or (group.get("status") if isinstance(group, Mapping) else None)) == "approved"
                for item_id in (getattr(group, "included_keyword_ids", None) or (group.get("included_keyword_ids", []) if isinstance(group, Mapping) else []))
            }
            if approved_ids:
                rows = [row for row in rows if (getattr(row, "id", None) or (row.get("id") if isinstance(row, Mapping) else None)) in approved_ids]
            normalized: list[dict[str, Any]] = []
            for row in rows:
                item = row.to_dict() if hasattr(row, "to_dict") else dict(row)
                item["demand_weight"] = item.get("monthly_searches")
                normalized.append(item)
            return normalized, bool(normalized), None if normalized else "Approved demand contains no reviewed keyword rows."
        if hasattr(demand, "targets"):
            demand = demand.targets()
        if isinstance(demand, Mapping):
            demand = demand.get("keywords") or demand.get("rows") or []
        rows = []
        for item in demand if isinstance(demand, Iterable) and not isinstance(demand, (str, bytes)) else []:
            payload = item.to_dict() if hasattr(item, "to_dict") else dict(item) if isinstance(item, Mapping) else {"keyword": str(item)}
            if payload.get("review_status") not in {None, "approved"} or payload.get("approved") is False:
                continue
            payload["demand_weight"] = payload.get("approved_monthly_search_occasions", payload.get("monthly_searches", payload.get("search_volume")))
            rows.append(payload)
        return rows, bool(rows), None if rows else "Approved demand contains no reviewed keyword rows."

    @staticmethod
    def _select_snapshot(snapshots: list[dict[str, Any]], context: VisibilityContext) -> dict[str, Any] | None:
        matches = [item for item in snapshots if SearchVisibilityService._context_matches(item, context)]
        if not matches:
            return None
        return sorted(matches, key=lambda item: (str(item.get("snapshot_date") or ""), str(item.get("raw_artifact_ref") or "")))[-1]

    @staticmethod
    def _context_matches(snapshot: Mapping[str, Any], context: VisibilityContext) -> bool:
        checks = (("market", context.market), ("location_code", context.location_code), ("language_code", context.language_code), ("device", context.device), ("snapshot_date", context.snapshot_date))
        for key, expected in checks:
            if expected is not None and snapshot.get(key) != expected:
                return False
        if not isinstance(snapshot.get("snapshot_date"), str) or not str(
            snapshot["snapshot_date"]
        ).strip():
            return False
        return snapshot.get("status", "complete") in {"complete", "success", "completed"}

    @staticmethod
    def _target_rank(snapshot: Mapping[str, Any], target_domain: str) -> int | None:
        rank = snapshot.get("target_rank")
        if isinstance(rank, int | float):
            return int(rank)
        rows = snapshot.get("results") if isinstance(snapshot.get("results"), list) else []
        matches = [item for item in rows if isinstance(item, Mapping) and _domain(item.get("url") or item.get("website")) == target_domain]
        return min((int(item.get("rank") or item.get("rank_absolute")) for item in matches if isinstance(item.get("rank") or item.get("rank_absolute"), int | float)), default=None)

    @staticmethod
    def _result(*, status: str, rows: list[dict[str, Any]], metrics: dict[str, Any], completeness: float, warnings: list[str], score: float | None = None) -> ProductSurfaceResult:
        confidence = completeness
        return ProductSurfaceResult(surface="search_visibility", version=SearchVisibilityService.VERSION, status=status, score=round(score, 4) if score is not None and status != "unknown" else None, completeness_percent=round(completeness, 4), evidence_confidence=round(confidence, 4), metrics=metrics, checks=rows, warnings=warnings)


def build_search_visibility(*args: Any, **kwargs: Any) -> ProductSurfaceResult:
    return SearchVisibilityService().build(*args, **kwargs)


calculate_search_visibility = build_search_visibility
SearchVisibilityV2Service = SearchVisibilityService


__all__ = ["SearchVisibilityService", "SearchVisibilityV2Service", "VisibilityContext", "build_search_visibility", "calculate_search_visibility"]
