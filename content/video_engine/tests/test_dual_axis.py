"""P71 T13 (was P69 T43b; R26-307, E99 s102) - A SECOND AXIS, AND AN INVERTED ONE, FOR A CO-MOVEMENT CLAIM.

R26-307 first: a page's `y2` was ACCEPTED AND IGNORED (`ledger_page.validate` returned [] and `build_spec` dropped the
key) - "a second axis must either draw or be refused by name" (E99 s106: a silent drop is neither advice nor refusal).
Now `y2` draws on the ONE builder that has a draw path for it - a dense line page - and is refused by name everywhere
else. The grammar, on the series object:

    "y2": {"series": [i, ...], "unit": "%", "label": "10-year yield", "invert": true},   # the right axis
    "claim": "comove" | "lead_lag",                                                     # s102 (a): REQUIRED with y2
    "ylabel": "Japan's holdings, $bn"                                                   # the left axis names its unit

s102's three conditions are the truth rules, refused by name: (a) the claim is co-movement or lead/lag; (b) each axis
names its unit and an inverted axis says "inverted" on the page; (c) each axis's tick labels wear their own series'
ink. E28 binds every single-axis page: without `y2` nothing changes, to the byte (the goldens are the contract).

The page is read on the SERVED player through the golden `dual-axis-inverted` (a reference beat: Japan's Treasury
holdings against the 10-year yield, inverted).
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

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"

PTS_A = [[2020.0, 1200.0], [2021.0, 1290.0], [2022.0, 1170.0], [2023.0, 1110.0]]
PTS_B = [[2020.0, 1.8], [2021.0, 1.4], [2022.0, 2.9], [2023.0, 4.1]]


def _page(**over) -> dict:
    """A two-line page with a second, inverted axis - every field the grammar asks for."""
    page = {"title": "Two lines", "src": "a source", "ylabel": "holdings, $bn", "claim": "comove",
            "series": [{"name": "HOLDINGS", "color": "teal", "pts": copy.deepcopy(PTS_A)},
                       {"name": "YIELD", "color": "amber", "pts": copy.deepcopy(PTS_B)}],
            "y2": {"series": [1], "unit": "%", "label": "10-year yield", "invert": True}}
    for k, v in over.items():
        if v is None:
            page.pop(k, None)
        else:
            page[k] = v
    return page


def _y2(**over) -> dict:
    y2 = {"series": [1], "unit": "%", "label": "10-year yield", "invert": True}
    for k, v in over.items():
        if v is None:
            y2.pop(k, None)
        else:
            y2[k] = v
    return y2


def _has(errors: list[str], *words: str) -> bool:
    return any(all(w in e for w in words) for e in errors)


# ---- R26-307 FIRST: `y2` where nothing draws it is refused BY NAME ----------------------------------------------------


@pytest.mark.parametrize("variant,obj", [
    ("bars", {"title": "t", "src": "s", "unit": "$", "bars": [{"label": "a", "value": 1}, {"label": "b", "value": 2}]}),
    ("line", {"title": "t", "src": "s", "unit": "$", "bars": [{"label": "a", "value": 1}, {"label": "b", "value": 2}],   # a combo
              "series": [{"name": "L", "pts": [[0, 1.0], [1, 2.0]]}]}),
    ("share", {"title": "t", "src": "s", "unit": "%", "shares": [{"label": "a", "value": 60}, {"label": "b", "value": 40}]}),
    ("line", {"title": "t", "src": "s", "schematic": {"shape": "hype", "phases": [{"name": "Peak", "from": 0.1, "to": 0.3}]}}),
])
def test_r26_307_a_y2_on_a_page_with_no_draw_path_is_refused_by_name(variant, obj):
    page = dict(obj, y2=_y2(series=[0]), claim="comove")
    errors = LPG.validate(page, variant)
    assert _has(errors, "y2"), (variant, errors)


def test_r26_307_a_y2_is_never_silently_dropped_by_build_spec():
    spec = LPG.build_spec(_page(), "line")
    assert spec["builder"] == "dense-line"
    assert spec[LPG.Y2_KEY] == {"series": [1], "unit": "%", "label": "10-year yield", "invert": True, "claim": "comove",
                                "header": "10-year yield (%, inverted)"}


# ---- s102 (a): the claim is REQUIRED, and it is co-movement or lead/lag ----------------------------------------------


def test_a_y2_without_claim_is_refused_citing_s102():
    errors = LPG.validate(_page(claim=None), "line")
    assert _has(errors, "claim", "s102"), errors


def test_a_claim_is_comove_or_lead_lag():
    errors = LPG.validate(_page(claim="level"), "line")
    assert _has(errors, "claim", "comove", "lead_lag"), errors
    assert LPG.validate(_page(claim="lead_lag"), "line") == []
    assert LPG.validate(_page(), "line") == []


def test_a_co_movement_claim_without_a_second_axis_is_refused_by_name():
    errors = LPG.validate(_page(y2=None), "line")
    assert _has(errors, "comove", "y2"), errors


def test_a_page_level_invert_is_refused_by_name():
    errors = LPG.validate(_page(invert=True), "line")
    assert _has(errors, "invert", "y2"), errors


# ---- s102 (b): each axis names its unit ------------------------------------------------------------------------------


def test_the_right_axis_names_its_unit_and_its_name():
    assert _has(LPG.validate(_page(y2=_y2(unit=None)), "line"), "y2", "unit")
    assert _has(LPG.validate(_page(y2=_y2(unit="")), "line"), "y2", "unit")
    assert _has(LPG.validate(_page(y2=_y2(label=None)), "line"), "y2", "label")


def test_the_left_axis_names_its_unit():
    errors = LPG.validate(_page(ylabel=None), "line")
    assert _has(errors, "ylabel", "s102"), errors


def test_an_inverted_axis_says_inverted_on_the_page():
    assert LPG.y2_header(_y2()) == "10-year yield (%, inverted)"
    assert LPG.y2_header(_y2(invert=False)) == "10-year yield (%)"
    assert LPG.y2_header(_y2(invert=None)) == "10-year yield (%)"
    assert LPG.Y2_INVERTED in LPG.y2_header(_y2())


# ---- the object's own shape, refused by name when malformed or misplaced (common rule (h)) ---------------------------


@pytest.mark.parametrize("y2,words", [
    ("yes", ("y2", "object")),
    (_y2(side="right"), ("y2", "side")),
    (_y2(series=[]), ("y2", "series")),
    (_y2(series=1), ("y2", "series")),
    (_y2(series=[True]), ("y2", "series")),
    (_y2(series=[2]), ("y2", "series", "2")),
    (_y2(series=[1, 1]), ("y2", "series")),
    (_y2(series=[0, 1]), ("y2", "left")),
    (_y2(invert="yes"), ("y2", "invert")),
])
def test_a_malformed_y2_is_refused_by_name(y2, words):
    errors = LPG.validate(_page(y2=y2), "line")
    assert _has(errors, *words), (y2, errors)


@pytest.mark.parametrize("over,words", [
    ({"log": True}, ("y2", "log")),
    ({"break": {"after": 2020.5, "before": 2021.5, "eras": ["a", "b"]}}, ("y2", "break")),
    ({"form": "tilted_line"}, ("y2", "form")),
])
def test_a_y2_on_a_page_whose_x_or_y_it_cannot_follow_is_refused(over, words):
    errors = LPG.validate(_page(**over), "line")
    assert _has(errors, *words), (over, errors)


def test_a_later_series_on_a_y2_page_is_refused():
    page = _page()
    page["series"].append({"name": "LATER", "later": True, "pts": copy.deepcopy(PTS_A)})
    assert _has(LPG.validate(page, "line"), "y2", "later")


def test_two_axes_in_one_unit_warn_with_the_unit():
    """s106: the engine advises - one measure on two scales invites reading the gap between the lines (E75 s3); s102
    allows it for a co-movement claim (Bravos's DOM 01:00: two yields, two scales), so it is a WARN, not a refusal."""
    spec = LPG.build_spec(_page(unit="%"), "line")
    assert any(w.startswith(LPG.FORM_WARN) and "%" in w and "y2" in w for w in spec.get("warnings") or []), spec.get("warnings")
    assert "warnings" not in LPG.build_spec(_page(), "line")


# ---- E28: a single-axis page is untouched ----------------------------------------------------------------------------


def test_a_single_axis_page_carries_no_y2_and_keeps_its_ink_key():
    one = _page(y2=None, claim=None)
    spec = LPG.build_spec(one, "line")
    assert LPG.Y2_KEY not in spec
    assert LPG.validate(one, "line") == []
    two = LPG.build_spec(_page(), "line")
    assert LPG.page_ink_key(spec) != LPG.page_ink_key(two), "a y2 page is its own ink: it lays out its own right column"


def test_the_ink_key_follows_the_right_axis_words_and_its_data():
    base = LPG.build_spec(_page(), "line")
    assert LPG.page_ink_key(base) == LPG.page_ink_key(LPG.build_spec(_page(), "line"))
    assert LPG.page_ink_key(base) != LPG.page_ink_key(LPG.build_spec(_page(y2=_y2(invert=False)), "line"))
    wide = _page()
    wide["series"][1]["pts"][-1][1] = 14.1   # a two-digit tick widens the column
    assert LPG.page_ink_key(base) != LPG.page_ink_key(LPG.build_spec(wide, "line"))


# ---- the key rail and the badges carry both axes ----------------------------------------------------------------------


def test_the_longform_key_rail_names_each_series_side():
    page = _page()
    page["series"][0].update(name="JAPAN'S HOLDINGS OF US TREASURIES", label="$1,117bn")   # names too long for their tags:
    page["series"][1].update(name="THE US TEN-YEAR TREASURY YIELD", label="4.48%")         # the key rail takes them (P69 T10)
    spec = LPG.apply_longform(B.stamp_full_stage(LPG.build_spec(page, "line")), "phone")
    assert spec["axes"].get("tag_form") == "badge", spec["axes"]
    names = {k["series"]: k["name"] for k in spec["axes"]["key"]}
    assert names == {0: "JAPAN'S HOLDINGS OF US TREASURIES (LHS)", 1: "THE US TEN-YEAR TREASURY YIELD (RHS, inverted)"}, names
    one = _page(y2=None, claim=None)
    one["series"] = page["series"]
    plain = LPG.apply_longform(B.stamp_full_stage(LPG.build_spec(one, "line")), "phone")
    assert [k["name"] for k in plain["axes"]["key"]] == ["JAPAN'S HOLDINGS OF US TREASURIES", "THE US TEN-YEAR TREASURY YIELD"]


def test_a_badge_keying_a_line_names_its_side():
    page = _page(badges=[{"label": "YIELD", "accent": "sunflower"}, {"label": "HOLDINGS", "accent": "teal"}])
    spec = LPG.build_spec(page, "line")
    labels = {b["accent"]: b["label"] for b in spec["badges"]}
    assert labels == {"sunflower": "YIELD (RHS, inverted)", "teal": "HOLDINGS (LHS)"}, labels
    plain = LPG.build_spec(_page(y2=None, claim=None, badges=[{"label": "YIELD", "accent": "sunflower"}]), "line")
    assert plain["badges"][0]["label"] == "YIELD", "a single-axis page's badge is untouched"


# ---- page_boxes: the right axis's words are a box --------------------------------------------------------------------


def test_page_boxes_carries_the_right_axis_column_beside_the_plot():
    spec = B.stamp_full_stage(LPG.build_spec(_page(), "line"))
    boxes = LPG.page_boxes(spec, "16:9")
    y2 = boxes[LPG.Y2_BOX]
    plot = boxes["plot"]
    assert y2["x"] >= plot["x"] + plot["w"] - 1 and y2["w"] > 0 and y2["h"] > 0, (y2, plot)
    one = LPG.page_boxes(B.stamp_full_stage(LPG.build_spec(_page(y2=None, claim=None), "line")), "16:9")
    assert LPG.Y2_BOX not in one


def test_the_golden_page_is_served_its_measured_right_axis():
    """measure_page_boxes' `dense-line+y2` representative (the golden's own page): the right axis's words as DRAWN, right of
    the measured plot. The fixture is generated (`measure_page_boxes.py --write`); a fixture measured before this slice
    has no such entry and the page falls back to the estimate above."""
    import measure_page_boxes as M
    page = B.stamp_full_stage(M.representative(M.DUAL_LINE))
    if not LPG.measured_boxes(page, "16:9"):
        pytest.skip("page-boxes.v1.json predates dense-line+y2 - regenerate it (measure_page_boxes.py --write)")
    boxes = LPG.page_boxes(page, "16:9")
    assert boxes["measured"] and boxes[LPG.Y2_BOX]["x"] >= boxes["plot"]["x"] + boxes["plot"]["w"], (boxes[LPG.Y2_BOX], boxes["plot"])


# ---- the compiler: a y2 page holds its page ------------------------------------------------------------------------


def _world(page: dict | None = None) -> dict:
    spec = LPG.build_spec(page or _page(), "line")
    return {"kind": "ledger", "page": B.stamp_full_stage(spec)}


def test_a_y2_page_takes_no_chart_state():
    for verb in ("rescale", "extend", "recast", "morph", "remake"):
        with pytest.raises(ValueError, match=r"y2.*chart_to|chart_to.*y2"):
            B.check_y2(_world(), [{"kind": "chart_to", "at": 3.0, "to": verb}])
    B.check_y2(_world(), [{"kind": "build_to", "at": 1.0, "dur": 1.0, "series": 1, "target": {"kind": "datum", "index": 2}}])


def test_a_y2_page_is_drawn_at_16_9():
    saved = B.ASPECT
    B.ASPECT = "9:16"
    try:
        with pytest.raises(ValueError, match="16:9") as got:
            B.check_y2(_world(), [])
        assert "not built at 9:16" in str(got.value) and "R26-307" in str(got.value), got.value
        assert "no room" not in str(got.value) and "margin" not in str(got.value), ("s106: a fit reason is a WARN", got.value)
    finally:
        B.ASPECT = saved


def test_a_y2_page_is_drawn_flat():
    world = _world()
    world["page"]["form"] = {"kind": "tilted_line"}
    with pytest.raises(ValueError, match="form"):
        B.check_y2(world, [])


def test_a_level_join_across_the_two_axes_is_refused():
    join = {"kind": "level_join", "at": 2.0, "dur": 1.0, "from": 1, "series": 0, "to": {"series": 1, "index": 2}, "label": "x"}
    with pytest.raises(ValueError, match="level_join"):
        B.check_y2(_world(), [join])


def test_r2_a_level_join_to_the_axis_from_a_right_axis_line_is_refused():
    """Review 1 (HIGH): the join's axis form `{y}` ends its rule on the LEFT axis (the engine's `axisX` is the plot's left
    edge), so a right-axis line's level would be read in the left's units."""
    join = {"kind": "level_join", "at": 2.0, "dur": 1.0, "series": 1, "from": 3, "to": {"y": 4.1}, "label": "x"}
    with pytest.raises(ValueError, match=r"level_join.*(left|axis)"):
        B.check_y2(_world(_page(y2=_y2(invert=False))), [join])
    B.check_y2(_world(), [dict(join, series=0, to={"y": 1110.0})])   # a LEFT line's level to its own axis: drawn


@pytest.mark.parametrize("spread", [
    {"kind": "spread", "at": 2.0, "dur": 1.0, "from": 0, "to": 1},
    {"kind": "spread", "at": 2.0, "dur": 1.0, "from": 1, "to": 0},
    {"kind": "spread", "at": 2.0, "dur": 1.0, "from": 1, "to_rule": 0},
])
def test_r2_a_spread_whose_edges_sit_on_two_axes_is_refused(spread):
    """Review 2 (HIGH): a spread fills the gap between its two edges - on a y2 page between two scales, which is no
    reading (E75 s3). A reference rule names its axis (review 7); the left rule and a right line are two scales."""
    page = _page(y2=_y2(invert=False), hlines=[{"y": 1150.0, "label": "rule", "axis": "left"}])
    with pytest.raises(ValueError, match=r"spread.*axes|axes.*spread"):
        B.check_y2(_world(page), [spread])


def test_r2_a_spread_on_one_axis_is_drawn():
    page = _page(y2=_y2(invert=False), hlines=[{"y": 3.0, "label": "rule", "axis": "right"}])
    B.check_y2(_world(page), [{"kind": "spread", "at": 2.0, "dur": 1.0, "from": 1, "to_rule": 0}])


@pytest.mark.parametrize("entry", [
    {"kind": "bracket", "at": 2.0, "dur": 1.0, "series": 1, "from": 0, "to": 3, "label": "+2.3 pts"},
    {"kind": "level_join", "at": 2.0, "dur": 1.0, "series": 1, "from": 0, "to": 3, "label": "x"},
    {"kind": "spread", "at": 2.0, "dur": 1.0, "from": 1, "to_rule": 0},
])
def test_r2_a_level_or_change_on_the_inverted_line_is_refused(entry):
    """Review 3: on an inverted axis a rise is DRAWN as a fall - s102 keeps E28 binding on any level or change claim."""
    page = _page(hlines=[{"y": 3.0, "label": "rule", "axis": "right"}])
    with pytest.raises(ValueError, match="inverted"):
        B.check_y2(_world(page), [entry])
    B.check_y2(_world(_page(y2=_y2(invert=False), hlines=page["hlines"])), [entry])   # the same on an upright right axis
    if entry["kind"] != "spread":
        B.check_y2(_world(page), [dict(entry, series=0)])   # ... and on the (never inverted) left line


# ---- 7, 8, 9: the hardening ------------------------------------------------------------------------------------------


def test_r2_a_rule_on_a_y2_page_names_its_axis():
    errors = LPG.validate(_page(hlines=[{"y": 1150.0, "label": "rule"}]), "line")
    assert _has(errors, "hlines", "axis"), errors
    assert _has(LPG.validate(_page(hlines=[{"y": 1150.0, "label": "rule", "axis": "up"}]), "line"), "axis", "left|right")
    assert LPG.validate(_page(hlines=[{"y": 1150.0, "label": "rule", "axis": "left"}]), "line") == []
    assert LPG.validate(_page(hline={"y": 3.0, "label": "r", "axis": "right"}), "line") == []
    one = _page(y2=None, claim=None, hlines=[{"y": 1150.0, "label": "rule", "axis": "left"}])
    assert _has(LPG.validate(one, "line"), "axis", "y2"), "an axis on a single-axis page names nothing it draws"


def test_r2_a_y2_nested_in_a_panel_or_a_series_is_refused_by_name():
    page = _page()
    page["series"][1]["y2"] = True
    assert _has(LPG.validate(page, "line"), "y2", "series")
    panels = {"title": "t", "src": "s", "panels": [{"title": "a", "y2": _y2(series=[0]),
                                                    "series": [{"name": "A", "pts": PTS_A}]},
                                                   {"title": "b", "series": [{"name": "B", "pts": PTS_B}]}]}
    assert _has(LPG.validate(panels, "line"), "y2", "panel")


def test_r2_a_y2_on_a_muted_line_warns():
    page = _page()
    page["series"][1]["muted"] = True
    spec = LPG.build_spec(page, "line")
    assert any("muted" in w and "y2" in w for w in spec.get("warnings") or []), spec.get("warnings")


def test_r2_the_same_unit_warn_reads_the_left_unit_out_of_ylabel():
    spec = LPG.build_spec(_page(ylabel="US 10-year yield, %"), "line")
    assert any("y2" in w and "'%'" in w for w in spec.get("warnings") or []), spec.get("warnings")
    assert "warnings" not in LPG.build_spec(_page(ylabel="holdings, $bn"), "line")


def test_a_single_axis_page_is_untouched_by_the_check():
    B.check_y2(_world(_page(y2=None, claim=None)), [{"kind": "chart_to", "at": 3.0, "to": "rescale"}])
    B.check_y2({"kind": "plate"}, [])


def test_the_compiler_path_refuses_a_y2_without_its_claim():
    with tempfile.TemporaryDirectory() as td:
        objects = Path(td) / "evidence/objects"
        objects.mkdir(parents=True)
        (objects / "p.series.json").write_text(json.dumps(_page(claim=None)), encoding="utf-8")
        with pytest.raises(ValueError, match="s102"):
            B.world_for_plate("ledger:p:line::right", (0, 0, 0), Path(td))


# ---- the engine's wiring: one shared right-axis block, lifted from the combo ------------------------------------------


def test_the_combo_and_the_line_share_one_right_axis_block():
    src = ENGINE.read_text(encoding="utf-8")
    assert src.count("const lpRightAxis = ") == 1
    combo = src[src.index("const buildLedgerCombo = "):]
    combo = combo[:combo.index("\n  };\n")]
    line = src[src.index("const buildLedgerLine = "):]
    line = line[:line.index("\n  };\n")]
    plan = src[src.index("const lpY2Plan = "):]
    plan = plan[:plan.index("\n  };\n")]
    assert "lpRightAxis(" in combo and "lpRightAxis(" in plan, "the combo and the line's second axis write ticks through ONE writer"
    assert "lpY2Plan(" in line and "lpY2Draw(" in line


# ---- the page read on the served player -------------------------------------------------------------------------------


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
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp, M = st.marks || [];
  const R = (e) => { const r = e.getBoundingClientRect(); return {x: r.left, y: r.top, w: r.width, h: r.height}; };
  const txt = (m) => ({v: m.geom.v, text: m.el.textContent, fill: m.el.style.fill, box: R(m.el),
                       px: parseFloat(getComputedStyle(m.el).fontSize)});
  const left = M.filter(m => m.role === 'ylabel').map(txt), right = M.filter(m => m.role === 'y2label').map(txt);
  const head = M.find(m => m.role === 'y2name'), yl = M.find(m => m.role === 'axislabel');
  const ser = [0, 1].map(i => { const m = st.markBy['s' + i]; return m ? {pts: m.geom.pts, vals: m.geom.vals, col: m.geom.col} : null; });
  const names = [0, 1].map(i => { const m = st.markBy['name:s' + i]; return m ? {text: m.el.textContent, box: R(m.el),
    em: parseFloat(getComputedStyle(m.el).fontSize) * Math.hypot(st.chart.getScreenCTM().a, st.chart.getScreenCTM().b)} : null; });
  const geo = (role) => M.filter(q => q.role === role).map(q => ({v: q.geom.v, y: q.geom.y}));
  const P = st.plot, m = st.chart.getScreenCTM(), sx = (x) => m.a * x + m.e;
  return {left, right, head: head ? txt(head) : null, ylabel: yl ? txt(yl) : null, ser, names, y2: st.y2 ? {invert: st.y2.invert, lo: st.y2.lo, hi: st.y2.hi} : null,
          plotRight: sx(P.W - P.R), plotLeft: sx(P.L), leftGeo: geo('ylabel'), rightGeo: geo('y2label'), sy: m.d,
          tickDy: st.portrait ? 14 : 8, rules: (st.hlines || []).map(h => h.y)};
}"""


def _serve(longform: bool = False, rules: list | None = None):
    """The golden on the served player; `rules`: reference rules added to its page's axes (a probe's, never the golden's)."""
    import render_baseline as RB
    import build_golden_sources as G
    import served_player as SP  # R26-351 (P72 T9): the one guarded Playwright start
    tl, uris = G.dual_axis_inverted(longform=longform)
    if rules:
        tl = copy.deepcopy(tl)
        tl["scenes"][0]["world"]["page"].setdefault("axes", {})["hlines"] = rules
    if longform:
        uris = dict(uris, **B.longform_assets(tl))
        assert RB.longform_face_missing(tl, uris) is None
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE["16:9"]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE)

    return at, errs, close


def _ink(fill: str) -> str:
    """One colour, however the browser writes it: `#34F5C5` and `rgb(52, 245, 197)` are the same ink."""
    f = re.sub(r"\s+", "", str(fill or "")).lower()
    m = re.fullmatch(r"#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})", f)
    return f"rgb({int(m[1], 16)},{int(m[2], 16)},{int(m[3], 16)})" if m else f


def _hits(a: dict, b: dict, pad: float = 0.0) -> bool:
    return a["x"] < b["x"] + b["w"] + pad and b["x"] < a["x"] + a["w"] + pad and a["y"] < b["y"] + b["h"] + pad and b["y"] < a["y"] + a["h"] + pad


def _read_page(f: dict) -> None:
    """s102 on the drawn page: two labelled axes, the right one inverted and saying so, the ticks inked."""
    assert f["y2"] and f["y2"]["invert"] is True, f["y2"]
    left, right, head = f["left"], f["right"], f["head"]
    assert len(left) >= 3 and len(right) >= 3, (left, right)
    col0, col1 = f["ser"][0]["col"], f["ser"][1]["col"]
    assert _ink(col0) != _ink(col1)
    assert all(_ink(t["fill"]) == _ink(col0) for t in left), ("s102 (c): the LEFT ticks wear the left line's ink", left, col0)
    assert all(_ink(t["fill"]) == _ink(col1) for t in right), ("s102 (c): the RIGHT ticks wear the right line's ink", right, col1)
    assert all(t["text"].endswith("%") for t in right), ("each right tick carries its unit", [t["text"] for t in right])
    assert head and "inverted" in head["text"] and "%" in head["text"], ("s102 (b): the inverted axis says so", head)
    assert _ink(head["fill"]) == _ink(col1), head
    assert f["ylabel"] and "$bn" in f["ylabel"]["text"], ("s102 (b): the left axis names its unit", f["ylabel"])
    # INVERTED: a larger value is written LOWER on the page, and the line is drawn on that same scale
    ordered = sorted(right, key=lambda t: t["v"])
    assert all(a["box"]["y"] < b["box"]["y"] for a, b in zip(ordered, ordered[1:])), [(t["v"], t["box"]["y"]) for t in ordered]
    pts, vals = f["ser"][1]["pts"], f["ser"][1]["vals"]
    hi, lo = vals.index(max(vals)), vals.index(min(vals))
    assert pts[hi][1] > pts[lo][1], ("the highest yield is drawn LOWEST (the axis is inverted)", pts[hi], pts[lo])
    lpts, lvals = f["ser"][0]["pts"], f["ser"][0]["vals"]
    assert lpts[lvals.index(max(lvals))][1] < lpts[lvals.index(min(lvals))][1], "the left axis is not inverted"
    # the right column stands right of the plot and clear of every end tag
    assert all(t["box"]["x"] >= f["plotRight"] - 0.5 for t in right), ([t["box"]["x"] for t in right], f["plotRight"])
    for n in f["names"]:
        assert n and n["text"].strip(), f["names"]
        assert not any(_hits(n["box"], t["box"]) for t in right), ("an end tag stands on a right tick", n, right)
        assert not _hits(n["box"], head["box"]), ("an end tag stands on the right axis's name", n, head)
        # review 5: an end tag keeps at least ONE EM (its own) from any right tick on its row - never "4% $1,117bn"
        row = [t for t in right if t["box"]["y"] < n["box"]["y"] + n["box"]["h"] and n["box"]["y"] < t["box"]["y"] + t["box"]["h"]]
        for t in row:
            gap = n["box"]["x"] - (t["box"]["x"] + t["box"]["w"])
            assert gap >= n["em"] - 0.5, ("an end tag a hair from a right tick", round(gap, 1), round(n["em"], 1), t["text"], n["text"])
    # review 6: each line's last datum stands at the height its OWN axis's ticks give its value (within 2 px, both axes)
    for ser, geo in ((f["ser"][0], f["leftGeo"]), (f["ser"][1], f["rightGeo"])):
        (v0, y0), (v1, y1) = [(g["v"], g["y"] - f["tickDy"]) for g in (geo[0], geo[-1])]
        v = ser["vals"][-1]
        want = y0 + (v - v0) / (v1 - v0) * (y1 - y0)
        assert abs(ser["pts"][-1][1] - want) * abs(f["sy"]) <= 2.0, ("a datum off its own axis", v, ser["pts"][-1][1], want)


@needs_browser
def test_the_comove_pair_draws_on_two_labelled_axes_one_inverted_the_ticks_inked():
    at, errs, close = _serve()
    try:
        f = at(12.0)
    finally:
        close()
    assert not errs, errs
    _read_page(f)


@needs_browser
def test_the_long_form_draws_both_axes_at_its_own_type():
    at, errs, close = _serve(longform=True)
    try:
        f = at(12.0)
    finally:
        close()
    assert not errs, errs
    _read_page(f)
    lpx = {round(t["px"], 2) for t in f["left"]}
    rpx = {round(t["px"], 2) for t in f["right"]}
    assert lpx == rpx, ("the right ticks are the left ticks' peers at the long form's type", lpx, rpx)
    assert round(f["head"]["px"], 2) == round(f["ylabel"]["px"], 2), (f["head"], f["ylabel"])


@needs_browser
def test_r2_a_rule_that_names_the_right_axis_is_drawn_on_the_right_scale():
    """Review 7: a y2 page's rule names its axis, and is drawn at the height THAT axis's ticks give its value."""
    at, errs, close = _serve(rules=[{"y": 3.0, "label": "3%", "axis": "right"}, {"y": 1200.0, "label": "1,200", "axis": "left"}])
    try:
        f = at(12.0)
    finally:
        close()
    assert not errs, errs
    for y_rule, geo, v in ((f["rules"][0], f["rightGeo"], 3.0), (f["rules"][1], f["leftGeo"], 1200.0)):
        (v0, y0), (v1, y1) = [(g["v"], g["y"] - f["tickDy"]) for g in (geo[0], geo[-1])]
        assert abs(y_rule - (y0 + (v - v0) / (v1 - v0) * (y1 - y0))) * abs(f["sy"]) <= 2.0, (v, y_rule)
