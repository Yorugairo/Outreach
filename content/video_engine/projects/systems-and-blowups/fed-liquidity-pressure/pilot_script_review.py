"""Validate the episode-local, pilot-only script-gate exception.

The raw ``SCRIPT-GATES.md`` report remains a faithful FAIL report. This module
only consumes a separately authored operator review sidecar and never writes
it or changes a gate verdict. Its narrow contract is episode-local: the
builder may use it for the approved bed/unit/minute/pilot prefix preflight,
while an episode build must continue to require an unmodified mechanical PASS.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable


EPISODE_ID = "fed-liquidity-pressure"
SCHEMA = "fed-liquidity.pilot-script-review.v1"
REVIEW_PATH = Path("review/PILOT-SCRIPT-REVIEW.json")
SCRIPT_NAME = "SCRIPT-VO.txt"
GATES_NAME = "SCRIPT-GATES.md"
OPENING_REVIEW_NAME = "SCRIPT-OPENING-REVIEW.json"
ELIGIBLE_SEGMENTS = frozenset({"bed", "unit", "minute", "pilot"})
ALLOWED_VERDICTS = frozenset({"MANUALLY_REVIEWED", "DEFERRED_TO_FULL_EPISODE"})

FAILURE_IDS = (
    "lint:RING",
    "audit:doc35-rule2-literal-tell",
    "opening:G15b",
    "opening:G21",
    "opening:G27",
)
FAILURE_REPORTS = {
    "lint:RING": "lint_script_pattern.py",
    "audit:doc35-rule2-literal-tell": "audit_script_doctrine.py",
    "opening:G15b": "gate_opening_structure.py",
    "opening:G21": "gate_opening_structure.py",
    "opening:G27": "gate_opening_structure.py",
}
_FAILURE_SET = frozenset(FAILURE_IDS)
_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SCRIPT_HASH_RE = re.compile(r"^script_hash:\s*([0-9a-f]{64})\s*$", re.I | re.M)
_VERDICT_RE = re.compile(r"^VERDICT:\s*(PASS|FAIL)\b", re.M)
_VERDICT_FAIL_RE = re.compile(r"^VERDICT:\s*FAIL\b", re.M)
_OPENING_REF_RE = re.compile(r"^opening_review:\s*(?P<path>\S+)\s*$", re.M)

_TOP_LEVEL_KEYS = frozenset(
    {
        "schema",
        "episode_id",
        "accepted_for",
        "script_hash",
        "script_gates_sha256",
        "operator_authorization",
        "opening_review",
        "failures",
    }
)
_AUTH_KEYS = frozenset({"quote", "reference"})
_OPENING_KEYS = frozenset({"path", "sha256"})
_ROW_KEYS = frozenset({"id", "report", "verdict", "quote", "rationale"})


@dataclass(frozen=True)
class ValidationResult:
    """Read-only result for one operator-authored pilot review sidecar."""

    ok: bool
    errors: tuple[str, ...]
    failure_ids: tuple[str, ...] = ()
    script_hash: str | None = None
    script_gates_sha256: str | None = None

    @property
    def blockers(self) -> tuple[str, ...]:
        """Alias used by callers that expose preflight blockers."""

        return self.errors


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r}")


def _read_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_constant,
    )


def _format_keys(keys: Iterable[Any]) -> str:
    return ", ".join(sorted(repr(key) for key in keys))


def _check_exact_keys(value: Any, expected: frozenset[str], label: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label}: must be a JSON object")
        return
    actual = frozenset(value)
    missing = expected - actual
    extra = actual - expected
    if missing:
        errors.append(f"{label}: missing field(s): {_format_keys(missing)}")
    if extra:
        errors.append(f"{label}: unexpected field(s): {_format_keys(extra)}")


def _section(text: str, heading: str, errors: list[str]) -> str:
    matches = list(re.finditer(rf"^##\s+{re.escape(heading)}\s*$", text, re.M))
    if len(matches) != 1:
        errors.append(f"raw script gates: expected one {heading} section")
        return ""
    start = matches[0].end()
    next_heading = re.search(r"^##\s+", text[start:], re.M)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def _parse_raw_failures(text: str, errors: list[str]) -> list[str]:
    """Parse tool-owned failure rows and reconcile each RESULT count."""

    lint = _section(text, "lint_script_pattern.py", errors)
    audit = _section(text, "audit_script_doctrine.py", errors)
    opening = _section(text, "gate_opening_structure.py", errors)
    observed: list[str] = []

    lint_rows: list[str] = []
    for line in lint.splitlines():
        match = re.match(r"^\s*FAIL\s+(?P<name>[A-Za-z0-9_-]+):\s*(?P<detail>.+?)\s*$", line)
        if not match:
            continue
        name = match.group("name")
        detail = match.group("detail")
        if name == "RING" and detail == "no opening token recurs in the close":
            lint_rows.append("lint:RING")
        else:
            lint_rows.append(f"lint:{name}")
    lint_count = re.findall(r"^RESULT:\s*(\d+)\s+failure\(s\)\s*$", lint, re.M)
    if len(lint_count) != 1:
        errors.append("raw script gates: lint failure count is missing or ambiguous")
    elif int(lint_count[0]) != len(lint_rows):
        errors.append("raw script gates: lint failure count does not match failure rows")
    observed.extend(lint_rows)

    audit_rows: list[str] = []
    for line in audit.splitlines():
        match = re.match(r"^\s*\[FAIL\s*\]\s+(?P<detail>.+?)\s*$", line)
        if not match:
            continue
        detail = match.group("detail")
        if detail.startswith("doc 35 rule 2: no falsifiable tell"):
            audit_rows.append("audit:doc35-rule2-literal-tell")
        else:
            audit_rows.append("audit:unknown")
    audit_count = re.findall(r"^RESULT:\s*(\d+)\s+FAIL\b", audit, re.M)
    if len(audit_count) != 1:
        errors.append("raw script gates: audit failure count is missing or ambiguous")
    elif int(audit_count[0]) != len(audit_rows):
        errors.append("raw script gates: audit failure count does not match failure rows")
    observed.extend(audit_rows)

    opening_rows: list[str] = []
    for line in opening.splitlines():
        failure = re.match(r"^\s*\[FAIL\s*\]\s*(?P<detail>.*?)\s*$", line)
        if failure:
            match = re.match(r"(?P<id>G\d+[A-Za-z]?)\b", failure.group("detail"))
            opening_rows.append(f"opening:{match.group('id')}" if match else "opening:unknown")
    opening_count = re.findall(r"^RESULT:\s*(\d+)\s+FAIL\s*/", opening, re.M)
    if len(opening_count) != 1:
        errors.append("raw script gates: opening failure count is missing or ambiguous")
    elif int(opening_count[0]) != len(opening_rows):
        errors.append("raw script gates: opening failure count does not match failure rows")
    observed.extend(opening_rows)

    if len(set(observed)) != len(observed):
        errors.append("raw script gates: duplicate failure row ID")
    if frozenset(observed) != _FAILURE_SET:
        missing = _FAILURE_SET - set(observed)
        extra = set(observed) - _FAILURE_SET
        if missing:
            errors.append(f"raw script gates: missing allowed failure row(s): {_format_keys(missing)}")
        if extra:
            errors.append(f"raw script gates: unknown failure row(s): {_format_keys(extra)}")
    return observed


def _opening_review_path(raw_path: str, root: Path, errors: list[str]) -> Path | None:
    supplied = raw_path.replace("\\", "/")
    candidate = Path(supplied)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.name != OPENING_REVIEW_NAME:
        errors.append("opening review: report path must name the episode-local SCRIPT-OPENING-REVIEW.json")
        return None
    # The gate runner records a repo-relative path, while the episode
    # consumer runs with the episode root. Accept either representation, but
    # require the final episode directory/name to be exact.
    if len(candidate.parts) == 1:
        return (root / candidate).resolve()
    if len(candidate.parts) < 2 or candidate.parts[-2].casefold() != root.name.casefold():
        errors.append("opening review: report path must stay beside SCRIPT-VO.txt")
        return None
    return (root / OPENING_REVIEW_NAME).resolve()


def _validate_artifact(
    *,
    root: Path,
    opening_path: Path,
    actual_script_hash: str,
    actual_gates_hash: str,
    observed_ids: list[str],
    spoken_text: str,
    errors: list[str],
) -> None:
    review_path = root / REVIEW_PATH
    try:
        payload = _read_json(review_path)
    except FileNotFoundError:
        errors.append(f"pilot script review: missing ({REVIEW_PATH.as_posix()})")
        return
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"pilot script review: malformed JSON ({exc})")
        return

    _check_exact_keys(payload, _TOP_LEVEL_KEYS, "pilot script review", errors)
    if not isinstance(payload, dict):
        return

    if payload.get("schema") != SCHEMA:
        errors.append(f"pilot script review: schema must be {SCHEMA!r}")
    if payload.get("episode_id") != EPISODE_ID:
        errors.append(f"pilot script review: episode_id must be {EPISODE_ID!r}")
    if payload.get("accepted_for") != "pilot_only":
        errors.append("pilot script review: accepted_for must be 'pilot_only'")

    script_hash = payload.get("script_hash")
    if not isinstance(script_hash, str) or not _HEX_SHA256.fullmatch(script_hash):
        errors.append("pilot script review: script_hash must be a lowercase SHA-256 hex string")
    elif script_hash != actual_script_hash:
        errors.append("pilot script review: script_hash is stale")

    gates_hash = payload.get("script_gates_sha256")
    if not isinstance(gates_hash, str) or not _HEX_SHA256.fullmatch(gates_hash):
        errors.append("pilot script review: script_gates_sha256 must be a lowercase SHA-256 hex string")
    elif gates_hash != actual_gates_hash:
        errors.append("pilot script review: script_gates_sha256 is stale")

    authorization = payload.get("operator_authorization")
    _check_exact_keys(authorization, _AUTH_KEYS, "pilot script review.operator_authorization", errors)
    if isinstance(authorization, dict):
        quote = authorization.get("quote")
        reference = authorization.get("reference")
        if not isinstance(quote, str) or not quote.strip() or not re.search(r"\byes\b", quote, re.I):
            errors.append("pilot script review.operator_authorization.quote must quote an explicit YES")
        if not isinstance(reference, str) or not reference.strip():
            errors.append("pilot script review.operator_authorization.reference must be non-empty")

    opening_ref = payload.get("opening_review")
    _check_exact_keys(opening_ref, _OPENING_KEYS, "pilot script review.opening_review", errors)
    if isinstance(opening_ref, dict):
        if opening_ref.get("path") != OPENING_REVIEW_NAME:
            errors.append(f"pilot script review.opening_review.path must be {OPENING_REVIEW_NAME!r}")
        opening_hash = opening_ref.get("sha256")
        if not isinstance(opening_hash, str) or not _HEX_SHA256.fullmatch(opening_hash):
            errors.append("pilot script review.opening_review.sha256 must be a lowercase SHA-256 hex string")
        elif opening_path.is_file() and opening_hash != _sha256(opening_path):
            errors.append("pilot script review.opening_review.sha256 is stale")

    failures = payload.get("failures")
    if not isinstance(failures, list):
        errors.append("pilot script review.failures must be a JSON array")
        failures = []
    elif len(failures) != len(_FAILURE_SET):
        errors.append("pilot script review.failures must contain exactly five rows")

    row_ids: list[str] = []
    for index, row in enumerate(failures):
        label = f"pilot script review.failures[{index}]"
        _check_exact_keys(row, _ROW_KEYS, label, errors)
        if not isinstance(row, dict):
            continue
        row_id = row.get("id")
        if not isinstance(row_id, str) or row_id not in _FAILURE_SET:
            errors.append(f"{label}.id is not an allowed failure row")
            continue
        row_ids.append(row_id)
        if row.get("report") != FAILURE_REPORTS[row_id]:
            errors.append(f"{label}.report does not match {row_id}")
        if row.get("verdict") not in ALLOWED_VERDICTS:
            errors.append(f"{label}.verdict must be MANUALLY_REVIEWED or DEFERRED_TO_FULL_EPISODE")
        quote = row.get("quote")
        if not isinstance(quote, str) or not quote.strip():
            errors.append(f"{label}.quote must be non-empty script evidence")
        elif quote not in spoken_text:
            errors.append(f"{label}.quote is not an exact substring of the current spoken script")
        rationale = row.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(f"{label}.rationale must be non-empty")

    if len(set(row_ids)) != len(row_ids):
        errors.append("pilot script review: duplicate failure row ID")
    if set(row_ids) != set(observed_ids):
        errors.append("pilot script review: failure rows do not match raw SCRIPT-GATES.md")


def validate(project_root: Path, *, expected_script_hash: str | None = None) -> ValidationResult:
    """Validate the current raw report and operator sidecar without writing."""

    root = Path(project_root).resolve()
    errors: list[str] = []
    script_path = root / SCRIPT_NAME
    gates_path = root / GATES_NAME
    opening_path = root / OPENING_REVIEW_NAME

    if not script_path.is_file():
        errors.append(f"script: missing ({SCRIPT_NAME})")
        return ValidationResult(False, tuple(errors))
    if not gates_path.is_file():
        errors.append(f"script gates: missing ({GATES_NAME})")
        return ValidationResult(False, tuple(errors))
    try:
        script_text = script_path.read_text(encoding="utf-8")
        gates_text = gates_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"pilot script review: cannot read source report ({exc})")
        return ValidationResult(False, tuple(errors))

    # Use the same canonical spoken hash owner as the recorders.
    scripts_dir = Path(__file__).resolve().parents[3] / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import run_script_gates as gates  # type: ignore  # noqa: PLC0415

    actual_script_hash = gates.script_hash(script_text)
    # Bind the operator sidecar to the raw bytes, not a newline-normalised
    # ``read_text`` projection. This preserves Get-FileHash identity on
    # Windows and makes a CRLF/LF rewrite stale the sidecar.
    actual_gates_hash = _sha256(gates_path)
    if expected_script_hash is not None and expected_script_hash != actual_script_hash:
        errors.append("pilot script review: supplied current script hash is stale")

    embedded = _SCRIPT_HASH_RE.findall(gates_text)
    if len(embedded) != 1 or embedded[0].lower() != actual_script_hash:
        errors.append("raw SCRIPT-GATES.md: script_hash is missing, duplicated, or stale")
    if _VERDICT_RE.findall(gates_text) != ["FAIL"] or len(_VERDICT_FAIL_RE.findall(gates_text)) != 1:
        errors.append("raw SCRIPT-GATES.md: exactly one VERDICT: FAIL is required for the exception")

    opening_ref = _OPENING_REF_RE.search(gates_text)
    if not opening_ref:
        errors.append("raw SCRIPT-GATES.md: opening_review reference is missing")
    else:
        reported_path = _opening_review_path(opening_ref.group("path"), root, errors)
        if reported_path is not None and reported_path != opening_path.resolve():
            errors.append("raw SCRIPT-GATES.md: opening_review reference is not the episode sidecar")

    observed_ids = _parse_raw_failures(gates_text, errors)

    if not opening_path.is_file():
        errors.append(f"opening review: missing ({OPENING_REVIEW_NAME})")
    else:
        try:
            from opening_review import validate_opening_review  # type: ignore  # noqa: PLC0415

            opening_result = validate_opening_review(script_path, opening_path)
            if not opening_result.estimated_draft_ready:
                errors.extend(f"opening review: {error}" for error in opening_result.errors)
        except (OSError, UnicodeError, ImportError) as exc:
            errors.append(f"opening review: validator unavailable ({exc})")

    _validate_artifact(
        root=root,
        opening_path=opening_path,
        actual_script_hash=actual_script_hash,
        actual_gates_hash=actual_gates_hash,
        observed_ids=observed_ids,
        spoken_text=gates.spoken_text(script_text),
        errors=errors,
    )
    return ValidationResult(
        not errors,
        tuple(dict.fromkeys(errors)),
        tuple(observed_ids),
        actual_script_hash,
        actual_gates_hash,
    )


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate the pilot-only script review sidecar")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args(argv)
    result = validate(args.project_root)
    if result.ok:
        print(f"pilot script review: PASS ({SCHEMA}; accepted_for=pilot_only)")
        return 0
    print("pilot script review: FAIL")
    for error in result.errors:
        print(f"  - {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
