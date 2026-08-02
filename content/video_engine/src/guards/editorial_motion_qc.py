"""Structural QC for revision-only editorial-motion renders.

These checks prove contract integrity, timing, containment, and declared motion
discipline. They intentionally do not claim that an edit is cinematic or good;
the Editorial Motion Proof Gate remains a human watch-through.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from content.video_engine.src.services.editorial_motion import (
    EditorialMotionError,
    validate_editorial_motion_plan,
    validate_editorial_pacing_recipe,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


_WHOLE_FRAME_ACTION_RE = re.compile(
    r"(?:background|whole[_-]?frame|plate)[_-]?(?:pan|drift|shake|translate|zoom)",
    re.IGNORECASE,
)
_SUPPORTED_AMBIENT_ACTIONS = {
    "cloud_drift",
    "lamp_flicker",
    "window_light",
    "smoke_drift",
    "leaves_flutter",
    "paper_dust",
    "river_flow",
    "ship_wake",
}


def _load(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} could not be read: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise ValueError(f"{label} must be an object")
    return dict(payload)


def _check(check_id: str, passed: bool, detail: str) -> dict[str, str]:
    return {"check_id": check_id, "status": "pass" if passed else "fail", "detail": detail}


def _asset_records(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw = payload.get("assets")
    if isinstance(raw, Mapping):
        return {
            str(asset_id): item if isinstance(item, Mapping) else {}
            for asset_id, item in raw.items()
        }
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        return {
            str(item.get("id") or item.get("asset_id") or ""): item
            for item in raw
            if isinstance(item, Mapping) and (item.get("id") or item.get("asset_id"))
        }
    return {}


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return True


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _is_evidence_asset(record: Mapping[str, Any]) -> bool:
    """Accept both the revision map flag and canonical asset-manifest kinds."""

    return record.get("evidence_eligible") is True or str(record.get("kind") or "") in {
        "archival_portrait",
        "archival_photo",
        "document",
    }


def run_editorial_motion_qc(
    plan: Mapping[str, Any] | str | Path,
    *,
    pacing_recipe: Mapping[str, Any] | str | Path,
    asset_map: Mapping[str, Any] | str | Path,
    asset_root: str | Path,
    revision_dir: str | Path,
    job_dir: str | Path,
    expected_hashes: Mapping[str, str] | None = None,
    check_files: bool = True,
) -> dict[str, Any]:
    """Return fail-closed structural evidence for one revision render."""

    checks: list[dict[str, str]] = []
    try:
        asset_payload = _load(asset_map, "asset map")
        assets = _asset_records(asset_payload)
        validated = validate_editorial_motion_plan(plan, known_asset_ids=set(assets))
        recipe = validate_editorial_pacing_recipe(pacing_recipe)
    except (EditorialMotionError, ValueError) as exc:
        return {
            "schema_version": "editorial_motion_qc.v1",
            "overall": "fail",
            "structural_pass": False,
            "human_review_required": True,
            "checks": [_check("contract_integrity", False, str(exc))],
        }
    checks.append(_check("contract_integrity", True, "plan and pacing contracts are current"))

    declared_asset_hash = str(asset_payload.get("artifact_hash") or "")
    actual_asset_hash = canonical_sha256(asset_payload)
    asset_hash_ok = (
        validated["asset_map_hash"] == actual_asset_hash
        and (not declared_asset_hash or declared_asset_hash == actual_asset_hash)
    )
    checks.append(
        _check(
            "asset_map_hash_integrity",
            asset_hash_ok,
            "asset map hash matches the plan" if asset_hash_ok else "asset map hash is stale or mismatched",
        )
    )

    stale: list[str] = []
    for key, expected in (expected_hashes or {}).items():
        if str(validated.get(key) or "") != str(expected):
            stale.append(key)
    checks.append(
        _check(
            "upstream_hash_integrity",
            not stale,
            "all supplied upstream hashes match" if not stale else "stale upstream hashes: " + ", ".join(stale),
        )
    )

    root = Path(asset_root).resolve()
    asset_errors: list[str] = []
    used_ids = {
        str(layer.get("asset_id") or "")
        for shot in validated["shots"]
        for layer in shot.get("layers") or []
    }
    for asset_id in sorted(used_ids):
        record = assets.get(asset_id) or {}
        if record.get("render_eligible") is not True:
            asset_errors.append(f"{asset_id} is not render eligible")
        if record.get("provider_output") is True and record.get("human_promoted") is not True:
            asset_errors.append(f"{asset_id} is unpromoted provider output")
        raw_path = record.get("path") or record.get("local_path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            asset_errors.append(f"{asset_id} has no local path")
            continue
        relative = Path(raw_path)
        if relative.is_absolute():
            candidate = relative.resolve()
        else:
            candidate = (root / relative).resolve()
        if not _inside(candidate, root):
            asset_errors.append(f"{asset_id} escapes the approved asset root")
            continue
        if check_files:
            if not candidate.is_file():
                asset_errors.append(f"{asset_id} file is missing")
                continue
            expected = str(record.get("sha256") or record.get("content_hash") or "")
            if not expected or _sha256(candidate) != expected:
                asset_errors.append(f"{asset_id} content hash is missing or stale")
    checks.append(
        _check(
            "asset_resolution",
            not asset_errors,
            "all used assets are contained, promoted, and hash-matched" if not asset_errors else "; ".join(asset_errors),
        )
    )

    revision = Path(revision_dir).resolve()
    job = Path(job_dir).resolve()
    revision_ok = _inside(revision, job / "animatic" / "revisions") and revision != job
    checks.append(
        _check(
            "revision_path_containment",
            revision_ok,
            "outputs remain under the job revision tree" if revision_ok else "revision output escapes animatic/revisions",
        )
    )

    motion_errors: list[str] = []
    maximum_hold_s = min(float(recipe["maximum_shot_duration_s"]), 6.0)
    moving_run = 0
    scale_run = 0
    previous_scale = ""
    previous_signature = ""
    signature_run = 0
    for shot in validated["shots"]:
        if float(shot["duration_s"]) > maximum_hold_s + 1e-4:
            motion_errors.append(
                f"{shot['shot_id']} exceeds the {maximum_hold_s:.3f}-second visual-hold ceiling"
            )
        camera = shot["camera"]
        moving = camera["kind"] != "locked"
        moving_run = moving_run + 1 if moving else 0
        if moving_run > int(recipe["max_consecutive_moving_shots"]):
            motion_errors.append(f"{shot['shot_id']} exceeds the consecutive moving-shot ceiling")
        scale = str(shot["shot_scale"])
        scale_run = scale_run + 1 if scale == previous_scale else 1
        previous_scale = scale
        if scale_run > int(recipe["max_consecutive_same_scale"]):
            motion_errors.append(f"{shot['shot_id']} repeats the same scale too long")
        signature = str(shot["uniqueness_signature"])
        signature_run = signature_run + 1 if signature == previous_signature else 1
        previous_signature = signature
        if signature_run > 2:
            motion_errors.append(f"{shot['shot_id']} repeats the same treatment signature")
        for layer in shot.get("layers") or []:
            action = str(layer.get("action") or "")
            if layer.get("role") == "world" and _WHOLE_FRAME_ACTION_RE.search(action):
                motion_errors.append(f"{shot['shot_id']} declares whole-frame movement as a layer action")
        unknown_ambient = sorted(
            action
            for action in shot.get("ambient_actions") or []
            if str(action).casefold() not in _SUPPORTED_AMBIENT_ACTIONS
        )
        if unknown_ambient:
            motion_errors.append(
                f"{shot['shot_id']} uses unsupported ambient actions: "
                + ", ".join(str(item) for item in unknown_ambient)
            )
    checks.append(
        _check(
            "motion_discipline",
            not motion_errors,
            "motion density, scale rhythm, and layer ownership satisfy the recipe" if not motion_errors else "; ".join(motion_errors),
        )
    )

    surface_errors: list[str] = []
    for shot in validated["shots"]:
        surface = shot.get("information_surface")
        if not isinstance(surface, Mapping) or surface.get("mode") == "none":
            continue
        if float(surface.get("x") or 0) + float(surface.get("width") or 0) > 1:
            surface_errors.append(f"{shot['shot_id']} information surface escapes the right edge")
        if float(surface.get("y") or 0) + float(surface.get("height") or 0) > 1:
            surface_errors.append(f"{shot['shot_id']} information surface escapes the bottom edge")
        for layer in shot.get("layers") or []:
            layout = layer.get("layout")
            if layer.get("role") == "character" and isinstance(layout, Mapping):
                if _rectangles_overlap(surface, layout):
                    surface_errors.append(
                        f"{shot['shot_id']} information surface overlaps character {layer.get('asset_id')}"
                    )
    checks.append(
        _check(
            "information_surface_safety",
            not surface_errors,
            "information surfaces stay on-canvas and clear of characters"
            if not surface_errors
            else "; ".join(surface_errors),
        )
    )

    value_errors: list[str] = []
    surface_count = sum(
        1
        for shot in validated["shots"]
        if isinstance(shot.get("information_surface"), Mapping)
        and shot["information_surface"].get("mode") != "none"
    )
    surface_limit = recipe.get("max_information_surfaces")
    if surface_limit is not None and surface_count > int(surface_limit):
        value_errors.append(
            f"information surfaces {surface_count} exceed the recipe limit {surface_limit}"
        )
    non_evidence_prop_layers = [
        (str(shot["shot_id"]), str(layer.get("asset_id") or ""))
        for shot in validated["shots"]
        for layer in shot.get("layers") or []
        if layer.get("role") == "prop"
        and not _is_evidence_asset(assets.get(str(layer.get("asset_id") or "")) or {})
    ]
    prop_limit = recipe.get("max_non_evidence_prop_layers")
    if prop_limit is not None and len(non_evidence_prop_layers) > int(prop_limit):
        rendered = ", ".join(f"{shot}:{asset}" for shot, asset in non_evidence_prop_layers)
        value_errors.append(
            f"non-evidence prop layers {len(non_evidence_prop_layers)} exceed the recipe limit "
            f"{prop_limit}: {rendered}"
        )
    checks.append(
        _check(
            "editorial_value_discipline",
            not value_errors,
            "information surfaces and non-evidence props stay within the approved limits"
            if not value_errors
            else "; ".join(value_errors),
        )
    )

    provider_ok = validated.get("provider_calls") == 0
    checks.append(
        _check(
            "provider_boundary",
            provider_ok,
            "provider calls equal zero" if provider_ok else "provider calls are not permitted in this proof",
        )
    )

    passed = all(check["status"] == "pass" for check in checks)
    return {
        "schema_version": "editorial_motion_qc.v1",
        "overall": "pass" if passed else "fail",
        "structural_pass": passed,
        "human_review_required": True,
        "quality_claim": "none; human watch-through required",
        "checks": checks,
    }


__all__ = ["run_editorial_motion_qc"]
