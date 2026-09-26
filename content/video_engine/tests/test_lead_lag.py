"""P71 T27 (was P69 T75; harvest v2 A53) - THE LEAD-LAG BRACKET: a bracket across TWO series, its label the lag.

BOOM draws it twice (VERIFY.md, the frame verification): a crest-to-crest "1-2 Years" bar over the business cycle's two
waves (16:12.5-16:13.0, the LEVEL form) and a "1.5 Years" ELBOW from a ring on the yield curve's end up to the PMI and
across to it (16:25.5-16:27.0). The token is the bracket's own: `{"kind": "bracket", at, dur, from: {series, datum},
to: {series, datum}, label?, sub?, color?, form?: "span" (the level, the default) | "elbow", keep?}` on a ledger row.
Its label IS the lag: computed by the compiler from the two data's x (`check_lead_lag`) and written when absent, and a
typed lag that disagrees is refused (a truth rule, E99 s109 / s106). On a second-axis page two ends on the two axes need
s102's lead/lag claim (P71 T13). A52 (the travelling ring) and A54 (the phase slide) were NOT FOUND in BOOM's frames and
are not built. This file pins the grammar, the truth, s102, the engine's wiring, the card, and the bracket read on the
SERVED player (the golden `lead-lag-bracket`: the divergence page's semiconductors topping six weeks before the
mega-caps).
"""
from __future__ import annotations

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

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/page_species.json"
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
PLATE = "ledger:ev-divergence-v1:line::right"
SEMIS, MEGA = 1, 2                     # the divergence page's SEMICONDUCTOR STOCKS and MEGA-CAP TECH STOCKS (the grammar and truth reads)
SEMIS_TOP, MEGA_TOP = 188, 217         # their peaks: 261.08 at 2026.4709, 123.16 at 2026.5886 - 43 days apart
LAG = {"kind": "bracket", "at": 8.0, "dur": 1.6, "from": {"series": SEMIS, "datum": SEMIS_TOP},
       "to": {"series": MEGA, "datum": MEGA_TOP}}


def _errs(entries, plate=PLATE):
    return B.validate_species([dict(e) for e in entries], (0, 0, 0), plate)


def _world(plate: str = PLATE) -> dict:
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        return B.world_for_plate(plate, (0, 0, 0), PROJECT)
    finally:
        B.ASPECT = saved


def _check(entries, world=None):
    sps = [json.loads(json.dumps(e)) for e in entries]
    notes = B.check_lead_lag(world or _world(), sps)
    return sps, notes


# ---- the grammar ---------------------------------------------------------------------------------------------------


def test_a_bracket_across_two_series_is_accepted_in_both_forms():
    assert _errs([LAG]) == [], "the level form (the default): from / to each name a series and a datum"
    assert _errs([dict(LAG, form="span")]) == [], "`span` names the level form explicitly"
    assert _errs([dict(LAG, form="elbow", label="6 weeks", sub="chips first")]) == [], "BOOM's elbow"
    assert "elbow" in B.BRACKET_FORMS and B.LAG_FORMS == ("span", "elbow")


@pytest.mark.parametrize("patch,needle", [
    ({"from": {"series": SEMIS}}, "'from' must name {series, datum}"),
    ({"to": {"series": MEGA, "datum": -1}}, "'to' must name {series, datum}"),
    ({"to": {"series": MEGA, "datum": MEGA_TOP, "index": 3}}, "'index' is not a lag end's key"),
    ({"to": {"series": SEMIS, "datum": 200}}, "both ends on series 1"),
    ({"to": MEGA_TOP}, "both ends the same way"),
    ({"series": 1}, "'series' is each end's own"),
    ({"tier": 1}, "'tier' is each end's own"),
    ({"form": "bar"}, "a lag is drawn as the level (form: span, the default) or the elbow"),
    ({"form": "brace"}, "a brace divides ONE bar"),
    ({"bar": 0}, "'bar' is the brace's"),
    ({"label": "  "}, "a lag bracket's label, when written, is a non-empty string"),
])
def test_a_malformed_lag_is_refused_by_name(patch, needle):
    errs = _errs([dict(LAG, **patch)])
    assert any(needle in e for e in errs), errs


def test_the_elbow_is_refused_by_name_on_a_one_series_bracket():
    errs = _errs([{"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 3, "to": 9, "label": "-4%", "form": "elbow"}])
    assert any("the elbow joins TWO series" in e for e in errs), errs


def test_a_one_series_bracket_validates_exactly_as_before():
    one = {"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 3, "to": 9, "label": "-4%"}
    assert _errs([one]) == []
    assert _errs([dict(one, label="")]) == ["bracket: needs a non-empty string label (the measured span says what it measures)"]
    assert _errs([dict(one, **{"from": "a"})]) == ["bracket: 'from' must be a non-negative integer datum index"]


# ---- the truth: the label IS the lag ------------------------------------------------------------------------------


def test_the_compiler_writes_the_computed_lag_when_no_label_is_typed():
    sps, notes = _check([dict(LAG, form="elbow")])
    assert sps[0]["label"] == "6 weeks", "43 days: the x of the two peaks, 2026.5886 - 2026.4709"
    assert notes == []


def test_a_level_over_two_data_far_apart_in_height_is_a_warn_toward_the_elbow_never_a_refusal():
    sps, notes = _check([LAG])
    assert sps[0]["label"] == "6 weeks"
    assert len(notes) == 1 and "points at air" in notes[0] and "form: elbow" in notes[0] and "261.08" in notes[0], notes
    assert B._lag_level_skew({"axes": {"domain": [0, 100]}, "series": []}, (0, 1), [50.0, 45.0]) == 0.05, "a near level: kept"
    assert B._lag_level_skew({"y2": {"series": [1]}, "series": []}, (0, 1), [50.0, 4.5]) is None, "two scales: no one height"


@pytest.mark.parametrize("label", ["6 weeks", "43 days", "1.4 months", "about 6 weeks", "1-2 months", "6 wks"])
def test_a_typed_lag_that_agrees_at_its_own_precision_is_kept(label):
    sps, _ = _check([dict(LAG, label=label)])
    assert sps[0]["label"] == label


@pytest.mark.parametrize("label,needle", [
    ("3 months", "the label says 3 months"),
    ("8 weeks", "the label says 8 weeks"),
    ("2-3 months", "the label says 2-3 months"),
    ("the lag", "a lag bracket's label IS its lag"),
    ("6", "a lag bracket's label IS its lag"),
])
def test_a_typed_lag_that_disagrees_or_names_no_time_is_refused(label, needle):
    with pytest.raises(ValueError, match="bracket") as exc:
        _check([dict(LAG, label=label)])
    assert needle in str(exc.value), str(exc.value)


def test_the_computed_lag_reads_in_the_unit_its_length_calls_for():
    assert B.lag_text(10 / 365.25) == "10 days"
    assert B.lag_text(43 / 365.25) == "6 weeks"
    assert B.lag_text(7 / 365.25) == "7 days"
    assert B.lag_text(16 / 12) == "16 months"
    assert B.lag_text(1.5) == "18 months"
    assert B.lag_text(2.5) == "2.5 years"
    assert B.lag_text(3.0) == "3 years"


@pytest.mark.parametrize("patch,needle", [
    ({"to": {"series": 9, "datum": 1}}, "series 9 is past the page's last series"),
    ({"to": {"series": MEGA, "datum": 900}}, "datum 900 is past series 2's last datum"),
    ({"to": {"series": MEGA, "datum": 0}, "from": {"series": SEMIS, "datum": 0}}, "no lag to bracket"),
])
def test_an_end_the_page_does_not_have_or_a_zero_lag_is_refused(patch, needle):
    with pytest.raises(ValueError) as exc:
        _check([dict(LAG, **patch)])
    assert needle in str(exc.value), str(exc.value)


def test_a_lag_stands_on_a_line_page_and_is_refused_by_name_elsewhere():
    bars = {"kind": B.SPECIES_LEDGER, "page": {"variant": "bars", "values": [1, 2], "labels": ["a", "b"]}}
    with pytest.raises(ValueError, match="stands on a line page"):
        B.check_lead_lag(bars, [dict(LAG)])
    sch = _world()
    sch["page"] = dict(sch["page"], schematic={"shape": "wave"})
    with pytest.raises(ValueError, match="a schematic's x is a shape"):
        B.check_lead_lag(sch, [dict(LAG)])


def test_a_row_with_no_lag_is_untouched_and_the_room_estimate_passes_it_by():
    one = {"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 3, "to": 9, "label": "-4%"}
    w = _world()
    assert B.check_lead_lag(w, [dict(one)]) == []
    assert B.bracket_room_notes(w["page"], [dict(LAG, label="6 weeks")], "16:9") == [], \
        "P72 T43's room estimate reads a span's integer ends; a lag bracket is laid out by its own geometry"


def test_a_lag_on_a_projection_is_refused_as_any_mark_on_an_estimate_is():
    assert ("from", 1) not in B._projection_named(LAG)
    assert ("from.series", SEMIS) in B._projection_named(LAG) and ("to.series", MEGA) in B._projection_named(LAG)


# ---- s102: two series on unlike scales -----------------------------------------------------------------------------


def _y2_page(claim: str, invert: bool = False) -> dict:
    return {"variant": "line", "builder": LPG.Y2_BUILDER,
            "y2": {"series": [1], "unit": "%", "label": "yield", "invert": invert, "claim": claim, "header": "yield (%)"}}


def test_two_ends_on_the_two_axes_need_the_lead_lag_claim():
    sp = {"kind": "bracket", "at": 1.0, "dur": 1.0, "from": {"series": 1, "datum": 6}, "to": {"series": 0, "datum": 22}}
    err = B._y2_species_error(sp, {1}, False, _y2_page("comove"))
    assert err and "s102" in err and "lead_lag" in err, err
    assert B._y2_species_error(sp, {1}, False, _y2_page("lead_lag")) is None


def test_a_lag_reads_time_so_the_inverted_line_does_not_refuse_it_and_a_level_still_is():
    lag = {"kind": "bracket", "at": 1.0, "dur": 1.0, "from": {"series": 1, "datum": 6}, "to": {"series": 0, "datum": 22}}
    assert B._y2_species_error(lag, {1}, True, _y2_page("lead_lag", invert=True)) is None, \
        "the lag is read on the one x - no level or change on the inverted line (s102 (a): 'this one leads that one')"
    span = {"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 3, "to": 9, "label": "-4%", "series": 1}
    assert "inverted" in (B._y2_species_error(span, {1}, True, _y2_page("lead_lag", invert=True)) or ""), \
        "a one-series bracket measures a level or a change - E28 still binds it (T13's rule, unchanged)"
    same = dict(lag, to={"series": 1, "datum": 22}, **{"from": {"series": 0, "datum": 6}})
    assert B._y2_species_error(dict(same, to={"series": 0, "datum": 30}), {1}, False, _y2_page("comove")) is None, \
        "both ends on the left axis: no second scale to read across"


# ---- the engine, the card, the registries ---------------------------------------------------------------------------


def test_the_engine_builds_the_lag_beside_the_brace_and_paints_it_from_the_bracket():
    src = ENGINE.read_text(encoding="utf-8")
    build = src[src.index("const buildPerform ="):src.index("const paintPerform =")]
    assert "lpLagBuild(" in build and build.index('sp.form === "brace"') < build.index("lpLagBuild("), \
        "a two-series bracket builds its own geometry, beside the brace's"
    paint = src[src.index("const paintBracket ="):]
    paint = paint[:paint.index("\n  };\n")]
    assert "if (b.lag) return paintLag(" in paint
    brace = src[src.index("  const LPBRACE = Object.freeze("):src.index("  const buildPerform = (st, scene, pg) => {")] +         src[src.index("  const paintBrace = (b, t, ud, st) => {"):src.index("  const paintBracket = (b, t, ud, st) => {")]
    assert "lpLagBuild = " not in brace and "paintLag = " not in brace,         "the lag's code stands OUTSIDE the brace's own windows (test_decomposition_brace reads them as the brace's)"
    head = src[:src.index("const LPLAG = Object.freeze(")]
    assert "[MEASURED: BOOM jx3Ll 16:13.0 and 16:27.0" in head[head.rindex("/* P71 T27"):], "the dials carry their reference (E38)"


def test_the_card_names_the_lag_and_the_elbow():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    opts = {o["token"]: o for o in cards["page_species:bracket"]["options"]}
    assert "lag" in opts and "elbow" in opts and "brace" in opts
    assert "computed" in opts["lag"]["means"] and "s102" in opts["lag"]["means"]
    assert any("P71 T27" in d for d in cards["page_species:bracket"]["doctrine"])


# ---- the bracket read on the served player --------------------------------------------------------------------------


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
  const st = world.__lp, PF = st.perform || {}, b = (PF.brackets || []).find(q => q.lag);
  if (!b) return null;
  const nums = (p) => (p ? p.getAttribute('d') || '' : '').replace(/[MLZ]/g, ' ').trim().split(/\\s+/).filter(Boolean).map(Number);
  const S = (st.states && st.states[st.active | 0]) || st;
  const pt = (si, i) => { const ser = (S.markBy || {})['s' + si], sp = ser && ser.geom && ser.geom.pts;
    const k0 = (ser && ser.geom.k0) | 0, off = (S.windowOffsets || [])[si] | 0; return sp ? sp[i - off - k0] || null : null; };
  const L = b.lag, lb = b.main.label.getBBox();
  const ink = (si) => { const ser = (S.markBy || {})['s' + si]; return ser && ser.geom.pts ? ser.geom.pts.map(q => [q[0], q[1]]) : []; };
  return { form: L.form, g: parseFloat(b.main.g.getAttribute('opacity') || '0'), glow: parseFloat(b.glow.g.getAttribute('opacity') || '0'),
           v: nums(b.main.line), h: nums(L.hline), heads: L.heads.map(e => [parseFloat(e.getAttribute('opacity') || '0'), e.getAttribute('transform')]),
           ticks: L.ticks.map(e => e.getAttribute('transform')), a: pt(L.si[0], L.ends[0]), b: pt(L.si[1], L.ends[1]),
           text: b.main.label.textContent.replace(/\\u00a0/g, ' '), glyphs: b.main.lg.map(t => parseFloat(t.getAttribute('opacity') || '0')),
           label: [lb.x, lb.y, lb.x + lb.width, lb.y + lb.height], k: st.stagePx, pts: L.si.map(ink) };
}"""


def _serve_timeline(tl: dict, uris: dict):
    import render_baseline as RB
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)   # R26-351: guarded

    def at(t: float, probe: str = PROBE) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(probe)

    return at, errs, close


@needs_browser
def test_the_elbow_runs_from_the_ringed_peak_to_the_other_series_level_and_across_its_lag_written():
    import build_golden_sources as G
    tl, uris = G.lead_lag_bracket()
    at, errs, close = _serve_timeline(tl, uris)
    try:
        a0, dur = G.LAG_AT, G.LAG_DUR
        before, early, mid, turn, landed, after = (at(a0 - 0.2), at(a0 + 0.08 * dur), at(a0 + 0.2 * dur), at(a0 + 0.4 * dur),
                                                   at(a0 + dur), at(a0 + dur + 2.0))
    finally:
        close()
    assert not errs, errs
    assert before["g"] == 0 and landed["form"] == "elbow", before
    A, Bp, k = landed["a"], landed["b"], landed["k"]
    x, y0, _x, y1 = landed["v"]
    assert abs(x - A[0]) < 0.2 and abs(_x - A[0]) < 0.2, "the vertical stands at the ringed datum's x (BOOM: the ring's centre)"
    assert abs(y1 - Bp[1]) < 0.2, "... and runs to the OTHER series' level"
    assert y0 - A[1] > (G.RING_MIN_RY_PX / k), "its tip clears the ring authored on the same datum"
    hx0, hy0, hx1, hy1 = landed["h"]
    assert abs(hy0 - Bp[1]) < 0.2 and abs(hy1 - Bp[1]) < 0.2 and abs(hx0 - A[0]) < 0.2, "the horizontal leaves the corner at that level"
    assert 0 < Bp[0] - hx1 < 20 / k, "... and stops a few px short of the other datum, its head pointing at it"
    assert all(o == 1 for o, _ in landed["heads"]), landed["heads"]
    assert landed["text"] == "6 weeks" and all(gl == 1 for gl in landed["glyphs"]), (landed["text"], landed["glyphs"])
    lab = landed["label"]
    assert lab[2] < x and abs((lab[1] + lab[3]) / 2 - (y0 + y1) / 2) < 30, \
        "the figure is written beside the vertical, at its middle, on the side away from the horizontal (BOOM 16:27)"
    ev, mv = early["v"], mid["v"]
    assert abs(ev[1] - ev[3]) < abs(mv[1] - mv[3]) < abs(y0 - y1), "the vertical GROWS (s99: it travels)"
    assert abs((ev[1] + ev[3]) / 2 - (y0 + y1) / 2) < 0.5, "... from its middle both ways (BOOM 16:25.2)"
    assert early["h"] == [] and mid["h"] == [], "the horizontal waits for the vertical"
    assert turn["v"] == landed["v"] and hx0 < turn["h"][2] < hx1, "then runs out of the corner toward `to`"
    assert early["heads"][0][0] == 1 and early["heads"][1][0] == 0, "the `from` head rides the growing tip; `to`'s waits"
    assert after == dict(landed, glyphs=after["glyphs"]) and all(gl == 1 for gl in after["glyphs"]), "it HOLDS"


@needs_browser
def test_the_level_form_stands_over_the_ink_between_its_ends_crest_to_crest():
    import build_golden_sources as G
    tl, uris = G.lead_lag_bracket(form="span")
    at, errs, close = _serve_timeline(tl, uris)
    try:
        a0, dur = G.LAG_AT, G.LAG_DUR
        early, landed = at(a0 + 0.2 * dur), at(a0 + dur)
    finally:
        close()
    assert not errs, errs
    A, Bp, k = landed["a"], landed["b"], landed["k"]
    x0, y, x1, y_ = landed["v"]
    assert abs(y - y_) < 0.01 and abs(x0 - A[0]) < 0.2 and abs(x1 - Bp[0]) < 0.2, "a LEVEL, crest to crest (BOOM 16:13)"
    between = [p[1] for pts in landed["pts"] for p in pts if A[0] - 0.01 <= p[0] <= Bp[0] + 0.01]
    over = min(min(between), A[1] - G.RING_MIN_RY_PX / k)   # the golden rings the `from` top: the level clears it too
    assert abs((over - y) * k - G.LAG_RISE_PX) < 1.0, "it stands RISE px over the highest ink between its ends (and the ring)"
    assert early["v"][2] < x1 - 1 and abs(early["v"][0] - x0) < 0.2, "the bar draws from the lead's end to the lag's"
    lab = landed["label"]
    assert lab[3] < y and abs((lab[0] + lab[2]) / 2 - (x0 + x1) / 2) < 2.0, "the label is centred OVER the bar"
    assert landed["text"] == "6 weeks"


@needs_browser
def test_a_relight_refires_a_lag_bracket_like_any_bracket():
    import build_golden_sources as G
    tl, uris = G.lead_lag_bracket(extra=[{"kind": "relight", "at": G.LAG_AT + G.LAG_DUR + 1.0, "dur": 1.2, "ref": "bracket"}])
    at, errs, close = _serve_timeline(tl, uris)
    try:
        mid = at(G.LAG_AT + G.LAG_DUR + 1.6)
    finally:
        close()
    assert not errs, errs
    assert mid["glow"] > 0.5, mid["glow"]
