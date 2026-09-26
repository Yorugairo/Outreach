"""P72 T46d - THE PAGE MARKS AND LOOKS (the wave-3 follow-ups' page half).

  * R26-219 (the span): the railway bracket's span stood IN the end tags' column, through "741 RAILWAY SHARE PRICES" -
    the engine now steps a span that lands inside a tag it spans back to the column's inner edge (the compiler's WARN
    names the move);
  * R26-373: M49 reads a BARS page (a point mark against the bars' tops and values); a mark on a DOCKED chart's datum
    before the card's line has drawn it is WARNed with the estimate ((c), punch on a dock datum, stays open);
  * R26-375: (a) a brace whose label is lifted above its bar draws a LEADER from its point to the label; (b) the
    compiler's copied bracket / bar constants are pinned to the engine's, and the span estimate's label top reads the
    series' own top (it was the plot's: the railway label's estimate 170 vs drawn 240); (c) a WARN that echoes a
    non-ASCII label never raises on a cp1252 console;
  * R26-379: `label_at: "axis"` - the level join's figure as the accent pill ON the value axis (Bravos DOM 00:50.5);
  * R26-382 / R26-383: a vector map beside a card (`room=` on a vecmap world, the map fitted into the strip beside
    it), `;fit=tight`, and the ping's glow measured off CHN 02:21;
  * R26-384: the failed link's disc sized by the stage (BOOM's 46 px), the hub's `look: "seal"` (DOM 04:30), and the
    gate crediting a rim node's own landing;
  * R26-387: the end tags stand over the lens's glass;
  * R26-395: a solo that ADDS its bar to the lit set (Bravos D40 R30); R26-396: the long form's lit end badge is a box;
  * R26-370: the tiers' shared scale is the compiler's default, a band's `axes.domain` is drawn, malformed keys refused.

E99 s106 throughout: a placement finding is a WARN; only the truth rules refuse. The browser rows need playwright +
chromium and are skipped without them.
"""
from __future__ import annotations

import inspect
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
SPECIES = SCRIPTS / "species"
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as MG  # noqa: E402
import ledger_page as LPG  # noqa: E402
import probe as PR  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE_SRC = ENGINE.read_text(encoding="utf-8")
RAIL_BRACKET = {"kind": "bracket", "at": 12.0, "dur": 1.6, "from": 53, "to": 139, "label": "−64%", "sub": "peak to trough"}
RAIL_BUILD = [dict(G.LIT_SPECIES[0]), dict(G.LIT_SPECIES[1])]


def _node(js: str) -> object:
    """Run an ES module snippet with node and return its one JSON line."""
    out = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, cwd=str(ROOT), timeout=60)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def _mod(name: str) -> str:
    return (SPECIES / name).resolve().as_uri()


def _rail_page() -> dict:
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(G.LIT_PLATE, (0, 0, 0), G.LIT_PROJECT)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world["page"]


def _bars_page(values=(42.0, 31.0, 27.0, 18.0, 9.0)) -> dict:
    s = {"title": "Five holders, ranked", "src": "Synthetic series for the test surface; not a figure about the world",
         "unit": "$", "unit_suffix": "B", "bars": [{"label": f"H{i}", "value": v} for i, v in enumerate(values)]}
    assert LPG.validate(s, "bars") == [], LPG.validate(s, "bars")
    return B.stamp_full_stage(LPG.build_spec(s, "bars", None, "right"))


def _tiers_series(**extra) -> dict:
    s = {"title": "Two reserves", "sub": "s", "src": "Synthetic series for the test surface; not a figure about the world",
         "tiers": [{"name": "A", "unit": "Mb", "pts": [[2015, 300], [2020, 320], [2025, 310]]},
                   {"name": "B", "unit": "Mb", "pts": [[2015, 600], [2020, 700], [2025, 650]]}]}
    s.update(extra)
    return s


# ---- R26-375 (c): a WARN that echoes a non-ASCII label never kills a redirected build ----------------------------------

def test_the_compile_report_survives_a_cp1252_console():
    code = ("import sys; sys.path.insert(0, r'%s'); import build_scene_timeline_f as B; B._console_safe(); "
            "print('  [WARN] P72 T18: figure ' + repr('\\u221264%%') + ' restates its bar')") % SCRIPTS
    env = dict(os.environ, PYTHONIOENCODING="cp1252")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, env=env, timeout=120)
    assert out.returncode == 0, out.stderr.decode("cp1252", "replace")
    assert b"\\u2212" in out.stdout, ("the minus written as its escape, the line kept", out.stdout)


def test_a_strict_stream_is_the_one_reconfigured_and_main_calls_it_first():
    class S:
        errors, done = "strict", None

        def reconfigure(self, **kw):
            self.done = kw
    s = S()
    B._console_safe(s)
    assert s.done == {"errors": "backslashreplace"}, "the encoding is kept (a log that encodes today is the same bytes)"
    s2 = S()
    s2.errors = "replace"
    B._console_safe(s2)
    assert s2.done is None, "a stream that already tolerates is left alone"
    body = inspect.getsource(B.main).splitlines()
    assert "_console_safe()" in body[1], ("the first statement of main", body[:3])


# ---- R26-375 (b): the compiler's copied constants ARE the engine's -----------------------------------------------------

def _frozen(name: str) -> dict:
    m = re.search(r"const " + name + r" = Object\.freeze\(\{(.*?)\}\);", ENGINE_SRC, re.S)
    assert m, name
    body = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
    return {k: float(v) for k, v in re.findall(r"([A-Z_]+):\s*(-?[\d.]+)", body)}


def test_the_bracket_and_brace_constants_match_the_engine():
    ps = {k: float(v) for k, v in re.findall(r"(BRACKET_GAP|BRACKET_ROOM|BRACKET_TICK_W):\s*([\d.]+)", ENGINE_SRC)}
    U = B.BRACKET_ROOM_U
    assert (U["GAP"], U["ROOM"]) == (ps["BRACKET_GAP"], ps["BRACKET_ROOM"])
    tag = re.search(r"BRACKET_TAG_AIR = ([\d.]+), BRACKET_TAG_MIN = ([\d.]+)", ENGINE_SRC)
    assert (U["TAG_AIR"], U["TAG_MIN"]) == (float(tag.group(1)), float(tag.group(2)))
    brace = _frozen("LPBRACE")
    for k in ("GAP", "R", "R_EM", "LABEL_EM", "NAME_EM", "ABOVE_EM", "HAND_DESC", "SUB_EM"):
        assert B.BRACE_ROOM_U[k] == brace[k], (k, B.BRACE_ROOM_U[k], brace[k])
    assert "const lx = fits ? x + 12 + half : x - 4 - half" in ENGINE_SRC and U["ANCHOR"] == 4
    assert "yClear - (sp.sub ? fss * 1.3 : 0) - 10" in ENGINE_SRC and (U["OVER"], U["SUB_LEAD"]) == (10, 1.3)


def test_the_bars_layout_constants_match_the_engine():
    bar, seg, val = _frozen("LPBAR"), _frozen("LPSEG"), _frozen("LPVAL")
    U = B.BARS_ROOM_U
    assert (U["W_PX"], U["PITCH_RATIO"]) == (bar["W_PX"], bar["PITCH_RATIO"])
    assert (U["FIG_LINE"], U["SEG_PAD_PX"], U["LEAD_PX"]) == (seg["FIG_LINE"], seg["PAD_PX"], seg["LEAD_PX"])
    assert (B.BRACKET_TYPE_ASC, B.BRACKET_TYPE_DESC) == (val["ASC"], val["LAB_DESC"])
    src = ENGINE_SRC[ENGINE_SRC.index("const buildLedgerBars"):][:9000]
    assert "LF ? LF.gutter : 60" in src and U["GUTTER"] == 60
    assert "LF ? LF.bars_b : 440, top = P ? 150 : PN ? LPBAR_PANEL.TOP : 90" in src and (U["BOTTOM"], U["TOP"]) == (440, 90)
    assert ": 980, gap = 0.34" in src and (U["X1"], U["GAP"]) == (980, 0.34)
    assert "(hi0 - lo0) * 0.14" in src and U["PAD"] == 0.14
    assert "x0 - 26," in src and U["TICK_DX"] == 26


def test_the_line_scale_the_span_estimate_mirrors_is_the_engines():
    src = ENGINE_SRC[ENGINE_SRC.index("const buildLedgerLine"):][:6000]
    U = B.BRACKET_ROOM_U
    assert "T = P ? 90 : 40, B = P ? G.H - 80 : LFT ? LFT.line_b : (PHONE ? 458 : 470)" in src
    assert (U["LINE_T"], U["LINE_B"], U["LINE_B_PHONE"]) == (40, 470, 458)
    assert "const pad = (y1 - y0) * 0.06 || 1" in src and U["LINE_PAD"] == 0.06


# ---- R26-219 (the span) + R26-375 (b): the compiler's word for it --------------------------------------------------------

def test_the_railway_span_warn_names_the_step_back_and_the_label_over_the_series_top():
    (w,) = B.check_brace(_rail_page(), RAIL_BUILD + [dict(RAIL_BRACKET)], "16:9")
    assert "steps the span back to the column's inner edge" in w and "REPORTED (E99 s106)" in w, w
    assert w.isascii(), w
    y = float(re.search(r"its box ~\[\d+, (\d+),", w).group(1))
    assert y > 200, ("the label stacks over the SERIES' top (the peak), not the plot's (the old 170)", y)


# ---- R26-370: the tiers' shared scale is the compiler's default -----------------------------------------------------------

def test_same_unit_tiers_carry_the_shared_scale_by_default():
    spec = LPG.build_spec(_tiers_series(), "tiers", None, "right")
    assert spec.get("shared_tier_domains") == {"Mb": [0.0, 700.0]}, spec.get("shared_tier_domains")


def test_independent_keeps_each_band_its_own_and_an_authored_key_is_taken():
    assert "shared_tier_domains" not in LPG.build_spec(_tiers_series(independent=True), "tiers", None, "right")
    s = _tiers_series(shared_tier_domains={"Mb": [100, 800]})
    assert LPG.validate(s, "tiers") == []
    assert LPG.build_spec(s, "tiers", None, "right")["shared_tier_domains"] == {"Mb": [100.0, 800.0]}


@pytest.mark.parametrize("bad, word", [({"Mb": [5, 1]}, "low first"), ({"GW": [0, 1]}, "not a unit"),
                                       ([0, 1], "must be an object")])
def test_a_malformed_shared_key_is_refused_by_name(bad, word):
    errs = LPG.validate(_tiers_series(shared_tier_domains=bad), "tiers")
    assert any("shared_tier_domains" in e and word in e for e in errs), errs


def test_a_malformed_band_domain_is_refused_by_name():
    s = _tiers_series()
    s["tiers"][0]["domain"] = [400, 100]
    errs = LPG.validate(s, "tiers")
    assert any("domain" in e and "tiers[0]" in e for e in errs), errs


def test_the_engine_draws_the_shared_scale_else_a_bands_own_domain():
    r = _node(f"""import {{ tierDomainOf, tierDomain }} from '{_mod("tiers.mjs")}';
      const pg = {{ shared_tier_domains: {{ Mb: [0, 700] }} }}, a = {{ unit: 'Mb' }}, b = {{ unit: 'Mb', axes: {{ domain: [250, 350] }} }};
      console.log(JSON.stringify({{ shared: tierDomainOf(pg, a, [300, 310]), own: tierDomainOf({{}}, b, [300, 310]),
        plain: tierDomainOf({{}}, a, [300, 310]), was: tierDomain([300, 310], true, null),
        indep: tierDomainOf({{ shared_tier_domains: pg.shared_tier_domains, axes: {{ independent: true }} }}, b, [300, 310]) }}));""")
    assert r["shared"][0] == 0 and r["shared"][1] == pytest.approx(756.0), r
    assert r["own"] == [250, 350], "a band's declared domain, verbatim"
    assert r["plain"] == r["was"], "no key, no domain: the band's own extent, as before"
    assert r["indep"] == [250, 350]


# ---- R26-395: a solo that ADDS its mark ------------------------------------------------------------------------------------

def test_a_solo_add_is_grammar_refused_by_name_when_malformed():
    assert B._validate_solo({"kind": "solo", "at": 5, "dur": 0.5, "bar": 2, "add": True}) == []
    errs = B._validate_solo({"kind": "solo", "at": 5, "dur": 0.5, "bar": 2, "add": "yes"})
    assert any("add" in e and "must be true" in e for e in errs), errs


def test_an_add_needs_a_standing_solo_of_its_kind():
    world = {"kind": "ledger", "page": _bars_page()}
    B.check_solo(world, [{"kind": "solo", "at": 5, "dur": 0.5, "bar": 0}, {"kind": "solo", "at": 7, "dur": 0.5, "bar": 2, "add": True}])
    with pytest.raises(ValueError, match="no solo stands before it"):
        B.check_solo(world, [{"kind": "solo", "at": 7, "dur": 0.5, "bar": 2, "add": True}])
    with pytest.raises(ValueError, match="no solo stands before it"):
        B.check_solo(world, [{"kind": "solo", "at": 5, "dur": 0.5, "bar": 0}, {"kind": "unsolo", "at": 6, "dur": 0.5},
                             {"kind": "solo", "at": 7, "dur": 0.5, "bar": 2, "add": True}])


def test_the_added_bar_keeps_its_ink_with_the_first():
    r = _node(f"""import {{ soloEvents, soloAlpha, SOLO }} from '{_mod("solo.mjs")}';
      const ev = soloEvents([{{ kind: 'solo', at: 5, dur: 0.5, bar: 0 }}, {{ kind: 'solo', at: 7, dur: 0.5, bar: 2, add: true }}], []);
      const a = (k, t) => +soloAlpha(ev, k, t).toFixed(3);
      console.log(JSON.stringify({{ keys: ev.map((e) => e.keys), b0: a('b:0', 8), b2: a('b:2', 8), b1: a('b:1', 8), b2mid: a('b:2', 6), dim: SOLO.DIM,
        plain: soloEvents([{{ kind: 'solo', at: 5, dur: 0.5, bar: 0 }}, {{ kind: 'solo', at: 7, dur: 0.5, bar: 2 }}], []).map((e) => e.keys) }}));""")
    assert r["keys"] == [["b:0"], ["b:0", "b:2"]], r
    assert (r["b0"], r["b2"], r["b1"]) == (1, 1, r["dim"]), r
    assert r["b2mid"] == r["dim"], "before its word the second bar is muted with the rest"
    assert r["plain"] == [["b:0"], ["b:2"]], "a solo without `add` takes the light, as before"


# ---- R26-379: the level's figure as the axis pill --------------------------------------------------------------------------

def test_label_at_axis_is_the_axis_forms_and_is_refused_by_name_elsewhere():
    base = {"kind": "level_join", "at": 5, "dur": 1.5, "from": 3, "label": "4%"}
    assert B._validate_level_join(dict(base, to={"y": 4.0}, label_at="axis")) == []
    assert any("label_at" in e and "one of" in e for e in B._validate_level_join(dict(base, to={"y": 4.0}, label_at="rule")))
    assert any("axis form" in e for e in B._validate_level_join(dict(base, to=7, label_at="axis")))
    assert any("side places the figure" in e for e in B._validate_level_join(dict(base, to={"y": 4.0}, label_at="axis", side="left")))


# ---- R26-384: the fail disc, the seal hub, the gate's rim landings ---------------------------------------------------------

def test_the_failed_links_disc_is_sized_by_the_stage():
    src = (SPECIES / "flow.mjs").read_text(encoding="utf-8")
    assert "FAIL_PX: 46," in src and "const r = FLOW.FAIL_PX / 2" in src, "BOOM's 46 px badge, whatever the card's size"


def test_the_seal_look_is_a_hubs_and_refused_by_name_elsewhere():
    assert B._validate_flow_look({"look": "seal", "layout": "hub"}) == []
    assert "not one of" in B._validate_flow_look({"look": "glow", "layout": "hub"})[0]
    assert "takes layout 'hub'" in B._validate_flow_look({"look": "seal"})[0]


def test_the_seal_spokes_are_dashes_drawn_by_the_pen():
    r = _node(f"""import {{ flowSealDashes, FLOW }} from '{_mod("flow.mjs")}';
      const pts = [{{ x: 0, y: 0 }}, {{ x: 340, y: 0 }}];
      console.log(JSON.stringify({{ none: flowSealDashes(pts, 0).length, part: flowSealDashes(pts, 0.55), all: flowSealDashes(pts, 1).length, D: FLOW.SPOKE_DASH, G: FLOW.SPOKE_GAP }}));""")
    assert r["none"] == 0 and r["all"] == 10, r
    assert r["part"][-1][0]["x"] == pytest.approx(170.0) and r["part"][-1][1]["x"] == pytest.approx(187.0), ("the pen's dash, cut at its reach", r)
    assert r["part"][0][1]["x"] == pytest.approx(r["D"]), r


def test_the_gate_credits_a_rim_node_landing_on_its_own_word():
    tl, _ = G.hub_spoke_fail()
    ev = MG._species_events(tl["scenes"])
    for _, _, _, w in G.HUB_NODES[1:]:
        assert round(w, 2) in ev, (w, ev)


# ---- R26-382 / R26-383: the map beside a card, the tight fit ---------------------------------------------------------------

@pytest.mark.parametrize("room", [[0.03, 0.12, 0.5, 0.72], [0.55, 0.1, 0.42, 0.8], [0.1, 0.62, 0.8, 0.35], [0.2, 0.05, 0.6, 0.3]])
def test_the_maps_strip_beside_a_room_is_one_law_in_two_languages(room):
    js = _node(f"""import {{ vecmapRegion }} from '{_mod("vecmap.mjs")}'; console.log(JSON.stringify(vecmapRegion({json.dumps(room)})));""")
    py = B.vecmap_free_region(room)
    assert (js is None) == (py is None)
    if py is not None:
        assert js == pytest.approx(py), (js, py)


def test_a_vecmap_takes_a_room_and_a_tight_fit_refused_by_name_elsewhere():
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        w = B.world_for_plate("vecmap:IRN,OMN,ARE;room=0.03,0.12,0.5,0.72;fit=tight", (0, 0, 0), None)
        assert w["room"] == [0.03, 0.12, 0.5, 0.72] and w["fit"] == "tight", w
        with pytest.raises(ValueError, match="no strip of the stage"):
            B.world_for_plate("vecmap:IRN;room=0.05,0.05,0.9,0.9", (0, 0, 0), None)
        with pytest.raises(ValueError, match="VECTOR MAP option"):
            B.world_for_plate(G.LIT_PLATE + ";fit=tight", (0, 0, 0), G.LIT_PROJECT)
        with pytest.raises(ValueError, match="FOCUS SET"):
            B.world_for_plate("vecmap;fit=tight", (0, 0, 0), None)
        with pytest.raises(ValueError, match="is not one of"):
            B.world_for_plate("vecmap:IRN;fit=loose", (0, 0, 0), None)
    finally:
        B.ASPECT = saved


def test_the_fit_goes_into_the_strip_and_tight_frames_closer():
    r = _node(f"""import {{ mapFit, vecmapRegion }} from '{_mod("vecmap.mjs")}';
      const box = [1000, 500], bb = [[600, 130, 640, 160]];
      const plain = mapFit(box, bb, 1920, 1080), tight = mapFit(box, bb, 1920, 1080, 0.055, {{ tight: true }});
      const reg = vecmapRegion([0.03, 0.12, 0.5, 0.72]), side = mapFit(box, bb, 1920, 1080, 0.055, {{ region: reg, tight: true }});
      const c = (f) => [f.sx * 620 + f.tx, f.sy * 145 + f.ty];
      console.log(JSON.stringify({{ reg, k0: plain.sx, k1: tight.sx, c0: c(plain), c2: c(side), same: mapFit(box, bb, 1920, 1080, 0.055, null) }}));""")
    assert r["reg"] == pytest.approx([0.53, 0, 0.47, 1]), r["reg"]
    assert r["k1"] > r["k0"] * 2, ("the tight fit frames the focus set closer", r["k0"], r["k1"])
    assert r["c0"] == pytest.approx([960, 540]), "the plain fit centres on the stage, as before"
    assert r["c2"][0] == pytest.approx(1920 * (0.53 + 0.47 / 2)), "beside the card, the focus stands at its strip's centre"


def test_the_ping_blooms():
    r = _node(f"""import {{ pingStyle, PING }} from '{_mod("vecmap.mjs")}'; console.log(JSON.stringify({{ s: pingStyle(), P: PING }}));""")
    assert "stroke-width:9" in r["s"] and r["s"].count("drop-shadow") == 2, r


# ---- R26-373 (a) / (b): M49 on a bars page; a dock datum before its line -----------------------------------------------------

def test_the_probe_counts_a_bars_pages_marks():
    page = _bars_page()
    tl = {"scenes": [{"scene_id": "s01", "span": [0, 30], "world": {"kind": "ledger", "page": page}, "docks": [],
                      "species": [{"kind": "ring", "at": 5, "dur": 2, "target": {"kind": "point", "x": 0.5, "y": 0.5}}]}]}
    marks, counts = PR.reach_marks_at(tl, 6.0)
    assert marks and counts["page"] == [5] and counts.get("bars") is True, counts


def test_the_gate_names_the_bar_a_mark_missed():
    doc = {"instants": [{"t": 6, "mreach": [{"kind": "ring", "scene": "s01", "at": 5.0, "chart": "page", "centre": [900, 300],
                                             "reach": [54, 40], "dist_px": 212.0, "norm": 4.1, "series": 0, "datum": 2, "on": "bar"}]}]}
    g = MG._mark_reach_gate(doc)
    assert g.level == "WARN" and "nearest bar (bar 2" in g.message, g


def _dock_row(at: float):
    ev = {"slide-a": {"chart": {"series": [{"name": "A", "pts": [[i, i] for i in range(20)]}]}}}
    docks = [{"slide": "slide-a", "enter": 10.0, "exit": 30.0}]
    sp = [{"kind": "ring", "at": at, "dur": 1.0, "target": {"kind": "datum", "dock": 0, "series": 0, "index": 18}}]
    return sp, docks, ev


def test_a_mark_before_its_dock_datum_is_drawn_is_warned_with_the_estimate():
    sp, docks, ev = _dock_row(11.0)
    assert B.dock_datum_errors(sp, docks, ev, "row") == []
    (w,) = B.dock_datum_draw_notes(sp, docks, ev, "row")
    assert "before the card's line has drawn it" in w and "REPORTED (E99 s106)" in w, w
    drawn = B.dock_datum_drawn_at(docks[0], ev["slide-a"]["chart"], 0, 18)
    assert 10.45 < drawn < 10.45 + 6.0 * 1.0 + 1e-9, drawn
    sp2, _, _ = _dock_row(drawn + 0.1)
    assert B.dock_datum_draw_notes(sp2, docks, ev, "row") == [], "a mark after the pen is silent"


def test_the_dock_draw_clock_mirrors_the_engines():
    m = re.search(r"const DUR = Math\.min\(([\d.]+), Math\.max\(([\d.]+), \(d\.exit - d\.enter\) \* ([\d.]+)\)\);", ENGINE_SRC)
    C = B.DOCK_CHART_DRAW
    assert m and (C["DUR_MAX"], C["DUR_MIN"], C["DUR_K"]) == tuple(float(v) for v in m.groups())
    assert "const EXIT = 0.72, CARD_IN = 0.75;" in ENGINE_SRC and C["CARD_IN"] == 0.75
    assert "clamp01((t - d.enter - CARD_IN * 0.6) / DUR)" in ENGINE_SRC and C["LEAD"] == 0.6
    assert "((tRel - pp.delay) / DUR - pp.stagger * 0.35) / 0.65" in ENGINE_SRC and (C["STAGGER"], C["LEN"]) == (0.35, 0.65)


# ---- the browser rows ---------------------------------------------------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _serve_tl(tl: dict, uris: dict, t: float, js: str):
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "t46d.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE[tl.get("aspect") or "16:9"]
        pg, errs, close = SP.open_served(html, w, h)
        try:
            pg.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
            return pg.evaluate(js), errs
        finally:
            close()


def _serve(page: dict, species: list, t: float, js: str, uris: dict | None = None):
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    tl = G._timeline("P72 T46d", scenes, {}, "16:9")
    return _serve_tl(tl, uris if uris is not None else G._base_uris(), t, js)


LP = "const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp, PF = st.perform || {};"
BB = "const bb = (el) => { if (!el) return null; const r = el.getBBox(); return [r.x, r.y, r.width, r.height]; };"


def _meet(a, b) -> float:
    return max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])) * max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))


@needs_browser
def test_the_railway_span_stands_clear_of_the_end_tags():
    js = "() => {" + LP + BB + """
      const b = PF.brackets[0], d = b.main.line.getAttribute('d'), x = +d.split(' ')[0].slice(1);
      const tags = st.paths.filter(p => p.name && !p.muted && p.name.textContent.trim()).map(p => bb(p.name));
      const t1 = b.main.t1.getAttribute('d');
      return { x, tags, t1, label: bb(b.main.label), dataX: st.linePts[0][139][0], fits: b.fits };
    }"""
    s, errs = _serve(_rail_page(), RAIL_BUILD + [dict(RAIL_BRACKET)], 14.5, js)
    assert not errs, errs
    for tb in s["tags"]:
        assert s["x"] < tb[0], ("the span stands before the column's first glyph", s["x"], tb)
    tick_end = float(s["t1"].split(" l")[1].split(" ")[0])
    assert s["x"] + tick_end >= s["dataX"], ("the foot tick stops at its data", s)
    assert s["x"] > s["dataX"], "still to the right of its data"
    assert s["fits"] is False and all(_meet(s["label"], tb) == 0 for tb in s["tags"]), s


@needs_browser
def test_the_span_estimate_is_where_the_label_is_drawn():
    page = _rail_page()
    (w,) = B.check_brace(page, RAIL_BUILD + [dict(RAIL_BRACKET)], "16:9")
    est = [float(v) for v in re.search(r"its box ~\[(\d+), (\d+), (\d+) x (\d+)\]", w).groups()]
    js = "() => {" + LP + "const r = PF.brackets[0].main.label.getBoundingClientRect(), s = document.getElementById('stage').getBoundingClientRect(); return [r.x - s.x, r.y - s.y, r.width, r.height]; }"
    drawn, errs = _serve(page, RAIL_BUILD + [dict(RAIL_BRACKET)], 14.5, js)
    assert not errs, errs
    assert abs(est[1] - drawn[1]) <= 24, ("the estimate's top within a line's air of the drawn label (was 70 px off)", est, drawn)
    assert abs((est[0] + est[2]) - (drawn[0] + drawn[2])) <= 24, ("its right edge (the anchor) too", est, drawn)


@needs_browser
@pytest.mark.parametrize("bar", [0, 1])
def test_a_lifted_braces_leader_runs_from_its_point_to_its_label(bar):
    tlp = _bars3()
    js = "() => {" + LP + BB + """
      const b = PF.brackets[0], L = b.main.lead;
      if (!L) return { above: b.above, lead: null };
      const n = L.getTotalLength(), a = L.getPointAtLength(0), z = L.getPointAtLength(n);
      return { above: b.above, cusp: b.cusp, a: [a.x, a.y], z: [z.x, z.y], label: bb(b.main.label), sub: bb(b.main.sub),
               off: +L.getAttribute('stroke-dashoffset') };
    }"""
    s, errs = _serve(tlp, [dict(G.BRACE_SPECIES[0], bar=bar)], 16.33, js)
    assert not errs, errs
    assert s["above"] and "a" in s, ("the lifted label's brace draws a leader", s)
    assert s["a"] == pytest.approx(s["cusp"], abs=0.2), ("it leaves the brace's point", s)
    words = s["sub"] or s["label"]
    assert s["z"][1] > words[1] + words[3] - 1 and s["z"][1] - (words[1] + words[3]) < 12, ("it ends just under the words", s)
    assert s["off"] == pytest.approx(0, abs=0.5), "drawn by the brace's word's end"


def _bars3() -> dict:
    s = G.stacked_funding_series()
    for k in ("series", "line_unit", "line_label"):
        s.pop(k, None)
    return B.stamp_full_stage(LPG.build_spec(s, "bars", None, "right"))


@needs_browser
def test_a_clean_brace_draws_no_leader():
    tl, uris = G.brace_funding()
    js = "() => {" + LP + "return PF.brackets.map(b => !!b.main.lead);}"
    s, errs = _serve_tl(tl, uris, G.FRAME_T["brace-funding"], js)
    assert not errs and s == [False], (s, errs)


@needs_browser
def test_the_added_bars_both_keep_their_ink_on_the_page():
    js = "() => {" + LP + "return st.bars.map(b => b.bar.getAttribute('opacity'));}"
    sp = [{"kind": "solo", "at": 5, "dur": 0.5, "bar": 0}, {"kind": "solo", "at": 7, "dur": 0.5, "bar": 2, "add": True}]
    s, errs = _serve(_bars_page(), sp, 9.0, js)
    assert not errs, errs
    assert s[0] is None and s[2] is None, ("both named bars at full ink (the attribute removed)", s)
    assert all(float(v) < 0.5 for i, v in enumerate(s) if i not in (0, 2)), s


def _lf_solo(t: float, js: str):
    species = [dict(e) for e in G.SOLO_SPECIES[:1]]
    plate = G.SOLO_PLATE + ";readability=longform"
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(plate, (0, 0, 0), G.LIT_PROJECT)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    tl = G._timeline("P72 T46d lf solo", scenes, {}, "16:9")
    return _serve_tl(tl, dict(G._base_uris(), **B.longform_assets(tl)), t, js)


BADGE_JS = "() => {" + LP + BB + """
  const pp = st.paths.find(p => (p.si | 0) === """ + str(G.SOLO_CHIPS) + """ && !p.muted);
  const r = pp.badge; if (!r) return { none: true };
  return { rect: [+r.getAttribute('x'), +r.getAttribute('y'), +r.getAttribute('width'), +r.getAttribute('height')],
           op: r.getAttribute('opacity'), fill: r.style.fill, tag: bb(pp.name), under: r.compareDocumentPosition(pp.name) & 4,
           ink: pp.name.style.fill };
}"""


@needs_browser
def test_the_long_forms_lit_end_badge_is_a_filled_box():
    s, errs = _lf_solo(G.SOLO_CHIPS_AT + 1.0, BADGE_JS)
    assert not errs, errs
    assert not s.get("none"), "the line builder draws the badge's box"
    r, tg = s["rect"], s["tag"]
    assert r[0] < tg[0] and r[1] < tg[1] and r[0] + r[2] > tg[0] + tg[2] and r[1] + r[3] > tg[1] + tg[3], ("round the tag", s)
    assert s["op"] == "1.000" and "lp-acc" in s["fill"] and s["under"], s
    assert "1e1f22" in s["ink"].lower() or "30, 31, 34" in s["ink"], ("the type on the box is the key's charcoal", s["ink"])


@needs_browser
def test_the_end_badge_box_is_nothing_before_the_word():
    s, errs = _lf_solo(G.SOLO_CHIPS_AT - 1.0, BADGE_JS)
    assert not errs, errs
    assert s["rect"][2] == 0 and s["op"] == "0", s


@needs_browser
def test_the_level_pill_stands_on_the_value_axis_at_the_rules_level():
    page = _level_page()
    vals = page["series"][0]["pts"]
    i = len(vals) - 1
    sp = [{"kind": "level_join", "at": 5.0, "dur": 1.5, "from": i, "to": {"y": float(vals[i][1])}, "label": "30%", "label_at": "axis"}]
    js = "() => {" + LP + BB + """
      const L = PF.levelJoins[0], p = L.pill;
      const r = p.g.getBoundingClientRect(), cr = p.rect.getBoundingClientRect(), stg = document.getElementById('stage').getBoundingClientRect();
      const ticks = st.marks.filter(m => m.role === 'ylabel').map(m => ({ box: (() => { const q = m.el.getBoundingClientRect(); return [q.x - stg.x, q.y - stg.y, q.width, q.height]; })(), vis: m.el.style.visibility }));
      const A = st.linePts[0][""" + "${I}" + """];
      const M = st.chart.getScreenCTM(), ay = M.b * A[0] + M.d * A[1] + M.f - stg.y;
      return { op: p.g.getAttribute('opacity'), pill: [cr.x - stg.x, cr.y - stg.y, cr.width, cr.height], ay, ticks,
               glyphs: L.lg.map(t => +t.getAttribute('opacity')), plotL: M.a * st.plot.L + M.e - stg.x };
    }"""
    s, errs = _serve(page, sp, 7.0, js.replace("${I}", str(i)))
    assert not errs, errs
    assert s["op"] == "1.000" and all(g == 0 for g in s["glyphs"]), s
    pl = s["pill"]
    assert abs(pl[1] + pl[3] / 2 - s["ay"]) < 1.5, ("centred on the rule's level", pl, s["ay"])
    assert pl[0] + pl[2] <= s["plotL"] + 4, ("on the tick column, left of the plot", pl, s["plotL"])
    hid = [t for t in s["ticks"] if t["vis"] == "hidden"]
    for t in hid:
        assert _meet(t["box"], pl) > 0
    for t in s["ticks"]:
        if _meet(t["box"], pl) > 0:
            assert t["vis"] == "hidden", ("a tick the pill covers is hidden", t, pl)


def _level_page() -> dict:
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(G.LEVEL_PLATE, (0, 0, 0), G.LEVEL_PROJECT)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world["page"]


@needs_browser
def test_the_end_tags_stand_over_the_lens():
    tl, uris = G.lens_over_the_line()
    js = "() => {" + LP + """
      const ld = PF.lenses[0], T = ld.tagLayer;
      const order = ld.g.compareDocumentPosition(T.g) & 4;
      const same = T.tags.filter(q => q.k === 0).every(q => q.cp.getAttribute('x') === q.src.getAttribute('x') && q.cp.getAttribute('y') === q.src.getAttribute('y') && q.cp.textContent === q.src.textContent && (q.cp.getAttribute('style') || '') === (q.src.getAttribute('style') || ''));
      return { n: T.tags.length, order, same, op: T.g.getAttribute('opacity'), clip: T.g.getAttribute('clip-path'), r: +T.ring.getAttribute('r') };
    }"""
    s, errs = _serve_tl(tl, uris, G.FRAME_T["lens-over-the-line"], js)
    assert not errs, errs
    assert s["n"] >= 2 and s["order"] and s["same"] and s["op"] == "1" and "url(#" in s["clip"] and s["r"] > 0, s


@needs_browser
def test_the_seal_hub_has_no_card_and_dashed_spokes():
    tl, uris = G.hub_spoke_fail()
    tl["scenes"][0]["species"][0]["look"] = "seal"
    tl["scenes"][0]["species"][0].pop("fail")
    js = """() => { const g = document.querySelector('#species g.flow'); if (!g) return null;
      return { spokes: g.querySelectorAll('path.flowspoke').length, arrows: g.querySelectorAll('path.flowarrow').length,
               cards: g.querySelectorAll('rect.chipcard').length }; }"""
    s, errs = _serve_tl(tl, uris, 9.6, js)
    assert not errs, errs
    assert s["arrows"] == 0 and s["spokes"] > 10, s
    assert s["cards"] == len(G.HUB_NODES) - 1, ("the rim keeps its cards; the hub stands without one", s)


@needs_browser
def test_the_map_fits_beside_the_card_with_a_soft_edge():
    import build_scene_timeline_f as BST
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate("vecmap:IRN,OMN,ARE;room=0.03,0.12,0.5,0.72;fit=tight", (0, 0, 0), None)
    finally:
        B.ASPECT = saved
    species = [{"kind": "light", "at": 2.0, "dur": 10.0, "idle": "breath", "ping": True, "target": {"kind": "country", "id": "OMN"}}]
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    uris = G._base_uris()
    uris[BST.MAP_PREFIX + world["map"]] = BST.world_map_json(world["map"])
    tl = G._timeline("P72 T46d map beside", scenes, {}, "16:9")
    tl["captions"], tl["caption_pages"] = [], []
    js = """() => { const svg = [...document.querySelectorAll('svg')].find(s => s.querySelector('.vmland')); if (!svg) return null;
      const f = [...svg.querySelectorAll('path.vmfocus')].map(p => p.getBoundingClientRect()), stg = document.getElementById('stage').getBoundingClientRect();
      const x0 = Math.min(...f.map(r => r.left)) - stg.x, x1 = Math.max(...f.map(r => r.right)) - stg.x;
      return { x0, x1, mask: svg.style.maskImage || svg.style.webkitMaskImage }; }"""
    s, errs = _serve_tl(tl, uris, 3.0, js)
    assert not errs, errs
    assert s["x0"] >= 0.53 * 1920 - 2, ("the focus set stands in the strip beside the card", s)
    assert "linear-gradient" in s["mask"], s
