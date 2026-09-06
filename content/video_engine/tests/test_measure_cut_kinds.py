"""The transition classifier (E38/TR-1) has to be checkable without the reference video, so
`classify()` is a pure function of the three series (L, D, S) plus one SSIM number. These tests
drive it with SYNTHETIC series - one per rule, shaped like the thing the rule is named after -
so a threshold change shows up here before it shows up in a 99-boundary run.

fps is 30 throughout, the window is [-0.6 s, +0.8 s] = 42 frames, boundary at index 18.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import measure_cut_kinds as MK  # noqa: E402

VIDEO_FPS = 30.0
N = 42
B = 18          # int(round(0.6 * 30))
CHANGED = 0.20  # SSIM well under SIM_SAME_WORLD
SAME = 0.95


def flat(value: float) -> np.ndarray:
    return np.full(N, float(value))


def base_series() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A steady scene: L 120, a little residual motion, sharp."""
    rng = np.random.default_rng(7)
    L = flat(120.0) + rng.normal(0, 0.05, N)
    D = flat(0.30) + rng.normal(0, 0.01, N)
    S = flat(900.0) + rng.normal(0, 2.0, N)
    D[0] = 0.0
    return L, D, S


def test_step_is_a_hard_cut():
    L, D, S = base_series()
    L[B:] += 40.0            # a new plate, brighter
    D[B] = 38.0              # one frame carries the whole change
    S[B:] += 60.0
    m = MK.classify(L, D, S, CHANGED, VIDEO_FPS)
    assert m.kind == "hard-cut", m.reason
    assert m.peak_index == B
    assert m.duration_frames == 1
    assert m.D_peak == pytest.approx(38.0, abs=0.1)
    assert m.first_motion_frames == 0     # the new plate is still the moment it arrives
    assert m.motion_after_0_5s < 1.5      # nothing moves after it - as a number


def test_six_frame_ramp_is_a_dissolve():
    L, D, S = base_series()
    ramp = slice(B - 2, B + 4)            # 6 frames of cross-fade
    L[ramp] = np.linspace(120.0, 160.0, 6)
    L[B + 4:] = 160.0
    D[ramp] = 7.0                         # elevated, flat - no dominant peak
    m = MK.classify(L, D, S, CHANGED, VIDEO_FPS)
    assert m.kind == "dissolve", m.reason
    assert m.duration_frames >= MK.DISSOLVE_MIN_FRAMES
    # what rules out a hard cut is the ramp, not the peak height: the neighbouring frames
    # each carry more than TRANSITION_FRAC of the peak, so the span is 6 frames, not 1
    assert D[B - 1] > MK.TRANSITION_FRAC * m.D_peak
    assert D[B + 1] > MK.TRANSITION_FRAC * m.D_peak


def test_luminance_dip_is_a_dip():
    L, D, S = base_series()
    dip = slice(B - 2, B + 3)             # 5 frames through near-black
    L[dip] = [70.0, 30.0, 8.0, 30.0, 70.0]
    L[B + 3:] = 120.0
    D[dip] = 9.0
    m = MK.classify(L, D, S, CHANGED, VIDEO_FPS)
    assert m.kind == "dip", m.reason
    assert m.L_min < MK.DIP_DARK_FRAC * min(m.L_before, m.L_after)


def test_a_dip_still_reads_as_a_dip_when_the_two_plates_look_alike():
    """Boundary 98 of the reference: a fade to black between two near-identical cream plates,
    SSIM 0.62. The caller already asserts a shot ended here, so "the world changed" must not
    be a condition of the dip - it was a false negative, and only ever that."""
    L, D, S = base_series()
    dip = slice(B - 3, B + 4)
    L[dip] = [80.0, 40.0, 12.0, 0.0, 12.0, 40.0, 80.0]
    D[dip] = 11.0
    m = MK.classify(L, D, S, SAME, VIDEO_FPS)
    assert m.kind == "dip", m.reason
    assert m.sim >= MK.SIM_SAME_WORLD


def test_a_blur_zoom_still_reads_as_one_when_the_two_plates_look_alike():
    """Boundary 26 of the reference: a zoom-through between two similar cream plates, SSIM 0.61.
    Same false negative as the dip - SSIM decides world-persists only."""
    L, D, S = base_series()
    S[B - 5: B + 5] = [1700.0, 1100.0, 690.0, 380.0, 330.0, 310.0, 330.0, 400.0, 690.0, 1680.0]
    D[B] = 26.0
    m = MK.classify(L, D, S, SAME, VIDEO_FPS)
    assert m.kind == "blur-zoom", m.reason
    assert m.sim >= MK.SIM_SAME_WORLD
    assert m.duration_frames >= MK.BLUR_MIN_FRAMES


def test_sharpness_valley_is_a_blur_zoom():
    L, D, S = base_series()
    S[B - 1: B + 3] = [300.0, 120.0, 140.0, 380.0]   # blur through, then recovers
    D[B - 1: B + 3] = [12.0, 26.0, 14.0, 6.0]
    m = MK.classify(L, D, S, CHANGED, VIDEO_FPS)
    assert m.kind == "blur-zoom", m.reason
    assert m.S_min < MK.BLUR_VALLEY_FRAC * m.S_before


def test_flat_d_with_a_persisting_world():
    L, D, S = base_series()
    D[B] = 0.45                            # an element entered; the background never moved
    m = MK.classify(L, D, S, SAME, VIDEO_FPS)
    assert m.kind == "world-persists", m.reason
    assert m.D_peak < MK.WORLD_PEAK_RATIO * max(m.D_median, MK.D_FLOOR)


def test_a_hard_cut_still_reads_as_one_inside_an_animating_scene():
    """Boundary 1 of the reference: both scenes are animating at D ~ 3, and one frame carries
    D 40. The span is still 1 frame, so it is a cut - the ambient motion must not hide it."""
    L, D, S = base_series()
    D[B - 6: B] = 3.0
    D[B] = 40.0
    D[B + 1: B + 8] = 3.0
    m = MK.classify(L, D, S, CHANGED, VIDEO_FPS)
    assert m.kind == "hard-cut", m.reason
    assert m.duration_frames == 1
    assert m.first_motion_frames == 7          # the new scene keeps moving for 7 frames
    assert m.motion_after_0_5s > 2.0


def test_unclassifiable_series_falls_through_to_other():
    """A three-frame ramp with a dominant peak: too long to be a cut, too short and too
    peaked to be a dissolve, no L excursion, no S valley. Nothing decides it."""
    L, D, S = base_series()
    D[B - 2: B + 3] = [5.0, 9.0, 25.0, 9.0, 5.0]
    m = MK.classify(L, D, S, CHANGED, VIDEO_FPS)
    assert m.kind == "other", m.reason
    assert m.duration_frames == 3


def test_peak_is_found_when_the_ledger_time_is_off_by_a_few_frames():
    L, D, S = base_series()
    L[B + 4:] += 40.0
    D[B + 4] = 38.0
    m = MK.classify(L, D, S, CHANGED, VIDEO_FPS)
    assert m.kind == "hard-cut", m.reason
    assert m.peak_index == B + 4


def test_measures_are_reported_even_for_other():
    L, D, S = base_series()
    D[B - 2: B + 3] = [5.0, 9.0, 25.0, 9.0, 5.0]
    m = MK.classify(L, D, S, CHANGED, VIDEO_FPS)
    assert m.D_median > 0 and m.S_before > 0 and m.D_peak == 25.0
    assert m.duration_frames == 3 and m.L_before > 0 and m.S_min > 0
    # and the "does anything move after it" number is still reported: here, nothing does
    assert m.motion_after_0_5s < 1.0


def test_ssim_is_one_for_identical_frames_and_low_for_different_ones():
    rng = np.random.default_rng(3)
    a = rng.integers(0, 255, (60, 100)).astype(np.float32)
    b = rng.integers(0, 255, (60, 100)).astype(np.float32)
    assert MK.ssim(a, a) == pytest.approx(1.0, abs=1e-6)
    assert MK.ssim(a, b) < MK.SIM_SAME_WORLD


def test_csv_writer_round_trips(tmp_path: Path):
    rows = [
        {"boundary": 2, "t_s": 26.2, "kind": "blur-zoom", "duration_frames": 5,
         "first_motion_frames": 3, "motion_after_0_5s": 2.41, "D_peak": 26.0, "D_median": 0.3,
         "L_before": 120.0, "L_min": 118.0, "L_after": 131.0, "S_before": 900.0, "S_min": 120.0,
         "at_gap": "yes", "gap_s": "0.34", "reason": "dropped by the writer"},
        {"boundary": 3, "t_s": 32.2, "kind": "hard-cut", "duration_frames": 1,
         "first_motion_frames": 1, "motion_after_0_5s": 1.1, "D_peak": 38.0, "D_median": 0.3,
         "L_before": 120.0, "L_min": 120.0, "L_after": 160.0, "S_before": 900.0, "S_min": 890.0,
         "at_gap": "yes", "gap_s": "0.58"},
    ]
    out = MK.write_csv(rows, tmp_path / "sub" / "measured.csv")
    with out.open(encoding="utf-8", newline="") as fh:
        back = list(csv.DictReader(fh))
    assert list(back[0]) == MK.CSV_FIELDS          # no stray columns, no missing ones
    assert back[0]["kind"] == "blur-zoom" and back[1]["kind"] == "hard-cut"
    assert float(back[0]["motion_after_0_5s"]) == pytest.approx(2.41)
    assert back[0]["gap_s"] == "0.34"              # the credible gap columns survive


def test_summary_shares_and_median_shot_length():
    rows = [
        {"boundary": 1, "t_s": 10.0, "kind": "hard-cut", "first_motion_frames": 1, "motion_after_0_5s": 1.0},
        {"boundary": 2, "t_s": 26.0, "kind": "hard-cut", "first_motion_frames": 1, "motion_after_0_5s": 1.0},
        {"boundary": 3, "t_s": 30.0, "kind": "dip", "first_motion_frames": 6, "motion_after_0_5s": 3.0},
        {"boundary": 4, "t_s": 40.0, "kind": "dip", "first_motion_frames": 8, "motion_after_0_5s": 4.0},
    ]
    s = MK.summarise(rows)
    assert s["n"] == 4
    assert s["kinds"]["hard-cut"]["share"] == 0.5
    assert s["kinds"]["hard-cut"]["median_shot_s"] == 13.0     # shots of 10.0 and 16.0
    assert s["kinds"]["dip"]["median_shot_s"] == 7.0           # shots of 4.0 and 10.0
    assert s["kinds"]["dissolve"]["n"] == 0
    assert s["thresholds"]["HARD_PEAK_RATIO"] == MK.HARD_PEAK_RATIO


def test_thresholds_are_all_reported_for_the_header():
    t = MK.thresholds()
    for name in ("HARD_PEAK_RATIO", "DISSOLVE_MIN_FRAMES", "DIP_DARK_FRAC",
                 "BLUR_VALLEY_FRAC", "SIM_SAME_WORLD", "SETTLE_RATIO"):
        assert name in t
