"""P69 T26a / R26-273 - A BAR CHANGES ITS OWN VALUE: the halving compare moves the bar, not only its number.

E28 (the operator, 2026-09-03): a chart reads right at a glance - the geometry says what the number says. P69 T6 put a
figure on a bars page and let `chart_to compare` melt it into the comparator, but the BAR stood still: on the T10b
halving frame "10%" was printed over a bar still drawn to 20% (`scratchpad/p69t10b/frames/t10b-halving-soft.png`).

Measured on the served player, on test_compare_on_bars' own three H fixtures:

  (1) THE MORPH       on a compare whose figure speaks for its bar (metric.value is the bar's own value) and whose
                      comparator is another value, the bar's rect is drawn to the comparator's value on the page's own
                      scale once the compare has landed - and on the compare's own clock in between (COMPARE.COUNT of
                      the window on min-jerk, the counter's clock): monotone, never past either end, a pure function of t.
  (2) RIDES THE TOP   the figure (the bar's value, which the bar's own label yields to - T6) keeps its gap to the bar's
                      top; the bar's own value label and its text ride with it.
  (3) FOLLOWS         `;bar_style=soft` (T10b): the foot squares the new zero end and the hatch silhouette is the moved
                      bar thrown along the light; `;form=extruded_bar` (P58 T5): the prism's cap stands on the new top.
  (4) NO CHANGE       a compare whose comparator is the same value (row 21's 3x -> "3 wafers") writes nothing on the bar:
                      its rect's attributes and the figure's group are exactly the built ones at every instant.
  (5) THE GHOST       the old height stays as a dashed outline ONLY when the row names it (`ghost: "yes"`); never by
                      default.
  (6) THE GOLDEN      `bar-value-morph` - the halving at rest after the morph - is a committed golden, pinned here the
                      way test_agenda_page pins its own surfaces (render_baseline.check).

The browser half needs playwright + chromium and is skipped without them.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import render_baseline as RB  # noqa: E402
from test_compare_on_bars import CMP_AT, CMP_S, FIXTURES, LAND_T  # noqa: E402

ASPECT = "16:9"
SOFT = ";bar_style=soft"
XBAR = ";form=extruded_bar"
GOLDEN = "bar-value-morph"
BEFORE_T = CMP_AT - 0.3              # the page built, the figure written, the compare not begun
COUNT = 0.72                         # species/compare.mjs COMPARE.COUNT - the counter's share of the window (the bar's clock)
MID_TS = [round(CMP_AT + CMP_S * COUNT * k / 6, 3) for k in range(1, 6)]
UNIT_TOL = 0.15                      # chart units: a rect's attributes are written to one decimal
PX_TOL = 1.2                         # stage px: the figure's gap to the bar's top, before and after


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _timeline(name: str, tmp: Path, opt: str = "", species: list[dict] | None = None) -> tuple[dict, dict]:
    oid, obj, authored, _bar = FIXTURES[name]
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        world = B.world_for_plate(f"ledger:{oid}:bars{opt}", (0, 0, 0), tmp)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    sp = copy.deepcopy(authored if species is None else species)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": sp}]
    return G._timeline("P69 T26a: " + name + opt, scenes, {}, ASPECT), G._base_uris()


PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, PF = st.perform || { figures: [] };
  const stage = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect(); return [r.x - stage.x, r.y - stage.y, r.width, r.height]; };
  const a = (el, k) => el.getAttribute(k);
  const S = st.scale || {};
  const bars = (st.bars || []).map(b => ({
    x: a(b.bar, 'x'), y: a(b.bar, 'y'), w: a(b.bar, 'width'), h: a(b.bar, 'height'), rx: a(b.bar, 'rx'),
    xf: b.bar.style.transform, box: R(b.bar), v: b.v,
    val: b.val ? { y: a(b.val, 'y'), text: b.val.textContent } : null,
    foot: b.foot ? { y: a(b.foot, 'y'), h: a(b.foot, 'height') } : null,
    cap: b.ex ? (b.bar.parentNode.querySelectorAll('polygon.bx-cap')[b.i] || null) : null }));
  bars.forEach(b => { if (b.cap) b.cap = b.cap.getAttribute('points'); });
  const L = st.soft || null;
  const sil = L ? L.sil.map(p => { const d = p.getAttribute('d') || ''; if (!d) return null; const bb = p.getBBox(); return [bb.x, bb.y, bb.width, bb.height]; }) : [];
  const figs = (PF.figures || []).map(fg => ({ text: (fg.label.textContent || '').replace(/\\u00a0/g, ' ').trim(),
    box: R(fg.label), xf: fg.g.getAttribute('transform'), op: +(fg.g.getAttribute('opacity') || 0) }));
  const ghosts = [...st.chart.querySelectorAll('.lp-bar-ghost')].map(g => { const bb = g.getBBox();
    return { box: [bb.x, bb.y, bb.width, bb.height], stage: R(g), fill: a(g, 'fill'), dash: a(g, 'stroke-dasharray'),
             op: +(a(g, 'opacity') || 0) }; });
  return { bars, figs, ghosts, sil, soft: !!L, my0: S.my ? S.my(0) : null, my20: S.my ? S.my(20) : null,
           my10: S.my ? S.my(10) : null, my3: S.my ? S.my(3) : null };
}"""


class Player:
    """One fixture served at the stage's native size: `at(t)` seeks and probes, `png(t)` shoots."""

    def __init__(self, browser, name: str, opt: str = "", species: list[dict] | None = None):
        self._td = tempfile.TemporaryDirectory()
        tmp = Path(self._td.name)
        tl, uris = _timeline(name, tmp / "ep", opt, species)
        html = tmp / "bars.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.w, self.h = RB.STAGE[ASPECT]
        self._srv, port = RB.serve(html.parent)
        self.page = browser.new_context(viewport={"width": self.w, "height": self.h}, device_scale_factor=1).new_page()
        self.errs: list[str] = []
        self.page.on("pageerror", lambda e: self.errs.append(str(e)))
        self.page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, self.w, self.h)
        self.page.wait_for_function("document.fonts.status === 'loaded'")

    def at(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE)

    def png(self, t: float) -> bytes:
        RB.frame_png(self.page, t, (self.w, self.h))
        self.page.wait_for_timeout(120)
        return RB.frame_png(self.page, t, (self.w, self.h))

    def close(self) -> None:
        self.page.context.close()
        self._srv.shutdown()
        self._td.cleanup()


def _ghosted(name: str) -> list[dict]:
    sp = copy.deepcopy(FIXTURES[name][2])
    for e in sp:
        if e.get("kind") == "chart_to":
            e["ghost"] = "yes"
    return sp


# key -> (fixture, row options, species override)
CASES = {
    "halving": ("row18-halving", "", None),
    "halving-soft": ("row18-halving", SOFT, None),
    "halving-xbar": ("row18-halving", XBAR, None),
    "halving-ghost": ("row18-halving", "", _ghosted("row18-halving")),
    "wafer": ("row21-wafer", "", None),
}


@pytest.fixture(scope="module")
def read(tmp_path_factory):
    """Each case served once: read before the compare, through its clock, landed, and after a seek round trip."""
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for key, (name, opt, species) in CASES.items():
                pl = Player(browser, name, opt, species)
                try:
                    got = {"before": pl.at(BEFORE_T), "mid": [pl.at(t) for t in MID_TS], "land": pl.at(LAND_T)}
                    got["back"] = pl.at(MID_TS[2])
                    got["land2"] = pl.at(LAND_T)
                    got["errs"] = list(pl.errs)
                    out[key] = got
                finally:
                    pl.close()
            cold = Player(browser, "row18-halving")   # a COLD seek straight into the landed frame
            try:
                out["cold"] = cold.at(LAND_T)
            finally:
                cold.close()
        finally:
            browser.close()
    return out


def _bar(p: dict) -> dict:
    return p["bars"][0]


def _f(v) -> float:
    return float(v)


@needs_browser
@pytest.mark.parametrize("key", ["halving", "halving-soft", "halving-xbar", "halving-ghost"])
def test_after_the_compare_the_bar_stands_at_the_comparators_value(read, key):
    got = read[key]
    assert not got["errs"], got["errs"]
    before, land = _bar(got["before"]), _bar(got["land"])
    p = got["land"]
    assert abs(_f(before["y"]) - p["my20"]) < UNIT_TOL, ("the bar builds to its own 20", before["y"], p["my20"])
    assert abs(_f(land["y"]) - p["my10"]) < UNIT_TOL, \
        f"{key}: after the compare the bar's top is at {land['y']} - the 20% top is {p['my20']:.1f}, the comparator's 10% is {p['my10']:.1f} (E28: the geometry says what the number says)"
    assert abs(_f(land["y"]) + _f(land["h"]) - p["my0"]) < UNIT_TOL, "the bar still stands on zero"
    assert land["x"] == before["x"] and land["w"] == before["w"], "only the height moves"
    assert got["land"]["figs"][0]["text"].startswith("10%"), got["land"]["figs"][0]["text"]


@needs_browser
def test_the_bar_moves_on_the_compares_own_clock_monotone_and_never_past_either_end(read):
    got = read["halving"]
    p0 = got["before"]
    tops = [_f(_bar(p0)["y"])] + [_f(_bar(m)["y"]) for m in got["mid"]] + [_f(_bar(got["land"])["y"])]
    assert all(b >= a - 1e-6 for a, b in zip(tops, tops[1:])), ("a halving's top only ever falls", tops)
    inner = tops[1:-1]
    assert all(p0["my20"] + 0.5 < y < p0["my10"] - 0.5 for y in inner[1:-1]), ("mid-clock the bar is BETWEEN the two values", tops)
    assert abs(tops[-2] - p0["my10"]) > 0.5 or abs(tops[-2] - tops[-1]) < UNIT_TOL


@needs_browser
def test_the_figure_rides_the_bars_top_and_the_value_label_with_it(read):
    got = read["halving"]
    b0, b1 = _bar(got["before"]), _bar(got["land"])
    f0, f1 = got["before"]["figs"][0], got["land"]["figs"][0]
    gap0 = b0["box"][1] - (f0["box"][1] + f0["box"][3])
    gap1 = b1["box"][1] - (f1["box"][1] + f1["box"][3])
    assert abs(gap1 - gap0) < PX_TOL, (f"the figure stood {gap0:.1f} px over its bar's top and {gap1:.1f} px after the morph "
                                       "- it must ride the top")
    assert b1["box"][1] - b0["box"][1] > 100, "the bar's top fell by half its height"
    dv = _f(b1["val"]["y"]) - _f(b0["val"]["y"])
    dt = _f(b1["y"]) - _f(b0["y"])
    assert abs(dv - dt) < UNIT_TOL, ("the bar's own value label rides its top", dv, dt)
    assert b1["val"]["text"] == "10%" and b0["val"]["text"] == "20%", (b0["val"], b1["val"])


@needs_browser
def test_soft_the_foot_and_the_hatch_follow_the_moved_bar(read):
    p = read["halving-soft"]["land"]
    assert p["soft"]
    b = _bar(p)
    assert abs(_f(b["y"]) - p["my10"]) < UNIT_TOL, ("the soft bar is drawn to the comparator", b["y"], p["my10"])
    assert b["xf"] in ("scaleY(1.0000)", "scaleY(1)"), ("the shoulders keep their radius: the height is the rect's, never a squash", b["xf"])
    assert abs(_f(b["foot"]["y"]) + _f(b["foot"]["h"]) - (_f(b["y"]) + _f(b["h"]))) < UNIT_TOL, ("the foot squares the zero end", b["foot"], b)
    sil = p["sil"][0]
    assert sil is not None
    before = read["halving-soft"]["before"]["sil"][0]
    moved = _f(b["y"]) - _f(_bar(read["halving-soft"]["before"])["y"])
    assert abs((sil[1] - before[1]) - moved) < 0.6, ("the hatch silhouette is the moved bar thrown along the light", sil, before, moved)


@needs_browser
def test_extruded_the_prisms_cap_stands_on_the_new_top(read):
    p = read["halving-xbar"]["land"]
    b = _bar(p)
    assert abs(_f(b["y"]) - p["my10"]) < UNIT_TOL, ("the extruded bar is drawn to the comparator", b["y"], p["my10"])
    assert b["cap"], "the extruded page draws a cap face"
    ys = [float(q.split(",")[1]) for q in b["cap"].split()]
    assert abs(max(ys) - _f(b["y"])) < UNIT_TOL + 0.1, ("the cap's front edge IS the bar's top", ys, b["y"])


@needs_browser
def test_a_compare_with_no_value_change_writes_nothing_on_the_bar(read):
    got = read["wafer"]
    assert not got["errs"], got["errs"]
    want = {k: v for k, v in got["before"]["bars"][1].items() if k in ("x", "y", "w", "h", "rx", "xf")}
    for p in got["mid"] + [got["land"], got["back"], got["land2"]]:
        have = {k: v for k, v in p["bars"][1].items() if k in ("x", "y", "w", "h", "rx", "xf")}
        assert have == want, ("3x -> '3 wafers' is the same value: the bar is the built one", have, want)
        assert all(f["xf"] is None for f in p["figs"]), "... and the figure is where the page wrote it"
        assert p["ghosts"] == []


@needs_browser
def test_the_ghost_is_drawn_only_when_the_row_names_it(read):
    assert read["halving"]["land"]["ghosts"] == [], "never by default"
    got = read["halving-ghost"]
    assert got["before"]["ghosts"] and got["before"]["ghosts"][0]["op"] == 0, "not before the compare"
    g = got["land"]["ghosts"][0]
    b0 = _bar(got["before"])
    assert g["op"] > 0.2 and g["fill"] == "none" and g["dash"], g
    assert abs(g["box"][1] - _f(b0["y"])) < UNIT_TOL, ("the ghost stands at the OLD height", g, b0)
    assert abs(g["box"][0] - _f(b0["x"])) < UNIT_TOL and abs(g["box"][2] - _f(b0["w"])) < UNIT_TOL, ("... across the bar's own width", g, b0)
    f = got["land"]["figs"][0]["box"]
    s = g["stage"]
    assert not (s[0] < f[0] + f[2] and f[0] < s[0] + s[2] and s[1] < f[1] + f[3] and f[1] < s[1] + s[3]),         ("the ghost never runs through the figure that rode down under it", s, f)


@needs_browser
def test_the_morph_is_a_pure_function_of_t(read):
    got = read["halving"]
    assert got["back"] == got["mid"][2], "a seek back lands the frame the play landed"
    assert got["land2"] == got["land"]
    cold = read["cold"]
    assert cold["bars"] == got["land"]["bars"] and cold["figs"] == got["land"]["figs"], "a cold seek lands the played frame"


# ---- the golden -------------------------------------------------------------------------------------------------

def test_the_halving_at_rest_is_a_committed_golden_surface():
    assert GOLDEN in G.SURFACES and GOLDEN in G.FRAME_T
    assert G.FRAME_T[GOLDEN] > LAND_T - 0.4, "read at rest, after the morph and the comparator's label"
    assert (RB.SOURCES / f"{GOLDEN}.timeline.json").exists() and (RB.SOURCES / f"{GOLDEN}.uris.json").exists()
    assert (RB.FRAMES / f"{GOLDEN}.png").exists(), "render_baseline.py --update bar-value-morph"
    tl = json.loads((RB.SOURCES / f"{GOLDEN}.timeline.json").read_text(encoding="utf-8"))
    kinds = [sp["kind"] for sp in tl["scenes"][0]["species"]]
    assert kinds == ["figure", "chart_to"] and tl["scenes"][0]["species"][1]["to"] == "compare"


@needs_browser
def test_the_golden_frame_is_unchanged():
    assert RB.check([GOLDEN]) == []
