"""Immutable opportunity and combined operator report assembly."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.models import (
    FORECAST_DISCLAIMER,
    BusinessEconomicsProfile,
    DemandEvidenceSet,
    InsightReport,
    OpportunityScenario,
)
from src.repositories.base import InsightRepository


class OpportunityReportingService:
    def __init__(self, repository: InsightRepository) -> None:
        self.repository = repository

    def assemble(self, scenario_id: str) -> dict[str, InsightReport]:
        scenario = self.repository.get_opportunity_scenario(scenario_id)
        if scenario is None:
            raise ValueError(f"opportunity scenario not found: {scenario_id}")
        run = self.repository.get_run(scenario.insight_run_id)
        if run is None or run.status != "completed":
            raise ValueError("opportunity reporting requires a completed insight run")
        seo = self.repository.get_report(run.id, "v2")
        if seo is None:
            raise ValueError("opportunity reporting requires the v2 SEO report")
        ai = (
            self.repository.get_report(run.id, "ai-v2")
            or self.repository.get_report(run.id, "ai-v1")
        )
        market = self.repository.get_report(run.id, "market-v1")
        economics = self.repository.get_business_economics_profile(
            scenario.economics_profile_id
        )
        if economics is None:
            raise ValueError("opportunity economics profile is missing")
        demand = (
            self.repository.get_demand_evidence_set(
                scenario.demand_evidence_set_id
            )
            if scenario.demand_evidence_set_id
            else None
        )
        if scenario.demand_evidence_set_id and demand is None:
            raise ValueError("opportunity demand evidence is missing")

        payload = self._opportunity_payload(
            scenario,
            economics,
            demand,
            seo=seo,
            ai=ai,
            market=market,
        )
        opportunity = InsightReport(
            insight_run_id=run.id,
            seo_target_id=run.seo_target_id,
            attempt_id=run.attempt_id,
            report_version="opportunity-v1",
            report_status=scenario.status,
            headline=f"Demand and capacity opportunity — {run.requested_domain}",
            executive_summary=payload["executive_answer"],
            key_actions=payload["recommended_first_move"],
            report_payload=payload,
            export_json=payload,
            export_markdown=self._opportunity_markdown(payload),
        )
        combined_payload = self._combined_payload(
            seo=seo,
            ai=ai,
            market=market,
            opportunity=payload,
        )
        combined = InsightReport(
            insight_run_id=run.id,
            seo_target_id=run.seo_target_id,
            attempt_id=run.attempt_id,
            report_version="v4",
            report_status=scenario.status,
            headline=f"Evidence and commercial opportunity — {run.requested_domain}",
            executive_summary=payload["executive_answer"],
            key_actions=payload["recommended_first_move"],
            report_payload=combined_payload,
            export_json=combined_payload,
            export_markdown=self._combined_markdown(combined_payload),
        )
        self.repository.save_report(opportunity)
        self.repository.save_report(combined)
        for report in (opportunity, combined):
            self.repository.save_opportunity_artifact(
                run.id,
                scenario.id,
                f"reports/{report.report_version}.json",
                report.to_dict(),
            )
            self.repository.save_opportunity_artifact(
                run.id,
                scenario.id,
                f"reports/{report.report_version}.md",
                (report.export_markdown or "").encode("utf-8"),
            )
        return {"opportunity-v1": opportunity, "v4": combined}

    @staticmethod
    def scenario_snapshot_sha256(scenario: OpportunityScenario) -> str:
        return hashlib.sha256(
            json.dumps(
                scenario.to_dict(),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()

    def _opportunity_payload(
        self,
        scenario: OpportunityScenario,
        economics: BusinessEconomicsProfile,
        demand: DemandEvidenceSet | None,
        *,
        seo: InsightReport,
        ai: InsightReport | None,
        market: InsightReport | None,
    ) -> dict[str, Any]:
        demand_groups = list(demand.groups) if demand else []
        nonbrand = sum(
            float(group.get("approved_monthly_search_occasions") or 0)
            for group in demand_groups
            if group.get("status") == "approved" and not group.get("is_brand")
        )
        brand = sum(
            float(group.get("approved_monthly_search_occasions") or 0)
            for group in demand_groups
            if group.get("status") == "approved" and group.get("is_brand")
        )
        scenario_hash = self.scenario_snapshot_sha256(scenario)
        verified_now = self._verified_now(seo, ai, market, demand, economics)
        potential = {
            "label": "modeled",
            "forecast_label": FORECAST_DISCLAIMER,
            "scenario_status": scenario.status,
            "scenario_state": scenario.state,
            "low_base_high": scenario.outputs,
            "capacity_ceiling": scenario.sensitivity.get("capacity_ceiling"),
        }
        what_to_confirm = [
            warning
            for warning in scenario.warnings
            if warning != FORECAST_DISCLAIMER
        ]
        for band, values in scenario.assumptions.items():
            for name, entry in values.items():
                if entry.get("material") and not entry.get("reviewed"):
                    what_to_confirm.append(f"{band}.{name} requires operator review")
        first_move = (
            [scenario.service_levers[0]]
            if scenario.service_levers
            else []
        )
        market_payload = market.report_payload if market else {}
        provider = (
            market_payload.get("provider")
            if isinstance(market_payload, dict)
            else {}
        ) or {}
        return {
            "report_contract": "opportunity-v1",
            "formula_version": scenario.formula_version,
            "forecast_label": FORECAST_DISCLAIMER,
            "scenario_id": scenario.id,
            "scenario_snapshot_sha256": scenario_hash,
            "source_versions": {
                "seo": seo.report_version,
                "ai": ai.report_version if ai else None,
                "market": market.report_version if market else None,
                "demand": demand.contract_version if demand else None,
                "demand_version": demand.version if demand else None,
                "economics_version": economics.version,
            },
            "executive_answer": OpportunityReportingService._executive_answer(
                scenario,
                economics,
            ),
            "verified_now": verified_now,
            "potential_if_assumptions_hold": potential,
            "what_we_need_to_confirm": sorted(set(what_to_confirm)),
            "recommended_first_move": first_move,
            "demand": {
                "label": "observed",
                "semantics": "Monthly search occasions, not unique people",
                "source_sha256": demand.source_sha256 if demand else None,
                "groups": demand_groups,
                "approved_nonbrand_search_occasions": nonbrand,
                "approved_brand_search_occasions_excluded_from_net_new": brand,
            },
            "modeled_unique_prospect_range": {
                "label": "modeled",
                "low": scenario.outputs.get("low", {}).get(
                    "modeled_unique_prospects"
                ),
                "base": scenario.outputs.get("base", {}).get(
                    "modeled_unique_prospects"
                ),
                "high": scenario.outputs.get("high", {}).get(
                    "modeled_unique_prospects"
                ),
                "searches_per_prospect": {
                    band: scenario.assumptions.get(band, {}).get(
                        "searches_per_prospect"
                    )
                    for band in ("low", "base", "high")
                },
            },
            "capacity_and_revenue": potential,
            "conversion_opportunities": scenario.service_levers,
            "service_path_fit": scenario.service_levers,
            "sensitivity": scenario.sensitivity,
            "provider_cost_and_completeness": provider,
            "screenshots": (
                market_payload.get("screenshots", [])
                if isinstance(market_payload, dict)
                else []
            ),
            "assumptions": scenario.assumptions,
            "evidence_refs": scenario.evidence_refs,
            "limitations": scenario.warnings,
        }

    @staticmethod
    def _verified_now(
        seo: InsightReport,
        ai: InsightReport | None,
        market: InsightReport | None,
        demand: DemandEvidenceSet | None,
        economics: BusinessEconomicsProfile,
    ) -> dict[str, Any]:
        scorecard = seo.report_payload.get("scorecard", {})
        ai_payload = ai.report_payload if ai else {}
        market_payload = market.report_payload if market else {}
        return {
            "label": "observed",
            "seo_score": scorecard.get("overall_score"),
            "ai_readiness_score": ai_payload.get("score"),
            "market_state": market_payload.get("state"),
            "rankings": market_payload.get("organic_rankings", []),
            "maps": market_payload.get("maps_rankings", []),
            "competitor_gaps": market_payload.get("recommended_actions", []),
            "economics": {
                "monthly_price": economics.monthly_price,
                "capacity_headroom": economics.capacity_headroom,
                "capacity_mrr": economics.capacity_mrr,
                "capacity_annual_run_rate": (
                    economics.capacity_annual_run_rate
                ),
                "field_provenance": economics.field_provenance,
            },
            "demand_state": demand.state if demand else "missing",
        }

    @staticmethod
    def _executive_answer(
        scenario: OpportunityScenario,
        economics: BusinessEconomicsProfile,
    ) -> str:
        capacity = (
            f"The reviewed capacity ceiling is {economics.capacity_headroom:g} "
            f"additional customers, ${economics.capacity_mrr:,.0f} MRR, and "
            f"${economics.capacity_annual_run_rate:,.0f} annual run-rate."
        )
        if not scenario.outputs:
            return (
                f"{capacity} Acquisition projections remain limited until "
                "approved demand and funnel assumptions are complete."
            )
        base = scenario.outputs["base"]
        return (
            f"{capacity} The reviewed base forecast models "
            f"{base.get('modeled_unique_prospects')} unique prospects and "
            f"{base.get('capacity_adjusted_active_customers')} capacity-adjusted "
            f"customers; this is a forecast, not a guarantee."
        )

    @staticmethod
    def _combined_payload(
        *,
        seo: InsightReport,
        ai: InsightReport | None,
        market: InsightReport | None,
        opportunity: dict[str, Any],
    ) -> dict[str, Any]:
        market_payload = market.report_payload if market else {}
        return {
            "report_contract": "v4",
            "source_versions": opportunity["source_versions"],
            "executive_answer": opportunity["executive_answer"],
            "verified_now": opportunity["verified_now"],
            "seo": seo.report_payload,
            "ai_readiness": ai.report_payload if ai else {
                "status": "unknown",
                "limitations": ["AI Readiness is unavailable for this legacy run."],
            },
            "rankings_and_maps": {
                "organic": market_payload.get("organic_rankings", []),
                "maps": market_payload.get("maps_rankings", []),
            },
            "competitors": {
                "approved": market_payload.get("approved_competitors", []),
                "gap_matrix": market_payload.get("gap_matrix", []),
            },
            "demand_groups": opportunity["demand"],
            "unique_prospect_range": opportunity[
                "modeled_unique_prospect_range"
            ],
            "capacity_and_revenue": opportunity["capacity_and_revenue"],
            "conversion_opportunities": opportunity[
                "conversion_opportunities"
            ],
            "service_path_fit": opportunity["service_path_fit"],
            "sensitivity": opportunity["sensitivity"],
            "provider_cost_and_completeness": opportunity[
                "provider_cost_and_completeness"
            ],
            "screenshots": opportunity["screenshots"],
            "what_we_need_to_confirm": opportunity[
                "what_we_need_to_confirm"
            ],
            "recommended_first_move": opportunity["recommended_first_move"],
            "assumptions_and_limitations": {
                "forecast_label": FORECAST_DISCLAIMER,
                "assumptions": opportunity["assumptions"],
                "limitations": opportunity["limitations"],
            },
            "opportunity_scenario_id": opportunity["scenario_id"],
            "opportunity_snapshot_sha256": opportunity[
                "scenario_snapshot_sha256"
            ],
        }

    @staticmethod
    def _opportunity_markdown(payload: dict[str, Any]) -> str:
        lines = [
            "# Demand and revenue opportunity",
            "",
            f"> {FORECAST_DISCLAIMER}",
            "",
            "## Executive answer",
            payload["executive_answer"],
            "",
            "## Verified now",
        ]
        for key, value in payload["verified_now"].items():
            if key not in {"rankings", "maps", "competitor_gaps"}:
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        lines.extend(["", "## Potential if assumptions hold"])
        for band, output in payload["capacity_and_revenue"][
            "low_base_high"
        ].items():
            lines.append(
                f"- {band.title()}: {output.get('modeled_unique_prospects')} "
                f"modeled unique prospects; "
                f"{output.get('capacity_adjusted_active_customers')} customers; "
                f"${output.get('ending_mrr', 0):,.0f} ending MRR; "
                f"${output.get('first_year_ramp_revenue', 0):,.0f} first-year ramp revenue."
            )
        lines.extend(["", "## What we need to confirm"])
        lines.extend(
            f"- {item}" for item in payload["what_we_need_to_confirm"]
        )
        lines.extend(["", "## Recommended first move"])
        lines.extend(
            f"- {item.get('service_package')}: {item.get('lever')}"
            for item in payload["recommended_first_move"]
        )
        lines.extend(
            [
                "",
                "## Limitations",
                "- Search volume represents search occasions, not unique people.",
                "- Rankings and Maps are dated samples, not promises.",
                f"- {FORECAST_DISCLAIMER}.",
            ]
        )
        return "\n".join(lines) + "\n"

    @staticmethod
    def _combined_markdown(payload: dict[str, Any]) -> str:
        lines = [
            "# Combined evidence and commercial opportunity",
            "",
            f"> {FORECAST_DISCLAIMER}",
            "",
            "## Executive answer",
            payload["executive_answer"],
            "",
            "## Verified evidence",
            f"- SEO score: {payload['verified_now'].get('seo_score')}",
            f"- AI Readiness: {payload['verified_now'].get('ai_readiness_score')}",
            "",
            "## Demand and modeled opportunity",
        ]
        capacity = payload["capacity_and_revenue"]
        lines.append(
            f"- Capacity ceiling: {capacity.get('capacity_ceiling')}"
        )
        for band, output in capacity.get("low_base_high", {}).items():
            lines.append(
                f"- {band}: {output.get('modeled_unique_prospects')} modeled "
                f"prospects; {output.get('capacity_adjusted_active_customers')} customers."
            )
        lines.extend(["", "## Assumptions and limitations"])
        lines.extend(
            f"- {item}"
            for item in payload["assumptions_and_limitations"]["limitations"]
        )
        return "\n".join(lines) + "\n"
