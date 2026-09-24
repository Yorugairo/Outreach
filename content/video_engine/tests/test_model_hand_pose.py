"""Focused checks for opt-in, ungloved Rigify finger flexion only."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

import pytest

from content.video_engine.scripts.model_foot_contact_probe import _blender_environment, pinned_blender


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "content/video_engine/src/modeling/blender/hand_pose.py"
SPEC = importlib.util.spec_from_file_location("mm_hand_pose_tested", MODULE_PATH)
assert SPEC and SPEC.loader
hand_pose = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = hand_pose
SPEC.loader.exec_module(hand_pose)


class _FakeBone:
    def __init__(self):
        self.rotation_mode = "XYZ"
        self.rotation_euler = (0.0, 0.0, 0.0)
        self.keys = []

    def keyframe_insert(self, **kwargs):
        self.keys.append(kwargs)


class _FakeViewLayer:
    def update(self):
        pass


class _FakeBpy:
    context = type("Context", (), {"view_layer": _FakeViewLayer()})()


def test_opt_in_rekeys_only_four_finger_chains_on_local_x():
    bones = {f"{finger}.{segment}.R": _FakeBone()
             for finger in hand_pose.FINGERS for segment in hand_pose.SEGMENTS}
    bones["thumb.02.R"] = _FakeBone()
    bones["hand_ik.R"] = _FakeBone()
    rig = type("Rig", (), {"pose": type("Pose", (), {"bones": bones})()})()
    hand_pose.key_palmward_finger_flexion(_FakeBpy(), rig, "R", frame=7)
    for finger in hand_pose.FINGERS:
        for segment, expected in zip(hand_pose.SEGMENTS, hand_pose.FLEXION_RAD):
            bone = bones[f"{finger}.{segment}.R"]
            assert bone.rotation_euler == (expected, 0.0, 0.0)
            assert bone.keys == [{"data_path": "rotation_euler", "frame": 7,
                                  "group": "mm_finger_flexion"}]
    assert not bones["thumb.02.R"].keys
    assert not bones["hand_ik.R"].keys
    with pytest.raises(ValueError, match="side must be"):
        hand_pose.key_palmward_finger_flexion(_FakeBpy(), rig, "X")


def test_pose_gate_rejects_lateral_splay_even_with_one_folded_finger():
    corrected = {"fingers": {name: {"palmward_m": 0.035,
                                    "retraction_m": 0.025,
                                    "lateral_sweep_m": 0.010}
                             for name in hand_pose.FINGERS},
                 "thumb_tip_to_distal_finger_bones_min_m": 0.0099}
    assert all(hand_pose.pose_checks(corrected).values())
    legacy = json.loads(json.dumps(corrected))
    for name in ("f_index", "f_ring", "f_pinky"):
        legacy["fingers"][name]["palmward_m"] = 0.005
        legacy["fingers"][name]["lateral_sweep_m"] = 0.060
    checks = hand_pose.pose_checks(legacy)
    assert not checks["four_finger_tips_palmward"]
    assert not checks["lateral_sweep_bounded"]
    compressed_thumb = json.loads(json.dumps(corrected))
    compressed_thumb["thumb_tip_to_distal_finger_bones_min_m"] = 0.002
    assert not hand_pose.pose_checks(compressed_thumb)["thumb_bone_clearance_proxy"]


def _blender(tmp_path: Path, *args: str, marker: str):
    run = subprocess.run(
        [str(pinned_blender()), "--background", "--factory-startup", "--disable-autoexec",
         "--python", str(MODULE_PATH), "--", *args],
        cwd=ROOT, env=_blender_environment(tmp_path), capture_output=True,
        text=True, timeout=120, check=False,
    )
    output = run.stdout + run.stderr
    assert run.returncode == 0 and "Traceback" not in output, output
    records = [json.loads(line.removeprefix(marker)) for line in run.stdout.splitlines()
               if line.startswith(marker)]
    assert len(records) == 1, output
    return records[0]


def test_script_disabled_saved_pose_reopens_with_legacy_contrast_and_phone_frames(tmp_path):
    source_text = os.environ.get("MM_HAND_POSE_SOURCE_SCENE")
    if not source_text:
        pytest.skip("set MM_HAND_POSE_SOURCE_SCENE to a hash-pinned saved exchange scene")
    source = Path(source_text).resolve(strict=True)
    source_before = hand_pose.sha256(source)
    output = tmp_path / "pose-review"
    built = _blender(tmp_path, "build", str(source), str(output), marker="HAND_POSE_BUILD=")
    assert built["status"] == "review_only_finger_flexion"
    receipt = json.loads((output / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["source_scene"]["sha256"] == source_before
    assert receipt["source_scene_sha256_after"] == source_before
    assert receipt["implementation_sha256"] == hand_pose.sha256(MODULE_PATH)
    assert receipt["claim_limits"] == [
        "palmward_finger_flexion_only", "no_closed_fist_silhouette",
        "no_wrist_alignment", "no_contact_gate", "no_glove_art", "no_fight_physics"]
    for frame, side in hand_pose.REVIEW_FRAMES:
        key = f"{frame}_{side}"
        before = receipt["before"][key]
        after = receipt["after"][key]
        assert all(receipt["checks"][key].values())
        for finger in ("f_index", "f_ring", "f_pinky"):
            assert before["fingers"][finger]["lateral_sweep_m"] >= 0.040
            assert after["fingers"][finger]["lateral_sweep_m"] <= 0.025
        assert after["thumb_tip_hand_local_m"] == before["thumb_tip_hand_local_m"]
        assert after["thumb_tip_to_distal_finger_bones_min_m"] >= 0.006
        for view in ("phone", "close"):
            entry = receipt["renders"][str(frame)][view]
            image = output / entry["path"]
            assert image.stat().st_size == entry["bytes"]
            assert hand_pose.sha256(image) == entry["sha256"]
            assert struct.unpack(">II", image.read_bytes()[16:24]) == (540, 960)
    reopened = _blender(
        tmp_path, "reopen", str(source), str(output / "finger-flexion-pose.blend"),
        str(output / "receipt.json"), marker="HAND_POSE_REOPEN=",
    )
    assert reopened == {"status": "reopened_and_measured",
                        "checked_frames": [10, 24],
                        "scene_and_renders_verified": True,
                        "source_unchanged": True}
    assert hand_pose.sha256(source) == source_before
