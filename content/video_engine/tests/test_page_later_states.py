"""P72 T26 - A PAGE'S LATER STATES (+ R26-408, R26-410: the same painters).

A ledger page may become other charts (`;then=` states, a `chart_to`); these are the laws a later state owes:
  R26-266  a `then=` state takes its OWN y scale: `then=<series>:<variant>[:<emphasize>][:domain=<ymin>,<ymax>]`
           (a rescale after a recast re-specifies the page's own object, so no door reached a state's range - H row 5's
           divergence state filled the bottom 40 % of its plot). Refused by name when malformed.
  R26-275  a long-form BARS page whose `then=` LINE state writes wider end tags draws in the viewBox that keeps them -
           P72 T12's `phone` law at every preset (at `middle` the line state stood in the bars page's legacy 1000
           units: its plot 30 % narrower than its own page's, its tags cut to their values).
  R26-265  `undraw` + `recede: true` - the page's axes, ticks, labels, rules, plot panel and words recede to the ground
           on the undraw's own clock, so a record owns a clean ground without a world change; a later `build_to`
           brings them back on its clock.
  R26-277  the `crimson` token paints E67's electric orange in every profile - the engine's written table (LP_INK)
           names that remap; this pins it.
  R26-331  a LEAVING bar's category label holds while its bar stands and goes with it (H 663.4: bars 5-8 stood with
           no month under them).
  R26-332  a state whose build has not started paints nothing - the page's `build_to` caps were applied to every
           state's paths (H 80.49: the arriving GDP line stood at 66 % from the recast's first frame, hidden only by
           the arriving-layer rule, and popped on at 66 % on its build's first frame, 81.70).
  R26-261  the title reads as ONE whole string at every instant of a plain recast - the old one or the new one, never
           a half-written mix (H 80.9: ": heir peak").
  R26-408  mid-rescale the x ticks never double-print: a target tick whose value AND text the standing chart carries
           stays hidden while its twin travels (the y branch's law).
  R26-410  in an extend's rescale phase the standing line's end name rides its own last datum, never ahead to the
           target's place over ink not yet drawn.

The fixtures are INLINE synthetic SHAPES (never a figure about the world) and the golden issuance page. The browser half
needs playwright + chromium and is skipped without them.
"""
from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"


def _chromium_available() -> bool:
    try:
        import served_player as SP
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

# ---- the fixtures: synthetic shapes --------------------------------------------------------------------------------
LINE_A = {"title": "The standing line's own title", "sub": "Synthetic points - the standing state", "src": "Synthetic - T26",
          "unit": "", "series": [{"label": "A", "color": "teal",
                                  "pts": [[2000 + i / 4, round(20 + 30 * i / 39, 2)] for i in range(40)]}],
          "xticks": [[2002, "2002"], [2005, "2005"], [2008, "2008"]]}
LINE_B = {"title": "The arriving line", "sub": "Synthetic points - the arriving state", "src": "Synthetic - T26",
          "unit": "", "series": [{"label": "B", "color": "cobalt",
                                  "pts": [[1970 + i / 2, round(8 + 3 * ((i % 20) / 20), 3)] for i in range(60)]}],
          "xticks": [[1975, "1975"], [1985, "1985"], [1995, "1995"]]}
LONG = {"title": "Three long names at the ends of three lines", "sub": "Synthetic points - the line state",
        "src": "Synthetic - T26", "unit": "", "ylabel": "index, synthetic, log scale", "log": True,
        "series": [{"label": f"+{v}%", "name": n, "color": c,
                    "pts": [[2025 + i / 40, round(100 * (1 + v / 100) ** (i / 39), 2)] for i in range(40)]}
                   for v, n, c in ((613, "MEMORY MAKERS (the long name)", "crimson"),
                                   (105, "SEMICONDUCTOR STOCKS", "teal"),
                                   (21, "MEGA-CAP TECH STOCKS", "cobalt"))],
        "badges": [{"label": "MEMORY", "value": "", "tag": "our layer", "accent": "coral"},
                   {"label": "SEMIS", "value": "", "tag": "their divergence", "accent": "teal"},
                   {"label": "MEGA", "value": "", "tag": "matches the market", "accent": "cobalt"}],
        "xticks": [[2025.2, "Mar"], [2025.5, "Jul"], [2025.8, "Oct"]]}
BARS8 = {"title": "Eight bars that leave", "sub": "Synthetic prints", "src": "Synthetic - T26", "unit": "%",
         "bars": [{"label": f"M{i + 1}", "value": v} for i, v in enumerate((-4, -12, -5, -10, -11, 11, -8, -10))]}
BARS1 = {"title": "One bar", "sub": "Synthetic share", "src": "Synthetic - T26", "unit": "%",
         "bars": [{"label": "Capex, next two years", "value": 94}]}
CRIMSON = {"title": "Two eras", "sub": "Synthetic yields", "src": "Synthetic - T26", "unit": "%",
           "series": [{"label": "5.1%", "name": "OLD ERA", "color": "teal",
                       "pts": [[i, round(5 + (i % 7) / 10, 2)] for i in range(40)]},
                      {"label": "4.7%", "name": "NEW ERA", "color": "crimson",
                       "pts": [[i, round(2 + i / 15, 2)] for i in range(40)]}],
           "xticks": [[0, "0"], [20, "20"], [39, "39"]]}
OBJECTS = {"t26-line-a": LINE_A, "t26-line-b": LINE_B, "t26-long": LONG, "t26-bars8": BARS8, "t26-bars1": BARS1,
           "t26-crimson": CRIMSON}


def _episode(tmp: Path) -> Path:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    for oid, obj in OBJECTS.items():
        (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    return tmp


def _world(row: str, tmp: Path) -> dict:
    ep = _episode(tmp)
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(row, (0, 0, 0), ep)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


def _tl(world: dict, species: list[dict], title: str = "P72 T26"):
    import build_golden_sources as G
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    tl = G._timeline(title, scenes, {}, "16:9")
    return tl, dict(G._base_uris(), **B.longform_assets(tl))


class _Served:
    """One served page of a timeline: seek (twice - the second read is the settled one) and evaluate."""

    def __init__(self, tl: dict, uris: dict):
        import render_baseline as RB
        import served_player as SP
        self.RB = RB
        self.size = RB.STAGE["16:9"]
        td = tempfile.TemporaryDirectory()
        html = Path(td.name) / "probe.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.page, self.errs, self._close = SP.open_served(html, *self.size, cleanup=td.cleanup)

    def seek(self, t: float) -> None:
        self.RB.frame_png(self.page, t, self.size)
        self.RB.frame_png(self.page, t, self.size)

    def ev(self, js: str, arg=None):
        return self.page.evaluate(js, arg)

    def close(self):
        self._close()


def _read(tl, uris, js: str, times: list[float]) -> list:
    s = _Served(tl, uris)
    try:
        out = []
        for t in times:
            s.seek(t)
            out.append(s.ev(js, t))
        assert not s.errs, s.errs
        return out
    finally:
        s.close()


PAGE_JS = "const w = [wA, wB].filter(e => e.__lp && e.classList.contains('ledger')).pop(), lp = w.__lp;"
# the visible alpha of an element: its own opacity and CSS filter opacity, times every ancestor's up to the stage
ALPHA_JS = """const alpha = (e) => { let a = 1;
  for (let n = e; n && n.id !== 'stage'; n = n.parentElement) { const c = getComputedStyle(n);
    if (c.display === 'none' || c.visibility === 'hidden') return 0;
    a *= +c.opacity; const f = /opacity\\(([\\d.]+)\\)/.exec(c.filter || ''); if (f) a *= +f[1];
    if (n.getAttribute && n.getAttribute('opacity') != null) a *= +n.getAttribute('opacity'); }
  return a; };"""


# ---- R26-266: a then= state takes its own y scale -------------------------------------------------------------------

def test_R26_266_a_then_state_names_its_own_domain(tmp_path):
    world = _world("ledger:t26-line-a:line;then=t26-line-b:line:domain=5,12", tmp_path)
    assert world["page_states"][0]["axes"]["domain"] == [5.0, 12.0]
    assert "domain" not in (world["page"].get("axes") or {}), "the page's own scale is the page's"


def test_R26_266_the_domain_and_the_emphasis_ride_together(tmp_path):
    world = _world("ledger:t26-line-a:line;then=t26-long:line:1:domain=90,800", tmp_path)
    state = world["page_states"][0]
    assert state["axes"]["domain"] == [90.0, 800.0] and state.get("emphasize") == 1, state.get("emphasize")


@pytest.mark.parametrize("bit,match", [
    ("domain=5", r"domain.*<ymin>,<ymax>"),
    ("domain=12,5", r"domain.*inverted"),
    ("domain=a,b", r"domain.*two numbers"),
    ("scale=5,12", r"then=.*'scale'.*domain"),
])
def test_R26_266_a_malformed_then_domain_is_refused_by_name(bit, match, tmp_path):
    with pytest.raises(ValueError, match=match):
        _world(f"ledger:t26-line-a:line;then=t26-line-b:line:{bit}", tmp_path)


def test_R26_266_a_then_state_without_a_domain_is_unchanged(tmp_path):
    a = _world("ledger:t26-line-a:line;then=t26-line-b:line", tmp_path / "a")
    assert "domain" not in (a["page_states"][0].get("axes") or {})


SCALE_JS = PAGE_JS + """ const S = lp.states[1]; const sc = S.scale || {};
  const ys = (S.paths || []).flatMap(pp => (pp.pts || []).map(p => p[1]));
  const pb = S.lfPanelEl ? S.lfPanelEl : null;
  return { active: lp.active | 0, y0: sc.y0, y1: sc.y1, top: Math.min(...ys), bot: Math.max(...ys),
           plotTop: sc.my ? sc.my(sc.y1) : null, plotBot: sc.my ? sc.my(sc.y0) : null };"""


@needs_browser
def test_R26_266_the_state_draws_on_the_range_it_names(tmp_path):
    """Recast at 10 s to the state born on `domain=7.9,11.2`: its scale is that pair, and its line fills the plot (its
    own object, drawn on the object's padded range, is what the row replaces)."""
    world = _world("ledger:t26-line-a:line;then=t26-line-b:line:domain=7.9,11.2", tmp_path)
    tl, uris = _tl(world, [{"kind": "chart_to", "to": "recast", "state": 1, "at": 10.0, "dur": 1.2, "keyed": False}])
    (r,) = _read(tl, uris, "(t) => {" + SCALE_JS + "}", [16.0])
    assert r["active"] == 1, r
    assert r["y0"] == pytest.approx(7.9) and r["y1"] == pytest.approx(11.2), r
    fill = (r["bot"] - r["top"]) / (r["plotBot"] - r["plotTop"])
    assert fill > 0.85, f"the state's line fills {fill:.2f} of its plot"


# ---- R26-275: a bars page's line state keeps its own width at every preset -----------------------------------------

@pytest.mark.parametrize("preset", ["bravos", "middle", "phone"])
def test_R26_275_a_bars_page_takes_its_line_states_tag_room_at_every_preset(preset, tmp_path):
    world = _world(f"ledger:t26-bars1:bars;then=t26-long:line;readability=longform:{preset}", tmp_path)
    page = world["page"]
    assert page["axes"].get("tag_room", 0) > 0, page["axes"]
    assert LPG.longform_bars_vw(page, LPG.longform_scale0()) > 1000, "the bars page's viewBox keeps the state's tags"


def test_R26_275_a_bars_page_with_no_line_state_keeps_the_legacy_viewbox(tmp_path):
    for preset in ("bravos", "middle"):
        page = _world(f"ledger:t26-bars1:bars;then=t26-bars8:bars;readability=longform:{preset}", tmp_path / preset)["page"]
        assert "tag_room" not in page["axes"] and LPG.longform_bars_vw(page, LPG.longform_scale0()) == 1000


BOX_JS = PAGE_JS + """ const stage = document.getElementById('stage').getBoundingClientRect(), k = 1920 / stage.width;
  const S = lp.states[lp.active | 0], R = (e) => { const r = e.getBoundingClientRect();
    return { x: (r.left - stage.left) * k, y: (r.top - stage.top) * k, w: r.width * k, h: r.height * k }; };
  const vis = (e) => e && +getComputedStyle(e).opacity > 0.5 && e.getAttribute('opacity') !== '0' && (e.textContent || '').trim();
  const tags = [...S.chart.querySelectorAll('text.sname')].filter(vis).map(e => ({ text: e.textContent, r: R(e) }));
  const yl = (S.marks || []).find(m => m.role === 'axislabel' && m.el && vis(m.el));
  return { active: lp.active | 0, panel: S.lfPanelEl ? R(S.lfPanelEl) : null, tags, ylabel: yl ? R(yl.el) : null,
           stageW: 1920 };"""


def _box_after(row: str, tmp: Path, species: list[dict], t: float) -> dict:
    tl, uris = _tl(_world(row, tmp), species)
    (r,) = _read(tl, uris, "(t) => {" + BOX_JS + "}", [t])
    return r


def _overlap(a: dict, b: dict) -> bool:
    return a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]


@needs_browser
@pytest.mark.parametrize("preset", ["bravos", "middle"])
def test_R26_275_the_line_state_draws_in_its_own_width_and_its_tags_on_the_stage(preset, tmp_path):
    """bars -> line at a long-form preset: the state's plot is as wide as the same line's own page (to 2 px), every end
    tag stands on the stage, and its y label meets no tag."""
    rec = [{"kind": "chart_to", "to": "recast", "state": 1, "at": 9.0, "dur": 1.5, "keyed": False}]
    got = _box_after(f"ledger:t26-bars1:bars;then=t26-long:line;readability=longform:{preset}", tmp_path / "b2l", rec, 18.0)
    own = _box_after(f"ledger:t26-long:line;readability=longform:{preset}", tmp_path / "own", [], 18.0)
    assert got["active"] == 1 and got["panel"] and own["panel"], (got, own)
    assert got["panel"]["w"] >= own["panel"]["w"] - 2.0, (
        f"{preset}: the line state's plot {got['panel']['w']:.0f} px vs its own page's {own['panel']['w']:.0f} px")
    assert got["tags"] and all(t["r"]["x"] + t["r"]["w"] <= got["stageW"] + 0.5 for t in got["tags"]), got["tags"]
    if got["ylabel"]:
        assert not [t for t in got["tags"] if _overlap(got["ylabel"], t["r"])], (got["ylabel"], got["tags"])


# ---- R26-265: an undraw may take the page's axes and chrome with it -------------------------------------------------

UNDRAW_AT, UNDRAW_S = 10.0, 0.8


def _undraw(**kw) -> dict:
    return dict({"kind": "undraw", "at": UNDRAW_AT, "dur": UNDRAW_S, "target": {"kind": "datum", "index": 0}}, **kw)


def test_R26_265_recede_is_an_undraws_word_and_refused_by_name_elsewhere():
    assert B._validate_entry(_undraw(recede=True)) == []
    errs = B._validate_entry(_undraw(recede="yes"))
    assert any("recede" in e for e in errs), errs
    errs = B._validate_entry({"kind": "build_to", "at": 1.0, "dur": 1.0, "target": {"kind": "datum", "index": 3}, "recede": True})
    assert any("recede" in e and "undraw" in e for e in errs), errs
    focus = {"kind": "panel_focus", "at": 1.0, "dur": 1.0, "recede": {"dim": 0.5}}   # a focus state's OWN recede (P69 T8b)
    assert not [e for e in B._validate_entry(focus) if "an undraw's word" in e], B._validate_entry(focus)


CHROME_JS = PAGE_JS + ALPHA_JS + """ const S = lp.states[lp.active | 0];
  const roles = ['axis', 'tick', 'ylabel', 'xtick', 'axislabel', 'rule', 'rulelabel'];
  const els = (S.marks || []).filter(m => roles.includes(m.role) && m.el && (m.el.textContent || m.el.tagName !== 'text'))
    .map(m => m.el).concat(S.lfPanelEl ? [S.lfPanelEl] : []);
  const ink = ['.lp-title', '.lp-sub', '.lp-src'].map(s => lp.page.querySelector(s)).filter(e => e && e.textContent.trim());
  return { n: els.length, chrome: Math.max(...els.map(alpha)), ink: Math.max(...ink.map(alpha)) };"""


@needs_browser
@pytest.mark.parametrize("opt", ["", ";readability=longform"])
def test_R26_265_the_page_recedes_to_its_ground_and_a_build_brings_it_back(opt, tmp_path):
    world = _world(f"ledger:t26-line-a:line{opt}", tmp_path)
    back = {"kind": "build_to", "at": 16.0, "dur": 1.0, "series": 0, "target": {"kind": "datum", "index": 39}}
    tl, uris = _tl(world, [_undraw(recede=True), back])
    before, mid, gone, returned = _read(tl, uris, "(t) => {" + CHROME_JS + "}", [9.5, UNDRAW_AT + UNDRAW_S * 0.1, 13.0, 18.0])
    assert before["n"] > 4 and before["chrome"] > 0.85 and before["ink"] > 0.85, before
    assert 0.05 < mid["chrome"] < 0.95, f"the axes recede on the undraw's own (eased) clock, as its lines do: {mid}"
    assert gone["chrome"] < 0.02 and gone["ink"] < 0.02, f"a clean ground under the record: {gone}"
    assert returned["chrome"] > 0.85 and returned["ink"] > 0.85, f"a later build_to brings the page back: {returned}"


@needs_browser
def test_R26_265_an_undraw_without_the_word_keeps_its_axes(tmp_path):
    world = _world("ledger:t26-line-a:line", tmp_path)
    tl, uris = _tl(world, [_undraw()])
    (gone,) = _read(tl, uris, "(t) => {" + CHROME_JS + "}", [13.0])
    assert gone["chrome"] > 0.85 and gone["ink"] > 0.85, gone


# ---- R26-277: the named colour is kept or remapped by the written table ---------------------------------------------

def test_R26_277_the_engine_names_its_crimson_remap_in_one_table():
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const LP_INK = \{([^}]*)\}", src)
    assert m, "the field's ink table"
    table = dict(re.findall(r"(\w+): \"(#[0-9A-Fa-f]{6})\"", m.group(1)))
    assert table["crimson"].upper() == "#FF8A4C", table   # E67: the crimson SLOT is the electric orange
    assert "The `crimson` slot IS that orange" in src


INK_JS = PAGE_JS + """ const S = lp.states[lp.active | 0];
  return (S.paths || []).filter(pp => !pp.muted).map(pp => ({ si: pp.si, stroke: getComputedStyle(pp.p).stroke }));"""


@needs_browser
@pytest.mark.parametrize("opt", ["", ";readability=longform"])
def test_R26_277_a_crimson_series_paints_the_tables_ink_in_every_profile(opt, tmp_path):
    tl, uris = _tl(_world(f"ledger:t26-crimson:line{opt}", tmp_path), [])
    (paths,) = _read(tl, uris, "(t) => {" + INK_JS + "}", [14.0])
    by = {p["si"]: p["stroke"] for p in paths}
    assert by[1] == "rgb(255, 138, 76)", by   # LP_INK.crimson, #FF8A4C
    assert by[0] == "rgb(52, 245, 197)", by   # LP_INK.teal, #34F5C5


# ---- R26-331: a leaving bar keeps its label until its own leave ------------------------------------------------------

BARS_JS = PAGE_JS + """ const S = lp.states[0];
  return (S.bars || []).map(bb => { const m = /scaleY\\(([-\\d.e]+)\\)/.exec(bb.bar.style.transform || '');
    return { s: m ? +m[1] : 1, lab: +(bb.lab.getAttribute('opacity') || 0) }; });"""


@needs_browser
@pytest.mark.parametrize("opt", ["", ";readability=longform"])
def test_R26_331_a_leaving_bars_label_holds_while_its_bar_stands(opt, tmp_path):
    world = _world(f"ledger:t26-bars8:bars;then=t26-line-a:line{opt}", tmp_path)
    tl, uris = _tl(world, [{"kind": "chart_to", "to": "recast", "state": 1, "at": 10.0, "dur": 0.8, "keyed": False}])
    times = [round(10.0 + 0.05 * k, 2) for k in range(1, 16)]
    bad = []
    for t, bars in zip(times, _read(tl, uris, "(t) => {" + BARS_JS + "}", times)):
        for i, b in enumerate(bars):
            if b["s"] >= 0.999 and b["lab"] < 0.999:
                bad.append((t, i + 1, "stands, unlabelled", b))
            elif b["lab"] < b["s"] - 0.02:
                bad.append((t, i + 1, "its label left ahead of it", b))
            elif b["s"] <= 0.001 and b["lab"] > 0.02:
                bad.append((t, i + 1, "its label outlived it", b))
    assert not bad, bad[:6]


# ---- R26-332: a state whose build has not started paints nothing ----------------------------------------------------

CAPS = [{"kind": "build_to", "at": 5.0, "dur": 0.5, "series": 0, "target": {"kind": "datum", "index": 10}},
        {"kind": "build_to", "at": 7.0, "dur": 1.0, "series": 0, "target": {"kind": "datum", "index": 39}}]
RECAST_AT, RECAST_S = 10.0, 1.2
STATE1_JS = PAGE_JS + """ const S = lp.states[1];
  return { op: S.chart.style.opacity, paths: (S.paths || []).map(pp => { const off = parseFloat(pp.p.getAttribute('stroke-dashoffset'));
    return Math.max(0, Math.min(1, 1 - (Number.isFinite(off) ? off : pp.len) / (pp.len || 1))); }) };"""


@needs_browser
def test_R26_332_the_arriving_state_carries_none_of_its_marks_before_its_build(tmp_path):
    """Read with the arriving-layer rule OFF - the paths' own dash, never the layer's opacity: until its build starts
    (the recast's end) the arriving line is drawn to nothing (the base drew it to the standing page's cap - 66 % of it -
    from the recast's first frame); built, it stands at the page's caps as it always did."""
    world = _world("ledger:t26-line-a:line;then=t26-line-b:line", tmp_path)
    species = CAPS + [{"kind": "chart_to", "to": "recast", "state": 1, "at": RECAST_AT, "dur": RECAST_S, "keyed": False}]
    tl, uris = _tl(world, species)
    end = RECAST_AT + RECAST_S
    times = [RECAST_AT, RECAST_AT + 0.4, end - 0.01, end + 12.0]
    reads = _read(tl, uris, "(t) => {" + STATE1_JS + "}", times)
    for t, r in zip(times[:3], reads[:3]):
        assert max(r["paths"]) < 0.001, f"t {t}: the arriving state is drawn {r['paths']} before its build"
    assert min(reads[3]["paths"]) > 0.6, f"built, it stands at the page's caps: {reads[3]}"


# ---- R26-261: the title rewrites whole across a plain recast --------------------------------------------------------

TITLE_JS = PAGE_JS + """ const pf = lp.perform || { retitles: [] };
  const gw = (g) => parseFloat(g.style.getPropertyValue('--w')) || 0;
  const old = ((pf.retitles || [])[0] || {}).glyphs || [], neu = ((pf.retitles || [])[1] || {}).glyphs || [];
  const A = lp.states[0], Bs = lp.states[1];
  const shown = (S) => +S.chart.style.opacity > 0 ? (S.marks || []).filter(m => ['ylabel', 'xtick'].includes(m.role) && m.el
    && (m.el.textContent || '').trim() && +(m.el.style.opacity || 1) > 0.05).length : 0;
  return { old: old.map(gw), neu: neu.map(gw), a: shown(A), b: shown(Bs) };"""


@needs_browser
@pytest.mark.parametrize("empty_first", [False, True], ids=["drawn", "undrawn-first"])
def test_R26_261_the_title_reads_whole_at_every_instant_of_a_recast(empty_first, tmp_path):
    """The standing title is a retitle the compiler takes with its page (R26-219's `leave_at` = the recast's start, as
    H row 22's "Why trim? ..." at 663.02) and the arriving one fires on the recast's clock: at every instant one of the
    two stands whole and the other not at all - never a mix (H 80.9 ": heir peak"; 663.4 "r 7 of 8 weak prints ..."),
    and never neither: with the line undrawn before the recast (H row 5 at 93.34) the plot is empty from its first frame,
    and the standing title still waits for the one that takes its place."""
    world = _world("ledger:t26-line-a:line;then=t26-line-b:line", tmp_path)
    species = [{"kind": "retitle", "at": 5.0, "dur": 1.2, "text": "The standing title, a retitle", "leave_at": RECAST_AT, "leave_s": 1.0},
               {"kind": "chart_to", "to": "recast", "state": 1, "at": RECAST_AT, "dur": RECAST_S, "keyed": False},
               {"kind": "retitle", "at": RECAST_AT + 0.1, "dur": RECAST_S, "text": "The arriving title, written whole"}]
    if empty_first:
        species.append({"kind": "undraw", "at": RECAST_AT - 1.0, "dur": 0.8, "target": {"kind": "datum", "index": 0}})
    tl, uris = _tl(world, species)
    times = [round(RECAST_AT + 0.05 * k, 2) for k in range(0, 33)]
    bad, mixed_axes = [], []
    for t, r in zip(times, _read(tl, uris, "(t) => {" + TITLE_JS + "}", times)):
        old_whole, old_gone = min(r["old"]) >= 0.999, max(r["old"]) <= 0.001
        new_whole, new_gone = bool(r["neu"]) and min(r["neu"]) >= 0.999, max(r["neu"] or [0]) <= 0.001
        if not ((old_whole and new_gone) or (old_gone and new_whole)):
            bad.append((t, round(min(r["old"]), 3), round(max(r["old"]), 3), round(min(r["neu"] or [0]), 3), round(max(r["neu"] or [0]), 3)))
        if r["a"] and r["b"]:
            mixed_axes.append((t, r["a"], r["b"]))
    assert not bad, f"a half-written title (t, old min/max, new min/max): {bad[:6]}"
    assert not mixed_axes, f"two scales' labels at once (t, standing, arriving): {mixed_axes[:6]}"


RETITLE_JS = PAGE_JS + """ const pf = lp.perform || { retitles: [] };
  return (((pf.retitles || [])[0] || {}).glyphs || []).map(g => parseFloat(g.style.getPropertyValue('--w')) || 0);"""


@needs_browser
def test_R26_261_a_retitle_off_a_recast_still_writes_by_hand(tmp_path):
    """No recast on: the retitle's own hand (erase, then glyph by glyph) is untouched - mid-write it is part-written."""
    world = _world("ledger:t26-line-a:line", tmp_path)
    tl, uris = _tl(world, [{"kind": "retitle", "at": 10.0, "dur": 2.0, "text": "A title the hand writes"}])
    (ws,) = _read(tl, uris, "(t) => {" + RETITLE_JS + "}", [11.2])
    assert ws and 0.05 < sum(ws) / len(ws) < 0.95, ws


# ---- R26-408 / R26-410: a rescale's ticks and an extend's end name --------------------------------------------------

RESCALE_AT, EXTEND_AT, XF_DUR = 8.0, 10.5, 1.2


def _issuance(species: list[dict]):
    import build_golden_sources as G
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{G.PROJ_ID}.series.json").write_text(json.dumps(G.projection_series()), encoding="utf-8")
            world = B.world_for_plate(G.PROJ_PLATE, (0, 0, 0), Path(td))
            B.stamp_full_stage(world["page"])
            B.derive_rescale_states(world, species, G.PROJ_PLATE, Path(td))
    finally:
        B.ASPECT = saved
    return _tl(world, species, "T26: a rescale's ticks, an extend's name")


XTICK_JS = PAGE_JS + """ const out = [];
  lp.states.forEach((S, si) => { if (!(+S.chart.style.opacity > 0)) return;
    for (const m of S.marks || []) { if (m.role !== 'xtick' || !m.el) continue; const txt = (m.el.textContent || '').trim();
      const o = m.el.style.opacity === '' ? 1 : +m.el.style.opacity; if (txt && o > 0.05) out.push([si, txt, o]); } });
  return out;"""


@needs_browser
@pytest.mark.parametrize("which", ["rescale", "extend"])
def test_R26_408_no_x_tick_double_prints_mid_rescale(which):
    species = [{"kind": "chart_to", "at": RESCALE_AT, "dur": XF_DUR, "to": "rescale", "window": [2021, 2023]},
               {"kind": "chart_to", "at": EXTEND_AT, "dur": XF_DUR, "to": "extend", "series": 1}]
    tl, uris = _issuance(species)
    at, share = (RESCALE_AT, 1.0) if which == "rescale" else (EXTEND_AT, 0.45)
    times = [round(at + XF_DUR * share * f, 3) for f in (0.15, 0.35, 0.55, 0.75, 0.95)]
    bad = []
    for t, ticks in zip(times, _read(tl, uris, "(t) => {" + XTICK_JS + "}", times)):
        texts = [x[1] for x in ticks]
        twice = sorted({x for x in texts if texts.count(x) > 1})
        if twice:
            bad.append((t, twice, ticks))
    assert not bad, f"x tick labels printed twice (t, texts, [state, text, opacity]): {bad[:3]}"


NAME_JS = PAGE_JS + """ const A = lp.states[1];
  const nm = (A.markBy || {})['name:s0'], pp = (A.paths || []).filter(p => (p.si | 0) === 0 && p.data).pop();
  if (!nm || !pp) return null;
  const len = pp.p.getTotalLength(), off = parseFloat(pp.p.getAttribute('stroke-dashoffset')) || 0;
  const q = pp.p.getPointAtLength(Math.max(0, len - off));
  return { op: +(nm.el.getAttribute('opacity') || 0), x: +nm.el.getAttribute('x'), y: +nm.el.getAttribute('y'),
           endX: q.x, endY: q.y, restX: nm.geom.x, restY: nm.geom.y, endRestX: pp.pts[pp.pts.length - 1][0],
           endRestY: pp.pts[pp.pts.length - 1][1] };"""


@needs_browser
def test_R26_410_the_end_name_rides_its_own_ink_in_an_extends_rescale_phase():
    """Window [2021, 2023], then the estimate: through the extend's rescale phase the standing actual's name keeps the
    offset it stands at from its own drawn end - it never travels ahead to where the grown line will end."""
    species = [{"kind": "chart_to", "at": RESCALE_AT, "dur": XF_DUR, "to": "rescale", "window": [2021, 2023]},
               {"kind": "chart_to", "at": EXTEND_AT, "dur": XF_DUR, "to": "extend", "series": 1}]
    tl, uris = _issuance(species)
    times = [round(EXTEND_AT + XF_DUR * 0.45 * f, 3) for f in (0.2, 0.5, 0.8, 0.97)]
    bad = []
    for t, r in zip(times, _read(tl, uris, "(t) => {" + NAME_JS + "}", times)):
        assert r, "the standing state has its actual's name and line"
        dx, dy = (r["x"] - r["endX"]) - (r["restX"] - r["endRestX"]), (r["y"] - r["endY"]) - (r["restY"] - r["endRestY"])
        if r["op"] > 0.05 and (abs(dx) > 3 or abs(dy) > 3):
            bad.append((t, round(dx, 1), round(dy, 1), r))
    assert not bad, f"the end name left its ink (t, dx, dy): {bad[:3]}"
