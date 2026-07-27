from __future__ import annotations

import pytest

from src.models import BusinessFactLedgerSnapshot, canonical_sha256
from src.services.ai_representation_accuracy_service import (
    AIRepresentationAccuracyService,
)


SHA = canonical_sha256({"fixture": "ai-representation"})


def _ref(path: str, span: str) -> dict[str, str]:
    return {
        "artifact_ref": path,
        "reference_kind": "source_span",
        "exact_span": span,
    }


def _ledger(*facts: dict) -> BusinessFactLedgerSnapshot:
    return BusinessFactLedgerSnapshot(
        run_id="run-1",
        attempt_id="attempt-1",
        work_item_id="work-1",
        vertical_pack_version="national_bjj_registry.agentic.v1",
        source_sha256=SHA,
        facts=list(facts),
    )


def _fact(
    fact_id: str,
    name: str,
    value: object,
    *,
    status: str = "observed",
    sensitivity: str = "public",
    approval: str = "approved",
    observed_at: str | None = None,
) -> dict:
    payload = {
        "fact_id": fact_id,
        "name": name,
        "normalized_value": value,
        "source_status": status,
        "sensitivity_class": sensitivity,
        "approval_state": approval,
        "evidence_refs": [_ref(f"runs/run-1/{fact_id}.json", str(value))],
    }
    if observed_at:
        payload["observed_at"] = observed_at
    return payload


def test_reuses_context_compatible_rows_and_classifies_against_public_facts() -> None:
    ledger = _ledger(
        _fact("schedule", "class schedule", "Monday through Saturday"),
        _fact("program", "programs", "adult and kids BJJ"),
    )
    rows = [
        {
            "status": "complete",
            "raw_artifact_ref": "provider/response-1.json",
            "response_text": "Classes run Monday through Saturday.",
            "market": "Tacoma, WA",
            "location_code": 1027773,
            "language_code": "en",
            "device": "desktop",
        },
        {
            "status": "complete",
            "raw_artifact_ref": "provider/response-2.json",
            "response_text": "The academy has adult programs.",
            "market": "Tacoma, WA",
            "location_code": 1027773,
            "language_code": "en",
            "device": "desktop",
        },
        {
            "status": "complete",
            "raw_artifact_ref": "provider/response-3.json",
            "response_text": "The academy has no kids BJJ program.",
            "market": "Tacoma, WA",
            "location_code": 1027773,
            "language_code": "en",
            "device": "desktop",
        },
    ]

    snapshot = AIRepresentationAccuracyService().analyze(
        rows,
        ledger,
        context={
            "market": "Tacoma, WA",
            "location_code": 1027773,
            "language_code": "en",
            "device": "desktop",
        },
    )

    assert snapshot.completeness_percent == 100.0
    assert [claim["classification"] for claim in snapshot.claims] == [
        "correct",
        "incomplete",
        "contradicted",
    ]
    assert all(claim["response_evidence_ref"]["response_span"] for claim in snapshot.claims)
    assert all(claim["fact_evidence_refs"] for claim in snapshot.claims)
    assert snapshot.review_state == "needs_review"


def test_context_mismatch_and_unknown_facts_remain_unverifiable() -> None:
    ledger = _ledger(_fact("schedule", "class schedule", "Monday through Saturday"))
    rows = [
        {
            "status": "complete",
            "raw_artifact_ref": "provider/tacoma.json",
            "response_text": "Tuition is $100 per month.",
            "market": "Tacoma, WA",
        },
        {
            "status": "complete",
            "raw_artifact_ref": "provider/houston.json",
            "response_text": "Classes run Monday through Saturday.",
            "market": "Houston, TX",
        },
    ]
    snapshot = AIRepresentationAccuracyService().analyze(
        rows,
        ledger,
        context={"market": "Tacoma, WA"},
    )

    assert len(snapshot.claims) == 1
    assert snapshot.claims[0]["classification"] == "unverifiable"
    assert any("context" in item for item in snapshot.limitations)


def test_outdated_claim_uses_newer_ledger_observation() -> None:
    ledger = _ledger(
        _fact(
            "schedule",
            "class schedule",
            "Monday through Saturday",
            observed_at="2026-07-26",
        )
    )
    snapshot = AIRepresentationAccuracyService().analyze(
        [
            {
                "status": "complete",
                "raw_artifact_ref": "provider/old.json",
                "response_text": "The class schedule is Monday through Saturday.",
                "snapshot_date": "2026-07-01",
            }
        ],
        ledger,
    )
    assert snapshot.claims[0]["classification"] == "outdated"


def test_exact_response_spans_and_paid_collection_boundary() -> None:
    ledger = _ledger(_fact("schedule", "class schedule", "Monday through Saturday"))
    snapshot = AIRepresentationAccuracyService().analyze(
        [
            {
                "status": "complete",
                "raw_artifact_ref": "provider/response.json",
                "response_text": "Classes run Monday through Saturday.",
                "claims": [
                    {
                        "claim": "Classes run Monday through Saturday.",
                        "response_span": "Classes run Monday through Friday.",
                    }
                ],
            }
        ],
        ledger,
    )
    assert snapshot.claims == []
    assert any("exact provider span" in item for item in snapshot.limitations)

    with pytest.raises(RuntimeError, match="paid collection"):
        AIRepresentationAccuracyService().collect(
            [], ledger, provider=object(), allow_paid_api_calls=True
        )


def test_ineligible_public_facts_are_not_used_and_hash_is_validated() -> None:
    ledger = _ledger(
        _fact("private", "private note", "secret", sensitivity="private", approval="needs_review"),
        _fact("unknown", "tuition", "$100", status="unknown"),
    )
    snapshot = AIRepresentationAccuracyService().analyze(
        [
            {
                "status": "complete",
                "raw_artifact_ref": "provider/response.json",
                "response_text": "Tuition is $100.",
            }
        ],
        ledger,
    )
    assert snapshot.claims[0]["classification"] == "unverifiable"
    assert len(snapshot.source_sha256) == 64

    with pytest.raises(ValueError, match="SHA-256"):
        AIRepresentationAccuracyService().analyze(
            [], ledger, source_sha256="not-a-hash"
        )
