from __future__ import annotations

import copy
import hashlib
from pathlib import Path

from content.video_engine.src.guards.editorial_motion_qc import run_editorial_motion_qc
from content.video_engine.src.services.editorial_motion import build_default_pacing_recipe
from content.video_engine.src.services.history_contracts import canonical_sha256


def _hashed(core: dict) -> dict:
    return {**core, "artifact_hash": canonical_sha256(core)}


def _shot(shot_id: str, start: float, duration: float, asset_id: str, *, moving: bool = False) -> dict:
    camera = {
        "kind": "push_settle" if moving else "locked",
        "amount": 0.018 if moving else 0.0,
        "easing": "smoothstep",
        "direction": "toward_focal_point",
        "hold_in_s": 0.25 if moving else duration,
        "move_s": duration - 0.65 if moving else 0.0,
        "hold_out_s": 0.4 if moving else 0.0,
    }
    return {
        "shot_id": shot_id,
        "parent_beat_ids": ["beat-one"],
        "parent_scene_bundle_id": "bundle-one",
        "start_s": start,
        "duration_s": duration,
        "word_range": {"start_index": int(start), "end_index": int(start)},
        "narration_excerpt": "Words.",
        "purpose": "reveal",
        "shot_scale": "wide" if not moving else "medium",
        "focal_point": {"x": 0.5, "y": 0.5},
        "layers": [{"asset_id": asset_id, "role": "world"}],
        "subject_action": "none",
        "ambient_actions": ["lamp_flicker"],
        "information_reveal": "none",
        "camera": camera,
        "transition_in": {"kind": "hard_cut", "reason": "phrase"},
        "transition_out": {"kind": "hard_cut", "reason": "phrase"},
        "audio_bridge": "continuous_narration",
        "provider_motion": {"requirement": "none", "fallback": "local_layer_motion"},
        "overlay_ids": [],
        "uniqueness_signature": f"{shot_id}-signature",
    }


def _fixture(tmp_path: Path) -> tuple[dict, dict, Path, Path, Path]:
    asset_root = tmp_path / "assets"
    asset_root.mkdir(exist_ok=True)
    image = asset_root / "world.png"
    image.write_bytes(b"image")
    asset_core = {
        "assets": {
            "world-one": {
                "path": "world.png",
                "sha256": hashlib.sha256(b"image").hexdigest(),
                "render_eligible": True,
                "human_promoted": True,
            }
        }
    }
    asset_map = _hashed(asset_core)
    plan_core = {
        "schema_version": "editorial_motion_plan.v1",
        "source_storyboard_hash": "1" * 64,
        "source_beat_plan_hash": "2" * 64,
        "scene_bundle_hashes": ["3" * 64],
        "scene_flow_graph_hash": "4" * 64,
        "asset_map_hash": asset_map["artifact_hash"],
        "audio_manifest_hash": "5" * 64,
        "pacing_recipe_hash": build_default_pacing_recipe()["artifact_hash"],
        "duration_s": 3.0,
        "source_start_s": 0.0,
        "shots": [_shot("shot-one", 0.0, 3.0, "world-one")],
        "provider_calls": 0,
        "revision_only": True,
    }
    job = tmp_path / "job"
    revision = job / "animatic" / "revisions" / "editorial-motion-v1"
    return _hashed(plan_core), asset_map, asset_root, job, revision


def _run(tmp_path: Path, **overrides):
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    values = {
        "plan": plan,
        "pacing_recipe": build_default_pacing_recipe(),
        "asset_map": assets,
        "asset_root": asset_root,
        "job_dir": job,
        "revision_dir": revision,
    }
    values.update(overrides)
    return run_editorial_motion_qc(**values)


def _detail(result: dict, check_id: str) -> str:
    return next(item["detail"] for item in result["checks"] if item["check_id"] == check_id)


def test_qc_passes_structural_fixture_but_requires_human_review(tmp_path: Path) -> None:
    result = _run(tmp_path)
    assert result["overall"] == "pass"
    assert result["structural_pass"] is True
    assert result["human_review_required"] is True
    assert result["quality_claim"].startswith("none")


def test_qc_verifies_adapter_manifest_and_contained_file_hashes(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    contained = revision / "public" / "proof.bin"
    contained.parent.mkdir(parents=True, exist_ok=True)
    contained.write_bytes(b"proof")
    recipe = build_default_pacing_recipe()
    manifest_core = {
        "schema_version": "martial_editorial_adapter_manifest.v1",
        "revision_id": revision.name,
        "motion_plan_hash": plan["artifact_hash"],
        "asset_map_hash": assets["artifact_hash"],
        "pacing_recipe_hash": recipe["artifact_hash"],
        "contained_file_hashes": [
            {"path": "public/proof.bin", "sha256": hashlib.sha256(b"proof").hexdigest()}
        ],
    }
    manifest = _hashed(manifest_core)

    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
        pacing_recipe=recipe,
        adapter_manifest=manifest,
    )

    assert result["overall"] == "pass"
    assert "hash-bound" in _detail(result, "adapter_manifest_integrity")


def test_qc_rejects_stale_adapter_contained_file(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    contained = revision / "public" / "proof.bin"
    contained.parent.mkdir(parents=True, exist_ok=True)
    contained.write_bytes(b"changed")
    recipe = build_default_pacing_recipe()
    manifest_core = {
        "schema_version": "martial_editorial_adapter_manifest.v1",
        "revision_id": revision.name,
        "motion_plan_hash": plan["artifact_hash"],
        "asset_map_hash": assets["artifact_hash"],
        "pacing_recipe_hash": recipe["artifact_hash"],
        "contained_file_hashes": [{"path": "public/proof.bin", "sha256": "0" * 64}],
    }

    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
        pacing_recipe=recipe,
        adapter_manifest=_hashed(manifest_core),
    )

    assert result["overall"] == "fail"
    assert "stale hash" in _detail(result, "adapter_manifest_integrity")


def test_qc_accepts_localized_ambient_actions(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    plan["shots"][0]["ambient_actions"] = ["cloud_drift", "river_flow", "ship_wake"]
    plan = _hashed({key: value for key, value in plan.items() if key != "artifact_hash"})
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert result["overall"] == "pass"
    assert "layer ownership" in _detail(result, "motion_discipline")


def test_qc_treats_archival_portrait_as_evidence_prop(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    assets["assets"]["portrait-one"] = {
        "path": "world.png",
        "sha256": hashlib.sha256(b"image").hexdigest(),
        "render_eligible": True,
        "human_promoted": True,
        "kind": "archival_portrait",
    }
    assets = _hashed({"assets": assets["assets"]})
    plan["asset_map_hash"] = assets["artifact_hash"]
    plan["shots"][0]["layers"].append(
        {"asset_id": "portrait-one", "role": "prop", "action": "reveal"}
    )
    plan = _hashed({key: value for key, value in plan.items() if key != "artifact_hash"})
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert result["overall"] == "pass"
    assert "non-evidence props" in _detail(result, "editorial_value_discipline")
def test_qc_rejects_stale_plan_hash(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    plan["duration_s"] = 4.0
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert result["overall"] == "fail"
    assert "stale" in result["checks"][0]["detail"]


def test_qc_rejects_stale_asset_hash(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    assets["assets"]["world-one"]["render_eligible"] = False
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert result["overall"] == "fail"
    assert "asset map hash" in _detail(result, "asset_map_hash_integrity")


def test_qc_rejects_path_escape(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    assets["assets"]["world-one"]["path"] = "../outside.png"
    assets = _hashed({"assets": assets["assets"]})
    plan["asset_map_hash"] = assets["artifact_hash"]
    plan = _hashed({key: value for key, value in plan.items() if key != "artifact_hash"})
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert "escapes" in _detail(result, "asset_resolution")


def test_qc_rejects_revision_escape(tmp_path: Path) -> None:
    result = _run(tmp_path, revision_dir=tmp_path / "outside")
    assert result["overall"] == "fail"
    assert "escapes" in _detail(result, "revision_path_containment")


def test_qc_rejects_unpromoted_provider_asset(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    assets["assets"]["world-one"].update({"provider_output": True, "human_promoted": False})
    assets = _hashed({"assets": assets["assets"]})
    plan["asset_map_hash"] = assets["artifact_hash"]
    plan = _hashed({key: value for key, value in plan.items() if key != "artifact_hash"})
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert "unpromoted provider output" in _detail(result, "asset_resolution")


def test_qc_rejects_undeclared_whole_frame_layer_movement(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    plan["shots"][0]["layers"][0]["action"] = "background_pan"
    plan = _hashed({key: value for key, value in plan.items() if key != "artifact_hash"})
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert "whole-frame movement" in _detail(result, "motion_discipline")


def test_qc_rejects_a_visual_hold_over_six_seconds(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    plan["shots"][0]["duration_s"] = 6.1
    plan["shots"][0]["camera"]["hold_in_s"] = 6.1
    plan["duration_s"] = 6.1
    plan = _hashed({key: value for key, value in plan.items() if key != "artifact_hash"})
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert result["overall"] == "fail"
    assert "visual-hold ceiling" in _detail(result, "motion_discipline")


def test_qc_reports_supplied_upstream_hash_mismatch(tmp_path: Path) -> None:
    result = _run(tmp_path, expected_hashes={"source_storyboard_hash": "9" * 64})
    assert result["overall"] == "fail"
    assert "source_storyboard_hash" in _detail(result, "upstream_hash_integrity")


def test_qc_rejects_information_surface_over_character(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    plan["shots"][0]["layers"].append(
        {
            "asset_id": "world-one",
            "role": "character",
            "layout": {"x": 0.6, "y": 0.1, "width": 0.3, "height": 0.7},
        }
    )
    plan["shots"][0]["information_surface"] = {
        "mode": "surface_ink",
        "x": 0.65,
        "y": 0.15,
        "width": 0.2,
        "height": 0.12,
    }
    plan = _hashed({key: value for key, value in plan.items() if key != "artifact_hash"})
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert result["overall"] == "fail"
    assert "overlaps character" in _detail(result, "information_surface_safety")


def test_qc_rejects_information_surface_above_recipe_limit(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    plan["shots"][0]["information_surface"] = {
        "mode": "surface_ink",
        "x": 0.1,
        "y": 0.1,
        "width": 0.2,
        "height": 0.12,
    }
    plan = _hashed({key: value for key, value in plan.items() if key != "artifact_hash"})
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert result["overall"] == "fail"
    assert "exceed the recipe limit" in _detail(result, "editorial_value_discipline")


def test_qc_rejects_repeated_non_evidence_prop_layers(tmp_path: Path) -> None:
    plan, assets, asset_root, job, revision = _fixture(tmp_path)
    plan["shots"][0]["layers"].extend(
        [
            {"asset_id": "world-one", "role": "prop"},
            {"asset_id": "world-one", "role": "prop"},
        ]
    )
    plan = _hashed({key: value for key, value in plan.items() if key != "artifact_hash"})
    result = _run(
        tmp_path,
        plan=plan,
        asset_map=assets,
        asset_root=asset_root,
        job_dir=job,
        revision_dir=revision,
    )
    assert result["overall"] == "fail"
    assert "non-evidence prop layers" in _detail(result, "editorial_value_discipline")
