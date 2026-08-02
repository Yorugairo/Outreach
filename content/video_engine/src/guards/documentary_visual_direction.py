"""Human Visual Direction Gate for History Documentary V4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from content.video_engine.src.services.documentary_style_board import (
    DOCUMENTARY_RUBRIC_DIMENSIONS,
    DOCUMENTARY_STYLE_BOARD_ROLES,
)
from content.video_engine.src.services.documentary_treatment import canonical_sha256


VISUAL_DIRECTION_VERSION = "documentary_visual_direction.v1"
MIN_SCORE = 4.0


def _load(value: Any, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    root = Path(value)
    if root.is_dir():
        root = root / "style_board" / "style_board.json"
        if not root.is_file():
            root = Path(value) / "style_board.json"
    if not root.is_file():
        raise FileNotFoundError(f"{label} does not exist: {root}")
    payload = json.loads(root.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{label} must be an object")
    return dict(payload)


def _scores(rubric: Mapping[str, Any]) -> Mapping[str, Any]:
    value = rubric.get("scores") or rubric.get("dimensions") or rubric.get("rubric")
    return value if isinstance(value, Mapping) else {}


def validate_documentary_visual_approval(
    style_board: Mapping[str, Any] | str | Path,
    rubric: Mapping[str, Any] | str | Path,
    expected_art_bible_hash: str | None = None,
) -> list[str]:
    """Return errors; an empty list means the operator rubric is acceptable.

    This function validates the rubric only.  It never writes approval state,
    so the caller remains responsible for the human gate transition.
    """

    errors: list[str] = []
    try:
        board = _load(style_board, "documentary style board")
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return [f"style board could not be loaded: {exc}"]
    try:
        packet = _load(rubric, "visual direction rubric")
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return [f"visual direction rubric could not be loaded: {exc}"]

    board_hash = str(board.get("art_bible_hash") or "").strip().lower()
    if len(board_hash) != 64:
        errors.append("style board is missing a valid art_bible_hash")
    current_hash = str(expected_art_bible_hash or board_hash).strip().lower()
    rubric_hash = str(packet.get("art_bible_hash") or "").strip().lower()
    if rubric_hash != current_hash:
        errors.append(f"rubric art_bible_hash {rubric_hash!r} does not match current {current_hash!r}")
    if board_hash != current_hash:
        errors.append(f"style board art_bible_hash {board_hash!r} does not match current {current_hash!r}")
    if board.get("approval_granted") is True:
        errors.append("style board approval_granted must remain false until operator transition")

    roles = board.get("roles") or board.get("required_roles") or []
    if not isinstance(roles, list) or set(str(value) for value in roles) != set(DOCUMENTARY_STYLE_BOARD_ROLES):
        errors.append("documentary style board must contain the six required roles: " + ", ".join(DOCUMENTARY_STYLE_BOARD_ROLES))
    stills = board.get("stills")
    if not isinstance(stills, list) or len(stills) != len(DOCUMENTARY_STYLE_BOARD_ROLES):
        errors.append("documentary style board must contain exactly six stills")
    else:
        still_roles = [str(item.get("role") or "") for item in stills if isinstance(item, Mapping)]
        missing = sorted(set(DOCUMENTARY_STYLE_BOARD_ROLES) - set(still_roles))
        if missing:
            errors.append("style board missing roles: " + ", ".join(missing))
        if len(set(still_roles)) != len(still_roles):
            errors.append("style board still roles must be unique")
        for index, still in enumerate(stills, start=1):
            if not isinstance(still, Mapping):
                errors.append(f"style board still {index} is not an object")
                continue
            safe = still.get("safe_zones")
            if not isinstance(safe, Mapping):
                errors.append(f"style board still {index} is missing safe zones")
                continue
            for aspect in ("landscape", "vertical"):
                zone = safe.get(aspect)
                if not isinstance(zone, Mapping) or not zone.get("action_zone") or not zone.get("caption_zone"):
                    errors.append(f"style board still {index} is missing {aspect} action/caption safe zones")

    scores = _scores(packet)
    if set(str(key) for key in scores) != set(DOCUMENTARY_RUBRIC_DIMENSIONS):
        errors.append("documentary rubric must contain the six rubric dimensions: " + ", ".join(DOCUMENTARY_RUBRIC_DIMENSIONS))
    for dimension in DOCUMENTARY_RUBRIC_DIMENSIONS:
        value = scores.get(dimension)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"rubric score {dimension!r} must be numeric")
            continue
        if value < 1 or value > 5:
            errors.append(f"rubric score {dimension!r} must be between 1 and 5")
        elif value < MIN_SCORE:
            errors.append(f"rubric score {dimension!r} is below the 4/5 threshold")

    # A supplied artifact hash is useful evidence, but it must be computed
    # from the board core rather than allowing stale hand-edited packets.
    supplied_hash = board.get("artifact_hash")
    board_core = dict(board)
    for transient in ("artifact_path", "review_packet_path"):
        board_core.pop(transient, None)
    if supplied_hash and supplied_hash != canonical_sha256(board_core):
        errors.append("style board artifact_hash does not match canonical content")
    return sorted(set(errors))


def validate_visual_approval(
    style_board: Mapping[str, Any] | str | Path,
    rubric: Mapping[str, Any] | str | Path,
    expected_art_bible_hash: str | None = None,
) -> list[str]:
    """Compatibility alias used by gate orchestration."""

    return validate_documentary_visual_approval(style_board, rubric, expected_art_bible_hash)


__all__ = [
    "DOCUMENTARY_RUBRIC_DIMENSIONS",
    "DOCUMENTARY_STYLE_BOARD_ROLES",
    "MIN_SCORE",
    "VISUAL_DIRECTION_VERSION",
    "validate_documentary_visual_approval",
    "validate_visual_approval",
]
