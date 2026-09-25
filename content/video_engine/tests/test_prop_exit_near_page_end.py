"""P71 T6 / R26-309 - A PROP'S AUTHORED EXIT NEAR ITS PAGE'S END IS HONOURED, measured on the served player.

Row 22's RAM prop, given an exit 0.3 s or 1.0 s before its page's slide, "stood on through the slide; only an exit
2.5 s early left" (BACKLOG-HISTORY R26-309). The cause (`$SP/p71-t6/logs/diagnosis.md`) is the engine's load-time
"SNAP NEAR-BOUNDARY EXITS TO THE BOUNDARY": any dock that exits 0.05-1.4 s before a scene boundary had its exit
moved to the boundary. That rule exists for a CARD, which the turn carries off in one motion. For a stamped prop the
mark's own exit (E50: `stampExit`, the ease-IN cubic over STAMP_ARRIVAL.EXIT_S) then began AT the boundary and ran
over the incoming page. A prop, or a stamped mark, OWNS its exit: the engine now honours it to the frame. s106: an
exit whose owed curve outruns the page is not an untruth, so it is not refused.

What this file reads, on the committed `prop-stamp` golden's own page split into two scenes at PAGE_END:
  (1) HONOURED     for leads 0.3, 1.0 and 2.5 s before a `slide:left` turn, the dock's opacity at every sampled frame
                   is 1 - stampExit(t - exit) from the AUTHORED exit, and it is 0 from exit + EXIT_S on;
  (2) GONE IN TIME a lead longer than the owed curve (1.0, 2.5) leaves the prop gone before the page turns;
  (3) A WIPE       a prop leaving 0.3 s before a wipe is not swept back to full opacity under the front;
  (4) A CARD       a plain card 1.0 s before the turn still rides it (its exit is still carried to the boundary) -
                   the rule every card was built on stays byte for byte;
  (5) A SPRING PROP a prop that does not stamp leaves on its own retract from its authored exit too.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

SURFACE = "prop-stamp"              # the stamped Fed prop on a ledger page; it enters at 10.0 and is settled by ~11.3
PAGE_END = 20.0                     # the page's end: the boundary the next scene arrives on
LEADS = (0.3, 1.0, 2.5)             # R26-309's three exits, seconds before the page's end
STEP = 0.05                         # the sampled frames' step
STOPACTION = ROOT / "content/video_engine/scripts/kinetics/stopaction.mjs"
TOL = 0.01                          # opacity is written to 6 places; the ease is the same cubic on both sides

PROBE = """() => { const d = document.querySelector('.dock[data-slide]');
  return d ? { op: d.style.opacity === '' ? 1 : +d.style.opacity, clip: d.style.clipPath } : null; }"""


def _node(src: str):
    r = subprocess.run(["node", "--input-type=module", "-e", src], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@pytest.fixture(scope="module")
def exit_curve():
    """EXIT_S and the owed curve, read off the module (never retyped): opacity(ts) = 1 - stampExit(ts)."""
    got = _node(f"""const m = await import({json.dumps(STOPACTION.as_uri())});
      const ts = []; for (let i = 0; i <= 200; i++) ts.push(i / 100);
      console.log(JSON.stringify({{ exit_s: m.STAMP_ARRIVAL.EXIT_S, curve: ts.map((x) => [x, m.stampExit(x)]) }}));""")
    table = dict((round(x, 2), v) for x, v in got["curve"])
    return got["exit_s"], (lambda ts: 0.0 if ts <= 0 else table[min(2.0, round(ts, 2))])


def _two_scenes(lead: float, turn: str, card: bool = False, spring: bool = False) -> tuple[dict, dict]:
    """The golden's page, cut at PAGE_END into two scenes; the next one arrives by `turn`. The dock exits `lead`
    seconds before the page's end. `card`: the same dock as a plain card (not a prop, no stamp); `spring`: a prop
    with no stop-action arrival."""
    tl, uris, _t, _a = RB.load_surface(SURFACE)
    tl, uris = copy.deepcopy(tl), dict(uris)
    s1 = tl["scenes"][0]
    d = s1["docks"][0]
    d["exit"] = round(PAGE_END - lead, 2)
    if card or spring:
        d.pop("arrive", None)
    if card:
        d["kind"] = "card"
        tl["evidence"][d["slide"]]["kind"] = "card"
    s1["span"] = [0.0, PAGE_END]
    s2 = {"scene_id": "s02", "world": copy.deepcopy(s1["world"]), "exit": turn, "span": [PAGE_END, tl["runtime_s"]],
          "docks": [], "species": []}
    tl["scenes"] = [s1, s2]
    return tl, uris


class _Player:
    def __init__(self, browser, tl: dict, uris: dict):
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / "p.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.size = RB.STAGE["16:9"]
        self._srv, port = RB.serve(html.parent)
        self.page = browser.new_context(viewport={"width": self.size[0], "height": self.size[1]}).new_page()
        self.errors: list[str] = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, *self.size)

    def at(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                           "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE)

    def close(self) -> None:
        self.page.context.close(); self._srv.shutdown(); self._td.cleanup()


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


@pytest.fixture(scope="module")
def browser():
    with SP.browser() as br:  # R26-351 (P72 T9): the one guarded Playwright start
        yield br


def _samples(exit_t: float, exit_s: float) -> list[float]:
    """From 0.1 s before the exit to 0.2 s past the owed curve's end, every STEP, plus the page's end +/- 0.05."""
    n = int(round((exit_s + 0.3) / STEP)) + 1
    ts = {round(exit_t - 0.1 + i * STEP, 3) for i in range(n)} | {round(PAGE_END - 0.05, 3), round(PAGE_END + 0.05, 3)}
    return sorted(ts)


def _opacity(p: dict | None) -> float:
    return 0.0 if p is None else float(p["op"])


@needs_browser
@pytest.mark.parametrize("lead", LEADS)
def test_a_stamped_prop_near_its_page_end_leaves_on_its_own_curve_from_its_authored_exit(browser, exit_curve, lead):
    exit_s, owed = exit_curve
    tl, uris = _two_scenes(lead, "slide:left")
    exit_t = tl["scenes"][0]["docks"][0]["exit"]
    p = _Player(browser, tl, uris)
    try:
        wrong = []
        for t in _samples(exit_t, exit_s):
            want = 1.0 - owed(t - exit_t)
            got = _opacity(p.at(t))
            if abs(got - want) > TOL:
                wrong.append(f"t={t:.2f} opacity {got:.3f}, owed {want:.3f}")
        assert not p.errors, p.errors
    finally:
        p.close()
    assert not wrong, (f"the prop authored to leave at {exit_t} ({lead} s before its page's end at {PAGE_END}) does not "
                       f"leave on its own {exit_s:.4f} s curve from that exit (R26-309): " + "; ".join(wrong[:6]))


@needs_browser
@pytest.mark.parametrize("lead", [x for x in LEADS if x > 0.6])
def test_a_prop_whose_curve_fits_is_gone_before_the_page_turns(browser, exit_curve, lead):
    exit_s, _owed = exit_curve
    assert lead > exit_s + 0.05, "the lead holds the whole owed curve"
    tl, uris = _two_scenes(lead, "slide:left")
    p = _Player(browser, tl, uris)
    try:
        before, after = _opacity(p.at(PAGE_END - 0.05)), _opacity(p.at(PAGE_END + 0.1))
    finally:
        p.close()
    assert before == 0.0 and after == 0.0, (f"exit {PAGE_END - lead}: the prop still stands at the page's end "
                                            f"({before:.3f} at {PAGE_END - 0.05}) and on the slide ({after:.3f})")


@needs_browser
def test_a_prop_leaving_just_before_a_wipe_is_not_swept_back_to_full(browser, exit_curve):
    exit_s, owed = exit_curve
    lead = 0.3
    tl, uris = _two_scenes(lead, "wipe")
    exit_t = tl["scenes"][0]["docks"][0]["exit"]
    p = _Player(browser, tl, uris)
    try:
        rows = [(t, _opacity(p.at(t))) for t in (PAGE_END + 0.02, PAGE_END + 0.1, PAGE_END + 0.2)]
    finally:
        p.close()
    wrong = [f"t={t:.2f} {got:.3f} (owed {1.0 - owed(t - exit_t):.3f})" for t, got in rows
             if abs(got - (1.0 - owed(t - exit_t))) > TOL]
    assert not wrong, "the wipe front took the prop back to full opacity over its own exit: " + "; ".join(wrong)


@needs_browser
def test_a_card_near_its_page_end_still_rides_the_turn(browser):
    """(4) the guard: a CARD's exit 1.0 s before the turn is still carried to the boundary - it stands whole to the
    page's end and leaves with the turn, as every card did before T6."""
    tl, uris = _two_scenes(1.0, "slide:left", card=True)
    p = _Player(browser, tl, uris)
    try:
        at_exit_plus, at_end = _opacity(p.at(PAGE_END - 0.6)), _opacity(p.at(PAGE_END - 0.05))
        past = _opacity(p.at(PAGE_END + 0.8))
    finally:
        p.close()
    assert at_exit_plus == 1.0 and at_end == 1.0, (at_exit_plus, at_end)
    assert past == 0.0, past


@needs_browser
def test_a_spring_prop_leaves_on_its_own_retract_from_its_authored_exit(browser):
    """(5) a prop with no stop-action arrival: its spring retract runs from the authored exit, so it is gone before
    the page's end (it used to stand whole to the boundary and retract over the incoming page)."""
    tl, uris = _two_scenes(1.0, "slide:left", spring=True)
    p = _Player(browser, tl, uris)
    try:
        before, mid, end = (_opacity(p.at(t)) for t in (PAGE_END - 1.05, PAGE_END - 0.85, PAGE_END - 0.05))
    finally:
        p.close()
    assert before == 1.0, before
    assert mid < 1.0, f"the retract has not begun 0.15 s after the authored exit: {mid:.3f}"
    assert end == 0.0, f"the prop stands at the page's end: {end:.3f}"
