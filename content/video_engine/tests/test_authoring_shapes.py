"""The shape compiler (P66 T3): the AUTHORED beat plan in, the approved skeleton out.

The rules asserted here are the plan's Acceptance 2, on the base the compiler emits from the TOKYO
bed's own read-back plan (P66 T7) at 9:16 - the open on the chart, the mount's clock, the axes
entry, the dip on a world change, the spiral return, the plate's six seconds, no rail and no park
in portrait, and a light only where the sentence points and only after the page's chart lands.

The Japan plan is compiled too, and only ONE thing is claimed of it: that it compiles and round
trips. Its rows are NOT the approved Japan cut's rows and this file never says they are (E99 s11:
the approved cuts are not rebuilt).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

from authoring import shapes as SH  # noqa: E402
from authoring import table as T  # noqa: E402

PROJECTS = ROOT / "content/video_engine/projects/systems-and-blowups"
TOKYO = PROJECTS / "tokyo-tea-break/build-short"
JAPAN = PROJECTS / "japan-tariff-trick/build-short"
LIGHTS = SH.LIGHT_KINDS
CLOCKED = SH.LIGHT_AFTER_BUILD_KINDS   # P66 T3c: the lights the "after the build" clock binds - and only those


def _words(build: Path) -> list[dict]:
    return json.loads((build / "timeline.json").read_text(encoding="utf-8"))["words"]


def _pages(build: Path):
    """The CLI's own page resolver, on this build's project - `shapes` reads a page's geometry only
    through the caller (`generate_base_table.page_resolver`; the kit names no episode)."""
    def pages(plate: str):
        C = SH.compiler()
        return (C.ledger_world(C.split_plate_opts(str(plate))[0], (0, 0, 0), build.parent) or {}).get("page")
    return pages


def _base(build: Path, aspect: str = "9:16"):
    """(the plan, the rows, the ROW records of `why`) - `SH.silent_why` reads the rest (P66 T3b)."""
    plan = SH.load_plan(build / "BEAT-PLAN.jsonl")
    rows, why = SH.compile(plan, _words(build), SH.DEFAULTS, aspect, pages=_pages(build))
    return plan, rows, SH.rows_why(why)


def _card_box(options: dict, aspect: str = "9:16") -> dict | None:
    """The stage rectangle a row's own placement puts a card in - the compiler's own arithmetic
    (`centred_place` with an authored centre: the width is `centre_w` of the stage, the height the
    card's 16:9 frame and its chrome)."""
    if not SH.placed(options):
        return None
    sw, sh = SH.pager().STAGE_PX[aspect]
    w = round(float(options["centre_w"]) * sw)
    h = round(w * float(options["card_aspect"])) if options.get("card_aspect") else SH.compiler().dock_card_h(w)
    return {"x": round(float(options["centre_x"]) * sw - w / 2), "y": round(float(options["centre_y"]) * sh - h / 2),
            "w": w, "h": h}


def _page(build: Path, plate: str):
    return _pages(build)(plate) if str(plate).startswith("ledger:") else None


@pytest.fixture(scope="module")
def tokyo():
    return _base(TOKYO)


@pytest.fixture(scope="module")
def japan():
    return _base(JAPAN)


def _land(plate: str) -> float:
    """The page's own landing offset, from the plate the compiler emitted."""
    return SH.page_land_offset(SH.entry_in(plate), SH._mount_s(plate))


def _rec(beat, t0, t1, plate, sentence="A sentence about it.", act=None, caps=(), recipe=None, row=None,
         moves=None):
    """One record in M41's schema - the shape a beat plan's line has on disk, with P66 T3b's
    optional `moves` (what the author says this sentence DOES)."""
    out = {"beat": beat, "t0": t0, "t1": t1, "sentence": sentence,
           "act": act if act is not None else "none of the 11 - it states the claim",
           "comparator": {"compared_to": "this against that"}, "capabilities": list(caps),
           "recipe": recipe, "why_none": None if recipe else "no proven recipe names this combination",
           "plate": plate, "source": "a fixture"}
    if row is not None:
        out["row"] = row
    if moves is not None:
        out["moves"] = list(moves)
    return out


def _take(plan, word_s: float = 0.35):
    """A take for a synthetic plan: each record's own sentence laid word by word across its window,
    so `at_word` resolves the way it does on a real take (`authoring/words.py`)."""
    ws = []
    for r in plan:
        toks = str(r["sentence"]).split()
        step = (float(r["t1"]) - float(r["t0"])) / max(len(toks), 1)
        for i, w in enumerate(toks):
            start = round(float(r["t0"]) + i * step, 2)
            ws.append({"w": w, "start": start, "end": round(start + min(step, word_s), 2)})
    return ws


# ---------------------------------------------------------------- the approved shape, on the Tokyo bed
def test_the_open_is_the_chart(tokyo):
    """E99 s67 Apply 6: the first row is the PAGE - on its axes, or mounting the hook's world on its
    last word when the plan's first beat carries a clip world (the Tokyo bed's does)."""
    _, rows, why = tokyo
    assert rows[0][0] == 0.0 and rows[0][2].startswith("ledger:")
    assert SH.entry_in(rows[0][2]) in ("axes", "mount")
    assert why[0]["skeleton"] in ("open-on-the-chart-axes", "open-page-mounts-the-world")
    assert "the open IS the chart" in why[0]["rule"]
    # the Tokyo bed's hook is a clip, so the page MOUNTS over it - and `why` says exactly that
    assert SH.entry_in(rows[0][2]) == "mount" and "mounts the hook's world" in why[0]["rule"]


def test_no_page_ever_arrives_built_and_the_clock_picks_the_entry(tokyo):
    """E99 s67 Apply 3: a page whose number lands 7 s or more after its entry mounts; every other
    page enters by its axes (a return by its spiral). `built` is never emitted.

    P66 T3b widened the list by ONE case, and only where the plan forces it: a page whose AUTHOR's
    own plate declares a `snap` or a `camera` (its chart already on it as it arrives) keeps that
    entry when the plan's first light is spoken before the clock's entry would have finished
    drawing - because the compiler will not fire a light over a build and will not move the
    author's beat either (see `shapes._entry`)."""
    _, rows, why = tokyo
    pages = [(r, w) for r, w in zip(rows, why) if r[2].startswith("ledger:")]
    assert pages, "the Tokyo bed is a page cut"
    for r, w in pages:
        entry = SH.entry_in(r[2])
        assert entry != "built" and ":built" not in r[2], r[2]
        assert entry in ("axes", "mount", "spiral") or entry in SH.BUILT_ON_ARRIVAL, r[2]
        if entry in SH.BUILT_ON_ARRIVAL:
            assert "the author's own" in w["rule"] and "before a" in w["rule"], w["rule"]
            continue
        if "the number lands at +" in w["rule"]:
            late = float(w["rule"].split("the number lands at +")[1].split("s")[0])
            assert (entry == "mount") == (late >= SH.MOUNT_AT_OR_AFTER_S), (late, r[2])
        if entry == "mount":
            assert "mount=" in r[2]


def test_the_return_comes_back_by_the_spiral(tokyo):
    """The Tokyo bed's holdings page has been on screen, and the beat plan says it returns."""
    _, rows, why = tokyo
    spirals = [(r, w) for r, w in zip(rows, why) if SH.entry_in(r[2] or "") == "spiral"]
    assert spirals, "the Tokyo bed carries a return"
    for r, w in spirals:
        assert w["signature"] == "spiral" and "returns" in w["rule"]


def test_the_exits_are_the_approved_ones(tokyo):
    """E47: the dip when the WORLD changes; page to page a suck or a cut, and never into a mount."""
    _, rows, why = tokyo
    for i, r in enumerate(rows):
        exit_, nxt = r[5], rows[i + 1] if i + 1 < len(rows) else None
        if nxt is None:
            assert exit_ == "cut"
            continue
        if "mount=" in nxt[2]:
            assert exit_ == "cut", f"row {i} exits {exit_!r} INTO a mount"
        elif r[2].startswith("ledger:") and nxt[2].startswith("ledger:"):
            assert exit_ == "cut" or exit_.startswith("suck"), f"page to page took {exit_!r}"
        elif SH.plate_of(r[2]) != SH.plate_of(nxt[2]):
            assert exit_ == "dip", f"the world changes at row {i} and it exits {exit_!r} (E47)"


def test_no_plate_row_is_shorter_than_six_seconds(tokyo):
    """M44 / `PLATE_MIN_S`: the operator, on the balloon dock - "why do we have a plate less than 6
    seconds long?" The seconds are taken from a neighbouring row, never from the words."""
    _, rows, _ = tokyo
    for r in rows:
        if not r[2].startswith("ledger:"):
            assert round(r[1] - r[0], 2) >= SH.PLATE_MIN_S, r


def test_portrait_emits_no_rail_and_no_park(tokyo, japan):
    """R26-171 and R26-172: at 9:16 no `badges` rail and no `chart_to park` leaves the compiler."""
    for _, rows, _ in (tokyo, japan):
        for r in rows:
            assert all("badges" not in (d[4] or {}) for d in r[4] or [])
            assert all(not (s.get("kind") == "chart_to" and s.get("to") == "park") for s in r[6] or [])
        assert "badges" not in repr(rows) and "'park'" not in repr(rows)


def _is_page_build(sp: dict, row) -> bool:
    """The page's OWN build: a `build_to` whose cap lands with the page's chart (P47 T2). It belongs
    to the page's arrival, not to the sentence speaking at that instant."""
    return (sp.get("kind") == "build_to" and isinstance(sp.get("dur"), (int, float))
            and abs(float(sp["at"]) + float(sp["dur"]) - (row[0] + _land(row[2]))) <= SH.ANNOTATE_TOL_S)


def test_a_light_only_points_and_only_after_the_page_has_built(tokyo, japan):
    """E99 s67 Apply 1-2: a light is punctuation, not filler - it fires only on a sentence the plan
    says POINTS, and never before the page's own chart lands.

    P66 T3c narrowed WHICH species the clock binds: the LIGHT proper (the lamp that darkens the page
    around a point - `LIGHT_AFTER_BUILD_KINDS`). A `build_to` IS the build and a callout, a figure or
    a note is the sentence's own mark - both land on their word (M11 counts the build's cap)."""
    for plan, rows, _ in (tokyo, japan):
        gs = SH.groups(plan)
        for r, g in zip(rows, gs):
            for sp in r[6] or []:
                if r[2].startswith("ledger:") and sp["kind"] in CLOCKED:
                    assert sp["at"] + 1e-6 >= r[0] + _land(r[2]), (sp, r[2])
                if "target" in sp and not _is_page_build(sp, r):
                    assert SH.points(SH._beat_at(g, sp["at"])), (sp, r[2])


def test_the_first_chart_is_annotated_with_its_own_landing(tokyo):
    """M11, by the GATE's own rule (`gate_motion_density._first_chart_gate`): the first chart carries
    one of `ANNOTATED_KINDS` inside [the landing, the landing + `ANNOTATE_TOL_S`], **or** a `build_to`
    whose CAP lands there - the line ending ON the datum is the annotation (P47 T2)."""
    _, rows, _ = tokyo
    first = rows[0]
    assert first[2].startswith("ledger:")
    land = first[0] + _land(first[2])
    marks = [s for s in first[6] or []
             if s["kind"] in SH.ANNOTATED_KINDS and land - 1e-6 <= s["at"] <= land + SH.ANNOTATE_TOL_S]
    caps = [s for s in first[6] or [] if _is_page_build(s, first)]
    assert marks or caps, first[6]


def test_the_opens_build_lands_with_the_page_and_not_on_its_own_word(tokyo):
    """P66 T3c: the plan's `build_to` on beat 3 is spoken at "climbed" (7.6 s) while the open's page
    lands at 5.5 s - three seconds of build AFTER the chart is there reads as a chart standing full
    and unannotated (M11 FAIL on the first generated base). The build is placed to END on the landing
    instead, and the row's `why` says so."""
    _, rows, why = tokyo
    land = rows[0][0] + _land(rows[0][2])
    build = next(s for s in rows[0][6] if s["kind"] == "build_to")
    assert abs(build["at"] + build["dur"] - land) <= 1e-6, build
    assert "END on the page's landing" in why[0]["rule"]


def test_no_held_light_the_compiler_would_drop_as_a_flash_is_emitted(tokyo, japan):
    """`build_scene_timeline_f` drops a held species with under `HOLD_MIN_S` before the next event -
    so a base that emits one describes a cut that will not have it (the open's held spotlight, 0.64 s
    before the build, was dropped at compile time and M11 then read the chart as unannotated)."""
    for _, rows, _ in (tokyo, japan):
        for r in rows:
            for sp in r[6] or []:
                assert not SH.flashes(sp, r[6], list(r[4] or []), r[1]), (sp, r[0])


# ---------------------------------------------------------------- E65: the card's room on the page
def test_every_card_on_a_page_is_placed_in_the_pages_own_room(tokyo):
    """E65 / R26-172 (*"parking is not a way to make room for a card on 9:16; the page's own empty
    room is"*): a card that does not place itself is given a rectangle of the page's own, and its box
    touches no line of the page's ink and none of its data. A bare `centre: True` - which reads at the
    STAGE's centre, over the chart - never leaves the compiler."""
    _, rows, _ = tokyo
    seen = 0
    for r in rows:
        page = _page(TOKYO, r[2])
        if page is None:
            continue
        ink = SH.page_ink(page, "9:16")
        boxes = SH.pager().page_boxes(page, "9:16")
        for d in r[4] or []:
            if not SH.placed(d[4]):
                assert not d[4].get("centre"), d      # never the stage's centre over a page
                continue
            box = _card_box(d[4])
            seen += 1
            assert all(not SH._meets(box, b) for b in ink), (d[0], box, ink)
            assert SH.compiler().mask_is_clear(boxes, box) or not boxes.get("data_mask"), (d[0], box)
    assert seen >= 4, "the Tokyo bed docks five cards on its pages"


def test_two_cards_live_at_one_instant_never_share_a_box(tokyo):
    """The third pass: the record and the plant both read at the stage's centre on 0:56 - one box,
    two cards, and both over the page's sub. A card takes the first room no card beside it holds."""
    _, rows, _ = tokyo
    for r in rows:
        placed = [d for d in r[4] or [] if SH.placed(d[4])]
        for i, a in enumerate(placed):
            for b in placed[i + 1:]:
                if float(b[2]) >= float(a[3]) or float(a[2]) >= float(b[3]):
                    continue                          # never on screen together
                assert not SH._meets(_card_box(a[4]), _card_box(b[4])), (a[0], b[0])


def test_a_card_the_plan_placed_itself_is_kept_verbatim():
    """E99 s66: the plan is the intelligence. A move that names its own `centre_*` is not re-placed."""
    place = {"centre": True, "centre_w": 0.42, "centre_x": 0.76, "centre_y": 0.316}
    docks = [["dock-x", 0, 1.0, 9.0, dict(place)]]
    notes: list = []
    out = SH.place_cards(docks, {"schema_version": "ledger_page.v1", "surface": "page"}, "9:16", notes)
    assert out[0][4] == place and not notes


def test_a_card_leaves_when_the_chart_is_redrawn_under_it(tokyo):
    """E65: the room is the page's empty room AS THE PAGE STANDS. The panel card was parked in it at
    0:09 and read over the RESCALED line from 0:22 - nine of M25's twenty-nine faults."""
    _, rows, why = tokyo
    panel = next(d for d in rows[0][4] if d[0] == "dock-c-blue-ties-panel")
    rescale = next(s["at"] for s in rows[0][6] if s["kind"] == "chart_to")
    assert float(panel[3]) == pytest.approx(rescale), (panel, rescale)
    assert "leaves at the chart's state change" in why[0]["rule"]


# ---------------------------------------------------------------- the row grammar
def test_the_rows_round_trip_through_the_kit(tmp_path, tokyo):
    """The rows are the kit's own tuples: what `write_shot_table` takes and `load_rows` reads back."""
    _, rows, _ = tokyo
    path = T.write_shot_table(tmp_path / "SHOT-TABLE-SHORT.py", rows, '"""a base."""\n')
    back = T.load_rows(path)
    assert len(back) == len(rows)
    for a, b in zip(rows, back):
        assert tuple(a) == tuple(b)
    assert all(isinstance(r, tuple) and len(r) == 7 for r in back)


def test_a_second_compile_is_byte_identical(tokyo):
    """Acceptance 1: re-running on the same plan changes nothing - no clock, no set ordering, no
    dict iteration leaks into the output."""
    plan, rows, why = tokyo
    rows2, why2 = SH.compile(plan, _words(TOKYO), SH.DEFAULTS, "9:16", pages=_pages(TOKYO))
    assert repr(rows2) == repr(rows) and repr(SH.rows_why(why2)) == repr(why)


def test_every_row_carries_one_why_record(tokyo):
    _, rows, why = tokyo
    assert len(why) == len(rows)
    for w in why:
        assert sorted(w) == ["act", "beat", "rule", "signature", "skeleton"]
        assert w["rule"] and w["skeleton"] and isinstance(w["beat"], int)
        assert w["signature"] in ("axes", "mount", "spiral", "suck", "cut", "dip", "card", "hold")


# ---------------------------------------------------------------- the variety rule and the chooser
def test_no_two_rows_running_use_the_same_skeleton(tokyo, japan):
    """The variety rule, counted on SKELETON IDS (P66 T2: the approved cuts carry consecutive
    signature WORDS - Japan's throw -> snap pair reads card, card - so the word cannot be the rule)."""
    for _, _, why in (tokyo, japan):
        ids = [w["skeleton"] for w in why]
        assert all(a != b for a, b in zip(ids, ids[1:])), ids


def test_choose_refuses_the_previous_skeleton_and_falls_back_in_the_documented_order():
    lib = SH.load_library()
    beat = {"shape": SH.SHAPE_PLATE, "act": "NAMES a flow", "docks": ["dock-a", "dock-b"]}
    first, rung = SH.choose(beat, [], lib)
    assert rung == "rung 1" and first["shape"] == SH.SHAPE_PLATE
    second, _ = SH.choose(beat, [first["id"]], lib)
    assert second["id"] != first["id"] and second["shape"] == SH.SHAPE_PLATE
    # rung 2: no skeleton of the shape carries this act, so the ACT filter is dropped
    _, rung2 = SH.choose({**beat, "act": "RETRACTS the announcement"}, [], lib)
    assert rung2 in ("rung 1", "rung 2")
    # rung 3: the plan names no dock, so a skeleton that needs one is not fillable
    third, rung3 = SH.choose({**beat, "docks": []}, [], lib)
    assert rung3 == "rung 3"
    # rung 4: the shape has one skeleton and it was the last one used - the shape outranks variety
    one = [s for s in lib if s["id"] == first["id"]]
    again, rung4 = SH.choose(beat, [first["id"]], one)
    assert again["id"] == first["id"] and rung4.startswith("rung 4")


def test_a_shape_with_no_skeleton_is_refused_by_name():
    with pytest.raises(SH.Refused) as e:
        SH.choose({"shape": "no-such-shape", "beat": 3}, [], SH.load_library())
    assert "no-such-shape" in str(e.value) and "beat 3" in str(e.value)


# ---------------------------------------------------------------- the positional rule
def test_a_plan_whose_sentences_play_none_of_the_acts_still_compiles():
    """Twelve of the Tokyo bed's twenty-five records carry `act: "none of the 11 - ..."`. Such a beat
    is never refused: it is chosen by its SHAPE and its POSITION - the first beat is the open, a beat
    the plan calls a return is the return, a beat whose world is a page is a page beat, the rest are
    narrative plates."""
    page = "ledger:ev-a-v1:line:12:right"
    plan = [_rec(1, 0.0, 3.0, "clip:hook.mp4", caps=["the hook's clip world"]),
            _rec(2, 3.0, 12.0, page, caps=["the page draws to datum 12"]),
            _rec(3, 12.0, 20.0, "plate-desk;idle=drift", caps=["a still life on the desk"]),
            _rec(4, 20.0, 30.0, page, caps=["the page RETURNS by the spiral, datum 12 lit"])]
    assert all(SH.acts_of(r) == set() for r in plan), "the fixture plays none of the twelve acts"
    rows, why = SH.compile(plan, None, SH.DEFAULTS, "9:16")
    why = SH.rows_why(why)
    assert len(rows) == 3, [r[2] for r in rows]                 # the hook is absorbed into the page it mounts
    assert "the open IS the chart" in why[0]["rule"] and rows[0][2].startswith("ledger:")
    assert not rows[1][2].startswith("ledger:") and "narrative plate" in why[1]["rule"]
    assert SH.entry_in(rows[2][2]) == "spiral" and why[2]["signature"] == "spiral"


def test_a_page_the_cut_has_never_shown_cannot_return():
    """A spiral unwinds a page from its OWN point: a beat that talks like a return over a page the
    viewer has never met is an ordinary page beat."""
    plan = [_rec(1, 0.0, 8.0, "ledger:ev-a-v1:line:12:right", caps=["the page draws to datum 12"]),
            _rec(2, 8.0, 20.0, "ledger:ev-b-v1:bars:3:right", caps=["the ring returns, datum 3 lit"])]
    rows, why = SH.compile(plan, None, SH.DEFAULTS, "9:16")
    why = SH.rows_why(why)
    assert SH.entry_in(rows[1][2]) != "spiral" and why[1]["signature"] != "spiral"


# ---------------------------------------------------------------- the refusals
@pytest.mark.parametrize("break_it, says", [
    (lambda p: p.__setitem__(1, _rec(3, 8.0, 16.0, "plate-desk")), "beat 2 has no record"),
    (lambda p: p[1].__setitem__("comparator", {"compared_to": "  "}), "beat 2 compares to nothing"),
    (lambda p: p[1].update({"recipe": None, "why_none": ""}), "beat 2 has no recipe and no why_none"),
    (lambda p: p[1].__setitem__("plate", None), "beat 2 names no plate"),
])
def test_a_plan_m41_would_fail_is_refused_by_name(break_it, says):
    """`Not Building`: a beat with no plan record is a refusal, not a slot. The compiler's INPUT is
    AUTHORED (E99 s66) and it never invents a beat (`gate_one_shot_floor` SRC_M41)."""
    plan = [_rec(1, 0.0, 8.0, "ledger:ev-a-v1:line:12:right", caps=["datum 12"]),
            _rec(2, 8.0, 16.0, "plate-desk;idle=drift")]
    break_it(plan)
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, None, SH.DEFAULTS, "9:16")
    assert "M41" in str(e.value) and says in str(e.value)


def test_an_empty_plan_is_refused():
    with pytest.raises(SH.Refused) as e:
        SH.compile([], None, SH.DEFAULTS, "9:16")
    assert "AUTHORED" in str(e.value)


def test_a_hole_the_plan_cannot_fill_is_refused_naming_the_beat_the_skeleton_and_the_hole():
    """The sentence POINTS - the plan's capabilities name a region - but names no datum index, and
    the page id carries no emphasize either. The compiler will not make one up."""
    plan = [_rec(1, 0.0, 9.0, "ledger:ev-a-v1:line:12:right", caps=["the page draws to datum 12"]),
            _rec(2, 9.0, 20.0, "ledger:ev-b-v1:bars:right", caps=["a spotlight on the region of the lower half"])]
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, None, SH.DEFAULTS, "9:16")
    said = str(e.value)
    assert "beat 2" in said and "{datum}" in said and "never invents" in said
    assert any(s["id"] in said for s in SH.load_library())


def test_a_sentence_that_points_at_nothing_gets_no_light_and_why_says_so():
    """Not a refusal - a light is simply not emitted where the sentence does not point (Apply 1)."""
    plan = [_rec(1, 0.0, 9.0, "ledger:ev-a-v1:line:12:right", caps=["the page draws to datum 12"]),
            _rec(2, 9.0, 20.0, "ledger:ev-b-v1:bars:right", caps=["the page is the world and nothing is claimed"])]
    rows, why = SH.compile(plan, None, SH.DEFAULTS, "9:16")
    why = SH.rows_why(why)
    assert not rows[1][6]
    assert "points at nothing" in why[1]["rule"]


# ---------------------------------------------------------------- the Japan plan, and the module's own rule
def test_the_japan_plan_compiles_and_round_trips(tmp_path, japan):
    """ONLY that it compiles and round trips - these are NOT the approved Japan cut's rows."""
    _, rows, why = japan
    assert rows and len(why) == len(rows)
    back = T.load_rows(T.write_shot_table(tmp_path / "SHOT-TABLE-SHORT.py", rows, '"""a base."""\n'))
    assert [tuple(r) for r in back] == [tuple(r) for r in rows]


def test_m16_is_measured_and_never_filled():
    """`event_gaps` READS the pulse for the author; nothing in this module adds an event to close a
    gap, because a compiler that fills to a rate is an allocator (`recipes.py:1-20`)."""
    rows = [(0.0, 12.0, "plate-a", (0, 0, 0), [], "cut", [{"kind": "spotlight", "at": 1.0}])]
    assert SH.event_gaps(rows) == [(1.0, 11.0)]
    assert not [n for n in dir(SH) if "fill_to" in n or "densify" in n]


def test_the_module_names_no_episode():
    """The kit's own rule (`authoring/__init__.py:12-15`): no episode id, no crop, no quote, no file
    name, no absolute path - every episode fact arrives as an argument."""
    text = (ROOT / "content/video_engine/scripts/authoring/shapes.py").read_text(encoding="utf-8").lower()
    hits = [f"{i}: {bad!r}" for i, line in enumerate(text.splitlines(), start=1)
            for bad in ("tokyo", "tariff", "snipe", "c:/", "c:\\") if bad in line]
    assert not hits, "an episode fact leaked into the kit:\n" + "\n".join(hits)


# ---------------------------------------------------------------- the beat's named moves (P66 T3b)
def _moved_plan():
    """Two beats on one page: the second NAMES what it does, and the first says nothing at all."""
    page = "ledger:ev-a-v1:line:12:right"
    moves = [{"kind": "spotlight", "at_word": "one hundred", "dur": 1.0,
              "target": {"kind": "datum", "index": 12}},
             {"kind": "figure", "at_word": "billion", "dur": 1.2, "label": "$122.6B",
              "target": {"kind": "datum", "index": 12}, "options": {"dy": -0.9, "color": "neg"}}]
    return [_rec(1, 0.0, 10.0, page, sentence="The page draws its line to the January print.",
                 caps=["the page draws to datum 12"]),
            _rec(2, 10.0, 20.0, page, sentence="It sold one hundred and twenty two billion.",
                 caps=["datum 12"], moves=moves)]


def test_a_beats_named_moves_land_on_their_own_words_with_their_own_targets():
    """The plan is the intelligence (E99 s66): the sentence says what it does, and the compiler puts
    it on the row at the WORD it belongs to - the take is the clock, never a stopwatch."""
    plan = _moved_plan()
    ws = _take(plan)
    rows, why = SH.compile(plan, ws, SH.DEFAULTS, "9:16")
    assert len(rows) == 1, [r[2] for r in rows]
    norm = SH._norm_words(ws)
    spot = [e for e in rows[0][6] if e["kind"] == "spotlight"
            and e["at"] == SH.word_at(norm, "one hundred", 10.0, 20.0)]
    assert len(spot) == 1 and spot[0]["target"] == {"kind": "datum", "index": 12} and spot[0]["dur"] == 1.0
    figures = [e for e in rows[0][6] if e["kind"] == "figure"]
    assert len(figures) == 1
    # `label` is written into the field THAT KIND carries its words in - a figure's is `text` - and
    # `options` are the species' own remaining fields, copied and never translated
    assert figures[0]["text"] == "$122.6B" and figures[0]["dy"] == -0.9 and figures[0]["color"] == "neg"
    assert figures[0]["at"] == SH.word_at(norm, "billion", 10.0, 20.0)
    assert spot[0]["at"] < figures[0]["at"]


def test_a_phrase_that_is_not_in_the_beats_sentence_is_refused_by_name():
    """A move belongs to the sentence it punctuates. The compiler will not go hunting for the word
    elsewhere in the take, and it names the beat and the phrase."""
    plan = _moved_plan()
    plan[1]["moves"][0]["at_word"] = "the metronome"
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    said = str(e.value)
    assert "beat 2" in said and "the metronome" in said and "own sentence" in said


def test_a_light_asked_for_before_the_page_has_built_is_refused_and_never_moved():
    """E99 s67 Apply 1-2: a light is punctuation, not a cover for the build. The move is the
    AUTHOR's, so the compiler refuses it by name rather than quietly re-timing the beat."""
    plan = [_rec(1, 0.0, 12.0, "ledger:ev-a-v1:line:12:right",
                 sentence="The line lands on the January print.", caps=["datum 12"],
                 moves=[{"kind": "spotlight", "at_word": "The line", "dur": 1.0,
                         "target": {"kind": "datum", "index": 12}}])]
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    said = str(e.value)
    assert "beat 1" in said and "before this page" in said and "Apply 1-2" in said
    assert "rather than move the author" in said


def test_a_dock_move_lands_on_its_word_and_parks_in_the_pages_own_room():
    """E65 / `card_in_page_room`: the card reads on its word, then parks in the page's own room and
    holds to the row's end. Its lane and its options are the defaults when the plan names none."""
    page = "ledger:ev-a-v1:line:12:right"
    plan = [_rec(1, 0.0, 12.0, page, sentence="The page draws its line to the print.",
                 caps=["the page draws to datum 12"]),
            _rec(2, 12.0, 24.0, page, sentence="The record itself says so.", caps=["datum 12"],
                 moves=[{"kind": "dock", "at_word": "The record", "asset": "dock-k-pledge"}])]
    ws = _take(plan)
    rows, why = SH.compile(plan, ws, SH.DEFAULTS, "9:16")
    mine = [d for d in rows[0][4] if d[0] == "dock-k-pledge"]
    assert len(mine) == 1, rows[0][4]
    asset, lane, t_in, t_out, options = mine[0]
    assert lane == SH.DOCK_LANE and options == {}
    assert t_in == SH.word_at(SH._norm_words(ws), "The record", 12.0, 24.0)
    assert t_out == rows[0][1]


def test_every_beat_the_plan_leaves_silent_is_named_in_why():
    """E99 s68 - the base the agent MODIFIES: a beat the plan names no move for contributes nothing,
    and says so, so the agent reads where the base is a base and not a cut."""
    plan = _moved_plan()
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    silent = SH.silent_why(why)
    assert [w["beat"] for w in silent] == [1]
    assert sorted(silent[0]) == ["beat", "note", "sentence", "silent"]
    assert silent[0]["sentence"] == plan[0]["sentence"]
    assert "the author's to add or to leave" in silent[0]["note"]
    assert len(SH.rows_why(why)) == len(rows)


def test_a_move_kind_and_a_cards_options_are_the_compilers_own_vocabulary():
    """Never re-typed here: a move that is legal in the kit is legal in the compiler."""
    import build_scene_timeline_f as C
    assert set(SH.move_kinds()) == set(C.SPECIES_KINDS) | {SH.MOVE_DOCK}
    assert set(SH.dock_option_keys()) == set(C.DOCK_OPTS) | {SH.MOVE_SLOT}
    bad = [_rec(1, 0.0, 12.0, "plate-desk;idle=drift",
                moves=[{"kind": "glitter", "at_word": "A sentence"}])]
    with pytest.raises(SH.Refused) as e:
        SH.compile(bad, _take(bad), SH.DEFAULTS, "9:16")
    assert "beat 1" in str(e.value) and "glitter" in str(e.value)
    worse = [_rec(1, 0.0, 12.0, "plate-desk;idle=drift",
                  moves=[{"kind": "dock", "at_word": "A sentence", "asset": "dock-x",
                          "options": {"place": {"x": 1}}}])]
    with pytest.raises(SH.Refused) as e:
        SH.compile(worse, _take(worse), SH.DEFAULTS, "9:16")
    assert "beat 1" in str(e.value) and "place" in str(e.value)


def test_the_tokyo_beds_own_moves_close_the_base(tokyo):
    """The finding T3b answers (the parent, 2026-09-17): ONE skeleton row per authored group left
    the eleven-beat opening group with one event, and `event_gaps` read up to 32 s. The lever is the
    PLAN - the moves the approved cut actually carries - and never a looser gate. The ceiling here
    is a ceiling on the BASE, not M16's 2.5 s: the plan's density is the author's."""
    _, rows, _ = tokyo
    gaps = SH.event_gaps(rows)
    worst = max([g for _, g in gaps] or [0.0])
    assert worst < 10.0, gaps
    assert sum(len(r[6] or []) for r in rows) >= 20


def test_the_deriver_is_byte_stable_on_both_read_back_plans():
    """`derive_beat_moves.py --check` re-derives from the cut and exits 1 on drift: the plan and the
    approved cut it was read back from cannot quietly disagree."""
    import derive_beat_moves as D
    for build in (TOKYO, JAPAN):
        moves, skipped = D.derive(build)
        was, now = D.render(build, moves)
        assert was == now, f"{build.name}: the plan has drifted from its cut"
        assert D.main([str(build), "--check"]) == 0
        assert moves, "the approved cut carries species and cards, and the plan now names them"
