"""P72 T13 - A BARS PAGE WRITES ITS UNITS AND KEEPS ITS LABELS CLEAR (R26-274, R26-287, R26-250, R26-217; E28: an
axis states its unit).

  R26-274  a WORD unit takes a space ("20 years"), a symbol unit none ("12%", "3.2x", "96Mb"), a unit the author
           spaced (" years") is written as given; and the y tick column never leaves the stage - on the default 16:9
           page the two-clocks page's "20 years" stood at x -20.
  R26-287  a unit with a prefix AND a suffix: `unit: "$"` + `unit_suffix: "B"` writes "$480B" on the value, the ticks
           and the pill, in the page and (through ledger_page's spec) the card; the key is refused BY NAME when
           malformed, beside a unit that is not a prefix, and on a page that would drop it (s106).
  R26-250  a rule's label is never written over a bar: it keeps its place when it clears, else slides along its
           rule into free ground, wraps, shrinks, or is written past the rule's end.
  R26-217  the treemap's legibility floors are resolved from the stage a cell renders on; the tiers ceiling's reason
           is measured per stage, not a portrait figure baked into the message.

R26-170 (the weak-prints page's labels and tags at one foot) was DONE at this slice's base by 2b7b6a4 (the row thins,
M28 FAIL 9 -> PASS 0); its guard stands here so it cannot regress.
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
SCRIPTS = ROOT / "content/video_engine/scripts"
GOLDEN = ROOT / "content/video_engine/tests/golden"
for p in (SCRIPTS, GOLDEN, ROOT / "content/video_engine/tests"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import ledger_page as L  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
SP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
MT = ROOT / "content/video_engine/projects/systems-and-blowups/memory-trades-the-calendar"
OBJ = SP / "evidence/objects"
CLOCKS = "ledger:ev-two-clocks-bars-v1:bars::right:axes:cut;idle=live"
CAPEX = "ledger:ev-capex-consensus-v2:bars:1:right:axes:cut;idle=live"
CONC = "ledger:ev-index-concentration-bars-v1:bars::right:axes:cut;idle=live"
WEAK = "ledger:ev-weak-prints-v1:bars:7:right:axes:cut;idle=live"
LONGFORM = ";readability=longform"
T_READ = 9.0   # the page has landed (ROLL + SAVOR + FIELD + PUNCH + BUILD = 7.4) and its values are written


def _obj(name: str) -> dict:
    return json.loads((OBJ / f"{name}.series.json").read_text(encoding="utf-8"))


# ---- R26-274 / R26-287: the formatter ------------------------------------------------------------------------------


@pytest.mark.parametrize("unit, text, want", [
    ("years", "20", "20 years"),          # a word unit takes a space (R26-274)
    (" years", "20", "20 years"),         # ... written as given when the author spaced it (the H object's own form)
    ("yen", "-5", "-5 yen"),
    ("USD billions", "90", "90 USD billions"),
    ("%", "12", "12%"),                   # a symbol unit none
    ("x", "3.2", "3.2x"),
    ("Mb", "-96", "-96Mb"),               # tiers-two's golden unit: two letters is a symbol
    ("bn", "480", "480bn"),
    ("$", "480", "$480"),                 # the prefix, as it always was
    ("$", "-40", "-$40"),
    ("", "7", "7"),
])
def test_a_word_unit_takes_a_space_and_a_symbol_unit_none(unit, text, want):
    assert L.with_unit(text, unit) == want


@pytest.mark.parametrize("text, suffix, want", [
    ("480", "B", "$480B"), ("-40", "B", "-$40B"), ("1.2", "tn", "$1.2tn"), ("480", "billion", "$480 billion")])
def test_a_prefix_and_a_suffix_write_the_figure_whole(text, suffix, want):
    assert L.with_unit(text, "$", suffix) == want


def test_the_engine_formatter_is_the_one_ledger_page_mirrors():
    """One law, two languages: the engine's word test IS ledger_page's (the same pattern, the same three letters)."""
    src = ENGINE.read_text(encoding="utf-8")
    assert "const LP_UNIT_WORD = /^(?=\\p{L})[\\s\\S]*?\\p{L}{3}/u;" in src
    assert "unit = lpUnitOf(pg);" in src, "the bars builder takes the page's unit through lpUnitOf"
    assert L.UNIT_WORD_RE.pattern == r"^(?=[^\W\d_])[\s\S]*?[^\W\d_]{3}"


# ---- R26-287: the key, its validation and its spec --------------------------------------------------------------------


def _capex(**extra) -> dict:
    return dict(_obj("ev-capex-consensus-v2"), **extra)


def test_the_suffix_rides_the_bars_spec_and_its_card():
    s = _capex(unit_suffix="B")
    assert L.validate(s, "bars") == []
    spec = L.build_spec(s, "bars", 1)
    assert spec["unit"] == "$" and spec[L.UNIT_SUFFIX_KEY] == "B"


def test_a_page_with_no_suffix_builds_the_spec_it_always_built():
    spec = L.build_spec(_capex(), "bars", 1)
    assert L.UNIT_SUFFIX_KEY not in spec and spec["unit"] == "$"


@pytest.mark.parametrize("patch, needle", [
    ({"unit_suffix": ""}, "unit_suffix '' must be the magnitude"),
    ({"unit_suffix": 3}, "unit_suffix 3 must be the magnitude"),
    ({"unit_suffix": " B"}, "unit_suffix ' B' must be the magnitude"),
    ({"unit_suffix": "B2"}, "unit_suffix 'B2' must be the magnitude"),
    ({"unit_suffix": "billions of dollars"}, "must be the magnitude"),
    ({"unit_suffix": "B", "unit": "%"}, "completes a PREFIX unit ('$'); this page's unit is '%' (a suffix already)"),
    ({"unit_suffix": "B", "unit": ""}, "this page's unit is '' - write the one unit"),
])
def test_a_malformed_or_misplaced_suffix_is_refused_by_name(patch, needle):
    errs = L.validate(_capex(**patch), "bars")
    assert any(needle in e for e in errs), errs


def test_a_suffix_on_a_page_that_would_drop_it_is_refused_by_name():
    line = {"title": "t", "src": "s", "unit": "$", "unit_suffix": "B",
            "series": [{"name": "a", "pts": [[2000 + i, 10.0 + i] for i in range(40)]}]}
    errs = L.validate(line, "line")
    assert any("unit_suffix is written by a bars page (story); this page draws 'dense-line'" in e for e in errs), errs


def test_a_stacked_figure_estimate_writes_the_unit_as_the_engine_does():
    """The segment WARN measures the figure the engine writes - "$9.5B", not "$9.5" - so its width is the drawn one."""
    import test_stacked_combo as TS
    series = dict(TS._bars_only(TS.FUNDING), unit_suffix="B")
    assert L.validate(series, "bars") == []
    warns = L.segment_fit_warnings(L.build_spec(series, "bars", 0, "right"), "16:9")
    thin = [w for w in warns if "'Left over'" in w and "bar 2" in w]
    assert len(thin) == 1 and "its figure '$9.5B' needs" in thin[0], warns


# ---- R26-217: the floors are the stage's ------------------------------------------------------------------------------


def test_the_treemap_floors_resolve_from_the_stage_and_equal_the_portrait_numbers():
    """The derivation stated in ledger_page: both stages put their 1080-px side across the phone's short side, so the
    floors in stage px are one number on both - resolved per stage, not assumed."""
    for aspect in L.STAGE_PX:
        f = L.treemap_floors(aspect)
        assert f["value_font"] == L.TREEMAP_VALUE_FONT and f["pad"] == L.TREEMAP_PAD, aspect
        assert f["min_cell"] == tuple(float(v) for v in L.TREEMAP_MIN_CELL), aspect
    assert L.label_tier(240, 160, "United States", "16.8", "16:9") == L.label_tier(240, 160, "United States", "16.8")


def test_the_tiers_ceiling_states_the_bands_it_measured_at_each_stage():
    from test_ledger_page import _tier, _tiers
    errs = L.validate(_tiers(*[_tier(f"T{i}", base=10.0 + i) for i in range(5)]), "tiers")
    row = next(e for e in errs if e.startswith("5 tiers"))
    assert "~1060" not in row and "~250" not in row, "the portrait figure baked into the message is gone"
    assert re.search(r"\d+ px tall at 16:9 and \d+ px tall at 9:16", row), row
    assert re.search(r"each of 4 bands takes a quarter of the plot, \d+ px at 16:9 and \d+ px at 9:16", row), row


# ---- the pages, read on the served player -------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """() => {
  const stg = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect(); return [r.x - stg.x, r.y - stg.y, r.width, r.height]; };
  const world = [wA, wB].find(e => e && e.__lp && e.classList.contains('ledger'));
  const st = world.__lp, shown = (e) => getComputedStyle(e).display !== 'none' && (e.textContent || '').length > 0;
  const ticks = (st.marks || []).filter(m => m.role === 'ylabel').map(m => ({ t: m.el.textContent, box: R(m.el) }));
  return { ticks, stageW: stg.width,
           vals: (st.bars || []).map(b => ({ t: b.val.textContent, shown: shown(b.val) })),
           pill: st.cval ? st.cval.textContent : null,
           bars: (st.bars || []).map(b => R(b.bar)),
           rules: (st.hlines || []).filter(h => h.lab).map(h => ({ t: h.lab.textContent, box: R(h.lab) })),
           fit: st.ruleFit || [] };
}"""


def _surface(plate, proj, aspect, over=None):
    import build_golden_sources as G
    import build_scene_timeline_f as B
    saved = B.ASPECT
    B.ASPECT = aspect
    try:
        world = B.world_for_plate(plate, (0, 0, 0), proj)
        if aspect == "16:9":
            B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    world = copy.deepcopy(world)
    for k, v in (over or {}).items():
        if k == "axes":
            world["page"]["axes"] = dict(world["page"].get("axes") or {}, **v)
        else:
            world["page"][k] = v
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
    tl = G._timeline("P72 T13", scenes, {}, aspect)
    return tl, dict(G._base_uris(), **B.longform_assets(tl))


def _read(plate, proj=SP, aspect="16:9", over=None, t=T_READ):
    """The page's DOM at t, and M28's verdict on it (probe.py's own read, gate_motion_density's own row)."""
    import render_baseline as RB
    import probe as PR
    import gate_motion_density as GM
    tl, uris = _surface(plate, proj, aspect, over)
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        (b / "t13.timeline.json").write_text(json.dumps(tl), encoding="utf-8")
        (b / "player.html").write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with PR.Probe(b, "t13.timeline.json") as p:
            p.seek(t)
            dom = p.page.evaluate(PROBE)
            inst = p.at(t, "read")
            errs = list(p.errs)
    gate = GM._labels_gate({"player_sha256": "x", "instants": [inst]})
    return dom, gate, errs


def _meets(a, b, pad=0.0):
    return a[0] < b[0] + b[2] + pad and b[0] < a[0] + a[2] + pad and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


@needs_browser
@pytest.mark.parametrize("unit", ["years", " years"])
def test_the_two_clocks_page_writes_20_years_and_its_ticks_stay_on_the_stage(unit):
    """Acceptance (1), on the default 16:9 page where the column left the stage (x -20 at the base)."""
    dom, gate, errs = _read(CLOCKS, over={"unit": unit})
    assert not errs, errs
    assert [v["t"] for v in dom["vals"]] == ["20 years", "5 years"], dom["vals"]
    assert dom["ticks"] and all(re.fullmatch(r"\d+ years", k["t"]) for k in dom["ticks"]), dom["ticks"]
    left = min(k["box"][0] for k in dom["ticks"])
    assert left >= 11.5, ("every y tick sits inside the stage, EDGE_PX from its edge", left)
    assert gate.level == "PASS", gate.message


@needs_browser
@pytest.mark.parametrize("profile", ["", LONGFORM])
def test_the_capex_bars_print_their_billions_on_the_value_the_ticks_and_the_pill(profile):
    """Acceptance (2): "$480B" / "$690B", the ticks "$...B" - the default page and the long form's."""
    dom, gate, errs = _read(CAPEX + profile, over={"unit_suffix": "B"})
    assert not errs, errs
    assert [v["t"] for v in dom["vals"]] == ["$480B", "$690B"], dom["vals"]
    assert dom["pill"] == "$690B", dom["pill"]
    assert dom["ticks"] and all(re.fullmatch(r"\$\d+B", k["t"]) for k in dom["ticks"]), dom["ticks"]
    assert min(k["box"][0] for k in dom["ticks"]) >= 11.5, dom["ticks"]
    assert gate.level == "PASS", gate.message


@needs_browser
def test_the_capex_page_without_a_suffix_writes_what_it_always_wrote():
    dom, _gate, errs = _read(CAPEX)
    assert not errs, errs
    assert [v["t"] for v in dom["vals"]] == ["$480", "$690"] and dom["pill"] == "$690", dom
    assert [k["t"] for k in dom["ticks"]] == ["$0", "$200", "$400", "$600"], dom["ticks"]


@needs_browser
@pytest.mark.parametrize("profile", ["", LONGFORM + ";bar_style=soft"])
def test_the_concentration_pages_rule_label_never_overlaps_its_bar(profile):
    """Acceptance (3): "historically 2-4%" clears the lone bar (M28 PASS) - where it already stood, so it is untouched."""
    dom, gate, errs = _read(CONC + profile)
    assert not errs, errs
    rule = next(r for r in dom["rules"] if r["t"] == "historically 2-4%")
    assert not any(_meets(rule["box"], b) for b in dom["bars"]), (rule, dom["bars"])
    assert dom["fit"] == [], "a label that clears keeps its place"
    assert gate.level == "PASS", gate.message


@needs_browser
@pytest.mark.parametrize("profile", ["", LONGFORM])
def test_a_long_rule_label_across_a_tall_bar_moves_off_it(profile):
    """R26-250's owed test: a wide bar and a long rule label. At the base the label stood across the right bar."""
    over = {"axes": {"hlines": [{"y": 300, "label": "a long comparator rule label", "color": "deemph"}]}}
    dom, gate, errs = _read(CAPEX + profile, over=over)
    assert not errs, errs
    rule = dom["rules"][0]
    assert not any(_meets(rule["box"], b) for b in dom["bars"]), (rule, dom["bars"])
    assert dom["fit"] and dom["fit"][0]["how"] in ("slide", "wrap", "shrink", "end"), dom["fit"]
    assert rule["box"][0] + rule["box"][2] <= dom["stageW"], rule
    assert gate.level == "PASS", gate.message


@needs_browser
@pytest.mark.parametrize("aspect", ["9:16", "16:9"])
def test_the_weak_prints_labels_and_value_tags_never_share_a_foot(aspect):
    """Acceptance (4), R26-170's guard: DONE at the base by 2b7b6a4 (the row thins); it stays M28 PASS."""
    _dom, gate, errs = _read(WEAK, MT, aspect)
    assert not errs, errs
    assert gate.level == "PASS", gate.message
