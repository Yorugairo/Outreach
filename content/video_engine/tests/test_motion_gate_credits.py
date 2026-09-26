"""P72 T7 - the motion gate credits what moves, and only what the frame shows moving.

Six items, one row each (the "frames inward, not tokens outward" lesson: every credit below is a thing the player
PAINTS at that instant, read off the engine's own clock, and each was checked on a rendered frame before it was
written here - the slice's NOTES.md names the instants):

  R26-326  the VERDICT STACK's beats (species/verdict.mjs): each proof's flight in from depth and its landing, each
           recede to the rail, the gather (the vertical form) and each card's burst - the gate saw ONE host-dock enter
           and FAILed M01 / M05 / M08 on H row 23 for want of events (13.7 s "with no visual event" at 11:35).
  R26-269  a RECORD's typing (species/record.mjs paintRecord): every word appears on its own onset and the paper's two
           feet land after the quotation's end - on `world-internal-memo-v1` the typing earned 0 events.
  R26-167  `--beat t0,t1`: a test-bed beat is judged on its OWN window for M11 - the episode's first-chart window
           (0:08-0:20, E24) is an opening's rule, never a beat's.
  R26-189  M50, the FLOW READ (E99 s74 Apply 3): every cut and every dip, each with the transform it refused, or
           `refused: (unnamed)` where the timeline carries no reason.
  R26-132 (2) a card at a DEPTH rides the camera past the frame: M24 names a settled depth card that a camera landing
           carries off an edge, with the overshoot in px (a WARN - s106 (4): "cut by the frame" is a fit finding).
  R26-202 (a) M27 judges a card AT REST: a thrown card's flight frames are its path - listed, never a FAIL.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import gate_motion_density as G  # noqa: E402

GOLDEN = ROOT / "content/video_engine/tests/golden/sources"
EP1 = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f"
needs_ep1 = pytest.mark.skipif(not (EP1 / "steel-and-paper.timeline.json").exists(), reason="episode one build not on disk")


def _by_id(gates) -> dict:
    return {g.id: g for g in gates}


# ------------------------------------------------------------------ the fixtures: H row 23's own numbers
# The stack as H row 23 authors it (build_episode_h.py VERDICT_ITEMS on the take, P69 T31): the host dock's window is
# `stack_entry`'s (0.5 s before the first proof, 1.0 s past the clear), the four proofs on their phrases.
STACK_ITEMS = [{"id": "dock-h-two-line-copy", "at": 696.49}, {"id": "dock-h-test-card", "at": 698.23},
               {"id": "dock-h-leases-record", "at": 701.36}, {"id": "dock-h-target-date-statement", "at": 705.6}]
STACK_CLEAR = 708.73
HOST = "dock-h-verdict-stack"


def _plate_timeline(docks: list[dict], span=(679.45, 716.79), species=(), aspect="16:9", caption_at=None) -> dict:
    """The picture plate carrying `docks`, after six-second filler scenes from 0:00 (each boundary an event, so the
    only stillness the gate can find is the plate's own). No page; the Ken Burns drift is not an event (doc 29 s8.19).
    `caption_at`: one caption page there, stamped `anchor` as the compiler stamps every page under a live dock."""
    filler = [{"scene_id": f"f{i:03d}", "span": [round(i * 6.0, 2), round(min((i + 1) * 6.0, span[0]), 2)],
               "world": {"asset_id": f"filler-{i}"}} for i in range(int(span[0] // 6.0) + 1) if i * 6.0 < span[0]]
    tl = {"aspect": aspect, "runtime_s": span[1],
          "scenes": filler + [{"scene_id": "s23", "span": list(span), "world": {"asset_id": "world-spike-certificate-ring-v2"},
                               "docks": docks, "species": list(species)}]}
    if caption_at is not None:
        tl["caption_pages"] = [{"s": caption_at, "t": [{"s": caption_at, "w": "Everything"}], "cap_mode": "anchor"}]
    return tl


# H row 23's other cards (the stack form's timeline): the certificate thrown and ringed, the railway index landed, both
# leaving just before the wall; the RAM stamped after it
ROW23_DOCKS = [{"slide": "dock-h-railway-share-ring", "slot": 1, "enter": 679.64, "exit": 695.89, "badge_at": [], "arrive": "throw"},
               {"slide": "dock-h-railway-index-card", "slot": 0, "enter": 688.91, "exit": 695.89, "badge_at": [], "arrive": "land"},
               {"slide": "prop-dram-memory-module-v1", "slot": 0, "enter": 711.52, "exit": 714.29, "badge_at": [], "arrive": "stamp"}]
ROW23_SPECIES = [{"kind": "callout", "at": 681.45, "dur": 6.66, "target": {"kind": "region", "x0": 0.1, "y0": 0.1, "x1": 0.3, "y1": 0.3}}]


def _stack_build(form: str | None = "16:9", aspect: str = "16:9"):
    host = {"slide": HOST, "slot": 0, "enter": 695.99, "exit": 709.73, "badge_at": []}
    payload = {"items": [dict(i) for i in STACK_ITEMS], "clear_at": STACK_CLEAR}
    if form:
        payload["form"] = form
    tl = _plate_timeline([dict(d) for d in ROW23_DOCKS] + [host], species=ROW23_SPECIES, aspect=aspect, caption_at=700.0)
    # the payload where the PLAYER reads it: the timeline's evidence map (engine fillDock, `TL.evidence[aid]`)
    tl["evidence"] = {HOST: {"species": "stack", "title": "Everything we checked holds", "badges": [], "stack": payload}}
    return tl, tl["evidence"]


# ------------------------------------------------------------------ R26-326: the verdict stack's beats
def test_the_stack_s_flights_recedes_and_burst_are_events_on_the_engine_s_own_clock() -> None:
    tl, meta = _stack_build()
    events, notes = G._stack_beats(tl["scenes"], meta, "16:9")
    assert notes == []
    # each proof ENTERS on its phrase and lands ENTER_S later (verdict.mjs VERDICT.ENTER_S 0.9) ...
    for it in STACK_ITEMS:
        assert it["at"] in events and round(it["at"] + 0.9, 2) in events
    # ... each hands the focus on at the NEXT proof's beat and is on the rail RECEDE_S later; the last recedes
    # LAST_RECEDE_LEAD (0.9) before the clear on the full frame, which keeps the reference's choreography (E99 s61)
    assert round(STACK_CLEAR - 0.9, 2) in events and round(STACK_CLEAR - 0.9 + 1.0, 2) in events
    assert round(698.23 + 1.0, 2) in events
    # ... and every card bursts BURST_STAGGER (0.06) after the one before, each throw BURST_S (0.5) long
    for i in range(len(STACK_ITEMS)):
        assert round(STACK_CLEAR + 0.06 * i, 2) in events and round(STACK_CLEAR + 0.06 * i + 0.5, 2) in events


def test_row_23_as_authored_no_longer_fails_m01_m05_m08_for_want_of_events() -> None:
    tl, meta = _stack_build()
    bare = dict(tl, evidence={HOST: {k: v for k, v in meta[HOST].items() if k != "stack"}})
    g = _by_id(G.run(bare, [], {"cues": []})[0])
    # the RED this slice was written against: the host dock is one enter and one exit, so 695.99 -> 709.73 is 13.7 s
    # "with no visual event"; without the payload that is still what the gate reads
    assert g["M01"].level == "FAIL" and "13.7s" in g["M01"].message, g["M01"].message
    g = _by_id(G.run(tl, [], {"cues": []})[0])
    for gid in ("M01", "M05", "M08"):
        assert g[gid].level != "FAIL", (gid, g[gid].message)
    ev = G.analyse(tl, [], {"cues": []})
    worst = max(d for a, d in ev["still"] if 695.99 <= a <= 709.73)
    assert worst < 3.5, worst   # the widest hold inside the wall: card 2's focus, 702.36 -> 705.6 (3.24 s)


def test_a_timeline_without_a_stack_reads_exactly_as_before() -> None:
    """The one-slot version (row 23 as it ships, VERDICT_STACK_ON = False) carries no `stack` payload: the credit is
    empty and the event list is the list the gate read before this slice, number for number."""
    tl, _meta = _stack_build()
    plain = dict(tl, evidence={HOST: {"species": "image", "title": "x", "badges": []}})
    assert G._stack_beats(plain["scenes"], plain["evidence"], "16:9") == ([], [])
    assert G.analyse(plain, [], {"cues": []})["events"] == G.analyse(dict(tl, evidence={}), [], {"cues": []})["events"]


def test_the_vertical_form_gathers_and_its_last_proof_never_recedes() -> None:
    tl, meta = _stack_build(form="9:16", aspect="9:16")
    events, _notes = G._stack_beats(tl["scenes"], meta, "9:16")
    # VERDICT_9X16: GATHER true - the wall draws in over GATHER_LEAD (0.9) before the clear, the last card holds the
    # centre (no recede), and the burst fires 0.035 apart over 0.42
    assert round(STACK_CLEAR - 0.9, 2) in events                 # the gather begins
    assert round(STACK_CLEAR - 0.9 + 1.0, 2) not in events       # no last recede on the gathering form
    assert round(STACK_CLEAR + 0.035 * 3, 2) in events and round(STACK_CLEAR + 0.035 * 3 + 0.42, 2) in events


def test_a_malformed_stack_payload_is_refused_by_name_and_credits_nothing() -> None:
    tl, meta = _stack_build()
    meta[HOST]["stack"]["items"] = "four proofs"
    events, notes = G._stack_beats(tl["scenes"], meta, "16:9")
    assert events == [] and notes and HOST in notes[0] and "items" in notes[0], notes
    stats = G.run(tl, [], {"cues": []})[1]
    assert any(HOST in str(v) and "refused" in str(v) for v in stats.values()), stats


def test_a_stack_whose_host_never_docks_credits_nothing() -> None:
    """The payload is the ENGINE's only when a dock mounts it: a meta entry with no timeline dock paints nothing."""
    tl, meta = _stack_build()
    tl["scenes"][-1]["docks"] = [d for d in tl["scenes"][-1]["docks"] if d["slide"] != HOST]
    assert G._stack_beats(tl["scenes"], meta, "16:9")[0] == []


# ------------------------------------------------------------------ R26-269: a record's typing
KARP_WORDS = [["“Something", 107.49], ["has", 107.59], ["gone", 107.69], ["wrong", 107.93], ["value.”", 110.95]]
KARP = "dock-h-karp-record"


def _record_build(enter=107.09, exit_=114.21, words=None, end=111.0):
    dock = {"slide": KARP, "slot": 0, "enter": enter, "exit": exit_, "badge_at": [], "arrive": "throw"}
    tl = _plate_timeline([dock], span=(104.31, 147.82))
    tl["evidence"] = {KARP: {"species": "record", "badges": [],
                             "record": {"words": words if words is not None else [list(w) for w in KARP_WORDS],
                                        "hl": [2, 3], "end": end, "attr": "Alex Karp", "src": "Palantir"}}}
    return tl, tl["evidence"]


def test_every_typed_word_and_the_paper_s_two_feet_are_events() -> None:
    tl, meta = _record_build()
    events, notes = G._record_beats(tl["scenes"], meta)
    assert notes == []
    assert [t for _w, t in KARP_WORDS] == [t for t in events if t <= 111.0]
    # the attribution at end + ATTR_AFTER (0.15), the source line at end + SRC_AFTER (0.45) - record.mjs RECORD
    assert 111.15 in events and 111.45 in events


def test_a_word_the_dock_is_not_on_stage_for_is_never_credited() -> None:
    tl, meta = _record_build(enter=107.8, exit_=110.0)
    events, _ = G._record_beats(tl["scenes"], meta)
    assert events == [107.93]   # before the enter nothing is painted; after the exit the card is gone


def test_the_memo_plate_s_typing_earns_events_without_the_steam() -> None:
    tl, _meta = _record_build()
    before = G.analyse(dict(tl, evidence={}), [], {"cues": []})["events"]
    after = G.analyse(tl, [], {"cues": []})["events"]
    typed = sorted(set(after) - set(before))
    assert typed == [107.49, 107.59, 107.69, 107.93, 110.95, 111.15, 111.45], typed


def test_malformed_record_words_are_refused_by_name() -> None:
    tl, meta = _record_build(words=[["gone", "later"]])
    events, notes = G._record_beats(tl["scenes"], meta)
    assert events == [] and notes and KARP in notes[0] and "words" in notes[0], notes


@needs_ep1
def test_ep1_keeps_every_fail_it_was_ruled_on_with_the_credits_counted() -> None:
    """E21: ep1 died of visual stillness - its record (s19, 3:46) and its approved nine-proof wall (s67, 11:41) now
    count, and not one FAIL level moves (neither window is inside a still stretch the ruling was made on)."""
    tl, docks, mp = G._load(EP1, "steel-and-paper.timeline.json")
    gates, stats = G.run(tl, docks, mp)
    g = _by_id(gates)
    assert G.fail_count(gates) == 9
    for gid in ("M01", "M03", "M05", "M07", "M08", "M10", "M11", "M12", "M44"):
        assert g[gid].level == "FAIL", (gid, g[gid].message)
    assert "credited_beats" in stats and "ev-holds-stack-v1" in stats["credited_beats"] and "ev-doc-karp" in stats["credited_beats"]


# ------------------------------------------------------------------ R26-167: a beat is judged on its own window
def _beat_bed(page_enter: float = 2.0, annotated: bool = True) -> dict:
    """A test-bed beat: a plate, then a ledger page entering 2 s into the window, spotlit as its build lands."""
    land = page_enter + G.PAGE_BUILD_END_S
    page = {"scene_id": "s02", "span": [page_enter, 15.0], "world": {"kind": "ledger", "page": {"builder": "story"}},
            "species": ([{"kind": "spotlight", "at": round(land + 0.2, 2), "dur": 1.5,
                          "target": {"kind": "region", "x0": 0.1, "y0": 0.1, "x1": 0.4, "y1": 0.4}}] if annotated else [])}
    return {"aspect": "16:9", "form": "long", "runtime_s": 15.0,   # a window of a LONG form (the test beds are)
            "scenes": [{"scene_id": "s01", "span": [0.0, page_enter], "world": {"asset_id": "plate-a"}}, page]}


def test_without_a_window_the_beat_fails_m11_on_the_episode_s_opening_rule() -> None:
    g = _by_id(G.run(_beat_bed(), [], {"cues": []})[0])
    assert g["M11"].level == "FAIL" and "outside 8-20s" in g["M11"].message, g["M11"].message


def test_with_beat_the_window_s_own_chart_is_judged_on_its_own_landing() -> None:
    g = _by_id(G.run(_beat_bed(), [], {"cues": []}, beat=(0.0, 15.0))[0])
    assert g["M11"].level in ("PASS", "WARN") and "beat 0.00-15.00" in g["M11"].message, g["M11"].message
    assert "outside" not in g["M11"].message


def test_a_beat_whose_chart_is_unannotated_still_fails_its_own_claim() -> None:
    g = _by_id(G.run(_beat_bed(annotated=False), [], {"cues": []}, beat=(0.0, 15.0))[0])
    assert g["M11"].level == "FAIL" and "unannotated" in g["M11"].message, g["M11"].message


def test_a_beat_that_carries_no_chart_is_not_failed_for_one() -> None:
    tl = _beat_bed()
    g = _by_id(G.run(tl, [], {"cues": []}, beat=(0.0, 1.9))[0])
    assert g["M11"].level == "INFO" and "no chart" in g["M11"].message, g["M11"].message


def test_the_cli_takes_the_window_and_refuses_a_malformed_one_by_name(tmp_path: Path, capsys) -> None:
    b = tmp_path / "bed"
    b.mkdir()
    (b / "bed.timeline.json").write_text(json.dumps(_beat_bed()), encoding="utf-8")
    G.main([str(b), "--beat", "0,15"])
    assert "beat 0.00-15.00" in capsys.readouterr().out
    for bad in ("15,0", "a,b", "3", "-1,4"):
        with pytest.raises(SystemExit):
            G.main([str(b), "--beat", bad])
        assert "--beat" in capsys.readouterr().err


# ------------------------------------------------------------------ R26-189: M50, the flow read
def _flow_timeline() -> dict:
    sc = lambda i, a, z, ex=None, why=None: {"scene_id": f"s{i:02d}", "span": [a, z], "world": {"asset_id": f"p{i}"},
                                             **({"exit": ex} if ex else {}), **({"exit_why": why} if why is not None else {})}
    return {"aspect": "16:9", "runtime_s": 60.0,
            "scenes": [sc(1, 0, 10, "cut"), sc(2, 10, 20, "dip"), sc(3, 20, 30, "melt:splash:plate:1"),
                       sc(4, 30, 40), sc(5, 40, 50, "dip",
                                         "TAKEN dip 7; refused: the melt's splash onto the plate (spent at 6:52)"),
                       sc(6, 50, 60, "blurzoom")]}


def test_m50_lists_every_cut_and_dip_with_the_transform_it_refused_or_unnamed() -> None:
    g = _by_id(G.run(_flow_timeline(), [], {"cues": []})[0])["M50"]
    assert g.level == "INFO", g
    assert "5 world change(s)" in g.message and "cuts+dips 3" in g.message, g.message
    assert "s02 dip at 0:10 refused: (unnamed)" in g.message
    assert "s04 cut at 0:30 refused: (unnamed)" in g.message     # no exit is the player's cut
    assert "s05 dip at 0:40 refused: the melt's splash onto the plate" in g.message
    assert "s03" not in g.message.split("|")[-1]                 # a melt is a transform, never listed as a cut


def test_a_malformed_exit_why_is_refused_by_name() -> None:
    tl = _flow_timeline()
    tl["scenes"][1]["exit_why"] = ["a", "list"]
    msg = _by_id(G.run(tl, [], {"cues": []})[0])["M50"].message
    assert "s02 dip at 0:10 refused: (malformed exit_why: list)" in msg, msg


# ------------------------------------------------------------------ R26-132 (2): a depth card at the landing
def _dock_depth() -> dict:
    return json.loads((GOLDEN / "dock-depth.timeline.json").read_text(encoding="utf-8"))


# MEASURED (probe.py --gate on the golden, warm): the gate's own instant for the card, `parked` at 6.95 - the focus zoom
# at 1.307 about (1480, 800), the card's box on screen. Its landing (7.11, 1.32) read directly: [1042, 526, 876, 632].
DEPTH_INSTANT = {"t": 6.95, "why": "s01 dock ev-quay-card parked", "camera": {"scene": "s01", "zoom": 1.307, "look": [1480, 800]},
                 "docks": [{"id": "ev-quay-card", "state": "moving", "box": [1047, 530, 866, 625], "rest": 0}],
                 "overlaps": [], "page": {}, "texts": [], "labels": []}


def test_the_depth_card_run_off_the_bottom_is_named_with_its_overshoot() -> None:
    tl = _dock_depth()
    layout = {"instants": [dict(DEPTH_INSTANT)]}
    g = _by_id(G.run(tl, [], {"cues": []}, layout=layout)[0])["M24"]
    assert g.level == "WARN", g
    assert "ev-quay-card" in g.message and "depth 1.15" in g.message and "focus_zoom" in g.message, g.message
    assert "79 px off the bottom" in g.message, g.message
    assert "off the right" not in g.message   # 1918 of 1920: in frame (the row the golden's frame is read against)
    warns, measured, unmeasured = G._depth_card_faults(tl["scenes"], "16:9", layout)
    assert measured == 1 and unmeasured == 0 and len(warns) == 1


def test_a_settled_flat_card_in_frame_reads_as_before() -> None:
    tl = _dock_depth()
    del tl["scenes"][0]["docks"][0]["depth"]
    layout = {"instants": [dict(DEPTH_INSTANT, docks=[{"id": "ev-quay-card", "state": "parked",
                                                       "box": [1160, 600, 640, 462], "rest": 1}])]}
    assert G._depth_card_faults(tl["scenes"], "16:9", layout) == ([], 0, 0)
    assert G._in_frame_gate(tl["scenes"], "16:9", layout) is None   # nothing moves the camera's frame over the card


def test_an_unmeasured_depth_card_is_said_not_measured_never_passed() -> None:
    tl = _dock_depth()
    g = G._in_frame_gate(tl["scenes"], "16:9", None)
    assert g is not None and g.level == "INFO" and "not measured" in g.message, g


# ------------------------------------------------------------------ R26-202 (a): a flight is a path, not a read
PANEL = "dock-c-blue-ties-panel"


def _v3b(t: float, rest: int, state: str = "moving") -> tuple[dict, dict]:
    """Tokyo v3b's row: the blue-ties panel THROWN at 9.09 (contact 9.55) over the 21.5x page (layout-probe.json at
    9.09: moving, rest 0, 2,432 px on the chart's data = 4 % of the card)."""
    page = {"scene_id": "s01", "span": [0.0, 38.96], "world": {"kind": "ledger", "page": {"builder": "story"}},
            "docks": [{"slide": PANEL, "enter": 9.09, "exit": 19.49, "arrive": "throw",
                       "place": {"x": 505, "y": 937, "w": 277, "h": 208}, "read_s": 1.2, "park_s": 0.7}]}
    tl = {"aspect": "9:16", "runtime_s": 38.96, "scenes": [page]}
    inst = {"t": t, "why": f"s01 dock {PANEL} enter", "docks": [{"id": PANEL, "state": state, "box": [-37, 800, 386, 156], "rest": rest}],
            "overlaps": [{"a": PANEL, "b": "page.plot", "area_px": 18603, "share_of_smaller": 31},
                         {"a": PANEL, "b": "page.data", "area_px": 2432, "share_of_smaller": 4}]}
    return tl, {"instants": [inst]}


def test_v3b_s_throw_flight_is_an_info_line_naming_the_flight_not_an_m27_fail() -> None:
    tl, layout = _v3b(9.09, rest=0)
    g = _by_id(G.run(tl, [], {"cues": []}, layout=layout)[0])["M27"]
    assert g.level != "FAIL", g.message
    assert "flight" in g.message and PANEL in g.message and "throw" in g.message and "0:09" in g.message, g.message


def test_a_card_that_settles_over_the_line_still_fails_m27() -> None:
    tl, layout = _v3b(9.7, rest=1, state="reading")
    g = _by_id(G.run(tl, [], {"cues": []}, layout=layout)[0])["M27"]
    assert g.level == "FAIL" and PANEL in g.message, g.message


def test_a_card_the_frame_shows_at_rest_inside_its_flight_clock_is_judged() -> None:
    """The clock alone never excuses a card: inside 9.09-9.55 a card the probe measured AT REST (rest 1) is read."""
    tl, layout = _v3b(9.3, rest=1)
    g = _by_id(G.run(tl, [], {"cues": []}, layout=layout)[0])["M27"]
    assert g.level == "FAIL", g.message
