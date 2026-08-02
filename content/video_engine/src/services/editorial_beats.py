"""Compile documentary narration scenes into sentence-level editorial cuts.

Storyboard scenes remain evidence-backed narration units.  This derived plan
adds a faster visual clock without fragmenting the approved narration or
changing its claim/citation bindings.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Mapping, Sequence

from content.video_engine.src.services.history_contracts import canonical_sha256


EDITORIAL_BEAT_PLAN_VERSION = "editorial_beat_plan.v1"
_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'])")
_SEMICOLON_BOUNDARY_RE = re.compile(r";\s+")
_CONTRAST_RE = re.compile(r"\s+(but|yet|instead)\s+", re.IGNORECASE)
_CLAUSE_BOUNDARY_RE = re.compile(
    r",\s+|\s+(?:and|while|because|when|with|which)\s+",
    re.IGNORECASE,
)
_WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)

_FUNCTION_ROTATION = (
    "archival_portrait",
    "document_quote_closeup",
    "migration_map_timeline",
    "lineage_graph",
    "illustrated_reconstruction",
    "concept_mechanics_cutaway",
)
_MOTION_ROTATION = (
    "push_in",
    "pan_left",
    "pan_right",
    "lift",
    "pull_back",
)
_RELATIONSHIP_ENTITY_TERMS = (
    "jigoro kano",
    "kodokan",
    "mitsuyo maeda",
    "maeda",
    "soshihiro satake",
    "satake",
    "carlos gracie",
    "jacyntho ferro",
    "george gracie",
    "lotus club",
)
_RELATIONSHIP_VERB_RE = re.compile(
    r"\b(?:established|founded|student|trained|training|taught|teaching|"
    r"teacher|worked with|partnered with|member|joined)\b",
    re.IGNORECASE,
)


class EditorialBeatPlanError(ValueError):
    """Raised when a sentence-level editorial plan cannot be compiled."""


def _supports_relationship(value: str) -> bool:
    lowered = value.casefold()
    entities = {
        entity
        for entity in _RELATIONSHIP_ENTITY_TERMS
        if entity in lowered
    }
    # Avoid counting aliases for the same person as two entities.
    if "jigoro kano" in entities:
        entities.discard("kano")
    if "mitsuyo maeda" in entities:
        entities.discard("maeda")
    if "soshihiro satake" in entities:
        entities.discard("satake")
    return len(entities) >= 2 and _RELATIONSHIP_VERB_RE.search(value) is not None


def _literature_mode(function: str, intent: str) -> str:
    if intent in {"battlefield_legend", "lofi_editorial_aside"}:
        return "lofi_comedy"
    if function in {"archival_portrait", "document_quote_closeup"}:
        return "archive_evidence"
    if function in {
        "illustrated_reconstruction",
        "migration_map_timeline",
        "lineage_graph",
    }:
        return "historical_comic"
    return "lofi_comedy"


def _words(value: str) -> int:
    return max(1, len(_WORD_RE.findall(value)))


def _split_sentences(value: str) -> list[str]:
    text = " ".join(value.split())
    if not text:
        return []
    sentences: list[str] = []
    for sentence in _SENTENCE_BOUNDARY_RE.split(text):
        sentences.extend(
            part.strip()
            for part in _SEMICOLON_BOUNDARY_RE.split(sentence)
            if part.strip()
        )
    return sentences


def _split_contrast(sentence: str) -> list[str]:
    match = _CONTRAST_RE.search(sentence)
    if match is None:
        return [sentence]
    left = sentence[: match.start()].strip()
    right = sentence[match.end() :].strip()
    if _words(left) < 3 or _words(right) < 2:
        return [sentence]
    connector = match.group(1).casefold()
    return [left, f"{connector} {right}"]


def _rebalance_connector(left: str, right: str) -> tuple[str, str]:
    trailing = re.search(
        r"\b(at|from|to|of|in|with|before|after|because|than)$",
        left,
        re.IGNORECASE,
    )
    if trailing is None:
        return left, right
    connector = trailing.group(1)
    return left[: trailing.start()].rstrip(), f"{connector} {right}"


def _split_long_idea(value: str, *, maximum_words: int = 14) -> list[str]:
    if _words(value) <= maximum_words:
        return [value]
    candidates: list[tuple[int, int]] = []
    midpoint = len(value) / 2
    for match in _CLAUSE_BOUNDARY_RE.finditer(value):
        left = value[: match.start()].rstrip(" ,")
        right = value[match.end() :].strip()
        connector = match.group(0).strip(" ,").casefold()
        if connector and not match.group(0).lstrip().startswith(","):
            right = f"{connector} {right}"
        if _words(left) >= 4 and _words(right) >= 4:
            candidates.append((round(abs(match.start() - midpoint)), match.start()))
    if not candidates:
        return [value]
    _, split_at = min(candidates)
    boundary = _CLAUSE_BOUNDARY_RE.search(value, split_at)
    if boundary is None or boundary.start() != split_at:
        return [value]
    left = value[: boundary.start()].rstrip(" ,")
    right = value[boundary.end() :].strip()
    connector = boundary.group(0).strip(" ,").casefold()
    if connector and not boundary.group(0).lstrip().startswith(","):
        right = f"{connector} {right}"
    left, right = _rebalance_connector(left, right)
    return [
        *_split_long_idea(left, maximum_words=maximum_words),
        *_split_long_idea(right, maximum_words=maximum_words),
    ]


def _split_for_timing(value: str) -> list[str]:
    word_matches = list(_WORD_RE.finditer(value))
    if len(word_matches) < 8:
        return [value]
    natural = _split_long_idea(
        value,
        maximum_words=max(5, len(word_matches) // 2),
    )
    if len(natural) > 1:
        return natural
    midpoint = len(word_matches) // 2
    split_at = word_matches[midpoint].start()
    left = value[:split_at].rstrip(" ,")
    right = value[split_at:].strip()
    left, right = _rebalance_connector(left, right)
    if _words(left) < 4 or _words(right) < 4:
        return [value]
    return [left, right]


def _intent_and_function(
    text: str,
    parent_function: str,
    index: int,
) -> tuple[str, str]:
    lowered = text.casefold()
    if any(value in lowered for value in ("battlefield", "samurai war", "warrior legend")):
        return "battlefield_legend", "illustrated_reconstruction"
    if any(value in lowered for value in ("but an institution", "tranquil institution")):
        return "tranquil_institution", "archival_portrait"
    if any(value in lowered for value in ("kodokan", "jigoro kano", "kano's system")):
        return "kodokan_origin", "archival_portrait"
    if any(value in lowered for value in ("terminology", "spelling", "public label", "title of first", "accounts differ")):
        return "document_evidence", "document_quote_closeup"
    if any(
        value in lowered
        for value in (
            "travel",
            "entered brazil",
            "arrival",
            "belém",
            "rio",
            "japan",
            "brazil",
            "americas",
            "regions",
            "international",
        )
    ):
        return "migration_route", "migration_map_timeline"
    if _supports_relationship(text) and any(
        value in lowered
        for value in (
            "network",
            "lineage",
            "student",
            "teacher",
            "intermediaries",
            "community",
            "branches",
            "family tree",
        )
    ):
        return "relationship_network", "lineage_graph"
    if any(
        value in lowered
        for value in (
            "source",
            "evidence",
            "scholarship",
            "record",
            "document",
            "advertised",
        )
    ):
        return "document_evidence", "document_quote_closeup"
    if any(
        value in lowered
        for value in (
            "transformation",
            "adaptation",
            "reorganized",
            "changed",
            "shift",
            "reinvention",
            "remade",
            "transformed",
        )
    ):
        return "concept_transition", "concept_mechanics_cutaway"
    if re.search(r"\b(?:18|19|20)\d{2}\b", lowered):
        return "dated_artifact", "artifact_cold_open"
    if parent_function == "chapter_cta":
        return "chapter_resolution", "chapter_cta"
    function = (
        parent_function
        if parent_function in _FUNCTION_ROTATION
        else _FUNCTION_ROTATION[index % len(_FUNCTION_ROTATION)]
    )
    if function == "lineage_graph" and not _supports_relationship(text):
        return "lofi_editorial_aside", "concept_mechanics_cutaway"
    return f"editorial_{function}", function


def _allocate_duration(total: float, texts: Sequence[str]) -> list[float]:
    if total <= 0:
        raise EditorialBeatPlanError("scene duration must be positive")
    if not texts:
        raise EditorialBeatPlanError("scene narration produced no editorial beats")
    minimum = 1.5
    if total + 1e-9 < minimum * len(texts):
        raise EditorialBeatPlanError(
            "scene duration cannot support 1.5 seconds per editorial beat"
        )
    weights = [_words(text) for text in texts]
    distributable = total - minimum * len(texts)
    weight_total = sum(weights)
    durations = [
        minimum + distributable * weight / weight_total
        for weight in weights
    ]
    durations[-1] += total - sum(durations)
    return durations


def compile_editorial_beat_plan(
    storyboard: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a deterministic sentence/contrast cut plan for History V4."""

    source = storyboard.get("source") or {}
    if (
        storyboard.get("schema_version") not in {"2.2.0", "2.3.0"}
        or not isinstance(source, Mapping)
        or source.get("kind") != "history_episode"
    ):
        raise EditorialBeatPlanError(
            "editorial beat plans require a History V4 Storyboard 2.2/2.3"
        )
    scenes = storyboard.get("scenes")
    if not isinstance(scenes, Sequence) or isinstance(
        scenes,
        (str, bytes, bytearray),
    ):
        raise EditorialBeatPlanError("storyboard scenes must be an array")

    beats: list[dict[str, Any]] = []
    global_start = 0.0
    previous_function = ""
    for scene in scenes:
        if not isinstance(scene, Mapping):
            raise EditorialBeatPlanError("storyboard scenes must be objects")
        if storyboard.get("schema_version") == "2.3.0":
            visual_beats = scene.get("visual_beats")
            if not isinstance(visual_beats, list) or not visual_beats:
                raise EditorialBeatPlanError(
                    f"scene {scene.get('scene_id')} requires visual_beats"
                )
            scene_id = int(scene["scene_id"])
            for item in visual_beats:
                if not isinstance(item, Mapping):
                    raise EditorialBeatPlanError("visual beats must be objects")
                beat_index = len(beats)
                function = str(
                    scene.get("visual_function")
                    or scene.get("visual_type")
                    or "document_quote_closeup"
                )
                visual_source = str(item.get("visual_source") or "")
                intent = f"living_{item.get('semantic_purpose') or 'explanation'}"
                beat = {
                    "beat_id": str(item["coverage_slot_id"]),
                    "coverage_slot_id": str(item["coverage_slot_id"]),
                    "parent_scene_id": scene_id,
                    "chapter_id": str(scene.get("chapter_id") or ""),
                    "narration_excerpt": str(item["narration_excerpt"]),
                    "visual_intent": intent,
                    "visual_source": visual_source,
                    "function": function,
                    "literature_mode": _literature_mode(function, intent),
                    "duration_s": float(item["duration_s"]),
                    "start_s": round(
                        global_start + float(item["parent_offset_s"]), 6
                    ),
                    "parent_offset_s": float(item["parent_offset_s"]),
                    "claim_refs": copy.deepcopy(
                        list(scene.get("claim_refs") or [])
                    ),
                    "citation_refs": copy.deepcopy(
                        list(scene.get("citation_refs") or [])
                    ),
                    "asset_ids": copy.deepcopy(list(item.get("asset_ids") or [])),
                    "motion": str(item["motion_recipe"]),
                    "motion_recipe": str(item["motion_recipe"]),
                    "micro_events": copy.deepcopy(
                        list(item.get("micro_events") or [])
                    ),
                    "transition": str(item.get("transition") or "hard_cut"),
                }
                if function == "illustrated_reconstruction":
                    beat["illustration_label"] = str(
                        scene.get("illustration_label")
                        or "ILLUSTRATION / RECONSTRUCTION"
                    )
                beats.append(beat)
            global_start += float((scene.get("timing") or {}).get("target_s") or 0)
            continue
        narration = str(scene.get("narration_text") or "").strip()
        sentences = _split_sentences(narration)
        fragments = [
            fragment
            for sentence in sentences
            for contrast in _split_contrast(sentence)
            for fragment in _split_long_idea(contrast)
        ]
        duration = float((scene.get("timing") or {}).get("target_s") or 0)
        durations = _allocate_duration(duration, fragments)
        for _ in range(8):
            refined: list[str] = []
            changed = False
            for fragment, beat_duration in zip(fragments, durations):
                parts = (
                    _split_for_timing(fragment)
                    if beat_duration > 12.0 + 1e-9
                    else [fragment]
                )
                refined.extend(parts)
                changed = changed or len(parts) > 1
            if not changed:
                break
            fragments = refined
            durations = _allocate_duration(duration, fragments)
        rounded_durations = [round(value, 6) for value in durations]
        rounded_durations[-1] = round(
            duration - sum(rounded_durations[:-1]),
            6,
        )
        parent_offset = 0.0
        for fragment_index, (fragment, beat_duration) in enumerate(
            zip(fragments, rounded_durations),
            start=1,
        ):
            beat_index = len(beats)
            parent_function = str(
                scene.get("visual_function")
                or scene.get("visual_type")
                or "document_quote_closeup"
            )
            intent, function = _intent_and_function(
                fragment,
                parent_function,
                beat_index,
            )
            if function == previous_function and intent.startswith("editorial_"):
                function = _FUNCTION_ROTATION[
                    (beat_index + 1) % len(_FUNCTION_ROTATION)
                ]
                intent = f"editorial_{function}"
            previous_function = function
            scene_id = int(scene["scene_id"])
            beat_id = f"scene-{scene_id:03d}-beat-{fragment_index:02d}"
            beat: dict[str, Any] = {
                "beat_id": beat_id,
                "parent_scene_id": scene_id,
                "chapter_id": str(scene.get("chapter_id") or ""),
                "narration_excerpt": fragment,
                "visual_intent": intent,
                "function": function,
                "literature_mode": _literature_mode(function, intent),
                "duration_s": beat_duration,
                "start_s": round(global_start + parent_offset, 6),
                "parent_offset_s": round(parent_offset, 6),
                "claim_refs": copy.deepcopy(list(scene.get("claim_refs") or [])),
                "citation_refs": copy.deepcopy(
                    list(scene.get("citation_refs") or [])
                ),
                "asset_ids": copy.deepcopy(list(scene.get("asset_ids") or [])),
                "motion": _MOTION_ROTATION[beat_index % len(_MOTION_ROTATION)],
                "transition": (
                    "hard_cut"
                    if fragment_index > 1 or intent == "battlefield_legend"
                    else str((scene.get("transition") or {}).get("in") or "hard_cut")
                ),
            }
            if intent in {"battlefield_legend", "tranquil_institution"}:
                beat["illustration_label"] = (
                    "ILLUSTRATED CONTRAST / NOT EVIDENCE"
                )
            beats.append(beat)
            parent_offset += beat_duration
        global_start += duration

    if not beats:
        raise EditorialBeatPlanError("storyboard produced no editorial beats")
    core = {
        "schema_version": EDITORIAL_BEAT_PLAN_VERSION,
        "source_storyboard_hash": canonical_sha256(storyboard),
        "duration_s": round(global_start, 6),
        "parent_scene_count": len(scenes),
        "beat_count": len(beats),
        "beats": beats,
    }
    if storyboard.get("schema_version") == "2.3.0":
        core["coverage_plan_hash"] = str(storyboard["coverage_plan_hash"])
        core["asset_selection_hash"] = str(storyboard["asset_selection_hash"])
    return {**core, "artifact_hash": canonical_sha256(core)}


__all__ = [
    "EDITORIAL_BEAT_PLAN_VERSION",
    "EditorialBeatPlanError",
    "compile_editorial_beat_plan",
]
