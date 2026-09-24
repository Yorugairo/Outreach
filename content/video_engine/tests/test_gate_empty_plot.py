"""M47 - THE EMPTY PLOT (P69 T87). Row 22's first cut of Steel and Paper H held the customs monitor's axes with ZERO
drawn series for 18 s (605.9-624 s): the tripwire board sat on an empty plot, then the RAM stamp sat alone on it. The
gate passed it; only the parent's frame read caught it (E25 a chart proves a sentence, the chart-to-chart ruling never
empty ground, E21 the screen never still). A defect only a frame read caught gets a gate.

The ink is read off the compiled timeline's own clocks - the page's build, its `build_to` caps, its undraws, its
`chart_to` hand-overs and the marks it carries - never off pixels."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_motion_density as G  # noqa: E402
from authoring import shapes as SH  # noqa: E402

H_BUILD = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h"
H_TL = "steel-and-paper-h.timeline.json"
LINE = [{"name": "DRAM", "pts": [[2023 + i / 12, 100 + i] for i in range(43)]},
        {"name": "HBM-CLASS", "pts": [[2023 + i / 12, 90 + i] for i in range(43)]}]


def _cap(at: float, index: int, series: int, dur: float = 0.4) -> dict:
    return {"kind": "build_to", "at": at, "dur": dur, "series": series, "target": {"kind": "datum", "index": index}}


def _line_page(sid: str, span: tuple[float, float], species: list[dict], *, enter: str = "axes", exit: str = "cut",
               states: list[dict] | None = None, docks: list[dict] | None = None, builder: str = "dense-line",
               **page) -> dict:
    world = {"kind": "ledger", "page": {"builder": builder, "enter": enter, "exit": exit, "series": LINE,
                                        "values": [], "axes": {"ylabel": "USD per kilogram"}, **page}}
    if states:
        world["page_states"] = states
    return {"scene_id": sid, "span": list(span), "world": world, "species": species, "docks": docks or []}


def _bars_state() -> dict:
    return {"builder": "story", "values": [-3.9, -12.4, -5.3], "labels": ["a", "b", "c"], "axes": {}}


def _m47(scenes: list[dict], kinetics: dict | None = None) -> G.Gate | None:
    return G._empty_plot_gate(scenes, kinetics or {})


def _first_cut() -> dict:
    """Row 22's first cut: the monitor's axes land at 605.9, both series held at index 0 (the build beat spent on a
    cap of nothing), the tripwire board docked over the bare axes, and the line only draws at 624.0."""
    board = {"slide": "tripwire-board", "enter": 606.4, "exit": 616.0}
    stamp = {"slide": "ram-stamp", "enter": 616.5, "exit": 623.8, "arrive": "stamp"}
    return _line_page("s22", (605.9, 660.0), [_cap(605.9, 0, 0), _cap(605.9, 0, 1), _cap(624.0, 40, 0, 5.4),
                                              _cap(624.0, 40, 1, 5.4)], docks=[board, stamp])


# ---- the five fixtures the brief names ---------------------------------------------------------------------------

def test_row_22_first_cut_fails_with_its_seconds_and_scene():
    g = _m47([_first_cut()])
    assert g is not None and g.id == "M47" and g.level == "FAIL", g
    assert "s22 18.1s" in g.message and "10:05" in g.message, g.message
    assert "2 card(s) over it" in g.message, g.message


def test_a_series_drawn_within_a_second_of_landing_passes():
    page = _line_page("s22", (605.9, 660.0), [_cap(605.9, 0, 0), _cap(605.9, 0, 1), _cap(606.9, 40, 0, 5.4),
                                             _cap(606.9, 40, 1, 5.4)])
    g = _m47([page])
    assert g.level == "PASS", g.message
    assert "longest empty 1.0s" in g.message, g.message


def test_a_one_second_recast_hand_over_passes():
    page = _line_page("s22", (600.0, 640.0), [{"kind": "chart_to", "at": 620.0, "dur": 1.0, "to": "recast", "state": 1}],
                      states=[_bars_state()])
    g = _m47([page])
    assert g.level == "PASS", g.message
    assert "longest empty 1.0s" in g.message and "s22 at 10:20" in g.message, g.message


def test_a_two_and_a_half_second_hand_over_warns():
    page = _line_page("s22", (600.0, 640.0), [{"kind": "chart_to", "at": 620.0, "dur": 2.5, "to": "recast", "state": 1}],
                      states=[_bars_state()])
    g = _m47([page])
    assert g.level == "WARN", g.message
    assert "s22 2.5s (10:20 -> 10:22" in g.message, g.message


def test_the_warn_edge_is_one_and_a_half_seconds_and_the_fail_edge_four():
    def gap(d: float) -> str:
        page = _line_page("p", (100.0, 140.0), [{"kind": "chart_to", "at": 120.0, "dur": d, "to": "recast", "state": 1}],
                          states=[_bars_state()])
        return _m47([page]).level
    assert gap(G.EMPTY_PLOT_WARN_S) == "PASS" and gap(G.EMPTY_PLOT_WARN_S + 0.1) == "WARN"
    assert gap(G.EMPTY_PLOT_FAIL_S) == "WARN" and gap(G.EMPTY_PLOT_FAIL_S + 0.1) == "FAIL"
    assert (G.EMPTY_PLOT_WARN_S, G.EMPTY_PLOT_FAIL_S) == (1.5, 4.0)


# ---- the ink model ----------------------------------------------------------------------------------------------

def test_an_undraw_takes_the_ink_and_a_held_empty_plot_fails():
    """E50 asks a page to end its life with an undraw - and then to become the next thing, not to hold bare axes."""
    page = _line_page("s05", (60.0, 100.0), [{"kind": "undraw", "at": 90.0, "dur": 0.6, "target": {"kind": "datum", "index": 0}}])
    g = _m47([page])
    assert g.level == "FAIL" and "s05 10.0s (1:30 -> 1:40" in g.message, g.message


def test_a_build_to_after_an_undraw_redraws_the_line():
    page = _line_page("s05", (60.0, 100.0), [{"kind": "undraw", "at": 90.0, "dur": 0.6, "target": {"kind": "datum", "index": 0}},
                                            _cap(91.0, 20, 0)])
    assert _m47([page]).level == "PASS"


def test_a_partial_undraw_or_one_series_undrawn_keeps_ink():
    partial = _line_page("a", (60.0, 100.0), [{"kind": "undraw", "at": 90.0, "dur": 0.6, "target": {"kind": "datum", "index": 12}}])
    one = _line_page("b", (100.0, 140.0), [{"kind": "undraw", "at": 130.0, "dur": 0.6, "series": 0,
                                           "target": {"kind": "datum", "index": 0}}])
    tail = _line_page("c", (140.0, 180.0), [{"kind": "undraw", "at": 170.0, "dur": 0.6, "paths": "tail",
                                            "target": {"kind": "datum", "index": 0}}])
    assert _m47([partial, one, tail]).level == "PASS"


def test_a_roll_out_page_is_not_empty_before_its_build_the_axes_belong_to_the_build():
    """`lpPaintChart`: `cs.chart.style.opacity = c > 0 ? 1 : 0` - the axes stand from the build's first frame, so the
    roll, the savor and the field are the page arriving, never an empty plot."""
    page = _line_page("s01", (0.0, 30.0), [], enter=None, exit="retract")
    g = _m47([page])
    assert g.level == "PASS" and "longest empty 0.0s" in g.message, g.message


def test_a_bars_page_has_ink_from_its_build_whatever_the_caps():
    page = _line_page("s12", (0.0, 30.0), [_cap(0.0, 0, 0), _cap(20.0, 2, 0)], builder="story", series=[],
                      values=[94.0], labels=["x"])
    assert _m47([page]).level == "PASS"


def test_a_comparator_line_is_ink_before_the_series_draws():
    """H's s08 (2:42): the railway yardstick (`axes.hlines`, ~50%) stands with its label while both series are held at
    index 0 for 5.5 s - the comparator before the series, a chart already proving its sentence (frame read 166.0 s)."""
    page = _line_page("s08", (162.6, 195.8), [_cap(162.6, 0, 0), _cap(162.6, 0, 1), _cap(168.12, 124, 0, 9.6)],
                      axes={"hlines": [{"y": 50, "label": "British railways, 1844-47 - ~50%"}]})
    assert _m47([page]).level == "PASS"
    bare = _line_page("s08", (162.6, 195.8), [_cap(162.6, 0, 0), _cap(162.6, 0, 1), _cap(168.12, 124, 0, 9.6)])
    assert _m47([bare]).level == "FAIL"
    one = _line_page("s08", (162.6, 195.8), [_cap(162.6, 0, 0), _cap(162.6, 0, 1), _cap(168.12, 124, 0, 9.6)],
                     axes={"hline": {"y": 50, "label": "the yardstick"}})   # the engine's `hlines || [hline]`
    assert _m47([one]).level == "PASS"


def test_a_keyed_recast_and_a_rescale_hand_over_without_emptying_the_plot():
    keyed = _line_page("k", (0.0, 40.0), [{"kind": "chart_to", "at": 20.0, "dur": 3.0, "to": "recast", "state": 1,
                                           "keyed": True}], states=[_bars_state()])
    rescale = _line_page("r", (40.0, 80.0), [{"kind": "chart_to", "at": 60.0, "dur": 3.0, "to": "rescale", "state": 1}],
                         states=[{"builder": "dense-line", "series": LINE, "values": []}])
    remake = _line_page("m", (80.0, 120.0), [{"kind": "chart_to", "at": 100.0, "dur": 3.0, "to": "remake", "state": 1}],
                        states=[_bars_state()])
    assert _m47([keyed, rescale, remake]).level == "PASS"


def test_a_plain_morph_is_a_recast_unless_the_arap_morph_is_on():
    page = _line_page("m", (0.0, 40.0), [{"kind": "chart_to", "at": 20.0, "dur": 3.0, "to": "morph", "state": 1}],
                      states=[_bars_state()])
    assert _m47([page]).level == "WARN"
    assert _m47([page], {"arap_morph": True}).level == "PASS"


def test_a_mark_on_the_plot_is_ink_while_it_is_live():
    """shapes.PLOT_MARKS (less the undraw, which takes ink): a bracket, a figure, a lit stretch... on the plot."""
    page = _line_page("s22", (605.9, 660.0), [_cap(605.9, 0, 0), _cap(605.9, 0, 1),
                                             {"kind": "bracket", "at": 606.0, "dur": 17.0, "from": 0, "to": 3},
                                             _cap(624.0, 40, 0), _cap(624.0, 40, 1)])
    assert _m47([page]).level == "PASS"


def test_a_panels_page_is_empty_until_its_first_panel_builds():
    panels = [{"builder": "dense-line", "series": LINE}, {"builder": "dense-line", "series": LINE}]
    focus = [{"kind": "panel_focus", "at": 10.0, "dur": 0.6, "roles": ["hidden", "hidden"]},
             {"kind": "panel_focus", "at": 13.0, "dur": 0.6, "roles": ["active", "hidden"]}]
    page = _line_page("s21", (10.0, 60.0), focus, builder="panels", series=[], panels=panels)
    g = _m47([page])
    assert g.level == "WARN" and "s21 3.0s (0:10 -> 0:13" in g.message, g.message
    shown = _line_page("s21", (10.0, 60.0), [], builder="panels", series=[], panels=panels)
    assert _m47([shown]).level == "PASS"


def test_the_retract_is_the_page_leaving_not_an_empty_plot():
    page = _line_page("s09", (0.0, 30.0), [{"kind": "undraw", "at": 27.5, "dur": 0.5, "target": {"kind": "datum", "index": 0}}],
                      exit="retract")
    g = _m47([page])
    assert g.level == "PASS" and "longest empty 0.5s" in g.message, g.message


# ---- scope ------------------------------------------------------------------------------------------------------

def test_no_row_without_a_plot_page():
    plate = {"scene_id": "p", "span": [0.0, 10.0], "world": {"asset_id": "host-plate"}, "species": [], "docks": []}
    pie = _line_page("pie", (10.0, 30.0), [], builder="share", series=[])
    assert _m47([plate]) is None and _m47([plate, pie]) is None


def test_the_mark_mirror_is_shapes_plot_marks_less_the_undraw():
    assert set(G.PLOT_INK_MARKS) == set(SH.PLOT_MARKS) - {"undraw"}
    assert set(G.PLOT_HELD_MARKS) == set(SH.HELD_MARKS)


def test_run_carries_the_row():
    tl = {"runtime_s": 60.0, "scenes": [_first_cut() | {"span": [0.0, 60.0]}]}
    tl["scenes"][0]["species"] = [_cap(0.0, 0, 0), _cap(0.0, 0, 1), _cap(18.1, 40, 0), _cap(18.1, 40, 1)]
    gates, _ = G.run(tl, [], {"cues": []})
    m47 = [g for g in gates if g.id == "M47"]
    assert len(m47) == 1 and m47[0].level == "FAIL" and "s22 18.1s" in m47[0].message, m47


# ---- the committed H door (gitignored - read only when on disk) -------------------------------------------------

@pytest.mark.skipif(not (H_BUILD / H_TL).exists(), reason="the H door's build is not on disk")
def test_the_committed_h_door_flip_hand_over_is_measured_and_under_the_warn_edge():
    """The H door (77c8921): row 22's flip - the bars recast back to the monitor at 663.02 over 0.8 s, the lines redrawn
    at 663.92 - is a hand-over of ~0.9 s, measured and under 1.5 s. Any other finding on the door is reported by the
    gate itself (T87's NOTES carry the door's row), not pinned here: the door is rebuilt slice by slice."""
    tl, _docks, _mp = G._load(H_BUILD, H_TL)
    _pages, bare = G._empty_plots(tl.get("scenes", []), tl.get("kinetics") or {})
    flip = [b for b in bare if b[0] == "s22"]
    assert any(abs(a - 663.02) < 0.05 for _sid, a, _d, _n in flip), flip
    assert all(d <= G.EMPTY_PLOT_WARN_S for _sid, _a, d, _n in flip), flip
