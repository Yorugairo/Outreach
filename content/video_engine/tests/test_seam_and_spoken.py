"""P54 follow-up: the black frame at a seam, and narration pointing at a visual not on screen. Pure functions only -
synthetic luma series and synthetic timelines, no browser."""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
READ_ROOT_SCRIPTS = Path("C:/Users/Snipe/Downloads/Outreach Program/content/video_engine/scripts")
for p in (HERE.parent / "scripts", Path(os.environ.get("VIDEO_ENGINE_SCRIPTS") or READ_ROOT_SCRIPTS)):
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

import measure_seam_frames as S      # noqa: E402
import measure_spoken_visuals as V   # noqa: E402

FPS = 30.0
AT = 10.0


def _series(values: list[float], at: float = AT) -> tuple[list[float], list[float]]:
    """Frames centred on the boundary: the middle value sits on the boundary frame."""
    mid = len(values) // 2
    return [round(at + (i - mid) / FPS, 4) for i in range(len(values))], values


def _clean_dip() -> list[float]:
    # a 0.47 s linear dip over a cream world (luma 230): 7 frames down, the black on the boundary, 7 frames up
    ramp = [230 * (1 - k / 7) for k in range(1, 7)]
    return [230.0] * 4 + ramp + [4.0, 0.0] + ramp[::-1] + [230.0] * 4


def _faults(values, kind, dip_s=None):
    ts, lumas = _series(values)
    return [f["fault"] for f in S.seam_faults(ts, lumas, AT, kind, dip_s, FPS)]


def test_a_near_black_frame_at_a_cut_is_a_flash():
    assert _faults([200.0] * 8 + [2.0] + [200.0] * 8, "cut") == ["flash"]


def test_a_bright_cut_has_no_fault():
    assert _faults([200.0] * 8 + [120.0] * 9, "cut") == []


def test_a_clean_linear_dip_has_no_fault():
    assert _faults(_clean_dip(), "dip", 0.47) == []


def test_a_dip_cut_into_black_from_a_bright_frame_is_a_jump():
    values = [230.0] * 10 + [0.0, 0.0] + [230 * k / 7 for k in range(1, 7)] + [230.0] * 4
    assert _faults(values, "dip", 0.47) == ["jump"]


def test_a_dip_holding_black_for_four_frames_is_a_hold():
    ramp = [230 * (1 - k / 7) for k in range(1, 7)]
    values = [230.0] * 4 + ramp + [2.0, 1.0, 0.0, 1.0] + ramp[::-1] + [230.0] * 4
    faults = _faults(values, "dip", 0.47)
    assert faults == ["hold"]


def test_a_black_frame_past_the_dip_window_is_outside():
    ts, lumas = _series(_clean_dip())
    lumas = list(lumas) + [230.0] * 3 + [1.0] + [230.0] * 3          # a stray black frame ~0.4 s after the boundary
    ts = ts + [round(ts[-1] + (k + 1) / FPS, 4) for k in range(7)]
    kinds = [f["fault"] for f in S.seam_faults(ts, lumas, AT, "dip", 0.47, FPS)]
    assert "outside" in kinds and "jump" in kinds


def test_a_longer_declared_dip_allows_a_longer_core():
    ramp = [230 * (1 - k / 14) for k in range(1, 14)]      # a 0.94 s dip ramps over twice the frames
    values = [230.0] * 4 + ramp + [2.0, 1.0, 0.0, 1.0] + ramp[::-1] + [230.0] * 4
    assert _faults(values, "dip", 0.94) == []


def test_a_hold_over_a_dark_world_is_marked():
    ramp = [18 * (1 - k / 7) for k in range(1, 7)]
    ts, lumas = _series([18.0] * 4 + ramp + [1.0, 0.0] + ramp[::-1] + [18.0] * 4)
    holds = [f for f in S.seam_faults(ts, lumas, AT, "dip", 0.47, FPS) if f["fault"] == "hold"]
    assert holds and holds[0]["dark_world"] is True


def test_boundaries_take_the_exit_of_the_scene_they_open():
    tl = {"runtime_s": 20.0, "scenes": [
        {"scene_id": "s01", "span": [0, 5], "exit": "dip"},
        {"scene_id": "s02", "span": [5, 12], "exit": "cut"},
        {"scene_id": "s03", "span": [12, 20], "exit": "dip:0.8", "world": {"page": {"enter": "mount"}}}]}
    b = S.boundaries_of(tl)
    assert [(x["t"], x["kind"], x["dip_s"]) for x in b] == [(5.0, "cut", None), (12.0, "dip", 0.8)]
    assert b[1]["next_enter"] == "mount"


def test_frame_times_sit_on_the_render_grid():
    ts = S.frame_times(8.32, 0.1, FPS)
    assert ts == [round(k / FPS, 4) for k in range(247, 253)]


# ---- gate B: spoken visuals -------------------------------------------------------------------------------

def _timeline(words: list[tuple[str, float]], scenes: list[dict]) -> dict:
    return {"caption_pages": [{"t": [{"w": w, "s": s} for w, s in words]}], "scenes": scenes}


def test_a_pointing_phrase_over_a_plate_alone_is_uncovered():
    tl = _timeline([("Now", 1.0), ("look", 1.2), ("at", 1.4), ("this", 1.5), ("chart.", 1.7)],
                   [{"scene_id": "s01", "span": [0, 5], "world": {"asset_id": "plate-a"}}])
    doc = V.analyse(tl)
    assert [(p["phrase"], p["t"]) for p in doc["pointers"]] == [("look at", 1.2), ("this chart", 1.5)]
    assert doc["n_uncovered"] == 2 and doc["pointers"][0]["on_stage"]["world"] == "plate"


def test_a_pointing_phrase_over_a_ledger_page_is_covered():
    tl = _timeline([("Watch", 3.0), ("the", 3.2), ("line.", 3.4)],
                   [{"scene_id": "s01", "span": [0, 5], "world": {"kind": "ledger", "page": {}}}])
    doc = V.analyse(tl)
    assert doc["n_pointers"] == 2 and doc["n_uncovered"] == 0      # "watch the" and "the line"


def test_a_dock_on_stage_covers_a_pointing_phrase_only_inside_its_window():
    scenes = [{"scene_id": "s01", "span": [0, 10], "world": {"asset_id": "plate-a"},
               "docks": [{"slide": "dock-a", "enter": 2.0, "exit": 4.0}]}]
    covered = V.analyse(_timeline([("See", 3.0), ("the", 3.1), ("gap", 3.2)], scenes))
    uncovered = V.analyse(_timeline([("See", 6.0), ("the", 6.1), ("gap", 6.2)], scenes))
    assert covered["n_uncovered"] == 0 and covered["pointers"][0]["on_stage"]["docks"] == ["dock-a"]
    assert uncovered["n_uncovered"] == 1


def test_a_card_species_covers_but_a_mark_on_a_plate_does_not():
    scenes = [{"scene_id": "s01", "span": [0, 10], "world": {"asset_id": "plate-a"},
               "species": [{"kind": "flow", "at": 1.0, "dur": 3.0}, {"kind": "callout", "at": 5.0, "dur": 3.0}]}]
    assert V.analyse(_timeline([("On", 2.0), ("screen", 2.1)], scenes))["n_uncovered"] == 0
    assert V.analyse(_timeline([("On", 6.0), ("screen", 6.1)], scenes))["n_uncovered"] == 1


def test_ordinary_speech_is_not_a_pointer_and_curly_apostrophes_match():
    tl = _timeline([("Here\u2019s", 1.0), ("the", 1.1), ("catch,", 1.2), ("the", 2.0), ("rate", 2.1), ("fell", 2.2)],
                   [{"scene_id": "s01", "span": [0, 5], "world": {"asset_id": "plate-a"}}])
    assert [p["phrase"] for p in V.analyse(tl)["pointers"]] == ["here's the"]
