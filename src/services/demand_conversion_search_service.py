"""Context-safe alignment of observed search evidence to reviewed demand groups."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Iterable

from src.models import DemandEvidenceSet, OwnedMeasurementSnapshot


_TOKEN_RE = re.compile(r"[a-z0-9]+")


class DemandConversionSearchService:
    """Join GSC/public observations to approved intent groups without guessing."""

    def align(
        self,
        *,
        prospect_id: str,
        vertical_id: str,
        market: str,
        demand: DemandEvidenceSet | None,
        owner_snapshots: Iterable[OwnedMeasurementSnapshot] = (),
        public_rankings: Iterable[dict[str, Any]] = (),
    ) -> dict[str, Any]:
        if not prospect_id.strip() or not vertical_id.strip() or not market.strip():
            raise ValueError("search alignment requires prospect, vertical, and market")
        if demand is not None:
            self._validate_demand_context(
                demand,
                prospect_id=prospect_id,
                vertical_id=vertical_id,
                market=market,
            )
        snapshots = list(owner_snapshots)
        self._validate_owner_context(
            snapshots,
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            market=market,
        )
        rankings = [dict(row) for row in public_rankings]
        groups = self._group_terms(demand)
        buckets: dict[str, dict[str, Any]] = {
            family: {
                "intent_family": family,
                "representative_term": payload["representative_term"],
                "queries": [],
                "ranking_observations": [],
                "impressions": 0.0,
                "clicks": 0.0,
                "position_weighted_sum": 0.0,
                "position_weight": 0.0,
                "evidence_refs": [],
            }
            for family, payload in groups.items()
        }
        unmatched_queries: list[dict[str, Any]] = []
        for snapshot in snapshots:
            if snapshot.source != "gsc_csv":
                continue
            query = str(snapshot.context.get("query") or "").strip()
            page = str(
                snapshot.context.get("page")
                or snapshot.context.get("landing_page")
                or ""
            ).strip()
            family, match_kind = self._match_family(query, groups)
            record = {
                "query": query or None,
                "page": page or None,
                "impressions": snapshot.metrics.get("impressions"),
                "clicks": snapshot.metrics.get("clicks"),
                "ctr": snapshot.metrics.get("ctr"),
                "position": snapshot.metrics.get("position"),
                "period_start": snapshot.period_start,
                "period_end": snapshot.period_end,
                "device": snapshot.context.get("device"),
                "match_kind": match_kind,
                "snapshot_id": snapshot.id,
            }
            if family is None:
                unmatched_queries.append(record)
                continue
            bucket = buckets[family]
            bucket["queries"].append(record)
            impressions = float(snapshot.metrics.get("impressions") or 0)
            clicks = float(snapshot.metrics.get("clicks") or 0)
            bucket["impressions"] += impressions
            bucket["clicks"] += clicks
            position = snapshot.metrics.get("position")
            if position is not None:
                weight = impressions if impressions > 0 else 1.0
                bucket["position_weighted_sum"] += float(position) * weight
                bucket["position_weight"] += weight
            bucket["evidence_refs"].append(
                {
                    "kind": "owned_measurement",
                    "id": snapshot.id,
                    "source_sha256": snapshot.source_sha256,
                    "artifact_ref": snapshot.artifact_ref,
                }
            )

        unmatched_rankings: list[dict[str, Any]] = []
        for ranking in rankings:
            keyword = str(ranking.get("keyword") or ranking.get("query") or "").strip()
            family, match_kind = self._match_family(keyword, groups)
            observation = {
                "keyword": keyword,
                "position": ranking.get("organic_position", ranking.get("position")),
                "ranking_url": ranking.get("ranking_url") or ranking.get("url"),
                "device": ranking.get("device"),
                "snapshot_date": ranking.get("snapshot_date")
                or ranking.get("observed_at"),
                "match_kind": match_kind,
                "evidence_ref": ranking.get("evidence_ref"),
            }
            if family is None:
                unmatched_rankings.append(observation)
                continue
            buckets[family]["ranking_observations"].append(observation)
            if observation["evidence_ref"]:
                buckets[family]["evidence_refs"].append(
                    dict(observation["evidence_ref"])
                )

        aligned_groups: list[dict[str, Any]] = []
        for family in sorted(buckets):
            bucket = buckets[family]
            impressions = bucket.pop("impressions")
            clicks = bucket.pop("clicks")
            position_sum = bucket.pop("position_weighted_sum")
            position_weight = bucket.pop("position_weight")
            bucket["observed_search_console"] = {
                "impressions": self._clean_number(impressions),
                "clicks": self._clean_number(clicks),
                "ctr": round(clicks / impressions, 6) if impressions > 0 else None,
                "average_position": (
                    round(position_sum / position_weight, 3)
                    if position_weight > 0
                    else None
                ),
                "provenance_label": "observed",
            }
            bucket["evidence_refs"] = self._dedupe_refs(bucket["evidence_refs"])
            aligned_groups.append(bucket)

        matched_groups = sum(
            1
            for group in aligned_groups
            if group["queries"] or group["ranking_observations"]
        )
        total_groups = len(aligned_groups)
        completeness = (
            round(100 * matched_groups / total_groups, 2) if total_groups else 0.0
        )
        return {
            "contract_version": "demand-search-alignment.v1",
            "prospect_id": prospect_id,
            "vertical_id": vertical_id,
            "market": market,
            "status": (
                "complete"
                if completeness >= 85
                else "partial"
                if completeness >= 50
                else "limited"
            ),
            "completeness_percent": completeness,
            "brand_and_nonbrand_separate": True,
            "groups": aligned_groups,
            "unmatched_queries": unmatched_queries,
            "unmatched_rankings": unmatched_rankings,
            "limitations": [
                "Search Console metrics describe observed query occasions and clicks, not unique people."
            ]
            if snapshots
            else [
                "Owner Search Console evidence is unavailable; query demand remains unknown."
            ],
        }

    @staticmethod
    def _validate_demand_context(
        demand: DemandEvidenceSet,
        *,
        prospect_id: str,
        vertical_id: str,
        market: str,
    ) -> None:
        if demand.prospect_id != prospect_id:
            raise ValueError("demand evidence prospect does not match")
        if demand.vertical_id != vertical_id:
            raise ValueError("demand evidence vertical does not match")
        if demand.market.casefold().strip() != market.casefold().strip():
            raise ValueError("demand evidence market does not match")
        if demand.state != "approved":
            raise ValueError("search alignment requires approved demand evidence")

    @staticmethod
    def _validate_owner_context(
        snapshots: list[OwnedMeasurementSnapshot],
        *,
        prospect_id: str,
        vertical_id: str,
        market: str,
    ) -> None:
        for snapshot in snapshots:
            if snapshot.prospect_id != prospect_id:
                raise ValueError("owner measurement prospect does not match")
            if snapshot.vertical_id != vertical_id:
                raise ValueError("owner measurement vertical does not match")
            observed_market = str(
                snapshot.context.get("market")
                or snapshot.context.get("location")
                or ""
            ).strip()
            if observed_market and observed_market.casefold() != market.casefold().strip():
                raise ValueError("owner measurement market does not match")

    @classmethod
    def _group_terms(
        cls,
        demand: DemandEvidenceSet | None,
    ) -> dict[str, dict[str, Any]]:
        if demand is None:
            return {}
        rows_by_id = {
            str(row["id"]): row
            for row in demand.rows
            if isinstance(row, dict) and row.get("id")
        }
        groups: dict[str, dict[str, Any]] = {}
        for group in demand.groups:
            if not isinstance(group, dict) or group.get("status") != "approved":
                continue
            family = str(group.get("intent_family") or "").strip()
            if not family:
                continue
            terms = {
                cls._normalize(str(rows_by_id[row_id].get("keyword") or ""))
                for row_id in group.get("included_keyword_ids", [])
                if row_id in rows_by_id
            }
            representative = str(group.get("representative_term") or "").strip()
            if representative:
                terms.add(cls._normalize(representative))
            terms.discard("")
            groups[family] = {
                "representative_term": representative,
                "terms": terms,
                "is_brand": bool(group.get("is_brand")),
            }
        return groups

    @classmethod
    def _match_family(
        cls,
        query: str,
        groups: dict[str, dict[str, Any]],
    ) -> tuple[str | None, str]:
        normalized = cls._normalize(query)
        if not normalized:
            return None, "missing_query"
        exact = [
            family
            for family, payload in groups.items()
            if normalized in payload["terms"]
        ]
        if len(exact) == 1:
            return exact[0], "exact"
        query_tokens = set(_TOKEN_RE.findall(normalized))
        candidates: list[tuple[float, str]] = []
        for family, payload in groups.items():
            best = 0.0
            for term in payload["terms"]:
                term_tokens = set(_TOKEN_RE.findall(term))
                if not term_tokens or not query_tokens:
                    continue
                overlap = len(query_tokens & term_tokens) / len(
                    query_tokens | term_tokens
                )
                best = max(best, overlap)
            if best >= 0.8:
                candidates.append((best, family))
        candidates.sort(key=lambda item: (-item[0], item[1]))
        if not candidates:
            return None, "unmatched"
        if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
            return None, "ambiguous"
        return candidates[0][1], "close_variant"

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(_TOKEN_RE.findall(value.casefold()))

    @staticmethod
    def _clean_number(value: float) -> int | float:
        return int(value) if value.is_integer() else round(value, 6)

    @staticmethod
    def _dedupe_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique: dict[tuple[tuple[str, str], ...], dict[str, Any]] = {}
        for ref in refs:
            key = tuple(sorted((str(k), str(v)) for k, v in ref.items()))
            unique[key] = ref
        return list(unique.values())
