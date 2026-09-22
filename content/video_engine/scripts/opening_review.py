"""Validate explicit human opening-review evidence without manufacturing a verdict.

The opening structure gate emits JUDGE rows for J13 (a concrete human
consequence by 0:30) and J14 (a useful, viewer-verifiable stay promise by
0:45).  This module validates a *reader-supplied* JSON sidecar for those rows;
it never infers a semantic PASS from tags, keywords, or the mechanical gate.

Sidecar schema (``opening_review.v1``)::

    {
      "schema": "opening_review.v1",
      "script_hash": "<run_script_gates canonical spoken SHA-256>",
      "review_kind": "estimated_draft" | "measured_recording",
      "rows": [
        {
          "id": "J13" | "J14",
          "verdict": "PASS",
          "quote": "exact spoken substring from the canonical script",
          "rationale": "non-empty human rationale",
          "clock": 24.0,
          "clock_basis": "estimated" | "actual"
        },
        ...
      ]
    }

Exactly two rows are required, one each for J13 and J14.  ``estimated_draft``
requires estimated clocks and reports draft readiness only.  A
``measured_recording`` sidecar requires actual clocks, but this bounded
validator deliberately reports measured readiness as unavailable until a
retained, hash-bound word-timeline contract is supplied by the recorder.  An
``actual`` string by itself is not measurement evidence.  No sidecar is
written by this module.

``clock`` is the reader's timestamp for completion of the quoted consequence
or promise, not merely the onset of its delivery tag.  J13 must complete by
0:30 and J14 by 0:45; an earlier J14 is allowed because the mechanical G09
gate owns the separate early-promise warning.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_script_gates as RG  # noqa: E402  (canonical spoken hash owner)


SCHEMA = "opening_review.v1"
J13 = "J13"
J14 = "J14"
REQUIRED_JUDGES = (J13, J14)
REVIEW_KINDS = frozenset(("estimated_draft", "measured_recording"))
CLOCK_BASES = frozenset(("estimated", "actual"))
STAKES_DEADLINE_S = 30.0
PROMISE_DEADLINE_S = 45.0
_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_TOP_LEVEL_KEYS = frozenset(("schema", "script_hash", "review_kind", "rows"))
_ROW_KEYS = frozenset(("id", "verdict", "quote", "rationale", "clock", "clock_basis"))


@dataclass(frozen=True)
class ValidationResult:
    """A read-only validation result for one explicit review sidecar."""

    ok: bool
    status: str
    errors: tuple[str, ...]
    expected_hash: str | None
    review_kind: str | None
    sidecar: Path

    @property
    def estimated_draft_ready(self) -> bool:
        """Whether this is a valid estimated draft review (not a recording)."""
        return self.ok and self.review_kind == "estimated_draft"

    @property
    def measured_recording_ready(self) -> bool:
        """Whether this is a valid review with measured/actual clocks."""
        return self.ok and self.review_kind == "measured_recording"

    @property
    def recording_ready(self) -> bool:
        """Alias emphasizing that estimated draft readiness is not recording readiness."""
        return self.measured_recording_ready


def opening_review_path(script: Path) -> Path:
    """Return the conventional sidecar path beside ``script``.

    Callers may pass an explicit review path to :func:`validate_opening_review`;
    this helper is only a naming convenience and never creates the file.
    """
    script = Path(script)
    stem = script.stem
    if stem.endswith("-VO"):
        stem = stem[:-3]
    return script.with_name(stem + "-OPENING-REVIEW.json")


def _result(
    *,
    ok: bool,
    errors: Iterable[str],
    expected_hash: str | None,
    review_kind: str | None,
    sidecar: Path,
    status: str | None = None,
) -> ValidationResult:
    errors_tuple = tuple(errors)
    if status is not None:
        final_status = status
    elif ok:
        assert review_kind in REVIEW_KINDS
        final_status = f"{review_kind}_ready"
    else:
        final_status = "invalid"
    return ValidationResult(ok, final_status, errors_tuple, expected_hash, review_kind, sidecar)


def _clock_number(value: Any) -> bool:
    """Return true for finite non-negative JSON numbers, excluding booleans."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value) and value >= 0
    except (OverflowError, ValueError):
        return False


def _format_keys(keys: Iterable[Any]) -> str:
    return ", ".join(sorted(repr(k) for k in keys))


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Keep duplicate JSON fields from being silently accepted by ``json``."""
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        obj[key] = value
    return obj


def validate_opening_review(script: Path, review: Path | None = None) -> ValidationResult:
    """Validate a human-supplied J13/J14 sidecar against the current script.

    The only script identity accepted is ``run_script_gates.script_hash`` over
    ``run_script_gates.spoken_text``.  This function performs no writes and
    returns ``ok=False`` for all missing, malformed, stale, failed, or untimely
    evidence.
    """
    script = Path(script)
    sidecar = Path(review) if review is not None else opening_review_path(script)
    errors: list[str] = []

    if not script.exists():
        return _result(ok=False, errors=(f"script missing: {script}",), expected_hash=None,
                        review_kind=None, sidecar=sidecar)
    try:
        script_text = script.read_text(encoding="utf-8")
    except OSError as exc:
        return _result(ok=False, errors=(f"script unreadable: {exc}",), expected_hash=None,
                        review_kind=None, sidecar=sidecar)

    # Keep canonicalization in one place: recorders and this validator use the
    # exact hash implementation owned by run_script_gates.
    spoken = RG.spoken_text(script_text)
    expected_hash = RG.script_hash(script_text)

    if not sidecar.exists():
        return _result(ok=False, errors=(f"review sidecar missing: {sidecar}",), expected_hash=expected_hash,
                        review_kind=None, sidecar=sidecar)
    try:
        raw = json.loads(sidecar.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (OSError, ValueError) as exc:
        return _result(ok=False, errors=(f"review sidecar malformed JSON: {exc}",), expected_hash=expected_hash,
                        review_kind=None, sidecar=sidecar)

    if not isinstance(raw, dict):
        return _result(ok=False, errors=("review sidecar must be a JSON object",), expected_hash=expected_hash,
                       review_kind=None, sidecar=sidecar)

    actual_top_keys = frozenset(raw)
    if actual_top_keys != _TOP_LEVEL_KEYS:
        missing = _TOP_LEVEL_KEYS - actual_top_keys
        extra = actual_top_keys - _TOP_LEVEL_KEYS
        if missing:
            errors.append(f"missing top-level field(s): {_format_keys(missing)}")
        if extra:
            errors.append(f"unexpected top-level field(s): {_format_keys(extra)}")

    schema = raw.get("schema")
    if not isinstance(schema, str) or schema != SCHEMA:
        errors.append(f"schema must be {SCHEMA!r}")

    script_hash = raw.get("script_hash")
    if not isinstance(script_hash, str) or not _HEX_SHA256.fullmatch(script_hash):
        errors.append("script_hash must be a lowercase SHA-256 hex string")
    elif script_hash != expected_hash:
        errors.append("script_hash is stale or does not match the current spoken script")

    review_kind = raw.get("review_kind")
    if not isinstance(review_kind, str) or review_kind not in REVIEW_KINDS:
        errors.append("review_kind must be 'estimated_draft' or 'measured_recording'")
        normalized_kind: str | None = None
    else:
        normalized_kind = review_kind

    rows = raw.get("rows")
    if not isinstance(rows, list):
        errors.append("rows must be a JSON array")
        rows = []
    elif len(rows) != len(REQUIRED_JUDGES):
        errors.append("rows must contain exactly one J13 row and one J14 row")

    row_ids: list[str] = []
    valid_rows: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        label = f"rows[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be a JSON object")
            continue
        actual_row_keys = frozenset(row)
        if actual_row_keys != _ROW_KEYS:
            missing = _ROW_KEYS - actual_row_keys
            extra = actual_row_keys - _ROW_KEYS
            if missing:
                errors.append(f"{label} missing field(s): {_format_keys(missing)}")
            if extra:
                errors.append(f"{label} has unexpected field(s): {_format_keys(extra)}")

        row_id = row.get("id")
        if not isinstance(row_id, str) or row_id not in REQUIRED_JUDGES:
            errors.append(f"{label}.id must be exactly 'J13' or 'J14'")
            continue
        row_ids.append(row_id)
        if row_id in valid_rows:
            errors.append(f"duplicate review row: {row_id}")
        else:
            valid_rows[row_id] = row

        if row.get("verdict") != "PASS":
            errors.append(f"{label} {row_id}.verdict must be explicit 'PASS'")

        quote = row.get("quote")
        if not isinstance(quote, str) or not quote.strip():
            errors.append(f"{label} {row_id}.quote must be a non-empty string")
        elif quote not in spoken:
            errors.append(f"{label} {row_id}.quote is not an exact substring of the current spoken script")

        rationale = row.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(f"{label} {row_id}.rationale must be non-empty human evidence")

        clock = row.get("clock")
        if not _clock_number(clock):
            errors.append(f"{label} {row_id}.clock must be a finite non-negative number (not a boolean)")

        clock_basis = row.get("clock_basis")
        if not isinstance(clock_basis, str) or clock_basis not in CLOCK_BASES:
            errors.append(f"{label} {row_id}.clock_basis must be 'estimated' or 'actual'")

        if _clock_number(clock):
            if row_id == J13 and clock > STAKES_DEADLINE_S:
                errors.append(f"{label} J13.clock must be at or before 30 seconds")
            elif row_id == J14 and clock > PROMISE_DEADLINE_S:
                errors.append(f"{label} J14.clock must be at or before 45 seconds")

        if normalized_kind is not None and isinstance(clock_basis, str) and clock_basis in CLOCK_BASES:
            expected_basis = "estimated" if normalized_kind == "estimated_draft" else "actual"
            if clock_basis != expected_basis:
                errors.append(f"{label} {row_id}.clock_basis must be {expected_basis!r} for {normalized_kind!r}")

    if len(set(row_ids)) != len(REQUIRED_JUDGES):
        missing_ids = set(REQUIRED_JUDGES) - set(row_ids)
        if missing_ids:
            errors.append(f"missing review row(s): {_format_keys(missing_ids)}")

    if not errors and normalized_kind == "measured_recording":
        return _result(
            ok=False,
            errors=("measured_recording readiness unavailable: actual clocks require "
                    "hash-bound retained word-timeline evidence",),
            expected_hash=expected_hash,
            review_kind=normalized_kind,
            sidecar=sidecar,
            status="measured_recording_unavailable",
        )

    return _result(ok=not errors, errors=errors, expected_hash=expected_hash,
                   review_kind=normalized_kind, sidecar=sidecar)


# Short alias for callers that use validators by noun.
validate = validate_opening_review


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate explicit J13/J14 opening-review evidence")
    parser.add_argument("script", type=Path)
    parser.add_argument("review", type=Path, nargs="?", help="JSON sidecar (default: conventional sidecar beside script)")
    args = parser.parse_args(argv)
    result = validate_opening_review(args.script, args.review)
    if result.ok:
        print(f"OPENING REVIEW: {result.status}")
        return 0
    print(f"OPENING REVIEW: {result.status}")
    for error in result.errors:
        print(f"  - {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
