"""R26-20's other half (E99 s87) - THE STAMP ARRIVAL, measured ON THE RENDERED FRAME.

The ruling: *"THE STAMP is remotion-ui RU-2's: a verdict arriving with WEIGHT - a clamped scale spring landing
while a free trailing ROTATION spring is still unwinding - and a prop arrives BY it"*, with the impact ring on
split shock curves, the exit E50 owes a landed mark, and OUR look. The operator, an hour later, on what it may
carry: *"sometimes we can stamp a card; the object the stamp carries should be up to us, but for props, it doesnt
make sense to put them in a card, the whole point of a prop is for it to get added to the world; we would either
stamp it or throw it on."*

`kinetics/stopaction-stamp.test.mjs` pins the ported MATH against the source's own lines. This file measures what
reached the FRAME, on the committed golden's own page, through the served player:

  (a) THE OFFSET      at one instant: the scale spring settled (exactly 1) while the mark is still turning, with
                      both numbers read off the element's own transform matrix - not off the module.
  (b) THE RING        its radius at two instants, showing the expansion to twice the mark's own radius, and that
                      it is drawn at all (the failure the source names is "an impact ring nobody sees").
  (c) THE LANDED BOX  inside the page's own room (E65), 0 px over the page's ink and over its tags.

and three boundaries: the vector map's `stamp` SPECIES is untouched, a prop is BARE, and the exit is owed.
"""
from __future__ import annotations

import contextlib
import json
import math
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

SURFACE = "prop-stamp"
ENTER = 10.0            # the contact (build_golden_sources.PROP_STAMP_ENTER)
T_LAND = 10.17          # the instant the golden pair is judged at (the scrub's step is 0.01, so this IS the frame a t of 10.1667 renders)
T_EARLY = 10.04         # one frame in, the mark still coming down and the ring just thrown
T_LATE = 10.20          # ... and the ring at the end of its expansion
T_WIDEST = 10.46        # the last drawn frame of the ring (its life is 0.4667 s, the scrub steps 0.01): the ring at its WIDEST
T_REST = 11.30          # 1.30 s after the contact, past the rotation spring's own rest
T_EXIT = 26.40          # 0.4 s into the owed exit


# ---- the grammar, and the boundary the ruling drew --------------------------------------------


def test_stamp_is_an_arrival_and_the_vector_maps_stamp_is_a_species_and_they_never_meet():
    """E99 s87 (4): *"the vector map's `stamp` species keeps its name where it is - the arrival is an `arrive:`
    value, so the two never collide."* Both words exist; they live in two registries with nothing in common."""
    assert "stamp" in B.ARRIVALS, "the arrival"
    assert B.SPECIES_STAMP == "stamp" and B.SPECIES_STAMP in B.VECMAP_SPECIES, "the vector map's species, untouched"
    assert B.SPECIES_STAMP in B.SPECIES_KINDS
    # ONE WORD, TWO REGISTRIES. They are read off different keys of different objects - a DOCK's `arrive`, a
    # SPECIES entry's `kind` - and neither door accepts the other's value:
    assert set(B.ARRIVALS) & set(B.SPECIES_KINDS) == {"stamp"}, "the word is the only thing they share"
    assert "arrive" in B.DOCK_OPTS and "kind" not in B.DOCK_OPTS
    with pytest.raises(ValueError, match="is not one of spring.throw.land.stamp"):
        B.dock_opts({"arrive": "light"})       # a vector map species kind is not an arrival
    assert "light" in B.VECMAP_SPECIES
    # ... and the ENGINE keeps them apart too: the arrival's dials are `STAMP_ARRIVAL` because the vector map's
    # species dials already own `STAMP` in the engine's one inlined name space (species/vecmap.mjs:60)
    eng = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")
    assert eng.count("const STAMP_ARRIVAL = Object.freeze({") == 1
    assert eng.count("const STAMP = Object.freeze({") == 1


def test_the_vector_maps_stamp_species_is_still_refused_outside_its_own_world():
    """The species' own law (`build_scene_timeline_f.py:326`, the brief's :319-320 before this row's additive lines, "the three species of the VECTOR MAP world, and
    of no other world") is exactly as it was - adding an arrival of the same name loosened nothing."""
    errs = B.validate_species([{"kind": "stamp", "at": 4.0, "dur": 1.0, "text": "1996"}],
                              B.KEN, "ledger:ev-x:line", pivot_span=None)
    assert errs, "a `stamp` species on a ledger page is still refused"
    assert any("vector map" in e.lower() or "vecmap" in e.lower() or "world" in e.lower() for e in errs), errs


def test_a_stamped_dock_compiles_and_names_neither_a_species_nor_a_card():
    opts = B.dock_opts({"prop": True, "arrive": "stamp", "mass": "ink", "ink": "page"})
    entry = B.dock_entry("ev-p", 0, 1.0, 5.0, 0, B.DOCK_KIND_PROP, {"x": 1, "y": 2, "w": 3, "h": 4},
                         opts["arrive"], opts["mass"], prop=True, ink=opts["ink"])
    assert entry["arrive"] == "stamp" and entry["kind"] == B.DOCK_KIND_PROP and entry["ink"] == "page"
    assert entry["badge_at"] == [], "a prop carries no badges - the rail is a document's"


def test_a_bare_prop_is_STAMPED_ON_or_THROWN_ON_and_the_two_differ_only_in_the_arrival():
    """The operator: *"we would either stamp it or throw it on."* The bareness is the payload's (the dock's `kind`,
    read by the engine's `dockIsBare`), never the arrival's, so a thrown prop is the existing throw minus the card."""
    stamped = B.dock_opts({"prop": True, "arrive": "stamp", "mass": "ink"})
    thrown = B.dock_opts({"prop": True, "arrive": "throw", "mass": "paper"})
    a = B.dock_entry("ev-p", 0, 1.0, 5.0, 0, B.DOCK_KIND_PROP, None, stamped["arrive"], stamped["mass"], prop=True)
    b = B.dock_entry("ev-p", 0, 1.0, 5.0, 0, B.DOCK_KIND_PROP, None, thrown["arrive"], thrown["mass"], prop=True)
    assert a["kind"] == b["kind"] == B.DOCK_KIND_PROP
    assert {k for k in a if a[k] != b.get(k)} == {"arrive", "mass"}
    eng = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")
    assert 'el.style.boxShadow = dockIsBare(d.slide) ? "none"' in eng, "no card's lift, whatever the arrival"
    assert 'dockEl.classList.toggle("cutout", dockIsBare(aid))' in eng, "the chrome stands down, whatever the arrival"
    # and a CARD may still be stamped: the arrival does not require a prop
    assert B.dock_opts({"arrive": "stamp"}) == {"arrive": "stamp"}

def test_the_ink_dial_is_a_props_option_and_both_values_render():
    assert B.DOCK_INKS == ("own", "page")
    assert {"prop-stamp", "prop-stamp-ink"} <= set(G.SURFACES), "both are committed surfaces"
    own = G.SURFACES["prop-stamp"]()[0]["scenes"][0]["docks"][0]
    page = G.SURFACES["prop-stamp-ink"]()[0]["scenes"][0]["docks"][0]
    assert own["ink"] == "own" and page["ink"] == "page"
    assert {k: v for k, v in own.items() if k != "ink"} == {k: v for k, v in page.items() if k != "ink"}, \
        "one key of difference between the pair, so the operator's comparison is a clean one"


def test_an_ink_dial_without_a_prop_and_an_unknown_ink_are_both_refused_by_name():
    with pytest.raises(ValueError, match="ink is a PROP's option"):
        B.dock_opts({"ink": "page"})
    with pytest.raises(ValueError, match="ink must be own|page"):
        B.dock_opts({"prop": True, "ink": "charcoal"})


def test_a_prop_is_never_a_card_a_press_card_or_a_picture_on_a_surface():
    for other, value in (("press", True), ("stack", True), ("cutout", True), ("fit", B.EMBED_FITS[0])):
        with pytest.raises(ValueError, match=f"prop and {other} cannot be combined"):
            B.dock_opts({"prop": True, other: value})


# ---- the frame --------------------------------------------------------------------------------


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
  const sb = document.getElementById('stage').getBoundingClientRect();
  const bb = (e) => { if (!e) return null; const r = e.getBoundingClientRect();
    return { x: r.left - sb.left, y: r.top - sb.top, w: r.width, h: r.height }; };
  const dock = document.querySelector('.dock[data-slide]');
  const ring = document.querySelector('.dock-ring');
  const img = dock ? dock.querySelector('.slide-frame img') : null;
  const cd = dock ? getComputedStyle(dock) : null;
  const ink = [];
  const world = document.querySelector('.world.ledger') || document.querySelector('.world');
  world.querySelectorAll('svg path.ser, svg text.sname, svg text, svg path').forEach((e) => {
    const r = e.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    if (getComputedStyle(e).visibility === 'hidden' || +getComputedStyle(e).opacity === 0) return;
    const cls = e.getAttribute('class') || '';
    if (!['ser', 'sname', 'lab'].includes(cls)) return;      // the marks, the series' end names, the tick and basis labels
    if (cls === 'ser') {   // a LINE is its points (every 3 px of its length, in stage px, with its own stroke), never its bbox
      const L = e.getTotalLength(), m = e.getScreenCTM(), sw = parseFloat(getComputedStyle(e).strokeWidth) || 2;
      const k = Math.hypot(m.a, m.b), pts = [];
      for (let s = 0; s <= L; s += 3) { const q = e.getPointAtLength(s);
        pts.push([m.a * q.x + m.c * q.y + m.e - sb.left, m.b * q.x + m.d * q.y + m.f - sb.top]); }
      ink.push({ cls, text: '', box: bb(e), pts, half: sw * k / 2 });
      return;
    }
    ink.push({ cls, text: (e.textContent || '').slice(0, 24), box: bb(e) });
  });
  const words = [...document.querySelectorAll('.world .lp-title, .world .lp-sub, .world .lp-src')]
    .filter((e) => e.getBoundingClientRect().width > 1 && +getComputedStyle(e).opacity > 0)
    .map((e) => ({ cls: e.className, text: (e.textContent || '').slice(0, 24), box: bb(e) }));
  return {
    words,
    dock: dock ? { box: bb(dock), layout: { x: dock.offsetLeft, y: dock.offsetTop, w: dock.offsetWidth, h: dock.offsetHeight },
                   transform: dock.style.transform, matrix: cd.transform,
                   opacity: +dock.style.opacity, origin: cd.transformOrigin, shadow: dock.style.boxShadow,
                   cls: dock.className, border: cd.borderTopWidth, bg: cd.backgroundColor,
                   pad: cd.paddingTop, blur: cd.backdropFilter } : null,
    frame: (() => { const f = dock ? dock.querySelector('.slide-frame') : null; if (!f) return null;
      const c = getComputedStyle(f); return { border: c.borderTopWidth, bg: c.backgroundColor,
        radius: c.borderRadius, mask: c.maskImage }; })(),
    img: img ? { box: bb(img), filter: getComputedStyle(img).filter } : null,
    rail: (() => { const r = dock ? dock.querySelector('.rail') : null;
      return r ? getComputedStyle(r).display : null; })(),
    ring: ring ? { box: bb(ring), opacity: +ring.style.opacity, width: parseFloat(getComputedStyle(ring).borderTopWidth),
                   colour: getComputedStyle(ring).borderTopColor } : null,
    ink,
  };
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
    """One surface, served and mounted from the GOLDEN's own source, so the test and the committed frames read
    the same page (the pattern `test_agenda_page.py` uses)."""

    def __init__(self, browser, surface: str, compiled: tuple[dict, dict] | None = None):
        tl, uris, _t, aspect = RB.load_surface(surface)
        if compiled is not None:
            tl, uris = compiled
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / f"{surface}.html"
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


def _matrix(css: str) -> tuple[float, float, float, float]:
    """a, b, c, d of a CSS `matrix(...)`."""
    nums = [float(x) for x in css[css.index("(") + 1:css.index(")")].split(",")]
    return nums[0], nums[1], nums[2], nums[3]


def _scale_and_deg(css: str) -> tuple[float, float]:
    """The uniform scale and the turn, in degrees, that a 2x2 CSS matrix carries. The scale is sqrt|det| - the
    squash tensor is area-preserving (det 1), so the hit's squash frame does not disturb it."""
    a, b, c, d = _matrix(css)
    return math.sqrt(abs(a * d - b * c)), math.degrees(math.atan2(b, a))


def _painted(dock: dict, box: dict | None = None) -> tuple[float, float, float]:
    """(painted centre x, y, painted half-diagonal) of a stamp entry, on `box` (the landed layout) or its place."""
    b = box or dock["place"]
    p0, p1, p2, p3 = dock.get("paint") or (0, 0, 1, 1)
    return (b["x"] + b["w"] * (p0 + p2) / 2, b["y"] + b["h"] * (p1 + p3) / 2,
            0.5 * math.hypot(b["w"] * (p2 - p0), b["h"] * (p3 - p1)))


def _disc_hits(ring_box: dict, e: dict) -> float:
    """How much of `e` the RING touches. Over its life the ring's stroke sweeps every radius out to its widest, so what
    it must not touch is the whole DISC of its widest radius (the engine draws a border-box circle: its stroke is
    inside `w / 2`). A line is its sampled points (with half its stroke); a word is its box, touched when the box's
    nearest point is within the radius. The disc, not its bounding square: the square's corners are page it never
    reaches - the compiler fits the same disc (`disc_clearance`)."""
    cx, cy, r = ring_box["x"] + ring_box["w"] / 2, ring_box["y"] + ring_box["h"] / 2, ring_box["w"] / 2
    if e.get("pts") is not None:
        hw = e.get("half", 1.0)
        return float(sum(1 for (px, py) in e["pts"] if math.hypot(px - cx, py - cy) <= r + hw))
    b = e["box"]
    dx = max(b["x"] - cx, 0.0, cx - (b["x"] + b["w"]))
    dy = max(b["y"] - cy, 0.0, cy - (b["y"] + b["h"]))
    return 1.0 if math.hypot(dx, dy) < r else 0.0


def _hits(box: dict, e: dict) -> float:
    """How much of `e` is inside `box`: a word's box overlap in px^2, or for a LINE the number of its sampled points
    (inflated by half its drawn stroke) that fall inside - a polyline's client rect is most of the plot and would
    'overlap' every box in it."""
    if e.get("pts") is not None:
        hw = e.get("half", 1.0)
        return float(sum(1 for (px, py) in e["pts"]
                         if box["x"] - hw <= px <= box["x"] + box["w"] + hw and box["y"] - hw <= py <= box["y"] + box["h"] + hw))
    return _overlap(box, e["box"])


def _overlap(p: dict, q: dict) -> float:
    return (max(0.0, min(p["x"] + p["w"], q["x"] + q["w"]) - max(p["x"], q["x"]))
            * max(0.0, min(p["y"] + p["h"], q["y"] + q["h"]) - max(p["y"], q["y"])))


def _row_timeline() -> tuple[dict, dict, dict]:
    """The committed surface's page and assets with its dock REPLACED by the one the loop's own door compiles."""
    tl, uris, _t, _a = RB.load_surface(SURFACE)
    tl = json.loads(json.dumps(tl))
    dock = _loop_dock(tl["scenes"][0]["world"], {"prop": True, "arrive": "stamp", "mass": "ink", "ink": "own"})
    tl["scenes"][0]["docks"] = [dock]
    return tl, uris, dock


@pytest.fixture(scope="module")
def frames():
    """Every instant this file measures, read through ONE browser: the `own` surface at six instants, the `page`-ink
    surface at its rest, and the ROW - the loop's own door compiled fresh - at the same six. (One browser because a
    second `sync_playwright()` in the same thread meets a loop that is already running.)"""
    tl, uris, dock = _row_timeline()
    with _browser() as br:
        own, inked = _Player(br, SURFACE), _Player(br, "prop-stamp-ink")
        row = _Player(br, SURFACE, (tl, uris))
        try:
            ts = (T_EARLY, T_LAND, T_LATE, T_WIDEST, T_REST, T_EXIT)
            out = {t: own.at(t) for t in ts}
            out["ink:" + str(T_REST)] = inked.at(T_REST)
            out["row"] = {t: row.at(t) for t in ts}
            out["row_dock"] = dock
            for pl in (own, inked, row):
                assert not pl.errors, pl.errors
            yield out
        finally:
            own.close(); inked.close(); row.close()


@needs_browser
def test_a_the_scale_spring_is_SETTLED_while_the_rotation_is_still_OFF_AXIS(frames):
    """(a) THE OFFSET, on the frame: at 10.17 the mark's transform matrix carries a scale of exactly 1.0000
    and a turn of -5.61 deg - 3.39 deg short of the -9.00 deg it lands at. The two numbers at ONE instant are
    what the single-spring landing cannot produce: `landXf` has one clock, so it is either moving or done."""
    scale, deg = _scale_and_deg(frames[T_LAND]["dock"]["matrix"])
    assert abs(scale - 1.0) < 1e-3, f"the scale spring has settled: {scale:.6f}"
    assert abs(deg - (-5.606)) < 0.05, f"... and the mark is still turning: {deg:.3f} deg"
    rest_scale, rest_deg = _scale_and_deg(frames[T_REST]["dock"]["matrix"])
    assert abs(rest_scale - 1.0) < 1e-3
    assert abs(rest_deg - (-8.99)) < 0.05, f"it comes to rest OFF-SQUARE at {rest_deg:.3f} deg"
    assert abs(deg - rest_deg) > 3.0, "the offset is 3.38 deg of turn still owed when the scale is already done"
    # and the arrival is still oversized one frame after the contact - it comes DOWN onto the page
    early, _ = _scale_and_deg(frames[T_EARLY]["dock"]["matrix"])
    from_to = RB.load_surface(SURFACE)[0]["scenes"][0]["docks"][0]["from_to"]
    assert B.STAMP_APPROACH_MIN <= from_to and 1.0 < early <= from_to, f"one frame in it is still coming down from {from_to}x: scale {early:.4f}"


@needs_browser
def test_b_the_impact_ring_is_DRAWN_and_expands_to_twice_the_marks_radius(frames):
    """(b) THE RING, on the frame - the failure the source names is one nobody sees, so this measures that it is
    painted (a width, an opacity, a colour) and that its radius doubles between two instants."""
    early, late = frames[T_EARLY]["ring"], frames[T_LATE]["ring"]
    for r, when in ((early, "0.04 s"), (late, "0.20 s")):
        assert r is not None, f"no ring at {when}"
        assert r["width"] > 2.0, f"the ring is painted at {when}: {r['width']:.2f} px of stroke"
        assert r["opacity"] > 0.25, f"... and visible at {when}: opacity {r['opacity']:.3f}"
        assert r["colour"] not in ("rgba(0, 0, 0, 0)", "transparent"), f"... in our ink at {when}: {r['colour']}"
    assert early["colour"] == "rgb(242, 242, 242)", "chalk on the charcoal page - never a gold ring"
    assert frames[T_WIDEST]["ring"]["opacity"] > 0, "the widest frame is a DRAWN frame"
    # THE RING HUGS THE MARK (the operator's round): its base radius is the mark's PAINTED half-diagonal, and its
    # peak is whatever the room leaves between a floor just outside that edge and the source's 2x
    dock = RB.load_surface(SURFACE)[0]["scenes"][0]["docks"][0]
    _cx, _cy, r0 = _painted(dock)   # off the PLACE, exactly as the engine takes it (Wd = place w, Hd = w * place h / w)
    r_early, r_late = early["box"]["w"] / 2, late["box"]["w"] / 2
    cap = dock["ring_to"]
    assert (r0 + B.STAMP_RING_GAP_PX) / r0 - 1e-3 <= cap <= B.STAMP_RING_TO, f"the ring's peak {cap}x sits between its floor and 2x"
    # the source's eased expansion k(life) at 0.04 s and 0.20 s is 0.4402 and 0.9512 (stopaction-stamp.test.mjs)
    assert abs(r_early / r0 - (1 + (cap - 1) * 0.4402)) < 0.02, f"at 0.04 s the ring stands at {r_early / r0:.4f} of the painted radius ({r_early:.1f} px)"
    assert abs(r_late / r0 - (1 + (cap - 1) * 0.9512)) < 0.02, f"at 0.20 s it has reached {r_late / r0:.4f} ({r_late:.1f} px)"
    assert r_late > r_early, "it expands"
    widest = frames[T_WIDEST]["ring"]["box"]["w"] / 2
    assert widest / r0 <= cap + 1e-3, f"at its widest it reaches {widest / r0:.4f} - the cap, never past it"
    assert widest >= r0 + B.STAMP_RING_GAP_PX - 0.5, f"and it stands OUTSIDE the painted edge: {widest:.1f} vs {r0:.1f} + {B.STAMP_RING_GAP_PX}"
    # SPLIT curves: the life is linear while the radius is eased, so the ring is thinner and fainter as it grows
    assert late["width"] < early["width"] and late["opacity"] < early["opacity"]
    assert frames[T_REST]["ring"]["opacity"] == 0, "an impact ring is never held (E56 stays the annotation ring's law)"


@needs_browser
def test_c_the_landed_box_is_in_the_pages_own_room_with_0_px_over_the_ink_and_the_tags(frames):
    """(c) THE PLACEMENT, on the frame: the mark stands inside the room the compiler's own `free_bands` cut for
    it (E65) and covers neither a series' marks nor its end names."""
    box, hull = frames[T_REST]["dock"]["layout"], frames[T_REST]["dock"]["box"]
    tl, _u, _t, _a = RB.load_surface(SURFACE)
    place = tl["scenes"][0]["docks"][0]["place"]
    assert tl["scenes"][0]["docks"][0]["place_room"] == "empty", "E65's EMPTY room - the plot's own clear rectangle"
    for k in ("x", "y", "w", "h"):
        assert abs(box[k] - place[k]) < 1.5, f"the landed box IS the placed box in {k}: {box[k]:.1f} vs {place[k]}"
    world = G.SURFACES[SURFACE]()[0]["scenes"][0]["world"]
    plot = LPG.page_boxes(world["page"], "16:9")["plot"]
    cx, cy, _r = _painted(tl["scenes"][0]["docks"][0], box)
    assert plot["x"] <= cx <= plot["x"] + plot["w"] and plot["y"] <= cy <= plot["y"] + plot["h"], \
        f"the mark's painted centre is inside the plot's own empty area: ({cx}, {cy})"
    ink = frames[T_REST]["ink"] + frames[T_REST]["words"]
    assert len(ink) >= 8, f"the page's own marks and end names were found: {len(ink)}"
    over = [(e["cls"], e["text"], round(_hits(hull, e), 1)) for e in ink if _hits(hull, e) > 0]
    assert over == [], f"0 px over the page's ink and tags, and it is over: {over}"
    assert [e for e in ink if e["cls"] == "sname"], "the tags are drawn on this page - the check is not vacuous"


@needs_browser
def test_a_prop_lands_BARE_with_no_card_no_frame_no_shadow_and_no_foot_mask(frames):
    """*"the whole point of a prop is for it to get added to the world"*: the card's chrome stands down, and the
    CUTOUT's foot dissolve - a bust's cue - stands down with it, because it would fade the base off a building."""
    d, f = frames[T_REST]["dock"], frames[T_REST]["frame"]
    assert d["shadow"] == "none", "no card's lift"
    assert d["border"] == "0px" and d["pad"] == "0px", "no border, no padding"
    assert d["bg"] in ("rgba(0, 0, 0, 0)", "transparent"), "no paper"
    assert d["blur"] == "none", "no backdrop blur - that is the paper's own depth cue"
    assert f["border"] == "0px" and f["radius"] == "0px", "the document's white frame stands down too"
    assert f["bg"] in ("rgba(0, 0, 0, 0)", "transparent"), "... and its white ground"
    assert frames[T_REST]["rail"] in (None, "none"), "a prop carries no badge rail"
    assert frames[T_REST]["img"]["box"]["h"] > 1, "the picture is mounted"
    # the cutout's foot mask is undone for a prop
    assert d["cls"].split().count("cutout") == 1, "it rides the cutout's chrome-down class"


@needs_browser
def test_the_mark_turns_about_its_OWN_CENTRE_not_about_the_ground_contact(frames):
    """badge-stamp.tsx:166 pivots at the seal's centre; the template's `.dock.arriving` pivots at 50% 100%, which
    is a falling card's cue. A stamp overrides it, or the mark would swing about its foot."""
    box_at_rest = frames[T_REST]["dock"]["layout"]
    ox, oy = (float(v.replace("px", "")) for v in frames[T_REST]["dock"]["origin"].split()[:2])
    p0, p1, p2, p3 = RB.load_surface(SURFACE)[0]["scenes"][0]["docks"][0]["paint"]
    assert abs(ox - box_at_rest["w"] * (p0 + p2) / 2) < 1.0, f"the pivot is the mark's PAINTED centre across: {ox}"
    assert abs(oy - box_at_rest["h"] * (p1 + p3) / 2) < 1.0, f"... and down: {oy}"


@needs_browser
def test_the_landed_mark_OWES_AN_EXIT_and_leaves_on_the_sources_own_curve(frames):
    """E50 through the source's `exitAtInFrames`: 0.4 s into a 0.5333 s ease-IN cubic the mark is at 0.578 of
    its opacity and has not moved - it leaves by its own curve, not by the dock's spring retract."""
    held, leaving = frames[T_REST]["dock"], frames[T_EXIT]["dock"]
    assert held["opacity"] == 1.0, "it holds at full ink until it is told to leave"
    assert abs(leaving["opacity"] - 0.578) < 0.01, f"and leaves on the cubic: {leaving['opacity']:.3f}"
    _s, deg = _scale_and_deg(leaving["matrix"])
    assert abs(deg - (-9.0)) < 0.05, "still off-square as it goes"
    assert abs(leaving["box"]["x"] - held["box"]["x"]) < 1.0, "an exit is not a retract: the mark does not move"


@needs_browser
def test_the_INK_dial_changes_the_picture_and_nothing_else(frames):
    """The operator's open question, both ways on the frame: `page` puts a filter on the PICTURE (and only on it)
    and `own` puts none. Every other measurement above is taken on the `own` surface."""
    own, inked = frames[T_REST], frames["ink:" + str(T_REST)]
    assert own["img"]["filter"] == "none", "the woodblock in its own colour is untouched"
    assert inked["img"]["filter"] != "none", f"the art is laid down in the page's ink: {inked['img']['filter']}"
    assert "invert" in inked["img"]["filter"], "on the charcoal page the impression is in its chalk"
    assert "grayscale" in inked["img"]["filter"], "one ink, as an impression has"
    # ... and nothing else moves: the same pose, the same box, the same arrival
    assert inked["dock"]["matrix"] == own["dock"]["matrix"], "the ink dial is not a motion"
    assert inked["dock"]["layout"] == own["dock"]["layout"], "... and not a placement"


@needs_browser
def test_the_RING_at_its_widest_crosses_none_of_the_page(frames):
    """R26-20 send-back (R26-191): the first cut's ring ran through the "+613% MEMORY MAKERS" end name while the mark
    sat clear of it - (c) had measured the mark alone. At the ring's WIDEST drawn frame its whole box (the stroke is
    inside it: the engine draws a border-box circle) overlaps 0 px of the chart's marks, the four end names, the
    title, the sub and the citation, and it lies whole inside the stage (capped, never clipped)."""
    ring = frames[T_WIDEST]["ring"]
    assert ring and ring["opacity"] > 0
    box = ring["box"]
    things = frames[T_WIDEST]["ink"] + frames[T_WIDEST]["words"]
    kinds = {c for e in things for c in e["cls"].split()}
    assert {"ser", "sname", "lab", "lp-title", "lp-sub", "lp-src"} <= kinds, f"every kind of page ink was found: {kinds}"
    over = [(e["cls"], e["text"], round(_disc_hits(box, e), 1)) for e in things if _disc_hits(box, e) > 0]
    assert over == [], f"0 px of ring over the page, and it is over: {over}"
    assert box["x"] >= 0 and box["y"] >= 0 and box["x"] + box["w"] <= 1920 and box["y"] + box["h"] <= 1080, box


# ---- the compiler's fit (the door the H rows go through) ------------------------------------------

STAGE = {"x": 0, "y": 0, "w": 1920, "h": 1080}


def test_the_compilers_ring_dials_are_the_modules():
    src = (ROOT / "content/video_engine/scripts/kinetics/stopaction.mjs").read_text(encoding="utf-8")
    assert f"RING_TO: {B.STAMP_RING_TO}," in src and f"RING_W_PX: {B.STAMP_RING_W_PX}," in src


FED = None


def _fed() -> dict:
    global FED
    FED = FED or B.painted_box(G.PROP_CUTOUT)
    return dict(FED)


def test_the_Feds_PAINTED_box_is_measured_off_its_alpha_and_the_cutouts_are_trimmed():
    """The operator's round measures the mark by its painted pixels. The Fed cutout: canvas 282 x 259, painted (alpha
    > 8) 280 x 257 at (1, 1) - every one of the 24 cutouts is trimmed to its alpha box with a 1 px margin, so the Fed
    'reading small' was the fit's priority, never padding. The mechanism still measures it, for the cutout that has."""
    fed = _fed()
    assert fed["canvas"] == [282, 259] and fed["painted"] == [280, 257]
    assert abs(fed["x0"] - 1 / 282) < 1e-9 and abs(fed["y1"] - 258 / 259) < 1e-9


def test_a_room_that_holds_the_full_ring_is_not_capped():
    room = {"x": 400, "y": 200, "w": 900, "h": 600}
    fit = B.stamp_dock_place({"asset_id": "plate-plain"}, "16:9", {"prop": True, "arrive": "stamp", "centre_w": 0.1},
                             _fed(), room, None, "t")
    assert fit["ring_to"] == 2.0 and fit["ring_capped"] is False and fit["from_to"] == 2.1, fit["why"]


def test_THE_MARK_TAKES_THE_ROOM_the_largest_mark_that_fits_and_a_larger_one_collides():
    """The operator: *"Use the space."* The mark is sized FIRST - the largest painted mark the place holds with its
    turned hull (at its least approach) and its ring's floor clear - and a mark 2 % larger at the same centre
    collides. On the golden's page that is 206 x 190 painted px, where the ring-first fit gave 134 x 123."""
    world = G.SURFACES[SURFACE]()[0]["scenes"][0]["world"]
    fit = B.stamp_dock_place(world, "16:9", {"prop": True, "arrive": "stamp"}, _fed(), None, None, "t")
    obs, bounds = B.ring_obstacles(world["page"], "16:9")
    (cx, cy), (pw, ph) = fit["centre"], fit["painted"]
    assert B._stamp_scale(cx, cy, pw, ph, obs, bounds) >= 1.0, "the mark it wrote fits"
    assert B._stamp_scale(cx, cy, pw * 1.02, ph * 1.02, obs, bounds) < 1.0, "and a mark 2 % larger at the same centre does not"
    assert pw > 134 * 1.4, f"it takes the room: {pw:.0f} px painted, against the 134 px the ring-first fit left"


def test_the_RING_HUGS_THE_MARK_and_no_floor_can_refuse_it():
    """The 1.6x floor and the mark-shrink step are DELETED: the ring's floor is just outside the painted edge and is
    reserved when the mark is sized, so across rooms of every size the ring is never refused - only a room too small
    for the MARK is."""
    assert not hasattr(B, "STAMP_RING_FLOOR") and not hasattr(B, "stamp_ring_fit"), "the ring-first API is gone"
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    assert "so the floor fits" not in src, "no mark-shrink step remains"
    for w, h in ((300, 260), (500, 300), (900, 700), (1600, 800)):
        fit = B.stamp_dock_place({"asset_id": "plate-plain"}, "16:9", {"prop": True, "arrive": "stamp"}, _fed(),
                                 {"x": 100, "y": 70, "w": w, "h": h}, None, "t")
        assert fit["ring_to"] >= fit["ring_floor"] > 1.0, (w, h, fit["why"])
        assert fit["ring_floor"] * 0.5 * math.hypot(*fit["painted"]) >= 0.5 * math.hypot(*fit["painted"]) + B.STAMP_RING_GAP_PX - 0.1   # floored to 4 places (L3)
    with pytest.raises(ValueError, match="under the 120 px mark floor"):
        B.stamp_dock_place({"asset_id": "plate-plain"}, "16:9", {"prop": True, "arrive": "stamp"}, _fed(),
                           {"x": 800, "y": 400, "w": 40, "h": 40}, [{"x": 700, "y": 520, "w": 400, "h": 20}], "t")


def test_a_mark_whose_centre_is_ON_the_ink_is_refused():
    with pytest.raises(ValueError, match="mark floor"):
        B.stamp_dock_place({"asset_id": "plate-plain"}, "16:9", {"prop": True, "arrive": "stamp", "centre_x": 0.5, "centre_y": 0.5},
                           _fed(), None, [{"x": 900, "y": 500, "w": 120, "h": 80}], "t")


def test_the_title_and_the_sub_ARE_obstacles_for_a_ring_though_a_card_may_park_over_them():
    page = G.SURFACES[SURFACE]()[0]["scenes"][0]["world"]["page"]
    obs, bounds = B.ring_obstacles(page, "16:9")
    boxes = LPG.page_boxes(page, "16:9")
    for k in ("title", "sub", "source"):
        assert boxes[k] in obs, k
    assert bounds == boxes["safe"]
    assert any(o["w"] < boxes["plot"]["w"] for o in obs), "the plot is taken cell by cell, not whole"


def test_the_row_loop_calls_ONE_door_for_every_stamp_before_the_slot_rule():
    """The loop's own call site, pinned by position: every `arrive: stamp` dock goes through `stamp_dock_place`
    BEFORE `eplace` is decided, whatever its slot, and the fit is the entry's `centre` / `ring_to` / `from_to`."""
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    body = src[src.index("        place = dock_place(world, ASPECT"):]
    body = body[:body.index("assign_press_stack(docks)")]
    i_fit = body.index('if dopt.get("arrive") == "stamp":')
    i_call = body.index("stamp_fit = stamp_dock_place(world, ASPECT, dopt, _paint, plate_room, newsreel_boxes(row_species, ASPECT),")
    i_slot = body.index("eplace = dplace if (slot == 0 or centred")
    assert i_fit < i_call < i_slot, "fitted before the slot rule, so slot 1 is fitted too"
    assert 'dplace, centred = {k: stamp_fit[k] for k in ("x", "y", "w", "h", "room")}, True' in body
    assert 'raise SystemExit(f"FAIL: {exc}") from exc' in body[i_fit:i_slot], "a refusal fails the row by number"
    assert "rplace = None if stamp_fit else" in body, "a stamp never gets a reading box"
    assert B.dock_entry("a", 0, 1, 5, 0, arrive="stamp", ring_to=1.6)["ring_to"] == 1.6
    assert "ring_to" not in B.dock_entry("a", 0, 1, 5, 0, arrive="throw", ring_to=1.6)
    eng = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")
    assert "RING_TO: +d.ring_to" in eng and "FROM: +d.from_to" in eng, "the engine draws the fitted peaks, never its own"


def _loop_dock(world: dict, opts: dict, slot: int = 0, plate_room: dict | None = None) -> dict:
    """ONE STAMP ROW, the way the row loop compiles it (build_scene_timeline_f.py main(), the dock pass): the row's
    options through `dock_opts`, the PAINTED box off the dock's own asset (`painted_box`), `stamp_dock_place` with
    the scene's plate room and newsreel reserve, then `dock_entry` with `centred` True and the fitted peaks. No hand
    box, no hand-clipped room, no `extra`."""
    dopt = B.dock_opts(opts)
    fit = B.stamp_dock_place(world, "16:9", dopt, B.painted_box(G.PROP_CUTOUT) if dopt.get("prop") else B.painted_box(None, dopt.get("card_aspect")),
                             plate_room, B.newsreel_boxes([], "16:9"), "shot row 1 (0-30s) dock ev-prop-fed")
    place = {k: fit[k] for k in ("x", "y", "w", "h", "room")}
    return B.dock_entry("ev-prop-fed", slot, 10.0, 26.0, 0, B.DOCK_KIND_PROP if dopt.get("prop") else B.DOCK_KIND_IMAGE,
                        place, dopt.get("arrive"), dopt.get("mass"), True, prop=bool(dopt.get("prop")),
                        ink=dopt.get("ink"), ring_to=fit["ring_to"], from_to=fit["from_to"], paint=fit["paint"])


def _golden_page(full_stage: bool) -> dict:
    page = LPG.build_spec(LPG.load_series(G.SERIES), "line", 0, "right")
    if full_stage:   # ASPECT pinned: `stamp_full_stage` reads the compiler's module global, which an earlier 9:16
        _aspect, B.ASPECT = B.ASPECT, "16:9"   # compile in the same process leaves set (the golden builder's same pin)
        try:
            page = B.stamp_full_stage(page)
        finally:
            B.ASPECT = _aspect
    return {"kind": "ledger", "page": page}


def test_THE_REVIEWERS_CASE_a_page_that_hides_its_end_names_is_refused_by_name_never_fitted_blind():
    """H1 (a): the golden's own page as the reviewer ran it - not full-stage, so it reports no `tags` box while
    it writes four end names. The first two cuts fitted it silently ({1251, 369, 347, 205}, a 322 px ring through
    all four names). Now the row fails, and says why."""
    with pytest.raises(ValueError, match=r"writes inline end names \(tag_units 696\) but reports no measured `tags` box"):
        _loop_dock(_golden_page(False), {"prop": True, "arrive": "stamp", "mass": "ink"})


def test_a_stamp_on_SLOT_ONE_with_no_centre_is_fitted_exactly_as_slot_zero():
    """H1 (c): slot 1 had no `eplace` and skipped the fit. The door is slot-agnostic and the loop takes it first."""
    a = _loop_dock(_golden_page(True), {"prop": True, "arrive": "stamp", "mass": "ink"}, slot=0)
    b = _loop_dock(_golden_page(True), {"prop": True, "arrive": "stamp", "mass": "ink"}, slot=1)
    assert {k: v for k, v in a.items() if k != "slot"} == {k: v for k, v in b.items() if k != "slot"}


def test_a_stamp_OFF_a_ledger_page_is_fitted_against_the_caption_band_and_the_safe_box_or_refused():
    """H1 (c): a plate stamp is held to the frame's own bands (the ledger page's `safe` and `caption_anchor`, the same
    on every page of an aspect - pinned here against page_boxes) or refused when it names no room at all."""
    boxes = LPG.page_boxes(_golden_page(True)["page"], "16:9")
    assert B.FRAME_BANDS["16:9"] == {"safe": boxes["safe"], "caption": boxes["caption_anchor"]}
    with pytest.raises(ValueError, match="needs the plate's `room` or the row's own centre_x / centre_y"):
        _loop_dock({"asset_id": "plate-plain"}, {"prop": True, "arrive": "stamp"})
    low = _loop_dock({"asset_id": "plate-plain"}, {"prop": True, "arrive": "stamp"},
                     plate_room={"x": 700, "y": 600, "w": 520, "h": 300})
    cap = B.FRAME_BANDS["16:9"]["caption"]
    _cx, cy, rp = _painted(low)
    assert cy + low["ring_to"] * rp + B.STAMP_RING_W_PX <= cap["y"] + 0.5, "the ring stops above the caption band"


def test_the_painted_aspect_is_the_pictures_not_a_cards():
    """H1 (d): the entry's box is the Fed cutout's own 259 / 282, so the rect the engine rings is the rect it paints."""
    d = _loop_dock(_golden_page(True), {"prop": True, "arrive": "stamp", "mass": "ink"})
    assert abs(d["place"]["h"] / d["place"]["w"] - 259 / 282) < 0.01, d["place"]
    assert d["paint"] == [round(1 / 282, 4), round(1 / 259, 4), round(281 / 282, 4), round(258 / 259, 4)], "and its PAINTED part"
    assert d["centre"] is True and "read_place" not in d, "H1 (b): one box for the whole arrival"


def test_M1_arrive_stamp_is_refused_where_no_painter_stamps():
    with pytest.raises(ValueError, match="arrive=stamp is a DOCK's arrival"):
        B.split_plate_opts("ledger:ev-divergence-v1:line;arrive=stamp;mass=ink")
    for other, value in (("embed", "poster"), ("read", {"centre_w": 0.3}), ("read_s", 1.0), ("park_s", 0.5),
                         ("centre_band", B.DOCK_BAND_ORDER[0])):
        opts = {"arrive": "stamp", other: value, **({"centre": True} if other == "read" else {})}
        with pytest.raises(ValueError, match=f"arrive=stamp and {other} cannot be combined"):
            B.dock_opts(opts)


@needs_browser
def test_A_REAL_STAMP_ROW_through_the_loops_door_lands_with_0_px_of_ring_or_mark_over_the_page(frames):
    """The reviewer's owed test: a stamp row compiled by the loop's own sequence (`_loop_dock`) on the golden's page as
    a real 16:9 build has it - full-stage, no hand clip, no `extra` - rendered through the served player, measured at
    every instant of the arrival and at the ring's widest: 0 of the ring's box (its stroke is inside it) and 0 of the
    turned mark over the chart's lines (sampled every 3 px of length with their stroke), its four end names, its tick
    and basis labels, the title, the sub and the citation."""
    reads, dock = frames["row"], frames["row_dock"]
    names = [e for e in reads[T_REST]["ink"] if e["cls"] == "sname"]
    assert len(names) == 4, f"the four end names are drawn: {[e['text'] for e in names]}"
    assert sum(len(e["pts"]) for e in reads[T_REST]["ink"] if e["cls"] == "ser") > 400, "the lines were sampled"
    for t, r in reads.items():
        things = r["ink"] + r["words"]
        shapes = [("mark", r["dock"]["box"])] + ([("ring", r["ring"]["box"])] if r["ring"] and r["ring"]["opacity"] > 0 else [])
        for what, box in shapes:
            hit = _disc_hits if what == "ring" else _hits
            over = [(e["cls"], e["text"], hit(box, e)) for e in things if hit(box, e) > 0]
            assert over == [], f"at {t} the {what} {box} is over the page: {over}"
    widest = reads[T_WIDEST]["ring"]["box"]
    _cx, _cy, r0 = _painted(dock)
    assert abs(widest["w"] / 2 / r0 - dock["ring_to"]) < 0.02, "the drawn ring IS the fitted one"
    assert widest["w"] / 2 <= dock["ring_to"] * r0 + 0.1, "and never larger (L3)"
    assert dock == RB.load_surface(SURFACE)[0]["scenes"][0]["docks"][0], \
        "and the committed golden IS this row: no hand clip, no extra - the fixture calls the same door"


def test_the_stamp_golden_is_the_same_whatever_aspect_the_process_last_compiled():
    """The full-suite-only failure (2026-09-22): `stamp_full_stage` reads the compiler's module-level ASPECT and
    `authoring.table.compile_timeline` sets it without restoring it, so a 9:16 short compiled earlier in the same
    process made the golden's page unstamped - no measured end-name box - and the stamp was REFUSED. Alone, 28/28
    passed; in the suite, five failed. The golden must be a function of its own inputs, never of process state."""
    import build_golden_sources as G   # noqa: E402
    saved = B.ASPECT
    try:
        B.ASPECT = None
        clean = G.SURFACES["prop-stamp"]()[0]["scenes"][0]["docks"][0]["place"]
        B.ASPECT = "9:16"   # what a Tokyo short's compile leaves behind
        dirty = G.SURFACES["prop-stamp"]()[0]["scenes"][0]["docks"][0]["place"]
        assert B.ASPECT == "9:16", "the builder restores what it pinned - it must not reset the process's own aspect"
    finally:
        B.ASPECT = saved
    assert dirty == clean
