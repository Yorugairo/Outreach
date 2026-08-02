"""Fail-closed visual QC for History Documentary V4 treatments and boards."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from content.video_engine.src.services.history_contracts import canonical_sha256


PHASH_DISTANCE_THRESHOLD = 6
_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_PROHIBITED_KEY_RE = re.compile(r"(?:url|path|study|creator|imitation|source[_-]?frame|renderer[_-]?prompt)", re.IGNORECASE)
_PROHIBITED_TEXT_RE = re.compile(r"(?:https?://|file://|data:|youtube|in\s+the\s+style\s+of|creator(?:'s)?\s+style)", re.IGNORECASE)
_SAFE_ZONES = {"center", "middle", "top", "bottom", "left", "right"}


def _check(check_id: str, passed: bool, detail: str) -> dict[str, str]:
    return {"check_id": check_id, "status": "pass" if passed else "fail", "detail": detail}


def _load(value: Any, job_dir: str | Path | None = None) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if value is None and job_dir is not None:
        root = Path(job_dir)
        for candidate in (root / "visual_treatment.v2.json", root / "storyboard.json", root / "style_board" / "style_board.json"):
            if candidate.is_file():
                value = candidate
                break
    if isinstance(value, (str, Path)):
        path = Path(value)
        if path.is_dir():
            return _load(None, path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError("documentary visual artifact must be an object")
        return dict(payload)
    raise FileNotFoundError("documentary visual treatment or storyboard is required")


def _entries(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    for key in ("shots", "scenes", "stills", "segments"):
        value = payload.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _function(entry: Mapping[str, Any]) -> str:
    for key in ("function", "visual_function", "documentary_function", "visual_type", "composition", "role"):
        value = entry.get(key)
        if value:
            return str(value).casefold()
    params = entry.get("parameters")
    if isinstance(params, Mapping):
        return str(params.get("documentary_function") or params.get("function") or "").casefold()
    return ""


def _asset_ids(entry: Mapping[str, Any]) -> list[str]:
    value = entry.get("asset_ids") or entry.get("approved_asset_ids") or []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value]
    return []


def _citations(entry: Mapping[str, Any]) -> list[Any]:
    value = (
        entry.get("citations")
        or entry.get("citation_ids")
        or entry.get("citation_refs")
        or []
    )
    if isinstance(value, (str, Mapping)):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return list(value)
    return []


def _duration(entry: Mapping[str, Any]) -> float:
    value = entry.get("duration_s")
    if value is None and isinstance(entry.get("timing"), Mapping):
        value = entry["timing"].get("target_s")
    try:
        return max(0.0, float(value or 0.0))
    except (TypeError, ValueError):
        return 0.0


def _walk_provenance(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            # Credits are an editorial/attribution record, not renderer input.
            # In particular, a perfectly valid asset ID such as
            # ``world-archive-study-v1`` must not fail the renderer boundary
            # merely because it appears as a top-level credit key.
            if not path and key.casefold() in {"credits", "asset_credits"}:
                continue
            if _PROHIBITED_KEY_RE.search(key) and key.casefold() not in {"still_path", "artifact_path", "contact_sheet_path"}:
                errors.append(f"{'.'.join((*path, key))} is prohibited provenance")
            errors.extend(_walk_provenance(child, (*path, key)))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            errors.extend(_walk_provenance(child, (*path, str(index))))
    elif isinstance(value, str) and _PROHIBITED_TEXT_RE.search(value):
        errors.append(f"{'.'.join(path) or 'value'} contains prohibited provenance")
    return errors


def _parse_phash(value: Any) -> int | None:
    if isinstance(value, int) and 0 <= value < 2**64:
        return value
    if isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{1,16}", value.strip()):
        return int(value.strip(), 16)
    return None


def _credits(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = payload.get("credits") or payload.get("asset_credits") or {}
    if isinstance(raw, Mapping):
        return {str(key): value for key, value in raw.items()}
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        result: dict[str, Any] = {}
        for item in raw:
            if isinstance(item, Mapping):
                key = item.get("credit_id") or item.get("asset_id") or item.get("id")
                if key:
                    result[str(key)] = item
        return result
    return {}


def run_documentary_visual_qc(
    artifact: Mapping[str, Any] | str | Path | None = None,
    job_dir: str | Path | None = None,
    *,
    require_final_manifest: bool = False,
) -> dict[str, Any]:
    """Run deterministic documentary visual checks and return a check packet."""

    try:
        payload = _load(artifact, job_dir)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return {"overall": "fail", "checks": [_check("artifact_load", False, str(exc))]}
    entries = _entries(payload)
    checks: list[dict[str, str]] = []
    checks.append(_check("documentary_entries", bool(entries), "documentary entries are present" if entries else "no documentary shots/stills found"))

    if job_dir is not None and payload.get("coverage_plan_hash"):
        coverage_path = Path(job_dir) / "editorial_coverage.json"
        try:
            coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
            coverage_ok = (
                payload.get("coverage_plan_hash")
                == coverage.get("artifact_hash")
                == canonical_sha256(coverage)
            )
        except (OSError, UnicodeError, json.JSONDecodeError):
            coverage_ok = False
        checks.append(
            _check(
                "coverage_hash_integrity",
                coverage_ok,
                "coverage plan hash matches immutable source"
                if coverage_ok
                else "coverage plan hash is missing or stale",
            )
        )
    if job_dir is not None and payload.get("asset_selection_hash"):
        review_path = Path(job_dir) / "asset_selection" / "approved-review.json"
        try:
            review = json.loads(review_path.read_text(encoding="utf-8"))
            selection_ok = payload.get("asset_selection_hash") == canonical_sha256(
                review
            )
        except (OSError, UnicodeError, json.JSONDecodeError):
            selection_ok = False
        checks.append(
            _check(
                "asset_selection_hash_integrity",
                selection_ok,
                "asset selection hash matches approved review"
                if selection_ok
                else "asset selection hash is missing or stale",
            )
        )

    classes = [str(item.get("scene_class") or item.get("manim_class") or "") for item in entries]
    stick = [value for value in classes if value.casefold() == "stickfigurescene" or "stick_figure" in value.casefold()]
    checks.append(_check("no_stick_figure_scene", not stick, "History V4 does not use StickFigureScene" if not stick else "StickFigureScene is prohibited in History V4"))

    instructional: list[str] = []
    for index, item in enumerate(entries, start=1):
        blob = json.dumps(item, ensure_ascii=False, sort_keys=True).casefold()
        if any(token in blob for token in ("tutorial", "instructional", "multi_person_grappling", "grappling_choreography", "step 1", "step_1", "technique_steps")):
            instructional.append(str(item.get("shot_id") or item.get("scene_id") or index))
    checks.append(_check("no_instructional_choreography", not instructional, "no instructional choreography or technique tutorial sequences" if not instructional else "instructional choreography found in shots " + ", ".join(instructional)))

    total_duration = sum(_duration(item) for item in entries)
    concept_duration = sum(_duration(item) for item in entries if "concept_mechanics" in _function(item) or "mechanics_cutaway" in _function(item))
    concept_ok = total_duration <= 0 or concept_duration / total_duration <= 0.15 + 1e-9
    checks.append(_check("concept_runtime_budget", concept_ok, "concept mechanics occupy at most 15% of planned runtime" if concept_ok else f"concept mechanics occupy {concept_duration / total_duration:.1%}; maximum is 15%"))

    labels_missing: list[str] = []
    citations_missing: list[str] = []
    historical_functions = {"artifact_cold_open", "archival_portrait", "illustrated_reconstruction", "document_quote_closeup", "migration_map_timeline", "lineage_graph", "concept_mechanics_cutaway"}
    for index, item in enumerate(entries, start=1):
        function = _function(item)
        shot_id = str(item.get("shot_id") or item.get("scene_id") or index)
        if function == "illustrated_reconstruction":
            label = str(item.get("illustration_label") or (item.get("parameters") or {}).get("illustration_label") if isinstance(item.get("parameters"), Mapping) else "")
            if not re.search(r"illustration|reconstruction", label, re.IGNORECASE):
                labels_missing.append(shot_id)
        if function in historical_functions and not _citations(item):
            citations_missing.append(shot_id)
    checks.append(_check("illustration_labels", not labels_missing, "illustrations are visibly labelled as illustration/reconstruction" if not labels_missing else "missing illustration/reconstruction labels for shots " + ", ".join(labels_missing)))
    checks.append(_check("citation_coverage", not citations_missing, "historical visual claims carry citation IDs" if not citations_missing else "missing citation IDs for shots " + ", ".join(citations_missing)))

    treatment_ids = [str(item.get("treatment_id") or "") for item in entries]
    signatures = [
        str(item.get("uniqueness_signature") or item.get("signature") or "")
        for item in entries
    ]
    repeated_treatments = [
        key
        for key, count in Counter(treatment_ids).items()
        if key and count > 1
    ]
    adjacent_signatures = [
        signature
        for left, signature in zip(signatures, signatures[1:])
        if signature and signature == left
    ]
    repeated = [
        *(f"treatment {value}" for value in repeated_treatments),
        *(f"adjacent signature {value}" for value in adjacent_signatures),
    ]
    checks.append(
        _check(
            "treatment_repetition",
            not repeated,
            (
                "treatment IDs are unique and adjacent signatures differ"
                if not repeated
                else "repeated treatment/signature: " + ", ".join(repeated)
            ),
        )
    )

    unsafe: list[str] = []
    for index, item in enumerate(entries, start=1):
        camera = item.get("camera")
        if isinstance(camera, Mapping):
            zone = str(camera.get("safe_zone") or "").casefold()
            if zone and zone not in _SAFE_ZONES:
                unsafe.append(f"{index}.camera.safe_zone")
            elif not zone and "safe_zones" not in item:
                unsafe.append(f"{index}.camera.safe_zone")
        elif not isinstance(item.get("safe_zones"), Mapping):
            unsafe.append(f"{index}.camera")
        safe = item.get("safe_zones")
        if isinstance(safe, Mapping):
            for aspect in ("landscape", "vertical"):
                zone = safe.get(aspect)
                if not isinstance(zone, Mapping) or not zone.get("action_zone") or not zone.get("caption_zone"):
                    unsafe.append(f"{index}.{aspect}")
    checks.append(_check("safe_zones", not unsafe, "action and caption safe zones are present" if not unsafe else "unsafe or incomplete zones: " + ", ".join(unsafe)))

    phashes = [_parse_phash(item.get("phash") or item.get("perceptual_hash")) for item in entries]
    duplicate_errors: list[str] = []
    if any(value is not None for value in phashes):
        if any(value is None for value in phashes):
            duplicate_errors.append("every entry must carry a valid phash when one is supplied")
        else:
            for index, (left, right) in enumerate(zip(phashes, phashes[1:]), start=1):
                assert left is not None and right is not None
                distance = (left ^ right).bit_count()
                if distance <= PHASH_DISTANCE_THRESHOLD:
                    duplicate_errors.append(f"adjacent entries {index} and {index + 1} have phash distance {distance}")
    checks.append(_check("near_duplicates", not duplicate_errors, "perceptual signatures are not near duplicates" if not duplicate_errors else "; ".join(duplicate_errors)))

    credits = _credits(payload)
    if not credits and job_dir is not None:
        selected_credits = (
            Path(job_dir)
            / "asset_selection"
            / "resolved"
            / "credits.json"
        )
        credits_path = (
            selected_credits
            if selected_credits.is_file()
            else Path(job_dir) / "credits.json"
        )
        if credits_path.is_file():
            try:
                credits_payload = json.loads(
                    credits_path.read_text(encoding="utf-8")
                )
                if isinstance(credits_payload, Mapping):
                    credits = _credits(credits_payload)
            except (OSError, UnicodeError, json.JSONDecodeError):
                credits = {}
    incomplete_credits: list[str] = []
    for index, item in enumerate(entries, start=1):
        ids = _asset_ids(item)
        credit_ids = {str(value) for value in (item.get("credit_ids") or item.get("credits") or [])} if isinstance(item.get("credit_ids") or item.get("credits") or [], Sequence) and not isinstance(item.get("credit_ids") or item.get("credits") or [], (str, bytes, bytearray, Mapping)) else set()
        for asset_id in ids:
            if not _ID_RE.fullmatch(asset_id):
                incomplete_credits.append(f"entry {index} invalid asset ID {asset_id!r}")
                continue
            candidates = {asset_id, f"credit-{asset_id}"} | credit_ids
            if not any(candidate in credits for candidate in candidates):
                incomplete_credits.append(f"entry {index} asset {asset_id!r} has no credit")
    checks.append(_check("credits_complete", not incomplete_credits, "all approved assets have credits" if not incomplete_credits else "; ".join(incomplete_credits)))

    provenance = _walk_provenance(payload)
    checks.append(_check("renderer_asset_boundary", not provenance, "renderer inputs contain IDs and internal style data only" if not provenance else "; ".join(sorted(set(provenance)))))

    if require_final_manifest:
        manifest = payload.get("final_manifest")
        if manifest is None and job_dir is not None:
            candidate = Path(job_dir) / "final_manifest.json"
            if candidate.is_file():
                try:
                    manifest = json.loads(candidate.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    manifest = None
        checks.append(_check("final_manifest", isinstance(manifest, Mapping), "final render manifest is present" if isinstance(manifest, Mapping) else "final render manifest is missing"))

    return {"overall": "pass" if all(item["status"] == "pass" for item in checks) else "fail", "checks": checks}


def run_visual_qc(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Compatibility alias for documentary-only callers."""

    return run_documentary_visual_qc(*args, **kwargs)


__all__ = [
    "PHASH_DISTANCE_THRESHOLD",
    "run_documentary_visual_qc",
    "run_visual_qc",
]
