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
    assert B.CHART_TO_KINDS == ("recast", "rescale", "extend", "park", "morph"), "the five verbs (P48 T2-T5)"
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


# ---- P48 T2: rescale - the axes retarget on one clock, the chart never leaves ----------------------------------------

RS_AT, RS_S = 11.0, 1.4
WINDOW = [2025.9, 2026.6]   # the holdings page's last months (decimal years) - the row-2 sell-off at full width


@pytest.mark.parametrize("entry, needle", [
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "rescale"}, "name the target domain"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "rescale", "ymin": "low"}, "ymin must be a number"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "rescale", "window": [2026, 2025]}, "from < to"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "rescale", "window": [2025, 2026], "state": 1}, "derived from the domain"),
])
def test_a_rescale_names_its_domain_and_never_a_state(entry, needle):
    errs = B._validate_page_fields("chart_to", entry)
    assert any(needle in e for e in errs), (needle, errs)
    assert not B._validate_page_fields("chart_to", {"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "rescale", "window": [2025, 2026]})


@needs_objects
def test_a_rescale_derives_its_state_from_the_page_s_own_series():
    world = B.world_for_plate("ledger:ev-japan-holdings-v1:line", (0, 0, 0), EP)
    sp = [{"kind": "chart_to", "at": RS_AT, "dur": RS_S, "to": "rescale", "window": WINDOW, "ymin": 1050}]
    B.derive_rescale_states(world, sp, "ledger:ev-japan-holdings-v1:line", EP)
    assert sp[0]["state"] == 1, "the species now points at the derived state"
    st = world["page_states"][0]
    assert st["derived"] == "rescale" and st["builder"] == "dense-line"
    assert st["axes"]["xdomain"] == WINDOW and st["axes"]["domain"] == [1050, None]
    pts = st["series"][0]["pts"]
    assert all(WINDOW[0] <= float(x) <= WINDOW[1] for x, _ in pts) and 2 <= len(pts) < 20, "the window slices the series"
    assert st["window_offsets"][0] > 300, "the datum index on the page maps to the derived state by the dropped count"
    assert st["title"] == world["page"]["title"] and st["sub"] == world["page"]["sub"], "the same words describe the same chart"


@needs_objects
def test_a_rescale_past_state_max_or_off_a_page_is_refused():
    world = B.world_for_plate(PLATE, (0, 0, 0), EP)   # one `then=` already: a rescale would be the third state, allowed; two would not
    sp = [{"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "rescale", "window": WINDOW},
          {"kind": "chart_to", "at": 2.0, "dur": 1.0, "to": "rescale", "ymin": 0}]
    with pytest.raises(ValueError, match="STATE_MAX"):
        B.derive_rescale_states(world, sp, PLATE, EP)
    with pytest.raises(ValueError, match="LEDGER PAGE"):
        B.derive_rescale_states({"kind": "still"}, [sp[0]], "plate-x", EP)


RS_PROBE = """() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp; const S = st.states || [st];
  const path = (s) => s.paths[0].p; const d = (s) => path(s).getAttribute('d');
  const head = (s) => d(s).split(' L')[0];
  const drawn = (s) => 1 - parseFloat(path(s).getAttribute('stroke-dashoffset') || '0') / path(s).len;
  const ticks = (s) => (s.marks || []).filter(m => m.role === 'tick').map(m => [m.geom.v, +m.el.getAttribute('y1'), m.el.style.opacity === '' ? 1 : +m.el.style.opacity]);
  return { n: S.length, charts: S.map(s => +(s.chart.style.opacity || 0)), head0: head(S[0]), d0: d(S[0]).length, clipped0: !!path(S[0]).getAttribute('clip-path'),
           built0: S[0].paths[0].d0 === d(S[0]), ticks0: ticks(S[0]), ticks1: S[1] ? ticks(S[1]) : null, active: st.active | 0,
           line1: S[1] ? (1 - parseFloat(S[1].paths[0].p.getAttribute('stroke-dashoffset') || '0') / S[1].paths[0].len) : null,
           subOld: (st.subGlyphs || []).reduce((a, g) => a + parseFloat(g.style.getPropertyValue('--w') || '0'), 0) / Math.max(1, (st.subGlyphs || []).length) };
}"""


def _rescale_player():
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    plate = "ledger:ev-japan-holdings-v1:line"
    world = B.world_for_plate(plate, (0, 0, 0), EP)
    species = [{"kind": "chart_to", "at": RS_AT, "dur": RS_S, "to": "rescale", "window": WINDOW}]
    B.derive_rescale_states(world, species, plate, EP)
    sc = tl["scenes"][0]
    scene = dict(sc, species=species, span=[0.0, 24.0], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=24.0, scenes=[scene], caption_pages=[], captions=[])
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "rescale.html"
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

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(RS_PROBE)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, errs, close


@needs_objects
@needs_browser
def test_a_rescale_moves_the_standing_chart_to_the_new_scale_and_lands_on_the_derived_state():
    at, errs, close = _rescale_player()
    try:
        before = at(RS_AT - 0.5)
        assert before["n"] == 2 and before["charts"] == [1, 0] and before["built0"], "before the word: the page exactly as built, the derived state hidden"
        mid = at(RS_AT + RS_S * 0.5)
        assert mid["charts"] == [1, 1], "mid-clock both svgs show: the standing chart moving, the target's furniture arriving"
        assert not mid["built0"] and mid["head0"] != before["head0"], "the standing line has been re-projected - its path moved"
        assert mid["line1"] < 0.01, "the target's own line is not drawn during the blend (no double line)"
        assert mid["clipped0"] and not before["clipped0"], "the plot box pins the moving line: nothing draws outside it during the blend"
        leaving = [tk for tk in mid["ticks0"] if tk[2] < 1]
        assert leaving, "ticks whose value leaves the window's domain fade as they travel"
        after = at(RS_AT + RS_S + 0.3)
        assert after["charts"] == [0, 1] and after["line1"] > 0.99 and after["active"] == 1, "after the clock the derived state stands, fully built"
        assert after["built0"] and not after["clipped0"], "and the standing chart's path is restored to its built geometry, unpinned (a seek is the play)"
        assert after["subOld"] > 0.98, "the words stayed: it is the same chart on a new scale"
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_a_rescale_seeks_exactly():
    at, _errs, close = _rescale_player()
    try:
        for t in (RS_AT + 0.3, RS_AT + RS_S * 0.7, RS_AT + RS_S + 2.0):
            a = at(t); at(2.0); at(RS_AT + RS_S + 5.0); b = at(t)
            assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), t
    finally:
        close()


# ---- P48 T3: extend - the axes retarget, then the new points draw on at the pen ------------------------------------

EX_RS_AT, EX_RS_S = 8.0, 1.2      # first: window the page to its early months
EX_AT, EX_S = 12.0, 2.0           # then: extend the window to the last datum
EX_WINDOW = [2025.9, 2026.3]


@pytest.mark.parametrize("entry, needle", [
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "extend"}, "exactly one of to_index"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "extend", "to_index": 5, "series": 1}, "exactly one of to_index"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "extend", "to_index": 0}, "positive datum index"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "extend", "series": 0}, "index (>= 1)"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "extend", "to_index": 5, "state": 1}, "derived, not named"),
])
def test_an_extend_names_new_points_or_a_later_series(entry, needle):
    errs = B._validate_page_fields("chart_to", entry)
    assert any(needle in e for e in errs), (needle, errs)
    assert not B._validate_page_fields("chart_to", {"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "extend", "to_index": 5})


@needs_objects
def test_an_extend_grows_the_standing_window_and_remembers_the_shared_datum():
    plate = "ledger:ev-japan-holdings-v1:line"
    world = B.world_for_plate(plate, (0, 0, 0), EP)
    n = len(world["page"]["series"][0]["pts"])
    sp = [{"kind": "chart_to", "at": EX_RS_AT, "dur": EX_RS_S, "to": "rescale", "window": EX_WINDOW},
          {"kind": "chart_to", "at": EX_AT, "dur": EX_S, "to": "extend", "to_index": n - 1}]
    B.derive_rescale_states(world, sp, plate, EP)
    assert [s["state"] for s in sp] == [1, 2]
    a, b = world["page_states"]
    assert a["derived"] == "rescale" and b["derived"] == "extend"
    assert b["axes"]["xdomain"][0] == EX_WINDOW[0] and b["axes"]["xdomain"][1] > EX_WINDOW[1], "the window keeps its start and grows to the datum"
    assert len(b["series"][0]["pts"]) > len(a["series"][0]["pts"])
    assert sp[1]["from_index"] == max(i for i, pt in enumerate(world["page"]["series"][0]["pts"]) if float(pt[0]) <= EX_WINDOW[1]), "the last shared datum, in the page's indexing"
    with pytest.raises(ValueError, match="adds nothing"):
        B.derive_rescale_states(B.world_for_plate(plate, (0, 0, 0), EP), [{"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "extend", "to_index": n - 1}], plate, EP)


def _later_series_ep(tmp: Path) -> tuple[Path, str]:
    """A temp episode whose page carries a second, `later: true` series (Bravos 29-30: consumption drawn on after production)."""
    src = json.loads((EP / "evidence/objects/ev-japan-holdings-v1.series.json").read_text(encoding="utf-8"))
    base = src["series"][0]
    twin = dict(base, name="Twin", label="", color="teal", later=True, pts=[[x, float(v) * 0.6] for x, v in base["pts"]])
    src["series"] = [base, twin]
    (tmp / "evidence/objects").mkdir(parents=True)
    (tmp / "evidence/objects/ev-later-v1.series.json").write_text(json.dumps(src), encoding="utf-8")
    return tmp, "ledger:ev-later-v1:line"


@needs_objects
def test_a_later_series_is_off_the_page_until_an_extend_reveals_it(tmp_path):
    ep, plate = _later_series_ep(tmp_path)
    world = B.world_for_plate(plate, (0, 0, 0), ep)
    assert len(world["page"]["series"]) == 1, "a later: true series is not on the page's own chart"
    sp = [{"kind": "chart_to", "at": EX_AT, "dur": EX_S, "to": "extend", "series": 1}]
    B.derive_rescale_states(world, sp, plate, ep)
    st = world["page_states"][0]
    assert len(st["series"]) == 2 and st["derived"] == "extend" and sp[0]["from_series"] == 1
    with pytest.raises(ValueError, match="not a later"):
        B.derive_rescale_states(B.world_for_plate(plate, (0, 0, 0), ep), [{"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "extend", "series": 3}], plate, ep)


EX_PROBE = """() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp; const S = st.states || [st];
  const drawn = (s, k) => { const pp = (s.paths || []).filter(p => !p.muted)[k]; return pp ? 1 - parseFloat(pp.p.getAttribute('stroke-dashoffset') || '0') / pp.len : null; };
  const tip = (s, k) => { const pp = (s.paths || []).filter(p => !p.muted)[k]; return pp ? +pp.tip.getAttribute('opacity') : null; };
  return { n: S.length, charts: S.map(s => +(s.chart.style.opacity || 0)), active: st.active | 0,
           drawn: S.map(s => [drawn(s, 0), drawn(s, 1)]), tips: S.map(s => [tip(s, 0), tip(s, 1)]),
           cap: S[S.length - 1].extendCap ? S[S.length - 1].extendCap.u2 : null };
}"""


def _extend_player(ep, plate, species, runtime=26.0):
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(plate, (0, 0, 0), ep)
    B.derive_rescale_states(world, species, plate, ep)
    scene = dict(tl["scenes"][0], species=species, span=[0.0, runtime], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=runtime, scenes=[scene], caption_pages=[], captions=[])
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "extend.html"
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

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(EX_PROBE)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, errs, close


@needs_objects
@needs_browser
def test_an_extend_retargets_the_axes_then_draws_the_new_points_at_the_pen():
    plate = "ledger:ev-japan-holdings-v1:line"
    n = len(B.world_for_plate(plate, (0, 0, 0), EP)["page"]["series"][0]["pts"])
    species = [{"kind": "chart_to", "at": EX_RS_AT, "dur": EX_RS_S, "to": "rescale", "window": EX_WINDOW},
               {"kind": "chart_to", "at": EX_AT, "dur": EX_S, "to": "extend", "to_index": n - 1}]
    at, errs, close = _extend_player(EP, plate, species)
    try:
        before = at(EX_AT - 0.3)
        assert before["charts"] == [0, 1, 0] and before["drawn"][1][0] > 0.99, "before the word: the windowed state stands, fully drawn"
        phase1 = at(EX_AT + EX_S * 0.2)
        assert phase1["charts"][1] == 1 and phase1["charts"][2] == 1 and phase1["drawn"][2][0] < 0.01, "phase 1: the standing chart moves to the new scale; the target's line is not yet drawn"
        phase2 = at(EX_AT + EX_S * 0.7)
        assert phase2["charts"] == [0, 0, 1] and phase2["active"] == 2, "phase 2: the target stands"
        assert 0.3 < phase2["drawn"][2][0] < 0.999, "its line is drawn to the pen: past the shared datum, short of the end"
        assert phase2["tips"][2][0] == 1 and phase2["cap"] is not None and phase2["cap"] > 0.3, "the nib is visible on the new tail"
        assert all(d is not None and d < 0.999 for d in [phase2["drawn"][2][0]]), "no path of the extended series runs ahead of the pen"
        after = at(EX_AT + EX_S + 0.3)
        assert after["charts"] == [0, 0, 1] and after["drawn"][2][0] > 0.99 and after["cap"] is None, "after the clock: fully drawn, the cap released"
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_a_later_series_draws_on_from_its_first_point(tmp_path):
    ep, plate = _later_series_ep(tmp_path)
    species = [{"kind": "chart_to", "at": EX_AT, "dur": EX_S, "to": "extend", "series": 1}]
    at, errs, close = _extend_player(ep, plate, species)
    try:
        before = at(EX_AT - 0.3)
        assert before["charts"] == [1, 0] and before["drawn"][0][1] is None, "one line on the page; the later series is not built into the page's own state"
        mid = at(EX_AT + EX_S * 0.75)
        assert mid["charts"] == [0, 1] and mid["drawn"][1][0] > 0.99, "phase 2: the page's own line stands fully drawn on the target"
        assert 0.05 < mid["drawn"][1][1] < 0.999 and mid["tips"][1][1] == 1, "the later series is drawing from its first point, the nib on it"
        after = at(EX_AT + EX_S + 0.5)
        assert after["drawn"][1] == [pytest.approx(1, abs=0.01), pytest.approx(1, abs=0.01)]
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_an_extend_seeks_exactly():
    plate = "ledger:ev-japan-holdings-v1:line"
    n = len(B.world_for_plate(plate, (0, 0, 0), EP)["page"]["series"][0]["pts"])
    species = [{"kind": "chart_to", "at": EX_RS_AT, "dur": EX_RS_S, "to": "rescale", "window": EX_WINDOW},
               {"kind": "chart_to", "at": EX_AT, "dur": EX_S, "to": "extend", "to_index": n - 1}]
    at, _errs, close = _extend_player(EP, plate, species)
    try:
        for t in (EX_AT + 0.3, EX_AT + EX_S * 0.7, EX_AT + EX_S + 1.0):
            a = at(t); at(3.0); at(EX_AT + EX_S + 4.0); b = at(t)
            assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), t
    finally:
        close()


# ---- P48 T2b: park - the chart makes room by one affine transform (Bravos 91) --------------------------------------

PK_AT, PK_S = 12.0, 1.0


@pytest.mark.parametrize("entry, needle", [
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "park", "scale": 0.1}, "scale must be a number in"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "park", "scale": "small"}, "scale must be a number in"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "park", "anchor": "centre"}, "anchor must be one of"),
    ({"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "park", "state": 1}, "the active chart parks"),
])
def test_a_park_names_how_small_and_which_side(entry, needle):
    errs = B._validate_page_fields("chart_to", entry)
    assert any(needle in e for e in errs), (needle, errs)
    assert not B._validate_page_fields("chart_to", {"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "park"})
    assert not B._validate_page_fields("chart_to", {"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "park", "scale": 0.6, "anchor": "bottom"})


@needs_objects
def test_a_park_derives_no_state():
    plate = "ledger:ev-japan-holdings-v1:line"
    world = B.world_for_plate(plate, (0, 0, 0), EP)
    sp = [{"kind": "chart_to", "at": PK_AT, "dur": PK_S, "to": "park"}]
    B.derive_rescale_states(world, sp, plate, EP)
    assert "page_states" not in world and "state" not in sp[0], "the active chart parks; nothing is built for it"


PK_PROBE = """() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp; const S = (st.states || [st])[st.active | 0];
  const sb = document.getElementById('stage').getBoundingClientRect(), k = %d / sb.width;
  const r = S.chart.getBoundingClientRect();
  const box = { x: (r.left - sb.left) * k, y: (r.top - sb.top) * k, w: r.width * k, h: r.height * k };
  const tr = S.chart.style.transform || '';
  const datum = (() => {   /* the species' own map (resolveTarget's vbMap): the datum's chart point through the svg's live rectangle */
    const q = (S.linePts || [[]])[0][5]; if (!q) return null; const vb = S.chart.viewBox.baseVal, k2 = Math.min(box.w / vb.width, box.h / vb.height);
    return [Math.round(box.x + (box.w - vb.width * k2) / 2 + q[0] * k2), Math.round(box.y + (box.h - vb.height * k2) / 2 + q[1] * k2)]; })();
  return { box: [Math.round(box.x), Math.round(box.y), Math.round(box.w), Math.round(box.h)], transform: tr, parked: !!S.parked, datum,
           title_y: Math.round((st.marks.find(m => m.key === 'title').el.getBoundingClientRect().top - sb.top) * k) };
}"""


def _park_player(species, runtime=24.0):
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    plate = "ledger:ev-japan-holdings-v1:line"
    world = B.world_for_plate(plate, (0, 0, 0), EP)
    B.derive_rescale_states(world, species, plate, EP)
    scene = dict(tl["scenes"][0], species=species, span=[0.0, runtime], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=runtime, scenes=[scene], caption_pages=[], captions=[])
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "park.html"
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
    probe = PK_PROBE % w

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(probe)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, errs, close


@needs_objects
@needs_browser
def test_a_park_shrinks_the_active_chart_toward_its_corner_and_holds():
    species = [{"kind": "chart_to", "at": PK_AT, "dur": PK_S, "to": "park", "scale": 0.7}]
    at, errs, close = _park_player(species)
    try:
        before = at(PK_AT - 0.5)
        assert not before["parked"] and before["transform"] == ""
        mid = at(PK_AT + PK_S * 0.5)
        assert mid["parked"] and 0.7 < mid["box"][2] / before["box"][2] < 1.0, "mid-clock the chart is between full and parked"
        after = at(PK_AT + PK_S + 0.5)
        assert after["parked"] and abs(after["box"][2] / before["box"][2] - 0.7) < 0.01 and abs(after["box"][3] / before["box"][3] - 0.7) < 0.01, "parked at 0.7 of itself"
        assert abs(after["box"][0] - before["box"][0]) <= 1 and abs(after["box"][1] - before["box"][1]) <= 1, "anchored at its top-left: the room opens below and to the right"
        assert after["title_y"] == before["title_y"], "the title stays"
        # a datum target maps through the park: its stage position is the corner + 0.7 x its offset from the corner
        bx, by = before["box"][0], before["box"][1]
        ex, ey = bx + 0.7 * (before["datum"][0] - bx), by + 0.7 * (before["datum"][1] - by)
        assert abs(after["datum"][0] - ex) <= 2 and abs(after["datum"][1] - ey) <= 2, (after["datum"], (ex, ey))
        held = at(PK_AT + PK_S + 6.0)
        assert held["box"] == after["box"], "the park holds until the next transition"
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_a_park_seeks_exactly_and_unparks_before_its_word():
    species = [{"kind": "chart_to", "at": PK_AT, "dur": PK_S, "to": "park"}]
    at, _errs, close = _park_player(species)
    try:
        a = at(PK_AT + 0.4); at(PK_AT + 5.0); b = at(PK_AT + 0.4)
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
        back = at(PK_AT - 1.0)
        assert not back["parked"] and back["transform"] == "", "before the word, after a seek back, the chart is exactly itself"
    finally:
        close()


# ---- P48 T4b: the keyed recast - n lines become n bars, by series (Bravos 99-105) --------------------------------------

KR_AT, KR_S = 12.0, 1.8
GOLDEN_SERIES = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-divergence-v1.series.json"


def _lines_to_bars_ep(tmp: Path, n_bars: int | None = None) -> tuple[Path, str]:
    """A temp episode: the four-line divergence page, and a bars object of the lines' last values (one bar per series)."""
    src = json.loads(GOLDEN_SERIES.read_text(encoding="utf-8"))
    names = [s.get("name") or s.get("label") or f"s{i}" for i, s in enumerate(src["series"])]
    lasts = [float(s["pts"][-1][1]) for s in src["series"]]
    if n_bars is not None:
        names, lasts = names[:n_bars], lasts[:n_bars]
    bars = {"title": "Where the four stand today", "sub": "index, 100 = Aug '25", "src": "Yahoo Finance", "unit": "",
            "bars": [{"label": n, "value": round(v, 1), "color": s.get("color", "crimson")} for n, v, s in zip(names, lasts, src["series"])]}
    (tmp / "evidence/objects").mkdir(parents=True)
    (tmp / "evidence/objects/ev-lines-v1.series.json").write_text(json.dumps(src), encoding="utf-8")
    (tmp / "evidence/objects/ev-bars-v1.series.json").write_text(json.dumps(bars), encoding="utf-8")
    return tmp, "ledger:ev-lines-v1:line;then=ev-bars-v1:bars"


def test_a_keyed_recast_is_admitted_on_the_legal_pair_only(tmp_path):
    ep, plate = _lines_to_bars_ep(tmp_path)
    world = B.world_for_plate(plate, (0, 0, 0), ep)
    assert (world["page"]["builder"], world["page_states"][0]["builder"]) == ("dense-line", "story")
    B.derive_rescale_states(world, [{"kind": "chart_to", "at": KR_AT, "dur": KR_S, "to": "recast", "state": 1, "keyed": True}], plate, ep)
    ep2, plate2 = _lines_to_bars_ep(tmp_path / "short", n_bars=2)
    with pytest.raises(ValueError, match="4 line\\(s\\) and 2 bar\\(s\\)"):
        B.derive_rescale_states(B.world_for_plate(plate2, (0, 0, 0), ep2), [{"kind": "chart_to", "at": KR_AT, "dur": KR_S, "to": "recast", "state": 1, "keyed": True}], plate2, ep2)
    with pytest.raises(ValueError, match="no honest key correspondence"):
        B.derive_rescale_states(B.world_for_plate(PLATE, (0, 0, 0), EP), [{"kind": "chart_to", "at": KR_AT, "dur": KR_S, "to": "recast", "state": 1, "keyed": True}], PLATE, EP)


KR_PROBE = """() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp; const S = st.states || [st];
  const A = S[0], Bs = S[1];
  const lines = A.paths.filter(p => !p.muted).map(p => ({ off: parseFloat(p.p.getAttribute('stroke-dashoffset') || '0'), tr: p.p.getAttribute('transform') || '', name: +p.name.getAttribute('opacity') }));
  const bars = (Bs.bars || []).map(b => b.bar.style.transform || '');
  const vals = (Bs.bars || []).map(b => b.val ? +b.val.getAttribute('opacity') : null);
  return { charts: S.map(s => +(s.chart.style.opacity || 0)), lines, bars, vals, active: st.active | 0,
           axisA: (() => { const m = A.marks.find(m => m.role === 'axis'); return m ? (m.el.style.opacity === '' ? 1 : +m.el.style.opacity) : null; })(),
           subOld: (st.subGlyphs || []).reduce((a, g) => a + parseFloat(g.style.getPropertyValue('--w') || '0'), 0) / Math.max(1, (st.subGlyphs || []).length) };
}"""


def _keyed_player(ep, plate, species, runtime=24.0):
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(plate, (0, 0, 0), ep)
    B.derive_rescale_states(world, species, plate, ep)
    scene = dict(tl["scenes"][0], species=species, span=[0.0, runtime], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=runtime, scenes=[scene], caption_pages=[], captions=[])
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "keyed.html"
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

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(KR_PROBE)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, errs, close


@needs_browser
def test_the_lines_become_their_bars_on_one_clock(tmp_path):
    ep, plate = _lines_to_bars_ep(tmp_path)
    species = [{"kind": "chart_to", "at": KR_AT, "dur": KR_S, "to": "recast", "state": 1, "keyed": True}]
    at, errs, close = _keyed_player(ep, plate, species)
    try:
        before = at(KR_AT - 0.5)
        assert before["charts"] == [1, 0] and all(l["off"] == 0 and l["tr"] == "" for l in before["lines"]), "before the word: four lines fully drawn, untouched"
        tag = at(KR_AT + KR_S * 0.2)   # phase 1: the names give way to the values; nothing has moved yet
        assert all(l["off"] == 0 and l["name"] < 0.2 for l in tag["lines"]) and all(o is None or o > 0.8 for o in tag["vals"]), tag
        mid = at(KR_AT + KR_S * 0.5)
        assert mid["charts"] == [1, 1], "mid-clock both states show"
        assert all(l["off"] < 0 and l["tr"].startswith("translate(") for l in mid["lines"]), "each line retreats from its start (a negative dash offset) and its end travels toward its bar"
        assert all("scaleY(" in b and b != "scaleY(0)" for b in mid["bars"]), "the bars are growing from the baseline"
        assert mid["axisA"] is not None and mid["axisA"] < 1, "the line page's furniture is leaving"
        after = at(KR_AT + KR_S + 0.4)
        assert after["charts"] == [0, 1] and after["active"] == 1 and all(b == "scaleY(1.0000)" or b == "scaleY(1)" for b in after["bars"]), "after the clock: the bar page stands built"
        assert all(l["tr"] == "" for l in after["lines"]), "the keyed transform is off the lines once the clock ends"
        assert after["subOld"] < 0.05, "the words that described the lines are erased; the bar page's words are the page's"
        back = at(KR_AT - 0.5)
        assert back["charts"] == [1, 0] and all(l["off"] == 0 and l["tr"] == "" and l["name"] == 1 for l in back["lines"]), "a seek back paints the four lines exactly as built (a seek is the play)"
        assert not errs, errs
    finally:
        close()


@needs_browser
def test_a_keyed_recast_seeks_exactly(tmp_path):
    ep, plate = _lines_to_bars_ep(tmp_path)
    species = [{"kind": "chart_to", "at": KR_AT, "dur": KR_S, "to": "recast", "state": 1, "keyed": True}]
    at, _errs, close = _keyed_player(ep, plate, species)
    try:
        for t in (KR_AT + 0.4, KR_AT + KR_S * 0.8, KR_AT + KR_S + 2.0):
            a = at(t); at(3.0); at(KR_AT + KR_S + 5.0); b = at(t)
            assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), t
    finally:
        close()


# ---- P48 T5: morph_to - the area under the standing line becomes the target's by ARAP, mid-page ---------------------

MT_AT, MT_S = 12.0, 2.0
MORPH_FILL_A = 0.28   # MORPH.FILL_A in the template


def _line_to_line_ep(tmp: Path) -> tuple[Path, str]:
    """A temp episode: the four-line divergence page, then a one-line page of its first series (dense-line on both sides)."""
    src = json.loads(GOLDEN_SERIES.read_text(encoding="utf-8"))
    one = dict(src, title="The memory makers alone", sub="index, 100 = Aug '25", series=[dict(src["series"][0])])
    one.pop("badges", None)
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / "evidence/objects/ev-lines-v1.series.json").write_text(json.dumps(src), encoding="utf-8")
    (tmp / "evidence/objects/ev-one-v1.series.json").write_text(json.dumps(one), encoding="utf-8")
    return tmp, "ledger:ev-lines-v1:line;then=ev-one-v1:line"


def test_a_morph_is_admitted_between_two_line_pages_only(tmp_path):
    ep, plate = _line_to_line_ep(tmp_path)
    world = B.world_for_plate(plate, (0, 0, 0), ep)
    assert (world["page"]["builder"], world["page_states"][0]["builder"]) == ("dense-line", "dense-line")
    B.derive_rescale_states(world, [{"kind": "chart_to", "at": MT_AT, "dur": MT_S, "to": "morph", "state": 1}], plate, ep)
    ep2, plate2 = _lines_to_bars_ep(tmp_path / "bars")
    with pytest.raises(ValueError, match="a morph moves the AREA UNDER A LINE"):
        B.derive_rescale_states(B.world_for_plate(plate2, (0, 0, 0), ep2), [{"kind": "chart_to", "at": MT_AT, "dur": MT_S, "to": "morph", "state": 1}], plate2, ep2)
    assert not B._validate_page_fields("chart_to", {"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "morph", "state": 1})
    assert any("'state' must be" in e for e in B._validate_page_fields("chart_to", {"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "morph"}))


MT_PROBE = """() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp; const S = st.states || [st];
  const M = (st.morphTo || {})['0>1'];
  const frac = (s) => s.paths.filter(p => !p.muted).map(p => parseFloat(p.p.getAttribute('stroke-dashoffset') || '0') / (p.len || 1));
  return { chartOp: S.map(s => s.chart.style.opacity), undrawn: frac(S[0]), target: frac(S[1]), active: st.active | 0,
           morph: M ? (M.svg.style.opacity === '1' ? { on: '1', fill: parseFloat(M.path.getAttribute('fill-opacity')), d: M.path.getAttribute('d'), u: M.u } : { on: '0' }) : null };   /* a hidden strip's attributes are not on the frame */
}"""


def _morph_timeline(ep, plate, species, runtime=30.0, kinetics=None):
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(plate, (0, 0, 0), ep)
    B.derive_rescale_states(world, species, plate, ep)
    scene = dict(tl["scenes"][0], species=species, span=[0.0, runtime], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=runtime, scenes=[scene], caption_pages=[], captions=[])
    # the golden surface's kinetics leave arap_morph OFF (the flag guards the goldens); a morph_to needs it ON, as a compiled
    # timeline has it (kinetics_defaults) - the flag-off test passes its own
    timeline["kinetics"] = kinetics if kinetics is not None else dict(tl.get("kinetics") or {}, arap_morph=True, min_jerk=True)
    return timeline, uris


def _morph_player(ep, plate, species, runtime=30.0, kinetics=None):
    from playwright.sync_api import sync_playwright
    timeline, uris = _morph_timeline(ep, plate, species, runtime, kinetics)
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "morph.html"
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

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(MT_PROBE)

    def frame(t: float) -> bytes:
        return RB.frame_png(page, t, (w, h))

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, frame, page, errs, close


@needs_browser
def test_the_area_under_the_line_becomes_the_target_s_area_and_the_invariants_hold(tmp_path):
    ep, plate = _line_to_line_ep(tmp_path)
    species = [{"kind": "chart_to", "at": MT_AT, "dur": MT_S, "to": "morph", "state": 1}]
    at, _frame, page, errs, close = _morph_player(ep, plate, species)
    try:
        before = at(MT_AT - 0.5)
        assert all(f == 0 for f in before["undrawn"]) and (before["morph"] is None or before["morph"]["on"] == "0"), "before the word: the four lines stand drawn, no strip"
        leave = at(MT_AT + MT_S * 0.15)   # inside the leave (the first 0.3 of the clock)
        assert any(0.02 < f < 0.98 for f in leave["undrawn"]), "the standing lines are leaving by length"
        assert leave["morph"]["on"] == "1" and 0.02 < leave["morph"]["fill"] < MORPH_FILL_A, "the area under the line fills as the line leaves"
        assert leave["chartOp"][0] == "1", "the standing axes stand through the leave"
        mid = at(MT_AT + MT_S * 0.55)   # mid-morph: the standing axes are leaving
        assert all(f >= 0.99 for f in mid["undrawn"]) and abs(mid["morph"]["fill"] - MORPH_FILL_A) < 0.01, "the lines are gone; the filled strip is the shape"
        assert mid["morph"]["d"] not in (None, "") and mid["active"] == 1, "a datum target now resolves against the target state"
        assert 0 < float(mid["chartOp"][0]) < 1 and float(mid["chartOp"][1]) == 0, "the standing axes leave over the morph's first half"
        inv = page.evaluate("() => window.__morphInvariants('0>1')")
        assert inv and inv["min_det"] > 0 and inv["end_error"] < 1e-3, inv
        assert inv["centroid_ok"] and inv["axis_ok"] and inv["area_ok"], inv   # M17's three invariants hold on this pair
        late = at(MT_AT + MT_S * 0.85)
        assert float(late["chartOp"][0]) == 0 and 0 < float(late["chartOp"][1]) < 1 and late["morph"]["d"] != mid["morph"]["d"], "the target's axes arrive over the second half as the strip keeps moving"
        hold = at(MT_AT + MT_S + 0.4)   # the target builds; the fill leaves with the build
        assert hold["morph"]["on"] == "1" and hold["morph"]["fill"] < MORPH_FILL_A and any(0.01 < f < 0.99 for f in hold["target"]), hold
        built = at(MT_AT + MT_S + 6.0)
        assert built["morph"]["on"] == "0" and all(f == 0 for f in built["target"]) and built["chartOp"] == ["0", "1"], "the target stands built; the strip is gone"
        assert not errs, errs
    finally:
        close()


@needs_browser
def test_a_morph_to_seeks_exactly(tmp_path):
    ep, plate = _line_to_line_ep(tmp_path)
    species = [{"kind": "chart_to", "at": MT_AT, "dur": MT_S, "to": "morph", "state": 1}]
    at, _frame, _page, _errs, close = _morph_player(ep, plate, species)
    try:
        for t in (MT_AT + 0.3, MT_AT + MT_S * 0.7, MT_AT + MT_S + 0.5, MT_AT - 1.0):
            a = at(t); at(3.0); at(MT_AT + MT_S + 8.0); at(MT_AT + 1.0); b = at(t)
            assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), t
    finally:
        close()


@needs_browser
def test_with_the_flag_off_a_morph_to_is_the_recast_hand_over_byte_for_byte(tmp_path):
    """kinetics.arap_morph off: a morph_to degrades to the plain recast of the same length - the frames are identical."""
    import hashlib
    ep, plate = _line_to_line_ep(tmp_path)
    hashes = []
    for verb in ("morph", "recast"):
        species = [{"kind": "chart_to", "at": MT_AT, "dur": MT_S, "to": verb, "state": 1}]
        _at, frame, _page, errs, close = _morph_player(ep, plate, species, kinetics={"arap_morph": False})
        try:
            hashes.append([hashlib.sha256(frame(t)).hexdigest() for t in (MT_AT + 0.6, MT_AT + MT_S + 0.5, MT_AT + MT_S + 3.0)])
            assert not errs, errs
        finally:
            close()
    assert hashes[0] == hashes[1]


@needs_browser
def test_measure_morph_measures_a_morph_to_per_morph_keyed_scene_at(tmp_path):
    """M17 per morph (P48 T5): measure_morph.py finds the morph_to on the page, seeks mid-morph and writes its invariants
    under scene@at - beside a page-enter morph's row, which keeps its scene-id key."""
    import measure_morph as MM
    ep, plate = _line_to_line_ep(tmp_path)
    species = [{"kind": "chart_to", "at": MT_AT, "dur": MT_S, "to": "morph", "state": 1}]
    timeline, uris = _morph_timeline(ep, plate, species)
    html = tmp_path / "player.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    scenes = MM.morph_scenes(timeline)
    assert [s["scene_id"] for s in scenes] == [timeline["scenes"][0]["scene_id"]]
    res = MM.measure_html(html, "9:16", scenes)
    key = f"{timeline['scenes'][0]['scene_id']}@{MT_AT:.2f}"
    assert list(res) == [key], res
    assert res[key]["min_det"] > 0 and res[key]["centroid_ok"] and res[key]["area_ok"], res[key]


# ---- P48 T7: the perform layer on a page with states - a figure follows the active state's datum ----------------------

FG_PROBE = """() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp; const PF = st.perform || { figures: [] };
  return { active: st.active | 0, onOwnSvg: !!st.performSvg && (PF.figures || []).every(fg => fg.g.ownerSVGElement === st.performSvg),
           layerShown: !!st.performSvg && getComputedStyle(st.performSvg).opacity === '1' && getComputedStyle(st.performSvg).display !== 'none',
           figs: (PF.figures || []).map(fg => ({ op: +fg.g.getAttribute('opacity'), x: +fg.label.getAttribute('x'), y: +fg.label.getAttribute('y'), D: fg.D })) };
}"""


@needs_objects
@needs_browser
def test_a_figure_follows_the_active_state_after_a_rescale_and_a_dropped_datum_shows_nothing():
    """The Tokyo cut (T7): the holdings page rescales to Feb-Jun on a word, then two figures write at the peak and at June -
    they stand at the WINDOWED line's points, on the perform layer above the states; a figure at a datum outside the window
    shows nothing; before the rescale the figures are where the page's own geometry puts them."""
    from playwright.sync_api import sync_playwright
    plate = "ledger:ev-japan-holdings-v1:line"
    world = B.world_for_plate(plate, (0, 0, 0), EP)
    n = len(world["page"]["series"][0]["pts"])
    species = [{"kind": "chart_to", "at": 8.0, "dur": 1.4, "to": "rescale", "window": [2026.043, 2026.457]},
               {"kind": "figure", "at": 10.0, "dur": 1.2, "target": {"kind": "datum", "index": n - 1}, "text": "1,116.7"},
               {"kind": "figure", "at": 10.0, "dur": 1.2, "target": {"kind": "datum", "index": 3}, "text": "early"}]
    B.derive_rescale_states(world, species, plate, EP)
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    scene = dict(tl["scenes"][0], species=species, span=[0.0, 24.0], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=24.0, scenes=[scene], caption_pages=[], captions=[])
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "fig.html"; html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
        w, h = RB.STAGE["9:16"]; srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True); page = br.new_context(viewport={"width": w, "height": h}).new_page()
                errs = []; page.on("pageerror", lambda e: errs.append(str(e)))
                page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000); RB.prepare_page(page, w, h)
                seek = "t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }"
                page.evaluate(seek, 12.0)
                r = page.evaluate(FG_PROBE)
                assert r["active"] == 1 and r["onOwnSvg"] and r["layerShown"], r   # a COLD seek past the rescale: the layer must not inherit the hidden chart's opacity
                june, early = r["figs"]
                assert june["op"] == 1 and early["op"] == 0, "June is in the window and writes; index 3 (2000) is outside it and shows nothing"
                pt = page.evaluate("() => { const st = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')).__lp; const S = st.states[1]; return S.linePts[0][S.linePts[0].length - 1]; }")
                assert abs(june["D"][0] - pt[0]) < 1e-6 and abs(june["D"][1] - pt[1]) < 1e-6, "the figure's datum is the windowed line's last point"
                assert abs(abs(june["x"] - pt[0]) - 14) < 0.06, "the figure writes 14 units beside its datum (x written to one decimal)"
                page.evaluate(seek, 7.0)   # before the word: the page's own geometry
                r0 = page.evaluate(FG_PROBE)
                pt0 = page.evaluate("() => { const st = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')).__lp; return st.linePts[0][st.linePts[0].length - 1]; }")
                assert r0["active"] == 0 and abs(r0["figs"][0]["D"][0] - pt0[0]) < 1e-6, r0
                assert not errs, errs
                br.close()
        finally:
            srv.shutdown()
