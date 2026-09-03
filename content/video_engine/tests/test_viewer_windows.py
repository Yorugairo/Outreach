"""The viewer's window cut (PRP P36 T1): boundaries, memory, and no leaks.

Green on synthetic word lists (the cut is pure arithmetic) and on the recorded
ep1 take when it is on disk. The two properties that make the instrument valid
are asserted directly: no word is split across two windows, and no beat tag or
pause mark ever reaches what the viewer reads.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import viewer_windows as V  # noqa: E402

EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
EP1_SCRIPT = EP / "SCRIPT-G-VO.txt"
EP1_TIMELINE = EP / "build-f/timeline.json"
needs_ep1 = pytest.mark.skipif(not EP1_SCRIPT.exists() or not EP1_TIMELINE.exists(),
                               reason="episode one script/take not on disk")


def _words(pairs):
    """[(word, start, end)] -> the load_timings word shape."""
    return [{"w": w, "start": s, "end": e} for w, s, e in pairs]


def _ticking(n, step=1.0):
    """n one-word-per-`step` seconds, each word named for its index."""
    return _words([(f"w{i}", i * step, i * step + step * 0.8) for i in range(n)])


# ---- the cut --------------------------------------------------------------

def test_windows_cut_on_word_boundaries_with_mmss_spans():
    ws = V.build_windows(_ticking(40))          # 40 words, one per second
    assert [w["i"] for w in ws] == [0, 1, 2]
    assert [w["span"] for w in ws] == ["0:00-0:15", "0:15-0:30", "0:30-0:45"]
    assert [w["start_s"] for w in ws] == [0.0, 15.0, 30.0]
    assert ws[0]["text"].split() == [f"w{i}" for i in range(15)]
    assert ws[2]["text"].split() == [f"w{i}" for i in range(30, 40)]


def test_no_word_is_split_across_two_windows():
    # w14 starts at 14.6 and finishes at 15.4: it belongs to window 0 whole,
    # and window 0's end_s reports where it actually stops.
    ws = V.build_windows(_words([("early", 0.0, 0.4), ("w14", 14.6, 15.4),
                                 ("after", 15.6, 16.0)]))
    assert ws[0]["text"] == "early w14" and ws[1]["text"] == "after"
    assert ws[0]["end_s"] == 15.4
    seen = [t for w in ws for t in w["text"].split()]
    assert len(seen) == len(set(seen)) == 3


def test_empty_window_keeps_the_index_on_the_clock():
    ws = V.build_windows(_words([("first", 0.0, 0.5), ("late", 31.0, 31.5)]))
    assert [w["text"] for w in ws] == ["first", "", "late"]
    assert ws[1]["span"] == "0:15-0:30" and ws[1]["end_s"] == 30.0


def test_span_formats_minutes_past_ten():
    ws = V.build_windows(_words([("late", 806.0, 806.4)]))
    assert ws[-1]["span"] == "13:15-13:30"


# ---- the rolling memory ---------------------------------------------------

def test_memory_is_exactly_the_previous_two_windows():
    ws = V.build_windows(_ticking(60))
    assert ws[0]["memory"] == ""
    assert ws[1]["memory"] == ws[0]["text"]
    assert ws[2]["memory"] == f"{ws[0]['text']} {ws[1]['text']}"
    assert ws[3]["memory"] == f"{ws[1]['text']} {ws[2]['text']}"
    assert ws[0]["text"] not in ws[3]["memory"]


def test_memory_windows_is_configurable():
    ws = V.build_windows(_ticking(60), memory_windows=1)
    assert ws[2]["memory"] == ws[1]["text"]
    assert V.build_windows(_ticking(60), memory_windows=0)[3]["memory"] == ""


# ---- no doctrine leaks ----------------------------------------------------

TAGGED = (
    "The safest thing you own looks like this. `[promise]` One test that sorts "
    "every holding you own. `[post-key]` And the opponent is a machine. "
    "[rehook] But a machine you can test. `[pre-key]` The spike stays on the desk."
)


def test_beat_tags_and_pause_marks_never_reach_the_viewer(tmp_path):
    script = tmp_path / "SCRIPT-T-VO.txt"
    script.write_text(TAGGED, encoding="utf-8")
    doc = V.build_document(script, TAGGED)
    seen = " ".join(w["text"] + " " + w["memory"] for w in doc["windows"])
    for mark in ("[promise]", "[post-key]", "[rehook]", "[pre-key]", "`["):
        assert mark not in seen, mark
    assert "One test" in seen and "machine" in seen


def test_marks_in_a_transcript_are_stripped_from_the_words():
    ws = V.build_windows(_words([("`[promise]`", 0.0, 0.0), ("One", 0.2, 0.4),
                                 ("test.", 0.5, 0.9)]))
    assert ws[0]["text"] == "One test."


# ---- the estimated fallback ----------------------------------------------

def test_estimated_when_no_take_exists(tmp_path):
    script = tmp_path / "SCRIPT-T-VO.txt"
    body = " ".join(["word"] * 400)
    script.write_text(body, encoding="utf-8")
    doc = V.build_document(script, body)
    assert doc["timing_source"] == "estimated"
    # 400 x "word " = 2000 chars at 16.29 chars/sec ~ 122s -> 9 windows
    assert doc["runtime_s"] == pytest.approx(len(body) / V.CHARS_PER_SEC, abs=1e-3)
    assert len(doc["windows"]) == 9
    assert all(w["text"] for w in doc["windows"])


def test_measured_when_a_timeline_is_given(tmp_path):
    script = tmp_path / "SCRIPT-T-VO.txt"
    script.write_text("One test that sorts every holding.", encoding="utf-8")
    tl = tmp_path / "timeline.json"
    tl.write_text(json.dumps({"words": _ticking(20)}), encoding="utf-8")
    doc = V.build_document(script, script.read_text(encoding="utf-8"), tl)
    assert doc["timing_source"] == "measured"
    assert [w["i"] for w in doc["windows"]] == [0, 1]
    assert doc["windows"][0]["text"].startswith("w0 w1")


def test_unreadable_timeline_falls_back_to_the_estimate(tmp_path):
    script = tmp_path / "SCRIPT-T-VO.txt"
    script.write_text("One test that sorts every holding you own.", encoding="utf-8")
    doc = V.build_document(script, script.read_text(encoding="utf-8"), tmp_path / "missing.json")
    assert doc["timing_source"] == "estimated"


# ---- the file and its determinism ----------------------------------------

def test_windows_path_drops_the_vo_suffix(tmp_path):
    assert V.windows_path(tmp_path / "SCRIPT-G-VO.txt").name == "SCRIPT-G-VIEWER-WINDOWS.json"


def test_written_json_is_byte_identical_across_runs(tmp_path):
    script = tmp_path / "SCRIPT-T-VO.txt"
    script.write_text(TAGGED, encoding="utf-8")
    first = V.write_windows(V.build_document(script, TAGGED), tmp_path / "a.json").read_bytes()
    second = V.write_windows(V.build_document(script, TAGGED), tmp_path / "b.json").read_bytes()
    assert first == second
    doc = json.loads(first.decode("utf-8"))
    assert doc["schema_version"] == "viewer_windows.v1"
    assert doc["window_s"] == 15.0 and doc["memory_windows"] == 2
    assert set(doc["windows"][0]) == {"i", "start_s", "end_s", "span", "text", "memory"}


def test_main_writes_beside_the_script(tmp_path):
    script = tmp_path / "SCRIPT-T-VO.txt"
    script.write_text(TAGGED, encoding="utf-8")
    assert V.main([str(script)]) == 0
    assert (tmp_path / "SCRIPT-T-VIEWER-WINDOWS.json").exists()


def test_main_refuses_a_script_with_no_spoken_words(tmp_path):
    script = tmp_path / "SCRIPT-T-VO.txt"
    script.write_text("# a heading only\n", encoding="utf-8")
    assert V.main([str(script)]) == 2


# ---- the real episode -----------------------------------------------------

@needs_ep1
def test_ep1_cuts_into_about_54_measured_windows():
    text = EP1_SCRIPT.read_text(encoding="utf-8")
    doc = V.build_document(EP1_SCRIPT, text, EP1_TIMELINE)
    assert doc["timing_source"] == "measured"
    assert 52 <= len(doc["windows"]) <= 56, len(doc["windows"])
    assert doc["runtime_s"] > 780
    seen = " ".join(w["text"] for w in doc["windows"])
    assert "[" not in seen and "`" not in seen
    assert doc["windows"][0]["text"].startswith("The safest thing you own")


@needs_ep1
def test_ep1_take_is_found_without_the_timeline_flag():
    text = EP1_SCRIPT.read_text(encoding="utf-8")
    words, source = V.resolve_words(EP1_SCRIPT, text)
    assert source == "measured" and len(words) > 2000
