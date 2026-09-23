"""Offline T4c prop/environment fixtures, saved-scene state and model contract."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
from tempfile import TemporaryDirectory

from content.video_engine.src.modeling.contracts import validate_model_asset, validate_model_scene


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "content/video_engine/tests/fixtures/modeling/generalization"
SPECS = ROOT / "content/video_engine/assets/modeling/native/generalization/asset-specs.v1.json"
NATIVE = SPECS.parent
BLENDER_INPUTS = ROOT / "content/video_engine/tests/fixtures/modeling/baseline/benchmark-inputs.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                            env={**os.environ, "PYTHONNOUSERSITE": "1"}, timeout=180, check=False)
    assert result.returncode == 0, f"command failed ({result.returncode}):\n{result.stdout}\n{result.stderr}"


def _png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", header[16:24])


def test_canonical_native_sources_and_manifests_are_hash_pinned() -> None:
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    manifest = json.loads((NATIVE / "diagnostic-manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "diagnostic_only"
    assert manifest["art_approval"] == "not_approved"
    assert manifest["provider_calls"] == 0
    scene_path = ROOT / manifest["scene_binding_path"]
    assert scene_path.is_relative_to(NATIVE)
    assert manifest["scene_binding_sha256"] == _sha256(scene_path)
    scene = validate_model_scene(scene_path, project_root=ROOT)
    assert {row["binding_id"] for row in scene["bindings"]} == {"prop", "environment"}
    for kind, spec in specs["assets"].items():
        entry = manifest["assets"][kind]
        source = ROOT / entry["editable_source"]
        descriptor_path = ROOT / entry["descriptor_path"]
        assert source == NATIVE / spec["source"]
        assert source.is_file() and source.stat().st_size > 50_000
        assert entry["editable_source_sha256"] == _sha256(source)
        assert descriptor_path.is_relative_to(NATIVE)
        assert entry["descriptor_sha256"] == _sha256(descriptor_path)
        descriptor = validate_model_asset(descriptor_path, project_root=ROOT)
        assert descriptor["asset_kind"] == kind
        assert descriptor["capabilities"] == spec["capabilities"]
        assert entry["review_state"] == "review_only"
        assert entry["render_eligible"] is False
        per_asset_path = NATIVE / f"{spec['asset_id']}.manifest.json"
        per_asset = json.loads(per_asset_path.read_text(encoding="utf-8"))
        assert per_asset["editable_source_sha256"] == _sha256(source)
        assert per_asset["descriptor_sha256"] == _sha256(descriptor_path)
        assert per_asset["art_approval"] == "not_approved"


def test_nonfighter_scenes_reopen_render_and_validate_as_review_only() -> None:
    blender = Path(json.loads(BLENDER_INPUTS.read_text(encoding="utf-8"))["tools"]["blender"]["path"])
    assert blender.is_file()
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    assert specs["status"] == "diagnostic_only"
    assert specs["art_approval"] == "not_approved"
    assert specs["provider_calls"] == 0
    assert {row["asset_kind"] for row in specs["assets"].values()} == {"prop", "environment"}
    for row in specs["assets"].values():
        assert not {"semantic_joints", "face_controls", "proportion_parameters"} & set(row["capabilities"])

    with TemporaryDirectory(prefix="t4c-") as directory:
        project = Path(directory)
        sources = project / "sources"
        renders = project / "renders"
        sources.mkdir()
        renders.mkdir()
        reports = {}
        for kind, spec in specs["assets"].items():
            source = sources / spec["source"]
            build_result = project / f"{kind}-build.json"
            _run([str(blender), "--background", "--factory-startup", "--offline-mode",
                  "--disable-autoexec", "--python-exit-code", "17", "--python",
                  str(FIXTURE / "build_scenes.py"), "--", "--kind", kind,
                  "--output", str(source), "--renders", str(renders), "--result", str(build_result)])
            assert source.stat().st_size > 50_000
            assert json.loads(build_result.read_text(encoding="utf-8"))["blender_version"] == "5.2.2 LTS"
            report_path = project / f"{kind}-inspection.json"
            _run([str(blender), "--background", "--factory-startup", "--offline-mode",
                  "--disable-autoexec", "--python-exit-code", "17", str(source),
                  "--python", str(FIXTURE / "inspect_saved_scene.py"), "--",
                  "--output", str(report_path)])
            reports[kind] = json.loads(report_path.read_text(encoding="utf-8"))
            assert reports[kind]["source"] == str(source)
            assert reports[kind]["resolution_px"] == [540, 960]
            assert reports[kind]["armature_objects"] == []
            assert reports[kind]["status"] == "diagnostic_only"

        prop = reports["prop"]
        assert prop["fixture_kind"] == "hinged_prop"
        assert {"Prop_Base", "Prop_Lid", "Hinge_Pivot", "Socket_Grip"} <= set(prop["objects"])
        assert prop["hinge_action_present"]
        assert abs(prop["hinge_angles_deg"]["1"]) < 0.01
        assert -80 < prop["hinge_angles_deg"]["25"] < -70
        assert prop["lid_parent"] == "Hinge_Pivot"
        assert prop["socket_parent"] == "Prop_Base"
        assert prop["socket_id"] == "grip_socket"
        assert all(abs(actual - expected) < 0.001 for actual, expected in
                   zip(prop["socket_world_location_m"], (0.0, -0.43, 0.30)))

        environment = reports["environment"]
        assert environment["fixture_kind"] == "layered_environment"
        assert environment["floor_surface_id"] == "floor"
        assert environment["floor_collision_role"] == "solid"
        assert environment["floor_has_collision_modifier"]
        assert abs(environment["floor_top_z_m"]) < 0.001
        layers = environment["layers"]
        assert layers["Foreground_Occluder"]["role"] == "foreground_occluder"
        assert layers["Midground_Dais"]["role"] == "midground"
        assert layers["Background_Wall"]["role"] == "background"
        assert layers["Foreground_Occluder"]["depth_y_m"] < layers["Midground_Dais"]["depth_y_m"]
        assert layers["Midground_Dais"]["depth_y_m"] < layers["Background_Wall"]["depth_y_m"]

        for name in ("hinged-prop-closed.png", "hinged-prop-open.png",
                     "environment-three-quarter.png", "environment-front.png"):
            path = renders / name
            assert path.stat().st_size > 4_000
            assert _png_size(path) == (540, 960)
        assert _sha256(renders / "hinged-prop-closed.png") != _sha256(renders / "hinged-prop-open.png")
        assert _sha256(renders / "environment-three-quarter.png") != _sha256(renders / "environment-front.png")

        manifest_path = project / "diagnostic-manifest.json"
        _run([sys.executable, str(FIXTURE / "validate_diagnostics.py"),
              "--source-dir", str(sources), "--project-root", str(project),
              "--contract-dir", str(project / "contract"), "--render-dir", str(renders),
              "--manifest", str(manifest_path)])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["status"] == "diagnostic_only"
        assert manifest["art_approval"] == "not_approved"
        scene_path = Path(manifest["scene_binding_path"])
        assert manifest["scene_binding_sha256"] == _sha256(scene_path)
        scene = validate_model_scene(scene_path, project_root=project)
        assert {binding["binding_id"] for binding in scene["bindings"]} == {"prop", "environment"}
        assert scene["motion_channels"][0]["semantic_target"] == "lid_hinge"
        assert scene["environment_collision_surfaces"][0]["surface_id"] == "floor"
        for kind, row in manifest["assets"].items():
            assert row["editable_source_sha256"] == _sha256(Path(row["editable_source"]))
            assert row["descriptor_sha256"] == _sha256(Path(row["descriptor_path"]))
            descriptor = validate_model_asset(row["descriptor_path"], project_root=project)
            assert descriptor["asset_kind"] == kind
            assert row["review_state"] == "review_only"
            assert row["render_eligible"] is False
