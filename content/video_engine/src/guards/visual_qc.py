"""Deterministic visual-quality checks for storyboard and editorial artifacts."""

from __future__ import annotations

import json
import hashlib
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, TypedDict

from content.video_engine.src.services.style_board import (
    COMPOSITION_FUNCTIONS,
    canonical_json,
)


class VisualCheck(TypedDict):
    check_id: str
    status: str
    detail: str


class VisualQCResult(TypedDict):
    overall: str
    checks: list[VisualCheck]


REQUIRED_BJJ_FUNCTIONS = {
    "result_preview",
    "wide_setup",
    "mechanic_transition",
    "wrong_right_compare",
    "force_diagram",
    "result_hold",
}

# V3 uses the full composition grammar, including the non-instructional
# pattern interrupt.  Keep this separate from ``REQUIRED_BJJ_FUNCTIONS`` so
# existing V2 storyboards retain their exact applicability behavior.
REQUIRED_V3_COMPOSITION_FUNCTIONS = frozenset(COMPOSITION_FUNCTIONS)
V3_CHECK_IDS = (
    "study_source_leakage",
    "art_bible_hash_integrity",
    "composition_treatment_coverage",
    "adjacent_signatures",
    "phash_distance",
    "v3_cast_continuity",
    "v3_safe_zones",
    "reviewed_overlay_anchors",
    "final_manifest_coverage",
)
PHASH_DISTANCE_THRESHOLD = 6
MAX_ALLOWED_PHASH_DISTANCE = PHASH_DISTANCE_THRESHOLD

_STUDY_LEAK_KEY = re.compile(
    r"(?:youtube|youtu|creator|reference[_ -]?study|study[_ -]?(?:path|source|id|hash|ref)|source[_ -]?frame|"
    r"frame[_ -]?source|imitation[_ -]?prompt|reference[_ -]?pack|video[_ -]?id|"
    r"downloaded[_ -]?video)",
    re.IGNORECASE,
)
_STUDY_LEAK_VALUE = re.compile(
    r"(?:youtube\.com|youtu\.be|youtube[_ -]?id|reference[_ -]?(?:pack|study)|"
    r"imitation[_ -]?prompt|source[_ -]?frame|study[_ -]?path)",
    re.IGNORECASE,
)


def _check(check_id: str, ok: bool, detail: str) -> VisualCheck:
    return {
        "check_id": check_id,
        "status": "pass" if ok else "fail",
        "detail": detail,
    }


def _parameters(scene: Mapping[str, Any]) -> Mapping[str, Any]:
    value = scene.get("parameters") or {}
    return value if isinstance(value, Mapping) else {}


def _function(scene: Mapping[str, Any]) -> str:
    params = _parameters(scene)
    return str(
        scene.get("visual_function")
        or params.get("function")
        or params.get("shot_function")
        or ""
    )


def _camera(scene: Mapping[str, Any]) -> Mapping[str, Any]:
    value = _parameters(scene).get("camera") or {}
    return value if isinstance(value, Mapping) else {}


def _bjj_scenes(storyboard: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [
        scene
        for scene in storyboard.get("scenes", [])
        if isinstance(scene, Mapping)
        and (
            scene.get("manim_class") == "BJJActionScene"
            or scene.get("visual_type") == "bjj_action"
            or bool(_parameters(scene).get("action"))
            and bool(_function(scene))
        )
    ]


def _load_manifest(root: Path | None) -> Mapping[str, Any]:
    if root is None:
        return {}
    path = root / "technique_manifest.json"
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, Mapping) else {}


def _load_edit_manifest(root: Path | None) -> Mapping[str, Any]:
    if root is None:
        return {}
    for path in (
        root / "edit_manifest.json",
        root / "editorial" / "edit_manifest.json",
    ):
        if path.is_file():
            value = json.loads(path.read_text(encoding="utf-8"))
            return value if isinstance(value, Mapping) else {}
    return {}


def _load_v3_json(root: Path | None, *names: str) -> Mapping[str, Any]:
    if root is None:
        return {}
    for name in names:
        path = root / name
        if path.is_file():
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return {}
            return value if isinstance(value, Mapping) else {}
    return {}


def _style_board_payload(
    storyboard: Mapping[str, Any], root: Path | None
) -> Mapping[str, Any]:
    embedded = storyboard.get("style_board")
    if isinstance(embedded, Mapping):
        return embedded
    if isinstance(storyboard.get("stills"), list):
        return storyboard
    for candidate in (
        root / "style_board" / "style_board.json" if root is not None else None,
        root / "style_board" / "review-packet.json" if root is not None else None,
        root / "style_board.json" if root is not None else None,
    ):
        if candidate is not None and candidate.is_file():
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return {}
            if isinstance(payload, Mapping):
                return payload
    return {}


def _v3_applicable(storyboard: Mapping[str, Any], root: Path | None) -> bool:
    version = str(
        storyboard.get("schema_version")
        or storyboard.get("visual_version")
        or storyboard.get("pipeline_version")
        or ""
    ).casefold()
    if "v3" in version or version in {"3", "visual.v3"}:
        return True
    if isinstance(storyboard.get("style_board"), Mapping):
        return True
    if isinstance(storyboard.get("stills"), list) and (
        storyboard.get("art_bible_hash") or storyboard.get("schema_version") == "style_board.v1"
    ):
        return True
    if root is not None and (
        (root / "style_board" / "style_board.json").is_file()
        or (root / "style_board" / "review-packet.json").is_file()
        or (root / "style_board.json").is_file()
    ):
        return True
    return False


def _v3_entries(
    storyboard: Mapping[str, Any],
    board: Mapping[str, Any],
    root: Path | None,
) -> list[Mapping[str, Any]]:
    board_entries: list[Mapping[str, Any]] = []
    for key in ("stills", "frames", "entries"):
        value = board.get(key)
        if isinstance(value, list):
            board_entries.extend(item for item in value if isinstance(item, Mapping))
            break
    if board_entries:
        # Style-board stills carry the perceptual hash, signatures, cast and
        # safe-zone evidence.  Do not append sparse final-manifest segments to
        # those checks; coverage and manifest checks merge them explicitly.
        return board_entries
    # A final/render manifest may carry the same evidence after compositing.
    final = _load_v3_json(
        root,
        "final_manifest.json",
        "render_manifest.json",
        "editorial/final_manifest.json",
        "editorial/edit_manifest.json",
        "edit_manifest.json",
    )
    for key in ("stills", "frames", "segments", "shots", "scenes"):
        value = final.get(key)
        if isinstance(value, list):
            entries.extend(item for item in value if isinstance(item, Mapping))
            break
    if entries:
        return entries
    return [
        (scene.get("parameters") if isinstance(scene.get("parameters"), Mapping) else scene)
        for scene in storyboard.get("scenes", [])
        if isinstance(scene, Mapping)
    ]


def _v3_final_manifest(
    storyboard: Mapping[str, Any], root: Path | None
) -> Mapping[str, Any]:
    for key in ("final_manifest", "edit_manifest", "editorial_manifest"):
        value = storyboard.get(key)
        if isinstance(value, Mapping):
            return value
    return _load_v3_json(
        root,
        "final_manifest.json",
        "render_manifest.json",
        "editorial/final_manifest.json",
        "editorial/edit_manifest.json",
        "edit_manifest.json",
    )


def _walk_values(value: Any, path: str = "$") -> list[tuple[str, str, Any]]:
    found: list[tuple[str, str, Any]] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            key_path = f"{path}.{key_text}"
            found.append((key_path, key_text, item))
            found.extend(_walk_values(item, key_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_walk_values(item, f"{path}[{index}]"))
    return found


def _study_leak_errors(
    storyboard: Mapping[str, Any], board: Mapping[str, Any], root: Path | None
) -> list[str]:
    errors: list[str] = []
    payloads: dict[str, Any] = {"storyboard": storyboard, "style_board": board}
    if root is not None:
        for name in ("visual_treatment.json", "visual_treatments.json", "treatments.json"):
            candidate = root / name
            if candidate.is_file():
                try:
                    payloads[name] = json.loads(candidate.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    errors.append(f"unreadable renderer artifact {name}")
                break
    for path, key, value in _walk_values(payloads):
        if _STUDY_LEAK_KEY.search(key):
            # ``source`` alone is intentionally not prohibited: internal
            # deterministic provenance is useful evidence.  The explicit
            # study/source-frame keys above are the renderer boundary.
            errors.append(f"study-source field {path}")
        if isinstance(value, str) and _STUDY_LEAK_VALUE.search(value):
            errors.append(f"study-source token at {path}")
    if root is not None:
        for name in ("final_manifest.json", "render_manifest.json", "edit_manifest.json"):
            path = root / name
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if _STUDY_LEAK_VALUE.search(text):
                errors.append(f"study-source token in {path.name}")
    return sorted(set(errors))


def _artifact_hash(payload: Mapping[str, Any], key: str = "artifact_hash") -> str:
    core = {str(k): v for k, v in payload.items() if str(k) != key}
    return hashlib.sha256(canonical_json(core)).hexdigest()


def _v3_hash_errors(
    board: Mapping[str, Any], root: Path | None
) -> list[str]:
    errors: list[str] = []
    expected = str(
        board.get("art_bible_hash") or board.get("artBibleHash") or ""
    ).strip().lower()
    if not expected:
        errors.append("style board is missing art_bible_hash")
    elif not re.fullmatch(r"[a-f0-9]{64}", expected):
        errors.append("style board art_bible_hash is not a 64-character SHA-256")
    declared = str(board.get("artifact_hash") or "").strip().lower()
    if declared and declared != _artifact_hash(board):
        errors.append("style board artifact_hash does not match canonical content")
    entries = [
        item
        for key in ("stills", "frames", "entries")
        if isinstance(board.get(key), list)
        for item in board.get(key, [])
        if isinstance(item, Mapping)
    ]
    for index, item in enumerate(entries):
        item_hash = str(
            item.get("art_bible_hash") or item.get("artBibleHash") or ""
        ).strip().lower()
        if expected and item_hash != expected:
            errors.append(f"still {index + 1} art_bible_hash differs from board")
        if root is not None and item.get("path") and item.get("image_hash"):
            image_path = root / "style_board" / str(item["path"])
            if not image_path.is_file():
                image_path = root / str(item["path"])
            if not image_path.is_file():
                errors.append(f"still {index + 1} image is missing")
            else:
                actual_image_hash = hashlib.sha256(image_path.read_bytes()).hexdigest()
                if actual_image_hash != str(item["image_hash"]).strip().lower():
                    errors.append(f"still {index + 1} image_hash does not match pixels")
    contact_path_value = board.get("contact_sheet_path")
    contact_hash = str(board.get("contact_sheet_hash") or "").strip().lower()
    if root is not None and contact_path_value and contact_hash:
        contact_path = root / "style_board" / str(contact_path_value)
        if not contact_path.is_file():
            contact_path = root / str(contact_path_value)
        if not contact_path.is_file():
            errors.append("style-board contact sheet is missing")
        elif hashlib.sha256(contact_path.read_bytes()).hexdigest() != contact_hash:
            errors.append("style-board contact_sheet_hash does not match pixels")
    if root is not None:
        for name in ("art_bible.json", "art_bible.v1.json"):
            path = root / name
            if not path.is_file():
                continue
            try:
                bible = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                errors.append(f"art bible is unreadable: {name}")
                break
            if not isinstance(bible, Mapping):
                errors.append(f"art bible is not an object: {name}")
                break
            explicit = str(
                bible.get("artifact_hash")
                or bible.get("art_bible_hash")
                or bible.get("hash")
                or ""
            ).strip().lower()
            actual = explicit or hashlib.sha256(canonical_json(bible)).hexdigest()
            if expected and actual != expected:
                errors.append("style board art_bible_hash does not match current art bible")
            break
    return errors


def _entry_function(item: Mapping[str, Any]) -> str:
    value = item.get("composition") or item.get("visual_function") or item.get("function")
    if not value and isinstance(item.get("parameters"), Mapping):
        params = item["parameters"]
        value = params.get("composition") or params.get("visual_function") or params.get("function")
    return str(value or "").casefold()


def _entry_treatment_id(item: Mapping[str, Any]) -> str:
    value = (
        item.get("treatment_id")
        or item.get("treatment")
        or item.get("style_treatment")
        or item.get("id")
    )
    if isinstance(value, Mapping):
        value = value.get("id") or value.get("name")
    return str(value or "").strip()


def _v3_coverage_errors(
    storyboard: Mapping[str, Any], board: Mapping[str, Any], root: Path | None
) -> list[str]:
    entries = list(_v3_entries(storyboard, board, root))
    board_treatments = board.get("treatments")
    if isinstance(board_treatments, list):
        entries.extend(item for item in board_treatments if isinstance(item, Mapping))
    final = _v3_final_manifest(storyboard, root)
    if final:
        for key in ("stills", "frames", "segments", "shots", "scenes"):
            value = final.get(key)
            if isinstance(value, list):
                entries.extend(item for item in value if isinstance(item, Mapping))
                break
    treatment_artifact = _load_v3_json(
        root,
        "visual_treatment.json",
        "visual_treatments.json",
        "treatments.json",
    )
    for key in ("treatments", "shots", "entries"):
        value = treatment_artifact.get(key)
        if isinstance(value, list):
            entries.extend(item for item in value if isinstance(item, Mapping))
            break
    if board:
        entries.extend(
            (scene.get("parameters") if isinstance(scene.get("parameters"), Mapping) else scene)
            for scene in storyboard.get("scenes", [])
            if isinstance(scene, Mapping)
        )
    functions = {_entry_function(item) for item in entries if _entry_function(item)}
    missing = sorted(REQUIRED_V3_COMPOSITION_FUNCTIONS - functions)
    no_treatment = sorted(
        function
        for function in REQUIRED_V3_COMPOSITION_FUNCTIONS
        if function in functions
        and not any(
            _entry_function(item) == function and _entry_treatment_id(item)
            for item in entries
        )
    )
    errors: list[str] = []
    if missing:
        errors.append("missing composition functions: " + ", ".join(missing))
    if no_treatment:
        errors.append("missing treatment ids: " + ", ".join(no_treatment))
    living_diagrams = {
        _entry_treatment_id(item)
        for item in entries
        if item.get("living_diagram") is True
    }
    if len(living_diagrams) < 2:
        errors.append(
            "Armbar V3 requires at least two distinct living-diagram treatments"
        )
    return errors


def _entry_signature(item: Mapping[str, Any]) -> str:
    value = item.get("signature") or item.get("visual_signature")
    if not value and isinstance(item.get("treatment"), Mapping):
        value = item["treatment"].get("signature")
    return str(value or "").strip()


def _v3_signature_errors(
    storyboard: Mapping[str, Any], board: Mapping[str, Any], root: Path | None
) -> list[str]:
    treatment_artifact = _load_v3_json(
        root,
        "visual_treatment.json",
        "visual_treatments.json",
        "treatments.json",
    )
    treatment_entries = treatment_artifact.get("shots")
    if not isinstance(treatment_entries, list):
        treatment_entries = board.get("treatments")
    candidates = (
        [item for item in treatment_entries if isinstance(item, Mapping)]
        if isinstance(treatment_entries, list)
        else []
    )
    entries = (
        candidates
        if candidates and all(_entry_signature(item) for item in candidates)
        else _v3_entries(storyboard, board, root)
    )
    signatures = [_entry_signature(item) for item in entries]
    if not any(signatures):
        declared = board.get("signatures")
        if isinstance(declared, list) and len(declared) >= len(entries):
            signatures = [str(value or "").strip() for value in declared[: len(entries)]]
    errors: list[str] = []
    if any(not signature for signature in signatures):
        errors.append("every V3 still/segment needs a visual signature")
    for index in range(1, len(signatures)):
        if signatures[index] and signatures[index] == signatures[index - 1]:
            errors.append(f"adjacent entries {index} and {index + 1} repeat signature")
    return sorted(set(errors))


def _parse_phash(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and 0 <= value < 2**64:
        return value
    if not isinstance(value, str):
        return None
    raw = value.strip().lower()
    if raw.startswith("0x"):
        raw = raw[2:]
    if not re.fullmatch(r"[0-9a-f]{1,16}", raw):
        return None
    return int(raw, 16)


def _v3_phash_errors(
    storyboard: Mapping[str, Any], board: Mapping[str, Any], root: Path | None
) -> list[str]:
    entries = _v3_entries(storyboard, board, root)
    values = [_parse_phash(item.get("phash") or item.get("p_hash")) for item in entries]
    if all(value is None for value in values):
        declared = board.get("phashes") or board.get("p_hashes")
        if isinstance(declared, list) and len(declared) >= len(entries):
            values = [_parse_phash(value) for value in declared[: len(entries)]]
    errors: list[str] = []
    if any(value is None for value in values):
        errors.append("every V3 still/segment needs a valid 64-bit phash")
        return errors
    for index, (left, right) in enumerate(zip(values, values[1:]), start=1):
        assert left is not None and right is not None
        distance = (left ^ right).bit_count()
        if distance <= PHASH_DISTANCE_THRESHOLD:
            errors.append(
                f"adjacent entries {index} and {index + 1} have phash distance {distance} (<=6)"
            )
    return errors


def _entry_cast(item: Mapping[str, Any]) -> str:
    value = item.get("cast")
    if value is None and isinstance(item.get("parameters"), Mapping):
        value = item["parameters"].get("cast")
    if not isinstance(value, Mapping):
        return ""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _v3_cast_errors(
    storyboard: Mapping[str, Any], board: Mapping[str, Any], root: Path | None
) -> list[str]:
    entries = _v3_entries(storyboard, board, root)
    values = [_entry_cast(item) for item in entries]
    if not values and isinstance(board.get("cast"), Mapping):
        values = [_entry_cast({"cast": board["cast"]})]
    if not values or any(not value for value in values):
        return ["all V3 stills/segments need a non-empty cast mapping"]
    if len(set(values)) != 1:
        return ["V3 cast identity changes across stills/segments"]
    return []


def _entry_safe_zones(item: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in ("safe_zones", "layout_hints", "safe_zone"):
        value = item.get(key)
        if isinstance(value, Mapping):
            return value
    return {}


def _v3_safe_zone_errors(
    storyboard: Mapping[str, Any], board: Mapping[str, Any], root: Path | None
) -> list[str]:
    entries = _v3_entries(storyboard, board, root)
    if not entries and isinstance(board.get("safe_zones"), Mapping):
        entries = [{"safe_zones": board["safe_zones"]}]
    settings = storyboard.get("global_settings")
    targets = settings.get("targets") if isinstance(settings, Mapping) else None
    if not isinstance(targets, list) or not targets:
        targets = ["landscape", "vertical"]
    errors: list[str] = []
    for index, item in enumerate(entries, start=1):
        zones = _entry_safe_zones(item)
        for target in targets:
            value = zones.get(str(target))
            if not isinstance(value, Mapping):
                errors.append(f"entry {index} missing {target} safe zones")
                continue
            if not (
                value.get("action_zone")
                or value.get("action")
                or value.get("action_bounds")
            ):
                errors.append(f"entry {index} missing {target}.action_zone")
            if not (
                value.get("caption_zone")
                or value.get("caption")
                or value.get("text_zone")
                or value.get("text")
                or value.get("overlay_zone")
            ):
                errors.append(f"entry {index} missing {target}.caption_zone")
    return sorted(set(errors))


def _entry_overlays(item: Mapping[str, Any]) -> list[Any]:
    for key in ("overlay_anchors", "reviewed_overlay_anchors", "overlays"):
        value = item.get(key)
        if isinstance(value, list):
            return value
    return []


def _v3_overlay_errors(
    storyboard: Mapping[str, Any], board: Mapping[str, Any], root: Path | None
) -> list[str]:
    entries = _v3_entries(storyboard, board, root)
    if not entries and isinstance(board.get("overlay_anchors"), list):
        entries = [{"overlay_anchors": board["overlay_anchors"]}]
    overlays: list[tuple[int, Any]] = []
    for index, item in enumerate(entries, start=1):
        overlays.extend((index, overlay) for overlay in _entry_overlays(item))
    if not overlays:
        return ["V3 concept has no reviewed overlay anchors"]
    errors: list[str] = []
    for index, overlay in overlays:
        if not isinstance(overlay, Mapping):
            errors.append(f"entry {index} overlay anchor is not an object")
            continue
        if overlay.get("reviewed") is not True:
            errors.append(f"entry {index} overlay anchor is not reviewed")
        if not (overlay.get("anchor") or overlay.get("anchor_id") or overlay.get("contact_id")):
            errors.append(f"entry {index} overlay anchor is missing an anchor id")
    return sorted(set(errors))


def _manifest_ids(manifest: Mapping[str, Any]) -> set[str]:
    ids: set[str] = set()
    for key in ("stills", "frames", "segments", "shots", "scenes", "items"):
        value = manifest.get(key)
        if not isinstance(value, list):
            continue
        for item in value:
            if not isinstance(item, Mapping):
                continue
            for field in ("still_id", "frame_id", "segment_id", "shot_id", "scene_id", "id"):
                if item.get(field) is not None:
                    ids.add(str(item[field]))
                    break
        if ids:
            break
    return ids


def _v3_manifest_errors(
    storyboard: Mapping[str, Any], board: Mapping[str, Any], root: Path | None
) -> list[str]:
    manifest = _v3_final_manifest(storyboard, root)
    if not manifest:
        return ["final render manifest is missing"]
    manifest_hash = str(manifest.get("artifact_hash") or "").strip().lower()
    if manifest_hash and manifest_hash != _artifact_hash(manifest):
        return ["final manifest artifact_hash does not match canonical content"]
    expected: set[str] = set()
    for item in _v3_entries(storyboard, board, None):
        for field in ("still_id", "frame_id", "segment_id", "shot_id", "scene_id", "id"):
            if item.get(field) is not None:
                expected.add(str(item[field]))
                break
    actual = _manifest_ids(manifest)
    missing = sorted(expected - actual)
    if not missing:
        return []
    # Editorial manifests often renumber scene IDs while retaining the style
    # board role/function.  Accept that representation only when every planned
    # still role is present; a short or unrelated manifest remains a failure.
    expected_roles = {
        str(item.get("role") or item.get("still_role") or "").casefold()
        for item in _v3_entries(storyboard, board, None)
        if item.get("role") or item.get("still_role")
    }
    actual_items: list[Mapping[str, Any]] = []
    for key in ("stills", "frames", "segments", "shots", "scenes", "items"):
        value = manifest.get(key)
        if isinstance(value, list):
            actual_items = [item for item in value if isinstance(item, Mapping)]
            break
    actual_roles = {
        str(item.get("role") or item.get("still_role") or "").casefold()
        for item in actual_items
        if item.get("role") or item.get("still_role")
    }
    if expected_roles and expected_roles <= actual_roles:
        return []
    expected_treatments = {
        str(item.get("treatment_id") or "").strip()
        for item in _v3_entries(storyboard, board, None)
        if item.get("treatment_id")
    }
    actual_treatments = {
        str(
            item.get("treatment_id")
            or item.get("visual_treatment_id")
            or item.get("treatment")
            or ""
        ).strip()
        for item in actual_items
        if item.get("treatment_id") or item.get("visual_treatment_id") or item.get("treatment")
    }
    if expected_treatments and expected_treatments <= actual_treatments:
        return []
    if not (expected & actual) and len(actual_items) >= len(expected):
        # A compositor may intentionally renumber all segments while keeping
        # the immutable plan order.  Count-based coverage is accepted only
        # when no planned identifier is present at all; partial manifests
        # still fail closed above.
        return []
    return ["final manifest missing entries: " + ", ".join(missing)]


def _run_v3_visual_qc(
    storyboard: Mapping[str, Any],
    root: Path | None,
    *,
    require_final_manifest: bool = True,
) -> list[VisualCheck]:
    board = _style_board_payload(storyboard, root)
    check_errors = {
        "study_source_leakage": _study_leak_errors(storyboard, board, root),
        "art_bible_hash_integrity": _v3_hash_errors(board, root),
        "composition_treatment_coverage": _v3_coverage_errors(storyboard, board, root),
        "adjacent_signatures": _v3_signature_errors(storyboard, board, root),
        "phash_distance": _v3_phash_errors(storyboard, board, root),
        "v3_cast_continuity": _v3_cast_errors(storyboard, board, root),
        "v3_safe_zones": _v3_safe_zone_errors(storyboard, board, root),
        "reviewed_overlay_anchors": _v3_overlay_errors(storyboard, board, root),
        "final_manifest_coverage": (
            _v3_manifest_errors(storyboard, board, root)
            if require_final_manifest
            else []
        ),
    }
    checks: list[VisualCheck] = []
    details = {
        "study_source_leakage": "renderer-facing artifacts contain no study-source identifiers",
        "art_bible_hash_integrity": "style-board and still hashes match the current art bible",
        "composition_treatment_coverage": "all eight composition functions resolve a treatment",
        "adjacent_signatures": "adjacent stills/segments use distinct signatures",
        "phash_distance": "adjacent 64-bit perceptual hashes are not near duplicates",
        "v3_cast_continuity": "cast identity remains stable across V3 entries",
        "v3_safe_zones": "action and caption safe zones are present for selected targets",
        "reviewed_overlay_anchors": "all visual overlays use reviewed anchors",
        "final_manifest_coverage": (
            "the final render manifest covers every planned entry"
            if require_final_manifest
            else "final-manifest coverage is deferred until Gate B"
        ),
    }
    for check_id in V3_CHECK_IDS:
        errors = check_errors[check_id]
        checks.append(
            _check(
                check_id,
                not errors,
                details[check_id] if not errors else "; ".join(errors),
            )
        )
    return checks


def run_visual_qc(
    storyboard: Mapping[str, Any],
    job_dir: str | Path | None = None,
    *,
    require_final_manifest: bool = True,
) -> VisualQCResult:
    root = Path(job_dir) if job_dir is not None else None
    scenes = _bjj_scenes(storyboard)
    if not scenes and not _v3_applicable(storyboard, root):
        return {
            "overall": "pass",
            "checks": [
                _check(
                    "visual_v2_applicability",
                    True,
                    "legacy/non-BJJ storyboard; visual-v2 checks not applicable",
                )
            ],
        }

    checks: list[VisualCheck] = []
    if not scenes:
        checks.extend(
            _run_v3_visual_qc(
                storyboard,
                root,
                require_final_manifest=require_final_manifest,
            )
        )
        return {
            "overall": "pass"
            if all(check["status"] == "pass" for check in checks)
            else "fail",
            "checks": checks,
        }
    functions = [_function(scene) for scene in scenes]
    function_counts = Counter(functions)
    missing = sorted(REQUIRED_BJJ_FUNCTIONS - set(functions))
    if function_counts.get("contact_closeup", 0) < 2:
        missing.append("contact_closeup>=2")
    checks.append(
        _check(
            "visual_function_coverage",
            not missing,
            (
                "required shot coverage present"
                if not missing
                else "missing visual functions: " + ", ".join(missing)
            ),
        )
    )

    repeated: list[str] = []
    run_signature: tuple[str, str, str] | None = None
    run_count = 0
    for scene in scenes:
        params = _parameters(scene)
        signature = (
            _function(scene),
            str(_camera(scene).get("framing") or ""),
            str(params.get("action") or ""),
        )
        if signature == run_signature:
            run_count += 1
        else:
            run_signature = signature
            run_count = 1
        if run_count > 2:
            repeated.append(
                f"scene {scene.get('scene_id', '?')} repeats {signature!r}"
            )
    checks.append(
        _check(
            "visual_repetition",
            not repeated,
            "no visual signature repeats more than twice"
            if not repeated
            else "; ".join(repeated),
        )
    )

    incomplete: list[str] = []
    for scene in scenes:
        params = _parameters(scene)
        if _function(scene) in {"force_diagram"}:
            continue
        required = ("state_from", "action", "state_to")
        missing_fields = [field for field in required if not params.get(field)]
        phases = (params.get("motion") or {}).get("phases") if isinstance(
            params.get("motion"), Mapping
        ) else None
        if not phases or list(phases) != [
            "anticipation",
            "action",
            "contact",
            "recovery",
        ]:
            missing_fields.append("motion.phases")
        if missing_fields:
            incomplete.append(
                f"scene {scene.get('scene_id', '?')}: {', '.join(missing_fields)}"
            )
    checks.append(
        _check(
            "action_state_completeness",
            not incomplete,
            "all action shots define reviewed states and four motion phases"
            if not incomplete
            else "; ".join(incomplete),
        )
    )

    cast_signatures = {
        json.dumps(_parameters(scene).get("cast") or {}, sort_keys=True)
        for scene in scenes
        if _function(scene) != "force_diagram"
    }
    cast_ok = len(cast_signatures) == 1 and cast_signatures != {"{}"}
    checks.append(
        _check(
            "cast_continuity",
            cast_ok,
            "persistent attacker/defender cast"
            if cast_ok
            else "BJJ action shots must share one non-empty cast mapping",
        )
    )

    manifest = _load_manifest(root)
    known_refs = {
        str(item.get("id") or item.get("reference_id"))
        for item in manifest.get("references", [])
        if isinstance(item, Mapping) and (item.get("id") or item.get("reference_id"))
    }
    unresolved_refs: list[str] = []
    for scene in scenes:
        params = _parameters(scene)
        refs = [str(item) for item in params.get("reference_refs") or []]
        source = str(params.get("action_source") or "")
        if not refs and source != "deterministic_library":
            unresolved_refs.append(
                f"scene {scene.get('scene_id', '?')} has no reviewed reference "
                "or deterministic_library source"
            )
        unresolved_refs.extend(
            f"scene {scene.get('scene_id', '?')} references unknown {ref!r}"
            for ref in refs
            if ref not in known_refs
        )
    checks.append(
        _check(
            "reference_provenance",
            not unresolved_refs,
            "all instructional references resolve"
            if not unresolved_refs
            else "; ".join(unresolved_refs),
        )
    )

    settings = storyboard.get("global_settings") or {}
    pacing = settings.get("pacing") or {} if isinstance(settings, Mapping) else {}
    landscape_budget = float(pacing.get("visual_change_max_s", 6))
    vertical_budget = float(pacing.get("shorts_visual_change_max_s", 3))
    targets = set(settings.get("targets") or []) if isinstance(settings, Mapping) else set()
    cadence_errors: list[str] = []
    safe_zone_errors: list[str] = []
    for scene in scenes:
        duration = float((scene.get("timing") or {}).get("target_s") or 0)
        beats = list(scene.get("beats") or [])
        params = _parameters(scene)
        phases = list((params.get("motion") or {}).get("phases") or []) if isinstance(
            params.get("motion"), Mapping
        ) else []
        if duration > landscape_budget and not beats and len(phases) < 2:
            cadence_errors.append(f"scene {scene.get('scene_id', '?')} landscape")
        if "vertical" in targets and duration > vertical_budget and not beats:
            cadence_errors.append(f"scene {scene.get('scene_id', '?')} vertical")
        hints = scene.get("layout_hints") or {}
        if not isinstance(hints, Mapping):
            safe_zone_errors.append(f"scene {scene.get('scene_id', '?')} layout_hints")
            continue
        for target in targets & {"landscape", "vertical"}:
            target_hints = hints.get(target)
            if not isinstance(target_hints, Mapping) or not target_hints.get("action_zone"):
                safe_zone_errors.append(
                    f"scene {scene.get('scene_id', '?')} {target}.action_zone"
                )
    checks.append(
        _check(
            "visual_cadence",
            not cadence_errors,
            "visual cadence budgets are covered"
            if not cadence_errors
            else "missing timed visual changes: " + ", ".join(cadence_errors),
        )
    )
    checks.append(
        _check(
            "layout_safe_zones",
            not safe_zone_errors,
            "all selected layouts define action zones"
            if not safe_zone_errors
            else "missing layout hints: " + ", ".join(safe_zone_errors),
        )
    )

    edit_manifest = _load_edit_manifest(root)
    if edit_manifest:
        planned_ids = {int(scene["scene_id"]) for scene in storyboard.get("scenes", [])}
        edited_ids = {
            int(item["scene_id"])
            for item in edit_manifest.get("segments", [])
            if isinstance(item, Mapping) and item.get("scene_id") is not None
        }
        missing_ids = sorted(planned_ids - edited_ids)
        checks.append(
            _check(
                "final_plan_coverage",
                not missing_ids,
                "editorial manifest covers every storyboard scene"
                if not missing_ids
                else f"editorial manifest missing scene ids {missing_ids}",
            )
        )

    # V3 concept QC is opt-in by artifact/version so old V2 storyboards keep
    # their established check set and applicability result.
    if _v3_applicable(storyboard, root):
        checks.extend(
            _run_v3_visual_qc(
                storyboard,
                root,
                require_final_manifest=require_final_manifest,
            )
        )

    return {
        "overall": "pass"
        if all(check["status"] == "pass" for check in checks)
        else "fail",
        "checks": checks,
    }


__all__ = [
    "REQUIRED_V3_COMPOSITION_FUNCTIONS",
    "V3_CHECK_IDS",
    "PHASH_DISTANCE_THRESHOLD",
    "MAX_ALLOWED_PHASH_DISTANCE",
    "REQUIRED_BJJ_FUNCTIONS",
    "VisualQCResult",
    "run_visual_qc",
]
