"""P71 T16 (was P69 T41; the Bravos harvest v2 A17 / T23 / S3; E77, E99 s93) - `project`: A LABELLED DASHED
CONTINUATION PAST THE LAST REAL POINT.

Before this slice a line page's series `projection` key was ACCEPTED AND IGNORED (`ledger_page.validate` returned []
and the engine drew nothing different - review finding 7's class, E99 s106: "a silent drop is neither advice nor
refusal"). Now a `later: true` series of a dense line page may carry

    "projection": {"label": "2026E", "tier": "PLAUSIBLE", "src": "the top of the 2026 projected range (dossier C1)"}

and `chart_to extend {series: k}` draws it on its word FROM the last actual datum of the line it continues: dashed
(S3: every dashed series is a projection), in its line's ink, never blooming (s117: context, not a primary line), its
end tag writing its LABEL (never a value, never a badge's chip), and the page's source line naming what it is and where
it comes from (s93). E77 / the brief: an estimate is never data - no ring, figure, callout, level join, span, bracket,
light or solo may read the projected stretch as if it were a real point.

Refused by name (truth rules, s106): a projection with no label, no tier, no source; a label that is a bare figure (it
reads as a datum); a first point that is not the last actual of a live line; points that do not run forward past it; a
projection on a standing series, on the page's first series, on a panel, or on a page that is not a dense line. WARN
(s106): a label that carries no estimate word. Byte-identical absent the key.
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

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402

ACTUAL = [[2020.0, 28.0], [2021.0, 28.0], [2022.0, 28.0], [2023.0, 28.0], [2024.0, 28.0], [2025.0, 121.0]]


def _proj(**over) -> dict:
    p = {"label": "2026E", "tier": "PLAUSIBLE", "src": "the top of the 2026 projected range (dossier C1)"}
    for k, v in over.items():
        if v is None:
            p.pop(k, None)
        else:
            p[k] = v
    return p


def _page(proj: dict | None = None, **ser_over) -> dict:
    """The issuance line and ONE projection from its last actual - every field the grammar asks for."""
    s1 = {"label": "estimate", "color": "crimson", "later": True, "pts": [[2025.0, 121.0], [2026.0, 150.0]],
          "projection": _proj() if proj is None else proj}
    for k, v in ser_over.items():
        if v is None:
            s1.pop(k, None)
        else:
            s1[k] = v
    return {"title": "The builders started borrowing", "src": "Morgan Stanley IM; Mellon (via the dossier)",
            "ylabel": "US$ billions per year",
            "series": [{"label": "issuance", "color": "crimson", "pts": copy.deepcopy(ACTUAL)}, s1]}


def _has(errors: list[str], *words: str) -> bool:
    return any(all(w in e for w in words) for e in errors)


# ---- THE PROBE'S CLASS FIRST: a malformed projection is refused BY NAME, never accepted and ignored ------------------


def test_red_an_unlabelled_untiered_projection_is_refused_by_name():
    """The plan's Expected RED (probed at 50b2f85, re-probed at 4e077e4): `projection: {label: "x"}` with no tier and
    a first point that is not the last actual was ACCEPTED AND IGNORED (validate -> [])."""
    page = _page(proj={"label": "x"}, pts=[[2025.5, 9.0], [2026.0, 4.0]])
    errs = LPG.validate(page, "line")
    assert _has(errs, "projection", "tier"), errs
    assert _has(errs, "projection", "last actual"), errs


@pytest.mark.parametrize("proj,words", [
    ({"tier": "PLAUSIBLE", "src": "s"}, ("projection", "label")),
    ({"label": "", "tier": "PLAUSIBLE", "src": "s"}, ("projection", "label")),
    ({"label": "2026E", "src": "s"}, ("projection", "tier")),
    ({"label": "2026E", "tier": "plausible-ish", "src": "s"}, ("projection", "tier")),
    ({"label": "2026E", "tier": "PLAUSIBLE"}, ("projection", "src")),
    ({"label": "2026E", "tier": "PLAUSIBLE", "src": "  "}, ("projection", "src")),
    ({"label": "2026E", "tier": "PLAUSIBLE", "src": "s", "value": 150}, ("projection", "value")),
    ("2026E", ("projection", "object")),
    ({"label": 2026, "tier": "PLAUSIBLE", "src": "s"}, ("projection", "label")),
])
def test_a_malformed_projection_is_refused_by_name(proj, words):
    assert _has(LPG.validate(_page(proj=proj), "line"), *words), LPG.validate(_page(proj=proj), "line")


@pytest.mark.parametrize("label", ["$150B", "150", "+24%", "150.0", "$130–150B", "1,250"])
def test_a_label_that_is_a_bare_figure_reads_as_a_datum_and_is_refused(label):
    errs = LPG.validate(_page(proj=_proj(label=label)), "line")
    assert _has(errs, "projection", "datum"), (label, errs)


def test_the_projection_opens_from_the_last_actual():
    """E77: the path opens from the real line, never from nowhere - its first point IS a live line's last datum."""
    for pts in ([[2024.0, 28.0], [2026.0, 150.0]],      # opens from an earlier datum, not the last
                [[2025.0, 125.0], [2026.0, 150.0]],     # at the last x, off its value
                [[2025.5, 121.0], [2026.0, 150.0]]):    # at its value, off its x
        assert _has(LPG.validate(_page(pts=pts), "line"), "projection", "last actual"), pts


def test_the_projection_runs_forward_past_the_last_actual():
    for pts in ([[2025.0, 121.0]],                                   # one point is no path
                [[2025.0, 121.0], [2024.5, 140.0]],                  # runs back into the actuals
                [[2025.0, 121.0], [2026.0, 140.0], [2026.0, 150.0]]):   # a vertical step: x must increase
        assert _has(LPG.validate(_page(pts=pts), "line"), "projection", "forward"), pts


def test_a_projection_draws_on_its_word_so_it_is_a_later_series():
    errs = LPG.validate(_page(later=None), "line")
    assert _has(errs, "projection", "later"), errs


def test_the_first_series_is_never_a_projection():
    page = _page()
    page["series"] = [dict(page["series"][1], later=None), page["series"][0]]
    page["series"][0].pop("later", None)
    assert _has(LPG.validate(page, "line"), "projection", "first series"), LPG.validate(page, "line")


def test_a_projection_on_a_panel_is_refused_by_name():
    page = {"title": "t", "src": "s", "panels": [
        {"sub": "a", "series": [{"label": "x", "pts": copy.deepcopy(ACTUAL)},
                                {"label": "e", "later": True, "pts": [[2025.0, 121.0], [2026.0, 150.0]], "projection": _proj()}]},
        {"sub": "b", "series": [{"label": "y", "pts": copy.deepcopy(ACTUAL)}]}]}
    assert _has(LPG.validate(page, "line"), "projection", "panel"), LPG.validate(page, "line")


def test_a_projection_on_a_page_that_is_not_a_dense_line_is_refused():
    page = _page()
    page["bars"] = [{"label": "a", "value": 1}, {"label": "b", "value": 2}]   # a combo draws its lines another way
    assert _has(LPG.validate(page, "line"), "projection", "dense line"), LPG.validate(page, "line")


def test_a_well_formed_projection_validates():
    assert LPG.validate(_page(), "line") == []
    for tier in LPG.PROJECTION_TIERS:
        assert LPG.validate(_page(proj=_proj(tier=tier)), "line") == [], tier


def test_a_label_with_no_estimate_word_warns_and_one_with_it_does_not():
    assert LPG.projection_warnings(_page()) == []
    for label in ("consensus", "2026 forecast", "if it holds", "scenario"):
        assert LPG.projection_warnings(_page(proj=_proj(label=label))) == [], label
    w = LPG.projection_warnings(_page(proj=_proj(label="next year")))
    assert len(w) == 1 and "next year" in w[0] and "estimate" in w[0], w
    assert LPG.validate(_page(proj=_proj(label="next year")), "line") == [], "advice, never a refusal (s106)"


# ---- THE SPEC: the tag writes the label, the source line names it, absent the key nothing changes --------------------


def test_a_page_without_the_key_is_byte_identical():
    page = _page()
    page["series"] = [page["series"][0], {"label": "cash", "color": "teal", "pts": [[x, v / 2] for x, v in ACTUAL]}]
    base = LPG.build_spec(copy.deepcopy(page), "line")
    assert base["builder"] == "dense-line"
    assert base["series"] == page["series"] and base["source"] == page["src"]
    assert "projection" not in json.dumps(base)


def test_the_derived_state_carries_the_projection_its_tag_is_the_label():
    page = _page()
    page["series"][1].pop("later")   # what the compiler's extend reveal does (rescale_state pops `later`)
    spec = LPG.build_spec(page, "line")
    s = spec["series"][1]
    assert s["projection"] == _proj()
    assert s["label"] == "2026E" and not s.get("name"), s   # the tag writes the LABEL - never "estimate" or a value
    assert spec["labels"][1] == "2026E"
    assert spec["series"][0] == page["series"][0]           # the actual is untouched


def test_a_projection_takes_its_lines_ink_when_it_names_none():
    page = _page(color=None)
    page["series"][0]["color"] = "teal"
    page["series"][1].pop("later")
    assert LPG.build_spec(page, "line")["series"][1]["color"] == "teal"


def test_the_source_line_names_the_projection_and_its_source():
    """s93: its source line says what it is - the page and every chart state built from the file carry it."""
    spec = LPG.build_spec(_page(), "line")   # state 0: the projection waits off the page, the source already names it
    assert spec["source"] == "Morgan Stanley IM; Mellon (via the dossier) · 2026E: the top of the 2026 projected range (dossier C1)"
    page = _page(proj=_proj(src="Morgan Stanley IM"))
    assert LPG.build_spec(page, "line")["source"] == page["src"], "a source the page already names is not written twice"


# ---- THE COMPILER: an estimate is never data (E77) --------------------------------------------------------------------


def _world(page: dict, species: list, aspect: str = "16:9") -> dict:
    saved = B.ASPECT
    B.ASPECT = aspect
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / "ref-proj.series.json").write_text(json.dumps(page), encoding="utf-8")
            plate = "ledger:ref-proj:line::right"
            world = B.world_for_plate(plate, (0, 0, 0), Path(td))
            B.stamp_full_stage(world["page"])
            B.derive_rescale_states(world, species, plate, Path(td))
            return world
    finally:
        B.ASPECT = saved


EXTEND = {"kind": "chart_to", "at": 8.0, "dur": 1.18, "to": "extend", "series": 1}


def test_the_extend_reveals_the_projection_as_a_derived_state():
    world = _world(_page(), [dict(EXTEND)])
    assert [len(s["series"]) for s in [world["page"], *world["page_states"]]] == [1, 2]
    s = world["page_states"][0]["series"][1]
    assert s["projection"]["tier"] == "PLAUSIBLE" and [float(v) for v in s["pts"][0]] == ACTUAL[-1]


@pytest.mark.parametrize("entry", [
    {"kind": "figure", "at": 9.5, "dur": 1.0, "target": {"kind": "datum", "index": 1, "series": 1}, "text": "$150B"},
    {"kind": "callout", "at": 9.5, "dur": 1.0, "target": {"kind": "datum", "index": 1, "series": 1}},
    {"kind": "level_join", "at": 9.5, "dur": 1.0, "series": 1, "from": 0, "to": {"series": 0, "index": 5}, "label": "+29"},
    {"kind": "bracket", "at": 9.5, "dur": 1.0, "series": 1, "from": 0, "to": 1, "label": "x"},
])
def test_nothing_reads_the_projected_stretch_as_a_datum(entry):
    with pytest.raises(ValueError, match=r"projection.*E77|E77.*projection"):
        _world(_page(), [dict(EXTEND), entry])


def test_at_9_16_a_source_line_cut_to_its_first_clause_would_drop_the_projection_s_source():
    """The portrait page keeps its source's first clause (the engine's lpFirstClause): a projection sourced after a ';'
    would stand unsourced - refused by name; a source with no ';' keeps it whole and draws."""
    with pytest.raises(ValueError, match=r"9:16.*first clause"):
        _world(_page(), [dict(EXTEND)], aspect="9:16")
    page = _page()
    page["src"] = "Morgan Stanley IM and Mellon, via the dossier"
    assert _world(page, [dict(EXTEND)], aspect="9:16")["page_states"]


# ---- THE PAGE ON THE SERVED PLAYER: dashed, from the last actual, labelled, never blooming ----------------------------


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
  const st = world.__lp, S = (st.states || [st]);
  const read = (cs) => (cs.paths || []).map(pp => {
    const m = pp.p.getAttribute('mask'), mk = m ? document.getElementById(m.slice(5, -1)) : null, tw = mk ? mk.querySelector('path') : null;
    return {si: pp.si, hot: !!pp.hot, context: !!pp.context, pts: pp.pts, off: parseFloat(pp.p.getAttribute('stroke-dashoffset')), len: pp.len,
            op: pp.p.style.opacity, filter: pp.p.getAttribute('filter') || pp.p.style.filter || '', mask: m,
            twin: tw ? {dash: tw.getAttribute('stroke-dasharray'), d: tw.getAttribute('d'), cap: tw.getAttribute('stroke-linecap')} : null,
            d: pp.p.getAttribute('d'), plen: pp.p.getTotalLength(), stroke: pp.p.getAttribute('stroke'), name: pp.name.textContent, nameOp: +pp.name.getAttribute('opacity'),
            chip: !!pp.name.querySelector('.tagchip'), w: parseFloat(getComputedStyle(pp.p).strokeWidth), cardW: pp.p.style.strokeWidth};
  });
  const src = [...st.page.querySelectorAll('.lp-src')].map(e => e.textContent);
  return {active: st.active | 0, states: S.map(read), src};
}"""


def _serve():
    import render_baseline as RB
    import build_golden_sources as G
    import served_player as SP  # R26-351 (P72 T9): the one guarded Playwright start
    tl, uris = G.project_issuance_2026e()
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE["16:9"]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE)

    return at, page.evaluate, errs, close


@needs_browser
def test_the_dashed_continuation_draws_on_its_word_from_the_last_actual_labelled():
    import build_golden_sources as G
    at, _ev, errs, close = _serve()
    try:
        before, mid, after = at(G.PROJ_AT - 0.2), at(G.PROJ_AT + 0.45 * G.PROJ_DUR + 0.3), at(G.FRAME_T["project-issuance-2026e"])
        back = at(G.PROJ_AT - 0.2)   # a seek back is the play
    finally:
        close()
    assert not errs, errs
    assert before == back, "a seek back paints the frame it painted before"
    # before its word: the projection is not on the page (the standing state has only the actual)
    assert len(before["states"][0]) == 1 and before["active"] == 0
    proj_b = before["states"][1][1]
    assert proj_b["op"] == "0" or proj_b["off"] >= proj_b["len"] - 0.5, proj_b
    # mid-pen: drawing from its first point, part of the way
    pm = mid["states"][1][1]
    assert 0 < pm["off"] < pm["len"], pm
    # landed: the target state stands, its actual drawn whole and the projection drawn whole
    assert after["active"] == 1
    act, proj = after["states"][1]
    assert proj["off"] <= 0.5 and act["off"] <= 0.5, (act["off"], proj["off"])
    # FROM THE LAST ACTUAL (E77): the path's first vertex is the actual's last, in the page's own units
    assert abs(proj["pts"][0][0] - act["pts"][-1][0]) < 0.05 and abs(proj["pts"][0][1] - act["pts"][-1][1]) < 0.05
    # DASHED (S3), by the Bravos law read with measure_dash: ~3.25 widths (4 on the core ink), a gap of half a dash - through a mask that follows the path
    assert proj["mask"] and proj["twin"], proj
    dash, gap = (float(v) for v in proj["twin"]["dash"].split())
    assert proj["twin"]["d"] == proj["d"]
    assert abs(dash / proj["w"] - 3.25) <= 0.5 and abs(gap / dash - 0.5) < 0.01, (dash, gap, proj["w"])
    n = (proj["plen"] + gap) / (dash + gap)   # whole dashes: the path opens on ink at the last actual and ENDS on ink
    assert abs(n - round(n)) < 0.05 and round(n) >= 2, (n, proj["plen"], dash, gap)   # the dash pair is written to 0.01
    assert not act["mask"], "the actual stays solid"
    # the same ink as its line, never blooming, never the primary (s117)
    assert proj["stroke"] == act["stroke"]
    assert act["hot"] and not proj["hot"] and proj["context"] and not proj["filter"], proj
    # LABELLED: the tag writes the projection's label, whole, and carries no badge chip (never a value)
    assert proj["name"].strip() == "2026E" and proj["nameOp"] == 1 and not proj["chip"], proj
    # ... and the source line names what it is and where it comes from (s93)
    assert any("2026E:" in s and "projected" in s for s in after["src"]), after["src"]


@needs_browser
def test_the_twin_follows_the_path_when_a_transition_re_projects_it():
    """The mask's twin is not a copy frozen at build: whatever writes the path's `d` (a rescale re-projecting it, a seek
    restoring it) writes the twin's in the same call - read by writing the projection's path on the served page."""
    import build_golden_sources as G
    at, ev, errs, close = _serve()
    try:
        at(G.FRAME_T["project-issuance-2026e"])
        got = ev("""() => {
          const st = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')).__lp;
          const pp = st.states[1].paths[1], m = pp.p.getAttribute('mask'), tw = document.getElementById(m.slice(5, -1)).querySelector('path');
          const d0 = pp.p.getAttribute('d');
          pp.p.setAttribute('d', 'M 10 10 L 20 20');
          const moved = tw.getAttribute('d');
          pp.p.setAttribute('d', d0);
          return {moved, back: tw.getAttribute('d') === d0};
        }""")
    finally:
        close()
    assert not errs, errs
    assert got == {"moved": "M 10 10 L 20 20", "back": True}, got


def test_the_golden_is_registered():
    import build_golden_sources as G
    assert "project-issuance-2026e" in G.SURFACES and "project-issuance-2026e" in G.FRAME_T
    tests = (ROOT / "content/video_engine/tests/test_golden_frames.py").read_text(encoding="utf-8")
    assert '"project-issuance-2026e"' in tests


def test_the_golden_reads_its_figures_off_the_committed_object():
    """Never re-typed: the actual and the projected point are the committed debt object's own ($121B 2025 actual, the
    $150B top of the 2026 range the script says: "tracking toward a hundred and fifty")."""
    import build_golden_sources as G
    obj = json.loads(G.PROJ_OBJECT.read_text(encoding="utf-8"))
    ser = G.projection_series()
    assert ser["series"][0]["pts"] == obj["series"][0]["pts"]
    hi = next(s for s in obj["series"] if s.get("label") == "$150B")
    assert ser["series"][1]["pts"] == hi["pts"] and ser["series"][1]["projection"]["tier"] == obj["research_tier"]
    assert LPG.validate(ser, "line") == []
