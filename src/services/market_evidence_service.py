"""Cost-bounded market SERP lifecycle isolated from target health scoring."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from typing import Any, Callable, Protocol
from urllib.parse import urlsplit

from src.models import (
    PROVIDER_CALL_CONTRACT_VERSION,
    InsightRun,
    KeywordSet,
    KeywordTarget,
    MarketEvidenceCompleteness,
    MarketEvidenceRun,
    ProviderCallRecord,
    new_id,
    utc_now_iso,
)
from src.repositories.base import InsightRepository
from src.services.keyword_set_service import KeywordSetService


class MarketProvider(Protocol):
    def collect_keyword_metrics(
        self,
        keywords: list[str],
        *,
        location_code: int,
        language_code: str,
    ) -> dict[str, Any]: ...

    def collect_organic_serp(
        self,
        keyword: str,
        *,
        location_code: int,
        language_code: str,
        device: str,
        depth: int = 100,
    ) -> dict[str, Any]: ...

    def collect_maps_serp(
        self,
        keyword: str,
        *,
        location_code: int,
        language_code: str,
        device: str,
        depth: int = 20,
    ) -> dict[str, Any]: ...


SOCIAL_DOMAINS = {
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "tiktok.com",
    "youtube.com",
    "x.com",
}
DIRECTORY_DOMAINS = {
    "bjjfanatics.com",
    "classpass.com",
    "expertise.com",
    "mapquest.com",
    "mindbodyonline.com",
    "reddit.com",
    "tripadvisor.com",
    "yelp.com",
    "yellowpages.com",
}
OWNED_DOMAINS = {
    "nationalbjjregistry.com",
    "nationalbjjregistry.org",
    "onetradenetwork.com",
}


class MarketEvidenceService:
    PILOT_CALL_CAP = 26
    COMPETITOR_AUTHORITY_CALL_CAP = 3
    DEEP_CALL_CAP = 40
    PREMIUM_WARNING_THRESHOLD_USD = 1.50
    KEYWORD_METRICS_CALL_CEILING_USD = 0.10
    SERP_CALL_CEILING_USD = 0.02
    HARD_STOP_FAILURES = {"authentication", "balance_payment"}

    def __init__(
        self,
        repository: InsightRepository,
        provider_factory: Callable[[], MarketProvider],
    ) -> None:
        self.repository = repository
        self.provider_factory = provider_factory
        self.keyword_service = KeywordSetService(repository)

    def search_visibility(
        self,
        market_run_id: str,
        demand_evidence: Any,
        *,
        context: dict[str, Any] | None = None,
    ) -> Any:
        """Attach an independent Search Visibility v2 snapshot to a market run."""

        from src.services.search_visibility_service import SearchVisibilityService

        market_run = self._require_market_run(market_run_id)
        result = SearchVisibilityService().build(
            demand_evidence,
            market_run.organic_evidence,
            market_run.target_domain,
            context=context,
            market_run=market_run,
        )
        market_run.artifact_refs.append({
            "kind": "search_visibility",
            "contract_version": result.version,
            "payload": result.to_dict(),
        })
        self.repository.save_market_evidence_run(market_run)
        return result

    def local_visibility_preflight(self, grid: Any, **kwargs: Any) -> dict[str, Any]:
        from src.services.local_visibility_service import LocalVisibilityService

        return LocalVisibilityService().preflight(grid, **kwargs)

    def local_visibility(
        self,
        market_run_id: str,
        grid: Any,
        *,
        keywords: list[str] | None = None,
        provider: MarketProvider | None = None,
        existing_evidence: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Collect a coordinate-bound local grid as a separate evidence surface."""

        from src.services.local_visibility_service import LocalVisibilityService

        market_run = self._require_market_run(market_run_id)
        result = LocalVisibilityService().collect(
            grid,
            provider or self.provider_factory(),
            keywords=keywords,
            existing_evidence=existing_evidence,
            market_run=market_run,
            device=kwargs.pop("device", market_run.device),
            language_code=kwargs.pop("language_code", market_run.language_code),
            **kwargs,
        )
        self.repository.save_market_evidence_run(market_run)
        return result

    @staticmethod
    def preflight(keyword_set: KeywordSet, *, phase: str) -> dict[str, Any]:
        approved = [target for target in keyword_set.targets() if target.review_status == "approved"]
        if phase == "pilot":
            pilot = KeywordSetService().select_pilot(keyword_set)
            return {
                "phase": "pilot",
                "keyword_metrics_calls": 1,
                "organic_calls": len(pilot),
                "maps_calls": len(pilot),
                "planned_calls": 1 + (2 * len(pilot)),
                "call_cap": MarketEvidenceService.PILOT_CALL_CAP,
                "keyword_count": len(pilot),
            }
        if phase != "deep":
            raise ValueError("phase must be pilot or deep")
        pilot_terms = {
            target.normalized_keyword
            for target in KeywordSetService().select_pilot(keyword_set)
        }
        remaining = [target for target in approved if target.normalized_keyword not in pilot_terms]
        local_remaining = [target for target in remaining if target.local_intent]
        return {
            "phase": "deep",
            "keyword_metrics_calls": 0,
            "organic_calls": len(remaining),
            "maps_calls": len(local_remaining),
            "planned_calls": len(remaining) + len(local_remaining),
            "call_cap": MarketEvidenceService.DEEP_CALL_CAP,
            "keyword_count": len(remaining),
        }

    @classmethod
    def paid_preflight(
        cls,
        keyword_set: KeywordSet,
        *,
        phase: str,
        provider_configured: bool,
        reusable_calls: int = 0,
        unresolved_calls: int = 0,
        retry_ceiling: int = 0,
    ) -> dict[str, Any]:
        """Cost/readiness layer without a network or billing-side effect."""

        base = cls.preflight(keyword_set, phase=phase)
        metrics_cost = (
            base["keyword_metrics_calls"] * cls.KEYWORD_METRICS_CALL_CEILING_USD
        )
        serp_cost = (
            (base["organic_calls"] + base["maps_calls"])
            * cls.SERP_CALL_CEILING_USD
        )
        ceiling = round(metrics_cost + serp_cost, 6)
        return {
            **base,
            "provider": "dataforseo",
            "provider_configured": bool(provider_configured),
            "account_readiness": (
                "configured_unverified"
                if provider_configured
                else "credentials_missing"
            ),
            "billing_readiness": "not_checked",
            "network_check_performed": False,
            "conservative_max_cost_usd": ceiling,
            "premium_warning_threshold_usd": cls.PREMIUM_WARNING_THRESHOLD_USD,
            "warning_threshold_exceeded": ceiling > cls.PREMIUM_WARNING_THRESHOLD_USD,
            "reusable_calls": max(0, int(reusable_calls)),
            "unresolved_calls": max(0, int(unresolved_calls)),
            "retry_ceiling": max(0, int(retry_ceiling)),
        }

    def start_pilot(
        self,
        *,
        insight_run_id: str,
        keyword_set_id: str,
        target_entity_name: str | None = None,
    ) -> MarketEvidenceRun:
        run = self._require_completed_run(insight_run_id)
        keyword_set = self._require_approved_keyword_set(keyword_set_id, run.requested_domain)
        pilot = self.keyword_service.select_pilot(keyword_set)
        preflight = self.preflight(keyword_set, phase="pilot")
        market_run = MarketEvidenceRun(
            insight_run_id=run.id,
            insight_attempt_id=run.attempt_id,
            keyword_set_id=keyword_set.id,
            keyword_set_version=keyword_set.keyword_set_key,
            target_domain=self._normalize_domain(run.requested_domain),
            target_entity_name=target_entity_name.strip() if target_entity_name else None,
            vertical_id=keyword_set.vertical_id,
            market=keyword_set.market,
            location_code=keyword_set.location_code,
            language_code=keyword_set.language_code,
            device=run.device or "desktop",
            provider_call_cap=self.PILOT_CALL_CAP,
            provider_contract_version=PROVIDER_CALL_CONTRACT_VERSION,
            provider_completeness=MarketEvidenceCompleteness(
                expected={
                    "keyword_metrics": 1,
                    "organic_serp": len(pilot),
                    "maps_serp": len(pilot),
                },
                successful={
                    "keyword_metrics": 0,
                    "organic_serp": 0,
                    "maps_serp": 0,
                },
                unresolved={
                    "keyword_metrics": 1,
                    "organic_serp": len(pilot),
                    "maps_serp": len(pilot),
                },
                inapplicable={
                    "keyword_metrics": 0,
                    "organic_serp": 0,
                    "maps_serp": 0,
                },
                reused={
                    "keyword_metrics": 0,
                    "organic_serp": 0,
                    "maps_serp": 0,
                },
            ).to_dict(),
            artifact_refs=[{"kind": "preflight", **preflight}],
        )
        self.repository.save_market_evidence_run(market_run)
        provider = self.provider_factory()

        metrics = self._provider_call(
            market_run,
            operation="keyword_metrics",
            query="50-keyword-batch",
            callback=lambda: provider.collect_keyword_metrics(
                [target.keyword for target in keyword_set.targets()],
                location_code=keyword_set.location_code,
                language_code=keyword_set.language_code,
            ),
        )
        if metrics is not None:
            market_run.keyword_metrics = [
                {
                    **item,
                    "source": metrics.get("source"),
                    "market": keyword_set.market,
                    "snapshot_date": metrics.get("snapshot_date"),
                    "raw_artifact_ref": metrics.get("raw_artifact_ref"),
                }
                for item in metrics.get("items", [])
                if isinstance(item, dict)
            ]
        if self._paid_queue_stopped(market_run):
            return self._finalize_collection(market_run)

        for target in pilot:
            organic = self._provider_call(
                market_run,
                operation="organic_serp",
                query=target.keyword,
                callback=lambda target=target: provider.collect_organic_serp(
                    target.keyword,
                    location_code=keyword_set.location_code,
                    language_code=keyword_set.language_code,
                    device=market_run.device,
                    depth=100,
                ),
            )
            if organic is not None:
                market_run.organic_evidence.append(
                    self._annotate_snapshot(organic, target, market_run, source_type="organic")
                )
            if self._paid_queue_stopped(market_run):
                break
            maps = self._provider_call(
                market_run,
                operation="maps_serp",
                query=target.keyword,
                callback=lambda target=target: provider.collect_maps_serp(
                    target.keyword,
                    location_code=keyword_set.location_code,
                    language_code=keyword_set.language_code,
                    device=market_run.device,
                    depth=20,
                ),
            )
            if maps is not None:
                market_run.maps_evidence.append(
                    self._annotate_snapshot(maps, target, market_run, source_type="maps")
                )
            if self._paid_queue_stopped(market_run):
                break

        market_run.competitor_candidates = self.derive_competitor_candidates(market_run)
        return self._finalize_collection(market_run)

    def approve_competitors(
        self,
        market_run_id: str,
        *,
        candidate_ids: list[str],
        operator: str,
    ) -> MarketEvidenceRun:
        market_run = self._require_market_run(market_run_id)
        if market_run.state != "needs_competitor_approval":
            raise ValueError("market evidence run is not waiting for competitor approval")
        if not operator.strip():
            raise ValueError("competitor approval requires an operator")
        unique_ids = list(dict.fromkeys(candidate_ids))
        if not 1 <= len(unique_ids) <= 3:
            raise ValueError("approve between one and three competitors")
        by_id = {str(candidate["candidate_id"]): candidate for candidate in market_run.competitor_candidates}
        if any(candidate_id not in by_id for candidate_id in unique_ids):
            raise ValueError("competitor approval must reference current direct-business candidates")
        now = utc_now_iso()
        market_run.approved_competitors = [
            {
                **by_id[candidate_id],
                "approval_set_version": 1,
                "approved_by": operator.strip(),
                "approved_at": now,
            }
            for candidate_id in unique_ids
        ]
        market_run.state = "enriching"
        market_run.updated_at = now
        return self.repository.save_market_evidence_run(market_run)

    def deepen(self, market_run_id: str) -> MarketEvidenceRun:
        market_run = self._require_market_run(market_run_id)
        if not market_run.approved_competitors:
            raise ValueError("deep collection requires an approved competitor set")
        if market_run.phase == "deep":
            return market_run
        keyword_set = self._require_approved_keyword_set(
            market_run.keyword_set_id,
            market_run.target_domain,
        )
        preflight = self.preflight(keyword_set, phase="deep")
        if preflight["planned_calls"] > self.DEEP_CALL_CAP:
            raise ValueError("deep collection preflight exceeds the 40-call cap")
        pilot_terms = {
            target.normalized_keyword
            for target in self.keyword_service.select_pilot(keyword_set)
        }
        remaining = [
            target
            for target in keyword_set.targets()
            if target.review_status == "approved" and target.normalized_keyword not in pilot_terms
        ]
        now = utc_now_iso()
        deep_run = replace(
            market_run,
            id=new_id(),
            state="enriching",
            phase="deep",
            provider_call_cap=len(market_run.provider_calls) + self.DEEP_CALL_CAP,
            provider_contract_version=PROVIDER_CALL_CONTRACT_VERSION,
            provider_completeness=self._extend_completeness(
                market_run,
                {
                    "organic_serp_deep": len(remaining),
                    "maps_serp_deep": len(
                        [target for target in remaining if target.local_intent]
                    ),
                },
            ),
            predecessor_market_run_id=market_run.id,
            artifact_refs=[
                *market_run.artifact_refs,
                {"kind": "supersedes_market_run", "market_run_id": market_run.id},
                {"kind": "preflight", **preflight},
            ],
            created_at=now,
            updated_at=now,
            completed_at=None,
        )
        market_run.state = "superseded"
        market_run.completed_at = now
        market_run.updated_at = now
        self.repository.save_market_evidence_run(market_run)
        self.repository.save_market_evidence_run(deep_run)
        provider = self.provider_factory()
        for target in remaining:
            organic = self._provider_call(
                deep_run,
                operation="organic_serp_deep",
                query=target.keyword,
                callback=lambda target=target: provider.collect_organic_serp(
                    target.keyword,
                    location_code=keyword_set.location_code,
                    language_code=keyword_set.language_code,
                    device=deep_run.device,
                    depth=100,
                ),
            )
            if organic is not None:
                deep_run.organic_evidence.append(
                    self._annotate_snapshot(organic, target, deep_run, source_type="organic")
                )
            if self._paid_queue_stopped(deep_run):
                break
            if target.local_intent:
                maps = self._provider_call(
                    deep_run,
                    operation="maps_serp_deep",
                    query=target.keyword,
                    callback=lambda target=target: provider.collect_maps_serp(
                        target.keyword,
                        location_code=keyword_set.location_code,
                        language_code=keyword_set.language_code,
                        device=deep_run.device,
                        depth=20,
                    ),
                )
                if maps is not None:
                    deep_run.maps_evidence.append(
                        self._annotate_snapshot(maps, target, deep_run, source_type="maps")
                    )
                if self._paid_queue_stopped(deep_run):
                    break
        deep_run.competitor_candidates = self.derive_competitor_candidates(deep_run)
        completeness = self._refresh_completeness(deep_run)
        if not completeness.is_complete:
            deep_run.state = "partial"
        else:
            deep_run.state = "complete" if deep_run.competitor_evidence else "enriching"
        deep_run.updated_at = utc_now_iso()
        if deep_run.state == "complete":
            deep_run.completed_at = utc_now_iso()
        return self.repository.save_market_evidence_run(deep_run)

    def resume_unresolved(
        self,
        market_run_id: str,
        *,
        account_recovered: bool = False,
    ) -> MarketEvidenceRun:
        """Create a successor and retry only unresolved eligible provider work."""

        predecessor = self._require_market_run(market_run_id)
        completeness = self._refresh_completeness(predecessor)
        if completeness.is_complete:
            raise ValueError("market evidence has no unresolved required work")
        keyword_set = self._require_approved_keyword_set(
            predecessor.keyword_set_id,
            predecessor.target_domain,
        )
        unresolved = [
            call
            for call in predecessor.provider_calls
            if self._call_is_unresolved(call)
        ]
        eligible = [
            call
            for call in unresolved
            if bool(call.get("retryable"))
            or (
                account_recovered
                and call.get("failure_class") in self.HARD_STOP_FAILURES
            )
        ]
        if not eligible:
            raise ValueError(
                "no unresolved calls are eligible; confirm provider account recovery or correct the request"
            )
        eligible_keys = {
            (
                str(call.get("operation") or ""),
                str(call.get("query_target") or call.get("query") or ""),
            )
            for call in eligible
        }

        now = utc_now_iso()
        reused_calls = [
            ProviderCallRecord(
                provider=str(call.get("provider") or "dataforseo"),
                operation=str(call.get("operation") or "unknown"),
                query_target=str(call.get("query_target") or call.get("query") or "unknown"),
                context=dict(call.get("context") or self._call_context(predecessor)),
                status="reused",
                predecessor_call_id=str(call.get("id") or ""),
                raw_artifact_ref=call.get("raw_artifact_ref"),
                completed_at=now,
            ).to_dict()
            for call in predecessor.provider_calls
            if self._call_is_success(call) and call.get("id")
        ]
        successor = replace(
            predecessor,
            id=new_id(),
            state="collecting",
            provider_call_cap=len(reused_calls) + len(eligible),
            provider_calls=reused_calls,
            actual_provider_cost=0.0,
            provider_contract_version=PROVIDER_CALL_CONTRACT_VERSION,
            provider_completeness=self._resume_completeness(
                completeness,
                reused_calls,
            ),
            evidence_limits=[
                item
                for item in predecessor.evidence_limits
                if (
                    str(item.get("operation") or ""),
                    str(item.get("query") or ""),
                )
                not in eligible_keys
            ],
            predecessor_market_run_id=predecessor.id,
            recovery_operation="resume_unresolved",
            artifact_refs=[
                *predecessor.artifact_refs,
                {
                    "kind": "resume_unresolved",
                    "predecessor_market_run_id": predecessor.id,
                    "reusable_calls": len(reused_calls),
                    "unresolved_calls": len(unresolved),
                    "retry_ceiling": len(eligible),
                    "account_recovered": bool(account_recovered),
                },
            ],
            created_at=now,
            updated_at=now,
            completed_at=None,
        )
        self.repository.save_market_evidence_run(successor)
        provider = self.provider_factory()
        targets = {
            target.normalized_keyword: target
            for target in keyword_set.targets()
        }
        for prior in eligible:
            operation = str(prior.get("operation") or "")
            query = str(prior.get("query_target") or prior.get("query") or "")
            callback = self._resume_callback(
                provider,
                operation=operation,
                query=query,
                keyword_set=keyword_set,
                market_run=successor,
            )
            payload = self._provider_call(
                successor,
                operation=operation,
                query=query,
                callback=callback,
                predecessor_call_id=str(prior.get("id") or "") or None,
                attempt=int(prior.get("attempt") or 1) + 1,
            )
            if payload is not None and operation == "keyword_metrics":
                successor.keyword_metrics = [
                    {
                        **item,
                        "source": payload.get("source"),
                        "market": keyword_set.market,
                        "snapshot_date": payload.get("snapshot_date"),
                        "raw_artifact_ref": payload.get("raw_artifact_ref"),
                    }
                    for item in payload.get("items", [])
                    if isinstance(item, dict)
                ]
            elif payload is not None and "organic_serp" in operation:
                target = targets.get(" ".join(query.casefold().split()))
                if target is not None:
                    successor.organic_evidence = self._replace_snapshot(
                        successor.organic_evidence,
                        self._annotate_snapshot(
                            payload,
                            target,
                            successor,
                            source_type="organic",
                        ),
                    )
            elif payload is not None and "maps_serp" in operation:
                target = targets.get(" ".join(query.casefold().split()))
                if target is not None:
                    successor.maps_evidence = self._replace_snapshot(
                        successor.maps_evidence,
                        self._annotate_snapshot(
                            payload,
                            target,
                            successor,
                            source_type="maps",
                        ),
                    )
            if self._paid_queue_stopped(successor):
                break

        successor.competitor_candidates = self.derive_competitor_candidates(successor)
        if successor.competitor_evidence:
            self._rebuild_comparative_evidence(successor)
        finalized = self._finalize_collection(
            successor,
            preserve_enriched=bool(successor.competitor_evidence),
        )
        if finalized.competitor_evidence:
            from src.services.market_reporting_service import MarketReportingService

            MarketReportingService(self.repository).assemble(finalized.id)
        return finalized

    @classmethod
    def derive_competitor_candidates(cls, market_run: MarketEvidenceRun) -> list[dict[str, Any]]:
        identities: dict[str, dict[str, Any]] = {}
        target_domain = cls._normalize_domain(market_run.target_domain)
        target_name = " ".join((market_run.target_entity_name or "").casefold().split())
        excluded_landscape: list[dict[str, Any]] = []

        for source_type, snapshots, weight in (
            ("organic", market_run.organic_evidence, 1.0),
            ("maps", market_run.maps_evidence, 1.5),
        ):
            for snapshot in snapshots:
                keyword = str(snapshot.get("keyword") or "")
                for result in snapshot.get("results", []):
                    if not isinstance(result, dict):
                        continue
                    url = str(result.get("url") or result.get("website") or "")
                    domain = cls._normalize_domain(url)
                    place_id = str(result.get("place_id") or "")
                    title = " ".join(str(result.get("title") or "").casefold().split())
                    rank_value = result.get("rank")
                    rank = int(rank_value) if isinstance(rank_value, int | float) and not isinstance(rank_value, bool) else None
                    if domain == target_domain or (
                        target_name and title and (title == target_name or target_name in title)
                    ):
                        excluded_landscape.append({"reason": "target", "keyword": keyword, "result": result})
                        continue
                    exclusion = cls._domain_exclusion(domain)
                    if exclusion:
                        excluded_landscape.append({"reason": exclusion, "keyword": keyword, "result": result})
                        continue
                    if not domain and not place_id:
                        excluded_landscape.append({"reason": "missing_identity", "keyword": keyword, "result": result})
                        continue
                    key = domain or f"place:{place_id}"
                    candidate = identities.setdefault(key, {
                        "candidate_id": key,
                        "domain": domain or None,
                        "place_ids": [],
                        "name": result.get("title"),
                        "appearances": 0,
                        "organic_appearances": 0,
                        "maps_appearances": 0,
                        "reciprocal_position_score": 0.0,
                        "observations": [],
                    })
                    if place_id and place_id not in candidate["place_ids"]:
                        candidate["place_ids"].append(place_id)
                    candidate["appearances"] += 1
                    candidate[f"{source_type}_appearances"] += 1
                    candidate["reciprocal_position_score"] += weight / max(rank or 100, 1)
                    candidate["observations"].append({
                        "keyword": keyword,
                        "source_type": source_type,
                        "rank": rank,
                        "url": result.get("url") or result.get("website"),
                        "raw_artifact_ref": snapshot.get("raw_artifact_ref"),
                    })

        market_run.artifact_refs = [
            ref for ref in market_run.artifact_refs if ref.get("kind") != "excluded_serp_landscape"
        ]
        if excluded_landscape:
            market_run.artifact_refs.append({
                "kind": "excluded_serp_landscape",
                "count": len(excluded_landscape),
                "items": excluded_landscape[:100],
            })
        candidates = list(identities.values())
        for candidate in candidates:
            candidate["reciprocal_position_score"] = round(candidate["reciprocal_position_score"], 6)
        candidates.sort(
            key=lambda item: (
                -int(item["appearances"]),
                -float(item["reciprocal_position_score"]),
                str(item.get("domain") or item.get("name") or ""),
            )
        )
        return candidates[:10]

    def _provider_call(
        self,
        market_run: MarketEvidenceRun,
        *,
        operation: str,
        query: str,
        callback: Callable[[], dict[str, Any]],
        predecessor_call_id: str | None = None,
        attempt: int = 1,
    ) -> dict[str, Any] | None:
        if len(market_run.provider_calls) >= market_run.provider_call_cap:
            raise ValueError("market evidence provider call cap exceeded")
        started_at = utc_now_iso()
        context = self._call_context(market_run)
        try:
            payload = callback()
        except Exception as exc:
            failure_class, retryable = self._classify_exception(exc)
            record = ProviderCallRecord(
                provider="dataforseo",
                operation=operation,
                query_target=query,
                context=context,
                status="failed",
                attempt=attempt,
                failure_class=failure_class,
                retryable=retryable,
                predecessor_call_id=predecessor_call_id,
                started_at=started_at,
                completed_at=utc_now_iso(),
            ).to_dict()
            record["query"] = query
            record["error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
            record["snapshot_date"] = date.today().isoformat()
            market_run.provider_calls.append(record)
            market_run.evidence_limits.append({
                "kind": "provider_failure",
                "operation": operation,
                "query": query,
                "failure_class": failure_class,
                "retryable": retryable,
                "message": f"{type(exc).__name__}: {str(exc)[:240]}",
            })
            self._refresh_completeness(market_run)
            return None
        cost = self._safe_cost(payload.get("provider_cost_usd"))
        market_run.actual_provider_cost = round(market_run.actual_provider_cost + cost, 6)
        failure: tuple[str, bool] | None = None
        evidence_limit_kind = "provider_task_unknown"
        if payload.get("status") != "complete":
            failure = self._classify_payload_failure(payload)
        elif operation == "keyword_metrics" and not [
            item for item in payload.get("items", []) if isinstance(item, dict)
        ]:
            failure = ("task_level", True)
            evidence_limit_kind = "empty_keyword_metrics"
        if failure is not None:
            failure_class, retryable = failure
            status = "failed"
        else:
            failure_class, retryable = None, False
            status = "success"
        record = ProviderCallRecord(
            provider="dataforseo",
            operation=operation,
            query_target=query,
            context=context,
            status=status,
            attempt=attempt,
            failure_class=failure_class,
            retryable=retryable,
            actual_cost=cost,
            raw_artifact_ref=payload.get("raw_artifact_ref"),
            predecessor_call_id=predecessor_call_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
        ).to_dict()
        record["query"] = query
        record["snapshot_date"] = (
            payload.get("snapshot_date") or date.today().isoformat()
        )
        market_run.provider_calls.append(record)
        if failure is not None:
            market_run.evidence_limits.append({
                "kind": evidence_limit_kind,
                "operation": operation,
                "query": query,
                "failure_class": failure_class,
                "retryable": retryable,
                "provider_error": payload.get("provider_error"),
                "raw_artifact_ref": payload.get("raw_artifact_ref"),
                "message": (
                    "The paid keyword-volume task returned no usable rows; "
                    "demand remains unknown."
                    if evidence_limit_kind == "empty_keyword_metrics"
                    else "The provider task did not return conclusive evidence."
                ),
            })
            self._refresh_completeness(market_run)
            return None
        self._refresh_completeness(market_run)
        return payload

    def _finalize_collection(
        self,
        market_run: MarketEvidenceRun,
        *,
        preserve_enriched: bool = False,
    ) -> MarketEvidenceRun:
        completeness = self._refresh_completeness(market_run)
        successful_market = len(market_run.organic_evidence) + len(
            market_run.maps_evidence
        )
        if not completeness.is_complete:
            market_run.state = "partial"
            if successful_market == 0:
                market_run.evidence_limits.append(
                    {
                        "kind": "provider_collection_failed",
                        "message": (
                            "No usable organic or Maps snapshots were returned; "
                            "market evidence remains unknown."
                        ),
                    }
                )
        elif preserve_enriched:
            market_run.state = "complete"
        elif market_run.competitor_candidates:
            market_run.state = "needs_competitor_approval"
        else:
            market_run.state = "partial"
            market_run.evidence_limits.append(
                {
                    "kind": "no_direct_competitor_candidates",
                    "message": (
                        "The bounded SERP sample produced no eligible "
                        "direct-business competitor candidates."
                    ),
                }
            )
        market_run.evidence_limits = self._dedupe_evidence_limits(
            market_run.evidence_limits
        )
        market_run.updated_at = utc_now_iso()
        if market_run.state in {"complete", "partial", "failed"}:
            market_run.completed_at = market_run.completed_at or utc_now_iso()
        return self.repository.save_market_evidence_run(market_run)

    def _refresh_completeness(
        self,
        market_run: MarketEvidenceRun,
    ) -> MarketEvidenceCompleteness:
        if market_run.provider_completeness:
            prior = MarketEvidenceCompleteness(**market_run.provider_completeness)
            expected = dict(prior.expected)
        else:
            expected: dict[str, int] = {}
            for call in market_run.provider_calls:
                operation = str(call.get("operation") or "unknown")
                expected[operation] = expected.get(operation, 0) + 1
        successful = {operation: 0 for operation in expected}
        inapplicable = {operation: 0 for operation in expected}
        reused = {operation: 0 for operation in expected}
        for call in market_run.provider_calls:
            operation = str(call.get("operation") or "unknown")
            if operation not in expected:
                expected[operation] = expected.get(operation, 0) + 1
                successful[operation] = 0
                inapplicable[operation] = 0
                reused[operation] = 0
            if self._call_is_success(call):
                successful[operation] += 1
                if call.get("status") == "reused":
                    reused[operation] += 1
            elif call.get("status") == "inapplicable":
                inapplicable[operation] += 1
        unresolved = {
            operation: max(
                0,
                expected_count
                - successful.get(operation, 0)
                - inapplicable.get(operation, 0),
            )
            for operation, expected_count in expected.items()
        }
        completeness = MarketEvidenceCompleteness(
            expected=expected,
            successful=successful,
            unresolved=unresolved,
            inapplicable=inapplicable,
            reused=reused,
        )
        market_run.provider_completeness = completeness.to_dict()
        return completeness

    @staticmethod
    def _extend_completeness(
        market_run: MarketEvidenceRun,
        additions: dict[str, int],
    ) -> dict[str, Any]:
        if market_run.provider_completeness:
            current = MarketEvidenceCompleteness(**market_run.provider_completeness)
            expected = dict(current.expected)
            successful = dict(current.successful)
            unresolved = dict(current.unresolved)
            inapplicable = dict(current.inapplicable)
            reused = dict(current.reused)
        else:
            expected = {}
            successful = {}
            unresolved = {}
            inapplicable = {}
            reused = {}
        for operation, count in additions.items():
            expected[operation] = expected.get(operation, 0) + count
            successful.setdefault(operation, 0)
            unresolved[operation] = unresolved.get(operation, 0) + count
            inapplicable.setdefault(operation, 0)
            reused.setdefault(operation, 0)
        return MarketEvidenceCompleteness(
            expected=expected,
            successful=successful,
            unresolved=unresolved,
            inapplicable=inapplicable,
            reused=reused,
        ).to_dict()

    @staticmethod
    def _resume_completeness(
        predecessor: MarketEvidenceCompleteness,
        reused_calls: list[dict[str, Any]],
    ) -> dict[str, Any]:
        successful = {operation: 0 for operation in predecessor.expected}
        reused = {operation: 0 for operation in predecessor.expected}
        for call in reused_calls:
            operation = str(call.get("operation") or "unknown")
            successful[operation] = successful.get(operation, 0) + 1
            reused[operation] = reused.get(operation, 0) + 1
        unresolved = {
            operation: max(
                0,
                count
                - successful.get(operation, 0)
                - predecessor.inapplicable.get(operation, 0),
            )
            for operation, count in predecessor.expected.items()
        }
        return MarketEvidenceCompleteness(
            expected=dict(predecessor.expected),
            successful=successful,
            unresolved=unresolved,
            inapplicable=dict(predecessor.inapplicable),
            reused=reused,
        ).to_dict()

    @classmethod
    def _paid_queue_stopped(cls, market_run: MarketEvidenceRun) -> bool:
        if not market_run.provider_calls:
            return False
        return (
            market_run.provider_calls[-1].get("failure_class")
            in cls.HARD_STOP_FAILURES
        )

    @staticmethod
    def _call_is_success(call: dict[str, Any]) -> bool:
        return call.get("status") in {"success", "reused", "complete", "completed"}

    @classmethod
    def _call_is_unresolved(cls, call: dict[str, Any]) -> bool:
        return not cls._call_is_success(call) and call.get("status") != "inapplicable"

    @staticmethod
    def _call_context(market_run: MarketEvidenceRun) -> dict[str, Any]:
        return {
            "market": market_run.market,
            "location_code": market_run.location_code,
            "language_code": market_run.language_code,
            "device": market_run.device,
            "target_domain": market_run.target_domain,
        }

    @classmethod
    def _classify_exception(cls, exc: Exception) -> tuple[str, bool]:
        status = getattr(exc, "http_status", None)
        text = f"{type(exc).__name__} {exc}".casefold()
        if status in {401, 403} or "authentication" in text or "unauthorized" in text:
            return "authentication", False
        if status == 402 or any(
            token in text
            for token in ("payment required", "insufficient balance", "account balance")
        ):
            return "balance_payment", False
        if status == 429 or "quota" in text or "rate limit" in text:
            return "quota", True
        if isinstance(exc, (ValueError, TypeError)):
            return "invalid_request", False
        if status is not None and status >= 500:
            return "transient", True
        if any(token in text for token in ("timeout", "temporar", "connection", "urlerror")):
            return "transient", True
        return "unknown", True

    @classmethod
    def _classify_payload_failure(
        cls,
        payload: dict[str, Any],
    ) -> tuple[str, bool]:
        error = payload.get("provider_error")
        error = error if isinstance(error, dict) else {}
        code = error.get("status_code")
        message = str(error.get("status_message") or "").casefold()
        if code in {401, 403} or "authentication" in message:
            return "authentication", False
        if code == 402 or any(
            token in message
            for token in ("payment", "balance", "not enough money")
        ):
            return "balance_payment", False
        if code == 429 or "quota" in message or "rate limit" in message:
            return "quota", True
        if isinstance(code, int) and 40000 <= code < 40100:
            return "invalid_request", False
        if code is not None:
            return "task_level", True
        return "unknown", True

    def _resume_callback(
        self,
        provider: MarketProvider,
        *,
        operation: str,
        query: str,
        keyword_set: KeywordSet,
        market_run: MarketEvidenceRun,
    ) -> Callable[[], dict[str, Any]]:
        if operation == "keyword_metrics":
            return lambda: provider.collect_keyword_metrics(
                [target.keyword for target in keyword_set.targets()],
                location_code=keyword_set.location_code,
                language_code=keyword_set.language_code,
            )
        if "organic_serp" in operation:
            return lambda: provider.collect_organic_serp(
                query,
                location_code=keyword_set.location_code,
                language_code=keyword_set.language_code,
                device=market_run.device,
                depth=100,
            )
        if "maps_serp" in operation:
            return lambda: provider.collect_maps_serp(
                query,
                location_code=keyword_set.location_code,
                language_code=keyword_set.language_code,
                device=market_run.device,
                depth=20,
            )
        raise ValueError(f"unsupported resumable provider operation: {operation}")

    @staticmethod
    def _replace_snapshot(
        snapshots: list[dict[str, Any]],
        replacement: dict[str, Any],
    ) -> list[dict[str, Any]]:
        normalized = " ".join(str(replacement.get("keyword") or "").casefold().split())
        output = [
            item
            for item in snapshots
            if " ".join(str(item.get("keyword") or "").casefold().split())
            != normalized
        ]
        output.append(replacement)
        return output

    def _rebuild_comparative_evidence(
        self,
        market_run: MarketEvidenceRun,
    ) -> None:
        from src.services.gap_analysis_service import GapAnalysisService

        seo_report = self.repository.get_report(market_run.insight_run_id, "v2")
        authority = (
            seo_report.report_payload.get("offsite_authority")
            if seo_report is not None
            and isinstance(seo_report.report_payload, dict)
            else None
        )
        matrix, recommendations, limitations = GapAnalysisService().analyze(
            market_run,
            target_pages=self.repository.list_page_records(
                market_run.insight_run_id
            ),
            target_authority=authority if isinstance(authority, dict) else None,
        )
        market_run.gap_matrix = matrix
        market_run.recommended_gaps = recommendations
        market_run.evidence_limits = [
            *market_run.evidence_limits,
            *limitations,
        ]

    @staticmethod
    def _dedupe_evidence_limits(
        limits: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for item in limits:
            key = (
                str(item.get("kind") or ""),
                str(item.get("operation") or ""),
                str(item.get("query") or ""),
            )
            if key not in seen:
                seen.add(key)
                output.append(item)
        return output

    @classmethod
    def _annotate_snapshot(
        cls,
        snapshot: dict[str, Any],
        target: KeywordTarget,
        market_run: MarketEvidenceRun,
        *,
        source_type: str,
    ) -> dict[str, Any]:
        results = snapshot.get("results") if isinstance(snapshot.get("results"), list) else []
        target_results = [
            result for result in results
            if isinstance(result, dict) and cls._is_target_result(result, market_run)
        ]
        target_result = min(
            target_results,
            key=lambda result: int(result.get("rank") or 10_000),
            default=None,
        )
        return {
            **snapshot,
            "category": target.category,
            "search_intent": target.search_intent,
            "optimization_focus": target.optimization_focus,
            "target_page_usage": target.target_page_usage,
            "local_intent": target.local_intent,
            "source_type": source_type,
            "target_rank": target_result.get("rank") if target_result else None,
            "target_url": (
                target_result.get("url") or target_result.get("website")
                if target_result else None
            ),
        }

    @classmethod
    def _is_target_result(cls, result: dict[str, Any], market_run: MarketEvidenceRun) -> bool:
        domain = cls._normalize_domain(str(result.get("url") or result.get("website") or ""))
        if domain and domain == cls._normalize_domain(market_run.target_domain):
            return True
        target_name = " ".join((market_run.target_entity_name or "").casefold().split())
        title = " ".join(str(result.get("title") or "").casefold().split())
        return bool(target_name and title and (title == target_name or target_name in title))

    @classmethod
    def _domain_exclusion(cls, domain: str) -> str | None:
        if not domain:
            return None
        if any(domain == item or domain.endswith(f".{item}") for item in SOCIAL_DOMAINS):
            return "social_network"
        if any(domain == item or domain.endswith(f".{item}") for item in DIRECTORY_DOMAINS):
            return "directory_or_aggregator"
        if any(domain == item or domain.endswith(f".{item}") for item in OWNED_DOMAINS):
            return "owned_property"
        return None

    def _require_completed_run(self, run_id: str) -> InsightRun:
        run = self.repository.get_run(run_id)
        if run is None:
            raise ValueError(f"insight run not found: {run_id}")
        if run.status != "completed":
            raise ValueError("market evidence requires a completed core insight run")
        return run

    def _require_approved_keyword_set(self, keyword_set_id: str, domain: str) -> KeywordSet:
        keyword_set = self.repository.get_keyword_set(keyword_set_id)
        if keyword_set is None:
            raise ValueError(f"keyword set not found: {keyword_set_id}")
        if keyword_set.state != "approved":
            raise ValueError("market evidence requires an approved keyword set")
        normalized_domain = self._normalize_domain(domain)
        direct_match = (
            keyword_set.normalized_domain
            and self._normalize_domain(keyword_set.normalized_domain) == normalized_domain
        )
        binding_match = bool(
            self.repository.list_keyword_set_bindings(
                keyword_set_id=keyword_set.id,
                normalized_domain=normalized_domain,
                state="active",
                limit=1,
            )
        )
        if keyword_set.normalized_domain and not direct_match and not binding_match:
            raise ValueError("keyword set is bound to a different target domain")
        if not keyword_set.normalized_domain and not binding_match:
            raise ValueError("keyword set is not bound to the target domain")
        return keyword_set

    def _require_market_run(self, market_run_id: str) -> MarketEvidenceRun:
        market_run = self.repository.get_market_evidence_run(market_run_id)
        if market_run is None:
            raise ValueError(f"market evidence run not found: {market_run_id}")
        return market_run

    @staticmethod
    def _normalize_domain(value: str) -> str:
        candidate = value.strip().casefold().rstrip(".")
        if "://" in candidate:
            candidate = (urlsplit(candidate).hostname or "").casefold().rstrip(".")
        return candidate.removeprefix("www.")

    @staticmethod
    def _safe_cost(value: Any) -> float:
        if isinstance(value, bool) or not isinstance(value, int | float):
            return 0.0
        return max(0.0, float(value))
