from __future__ import annotations

from pathlib import Path

from src.config import AgenticAnalysisSettings
from src.models import InsightRun, ProspectRecord, SEOTarget, SiteEvidencePack
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.agentic_journey_service import (
    BrowserCandidateAction,
    JourneyActionPolicy,
)
from src.services.vertical_agentic_evidence_service import (
    VerticalAgenticEvidenceService,
)
from src.vertical_agentic_packs import list_vertical_agentic_packs


PILOTS = (
    {
        "name": "Nova Ryu",
        "domain": "novaryu.test",
        "category": "bjj_academy",
        "location": "Tacoma, WA",
        "vertical_id": "national_bjj_registry",
        "vertical_pack_version": "national_bjj_registry.v1",
        "agentic_pack_version": "national_bjj_registry.agentic.v1",
    },
    {
        "name": "Lacey Glass",
        "domain": "laceyglass.test",
        "category": "glazier",
        "location": "Lacey, WA",
        "vertical_id": "one_trade_network",
        "vertical_pack_version": "one_trade_network.v1",
        "agentic_pack_version": "one_trade_network.agentic.v1",
    },
)


def test_two_vertical_frozen_pilot_queues_bounded_non_provider_work(tmp_path: Path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    for pack in list_vertical_agentic_packs():
        repository.save_vertical_agentic_pack(pack)
    service = VerticalAgenticEvidenceService(
        repository,
        settings=AgenticAnalysisSettings(
            enabled=True,
            operator_approved=True,
            promotion_approved=True,
        ),
    )

    for index, fixture in enumerate(PILOTS, start=1):
        target = repository.upsert_target(
            SEOTarget(
                input_url=f"https://{fixture['domain']}",
                normalized_url=f"https://{fixture['domain']}/",
                normalized_domain=fixture["domain"],
            )
        )
        run = repository.create_run(
            InsightRun(
                id=f"pilot-run-{index}",
                seo_target_id=target.id,
                requested_url=target.normalized_url,
                requested_domain=target.normalized_domain,
                status="completed",
                current_stage="completed",
            )
        )
        repository.save_prospect(
            ProspectRecord(
                id=f"pilot-prospect-{index}",
                business_name=fixture["name"],
                website_url=target.normalized_url,
                normalized_domain=target.normalized_domain,
                category=fixture["category"],
                location=fixture["location"],
                contact_route=f"{target.normalized_url}contact",
                source_provenance="frozen_pilot_fixture",
                vertical_pack_version=fixture["vertical_pack_version"],
                vertical_id=fixture["vertical_id"],
                qualification_status="qualified",
            )
        )
        evidence_pack = repository.save_site_evidence_pack(
            SiteEvidencePack(
                id=f"pilot-pack-{index}",
                run_id=run.id,
                attempt_id=run.attempt_id,
                source_snapshot_ids={},
                source_hashes={},
                target_facts={
                    "business_name": fixture["name"],
                    "location": fixture["location"],
                },
                page_facts=[],
                deterministic_surfaces={},
                evidence_refs=[],
                vertical_pack_version=fixture["vertical_pack_version"],
                limitations=["Frozen pilot fixture: no live URL or provider work."],
            )
        )

        preflight = service.preflight(
            run.id,
            evidence_pack=evidence_pack,
            execution_mode="automatic",
        )
        work_items = service.enqueue_defaults(evidence_pack)
        prospect_view = service.evidence(run.id, mode="prospect")

        assert preflight["available"] is True
        assert preflight["provider_calls"] == 0
        assert preflight["provider_cost_usd"] == 0
        assert preflight["max_inference_cost_usd"] == 0.25
        assert preflight["vertical_agentic_pack_version"] == fixture[
            "agentic_pack_version"
        ]
        assert len(work_items) == 5
        assert sum(item.max_cost_usd for item in work_items) == 0.25
        assert len([item for item in work_items if item.work_kind == "target_journey"]) == 3
        assert prospect_view["owner_diagnostics"] == []


def test_pilot_action_policy_fails_closed_for_form_and_unknown_host() -> None:
    form_action = BrowserCandidateAction(
        id="form-submit",
        action_kind="activate_candidate",
        label="Submit enrollment",
        role="button",
        mutates_state=True,
        enters_data=True,
    )
    external = BrowserCandidateAction(
        id="external-action",
        action_kind="navigate_candidate",
        label="Continue elsewhere",
        role="link",
        destination_url="https://unknown-action-host.test/start",
    )

    assert JourneyActionPolicy.evaluate(
        form_action,
        allowed_hosts={"novaryu.test"},
    )[0] == "blocked"
    assert JourneyActionPolicy.evaluate(
        external,
        allowed_hosts={"novaryu.test"},
    )[0] == "needs_approval"

