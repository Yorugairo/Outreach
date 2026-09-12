"""The viewer's window cut (PRP P36 T1): boundaries, memory, screens, no leaks.

Green on synthetic word lists (the cut is pure arithmetic) and on the recorded
ep1 take when it is on disk. The three properties that make the instrument valid
are asserted directly: no word is split across two windows, no beat tag or pause
mark ever reaches what the viewer reads, and a window that carries a chart shows
that chart's title and figures and nothing doctrinal with them (R26-0, E43).
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
    assert set(doc["windows"][0]) == {"i", "start_s", "end_s", "span", "text",
                                      "memory", "screens"}
    assert doc["windows"][0]["screens"] == [] and doc["screens_source"] == "none (no build given)"


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
    # the words, with the `[screen]` lines (R26-0) taken back out: no tag, no mark
    spoken = " ".join(ln for w in doc["windows"] for ln in w["text"].splitlines()
                      if not ln.startswith(V.SCREEN_PREFIX))
    assert "[" not in spoken and "`" not in spoken
    assert doc["screens_source"].endswith(".timeline.json")
    assert doc["windows"][0]["text"].startswith("The safest thing you own")


@needs_ep1
def test_ep1_take_is_found_without_the_timeline_flag():
    text = EP1_SCRIPT.read_text(encoding="utf-8")
    words, source = V.resolve_words(EP1_SCRIPT, text)
    assert source == "measured" and len(words) > 2000

# ---- the screens the viewer can see (R26-0, ruling E43) -------------------

# One scene of the shape a build writes: a ledger page (the chart), a dock that
# lands late in it, three species - two that paint words and one that does not -
# and the doctrine layers (`judge`, `badges`, the species names) that must stay
# behind.
SCENE_TIMELINE = {
    "runtime_s": 40.0,
    "scenes": [
        {"scene_id": "s01", "span": [0.0, 20.0],
         "world": {"kind": "ledger", "page": {
             "title": "Our biggest customer is selling",
             "sub": "Japan's holdings of US Treasuries, $bn, monthly",
             "labels": ["Japan"], "value_strings": ["1,239.3"],
             "series": [{"label": "-9.9%", "name": "Japan"}],
             "badges": ["DERIVED"], "judge": {"note": "G-c intensity 0.18"}}},
         "docks": [{"slide": "dock-h-fed", "enter": 16.0, "exit": 19.5}],
         "species": [
             {"kind": "figure", "at": 5.0, "text": "$1,116.7B",
              "target": {"kind": "datum", "index": 315}},
             {"kind": "bracket", "at": 17.0, "label": "-$122.6B", "sub": "a tenth of the pile"},
             {"kind": "spotlight", "at": 6.0, "target": {"kind": "datum", "index": 315}},
         ]},
        {"scene_id": "s02", "span": [20.0, 40.0],
         "world": {"kind": "clip", "asset_id": "outro"},
         "docks": [{"slide": "dock-k-pledge", "enter": 21.0, "exit": 25.0}],
         "species": []},
    ],
    "evidence": {
        "dock-h-fed": {"title": "The Fed hasn't moved", "species": "chart",
                       "judge": {"verdict": "laundered"}},
        "dock-k-pledge": {"title": "Japan to roll out $65bn in support for chips",
                          "species": "record",
                          "record": {"kicker": "Japan to roll out $65bn",
                                     "words": [["...at", 21.1], ["least", 21.2],
                                               ["10", 21.3], ["trillion", 21.4],
                                               ["yen...", 21.5]]}},
    },
}
DOCTRINE_WORDS = ("judge", "badges", "DERIVED", "spotlight", "bracket", "datum",
                  "species", "scene_id", "G-c", "[promise]", "ledger")


def _build_with_screens(tmp_path, scene=None, **kw):
    """A 40s take plus a scene timeline beside it, as a build has them."""
    script = tmp_path / "SCRIPT-T-VO.txt"
    script.write_text("One test that sorts every holding you own.", encoding="utf-8")
    (tmp_path / "timeline.json").write_text(json.dumps({"words": _ticking(40)}), encoding="utf-8")
    (tmp_path / "ep.timeline.json").write_text(
        json.dumps(SCENE_TIMELINE if scene is None else scene), encoding="utf-8")
    return script, V.build_document(script, script.read_text(encoding="utf-8"),
                                    tmp_path / "timeline.json", **kw)


def test_a_window_carrying_a_chart_shows_its_title_and_its_figures(tmp_path):
    _, doc = _build_with_screens(tmp_path)
    assert doc["screens_source"] == "ep.timeline.json"
    w0 = doc["windows"][0]
    assert w0["screens"][0]["kind"] == "a chart"
    assert w0["screens"][0]["title"] == "Our biggest customer is selling"
    # standing figures (what the page draws) and the figure painted at 5.0s
    assert w0["screens"][0]["figures"] == ["Japan", "1,239.3", "-9.9%", "$1,116.7B"]
    line = [ln for ln in w0["text"].splitlines() if ln.startswith("[screen]")]
    assert len(line) == 1
    assert line[0].startswith('[screen] a chart: "Our biggest customer is selling"')
    assert "Japan's holdings of US Treasuries, $bn, monthly" in line[0]
    assert "showing Japan; 1,239.3; -9.9%; $1,116.7B" in line[0]


def test_no_tag_and_no_doctrine_travels_with_a_screen(tmp_path):
    scene = json.loads(json.dumps(SCENE_TIMELINE))
    scene["scenes"][0]["world"]["page"]["title"] = "`[promise]` Our biggest customer is selling"
    _, doc = _build_with_screens(tmp_path, scene)
    seen = "\n".join(w["text"] + " " + w["memory"] for w in doc["windows"])
    for word in DOCTRINE_WORDS:
        assert word not in seen, word
    assert "Our biggest customer is selling" in seen


def test_a_figure_lands_in_the_window_whose_clock_holds_it(tmp_path):
    _, doc = _build_with_screens(tmp_path)
    w0, w1 = doc["windows"][0], doc["windows"][1]
    assert "$1,116.7B" in w0["text"] and "$1,116.7B" not in w1["text"]
    # the bracket paints at 17.0s and the dock lands at 16.0s: window 1, not window 0
    assert "-$122.6B a tenth of the pile" in w1["text"]
    assert 'a chart: "The Fed hasn\'t moved"' in w1["text"]
    assert "The Fed hasn't moved" not in w0["text"]


def test_a_clipping_reads_as_a_clipping_with_the_line_it_holds_up(tmp_path):
    _, doc = _build_with_screens(tmp_path)
    w1 = doc["windows"][1]      # the record docks at 21.0s
    clipping = [s for s in w1["screens"] if s["kind"] == "a news clipping"]
    assert clipping and clipping[0]["title"].startswith("Japan to roll out $65bn")
    assert "...at least 10 trillion yen..." in w1["text"]


def test_the_words_stay_the_words_and_the_memory_carries_no_screens(tmp_path):
    _, doc = _build_with_screens(tmp_path)
    for w in doc["windows"]:
        assert "[screen]" not in w["memory"]
        assert w["text"].splitlines()[0].startswith("w")     # the spoken words come first
    assert doc["windows"][1]["memory"] == "".join(
        [" ".join(f"w{i}" for i in range(15))])


def test_no_screens_reads_the_words_only(tmp_path):
    _, doc = _build_with_screens(tmp_path, no_screens=True)
    assert doc["screens_source"] == "none (--no-screens)"
    assert all(w["screens"] == [] and "[screen]" not in w["text"] for w in doc["windows"])


def test_a_word_timeline_with_no_scene_timeline_beside_it_says_so(tmp_path):
    script = tmp_path / "SCRIPT-T-VO.txt"
    script.write_text("One test that sorts every holding you own.", encoding="utf-8")
    tl = tmp_path / "timeline.json"
    tl.write_text(json.dumps({"words": _ticking(20)}), encoding="utf-8")
    doc = V.build_document(script, script.read_text(encoding="utf-8"), tl)
    assert doc["screens_source"] == "none found beside timeline.json"
    assert all(w["screens"] == [] for w in doc["windows"])


def test_the_scene_timeline_is_found_from_a_build_directory(tmp_path):
    _, _ = _build_with_screens(tmp_path)
    assert V.scene_timeline_path(tmp_path).name == "ep.timeline.json"
    assert V.scene_timeline_path(tmp_path / "timeline.json").name == "ep.timeline.json"
    assert V.scene_timeline_path(tmp_path / "ep.timeline.json").name == "ep.timeline.json"
    assert V.is_scene_timeline(tmp_path / "timeline.json") is False


def test_one_page_held_across_a_scene_boundary_reads_as_one_screen():
    page = {"title": "Our biggest customer is selling", "labels": ["Japan"]}
    doc = {"scenes": [{"span": [0.0, 8.0], "world": {"kind": "ledger", "page": page}},
                      {"span": [8.0, 20.0], "world": {"kind": "ledger", "page": page}}]}
    screens = V.window_screens(V.screen_records(doc), 0.0, 15.0)
    assert len(screens) == 1 and screens[0]["title"] == "Our biggest customer is selling"


def test_a_screen_with_nothing_written_on_it_is_not_a_screen_line():
    doc = {"scenes": [{"span": [0.0, 10.0], "world": {"kind": "clip", "asset_id": "outro"},
                       "species": [{"kind": "life", "at": 1.0}]}]}
    assert V.window_screens(V.screen_records(doc), 0.0, 15.0) == []


def test_page_figures_read_only_what_is_drawn():
    page = {"labels": ["4%", "4.5%"], "value_strings": ["665", "633"],
            "series": [{"label": "10-year"}], "judge": {"g": "fail"}, "badges": ["DERIVED"]}
    assert V.page_figures(page) == ["4%", "4.5%", "665", "633", "10-year"]


# ---- the real Tokyo short (the take E43 was ruled on) ---------------------

TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
TOKYO_SCRIPT = TOKYO / "SCRIPT-90S-VO.claude.txt"
TOKYO_TIMELINE = TOKYO / "build-short-t0/timeline.json"
needs_tokyo = pytest.mark.skipif(not TOKYO_SCRIPT.exists() or not TOKYO_TIMELINE.exists(),
                                 reason="the Tokyo short's take is not on disk")


@needs_tokyo
def test_tokyo_0_30_to_0_45_carries_the_chart_e43_named():
    text = TOKYO_SCRIPT.read_text(encoding="utf-8")
    doc = V.build_document(TOKYO_SCRIPT, text, TOKYO_TIMELINE)
    assert doc["timing_source"] == "measured"
    assert doc["screens_source"] == "tokyo-short.timeline.json"
    w2 = next(w for w in doc["windows"] if w["span"] == "0:30-0:45")
    assert w2["screens"], "E43's window must carry the chart the blind read could not see"
    assert any(s["title"] == "Our biggest customer is selling" for s in w2["screens"])
    assert "[screen] a chart:" in w2["text"]
    for word in DOCTRINE_WORDS:
        assert word not in w2["text"], word
