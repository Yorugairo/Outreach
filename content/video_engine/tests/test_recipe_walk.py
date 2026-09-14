"""P56 T4: the walk and the co-occurrence matcher - on synthetic timelines, then on the cuts on disk.

The synthetic pins: a 3-member recipe fires twice and not three times; the ORDER is required (the same members in
the other order never fire); the window bounds a fire; an `optional` member may be absent and holds None. The real
pins re-derive T2's own numbers (`docs/research/runs/p56-recipe-seeds/seeds.jsonl`) from the timelines on disk:
Steel's badge ladder at 50.40 (seed R1) and Japan's card-becomes-the-chart (seed R6), plus the field reads T2
reported - 43 dock enters and 81 badges in Steel, 6 dock enters in Japan, and `exit: wipe_right` on 32 Steel scenes
resolving to the card `exit:wipe` with the option `wipe_right`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import recipe_walk as RW  # noqa: E402

PROJECTS = "content/video_engine/projects/systems-and-blowups"
STEEL = f"{PROJECTS}/steel-and-paper/build-f/steel-and-paper.timeline.json"
JAPAN = f"{PROJECTS}/japan-tariff-trick/build-short/japan-short.timeline.json"
SEEDS = "docs/research/runs/p56-recipe-seeds/seeds.jsonl"


def member(card: str, offset, **over) -> dict:
    return {"card": card, "offset_s": offset, "role": "a member of the test recipe", **over}


def scene(scene_id: str, span: list, species: list | None = None, **over) -> dict:
    base = {"scene_id": scene_id, "span": span, "world": {"asset_id": "plate-x"}, "exit": "cut",
            "species": species or [], "docks": []}
    return {**base, **over}


def timeline(scenes: list[dict], evidence: dict | None = None) -> dict:
    return {"schema_version": "scene_evidence_timeline.v1", "scenes": scenes, "evidence": evidence or {}}


LADDER = [member("species:trace", 0.0), member("species:callout", 0.5), member("species:punch", 1.0)]
TWICE = timeline([scene("s01", [0.0, 10.0], [
    {"kind": "trace", "at": 1.0}, {"kind": "callout", "at": 1.5}, {"kind": "punch", "at": 2.0},
    {"kind": "trace", "at": 5.0}, {"kind": "callout", "at": 5.5}, {"kind": "punch", "at": 6.0}])])


# --------------------------------------------------------------------------- synthetic

def test_a_three_member_recipe_fires_twice_and_names_both_instants():
    # Act
    fires = RW.match(RW.events(TWICE), LADDER, 6.0)

    # Assert
    assert [f.members_at for f in fires] == [[1.0, 1.5, 2.0], [5.0, 5.5, 6.0]]
    assert RW.count(RW.events(TWICE), LADDER, 6.0) == 2


def test_the_order_is_required_the_same_members_reversed_never_fire():
    # Arrange: the punch comes LAST in the cut, so a recipe that wants it first has no fire
    reversed_members = [member("species:punch", 0.0), member("species:callout", 0.5), member("species:trace", 1.0)]

    # Act / Assert
    assert RW.match(RW.events(TWICE), reversed_members, 6.0) == []


def test_the_window_bounds_a_fire():
    # Arrange: the punch sits 1.0 s after the trace
    members = [member("species:trace", 0.0), member("species:punch", 1.0)]

    # Act / Assert
    assert RW.count(RW.events(TWICE), members, 6.0) == 2
    assert RW.count(RW.events(TWICE), members, 0.5) == 0


def test_an_optional_member_may_be_absent_and_holds_none():
    # Arrange: the second scene plays the trace and the punch with no callout between them
    doc = timeline([scene("s01", [0.0, 10.0], [{"kind": "trace", "at": 1.0}, {"kind": "punch", "at": 2.0}])])
    members = [member("species:trace", 0.0), member("species:callout", 0.5, optional=True),
               member("species:punch", 1.0)]

    # Act
    fires = RW.match(RW.events(doc), members, 6.0)

    # Assert
    assert [f.members_at for f in fires] == [[1.0, None, 2.0]]
    assert [e is None for e in fires[0].events] == [False, True, False]


def test_a_required_member_that_never_fires_kills_the_chain():
    # Arrange
    doc = timeline([scene("s01", [0.0, 10.0], [{"kind": "trace", "at": 1.0}, {"kind": "punch", "at": 2.0}])])

    # Act / Assert
    assert RW.match(RW.events(doc), LADDER, 6.0) == []


def test_t0_keeps_only_the_fire_the_proof_claims():
    # Act
    fires = RW.match(RW.events(TWICE), LADDER, 6.0, t0=5.0)

    # Assert
    assert [f.members_at for f in fires] == [[5.0, 5.5, 6.0]]
    assert RW.match(RW.events(TWICE), LADDER, 6.0, t0=3.0) == []


def test_a_member_names_an_option_and_only_that_option_matches():
    # Arrange: two scenes, one leaving on a wipe_right, one on a plain cut
    doc = timeline([scene("s01", [0.0, 2.0], exit="wipe_right"), scene("s02", [2.0, 4.0], exit="cut")])
    options = {"wipe_right": "exit:wipe"}

    # Act
    evts = [e for e in RW.events(doc, options) if e.cls == "exit"]

    # Assert
    assert [(e.card, e.option) for e in evts] == [("exit:wipe", "wipe_right"), ("exit:cut", None)]


def test_the_walk_is_deterministic_and_orders_the_same_instant_by_what_the_viewer_meets_first():
    # Arrange: a dock and its badge, a species and the exit all inside one scene
    doc = timeline([scene("s01", [0.0, 6.0], [{"kind": "callout", "at": 3.0}],
                          docks=[{"slide": "ev-a", "enter": 0.0, "exit": 6.0, "badge_at": [2.0]}])],
                   {"ev-a": {"species": "chart", "chart": {"series": []}}})

    # Act
    first = [(e.t, e.cls, e.card) for e in RW.events(doc)]

    # Assert
    assert first == [(e.t, e.cls, e.card) for e in RW.events(doc)]
    assert first[:5] == [(0.0, "cut", None), (0.0, "world", RW.PLATE_CARD), (0.0, "dock_enter", "dock_kind:image"),
                         (0.0, "dock_enter", "dock_payload:chart"), (0.0, "dock_enter", "chart_dock:series")]
    assert first[5:] == [(2.0, "badge", RW.BADGE_CARD), (3.0, "species", "species:callout"),
                         (6.0, "dock_exit", None), (6.0, "exit", "exit:cut")]


# --------------------------------------------------------------------------- the cuts on disk

@pytest.fixture(scope="module")
def options() -> dict:
    records = [json.loads(line) for line in (ROOT / "docs/EFFECTS-CATALOG.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    return RW.option_owner(records)


@pytest.fixture(scope="module")
def seeds() -> dict:
    rows = [json.loads(line) for line in (ROOT / SEEDS).read_text(encoding="utf-8").splitlines() if line.strip()]
    return {row["seed"]: row for row in rows}


@pytest.fixture(scope="module")
def steel(options) -> list:
    return RW.events(RW.load_timeline(ROOT / STEEL), options)


@pytest.fixture(scope="module")
def japan(options) -> list:
    return RW.events(RW.load_timeline(ROOT / JAPAN), options)


def test_steels_field_reads_are_t2s(steel):
    # Assert: T2 counted 43 dock enters, 81 badges and 75 plate worlds with no species at all
    assert sum(1 for e in steel if e.cls == "dock_enter" and e.card.startswith("dock_kind:")) == 43
    assert sum(1 for e in steel if e.cls == "badge") == 81
    assert sum(1 for e in steel if e.cls == "world" and e.card == RW.PLATE_CARD) == 75
    assert [e for e in steel if e.cls in ("species", "page_species", "chart_to")] == []


def test_steels_wipe_right_is_the_wipe_cards_option_on_thirty_two_scenes(steel):
    # Act
    wipes = [e for e in steel if e.cls == "exit" and e.option == "wipe_right"]

    # Assert
    assert len(wipes) == 32
    assert {e.card for e in wipes} == {"exit:wipe"}


def test_japan_carries_six_dock_enters(japan):
    assert sum(1 for e in japan if e.cls == "dock_enter" and e.card.startswith("dock_kind:")) == 6


def test_the_badge_ladder_fires_at_fifty_forty_exactly_where_t2_says(steel, seeds):
    # Arrange: seed R1's members, with the badge card the walk gives a badge
    members = [member("dock_kind:image", 0.0), member(RW.BADGE_CARD, 2.05),
               member(RW.BADGE_CARD, 3.35, optional=True), member(RW.BADGE_CARD, 4.65, optional=True),
               member(RW.BADGE_CARD, 5.95, optional=True)]

    # Act
    fires = RW.match(steel, members, 6.0, t0=50.40)

    # Assert: the instants are seed R1's second instance, verbatim
    assert len(fires) == 1
    assert fires[0].members_at == [50.4, 52.45, 53.75, 55.05, 56.35]
    assert fires[0].members_at in seeds["R1"]["all_members_at"]
    assert fires[0].scene == "s05"


def test_the_card_becomes_the_chart_fires_at_its_throw(japan, seeds):
    # Arrange: seed R6 - the plate drifts, the card is thrown at 0.82, the world dips and the page snaps from it
    members = [member("idle:drift", 0.0), member("arrival:throw", [0.82, 4.12], option="paper"),
               member("exit:dip", [1.82, 5.12]), member("page_enter:snap", [1.82, 5.12])]

    # Act
    fires = RW.match(japan, members, 6.0, t0=0.0)

    # Assert
    assert [f.members_at for f in fires] == [[0.0, 0.82, 1.82, 1.82]]
    assert fires[0].members_at == seeds["R6"]["members_at"]
    assert RW.count(japan, members, 6.0) == seeds["R6"]["count"] == 2


def test_the_trace_callout_ladder_reproduces_t2s_count(japan, seeds):
    # Arrange: seed R7 - trace, callout, trace, callout, trace, callout
    members = [member("species:trace", 0.0), member("species:callout", 0.55), member("species:trace", 1.26),
               member("species:callout", 1.81), member("species:trace", 2.52), member("species:callout", 3.07)]

    # Act
    fires = RW.match(japan, members, 6.0)

    # Assert
    assert len(fires) == seeds["R7"]["count"] == 4
    assert fires[0].members_at == seeds["R7"]["members_at"]


# --------------------------------------------------------------------------- the P56 review (2026-09-13)

HELD_DOCK = [scene("s01", [0.0, 2.0], docks=[{"slide": "ev-a", "enter": 0.0, "exit": 10.0, "badge_at": [10.0]}]),
             scene("s02", [2.0, 12.0], [{"kind": "punch", "at": 9.0}], world={"asset_id": "plate-y"})]
LADDER_ACROSS = [member(RW.PLATE_CARD, 0.0), member(RW.BADGE_CARD, [9.0, 11.0]),
                 member("species:punch", [8.0, 10.0])]


def test_the_members_fire_in_time_order_not_the_walks_index_order():
    # Arrange: s01's badge is at 10.0 and s02's punch at 9.0 - later in the WALK, earlier on the clock
    evts = RW.events(timeline(HELD_DOCK, {"ev-a": {"species": "chart"}}))
    assert [(e.t, e.card) for e in evts if e.cls in ("badge", "species")] == [
        (10.0, RW.BADGE_CARD), (9.0, "species:punch")]

    # Act / Assert: a ladder may not climb backwards (it used to fire [0.0, 10.0, 9.0])
    assert RW.match(evts, LADDER_ACROSS, 12.0) == []


def test_the_same_ladder_fires_when_its_last_member_really_is_last():
    # Arrange: the punch moves to 10.5, after the badge
    doc = timeline([HELD_DOCK[0], scene("s02", [2.0, 12.0], [{"kind": "punch", "at": 10.5}],
                                       world={"asset_id": "plate-y"})], {"ev-a": {"species": "chart"}})

    # Act
    fires = RW.match(RW.events(doc), LADDER_ACROSS, 12.0)

    # Assert
    assert [f.members_at for f in fires] == [[0.0, 10.0, 10.5]]


CHILD = {"id": "recipe:test-child", "status": "proven", "window_s": 6.0,
         "members": [member("species:trace", 0.0), member("species:callout", 0.5)]}
PARENT = [member(RW.PLATE_CARD, 0.0), member("recipe:test-child", 1.0)]


def test_a_member_naming_a_recipe_fires_where_the_flattened_members_fire():
    # Arrange
    doc = timeline([scene("s01", [0.0, 10.0], [{"kind": "trace", "at": 1.0}, {"kind": "callout", "at": 1.5}])])
    evts = RW.events(doc)
    flat = [member(RW.PLATE_CARD, 0.0), member("species:trace", 1.0), member("species:callout", 1.5)]

    # Act
    fires = RW.match(evts, PARENT, 6.0, recipes={"recipe:test-child": CHILD})

    # Assert
    assert [f.members_at for f in fires] == [[0.0, 1.0, 1.5]]
    assert [f.members_at for f in fires] == [f.members_at for f in RW.match(evts, flat, 6.0)]
    assert RW.count(evts, PARENT, 6.0, recipes={"recipe:test-child": CHILD}) == 1
    assert RW.match(evts, PARENT, 6.0) == []       # with no registry no event can BE the recipe member


def test_a_range_offset_on_a_recipe_member_adds_to_both_ends():
    # Arrange
    child = {"id": "recipe:test-child",
             "members": [member("species:trace", 0.0), member("species:callout", [0.5, 1.0])]}

    # Act
    flat = RW.flatten([member(RW.PLATE_CARD, 0.0), member("recipe:test-child", [1.0, 2.0])],
                      {"recipe:test-child": child})

    # Assert
    assert [m["offset_s"] for m in flat] == [0.0, [1.0, 2.0], [1.5, 3.0]]


def test_a_timeline_with_only_spans_walks_to_a_cut_list_instead_of_raising():
    # Arrange: no scene_id, no world, no exit, a dock with no window, a species with no `at`, an item with no `at`
    doc = {"schema_version": "scene_evidence_timeline.v1",
           "scenes": [{"span": [0.0, 4.0]},
                      {"span": [4.0, 8.0], "docks": [{"slide": "ev-a"}], "species": [{"kind": "punch"}]}],
           "evidence": {"ev-a": {"stack": {"items": [{"label": "no instant"}]}}}}

    # Act
    evts = RW.events(doc)

    # Assert
    assert [e.t for e in evts if e.cls == "cut"] == [0.0]          # both scenes are the same (empty) plate world
    assert [(e.t, e.cls) for e in evts if e.cls in ("dock_enter", "dock_exit")] == [
        (4.0, "dock_enter"), (8.0, "dock_exit")]                   # the dock holds its scene
    assert [(e.t, e.card) for e in evts if e.cls == "species"] == [(4.0, "species:punch")]
    assert [e for e in evts if e.cls == "item"] == []              # a stack item with no instant is not an event
    assert {e.card for e in evts if e.cls == "exit"} == {"exit:wipe_left"}   # the timeline schema's own default
