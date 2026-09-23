"""Measured review geometry, not approval or a waiver of chart-embed refusal."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B

EPISODE = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
PLATE = EPISODE / "review/imagegen-complete-worlds-v1/finance-evidence-hall-hosted-v3-cream.png"
SIDECAR = PLATE.with_suffix(".layers.json")
SYNTHETIC_CENTER_QUAD = [[0.35, 0.22], [0.65, 0.22], [0.65, 0.40], [0.35, 0.40]]


def _synthetic_hall_surfaces(tmp_path: Path) -> dict:
    plate = tmp_path / "synthetic-finance-hall.png"
    plate.write_bytes(b"\x89PNG\r\n\x1a\n")
    sidecar = {"embed": {"center-paper": {"kind": "paper", "quad": SYNTHETIC_CENTER_QUAD}}}
    plate.with_suffix(".layers.json").write_text(json.dumps(sidecar), encoding="utf-8")
    return B.plate_embeds(plate)


def _assert_measured_hall_candidate(plate: Path, sidecar: Path) -> None:
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    assert hashlib.sha256(plate.read_bytes()).hexdigest() == data["measurement"]["image_sha256"]
    assert data["status"] == "approved_for_composition"
    assert data["render_eligible"] is True
    approval_path = plate.parents[2] / data["approval_reference"]
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    assert approval["operator_decision"] == "approved_for_composition"
    assert approval["render_eligible"] is True
    assert approval["asset_sha256"] == data["measurement"]["image_sha256"]
    assert (plate.parents[2] / approval["asset_path"]).resolve() == plate.resolve()
    assert "pilot composition only" in approval["approval_basis"]
    assert "not HG3 or release" in approval["approval_basis"]
    assert "still require inspection" in data["approval_scope"]

    surfaces = B.plate_embeds(plate)
    assert set(surfaces) == {"center-paper"}
    surface = surfaces["center-paper"]
    assert surface["kind"] == "paper"
    assert B.embed_quad_error("center-paper", surface, "Fed hall review") is None
    # Every corner is strictly within the measured raw cream-face bounding box.
    for x, y in surface["quad"]:
        assert 503 / 1672 < x < 1170 / 1672
        assert 165 / 941 < y < 394 / 941


def test_measured_hall_center_is_bound_to_actual_candidate():
    if not PLATE.is_file():
        pytest.skip("review-only finance evidence hall plate is absent in this checkout")
    _assert_measured_hall_candidate(PLATE, SIDECAR)


def test_measured_hall_candidate_contract_runs_when_asset_exists(tmp_path):
    episode = tmp_path / "fed-liquidity-pressure"
    review = episode / "review/imagegen-complete-worlds-v1"
    review.mkdir(parents=True)
    plate = review / "finance-evidence-hall-hosted-v3-cream.png"
    plate_bytes = b"synthetic approved review plate"
    plate.write_bytes(plate_bytes)
    image_sha256 = hashlib.sha256(plate_bytes).hexdigest()

    approval_reference = "review/imagegen-complete-worlds-v1/approval.json"
    approval_path = episode / approval_reference
    approval_path.write_text(json.dumps({
        "operator_decision": "approved_for_composition",
        "render_eligible": True,
        "asset_sha256": image_sha256,
        "asset_path": "review/imagegen-complete-worlds-v1/finance-evidence-hall-hosted-v3-cream.png",
        "approval_basis": "pilot composition only; not HG3 or release",
    }), encoding="utf-8")
    sidecar = plate.with_suffix(".layers.json")
    sidecar.write_text(json.dumps({
        "measurement": {"image_sha256": image_sha256},
        "status": "approved_for_composition",
        "render_eligible": True,
        "approval_reference": approval_reference,
        "approval_scope": "still require inspection",
        "embed": {"center-paper": {"kind": "paper", "quad": SYNTHETIC_CENTER_QUAD}},
    }), encoding="utf-8")

    _assert_measured_hall_candidate(plate, sidecar)


def test_synthetic_center_surface_passes_existing_geometry_contract(tmp_path):
    surfaces = _synthetic_hall_surfaces(tmp_path)
    assert set(surfaces) == {"center-paper"}
    surface = surfaces["center-paper"]
    assert surface["kind"] == "paper"
    assert B.embed_quad_error("center-paper", surface, "Fed hall review") is None
    # Keep the synthetic surface inside the measured cream-face bounds.
    for x, y in surface["quad"]:
        assert 503 / 1672 < x < 1170 / 1672
        assert 165 / 941 < y < 394 / 941


def test_synthetic_geometry_does_not_silently_allow_chart_embeds(tmp_path):
    surfaces = _synthetic_hall_surfaces(tmp_path)
    error = B.embed_error(
        {"asset_id": "w4-finance-evidence-hall-v1"}, surfaces,
        "center-paper", "Fed hall review", species="chart",
    )
    assert error and "B1" in error


def test_current_asset_contract_retains_operator_backend_and_style():
    spec = json.loads((EPISODE / "ASSET-CLAIM-SPEC.json").read_text(encoding="utf-8"))
    assert spec["execution_constraints"]["provider"] == "built_in_imagegen"
    assert spec["style_block"].startswith(
        "A light application of wood block print meets vox newspaper with rich anime colors."
    )
    assert spec["render_eligible"] is False
    assert len(spec["slots"]) == 3
    candidate_review = spec["candidate_review"]
    assert candidate_review["status"] == "quarantined_review_only_not_selected"
    assert set(candidate_review["paths"]) == {slot["asset_id"] for slot in spec["slots"]}
    for slot in spec["slots"]:
        candidate = candidate_review["paths"][slot["asset_id"]]
        assert candidate == slot["candidate_path"]
        assert candidate.startswith("review/")
        if "prompt_record" in slot:
            assert slot["prompt_record"].startswith("review/")
