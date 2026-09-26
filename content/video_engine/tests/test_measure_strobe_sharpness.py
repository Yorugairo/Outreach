"""P72 T32 (R26-85): the strobe's two terms - speed and edge sharpness - read off the pixels, the same code for the
reference's frames and ours (E38). Known answers only: synthetic bars whose speed, cadence and shutter are set."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import measure_strobe_sharpness as MS  # noqa: E402


def _profile(sigma: float, x0: float = 0.3) -> np.ndarray:
    i = np.arange(13, dtype=np.float64) - 6
    return MS._area_step(i, 30.0, 230.0, x0, sigma)


def test_a_sharp_edge_fits_no_softness_wherever_it_falls_in_the_pixel():
    # below ~0.2 px a pixel-sampled step cannot tell one sigma from another: the fit's resolution floor
    for x0 in (-0.45, -0.2, 0.0, 0.25, 0.49):
        assert MS.edge_sigma(_profile(0.0, x0)) == pytest.approx(0.0, abs=0.2)


def test_a_soft_edge_fits_its_own_sigma():
    for sigma in (0.6, 1.2, 2.4):
        assert MS.edge_sigma(_profile(sigma)) == pytest.approx(sigma, abs=0.05)


def test_a_flat_or_double_edge_profile_is_no_read():
    assert MS.edge_sigma(np.full(13, 80.0)) is None
    two = np.array([30, 30, 30, 230, 230, 30, 30, 30, 230, 230, 230, 230, 230], dtype=np.float64)
    assert MS.edge_sigma(two) is None


def test_the_phase_shift_reads_a_moving_bar_over_a_static_ground():
    a, b = MS._bar_frames(240.0, 24.0, 2)
    dx, dy, peak = MS.phase_shift(a, b)
    assert dx == pytest.approx(10.0, abs=0.3) and abs(dy) < 0.3 and peak >= MS.PEAK_MIN


def test_on_ones_and_on_twos_share_the_speed_and_halve_the_step_rate():
    one = MS.mark_read(MS._bar_frames(200.0, 24.0, 25, on=1), 24.0, 1920)
    two = MS.mark_read(MS._bar_frames(200.0, 24.0, 25, on=2), 24.0, 1920)
    assert one["v"] == pytest.approx(200.0, rel=0.03) and two["v"] == pytest.approx(200.0, rel=0.03)
    assert one["w_s"] == pytest.approx(24.0) and two["w_s"] == pytest.approx(12.0)
    assert two["d"] == pytest.approx(2 * one["d"], rel=0.03)
    assert two["S"] == pytest.approx(2 * one["S"], rel=0.05)


def test_a_sharp_edge_reads_at_the_pixel_nyquist_so_T_is_half_the_speed():
    r = MS.mark_read(MS._bar_frames(200.0, 24.0, 25), 24.0, 1920)
    assert r["u0"] == pytest.approx(MS.NYQUIST) and r["T"] == pytest.approx(100.0, rel=0.03)


def test_the_red_parity_bar_carries_its_shutter_blur_along_the_motion_only():
    r = MS.mark_read(MS._bar_frames(154.0, 24.0, 25, shutter=0.5), 24.0, 1080)
    assert r["w_along"] == pytest.approx(0.8 * 154.0 * 0.5 / 24.0, rel=0.08)
    assert r["w_across"] == pytest.approx(0.0, abs=0.1)
    assert 45.0 <= r["T"] <= 58.0          # 0.8755 * 24 / (0.8 * 0.5) = 52.5 Hz at any speed under the blur


def test_speeds_are_reported_at_the_1920_stage_and_in_picture_widths():
    r = MS.mark_read(MS._bar_frames(200.0, 24.0, 13), 24.0, 1280)
    assert r["v_1920"] == pytest.approx(r["v"] * 1920 / 1280, rel=1e-3)
    assert r["pw_s"] == pytest.approx(r["v"] / 1280, abs=1e-3)


def test_a_held_region_reads_no_motion_and_no_sharpness():
    frames = MS._bar_frames(0.0, 24.0, 6)
    r = MS.mark_read(frames, 24.0, 1920)
    assert r["v"] == 0.0 and r["moved_pairs"] == 0 and r["w_along"] is None and r["T"] is None


def test_the_known_answer_fixtures_pass():
    assert MS.check_fixtures() == []


def _write_index(root: Path, mode: str, frames: list[np.ndarray], fps: float = 24.0) -> Path:
    from PIL import Image
    items = []
    if mode == "pairs":
        for k in range(0, len(frames) - 1, 2):
            names = [f"p{k}a.png", f"p{k}b.png"]
            for name, f in zip(names, frames[k:k + 2]):
                Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).save(root / name)
            items.append({"t": k / fps, "frames": names})
    else:
        for k, f in enumerate(frames):
            Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).save(root / f"r{k}.png")
            items.append({"t": k / fps, "frames": [f"r{k}.png"]})
    h, w = frames[0].shape
    idx = root / "index.json"
    idx.write_text(json.dumps({"fps": fps, "width": w, "height": h, "mode": mode, "items": items}), encoding="utf-8")
    return idx


def test_a_run_index_measures_like_the_arrays(tmp_path):
    frames = MS._bar_frames(180.0, 24.0, 13, size=(128, 256))
    idx = _write_index(tmp_path, "run", frames)
    src = {"kind": "frames", **MS.load_index(idx)}
    got = MS.measure(src, 0.0, 13 / 24.0, (0, 0, 256, 128))
    want = MS.mark_read([np.round(f) for f in frames], 24.0, 256)
    assert got["v"] == pytest.approx(want["v"], abs=0.5) and got["w_s"] == want["w_s"]


def test_the_survey_finds_a_bar_in_the_band_and_not_one_outside_it(tmp_path):
    inside = MS._bar_frames(12.0 * 24 / (1920 / 256), 24.0, 2, size=(128, 256))   # 12 px/frame at the 1920 stage
    idx = _write_index(tmp_path, "pairs", inside)
    src = {"kind": "frames", **MS.load_index(idx)}
    hits = MS.survey(src, 1.0, (100.0, 300.0))
    assert hits and all(100.0 <= h["v_1920"] <= 300.0 for h in hits)
    assert MS.survey(src, 1.0, (400.0, 900.0)) == []


def test_events_chain_hits_within_the_gap():
    hits = [{"t": t, "box": [0, 0, 128, 128], "v_1920": 150.0, "peak": 0.5} for t in (1.0, 2.0, 3.0, 9.0)]
    ev = MS.events(hits)
    assert [(e["t_first"], e["t_last"], e["n_tiles"]) for e in ev] == [(1.0, 3.0, 3), (9.0, 9.0, 1)]


def test_a_malformed_index_is_refused_by_name(tmp_path):
    bad = tmp_path / "index.json"
    bad.write_text(json.dumps({"fps": 24, "width": 8, "height": 8, "items": []}), encoding="utf-8")
    with pytest.raises(SystemExit, match="'mode'"):
        MS.load_index(bad)
    bad.write_text(json.dumps({"fps": 24, "width": 8, "height": 8, "mode": "stack", "items": []}), encoding="utf-8")
    with pytest.raises(SystemExit, match="'stack'"):
        MS.load_index(bad)


def test_a_malformed_box_is_refused_by_name():
    with pytest.raises(Exception, match="--box"):
        MS._box("10,10,4,4")
    assert MS._box("10,20,64,32") == (10, 20, 64, 32)


def test_a_record_whose_source_is_missing_is_refused_by_name(tmp_path):
    rec = tmp_path / "rec.json"
    rec.write_text(json.dumps({"marks": [{"id": "gone", "source": "nowhere.mp4", "t0": 0, "t1": 1,
                                          "box": [0, 0, 32, 32], "v": 100.0}]}), encoding="utf-8")
    with pytest.raises(SystemExit, match="gone"):
        MS.check_record(rec, tmp_path)


def test_check_exits_zero_on_the_fixtures():
    assert MS.main(["--check"]) == 0


def test_the_parity_width_is_the_shutter_ramp():
    assert MS._parity_width(154.0, 24.0, 0.5) == pytest.approx(0.8 * 154.0 / 48.0)
    assert math.isclose(MS._parity_width(154.0, 24.0, 0.0), 0.0)
