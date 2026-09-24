"""P69 T65 - A RING MAY CIRCLE THE THING THE SENTENCE POINTS AT: A PICTURE, A CARD OR A PROP (E99 s110 (2)).

The operator, 2026-09-23, on row 18's -64% ring round the railway certificate card (E56 had limited a ring to a
number or a point on a CHART): *"probably keep it as a ring"* - "a ring may circle a picture, a card or a prop when the
sentence points at THAT thing ("look at that certificate again") and carries its number beside it; E56's one-use now
reads: the ring marks what the sentence points at."

What this file holds the compiler and the engine to:

  (1) THE TARGET      a `callout` (the hand's closed circle) or a `ring` (the dashed form) may take
                      `{"kind": "dock", "dock": "<the dock's asset id>"}` - a docked card, a press card or a prop - with
                      an optional `box: [x0, y0, x1, y1]` (fractions of the card: its face). No other species may.
  (2) THE USE, NARROWED BY NAME  the ring on a dock carries its NUMBER (a digit in its `label`) and names the phrase
                      that POINTS at the thing (`points`); either missing is refused citing s110 (2). A picture's
                      point or region with no number is still E56's refusal, word for word.
  (3) ON STAGE        the dock must be on the row and on the stage at the ring's word (a thing that has not arrived or
                      has LEFT is refused by name), the ring's `at` must fall on the pointing phrase as the take says
                      it, and the ring leaves on the dock's leave (a longer `dur` is clamped to the dock's exit).
  (4) THE LIVE BOX    the engine draws the ring at the dock's box AT t - its placed box (the park, a prop's moves:
                      the box the element is written to, and the contact shadow's, R26-58 - so a cold seek rings what
                      forward play rings), else the card as laid out - so a prop that is moved carries its ring; it
                      draws nothing once the dock has gone; the stamp's IMPACT ring is untouched (it is not this ring
                      and is never held).
  (5) BYTE-IDENTICAL  a row with no dock target is returned as the SAME list; every existing ring compiles as it did.
"""
from __future__ import annotations

import contextlib
import copy
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402

PLATE = "world-spike-desk-v1"
STILL = (0, 0, 0)
CERT = "dock-h-certificate-1845"
DOCK = {"kind": "dock", "dock": CERT}
S110 = "E99 s110 (2)"
# the take around row 18's sentence, in timeline.json's own shape (start / end): "So look at that certificate again"
WORDS = [{"w": w, "start": a, "end": z} for w, a, z in (
    ("So", 410.00, 410.20), ("look", 410.24, 410.50), ("at", 410.52, 410.62), ("that", 410.64, 410.90),
    ("certificate", 410.92, 411.60), ("again.", 411.62, 412.10), ("1845", 413.00, 413.80), ("is", 413.84, 413.96),
    ("the", 413.98, 414.08), ("proof.", 414.10, 414.60))]
T_RING = 410.64                       # "that" - the phrase that points at THAT thing
CARD_ON = {"slide": CERT, "slot": 0, "enter": 408.5, "exit": 413.4}   # thrown back on the splash, off before the page returns


def _callout(**kw) -> dict:
    return {"kind": "callout", "at": T_RING, "dur": 2.6, "label": "−64%", "target": dict(DOCK),
            "points": "that certificate", **kw}


def _ring(**kw) -> dict:
    return {**_callout(), "kind": B.SPECIES_RING, "form": "dashed", **kw}


def _errs(entry) -> list[str]:
    return B.validate_species([entry], STILL, PLATE)


# ---- (1) the target: a callout or a ring may take a dock; nothing else may ----------------------------------------------


def test_a_callout_and_a_ring_may_target_a_DOCK():
    assert _errs(_callout()) == []
    assert _errs(_ring()) == []


def test_a_dock_target_may_name_the_cards_face_as_a_box_of_fractions():
    assert _errs(_callout(target={**DOCK, "box": [0.1, 0.2, 0.9, 0.8]})) == []
    for bad in ([0.1, 0.2, 0.9], [0.9, 0.2, 0.1, 0.8], [0.1, 0.2, 1.4, 0.8], "face", [0.1, 0.2, 0.9, True]):
        errs = _errs(_callout(target={**DOCK, "box": bad}))
        assert len(errs) == 1 and "box" in errs[0] and "fractions of the card" in errs[0], (bad, errs)


def test_a_dock_target_names_its_dock_and_nothing_else():
    for bad in ("", "  ", None, 7):
        errs = _errs(_callout(target={"kind": "dock", "dock": bad}))
        assert len(errs) == 1 and "must name its card or prop" in errs[0], (bad, errs)
    errs = _errs(_callout(target={**DOCK, "index": 3}))
    assert len(errs) == 1 and "'index'" in errs[0] and "not a dock target's" in errs[0], errs


def test_no_other_species_may_target_a_dock():
    for kind in ("spotlight", "punch", "squiggle", "focus_zoom"):
        errs = _errs({"kind": kind, "at": T_RING, "dur": 1.0, "target": dict(DOCK)})
        assert any("target kind 'dock' not allowed" in e for e in errs), (kind, errs)


def test_the_underline_is_the_press_cards_phrase_form_never_a_dock_ring():
    errs = _errs(_callout(form="underline"))
    assert len(errs) == 1 and "underline" in errs[0] and "phrase target" in errs[0], errs


# ---- (2) the use: the number beside it AND the phrase that points at it, both by name -----------------------------------


def test_a_ring_on_a_dock_with_NO_NUMBER_is_refused_citing_s110():
    for entry in (_callout(label="the certificate"), _callout(label=None), _ring(label="")):
        errs = _errs({k: v for k, v in entry.items() if v is not None})
        assert len(errs) == 1 and S110 in errs[0] and "NUMBER" in errs[0], errs


def test_a_ring_on_a_dock_with_NO_POINTING_PHRASE_is_refused_citing_s110():
    for pts in (None, "", "   ", 3):
        entry = {k: v for k, v in _callout(points=pts).items() if v is not None}
        errs = _errs(entry)
        assert len(errs) == 1 and S110 in errs[0] and "`points`" in errs[0], (pts, errs)


def test_points_is_the_dock_rings_key_alone():
    errs = _errs({"kind": "callout", "at": 1.0, "dur": 1.0, "target": {"kind": "datum", "index": 2}, "points": "this"})
    assert len(errs) == 1 and "`points`" in errs[0] and "dock" in errs[0], errs


def test_E56_is_unchanged_for_a_pictures_point_or_region():
    """s110 (2) widens the ring to the THING the sentence points at - a docked picture, card or prop - and nothing else:
    a picture's point or region with no number is still the cheap call-out, refused with E56's own words."""
    for kind, extra in (("callout", {}), (B.SPECIES_RING, {"form": "dashed"})):
        for tgt in ({"kind": "point", "x": 0.4, "y": 0.4}, {"kind": "region", "x0": 0.1, "y0": 0.1, "x1": 0.3, "y1": 0.3}):
            errs = _errs({"kind": kind, "at": 1.0, "dur": 1.0, "target": tgt, **extra})
            assert len(errs) == 1 and "a ring circles a NUMBER or a POINT ON A CHART (E56)" in errs[0], errs
            assert "use a spotlight (the light) on a picture" in errs[0], errs
            assert _errs({"kind": kind, "at": 1.0, "dur": 1.0, "target": tgt, "label": "25%", **extra}) == []


# ---- (3) on stage at its word, on the phrase, and leaving with the dock -------------------------------------------------


def _row(species, docks=(CARD_ON,), words=WORDS):
    return B.dock_ring_targets(list(species), [dict(d) for d in docks], words, "shot row 18 (409.2-413.4s)")


def test_a_ring_on_a_dock_on_stage_at_its_word_compiles_and_leaves_with_the_dock():
    sp = [_callout(dur=4.0)]   # authored past the card's exit (413.4 s)
    out, notes = _row(sp)
    assert out[0]["dur"] == pytest.approx(round(CARD_ON["exit"] - T_RING, 2)), out[0]
    assert sp[0]["dur"] == 4.0, "the authored entry is never mutated - the row gets a copy"
    assert len(notes) == 1 and "the dock's leave" in notes[0] and CERT in notes[0], notes
    out2, notes2 = _row([_callout(dur=1.5)])
    assert out2[0]["dur"] == 1.5 and notes2 == [], "a ring shorter than its dock's life is its own length"


def test_a_ring_on_a_dock_NOT_ON_THE_ROW_is_refused_by_name():
    with pytest.raises(ValueError, match=r"'dock-h-certificate-1845'.*not on this row"):
        _row([_callout()], docks=())


def test_a_ring_on_a_thing_that_has_LEFT_is_refused_by_name():
    with pytest.raises(ValueError, match=r"has LEFT"):
        _row([_callout()], docks=({**CARD_ON, "exit": 410.2},))
    with pytest.raises(ValueError, match=r"has not arrived"):
        _row([_callout()], docks=({**CARD_ON, "enter": 411.0},))


def test_the_rings_word_is_the_phrase_that_points_at_the_thing():
    with pytest.raises(ValueError, match=r"E99 s110 \(2\).*'that certificate' is said 410.64-411.60s"):
        _row([_callout(at=413.0, dur=0.3)])
    out, _ = _row([_callout(at=411.1, dur=1.0)])
    assert out[0]["at"] == 411.1, "any instant inside the phrase is on it"
    with pytest.raises(ValueError, match=r"'that railway certificate' is not in the take"):
        _row([_callout(points="that railway certificate")])
    with pytest.raises(ValueError, match=r"needs the build's words"):
        _row([_callout()], words=None)


def test_a_row_with_no_dock_ring_is_returned_as_the_SAME_list():
    sp = [{"kind": "callout", "at": 1.0, "dur": 1.0, "label": "25%", "target": {"kind": "point", "x": 0.4, "y": 0.4}}]
    out, notes = B.dock_ring_targets(sp, [], None, "row")
    assert out is sp and notes == []


# ---- (4) the engine: the ring at the dock's LIVE box, gone with the dock --------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """(aid) => {
  const sb = document.getElementById('stage').getBoundingClientRect();
  const box = (r) => r ? { x: r.left - sb.left, y: r.top - sb.top, w: r.width, h: r.height } : null;
  const d = document.querySelector('.dock[data-slide="' + aid + '"]');
  const img = d && d.querySelector('.slide-frame img');
  const co = document.querySelector('#species path.co'), lab = document.querySelector('#species text.lab');
  const ring = document.querySelector('.dock-ring');
  return { card: d ? box(d.getBoundingClientRect()) : null, img: img ? box(img.getBoundingClientRect()) : null,
           co: co ? box(co.getBoundingClientRect()) : null, label: lab ? lab.textContent : null,
           impact: ring ? +getComputedStyle(ring).opacity : null };
}"""


class _Player:
    def __init__(self, browser, tl: dict, uris: dict):
        import render_baseline as RB
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

    def at(self, t: float, aid: str) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                           "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE, aid)

    def close(self) -> None:
        self.page.context.close(); self._srv.shutdown(); self._td.cleanup()


@contextlib.contextmanager
def _browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    try:
        yield br
    finally:
        br.close(); pw.stop()


CARD_AID, CARD_RING_AT, CARD_RING_DUR = "ev-golden-chart", 10.0, 6.0
PROP_AID, T_MOVE, T_BEFORE, T_AFTER = "ev-prop-fed", 14.0, 13.9, 15.3


def _card_timeline() -> tuple[dict, dict]:
    """The committed `chart-callout` surface (a still card on a plain plate) with its callout moved from a plate point
    onto the CARD, as the new grammar writes it."""
    import render_baseline as RB
    tl, uris, _t, _a = RB.load_surface("chart-callout")
    tl = copy.deepcopy(tl)
    tl["scenes"][0]["species"] = [{"kind": "callout", "at": CARD_RING_AT, "dur": CARD_RING_DUR, "label": "−64%",
                                   "target": {"kind": "dock", "dock": CARD_AID}, "points": "that chart"}]
    return tl, dict(uris)


def _prop_timeline() -> tuple[dict, dict]:
    """The committed `prop-stamp` surface: the Fed stamped at an authored place, MOVED on 14 s, and ringed from 12 s to
    its exit - the ring must travel with it."""
    import render_baseline as RB
    import build_golden_sources as G
    tl, uris, _t, _a = RB.load_surface("prop-stamp")
    tl = copy.deepcopy(tl)
    world = tl["scenes"][0]["world"]
    opts = {"prop": True, "arrive": "stamp", "mass": "ink", "ink": "own", "place": {"x": 0.62, "y": 0.62, "w": 0.12},
            "moves": [{"at": T_MOVE, "x": 0.4, "y": 0.66, "w": 0.16, "dur": 1.0, "ease": "minjerk"}]}
    dopt = B.dock_opts(opts)
    paint = B.painted_box(G.PROP_CUTOUT)   # the cutout's painted extent - test_prop_free_placement's own `_fed()`
    fit = B.stamp_dock_place(world, "16:9", dopt, paint, None, None, "t")
    moves, _w = B.prop_moves(dopt, paint, fit, "16:9", G.PROP_STAMP_ENTER, G.PROP_STAMP_EXIT, None, "t", world)
    new = B.dock_entry(PROP_AID, 0, G.PROP_STAMP_ENTER, G.PROP_STAMP_EXIT, 0, B.DOCK_KIND_PROP,
                       {k: fit[k] for k in ("x", "y", "w", "h", "room")}, "stamp", "ink", True, prop=True, ink="own",
                       ring_to=fit["ring_to"], from_to=fit["from_to"], paint=fit["paint"], moves=moves)
    tl["scenes"][0]["docks"] = [new]
    tl["scenes"][0]["species"] = [{"kind": "callout", "at": 12.0, "dur": round(G.PROP_STAMP_EXIT - 12.0, 2), "label": "5.25%",
                                   "target": {"kind": "dock", "dock": PROP_AID}, "points": "the Fed"}]
    return tl, dict(uris)


@pytest.fixture(scope="module")
def drawn():
    out = {}
    with _browser() as br:
        card = _Player(br, *_card_timeline())
        try:
            out["card"] = {t: card.at(t, CARD_AID) for t in (9.9, 13.0, CARD_RING_AT + CARD_RING_DUR + 0.2)}
            out["card_errors"] = list(card.errors)
        finally:
            card.close()
        prop = _Player(br, *_prop_timeline())
        try:
            out["prop"] = {t: prop.at(t, PROP_AID) for t in (T_BEFORE, T_AFTER, 25.5, 26.4)}   # T_BEFORE is a COLD seek
            out["prop_warm"] = prop.at(T_BEFORE, PROP_AID)                                  # ... and this one is not
            out["prop_errors"] = list(prop.errors)
        finally:
            prop.close()
    return out


def _centre(b: dict) -> tuple[float, float]:
    return b["x"] + b["w"] / 2, b["y"] + b["h"] / 2


@needs_browser
def test_the_ring_is_drawn_ROUND_THE_CARD_as_drawn_with_its_number(drawn):
    r = drawn["card"][13.0]
    assert drawn["card_errors"] == []
    assert r["co"] is not None, "a callout on a dock target draws its ring (RED before T65: resolveTarget knew no dock)"
    (cx, cy), (kx, ky) = _centre(r["co"]), _centre(r["card"])
    assert abs(cx - kx) < 12 and abs(cy - ky) < 12, (r["co"], r["card"])
    assert r["co"]["w"] > r["card"]["w"] and r["co"]["h"] > r["card"]["h"], "the ring passes ROUND the card, outside it"
    assert r["label"] == "−64%", "the ring writes its figure beside it"
    assert drawn["card"][9.9]["co"] is None and drawn["card"][CARD_RING_AT + CARD_RING_DUR + 0.2]["co"] is None


@needs_browser
def test_a_MOVED_prop_carries_its_ring(drawn):
    a, b = drawn["prop"][T_BEFORE], drawn["prop"][T_AFTER]
    assert drawn["prop_errors"] == []
    assert a["co"] and b["co"], (a, b)
    for r in (a, b):
        (cx, cy), (ix, iy) = _centre(r["co"]), _centre(r["img"])
        assert abs(cx - ix) < 14 and abs(cy - iy) < 14, ("the ring is centred on the prop's painted box", r)
    assert abs((_centre(b["co"])[0] - _centre(a["co"])[0]) - (_centre(b["img"])[0] - _centre(a["img"])[0])) < 6, \
        "the ring moved by what the prop moved"
    assert b["co"]["w"] > a["co"]["w"], "and grew with it (0.12 -> 0.16 of the stage)"


@needs_browser
def test_the_ring_LEAVES_ON_THE_PROPS_LEAVE_and_the_impact_ring_is_untouched(drawn):
    assert drawn["prop"][25.5]["co"] is not None
    assert drawn["prop"][26.4]["co"] is None, "the prop has left (exit 26.0): nothing is ringed"
    assert drawn["prop"][T_AFTER]["impact"] in (None, 0.0), "the stamp's impact ring is never held - it is not this ring"


@needs_browser
def test_a_COLD_SEEK_rings_the_box_forward_play_rings(drawn):
    """The ring reads the PLACED box at t (the contact shadow's own, R26-58), never the layout of an image mounted in the
    same frame and not yet decoded - which drew a quarter ring on the first seek (281 x 75 px round a 262 x 246 prop)."""
    assert drawn["prop"][T_BEFORE]["co"] == drawn["prop_warm"]["co"], (drawn["prop"][T_BEFORE]["co"], drawn["prop_warm"]["co"])
