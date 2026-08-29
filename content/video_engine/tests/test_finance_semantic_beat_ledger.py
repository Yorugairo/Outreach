from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from content.video_engine.src.services.finance_channel import (
    FinanceChannelValidationError,
    file_sha256,
    validate_artifact,
    with_artifact_hash,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = (
    REPO_ROOT
    / "content"
    / "video_engine"
    / "scripts"
    / "compile_finance_semantic_beat_ledger.py"
)
PILOT_ROOT = (
    REPO_ROOT
    / "content"
    / "video_engine"
    / "projects"
    / "systems-and-blowups"
    / "pilots"
    / "current-bubble-mechanism"
)
LEDGER_PATH = (
    PILOT_ROOT
    / "edit"
    / "sentence-native-v1"
    / "semantic-beat-ledger.v1.json"
)
WORDS_PATH = PILOT_ROOT / "audio" / "canonical" / "history_episode_1_master.words.json"


def _module():
    spec = importlib.util.spec_from_file_location("finance_semantic_beat_compiler", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_checked_in_ledger_validates_and_binds_current_sources() -> None:
    ledger = _json(LEDGER_PATH)
    assert validate_artifact(ledger)["schema_version"] == "finance_semantic_beat_ledger.v1"
    for binding in ledger["source_bindings"].values():
        path = Path(binding["path"])
        if not path.is_absolute():
            path = REPO_ROOT / path
        assert path.is_file()
        assert binding["sha256"] == file_sha256(path)


def test_compiler_is_deterministic_and_preserves_every_canonical_word_once() -> None:
    module = _module()
    first = module.compile_semantic_beat_ledger(PILOT_ROOT, reviewed_boundaries=True)
    second = module.compile_semantic_beat_ledger(PILOT_ROOT, reviewed_boundaries=True)
    assert first == second
    assert first == _json(LEDGER_PATH)

    words_payload = _json(WORDS_PATH)
    words = words_payload["words"]
    beats = first["beats"]
    assert 180 <= len(beats) <= 240
    assert beats[0]["start_word_index"] == 0
    assert beats[-1]["end_word_index"] == len(words) - 1
    expected_start = 0
    for beat in beats:
        assert beat["start_word_index"] == expected_start
        assert beat["end_word_index"] >= beat["start_word_index"]
        excerpt = " ".join(
            word["w"]
            for word in words[beat["start_word_index"] : beat["end_word_index"] + 1]
        )
        assert beat["excerpt"] == excerpt
        verb = beat["causal_verb"]
        assert beat["start_word_index"] <= verb["word_index"] <= beat["end_word_index"]
        assert verb["surface"] == words[verb["word_index"]]["w"]
        for noun in beat["active_nouns"]:
            assert beat["start_word_index"] <= noun["start_word_index"]
            assert noun["end_word_index"] <= beat["end_word_index"]
        expected_start = beat["end_word_index"] + 1
    assert expected_start == len(words)


def test_stable_ids_and_manually_reviewed_chapter_boundaries() -> None:
    ledger = _json(LEDGER_PATH)
    chapters = ledger["chapters"]
    reviews = ledger["chapter_boundary_review"]
    assert len(chapters) == 11
    assert [review["chapter_id"] for review in reviews] == [
        chapter["chapter_id"] for chapter in chapters
    ]
    assert all(review["status"] == "manually_reviewed" for review in reviews)
    for chapter in chapters:
        chapter_beats = [
            beat for beat in ledger["beats"] if beat["chapter_id"] == chapter["chapter_id"]
        ]
        assert chapter_beats[0]["start_word_index"] == chapter["start_word_index"]
        assert chapter_beats[-1]["end_word_index"] == chapter["end_word_index"]
        assert [beat["local_index"] for beat in chapter_beats] == list(
            range(1, len(chapter_beats) + 1)
        )
        assert len({beat["beat_id"] for beat in chapter_beats}) == len(chapter_beats)


@pytest.mark.parametrize("field", ["active_nouns", "causal_verb"])
def test_validator_rejects_missing_semantic_noun_or_verb(field: str) -> None:
    ledger = copy.deepcopy(_json(LEDGER_PATH))
    ledger.pop("artifact_hash")
    ledger["beats"][0][field] = [] if field == "active_nouns" else {}
    ledger = with_artifact_hash(ledger)
    with pytest.raises(FinanceChannelValidationError, match="requires"):
        validate_artifact(ledger)


def test_claim_refs_are_known_to_the_bound_claim_ledger() -> None:
    ledger = _json(LEDGER_PATH)
    claims = _json(PILOT_ROOT / "claim-ledger.v1.json")
    claim_ids = {claim["claim_id"] for claim in claims["claims"]}
    assert {
        claim_ref
        for beat in ledger["beats"]
        for claim_ref in beat["claim_refs"]
    } <= claim_ids
