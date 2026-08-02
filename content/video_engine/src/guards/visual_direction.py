"""Human Visual Direction Gate validation for the V3 style board.

The guard validates evidence supplied by an operator.  It never changes a
run's gate status and it does not infer approval from machine-green checks.
Callers receive stable, actionable error strings so the same result can be
persisted in a review packet or displayed by the CLI.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from content.video_engine.src.services.style_board import (
    REQUIRED_STILL_ROLES,
    STYLE_BOARD_STILL_ROLES,
)


VISUAL_DIRECTION_VERSION = "visual_direction.v1"
# The names are intentionally product-facing rather than renderer internals.
# The parser accepts common aliases, then normalizes every accepted score to
# exactly these six canonical dimensions.
VISUAL_DIRECTION_DIMENSIONS: tuple[str, ...] = (
    "originality",
    "hierarchy",
    "body_ownership",
    "typography",
    "diagram_integration",
    "audience_clarity",
)
REQUIRED_DIMENSIONS = VISUAL_DIRECTION_DIMENSIONS
RUBRIC_DIMENSIONS = VISUAL_DIRECTION_DIMENSIONS
MIN_VISUAL_DIRECTION_SCORE = 4

_DIMENSION_ALIASES: dict[str, frozenset[str]] = {
    "originality": frozenset(
        {"originality", "source_separation", "distinctiveness", "novelty"}
    ),
    "hierarchy": frozenset(
        {"hierarchy", "visual_hierarchy", "composition_clarity", "composition", "layout", "framing"}
    ),
    "body_ownership": frozenset(
        {"body_ownership", "cast_continuity", "cast", "character_continuity", "identity"}
    ),
    "typography": frozenset(
        {"typography", "type", "text", "label_legibility"}
    ),
    "diagram_integration": frozenset(
        {"diagram_integration", "diagram", "treatment_coherence", "treatment", "visual_treatment", "style_consistency"}
    ),
    "audience_clarity": frozenset(
        {"audience_clarity", "instructional_legibility", "legibility", "clarity", "mechanics", "brand_fit", "art_direction", "palette", "fit"}
    ),
}
_HASH_RE = re.compile(r"^[a-f0-9]{64}$")


class VisualDirectionValidationError(ValueError):
    """Raised by the exception-style validation API."""

    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors) or "visual direction is valid")


def _load(value: Any, label: str) -> Any:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    if isinstance(value, (str, Path)):
        path = Path(value)
        if not path.is_file():
            raise FileNotFoundError(f"{label} does not exist: {path}")
        return json.loads(path.read_text(encoding="utf-8"))
    raise TypeError(f"{label} must be a mapping or JSON path")


def _style_board_paths(job_dir: Path) -> tuple[Path, ...]:
    root = job_dir / "style_board"
    return (
        root / "style_board.json",
        root / "review-packet.json",
        root / "review_packet.json",
        job_dir / "style_board.json",
        job_dir / "style_board" / "review_packet.json",
    )


def _load_style_board(job_dir: str | Path | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(job_dir, Mapping):
        return job_dir
    root = Path(job_dir)
    for path in _style_board_paths(root):
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, Mapping):
                return payload
    raise FileNotFoundError(f"style-board artifact is missing under {root}")


def _still_entries(board: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    for key in ("stills", "frames", "entries"):
        value = board.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _normalized_role(value: Any) -> str:
    role = str(value or "").strip().casefold().replace("-", "_").replace(" ", "_")
    for canonical, aliases in {
        "hook": {"hook", "hero", "hero_frame", "result_preview", "opening"},
        "wide_setup": {"wide_setup", "wide", "context"},
        "contact_closeup": {"contact_closeup", "contact_detail", "detail", "closeup", "close_up"},
        "wrong_right_compare": {"wrong_right_compare", "wrong_right", "comparison", "compare"},
        "force_diagram": {"force_diagram", "diagram", "leverage_diagram", "force"},
        "result_hold": {"result_hold", "held_result", "result"},
    }.items():
        if role in aliases:
            return canonical
    return role


def _canonical_dimension_scores(rubric: Mapping[str, Any]) -> tuple[dict[str, float], list[str]]:
    candidate: Any = rubric.get("scores")
    if candidate is None:
        candidate = rubric.get("dimensions")
    if candidate is None and isinstance(rubric.get("rubric"), Mapping):
        nested = rubric["rubric"]
        candidate = nested.get("scores") or nested.get("dimensions")
        if candidate is None:
            candidate = nested
    values: dict[str, Any] = {}
    if isinstance(candidate, Mapping):
        values = dict(candidate)
    elif isinstance(candidate, Sequence) and not isinstance(candidate, (str, bytes, bytearray)):
        for item in candidate:
            if not isinstance(item, Mapping):
                continue
            name = item.get("id") or item.get("name") or item.get("dimension")
            if name is not None and (item.get("score") is not None or item.get("value") is not None):
                values[str(name)] = item.get("score", item.get("value"))
    if not values:
        # Direct ``{"originality": 4, ...}`` packets are convenient for
        # operators and were accepted by the early V3 prototype.
        values = {
            str(key): value
            for key, value in rubric.items()
            if str(key).casefold() not in {
                "schema_version",
                "art_bible_hash",
                "reviewer",
                "reviewed_by",
                "approved",
                "approval_granted",
                "notes",
                "artifact_hash",
            }
            and isinstance(value, (int, float))
            and not isinstance(value, bool)
        }
    errors: list[str] = []
    scores: dict[str, float] = {}
    for dimension, aliases in _DIMENSION_ALIASES.items():
        match = next(
            (
                key
                for key in values
                if str(key).casefold().replace("-", "_").replace(" ", "_") in aliases
            ),
            None,
        )
        if match is None:
            continue
        raw = values[match]
        try:
            score = float(raw)
        except (TypeError, ValueError):
            errors.append(f"dimension {dimension!r} is not numeric")
            continue
        scores[dimension] = score
    if len(scores) != len(VISUAL_DIRECTION_DIMENSIONS):
        errors.append(
            f"six rubric dimensions are required (found {len(scores)})"
        )
    for dimension, score in scores.items():
        if not 1 <= score <= 5:
            errors.append(f"dimension {dimension!r} must be between 1 and 5")
        elif score < MIN_VISUAL_DIRECTION_SCORE:
            errors.append(
                f"dimension {dimension!r} is below the 4/5 threshold ({score:g})"
            )
    return scores, errors


def _hash_from_board(board: Mapping[str, Any]) -> str:
    for key in (
        "art_bible_hash",
        "art_bible_artifact_hash",
        "artBibleHash",
        "current_art_bible_hash",
    ):
        value = board.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return ""


def _validate_board_shape(board: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    stills = _still_entries(board)
    if len(stills) != len(STYLE_BOARD_STILL_ROLES):
        errors.append(
            f"style board must contain exactly six stills (found {len(stills)})"
        )
    roles = {_normalized_role(item.get("role") or item.get("still_role")) for item in stills}
    missing = [role for role in REQUIRED_STILL_ROLES if role not in roles]
    # Some early V3 review packets used ``mechanic_transition`` in place of a
    # separate hook still.  Keep that reviewed six-frame vocabulary readable
    # while still enforcing six distinct, known roles.
    alternate = {
        "hook",
        "wide_setup",
        "contact_closeup",
        "mechanic_transition",
        "force_diagram",
        "result_hold",
    }
    if len(stills) == 6 and roles == alternate:
        missing = []
    if missing:
        errors.append("style board missing still roles: " + ", ".join(missing))
    return errors


def validate_visual_approval(
    job_dir: str | Path | Mapping[str, Any],
    rubric_path: str | Path | Mapping[str, Any],
    expected_art_bible_hash: str | None = None,
) -> list[str]:
    """Return all Visual Direction Gate errors; an empty list is valid.

    The function intentionally does not write ``job.json`` or set any gate
    status.  The parent pipeline decides when an operator's approval is
    persisted.
    """

    errors: list[str] = []
    try:
        board = _load_style_board(job_dir)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        return [f"style board could not be loaded: {exc}"]
    try:
        rubric = _load(rubric_path, "visual direction rubric")
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError) as exc:
        return [f"visual direction rubric could not be loaded: {exc}"]
    if not isinstance(rubric, Mapping):
        return ["visual direction rubric must be an object"]
    errors.extend(_validate_board_shape(board))
    board_hash = _hash_from_board(board)
    expected = str(expected_art_bible_hash or board_hash).strip().lower()
    if not board_hash:
        errors.append("style board is missing art_bible_hash")
    elif not _HASH_RE.fullmatch(board_hash):
        errors.append("style board art_bible_hash must be a 64-character SHA-256")
    if expected and board_hash and board_hash != expected:
        errors.append(
            f"style board art_bible_hash {board_hash!r} does not match current {expected!r}"
        )
    rubric_hash = str(
        rubric.get("art_bible_hash")
        or rubric.get("art_bible_artifact_hash")
        or rubric.get("artBibleHash")
        or rubric.get("current_art_bible_hash")
        or ""
    ).strip().lower()
    if not rubric_hash:
        errors.append("visual direction rubric is missing art_bible_hash")
    elif not _HASH_RE.fullmatch(rubric_hash):
        errors.append("rubric art_bible_hash must be a 64-character SHA-256")
    elif expected and rubric_hash != expected:
        errors.append(
            f"rubric art_bible_hash {rubric_hash!r} does not match current {expected!r}"
        )
    if board_hash and rubric_hash and board_hash != rubric_hash:
        errors.append("style board and rubric art_bible_hash values differ")
    _scores, score_errors = _canonical_dimension_scores(rubric)
    errors.extend(score_errors)
    return errors


def validate_visual_direction(
    style_board: Mapping[str, Any] | str | Path,
    rubric: Mapping[str, Any] | str | Path,
    expected_art_bible_hash: str | None = None,
) -> list[str]:
    """Direct-artifact alias for callers that do not have a job directory."""

    board = _load(style_board, "style board")
    if not isinstance(board, Mapping):
        return ["style board must be an object"]
    return validate_visual_approval(board, rubric, expected_art_bible_hash)


def visual_direction_ok(
    job_dir: str | Path | Mapping[str, Any],
    rubric_path: str | Path | Mapping[str, Any],
    expected_art_bible_hash: str | None = None,
) -> bool:
    return not validate_visual_approval(job_dir, rubric_path, expected_art_bible_hash)


class VisualDirectionGuard:
    """Small object adapter for dependency-injected pipeline callers."""

    def validate(
        self,
        job_dir: str | Path | Mapping[str, Any],
        rubric_path: str | Path | Mapping[str, Any],
        expected_art_bible_hash: str | None = None,
    ) -> list[str]:
        return validate_visual_approval(job_dir, rubric_path, expected_art_bible_hash)

    check = validate


__all__ = [
    "REQUIRED_DIMENSIONS",
    "RUBRIC_DIMENSIONS",
    "MIN_VISUAL_DIRECTION_SCORE",
    "VISUAL_DIRECTION_DIMENSIONS",
    "VISUAL_DIRECTION_VERSION",
    "VisualDirectionGuard",
    "VisualDirectionValidationError",
    "validate_visual_approval",
    "validate_visual_direction",
    "visual_direction_ok",
]
