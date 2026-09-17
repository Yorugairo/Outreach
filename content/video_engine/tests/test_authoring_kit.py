"""The authoring kit (P51 T0): the mechanism both shorts now write their shot table through.

The kit is pure - every episode fact arrives as an argument - so these tests run on synthetic
words, synthetic cards and synthetic rows, and the last one greps the package for the episode
facts that must never live in it.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import audio_spectrum as SP  # noqa: E402
import build_scene_timeline_f as B  # noqa: E402
import master_vo_tone as MT  # noqa: E402
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
    # ... under M13's gap rule, the pin the two approved shorts carry; the default since TR-13 (P52 T11) is the onset rule
    assert W.cut_before(TAKE, "Your costs", rule="gap") == 1.80
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


def test_page_transitions_cut_reads_past_a_page_option():
    bare = "ledger:ev-meta-yield-v1:bars:3:right:mount=2.43:cut"
    assert A.page_transitions(bare)["cut"] is True
    assert A.page_transitions(bare + ";form=extruded_bar")["cut"] is True
    assert A.page_transitions(bare + ";depth=0.5;form=extruded_bar")["cut"] is True
    assert A.page_transitions("ledger:ev-x:line:3:right:mount=0.4")["cut"] is False
    assert A.page_transitions("ledger:ev-x:line:3:right:mount=0.4;form=extruded_bar")["cut"] is False


def test_page_transitions_then_and_idle_keep_the_shipped_suffix_reading():
    assert A.page_transitions("ledger:ev-x:line:3:right:mount=0.4:cut;then=ev-y:line")["cut"] is False
    assert A.page_transitions("ledger:ev-x:line:3:right:mount=0.4:cut;form=extruded_bar;then=ev-y:line")["cut"] is False
    assert A.page_transitions("ledger:ev-x:line:3:right:cut;idle=drift")["cut"] is False


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


# ---------------------------------------------------------------- the VO tone chain (the operator's A/B, chain G)
APPROVED_CHAIN = ("highpass=f=70:poles=2,equalizer=f=280:t=q:w=0.9:g=-3.2,equalizer=f=800:t=q:w=2.2:g=5,"
                  "equalizer=f=1400:t=q:w=1.3:g=-4,equalizer=f=2600:t=q:w=3.0:g=6,"
                  "equalizer=f=11000:t=q:w=1.0:g=5,treble=f=7000:g=2")


def test_the_vo_tone_chain_is_the_ruling_verbatim():
    """The operator chose chain G off an A/B (2026-09-16, E99 s54, amending s48's chain C); the kit
    carries that string and nothing else."""
    assert A.vo_tone_filter() == APPROVED_CHAIN
    assert len(A.VO_TONE) == 7 and A.vo_tone_filter().count(",") == 6


def test_the_vo_tone_chain_carries_no_rejected_stage():
    """What the A/B REFUSED must not creep back in: a cut at 3.2 kHz, a notch at 350 Hz, any
    saturation, and above all any loudnorm - the stage is level-neutral or the bed math drifts."""
    chain = A.vo_tone_filter()
    for rejected in ("3200", "3.2k", "f=350", "asoftclip", "aexciter", "acrusher", "acompressor",
                     "alimiter", "loudnorm", "dynaudnorm", "speechnorm"):
        assert rejected not in chain, f"a rejected stage came back into the chain: {rejected}"
    assert "atempo" not in chain and "rubberband" not in chain, "a tone stage may never retime the take"


def test_the_trim_is_flat_appended_last_and_sized_off_the_measured_peak():
    """The A/B was judged at matched loudness, so it ruled TONE and set no level. The level is one flat
    `volume=` trim, sized per file, LAST - flat moves every band by the same number, so it cannot touch
    the ruled tone, and the chain in front of it stays byte-identical."""
    assert A.vo_makeup_db(-2.01) == 0.51 and A.vo_makeup_db(-0.13) == -1.37
    assert A.vo_makeup_db(-0.13, target=-2.0) == -1.87 and A.VO_TP_TARGET_DBTP == -1.5
    # -2.01 dBTP is what chain G measured on the Steel and Paper take, so the trim goes UP; chain C's
    # own -0.13 dBTP pulled it down. The sign is per file, never per chain.
    trimmed = A.vo_tone_filter(A.vo_makeup_db(-2.01))
    assert trimmed == APPROVED_CHAIN + ",volume=0.51dB"
    assert trimmed.startswith(A.vo_tone_filter()), "the ruled chain is untouched in front of the trim"
    for rejected in ("alimiter", "loudnorm", "acompressor", "asoftclip"):
        assert rejected not in trimmed, f"level is a flat gain, never {rejected}"


def _bell_db(f0: float, q: float, gain_db: float, at_hz: float, fs: int = 48000) -> float:
    """The dB an ffmpeg `equalizer=t=q` peaking bell puts at `at_hz` - the RBJ biquad, evaluated.
    Lets a test reason about what the stages do to each OTHER, not just what each one claims."""
    amp = 10 ** (gain_db / 40)
    w0 = 2 * math.pi * f0 / fs
    alpha, cos_w0 = math.sin(w0) / (2 * q), math.cos(w0)
    b = (1 + alpha * amp, -2 * cos_w0, 1 - alpha * amp)
    a = (1 + alpha / amp, -2 * cos_w0, 1 - alpha / amp)
    z = np.exp(-1j * 2 * math.pi * at_hz / fs)
    return float(20 * np.log10(abs((b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z))))


def test_the_vo_tone_chain_cuts_twice_and_is_no_longer_a_half_correction():
    """G is a FULL correction, not s48's half one: two cuts (280 Hz and 1400 Hz) against four lifts,
    and the biggest lift is +6, where chain C's ceiling was +4."""
    gains = [float(re.search(r"g=(-?[\d.]+)", s).group(1)) for s in A.VO_TONE if "g=" in s]
    assert [g for g in gains if g < 0] == [-3.2, -4.0], "280 Hz and 1400 Hz, in that order"
    assert sorted(g for g in gains if g > 0) == [2.0, 5.0, 5.0, 6.0] and max(gains) == 6.0
    assert A.VO_TONE[0].startswith("highpass=f=70")


def test_the_1400_hz_cut_is_not_redundant_and_must_not_be_deleted():
    """WHY the odd stage exists. C's wide 800 and 2700 bells had skirts that SUMMED in the gap between
    them, pushing 1-2 kHz over a region the raw take already had right. G narrows both bells AND cuts
    what is left at 1400. Anyone tempted to delete the cut as redundant should read this test: the
    narrowing alone does not close the gap, and the cut is doing more than closing it."""
    c_sum = _bell_db(800, 1.2, 3, 1400) + _bell_db(2700, 0.9, 4, 1400)
    g_sum = _bell_db(800, 2.2, 5, 1400) + _bell_db(2600, 3.0, 6, 1400)
    assert c_sum > 2.4, f"chain C really did pile up in the gap: {c_sum:+.2f} dB at 1400 Hz"
    assert g_sum < c_sum - 1.0, f"narrowing the bells took most of it out: {g_sum:+.2f} dB"
    assert g_sum > 0.5, f"... but NOT all of it - the gap still sits proud at {g_sum:+.2f} dB"
    # the cut more than cancels that residue, which is why the measured band reads about -2.8 and not 0
    net = g_sum + _bell_db(1400, 1.3, -4, 1400) + _bell_db(280, 0.9, -3.2, 1400)
    assert net < -2.0, f"with the cut, 1400 Hz ends up genuinely down: {net:+.2f} dB"
    assert abs(net - MT.BAND_TOL[1400.0][0]) < MT.BAND_TOL[1400.0][1], "and the gate expects that number"


# ---------------------------------------------------------------- the 1/3-octave measurement the gate reads
def _spectrum(n: int, seed: int, magnitude=None) -> np.ndarray:
    """Noise built in the FREQUENCY domain from a chosen magnitude and a random phase - so a test can
    shape one band exactly and the band power is the magnitude, not a draw. Returned at unit RMS."""
    freqs = np.fft.rfftfreq(n, 1 / SP.SR)
    mag = np.ones(freqs.size) if magnitude is None else magnitude(freqs)
    phase = np.random.default_rng(seed).uniform(0, 2 * np.pi, freqs.size)
    x = np.fft.irfft(mag * np.exp(1j * phase), n)
    return (x / np.sqrt((x ** 2).mean())).astype(np.float32)


def _noise(n: int = 96000, seed: int = 7) -> np.ndarray:
    """Flat-spectrum noise at unit RMS."""
    return _spectrum(n, seed)


def _boosted(n: int, lo: float, hi: float, db: float, seed: int = 7) -> np.ndarray:
    """The same noise with [lo, hi) Hz lifted by `db` - a synthetic equalizer with a known answer.
    Not renormalised: an absolute band reading has to see the lift where it was applied."""
    freqs = np.fft.rfftfreq(n, 1 / SP.SR)
    lift = np.where((freqs >= lo) & (freqs < hi), 10 ** (db / 20), 1.0)
    phase = np.random.default_rng(seed).uniform(0, 2 * np.pi, freqs.size)
    flat = np.fft.irfft(np.exp(1j * phase), n)
    return (np.fft.irfft(lift * np.exp(1j * phase), n) / np.sqrt((flat ** 2).mean())).astype(np.float32)


def test_the_third_octave_grid_steps_by_a_third_of_an_octave():
    centres = SP.iso_third_octave_centres()
    assert centres[0] == 25.0 and centres[-1] < 17000
    assert all(round(b / a, 6) == round(2 ** (1 / 3), 6) for a, b in zip(centres, centres[1:]))
    assert any(abs(fc - 1000) < 10 for fc in centres), "the 1 kHz band is on the grid"


def test_band_levels_put_a_tone_in_its_own_band_and_nowhere_else():
    t = np.arange(96000) / SP.SR
    sine = np.sin(2 * np.pi * 1000 * t).astype(np.float32)
    levels = SP.band_levels(sine, centres=[500.0, 1000.0, 2000.0], shape=False)
    assert levels[1000.0] - max(levels[500.0], levels[2000.0]) > 40, "a pure tone sits in one band"


def test_a_known_boost_reads_back_as_the_band_delta():
    """The gate's whole job: output-minus-input in absolute band dB IS the filter's response."""
    before = SP.band_levels(_noise(), centres=[500.0, 1000.0, 2000.0], shape=False)
    after = SP.band_levels(_boosted(96000, 890.0, 1130.0, 6.0), centres=[500.0, 1000.0, 2000.0], shape=False)
    deltas = SP.band_deltas(before, after)
    assert abs(deltas[1000.0] - 6.0) < 0.5
    assert abs(deltas[500.0]) < 0.5 and abs(deltas[2000.0]) < 0.5, "an untouched band does not move"


def test_the_shape_reading_is_level_invariant_and_the_absolute_one_is_not():
    """`shape=True` compares two DIFFERENT files (a reference mastered hotter is not brighter);
    `shape=False` compares one file before and after a filter, where the gain is the point."""
    x = _noise()
    centres = [500.0, 1000.0, 2000.0]
    quiet, loud = SP.band_levels(x, centres=centres), SP.band_levels(x * 4, centres=centres)
    assert all(abs(loud[fc] - quiet[fc]) < 0.01 for fc in centres)
    absolute = SP.band_deltas(SP.band_levels(x, centres=centres, shape=False),
                              SP.band_levels(x * 4, centres=centres, shape=False))
    assert all(abs(d - 20 * math.log10(4)) < 0.01 for d in absolute.values())


def test_a_falling_spectrum_reads_as_a_falling_band_curve():
    """Monotonic in, monotonic out: 1/f noise has to step DOWN band by band, or the band edges are wrong."""
    pink = _spectrum(96000, seed=3, magnitude=lambda f: 1 / np.maximum(f, 1.0))
    levels = SP.band_levels(pink, centres=[fc for fc in SP.iso_third_octave_centres() if 100 <= fc <= 8000],
                            shape=False)
    curve = list(levels.values())
    # octave by octave (three bands), because one third-octave step is inside the frame gate's own wobble
    assert all(b < a for a, b in zip(curve, curve[3:])), f"1/f noise did not fall octave by octave: {curve}"
    assert curve[0] - curve[-1] > 12, "seven octaves of 1/f have to lose real level"


def test_the_speech_gate_drops_the_quiet_half_of_the_frames():
    """Frames under the median frame RMS are not voice; dropping them is what makes two takes with
    different amounts of silence comparable in shape."""
    loud, quiet = _noise(96000), _noise(96000, seed=11) * 0.001
    alternating = np.concatenate([np.concatenate([loud[i:i + 8192], quiet[i:i + 8192]])
                                  for i in range(0, 8192 * 6, 8192)])
    rms = lambda a: float(np.sqrt((np.asarray(a, dtype=float) ** 2).mean()))
    kept = SP.speech_frames(alternating)
    assert kept.shape[1] == SP.FRAME and 0 < kept.shape[0] < len(alternating) // SP.HOP
    assert rms(kept) > rms(alternating), "the average moved up: the quiet frames are out of it"
    assert rms(kept) > 100 * rms(quiet), "... and what it kept is the voice, not the silence"
    with pytest.raises(ValueError):
        SP.speech_frames(np.zeros(100, dtype=np.float32))


def test_to_json_makes_the_band_reading_round_trip():
    levels = SP.band_levels(_noise(), centres=[500.0, 1000.0], shape=False)
    assert json.loads(json.dumps(SP.to_json(levels))) == {"500.0": levels[500.0], "1000.0": levels[1000.0]}


# ---------------------------------------------------------------- the gate the tone stage ships with
def _measured(dur: float, lufs: float, tp: float, bands: dict) -> dict:
    return {"duration_s": dur, "lufs": lufs, "tp_dbtp": tp, "bands_db": SP.to_json(bands)}


UNTONED = _measured(390.326, -18.8, -2.41, {fc: 0.0 for fc in MT.PROBE_BANDS})
TRIM = 0.51            # what chain G computed on the Steel and Paper take (it measured -2.01 dBTP)
BIG_TRIM = -1.63       # ... and what chain C computed on the same take, kept because the size matters below
# chain G's own response, MEASURED on the real take with audio_spectrum.band_levels, no trim applied.
# Not the nominal gains: +5 at 800 Hz reads +3.16 and +6 at 2600 Hz reads +4.45, because a narrow bell
# is averaged across a 1/3-octave band wider than itself.
CHAIN_G = {280.0: -3.16, 800.0: 3.16, 1400.0: -2.75, 2600.0: 4.45, 8000.0: 3.79, 11000.0: 6.96}
LANDED = {fc: db + TRIM for fc, db in CHAIN_G.items()}


def _episode(tmp_path: Path, declared: str | None) -> Path:
    """A take inside an episode that either declares a VO_LUFS literal or wires no bed at all."""
    take = tmp_path / "an-episode/vo-f/audio/scene_1.mp3"
    take.parent.mkdir(parents=True)
    if declared is not None:
        (tmp_path / "an-episode/build_short.py").write_text(declared, encoding="utf-8")
    return take


def test_the_tone_gate_passes_a_take_the_chain_and_the_trim_landed_on(tmp_path):
    take = _episode(tmp_path, "PLATFORM = 'yt'\nVO_LUFS = -20.5   # measured\n")
    after = _measured(390.326, -20.53, -1.77, LANDED)
    rows = MT.gate_rows(take, UNTONED, after, TRIM)
    assert [label.split()[0] for label, _, _ in rows] == [
        "G1", "G2", "G3", "G4a", "G4b", "G4c", "G4d", "G4e", "G4f", "G5"]
    assert all(s == MT.PASS for _, s, _ in rows), MT.report_text(take, rows)


def test_the_gate_reads_the_band_deltas_with_the_flat_trim_taken_back_out():
    """The trim moves every band by the same number; G4 is about TONE, so it is removed before the
    comparison. How much that MATTERS depends on the trim's size, which is why both sizes are pinned."""
    after = _measured(390.326, -20.53, -1.77, LANDED)
    assert all(s == MT.PASS for l, s, _ in MT.gate_rows(Path("x.mp3"), UNTONED, after, TRIM) if l.startswith("G4"))
    # chain G's trim is small (+0.51) against windows of 1.0-2.0, so leaving it in flips NOTHING here:
    # on this take the subtraction is invisible, and a gate that only works by luck is not a gate.
    small = [l.split()[0] for l, s, _ in MT.gate_rows(Path("x.mp3"), UNTONED, after, 0.0) if s == MT.FAIL]
    assert small == []
    # ... so the size that proves the point is a REAL one this stage produced: chain C's -1.63 on this
    # same take. Then five of the six rows fail and 11 kHz still scrapes through on its wider window -
    # exactly the half-working gate the subtraction exists to prevent.
    big = _measured(390.326, -21.41, -1.77, {fc: db + BIG_TRIM for fc, db in CHAIN_G.items()})
    left_in = [l.split()[0] for l, s, _ in MT.gate_rows(Path("x.mp3"), UNTONED, big, 0.0) if s == MT.FAIL]
    assert left_in == ["G4a", "G4b", "G4c", "G4d", "G4e"], "11 kHz (G4f) survives on its +/-2.0 window"
    assert all(s == MT.PASS for l, s, _ in MT.gate_rows(Path("x.mp3"), UNTONED, big, BIG_TRIM) if l.startswith("G4"))


def test_the_tone_gate_fails_a_retime_a_hot_peak_a_missed_trim_and_a_chain_that_never_landed():
    flat = _measured(390.4, -19.8, -0.13, {fc: 0.0 for fc in MT.PROBE_BANDS})
    rows = MT.gate_rows(Path("x.mp3"), UNTONED, flat, 0.0)
    assert [l.split()[0] for l, s, _ in rows if s == MT.FAIL] == [
        "G1", "G3", "G4a", "G4b", "G4c", "G4d", "G4e", "G4f", "G5"]
    assert "VERDICT: FAIL (9 FAIL)" in MT.report_text(Path("x.mp3"), rows)
    # ... and the tolerances are the ruled ones, loose on purpose: this proves the chain ran, it is not an EQ check
    assert (MT.DUR_TOL_S, MT.VO_LUFS_TOL, MT.TP_CEIL_DBTP, MT.TP_LAND_TOL) == (0.005, 0.3, -1.0, 0.5)
    assert MT.BAND_TOL == {280.0: (-3.2, 1.0), 800.0: (3.2, 1.5), 1400.0: (-2.8, 1.5),
                           2600.0: (4.5, 1.5), 8000.0: (3.8, 1.5), 11000.0: (7.0, 2.0)}
    assert tuple(MT.BAND_TOL) == MT.PROBE_BANDS, "every probed band is gated, in the row order a-f"


def test_g2_fails_a_bed_literal_the_toned_take_has_moved_under_and_names_the_line(tmp_path):
    """The failure nothing else in the pipeline catches: the take is re-mastered, `VO_LUFS` is not, and
    `bed_gain` puts the bed at the wrong level under every cue in silence."""
    take = _episode(tmp_path, "BED_LU = 20.0\nVO_LUFS, BED_LU, BED_LUFS = -17.2, 20.0, -13.03\n")
    label, status, value = MT.vo_lufs_row(take, -19.78)
    assert status == MT.FAIL and "-17.2 declared vs -19.78 measured (-2.58 LU)" in value
    assert value.endswith("build_short.py:2"), "the row names the exact line to edit"
    assert MT.vo_lufs_row(take, -17.0)[1] == MT.PASS, "within the tolerance the literal still stands"


def test_g2_is_not_a_failure_for_an_episode_that_wires_no_bed(tmp_path):
    """Steel and Paper's long-form cut declares no VO_LUFS - there is no bed to drift."""
    label, status, value = MT.vo_lufs_row(_episode(tmp_path, None), -19.78)
    assert status == MT.NA and "wires no bed" in value
    assert MT.NA not in (MT.PASS, MT.FAIL)
    rows = MT.gate_rows(_episode(tmp_path / "b", None), UNTONED, _measured(390.326, -19.78, -1.5, LANDED), TRIM)
    assert "VERDICT: PASS (0 FAIL)" in MT.report_text(Path("x.mp3"), rows)


def test_the_new_vo_lufs_line_is_paste_ready(tmp_path):
    line = MT.vo_lufs_line(tmp_path / "scene_1.mp3", -19.78)
    assert line.startswith("VO_LUFS = -19.8   # ") and "post-tone, measured " in line
    ns: dict = {}
    exec(compile(line, "<paste>", "exec"), ns)
    assert ns["VO_LUFS"] == -19.8, "the printed line has to be valid Python the operator can paste"


def test_the_tone_stage_never_composes_its_own_chain():
    """The ruling lives in the kit; the stage asks for it. A second copy of the string is a second ruling,
    and the trim is composed in the kit too so the stage cannot append a filter of its own."""
    import ast
    src = (ROOT / "content/video_engine/scripts/master_vo_tone.py").read_text(encoding="utf-8")
    assert "vo_tone_filter(" in src and "vo_makeup_db(" in src
    tree = ast.parse(src)
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body
            and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
    literals = [n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs]
    # prose may NAME the filters (the docstrings explain them); no string the stage actually builds may be one
    for token in ("equalizer=", "highpass=", "treble=", "volume="):
        assert not [s for s in literals if token in s], f"the stage composed a filter of its own: {token}"


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
    # P55 T8 (2026-09-13) added `effects.py` - the effects-catalogue resolver - and P56 T5 (2026-09-13) `recipes.py` - the
    # recipe presets (a beat as a proven combination, E96) - and P66 T3 (2026-09-17) `shapes.py` - the shape compiler
    # (the approved skeleton as the BASE the agent modifies, E99 s68) - to the kit by design; the pin moves with them
    assert sorted(p.name for p in KIT.glob("*.py")) == ["__init__.py", "audio.py", "docks.py", "effects.py", "recipes.py", "shapes.py", "table.py", "words.py"]


def test_tr13_the_onset_rule_is_the_default_and_places_a_cut_three_frames_before_the_word():
    """TR-13 (P52 T11, doc 46 s46.6): on a measured take the default rule lands a CUT at the next word's onset minus
    CUT_LEAD_S (3 frames at 30 fps) and a DIP boundary ON the onset - the engine centres the dip's black on the boundary."""
    assert W.cut_rule(TAKE) == "onset" and W.DEFAULT_CUT_RULE == "onset" and W.CUT_LEAD_S == 0.10
    assert W.cut_before(TAKE, "Your costs") == 1.90                     # "Your" starts at 2.00
    assert W.cut_before(TAKE, "Your costs", exit="dip") == 2.00         # the dip's black midpoint is the onset
    assert W.cut_before(TAKE, "The Fed") == 0.0                         # nothing before the first word


def test_tr13_the_gap_pin_keeps_m13s_placement_and_the_refusal_holds_under_both_rules():
    """The two approved shorts are pinned to rule="gap" (M13's 0.8 of the gap) so they rebuild byte-identical; a gap
    under MIN_GAP is refused under either rule; an unknown rule is refused by name."""
    assert W.cut_before(TAKE, "Your costs", rule="gap") == 1.80
    for rule in (None, "gap", "onset"):
        with pytest.raises(SystemExit) as e:
            W.cut_before(TAKE, "Two numbers", rule=rule)                 # the gap is 0.10 s
        assert "M13" in str(e.value)
    with pytest.raises(ValueError):
        W.cut_before(TAKE, "Your costs", rule="middle")


def test_tr13_an_estimated_take_keeps_the_gap_rule_and_says_so():
    """Three frames mean nothing against a guessed clock: a take with an `estimated` word keeps the gap rule by default,
    and a caller's pin still wins."""
    est = [dict(w, estimated=True) for w in TAKE]
    assert W.is_estimated(est) and not W.is_estimated(TAKE)
    assert W.cut_rule(est) == "gap" and W.cut_before(est, "Your costs") == 1.80
    assert W.cut_before(est, "Your costs", rule="onset") == 1.90


# ---------------------------------------------------------------- P67 T2: the compile door
# The door binds the FIRST compile of a build dir: no passing `## Recall` receipt and no named
# reason, no timeline. A recompile of an existing build (the live editor, `change_report.py`) keeps
# working - it carries the block it compiled under, or is stamped as a pre-P67 build.
import recall_verify as RV  # noqa: E402

FIXTURE_DOC = "docs/FIXTURE.md"
FIXTURE_SPAN = "the world is a plate"
TIMELINE_X = "timeline-x.json"


def _receipt_repo(tmp_path: Path, stages=RV.STAGES, ledger: bool = True) -> tuple[Path, Path]:
    """A synthetic repo: one cited doc, a project whose ledger cites it once per stage, an empty build dir.

    `RV.REPO` is pointed here by the caller, so no citation depends on a real doc's line numbers."""
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / FIXTURE_DOC).write_text(
        "# a fixture doc\n\n" + FIXTURE_SPAN + " and the plate is alive\n", encoding="utf-8")
    ep = tmp_path / "an-episode"
    (ep / "build").mkdir(parents=True, exist_ok=True)
    if ledger:
        lines = ["## Recall", ""]
        lines += [f'- Recall({s}): {FIXTURE_DOC}:3 "{FIXTURE_SPAN}" (the fixture)' for s in stages]
        (ep / "PRODUCTION-LEDGER.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ep, ep / "build"


def _stub_compiler(monkeypatch) -> None:
    """The compiler, stubbed to write its timeline and return green: the DOOR is what is under test."""
    def main() -> int:
        Path(B.BUILD, B.TIMELINE_NAME).write_text("{}", encoding="utf-8")
        return 0
    monkeypatch.setattr(B, "main", main)


def _compile(ep: Path, build: Path, **kw) -> int:
    return T.compile_timeline(ep, build, timeline_name=TIMELINE_X, shot_table_file="SHOT-TABLE-SHORT.py",
                              title="a title", subtitle="a subtitle", episode_id="an-episode",
                              aspect="16:9", caption_style=None, kinetics={}, **kw)


def _manifest(build: Path) -> dict:
    return json.loads((build / T.MANIFEST_NAME).read_text(encoding="utf-8"))


def test_p67_a_verified_receipt_compiles_and_the_manifest_carries_the_block(tmp_path, monkeypatch):
    monkeypatch.setattr(RV, "REPO", tmp_path)
    _stub_compiler(monkeypatch)
    ep, build = _receipt_repo(tmp_path)
    assert _compile(ep, build) == 0
    block = _manifest(build)["compile"][T.RECEIPT_KEY]
    assert block["verdict"] == "pass"
    assert block["stages"] == {s: 1 for s in RV.STAGES} and len(block["stages"]) == 9
    assert block["sha256"] == RV.parse_block((ep / "PRODUCTION-LEDGER.md").read_text(encoding="utf-8")).sha256()
    assert block["ledger"] == "../PRODUCTION-LEDGER.md" and block["checked_at"].startswith("20")
    assert (build / TIMELINE_X).is_file()


def test_p67_a_missing_stage_refuses_by_name_and_no_timeline_is_written(tmp_path, monkeypatch):
    monkeypatch.setattr(RV, "REPO", tmp_path)
    _stub_compiler(monkeypatch)
    ep, build = _receipt_repo(tmp_path, stages=[s for s in RV.STAGES if s != "world"])
    with pytest.raises(SystemExit) as e:
        _compile(ep, build)
    assert 'REFUSED stage "world"' in str(e.value), "the refusal carries the verifier's text verbatim"
    assert not (build / TIMELINE_X).exists() and not (build / T.MANIFEST_NAME).exists()


def test_p67_the_escape_is_a_named_reason_written_into_the_manifest_verbatim(tmp_path, monkeypatch):
    monkeypatch.setattr(RV, "REPO", tmp_path)
    _stub_compiler(monkeypatch)
    ep, build = _receipt_repo(tmp_path, ledger=False)   # the lab authors no episode: there is no ledger at all
    assert _compile(ep, build, no_receipt="recipe lab candidate x") == 0
    assert _manifest(build)["compile"][T.RECEIPT_KEY] == {"skipped_reason": "recipe lab candidate x"}


@pytest.mark.parametrize("reason", ["", "   ", True])
def test_p67_an_empty_string_or_a_bare_flag_is_not_a_reason(tmp_path, monkeypatch, reason):
    monkeypatch.setattr(RV, "REPO", tmp_path)
    _stub_compiler(monkeypatch)
    ep, build = _receipt_repo(tmp_path, ledger=False)
    with pytest.raises(SystemExit) as e:
        _compile(ep, build, no_receipt=reason)
    assert "not a reason" in str(e.value)
    assert not (build / TIMELINE_X).exists()


def test_p67_a_pre_p67_build_recompiles_and_is_stamped_legacy(tmp_path, monkeypatch):
    monkeypatch.setattr(RV, "REPO", tmp_path)
    _stub_compiler(monkeypatch)
    ep, build = _receipt_repo(tmp_path, ledger=False)   # no receipt exists, and the recompile still runs
    (build / T.MANIFEST_NAME).write_text(json.dumps({"compile": {"episode_dir": ".."}}), encoding="utf-8")
    assert _compile(ep, build) == 0
    assert _manifest(build)["compile"][T.RECEIPT_KEY] == {"skipped_reason": T.LEGACY_REASON}
    # a manifest written by the render baseline BEFORE any compile (no `compile` block) is NOT legacy: the first
    # compile is still ahead, so the door runs - and with no receipt and no reason it refuses (parent, P67 T2 review)
    (build / T.MANIFEST_NAME).write_text(json.dumps({"engine_sha": "abc"}), encoding="utf-8")
    with pytest.raises(SystemExit):
        _compile(ep, build)


def test_p67_a_build_that_already_carries_a_receipt_recompiles_under_it_unchanged(tmp_path, monkeypatch):
    monkeypatch.setattr(RV, "REPO", tmp_path)
    _stub_compiler(monkeypatch)
    ep, build = _receipt_repo(tmp_path, stages=["world"])   # a ledger that WOULD be refused on a first compile
    carried = {"ledger": "../PRODUCTION-LEDGER.md", "sha256": "0" * 64, "stages": {s: 1 for s in RV.STAGES},
               "verdict": "pass", "checked_at": "2026-09-16T00:00:00+00:00"}
    (build / T.MANIFEST_NAME).write_text(
        json.dumps({"compile": {"episode_dir": "..", T.RECEIPT_KEY: carried}}), encoding="utf-8")
    assert _compile(ep, build) == 0, "the live editor's recompile is not the door"
    assert _manifest(build)["compile"][T.RECEIPT_KEY] == carried


# ---------------------------------------------------------------- the cue bound to what fires (E99 s72)
#
# *"Sound effects are way off, we're playing spiral and whirls when there's no spiral or whirl
# effect."* Synthetic timelines only: a page that enters by spiral and retracts, a page that enters
# on its axes and leaves on the cut, and one thrown card - the three shapes the base got wrong.

STOP = {"FLIGHT_S": 0.4, "ANTIC_S": 0.12, "DROP_S": 0.18}


def _scene(sid, t0, t1, page=None, docks=(), exit_="cut") -> dict:
    world = {"page": dict(page)} if page else {"asset_id": "plate-x"}
    return {"scene_id": sid, "span": [t0, t1], "world": world, "docks": list(docks), "exit": exit_}


def _timeline(*scenes) -> dict:
    return {"scenes": list(scenes), "evidence": {}}


SPIRAL_RETRACTS = _timeline(
    _scene("s01", 0.0, 10.0, page={"builder": "dense-line", "variant": "line", "enter": "spiral"}),
    _scene("s02", 10.0, 20.0, page={"builder": "dense-line", "variant": "line", "enter": "axes", "exit": "cut"},
           docks=[{"slide": "dock-a", "enter": 12.0, "exit": 16.0, "arrive": "throw", "mass": "paper"}]))


def _cue(slot, at):
    return {"slot": slot, "at": at, "gain": 0.12, "variants": {"A": "x.mp3"}}


def test_the_compiled_timeline_says_what_fires_and_when():
    fires = A.fired(SPIRAL_RETRACTS, STOP)
    got = [(f["kind"], f["what"], f["at"], f["scene"]) for f in fires]
    assert ("page enter", "spiral", 0.0, "s01") in got
    # s01 declares no `exit`, so it RETRACTS over its last LP_RETRACT_S - and it came in by spiral,
    # so the bed's map calls that drain a WHIRL; s02 leaves on the cut and retracts not at all
    assert ("page retract", "whirl", 10.0 - sum(A.gates().LP_RETRACT_S), "s01") in got
    assert not [f for f in fires if f["kind"] == "page retract" and f["scene"] == "s02"]
    assert ("page enter", "axes", 10.0, "s02") in got
    # the landing is the CONTACT frame, not the dock's enter (a throw flies on the stepped clock)
    assert ("landing", "throw", round(A.landing_contact(12.0, "throw", STOP), 2), "s02") in got


def test_a_spiral_cue_is_kept_only_where_a_spiral_fires():
    cues = [_cue("page enter 1 (spiral)", 0.0), _cue("page enter 2 (spiral)", 10.0)]
    kept, dropped = A.bind_cues(cues, SPIRAL_RETRACTS)
    assert [c["slot"] for c in kept] == ["page enter 1 (spiral)"]
    assert len(dropped) == 1 and dropped[0]["slot"] == "page enter 2 (spiral)"
    assert "page enter (axes)" in dropped[0]["why"], dropped[0]["why"]


def test_a_whirl_is_kept_on_the_page_that_retracts_and_dropped_on_the_one_that_cuts():
    keep = _cue("page retract 1 (whirl)", 10.0 - 2.2)
    drop = _cue("page retract 2 (whirl)", 20.0 - 2.2)
    kept, dropped = A.bind_cues([keep, drop], SPIRAL_RETRACTS)
    assert [c["slot"] for c in kept] == ["page retract 1 (whirl)"]
    assert "no `page retract (whirl)` fires" in dropped[0]["why"]


def test_a_roll_out_enter_is_dropped_on_a_page_that_does_not_roll():
    """The map plays its page-ROLL at any entry that is not a mount or a spiral; `axes`, `snap` and
    `camera` have no cream roll-out at all, and three of the base's four pages entered that way."""
    kept, dropped = A.bind_cues([_cue("page enter 2", 10.0)], SPIRAL_RETRACTS)
    assert not kept and len(dropped) == 1
    assert "page enter (roll-out)" in dropped[0]["why"]
    # ... and a page that declares NO entry is exactly the one the roll belongs to
    rolls = _timeline(_scene("s01", 0.0, 8.0, page={"builder": "dense-line", "variant": "line", "exit": "cut"}))
    kept, dropped = A.bind_cues([_cue("page enter 1", 0.0)], rolls)
    assert len(kept) == 1 and not dropped


def test_a_landing_cue_is_kept_one_frame_early_and_dropped_where_nothing_lands():
    contact = A.landing_contact(12.0, "throw", STOP)
    kept, dropped = A.bind_cues([_cue("landing 2 (throw, paper)", round(contact - 1 / 24, 2)),
                                 _cue("landing 1 (land, metal)", 5.0)], SPIRAL_RETRACTS)
    assert [c["slot"] for c in kept] == ["landing 2 (throw, paper)"]
    assert dropped[0]["slot"] == "landing 1 (land, metal)"


def test_a_bed_and_a_slot_the_binder_cannot_judge_are_never_dropped():
    beds = [{"slot": "hook bed", "at": 0.0, "gain": 0.1}, _cue("press 3", 4.0)]
    kept, dropped = A.bind_cues(beds, SPIRAL_RETRACTS)
    assert kept == beds and not dropped
    assert A.cue_key({"slot": "hook bed"}) is None and A.cue_key({"slot": "press 3"}) is None


def test_the_binder_names_every_firing_effect_the_map_leaves_silent():
    notes = A.unsounded([_cue("page enter 1 (spiral)", 0.0)], SPIRAL_RETRACTS)
    assert any("page retract (whirl)" in n for n in notes)
    assert any("landing (throw)" in n for n in notes)
    assert all(n.startswith("no cue mapped for ") for n in notes), notes


def test_the_binder_adds_nothing_and_never_reorders_what_it_keeps():
    cues = [_cue("page enter 1 (spiral)", 0.0), {"slot": "hook bed", "at": 0.0},
            _cue("landing 2 (throw, paper)", round(A.landing_contact(12.0, "throw", STOP) - 1 / 24, 2))]
    kept, _dropped = A.bind_cues(cues, SPIRAL_RETRACTS)
    assert kept == [c for c in cues], "the cues keep their order, their files and their gains"


def test_an_absent_page_entry_reads_as_the_roll_out_not_as_the_walks_mount_default():
    """`recipe_walk` writes `page_enter:mount` for an absent entry (its own default) and a mount has
    no page turn at all - so the page block is read, not the walk's card."""
    assert A.page_entry({}) == A.ROLL_OUT
    assert A.page_entry({"enter": "camera=dock-h"}) == "camera", "the entry's head, not its argument"


# --- NEAREST-FIRST AND CONSUMED (the sixth pass' review, findings 2 / 3 / 5) ---------------------
# The binder's first cut silenced a fire with ANY cue of the same kind inside the tolerance, compared
# no mass and read no scene: two paper landings 1.0 s apart - ordinary in a dense beat - left the
# first one silent AND unnamed, a `metal` cue was kept over a `paper` landing, and a cue authored for
# row 5 could bind to row 2's landing. A fire sounds ONCE and a cue binds ONCE.

TWO_LANDINGS = _timeline(
    _scene("s01", 0.0, 10.0, page={"builder": "dense-line", "variant": "line", "enter": "axes", "exit": "cut"},
           docks=[{"slide": "dock-a", "enter": 2.0, "exit": 6.0, "arrive": "throw", "mass": "paper"},
                  {"slide": "dock-b", "enter": 3.0, "exit": 7.0, "arrive": "throw", "mass": "paper"}]))


def _contacts(timeline) -> list[float]:
    return [f["at"] for f in A.fired(timeline) if f["kind"] == "landing"]


def test_one_cue_binds_to_one_fire_and_the_landing_it_leaves_silent_is_NAMED():
    """The reviewer's own fixture: two paper landings 1.0 s apart, ONE cue on the second."""
    first, second = _contacts(TWO_LANDINGS)
    assert round(second - first, 2) == 1.0 < A.gates().CUE_TOL_S, "both landings sit inside one tolerance"
    cues = [_cue("landing 1 (throw, paper)", second)]
    kept, dropped = A.bind_cues(cues, TWO_LANDINGS)
    assert [c["slot"] for c in kept] == ["landing 1 (throw, paper)"] and not dropped
    notes = A.unsounded(kept, TWO_LANDINGS)
    assert any(f"landing (throw) at {first:.2f}s" in n for n in notes), notes
    assert not any(f"landing (throw) at {second:.2f}s" in n for n in notes), notes


def test_the_nearer_cue_takes_the_fire_and_the_second_cue_takes_the_other_one():
    first, second = _contacts(TWO_LANDINGS)
    kept, dropped = A.bind_cues([_cue("landing 1 (throw, paper)", second),
                                 _cue("landing 1 (throw, paper)", first)], TWO_LANDINGS)
    assert len(kept) == 2 and not dropped, "two fires, two cues - each bound to its own"
    notes = A.unsounded(kept, TWO_LANDINGS)
    assert not [n for n in notes if "landing" in n], notes   # both landings are sounded; the page enter is not


def test_a_third_cue_on_two_fires_is_DROPPED_because_a_fire_sounds_once():
    first, second = _contacts(TWO_LANDINGS)
    cues = [_cue("landing 1 (throw, paper)", first), _cue("landing 1 (throw, paper)", second),
            _cue("landing 1 (throw, paper)", round((first + second) / 2, 2))]
    kept, dropped = A.bind_cues(cues, TWO_LANDINGS)
    assert len(kept) == 2 and len(dropped) == 1
    assert dropped[0]["at"] == round((first + second) / 2, 2), "the FARTHEST cue is the one left over"
    assert "already bound" in dropped[0]["why"], dropped[0]["why"]


def test_a_metal_cue_does_not_bind_to_a_paper_landing_and_the_drop_names_the_weight():
    first, _second = _contacts(TWO_LANDINGS)
    kept, dropped = A.bind_cues([_cue("landing 1 (throw, metal)", first)], TWO_LANDINGS)
    assert not kept and len(dropped) == 1
    assert "paper" in dropped[0]["why"] and "metal" in dropped[0]["why"], dropped[0]["why"]
    # ... and the same cue over a metal landing IS kept: the mass is compared, never invented
    metal = _timeline(_scene("s01", 0.0, 10.0, page={"builder": "dense-line", "variant": "line", "exit": "cut"},
                             docks=[{"slide": "dock-a", "enter": 2.0, "exit": 6.0, "arrive": "throw",
                                     "mass": "metal"}]))
    kept, dropped = A.bind_cues([_cue("landing 1 (throw, metal)", _contacts(metal)[0])], metal)
    assert len(kept) == 1 and not dropped


def test_a_cue_whose_slot_names_no_mass_binds_to_a_landing_of_any_weight():
    """`cue_key` compares a mass only when BOTH sides carry one - a slot that names none is not judged on it."""
    first, _second = _contacts(TWO_LANDINGS)
    kept, dropped = A.bind_cues([_cue("landing 1 (throw)", first)], TWO_LANDINGS)
    assert len(kept) == 1 and not dropped


TWO_SCENES = _timeline(
    _scene("s01", 0.0, 10.0, page={"builder": "dense-line", "variant": "line", "enter": "axes", "exit": "cut"},
           docks=[{"slide": "dock-a", "enter": 2.0, "exit": 6.0, "arrive": "throw", "mass": "paper"}]),
    _scene("s02", 10.0, 20.0, page={"builder": "dense-line", "variant": "line", "enter": "axes", "exit": "cut"},
           docks=[{"slide": "dock-b", "enter": 12.0, "exit": 16.0, "arrive": "throw", "mass": "paper"}]))


def test_a_cue_binds_only_on_the_ROW_its_slot_numbers():
    """The slot's own index is the ROW (`build_short.sound_cues`: `landing {i + 1}`), and the compiler
    names the nth row's scene `s{n:02d}` (`build_scene_timeline_f.scene_row_id`)."""
    on_s01 = _contacts(TWO_SCENES)[0]
    kept, dropped = A.bind_cues([_cue("landing 2 (throw, paper)", on_s01)], TWO_SCENES)
    assert not kept and len(dropped) == 1, "row 2's cue never binds to row 1's landing"
    assert "s01" in dropped[0]["why"] and "s02" in dropped[0]["why"], dropped[0]["why"]
    kept, dropped = A.bind_cues([_cue("landing 1 (throw, paper)", on_s01)], TWO_SCENES)
    assert len(kept) == 1 and not dropped


def test_a_row_the_timeline_does_not_carry_binds_by_time_alone():
    """A slot numbering a row this timeline has no scene for narrows nothing - a row that cannot be
    resolved must never DROP a cue."""
    on_s01 = _contacts(TWO_SCENES)[0]
    assert A.cue_scene({"n": 9}, TWO_SCENES) is None and A.cue_scene({"n": 2}, TWO_SCENES) == "s02"
    kept, dropped = A.bind_cues([_cue("landing 9 (throw, paper)", on_s01)], TWO_SCENES)
    assert len(kept) == 1 and not dropped


def test_the_unsounded_notes_are_the_fires_no_KEPT_cue_took():
    """`unsounded` reads the same pairing the binder does, so the two can never disagree."""
    rep = A.bind_report([_cue("landing 1 (throw, paper)", _contacts(TWO_LANDINGS)[1])], TWO_LANDINGS)
    assert [f["at"] for f in rep["silent"] if f["kind"] == "landing"] == [_contacts(TWO_LANDINGS)[0]]
    assert sum(1 for r in rep["cues"] if r["fire"] is not None) == 1
