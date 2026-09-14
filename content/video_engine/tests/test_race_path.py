"""E91 s1 / BACKLOG R26-78 (P57 T15): THE RACE'S TWO PATH SETTINGS.

The operator, human gate 5 of P52 (the race A/B): *"both Arm A and B look good to me, Arm A is smoother, but
Arm B has more dynamism/energy to it. seems like 2 settings to me, not a discard situation."* So a race page
NAMES its path on the row: `path=eased` (the default - the engine as it has always been, arm A) or
`path=clothoid` (arm B, the chain of clothoid segments fitted through the same period knots).

What this file holds, and the whole of what the setting may do:
  - the grammar: the key is a RACE page's, and any other word is refused BY NAME;
  - THE PERIOD CLOCK IS IDENTICAL IN BOTH - every row sits at the same place at every period boundary, to a
    twentieth of a pixel, because a clothoid segment's ends ARE the knots it was fitted to;
  - between two knots the marks travel different paths - a different lane and a different length of bar;
  - the page reads the same either way: the same rows, in the same rank order, with the same names;
  - a cold seek lands where a play does (the position is a pure function of u in both settings);
  - the two committed frames (`race-path-eased` / `race-path-clothoid`) are the pair, byte-exact.
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

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

STEEL = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
RACE_ID = "ev-race-path-v1"
KNOTS = [G.race_t(i) for i in range(len(G.RACE_PERIODS))]              # every period boundary, in scene seconds
MIDS = [G.race_t(i + 0.5) for i in range(len(G.RACE_PERIODS) - 1)]     # halfway through every segment
PINNED = G.race_t(G.RACE_U)                                            # the instant the golden pair is read at
KNOT_EPS = 0.05    # px: what "the knots do not move" means when one arm reaches its knot through a fitted curve
MOVED_PX = 2.0     # px: what "a different path" means on a 1000 px page - a twentieth of a row's pitch


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---- the grammar -------------------------------------------------------------------------------------


def test_both_settings_ship_and_eased_is_the_default():
    """E91 s1: neither is discarded, and the default is the engine as it is."""
    assert B.RACE_PATHS == ("eased", "clothoid") and B.RACE_PATHS[0] == "eased"
    assert "path" in B.PLATE_OPTS


@pytest.mark.parametrize("word", ["spline", "clothoidal", "smooth", "eased "])
def test_an_unknown_path_is_refused_by_name(word):
    with pytest.raises(ValueError) as exc:
        B.split_plate_opts(f"ledger:{RACE_ID}:race;path={word}")
    assert "path" in str(exc.value) and "eased|clothoid" in str(exc.value), str(exc.value)


def _race_ep(tmp_path: Path) -> Path:
    """An episode dir carrying the golden pair's own synthetic race object - the compiler reads data from a
    series file and nowhere else (doc 29 s9.26)."""
    objects = tmp_path / "evidence/objects"
    objects.mkdir(parents=True, exist_ok=True)
    (objects / f"{RACE_ID}.series.json").write_text(json.dumps(G.race_series(), indent=1), encoding="utf-8")
    return tmp_path


def test_a_race_page_that_names_no_path_carries_no_key(tmp_path):
    """The default is unchanged and writes nothing: every page built before this slice is byte-identical."""
    world = B.world_for_plate(f"ledger:{RACE_ID}:race", (0, 0, 0), _race_ep(tmp_path))
    assert world["page"]["builder"] == "race" and "path" not in world["page"]


@pytest.mark.parametrize("setting", ["eased", "clothoid"])
def test_a_race_row_may_name_either_path(setting, tmp_path):
    world = B.world_for_plate(f"ledger:{RACE_ID}:race;path={setting}", (0, 0, 0), _race_ep(tmp_path))
    assert world["page"]["path"] == setting


def test_the_path_is_a_race_page_option():
    """A line page has no periods to move between: the option is refused, and the message says what the page is."""
    with pytest.raises(ValueError) as exc:
        B.world_for_plate("ledger:ev-divergence-v1:line;path=clothoid", (0, 0, 0), STEEL)
    assert "RACE page option" in str(exc.value) and "dense-line" in str(exc.value), str(exc.value)


# ---- the page, in the player -------------------------------------------------------------------------


PROBE = """() => {
  const st = window.wA?.__lp || window.wB?.__lp || document.querySelector('.world')?.__lp;
  const R = st.race;
  const ty = (el) => Number(/translate\\(0 (-?[\\d.]+)\\)/.exec(el.getAttribute('transform'))[1]);
  return { path: R.path || null,
           rows: R.items.map((it, j) => ({ name: it.g.querySelector('text.lab').textContent,
                                           y: ty(it.g), w: Number(it.bar.getAttribute('width')) })) };
}"""


@contextlib.contextmanager
def _browser():
    """ONE browser for both arms: the sync API is a single fibre per thread, so a second playwright started
    while the first is live is an error, and the pair has to be read side by side."""
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    try:
        yield br
    finally:
        br.close(); pw.stop()


class _Player:
    """One arm of the pair, served and mounted from the GOLDEN's own source, so the test and the committed
    frames read the same page."""

    def __init__(self, browser, setting: str):
        tl, uris, _t, aspect = RB.load_surface(f"race-path-{setting}")
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / f"race-{setting}.html"
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


def _order(read: dict) -> list[str]:
    """The rank order the viewer reads off the page: the row names, top to bottom."""
    return [r["name"] for r in sorted(read["rows"], key=lambda r: r["y"])]


@needs_browser
def test_the_two_settings_agree_at_every_knot_and_travel_differently_between_them():
    """E91 s1, the whole claim in one test: the clock and the knots are identical, the path is not."""
    with _browser() as br:
        a, b = _Player(br, "eased"), _Player(br, "clothoid")
        try:
            assert a.at(PINNED)["path"] == "eased" and b.at(PINNED)["path"] == "clothoid"
            for t in KNOTS:   # THE PERIOD CLOCK: every row at the same place, in the same order, at every boundary
                ra, rb = a.at(t), b.at(t)
                assert _order(ra) == _order(rb), (t, _order(ra), _order(rb))
                for x, y in zip(ra["rows"], rb["rows"]):
                    assert x["name"] == y["name"]
                    assert abs(x["y"] - y["y"]) <= KNOT_EPS and abs(x["w"] - y["w"]) <= KNOT_EPS, (t, x, y)
            moved_y, moved_w = [], []
            for t in MIDS:   # THE PATH: between the knots the marks are elsewhere
                ra, rb = a.at(t), b.at(t)
                moved_y.append(max(abs(x["y"] - y["y"]) for x, y in zip(ra["rows"], rb["rows"])))
                moved_w.append(max(abs(x["w"] - y["w"]) for x, y in zip(ra["rows"], rb["rows"])))
            # WHICH row is momentarily above WHICH is the crossing's own business and differs mid-swap by
            # construction (that is what a different path IS); away from a crossing - the pinned instant the
            # golden pair is read at - the page reads exactly the same, in the same order.
            assert _order(a.at(PINNED)) == _order(b.at(PINNED)) == ["CHI", "ALPHA", "BETA", "DELTA", "EPS"]
            i = MIDS.index(PINNED)
            assert moved_y[i] >= MOVED_PX, ("the pinned instant is where the golden pair is read", moved_y[i])
            assert max(moved_w) >= MOVED_PX, ("the path changes the bar's length too, not only its lane", moved_w)
            assert not a.errors and not b.errors, (a.errors, b.errors)
        finally:
            a.close(); b.close()


@needs_browser
@pytest.mark.parametrize("setting", ["eased", "clothoid"])
def test_a_cold_seek_lands_where_a_play_does(setting):
    """Both paths are pure functions of u: the fit is baked from the data, never from the clock."""
    with _browser() as br:
        p = _Player(br, setting)
        try:
            cold = p.at(PINNED)
            p.at(KNOTS[-1]); p.at(KNOTS[0])
            assert p.at(PINNED) == cold
            assert not p.errors, p.errors
        finally:
            p.close()


# ---- the committed pair ------------------------------------------------------------------------------


@needs_browser
@pytest.mark.parametrize("surface", ["race-path-eased", "race-path-clothoid"])
def test_the_golden_pair_is_unchanged(surface):
    """The pair is a golden like any other: one page, one instant, the two settings (P39 T3's harness)."""
    assert (RB.SOURCES / f"{surface}.timeline.json").exists(), surface
    assert (RB.FRAMES / f"{surface}.png").exists(), f"{surface}: no golden frame - render it with render_baseline.py"
    failures = RB.check([surface])
    assert not failures, "\n".join(failures)
