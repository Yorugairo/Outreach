"""One-generated-plate-per-editorial-block contracts for documentary V4.2.

The block plan is intentionally separate from the renderer.  It describes
what an image producer should make for each meaningful narration block.  The
completed batch then binds each generated file to the exact coverage slots it
serves.  Generated pixels remain review-only; Remotion owns all factual text,
citations, and other meaning-bearing overlays.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from content.video_engine.src.services.asset_resolver import (
    AssetManifestValidationError,
    validate_asset_manifest,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


GENERATED_BLOCK_PLAN_VERSION = "generated_image_block_plan.v1"
GENERATED_BLOCK_BATCH_VERSION = "generated_image_block_batch.v1"
TIMESTAMPED_PLATE_PLAN_VERSION = "timestamped_plate_plan.v1"
TIMESTAMPED_PROMPT_SPINE_VERSION = "timestamped_plate_prompt_spine.v1"
TIMESTAMPED_PLATE_CANDIDATE_INVENTORY_VERSION = (
    "timestamped_plate_candidate_inventory.v1"
)
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_HEX64 = re.compile(r"^[a-f0-9]{64}$")
_PROHIBITED_PROMPT_LANGUAGE = (
    "in the style of",
    "style of",
    "youtube.com",
    "youtu.be",
    "source frame",
    "creator name",
)


class GeneratedBlockImageError(ValueError):
    """Raised when a one-image-per-block artifact is unsafe or incomplete."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def _load(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GeneratedBlockImageError([f"{label} is not valid JSON: {exc}"]) from exc
    if not isinstance(payload, dict):
        raise GeneratedBlockImageError([f"{label} must contain an object"])
    return payload


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_remote(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme or parsed.netloc)


def _resolve_local(path_text: str, job_root: Path) -> Path | None:
    raw = Path(path_text)
    if raw.is_absolute() or _is_remote(path_text):
        return None
    try:
        resolved = (job_root / raw).resolve(strict=True)
        resolved.relative_to(job_root)
    except (OSError, RuntimeError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def _public_asset_manifest(value: Mapping[str, Any]) -> dict[str, Any]:
    """Drop resolver-only local paths before persisting a manifest."""

    payload = copy.deepcopy(dict(value))
    for asset in payload.get("assets") or []:
        if isinstance(asset, dict):
            asset.pop("_resolved_path", None)
    return payload


def _safe_manifest_id(value: str, label: str) -> str:
    manifest_id = str(value or "").strip().casefold()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", manifest_id):
        raise GeneratedBlockImageError(
            [f"{label} must be a lowercase hyphenated identifier"]
        )
    return manifest_id


def _approved_candidate_inventory(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    expected_plan: Mapping[str, Any] | str | Path | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate a reviewed timestamped candidate inventory for promotion.

    The inventory remains intentionally separate from the generated-plate plan:
    it is the review record that associates produced bytes with a planned
    timestamp.  This helper never changes a candidate in place; promotion
    returns a new standard ``asset_manifest.v1``.
    """

    payload = _load(value, "timestamped plate candidate inventory")
    root = Path(job_root).resolve()
    errors: list[str] = []
    if payload.get("schema_version") != TIMESTAMPED_PLATE_CANDIDATE_INVENTORY_VERSION:
        errors.append(
            "timestamped plate candidate inventory must use "
            f"{TIMESTAMPED_PLATE_CANDIDATE_INVENTORY_VERSION}"
        )
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        errors.append("timestamped plate candidate inventory requires items")
        items = []

    plan_blocks: list[Mapping[str, Any]] = []
    expected_plan_hash = ""
    if expected_plan is not None:
        plan = validate_timestamped_plate_plan(expected_plan)
        plan_blocks = [item for item in plan.get("blocks") or [] if isinstance(item, Mapping)]
        expected_plan_hash = str(plan["artifact_hash"])
        if str(payload.get("plan_hash") or "") != expected_plan_hash:
            errors.append("timestamped plate candidate inventory plan_hash is stale")

    declared_hash = str(payload.get("artifact_hash") or "").casefold()
    actual_hash = canonical_sha256(
        {key: item for key, item in payload.items() if key != "artifact_hash"}
    )
    if declared_hash != actual_hash:
        errors.append("timestamped plate candidate inventory artifact_hash is stale")

    expected_by_order: dict[int, Mapping[str, Any]] = {
        int(item.get("order") or 0): item for item in plan_blocks
    }
    seen_orders: set[int] = set()
    seen_slots: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(items):
        label = f"items[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        item = copy.deepcopy(dict(raw))
        try:
            order = int(item.get("order"))
        except (TypeError, ValueError):
            errors.append(f"{label}.order must be an integer")
            continue
        if order <= 0 or order in seen_orders:
            errors.append(f"{label}.order must be unique and positive")
        seen_orders.add(order)
        slot_id = str(item.get("slot_id") or "")
        if not _SAFE_ID.fullmatch(slot_id) or slot_id in seen_slots:
            errors.append(f"{label}.slot_id must be a unique safe identifier")
        seen_slots.add(slot_id)
        path_text = str(item.get("source_path") or "").strip()
        resolved = _resolve_local(path_text, root) if path_text else None
        if resolved is None:
            errors.append(f"{label}.source_path must resolve inside the job directory")
        declared_sha = str(item.get("sha256") or "").casefold()
        if not _HEX64.fullmatch(declared_sha):
            errors.append(f"{label}.sha256 must be a lowercase SHA-256 digest")
        elif resolved is not None and _file_sha256(resolved) != declared_sha:
            errors.append(f"{label}.sha256 is stale")
        status = str(item.get("status") or "")
        if status not in {"candidate", "review_only_archive"}:
            errors.append(f"{label}.status must be candidate or review_only_archive")
        if item.get("render_eligible") is not False:
            errors.append(f"{label}.render_eligible must remain false before promotion")
        if expected_by_order:
            expected = expected_by_order.get(order)
            if expected is None:
                errors.append(f"{label}.order is not present in the timestamped plate plan")
            else:
                expected_slots = expected.get("coverage_slot_ids") or []
                if expected_slots != [slot_id]:
                    errors.append(f"{label}.slot_id does not match its planned coverage slot")
                for time_key in ("start_s", "end_s"):
                    try:
                        actual_time = float(item.get(time_key))
                        planned_time = float(expected.get(time_key))
                    except (TypeError, ValueError):
                        errors.append(f"{label}.{time_key} must be numeric")
                    else:
                        if abs(actual_time - planned_time) > 1e-3:
                            errors.append(f"{label}.{time_key} does not match the timestamped plate plan")
        normalized.append(
            {
                **item,
                "order": order,
                "slot_id": slot_id,
                "source_path": path_text,
                "sha256": declared_sha,
                "status": status,
            }
        )

    if expected_by_order and set(expected_by_order) != seen_orders:
        errors.append("timestamped plate candidate inventory does not cover every planned order")
    if int(payload.get("plate_count") or 0) != len(normalized):
        errors.append("timestamped plate candidate inventory plate_count does not match items")
    if int(payload.get("candidate_count") or 0) != sum(
        item["status"] == "candidate" for item in normalized
    ):
        errors.append("timestamped plate candidate inventory candidate_count does not match items")
    if int(payload.get("review_only_archive_count") or 0) != sum(
        item["status"] == "review_only_archive" for item in normalized
    ):
        errors.append(
            "timestamped plate candidate inventory review_only_archive_count does not match items"
        )
    if errors:
        raise GeneratedBlockImageError(errors)
    return (
        {
            **payload,
            "items": normalized,
            "plan_hash": expected_plan_hash or str(payload.get("plan_hash") or ""),
            "artifact_hash": actual_hash,
        },
        normalized,
    )


def replace_timestamped_plate_candidate(
    inventory: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    expected_plan: Mapping[str, Any] | str | Path,
    order: int,
    replacement_path: str,
) -> dict[str, Any]:
    """Create a new immutable review inventory with one approved replacement.

    A candidate inventory is evidence of a specific review state, so an
    imperfect or rights-blocked image is never edited in place.  The caller
    receives a sibling inventory with the exact planned interval preserved and
    the replacement bytes hashed before a new promotion is possible.
    """

    root = Path(job_root).resolve()
    try:
        replacement_order = int(order)
    except (TypeError, ValueError) as exc:
        raise GeneratedBlockImageError(["order must be an integer"]) from exc
    validated, items = _approved_candidate_inventory(
        inventory,
        job_root=root,
        expected_plan=expected_plan,
    )
    replacement = _resolve_local(str(replacement_path or "").strip(), root)
    if replacement is None:
        raise GeneratedBlockImageError(
            ["replacement_path must resolve to a local file inside the job directory"]
        )
    matching = [item for item in items if int(item["order"]) == replacement_order]
    if len(matching) != 1:
        raise GeneratedBlockImageError(
            [f"timestamped plate inventory has no unique order {replacement_order}"]
        )
    replacement_item = matching[0]
    source_path = replacement.relative_to(root).as_posix()
    updated_items: list[dict[str, Any]] = []
    for item in items:
        if int(item["order"]) != replacement_order:
            updated_items.append(item)
            continue
        updated_items.append(
            {
                **item,
                "source_path": source_path,
                "sha256": _file_sha256(replacement),
                "status": "candidate",
                "render_eligible": False,
                "replaces": {
                    "source_path": replacement_item["source_path"],
                    "sha256": replacement_item["sha256"],
                    "status": replacement_item["status"],
                    "reason": "original_rights-cleared illustration replaces review-only or rejected input",
                },
            }
        )
    core = {
        key: copy.deepcopy(value)
        for key, value in validated.items()
        if key not in {"items", "artifact_hash", "candidate_count", "review_only_archive_count"}
    }
    core.update(
        {
            "items": updated_items,
            "candidate_count": sum(item["status"] == "candidate" for item in updated_items),
            "review_only_archive_count": sum(
                item["status"] == "review_only_archive" for item in updated_items
            ),
            "render_eligible": False,
        }
    )
    return {**core, "artifact_hash": canonical_sha256(core)}


def compile_timestamped_plate_asset_manifest(
    inventory: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    project_root: str | Path,
    expected_plan: Mapping[str, Any] | str | Path,
    manifest_id: str,
    project_id: str,
    episode_id: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    """Promote reviewed original plates into a hash-bound asset manifest.

    ``review_only_archive`` entries deliberately stay in the manifest but are
    quarantined.  This preserves full timestamp accounting while preventing an
    unresolved source from becoming renderable through an all-or-nothing batch
    approval.
    """

    root = Path(job_root).resolve()
    project = Path(project_root).resolve()
    try:
        root.relative_to(project)
    except ValueError as exc:
        raise GeneratedBlockImageError(
            ["timestamped plate job_root must be contained by project_root"]
        ) from exc
    validated_inventory, items = _approved_candidate_inventory(
        inventory,
        job_root=root,
        expected_plan=expected_plan,
    )
    safe_manifest_id = _safe_manifest_id(manifest_id, "manifest_id")
    if not str(project_id or "").strip():
        raise GeneratedBlockImageError(["project_id is required"])
    if not str(episode_id or "").strip():
        raise GeneratedBlockImageError(["episode_id is required"])
    if not str(approved_by or "").strip():
        raise GeneratedBlockImageError(["approved_by is required"])
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(approved_at or "").strip()):
        raise GeneratedBlockImageError(["approved_at must be an ISO YYYY-MM-DD date"])

    assets: list[dict[str, Any]] = []
    for item in items:
        order = int(item["order"])
        slot_id = str(item["slot_id"])
        resolved = _resolve_local(str(item["source_path"]), root)
        if resolved is None:  # Validation above makes this a defensive guard.
            raise GeneratedBlockImageError([f"plate {order:03d} source is missing"])
        try:
            project_relative = resolved.relative_to(project).as_posix()
        except ValueError as exc:  # Defensive; job containment is asserted above.
            raise GeneratedBlockImageError(
                [f"plate {order:03d} escapes the project root"]
            ) from exc
        asset_id = f"timestamped-plate-{order:03d}-{slot_id}"
        metadata = {
            "timestamped_plate_order": order,
            "coverage_slot_id": slot_id,
            "start_s": float(item["start_s"]),
            "end_s": float(item["end_s"]),
            "timestamped_plate_plan_hash": validated_inventory["plan_hash"],
            "candidate_inventory_hash": validated_inventory["artifact_hash"],
            "source_kind": "ai_assisted_illustration",
            "evidence_eligible": False,
            "contains_factual_text": False,
            "disclosure_label": "AI-assisted illustration / reconstruction",
        }
        if item["status"] == "candidate":
            assets.append(
                {
                    "id": asset_id,
                    "path": project_relative,
                    "sha256": str(item["sha256"]),
                    "kind": "generated_illustration_plate",
                    "role": "timestamped-primary-plate",
                    "title": f"Timestamped illustration plate {order:03d}",
                    "origin": "Operator-approved original AI-assisted illustration generated through the local Codex image path",
                    "rights": {
                        "permission": "original",
                        "reviewed": True,
                        "reviewed_by": str(approved_by),
                        "reviewed_at": str(approved_at),
                        "source": "Outreach Program",
                        "attribution_required": False,
                    },
                    "likeness": {"living": False, "approved": True},
                    "alteration_policy": {
                        "allowed": True,
                        "reviewed": True,
                        "policy": "Illustration/reconstruction only; factual text and citations are composited locally.",
                    },
                    "render_eligible": True,
                    "metadata": metadata,
                }
            )
        else:
            assets.append(
                {
                    "id": asset_id,
                    "path": project_relative,
                    "sha256": str(item["sha256"]),
                    "kind": "archival_photo_review",
                    "role": "timestamped-primary-plate",
                    "title": f"Timestamped archive review plate {order:03d}",
                    "origin": "Operator-supplied archival review insert; source, date, license, and attribution are pending verification",
                    "rights": {
                        "permission": "unverified",
                        "reviewed": False,
                        "reviewed_by": None,
                        "reviewed_at": None,
                        "source": "Pending source and rights verification",
                        "attribution_required": True,
                    },
                    "likeness": {"living": False, "approved": False},
                    "alteration_policy": {
                        "allowed": False,
                        "reviewed": False,
                        "policy": "Review-only archival insert; cannot render or publish until rights review is completed.",
                    },
                    "render_eligible": False,
                    "quarantine_reason": [
                        "awaiting_source_date_license_and_attribution_verification"
                    ],
                    "metadata": metadata,
                }
            )

    core = {
        "schema_version": "asset_manifest.v1",
        "manifest_id": safe_manifest_id,
        "project_id": str(project_id),
        "episode_id": str(episode_id),
        "job_id": root.name,
        "review": {
            "status": "operator_approved_with_quarantined_exceptions",
            "reviewed_by": str(approved_by),
            "reviewed_at": str(approved_at),
            "approved_generated_plate_count": sum(
                item["status"] == "candidate" for item in items
            ),
            "quarantined_archive_count": sum(
                item["status"] == "review_only_archive" for item in items
            ),
        },
        "notes": {
            "promotion_policy": "Approved original illustrations are render eligible; generated pixels are not factual evidence and all dates, claims, quotations, and citations remain local editorial overlays.",
            "coverage_plan_hash": validated_inventory.get("coverage_plan_hash"),
            "timestamped_plate_plan_hash": validated_inventory["plan_hash"],
            "timestamped_prompt_spine_hash": validated_inventory.get("prompt_spine_hash"),
            "candidate_inventory_hash": validated_inventory["artifact_hash"],
            "archive_policy": "Review-only archival entries remain quarantined until source, date, license, and attribution are verified.",
        },
        "assets": assets,
    }
    try:
        validated = validate_asset_manifest(
            core,
            project_root=project,
            job_dir=root,
            check_files=True,
        )
    except AssetManifestValidationError as exc:
        raise GeneratedBlockImageError(list(exc.errors)) from exc
    return _public_asset_manifest(validated)


def _block_id(index: int, slot_id: str) -> str:
    safe = re.sub(r"[^a-z0-9]+", "-", slot_id.casefold()).strip("-")
    return f"image-block-{index:03d}-{safe[:52]}"


def _visual_source(function: str) -> str:
    return {
        "migration_map_timeline": "migration_world",
        "lineage_graph": "lineage_scroll",
        "concept_mechanics_cutaway": "concept_cutaway",
        "archival_portrait": "period_portrait",
        "document_quote_closeup": "archive_world",
        "artifact_cold_open": "period_scene",
        "illustrated_reconstruction": "historical_reconstruction",
        "chapter_cta": "editorial_card",
    }.get(function, "editorial_scene")


def _prompt_for_block(
    excerpt: str,
    *,
    function: str,
    archetype: str,
    style_atoms: list[str],
) -> str:
    source = _visual_source(function)
    return (
        "Use case: historical-scene. Asset type: original editorial illustration plate. "
        f"Primary request: create one distinct {source} visual for the narration beat: "
        f"{excerpt!r}. Style/medium: original Japanese woodblock-informed branded literature, "
        "deep navy ink, weathered warm paper, rust, ochre, and jade accents, layered paper depth, "
        "deliberately illustrated rather than photoreal. "
        f"Composition: {archetype}; make the beat readable as a standalone image and leave a calm "
        f"safe region for post captions. Internal style atoms: {', '.join(style_atoms) or 'woodblock-paper-field, carved-ink-contour'}. "
        "Do not place any words, letters, numbers, map labels, dates, citations, logos, watermarks, "
        "or speech balloons inside the image. Do not imitate a named creator or copy a reference frame. "
        "Do not invent a historical likeness; use anonymous illustrative silhouettes unless an approved "
        "local portrait is composited later. The plate is atmosphere and visual explanation only; "
        "Remotion will add reviewed facts and citations after generation."
    )


def _timestamp_text(seconds: float) -> str:
    minutes, remainder = divmod(max(0.0, seconds), 60.0)
    return f"{int(minutes):02d}:{remainder:06.3f}"


def _prompt_spine(
    value: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    payload = _load(value, "timestamped plate prompt spine")
    errors: list[str] = []
    if payload.get("schema_version") != TIMESTAMPED_PROMPT_SPINE_VERSION:
        errors.append(
            f"prompt spine must use {TIMESTAMPED_PROMPT_SPINE_VERSION}"
        )
    global_rules = payload.get("global_continuity")
    if not isinstance(global_rules, Mapping):
        errors.append("prompt spine global_continuity must be an object")
    chapters = payload.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        errors.append("prompt spine chapters must be a non-empty array")
        chapters = []
    seen: set[str] = set()
    normalized_chapters: list[dict[str, Any]] = []
    for index, raw in enumerate(chapters):
        label = f"prompt spine chapters[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        item = copy.deepcopy(dict(raw))
        chapter_id = str(item.get("chapter_id") or "")
        if not _SAFE_ID.fullmatch(chapter_id):
            errors.append(f"{label}.chapter_id must be a safe ID")
        if chapter_id in seen:
            errors.append(f"{label}.chapter_id duplicates {chapter_id!r}")
        seen.add(chapter_id)
        for key in (
            "story_world",
            "visual_arc",
            "entry_motif",
            "exit_motif",
            "character_staging",
        ):
            if not str(item.get(key) or "").strip():
                errors.append(f"{label}.{key} is required")
        motifs = item.get("recurring_motifs")
        if not isinstance(motifs, list) or not motifs or not all(
            isinstance(motif, str) and motif.strip() for motif in motifs
        ):
            errors.append(f"{label}.recurring_motifs must be a non-empty string array")
        normalized_chapters.append(item)
    raw_sequences = payload.get("shot_sequences")
    if not isinstance(raw_sequences, list) or not raw_sequences:
        errors.append("prompt spine shot_sequences must be a non-empty array")
        raw_sequences = []
    sequences: dict[str, list[str]] = {}
    for index, raw in enumerate(raw_sequences):
        label = f"prompt spine shot_sequences[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        parent_shot_id = str(raw.get("parent_shot_id") or "")
        if not _SAFE_ID.fullmatch(parent_shot_id):
            errors.append(f"{label}.parent_shot_id must be a safe ID")
        if parent_shot_id in sequences:
            errors.append(f"{label}.parent_shot_id duplicates {parent_shot_id!r}")
        directions = raw.get("plate_directions")
        if not isinstance(directions, list) or not directions or not all(
            isinstance(direction, str) and direction.strip() for direction in directions
        ):
            errors.append(f"{label}.plate_directions must be a non-empty string array")
            directions = []
        sequences[parent_shot_id] = [str(direction).strip() for direction in directions]
    declared_hash = str(payload.get("artifact_hash") or "").casefold()
    core = {key: item for key, item in payload.items() if key != "artifact_hash"}
    actual_hash = canonical_sha256(core)
    if declared_hash and declared_hash != actual_hash:
        errors.append("prompt spine artifact_hash is stale")
    if errors:
        raise GeneratedBlockImageError(errors)
    return {
        **payload,
        "global_continuity": copy.deepcopy(dict(global_rules)),
        "chapters": normalized_chapters,
        "shot_sequences": sequences,
        "artifact_hash": actual_hash,
    }


def _timestamp_prompt_for_slot(
    slot: Mapping[str, Any],
    *,
    order: int,
    chapter: Mapping[str, Any],
    global_continuity: Mapping[str, Any],
    visual_direction: str,
    previous_slot: Mapping[str, Any] | None,
    next_slot: Mapping[str, Any] | None,
    style_atoms: list[str],
) -> str:
    start_s = float(slot.get("start_s") or 0.0)
    duration_s = float(slot.get("duration_s") or 0.0)
    end_s = start_s + duration_s
    excerpt = " ".join(str(slot.get("narration_excerpt") or "").split())
    function = str(slot.get("function") or "artifact_cold_open")
    archetype = str(slot.get("visual_archetype") or _visual_source(function))
    prior = (
        str(previous_slot.get("visual_archetype") or "previous visual")
        if previous_slot is not None
        else str(chapter.get("entry_motif") or "chapter entry")
    )
    following = (
        str(next_slot.get("visual_archetype") or "next visual")
        if next_slot is not None
        else str(chapter.get("exit_motif") or "chapter exit")
    )
    locks = "; ".join(
        str(item).strip()
        for item in global_continuity.get("locks", [])
        if isinstance(item, str) and item.strip()
    )
    output = str(global_continuity.get("output") or "16:9 landscape production plate")
    return (
        f"Create plate {order:03d} for the exact narration interval "
        f"{_timestamp_text(start_s)}–{_timestamp_text(end_s)} ({duration_s:.3f}s). "
        f"Narration beat: {excerpt!r}. Story world: {str(chapter.get('story_world') or '').strip()}. "
        f"Visual arc: {str(chapter.get('visual_arc') or '').strip()}. "
        f"Use a distinct {archetype} composition. Exact visual direction: {visual_direction}. "
        f"It follows {prior} and prepares {following}. "
        f"Continuity motifs: {', '.join(str(item) for item in chapter.get('recurring_motifs') or [])}. "
        f"Character staging: {str(chapter.get('character_staging') or '').strip()}. "
        f"Output: {output}. Style locks: {locks}. Internal style atoms: {', '.join(style_atoms)}. "
        "The plate must be an original, non-photorealistic historical editorial illustration with no readable words, "
        "dates, labels, citations, logos, watermarks, diagrams, or factual text. Do not imitate a named creator, "
        "copy a reference frame, or invent a historical likeness. Use anonymous period figures only; approved archival "
        "portraits and all factual surfaces are composited later. Preserve a calm negative-space area for a local fact "
        "surface, keep the full composition inside frame, and make this plate visibly different from its adjacent plates."
    )


def compile_timestamped_plate_plan(
    coverage: Mapping[str, Any] | str | Path,
    *,
    prompt_spine: Mapping[str, Any] | str | Path,
    art_bible_id: str = "",
    art_bible_hash: str = "",
    style_atoms: list[str] | None = None,
) -> dict[str, Any]:
    """Compile one image prompt for every timestamped coverage slot.

    This is intentionally separate from ``compile_generated_block_plan``:
    legacy block plans may group continuation slots, while this production lane
    treats the canonical narration timeline as the image-generation schedule.
    """

    payload = _load(coverage, "editorial coverage")
    if payload.get("schema_version") != "editorial_coverage.v1":
        raise GeneratedBlockImageError(
            ["timestamped plate planning requires editorial_coverage.v1"]
        )
    slots = payload.get("slots")
    if not isinstance(slots, list) or not slots:
        raise GeneratedBlockImageError(["editorial coverage requires slots"])
    spine = _prompt_spine(prompt_spine)
    chapters = {
        str(item.get("chapter_id") or ""): item
        for item in spine["chapters"]
    }
    slot_counts_by_parent: dict[str, int] = defaultdict(int)
    for raw in slots:
        if isinstance(raw, Mapping):
            slot_counts_by_parent[str(raw.get("parent_shot_id") or "")] += 1
    errors: list[str] = []
    for parent_shot_id, count in slot_counts_by_parent.items():
        directions = spine["shot_sequences"].get(parent_shot_id)
        if directions is None:
            errors.append(
                f"prompt spine has no shot sequence for parent_shot_id {parent_shot_id!r}"
            )
        elif len(directions) != count:
            errors.append(
                f"prompt spine sequence {parent_shot_id!r} has {len(directions)} directions; expected {count}"
            )
    unused_sequences = set(spine["shot_sequences"]) - set(slot_counts_by_parent)
    for parent_shot_id in sorted(unused_sequences):
        errors.append(
            f"prompt spine sequence {parent_shot_id!r} does not match a coverage parent shot"
        )
    if errors:
        raise GeneratedBlockImageError(errors)
    atoms = list(style_atoms or [
        "woodblock-paper-field",
        "carved-ink-contour",
        "limited-period-palette",
        "layered-editorial-depth",
    ])
    blocks: list[dict[str, Any]] = []
    errors = []
    previous_end = 0.0
    seen_slots: set[str] = set()
    position_by_parent: dict[str, int] = defaultdict(int)
    for index, raw in enumerate(slots, start=1):
        label = f"slots[{index - 1}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        slot = dict(raw)
        slot_id = str(slot.get("slot_id") or "")
        if not _SAFE_ID.fullmatch(slot_id) or slot_id in seen_slots:
            errors.append(f"{label}.slot_id must be a unique safe ID")
        seen_slots.add(slot_id)
        chapter_id = str(slot.get("chapter_id") or "")
        chapter = chapters.get(chapter_id)
        if chapter is None:
            errors.append(f"{label}.chapter_id {chapter_id!r} is missing from the prompt spine")
            continue
        parent_shot_id = str(slot.get("parent_shot_id") or "")
        directions = spine["shot_sequences"].get(parent_shot_id)
        position = position_by_parent[parent_shot_id]
        position_by_parent[parent_shot_id] += 1
        if directions is None or position >= len(directions):
            errors.append(f"{label} has no exact visual direction")
            continue
        visual_direction = directions[position]
        try:
            start_s = float(slot["start_s"])
            duration_s = float(slot["duration_s"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"{label} requires numeric start_s and duration_s")
            continue
        if duration_s <= 0 or start_s < 0:
            errors.append(f"{label} requires a positive duration_s and non-negative start_s")
            continue
        if index > 1 and abs(start_s - previous_end) > 1e-3:
            errors.append(f"{label}.start_s does not follow the preceding timestamp")
        previous_end = start_s + duration_s
        previous_slot = slots[index - 2] if index > 1 and isinstance(slots[index - 2], Mapping) else None
        next_slot = slots[index] if index < len(slots) and isinstance(slots[index], Mapping) else None
        blocks.append(
            {
                "block_id": _block_id(index, slot_id),
                "order": index,
                "coverage_slot_ids": [slot_id],
                "start_s": round(start_s, 6),
                "end_s": round(start_s + duration_s, 6),
                "narration_excerpt": " ".join(str(slot.get("narration_excerpt") or "").split()),
                "chapter_id": chapter_id,
                "function": str(slot.get("function") or "artifact_cold_open"),
                "visual_archetype": str(slot.get("visual_archetype") or "editorial_scene"),
                "visual_source": str(slot.get("selected_visual_source") or slot.get("preferred_visual_source") or "original_illustration"),
                "visual_direction": visual_direction,
                "duration_s": round(duration_s, 6),
                "motion_recipe": str(slot.get("motion_recipe") or "detail_punch"),
                "claim_refs": copy.deepcopy(list(slot.get("claim_refs") or [])),
                "citation_refs": copy.deepcopy(list(slot.get("citation_refs") or [])),
                "prompt": _timestamp_prompt_for_slot(
                    slot,
                    order=index,
                    chapter=chapter,
                    global_continuity=spine["global_continuity"],
                    visual_direction=visual_direction,
                    previous_slot=previous_slot,
                    next_slot=next_slot,
                    style_atoms=atoms,
                ),
                "planned_path": f"timestamped_plates/{index:03d}_{slot_id}.png",
                "status": "planned",
                "render_eligible": False,
                "evidence_eligible": False,
                "contains_factual_text": False,
                "disclosure_label": "AI-assisted illustration / reconstruction",
            }
        )
    if errors:
        raise GeneratedBlockImageError(errors)
    core = {
        "schema_version": TIMESTAMPED_PLATE_PLAN_VERSION,
        "provider": "openai-built-in-image-generation",
        "coverage_plan_hash": str(payload.get("artifact_hash") or canonical_sha256(payload)),
        "prompt_spine_hash": spine["artifact_hash"],
        "art_bible_id": art_bible_id,
        "art_bible_hash": art_bible_hash,
        "style_atoms": atoms,
        "plate_count": len(blocks),
        "duration_s": round(previous_end, 6),
        "one_primary_plate_per_timestamp_slot": True,
        "blocks": blocks,
        "policy": {
            "generated_pixels_are_not_evidence": True,
            "factual_overlay_owner": "remotion",
            "provider_output_render_eligible": False,
            "reuse_requires_explicit_continuity_reprise": True,
            "batch_review_size_max": 12,
        },
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def validate_timestamped_plate_plan(
    value: Mapping[str, Any] | str | Path,
    *,
    expected_coverage: Mapping[str, Any] | str | Path | None = None,
    expected_prompt_spine: Mapping[str, Any] | str | Path | None = None,
) -> dict[str, Any]:
    """Fail closed when timestamp coverage is incomplete, reused, or stale."""

    payload = _load(value, "timestamped plate plan")
    errors: list[str] = []
    if payload.get("schema_version") != TIMESTAMPED_PLATE_PLAN_VERSION:
        errors.append(f"timestamped plate plan must use {TIMESTAMPED_PLATE_PLAN_VERSION}")
    if payload.get("one_primary_plate_per_timestamp_slot") is not True:
        errors.append("one_primary_plate_per_timestamp_slot must be true")
    blocks = payload.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        errors.append("timestamped plate plan requires blocks")
        blocks = []
    previous_end = 0.0
    seen_slots: set[str] = set()
    for index, raw in enumerate(blocks):
        label = f"blocks[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        slot_ids = raw.get("coverage_slot_ids")
        if not isinstance(slot_ids, list) or len(slot_ids) != 1:
            errors.append(f"{label}.coverage_slot_ids must contain exactly one timestamp slot")
            continue
        slot_id = str(slot_ids[0] or "")
        if slot_id in seen_slots:
            errors.append(f"{label} reuses timestamp slot {slot_id!r}")
        seen_slots.add(slot_id)
        try:
            start_s = float(raw["start_s"])
            end_s = float(raw["end_s"])
            duration_s = float(raw["duration_s"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"{label} requires numeric start_s, end_s, and duration_s")
            continue
        if start_s < 0 or end_s <= start_s or abs((end_s - start_s) - duration_s) > 1e-3:
            errors.append(f"{label} has invalid timestamp bounds")
        if index and abs(start_s - previous_end) > 1e-3:
            errors.append(f"{label}.start_s is not contiguous with the previous plate")
        previous_end = end_s
        if not str(raw.get("prompt") or "").strip():
            errors.append(f"{label}.prompt is required")
        if not str(raw.get("visual_direction") or "").strip():
            errors.append(f"{label}.visual_direction is required")
    core = {key: item for key, item in payload.items() if key != "artifact_hash"}
    actual_hash = canonical_sha256(core)
    if str(payload.get("artifact_hash") or "").casefold() != actual_hash:
        errors.append("timestamped plate plan artifact_hash is stale")
    if expected_coverage is not None:
        coverage = _load(expected_coverage, "editorial coverage")
        expected_ids = [
            str(slot.get("slot_id") or "")
            for slot in coverage.get("slots") or []
            if isinstance(slot, Mapping)
        ]
        if str(payload.get("coverage_plan_hash") or "") != str(coverage.get("artifact_hash") or canonical_sha256(coverage)):
            errors.append("timestamped plate plan coverage_plan_hash is stale")
        if expected_ids != [
            str((item.get("coverage_slot_ids") or [""])[0])
            for item in blocks
            if isinstance(item, Mapping)
        ]:
            errors.append("timestamped plate plan does not cover every coverage slot in order")
    if expected_prompt_spine is not None:
        spine = _prompt_spine(expected_prompt_spine)
        if payload.get("prompt_spine_hash") != spine["artifact_hash"]:
            errors.append("timestamped plate plan prompt_spine_hash is stale")
    if errors:
        raise GeneratedBlockImageError(errors)
    return {**payload, "artifact_hash": actual_hash}


def compile_generated_block_plan(
    coverage: Mapping[str, Any] | str | Path,
    *,
    art_bible_id: str = "",
    art_bible_hash: str = "",
    style_atoms: list[str] | None = None,
) -> dict[str, Any]:
    """Group coverage by meaningful narration excerpt and create one prompt per block."""

    payload = _load(coverage, "editorial coverage")
    if payload.get("schema_version") != "editorial_coverage.v1":
        raise GeneratedBlockImageError(
            ["generated image block planning requires editorial_coverage.v1"]
        )
    slots = payload.get("slots")
    if not isinstance(slots, list) or not slots:
        raise GeneratedBlockImageError(["editorial coverage requires slots"])

    grouped: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for index, raw in enumerate(slots):
        if not isinstance(raw, Mapping):
            raise GeneratedBlockImageError([f"slots[{index}] must be an object"])
        excerpt = " ".join(str(raw.get("narration_excerpt") or "").split())
        if not excerpt:
            raise GeneratedBlockImageError([f"slots[{index}] narration_excerpt is required"])
        grouped.setdefault(excerpt.casefold(), []).append(dict(raw))

    atoms = list(style_atoms or [
        "woodblock-paper-field",
        "carved-ink-contour",
        "limited-period-palette",
        "layered-editorial-depth",
    ])
    blocks: list[dict[str, Any]] = []
    for index, records in enumerate(grouped.values(), start=1):
        first = records[0]
        slot_ids = [str(record.get("slot_id") or "") for record in records]
        function = str(first.get("function") or "artifact_cold_open")
        excerpt = " ".join(str(first.get("narration_excerpt") or "").split())
        archetype = str(first.get("visual_archetype") or _visual_source(function))
        blocks.append(
            {
                "block_id": _block_id(index, slot_ids[0]),
                "order": index,
                "coverage_slot_ids": slot_ids,
                "narration_excerpt": excerpt,
                "function": function,
                "visual_archetype": archetype,
                "visual_source": _visual_source(function),
                "duration_s": round(sum(float(record.get("duration_s") or 0) for record in records), 6),
                "motion_recipe": str(first.get("motion_recipe") or "detail_punch"),
                "prompt": _prompt_for_block(
                    excerpt,
                    function=function,
                    archetype=archetype,
                    style_atoms=atoms,
                ),
                "planned_path": f"generated_blocks/{index:03d}.png",
                "status": "planned",
                "render_eligible": False,
                "evidence_eligible": False,
                "contains_factual_text": False,
                "disclosure_label": "AI-assisted illustration / reconstruction",
            }
        )

    core = {
        "schema_version": GENERATED_BLOCK_PLAN_VERSION,
        "provider": "openai-built-in-image-generation",
        "coverage_plan_hash": str(payload.get("artifact_hash") or canonical_sha256(payload)),
        "art_bible_id": art_bible_id,
        "art_bible_hash": art_bible_hash,
        "style_atoms": atoms,
        "block_count": len(blocks),
        "coverage_slot_count": len(slots),
        "one_generated_plate_per_block": True,
        "blocks": blocks,
        "policy": {
            "generated_pixels_are_not_evidence": True,
            "factual_overlay_owner": "remotion",
            "provider_output_render_eligible": False,
            "minimum_block_count_for_ten_minute_episode": 60,
        },
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def validate_generated_block_batch(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    expected_plan: Mapping[str, Any] | str | Path | None = None,
    check_files: bool = True,
) -> dict[str, Any]:
    """Validate generated files and their exact coverage mapping."""

    payload = _load(value, "generated image block batch")
    root = Path(job_root).resolve()
    errors: list[str] = []
    if payload.get("schema_version") != GENERATED_BLOCK_BATCH_VERSION:
        errors.append(f"schema_version must be {GENERATED_BLOCK_BATCH_VERSION}")
    if payload.get("one_generated_plate_per_block") is not True:
        errors.append("one_generated_plate_per_block must be true")
    blocks = payload.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        errors.append("blocks must contain at least one generated block")
        blocks = []

    expected_blocks: list[Mapping[str, Any]] = []
    expected_hash = ""
    if expected_plan is not None:
        plan = _load(expected_plan, "generated image block plan")
        expected_blocks = [item for item in plan.get("blocks", []) if isinstance(item, Mapping)]
        expected_hash = str(plan.get("artifact_hash") or "")
        if payload.get("plan_hash") != expected_hash:
            errors.append("generated image batch plan_hash is stale or missing")

    seen_ids: set[str] = set()
    seen_slots: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(blocks):
        label = f"blocks[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        item = copy.deepcopy(dict(raw))
        block_id = str(item.get("block_id") or "")
        if not _SAFE_ID.fullmatch(block_id):
            errors.append(f"{label}.block_id must be a safe lowercase ID")
        if block_id in seen_ids:
            errors.append(f"{label}.block_id duplicates {block_id!r}")
        seen_ids.add(block_id)
        slot_ids = item.get("coverage_slot_ids")
        if not isinstance(slot_ids, list) or not slot_ids or not all(isinstance(slot, str) and slot for slot in slot_ids):
            errors.append(f"{label}.coverage_slot_ids must contain non-empty strings")
            slot_ids = []
        for slot_id in slot_ids:
            if slot_id in seen_slots:
                errors.append(f"{label} reuses coverage slot {slot_id!r}")
            seen_slots.add(slot_id)
        if str(item.get("source_kind") or "") != "ai_assisted_illustration":
            errors.append(f"{label}.source_kind must be ai_assisted_illustration")
        for key in ("render_eligible", "evidence_eligible", "contains_factual_text"):
            if item.get(key) is not False:
                errors.append(f"{label}.{key} must remain false")
        disclosure = str(item.get("disclosure_label") or "")
        if not re.search(r"illustration|reconstruction", disclosure, re.I):
            errors.append(f"{label}.disclosure_label must identify illustration/reconstruction")
        prompt = str(item.get("prompt") or "")
        for term in _PROHIBITED_PROMPT_LANGUAGE:
            if term in prompt.casefold():
                errors.append(f"{label}.prompt contains prohibited source/style language")
        path_text = str(item.get("path") or item.get("planned_path") or "").strip()
        if not path_text:
            errors.append(f"{label}.path is required")
        elif Path(path_text).is_absolute() or _is_remote(path_text):
            errors.append(f"{label}.path must be job-relative")
        resolved = _resolve_local(path_text, root) if path_text else None
        if check_files and resolved is None and path_text:
            errors.append(f"{label}.path does not resolve inside the job directory")
        declared_sha = str(item.get("sha256") or "").casefold()
        if not _HEX64.fullmatch(declared_sha):
            errors.append(f"{label}.sha256 must be a lowercase SHA-256 digest")
        if resolved is not None and _HEX64.fullmatch(declared_sha) and _file_sha256(resolved) != declared_sha:
            errors.append(f"{label}.sha256 is stale")
        normalized.append({**item, "block_id": block_id, "coverage_slot_ids": slot_ids, "path": path_text, "sha256": declared_sha, "source_kind": "ai_assisted_illustration"})

    if expected_blocks:
        expected_ids = {str(item.get("block_id") or "") for item in expected_blocks}
        actual_ids = {str(item.get("block_id") or "") for item in normalized}
        if expected_ids != actual_ids:
            errors.append("generated image batch block IDs do not match the plan")
        expected_slots = {
            str(slot)
            for item in expected_blocks
            for slot in item.get("coverage_slot_ids", [])
        }
        if expected_slots != seen_slots:
            errors.append("generated image batch coverage slots do not match the plan")

    declared_hash = str(payload.get("artifact_hash") or "").casefold()
    core = {key: value for key, value in payload.items() if key != "artifact_hash"}
    actual_hash = canonical_sha256(core)
    if declared_hash and declared_hash != actual_hash:
        errors.append("generated image batch artifact_hash is stale")
    if errors:
        raise GeneratedBlockImageError(errors)
    return {**payload, "blocks": normalized, "plan_hash": expected_hash or str(payload.get("plan_hash") or ""), "artifact_hash": actual_hash}


__all__ = [
    "GENERATED_BLOCK_BATCH_VERSION",
    "GENERATED_BLOCK_PLAN_VERSION",
    "TIMESTAMPED_PLATE_PLAN_VERSION",
    "TIMESTAMPED_PLATE_CANDIDATE_INVENTORY_VERSION",
    "TIMESTAMPED_PROMPT_SPINE_VERSION",
    "GeneratedBlockImageError",
    "compile_generated_block_plan",
    "compile_timestamped_plate_asset_manifest",
    "compile_timestamped_plate_plan",
    "replace_timestamped_plate_candidate",
    "validate_timestamped_plate_plan",
    "validate_generated_block_batch",
]
