"""The two defaults a WORLD-TAKING transition implies (P53 T2 / T6; BACKLOG R26-60, R26-66).

Measured before either was written (`measure_stage_gaps.py` on `normal-for-which-bridge/build-short-axes`): the
suck at 13.79 s and the melt at 40.51 s each left the stage with no world on it for 3.1 s, 8.9% of a 69.8 s short,
and both ran under a live sentence. An inked arrival on the page that FOLLOWS took the measured share to 0.0%.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402


def _page_scene(sid: str, a: float, b: float, exit_id: str | None = None, **page) -> dict:
    return {"scene_id": sid, "span": [a, b], "exit": exit_id,
            "world": {"kind": "ledger", "page": {"schema_version": "ledger_page.v1", "builder": "story", **page}}}


def test_the_page_a_suck_takes_is_stamped_cut():
    """E47: the boundary between scenes[i-1] and scenes[i] is scenes[i]["exit"] - the suck INTO s02 takes s01's world,
    so s01's page must not retract into it first (R26-60)."""
    scenes = [_page_scene("s01", 1.0, 10.0, "cut"), _page_scene("s02", 10.0, 20.0, "suck:0.5,0.5")]
    notes = B.stamp_transition_pages(scenes)
    assert scenes[0]["world"]["page"]["exit"] == "cut", "R26-60: the outgoing page must not retract itself into the suck"
    assert "exit" not in scenes[1]["world"]["page"], "the incoming page keeps its own exit"
    assert any("exit=cut" in n and "s01" in n for n in notes), notes


def test_chart_to_chart_the_next_page_is_on_its_axes_whatever_the_transition():
    """The operator, 2026-09-12: "The empty cream stage isnt supposed to be on stage during the exits ... It doesnt make
    sense to do that when transitioning from chart-to-chart" - review-v1's cream at 0:34 followed a CUT between charts."""
    for kind in ("cut", "melt", "suck:0.5,0.5", "dip", "wipe_right"):
        scenes = [_page_scene("s01", 1.0, 10.0, "cut"), _page_scene("s02", 10.0, 20.0, kind)]
        notes = B.stamp_transition_pages(scenes)
        assert scenes[1]["world"]["page"]["enter"] == "axes", kind
        assert any("s02" in n and "enter=axes" in n for n in notes), (kind, notes)


def test_only_a_world_taking_transition_stamps_the_outgoing_page():
    for kind in ("cut", "dip", "wipe_right", None):
        scenes = [_page_scene("s01", 1.0, 10.0, "cut"), _page_scene("s02", 10.0, 20.0, kind)]
        B.stamp_transition_pages(scenes)
        assert "exit" not in scenes[0]["world"]["page"], kind


def test_a_page_after_a_plate_keeps_its_own_arrival():
    """The empty cream roll-out belongs to the mount (a ledger plate onto a narrative plate)."""
    scenes = [{"scene_id": "s01", "span": [1.0, 10.0], "exit": "cut", "world": {"asset_id": "plate-x"}},
              _page_scene("s02", 10.0, 20.0, "suck:0.5,0.5")]
    assert B.stamp_transition_pages(scenes) == []
    assert "enter" not in scenes[1]["world"]["page"]


def test_the_hook_opens_on_the_axes_register():
    """The operator, 2026-09-12: "hook should open on the axes register, then we immediately answer it on the ledger"."""
    scenes = [_page_scene("s01", 0.0, 10.0, "cut"), {"scene_id": "s02", "span": [10.0, 20.0], "exit": "dip", "world": {"asset_id": "plate-y"}}]
    notes = B.stamp_transition_pages(scenes)
    assert scenes[0]["world"]["page"]["enter"] == "axes"
    assert any("s01" in n and "hook" in n for n in notes), notes


def test_a_hook_that_declares_its_enter_is_left_alone():
    scenes = [_page_scene("s01", 0.0, 10.0, "cut", enter="built")]
    assert B.stamp_transition_pages(scenes) == []
    assert scenes[0]["world"]["page"]["enter"] == "built"


def test_an_author_who_chose_is_not_corrected():
    scenes = [_page_scene("s01", 1.0, 10.0, "cut", exit="cut"),
              _page_scene("s02", 10.0, 20.0, "suck", enter="spiral")]
    assert B.stamp_transition_pages(scenes) == []
    assert scenes[1]["world"]["page"]["enter"] == "spiral"


def test_a_world_that_is_not_a_page_is_left_alone():
    scenes = [{"scene_id": "s01", "span": [0.0, 10.0], "exit": "cut", "world": {"asset_id": "plate-x"}},
              {"scene_id": "s02", "span": [10.0, 20.0], "exit": "suck", "world": {"asset_id": "plate-y"}}]
    assert B.stamp_transition_pages(scenes) == []


def _line(n: int) -> list:
    return [{"name": "a", "pts": [[k, k] for k in range(n)]}, {"name": "b", "pts": [[k, 2 * k] for k in range(n)]}]


def test_a_ring_on_the_last_datum_marks_the_tip():
    """review-v1 0:57: the dashed ring on the last datum sat on the line's own name, "x3.9 Federal debt"."""
    sc = _page_scene("s01", 1.0, 10.0, "cut", series=_line(10))
    sc["species"] = [{"kind": "ring", "target": {"kind": "datum", "index": 9}},
                     {"kind": "callout", "target": {"kind": "datum", "series": 1, "index": 8}}]
    notes = B.stamp_tip_marks([sc])
    assert sc["world"]["page"]["tip_mark"] == [0, 1]
    assert any("tip_mark" in n for n in notes), notes


def test_a_figure_or_a_ring_mid_line_marks_no_tip():
    sc = _page_scene("s01", 1.0, 10.0, "cut", series=_line(10))
    sc["species"] = [{"kind": "figure", "target": {"kind": "datum", "index": 9}},
                     {"kind": "ring", "target": {"kind": "datum", "index": 3}}]
    assert B.stamp_tip_marks([sc]) == []
    assert "tip_mark" not in sc["world"]["page"]


def test_a_declared_tip_mark_is_left_alone():
    sc = _page_scene("s01", 1.0, 10.0, "cut", series=_line(10), tip_mark=[])
    sc["species"] = [{"kind": "ring", "target": {"kind": "datum", "index": 9}}]
    assert B.stamp_tip_marks([sc]) == []
    assert sc["world"]["page"]["tip_mark"] == []


# ---- E88 / R26-76: THE MELT TAKES THE CHART, NOT THE BOARD ----------------------------------------------------------
def _plate_scene(sid: str, a: float, b: float, exit_id: str | None = None) -> dict:
    return {"scene_id": sid, "span": [a, b], "exit": exit_id, "world": {"asset_id": "plate-" + sid}}


def test_a_melt_out_of_a_world_that_is_not_a_page_is_refused():
    """The whole-world melt is retired: a melt takes a chart's ink and leaves the board, so there must be a page."""
    for ending in ("melt", "melt:throw", "melt:splash:chart", "melt:splash:plate"):
        scenes = [_plate_scene("s01", 1.0, 10.0, "cut"), _page_scene("s02", 10.0, 20.0, ending)]
        with pytest.raises(ValueError, match="not a ledger page"):
            B.stamp_transition_pages(scenes)


def test_a_throw_and_a_chart_splash_need_a_page_to_draw_the_next_chart_on():
    for ending in ("melt", "melt:throw", "melt:splash:chart"):
        scenes = [_page_scene("s01", 1.0, 10.0, "cut"), _plate_scene("s02", 10.0, 20.0, ending)]
        with pytest.raises(ValueError, match="s01 -> s02"):
            B.stamp_transition_pages(scenes)


def test_a_plate_splash_needs_a_plate():
    scenes = [_page_scene("s01", 1.0, 10.0, "cut"), _page_scene("s02", 10.0, 20.0, "melt:splash:plate")]
    with pytest.raises(ValueError, match="say melt:splash:chart"):
        B.stamp_transition_pages(scenes)
    ok = [_page_scene("s01", 1.0, 10.0, "cut"), _plate_scene("s02", 10.0, 20.0, "melt:splash:plate")]
    notes = B.stamp_transition_pages(ok)
    assert ok[0]["world"]["page"]["exit"] == "cut", "the page it takes still does not retract first (R26-60)"
    assert any("exit=cut" in n for n in notes), notes


def test_a_chart_splash_page_arrives_built_out_of_the_splatter():
    scenes = [_page_scene("s01", 1.0, 10.0, "cut"), _page_scene("s02", 10.0, 20.0, "melt:splash:chart")]
    notes = B.stamp_transition_pages(scenes)
    assert scenes[1]["world"]["page"]["enter"] == "built", "not its normal build, and not the axes register"
    assert any("s02" in n and "enter=built" in n for n in notes), notes
    declared = [_page_scene("s01", 1.0, 10.0, "cut"), _page_scene("s02", 10.0, 20.0, "melt:splash:chart", enter="axes")]
    with pytest.raises(ValueError, match="build under the stains"):
        B.stamp_transition_pages(declared)


def test_a_throw_hands_the_same_board_to_the_next_chart_on_its_axes():
    scenes = [_page_scene("s01", 1.0, 10.0, "cut"), _page_scene("s02", 10.0, 20.0, "melt:throw")]
    B.stamp_transition_pages(scenes)
    assert scenes[1]["world"]["page"]["enter"] == "axes" and scenes[0]["world"]["page"]["exit"] == "cut"


# ---- E87 s3 / R26-75: THE SLIDE - A HAND-OFF, NOT A WORLD-TAKING TRANSITION -----------------------------------------
def test_a_slide_names_the_direction_it_pushes_along_and_may_carry_its_own_length():
    """E87 s3 (the operator, 2026-09-13: *"We should also have a push/slide option ... basically literally pushing out
    one frame with the next, so that you keep some of that congruency"*): `slide:<left|right|up|down>[:<s>]`. The
    direction is the axis AND the sign - which way the outgoing frame is pushed - and is never defaulted: a slide with
    no direction is a slide nobody authored. The player's `slideOpts` reads the same grammar; these two are one
    statement made twice."""
    for d in B.SLIDE_DIRECTIONS:
        assert B.parse_exit(f"slide:{d}") == (f"slide:{d}", None), d
        assert B.parse_exit(f"slide:{d}:0.9") == (f"slide:{d}:0.9", 0.9), d
        assert B.scene_exit(f"slide:{d}", True) == (f"slide:{d}", None), "an authored slide wins"
    assert B.SLIDE_DIRECTIONS == ("left", "right", "up", "down")
    assert "slide" in B.SCENE_EXITS and "slide" in B.TIMED_EXITS
    assert B.SLIDE_S == 0.6, "the default length the player's SLIDE_S carries too"


def test_a_slide_with_no_direction_an_unknown_one_or_push_is_refused():
    """`push` is OUR camera push-in and the name is not reused (E87 s3) - this transition is `slide`."""
    with pytest.raises(ValueError, match="names no direction"):
        B.parse_exit("slide")
    with pytest.raises(ValueError, match="the camera push-in"):
        B.parse_exit("slide:push")
    for bad in ("slide:", "slide:sideways", "slide:LEFT", "slide:0.5", "slide:left:0", "slide:left:-1",
                "slide:left:soon", "slide:left:0.5:0.5"):
        with pytest.raises(ValueError):
            B.parse_exit(bad)


def test_the_mechanical_default_is_never_a_slide():
    """A slide is AUTHORED or it does not happen: `scene_exit`'s table is the dip, the cut, and what the row says."""
    for docks in (True, False):
        for enter in (None, "mount", "spiral", "morph", "built"):
            for changed in (True, False):
                assert B.scene_exit(None, docks, enter, changed)[0] != "slide"
    assert "slide" not in B.LEDGER_EXITS, "the page's own retract law is untouched: a slide hands over the WORLD"


def test_a_slide_hands_over_and_never_takes_the_outgoing_world():
    """The slide is a HAND-OFF: the outgoing page keeps its own law (it is not stamped `exit=cut` the way the page a
    suck or a melt TAKES is), and the incoming chart arrives on its axes exactly as it does across a cut - so M31
    reads the boundary as chart-to-chart (any non-dip boundary with a page on both sides, gate_motion_density.py
    `_into_page`) and never sees empty cream there."""
    assert "slide" not in B.WORLD_TAKING_EXITS
    for kind in ("slide:left", "slide:up:0.4"):
        scenes = [_page_scene("s01", 1.0, 10.0, "cut"), _page_scene("s02", 10.0, 20.0, kind)]
        notes = B.stamp_transition_pages(scenes)
        assert "exit" not in scenes[0]["world"]["page"], kind
        assert scenes[1]["world"]["page"]["enter"] == "axes", kind
        assert any("s02" in n and "enter=axes" in n and "slide" in n for n in notes), (kind, notes)
