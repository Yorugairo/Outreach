"""Pronunciation rules as a versioned, accretive repo artifact.

A dictionary entered by hand in a vendor dashboard is invisible to the pipeline,
unversioned, and lost with the account. Held here it behaves like the asset
catalogue: every episode's mispronunciations become permanent corrections that all
later episodes inherit.

Two things this module refuses to let you get wrong:

* **Phoneme rules on the wrong model.** Only ``eleven_flash_v2`` and ``eleven_v3``
  honour phoneme tags. Every other model — including ``eleven_multilingual_v2`` —
  skips them *silently* and uses the default pronunciation, so a perfectly correct
  IPA rule produces no audible change and no error. That failure is rejected at
  authoring time instead.
* **Bare-word rules that fire where you did not mean them.** A rule fixing "won"
  in "Korean won" also fires on "he won the race". ``preview`` reports every match
  against a real script so a collision is visible before a take is paid for.

Nothing here touches the network. ``compile_sync_request`` produces the request
body; the operator or run agent performs the call.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.services.artifact_io import (
    load_json,
    sha256_json,
    stamp_artifact_hash,
    write_artifact,
)

PRONUNCIATION_DICTIONARY_VERSION = "pronunciation_dictionary.v1"

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _VIDEO_ENGINE_ROOT / "configs"

#: Models that honour phoneme tags. Everything else silently ignores them.
PHONEME_CAPABLE_MODELS = frozenset({"eleven_flash_v2", "eleven_v3"})

CREATE_ENDPOINT = "/v1/pronunciation-dictionaries/add-from-rules"
ADD_RULES_ENDPOINT = "/v1/pronunciation-dictionaries/{dictionary_id}/add-rules"


class PronunciationDictionaryError(ValueError):
    """A rule is malformed, unusable on the declared model, or conflicting."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid pronunciation dictionary")


def _schema_errors(payload: Mapping[str, Any]) -> list[str]:
    schema = load_json(
        _CONFIG_DIR / "pronunciation_dictionary.schema.json", "pronunciation schema"
    )
    validator = Draft7Validator(schema)
    return [
        "dictionary" + "".join(f"[{part!r}]" for part in error.absolute_path) + f": {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda e: list(e.absolute_path))
    ]


def _rule_errors(rules: Sequence[Mapping[str, Any]], model_id: str) -> list[str]:
    errors: list[str] = []
    seen: dict[str, int] = {}

    for index, rule in enumerate(rules):
        label = f"rules[{index}] ({rule.get('string_to_replace')!r})"
        kind = rule.get("type")

        if kind == "alias" and not rule.get("alias"):
            errors.append(f"{label}: an alias rule requires 'alias'")
        if kind == "phoneme":
            if not rule.get("phoneme"):
                errors.append(f"{label}: a phoneme rule requires 'phoneme'")
            if not rule.get("alphabet"):
                errors.append(f"{label}: a phoneme rule requires 'alphabet'")
            if model_id not in PHONEME_CAPABLE_MODELS:
                errors.append(
                    f"{label}: phoneme rules are silently ignored by {model_id!r}. Only "
                    + ", ".join(sorted(PHONEME_CAPABLE_MODELS))
                    + " honour phoneme tags; use an alias rule or change model_id"
                )

        target = str(rule.get("string_to_replace") or "")
        if target in seen:
            errors.append(
                f"{label}: duplicates rules[{seen[target]}]; the later rule would "
                "replace the earlier one at the provider"
            )
        seen[target] = index

    return errors


def ordered_rules(rules: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Longest target first, so a phrase rule wins over a bare-word rule."""

    return sorted(
        (dict(rule) for rule in rules),
        key=lambda rule: (-len(str(rule.get("string_to_replace") or "")),
                          str(rule.get("string_to_replace") or "")),
    )


def rules_hash(rules: Sequence[Mapping[str, Any]]) -> str:
    return sha256_json(ordered_rules(rules))


def validate_dictionary(
    value: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    """Validate structure, then usability on the declared model."""

    payload = dict(load_json(value, "pronunciation dictionary"))
    payload["schema_version"] = PRONUNCIATION_DICTIONARY_VERSION
    payload.pop("artifact_hash", None)
    stamp_artifact_hash(payload)

    errors = _schema_errors(payload)
    if errors:
        raise PronunciationDictionaryError(errors)

    errors = _rule_errors(payload.get("rules") or [], str(payload.get("model_id") or ""))
    if errors:
        raise PronunciationDictionaryError(errors)
    return payload


def _matches(target: str, text: str) -> list[str]:
    """Whole-token matches of ``target`` in ``text``, with surrounding context."""

    pattern = re.compile(rf"(?<!\w){re.escape(target)}(?!\w)", re.IGNORECASE)
    found: list[str] = []
    for match in pattern.finditer(text):
        start = max(0, match.start() - 32)
        end = min(len(text), match.end() + 32)
        found.append(text[start:end].replace("\n", " ").strip())
    return found


def preview(
    dictionary: Mapping[str, Any] | str | Path,
    script_text: str,
) -> dict[str, Any]:
    """Report where each rule fires in a real script, before paying for a take.

    A rule that matches nothing is dead weight. A bare-word rule that matches far
    more often than expected is the "Korean won" trap — it will also fire on
    "he won the race".
    """

    payload = validate_dictionary(dictionary)
    rules = ordered_rules(payload.get("rules") or [])

    report: list[dict[str, Any]] = []
    consumed: list[tuple[int, int]] = []
    for rule in rules:
        target = str(rule.get("string_to_replace"))
        hits = _matches(target, script_text)
        report.append(
            {
                "string_to_replace": target,
                "type": rule.get("type"),
                "match_count": len(hits),
                "samples": hits[:3],
            }
        )

    unmatched = [entry["string_to_replace"] for entry in report if entry["match_count"] == 0]
    return {
        "rule_count": len(rules),
        "matched_rule_count": sum(1 for entry in report if entry["match_count"]),
        "unmatched_rules": unmatched,
        "total_matches": sum(entry["match_count"] for entry in report),
        "rules": report,
    }


def needs_sync(dictionary: Mapping[str, Any]) -> bool:
    """True when local rules differ from what was last pushed."""

    return rules_hash(dictionary.get("rules") or []) != dictionary.get("synced_rules_hash")


def compile_sync_request(
    dictionary: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    """Produce the request body and endpoint. Performs no network call."""

    payload = validate_dictionary(dictionary)
    rules = ordered_rules(payload.get("rules") or [])
    dictionary_id = payload.get("dictionary_id")

    body: dict[str, Any] = {"rules": rules}
    if dictionary_id:
        endpoint = ADD_RULES_ENDPOINT.format(dictionary_id=dictionary_id)
    else:
        endpoint = CREATE_ENDPOINT
        body["name"] = payload.get("name")

    return {
        "method": "POST",
        "endpoint": endpoint,
        "body": body,
        "rule_count": len(rules),
        "needs_sync": needs_sync(payload),
        "rules_hash": rules_hash(rules),
    }


def record_sync_result(
    dictionary: Mapping[str, Any] | str | Path,
    *,
    dictionary_id: str,
    version_id: str,
    output_path: str | Path,
) -> dict[str, Any]:
    """Persist the provider ids and mark the current rules as synced."""

    payload = validate_dictionary(dictionary)
    payload["dictionary_id"] = str(dictionary_id)
    payload["version_id"] = str(version_id)
    payload["synced_rules_hash"] = rules_hash(payload.get("rules") or [])
    payload.pop("artifact_hash", None)
    stamp_artifact_hash(payload)

    path = write_artifact(Path(output_path), payload)
    return {
        "path": str(path),
        "dictionary_id": payload["dictionary_id"],
        "version_id": payload["version_id"],
        "rule_count": len(payload.get("rules") or []),
        "needs_sync": needs_sync(payload),
    }


def add_rules(
    dictionary: Mapping[str, Any] | str | Path,
    new_rules: Sequence[Mapping[str, Any]],
    *,
    output_path: str | Path,
) -> dict[str, Any]:
    """Append corrections. A rule reusing a target is reported as an override."""

    payload = validate_dictionary(dictionary)
    existing = {str(rule.get("string_to_replace")): rule for rule in payload.get("rules") or []}
    overrides: list[str] = []
    added: list[str] = []

    merged = list(payload.get("rules") or [])
    for rule in new_rules:
        target = str(rule.get("string_to_replace") or "")
        if target in existing:
            overrides.append(target)
            merged = [r for r in merged if str(r.get("string_to_replace")) != target]
        else:
            added.append(target)
        merged.append(dict(rule))

    payload["rules"] = merged
    validated = validate_dictionary(payload)
    path = write_artifact(Path(output_path), validated)
    return {
        "path": str(path),
        "added": added,
        "overridden": overrides,
        "rule_count": len(validated["rules"]),
        "needs_sync": needs_sync(validated),
    }
