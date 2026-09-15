"""P61 T2 - THE WHOLE-CHART REMAKE: the compiler's refusals, and the invariant a jump cannot satisfy.

E99 s34, the operator: *"i care that the morph reads as a transformation, not a cut, and that it reads as
intentional. The entire chart should transform, but I don't much mind if the text is re-written or directly
morphed - both is a transformation."*

Two halves. The first is the COMPILER: a remake is admitted only on a line <-> bars pair whose bars ARE the
line's own data, and every refusal names what it could not key and which verb can. The second is the PLAYER,
read in a browser at the instants that matter - and the one that decides it is u = 0.50, where NEITHER chart
is drawable as itself: the line has gone into its columns and the bars have not been drawn, so no cut, no
crossfade and no jump can produce the frame. The goldens `remake-line-to-bars` / `remake-bars-to-line` are
judged at exactly that instant (their quarter and three-quarter frames ride PROOF_FRAMES).
"""
from __future__ import annotations

import contextlib
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as BST  # noqa: E402
import render_baseline as RB  # noqa: E402

AT, DUR = 12.0, 2.4   # the goldens' own row (build_golden_sources.REMAKE_AT / REMAKE_S)


# ---- the fixtures the compiler is asked about ---------------------------------------------------
def _line(n: int = 15, base: float = 1180.4) -> dict:
    steps = [0.0, 9.4, -4.2, 12.1, -6.6, 5.3, 14.2, -9.9, 3.7, 11.4, -12.8, 6.9, 4.1, -7.3, 10.6]
    pts, v = [], base
    for i in range(n):
        v = round(v + steps[i % len(steps)], 1)
        pts.append([round(2025 + i / 12, 4), v])
    return {"title": "The pile", "sub": "monthly", "src": "fixture", "unit": "$", "ylabel": "$bn",
            "series": [{"name": "Holdings", "label": "months", "color": "crimson", "pts": pts}]}


def _bars(values: list[float], labels: list[str] | None = None) -> dict:
    months = ("Nov", "Dec", "Jan", "Feb", "Mar", "Apr")
    names = labels or [months[i % 6] for i in range(len(values))]
    return {"title": "Where it stood", "sub": "at each print", "src": "fixture", "unit": "$",
            "bars": [{"label": names[i], "value": v, "color": "teal"} for i, v in enumerate(values)]}


def _world(first: dict, second: dict, first_variant: str, second_variant: str, species: list) -> dict:
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/a.series.json").write_text(json.dumps(first), encoding="utf-8")
        (ep / "evidence/objects/b.series.json").write_text(json.dumps(second), encoding="utf-8")
        plate = f"ledger:a:{first_variant};then=b:{second_variant}"
        world = BST.world_for_plate(plate, (0, 0, 0), ep)
        BST.derive_rescale_states(world, species, plate, ep, sid="s01")
    return world


def _remake(**kw) -> dict:
    return dict({"kind": "chart_to", "at": AT, "dur": DUR, "to": "remake", "state": 1}, **kw)


# ---- 1. the compiler: what it keys, and what it refuses BY NAME ---------------------------------
def test_the_seventh_verb_is_admitted_and_carries_a_when() -> None:
    assert "remake" in BST.CHART_TO_KINDS
    assert BST.CHART_TO_WHEN["remake"].strip(), "every kind carries a when (P50 T1)"


def test_a_line_and_the_bars_that_are_its_own_values_key_on_level() -> None:
    line = _line()
    tail = [pt[1] for pt in line["series"][0]["pts"][-5:]]
    sp = _remake()
    _world(line, _bars(tail), "line", "bars", [sp])
    assert sp["keyed_on"] == "level" and sp["line_at"] == "from"
    assert sp["mark_map"] == [{"datum": 10 + k, "bar": k} for k in range(5)], sp["mark_map"]


def test_the_same_pair_the_other_way_round_keys_the_same_and_says_where_the_line_is() -> None:
    line = _line()
    tail = [pt[1] for pt in line["series"][0]["pts"][-5:]]
    sp = _remake()
    _world(_bars(tail), line, "bars", "line", [sp])
    assert sp["keyed_on"] == "level" and sp["line_at"] == "to"
    assert len(sp["mark_map"]) == 5


def test_bars_that_are_the_lines_own_changes_key_on_change_and_never_re_derive_e64s_rule() -> None:
    line = _line()
    pts = line["series"][0]["pts"]
    changes = [round(pts[i][1] - pts[i - 1][1], 1) for i in range(len(pts) - 4, len(pts))]
    months = [BST.month_of_x(pts[i][0]) for i in range(len(pts) - 4, len(pts))]   # a change bar is labelled with its own datum's month
    sp = _remake()
    _world(line, _bars(changes, months), "line", "bars", [sp])
    assert sp["keyed_on"] == "change"
    assert [m["bar"] for m in sp["mark_map"]] == [0, 1, 2, 3]


def test_a_line_to_line_pair_is_refused_and_names_the_three_verbs_that_can() -> None:
    with pytest.raises(ValueError) as e:
        _world(_line(), _line(base=900.0), "line", "line", [_remake()])
    msg = str(e.value)
    assert "dense-line -> dense-line" in msg and "RESCALE" in msg and "EXTEND" in msg and "chart_to morph" in msg


def test_bars_that_are_neither_the_values_nor_the_changes_are_refused_by_the_numbers() -> None:
    with pytest.raises(ValueError) as e:
        _world(_line(), _bars([1.0, 2.0, 3.0, 4.0, 5.0]), "line", "bars", [_remake()])
    msg = str(e.value)
    assert "neither the line's own VALUES" in msg and "nor its own CHANGES" in msg
    assert "bar 0 is 1" in msg, "the refusal names the numbers that disagree (E77: figures are never fabricated)"
    assert "recast" in msg and "cut" in msg, "and it names the verbs that can"


def test_a_remake_and_a_retitle_on_one_row_are_refused_because_two_hands_would_write_one_string() -> None:
    line = _line()
    tail = [pt[1] for pt in line["series"][0]["pts"][-5:]]
    row = [_remake(), {"kind": "retitle", "at": 12.0, "dur": 1.0, "text": "Another title"}]
    with pytest.raises(ValueError) as e:
        _world(line, _bars(tail), "line", "bars", row)
    assert "retitle" in str(e.value) and "twice" in str(e.value)


def test_a_state_the_page_does_not_have_is_refused_by_index() -> None:
    line = _line()
    tail = [pt[1] for pt in line["series"][0]["pts"][-5:]]
    with pytest.raises(ValueError) as e:
        _world(line, _bars(tail), "line", "bars", [_remake(state=3)])
    assert "state 3 is not one of the page's other chart states" in str(e.value)


def test_keyed_and_method_belong_to_other_verbs_and_are_refused_on_a_remake() -> None:
    errs = BST.validate_species([_remake(keyed=True)], (0, 0, 0), "ledger:a:line;then=b:bars")
    assert any("keyed" in e and "RECAST" in e for e in errs), errs
    errs = BST.validate_species([_remake(method="a")], (0, 0, 0), "ledger:a:line;then=b:bars")
    assert any("method" in e and "MORPH" in e for e in errs), errs


# ---- 2. the player, at the instants that matter -------------------------------------------------
def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


browser_only = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """() => {
  const world = [...document.querySelectorAll('.ledger')].find((e) => e.__lp);
  if (!world) return null;
  const st = world.__lp, states = st.states || [st], xf = st.xfNow;
  const svg = st.page.querySelector('svg.lp-remake');
  const box = (el) => { const b = el.getBBox(); return [+b.x.toFixed(2), +b.y.toFixed(2), +b.width.toFixed(2), +b.height.toFixed(2)]; };
  const rings = svg ? [...svg.querySelectorAll('path.remake')].map((p) => ({ fill: +p.getAttribute('fill-opacity'), bbox: box(p), d: p.getAttribute('d') })) : [];
  const dots = svg ? [...svg.querySelectorAll('circle')].map((c) => +c.getAttribute('opacity')) : [];
  const dotsAt = svg ? [...svg.querySelectorAll('circle')].map((c) => c.getAttribute('cx') + ',' + c.getAttribute('cy') + ',' + c.getAttribute('opacity')) : [];
  const L = states.find((S) => (S.paths || []).length) || {};
  const B = states.find((S) => (S.bars || []).length) || {};
  const lines = (L.paths || []).map((pp) => {
    const off = Math.abs(parseFloat(pp.p.getAttribute('stroke-dashoffset') || '0'));
    return { vis: pp.len ? Math.max(0, pp.len - off) / pp.len : 1, hidden: pp.p.style.opacity === '0' };
  });
  const bars = (B.bars || []).map((bb) => ({
    transform: bb.bar.style.transform || '', opacity: bb.bar.style.opacity || '',
    rect: box(bb.bar), val: +bb.val.getAttribute('opacity'), lab: +bb.lab.getAttribute('opacity'),
    valText: bb.val.textContent, labText: bb.lab.textContent }));
  const labels = (S) => (S.marks || []).filter((m) => m.el && ['ylabel', 'xtick', 'axislabel'].includes(m.role)).map((m) => m.el.textContent);
  const w = (gs) => (gs || []).map((g) => +(g.style.getPropertyValue('--w') || 0));
  return { on: !!xf, remake: !!(xf && xf.remake), u: xf ? xf.u : null, active: st.active,
           rings, dots, dotsAt, lines, bars, labelsA: labels(states[0]), labelsB: labels(states[1]),
           title: w(st.titleGlyphs), titleB: states[1] && states[1].titleInk ? w(states[1].titleInk.glyphs) : null,
           chartOpacity: [states[0].chart.style.opacity, states[1].chart.style.opacity] };
}"""


@contextlib.contextmanager
def _player(surface: str):
    tl, uris, _t, aspect = RB.load_surface(surface)
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / f"{surface}.html"
        html.write_text(RB.instantiate(tl, uris, RB.TEMPLATE), encoding="utf-8")
        w, h = RB.STAGE[aspect]
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                yield page, (w, h)
                browser.close()
        finally:
            srv.shutdown()


def _at(page, t: float) -> dict:
    page.evaluate("t => { const s = document.getElementById('scrub');"
                  " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
    return page.evaluate(PROBE)


def _shot(page, t: float, size) -> bytes:
    return RB.frame_png(page, t, size)


@browser_only
@pytest.mark.parametrize("surface", ["remake-line-to-bars", "remake-bars-to-line"])
def test_at_u_050_neither_chart_is_drawable_as_itself(surface: str) -> None:
    """The invariant a jump cannot satisfy. At half the clock the source's own ink is inside the rings and
    the target's has not been drawn: what stands is n shapes that are neither chart's."""
    with _player(surface) as (page, _size):
        p0 = _at(page, AT)
        p5 = _at(page, AT + 0.50 * DUR)
        assert p0 and p5 and p5["remake"] and abs(p5["u"] - 0.5) < 1e-6

        # the SOURCE is not drawable as itself
        if surface == "remake-line-to-bars":
            assert all(q["vis"] < 0.02 or q["hidden"] for q in p5["lines"]), p5["lines"]
        else:
            assert all(b["opacity"] == "0" for b in p5["bars"]), [b["opacity"] for b in p5["bars"]]
        # the TARGET is not drawable as itself
        if surface == "remake-line-to-bars":
            assert all(b["transform"].startswith("scaleY(0") for b in p5["bars"]), [b["transform"] for b in p5["bars"]]
            assert all(b["val"] == 0 for b in p5["bars"]), "no bar has its number yet"
        else:
            assert all(q["vis"] < 0.02 or q["hidden"] for q in p5["lines"]), p5["lines"]
        # and what DOES stand is neither: every ring has left its own shape and has not reached its bar
        assert len(p5["rings"]) == 5 and all(r["fill"] > 0.9 for r in p5["rings"]), p5["rings"]
        bars = p5["bars"]
        for k, r in enumerate(p5["rings"]):
            start = p0["rings"][k]["bbox"]
            assert max(abs(a - b) for a, b in zip(r["bbox"], start)) > 2.0, f"ring {k} has not left its own shape"
            assert max(abs(a - b) for a, b in zip(r["bbox"], bars[k]["rect"])) > 2.0, f"ring {k} is already its bar"


@browser_only
@pytest.mark.parametrize("surface", ["remake-line-to-bars", "remake-bars-to-line"])
def test_u_zero_is_the_exact_source_and_u_one_is_the_exact_target(surface: str) -> None:
    with _player(surface) as (page, _size):
        p0 = _at(page, AT)
        assert p0["remake"] and p0["u"] == 0
        assert all(r["fill"] == 0 for r in p0["rings"]), "at u=0 the rings carry no ink"
        assert all(d == 0 for d in p0["dots"]), "and no datum has left"
        assert all(t == 1 for t in p0["title"]), "the page's own title is whole"
        assert all(s == "" for s in p0["labelsB"]), "and the arriving chart has not written a character"
        if surface == "remake-line-to-bars":
            assert all(q["vis"] > 0.99 for q in p0["lines"]), p0["lines"]
            assert all(b["transform"].startswith("scaleY(0") for b in p0["bars"])
        else:
            assert all(b["opacity"] in ("", "1") for b in p0["bars"]), p0["bars"]

        p1 = _at(page, AT + DUR)
        assert not p1["on"], "the clock is over: the target stands by its own law"
        if surface == "remake-line-to-bars":
            assert all(b["transform"].startswith("scaleY(1") for b in p1["bars"]), [b["transform"] for b in p1["bars"]]
            assert all(b["val"] == 1 for b in p1["bars"])
            assert all(b["valText"] and b["labText"] for b in p1["bars"]), "every number and category is whole"
        else:
            assert all(q["vis"] > 0.99 and not q["hidden"] for q in p1["lines"]), p1["lines"]
        assert all(s != "" for s in p1["labelsB"]), "every arriving label is written"


@browser_only
@pytest.mark.parametrize("surface", ["remake-line-to-bars", "remake-bars-to-line"])
def test_two_seeks_to_one_t_write_the_identical_frame(surface: str) -> None:
    """PURE FUNCTION OF t. The remake integrates nothing, so arriving at 13.2 from 12.0, from 5.0 and from
    past the clock's end writes the same numbers - every ring's `d` character for character, every datum's
    place, every label's string, every glyph's width.

    Measured on the PAINTER's own output rather than on pixels deliberately: a warm player's pixels are not
    byte-stable on ANY surface (three consecutive captures of the shipped `data-to-bars` at its own golden
    instant differ by 13 bytes, and 1 519 after a seek away and back - measured 2026-09-15, P61 T2). The
    goldens are COLD renders and pin the pixels; this pins the function."""
    keys = ("rings", "dotsAt", "labelsA", "labelsB", "title", "titleB", "bars", "lines", "chartOpacity")
    with _player(surface) as (page, _size):
        t = AT + 0.50 * DUR
        a = _at(page, t)
        _at(page, 5.0)
        b = _at(page, t)
        _at(page, AT + DUR + 3.0)
        c = _at(page, t)
        for k in keys:
            assert json.dumps(a[k]) == json.dumps(b[k]) == json.dumps(c[k]), f"{k} is not a function of t alone"


@browser_only
def test_the_axes_hand_over_and_are_never_crossfaded_as_a_layer() -> None:
    """E99 s1 refused a crossfade, and T1 named the whole-<svg> opacity cross (lpPaintMorphTo, E:9799/:9801)
    the largest gap. Through a remake BOTH chart layers stand at full opacity and it is the MARKS that
    change hands - the gridlines slide by rank, the labels re-write character by character."""
    with _player("remake-line-to-bars") as (page, _size):
        for u in (0.25, 0.5, 0.75):
            p = _at(page, AT + u * DUR)
            assert p["chartOpacity"][0] in ("1", ""), f"u={u}: the leaving chart's layer is being faded"
            assert p["chartOpacity"][1] in ("1", ""), f"u={u}: the arriving chart's layer is being faded"
        mid = _at(page, AT + 0.5 * DUR)
        part = [s for s in mid["labelsA"] + mid["labelsB"] if s not in ("",)]
        assert part, "the labels are mid-write, not mid-fade"


@browser_only
def test_the_title_transforms_too() -> None:
    """T1's gap 6: no chart_to verb touched the title. Under a remake the standing one is erased glyph by
    glyph and the arriving state's is written - the hand the sub and the source already take."""
    with _player("remake-line-to-bars") as (page, _size):
        early = _at(page, AT + 0.1 * DUR)
        late = _at(page, AT + 0.9 * DUR)
        assert sum(early["title"]) > sum(late["title"]), "the standing title is being erased"
        assert late["titleB"] is not None and sum(late["titleB"]) > 0, "and the arriving one is being written"
        assert sum(late["titleB"]) > sum(early["titleB"] or [0]), "on the same clock, in the same direction"
