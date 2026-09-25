"""P69 T64 - THE STACKED BAR OF VALUES, AND THE STACKED-BAR-PLUS-LINE COMBO (E99 s110 (1); s100; s102; s106; s109).

E99 s110 (1): "allowed, I think one legitimate case I can think of in finance is it's usually like when you're looking
at financial metrics against business metrics or something like that, where you could have a stacked bar and a line."
A stacked bar of values is valid under s109's honesty tests (true proportion, every segment's figure written, the total
written); its home case is the COMBO - stacked bars with a line over them, each on its own labelled scale per s102 when
their units differ.

  (1) THE FIELD      a bar datum may carry `segments: [{name, value, value_string?, color?}]` (SEGMENTS_MIN..MAX); the
                     bar's own `value` is the TOTAL, and the page carries the segments per bar plus ONE key (name,
                     colour) in the stack's order. Every other bar key the form does not know is refused BY NAME - a
                     misspelt `segmnts` was silently dropped before (R26-307)
  (2) HONESTY        refused: segments that do not sum to the written total (within the figures' own rounding), a
                     negative or a zero segment (the stack stands bottom-up from zero - there is no signed baseline),
                     a range, members and segments on one bar, a breakthrough, a panel's or a tier's bars, a variant that
                     is not bars, names or order that change between bars, a name in two colours, a segment in a unit
                     that is not the page's (two units on one axis); a segment too thin for its figure is a WARN with
                     its numbers - its figure takes a leader (s106)
  (3) THE COMBO      stacked bars + ONE line: the line shares the bars' scale when its unit is theirs, and takes its OWN
                     right axis when it differs (`line_unit`) - then both axes are named (`ylabel`, `line_label`) and
                     the right one is written in the line's colour (s102 (b)(c)); `tiers: true`, a second line, and a
                     line in a segment's colour are refused
  (4) THE ROW        a stacked page takes park and nothing that moves, re-values or re-draws its bars; never a prism
  (5) THE PAINT      each segment drawn true to its value inside its bar, bottom-up in the key's order and colours, its
                     figure written (inside, or beside on a leader), the total over the bar, the key once; the combo's
                     line on its own labelled scale
  (6) OFF            a page with no segments is the page it was

Fixtures are READ off committed, sourced objects, never typed: ev-capex-funding-v1 (Epoch AI, company filings - the five
builders' operating cash and cash capital spending) and cbo-interest-revenue (CBO Monthly Budget Review, 9 Sep 2026).
The browser half needs playwright + chromium.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
PROJECTS = ROOT / "content/video_engine/projects/systems-and-blowups"


def _obj(base: dict, **patch) -> dict:
    o = copy.deepcopy(base)
    o.update(patch)
    return o


FUNDING = G.stacked_funding_series()   # the combo: operating cash = capex + what is left, the capex share as the line
OUTLAYS = G.stacked_outlays_series()   # the bars page: outlays = paid by revenue + borrowed


def _bars_only(o: dict) -> dict:
    """The combo's stacks alone - a BARS page of the same three stacked bars."""
    return {k: copy.deepcopy(v) for k, v in o.items() if k not in ("series", "line_unit", "line_label")}


# ---- (1) the field ---------------------------------------------------------------------------------------------------

def test_the_fixtures_are_read_off_the_committed_objects():
    fund = json.loads((PROJECTS / "steel-and-paper/evidence/objects/ev-capex-funding-v1.series.json").read_text(encoding="utf-8"))
    ocf = dict((round(x, 3), y) for x, y in next(s for s in fund["series"] if s.get("name") == "CASH FROM OPERATIONS")["pts"])
    capex = dict((round(x, 3), y) for x, y in next(s for s in fund["series"] if s.get("name") == "CASH CAPEX")["pts"])
    for bar, x in zip(FUNDING["bars"], (2024.125, 2025.125, 2026.125)):
        assert float(bar["value"]) == ocf[x], "the bar is the quarter's operating cash, as filed"
        assert float(bar["segments"][0]["value"]) == capex[x], "its first segment the quarter's cash capex, as filed"
    cbo = json.loads((PROJECTS / "american-debt-trap/evidence/objects/cbo-interest-revenue.series.json").read_text(encoding="utf-8"))
    f = cbo["facts"]
    assert OUTLAYS["bars"][0]["value"] == f["outlays_usd_billions"]
    assert [s["value"] for s in OUTLAYS["bars"][0]["segments"]] == [f["revenue_usd_billions"], f["deficit_usd_billions"]]


def test_a_bar_key_the_form_does_not_know_is_refused_by_name():
    o = _bars_only(FUNDING)
    o["bars"][0]["segmnts"] = o["bars"][0].pop("segments")
    errs = LPG.validate(o, "bars")
    assert any("segmnts" in e and "bars[0]" in e and "segments" in e for e in errs), errs


@pytest.mark.parametrize("where", ["panel", "tier"])
def test_a_nested_bar_is_held_to_the_same_fields(where):
    bars = [{"label": "a", "value": 1, "color": "teal", "valu": 2}, {"label": "b", "value": 2, "color": "teal"}]
    if where == "panel":
        o = {"title": "t", "src": "s", "panels": [{"sub": "p", "builder": "bars", "unit": "%", "bars": bars},
                                                   {"sub": "q", "builder": "bars", "unit": "%", "bars": copy.deepcopy(bars[1:]) * 2}]}
        errs = LPG.validate(o, "line")
    else:
        o = {"title": "t", "src": "s", "tiers": [{"name": "A", "unit": "%", "bars": bars},
                                                  {"name": "B", "unit": "%", "bars": copy.deepcopy(bars[1:]) * 2}]}
        errs = LPG.validate(o, "tiers")
    assert any("'valu'" in e for e in errs), errs


def test_every_bar_on_disk_is_a_bar_the_form_knows():
    """The allowlist is the record's: every bar datum in a committed evidence object passes it."""
    bad = []
    for p in sorted(PROJECTS.rglob("*.series.json")):
        try:
            obj = json.loads(p.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        for b in (obj.get("bars") or []) if isinstance(obj, dict) else []:
            if isinstance(b, dict):
                bad += [f"{p.name}: {k}" for k in b if k not in LPG.BAR_FIELDS]
    assert not bad, bad


def test_a_stacked_bar_carries_its_segments_and_the_page_its_key():
    assert LPG.validate(OUTLAYS, "bars") == []
    spec = LPG.build_spec(OUTLAYS, "bars", 0, "right")
    assert spec["builder"] == "story"
    assert spec["values"] == [6812.0] and spec["value_strings"] == ["6812"], "the bar is its TOTAL, written"
    assert spec[LPG.SEGMENTS_KEY] == [[{"name": "Paid by revenue", "value": 4845.0, "value_string": "4845", "color": "teal"},
                                       {"name": "Borrowed", "value": 1967.0, "value_string": "1967", "color": "crimson"}]]
    assert spec["segment_key"] == [{"name": "Paid by revenue", "color": "teal"}, {"name": "Borrowed", "color": "crimson"}]


def test_the_colours_follow_the_key_and_a_bar_without_segments_is_null():
    o = _bars_only(FUNDING)
    o["bars"].append({"label": "Plain", "value": 50, "color": "deemph"})
    spec = LPG.build_spec(o, "bars", 0, "right")
    assert spec["segments"][3] is None and len(spec["segments"]) == 4
    assert [s["color"] for s in spec["segments"][0]] == [k["color"] for k in spec["segment_key"]]
    assert all([s["name"] for s in segs] == ["Cash capex", "Left over"] for segs in spec["segments"][:3])
    assert spec["segments"][2][1]["value_string"] == "9.5", "a figure is written as the file wrote it"


def test_a_page_without_segments_is_the_spec_it_was():
    plain = _bars_only(OUTLAYS)
    plain["bars"][0].pop("segments")
    spec = LPG.build_spec(plain, "bars", 0, "right")
    assert "segments" not in spec and "segment_key" not in spec and "warnings" not in spec
    assert LPG.validate(plain, "bars") == []


def test_the_default_inks_are_e67s_cycle_by_the_segments_place():
    o = _bars_only(OUTLAYS)
    for s in o["bars"][0]["segments"]:
        s.pop("color", None)
    spec = LPG.build_spec(o, "bars", 0, "right")
    assert [k["color"] for k in spec["segment_key"]] == list(LPG.SEGMENT_INKS[:2])


# ---- (2) honesty -----------------------------------------------------------------------------------------------------

def _outlays(**seg0) -> dict:
    o = copy.deepcopy(OUTLAYS)
    o["bars"][0]["segments"][0].update(seg0)
    return o


@pytest.mark.parametrize("patch,pattern", [
    ({"value": 4800}, r"segments sum to 6767, and the bar's written total is 6812"),
    ({"value": -4845}, r"negative segment .*signed baseline"),
    ({"value": 0}, r"zero"),
    ({"value": "lots"}, r"not numeric"),
    ({"unit": "%"}, r"two units on one axis"),
    ({"share": 71}, r"'share' is not a segment field"),
    ({"name": ""}, r"needs a name"),
])
def test_a_segment_that_is_not_true_is_refused_by_name(patch, pattern):
    errs = LPG.validate(_outlays(**patch), "bars")
    assert any(re.search(pattern, e) for e in errs), errs


def test_the_sum_holds_within_the_written_figures_own_rounding():
    o = _bars_only(OUTLAYS)
    o["bars"][0].update(value=100.0, segments=[{"name": "a", "value": 33.3}, {"name": "b", "value": 33.3},
                                               {"name": "c", "value": 33.3}])
    assert LPG.validate(o, "bars") == [], "three thirds written 33.3 each are 99.9 of 100.0 - inside half a unit each"
    o["bars"][0]["segments"][2]["value"] = 33.0
    assert any("sum to" in e for e in LPG.validate(o, "bars"))
    f = _bars_only(FUNDING)
    assert LPG.validate(f, "bars") == [], "0.1-place figures (46.0 + 58.5 = 104.5) sum exactly in decimal"


@pytest.mark.parametrize("segs,pattern", [
    ([{"name": "all", "value": 6812}], r"1 segment\(s\)"),
    ([{"name": f"s{k}", "value": 1} for k in range(5)], r"5 segment\(s\)"),
    ([{"name": "a", "value": 3406}, {"name": "A", "value": 3406}], r"'a' twice"),
    ("x", r"a list of"),
])
def test_the_stack_is_two_to_four_named_segments(segs, pattern):
    o = copy.deepcopy(OUTLAYS)
    o["bars"][0]["segments"] = segs
    errs = LPG.validate(o, "bars")
    assert any(re.search(pattern, e) for e in errs), errs


def test_the_order_and_the_colours_are_the_pages_one_key():
    o = _bars_only(FUNDING)
    o["bars"][1]["segments"].reverse()
    assert any("order" in e and "bars[1]" in e for e in LPG.validate(o, "bars"))
    o = _bars_only(FUNDING)
    o["bars"][2]["segments"][0]["color"] = "cobalt"
    assert any("'Cash capex'" in e and "colour" in e for e in LPG.validate(o, "bars"))
    o = _bars_only(FUNDING)
    for bar in o["bars"]:
        bar["segments"][1]["color"] = bar["segments"][0]["color"]
    assert any("one colour" in e for e in LPG.validate(o, "bars")), "two segments in one ink read as one"


def test_a_stack_is_refused_where_it_cannot_stand():
    rng = copy.deepcopy(OUTLAYS)
    rng["bars"][0]["value"] = [6800, 6812]
    assert any("RANGE" in e and "segments" in e for e in LPG.validate(rng, "bars"))
    both = copy.deepcopy(OUTLAYS)
    both["bars"][0]["members"] = [{"name": "a"}, {"name": "b"}]
    assert any("members and segments" in e for e in LPG.validate(both, "bars"))
    bt = _obj(OUTLAYS, overflow="burst", domain=[0, 5000])
    assert any("breakthrough" in e and "segments" in e for e in LPG.validate(bt, "bars"))
    assert any("segments" in e and "'progress'" in e for e in LPG.validate(OUTLAYS, "progress"))
    neg = copy.deepcopy(OUTLAYS)
    neg["bars"][0]["value"] = -6812
    assert any("negative" in e for e in LPG.validate(neg, "bars"))


def test_a_stack_is_a_bars_pages_or_a_combos_and_never_a_panels_or_a_tiers():
    seg = copy.deepcopy(OUTLAYS["bars"][0])
    o = {"title": "t", "src": "s", "panels": [{"sub": "p", "builder": "bars", "unit": "$", "bars": [seg]},
                                               {"sub": "q", "builder": "bars", "unit": "$", "bars": [{"label": "x", "value": 1, "color": "teal"}]}]}
    assert any("segments" in e and "panels[0]" in e for e in LPG.validate(o, "line"))
    o = {"title": "t", "src": "s", "tiers": [{"name": "A", "unit": "$", "bars": [seg]},
                                              {"name": "B", "unit": "%", "bars": [{"label": "Outlays", "value": 1, "color": "teal"}]}]}
    assert any("segments" in e and "tiers[0]" in e for e in LPG.validate(o, "tiers"))


def test_a_segment_too_thin_for_its_figure_is_a_warn_with_its_numbers():
    spec = LPG.build_spec(_bars_only(FUNDING), "bars", 0, "right")
    warns = LPG.segment_fit_warnings(spec, "16:9")
    thin = [w for w in warns if "'Left over'" in w and "bar 2" in w]
    assert len(thin) == 1, warns
    assert thin[0].startswith("WARN segment:") and "leader" in thin[0] and re.search(r"\d+ px", thin[0]), thin[0]
    assert not [w for w in warns if "'Cash capex'" in w], "a tall segment holds its own figure"
    assert LPG.segment_fit_warnings(LPG.build_spec(OUTLAYS, "bars", 0, "right"), "16:9") == []


# ---- (3) the combo ---------------------------------------------------------------------------------------------------

def test_the_combo_lays_one_line_over_its_stacks_on_its_own_labelled_scale():
    assert LPG.validate(FUNDING, "bars") == []
    spec = LPG.build_spec(FUNDING, "bars", 2, "right")
    assert spec["builder"] == "combo"
    assert spec["line_unit"] == "%" and spec["line_label"] == FUNDING["line_label"] and spec["unit"] == "$"
    assert spec["axes"]["ylabel"] == FUNDING["ylabel"], "the bars' axis is named"
    assert len(spec["segments"]) == 3 and all(len(s) == 2 for s in spec["segments"])
    assert [p[1] for p in spec["series"][0]["pts"]] == [44, 65, 94]


@pytest.mark.parametrize("drop,pattern", [("line_label", r"line_label"), ("ylabel", r"ylabel"), ("unit", r"`unit`")])
def test_two_units_name_both_axes(drop, pattern):
    o = copy.deepcopy(FUNDING)
    o.pop(drop)
    errs = LPG.validate(o, "bars")
    assert any(re.search(pattern, e) and "axis" in e for e in errs), errs


def test_one_unit_is_one_axis():
    o = copy.deepcopy(FUNDING)
    for k in ("line_unit", "line_label"):
        o.pop(k)
    assert LPG.validate(o, "bars") == [], "the line shares the bars' scale: no second axis to name"
    o["line_unit"] = "$"
    assert LPG.validate(o, "bars") == []


def test_what_a_stacked_combo_may_not_carry():
    two = copy.deepcopy(FUNDING)
    two["series"].append(dict(copy.deepcopy(two["series"][0]), name="OTHER", color="cobalt"))
    assert any("ONE line" in e for e in LPG.validate(two, "bars"))
    tiers = _obj(FUNDING, tiers=True)
    assert any("tiers" in e and "segments" in e for e in LPG.validate(tiers, "bars"))
    clash = copy.deepcopy(FUNDING)
    clash["series"][0]["color"] = clash["bars"][0]["segments"][1]["color"]
    assert any("colour" in e and "line" in e for e in LPG.validate(clash, "bars"))
    unit = copy.deepcopy(FUNDING)
    unit["series"][0]["unit"] = "$"
    assert any("two units on one axis" in e for e in LPG.validate(unit, "bars"))


def test_a_combo_without_segments_is_untouched():
    plain = copy.deepcopy(FUNDING)
    for b in plain["bars"]:
        b.pop("segments")
    plain.pop("line_label")
    assert LPG.validate(plain, "bars") == [], "the P47 T9 combo: its right axis in line_unit, no new obligation"
    spec = LPG.build_spec(plain, "bars", 2, "right")
    assert "segments" not in spec and "line_label" not in spec


# ---- (4) the row -----------------------------------------------------------------------------------------------------

def _world(obj: dict, tmp: Path, opt: str = "", aspect: str = "16:9", oid: str = "fx-stack", variant: str = "bars") -> dict:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    saved = B.ASPECT
    B.ASPECT = aspect
    try:
        world = B.world_for_plate(f"ledger:{oid}:{variant}{opt}", (0, 0, 0), tmp)
        if aspect == "16:9":
            B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


def test_the_compiler_carries_the_stack_and_its_warn(tmp_path):
    world = _world(_bars_only(FUNDING), tmp_path)
    page = world["page"]
    assert page["segments"][0][0]["name"] == "Cash capex" and page["segment_key"][1]["name"] == "Left over"
    assert any(w.startswith("WARN segment:") and "'Left over'" in w for w in page.get("warnings", [])), page.get("warnings")
    combo = _world(FUNDING, tmp_path / "c")["page"]
    assert combo["builder"] == "combo" and combo["line_label"] == FUNDING["line_label"]


def test_a_stacked_page_takes_park_and_nothing_that_moves_its_bars(tmp_path):
    world = _world(OUTLAYS, tmp_path)
    B.check_segments(world, [{"kind": "chart_to", "to": "park", "at": 9.0, "dur": 0.8, "scale": 0.7}])
    for verb in ("rescale", "compare", "morph", "remake", "extend", "recast"):
        with pytest.raises(ValueError, match=r"stacked"):
            B.check_segments(world, [{"kind": "chart_to", "to": verb, "at": 9.0, "dur": 0.8, "state": 1}])


def test_a_stacked_page_is_not_a_prism_and_may_be_soft(tmp_path):
    with pytest.raises(ValueError, match=r"extruded_bar.*stack|stack.*extruded_bar"):
        _world(OUTLAYS, tmp_path, ";form=extruded_bar")
    assert _world(OUTLAYS, tmp_path / "soft", ";bar_style=soft")["page"]["bar_style"] == "soft"


def test_a_plain_page_is_the_world_it_was(tmp_path):
    plain = _bars_only(OUTLAYS)
    plain["bars"][0].pop("segments")
    page = _world(plain, tmp_path)["page"]
    assert "segments" not in page and "warnings" not in page
    B.check_segments({"kind": "ledger", "page": page}, [{"kind": "chart_to", "to": "rescale", "at": 1, "dur": 1}])


# ---- (5) + (6) the player -------------------------------------------------------------------------------------------

PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, stage = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { if (!el) return null; const r = el.getBoundingClientRect(); return [r.x - stage.x, r.y - stage.y, r.width, r.height]; };
  const op = (el) => { let o = 1; for (let e = el; e && e !== st.chart; e = e.parentNode) { const a = e.getAttribute && e.getAttribute('opacity'); if (a != null) o *= +a; } return o; };
  const m = st.chart.getScreenCTM(), Y = (y) => m.d * y + m.f - stage.y, X = (x) => m.a * x + m.e - stage.x;
  const S = st.segs || { bars: [], figs: [] };
  const kScale = (el) => { const q = /scaleY\\(([-\\d.e]+)\\)/.exec(el.style.transform || ''); return q ? +q[1] : 1; };
  const baseY = (el) => Y(parseFloat((el.style.transformOrigin || '0 0').split(/\\s+/)[1]));
  return {
    bars: S.bars.map(b => ({ i: b.i, box: R(b.bar), tf: b.bar.style.transform, k: kScale(b.bar), base: baseY(b.bar),
      parts: b.segs.map(s => ({ j: s.j, name: s.name, fill: getComputedStyle(s.el).fill, y1: Y(s.y1), y0: Y(s.y0), x: X(b.x), w: b.bw * m.a,
        tf: s.el.style.transform, value: s.value })),
      total: b.val && getComputedStyle(b.val).display !== 'none' && op(b.val) > 0.01 ? { box: R(b.val), text: b.val.textContent } : null })),
    figs: S.figs.map(f => ({ bar: f.bar, j: f.j, text: f.text, inside: f.inside, box: R(f.el), op: op(f.el),
      lead: f.lead ? { op: op(f.lead) } : null })),
    key: S.key ? { box: R(S.key), op: op(S.key), names: [...S.key.querySelectorAll('.lp-seg-name')].map(e => e.textContent),
      fills: [...S.key.querySelectorAll('.lp-seg-sw')].map(e => getComputedStyle(e).fill),
      line: [...S.key.querySelectorAll('.lp-seg-sw')].map(e => !!e.dataset.line) } : null,
    pill: st.callout && op(st.callout) > 0.01 ? R(st.callout) : null,
    y2: [...st.chart.querySelectorAll('.lp-y2')].map(e => ({ text: e.textContent, fill: getComputedStyle(e).fill, box: R(e) })),
    y2name: (() => { const e = st.chart.querySelector('.lp-y2-name'); return e ? { text: e.textContent, fill: getComputedStyle(e).fill, box: R(e) } : null; })(),
    names: (st.segNames || []).map(R),
    lines: st.combo ? st.combo.lines.map(ln => ({ pts: ln.pts.map(([x, y]) => [X(x), Y(y)]), sw: parseFloat(getComputedStyle(ln.p).strokeWidth) * m.a,
      labels: ln.labels.map(l => ({ text: l.textContent, box: R(l), op: op(l) })), name: ln.name.textContent })) : [],
    ink: [...st.page.querySelectorAll('.lp-src, .lp-sub, .lp-title')].map(R),
    segEls: st.chart.querySelectorAll('.lp-seg').length, keyEls: st.chart.querySelectorAll('.lp-seg-key').length,
  };
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
INK = {"teal": "rgb(52, 245, 197)", "crimson": "rgb(255, 138, 76)", "cobalt": "rgb(79, 195, 255)",
       "amber": "rgb(245, 183, 46)", "deemph": "rgb(184, 196, 208)"}   # the engine's LP_INK (E67)
HELD, GROWING = 12.0, 5.0


def _one_axis() -> dict:
    """The combo with a line in the STACKS' own unit: the filed cash capex, on the stacks' scale - the same figure as each
    stack's first part, so its points must sit exactly on those parts' tops."""
    o = copy.deepcopy(FUNDING)
    for k in ("line_unit", "line_label"):
        o.pop(k)
    o["series"] = [{"name": "CASH CAPEX", "label": "", "color": "teal",
                    "pts": [[x, b["segments"][0]["value"]] for x, b in zip((2024.125, 2025.125, 2026.125), o["bars"])]}]
    return o


def _plain_combo() -> dict:
    o = copy.deepcopy(FUNDING)
    for b in o["bars"]:
        b.pop("segments")
    o.pop("line_label")
    return o


# key -> (object, row options, aspect, instants)
CASES = {
    "outlays": (OUTLAYS, "", "16:9", [HELD]),
    "funding": (_bars_only(FUNDING), "", "16:9", [GROWING, HELD]),
    "soft": (_bars_only(FUNDING), ";bar_style=soft", "16:9", [HELD]),
    "portrait": (_bars_only(FUNDING), "", "9:16", [HELD]),
    "combo": (FUNDING, "", "16:9", [GROWING, HELD]),
    "combo-portrait": (FUNDING, "", "9:16", [HELD]),
    "one-axis": (_one_axis(), "", "16:9", [HELD]),
    "plain": ({**_bars_only(OUTLAYS), "bars": [{k: v for k, v in OUTLAYS["bars"][0].items() if k != "segments"}]}, "", "16:9", [HELD]),
    "plain-combo": (_plain_combo(), "", "16:9", [HELD]),
}


@pytest.fixture(scope="module")
def painted(tmp_path_factory):
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    from playwright.sync_api import sync_playwright

    tmp = tmp_path_factory.mktemp("stacks")
    out = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for key, (obj, opt, aspect, ts) in list(CASES.items()) + [(g, (None, "", None, None)) for g in GOLDENS]:
                if obj is None:   # a committed golden, served from its own sources at its own instant
                    tl, uris, t0, aspect = RB.load_surface(key)
                    ts = [t0]
                else:
                    world = _world(obj, tmp / key, opt, aspect)
                    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
                               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
                    tl, uris = G._timeline("P69 T64 " + key, scenes, {}, aspect), G._base_uris()
                w, h = RB.STAGE[aspect]
                html = tmp / f"{key}.html"
                html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
                srv, port = RB.serve(html.parent)
                page = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                errors: list[str] = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                try:
                    page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                    RB.prepare_page(page, w, h)
                    page.wait_for_function("document.fonts.status === 'loaded'")
                    got = {"errors": errors, "at": {}}
                    for t in ts:
                        RB.frame_png(page, t, (w, h))
                        got["at"][t] = page.evaluate(PROBE)
                    if len(ts) > 1:   # a cold seek BACK lands what forward play landed
                        RB.frame_png(page, ts[0], (w, h))
                        got["back"] = page.evaluate(PROBE)
                    out[key] = got
                finally:
                    page.context.close()
                    srv.shutdown()
        finally:
            browser.close()
    return out


def _meets(a, b, pad=0.0) -> bool:
    return a[0] - pad < b[0] + b[2] and b[0] < a[0] + a[2] + pad and a[1] - pad < b[1] + b[3] and b[1] < a[1] + a[3] + pad


def _inside(a, b, tol=1.0) -> bool:
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[0] + a[2] <= b[0] + b[2] + tol and a[1] + a[3] <= b[1] + b[3] + tol


STACKED = ["outlays", "funding", "soft", "portrait", "combo", "combo-portrait", "one-axis"]
GOLDENS = ["stacked-combo-funding", "stacked-outlays"]


@needs_browser
@pytest.mark.parametrize("key", STACKED)
def test_each_part_stands_true_to_its_value_bottom_up_inside_its_bar(painted, key):
    got = painted[key]
    assert not got["errors"], got["errors"]
    p = got["at"][HELD]
    assert p["bars"], "the stacks are drawn"
    for b in p["bars"]:
        x, y, w, h = b["box"]
        parts = b["parts"]
        total = sum(q["value"] for q in parts)
        assert parts[0]["y0"] == pytest.approx(b["base"], abs=0.5), ("part 0 stands on the zero line", parts[0], b["base"])
        for lo, hi in zip(parts, parts[1:]):
            assert hi["y0"] == pytest.approx(lo["y1"], abs=0.5), ("the stack runs UP, part on part", lo, hi)
        assert parts[-1]["y1"] == pytest.approx(y, abs=1.5), ("the stack's top is the bar's total", parts[-1], b["box"])
        height = b["base"] - y
        for q in parts:
            assert (q["y0"] - q["y1"]) == pytest.approx(height * q["value"] / total, abs=1.0), ("drawn TRUE to its value (s100 (a))", q)
            assert q["x"] == pytest.approx(x, abs=0.6) and q["w"] == pytest.approx(w, abs=0.6)
            assert q["tf"] == b["tf"], "each part mirrors its bar"


@needs_browser
@pytest.mark.parametrize("key", STACKED)
def test_the_parts_wear_the_keys_colours_and_the_key_names_them_once(painted, key):
    obj = CASES[key][0]
    spec = LPG.build_spec(obj, "bars", None, "right")
    p = painted[key]["at"][HELD]
    order = [(k["name"], INK[k["color"]]) for k in spec["segment_key"]]
    for b in p["bars"]:
        assert [(q["name"], q["fill"]) for q in b["parts"]] == order
    k = p["key"]
    assert k and k["op"] > 0.99 and p["keyEls"] == 1, "ONE key, standing"
    lines = list(obj.get("series") or [])
    assert k["names"] == [n for n, _ in order] + [s["name"] for s in lines], k
    assert k["fills"] == [c for _, c in order] + [INK[s["color"]] for s in lines]
    assert k["line"] == [False] * len(order) + [True] * len(lines), "the line is keyed as a stroke"


@needs_browser
@pytest.mark.parametrize("key", STACKED)
def test_every_figure_and_the_total_are_written_and_touch_no_other_ink(painted, key):
    obj = CASES[key][0]
    p = painted[key]["at"][HELD]
    unit = obj.get("unit") or ""
    spec = LPG.build_spec(obj, "bars", None, "right")
    want = sorted((i, j, ("$" if unit == "$" else "") + s["value_string"]) for i, ss in enumerate(spec["segments"]) for j, s in enumerate(ss or []))
    assert sorted((f["bar"], f["j"], f["text"]) for f in p["figs"]) == want, "each part's figure is written (s100 (b))"
    bars = {b["i"]: b for b in p["bars"]}
    words = [f["box"] for f in p["figs"]] + [b["total"]["box"] for b in p["bars"] if b["total"]]
    for f in p["figs"]:
        assert f["op"] > 0.99
        part = next(q for q in bars[f["bar"]]["parts"] if q["j"] == f["j"])
        pbox = [part["x"], part["y1"], part["w"], part["y0"] - part["y1"]]
        if f["inside"]:
            assert _inside(f["box"], pbox, tol=0.5), ("a figure inside stays inside its part", f, pbox)
        else:
            assert f["lead"] and f["lead"]["op"] > 0.99, "a figure beside its bar keeps its leader"
            for b in p["bars"]:
                assert not _meets(f["box"], b["box"]), ("... and touches no bar", f, b["box"])
        for o in words:
            assert o is f["box"] or not _meets(f["box"], o), ("no figure on another word", f, o)
    for b in p["bars"]:
        total = (b["total"] or {}).get("box") or p["pill"]
        assert total, "the bar's total is written"
        assert total[1] + total[3] <= b["box"][1] + 1, ("... over the bar", total, b["box"])
        if b["total"] and unit == "$":
            assert b["total"]["text"].startswith("$"), ("the total carries its unit, as its parts do", b["total"])
    for box in [f["box"] for f in p["figs"]] + [b["box"] for b in p["bars"]] + p["ink"] + words:
        assert not _meets(p["key"]["box"], box), ("the key touches no other ink", p["key"]["box"], box)


@needs_browser
def test_a_figure_too_thin_for_its_part_is_written_beside_it_as_the_compiler_warned(painted):
    p = painted["funding"]["at"][HELD]
    beside = [(f["bar"], f["j"]) for f in p["figs"] if not f["inside"]]
    assert beside == [(2, 1)], ("Q1 2026's $9.5 left over, and only it", beside)
    spec = LPG.build_spec(_bars_only(FUNDING), "bars", None, "right")
    assert [w.split(" on bar ")[1][:1] for w in LPG.segment_fit_warnings(spec, "16:9")] == ["2"]


@needs_browser
@pytest.mark.parametrize("key", ["funding", "combo"])
def test_the_figures_land_with_their_bar_and_a_seek_lands_what_play_lands(painted, key):
    got = painted[key]
    early = got["at"][GROWING]
    for b in early["bars"]:
        for q in b["parts"]:
            assert q["tf"] == b["tf"], "a growing part mirrors its growing bar"
    growing = {b["i"] for b in early["bars"] if b["k"] < 0.9}
    assert growing, "the instant is mid-build"
    for f in early["figs"]:
        if f["bar"] in growing:
            assert f["op"] < 0.01, ("no figure before its bar stands", f)
    assert got["back"] == early, "a pure function of t"


@needs_browser
@pytest.mark.parametrize("key", ["combo", "combo-portrait"])
def test_the_combos_line_takes_its_own_labelled_axis_in_its_own_colour(painted, key):
    p = painted[key]["at"][HELD]
    teal = INK["teal"]
    assert p["y2"] and all(t["text"].endswith("%") and t["fill"] == teal for t in p["y2"]), ("s102 (b)(c)", p["y2"])
    assert p["y2name"] and p["y2name"]["text"] == FUNDING["line_label"] and p["y2name"]["fill"] == teal
    zero = next(t for t in p["y2"] if t["text"] == "0%")
    base = p["bars"][0]["base"]
    assert abs((zero["box"][1] + zero["box"][3] / 2) - base) < 30, ("the line's axis stands on the stacks' zero", zero, base)
    (ln,) = p["lines"]
    assert ln["name"] == "", "the line is named in the key, not inline"
    assert [lb["text"] for lb in ln["labels"]] == ["44%", "65%", "94%"]
    others = [f["box"] for f in p["figs"]] + [b["total"]["box"] for b in p["bars"] if b["total"]] + [t["box"] for t in p["y2"]] \
        + [p["y2name"]["box"], p["key"]["box"]]
    for lb in ln["labels"]:
        assert lb["op"] > 0.99
        for o in others:
            assert not _meets(lb["box"], o), ("a line label never overprints", lb, o)
    for b in p["bars"]:
        for q in b["parts"]:
            box = [q["x"], q["y1"], q["w"], q["y0"] - q["y1"]]
            for lb, pt in zip(ln["labels"], ln["pts"]):
                if _meets(lb["box"], box, -1.0):
                    assert box[0] <= pt[0] <= box[0] + box[2] and box[1] <= pt[1] <= box[1] + box[3], \
                        ("a label sits on a part only when its own point is in it", lb, q)


@needs_browser
def test_a_line_in_the_stacks_unit_is_drawn_on_their_scale(painted):
    p = painted["one-axis"]["at"][HELD]
    assert p["y2"] == [] and p["y2name"] is None, "one unit is one axis"
    (ln,) = p["lines"]
    for b, pt in zip(p["bars"], ln["pts"]):
        assert pt[1] == pytest.approx(b["parts"][0]["y1"], abs=1.0), ("the capex line meets each stack's capex top", pt, b["parts"][0])


@needs_browser
@pytest.mark.parametrize("key", ["plain", "plain-combo"])
def test_without_segments_a_page_draws_no_part_no_key_and_no_coloured_axis(painted, key):
    p = painted[key]["at"][HELD]
    assert p["segEls"] == 0 and p["keyEls"] == 0 and p["bars"] == [] and p["figs"] == []
    assert p["y2"] == [] and p["y2name"] is None


def test_the_engine_names_its_dials_once():
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const LPSEG = Object\.freeze\(\{([^}]*)\}\)", src)
    assert m, "the engine carries the LPSEG dial block"
    dials = dict(re.findall(r"([A-Z_]+): ([\d.]+)", m.group(1)))
    assert float(dials["PAD_PX"]) == LPG.SEGMENT_FIG["pad"] and float(dials["FIG_MIN"]) == LPG.SEGMENT_FIG["min"]
    assert float(dials["FIG_LINE"]) == LPG.SEGMENT_FIG["line"], dials
    lines = re.split(r"\r?\n", src)
    assert sum("lpSegPaint(S)" in ln for ln in lines) == 2, "the parts are mirrored every frame, on both paint paths"


def _line_hits(pts, box, pad, step=1.0):
    """Does the polyline's stroke (half its width about its path, sampled every `step` px) touch the box?"""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(1, int(((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5 / step))
        for j in range(n + 1):
            x, y = ax + (bx - ax) * j / n, ay + (by - ay) * j / n
            if box[0] - pad < x < box[0] + box[2] + pad and box[1] - pad < y < box[1] + box[3] + pad:
                return True
    return False


@needs_browser
@pytest.mark.parametrize("key", ["combo", "combo-portrait", "one-axis", "stacked-combo-funding", "stacked-outlays"])
def test_the_line_crosses_no_written_figure_total_key_or_axis_name(painted, key):
    """The parent's frame read (2026-09-24): the share line ran through the Q1 '26 total. MEASURED: every segment of every
    line, as drawn (half its stroke either side), against every part's figure, every total, the key and both axis names."""
    got = painted[key]
    assert not got["errors"], got["errors"]
    p = got["at"][max(got["at"])]
    words = [("figure " + f["text"], f["box"]) for f in p["figs"]]
    words += [("total " + b["total"]["text"], b["total"]["box"]) for b in p["bars"] if b["total"]]
    words += [("the total's pill", p["pill"])] if p["pill"] else []
    words += [("the key", p["key"]["box"])] if p["key"] else []
    words += [("an axis name", n) for n in p["names"]]
    assert words, "the page writes its figures"
    if key == "stacked-outlays":
        assert p["lines"] == [], "a bars page has no line"
    for ln in p["lines"]:
        for what, box in words:
            assert not _line_hits(ln["pts"], box, ln["sw"] / 2), (f"the line crosses {what}", box, ln["pts"])


@needs_browser
@pytest.mark.parametrize("key", ["combo", "combo-portrait", "stacked-combo-funding"])
def test_the_right_axis_name_stands_on_a_line_of_its_own_over_its_top_tick(painted, key):
    p = painted[key]["at"][max(painted[key]["at"])]
    name, top = p["y2name"]["box"], min(t["box"][1] for t in p["y2"])
    assert name[1] + name[3] <= top - 4, ("the axis's name clear of its top tick", name, top)
