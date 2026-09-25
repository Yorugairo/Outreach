"""P70 T2 (was P69 T46) - THE SCHEMATIC: a shape drawn with no data, carrying the narrative (E99 s109 (1)).

The operator, 2026-09-23: "I think we can draw with no data - that is the art and narrative coming to life in the world".
s109 (1): a schematic (the hype cycle, the debt cycle, a mania arc, phase waves) "carries no axis values and no figures
it cannot source, and says it is a shape, not a series". The Bravos harvest v2 T7 (n=5), Jw8ykhoOVBQ 04:24-04:30.

A LINE object may carry `schematic: {shape, phases: [{name, from, to, side?}], n?, name?, color?}` in place of `series`.
`ledger_page.schematic_series` generates ONE dense series from the named closed form on x in [0, 1]; the existing
dense-line builder draws it, so T36's `lit_stretch`, `span` and `bracket` address it by x-fraction unchanged. The page
writes no value (no tick number on either axis, and no end tag - the title names the shape) and carries a small tag, "a shape, not a series",
which `page_boxes` reports. A bracket, figure, note or span whose text carries a digit is refused on a schematic page
unless it names its `src` (a truth rule, hard). E99 s125 (a real series laid over a schematic) is P71's; this slice
keeps the shape addressable for it (`spec.series[0]` the curve, `spec.schematic` its phases, the engine's marks).
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

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/page_builder.json"
PHASES = [{"name": "Innovation trigger", "from": 0.0, "to": 0.12},
          {"name": "Peak of inflated expectations", "from": 0.12, "to": 0.3},
          {"name": "Trough of disillusionment", "from": 0.3, "to": 0.48},
          {"name": "Slope of enlightenment", "from": 0.48, "to": 0.72},
          {"name": "Plateau of productivity", "from": 0.72, "to": 1.0}]
HYPE = {"title": "The hype cycle", "sub": "Five phases of a new technology's reputation",
        "src": "Shape: Gartner's hype cycle - a schematic, no data", "ylabel": "Expectations",
        "schematic": {"shape": "hype", "phases": PHASES}}


def _obj(**patch) -> dict:
    out = copy.deepcopy(HYPE)
    out.update(patch)
    return out


def _sch(**patch) -> dict:
    return _obj(schematic=dict(copy.deepcopy(HYPE["schematic"]), **patch))


# ---- the object: one generated series, validated as the line it is --------------------------------------------------


def test_a_schematic_is_a_line_page_with_no_data():
    """The expected RED: at the base a schematic object is "no chartable values"."""
    assert LPG.validate(_obj(), "line") == []
    assert LPG.pick_builder(_obj(), "line") == "dense-line"


def test_the_series_is_generated_from_the_named_closed_form_pure_and_deterministic():
    for shape in LPG.SCHEMATIC_SHAPES:
        a = LPG.schematic_series({"shape": shape, "phases": PHASES})
        b = LPG.schematic_series({"shape": shape, "phases": PHASES})
        assert a == b, shape
        xs = [p[0] for p in a["pts"]]
        assert len(xs) == LPG.SCHEMATIC_N and xs[0] == 0.0 and xs[-1] == 1.0, shape
        assert all(x1 > x0 for x0, x1 in zip(xs, xs[1:])), shape
        assert all(0.0 <= p[1] <= 1.0 for p in a["pts"]), shape
        assert "label" not in a, "the series carries no value (and the page draws no end tag for it)"
    assert len(LPG.schematic_series({"shape": "waves", "phases": PHASES, "n": 61})["pts"]) == 61


def _argmax(pts, lo, hi, sign=1):
    return max((p for p in pts if lo <= p[0] <= hi), key=lambda p: sign * p[1])[0]


def test_each_shape_is_the_shape_its_name_says():
    hype = LPG.schematic_series({"shape": "hype", "phases": PHASES})["pts"]
    peak, trough = _argmax(hype, 0, 1), _argmax(hype, 0.25, 0.7, -1)
    assert 0.15 <= peak <= 0.25 and 0.33 <= trough <= 0.45, (peak, trough)
    plateau = [p[1] for p in hype if p[0] >= 0.85]
    assert max(plateau) - min(plateau) < 0.05 and min(plateau) > [p[1] for p in hype if p[0] == trough][0] + 0.3
    waves = LPG.schematic_series({"shape": "waves", "phases": PHASES})["pts"]
    tops = [p for i, p in enumerate(waves[1:-1], 1) if p[1] > waves[i - 1][1] and p[1] >= waves[i + 1][1]]
    assert len(tops) == 2, tops
    debt = LPG.schematic_series({"shape": "debt_cycle", "phases": PHASES})["pts"]
    top = _argmax(debt, 0, 1)
    assert 0.7 <= top <= 0.85 and debt[-1][1] < max(p[1] for p in debt) - 0.25, (top, debt[-1])


def test_the_spec_carries_the_shape_its_phases_and_its_tag_and_no_value():
    spec = LPG.build_spec(_obj(), "line", None, "right")
    assert spec["builder"] == "dense-line" and len(spec["series"]) == 1
    assert spec["schematic"] == {"shape": "hype", "tag": LPG.SCHEMATIC_TAG,
                                 "phases": [dict(p, **{"from": float(p["from"]), "to": float(p["to"])}) for p in PHASES]}
    assert LPG.SCHEMATIC_TAG == "a shape, not a series"
    ser = spec["series"][0]
    assert ser["name"] == "Hype cycle" and "label" not in ser and ser["color"] == LPG.SCHEMATIC_INK
    assert "xticks" not in spec["axes"] and spec["unit"] == ""
    assert spec["axes"] == {"ylabel": "Expectations", "domain": list(LPG.SCHEMATIC_DOMAIN)}, "the domain is the page's room, never written"


def test_the_file_s_own_float_tokens_are_read_as_numbers():
    """load_series decodes floats as strings (parse_float=str): an edge on disk arrives as "0.12"."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "s.series.json"
        p.write_text(json.dumps(_obj()), encoding="utf-8")
        obj = LPG.load_series(p)
    assert obj["schematic"]["phases"][1]["from"] == "0.12"
    assert LPG.validate(obj, "line") == []
    assert LPG.build_spec(obj, "line")["schematic"]["phases"][1]["from"] == 0.12


def test_a_page_without_a_schematic_is_the_page_it_always_was():
    plain = {"title": "A line", "src": "Synthetic", "series": [{"name": "A", "pts": [[i, i * i] for i in range(20)]}]}
    spec = LPG.build_spec(plain, "line", None, "right")
    assert "schematic" not in spec
    assert "schematic" not in LPG.page_boxes(spec, "16:9") and "schematic" not in LPG.page_boxes(spec, "9:16")
    assert LPG.pick_builder(plain, "line") == "dense-line"


def test_the_shape_keys_its_own_ink_and_a_plain_page_keeps_its_key():
    spec = LPG.build_spec(_obj(), "line", None, "right")
    plain = dict(spec)
    plain.pop("schematic")
    assert LPG.page_ink_key(spec) != LPG.page_ink_key(plain), "the tag and the missing tick column move boxes"


# ---- refused by name --------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("patch, needle", [
    ({"series": [{"name": "A", "pts": [[0, 1], [1, 2]]}]}, "a schematic carries no data"),
    ({"pts": [[0, 1], [1, 2]]}, "a schematic carries no data"),
    ({"bars": [{"label": "A", "value": 1}]}, "a schematic carries no data"),
    ({"unit": "%"}, "a schematic carries no data"),
    ({"hlines": [{"y": 0.5, "label": "rule"}]}, "carries no axis values"),
    ({"xticks": [[0.2, "2000"]]}, "carries no axis values"),
    ({"log": True}, "carries no axis values"),
    ({"domain": [0, 1]}, "carries no axis values"),
])
def test_data_beside_a_schematic_is_refused(patch, needle):
    errs = LPG.validate(_obj(**patch), "line")
    assert any(needle in e for e in errs), errs
    assert any("E99 s109 (1)" in e for e in errs), errs


@pytest.mark.parametrize("patch, needle", [
    ({"shape": "mania"}, "shape 'mania' is not one of hype|waves|debt_cycle"),
    ({"n": 8}, "n must be an integer from"),
    ({"n": True}, "n must be an integer from"),
    ({"name": ""}, "name must be a non-empty string"),
    ({"color": "gold"}, "color must be one of"),
    ({"ticks": 3}, "'ticks' is not a schematic key"),
    ({"phases": []}, "phases must be a list of 1 to 6"),
    ({"phases": [{"name": "A", "from": 0.4, "to": 0.2}]}, "from 0.4 is not before to 0.2"),
    ({"phases": [{"name": "A", "from": 0.0, "to": 1.4}]}, "'to' must be an x-fraction of the shape (0..1)"),
    ({"phases": [{"name": "", "from": 0.0, "to": 0.5}]}, "needs a non-empty name"),
    ({"phases": [{"name": "A", "from": 0.0, "to": 0.5, "value": 3}]}, "'value' is not a phase key"),
    ({"phases": [{"name": "A", "from": 0.0, "to": 0.5, "side": "left"}]}, "side must be above or below"),
    ({"phases": [{"name": "A", "from": 0.0, "to": 0.5}, {"name": "B", "from": 0.4, "to": 0.8}]}, "overlaps"),
])
def test_a_malformed_schematic_is_refused_by_name(patch, needle):
    errs = LPG.validate(_sch(**patch), "line")
    assert any(needle in e for e in errs), errs


def test_a_schematic_is_a_line_page_only():
    errs = LPG.validate(_obj(), "bars")
    assert any("a schematic is a LINE page" in e for e in errs), errs
    errs = LPG.validate(_obj(schematic="hype"), "line")
    assert any("schematic must be an object" in e for e in errs), errs


# ---- the truth rule: no figure it cannot source ------------------------------------------------------------------------


def _world() -> dict:
    return {"kind": "ledger", "page": LPG.build_spec(_obj(), "line", None, "right")}


@pytest.mark.parametrize("sp", [
    {"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 20, "to": 50, "label": "18 months"},
    {"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 20, "to": 50, "label": "the lag", "sub": "about 2 years"},
    {"kind": "figure", "at": 1.0, "dur": 1.0, "target": {"kind": "datum", "index": 24}, "text": "-64%"},
    {"kind": "note", "at": 1.0, "dur": 1.0, "text": "3x the plateau"},
    {"kind": "span", "at": 1.0, "dur": 1.0, "from": 0.3, "to": 0.48, "label": "2001-2003"},
])
def test_a_figure_on_a_schematic_is_refused_unless_it_names_its_source(sp):
    errs = LPG.schematic_text_errors(_world()["page"], [sp])
    assert len(errs) == 1 and "no figures it cannot source" in errs[0] and "E99 s109 (1)" in errs[0], errs
    with pytest.raises(ValueError, match="no figures it cannot source"):
        B.check_schematic(_world(), [sp])
    sourced = dict(sp, src="Gartner, Hype Cycle for Emerging Technologies")
    assert LPG.schematic_text_errors(_world()["page"], [sourced]) == []
    B.check_schematic(_world(), [sourced])


def test_words_on_a_schematic_and_figures_on_a_plain_page_pass():
    words = [{"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 20, "to": 50, "label": "the lag"},
             {"kind": "span", "at": 1.0, "dur": 1.0, "from": 0.3, "to": 0.48, "label": "the trough"},
             {"kind": "lit_stretch", "at": 1.0, "dur": 1.0, "from": 0.2, "to": 0.4}]
    assert LPG.schematic_text_errors(_world()["page"], words) == []
    B.check_schematic(_world(), words)
    plain = {"kind": "ledger", "page": {"builder": "dense-line", "series": []}}
    fig = {"kind": "figure", "at": 1.0, "dur": 1.0, "text": "-64%"}
    assert LPG.schematic_text_errors(plain["page"], [fig]) == []
    B.check_schematic(plain, [fig])


def test_the_phases_are_x_fractions_the_light_and_the_span_address():
    """`lit_stretch` and `span` take two 0..1 x-fractions of the drawn series; the schematic's x IS that fraction."""
    plate = "ledger:ev-x:line::right"
    for kind in ("lit_stretch", "span"):
        sp = {"kind": kind, "at": 1.0, "dur": 1.0, "from": PHASES[1]["from"] + 0.08, "to": PHASES[2]["from"] + 0.09}
        if kind == "span":
            sp["label"] = "peak to trough"
        assert B.validate_species([sp], (0, 0, 0), plate) == [], kind


# ---- the compiler's own path ---------------------------------------------------------------------------------------------


def _project(obj: dict) -> tempfile.TemporaryDirectory:
    td = tempfile.TemporaryDirectory()
    d = Path(td.name) / "evidence/objects"
    d.mkdir(parents=True)
    (d / "ev-hype-schematic.series.json").write_text(json.dumps(obj), encoding="utf-8")
    return td


def test_a_schematic_row_compiles_through_the_plate_grammar_in_the_long_form():
    td = _project(_obj())
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate("ledger:ev-hype-schematic:line::right;idle=live;readability=longform", (0, 0, 0),
                                  Path(td.name))
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
        td.cleanup()
    page = world["page"]
    assert page["builder"] == "dense-line" and page["schematic"]["shape"] == "hype"
    assert page["axes"]["readability"] == "longform" and page.get("full_stage") is True
    boxes = LPG.page_boxes(page, "16:9")
    tag = boxes["schematic"]
    assert tag["w"] > 0 and tag["h"] > 0
    st = boxes["stage"]
    assert 0 <= tag["x"] and tag["x"] + tag["w"] <= st["w"] and 0 <= tag["y"] and tag["y"] + tag["h"] <= st["h"], tag


def test_a_schematic_row_with_data_beside_it_is_refused_by_the_compiler():
    td = _project(_obj(series=[{"name": "A", "pts": [[0, 1], [1, 2]]}]))
    try:
        with pytest.raises(ValueError, match="a schematic carries no data"):
            B.world_for_plate("ledger:ev-hype-schematic:line::right", (0, 0, 0), Path(td.name))
    finally:
        td.cleanup()


def test_the_shape_passes_the_empty_plot_gate_m47():
    """P69 T87's M47 reads a plot standing with no ink - exactly what a page with no data could be. The schematic's line
    draws on the page's build, so its golden passes it."""
    import gate_motion_density as GMD
    import render_baseline as RB
    tl, _uris, _t, _aspect = RB.load_surface("schematic-hype-trough")
    gate = GMD._empty_plot_gate(tl["scenes"], tl.get("kinetics"))
    assert gate is not None and gate.level == "PASS", gate


# ---- the engine and the card -----------------------------------------------------------------------------------------


def test_the_engine_suppresses_values_behind_the_page_s_schematic_only():
    src = ENGINE.read_text(encoding="utf-8")
    assert "const lpSchematicTag" in src and "pg.schematic" in src
    body = src[src.index("const buildLedgerLine"):src.index("const LPX = {")]
    assert "SCH ? " in body or "if (SCH)" in body


def test_the_card_names_the_builder_option_its_when_and_its_ruling():
    cards = json.loads(CARDS.read_text(encoding="utf-8"))["cards"]
    card = next(c for c in cards if c.get("id") == "page_builder:line+schematic")
    blob = json.dumps(card)
    assert "E99 s109 (1)" in blob and "a shape, not a series" in blob
    assert card.get("when") and "phase model" in json.dumps(card["when"])


# ---- the served player: no value on the page, the tag and the phases written, the light walks peak -> trough ----------


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
  const st = world.__lp, stg = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect(); return {x: r.x - stg.x, y: r.y - stg.y, w: r.width, h: r.height}; };
  const texts = [...st.chart.querySelectorAll('text')].filter(e => +(e.getAttribute('opacity') ?? 1) > 0.05 && (e.textContent || '').trim());
  const tag = st.chart.querySelector('.lp-schematic');
  const phases = [...st.chart.querySelectorAll('.lp-phase')];
  const ser = st.markBy.s0, stroke = ser && ser.el.getAttribute('stroke');
  const PF = st.perform || {}, L = (PF.lits || [])[0];
  const d = L ? (L.core.getAttribute('d') || '') : '', pts = d ? d.slice(1).split(' L').map(s => s.split(' ').map(Number)) : [];
  const m = st.chart.getScreenCTM();
  return { texts: texts.map(e => e.textContent), tag: tag ? {text: tag.textContent, op: +tag.getAttribute('opacity'), box: R(tag)} : null,
           phases: phases.map(e => ({text: e.textContent, op: +e.getAttribute('opacity'), fill: e.style.fill,
                                     px: parseFloat(getComputedStyle(e).fontSize) * (m ? Math.hypot(m.a, m.b) : 1), box: R(e)})),
           nameFill: st.markBy['name:s0'] ? st.markBy['name:s0'].el.style.fill : null, stroke,
           endTag: st.markBy['name:s0'] ? (st.markBy['name:s0'].el.textContent || '') : null,
           lit: L ? parseFloat(L.g.getAttribute('opacity') || '0') : 0, first: pts[0] || null, last: pts[pts.length - 1] || null,
           geom: st.schematic ? st.schematic.phases.map(p => [p.x0, p.x1]) : null };
}"""


def _serve(surface: str, longform: bool = False):
    """The golden's own timeline on the served player; `longform`: its page re-profiled as a `;readability=longform` row
    compiles it (ledger_page.apply_longform, the face in the uris) - H's own page profile."""
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface(surface)
    if longform:
        tl = copy.deepcopy(tl)
        for sc in tl["scenes"]:
            LPG.apply_longform(sc["world"]["page"])
        uris = dict(uris, **B.longform_assets(tl))
        assert RB.longform_face_missing(tl, uris) is None
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[aspect]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)   # R26-351: guarded

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE)

    return at, errs, close


@needs_browser
@pytest.mark.parametrize("longform", [False, True], ids=["ledger", "longform"])
def test_the_page_writes_no_value_says_it_is_a_shape_and_names_its_phases_in_the_series_ink(longform):
    import build_golden_sources as G
    at, errs, close = _serve("schematic-hype-trough", longform)
    try:
        early, held = at(2.2), at(G.SCHEMATIC_LIT_AT - 0.3)
    finally:
        close()
    assert not errs, errs
    digits = [t for t in held["texts"] if re.search(r"\d", t)]
    assert digits == [], f"a schematic writes no value on either axis: {digits}"
    assert held["tag"] and held["tag"]["text"] == "a shape, not a series" and held["tag"]["op"] > 0.9, held["tag"]
    assert held["endTag"] == "", ("s120 (3): a schematic is ONE shape its title names - no end tag", held["endTag"])
    names = [p["text"] for p in held["phases"]]
    assert len(names) == len(G.SCHEMATIC_OBJECT["schematic"]["phases"]), names
    for p in held["phases"]:
        assert p["op"] > 0.9, p
        assert p["fill"] and p["fill"] == held["nameFill"], ("s118: a phase wears its series' ink", p, held["nameFill"])
        assert p["px"] >= LPG.CARD_TYPE_PX - 0.01, ("E99 s90: every word at the phone floor", p)
    boxes = [p["box"] for p in held["phases"]] + [held["tag"]["box"]]
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            clear = a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"] or a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"]
            assert clear, ("two words on a schematic never overprint", a, b)
    assert early["phases"][-1]["op"] < 0.1, "a phase is named as the pen reaches it, not before"
    assert held["geom"] and all(x0 < x1 for x0, x1 in held["geom"]), held["geom"]


@needs_browser
def test_the_light_walks_from_the_peak_to_the_trough_on_its_word():
    import build_golden_sources as G
    at, errs, close = _serve("schematic-hype-trough")
    try:
        a0, dur = G.SCHEMATIC_LIT_AT, G.SCHEMATIC_LIT_DUR
        before, mid, landed = at(a0 - 0.1), at(a0 + 0.5 * dur * 0.8), at(a0 + dur + 0.5)
    finally:
        close()
    assert not errs, errs
    assert before["lit"] == 0 and mid["lit"] == 1 and landed["lit"] == 1
    assert mid["first"][0] < mid["last"][0] < landed["last"][0], (mid["first"], mid["last"], landed["last"])
    assert landed["last"][1] > mid["first"][1] + 50, "the light lands LOW, at the trough, from the peak it leaves"


@needs_browser
def test_a_plain_line_page_keeps_its_end_tag():
    """The end tag is dropped on a schematic page ONLY: the lit-stretch golden's railway page still names its line."""
    at, errs, close = _serve("lit-stretch-crash")
    try:
        f = at(14.0)
    finally:
        close()
    assert not errs, errs
    assert f["endTag"] and f["endTag"].strip(), f["endTag"]
