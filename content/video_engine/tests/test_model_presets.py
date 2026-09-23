from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from content.video_engine.src.modeling.blender.presets import (
    DEFAULT_CONTROLS,
    FAMILY_ID,
    family_manifest,
    resolve_controls,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = ROOT / "content/video_engine/tests/fixtures/modeling/presets"
BASELINE_DIR = ROOT / "content/video_engine/tests/fixtures/modeling/baseline"
BUILD_DRIVER = FIXTURE_DIR / "build_fixture.py"
REOPEN_DRIVER = FIXTURE_DIR / "inspect_saved_fixture.py"


def test_preset_controls_are_bounded_repeatable_and_reject_unknown_inputs() -> None:
    first = resolve_controls()
    second = resolve_controls()
    assert first == second == DEFAULT_CONTROLS
    assert first is not DEFAULT_CONTROLS
    assert family_manifest()["family_id"] == FAMILY_ID
    assert family_manifest()["status"] == "diagnostic_only"
    assert family_manifest()["art_approval"] == "not_approved"

    tailored = resolve_controls({
        "body": {"height": 0.62, "muscle": 0.52},
        "face": {"head_width": 0.21, "hand_scale": 0.19},
        "hair_style": "crop",
        "clothing_style": "warmup",
        "skin_palette": "deep",
        "clothing_palette": "brick",
    })
    assert tailored["body"]["height"] == 0.62
    assert tailored["face"]["head_width"] == 0.21
    assert tailored["hair_style"] == "crop"
    assert tailored["clothing_style"] == "warmup"
    assert tailored["skin_palette"] == "deep"
    assert tailored["clothing_palette"] == "brick"

    with pytest.raises(ValueError, match="unknown preset control"):
        resolve_controls({"unbounded": 1})
    with pytest.raises(ValueError, match="between"):
        resolve_controls({"body": {"height": 0.9}})
    with pytest.raises(ValueError, match="finite number"):
        resolve_controls({"face": {"jaw_drop": float("nan")}})
    with pytest.raises(ValueError, match="hair_style"):
        resolve_controls({"hair_style": "not-a-style"})


def _blender_executable() -> Path:
    baseline = json.loads((BASELINE_DIR / "benchmark-inputs.json").read_text(encoding="utf-8"))
    path = Path(baseline["tools"]["blender"]["path"])
    assert path.is_file(), f"pinned Blender executable missing: {path}"
    return path


def _run_blender(
    script: Path,
    profile: Path,
    extra_args: list[str],
    *,
    blend_file: Path | None = None,
    timeout: int = 1200,
) -> subprocess.CompletedProcess[str]:
    command = [
        str(_blender_executable()),
        "--background",
        "--factory-startup",
        "--offline-mode",
        "--disable-autoexec",
        "--python-exit-code",
        "17",
    ]
    if blend_file is not None:
        command.append(str(blend_file))
    command.extend(["--python", str(script), "--", *extra_args])
    environment = os.environ.copy()
    environment["BLENDER_USER_RESOURCES"] = str(profile)
    environment["PYTHONNOUSERSITE"] = "1"
    return subprocess.run(command, cwd=ROOT, env=environment, text=True, capture_output=True, timeout=timeout, check=False)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def test_canonical_native_asset_matches_its_diagnostic_manifest() -> None:
    asset_dir = ROOT / "content/video_engine/assets/modeling/native"
    manifest = json.loads((asset_dir / "fighter-family-v1.manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "diagnostic_only"
    assert manifest["art_approval"] == "not_approved"
    assert manifest["authoring"]["provider_calls"] == 0
    assert manifest["editable_source"] == "fighter-family-v1.blend"
    assert _sha256(asset_dir / manifest["editable_source"]) == manifest["editable_source_sha256"]
    garment_manifest = json.loads((asset_dir / "fighter-family-v1.1.manifest.json").read_text(encoding="utf-8"))
    assert garment_manifest["status"] == "diagnostic_only"
    assert garment_manifest["art_approval"] == "not_approved"
    assert garment_manifest["editable_source"] == "fighter-family-v1.1.blend"
    assert garment_manifest["source_v1_sha256"] == manifest["editable_source_sha256"]
    assert _sha256(asset_dir / garment_manifest["editable_source"]) == garment_manifest["editable_source_sha256"]


def test_blender_builds_and_reopens_editable_diagnostic_preset(tmp_path: Path) -> None:
    controls_path = FIXTURE_DIR / "default-controls.v1.json"
    controls_doc = json.loads(controls_path.read_text(encoding="utf-8"))
    controls = resolve_controls(controls_doc["controls"])
    profile = (BASELINE_DIR / "profile").resolve()
    artifact = tmp_path / "fighter-family-v1.1.blend"
    renders = tmp_path / "renders"
    build_result_path = tmp_path / "build-result.json"

    build = _run_blender(BUILD_DRIVER, profile, [
        "--controls", str(controls_path),
        "--output", str(artifact),
        "--renders", str(renders),
        "--result", str(build_result_path),
    ])
    assert build.returncode == 0, f"Blender authoring failed ({build.returncode})\n{build.stdout}\n{build.stderr}"
    assert artifact.is_file() and artifact.stat().st_size > 100_000
    assert build_result_path.is_file()
    build_result = json.loads(build_result_path.read_text(encoding="utf-8"))
    assert build_result["controls_applied"] == controls
    assert build_result["runtime"]["blender_version"] == "5.2.2 LTS"
    assert build_result["runtime"]["provider_calls"] == 0
    assert build_result["asset_sha256"] == _sha256(artifact)

    for view in ("front", "three-quarter", "side", "back", "face", "hand", "stress-arm",
                 "garment-front", "garment-three-quarter", "stress-frame-28", "stress-hip-leg-frame-52"):
        image = renders / f"fighter-family-{view}.png"
        assert image.is_file() and image.stat().st_size > 4_000, f"missing/empty {view} diagnostic render"
    assert _sha256(renders / "fighter-family-front.png") != _sha256(renders / "fighter-family-stress-hip-leg-frame-52.png")

    reopened_path = tmp_path / "reopened-inspection.json"
    # Blender loads the actual persisted project before running the read-only inspector.
    reopened = _run_blender(
        REOPEN_DRIVER,
        profile,
        ["--output", str(reopened_path)],
        blend_file=artifact,
        timeout=600,
    )
    assert reopened.returncode == 0, f"Blender reopen inspection failed ({reopened.returncode})\n{reopened.stdout}\n{reopened.stderr}"
    assert reopened_path.is_file()
    state = json.loads(reopened_path.read_text(encoding="utf-8"))

    assert state["family_id"] == FAMILY_ID
    assert state["asset_status"] == "diagnostic_only"
    assert state["verdict"]["saved_scene_integrity"] == "pass"
    assert state["verdict"]["rig_deformation_probe"] == "pass"
    assert state["character"]["body_materials"]
    assert state["character"]["clothing_representation"] == "separate_editable_skinned_garment_shell"
    assert "MM_Costume_cobalt" not in state["character"]["body_materials"]
    garment = state["garment"]
    assert garment["present"] is True
    assert garment["object_name"] == "Garment_FightShorts"
    assert garment["representation"] == "separate_editable_skinned_shell"
    assert garment["stored_vertex_count"] >= 500
    assert garment["stored_polygon_count"] >= 250
    assert garment["weighted_vertex_count"] == garment["stored_vertex_count"]
    assert garment["source_vertex_attribute"] == "body_source_vertex_index"
    assert "MM_Costume_cobalt" in garment["material_names"]
    assert garment["armature_modifier_targets"] == ["Human.rigify", "Human.rigify"]
    assert garment["solidify_modifier"]["thickness_m"] == 0.003
    garment_object = next(obj for obj in state["objects"] if obj["name"] == "Garment_FightShorts")
    assert garment_object["modifier_stack"][1]["vertex_group"] == "mhmask-preserve-volume"
    assert state["character"]["vertex_group_count"] >= 100
    assert state["character"]["armature_modifier_targets"] == ["Human.rigify", "Human.rigify"]
    assert state["character"]["armature_modifier_stack"] == [
        {"name": "Armature", "target": "Human.rigify", "vertex_group": "", "preserve_volume": False,
         "use_vertex_groups": True, "use_bone_envelopes": False, "show_viewport": True, "show_render": True},
        {"name": "Armature PV", "target": "Human.rigify", "vertex_group": "mhmask-preserve-volume",
         "preserve_volume": True, "use_vertex_groups": True, "use_bone_envelopes": False,
         "show_viewport": True, "show_render": True},
    ]
    assert state["rig"]["bone_count"] >= 500
    assert state["rig"]["required_deform_bones_present"] is True
    assert state["rig"]["fk_controls_present"] is True
    assert state["rig"]["pose_action_present"] is True
    assert state["modifier_probe"]["status"] == "measured"
    assert state["modifier_probe"]["both_vs_main_only_max_m"] < 0.0001
    assert state["modifier_probe"]["both_vs_pv_only_max_m"] > 0.05
    assert state["rig"]["style_controls"] == {
        "hair_style": "quiff",
        "clothing_style": "fight_kit",
        "skin_palette": "sand",
        "clothing_palette": "cobalt",
    }
    assert state["character"]["body_custom_controls_json"]
    assert state["character"]["head_forward_world"][1] < -0.5
    assert state["character"]["head_up_world"][2] > 0.7
    assert state["floor"]["object_present"] is True
    assert abs(state["floor"]["baseline_body_clearance_m"]) < 0.02

    layers = {obj["diagnostic_layer"] for obj in state["objects"]}
    assert {"face", "hair"}.issubset(layers)
    assert any(obj["name"] == "Hair_SweptQuiff" and obj["vertices_stored"] > 10 for obj in state["objects"])
    assert any(obj["diagnostic_layer"] == "clothing" for obj in state["objects"])
    assert any(obj["name"] == "Face_Iris_L" for obj in state["objects"])
    assert any(obj["name"] == "Face_Pupil_L" for obj in state["objects"])
    assert any(obj["attachment_bone"] == "DEF-spine.006" for obj in state["objects"] if obj["diagnostic_layer"] == "face")

    metrics = state["face_hand_metrics"]
    assert metrics["head_weighted_group"]["vertex_count"] >= 500
    assert metrics["left_hand_weighted_group"]["vertex_count"] >= 100
    assert metrics["right_hand_weighted_group"]["vertex_count"] >= 100
    assert 0.04 < metrics["iris_center_distance_m"] < 0.10

    contact = next(frame for frame in state["stress_samples"] if frame["frame"] == 27)
    assert contact["vertices_changed_gt_1e-5_from_frame_1"] >= 100
    assert contact["max_vertex_displacement_from_frame_1_m"] > 0.05
    leg_stress = next(frame for frame in state["stress_samples"] if frame["frame"] == 52)
    assert leg_stress["max_vertex_displacement_from_frame_1_m"] > 0.3
    for sample in (state["stress_samples"][0], leg_stress):
        clearance = sample["garment_clearance"]
        assert clearance["status"] == "measured"
        assert clearance["matched_signed_offset_min_m"] > 0.004
        assert clearance["nearest_body_surface_min_m"] > 0.001
        assert clearance["matched_vertices_at_or_below_1mm"] == 0
        assert clearance["matched_faces"] == garment["stored_polygon_count"]
        assert clearance["face_centroid_offset_min_m"] > 0.003
        assert clearance["face_centroids_at_or_below_1mm"] == 0
    assert state["verdict"]["art_status"].startswith("diagnostic only")

    # A second build proves the controls change the saved mesh, morphs, hair,
    # palette and separate clothing geometry rather than merely changing manifest text.
    alternate_controls = FIXTURE_DIR / "alternate-controls.v1.json"
    alternate_artifact = tmp_path / "alternate-fighter-family-v1.1.blend"
    alternate_build = _run_blender(BUILD_DRIVER, profile, [
        "--controls", str(alternate_controls),
        "--output", str(alternate_artifact),
        "--renders", str(tmp_path / "alternate-renders"),
        "--result", str(tmp_path / "alternate-build-result.json"),
    ])
    assert alternate_build.returncode == 0, alternate_build.stdout + alternate_build.stderr
    alternate_report = tmp_path / "alternate-reopened-inspection.json"
    alternate_reopen = _run_blender(REOPEN_DRIVER, profile,
                                    ["--output", str(alternate_report)], blend_file=alternate_artifact,
                                    timeout=600)
    assert alternate_reopen.returncode == 0, alternate_reopen.stdout + alternate_reopen.stderr
    alternate = json.loads(alternate_report.read_text(encoding="utf-8"))
    assert alternate["verdict"]["saved_scene_integrity"] == "pass"
    assert alternate["rig"]["style_controls"] == {
        "hair_style": "crop", "clothing_style": "warmup",
        "skin_palette": "deep", "clothing_palette": "brick",
    }
    assert "MM_Skin_deep" in alternate["character"]["body_materials"]
    assert "MM_Costume_brick" in alternate["garment"]["material_names"]
    assert alternate["garment"]["object_name"] == "Garment_WarmupPants"
    assert alternate["garment"]["stored_vertex_count"] >= garment["stored_vertex_count"]
    assert alternate["character"]["body_bounds_frame_1_world_m"] != state["character"]["body_bounds_frame_1_world_m"]
    alternate_keys = {key["name"]: key["value"] for key in alternate["character"]["shape_keys"]}
    default_keys = {key["name"]: key["value"] for key in state["character"]["shape_keys"]}
    assert alternate_keys["head-scale-horiz-incr"] == 0.21
    assert default_keys["head-scale-horiz-incr"] == 0.16
    assert alternate_keys["l-hand-scale-incr"] == 0.19
    assert default_keys["l-hand-scale-incr"] == 0.12
    assert not any(obj["name"] == "Hair_SweptQuiff" for obj in alternate["objects"])


@pytest.mark.parametrize("palette", ("chalk", "graphite"))
def test_editable_shorts_palette_variants_survive_reopen(tmp_path: Path, palette: str) -> None:
    controls_path = FIXTURE_DIR / f"{palette}-shorts-controls.v1.json"
    assert resolve_controls(json.loads(controls_path.read_text(encoding="utf-8"))["controls"])["clothing_palette"] == palette
    profile = (BASELINE_DIR / "profile").resolve()
    artifact = tmp_path / f"fighter-family-{palette}-v1.1.blend"
    renders = tmp_path / f"{palette}-renders"
    result_path = tmp_path / f"{palette}-build.json"
    build = _run_blender(BUILD_DRIVER, profile, [
        "--controls", str(controls_path), "--output", str(artifact),
        "--renders", str(renders), "--result", str(result_path),
    ])
    assert build.returncode == 0, build.stdout + build.stderr
    assert artifact.is_file()
    assert (renders / "fighter-family-garment-front.png").stat().st_size > 4_000
    report_path = tmp_path / f"{palette}-reopened.json"
    reopened = _run_blender(REOPEN_DRIVER, profile, ["--output", str(report_path)], blend_file=artifact)
    assert reopened.returncode == 0, reopened.stdout + reopened.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["garment"]["object_name"] == "Garment_FightShorts"
    assert f"MM_Costume_{palette}" in report["garment"]["material_names"]
    assert report["garment"]["stored_vertex_count"] >= 500
    assert report["verdict"]["garment_geometry"] == "pass"
