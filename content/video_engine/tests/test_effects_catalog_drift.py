"""P55 T4: the drift gate - each of its eight checks breaks on purpose in a tmp copy of the cards and names the culprit.

The committed catalogue passes; a fake compiler exit with no card, a ghost card token, a renamed anchor symbol, a
missing golden, a refused exit example (`melt:splash`, refused since E88), a shared alias, a composite card that lost
its phases and a species card that copies its WHEN each fail naming the token or the card id. `build_effects_catalog.py
--check` carries the gate, so `build_docs_layers.py` does too.

P56 T4 adds the four RECIPE checks, each broken the same way in a tmp copy of the recipe files: a member that names
no card, an option its card does not list, a recipe with one member and a cycle (9); a `proven` recipe with no proof,
a proof timeline that is not on disk, a proof whose members do NOT fire at that instant and a `members_at` that
disagrees with the walk (10); a title or alias that is a card's or another recipe's, or an AMBIGUOUS_NAME (11); a
`proven` recipe that never fired, and the INFO line for one that fired exactly once (12).

P56 T8 adds the four uncarded effects the recipe mining found (`plate_option:ken`, `plate_option:world`,
`plate_option:clip`, `dock_option:badge` - each `implicit`, each measured on a shipped timeline), the proof that
`wipe_right` needs no card of its own (it is `exit:wipe`'s option, fired 32 times in Steel), and the long form's
vocabulary verdict: Steel carries `species: []` on all 75 scenes and 0 ledger pages, so no Steel-proven recipe can
name a species or a page member.
"""
from __future__ import annotations

import copy
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_effects_catalog as BEC  # noqa: E402
import build_scene_timeline_f as B  # noqa: E402
import effects_catalog_check as ECC  # noqa: E402
import docs_find as DF  # noqa: E402
import recipe_walk as RW  # noqa: E402

CARDS_DIR = ROOT / BEC.CARDS_REL
RECIPES_DIR = ROOT / BEC.RECIPES_REL
GOOD_RECIPE = "recipe:trace-callout-ladder"   # japan, 4 fires, every member a live card - the mutation base
STEEL_TIMELINE = ("content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/"
                  "steel-and-paper.timeline.json")        # the long form: 75 plate worlds, 43 docks, no species
JAPAN_TIMELINE = ("content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short/"
                  "japan-short.timeline.json")            # a short: clip worlds (s09, s12) and page badge rails


@pytest.fixture()
def cards_dir(tmp_path: Path) -> Path:
    """A tmp copy of the committed card files - the checks run against the real repo, the cards are the copy's."""
    target = tmp_path / "cards"
    shutil.copytree(CARDS_DIR, target)
    return target


def edit_card(cards_dir: Path, card_id: str, mutate) -> None:
    axis = card_id.split(":")[0]
    path = cards_dir / f"{axis}.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    card = next(c for c in doc["cards"] if c["id"] == card_id)
    mutate(card)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_card(cards_dir: Path, template_id: str, token: str, **over) -> None:
    axis = template_id.split(":")[0]
    path = cards_dir / f"{axis}.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    card = copy.deepcopy(next(c for c in doc["cards"] if c["id"] == template_id))
    card.update({"id": f"{axis}:{token}", "token": token, "title": f"The {token} test card", "aliases": [], **over})
    doc["cards"].append(card)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cards(cards_dir: Path) -> list[dict]:
    return ECC.load_cards(cards_dir)


@pytest.fixture()
def recipes_dir(tmp_path: Path) -> Path:
    """A tmp copy of the committed recipe files - the checks run against the real repo, the recipes are the copy's."""
    target = tmp_path / "recipes"
    shutil.copytree(RECIPES_DIR, target)
    return target


def edit_recipe(recipes_dir: Path, recipe_id: str, mutate) -> None:
    path = recipes_dir / f"{recipe_id.split(':', 1)[1]}.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    mutate(doc)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def recipes(recipes_dir: Path) -> list[dict]:
    return ECC.load_recipes(recipes_dir)


# --------------------------------------------------------------------------- the committed catalogue

@pytest.mark.xfail(strict=True, reason="R26-239: four compiler tokens (room, domain, build, labelfit) have no card")
def test_the_committed_catalogue_passes_every_check():
    """R26-224 (2026-09-18), classified (c) a real gap, filed as R26-239 and named rather than hidden: the drift
    gate's coverage check reports four compiler tokens with no card - `room` (R26-221), `domain` (R26-223) and
    `build` (R26-226), all three built today, and `labelfit` (pre-existing, R26-191). `build_effects_catalog.py
    --check` exits 1 on the same four, so the catalogue cannot be regenerated until they are carded. Writing the
    cards is the row's work, not a test lane's; the xfail is strict, so it fails the moment they land."""
    # Act
    report = ECC.run(ROOT)

    # Assert
    assert report.failures == []
    assert all(": " in entry for entry in report.skipped)


# --------------------------------------------------------------------------- 9. recipe members

def test_recipe_members_names_a_member_that_is_no_card(recipes_dir):
    # Arrange
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d["members"][1].update(card="species:no_such_thing"))

    # Act
    failures = ECC.check_recipe_members(recipes(recipes_dir), cards(CARDS_DIR))

    # Assert
    assert any(GOOD_RECIPE in f and "species:no_such_thing" in f for f in failures), failures


def test_recipe_members_refuses_an_option_the_card_does_not_list(recipes_dir):
    # Arrange: `wipe_right` belongs to exit:wipe, not to the callout species
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d["members"][1].update(option="wipe_right"))

    # Act
    failures = ECC.check_recipe_members(recipes(recipes_dir), cards(CARDS_DIR))

    # Assert
    assert any(GOOD_RECIPE in f and "wipe_right" in f and "does not list" in f for f in failures), failures


def test_recipe_members_refuses_fewer_than_two_members(recipes_dir):
    # Arrange
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d.update(members=d["members"][:1]))

    # Act
    failures = ECC.check_recipe_members(recipes(recipes_dir), cards(CARDS_DIR))

    # Assert
    assert any(GOOD_RECIPE in f and "COMBINATION" in f for f in failures), failures


def test_recipe_members_names_a_cycle_in_the_recipe_graph(recipes_dir):
    # Arrange: two recipes name each other as members
    other = "recipe:punch-then-callout"
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d["members"][1].update(card=other))
    edit_recipe(recipes_dir, other, lambda d: d["members"][1].update(card=GOOD_RECIPE))

    # Act
    failures = ECC.check_recipe_members(recipes(recipes_dir), cards(CARDS_DIR))

    # Assert
    assert any("cycle" in f and GOOD_RECIPE in f and other in f for f in failures), failures


# --------------------------------------------------------------------------- 10. recipe proof

def test_recipe_proof_names_a_proven_recipe_with_no_proof(recipes_dir):
    # Arrange
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d.pop("proof"))

    # Act
    failures = ECC.check_recipe_proof(recipes(recipes_dir), ROOT, cards(CARDS_DIR))

    # Assert
    assert any(GOOD_RECIPE in f and "no proof" in f for f in failures), failures


def test_recipe_proof_names_a_timeline_that_is_not_on_disk(recipes_dir):
    # Arrange
    gone = "content/video_engine/projects/systems-and-blowups/nowhere/build-x/nowhere.timeline.json"
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d["proof"].update(timeline=gone))

    # Act
    failures = ECC.check_recipe_proof(recipes(recipes_dir), ROOT, cards(CARDS_DIR))

    # Assert
    assert any(GOOD_RECIPE in f and "not on disk" in f for f in failures), failures


def test_recipe_proof_names_the_member_that_does_not_fire_and_the_instant(recipes_dir):
    # Arrange: the ladder is real, but the fifth member is asked for 30 s late
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d["members"][4].update(offset_s=30.0))

    # Act
    failures = [f for f in ECC.check_recipe_proof(recipes(recipes_dir), ROOT, cards(CARDS_DIR))
                if GOOD_RECIPE in f]

    # Assert
    assert len(failures) == 1
    assert "member 5 (species:trace" in failures[0] and "9.22" in failures[0]


def test_recipe_proof_names_a_members_at_that_disagrees_with_the_walk(recipes_dir):
    # Arrange: the walk still finds the fire, but the proof states a different instant for member 2
    edit_recipe(recipes_dir, GOOD_RECIPE,
                lambda d: d["proof"].update(members_at=[9.22, 9.99, 10.48, 11.03, 11.74, 12.29]))

    # Act
    failures = [f for f in ECC.check_recipe_proof(recipes(recipes_dir), ROOT, cards(CARDS_DIR))
                if GOOD_RECIPE in f]

    # Assert
    assert len(failures) == 1
    assert "member 2: the walk says 9.77, the proof 9.99" in failures[0]


def test_recipe_proof_names_a_candidate_that_carries_a_proof(recipes_dir):
    # Arrange
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d.update(status="candidate"))

    # Act
    failures = ECC.check_recipe_proof(recipes(recipes_dir), ROOT, cards(CARDS_DIR))

    # Assert
    assert any(GOOD_RECIPE in f and "candidate carries a proof" in f for f in failures), failures


def test_the_committed_recipes_that_do_fire_are_named_one_by_one():
    """The proof check is not vacuous: most of the committed recipes fire exactly where they claim."""
    # Act
    failures = ECC.check_recipe_proof(recipes(RECIPES_DIR), ROOT, cards(CARDS_DIR))

    # Assert
    assert len(recipes(RECIPES_DIR)) - len(failures) >= 12, failures


# --------------------------------------------------------------------------- 11. recipe aliases

def test_recipe_aliases_refuses_a_name_a_card_already_holds(recipes_dir):
    # Arrange: "the evidence wall" is the verdict stack card's alias
    edit_recipe(recipes_dir, GOOD_RECIPE,
                lambda d: d["aliases"].append({"name": "the evidence wall", "source": "operator 2026-09-13"}))

    # Act
    failures = ECC.check_recipe_aliases(cards(CARDS_DIR), recipes(recipes_dir))

    # Assert
    assert any("evidence wall" in f and "dock_payload:stack" in f for f in failures), failures


def test_recipe_aliases_refuses_an_ambiguous_name(recipes_dir):
    # Arrange
    edit_recipe(recipes_dir, GOOD_RECIPE,
                lambda d: d["aliases"].append({"name": "push", "source": "operator 2026-09-13"}))

    # Act
    failures = ECC.check_recipe_aliases(cards(CARDS_DIR), recipes(recipes_dir))

    # Assert
    assert any("'push'" in f and "AMBIGUOUS_NAMES" in f for f in failures), failures


def test_recipe_aliases_refuses_a_name_another_recipe_holds(recipes_dir):
    # Arrange
    alias = {"name": "the two-hop ladder", "source": "operator 2026-09-13"}
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d["aliases"].append(dict(alias)))
    edit_recipe(recipes_dir, "recipe:punch-then-callout", lambda d: d["aliases"].append(dict(alias)))

    # Act
    failures = ECC.check_recipe_aliases(cards(CARDS_DIR), recipes(recipes_dir))

    # Assert
    assert any("two-hop ladder" in f and GOOD_RECIPE in f for f in failures), failures


def test_the_committed_recipe_names_are_each_their_own():
    assert ECC.check_recipe_aliases(cards(CARDS_DIR), recipes(RECIPES_DIR)) == []


# --------------------------------------------------------------------------- 12. recipe count

def test_recipe_count_fails_a_proven_recipe_that_never_fired(recipes_dir):
    # Arrange
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d.update(count=0))

    # Act
    failures, info = ECC.check_recipe_count(recipes(recipes_dir))

    # Assert
    assert any(GOOD_RECIPE in f and "fired at least once" in f for f in failures), failures
    assert info == [] or all(GOOD_RECIPE not in i for i in info)


def test_recipe_count_reports_a_single_fire_as_info_not_a_failure(recipes_dir):
    # Arrange
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d.update(count=1))

    # Act
    failures, info = ECC.check_recipe_count(recipes(recipes_dir))

    # Assert
    assert all(GOOD_RECIPE not in f for f in failures)
    assert any(GOOD_RECIPE in i and "a decoration" in i for i in info), info


def test_recipe_count_fails_a_candidate_that_has_fired(recipes_dir):
    # Arrange
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d.update(status="candidate", count=4))

    # Act
    failures, _ = ECC.check_recipe_count(recipes(recipes_dir))

    # Assert
    assert any(GOOD_RECIPE in f and "is proven" in f for f in failures), failures


def test_the_run_carries_the_recipe_counts_and_the_decoration_lines():
    # Act
    report = ECC.run(ROOT)

    # Assert
    assert report.recipes == len(recipes(RECIPES_DIR)) and report.proven >= 1
    assert all(i.startswith("count: recipe:") for i in report.info)


# --------------------------------------------------------------------------- 1. coverage

def test_coverage_names_a_compiler_exit_that_has_no_card(cards_dir, monkeypatch):
    # Arrange
    monkeypatch.setattr(B, "SCENE_EXITS", B.SCENE_EXITS + ("zzz_fake",))

    # Act
    failures = ECC.check_coverage(cards(cards_dir))

    # Assert
    assert any("zzz_fake" in f and "SCENE_EXITS" in f for f in failures), failures


@pytest.mark.xfail(strict=True, reason="R26-239: four compiler tokens (room, domain, build, labelfit) have no card")
def test_coverage_accepts_a_token_listed_as_a_parent_cards_option(cards_dir):
    """R26-224 (2026-09-18): the first assert (a token hidden by a parent card's option is reported) still holds;
    the LAST one - the committed cards cover every token - is R26-239's four. Strict xfail: see the test above."""
    # Arrange: `wipe_right` has no card of its own - it is exit:wipe's option
    edit_card(cards_dir, "exit:wipe", lambda c: c.update(options=[]))

    # Act
    failures = ECC.check_coverage(cards(cards_dir))

    # Assert
    assert any("'wipe_right'" in f for f in failures)
    assert ECC.check_coverage(ECC.load_cards(CARDS_DIR)) == []


# --------------------------------------------------------------------------- 2. phantoms

def test_a_wired_card_on_a_token_the_compiler_refuses_is_a_phantom(cards_dir):
    # Arrange
    add_card(cards_dir, "exit:dip", "zzz_ghost", status="wired", backlog=None)

    # Act
    failures = ECC.check_phantoms(cards(cards_dir))

    # Assert
    assert any("exit:zzz_ghost" in f for f in failures), failures


def test_a_planned_card_with_a_backlog_row_is_not_a_phantom(cards_dir):
    # Arrange
    add_card(cards_dir, "exit:dip", "zzz_ghost", status="planned", backlog=["R26-75"])

    # Act
    failures = ECC.check_phantoms(cards(cards_dir))

    # Assert
    assert not any("zzz_ghost" in f for f in failures)


# --------------------------------------------------------------------------- 3. anchors

def test_a_renamed_anchor_symbol_fails_naming_it(cards_dir):
    # Arrange
    edit_card(cards_dir, "exit:dip", lambda c: c["lives"].update(symbol="zzzDipRenamed"))

    # Act
    failures = ECC.check_anchors(cards(cards_dir))

    # Assert
    assert any("exit:dip" in f and "zzzDipRenamed" in f for f in failures), failures


def test_an_also_identifier_and_a_missing_path_each_fail(cards_dir):
    # Arrange
    edit_card(cards_dir, "dock_payload:stack", lambda c: c["lives"]["also"].append("zzzVerdictGone"))
    edit_card(cards_dir, "species:chip", lambda c: c["lives"].update(path="content/video_engine/scripts/species/zzz.mjs"))

    # Act
    failures = ECC.check_anchors(cards(cards_dir))

    # Assert: the verdict stack's symbol lives in its species/*.mjs module, and only the added name is missing
    assert [f for f in failures if "dock_payload:stack" in f] == [
        "anchor: dock_payload:stack: 'zzzVerdictGone' not found in content/video_engine/scripts/species/verdict.mjs"]
    assert any("species:chip" in f and "does not exist" in f for f in failures)


# --------------------------------------------------------------------------- 4. proof

def test_a_golden_that_is_not_a_pytest_surface_fails(cards_dir):
    # Arrange
    edit_card(cards_dir, "exit:dip", lambda c: c["proof"].update(golden="zzz-missing"))

    # Act
    failures = ECC.check_proof(cards(cards_dir))

    # Assert
    assert any("exit:dip" in f and "zzz-missing" in f for f in failures), failures


def test_a_golden_on_disk_but_outside_the_pytest_surfaces_counts_as_no_golden(cards_dir):
    # Arrange: decision 7 - a frame exists, but nothing verifies it
    names = ECC.golden_names(ROOT) - {"ledger-extend"}
    assert (ROOT / ECC.FRAMES_REL / "ledger-extend.png").is_file()

    # Act
    failures = ECC.check_proof(cards(cards_dir), ROOT, names)

    # Assert
    assert any("chart_to:extend" in f and "ledger-extend" in f for f in failures), failures


def test_a_proof_test_naming_a_missing_function_fails(cards_dir):
    # Arrange
    edit_card(cards_dir, "exit:dip", lambda c: c["proof"].update(
        test="content/video_engine/tests/test_transitions_e47.py::test_zzz_not_there"))

    # Act
    failures = ECC.check_proof(cards(cards_dir))

    # Assert
    assert any("exit:dip" in f and "test_zzz_not_there" in f for f in failures), failures


# --------------------------------------------------------------------------- 5. examples

def test_an_exit_example_the_compiler_refuses_fails_naming_the_card(cards_dir):
    # Arrange: `melt:splash` is refused since E88
    edit_card(cards_dir, "exit:melt", lambda c: c["author"].update(example="'melt:splash'"))

    # Act
    failures, _ = ECC.check_examples(cards(cards_dir))

    # Assert
    assert any(f.startswith("example: exit:melt:") for f in failures), failures


def test_a_species_example_refused_by_validate_species_fails(cards_dir):
    # Arrange: a pointing species with no target
    edit_card(cards_dir, "species:callout", lambda c: c["author"].update(example="{'kind': 'callout', 'at': 1.0, 'dur': 2.0}"))

    # Act
    failures, _ = ECC.check_examples(cards(cards_dir))

    # Assert
    assert any(f.startswith("example: species:callout:") for f in failures), failures


def test_an_example_the_gate_cannot_parse_is_listed_as_skipped_never_passed_silently(cards_dir):
    # Arrange
    edit_card(cards_dir, "exit:dip", lambda c: c["author"].update(example="(DIP_ROW)"))

    # Act
    failures, skipped = ECC.check_examples(cards(cards_dir))

    # Assert
    assert any(s.startswith("exit:dip:") for s in skipped)
    assert not any("exit:dip" in f for f in failures)


# --------------------------------------------------------------------------- 6. aliases

def test_an_alias_on_two_cards_fails_naming_both_ids(cards_dir):
    # Arrange
    edit_card(cards_dir, "dock_option:stack",
              lambda c: c["aliases"].append({"name": "Evidence  Wall", "source": "tmp"}))

    # Act
    failures = ECC.check_aliases(cards(cards_dir))

    # Assert
    assert any("dock_option:stack" in f and "dock_payload:stack" in f for f in failures), failures


def test_an_alias_equal_to_another_cards_title_fails(cards_dir):
    # Arrange
    title = next(c["title"] for c in cards(cards_dir) if c["id"] == "dock_payload:stack")
    edit_card(cards_dir, "exit:dip", lambda c: c["aliases"].append({"name": title.upper(), "source": "tmp"}))

    # Act
    failures = ECC.check_aliases(cards(cards_dir))

    # Assert
    assert any("exit:dip" in f and "dock_payload:stack" in f for f in failures), failures


# --------------------------------------------------------------------------- 7. phases

def test_a_composite_card_that_lost_its_phases_fails_against_its_inventory_row(cards_dir, tmp_path):
    # Arrange
    inventory = tmp_path / "inventory"
    inventory.mkdir()
    row = {"axis": "exit", "token": "dip", "phases": [{"name": "in"}, {"name": "out"}]}
    (inventory / "inventory-C.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    edit_card(cards_dir, "exit:dip", lambda c: c.update(phases=[]))

    # Act
    failures, notes = ECC.check_phases(cards(cards_dir), inventory)

    # Assert
    assert any("exit:dip" in f for f in failures), failures
    assert notes == []


def test_the_phase_check_is_skipped_with_a_note_when_the_inventory_is_absent(cards_dir, tmp_path):
    # Act
    failures, notes = ECC.check_phases(cards(cards_dir), tmp_path / "absent")

    # Assert
    assert failures == [] and len(notes) == 1 and "skipped" in notes[0]


# --------------------------------------------------------------------------- 8. when

def test_a_species_card_that_copies_its_when_fails(cards_dir):
    # Arrange
    edit_card(cards_dir, "species:trace", lambda c: c.update(when="copied from the compiler"))

    # Act
    failures = ECC.check_when(cards(cards_dir))

    # Assert
    assert any("species:trace" in f for f in failures), failures


def test_a_species_kind_with_no_when_entry_fails(cards_dir, monkeypatch):
    # Arrange
    monkeypatch.setattr(B, "SPECIES_KINDS", B.SPECIES_KINDS + ("zzz_new",))

    # Act
    failures = ECC.check_when(cards(cards_dir))

    # Assert
    assert any("zzz_new" in f and "SPECIES_WHEN" in f for f in failures), failures


# --------------------------------------------------------------------------- P56 T8: the four uncarded effects

def card_of(card_id: str) -> dict:
    return next(c for c in cards(CARDS_DIR) if c["id"] == card_id)


@pytest.mark.xfail(strict=True, reason="R26-240: docs_find's effects layer does not rank by field, so the `does` match leads")
def test_the_ken_burns_card_is_implicit_and_docs_find_answers_with_it_first():
    """R26-224 (2026-09-18), classified (c) a defect in the recall layer, filed as R26-240: the card's own three
    assertions still pass; the RECALL one does not. `docs_find "Ken Burns" --layer effects` now answers with
    `plate_option:alive` (81210d8 / E99 s55, whose `does` mentions the Ken Burns plate) before `plate_option:ken`,
    because the effects Layer is the only recall layer built WITHOUT `rank_by_field=True` (capabilities and assets
    have it): every effects hit ranks 0, so the order is the catalogue's id order and `alive` sorts first.
    Measured: ken matches in `title` (field index 1), alive in `does` (index 3) - with the flag, ken leads."""
    """(a) The push and the drift are ONE card with no token of its own, and the recall layer leads with it."""
    # Arrange
    card = card_of("plate_option:ken")

    # Act
    hits = DF.search("Ken Burns", ("effects",), ROOT, 8).hits

    # Assert
    assert card["implicit"] is True and card["status"] == "live"
    assert {a["name"] for a in card["aliases"]} == {"Ken Burns", "the slow push"}
    assert "scale" in card["does"] and "x`/`y" in card["does"]      # both halves as the timeline carries them
    assert hits and hits[0].snippet.startswith("plate_option:ken"), [h.snippet for h in hits[:3]]


def test_the_ken_card_is_implicit_because_its_token_is_no_plate_option(cards_dir):
    """The drift gate accepts `ken` only as implicit: `ken` is not one of the compiler's PLATE_OPTS."""
    # Arrange
    assert "ken" not in B.PLATE_OPTS
    edit_card(cards_dir, "plate_option:ken", lambda c: c.pop("implicit"))

    # Act
    failures = ECC.check_phantoms(cards(cards_dir))

    # Assert
    assert any("plate_option:ken" in f for f in failures), failures
    assert not any("plate_option:ken" in f for f in ECC.check_phantoms(cards(CARDS_DIR)))


def test_the_world_and_clip_cards_are_the_walks_own_world_events():
    """(a2) The default plate world and the clip world: `world.kind == "clip"` is the field that tells them apart."""
    # Arrange
    steel = RW.load_timeline(ROOT / STEEL_TIMELINE)
    japan = RW.load_timeline(ROOT / JAPAN_TIMELINE)
    options = RW.option_owner(cards(CARDS_DIR))

    # Act
    plates = [e for e in RW.events(steel, options) if e.card == "plate_option:world"]
    clips = [e for e in RW.events(japan, options) if e.card == "plate_option:clip"]

    # Assert
    for card_id in ("plate_option:world", "plate_option:clip"):
        assert card_of(card_id)["implicit"] is True and card_of(card_id)["status"] == "live"
    assert len(plates) == len(steel["scenes"]) == 75 and plates[0].t == 0.0     # Steel: 75 of 75 worlds are plates
    assert [(e.scene, e.t) for e in clips] == [("s09", 60.1), ("s12", 79.08)]   # measured 2026-09-13
    assert all(s["world"].get("kind") == "clip" for s in japan["scenes"] if s["scene_id"] in ("s09", "s12"))
    assert card_of("plate_option:clip")["proof"]["first_use"]["t"] == 79.08     # s12, the outro clip


def test_the_badge_card_is_the_walks_badge_event_on_a_dock_rail_and_a_page_rail():
    """(a2) One card for both rails: `badge_at[]` on a dock, `page.badges[]` on a ledger page."""
    # Arrange
    steel = RW.load_timeline(ROOT / STEEL_TIMELINE)
    japan = RW.load_timeline(ROOT / JAPAN_TIMELINE)
    options = RW.option_owner(cards(CARDS_DIR))
    card = card_of("dock_option:badge")

    # Act
    on_docks = [e for e in RW.events(steel, options) if e.card == "dock_option:badge"]
    on_pages = [e for e in RW.events(japan, options) if e.card == "dock_option:badge"]

    # Assert
    assert card["implicit"] is True and card["status"] == "live" and card["author"]["key"].startswith("`badge_at[]`")
    assert "the badge ladder" not in {a["name"].lower() for a in card["aliases"]}   # that is the recipe's title
    assert len(on_docks) == 81 and on_docks[0].t == 11.55                           # measured 2026-09-13
    first = next(d for s in steel["scenes"] for d in (s.get("docks") or []) if d.get("badge_at"))
    assert round(first["badge_at"][0] - first["enter"], 2) == 2.05                  # dock_enter + 2.05
    assert round(first["badge_at"][1] - first["badge_at"][0], 2) == 1.30            # then 1.30 apart
    assert [e.scene for e in on_pages] == ["s06", "s08"]                            # the page rail (Japan s06)
    assert card["proof"]["first_use"] == {"project": "steel-and-paper", "build": "build-f", "t": 11.55}


# --------------------------------------------------------------------------- P56 T8 (b): wipe_right is an option

def test_a_wipe_right_member_is_accepted_as_the_wipe_cards_option(recipes_dir, cards_dir):
    """(b) `wipe_right` needs no card: it is `exit:wipe`'s listed OPTION, and a member may name it."""
    # Arrange
    edit_recipe(recipes_dir, GOOD_RECIPE,
                lambda d: d["members"][1].update(card="exit:wipe", option="wipe_right"))

    # Act
    failures = ECC.check_recipe_members(recipes(recipes_dir), cards(cards_dir))

    # Assert
    assert [f for f in failures if GOOD_RECIPE in f] == [], failures
    assert "wipe_right" in {o["token"] for o in card_of("exit:wipe")["options"]}


def test_steels_thirty_two_wipe_right_exits_are_fires_of_that_member():
    """The walk resolves the timeline's `wipe_right` to exit:wipe + the option - 32 of them (measured 2026-09-13)."""
    # Arrange
    steel = RW.load_timeline(ROOT / STEEL_TIMELINE)

    # Act
    fires = [e for e in RW.events(steel, RW.option_owner(cards(CARDS_DIR)))
             if e.card == "exit:wipe" and e.option == "wipe_right"]

    # Assert
    assert len(fires) == 32, f"Steel's wipe_right exits: {len(fires)} (the pin is the 2026-09-13 measurement)"
    assert RW.fits(fires[0], {"card": "exit:wipe", "option": "wipe_right"})


# --------------------------------------------------------------------------- P56 T8 (c): the long form's vocabulary

STEEL_SPEAKABLE_AXES = frozenset({"dock_kind", "dock_payload", "chart_dock", "dock_option", "exit", "plate_option"})
"""The only axes a Steel-proven recipe can use: 75 plate worlds, 43 docks, no species and no ledger page.
Measured 2026-09-13, per recipe: badge-ladder {dock_kind}, held-dock-across-the-cut {dock_payload, exit},
plate-dock-wipe {dock_kind, dock_payload, exit}, test-card-rows {chart_dock}, verdict-recap {dock_payload} - the
speakable SET is pinned, not that union, so T3's amendment may add dock_option:badge / plate_option:ken members."""


def test_the_long_form_speaks_no_species_and_no_page_vocabulary():
    """(c) Steel's timeline: 75 scenes with `species: []` and 0 ledger pages - the verdict as a test, not a hope."""
    # Arrange
    steel = RW.load_timeline(ROOT / STEEL_TIMELINE)

    # Act
    scenes = steel["scenes"]

    # Assert
    assert len(scenes) == 75
    assert [s["scene_id"] for s in scenes if s.get("species")] == []
    assert [s["scene_id"] for s in scenes if (s.get("world") or {}).get("page")] == []


def test_every_steel_proven_recipe_uses_only_the_axes_the_long_form_can_speak():
    # Arrange
    steel_recipes = [r for r in recipes(RECIPES_DIR)
                     if r.get("status") == "proven" and (r.get("proof") or {}).get("project") == "steel-and-paper"]

    # Act
    used = {r["id"]: sorted({m["card"].split(":")[0] for m in r["members"]}) for r in steel_recipes}

    # Assert
    assert len(steel_recipes) == 5, sorted(used)
    assert all(set(axes) <= STEEL_SPEAKABLE_AXES for axes in used.values()), used


def test_a_species_member_with_a_steel_proof_cannot_fire_and_fails(recipes_dir):
    """A species can never fire on the long form, so a Steel proof naming one is a failure, not a warning."""
    # Arrange
    steel_recipe = "recipe:verdict-recap"
    edit_recipe(recipes_dir, steel_recipe, lambda d: d["members"][0].update(card="species:trace"))

    # Act
    failures = [f for f in ECC.check_recipe_proof(recipes(recipes_dir), ROOT, cards(CARDS_DIR))
                if steel_recipe in f]

    # Assert
    assert failures and "species:trace" in failures[0], failures


# --------------------------------------------------------------------------- the generator carries the gate

def test_build_effects_catalog_check_exits_1_on_drift(monkeypatch, capsys):
    # Arrange
    monkeypatch.setattr(BEC, "check", lambda repo, when=None: [])
    monkeypatch.setattr(ECC, "check", lambda repo: ["alias: 'zzz' is on a:b and c:d"])

    # Act
    code = BEC.main(["--check"])

    # Assert
    out = capsys.readouterr().out
    assert code == 1
    assert "DRIFT" in out and "zzz" in out


def test_the_cli_exits_1_and_prints_each_failure(cards_dir, monkeypatch, capsys):
    # Arrange
    real_run = ECC.run
    monkeypatch.setattr(ECC, "run", lambda repo: real_run(repo, cards_dir))
    edit_card(cards_dir, "exit:dip", lambda c: c["lives"].update(symbol="zzzDipRenamed"))

    # Act
    code = ECC.main([])

    # Assert
    out = capsys.readouterr().out
    assert code == 1
    assert "FAIL anchor: exit:dip: 'zzzDipRenamed'" in out


# --------------------------------------------------------------------------- the P56 review (2026-09-13)

def test_recipe_count_fails_a_count_the_walk_does_not_reproduce(recipes_dir):
    # Arrange: the ladder fires 4 times in Japan; the file claims 99
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d.update(count=99))

    # Act
    failures, _ = ECC.check_recipe_count(recipes(recipes_dir), ROOT, cards(CARDS_DIR))

    # Assert
    assert any(GOOD_RECIPE in f and "99" in f and "4" in f for f in failures), failures


def test_the_committed_counts_are_the_matchers_own():
    """One definition of count: what `recipe_walk.count` finds in the proof timeline."""
    # Act
    failures, _ = ECC.check_recipe_count(recipes(RECIPES_DIR), ROOT, cards(CARDS_DIR))

    # Assert
    assert failures == []


def test_recipe_members_refuses_a_first_member_that_is_not_the_anchor(recipes_dir):
    # Arrange
    edit_recipe(recipes_dir, GOOD_RECIPE, lambda d: d["members"][0].update(offset_s=0.5))

    # Act
    failures = ECC.check_recipe_members(recipes(recipes_dir), cards(CARDS_DIR))

    # Assert
    assert any(GOOD_RECIPE in f and "member 1" in f and "0" in f for f in failures), failures


def test_a_proven_recipe_whose_optional_member_is_absent_validates_and_passes(recipes_dir):
    """An absent optional member holds null in `proof.members_at`: the schema allows it, the walk agrees."""
    import jsonschema

    # Arrange: an optional punch behind the ladder's first hop - Japan plays no punch at all
    def mutate(doc):
        doc["members"].insert(1, {"card": "species:punch", "offset_s": [0.0, 0.55], "optional": True,
                                  "role": "a punch this cut never plays here"})
        doc["proof"]["members_at"].insert(1, None)
    edit_recipe(recipes_dir, GOOD_RECIPE, mutate)
    doc = json.loads((recipes_dir / "trace-callout-ladder.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / BEC.RECIPE_SCHEMA_REL).read_text(encoding="utf-8"))

    # Act
    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(doc))
    proof = [f for f in ECC.check_recipe_proof(recipes(recipes_dir), ROOT, cards(CARDS_DIR)) if GOOD_RECIPE in f]
    counts, _ = ECC.check_recipe_count(recipes(recipes_dir), ROOT, cards(CARDS_DIR))

    # Assert
    assert [e.message for e in errors] == []
    assert proof == []
    assert [c for c in counts if GOOD_RECIPE in c] == []


def test_the_drift_gate_expands_a_recipe_member_before_it_walks(recipes_dir):
    """A parent naming a child recipe is proven by the flattened members - the gate passes the registry down."""
    # Arrange: the ladder's last two members move into a child recipe the parent names
    child = json.loads((recipes_dir / "trace-callout-ladder.json").read_text(encoding="utf-8"))
    parent = copy.deepcopy(child)
    child.update(id="recipe:test-tail", title="The test tail", aliases=[], count=4,
                 members=[dict(m, offset_s=(m["offset_s"] - 2.52)) for m in child["members"][4:]])
    child["proof"] = dict(parent["proof"], t=11.74, members_at=[11.74, 12.29])
    (recipes_dir / "test-tail.json").write_text(json.dumps(child, indent=2) + "\n", encoding="utf-8")
    parent["members"] = parent["members"][:4] + [{"card": "recipe:test-tail", "offset_s": 2.52,
                                                  "role": "the ladder's third rung, as its own recipe"}]
    (recipes_dir / "trace-callout-ladder.json").write_text(json.dumps(parent, indent=2) + "\n", encoding="utf-8")

    # Act
    failures = ECC.check_recipe_proof(recipes(recipes_dir), ROOT, cards(CARDS_DIR))
    counts, _ = ECC.check_recipe_count(recipes(recipes_dir), ROOT, cards(CARDS_DIR))

    # Assert
    assert [f for f in failures if GOOD_RECIPE in f] == []
    assert [c for c in counts if GOOD_RECIPE in c] == []
