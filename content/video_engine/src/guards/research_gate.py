"""Human Research Gate validation for History Documentary V4.

The gate is deliberately a pure check.  It never changes packet reviewer
state or auto-approves a run.  A rubric is valid only when all six editorial
dimensions are scored at least 4/5 and the rubric names the exact current
research-packet digest.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from content.video_engine.src.services.history_contracts import (
    HistoryContractService,
    HistoryContractValidationError,
    _load_json,
)


RESEARCH_GATE_VERSION = "research_gate.v1"
MIN_RESEARCH_GATE_SCORE = 4
RESEARCH_GATE_DIMENSIONS: tuple[str, ...] = (
    "thesis_clarity",
    "source_quality",
    "contested_framing",
    "claim_completeness",
    "promotional_neutrality",
    "rights_readiness",
)
REQUIRED_DIMENSIONS = RESEARCH_GATE_DIMENSIONS
RUBRIC_DIMENSIONS = RESEARCH_GATE_DIMENSIONS
_HASH_RE = re.compile(r"^[a-f0-9]{64}$")


class ResearchGateValidationError(ValueError):
    """Raised when a Research Gate review packet fails closed."""

    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("invalid research gate rubric: " + "; ".join(self.errors))


def _rubric_payload(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    return _load_json(value, "research gate rubric", root=root)


def _hash_from_rubric(rubric: Mapping[str, Any]) -> str:
    for key in (
        "research_hash",
        "research_packet_hash",
        "packet_hash",
        "current_research_hash",
        "artifact_hash",
        "content_hash",
    ):
        value = rubric.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return ""


def _canonical_dimension_scores(rubric: Mapping[str, Any]) -> tuple[dict[str, float], list[str]]:
    candidate: Any = rubric.get("scores")
    if candidate is None:
        candidate = rubric.get("dimensions")
    if candidate is None and isinstance(rubric.get("rubric"), Mapping):
        nested = rubric["rubric"]
        candidate = nested.get("scores") or nested.get("dimensions") or nested
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
        values = {
            str(key): value
            for key, value in rubric.items()
            if str(key).casefold() not in {
                "schema_version",
                "research_hash",
                "research_packet_hash",
                "packet_hash",
                "current_research_hash",
                "artifact_hash",
                "content_hash",
                "reviewer",
                "reviewed_by",
                "approved",
                "approval_granted",
                "notes",
            }
            and isinstance(value, (int, float))
            and not isinstance(value, bool)
        }
    errors: list[str] = []
    scores: dict[str, float] = {}
    for dimension in RESEARCH_GATE_DIMENSIONS:
        normalized = dimension.casefold().replace("-", "_").replace(" ", "_")
        match = next(
            (
                key
                for key in values
                if str(key).casefold().replace("-", "_").replace(" ", "_") == normalized
            ),
            None,
        )
        if match is None:
            continue
        raw = values[match]
        if isinstance(raw, bool):
            errors.append(f"dimension {dimension!r} is not numeric")
            continue
        try:
            score = float(raw)
        except (TypeError, ValueError):
            errors.append(f"dimension {dimension!r} is not numeric")
            continue
        scores[dimension] = score
    if len(scores) != len(RESEARCH_GATE_DIMENSIONS):
        errors.append(f"six Research Gate dimensions are required (found {len(scores)})")
    for dimension, score in scores.items():
        if not 1 <= score <= 5:
            errors.append(f"dimension {dimension!r} must be between 1 and 5")
        elif score < MIN_RESEARCH_GATE_SCORE:
            errors.append(f"dimension {dimension!r} is below the 4/5 threshold ({score:g})")
    return scores, errors


def validate_research_approval(
    research_packet: Mapping[str, Any] | str | Path,
    rubric: Mapping[str, Any] | str | Path,
    expected_research_hash: str | None = None,
    *,
    root: str | Path | None = None,
) -> list[str]:
    """Return all Research Gate errors; an empty list means valid.

    ``expected_research_hash`` is the immutable hash captured by the current
    run.  When callers do not have a run snapshot, the rubric still must carry
    a hash and it is compared with the packet's freshly computed digest.
    """

    errors: list[str] = []
    # Pipeline callers commonly pass a job directory rather than the packet
    # file.  Resolve only known job-local names; never search outside it.
    if isinstance(research_packet, (str, Path)):
        packet_path = Path(research_packet)
        if packet_path.is_dir():
            candidates = (
                packet_path / "research_packet.json",
                packet_path / "research.json",
                packet_path / "artifacts" / "research_packet.json",
            )
            research_packet = next(
                (candidate for candidate in candidates if candidate.is_file()),
                candidates[0],
            )
    service = HistoryContractService(root=root)
    try:
        packet = service.validate_research_packet(research_packet, root=root)
    except (HistoryContractValidationError, FileNotFoundError, OSError, TypeError, ValueError) as exc:
        if isinstance(exc, HistoryContractValidationError):
            errors.extend(exc.errors)
        else:
            errors.append(f"research packet could not be loaded: {exc}")
        return errors
    try:
        packet_hash = str(packet.get("artifact_hash") or "").strip().lower()
        if not packet_hash or not _HASH_RE.fullmatch(packet_hash):
            errors.append("research packet is missing a canonical SHA-256 hash")
        rubric_payload = _rubric_payload(rubric, root=root)
    except (HistoryContractValidationError, FileNotFoundError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"research gate rubric could not be loaded: {exc}")
        return errors
    rubric_hash = _hash_from_rubric(rubric_payload)
    if not rubric_hash:
        errors.append("research gate rubric must include the current research hash")
    elif not _HASH_RE.fullmatch(rubric_hash):
        errors.append("research gate research hash must be a 64-character lowercase SHA-256")
    elif packet_hash and rubric_hash != packet_hash:
        errors.append(
            f"research gate hash {rubric_hash!r} does not match packet hash {packet_hash!r}"
        )
    expected = str(expected_research_hash or "").strip().lower()
    if expected:
        if not _HASH_RE.fullmatch(expected):
            errors.append("expected research hash must be a 64-character lowercase SHA-256")
        else:
            if packet_hash and packet_hash != expected:
                errors.append(
                    f"research packet hash {packet_hash!r} does not match current {expected!r}"
                )
            if rubric_hash and rubric_hash != expected:
                errors.append(
                    f"research gate hash {rubric_hash!r} does not match current {expected!r}"
                )
    _scores, score_errors = _canonical_dimension_scores(rubric_payload)
    errors.extend(score_errors)
    return errors


def validate_research_gate(
    research_packet: Mapping[str, Any] | str | Path,
    rubric: Mapping[str, Any] | str | Path,
    expected_research_hash: str | None = None,
    *,
    root: str | Path | None = None,
) -> list[str]:
    return validate_research_approval(
        research_packet,
        rubric,
        expected_research_hash,
        root=root,
    )


def check_research_approval(*args: Any, **kwargs: Any) -> list[str]:
    return validate_research_approval(*args, **kwargs)


def research_gate_ok(
    research_packet: Mapping[str, Any] | str | Path,
    rubric: Mapping[str, Any] | str | Path,
    expected_research_hash: str | None = None,
    *,
    root: str | Path | None = None,
) -> bool:
    return not validate_research_approval(
        research_packet,
        rubric,
        expected_research_hash,
        root=root,
    )


class ResearchGateGuard:
    """Object adapter for dependency-injected pipeline callers."""

    def validate(
        self,
        research_packet: Mapping[str, Any] | str | Path,
        rubric: Mapping[str, Any] | str | Path,
        expected_research_hash: str | None = None,
        *,
        root: str | Path | None = None,
    ) -> list[str]:
        return validate_research_approval(
            research_packet,
            rubric,
            expected_research_hash,
            root=root,
        )

    check = validate


__all__ = [
    "RESEARCH_GATE_VERSION",
    "MIN_RESEARCH_GATE_SCORE",
    "RESEARCH_GATE_DIMENSIONS",
    "REQUIRED_DIMENSIONS",
    "RUBRIC_DIMENSIONS",
    "ResearchGateValidationError",
    "ResearchGateGuard",
    "validate_research_approval",
    "validate_research_gate",
    "check_research_approval",
    "research_gate_ok",
]
