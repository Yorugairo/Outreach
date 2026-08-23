"""Record scene-pack selections into the existing review contract.

Selection is exception-based. Every slot already carries an auto-selected
default from the board, so a 150-slot episode records cleanly with zero
operator input; an operator payload only has to name the slots they changed.

``approved`` is never set by product code. Gate A and Gate B are operator
actions per ``content/video_engine/AGENTS.md``; this module requires an
explicit flag and records who set it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.models import utc_now_iso
from content.video_engine.src.services.artifact_io import (
    load_json,
    stamp_artifact_hash,
    write_artifact,
)

ASSET_SELECTION_REVIEW_VERSION = "asset_selection_review.v1"
VIDEO_INTENT_VERSION = "video_intent.v1"

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _VIDEO_ENGINE_ROOT / "configs"


class SceneSelectionError(ValueError):
    """The selection payload could not be reconciled with the board."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid scene selection")


def _schema_errors(payload: Mapping[str, Any]) -> list[str]:
    schema = load_json(
        _CONFIG_DIR / "asset_selection_review.schema.json", "asset selection review schema"
    )
    validator = Draft7Validator(schema)
    return [
        "review" + "".join(f"[{part!r}]" for part in error.absolute_path) + f": {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda e: list(e.absolute_path))
    ]


def _operator_choices(payload: Mapping[str, Any] | None) -> dict[str, str]:
    """Collapse an operator payload to slot_id -> candidate_id, rejecting dupes."""

    if not payload:
        return {}
    chosen: dict[str, str] = {}
    errors: list[str] = []
    for index, entry in enumerate(payload.get("selections") or []):
        slot_id = str(entry.get("slot_id") or "").strip()
        candidate_id = entry.get("candidate_id")
        if not slot_id:
            errors.append(f"selections[{index}].slot_id is required")
            continue
        if candidate_id in (None, ""):
            continue
        if slot_id in chosen and chosen[slot_id] != str(candidate_id):
            errors.append(
                f"slot {slot_id!r} has multiple explicit selections; exactly one is allowed"
            )
            continue
        chosen[slot_id] = str(candidate_id)
    if errors:
        raise SceneSelectionError(errors)
    return chosen


def _resolve_slot(
    row: Mapping[str, Any], chosen: Mapping[str, str]
) -> tuple[str, str] | None:
    """Return ``(candidate_id, source)`` or ``None`` when the slot is unresolved."""

    slot_id = str(row.get("slot_id"))
    if slot_id in chosen:
        return chosen[slot_id], "operator"
    default = row.get("selected_candidate_id")
    if default:
        return str(default), "auto"
    return None


def _validate_against_board(
    rows: Sequence[Mapping[str, Any]], chosen: Mapping[str, str]
) -> list[str]:
    errors: list[str] = []
    known = {str(row.get("slot_id")) for row in rows}
    for slot_id in sorted(set(chosen) - known):
        errors.append(f"selection names unknown slot {slot_id!r}")
    for row in rows:
        slot_id = str(row.get("slot_id"))
        if slot_id not in chosen:
            continue
        ids = {str(item.get("id")) for item in row.get("candidates") or []}
        if chosen[slot_id] not in ids:
            errors.append(
                f"slot {slot_id!r} selects candidate {chosen[slot_id]!r}, which is not "
                "one of its candidates"
            )
    return errors


def build_selection_review(
    *,
    board: Mapping[str, Any] | str | Path,
    reviewed_by: str,
    operator_payload: Mapping[str, Any] | str | Path | None = None,
    approved: bool = False,
    entitlement_snapshot: Mapping[str, Any] | None = None,
    reviewed_at: str | None = None,
) -> dict[str, Any]:
    """Reconcile operator choices with board defaults into the review contract."""

    if not str(reviewed_by).strip():
        raise SceneSelectionError(["reviewed_by is required"])

    board_payload = load_json(board, "scene board")
    rows = list(board_payload.get("slots") or [])
    if not rows:
        raise SceneSelectionError(["board contains no slots"])

    raw = load_json(operator_payload, "selection payload") if operator_payload else None
    chosen = _operator_choices(raw)

    errors = _validate_against_board(rows, chosen)
    selections: list[dict[str, Any]] = []
    auto_slots: list[str] = []
    for row in rows:
        slot_id = str(row.get("slot_id"))
        resolved = _resolve_slot(row, chosen)
        if resolved is None:
            errors.append(f"slot {slot_id!r} has no selection and no usable default")
            continue
        candidate_id, source = resolved
        if source == "auto":
            auto_slots.append(slot_id)
        selections.append(
            {
                "slot_id": slot_id,
                "candidate_id": candidate_id,
                "approved_cost_usd": 0.0,
                "selection_source": source,
            }
        )
    if errors:
        raise SceneSelectionError(errors)

    review = {
        "schema_version": ASSET_SELECTION_REVIEW_VERSION,
        "coverage_hash": board_payload.get("coverage_hash"),
        "candidate_batch_hash": board_payload.get("candidate_batch_hash"),
        "timing_basis": board_payload.get("timing_basis", "canonical"),
        "approved": bool(approved),
        "reviewed_by": str(reviewed_by),
        "reviewed_at": reviewed_at or utc_now_iso(),
        "auto_selected_slot_ids": auto_slots,
        "selections": selections,
    }
    if entitlement_snapshot:
        review["entitlement_snapshot"] = dict(entitlement_snapshot)

    schema_errors = _schema_errors(review)
    if schema_errors:
        raise SceneSelectionError(schema_errors)
    return review


def build_video_intents(
    board: Mapping[str, Any], review: Mapping[str, Any]
) -> dict[str, Any]:
    """One intent per selected slot, with no provider bound.

    Tier 3 exists as a contract only. Nothing here releases a paid job; the
    queue stays paused and ``provider`` stays unset until an operator binds one.
    """

    by_slot = {str(row.get("slot_id")): row for row in board.get("slots") or []}
    intents = [
        {
            "slot_id": entry["slot_id"],
            "candidate_id": entry["candidate_id"],
            "duration_s": by_slot.get(entry["slot_id"], {}).get("duration_s"),
            "motion_recipe": by_slot.get(entry["slot_id"], {}).get("motion_recipe"),
            "provider": None,
            "status": "not_requested",
        }
        for entry in review.get("selections") or []
    ]
    payload = {
        "schema_version": VIDEO_INTENT_VERSION,
        "coverage_hash": review.get("coverage_hash"),
        "intent_count": len(intents),
        "intents": intents,
    }
    return stamp_artifact_hash(payload)


def record_scene_selection(
    *,
    board: Mapping[str, Any] | str | Path,
    output_dir: str | Path,
    reviewed_by: str,
    operator_payload: Mapping[str, Any] | str | Path | None = None,
    approved: bool = False,
    entitlement_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist the review and the unbound video intents."""

    board_payload = load_json(board, "scene board")
    review = build_selection_review(
        board=board_payload,
        reviewed_by=reviewed_by,
        operator_payload=operator_payload,
        approved=approved,
        entitlement_snapshot=entitlement_snapshot,
    )
    intents = build_video_intents(board_payload, review)

    out = Path(output_dir)
    review_path = write_artifact(out / "asset_selection_review.json", review)
    intents_path = write_artifact(out / "video_intents.json", intents)
    operator_count = sum(
        1 for entry in review["selections"] if entry.get("selection_source") == "operator"
    )
    return {
        "review_path": str(review_path),
        "video_intents_path": str(intents_path),
        "selection_count": len(review["selections"]),
        "auto_selected": len(review["auto_selected_slot_ids"]),
        "operator_selected": operator_count,
        "approved": review["approved"],
    }
