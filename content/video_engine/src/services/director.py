"""Director: request pack out, validated proposal in.

``content/video_engine/AGENTS.md`` requires every stage to be deterministic and
idempotent from persisted inputs. An LLM called inline would break that. So the
model sits *upstream* of the pipeline: this module emits a request pack, an
external agent answers it, and the validated proposal becomes the persisted
input every downstream stage replays from. Re-running never re-solicits.

The director segments and directs. It may not rewrite. Validation rejects any
proposal whose beat narration does not reconstruct the attested script.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.services.artifact_io import (
    load_json,
    stamp_artifact_hash,
    write_artifact,
)
from content.video_engine.src.services.style_packs import StylePackError, get_pack

DIRECTOR_PROPOSAL_VERSION = "director_proposal.v1"
DIRECTOR_REQUEST_VERSION = "director_request.v1"

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _VIDEO_ENGINE_ROOT / "configs"
_NORMALIZE = re.compile(r"\s+")

def operator_writes_copy(lane: str) -> bool:
    """Read the policy from the style-pack registry — one source of truth.

    Model-written humour is unreliable, so lanes that flag this get structure
    from the director and copy from the operator.
    """

    try:
        return bool(get_pack(lane).get("operator_writes_on_screen_copy", False))
    except StylePackError:
        return False

#: Rules every lane inherits, derived from the 2026-08-22 art-style review.
LANE_RULES: tuple[str, ...] = (
    "Never place text inside a plate. All on-screen typography is composited by "
    "the renderer as real type; propose it in on_screen_text instead.",
    "Carry character identity in silhouette and costume colour, never in facial "
    "features, so face drift cannot break continuity.",
    "narration_text must be copied verbatim from the script in order. Do not "
    "rewrite, summarize, translate, or reorder it.",
)


class DirectorError(ValueError):
    """Proposal failed validation. Nothing was persisted."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid director proposal")


def _normalize(text: str) -> str:
    return _NORMALIZE.sub(" ", text).strip().casefold()


def _proposal_schema() -> dict[str, Any]:
    return load_json(_CONFIG_DIR / "director_proposal.schema.json", "proposal schema")


def _schema_errors(payload: Mapping[str, Any]) -> list[str]:
    validator = Draft7Validator(_proposal_schema())
    return [
        "proposal" + "".join(f"[{part!r}]" for part in error.absolute_path) + f": {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda e: list(e.absolute_path))
    ]


def compile_director_request(
    brief: Mapping[str, Any] | str | Path,
    *,
    style_note: str | None = None,
) -> dict[str, Any]:
    """Emit everything an external agent needs to answer, and nothing else."""

    payload = load_json(brief, "director brief")
    lane = str(payload.get("lane") or "")
    script = dict(payload.get("script") or {})
    hold_s = float(payload.get("target_slot_hold_s") or 6.0)
    estimated = float(script.get("estimated_duration_s") or 0.0)

    request = {
        "schema_version": DIRECTOR_REQUEST_VERSION,
        "brief_hash": str(payload.get("artifact_hash") or ""),
        "lane": lane,
        "aspect": payload.get("aspect"),
        "title": payload.get("title"),
        "script_text": script.get("text"),
        "word_count": script.get("word_count"),
        "estimated_duration_s": estimated,
        "target_slot_hold_s": hold_s,
        "suggested_beat_count": max(1, round(estimated / hold_s)) if hold_s else 1,
        "operator_writes_on_screen_copy": operator_writes_copy(lane),
        "rules": list(LANE_RULES),
        "style_note": style_note,
        "response_schema": _proposal_schema(),
    }
    return stamp_artifact_hash(request)


def _narration_errors(beats: Sequence[Mapping[str, Any]], script_text: str) -> list[str]:
    """The concatenated beats must reconstruct the script exactly."""

    joined = _normalize(" ".join(str(beat.get("narration_text") or "") for beat in beats))
    expected = _normalize(script_text)
    if joined == expected:
        return []
    if joined in expected:
        return ["beats do not cover the whole script; narration is truncated"]
    if expected in joined:
        return ["beats add narration beyond the script"]
    return [
        "beat narration does not reconstruct the attested script — the director "
        "may segment and direct but never rewrite"
    ]


def _copy_errors(beats: Sequence[Mapping[str, Any]], lane: str) -> list[str]:
    errors: list[str] = []
    operator_owns_copy = operator_writes_copy(lane)
    for index, beat in enumerate(beats):
        label = f"beats[{index}]"
        deferred = beat.get("copy_deferred") is True
        text = beat.get("on_screen_text")
        if deferred and text not in (None, ""):
            errors.append(f"{label}.on_screen_text must be null when copy_deferred is true")
        if operator_owns_copy and not deferred and text:
            errors.append(
                f"{label} proposes on-screen copy for lane {lane!r}; this lane "
                "requires copy_deferred so the operator writes it"
            )
    return errors


def _beat_id_errors(beats: Sequence[Mapping[str, Any]]) -> list[str]:
    seen: set[str] = set()
    errors: list[str] = []
    for index, beat in enumerate(beats):
        beat_id = str(beat.get("beat_id") or "")
        if beat_id in seen:
            errors.append(f"beats[{index}].beat_id duplicates {beat_id!r}")
        seen.add(beat_id)
    return errors


def validate_director_proposal(
    proposal: Mapping[str, Any] | str | Path,
    *,
    brief: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    """Validate a proposal against its brief and stamp its artifact hash."""

    brief_payload = load_json(brief, "director brief")
    payload = dict(load_json(proposal, "director proposal"))
    payload["schema_version"] = DIRECTOR_PROPOSAL_VERSION
    payload.pop("artifact_hash", None)
    stamp_artifact_hash(payload)

    errors = _schema_errors(payload)
    if errors:
        raise DirectorError(errors)

    brief_hash = str(brief_payload.get("artifact_hash") or "")
    if payload.get("brief_hash") != brief_hash:
        errors.append("brief_hash does not match the director brief")
    if payload.get("lane") != brief_payload.get("lane"):
        errors.append("lane does not match the director brief")

    beats = list(payload.get("beats") or [])
    script_text = str((brief_payload.get("script") or {}).get("text") or "")
    errors.extend(_narration_errors(beats, script_text))
    errors.extend(_copy_errors(beats, str(payload.get("lane") or "")))
    errors.extend(_beat_id_errors(beats))

    if errors:
        raise DirectorError(errors)
    return payload


def record_director_proposal(
    proposal: Mapping[str, Any] | str | Path,
    *,
    brief: Mapping[str, Any] | str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Persist a validated proposal as the replayable downstream input."""

    validated = validate_director_proposal(proposal, brief=brief)
    path = write_artifact(Path(output_dir) / "director_proposal.json", validated)
    return {
        "proposal_path": str(path),
        "proposal_hash": validated["artifact_hash"],
        "lane": validated["lane"],
        "beat_count": len(validated["beats"]),
        "deferred_copy_beats": sum(
            1 for beat in validated["beats"] if beat.get("copy_deferred") is True
        ),
    }


def load_recorded_proposal(output_dir: str | Path) -> dict[str, Any] | None:
    """Return the persisted proposal so reruns replay instead of re-soliciting."""

    path = Path(output_dir) / "director_proposal.json"
    if not path.is_file():
        return None
    return load_json(path, "director proposal")
