"""Provider-neutral character-builder contract for Google Flow.

The pack is an operator-facing prompt and reference plan.  It is deliberately
not a render manifest: Flow outputs stay quarantined until a human reviews the
character sheet and promotes a content-hashed asset into the job manifest.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft7Validator

from content.video_engine.src.services.history_contracts import canonical_sha256


FLOW_CHARACTER_PACK_VERSION = "flow_character_pack.v1"
FLOW_CHARACTER_PROVIDER = "google_flow"
FLOW_CHARACTER_MODEL = "nano-banana-pro"
_HASH_RE = re.compile(r"^[a-f0-9]{64}$")
_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_PROHIBITED = (
    "in the style of",
    "style of",
    "youtube.com",
    "youtu.be",
    "reference pack",
    "source frame",
    "creator name",
    "copy this image",
)


class FlowCharacterPackError(ValueError):
    """Raised when a Flow character pack is unsafe or incomplete."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors) or "invalid Flow character pack")


def _load(value: Mapping[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FlowCharacterPackError([f"character pack is not valid JSON: {exc}"]) from exc
    if not isinstance(payload, Mapping):
        raise FlowCharacterPackError(["character pack root must be an object"])
    return copy.deepcopy(dict(payload))


def _schema_errors(payload: Mapping[str, Any]) -> list[str]:
    schema_path = Path(__file__).resolve().parents[2] / "configs" / "flow_character_pack.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"character pack schema could not be loaded: {exc}"]
    validator = Draft7Validator(schema)
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    return [
        "schema "
        + (".".join(str(part) for part in error.absolute_path) or "root")
        + f": {error.message}"
        for error in errors
    ]


def validate_flow_character_pack(
    value: Mapping[str, Any] | str | Path,
    *,
    expected_art_bible_hash: str | None = None,
    expected_id: str | None = None,
) -> dict[str, Any]:
    """Validate a planned Flow character pack and return a normalized copy."""

    payload = _load(value)
    errors = _schema_errors(payload)
    if expected_art_bible_hash and payload.get("art_bible_hash") != expected_art_bible_hash:
        errors.append("art_bible_hash is stale")
    if expected_id and payload.get("id") != expected_id:
        errors.append("character pack id is stale")
    if payload.get("builder_surface") not in {None, "character_builder"}:
        errors.append("builder_surface must be character_builder")
    if payload.get("render_eligible") is not False:
        errors.append("character pack must remain non-renderable")
    characters = payload.get("characters") or []
    seen: set[str] = set()
    for index, character in enumerate(characters):
        if not isinstance(character, Mapping):
            continue
        label = f"characters[{index}]"
        identifier = str(character.get("id") or "")
        if identifier in seen:
            errors.append(f"{label}.id duplicates {identifier!r}")
        seen.add(identifier)
        prompt = str(character.get("prompt") or "")
        negative = str(character.get("negative_prompt") or "")
        for field, text in (("prompt", prompt), ("negative_prompt", negative)):
            lowered = text.casefold()
            for term in _PROHIBITED:
                if term in lowered:
                    errors.append(f"{label}.{field} contains prohibited input {term!r}")
        refs = character.get("reference_asset_ids")
        if refs not in (None, []) and not all(isinstance(item, str) and item for item in refs):
            errors.append(f"{label}.reference_asset_ids must be empty until promotion")
        rights = character.get("rights_policy")
        if isinstance(rights, Mapping) and rights.get("label_as_illustration") is not True:
            errors.append(f"{label}.rights_policy must label the output as illustration")
    declared_hash = payload.get("artifact_hash")
    actual_hash = canonical_sha256(payload)
    if declared_hash is not None:
        if not isinstance(declared_hash, str) or not _HASH_RE.fullmatch(declared_hash):
            errors.append("artifact_hash must be a 64-character lowercase SHA-256")
        elif declared_hash != actual_hash:
            errors.append("artifact_hash does not match canonical content")
    if errors:
        raise FlowCharacterPackError(errors)
    return {**payload, "artifact_hash": actual_hash}


def build_flow_character_pack(
    *,
    episode_id: str,
    art_bible_id: str,
    art_bible_hash: str,
    characters: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build and hash a character-builder prompt packet."""

    payload = {
        "schema_version": FLOW_CHARACTER_PACK_VERSION,
        "provider": FLOW_CHARACTER_PROVIDER,
        "model": FLOW_CHARACTER_MODEL,
        "builder_surface": "character_builder",
        "episode_id": episode_id,
        "art_bible_id": art_bible_id,
        "art_bible_hash": art_bible_hash,
        "characters": [copy.deepcopy(dict(item)) for item in characters],
        "workflow": {
            "generate_character_sheet_first": True,
            "operator_review_required": True,
            "ingredients_to_video_requires_approved_reference": True,
            "provider_output_render_eligible": False,
        },
        "render_eligible": False,
    }
    return {**payload, "artifact_hash": canonical_sha256(payload)}


__all__ = [
    "FLOW_CHARACTER_MODEL",
    "FLOW_CHARACTER_PACK_VERSION",
    "FLOW_CHARACTER_PROVIDER",
    "FlowCharacterPackError",
    "build_flow_character_pack",
    "validate_flow_character_pack",
]
