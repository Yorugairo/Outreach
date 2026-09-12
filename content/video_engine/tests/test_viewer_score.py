"""P36 T3 - the viewer's scorer. No live calls: every report here is recorded."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import viewer_score as V  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "viewer"


# --- the fixture: a script whose [rehook] is declared but never felt ---------
SCRIPT = (
    "`[promise]` By the end you will run one test yourself, thirty seconds a stock. "
    "It sorts what you hold into steel or paper. "
    "`[rehook]` But the interesting part is who paid for the steel. "
    "Nothing much happens in this stretch and it simply keeps going. "
    "`[new]` Between 2020 and 2024 the builders borrowed twenty-eight billion dollars a year. "
    "Last year the number was a hundred and twenty-one billion."
)


def _windows() -> dict:
    texts = [
        "By the end you will run one test yourself, thirty seconds a stock. It sorts what you hold into steel or paper.",
        "But the interesting part is who paid for the steel.",
        "Nothing much happens in this stretch and it simply keeps going.",
        "Between 2020 and 2024 the builders borrowed twenty-eight billion dollars a year. "
        "Last year the number was a hundred and twenty-one billion.",
    ]
    ws = []
    for i, t in enumerate(texts):
        ws.append({"i": i, "start_s": 15.0 * i, "end_s": 15.0 * (i + 1),
                   "span": f"{int(15 * i // 60)}:{int(15 * i % 60):02d}-{int(15 * (i + 1) // 60)}:{int(15 * (i + 1) % 60):02d}",
                   "text": t, "memory": " ".join(texts[max(0, i - 2):i])})
    return {"schema_version": "viewer_windows.v1", "window_s": 15.0, "memory_windows": 2,
            "timing_source": "measured", "runtime_s": 60.0, "windows": ws}


def _reports() -> dict:
    return {"schema_version": "viewer_reports.v1", "prompt_version": "v1", "model": "test", "effort": "high",
            "reports": [
                {"i": 0, "new_things": ["there is a test I can run in thirty seconds a stock",
                                        "holdings sort into steel or paper"],
                 "held_question": "what are the three questions?", "asked_of_me": "run the test", "could_not_follow": []},
                # window 1 carries the [rehook] sentence but the reader felt nothing of it
                {"i": 1, "new_things": [], "held_question": "", "asked_of_me": "", "could_not_follow": []},
                {"i": 2, "new_things": [], "held_question": "", "asked_of_me": "", "could_not_follow": ["who is 'they'"]},
                {"i": 3, "new_things": ["the builders borrowed twenty-eight billion a year",
                                        "last year it was a hundred and twenty-one billion"],
                 "held_question": "where did the extra borrowing go?", "asked_of_me": "", "could_not_follow": []},
            ]}


@pytest.fixture()
def scored():
    return V.score(_windows(), _reports(), SCRIPT)


# --- beat recall -------------------------------------------------------------
def test_a_declared_beat_the_reader_never_felt_drops_recall_below_100(scored):
    by_tag = {r["tag"]: r for r in scored["recall"]}
    assert by_tag["promise"]["perceived"] and by_tag["new"]["perceived"]
    assert not by_tag["rehook"]["perceived"], by_tag["rehook"]
    assert scored["recall_pct"] < 100.0
    v01 = next(r for r in scored["rows"] if r["id"] == "V01")
    assert v01["level"] == "FAIL" and "[rehook]" in v01["message"], v01


def test_recall_cites_the_readers_own_line(scored):
    promise = next(r for r in scored["recall"] if r["tag"] == "promise")
    assert "thirty seconds" in promise["matched"]
    assert promise["matched_window"] in (promise["window"] - 1, promise["window"], promise["window"] + 1)


def test_a_beat_felt_one_window_late_still_counts():
    reports = _reports()
    reports["reports"][2]["new_things"] = ["someone paid for the steel"]      # the rehook, felt one window late
    res = V.score(_windows(), reports, SCRIPT)
    assert next(r for r in res["recall"] if r["tag"] == "rehook")["perceived"]


# --- gain, dead runs, loops, confusion ---------------------------------------
def test_two_windows_with_nothing_concrete_are_a_dead_run(scored):
    assert scored["dead"] == [1, 2]
    assert scored["dead_runs"] == [[1, 2]]
    v02 = next(r for r in scored["rows"] if r["id"] == "V02")
    assert v02["level"] == "WARN" and "dead-run" in v02["message"]


def test_open_loop_coverage_and_confusion_are_reported(scored):
    v03 = next(r for r in scored["rows"] if r["id"] == "V03")
    assert "2/4" in v03["message"] and v03["level"] == "PASS"     # exactly at the 50% floor
    v04 = next(r for r in scored["rows"] if r["id"] == "V04")
    assert v04["level"] == "WARN" and "who is" in v04["message"]


def test_concreteness_rule_counts_numerals_names_and_new_words():
    assert V.is_concrete("borrowed twenty-eight billion in 2024", "2024 borrowing", "")
    assert V.is_concrete("a man named Karp said it", "Karp said", "")
    assert V.is_concrete("the buildout is leased", "the buildout is leased", "nothing about that")
    assert not V.is_concrete("it keeps going", "nothing much happens and it keeps going", "it keeps going")
    assert not V.is_concrete("", "x", "")


def test_gain_counts_only_concrete_things(scored):
    per = {p["i"]: p for p in scored["per_window"]}
    assert per[0]["gain"] == 2 and per[3]["gain"] == 2
    assert per[1]["gain"] == 0 and per[2]["gain"] == 0


# --- plumbing ----------------------------------------------------------------
def test_sentence_at_takes_the_sentence_the_tag_precedes():
    s = V.sentence_at(SCRIPT, SCRIPT.index("`[rehook]`"))
    assert s == "But the interesting part is who paid for the steel."


def test_the_viewer_never_sees_tags_in_a_scored_sentence():
    for b in V.declared_beats(SCRIPT):
        assert "[" not in b["sentence"] and "`" not in b["sentence"]


def test_render_is_deterministic_and_carries_the_result_line(scored):
    a = V.render(scored, "X-VO.txt")
    b = V.render(V.score(_windows(), _reports(), SCRIPT), "X-VO.txt")
    assert a == b
    assert "RESULT: 1 FAIL / 2 WARN" in a and "| `[rehook]` |" in a and "**NO**" in a


def test_paths_strip_the_vo_suffix(tmp_path):
    w, r, o = V.paths_for(tmp_path / "SCRIPT-G-VO.txt")
    assert w.name == "SCRIPT-G-VIEWER-WINDOWS.json"
    assert r.name == "SCRIPT-G-VIEWER-REPORTS.json"
    assert o.name == "SCRIPT-G-VIEWER.md"


def test_main_writes_the_report(tmp_path, capsys):
    script = tmp_path / "T-VO.txt"
    script.write_text(SCRIPT, encoding="utf-8")
    (tmp_path / "T-VIEWER-WINDOWS.json").write_text(json.dumps(_windows()), encoding="utf-8")
    (tmp_path / "T-VIEWER-REPORTS.json").write_text(json.dumps(_reports()), encoding="utf-8")
    assert V.main([str(script)]) == 0
    assert "RESULT:" in capsys.readouterr().out
    assert (tmp_path / "T-VIEWER.md").exists()


def test_main_refuses_without_the_inputs(tmp_path, capsys):
    script = tmp_path / "T-VO.txt"
    script.write_text(SCRIPT, encoding="utf-8")
    assert V.main([str(script)]) == 2
    assert "viewer_windows.py" in capsys.readouterr().err


# --- the recorded fixture on disk (the plan's "recorded reports as fixtures") --
def test_recorded_fixture_pair_scores_the_same_way():
    wp, rp = FIXTURES / "windows.json", FIXTURES / "reports.json"
    if not (wp.exists() and rp.exists()):
        pytest.skip("recorded viewer fixtures absent")
    res = V.score(json.loads(wp.read_text(encoding="utf-8")),
                  json.loads(rp.read_text(encoding="utf-8")), SCRIPT)
    assert res["recall_pct"] < 100.0 and res["dead_runs"]


def test_a_window_cut_is_our_artifact_not_the_scripts_defect():
    # ep1 calibration 2026-09-03: 20 of 42 "could not follow" items were the 15s cut itself
    reports = _reports()
    reports["reports"][0]["could_not_follow"] = ["The sentence ending with 'Different voice' is incomplete.",
                                                 "Who exactly 'they' refers to."]
    res = V.score(_windows(), reports, SCRIPT)
    p0 = res["per_window"][0]
    assert p0["could_not_follow"] == ["Who exactly 'they' refers to."]
    assert len(p0["window_cuts"]) == 1


def test_a_promise_is_perceived_when_the_reader_files_it_under_asked_of_me():
    """A promise beat is what the reader reports as an ask, not as a fact (2026-09-04)."""
    script = "Rates rose. `[pre-key]` [promise] By the end you'll read that number yourself off the table. "
    windows = {"schema_version": "viewer_windows.v1", "window_s": 15.0, "memory_windows": 2,
               "timing_source": "estimated", "runtime_s": 15.0,
               "windows": [{"i": 0, "start_s": 0.0, "end_s": 15.0, "span": "0:00-0:15",
                            "text": "Rates rose. By the end you'll read that number yourself off the table.", "memory": ""}]}
    reports = {"reports": [{"i": 0, "span": "0:00-0:15", "new_things": ["Rates went up."],
                            "held_question": "", "asked_of_me": "Read that number for myself off the table by the end.",
                            "could_not_follow": []}]}
    res = V.score(windows, reports, script)
    promise = [r for r in res["recall"] if r["tag"] == "promise"][0]
    assert promise["perceived"], promise


def test_a_ring_sentence_maps_to_the_window_that_speaks_it_not_the_opener_it_echoes():
    windows = [{"i": 0, "text": "Tokyo took a tea break and left America the tab. The Fed sat still."},
               {"i": 1, "text": "Nothing here."},
               {"i": 2, "text": "The Fed still sat still. Tokyo is still on its tea break, and America still holds the tab."}]
    assert V.window_of_sentence(windows, "Tokyo is still on its tea break, and America still holds the tab.") == 2
    assert V.window_of_sentence(windows, "Tokyo took a tea break and left America the tab.") == 0


# --- V01 and the screens (R26-0, ruling E43) ---------------------------------
# The shorts case the ruling was written on: two beats sit on one sentence whose
# numbers the CHART carries, so the words of the beat are never echoed back. The
# window now ends in the `[screen]` line viewer_windows.py folds in.
CHART_SCRIPT = (
    "The opponent isn't the Fed; it's a Japanese balance sheet. "
    "`[promise]` [rehook] Two numbers show where the money went: a Treasury page, and your phone."
)
CHART_SCREEN = {"kind": "a chart", "title": "Our biggest customer is selling",
                "sub": "Japan's holdings of US Treasuries, $bn, monthly since 2000",
                "figures": ["Japan", "-9.9%", "$1,116.7B"]}


def _chart_windows(with_screens: bool = True) -> dict:
    spoken = ("The opponent isn't the Fed; it's a Japanese balance sheet. "
              "Two numbers show where the money went: a Treasury page, and your phone.")
    screens = [CHART_SCREEN] if with_screens else []
    text = spoken if not screens else (
        spoken + '\n[screen] a chart: "Our biggest customer is selling" - '
        "Japan's holdings of US Treasuries, $bn, monthly since 2000 - "
        "showing Japan; -9.9%; $1,116.7B")
    return {"schema_version": "viewer_windows.v1", "window_s": 15.0, "memory_windows": 2,
            "timing_source": "measured", "screens_source": "ep.timeline.json", "runtime_s": 15.0,
            "windows": [{"i": 0, "start_s": 0.0, "end_s": 15.0, "span": "0:30-0:45",
                         "text": text, "memory": "", "screens": screens}]}


def _chart_reports(names_the_figure: bool) -> dict:
    saw = ("Japan's holdings are down to $1,116.7B" if names_the_figure
           else "Something is going on with the Fed")
    return {"schema_version": "viewer_reports.v1", "prompt_version": "v2", "model": "test",
            "reports": [{"i": 0, "span": "0:30-0:45", "new_things": [saw],
                         "held_question": "", "asked_of_me": "", "could_not_follow": []}]}


def test_a_chart_carried_beat_counts_when_the_reader_names_the_screens_figure():
    res = V.score(_chart_windows(), _chart_reports(True), CHART_SCRIPT)
    by_tag = {r["tag"]: r for r in res["recall"]}
    assert by_tag["promise"]["perceived"] and by_tag["rehook"]["perceived"]
    assert by_tag["promise"]["via"] == "screen"
    assert by_tag["promise"]["screen_figure"] == "$1,116.7B"
    assert "$1,116.7B" in by_tag["promise"]["matched"]
    v01 = next(r for r in res["rows"] if r["id"] == "V01")
    assert v01["level"] == "PASS" and "off a screen's figure (E43)" in v01["message"]
    assert "yes (screen)" in V.render(res, "X-VO.txt")


def test_the_same_beat_with_no_figure_named_is_still_a_miss():
    res = V.score(_chart_windows(), _chart_reports(False), CHART_SCRIPT)
    by_tag = {r["tag"]: r for r in res["recall"]}
    assert not by_tag["promise"]["perceived"] and not by_tag["rehook"]["perceived"]
    assert by_tag["promise"]["via"] == "" and by_tag["promise"]["screen_figure"] == ""
    v01 = next(r for r in res["rows"] if r["id"] == "V01")
    assert v01["level"] == "FAIL" and "screen" not in v01["message"]


def test_with_no_screen_in_the_window_the_verdict_is_exactly_the_old_one():
    named = V.score(_chart_windows(with_screens=False), _chart_reports(True), CHART_SCRIPT)
    blind = V.score(_chart_windows(with_screens=False), _chart_reports(False), CHART_SCRIPT)
    for res in (named, blind):
        assert all(not r["perceived"] for r in res["recall"])
        assert next(r for r in res["rows"] if r["id"] == "V01")["level"] == "FAIL"


def test_a_reader_saying_the_figure_in_plain_digits_still_matches():
    reports = _chart_reports(True)
    reports["reports"][0]["new_things"] = ["Japan is down to about 1116.7 billion dollars"]
    res = V.score(_chart_windows(), reports, CHART_SCRIPT)
    assert next(r for r in res["recall"] if r["tag"] == "promise")["via"] == "screen"


def test_the_words_rule_still_wins_when_the_reader_echoed_the_sentence():
    reports = _chart_reports(True)
    reports["reports"][0]["new_things"] = ["two numbers show where the money went: a page and my phone",
                                           "Japan's holdings are $1,116.7B"]
    res = V.score(_chart_windows(), reports, CHART_SCRIPT)
    promise = next(r for r in res["recall"] if r["tag"] == "promise")
    assert promise["perceived"] and promise["via"] == "words"


def test_figure_numbers_read_the_same_number_through_its_punctuation():
    assert V.figure_numbers("$1,116.7B") == {"1116.7"}
    assert V.figure_numbers("-$122.6B a tenth of the pile") == {"122.6"}
    assert V.figure_numbers("3.97% - the February low") == {"3.97"}
    assert V.figure_numbers("no number here") == set()


def test_a_screen_line_is_not_the_spoken_text():
    w = {"i": 0, "text": 'said this.\n[screen] a chart: "a title" - showing 42', "memory": ""}
    assert V.spoken_text(w) == "said this."
    # placement and the concreteness rule read the words, so the screen cannot move a beat
    assert V.window_of_sentence([w], "said this.") == 0
    assert not V.is_concrete("a title", V.spoken_text(w), "")   # score() passes the words


def test_a_multi_word_label_counts_and_a_one_word_country_never_does():
    """A named figure is a NUMBER or a label named by at least two of its own words."""
    screens = [{"kind": "a chart", "title": "Our biggest customer is selling", "sub": "",
                "figures": ["Japan", "The opponent: a balance sheet"]}]
    named = "The speaker says a Japanese balance sheet is driving this, rather than the Fed."
    assert V.screen_figure_hit(screens, named) == "The opponent: a balance sheet"
    # "Japan" is the episode's own vocabulary, not something read off the screen
    assert V.screen_figure_hit(screens, "Japan is America's biggest lender") != "Japan"
    assert V.screen_figure_hit([{"kind": "a chart", "title": "", "sub": "",
                                 "figures": ["Japan"]}], "Japan is selling") == ""
    assert V.label_hit("The opponent: a balance sheet", "a balance sheet, apparently")
    assert not V.label_hit("Japan", "Japan is selling")
    assert V.screen_figure_hit(screens, "nothing like it") == ""
