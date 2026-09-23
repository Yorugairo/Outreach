"""Real Blender verification of the pinned native Rigify contact diagnostic."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest

from content.video_engine.scripts.model_foot_contact_probe import (
    _blender_environment,
    execute_probe,
    pinned_blender,
    validate_receipt,
)
from content.video_engine.src.modeling.blender.contact import (
    CLEARANCE_BUDGET_M,
    ContactProbeError,
    REVIEW_RELATIVE,
    ROOT,
    ROOT_SHIFT_M,
    SCHEMA,
    SLIP_BUDGET_M,
    SOURCE_RELATIVE,
    SOURCE_SHA256,
    UNCOMPENSATED_MIN_SLIP_M,
    sha256_file,
)


def _synthetic_receipt(output: Path) -> dict:
    """A tiny internally consistent receipt for validator tests; no Blender needed."""
    base = [[round(0.1 + index * 0.001, 8), 0.0, 0.0] for index in range(16)]
    moved = [[round(point[0] + 0.05, 8), 0.0, 0.0] for point in base]
    held = [[round(point[0] + 0.001, 8), 0.0, 0.0] for point in base]
    raw = {
        "schema": "model_foot_contact_witness.v1",
        "evaluated_human_vertex_count": 100,
        "vertex_indices": list(range(16)),
        "neutral_combined_skin_weights": [[0.8, 0.0] for _ in range(16)],
        "world_coordinates_m": {"neutral": base, "uncompensated": moved, "compensated": held},
    }
    raw_path = output / "witness-patches.json"
    raw_path.write_text(json.dumps(raw), encoding="utf-8")

    def pose(points: list[list[float]], root_x: float, foot_x: float) -> dict:
        return {
            "witness_vertex_count": 16,
            "evaluated_human_vertex_count": 100,
            "witness_min_z_m": 0.0,
            "witness_centroid_world_m": [round(sum(p[0] for p in points) / 16, 8), 0.0, 0.0],
            "left_leg_ik_fk": 0.0,
            "controls": {"root": {"translation_world_m": [root_x, 0.0, 0.0]},
                         "foot_ik.L": {"translation_world_m": [foot_x, 0.0, 0.07]}},
        }

    renders = {}
    for label in ("neutral", "uncompensated", "compensated"):
        image = output / f"{label}.png"
        image.write_bytes(b"\x89PNG\r\n\x1a\nsynthetic-validator-fixture")
        renders[label] = {"path": image.name, "sha256": sha256_file(image),
                          "bytes": image.stat().st_size}
    return {
        "schema": SCHEMA,
        "status": "diagnostic_only",
        "verdict": "pass",
        "source": {"path": SOURCE_RELATIVE, "sha256_before": SOURCE_SHA256,
                   "sha256_after": SOURCE_SHA256, "mutated": False},
        "tool": {"name": "Blender", "version": "5.2.2 LTS", "offline": True,
                 "embedded_scripts": "disabled"},
        "binding_private": {"semantic_effector": "left_foot", "control": "foot_ik.L"},
        "saved_action_retained": "Human.rigifyAction",
        "budgets_predeclared_m": {"root_shift": ROOT_SHIFT_M,
                                  "compensated_max_witness_slip_xy": SLIP_BUDGET_M,
                                  "compensated_clearance_change": CLEARANCE_BUDGET_M,
                                  "uncompensated_mean_witness_slip_min": UNCOMPENSATED_MIN_SLIP_M},
        "witness_selection": {
            "anatomical_skin_groups_left": ["DEF-foot.L", "DEF-toe.L"],
            "anatomical_skin_groups_right_exclusion": ["DEF-foot.R", "DEF-toe.R"],
            "minimum_combined_left_weight": 0.20,
            "maximum_combined_right_weight": 0.05,
            "observed_minimum_left_weight": 0.8,
            "observed_maximum_right_weight": 0.0,
            "neutral_xy_radius_m": [0.16, 0.30],
            "neutral_floor_band_relative_m": [-0.005, 0.010],
        },
        "witness_raw": {"path": raw_path.name, "sha256": sha256_file(raw_path),
                        "vertex_count": 16},
        "poses": {"neutral": pose(base, 0.0, 0.2),
                  "uncompensated": pose(moved, 0.05, 0.25),
                  "compensated": pose(held, 0.05, 0.2)},
        "floor_world_z_m": 0.0,
        "deltas_from_neutral": {
            "uncompensated": {"max_witness_slip_xy_m": 0.05,
                              "mean_witness_slip_xy_m": 0.05,
                              "max_witness_displacement_xyz_m": 0.05,
                              "clearance_change_m": 0.0,
                              "root_shift_xyz_m": [0.05, 0.0, 0.0],
                              "foot_ik_control_slip_xy_m": 0.05},
            "compensated": {"max_witness_slip_xy_m": 0.001,
                            "mean_witness_slip_xy_m": 0.001,
                            "max_witness_displacement_xyz_m": 0.001,
                            "clearance_change_m": 0.0,
                            "root_shift_xyz_m": [0.05, 0.0, 0.0],
                            "foot_ik_control_slip_xy_m": 0.0},
        },
        "checks": {"ik_mode_all_poses": True,
                   "uncompensated_witness_slip_measurable": True,
                   "uncompensated_root_shift_m": True,
                   "compensated_root_shift_m": True,
                   "compensated_control_held": True,
                   "compensated_witness_slip": True,
                   "compensated_clearance_change": True,
                   "compensated_floor_penetration": True},
        "renders": renders,
    }


def test_blender_environment_omits_credentials_and_python_injection(tmp_path: Path,
                                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "do-not-pass")
    monkeypatch.setenv("PYTHONPATH", "untrusted-code")
    monkeypatch.setenv("PATH", "untrusted-bin")
    env = _blender_environment(tmp_path)
    assert "AWS_SECRET_ACCESS_KEY" not in env and "PYTHONPATH" not in env
    assert "untrusted-bin" not in env["PATH"]
    assert env["PYTHONNOUSERSITE"] == "1"
    assert all(Path(env[key]).is_relative_to(tmp_path) for key in
               ("TEMP", "TMP", "USERPROFILE", "APPDATA", "LOCALAPPDATA",
                "BLENDER_USER_RESOURCES", "BLENDER_USER_CONFIG"))


@pytest.mark.parametrize("tamper", [
    "forged_verdict", "forged_check", "underreported_slip", "loosened_budget",
    "wrong_source", "bad_raw_digest", "non_foot_weight", "bad_render_digest",
    "escaped_render_path",
])
def test_validator_rejects_malformed_receipt_without_blender(tmp_path: Path, tamper: str) -> None:
    receipt = _synthetic_receipt(tmp_path)
    assert validate_receipt(receipt, tmp_path) is receipt
    if tamper == "forged_verdict":
        receipt["verdict"] = "fail"
    elif tamper == "forged_check":
        receipt["checks"]["compensated_witness_slip"] = 1
    elif tamper == "underreported_slip":
        receipt["deltas_from_neutral"]["compensated"]["max_witness_slip_xy_m"] = 0.0
    elif tamper == "loosened_budget":
        receipt["budgets_predeclared_m"]["compensated_max_witness_slip_xy"] = 0.01
    elif tamper == "wrong_source":
        receipt["source"]["path"] = "another.blend"
    elif tamper == "bad_raw_digest":
        receipt["witness_raw"]["sha256"] = "0" * 64
    elif tamper == "non_foot_weight":
        raw_path = tmp_path / "witness-patches.json"
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        raw["neutral_combined_skin_weights"][0] = [0.0, 0.8]
        raw_path.write_text(json.dumps(raw), encoding="utf-8")
        receipt["witness_raw"]["sha256"] = sha256_file(raw_path)
    elif tamper == "bad_render_digest":
        receipt["renders"]["neutral"]["sha256"] = "0" * 64
    else:
        receipt["renders"]["neutral"]["path"] = "../neutral.png"
    with pytest.raises(ContactProbeError):
        validate_receipt(receipt, tmp_path)


def test_rejects_non_quarantine_run_name_before_writes() -> None:
    with pytest.raises(ContactProbeError, match="run name"):
        execute_probe("../outside")


def test_real_blender_holds_left_foot_patch_under_root_shift() -> None:
    source = ROOT / SOURCE_RELATIVE
    assert sha256_file(source) == SOURCE_SHA256
    assert pinned_blender().is_file(), "pinned Blender 5.2.2 is required for this proof"
    name = f"pytest-{uuid4().hex[:12]}"
    receipt = execute_probe(name)
    output = ROOT / REVIEW_RELATIVE / name
    persisted = json.loads((output / "receipt.json").read_text(encoding="utf-8"))

    assert receipt["verdict"] == persisted["verdict"] == "pass"
    assert receipt["source"] == {
        "path": SOURCE_RELATIVE,
        "sha256_before": SOURCE_SHA256,
        "sha256_after": SOURCE_SHA256,
        "mutated": False,
    }
    assert sha256_file(source) == SOURCE_SHA256
    assert receipt["tool"]["version"] == "5.2.2 LTS"
    assert receipt["tool"]["offline"] is True
    assert receipt["tool"]["embedded_scripts"] == "disabled"
    assert receipt["binding_private"]["semantic_effector"] == "left_foot"
    assert receipt["binding_private"]["control"] == "foot_ik.L"
    assert receipt["saved_action_retained"] == "Human.rigifyAction"
    assert receipt["budgets_predeclared_m"]["compensated_max_witness_slip_xy"] == SLIP_BUDGET_M
    assert receipt["budgets_predeclared_m"]["compensated_clearance_change"] == CLEARANCE_BUDGET_M
    assert all(receipt["checks"].values())

    poses = receipt["poses"]
    neutral = poses["neutral"]
    assert neutral["witness_vertex_count"] == 294
    assert receipt["witness_selection"]["anatomical_skin_groups_left"] == ["DEF-foot.L", "DEF-toe.L"]
    assert receipt["witness_selection"]["neutral_floor_band_relative_m"] == [-0.005, 0.010]
    assert all(pose["left_leg_ik_fk"] == 0.0 for pose in poses.values())
    assert all(pose["evaluated_human_vertex_count"] == neutral["evaluated_human_vertex_count"]
               for pose in poses.values())
    raw_path = output / receipt["witness_raw"]["path"]
    assert sha256_file(raw_path) == receipt["witness_raw"]["sha256"]
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    assert raw["schema"] == "model_foot_contact_witness.v1"
    assert len(raw["vertex_indices"]) == neutral["witness_vertex_count"]
    assert len(set(raw["vertex_indices"])) == len(raw["vertex_indices"])
    assert len(raw["neutral_combined_skin_weights"]) == neutral["witness_vertex_count"]
    assert all(left >= 0.20 and right <= 0.05
               for left, right in raw["neutral_combined_skin_weights"])
    for label, pose in poses.items():
        assert len(raw["world_coordinates_m"][label]) == pose["witness_vertex_count"]
        assert {"root", "foot_ik.L", "toe_ik.L", "thigh_ik_target.L",
                "VIS_thigh_ik_pole.L", "DEF-foot.L"} <= pose["controls"].keys()

    uncompensated = receipt["deltas_from_neutral"]["uncompensated"]
    compensated = receipt["deltas_from_neutral"]["compensated"]
    assert uncompensated["mean_witness_slip_xy_m"] >= UNCOMPENSATED_MIN_SLIP_M
    assert compensated["max_witness_slip_xy_m"] <= SLIP_BUDGET_M
    assert abs(compensated["clearance_change_m"]) <= CLEARANCE_BUDGET_M
    assert compensated["foot_ik_control_slip_xy_m"] <= SLIP_BUDGET_M
    assert poses["compensated"]["witness_min_z_m"] >= receipt["floor_world_z_m"] - CLEARANCE_BUDGET_M

    assert set(receipt["renders"]) == {"neutral", "uncompensated", "compensated"}
    for render in receipt["renders"].values():
        image = output / render["path"]
        assert image.is_file()
        assert image.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        assert sha256_file(image) == render["sha256"]
    assert (output / "blender.stdout.log").is_file()
    assert (output / "blender.stderr.log").is_file()
