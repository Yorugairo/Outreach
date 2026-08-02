"""Semantic coverage planning for History V4.1 living-editorial renders."""

from __future__ import annotations

import copy
import math
import re
from typing import Any, Mapping, Sequence

from content.video_engine.src.services.history_contracts import canonical_sha256


EDITORIAL_COVERAGE_VERSION = "editorial_coverage.v1"
MOTION_RECIPES = (
    "parallax_push",
    "detail_punch",
    "masked_reveal",
    "evidence_highlight",
    "map_trace",
    "comic_pop",
    "split_compare",
    "type_build",
    "paper_transition",
)
VISUAL_SOURCES = {
    "archive",
    "stock_photo",
    "stock_vector",
    "original_illustration",
    "document",
    "map",
    "graph",
    "typography",
}
VISUAL_ARCHETYPES = {
    "archive_portrait",
    "chapter_card",
    "distance_map",
    "document_evidence",
    "entity_graph",
    "historical_martial_archive",
    "historical_travel_broll",
    "lofi_stick_figure_comic",
    "martial_arts_broll",
    "period_comic_block",
    "typography_explainer",
}
SEMANTIC_PURPOSES = {
    "evidence",
    "setting",
    "person",
    "object",
    "transition",
    "humor",
    "explanation",
    "correction",
}

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'])")
_SEMICOLON_RE = re.compile(r";\s+")
_CONTRAST_RE = re.compile(r"\s+(but|yet|instead|however)\s+", re.IGNORECASE)
_CLAUSE_RE = re.compile(
    r",\s+|\s+(?:while|because|when|which|although|whereas|and)\s+",
    re.IGNORECASE,
)
_WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)
_YEAR_RE = re.compile(r"\b(?:18|19|20)\d{2}\b")
_STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "because",
    "before",
    "being",
    "between",
    "could",
    "every",
    "first",
    "from",
    "have",
    "into",
    "more",
    "other",
    "over",
    "said",
    "that",
    "their",
    "there",
    "these",
    "they",
    "this",
    "through",
    "under",
    "what",
    "when",
    "where",
    "which",
    "while",
    "with",
    "would",
}
_ABSTRACT_SEARCH_TERMS = {
    "changed",
    "date",
    "does",
    "emphasis",
    "identity",
    "larger",
    "mean",
    "older",
    "overnight",
    "point",
    "setting",
    "starting",
    "structure",
    "useful",
}
_ENTITY_TERMS = (
    ("jigoro kano", "Jigoro Kano"),
    ("kano", "Jigoro Kano"),
    ("kodokan", "Kodokan"),
    ("mitsuyo maeda", "Mitsuyo Maeda"),
    ("maeda", "Mitsuyo Maeda"),
    ("soshihiro satake", "Soshihiro Satake"),
    ("satake", "Soshihiro Satake"),
    ("carlos gracie", "Carlos Gracie"),
    ("gracie", "Gracie"),
    ("belém", "Belém"),
    ("belem", "Belém"),
    ("são paulo", "São Paulo"),
    ("sao paulo", "São Paulo"),
    ("rio", "Rio de Janeiro"),
    ("brazil", "Brazil"),
    ("japan", "Japan"),
    ("jujutsu", "jujutsu"),
    ("jiu-jitsu", "jiu-jitsu"),
    ("jiu jitsu", "jiu-jitsu"),
    ("judo", "judo"),
    ("dojo", "dojo"),
    ("samurai", "samurai"),
    ("battlefield", "battlefield"),
    ("steamship", "steamship"),
    ("ship", "ship"),
    ("port", "port"),
)
_BLOCKED_STOCK_TERMS = (
    "animal",
    "booking",
    "booking app",
    "business",
    "business meeting",
    "couple",
    "disc golf",
    "gift",
    "gift bag",
    "golf",
    "generative ai",
    "hotel",
    "hotel resort",
    "immigration",
    "immigration app",
    "job id",
    "mobile app",
    "office",
    "office worker",
    "photo effect",
    "pirate",
    "real estate",
    "resort",
    "senior couple",
    "squirrel",
    "titanic",
    "titantic",
    "tour boat",
    "tourist",
    "tourists",
    "style raw",
    "stylize",
    "travel booking",
    "vacation resort",
    "wedding couple",
)


class EditorialCoverageError(ValueError):
    """Raised when semantic coverage cannot satisfy the cadence contract."""


def _words(value: str) -> list[str]:
    return _WORD_RE.findall(value)


def _contains_term(value: str, term: str) -> bool:
    return re.search(
        rf"(?<!\w){re.escape(term.casefold())}(?!\w)",
        value.casefold(),
    ) is not None


def _split_contrast(value: str) -> list[str]:
    match = _CONTRAST_RE.search(value)
    if match is None:
        return [value]
    left = value[: match.start()].strip()
    right = value[match.end() :].strip()
    if len(_words(left)) < 3 or len(_words(right)) < 3:
        return [value]
    return [left, f"{match.group(1).casefold()} {right}"]


def _split_long_clause(value: str, maximum_words: int = 14) -> list[str]:
    if len(_words(value)) <= maximum_words:
        return [value]
    matches = list(_CLAUSE_RE.finditer(value))
    if not matches:
        return [value]
    midpoint = len(value) / 2
    match = min(matches, key=lambda item: abs(item.start() - midpoint))
    left = value[: match.start()].strip(" ,")
    right = value[match.end() :].strip()
    connector = match.group(0).strip(" ,").casefold()
    if connector and not match.group(0).lstrip().startswith(","):
        right = f"{connector} {right}"
    if len(_words(left)) < 4 or len(_words(right)) < 4:
        return [value]
    return [
        *_split_long_clause(left, maximum_words),
        *_split_long_clause(right, maximum_words),
    ]


def split_semantic_units(value: str) -> list[str]:
    """Split at sentence, contrast, and meaningful clause boundaries only."""

    normalized = " ".join(str(value).split())
    if not normalized:
        return []
    result: list[str] = []
    for sentence in _SENTENCE_RE.split(normalized):
        for semicolon_part in _SEMICOLON_RE.split(sentence):
            for contrast_part in _split_contrast(semicolon_part):
                result.extend(_split_long_clause(contrast_part))
    return [item for item in result if item]


def _allocate(total: float, units: Sequence[str]) -> list[float]:
    if total <= 0 or not units:
        raise EditorialCoverageError("coverage requires positive duration and narration")
    weights = [max(1, len(_words(unit))) for unit in units]
    weight_total = sum(weights)
    return [total * weight / weight_total for weight in weights]


def _purpose(text: str, function: str) -> str:
    lowered = text.casefold()
    if any(term in lowered for term in ("myth", "legend", "not simply", "instead")):
        return "correction"
    if any(term in lowered for term in ("record", "source", "document", "evidence")):
        return "evidence"
    if any(term in lowered for term in ("joke", "absurd", "imagine")):
        return "humor"
    if any(term in lowered for term in ("japan", "brazil", "belém", "rio", "port")):
        return "setting"
    if any(
        term in lowered
        for term in ("kano", "maeda", "satake", "gracie", "teacher", "student")
    ):
        return "person"
    if any(term in lowered for term in ("became", "changed", "shift", "moved", "transition")):
        return "transition"
    if function in {"artifact_cold_open", "illustrated_reconstruction"}:
        return "object"
    return "explanation"


def _fallback_source(function: str) -> str:
    return {
        "archival_portrait": "archive",
        "document_quote_closeup": "document",
        "migration_map_timeline": "map",
        "lineage_graph": "graph",
        "illustrated_reconstruction": "original_illustration",
        "artifact_cold_open": "original_illustration",
        "chapter_cta": "typography",
    }.get(function, "typography")


def _entity_concepts(text: str) -> list[str]:
    concepts: list[str] = []
    for needle, canonical in _ENTITY_TERMS:
        if _contains_term(text, needle) and canonical.casefold() not in {
            item.casefold() for item in concepts
        }:
            concepts.append(canonical)
    for year in _YEAR_RE.findall(text):
        if year not in concepts:
            concepts.append(year)
    return concepts


def _visual_archetype(
    function: str,
    *,
    global_index: int,
    has_assets: bool,
    continuation_index: int,
    purpose: str,
    text: str,
) -> tuple[str, str, str, bool]:
    """Resolve a finite editorial template before provider discovery."""

    if function == "lineage_graph":
        return ("entity_graph", "graph", "graph", False)
    if function == "document_quote_closeup":
        return ("document_evidence", "document", "document", False)
    if function == "chapter_cta":
        return ("chapter_card", "typography", "typography", False)
    if function == "migration_map_timeline":
        if global_index % 3 == 1 and any(
            _contains_term(text, term)
            for term in (
                "travel",
                "ship",
                "port",
                "japan",
                "brazil",
                "belém",
                "rio",
                "route",
                "crossed",
            )
        ):
            return (
                "historical_travel_broll",
                "stock_photo",
                "map",
                True,
            )
        return ("distance_map", "map", "map", False)
    if function == "archival_portrait":
        if has_assets and continuation_index == 0:
            return ("archive_portrait", "archive", "archive", False)
        if global_index % 2 == 0:
            if any(
                _contains_term(text, term)
                for term in (
                    "japan",
                    "judo",
                    "jujutsu",
                    "kano",
                    "kodokan",
                    "maeda",
                )
            ):
                return (
                    "historical_martial_archive",
                    "stock_photo",
                    "archive" if has_assets else "typography",
                    True,
                )
            return (
                "martial_arts_broll",
                "stock_photo",
                "archive" if has_assets else "typography",
                True,
            )
        return (
            "archive_portrait" if has_assets else "typography_explainer",
            "archive" if has_assets else "typography",
            "archive" if has_assets else "typography",
            False,
        )
    if function in {"artifact_cold_open", "illustrated_reconstruction"}:
        if (
            continuation_index == 1
            and global_index % 2 == 1
            and any(
                _contains_term(text, term)
                for term in (
                    "battlefield",
                    "legend",
                    "jujutsu",
                    "judo",
                    "japan",
                    "kano",
                    "maeda",
                    "contest",
                )
            )
        ):
            return (
                "period_comic_block",
                "stock_vector",
                "original_illustration",
                True,
            )
        return (
            "period_comic_block",
            "original_illustration",
            "original_illustration",
            False,
        )
    if function == "concept_mechanics_cutaway":
        if purpose in {"humor", "correction"} and global_index % 2 == 0:
            return (
                "lofi_stick_figure_comic",
                "stock_vector",
                "typography",
                True,
            )
        if global_index % 4 == 0:
            if any(
                _contains_term(text, term)
                for term in ("kano", "judo", "jujutsu", "institutional")
            ):
                return (
                    "historical_martial_archive",
                    "stock_photo",
                    "typography",
                    True,
                )
            return (
                "martial_arts_broll",
                "stock_photo",
                "typography",
                True,
            )
        return ("typography_explainer", "typography", "typography", False)
    return ("typography_explainer", _fallback_source(function), _fallback_source(function), False)


def _search_profile(
    text: str,
    archetype: str,
) -> tuple[list[str], str, list[str], list[list[str]]]:
    concepts = _entity_concepts(text)
    if archetype == "historical_martial_archive":
        query_parts = [
            *concepts[:2],
            "historical judo historical martial arts archival dojo Japan",
        ]
        required = [
            "judo",
            "jujutsu",
            "jiu jitsu",
            "jiujitsu",
            "judoka",
            "kodokan",
        ]
        required_groups = [
            required,
            [
                "historical",
                "historic",
                "archive",
                "archival",
                "vintage",
                "black and white",
                "early 20th",
                "1900",
                "1910",
            ],
        ]
    elif archetype == "martial_arts_broll":
        if any(
            _contains_term(text, term)
            for term in ("brazil", "gracie", "maeda", "jiu-jitsu", "jiu jitsu")
        ):
            subject = "Brazilian jiu jitsu grappling training gi documentary photo"
        elif any(
            _contains_term(text, term)
            for term in ("contest", "professional", "fight", "fighting", "match")
        ):
            subject = "judo competition throw tatami documentary photo"
        elif any(
            _contains_term(text, term)
            for term in ("education", "teaching", "teacher", "student", "curriculum")
        ):
            subject = "judo class instruction dojo tatami documentary photo"
        else:
            subject = "judo training dojo tatami documentary photo"
        query_parts = [
            *concepts[:2],
            subject,
        ]
        required = [
            "judo",
            "jujutsu",
            "jiu jitsu",
            "jiujitsu",
            "judoka",
            "grappling",
            "brazilian jiujitsu",
            "brazilian jiu jitsu",
        ]
        required_groups = [required]
    elif archetype == "historical_travel_broll":
        query_parts = [
            *[
                item
                for item in concepts
                if item
                in {
                    "Japan",
                    "Brazil",
                    "Belém",
                    "Rio de Janeiro",
                    "São Paulo",
                    "steamship",
                    "ship",
                    "port",
                }
            ][:3],
            "historic steamship ocean liner 1900 port archival photo",
        ]
        required = [
            "steamship",
            "steamboat",
            "ocean liner",
            "steamer",
            "historic ship",
            "vintage maritime",
            "voyage",
        ]
        required_groups = [
            required,
            [
                "vintage",
                "historic",
                "historical",
                "early 20th",
                "1900",
                "1910",
                "black and white",
                "archival",
                "old",
            ],
        ]
    elif archetype == "period_comic_block":
        subject = (
            "samurai battlefield"
            if any(
                _contains_term(text, term)
                for term in ("battlefield", "legend", "samurai")
            )
            else "Japanese judo jujutsu martial arts"
        )
        query_parts = [*concepts[:2], f"{subject} vintage comic halftone woodblock"]
        required = [
            "samurai",
            "battlefield",
            "judo",
            "jujutsu",
            "martial arts",
            "comic",
            "halftone",
            "woodblock",
            "ukiyo",
            "vintage",
        ]
        required_groups = [
            [
                "samurai",
                "battlefield",
                "judo",
                "jujutsu",
                "martial arts",
            ],
            ["comic", "halftone", "woodblock", "ukiyo", "vintage"],
        ]
    elif archetype == "lofi_stick_figure_comic":
        query_parts = [
            *concepts[:1],
            "hand drawn stick figure martial arts editorial comic monochrome",
        ]
        required = [
            "stick figure",
            "doodle",
            "hand drawn",
            "cartoon",
            "comic",
            "martial arts",
        ]
        required_groups = [
            ["stick figure", "doodle", "hand drawn", "cartoon", "comic"],
            ["martial arts", "judo", "jujutsu", "grappling", "stick figure"],
        ]
    else:
        query_parts = concepts or ["history editorial"]
        required = []
        required_groups = []
    query = " ".join(part for part in query_parts if part)
    if not concepts:
        concepts = [
            word
            for word in _words(query)
            if len(word) >= 4
            and word.casefold() not in _STOPWORDS
            and word.casefold() not in _ABSTRACT_SEARCH_TERMS
        ][:5]
    return concepts[:5], query, required, required_groups


def _micro_events(duration: float, recipe: str) -> list[dict[str, Any]]:
    events = [{"at_s": 0.0, "action": "establish", "recipe": recipe}]
    cursor = 2.25
    actions = ("reframe", "reveal", "emphasize")
    index = 0
    while duration - cursor > 0.35:
        events.append(
            {
                "at_s": round(cursor, 3),
                "action": actions[index % len(actions)],
                "recipe": recipe,
            }
        )
        cursor += 2.25
        index += 1
    return events


def compile_editorial_coverage(
    shot_plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Compile shot_plan.v3 into deterministic 3–6 second semantic slots."""

    if shot_plan.get("schema_version") != "shot_plan.v3":
        raise EditorialCoverageError("coverage requires shot_plan.v3")
    raw_shots = shot_plan.get("shots")
    if not isinstance(raw_shots, Sequence) or isinstance(
        raw_shots, (str, bytes, bytearray)
    ):
        raise EditorialCoverageError("shot plan shots must be an array")

    slots: list[dict[str, Any]] = []
    previous_signature = ""
    start_s = 0.0
    for shot in raw_shots:
        if not isinstance(shot, Mapping):
            raise EditorialCoverageError("shot plan shots must be objects")
        narration = str(shot.get("narration_text") or "").strip()
        units = split_semantic_units(narration)
        duration = float(
            shot.get("duration_s")
            or (shot.get("timing") or {}).get("target_s")
            or 0
        )
        unit_durations = _allocate(duration, units)
        parent_offset = 0.0
        for unit_index, (unit, unit_duration) in enumerate(
            zip(units, unit_durations),
            start=1,
        ):
            continuation_count = max(1, math.ceil(unit_duration / 6.0))
            continuation_duration = unit_duration / continuation_count
            if continuation_duration < 3.0 and continuation_count > 1:
                continuation_count = max(1, math.floor(unit_duration / 3.0))
                continuation_duration = unit_duration / continuation_count
            for continuation_index in range(continuation_count):
                slot_index = len(slots)
                function = str(
                    shot.get("visual_function")
                    or shot.get("function")
                    or "document_quote_closeup"
                )
                recipe = MOTION_RECIPES[slot_index % len(MOTION_RECIPES)]
                purpose = _purpose(unit, function)
                archetype, source, fallback, stock_eligible = _visual_archetype(
                    function,
                    global_index=slot_index,
                    has_assets=bool(shot.get("asset_ids")),
                    continuation_index=continuation_index,
                    purpose=purpose,
                    text=unit,
                )
                (
                    concepts,
                    search_query,
                    required_terms,
                    required_term_groups,
                ) = _search_profile(
                    unit, archetype
                )
                signature = (
                    f"{source}:{archetype}:{function}:{recipe}:{slot_index % 3}:"
                    f"{','.join(str(value) for value in shot.get('asset_ids') or [])}"
                )
                if signature == previous_signature:
                    raise EditorialCoverageError(
                        "adjacent coverage slots repeat their complete signature"
                    )
                previous_signature = signature
                slot_id = (
                    f"{shot['shot_id']}-unit-{unit_index:02d}"
                    f"-part-{continuation_index + 1:02d}"
                )
                slot_duration = round(continuation_duration, 6)
                slot = {
                    "slot_id": slot_id,
                    "parent_shot_id": str(shot["shot_id"]),
                    "chapter_id": str(shot.get("chapter_id") or ""),
                    "narration_excerpt": unit,
                    "continuation_index": continuation_index + 1,
                    "continuation_count": continuation_count,
                    "semantic_purpose": purpose,
                    "visual_archetype": archetype,
                    "stock_eligible": stock_eligible,
                    "preferred_visual_source": source,
                    "fallback_visual_source": fallback,
                    "search_concepts": concepts,
                    "search_query": search_query if stock_eligible else "",
                    "required_terms": required_terms if stock_eligible else [],
                    "required_term_groups": (
                        required_term_groups if stock_eligible else []
                    ),
                    "blocked_terms": (
                        list(_BLOCKED_STOCK_TERMS) if stock_eligible else []
                    ),
                    "function": function,
                    "claim_refs": copy.deepcopy(list(shot.get("claim_refs") or [])),
                    "citation_refs": copy.deepcopy(
                        list(shot.get("citations") or [])
                    ),
                    "asset_ids": copy.deepcopy(list(shot.get("asset_ids") or [])),
                    "duration_s": slot_duration,
                    "start_s": round(start_s + parent_offset, 6),
                    "motion_recipe": recipe,
                    "micro_events": _micro_events(slot_duration, recipe),
                    "transition": (
                        "hard_cut"
                        if continuation_index == 0
                        else "match_cut"
                    ),
                    "uniqueness_signature": signature,
                }
                slots.append(slot)
                parent_offset += continuation_duration
        start_s += duration

    if not slots:
        raise EditorialCoverageError("shot plan produced no coverage slots")
    core = {
        "schema_version": EDITORIAL_COVERAGE_VERSION,
        "source_shot_plan_hash": str(
            shot_plan.get("artifact_hash") or canonical_sha256(shot_plan)
        ),
        "duration_s": round(start_s, 6),
        "slot_count": len(slots),
        "cadence": {
            "major_shot_target_s": [3.0, 6.0],
            "maximum_composition_s": 8.0,
            "micro_event_target_s": [1.5, 3.0],
        },
        "slots": slots,
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def validate_editorial_coverage(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != EDITORIAL_COVERAGE_VERSION:
        errors.append(f"coverage must use {EDITORIAL_COVERAGE_VERSION}")
    slots = payload.get("slots")
    if not isinstance(slots, list) or not slots:
        return [*errors, "coverage requires slots"]
    seen: set[str] = set()
    previous = ""
    for index, slot in enumerate(slots):
        if not isinstance(slot, Mapping):
            errors.append(f"slots[{index}] must be an object")
            continue
        slot_id = str(slot.get("slot_id") or "")
        if not slot_id or slot_id in seen:
            errors.append(f"slots[{index}].slot_id must be unique")
        seen.add(slot_id)
        duration = float(slot.get("duration_s") or 0)
        if duration <= 0 or duration > 8.0:
            errors.append(f"{slot_id or index} duration must be >0 and <=8 seconds")
        if slot.get("semantic_purpose") not in SEMANTIC_PURPOSES:
            errors.append(f"{slot_id or index} has invalid semantic purpose")
        if slot.get("preferred_visual_source") not in VISUAL_SOURCES:
            errors.append(f"{slot_id or index} has invalid visual source")
        archetype = slot.get("visual_archetype")
        if archetype is not None and archetype not in VISUAL_ARCHETYPES:
            errors.append(f"{slot_id or index} has invalid visual archetype")
        stock_eligible = slot.get("stock_eligible")
        if stock_eligible is True:
            if slot.get("preferred_visual_source") not in {"stock_photo", "stock_vector"}:
                errors.append(
                    f"{slot_id or index} is stock eligible without a stock source"
                )
            if not str(slot.get("search_query") or "").strip():
                errors.append(f"{slot_id or index} requires a stock search query")
            if not list(slot.get("required_terms") or []):
                errors.append(f"{slot_id or index} requires stock relevance terms")
            if not list(slot.get("required_term_groups") or []):
                errors.append(
                    f"{slot_id or index} requires grouped stock relevance terms"
                )
        events = slot.get("micro_events")
        if not isinstance(events, list) or not events:
            errors.append(f"{slot_id or index} requires micro-events")
        else:
            times = [float(event.get("at_s") or 0) for event in events if isinstance(event, Mapping)]
            if not times or times[0] != 0:
                errors.append(f"{slot_id or index} micro-events must start at 0")
            boundaries = [*times, duration]
            if any(
                later - earlier > 3.0 + 1e-9
                for earlier, later in zip(boundaries, boundaries[1:])
            ):
                errors.append(f"{slot_id or index} has a static interval over 3 seconds")
        signature = str(slot.get("uniqueness_signature") or "")
        if signature and signature == previous:
            errors.append(f"{slot_id or index} repeats the adjacent signature")
        previous = signature
    expected = canonical_sha256(
        {key: value for key, value in payload.items() if key != "artifact_hash"}
    )
    if payload.get("artifact_hash") != expected:
        errors.append("coverage artifact_hash does not match content")
    return errors


__all__ = [
    "EDITORIAL_COVERAGE_VERSION",
    "EditorialCoverageError",
    "MOTION_RECIPES",
    "VISUAL_ARCHETYPES",
    "compile_editorial_coverage",
    "split_semantic_units",
    "validate_editorial_coverage",
]
