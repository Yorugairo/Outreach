from __future__ import annotations

import pytest

from src.models import (
    BusinessEconomicsProfile,
    DemandEvidenceRow,
    DemandEvidenceSet,
    DemandGroup,
)
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.opportunity_model_service import OpportunityModelService
from src.vertical_packs import get_vertical_pack


def _demand() -> DemandEvidenceSet:
    rows = [
        DemandEvidenceRow(
            keyword="bjj tacoma",
            market="Tacoma, WA",
            source="operator_csv",
            snapshot_period="2026-07",
            match_semantics="close_variants",
            monthly_searches=1000,
        ),
        DemandEvidenceRow(
            keyword="nova ryu tacoma",
            market="Tacoma, WA",
            source="operator_csv",
            snapshot_period="2026-07",
            match_semantics="close_variants",
            monthly_searches=500,
            brand_demand=True,
        ),
    ]
    groups = [
        DemandGroup(
            intent_family="bjj_classes",
            included_keyword_ids=[rows[0].id],
            representative_term=rows[0].keyword,
            aggregation_rule="max_close_variant",
            approved_monthly_search_occasions=1000,
            reviewer="operator",
            rationale="Reviewed local class intent.",
            status="approved",
        ),
        DemandGroup(
            intent_family="brand",
            included_keyword_ids=[rows[1].id],
            representative_term=rows[1].keyword,
            aggregation_rule="max_close_variant",
            approved_monthly_search_occasions=500,
            reviewer="operator",
            rationale="Brand demand is reported separately.",
            is_brand=True,
            status="approved",
        ),
    ]
    return DemandEvidenceSet(
        prospect_id="prospect-1",
        keyword_set_id="keywords-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        source_sha256="a" * 64,
        rows=[row.to_dict() for row in rows],
        groups=[group.to_dict() for group in groups],
        state="approved",
        approved_by="operator",
        approved_at="2026-07-25T00:00:00+00:00",
    )


def _economics(*, vertical_id="national_bjj_registry"):
    return BusinessEconomicsProfile(
        prospect_id="prospect-1",
        vertical_id=vertical_id,
        revenue_model="membership" if vertical_id == "national_bjj_registry" else "won_job",
        monthly_price=100,
        currency="USD",
        capacity_headroom=20,
        field_provenance={
            "monthly_price": "business_supplied",
            "capacity_headroom": "business_supplied",
        },
        state="approved",
        approved_by="operator",
        approved_at="2026-07-25T00:00:00+00:00",
    )


def _assumptions(*, reviewed=True):
    raw = {
        "low": [2.5, 0.10, 0.05, 0.5, 0.30, 0.70, 0.40, 12],
        "base": [2.0, 0.20, 0.10, 0.5, 0.40, 0.80, 0.50, 12],
        "high": [1.5, 0.30, 0.15, 0.4, 0.50, 0.85, 0.60, 12],
    }
    names = OpportunityModelService.MATERIAL_ASSUMPTIONS
    return {
        band: {
            name: {
                "value": value,
                "provenance": "assumed",
                "reviewed": reviewed,
            }
            for name, value in zip(names, values)
        }
        for band, values in raw.items()
    }


def test_nova_formula_excludes_brand_and_clamps_capacity_with_ramp():
    scenario = OpportunityModelService().create_scenario(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        economics=_economics(),
        demand=_demand(),
        assumptions=_assumptions(),
    )

    assert scenario.status == "complete"
    assert scenario.outputs["base"]["monthly_nonbrand_search_occasions"] == 1000
    assert scenario.outputs["base"]["modeled_unique_prospects"] == 500
    assert scenario.outputs["base"]["incremental_visits"] == 125
    assert scenario.outputs["base"]["capacity_adjusted_active_customers"] == 20
    assert scenario.outputs["base"]["ending_mrr"] == 2000
    assert scenario.outputs["base"]["annual_run_rate"] == 24000
    assert scenario.outputs["base"]["first_year_ramp_revenue"] == 12000
    assert all(
        output["capacity_adjusted_active_customers"] <= 20
        for output in scenario.outputs.values()
    )


def test_missing_demand_suppresses_acquisition_but_keeps_capacity_ceiling():
    scenario = OpportunityModelService().create_scenario(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        economics=_economics(),
        demand=None,
        assumptions=_assumptions(),
    )

    assert scenario.status == "limited"
    assert scenario.outputs == {}
    assert scenario.sensitivity["capacity_ceiling"] == {
        "active_customers": 20,
        "mrr": 2000,
        "annual_run_rate": 24000,
        "label": "Capacity ceiling, not promised ranking revenue",
    }


def test_unreviewed_numeric_assumptions_are_partial_and_cannot_be_approved(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    service = OpportunityModelService(repository)
    scenario = service.create_scenario(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        economics=_economics(),
        demand=_demand(),
        assumptions=_assumptions(reviewed=False),
    )
    assert scenario.status == "partial"
    assert scenario.outputs
    with pytest.raises(ValueError, match="complete"):
        service.approve_scenario(scenario.id, operator="operator")


def test_complete_scenario_approval_creates_immutable_successor(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    service = OpportunityModelService(repository)
    scenario = service.create_scenario(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        economics=_economics(),
        demand=_demand(),
        assumptions=_assumptions(),
    )
    approved = service.approve_scenario(scenario.id, operator="operator")
    assert approved.id != scenario.id
    assert approved.predecessor_id == scenario.id
    assert approved.state == "approved"
    assert repository.get_opportunity_scenario(scenario.id).state == "draft"


def test_vertical_packs_define_same_four_stage_shape_for_trades_and_bjj():
    assert get_vertical_pack("national_bjj_registry.v1").service_taxonomy[
        "funnel_stages"
    ] == ["visit", "signup", "attended_trial", "member"]
    assert get_vertical_pack("one_trade_network.v1").service_taxonomy[
        "funnel_stages"
    ] == ["visit", "lead", "qualified_appointment", "won_job"]
