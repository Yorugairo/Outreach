"""P61 T7 - THE VERDICT STACK ON A SHORT: the five phases, measured on the rendered 9:16 surface.

E99 s21, the operator on the first attempt: *"We're missing some of the choreography, our cards in steel and paper
felt much more alive, and also it didn't just place them horizontally, we had real choreography and movement, which
then made the burst better as well, but this is the right direction."*

A golden frame proves a phase LOOKS right; these tests prove it IS right - the rectangles on the stage at the five
instants, read the way `gate_vertical_safe_box.py` reads a built player:

  * ENTER  - one card at a time, arriving from depth (translateZ, rotateY), not appearing
  * FOCUS  - large near the safe box's centre while its phrase is spoken
  * MOSAIC - the rails scattered over the whole height of the box, NEVER a horizontal row
  * ORDER  - and laid in READING BANDS (P61 T7b, E99 s43): 1-2 across the top left to right, 3-4 across the
             bottom, 5-6 top, 7-8 bottom, 9 top - so the recede hands the eye to the place a reader looks next
  * IDLE   - the railed cards move, every one of them, and by a few px (E49, a named kind)
  * CENTRE - the LAST proof lands in the MIDDLE and stays there: the wall ends on it (P61 T7c, E99 s59)
  * GATHER - and over the last GATHER_LEAD every railed card draws IN toward it, monotonically, so the
             burst leaves a gathered wall (E99 s59: "we're missing the gather")
  * BURST  - radial from the mosaic's own centre, TIGHTER than Steel and Paper's own measured beat

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
SURFACE_16 = "verdict-stack"                     # the FULL-FRAME form: same choreography, its own raster (E99 s59)
MODULE = ROOT / "content/video_engine/scripts/species/verdict.mjs"
STAGE_W, STAGE_H = RB.STAGE["9:16"]
STAGE16_W, STAGE16_H = RB.STAGE["16:9"]
SAFE_X, SAFE_Y = (80, 880), (280, 1340)          # gate_vertical_safe_box.py SAFE_X / SAFE_Y
ITEMS_AT = [2.0, 3.5, 5.0, 6.4, 7.8, 9.2, 10.6, 12.2, 13.8]   # build_golden_sources.STACK9_ITEMS_AT
CLEAR_AT = 16.5                                               # build_golden_sources.STACK9_CLEAR_AT
ITEMS16_AT = [3.0, 5.0, 7.0, 9.0, 11.0, 13.0]                 # build_golden_sources.STACK_ITEMS_AT
CLEAR16_AT = 20.0                                             # build_golden_sources.STACK_CLEAR_AT
T_ENTER, T_FOCUS, T_MOSAIC, T_IDLE, T_BURST = 2.25, 3.1, 13.6, 15.4, 16.75
T_GATHER, T_GATHER16 = 15.79, 19.29              # render_baseline.PROOF_FRAMES - the two @proof-gather instants


def _dial(name: str, portrait: bool = False) -> float:
    """A dial off the module's text: the FIRST match is VERDICT's, the second (if any) the short's override."""
    src = MODULE.read_text(encoding="utf-8")
    hits = re.findall(rf"^\s*{name}:\s*(-?[\d.]+),", src, re.M)
    assert hits, f"{name} is no longer a dial of the verdict stack"
    return float(hits[1] if portrait and len(hits) > 1 else hits[0])


STAGGER = _dial("BURST_STAGGER")                 # verdict.mjs BURST_STAGGER (0.06 -> 0.035, P61 T7c)
BURST_S = _dial("BURST_S")
GATHER_LEAD = _dial("GATHER_LEAD")
GATHER_PULL = _dial("GATHER_PULL")

# THE REFERENCE, measured 2026-09-16 frame by frame off Steel and Paper's frozen build-f player over
# 701.80-728.00 s (`ev-holds-stack-v1`, nine proofs, clear_at 726.98) - the numbers "tighter" is measured against,
# and the numbers the gather's clock and easing were read from. See scratchpad/assembly/P61-T7c.md section 1.
REF = {"stagger": 0.06,          # card i fired 60 ms after card i-1: the nine over 0.48 s
       "burst_s": 0.50,          # each throw's own clock
       "gone_after": 0.99,       # the last frame with any card above opacity 0.05 was clear_at + 0.99
       "station_s": 0.90,        # the lead the beat leaves its last station change - the gather's window
       "station_px": 495.0,      # how far that move carries a card in those 0.9 s - the gather's speed budget
       "rail_drift_px": 11.2}    # the WHOLE of a settled rail's travel in the 3.29 s before the burst - no gather

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
def playwright():
    """ONE driver for the whole module: a second `sync_playwright()` inside the first one's loop is refused, and
    since P61 T7c this module reads two surfaces (the short's and the full frame's)."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        yield pw


def _reader(pw, surface: str, aspect: str, size: tuple[int, int]):
    tl, uris, _t, got = RB.load_surface(surface)
    assert got == aspect, f"{surface} is not a {aspect} surface"
    with tempfile.TemporaryDirectory() as td:
        page_path = Path(td) / f"{surface}.html"
        page_path.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(Path(td))
        try:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": size[0], "height": size[1]}).new_page()
            page.goto(f"http://127.0.0.1:{port}/{surface}.html", wait_until="networkidle", timeout=180000)
            RB.prepare_page(page, size[0], size[1])
            yield Reader(page)
            browser.close()
        finally:
            srv.shutdown()


@pytest.fixture(scope="module")
def reader(playwright):
    yield from _reader(playwright, SURFACE, "9:16", (STAGE_W, STAGE_H))


# --------------------------------------------------------------------- the compiler's own times

def test_stack_entry_derives_the_host_docks_window_from_the_beats() -> None:
    items = [{"id": f"ev-{i}", "at": at} for i, at in enumerate(ITEMS_AT)]
    payload, enter, exitt = BST.stack_entry(items, CLEAR_AT, form="9:16")
    assert payload["clear_at"] == CLEAR_AT and payload["form"] == "9:16"
    assert [it["at"] for it in payload["items"]] == ITEMS_AT
    assert enter == round(ITEMS_AT[0] - BST.STACK_ENTER_LEAD, 2)
    # nine cards, the COMPILER's 60 ms apart, 0.5 s each = 0.98 s, so doc 29's own ~1 s floor is what holds here
    # (the painter's own burst is tighter since E99 s59 - the window the compiler sizes is a ceiling, not a copy)
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
    """One timing fact in one file (doc 29 s9.24): the compiler cannot import the painter, so it copies four
    numbers - and a copy that is not checked is a drift waiting to happen.

    P61 T7c: two of the four are still EXACT (they open the window: the enter's lead, and the lead the last proof
    holds before the clear - which is now the GATHER's window, the same 0.9 s). The two BURST numbers became a
    CEILING instead of a copy: the compiler uses them only to size the host dock's exit, and E99 s59 made the burst
    TIGHTER, so a module value at or below the compiler's can never cut the choreography - while a module value
    ABOVE it would, and still fails here. `build_scene_timeline_f.py` is outside this slice's write set; bringing
    STACK_BURST_STAGGER / STACK_BURST_S down to 0.035 / 0.42 (and renaming STACK_RECEDE_LEAD) is a one-line
    compiler follow-up the lane reported and did not take."""
    src = MODULE.read_text(encoding="utf-8")
    for name, value in (("GATHER_LEAD", BST.STACK_RECEDE_LEAD),
                        ("MOUNT_LEAD", BST.STACK_ENTER_LEAD)):
        m = re.search(rf"^\s*{name}:\s*([\d.]+),", src, re.M)
        assert m, f"{name} is no longer a dial of VERDICT"
        assert float(m.group(1)) == value, f"{name}: verdict.mjs says {m.group(1)}, the compiler says {value}"
    assert STAGGER <= BST.STACK_BURST_STAGGER, \
        f"the burst is {STAGGER}s apart but the compiler sizes the window on {BST.STACK_BURST_STAGGER}s - it would cut it"
    assert BURST_S <= BST.STACK_BURST_S, \
        f"the burst runs {BURST_S}s but the compiler sizes the window on {BST.STACK_BURST_S}s - it would cut it"


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


SPOT_RE = re.compile(r"Object\.freeze\(\[([\d.]+), ([\d.]+), ([\d.]+)\]\)")
CARD_RATIO = 480 / 1056          # verdict.mjs CARD_H / CARD_W


def _spots_9x16() -> list[tuple[float, float, float, float]]:
    """The short's nine rail spots as stage rects (x0, y0, x1, y1) - read off the module, no browser needed."""
    src = MODULE.read_text(encoding="utf-8")
    block = re.search(r"const VERDICT_SPOTS_9X16 = Object\.freeze\(\[(.*?)\]\);", src, re.S)
    assert block, "VERDICT_SPOTS_9X16 is no longer a frozen array in the module"
    rects = []
    for L, T, W in SPOT_RE.findall(block.group(1)):
        x, y, w = float(L) / 100 * STAGE_W, float(T) / 100 * STAGE_H, float(W) / 100 * STAGE_W
        rects.append((x, y, x + w, y + w * CARD_RATIO))
    return rects


def test_the_rails_are_laid_in_reading_bands() -> None:
    """E99 s43 verbatim, the operator on the first mosaic: *"I realized we probably don't want to be sending peoples
    eyes scattered everywhere, probably to do 1-2 on top, left to right since thats how people read. then 3-4, on
    bottom, 5-6 on top, 7-8 on bottom etc."*

    THE RULE, on the spots themselves: the pairs alternate TOP band / BOTTOM band, and inside a band the proofs run
    left to right along a line and only ever wrap DOWN to the next one - a reading path. s21's "asymmetric spots" is
    amended by s43: the asymmetry is in SIZE and TILT (checked by the mosaic test), never in ORDER."""
    rects = _spots_9x16()
    assert len(rects) == 9, f"{len(rects)} rail spots - the short's wall is nine proofs"
    mid = sum(SAFE_Y) / 2
    bands = []
    for i, (_x0, y0, _x1, y1) in enumerate(rects):
        if y1 <= mid:
            bands.append("top")
        elif y0 >= mid:
            bands.append("bot")
        else:
            pytest.fail(f"proof {i + 1} straddles the focus card's band (y {y0:.0f}-{y1:.0f}) - it is in no band")
    assert bands == ["top", "top", "bot", "bot", "top", "top", "bot", "bot", "top"], \
        f"the bands do not alternate by pairs: {bands}"
    for a, b in ((0, 1), (2, 3), (4, 5), (6, 7)):
        assert rects[a][0] < rects[b][0], \
            f"proof {b + 1} is not to the RIGHT of proof {a + 1} ({rects[b][0]:.0f} vs {rects[a][0]:.0f}) - " \
            "a pair reads left to right"
    for name in ("top", "bot"):
        seq = [i for i, b in enumerate(bands) if b == name]
        for prev, i in zip(seq, seq[1:]):
            p, r = rects[prev], rects[i]
            share = (min(p[3], r[3]) - max(p[1], r[1])) / min(p[3] - p[1], r[3] - r[1])
            if share > 0.5:          # the same line of the band
                assert r[0] > p[0], \
                    f"proof {i + 1} sits LEFT of proof {prev + 1} on one line of the {name} band - the eye goes back"
            else:                    # a new line: a reading path wraps DOWN, never up
                assert (r[1] + r[3]) / 2 > (p[1] + p[3]) / 2, \
                    f"the {name} band climbs back up from proof {prev + 1} to proof {i + 1} instead of wrapping down"


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
def test_the_mosaic_on_the_stage_reads_in_bands_and_buries_nothing(reader) -> None:
    """The same rule as `test_the_rails_are_laid_in_reading_bands`, on the RENDERED rectangles (tilt, idle and breath
    included) - and the other half of s43's layout: the focus card is large BETWEEN the bands, so no rail is behind
    it. The first lay-out of this form lost a whole card behind proof 8."""
    on = reader.visible(T_MOSAIC)
    focus = [r for r in on if r["z"] == "9"]
    rails = {r["i"]: r for r in on if r["z"] != "9"}
    assert len(focus) == 1 and len(rails) == 7
    mid = sum(SAFE_Y) / 2
    bands = ["top" if rails[i]["cy"] < mid else "bot" for i in sorted(rails)]
    assert bands == ["top", "top", "bot", "bot", "top", "top", "bot"], \
        f"the rendered bands do not alternate by pairs: {bands}"
    for a, b in ((0, 1), (2, 3), (4, 5)):
        assert rails[a]["x"] < rails[b]["x"], \
            f"proof {b + 1} is not to the RIGHT of proof {a + 1} on the stage"
    f = focus[0]
    for i, r in rails.items():
        ox = max(0.0, min(r["x"] + r["w"], f["x"] + f["w"]) - max(r["x"], f["x"]))
        oy = max(0.0, min(r["y"] + r["h"], f["y"] + f["h"]) - max(r["y"], f["y"]))
        assert ox * oy <= 0.02 * r["w"] * r["h"], \
            f"rail {i} is {100 * ox * oy / (r['w'] * r['h']):.0f}% behind the focus card - not overlapped, BURIED"


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
    # both samples sit BEFORE the gather opens (CLEAR_AT - GATHER_LEAD): what is pinned here is the idle, and
    # once the wall draws in the rails move by tens of px on purpose (P61 T7c).
    assert T_IDLE < CLEAR_AT - GATHER_LEAD
    before = {r["i"]: r for r in reader.visible(T_IDLE - 0.35) if r["z"] != "9"}
    after = {r["i"]: r for r in reader.visible(T_IDLE) if r["z"] != "9"}
    assert len(before) == 8 and set(before) == set(after)
    for i, r in before.items():
        moved = max(abs(after[i]["cx"] - r["cx"]), abs(after[i]["cy"] - r["cy"]),
                    abs(after[i]["w"] - r["w"]))
        assert moved >= 0.3, f"rail {i} is bit-identical 0.35s later ({moved:.2f}px) - a dead card (E49)"
        assert moved <= 25, f"rail {i} moved {moved:.1f}px in 0.35s - that is a move, not an idle"


@needs_browser
def test_the_burst_is_radial_from_the_mosaics_centre_and_staggered(reader) -> None:
    rest = {r["i"]: r for r in reader.at(CLEAR_AT - 0.01)}
    box_cx, box_cy = sum(SAFE_X) / 2, sum(SAFE_Y) / 2
    n = len(rest)

    def throw(i: int, t: float) -> tuple[float, float]:
        r = [x for x in reader.at(round(t, 3)) if x["i"] == i][0]
        return r["cx"] - rest[i]["cx"], r["cy"] - rest[i]["cy"]

    # EVERY RAIL leaves along its own bearing, away from the wall's centre - not toward one exit. The CENTRE card
    # (the last proof, P61 T7c) stands AT that centre and so has no outward bearing: it is thrown straight down and
    # at the viewer, last of the wall.
    full = {}
    for i in range(n):
        dx, dy = throw(i, CLEAR_AT + i * STAGGER + BURST_S)     # cb = 1: the whole throw
        bx, by = rest[i]["cx"] - box_cx, rest[i]["cy"] - box_cy
        if i == n - 1:
            assert dy > 200 and abs(dx) < 40, f"the centre card is not thrown DOWN and out: ({dx:.0f}, {dy:.0f})"
        else:
            assert dx * bx + dy * by > 0, f"card {i} is thrown toward the centre of the wall, not away from it"
        full[i] = (dx * dx + dy * dy) ** 0.5
        assert full[i] > 200, f"card {i} barely moves ({full[i]:.0f}px) - the burst is the rhetoric, not a fade"

    # THE STAGGER (0.035 s since E99 s59; the reference's own is 0.06): card i's throw at t + i x STAGGER is the
    # SAME share of its own bearing as card 0's at t
    shares = []
    for i in range(n):
        dx, dy = throw(i, CLEAR_AT + i * STAGGER + 0.2)
        shares.append((dx * dx + dy * dy) ** 0.5 / full[i])
    assert max(shares) - min(shares) < 0.02,         f"the cards are not {STAGGER}s apart: at their own +0.25s they are {min(shares):.3f}-{max(shares):.3f} through"
    assert 0.1 < shares[0] < 0.9, "the instant chosen proves nothing - the throw is over or has not begun"

    # and at ONE instant they are visibly staggered, the later cards still at rest
    fired = reader.at(T_BURST)
    moved = [r["i"] for r in fired if abs(r["cx"] - rest[r["i"]]["cx"]) + abs(r["cy"] - rest[r["i"]]["cy"]) > 2]
    assert 3 <= len(moved) <= n - 1, f"{len(moved)} of {n} cards away at {T_BURST}s - the stagger is not legible"
    assert moved == sorted(moved), "the cards leave out of order"


# --------------------------------------------------------------------- P61 T7c: the centre, the gather, the burst


@pytest.fixture(scope="module")
def reader16(playwright):
    """The FULL-FRAME surface, seeked - the same reads on the form that keeps its raster (E99 s59)."""
    yield from _reader(playwright, SURFACE_16, "16:9", (STAGE16_W, STAGE16_H))


def _focus_spot(i: int, portrait: bool) -> tuple[float, float]:
    """Card i's FOCUS pose centre in stage px - verdictFocusRect, off the module's own dials."""
    ax, dx = _dial("ACTIVE_X", portrait), _dial("ACTIVE_DX", portrait)
    ay, rdy = _dial("ACTIVE_Y", portrait), _dial("ACTIVE_ROW_DY", portrait)
    return ax + (dx if i % 2 else -dx), ay + (i % int(_dial("ACTIVE_ROWS", portrait))) * rdy


def _last_card_rests_at_the_centre(rd, items_at, clear_at, portrait) -> None:
    """E99 s59: *"the last card should land in the middle"* - and STAYS there: the wall ends on it. Read from the
    last proof's landing (its beat + ENTER_S) to the frame before the clear."""
    n = len(items_at)
    fx, fy = _focus_spot(n - 1, portrait)
    stage_w = STAGE_W if portrait else STAGE16_W
    t = items_at[-1] + _dial("ENTER_S", portrait)
    while t < clear_at:
        card = [r for r in rd.at(round(t, 2)) if r["i"] == n - 1][0]
        assert card["z"] == "9", f"the last proof left the focus at {t:.2f}s - the wall must END on it"
        assert abs(card["cx"] - fx) <= 40, f"at {t:.2f}s the last proof is at x {card['cx']:.0f}, not the centre {fx:.0f}"
        assert abs(card["cy"] - fy) <= 40, f"at {t:.2f}s the last proof is at y {card['cy']:.0f}, not the centre {fy:.0f}"
        assert card["w"] >= 0.98 * _dial("ACTIVE_W", portrait), \
            f"at {t:.2f}s the last proof is {card['w']:.0f}px wide on a {stage_w}px stage - it receded off the centre"
        t += 0.25


def _the_wall_only_ever_closes(rd, items_at, clear_at, portrait) -> None:
    """THE GATHER (E99 s59): over the last GATHER_LEAD every railed card's distance to the CENTRE card falls, frame
    by frame - and by a real distance, not the reference's 11.2 px of drift."""
    n = len(items_at)
    fx, fy = _focus_spot(n - 1, portrait)
    ds = {i: [] for i in range(n - 1)}
    t = clear_at - GATHER_LEAD
    while t < clear_at - 1e-9:
        for r in rd.at(round(t, 4)):
            if r["i"] < n - 1:
                ds[r["i"]].append(((fx - r["cx"]) ** 2 + (fy - r["cy"]) ** 2) ** 0.5)
        t += 1 / 30
    for i, seq in ds.items():
        assert len(seq) >= 26, f"rail {i + 1}: {len(seq)} frames read across the gather"
        for k, (a, b) in enumerate(zip(seq, seq[1:])):
            assert b <= a + 0.01, f"rail {i + 1} backs AWAY from the centre card at frame {k} ({a:.1f} -> {b:.1f})"
        drew = seq[0] - seq[-1]
        assert drew > REF["rail_drift_px"] * 2, \
            f"rail {i + 1} draws in {drew:.1f}px - the reference's settled rails already drift {REF['rail_drift_px']}px"
        # the cap: GATHER_PULL of where it stood, plus the railed idle's own reach - the idle FADES OUT across the
        # same window (the wall holds its breath), so a card's measured travel carries its last drift with it
        idle_px = _dial("IDLE_DRIFT_PX", portrait) if portrait else _dial("DRIFT_X_REST")
        assert drew <= GATHER_PULL * seq[0] + 2 * idle_px, f"rail {i + 1} draws in {drew:.1f}px - past GATHER_PULL"
        assert drew < REF["station_px"], \
            f"rail {i + 1} travels {drew:.1f}px in {GATHER_LEAD}s - past the reference's own station change"


@needs_browser
def test_the_last_proof_lands_in_the_middle_and_stays_on_the_short(reader) -> None:
    _last_card_rests_at_the_centre(reader, ITEMS_AT, CLEAR_AT, True)


@needs_browser
def test_the_last_proof_lands_in_the_middle_and_stays_full_frame(reader16) -> None:
    _last_card_rests_at_the_centre(reader16, ITEMS16_AT, CLEAR16_AT, False)


@needs_browser
def test_the_wall_gathers_before_it_bursts_on_the_short(reader) -> None:
    _the_wall_only_ever_closes(reader, ITEMS_AT, CLEAR_AT, True)


@needs_browser
def test_the_wall_gathers_before_it_bursts_full_frame(reader16) -> None:
    _the_wall_only_ever_closes(reader16, ITEMS16_AT, CLEAR16_AT, False)


@needs_browser
def test_the_burst_is_tighter_than_the_reference_and_leaves_the_gathered_wall(reader) -> None:
    """E99 s59: *"the burst should be tighter"*, measured against Steel and Paper's own beat (REF above): the
    spacing, the throw's clock and the time the wall takes to leave, each inside a named tolerance of the target
    this slice set - and the departure points are the GATHERED ones, closer together than the rails they came from.
    """
    assert STAGGER == 0.035 and BURST_S == 0.42, "the tightened dials moved without this test being re-read"
    assert STAGGER <= 0.6 * REF["stagger"] and BURST_S <= 0.9 * REF["burst_s"]
    n = len(ITEMS_AT)
    # the whole wall is gone within the tightened envelope - and well inside the reference's measured 0.99 s
    gone = (n - 1) * STAGGER + BURST_S
    assert abs(gone - 0.70) <= 0.02, f"the wall clears in {gone:.3f}s, not the 0.70s this slice set"
    assert gone <= 0.75 * REF["gone_after"], f"{gone:.3f}s is not tighter than the reference's {REF['gone_after']}s"
    last = [r for r in reader.at(round(CLEAR_AT + gone + 0.02, 3)) if r["op"] > 0.05]
    assert not last, f"{len(last)} cards still on the stage {gone + 0.02:.2f}s after the clear"
    # the departure points: every rail stands closer to the centre card than its own rail spot did
    rest = {r["i"]: r for r in reader.at(CLEAR_AT - 0.01)}
    railed = {r["i"]: r for r in reader.at(CLEAR_AT - GATHER_LEAD - 0.01)}
    fx, fy = _focus_spot(n - 1, True)
    closer = [((railed[i]["cx"] - fx) ** 2 + (railed[i]["cy"] - fy) ** 2) ** 0.5
              - ((rest[i]["cx"] - fx) ** 2 + (rest[i]["cy"] - fy) ** 2) ** 0.5 for i in range(n - 1)]
    assert min(closer) > 20, f"the wall barely closed before the burst: {[round(c) for c in closer]}"
    # and nothing SNAPS when the throw takes over: the first burst frame is the gathered pose
    before = {r["i"]: r for r in reader.at(CLEAR_AT - 0.001)}
    after = {r["i"]: r for r in reader.at(CLEAR_AT)}
    for i in range(n):
        jump = max(abs(after[i]["cx"] - before[i]["cx"]), abs(after[i]["cy"] - before[i]["cy"]))
        assert jump <= 2.0, f"card {i} jumps {jump:.1f}px into the burst - the throw left from the rail, not the wall"


@needs_browser
def test_two_seeks_to_one_instant_give_one_frame(reader) -> None:
    """A pose is a pure function of t: the enter, the idle, the drift and the burst read the clock and nothing else."""
    for t in (T_ENTER, T_FOCUS, T_MOSAIC, T_IDLE, T_BURST):
        reader.at(5.0)
        forward = reader.at(t)
        reader.at(20.0)
        assert reader.at(t) == forward, f"two seeks to {t}s gave two frames"
