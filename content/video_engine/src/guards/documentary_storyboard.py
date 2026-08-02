"""Fail-closed Storyboard 2.2 checks for History Documentary V4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft7Validator, FormatChecker


DOCUMENTARY_FUNCTIONS = {
    "artifact_cold_open",
    "archival_portrait",
    "illustrated_reconstruction",
    "document_quote_closeup",
    "migration_map_timeline",
    "lineage_graph",
    "concept_mechanics_cutaway",
    "chapter_cta",
}
_PROHIBITED_SCENES = {"StickFigureScene", "BJJActionScene", "CombatScienceScene"}
_PROHIBITED_TEXT = (
    "in the style of",
    "youtube reference pack",
    "consultant outline",
    "http://",
    "https://",
    "source_frame",
    "creator_name",
)
_PROHIBITED_KEYS = {
    "url",
    "source_url",
    "path",
    "source_path",
    "asset_path",
    "study_path",
    "creator",
    "creator_name",
    "source_frame",
    "renderer_prompt",
}


def _load(value: Mapping[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    payload = json.loads(Path(value).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("storyboard root must be an object")
    return payload


def _safe_renderer_value(
    value: Any,
    violations: list[str],
    path: tuple[str, ...] = (),
) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key).casefold().replace("-", "_")
            if key in _PROHIBITED_KEYS:
                violations.append(
                    f"renderer input {'.'.join((*path, str(raw_key)))} is prohibited"
                )
            _safe_renderer_value(child, violations, (*path, str(raw_key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _safe_renderer_value(child, violations, (*path, str(index)))
    elif isinstance(value, str):
        lowered = value.casefold()
        if any(token in lowered for token in _PROHIBITED_TEXT):
            violations.append(
                f"renderer input {'.'.join(path) or '$'} contains prohibited provenance"
            )


def guard(
    storyboard: Mapping[str, Any] | str | Path,
    *,
    schema_path: str | Path | None = None,
) -> tuple[bool, list[str]]:
    try:
        payload = _load(storyboard)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return False, [f"storyboard could not be loaded: {exc}"]
    version = str(payload.get("schema_version") or "")
    path = (
        Path(schema_path)
        if schema_path is not None
        else Path(__file__).resolve().parents[2]
        / "configs"
        / (
            "storyboard_v2_3.schema.json"
            if version == "2.3.0"
            else "storyboard_v2_2.schema.json"
        )
    )
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return False, [f"Storyboard 2.2 schema could not be loaded: {exc}"]
    violations = [
        "schema "
        + (".".join(str(value) for value in error.absolute_path) or "$")
        + f": {error.message}"
        for error in Draft7Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(payload)
    ]
    if violations:
        return False, sorted(violations)

    claims = {str(claim["id"]): claim for claim in payload["claims"]}
    scenes = payload["scenes"]
    scene_ids = {int(scene["scene_id"]) for scene in scenes}
    used_functions: set[str] = set()
    concept_duration = 0.0
    total_duration = 0.0
    treatment_ids: set[str] = set()
    coverage_slot_ids: set[str] = set()
    for scene in scenes:
        scene_id = scene["scene_id"]
        function = str(scene["visual_function"])
        used_functions.add(function)
        total_duration += float(scene["timing"]["target_s"])
        if function == "concept_mechanics_cutaway":
            concept_duration += float(scene["timing"]["target_s"])
        if scene["manim_class"] in _PROHIBITED_SCENES:
            violations.append(
                f"scene {scene_id} uses prohibited History V4 class "
                f"{scene['manim_class']!r}"
            )
        treatment_id = str(scene["visual_treatment_id"])
        if treatment_id in treatment_ids:
            violations.append(
                f"scene {scene_id} repeats visual treatment {treatment_id!r}"
            )
        treatment_ids.add(treatment_id)
        if version == "2.3.0":
            beats = scene.get("visual_beats") or []
            beat_duration = 0.0
            for beat in beats:
                slot_id = str(beat.get("coverage_slot_id") or "")
                if not slot_id or slot_id in coverage_slot_ids:
                    violations.append(
                        f"scene {scene_id} has duplicate or missing coverage_slot_id"
                    )
                coverage_slot_ids.add(slot_id)
                duration = float(beat.get("duration_s") or 0)
                beat_duration += duration
                events = beat.get("micro_events") or []
                event_times = [
                    float(event.get("at_s") or 0)
                    for event in events
                    if isinstance(event, Mapping)
                ]
                if not event_times or event_times[0] != 0:
                    violations.append(
                        f"coverage slot {slot_id!r} must establish at 0 seconds"
                    )
                boundaries = [*event_times, duration]
                if any(
                    later - earlier > 3.0 + 1e-9
                    for earlier, later in zip(boundaries, boundaries[1:])
                ):
                    violations.append(
                        f"coverage slot {slot_id!r} has a static interval over 3 seconds"
                    )
            if abs(beat_duration - float(scene["timing"]["target_s"])) > 0.05:
                violations.append(
                    f"scene {scene_id} visual beat duration does not match narration timing"
                )
        if function == "illustrated_reconstruction" and not str(
            scene.get("illustration_label") or ""
        ).strip():
            violations.append(
                f"scene {scene_id} illustrated reconstruction requires a visible label"
            )
        claim_refs = [str(value) for value in scene["claim_refs"]]
        citation_refs = set(str(value) for value in scene["citation_refs"])
        if scene["act"] != "cta" and not claim_refs:
            violations.append(f"scene {scene_id} has historical narration without a claim")
        allowed_citations: set[str] = set()
        for claim_id in claim_refs:
            claim = claims.get(claim_id)
            if claim is None:
                violations.append(
                    f"scene {scene_id} references unknown claim {claim_id!r}"
                )
                continue
            if claim.get("verified") is not True:
                violations.append(
                    f"scene {scene_id} references unverified claim {claim_id!r}"
                )
            allowed_citations.update(str(value) for value in claim["citation_ids"])
            if claim.get("contested") is True and not str(
                claim.get("qualified_narration") or ""
            ).strip():
                violations.append(
                    f"contested claim {claim_id!r} lacks qualified narration"
                )
        unknown_citations = sorted(citation_refs - allowed_citations)
        if unknown_citations:
            violations.append(
                f"scene {scene_id} uses citations outside its claim set: "
                + ", ".join(unknown_citations)
            )
        _safe_renderer_value(
            {
                "parameters": scene["parameters"],
                "asset_ids": scene["asset_ids"],
                "visual_function": function,
            },
            violations,
            (f"scene-{scene_id}",),
        )

    missing_functions = sorted(DOCUMENTARY_FUNCTIONS - used_functions)
    if missing_functions:
        violations.append(
            "History V4 storyboard is missing documentary functions: "
            + ", ".join(missing_functions)
        )
    cap = float(payload["global_settings"]["concept_mechanics_runtime_cap"])
    if total_duration <= 0:
        violations.append("History V4 storyboard duration must be positive")
    elif concept_duration / total_duration > cap + 1e-9:
        violations.append(
            "concept mechanics runtime exceeds "
            f"{cap:.0%} ({concept_duration / total_duration:.1%})"
        )

    for collection_name, derivatives in payload["derivatives"].items():
        for derivative in derivatives:
            missing_scenes = sorted(set(derivative["scene_ids"]) - scene_ids)
            if missing_scenes:
                violations.append(
                    f"{collection_name} {derivative['id']!r} references missing scenes "
                    + ", ".join(str(value) for value in missing_scenes)
                )
            derivative_claims = {
                str(claim_id)
                for scene in scenes
                if scene["scene_id"] in derivative["scene_ids"]
                for claim_id in scene["claim_refs"]
            }
            if set(derivative["claim_ids"]) != derivative_claims:
                violations.append(
                    f"{collection_name} {derivative['id']!r} claim_ids do not "
                    "match its scene claim cluster"
                )
    return not violations, sorted(set(violations))


validate_storyboard = guard


__all__ = [
    "DOCUMENTARY_FUNCTIONS",
    "guard",
    "validate_storyboard",
]
