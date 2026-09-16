"""The warped-timeline emission and its gate (doc 37 s20 chain promotion).

doc 37 s20 names ONE blocker on promoting `tempo_edit.py` into the chain:
"the warped-timeline emission (each chunk's word times scale by its rate;
pauses shift as in insert_edit_pauses) so docks, captions and choreography
ride the authored clock". These tests are that arithmetic, on synthetic
words and synthetic field rates - `stretch` is replaced by an exact
resampler, so no ffmpeg, no fixture audio and no network run here. The
`--verify` gate against a real take is evidence of a different kind and
lives in the run log, not in pytest.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import tempo_edit as TE  # noqa: E402


# ---------------------------------------------------------------- fixtures

def _name(i: int) -> str:
    """Letters only - a digit in a word would trip the field's own
    number-dense rule and cap the sentence, which is not what these
    tests are measuring."""
    return chr(97 + i // 26) + chr(97 + i % 26)


def _words(n: int = 130, dur: float = 0.30, intra: float = 0.06,
           inter: float = 0.15, per_sentence: int = 6) -> list[dict]:
    """A synthetic take: words never overlap, sentence gaps are wide
    enough to host a chunk boundary (>=120ms, class 5b), intra-sentence
    gaps are not - so no boundary can ever land inside a sentence. Long
    enough (~49s) that the 9s hook hold and the 14s tail hold leave a
    cruising middle, so the field actually varies."""
    out, t = [], 0.0
    for i in range(n):
        last = (i + 1) % per_sentence == 0
        out.append({"w": _name(i) + ("." if last else ""),
                    "start": round(t, 3), "end": round(t + dur, 3)})
        t += dur + (inter if last else intra)
    return out


def _plan(pauses=(), runs=()) -> dict:
    return {"pauses": [dict(p) for p in pauses], "tighten_runs": list(runs)}


@pytest.fixture
def take(tmp_path, monkeypatch):
    """An episode root with the two files `build` reads from disk, and an
    exact stand-in for the WSOLA stretcher."""
    (tmp_path / "SCRIPT-G-VO.txt").write_text("no tags here", encoding="utf-8")
    monkeypatch.setattr(TE, "EP", tmp_path)

    def exact_stretch(seg, rate, pre=0, post=0):
        body = len(seg) - pre - post
        if abs(rate - 1.0) < 0.005 or len(seg) < TE.SR // 25:
            return np.zeros(max(body, 1), dtype="float32")
        return np.zeros(max(int(round(body / rate)), 1), dtype="float32")

    monkeypatch.setattr(TE, "stretch", exact_stretch)
    return tmp_path


def _build(words, plan):
    audio = np.zeros(int(TE.SR * (words[-1]["end"] + 0.4)), dtype="float32")
    return TE.build(words, plan, audio)


def _timeline(words) -> dict:
    return {"words": [dict(w) for w in words],
            "sentences": [{"text": " ".join(x["w"] for x in g),
                           "start": g[0]["start"], "end": g[-1]["end"]}
                          for g in TE.sentence_groups(words)],
            "runtime_s": words[-1]["end"]}


# ------------------------------------------------------- sentence grouping

def test_sentence_groups_split_on_enders():
    groups = TE.sentence_groups(_words(n=12, per_sentence=4))
    assert [len(g) for g in groups] == [4, 4, 4]


def test_sentence_groups_keep_a_dangling_tail():
    groups = TE.sentence_groups(_words(n=10, per_sentence=4))
    assert [len(g) for g in groups] == [4, 4, 2]


def test_sentence_groups_survive_a_closing_quote():
    ws = [{"w": "one", "start": 0.0, "end": 0.2},
          {"w": 'two."', "start": 0.3, "end": 0.5},
          {"w": "three", "start": 0.6, "end": 0.8}]
    assert [len(g) for g in TE.sentence_groups(ws)] == [2, 1]


# ------------------------------------------------------- the warping proper

def test_words_scale_by_their_own_chunks_rate(take):
    """The emission's headline claim: a word inside a chunk is stretched
    by THAT chunk's rate, not by the take's average."""
    words = _words()
    _, to_edited, meta = _build(words, _plan())
    assert len(meta["chunks"]) > 1, "the field must actually vary"
    seen = set()
    for c in meta["chunks"]:
        for w in words:
            if not (c["start"] <= w["start"] and w["end"] <= c["end"]):
                continue
            src = w["end"] - w["start"]
            got = to_edited(w["end"]) - to_edited(w["start"])
            assert got == pytest.approx(src / c["rate"], abs=0.002)
            seen.add(c["rate"])
    assert len(seen) > 1, "more than one rate must have been exercised"


def test_chunk_boundaries_never_fall_inside_a_word(take):
    """class 3 - WORDS ARE NEVER SPLIT; class 5b - and only a gap of
    >=120ms of reported silence may host the cut."""
    words = _words()
    _, _, meta = _build(words, _plan())
    for b in meta["boundaries"]:
        assert not any(w["start"] < b["at"] < w["end"] for w in words)
        assert b["gap_s"] >= TE.MIN_STEP_GAP_S


def test_the_map_is_monotone_across_the_whole_take(take):
    words = _words()
    _, to_edited, _ = _build(words, _plan())
    times = [to_edited(t) for w in words for t in (w["start"], w["end"])]
    assert all(b >= a - 1e-9 for a, b in zip(times, times[1:]))


def test_an_inserted_pause_shifts_everything_after_it(take):
    """The same shape insert_edit_pauses.py produces: words before the
    anchor are untouched, words after move by exactly the pause."""
    words = _words()
    plan = _plan([{"after": _name(29) + ".", "s": 1.2, "kind": "key-post"}])
    _, _, meta = _build(words, plan)
    assert [i["s"] for i in meta["inserts"]] == [1.2]
    at = meta["inserts"][0]["at"]
    flat = [dict(p, ins_s=0.0) if p["o0"] is None else p
            for p in meta["pieces"]]
    for w in words:
        shift = (TE.constructed_time(w["start"], meta["pieces"])
                 - TE.constructed_time(w["start"], flat))
        assert shift == pytest.approx(1.2 if w["start"] > at else 0.0,
                                      abs=1e-6)


def test_the_pause_lands_between_the_two_words_it_separates(take):
    words = _words()
    plan = _plan([{"after": _name(29) + ".", "s": 1.2, "kind": "key-post"}])
    _, to_edited, meta = _build(words, plan)
    gap = words[30]["start"] - words[29]["end"]
    rate = next(c["rate"] for c in meta["chunks"]
                if c["start"] <= words[29]["end"] <= c["end"])
    grown = to_edited(words[30]["start"]) - to_edited(words[29]["end"])
    # the original gap, warped, plus the pause, less the two crossfades
    assert grown == pytest.approx(gap / rate + 1.2 - 2 * TE.XF / TE.SR,
                                  abs=0.02)


def test_a_dead_space_cap_shortens_the_gap_it_caps(take):
    """The other half of the one pass: an over-cap gap is compressed to
    its target, and the words either side keep their own duration."""
    words = _words()
    for w in words[30:]:                      # a 1.6s hole before w30
        w["start"] = round(w["start"] + 1.4, 3)
        w["end"] = round(w["end"] + 1.4, 3)
    _, to_edited, meta = _build(words, _plan())
    assert meta["cuts"] == 1
    grown = to_edited(words[30]["start"]) - to_edited(words[29]["end"])
    assert grown < 0.9, "the inter-sentence cap is 0.65s"
    src = words[30]["end"] - words[30]["start"]
    rate = next(c["rate"] for c in meta["chunks"]
                if c["start"] <= words[30]["start"] <= c["end"])
    assert (to_edited(words[30]["end"]) - to_edited(words[30]["start"])
            == pytest.approx(src / rate, abs=0.002))


def _kept(meta, a: float, b: float) -> float:
    """How much ORIGINAL take time between two instants survived into the
    render - rate-free, so it measures the edit and not the stretcher."""
    return sum(min(p["o1"], b) - max(p["o0"], a) for p in meta["pieces"]
               if p["o0"] is not None and p["o1"] > a and p["o0"] < b)


def _over_cap_anchored_take():
    """A gap that is BOTH over the inter-sentence cap and carries a pause
    anchor - the case the two ops used to fight over."""
    words = _words()
    for w in words[30:]:                      # a 1.55s hole after w29.
        w["start"] = round(w["start"] + 1.4, 3)
        w["end"] = round(w["end"] + 1.4, 3)
    plan = _plan([{"after": _name(29) + ".", "s": 1.2, "kind": "key-post"}])
    return words, plan


def test_an_over_cap_anchored_gap_is_capped_once_not_half_undone(take):
    """REGRESSION (the cut/ins ordering defect): the cap advanced the read
    head past the silence it discarded, then the insertion reset it to the
    RAW gap's midpoint - behind it - so (g - tgt)/2 of capped silence came
    back. The gap must keep exactly the target, never the target/2 plus
    half the raw gap."""
    words, plan = _over_cap_anchored_take()
    a, b = words[29]["end"], words[30]["start"]
    _, _, meta = _build(words, plan)
    assert meta["merged"] == 1, "the pause must merge into the cap"
    assert meta["regressions"] == [], "the read head must never rewind"
    assert b - a == pytest.approx(1.55, abs=1e-6)
    assert _kept(meta, a, b) == pytest.approx(TE.INTERT, abs=1e-6)
    # the defect kept INTERT/2 + (b - a)/2 instead
    assert _kept(meta, a, b) < TE.INTERT / 2 + (b - a) / 2 - 0.4


def test_the_pause_sits_in_the_middle_of_the_silence_that_survives(take):
    """class 2 - an insertion snaps to the MIDPOINT of its silence gap.
    After a cap that means the midpoint of what the cap left: half the
    target either side, not target/2 before and half the raw gap after."""
    words, plan = _over_cap_anchored_take()
    a, b = words[29]["end"], words[30]["start"]
    _, _, meta = _build(words, plan)
    i = next(i for i, p in enumerate(meta["pieces"]) if p["o0"] is None)
    before = [p for p in meta["pieces"][:i] if p["o0"] is not None][-1]
    after = next(p for p in meta["pieces"][i:] if p["o0"] is not None)
    assert before["o1"] == pytest.approx(a + TE.INTERT / 2, abs=1e-6)
    assert after["o0"] == pytest.approx(b - TE.INTERT / 2, abs=1e-6)


def test_the_merged_gap_carries_the_cap_and_the_pause_and_nothing_else(take):
    words, plan = _over_cap_anchored_take()
    a, b = words[29]["end"], words[30]["start"]
    _, to_edited, meta = _build(words, plan)
    rate = next(c["rate"] for c in meta["chunks"]
                if c["start"] <= a <= c["end"])
    grown = to_edited(words[30]["start"]) - to_edited(words[29]["end"])
    assert grown == pytest.approx(
        TE.INTERT / rate + 1.2 - 2 * TE.XF / TE.SR, abs=0.03)


def test_an_anchor_in_an_under_cap_gap_stays_a_bare_insertion(take):
    """Nothing merges when there is no cap: the natural gap survives
    whole and the pause is planted at its midpoint, as before."""
    words = _words()
    plan = _plan([{"after": _name(29) + ".", "s": 1.2, "kind": "key-post"}])
    a, b = words[29]["end"], words[30]["start"]
    _, _, meta = _build(words, plan)
    assert meta["merged"] == 0 and meta["cuts"] == 0
    assert meta["regressions"] == []
    assert _kept(meta, a, b) == pytest.approx(b - a, abs=1e-6)


def test_two_anchors_in_one_capped_gap_both_land(take):
    words, plan = _over_cap_anchored_take()
    plan["pauses"].append({"before": _name(30), "s": 0.4, "kind": "key-pre"})
    _, _, meta = _build(words, plan)
    assert meta["merged"] == 1 and meta["regressions"] == []
    planted = sum(p["ins_s"] for p in meta["pieces"] if p["o0"] is None)
    assert planted == pytest.approx(1.6, abs=1e-6)


def test_constructed_time_agrees_with_the_rendered_map(take):
    """G4's oracle is genuinely a second opinion: summing the preceding
    chunk scalings and insertions reaches the same clock the piece
    lengths do."""
    words = _words()
    plan = _plan([{"after": _name(29) + ".", "s": 1.2, "kind": "key-post"}])
    _, to_edited, meta = _build(words, plan)
    for w in words:
        assert TE.constructed_time(w["start"], meta["pieces"]) == \
            pytest.approx(to_edited(w["start"]), abs=5e-4)


# ------------------------------------------------------- warp_timeline

def test_warp_timeline_rewrites_words_sentences_and_the_clock(take):
    words = _words()
    tl = _timeline(words)
    _, to_edited, meta = _build(words, _plan())
    TE.warp_timeline(tl, to_edited, 41.234, meta)
    assert tl["runtime_s"] == 41.234
    assert len(tl["words"]) == len(words)
    assert tl["words"][0]["start"] == pytest.approx(0.0, abs=1e-6)
    assert tl["words"][-1]["end"] < words[-1]["end"], "the take was tightened"
    for sn, g in zip(tl["sentences"], TE.sentence_groups(tl["words"])):
        assert sn["start"] == pytest.approx(g[0]["start"], abs=0.002)
        assert sn["end"] == pytest.approx(g[-1]["end"], abs=0.002)


def test_warp_timeline_sets_the_keys_downstream_actually_reads(take):
    """`build_scene_timeline_f.py` and `render_episode.py` pick the voice
    track with `paused_audio` guarded by `edit_pauses_applied`;
    `dead_space_compressed` is the ORDER guard the two-tool path checks;
    `tempo_field_applied` is this tool's re-run refusal."""
    words = _words()
    tl = _timeline(words)
    _, to_edited, meta = _build(words, _plan())
    TE.warp_timeline(tl, to_edited, 41.0, meta)
    assert tl["paused_audio"] == "audio/episode-paused.mp3"
    assert tl["edit_pauses_applied"] is True
    assert tl["dead_space_compressed"] is True
    assert tl["tempo_field_applied"] is True
    assert tl["tempo_field"]["chunks"] == len(meta["chunks"])
    json.dumps(tl)                      # the emitted timeline stays JSON


def test_warp_timeline_keeps_every_other_field(take):
    words = _words()
    tl = _timeline(words)
    tl["episode"], tl["take"] = "synthetic", "vo-x"
    tl["words"][3]["part"] = 2
    _, to_edited, meta = _build(words, _plan())
    TE.warp_timeline(tl, to_edited, 41.0, meta)
    assert tl["episode"] == "synthetic" and tl["take"] == "vo-x"
    assert tl["words"][3]["part"] == 2


def test_warp_timeline_output_passes_its_own_monotonicity_gate(take):
    words = _words()
    tl = _timeline(words)
    _, to_edited, meta = _build(words, _plan(
        [{"after": _name(29) + ".", "s": 1.2, "kind": "key-post"}]))
    TE.warp_timeline(tl, to_edited, 41.0, meta)
    assert TE.gate_monotonic(tl["words"])["verdict"] == "PASS"
    assert TE.gate_words_preserved(words, tl["words"])["verdict"] == "PASS"


# ------------------------------------------------------- the gate says no

def test_g1_catches_an_overlap():
    ws = [{"w": "a", "start": 0.0, "end": 1.0},
          {"w": "b", "start": 0.8, "end": 1.5}]
    r = TE.gate_monotonic(ws)
    assert r["verdict"] == "FAIL" and "before" in r["detail"]


def test_g1_catches_an_inverted_word():
    ws = [{"w": "a", "start": 1.0, "end": 0.5}]
    assert TE.gate_monotonic(ws)["verdict"] == "FAIL"


def test_g2_catches_a_dropped_word():
    src = [{"w": "a"}, {"w": "b"}]
    assert TE.gate_words_preserved(src, src[:1])["verdict"] == "FAIL"


def test_g2_catches_a_rewritten_word():
    src = [{"w": "a"}, {"w": "b"}]
    out = [{"w": "a"}, {"w": "B"}]
    r = TE.gate_words_preserved(src, out)
    assert r["verdict"] == "FAIL" and "'b' -> 'B'" in r["detail"]


@pytest.mark.parametrize("measured,verdict",
                         [(100.02, "PASS"), (100.2, "FAIL")])
def test_g3_measures_the_clock_against_the_file(measured, verdict):
    assert TE.gate_clock(100.0, measured)["verdict"] == verdict


def test_g4_catches_an_anchor_that_moved():
    pieces = [{"o0": 0.0, "o1": 10.0, "rate": 1.0, "ins_s": None}]
    src = [{"w": "one", "start": 1.0, "end": 1.4},
           {"w": "two", "start": 2.0, "end": 2.4}]
    good = [dict(w) for w in src]
    bad = [dict(w) for w in src]
    bad[1]["start"] += 0.4
    bad[1]["end"] += 0.4
    pcm = np.ones(int(TE.SR * 10), dtype="float32")
    meta = {"pieces": pieces}
    assert TE.gate_anchors(src, good, meta, pcm)["verdict"] == "PASS"
    assert TE.gate_anchors(src, bad, meta, pcm)["verdict"] == "FAIL"


def test_g4_catches_a_word_pointing_at_silence():
    pieces = [{"o0": 0.0, "o1": 10.0, "rate": 1.0, "ins_s": None}]
    src = [{"w": "one", "start": 1.0, "end": 1.4}]
    pcm = np.ones(int(TE.SR * 10), dtype="float32")
    pcm[int(TE.SR * 0.9):int(TE.SR * 1.5)] = 0.0
    r = TE.gate_anchors(src, src, {"pieces": pieces}, pcm)
    assert r["verdict"] == "FAIL" and "silent" in r["detail"]


def _meta(chunks, bounds):
    return {"chunks": chunks, "boundaries": bounds}


def test_g5a_catches_a_chunk_under_the_wsola_floor():
    rows = TE.gate_rate_sanity(_meta(
        [{"start": 0.0, "end": 0.10, "rate": 1.0}], []))
    assert rows[0]["id"] == "G5a" and rows[0]["verdict"] == "FAIL"


def test_g5b_catches_a_rate_step_outside_a_real_silence():
    rows = TE.gate_rate_sanity(_meta(
        [{"start": 0.0, "end": 5.0, "rate": 1.0}],
        [{"at": 2.0, "gap_s": 0.04, "rate_before": 1.0, "rate_after": 1.1}]))
    assert rows[1]["id"] == "G5b" and rows[1]["verdict"] == "FAIL"


def test_g5c_warns_by_default_and_fails_under_strict():
    meta = _meta([{"start": 0.0, "end": 5.0, "rate": 1.0}],
                 [{"at": 2.0, "gap_s": 0.3, "rate_before": 1.0,
                   "rate_after": 1.12}])
    assert TE.gate_rate_sanity(meta)[2]["verdict"] == "WARN"
    assert TE.gate_rate_sanity(meta, strict=True)[2]["verdict"] == "FAIL"


def test_g5c_passes_when_the_step_is_inside_the_doc_limit():
    meta = _meta([{"start": 0.0, "end": 5.0, "rate": 1.0}],
                 [{"at": 2.0, "gap_s": 0.3, "rate_before": 1.0,
                   "rate_after": 1.01}])
    assert TE.gate_rate_sanity(meta, strict=True)[2]["verdict"] == "PASS"


def test_print_table_returns_non_zero_on_a_fail(capsys):
    rows = [TE.row("G1", "a", True, "ok"), TE.row("G2", "b", False, "no")]
    assert TE.print_table(rows) == 1
    assert "FAIL" in capsys.readouterr().out


def test_print_table_returns_zero_when_only_warns(capsys):
    rows = [TE.row("G1", "a", True, "ok"),
            TE.row("G5c", "b", False, "loud", warn=True)]
    assert TE.print_table(rows) == 0
    assert "WARN" in capsys.readouterr().out


# ------------------------------------------------------- the source loader

def test_load_source_timeline_reads_a_provider_words_file(tmp_path):
    p = tmp_path / "scene_9.words.json"
    p.write_text(json.dumps({"words": [
        {"w": "One", "start_s": 0.0, "end_s": 0.4},
        {"w": "two.", "start_s": 0.5, "end_s": 0.9}]}), encoding="utf-8")
    tl = TE.load_source_timeline(p)
    assert tl["words"] == [{"w": "One", "start": 0.0, "end": 0.4},
                           {"w": "two.", "start": 0.5, "end": 0.9}]
    assert tl["sentences"][0]["text"] == "One two."


def test_load_source_timeline_refuses_an_already_edited_clock(tmp_path):
    p = tmp_path / "timeline.json"
    p.write_text(json.dumps({"words": [], "tempo_field_applied": True}),
                 encoding="utf-8")
    with pytest.raises(SystemExit):
        TE.load_source_timeline(p)
