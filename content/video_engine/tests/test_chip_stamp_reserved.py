"""P71 T5 (R26-313; E99 s128): A STAMPED CHIP'S SEAL IS RESERVED - the row's OTHER stamps and cards keep off it; the
stamp itself stays where it lands, over the chart.

E99 s128 (the operator, 2026-09-24, on the seal sheet): "the prop is an object that is meant to live in the world, a
stamp is us just saying 'hey we're applying this thing here for your reference' so i dont mind it being drawn over".
Its carrier here: "a stamped chip's reserved box keeps OTHER elements from landing under it on the same beat; it does
not keep the stamp off the chart". P69 T5's law (E99 s88 (3), "the stamp takes the room first") already fitted a row's
stamped DOCKS in row order, each round the earlier ones' boxes; a stamped CHIP (P70 T1 / T1b) was fitted against those
boxes but never added its own, so a later stamp, a second chip or a card could land on its seal. What this file holds:

  (1) the box: a stamped chip reserves its SEAL (`seal_r`) and its impact ring's peak (`ring_to` x `seal_r` plus the
      stroke), the square round that disc at the grown mark's painted centre; a glyph chip reserves nothing;
  (2) the order: a stamped chip joins the row's stamp order at its `at` (a dock landing at the same instant goes first);
  (3) the acceptance, through `main()` on a one-row bed: a later stamped dock, a card and a second stamped chip each go
      round the chip's reserved box - or, where no room exists, the build is told with numbers (s106);
  (4) s128: the stamped chip ITSELF is never moved, grown, shrunk or filled for the chart - its place and size are the
      same over a drawn line as over an empty plot, and the first chip of a row is fitted exactly as it was;
  (5) a row with no stamped chip is fitted exactly as it was.
"""
from __future__ import annotations

import copy
import json
import math
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as BGS  # noqa: E402

GPU = "prop-icon-gpu-ai-accelerator-v1"
FED = "prop-federal-reserve-building-v1"
PLAIN = {"asset_id": "plate-plain"}
WHERE = "shot row 1 (0.0-30.0s)"


def _chip(**extra) -> dict:
    return {"kind": "chip", "form": "stamp", "arrive": "stamp", "at": 10.0, "dur": 3.0, "icon": GPU, "label": "NVIDIA",
            "size": 180, "target": {"kind": "point", "x": 0.3, "y": 0.45}, **extra}


def _glyph(**extra) -> dict:
    return {"kind": "chip", "icon": "cpu", "label": "NVIDIA", "at": 10.0, "dur": 3.0,
            "target": {"kind": "point", "x": 0.3, "y": 0.45}, **extra}


def _gpu_paint() -> dict:
    return B.painted_box(B.catalogue_stamp_asset(GPU)["file"])


def _centre(chip: dict) -> tuple[float, float]:
    return B.chip_stamp_art(chip, "16:9", _gpu_paint())["centre"]


def _seal_box(chip: dict) -> dict:
    """The box T5 reserves, computed here from the fitted chip's own numbers (the seal, the ring's peak, the stroke)."""
    cx, cy = _centre(chip)
    r = chip["ring_to"] * chip["seal_r"] + B.STAMP_RING_W_PX
    return {"x": math.floor(cx - r), "y": math.floor(cy - r),
            "w": math.ceil(cx + r) - math.floor(cx - r), "h": math.ceil(cy + r) - math.floor(cy - r)}


def _overlap(a: dict, b: dict) -> float:
    return (max(0.0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
            * max(0.0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])))


def _intrusion(cx: float, cy: float, r: float, box: dict) -> float:
    """How far a disc of radius r at (cx, cy) reaches into a rectangle (<= 0: clear)."""
    dx = max(box["x"] - cx, 0.0, cx - (box["x"] + box["w"]))
    dy = max(box["y"] - cy, 0.0, cy - (box["y"] + box["h"]))
    return r - math.hypot(dx, dy)


# ---- (1) the box ------------------------------------------------------------------------------------------------------


def test_a_stamped_chip_reserves_its_SEAL_and_its_rings_PEAK_the_square_round_that_disc():
    chip, _notes = B.chip_stamp_ring_fit(_chip(), PLAIN, "16:9", _gpu_paint(), [], "c")
    box = B.chip_stamp_reserved_box(chip, "16:9", _gpu_paint())
    cx, cy = _centre(chip)
    assert chip["ring_to"] > 1.0, "the ring's peak stands outside the seal"
    assert box == _seal_box(chip), box
    assert box["x"] <= cx - chip["seal_r"] and box["x"] + box["w"] >= cx + chip["seal_r"], "the whole seal is inside it"


def test_a_GLYPH_chip_reserves_nothing_its_law_is_the_badge_spring():
    assert B.chip_stamp_reserved_box(_glyph(), "16:9", _gpu_paint()) is None
    assert B.chip_stamp_reserved_box(_chip(arrive=None), "16:9", _gpu_paint()) is None, "the stamp form on its spring"


# ---- (2) the order ------------------------------------------------------------------------------------------------------


def test_a_stamped_chip_joins_the_rows_stamp_order_at_its_AT():
    # stamped docks 0 (enter 5) and 2 (enter 12); chips at 3, 5 and 20
    assert B.stamp_order([(0, 5.0), (2, 12.0)], []) == [("dock", 0), ("dock", 2)], "no chip: the docks in row order"
    assert B.stamp_order([(0, 5.0), (2, 12.0)], [3.0, 5.0, 20.0]) == \
        [("chip", 0), ("dock", 0), ("chip", 1), ("dock", 2), ("chip", 2)], "a dock landing at the chip's instant goes first"
    assert B.stamp_order([], [3.0]) == [("chip", 0)]


def test_row_stamp_fits_with_no_chip_is_the_walk_it_always_was():
    world = copy.deepcopy(BGS.SURFACES["prop-stamp"]()[0]["scenes"][0]["world"])
    docks = [("ev-prop-fed", B.dock_opts({"prop": True, "arrive": "stamp"}), B.painted_box(BGS.PROP_CUTOUT))]
    assert B.row_stamp_fits(world, "16:9", docks, None, [], "r") == \
        B.row_stamp_fits(world, "16:9", docks, None, [], "r", chips=[], enters=[12.0])


# ---- (3) the acceptance, through main() on a one-row bed ---------------------------------------------------------------


class _PastThePlace(Exception):
    """Raised at the row's first dock (or, with none, at its build windows), once its stamps are fitted and its cards'
    place is taken."""


def _bed(tmp_path, monkeypatch, species: list, docks: list, plate: str = "ledger:ev-row-path:line") -> dict:
    """`main()` on one ledger-page row (test_chip_stamp_arrival's bed), stopped at the first dock of the dock loop.
    Returns what the row path decided: the fitted chips (in fitting order), every `row_stamp_fits` answer, the cards'
    `place` and the world. `plate` (the row's plate): the page by default, or a picture plate, where a lone ring has room."""
    ep, build = tmp_path / "ep", tmp_path / "ep" / "build"
    (ep / "evidence/objects").mkdir(parents=True)
    (build / "audio").mkdir(parents=True)
    shutil.copy2(BGS.SERIES, ep / "evidence/objects" / "ev-row-path.series.json")
    shutil.copy2(BGS.PROP_CUTOUT, ep / "evidence/objects" / f"{FED}.png")
    (build / "audio/episode.mp3").write_bytes(b"")
    (build / "timeline.json").write_text(json.dumps({"runtime_s": 30.0, "words": []}), encoding="utf-8")
    (build / "caption-pages.json").write_text("[]", encoding="utf-8")
    row = (0.0, 30.0, plate, (0, 0, 0), docks, None, species)
    (ep / "SHOT-ROW-PATH.py").write_text("W = " + repr([row]) + "\n", encoding="utf-8")
    seen: dict = {"chips": [], "stamps": [], "place": None}
    real_fit, real_rows, real_place = B.chip_stamp_ring_fit, B.row_stamp_fits, B.dock_place

    def chip_fit(entry, world, *a, **k):
        out = real_fit(entry, world, *a, **k)
        if B.chip_is_stamped(entry):
            seen["chips"].append(out[0])
            seen["world"] = world
        return out

    def rows(*a, **k):
        out = real_rows(*a, **k)
        seen["stamps"].append(out)
        return out

    def place(*a, **k):
        out = real_place(*a, **k)
        if "clear_of" in k:   # the row loop's own call (the stamp fit's E65 tie-break passes it positionally)
            seen["place"], seen["clear_of"] = out, list(k["clear_of"] or [])
        return out

    def stop(*_a, **_k):
        raise _PastThePlace

    for name, value in (("BUILD", build), ("EP", ep), ("SHOT_TABLE_FILE", "SHOT-ROW-PATH.py"), ("ASPECT", "16:9"),
                        ("chip_stamp_ring_fit", chip_fit), ("row_stamp_fits", rows), ("dock_place", place),
                        ("solo_centre_by_clock", stop), ("page_build_windows", stop)):
        monkeypatch.setattr(B, name, value)
    monkeypatch.setattr(B.R, "EP", ep)
    with pytest.raises((_PastThePlace, SystemExit)) as info:
        B.main()
    assert info.type is _PastThePlace, f"the row failed: {info.value}"
    return seen


DESK = "world-spike-desk-v1"   # a picture plate (test_stamp_is_a_seal's): no page ink, so a lone ring has room to 2x
STAMP_DOCK = (FED, 1, 12.0, 20.0, {"prop": True, "arrive": "stamp"})
CARD = ("ev-a-card", 0, 11.0, 20.0)


def _dock_alone(tmp_path, monkeypatch) -> dict:
    return _bed(tmp_path / "alone", monkeypatch, [], [STAMP_DOCK])["stamps"][-1][0][0]


def test_1_a_LATER_stamped_dock_goes_round_the_chips_reserved_box(tmp_path, monkeypatch, capsys):
    alone = _dock_alone(tmp_path, monkeypatch)
    cx, cy = alone["centre"]   # the chip lands on the very room the dock takes alone
    chip = _chip(target={"kind": "point", "x": cx / 1920, "y": cy / 1080})
    seen = _bed(tmp_path / "both", monkeypatch, [chip], [STAMP_DOCK])
    fitted = seen["chips"][0]
    box = _seal_box(fitted)
    dock = seen["stamps"][-1][0][0]
    hull = B._rest_hull(dock["centre"], dock["painted"], B.prop_rest_deg(B.dock_opts(STAMP_DOCK[4])))
    ring = dock["ring_to"] * 0.5 * math.hypot(*dock["painted"]) + B.STAMP_RING_W_PX
    assert _overlap(hull, box) == 0, f"the dock's mark {hull} lands on the chip's seal {box}"
    assert _intrusion(*dock["centre"], ring, box) <= 1e-6, "the dock's ring stays off the chip's seal"
    assert box in seen["stamps"][-1][1], "the chip's box is in the row's reserved list, for the cards"
    assert dock["centre"] != alone["centre"], "the dock moved off the chip's seal"


def test_2_a_CARD_placed_by_the_page_goes_round_the_chips_reserved_box(tmp_path, monkeypatch):
    first = _bed(tmp_path / "alone", monkeypatch, [], [CARD])["place"]
    chip = _chip(target={"kind": "point", "x": (first["x"] + first["w"] / 2) / 1920,
                                  "y": (first["y"] + first["h"] / 2) / 1080})
    seen = _bed(tmp_path / "both", monkeypatch, [chip], [CARD])
    box = _seal_box(seen["chips"][0])
    assert box in seen["clear_of"], "the card is placed clear of the chip's seal"
    card = seen["place"]
    assert card is None or _overlap(card, box) == 0 or card.get("room") == "overlap",         f"the card {card} lands on the chip's seal {box} without the least-overlap WARN's room"


def test_2b_a_card_OVER_a_chips_seal_is_REPORTED_with_its_numbers_never_refused():
    chip, _notes = B.chip_stamp_ring_fit(_chip(), PLAIN, "16:9", _gpu_paint(), [], "c")
    box = _seal_box(chip)
    card = {"x": box["x"] + 10, "y": box["y"] + 10, "w": 300, "h": 200}
    msg = B.stamp_clash_error("shot row 1 dock ev-a-card", card, [box])
    assert msg and f"[{box['x']}, {box['y']}, {box['w']}, {box['h']}]" in msg, msg


def test_3_a_SECOND_stamped_chip_is_fitted_clear_of_the_first(tmp_path, monkeypatch, capsys):
    a = _chip(label="A", at=10.0, target={"kind": "point", "x": 0.30, "y": 0.45})
    b = _chip(label="B", at=11.0, target={"kind": "point", "x": 0.62, "y": 0.45})
    seen = _bed(tmp_path, monkeypatch, [a, b], [], plate=DESK)
    fa, fb = seen["chips"]
    box_a = _seal_box(fa)
    ring_b = fb["ring_to"] * fb["seal_r"] + B.STAMP_RING_W_PX
    out = capsys.readouterr().out
    assert _intrusion(*_centre(fb), ring_b, box_a) <= 1e-6, \
        f"the second chip's seal and ring reach {_intrusion(*_centre(fb), ring_b, box_a):.1f} px into the first's {box_a}"
    assert "[WARN] P71 T5" not in out, "there is room: no finding"
    alone, _ = B.chip_stamp_ring_fit(b, seen["world"], "16:9", _gpu_paint(), [], "b")
    assert fb["ring_to"] < alone["ring_to"], "its ring gives way to the first chip's seal"
    assert (fb["size"], fb["seal_r"], _centre(fb)) == (alone["size"], alone["seal_r"], _centre(alone)), \
        "the second chip keeps its place and size - only its ring gives way"


def test_3b_two_chips_whose_SEALS_meet_are_a_WARN_with_their_numbers_never_moved(tmp_path, monkeypatch, capsys):
    a = _chip(label="A", at=10.0, target={"kind": "point", "x": 0.40, "y": 0.45})
    b = _chip(label="B", at=11.0, target={"kind": "point", "x": 0.50, "y": 0.45})
    seen = _bed(tmp_path, monkeypatch, [a, b], [])
    fa, fb = seen["chips"]
    box_a = _seal_box(fa)
    out = capsys.readouterr().out
    line = next((ln for ln in out.splitlines() if "[WARN] P71 T5" in ln), "")
    assert "chip stamp 'B'" in line and f"[{box_a['x']}, {box_a['y']}, {box_a['w']}, {box_a['h']}]" in line, out
    assert " px into " in line and "E99 s128" in line, line
    assert _centre(fb) == _centre(b | {"size": fb["size"]}), "the second chip stands on its own target"


# ---- (4) s128: the stamp itself stays where it lands, over the chart ------------------------------------------------------


def test_4_the_FIRST_chip_of_a_row_is_fitted_exactly_as_it_was(tmp_path, monkeypatch):
    a = _chip(label="A", at=10.0, target={"kind": "point", "x": 0.30, "y": 0.45})
    b = _chip(label="B", at=11.0, target={"kind": "point", "x": 0.62, "y": 0.45})
    seen = _bed(tmp_path, monkeypatch, [a, b], [])
    today, _ = B.chip_stamp_ring_fit(a, seen["world"], "16:9", _gpu_paint(), B.newsreel_boxes([a, b], "16:9"), "a")
    first = seen["chips"][0]
    for k in ("size", "seal_r", "ring_to", "from_to", "paint", "target"):
        assert first[k] == today[k], k


def test_4b_a_chip_over_a_DRAWN_LINE_keeps_its_place_and_size_exactly(tmp_path, monkeypatch):
    """s128 (1): overlapping the data is not a defect. The same chip over the page with its line and over the same page
    with no ink at all: its place, its grown size and its seal are the same; T5 adds no chart ink to its obstacles."""
    chip = _chip(target={"kind": "point", "x": 0.5, "y": 0.5})
    seen = _bed(tmp_path, monkeypatch, [chip], [])
    world = seen["world"]
    boxes = B.LPG.page_boxes(world["page"], "16:9")
    cx, cy = _centre(seen["chips"][0])
    pl = boxes["plot"]
    assert pl["x"] < cx < pl["x"] + pl["w"] and pl["y"] < cy < pl["y"] + pl["h"], "the chip stands over the plot"
    assert "1" in "".join(boxes.get("data_mask") or []), "the page draws a line"
    over, _ = B.chip_stamp_ring_fit(chip, world, "16:9", _gpu_paint(), [], "c")
    bare, _ = B.chip_stamp_ring_fit(chip, PLAIN, "16:9", _gpu_paint(), [], "c")
    for k in ("size", "seal_r", "paint", "target"):
        assert over[k] == bare[k], k
    assert _centre(over) == _centre(bare) == _centre(seen["chips"][0])


# ---- (5) byte-identical --------------------------------------------------------------------------------------------------


def test_5_a_row_with_NO_stamped_chip_is_fitted_as_it_always_was(tmp_path, monkeypatch):
    seen = _bed(tmp_path, monkeypatch, [_glyph()], [STAMP_DOCK, CARD])
    assert len(seen["stamps"]) == 1, "one walk of the row's stamps, as before"
    assert seen["chips"] == []
    fits, taken = seen["stamps"][0]
    assert seen["clear_of"] == taken and len(taken) == 1, "the cards go round the stamped dock only"


# ---- (6) the READ pop clears the seals too (the parent's ruling: a recorded deviation into P71 T15's `read_over_build`) --


class _PastTheCard(Exception):
    """Raised once the row's first dock (the card) is written, with its read decided."""


def _bed_read(tmp_path, monkeypatch, species: list, docks: list) -> dict:
    """The one-row bed run past the card's E63 read: the card's `dock_entry` arguments and the row's reserved boxes."""
    ep = tmp_path / "ep"
    (ep / "evidence/objects").mkdir(parents=True)
    shutil.copy2(BGS.PROP_CUTOUT, ep / "evidence/objects" / "ev-a-card.png")   # any picture: the card's own asset
    seen: dict = {"stamps": []}
    real_rows = B.row_stamp_fits

    def entry(aid, slot, enter, exitt, n_badges, kind=None, place=None, arrive=None, mass=None, centre=False, **k):
        seen["card"] = dict(k, aid=aid, slot=slot, place=place, centre=centre)
        raise _PastTheCard

    def rows(*a, **k):
        out = real_rows(*a, **k)
        seen["stamps"].append(out)
        seen["page"] = (a[0] or {}).get("page")
        return out

    build = ep / "build"
    (build / "audio").mkdir(parents=True)
    shutil.copy2(BGS.SERIES, ep / "evidence/objects" / "ev-row-path.series.json")
    shutil.copy2(BGS.PROP_CUTOUT, ep / "evidence/objects" / f"{FED}.png")
    (build / "audio/episode.mp3").write_bytes(b"")
    (build / "timeline.json").write_text(json.dumps({"runtime_s": 30.0, "words": []}), encoding="utf-8")
    (build / "caption-pages.json").write_text("[]", encoding="utf-8")
    row = (0.0, 30.0, "ledger:ev-row-path:line", (0, 0, 0), docks, None, species)
    (ep / "SHOT-ROW-PATH.py").write_text("W = " + repr([row]) + "\n", encoding="utf-8")
    for name, value in (("BUILD", build), ("EP", ep), ("SHOT_TABLE_FILE", "SHOT-ROW-PATH.py"), ("ASPECT", "16:9"),
                        ("dock_entry", entry), ("row_stamp_fits", rows)):
        monkeypatch.setattr(B, name, value)
    monkeypatch.setattr(B.R, "EP", ep)
    with pytest.raises((_PastTheCard, SystemExit)) as info:
        B.main()
    assert info.type is _PastTheCard, f"the row failed: {info.value}"
    return seen


BED_B = ([_chip(label="NVIDIA", at=10.0, target={"kind": "point", "x": 0.325, "y": 0.48}),
          _chip(label="MEMORY", at=11.0, target={"kind": "point", "x": 0.56, "y": 0.22})],
         [("ev-a-card", 0, 11.5, 20.0), (FED, 1, 12.0, 20.0, {"prop": True, "arrive": "stamp"})])


def test_6_the_cards_READ_pop_clears_every_chips_seal_as_its_park_does(tmp_path, monkeypatch, capsys):
    """Bed b's frame read (59.86-61.8 s): the card parked clear of both seals, but E63 grew its READ over NVIDIA's seal
    (34 408 px^2). The read now clears every reserved box, or the card is not read-popped at all."""
    seen = _bed_read(tmp_path, monkeypatch, *BED_B)
    card, boxes = seen["card"], seen["stamps"][-1][1]
    assert len(boxes) == 3, f"two chip seals and the stamped dock are reserved: {boxes}"
    read = card.get("read_place") or (None if (card.get("centre") or card.get("read_deferred"))
                                      else B.dock_read_box("16:9", None, None))
    out = capsys.readouterr().out
    for s in boxes:   # r4: clear, or the WARN with its numbers (s106 - the engine advises, the author decides)
        assert _overlap(card["place"], s) == 0 or "(its park): no clear spot holds it" in out, f"the park {card['place']} lands on {s}"
        assert read is None or _overlap(read, s) == 0 or "(its read): its box" in out, f"the read {read} lands on {s}"
    assert "(its read): its box" not in out, "the read is clear, or deferred"


def test_6b_a_read_that_cannot_clear_a_seal_is_moved_or_deferred_never_drawn_over_it():
    """`read_over_build` with a stamp over the only room its read had: the read goes elsewhere or is deferred."""
    world = copy.deepcopy(BGS.SURFACES["prop-stamp"]()[0]["scenes"][0]["world"])
    page, read_box = world["page"], B.dock_read_box("16:9")
    place = B.dock_place(world, "16:9", [])
    free = B.read_over_build(place, read_box, page, "16:9", 10.0, 11.2, [])
    target = (free or {}).get("read_place") or read_box
    stamp = {"x": target["x"] + 10, "y": target["y"] + 10, "w": 60, "h": 60}
    got = B.read_over_build(place, read_box, page, "16:9", 10.0, 11.2, [], stamps=[stamp])
    assert got is not None, "a read over a stamp is decided, not left where it lands"
    assert got.get("read_deferred") or _overlap(got["read_place"], stamp) == 0, got
    assert B.read_over_build(place, read_box, page, "16:9", 10.0, 11.2, [], stamps=[]) == free, "no stamp: as before"


def test_6c_a_read_left_over_a_seal_is_a_WARN_with_its_numbers():
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    body = src[src.index('_drawn_read = None if (stamp_fit or e63.get("read_deferred"))'):][:700]
    assert "stamp_clash_error(" in body and "(its read)" in body and "[WARN] P71 T5" in body and "SystemExit" not in body


# ---- (7) round 3: a park or a read never covers the page's own words (E28; the parent's ruling) ------------------------


def _path(a: dict, b: dict, n: int = 21) -> list[dict]:
    """The card's box from its read to its park: every box on the straight path (the engine's min-jerk slide is a
    monotone re-timing of it, so these are every box it passes through, to the sampling)."""
    return [{k: a[k] + (b[k] - a[k]) * i / (n - 1) for k in ("x", "y", "w", "h")} for i in range(n)]


def test_7_the_card_never_covers_the_basis_label_or_a_seal_from_its_read_to_its_park(tmp_path, monkeypatch, capsys):
    """Bed b round 2: parked at [520, 224] over "index - 100 = Aug 2025, log scale" (E28 (2): a selected axis states its
    rule on the page). Now the read, the park and every box of the slide between clear the basis label, every end tag,
    the source line and all three reserved boxes."""
    seen = _bed_read(tmp_path, monkeypatch, *BED_B)
    card, boxes = seen["card"], seen["stamps"][-1][1]
    words = [(n, r) for n, r in B.prop_obstacle_groups(seen["page"], "16:9")[0]["label"]   # the page's words (the test's
             if n not in ("title", "sub", "the x axis")]                                    # own read of them: E45 / E65 exempt)
    names = [n for n, _r in words]
    assert "the basis label" in names, f"the page states its rule: {names}"
    read = card.get("read_place") or card["place"]
    out = capsys.readouterr().out
    warned = "(its park): no clear spot holds it" in out
    for box in _path(read, card["place"]):
        for s in boxes:   # r4: a seal is the lesser fault - covered only with the WARN
            assert _overlap(box, s) == 0 or warned, f"{box} lands on the reserved box {s} with no WARN"
        for n, r in words:   # ... and a WORD outranks a seal: the card covers the basis label only if nothing else holds
            assert _overlap(box, r) == 0 or (warned and f"covers {n}" in out), f"{box} covers {n} {r} with no WARN"


def test_7b_a_park_that_covers_no_word_is_the_park_it_always_was(monkeypatch):
    world = copy.deepcopy(BGS.SURFACES["prop-stamp"]()[0]["scenes"][0]["world"])
    now = B.page_place(world["page"], "16:9")
    monkeypatch.setattr(B, "page_text_boxes", lambda page, aspect: [])
    before = B.page_place(world["page"], "16:9")
    words = [r for _n, r in B.prop_obstacle_groups(world["page"], "16:9")[0]["label"]]
    if not any(_overlap(before, r) > 0 for r in words if r):
        assert now == before, "no stamp, no word under it: byte-identical"


def test_7c_the_heading_and_the_x_ticks_stay_E45_s_and_E65_s():
    assert B.PLACE_TEXT_EXEMPT == ("title", "sub", "the x axis")
    world = copy.deepcopy(BGS.SURFACES["prop-stamp"]()[0]["scenes"][0]["world"])
    names = [n for n, _r in B.page_text_boxes(world["page"], "16:9")]
    assert not {"title", "sub", "the x axis"} & set(names) and "source" in names


def test_7d_the_last_resort_and_a_read_no_larger_than_its_park_are_WARNs_with_numbers():
    words = [("the basis label", {"x": 151, "y": 208, "w": 947, "h": 36})]
    msg = B.text_cover_notes("row 4 dock d (its park)", {"x": 520, "y": 224, "w": 148, "h": 107}, words)
    assert msg and "covers the basis label [151, 208, 947, 36] by 2960 px^2" in msg[0], msg
    assert B.text_cover_notes("r", {"x": 520, "y": 300, "w": 148, "h": 107}, words) == []
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    assert "the pop is not a read" in src and "is no larger than" in src


# ---- (8) round 4: never trade legibility for clearance (E99 s106; the parent's ruling) ----------------------------------


def _default_park(page: dict) -> dict:
    """The card's DEFAULT PARK: where the compiler parks it with nothing in the way (no stamp, no word)."""
    return B.page_place(page, "16:9", [], None, words=False)


def test_8_a_card_is_NEVER_placed_below_its_default_park_size(tmp_path, monkeypatch, capsys):
    """Round 3 kept bed b's card clear by shrinking it into E65's corner at the floor (100 x 80, illegible). The park
    and the read are never smaller than the park the card takes when nothing is in the way."""
    seen = _bed_read(tmp_path, monkeypatch, *BED_B)
    card, park = seen["card"], _default_park(seen["page"])
    assert card["place"]["w"] >= park["w"] and card["place"]["h"] >= park["h"], \
        f"the card {card['place']} is below its default park {park}"
    if card.get("read_place"):
        assert card["read_place"]["w"] >= park["w"], f"the read {card['read_place']} is below the park {park}"


def test_8a_where_the_room_is_full_the_card_keeps_off_the_CHART_and_takes_the_seal_with_the_WARN(tmp_path, monkeypatch,
                                                                                                 capsys):
    """Round 5 (the parent's order): page words > plot ink > seals. E45: a dock never covers the chart - the data ink is
    the evidence; a seal is a stamp drawn over the world (s128), the lesser fault. On this bed no spot at the park size
    is clear, so the card keeps its size OFF the plot's ink and takes the seal overlap - and says so."""
    seen = _bed_read(tmp_path, monkeypatch, *BED_B)
    card, boxes = seen["card"]["place"], seen["stamps"][-1][1]
    out = capsys.readouterr().out
    ink = [r for _n, r in B.prop_obstacle_groups(seen["page"], "16:9")[0]["data"]]
    assert card.get("room") == "overlap", card
    assert sum(_overlap(card, c) for c in ink) == 0, f"the card {card} covers the chart's ink"
    assert any(_overlap(card, s) > 0 for s in boxes), "... it takes the seal instead (the lesser fault)"
    line = next((ln for ln in out.splitlines() if "(its park): no clear spot holds it" in ln), "")
    assert "a seal or stamp" in line and "the plot's ink" not in line, line
    assert "the room is full: give the card a slot, drop a stamp, or dock it after the seals leave" in line


def test_8b_where_every_spot_covers_a_seal_the_card_keeps_its_size_and_covers_NO_WORD():
    """The overlap cost is ordered page words > seals > plot ink: a seal over the whole safe box leaves only covered
    spots, and the card takes one at its full park size that covers none of the page's words."""
    world = copy.deepcopy(BGS.SURFACES["prop-stamp"]()[0]["scenes"][0]["world"])
    page, park = world["page"], _default_park(world["page"])
    safe = B.LPG.page_boxes(page, "16:9")["safe"]
    got = B.page_place(page, "16:9", [], [dict(safe)])
    assert (got["w"], got["h"]) == (park["w"], park["h"]) and got["room"] == "overlap", got
    for n, r in B.page_text_boxes(page, "16:9"):
        assert _overlap(got, r) == 0, f"the card {got} covers {n} {r} - a word outranks a seal"
    msg = B.park_full_note("shot row 1 dock d", got, page, "16:9", [dict(safe)])
    assert msg and "the room is full: give the card a slot, drop a stamp, or dock it after the seals leave" in msg, msg
    assert f"{park['w']}x{park['h']}" in msg and "a seal or stamp" in msg


def test_8c_with_nothing_in_the_way_the_park_is_the_search_to_the_byte(monkeypatch):
    world = copy.deepcopy(BGS.SURFACES["prop-stamp"]()[0]["scenes"][0]["world"])
    monkeypatch.setattr(B, "page_text_boxes", lambda page, aspect: [])
    assert B.page_place(world["page"], "16:9") == B._page_place_search(world["page"], "16:9")
