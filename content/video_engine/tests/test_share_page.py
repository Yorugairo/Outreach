"""The SHARE page (P48 T4): the donut exception, its bounds, and the piece that leaves.

`ledger_page` refuses a donut by name for every variant but `share`. E53 s1 as amended (2026-09-07) allows it inside four
bounds - a part-to-whole claim about ONE named slice, that slice highlighted and the rest muted, the figure the claim turns
on WRITTEN on the page, and five slices or fewer - and the compiler enforces each of them rather than trusting the author.

The browser rows prove the frame: five wedges keyed and named, the claim's slice the only coloured one, and the peel
leaving on its word with its own figure written and nothing overprinted.
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
import ledger_page as L  # noqa: E402
import render_baseline as RB  # noqa: E402

OBJECT = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/evidence/objects/ev-top-holders-v1.series.json"
PEEL_AT, PEEL_S = 12.0, 1.6


def _series() -> dict:
    """The Tokyo object when it is on disk, else the same SHAPE with the same figures - the bounds are what is under test."""
    if OBJECT.exists():
        return json.loads(OBJECT.read_text(encoding="utf-8"))
    return {
        "title": "Who owns America's debt", "src": "US Treasury TIC Table 5", "unit": "$bn",
        "shares": [{"label": n, "short": s, "value": v, "value_string": "$%s B" % v, "color": c} for n, s, v, c in (
            ("Japan", "Japan", 1239.3, "teal"), ("United Kingdom", "UK", 897.3, "deemph"),
            ("China, Mainland", "China", 694.2, "deemph"), ("Belgium", "Belgium", 454.7, "deemph"),
            ("Canada", "Canada", 446.4, "deemph"))],
        "emphasize": 0,
        "peel": {"index": 0, "value": -122.6, "value_string": "-$122.6B", "label": "sold since February 2026"},
    }


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---- the exception and its bounds -----------------------------------------------------------------


def test_a_donut_is_still_refused_by_name_for_every_other_variant():
    errs = L.validate({"title": "t", "src": "s", "shares": _series()["shares"]}, "bars")
    assert errs and any("donut" in e and "E53" in e for e in errs), errs
    assert "share" in L.VARIANTS and "share" in L.CHART_VARIANTS


def test_the_share_variant_builds_a_share_page_from_the_object():
    s = _series()
    assert L.validate(s, "share") == []
    spec = L.build_spec(s, "share")
    assert spec["builder"] == "share" and spec["variant"] == "share"
    assert len(spec["values"]) == 5 and spec["emphasize"] == 0
    assert spec["short_labels"][1] == "UK", "a wedge is narrow: a slice may name itself short for the page"
    assert spec["labels"][1] == "United Kingdom", "... and the release's own name stays on the spec"
    assert spec["peel"]["value_string"] == "-$122.6B"
    assert spec["colors"][1] == "deemph" and spec["colors"][0] != "deemph", "one slice coloured, the rest muted"


@pytest.mark.parametrize("over, needle", [
    ({"shares": _series()["shares"] + [{"label": "France", "value": 300.0}]}, "5 or fewer"),
    ({"emphasize": None}, "the ONE slice the claim is about"),
    ({"peel": None}, "must declare 'peel'"),
    ({"peel": {**_series()["peel"], "value_string": ""}}, "value_string is required"),
    ({"peel": {**_series()["peel"], "index": 2}}, "is not the emphasised slice"),
    ({"peel": {**_series()["peel"], "value": -9999.0}}, "larger than the slice it comes out of"),
    ({"shares": [dict(_series()["shares"][0], value=-5.0)] + _series()["shares"][1:]}, "cannot be negative"),
])
def test_each_bound_of_the_amendment_is_enforced_by_name(over, needle):
    errs = L.validate({**_series(), **over}, "share")
    assert any(needle in e for e in errs), (needle, errs)


def test_peel_is_a_page_species_that_carries_no_figures_of_its_own():
    """WHICH piece leaves and what it is worth are the PAGE's, validated against the bounds; the species says WHEN."""
    assert "peel" in B.SPECIES_KINDS and "peel" in B.PAGE_SPECIES
    assert B.SPECIES_TARGETS["peel"] == ()


# ---- the frame -------------------------------------------------------------------------------------


def _player(aspect: str = "9:16"):
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    spec = L.build_spec(_series(), "share")
    sc = tl["scenes"][0]
    scene = dict(sc, species=[{"kind": "peel", "at": PEEL_AT, "dur": PEEL_S}],
                 world=dict(sc["world"], page=spec, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect=aspect, scenes=[scene], caption_pages=[], captions=[])
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "share.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    w, h = RB.STAGE[aspect]
    srv, port = RB.serve(html.parent)
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    page = br.new_context(viewport={"width": w, "height": h}).new_page()
    page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return page, close


PROBE = """() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp, S = st.share;
  const bb = (e) => { const r = e.getBBox(); return [r.x, r.y, r.width, r.height]; };
  return { cx: S.cx, cy: S.cy, R: S.R,
    wedges: S.wedges.map(x => ({ i: x.i, name: x.lab.textContent, op: +x.lab.getAttribute('opacity'),
                                 fill: x.keep.getAttribute('fill'), box: bb(x.lab) })),
    peel: S.peel ? { fill: S.peel.piece.getAttribute('fill'), tf: S.peel.piece.style.transform || '',
                     fig: S.ptext.textContent, figOp: +S.ptext.getAttribute('opacity'), figBox: bb(S.ptext) } : null,
    keys: st.marks.map(m => m.key) };
}"""


def _at(page, t: float) -> dict:
    page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
    return page.evaluate(PROBE)


def _apart(a: list, b: list, what: str) -> None:
    assert (a[0] + a[2] <= b[0] + 1 or b[0] + b[2] <= a[0] + 1
            or a[1] + a[3] <= b[1] + 1 or b[1] + b[3] <= a[1] + 1), what


@needs_browser
def test_the_pie_draws_five_named_wedges_and_only_the_claim_is_coloured():
    page, close = _player()
    try:
        d = _at(page, 11.0)
        assert [w["name"] for w in d["wedges"]] == ["Japan", "UK", "China", "Belgium", "Canada"]
        assert all(w["op"] >= 0.99 for w in d["wedges"]), \
            "a wedge nobody named: %s" % [(w["name"], w["op"]) for w in d["wedges"]]
        assert d["wedges"][0]["fill"] == "#178C83", "the claim's slice keeps its declared colour"
        assert all(w["fill"].startswith("rgba(184,196,208") for w in d["wedges"][1:]), \
            "E53 s1(b): every other slice is muted context"
        assert {"w:0", "w:4", "peel", "peelfig", "wlab:0"} <= set(d["keys"])
        for i in range(len(d["wedges"])):          # s9.23b: no two names overprint
            for j in range(i + 1, len(d["wedges"])):
                _apart(d["wedges"][i]["box"], d["wedges"][j]["box"],
                       "%s overprints %s" % (d["wedges"][i]["name"], d["wedges"][j]["name"]))
    finally:
        close()


@needs_browser
def test_the_piece_leaves_on_its_word_goes_blood_red_and_writes_its_own_figure():
    page, close = _player()
    try:
        before = _at(page, PEEL_AT - 0.2)
        assert before["peel"]["fill"] == "#178C83", "at rest the piece is part of its slice, in its slice's colour"
        assert before["peel"]["figOp"] == 0, "nothing has left, so nothing is claimed yet"
        after = _at(page, PEEL_AT + PEEL_S + 0.3)
        assert after["peel"]["fill"] == "var(--lp-neg)", "E28: the loss is geometry AND colour"
        assert "translate(" in after["peel"]["tf"]
        assert after["peel"]["fig"] == "-$122.6B" and after["peel"]["figOp"] >= 0.99, "E53 s1(c): the figure is written"
        for w in after["wedges"]:                  # the claim never lands on a wedge's name
            _apart(after["peel"]["figBox"], w["box"], "the peel's figure overprints %s" % w["name"])
    finally:
        close()


@needs_browser
def test_the_share_page_renders_identically_twice():
    """Purity: the pie is a function of t, so a seek lands the identical frame (P43's seek test)."""
    page, close = _player()
    try:
        a = _at(page, PEEL_AT + 0.7)
        _at(page, 2.0)
        b = _at(page, PEEL_AT + 0.7)
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    finally:
        close()
