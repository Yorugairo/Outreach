"""Provisional coverage: slot the script before audio exists.

``editorial_coverage`` is normally compiled from word-level audio timings by
``editorial_motion.compile_canonical_visual_coverage``. But an operator must be
able to see a board before paying for synthesis, so this module compiles the
same contract from word count over WPM and marks it ``timing_basis:
"estimated"``.

That artifact is valid for board layout, slot counting and prompt fan-out. It is
**not** valid for render timing — audio remains the clock. ``assert_render_ready``
is the guard every render-timing consumer should call.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.services.artifact_io import (
    load_json,
    stamp_artifact_hash,
    write_artifact,
)

EDITORIAL_COVERAGE_VERSION = "editorial_coverage.v1"
ESTIMATED_TIMING_BASIS = "estimated"
CANONICAL_TIMING_BASIS = "canonical"

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _VIDEO_ENGINE_ROOT / "configs"
_WORD_PATTERN = re.compile(r"[^\s]+")

#: The coverage contract caps a single slot at 8 seconds.
_MAX_SLOT_DURATION_S = 8.0
_MIN_SLOT_DURATION_S = 0.5
_DURATION_TOLERANCE_RATIO = 0.01

_LANE_ARCHETYPES = {
    "stick_explainer": "lofi_stick_figure_comic",
    "cutout_history": "period_comic_block",
    "flat_cartoon_explainer": "lofi_stick_figure_comic",
    "presenter_infographic": "typography_explainer",
    "woodblock": "period_comic_block",
    "whiteboard": "typography_explainer",
}
_CTA_ARCHETYPE = "chapter_card"
_PREFERRED_SOURCE = "original_illustration"
_FALLBACK_SOURCE = "typography"


class ProvisionalCoverageError(ValueError):
    """Coverage could not be compiled or is being used for the wrong purpose."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid provisional coverage")


def assert_render_ready(coverage: Mapping[str, Any]) -> None:
    """Refuse estimated timing wherever the render clock is required."""

    basis = coverage.get("timing_basis", CANONICAL_TIMING_BASIS)
    if basis != CANONICAL_TIMING_BASIS:
        raise ProvisionalCoverageError(
            [
                f"coverage timing_basis is {basis!r}; render timing requires "
                "canonical coverage compiled from audio word timings"
            ]
        )


def _schema_errors(payload: Mapping[str, Any]) -> list[str]:
    schema = load_json(_CONFIG_DIR / "editorial_coverage.schema.json", "coverage schema")
    validator = Draft7Validator(schema)
    return [
        "coverage" + "".join(f"[{part!r}]" for part in error.absolute_path) + f": {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda e: list(e.absolute_path))
    ]


def _words(text: str) -> list[str]:
    return _WORD_PATTERN.findall(text)


def _split_evenly(words: Sequence[str], groups: int) -> list[list[str]]:
    """Partition words into ``groups`` contiguous, near-equal runs."""

    total = len(words)
    if groups <= 1 or total <= 1:
        return [list(words)]
    groups = min(groups, total)
    base, remainder = divmod(total, groups)
    chunks: list[list[str]] = []
    cursor = 0
    for index in range(groups):
        size = base + (1 if index < remainder else 0)
        chunks.append(list(words[cursor : cursor + size]))
        cursor += size
    return chunks


def _slot_duration(word_total: int, words_per_minute: int) -> float:
    raw = word_total / words_per_minute * 60.0
    return round(min(max(raw, _MIN_SLOT_DURATION_S), _MAX_SLOT_DURATION_S), 3)


def _archetype(lane: str, act: str) -> str:
    if act == "cta":
        return _CTA_ARCHETYPE
    return _LANE_ARCHETYPES.get(lane, "typography_explainer")


def _micro_events(beat: Mapping[str, Any], index: int) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = [
        {"at_ratio": 0.0, "kind": "enter", "note": str(beat.get("visual_intent") or "")[:120]}
    ]
    text = beat.get("on_screen_text")
    if text:
        events.append({"at_ratio": 0.25, "kind": "type_in", "note": str(text)[:120]})
    elif beat.get("copy_deferred") is True:
        events.append({"at_ratio": 0.25, "kind": "type_in_deferred", "note": "operator copy"})
    return events


def _build_slot(
    *,
    beat: Mapping[str, Any],
    lane: str,
    part_index: int,
    part_total: int,
    words: Sequence[str],
    words_per_minute: int,
) -> dict[str, Any]:
    beat_id = str(beat.get("beat_id"))
    slot_id = beat_id if part_total == 1 else f"{beat_id}-p{part_index + 1}"
    excerpt = " ".join(words)
    return {
        "slot_id": slot_id,
        "parent_shot_id": beat_id,
        "narration_excerpt": excerpt,
        "semantic_purpose": beat.get("semantic_purpose"),
        "visual_archetype": _archetype(lane, str(beat.get("act") or "")),
        "stock_eligible": False,
        "preferred_visual_source": _PREFERRED_SOURCE,
        "fallback_visual_source": _FALLBACK_SOURCE,
        "search_concepts": [],
        "duration_s": _slot_duration(len(words), words_per_minute),
        "motion_recipe": beat.get("motion_recipe"),
        "micro_events": _micro_events(beat, part_index),
        "uniqueness_signature": f"{lane}:{beat_id}:{part_index}",
        "visual_intent": str(beat.get("visual_intent") or ""),
        "on_screen_text": beat.get("on_screen_text"),
        "copy_deferred": beat.get("copy_deferred") is True,
        "act": beat.get("act"),
    }


def _slots_for_beat(
    beat: Mapping[str, Any],
    *,
    lane: str,
    words_per_minute: int,
    hold_s: float,
) -> list[dict[str, Any]]:
    words = _words(str(beat.get("narration_text") or ""))
    if not words:
        return []
    beat_duration = len(words) / words_per_minute * 60.0
    parts = max(1, math.ceil(beat_duration / hold_s))
    chunks = _split_evenly(words, parts)
    return [
        _build_slot(
            beat=beat,
            lane=lane,
            part_index=index,
            part_total=len(chunks),
            words=chunk,
            words_per_minute=words_per_minute,
        )
        for index, chunk in enumerate(chunks)
    ]


def _cadence(slots: Sequence[Mapping[str, Any]], hold_s: float) -> dict[str, Any]:
    durations = [float(slot["duration_s"]) for slot in slots]
    return {
        "target_hold_s": round(hold_s, 3),
        "min_hold_s": round(min(durations), 3),
        "max_hold_s": round(max(durations), 3),
        "mean_hold_s": round(sum(durations) / len(durations), 3),
    }


def compile_provisional_coverage(
    proposal: Mapping[str, Any] | str | Path,
    *,
    brief: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    """Compile estimated-timing coverage from a validated director proposal."""

    proposal_payload = load_json(proposal, "director proposal")
    brief_payload = load_json(brief, "director brief")

    lane = str(proposal_payload.get("lane") or "")
    words_per_minute = int(brief_payload.get("words_per_minute") or 140)
    hold_s = min(float(brief_payload.get("target_slot_hold_s") or 6.0), _MAX_SLOT_DURATION_S)

    slots: list[dict[str, Any]] = []
    for beat in proposal_payload.get("beats") or []:
        slots.extend(
            _slots_for_beat(beat, lane=lane, words_per_minute=words_per_minute, hold_s=hold_s)
        )
    if not slots:
        raise ProvisionalCoverageError(["proposal produced no coverage slots"])

    duration_s = round(sum(float(slot["duration_s"]) for slot in slots), 3)
    payload = {
        "schema_version": EDITORIAL_COVERAGE_VERSION,
        "source_shot_plan_hash": str(proposal_payload.get("artifact_hash") or ""),
        "source_artifact_kind": "director_proposal",
        "timing_basis": ESTIMATED_TIMING_BASIS,
        "duration_s": duration_s,
        "slot_count": len(slots),
        "cadence": _cadence(slots, hold_s),
        "slots": slots,
    }
    stamp_artifact_hash(payload)

    errors = _schema_errors(payload)
    if errors:
        raise ProvisionalCoverageError(errors)
    return payload


def duration_drift_ratio(
    coverage: Mapping[str, Any], brief: Mapping[str, Any]
) -> float:
    """Relative gap between compiled coverage and the brief's script estimate."""

    expected = float((brief.get("script") or {}).get("estimated_duration_s") or 0.0)
    if expected <= 0:
        return 0.0
    return abs(float(coverage.get("duration_s") or 0.0) - expected) / expected


def compile_and_write(
    proposal: Mapping[str, Any] | str | Path,
    *,
    brief: Mapping[str, Any] | str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Compile, verify total duration against the brief, and persist."""

    brief_payload = load_json(brief, "director brief")
    coverage = compile_provisional_coverage(proposal, brief=brief_payload)
    drift = duration_drift_ratio(coverage, brief_payload)
    if drift > _DURATION_TOLERANCE_RATIO:
        raise ProvisionalCoverageError(
            [
                f"coverage duration {coverage['duration_s']}s drifts {drift:.3%} from "
                f"the brief estimate; tolerance is {_DURATION_TOLERANCE_RATIO:.0%}"
            ]
        )
    path = write_artifact(Path(output_dir) / "provisional_coverage.json", coverage)
    return {
        "coverage_path": str(path),
        "coverage_hash": coverage["artifact_hash"],
        "timing_basis": coverage["timing_basis"],
        "slot_count": coverage["slot_count"],
        "duration_s": coverage["duration_s"],
        "duration_drift_ratio": round(drift, 6),
    }
