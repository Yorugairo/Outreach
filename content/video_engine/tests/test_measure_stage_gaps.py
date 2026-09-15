"""P58: the empty stage, measured right - a picture plate is a world on stage. Pure: a synthetic timeline and a
stubbed probe record (no browser)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
READ_ROOT_SCRIPTS = Path("C:/Users/Snipe/Downloads/Outreach Program/content/video_engine/scripts")
for p in (HERE.parent / "scripts", Path(os.environ.get("VIDEO_ENGINE_SCRIPTS") or READ_ROOT_SCRIPTS)):
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

import gate_motion_density as G      # noqa: E402
import measure_stage_gaps as M       # noqa: E402

AT = 10.0
STEP, LEAD, TAIL = 0.1, 0.6, 3.0
INK = {"page": {"title": [0, 0, 10, 10]}}


def _page(enter: str = "snap") -> dict:
    return {"kind": "ledger", "page": {"enter": enter}}


def _plate() -> dict:
    return {"asset_id": "plate-vault"}


def _timeline(world_b: dict, exit_b: str) -> dict:
    return {"runtime_s": 20.0,
            "scenes": [{"scene_id": "s01", "span": [0.0, AT], "world": _page()},
                       {"scene_id": "s02", "span": [AT, 20.0], "exit": exit_b, "world": world_b}],
            "caption_pages": [{"t": [{"w": "live", "s": AT + 0.5}, {"w": "sentence", "s": AT + 0.9}]}]}


def _ink_until_boundary(t: float, _sid: str) -> dict:
    """The outgoing page's ink is in the probe's record up to the boundary; nothing after (no page, no dock)."""
    return INK if t < AT else {}


def _row(tl: dict) -> dict:
    return M.measure_timeline(tl, _ink_until_boundary, STEP, LEAD, TAIL)["boundaries"][0]


@pytest.mark.parametrize("exit_b", ["cut", "door:right"])
def test_a_cut_or_a_door_into_a_plate_measures_no_empty_stage(exit_b):
    row = _row(_timeline(_plate(), exit_b))
    assert row["gap_s"] == 0.0 and row["spoken"] == [] and not row["licensed"]
    assert row["picture_s"] == pytest.approx(TAIL + STEP)


def test_a_clip_world_is_a_picture_too():
    assert _row(_timeline({"kind": "clip", "asset_id": "clip-a"}, "cut"))["gap_s"] == 0.0


def test_a_suck_into_a_ledger_page_with_no_ink_still_measures_empty_and_m31_fails(tmp_path):
    tl = _timeline(_page("axes"), "suck:0.5,0.52")
    doc = M.measure_timeline(tl, _ink_until_boundary, STEP, LEAD, TAIL)
    row = doc["boundaries"][0]
    assert row["gap_s"] == pytest.approx(TAIL + STEP) and row["picture_s"] == 0.0
    assert row["spoken"] == ["live", "sentence"]
    (tmp_path / "stage-gaps.json").write_text(json.dumps(doc), encoding="utf-8")
    gate = G._stage_gap_gate(tmp_path, tl["scenes"])
    assert gate.level == "FAIL" and "chart-to-chart" in gate.message


def test_a_dip_into_a_plate_reads_its_black_ramp_licensed():
    row = _row(_timeline(_plate(), "dip"))
    half = M.SF.DIP_S / 2
    # the outgoing page's ink holds up to the boundary; after it, only the grid instants inside the ramp are empty
    ramp_after = [k * STEP for k in range(int(TAIL / STEP) + 1) if k * STEP <= half + 1e-9]
    assert row["from"] == pytest.approx(AT)
    assert row["to"] == pytest.approx(AT + ramp_after[-1] + STEP)
    assert row["gap_s"] == pytest.approx(len(ramp_after) * STEP) and row["gap_s"] <= 2 * half + STEP
    assert row["licensed"] and row["picture_s"] > 0.0


def test_a_picture_inside_a_dip_ramp_is_not_on_stage():
    tl = _timeline(_plate(), "dip:0.8")
    dips = M.dip_windows(tl)
    assert dips == [pytest.approx((AT - 0.4, AT + 0.4))]
    assert not M.picture_on_stage(tl, AT + 0.3, dips)
    assert M.picture_on_stage(tl, AT + 0.5, dips)
    assert not M.picture_on_stage(tl, AT - 1.0, [])   # a ledger page is not a picture: ink decides


def test_m31_over_a_plate_gap_of_zero_reports_no_spoken_empty_run(tmp_path):
    doc = {"runtime_s": 20.0, "empty_share": 0.155, "boundaries": [
        {"at": 5.0, "scene": "s01", "exit": "dip", "gap_s": 3.1, "spoken": ["over", "the", "black"], "licensed": True},
        {"at": 10.0, "scene": "s02", "exit": "door", "gap_s": 0.0, "picture_s": 3.1, "spoken": [], "licensed": False}]}
    (tmp_path / "stage-gaps.json").write_text(json.dumps(doc), encoding="utf-8")
    gate = G._stage_gap_gate(tmp_path, [])
    assert gate.level == "PASS" and "UNDER A LIVE SENTENCE" not in gate.message
