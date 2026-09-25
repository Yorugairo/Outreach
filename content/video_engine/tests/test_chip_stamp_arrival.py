"""P70 T1 (was P69 T12): THE CHIP LANDS AS A STAMP - `arrive: "stamp"` on the chip's stamp form, rendered both ways.

The stamp form (`form: "stamp"`, P62) keeps the chip's spring landing. With `arrive: "stamp"` its art lands by the stamp
arrival (E99 s87, kinetics/stopaction.mjs `stampXf`; the painter's half is pinned by tests/kinetics/chip.test.mjs), and
the compiler, the motion gate, the card walk and the cue binder all read that landing at its CONTACT, 0.1542 s after its
`at` - the instant every stamp lands at (P69 T2-T4, s116). What this file pins:

  (1) the grammar: the arrival is the stamp FORM's, refused by name anywhere else (`CHIP_ARRIVALS`);
  (2) the label (E99 s90): drawn at the phone floor under the arrival; a stamp-form chip without it is WARNed (s106);
  (3) the arrival FITTED to the room at compile time by the dock stamp's own law - the ring's peak AND the approach
      (`ring_to`, `from_to`; stamp_fit + _stamp_floors), round the mark AND its label (the ring never crosses the
      name) - written on the species; a WARN with numbers when it cannot clear, never a refusal (s106);
  (4) the gate counts the landing at at + STAMP_CONTACT_S, recipe_walk emits `arrival:stamp`, `fired` pairs a landing
      cue to that contact; a glyph chip's events are unchanged;
  (5) s112: the stamp-timing advice reads a stamped chip as it reads a stamped dock;
  (6) the two goldens come from one source that differs only in `arrive`.
"""
from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as MG  # noqa: E402
import ledger_page as LPG  # noqa: E402
import recipe_walk as RW  # noqa: E402
from authoring import audio as AU, docks as D, words as W  # noqa: E402

CHIP_MJS = ROOT / "content/video_engine/scripts/species/chip.mjs"
COMPILER = ROOT / "content/video_engine/scripts/build_scene_timeline_f.py"
PLATE, STILL = "world-spike-desk-v1", (0, 0, 0)
GPU = "prop-icon-gpu-ai-accelerator-v1"   # the icons catalogue's GPU cutout (E94, approved) - the golden's NVIDIA
CONTACT = MG.STAMP_CONTACT_S
# H row 7's take: "... and it isn't Nvidia." (`isn't Nvidia` 58.35-59.60, the door's NVIDIA_CHIP lands at 58.60)
WS = [{"w": w, "start_s": s, "end_s": e} for w, s, e in (
    ("and", 57.90, 58.05), ("it", 58.05, 58.18), ("isn't", 58.18, 58.60), ("Nvidia.", 58.60, 59.60),
    ("But", 60.10, 60.30))]
TL_WORDS = [{"w": w["w"], "start": w["start_s"], "end": w["end_s"]} for w in WS]


def _stamp(**extra) -> dict:
    return {"kind": "chip", "form": "stamp", "at": 10.0, "dur": 6.0, "icon": GPU, "label": "NVIDIA",
            "target": {"kind": "point", "x": 0.5, "y": 0.42}, **extra}


def _glyph(**extra) -> dict:
    return {"kind": "chip", "at": 10.0, "dur": 6.0, "icon": "cpu", "label": "NVIDIA",
            "target": {"kind": "point", "x": 0.5, "y": 0.42}, **extra}


def _scene(species=(), docks=(), span=(0.0, 30.0), world=None) -> dict:
    return {"scene_id": "s01", "span": list(span), "world": world or {"asset_id": "plate-plain"},
            "species": list(species), "docks": list(docks), "exit": "cut"}


def _gpu_paint() -> dict:
    return B.painted_box(B.catalogue_stamp_asset(GPU)["file"])


# ---- (1) the grammar ----------------------------------------------------------------------------------------------


def test_the_arrival_is_the_stamp_forms_and_CHIP_ARRIVALS_names_it():
    assert B.CHIP_ARRIVALS == ("stamp",)
    assert B.validate_species([_stamp(arrive="stamp")], STILL, PLATE) == []
    assert B.validate_species([_stamp()], STILL, PLATE) == [], "absent: the spring landing, as always"


def test_a_glyph_chip_carrying_arrive_is_REFUSED_by_name():
    errs = B.validate_species([_glyph(arrive="stamp")], STILL, PLATE)
    assert any("the stamp arrival is the stamp form's" in e for e in errs), errs


@pytest.mark.parametrize("value", ["throw", "land", "spring", "", None, 1])
def test_any_other_arrival_on_the_stamp_form_is_REFUSED_naming_CHIP_ARRIVALS(value):
    errs = B.validate_species([_stamp(arrive=value)], STILL, PLATE)
    assert any("CHIP_ARRIVALS" in e and "stamp" in e for e in errs), errs


def test_the_stamp_form_still_refuses_readability_so_longform_is_not_a_chip_option():
    errs = B.validate_species([_stamp(arrive="stamp", readability="landscape-phone")], STILL, PLATE)
    assert any("'readability' is not supported" in e for e in errs), errs


# ---- (2) the label: the s90 floor ---------------------------------------------------------------------------------


def test_the_label_floor_is_the_card_type_floor_and_chip_mjs_carries_the_same_number():
    assert B.CHIP_STAMP_LABEL_FLOOR == 59.08 == round(LPG.CARD_TYPE_PX, 2)
    src = CHIP_MJS.read_text(encoding="utf-8")
    assert re.search(r"LABEL_FLOOR:\s*59\.08,", src), "chip.mjs CHIP_STAMP.LABEL_FLOOR is the compiler's floor"
    assert re.search(rf"LABEL_SIZE:\s*{B.CHIP_STAMP_LABEL_SIZE},", src), "the compiler's mirror of the unstamped size"
    assert re.search(rf'MASS:\s*"{B.CHIP_STAMP_MASS}"', src)


def test_a_stamp_form_chip_WITHOUT_the_arrival_is_WARNED_that_its_label_is_under_the_floor():
    msg = B.chip_stamp_label_advice(_stamp())
    for part in ("'NVIDIA'", GPU, "48 stage px", "59.08", "E99 s90", 'add `arrive: "stamp"`'):
        assert part in msg, (part, msg)
    assert "size" not in msg.split(" - ", 1)[1] and "read the frame" not in msg, 'it names only what exists'
    assert B.chip_stamp_label_advice(_stamp(arrive="stamp")) is None, "the arrival draws it at the floor"
    assert B.chip_stamp_label_advice(_glyph()) is None
    assert B.chip_stamp_label_advice({"kind": "callout"}) is None


def test_the_label_advice_is_a_WARN_the_row_loop_PRINTS_never_a_refusal():
    body = COMPILER.read_text(encoding="utf-8").split("def main() -> int:", 1)[1]
    assert "_label_warn = chip_stamp_label_advice(e)" in body
    assert 'print(f"  [WARN] P70 T1: shot row {i + 1}: {_label_warn}")' in body
    assert "raise" not in inspect.getsource(B.chip_stamp_label_advice)


# ---- (3) the ring's peak, fitted to the room ----------------------------------------------------------------------


def test_the_art_box_is_the_painters_the_target_centre_the_side_and_the_painted_box_in_the_square():
    paint = {"aspect": 0.5, "x0": 0.1, "y0": 0.2, "x1": 0.9, "y1": 0.8}   # a 2:1 canvas drawn `meet` in the square
    art = B.chip_stamp_art(_stamp(size=300, label=None, target={"kind": "point", "x": 0.5, "y": 0.5}), "16:9", paint)
    assert art["side"] == 300
    # the canvas is 300 x 150, centred: y from 75 to 225 in the square; painted 0.2-0.8 of it -> 105..195
    assert art["paint"] == [0.1, 0.35, 0.9, 0.65]
    assert art["centre"] == pytest.approx((960.0, 540.0))
    assert art["painted"] == pytest.approx((240.0, 90.0))
    region = B.chip_stamp_art(_stamp(label=None, target={"kind": "region", "x0": 0.4, "y0": 0.4, "x1": 0.5, "y1": 0.5}), "16:9",
                              {"aspect": 1.0, "x0": 0, "y0": 0, "x1": 1, "y1": 1})
    assert region["side"] == pytest.approx(108.0), "a region caps the side, as the painter's min(size, w, h)"


# the label as DRAWN (Kalam 700 at 59.08, getBBox on the rendered face; scratchpad/p70-t1/logs/advance-probe.json)
DRAWN_LABELS = {"NVIDIA": (181.77, 94.0), "BEAR MARKET": (388.28, 94.5), "SK hynix": (233.90, 94.4), "WAVE": (150.75, 94.3)}


@pytest.mark.parametrize("label", sorted(DRAWN_LABELS))
def test_the_labels_box_holds_the_label_AS_DRAWN_with_its_keyline(label):
    w, h = DRAWN_LABELS[label]
    box = B.chip_stamp_label_box(label, 260)
    assert box["x1"] - box["x0"] >= w + 2 * B.CHIP_STAMP_LABEL_KEYLINE_PX
    assert box["y1"] - box["y0"] >= h + 2 * B.CHIP_STAMP_LABEL_KEYLINE_PX
    assert box["x0"] == -box["x1"], "text-anchor: middle"
    two = B.chip_stamp_label_box(label + "\n" + label, 260)
    assert two["y1"] - box["y1"] == pytest.approx(round(52 * 59.08 / 48, 2)), "one scaled line step per line"
    assert B.chip_stamp_label_box("", 260) is None and B.chip_stamp_label_box(None, 260) is None


def test_the_chips_painted_extent_is_the_UNION_of_its_mark_and_its_label_and_the_ring_circles_both():
    paint = _gpu_paint()
    e = _stamp(arrive="stamp", target={"kind": "point", "x": 0.5, "y": 0.5})
    art, bare = B.chip_stamp_art(e, "16:9", paint), B.chip_stamp_art(dict(e, label=None), "16:9", paint)
    lab = art["label"]
    assert art["paint"][3] > 1 and art["painted"][1] > bare["painted"][1], "the name hangs below the art, inside the box"
    (cx, cy), (w, h), side = art["centre"], art["painted"], art["side"]
    r0 = 0.5 * (w ** 2 + h ** 2) ** 0.5   # the ring's base radius: the engine's chipStampPaint(...).r
    sq_cx, sq_cy = 960.0, 540.0           # the art square's centre on the stage
    for x, y in ((lab["x0"], lab["y0"]), (lab["x1"], lab["y0"]), (lab["x0"], lab["y1"]), (lab["x1"], lab["y1"])):
        assert ((sq_cx + x - cx) ** 2 + (sq_cy + y - cy) ** 2) ** 0.5 <= r0 + 1e-6, "every label corner inside the ring"


def test_on_a_clear_plate_the_ring_takes_the_sources_full_2x_and_is_written_on_a_COPY():
    e = _stamp(arrive="stamp", size=180)
    out, notes = B.chip_stamp_ring_fit(e, {"asset_id": "plate-plain"}, "16:9", _gpu_paint())
    assert notes == []
    assert out is not e and "ring_to" not in e, "the authored entry is never mutated"
    assert out["ring_to"] == B.STAMP_RING_TO and out["from_to"] == B.STAMP_FROM, "the room holds the source's whole law"
    assert len(out["paint"]) == 4 and out["paint"][3] > 1, "the union, the label below the art"


def test_a_ring_near_the_caption_band_is_CAPPED_by_stamp_fit_rounded_down():
    e = _stamp(arrive="stamp", size=180, target={"kind": "point", "x": 0.5, "y": 0.5})
    out, notes = B.chip_stamp_ring_fit(e, {"asset_id": "plate-plain"}, "16:9", _gpu_paint())
    art = B.chip_stamp_art(e, "16:9", _gpu_paint())
    (cx, cy), (pw, ph) = art["centre"], art["painted"]
    band = B.FRAME_BANDS["16:9"]["caption"]
    clear = min(band["y"] - cy, B.disc_clearance(cx, cy, [band], B.FRAME_BANDS["16:9"]["safe"]))
    rp = 0.5 * (pw ** 2 + ph ** 2) ** 0.5
    assert out["ring_to"] < B.STAMP_RING_TO
    assert out["ring_to"] == pytest.approx((clear - B.STAMP_RING_W_PX) / rp, abs=1e-2)   # stamp_fit reads its own ROUNDED box
    assert notes == [], "a capped ring is the fit doing its job, not a finding"


def test_the_APPROACH_is_fitted_by_the_docks_law_capped_never_clipped():
    """The send-back's fix 1: the 2.1x fall carries the mark and its name over the page, so it is fitted as the dock's
    is - stamp_fit's `from_to` (the turned hull clear at that scale), rounded down."""
    e = _stamp(arrive="stamp", target={"kind": "point", "x": 0.5, "y": 0.34})   # the default 260: the safe box's top is near
    out, notes = B.chip_stamp_ring_fit(e, {"asset_id": "plate-plain"}, "16:9", _gpu_paint())
    art = B.chip_stamp_art(e, "16:9", _gpu_paint())
    (cx, cy), (w, h) = art["centre"], art["painted"]
    hx, hy = B.turned_half_extents(w, h)
    safe = B.FRAME_BANDS["16:9"]["safe"]
    assert B.STAMP_APPROACH_MIN <= out["from_to"] < B.STAMP_FROM and notes == []
    assert out["from_to"] == pytest.approx((cy - safe["y"]) / hy, abs=5e-3), "held by the safe box's top"
    assert B._floor4(out["from_to"]) == out["from_to"]


def test_where_NOTHING_fits_it_is_a_WARN_with_numbers_and_the_ring_is_drawn_at_its_floor_never_a_refusal():
    e = _stamp(arrive="stamp", target={"kind": "point", "x": 0.5, "y": 0.86})   # the mark sits on the caption band
    out, notes = B.chip_stamp_ring_fit(e, {"asset_id": "plate-plain"}, "16:9", _gpu_paint(), where="row 7 chip")
    assert len(notes) == 2 and all(n.startswith("row 7 chip (mark and label ") for n in notes), notes
    assert "the ring is drawn at its floor" in notes[0] and "though the room holds" in notes[0]
    assert "the approach comes down from 1.20x though the room holds" in notes[1], "the dock's _stamp_floors, word for word"
    art = B.chip_stamp_art(e, "16:9", _gpu_paint())
    rp = 0.5 * (art["painted"][0] ** 2 + art["painted"][1] ** 2) ** 0.5
    assert out["ring_to"] == pytest.approx((rp + B.STAMP_RING_GAP_PX) / rp, abs=1e-3), "stamp_fit's floor, on its rounded box"
    assert out["from_to"] == B.STAMP_APPROACH_MIN
    assert "raise" not in inspect.getsource(B.chip_stamp_ring_fit)


def test_on_a_ledger_page_the_ring_is_fitted_against_the_pages_own_obstacles():
    import build_golden_sources as BGS
    series = LPG.load_series(BGS.SERIES)   # H's committed divergence object, the golden's own page
    saved, B.ASPECT = B.ASPECT, "16:9"
    try:
        page = B.stamp_full_stage(LPG.build_spec(series, "line", 0, "right"))
    finally:
        B.ASPECT = saved
    world = {"kind": "ledger", "page": page}
    e = _stamp(arrive="stamp", size=180, target={"kind": "point", "x": 0.86, "y": 0.19})   # the golden's first corner
    out, notes = B.chip_stamp_ring_fit(e, world, "16:9", _gpu_paint())
    assert any("the ring is drawn at its floor" in n for n in notes), notes
    assert any("the approach comes down from 1.20x" in n for n in notes), "the end tags hold the fall under its floor"


def test_a_non_stamped_entry_is_returned_AS_IT_WAS():
    for e in (_stamp(), _glyph(), {"kind": "callout", "at": 1.0}):
        out, notes = B.chip_stamp_ring_fit(e, None, "16:9", _gpu_paint())
        assert out is e and notes == []


def test_the_row_loop_fits_a_stamped_chip_after_the_stamps_and_before_the_cards_are_placed():
    body = COMPILER.read_text(encoding="utf-8").split("def main() -> int:", 1)[1]
    i_fit = body.index("stamp_fits, stamp_boxes = row_stamp_fits(")
    i_chip = body.index("e, _chip_notes = chip_stamp_ring_fit(")
    i_place = body.index("place = dock_place(world, ASPECT, newsreel_boxes(row_species, ASPECT), clear_of=stamp_boxes)")
    assert 0 < i_fit < i_chip < i_place
    assert 'print(f"  [WARN] P70 T1: {_n}")' in body


# ---- (4) the gate, the walk and the cue read the contact ----------------------------------------------------------


def test_the_gate_counts_a_stamped_chips_landing_at_its_CONTACT():
    sc = _scene([_stamp(arrive="stamp")])
    assert (10.0 + CONTACT, f"chip {GPU} stamp") in MG._landings(sc)
    assert MG._arrivals([sc]) == [(10.0, f"chip {GPU}", "stamp", 10.0 + CONTACT)]
    assert MG._arrival_events([sc]) == [round(10.0 + CONTACT, 2)]


def test_a_glyph_chip_and_the_stamp_form_on_its_spring_keep_their_events():
    for e in (_glyph(), _glyph(cross_at=12.0), _stamp()):
        sc = _scene([e])
        assert MG._arrivals([sc]) == [] and MG._arrival_events([sc]) == []
        assert not any(lab.startswith("chip ") for _t, lab in MG._landings(sc))
    assert MG._species_events([_scene([_glyph(cross_at=12.0)])]) == [10.0, 12.0]
    assert MG._species_events([_scene([_stamp(arrive="stamp")])]) == [10.0], "the at is the species event it was"


def test_the_cadence_row_names_the_stamped_chip():
    g = MG._cadence_gate([_scene([_stamp(arrive="stamp")])])
    assert g is not None and "1 arrival(s)" in g.message and f"chip {GPU} stamp (ink)" in g.message


def test_recipe_walk_emits_arrival_stamp_for_a_stamped_chip_and_nothing_for_a_glyph_chip():
    tl = {"scenes": [_scene([_stamp(arrive="stamp")])]}
    arr = [e for e in RW.events(tl) if e.cls == "arrival"]
    assert [(e.t, e.card, e.ref) for e in arr] == [(10.0, "arrival:stamp", GPU)]
    for e in (_glyph(), _stamp()):
        assert [x for x in RW.events({"scenes": [_scene([e])]}) if x.cls == "arrival"] == []


def test_fired_pairs_a_landing_cue_to_the_stamped_chips_contact_at_the_stamp_mass():
    lands = [r for r in AU.fired({"scenes": [_scene([_stamp(arrive="stamp")])]}) if r["kind"] == "landing"]
    assert lands == [{"kind": "landing", "what": "stamp", "at": round(10.0 + CONTACT, 2), "until": round(10.0 + CONTACT, 2),
                      "scene": "s01", "ref": GPU, "mass": "ink"}]
    assert [r for r in AU.fired({"scenes": [_scene([_glyph()])]}) if r["kind"] == "landing"] == []


# ---- (5) s112: the stamp-timing advice ----------------------------------------------------------------------------


def test_a_stamped_chip_put_ON_its_word_is_ADVISED_and_one_anchored_after_it_is_SILENT():
    on = B.stamp_timing_advice([_scene([_stamp(arrive="stamp", at=58.60)], span=(50.0, 70.0))], TL_WORDS)
    assert [(a["kind"], a["word"], a["chip"]) for a in on] == [("inside", "Nvidia.", GPU)]
    assert "chip 'NVIDIA'" in on[0]["message"] and "after('Nvidia')" in on[0]["message"]
    after = D.stamp_enter(W.after(WS, "Nvidia"))
    assert B.stamp_timing_advice([_scene([_stamp(arrive="stamp", at=after)], span=(50.0, 70.0))], TL_WORDS) == []
    assert B.stamp_timing_advice([_scene([_stamp(at=58.60)], span=(50.0, 70.0))], TL_WORDS) == [], "stamped chips only"


def test_a_stamped_chip_within_STAMP_DATA_CLEAR_S_of_a_data_mark_is_ADVISED():
    fig = {"kind": "figure", "at": 9.9, "dur": 0.3}   # lands at 10.2, 0.05 s after the chip's contact
    adv = B.stamp_timing_advice([_scene([_stamp(arrive="stamp"), fig])], TL_WORDS)
    assert [a["kind"] for a in adv] == ["data"] and adv[0]["mark"] == "figure landing"


def test_a_stamped_chip_is_never_a_data_mark_for_a_stamped_dock():
    dock = {"slide": "prop-rack", "slot": 0, "enter": 10.0, "exit": 20.0, "arrive": "stamp", "kind": "prop"}
    chip = _stamp(arrive="stamp", at=9.99, target={"kind": "point", "x": 0.2, "y": 0.3})
    adv = B.stamp_timing_advice([_scene([chip], [dock])], None)
    assert [a for a in adv if a["kind"] == "data"] == []


# ---- (6) one source, two goldens ----------------------------------------------------------------------------------


def test_the_two_goldens_come_from_one_source_that_differs_only_in_arrive():
    import build_golden_sources as BGS
    pop, pop_uris = BGS.SURFACES["chip-stamp-pop"]()
    arr, arr_uris = BGS.SURFACES["chip-stamp-arrival"]()
    assert pop_uris == arr_uris
    (p,), (a,) = pop["scenes"][0]["species"], arr["scenes"][0]["species"]
    fitted = {"arrive", "ring_to", "from_to", "paint"}   # the arrival, and what the compiler's fit writes because of it
    assert {k: v for k, v in a.items() if k not in fitted} == p
    assert a["arrive"] == "stamp" and "arrive" not in p and "ring_to" not in p and "from_to" not in p
    assert a["ring_to"] < B.STAMP_RING_TO and a["from_to"] < B.STAMP_FROM, "both fits at work, and no finding"
    assert (p["icon"], p["label"], p["form"]) == (GPU, "NVIDIA", "stamp")
    strip = {k: v for k, v in pop.items() if k != "scenes"} == {k: v for k, v in arr.items() if k != "scenes"}
    assert strip, "the timelines differ only in the chip's entry"
    assert BGS.FRAME_T["chip-stamp-arrival"] == pytest.approx(a["at"] + CONTACT + 0.10, abs=0.005)
    assert BGS.FRAME_T["chip-stamp-pop"] == BGS.FRAME_T["chip-stamp-arrival"]


# ---- (7) the review's fixes: the row path, the owed exit, the mirrors, one predicate, the live face -----------------


STOPACTION = ROOT / "content/video_engine/scripts/kinetics/stopaction.mjs"


def test_the_compilers_label_step_mirrors_equal_chip_mjs_and_the_exit_mirror_equals_stopaction():
    src = CHIP_MJS.read_text(encoding="utf-8")
    assert re.search(rf"LABEL_GAP:\s*{B.CHIP_STAMP_LABEL_GAP},", src), "CHIP_STAMP.LABEL_GAP"
    assert re.search(rf"LABEL_LINE_H:\s*{B.CHIP_STAMP_LABEL_LINE_H},", src), "CHIP_STAMP.LABEL_LINE_H"
    m = re.search(r"EXIT_S:\s*(\d+)\s*/\s*(\d+),", STOPACTION.read_text(encoding="utf-8"))
    assert m and B.STAMP_EXIT_S == int(m.group(1)) / int(m.group(2)), "STAMP_ARRIVAL.EXIT_S, one dial written twice"
    assert B.CHIP_STAMP_MIN_DUR_S == pytest.approx(CONTACT + B.STAMP_EXIT_S)


def test_one_predicate_says_which_chip_lands_as_a_stamp_for_the_compiler_the_gate_and_the_walk():
    cases = [_stamp(arrive="stamp"), _stamp(), _stamp(arrive="throw"), _stamp(arrive=True), _glyph(arrive="stamp"), _glyph(),
             {"kind": "callout", "form": "stamp", "arrive": "stamp"}, None, "chip"]
    for e in cases:
        want = isinstance(e, dict) and e.get("kind") == "chip" and e.get("form") == "stamp" and e.get("arrive") == "stamp"
        assert RW.is_stamped_chip(e) is want and B.chip_is_stamped(e) is want, e
        if isinstance(e, dict):
            assert (MG._stamped_chips({"species": [e]}) == [e]) is want, e
            walk = [x for x in RW.events({"scenes": [_scene([e])]}) if x.cls == "arrival"]
            assert bool(walk) is want, ("the walk fires only where the gate counts a landing", e)
    assert MG.is_stamped_chip is RW.is_stamped_chip, "the gate reads the walk's own predicate"


def test_a_stamped_chip_shorter_than_its_landing_and_its_exit_is_WARNED_with_its_numbers():
    need = B.CHIP_STAMP_MIN_DUR_S
    msg = B.chip_stamp_dur_advice(_stamp(arrive="stamp", dur=0.5))
    for part in ("'NVIDIA'", GPU, "dur 0.5s", f"{CONTACT:g}s", f"{B.STAMP_EXIT_S:.4f}s", f"{need:.4f}s", f"{need:.2f}s"):
        assert part in msg, (part, msg)
    assert B.chip_stamp_dur_advice(_stamp(arrive="stamp", dur=round(need + 0.01, 2))) is None
    assert B.chip_stamp_dur_advice(_stamp(dur=0.5)) is None, "the spring landing owes no stamp exit"
    assert B.chip_stamp_dur_advice(_glyph(dur=0.5)) is None
    assert "raise" not in inspect.getsource(B.chip_stamp_dur_advice)


class _PastTheChips(Exception):
    """Raised once the row path has fitted the row's stamped chips - the test needs nothing after."""


def test_a_row_COMPILES_its_stamped_chip_with_the_fit_written_on_it(tmp_path, monkeypatch, capsys):
    """The review's fix 1: `main()` on a one-row bed (the `test_ledger_panels._row_path` door), stopped once the scene's
    species are final. The stamped chip carries the fit the door computes - `ring_to`, `from_to`, `paint` - and the row
    prints its WARNs: the floors on this page, the label under the floor, the owed exit."""
    import json
    import shutil
    import build_golden_sources as BGS
    ep, build = tmp_path / "ep", tmp_path / "ep" / "build"
    (ep / "evidence/objects").mkdir(parents=True)
    (build / "audio").mkdir(parents=True)
    shutil.copy2(BGS.SERIES, ep / "evidence/objects" / "ev-row-path.series.json")
    (build / "audio/episode.mp3").write_bytes(b"")
    (build / "timeline.json").write_text(json.dumps({"runtime_s": 30.0, "words": []}), encoding="utf-8")
    (build / "caption-pages.json").write_text("[]", encoding="utf-8")
    stamped = _stamp(arrive="stamp", size=180, target={"kind": "point", "x": 0.86, "y": 0.19})
    plain = _stamp(label="PLAIN", at=4.0, dur=3.0, target={"kind": "point", "x": 0.3, "y": 0.3})
    short = _stamp(arrive="stamp", label="SHORT", at=20.0, dur=0.5, target={"kind": "point", "x": 0.3, "y": 0.3})
    row = (0.0, 30.0, "ledger:ev-row-path:line", (0, 0, 0), [], None, [stamped, plain, short])
    (ep / "SHOT-ROW-PATH.py").write_text("W = " + repr([row]) + "\n", encoding="utf-8")
    seen: dict = {}

    def stop(world, row_species, a):
        seen["species"], seen["world"] = row_species, world
        raise _PastTheChips

    for name, value in (("BUILD", build), ("EP", ep), ("SHOT_TABLE_FILE", "SHOT-ROW-PATH.py"), ("ASPECT", "16:9"),
                        ("page_build_windows", stop)):
        monkeypatch.setattr(B, name, value)
    with pytest.raises(_PastTheChips):
        B.main()
    out = capsys.readouterr().out
    got = {e["label"]: e for e in seen["species"] if e.get("kind") == "chip"}
    for lab in ("NVIDIA", "SHORT"):
        assert {"ring_to", "from_to", "paint"} <= set(got[lab]), (lab, got[lab])
    assert not {"ring_to", "from_to", "paint"} & set(got["PLAIN"]), "the spring landing is written as it always was"
    want, _notes = B.chip_stamp_ring_fit(dict(stamped, _catalogue="icons"),
                                         B.page_on_screen(seen["world"], seen["species"], 10.0), "16:9", _gpu_paint(), [], "x")
    assert (got["NVIDIA"]["ring_to"], got["NVIDIA"]["from_to"], got["NVIDIA"]["paint"]) == \
        (want["ring_to"], want["from_to"], want["paint"]), "the row loop writes the door's own fit"
    assert got["NVIDIA"]["from_to"] == B.STAMP_APPROACH_MIN and "the approach comes down from 1.20x" in out
    assert "[WARN] P70 T1: shot row 1 (0.0-30.0s) chip stamp 'NVIDIA'" in out and "the ring is drawn at its floor" in out
    assert "[WARN] P70 T1: shot row 1: chip stamp 'PLAIN'" in out and "under the E99 s90 phone floor" in out
    assert "[WARN] P70 T1: shot row 1: chip stamp 'SHORT'" in out and "dur 0.5s is shorter than" in out


LIVE_LABELS = ("NVIDIA", "BEAR MARKET", "SK hynix", "WAVE")
_LIVE_READ = """() => { const faces = [...document.fonts].filter(f => /kalam/i.test(f.family) && String(f.weight) === "700");
  return { loaded: faces.some(f => f.status === "loaded"),
           labels: [...document.querySelectorAll('text.chipstamplab')].map(t => { const b = t.getBBox();
             return { text: t.textContent, len: t.getComputedTextLength(), w: b.width, h: b.height,
                      top: +t.getAttribute('y') - b.y, bot: b.y + b.height - +t.getAttribute('y') }; }) }; }"""


def test_the_label_table_matches_the_LIVE_face_as_the_browser_draws_it(tmp_path):
    """The review's fix 3: the table is a measurement of Kalam 700 as served (fonts.googleapis.com, the player's own
    link), so a font update or a fallback face would move the real label off it silently. This renders the four labels
    with the LIVE face and holds the table to the drawn text: the advance to 1 px, the drawn box inside the table's."""
    playwright = pytest.importorskip("playwright.sync_api")
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface("chip-stamp-arrival")
    sp0 = tl["scenes"][0]["species"][0]
    tl["scenes"][0]["species"] = [dict(sp0, label=lab, target={"kind": "point", "x": 0.25 + 0.5 * (i % 2), "y": 0.3 + 0.4 * (i // 2)})
                                  for i, lab in enumerate(LIVE_LABELS)]
    html = tmp_path / "live-labels.html"
    html.write_text(RB.instantiate(tl, uris, RB.TEMPLATE), encoding="utf-8")
    w, h = RB.STAGE[aspect or "16:9"]
    srv, port = RB.serve(html.parent)
    try:
        with playwright.sync_playwright() as pw:
            try:
                br = pw.chromium.launch(headless=True)
            except Exception as exc:   # noqa: BLE001 - no browser is a skip with its reason, never a pass
                pytest.skip(f"playwright chromium not installed: {exc}")
            page = br.new_context(viewport={"width": w, "height": h}).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            RB.frame_png(page, 13.0, (w, h))
            page.wait_for_timeout(300)
            read = page.evaluate(_LIVE_READ)
            br.close()
    finally:
        srv.shutdown()
    if not read["loaded"]:
        pytest.skip("the live Kalam 700 face did not load (offline: fonts.googleapis.com unreachable) - the table is "
                    "held to the served face only")
    size = B.CHIP_STAMP_LABEL_FLOOR
    assert sorted(r["text"] for r in read["labels"]) == sorted(LIVE_LABELS)
    for r in read["labels"]:
        est = sum(B.CHIP_STAMP_LABEL_ADVANCE_EM[c] for c in r["text"]) * size
        box = B.chip_stamp_label_box(r["text"], 260)
        assert abs(r["len"] - est) <= 1.0, (r["text"], r["len"], est)
        assert r["w"] <= box["x1"] - box["x0"] - 2 * B.CHIP_STAMP_LABEL_KEYLINE_PX + 1.0, (r["text"], r["w"])
        assert r["top"] <= B.CHIP_STAMP_LABEL_ASC_EM * size + 1.0 and r["bot"] <= B.CHIP_STAMP_LABEL_DESC_EM * size + 1.0, r
