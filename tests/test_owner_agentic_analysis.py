from __future__ import annotations

import pytest

from src.models import (
    AgenticWorkItem,
    OwnedMeasurementSnapshot,
    canonical_sha256,
)
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.owner_agentic_analysis_service import OwnerAgenticAnalysisService


CONSENT = {
    "confirmed": True,
    "operator": "operator-1",
    "confirmed_at": "2026-07-26T12:00:00Z",
}
CONSENT_ID = canonical_sha256(CONSENT)
SHA = canonical_sha256({"owner": "source"})


def owned_snapshot(**overrides: object) -> OwnedMeasurementSnapshot:
    payload: dict[str, object] = {
        "prospect_id": "prospect-1",
        "vertical_id": "national_bjj_registry",
        "source": "ga4_csv",
        "period_start": "2026-06-01",
        "period_end": "2026-06-30",
        "source_sha256": SHA,
        "context": {
            "owner_verified": True,
            "owner_consent": CONSENT,
            "data_freshness": {
                "status": "fresh",
                "snapshot_date": "2026-06-30",
            },
            "property_id": "property-1",
        },
        "metrics": {"sessions": 1200, "trial_submissions": 18},
        "artifact_ref": "owned/ga4/property-1.json",
    }
    payload.update(overrides)
    return OwnedMeasurementSnapshot(**payload)


def owner_work_item(**overrides: object) -> AgenticWorkItem:
    payload: dict[str, object] = {
        "run_id": "run-1",
        "attempt_id": "attempt-1",
        "evidence_pack_id": "owner-pack-1",
        "vertical_pack_version": "national_bjj_registry.agentic.v1",
        "work_kind": "owner_diagnostic",
        "mode": "owner_verified",
        "consent_id": CONSENT_ID,
        "source_sha256": SHA,
        "idempotency_key": "owner:run-1:v1",
        "requested_runtime": "hermes",
        "requested_provider": "openrouter",
        "requested_model": "deepseek/deepseek-v4-flash",
        "prompt_version": "owner.v1",
        "rubric_version": "owner.v1",
        "schema_version": "owner.v1",
    }
    payload.update(overrides)
    return AgenticWorkItem(**payload)


def test_owner_pack_uses_only_consented_aggregate_snapshots(tmp_path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    source = repository.save_owned_measurement_snapshot(owned_snapshot())
    service = OwnerAgenticAnalysisService(repository)

    preflight = service.preflight(
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        approved_snapshot_ids=[source.id],
        consent_id=CONSENT_ID,
    )
    pack = service.build_evidence_pack(
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        approved_snapshot_ids=[source.id],
        consent_id=CONSENT_ID,
    )

    assert preflight["aggregate_only"] is True
    assert pack["privacy_scope"] == "private_owner_only"
    assert pack["sources"][0]["metrics"] == {
        "sessions": 1200,
        "trial_submissions": 18,
    }
    assert "owner_consent" not in pack["sources"][0]["context"]


def test_owner_diagnostic_resolves_metric_fields_and_never_exports_to_prospect(tmp_path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    source = repository.save_owned_measurement_snapshot(owned_snapshot())
    work = owner_work_item()
    repository.save_agentic_work_item(work)
    service = OwnerAgenticAnalysisService(repository)
    snapshot = service.create_snapshot(
        work_item=work,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        approved_snapshot_ids=[source.id],
        observations=[
            {
                "id": "sessions-observed",
                "text": "The approved GA4 export records 1,200 sessions.",
                "evidence_refs": [
                    {"snapshot_id": source.id, "field_path": "metrics.sessions"}
                ],
            }
        ],
        hypotheses=[
            {
                "id": "trial-friction",
                "text": "The gap between sessions and trial submissions is a funnel hypothesis.",
                "evidence_refs": [
                    {
                        "snapshot_id": source.id,
                        "field_path": "metrics.trial_submissions",
                    }
                ],
            }
        ],
    )

    assert snapshot.privacy_scope == "private_owner_only"
    assert snapshot.hypotheses[0]["inference"] is True
    assert service.client_payload(snapshot, requested_mode="owner_verified")["id"] == snapshot.id
    with pytest.raises(ValueError, match="cannot enter prospect"):
        service.client_payload(snapshot, requested_mode="prospect")


def test_owner_analysis_rejects_scope_consent_staleness_and_causal_claims(tmp_path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    source = repository.save_owned_measurement_snapshot(owned_snapshot())
    service = OwnerAgenticAnalysisService(repository)
    with pytest.raises(ValueError, match="consent identity"):
        service.preflight(
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            approved_snapshot_ids=[source.id],
            consent_id="different-consent",
        )

    stale = owned_snapshot(
        source_sha256=canonical_sha256({"stale": True}),
        context={
            "owner_verified": True,
            "owner_consent": CONSENT,
            "data_freshness": {"status": "stale", "snapshot_date": "2024-01-01"},
        },
    )
    repository.save_owned_measurement_snapshot(stale)
    with pytest.raises(ValueError, match="stale"):
        service.preflight(
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            approved_snapshot_ids=[stale.id],
            consent_id=CONSENT_ID,
        )

    work = owner_work_item()
    repository.save_agentic_work_item(work)
    with pytest.raises(ValueError, match="causality"):
        service.create_snapshot(
            work_item=work,
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            approved_snapshot_ids=[source.id],
            observations=[],
            hypotheses=[
                {
                    "id": "causal",
                    "text": "The landing page caused 18 trial submissions.",
                    "evidence_refs": [
                        {
                            "snapshot_id": source.id,
                            "field_path": "metrics.trial_submissions",
                        }
                    ],
                }
            ],
        )
