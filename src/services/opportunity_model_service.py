"""Deterministic search-demand to capacity/revenue opportunity modeling."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from src.models import (
    EVIDENCE_PROVENANCE_TYPES,
    FORECAST_DISCLAIMER,
    OPPORTUNITY_FORMULA_VERSION,
    BusinessEconomicsProfile,
    DemandEvidenceSet,
    DemandGroup,
    OpportunityScenario,
    new_id,
    utc_now_iso,
)
from src.repositories.base import InsightRepository
from src.vertical_packs import resolve_vertical_pack


class OpportunityModelService:
    """Pure formula service with optional repository-backed lifecycle methods."""

    MATERIAL_ASSUMPTIONS = (
        "searches_per_prospect",
        "organic_incremental_click_share",
        "maps_incremental_click_share",
        "organic_maps_overlap_rate",
        "visit_to_signup_rate",
        "signup_to_attended_rate",
        "attended_to_customer_rate",
        "ramp_months",
    )
    BANDS = ("low", "base", "high")

    def __init__(self, repository: InsightRepository | None = None) -> None:
        self.repository = repository

    def create_scenario(
        self,
        *,
        insight_run_id: str,
        prospect_id: str,
        economics: BusinessEconomicsProfile,
        demand: DemandEvidenceSet | None,
        assumptions: dict[str, dict[str, Any]],
    ) -> OpportunityScenario:
        if economics.prospect_id != prospect_id:
            raise ValueError("economics profile belongs to a different prospect")
        if demand is not None and demand.prospect_id != prospect_id:
            raise ValueError("demand evidence belongs to a different prospect")
        if demand is not None and demand.vertical_id != economics.vertical_id:
            raise ValueError("demand and economics verticals do not match")

        normalized = self._normalize_assumptions(assumptions, economics)
        demand_ready = demand is not None and demand.state == "approved"
        economics_ready = economics.state == "approved"
        search_occasions = (
            self.approved_nonbrand_search_occasions(demand)
            if demand_ready and demand is not None
            else None
        )
        numeric_complete = all(
            self._band_numeric_complete(normalized[band])
            for band in self.BANDS
        )
        reviewed_complete = all(
            self._band_reviewed(normalized[band])
            for band in self.BANDS
        )
        material_total = len(self.MATERIAL_ASSUMPTIONS) * len(self.BANDS) + 2
        material_known = sum(
            1
            for band in self.BANDS
            for name in self.MATERIAL_ASSUMPTIONS
            if self._entry_value(normalized[band].get(name)) is not None
        )
        material_known += int(demand_ready) + int(economics_ready)
        completeness = round(100 * material_known / material_total, 2)

        warnings: list[str] = [FORECAST_DISCLAIMER]
        outputs: dict[str, dict[str, Any]] = {}
        if not demand_ready:
            warnings.append(
                "Approved demand evidence is required before acquisition projections."
            )
        if search_occasions is not None and search_occasions <= 0:
            warnings.append(
                "No approved non-brand search occasions are available for net-new modeling."
            )
        if not economics_ready:
            warnings.append(
                "The business economics profile requires operator approval."
            )
        if not numeric_complete:
            warnings.append(
                "Every low/base/high material assumption requires a numeric value."
            )
        if numeric_complete and not reviewed_complete:
            warnings.append(
                "Numeric projections are reviewable but material assumptions remain unapproved."
            )

        can_calculate = (
            demand_ready
            and economics_ready
            and search_occasions is not None
            and search_occasions > 0
            and numeric_complete
        )
        if can_calculate:
            outputs = {
                band: self._calculate_band(
                    search_occasions=search_occasions,
                    economics=economics,
                    assumptions=normalized[band],
                )
                for band in self.BANDS
            }

        if can_calculate and reviewed_complete:
            status = "complete"
        elif can_calculate:
            status = "partial"
        else:
            status = "limited"

        scenario = OpportunityScenario(
            insight_run_id=insight_run_id,
            prospect_id=prospect_id,
            demand_evidence_set_id=demand.id if demand else None,
            demand_evidence_version=demand.version if demand else None,
            economics_profile_id=economics.id,
            economics_profile_version=economics.version,
            assumptions=normalized,
            outputs=outputs,
            status=status,
            completeness_percent=completeness,
            sensitivity=self._sensitivity(outputs, economics),
            service_levers=self._service_levers(economics.vertical_id),
            evidence_refs=self._evidence_refs(demand, economics),
            warnings=warnings,
        )
        if self.repository is not None:
            return self.repository.save_opportunity_scenario(scenario)
        return scenario

    def approve_scenario(
        self,
        scenario_id: str,
        *,
        operator: str,
    ) -> OpportunityScenario:
        if self.repository is None:
            raise ValueError("scenario approval requires a repository")
        scenario = self.repository.get_opportunity_scenario(scenario_id)
        if scenario is None:
            raise ValueError(f"opportunity scenario not found: {scenario_id}")
        if scenario.state == "approved":
            return scenario
        if scenario.status != "complete":
            raise ValueError("only complete opportunity scenarios may be approved")
        if not operator.strip():
            raise ValueError("scenario approval requires an operator")
        if not all(
            self._band_reviewed(scenario.assumptions[band])
            for band in self.BANDS
        ):
            raise ValueError("scenario approval requires reviewed material assumptions")
        approved = replace(
            scenario,
            id=new_id(),
            state="approved",
            predecessor_id=scenario.id,
            approved_by=operator.strip(),
            approved_at=utc_now_iso(),
            created_at=utc_now_iso(),
        )
        return self.repository.save_opportunity_scenario(approved)

    @staticmethod
    def approved_nonbrand_search_occasions(
        demand: DemandEvidenceSet,
    ) -> float:
        if demand.state != "approved":
            raise ValueError("search-occasion arithmetic requires approved demand evidence")
        total = 0.0
        for payload in demand.groups:
            group = DemandGroup(**payload)
            if group.status != "approved" or group.is_brand:
                continue
            if group.approved_monthly_search_occasions is not None:
                total += group.approved_monthly_search_occasions
        return round(total, 6)

    def _normalize_assumptions(
        self,
        assumptions: dict[str, dict[str, Any]],
        economics: BusinessEconomicsProfile,
    ) -> dict[str, dict[str, Any]]:
        output: dict[str, dict[str, Any]] = {}
        economics_defaults = {
            "visit_to_signup_rate": economics.visit_to_signup_rate,
            "signup_to_attended_rate": economics.signup_to_attended_rate,
            "attended_to_customer_rate": economics.attended_to_customer_rate,
            "ramp_months": economics.desired_fill_months,
        }
        for band in self.BANDS:
            source = assumptions.get(band)
            if not isinstance(source, dict):
                source = {}
            normalized: dict[str, Any] = {}
            for name in self.MATERIAL_ASSUMPTIONS:
                entry = source.get(name)
                if entry is None and economics_defaults.get(name) is not None:
                    entry = {
                        "value": economics_defaults[name],
                        "provenance": economics.field_provenance.get(
                            name,
                            "business_supplied",
                        ),
                        "reviewed": economics.state == "approved",
                    }
                normalized[name] = self._normalize_entry(name, entry)
            if "retention_months" in source or economics.retention_months is not None:
                normalized["retention_months"] = self._normalize_entry(
                    "retention_months",
                    source.get("retention_months")
                    or {
                        "value": economics.retention_months,
                        "provenance": economics.field_provenance.get(
                            "retention_months",
                            "business_supplied",
                        ),
                        "reviewed": economics.state == "approved",
                    },
                    material=False,
                )
            output[band] = normalized
        return output

    @staticmethod
    def _normalize_entry(
        name: str,
        entry: Any,
        *,
        material: bool = True,
    ) -> dict[str, Any]:
        if isinstance(entry, dict):
            value = entry.get("value")
            provenance = str(entry.get("provenance") or "assumed")
            reviewed = bool(entry.get("reviewed", False))
        else:
            value = entry
            provenance = "assumed"
            reviewed = False
        if provenance not in EVIDENCE_PROVENANCE_TYPES:
            raise ValueError(f"invalid assumption provenance for {name}: {provenance}")
        if value is None:
            return {
                "value": None,
                "provenance": provenance,
                "reviewed": False,
                "material": material,
            }
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValueError(f"{name} must be numeric")
        number = float(value)
        rate_fields = {
            "organic_incremental_click_share",
            "maps_incremental_click_share",
            "organic_maps_overlap_rate",
            "visit_to_signup_rate",
            "signup_to_attended_rate",
            "attended_to_customer_rate",
        }
        if name in rate_fields and not 0 <= number <= 1:
            raise ValueError(f"{name} must be between zero and one")
        if name in {"searches_per_prospect", "ramp_months", "retention_months"} and number <= 0:
            raise ValueError(f"{name} must be greater than zero")
        return {
            "value": number,
            "provenance": provenance,
            "reviewed": reviewed,
            "material": material,
        }

    def _calculate_band(
        self,
        *,
        search_occasions: float,
        economics: BusinessEconomicsProfile,
        assumptions: dict[str, Any],
    ) -> dict[str, Any]:
        value = lambda name: float(self._entry_value(assumptions[name]) or 0)
        unique_prospects = search_occasions / value("searches_per_prospect")
        organic_visits = unique_prospects * value(
            "organic_incremental_click_share"
        )
        maps_visits = unique_prospects * value("maps_incremental_click_share")
        overlap_visits = min(organic_visits, maps_visits) * value(
            "organic_maps_overlap_rate"
        )
        incremental_visits = max(
            0.0,
            organic_visits + maps_visits - overlap_visits,
        )
        signups = incremental_visits * value("visit_to_signup_rate")
        attended = signups * value("signup_to_attended_rate")
        incremental_customers = attended * value(
            "attended_to_customer_rate"
        )
        capacity_adjusted = min(
            incremental_customers,
            economics.capacity_headroom,
        )
        capacity_constrained = incremental_customers > economics.capacity_headroom
        mrr = capacity_adjusted * economics.monthly_price
        annual_run_rate = mrr * 12
        time_to_fill = (
            economics.capacity_headroom / incremental_customers
            if incremental_customers > 0 and economics.capacity_headroom > 0
            else None
        )
        ramp_months = value("ramp_months")
        year_one_ending_active = capacity_adjusted * min(1.0, 12 / ramp_months)
        if ramp_months <= 12:
            member_months = capacity_adjusted * (12 - (ramp_months / 2))
        else:
            member_months = year_one_ending_active * 6
        first_year_revenue = member_months * economics.monthly_price
        retention = self._entry_value(assumptions.get("retention_months"))
        ltv_revenue = (
            capacity_adjusted * economics.monthly_price * float(retention)
            if retention is not None
            else None
        )
        return {
            "monthly_nonbrand_search_occasions": round(search_occasions, 2),
            "modeled_unique_prospects": round(unique_prospects, 2),
            "incremental_organic_visits": round(organic_visits, 2),
            "incremental_maps_visits": round(maps_visits, 2),
            "modeled_overlap_visits": round(overlap_visits, 2),
            "incremental_visits": round(incremental_visits, 2),
            "signups_or_leads": round(signups, 2),
            "attended_trials_or_appointments": round(attended, 2),
            "incremental_customers_before_capacity": round(
                incremental_customers,
                2,
            ),
            "capacity_adjusted_active_customers": round(capacity_adjusted, 2),
            "capacity_headroom": economics.capacity_headroom,
            "capacity_constrained": capacity_constrained,
            "time_to_fill_months": (
                round(time_to_fill, 2) if time_to_fill is not None else None
            ),
            "ending_mrr": round(mrr, 2),
            "annual_run_rate": round(annual_run_rate, 2),
            "ramp_months": round(ramp_months, 2),
            "year_one_ending_active_customers": round(
                year_one_ending_active,
                2,
            ),
            "first_year_ramp_revenue": round(first_year_revenue, 2),
            "retention_ltv_revenue": (
                round(ltv_revenue, 2) if ltv_revenue is not None else None
            ),
        }

    @staticmethod
    def _entry_value(entry: Any) -> float | None:
        if not isinstance(entry, dict):
            return None
        value = entry.get("value")
        if isinstance(value, bool) or not isinstance(value, int | float):
            return None
        return float(value)

    def _band_numeric_complete(self, band: dict[str, Any]) -> bool:
        return all(
            self._entry_value(band.get(name)) is not None
            for name in self.MATERIAL_ASSUMPTIONS
        )

    def _band_reviewed(self, band: dict[str, Any]) -> bool:
        return all(
            bool(band.get(name, {}).get("reviewed"))
            for name in self.MATERIAL_ASSUMPTIONS
        )

    @staticmethod
    def _sensitivity(
        outputs: dict[str, dict[str, Any]],
        economics: BusinessEconomicsProfile,
    ) -> dict[str, Any]:
        return {
            "capacity_ceiling": {
                "active_customers": economics.capacity_headroom,
                "mrr": round(economics.capacity_mrr, 2),
                "annual_run_rate": round(
                    economics.capacity_annual_run_rate,
                    2,
                ),
                "label": "Capacity ceiling, not promised ranking revenue",
            },
            "low_to_high": (
                {
                    "modeled_unique_prospects": [
                        outputs["low"]["modeled_unique_prospects"],
                        outputs["high"]["modeled_unique_prospects"],
                    ],
                    "capacity_adjusted_active_customers": [
                        outputs["low"]["capacity_adjusted_active_customers"],
                        outputs["high"]["capacity_adjusted_active_customers"],
                    ],
                    "first_year_ramp_revenue": [
                        outputs["low"]["first_year_ramp_revenue"],
                        outputs["high"]["first_year_ramp_revenue"],
                    ],
                }
                if outputs
                else {}
            ),
        }

    @staticmethod
    def _service_levers(vertical_id: str) -> list[dict[str, Any]]:
        pack = resolve_vertical_pack(f"{vertical_id}.v1")
        stages = pack.service_taxonomy.get("funnel_stages", [])
        return [
            {
                "order": 1,
                "service_package": "website_seo_vertical_visibility",
                "lever": "visibility",
                "affects": ["qualified_visits"],
            },
            {
                "order": 2,
                "service_package": "vertical_plugin_embed",
                "lever": "onsite_conversion",
                "affects": [stages[1] if len(stages) > 1 else "signup_or_lead"],
            },
            {
                "order": 3,
                "service_package": "custom_website_crm_saas",
                "lever": "follow_up_and_close",
                "affects": stages[2:] or ["attendance", "customer"],
            },
        ]

    @staticmethod
    def _evidence_refs(
        demand: DemandEvidenceSet | None,
        economics: BusinessEconomicsProfile,
    ) -> list[dict[str, Any]]:
        refs = [
            {
                "kind": "business_economics_profile",
                "record_id": economics.id,
                "version": economics.version,
            }
        ]
        if demand is not None:
            refs.append(
                {
                    "kind": "demand_evidence_set",
                    "record_id": demand.id,
                    "version": demand.version,
                    "source_sha256": demand.source_sha256,
                }
            )
        return refs
