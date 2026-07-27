from __future__ import annotations

import json
from pathlib import Path

from src.models import ReportSnapshot, canonical_sha256
from src.services.client_report_service import ClientReportService


def test_client_bundle_is_offline_deterministic_and_filters_unsafe_findings(tmp_path: Path) -> None:
    artifact_root = tmp_path / "artifacts"
    payload_ref = "runs/run-1/reports/snapshot.json"
    payload = {
        "normalized_domain": "example.test",
        "headline": "Evidence-backed report",
        "executive_summary": "A bounded summary.",
        "technical_seo_health": {"score": 82, "status": "complete"},
        "assets": [{"artifact_path": "runs/run-1/screenshots/home.png", "sha256": ""}],
    }
    payload_path = artifact_root / Path(*payload_ref.split("/"))
    payload_path.parent.mkdir(parents=True)
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    image = artifact_root / "runs/run-1/screenshots/home.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"png-bytes")
    evidence = artifact_root / "runs/run-1/pages/page-1.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text(
        json.dumps({"attempt_id": "attempt-1", "title": ""}),
        encoding="utf-8",
    )
    payload["assets"][0]["sha256"] = __import__("hashlib").sha256(image.read_bytes()).hexdigest()
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    snapshot = ReportSnapshot(
        id="snapshot-1", run_id="run-1", attempt_id="attempt-1", report_contract="operator-v5",
        schema_version=1, source_snapshot_ids={"seo": "seo-1"}, source_hashes={"seo": "a" * 64},
        renderer_version="operator-renderer.v1", payload_sha256=canonical_sha256(payload),
        payload_artifact_ref=payload_ref, completeness_percent=90, status="complete",
        created_at="2026-07-26T00:00:00+00:00",
    )
    assessment = {
        "id": "assessment-1", "runtime": "hermes", "requested_model": "deepseek",
        "served_provider": "openrouter", "served_model": "deepseek", "validation_result": {"customer_safe": False},
        "findings": [
            {
                "id": "safe",
                "claim_type": "observed",
                "title": "Missing title",
                "claim": "Improve the title.",
                "confidence": "high",
                "severity": "medium",
                "commercial_relevance": "The search result can be clearer.",
                "service_fit": [],
                "customer_safe": True,
                "review_reason": None,
                "evidence_refs": [
                    {
                        "artifact_path": "pages/page-1.json",
                        "field": "title",
                        "reason": "missing",
                        "observed": "",
                    }
                ],
            },
            {"id": "unsafe", "customer_safe": False, "claim": "Unsupported promise.", "evidence_refs": [{"artifact_path": "pages/page-1.json"}]},
        ],
    }
    service = ClientReportService(artifact_root=artifact_root, output_root=tmp_path / "out")
    first = service.render(snapshot, assessment=assessment)
    second = service.render(snapshot, assessment=assessment)
    assert first.id == second.id
    bundle_dir = tmp_path / "out" / "bundles" / first.id
    assert (bundle_dir / "report.html").read_bytes().startswith(b"<!doctype html>")
    assert (bundle_dir / "report.pdf").read_bytes().startswith(b"%PDF-1.4")
    report = json.loads((bundle_dir / "data/report.json").read_text(encoding="utf-8"))
    assert [c["id"] for c in report["layers"]["evidence"]["claims"] if c["kind"] == "validated_assessment"] == ["finding:safe"]
    manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
    assert any(asset.get("evidence_ref") == "pages/page-1.json" for asset in manifest["assets"])
    assert service.validate(first)["valid"] is True


def test_client_bundle_rejects_artifact_path_escape(tmp_path: Path) -> None:
    artifact_root = tmp_path / "artifacts"
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    snapshot = ReportSnapshot(
        id="snapshot-escape",
        run_id="run-1",
        attempt_id="attempt-1",
        report_contract="operator-v5",
        schema_version=1,
        source_snapshot_ids={},
        source_hashes={},
        renderer_version="operator-renderer.v1",
        payload_sha256=canonical_sha256({}),
        payload_artifact_ref="../outside.json",
    )
    service = ClientReportService(artifact_root=artifact_root, output_root=tmp_path / "out")
    import pytest

    with pytest.raises(ValueError, match="escapes"):
        service.render(snapshot)
