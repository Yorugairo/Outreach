from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from content.video_engine.src.services.editorial_motion import (
    EditorialMotionError,
    canonical_sha256,
    validate_editorial_motion_plan,
)
from content.video_engine.src.services.finance_channel import (
    FinanceChannelValidationError,
    validate_artifact,
    validate_finance_layered_composition_package,
    with_artifact_hash,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
PILOT_ROOT = REPO_ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
PLAN_PATH = PILOT_ROOT / "edit/sentence-native-v1/layered-composition-plan.v1.json"
SCRIPT_PATH = REPO_ROOT / "content/video_engine/scripts/compile_finance_layered_composition.py"
WORDS_PATH = PILOT_ROOT / "audio/canonical/history_episode_1_master.words.json"


def _load_compiler():
    spec = importlib.util.spec_from_file_location("finance_layered_compiler", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _plan() -> dict:
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def test_checked_in_layered_plan_covers_202_beats_and_all_six_roles() -> None:
    plan = _plan()
    assert validate_artifact(plan)["artifact_hash"] == plan["artifact_hash"]
    assert validate_finance_layered_composition_package(plan, REPO_ROOT)["cue_count"] == 202
    assert plan["summary"]["cue_count"] == 202
    assert plan["summary"]["camera_only_cue_count"] == 0
    assert plan["summary"]["non_evidence_three_plus_layer_ratio"] >= 0.7
    assert set(plan["summary"]["role_counts"]) == {
        "world", "subject", "prop", "mechanism", "evidence", "transition"
    }
    assert all(len(cue["layers"]) >= 3 for cue in plan["cues"])


def test_layer_actions_bind_to_exact_canonical_word_times() -> None:
    plan = _plan()
    words = json.loads(WORDS_PATH.read_text(encoding="utf-8"))["words"]
    for cue in plan["cues"]:
        for layer in cue["layers"]:
            action_index = layer["action_word_range"]["start_index"]
            assert layer["action_word_range"]["end_index"] == action_index
            assert layer["action_time_range"] == {
                "start_s": words[action_index]["start_s"],
                "end_s": words[action_index]["end_s"],
            }
            assert cue["word_range"]["start_index"] <= action_index <= cue["word_range"]["end_index"]


def test_layered_compiler_is_deterministic() -> None:
    module = _load_compiler()
    assert module.compile_plan(PILOT_ROOT) == module.compile_plan(PILOT_ROOT) == _plan()


def test_finance_validator_rejects_camera_only_and_action_range_drift() -> None:
    plan = _plan()
    camera_only = copy.deepcopy(plan)
    cue = camera_only["cues"][0]
    for layer in cue["layers"]:
        if layer["role"] != "world":
            layer["action"] = "camera_pan"
    camera_only["summary"]["camera_only_cue_count"] = 1
    camera_only = with_artifact_hash({key: value for key, value in camera_only.items() if key != "artifact_hash"})
    with pytest.raises(FinanceChannelValidationError, match="camera-only"):
        validate_artifact(camera_only)

    drifted = copy.deepcopy(plan)
    layer = drifted["cues"][0]["layers"][1]
    layer["action_word_range"] = {"start_index": 9999, "end_index": 9999}
    drifted = with_artifact_hash({key: value for key, value in drifted.items() if key != "artifact_hash"})
    with pytest.raises(FinanceChannelValidationError, match="action word range escapes"):
        validate_artifact(drifted)


def _generic_editorial_plan() -> dict:
    hash_value = "a" * 64
    activation = {
        "start_s": 0.0, "end_s": 2.0, "action_start_s": 0.5, "action_end_s": 1.0,
        "start_word_index": 0, "end_word_index": 1,
        "action_start_word_index": 1, "action_end_word_index": 1,
    }
    core = {
        "schema_version": "editorial_motion_plan.v1",
        "source_storyboard_hash": hash_value,
        "source_beat_plan_hash": hash_value,
        "scene_bundle_hashes": [hash_value],
        "scene_flow_graph_hash": hash_value,
        "asset_map_hash": hash_value,
        "audio_manifest_hash": hash_value,
        "pacing_recipe_hash": hash_value,
        "duration_s": 2.0,
        "shots": [{
            "shot_id": "layered-fixture", "parent_beat_ids": ["beat-one"],
            "parent_scene_bundle_id": "scene-one", "start_s": 0.0, "duration_s": 2.0,
            "word_range": {"start_index": 0, "end_index": 1}, "narration_excerpt": "Money moves.",
            "purpose": "explain", "shot_scale": "medium", "focal_point": {"x": 0.5, "y": 0.5},
            "layers": [
                {"asset_id": "world", "role": "world", "action": "locked"},
                {"asset_id": "subject", "role": "subject", "action": "subject_moves", "activation": activation},
                {"asset_id": "mechanism", "role": "mechanism", "action": "mechanism_routes", "activation": activation},
                {"asset_id": "evidence", "role": "evidence", "action": "evidence_reveal", "activation": activation},
                {"asset_id": "transition", "role": "transition", "action": "hard_cut", "activation": activation},
            ],
            "subject_action": "subject_moves", "ambient_actions": [], "information_reveal": "evidence_reveal",
            "camera": {"kind": "locked", "amount": 0.0, "easing": "linear", "hold_in_s": 2.0, "move_s": 0.0, "hold_out_s": 0.0},
            "transition_in": {"kind": "hard_cut", "reason": "start"},
            "transition_out": {"kind": "hard_cut", "reason": "end"},
            "audio_bridge": "continuous_narration", "provider_motion": {"requirement": "none", "fallback": "local_layer_motion"},
            "overlay_ids": [], "uniqueness_signature": "layered-finance-fixture",
        }],
        "provider_calls": 0, "revision_only": True,
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def test_editorial_motion_accepts_new_roles_and_rejects_invalid_activation() -> None:
    plan = _generic_editorial_plan()
    known = {"world", "subject", "mechanism", "evidence", "transition"}
    assert validate_editorial_motion_plan(plan, known_asset_ids=known)["shots"][0]["layers"][1]["role"] == "subject"
    invalid = copy.deepcopy(plan)
    invalid["shots"][0]["layers"][1]["activation"]["action_end_s"] = 3.0
    invalid["artifact_hash"] = canonical_sha256({key: value for key, value in invalid.items() if key != "artifact_hash"})
    with pytest.raises(EditorialMotionError, match="action window escapes"):
        validate_editorial_motion_plan(invalid, known_asset_ids=known)
