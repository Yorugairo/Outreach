"""Deterministic editorial-motion contracts for narration-led documentaries.

The compiler accepts explicit shot decisions and binds them to canonical word
timings.  It never decides what the edit should mean and never receives raw
renderer paths.  Remotion executes the resulting asset-ID-only plan.
"""

from __future__ import annotations

import copy
import json
import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.generated_block_images import (
    GeneratedBlockImageError,
    validate_timestamped_plate_plan,
)


EDITORIAL_MOTION_PLAN_VERSION = "editorial_motion_plan.v1"
EDITORIAL_PACING_RECIPE_VERSION = "editorial_pacing_recipe.v1"
_HASH_RE = re.compile(r"^[a-f0-9]{64}$")
_SAFE_ID_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
_EMPTY_ACTIONS = {"", "none", "hold", "static"}
_ALIGNMENT_ARTICLES = {"a", "an", "the"}
_ALIGNMENT_TOKEN_ALIASES = {
    "travelling": "traveling",
    "travelled": "traveled",
    "organisation": "organization",
    "programme": "program",
}
_JOURNEY_TERMS = (
    "travel", "travelling", "traveled", "travelled", "entered", "arrived",
    "arrival", "journey", "route", "crossed", "across", "moved", "moving",
)
_LOCATION_TERMS = (
    ("japan", "Japan"),
    ("brazil", "Brazil"),
    ("belém", "Belém"),
    ("belem", "Belém"),
    ("rio", "Rio de Janeiro"),
    ("americas", "the Americas"),
)
_ACADEMIC_TERMS = ("institution", "school", "teacher", "teaching", "education", "classroom", "record")
_MARTIAL_TERMS = ("judo", "jiu-jitsu", "jujutsu", "martial", "technique", "contest", "practice", "training")
_SCENIC_TERMS = ("port", "harbor", "river", "sea", "ship", "street", "coast", "weather")
_EVIDENCE_TERMS = ("record", "source", "evidence", "scholarship", "document", "accounts differ")
_LIST_TRIGGERS = (
    "acquires", "includes", "include", "contains", "contained", "carried",
    "carry", "has", "have", "ask", "asking", "deciding", "through", "emphasize",
)


class EditorialMotionError(ValueError):
    """Raised when editorial timing or renderer instructions fail closed."""

    def __init__(self, errors: Sequence[str] | str) -> None:
        self.errors = [str(errors)] if isinstance(errors, str) else list(errors)
        super().__init__("; ".join(self.errors))


def _load(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EditorialMotionError(f"{label} could not be read: {exc}") from exc
    if not isinstance(payload, dict):
        raise EditorialMotionError(f"{label} must be an object")
    return payload


def _schema(name: str) -> Mapping[str, Any]:
    path = Path(__file__).resolve().parents[2] / "configs" / name
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EditorialMotionError(f"unable to load {name}: {exc}") from exc
    return payload


def _without_hash(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: copy.deepcopy(value) for key, value in payload.items() if key != "artifact_hash"}


def _artifact_hash(payload: Mapping[str, Any], label: str, *, required: bool = True) -> str:
    declared = str(payload.get("artifact_hash") or "").casefold()
    if not declared:
        if required:
            raise EditorialMotionError(f"{label} is missing artifact_hash")
        return canonical_sha256(payload)
    actual = canonical_sha256(_without_hash(payload))
    if declared != actual:
        raise EditorialMotionError(f"{label} artifact_hash is stale")
    return declared


def _schema_errors(payload: Mapping[str, Any], schema_name: str) -> list[str]:
    validator = Draft7Validator(_schema(schema_name))
    return [
        f"{'.'.join(str(item) for item in error.absolute_path) or '$'}: {error.message}"
        for error in sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))
    ]


def build_default_pacing_recipe() -> dict[str, Any]:
    core: dict[str, Any] = {
        "schema_version": EDITORIAL_PACING_RECIPE_VERSION,
        "id": "history-documentary-restrained-v1",
        "preferred_shot_duration_s": [1.8, 5.5],
        "maximum_shot_duration_s": 6.0,
        "max_consecutive_same_scale": 2,
        "max_consecutive_moving_shots": 2,
        "max_information_surfaces": 0,
        "max_non_evidence_prop_layers": 1,
        "motion_density": "restrained",
        "transition_policy": "hard_cuts_default",
        "chapter_reset_policy": "paper_reset",
        "provider_motion_policy": "shot_level_exception_only",
        "reference_policy": "abstract_structure_only",
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def validate_editorial_pacing_recipe(
    value: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    payload = _load(value, "editorial pacing recipe")
    errors = _schema_errors(payload, "editorial_pacing_recipe.schema.json")
    if errors:
        raise EditorialMotionError(errors)
    low, high = (float(item) for item in payload["preferred_shot_duration_s"])
    if low > high:
        errors.append("preferred_shot_duration_s must be ordered low to high")
    if float(payload["maximum_shot_duration_s"]) < high:
        errors.append("maximum_shot_duration_s must not be below the preferred range")
    try:
        _artifact_hash(payload, "editorial pacing recipe")
    except EditorialMotionError as exc:
        errors.extend(exc.errors)
    if errors:
        raise EditorialMotionError(errors)
    return payload


def _word_records(value: Mapping[str, Any] | Sequence[Mapping[str, Any]] | str | Path) -> list[dict[str, Any]]:
    if isinstance(value, (str, Path)):
        payload: Any = _load(value, "canonical word timings")
    else:
        payload = value
    raw_words: Any = payload.get("words") if isinstance(payload, Mapping) else payload
    if not isinstance(raw_words, Sequence) or isinstance(raw_words, (str, bytes, bytearray)):
        raise EditorialMotionError("canonical word timings require a words array")
    words: list[dict[str, Any]] = []
    previous_end = -1.0
    for index, raw in enumerate(raw_words):
        if not isinstance(raw, Mapping):
            raise EditorialMotionError(f"words[{index}] must be an object")
        text = str(raw.get("w") or raw.get("word") or "").strip()
        try:
            start = float(raw["start_s"])
            end = float(raw["end_s"])
        except (KeyError, TypeError, ValueError) as exc:
            raise EditorialMotionError(f"words[{index}] has invalid timing") from exc
        if not text or start < 0 or end <= start or start + 1e-6 < previous_end:
            raise EditorialMotionError(f"words[{index}] is empty, reversed, or overlaps")
        words.append({"w": text, "start_s": start, "end_s": end})
        previous_end = end
    if not words:
        raise EditorialMotionError("canonical word timings may not be empty")
    return words


def _asset_ids(value: Mapping[str, Any] | Sequence[str]) -> tuple[set[str], str]:
    if isinstance(value, Mapping):
        raw_assets = value.get("assets", value)
        if isinstance(raw_assets, Mapping):
            ids = {str(item) for item in raw_assets}
        elif isinstance(raw_assets, Sequence):
            ids = {
                str(item.get("id") or "")
                for item in raw_assets
                if isinstance(item, Mapping)
            }
        else:
            raise EditorialMotionError("asset map must contain assets")
        declared = str(value.get("artifact_hash") or "").casefold()
        if declared:
            asset_hash = _artifact_hash(value, "asset map")
        else:
            asset_hash = canonical_sha256(value)
    else:
        ids = {str(item) for item in value}
        asset_hash = canonical_sha256(sorted(ids))
    if not ids or "" in ids or any(_SAFE_ID_RE.fullmatch(item) is None for item in ids):
        raise EditorialMotionError("asset map contains invalid asset IDs")
    return ids, asset_hash


def _asset_kinds(value: Mapping[str, Any] | Sequence[str]) -> dict[str, str]:
    """Return the locally declared media kind for assets represented as records.

    Older compact asset maps intentionally contain only IDs, so absence of a
    kind means no media-specific constraint is inferred.
    """

    if not isinstance(value, Mapping):
        return {}
    raw_assets = value.get("assets", value)
    if not isinstance(raw_assets, Sequence) or isinstance(raw_assets, (str, bytes)):
        return {}
    return {
        str(item.get("id") or ""): str(item.get("kind") or "").casefold()
        for item in raw_assets
        if isinstance(item, Mapping) and str(item.get("id") or "")
    }


def _transition(raw: Any, *, default_reason: str) -> dict[str, Any]:
    item = dict(raw) if isinstance(raw, Mapping) else {"kind": str(raw or "hard_cut")}
    item.setdefault("reason", default_reason)
    item.setdefault("duration_s", 0.0)
    kind = str(item.get("kind") or "")
    if kind == "crossfade":
        if not item.get("time_or_place_change") or float(item.get("duration_s") or 0) <= 0:
            raise EditorialMotionError("crossfade requires duration and time_or_place_change=true")
    elif kind == "match_cut" and not str(item.get("motif_id") or ""):
        raise EditorialMotionError("match_cut requires motif_id")
    elif kind == "hard_cut":
        item["duration_s"] = 0.0
    return item


def _camera(raw: Any, duration: float) -> dict[str, Any]:
    item = dict(raw) if isinstance(raw, Mapping) else {"kind": "locked"}
    kind = str(item.get("kind") or "locked")
    item.setdefault("easing", "smoothstep")
    item.setdefault("direction", "toward_focal_point")
    if kind == "locked":
        item.update(
            {
                "amount": 0.0,
                "hold_in_s": duration,
                "move_s": 0.0,
                "hold_out_s": 0.0,
            }
        )
        return item
    item.setdefault("amount", 0.018)
    item.setdefault("hold_in_s", min(0.25, duration * 0.15))
    item.setdefault("hold_out_s", 0.0 if kind == "cut_on_motion" else min(0.4, duration * 0.2))
    item.setdefault("move_s", max(0.0, duration - float(item["hold_in_s"]) - float(item["hold_out_s"])))
    total = sum(float(item[field]) for field in ("hold_in_s", "move_s", "hold_out_s"))
    if not math.isclose(total, duration, abs_tol=1e-4):
        raise EditorialMotionError("camera hold/move/settle phases must equal shot duration")
    if float(item["amount"]) <= 0:
        raise EditorialMotionError("moving camera requires a positive amount")
    if kind != "cut_on_motion" and float(item["hold_out_s"]) <= 0:
        raise EditorialMotionError("moving camera requires a settle before the cut")
    return item


def _rectangles_overlap(first: Mapping[str, Any], second: Mapping[str, Any]) -> bool:
    first_x = float(first.get("x") or 0)
    first_y = float(first.get("y") or 0)
    first_right = first_x + float(first.get("width") or 0)
    first_bottom = first_y + float(first.get("height") or 0)
    second_x = float(second.get("x") or 0)
    second_y = float(second.get("y") or 0)
    second_right = second_x + float(second.get("width") or 0)
    second_bottom = second_y + float(second.get("height") or 0)
    return (
        first_x < second_right
        and first_right > second_x
        and first_y < second_bottom
        and first_bottom > second_y
    )


def _placement_errors(layer: Mapping[str, Any], *, label: str) -> list[str]:
    """Validate authored support and exclusion geometry when a layer opts in.

    Legacy plans remain valid without placement metadata. New character work can
    declare the plane beneath a figure and the objects it cannot overlap, so a
    layout cannot silently strand a person on cargo, furniture, or a document.
    """

    placement = layer.get("placement")
    if not isinstance(placement, Mapping):
        return []
    layout = layer.get("layout")
    if not isinstance(layout, Mapping):
        return [f"{label}.placement requires a bounded layout"]
    errors: list[str] = []
    support = placement.get("support_plane")
    foot_anchor = placement.get("foot_anchor")
    if not isinstance(support, Mapping) or not isinstance(foot_anchor, Mapping):
        return [f"{label}.placement requires a support_plane and foot_anchor"]
    support_x = float(support.get("x") or 0)
    support_y = float(support.get("y") or 0)
    support_right = support_x + float(support.get("width") or 0)
    support_bottom = support_y + float(support.get("height") or 0)
    if support_right > 1 or support_bottom > 1:
        errors.append(f"{label}.placement support_plane escapes the frame")
    foot_x = float(layout.get("x") or 0) + float(layout.get("width") or 0) * float(foot_anchor.get("x") or 0)
    foot_y = float(layout.get("y") or 0) + float(layout.get("height") or 0) * float(foot_anchor.get("y") or 0)
    if not (support_x <= foot_x <= support_right and support_y <= foot_y <= support_bottom):
        errors.append(f"{label}.placement foot anchor is outside support_plane")
    for index, zone in enumerate(placement.get("exclusion_zones") or []):
        if not isinstance(zone, Mapping):
            continue
        zone_right = float(zone.get("x") or 0) + float(zone.get("width") or 0)
        zone_bottom = float(zone.get("y") or 0) + float(zone.get("height") or 0)
        if zone_right > 1 or zone_bottom > 1:
            errors.append(f"{label}.placement.exclusion_zones[{index}] escapes the frame")
        if _rectangles_overlap(layout, zone):
            errors.append(
                f"{label}.placement overlaps exclusion zone {str(zone.get('id') or index)!r}"
            )
    return errors


def _semantic_plan_checks(payload: Mapping[str, Any], *, known_asset_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    shots = list(payload.get("shots") or [])
    cursor = 0.0
    seen_ids: set[str] = set()
    previous_word_end = -1
    previous_asset_ids: set[str] = set()
    seen_sound_effects: dict[str, str] = {}
    for index, shot in enumerate(shots):
        label = f"shots[{index}]"
        shot_id = str(shot.get("shot_id") or "")
        if shot_id in seen_ids:
            errors.append(f"{label}.shot_id is duplicated")
        seen_ids.add(shot_id)
        start = float(shot.get("start_s") or 0)
        duration = float(shot.get("duration_s") or 0)
        if not math.isclose(start, cursor, abs_tol=1e-4):
            errors.append(f"{label} creates a timing gap or overlap")
        cursor = start + duration
        word_range = shot.get("word_range") or {}
        first_word = int(word_range.get("start_index", -1))
        last_word = int(word_range.get("end_index", -1))
        if first_word != previous_word_end + 1 or last_word < first_word:
            errors.append(f"{label}.word_range is not contiguous")
        previous_word_end = last_word
        camera = shot.get("camera") or {}
        phases = sum(float(camera.get(field) or 0) for field in ("hold_in_s", "move_s", "hold_out_s"))
        if not math.isclose(phases, duration, abs_tol=1e-4):
            errors.append(f"{label}.camera phases do not equal duration")
        if camera.get("kind") == "locked" and (
            float(camera.get("amount") or 0) != 0 or float(camera.get("move_s") or 0) != 0
        ):
            errors.append(f"{label}.locked camera may not move")
        if camera.get("kind") not in {"locked", "cut_on_motion"} and float(camera.get("hold_out_s") or 0) <= 0:
            errors.append(f"{label}.moving camera must settle")
        has_subject = str(shot.get("subject_action") or "").casefold() not in _EMPTY_ACTIONS
        has_ambient = bool(shot.get("ambient_actions"))
        has_information = str(shot.get("information_reveal") or "").casefold() not in _EMPTY_ACTIONS
        current_asset_ids = {
            str(layer.get("asset_id") or "")
            for layer in shot.get("layers") or []
            if str(layer.get("asset_id") or "")
        }
        has_asset_addition = bool(current_asset_ids - previous_asset_ids)
        if not (has_asset_addition or has_subject or has_ambient or has_information):
            removed_assets = previous_asset_ids - current_asset_ids
            reason = "; removing assets alone is not a visual event" if removed_assets else ""
            errors.append(
                f"{label} has no positive visual event: add a relevant asset, subject action, "
                f"localized ambient action, or information reveal{reason}"
            )
        previous_asset_ids = current_asset_ids
        transition = shot.get("transition_out") or {}
        if transition.get("kind") == "crossfade" and not transition.get("time_or_place_change"):
            errors.append(f"{label}.crossfade lacks a time/place change")
        if transition.get("kind") == "match_cut" and not transition.get("motif_id"):
            errors.append(f"{label}.match_cut lacks a motif")
        if known_asset_ids is not None:
            for layer in shot.get("layers") or []:
                if str(layer.get("asset_id") or "") not in known_asset_ids:
                    errors.append(f"{label} references an unknown asset ID")
                errors.extend(_placement_errors(layer, label=label))
        else:
            for layer in shot.get("layers") or []:
                errors.extend(_placement_errors(layer, label=label))
        for layer_index, layer in enumerate(shot.get("layers") or []):
            if not isinstance(layer, Mapping) or not isinstance(layer.get("timing"), Mapping):
                continue
            timing = layer["timing"]
            exit_at = float(timing.get("exit_at_s") or 0)
            exit_duration = float(timing.get("exit_duration_s") or 0)
            effect_duration = float(timing.get("exit_effect_duration_s") or exit_duration)
            if exit_at + max(exit_duration, effect_duration) > duration + 1e-4:
                errors.append(f"{label}.layers[{layer_index}].timing escapes the shot duration")
        for effect_index, effect in enumerate(shot.get("sound_effects") or []):
            if not isinstance(effect, Mapping):
                continue
            effect_label = f"{label}.sound_effects[{effect_index}]"
            effect_id = str(effect.get("id") or "")
            effect_hash = str(effect.get("sha256") or "")
            at_s = float(effect.get("at_s") or 0)
            effect_duration = float(effect.get("duration_s") or 0)
            if at_s + effect_duration > duration + 1e-4:
                errors.append(f"{effect_label} escapes the shot duration")
            if _SAFE_ID_RE.fullmatch(effect_id) is None or _HASH_RE.fullmatch(effect_hash) is None:
                errors.append(f"{effect_label} has an invalid ID or SHA-256")
            previous_hash = seen_sound_effects.setdefault(effect_id, effect_hash)
            if previous_hash != effect_hash:
                errors.append(f"{effect_label} reuses {effect_id!r} with a different SHA-256")
        declared_actions = shot.get("required_visual_actions") or []
        action_subjects: set[str] = set()
        for action_index, action in enumerate(declared_actions):
            if not isinstance(action, Mapping):
                errors.append(f"{label}.required_visual_actions[{action_index}] must be an object")
                continue
            subject = str(action.get("subject") or "").strip().casefold()
            if not subject or subject in action_subjects:
                errors.append(f"{label}.required_visual_actions has an empty or duplicate subject")
            action_subjects.add(subject)
        if shot.get("visual_intent") == "journey" and not any(
            isinstance(action, Mapping) and action.get("kind") == "map_cut_in"
            for action in declared_actions
        ):
            errors.append(f"{label}.journey intent requires a map_cut_in action")
    if not math.isclose(cursor, float(payload.get("duration_s") or 0), abs_tol=1e-4):
        errors.append("shot timing does not cover duration_s")
    return errors


def validate_editorial_motion_plan(
    value: Mapping[str, Any] | str | Path,
    *,
    known_asset_ids: Sequence[str] | set[str] | None = None,
) -> dict[str, Any]:
    payload = _load(value, "editorial motion plan")
    errors = _schema_errors(payload, "editorial_motion_plan.schema.json")
    known = set(known_asset_ids) if known_asset_ids is not None else None
    errors.extend(_semantic_plan_checks(payload, known_asset_ids=known))
    try:
        _artifact_hash(payload, "editorial motion plan")
    except EditorialMotionError as exc:
        errors.extend(exc.errors)
    if errors:
        raise EditorialMotionError(errors)
    return payload


def derive_editorial_motion_sample(
    value: Mapping[str, Any] | str | Path,
    *,
    end_s: float,
    known_asset_ids: Sequence[str] | set[str] | None = None,
) -> dict[str, Any]:
    """Derive an immutable review sample ending on an authored cut boundary."""

    plan = validate_editorial_motion_plan(value, known_asset_ids=known_asset_ids)
    if end_s <= 0 or end_s > float(plan["duration_s"]) + 1e-4:
        raise EditorialMotionError("editorial sample end_s escapes the motion plan")
    if not any(
        math.isclose(
            float(shot["start_s"]) + float(shot["duration_s"]),
            end_s,
            abs_tol=1e-4,
        )
        for shot in plan["shots"]
    ):
        raise EditorialMotionError(
            "editorial sample end_s must equal an authored shot boundary"
        )
    selected = [
        copy.deepcopy(dict(shot))
        for shot in plan["shots"]
        if float(shot["start_s"]) + float(shot["duration_s"]) <= end_s + 1e-4
    ]
    if not selected:
        raise EditorialMotionError("editorial sample must contain at least one complete shot")
    actual_end = float(selected[-1]["start_s"]) + float(selected[-1]["duration_s"])
    core = {
        key: copy.deepcopy(item)
        for key, item in plan.items()
        if key not in {"artifact_hash", "duration_s", "shots"}
    }
    core["duration_s"] = round(actual_end, 6)
    core["shots"] = selected
    sample = {**core, "artifact_hash": canonical_sha256(core)}
    return validate_editorial_motion_plan(sample, known_asset_ids=known_asset_ids)


def compile_editorial_motion_plan(
    *,
    storyboard: Mapping[str, Any] | str | Path,
    beat_plan: Mapping[str, Any] | str | Path,
    narration_plan: Mapping[str, Any] | str | Path,
    audio_manifest: Mapping[str, Any] | str | Path,
    word_timings: Mapping[str, Any] | Sequence[Mapping[str, Any]] | str | Path,
    pacing_recipe: Mapping[str, Any] | str | Path,
    shot_specs: Sequence[Mapping[str, Any]],
    scene_bundles: Sequence[Mapping[str, Any]],
    scene_flow_graph: Mapping[str, Any],
    asset_map: Mapping[str, Any] | Sequence[str],
    source_end_s: float | None = None,
) -> dict[str, Any]:
    """Compile explicit shot decisions against canonical word timings."""

    story = _load(storyboard, "storyboard")
    beats = _load(beat_plan, "editorial beat plan")
    narration = _load(narration_plan, "history narration")
    audio = _load(audio_manifest, "canonical audio manifest")
    recipe = validate_editorial_pacing_recipe(pacing_recipe)
    words = _word_records(word_timings)
    asset_ids, asset_map_hash = _asset_ids(asset_map)
    asset_kinds = _asset_kinds(asset_map)
    errors: list[str] = []

    storyboard_hash = canonical_sha256(story)
    if narration.get("source_storyboard_hash") != storyboard_hash:
        errors.append("history narration does not match the storyboard hash")
    if narration.get("narration_hash") != audio.get("narration_hash"):
        errors.append("canonical audio narration hash does not match history narration")
    if audio.get("status") != "ready":
        errors.append("canonical audio is not ready")
    if beats.get("schema_version") != "editorial_beat_plan.v1":
        errors.append("beat_plan must use editorial_beat_plan.v1")
    if beats.get("source_storyboard_hash") != storyboard_hash:
        errors.append("editorial beat plan does not match the storyboard hash")
    try:
        beat_plan_hash = _artifact_hash(beats, "editorial beat plan")
    except EditorialMotionError as exc:
        errors.extend(exc.errors)
        beat_plan_hash = "0" * 64
    try:
        _artifact_hash(narration, "history narration")
    except EditorialMotionError as exc:
        errors.extend(exc.errors)
    try:
        audio_manifest_hash = _artifact_hash(audio, "canonical audio manifest")
    except EditorialMotionError as exc:
        errors.extend(exc.errors)
        audio_manifest_hash = "0" * 64
    scene_hashes: list[str] = []
    for index, bundle in enumerate(scene_bundles):
        try:
            scene_hashes.append(_artifact_hash(bundle, f"scene bundle {index}"))
        except EditorialMotionError as exc:
            errors.extend(exc.errors)
    if not scene_hashes:
        errors.append("at least one validated scene bundle is required")
    try:
        flow_hash = _artifact_hash(scene_flow_graph, "scene flow graph")
    except EditorialMotionError as exc:
        errors.extend(exc.errors)
        flow_hash = "0" * 64
    if errors:
        raise EditorialMotionError(errors)
    if not shot_specs:
        raise EditorialMotionError("shot_specs may not be empty")

    def required_word_index(spec: Mapping[str, Any], key: str, index: int) -> int:
        value = (spec.get("word_range") or {}).get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            raise EditorialMotionError(
                f"shot_specs[{index}].word_range.{key} must be an integer"
            )
        return value

    first_word = required_word_index(shot_specs[0], "start_index", 0)
    final_word = required_word_index(shot_specs[-1], "end_index", len(shot_specs) - 1)
    if first_word < 0 or final_word >= len(words):
        raise EditorialMotionError("shot word ranges escape canonical word timings")
    source_start = words[first_word]["start_s"]
    selected_end = float(source_end_s) if source_end_s is not None else words[final_word]["end_s"]
    if selected_end < words[final_word]["end_s"]:
        raise EditorialMotionError("source_end_s cuts off the final selected word")
    if selected_end > float(audio.get("duration_s") or 0) + 1e-4:
        raise EditorialMotionError("selected audio interval exceeds the canonical audio duration")
    duration_total = selected_end - source_start
    if duration_total <= 0:
        raise EditorialMotionError("selected audio interval must be positive")

    shots: list[dict[str, Any]] = []
    previous_end_index = first_word - 1
    for index, raw_spec in enumerate(shot_specs):
        spec = copy.deepcopy(dict(raw_spec))
        start_index = required_word_index(spec, "start_index", index)
        end_index = required_word_index(spec, "end_index", index)
        if start_index != previous_end_index + 1 or end_index < start_index or end_index >= len(words):
            raise EditorialMotionError(f"shot_specs[{index}].word_range is not contiguous")
        shot_absolute_start = source_start if index == 0 else words[start_index]["start_s"]
        next_absolute_start = selected_end
        if index + 1 < len(shot_specs):
            next_index = required_word_index(shot_specs[index + 1], "start_index", index + 1)
            if next_index < 0 or next_index >= len(words):
                raise EditorialMotionError(
                    f"shot_specs[{index + 1}].word_range escapes canonical word timings"
                )
            next_absolute_start = words[next_index]["start_s"]
        duration = next_absolute_start - shot_absolute_start
        if duration <= 0:
            raise EditorialMotionError(f"shot_specs[{index}] has non-positive derived duration")
        if duration > float(recipe["maximum_shot_duration_s"]) + 1e-4:
            raise EditorialMotionError(
                f"shot_specs[{index}] exceeds the pacing maximum of "
                f"{float(recipe['maximum_shot_duration_s']):.3f} seconds"
            )
        layers = [copy.deepcopy(dict(layer)) for layer in spec.get("layers") or []]
        if not layers:
            raise EditorialMotionError(f"shot_specs[{index}] requires layers")
        for layer in layers:
            asset_id = str(layer.get("asset_id") or "")
            if asset_id not in asset_ids:
                raise EditorialMotionError(f"shot_specs[{index}] references an unknown asset ID")
            if (
                asset_kinds.get(asset_id) == "archival_portrait"
                and str(layer.get("role") or "") == "world"
                and not isinstance(layer.get("layout"), Mapping)
            ):
                raise EditorialMotionError(
                    f"shot_specs[{index}] archival portrait {asset_id!r} must declare a contained layout; "
                    "a full-bleed world layer crops portrait evidence"
                )
        information_surface = spec.get("information_surface")
        if information_surface is not None:
            if not isinstance(information_surface, Mapping):
                raise EditorialMotionError(f"shot_specs[{index}].information_surface must be an object")
            surface_asset_id = str(information_surface.get("surface_asset_id") or "")
            if surface_asset_id and surface_asset_id not in {
                str(layer.get("asset_id") or "") for layer in layers
            }:
                raise EditorialMotionError(
                    f"shot_specs[{index}].information_surface references an asset outside the shot"
                )
        camera = _camera(spec.get("camera"), duration)
        shot = {
            "shot_id": str(spec.get("shot_id") or f"editorial-shot-{index + 1:03d}"),
            "parent_beat_ids": list(spec.get("parent_beat_ids") or []),
            "parent_scene_bundle_id": str(spec.get("parent_scene_bundle_id") or ""),
            "start_s": round(shot_absolute_start - source_start, 6),
            "duration_s": round(duration, 6),
            "word_range": {"start_index": start_index - first_word, "end_index": end_index - first_word},
            "narration_excerpt": " ".join(word["w"] for word in words[start_index : end_index + 1]),
            "purpose": str(spec.get("purpose") or "explain"),
            "shot_scale": str(spec.get("shot_scale") or "medium"),
            "focal_point": copy.deepcopy(spec.get("focal_point") or {"x": 0.5, "y": 0.5}),
            "layers": layers,
            "subject_action": str(spec.get("subject_action") or "none"),
            "ambient_actions": list(spec.get("ambient_actions") or []),
            "sound_effects": [
                copy.deepcopy(dict(effect))
                for effect in spec.get("sound_effects") or []
                if isinstance(effect, Mapping)
            ],
            "information_reveal": str(spec.get("information_reveal") or "none"),
            "camera": camera,
            "transition_in": _transition(spec.get("transition_in"), default_reason="shot entry"),
            "transition_out": _transition(spec.get("transition_out"), default_reason="narration boundary"),
            "audio_bridge": str(spec.get("audio_bridge") or "continuous_narration"),
            "provider_motion": copy.deepcopy(
                spec.get("provider_motion")
                or {"requirement": "none", "fallback": "local_layer_motion"}
            ),
            "overlay_ids": list(spec.get("overlay_ids") or []),
            "uniqueness_signature": str(spec.get("uniqueness_signature") or ""),
        }
        if spec.get("visual_intent") is not None:
            shot["visual_intent"] = str(spec["visual_intent"])
        if spec.get("required_visual_actions") is not None:
            shot["required_visual_actions"] = [
                copy.deepcopy(dict(action))
                for action in spec["required_visual_actions"]
                if isinstance(action, Mapping)
            ]
        if information_surface is not None:
            shot["information_surface"] = copy.deepcopy(dict(information_surface))
        shots.append(shot)
        previous_end_index = end_index

    core: dict[str, Any] = {
        "schema_version": EDITORIAL_MOTION_PLAN_VERSION,
        "source_storyboard_hash": storyboard_hash,
        "source_beat_plan_hash": beat_plan_hash,
        "scene_bundle_hashes": scene_hashes,
        "scene_flow_graph_hash": flow_hash,
        "asset_map_hash": asset_map_hash,
        "audio_manifest_hash": audio_manifest_hash,
        "pacing_recipe_hash": recipe["artifact_hash"],
        "duration_s": round(duration_total, 6),
        "source_start_s": round(source_start, 6),
        "shots": shots,
        "provider_calls": 0,
        "revision_only": True,
    }
    plan = {**core, "artifact_hash": canonical_sha256(core)}
    return validate_editorial_motion_plan(plan, known_asset_ids=asset_ids)


def _normalized_tokens(value: str) -> list[str]:
    """Normalize narration text for deterministic, punctuation-insensitive joins."""

    tokens = [
        re.sub(r"[^a-z0-9]", "", token)
        for token in re.findall(r"\S+", str(value or "").casefold())
    ]
    return [_ALIGNMENT_TOKEN_ALIASES.get(token, token) for token in tokens if token]


def _timestamped_groups(blocks: Sequence[Mapping[str, Any]]) -> list[list[dict[str, Any]]]:
    """Keep consecutive plates for one narration excerpt together.

    Each plate remains a separate shot, but grouping lets the compiler map the
    repeated visual continuations onto the one matching span of spoken words.
    """

    groups: list[list[dict[str, Any]]] = []
    for raw in blocks:
        block = copy.deepcopy(dict(raw))
        excerpt = " ".join(str(block.get("narration_excerpt") or "").split())
        if not excerpt:
            raise EditorialMotionError("timestamped plate block narration_excerpt is required")
        if groups and " ".join(
            str(groups[-1][0].get("narration_excerpt") or "").split()
        ) == excerpt:
            groups[-1].append(block)
        else:
            groups.append([block])
    return groups


def _find_phrase_start(
    words: Sequence[Mapping[str, Any]],
    phrase_tokens: Sequence[str],
    *,
    cursor: int,
    group_index: int,
) -> tuple[int, int]:
    """Resolve an authored excerpt to the next exact canonical word span.

    A failure is intentional: a visual plate must not be silently connected to
    a different narration passage merely because durations happen to line up.
    """

    if not phrase_tokens:
        raise EditorialMotionError(f"timestamped narration group {group_index} is empty")
    canonical = [
        (index, token)
        for index, word in enumerate(words)
        for token in _normalized_tokens(str(word.get("w") or ""))
        if token not in _ALIGNMENT_ARTICLES and index >= cursor
    ]
    phrase = [token for token in phrase_tokens if token not in _ALIGNMENT_ARTICLES]
    if not phrase:
        raise EditorialMotionError(
            f"timestamped narration group {group_index} contains only ignorable articles"
        )
    last_start = len(canonical) - len(phrase)
    for start in range(0, last_start + 1):
        if [token for _, token in canonical[start : start + len(phrase)]] == phrase:
            first = canonical[start][0]
            leading = [
                token
                for word in words[cursor:first]
                for token in _normalized_tokens(str(word.get("w") or ""))
            ]
            if leading and all(token in _ALIGNMENT_ARTICLES for token in leading):
                first = cursor
            return first, canonical[start + len(phrase) - 1][0]
    excerpt = " ".join(phrase)
    raise EditorialMotionError(
        f"timestamped narration group {group_index} cannot be resolved at canonical word {cursor}: {excerpt!r}"
    )


def _weighted_word_ranges(
    start_index: int,
    end_index: int,
    blocks: Sequence[Mapping[str, Any]],
    *,
    group_index: int,
) -> list[tuple[int, int]]:
    """Split a matched narration span across its one-plate-per-timestamp slots."""

    word_count = end_index - start_index + 1
    if word_count < len(blocks):
        raise EditorialMotionError(
            f"timestamped narration group {group_index} has {len(blocks)} plates but only {word_count} spoken words"
        )
    weights = [float(item.get("duration_s") or 0) for item in blocks]
    if any(weight <= 0 for weight in weights):
        raise EditorialMotionError(
            f"timestamped narration group {group_index} has a non-positive planned duration"
        )
    total = sum(weights)
    ranges: list[tuple[int, int]] = []
    cursor = start_index
    accumulated = 0.0
    for index, weight in enumerate(weights):
        remaining_blocks = len(weights) - index - 1
        if index == len(weights) - 1:
            next_cursor = end_index + 1
        else:
            accumulated += weight
            desired = start_index + round(word_count * accumulated / total)
            minimum = cursor + 1
            maximum = end_index + 1 - remaining_blocks
            next_cursor = min(max(desired, minimum), maximum)
        ranges.append((cursor, next_cursor - 1))
        cursor = next_cursor
    return ranges


def _sentence_word_range(
    words: Sequence[Mapping[str, Any]], start_index: int, end_index: int
) -> tuple[int, int]:
    """Expand a timed fragment to its narrated sentence without guessing prose."""

    start = start_index
    while start > 0 and not re.search(r"[.!?][\"')\]]*$", str(words[start - 1].get("w") or "")):
        start -= 1
    end = end_index
    while end < len(words) - 1 and not re.search(r"[.!?][\"')\]]*$", str(words[end].get("w") or "")):
        end += 1
    return start, end


def _first_action_word_index(
    words: Sequence[Mapping[str, Any]], action: Mapping[str, str]
) -> int | None:
    """Locate an explicit action subject in the contextual sentence."""

    subject_tokens = _normalized_tokens(str(action.get("subject") or ""))
    if not subject_tokens:
        return None
    tokens = [_normalized_tokens(str(word.get("w") or "")) for word in words]
    flattened = [item[0] if item else "" for item in tokens]
    for index in range(0, len(flattened) - len(subject_tokens) + 1):
        if flattened[index : index + len(subject_tokens)] == subject_tokens:
            return index
    return None


def _contextual_visual_intent_and_actions(
    words: Sequence[Mapping[str, Any]], start_index: int, end_index: int
) -> tuple[str, list[dict[str, str]]]:
    """Classify each narrated sentence which overlaps a timed fragment.

    A slot may end at a sentence boundary.  Treating its following sentence as
    part of the same context lets a later enumeration mask an earlier one;
    evaluate each sentence independently, then keep only actions whose spoken
    subject starts inside this slot.
    """

    sentence_ranges: list[tuple[int, int]] = []
    cursor = start_index
    while cursor <= end_index:
        sentence_range = _sentence_word_range(words, cursor, cursor)
        if not sentence_ranges or sentence_ranges[-1] != sentence_range:
            sentence_ranges.append(sentence_range)
        cursor = sentence_range[1] + 1

    actions: list[dict[str, str]] = []
    intents: list[str] = []
    for sentence_start, sentence_end in sentence_ranges:
        sentence_words = words[sentence_start : sentence_end + 1]
        sentence = " ".join(str(word["w"]) for word in sentence_words)
        intent, contextual_actions = _visual_intent_and_actions(sentence)
        intents.append(intent)
        for action in contextual_actions:
            relative_index = _first_action_word_index(sentence_words, action)
            if relative_index is None:
                continue
            action_index = sentence_start + relative_index
            if start_index <= action_index <= end_index:
                actions.append(action)
    if any(action["kind"] == "map_cut_in" for action in actions):
        return "journey", actions
    primary_intent = intents[0] if intents else "explanation"
    if primary_intent == "explanation":
        primary_intent = next((intent for intent in intents if intent != "explanation"), primary_intent)
    return primary_intent, actions


def analyze_timestamped_semantic_coverage(
    *,
    timestamped_plate_plan: Mapping[str, Any] | str | Path,
    word_timings: Mapping[str, Any] | Sequence[Mapping[str, Any]] | str | Path,
) -> dict[str, Any]:
    """Report exact narration intervals that an inherited plate plan omits.

    A visual schedule may not be retimed proportionally across prose it was
    never written to depict.  This analysis keeps the original plate groups
    bound to their matching canonical narration and turns every uncovered word
    range into explicit, generation-required semantic slots.  Callers must
    select assets for those slots before an editorial plan can be rendered.
    """

    plates = _load(timestamped_plate_plan, "timestamped plate plan")
    validate_timestamped_plate_plan(plates)
    words = _word_records(word_timings)
    blocks = sorted(
        [dict(item) for item in plates.get("blocks") or [] if isinstance(item, Mapping)],
        key=lambda item: int(item.get("order") or 0),
    )
    groups = _timestamped_groups(blocks)
    cursor = 0
    resolved: list[dict[str, Any]] = []
    uncovered_ranges: list[tuple[int, int]] = []
    for group_index, group in enumerate(groups, start=1):
        first_word, last_word = _find_phrase_start(
            words,
            _normalized_tokens(str(group[0].get("narration_excerpt") or "")),
            cursor=cursor,
            group_index=group_index,
        )
        if group_index == 1 and first_word != 0:
            raise EditorialMotionError(
                f"timestamped narration begins at canonical word {first_word}, not the opening word"
            )
        if first_word > cursor:
            uncovered_ranges.append((cursor, first_word - 1))
        for block, (start_index, end_index) in zip(
            group,
            _weighted_word_ranges(
                first_word,
                last_word,
                group,
                group_index=group_index,
            ),
            strict=True,
        ):
            resolved.append(
                {
                    "block_id": str(block.get("block_id") or ""),
                    "order": int(block.get("order") or 0),
                    "word_range": {"start_index": start_index, "end_index": end_index},
                }
            )
        cursor = last_word + 1
    if cursor < len(words):
        uncovered_ranges.append((cursor, len(words) - 1))

    needed_slots: list[dict[str, Any]] = []
    for gap_index, (start_index, end_index) in enumerate(uncovered_ranges, start=1):
        # Break a prose gap at word boundaries near four seconds.  This is a
        # prompt/demand artifact, not permission to reuse a neighboring plate.
        gap_start_s = float(words[start_index]["start_s"])
        slot_start = start_index
        part = 1
        for index in range(start_index + 1, end_index + 2):
            is_end = index == end_index + 1
            elapsed = (
                float(words[index]["start_s"]) - float(words[slot_start]["start_s"])
                if not is_end
                else float(words[end_index]["end_s"]) - float(words[slot_start]["start_s"])
            )
            if not is_end and elapsed < 4.0:
                continue
            slot_end = index - 1 if not is_end else end_index
            spoken = " ".join(str(word["w"]) for word in words[slot_start : slot_end + 1])
            intent, actions = _contextual_visual_intent_and_actions(
                words, slot_start, slot_end
            )
            needed_slots.append(
                {
                    "slot_id": f"semantic-gap-{gap_index:02d}-{part:02d}",
                    "word_range": {"start_index": slot_start, "end_index": slot_end},
                    "start_s": round(float(words[slot_start]["start_s"]), 3),
                    "end_s": round(float(words[slot_end]["end_s"]), 3),
                    "narration_excerpt": spoken,
                    "visual_intent": intent,
                    "required_visual_actions": actions,
                    "asset_status": "generation_required",
                }
            )
            slot_start = index
            part += 1
    core = {
        "schema_version": "timestamped_semantic_coverage.v4",
        "timestamped_plate_plan_hash": plates["artifact_hash"],
        "canonical_word_count": len(words),
        "resolved_plate_count": len(resolved),
        "resolved": resolved,
        "uncovered_slots": needed_slots,
        "uncovered_word_count": sum(
            item["word_range"]["end_index"] - item["word_range"]["start_index"] + 1
            for item in needed_slots
        ),
        "render_ready": not needed_slots,
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def compile_canonical_visual_coverage(
    *,
    audio_manifest: Mapping[str, Any] | str | Path,
    word_timings: Mapping[str, Any] | Sequence[Mapping[str, Any]] | str | Path,
    target_duration_s: float = 4.0,
    minimum_duration_s: float = 1.8,
    maximum_duration_s: float = 6.0,
) -> dict[str, Any]:
    """Create the authoritative image schedule directly from final narration.

    The output intentionally contains no inherited asset IDs.  Every slot needs
    an explicit approved assignment, which prevents a visually attractive old
    plate from being reused merely because it occupies the same clock time.
    """

    audio = _load(audio_manifest, "canonical audio manifest")
    audio_hash = _artifact_hash(audio, "canonical audio manifest")
    if audio.get("status") != "ready":
        raise EditorialMotionError("canonical audio is not ready")
    words = _word_records(word_timings)
    if target_duration_s <= 0 or minimum_duration_s <= 0 or maximum_duration_s < target_duration_s:
        raise EditorialMotionError("canonical visual coverage has invalid duration targets")
    if minimum_duration_s > maximum_duration_s:
        raise EditorialMotionError("canonical visual coverage minimum exceeds maximum")

    def boundary_duration(start: int, end: int) -> float:
        if end >= len(words) - 1:
            return float(words[end]["end_s"]) - float(words[start]["start_s"])
        return float(words[end + 1]["start_s"]) - float(words[start]["start_s"])

    def boundary_quality(index: int) -> int:
        token = str(words[index].get("w") or "")
        if re.search(r"[.!?][\"')\]]*$", token):
            return 0
        if re.search(r"[;:][\"')\]]*$", token):
            return 1
        if token.endswith(","):
            return 2
        return 3

    ranges: list[tuple[int, int]] = []
    start = 0
    while start < len(words):
        candidates = [
            end
            for end in range(start, len(words))
            if minimum_duration_s - 1e-4 <= boundary_duration(start, end) <= maximum_duration_s + 1e-4
        ]
        if not candidates:
            # A final short phrase is valid only when it cannot be joined to
            # the preceding slot without breaking the six-second hard cap.
            candidates = [len(words) - 1]
        end = min(
            candidates,
            key=lambda item: (
                abs(boundary_duration(start, item) - target_duration_s),
                boundary_quality(item),
                item,
            ),
        )
        if end == len(words) - 1 and ranges:
            final_duration = boundary_duration(start, end)
            previous_start, previous_end = ranges[-1]
            combined_duration = float(words[end]["end_s"]) - float(words[previous_start]["start_s"])
            if final_duration < minimum_duration_s and combined_duration <= maximum_duration_s + 1e-4:
                ranges[-1] = (previous_start, end)
                break
        ranges.append((start, end))
        start = end + 1

    slots: list[dict[str, Any]] = []
    for order, (start_index, end_index) in enumerate(ranges, start=1):
        start_s = float(words[start_index]["start_s"])
        end_s = (
            float(words[end_index]["end_s"])
            if end_index == len(words) - 1
            else float(words[end_index + 1]["start_s"])
        )
        intent, actions = _contextual_visual_intent_and_actions(words, start_index, end_index)
        slots.append(
            {
                "slot_id": f"canonical-{order:03d}",
                "word_range": {"start_index": start_index, "end_index": end_index},
                "start_s": round(start_s, 3),
                "end_s": round(end_s, 3),
                "duration_s": round(end_s - start_s, 3),
                "narration_excerpt": " ".join(str(word["w"]) for word in words[start_index : end_index + 1]),
                "visual_intent": intent,
                "required_visual_actions": actions,
                "asset_status": "generation_required",
                "asset_assignment_policy": "explicit_approved_assignment_only",
            }
        )
    core = {
        "schema_version": "canonical_visual_coverage.v11",
        "audio_manifest_hash": audio_hash,
        "narration_hash": str(audio.get("narration_hash") or ""),
        "word_timing_hash": canonical_sha256({"words": words}),
        "duration_s": round(float(audio["duration_s"]), 3),
        "target_duration_s": target_duration_s,
        "minimum_duration_s": minimum_duration_s,
        "maximum_duration_s": maximum_duration_s,
        "slot_count": len(slots),
        "slots": slots,
        "render_ready": False,
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def _timestamped_focal_point(block: Mapping[str, Any]) -> dict[str, float]:
    direction = str(block.get("visual_direction") or "").casefold()
    if "left" in direction and "right" not in direction:
        x = 0.34
    elif "right" in direction and "left" not in direction:
        x = 0.66
    else:
        x = 0.5
    if any(token in direction for token in ("sky", "cloud", "roof", "mountain")):
        y = 0.36
    elif any(token in direction for token in ("floor", "mat", "water", "deck")):
        y = 0.62
    else:
        y = 0.48
    return {"x": x, "y": y}


def _timestamped_scale(block: Mapping[str, Any], *, prior: Sequence[str]) -> str:
    preferred = {
        "artifact_cold_open": "wide",
        "archival_portrait": "medium_detail",
        "document_quote_closeup": "insert",
        "migration_map_timeline": "wide",
        "lineage_graph": "medium",
        "concept_mechanics_cutaway": "medium_detail",
        "chapter_cta": "wide",
    }.get(str(block.get("function") or ""), "medium")
    if len(prior) >= 2 and prior[-1] == preferred and prior[-2] == preferred:
        cycle = ("wide", "medium", "medium_detail", "close", "insert")
        return next(scale for scale in cycle if scale != preferred)
    return preferred


def _enumerated_items(excerpt: str) -> list[str]:
    """Return explicit enumerations, never a generic noun scrape.

    Lists may follow their enumerating verb (``carried skills, names, ...``)
    or form the grammatical subject (``Theaters, demonstrations, ... put``).
    In both cases a real comma-separated enumeration is required before the
    planner schedules per-item visual actions.
    """

    normalized = " ".join(str(excerpt or "").split())
    lowered = normalized.casefold()

    def split_items(tail: str) -> list[str]:
        tail = tail.split(".", 1)[0].strip(" ,")
        if "," not in tail:
            return []
        items = [
            item.strip(" ,")
            for item in re.split(r",\s*(?:(?:and|or)\s+)?|\s+(?:and|or)\s+", tail)
            if item.strip(" ,")
        ]
        return items if len(items) >= 2 else []

    # A parallel-clause list is editorially meaningful even though its items
    # are short actions rather than nouns: ``a student can …, a teacher can
    # …, and memory can …``. Require a modal in every comma-separated clause
    # so ordinary prose cannot become a noun-per-cut scrape.
    parallel_clauses = [
        clause.strip(" ,.")
        for clause in re.split(r",\s*(?:and\s+)?", normalized)
        if clause.strip(" ,.")
    ]
    if len(parallel_clauses) >= 2 and all(
        re.search(
            r"\b(?:can|could|may|might|will|would|must|should)\s+\w+",
            clause,
            flags=re.IGNORECASE,
        )
        for clause in parallel_clauses
    ):
        return parallel_clauses

    # These patterns name deliberate alternative contexts or uses. They are
    # not a noun scraper: an actual comma-separated enumeration is still
    # required before the planner creates per-item visual actions.
    for pattern in (
        r"\b(?:entered|enter)\s+(?P<tail>[^.]+)",
        r"\bused\s+(?:to|for)\s+(?P<tail>[^.]+)",
        r"\b(?:show|shows)\s+why\s+(?P<tail>.+?)\s+\b(?:can|could|will|may|must|should)\b",
    ):
        match = re.search(pattern, normalized, flags=re.IGNORECASE)
        if match:
            items = split_items(match.group("tail"))
            if items:
                return items

    # Research narration often inventories social roles with an explicit
    # identifying verb: ``studies identify teachers, fighters, and networks
    # that ...``. The relative clause is not another item. Check it after
    # more specific contextual forms such as ``used to ... identify ...``.
    # This remains a named inventory with commas, not a noun-per-cut scrape.
    identified_list = re.search(
        r"\b(?:identify|identifies|identified)\s+(?P<tail>.+?)(?:\s+\b(?:that|which|who)\b|[.;]|$)",
        normalized,
        flags=re.IGNORECASE,
    )
    if identified_list:
        items = split_items(identified_list.group("tail"))
        if items:
            return items

    # A subject-led list matters just as much as a verb-led list for editorial
    # cadence: e.g. ``Theaters, demonstrations, challenges, and lessons put
    # ...`` or ``performances, institutions, promotion, and nationalism
    # helped distinguish ...``. Stop at its first governing verb; a plain
    # sentence cannot match because ``split_items`` still insists on a
    # comma-separated enumeration.
    subject_list = re.search(
        r"^(?P<tail>[^.]+?)\s+\b(?:put|puts|shape|shapes|shaped|influence|influences|"
        r"influenced|make|makes|made|became|become|were|are|was|is|carried|carry|"
        r"included|include|moved|move|arrived|arrive|help|helps|helped)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if subject_list:
        subject_tail = subject_list.group("tail")
        # A temporal lead-in can precede the actual enumerated subject:
        # ``Scholarship locates a phase ... when performances, institutions,
        # promotion, and nationalism helped ...``.  The temporal clause is
        # framing, not a list item, so retain only the subject after it.
        subject_tail = re.sub(
            r"^.*?\b(?:when|while)\s+",
            "",
            subject_tail,
            count=1,
            flags=re.IGNORECASE,
        )
        items = split_items(subject_tail)
        if items:
            return items

    for trigger in _LIST_TRIGGERS:
        marker = f"{trigger} "
        position = lowered.find(marker)
        if position < 0:
            continue
        tail = normalized[position + len(marker) :].split(".", 1)[0].strip(" ,")
        if trigger == "through" and ", and " not in tail.casefold() and tail.count(",") < 2:
            continue
        items = split_items(tail)
        if items:
            return items
    return []


def _visual_intent_and_actions(excerpt: str) -> tuple[str, list[dict[str, str]]]:
    """Classify the asset family and required actions for an audio-timed beat."""

    lowered = str(excerpt or "").casefold()
    actions: list[dict[str, str]] = []
    locations = [label for needle, label in _LOCATION_TERMS if needle in lowered]
    has_journey = bool(locations) and any(term in lowered for term in _JOURNEY_TERMS)
    if has_journey:
        actions.extend({"kind": "map_cut_in", "subject": location} for location in dict.fromkeys(locations))
    for item in _enumerated_items(excerpt):
        actions.append({"kind": "list_item_popout", "subject": item})
    unique_actions: list[dict[str, str]] = []
    seen_subjects: set[str] = set()
    for action in actions:
        subject = action["subject"].casefold()
        if subject not in seen_subjects:
            unique_actions.append(action)
            seen_subjects.add(subject)
    has_list = any(action["kind"] == "list_item_popout" for action in unique_actions)
    if re.search(r"\b(?:18|19|20)\d{2}\b", lowered):
        return "evidence", unique_actions
    if has_list and any(term in lowered for term in _ACADEMIC_TERMS):
        return "academic", unique_actions
    if has_list and any(term in lowered for term in _MARTIAL_TERMS):
        return "martial", unique_actions
    if has_journey:
        return "journey", unique_actions
    if any(term in lowered for term in _EVIDENCE_TERMS):
        return "evidence", unique_actions
    if any(term in lowered for term in _ACADEMIC_TERMS):
        return "academic", unique_actions
    if any(term in lowered for term in _MARTIAL_TERMS):
        return "martial", unique_actions
    if any(term in lowered for term in _SCENIC_TERMS):
        return "scenic", unique_actions
    if "instead" in lowered or "not " in lowered:
        return "transition", unique_actions
    return "explanation", unique_actions


def compile_timestamped_editorial_motion_plan(
    *,
    timestamped_plate_plan: Mapping[str, Any] | str | Path,
    asset_map: Mapping[str, Any] | str | Path,
    audio_manifest: Mapping[str, Any] | str | Path,
    word_timings: Mapping[str, Any] | Sequence[Mapping[str, Any]] | str | Path,
    pacing_recipe: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    """Bind every approved timestamped plate to the canonical narration.

    The plate schedule is the visual timebase and canonical ElevenLabs word
    timings are the audio timebase.  The compiler verifies authored excerpts
    still occur in order, then proportionally maps every scheduled plate onto
    continuous narration word boundaries.  It never turns unplanned narration
    into an extended static hold or substitutes a legacy asset.
    """

    try:
        plates = validate_timestamped_plate_plan(timestamped_plate_plan)
    except GeneratedBlockImageError as exc:
        raise EditorialMotionError(exc.errors) from exc
    assets_payload = _load(asset_map, "timestamped plate asset map")
    asset_ids, asset_map_hash = _asset_ids(assets_payload)
    audio = _load(audio_manifest, "canonical audio manifest")
    recipe = validate_editorial_pacing_recipe(pacing_recipe)
    words = _word_records(word_timings)
    errors: list[str] = []
    try:
        audio_manifest_hash = _artifact_hash(audio, "canonical audio manifest")
    except EditorialMotionError as exc:
        errors.extend(exc.errors)
        audio_manifest_hash = "0" * 64
    if audio.get("status") != "ready":
        errors.append("canonical audio is not ready")
    if float(audio.get("duration_s") or 0) + 1e-4 < words[-1]["end_s"]:
        errors.append("canonical audio duration cuts off its final word timing")
    raw_assets = assets_payload.get("assets")
    records = (
        [dict(item) for item in raw_assets if isinstance(item, Mapping)]
        if isinstance(raw_assets, Sequence) and not isinstance(raw_assets, (str, bytes, bytearray))
        else []
    )
    by_slot: dict[str, str] = {}
    for record in records:
        metadata = record.get("metadata")
        slot_id = str(metadata.get("coverage_slot_id") or "") if isinstance(metadata, Mapping) else ""
        asset_id = str(record.get("id") or record.get("asset_id") or "")
        if not slot_id:
            continue
        if slot_id in by_slot:
            errors.append(f"timestamped asset map duplicates coverage slot {slot_id!r}")
        if asset_id not in asset_ids or record.get("render_eligible") is not True:
            errors.append(f"timestamped asset for slot {slot_id!r} is not render eligible")
        metadata_plan_hash = str(metadata.get("timestamped_plate_plan_hash") or "") if isinstance(metadata, Mapping) else ""
        if metadata_plan_hash != plates["artifact_hash"]:
            errors.append(f"timestamped asset for slot {slot_id!r} has a stale plate-plan hash")
        by_slot[slot_id] = asset_id
    blocks = sorted(
        [dict(item) for item in plates.get("blocks") or [] if isinstance(item, Mapping)],
        key=lambda item: int(item.get("order") or 0),
    )
    expected_slots = [str((block.get("coverage_slot_ids") or [""])[0]) for block in blocks]
    if len(blocks) != int(plates.get("plate_count") or 0):
        errors.append("timestamped plate count does not match its blocks")
    if set(expected_slots) != set(by_slot) or len(by_slot) != len(expected_slots):
        missing = sorted(set(expected_slots) - set(by_slot))
        unexpected = sorted(set(by_slot) - set(expected_slots))
        if missing:
            errors.append("timestamped asset map is missing slots: " + ", ".join(missing))
        if unexpected:
            errors.append("timestamped asset map has unexpected slots: " + ", ".join(unexpected))
    if errors:
        raise EditorialMotionError(errors)

    semantic_coverage = analyze_timestamped_semantic_coverage(
        timestamped_plate_plan=plates,
        word_timings=words,
    )
    uncovered = list(semantic_coverage.get("uncovered_slots") or [])
    if uncovered:
        examples = ", ".join(
            f"{item['slot_id']} ({item['start_s']:.3f}-{item['end_s']:.3f}s)"
            for item in uncovered[:3]
        )
        raise EditorialMotionError(
            "timestamped plate plan leaves canonical narration uncovered; "
            "create and approve semantic plates before rendering: " + examples
        )

    specs: list[dict[str, Any]] = []
    scales: list[str] = []
    ranges_by_order = {
        int(item["order"]): (
            int(item["word_range"]["start_index"]),
            int(item["word_range"]["end_index"]),
        )
        for item in semantic_coverage["resolved"]
    }
    for block in blocks:
        order = int(block.get("order") or 0)
        start_index, end_index = ranges_by_order[order]
        slot_id = str((block.get("coverage_slot_ids") or [""])[0])
        asset_id = by_slot[slot_id]
        scale = _timestamped_scale(block, prior=scales)
        scales.append(scale)
        use_push = order % 5 == 0
        camera: dict[str, Any] = (
            {"kind": "push_settle", "amount": 0.01, "direction": "toward_focal_point"}
            if use_push
            else {"kind": "locked"}
        )
        transition_reason = "new timestamped primary plate"
        spoken_excerpt = " ".join(word["w"] for word in words[start_index : end_index + 1])
        visual_intent, required_actions = _visual_intent_and_actions(spoken_excerpt)
        specs.append(
            {
                "shot_id": f"timestamped-motion-{order:03d}",
                "word_range": {"start_index": start_index, "end_index": end_index},
                "visual_intent": visual_intent,
                "required_visual_actions": required_actions,
                "parent_beat_ids": [str(block.get("block_id") or f"plate-{order:03d}")],
                "parent_scene_bundle_id": "timestamped-original-plates",
                "purpose": "hook" if order == 1 else "explain",
                "shot_scale": scale,
                "focal_point": _timestamped_focal_point(block),
                "layers": [{"asset_id": asset_id, "role": "world", "action": "locked"}],
                "subject_action": "none",
                "ambient_actions": [],
                "information_reveal": "none",
                "camera": camera,
                "transition_in": {"kind": "hard_cut", "reason": transition_reason},
                "transition_out": {"kind": "hard_cut", "reason": transition_reason},
                "audio_bridge": "continuous_narration",
                "provider_motion": {"requirement": "none", "fallback": "locked_hold"},
                "overlay_ids": [],
                "uniqueness_signature": f"timestamped:{order:03d}:{slot_id}:{scale}:{camera['kind']}",
            }
        )

    story_core = {
        "schema_version": "timestamped_editorial_storyboard_binding.v1",
        "timestamped_plate_plan_hash": plates["artifact_hash"],
        "coverage_plan_hash": str(plates.get("coverage_plan_hash") or ""),
        "asset_map_hash": asset_map_hash,
        "audio_manifest_hash": audio_manifest_hash,
    }
    story_hash = canonical_sha256(story_core)
    narration_core = {
        "schema_version": "history_narration.v1",
        "source_storyboard_hash": story_hash,
        "narration_hash": str(audio.get("narration_hash") or ""),
        "segments": [
            {"segment_id": "timestamped-master", "text": " ".join(word["w"] for word in words)}
        ],
    }
    narration = {**narration_core, "artifact_hash": canonical_sha256(narration_core)}
    beat_core = {
        "schema_version": "editorial_beat_plan.v1",
        "source_storyboard_hash": story_hash,
        "duration_s": float(audio["duration_s"]),
        "beat_count": len(specs),
        "beats": [
            {"beat_id": spec["parent_beat_ids"][0], "narration_excerpt": spec["shot_id"]}
            for spec in specs
        ],
    }
    beats = {**beat_core, "artifact_hash": canonical_sha256(beat_core)}
    bundle_core = {
        "schema_version": "scene_bundle.v1",
        "id": "timestamped-original-plates",
        "timestamped_plate_plan_hash": plates["artifact_hash"],
    }
    bundle = {**bundle_core, "artifact_hash": canonical_sha256(bundle_core)}
    flow_core = {
        "schema_version": "scene_flow_graph.v1",
        "id": "timestamped-original-plates-flow",
        "timestamped_plate_plan_hash": plates["artifact_hash"],
        "asset_map_hash": asset_map_hash,
    }
    flow = {**flow_core, "artifact_hash": canonical_sha256(flow_core)}
    compiled = compile_editorial_motion_plan(
        storyboard=story_core,
        beat_plan=beats,
        narration_plan=narration,
        audio_manifest=audio,
        word_timings=words,
        pacing_recipe=recipe,
        shot_specs=specs,
        scene_bundles=[bundle],
        scene_flow_graph=flow,
        asset_map=assets_payload,
        source_end_s=float(audio["duration_s"]),
    )
    overlong = [
        str(shot["shot_id"])
        for shot in compiled["shots"]
        if float(shot["duration_s"]) > 6.0 + 1e-4
    ]
    if overlong:
        raise EditorialMotionError(
            "timestamped editorial shots exceed the 6-second visual-hold ceiling: "
            + ", ".join(overlong)
        )
    return compiled


__all__ = [
    "EDITORIAL_MOTION_PLAN_VERSION",
    "EDITORIAL_PACING_RECIPE_VERSION",
    "EditorialMotionError",
    "build_default_pacing_recipe",
    "analyze_timestamped_semantic_coverage",
    "compile_canonical_visual_coverage",
    "compile_editorial_motion_plan",
    "compile_timestamped_editorial_motion_plan",
    "derive_editorial_motion_sample",
    "validate_editorial_motion_plan",
    "validate_editorial_pacing_recipe",
]
