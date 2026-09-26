"""P72 T21 - the named places the engine was not yet a pure function of t.

A frame reached by PLAYING (every 24 fps frame from before the moment, in one page - the way render_episode captures)
must be the frame reached by a COLD SEEK (a fresh page, one seek). Each test below plays into one named moment and
seeks it cold, and compares the two captures byte for byte:

  R26-260 + R26-21  the snap - a page that grows out of its landed card reads the card's box from the dock's declared
                    geometry, not from a layout the dock loop recorded on an earlier frame, and the snap turns about
                    the page's own origin (it wrote "0 0" whenever a card was recorded, the punch then turned about
                    the corner: the page landed (+137, +100) px off in play)
  R26-294           the dock slot - a stamped prop's pivot never outlives it in the slot: the next card in that slot
                    turns about its own origin whatever the slot held before
  R26-321           the melt - the ink clone is the page as painted at the boundary (span[0]), not the live frame
                    that happened to mount it
  R26-322           `melt:morph` - the hand ring is read off the outgoing page AFTER it has painted this frame
  R26-324           the title glow - a title whose colour changed repaints whole
  R26-376           the dock at a depth - its camera wrapper turns about the card's PLACED box, not a layout that
                    has not decoded yet

R26-325 (row 12, H 333.42) was DIAGNOSED, not fixed here: the #stage DOM is identical played and cold; the page's
`will-change: transform` layer keeps the raster scale an earlier (larger) breath gave it. The engine half of that
claim is pinned below (the DOM is a pure function of t on a breathing page), and every frame here is shot after
its will-change layers are re-promoted (REPROMOTE_JS), so what is compared is the engine's state, not that raster.

The browser half needs playwright + chromium (started only through served_player).
"""
from __future__ import annotations

import copy
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "golden"))

import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402

FPS = 24


def _chromium_available() -> bool:
    try:
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---- the harness: a play and a cold seek of one timeline ---------------------------------------------------------

def _grid(t_from: float, t_to: float) -> list[float]:
    """Every frame of the 24 fps grid from t_from up to (not including) t_to."""
    i0 = round(t_from * FPS)
    return [k / FPS for k in range(i0, int(t_to * FPS) + 1) if k / FPS < t_to - 1e-9]


class _Page:
    def __init__(self, tl: dict, uris: dict):
        self.td = tempfile.TemporaryDirectory()
        html = Path(self.td.name) / "pure.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.w, self.h = RB.STAGE[str(tl.get("aspect") or "16:9")]
        self.page, self.errs, self._close = SP.open_served(html, self.w, self.h, cleanup=self.td.cleanup)

    def shot(self, t: float) -> bytes:
        return RB.rgb_bytes(RB.frame_png(self.page, t, (self.w, self.h)))[1]

    def close(self):
        self._close()


# R26-325 (DIAGNOSED here, not the engine's): a `will-change` element is a composited layer, and Chromium keeps such a
# layer's raster state from the frames it was painted on - a page that breathed larger, or a snap / melt that scaled it,
# rasters its ink at the old scale on the next frame, where a fresh page rasters it at this one. That residue is not in
# the DOM (a played and a sought #stage are the same text), so both frames are compared after every will-change layer
# on the page is re-promoted (will-change off, two frames, back on - a cold page has a history too: the load's own
# frame at 0): what is left is the engine's state alone.
REPROMOTE_JS = """() => { const els = [...document.querySelectorAll('#stage *')].filter((e) => getComputedStyle(e).willChange !== 'auto');
  els.forEach((e) => { e.style.willChange = 'auto'; }); void document.body.offsetHeight;
  return new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => { els.forEach((e) => { e.style.willChange = ''; }); r(els.length); }))); }"""


def _played(tl: dict, uris: dict, t_from: float, ts: list[float], visit: list[float] | None = None,
            settle: bool = True) -> dict:
    """The frames at ts reached by playing every grid frame from t_from (after any `visit` seeks), in one page, each
    shot after the page's will-change layers are re-promoted (REPROMOTE_JS - the compositor's kept raster, R26-325)
    unless `settle` is off (the glow's own test reads the raw frame: its residue was a repaint, not a raster scale)."""
    p = _Page(tl, uris)
    try:
        for v in visit or []:
            p.shot(v)
        out, last = {}, t_from
        for t in sorted(ts):
            for g in _grid(last, t):
                p.shot(g)
            out[t] = p.shot(t)
            if settle:
                p.page.evaluate(REPROMOTE_JS)
                out[t] = p.shot(t)
            last = t + 1e-6
        assert not p.errs, p.errs
        return out
    finally:
        p.close()


def _cold(tl: dict, uris: dict, ts: list[float], settle: bool = True) -> dict:
    out = {}
    for t in ts:
        p = _Page(tl, uris)
        try:
            out[t] = p.shot(t)
            if settle:
                p.page.evaluate(REPROMOTE_JS)
                out[t] = p.shot(t)
            assert not p.errs, p.errs
        finally:
            p.close()
    return out


def _diff(a: bytes, b: bytes, w: int) -> tuple[int, int]:
    """(pixels that differ, the largest channel difference) over the whole frame."""
    import numpy as np
    A = np.frombuffer(a, dtype=np.uint8).reshape(-1, w, 3).astype(int)
    B = np.frombuffer(b, dtype=np.uint8).reshape(-1, w, 3).astype(int)
    d = np.abs(A - B).max(axis=2)
    return int((d > 0).sum()), int(d.max()) if d.size else 0


def _assert_pure(tl: dict, uris: dict, t_from: float, ts: list[float], why: str, visit: list[float] | None = None,
                 settle: bool = True):
    w = RB.STAGE[str(tl.get("aspect") or "16:9")][0]
    played, cold = _played(tl, uris, t_from, ts, visit, settle), _cold(tl, uris, ts, settle)
    bad = {t: _diff(played[t], cold[t], w) for t in ts if played[t] != cold[t]}
    assert not bad, f"{why}: played != cold at {bad} (t: (px, max))"


def _surface(name: str) -> tuple[dict, dict]:
    tl, uris, _t, aspect = RB.load_surface(name)
    return copy.deepcopy(tl), dict(uris)


# ---- R26-260 + R26-21: the snap ----------------------------------------------------------------------------------

SNAP_AT = 8.0
SNAP_CARD = "ev-golden-headline"


def _snap_timeline(centre: bool = True) -> tuple[dict, dict]:
    """A 16:9 page, a card thrown onto it at 6.0, and the next page SNAPS out of that card at 8.0 (throw-then-zoom,
    `recipe:card-becomes-the-chart`): the card's box -> the stage over SNAP_S."""
    tl, uris = _surface("card-parks-at-its-date")
    base = tl["scenes"][0]
    page = dict(base["world"]["page"])
    card = {"slide": SNAP_CARD, "slot": 0, "enter": 6.0, "exit": SNAP_AT + 0.5, "arrive": "throw", "mass": "paper",
            "badge_at": [], "place": {"x": 1180, "y": 520, "w": 600, "h": 400}}
    if centre:
        card["centre"] = True
    else:
        card.update(read_s=0.6, park_s=0.5, park=True)
    s1 = dict(base, scene_id="s01", span=[0.0, SNAP_AT], exit="cut", species=[], docks=[card],
              world=dict(base["world"], page=dict(page, exit="cut")))
    s2 = dict(base, scene_id="s02", span=[SNAP_AT, 16.0], exit="cut", species=[], docks=[],
              world=dict(base["world"], page=dict(page, enter="snap", snap_from=SNAP_CARD)))
    return dict(tl, runtime_s=16.0, scenes=[s1, s2], caption_pages=[], captions=[]), uris


@needs_browser
def test_a_snapped_page_lands_where_a_cold_seek_lands_it():
    """R26-260: after the snap the page stands at the stage, played or seeked (it stood (+137, +100) px off in play)."""
    tl, uris = _snap_timeline()
    _assert_pure(tl, uris, SNAP_AT - 0.5, [SNAP_AT + 0.5, SNAP_AT + 1.38, SNAP_AT + 4.0], "R26-260 the snapped page")


@needs_browser
def test_a_cold_seek_into_the_snap_window_reads_the_cards_box():
    """R26-21: inside the 0.45 s window the page grows from the card's box on a cold seek too (it showed full)."""
    tl, uris = _snap_timeline()
    _assert_pure(tl, uris, SNAP_AT - 0.5, [SNAP_AT + 0.05, SNAP_AT + 0.2, SNAP_AT + 0.4], "R26-21 the snap window")


@needs_browser
def test_a_parked_cards_snap_is_pure_too():
    """The same with a card that pops at reading size and parks: the box the page grows from is the parked one."""
    tl, uris = _snap_timeline(centre=False)
    _assert_pure(tl, uris, SNAP_AT - 0.5, [SNAP_AT + 0.2, SNAP_AT + 1.0], "R26-21 the parked card's snap")


# ---- R26-294: the dock slot ----------------------------------------------------------------------------------------

def _slot_timeline() -> tuple[dict, dict]:
    """A stamped prop in slot 0 (2.0-5.0), then a thrown card in the SAME slot (6.0-20.0) that breathes (kinetics idle)."""
    tl, uris = _surface("prop-stamp")
    tl2, uris2 = _surface("card-parks-at-its-date")
    uris[SNAP_CARD] = uris2[SNAP_CARD]
    ev = dict(tl["evidence"]); ev[SNAP_CARD] = tl2["evidence"][SNAP_CARD]
    sc = tl["scenes"][0]
    prop = dict(sc["docks"][0], enter=2.0, exit=5.0)
    card = {"slide": SNAP_CARD, "slot": 0, "enter": 6.0, "exit": 20.0, "arrive": "throw", "mass": "paper", "centre": True,
            "badge_at": [], "place": {"x": 48, "y": 405, "w": 900, "h": 600}}
    kin = dict(tl.get("kinetics") or {}, idle=True)
    return dict(tl, evidence=ev, kinetics=kin, scenes=[dict(sc, docks=[prop, card], species=[])],
                caption_pages=[], captions=[]), uris


@needs_browser
def test_a_card_after_a_stamp_in_its_slot_turns_about_its_own_origin():
    """R26-294: a jump seek from the stamp's frame to the card's is the card's cold frame (it sat ~1 px off)."""
    tl, uris = _slot_timeline()
    _assert_pure(tl, uris, 9.0, [9.0, 11.3], "R26-294 the slot's state", visit=[3.0])


# ---- R26-321 / R26-322: the melt -----------------------------------------------------------------------------------

MELT_CUT = 15.0


def _live(tl: dict) -> dict:
    """The golden with the outgoing page LIVE (E49's idle) - the life a melt used to clone on whatever frame mounted it."""
    s = tl["scenes"]
    s0 = dict(s[0], world=dict(s[0]["world"], idle="live"))
    return dict(tl, scenes=[s0] + s[1:], kinetics=dict(tl.get("kinetics") or {}, idle=True), caption_pages=[], captions=[])


@needs_browser
@pytest.mark.parametrize("name", ["melt-page", "melt-plate", "melt-gather"])
def test_a_melts_ink_is_the_page_as_painted_at_the_boundary(name):
    """R26-321: the thrown ink is cloned from the page at span[0], so a play and a seek melt the same pixels."""
    tl, uris = _surface(name)
    _assert_pure(_live(tl), uris, MELT_CUT - 0.5, [MELT_CUT + 0.05, MELT_CUT + 0.4, MELT_CUT + 0.9, MELT_CUT + 3.5],
                 f"R26-321 {name}")   # the last instant is past every window here: the clone is gone, played or sought


MORPH_AT = 28.0
MORPH_HAND = MORPH_AT + 1.595 + 0.005   # melt-morph's own hand-over frame (FRAME_T["melt-morph"] - its cut), on this cut


def _morph_after_melt() -> tuple[dict, dict]:
    """melt-page's BARS page (0-10), then card-parks-at-its-date's LINE page arriving by a melt (10-28), then melt-morph's
    page arriving by `melt:morph` (28): the morph follows a melt, and the page it leaves is not the page before it (the
    two pages' ink boxes differ, so the ring read off the wrong one is a different ring)."""
    tl, uris = _surface("melt-morph")
    tp, _up = _surface("melt-page")
    tc, uc = _surface("card-parks-at-its-date")
    uris.update(uc)
    bars, morph, lb = tp["scenes"][1], tl["scenes"][1], tc["scenes"][0]
    line_world = {k: v for k, v in lb["world"].items() if k != "idle"}
    s1 = dict(bars, scene_id="s01", span=[0.0, 10.0], exit="cut")
    s2 = dict(lb, scene_id="s02", span=[10.0, MORPH_AT], exit="melt", docks=[], species=[], world=line_world)
    s3 = dict(morph, scene_id="s03", span=[MORPH_AT, MORPH_AT + 15.0])
    return dict(tl, runtime_s=MORPH_AT + 15.0, scenes=[s1, s2, s3], caption_pages=[], captions=[]), uris


def _morph_reference() -> tuple[dict, dict]:
    """The same leaving page and the same morph with NOTHING before the leaving page: its first scene. Here the world
    the morph leaves has shown that page on every frame, so no stale box can be read - the frame the morph owes."""
    tl, uris = _morph_after_melt()
    s2, s3 = tl["scenes"][1], tl["scenes"][2]
    return dict(tl, scenes=[dict(s2, span=[0.0, MORPH_AT], exit="cut"), s3]), uris


HAND_JS = "() => (typeof window.__lpMeltHand === 'function' ? window.__lpMeltHand() : 'no __lpMeltHand hook')"


def _hand(tl: dict, uris: dict, t: float, t_from: float | None = None) -> object:
    """The ring the arriving page was handed on the frame t (played from t_from, or cold)."""
    p = _Page(tl, uris)
    try:
        for g in _grid(t_from, t) if t_from is not None else []:
            p.shot(g)
        p.shot(t)
        return p.page.evaluate(HAND_JS)
    finally:
        p.close()


@needs_browser
def test_a_morph_after_a_melt_reads_its_ring_off_the_page_it_leaves():
    """R26-322: the hand ring is computed after the outgoing page paints - never the box of the page BEFORE it, which the
    world still showed when the ring used to be read (or a previous melt's mount). On the morph's first frames the ring
    handed after a melt is the ring handed after nothing, played and cold; and the frames themselves are pure."""
    tl, uris = _morph_after_melt()
    ref, ruris = _morph_reference()
    for t in (MORPH_AT, MORPH_AT + 1 / FPS):
        played, cold, want = _hand(tl, uris, t, MORPH_AT - 0.25), _hand(tl, uris, t), _hand(ref, ruris, t, MORPH_AT - 0.25)
        assert isinstance(want, dict) and len(want.get("poly") or []) >= 3, want
        assert played == want, f"R26-322 at {t}: the ring handed after a melt is not the leaving page's"
        assert cold == want, f"R26-322 at {t}: the cold ring is not the leaving page's"
    _assert_pure(tl, uris, MORPH_AT - 0.5, [MORPH_AT + 1 / FPS, MORPH_HAND], "R26-322 the morph's frames")


# ---- R26-324: the title glow -----------------------------------------------------------------------------------------

@needs_browser
def test_the_title_glow_after_its_relight_is_the_cold_glow():
    """R26-324: after the relight hands the title its own ink back, the glow (on) is the cold glow to the bit."""
    from test_relight_clears import T_EARLY, RL_S, FRAME, _timeline
    tl, uris, _aspect = _timeline(T_EARLY, None)
    after = T_EARLY + RL_S + FRAME
    _assert_pure(dict(tl, caption_pages=[], captions=[]), uris, T_EARLY - 0.25, [after, after + 0.5], "R26-324 the title glow",
                 settle=False)


# ---- R26-376: the dock at a depth -----------------------------------------------------------------------------------

@needs_browser
def test_a_dock_at_a_depth_seeks_where_it_plays():
    """R26-376: the depth wrapper turns about the card's placed box (it read an undecoded layout and sat 69 px high)."""
    from build_golden_sources import FRAME_T
    tl, uris = _surface("dock-depth")
    t = FRAME_T["dock-depth"]
    _assert_pure(dict(tl, caption_pages=[], captions=[]), uris, t - 1.0, [t - 0.5, t], "R26-376 the dock's plane")


# ---- R26-325: the engine half of the diagnosis ----------------------------------------------------------------------

@needs_browser
def test_a_breathing_pages_dom_is_a_pure_function_of_t():
    """R26-325's engine half: on a live page the #stage DOM played is the DOM seeked cold (the pixels may differ by
    the compositor's kept raster scale - the diagnosis - which is not the engine's state)."""
    tl, uris = _surface("page-life-live")
    t = 11.3

    def strip(dom: str) -> str:
        return re.sub(r'data:[^"\')]{40,}', "data:", dom)

    p = _Page(tl, uris)
    try:
        for g in _grid(t - 2.0, t):
            p.shot(g)
        p.shot(t); played = strip(p.page.evaluate(RB.STAGE_DOM))
    finally:
        p.close()
    q = _Page(tl, uris)
    try:
        q.shot(t); cold = strip(q.page.evaluate(RB.STAGE_DOM))
    finally:
        q.close()
    assert played == cold
