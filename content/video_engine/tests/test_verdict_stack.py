"""P61 T7 - THE VERDICT STACK ON A SHORT: the five phases, measured on the rendered 9:16 surface.

E99 s21, the operator on the first attempt: *"We're missing some of the choreography, our cards in steel and paper
felt much more alive, and also it didn't just place them horizontally, we had real choreography and movement, which
then made the burst better as well, but this is the right direction."*

A golden frame proves a phase LOOKS right; these tests prove it IS right - the rectangles on the stage at the five
instants, read the way `gate_vertical_safe_box.py` reads a built player:

  * ENTER  - one card at a time, arriving from depth (translateZ, rotateY), not appearing
  * FOCUS  - large near the safe box's centre while its phrase is spoken
  * MOSAIC - the rails scattered over the whole height of the box, NEVER a horizontal row
  * IDLE   - the railed cards move, every one of them, and by a few px (E49, a named kind)
  * BURST  - radial from the mosaic's own centre, 60 ms apart

plus: every card stays inside G-l's safe box for its whole life, two seeks to one t give one frame, and the
FULL-FRAME dials are untouched (its goldens are test_golden_frames.py's business; what is pinned here is that
nothing in this slice moved a landscape number).

The browser work is one page for the whole module: it is seeked, never reloaded, which is also what makes the
two-seeks test meaningful.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as BST  # noqa: E402
import render_baseline as RB  # noqa: E402

SURFACE = "verdict-stack-9x16"
MODULE = ROOT / "content/video_engine/scripts/species/verdict.mjs"
STAGE_W, STAGE_H = RB.STAGE["9:16"]
SAFE_X, SAFE_Y = (80, 880), (280, 1340)          # gate_vertical_safe_box.py SAFE_X / SAFE_Y
ITEMS_AT = [2.0, 3.5, 5.0, 6.4, 7.8, 9.2, 10.6, 12.2, 13.8]   # build_golden_sources.STACK9_ITEMS_AT
CLEAR_AT = 16.5                                               # build_golden_sources.STACK9_CLEAR_AT
T_ENTER, T_FOCUS, T_MOSAIC, T_IDLE, T_BURST = 2.25, 3.1, 13.6, 15.4, 16.75
STAGGER = 0.06                                                # verdict.mjs BURST_STAGGER

RECTS_JS = """() => {
  const st = document.getElementById('stage').getBoundingClientRect();
  return [...document.querySelectorAll('.stackcard')].map((c, i) => {
    const b = c.getBoundingClientRect();
    return {i, x: b.x - st.x, y: b.y - st.y, w: b.width, h: b.height,
            cx: b.x - st.x + b.width / 2, cy: b.y - st.y + b.height / 2,
            op: parseFloat(c.style.opacity || '1'), z: c.style.zIndex, tf: c.style.transform};
  });
}"""


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


CHROMIUM = _chromium_available()
needs_browser = pytest.mark.skipif(not CHROMIUM, reason="playwright chromium not installed")


class Reader:
    """The surface, seeked. `at(t)` is every `.stackcard`'s rectangle on the stage at t."""

    def __init__(self, page) -> None:
        self.page = page

    def at(self, t: float) -> list[dict]:
        self.page.evaluate(
            "t => { const s = document.getElementById('scrub');"
            " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(RECTS_JS)

    def visible(self, t: float) -> list[dict]:
        return [r for r in self.at(t) if r["op"] > 0.01]


@pytest.fixture(scope="module")
def reader():
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface(SURFACE)
    assert aspect == "9:16", f"{SURFACE} is not a portrait surface"
    with tempfile.TemporaryDirectory() as td:
        page_path = Path(td) / "surface.html"
        page_path.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(Path(td))
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_context(viewport={"width": STAGE_W, "height": STAGE_H}).new_page()
                page.goto(f"http://127.0.0.1:{port}/surface.html", wait_until="networkidle", timeout=180000)
                RB.prepare_page(page, STAGE_W, STAGE_H)
                yield Reader(page)
                browser.close()
        finally:
            srv.shutdown()


# --------------------------------------------------------------------- the compiler's own times

def test_stack_entry_derives_the_host_docks_window_from_the_beats() -> None:
    items = [{"id": f"ev-{i}", "at": at} for i, at in enumerate(ITEMS_AT)]
    payload, enter, exitt = BST.stack_entry(items, CLEAR_AT, form="9:16")
    assert payload["clear_at"] == CLEAR_AT and payload["form"] == "9:16"
    assert [it["at"] for it in payload["items"]] == ITEMS_AT
    assert enter == round(ITEMS_AT[0] - BST.STACK_ENTER_LEAD, 2)
    # nine cards, 60 ms apart, 0.5 s each = 0.98 s, so doc 29's own ~1 s floor is what holds here
    assert exitt == round(CLEAR_AT + max(BST.STACK_HOLD_AFTER,
                                         (len(ITEMS_AT) - 1) * BST.STACK_BURST_STAGGER + BST.STACK_BURST_S), 2)
    # ... and with enough cards the stagger takes over: 20 of them outlast the floor
    many = [{"id": f"ev-{i}", "at": round(2.0 + 0.6 * i, 2)} for i in range(20)]
    assert BST.stack_entry(many, 16.0)[2] == round(16.0 + 19 * BST.STACK_BURST_STAGGER + BST.STACK_BURST_S, 2)


def test_stack_entry_refuses_a_window_that_cuts_the_choreography() -> None:
    items = [{"id": "a", "at": 2.0}, {"id": "b", "at": 3.5}]
    with pytest.raises(ValueError, match="before the burst finishes"):
        BST.stack_entry(items, 6.0, exitt=6.2)
    with pytest.raises(ValueError, match="after the first proof"):
        BST.stack_entry(items, 6.0, enter=2.5)
    with pytest.raises(ValueError, match="ONE AT A TIME"):
        BST.stack_entry([{"id": "a", "at": 3.5}, {"id": "b", "at": 3.5}], 6.0)
    with pytest.raises(ValueError, match="never be read"):
        BST.stack_entry(items, 4.0)
    with pytest.raises(ValueError, match="a LIST of proofs"):
        BST.stack_entry([{"id": "a", "at": 2.0}], 6.0)
    with pytest.raises(ValueError, match="not one of"):
        BST.stack_entry(items, 6.0, form="4:3")


def test_the_compilers_stack_dials_still_mirror_the_module() -> None:
    """One timing fact in one file (doc 29 s9.24): the compiler cannot import the painter, so it copies three
    numbers - and a copy that is not checked is a drift waiting to happen."""
    src = MODULE.read_text(encoding="utf-8")
    for name, value in (("LAST_RECEDE_LEAD", BST.STACK_RECEDE_LEAD),
                        ("BURST_STAGGER", BST.STACK_BURST_STAGGER),
                        ("BURST_S", BST.STACK_BURST_S),
                        ("MOUNT_LEAD", BST.STACK_ENTER_LEAD)):
        m = re.search(rf"^\s*{name}:\s*([\d.]+),", src, re.M)
        assert m, f"{name} is no longer a dial of VERDICT"
        assert float(m.group(1)) == value, f"{name}: verdict.mjs says {m.group(1)}, the compiler says {value}"


def test_the_full_frame_dials_are_untouched() -> None:
    """The 16:9 form's goldens are byte-identical because its numbers are: the nine landscape spots and the focus
    pose, pinned here so a portrait tweak that reached them fails by name and not by a pixel diff."""
    src = MODULE.read_text(encoding="utf-8")
    assert "Object.freeze([2, 5, 24]), Object.freeze([27, 3, 22]), Object.freeze([51, 4, 22]), Object.freeze([74, 5, 24])" in src
    assert "Object.freeze([1, 40, 22]), Object.freeze([77, 40, 22])" in src
    assert "Object.freeze([4, 62, 26]), Object.freeze([37, 66, 24]), Object.freeze([68, 62, 26])" in src
    for line in ("ACTIVE_X: 930,", "ACTIVE_Y: 400,", "ACTIVE_W: 840,", "ENTER_SWING: 460,", "ENTER_Z: -700,",
                 "BURST_NORM_X: 700,", "BURST_NORM_Y: 460,", "ORIGIN_X: 0.5,", "IDLE_KIND: null,"):
        assert line in src, f"the full-frame dial `{line}` moved"


def test_the_short_names_an_idle_kind_that_the_idle_module_knows() -> None:
    """E49: every idle is a NAMED kind. The short's rails carry one - and it has to be one idle.mjs paints."""
    src = MODULE.read_text(encoding="utf-8")
    kind = re.search(r'IDLE_KIND:\s*"(\w+)"', src)
    assert kind, "the short's form declares no idle kind"
    kinds = (ROOT / "content/video_engine/scripts/kinetics/idle.mjs").read_text(encoding="utf-8")
    assert re.search(rf'IDLE_KINDS = Object\.freeze\(\[[^\]]*"{kind.group(1)}"', kinds), \
        f"{kind.group(1)} is not one of idle.mjs's IDLE_KINDS"


# --------------------------------------------------------------------- the five phases, on the stage

@needs_browser
def test_enter_one_card_at_a_time_from_depth(reader) -> None:
    on = reader.visible(T_ENTER)
    assert len(on) == 1, f"{len(on)} cards on screen at {T_ENTER}s - the proofs enter ONE AT A TIME, on their own phrase"
    card = on[0]
    assert card["i"] == 0 and 0 < card["op"] < 1, "the first proof is mid-flight, not landed"
    z = re.search(r"translateZ\((-?[\d.]+)px\)", card["tf"])
    y = re.search(r"rotateY\((-?[\d.]+)deg\)", card["tf"])
    assert z and float(z.group(1)) < -100, f"no depth left in the enter: {card['tf']}"
    assert y and abs(float(y.group(1))) > 1, f"the card is not turned as it comes: {card['tf']}"
    # and nothing has entered before its beat
    assert reader.visible(ITEMS_AT[0] - 0.05) == []


@needs_browser
def test_focus_holds_large_near_the_safe_boxs_centre(reader) -> None:
    on = reader.visible(T_FOCUS)
    assert len(on) == 1, "the focus phase is the talking card alone"
    card = on[0]
    assert card["w"] >= 0.55 * STAGE_W, f"the focus card is {card['w']:.0f}px wide on a {STAGE_W}px stage - not LARGE"
    box_cx, box_cy = sum(SAFE_X) / 2, sum(SAFE_Y) / 2
    assert abs(card["cx"] - box_cx) <= 60, f"focus centre x {card['cx']:.0f} is not near the box's centre {box_cx}"
    assert abs(card["cy"] - box_cy) <= 120, f"focus centre y {card['cy']:.0f} is not near the box's centre {box_cy}"
    rails = [r for r in reader.at(T_MOSAIC) if r["op"] > 0.01 and r["z"] != "9"]
    assert card["w"] >= 1.4 * max(r["w"] for r in rails), "the focus card does not read as bigger than the rails"


@needs_browser
def test_the_mosaic_is_never_a_horizontal_row(reader) -> None:
    on = reader.visible(T_MOSAIC)
    assert len(on) == 8, f"{len(on)} proofs placed at {T_MOSAIC}s, expected 8"
    rails = [r for r in on if r["z"] != "9"]
    assert len(rails) == 7
    tops = sorted(r["y"] for r in rails)
    assert tops[-1] - tops[0] >= 0.25 * STAGE_H, \
        f"the rails span {tops[-1] - tops[0]:.0f}px of a {STAGE_H}px stage - that is a row, not a mosaic"
    # no band of 60px holds half the rails (the defect: four cards in a line across the top)
    for t0 in tops:
        band = [y for y in tops if t0 <= y <= t0 + 60]
        assert len(band) < len(rails) / 2 + 1, f"{len(band)} rails inside one 60px band at y {t0:.0f} - a row"
    # and the wall is not a two-column grid either: the left edges take four places or more
    lefts = sorted(r["x"] for r in rails)
    columns = 1 + sum(1 for a, b in zip(lefts, lefts[1:]) if b - a > 40)
    assert columns >= 4, f"the rails stand in {columns} columns - a grid, not a scatter: {[round(x) for x in lefts]}"
    widths = {round(r["w"]) for r in rails}
    assert len(widths) >= 5, f"the rails come in {len(widths)} sizes - a wall of one size is a grid"


@needs_browser
def test_every_card_stays_inside_the_vertical_safe_box(reader) -> None:
    """G-l: platform chrome covers the top 280, the bottom 480 and the right 200px of a short. The 16:9 spots put
    four cards inside the top chrome and hung two off the edges - that is what this checks can never come back."""
    bad = []
    t = ITEMS_AT[0]
    while t <= CLEAR_AT:                      # up to the burst; the throw is MEANT to leave the frame
        for r in reader.at(round(t, 2)):
            if r["op"] <= 0.99:               # judge a card once it is fully on screen
                continue
            if r["x"] < SAFE_X[0] or r["x"] + r["w"] > SAFE_X[1] or r["y"] < SAFE_Y[0] or r["y"] + r["h"] > SAFE_Y[1]:
                bad.append((round(t, 2), r["i"], round(r["x"]), round(r["y"]), round(r["w"]), round(r["h"])))
        t += 0.25
    assert not bad, f"cards outside x{SAFE_X} y{SAFE_Y}: {bad[:6]}"


@needs_browser
def test_the_railed_cards_idle_and_none_of_them_is_still(reader) -> None:
    """E49: nothing ever goes truly still. Every railed card has moved a little 0.35s later - and only a little."""
    before = {r["i"]: r for r in reader.visible(T_IDLE) if r["z"] != "9"}
    after = {r["i"]: r for r in reader.visible(T_IDLE + 0.35) if r["z"] != "9"}
    assert len(before) == 8 and set(before) == set(after)
    for i, r in before.items():
        moved = max(abs(after[i]["cx"] - r["cx"]), abs(after[i]["cy"] - r["cy"]),
                    abs(after[i]["w"] - r["w"]))
        assert moved >= 0.3, f"rail {i} is bit-identical 0.35s later ({moved:.2f}px) - a dead card (E49)"
        assert moved <= 25, f"rail {i} moved {moved:.1f}px in 0.35s - that is a move, not an idle"


@needs_browser
def test_the_burst_is_radial_from_the_mosaics_centre_and_60ms_apart(reader) -> None:
    rest = {r["i"]: r for r in reader.at(CLEAR_AT - 0.01)}
    box_cx, box_cy = sum(SAFE_X) / 2, sum(SAFE_Y) / 2
    n = len(rest)

    def throw(i: int, t: float) -> tuple[float, float]:
        r = [x for x in reader.at(round(t, 3)) if x["i"] == i][0]
        return r["cx"] - rest[i]["cx"], r["cy"] - rest[i]["cy"]

    # EVERY card leaves along its own bearing, away from the wall's centre - not toward one exit
    full = {}
    for i in range(n):
        dx, dy = throw(i, CLEAR_AT + i * STAGGER + BST.STACK_BURST_S)     # cb = 1: the whole throw
        bx, by = rest[i]["cx"] - box_cx, rest[i]["cy"] - box_cy
        assert dx * bx + dy * by > 0, f"card {i} is thrown toward the centre of the wall, not away from it"
        full[i] = (dx * dx + dy * dy) ** 0.5
        assert full[i] > 200, f"card {i} barely moves ({full[i]:.0f}px) - the burst is the rhetoric, not a fade"

    # THE 60 ms: card i's throw at t + i x STAGGER is the SAME share of its own bearing as card 0's at t
    shares = []
    for i in range(n):
        dx, dy = throw(i, CLEAR_AT + i * STAGGER + 0.25)
        shares.append((dx * dx + dy * dy) ** 0.5 / full[i])
    assert max(shares) - min(shares) < 0.02,         f"the cards are not {STAGGER}s apart: at their own +0.25s they are {min(shares):.3f}-{max(shares):.3f} through"
    assert 0.1 < shares[0] < 0.9, "the instant chosen proves nothing - the throw is over or has not begun"

    # and at ONE instant they are visibly staggered, the later cards still at rest
    fired = reader.at(T_BURST)
    moved = [r["i"] for r in fired if abs(r["cx"] - rest[r["i"]]["cx"]) + abs(r["cy"] - rest[r["i"]]["cy"]) > 2]
    assert 3 <= len(moved) <= n - 1, f"{len(moved)} of {n} cards away at {T_BURST}s - the stagger is not legible"
    assert moved == sorted(moved), "the cards leave out of order"


@needs_browser
def test_two_seeks_to_one_instant_give_one_frame(reader) -> None:
    """A pose is a pure function of t: the enter, the idle, the drift and the burst read the clock and nothing else."""
    for t in (T_ENTER, T_FOCUS, T_MOSAIC, T_IDLE, T_BURST):
        reader.at(5.0)
        forward = reader.at(t)
        reader.at(20.0)
        assert reader.at(t) == forward, f"two seeks to {t}s gave two frames"
