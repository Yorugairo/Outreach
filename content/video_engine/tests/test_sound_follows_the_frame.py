"""P72 T20 - THE SOUND FOLLOWS THE FRAME (E99 s116; E81; BACKLOG R26-286, R26-329, R26-35, R26-36, R26-363).

What this file holds the kit (`authoring.audio`) to:

  (1) THE SUCK FIRES WHERE THE ENGINE PLAYS IT   a row whose exit reads `suck:<x>,<y>` arrives on the cut and the OUTGOING
                            world collapses into the point over the engine's SUCK_S (scene-evidence-engine.mjs: `su =
                            (t - sc.span[0]) / SUCK_S` on the scene CARRYING the exit). `fired` booked it at that scene's
                            END, so a suck cue on the true instant was DROPPED (R26-286's second half).
  (2) EVERY SUCK HAS A CUE  `suck_cues` names one `suck N` cue per suck row, on the row's start (the Tokyo map's own
                            reading), with the sound and the gain the door chooses - refused by name when malformed.
  (3) A SLOT HAND-OFF'S LANDING IS WHERE THE CARD IS FIRST SEEN   the engine paints ONE card per slot, the first live one
                            (`live.find(x => x.slot === s)`), and an outgoing card stays live EXIT (0.72 s) past its exit -
                            so the incoming card is first painted then, already settled. Its landing (and the cue the
                            binder moves onto it, s116) is that first frame, not the land's contact 0.32 s after the enter.
  (4) THE BED SWELL ON THE CAMERA ARRIVAL (R26-35, checked, never re-rendered - E45): the kit's default envelope holds
                            Tokyo's swell through the camera arrival; the approved cut's recorded plan keeps its pin.
  (5) R26-36's ONE ASSERTION  a `:cut;then=` / `;idle=` page IS a cut to the compiler, and `page_transitions` keeps the
                            legacy raw-suffix reading (`LEGACY_SUFFIX_OPTS`) for the shipped plans - OPEN until a listened pass.
  (6) E81's START (R26-363)  each landing cue measured and started 8-10 dB under the voice through `e81_gain`.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

from authoring import audio as A  # noqa: E402
import build_scene_timeline_f as C  # noqa: E402

FRAME = 1 / A.FPS
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
TOKYO_PLAN = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/sound/SOUND-PLAN.json"


def _page(exit_="cut") -> dict:
    return {"builder": "dense-line", "variant": "line", "enter": "axes", "exit": exit_}


def _scene(sid, t0, t1, docks=(), exit_="cut", page=True) -> dict:
    world = {"kind": "ledger", "page": _page()} if page else {"kind": "plate", "asset_id": "world-desk"}
    return {"scene_id": sid, "span": [t0, t1], "world": world, "docks": list(docks), "exit": exit_}


def _timeline(*scenes, evidence=None) -> dict:
    return {"scenes": list(scenes), "evidence": dict(evidence or {})}


def _cue(slot, at, **extra) -> dict:
    return {"slot": slot, "at": at, "gain": 0.12, "fade_in": 0.0, "variants": {"A": "x.mp3"}, **extra}


def _frame_ceil(t: float) -> float:
    return math.ceil(t * A.FPS - 1e-9) / A.FPS


# ---------------------------------------------------------------- (1) the suck fires where the engine plays it

# H row 17 -> 17b's shape: a page, then a plate whose exit sucks the page into a point of the desk
SUCKED = _timeline(_scene("s01", 0.0, 12.0),
                   _scene("s02", 12.0, 37.0, exit_="suck:0.345,0.58", page=False),
                   _scene("s03", 37.0, 50.0, exit_="dip", page=False))


def test_the_suck_is_read_off_the_engine_not_retyped():
    text = ENGINE.read_text(encoding="utf-8")
    assert "const SUCK_S = %g" % A.suck_s() in text
    assert "const EXIT = %g" % A.dock_exit_s() in text
    assert "const DOCK_JOIN = %g" % A.dock_join_s() in text


def test_the_suck_fires_at_the_start_of_the_scene_carrying_it_over_suck_s():
    sucks = [f for f in A.fired(SUCKED) if f["kind"] == A.SUCK]
    assert sucks == [{"kind": "suck", "what": "suck", "at": 12.0, "until": round(12.0 + A.suck_s(), 2),
                      "scene": "s02", "ref": "suck:0.345,0.58"}], sucks


def test_a_suck_cue_on_its_rows_start_is_bound_and_one_on_the_scenes_end_is_dropped():
    on_row = _cue("suck 2", 12.0)
    kept, dropped = A.bind_cues([on_row], SUCKED)
    assert kept == [on_row] and not dropped, "the Tokyo map's reading (`suck N` at r[0]) is what the frame plays"
    late = _cue("suck 2", 37.0)
    kept, dropped = A.bind_cues([late], SUCKED)
    assert not kept and len(dropped) == 1 and "suck (suck)" in dropped[0]["why"]


def test_the_suck_no_longer_reads_as_silent_once_cued():
    def sucks(notes):
        return [n for n in notes if "suck" in n]
    assert sucks(A.unsounded([_cue("suck 2", 12.0)], SUCKED)) == []
    assert sucks(A.unsounded([], SUCKED)) == ["no cue mapped for suck (suck) at 12.00s on s02"]


# ---------------------------------------------------------------- (2) every suck row has a cue

WHOOSH_3 = "fs-whoosh-3-648729.mp3"   # the door's pick in the test bed (the kit names no file: the episode owns its files)

ROWS = [(0.0, 12.0, "ledger:ev-a:line:0:right:cut;idle=live", (0, 0, 0), [], None, []),
        (12.0, 37.0, "world-desk-v1;use=landing", (0, 0, 0), [], "suck:0.345,0.58", []),
        (37.0, 50.0, "world-desk-v1", (0, 0, 0), [], "dip", []),
        (50.0, 60.0, "world-slate-v1", (0, 0, 0), [], "suck:0.49,0.31", [])]


def test_suck_cues_names_one_cue_per_suck_row_on_its_start():
    cues = A.suck_cues(ROWS, {"A": WHOOSH_3}, 0.09)
    assert [(c["slot"], c["at"]) for c in cues] == [("suck 2", 12.0), ("suck 4", 50.0)]
    assert all(c["variants"] == {"A": WHOOSH_3} and c["gain"] == 0.09 and c["fade_in"] == 0.0 for c in cues)


def test_suck_cues_are_what_the_binder_keeps():
    tl = _timeline(*[_scene("s%02d" % (i + 1), r[0], r[1], exit_=r[5] or "cut", page=i == 0) for i, r in enumerate(ROWS)])
    cues = A.suck_cues(ROWS, {"A": WHOOSH_3}, 0.09)
    kept, dropped = A.bind_cues(cues, tl)
    assert kept == cues and not dropped
    assert not [n for n in A.unsounded(cues, tl) if "suck" in n]


@pytest.mark.parametrize("variants, gain, needle", [({}, 0.09, "variants"), ({"A": ""}, 0.09, "variants"),
                                                    ({"A": WHOOSH_3}, 0.0, "gain"), ({"A": WHOOSH_3}, 1.5, "gain")])
def test_suck_cues_refuse_a_malformed_sound_by_name(variants, gain, needle):
    with pytest.raises(ValueError, match=needle):
        A.suck_cues(ROWS, variants, gain)


# ---------------------------------------------------------------- (3) a slot hand-off's landing is where the card is seen

# H row 23's shape: cards handed one to the next in ONE slot, each exit = the next enter
HANDOFF = _timeline(_scene("s01", 0.0, 40.0, page=False, docks=[
    {"slide": "dock-index", "slot": 1, "enter": 10.0, "exit": 17.58, "arrive": "land", "mass": "paper"},
    {"slide": "dock-test", "slot": 1, "enter": 17.58, "exit": 22.45, "arrive": "land", "mass": "paper"}]))
# ... and the same two cards, the second in the OTHER slot: nothing holds its slot
FREE = _timeline(_scene("s01", 0.0, 40.0, page=False, docks=[
    {"slide": "dock-index", "slot": 1, "enter": 10.0, "exit": 17.58, "arrive": "land", "mass": "paper"},
    {"slide": "dock-free", "slot": 0, "enter": 17.58, "exit": 22.45, "arrive": "land", "mass": "paper"}]))


def _fire(tl, ref):
    return next(f for f in A.fired(tl) if f["kind"] == "landing" and f["ref"] == ref)


def test_a_handed_on_card_is_first_seen_when_the_outgoing_card_leaves_the_slot():
    seen = A.first_seen(HANDOFF, "dock-test", 17.58)
    assert seen == _frame_ceil(17.58 + A.dock_exit_s()), seen      # 18.3333: the engine's first painted frame


def test_the_hand_off_landing_fires_on_that_frame_not_on_the_lands_contact():
    contact = A.landing_contact(17.58, "land", A.stop_dials())
    fire = _fire(HANDOFF, "dock-test")
    assert fire["at"] == 18.33, "17.58 + EXIT 0.72 = 18.30, the next frame 18.3333 - not the contact 17.90"
    assert fire["at"] == round(A.first_seen(HANDOFF, "dock-test", 17.58), 2) > round(contact, 2) + FRAME


def test_the_hand_off_cue_is_moved_within_one_frame_of_the_cards_first_frame():
    contact = A.landing_contact(17.58, "land", A.stop_dials())
    cue = _cue("landing 1 (land, paper)", round(contact - FRAME, 2))    # the door's cue: the contact, one frame early
    kept, dropped = A.bind_cues([cue], HANDOFF)
    assert not dropped
    seen = A.first_seen(HANDOFF, "dock-test", 17.58)
    assert abs(kept[0]["at"] - seen) <= FRAME, (kept[0]["at"], seen)
    assert kept[0][A.RETIMED_KEY]["from"] == cue["at"]


@pytest.mark.parametrize("freed, painted", [(754.49, 18125 / 24), (784.82, 18854 / 24)])
def test_the_first_frame_is_the_one_the_render_seeks_through_the_scrubber(freed, painted):
    """H rows 25 and 26 (frames/moves-sheet.png): the render seeks f / 24 through `#scrub` (step 0.01), so a card freed at
    755.21 is painted on 755.2083 (seeked at 755.21) and one freed at 785.54 on 785.5833 (785.5417 seeks 785.54, still held)."""
    tl = _timeline(_scene("s01", 700.0, 800.0, page=False, docks=[
        {"slide": "dock-a", "slot": 1, "enter": freed - 5.0, "exit": freed, "arrive": "land"},
        {"slide": "dock-b", "slot": 1, "enter": freed, "exit": freed + 5.0, "arrive": "land"}]))
    assert A.first_seen(tl, "dock-b", freed) == painted


def test_a_card_with_its_slot_free_keeps_its_contact():
    contact = round(A.landing_contact(17.58, "land", A.stop_dials()), 2)
    assert _fire(FREE, "dock-free")["at"] == contact                 # slot 0: nobody before it
    assert _fire(HANDOFF, "dock-index")["at"] == round(A.landing_contact(10.0, "land", A.stop_dials()), 2)
    assert A.first_seen(FREE, "dock-free", 17.58) == 17.58


def test_a_press_card_and_a_slotless_dock_never_hold_a_slot():
    tl = _timeline(_scene("s01", 0.0, 40.0, page=False, docks=[
        {"slide": "dock-press", "slot": 1, "enter": 10.0, "exit": 17.58, "kind": "press"},
        {"slide": "dock-test", "slot": 1, "enter": 17.58, "exit": 22.45, "arrive": "land"}]))
    assert A.first_seen(tl, "dock-test", 17.58) == 17.58
    loose = _timeline(_scene("s01", 0.0, 40.0, page=False, docks=[
        {"slide": "dock-a", "enter": 10.0, "exit": 17.58, "arrive": "land"},
        {"slide": "dock-b", "enter": 17.58, "exit": 22.45, "arrive": "land"}]))
    assert A.first_seen(loose, "dock-b", 17.58) == 17.58


def test_a_handed_prop_leaves_its_slot_on_its_word():
    tl = _timeline(_scene("s01", 0.0, 40.0, page=False, docks=[
        {"slide": "prop-a", "slot": 1, "enter": 10.0, "exit": 17.58, "arrive": "stamp", "handed": "morph"},
        {"slide": "dock-b", "slot": 1, "enter": 17.58, "exit": 22.45, "arrive": "land"}]))
    assert A.first_seen(tl, "dock-b", 17.58) == 17.58


def test_the_engines_boundary_snap_holds_the_outgoing_card_to_the_turn():
    """a card exiting 0.05-1.4 s before a scene turn is held to the turn (engine :7661) - and the slot with it."""
    tl = _timeline(_scene("s01", 0.0, 18.0, page=False, docks=[
        {"slide": "dock-a", "slot": 1, "enter": 10.0, "exit": 17.0, "arrive": "land"},
        {"slide": "dock-b", "slot": 1, "enter": 17.2, "exit": 22.0, "arrive": "land"}]),
        _scene("s02", 18.0, 40.0, page=False))
    assert A.first_seen(tl, "dock-b", 17.2) == _frame_ceil(18.0 + A.dock_exit_s())


def test_a_card_whose_slot_never_frees_is_never_seen():
    tl = _timeline(_scene("s01", 0.0, 40.0, page=False, docks=[
        {"slide": "dock-a", "slot": 1, "enter": 10.0, "exit": 30.0, "arrive": "land"},
        {"slide": "dock-b", "slot": 1, "enter": 12.0, "exit": 20.0, "arrive": "land"}]))
    assert A.first_seen(tl, "dock-b", 12.0) is None
    assert _fire(tl, "dock-b")["at"] == round(A.landing_contact(12.0, "land", A.stop_dials()), 2), \
        "a card the frame never shows keeps its contact - the binder never invents an instant"


def test_a_same_slide_re_authored_within_dock_join_is_one_card():
    tl = _timeline(_scene("s01", 0.0, 10.0, page=False, docks=[
        {"slide": "dock-a", "slot": 1, "enter": 2.0, "exit": 10.0, "arrive": "land"}]),
        _scene("s02", 10.0, 30.0, page=False, docks=[
            {"slide": "dock-a", "slot": 1, "enter": 10.0, "exit": 16.0, "arrive": "land"},
            {"slide": "dock-b", "slot": 1, "enter": 16.0, "exit": 22.0, "arrive": "land"}]))
    assert A.first_seen(tl, "dock-b", 16.0) == _frame_ceil(16.0 + A.dock_exit_s())


# ---------------------------------------------------------------- (4) the bed swell on the camera arrival (R26-35)

# Tokyo's recorded rows 8-9 (tokyo-tea-break/SHOT-TABLE-SHORT.py): the fed card thrown at 75.79, the page arriving by
# `:camera=` on it at 76.83 (the camera arrival's clock: build_scene_timeline_f.CAMERA_ARRIVAL_S)
TOKYO_ROWS = [(61.76, 76.83, "ledger:ev-meta-yield-v1:bars:3:right:mount=2.43:cut", (0, 0, 0),
               [("dock-h-fed-vs-yields", 0, 75.79, 76.83, {"arrive": "throw", "mass": "paper"})], None, []),
              (76.83, 82.623, "ledger:ev-fed-vs-yields-v1:line:0:right:camera=dock-h-fed-vs-yields:cut", (0, 0, 0),
               [], "cut", [])]
TOKYO_SWELL = (4.0, 0.45)     # build_short.py BED_SWELL_DB, SNAP_S_BED


def test_the_kits_envelope_holds_tokyos_swell_through_the_camera_arrival():
    env = A.bed_envelope(TOKYO_ROWS, *TOKYO_SWELL, fallback_end=lambda d: float(d[2]) + 1.2)
    t_cam = 76.83
    assert A.swell_holds(env, TOKYO_SWELL[0], t_cam, t_cam + C.CAMERA_ARRIVAL_S), env


def test_tokyos_recorded_plan_keeps_its_pin_and_misses_the_arrival_as_recorded():
    """E45 / acceptance (4): the approved cut is frozen - its plan still carries the throw + 1.2 s fallback."""
    plan = json.loads(TOKYO_PLAN.read_text(encoding="utf-8"))
    turn = next(c for c in plan["cues"] if c["slot"] == "turn bed")
    assert turn["env"] == [[75.49, 0.0], [75.79, 4.0], [76.99, 4.0], [77.79, 0.0]]
    pinned = A.bed_envelope(TOKYO_ROWS, *TOKYO_SWELL, fallback_end=lambda d: float(d[2]) + 1.2, snap_keys=(":snap=",))
    assert pinned == turn["env"]
    assert not A.swell_holds(turn["env"], TOKYO_SWELL[0], 76.83, 76.83 + C.CAMERA_ARRIVAL_S)


def test_swell_holds_reads_the_envelope_as_the_player_does():
    env = [[1.0, 0.0], [1.3, 4.0], [3.0, 4.0], [3.8, 0.0]]
    assert A.swell_holds(env, 4.0, 1.3, 3.0)
    assert not A.swell_holds(env, 4.0, 1.2, 3.0)
    assert not A.swell_holds(env, 4.0, 1.3, 3.1)
    assert not A.swell_holds([], 4.0, 1.3, 3.0)


# ---------------------------------------------------------------- (5) R26-36's one assertion - OPEN until a listened pass

# two of the committed H door's own rows (lane A build-h/SHOT-TABLE-H.py, 2026-09-25)
H_CUT_THEN = ("ledger:ev-divergence-v1:line:234:right:spiral:cut;idle=live;domain=80,277",
              "ledger:ev-railway-index-v1:line:139:right:axes:cut;idle=live;then=ev-equip-ipp-gdp-v2:line;"
              "then=ev-divergence-v1:line")


@pytest.mark.parametrize("plate", H_CUT_THEN)
def test_a_cut_then_row_is_a_cut_to_the_compiler_and_the_legacy_reading_is_kept(plate):
    bare, _opts = C.split_plate_opts(plate)
    assert bare.endswith(":cut"), "the compiler reads the page as leaving on the cut"
    assert A.page_transitions(plate)["cut"] is False, "LEGACY_SUFFIX_OPTS: the shipped plans' raw-suffix reading stands"
    assert A.LEGACY_SUFFIX_OPTS == ("then", "idle")


# ---------------------------------------------------------------- (6) E81's start for each landing cue (R26-363)

# MEASURED 2026-09-25 (ffmpeg ebur128, integrated - P70 T8's level.log method; p72-t20 logs/levels.json): the H take and the
# accent files its door cues, from steel-and-paper/sound/
VO_H = -28.1
ACCENTS = {"fs-page-stroke-447925.mp3": (-14.4, -32.8), "fs-page-roll-464302.mp3": (-14.0, -32.4),
           "fs-whoosh-3-648729.mp3": (-16.2, -34.6), "fs-whoosh-1-706679.mp3": (-14.0, -32.4)}   # (file, the cue at 0.12)


def test_accent_level_predicts_the_measured_cue_at_a_gain():
    for name, (file_lufs, at_012) in ACCENTS.items():
        assert A.accent_level(VO_H, file_lufs, 0.12)["cue"] == pytest.approx(at_012, abs=0.1), name


def test_every_accent_started_at_e81_sits_nine_db_under_the_voice():
    for name, (file_lufs, _at) in ACCENTS.items():
        level = A.accent_level(VO_H, file_lufs, A.e81_gain(VO_H, file_lufs))
        assert level["under_db"] == pytest.approx(A.E81_UNDER_DB, abs=0.05), (name, level)


def test_the_shared_landing_gain_is_a_departure_from_e81():
    """R26-363's measurement: 0.12 puts the page stroke 4.7 dB and the page roll 4.3 dB under the voice, not 8-10."""
    lo, _hi = A.E81_RANGE_DB
    for name in ("fs-page-stroke-447925.mp3", "fs-page-roll-464302.mp3"):
        assert A.accent_level(VO_H, ACCENTS[name][0], 0.12)["under_db"] < lo, name
