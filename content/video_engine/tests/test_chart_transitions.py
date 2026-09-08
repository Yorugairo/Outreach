"""P48: a chart changes STATE and never cuts.

`;then=<series>:<variant>` on a plate id puts a second full ledger_page.v1 spec on `world.page_states`; the `chart_to`
species moves between them. A **recast** is not a cut: the standing chart runs its own build law BACKWARDS - which is
what an un-draw is, for any builder - and the named state then draws on by its own law, on the same page, under words
the page rewrites with the same hand that rewrites a title.

The acceptance case is Tokyo row 2: the 26-year holdings line leaves, the title backspaces and rewrites, and a pie of
the five biggest foreign holders draws on with Japan's sold wedge in it.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

EP = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
PLATE = "ledger:ev-japan-holdings-v1:line;then=ev-top-holders-v1:share"
XF_AT, XF_S = 11.0, 1.3
RT_AT, RT_S = 11.0, 2.0

needs_objects = pytest.mark.skipif(
    not ((EP / "evidence/objects/ev-japan-holdings-v1.series.json").exists()
         and (EP / "evidence/objects/ev-top-holders-v1.series.json").exists()),
    reason="the Tokyo evidence objects are not on disk",
)


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---- the grammar ------------------------------------------------------------------------------------


def test_chart_to_is_a_page_species_with_a_verb_and_a_state():
    assert "chart_to" in B.SPECIES_KINDS and "chart_to" in B.PAGE_SPECIES
    assert B.SPECIES_TARGETS["chart_to"] == ()
    assert B.CHART_TO_KINDS == ("recast",), "rescale / extend / morph_to land with their own laws (P48 T2/T3/T5)"
    assert B.STATE_MAX == 3


@pytest.mark.parametrize("entry, needle", [
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "state": 1}, "'to' must be one of"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "wobble", "state": 1}, "'to' must be one of"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "recast"}, "'state' must be the index"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "recast", "state": 0}, "0 is the page's own chart"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "recast", "state": 3}, "past STATE_MAX"),
])
def test_a_chart_to_that_names_no_verb_or_no_other_state_is_a_build_error(entry, needle):
    errs = B._validate_page_fields("chart_to", entry)
    assert any(needle in e for e in errs), (needle, errs)


@needs_objects
def test_then_puts_a_second_full_page_spec_on_the_world():
    world = B.world_for_plate(PLATE, (0, 0, 0), EP)
    assert world["page"]["builder"] == "dense-line"
    states = world["page_states"]
    assert len(states) == 1 and states[0]["builder"] == "share"
    assert states[0]["schema_version"] == world["page"]["schema_version"], "a state is a page spec, not a fragment"
    assert states[0]["sub"] and states[0]["sub"] != world["page"]["sub"], "each state carries the words that describe it"
    assert "then" not in world, "the option is consumed into page_states, never left on the world"


@needs_objects
def test_a_page_may_not_carry_more_charts_than_state_max():
    plate = PLATE + ";then=ev-top-holders-v1:share;then=ev-top-holders-v1:share"
    with pytest.raises(ValueError, match="past STATE_MAX"):
        B.world_for_plate(plate, (0, 0, 0), EP)


@needs_objects
def test_then_is_refused_on_a_plate_that_is_not_a_page(monkeypatch):
    """Only a page has chart states. (A plate id that does not resolve at all fails earlier, on the plate.)"""
    monkeypatch.setattr(B, "_world_for_bare_plate", lambda *a, **k: {"kind": "image", "asset_id": "x"})
    with pytest.raises(ValueError, match="then= is a LEDGER PAGE option"):
        B.world_for_plate("some-plate;then=ev-top-holders-v1:share", (0, 0, 0), EP)


@needs_objects
def test_a_then_that_is_not_a_page_for_its_variant_names_the_reason():
    with pytest.raises(ValueError, match="donut"):
        B.world_for_plate("ledger:ev-japan-holdings-v1:line;then=ev-top-holders-v1:bars", (0, 0, 0), EP)


@needs_objects
def test_a_missing_then_object_fails_loudly_rather_than_rendering_an_empty_chart():
    with pytest.raises(ValueError, match="series file missing"):
        B.world_for_plate("ledger:ev-japan-holdings-v1:line;then=ev-nope-v1:share", (0, 0, 0), EP)


# ---- the frame ---------------------------------------------------------------------------------------


PROBE = """() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp;
  const drawn = (s) => (s.paths || []).map(pp => 1 - parseFloat(pp.p.getAttribute('stroke-dashoffset') || '0') / pp.len);
  const ink = (gs) => (gs || []).reduce((a, g) => a + parseFloat(g.style.getPropertyValue('--w') || '0'), 0) / Math.max(1, (gs || []).length);
  const S = st.states || [st];
  return {
    n: S.length,
    charts: S.map(s => +(s.chart.style.opacity || 0)),
    lineDrawn: drawn(S[0]),
    sweep: S[1] && S[1].share ? S[1].share.wedges.map(x => +x.lab.getAttribute('opacity')) : null,
    subOld: ink(st.subGlyphs), subNew: S[1] && S[1].subInk ? ink(S[1].subInk.glyphs) : null,
    srcNew: S[1] && S[1].srcInk ? ink(S[1].srcInk.glyphs) : null,
  };
}"""


def _player(species):
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(PLATE, (0, 0, 0), EP)
    sc = tl["scenes"][0]
    scene = dict(sc, species=species, span=[0.0, 26.0],
                 world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=26.0, scenes=[scene], caption_pages=[], captions=[])
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "recast.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    w, h = RB.STAGE["9:16"]
    srv, port = RB.serve(html.parent)
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    page = br.new_context(viewport={"width": w, "height": h}).new_page()
    errs: list[str] = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return page, errs, close


SPECIES = [
    {"kind": "retitle", "at": RT_AT, "dur": RT_S, "text": "Who owns America's debt"},
    {"kind": "chart_to", "at": XF_AT, "dur": XF_S, "to": "recast", "state": 1},
    {"kind": "peel", "at": 17.4, "dur": 1.6},
]


def _at(page, t: float) -> dict:
    page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
    return page.evaluate(PROBE)


@needs_objects
@needs_browser
def test_the_line_leaves_and_the_pie_arrives_on_one_page_with_no_cut():
    page, errs, close = _player(SPECIES)
    try:
        before = _at(page, XF_AT - 1.0)
        assert before["n"] == 2 and before["charts"][1] == 0, "the second chart is built at load and hidden"
        assert all(f > 0.99 for f in before["lineDrawn"]), "before the word, the page is state A exactly"
        assert before["subNew"] == 0, "and nothing of the next state's words is on the page"

        mid = _at(page, XF_AT + XF_S * 0.55)
        assert all(f < 0.95 for f in mid["lineDrawn"]), "the standing chart is leaving, not standing"
        assert mid["charts"][1] == 0, "and the next chart has not started: a recast is a hand-over, not a dissolve"
        assert mid["subOld"] < 0.2, "the words that described the old chart have been erased"

        after = _at(page, XF_AT + XF_S + 3.4)
        assert after["charts"][0] == 0 and after["charts"][1] == 1
        assert all(f < 0.01 for f in after["lineDrawn"]), "the line is gone, not hidden under the pie"
        assert all(o > 0.99 for o in after["sweep"]), "every wedge is drawn and named"
        assert after["subNew"] > 0.98 and after["srcNew"] > 0.98, "the page's words describe the chart that is on it"
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_a_recast_seeks_exactly() -> None:
    """The whole transition is a pure function of t: a seek lands the identical frame (P43's seek test)."""
    page, _errs, close = _player(SPECIES)
    try:
        for t in (XF_AT + 0.4, XF_AT + XF_S + 1.0, 19.5):
            a = _at(page, t)
            _at(page, 2.0)
            b = _at(page, t)
            assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), t
    finally:
        close()


@needs_objects
@needs_browser
def test_a_page_that_declares_no_transition_is_exactly_what_it_was():
    """The whole plan rests on this: two states on a page change nothing until a chart_to fires."""
    page, _errs, close = _player([])
    try:
        d = _at(page, 20.0)
        assert d["charts"][0] == 1 and d["charts"][1] == 0
        assert all(f > 0.99 for f in d["lineDrawn"])
        assert d["subNew"] == 0 and d["subOld"] > 0.9
    finally:
        close()
