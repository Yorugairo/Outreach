"""Paste-lane entry: operator-attested script ingest.

The corpus lane starts from a fact-layer bundle and runs the research gate. A
pasted script has no such provenance, so this lane substitutes an explicit
operator attestation: who asserted the source, what it is, and on what basis the
claims stand. That attestation is required before any artifact is written and is
required again before publish.

Nothing here grants evidence status. Attestation covers the *script*; generated
pixels remain non-evidence under the existing candidate contracts.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.pipeline import V4_1_STAGES
from content.video_engine.src.services.artifact_io import (
    load_json,
    sha256_text,
    stamp_artifact_hash,
    write_artifact,
)

SOURCE_ATTESTATION_VERSION = "source_attestation.v1"
DIRECTOR_BRIEF_VERSION = "director_brief.v1"

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _VIDEO_ENGINE_ROOT / "configs"

#: Stages the paste lane skips. Provenance is asserted, not researched.
RESEARCH_LANE_STAGES = ("validating_research", "awaiting_research_approval")

DEFAULT_WORDS_PER_MINUTE = 140
DEFAULT_SLOT_HOLD_S = 6.0
_MAX_SLOT_HOLD_S = 8.0
_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_WORD_PATTERN = re.compile(r"[^\s]+")


class ScriptIngestError(ValueError):
    """Attestation or script failed validation. Nothing was written."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid script ingest")


def paste_lane_stages() -> list[str]:
    """V4.1 order with the research gate removed, publish gate retained."""

    return [stage for stage in V4_1_STAGES if stage not in RESEARCH_LANE_STAGES]


def _schema(name: str) -> dict[str, Any]:
    return load_json(_CONFIG_DIR / f"{name}.schema.json", f"{name} schema")


def _schema_errors(payload: Mapping[str, Any], name: str) -> list[str]:
    validator = Draft7Validator(_schema(name))
    return [
        f"{name}{''.join(f'[{part!r}]' for part in error.absolute_path)}: {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda e: list(e.absolute_path))
    ]


def word_count(text: str) -> int:
    return len(_WORD_PATTERN.findall(text))


def estimated_duration_s(words: int, words_per_minute: int) -> float:
    """Authoring-time estimate only. Audio remains the render clock."""

    if words_per_minute <= 0:
        raise ScriptIngestError(["words_per_minute must be positive"])
    return round(words / words_per_minute * 60.0, 3)


def build_attestation(
    raw: Mapping[str, Any] | str | Path,
    *,
    script_text: str,
) -> dict[str, Any]:
    """Normalize and validate an operator attestation against the script."""

    payload = dict(load_json(raw, "attestation"))
    payload["schema_version"] = SOURCE_ATTESTATION_VERSION
    payload["script_sha256"] = sha256_text(script_text)
    payload.pop("artifact_hash", None)
    stamp_artifact_hash(payload)

    errors = _schema_errors(payload, "source_attestation")
    if errors:
        raise ScriptIngestError(errors)
    return payload


def _validate_brief_inputs(slug: str, wpm: int, hold_s: float) -> list[str]:
    errors: list[str] = []
    if not _SLUG_PATTERN.fullmatch(slug):
        errors.append("brief_id must be a lowercase hyphenated slug")
    if not 90 <= wpm <= 200:
        errors.append("words_per_minute must be between 90 and 200")
    if not 0 < hold_s <= _MAX_SLOT_HOLD_S:
        errors.append(
            f"target_slot_hold_s must be greater than 0 and at most {_MAX_SLOT_HOLD_S}"
        )
    return errors


def build_brief(
    *,
    brief_id: str,
    title: str,
    lane: str,
    script_text: str,
    attestation: Mapping[str, Any],
    aspect: str = "landscape",
    words_per_minute: int = DEFAULT_WORDS_PER_MINUTE,
    target_slot_hold_s: float = DEFAULT_SLOT_HOLD_S,
) -> dict[str, Any]:
    """Normalize a pasted script into the director's input contract."""

    text = script_text.strip()
    if not text:
        raise ScriptIngestError(["script contains no text"])

    errors = _validate_brief_inputs(brief_id, words_per_minute, target_slot_hold_s)
    if errors:
        raise ScriptIngestError(errors)

    words = word_count(text)
    payload = {
        "schema_version": DIRECTOR_BRIEF_VERSION,
        "brief_id": brief_id,
        "title": title.strip(),
        "lane": lane,
        "aspect": aspect,
        "words_per_minute": words_per_minute,
        "target_slot_hold_s": float(target_slot_hold_s),
        "script": {
            "text": text,
            "word_count": words,
            "estimated_duration_s": estimated_duration_s(words, words_per_minute),
            "sha256": sha256_text(text),
        },
        "attestation_hash": str(attestation["artifact_hash"]),
    }
    stamp_artifact_hash(payload)

    schema_errors = _schema_errors(payload, "director_brief")
    if schema_errors:
        raise ScriptIngestError(schema_errors)
    return payload


def ingest_script(
    *,
    script_path: str | Path,
    attestation: Mapping[str, Any] | str | Path,
    output_dir: str | Path,
    brief_id: str,
    title: str,
    lane: str,
    aspect: str = "landscape",
    words_per_minute: int = DEFAULT_WORDS_PER_MINUTE,
    target_slot_hold_s: float = DEFAULT_SLOT_HOLD_S,
) -> dict[str, Any]:
    """Write ``source_attestation.json`` then ``director_brief.json``.

    Attestation is validated first so a run without provenance leaves no
    artifacts behind.
    """

    path = Path(script_path)
    if not path.is_file():
        raise ScriptIngestError([f"script not found: {path}"])
    script_text = path.read_text(encoding="utf-8")

    attested = build_attestation(attestation, script_text=script_text)
    brief = build_brief(
        brief_id=brief_id,
        title=title,
        lane=lane,
        script_text=script_text,
        attestation=attested,
        aspect=aspect,
        words_per_minute=words_per_minute,
        target_slot_hold_s=target_slot_hold_s,
    )

    out = Path(output_dir)
    attestation_path = write_artifact(out / "source_attestation.json", attested)
    brief_path = write_artifact(out / "director_brief.json", brief)

    return {
        "brief_id": brief["brief_id"],
        "lane": brief["lane"],
        "word_count": brief["script"]["word_count"],
        "estimated_duration_s": brief["script"]["estimated_duration_s"],
        "attestation_path": str(attestation_path),
        "brief_path": str(brief_path),
        "attestation_hash": attested["artifact_hash"],
        "brief_hash": brief["artifact_hash"],
        "stage_order": paste_lane_stages(),
    }
