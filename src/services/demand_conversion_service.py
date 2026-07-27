"""Deterministic, provenance-bearing demand-to-conversion evidence modeling."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable

from src.models import (
    DEMAND_CONVERSION_FORMULA_VERSION,
    DEMAND_CONVERSION_SOURCE_CLASSES,
    BusinessEconomicsProfile,
    ConversionEventMap,
    DemandConversionEvidence,
    DemandEvidenceSet,
    DemandTrendSnapshot,
    OwnedMeasurementSnapshot,
    canonical_sha256,
    new_id,
    utc_now_iso,
)
from src.repositories.base import InsightRepository
from src.services.owned_measurement_service import OwnedMeasurementService


FORECAST_WARNING = (
    "Modeled outcomes are scenarios, not causal findings, ranking promises, "
    "or revenue guarantees."
)


class DemandConversionService:
    """Build immutable prospect or owner-verified commercial evidence."""

    def __init__(self, repository: InsightRepository | None = None) -> None:
        self.repository = repository

    def build(
        self,
        *,
        insight_run_id: str,
        prospect_id: str,
        vertical_id: str,
        market: str,
        mode: str = "prospect",
        demand: DemandEvidenceSet | None = None,
        economics: BusinessEconomicsProfile | None = None,
        owner_snapshots: Iterable[OwnedMeasurementSnapshot] = (),
        trend_snapshots: Iterable[DemandTrendSnapshot] = (),
        event_map: ConversionEventMap | None = None,
        search_alignment: dict[str, Any] | None = None,
        public_sources: Iterable[dict[str, Any]] = (),
        assumptions: dict[str, dict[str, float | int | None]] | None = None,
        target_id: str | None = None,
        normalized_domain: str | None = None,
        attempt_id: str | None = None,
    ) -> DemandConversionEvidence:
        if mode not in {"prospect", "owner_verified"}:
            raise ValueError(f"unsupported demand conversion mode: {mode}")
        owner_records = list(owner_snapshots)
        trend_records = list(trend_snapshots)
        public_records = [dict(source) for source in public_sources]
        self._validate_inputs(
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            market=market,
            mode=mode,
            demand=demand,
            economics=economics,
            owner_snapshots=owner_records,
            trend_snapshots=trend_records,
            event_map=event_map,
        )
        assumption_bands = self._normalize_assumptions(assumptions or {})
        baseline = (
            OwnedMeasurementService().derive_funnel_baseline(
                owner_records,
                prospect_id=prospect_id,
                vertical_id=vertical_id,
            )
            if owner_records
            else {}
        )
        intent_groups = self._intent_groups(demand, trend_records)
        nonbrand_search_occasions = sum(
            float(group["monthly_search_occasions"])
            for group in intent_groups
            if not group["is_brand"]
            and group["monthly_search_occasions"] is not None
        )
        outputs, scenario_assumptions = self._model_outputs(
            assumption_bands=assumption_bands,
            baseline=baseline,
            nonbrand_search_occasions=nonbrand_search_occasions,
            economics=economics,
            mode=mode,
        )
        sources = self._source_snapshots(
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            market=market,
            demand=demand,
            economics=economics,
            owner_snapshots=owner_records,
            trend_snapshots=trend_records,
            public_sources=public_records,
            modeled=bool(outputs),
            assumptions=scenario_assumptions,
        )
        completeness, checks = self._completeness(
            mode=mode,
            demand=demand,
            economics=economics,
            owner_snapshots=owner_records,
            trend_snapshots=trend_records,
            event_map=event_map,
            search_alignment=search_alignment,
            assumptions=scenario_assumptions,
        )
        status = (
            "complete"
            if completeness >= 85
            else "partial"
            if completeness >= 50
            else "limited"
        )
        warnings = [FORECAST_WARNING]
        if demand is None:
            warnings.append(
                "Approved demand evidence is unavailable; acquisition projections are suppressed."
            )
        else:
            warnings.append(
                "Keyword volume represents monthly search occasions, not unique people."
            )
        if mode == "prospect":
            warnings.append(
                "Prospect mode uses public, supplied, and assumed evidence only."
            )
        if mode == "owner_verified" and any(
            scenario_assumptions[band].get(key, {}).get("provenance_label")
            == "assumed"
            for band in scenario_assumptions
            for key in ("lead_rate", "booking_rate", "close_rate")
        ):
            warnings.append(
                "One or more funnel rates remain assumed because the owner aggregate was incomplete."
            )
        evidence_refs = self._evidence_refs(
            demand=demand,
            economics=economics,
            owner_snapshots=owner_records,
            trend_snapshots=trend_records,
            event_map=event_map,
            search_alignment=search_alignment,
            public_sources=public_records,
        )
        observed_inputs = {
            "funnel_baseline": baseline or {
                "status": "unknown",
                "reason": "Owner-authorized aggregate measurements are unavailable.",
            },
            "search_alignment": search_alignment
            or {
                "status": "unknown",
                "reason": "Context-matched search evidence is unavailable.",
            },
            "demand": {
                "monthly_search_occasions_nonbrand": self._round(
                    nonbrand_search_occasions
                )
                if demand is not None
                else None,
                "semantics": "search occasions, never unique people",
                "provenance_label": "supplied" if demand is not None else "unknown",
            },
            "completeness_checks": checks,
        }
        economics_payload = (
            {
                "profile_id": economics.id,
                "profile_version": economics.version,
                "monthly_price": economics.monthly_price,
                "currency": economics.currency,
                "state": economics.state,
                "field_provenance": economics.field_provenance,
                "provenance_label": "supplied",
            }
            if economics is not None
            else {
                "status": "unknown",
                "provenance_label": "assumed",
            }
        )
        capacity_payload = (
            {
                "available_customers": economics.capacity_headroom,
                "capacity_mrr": economics.capacity_mrr,
                "capacity_annual_run_rate": economics.capacity_annual_run_rate,
                "provenance_label": "supplied",
            }
            if economics is not None
            else {
                "available_customers": None,
                "provenance_label": "assumed",
            }
        )
        record = DemandConversionEvidence(
            insight_run_id=insight_run_id,
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            mode=mode,
            market=market,
            target_id=target_id,
            normalized_domain=normalized_domain,
            attempt_id=attempt_id,
            source_snapshots=sources,
            intent_groups=intent_groups,
            observed_inputs=observed_inputs,
            modeled_outputs=outputs,
            economics=economics_payload,
            capacity=capacity_payload,
            completeness_percent=completeness,
            status=status,
            assumptions=self._assumption_rows(scenario_assumptions),
            warnings=warnings,
            evidence_refs=evidence_refs,
        )
        if self.repository is not None:
            saver = getattr(self.repository, "save_demand_conversion_evidence", None)
            if not callable(saver):
                raise ValueError(
                    "repository does not support demand conversion evidence"
                )
            return saver(record)
        return record

    def approve(
        self,
        evidence: DemandConversionEvidence | str,
        *,
        operator: str,
    ) -> DemandConversionEvidence:
        record = evidence
        if isinstance(record, str):
            if self.repository is None:
                raise ValueError("evidence IDs require a repository")
            loader = getattr(self.repository, "get_demand_conversion_evidence", None)
            record = loader(record) if callable(loader) else None
            if record is None:
                raise ValueError(f"demand conversion evidence not found: {evidence}")
        if record.state != "draft":
            raise ValueError("only draft demand conversion evidence may be approved")
        if not operator.strip():
            raise ValueError("approval requires an operator")
        approved = replace(
            record,
            id=new_id(),
            state="approved",
            approved_by=operator,
            approved_at=utc_now_iso(),
            predecessor_id=record.id,
            created_at=utc_now_iso(),
        )
        if self.repository is not None:
            return self.repository.save_demand_conversion_evidence(approved)
        return approved

    @staticmethod
    def _validate_inputs(
        *,
        prospect_id: str,
        vertical_id: str,
        market: str,
        mode: str,
        demand: DemandEvidenceSet | None,
        economics: BusinessEconomicsProfile | None,
        owner_snapshots: list[OwnedMeasurementSnapshot],
        trend_snapshots: list[DemandTrendSnapshot],
        event_map: ConversionEventMap | None,
    ) -> None:
        if not prospect_id.strip() or not vertical_id.strip() or not market.strip():
            raise ValueError("demand conversion requires prospect, vertical, and market")
        if demand is not None:
            if demand.prospect_id != prospect_id or demand.vertical_id != vertical_id:
                raise ValueError("demand evidence context does not match")
            if demand.market.casefold().strip() != market.casefold().strip():
                raise ValueError("demand evidence market does not match")
            if demand.state != "approved":
                raise ValueError("demand conversion requires approved demand evidence")
        if economics is not None:
            if (
                economics.prospect_id != prospect_id
                or economics.vertical_id != vertical_id
            ):
                raise ValueError("economics context does not match")
            if economics.state != "approved":
                raise ValueError("demand conversion requires approved economics")
        for snapshot in owner_snapshots:
            if (
                snapshot.prospect_id != prospect_id
                or snapshot.vertical_id != vertical_id
            ):
                raise ValueError("owner measurement context does not match")
            snapshot_market = str(
                snapshot.context.get("market")
                or snapshot.context.get("location")
                or ""
            ).strip()
            if snapshot_market and snapshot_market.casefold() != market.casefold():
                raise ValueError("owner measurement market does not match")
        if mode == "prospect" and owner_snapshots:
            raise ValueError("prospect mode cannot consume owner measurements")
        if mode == "owner_verified" and not owner_snapshots:
            raise ValueError("owner-verified mode requires owner measurements")
        for trend in trend_snapshots:
            if trend.prospect_id != prospect_id or trend.vertical_id != vertical_id:
                raise ValueError("demand trend context does not match")
            if trend.market.casefold().strip() != market.casefold().strip():
                raise ValueError("demand trend market does not match")
            if trend.state != "approved":
                raise ValueError("demand conversion requires approved demand trends")
        if event_map is not None:
            if (
                event_map.prospect_id != prospect_id
                or event_map.vertical_id != vertical_id
            ):
                raise ValueError("conversion event map context does not match")
            if event_map.state != "approved":
                raise ValueError("demand conversion requires an approved event map")

    @staticmethod
    def _normalize_assumptions(
        assumptions: dict[str, dict[str, float | int | None]],
    ) -> dict[str, dict[str, float | int | None]]:
        normalized: dict[str, dict[str, float | int | None]] = {}
        for band in ("low", "base", "high"):
            values = dict(assumptions.get(band) or {})
            for rate_key in (
                "organic_visit_capture_rate",
                "lead_rate",
                "booking_rate",
                "close_rate",
            ):
                value = values.get(rate_key)
                if value is not None and not 0 <= float(value) <= 1:
                    raise ValueError(f"{rate_key} must be between zero and one")
            visits = values.get("incremental_qualified_visits")
            if visits is not None and float(visits) < 0:
                raise ValueError("incremental qualified visits cannot be negative")
            normalized[band] = values
        return normalized

    @staticmethod
    def _intent_groups(
        demand: DemandEvidenceSet | None,
        trends: list[DemandTrendSnapshot],
    ) -> list[dict[str, Any]]:
        if demand is None:
            return []
        trend_by_family: dict[str, list[dict[str, Any]]] = {}
        for snapshot in trends:
            for term in snapshot.terms:
                trend_by_family.setdefault(str(term["intent_family"]), []).append(
                    {
                        "source": snapshot.source,
                        "snapshot_id": snapshot.id,
                        "period_start": snapshot.period_start,
                        "period_end": snapshot.period_end,
                        "metrics": dict(term["metrics"]),
                        "provenance_label": term["provenance_label"],
                    }
                )
        groups: list[dict[str, Any]] = []
        for group in demand.groups:
            if group.get("status") != "approved":
                continue
            family = str(group.get("intent_family") or "")
            groups.append(
                {
                    "group_id": group.get("id"),
                    "intent_family": family,
                    "representative_term": group.get("representative_term"),
                    "monthly_search_occasions": group.get(
                        "approved_monthly_search_occasions"
                    ),
                    "aggregation_rule": group.get("aggregation_rule"),
                    "is_brand": bool(group.get("is_brand")),
                    "provenance_label": "supplied",
                    "trend_evidence": trend_by_family.get(family, []),
                }
            )
        return groups

    @classmethod
    def _model_outputs(
        cls,
        *,
        assumption_bands: dict[str, dict[str, float | int | None]],
        baseline: dict[str, Any],
        nonbrand_search_occasions: float,
        economics: BusinessEconomicsProfile | None,
        mode: str,
    ) -> tuple[dict[str, Any], dict[str, dict[str, dict[str, Any]]]]:
        observed = dict(baseline.get("observed_metrics") or {})
        outputs: dict[str, Any] = {}
        assumptions: dict[str, dict[str, dict[str, Any]]] = {}
        for band in ("low", "base", "high"):
            supplied = assumption_bands[band]
            visit_capture = supplied.get("organic_visit_capture_rate")
            explicit_visits = supplied.get("incremental_qualified_visits")
            visits = (
                float(explicit_visits)
                if explicit_visits is not None
                else nonbrand_search_occasions * float(visit_capture)
                if visit_capture is not None and nonbrand_search_occasions > 0
                else None
            )
            rate_values: dict[str, tuple[float | None, str]] = {}
            for key, observed_key in (
                ("lead_rate", "visit_to_signup"),
                ("booking_rate", "attendance_rate"),
                ("close_rate", "close_rate"),
            ):
                observed_value = observed.get(observed_key) if mode == "owner_verified" else None
                if observed_value is not None:
                    rate_values[key] = (float(observed_value), "observed")
                else:
                    supplied_value = supplied.get(key)
                    rate_values[key] = (
                        float(supplied_value) if supplied_value is not None else None,
                        "assumed",
                    )
            assumptions[band] = {
                "incremental_qualified_visits": {
                    "value": cls._round(visits) if visits is not None else None,
                    "provenance_label": (
                        "supplied" if explicit_visits is not None else "modeled"
                    ),
                },
                "organic_visit_capture_rate": {
                    "value": visit_capture,
                    "provenance_label": "assumed",
                },
                **{
                    key: {
                        "value": cls._round(value) if value is not None else None,
                        "provenance_label": provenance,
                    }
                    for key, (value, provenance) in rate_values.items()
                },
            }
            if (
                economics is None
                or visits is None
                or any(value is None for value, _ in rate_values.values())
            ):
                continue
            lead_rate = rate_values["lead_rate"][0] or 0.0
            booking_rate = rate_values["booking_rate"][0] or 0.0
            close_rate = rate_values["close_rate"][0] or 0.0
            leads = visits * lead_rate
            bookings = leads * booking_rate
            unconstrained = bookings * close_rate
            incremental_members = min(unconstrained, economics.capacity_headroom)
            mrr = incremental_members * economics.monthly_price
            outputs[band] = {
                "provenance_label": "modeled",
                "monthly_search_occasions": cls._round(nonbrand_search_occasions),
                "incremental_qualified_visits": cls._round(visits),
                "incremental_leads": cls._round(leads),
                "incremental_bookings": cls._round(bookings),
                "unconstrained_members": cls._round(unconstrained),
                "incremental_members": cls._round(incremental_members),
                "capacity_constrained": unconstrained > economics.capacity_headroom,
                "incremental_recurring_revenue": cls._round(mrr),
                "annual_run_rate": cls._round(mrr * 12),
                "currency": economics.currency,
                "formula_version": DEMAND_CONVERSION_FORMULA_VERSION,
            }
        if len(outputs) != 3:
            outputs = {}
        return outputs, assumptions

    @classmethod
    def _source_snapshots(
        cls,
        *,
        prospect_id: str,
        vertical_id: str,
        market: str,
        demand: DemandEvidenceSet | None,
        economics: BusinessEconomicsProfile | None,
        owner_snapshots: list[OwnedMeasurementSnapshot],
        trend_snapshots: list[DemandTrendSnapshot],
        public_sources: list[dict[str, Any]],
        modeled: bool,
        assumptions: dict[str, Any],
    ) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []
        if demand is not None:
            sources.append(
                cls._source(
                    source_name=demand.source,
                    source_class="approved_market",
                    provenance_label="supplied",
                    source_sha256=demand.source_sha256,
                    artifact_ref=f"demand_evidence_sets/{demand.id}.json",
                    snapshot_date=demand.created_at[:10],
                    prospect_id=prospect_id,
                    vertical_id=vertical_id,
                    market=market,
                )
            )
        if economics is not None:
            sources.append(
                cls._source(
                    source_name="business_economics_profile",
                    source_class="operator_supplied",
                    provenance_label="supplied",
                    source_sha256=canonical_sha256(economics.to_dict()),
                    artifact_ref=f"economics_profiles/{economics.id}.json",
                    snapshot_date=economics.created_at[:10],
                    prospect_id=prospect_id,
                    vertical_id=vertical_id,
                    market=market,
                )
            )
        for snapshot in owner_snapshots:
            sources.append(
                cls._source(
                    source_name=snapshot.source,
                    source_class="owner_first_party",
                    provenance_label="observed",
                    source_sha256=snapshot.source_sha256,
                    artifact_ref=f"owned_measurements/{snapshot.id}.json",
                    snapshot_date=snapshot.period_end[:10],
                    prospect_id=prospect_id,
                    vertical_id=vertical_id,
                    market=market,
                    extra={
                        "snapshot_id": snapshot.id,
                        "period_start": snapshot.period_start,
                        "period_end": snapshot.period_end,
                        "device": snapshot.context.get("device"),
                    },
                )
            )
        for snapshot in trend_snapshots:
            sources.append(
                cls._source(
                    source_name=snapshot.source,
                    source_class="approved_market",
                    provenance_label="observed"
                    if snapshot.source == "google_trends_csv"
                    else "supplied",
                    source_sha256=snapshot.source_sha256,
                    artifact_ref=f"demand_trends/{snapshot.id}.json",
                    snapshot_date=snapshot.period_end[:10],
                    prospect_id=prospect_id,
                    vertical_id=vertical_id,
                    market=market,
                    extra={
                        "snapshot_id": snapshot.id,
                        "period_start": snapshot.period_start,
                        "period_end": snapshot.period_end,
                    },
                )
            )
        for source in public_sources:
            payload = dict(source)
            source_class = str(payload.get("source_class") or "public_observed")
            payload.setdefault(
                "hierarchy_level",
                DEMAND_CONVERSION_SOURCE_CLASSES.get(source_class),
            )
            payload.setdefault("provenance_label", "observed")
            payload.setdefault("prospect_id", prospect_id)
            payload.setdefault("vertical_id", vertical_id)
            payload.setdefault("market", market)
            sources.append(payload)
        if modeled:
            sources.append(
                cls._source(
                    source_name=DEMAND_CONVERSION_FORMULA_VERSION,
                    source_class="scenario_model",
                    provenance_label="modeled",
                    source_sha256=canonical_sha256(
                        {
                            "formula_version": DEMAND_CONVERSION_FORMULA_VERSION,
                            "assumptions": assumptions,
                        }
                    ),
                    artifact_ref=(
                        "docs/product-revenue-contract.md"
                        "#demand-conversion-evidence-modes"
                    ),
                    snapshot_date=utc_now_iso()[:10],
                    prospect_id=prospect_id,
                    vertical_id=vertical_id,
                    market=market,
                )
            )
        return sources

    @staticmethod
    def _source(
        *,
        source_name: str,
        source_class: str,
        provenance_label: str,
        source_sha256: str,
        artifact_ref: str,
        snapshot_date: str,
        prospect_id: str,
        vertical_id: str,
        market: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "source_name": source_name,
            "source_class": source_class,
            "hierarchy_level": DEMAND_CONVERSION_SOURCE_CLASSES[source_class],
            "provenance_label": provenance_label,
            "source_sha256": source_sha256,
            "artifact_ref": artifact_ref,
            "snapshot_date": snapshot_date,
            "prospect_id": prospect_id,
            "vertical_id": vertical_id,
            "market": market,
        }
        payload.update(extra or {})
        return payload

    @staticmethod
    def _completeness(
        *,
        mode: str,
        demand: DemandEvidenceSet | None,
        economics: BusinessEconomicsProfile | None,
        owner_snapshots: list[OwnedMeasurementSnapshot],
        trend_snapshots: list[DemandTrendSnapshot],
        event_map: ConversionEventMap | None,
        search_alignment: dict[str, Any] | None,
        assumptions: dict[str, dict[str, dict[str, Any]]],
    ) -> tuple[float, list[dict[str, Any]]]:
        rate_known = all(
            assumptions[band][key]["value"] is not None
            for band in assumptions
            for key in ("lead_rate", "booking_rate", "close_rate")
        )
        if mode == "owner_verified":
            weights = {
                "approved_demand": (15, demand is not None),
                "approved_economics": (10, economics is not None),
                "capacity": (10, economics is not None),
                "owner_first_party": (15, bool(owner_snapshots)),
                "search_console": (
                    10,
                    any(row.source == "gsc_csv" for row in owner_snapshots),
                ),
                "analytics": (
                    10,
                    any(row.source == "ga4_csv" for row in owner_snapshots),
                ),
                "booking_crm": (
                    10,
                    any(row.source == "crm_csv" for row in owner_snapshots),
                ),
                "funnel_rates": (15, rate_known),
                "event_map": (5, event_map is not None),
            }
        else:
            weights = {
                "approved_demand": (20, demand is not None),
                "approved_economics": (15, economics is not None),
                "capacity": (10, economics is not None),
                "public_search": (
                    15,
                    bool(
                        search_alignment
                        and any(
                            row.get("ranking_observations")
                            for row in search_alignment.get("groups", [])
                        )
                    ),
                ),
                "funnel_rates": (30, rate_known),
                "trend_or_market": (10, bool(trend_snapshots or demand)),
            }
        known = sum(weight for weight, passed in weights.values() if passed)
        total = sum(weight for weight, _ in weights.values())
        checks = [
            {
                "check_id": check_id,
                "weight": weight,
                "status": "known" if passed else "unknown",
            }
            for check_id, (weight, passed) in weights.items()
        ]
        return round(100 * known / total, 2), checks

    @staticmethod
    def _evidence_refs(
        *,
        demand: DemandEvidenceSet | None,
        economics: BusinessEconomicsProfile | None,
        owner_snapshots: list[OwnedMeasurementSnapshot],
        trend_snapshots: list[DemandTrendSnapshot],
        event_map: ConversionEventMap | None,
        search_alignment: dict[str, Any] | None,
        public_sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        refs: list[dict[str, Any]] = []
        if demand is not None:
            refs.append(
                {
                    "kind": "demand_evidence_set",
                    "id": demand.id,
                    "source_sha256": demand.source_sha256,
                }
            )
        if economics is not None:
            refs.append(
                {
                    "kind": "business_economics_profile",
                    "id": economics.id,
                    "sha256": canonical_sha256(economics.to_dict()),
                }
            )
        refs.extend(
            {
                "kind": "owned_measurement",
                "id": snapshot.id,
                "source_sha256": snapshot.source_sha256,
                "artifact_ref": snapshot.artifact_ref,
            }
            for snapshot in owner_snapshots
        )
        refs.extend(
            {
                "kind": "demand_trend",
                "id": snapshot.id,
                "source_sha256": snapshot.source_sha256,
                "artifact_ref": snapshot.artifact_ref,
            }
            for snapshot in trend_snapshots
        )
        if event_map is not None:
            refs.append(
                {
                    "kind": "conversion_event_map",
                    "id": event_map.id,
                    "sha256": canonical_sha256(event_map.to_dict()),
                }
            )
        for group in (search_alignment or {}).get("groups", []):
            refs.extend(group.get("evidence_refs", []))
        refs.extend(
            {
                "kind": "public_artifact",
                "artifact_ref": source.get("artifact_ref"),
                "source_sha256": source.get("source_sha256"),
            }
            for source in public_sources
            if source.get("artifact_ref")
        )
        return refs

    @staticmethod
    def _assumption_rows(
        assumptions: dict[str, dict[str, dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        return [
            {
                "band": band,
                "name": name,
                **payload,
            }
            for band in ("low", "base", "high")
            for name, payload in assumptions[band].items()
        ]

    @staticmethod
    def _round(value: float | int | None) -> float | int | None:
        if value is None:
            return None
        rounded = round(float(value), 4)
        return int(rounded) if rounded.is_integer() else rounded
