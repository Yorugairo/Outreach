"""Pin the negative hand/contact baseline before building its successor."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / (
    "content/video_engine/tests/fixtures/modeling/blender/characters/"
    "source-exchange/hand-foundation-baseline.v1.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_hand_foundation_baseline_pins_inputs_and_not_a_contact_approval():
    baseline = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert baseline["status"] == "review_only_negative_baseline"
    for key in ("source_clock", "source_character_blend", "source_exchange_fixture"):
        entry = baseline[key]
        path = ROOT / entry["path"]
        assert path.is_file(), path
        assert digest(path) == entry["sha256"], path
    video = baseline["source_video"]
    video_path = ROOT / video["path"]
    if video_path.is_file():
        assert digest(video_path) == video["sha256"]
    for name, expected in baseline["implementation_sha256"].items():
        if name == "inspect_hand_wrist.py":
            path = FIXTURE.parent / name
        else:
            path = ROOT / "content/video_engine/src/modeling/blender" / name
        assert digest(path) == expected, path
    assert "proximity_only" in baseline["saved_contact_transfer_review"]["contact_claim"]
    assert "fail" in baseline["visual_baseline_verdict"]


def test_hand_foundation_budgets_are_stricter_than_observed_failed_pose():
    baseline = json.loads(FIXTURE.read_text(encoding="utf-8"))
    observed = baseline["skeletal_centerline_baseline_deg"]
    budgets = baseline["predeclared_engineering_budgets"]
    assert observed["guard_f0_both"] > budgets["max_guard_and_recovery_centerline_angle_deg"]
    assert observed["right_jab_f10"] > budgets["max_strike_contact_centerline_angle_deg"]
    assert observed["left_hook_f24"] > budgets["max_strike_contact_centerline_angle_deg"]
    assert baseline["separate_prior_negative_glove_evidence"]["right_f10_unsigned_pad_head_gap_m"] > budgets[
        "signed_knuckle_to_target_gap_at_contact_m"
    ][1]
    assert baseline["observed_source_events"]["left_head_response_frame"] > baseline[
        "observed_source_events"
    ]["left_hook_contact_frame"]
    assert sum(baseline["topology_requirement"]["reference_landmarks"].values()) == 27
