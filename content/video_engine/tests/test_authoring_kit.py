"""The authoring kit (P51 T0): the mechanism both shorts now write their shot table through.

The kit is pure - every episode fact arrives as an argument - so these tests run on synthetic
words, synthetic cards and synthetic rows, and the last one greps the package for the episode
facts that must never live in it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
from authoring import Project  # noqa: E402
from authoring import audio as A, docks as D, table as T, words as W  # noqa: E402

KIT = ROOT / "content/video_engine/scripts/authoring"


def _ws(pairs) -> list[dict]:
    """A take's word list: (word, start, end) triples in the shape the aligner writes."""
    return [{"w": w, "start_s": s, "end_s": e} for w, s, e in pairs]


TAKE = _ws([("The", 0.0, 0.30), ("Fed", 0.30, 0.60), ("hasn't", 0.60, 0.90), ("moved.", 0.90, 1.00),
            ("Your", 2.00, 2.30), ("costs", 2.30, 2.60), ("climbed", 2.60, 2.90), ("anyway?", 2.90, 3.10),
            ("Two", 3.20, 3.50), ("numbers:", 3.50, 3.80), ("one", 5.00, 5.30), ("two!", 5.30, 5.60)])


# ---------------------------------------------------------------- the anchors (M13)
def test_phrase_start_matches_through_punctuation():
    assert W.phrase_start(TAKE, "the fed hasn't moved") == (0, 0.0)
    assert W.phrase_start(TAKE, "Two numbers") == (8, 3.2)
    assert W.at(TAKE, "Your costs") == 2.0


def test_a_phrase_that_is_not_in_the_take_refuses_by_name():
    with pytest.raises(SystemExit) as e:
        W.phrase_start(TAKE, "the Fed moved")
    assert "the Fed moved" in str(e.value)


def test_word_in_finds_the_word_inside_the_phrase():
    assert W.word_in(TAKE, "the fed hasn't", "moved") == 0.9


def test_cut_before_sits_at_eight_tenths_of_the_gap():
    # the gap after "moved." (1.00) before "Your" (2.00) is a second: the cut lands at 1.80
    assert W.cut_before(TAKE, "Your costs") == 1.80
    assert W.cut_before(TAKE, "The Fed") == 0.0, "nothing to cut before the first word"


def test_cut_before_refuses_a_gap_under_the_m13_minimum():
    with pytest.raises(SystemExit) as e:
        W.cut_before(TAKE, "Two numbers")          # the gap is 0.10 s
    assert "M13" in str(e.value) and "Two numbers" in str(e.value)


def test_the_m13_dials_are_the_ruled_ones():
    assert (W.CUT_AT, W.MIN_GAP) == (0.8, 0.30)


def test_next_sentence_start_is_the_takes_own_punctuation():
    assert W.next_sentence_start(TAKE, 0.0) == 2.0      # after "moved."
    assert W.next_sentence_start(TAKE, 2.1) == 3.2      # after "anyway?"
    assert W.next_sentence_start(TAKE, 5.4) is None     # nothing ends after the last word


# ---------------------------------------------------------------- the timeline
def _project(tmp_path: Path) -> Project:
    (tmp_path / "build").mkdir()
    return Project(here=tmp_path, build=tmp_path / "build", take=tmp_path, take_stem="scene_1",
                   script_name="SCRIPT.txt", episode_id="an-episode")


def test_write_timeline_splits_sentences_on_the_four_stops(tmp_path):
    p = _project(tmp_path)
    tl = W.write_timeline(p, TAKE, 12.5)
    assert [s["text"] for s in tl["sentences"]] == [
        "The Fed hasn't moved.", "Your costs climbed anyway?", "Two numbers:", "one two!"]
    assert tl["sentences"][0]["start"] == 0.0 and tl["sentences"][0]["end"] == 1.0
    assert (tl["episode"], tl["script"], tl["take"]) == ("an-episode", "SCRIPT.txt", "vo-short")
    assert tl["runtime_s"] == 12.5 and tl["edit_pauses_applied"] is False
    assert json.loads((p.build / "timeline.json").read_text(encoding="utf-8")) == tl


def test_shifted_words_reads_the_built_timeline_back_in_the_takes_shape(tmp_path):
    p = _project(tmp_path)
    W.write_timeline(p, TAKE, 12.5)
    assert W.shifted_words(p)[:2] == [{"w": "The", "start_s": 0.0, "end_s": 0.3},
                                      {"w": "Fed", "start_s": 0.3, "end_s": 0.6}]


# ---------------------------------------------------------------- the cards
def _png(path: Path, size: tuple[int, int]) -> Path:
    from PIL import Image
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, (22, 24, 28)).save(path)
    return path


def test_card_aspect_reads_the_rendered_cards_own_size(tmp_path):
    build = tmp_path / "build"
    _png(build / "docks/dock-x.png", (800, 400))
    assert D.card_aspect("dock-x", build) == 0.5


def test_still_card_aspect_reads_the_crop_off_the_still(tmp_path):
    still = _png(tmp_path / "a-still.png", (768, 1376))
    assert D.still_card_aspect(still, (0.19, 0.48)) == round(0.48 * 1376 / 768, 4)


def test_centred_card_point_maps_a_fraction_of_the_card_to_the_stage():
    mid = D.centred_card_point(1.0, 0.5, 0.5, 0.5, centre_w=0.5, centre_x=0.5)
    assert mid == {"kind": "point", "x": 0.5, "y": 0.5}
    corner = D.centred_card_point(1.0, 0.5, 0.0, 0.0, centre_w=0.5, centre_x=0.5)
    assert corner["x"] == 0.25                       # half the card's width to the left of centre
    assert corner["y"] == round((0.5 * 1920 - 540 / 2) / 1920, 4)


def test_a_tall_card_is_capped_at_the_stages_share():
    top = D.centred_card_point(4.0, 0.5, 0.5, 0.0, centre_w=0.74, centre_x=0.5)
    foot = D.centred_card_point(4.0, 0.5, 0.5, 1.0, centre_w=0.74, centre_x=0.5)
    height_px = round((foot["y"] - top["y"]) * 1920)
    assert height_px == round(B.CENTRE_MAX_H * 1920), "the card cannot grow past CENTRE_MAX_H"
    assert round((top["y"] + foot["y"]) / 2, 3) == 0.5, "... and the cap keeps it centred"


# ---------------------------------------------------------------- the record dock
RECORD_TAKE = _ws([("pledged", 4.5, 4.9), ("ten", 5.0, 5.4), ("trillion", 5.5, 5.9),
                   ("yen", 6.0, 6.4), ("to", 6.5, 6.7), ("chips,", 7.0, 7.4)])


def test_record_words_land_the_highlighter_on_the_narrators_word():
    typed, hl, end = D.record_words("at least 10 trillion yen in support", 0.0, RECORD_TAKE,
                                    "ten trillion yen", {"10": "ten", "trillion": "trillion", "yen": "yen"},
                                    ("at", "least", "10", "trillion", "yen"))
    assert hl == [0, 4]
    at = dict((w, t) for w, t in typed)
    assert at["at"] == 0.0 and at["least"] == 0.1     # the run-up types at `per`
    assert (at["10"], at["trillion"], at["yen"]) == (5.0, 5.5, 6.0)   # ... the phrase lands on the voice
    assert at["in"] == 6.07 and at["support"] == 6.14                 # ... the tail types at `tail_per`
    assert end == 6.19


def test_record_asset_is_a_real_one_pixel_png(tmp_path):
    import build_render_f as R
    assert D.record_asset("dock-rec", tmp_path) == "dock-rec"
    from PIL import Image
    assert Image.open(tmp_path / "docks/dock-rec.png").size == (1, 1)
    assert R.STAMPED["dock-rec"] == str(tmp_path / "docks/dock-rec.png")


def test_meta_set_fills_only_the_named_card():
    meta = [{"asset": "a"}, {"asset": "b"}]
    D.meta_set(meta, "b", "record", {"words": []})
    assert meta == [{"asset": "a"}, {"asset": "b", "record": {"words": []}}]


# ---------------------------------------------------------------- the bed and the cue clock
THROWN = [(0.0, 5.0, "plate-a", (0, 0, 0), [("card-x", 0, 2.0, 5.0, {"arrive": "throw", "mass": "paper"})], "cut", None),
          (5.0, 9.0, "ledger:ev-x:line:3:right:snap=card-x:cut", (0, 0, 0), [], "cut", None)]


def test_the_bed_swells_from_the_throw_through_the_snap():
    env = A.bed_envelope(THROWN, 4.0, 0.45, fallback_end=lambda d: float(d[2]) + 1.2)
    assert env == [[1.7, 0.0], [2.0, 4.0], [5.45, 4.0], [6.25, 0.0]]


def test_a_card_no_row_snaps_up_falls_back_to_the_episodes_own_end():
    env = A.bed_envelope(THROWN, 4.0, 0.45, fallback_end=lambda d: float(d[2]) + 1.2, snap_keys=(":camera=",))
    assert env == [[1.7, 0.0], [2.0, 4.0], [3.2, 4.0], [4.0, 0.0]]


def test_row_arrivals_yields_the_docks_that_land_with_weight():
    assert [d[0] for d, _ in A.row_arrivals(THROWN[0])] == ["card-x"]
    assert list(A.row_arrivals(THROWN[1])) == []


def test_page_transitions_read_the_entry_and_the_exit():
    p = A.page_transitions("ledger:ev-x:line:3:right:mount=0.4:cut")
    assert p["ledger"] and p["mount"] and p["cut"] and not p["spiral"]
    assert A.page_transitions("plate-a;idle=drift")["ledger"] is False
    assert A.page_transitions("ledger:ev-x:line:3:right:camera=card-x:cut")["camera"] is True


def test_landing_contact_steps_a_throw_onto_a_frame():
    dials = {"FLIGHT_S": 0.5, "ANTIC_S": 0.2, "DROP_S": 0.3}
    assert A.landing_contact(2.0, "throw", dials) == 2.5
    assert A.landing_contact(2.0, "land", dials) == 2.5
    # a flight that does not sit on a frame is rounded UP to the first frame at or past it
    assert A.landing_contact(0.0, "throw", {"FLIGHT_S": 0.51, "ANTIC_S": 0.0, "DROP_S": 0.0}) == 13 / 24


def test_stop_dials_are_read_from_the_kinetics_module():
    dials = A.stop_dials()
    assert set(A.STOP_DIALS) <= set(dials) and all(v > 0 for k, v in dials.items() if k in A.STOP_DIALS)


def test_bed_gain_is_the_measured_ratio():
    assert A.bed_gain(-17.9, -20.0, -13.0) == round(10 ** ((-17.9 - 20.0 + 13.0) / 20), 4)


def test_outro_clock_pads_to_whichever_finishes_last():
    t_outro, t_line, runtime = A.outro_clock(79.0, 2.3, outro_lead=0.1, outro_s=6.2, brand_gap=0.7, brand_tail=1.0)
    assert (t_outro, t_line) == (78.9, 79.7)
    assert runtime == 85.1, "the card outlasts the brand line here (78.9 + 6.2)"
    # ... and a long brand line pushes the runtime past the card instead
    assert A.outro_clock(79.0, 5.0, outro_lead=0.1, outro_s=6.2, brand_gap=0.7, brand_tail=1.0)[2] == 85.7


# ---------------------------------------------------------------- the table
def test_write_shot_table_writes_the_tuple_rows_the_compiler_loads(tmp_path):
    out = T.write_shot_table(tmp_path / "SHOT-TABLE-SHORT.py", list(THROWN), '"""a header."""\n')
    text = out.read_text(encoding="utf-8")
    assert text.startswith('"""a header."""\nW = [(')
    ns: dict = {}
    exec(compile(text, str(out), "exec"), ns)
    assert ns["W"] == list(THROWN)


def test_row_line_names_the_world_and_what_fires_on_it():
    row = (1.0, 2.0, "clip:build/clips/a-clip.mp4", (0, 0, 0), [("card-x", 0, 1.0, 2.0)], "cut",
           [{"kind": "spotlight"}])
    assert T.row_line(row) == "    1.00-  2.00  a-clip.mp4  species ['spotlight']"
    assert "docks ['card-x']" in T.row_line(row, show_docks=True)


def test_hold_until_gives_every_held_light_its_sentence():
    rows = [(0.0, 3.0, "ledger:ev-x:line:1:right", (0, 0, 0), [], "cut",
             [{"kind": "spotlight", "at": 0.5, "dur": "hold"},
              {"kind": "spotlight", "at": 0.5, "dur": "hold", "until": 9.9},
              {"kind": "callout", "at": 0.5, "dur": 1.0}])]
    T.hold_until(rows, TAKE)
    assert rows[0][6][0]["until"] == 2.0, "the first word of the next sentence (E25)"
    assert rows[0][6][1]["until"] == 9.9, "a row that names its own `until` keeps it"
    assert "until" not in rows[0][6][2], "only a HELD light follows its sentence"


# ---------------------------------------------------------------- E61: the plate's use
def test_a_plate_may_name_its_use():
    bare, opts = B.split_plate_opts("plate-x;idle=drift;use=bridge")
    assert bare == "plate-x" and opts == {"idle": "drift", "use": "bridge"}
    assert B.PLATE_USES == ("landing", "bridge", "reset")


def test_an_unknown_use_refuses_and_names_the_option():
    with pytest.raises(ValueError) as e:
        B.split_plate_opts("plate-x;use=nope")
    assert "use" in str(e.value) and "nope" in str(e.value)
    assert "landing|bridge|reset" in str(e.value)


# ---------------------------------------------------------------- the rule the kit is for
FORBIDDEN = ("tokyo", "tariff", "snipe", "c:/", "c:\\")


def test_the_kit_holds_no_episode_fact():
    hits = []
    for f in sorted(KIT.glob("*.py")):
        text = f.read_text(encoding="utf-8").lower()
        for i, line in enumerate(text.splitlines(), start=1):
            for bad in FORBIDDEN:
                if bad in line:
                    hits.append(f"{f.name}:{i}: {bad!r}")
    assert not hits, "an episode fact (or an absolute path) leaked into the kit:\n" + "\n".join(hits)


def test_the_kit_is_the_five_modules_the_plan_names():
    assert sorted(p.name for p in KIT.glob("*.py")) == ["__init__.py", "audio.py", "docks.py", "table.py", "words.py"]
