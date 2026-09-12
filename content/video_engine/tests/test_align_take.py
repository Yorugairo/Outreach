"""R26-69: forced alignment of a recogniser's words onto the SCRIPT's tokens.

The core is pure (no Whisper): these tests hand it synthetic recogniser words and check that the output's
words are the script's tokens exactly, that digits the recogniser writes meet the script's number WORDS,
that a word the recogniser dropped is recovered with an interpolated time, and that the clock never runs
backwards or overlaps.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import align_take as AT  # noqa: E402
import scratch_take  # noqa: E402


def _rec(triples) -> list[dict]:
    return [{"w": w, "start_s": s, "end_s": e} for w, s, e in triples]


def _assert_monotone(words: list[dict]) -> None:
    prev_end = 0.0
    for w in words:
        assert w["start_s"] >= prev_end - 1e-9, w
        assert w["end_s"] >= w["start_s"], w
        prev_end = w["end_s"]


# ---- script tokens -------------------------------------------------------------------------------------

def test_script_tokens_strip_beat_marks_and_keep_stops_on_their_word():
    text = "Five percent was normal once. [ring]\n\n[post-key] But `[new]` a yield , is ask them: normal"
    assert AT.script_tokens(text) == ["Five", "percent", "was", "normal", "once.", "But", "a", "yield,",
                                      "is", "ask", "them:", "normal"]


def test_beat_mark_strip_matches_scratch_take_load_script(tmp_path, monkeypatch):
    raw = "[rehook] Start `[new]` with the number. [catalyst] [new] Today"
    path = tmp_path / "s.txt"
    path.write_text(raw, encoding="utf-8")
    monkeypatch.setattr(scratch_take, "SCRIPT_PATH", path)
    assert AT.strip_beat_marks(raw) == scratch_take.load_script()


# ---- digits to words -----------------------------------------------------------------------------------

@pytest.mark.parametrize("raw, units", [
    ("4.83", ["four", "point", "eight", "three"]),
    ("4.83%", ["four", "point", "eight", "three", "percent"]),
    ("123%", ["one", "hundred", "twenty", "three", "percent"]),
    ("1981", ["nineteen", "eighty", "one"]),
    ("2023.", ["twenty", "twenty", "three"]),
    ("1905", ["nineteen", "oh", "five"]),
    ("2005", ["two", "thousand", "five"]),
    ("10-year", ["ten", "year"]),
    ("1,200", ["one", "thousand", "two", "hundred"]),
    ("Heavier.", ["heavier"]),
    ("thirty-one", ["thirty", "one"]),
])
def test_word_units_expand_digits_to_the_words_a_script_writes(raw, units):
    assert AT.word_units(raw) == units


def test_dollar_sign_is_spoken_after_its_scale_word():
    rec = _rec([("$1.2", 1.0, 2.0), ("trillion", 2.0, 2.6)])
    assert [u for u, _, _ in AT.recognised_units(rec)] == ["one", "point", "two", "trillion", "dollars"]


@pytest.mark.parametrize("heard, units", [
    (["5", "%"], ["five", "percent"]),
    (["4", ".66."], ["four", "point", "six", "six"]),
    (["$1", ".2", "trillion"], ["one", "point", "two", "trillion", "dollars"]),
    (["$5", ".28", "a"], ["five", "point", "two", "eight", "dollars", "a"]),
])
def test_a_number_the_recogniser_split_into_fragments_reads_whole(heard, units):
    rec = _rec([(w, float(i), float(i) + 1.0) for i, w in enumerate(heard)])
    assert [u for u, _, _ in AT.recognised_units(rec)] == units


def test_recognised_units_split_a_word_span_by_character_length_in_order():
    units = AT.recognised_units(_rec([("31%", 1.0, 2.0)]))
    assert [u for u, _, _ in units] == ["thirty", "one", "percent"]
    assert units[0][1] == pytest.approx(1.0) and units[-1][2] == pytest.approx(2.0)
    for (_, _, e), (_, s, _) in zip(units, units[1:]):
        assert s == pytest.approx(e)


# ---- the alignment -------------------------------------------------------------------------------------

def test_every_script_token_comes_out_in_order_with_matched_times():
    tokens = AT.script_tokens("In nineteen eighty-one, the load was thirty-one percent.")
    rec = _rec([("In", 0.0, 0.2), ("1981,", 0.2, 1.0), ("the", 1.0, 1.1), ("load", 1.1, 1.4),
                ("was", 1.4, 1.6), ("31%.", 1.6, 2.6)])
    words, stats = AT.force_align(tokens, rec, duration_s=2.6)
    assert [w["w"] for w in words] == tokens
    assert stats == {"matched": len(tokens), "interpolated": 0, "script_tokens": len(tokens)}
    assert words[0]["start_s"] == 0.0 and words[1]["start_s"] == pytest.approx(0.2)
    assert words[-1]["end_s"] == pytest.approx(2.6)
    _assert_monotone(words)


def test_a_dropped_word_is_recovered_between_its_matched_neighbours():
    tokens = AT.script_tokens("the bridge under it is heavier")
    rec = _rec([("the", 0.0, 0.2), ("bridge", 0.2, 0.6), ("it", 1.0, 1.2), ("is", 1.2, 1.4),
                ("heavier", 1.4, 2.0)])
    words, stats = AT.force_align(tokens, rec, duration_s=2.0)
    assert [w["w"] for w in words] == tokens
    assert stats["matched"] == 5 and stats["interpolated"] == 1
    under = words[2]
    assert under["start_s"] == pytest.approx(0.6) and under["end_s"] == pytest.approx(1.0)
    _assert_monotone(words)


def test_an_interpolated_run_splits_its_gap_by_character_length_monotone():
    tokens = AT.script_tokens("start a longword end")
    rec = _rec([("start", 0.0, 0.5), ("end", 1.4, 1.8)])
    words, stats = AT.force_align(tokens, rec, duration_s=1.8)
    assert stats["interpolated"] == 2
    a, longword = words[1], words[2]
    assert a["start_s"] == pytest.approx(0.5)
    assert longword["end_s"] == pytest.approx(1.4)
    assert (longword["end_s"] - longword["start_s"]) == pytest.approx(8 * (a["end_s"] - a["start_s"]))
    _assert_monotone(words)


def test_a_run_with_no_room_borrows_its_neighbours_spans_and_stays_monotone():
    tokens = AT.script_tokens("one two three four")
    rec = _rec([("one", 0.0, 0.4), ("four", 0.4, 0.8)])
    words, stats = AT.force_align(tokens, rec, duration_s=0.8)
    assert stats["interpolated"] == 2
    assert words[0]["start_s"] == 0.0 and words[-1]["end_s"] == pytest.approx(0.8)
    assert all(w["end_s"] > w["start_s"] for w in words)
    _assert_monotone(words)


def test_leading_and_trailing_unmatched_runs_stay_inside_the_take():
    tokens = AT.script_tokens("so then middle words here finally")
    rec = _rec([("middle", 1.0, 1.4), ("words", 1.4, 1.8), ("here", 1.8, 2.1)])
    words, stats = AT.force_align(tokens, rec, duration_s=3.0)
    assert stats == {"matched": 3, "interpolated": 3, "script_tokens": 6}
    assert words[0]["start_s"] >= 0.0 and words[1]["end_s"] == pytest.approx(1.0)
    assert words[-1]["start_s"] == pytest.approx(2.1) and words[-1]["end_s"] <= 3.0 + 1e-9
    _assert_monotone(words)


def test_a_misheard_word_does_not_shift_the_rest():
    tokens = AT.script_tokens("nothing defaulted nothing crashed")
    rec = _rec([("nothing", 0.0, 0.3), ("defaulting", 0.3, 0.9), ("nothing", 1.2, 1.5), ("crashed.", 1.5, 2.0)])
    words, stats = AT.force_align(tokens, rec, duration_s=2.0)
    assert [w["start_s"] for w in words] == pytest.approx([0.0, 0.3, 1.2, 1.5])
    assert stats["matched"] == 4


def test_no_recognised_words_spreads_the_script_over_the_take():
    tokens = AT.script_tokens("a bb ccc")
    words, stats = AT.force_align(tokens, [], duration_s=1.2)
    assert stats == {"matched": 0, "interpolated": 3, "script_tokens": 3}
    assert words[0]["start_s"] == 0.0 and words[-1]["end_s"] == pytest.approx(1.2)
    _assert_monotone(words)


def test_payload_carries_the_aligned_counts_in_the_take_schema():
    tokens = AT.script_tokens("hello world")
    words, stats = AT.force_align(tokens, _rec([("hello", 0.0, 0.5), ("world", 0.5, 1.0)]), 1.0)
    payload = AT.build_payload("chirp", 1.0, words, stats)
    assert set(payload) == {"engine", "voice", "duration_s", "words", "aligned"}
    assert payload["engine"] == "chirp-aligned"
    assert payload["aligned"] == {"matched": 2, "interpolated": 0, "script_tokens": 2}
    assert set(payload["words"][0]) == {"w", "start_s", "end_s"}
