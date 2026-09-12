"""TR-2: where a picture change sits relative to the narration (the J/L-cut question).

`measure_cut_offsets.py` has to be checkable without the reference video and without the
reference's 20-minute caption file, so every unit here drives it with a SYNTHETIC VTT whose
word onsets are chosen by hand:

    one 0.00  two 0.20  three 0.40  | 0.80 s pause | four 1.20  five 1.40  six 1.60
    | 0.40 s pause | seven 2.00  eight 2.20  nine 2.40

Rule (a) Delta t >= 0.30 s sees two pauses: [0.40, 1.20] and [1.60, 2.00].
Rule (b) Delta t >= 0.45 s sees one:        [0.40, 1.20].

Three boundaries exercise the three verdicts: one inside the pause (at 0.80 of it - doc 46
sec 46.3's median), one before it (picture leads / L-cut-like) and one after it (audio leads
into the new shot / J-cut-like).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import measure_cut_offsets as MO  # noqa: E402

FPS = 30.0

SYNTHETIC_VTT = """WEBVTT
Kind: captions
Language: en

00:00:00.000 --> 00:00:00.390 align:start position:0%

one<00:00:00.200><c> two</c><00:00:00.400><c> three</c>

00:00:00.390 --> 00:00:00.400 align:start position:0%
one two three


00:00:01.200 --> 00:00:01.990 align:start position:0%
one two three
four<00:00:01.400><c> five</c><00:00:01.600><c> six</c>

00:00:01.990 --> 00:00:02.000 align:start position:0%
four five six


00:00:02.000 --> 00:00:02.600 align:start position:0%
four five six
seven<00:00:02.200><c> eight</c><00:00:02.400><c> nine</c>
"""

# boundary, t_s, kind
SYNTHETIC_BOUNDARIES = [
    (1, 1.04, "hard-cut"),   # inside [0.40, 1.20] at 0.80 of the pause
    (2, 0.32, "dip"),        # 80 ms BEFORE the pause opens - picture leads
    (3, 1.32, "blur-zoom"),  # 120 ms AFTER the pause closes - audio leads
]


@pytest.fixture()
def vtt(tmp_path: Path) -> Path:
    p = tmp_path / "synthetic.en.vtt"
    p.write_text(SYNTHETIC_VTT, encoding="utf-8")
    return p


@pytest.fixture()
def boundaries_csv(tmp_path: Path) -> Path:
    p = tmp_path / "boundaries.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["boundary", "t_s", "kind", "duration_frames"])
        for b, t, k in SYNTHETIC_BOUNDARIES:
            w.writerow([b, t, k, 1])
    return p


# --- the VTT parser -------------------------------------------------------------------

def test_vtt_parser_reads_inline_word_timestamps_not_cue_starts(vtt: Path):
    words = MO.parse_vtt_words(vtt)
    assert [w for w, _ in words] == [
        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"
    ]
    assert [round(t, 3) for _, t in words] == [
        0.0, 0.2, 0.4, 1.2, 1.4, 1.6, 2.0, 2.2, 2.4
    ]


def test_vtt_parser_skips_the_roll_up_cues_that_carry_no_word_timing(vtt: Path):
    # nine words, not the 9 + 6 the repeated context lines would add
    assert len(MO.parse_vtt_words(vtt)) == 9


def test_onset_intervals_are_the_gaps_a_caption_only_source_can_state(vtt: Path):
    onsets = [t for _, t in MO.parse_vtt_words(vtt)]
    assert MO.onset_gaps(onsets, 0.30) == [(0.4, 1.2), (1.6, 2.0)]
    assert MO.onset_gaps(onsets, 0.45) == [(0.4, 1.2)]


# --- the offset of one boundary against one rule ---------------------------------------

def test_boundary_inside_the_pause_is_on_the_pause_and_reports_its_fraction(vtt: Path):
    gaps = MO.onset_gaps([t for _, t in MO.parse_vtt_words(vtt)], 0.30)
    off = MO.offset(1.04, gaps)
    assert off["in_gap"] is True
    assert off["verdict"] == MO.ON_PAUSE
    assert off["gap_start"] == pytest.approx(0.40)
    assert off["gap_end"] == pytest.approx(1.20)
    assert off["off_start_ms"] == pytest.approx(640.0, abs=0.5)
    assert off["off_end_ms"] == pytest.approx(-160.0, abs=0.5)
    assert off["pos_in_gap"] == pytest.approx(0.80, abs=1e-6)


def test_boundary_before_the_pause_means_the_picture_leads(vtt: Path):
    gaps = MO.onset_gaps([t for _, t in MO.parse_vtt_words(vtt)], 0.30)
    off = MO.offset(0.32, gaps)
    assert off["in_gap"] is False
    assert off["verdict"] == MO.PICTURE_LEADS
    assert off["off_start_ms"] == pytest.approx(-80.0, abs=0.5)   # negative = picture first
    assert off["pos_in_gap"] is None


def test_boundary_after_the_pause_means_the_audio_led_into_the_new_shot(vtt: Path):
    gaps = MO.onset_gaps([t for _, t in MO.parse_vtt_words(vtt)], 0.30)
    off = MO.offset(1.32, gaps)
    assert off["in_gap"] is False
    assert off["verdict"] == MO.AUDIO_LEADS
    assert off["off_end_ms"] == pytest.approx(120.0, abs=0.5)     # positive past gap_end
    # the nearest pause is the one it just left, not the next one 280 ms away
    assert off["gap_end"] == pytest.approx(1.20)


def test_the_two_rules_disagree_when_the_narrower_pause_drops_out(vtt: Path):
    onsets = [t for _, t in MO.parse_vtt_words(vtt)]
    a = MO.offset(1.98, MO.onset_gaps(onsets, 0.30))
    b = MO.offset(1.98, MO.onset_gaps(onsets, 0.45))
    assert a["verdict"] == MO.ON_PAUSE and a["gap_start"] == pytest.approx(1.60)
    assert b["verdict"] == MO.AUDIO_LEADS and b["gap_end"] == pytest.approx(1.20)


def test_nearest_word_edge_is_signed_and_uses_the_word_grid_not_the_gap_grid(vtt: Path):
    edges = MO.word_edges([t for _, t in MO.parse_vtt_words(vtt)])
    assert MO.nearest_word_edge_ms(1.04, edges) == pytest.approx(-160.0, abs=0.5)
    assert MO.nearest_word_edge_ms(0.32, edges) == pytest.approx(-80.0, abs=0.5)
    assert MO.nearest_word_edge_ms(2.40, edges) == pytest.approx(0.0, abs=0.5)


def test_no_gap_at_all_yields_a_row_with_no_verdict():
    assert MO.offset(1.0, []) == {
        "gap_start": None, "gap_end": None, "off_start_ms": None,
        "off_end_ms": None, "in_gap": False, "pos_in_gap": None, "verdict": MO.NO_GAP,
    }


# --- the whole pass, and the csv round-trip --------------------------------------------

def test_build_rows_carries_the_kind_through_from_the_boundary_csv(vtt: Path, boundaries_csv: Path):
    rows = MO.build_rows(MO.load_boundaries(boundaries_csv), MO.parse_vtt_words(vtt))
    assert [r["kind"] for r in rows] == ["hard-cut", "dip", "blur-zoom"]
    assert [r["verdict_a"] for r in rows] == [MO.ON_PAUSE, MO.PICTURE_LEADS, MO.AUDIO_LEADS]
    assert rows[0]["pos_in_gap_a"] == pytest.approx(0.80, abs=1e-6)
    assert rows[2]["in_gap_b"] is False


def test_csv_round_trip_preserves_every_field(tmp_path: Path, vtt: Path, boundaries_csv: Path):
    rows = MO.build_rows(MO.load_boundaries(boundaries_csv), MO.parse_vtt_words(vtt))
    out = MO.write_csv(rows, tmp_path / "offsets.csv")
    back = list(csv.DictReader(out.read_text(encoding="utf-8").splitlines()))
    assert list(back[0]) == MO.FIELDS
    assert len(back) == len(rows)
    assert back[0]["kind"] == "hard-cut"
    assert float(back[0]["off_a_start_ms"]) == pytest.approx(640.0, abs=0.5)
    assert float(back[0]["pos_in_gap_a"]) == pytest.approx(0.80, abs=0.01)
    assert back[1]["in_gap_a"] == "no"
    assert float(back[2]["off_a_end_ms"]) == pytest.approx(120.0, abs=0.5)
    assert back[2]["pos_in_gap_a"] == ""


def test_summary_reports_the_distribution_and_the_three_shares(vtt: Path, boundaries_csv: Path):
    rows = MO.build_rows(MO.load_boundaries(boundaries_csv), MO.parse_vtt_words(vtt))
    s = MO.summarise(rows, "a")
    assert s["n"] == 3
    assert s["in_gap"] == 1 and s["picture_leads"] == 1 and s["audio_leads"] == 1
    assert s["share_in_gap"] == pytest.approx(1 / 3, abs=1e-3)
    # the median of the three signed offsets to gap_end: -160, -900, +120
    assert s["off_end_ms"]["p50"] == pytest.approx(-160.0, abs=0.5)
    assert s["off_end_frames"]["p50"] == pytest.approx(-160.0 / (1000 / FPS), abs=0.01)


def test_percentiles_interpolate_and_stay_ordered():
    xs = [0.0, 10.0, 20.0, 30.0, 40.0]
    assert MO.pct(xs, 0.50) == pytest.approx(20.0)
    assert MO.pct(xs, 0.10) == pytest.approx(4.0)
    assert MO.pct(xs, 0.90) == pytest.approx(36.0)
    assert MO.pct([], 0.5) is None


def test_tr13_verdict_reads_our_scene_timeline_and_names_the_cut_and_the_centred_dip(tmp_path: Path):
    """TR-13 (P52 T11): `--scenes` turns the compiler's scene timeline into boundaries (every scene end but the last, kind =
    the exit name) and `tr13_rows` gives the verdict against the next word's onset: a cut 100 ms (3 frames) before it is
    `cut-3f`, a dip ON it is `dip-centred`, a boundary a full gap early is `off`."""
    import json
    scenes = {"scenes": [{"scene_id": "s01", "exit": "cut", "span": [0.0, 1.10]},          # "four" starts at 1.20: the cut 100 ms before it
                         {"scene_id": "s02", "exit": "dip:0.4", "span": [1.10, 2.00]},     # "seven" starts at 2.00: the dip's black on it
                         {"scene_id": "s03", "exit": "cut", "span": [2.00, 2.20]},         # a boundary that is nowhere near a lead
                         {"scene_id": "s04", "exit": "cut", "span": [2.20, 3.0]}]}
    p = tmp_path / "x-short.timeline.json"
    p.write_text(json.dumps(scenes), encoding="utf-8")
    bounds = MO.scene_boundaries(p)
    assert [(b["boundary"], b["t_s"], b["kind"]) for b in bounds] == [("s01>s02", 1.10, "cut"), ("s02>s03", 2.00, "dip"), ("s03>s04", 2.20, "cut")]
    onsets = [0.0, 0.2, 0.4, 1.2, 1.4, 1.6, 2.0, 2.2, 2.4]
    rows = MO.tr13_rows(MO.build_rows(bounds, [(str(i), t) for i, t in enumerate(onsets)]), onsets, FPS)
    assert [r["tr13"] for r in rows] == ["cut-3f", "dip-centred", "off"]
    assert round(rows[0]["lead_ms"]) == 100 and round(rows[1]["lead_ms"]) == 0 and rows[2]["onset_s"] == 2.2
    # a build's own timeline.json is a words file: start/end keys read like s/e
    w = tmp_path / "timeline.json"
    w.write_text(json.dumps({"words": [{"w": "a", "start": 0.0, "end": 0.1}, {"w": "b", "start": 1.2, "end": 1.3}]}), encoding="utf-8")
    words, ends = MO.load_words(w)
    assert words == [("a", 0.0), ("b", 1.2)] and ends == [0.1, 1.3]
