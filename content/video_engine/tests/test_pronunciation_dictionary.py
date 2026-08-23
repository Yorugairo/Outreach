from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.pronunciation_dictionary import (
    ADD_RULES_ENDPOINT,
    CREATE_ENDPOINT,
    PHONEME_CAPABLE_MODELS,
    PronunciationDictionaryError,
    add_rules,
    compile_sync_request,
    needs_sync,
    ordered_rules,
    preview,
    record_sync_result,
    validate_dictionary,
)

SCRIPT = (
    "South Korea committed three trillion Korean won to the programme. "
    "The fund won broad support, and analysts said the bet had already won."
)


def _alias(target="Korean won", alias="Korean wahn") -> dict:
    return {"string_to_replace": target, "type": "alias", "alias": alias}


def _phoneme(target="Nginx", phoneme="ˈɛndʒɪnˈɛks") -> dict:
    return {
        "string_to_replace": target,
        "type": "phoneme",
        "phoneme": phoneme,
        "alphabet": "ipa",
    }


def _dictionary(*rules, model_id="eleven_v3") -> dict:
    return {
        "schema_version": "pronunciation_dictionary.v1",
        "name": "Systems and Blowups",
        "model_id": model_id,
        "rules": list(rules) or [_alias()],
    }


def test_alias_rule_is_valid_on_any_model():
    for model in ("eleven_multilingual_v2", "eleven_v3", "eleven_flash_v2"):
        assert validate_dictionary(_dictionary(_alias(), model_id=model))["model_id"] == model


def test_phoneme_rule_on_multilingual_v2_is_rejected_loudly():
    # The trap: multilingual v2 skips phoneme tags silently, so the rule would
    # appear to work and change nothing.
    with pytest.raises(PronunciationDictionaryError) as excinfo:
        validate_dictionary(_dictionary(_phoneme(), model_id="eleven_multilingual_v2"))

    joined = " ".join(excinfo.value.errors)
    assert "silently ignored" in joined
    assert "eleven_v3" in joined


@pytest.mark.parametrize("model", sorted(PHONEME_CAPABLE_MODELS))
def test_phoneme_rule_is_accepted_on_capable_models(model):
    assert validate_dictionary(_dictionary(_phoneme(), model_id=model))


def test_phoneme_rule_requires_an_alphabet():
    rule = _phoneme()
    del rule["alphabet"]

    with pytest.raises(PronunciationDictionaryError) as excinfo:
        validate_dictionary(_dictionary(rule))

    assert any("requires 'alphabet'" in error for error in excinfo.value.errors)


def test_alias_rule_requires_an_alias():
    with pytest.raises(PronunciationDictionaryError) as excinfo:
        validate_dictionary(_dictionary({"string_to_replace": "won", "type": "alias"}))

    assert any("requires 'alias'" in error for error in excinfo.value.errors)


def test_duplicate_targets_are_rejected():
    with pytest.raises(PronunciationDictionaryError) as excinfo:
        validate_dictionary(_dictionary(_alias(), _alias(alias="Korean wone")))

    assert any("duplicates" in error for error in excinfo.value.errors)


def test_longest_target_is_ordered_first():
    rules = ordered_rules([_alias("won", "wahn"), _alias("Korean won", "Korean wahn")])

    assert rules[0]["string_to_replace"] == "Korean won"


def test_preview_finds_the_phrase_and_not_the_verb():
    report = preview(_dictionary(_alias()), SCRIPT)

    entry = report["rules"][0]
    assert entry["string_to_replace"] == "Korean won"
    assert entry["match_count"] == 1


def test_preview_exposes_the_bare_word_collision():
    # This is the whole point: "won" also fires on "won broad support".
    report = preview(_dictionary(_alias("won", "wahn")), SCRIPT)

    assert report["rules"][0]["match_count"] == 3
    assert report["total_matches"] == 3


def test_preview_reports_dead_rules():
    report = preview(_dictionary(_alias("Kubernetes", "koo-ber-net-eez")), SCRIPT)

    assert report["unmatched_rules"] == ["Kubernetes"]
    assert report["matched_rule_count"] == 0


def test_preview_does_not_match_inside_words():
    report = preview(_dictionary(_alias("won", "wahn")), "The wonder of it all.")

    assert report["total_matches"] == 0


def test_first_sync_creates_and_later_sync_appends():
    fresh = compile_sync_request(_dictionary())
    assert fresh["endpoint"] == CREATE_ENDPOINT
    assert fresh["body"]["name"] == "Systems and Blowups"

    known = dict(_dictionary())
    known["dictionary_id"] = "5xM3yVvZQKV0EfqQpLrJ"
    later = compile_sync_request(known)
    assert later["endpoint"] == ADD_RULES_ENDPOINT.format(
        dictionary_id="5xM3yVvZQKV0EfqQpLrJ"
    )
    assert "name" not in later["body"]


def test_sync_request_makes_no_network_call(monkeypatch):
    import socket

    def _forbidden(*args, **kwargs):  # pragma: no cover - regression guard
        raise AssertionError("compiling a sync request must not touch the network")

    monkeypatch.setattr(socket.socket, "connect", _forbidden)

    assert compile_sync_request(_dictionary())["rule_count"] == 1


def test_recording_a_sync_marks_it_current(tmp_path):
    summary = record_sync_result(
        _dictionary(),
        dictionary_id="dict-1",
        version_id="ver-1",
        output_path=tmp_path / "pron.json",
    )
    saved = json.loads(Path(summary["path"]).read_text(encoding="utf-8"))

    assert summary["needs_sync"] is False
    assert saved["dictionary_id"] == "dict-1"
    assert needs_sync(saved) is False


def test_adding_a_rule_reopens_the_sync(tmp_path):
    synced = record_sync_result(
        _dictionary(),
        dictionary_id="dict-1",
        version_id="ver-1",
        output_path=tmp_path / "pron.json",
    )
    grown = add_rules(
        synced["path"],
        [_alias("Nikkei", "nih-KAY")],
        output_path=tmp_path / "pron.json",
    )

    assert grown["added"] == ["Nikkei"]
    assert grown["needs_sync"] is True, "new rules must be pushed before the next take"


def test_replacing_a_rule_is_reported_as_an_override(tmp_path):
    result = add_rules(
        _dictionary(),
        [_alias(alias="Korean wone")],
        output_path=tmp_path / "pron.json",
    )

    assert result["overridden"] == ["Korean won"]
    assert result["added"] == []
    assert result["rule_count"] == 1


def test_accretion_keeps_earlier_episode_fixes(tmp_path):
    first = add_rules(
        _dictionary(),
        [_alias("Nikkei", "nih-KAY")],
        output_path=tmp_path / "pron.json",
    )
    second = add_rules(
        first["path"],
        [_alias("Nasdaq", "NAZ-dak")],
        output_path=tmp_path / "pron.json",
    )
    saved = json.loads(Path(second["path"]).read_text(encoding="utf-8"))
    targets = {rule["string_to_replace"] for rule in saved["rules"]}

    assert targets == {"Korean won", "Nikkei", "Nasdaq"}
