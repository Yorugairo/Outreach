"""P61 T3 / R26-117 - THE BALL BECOMES THE NEXT FULL CHART, and P48 T5b / R26-16's PLANTED SOURCE.

E99 s39, the operator (`docs/portable/OPERATOR-RULINGS.md:3196`): *"if the whole thing is magically formed
that is basically a snap/cut, and not the morph we're looking for. A morph should be proof of form/function
to the audience, that we're really manipulating the world they're watching, not tricking them."* E99 s1: *"the
morph needs to prove that it can morph the entire data set/chart."*

What this file pins:

  1. THE GRAMMAR    `melt:morph` is the FOURTH authored ending, read in exactly ONE place per side
                    (`build_scene_timeline_f._melt_parts` / `species/melt.mjs meltOpts`), the two agreeing
                    string for string; a word this engine does not have is refused BY NAME, on both sides.
  2. THE REFUSALS   the hand-over has two ends, so the compiler refuses a `melt:morph` whose next world is
                    not a page, whose next page does not enter BY the morph, whose page has no area under a
                    line to land on, or which names a prop of its own (the BALL is the prop).
  3. THE DEFAULT    an exit string with no `morph` renders today's melt BYTE-IDENTICAL: `parse_exit("melt")`
                    is the tuple it was, and every pre-existing `melt*` golden is its own sha256.
  4. ONE CLOCK      the melt's window is the sag, the ball and the HAND, and the hand's seconds ARE the
                    arriving page's morph seconds - so the melt's last frame is the morph's last frame.
  5. THE HAND-OVER  read in a browser: at the hand-over the page's prop IS the ball's ring; at u = 0.5
                    NEITHER the ball nor the finished chart is drawable as itself (the @proof-050 pattern of
                    P57 T12c / P61 T2); at u = 1 the shape's top edge sits ON series 0, within 1 unit; and
                    no frame of the window draws a series of the arriving chart while the morph runs.
  6. THE SEEK       two seeks of the same instant are the same bytes.
  7. THE PLANTED    `world.morph = {poly: [...]}` - a real element's own traced silhouette. Its three
     SOURCE        refusals by name (under three points, self-intersecting, off the stage), and the poly the
                   `morph-planted` golden carries RE-TRACED by `kinetics/contour.mjs` from the same raster
                   `build_golden_sources.planted_inside` draws - so the picture and the poly are one element.

E99 s34: `melt:morph` is authored on this slice's own goldens and NOWHERE near the approved Japan short.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

MELT_MJS = ROOT / "content/video_engine/scripts/species/melt.mjs"
CONTOUR_MJS = ROOT / "content/video_engine/scripts/kinetics/contour.mjs"
FRAMES = ROOT / "content/video_engine/tests/golden/frames"

CUT = G.MORPH_CUT          # 15.0 - where both surfaces hand over
NODE = "node.exe" if sys.platform == "win32" else "node"


def _node(src: str):
    out = subprocess.run([NODE, "--input-type=module", "-e", src], capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def _melt(expr: str):
    return _node(f'import {{ MELT, MELT_ENDINGS, meltOpts, meltHandAt, meltHandDelay, meltHandSecs }} '
                 f'from {json.dumps(MELT_MJS.as_uri())};\nconsole.log(JSON.stringify(({expr})));\n')


# ---- 1. THE GRAMMAR, on both sides ---------------------------------------------------------------

def test_the_compiler_reads_morph_as_the_fourth_ending() -> None:
    assert B.MELT_ENDINGS == ("throw", "splash:chart", "splash:plate", "morph")
    assert B.melt_ending("melt:morph") == "morph"
    assert B.melt_ending("melt") == "throw", "the default is untouched"
    assert B.melt_ending("melt:morph:2.4") == "morph"
    assert B.melt_ending("melt:weight:morph") == "morph", "a phase does not change the ending"
    assert B.melt_ending("melt:gather:morph") == "morph"
    assert B.melt_ending("melt:morph:depth=1.2") == "morph"
    assert B.melt_ending("melt:weight:metal:morph") == "morph", "a material is still read beside it"


def test_the_player_reads_the_same_strings_the_compiler_does() -> None:
    """One place per side, and the two have to agree - the pair every melt slice pins."""
    strings = ["melt", "melt:morph", "melt:morph:2.4", "melt:weight:morph", "melt:gather:morph",
               "melt:morph:depth=1.2", "melt:weight:metal:morph", "melt:splash:chart"]
    mine = [B.melt_ending(s) for s in strings]
    theirs = _melt("[" + ", ".join(f"meltOpts({json.dumps(s)}).ending" for s in strings) + "]")
    assert mine == theirs, list(zip(strings, mine, theirs))
    assert _melt("[...MELT_ENDINGS]") == list(B.MELT_ENDINGS)


@pytest.mark.parametrize("bad, why", [
    ("melt:morphh", "morphh"),               # a typo is a refusal, never a silent default
    ("melt:morph:throw", "two endings"),
    ("melt:morph:splash:chart", "two endings"),
    ("melt:morph:0.3,0.4", "THROW"),         # an x,y point is the throw's, not a hand-over's
])
def test_an_unknown_or_doubled_word_is_refused_by_name(bad: str, why: str) -> None:
    with pytest.raises(ValueError) as e:
        B._melt_parts(bad)
    assert why in str(e.value), str(e.value)
    err = subprocess.run([NODE, "--input-type=module", "-e",
                          f'import {{ meltOpts }} from {json.dumps(MELT_MJS.as_uri())};\n'
                          f'meltOpts({json.dumps(bad)});\n'], capture_output=True, text=True, cwd=str(ROOT))
    assert err.returncode != 0, f"the player accepted {bad!r}"


# ---- 2. THE REFUSALS at the boundary --------------------------------------------------------------
def _pages() -> tuple[dict, dict]:
    series = LPG.load_series(G.SERIES)
    a = LPG.build_spec(series, "line", None, "right")
    b = G._morph_target_page()
    return a, b


def _scenes(exit_id: str, second_world: dict) -> list[dict]:
    a, _b = _pages()
    return [{"scene_id": "s01", "world": {"kind": "ledger", "page": a, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
             "exit": "cut", "span": [0.0, CUT], "docks": [], "species": []},
            {"scene_id": "s02", "world": second_world, "exit": exit_id, "span": [CUT, 30.0], "docks": [], "species": []}]


def test_a_melt_morph_into_a_plate_is_refused() -> None:
    scenes = _scenes("melt:morph", {"asset_id": "plate-plain", "sha256": "0" * 64,
                                    "ken_burns": {"scale": 0, "x": 0, "y": 0}})
    with pytest.raises(ValueError) as e:
        B.stamp_transition_pages(scenes)
    assert "not a ledger page" in str(e.value), str(e.value)


def test_a_melt_morph_whose_page_declares_another_enter_is_refused() -> None:
    _a, b = _pages()
    b = dict(b, enter="axes")
    scenes = _scenes("melt:morph", {"kind": "ledger", "page": b, "ken_burns": {"scale": 0, "x": 0, "y": 0}})
    with pytest.raises(ValueError) as e:
        B.stamp_transition_pages(scenes)
    assert "arrives BY the morph" in str(e.value) and "axes" in str(e.value), str(e.value)


def test_a_melt_morph_onto_a_page_with_no_area_under_a_line_is_refused() -> None:
    raw = json.loads(G.SERIES.read_text(encoding="utf-8"))
    bars = {"title": "Where the four lines end", "sub": "", "src": raw.get("src", ""), "unit": "",
            "bars": [{"label": n, "value": round(float(sr["pts"][-1][1]), 1), "color": sr.get("color", "crimson")}
                     for sr, n in zip(raw["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}
    page2 = LPG.build_spec(bars, "bars", None, "right")
    scenes = _scenes("melt:morph", {"kind": "ledger", "page": page2, "ken_burns": {"scale": 0, "x": 0, "y": 0}})
    with pytest.raises(ValueError) as e:
        B.stamp_transition_pages(scenes)
    assert "AREA UNDER A LINE" in str(e.value) and "splash:chart" in str(e.value), str(e.value)


def test_a_melt_morph_that_names_its_own_prop_is_refused_the_ball_is_the_prop() -> None:
    _a, b = _pages()
    scenes = _scenes("melt:morph", {"kind": "ledger", "page": b, "morph": "tab",
                                    "ken_burns": {"scale": 0, "x": 0, "y": 0}})
    with pytest.raises(ValueError) as e:
        B.stamp_transition_pages(scenes)
    assert "the BALL is the prop" in str(e.value), str(e.value)


def test_a_melt_morph_whose_page_declares_nothing_is_stamped_enter_morph() -> None:
    _a, b = _pages()
    b = {k: v for k, v in b.items() if k != "enter"}
    scenes = _scenes("melt:morph", {"kind": "ledger", "page": b, "ken_burns": {"scale": 0, "x": 0, "y": 0}})
    notes = B.stamp_transition_pages(scenes)
    assert b["enter"] == "morph"
    assert any("enter=morph stamped" in n for n in notes), notes


# ---- 3. THE DEFAULT: not one byte of today's melt moves -------------------------------------------

def test_parse_exit_of_a_bare_melt_is_the_tuple_it_was() -> None:
    assert B.parse_exit("melt") == ("melt", None)
    assert B.parse_exit("melt:splash:chart") == ("melt:splash:chart", None)
    assert B._melt_parts("melt") == ("throw", None, None, False, "chart")
    assert B._melt_parts("melt:weight") == ("throw", None, None, False, "reference")   # P61 T5c / E99 s49: the WEIGHT ball's default body


def test_the_melt_that_never_asks_for_a_morph_has_the_window_it_had() -> None:
    assert _melt("meltOpts('melt').secs") == _melt("MELT.S")
    assert _melt("meltOpts('melt:morph').secs") == _melt("MELT.S + MELT.M_S")
    assert _melt("meltOpts('melt:morph:3').secs") == 3.0, "a declared length is the length"


@pytest.mark.parametrize("name", ["melt-page", "melt-page@proof-015", "melt-page@proof-045",
                                  "melt-page@proof-075", "melt-page@proof-100", "melt-splash", "melt-plate"])
def test_the_flag_off_melt_goldens_are_their_own_sha256(name: str) -> None:
    """The endings that shipped are pinned HERE too, by hash, so this file fails on its own if the fourth
    ending moved any of them - not only through test_golden_frames' whole-tree run."""
    p = FRAMES / f"{name}.png"
    assert p.is_file(), p
    assert hashlib.sha256(RB.render_surface(name)).hexdigest() == hashlib.sha256(p.read_bytes()).hexdigest()


# ---- 4. ONE CLOCK ---------------------------------------------------------------------------------

def test_the_hand_splits_the_melts_window_once_and_leaves_no_gap() -> None:
    parts = _melt("(() => { const o = meltOpts('melt:morph');"
                  " return [meltHandAt(o), meltHandDelay(o, true), meltHandSecs(o), o.secs]; })()")
    at, delay, secs, total = parts
    assert 0 < at < 1
    assert abs(delay + secs - total) < 1e-9, "the melt's last frame IS the page's morph's last frame"
    assert abs(delay - at * total) < 1e-9
    assert _melt("meltHandDelay(meltOpts('melt'), true)") == 0, "a throw is held by meltDrawDelay, not by this"
    assert _melt("meltHandDelay(meltOpts('melt:morph'), false)") == 0, "a world that is not a page is handed nothing"


def test_the_golden_carries_the_grammar_the_compiler_wrote() -> None:
    tl, _uris, _t, _aspect = RB.load_surface("melt-morph")
    s2 = tl["scenes"][1]
    assert s2["exit"] == "melt:morph"
    assert B.melt_ending(s2["exit"]) == "morph"
    assert s2["world"]["page"]["enter"] == "morph"
    assert s2["world"]["page"]["builder"] in B.MORPH_BUILDERS
    assert "morph" not in s2["world"], "the ball is the prop; the row names none"


# ---- 5. THE HAND-OVER, read in a browser ----------------------------------------------------------
def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


browser_only = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = r"""() => {
  /* BOTH worlds are ledger pages across a melt boundary (the page that melted is still mounted under it), so the
     one this probe is about is the one carrying a MORPH - the ARRIVING page - and the last mounted one otherwise. */
  const worlds = [...document.querySelectorAll('.ledger')].filter((e) => e.__lp);
  const world = worlds.find((e) => e.__lp.morph) || worlds[worlds.length - 1] || null;
  const melt = [...document.querySelectorAll('.world')].find((e) => e.__melt);
  const bb = (pts) => { let a = 1e9, b = 1e9, c = -1e9, d = -1e9;
    for (const p of pts) { a = Math.min(a, p[0]); b = Math.min(b, p[1]); c = Math.max(c, p[0]); d = Math.max(d, p[1]); }
    return [a, b, c - a, d - b].map((v) => +v.toFixed(2)); };
  const st = world ? world.__lp : null, M = st ? st.morph : null;
  const lines = st ? (st.paths || []).map((pp) => {
    const da = (pp.p.getAttribute('stroke-dasharray') || '').trim().split(/[\s,]+/).map(Number);
    const off = parseFloat(pp.p.getAttribute('stroke-dashoffset') || '0'), len = pp.len || 1;
    const d0 = da.length && isFinite(da[0]) ? da[0] : len;
    return { vis: +(Math.max(0, len - off) / len).toFixed(4), hidden: pp.p.style.opacity === '0' };
  }) : [];
  const m = melt ? melt.__melt : null;
  return {
    hasMorph: !!M, hand: M ? !!M.hand : null, u: M ? M.u : null,
    A: M ? bb(M.A) : null, B: M ? bb(M.B) : null, now: (M && M.pts) ? bb(M.pts) : null,
    top: (M && M.pts) ? M.pts.slice(0, M.pts.length / 2).map((p) => [+p[0].toFixed(3), +p[1].toFixed(3)]) : null,
    fill: M ? +M.path.getAttribute('fill-opacity') : null,
    strokeA: M ? +(M.path.getAttribute('stroke-opacity') || 1) : null,
    series0: (st && st.linePts && st.linePts[0]) ? st.linePts[0].map((p) => [+p[0].toFixed(3), +p[1].toFixed(3)]) : null,
    axisB: st ? st.axisB : null,
    lines, chartOpacity: st ? st.chart.style.opacity : null,
    ballAlpha: m ? +m.body.getAttribute('opacity') : null,
    ballD: m ? (m.body.getAttribute('d') || '').slice(0, 64) : null,
    ballBox: (m && m.body.getAttribute('d')) ? (() => { const b = m.body.getBBox();
      return [+b.x.toFixed(2), +b.y.toFixed(2), +b.width.toFixed(2), +b.height.toFixed(2)]; })() : null,
    boardUp: melt ? melt.style.opacity : null,
    blur: m ? m.blur.getAttribute('stdDeviation') : null,
  };
}"""


@contextlib.contextmanager
def _player(surface: str, flags: dict):
    tl, uris, _t, aspect = RB.load_surface(surface)
    from playwright.sync_api import sync_playwright
    tl = dict(tl, kinetics=dict(tl.get("kinetics") or {}, **flags))
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


def _hand_window() -> tuple[float, float]:
    """(the hand-over instant, the seconds the hand runs for) of the `melt-morph` golden's own row."""
    delay, secs = _melt("(() => { const o = meltOpts('melt:morph');"
                        " return [meltHandDelay(o, true), meltHandSecs(o)]; })()")
    return CUT + delay, secs


FLAGS = dict(G.MORPH_KINETICS)


@browser_only
def test_at_the_hand_over_the_pages_prop_IS_the_balls_ring() -> None:
    """R26-117: *"the ball is the prop it starts from"*. On the hand-over frame the page's morph is open at
    u = 0, its source outline is a ring the size of the ball, standing where the ball stands - and the ball
    itself is still the thing on the board, at full paint."""
    at, _secs = _hand_window()
    with _player("melt-morph", FLAGS) as (page, _size):
        before = _at(page, at - 0.06)            # the last frame of the BALL phase
        p = _at(page, at + 0.005)                # ... and the first frame of the HAND
        assert p["hasMorph"] and p["hand"] is True, p
        assert p["u"] < 0.02, p["u"]
        assert p["ballAlpha"] > 0.98, "the ball is still the ball"
        assert p["fill"] < 0.02 and p["strokeA"] < 0.05, "the page's own ink has not begun to rise"
        # the prop's own box is a RING, not a slab: near-square, and far narrower than the area it becomes
        w, h = p["A"][2], p["A"][3]
        assert 0.8 < w / h < 1.25, f"the prop is a RING, not a strip: {p['A']}"
        assert p["B"][2] > 2.5 * w, "and the area it becomes is far wider"
        # NO CUT ACROSS THE BOUNDARY: the ball's own painted body is the same body it was one frame earlier - the
        # melt's overlay is still what draws it, and from here it wears the page's outline instead of its circle.
        assert before["hasMorph"] is False or before["u"] is None or before["u"] <= 0, before["u"]
        for k, (a, b) in enumerate(zip(before["ballBox"], p["ballBox"])):
            assert abs(a - b) < 4.0, f"the ball's box jumped at the hand-over: {before['ballBox']} -> {p['ballBox']}"
        assert 0.9 < p["ballBox"][2] / p["ballBox"][3] < 1.12, f"and it is still round: {p['ballBox']}"


@browser_only
def test_at_u_050_of_the_hand_neither_the_ball_nor_the_chart_is_drawable_as_itself() -> None:
    """The @proof-050 pattern (P57 T12c, P61 T2): the instant a cut cannot produce. Half way through the hand
    the shape has left the ring and has not reached the area, the arriving chart has drawn no series, and the
    one thing on the board is carrying BOTH paints - the ball's and the page's."""
    at, secs = _hand_window()
    with _player("melt-morph", FLAGS) as (page, _size):
        p = _at(page, at + 0.5 * secs)
        assert p["hand"] and abs(p["u"] - 0.5) < 0.02, p["u"]
        far = lambda a, b: max(abs(x - y) for x, y in zip(a, b))   # noqa: E731
        assert far(p["now"], p["A"]) > 20, f"it has left the ball's ring: {p['now']} vs {p['A']}"
        assert far(p["now"], p["B"]) > 20, f"it has not reached the area: {p['now']} vs {p['B']}"
        assert all(q["vis"] < 0.02 or q["hidden"] for q in p["lines"]), p["lines"]
        assert 0.05 < p["ballAlpha"] < 0.95, f"the ball's paint is mid-hand-off: {p['ballAlpha']}"
        assert 0 < p["fill"] < 0.28, f"and the page's own ink is rising under it: {p['fill']}"
        assert float(p["blur"]) == 0.0, "a hand-over is not a blur"


@browser_only
def test_at_u_1_the_shape_sits_on_the_series_within_one_unit() -> None:
    """The morph LANDS on the arriving page's own geometry: the strip's top edge is series 0, sampled."""
    at, secs = _hand_window()
    with _player("melt-morph", FLAGS) as (page, _size):
        p = _at(page, at + secs - 0.01)
        assert p["hand"] and p["u"] > 0.99, p["u"]
        ser, top = p["series0"], p["top"]
        assert ser and top and len(top) >= 8
        def y_at(x: float) -> float:
            for a, b in zip(ser, ser[1:]):
                if a[0] - 1e-6 <= x <= b[0] + 1e-6:
                    u = (x - a[0]) / max(1e-9, b[0] - a[0])
                    return a[1] + (b[1] - a[1]) * u
            return ser[-1][1]
        worst = max(abs(py - y_at(px)) for px, py in top)
        assert worst < 1.0, f"the area's top edge is {worst:.3f} units off the series"


@browser_only
def test_no_frame_of_the_hand_draws_the_arriving_chart_flat() -> None:
    """Nothing appears from nowhere (E99 s34): across the hand, the page's chart layer never carries a drawn
    series - the shape is the only thing on the board - and the ball's paint falls monotonically."""
    at, secs = _hand_window()
    with _player("melt-morph", FLAGS) as (page, _size):
        alphas = []
        for k in (0.0, 0.2, 0.4, 0.6, 0.8, 0.98):
            p = _at(page, at + k * secs + 0.005)
            assert p["hand"], k
            assert all(q["vis"] < 0.02 or q["hidden"] for q in p["lines"]), (k, p["lines"])
            alphas.append(p["ballAlpha"])
        assert all(a >= b - 1e-6 for a, b in zip(alphas, alphas[1:])), alphas
        assert alphas[0] > 0.95 and alphas[-1] < 0.05, alphas


@browser_only
def test_two_seeks_of_one_instant_are_the_same_frame() -> None:
    at, secs = _hand_window()
    t = at + 0.5 * secs
    with _player("melt-morph", FLAGS) as (page, size):
        _at(page, t)
        a = RB.frame_png(page, t, size)
        _at(page, at + 0.9 * secs)
        _at(page, t)
        b = RB.frame_png(page, t, size)
    assert hashlib.sha256(a).hexdigest() == hashlib.sha256(b).hexdigest()


# ---- 6. P48 T5b: THE PLANTED SOURCE ---------------------------------------------------------------

def test_a_named_prop_and_an_absent_one_are_still_admitted() -> None:
    for name in B.MORPH_SHAPES:
        assert B.morph_source_error({"morph": name}, "w") is None
    assert B.morph_source_error({}, "w") is None
    assert B.morph_source_error(None, "w") is None
    assert "not one of" in (B.morph_source_error({"morph": "napkin"}, "w") or "")


@pytest.mark.parametrize("poly, why", [
    ([[0.2, 0.2], [0.4, 0.2]], "at least 3"),
    ([[0.2, 0.2]], "at least 3"),
    ([[0.2, 0.2], [0.8, 0.2], [0.2, 0.8], [0.8, 0.8]], "crosses itself"),
    ([[0.2, 0.2], [1.4, 0.2], [0.2, 0.8]], "outside the stage"),
    ([[0.2, 0.2], [-0.01, 0.2], [0.2, 0.8]], "outside the stage"),
    ([[0.2, 0.2], [0.8, "x"], [0.2, 0.8]], "pair of numbers"),
    ([[0.2, 0.2], [0.8, 0.2, 0.1], [0.2, 0.8]], "pair [x, y]"),
])
def test_a_bad_planted_poly_is_refused_by_name(poly, why: str) -> None:
    msg = B.morph_poly_error(poly, "s02: world.morph")
    assert msg and why in msg, msg
    assert msg.startswith("s02: world.morph"), msg


def test_a_good_planted_poly_is_admitted_and_reaches_the_compilers_scene_walk() -> None:
    assert B.morph_poly_error(G.PLANTED_BLOB, "w") is None
    scenes = [{"scene_id": "s01", "world": {"asset_id": "p", "sha256": "0" * 64}, "exit": "cut",
               "span": [0.0, CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"kind": "ledger", "page": G._morph_target_page(),
                                            "morph": {"poly": [[0.2, 0.2], [0.8, 0.2]]}},
               "exit": "cut", "span": [CUT, 30.0], "docks": [], "species": []}]
    with pytest.raises(ValueError) as e:
        B.stamp_transition_pages(scenes)
    assert "s02: world.morph" in str(e.value) and "at least 3" in str(e.value), str(e.value)


def test_the_planted_polys_own_silhouette_is_re_traced_and_must_match() -> None:
    """The golden's poly is not drawn, it is TRACED. This re-runs `contourSilhouette` over the same raster
    `png_planted` paints and refuses any drift between the picture and the poly."""
    src = (
        f'const {{ contourSilhouette }} = await import({json.dumps(CONTOUR_MJS.as_uri())});\n'
        f'const W = {G.PLANTED_W}, H = {G.PLANTED_H}, CX = {G.PLANTED_C[0]}, CY = {G.PLANTED_C[1]}, R0 = {G.PLANTED_R};\n'
        'const rAt = (th) => R0 * (1 + 0.22 * Math.cos(3 * th + 0.6) + 0.12 * Math.sin(5 * th - 0.3));\n'
        'const inside = (x, y) => { const dx = x - CX, dy = y - CY; return Math.hypot(dx, dy) <= rAt(Math.atan2(dy, dx)); };\n'
        'const data = new Uint8Array(W * H);\n'
        'for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) data[j * W + i] = inside(i, j) ? 1 : 0;\n'
        'const pts = contourSilhouette({ w: W, h: H, data }, { tol: 0.6 });\n'
        'console.log(JSON.stringify(pts.map((p) => [ +(((p[0] + 0.5) / W) * 1.1 - 0.05).toFixed(5),\n'
        '                                            +(((p[1] + 0.5) / H) * 1.1 - 0.05).toFixed(5) ])));\n'
    )
    assert _node(src) == G.PLANTED_BLOB, "the committed poly is no longer what the tracer reads off the raster"


def test_the_python_raster_and_the_tracers_own_inside_agree_pixel_for_pixel() -> None:
    """The picture and the poly come from ONE shape: `planted_inside` is what `png_planted` draws, and the
    tracer's `inside` above is the same formula. A sample-by-sample comparison is what makes that a fact."""
    src = (
        f'const W = {G.PLANTED_W}, H = {G.PLANTED_H}, CX = {G.PLANTED_C[0]}, CY = {G.PLANTED_C[1]}, R0 = {G.PLANTED_R};\n'
        'const rAt = (th) => R0 * (1 + 0.22 * Math.cos(3 * th + 0.6) + 0.12 * Math.sin(5 * th - 0.3));\n'
        'const inside = (x, y) => { const dx = x - CX, dy = y - CY; return Math.hypot(dx, dy) <= rAt(Math.atan2(dy, dx)); };\n'
        'const on = []; for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) if (inside(i, j)) on.push(j * W + i);\n'
        'console.log(JSON.stringify(on));\n'
    )
    theirs = set(_node(src))
    mine = {j * G.PLANTED_W + i for j in range(G.PLANTED_H) for i in range(G.PLANTED_W) if G.planted_inside(i, j)}
    assert mine == theirs, f"{len(mine ^ theirs)} samples differ between the raster and the tracer's input"


def test_the_planted_golden_carries_the_traced_poly_and_nothing_else() -> None:
    tl, _uris, _t, _aspect = RB.load_surface("morph-planted")
    src = tl["scenes"][1]["world"]["morph"]
    assert isinstance(src, dict) and src["poly"] == G.PLANTED_BLOB
    assert tl["scenes"][1]["world"]["page"]["enter"] == "morph"
    assert B.morph_poly_error(src["poly"], "w") is None


@browser_only
def test_the_planted_morph_starts_on_the_element_and_ends_on_the_series() -> None:
    """R26-16's tie, measured: at u = 0 the page's prop is the traced outline - the shape the plate held one
    frame earlier - and at u = 1 it is the area under the arriving page's own series."""
    with _player("morph-planted", FLAGS) as (page, _size):
        p0 = _at(page, CUT + 0.02)
        assert p0["hasMorph"] and p0["hand"] is False, "a planted source is not a hand-over"
        assert p0["u"] < 0.02
        far = lambda a, b: max(abs(x - y) for x, y in zip(a, b))   # noqa: E731
        assert far(p0["now"], p0["A"]) < 3.0, "at u = 0 it IS the traced outline"
        p1 = _at(page, CUT + 1.99)
        assert p1["u"] > 0.99
        ser, top = p1["series0"], p1["top"]
        def y_at(x: float) -> float:
            for a, b in zip(ser, ser[1:]):
                if a[0] - 1e-6 <= x <= b[0] + 1e-6:
                    return a[1] + (b[1] - a[1]) * ((x - a[0]) / max(1e-9, b[0] - a[0]))
            return ser[-1][1]
        assert max(abs(py - y_at(px)) for px, py in top) < 1.0
        pm = _at(page, CUT + 1.0)
        assert far(pm["now"], pm["A"]) > 20 and far(pm["now"], pm["B"]) > 20, "and in between it is neither"


# ---- 7. P61 T6 proof B: the GATHER and the MORPH compose by construction ---------------------------

def test_the_gather_and_the_morph_compose_and_neither_changes_the_other() -> None:
    """E99 s2 asks the splash to land in *"a scenic, high-resolution world plate or fully assembled chart"*.
    `gather` is a PHASE token and `morph` an ENDING, read in different branches of the same two parsers, so
    `melt:gather:morph` needed no code: the page's marks travel the vortex and amass on ONE point, and that
    point is handed to the next page as its prop and becomes the chart. This asserts the composition on both
    sides and that the window makes room for BOTH phases."""
    s = "melt:gather:morph"
    assert B.melt_gather(s) is True and B.melt_ending(s) == "morph"
    assert _melt(f"(() => {{ const o = meltOpts({json.dumps(s)}); return [o.gather, o.ending, o.secs]; }})()") == \
        [True, "morph", _melt("MELT.S + MELT.G_S + MELT.M_S")]
    assert B.melt_gather("melt:morph") is False, "a morph alone is not a gather"
    assert B.melt_ending("melt:gather") == "throw", "a gather alone does not change the ending"
    tl, _u, _t, _a = RB.load_surface("melt-gather-morph")
    assert tl["scenes"][1]["exit"] == s
    assert tl["scenes"][1]["world"]["page"]["enter"] == "morph"


@pytest.mark.parametrize("name", ["melt-morph", "melt-morph@proof-ball", "melt-morph@proof-050",
                                  "melt-morph@proof-built", "melt-morph@proof-ground",
                                  "morph-planted", "morph-planted@proof-050", "morph-planted@proof-ground",
                                  "melt-gather-morph", "melt-gather-morph@proof-point",
                                  "melt-gather-morph@proof-chart"])
def test_the_slices_own_goldens_are_on_disk_and_are_their_own_sha256(name: str) -> None:
    p = FRAMES / f"{name}.png"
    assert p.is_file(), p
    assert hashlib.sha256(RB.render_surface(name)).hexdigest() == hashlib.sha256(p.read_bytes()).hexdigest()



# ---- 8. P61 T3b / E99 s52: THE MORPH PAGE'S GROUND ARRIVES, NEVER SNAPS IN AROUND THE PROP -----------
#
# The operator, 2026-09-16, on `p48-hg3-morph-onto-planted`: *"The actual morph is fine, but going from the ink
# splotch to the full fill on the board instantly around it is the problem here."* Measured before this slice:
# `morph-planted` went from a cream plate carrying one dark splotch at 14.98 to the WHOLE charcoal board at 15.00,
# because `paintLedger` pinned a morph page's field beat to `b = 1` (its end state) on the page's first frame and
# the field's crisp rect is opaque at b >= 1. One frame delivered 61 % of the stage.
#
# THE METRIC - INK COVERAGE, not a colour count. The field arrives partly by OPACITY (the seeps' own alpha, the
# crisp rect's ramp), and a binary "is this pixel charcoal" count flips a whole board in the two frames an opacity
# crosses its threshold - it would report a gradual darkening as a snap and a snap as gradual. Coverage is what
# "filled area" means: per pixel, how far it has travelled from the page's cream to the field's charcoal, clamped
# to [0, 1] and averaged over the stage. FILL normalises that to the page's own first frame (0) and the board once
# whole (1), so the thresholds below are shares OF THE BOARD and not of the metric.
ENGINE_SRC = RB.ENGINE.read_text(encoding="utf-8")
CREAM_L, INK_L = 230.0, 47.0     # #F4E6C7, the ledger page's cream; #25313C, the field's charcoal
FRAME_S = 0.02                   # the scrub's own step - the player seeks in hundredths and a 50 fps frame is two
GROUND_STEP_MAX = 0.125          # no two consecutive frames may fill more than an EIGHTH of the board (see below)
GROUND_FIRST_MAX = 0.05          # ... and the page's first frame carries at most a twentieth of it


def _morph_dial(name: str) -> float:
    """One of `MORPH`'s dials, read off the engine's own source - never copied into this file."""
    import re
    m = re.search(r"const MORPH = \{(.*?)\};", ENGINE_SRC, re.S)
    assert m, "the engine has no MORPH dials"
    d = re.search(rf"\b{re.escape(name)}:\s*([0-9.]+)", m.group(1))
    assert d, f"MORPH has no dial {name}: {m.group(1)}"
    return float(d.group(1))


def _coverage(png: bytes) -> float:
    import io as _io

    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(_io.BytesIO(png)).convert("RGB"), dtype=np.float32)
    lum = 0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2]
    return float(np.clip((CREAM_L - lum) / (CREAM_L - INK_L), 0.0, 1.0).mean())


def _sweep(page, size, t0: float, t1: float) -> list[tuple[float, float]]:
    """(t, coverage) at the player's own frame step across [t0, t1]."""
    out, n = [], int(round((t1 - t0) / FRAME_S))
    for i in range(n + 1):
        t = round(t0 + i * FRAME_S, 4)
        out.append((t, _coverage(RB.frame_png(page, t, size))))
    return out


@browser_only
def test_the_planted_morph_pages_ground_arrives_and_never_snaps_in_around_the_prop() -> None:
    """E99 s52, measured on the frames themselves.

    THE THRESHOLDS, and why. The board's full coverage is measured on this run, never assumed: `full` is the
    highest coverage inside the ground's own window. GROUND_FIRST_MAX 0.05 is the ruling itself - the page's
    first frame may not arrive with its board already on it (before this slice that frame read 1.00).
    GROUND_STEP_MAX 0.125 is an eighth of the board per frame: it forbids the ground arriving in fewer than
    eight frames (0.16 s), which is the shortest run anything can take and still be watched rather than cut,
    and it clears both beats that legitimately move a lot of area in one frame - the PUNCH's first expoOut
    frame (measured 0.086 of the board) and the soak's own steepest (0.043) - by about 1.5x, so a re-tuned
    dial does not fail it and a choreography collapsing back toward a snap does."""
    groundS = _morph_dial("S") * _morph_dial("GROUND")
    with _player("morph-planted", FLAGS) as (page, size):
        rows = _sweep(page, size, CUT, CUT + 2.0)
    base = rows[0][1]
    full = max(c for t, c in rows if t <= CUT + groundS + 1e-9)
    span = full - base
    assert span > 0.3, f"the board never filled at all: base {base:.4f} full {full:.4f}"
    fill = [(t, (c - base) / span) for t, c in rows]
    # 1. THE RULING: the page's FIRST frame is a cream page under the splotch, not a filled board.
    assert fill[1][1] <= GROUND_FIRST_MAX, f"the board is {fill[1][1]:.3f} filled on the page's first frame"
    # 2. ... and no single frame of the whole window delivers more than an eighth of it.
    steps = [(fill[i][0], fill[i][1] - fill[i - 1][1]) for i in range(1, len(fill))]
    worst_t, worst = max(steps, key=lambda r: abs(r[1]))
    assert abs(worst) <= GROUND_STEP_MAX, f"the board's fill jumped {worst:+.3f} at t={worst_t} (max {GROUND_STEP_MAX})"
    # 3. and it ARRIVES: the ground is soaking IN over its own window, whole by the end of it, never contracting.
    during = [f for t, f in fill if t <= CUT + groundS + 1e-9]
    assert during[-1] > 0.98, f"the ground is only {during[-1]:.3f} arrived when its window closes"
    assert min(during[i] - during[i - 1] for i in range(1, len(during))) > -0.02, "a soak never contracts"


@browser_only
def test_the_handed_pages_board_never_left_so_nothing_arrives_across_the_hand_over() -> None:
    """The rule's other half (E88): a melt takes the CHART's ink and leaves the board, so the page handed the
    ball arrives on a board that never went away. Its ground is therefore whole on its first frame - a ramp
    there would fade a board out from under the ball - and nothing about the board may move across the
    hand-over. Measured: the coverage over the hand is flat to a hundredth."""
    at, _secs = _hand_window()
    with _player("melt-morph", FLAGS) as (page, size):
        rows = _sweep(page, size, at - 0.10, at + 0.20)
    lo, hi = min(c for _t, c in rows), max(c for _t, c in rows)
    assert lo > 0.85, f"the handed page's board is not whole across the hand-over (min coverage {lo:.4f})"
    assert hi - lo < 0.01, f"the board moved across the hand-over: {lo:.4f} .. {hi:.4f}"
    worst = max(abs(rows[i][1] - rows[i - 1][1]) for i in range(1, len(rows)))
    assert worst < 0.005, f"a frame of the hand-over changed the board by {worst:.4f}"


FIELD_PROBE = r"""() => {
  const worlds = [...document.querySelectorAll('.ledger')].filter((e) => e.__lp);
  const w = worlds.find((e) => e.__lp.morph) || worlds[worlds.length - 1];
  const st = w ? w.__lp : null;
  if (!st) return null;
  return {
    blobs: (st.blobs || []).map((b) => ({ i: b.i, cx: +b.cx.toFixed(2), cy: +b.cy.toFixed(2),
                                          lag: +b.lag.toFixed(4), r0: +(b.r0 || 0).toFixed(2), pow: b.pow || 1.5 })),
    strokes: (st.strokes || []).length,
    rect: +(st.rect.getAttribute('opacity') || 0),
  };
}"""


def _field_at(page, t: float) -> dict:
    page.evaluate("t => { const s = document.getElementById('scrub');"
                  " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
    return page.evaluate(FIELD_PROBE)


@browser_only
def test_the_soaks_seed_is_the_splotch_and_the_rest_open_by_distance() -> None:
    """E99 s52 asks for the soak spreading OUT FROM the splotch. The soak's own order is its nine stains'
    `lag`; on a planted morph page that order is replaced by DISTANCE from the prop's area centroid, the
    nearest stain is moved onto that point and opens at lag 0 already the splotch's own width (so the first
    ink seen is ink coming out from under an opaque prop, never a stain switched on), and the farthest waits
    MORPH.SEED_LAG of the ground's window."""
    with _player("morph-planted", FLAGS) as (page, _size):
        st = _field_at(page, CUT + 0.02)
    assert st and st["strokes"] == 0, "the morph page's field is the SOAK, not the scribble (the stamped default)"
    seeds = [b for b in st["blobs"] if b["r0"] > 0]
    assert len(seeds) == 1, f"exactly one stain is the seed: {[b['i'] for b in seeds]}"
    seed = seeds[0]
    assert seed["lag"] == 0.0, f"the seed stain opens at once: lag {seed['lag']}"
    assert seed["pow"] == _morph_dial("SEED_POW"), f"and on its own faster curve: pow {seed['pow']}"
    assert seed["r0"] > 40, f"and already the splotch's own width: r0 {seed['r0']}"
    # every other stain's lag rises with its distance from the seed, and the farthest is the last to open
    others = sorted(st["blobs"], key=lambda b: (b["cx"] - seed["cx"]) ** 2 + (b["cy"] - seed["cy"]) ** 2)
    lags = [b["lag"] for b in others]
    assert lags == sorted(lags), f"the stains do not open outward from the splotch: {lags}"
    assert abs(lags[-1] - _morph_dial("SEED_LAG")) < 1e-3, f"the farthest stain waits MORPH.SEED_LAG: {lags[-1]}"
    assert st["rect"] == 0, "and the crisp rect - the whole board - is not painted on the page's first frame"


def test_a_morph_page_is_stamped_the_soak_and_a_row_that_names_its_field_stands() -> None:
    """E99 s52 / E99 s35: a morph page's ground has to ARRIVE, so a morph page that names no `;field=` is
    stamped `soak` - the entry a prop that is already ink spreads out of. A row that names one is untouched."""
    _pg1, pg2 = _pages()
    pg2["enter"] = "morph"
    notes = B.stamp_transition_pages(_scenes("cut", {"kind": "ledger", "page": pg2, "ken_burns": {"scale": 0, "x": 0, "y": 0}}))
    assert pg2["field"] == "soak", pg2.get("field")
    assert any("field=soak stamped" in n for n in notes), notes
    # ... and the cross-fade (continuity) or the scribble (the opt-in back-up) stand where a row names them
    for named in ("plates", "scribble"):
        _pgA, pgB = _pages()
        pgB["enter"] = "morph"
        pgB["field"] = named
        B.stamp_transition_pages(_scenes("cut", {"kind": "ledger", "page": pgB, "ken_burns": {"scale": 0, "x": 0, "y": 0}}))
        assert pgB["field"] == named, f"a row that says field={named} is not overwritten"
    # a page that does NOT enter by a morph is never touched by this stamp
    _pgC, pgD = _pages()
    B.stamp_transition_pages(_scenes("cut", {"kind": "ledger", "page": pgD, "ken_burns": {"scale": 0, "x": 0, "y": 0}}))
    assert pgD.get("field") is None, pgD.get("field")


def test_the_morph_goldens_carry_the_field_each_kind_of_morph_owes() -> None:
    """The PLANTED fixture proves the stamped default rather than restating it (`_morph_target_page` names no
    field, and the compiler writes `soak`); the two HANDED fixtures name scene 1's OWN field, because a melt
    leaves the board it took the ink off (E88) and the page handed the ball is continuing that board."""
    tl, _u, _t, _a = RB.load_surface("morph-planted")
    assert tl["scenes"][1]["world"]["page"]["field"] == "soak"
    for surface in ("melt-morph", "melt-gather-morph"):
        tl, _u, _t, _a = RB.load_surface(surface)
        out, arrive = tl["scenes"][0]["world"]["page"], tl["scenes"][1]["world"]["page"]
        assert arrive["enter"] == "morph"
        assert arrive["field"] == out["field"], (surface, out.get("field"), arrive.get("field"))
