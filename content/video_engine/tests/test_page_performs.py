"""P47 T2 - BUILD-ON: the page performs on a word (operator 2026-09-06: "we're being a bit too lazy with the world plates ...
perform some transformations on the chart"; SHOT-TABLE-V3-PROPOSAL part B).

Four PAGE species on the ledger clock, authored in the scene's species list: build_to caps the drawn series at a datum (the
build beat is spent on the first cap, each later cap draws on its own word), bracket spans two data beside them with a
written label, retitle erases the title glyph by glyph and writes the new one, relight re-fires a bracket in the sunflower.

Static and compiler checks always run; the browser proof (through render_baseline's harness and the template's read-only
__lpProbe) needs playwright + chromium and is skipped without them.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import render_baseline as RB  # noqa: E402

LEDGER = "ledger:x:line"
BUILD_START, BUILD_S = 4.4, 3.0        # LP: ROLL .7 + SAVOR .8 + FIELD 2.4 + PUNCH .5 -> the build runs 4.4-7.4 s on a page entered at 0
T_CAP2, CAP2_S = 12.0, 1.5
T_BRACKET, BRACKET_S = 15.0, 2.0
T_RETITLE, RETITLE_S = 19.0, 2.0
T_RELIGHT, RELIGHT_S = 22.0, 1.0
T_UNDRAW, UNDRAW_S = 23.2, 1.2         # E50: the line unwinds to nothing on a word
T_FIGURE, FIGURE_S = 24.5, 1.2         # ... and the figure the sentence turns to writes at the peak's spot
T_REDRAW, REDRAW_S = 25.8, 1.0         # P47 T9: then the TAIL redraws - the months the sentence is about - while the history stays un-drawn (all before the golden's own retract at 27.5)


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---- the compiler grammar ------------------------------------------------------------------------


def test_the_four_page_species_are_kinds_and_take_their_own_fields():
    for k in ("build_to", "bracket", "retitle", "relight", "undraw", "figure", "note"):
        assert k in B.SPECIES_KINDS and k in B.PAGE_SPECIES
    assert B.SPECIES_TARGETS["note"] == ()
    assert B.SPECIES_TARGETS["build_to"] == ("datum",) and B.SPECIES_TARGETS["undraw"] == ("datum",) and B.SPECIES_TARGETS["figure"] == ("datum",)
    ok = [{"kind": "build_to", "at": 4.4, "dur": 3.0, "target": {"kind": "datum", "index": 5}},
          {"kind": "bracket", "at": 15.0, "dur": 2.0, "from": 5, "to": 9, "label": "-$122.6B", "sub": "a tenth of the pile", "color": "neg"},
          {"kind": "retitle", "at": 19.0, "dur": 2.0, "text": "The opponent: a balance sheet"},
          {"kind": "relight", "at": 22.0, "dur": 1.0, "ref": "bracket", "index": 0},
          {"kind": "undraw", "at": 24.0, "dur": 1.5, "target": {"kind": "datum", "index": 0}},
          {"kind": "figure", "at": 25.5, "dur": 1.5, "target": {"kind": "datum", "index": 5}, "text": "$1,239.3B", "sub": "February 2026", "dy": -0.5},
          {"kind": "note", "at": 26.0, "dur": 1.2, "text": "Japan started selling in February."},
          {"kind": "build_to", "at": 27.0, "dur": 1.2, "target": {"kind": "datum", "index": 9}, "paths": "tail"}]
    assert B.validate_species(ok, (0.0, 0, 0), LEDGER) == []


@pytest.mark.parametrize("entry, needle", [
    ({"kind": "build_to", "at": 1.0, "dur": 1.0}, "no declared target"),
    ({"kind": "build_to", "at": 1.0, "dur": 1.0, "target": {"kind": "point", "x": 0.5, "y": 0.5}}, "not allowed"),
    ({"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 2, "label": "x"}, "'to' must be"),
    ({"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 2, "to": 4, "label": " "}, "non-empty string label"),
    ({"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 2, "to": 4, "label": "x", "color": "pink"}, "color must be one of"),
    ({"kind": "retitle", "at": 1.0, "dur": 1.0}, "non-empty string text"),
    ({"kind": "relight", "at": 1.0, "dur": 1.0, "ref": "dock"}, "ref must be one of"),
    ({"kind": "relight", "at": 1.0, "dur": 1.0, "ref": "bracket", "index": -1}, "index must be"),
    ({"kind": "undraw", "at": 1.0, "dur": 1.0}, "no declared target"),
    ({"kind": "figure", "at": 1.0, "dur": 1.0, "target": {"kind": "datum", "index": 2}}, "non-empty string text"),
    ({"kind": "figure", "at": 1.0, "dur": 1.0, "target": {"kind": "datum", "index": 2}, "text": "$1B", "dy": "up"}, "dy must be a number"),
    ({"kind": "note", "at": 1.0, "dur": 1.0}, "non-empty string text"),
    ({"kind": "undraw", "at": 1.0, "dur": 1.0, "target": {"kind": "datum", "index": 0}, "paths": "everything"}, "paths must be one of"),
])
def test_a_page_species_missing_its_field_is_a_build_error_naming_the_field(entry, needle):
    errs = B.validate_species([entry], (0.0, 0, 0), LEDGER)
    assert errs and any(needle in e for e in errs), errs


def test_a_page_species_on_a_plain_plate_is_refused():
    errs = B.validate_species([{"kind": "retitle", "at": 1.0, "dur": 1.0, "text": "x"}], (0.0, 0, 0), "plate-07")
    assert errs and "page species" in errs[0] and "ledger" in errs[0]


# ---- the gate --------------------------------------------------------------------------------------


def _scene(species):
    return {"scene_id": "s01", "span": [0.0, 30.0], "world": {"kind": "ledger", "page": {"title": "t", "series": [{"pts": [[0, 1], [1, 2]]}]}},
            "species": species}


def test_the_gate_credits_each_page_species_and_lists_the_build_to_holds():
    sp = [{"kind": "build_to", "at": 4.4, "dur": 3.0, "target": {"kind": "datum", "index": 3}},
          {"kind": "build_to", "at": 12.0, "dur": 1.5, "target": {"kind": "datum", "index": 9}},
          {"kind": "bracket", "at": 15.0, "dur": 2.0, "from": 3, "to": 9, "label": "x"},
          {"kind": "retitle", "at": 19.0, "dur": 2.0, "text": "y"},
          {"kind": "relight", "at": 22.0, "dur": 1.0, "ref": "bracket"}]
    ev = G._species_events([_scene(sp)])
    for t in (4.4, 7.4, 12.0, 13.5, 15.0, 17.0, 19.0, 21.0, 22.0):
        assert t in ev, (t, ev)
    assert 23.0 not in ev, "a relight is one flash, not a span"
    assert G._build_to_holds([_scene(sp)]) == [(7.4, 4.6)]
    gate = G._build_to_gate([_scene(sp)])
    assert gate.id == "M19" and gate.level == "INFO" and "0:07+4.6s" in gate.message
    assert G._build_to_gate([_scene([])]) is None, "no build_to, no row - the note exists only when the cap does"


def test_m21_the_deployed_life_runs_from_the_last_data_mark_to_the_exit_or_the_undraw():
    """E50: the clock starts when the last data point lands; annotations do not restart it; an undraw ends it."""
    caps = [{"kind": "build_to", "at": 4.4, "dur": 3.0, "target": {"kind": "datum", "index": 3}},
            {"kind": "build_to", "at": 12.0, "dur": 1.5, "target": {"kind": "datum", "index": 9}}]
    ann = [{"kind": "retitle", "at": 19.0, "dur": 2.0, "text": "y"}, {"kind": "relight", "at": 22.0, "dur": 1.0, "ref": "title"},
           {"kind": "spotlight", "at": 20.0, "dur": 2.0, "target": {"kind": "datum", "index": 9}}]
    lives = G._deployed_lives([_scene(caps + ann)])
    assert lives == [("s01", 13.5, 30.0, 16.5)], lives
    g = G._deployed_gate([_scene(caps + ann)])
    assert g.id == "M21" and g.level == "WARN" and "16.5s" in g.message and "undraw" in g.message
    und = [{"kind": "undraw", "at": 18.0, "dur": 1.2, "target": {"kind": "datum", "index": 0}},
           {"kind": "figure", "at": 19.5, "dur": 1.5, "target": {"kind": "datum", "index": 3}, "text": "$1B"}]
    assert G._deployed_lives([_scene(caps + und)]) == [("s01", 13.5, 18.0, 4.5)], "the undraw ends the life; the figure is the next thing, not a data mark"
    assert G._deployed_gate([_scene(caps + und)]).level == "PASS"
    long = [dict(caps[1], at=8.0), {"kind": "bracket", "at": 10.0, "dur": 2.0, "from": 3, "to": 9, "label": "x"}]
    lives = G._deployed_lives([_scene([caps[0]] + long)])
    assert lives[0][1] == 12.0 and lives[0][3] == 18.0, "the bracket's label is a data mark"
    sc = _scene(caps); sc["span"] = [0.0, 22.0]
    assert G._deployed_gate([sc]).level == "INFO", "8-12 s is the ceiling a dock's clip may use"
    assert G._deployed_gate([{"scene_id": "p", "span": [0.0, 30.0], "world": {"kind": "clip"}, "species": []}]) is None, "ledger pages only"
    ev = G._species_events([_scene(und)])
    assert 18.0 in ev and 19.2 in ev and 19.5 in ev and 21.0 in ev, "an undraw and a figure are events at both ends"


def test_m22_a_push_is_tied_to_a_landing_or_it_is_filler():
    """E51 (the third watch): the 1:14 push on the Meta page zoomed on a bar that landed five seconds earlier - filler."""
    cap = {"kind": "build_to", "at": 4.4, "dur": 3.0, "target": {"kind": "datum", "index": 3}}
    tied = {"kind": "punch", "at": 7.6, "dur": 0.9, "target": {"kind": "datum", "index": 3}}        # 0.2 s after the cap lands
    late = {"kind": "punch", "at": 12.4, "dur": 0.9, "target": {"kind": "datum", "index": 3}}       # 5 s after anything landed
    assert G._untied_pushes([_scene([cap, tied])]) == []
    assert G._untied_pushes([_scene([cap, late])]) == [("s01", "punch", 12.4)]
    g = G._push_tie_gate([_scene([cap, late])])
    assert g.id == "M22" and g.level == "WARN" and "0:12" in g.message
    assert G._push_tie_gate([_scene([cap])]) is None, "no push, no row"
    sc = _scene([late]); sc["docks"] = [{"slide": "dock-x", "enter": 11.9, "exit": 20.0, "arrive": "throw"}]
    assert G._untied_pushes([sc]) == [], "a card's contact (enter + 0.46 on a throw) is a landing the push may ride"
    br = {"kind": "bracket", "at": 10.0, "dur": 2.0, "from": 3, "to": 9, "label": "x"}
    assert G._untied_pushes([_scene([cap, br, late])]) == [], "the bracket's label landing at 12.0 ties the push at 12.4"
    sp = _scene([]); sp["world"]["page"]["enter"] = "snap"
    assert G._page_land_offset(sp) == 0.0 and G._deployed_lives([sp])[0][1] == 0.0, "a snapped page arrives built: its mark is its entry"


# ---- the browser ----------------------------------------------------------------------------------


def _line_golden() -> tuple[str, dict, dict, str, list]:
    """The first golden whose page is a drawn line with enough data to cap."""
    for name in ("ledger-soak-page", "ledger-page-mid-build", "chart-callout"):
        try:
            tl, uris, _t, aspect = RB.load_surface(name)
        except FileNotFoundError:
            continue
        pg = tl["scenes"][0]["world"].get("page") or {}
        pts = ((pg.get("series") or [{}])[0].get("pts") or [])
        if len(pts) >= 6:
            return name, tl, uris, aspect, pts
    pytest.skip("no golden carries a drawn line")


def _authored(tl: dict, pts: list) -> tuple[dict, int, int]:
    vals = [float(v) for _x, v in pts]
    peak, last = max(range(len(vals)), key=lambda i: vals[i]), len(vals) - 1
    if peak == last:
        peak = max(1, last // 2)
    sc = tl["scenes"][0]
    species = [
        {"kind": "build_to", "at": BUILD_START, "dur": BUILD_S, "target": {"kind": "datum", "index": peak}},
        {"kind": "build_to", "at": T_CAP2, "dur": CAP2_S, "target": {"kind": "datum", "index": last}},
        {"kind": "bracket", "at": T_BRACKET, "dur": BRACKET_S, "from": peak, "to": last, "label": "-$122.6B", "sub": "a tenth of the pile", "color": "neg"},
        {"kind": "retitle", "at": T_RETITLE, "dur": RETITLE_S, "text": "The opponent: a balance sheet"},
        {"kind": "relight", "at": T_RELIGHT, "dur": RELIGHT_S, "ref": "bracket", "index": 0},
        {"kind": "undraw", "at": T_UNDRAW, "dur": UNDRAW_S, "target": {"kind": "datum", "index": 0}},
        {"kind": "figure", "at": T_FIGURE, "dur": FIGURE_S, "target": {"kind": "datum", "index": peak}, "text": "$1,239.3B", "sub": "February 2026"},
        {"kind": "build_to", "at": T_REDRAW, "dur": REDRAW_S, "target": {"kind": "datum", "index": last}, "paths": "tail"},
    ]
    pg0 = sc["world"]["page"]
    page = dict(pg0, series=pg0["series"][:1], axes=dict(pg0.get("axes") or {}, highlight_from=pts[peak][0]))   # ONE series with a highlighted TAIL from the peak (k0 > 0), as the holdings page has - the split is single-series only
    scenes = [dict(sc, species=species, world=dict(sc["world"], page=page, ken_burns={"scale": 0, "x": 0, "y": 0}))]
    return dict(tl, scenes=scenes, caption_pages=[], captions=[], kinetics={"min_jerk": True, "analytic_spring": True}), peak, last


class _Player:
    def __init__(self, tl: dict, uris: dict, aspect: str):
        from playwright.sync_api import sync_playwright
        self.td = tempfile.TemporaryDirectory()
        html = Path(self.td.name) / "perform.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.w, self.h = RB.STAGE[aspect]
        self.srv, port = RB.serve(html.parent)
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)
        self.page = self.browser.new_context(viewport={"width": self.w, "height": self.h}).new_page()
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, self.w, self.h)

    def probe(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate("() => window.__lpProbe()")

    def close(self):
        self.browser.close(); self.pw.stop(); self.srv.shutdown(); self.td.cleanup()


def _poly_frac(pts: list, i: int) -> float:
    L = lambda k: sum(math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]) for j in range(1, k + 1))
    tot = L(len(pts) - 1)
    return L(i) / tot if tot else 1.0


@needs_browser
def test_build_to_caps_the_line_at_the_datum_and_the_next_word_draws_the_rest():
    name, tl, uris, aspect, pts = _line_golden()
    tl2, peak, last = _authored(tl, pts)
    P = _Player(tl2, uris, aspect)
    try:
        def line(pr):
            return [p for p in pr["paths"] if p["si"] == 0 and not p["muted"]][0]
        a = line(P.probe(9.0))
        i = max(0, min(len(a["pts"]) - 1, peak - a["k0"]))
        want = _poly_frac(a["pts"], i)
        assert abs(a["frac"] - want) < 0.01, f"at 9.0 s the line is capped at the peak: drawn {a['frac']:.3f}, cap {want:.3f}"
        assert abs(a["tip"][0] - a["pts"][i][0]) <= 2.0, "the series' last drawn x is the datum's x (+-2 px)"
        b = line(P.probe(11.9))
        assert abs(b["frac"] - a["frac"]) < 1e-6, "the cap HOLDS until the next word"
        c = line(P.probe(T_CAP2 + CAP2_S / 2))
        assert want + 0.02 < c["frac"] < 0.98, f"mid-word the rest is drawing: {c['frac']:.3f}"
        d = line(P.probe(T_CAP2 + CAP2_S + 0.2))
        assert d["frac"] >= 0.995, "the whole line lands on the next word"
    finally:
        P.close()


@needs_browser
def test_the_bracket_draws_beside_the_two_data_and_writes_its_label_by_glyph():
    name, tl, uris, aspect, pts = _line_golden()
    tl2, peak, last = _authored(tl, pts)
    P = _Player(tl2, uris, aspect)
    try:
        before = P.probe(T_BRACKET - 0.1)["brackets"][0]
        assert before["opacity"] == 0, "nothing before its word"
        mid = P.probe(T_BRACKET + 0.4)["brackets"][0]
        assert mid["opacity"] == 1 and 0 < mid["offset"] < mid["len"], "the span is being drawn by the hand"
        assert all(o == 0 for o in mid["label"]), "the label waits for the span"
        done = P.probe(T_BRACKET + BRACKET_S)["brackets"][0]
        assert done["offset"] < 0.5 and all(o >= 0.999 for o in done["label"]), "span drawn, label written"
        x, y, w, h = done["bbox"]
        y0, y1 = min(done["A"][1], done["B"][1]), max(done["A"][1], done["B"][1])
        assert done["y0"] == y0 and done["y1"] == y1, "the span is exactly the two data's y"
        ax, bx = done["A"][0], done["B"][0]
        assert done["x"] >= max(ax, bx) + 10, f"the span stands to the RIGHT of both data: x {done['x']:.1f} vs data {max(ax, bx):.1f}"
        if done["fits"]:
            assert x >= max(ax, bx) + 10, "room beside: the whole bracket, label included, sits right of the data"
        else:
            assert y < y0, "no room beside: the label stacks ABOVE the peak, never over the line's history"
        assert done["glow"] == 0, "no relight yet"
        lit = P.probe(T_RELIGHT + RELIGHT_S / 2)["brackets"][0]
        assert abs(lit["glow"] - 1.0) < 1e-3, "the relight peaks at the middle of its word"
        after = P.probe(T_RELIGHT + RELIGHT_S + 0.1)["brackets"][0]
        assert after["glow"] == 0 and after["opacity"] == 1, "the flash is gone, the bracket stands"
    finally:
        P.close()


@needs_browser
def test_retitle_erases_the_old_title_glyph_by_glyph_before_the_new_one_writes():
    name, tl, uris, aspect, pts = _line_golden()
    tl2, peak, last = _authored(tl, pts)
    P = _Player(tl2, uris, aspect)
    try:
        pre = P.probe(T_RETITLE - 0.1)
        assert all(w >= 0.999 for w in pre["title"]) and all(w == 0 for w in pre["retitles"][0]), "before the word: the old title stands, the new is unwritten"
        mid = P.probe(T_RETITLE + 0.2)
        assert mid["title"][0] == 0 and mid["title"][-1] > 0, "the erase runs glyph by glyph, first glyph first"
        assert all(w == 0 for w in mid["retitles"][0]), "the new title does not write until the old is gone"
        post = P.probe(T_RETITLE + RETITLE_S + 0.6)
        assert all(w == 0 for w in post["title"]) and all(w >= 0.999 for w in post["retitles"][0]), "old gone, new written"
    finally:
        P.close()


@needs_browser
def test_undraw_unwinds_the_line_to_nothing_and_the_figure_writes_at_the_datum():
    """E50: on its word the line retraces itself back to nothing (the axes stay); then the figure the sentence turns to
    pops a dot on the datum and writes beside it, glyph by glyph."""
    name, tl, uris, aspect, pts = _line_golden()
    tl2, peak, last = _authored(tl, pts)
    P = _Player(tl2, uris, aspect)
    try:
        full = [p for p in P.probe(T_UNDRAW - 0.1)["paths"] if not p["muted"] and p["pts"]]
        assert full and all(p["frac"] > 0.99 for p in full), "fully deployed before the word"
        mid = [p for p in P.probe(T_UNDRAW + UNDRAW_S * 0.5)["paths"] if not p["muted"] and p["pts"]]
        assert all(0.05 < p["frac"] < 0.95 for p in mid), f"unwinding at the middle of the word: {[round(p['frac'], 3) for p in mid]}"
        assert mid[0]["frac"] < full[0]["frac"], "the nib is retracing, not drawing"
        gone = [p for p in P.probe(T_UNDRAW + UNDRAW_S + 0.05)["paths"] if not p["muted"] and p["pts"]]
        assert all(p["frac"] < 0.005 for p in gone), "to nothing"
        assert P.probe(T_FIGURE - 0.1)["figures"][0]["opacity"] == 0, "the figure waits for its word"
        early = P.probe(T_FIGURE + FIGURE_S * 0.05)["figures"][0]
        assert early["opacity"] == 1 and any(o < 0.5 for o in early["label"]), "the figure is being written, glyph by glyph - no pin dot (the third watch)"
        gone2 = [p for p in P.probe(T_FIGURE + FIGURE_S)["paths"] if not p["muted"] and p["pts"]]
        assert all(p["hidden"] for p in gone2), "an un-drawn path is hidden outright - no zero-length cap dot lingers"
        done = P.probe(T_FIGURE + FIGURE_S)["figures"][0]
        assert all(o >= 0.999 for o in done["label"]), "written"
        D = done["D"]; lp = P.probe(T_FIGURE + FIGURE_S)["linePts"][0][peak]
        assert abs(D[0] - lp[0]) < 1e-6 and abs(D[1] - lp[1]) < 1e-6, "pinned to the datum's exact position"
        assert (done["x"] > D[0]) == done["fits"], "beside the datum on the side with room"
        # P47 T9: the tail redraws after the undraw; the history stays un-drawn
        tail = [p for p in P.probe(T_REDRAW + REDRAW_S + 0.05)["paths"] if not p["muted"] and p["pts"] and p["k0"] > 0]
        hist = [p for p in P.probe(T_REDRAW + REDRAW_S + 0.05)["paths"] if p["pts"] and p["k0"] == 0]
        assert tail and all(p["frac"] > 0.99 for p in tail), f"the tail redrew to its end: {[round(p['frac'], 3) for p in tail]}"
        assert all(p["frac"] < 0.005 and p["hidden"] for p in hist), "the history stays un-drawn (paths: tail)"
        mid = [p for p in P.probe(T_REDRAW + REDRAW_S * 0.5)["paths"] if not p["muted"] and p["pts"] and p["k0"] > 0]
        assert all(0.05 < p["frac"] < 0.95 for p in mid), "redrawing at the middle of the word"
    finally:
        P.close()


@needs_browser
def test_the_performing_page_renders_identically_twice():
    name, tl, uris, aspect, pts = _line_golden()
    tl2, _p, _l = _authored(tl, pts)
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "perform.html"
        html.write_text(RB.instantiate(tl2, uris), encoding="utf-8")
        a = hashlib.sha256(RB.rgb_bytes(RB.render_frame(html, T_BRACKET + 1.2, aspect))[1]).hexdigest()
        b = hashlib.sha256(RB.rgb_bytes(RB.render_frame(html, T_BRACKET + 1.2, aspect))[1]).hexdigest()
    assert a == b, "two browsers, one frame: the species are pure functions of t"


def test_m11_takes_a_build_to_landing_with_the_build_as_the_first_charts_annotation():
    """The v3 page has no callout at its landing any more: the line ENDS on the peak (the cap), which is the annotation."""
    def tl(species):
        sc = _scene(species); sc["span"] = [2.0, 40.0]
        return {"aspect": "9:16", "runtime_s": 60.0, "scenes": [sc], "caption_pages": []}
    land = 2.0 + G.PAGE_BEAT_OFFSETS[-1]
    ok = G._first_chart_gate(tl([{"kind": "build_to", "at": round(land - 3.0, 2), "dur": 3.0, "target": {"kind": "datum", "index": 311}}]), [], {})
    assert ok.level in ("PASS", "WARN") and "the cap is the annotation" in ok.message, ok.message
    late = G._first_chart_gate(tl([{"kind": "build_to", "at": 18.0, "dur": 1.2, "target": {"kind": "datum", "index": 315}}]), [], {})
    assert late.level == "FAIL" and "unannotated" in late.message, "a cap that lands on a later word is not the first chart's annotation"


def test_a_page_species_authored_before_its_scene_is_a_state_and_credits_no_event_before_the_span():
    sc = _scene([{"kind": "retitle", "at": 41.0, "dur": 2.4, "text": "carried"}, {"kind": "bracket", "at": 50.0, "dur": 0.8, "from": 1, "to": 2, "label": "x"}])
    sc["span"] = [44.88, 61.76]
    ev = G._species_events([sc])
    assert all(t >= 44.88 for t in ev), ev
    assert 50.0 in ev and 50.8 in ev, "the bracket inside the span is credited as before"
