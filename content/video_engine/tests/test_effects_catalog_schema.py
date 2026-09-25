"""R26-141: the drift gate refuses a card the card schema refuses, by name (P72 T2).

P61 T4b's cards passed `effects_catalog_check.py` with a `does` over 240 characters and a `lives.note` over 200;
only `build_docs_layers.py --write` refused them, six minutes later, through `build_effects_catalog.py`. A lane's
validate line runs the drift gate, not the layers, so the gate now loads `configs/effect_card.schema.json` itself
and names the card, the field and the cap. Every edit here is to a temp copy of the cards; the repo's are only read.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_effects_catalog as BEC  # noqa: E402
import effects_catalog_check as ECC  # noqa: E402

CARDS_DIR = ROOT / BEC.CARDS_REL
SCHEMA = json.loads((ROOT / BEC.SCHEMA_REL).read_text(encoding="utf-8"))


def card_cap(field: str) -> int:
    return SCHEMA["$defs"]["card"]["properties"][field]["maxLength"]


@pytest.fixture()
def cards_dir(tmp_path: Path) -> Path:
    target = tmp_path / "cards"
    shutil.copytree(CARDS_DIR, target)
    return target


def edit_first_card(cards_dir: Path, axis: str, change) -> str:
    path = cards_dir / f"{axis}.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    change(doc["cards"][0])
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc["cards"][0]["id"]


def test_the_committed_cards_pass_the_schema():
    assert ECC.check_schema(CARDS_DIR) == []


def test_a_does_over_its_cap_is_refused_naming_the_card_the_field_and_the_cap(cards_dir):
    # Arrange
    cap = card_cap("does")
    card_id = edit_first_card(cards_dir, "arrival", lambda c: c.update(does="x" * (cap + 11)))

    # Act
    failures = ECC.check_schema(cards_dir)

    # Assert
    assert failures == [f"arrival.json: {card_id}: `does` is {cap + 11} chars, over the schema's maxLength {cap}"]


def test_a_nested_field_over_its_cap_is_named_by_its_dotted_path(cards_dir):
    card_id = edit_first_card(cards_dir, "arrival", lambda c: c["lives"].update(note="n" * 201))

    failures = ECC.check_schema(cards_dir)

    assert len(failures) == 1 and failures[0].startswith(f"arrival.json: {card_id}: `lives.note` is 201 chars")
    assert failures[0].endswith("maxLength 200")


def test_a_missing_required_field_is_named(cards_dir):
    card_id = edit_first_card(cards_dir, "exit", lambda c: c.pop("does"))

    failures = ECC.check_schema(cards_dir)

    assert len(failures) == 1 and f"exit.json: {card_id}:" in failures[0] and "'does'" in failures[0], failures


def test_the_gate_run_carries_the_schema_check(cards_dir):
    """Wired, not only defined: the gate's own run over the broken copy fails on the card by name."""
    card_id = edit_first_card(cards_dir, "arrival", lambda c: c.update(does="x" * (card_cap("does") + 1)))

    failures = ECC.run(ROOT, cards_dir=cards_dir).failures

    assert any(f.startswith(f"arrival.json: {card_id}: `does`") for f in failures), failures
