from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from content.video_engine.src.services.history_contracts import (
    HISTORY_EPISODE_VERSION,
    RESEARCH_PACKET_VERSION,
    HistoryContractValidationError,
    canonical_sha256,
    check_history_episode,
    check_research_packet,
    load_history_episode,
    load_research_packet,
    validate_history_episode,
    validate_research_packet,
)


ENGINE_ROOT = Path(__file__).resolve().parents[1]


def _template(name: str) -> dict:
    return json.loads((ENGINE_ROOT / "templates" / name).read_text(encoding="utf-8"))


def test_history_and_research_templates_are_strict_and_hash_stable() -> None:
    episode = validate_history_episode(_template("history_episode.json"))
    packet = validate_research_packet(_template("research_packet.json"))
    assert episode["schema_version"] == HISTORY_EPISODE_VERSION
    assert packet["schema_version"] == RESEARCH_PACKET_VERSION
    assert episode["artifact_hash"] == canonical_sha256(episode)
    assert packet["artifact_hash"] == canonical_sha256(packet)

    for filename, payload in (
        ("history_episode.schema.json", episode),
        ("research_packet.schema.json", packet),
    ):
        schema = json.loads((ENGINE_ROOT / "configs" / filename).read_text(encoding="utf-8"))
        assert list(Draft7Validator(schema).iter_errors(payload)) == []

    reordered = {key: packet[key] for key in reversed(list(packet))}
    assert canonical_sha256(reordered) == packet["artifact_hash"]


def test_history_validation_rejects_unknown_fields_and_bad_output_set() -> None:
    episode = _template("history_episode.json")
    episode["unexpected"] = True
    errors = check_history_episode(episode)
    assert any("additional properties" in error.casefold() for error in errors)

    episode = _template("history_episode.json")
    episode["outputs"] = episode["outputs"][:3]
    errors = check_history_episode(episode)
    assert any("chapter-level subvideo" in error for error in errors)


def test_research_validation_requires_citations_and_blocks_study_leakage() -> None:
    packet = _template("research_packet.json")
    packet["claims"][0]["citation_ids"] = []
    errors = check_research_packet(packet)
    assert any("requires at least one citation" in error or "minItems" in error for error in errors)

    packet = _template("research_packet.json")
    packet["sources"].append(
        {
            "id": "consultant-outline",
            "title": "Consultant outline",
            "source_kind": "consultant",
            "locator": "operator note",
            "role": "factual",
            "is_factual_source": True,
        }
    )
    errors = check_research_packet(packet)
    assert any("cannot be a factual source" in error for error in errors)


def test_research_validation_requires_quote_locator_and_independent_contested_sources() -> None:
    packet = _template("research_packet.json")
    packet["claims"][0]["direct_quote"] = True
    packet["claims"][0]["quote"] = "A direct quotation."
    packet["citations"][0].pop("locator")
    errors = check_research_packet(packet)
    assert any("direct quote" in error and "locator" in error for error in errors)

    packet = _template("research_packet.json")
    packet["sources"][1]["independence_group"] = packet["sources"][0]["independence_group"]
    errors = check_research_packet(packet)
    assert any("independent citations" in error for error in errors)


def test_loaders_are_path_safe_and_do_not_mutate_input(tmp_path: Path) -> None:
    episode = _template("history_episode.json")
    original = copy.deepcopy(episode)
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(_template("research_packet.json")), encoding="utf-8")
    assert load_research_packet(packet_path, root=tmp_path)["schema_version"] == RESEARCH_PACKET_VERSION
    assert episode == original

    outside = tmp_path.parent / "outside-packet.json"
    outside.write_text(json.dumps(_template("research_packet.json")), encoding="utf-8")
    with pytest.raises((ValueError, HistoryContractValidationError)):
        load_research_packet(Path("..") / outside.name, root=tmp_path)
