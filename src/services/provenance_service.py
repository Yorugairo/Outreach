from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class EvidenceReferenceError(ValueError):
    """Raised when a report evidence reference cannot be independently verified."""


def validate_evidence_ref(
    run_dir: str | Path,
    ref: object,
    *,
    expected_attempt_id: str | None = None,
) -> None:
    """Validate one evidence reference against a persisted run artifact.

    Evidence must be an independent JSON artifact inside the run boundary. Report
    files are intentionally excluded so a report cannot prove its own claims.
    """
    if not isinstance(ref, dict) or "observed" not in ref:
        raise EvidenceReferenceError("evidence reference must be an object with observed")
    required = ("artifact_path", "field", "reason")
    if any(not isinstance(ref.get(key), str) or not ref[key].strip() for key in required):
        raise EvidenceReferenceError("evidence reference requires artifact_path, field, and reason")

    raw_path = ref["artifact_path"]
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise EvidenceReferenceError("evidence path must be run-relative")
    if relative.suffix.casefold() != ".json":
        raise EvidenceReferenceError("evidence artifact must be JSON")
    if relative.parts and relative.parts[0].casefold() == "reports":
        raise EvidenceReferenceError("report artifacts cannot be evidence")

    root = Path(run_dir).resolve()
    artifact = (root / relative).resolve()
    try:
        artifact.relative_to(root)
    except ValueError as exc:
        raise EvidenceReferenceError("evidence path escapes the run") from exc
    if not artifact.is_file():
        raise EvidenceReferenceError(f"evidence artifact is missing: {relative.as_posix()}")

    try:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        resolved = resolve_evidence_field(payload, ref["field"])
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise EvidenceReferenceError(f"evidence field cannot be resolved: {ref['field']}") from exc

    if expected_attempt_id is not None and isinstance(payload, dict):
        artifact_attempt = payload.get("attempt_id")
        if artifact_attempt is not None and artifact_attempt != expected_attempt_id:
            raise EvidenceReferenceError("evidence artifact belongs to a different attempt")

    observed = ref["observed"]
    if type(resolved) is not type(observed) or resolved != observed:
        raise EvidenceReferenceError("observed value does not match persisted evidence")


def resolve_evidence_field(payload: object, field: str) -> object:
    if not field or field.startswith(".") or field.endswith("."):
        raise ValueError("malformed evidence field")
    current = payload
    for part in field.split("."):
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*)(.*)", part)
        if match is None:
            raise ValueError("malformed evidence field")
        key, indexes = match.groups()
        if not isinstance(current, dict) or key not in current:
            raise KeyError(key)
        current = current[key]
        while indexes:
            index_match = re.match(r"^\[(0|[1-9][0-9]*)\](.*)$", indexes)
            if index_match is None:
                raise ValueError("malformed evidence index")
            index_text, indexes = index_match.groups()
            if not isinstance(current, list):
                raise TypeError("indexed evidence value is not a list")
            current = current[int(index_text)]
    return current
