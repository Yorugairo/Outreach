"""P69 T81 / E99 s112 - THE STAMP IS PUNCTUATION: IT LANDS JUST AFTER THE THING IT NAMES, NEVER DURING IT.

The operator (2026-09-24), on the row-19 GPU and the row-21 rack: *"I think of the stamp as the punctuation on the
thing, so it has to follow immediately after not during."* What this file holds the kit and the compiler to:

  (1) THE WORD-END ANCHOR   `authoring.words.after(ws, phrase[, word])` is the instant a stamp's CONTACT lands: the end
                            of the word (or the phrase's last word - `after_idea`, the end of the idea) plus a small
                            beat (`STAMP_AFTER_BEAT_S`). `authoring.docks.stamp_enter(contact)` resolves the dock's
                            ENTER from that contact (the mark falls 0.1542 s before it meets the page), rounded UP to
                            the shot table's 0.01 s, so the contact never lands before the instant asked.
  (2) THE COMPILER'S FORM   a stamped dock may say `after: "<phrase>"` (and `after_beat`); the compiler resolves its
                            enter from the take's words through the SAME two functions, the phrase searched at or
                            after the tuple's own enter. `names: "<phrase>"` tells the advice which word it punctuates.
  (3) THE ADVICE (s106)     `stamp_timing_advice` WARNs, with its numbers, when a stamp's contact lands inside its own
                            word or within `STAMP_DATA_CLEAR_S` of a data mark on its scene - never a refusal. Each
                            finding names the word or the mark, the offset and the suggested contact and enter.
  (4) BYTE-IDENTICAL        a dock that names none of it compiles to the entry it always did.
"""
from __future__ import annotations

import inspect
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as MG  # noqa: E402
from authoring import docks as D, words as W  # noqa: E402

COMPILER = ROOT / "content/video_engine/scripts/build_scene_timeline_f.py"
STAMP = {"prop": True, "arrive": "stamp"}
# a take: "... going into racks. It passes." then "racks" again later (a second occurrence the floor must reach)
WS = [{"w": w, "start_s": s, "end_s": e} for w, s, e in (
    ("They're", 9.40, 9.62), ("going", 9.62, 9.90), ("into", 9.90, 10.05), ("racks.", 10.05, 10.62),
    ("It", 11.10, 11.22), ("passes.", 11.22, 11.80), ("Stacked", 12.00, 12.40), ("memory", 12.40, 12.85),
    ("in", 12.85, 12.95), ("racks", 12.95, 13.40), ("again.", 13.40, 13.90))]
TL_WORDS = [{"w": w["w"], "start": w["start_s"], "end": w["end_s"]} for w in WS]   # timeline.json's own shape
CONTACT = MG.STAMP_CONTACT_S


def _scene(docks, species=(), span=(0.0, 30.0), world=None) -> dict:
    return {"scene_id": "s01", "span": list(span), "world": world or {"asset_id": "plate-plain"},
            "species": list(species), "docks": list(docks)}


def _stamp_dock(enter: float, **extra) -> dict:
    return {"slide": "prop-rack", "slot": 0, "enter": enter, "exit": 20.0, "arrive": "stamp", "kind": "prop", **extra}


# ---- (1) the kit: the word-END anchor --------------------------------------------------------------------------------


def test_after_is_the_words_END_plus_the_beat_not_its_start():
    assert W.STAMP_AFTER_BEAT_S == pytest.approx(0.12)
    assert W.word_end(WS, "racks") == pytest.approx(10.62)
    assert W.after(WS, "racks") == pytest.approx(10.62 + W.STAMP_AFTER_BEAT_S)
    assert W.after(WS, "racks", beat=0.3) == pytest.approx(10.92)


def test_after_reads_a_word_INSIDE_its_phrase_and_after_idea_reads_the_phrases_END():
    assert W.after(WS, "going into racks", "racks") == pytest.approx(10.74)          # word_in's reading, at its END
    assert W.after(WS, "going into", "into") == pytest.approx(10.05 + 0.12)
    assert W.after_idea(WS, "Stacked memory") == pytest.approx(12.85 + 0.12)          # the idea's end: its last word
    assert W.after_idea(WS, "They're going into racks") == pytest.approx(10.74)


def test_after_takes_the_first_occurrence_AT_OR_AFTER_a_floor_and_refuses_a_phrase_the_take_lacks():
    assert W.after(WS, "racks") == pytest.approx(10.74)                    # the take's first "racks"
    assert W.after(WS, "racks", from_s=12.0) == pytest.approx(13.52)       # ... the one at or after 12 s
    assert W.after(WS, "racks", from_s=10.08) == pytest.approx(10.74), "an at() rounded UP past the onset still finds it"
    with pytest.raises(SystemExit, match="phrase not in the take"):
        W.after(WS, "server racks")
    with pytest.raises(SystemExit, match="not in the"):
        W.after(WS, "going into", "racks", window=2)
    with pytest.raises(ValueError, match="beat"):
        W.after(WS, "racks", beat=-0.1)


def test_stamp_enter_resolves_the_ENTER_FROM_THE_CONTACT_and_never_lands_early():
    """The mark falls STAMP_CONTACT_S before it meets the page: the enter is the contact less that, rounded UP to 0.01
    (the compiled dock writes its enter to 2 dp), so enter + contact lands on the instant asked or within one step after."""
    for contact in (10.74, 13.52, 386.831, 5.0):
        enter = D.stamp_enter(contact)
        assert enter == round(enter, 2)
        assert contact - 1e-9 <= enter + CONTACT < contact + 0.01 + 1e-9, (contact, enter)


def test_the_kits_contact_is_the_gates_contact():
    from authoring import audio as A
    assert A.stamp_contact_s() == MG.STAMP_CONTACT_S


# ---- (2) the compiler's form: `after` / `after_beat` / `names` on a stamped dock -------------------------------------


def test_the_grammar_takes_after_after_beat_and_names_on_a_stamp():
    d = B.dock_opts({**STAMP, "after": "racks", "after_beat": 0.2, "names": "racks"})
    assert (d["after"], d["after_beat"], d["names"]) == ("racks", 0.2, "racks")
    assert set(B.STAMP_ANCHOR_OPTS) <= set(B.DOCK_OPTS)


@pytest.mark.parametrize("opts, match", [
    ({"prop": True, "arrive": "throw", "after": "racks"}, "STAMP's word anchor"),
    ({"prop": True, "names": "racks"}, "STAMP's word anchor"),
    ({**STAMP, "after": "  "}, "must name a word or phrase"),
    ({**STAMP, "names": 3}, "must name a word or phrase"),
    ({**STAMP, "after_beat": 0.2}, "after_beat is the beat after an `after`"),
    ({**STAMP, "after": "racks", "after_beat": -0.1}, "after_beat must be"),
    ({**STAMP, "after": "racks", "after_beat": True}, "after_beat must be"),
    ({**STAMP, "after": "racks", "after_beat": 1.5}, "after_beat must be"),
])
def test_the_anchor_is_refused_by_name_where_it_means_nothing(opts, match):
    with pytest.raises(ValueError, match=match):
        B.dock_opts(opts)


def test_the_compiler_resolves_an_after_dock_through_the_KITS_two_functions():
    ds = [("prop-rack", 0, 10.05, 20.0, {**STAMP, "after": "racks"})]
    out, notes = B.resolve_stamp_after(ds, TL_WORDS, "shot row 1 (0-30s)")
    enter = out[0][2]
    assert enter == D.stamp_enter(W.after(WS, "racks", from_s=10.05))
    assert W.after(WS, "racks") - 1e-9 <= enter + CONTACT < W.after(WS, "racks") + 0.01
    assert out[0][:2] == ds[0][:2] and out[0][3:] == ds[0][3:], "only the enter moves"
    assert len(notes) == 1 and "racks" in notes[0] and f"{enter:.2f}" in notes[0]


def test_the_compilers_after_searches_from_the_tuples_own_enter_and_takes_its_beat():
    ds = [("prop-rack", 0, 12.0, 20.0, {**STAMP, "after": "racks", "after_beat": 0.3})]
    enter = B.resolve_stamp_after(ds, TL_WORDS, "row")[0][0][2]
    assert enter == D.stamp_enter(13.40 + 0.3)
    ds = [("prop-rack", 0, 9.62, 20.0, {**STAMP, "after": "going into racks"})]   # the idea's end
    assert B.resolve_stamp_after(ds, TL_WORDS, "row")[0][0][2] == D.stamp_enter(10.74)


def test_a_row_with_no_after_is_returned_AS_IT_WAS():
    ds = [("prop-rack", 0, 10.05, 20.0, dict(STAMP)), ("dock-card", 1, 4.0, 9.0)]
    out, notes = B.resolve_stamp_after(ds, TL_WORDS, "row")
    assert out is ds and notes == []
    out, _ = B.resolve_stamp_after(ds + [("prop-b", 0, 9.0, 20.0, {**STAMP, "after": "racks"})], TL_WORDS, "row")
    assert out[0] is ds[0] and out[1] is ds[1], "a dock with no after is the same object"
    assert B.resolve_stamp_after([], None, "row") == ([], [])


def test_the_compilers_after_is_refused_only_where_it_cannot_be_played():
    with pytest.raises(ValueError, match="needs the build's words"):
        B.resolve_stamp_after([("p", 0, 10.0, 20.0, {**STAMP, "after": "racks"})], None, "shot row 3")
    with pytest.raises(ValueError, match="shot row 3 dock p: after 'server racks'"):
        B.resolve_stamp_after([("p", 0, 10.0, 20.0, {**STAMP, "after": "server racks"})], TL_WORDS, "shot row 3")
    with pytest.raises(ValueError, match="past the dock's exit"):
        B.resolve_stamp_after([("p", 0, 10.0, 10.5, {**STAMP, "after": "racks"})], TL_WORDS, "shot row 3")
    with pytest.raises(ValueError, match="STAMP's word anchor"):
        B.resolve_stamp_after([("p", 0, 10.0, 20.0, {"prop": True, "after": "racks"})], TL_WORDS, "shot row 3")


def test_the_row_loop_resolves_after_BEFORE_any_consumer_reads_a_docks_enter():
    """Pinned by position: the resolution runs before the held-species pass reads the docks' enters (`ats`), before the
    prop morphs and the stamps' fit - so the gate, the cues, the camera and the fit all read ONE enter."""
    src = COMPILER.read_text(encoding="utf-8")
    body = src[src.index("def main() -> int:"):]
    i_res = body.index("ds, _after_notes = resolve_stamp_after(ds, tl.get(\"words\"), f\"shot row {i + 1} ({a}-{b}s)\")")
    i_ats = body.index("ats = sorted(")
    i_pm = body.index("_pm = prop_morph_row(")
    i_fit = body.index("stamp_fits, stamp_boxes = row_stamp_fits(")
    assert 0 < i_res < i_ats < i_pm < i_fit


# ---- (3) the advice: inside its word, or on a data mark --------------------------------------------------------------


def test_a_stamp_entered_ON_its_words_start_is_ADVISED_with_the_word_the_offset_and_the_suggestion():
    """The H door's form today: the enter on the word's onset (`word_in(...)`), so the contact is 0.1542 s into it."""
    adv = B.stamp_timing_advice([_scene([_stamp_dock(10.05)])], TL_WORDS)
    assert len(adv) == 1
    a = adv[0]
    assert (a["kind"], a["word"], a["scene"], a["slide"], a["row"]) == ("inside", "racks.", "s01", "prop-rack", 1)
    assert a["contact"] == pytest.approx(10.05 + CONTACT)
    assert a["word_span"] == [10.05, 10.62]
    assert a["offset"] == pytest.approx(10.05 + CONTACT - 10.62, abs=1e-3)       # negative: before the word ends
    assert a["suggest_contact"] == pytest.approx(10.74)
    assert a["suggest_enter"] == D.stamp_enter(10.74)
    m = a["message"]
    for part in ("E99 s112", "INSIDE", "'racks.'", "10.20s", "0.42s before it ends", "after('racks')", "10.74s",
                 f"enter {D.stamp_enter(10.74):.2f}s"):
        assert part in m, (part, m)


def test_a_stamp_NAMED_to_a_phrase_is_judged_against_THE_PHRASES_END():
    """`names` says which thing it punctuates: entered on "Stacked", its contact is judged against "memory"'s end."""
    adv = B.stamp_timing_advice([_scene([_stamp_dock(12.0, names="stacked memory")])], TL_WORDS)
    assert len(adv) == 1 and adv[0]["word"] == "stacked memory" and adv[0]["word_span"] == [12.0, 12.85]
    assert adv[0]["suggest_contact"] == pytest.approx(12.97) and "after_idea('stacked memory')" in adv[0]["message"]
    early = B.stamp_timing_advice([_scene([_stamp_dock(11.0, names="Stacked memory")])], TL_WORDS)
    assert len(early) == 1 and early[0]["kind"] == "before" and "BEFORE" in early[0]["message"]


def test_the_word_an_unnamed_stamp_was_put_ON_is_the_one_STARTING_at_its_enter_never_the_one_ending_there():
    """The H door's row-9 case: "The Fed" - the enter is "Fed"'s onset (`word_in`), which is also where "The" ends
    (to the rounding). The stamp was put on "Fed", so "Fed" is its word, and a contact inside it is advised."""
    ws = [{"w": "The", "start": 217.32, "end": 217.4604}, {"w": "Fed", "start": 217.4604, "end": 217.80},
          {"w": "at", "start": 217.80, "end": 217.90}]
    adv = B.stamp_timing_advice([_scene([_stamp_dock(217.46)], span=(200.0, 230.0))], ws)
    assert [(a["kind"], a["word"]) for a in adv] == [("inside", "Fed")]
    assert "after('Fed')" in adv[0]["message"], "the suggestion keeps the word's own case"
    assert adv[0]["suggest_contact"] == pytest.approx(217.92)


def test_a_data_mark_landing_ON_the_stamps_enter_while_it_still_comes_down_is_ADVISED():
    """The H door's row-10 case: the stamp entered ON the recast's landing - "drop the stamp at the exact same time as
    the data point" - so its contact is 0.1542 s after the mark: outside +-0.15 s, inside the fall, advised."""
    fig = {"kind": "figure", "at": 7.7, "dur": 0.3}                                   # lands at 8.0
    adv = B.stamp_timing_advice([_scene([_stamp_dock(8.0)], [fig])], TL_WORDS)
    assert [a["kind"] for a in adv] == ["data"] and adv[0]["offset"] == pytest.approx(CONTACT, abs=1e-3)
    assert adv[0]["suggest_enter"] == pytest.approx(8.01) and adv[0]["suggest_contact"] == pytest.approx(8.01 + CONTACT)
    moved = dict(_stamp_dock(adv[0]["suggest_enter"]))
    assert B.stamp_timing_advice([_scene([moved], [fig])], TL_WORDS) == [], "the suggestion clears the advice"


def test_a_stamp_that_lands_just_after_its_word_and_clear_of_the_data_is_SILENT():
    ok = D.stamp_enter(W.after(WS, "racks"))
    assert B.stamp_timing_advice([_scene([_stamp_dock(ok)])], TL_WORDS) == []
    assert B.stamp_timing_advice([_scene([_stamp_dock(ok, names="racks")])], TL_WORDS) == []
    assert B.stamp_timing_advice([_scene([_stamp_dock(8.0)])], TL_WORDS) == [], "in a gap: no word of its own"
    assert B.stamp_timing_advice([_scene([dict(_stamp_dock(10.05), arrive="throw")])], TL_WORDS) == [], "stamps only"


def test_a_stamp_ON_THE_SAME_INSTANT_as_a_data_mark_is_ADVISED():
    ok = D.stamp_enter(W.after(WS, "racks"))
    contact = ok + CONTACT
    fig = {"kind": "figure", "at": round(contact - 0.35, 2), "dur": 0.3}          # the figure lands 0.05 s before
    adv = B.stamp_timing_advice([_scene([_stamp_dock(ok)], [fig])], TL_WORDS)
    assert len(adv) == 1 and adv[0]["kind"] == "data" and adv[0]["mark"] == "figure landing"
    land = fig["at"] + fig["dur"]
    assert adv[0]["mark_at"] == pytest.approx(land) and adv[0]["offset"] == pytest.approx(contact - land, abs=1e-3)
    assert adv[0]["suggest_contact"] >= land + B.STAMP_DATA_CLEAR_S - 1e-9
    assert adv[0]["suggest_enter"] == D.stamp_enter(adv[0]["suggest_contact"])
    assert B.stamp_timing_advice([_scene([_stamp_dock(adv[0]["suggest_enter"])], [fig])], TL_WORDS) == []
    assert "figure landing" in adv[0]["message"] and "one instant" in adv[0]["message"]
    far = {"kind": "figure", "at": round(contact - 0.6, 2), "dur": 0.3}
    assert B.stamp_timing_advice([_scene([_stamp_dock(ok)], [far])], TL_WORDS) == []
    other_dock = {"slide": "dock-card", "slot": 1, "enter": round(contact, 2), "exit": 20.0}
    assert B.stamp_timing_advice([_scene([_stamp_dock(ok), other_dock])], TL_WORDS) == [], "a DOCK is not a data mark"


def test_the_advice_is_a_WARN_the_row_loop_PRINTS_never_a_refusal():
    src = COMPILER.read_text(encoding="utf-8")
    body = src[src.index("def main() -> int:"):]
    assert "for _adv in stamp_timing_advice(scenes, tl.get(\"words\")):" in body
    assert 'print(f"  [WARN] P69 T81: {_adv[\'message\']}")' in body
    assert "raise" not in inspect.getsource(B.stamp_timing_advice)
    assert B.stamp_timing_advice([_scene([_stamp_dock(10.05)])], None) == [], "no words: no word to judge, and no error"


# ---- (4) byte identity -----------------------------------------------------------------------------------------------


def test_a_dock_that_names_nothing_writes_the_entry_it_always_wrote():
    base = B.dock_entry("prop-rack", 0, 10.05, 20.0, 0, B.DOCK_KIND_PROP, None, "stamp", None, True, prop=True)
    assert "names" not in base
    named = B.dock_entry("prop-rack", 0, 10.05, 20.0, 0, B.DOCK_KIND_PROP, None, "stamp", None, True, prop=True,
                         names="racks")
    assert named["names"] == "racks" and {k: v for k, v in named.items() if k != "names"} == base


def test_the_card_carries_the_anchor_as_the_stamps_options():
    cards = json.loads((ROOT / "content/video_engine/effects/cards/arrival.json").read_text(encoding="utf-8"))["cards"]
    card = next(c for c in cards if c["id"] == "arrival:stamp")
    opts = {o["token"]: o for o in card["options"]}
    for tok in B.STAMP_ANCHOR_OPTS:
        assert opts[tok]["source_set"] == "DOCK_OPTS", tok
    assert "E99 s112" in card["doctrine"]
    assert "s112" in card["callable"]["why"]
