"""P69 T84 / E99 s116 - A LANDING'S SOUND IS TIMED BY THE LANDING ITSELF.

The operator (2026-09-24): *"shouldn't the sound of the stamps be associated by the time of the stamp themselves, if
not directly called by the stamp itself?"* The cue plan names WHICH sound; the compiled landing says WHEN. What this
file holds the binder (`authoring.audio.bind_report` / `bind_cues`) to:

  (1) A KEPT LANDING CUE PLAYS ON ITS CONTACT   a `landing` cue the binder pairs with a compiled landing (throw, land,
                            stamp) takes that landing's contact as its instant - unless it already sits on the contact
                            or one frame early (the weight report's Q5 lead, `landing_contact`'s docstring), which it
                            keeps. Every move is REPORTED (`bind_report(...)["retimed"]`, `retimed(...)`).
  (2) NOTHING ELSE CHANGES  what is dropped, which fire a cue binds to, the kept list's order, and every cue that is
                            not a bound landing (a page enter, a bed, a press) are exactly what they were.
  (3) THE RACK              P69 T81's finding: a stamp whose enter the compiler moves (`after`) left the door's cue,
                            derived from the tuple's enter, 0.4 s before the contact - the binder puts it ON the contact.
  (4) THE WRITERS           `lab_build.bind_embedded_cues` writes the moved instant into the timeline's `sound` AND the
                            private plan, and names the move; a build with nothing to move is written as it was.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import lab_build as LB  # noqa: E402
from authoring import audio as A, docks as D, words as W  # noqa: E402

FRAME = 1 / A.FPS


def _scene(sid, t0, t1, docks=(), page=None) -> dict:
    page = page or {"builder": "dense-line", "variant": "line", "enter": "axes", "exit": "cut"}
    return {"scene_id": sid, "span": [t0, t1], "world": {"page": dict(page)}, "docks": list(docks), "exit": "cut"}


def _timeline(*scenes) -> dict:
    return {"scenes": list(scenes), "evidence": {}}


def _cue(slot, at, **extra) -> dict:
    return {"slot": slot, "at": at, "gain": 0.12, "fade_in": 0.0, "variants": {"A": "x.mp3"}, **extra}


# one of each weighted arrival on row 1 (scene s01), far enough apart that no two share a tolerance
THREE = _timeline(_scene("s01", 0.0, 30.0, docks=[
    {"slide": "prop-a", "enter": 2.0, "exit": 6.0, "arrive": "stamp"},
    {"slide": "dock-b", "enter": 10.0, "exit": 14.0, "arrive": "throw"},
    {"slide": "dock-c", "enter": 20.0, "exit": 24.0, "arrive": "land"}]))


def _contact(timeline, what) -> float:
    return next(f["at"] for f in A.fired(timeline) if f["kind"] == "landing" and f["what"] == what)


# ---------------------------------------------------------------- (1) a kept landing cue plays on its contact

def test_a_stamp_cue_off_its_contact_is_moved_onto_it_and_the_move_is_reported():
    contact = _contact(THREE, "stamp")
    stale = _cue("landing 1 (stamp, ink)", round(contact - 0.43, 2))
    kept, dropped = A.bind_cues([stale], THREE)
    assert not dropped and len(kept) == 1
    assert kept[0]["at"] == contact, "the compiled stamp says WHEN"
    assert kept[0]["variants"] == stale["variants"] and kept[0]["gain"] == stale["gain"], "the plan says WHICH"
    assert stale["at"] == round(contact - 0.43, 2), "the caller's cue is never mutated"
    moves = A.bind_report([stale], THREE)["retimed"]
    assert moves == [{"slot": "landing 1 (stamp, ink)", "what": "stamp", "scene": "s01",
                      "from": round(contact - 0.43, 2), "to": contact}], moves
    assert A.retimed([stale], THREE) == moves


def test_every_weighted_landing_takes_its_own_contact_throw_land_and_stamp():
    cues = [_cue("landing 1 (stamp, ink)", round(_contact(THREE, "stamp") - 0.5, 2)),
            _cue("landing 1 (throw, paper)", round(_contact(THREE, "throw") + 0.6, 2)),
            _cue("landing 1 (land, paper)", round(_contact(THREE, "land") - 1.2, 2))]
    kept, dropped = A.bind_cues(cues, THREE)
    assert not dropped
    assert [c["at"] for c in kept] == [_contact(THREE, w) for w in ("stamp", "throw", "land")]
    assert len(A.retimed(cues, THREE)) == 3


def test_a_late_cue_is_moved_back_onto_the_contact_a_landing_never_sounds_after_it_lands():
    contact = _contact(THREE, "throw")
    kept, _dropped = A.bind_cues([_cue("landing 1 (throw, paper)", round(contact + 3 * FRAME, 2))], THREE)
    assert kept[0]["at"] == contact


def test_a_cue_on_the_contact_or_one_frame_early_keeps_its_instant_and_is_not_reported():
    for what in ("stamp", "throw", "land"):
        contact = _contact(THREE, what)
        for at in (contact, round(contact - FRAME, 2)):
            cue = _cue(f"landing 1 ({what})", at)
            kept, dropped = A.bind_cues([cue], THREE)
            assert kept == [cue] and not dropped, (what, at)
            assert A.retimed([cue], THREE) == [], (what, at)


def test_two_frames_early_is_not_the_lead_and_is_moved():
    contact = _contact(THREE, "stamp")
    kept, _dropped = A.bind_cues([_cue("landing 1 (stamp, ink)", round(contact - 2 * FRAME, 2))], THREE)
    assert kept[0]["at"] == contact, "the weight report Q5: on the frame or one early, never two ahead"


def test_the_moved_cue_names_where_it_came_from_and_a_second_binding_moves_nothing():
    contact = _contact(THREE, "stamp")
    kept, _dropped = A.bind_cues([_cue("landing 1 (stamp, ink)", round(contact - 0.43, 2))], THREE)
    assert kept[0][A.RETIMED_KEY]["from"] == round(contact - 0.43, 2)
    assert kept[0][A.RETIMED_KEY]["to"] == contact
    again, dropped = A.bind_cues(kept, THREE)
    assert again == kept and not dropped and A.retimed(kept, THREE) == [], "binding is idempotent"


# P70 T8: THE POOF'S SOUND - its cue is a landing too (`WEIGHTED_ARRIVALS`), named with its mass, and it plays on the
# poof's own contact (the enter + POOF.EJECT_S, the burst leaving the prop) - the plan names the whoosh, the poof its instant
POOF_TL = _timeline(_scene("s01", 0.0, 30.0, docks=[
    {"slide": "prop-ibeam", "enter": 10.81, "exit": 20.0, "arrive": "poof", "kind": "prop"}]))


def test_a_poof_cue_authored_a_third_of_a_second_off_moves_onto_the_poofs_contact():
    contact = _contact(POOF_TL, "poof")
    assert contact == round(10.81 + A.poof_contact_s(), 2), "the poof's contact is its burst, not a landing's drop"
    stale = _cue("landing 1 (poof, paper)", round(contact + 0.3, 2), variants={"A": "fs-whoosh-1-706679.mp3"})
    kept, dropped = A.bind_cues([stale], POOF_TL)
    assert not dropped and kept[0]["at"] == contact
    assert kept[0]["variants"] == {"A": "fs-whoosh-1-706679.mp3"}, "the plan says WHICH"
    assert A.retimed([stale], POOF_TL) == [{"slot": "landing 1 (poof, paper)", "what": "poof", "scene": "s01",
                                            "from": round(contact + 0.3, 2), "to": contact}]
    early = _cue("landing 1 (poof, paper)", round(contact - 0.3, 2))
    assert A.bind_cues([early], POOF_TL)[0][0]["at"] == contact, "... from either side"


def test_a_poof_cue_on_its_contact_or_one_frame_early_is_kept_and_a_metal_cue_does_not_play_over_it():
    contact = _contact(POOF_TL, "poof")
    assert contact == round(10.81 + A.poof_contact_s(), 2)
    for at in (contact, round(contact - FRAME, 2)):
        cue = _cue("landing 1 (poof, paper)", at)
        assert A.bind_cues([cue], POOF_TL) == ([cue], [])
    kept, dropped = A.bind_cues([_cue("landing 1 (poof, metal)", contact)], POOF_TL)
    assert not kept and "lands paper" in dropped[0]["why"], "a poof names its mass: paper unless the row says otherwise"


# ---------------------------------------------------------------- (2) nothing else changes

def test_a_page_cue_off_its_instant_is_kept_where_it_was():
    cue = _cue("page enter 1 (axes)", 0.6)
    kept, dropped = A.bind_cues([cue], THREE)
    assert kept == [cue] and not dropped and A.retimed([cue], THREE) == []


def test_a_bed_and_a_press_are_untouched():
    cues = [{"slot": "hook bed", "at": 0.0, "gain": 0.1}, _cue("press 3", 4.0), _cue("dip 2", 9.3)]
    kept, dropped = A.bind_cues(cues, THREE)
    assert kept == cues and not dropped


def test_the_drop_and_the_pairing_are_the_ones_the_cue_own_instant_chose():
    """Retiming runs AFTER the nearest-first, consume-once pairing, on the cue's authored instant: two paper
    landings 1.0 s apart and two cues each nearer its own - both kept, each moved onto ITS fire; a third cue is
    still the one left over and is dropped with the same why."""
    two = _timeline(_scene("s01", 0.0, 10.0, docks=[
        {"slide": "dock-a", "enter": 2.0, "exit": 6.0, "arrive": "throw", "mass": "paper"},
        {"slide": "dock-b", "enter": 3.0, "exit": 7.0, "arrive": "throw", "mass": "paper"}]))
    first, second = [f["at"] for f in A.fired(two) if f["kind"] == "landing"]
    cues = [_cue("landing 1 (throw, paper)", round(second + 0.2, 2)),
            _cue("landing 1 (throw, paper)", round(first - 0.2, 2)),
            _cue("landing 1 (throw, paper)", round((first + second) / 2, 2))]
    kept, dropped = A.bind_cues(cues, two)
    assert [c["at"] for c in kept] == [second, first], "each cue lands on the fire it bound to, in the list's order"
    assert len(dropped) == 1 and dropped[0]["at"] == round((first + second) / 2, 2)
    assert "already bound" in dropped[0]["why"]
    assert A.unsounded(kept, two) == A.unsounded(cues[:2], two), "the silent fires are the same fires"


def test_bind_cues_keeps_its_two_tuple_and_bind_report_names_the_instant_each_kept_cue_plays():
    contact = _contact(THREE, "stamp")
    out = A.bind_cues([_cue("landing 1 (stamp, ink)", 1.8)], THREE)
    assert isinstance(out, tuple) and len(out) == 2
    row = A.bind_report([_cue("landing 1 (stamp, ink)", 1.8)], THREE)["cues"][0]
    assert row["at"] == 1.8 and row["plays"] == contact, "`at` stays the authored instant; `plays` is the contact"


# ---------------------------------------------------------------- (3) the rack (P69 T81's finding)

# the H take around row 21's rack: "... going into racks that are already under construction."
RACK_WS = [{"w": w, "start_s": s, "end_s": e} for w, s, e in (
    ("is", 585.58, 585.70), ("going", 585.70, 585.98), ("into", 585.98, 586.21), ("racks", 586.21, 586.62),
    ("that", 586.62, 586.80), ("are", 586.80, 586.95))]


def test_the_rack_stamped_after_racks_sounds_on_its_compiled_contact():
    """The door derives the cue from the tuple's enter (the word's onset, 586.21 s: contact - 1 frame = 586.32 s);
    the compiler moves the enter so the contact lands after "racks" ends (`words.after` + `docks.stamp_enter`). The
    binder binds the stale cue (within CUE_TOL_S) and plays it on the contact the compiled stamp lands on."""
    tuple_enter = 586.21
    door_cue = round(A.landing_contact(tuple_enter, "stamp", A.stop_dials()) - FRAME, 2)
    assert door_cue == 586.32
    # the compiler form (`after: "racks"`, searched at or after the tuple's enter - resolve_stamp_after)
    enter = D.stamp_enter(W.after(RACK_WS, "racks", from_s=tuple_enter))
    compiled = _timeline(_scene("s21", 530.0, 600.0, docks=[
        {"slide": "prop-ai-server-rack-cabinet-v1", "enter": enter, "exit": 598.0, "arrive": "stamp"}]))
    contact = _contact(compiled, "stamp")
    assert contact > 586.62, "the contact lands after the word"
    kept, dropped = A.bind_cues([_cue("landing 21 (stamp, ink)", door_cue)], compiled)
    assert not dropped and kept[0]["at"] == contact
    assert A.retimed([_cue("landing 21 (stamp, ink)", door_cue)], compiled)[0]["from"] == 586.32


# ---------------------------------------------------------------- (4) the writers

def _build(tmp_path, cues, timeline) -> tuple[Path, Path]:
    tl = dict(timeline, sound=[dict(c) for c in cues])
    (tmp_path / "t.timeline.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")
    plan = tmp_path / "SOUND-PLAN.json"
    plan.write_text(json.dumps({"cues": [dict(c) for c in cues]}, indent=1), encoding="utf-8")
    return tmp_path / "t.timeline.json", plan


def test_bind_embedded_cues_writes_the_moved_instant_into_the_timeline_and_the_plan_and_names_it(tmp_path):
    contact = _contact(THREE, "stamp")
    tl_path, plan = _build(tmp_path, [_cue("landing 1 (stamp, ink)", 1.8)], THREE)
    notes = LB.bind_embedded_cues(tmp_path, plan, tl_path.name)
    assert json.loads(tl_path.read_text(encoding="utf-8"))["sound"][0]["at"] == contact
    assert json.loads(plan.read_text(encoding="utf-8"))["cues"][0]["at"] == contact
    assert any("P69 T84 retimed" in n and "landing 1 (stamp, ink)" in n and "1.80s" in n
               and f"{contact:.2f}s" in n for n in notes), notes


def test_bind_embedded_cues_leaves_a_timeline_with_nothing_to_move_byte_for_byte(tmp_path):
    contact = _contact(THREE, "stamp")
    tl_path, plan = _build(tmp_path, [_cue("landing 1 (stamp, ink)", round(contact - FRAME, 2))], THREE)
    before = tl_path.read_bytes()
    assert LB.bind_embedded_cues(tmp_path, plan, tl_path.name) == []
    assert tl_path.read_bytes() == before
