"""P72 T6: THE VALUE GATE READS EVERY PAGE - R26-318, R26-303, R26-264 and R26-319.

M26 (R26-40) reads a bar's printed number against the height it is drawn at, on the scale the page prints. Four holes:

  R26-318 (the highest: "a truth gate that silently cannot read is a false PASS"). The long form's sheet paints no gridline
          and hides a zero line on its panel's edge, so the probe paired no tick label with a rule, wrote no `page.bars`,
          and M26 reported INFO "no bars page printed a value" over the whole H episode - row 12's 94 page among them.
          The rules are still in the page, only unpainted: the fix reads each DECLARED tick rule from its own live
          geometry (the attributes every scale painter moves with the bars) through its parent's screen CTM, and pairs it
          with a PRINTED tick label exactly as a painted one is paired. Never a threshold fitted to our frames (E38). A
          bars page the probe still cannot read - no printed tick on a rule, or no zero rule - is written `ns` and FAILs
          by name.
  R26-303 "+55–60%" read as 5560. A range reads as its two ends: the bar is judged at the end nearest zero (the one it
          is drawn to, `ledger_page.range_foot`) and its band at the far end.
  R26-264 a card's own badge (a pill INSIDE the dock) was counted as page ink the card covers (M25 / M27 FAIL on the sell
          ticket's own SELL badge). A dock's own children are never page ink under it.
  R26-319 `form=gauge:h` - the horizontal fill gauge - is admitted: its fill is a WIDTH, and M26 reads widths.

Every page M26 read before reads the same (the old path first: a visible rule under a tick label; the map only when it
finds none), so the committed probes do not move.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import probe as P  # noqa: E402
import render_baseline as RB  # noqa: E402

H_EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
H_OBJ = "ev-capex-ocf-94-bars-v1"                       # PIMCO Fig. 3: 94 % of operating cash flow (H rows 12 and 17)
ROW12 = f"ledger:{H_OBJ}:bars::right:axes:cut;idle=live;readability=longform"   # SHOT-TABLE-H.md row 12, verbatim
ROW12_TITLE = "Ninety-four cents of every dollar"
GAUGE_H = f"ledger:{H_OBJ}:progress::right;form=gauge:h"
GAUGE_V = f"ledger:{H_OBJ}:progress::right;form=gauge"
KEN = (0, 0, 0)
REST_T = 9.0
BUILD = [(round(0.25 * k, 2), "build") for k in range(0, 37)] + [(REST_T, "hold")]


def world(plate: str, ep_dir: Path = H_EP) -> dict:
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        return B.world_for_plate(plate, KEN, ep_dir)
    finally:
        B.ASPECT = saved


# ---- R26-318: a page the probe cannot read FAILs by name (browser-free) ------------------------------------------------
def _doc(*pages: dict, aspect: str = "16:9") -> dict:
    return {"aspect": aspect, "instants": [{"t": 1.0 + i, "why": "x", "page": {"bars": pg}} for i, pg in enumerate(pages)]}


READ_OK = {"base": 500, "tick": [100, 100], "b": [{"l": "a", "h": 200, "y": 300, "v": "50%"}]}


def test_the_fail_header_counts_value_faults() -> None:
    doc = _doc({"ns": "no scale", "pg": "X", "b": [{"l": "a", "h": 300, "y": 400, "v": "20%"}]})
    assert G._values_gate(doc).message.startswith("1 value fault(s) over 1 instants probed"), G._values_gate(doc).message


def test_a_painted_page_with_an_unusable_scale_fails_by_name() -> None:
    """Round 2 (MEDIUM 3): the zero line ABOVE the tick (span <= 1), a one-member tick, a zero tick - a scale the row cannot
    read is never a silent skip once a value is printed."""
    for bars in ({"base": 0, "tick": [100, 324], "b": [{"l": "a", "h": 300, "y": 400, "v": "20%"}]},
                 {"base": 500, "tick": [100], "b": [{"l": "a", "h": 300, "y": 200, "v": "20%"}]},
                 {"base": 500, "tick": [0, 100], "b": [{"l": "a", "h": 300, "y": 200, "v": "20%"}]}):
        gate = G._values_gate(_doc(dict(bars, pg="Unusable")))
        assert gate.level == "FAIL" and "unreadable scale on 'Unusable'" in gate.message, (bars, gate.message)
    quiet = {"base": 0, "tick": [100, 324], "b": [{"l": "a", "h": 300, "y": 400}]}   # nothing printed: nothing to check
    assert G._values_gate(_doc(quiet)).level == "INFO"


def test_every_bars_record_on_the_page_is_judged() -> None:
    """Round 2 (HIGH 1): a second bars chart on screen (a bars PANEL) rides `bars_more` and is judged like the first."""
    lie = {"base": 500, "tick": [100, 100], "pn": 3, "b": [{"l": "Consumer", "h": 20, "y": 480, "v": "+89%"}]}
    doc = {"aspect": "16:9", "instants": [{"t": 1.0, "why": "x", "page": {"bars": READ_OK, "bars_more": [lie]}}]}
    gate = G._values_gate(doc)
    assert gate.level == "FAIL" and "Consumer prints +89%" in gate.message, gate.message
    doc["instants"][0]["page"]["bars_more"] = [{"ns": "no scale", "pg": "Four gauges", "pn": 2, "b": [{"l": "b", "h": 9, "y": 490, "v": "5"}]}]
    gate = G._values_gate(doc)
    assert gate.level == "FAIL" and "no scale on 'Four gauges' (panel 3)" in gate.message, gate.message


def _hand(scene: str | None, xf: float, t: float = 1.0, si: int = 1) -> dict:
    """An unreadable record mid hand-over INTO state `si` (the page's `xfNow.to`)."""
    return {"t": t, "why": "x", "camera": {"scene": scene} if scene is not None else {},
            "page": {"bars": {"ns": "in hand-over", "pg": "Keyed", "xf": xf, "si": si, "b": [{"l": "Memory", "h": 170, "y": 560, "v": "712.5"}]}}}


def _rest(scene: str | None, si: int | None, t: float = 3.0, **extra) -> dict:
    """A record READ at rest on state `si` (None: a single-state page's record, which names no state)."""
    bars = dict(READ_OK, **({"si": si} if si is not None else {}), **extra)
    return {"t": t, "why": "x", "camera": {"scene": scene} if scene is not None else {}, "page": {"bars": bars}}


def test_a_hand_over_is_named_not_failed_when_the_page_is_read_at_rest() -> None:
    """Round 2 (HIGH 2): unreadable mid hand-over (the page's own xfNow) is named with its clock and excused only if the
    same page is read at rest somewhere in the doc; otherwise it is the unreadable page it looks like."""
    rest = _rest("s01", 1)                                           # the ARRIVING state, read at rest in the same scene
    gate = G._values_gate({"aspect": "16:9", "instants": [_hand("s01", 0.37), rest]})
    assert gate.level == "PASS" and "in hand-over on 'Keyed'" in gate.message and "u 0.37" in gate.message, gate.message
    gate = G._values_gate({"aspect": "16:9", "instants": [_hand("s01", 0.37)]})
    assert gate.level == "FAIL" and "no scale on 'Keyed'" in gate.message, gate.message
    elsewhere = _rest("s09", 1)                                      # read, but on another scene's page
    gate = G._values_gate({"aspect": "16:9", "instants": [_hand("s01", 0.37), elsewhere]})
    assert gate.level == "FAIL" and "no scale on 'Keyed'" in gate.message, gate.message


@pytest.mark.parametrize("rest, why", [
    (_rest("s01", None), "a single-state record read on its painted rules names no state: it excuses nothing"),
    (_rest("s01", 0, sc="declared", pg="Keyed"), "the LEAVING state of the same page, same title: not the arriving one"),
    (_rest("s01", 2), "another state of the page, read at rest"),
])
def test_the_hand_over_excuse_is_never_borrowed(rest: dict, why: str) -> None:
    """Round 3 (the reviewer's abuse cases): the excuse is keyed by (scene, the ARRIVING state's index) - a painted read
    with no state, another state of the same page, or a state read in another scene excuses nothing."""
    gate = G._values_gate({"aspect": "16:9", "instants": [_hand("s01", 0.4), rest]})
    assert gate.level == "FAIL" and "no scale on 'Keyed'" in gate.message, (why, gate.message)


def test_the_hand_over_excuse_needs_a_scene() -> None:
    """Round 3: with no `camera.scene` on either instant, a read at rest would otherwise excuse every hand-over in the doc."""
    gate = G._values_gate({"aspect": "16:9", "instants": [_hand(None, 0.4), _rest(None, 1)]})
    assert gate.level == "FAIL" and "no scale on 'Keyed'" in gate.message, gate.message


def test_a_page_the_probe_cannot_read_fails_by_name_and_never_passes() -> None:
    doc = _doc({"ns": "no scale", "pg": ROW12_TITLE, "b": [{"l": "Capex, next two", "h": 300, "y": 200, "v": "94%"}]})
    fails, read, _worst = G._value_faults(doc)
    assert read == 0 and len(fails) == 1
    assert f"no scale on '{ROW12_TITLE}'" in fails[0] and "94%" in fails[0], fails
    gate = G._values_gate(doc)
    assert gate.level == "FAIL" and f"no scale on '{ROW12_TITLE}'" in gate.message, gate.message


def test_one_unreadable_page_fails_the_row_beside_a_readable_one() -> None:
    doc = _doc(READ_OK, {"ns": "no scale", "pg": "Two clocks", "b": [{"l": "Compute", "h": 90, "y": 400, "v": "20"}]})
    gate = G._values_gate(doc)
    assert gate.level == "FAIL" and "no scale on 'Two clocks'" in gate.message, gate.message


def test_an_unreadable_page_with_nothing_printed_is_nothing_to_check() -> None:
    """The row judges a PRINTED number; a page whose values have not landed yet claims nothing the gate could miss."""
    doc = _doc({"ns": "no scale", "pg": "Two clocks", "b": [{"l": "Compute", "h": 40, "y": 450}]})
    assert G._value_faults(doc)[0] == []
    assert G._values_gate(doc).level == "INFO"


# ---- R26-303: a range reads as its two ends ---------------------------------------------------------------------------
@pytest.mark.parametrize("text, want", [
    ("+55–60%", (55.0, 60.0)), ("55-60%", (55.0, 60.0)), ("-5–-3%", (-5.0, -3.0)), ("$1.2–1.5", (1.2, 1.5)),
    ("-$47.7", (-47.7,)), ("1,405", (1405.0,)), ("36.59%", (36.59,)), ("+89%", (89.0,)), ("94", (94.0,)),
    # round 2 (LOW 6 / 7): the U+2212 sign on a single value; ranges by an explicit separator, each side its own sign
    ("\u22123.2%", (-3.2,)), ("+55 to 60%", (55.0, 60.0)), ("\u221212% to \u22128%", (-12.0, -8.0)),
    ("-12--8%", (-12.0, -8.0)), ("\u221212\u2013\u22128%", (-12.0, -8.0)), ("55\u201460", (55.0, 60.0)),
    ("55%\u201360%", (55.0, 60.0)), ("+55%\u2013+60%", (55.0, 60.0)), ("~55-60", (55.0, 60.0)), ("1.2\u20131.5x", (1.2, 1.5)),
    ("$1,200\u20131,500", (1200.0, 1500.0)), ("-12 to -8", (-12.0, -8.0)), ("2024-25", None),
])
def test_a_printed_number_or_range(text: str, want: tuple) -> None:
    assert G._printed_values(text) == want


@pytest.mark.parametrize("text", ["-$47.7", "1,405", "36.59%", "+89%", "$665", "-66.8", "0.00 %", "2x", "Q3"])
def test_a_single_number_reads_exactly_as_it_always_did(text: str) -> None:
    old = G._printed_number(text)
    got = G._printed_values(text)
    assert (got is None and old is None) or got == (old,), (text, old, got)


def _range_row(h: float, band_top: float | None) -> dict:
    row = {"l": "Conventional", "h": h, "y": 500 - h, "v": "+55–60%"}
    if band_top is not None:
        row["r"] = [band_top, 500 - band_top - h + 6]
    return row


def test_a_range_bar_is_judged_at_both_ends() -> None:
    # 100 on the tick is 400 px: the bar at 55 is 220 px, the band's far end at 60 is 240 px over the zero
    true = {"base": 500, "tick": [100, 100], "b": [_range_row(220, 260)]}
    fails, read, _w = G._value_faults(_doc(true))
    assert fails == [] and read == 1
    far_lie = {"base": 500, "tick": [100, 100], "b": [_range_row(220, 220)]}    # the band runs to 70
    fails = G._value_faults(_doc(far_lie))[0]
    assert len(fails) == 1 and "far end" in fails[0] and "60" in fails[0] and "70.00" in fails[0], fails
    foot_lie = {"base": 500, "tick": [100, 100], "b": [_range_row(160, 260)]}   # the bar stands at 40
    fails = G._value_faults(_doc(foot_lie))[0]
    assert len(fails) == 1 and "prints +55–60%" in fails[0] and "40.00" in fails[0], fails


def test_a_range_printed_over_a_bar_with_no_band_fails() -> None:
    fails = G._value_faults(_doc({"base": 500, "tick": [100, 100], "b": [_range_row(220, None)]}))[0]
    assert len(fails) == 1 and "no band" in fails[0], fails


# ---- R26-319: the width reader ----------------------------------------------------------------------------------------
def test_the_gate_reads_a_width_against_a_horizontal_scale() -> None:
    true = {"dir": "h", "base": 300, "tick": [100, 1100], "b": [{"l": "Capex", "w": 752, "x": 300, "v": "94%"}]}
    fails, read, worst = G._value_faults(_doc(true))
    assert fails == [] and read == 1 and worst[0] < 0.01
    lie = {"dir": "h", "base": 300, "tick": [100, 1100], "b": [{"l": "Capex", "w": 640, "x": 300, "v": "94%"}]}
    fails = G._value_faults(_doc(lie))[0]
    assert len(fails) == 1 and "prints 94% and draws 80.00" in fails[0] and "640 px" in fails[0], fails


def test_gauge_h_is_a_form_setting_now() -> None:
    assert B.page_form_geom("gauge:h", "r") == {"kind": "gauge", "dir": "h"}
    assert B.page_form_geom("gauge", "r") == {"kind": "gauge"}                  # the vertical gauge, to the byte
    with pytest.raises(ValueError) as exc:
        B.page_form_geom("gauge:x", "r")
    assert "takes no setting but :h" in str(exc.value)
    page = world(GAUGE_H)["page"]
    assert page["form"] == {"kind": "gauge", "dir": "h", "ceiling": 100}
    assert LPG.page_ink_key(page) != LPG.page_ink_key(world(GAUGE_V)["page"])   # its plot is not the vertical capsule's


def test_the_object_naming_gauge_h_is_held_to_the_same_rule() -> None:
    obj = json.loads((H_EP / f"evidence/objects/{H_OBJ}.series.json").read_text(encoding="utf-8"))
    assert LPG.validate(dict(obj, form="gauge:h"), "progress") == []
    assert any("takes no setting but :h" in e for e in LPG.validate(dict(obj, form="gauge:x"), "progress"))
    assert any("never names it" in e for e in LPG.validate(dict(obj, form="gauge:h", hlines=[]), "progress"))


def test_the_horizontal_gauge_refuses_the_soft_bar_by_name() -> None:
    with pytest.raises(ValueError) as exc:
        world(GAUGE_H + ";bar_style=soft")
    msg = str(exc.value)
    assert "bar_style=soft and form=gauge:h" in msg and "upright bar" in msg, msg   # the refusal's own words, by name


# ---- R26-264: a card's own badge is never page ink under it -----------------------------------------------------------
def _card_dom(pill_owner: str | None) -> dict:
    pill = {"el": "p1", "name": "pill", "box": [120, 120, 100, 40], "op": 1, "arriving": False, "paper": False}
    item = {"k": "pill", "box": [120, 120, 100, 40], "px": 30, "s": 1, "txt": "SELL"}
    if pill_owner:
        pill["own"] = item["own"] = pill_owner
    return {"docks": [{"el": "d1", "name": "ticket", "box": [100, 100, 400, 300], "op": 1, "arriving": False, "paper": True}, pill],
            "items": [item], "plots": [], "data": [], "labels": []}


def _derive(dom: dict) -> dict:
    return P.derive(dom, 1.0, "x", {}, "16:9", {"ticket": {"slide": "ticket", "place": {"x": 100, "y": 400, "w": 400}}},
                    {"ticket": [100, 100, 400, 300]})


def test_a_cards_own_badge_is_not_page_ink_under_it() -> None:
    inst = _derive(_card_dom("d1"))                   # a pill names its card by the card's ELEMENT (round 2, LOW 9)
    assert not [o for o in inst["overlaps"] if {o["a"], o["b"]} == {"ticket", "pill"}], inst["overlaps"]
    settled = dict(inst, docks=[dict(inst["docks"][0], state="parked", rest=1)])
    assert G._layout_faults({"instants": [settled]})[0] == []


def test_another_cards_badge_under_this_card_is_still_a_fault() -> None:
    inst = _derive(_card_dom("d9"))                    # the pill belongs to ANOTHER card (d9) and lies under this one
    settled = dict(inst, docks=[dict(inst["docks"][0], state="parked", rest=1)])
    fails = G._layout_faults({"instants": [settled]})[0]
    assert fails and "a pill under ticket" in fails[0], fails


def test_twin_cards_are_told_apart_by_their_element() -> None:
    """Two cards may share a slide name: the badge of the second is not the first's own ink."""
    dom = _card_dom("d2")
    dom["docks"].append({"el": "d2", "name": "ticket", "box": [480, 100, 400, 300], "op": 1, "arriving": False, "paper": True})
    pairs = [o for o in _derive(dom)["overlaps"] if {o["a"], o["b"]} == {"ticket", "pill"}]
    assert pairs, "the second card's badge under the first vanished"


def test_a_pill_that_is_not_the_cards_own_is_still_ink_under_it() -> None:
    inst = _derive(_card_dom(None))                    # the PAGE's pill (or another card's) under this card
    settled = dict(inst, docks=[dict(inst["docks"][0], state="parked", rest=1)])
    fails = G._layout_faults({"instants": [settled]})[0]
    assert fails and "a pill under ticket" in fails[0], fails


# ---- the served player ------------------------------------------------------------------------------------------------
def _browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="playwright chromium not installed")


def _on_a_thread(fn):
    """One Playwright loop per thread (test_probe.py's rule): every player here is built, read and closed on its own."""
    import threading
    out: dict = {}

    def run() -> None:
        try:
            out["v"] = fn()
        except BaseException as e:        # noqa: BLE001 - re-raised on the calling thread below
            out["err"] = e

    th = threading.Thread(target=run)
    th.start()
    th.join()
    if "err" in out:
        raise out["err"]
    return out["v"]


def _timeline_for(w: dict) -> tuple[dict, dict]:
    import build_golden_sources as GS
    scenes = [{"scene_id": "s01", "world": dict(w, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, GS.RUNTIME], "docks": [], "species": []}]
    tl = GS._timeline("P72 T6 value gate", scenes, {}, "16:9")
    return tl, dict(GS._base_uris(), **B.longform_assets(tl))


def _probe(tmp: Path, tl: dict, uris: dict, instants, css: str | None = None, read_js: str | None = None):
    """Serve one timeline, probe it at `instants` (the gate's own reader) and return (doc, read_js's value at REST_T)."""
    def run():
        RB.write_split(tmp, tl, uris, "t6.timeline.json")
        p = P.Probe(tmp, "t6.timeline.json")
        try:
            if css:
                p.page.add_style_tag(content=css)
            doc = P.probe_doc(p.build, "t6.timeline.json", p, instants)
            extra = None
            if read_js:
                p.seek(REST_T)
                extra = p.page.evaluate(read_js)
            return doc, extra, list(p.errs)
        finally:
            p.close()
    return _on_a_thread(run)


def _row12(mutate=None) -> tuple[dict, dict]:
    w = world(ROW12)
    if mutate:
        mutate(w["page"])
    return _timeline_for(w)


@pytest.fixture(scope="module")
def row12(tmp_path_factory):
    tl, uris = _row12()
    return _probe(tmp_path_factory.mktemp("row12"), tl, uris, BUILD)


@needs_browser
def test_row12_the_long_form_bars_page_is_read_against_its_own_scale_and_passes(row12) -> None:
    doc, _x, errs = row12
    assert errs == []
    fails, read, worst = G._value_faults(doc)
    landed = [i for i in doc["instants"] if any(b.get("v") for b in ((i.get("page") or {}).get("bars") or {}).get("b") or [])]
    assert fails == [] and read == len(landed) >= 10, (fails, read, len(landed))
    assert worst[0] < 0.01
    bars = landed[-1]["page"]["bars"]
    assert "ns" not in bars and bars["tick"][0] == 100, bars                  # the top printed tick, 100%, at its own line
    assert G._values_gate(doc).level == "PASS", G._values_gate(doc).message


@needs_browser
def test_row12_a_planted_wrong_height_fails(tmp_path: Path) -> None:
    def plant(page: dict) -> None:
        page["values"] = [80.0]                        # drawn at 80, printed "94" (value_strings untouched)
    tl, uris = _row12(plant)
    doc, _x, _e = _probe(tmp_path, tl, uris, [(REST_T, "hold")])
    gate = G._values_gate(doc)
    assert gate.level == "FAIL" and "prints 94% and draws 80" in gate.message, gate.message


@needs_browser
def test_a_long_form_page_whose_scale_is_not_printed_fails_no_scale_by_name(tmp_path: Path) -> None:
    tl, uris = _row12()
    hide = '.lp-chart text.lab[text-anchor="end"] { display: none !important; }'   # every y tick label, unprinted
    doc, _x, _e = _probe(tmp_path, tl, uris, [(REST_T, "hold")], css=hide)
    gate = G._values_gate(doc)
    assert gate.level == "FAIL" and f"no scale on '{ROW12_TITLE}'" in gate.message, gate.message


@needs_browser
def test_the_range_page_is_read_at_both_ends_through_the_probe(tmp_path: Path) -> None:
    import build_golden_sources as GS
    tl, uris = GS.bars_range()
    doc, _x, _e = _probe(tmp_path, tl, uris, [(REST_T, "hold")])
    rows = doc["instants"][0]["page"]["bars"]["b"]
    rng = [r for r in rows if "–" in str(r.get("v"))]
    assert len(rng) == 1 and rng[0].get("r"), rows                            # the band's box rides its bar's row
    gate = G._values_gate(doc)
    assert gate.level == "PASS", gate.message


GAUGE_READ = r"""() => {
  const w = document.getElementById('wB'); const S = w && w.__lp; if (!S || !S.gauge) return null;
  const g = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect(); return [r.x - g.x, r.y - g.y, r.width, r.height]; };
  return { caps: S.gauge.caps.map((c) => R(c.track)), bars: S.bars.map((b) => ({ box: R(b.bar), val: b.val.textContent, vbox: R(b.val),
           vfill: getComputedStyle(b.val).fill, lab: R(b.lab) })), dir: S.scale.dir || null,
           names: [...S.chart.querySelectorAll('text.sname')].map((t) => ({ text: t.textContent, box: R(t) })),
           ticks: [...S.chart.querySelectorAll('text.lab')].filter((t) => t.textContent.endsWith('%')).map((t) => ({ text: t.textContent, box: R(t) })) };
}"""


@pytest.fixture(scope="module")
def gauge_h(tmp_path_factory):
    tl, uris = _timeline_for(world(GAUGE_H))
    return _probe(tmp_path_factory.mktemp("gauge-h"), tl, uris, BUILD, read_js=GAUGE_READ)


@needs_browser
def test_gauge_h_draws_one_horizontal_capsule_whose_fill_is_its_width(gauge_h) -> None:
    _doc, d, errs = gauge_h
    assert errs == [] and d and d["dir"] == "h"
    (cx, cy, cw, ch), = d["caps"]
    assert cw > 2.5 * ch                                                      # horizontal
    bx, by, bw, bh = d["bars"][0]["box"]
    assert abs(bx - cx) < 1.0 and abs(bw / cw - 0.94) < 0.004                 # from zero at the left, 94 of the whole
    assert abs(by - cy) < 1.0 and abs(bh - ch) < 1.0


@needs_browser
def test_gauge_h_writes_its_figure_the_whole_and_the_scale_clear_of_the_capsule(gauge_h) -> None:
    _doc, d, _e = gauge_h
    (cx, cy, cw, ch), = d["caps"]
    b = d["bars"][0]
    assert b["val"] == "94%" and b["vfill"] == "rgb(255, 138, 76)"            # value_strings verbatim, in the bar's ink
    vx, vy, vw, vh = b["vbox"]
    assert vy >= cy + ch and abs((vx + vw / 2) - (cx + 0.94 * cw)) < 2.0      # under the capsule, centred on the fill's end
    name = next(n for n in d["names"] if n["text"] == "every dollar from operations")
    nx, ny, nw, nh = name["box"]
    assert nx >= cx + cw and ny < cy + ch / 2 < ny + nh                       # the whole names itself past the ceiling
    ticks = {t["text"]: t["box"] for t in d["ticks"]}
    for text, share in (("0%", 0.0), ("100%", 1.0)):
        tx, ty, tw, th = ticks[text]
        assert ty + th <= cy and abs((tx + tw / 2) - (cx + share * cw)) < 2.0   # the printed scale over its stubs
    lx, ly, lw, lh = b["lab"]
    assert lx + lw <= cx                                                      # the category names the capsule from its left


@needs_browser
def test_m26_reads_the_horizontal_gauge_at_every_instant(gauge_h) -> None:
    doc, _d, _e = gauge_h
    fails, read, worst = G._value_faults(doc)
    landed = [i for i in doc["instants"] if any(b.get("v") for b in ((i.get("page") or {}).get("bars") or {}).get("b") or [])]
    assert fails == [] and read == len(landed) >= 10, (fails, read, len(landed))
    assert landed[-1]["page"]["bars"]["dir"] == "h" and worst[0] < 0.01
    assert G._values_gate(doc).level == "PASS", G._values_gate(doc).message


@needs_browser
def test_m26_fails_a_horizontal_gauge_that_prints_a_number_its_fill_does_not_carry(tmp_path: Path) -> None:
    w = world(GAUGE_H)
    w["page"]["value_strings"] = ["80"]
    tl, uris = _timeline_for(w)
    doc, _d, _e = _probe(tmp_path, tl, uris, [(REST_T, "hold")])
    gate = G._values_gate(doc)
    assert gate.level == "FAIL" and "prints 80%" in gate.message, gate.message


@needs_browser
def test_the_vertical_gauge_still_reads_on_its_own_rules(tmp_path: Path) -> None:
    """The old path first: a page whose tick labels stand on visible rules is read exactly as it always was - no map
    marker, no width, the same numbers (the committed probes do not move)."""
    tl, uris = _timeline_for(world(GAUGE_V))
    doc, _d, _e = _probe(tmp_path, tl, uris, [(REST_T, "hold")])
    bars = doc["instants"][0]["page"]["bars"]
    assert set(bars) == {"base", "tick", "b"} and set(bars["b"][0]) == {"l", "h", "y", "v"}, bars
    assert G._values_gate(doc).level == "PASS"


DOCK_PAGE = """<!doctype html><html><body style="margin:0">
<div id="stage" style="position:absolute;left:0;top:0;width:1920px;height:1080px">
  <div class="dock" id="d1" data-slide="ticket" style="position:absolute;left:100px;top:100px;width:400px;height:300px;background:#eee">
    <span class="pill" style="position:absolute;left:20px;top:20px;width:100px;height:40px;font-size:30px">SELL</span>
  </div>
</div></body></html>"""


@needs_browser
def test_the_probe_names_the_card_a_badge_belongs_to() -> None:
    def run():
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            try:
                pg = br.new_context(viewport={"width": 1920, "height": 1080}).new_page()
                pg.set_content(DOCK_PAGE)
                return pg.evaluate(P.READ_DOM)
            finally:
                br.close()
    dom = _on_a_thread(run)
    pills = [d for d in dom["docks"] if d["name"] == "pill"]
    assert pills and pills[0].get("own") == "d1", dom["docks"]
    assert [i.get("own") for i in dom["items"] if i["k"] == "pill"] == ["d1"]
    inst = _derive(copy.deepcopy(dom))
    assert not [o for o in inst["overlaps"] if {o["a"], o["b"]} == {"ticket", "pill"}], inst["overlaps"]


@needs_browser
def test_gauge_h_composes_with_the_long_form(tmp_path: Path) -> None:
    """H row 12's own options on the lying capsule: the long form's sheet (which paints no gridline) - M26 still reads it."""
    tl, uris = _timeline_for(world(GAUGE_H + ";idle=live;readability=longform"))
    doc, d, errs = _probe(tmp_path, tl, uris, [(REST_T, "hold")], read_js=GAUGE_READ)
    assert errs == [] and d["dir"] == "h"
    (cx, _cy, cw, _ch), = d["caps"]
    assert abs(d["bars"][0]["box"][2] / cw - 0.94) < 0.004
    assert G._values_gate(doc).level == "PASS", G._values_gate(doc).message


TWO = {"title": "Two shares of two wholes", "sub": "fixture", "src": "golden fixture", "unit": "%", "domain": [0, 100],
       "hlines": [{"y": 100, "label": "the whole", "color": "deemph"}],
       "bars": [{"label": "Part", "value": 60, "color": "teal"}, {"label": "Other", "value": 25, "color": "crimson"}]}


@needs_browser
def test_gauge_h_with_two_bars_lays_one_capsule_each_and_no_word_meets_a_capsule(tmp_path: Path) -> None:
    ep = tmp_path / "ep"
    (ep / "evidence/objects").mkdir(parents=True)
    (ep / "evidence/objects/g-two.series.json").write_text(json.dumps(TWO), encoding="utf-8")
    tl, uris = _timeline_for(world("ledger:g-two:progress;form=gauge:h", ep))
    doc, d, _e = _probe(tmp_path / "b", tl, uris, [(REST_T, "hold")], read_js=GAUGE_READ)
    assert len(d["caps"]) == 2
    for b, share, cap in zip(d["bars"], (0.60, 0.25), d["caps"]):
        assert abs(b["box"][2] / cap[2] - share) < 0.004
    meets = lambda a, c: not (a[0] + a[2] <= c[0] or a[0] >= c[0] + c[2] or a[1] + a[3] <= c[1] or a[1] >= c[1] + c[3])  # noqa: E731
    words = [b["vbox"] for b in d["bars"]] + [b["lab"] for b in d["bars"]] + [n["box"] for n in d["names"]] + [t["box"] for t in d["ticks"]]
    for w in words:
        for c in d["caps"]:
            assert not meets(w, c), (w, c)
    assert G._values_gate(doc).level == "PASS", G._values_gate(doc).message


# ---- round 2: the served player -----------------------------------------------------------------------------------------
def _surface(name: str, ts, mutate=None, css: str | None = None):
    import tempfile
    tl, uris, _t, _a = RB.load_surface(name)
    if mutate:
        tl = mutate(copy.deepcopy(tl))
    return _probe(Path(tempfile.mkdtemp()), tl, uris, [(t, name) for t in ts], css=css)


def _panel_lie(tl: dict) -> dict:
    for sc in tl["scenes"]:
        for p_ in ((sc.get("world") or {}).get("page") or {}).get("panels") or []:
            if p_.get("builder") == "bars" and len(p_.get("value_strings") or []) == 3:
                p_["value_strings"] = ["+5", "+6", "+9"]
    return tl


@needs_browser
def test_a_bars_panel_is_read_and_a_planted_panel_fails() -> None:
    """HIGH 1: panels-mixed-grow's two BARS panels (the wafer ratio and the contract prices, a range among them) are read,
    each by name, at 16.8 (all four built, before the grow); the same page with the contract panel printing +5 / +6 / +9
    over its +55-60 / +60 / +89 bars FAILs, naming the panel. (At 17.6 the contract panel has receded: its values are not
    fully printed, so there is nothing of it to judge - the grown wafer panel is read there.)"""
    doc, _x, _e = _surface("panels-mixed-grow", [16.8])
    page = doc["instants"][0]["page"]
    recs = [page.get("bars")] + list(page.get("bars_more") or [])
    panels = [r for r in recs if r and r.get("pn") is not None]
    assert len(panels) == 2 and all("ns" not in r for r in panels), recs
    assert G._values_gate(doc).level == "PASS", G._values_gate(doc).message
    doc, _x, _e = _surface("panels-mixed-grow", [16.8, 17.6], mutate=_panel_lie)
    gate = G._values_gate(doc)
    assert gate.level == "FAIL" and "panel 4: Conventional D prints +5%" in gate.message, gate.message
    grown = doc["instants"][1]["page"]
    assert any(r.get("pn") == 1 and "ns" not in r for r in [grown.get("bars"), *(grown.get("bars_more") or [])]), grown


@needs_browser
def test_the_keyed_recast_is_named_mid_hand_over_and_read_at_rest() -> None:
    """HIGH 2: ledger-keyed at 12.75 (u 0.37 of the keyed recast: the values in flight, no printed tick on a rule) is
    `in hand-over` with its clock, at 14.5 the bars page is read - and the row names the first and does not fail it."""
    doc, _x, _e = _surface("ledger-keyed", [12.75, 14.5])
    mid, rest = ((i["page"].get("bars") or {}) for i in doc["instants"])
    assert mid.get("ns") == "in hand-over" and 0 < mid.get("xf", 0) < 1 and mid.get("si") == 1, mid
    assert "ns" not in rest and rest.get("b") and rest.get("si") == 1, rest    # the arriving state, read at rest
    gate = G._values_gate(doc)
    assert gate.level == "PASS" and "in hand-over" in gate.message, gate.message


@needs_browser
def test_a_hidden_zero_line_is_never_read_as_the_zero(tmp_path: Path) -> None:
    """MEDIUM 3: the flat bars page with its zero line hidden - the painted path used the empty box of the hidden rule as
    the zero; it now reads the declared rules, and the page reads true."""
    tl, uris = _timeline_for(world(f"ledger:{H_OBJ}:bars::right"))
    doc, _x, _e = _probe(tmp_path, tl, uris, [(REST_T, "hold")], css=".lp-chart line.ax { display: none !important; }")
    bars = doc["instants"][0]["page"]["bars"]
    assert bars.get("sc") == "declared", bars
    assert G._values_gate(doc).level == "PASS", G._values_gate(doc).message


# ---- round 2 (INFO 10): what reads the page's y scale is refused by name on the lying capsule --------------------------
GAUGE_H_READERS = [
    {"kind": "chart_to", "at": 5.0, "to": "rescale"}, {"kind": "bracket", "at": 5.0}, {"kind": "figure", "at": 5.0, "target": {"kind": "datum", "i": 0}},
    {"kind": "ring", "at": 5.0, "target": {"kind": "datum", "i": 0}}, {"kind": "callout", "at": 5.0, "target": {"kind": "datum", "i": 0}},
    {"kind": "build_to", "at": 5.0, "target": {"kind": "datum", "i": 0}}, {"kind": "level_join", "at": 5.0},
]


@pytest.mark.parametrize("sp", GAUGE_H_READERS, ids=lambda sp: sp["kind"])
def test_gauge_h_refuses_a_species_that_reads_the_page_scale_by_name(sp: dict) -> None:
    """`st.scale.my` on a horizontal gauge is the TURNED frame's y, and a mark's geometry is laid out along x: a species
    that anchors on the page's data (a datum target, a bracket, a figure, a rescale / recast, a join) would draw at the
    wrong place - refused by name, never drawn wrong. The vertical gauge is untouched."""
    with pytest.raises(ValueError) as exc:
        B.check_gauge_h(world(GAUGE_H), [dict(sp)])
    assert "form=gauge:h" in str(exc.value) and repr(sp["kind"]) in str(exc.value), str(exc.value)
    B.check_gauge_h(world(GAUGE_V), [dict(sp)])                              # the vertical gauge: no refusal here


def test_gauge_h_keeps_a_species_that_does_not_read_the_scale_and_refuses_a_later_state() -> None:
    B.check_gauge_h(world(GAUGE_H), [{"kind": "spotlight", "at": 5.0, "target": {"kind": "region", "x": 0.1, "y": 0.1, "w": 0.2, "h": 0.2}},
                                     {"kind": "retitle", "at": 6.0, "text": "x"}])
    w = world(GAUGE_H)
    w["page_states"] = [copy.deepcopy(w["page"])]                            # what `then=` compiles to
    with pytest.raises(ValueError) as exc:
        B.check_gauge_h(w, [])
    assert "form=gauge:h" in str(exc.value) and "then=" in str(exc.value), str(exc.value)


def test_the_compiler_calls_the_gauge_h_check_on_the_row() -> None:
    with pytest.raises(ValueError) as exc:
        B.derive_rescale_states(world(GAUGE_H), [{"kind": "ring", "at": 5.0, "target": {"kind": "datum", "i": 0}}], GAUGE_H, H_EP)
    assert "form=gauge:h" in str(exc.value)


@needs_browser
def test_a_page_under_the_dips_full_veil_prints_nothing_to_fail(tmp_path: Path) -> None:
    """Round 2 (found on the H door at 11:56.79, row 24's first frame): the dip's veil (#dipveil) stands over the page at
    full black, and the DOM still holds the panel's values at full opacity with its ticks not yet up - the viewer reads
    nothing there, so an unreadable page under the veil has printed nothing and is nothing to fail."""
    tl, uris = _row12()
    veiled = ('.lp-chart text.lab[text-anchor="end"] { display: none !important; }'
              '#dipveil { display: block !important; opacity: 1 !important; }')
    doc, _x, _e = _probe(tmp_path, tl, uris, [(REST_T, "hold")], css=veiled)
    bars = doc["instants"][0]["page"]["bars"]
    assert bars.get("ns") and not any(b.get("v") for b in bars["b"]), bars
    assert G._values_gate(doc).level == "INFO", G._values_gate(doc).message



# ---- round 3: the veil counts only when it covers the page --------------------------------------------------------------
@needs_browser
@pytest.mark.parametrize("veil, level", [(0.02, "FAIL"), (0.5, "FAIL"), (1.0, "INFO")])
def test_a_part_veil_never_hides_an_unreadable_page(tmp_path: Path, veil: float, level: str) -> None:
    """Round 3 (the reviewer's HIGH): partway through a dip the page is still printed - a no-scale page with "94%" on it
    under a veil at 0.02 or 0.5 FAILs by name; only a veil that COVERS the page (>= 0.95, the on-screen cut) prints
    nothing, and nothing is to check."""
    tl, uris = _row12()
    css = ('.lp-chart text.lab[text-anchor="end"] { display: none !important; }'
           f'#dipveil {{ display: block !important; opacity: {veil} !important; }}')
    doc, _x, _e = _probe(tmp_path, tl, uris, [(REST_T, "hold")], css=css)
    gate = G._values_gate(doc)
    assert gate.level == level, (veil, gate.message)
    if level == "FAIL":
        assert f"no scale on '{ROW12_TITLE}'" in gate.message and "94%" in gate.message, gate.message
