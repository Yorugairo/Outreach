from __future__ import annotations

from src.models import (
    BusinessEconomicsProfile,
    DemandEvidenceRow,
    DemandEvidenceSet,
    DemandGroup,
)
from src.services.opportunity_model_service import OpportunityModelService
from src.services.opportunity_reporting_service import (
    OpportunityReportingService,
)
from src.services.outreach_service import OutreachService
from tests.test_opportunity_model import _assumptions
from tests.test_revenue_services import _repo_with_run


def _approved_inputs(repository, prospect):
    row = DemandEvidenceRow(
        keyword="plumber austin",
        market="Austin, TX",
        source="operator_csv",
        snapshot_period="2026-07",
        match_semantics="close_variants",
        monthly_searches=500,
    )
    group = DemandGroup(
        intent_family="plumbing_repair",
        included_keyword_ids=[row.id],
        representative_term=row.keyword,
        aggregation_rule="max_close_variant",
        approved_monthly_search_occasions=500,
        reviewer="operator",
        rationale="Reviewed repair-intent close variants.",
        status="approved",
    )
    demand = repository.save_demand_evidence_set(
        DemandEvidenceSet(
            prospect_id=prospect.id,
            keyword_set_id="keywords-trade-1",
            vertical_id="one_trade_network",
            market="Austin, TX",
            source_sha256="a" * 64,
            rows=[row.to_dict()],
            groups=[group.to_dict()],
            state="approved",
            approved_by="operator",
            approved_at="2026-07-25T00:00:00+00:00",
        )
    )
    economics = repository.save_business_economics_profile(
        BusinessEconomicsProfile(
            prospect_id=prospect.id,
            vertical_id="one_trade_network",
            revenue_model="won_job",
            monthly_price=500,
            currency="USD",
            capacity_headroom=10,
            field_provenance={
                "monthly_price": "business_supplied",
                "capacity_headroom": "business_supplied",
            },
            state="approved",
            approved_by="operator",
            approved_at="2026-07-25T00:00:00+00:00",
        )
    )
    return demand, economics


def _approved_scenario(repository, run, prospect):
    demand, economics = _approved_inputs(repository, prospect)
    service = OpportunityModelService(repository)
    draft = service.create_scenario(
        insight_run_id=run.id,
        prospect_id=prospect.id,
        economics=economics,
        demand=demand,
        assumptions=_assumptions(),
    )
    return service.approve_scenario(draft.id, operator="operator")


def test_opportunity_v1_and_v4_are_labeled_and_scenario_scoped(tmp_path):
    repository, artifact_root, run, prospect = _repo_with_run(tmp_path)
    scenario = _approved_scenario(repository, run, prospect)

    reports = OpportunityReportingService(repository).assemble(scenario.id)

    opportunity = reports["opportunity-v1"]
    combined = reports["v4"]
    assert opportunity.report_payload["forecast_label"] == "Forecast, not guarantee"
    assert opportunity.report_payload["demand"]["semantics"] == (
        "Monthly search occasions, not unique people"
    )
    assert opportunity.report_payload["potential_if_assumptions_hold"]["label"] == "modeled"
    assert opportunity.report_payload["verified_now"]["label"] == "observed"
    assert combined.report_payload["report_contract"] == "v4"
    assert combined.report_payload["opportunity_scenario_id"] == scenario.id
    scoped = (
        artifact_root
        / "runs"
        / run.id
        / "opportunity"
        / scenario.id
        / "reports"
    )
    assert (scoped / "opportunity-v1.json").exists()
    assert (scoped / "opportunity-v1.md").exists()
    assert (scoped / "v4.json").exists()
    assert (scoped / "v4.md").exists()


def test_v4_pitch_revalidates_approved_scenario_and_keeps_revenue_out_of_opener(
    tmp_path,
):
    repository, artifact_root, run, prospect = _repo_with_run(tmp_path)
    scenario = _approved_scenario(repository, run, prospect)
    OpportunityReportingService(repository).assemble(scenario.id)
    service = OutreachService(repository, artifact_root=artifact_root)

    package = service.create_package(
        insight_run_id=run.id,
        prospect_id=prospect.id,
        report_version="v4",
    )

    assert package.opportunity_scenario_id == scenario.id
    assert "## Modeled commercial opportunity" in package.evidence_brief
    assert "Forecast, not guarantee" in package.evidence_brief
    assert "MRR" not in package.email_body
    assert "$" not in package.email_body
    approved = service.approve_package(
        package.id,
        operator="operator",
        acknowledge_partial_ai=True,
    )
    exported = service.export_package(approved.id)
    assert exported["json"]["opportunity_scenario_id"] == scenario.id
    assert exported["json"]["opportunity_snapshot_sha256"]
