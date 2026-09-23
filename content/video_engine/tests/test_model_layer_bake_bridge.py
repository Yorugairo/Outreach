"""Saved Blender to fixed-view raster bridge, including native geometry evidence."""

from __future__ import annotations

from array import array
import copy
from fractions import Fraction
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest
from PIL import Image

from content.video_engine.src.modeling.bake_layers import (
    BakeError,
    FRAMES,
    SOURCE,
    bake_bridge,
    pinned_source,
    run_blender,
    sha256,
    validate_bundle,
)
from content.video_engine.src.modeling.layered import LayeredScene


@pytest.fixture(scope="module")
def bundle(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path, Path, dict]:
    root = tmp_path_factory.mktemp("saved-blender-bridge")
    fixture = root / "fixture"
    evidence = root / "evidence"
    before = sha256(SOURCE)
    receipt_path = bake_bridge(fixture, evidence)
    assert sha256(SOURCE) == before == pinned_source()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    return fixture, evidence, receipt_path, receipt


def _mutated_receipt(tmp_path: Path, original: dict, change) -> Path:
    receipt = copy.deepcopy(original)
    change(receipt)
    path = tmp_path / "receipt-mutated.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    return path


def test_rejects_existing_and_symlinked_output_roots_without_writing(tmp_path: Path) -> None:
    existing = tmp_path / "existing"
    existing.mkdir()
    sentinel = existing / "neutral-beauty.png"
    sentinel.write_bytes(b"do not replace")
    with pytest.raises(BakeError, match="must be new"):
        run_blender("inspect", existing)
    with pytest.raises(BakeError, match="must be new"):
        bake_bridge(existing, tmp_path / "evidence")
    with pytest.raises(BakeError, match="must be new"):
        bake_bridge(tmp_path / "fixture", existing)
    with pytest.raises(BakeError, match="non-nested"):
        bake_bridge(tmp_path / "fixture", tmp_path / "fixture" / "evidence")
    assert sentinel.read_bytes() == b"do not replace"
    assert not (tmp_path / "evidence").exists()
    assert not (tmp_path / "fixture").exists()

    link = tmp_path / "linked-parent"
    try:
        link.symlink_to(existing, target_is_directory=True)
    except (OSError, NotImplementedError):
        pass  # Windows may deny symlink creation without developer mode.
    else:
        with pytest.raises(BakeError, match="symlink"):
            run_blender("inspect", link / "new-evidence")
        with pytest.raises(BakeError, match="symlink"):
            bake_bridge(tmp_path / "new-fixture", link / "new-evidence")
        assert sentinel.read_bytes() == b"do not replace"

    if os.name == "nt":
        junction = tmp_path / "junction-parent"
        created = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(existing)],
                                 capture_output=True, text=True, check=False)
        assert created.returncode == 0, created.stderr
        with pytest.raises(BakeError, match="junction"):
            run_blender("inspect", junction / "new-evidence")
        with pytest.raises(BakeError, match="junction"):
            bake_bridge(tmp_path / "new-fixture", junction / "new-evidence")
        assert sentinel.read_bytes() == b"do not replace"


def test_real_blender_bakes_fixed_front_camera_and_independent_geometry_depth(bundle) -> None:
    fixture, evidence, receipt_path, receipt = bundle
    result = validate_bundle(receipt_path, fixture, evidence)
    state = json.loads((evidence / "blender-state.json").read_text(encoding="utf-8"))
    assert state["blender_version"].startswith("5.2.2")
    assert state["blender_build_hash"] == "d13f752e3b9c"
    assert state["camera"]["object"] == "ReviewCamera_front"
    assert state["camera"]["projection"] == "ORTHO"
    assert state["camera"]["resolution_px"] == [512, 768]
    assert state["floor_hidden_in_working_process"] is True
    assert "Human" in state["visible_meshes"]
    assert "Garment_FightShorts" in state["visible_meshes"]
    assert "Diagnostic_Floor" not in state["visible_meshes"]
    assert "BVH ray cast" in state["mask_method"]
    assert receipt["source_frame_to_diagnostic_frame"] == {"1": 0, "27": 27, "52": 52}
    assert receipt["source"]["sha256"] == receipt["source"]["sha256_after"] == pinned_source()
    assert receipt["review_state"] == "review_only" and receipt["render_eligible"] is False
    assert "dimensionless" in receipt["layer_depth_units"]
    assert "metres" in receipt["depth_units"]
    assert receipt["alpha_mask_alignment_tolerance"] == {
        "bounds_px": 2, "interior_fraction": 0.005, "interior_pixels_floor": 64,
    }
    assert all(row["geometry_pixels"] > 70_000 and row["interior_mismatch_pixels"] < 64
               for row in result.values())
    assert all(row["depth_max_m"] > row["depth_min_m"] > 6 for row in result.values())
    assert (evidence / "matched-sheet.png").is_file()


def test_layered_scene_has_exact_24fps_probe_states_without_combat_and_random_seek(bundle) -> None:
    fixture, _, _, _ = bundle
    scene = LayeredScene.load(fixture / "bridge-scene.v1.json", asset_root=fixture)
    assert scene.timeline.clock.fps == Fraction(24, 1)
    assert scene.yaw_limits == (0, 0) and scene.pitch_limits == (0, 0)
    assert [scene.evaluate(frame).selected_states["generic-fighter"]["pose"]
            for frame in (0, 26, 27, 51, 52, 71)] == [
                "neutral", "neutral", "arm_stress", "arm_stress", "leg_stress", "leg_stress"]
    assert all(not scene.evaluate(frame).events and not scene.evaluate(frame).contacts
               for frame in (0, 27, 52, 71))
    frames = (52, 0, 27, 41, 0, 52, 12, 27)
    first = {frame: scene.render(frame, supersample=1).image.tobytes() for frame in frames}
    for frame in (71, 12, 51, 1, 29):
        scene.render(frame, supersample=1)
    assert first == {frame: scene.render(frame, supersample=1).image.tobytes() for frame in frames}
    assert first[0] != first[27] != first[52]


def test_rejects_stale_source_and_output_hashes(bundle, tmp_path: Path) -> None:
    fixture, evidence, _, receipt = bundle
    altered_source = tmp_path / "altered.blend"
    altered_source.write_bytes(SOURCE.read_bytes() + b"stale")
    with pytest.raises(BakeError, match="source SHA-256"):
        run_blender("inspect", tmp_path / "inspect", source=altered_source)
    changed = _mutated_receipt(tmp_path, receipt,
                               lambda row: row["states"]["neutral"]["beauty"].update(sha256="0" * 64))
    with pytest.raises(BakeError, match="beauty SHA-256"):
        validate_bundle(changed, fixture, evidence)


def test_rejects_stale_implementation_and_review_sheet_hashes(bundle, tmp_path: Path) -> None:
    fixture, evidence, _, receipt = bundle
    changed = _mutated_receipt(tmp_path, receipt,
                               lambda row: row.update(implementation_sha256="0" * 64))
    with pytest.raises(BakeError, match="implementation SHA-256"):
        validate_bundle(changed, fixture, evidence)
    changed = _mutated_receipt(tmp_path, receipt,
                               lambda row: row["matched_sheet"].update(sha256="0" * 64))
    with pytest.raises(BakeError, match="review sheet SHA-256"):
        validate_bundle(changed, fixture, evidence)


def test_rejects_unsafe_path_and_unsupported_view(bundle, tmp_path: Path) -> None:
    fixture, evidence, _, receipt = bundle
    changed = _mutated_receipt(tmp_path, receipt,
                               lambda row: row["states"]["neutral"]["beauty"].update(path="../escape.png"))
    with pytest.raises(BakeError, match="escapes"):
        validate_bundle(changed, fixture, evidence)

    fixture_copy = tmp_path / "fixture-view"
    shutil.copytree(fixture, fixture_copy)
    scene_path = fixture_copy / "bridge-scene.v1.json"
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    scene["view_envelope_deg"]["yaw_deg"] = [-5, 5]
    scene_path.write_text(json.dumps(scene), encoding="utf-8")
    changed = _mutated_receipt(tmp_path, receipt,
                               lambda row: row["scene"].update(sha256=sha256(scene_path)))
    with pytest.raises(BakeError, match="unsupported authored view"):
        validate_bundle(changed, fixture_copy, evidence)


def test_rejects_hidden_or_empty_geometry_from_real_blender_and_receipt(bundle, tmp_path: Path) -> None:
    fixture, evidence, _, receipt = bundle
    with pytest.raises(BakeError, match="Blender bake failed"):
        run_blender("bake", tmp_path / "hidden", hide_character=True)
    assert "required visible character geometry missing or hidden: Human" in (
        tmp_path / "hidden" / "blender-stderr.txt").read_text(encoding="utf-8")

    evidence_copy = tmp_path / "evidence-empty"
    shutil.copytree(evidence, evidence_copy)
    mask_path = evidence_copy / "neutral-mask.png"
    Image.new("L", (512, 768), 0).save(mask_path)
    changed = _mutated_receipt(tmp_path, receipt,
                               lambda row: row["states"]["neutral"]["mask"].update(sha256=sha256(mask_path)))
    with pytest.raises(BakeError, match="empty or hidden character geometry"):
        validate_bundle(changed, fixture, evidence_copy)


def test_rejects_alpha_mask_and_depth_misalignment_even_with_updated_hashes(bundle, tmp_path: Path) -> None:
    fixture, evidence, _, receipt = bundle
    evidence_copy = tmp_path / "evidence-depth"
    shutil.copytree(evidence, evidence_copy)
    depth_path = evidence_copy / "neutral-depth.f32"
    depths = array("f")
    depths.frombytes(depth_path.read_bytes())
    first_geometry = next(i for i, value in enumerate(depths) if value > 0)
    depths[first_geometry] = 0
    depth_path.write_bytes(depths.tobytes())
    changed = _mutated_receipt(tmp_path, receipt,
                               lambda row: row["states"]["neutral"]["depth_f32"].update(sha256=sha256(depth_path)))
    with pytest.raises(BakeError, match="lacks finite camera-space depth"):
        validate_bundle(changed, fixture, evidence_copy)

    fixture_copy = tmp_path / "fixture-alpha"
    shutil.copytree(fixture, fixture_copy)
    beauty_path = fixture_copy / "neutral-beauty.png"
    with Image.open(beauty_path) as source:
        image = source.convert("RGBA")
    image.putpixel((0, 0), (255, 0, 0, 255))
    image.save(beauty_path)
    evidence_alpha = tmp_path / "evidence-alpha"
    shutil.copytree(evidence, evidence_alpha)
    shutil.copyfile(beauty_path, evidence_alpha / "neutral-beauty.png")
    def update_beauty_hashes(row: dict) -> None:
        row["states"]["neutral"]["beauty"]["sha256"] = sha256(beauty_path)
        row["states"]["neutral"]["blender_beauty"]["sha256"] = sha256(beauty_path)

    changed = _mutated_receipt(tmp_path, receipt, update_beauty_hashes)
    with pytest.raises(BakeError, match="bounds are misaligned"):
        validate_bundle(changed, fixture_copy, evidence_alpha)
