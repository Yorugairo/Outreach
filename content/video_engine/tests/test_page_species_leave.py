"""R26-219 - A NOTE OR FIGURE THE PAGE WRITES DOES NOT SURVIVE A `chart_to`.

Measured on the Steel and Paper H unit (2026-09-18): the railway page's two `note`s and its `-64%` `figure` were
still standing on the GDP page eight seconds after the recast. A note, a figure, a retitle, a bracket and a spread
are PAGE-BOUND - the hand wrote them on one page, about that page's marks - so a `chart_to` that REPLACES the page
takes them with it, on the page's own 1.0 s leave (the vortex's first phase, so nothing pops).

The law is decided ONCE, in the compiler (`stamp_page_leave`, beside the hold pass that decides the other end of a
species' life), and run in the player's perform layer off the stamped clock. Three parts of it are the compiler's
precisely so a GATE can read them - a player clock nothing measures is a lie in the timeline, and the shot table,
`gate_motion_density` and M21's deployed life all credit a species for its `dur`:

  * `leave_at` / `leave_s` - when the retract starts and how long it takes;
  * the `dur` CLAMP - the authored duration never outlasts the page (a note `dur: 10` under a recast 1.0 s later
    reads 2.0 s: its second on the page plus the page's leave);
  * the DROP - a species whose replacing verb fires on its own word is removed, not written-then-retracted, the way
    `HOLD_MIN_S` refuses a flash.

`keep: true` on the species refuses all of it. The verbs that replace a page are the three that re-write the chart
into another state; a rescale, an extend, a park and a compare all keep the SAME page and take nothing with them -
which is also why every golden is untouched.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

DIVERGENCE = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-divergence-v1.series.json"


def _note(at: float = 5.0, **kw) -> dict:
    return {"kind": "note", "at": at, "dur": 2.0, "text": "the railway bill came due", **kw}


def _recast(at: float = 12.0, dur: float = 1.8) -> dict:
    return {"kind": "chart_to", "at": at, "dur": dur, "to": "recast", "state": 1}


# ---- the law, as constants ----------------------------------------------------------------------------


def test_the_page_bound_species_are_the_five_the_hand_writes_on_a_page():
    assert B.PAGE_BOUND_SPECIES == ("note", "figure", "retitle", "bracket", "spread")
    assert set(B.PAGE_BOUND_SPECIES) <= set(B.PAGE_SPECIES), "each one is painted by the page's own perform layer"


def test_only_the_three_verbs_that_re_write_the_chart_replace_the_page():
    assert B.PAGE_REPLACING_VERBS == ("recast", "morph", "remake")
    assert set(B.PAGE_REPLACING_VERBS) <= set(B.CHART_TO_KINDS)
    kept = set(B.CHART_TO_KINDS) - set(B.PAGE_REPLACING_VERBS)
    assert kept == {"rescale", "extend", "park", "compare"}, (
        "a rescale retargets the axes, an extend grows the window, a park makes room and a compare morphs a figure "
        "the page already wrote - the page is the same page, so nothing written on it leaves")


def test_the_leave_is_the_pages_own_one_second():
    assert B.PAGE_LEAVE_S == 1.0, "the vortex's first phase (LP_RETRACT.COLOURS) - a fade the eye does not see pop"


# ---- the stamp ---------------------------------------------------------------------------------------


def test_a_note_ends_with_the_page_the_recast_replaces():
    ct = _recast(at=12.0, dur=1.8)
    row = [_note(at=5.0), ct]
    stamped, clamped, dropped = B.stamp_page_leave(row)
    assert (len(stamped), clamped, dropped) == (1, [], [])
    note = row[0]
    assert note["leave_at"] == 12.0 and note["leave_s"] == 1.0
    end = B.page_species_end(note)
    assert end == 13.0
    assert end <= ct["at"] + B.PAGE_LEAVE_S, "the note is off the page within the page's own leave of the word"
    assert end <= ct["at"] + ct["dur"], "and inside the recast's own hand-over, so it never outlives the chart it described"
    assert end > ct["at"], "it retracts, it does not vanish on the frame the word lands"


def test_the_dur_is_clamped_to_the_leave_so_no_gate_credits_a_note_the_page_took():
    """The reviewer's own case: `dur: 10` killed by a recast 1.0 s later reads 1.0 s + the leave in the timeline."""
    row = [_note(at=6.0, dur=10.0), _recast(at=7.0, dur=1.8)]
    stamped, clamped, dropped = B.stamp_page_leave(row)
    note = row[0]
    assert note["dur"] == 2.0, ("its second on the page plus the page's 1.0 s leave", note)
    assert note["leave_clamped"] is True, "the record of why the duration is what it is"
    assert clamped == [("note", 10.0, 2.0)] and len(stamped) == 1 and dropped == []
    assert note["at"] + note["dur"] == B.page_species_end(note) == 8.0, \
        "the dur and the leave agree: the timeline's own end IS the page's"


def test_a_dur_that_already_fits_inside_the_leave_is_not_touched():
    row = [_note(at=5.0, dur=2.0), _recast(at=12.0)]
    stamped, clamped, dropped = B.stamp_page_leave(row)
    assert row[0]["dur"] == 2.0 and clamped == [] and "leave_clamped" not in row[0]
    assert len(stamped) == 1 and dropped == []


def test_keep_true_holds_the_note_through_the_recast():
    row = [_note(at=5.0, keep=True), _recast()]
    stamped, clamped, dropped = B.stamp_page_leave(row)
    assert (stamped, clamped, dropped) == ([], [], [])
    assert "leave_at" not in row[0] and B.page_species_end(row[0]) is None
    assert row[0]["dur"] == 2.0, "and its authored duration is its own"
    assert B._validate_page_fields("note", row[0]) == []


def test_every_page_bound_species_takes_the_leave_and_nothing_else_does():
    row = [{"kind": k, "at": 4.0, "dur": 1.0} for k in B.PAGE_BOUND_SPECIES]
    row += [{"kind": k, "at": 4.0, "dur": 1.0} for k in ("build_to", "undraw", "relight", "span", "callout", "ring")]
    row += [_recast(at=10.0)]
    stamped, _clamped, dropped = B.stamp_page_leave(row)
    assert len(stamped) == len(B.PAGE_BOUND_SPECIES) and dropped == []
    assert {e["kind"] for e in stamped} == set(B.PAGE_BOUND_SPECIES)
    assert {e["kind"] for e in row if "leave_at" in e} == set(B.PAGE_BOUND_SPECIES)


@pytest.mark.parametrize("to, extra", [("rescale", {"ymin": 0, "ymax": 10}), ("extend", {"to_index": 9}),
                                       ("park", {}), ("compare", {})])
def test_a_verb_that_keeps_the_page_takes_nothing_with_it(to, extra):
    row = [_note(at=5.0), {"kind": "chart_to", "at": 12.0, "dur": 1.0, "to": to, **extra}]
    assert B.stamp_page_leave(row) == ([], [], [])
    assert B.page_species_end(row[0]) is None


def test_a_note_written_after_the_recast_stands_and_the_first_verb_wins():
    """The note the ARRIVING page writes is not the leaving page's: only a replacing verb at or after the note's
    own word takes it. And when two recasts run, the first one is the one that took what stood before it."""
    row = [_note(at=5.0), _recast(at=12.0), _note(at=14.0), _recast(at=20.0)]
    stamped, _clamped, dropped = B.stamp_page_leave(row)
    assert len(stamped) == 2 and dropped == []
    assert row[0]["leave_at"] == 12.0, "the first note leaves on the FIRST recast, not the second"
    assert row[2]["leave_at"] == 20.0, "the note the second page carried leaves on its own page's recast"


def test_a_recast_on_the_notes_own_word_DROPS_it_rather_than_writing_it_to_retract_it():
    """`HOLD_MIN_S` (2026-09-08) refuses a held light with no room because a flash is a glitch. A note whose page is
    re-written on the very word the hand would start writing has no room at all: it is dropped from the row, and the
    drop is reported, rather than written and immediately retracted."""
    note, ct = _note(at=12.0), _recast(at=12.0)
    row = [note, ct]
    stamped, clamped, dropped = B.stamp_page_leave(row)
    assert (stamped, clamped) == ([], [])
    assert dropped == [note], dropped
    assert row == [ct], "the species is REMOVED from the row, so no gate and no player ever sees it"
    assert "leave_at" not in note, "nothing was stamped on it: there was nothing to stamp"


def test_a_recast_a_hair_after_the_word_is_a_leave_not_a_drop():
    row = [_note(at=12.0), _recast(at=12.4)]
    stamped, clamped, dropped = B.stamp_page_leave(row)
    assert len(stamped) == 1 and dropped == []
    assert row[0]["leave_at"] == 12.4 and row[0]["dur"] == 1.4 and clamped == [("note", 2.0, 1.4)]


def test_a_row_with_no_replacing_verb_stamps_nothing_and_a_stamped_row_is_stamped_once():
    row = [_note(at=5.0)]
    assert B.stamp_page_leave(row) == ([], [], []) and B.page_species_end(row[0]) is None
    row.append(_recast(at=12.0))
    assert len(B.stamp_page_leave(row)[0]) == 1
    assert B.stamp_page_leave(row) == ([], [], []), "idempotent: a second pass over a stamped row changes nothing"
    assert row[0]["leave_at"] == 12.0


def test_page_species_end_of_something_that_never_leaves_is_none():
    assert B.page_species_end({"kind": "note", "at": 1.0}) is None
    assert B.page_species_end(None) is None
    assert B.page_species_end({"kind": "note", "at": 1.0, "leave_at": True}) is None, "a bool is not a clock"
    assert B.page_species_end({"kind": "note", "at": 1.0, "leave_at": 4.0}) == 5.0, "an unstamped leave_s is the page's own"


# ---- `keep`, as a field ------------------------------------------------------------------------------


def test_keep_must_be_a_bool_and_only_a_page_bound_species_has_one():
    errs = B._validate_page_fields("note", {"kind": "note", "at": 1.0, "text": "x", "keep": "yes"})
    assert any("keep must be true or false" in e for e in errs), errs
    errs = B._validate_page_fields("undraw", {"kind": "undraw", "at": 1.0, "keep": True})
    assert any("keep is only for a page-bound species" in e for e in errs), errs
    for k in B.PAGE_BOUND_SPECIES:
        assert not [e for e in B._validate_page_fields(k, {"kind": k, "at": 1.0, "keep": False}) if "keep" in e], k


# ---- the pass is WIRED into the compiler's row loop, and its report names all three outcomes ----------


def test_the_stamp_runs_on_every_row_beside_the_hold_pass_and_reports_the_clamp_and_the_drop():
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    assert "left, clamped, page_dropped = stamp_page_leave(row_species)" in src, \
        "the pass has to run on the authored row, not on demand"
    hold = src.index("hold: dropped")
    validate = src.index("species_errors = (validate_species(row_species")
    call = src.index("left, clamped, page_dropped = stamp_page_leave(row_species)")
    assert hold < call < validate, "after the hold pass has settled every `dur`, before the row is validated"
    for line in ("page leave: dur clamped to the leave on row", "page leave: dropped "):
        assert line in src, ("the compile output says what it did: " + line)


# ---- and the player runs the clock: the note is GONE on the next page ---------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
needs_objects = pytest.mark.skipif(not DIVERGENCE.exists(), reason="the divergence evidence object is not on disk")

LEAVE_PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const note = world.querySelector('.lp-note');
  return { note: note ? (note.style.opacity === '' ? 1 : parseFloat(note.style.opacity)) : null,
           written: note ? [...note.querySelectorAll('.g')].reduce((a, g) => a + (parseFloat(g.style.getPropertyValue('--w')) || 0), 0) : null };
}"""


def _leave_player(species, runtime=30.0):
    """A three-series line page with a bars state to recast into, and whatever species the case names."""
    from playwright.sync_api import sync_playwright
    src = json.loads(DIVERGENCE.read_text(encoding="utf-8"))
    src = dict(src, series=src["series"][:3])
    bars = {"title": "Where the three stand today", "sub": "index, 100 = Aug 2025", "src": "Yahoo Finance", "unit": "",
            "bars": [{"label": s.get("name") or ("s%d" % i), "value": round(float(s["pts"][-1][1]), 1),
                      "color": s.get("color", "crimson")} for i, s in enumerate(src["series"])]}
    td = tempfile.TemporaryDirectory()
    ep = Path(td.name)
    (ep / "evidence/objects").mkdir(parents=True)
    (ep / "evidence/objects/ev-lines-v1.series.json").write_text(json.dumps(src), encoding="utf-8")
    (ep / "evidence/objects/ev-bars-v1.series.json").write_text(json.dumps(bars), encoding="utf-8")
    plate = "ledger:ev-lines-v1:line;then=ev-bars-v1:bars"
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(plate, (0, 0, 0), ep)
    B.derive_rescale_states(world, species, plate, ep)
    scene = dict(tl["scenes"][0], species=species, span=[0.0, runtime],
                 world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=runtime, scenes=[scene], caption_pages=[], captions=[])
    html = ep / "leave.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    w, h = RB.STAGE["9:16"]
    srv, port = RB.serve(html.parent)
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    page = br.new_context(viewport={"width": w, "height": h}).new_page()
    errs: list[str] = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(LEAVE_PROBE)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, errs, close


RC_AT, RC_S = 14.0, 1.8


@needs_objects
@needs_browser
def test_the_note_the_page_wrote_is_gone_on_the_page_that_replaced_it():
    """The H unit's own defect, at the instants that matter: the note stands while its page does, retracts on the
    page's leave, and is off the screen for the rest of the scene (it was still standing eight seconds later)."""
    row = [_note(at=6.0), _recast(at=RC_AT, dur=RC_S)]
    assert len(B.stamp_page_leave(row)[0]) == 1
    at, errs, close = _leave_player(row)
    try:
        before = at(RC_AT - 0.5)
        assert before["note"] == 1 and before["written"] > 0, "the page's own note, written and standing"
        mid = at(RC_AT + B.PAGE_LEAVE_S * 0.5)
        assert 0.01 < mid["note"] < 0.99, ("the note RETRACTS on the page's leave rather than cutting", mid)
        after = at(RC_AT + B.PAGE_LEAVE_S + 0.05)
        assert after["note"] == 0, ("off the page by the end of its leave", after)
        eight = at(RC_AT + 8.0)
        assert eight["note"] == 0, ("R26-219, measured: eight seconds later it was still standing", eight)
        back = at(RC_AT - 0.5)
        assert back["note"] == 1 and back["written"] == before["written"], "a seek back is the play"
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_a_clamped_note_is_fully_written_before_its_page_goes():
    """The clamp is not bookkeeping: the hand has to finish inside the room the page leaves it. `dur: 10` under a
    recast 1.2 s later writes every glyph by the moment the retract starts."""
    row = [_note(at=6.0, dur=10.0), _recast(at=7.2, dur=1.8)]
    assert B.stamp_page_leave(row)[1] == [("note", 10.0, 2.2)]
    at, errs, close = _leave_player(row)
    try:
        full = at(7.2)   # the word that replaces the page: the note is written whole
        assert full["note"] == 1, full
        n_glyphs = at(6.0)
        assert full["written"] >= n_glyphs["written"], full
        assert full["written"] > 0 and abs(full["written"] - round(full["written"])) < 0.5, \
            ("every glyph at full width by the leave's first frame", full)
        assert at(7.2 + B.PAGE_LEAVE_S + 0.05)["note"] == 0, "and gone by the end of the leave"
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_a_note_that_keeps_survives_the_same_recast():
    row = [_note(at=6.0, keep=True), _recast(at=RC_AT, dur=RC_S)]
    assert B.stamp_page_leave(row) == ([], [], [])
    at, errs, close = _leave_player(row)
    try:
        assert at(RC_AT - 0.5)["note"] == 1
        assert at(RC_AT + B.PAGE_LEAVE_S + 0.05)["note"] == 1, "keep: true - the note is about the argument, not the page"
        assert at(RC_AT + 8.0)["note"] == 1
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_a_dropped_note_never_reaches_the_page_at_all():
    """The drop, on the frames: the species is off the row, so the page carries no note at any t."""
    row = [_note(at=8.0), _recast(at=8.0, dur=RC_S)]
    _stamped, _clamped, dropped = B.stamp_page_leave(row)
    assert len(dropped) == 1 and all(e["kind"] != "note" for e in row)
    at, errs, close = _leave_player(row)
    try:
        for t in (4.0, 8.0, 9.0, 12.0):
            assert at(t)["note"] is None, ("no note element was ever built", t)
        assert not errs, errs
    finally:
        close()
