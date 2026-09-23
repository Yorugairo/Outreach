"""P69 T35b: a recipe's optional `use_when` block (BRAVOS-USE-WHEN.md's fields) is pinned.

The pins: a recipe carrying a full `use_when` validates against `effect_recipe.schema.json`; one missing a required
key is refused; a `moment` outside the documented vocabulary (hook / setup / proof / turn / reveal / close, or several
joined by ' / ') is refused; a recipe without `use_when` still validates (the field is optional); and
`build_effects_catalog.py` carries the block into the recipe's catalogue record and writes its `use when` line, while
a recipe without one gets neither.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_effects_catalog as BEC  # noqa: E402

USE_WHEN = {
    "act": "COMPARES - two durations",
    "moment": "turn",
    "shape": "two numbers, one unit",
    "use": "a contrast of two clocks where the short one is the claim",
    "dont": "two units, or more than two durations",
}


@pytest.fixture(scope="module")
def validator() -> jsonschema.Draft202012Validator:
    schema = json.loads((ROOT / BEC.RECIPE_SCHEMA_REL).read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema)


def recipe(**over) -> dict:
    base = {
        "schema_version": "effect_recipes.v1", "id": "recipe:use-when-probe", "title": "The use-when probe",
        "aliases": [], "acts": ["COMPARES"],
        "members": [{"card": "page_builder:bars", "offset_s": 0.0, "role": "two bars built on one unit"},
                    {"card": "page_species:figure", "offset_s": 1.5, "role": "the short bar's figure written"}],
        "does": "Two durations on one unit, the short one's figure written on its word.", "status": "candidate",
        "source": "test_recipe_use_when", "count": 0,
    }
    return {**base, **over}


def errors_of(validator: jsonschema.Draft202012Validator, doc: dict) -> list[str]:
    return [e.message for e in validator.iter_errors(doc)]


def test_a_recipe_with_a_full_use_when_validates(validator):
    # Arrange
    doc = recipe(use_when=dict(USE_WHEN))

    # Act
    errors = errors_of(validator, doc)

    # Assert
    assert errors == []


@pytest.mark.parametrize("missing", ["act", "moment", "shape", "use", "dont"])
def test_a_use_when_missing_a_required_key_is_refused(validator, missing):
    # Arrange
    block = {k: v for k, v in USE_WHEN.items() if k != missing}
    doc = recipe(use_when=block)

    # Act
    errors = errors_of(validator, doc)

    # Assert
    assert any(repr(missing) in message and "required" in message for message in errors), errors


@pytest.mark.parametrize("moment", ["climax", "Proof", "proof/reveal", "proof / climax", "", "proof / "])
def test_a_moment_outside_the_vocabulary_is_refused(validator, moment):
    # Arrange
    doc = recipe(use_when={**USE_WHEN, "moment": moment})

    # Act
    errors = errors_of(validator, doc)

    # Assert
    assert errors, f"moment {moment!r} should be refused"


@pytest.mark.parametrize("moment", ["hook", "setup", "proof", "turn", "reveal", "close", "proof / reveal",
                                    "hook / turn"])
def test_every_documented_moment_and_a_joined_pair_validates(validator, moment):
    # Arrange
    doc = recipe(use_when={**USE_WHEN, "moment": moment})

    # Act
    errors = errors_of(validator, doc)

    # Assert
    assert errors == []


def test_a_recipe_without_use_when_still_validates(validator):
    # Arrange
    doc = recipe()

    # Act
    errors = errors_of(validator, doc)

    # Assert
    assert "use_when" not in doc
    assert errors == []


def test_the_catalogue_record_carries_use_when_and_writes_its_line():
    # Arrange
    doc = recipe(use_when=copy.deepcopy(USE_WHEN))

    # Act
    record = BEC.recipe_record_of(doc, {}, [], ROOT)
    block = BEC.recipe_block(record)

    # Assert
    assert record["use_when"] == USE_WHEN
    use_lines = [line for line in block if line.startswith("- **use when**")]
    assert use_lines == [f"- **use when** {USE_WHEN['act']} - {USE_WHEN['moment']} - {USE_WHEN['shape']}: "
                         f"{USE_WHEN['use']}. **not** {USE_WHEN['dont']}"]


def test_a_record_without_use_when_carries_no_key_and_no_line():
    # Arrange
    doc = recipe()

    # Act
    record = BEC.recipe_record_of(doc, {}, [], ROOT)
    block = BEC.recipe_block(record)

    # Assert
    assert "use_when" not in record
    assert not any("**use when**" in line for line in block)


def test_every_committed_recipe_with_use_when_carries_it_into_the_catalogue():
    # Arrange
    files = sorted((ROOT / BEC.RECIPES_REL).glob("*.json"))
    on_disk = {}
    for path in files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("use_when"):
            on_disk[doc["id"]] = doc["use_when"]

    # Act
    records = {r["id"]: r for r in BEC.recipes_of(BEC.build(ROOT))}

    # Assert
    assert on_disk, "no committed recipe carries use_when"
    for rid, block in on_disk.items():
        assert records[rid]["use_when"] == block
