"""T6a review-only Blender scene compilation and independent pass proof."""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from content.video_engine.src.modeling.blender import render, scene


def _fixture_copy(tmp_path: Path, edit) -> Path:
    document = json.loads(scene.DEFAULT_FIXTURE.read_text(encoding="utf-8"))
    edit(document)
    target = tmp_path / "altered.model_scene.v1.json"
    target.write_text(json.dumps(document), encoding="utf-8")
    return target


def test_real_blender_compiles_reopens_and_renders_independent_passes(tmp_path: Path) -> None:
    output = tmp_path / "compiled"
    receipt = scene.compile_and_render(output_root=output)
    compiled = json.loads((output / "compile-state.json").read_text(encoding="utf-8"))

    assert receipt["review_state"] == "review_only"
    assert receipt["render_eligible"] is False
    assert receipt["for_render_requested"] is False
    assert receipt["blender_version"] == "5.2.2 LTS"
    assert receipt["fixture_sha256"] == scene.sha256_file(scene.DEFAULT_FIXTURE)
    assert receipt["compiled_scene_sha256"] == scene.sha256_file(output / "compiled-scene.blend")
    assert receipt["reopened_scene_sha256"] == receipt["compiled_scene_sha256"]
    assert all(receipt["source_hashes_unchanged"].values())
    assert set(receipt["descriptor_hashes"]) == {"prop", "environment"}
    assert set(receipt["source_hashes"]) == {"prop", "environment"}

    state = receipt["reopened_state"]
    assert state["review_state"] == "review_only"
    assert state["render_eligible"] is False
    assert state["source_camera_light_objects"] == []
    assert state["collections"] == ["binding__environment", "binding__prop"]
    assert state["namespaced_tree_counts"] == {"environment": 7, "prop": 7}
    assert all(
        name.startswith(("environment__", "prop__", "compiler_"))
        for name in state["object_names"]
    )
    assert state["hinge_action_present"]
    assert state["hinge_angles_deg"] == {"1": 0.0, "13": -37.242255, "25": -74.484511}
    assert state["socket"] == {
        "object": "prop__Socket_Grip", "parent": "prop__Prop_Base", "socket_id": "grip_socket"
    }
    assert state["environment_floor"]["collision_modifier"] is True
    assert state["environment_floor"]["top_z_m"] == 0.0
    assert all(row["visible"] and not row["hide_render"] for row in state["geometry_meshes"])
    assert {row["binding_id"] for row in state["geometry_meshes"]} == {"prop", "environment"}

    assert compiled["camera"]["projection"] == "ORTHO"
    assert compiled["camera"]["orthographic_scale_m"] == 6.25
    assert {row["name"] for row in compiled["lights"]} == {
        "compiler_light__key", "compiler_light__fill"
    }
    assert compiled["render_profile"]["engine"] == "CYCLES"
    assert compiled["render_profile"]["resolution_px"] == [320, 240]
    assert compiled["render_profile"]["samples"] == 8
    assert set(compiled["source_materials"]["prop"]) == {
        "Backdrop_Indigo", "Ceramic_Cream", "Enamel_Teal", "Hinge_Bronze"
    }
    assert set(compiled["source_materials"]["environment"]) == {
        "Background_Amber", "Floor_Stone", "Foreground_Ink", "Midground_Blue"
    }

    assert {row["frame"] for row in receipt["frames"]} == {1, 13, 25}
    for row in receipt["frames"]:
        metrics = row["metrics"]
        assert metrics["depth_unit"] == "m"
        assert metrics["depth_format"] == "OpenEXR 32-bit float"
        assert metrics["resolution_px"] == [320, 240]
        assert metrics["depth_valid_pixels"] > 0
        assert metrics["depth_min_m"] > 0
        assert metrics["depth_max_m"] < 100
        assert metrics["depth_mask_mismatch_pixels"] == 0
        assert all(count > 0 for count in metrics["mask_pixel_counts"].values())
        assert set(metrics["mask_pixel_counts"]) == {"prop", "environment"}
        assert metrics["alpha_nonzero_pixels"] > 0
        # The alpha edge is antialiased; hard binding-ID masks use a 0.5 threshold.
        assert metrics["alpha_mask_edge_mismatch_pixels"] < metrics["alpha_nonzero_pixels"]
        for key in ("beauty", "depth"):
            assert scene.sha256_file(Path(row["outputs"][key])) == row["output_sha256"][key]
        for binding_id, path in row["outputs"]["masks"].items():
            assert scene.sha256_file(Path(path)) == row["output_sha256"]["masks"][binding_id]

    parity = receipt["seek_parity"]
    assert parity["verified"] is True
    assert parity["order"] == [13, 1, 25]
    assert parity["repeat_order"] == [25, 1, 13]
    assert {row["frame"] for row in parity["frames"]} == {1, 13, 25}
    assert all(row["same_decoded_pixels"] for row in parity["frames"])


def test_rejects_stale_descriptor_and_source_hashes(tmp_path: Path) -> None:
    stale_scene = _fixture_copy(
        tmp_path, lambda document: document["bindings"][0].update(descriptor_sha256="0" * 64)
    )
    with pytest.raises(scene.SceneCompileError, match="descriptor"):
        scene._validate_scene_document(stale_scene, scene.ROOT)

    source = tmp_path / "editable.blend"
    source.write_bytes(b"BLENDER" + b"x" * 51_000)
    descriptor = tmp_path / "descriptor.json"
    descriptor.write_text(json.dumps({
        "asset_id": "test-prop", "asset_kind": "prop", "revision": {"revision_id": "r1"},
        "resources": [{"resource_kind": "editable_source", "path": "editable.blend", "sha256": "0" * 64}],
    }), encoding="utf-8")
    binding = {"binding_id": "prop", "asset_id": "test-prop", "revision_id": "r1",
               "descriptor_path": "descriptor.json", "descriptor_sha256": scene.sha256_file(descriptor)}
    with pytest.raises(scene.SceneCompileError, match="stale editable source hash"):
        scene._binding_sources({"bindings": [binding]}, tmp_path)


def test_rejects_unsupported_passes(tmp_path: Path) -> None:
    altered = _fixture_copy(
        tmp_path, lambda document: document["render_profile"]["passes"].append("normal")
    )
    with pytest.raises(scene.SceneCompileError, match="unsupported render passes: normal"):
        scene._validate_scene_document(altered, scene.ROOT)


def test_rejects_existing_and_redirected_output_roots(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = tmp_path / "existing"
    existing.mkdir()
    with pytest.raises(scene.SceneCompileError, match="new and exclusive"):
        scene._checked_output_root(existing, must_be_new=True)

    # The path guard is also exercised when Windows marks an ancestor as a junction.
    redirected = tmp_path / "redirected"
    redirected.mkdir()
    monkeypatch.setattr(scene, "_path_redirected", lambda path: path == redirected)
    with pytest.raises(scene.SceneCompileError, match="symlink or junction"):
        scene._checked_output_root(redirected / "derived", must_be_new=True)
    monkeypatch.undo()

    link = tmp_path / "link"
    try:
        os.symlink(existing, link, target_is_directory=True)
    except (OSError, NotImplementedError):
        return  # The path-guard branch was verified above; symlink privilege is optional.
    with pytest.raises(scene.SceneCompileError, match="symlink or junction"):
        scene._checked_output_root(link / "derived", must_be_new=True)


def test_rejects_missing_duplicate_controls_and_hidden_or_empty_geometry() -> None:
    with pytest.raises(scene.SceneCompileError, match="found 0"):
        scene.resolve_control([], "lid_hinge", "articulation_id")
    with pytest.raises(scene.SceneCompileError, match="found 2"):
        scene.resolve_control(
            [{"articulation_id": "lid_hinge"}, {"articulation_id": "lid_hinge"}],
            "lid_hinge", "articulation_id",
        )
    row = {"binding_id": "prop", "object_type": "MESH", "object_name": "prop__mesh",
           "vertices": 8, "polygons": 6, "evaluated_vertices": 8,
           "evaluated_polygons": 6, "hide_render": False, "hide_viewport": False, "visible": True}
    with pytest.raises(scene.SceneCompileError, match="hidden mesh geometry"):
        scene.validate_geometry_rows([{**row, "hide_render": True}], {"prop"})
    with pytest.raises(scene.SceneCompileError, match="empty mesh geometry"):
        scene.validate_geometry_rows([{**row, "evaluated_polygons": 0}], {"prop"})


def test_blender_render_failure_is_fatal_and_preserves_logs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(scene.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(
        returncode=17, stdout="render began", stderr="Cycles render failed",
    ))
    with pytest.raises(scene.SceneCompileError, match="Blender render worker failed"):
        scene._run_blender_worker(
            blender=scene._default_blender(), script=Path(render.__file__),
            output_root=tmp_path, stage="render", arguments=[],
        )
    assert (tmp_path / "logs/render-stdout.txt").read_text(encoding="utf-8") == "render began"
    assert (tmp_path / "logs/render-stderr.txt").read_text(encoding="utf-8") == "Cycles render failed"


def test_failed_render_cannot_overwrite_its_prior_logs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def failed_render(*args, **kwargs):
        calls.append(True)
        return SimpleNamespace(returncode=17, stdout="first stdout", stderr="first stderr")

    monkeypatch.setattr(scene.subprocess, "run", failed_render)
    arguments = {"blender": scene._default_blender(), "script": Path(render.__file__),
                 "output_root": tmp_path, "stage": "render", "arguments": []}
    with pytest.raises(scene.SceneCompileError, match="worker failed"):
        scene._run_blender_worker(**arguments)
    with pytest.raises(scene.SceneCompileError, match="refusing to reuse"):
        scene._run_blender_worker(**arguments)
    assert len(calls) == 1
    assert (tmp_path / "logs/render-stdout.txt").read_text(encoding="utf-8") == "first stdout"
    assert (tmp_path / "logs/render-stderr.txt").read_text(encoding="utf-8") == "first stderr"


def test_redirected_log_directory_is_rejected_before_blender(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    monkeypatch.setattr(scene, "_path_redirected", lambda path: path == logs)

    def should_not_run(*args, **kwargs):
        pytest.fail("Blender must not run with a redirected log directory")

    monkeypatch.setattr(scene.subprocess, "run", should_not_run)
    with pytest.raises(scene.SceneCompileError, match="symlink or junction"):
        scene._run_blender_worker(
            blender=scene._default_blender(), script=Path(render.__file__),
            output_root=tmp_path, stage="render", arguments=[],
        )
