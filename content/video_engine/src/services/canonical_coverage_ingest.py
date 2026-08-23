"""Flip estimated coverage onto the real render clock.

Provisional coverage times slots from word count over WPM so a board can exist
before anyone pays for synthesis. Once ElevenLabs has actually spoken the script,
that estimate is superseded: this module re-derives every slot boundary from
measured word timings and re-emits the coverage with ``timing_basis: canonical``.

Two guards matter more than the arithmetic:

* **The read must reconcile with the attested script.** The director is already
  forbidden from rewriting narration; a voice take that drifted from the script
  would smuggle the same problem in through the audio door. A re-recorded or
  edited read is rejected, never silently re-timed.
* **Duration comes from the audio, never from word count.** That is the whole
  point of the flip. A slot that measures longer than the coverage contract's 8s
  cap is *reported*, not clamped — clamping would put the plate out of sync with
  the voice, which is the failure the cap exists to prevent.

The estimated artifact is kept alongside rather than overwritten, so the two can
be diffed.
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
from content.video_engine.src.services.provisional_coverage import (
    CANONICAL_TIMING_BASIS,
    EDITORIAL_COVERAGE_VERSION,
)

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _VIDEO_ENGINE_ROOT / "configs"

CANONICAL_AUDIO_SCHEMA = "elevenlabs_canonical_audio.schema.json"
READY_STATUS = "ready"

#: The coverage contract caps a slot at 8s. Measured overruns are reported.
_SLOT_CAP_S = 8.0
_WORD_TOKEN = re.compile(r"[a-z0-9']+")


class CanonicalIngestError(ValueError):
    """The audio is unusable, or the read does not match the attested script."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid canonical audio ingest")


def _tokens(text: str) -> list[str]:
    return _WORD_TOKEN.findall(str(text).casefold())


def _schema_errors(payload: Mapping[str, Any]) -> list[str]:
    schema = load_json(_CONFIG_DIR / CANONICAL_AUDIO_SCHEMA, "canonical audio schema")
    validator = Draft7Validator(schema)
    return [
        "audio" + "".join(f"[{part!r}]" for part in error.absolute_path) + f": {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda e: list(e.absolute_path))
    ]


def flatten_word_timings(
    audio: Mapping[str, Any], *, project_root: str | Path | None = None
) -> list[dict[str, Any]]:
    """One absolute-time word list for the whole take.

    Prefers the master ``words_path`` file when it resolves: it is the single
    authoritative list. Real pilot artifacts carry **overlapping** per-block
    timings — 99 blocks summing to 4,889 entries against a 2,445-word master —
    because blocks repeat words across their boundaries. Reassembling from blocks
    therefore double-counts, so the fallback path deduplicates on word and start
    time.

    Block timings may be block-relative or already absolute; a block whose first
    word starts before the block does is treated as relative and offset.
    """

    if project_root is not None:
        words_path = Path(project_root) / str(audio.get("words_path") or "")
        if words_path.is_file():
            loaded = load_json(words_path, "master word timings")
            master = loaded.get("words") if isinstance(loaded, Mapping) else loaded
            if master:
                return [
                    {
                        "w": str(item.get("w") or ""),
                        "start_s": round(float(item.get("start_s") or 0.0), 3),
                        "end_s": round(float(item.get("end_s") or 0.0), 3),
                    }
                    for item in master
                ]

    words: list[dict[str, Any]] = []
    seen: set[tuple[str, float]] = set()
    for block in sorted(audio.get("blocks") or [], key=lambda b: int(b.get("order") or 0)):
        block_start = float(block.get("start_s") or 0.0)
        timings = list(block.get("word_timings") or [])
        if not timings:
            continue
        first = float(timings[0].get("start_s") or 0.0)
        offset = block_start if first < block_start else 0.0
        for timing in timings:
            entry = {
                "w": str(timing.get("w") or ""),
                "start_s": round(float(timing.get("start_s") or 0.0) + offset, 3),
                "end_s": round(float(timing.get("end_s") or 0.0) + offset, 3),
            }
            key = (entry["w"], entry["start_s"])
            if key in seen:
                continue
            seen.add(key)
            words.append(entry)
    words.sort(key=lambda entry: entry["start_s"])
    return words


def validate_canonical_audio(
    audio: Mapping[str, Any] | str | Path,
    *,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    """Accept only a completed, timed take."""

    payload = dict(load_json(audio, "canonical audio"))

    # Optional hash fields are legitimately absent on the paste lane, which has no
    # storyboard. Real pilot artifacts carry them present-but-empty, which the
    # schema rejects while treating absent as fine — the two mean the same thing,
    # so normalise rather than weaken the schema for every other lane.
    for optional_hash in ("storyboard_hash",):
        if payload.get(optional_hash) == "":
            payload.pop(optional_hash)

    errors = _schema_errors(payload)
    if errors:
        raise CanonicalIngestError(errors)
    if payload.get("status") != READY_STATUS:
        errors.append(
            f"status is {payload.get('status')!r}; canonical timing requires {READY_STATUS!r}"
        )
    if not flatten_word_timings(payload, project_root=project_root):
        errors.append("audio carries no word timings; canonical timing is impossible")
    if errors:
        raise CanonicalIngestError(errors)
    return payload


def reconcile_read_against_script(
    words: Sequence[Mapping[str, Any]], script_text: str
) -> list[str]:
    """The spoken read must be the attested script, in order, verbatim."""

    spoken = [_WORD_TOKEN.findall(str(word.get("w") or "").casefold()) for word in words]
    spoken_flat = [token for group in spoken for token in group]
    expected = _tokens(script_text)

    if spoken_flat == expected:
        return []
    if not expected:
        return ["attested script is empty"]

    limit = min(len(spoken_flat), len(expected))
    diverged = next(
        (i for i in range(limit) if spoken_flat[i] != expected[i]),
        limit,
    )
    context = " ".join(expected[max(0, diverged - 4) : diverged + 4]) or "(start)"
    if diverged < limit:
        return [
            f"the read diverges from the attested script at word {diverged + 1} "
            f"(near: {context!r}); a re-recorded or edited take must be re-attested "
            "rather than silently re-timed"
        ]
    if len(spoken_flat) < len(expected):
        return [
            f"the read stops {len(expected) - len(spoken_flat)} words short of the "
            "attested script"
        ]
    return [
        f"the read adds {len(spoken_flat) - len(expected)} words beyond the attested script"
    ]


def _retime_slots(
    slots: Sequence[Mapping[str, Any]], words: Sequence[Mapping[str, Any]]
) -> tuple[list[dict[str, Any]], list[str]]:
    """Consume the word stream slot by slot, taking measured boundaries."""

    retimed: list[dict[str, Any]] = []
    overruns: list[str] = []
    cursor = 0

    for slot in slots:
        need = len(_tokens(slot.get("narration_excerpt") or ""))
        if need <= 0:
            retimed.append(dict(slot))
            continue

        taken = 0
        start_index = cursor
        while cursor < len(words) and taken < need:
            taken += len(_WORD_TOKEN.findall(str(words[cursor].get("w") or "").casefold()))
            cursor += 1
        if start_index >= len(words):
            overruns.append(f"slot {slot.get('slot_id')!r} has no audio words remaining")
            retimed.append(dict(slot))
            continue

        start_s = float(words[start_index]["start_s"])
        end_s = float(words[min(cursor, len(words)) - 1]["end_s"])
        duration = round(max(end_s - start_s, 0.001), 3)

        updated = dict(slot)
        updated["duration_s"] = duration
        updated["measured_start_s"] = round(start_s, 3)
        updated["measured_end_s"] = round(end_s, 3)
        if duration > _SLOT_CAP_S:
            overruns.append(
                f"slot {slot.get('slot_id')!r} measures {duration}s, over the {_SLOT_CAP_S}s "
                "coverage cap; split the beat rather than clamping the plate"
            )
        retimed.append(updated)

    return retimed, overruns


def compile_canonical_coverage(
    estimated_coverage: Mapping[str, Any] | str | Path,
    *,
    audio: Mapping[str, Any] | str | Path,
    brief: Mapping[str, Any] | str | Path,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    """Re-derive every slot boundary from measured word timings."""

    coverage = dict(load_json(estimated_coverage, "estimated coverage"))
    audio_payload = validate_canonical_audio(audio, project_root=project_root)
    brief_payload = load_json(brief, "director brief")

    words = flatten_word_timings(audio_payload, project_root=project_root)
    script_text = str((brief_payload.get("script") or {}).get("text") or "")
    errors = reconcile_read_against_script(words, script_text)
    if errors:
        raise CanonicalIngestError(errors)

    slots = list(coverage.get("slots") or [])
    if not slots:
        raise CanonicalIngestError(["estimated coverage contains no slots"])
    retimed, overruns = _retime_slots(slots, words)

    payload = dict(coverage)
    payload["schema_version"] = EDITORIAL_COVERAGE_VERSION
    payload["timing_basis"] = CANONICAL_TIMING_BASIS
    payload["slots"] = retimed
    payload["slot_count"] = len(retimed)
    # Duration is the audio's, never a sum of word-count estimates.
    payload["duration_s"] = round(float(audio_payload.get("duration_s") or 0.0), 3)
    payload.pop("artifact_hash", None)
    stamp_artifact_hash(payload)

    payload["_overruns"] = overruns
    return payload


def ingest_canonical_audio(
    estimated_coverage: Mapping[str, Any] | str | Path,
    *,
    audio: Mapping[str, Any] | str | Path,
    brief: Mapping[str, Any] | str | Path,
    output_dir: str | Path,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    """Write ``canonical_coverage.json`` beside the retained estimate."""

    payload = compile_canonical_coverage(
        estimated_coverage, audio=audio, brief=brief, project_root=project_root
    )
    overruns = payload.pop("_overruns", [])
    stamp_artifact_hash(payload)

    path = write_artifact(Path(output_dir) / "canonical_coverage.json", payload)
    return {
        "coverage_path": str(path),
        "coverage_hash": payload["artifact_hash"],
        "timing_basis": payload["timing_basis"],
        "slot_count": payload["slot_count"],
        "duration_s": payload["duration_s"],
        "overrun_count": len(overruns),
        "overruns": overruns,
    }
