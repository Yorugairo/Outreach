from __future__ import annotations

import pytest

from src.models import (
    BusinessEconomicsProfile,
    DemandEvidenceRow,
    DemandEvidenceSet,
    DemandGroup,
    OwnedMeasurementSnapshot,
)
from src.services.demand_conversion_service import DemandConversionService


SHA = "b" * 64


def _demand(volume: float = 200) -> DemandEvidenceSet:
    row = DemandEvidenceRow(
        id="row-1",
        keyword="bjj tacoma",
        market="Tacoma, WA",
        source="keyword_planner_csv",
        snapshot_period="2026-07",
        match_semantics="close_variant",
        monthly_searches=volume,
    )
    group = DemandGroup(
        id="group-1",
        intent_family="primary",
        included_keyword_ids=[row.id],
        representative_term=row.keyword,
        aggregation_rule="max_close_variant",
        approved_monthly_search_occasions=volume,
        reviewer="operator",
        rationale="Reviewed close-variant family.",
        status="approved",
    )
    return DemandEvidenceSet(
        id="demand-1",
        prospect_id="prospect-1",
        keyword_set_id="keyword-set-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        source_sha256=SHA,
        rows=[row.to_dict()],
        groups=[group.to_dict()],
        state="approved",
        approved_by="operator",
        approved_at="2026-07-26T12:00:00+00:00",
    )


def _economics(capacity: float = 20) -> BusinessEconomicsProfile:
    return BusinessEconomicsProfile(
        id="economics-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        revenue_model="membership",
        monthly_price=100,
        currency="USD",
        capacity_headroom=capacity,
        field_provenance={
            "monthly_price": "business_supplied",
            "capacity_headroom": "business_supplied",
        },
        state="approved",
        approved_by="operator",
        approved_at="2026-07-26T12:00:00+00:00",
    )


def _snapshot(
    snapshot_id: str,
    source: str,
    metrics: dict[str, float | int],
) -> OwnedMeasurementSnapshot:
    return OwnedMeasurementSnapshot(
        id=snapshot_id,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        source=source,
        period_start="2026-04-01",
        period_end="2026-06-30",
        source_sha256=SHA,
        context={"market": "Tacoma, WA"},
        metrics=metrics,
        artifact_ref=f"owned/{snapshot_id}.json",
    )


def _assumptions(*, include_rates: bool) -> dict:
    capture = {"low": 0.05, "base": 0.10, "high": 0.20}
    output = {
        band: {"organic_visit_capture_rate": rate}
        for band, rate in capture.items()
    }
    if include_rates:
        for values in output.values():
            values.update(
                {
                    "lead_rate": 0.10,
                    "booking_rate": 0.80,
                    "close_rate": 0.50,
                }
            )
    return output


def _public_source() -> dict:
    return {
        "source_name": "public_serp_sample",
        "source_class": "public_observed",
        "hierarchy_level": 4,
        "provenance_label": "observed",
        "source_sha256": SHA,
        "artifact_ref": "market/organic-1.json",
        "snapshot_date": "2026-07-26",
    }


def test_prospect_mode_uses_assumptions_and_capacity_aware_formula() -> None:
    evidence = DemandConversionService().build(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=_demand(),
        economics=_economics(),
        assumptions=_assumptions(include_rates=True),
        public_sources=[_public_source()],
        search_alignment={
            "groups": [
                {
                    "intent_family": "primary",
                    "ranking_observations": [{"position": 12}],
                }
            ]
        },
    )

    assert evidence.mode == "prospect"
    assert evidence.status == "complete"
    assert evidence.modeled_outputs["base"] == {
        "provenance_label": "modeled",
        "monthly_search_occasions": 200,
        "incremental_qualified_visits": 20,
        "incremental_leads": 2,
        "incremental_bookings": 1.6,
        "unconstrained_members": 0.8,
        "incremental_members": 0.8,
        "capacity_constrained": False,
        "incremental_recurring_revenue": 80,
        "annual_run_rate": 960,
        "currency": "USD",
        "formula_version": "demand-conversion-formula.v1",
    }
    assert all(
        source["source_class"] != "owner_first_party"
        for source in evidence.source_snapshots
    )


def test_owner_verified_mode_replaces_funnel_assumptions_with_observed_rates() -> None:
    owner = [
        _snapshot("gsc-1", "gsc_csv", {"impressions": 500, "clicks": 50}),
        _snapshot("ga4-1", "ga4_csv", {"sessions": 100, "users": 80}),
        _snapshot(
            "crm-1",
            "crm_csv",
            {"signups": 10, "appointments": 8, "customers": 4},
        ),
    ]
    evidence = DemandConversionService().build(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        mode="owner_verified",
        demand=_demand(),
        economics=_economics(),
        owner_snapshots=owner,
        assumptions=_assumptions(include_rates=False),
    )

    by_name = {
        (row["band"], row["name"]): row for row in evidence.assumptions
    }
    assert by_name[("base", "lead_rate")] == {
        "band": "base",
        "name": "lead_rate",
        "value": 0.1,
        "provenance_label": "observed",
    }
    assert by_name[("base", "booking_rate")]["value"] == 0.8
    assert by_name[("base", "close_rate")]["value"] == 0.5
    assert evidence.modeled_outputs["base"]["incremental_members"] == 0.8
    assert any(
        source["source_class"] == "owner_first_party"
        for source in evidence.source_snapshots
    )


def test_unknown_inputs_suppress_projections_instead_of_becoming_zero() -> None:
    evidence = DemandConversionService().build(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=_demand(),
        economics=_economics(),
        assumptions={},
    )

    assert evidence.modeled_outputs == {}
    assert evidence.status == "partial"
    assert any(
        check["check_id"] == "funnel_rates" and check["status"] == "unknown"
        for check in evidence.observed_inputs["completeness_checks"]
    )


def test_capacity_caps_members_and_revenue() -> None:
    evidence = DemandConversionService().build(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=_demand(10_000),
        economics=_economics(capacity=20),
        assumptions={
            band: {
                "organic_visit_capture_rate": 1,
                "lead_rate": 1,
                "booking_rate": 1,
                "close_rate": 1,
            }
            for band in ("low", "base", "high")
        },
    )

    assert evidence.modeled_outputs["base"]["unconstrained_members"] == 10_000
    assert evidence.modeled_outputs["base"]["incremental_members"] == 20
    assert evidence.modeled_outputs["base"]["incremental_recurring_revenue"] == 2_000
    assert evidence.modeled_outputs["base"]["capacity_constrained"] is True


def test_mode_and_context_gates_fail_closed() -> None:
    with pytest.raises(ValueError, match="requires owner measurements"):
        DemandConversionService().build(
            insight_run_id="run-1",
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            market="Tacoma, WA",
            mode="owner_verified",
            demand=_demand(),
            economics=_economics(),
        )

    with pytest.raises(ValueError, match="cannot consume owner"):
        DemandConversionService().build(
            insight_run_id="run-1",
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            market="Tacoma, WA",
            demand=_demand(),
            economics=_economics(),
            owner_snapshots=[
                _snapshot("gsc-1", "gsc_csv", {"impressions": 10})
            ],
        )
