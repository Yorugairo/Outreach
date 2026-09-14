"""E91 s2 / BACKLOG R26-79 (P57 T16): AT A RANK SWAP, ROWS PASS EACH OTHER CLEANLY.

The operator's ruling, s2 of the race A/B: *"whichever setting, rows pass each other cleanly: at a rank swap
two labels or two values never print on top of each other"* - arm B at 7.5 s read "ALBETA" with "136" over
"138". The cause is the race's own geometry: at a crossing the two rows ARE at one row position, so their
names sit on one baseline and their values, equal there by definition, print on one another.

The cure is the crossing LANE (`lpRaceLane`, LPX.RACE_LANE_NEAR / RACE_LANE_FULL / RACE_LANE_PAD): while it
passes, the PASSING row's label and value step into its own bar, and step back out when it is clear. The axis
is forced - two labels that exchange VERTICAL order must pass through one another whatever share of a row
they are shifted by - and the openness is read off the pair's own separation on the page, which is what makes
it hold on either path setting. Everything is a pure function of u.

The proof here is the PLAYER's own boxes (`getBoundingClientRect`, as test_figure_placement.py reads them),
not the maths behind them: every pair of labels and every pair of values, right across every crossing in the
fixture, on BOTH path settings. Plus the committed golden `race-swap` at the crossing itself.
"""
from __future__ import annotations

import contextlib
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

# every crossing in the fixture's five rows, in period units (the engine solves the same roots)
CROSSINGS = {("ALPHA", "CHI"): G.race_crossing("ALPHA", "CHI"),
             ("BETA", "CHI"): G.race_crossing("BETA", "CHI"),
             ("ALPHA", "BETA"): G.race_crossing("ALPHA", "BETA"),
             ("CHI", "DELTA"): G.race_crossing("CHI", "DELTA")}
SWEEP = [round(0.025 * k - 0.35, 3) for k in range(29)]   # +-0.35 of a period around a crossing, at 30 ms
PINNED = G.race_t(G.RACE_SWAP_U)          # the golden's instant: the ALPHA/BETA crossing, 7.407 s
KNOTS = [G.race_t(i) for i in range(len(G.RACE_PERIODS))]
NAME_X, TRACK_X = 150.0, 172.0   # buildLedgerRace's G: the name column's right edge, and where the track starts
RESTING_X = f"{NAME_X:.1f}"      # where a row's name sits when it is not passing anybody


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---- the page, in the player ---------------------------------------------------------------------------

PROBE = """() => {
  const st = window.wA?.__lp || window.wB?.__lp || document.querySelector('.world')?.__lp;
  const R = st.race, stg = document.getElementById('stage').getBoundingClientRect();
  const box = (el) => { const r = el.getBoundingClientRect(); return [r.x - stg.x, r.y - stg.y, r.width, r.height]; };
  const ty = (el) => Number(/translate\\(0 (-?[\\d.]+)\\)/.exec(el.getAttribute('transform'))[1]);
  return { path: R.path || null,
           rows: R.items.map((it) => { const lab = it.g.querySelector('text.lab');
             return { name: lab.textContent, value: it.val.textContent, y: ty(it.g),
                      lab_x: lab.getAttribute('x'), val_x: Number(it.val.getAttribute('x')),
                      lab_y: lab.getAttribute('y'), val_y: it.val.getAttribute('y'),
                      bar_end: Number(it.bar.getAttribute('x')) + Number(it.bar.getAttribute('width')),
                      lab_box: box(lab), val_box: box(it.val) }; }) };
}"""


@contextlib.contextmanager
def _browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    try:
        yield br
    finally:
        br.close(); pw.stop()


class _Player:
    """The race, served and mounted from the GOLDEN's own source, so the test and the committed frame read
    the same page. `setting` names the path (E91 s1): the crossings are the same crossings in both."""

    def __init__(self, browser, setting: str):
        tl, uris, _t, aspect = RB.load_surface(f"race-path-{setting}")
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / f"race-swap-{setting}.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE[aspect]
        self._srv, port = RB.serve(html.parent)
        self.page = browser.new_context(viewport={"width": w, "height": h}).new_page()
        self.errors: list[str] = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, w, h)

    def at(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                           "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE)

    def close(self) -> None:
        self.page.context.close(); self._srv.shutdown(); self._td.cleanup()


def _overlap(a: list[float], b: list[float]) -> tuple[float, float]:
    """The shared width and height of two [x, y, w, h] boxes - both positive is ink on ink."""
    return (min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]),
            min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))


def _collisions(read: dict) -> list[str]:
    """Every pair of the page's own row labels, and every pair of its values, that share ink."""
    out = []
    rows = read["rows"]
    for kind, key, text in (("label", "lab_box", "name"), ("value", "val_box", "value")):
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                if not rows[i][text] or not rows[j][text]:
                    continue
                ow, oh = _overlap(rows[i][key], rows[j][key])
                if ow > 0 and oh > 0:
                    out.append(f"{kind}s {rows[i][text]!r} and {rows[j][text]!r} share "
                               f"{ow:.0f}x{oh:.0f} px ({rows[i][key]} / {rows[j][key]})")
    return out


@needs_browser
@pytest.mark.parametrize("setting", ["eased", "clothoid"])
def test_two_rows_never_print_on_one_another_through_a_crossing(setting):
    """E91 s2, the whole claim: at every crossing in the fixture, and right across each crossing's window,
    no two labels and no two values share a pixel - on either path setting."""
    with _browser() as br:
        p = _Player(br, setting)
        try:
            bad: list[str] = []
            for pair, u in CROSSINGS.items():
                for d in SWEEP:
                    t = G.race_t(u + d)
                    for line in _collisions(p.at(t)):
                        bad.append(f"{setting} {pair[0]}/{pair[1]} crossing at u={u:.3f}, t={t:.3f}: {line}")
            assert not bad, f"{len(bad)} collision(s):\n" + "\n".join(bad[:12])
            assert not p.errors, p.errors
        finally:
            p.close()


@needs_browser
@pytest.mark.parametrize("setting", ["eased", "clothoid"])
def test_the_passing_row_is_the_one_in_the_lane(setting):
    """The cure is not a fade and it is not a scramble: at the crossing both names and both numbers are on
    the page, the row being passed has not moved, and the row coming through is inside its own bar."""
    with _browser() as br:
        p = _Player(br, setting)
        try:
            read = p.at(PINNED)
            rows = {r["name"]: r for r in read["rows"]}
            a, b = rows["ALPHA"], rows["BETA"]          # BETA takes second place off ALPHA here
            assert a["value"] and b["value"], (a, b)
            assert a["lab_x"] == RESTING_X, ("the row being passed keeps its place", a["lab_x"])
            assert float(b["lab_x"]) > TRACK_X, ("the passing row's name steps into its bar", b["lab_x"])
            assert b["val_x"] < b["bar_end"], ("and so does its value", b["val_x"], b["bar_end"])
            assert a["val_x"] > a["bar_end"], ("while the passed row's value stays outside its bar", a)
            assert not _collisions(read), _collisions(read)
            assert not p.errors, p.errors
        finally:
            p.close()


@needs_browser
@pytest.mark.parametrize("setting", ["eased", "clothoid"])
def test_the_lane_is_shut_wherever_no_pair_is_crossing(setting):
    """The whole reason every page built before this slice is byte-identical: with no crossing in flight the
    label and the value sit exactly where the builder put them - and the lane never touches the vertical."""
    with _browser() as br:
        p = _Player(br, setting)
        try:
            for t in KNOTS + [G.race_t(G.RACE_U)]:   # every period boundary, and the path pair's own instant
                for r in p.at(t)["rows"]:
                    assert r["lab_x"] == RESTING_X, (t, r)
                    assert r["val_x"] > r["bar_end"], (t, r)
            for t in [G.race_t(u + d) for u in CROSSINGS.values() for d in (-0.35, 0.35)] + [PINNED]:
                for r in p.at(t)["rows"]:   # a label's y is the builder's, at every instant, crossing or not
                    assert r["lab_y"] == r["val_y"] == "49.0", (t, r)
            assert not p.errors, p.errors
        finally:
            p.close()


@needs_browser
def test_a_cold_seek_into_the_swap_lands_where_a_play_does():
    """The lane is a pure function of u: it is read off the swaps the build solved and the positions those
    swaps produce, never off the clock."""
    with _browser() as br:
        p = _Player(br, "eased")
        try:
            cold = p.at(PINNED)
            p.at(KNOTS[-1]); p.at(KNOTS[0]); p.at(PINNED - 0.2)
            assert p.at(PINNED) == cold
            assert not p.errors, p.errors
        finally:
            p.close()


# ---- the committed frame -------------------------------------------------------------------------------


@needs_browser
def test_the_swap_golden_is_unchanged():
    """`race-swap`: the crossing the operator's still was taken at, read as a frame (P39 T3's harness)."""
    assert (RB.SOURCES / "race-swap.timeline.json").exists()
    assert (RB.FRAMES / "race-swap.png").exists(), "no golden frame - render it with render_baseline.py"
    failures = RB.check(["race-swap"])
    assert not failures, "\n".join(failures)
