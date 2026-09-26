"""P72 T7b (R26-342) - M21 reads what the page does on screen: a PARK ends the chart's deployed life, an UN-PARK opens
a new one.

P69 T32 (Steel and Paper H, row 24 of the treatment = table row 26): the divergence page returns drawn by the spiral
(landed 766.77 s), PARKS to a third for the agenda and three cards on "You now have" (770.42), grows back on "a copy
of this chart" (788.94 + 0.9), is rung twice and takes the certificate - and M21 read ONE deployed life of 38.8 s
(12:47 -> 13:26), because the clock counted only the build's marks. Table row 24 (s24) is the same class through a
panels page's focus: a `panel_focus` with a `region` fits the panels into a box for the card beside them, and the
next focus without one grows them back.

So a page's span is cut into FULL-STAGE WINDOWS by its parks, and E50's clock runs inside each window as it always
has. What does NOT move the clock is kept exactly: an annotation (a callout, a ring, a retitle, a relight) never
restarts it (E50 section 1, the operator's own words), and a card landing on the page never does either (E50 section 2:
the 12 s ceiling exists so a chart can hold still under a dock). A page that never parks reads byte-identical.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import gate_motion_density as G  # noqa: E402


def _page(sid, a, z, species=None, enter="spiral", docks=None):
    return {"scene_id": sid, "span": [a, z], "species": species or [], "docks": docks or [],
            "world": {"kind": "ledger", "page": {"schema_version": "ledger_page.v1", "builder": "story", "enter": enter}}}


def _park(at, scale, dur=0.9):
    return {"kind": "chart_to", "to": "park", "at": at, "dur": dur, "scale": scale, "anchor": "left"}


def _ring(at, dur=4.0):
    return {"kind": "callout", "at": at, "dur": dur, "target": {"kind": "datum", "index": 12, "series": 0}}


def _focus(at, region=None, dur=1.2):
    sp = {"kind": "panel_focus", "layout": "row", "at": at, "dur": dur, "roles": ["active", "hidden", "hidden"],
          "recede": {"scale": 0.86, "dim": 0.55, "blur": 5.0}, "boxes": [None, None, None]}
    if region is not None:
        sp["region"] = region
    return sp


def _s26():
    """H's s26 as compiled (lane A 39fc26a build-h): the spiral return, the park, the un-park, two rings, a card."""
    return _page("s26", 765.17, 805.58,
                 species=[{"kind": "retitle", "at": 765.17, "dur": 1.6, "text": "Steel gets used. Paper gets believed."},
                          _park(770.42, 0.34), {"kind": "agenda", "at": 771.4, "dur": 3.4, "rows": []},
                          _park(788.94, 1.0), _ring(793.05, 5.06), _ring(798.31, 3.85)],
                 docks=[{"slide": "dock-h-tripwire-board", "enter": 775.1, "exit": 780.36, "arrive": "land"},
                        {"slide": "dock-h-railway-share-close", "enter": 802.36, "exit": 805.58, "arrive": "land"}])


def _s24():
    """H's s24: a PANELS page whose focus fits the panels into a box for the card, then grows them back."""
    return _page("s24", 716.79, 743.04,
                 species=[_focus(716.79, dur=0.05), _focus(728.66, region=[0.02, 0.22, 0.345, 0.58]), _focus(739.06)],
                 docks=[{"slide": "dock-h-memory-arithmetic", "enter": 729.26, "exit": 739.06, "arrive": "throw"}])


def _lives(scene):
    return G._deployed_lives([scene])


# ---- the park ends a life; the un-park opens one --------------------------------------------------------------

def test_the_park_ends_the_returning_pages_first_life_and_the_un_park_opens_the_next():
    land = 765.17 + G._page_land_offset(_s26())
    assert _lives(_s26()) == [("s26", round(land, 2), 770.42, round(770.42 - land, 2)),
                              ("s26", 789.84, 805.58, 15.74)], _lives(_s26())


def test_the_rings_after_the_un_park_do_not_restart_the_clock_E50_section_1():
    """The two callouts at 793.05 and 798.31 add no data - the un-park's life still runs from its land to the exit."""
    last = _lives(_s26())[-1]
    assert last[1] == 789.84 and last[2] == 805.58, last


def test_a_card_landing_on_the_page_does_not_restart_the_clock_E50_section_2():
    s = _s26()
    s["docks"].append({"slide": "late-card", "enter": 795.0, "exit": 805.58, "arrive": "throw"})
    assert _lives(s)[-1][1] == 789.84


def test_a_page_that_parks_and_never_un_parks_ends_its_life_at_the_park():
    s = _page("s05", 100.0, 140.0, species=[_park(110.0, 0.55)])
    land = round(100.0 + G._page_land_offset(s), 2)
    assert _lives(s) == [("s05", land, 110.0, round(110.0 - land, 2))], _lives(s)


def test_a_panels_page_parks_by_its_focus_region_and_un_parks_when_the_region_goes():
    land = round(716.79 + G._page_land_offset(_s24()), 2)
    assert _lives(_s24()) == [("s24", land, 728.66, round(728.66 - land, 2)),
                              ("s24", 740.26, 743.04, 2.78)], _lives(_s24())


def test_a_build_after_the_un_park_restarts_the_clock_inside_its_window():
    s = _s26()
    s["species"].append({"kind": "build_to", "at": 792.0, "dur": 1.0, "series": 0, "target": {"kind": "datum", "index": 3}})
    assert _lives(s)[-1] == ("s26", 793.0, 805.58, 12.58)


def test_an_undraw_after_the_un_park_ends_that_window():
    s = _s26()
    s["species"].append({"kind": "undraw", "at": 797.0, "dur": 1.0})
    assert _lives(s)[-1] == ("s26", 789.84, 797.0, 7.16)


def test_a_mark_made_while_parked_opens_nothing_the_un_park_does():
    """Tokyo's s04 class: the chart changes while it is parked (a build here; a recast there) - the stretch it stands
    at full size again begins at the un-park's land, not at that mark."""
    s = _page("s06", 100.0, 140.0, species=[_park(110.0, 0.5),
                                             {"kind": "build_to", "at": 112.0, "dur": 1.0, "series": 1, "target": {"kind": "datum", "index": 5}},
                                             _park(120.0, 1.0)])
    assert _lives(s)[-1] == ("s06", 120.9, 140.0, 19.1), _lives(s)


def test_a_second_park_while_parked_moves_no_window():
    """Re-parking to another size is still parked: the window opened by the un-park is the only one after it."""
    s = _page("s07", 100.0, 150.0, species=[_park(110.0, 0.55), _park(115.0, 0.4), _park(130.0, 1.0)])
    lives = _lives(s)
    assert [l[1:3] for l in lives][1:] == [(130.9, 150.0)], lives


def test_an_un_park_on_a_page_that_never_parked_moves_nothing():
    """A scale-1.0 park with no park before it grows nothing back - the chart was never out of its full size."""
    plain = _page("s08", 100.0, 130.0)
    same = _page("s08", 100.0, 130.0, species=[_park(110.0, 1.0)])
    assert _lives(same) == _lives(plain)


def test_a_panel_park_is_the_panels_own_and_moves_no_page_window():
    """`chart_to park` with `panel: i` shrinks ONE panel of a panels page (PANEL_CHART_TO) - the page keeps the stage."""
    plain = _page("s09", 100.0, 130.0)
    one = _page("s09", 100.0, 130.0, species=[dict(_park(110.0, 0.5), panel=1)])
    assert _lives(one) == _lives(plain)


# ---- the gate's row ------------------------------------------------------------------------------------------

def test_m21_names_the_un_park_life_and_s26_still_warns_on_it():
    g = G._deployed_gate([_s26()])
    assert g.level == "WARN", g
    assert "s26 15.7s" in g.message and "after its un-park" in g.message, g.message
    assert "38.8" not in g.message, g.message


def test_the_floor_never_fires_on_a_life_opened_by_an_un_park():
    """s24's un-park life is 2.78 s to the exit: the viewer read that chart before it parked - it is no page cut short."""
    s = _s24()
    s["world"]["page"]["enter"] = "built"
    g = G._deployed_gate([s])
    assert g.level == "INFO" and "short" not in g.message, g.message


# ---- what must NOT move ---------------------------------------------------------------------------------------

def test_a_page_with_no_park_reads_as_before_rings_and_all():
    """s20's class (a returning page rung twice, no park): one life from the landing to the exit - the rings never
    restart it (E50 section 1), so its WARN stands and is the author's to answer."""
    s = _page("s20", 513.69, 533.8, species=[_ring(517.62, 3.42), _ring(521.24, 6.71)])
    land = round(513.69 + G._page_land_offset(s), 2)
    assert _lives(s) == [("s20", land, 533.8, round(533.8 - land, 2))]
    assert G._deployed_gate([s]).level == "WARN"


def test_the_arrive_built_floor_still_fires_on_a_page_cut_short_with_no_park():
    s = _page("s03", 100.0, 103.0, enter="built")
    g = G._deployed_gate([s])
    assert g.level == "WARN" and "short" in g.message, g.message
