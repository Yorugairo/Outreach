"""P69 T6 / R26-190 - A FIGURE LANDS ON A BARS PAGE, AND THE COMPARE MORPHS IT.

BACKLOG R26-190 (E99 s74, 2026-09-17): the engine dropped EVERY figure on a `builder story` (bars) page, because
`buildPerform` anchored a figure to the page's `linePts` - which a bars page never has (`nFig: 0`, `linePts: []`) -
so `paintCompare` found no figure and `chart_to compare, form melt, then splash` played nothing at its instant. The
order: the figure on a bars page anchors to ITS BAR'S TOP - the bar's own rect - as a line figure anchors to its
point; the compare then morphs it.

The three Steel and Paper H beats that need it are compiled here as fixtures (P69 T6 acceptance 3), their values
COPIED from the evidence objects (`ev-capex-ocf-94-bars-v1`, `ev-index-concentration-bars-v1`,
`ev-hbm-wafer-ratio-bars-v1`) so this file never depends on an untracked series on disk:
  row 17  the 94 bar with its figure written at the bar's top;
  row 18  the 20 bar's figure, halved by a `chart_to compare` (melt, then splash) into the 10 it would erase;
  row 21  the wafer ratio, 1 vs 3: the HBM bar's figure morphed by the same compare.
The comparator rows are fixture rows (T25/T26/T29 author the episode's own); their arithmetic is authored and the
compiler checks it here, as it would on any shot row (E77).

Line pages are pinned byte-identical by the `page-figure` and `compare-*` goldens (test_golden_frames.py).
The browser proof needs playwright + chromium and is skipped without them.
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
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

ASPECT = "16:9"                  # the H episode is long-form: its pages are stamped full-stage (R26-205)
FIG_AT, FIG_S = 8.0, 1.5         # the page has built (LP: its bars grow 4.4-7.4 s on a page entered at 0)
CMP_AT, CMP_S = 11.0, 2.4        # the compare's word - the same clock the `compare-morph` golden runs
LAND_T = CMP_AT + CMP_S + 0.4    # the comparator written whole

# ---- the three H objects, their values copied (P69 T14a's series files, read not edited) -------------------------

OBJ_94 = {"title": "Ninety-four cents of every dollar",
          "sub": "Hyperscaler capital spending as a share of their operating cash flow - PIMCO's projection for the next two years",
          "src": "PIMCO, AI Credit Expansion: Assessing the Micro and Macro Risks, Figure 3 - a projection, not an actual",
          "unit": "%", "domain": [0, 100],
          "hlines": [{"y": 100, "label": "every dollar from operations", "color": "deemph"}],
          "bars": [{"label": "Capex, next two years", "value": 94, "note": "94%", "color": "crimson"}]}
OBJ_20 = {"title": "One bet, a fifth of the index",
          "sub": "AI builders as a share of the S&P 500 - today, against their historical two-to-four percent",
          "src": "Figures via Bravos Research - S&P 500 weighting (attributed)",
          "unit": "%",
          "hlines": [{"y": 4, "label": "historically 2-4%", "color": "deemph"}, {"y": 2, "color": "deemph"}],
          "bars": [{"label": "AI builders, share of the S&P 500 today", "value": 20, "note": "20%", "color": "crimson"}]}
OBJ_13 = {"title": "Wafer capacity per gigabyte",
          "sub": "HBM against standard DRAM - stacking the dies takes about three times the silicon for the same gigabyte",
          "src": "Micron / SK hynix technical disclosures, via industry reporting - approximate ratio",
          "unit": "x",
          "bars": [{"label": "Standard DRAM", "value": 1, "note": "1x", "color": "deemph"},
                   {"label": "HBM (stacked dies)", "value": 3, "note": "about 3x", "color": "crimson"}]}


def _figure(text: str, index: int) -> dict:
    return {"kind": "figure", "at": FIG_AT, "dur": FIG_S, "text": text, "target": {"kind": "datum", "index": index}}


def _compare(metric: dict, comparator: dict, inputs: dict, derive: str, source: str) -> dict:
    return {"kind": "chart_to", "at": CMP_AT, "dur": CMP_S, "to": "compare", "form": "melt", "then": "splash",
            "hold": "metric", "metric": metric, "comparator": comparator, "inputs": inputs, "derive": derive,
            "source": source}


# name -> (object id, object, species, the bar the figure names)
FIXTURES = {
    "row17-94": ("fx-capex-ocf-94-bars", OBJ_94, [_figure("94%", 0)], 0),
    "row18-halving": ("fx-index-concentration-bars", OBJ_20, [
        _figure("20%", 0),
        _compare({"value": 20, "text": "20%", "label": "of the S&P 500"},
                 {"value": 10, "text": "10%", "label": "of the market, if they halve"},
                 {"share": 20}, "share / 2",
                 "[DERIVED: from ev-index-concentration-bars-v1, a fifth of the index falling by half, share / 2]")], 0),
    "row21-wafer": ("fx-hbm-wafer-ratio-bars", OBJ_13, [
        _figure("3x", 1),
        _compare({"value": 3, "text": "3x", "label": "HBM against standard DRAM"},
                 {"value": 3, "text": "3 wafers", "label": "for the gigabytes 1 wafer of DRAM makes"},
                 {"hbm": 3, "dram": 1}, "hbm / dram",
                 "[DERIVED: from ev-hbm-wafer-ratio-bars-v1, hbm / dram]")], 1),
}

# P69 T6c: two SHAPES for the cap alone - synthetic rows, no figure, never an H beat. Four bars draw 202 px at their
# natural pitch on the full stage (over the cap: they narrow, and their pitch cannot widen past the plot); five draw
# 162 px (under it: built exactly as before).
_SHAPE = {"title": "Shape", "sub": "Synthetic bars for the width cap; not a figure about the world",
          "src": "Synthetic - the cap's own fixture", "unit": "%"}
CAP_SHAPES = {
    "cap-4": ("fx-cap-four-bars", dict(_SHAPE, bars=[{"label": f"Row {i + 1}", "value": 10 + 5 * i} for i in range(4)]), [], None),
    "cap-5": ("fx-cap-five-bars", dict(_SHAPE, bars=[{"label": f"Row {i + 1}", "value": 10 + 5 * i} for i in range(5)]), [], None),
}


def fixture_world(name: str, tmp: Path, species: list[dict] | None = None) -> tuple[dict, str, list[dict]]:
    """The fixture's episode on disk under `tmp`, its world as the compiler builds it (stamped full-stage, as a
    16:9 build stamps every page), its plate id and its species (a copy)."""
    oid, obj, authored, _bar = {**FIXTURES, **CAP_SHAPES}[name]
    species = authored if species is None else species
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    plate = f"ledger:{oid}:bars"
    world = B.world_for_plate(plate, (0, 0, 0), tmp)
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world, plate, copy.deepcopy(species)


def fixture_timeline(name: str, tmp: Path, species: list[dict] | None = None) -> tuple[dict, dict]:
    world, _plate, species = fixture_world(name, tmp, species)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    return G._timeline("P69 T6: " + name, scenes, {}, ASPECT), G._base_uris()


PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, PF = st.perform || { figures: [] };
  const bars = (st.marks || []).filter(m => m.role === 'bar').map(m => m.geom);
  const box = (el) => { try { const b = el.getBBox(); return [b.x, b.y, b.width, b.height]; } catch (e) { return null; } };
  const stage = document.getElementById('stage').getBoundingClientRect();
  const onStage = (el) => { const r = el.getBoundingClientRect(); return r.width > 0 ? [r.x - stage.x, r.y - stage.y, r.width, r.height] : null; };
  const vals = (st.bars || []).map(b => ({ op: b.val ? +(b.val.getAttribute('opacity') || 0) : 0, box: b.val ? box(b.val) : null,
                                           size: b.val ? parseFloat(getComputedStyle(b.val).fontSize) : 0,
                                           fill: b.val ? (b.val.style.fill || '') : '' }));
  const rules = (st.hlines || []).map(r => r.y);
  const figs = (PF.figures || []).map(fg => {
    const bb = box(fg.label);
    const P = fg.__compare, Bl = P && P.ball;
    const ink = [fg.label, fg.sub, P && P.ghost, P && P.sub].filter(el => el && +(el.getAttribute('opacity') || 1) > 0.01
                  && (el.textContent || '').trim()).map(onStage).filter(Boolean);
    const op = (el) => el ? +(el.getAttribute('opacity') || 0) : 0, d = (el) => el ? (el.getAttribute('d') || '').trim().length : 0;
    return { D: fg.D, x: fg.x, y: fg.y, fits: fg.fits, idx: fg.idx, fs: fg.fs, anchor: fg.anchor || null, stageInk: ink,
             opacity: +(fg.g.getAttribute('opacity') || 0), text: (fg.label.textContent || '').replace(/\\u00a0/g, ' '),
             glyphs: fg.lg.map(ts => +(ts.getAttribute('opacity') || 0)), box: bb,
             ink: Bl ? { d: d(Bl.ink), op: op(Bl.ink) } : null, drop: Bl ? { d: d(Bl.drop), op: op(Bl.drop) } : null };
  });
  const sc = st.scale || {};
  /* P69 T6c: each bar's width ON THE STAGE, and each category label's lines and box */
  const barPx = (st.bars || []).map(b => b.bar.getBoundingClientRect().width);
  const labs = (st.bars || []).map(b => ({ lines: b.lab.querySelectorAll('tspan').length || 1, box: box(b.lab),
                                           text: (b.lab.textContent || '') }));
  return { kind: st.kind, linePts: (st.linePts || []).length, bars, vals, rules, figs, plot: [sc.x0, sc.x1], barPx, labs };
}"""


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


class Player:
    """One fixture served in the player at the stage's native size: `at(t)` seeks and probes, `png(t)` shoots."""

    def __init__(self, name: str, species: list[dict] | None = None):
        from playwright.sync_api import sync_playwright
        self._td = tempfile.TemporaryDirectory()
        tmp = Path(self._td.name)
        timeline, uris = fixture_timeline(name, tmp / "ep", species)
        html = tmp / "bars.html"
        html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
        self.w, self.h = RB.STAGE[ASPECT]
        self._srv, port = RB.serve(html.parent)
        self._pw = sync_playwright().start()
        self._br = self._pw.chromium.launch(headless=True)
        self.page = self._br.new_context(viewport={"width": self.w, "height": self.h}).new_page()
        self.errs: list[str] = []
        self.page.on("pageerror", lambda e: self.errs.append(str(e)))
        self.page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, self.w, self.h)

    def at(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE)

    def png(self, t: float) -> bytes:
        return RB.frame_png(self.page, t, (self.w, self.h))

    def close(self) -> None:
        self._br.close(); self._pw.stop(); self._srv.shutdown(); self._td.cleanup()


# ---- the compiler: the three beats are rows it accepts ---------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_the_three_h_beats_compile_as_bars_pages(name, tmp_path):
    world, plate, species = fixture_world(name, tmp_path)
    assert world["page"]["builder"] == "story", "a shares object drawn as bars is a STORY page"
    assert world["page"].get("full_stage") is True, "and a 16:9 build stamps it full-stage (R26-205)"
    assert B.validate_species(species, (0, 0, 0), plate) == []


# ---- the player: the figure lands at its bar's top, and the compare morphs it ----------------------------------------


def _meets(a: list[float], b: list[float]) -> bool:
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


@needs_browser
@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_a_figure_on_a_bars_page_is_written_at_its_bars_top(name):
    """R26-190's ORDER: the figure anchors to the bar its target names - that bar's own rect - as a line figure
    anchors to its point. The datum is the bar's top (the mark's `cx`, `end`: the one datum rule `lpMarkDatumOn`
    already reads for a bar), and the number stands where the bar's own VALUE stood - centred over the bar, above its
    top with air (the parent's frame read: never beside the bar, where a lone bar's side is the tick column), never on
    the bar's own ink, written whole by the hand."""
    P = Player(name)
    try:
        want = FIXTURES[name][3]
        before = P.at(FIG_AT - 0.5)
        assert before["kind"] == "story" and before["linePts"] == 0, "a bars page has no line points - the cause"
        assert len(before["figs"]) == 1, f"nFig: {len(before['figs'])} - the bars page dropped its figure (R26-190)"
        assert before["figs"][0]["opacity"] == 0, "and it is not on the page before its word"
        s = P.at(FIG_AT + FIG_S + 0.5)
        fg, bar = s["figs"][0], s["bars"][want]
        assert fg["idx"] == want and fg["anchor"] == "middle", "the figure names the bar its target names, centred on it"
        assert abs(fg["D"][0] - bar["cx"]) < 0.05 and abs(fg["D"][1] - bar["end"]) < 0.05, (fg["D"], bar)
        assert fg["opacity"] == 1 and all(g == 1 for g in fg["glyphs"]), "the hand has written the number whole"
        box = fg["box"]
        assert box and box[2] > 0, "the written figure has ink"
        assert abs((box[0] + box[2] / 2) - bar["cx"]) < 1.0, f"centred on its bar: {box} vs cx {bar['cx']}"
        rect = [bar["x"], bar["y"], bar["w"], bar["h"]]
        if any(ry < bar["end"] for ry in s["rules"]):   # a rule the bar does not reach: the number goes INSIDE (the 94)
            assert box[1] >= bar["end"] and box[1] + box[3] <= bar["base"], f"inside its bar: {box} vs {rect}"
        else:
            assert not _meets(box, rect), f"never on the bar's own ink: {box} over {rect}"
            assert box[1] + box[3] <= bar["end"], f"and above its top: {box} vs top {bar['end']}"
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
def test_the_bars_own_value_yields_while_its_figure_stands_and_returns_when_it_leaves():
    """One number, not two (the parent's frame read: "94% 94%"): the bar's value is lit before the figure's word,
    gone while the figure stands, and lit again when the figure leaves (R26-219's leave clock, `leave_at`)."""
    leave_at, leave_s = FIG_AT + FIG_S + 2.0, 0.5
    species = [dict(FIXTURES["row17-94"][2][0], leave_at=leave_at, leave_s=leave_s)]
    P = Player("row17-94", species)
    try:
        assert P.at(FIG_AT - 0.5)["vals"][0]["op"] == 1, "the bar's own number is written before the figure's word"
        mid = P.at(FIG_AT + FIG_S * 0.3)["vals"][0]["op"]
        assert 0 < mid < 1, f"it yields on the figure's own write clock, not by a cut: {mid}"
        assert P.at(FIG_AT + FIG_S + 0.5)["vals"][0]["op"] == 0, "while the figure stands the value is gone"
        back = P.at(leave_at + leave_s + 0.2)
        assert back["figs"][0]["opacity"] == 0 and back["vals"][0]["op"] == 1, "the figure left: the value is back"
        assert P.at(FIG_AT + FIG_S + 0.5)["vals"][0]["op"] == 0, "and a seek back hides it again (pure in t)"
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_everything_a_bars_figure_writes_stays_inside_the_text_safe_box(name):
    """The parent's frame read: the halving's comparator label started ~9 px from the stage edge. Every line the
    figure writes - its number, the comparator, the held metric and the label beneath - is inside SAFE_BOX."""
    sx, sy, sw, sh = LPG.SAFE_BOX[ASPECT]
    P = Player(name)
    try:
        for t in (FIG_AT + FIG_S + 0.5, LAND_T):
            fg = P.at(t)["figs"][0]
            assert fg["stageInk"], "the figure writes something"
            for r in fg["stageInk"]:
                assert sx <= r[0] and r[0] + r[2] <= sx + sw and sy <= r[1] and r[1] + r[3] <= sy + sh, \
                    f"t={t}: {r} leaves the text-safe box {(sx, sy, sw, sh)}"
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
def test_a_bars_value_label_clears_every_comparator_rule():
    """The parent's frame read: the 94 page's "94%" sat ON its dashed 100 % rule, struck through. A value clears every
    `axes.hlines` rule by half of its own size (M28's air) - checked on the page with no figure on it."""
    P = Player("row17-94", [])
    try:
        s = P.at(FIG_AT)
        assert s["rules"], "the fixture draws its rule"
        for v in s["vals"]:
            assert v["op"] == 1 and v["box"], v
            top, bot = v["box"][1], v["box"][1] + v["box"][3]
            for ry in s["rules"]:
                gap = min(abs(ry - top), abs(ry - bot))
                assert not (top < ry < bot), f"the rule at {ry} strikes the value {v['box']}"
                assert gap >= 0.25 * v["size"], f"the value sits {gap:.1f} off the rule at {ry} ({v['box']})"
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
@pytest.mark.parametrize("figure", [False, True], ids=["value", "figure"])
def test_on_the_94_page_the_number_stays_under_the_100_rule_inside_its_bar(figure):
    """The parent's second frame read: lifted ABOVE the dashed 100 % rule, "94%" read as more than 100 (E28: position
    is meaning). A number never stands past a rule its value does not pass: with no room between the bar's top and
    the rule, the value - and the figure that takes its place - is written INSIDE the bar, below the rule and at or
    under the bar's top, in an ink that is not the bar's own fill."""
    P = Player("row17-94", None if figure else [])
    try:
        s = P.at(FIG_AT + FIG_S + 0.5)
        bar, ry = s["bars"][0], min(s["rules"])
        assert ry < bar["end"], "the fixture: the 100 % rule is above the 94 bar's top"
        box = s["figs"][0]["box"] if figure else s["vals"][0]["box"]
        assert box and box[2] > 0, box
        assert box[1] > ry, f"the number sits under the 100 % rule, never above it: {box} vs rule {ry}"
        assert box[1] >= bar["end"] - 0.5 and box[1] + box[3] <= bar["base"], \
            f"inside its bar or at its top: {box} vs top {bar['end']} base {bar['base']}"
        if not figure:
            assert s["vals"][0]["op"] == 1 and s["vals"][0]["fill"], "and it is printed, in an ink of its own"
        assert not P.errs, P.errs
    finally:
        P.close()


ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
BAR_GAP = 0.34   # buildLedgerBars' own `gap`: the share of a bar's pitch left as air on an uncapped page


def _lpbar() -> dict:
    """The engine's bar-width cap (P69 T6c / E99 s96): a width in STAGE px and the bar/pitch ratio, read off the
    engine, never retyped."""
    m = re.search(r"const LPBAR = Object\.freeze\(\{ W_PX: ([\d.]+), PITCH_RATIO: ([\d.]+) \}\)",
                  ENGINE.read_text(encoding="utf-8"))
    assert m, "the engine names its bar-width cap in stage px (LPBAR.W_PX, LPBAR.PITCH_RATIO)"
    return {"W_PX": float(m.group(1)), "PITCH_RATIO": float(m.group(2))}


def test_the_cap_is_bravos_measured_hero_bar():
    """E99 s96: the cap is Bravos's MEASURED hero bar - 196 px on a 1920 stage at 0.44 of its pitch
    (BRAVOS-LONGFORM-CHART-SPEC.md, bubbles 0008: 196 / 442 px)."""
    cap = _lpbar()
    assert cap["W_PX"] == 196 and cap["PITCH_RATIO"] == 0.44, cap


@needs_browser
@pytest.mark.parametrize("name", ["row17-94", "row18-halving", "row21-wafer", "cap-4"])
def test_a_bar_is_capped_at_the_measured_width_and_a_short_row_stands_centred(name):
    """The operator: "that bar can't be that wide ... it reads like a giant block", then "The two bar width is also
    still way too much" (E99 s96). A bar is never wider than LPBAR.W_PX on the stage; a row that would draw wider
    narrows to exactly that width, stands CENTRED in the plot as a group, with even gaps at the measured bar/pitch
    ratio - or at the plot's own pitch when that ratio would not fit. The value, the figure and the category label
    follow the bar."""
    cap = _lpbar()
    P = Player(name)
    try:
        s = P.at(FIG_AT + FIG_S + 0.5)
        x0, x1 = s["plot"]
        bars, n = s["bars"], len(s["bars"])
        for px in s["barPx"]:
            assert abs(px - cap["W_PX"]) < 0.5, f"a bar {px:.1f} px wide on the stage, the cap is {cap['W_PX']} px"
        left, right = min(b["x"] for b in bars), max(b["x"] + b["w"] for b in bars)
        assert abs((left + right) / 2 - (x0 + x1) / 2) < 0.5, f"the row [{left:.1f}, {right:.1f}] is centred in [{x0}, {x1}]"
        if n > 1:
            gaps = [b2["x"] - (b1["x"] + b1["w"]) for b1, b2 in zip(bars, bars[1:])]
            assert max(gaps) - min(gaps) < 0.5, f"even gaps: {gaps}"
            pitch = bars[1]["x"] - bars[0]["x"]
            want = min((x1 - x0) / n, bars[0]["w"] / cap["PITCH_RATIO"])
            assert abs(pitch - want) < 0.1, f"the pitch {pitch:.2f}: the measured ratio's, or the plot's when it will not fit ({want:.2f})"
            assert right - left <= x1 - x0 + 0.05, "the row never leaves its plot"
        for b, v in zip(bars, s["vals"]):
            if v["box"] and v["op"] > 0:
                assert abs((v["box"][0] + v["box"][2] / 2) - b["cx"]) < 1.0, f"the value is centred on its bar: {v['box']} vs {b['cx']}"
        for b, lab in zip(bars, s["labs"]):
            assert lab["box"] and abs((lab["box"][0] + lab["box"][2] / 2) - b["cx"]) < 1.0, f"the name follows its bar: {lab}"
        if FIXTURES.get(name):
            fg, bar = s["figs"][0], bars[FIXTURES[name][3]]
            assert abs((fg["box"][0] + fg["box"][2] / 2) - bar["cx"]) < 1.0, "the figure follows its bar's new rect"
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
@pytest.mark.parametrize("name", ["row18-halving", "row21-wafer"])
def test_a_category_label_wider_than_its_capped_bar_wraps_to_two_lines_and_meets_no_neighbour(name):
    """E99 s96 (2): a category label wider than its narrowed bar is written on TWO lines, broken at a word, rather
    than running into its neighbour's column; no two names meet."""
    P = Player(name)
    try:
        s = P.at(FIG_AT + FIG_S + 0.5)
        bars, labs = s["bars"], s["labs"]
        wrapped = 0
        for b, lab in zip(bars, labs):
            if lab["lines"] == 2:
                wrapped += 1
                continue
            assert lab["box"][2] <= b["w"] + 0.5 or " " not in lab["text"].strip(), \
                f"a one-line name {lab['box'][2]:.1f} wide under a {b['w']:.1f} bar: it wraps ({lab['text']!r})"
        assert wrapped, f"the fixture carries a name wider than its bar: {labs}"
        for a, c in zip(labs, labs[1:]):
            assert a["box"][0] + a["box"][2] <= c["box"][0], f"two names meet: {a} / {c}"
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
def test_a_row_narrower_than_the_cap_is_built_as_before():
    """Five bars draw 162 px at their natural pitch on the full stage: under the cap, so the row keeps the plot's
    own pitch and the 0.34 gap, from the plot's left edge - exactly the layout it had before the cap (the goldens
    hold the bytes of every such page)."""
    cap = _lpbar()
    P = Player("cap-5")
    try:
        s = P.at(FIG_AT + FIG_S + 0.5)
        x0, x1 = s["plot"]
        bars, n = s["bars"], len(s["bars"])
        pitch = (x1 - x0) / n
        assert all(px < cap["W_PX"] for px in s["barPx"]), s["barPx"]
        for i, b in enumerate(bars):
            assert abs(b["w"] - round(pitch * (1 - BAR_GAP), 1)) < 0.051, (i, b["w"], pitch)
            assert abs(b["x"] - round(x0 + pitch * (i + BAR_GAP / 2), 1)) < 0.051, (i, b["x"])
        assert all(lab["lines"] == 1 for lab in s["labs"]), "an uncapped page wraps no name"
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
@pytest.mark.parametrize("name", ["row18-halving", "row21-wafer"])
def test_the_compare_melts_the_bars_figure_then_splashes_and_lands_on_the_comparator(name):
    """`chart_to compare, form melt, then splash` at its instant: the written figure's outlines are on stage through
    the window (the melt, the ball, the burst), and at the landing the figure's own <text> is the comparator."""
    P = Player(name)
    try:
        row = FIXTURES[name][2][1]
        for u in (0.15, 0.45):
            s = P.at(CMP_AT + CMP_S * u)
            ink = (s["figs"] or [{}])[0].get("ink")
            assert ink and ink["d"] > 0 and ink["op"] == 1, \
                f"u={u}: the compare paints nothing at its instant (nFig: {len(s['figs'])}, ink {ink})"
        pre = P.at(CMP_AT - 0.2)
        assert pre["figs"][0]["text"] == row["metric"]["text"], "a seek back: the quoted figure stands before the word"
        late = P.at(CMP_AT + CMP_S * 0.8)
        f = late["figs"][0]
        assert (f["ink"]["d"] > 0 and f["ink"]["op"] == 1) or f["drop"]["d"] > 0, f"u=0.8: the splash is on the page ({f})"
        land = P.at(LAND_T)
        fg = land["figs"][0]
        assert fg["text"].strip() == row["comparator"]["text"], (fg["text"], row["comparator"]["text"])
        assert fg["ink"]["op"] == 0, "the outlines are gone: the landed frame is the page's own type"
        assert not P.errs, P.errs
    finally:
        P.close()
