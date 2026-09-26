"""A TAKE'S RATE IS MEASURED, NEVER ASSUMED (E99 s82, R26-227; P72 T28).

`scratch_take.py --rate 1.075` was asked for ~175 wpm and measured 166 (2,320 words over 13:58): the index printed chars/s
against an estimator, never words per minute against the ask. The pins: the rate is words over SPOKEN seconds (first word's
start to last word's end); the report prints the words, the spoken seconds, the measured wpm and the ask; a take outside the
asked band exits 2 (a planted slow take); inside it, or with no ask, exits 0; a malformed ask is refused by name; the
kokoro index carries the same line. No synthesis runs here - `--measure` reads a words file already on disk.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import scratch_take as ST  # noqa: E402


def take(n: int, seconds: float, lead: float = 0.5) -> list[dict]:
    """`n` words spread evenly over `seconds` of speech, starting `lead` s into the file."""
    step = seconds / n
    return [{"w": f"word{i}", "start_s": round(lead + i * step, 3), "end_s": round(lead + (i + 1) * step, 3)}
            for i in range(n)]


def write_words(tmp_path: Path, words: list[dict], wrap: bool = True) -> Path:
    p = tmp_path / "scratch-kokoro.words.json"
    p.write_text(json.dumps({"engine": "kokoro-82M", "words": words} if wrap else words), encoding="utf-8")
    return p


def test_the_rate_is_words_over_spoken_seconds():
    rate = ST.measure(take(166, 60.0, lead=3.0) + [{"w": ".", "start_s": 63.0, "end_s": 63.0}])
    assert rate.words == 166                     # a bare stop is not a word
    assert rate.spoken_s == pytest.approx(60.0)  # the lead-in silence is not speech
    assert rate.wpm == pytest.approx(166.0)


def test_the_ask_parses_as_a_band_or_one_number_and_a_malformed_ask_is_refused_by_name():
    assert ST.parse_ask("170-180") == (170.0, 180.0)
    assert ST.parse_ask("175") == (175.0 - ST.ASK_TOL_WPM, 175.0 + ST.ASK_TOL_WPM)
    for bad in ("fast", "180-170", "0", "-5"):
        with pytest.raises(ValueError, match="--wpm"):
            ST.parse_ask(bad)


def test_a_planted_slow_take_prints_the_measure_and_the_ask_and_exits_2(tmp_path, capsys):
    path = write_words(tmp_path, take(2320, 838.0))
    assert ST.main(["--measure", str(path), "--wpm", "170-180"]) == 2
    out = capsys.readouterr().out
    assert "2,320 words" in out and "838.0 s spoken" in out and "166.1 wpm" in out
    assert "ask 170-180 wpm" in out and "OUTSIDE" in out and "re-take" in out


def test_a_take_inside_the_band_exits_0(tmp_path, capsys):
    path = write_words(tmp_path, take(350, 120.0), wrap=False)      # 175 wpm, a bare list
    assert ST.main(["--measure", str(path), "--wpm", "170-180"]) == 0
    out = capsys.readouterr().out
    assert "175.0 wpm" in out and "inside" in out


def test_no_ask_measures_and_says_so(tmp_path, capsys):
    path = write_words(tmp_path, take(100, 60.0))
    assert ST.main(["--measure", str(path)]) == 0
    out = capsys.readouterr().out
    assert "100.0 wpm" in out and "no ask" in out


def test_a_words_file_with_no_words_is_refused_by_name(tmp_path, capsys):
    path = write_words(tmp_path, [])
    assert ST.main(["--measure", str(path), "--wpm", "170-180"]) == 2
    assert "no timed words" in capsys.readouterr().out


def test_the_index_line_carries_the_measure_and_the_ask():
    line = ST.rate_line(ST.measure(take(166, 60.0)), (170.0, 180.0))
    assert line.startswith("rate: 166 words / 60.0 s spoken = 166.0 wpm") and "ask 170-180 wpm" in line
