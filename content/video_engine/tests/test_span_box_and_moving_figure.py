"""P72 T46g - THE SPAN'S BOX (R26-407, Bravos A56) AND THE FIGURE ON A MOVING DATUM (R26-409).

  * R26-407: `span` accepted ANY `form` and drew its shade regardless (`form: "zzz"` validated to no error - R26-307's
    class, E99 s106: a silent drop is neither advice nor refusal). The compiler now refuses an unknown form BY NAME, and
    `form: "box"` is built: a dashed rectangle round the named series' own ink over the stretch (x from..to, y the
    stretch's own min..max, both padded), drawn round by length on its word, standing for its `dur` and then leaving -
    Bravos A56 (BOOM 17:55.5-17:58.5: the box names the latest actual move, then leaves for the dated rule). A glow on a
    box span is refused by name (the glow edges a SHADE's rect; a box draws its own edge).
  * R26-409: `species/figure.mjs` read its datum off the ACTIVE state, so through an extend's re-fit H row 16's "$121B"
    held its old place (12.2-13.0 s) and then jumped ~180 px, changing side. It now tweens from its place on the leaving
    state to its place on the arriving one on the datum's own eased clock (the engine's `lpXfClock`, lpDatumNow's).

The browser rows need playwright + chromium and are skipped without them (served_player.py, R26-351).
"""
from __future__ import annotations

import json
import math
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
SPAN_MJS = SCRIPTS / "species/span.mjs"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402
import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

SPAN = {"kind": "span", "at": 8.0, "dur": 3.0, "from": 191, "to": 234, "label": "SINCE THE PEAK"}


def _span(**o) -> dict:
    e = dict(SPAN)
    e.update(o)
    return {k: v for k, v in e.items() if v is not None}


# ---------------------------------------------------------------- R26-407: the form is refused by name, or built

@pytest.mark.parametrize("form", ["zzz", "Box", "boxed", 3, None])
def test_an_unknown_span_form_is_refused_by_name(form):
    e = _span()
    e["form"] = form
    errs = B._validate_entry(e)
    assert any("span: form" in m and "shade|box" in m and "R26-407" in m for m in errs), errs
    assert any(repr(form) in m for m in errs), ("the refusal names the value it refused", errs)


@pytest.mark.parametrize("form", ["shade", "box"])
def test_the_two_span_forms_are_accepted(form):
    assert B._validate_entry(_span(form=form)) == []


def test_a_span_with_no_form_is_the_shade_and_unchanged():
    assert B._validate_entry(_span()) == []
    assert "needs a non-empty string label" in " ".join(B._validate_entry(_span(label=None)))


def test_a_box_names_a_move_and_may_carry_no_name():
    assert B._validate_entry(_span(form="box", label=None)) == [], "Bravos A56's box writes nothing"
    for bad in ("", "  ", 7):
        errs = B._validate_entry(_span(form="box", label=bad))
        assert any("span: a box's label" in m for m in errs), (bad, errs)


def test_the_compilers_span_forms_are_the_modules():
    src = SPAN_MJS.read_text(encoding="utf-8")
    m = re.search(r"export const SPAN_FORMS = Object\.freeze\(\[([^\]]*)\]\)", src)
    assert m, "species/span.mjs exports SPAN_FORMS"
    assert tuple(json.loads("[" + m.group(1) + "]")) == B.SPAN_FORMS == ("shade", "box")


def test_a_glow_on_a_box_span_is_refused_by_name():
    world = {"kind": "ledger", "page": {"builder": "dense-line"}}
    glow = {"kind": "glow", "at": 9.0, "dur": 1.0, "span": 0}
    assert not B._validate_entry(glow), B._validate_entry(glow)
    with pytest.raises(ValueError, match=r"span 0 is a box .*R26-407"):
        B.check_glow(world, [_span(form="box"), glow])
    assert B.check_glow(world, [_span(), glow]) == [], "a shade keeps its glow"


# ---------------------------------------------------------------- the browser rows

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
LP = "const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp, PF = st.perform || {};"


def _serve(tl: dict, uris: dict, ts: list[float], js: str) -> tuple[list, list]:
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "t46g.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE[tl.get("aspect") or "16:9"]
        pg, errs, close = SP.open_served(html, w, h)
        try:
            out = []
            for t in ts:
                pg.evaluate("t => { const s = document.getElementById('scrub'); s.value = t;"
                            " s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                out.append(pg.evaluate(js))
            return out, errs
        finally:
            close()


def _box_timeline(species: list) -> tuple[dict, dict]:
    tl, uris = G.span_decade()
    tl["scenes"][0]["species"] = species
    return tl, uris


BOX_JS = "() => {" + LP + """
  const sd = (PF.spans || [])[0], S = (st.states || [st])[st.active | 0], pts = st.linePts[0];
  const bb = sd.box ? sd.box.getBBox() : null;
  return { d: sd.box ? sd.box.getAttribute('d') : null, op: sd.box ? +sd.box.getAttribute('opacity') : null,
           dash: sd.box ? sd.box.getAttribute('stroke-dasharray') : null, fill: sd.box ? sd.box.getAttribute('fill') : null,
           inGround: !!(sd.box && S.chart.contains(sd.box) && S.chart.firstChild === sd.box),
           bb: bb && [bb.x, bb.y, bb.width, bb.height], shade: +sd.rect.getAttribute('fill-opacity'),
           lab: +sd.label.getAttribute('opacity'), stretch: pts.slice(191, 235) };
}"""


@needs_browser
def test_the_box_is_drawn_round_the_stretch_of_its_own_series_then_leaves():
    tl, uris = _box_timeline([_span(form="box", label=None)])
    (pre, mid, held, gone), errs = _serve(tl, uris, [7.9, 8.2, 10.0, 11.2], BOX_JS)
    assert not errs, errs
    assert pre["op"] == 0 and not pre["d"], pre
    assert mid["d"] and "Z" not in mid["d"], ("mid-draw: the outline is still going round", mid["d"])
    assert held["d"].endswith("Z") and held["op"] == 1, held
    assert held["fill"] == "none" and held["dash"], held
    assert not held["inGround"], "a box is ink ON the page - never sunk to the ground as a shade is"
    assert held["shade"] == 0 and held["lab"] == 0, "no shade and, with no label, no name"
    xs = [p[0] for p in held["stretch"]]
    ys = [p[1] for p in held["stretch"]]
    x, y, w, h = held["bb"]
    assert x < min(xs) and x + w > max(xs), ("the box goes round the stretch's x", held["bb"], min(xs), max(xs))
    assert y < min(ys) and y + h > max(ys), ("... and round its own ink's y", held["bb"], min(ys), max(ys))
    assert min(ys) - y < 40 and y + h - max(ys) < 40, ("tight: the stretch's own min..max, padded - not the plot", held["bb"])
    assert gone["op"] == 0, ("after its dur the box has left for the dated rule (A56)", gone)


@needs_browser
def test_a_shade_span_is_untouched_by_the_box():
    tl, uris = _box_timeline([_span()])
    (held,), errs = _serve(tl, uris, [10.0], BOX_JS)
    assert not errs, errs
    assert held["d"] is None, "a shade builds no box"
    assert held["shade"] > 0


# ---------------------------------------------------------------- R26-409: the figure rides its datum

FIG = {"kind": "figure", "at": 2.0, "dur": 1.5, "text": "$121B", "dy": -1.4}
FIG_JS = "() => {" + LP + """
  const f = (PF.figures || [])[0], l = f.label, a = l.getAttribute('text-anchor'), x = +l.getAttribute('x');
  const tw = l.getComputedTextLength();
  return { left: a === 'end' ? x - tw : x, y: +l.getAttribute('y'), anchor: a, op: +f.g.getAttribute('opacity'),
           D: window.__lpDatum(null, 0, f.idx), active: st.active, xf: !!st.xfNow };
}"""


def _moving_figure_timeline() -> tuple[dict, dict, float, float]:
    tl, uris = G.project_issuance_2026e()
    last = len(G.projection_series()["series"][0]["pts"]) - 1
    tl["scenes"][0]["species"] = [dict(FIG, target={"kind": "datum", "series": 0, "index": last})] + tl["scenes"][0]["species"]
    return tl, uris, G.PROJ_AT, G.PROJ_DUR


@needs_browser
def test_a_figure_rides_its_datum_through_an_extends_refit_and_never_jumps():
    tl, uris, at, dur = _moving_figure_timeline()
    ts = [round(at - 0.1 + 0.05 * k, 3) for k in range(int((dur + 0.3) / 0.05) + 1)]
    rows, errs = _serve(tl, uris, ts, FIG_JS)
    assert not errs, errs
    assert rows[0]["xf"] is False and any(r["xf"] for r in rows), "the samples straddle the re-fit"
    moved = math.hypot(rows[-1]["left"] - rows[0]["left"], rows[-1]["y"] - rows[0]["y"])
    assert moved > 60, ("the datum's re-fit moves the figure's place", moved)
    # the place relative to its datum changes over the move (it is written leftward at the page's edge, rightward after):
    # that change is spread over the move, so no step of the figure outruns its datum's own step by more than half of it
    rel = [(r["left"] - r["D"][0], r["y"] - r["D"][1]) for r in (rows[0], rows[-1])]
    side = math.hypot(rel[1][0] - rel[0][0], rel[1][1] - rel[0][1])
    for a, b in zip(rows, rows[1:]):
        fig = math.hypot(b["left"] - a["left"], b["y"] - a["y"])
        dat = math.hypot(b["D"][0] - a["D"][0], b["D"][1] - a["D"][1])
        assert fig <= dat + 0.5 * side + 0.5, ("no frame jumps: the figure rides its datum", a, b, fig, dat, side)
    for r in rows:
        assert r["op"] == 1
        assert math.hypot(r["left"] - r["D"][0], r["y"] - r["D"][1]) < 260, ("it stays by its datum", r)
