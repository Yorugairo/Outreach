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
# The rebuilt choreography vocabulary (E99 s70 Apply 2) - read from the schema, never typed twice
VOCABULARY = {w["const"] for w in json.loads(
    (ROOT / "content/video_engine/configs/shape_skeleton.schema.json").read_text(encoding="utf-8")
)["$defs"]["signature"]["oneOf"]}
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
def _first_page(rows):
    """The row the open's PAGE is on - rows[0] when the page is the first frame, rows[1] when it
    mounts over the hook's own world (the approved open's two rows)."""
    return next(i for i, r in enumerate(rows) if str(r[2]).startswith("ledger:"))


def test_the_open_is_the_chart(tokyo):
    """E99 s67 Apply 6: the open is the PAGE - on its axes from frame 0, or mounting over the hook's
    own world, which is what the Tokyo bed's clip hook asks for."""
    _, rows, why = tokyo
    p = _first_page(rows)
    assert rows[0][0] == 0.0
    assert SH.entry_in(rows[p][2]) in ("axes", "mount")
    assert why[p]["skeleton"] in ("open-on-the-chart-axes", "open-page-mounts-the-world")
    assert "the open IS the chart" in why[p]["rule"]
    # the Tokyo bed's hook is a clip, so the page MOUNTS over it - and `why` says exactly that
    assert SH.entry_in(rows[p][2]) == "mount" and "mounts the hook's world" in why[p]["rule"]


def test_the_open_keeps_the_hooks_world(tokyo):
    """THE FOURTH PASS, defect 1 (the parent, reading base v3 at 0.20 s beside the approved cut): the
    approved frame is the tea-break clip with the page mounting over it 2 s in; the base was BARE
    CREAM, because the compiler absorbed the hook's beats into the page that mounts over them. A
    mount with no world under it is a refusal - so the open is TWO rows, the hook's own world from
    frame 0 to the mount word and the page over it, exactly as the approved table writes the pair."""
    _, rows, why = tokyo
    world, page = rows[0], rows[1]
    assert not str(world[2]).startswith("ledger:") and world[0] == 0.0, world
    assert SH.world_of(world[2]) == "clip", "the Tokyo bed's hook is the counter clip"
    assert world[5] is None, "the mount IS the transition - the world under it carries no exit (E45)"
    assert page[0] == world[1] > 0.0 and "mount=" in page[2], (world, page)
    assert why[0]["signature"] == "hold" and "the hook's own world holds under the page" in why[0]["rule"]
    assert why[0]["group"] == why[1]["group"], "one group, two rows - the open's pair"
    # the mount lands on the hook's LAST sentence (the approved cut: `t_mount = at("left America")`)
    assert page[0] == pytest.approx(1.78, abs=0.01), page[0]


def test_a_mount_over_a_world_the_plan_names_is_always_two_rows():
    """The rule, on a synthetic plan: whatever skeleton the open takes, the world the hook is spoken
    over reaches the table. (Before the fourth pass the hook's beats were absorbed and the row began
    with the page.)"""
    page = "ledger:ev-a-v1:line:12:right"
    plan = [_rec(1, 0.0, 3.0, "plate-desk;idle=drift", caps=["the hook's plate world"]),
            _rec(2, 3.2, 6.0, "plate-desk;idle=drift", caps=["still the hook"]),
            _rec(3, 6.4, 20.0, page, caps=["the page draws to datum 12"])]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert [SH.world_of(r[2]) for r in rows] == ["plate", "page"], [r[2] for r in rows]
    assert rows[0][2].startswith("plate-desk") and rows[0][1] == pytest.approx(3.2), rows[0]
    assert rows[1][2].startswith("ledger:") and "mount=" in rows[1][2]
    assert SH.rows_why(why)[0]["signature"] == "hold"


def test_no_page_ever_arrives_built_and_the_clock_picks_the_entry(tokyo):
    """E99 s67 Apply 3: a page whose number lands 7 s or more after its entry mounts; every other
    page enters by its axes (a return by its spiral). `built` is never emitted.

    P66 T3b widened the list by ONE case and E99 s70 widened it to the rule it should always have
    been: a CONTINUITY entry the author wrote (`snap`, `camera`, `morph` - the entries that carry the
    world that was there into this one) STANDS. The clock chooses between a mount and an axes entry;
    it never overwrites the continuity transitions the operator said had been dropped."""
    _, rows, why = tokyo
    pages = [(r, w) for r, w in zip(rows, why) if r[2].startswith("ledger:")]
    assert pages, "the Tokyo bed is a page cut"
    for r, w in pages:
        entry = SH.entry_in(r[2])
        assert entry != "built" and ":built" not in r[2], r[2]
        assert entry in ("axes", "mount", "spiral") or entry in SH.CONTINUITY_ENTRIES, r[2]
        if entry in SH.CONTINUITY_ENTRIES:
            assert "the author's own" in w["rule"], w["rule"]
            continue
        if "the number lands at +" in w["rule"]:
            late = float(w["rule"].split("the number lands at +")[1].split("s")[0])
            assert (entry == "mount") == (late >= SH.MOUNT_AT_OR_AFTER_S), (late, r[2])
        if entry == "mount":
            assert "mount=" in r[2]


def test_the_return_comes_back_by_the_spiral(tokyo):
    """The bed's page has been on screen, and the beat plan says it returns.

    The SPIRAL is the entry (the clock's, enforced by construction). The row's SIGNATURE is the
    skeleton's, and since E99 s70 a skeleton whose signature is a mechanism the PLAN itself names -
    the recast, the park, the melt - is preferred on that beat (rung 0), so the signature word may
    be the transform the page plays rather than the arrival it made. Both are the return's.
    """
    _, rows, why = tokyo
    spirals = [(r, w) for r, w in zip(rows, why) if SH.entry_in(r[2] or "") == "spiral"]
    assert spirals, "the bed carries a return"
    for r, w in spirals:
        assert "returns" in w["rule"]
        assert w["signature"] in ("spiral",) or "rung 0" in w["rule"], w["rule"]


def test_the_exits_are_the_approved_ones(tokyo):
    """E47: the dip when the WORLD changes; page to page a suck or a cut, and never into a mount."""
    _, rows, why = tokyo
    for i, r in enumerate(rows):
        exit_, nxt = r[5], rows[i + 1] if i + 1 < len(rows) else None
        if nxt is None:
            assert exit_ == "cut"
            continue
        if exit_ is None:
            # the world a page MOUNTS over hands over by the mount itself (E45), so it carries none
            assert "mount=" in nxt[2] and i == 0, (i, r[2], nxt[2])
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
    _, rows, why = tokyo
    for n, r in enumerate(rows):
        if r[2].startswith("ledger:"):
            continue
        if r[5] is None:
            # the hook's own world under the page that mounts over it: both approved opens hold it
            # for about two seconds and mount on the hook's last sentence, and the row's `why` says
            # M44 reads it - the author's answer is a longer hook, never a later mount
            assert "under M44's six seconds" in why[n]["rule"], why[n]["rule"]
            continue
        assert round(r[1] - r[0], 2) >= SH.PLATE_MIN_S, r


def test_portrait_emits_no_rail(tokyo, japan):
    """R26-171: at 9:16 no `badges` rail leaves the compiler. (R26-172, which stood beside it - no
    `chart_to park` at 9:16 - is WITHDRAWN: see the park's own pin below.)"""
    for _, rows, _ in (tokyo, japan):
        for r in rows:
            assert all("badges" not in (d[4] or {}) for d in r[4] or [])
        assert "badges" not in repr(rows)


def test_the_parks_the_plan_names_are_emitted_in_portrait(tokyo):
    """THE FOURTH PASS, defect 3 (the parent, at 56.72 / 57.52 s): the APPROVED PORTRAIT cut parks its
    page small at the top and the clipping and the wafer card take the room below; base v3 left the
    page full size and dropped both cards over its ink, because R26-172 stripped every park at 9:16.
    The ruling is WITHDRAWN and the three parks the Tokyo plan names (beats 10, 16 and 17 - the park
    for the fingers, the park for the record and the fab, the UN-PARK as they leave) are on the base."""
    plan, rows, _ = tokyo
    named = [(b["beat"], m["options"]["scale"]) for b in plan for m in SH.moves_of(b)
             if m.get("kind") == "chart_to" and (m.get("options") or {}).get("to") == "park"]
    assert [n for n, _ in named] == [10, 16, 17], named
    made = [(float(s["at"]), float(s["scale"])) for r in rows for s in r[6] or []
            if s.get("kind") == "chart_to" and s.get("to") == "park"]
    assert len(made) == len(named), (made, named)
    assert [s for _, s in made] == [s for _, s in named]
    assert SH.UNPARK_SCALE in [s for _, s in made], "the un-park is the park to 1.0 (CAPABILITIES.md:120)"


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
    for plan, rows, why in (tokyo, japan):
        gs = SH.groups(plan)
        for r, w in zip(rows, why):
            g = gs[w["group"]]              # one group may play TWO rows (the open's world and page)
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
    first = rows[_first_page(rows)]
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
    p = _first_page(rows)
    land = rows[p][0] + _land(rows[p][2])
    build = next(s for s in rows[p][6] if s["kind"] == "build_to")
    assert abs(build["at"] + build["dur"] - land) <= 1e-6, build
    # ... which is the annotation M11 counts: the line ends ON the datum as the page lands (P47 T2)
    assert _is_page_build(build, rows[p]), (build, rows[p][2])


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
    for n, r in enumerate(rows):
        page = _page(TOKYO, r[2])
        if page is None:
            continue
        for d in r[4] or []:
            if not SH.placed(d[4]):
                # the one card that keeps its own throw is the card the NEXT page grows out of
                assert not d[4].get("centre") or d[4].get("arrive") == "throw", d
                continue
            # the room is the page AS IT STANDS when the card lands: under a park, the band the park
            # freed (the approved cut's own answer at 56.7 s - E65 + the park, R26-172 withdrawn)
            park = SH.park_scale_at(r[6] or [], float(d[2]))
            ink = SH.page_ink(page, "9:16", park)
            boxes = SH.parked_boxes(SH.pager().page_boxes(page, "9:16"), park)
            box = _card_box(d[4])
            seen += 1
            assert all(not SH._meets(box, b) for b in ink), (d[0], box, ink)
            assert SH.compiler().mask_is_clear(boxes, box) or not boxes.get("data_mask"), (d[0], box)
    assert seen >= 4, "the Tokyo bed docks five cards on its pages"


def test_a_card_with_no_room_parks_the_page_to_make_one():
    """THE FOURTH PASS, defect 3, the other half: when the page has no room of its own, the card is
    not dropped over its ink and does not fall back to the stage's centre - THE PAGE PARKS, the card
    takes the band the park frees, and the page UN-PARKS when the card leaves. The approved cut's own
    move (`page-parks-to-make-room-for-the-card` / `page-unparks-and-retakes-the-stage`)."""
    page = {"schema_version": "ledger_page.v1", "surface": "page", "builder": "story", "variant": "bars",
            "title": "A page with no room", "sub": "every cell of its plot carries ink",
            "source": "a fixture", "quiet_zone": "right",
            "labels": ["a", "b", "c", "d"], "values": [-47.7, 18.3, -66.8, -26.4],
            "colors": ["crimson", "teal", "crimson", "crimson"], "unit": "$"}
    boxes = SH.pager().page_boxes(page, "9:16")
    full = ["1" * len(boxes["data_mask"])] * len(boxes["data_mask"]) if boxes.get("data_mask") else None
    if full:
        page = {**page, "data_mask": full}
    docks, species, notes = [["dock-x", 0, 10.0, 16.0, {"centre": True}]], [], []
    out = SH.place_cards(docks, page, "9:16", notes, species, 30.0, SH.DEFAULTS)
    parks = [s for s in species if s.get("kind") == "chart_to" and s.get("to") == "park"]
    assert [s["to"] for s in parks] == ["park", "park"], species
    assert parks[0]["at"] == pytest.approx(10.0 - SH.PARK_LEAD_S) and parks[0]["scale"] < 1.0
    assert parks[1]["at"] == pytest.approx(16.0 + SH.UNPARK_LAG_S) and parks[1]["scale"] == SH.UNPARK_SCALE
    assert SH.placed(out[0][4]), "the card took the room the park made"
    assert any("PARKS" in n for n in notes) and any("UN-PARKS" in n for n in notes)


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
    p = _first_page(rows)
    panel = next(d for d in rows[p][4] if d[0] == "dock-c-blue-ties-panel")
    rescale = next(s["at"] for s in rows[p][6] if s["kind"] == "chart_to")
    assert float(panel[3]) == pytest.approx(rescale), (panel, rescale)
    assert "leaves at the chart's state change" in why[p]["rule"]


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
        assert sorted(w) == ["act", "beat", "group", "rule", "signature", "skeleton"]
        assert w["rule"] and w["skeleton"] and isinstance(w["beat"], int)
        assert w["signature"] in VOCABULARY, w["signature"]


# ---------------------------------------------------------------- the variety rule and the chooser
def test_no_two_rows_running_use_the_same_skeleton(tokyo, japan):
    """The variety rule, counted on SKELETON IDS (P66 T2: the approved cuts carry consecutive
    signature WORDS - Japan's throw -> snap pair reads card, card - so the word cannot be the rule)."""
    for _, _, why in (tokyo, japan):
        # one per GROUP: the open's two rows (the hook's world and the page over it) are one choice
        ids = [w["skeleton"] for i, w in enumerate(why) if not i or w["group"] != why[i - 1]["group"]]
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
    # the plan names no dock, so a skeleton that NEEDS one is not fillable - whichever rung answers,
    # the skeleton that comes back never asks for a card the plan does not have (E99 s70 widened the
    # library, so a dockless skeleton of this shape now answers on rung 1 where it once fell to 3)
    third, rung3 = SH.choose({**beat, "docks": []}, [], lib)
    assert rung3.startswith("rung")
    assert "{dock}" not in str(third["rows"])
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
    assert len(rows) == 4, [r[2] for r in rows]                 # the hook's world, then the page that mounts over it
    assert rows[0][2].startswith("clip:") and why[0]["signature"] == "hold"
    assert "the open IS the chart" in why[1]["rule"] and rows[1][2].startswith("ledger:")
    assert not rows[2][2].startswith("ledger:") and "narrative plate" in why[2]["rule"]
    assert SH.entry_in(rows[3][2]) == "spiral" and why[3]["signature"] == "spiral"


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
    assert sorted(silent[0]) == ["beat", "lights_only", "note", "sentence", "silent"]
    assert silent[0]["sentence"] == plan[0]["sentence"]
    assert silent[0]["lights_only"] is False
    assert "the author's to add or to leave" in silent[0]["note"]
    assert len(SH.rows_why(why)) == len(rows)


def test_a_beat_that_carries_only_a_light_is_SILENT():
    """E99 s71 (the operator, 2026-09-17): *a spotlight is never the move.* When a sentence names a
    thing, the THING ARRIVES - a badge or pill springing with its callout, a stamped prop or icon, a
    docked screenshot, a flight. A beat whose whole plan is one light is a hole in the base and the
    `why` says so, with the act and where the move it wants is written down."""
    plan = [_rec(1, 0.0, 12.0, "ledger:ev-a-v1:line:3:right:axes:cut",
                 sentence="The print that matters is the one they filed in February.", act="QUOTES a number",
                 caps=["spotlight on datum 3"],
                 moves=[{"kind": "spotlight", "at_word": "February", "target": {"kind": "datum", "index": 3},
                         "dur": 1.2}]),
            _rec(2, 12.5, 24.0, "plate-desk;idle=drift", sentence="And the desk it landed on.")]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    silent = {w["beat"]: w for w in SH.silent_why(why)}
    assert set(silent) == {1, 2}, sorted(silent)
    assert silent[1]["lights_only"] is True and "spotlight" in silent[1]["note"]
    assert "a light is never the move" in silent[1]["note"]
    assert "SPECIES-BY-SENTENCE.md" in silent[1]["note"] and "QUOTES" in silent[1]["note"]
    assert silent[2]["lights_only"] is False
    # and the light itself is still emitted - the rule names the hole, it never drops the author's move
    assert any(sp["kind"] == "spotlight" for sp in (rows[0][6] or []))


# ---------------------------------------------------------------- the page's own CHAIN (E99 s70 Apply 3)

def _chained(state: str = "ev-b-v1:bars:3", **moves):
    plate = f"ledger:ev-a-v1:line:3:right:axes:cut;then={state}" if state else "ledger:ev-a-v1:line:3:right:axes:cut"
    return [_rec(1, 0.0, 14.0, plate, sentence="The same data, month by month, is what it did.",
                 act="COMPARES two series", caps=["datum 3"], **moves),
            _rec(2, 14.5, 26.0, "plate-desk;idle=drift", sentence="And the desk it landed on.")]


def test_the_pages_then_chain_travels_onto_the_generated_row():
    """The bug E99 s70 names: `{page}` is the plate id with its `;options` tail stripped, so without
    `with_states` the base rebuilds the page WITHOUT the states its own chart_to moves travel to -
    and every transform renders nothing while the gates count the tokens and read PASS."""
    plan = _chained(moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4,
                            "options": {"to": "recast", "state": 1}}])
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert SH.states_of(rows[0][2]) == ["ev-b-v1:bars:3"], rows[0][2]
    assert any("`;then=` chain travels with it" in w["rule"] for w in SH.rows_why(why))
    assert [sp["to"] for sp in (rows[0][6] or []) if sp["kind"] == "chart_to"] == ["recast"]


def test_a_transform_that_would_render_nothing_is_refused_by_name():
    """E99 s70 Apply 3: never a silent no-op - the beat and the move are named."""
    plan = _chained(state="", moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4,
                                      "options": {"to": "recast", "state": 1}}])
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert "beat 1" in str(e.value) and "recast" in str(e.value)
    assert "declares 0 `;then=` state(s)" in str(e.value) and "redraw NOTHING" in str(e.value)


def test_a_transform_the_pages_form_does_not_admit_is_refused():
    """CAPABILITIES.md:118 - a morph hands one LINE's area to another's; a line -> bars pair is the recast."""
    plan = _chained(moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4,
                            "options": {"to": "morph", "state": 1}}])
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert "a morph hands ONE LINE's area" in str(e.value) and "'bars'" in str(e.value)


def test_a_rescale_with_no_domain_and_a_park_with_a_state_are_refused():
    for options, says in (({"to": "rescale"}, "names the target domain"),
                          ({"to": "park", "state": 1}, "`state` is not named on a park")):
        plan = _chained(moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4, "options": options}])
        with pytest.raises(SH.Refused) as e:
            SH.compile(plan, _take(plan), SH.DEFAULTS, "16:9")
        assert says in str(e.value), str(e.value)


def test_the_park_is_offered_in_both_aspects():
    """R26-172 WITHDRAWN (the parent, 2026-09-17, on the approved PORTRAIT cut's own 56.72 s frame):
    the park is how a page makes room for a card, in portrait as in landscape."""
    lib = SH.load_library()
    for aspect in ("9:16", "16:9"):
        assert {"park", "unpark"} <= {s["signature"] for s in SH.usable_library(lib, aspect)}


# ---------------------------------------------------------------- the thrown chart card (E99 s71)

def _thrown_card_plan(entry: str):
    """Three beats: the open on its chart, a plate the page's own CARD is thrown onto, and the page.

    Three and not two because the compiler's own open rule makes the hook and the page that mounts
    over it ONE row when the first beat's world is a plate - so the card's beat has to be the second.
    """
    return [_rec(1, 0.0, 10.0, "ledger:ev-open-v1:line:0:right:axes:cut", sentence="It opens on the chart."),
            _rec(2, 10.5, 20.0, "plate-desk;idle=drift", sentence="The desk it landed on.",
                 moves=[{"kind": "dock", "at_word": "desk", "asset": "dock-a-fed-rate",
                         "options": {"arrive": "throw", "mass": "paper"}}]),
            _rec(3, 20.5, 32.0, f"ledger:ev-fed-rate-v1:line:3:right:{entry}:cut",
                 sentence="And the rate it never moved.")]


def test_a_thrown_chart_card_that_nothing_takes_to_the_stage_is_refused():
    """E99 s71: a thrown full-page card ZOOMS or the camera PUSHES to it - it never floats over the
    world. The card is recognised without naming an episode: its name after the slot letter appears
    inside a ledger page id this same cut carries."""
    plan = _thrown_card_plan("axes")
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert "dock-a-fed-rate" in str(e.value) and "FULL CHART CARD" in str(e.value)
    assert ":snap=dock-a-fed-rate" in str(e.value) and ":camera=dock-a-fed-rate" in str(e.value)


def test_a_camera_entry_whose_card_no_row_carries_is_refused():
    """THE FOURTH PASS, defect 5 (the parent, at 77.80 s): the base played a blurred page and no card
    where the approved cut plays the Fed page with its ring. `camera=<dock>` is a read-back token and
    the compiler emitted it whatever the rows held, so the camera could push to a card nobody threw."""
    plan = _thrown_card_plan("camera=dock-a-fed-rate")
    plan[1]["moves"] = []                      # nobody throws the card the page arrives by
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert "arrives by `camera=dock-a-fed-rate`" in str(e.value), str(e.value)
    assert "no row carries" in str(e.value) and "never thrown" in str(e.value)


def test_a_camera_entry_carries_the_card_thrown_on_the_row_before(tokyo):
    """... and where the card IS thrown, the compiler keeps it: the card the next page grows out of
    takes no room of this page's (it is not evidence parked in a corner - it is the page to be), and
    the row it becomes STARTS WHEN THE CARD HAS BEEN READ, as the approved cut does (the card lands on
    "The Fed still" and the page arrives on "moved"). Base v3 started that row on the next beat, so
    the camera's 0.45 s arrival was still in flight at the instant the parent read."""
    _, rows, _ = tokyo
    page = rows[-1]
    head, _, card = str(SH.entry_token_in(page[2]) or "").partition("=")
    assert head == "camera" and card == "dock-h-fed-vs-yields", page[2]
    thrown = next(d for d in rows[-2][4] if str(d[0]) == card)
    assert not SH.placed(thrown[4]) and thrown[4].get("arrive") == "throw", thrown
    assert float(thrown[3]) >= float(page[0]) - 1e-6, "the card lives to the page's arrival"
    read_s = float(thrown[4].get("read_s") or SH.compiler().DOCK_READ_S)
    assert float(page[0]) == pytest.approx(float(thrown[2]) + read_s, abs=0.01), (page[0], thrown)
    # ... and the eye's arrival is over before the instant the parent read the base at
    assert float(page[0]) + SH.compiler().CAMERA_ARRIVAL_S < 77.8


def test_a_recast_arrives_building(tokyo):
    """THE FOURTH PASS, defect 2 (the parent, at 52.00 s): the approved recast grows its FIRST bar
    there; base v3 stood all four. E99 s67 Apply 2 - a chart never lands fully built - so a recast the
    author left un-keyed is emitted as the PLAIN hand-over the approved table writes (`keyed: false`,
    `build_scene_timeline_f.py:388`), and the arriving state draws on its own build envelope."""
    _, rows, why = tokyo
    casts = [(n, s) for n, r in enumerate(rows) for s in r[6] or []
             if s.get("kind") == "chart_to" and s.get("to") == "recast"]
    assert len(casts) == 2, casts
    for n, s in casts:
        assert s["keyed"] is False, s
        assert isinstance(s.get("dur"), (int, float)) and s["dur"] > 0, s
        assert "DRAWS ON ITS OWN BUILD ENVELOPE" in why[n]["rule"]


def test_a_recast_the_author_keys_keeps_its_key():
    """E64 stands where the AUTHOR asks for it: a keyed recast is the same data travelling, and the
    compiler never overwrites the key the plan names."""
    plan = _chained(moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4,
                            "options": {"to": "recast", "state": 1, "keyed": True}}])
    rows, _ = SH.compile(plan, _take(plan), SH.DEFAULTS, "16:9")
    cast = next(s for r in rows for s in r[6] or [] if s.get("kind") == "chart_to")
    assert cast["keyed"] is True, cast


def test_the_carried_retitle_reaches_the_returning_page(tokyo):
    """THE FOURTH PASS, defect 4 (the parent, at 50.30 s): the approved page reads "The opponent: a
    balance sheet" and the base still read the first title, because the deriver skipped the cut's
    CARRIED retitle - fired three seconds before its own scene, so the page ARRIVES retitled. The plan
    now names it on that scene's first word and the compiler realises it there."""
    plan, rows, _ = tokyo
    carried = [m for b in plan for m in SH.moves_of(b)
               if m.get("kind") == "retitle" and m.get("label") == "The opponent: a balance sheet"]
    assert len(carried) == 2, "the title is rewritten once on the page and carried onto its return"
    spiral = next(r for r in rows if SH.entry_in(r[2]) == "spiral")
    titles = [s for s in spiral[6] or [] if s.get("kind") == "retitle"]
    assert titles and titles[0]["text"] == "The opponent: a balance sheet", titles
    assert float(titles[0]["at"]) < 50.3, "the page reads the retitle by the instant the parent read"


def test_the_same_card_is_fine_once_the_page_snaps_up_out_of_it():
    plan = _thrown_card_plan("snap=dock-a-fed-rate")
    rows, _ = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert SH.entry_in(rows[-1][2]) == "snap", rows[-1][2]


def test_an_evidence_still_may_be_thrown_and_left_to_read():
    """E99 s67 Apply 5's other half: a DOCK is an evidence still, and a still is not a chart page."""
    plan = _thrown_card_plan("axes")
    plan[1]["moves"][0]["asset"] = "dock-c-blue-ties-panel"
    rows, _ = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert [str(d[0]) for d in rows[1][4]] == ["dock-c-blue-ties-panel"]


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
