from __future__ import annotations

from pathlib import Path

import pytest

from src.models import RemediationBlueprintSnapshot, canonical_sha256
from src.services.remediation_blueprint_service import (
    BlueprintValidationError,
    RemediationBlueprintService,
)


SHA = canonical_sha256({"fixture": "remediation-blueprint"})


def ref(name: str = "pages/home.json", span: str = "The academy offers classes.") -> dict[str, str]:
    return {"artifact_ref": f"runs/run-1/{name}", "reference_kind": "source_span", "exact_span": span}


def candidate() -> dict:
    evidence = [ref()]
    return {
        "schema_version": "remediation-blueprint.v1",
        "target": {"name": "Nova Ryu", "url": "https://novaryu.com"},
        "title": "A clearer academy journey",
        "summary": "A compact after-state for program discovery and conversion.",
        "sitemap": [{"id": "programs", "title": "Programs", "status": "recommended", "evidence_refs": evidence}],
        "pages": [{"id": "programs-bjj", "title": "Programs page", "status": "recommended", "description": "Explain programs and next steps.", "evidence_refs": evidence}],
        "navigation": [{"id": "nav-programs", "label": "Programs", "destination": "/programs", "status": "recommended", "evidence_refs": evidence}],
        "answer_blocks": [{"id": "answer-start", "title": "What should a beginner expect?", "value": "unknown", "status": "unknown"}],
        "cta_flows": [{"id": "cta-trial", "title": "Book an intro", "destination": "unknown", "status": "recommended", "evidence_refs": evidence}],
        "schema_recommendations": [{"id": "schema-local", "title": "Align LocalBusiness facts", "status": "recommended", "evidence_refs": evidence}],
        "embeds": [{"id": "class-schedule", "title": "Vertical schedule embed", "status": "recommended", "evidence_refs": evidence}],
        "crm": {"id": "lead-routing", "title": "Route intro requests to CRM", "status": "recommended", "evidence_refs": evidence},
        "limitations": ["Actual class availability requires operator confirmation."],
    }


def snapshot(*, review_state: str = "needs_review", **overrides: object) -> RemediationBlueprintSnapshot:
    payload = candidate()
    payload.update(overrides.pop("blueprint", {}) if isinstance(overrides.get("blueprint"), dict) else {})
    service = RemediationBlueprintService()
    normalized = service.normalize(payload)
    fields = normalized["placeholder_fields"]
    kwargs = {
        "run_id": "run-1",
        "attempt_id": "attempt-1",
        "work_item_id": "work-blueprint",
        "mode": "prospect",
        "source_snapshot_ids": ["decision-1", "journey-1"],
        "source_sha256": SHA,
        "blueprint": normalized,
        "evidence_refs": [ref()],
        "review_state": review_state,
        "placeholder_fields": fields,
        "approved_by": "operator-1" if review_state == "approved" else None,
        "approved_at": "2026-07-26T00:00:00+00:00" if review_state == "approved" else None,
    }
    kwargs.update(overrides)
    return RemediationBlueprintSnapshot(**kwargs)


def test_blueprint_service_normalizes_sections_and_unknown_placeholders() -> None:
    result = RemediationBlueprintService().validate(snapshot())

    assert result["valid"] is True
    assert set(("sitemap", "navigation", "answer_blocks", "cta_flows", "schema_recommendations", "embeds", "crm")) <= set(result["blueprint"])
    assert any(path.endswith("answer_blocks[0].value") for path in result["placeholder_fields"])
    assert result["source_snapshot_ids"] == ["decision-1", "journey-1"]


def test_positive_items_require_evidence_and_code_is_not_accepted() -> None:
    service = RemediationBlueprintService()
    without_refs = candidate()
    without_refs["pages"] = [{"id": "p1", "title": "New page", "status": "recommended"}]
    with pytest.raises(BlueprintValidationError, match="requires evidence"):
        service.normalize(without_refs)

    with pytest.raises(BlueprintValidationError, match="executable"):
        service.normalize({"pages": [{"id": "p1", "status": "unknown", "html": "<main>no</main>"}]})


def test_renderer_input_and_review_gate_are_strict(tmp_path: Path) -> None:
    from src.services.remediation_blueprint_service import OfflinePrototypeRenderer, PrototypeSafetyError

    renderer = OfflinePrototypeRenderer(tmp_path)
    with pytest.raises(BlueprintValidationError, match="approved"):
        renderer.render(snapshot())
    with pytest.raises(BlueprintValidationError, match="RemediationBlueprintSnapshot"):
        renderer.render({"blueprint": candidate()})  # type: ignore[arg-type]

    with pytest.raises(PrototypeSafetyError, match="published"):
        renderer.publish()

