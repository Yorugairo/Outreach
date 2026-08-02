"""Review-only AI-assisted illustration contracts for documentary style boards.

Generated pixels are allowed to help establish visual direction, but they are
not evidence and do not become renderer assets merely because they exist.  The
Visual Direction Gate binds the contact sheet that contains them; a later
promotion step must still add approved files to the rights-reviewed asset
manifest before final rendering.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse


GENERATED_VISUAL_BATCH_VERSION = "generated_visual_candidates.v1"
ALLOWED_PREVIEW_ROLES = {
    "archive",
    "cold_open",
    "concept_mechanics",
    "document",
    "illustration",
    "lineage_concept",
    "map_timeline",
    "lofi_comedy",
}
ALLOWED_REVIEW_STATUSES = {"pending", "selected", "rejected"}
_HEX64 = re.compile(r"^[a-f0-9]{64}$")
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_PROHIBITED_PROMPT_LANGUAGE = (
    "in the style of",
    "style of",
    "youtube.com",
    "youtu.be",
)


class GeneratedVisualValidationError(ValueError):
    """Raised when generated visual candidates cannot be used for review."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    material = copy.deepcopy(dict(payload))
    material.pop("artifact_hash", None)
    encoded = json.dumps(
        material,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(value: Mapping[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GeneratedVisualValidationError(
            [f"generated visual candidate batch is not valid JSON: {exc}"]
        ) from exc
    if not isinstance(payload, dict):
        raise GeneratedVisualValidationError(
            ["generated visual candidate batch must contain an object"]
        )
    return payload


def _is_remote(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme or parsed.netloc)


def _resolve_candidate(path_text: str, job_root: Path) -> Path | None:
    raw = Path(path_text)
    if raw.is_absolute() or _is_remote(path_text):
        return None
    try:
        resolved = (job_root / raw).resolve(strict=True)
        resolved.relative_to(job_root)
    except (OSError, RuntimeError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def validate_generated_visual_candidates(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    check_files: bool = True,
) -> dict[str, Any]:
    """Validate and normalize a fail-closed style-board candidate batch."""

    payload = _load(value)
    root = Path(job_root).resolve()
    errors: list[str] = []
    if payload.get("schema_version") != GENERATED_VISUAL_BATCH_VERSION:
        errors.append(
            "schema_version must be generated_visual_candidates.v1"
        )
    provider = str(payload.get("provider") or "").strip()
    if not provider:
        errors.append("provider is required")
    provider_calls = payload.get("provider_calls", 0)
    if not isinstance(provider_calls, int) or isinstance(provider_calls, bool):
        errors.append("provider_calls must be an integer")
    elif provider_calls < 0:
        errors.append("provider_calls must be non-negative")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must contain at least one candidate")
        items = []

    normalized_items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    selected_roles: dict[str, int] = {}
    for index, raw in enumerate(items):
        label = f"items[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        item = copy.deepcopy(dict(raw))
        item_id = str(item.get("id") or "").strip()
        if not _SAFE_ID.fullmatch(item_id):
            errors.append(f"{label}.id must be a safe lowercase asset ID")
        elif item_id in seen_ids:
            errors.append(f"{label}.id duplicates {item_id!r}")
        seen_ids.add(item_id)

        role = str(item.get("role") or "").strip()
        if role not in ALLOWED_PREVIEW_ROLES:
            errors.append(
                f"{label}.role must be one of "
                + ", ".join(sorted(ALLOWED_PREVIEW_ROLES))
            )
        status = str(item.get("review_status") or "pending").strip()
        if status not in ALLOWED_REVIEW_STATUSES:
            errors.append(
                f"{label}.review_status must be pending, selected, or rejected"
            )
        selected = (
            item.get("style_board_selected") is True
            and status != "rejected"
        )
        if selected:
            selected_roles[role] = selected_roles.get(role, 0) + 1
        if item.get("preview_eligible") is not True:
            errors.append(f"{label}.preview_eligible must be true")
        if item.get("render_eligible") is not False:
            errors.append(
                f"{label}.render_eligible must remain false before promotion"
            )
        if item.get("evidence_eligible") is not False:
            errors.append(f"{label}.evidence_eligible must be false")
        if item.get("contains_factual_text") is not False:
            errors.append(f"{label}.contains_factual_text must be false")
        source_kind = str(item.get("source_kind") or "")
        if source_kind != "ai_assisted_illustration":
            errors.append(
                f"{label}.source_kind must be ai_assisted_illustration"
            )
        disclosure = str(item.get("disclosure_label") or "")
        if not re.search(r"illustration|reconstruction", disclosure, re.I):
            errors.append(
                f"{label}.disclosure_label must identify illustration/reconstruction"
            )
        default_usage = (
            "background_only"
            if role in {"document", "map_timeline"}
            else "full_plate"
        )
        usage = str(item.get("usage") or default_usage)
        if usage not in {"full_plate", "background_only", "context_layer"}:
            errors.append(
                f"{label}.usage must be full_plate, background_only, or context_layer"
            )
        if role in {"document", "map_timeline"} and usage != "background_only":
            errors.append(
                f"{label}.usage must be background_only for the {role} role"
            )

        prompt_summary = str(item.get("prompt_summary") or "")
        lowered_prompt = prompt_summary.casefold()
        for prohibited in _PROHIBITED_PROMPT_LANGUAGE:
            if prohibited in lowered_prompt:
                errors.append(
                    f"{label}.prompt_summary contains prohibited source/style language"
                )
        path_text = str(item.get("path") or "").strip()
        if not path_text:
            errors.append(f"{label}.path is required")
        elif Path(path_text).is_absolute() or _is_remote(path_text):
            errors.append(f"{label}.path must be a job-relative local path")
        declared_sha = str(item.get("sha256") or "").casefold()
        if not _HEX64.fullmatch(declared_sha):
            errors.append(f"{label}.sha256 must be a lowercase SHA-256 digest")
        resolved = _resolve_candidate(path_text, root) if path_text else None
        if check_files and resolved is None and path_text:
            errors.append(
                f"{label}.path does not resolve inside the job directory"
            )
        if resolved is not None and _HEX64.fullmatch(declared_sha):
            actual_sha = _file_sha256(resolved)
            if actual_sha != declared_sha:
                errors.append(
                    f"{label}.sha256 is stale (declared {declared_sha}, actual {actual_sha})"
                )
        normalized = {
            **item,
            "id": item_id,
            "role": role,
            "review_status": status,
            "motion_selected": item.get("motion_selected") is True,
            "usage": usage,
            "path": path_text,
            "sha256": declared_sha,
        }
        if resolved is not None:
            normalized["_resolved_path"] = str(resolved)
        normalized_items.append(normalized)

    if selected_roles.get("cold_open", 0) not in {0, 2}:
        errors.append(
            "cold_open requires exactly two selected candidates for contrast"
        )
    for role, count in selected_roles.items():
        if role != "cold_open" and count > 1:
            errors.append(
                f"{role} may select at most one generated style-board candidate"
            )

    declared_hash = str(payload.get("artifact_hash") or "").casefold()
    if declared_hash and not _HEX64.fullmatch(declared_hash):
        errors.append("artifact_hash must be a lowercase SHA-256 digest")
    expected_hash = _canonical_sha256(payload)
    if declared_hash and declared_hash != expected_hash:
        errors.append(
            f"artifact_hash is stale (declared {declared_hash}, expected {expected_hash})"
        )
    if errors:
        raise GeneratedVisualValidationError(errors)
    normalized_payload = {
        **payload,
        "items": normalized_items,
        "artifact_hash": expected_hash,
    }
    return normalized_payload


def style_board_candidates_by_role(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Return only explicitly selected, non-renderable preview candidates."""

    validated = validate_generated_visual_candidates(
        value,
        job_root=job_root,
        check_files=True,
    )
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in validated["items"]:
        if (
            item.get("style_board_selected") is True
            and item.get("review_status") != "rejected"
        ):
            grouped.setdefault(str(item["role"]), []).append(item)
    return grouped, validated


def motion_candidates_by_role(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Return reviewed generated plates approved for review-motion previews.

    These files are still preview-only.  ``motion_selected`` only says that an
    operator wants the plate used in a local animatic revision; it never
    promotes the provider output into the rights-cleared render manifest.
    """

    validated = validate_generated_visual_candidates(
        value,
        job_root=job_root,
        check_files=True,
    )
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in validated["items"]:
        if (
            item.get("motion_selected") is True
            and item.get("review_status") != "rejected"
        ):
            grouped.setdefault(str(item["role"]), []).append(item)
    return grouped, validated


__all__ = [
    "ALLOWED_PREVIEW_ROLES",
    "GENERATED_VISUAL_BATCH_VERSION",
    "GeneratedVisualValidationError",
    "motion_candidates_by_role",
    "style_board_candidates_by_role",
    "validate_generated_visual_candidates",
]
