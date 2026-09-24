"""Opt-in impulse/recoil/retraction proof for the pinned source exchange."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile

import pytest

from content.video_engine.scripts.model_foot_contact_probe import _blender_environment, pinned_blender
from content.video_engine.src.modeling.blender import contact_transfer, fight_motion
from content.video_engine.src.modeling.blender.contact import ROOT as CODE_ROOT, SOURCE_SHA256, sha256_file


SOURCE_ROOT = Path(os.environ.get("CONTACT_TRANSFER_SOURCE_ROOT", str(CODE_ROOT))).resolve()
FIXTURE = SOURCE_ROOT / fight_motion.FIXTURE_RELATIVE
WORKER = CODE_ROOT / "content/video_engine/tests/fixtures/modeling/blender/characters/source-exchange/run_contact_transfer.py"
REVIEW_ROOT = CODE_ROOT / fight_motion.REVIEW_RELATIVE
REVIEW_TEST_PREFIX = ".test-contact-transfer-"


def _run_blender(tmp_path: Path, *args: str, marker: str) -> dict:
    command = [str(pinned_blender()), "--background", "--factory-startup", "--disable-autoexec",
               "--python", str(WORKER), "--", *args]
    run = subprocess.run(command, cwd=CODE_ROOT, env=_blender_environment(tmp_path),
                         capture_output=True, text=True, timeout=180, check=False)
    output = run.stdout + run.stderr
    assert run.returncode == 0 and "Traceback" not in output, output
    values = [line.removeprefix(marker) for line in run.stdout.splitlines()
              if line.startswith(marker)]
    assert len(values) == 1, output
    return json.loads(values[0])


def _owned_review_child():
    review_root = REVIEW_ROOT.resolve(strict=True)
    child = Path(tempfile.mkdtemp(prefix=REVIEW_TEST_PREFIX, dir=review_root))
    assert child.parent.resolve() == review_root
    assert child.is_dir() and not child.is_symlink() and not any(child.iterdir())
    return child


def test_contact_gate_rejects_deep_follow_through_and_accepts_impulse_then_retraction() -> None:
    legacy = contact_transfer._contact_pair_checks(
        palm_plane_min_gap=-0.11696,
        palm_plane_end_gap=-0.01,
        follow_palm_plane_gap=-0.11696,
        contact_hand_proximity=0.0468,
        follow_hand_proximity=0.0468,
        root_dx=0.0,
        head_dx=0.0112,
        torso_dx=0.0,
        guard_contact=0.40,
        guard_follow=0.40,
        guard_recovery=0.40,
    )
    assert not legacy["palm_plane_penetration_capped"]
    assert not legacy["palm_plane_does_not_deepen"]
    assert not legacy["hand_finger_proximity_increases_after_contact"]
    assert not legacy["receiver_root_recoil"]
    assert not legacy["receiver_head_recoil"]
    assert not legacy["strike_hand_retracts"]
    assert not legacy["strike_hand_returns_to_guard"]

    corrected = contact_transfer._contact_pair_checks(
        palm_plane_min_gap=0.001,
        palm_plane_end_gap=0.003,
        follow_palm_plane_gap=0.04,
        contact_hand_proximity=0.019,
        follow_hand_proximity=0.04,
        root_dx=0.03,
        head_dx=0.05,
        torso_dx=0.025,
        guard_contact=0.40,
        guard_follow=0.25,
        guard_recovery=0.02,
    )
    assert all(corrected.values()), corrected


def test_render_manifest_verifier_rejects_tampered_frame_digest(tmp_path: Path) -> None:
    renders = {}
    for frame in contact_transfer.RENDER_FRAMES:
        name = f"frame-{frame:02d}.png"
        payload = b"render-manifest-test" + str(frame).encode("ascii")
        path = tmp_path / name
        path.write_bytes(payload)
        renders[str(frame)] = {
            "path": name,
            "sha256": sha256_file(path),
            "bytes": len(payload),
        }

    receipt = {"renders": renders}
    assert contact_transfer._verify_renders(receipt, tmp_path / "receipt.json") == "verified"
    renders["10"]["sha256"] = "0" * 64
    with pytest.raises(fight_motion.FightMotionError, match="render missing or changed"):
        contact_transfer._verify_renders(receipt, tmp_path / "receipt.json")


def test_saved_contact_transfer_reopens_with_contact_recoil_and_return(tmp_path: Path) -> None:
    source = SOURCE_ROOT / "content/video_engine/assets/modeling/native/fighter-family-v1.1.blend"
    before = sha256_file(source)
    child = _owned_review_child()
    try:
        built = _run_blender(tmp_path, "build", str(SOURCE_ROOT), str(child), "render",
                             marker="CONTACT_TRANSFER_JSON=")
        assert built["status"] == "review_only_diagnostic"
        receipt_path = child / "receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert receipt["schema"] == "model_fight_motion_contact_transfer.v1"
        assert receipt["mode"] == "contact_transfer_opt_in"
        assert receipt["fps"] == 30 and receipt["frame_range"] == [0, 35]
        assert receipt["source_blend_sha256_after"] == before == SOURCE_SHA256
        assert receipt["fixture_sha256"] == fight_motion.FIXTURE_SHA256
        assert receipt["implementation_sha256"] == sha256_file(Path(contact_transfer.__file__))
        assert receipt["fight_motion_sha256"] == sha256_file(Path(fight_motion.__file__))
        assert receipt["provenance_roots"]["implementation_checkout"] == str(CODE_ROOT)
        assert receipt["provenance_roots"]["source_input_checkout"] == str(SOURCE_ROOT)
        assert receipt["provenance_roots"]["review_output"] == str(child.resolve())
        assert receipt["camera"]["resolution_px"] == [540, 960]
        assert set(receipt["renders"]) == {str(frame) for frame in contact_transfer.RENDER_FRAMES}
        assert len(receipt["frames"]) == 36
        assert all(receipt["metrics"]["checks"].values()), receipt["metrics"]
        assert "right_follow_through" not in receipt["metrics"]["checks"]
        assert "contact_surface_gap" not in receipt["metrics"]["checks"]
        assert "right_strike_fist_flex" not in receipt["metrics"]["checks"]
        assert "left_strike_fist_flex" not in receipt["metrics"]["checks"]
        style = receipt["metrics"]["contact_transfer"]["style_comparison"]
        transfer = receipt["metrics"]["contact_transfer"]
        assert transfer["contact_geometry_status"] == "palm_plane_alignment_and_nearest_sample_proximity_only"
        assert transfer["contact_surface_acceptance"] == "not_established"
        assert transfer["wrist_alignment_status"] == "unverified_MM-HAND-01"
        assert transfer["digit_shape_status"] == "unverified_MM-HAND-01"
        assert "knuckle-contact test" in transfer["hand_finger_sample_note"]
        assert style["interpretation"] == "measured_scripted_response_not_visual_or_physics_approval"
        assert style["lead_hook_hip_pivot_abs_rad"] > style["jab_hip_pivot_abs_rad"]
        assert style["lead_hook_head_recoil_advantage_m"] >= 0.01
        for strike in ("right_jab", "left_hook"):
            beat = receipt["metrics"]["contact_transfer"][strike]
            assert all(beat["checks"].values()), beat
            assert beat["wrist_alignment_status"] == "unverified_MM-HAND-01"
            assert "hand_ik_target_rotation_change_deg_across_contact_frames" in beat
            assert "digit_control_euler_activity_abs_sum_rad_at_contact" in beat
            assert "attacker_finger_curl_abs_rad_at_contact" not in beat
            assert "contact_surface_distance" not in beat["checks"]
            assert beat["post_contact_palm_plane_separation_m"] >= 0.015
            assert beat["hand_finger_nearest_sample_proximity_growth_m"] >= 0.01
            assert beat["guard_distance_m"]["follow"] < beat["guard_distance_m"]["contact"]
            assert beat["guard_distance_m"]["recovery"] <= 0.06
        jab_contact_proximity = transfer["right_jab"]["hand_finger_nearest_sample_distance_m"]["contact_frames"][-1]
        assert jab_contact_proximity > 0.0  # recorded proximity only; not a knuckle-contact threshold
        reopened = _run_blender(tmp_path, "reopen", str(SOURCE_ROOT), str(child / "contact-transfer.blend"),
                                str(receipt_path), marker="CONTACT_TRANSFER_REOPEN_JSON=")
        assert reopened["status"] == "reopened_and_measured"
        assert reopened["summary_verified"] is True
        assert reopened["checked_frames"] == list(range(36))
        assert reopened["render_verification"] == "verified"
        original_receipt = dict(receipt)
        for field in ("implementation_sha256", "fight_motion_sha256",
                      "source_blend_sha256_after", "fixture_sha256", "render_digest"):
            tampered = json.loads(json.dumps(original_receipt))
            if field == "render_digest":
                tampered["renders"]["10"]["sha256"] = "0" * 64
            else:
                tampered[field] = "0" * 64
            receipt_path.write_text(json.dumps(tampered), encoding="utf-8")
            rejected = _run_blender(
                tmp_path, "reopen", str(SOURCE_ROOT), str(child / "contact-transfer.blend"),
                str(receipt_path), marker="CONTACT_TRANSFER_REOPEN_REJECTED_JSON=",
            )
            if field == "render_digest":
                assert "render missing or changed" in rejected["error"], rejected
            else:
                assert "hashes differ" in rejected["error"], rejected
        assert sha256_file(source) == before
    finally:
        import shutil

        assert child.parent.resolve() == REVIEW_ROOT.resolve(strict=True)
        assert child.name.startswith(REVIEW_TEST_PREFIX) and not child.is_symlink()
        shutil.rmtree(child)
