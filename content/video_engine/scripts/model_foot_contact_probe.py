"""Run the hash-pinned v1.1 foot-contact probe in isolated offline Blender."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content.video_engine.src.modeling.blender.contact import (  # noqa: E402
    ContactProbeError,
    CLEARANCE_BUDGET_M,
    REVIEW_RELATIVE,
    ROOT_SHIFT_M,
    SCHEMA,
    SLIP_BUDGET_M,
    SOURCE_RELATIVE,
    SOURCE_SHA256,
    UNCOMPENSATED_MIN_SLIP_M,
    sha256_file,
)


WORKER = ROOT / "content/video_engine/src/modeling/blender/contact.py"
BENCHMARK = ROOT / "content/video_engine/tests/fixtures/modeling/baseline/benchmark-inputs.json"
_RUN_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


def pinned_blender() -> Path:
    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    path = Path(benchmark["tools"]["blender"]["path"])
    if not path.is_file():
        raise ContactProbeError(f"pinned Blender executable unavailable: {path}")
    return path


def _blender_environment(output: Path) -> dict[str, str]:
    """Pass only Windows runtime basics and paths isolated under this run."""
    system_root = Path(os.environ.get("SystemRoot") or os.environ.get("WINDIR") or "C:/Windows")
    resources = output / "blender-user-resources"
    temporary = output / "tmp"
    for path in (temporary, resources, resources / "config", resources / "scripts",
                 resources / "datafiles", resources / "extensions", resources / "appdata",
                 resources / "localappdata"):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "SystemRoot": str(system_root),
        "WINDIR": str(system_root),
        "PATH": os.pathsep.join((str(system_root / "System32"), str(system_root))),
        "TEMP": str(temporary),
        "TMP": str(temporary),
        "HOME": str(resources),
        "USERPROFILE": str(resources),
        "APPDATA": str(resources / "appdata"),
        "LOCALAPPDATA": str(resources / "localappdata"),
        "PYTHONNOUSERSITE": "1",
        "BLENDER_USER_RESOURCES": str(resources),
        "BLENDER_USER_CONFIG": str(resources / "config"),
        "BLENDER_USER_SCRIPTS": str(resources / "scripts"),
        "BLENDER_USER_DATAFILES": str(resources / "datafiles"),
        "BLENDER_USER_EXTENSIONS": str(resources / "extensions"),
    }


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContactProbeError(f"invalid receipt number: {label}")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ContactProbeError(f"invalid receipt number: {label}") from exc
    if not math.isfinite(number):
        raise ContactProbeError(f"invalid receipt number: {label}")
    return number


def _near(actual: Any, expected: float, label: str, tolerance: float = 2e-7) -> None:
    if abs(_number(actual, label) - expected) > tolerance:
        raise ContactProbeError(f"receipt measurement disagrees with raw witness: {label}")


def _vector(value: Any, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 3:
        raise ContactProbeError(f"invalid receipt vector: {label}")
    return [_number(component, label) for component in value]


def _verified_file(output: Path, name: Any, expected_name: str, digest: Any,
                   *, max_bytes: int) -> Path:
    if name != expected_name or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ContactProbeError(f"invalid receipt artifact declaration: {expected_name}")
    path = output / expected_name
    if not path.is_file() or path.is_symlink() or path.stat().st_size > max_bytes:
        raise ContactProbeError(f"missing or oversized receipt artifact: {expected_name}")
    if sha256_file(path) != digest:
        raise ContactProbeError(f"receipt artifact digest mismatch: {expected_name}")
    return path


def validate_receipt(receipt: Any, output: Path) -> dict[str, Any]:
    """Recompute the pass/fail facts from the raw patch before trusting Blender output."""
    try:
        if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA or receipt.get("status") != "diagnostic_only":
            raise ContactProbeError("invalid receipt schema/status")
        source = receipt["source"]
        if source != {"path": SOURCE_RELATIVE, "sha256_before": SOURCE_SHA256,
                      "sha256_after": SOURCE_SHA256, "mutated": False}:
            raise ContactProbeError("receipt source does not match pinned input")
        tool = receipt["tool"]
        if (tool["name"] != "Blender" or tool["version"] != "5.2.2 LTS"
                or tool["offline"] is not True or tool["embedded_scripts"] != "disabled"):
            raise ContactProbeError("receipt does not confirm isolated Blender 5.2.2")
        if (receipt["binding_private"]["semantic_effector"] != "left_foot"
                or receipt["binding_private"]["control"] != "foot_ik.L"
                or receipt["saved_action_retained"] != "Human.rigifyAction"):
            raise ContactProbeError("receipt rig binding/action mismatch")
        budgets = receipt["budgets_predeclared_m"]
        expected_budgets = {"root_shift": ROOT_SHIFT_M,
                            "compensated_max_witness_slip_xy": SLIP_BUDGET_M,
                            "compensated_clearance_change": CLEARANCE_BUDGET_M,
                            "uncompensated_mean_witness_slip_min": UNCOMPENSATED_MIN_SLIP_M}
        if budgets != expected_budgets:
            raise ContactProbeError("receipt changed predeclared budgets")
        selection = receipt["witness_selection"]
        if (selection["anatomical_skin_groups_left"] != ["DEF-foot.L", "DEF-toe.L"]
                or selection["anatomical_skin_groups_right_exclusion"] != ["DEF-foot.R", "DEF-toe.R"]
                or selection["minimum_combined_left_weight"] != 0.20
                or selection["maximum_combined_right_weight"] != 0.05
                or selection["neutral_xy_radius_m"] != [0.16, 0.30]
                or selection["neutral_floor_band_relative_m"] != [-0.005, 0.010]):
            raise ContactProbeError("receipt witness selection does not identify the left sole band")

        raw_entry = receipt["witness_raw"]
        raw_path = _verified_file(output, raw_entry["path"], "witness-patches.json",
                                  raw_entry["sha256"], max_bytes=4_000_000)
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        if raw["schema"] != "model_foot_contact_witness.v1":
            raise ContactProbeError("invalid raw witness schema")
        indices = raw["vertex_indices"]
        vertex_count = raw["evaluated_human_vertex_count"]
        if (not isinstance(vertex_count, int) or vertex_count <= 0
                or not isinstance(indices, list) or len(indices) < 16
                or len(indices) != raw_entry["vertex_count"]
                or any(type(index) is not int or index < 0 or index >= vertex_count for index in indices)
                or indices != sorted(set(indices))):
            raise ContactProbeError("invalid stable witness vertex indices")
        skin_weights = raw["neutral_combined_skin_weights"]
        if not isinstance(skin_weights, list) or len(skin_weights) != len(indices):
            raise ContactProbeError("missing neutral anatomical skin weights")
        verified_weights = []
        for pair in skin_weights:
            if not isinstance(pair, list) or len(pair) != 2:
                raise ContactProbeError("invalid neutral anatomical skin weights")
            left = _number(pair[0], "left foot skin weight")
            right = _number(pair[1], "right foot skin weight")
            if left < 0.20 or right > 0.05:
                raise ContactProbeError("witness includes a vertex outside left-foot skin weights")
            verified_weights.append((left, right))
        _near(selection["observed_minimum_left_weight"],
              min(pair[0] for pair in verified_weights), "minimum left skin weight")
        _near(selection["observed_maximum_right_weight"],
              max(pair[1] for pair in verified_weights), "maximum right skin weight")
        labels = ("neutral", "uncompensated", "compensated")
        poses = receipt["poses"]
        if set(poses) != set(labels) or set(raw["world_coordinates_m"]) != set(labels):
            raise ContactProbeError("receipt/raw witness poses differ")
        points = {}
        for label in labels:
            pose = poses[label]
            patch = raw["world_coordinates_m"][label]
            if (pose["witness_vertex_count"] != len(indices)
                    or pose["evaluated_human_vertex_count"] != vertex_count
                    or not isinstance(patch, list) or len(patch) != len(indices)):
                raise ContactProbeError(f"invalid witness length: {label}")
            points[label] = [_vector(point, f"{label} witness") for point in patch]
            _near(pose["witness_min_z_m"], min(point[2] for point in points[label]),
                  f"{label} minimum Z")
            for axis, recorded in enumerate(_vector(pose["witness_centroid_world_m"], f"{label} centroid")):
                _near(recorded, sum(point[axis] for point in points[label]) / len(indices),
                      f"{label} centroid axis {axis}")
        floor_z = _number(receipt["floor_world_z_m"], "floor Z")
        deltas = receipt["deltas_from_neutral"]
        if set(deltas) != {"uncompensated", "compensated"}:
            raise ContactProbeError("invalid delta labels")
        for label in ("uncompensated", "compensated"):
            patch_slips = [math.dist(a[:2], b[:2]) for a, b in
                           zip(points["neutral"], points[label])]
            full_slips = [math.dist(a, b) for a, b in zip(points["neutral"], points[label])]
            delta = deltas[label]
            _near(delta["max_witness_slip_xy_m"], max(patch_slips), f"{label} max slip")
            _near(delta["mean_witness_slip_xy_m"], sum(patch_slips) / len(patch_slips),
                  f"{label} mean slip")
            _near(delta["max_witness_displacement_xyz_m"], max(full_slips),
                  f"{label} max displacement")
            _near(delta["clearance_change_m"],
                  min(point[2] for point in points[label])
                  - min(point[2] for point in points["neutral"]), f"{label} clearance")
            controls = poses[label]["controls"]
            base_controls = poses["neutral"]["controls"]
            for axis, recorded in enumerate(_vector(delta["root_shift_xyz_m"], f"{label} root delta")):
                _near(recorded,
                      _vector(controls["root"]["translation_world_m"], "root")[axis]
                      - _vector(base_controls["root"]["translation_world_m"], "neutral root")[axis],
                      f"{label} root axis {axis}")
            _near(delta["foot_ik_control_slip_xy_m"], math.dist(
                _vector(controls["foot_ik.L"]["translation_world_m"], "foot control")[:2],
                _vector(base_controls["foot_ik.L"]["translation_world_m"], "neutral foot control")[:2]),
                f"{label} foot control slip")
        uncomp = deltas["uncompensated"]
        comp = deltas["compensated"]
        checks = {
            "ik_mode_all_poses": all(_number(poses[label]["left_leg_ik_fk"], "IK_FK") == 0.0 for label in labels),
            "uncompensated_witness_slip_measurable": _number(uncomp["mean_witness_slip_xy_m"], "uncompensated slip") >= UNCOMPENSATED_MIN_SLIP_M,
            "uncompensated_root_shift_m": abs(_number(uncomp["root_shift_xyz_m"][0], "uncompensated root") - ROOT_SHIFT_M) <= 0.001,
            "compensated_root_shift_m": abs(_number(comp["root_shift_xyz_m"][0], "compensated root") - ROOT_SHIFT_M) <= 0.001,
            "compensated_control_held": _number(comp["foot_ik_control_slip_xy_m"], "control slip") <= SLIP_BUDGET_M,
            "compensated_witness_slip": _number(comp["max_witness_slip_xy_m"], "compensated slip") <= SLIP_BUDGET_M,
            "compensated_clearance_change": abs(_number(comp["clearance_change_m"], "clearance")) <= CLEARANCE_BUDGET_M,
            "compensated_floor_penetration": _number(poses["compensated"]["witness_min_z_m"], "minimum Z") >= floor_z - CLEARANCE_BUDGET_M,
        }
        declared_checks = receipt["checks"]
        if (not isinstance(declared_checks, dict)
                or any(type(value) is not bool for value in declared_checks.values())
                or declared_checks != checks
                or receipt["verdict"] != ("pass" if all(checks.values()) else "fail")):
            raise ContactProbeError("receipt verdict/checks disagree with measured values")
        renders = receipt["renders"]
        if set(renders) != set(labels):
            raise ContactProbeError("receipt is missing a matched render")
        for label in labels:
            render = renders[label]
            path = _verified_file(output, render["path"], f"{label}.png",
                                  render["sha256"], max_bytes=10_000_000)
            with path.open("rb") as stream:
                signature = stream.read(8)
            if path.stat().st_size != render["bytes"] or signature != b"\x89PNG\r\n\x1a\n":
                raise ContactProbeError(f"invalid PNG receipt: {label}")
        return receipt
    except (KeyError, TypeError, ValueError, IndexError, OSError, json.JSONDecodeError) as exc:
        raise ContactProbeError(f"malformed Blender receipt: {exc}") from exc


def execute_probe(run_name: str, *, blender_path: Path | None = None) -> dict[str, Any]:
    """Create one immutable quarantined run; preserve logs and failed receipts."""
    if not _RUN_NAME.fullmatch(run_name):
        raise ContactProbeError("run name must be a lowercase slug")
    source = (ROOT / SOURCE_RELATIVE).resolve(strict=True)
    if sha256_file(source) != SOURCE_SHA256:
        raise ContactProbeError("source hash differs from pinned v1.1 scene")
    blender = blender_path or pinned_blender()
    if not blender.is_file():
        raise ContactProbeError(f"Blender executable unavailable: {blender}")
    review = (ROOT / REVIEW_RELATIVE).resolve()
    review.mkdir(parents=True, exist_ok=True)
    output = review / run_name
    if output.exists():
        raise ContactProbeError(f"probe run already exists: {run_name}")
    output.mkdir()
    env = _blender_environment(output)
    command = [str(blender), "--background", "--factory-startup", "--offline-mode",
               "--disable-autoexec", "--python-exit-code", "17", "--python", str(WORKER),
               "--", "--source", str(source), "--output", str(output)]
    try:
        process = subprocess.run(command, cwd=ROOT, env=env, text=True,
                                 capture_output=True, timeout=300, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContactProbeError(f"Blender probe could not complete: {exc}") from exc
    (output / "blender.stdout.log").write_text(process.stdout, encoding="utf-8")
    (output / "blender.stderr.log").write_text(process.stderr, encoding="utf-8")
    if sha256_file(source) != SOURCE_SHA256:
        raise ContactProbeError("source hash changed during Blender probe")
    if process.returncode != 0:
        raise ContactProbeError(f"Blender probe exited {process.returncode}; logs: {output}")
    receipt_path = output / "receipt.json"
    if not receipt_path.is_file():
        raise ContactProbeError(f"Blender exited without receipt; logs: {output}")
    if receipt_path.stat().st_size > 1_000_000:
        raise ContactProbeError(f"Blender receipt exceeds size limit: {receipt_path}")
    try:
        document = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ContactProbeError(f"Blender wrote malformed JSON: {receipt_path}") from exc
    receipt = validate_receipt(document, output)
    receipt["run_dir"] = str(output)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, help="new lowercase run slug inside ignored review quarantine")
    args = parser.parse_args(argv)
    try:
        receipt = execute_probe(args.run)
    except ContactProbeError as exc:
        print(f"CONTACT_PROBE_ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"verdict": receipt["verdict"], "run_dir": receipt["run_dir"],
                      "checks": receipt["checks"], "deltas": receipt["deltas_from_neutral"]},
                     sort_keys=True))
    return 0 if receipt["verdict"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
