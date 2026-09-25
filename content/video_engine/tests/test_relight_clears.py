"""P71 T2 / R26-308 - a title relight clears on its last frame: the title's colour is a pure function of t.

The relight fires the sunflower (PS.RELIGHT_COL) through the title on a sine over its dur. It used to write the glyphs'
colour only INSIDE its window, so the last frame inside kept the sunflower and a frame reached by playing through the
relight differed from the same frame reached by a seek. It also always lit the LAST retitle's glyphs, whatever title
stood at t. Now every frame of a page with a title relight writes the colour of every title glyph from t: the sunflower
on the glyphs of the title STANDING at t while a relight's sine is up, and otherwise the glyph's own (a keyed span's
token, T86's `__col`, else the title's ink). The glow (P69 T37c, a currentColor text-shadow) follows the same colour.

The browser half (the real engine through the player, as test_page_performs does) needs playwright + chromium.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_baseline as RB  # noqa: E402

try:
    from test_page_performs import _Player, _authored, _line_golden, needs_browser, T_RETITLE  # noqa: E402
except Exception:  # pragma: no cover - the browser half is skipped when its harness cannot load
    needs_browser = pytest.mark.skip(reason="test_page_performs harness unavailable")
    T_RETITLE = 19.0

RELIT = "rgb(245, 183, 46)"      # PS.RELIGHT_COL "#F5B72E", as the DOM reads it back
FRAME = 1 / 24
FLIP = "The flip: memory breaks while the buildout holds"
SPAN = "The flip"
T_EARLY = 16.0                   # a relight BEFORE the retitle (T_RETITLE 19.0): the original title stands
T_LATE = 25.0                    # a relight AFTER the retitle has written (19.0 + 2.0): the retitle stands
RL_S = 1.0

TITLES_JS = """() => {
  const w = [...document.querySelectorAll('.lp-page')].find((e) => getComputedStyle(e).visibility !== 'hidden'
            && +getComputedStyle(e).opacity > 0) || document;
  const glyphs = (el) => [...el.querySelectorAll('.g')].map((g) => { const cs = getComputedStyle(g);
    return { ch: g.textContent, c: cs.color, s: cs.textShadow }; });
  const home = (w.querySelector('.lp-title') || document.body).parentNode;   /* the tokens are declared on the page */
  const probe = document.createElement('span'); home.appendChild(probe);
  probe.style.color = 'var(--lp-neg)'; const neg = getComputedStyle(probe).color; probe.remove();
  const title = w.querySelector('.lp-title:not(.lp-retitle)');
  return { neg, own: title ? getComputedStyle(title).color : null, title: title ? glyphs(title) : [],
           retitles: [...w.querySelectorAll('.lp-retitle')].map((r) => ({ own: getComputedStyle(r).color, glyphs: glyphs(r) })) };
}"""


def _timeline(relight_at: float, retitle: dict | None) -> tuple[dict, dict, str]:
    """The line golden's performing page with ONE title relight (the bracket relight kept) and the retitle as keyed,
    or no retitle at all."""
    _name, tl, uris, aspect, pts = _line_golden()
    tl2, _peak, _last = _authored(tl, pts)
    sc = tl2["scenes"][0]
    species = []
    for sp in sc["species"]:
        if sp["kind"] == "retitle":
            if retitle is None:
                continue
            sp = dict(sp, text=FLIP, **retitle)
        species.append(sp)
    species.append({"kind": "relight", "at": relight_at, "dur": RL_S, "ref": "title"})
    return dict(tl2, scenes=[dict(sc, species=species)]), uris, aspect


TITLE_BOX_JS = """() => {
  const st = document.getElementById('stage').getBoundingClientRect();
  const rs = [...document.querySelectorAll('.lp-title')].map((e) => e.getBoundingClientRect()).filter((r) => r.width > 0);
  return [Math.min(...rs.map((r) => r.left)) - st.left, Math.min(...rs.map((r) => r.top)) - st.top,
          Math.max(...rs.map((r) => r.right)) - st.left, Math.max(...rs.map((r) => r.bottom)) - st.top];
}"""
GLOW_OFF_JS = "() => document.querySelectorAll('.lp').forEach((e) => e.style.setProperty('--lp-title-glow', 'none'))"


def _read(P, t: float) -> tuple[dict, bytes]:
    png = RB.frame_png(P.page, t, (P.w, P.h))
    return P.page.evaluate(TITLES_JS), png


def _title_crop(P, png: bytes, pad: int = 16) -> bytes:
    """The title's own pixels (every title of the page, padded): the frame's other species keep their own history."""
    import numpy as np
    (w, h), rgb = RB.rgb_bytes(png)
    x0, y0, x1, y1 = P.page.evaluate(TITLE_BOX_JS)
    a = np.frombuffer(rgb, dtype=np.uint8).reshape(h, w, 3)
    return a[max(0, int(y0) - pad):min(h, int(y1) + pad), max(0, int(x0) - pad):min(w, int(x1) + pad)].tobytes()


def _standing(fr: dict, retitled: bool) -> list[dict]:
    return fr["retitles"][0]["glyphs"] if retitled else fr["title"]


def _own(fr: dict, retitled: bool, keyed: bool) -> list[str]:
    """What each standing glyph reads when no relight is up: the span's token on a keyed span, else the title's ink."""
    glyphs = _standing(fr, retitled)
    if not retitled:
        return [fr["own"]] * len(glyphs)
    k = len(SPAN) if len(glyphs) == len(FLIP) else len(SPAN) - SPAN.count(" ")   # a wrapped title writes no space glyph
    own = fr["retitles"][0]["own"]
    return [fr["neg"] if keyed and j < k else own for j in range(len(glyphs))]


def _glow_agrees(glyphs: list[dict]) -> bool:
    """T37c's glow is a currentColor text-shadow: each glyph's shadow carries its own colour and no other."""
    return all(g["s"] != "none" and g["s"].count("rgb") == g["s"].count(g["c"]) >= 1 for g in glyphs)


CASES = {
    "no retitle": (None, False, False),
    "retitle": ({}, True, False),
    "retitle keyed span": ({"color": "neg", "color_span": SPAN}, True, True),
}


@needs_browser
@pytest.mark.parametrize("case", list(CASES))
def test_the_frame_after_a_title_relight_reads_the_titles_own_colour_by_seek_and_by_play_through(case):
    retitle, retitled, keyed = CASES[case]
    at = T_LATE if retitled else T_EARLY
    tl, uris, aspect = _timeline(at, retitle)
    after = at + RL_S + FRAME
    P = _Player(tl, uris, aspect)
    try:
        before, _ = _read(P, at - 0.5)
        seek, _ = _read(P, after)                       # reached by a seek from before the relight
        lit, _ = _read(P, at + RL_S / 2)
        _read(P, at + RL_S - FRAME)                     # the relight's last frame inside its window
        play, _ = _read(P, after)                       # ... and the next frame, reached by playing through
        back, _ = _read(P, at - 0.5)                    # a seek back before the relight
        # the bits: T37c's glow is a text-shadow, and Chromium's PARTIAL repaint of a shadowed glyph after ANY colour
        # change differs from a full paint by a few levels in the glow's band (a full re-layout restores it; the same
        # residue follows a colour flipped by hand with no relight at all). With the glow off the title's pixels are
        # the engine's alone, so the bit test is taken there.
        P.page.evaluate(GLOW_OFF_JS)
        _read(P, at - 0.5)
        seek_px = _title_crop(P, _read(P, after)[1])
        _read(P, at + RL_S / 2)
        _read(P, at + RL_S - FRAME)
        play_px = _title_crop(P, _read(P, after)[1])
    finally:
        P.close()
    own = _own(before, retitled, keyed)
    assert own and RELIT not in own
    assert [g["c"] for g in _standing(lit, retitled)] == [RELIT] * len(own), "mid-relight: every standing glyph lit"
    assert [g["c"] for g in _standing(play, retitled)] == own, \
        f"the frame after the relight reads the title's own colour: {[g['c'] for g in _standing(play, retitled)]}"
    assert [g["c"] for g in _standing(seek, retitled)] == own
    assert play == seek, "every title glyph's colour and glow read the same by a seek and by a play-through"
    assert play_px == seek_px, "the title's bits are the same by a seek and by a play-through"
    assert back == before, "a seek back before the relight paints the title unlit"
    for fr in (before, lit, play):
        assert _glow_agrees(_standing(fr, retitled)), "the glow follows the glyph's colour at t"


@needs_browser
@pytest.mark.parametrize("keyed", [False, True])
def test_a_relight_before_a_retitle_lights_the_standing_title_and_not_the_later_retitle(keyed):
    tl, uris, aspect = _timeline(T_EARLY, {"color": "neg", "color_span": SPAN} if keyed else {})
    P = _Player(tl, uris, aspect)
    try:
        before, _ = _read(P, T_EARLY - 0.5)
        mid, _ = _read(P, T_EARLY + RL_S / 2)
        after, _ = _read(P, T_EARLY + RL_S + FRAME)
        written, _ = _read(P, T_RETITLE + 2.6)          # the retitle stands, written; the relight long gone
    finally:
        P.close()
    assert [g["c"] for g in mid["title"]] == [RELIT] * len(mid["title"]), "the standing (original) title lights"
    assert _glow_agrees(mid["title"])
    rt_own = [g["c"] for g in before["retitles"][0]["glyphs"]]
    assert RELIT not in rt_own
    assert [g["c"] for g in mid["retitles"][0]["glyphs"]] == rt_own, "the not-yet-shown retitle is never lit"
    assert [g["c"] for g in after["title"]] == [before["own"]] * len(after["title"])
    assert [g["c"] for g in written["retitles"][0]["glyphs"]] == _own(written, True, keyed), \
        "the retitle writes in its own colour (a keyed span keeps its token)"


@needs_browser
def test_a_relight_across_a_retitle_moves_to_the_title_standing_at_each_frame():
    """A relight still up when the retitle fires lights the title standing at each t: the original before the word,
    the retitle from its `at` on (the chain's own clock) - never both at once."""
    at = T_RETITLE - RL_S / 2
    tl, uris, aspect = _timeline(at, {})
    P = _Player(tl, uris, aspect)
    try:
        pre, _ = _read(P, T_RETITLE - 0.1)
        post, _ = _read(P, T_RETITLE + 0.1)
    finally:
        P.close()
    assert {g["c"] for g in pre["title"]} == {RELIT} and RELIT not in {g["c"] for g in pre["retitles"][0]["glyphs"]}
    assert RELIT not in {g["c"] for g in post["title"]} and {g["c"] for g in post["retitles"][0]["glyphs"]} == {RELIT}
