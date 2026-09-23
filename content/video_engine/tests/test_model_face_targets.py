"""Real Blender proof for MPFB facial targets on the tracked v1.1 family."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = ROOT / "content/video_engine/tests/fixtures/modeling/face-target-proof"
BASELINE_DIR = ROOT / "content/video_engine/tests/fixtures/modeling/baseline"
DRIVER = FIXTURE_DIR / "run_face_target_proof.py"
CONFIG = FIXTURE_DIR / "face-targets.v1.json"
SOURCE = ROOT / "content/video_engine/assets/modeling/native/fighter-family-v1.1.blend"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run_blender(blend_file: Path, *driver_args: str) -> subprocess.CompletedProcess[str]:
    benchmark = json.loads((BASELINE_DIR / "benchmark-inputs.json").read_text(encoding="utf-8"))
    executable = Path(benchmark["tools"]["blender"]["path"])
    assert executable.is_file(), f"pinned Blender unavailable: {executable}"
    env = os.environ.copy()
    env["BLENDER_USER_RESOURCES"] = str((BASELINE_DIR / "profile").resolve())
    env["PYTHONNOUSERSITE"] = "1"
    return subprocess.run(
        [str(executable), "--background", "--factory-startup", "--offline-mode",
         "--disable-autoexec", "--python-exit-code", "17", str(blend_file),
         "--python", str(DRIVER), "--", *driver_args],
        cwd=ROOT, env=env, text=True, capture_output=True, timeout=240, check=False,
    )


def test_face_target_proof_rejects_relative_render_path_before_writes(tmp_path: Path) -> None:
    output = tmp_path / "must-not-exist.blend"
    report = tmp_path / "must-not-exist.json"
    process = _run_blender(
        SOURCE, "--mode", "build", "--output", str(output.resolve()),
        "--renders", "relative-render-path", "--report", str(report.resolve()),
    )
    assert process.returncode != 0
    assert "--renders must be an absolute path" in (process.stdout + process.stderr)
    assert not output.exists() and not report.exists()


def test_face_targets_are_editable_region_local_and_survive_reopen(tmp_path: Path) -> None:
    document = json.loads(CONFIG.read_text(encoding="utf-8"))
    source_hash = _sha256(SOURCE)
    assert source_hash == document["source_sha256"]
    blend = (tmp_path / "face-target-proof.blend").resolve()
    renders = (tmp_path / "renders").resolve()
    build_report = (tmp_path / "build.json").resolve()
    reopened_report = (tmp_path / "reopen.json").resolve()
    build = _run_blender(
        SOURCE, "--mode", "build", "--output", str(blend),
        "--renders", str(renders), "--report", str(build_report),
    )
    assert build.returncode == 0, build.stdout + "\n" + build.stderr
    state = json.loads(build_report.read_text(encoding="utf-8"))
    assert state["status"] == "diagnostic_only"
    assert state["stored_body_vertices"] == document["expected_body_vertices"] == 19158
    assert state["rig_bones"] == 930 and state["garment_vertices"] == 741
    assert state["saved_blend_sha256"] == _sha256(blend)
    assert state["source_sha256"] == source_hash
    assert state["mpfb_package_sha256"] == "923b0a0950b2b1d75440200b5457e9af9951e477b37a8e1537956f5f28b15c31"
    assert 0.09 < state["target_scale_factor"] < 0.11
    assert len(state["targets"]) == len(document["targets"]) == 4
    for actual, expected in zip(state["targets"], document["targets"]):
        assert actual["path"] == expected["relative_path"]
        assert actual["sha256"] == expected["sha256"]
        assert actual["shape_key"] == expected["shape_key"]
        assert actual["weight"] == expected["weight"]
        assert actual["target_entries"] >= actual["changed_vertices_gt_1e-6_m"] > 30
        assert actual["max_target_index"] < state["stored_body_vertices"]
        assert 0.001 < actual["max_full_weight_displacement_m"] < 0.03
        assert actual["max_target_to_shape_key_error_m"] < 2e-6
        assert actual["non_face_max_displacement_below_head_floor_m"] < 1e-6
        assert actual["changed_basis_bounds_local_m"]["min"][2] >= actual["head_floor_z_local_m"]
    assert set(state["renders"]) == {
        "neutral_front", "neutral_profile", "morph_front", "morph_profile", "rig_stress_frame_52",
    }
    for entry in state["renders"].values():
        image = Path(entry["path"])
        assert image.parent == renders and image.is_file()
        assert image.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        assert entry["sha256"] == _sha256(image)
    assert state["renders"]["neutral_front"]["sha256"] != state["renders"]["morph_front"]["sha256"]
    assert state["renders"]["neutral_profile"]["sha256"] != state["renders"]["morph_profile"]["sha256"]

    reopened = _run_blender(blend, "--mode", "reopen", "--report", str(reopened_report))
    assert reopened.returncode == 0, reopened.stdout + "\n" + reopened.stderr
    inspection = json.loads(reopened_report.read_text(encoding="utf-8"))
    assert inspection["status"] == "reopened"
    assert inspection["blend_sha256"] == state["saved_blend_sha256"]
    assert inspection["body_vertices"] == state["stored_body_vertices"]
    assert inspection["rig_bones"] == state["rig_bones"]
    assert inspection["garment_vertices"] == state["garment_vertices"]
    assert inspection["proof_shape_key_weights"] == {
        row["shape_key"]: row["weight"] for row in document["targets"]
    }
    assert inspection["stress_frame"] == 52
    assert inspection["evaluated_vertices_changed_gt_1e-5_m"] > 1000
    assert _sha256(SOURCE) == source_hash
