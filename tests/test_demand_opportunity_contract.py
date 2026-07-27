from __future__ import annotations

import pytest

from src.models import (
    DEMAND_AGGREGATION_RULES,
    FORECAST_DISCLAIMER,
    OPPORTUNITY_FORMULA_VERSION,
    AcquisitionCalibrationRecord,
    BusinessEconomicsProfile,
    DemandEvidenceRow,
    DemandEvidenceSet,
    DemandGroup,
    MarketEvidenceCompleteness,
    MarketEvidenceRun,
    OpportunityScenario,
    ProviderCallRecord,
)


def _row(*, keyword: str = "bjj tacoma", monthly_searches: float = 100) -> DemandEvidenceRow:
    return DemandEvidenceRow(
        keyword=keyword,
        market="Tacoma, WA",
        source="google_keyword_planner_csv",
        snapshot_period="2026-07",
        match_semantics="close_variants",
        monthly_searches=monthly_searches,
        evidence_ref={"artifact_path": "imports/demand.csv", "row": 2},
    )


def _group(row: DemandEvidenceRow, *, is_brand: bool = False) -> DemandGroup:
    return DemandGroup(
        intent_family="brand" if is_brand else "bjj_classes",
        included_keyword_ids=[row.id],
        representative_term=row.keyword,
        aggregation_rule="max_close_variant",
        approved_monthly_search_occasions=row.monthly_searches,
        reviewer="operator@example.test",
        rationale="Close variants share one intent and one landing page.",
        is_brand=is_brand,
        status="approved",
    )


def _economics(*, vertical_id: str = "national_bjj_registry") -> BusinessEconomicsProfile:
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
        funnel_labels=(
            ["visit", "signup", "attended_trial", "member"]
            if vertical_id == "national_bjj_registry"
            else ["visit", "lead", "qualified_appointment", "won_job"]
        ),
        state="approved",
        approved_by="operator@example.test",
        approved_at="2026-07-25T00:00:00+00:00",
    )


def test_contract_constants_freeze_truth_semantics() -> None:
    assert OPPORTUNITY_FORMULA_VERSION == "opportunity-formula.v1"
    assert FORECAST_DISCLAIMER == "Forecast, not guarantee"
    assert DEMAND_AGGREGATION_RULES == {
        "provider_grouped",
        "max_close_variant",
        "sum_distinct_intents",
    }


def test_provider_call_and_required_evidence_completeness_are_separate() -> None:
    failed = ProviderCallRecord(
        provider="dataforseo",
        operation="organic_serp",
        query_target="bjj tacoma",
        context={"location_code": 1027773, "device": "desktop"},
        status="failed",
        failure_class="balance_payment",
        retryable=False,
        actual_cost=0.01,
    )
    assert failed.to_dict()["failure_class"] == "balance_payment"

    incomplete = MarketEvidenceCompleteness(
        expected={"organic_serp": 2},
        successful={"organic_serp": 1},
        unresolved={"organic_serp": 1},
        inapplicable={"organic_serp": 0},
        reused={"organic_serp": 0},
    )
    assert incomplete.is_complete is False
    with pytest.raises(ValueError, match="unresolved required work"):
        MarketEvidenceRun(
            insight_run_id="run-1",
            insight_attempt_id="attempt-1",
            keyword_set_id="keywords-1",
            keyword_set_version="v1",
            target_domain="novaryu.com",
            state="complete",
            provider_contract_version="provider-calls.v1",
            provider_completeness=incomplete.to_dict(),
        )


def test_legacy_market_runs_do_not_require_new_provider_fields() -> None:
    legacy = MarketEvidenceRun(
        insight_run_id="run-1",
        insight_attempt_id="attempt-1",
        keyword_set_id="keywords-1",
        keyword_set_version="v1",
        target_domain="novaryu.com",
        provider_calls=[{"status": "completed", "operation": "legacy"}],
    )
    assert legacy.provider_contract_version is None
    assert legacy.provider_completeness == {}


def test_demand_contract_models_search_occasions_and_reviewed_groups() -> None:
    row = _row()
    group = _group(row)
    evidence = DemandEvidenceSet(
        prospect_id="prospect-1",
        keyword_set_id="keywords-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        location_code=1027773,
        source_sha256="a" * 64,
        source="google_keyword_planner_csv",
        snapshot_period="2026-07",
        rows=[row.to_dict()],
        groups=[group.to_dict()],
        state="approved",
        approved_by="operator@example.test",
        approved_at="2026-07-25T00:00:00+00:00",
    )
    assert evidence.groups[0]["approved_monthly_search_occasions"] == 100
    assert evidence.groups[0]["is_brand"] is False

    with pytest.raises(ValueError, match="explicit operator approval"):
        DemandGroup(
            intent_family="mixed",
            included_keyword_ids=[row.id],
            representative_term=row.keyword,
            aggregation_rule="sum_distinct_intents",
            approved_monthly_search_occasions=100,
        )


def test_nova_capacity_ceiling_is_executable_without_a_demand_forecast() -> None:
    economics = _economics()
    assert economics.capacity_mrr == 2_000
    assert economics.capacity_annual_run_rate == 24_000

    scenario = OpportunityScenario(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        demand_evidence_set_id=None,
        demand_evidence_version=None,
        economics_profile_id=economics.id,
        economics_profile_version=economics.version,
        assumptions={"low": {}, "base": {}, "high": {}},
        outputs={},
        status="limited",
        completeness_percent=25,
        warnings=["Demand evidence is required before acquisition projections."],
    )
    assert scenario.to_dict()["forecast_label"] == FORECAST_DISCLAIMER
    assert scenario.outputs == {}


def test_opportunity_approval_requires_complete_reviewed_model() -> None:
    economics = _economics()
    with pytest.raises(ValueError, match="must be complete"):
        OpportunityScenario(
            insight_run_id="run-1",
            prospect_id="prospect-1",
            demand_evidence_set_id="demand-1",
            demand_evidence_version=1,
            economics_profile_id=economics.id,
            economics_profile_version=1,
            assumptions={"low": {}, "base": {}, "high": {}},
            outputs={"low": {}, "base": {}, "high": {}},
            status="partial",
            state="approved",
            approved_by="operator@example.test",
            approved_at="2026-07-25T00:00:00+00:00",
        )


def test_calibration_contract_accepts_aggregate_counts_and_rejects_negatives() -> None:
    record = AcquisitionCalibrationRecord(
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        source="ga4_csv",
        period_start="2026-06-01",
        period_end="2026-06-30",
        total_users=100,
        signups_or_leads=10,
        new_customers=3,
        artifact_ref={"artifact_path": "calibration/ga4.csv"},
    )
    assert record.to_dict()["total_users"] == 100
    with pytest.raises(ValueError, match="cannot be negative"):
        AcquisitionCalibrationRecord(
            prospect_id="prospect-1",
            vertical_id="one_trade_network",
            market="Tacoma, WA",
            source="crm_csv",
            period_start="2026-06-01",
            period_end="2026-06-30",
            new_customers=-1,
            artifact_ref={"artifact_path": "calibration/crm.csv"},
        )


def test_trade_vertical_uses_same_economics_contract_with_different_funnel() -> None:
    trades = _economics(vertical_id="one_trade_network")
    assert trades.funnel_labels == [
        "visit",
        "lead",
        "qualified_appointment",
        "won_job",
    ]
