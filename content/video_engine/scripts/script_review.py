"""Strict, offline validation for complete script-review receipts and maps.

The runner owns mechanical diagnostics; this module owns custody and
completeness of the human/semantic review package.  It deliberately does not
decide whether a reviewer is *right*.  It verifies that the reviewer answered
the obligations that were due, against the exact annotated script, spoken
script, narrative map, and contract inventory supplied to the review.

Two versioned documents are supported:

``script_review.v1``
    A full, stage-scoped receipt.  The ``rows`` list is keyed by the exact
    obligation IDs emitted by :mod:`script_review_contract`.

``narrative_map.v1``
    A semantic map of micro loops and macro relationships.  It is not a beat
    tag counter and it does not require a rhetorical question mark: a clear
    non-interrogative tension statement is valid.

The public functions are intentionally small and usable by the existing
runner later (T4) without making this module depend on a provider or a
renderer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import script_review_contract as contract


RECEIPT_SCHEMA = "script_review.v1"
MAP_SCHEMA = "narrative_map.v1"
SCHEMA = RECEIPT_SCHEMA
STATUSES = frozenset({"PASS", "WARN", "FAIL", "INFO", "NOT_RUN", "STALE", "DEFERRED", "NA"})
STAGES = tuple(contract.STAGES)
STAGE_ORDER = dict(contract.STAGE_ORDER)
FORMS = frozenset({"long", "short"})
_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{1,127}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    """Return deterministic JSON for hashes and human-review custody."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def map_digest(value: Any) -> str:
    """Hash a map object or parsed map file using canonical JSON bytes."""
    if isinstance(value, Path):
        value = _read_json(value)
    if isinstance(value, str):
        value = json.loads(value)
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _read_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonfinite,
    )


def _load_object(value: Any, *, label: str) -> Any:
    if isinstance(value, Path):
        if not value.is_file():
            raise ValueError(f"{label} missing: {value}")
        return _read_json(value)
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        candidate = Path(value)
        if candidate.is_file():
            return _read_json(candidate)
        try:
            return json.loads(value, object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_nonfinite)
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"{label} is neither a JSON document nor a file: {exc}") from exc
    raise ValueError(f"{label} must be a JSON object or file")


def _script_text(value: str | Path) -> str:
    if isinstance(value, Path):
        if not value.is_file():
            raise ValueError(f"script missing: {value}")
        return value.read_text(encoding="utf-8")
    candidate = Path(value)
    if candidate.is_file():
        return candidate.read_text(encoding="utf-8")
    return value


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(_HEX_SHA256.fullmatch(value))


def _first(mapping: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        if name in mapping:
            return mapping[name]
    return None


def _number(value: Any, *, nonnegative: bool = True) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if not math.isfinite(float(value)):
        return False
    return not nonnegative or float(value) >= 0


def _stage(value: Any) -> bool:
    return isinstance(value, str) and value in STAGE_ORDER


def _format_set(items: Iterable[str]) -> str:
    return ", ".join(sorted(repr(item) for item in items))


def _scope_valid(scope: Any) -> tuple[bool, str | None]:
    if isinstance(scope, str):
        return (bool(scope.strip()), None if scope.strip() else "scope must not be empty")
    if not isinstance(scope, dict):
        return False, "scope must be a non-empty string or object"
    kind = scope.get("kind", scope.get("type"))
    if not isinstance(kind, str) or not kind.strip():
        return False, "scope.kind must be non-empty"
    start = scope.get("start_s", scope.get("start"))
    end = scope.get("end_s", scope.get("end"))
    if start is not None and not _number(start):
        return False, "scope.start_s must be a finite non-negative number"
    if end is not None and not _number(end):
        return False, "scope.end_s must be a finite non-negative number"
    if start is not None and end is not None and float(end) < float(start):
        return False, "scope.end_s must be at or after scope.start_s"
    return True, None


def _span(value: Any) -> tuple[float, float] | None:
    """Normalize a time span from common map spellings."""
    if isinstance(value, (list, tuple)) and len(value) == 2:
        start, end = value
    elif isinstance(value, dict):
        start = value.get("start_s", value.get("start"))
        end = value.get("end_s", value.get("end"))
    else:
        return None
    if not (_number(start) and _number(end)) or float(end) < float(start):
        return None
    return float(start), float(end)


def _span_text(value: Any) -> str:
    span = _span(value)
    if span is None:
        return "?"
    return f"{span[0]:g}–{span[1]:g}s"


def _relationship_refs(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    if isinstance(value, dict):
        refs: list[str] = []
        for key in ("from", "to", "id", "loop_id", "phase_id", "target"):
            item = value.get(key)
            if isinstance(item, str):
                refs.append(item)
        return refs
    return []


@dataclass(frozen=True)
class ReviewResult:
    ok: bool
    status: str
    errors: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    unexpected: tuple[str, ...] = ()
    failed: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    deferred: tuple[str, ...] = ()
    stale: tuple[str, ...] = ()
    diagnostics: dict[str, Any] = field(default_factory=dict)
    receipt: dict[str, Any] | None = None
    receipt_path: Path | None = None

    @property
    def clearance(self) -> str:
        return self.status

    @property
    def complete(self) -> bool:
        return self.ok and self.status in {"CLEAR", "PASS"}


def _result(errors: list[str], *, missing: Iterable[str] = (), unexpected: Iterable[str] = (),
            failed: Iterable[str] = (), warnings: Iterable[str] = (), deferred: Iterable[str] = (),
            stale: Iterable[str] = (), receipt: dict[str, Any] | None = None,
            diagnostics: dict[str, Any] | None = None, status: str | None = None,
            receipt_path: Path | None = None) -> ReviewResult:
    errors = list(dict.fromkeys(errors))
    missing = tuple(dict.fromkeys(missing))
    unexpected = tuple(dict.fromkeys(unexpected))
    failed = tuple(dict.fromkeys(failed))
    warnings = tuple(dict.fromkeys(warnings))
    deferred = tuple(dict.fromkeys(deferred))
    stale = tuple(dict.fromkeys(stale))
    if status is None:
        if failed:
            status = "FAIL"
        elif errors or missing or unexpected or stale or deferred:
            status = "INCOMPLETE"
        else:
            status = "CLEAR"
    return ReviewResult(not errors and not missing and not unexpected and not failed and not stale and not deferred,
                        status, tuple(errors), missing, unexpected, failed, warnings, deferred, stale,
                        diagnostics or {}, receipt, receipt_path)


def _dependency_hashes(receipt: Mapping[str, Any]) -> Mapping[str, Any] | None:
    value = receipt.get("dependencies")
    return value if isinstance(value, dict) else None


def _hash_field(data: Mapping[str, Any], *names: str) -> Any:
    return _first(data, *names)


def _validate_hash_field(errors: list[str], actual: str, data: Mapping[str, Any], label: str, *names: str) -> None:
    value = _hash_field(data, *names)
    if not _is_sha(value):
        errors.append(f"{label} must be a lowercase SHA-256 hex string")
    elif value != actual:
        errors.append(f"{label} is stale or does not match the current input")


def _reviewer_ok(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    identity = item.get("id", item.get("reviewer_id"))
    role = item.get("role")
    run_id = item.get("run_id")
    return (isinstance(identity, str) and bool(identity.strip()) and
            isinstance(role, str) and bool(role.strip()) and
            isinstance(run_id, str) and bool(run_id.strip()))


_RECEIPT_TOP_KEYS = frozenset({
    "schema", "annotated_script_hash", "annotated_sha256", "spoken_script_hash", "spoken_sha256",
    "map_hash", "map_sha256", "contract_digest", "form", "stage", "scope", "reviewers", "rows",
    "dependencies", "runtime_s", "timing_source", "source", "created_at", "notes",
})
_ROW_KEYS = frozenset({
    "obligation_id", "id", "status", "quote", "span", "rationale", "evidence", "reviewer",
    "dependencies", "na_basis", "deferred_to", "defer_to", "reused_from", "source",
})
_MAP_TOP_KEYS = frozenset({"schema", "runtime_s", "micro_loops", "micro", "macro_phases", "macro", "script_hash", "notes"})
_MICRO_KEYS = frozenset({
    "id", "setup", "tension", "advance", "payoff", "next_loop", "next_loop_id", "next",
    "shared_object_or_person", "shared_object", "shared_person", "shared",
})
_MACRO_KEYS = frozenset({
    "id", "start_s", "end_s", "start", "end", "intent", "phase",
    "callbacks", "callback", "foreshadows", "foreshadow",
})


def validate_receipt(
    script: str | Path,
    receipt: Any,
    *,
    narrative_map: Any | None = None,
    craft_map: Path = contract.CRAFT_MAP,
    requested_stage: str | None = None,
    requested_form: str | None = None,
    stage: str | None = None,
    form: str | None = None,
    timeline: Path | None = None,
    scratch_take: Path | None = None,
    viewer_artifact: Path | None = None,
    screens: Path | None = None,
    viewer_windows: Path | None = None,
    viewer_reports: Path | None = None,
) -> ReviewResult:
    """Validate one complete ``script_review.v1`` receipt.

    ``script`` is either the annotated script text or its path.  ``receipt``
    may be a parsed object or a path.  A map object/path is required because a
    map hash without the map itself cannot prove custody.  The caller can
    still validate a standalone map with :func:`validate_narrative_map`.
    """
    errors: list[str] = []
    if requested_stage is None:
        requested_stage = stage
    elif stage is not None and stage != requested_stage:
        errors.append("conflicting requested_stage/stage arguments")
    if requested_form is None:
        requested_form = form
    elif form is not None and form != requested_form:
        errors.append("conflicting requested_form/form arguments")
    missing: list[str] = []
    unexpected: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []
    deferred: list[str] = []
    stale: list[str] = []
    try:
        script_text = _script_text(script)
    except (OSError, ValueError) as exc:
        return _result([str(exc)], status="INCOMPLETE")
    receipt_path = receipt if isinstance(receipt, Path) else None
    annotated_hash = contract.annotated_hash(script_text)
    spoken_hash = contract.spoken_hash(script_text)
    spoken = contract.canonical_spoken(script_text)
    try:
        raw = _load_object(receipt, label="receipt")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _result([str(exc)], status="INCOMPLETE")
    if not isinstance(raw, dict):
        return _result(["receipt must be a JSON object"], status="INCOMPLETE")
    source_meta = raw.get("source")
    if viewer_artifact is None and isinstance(source_meta, dict) and source_meta.get("viewer_artifact"):
        viewer_artifact = Path(str(source_meta["viewer_artifact"]))
    if screens is None and isinstance(source_meta, dict) and source_meta.get("screens"):
        screens = Path(str(source_meta["screens"]))
    if viewer_windows is None and isinstance(source_meta, dict) and source_meta.get("viewer_windows"):
        viewer_windows = Path(str(source_meta["viewer_windows"]))
    if viewer_reports is None and isinstance(source_meta, dict) and source_meta.get("viewer_reports"):
        viewer_reports = Path(str(source_meta["viewer_reports"]))

    extra_top = set(raw) - _RECEIPT_TOP_KEYS
    if extra_top:
        unexpected.extend(sorted(extra_top))
        errors.append("unexpected receipt field(s): " + _format_set(extra_top))
    if raw.get("schema") != RECEIPT_SCHEMA:
        errors.append(f"schema must be {RECEIPT_SCHEMA!r}")

    _validate_hash_field(errors, annotated_hash, raw, "annotated_script_hash", "annotated_script_hash", "annotated_sha256")
    _validate_hash_field(errors, spoken_hash, raw, "spoken_script_hash", "spoken_script_hash", "spoken_sha256")
    if narrative_map is None:
        errors.append("narrative_map is required to verify map_hash")
        actual_map_hash = None
        map_object = None
    else:
        try:
            map_object = _load_object(narrative_map, label="narrative_map")
            actual_map_hash = map_digest(map_object)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            map_object = None
            actual_map_hash = None
            errors.append(str(exc))
    if actual_map_hash is not None:
        _validate_hash_field(errors, actual_map_hash, raw, "map_hash", "map_hash", "map_sha256")
        if not isinstance(map_object, dict) or map_object.get("script_hash") != spoken_hash:
            errors.append("narrative map script_hash is required and must match the spoken script")
    elif not _is_sha(_hash_field(raw, "map_hash", "map_sha256")):
        errors.append("map_hash must be a lowercase SHA-256 hex string")

    # The top-level digest is the complete form-specific inventory.  A
    # receipt's stage only changes which rows are due; it must not permit a
    # stale/partial contract digest to masquerade as the current contract.
    # The value is checked after form parsing below as well, when
    # ``full_contract_digest`` is available.

    form = raw.get("form")
    if not isinstance(form, str) or form not in FORMS:
        errors.append("form must be 'long' or 'short'")
        form_value = None
    else:
        form_value = form
    if requested_form is not None and form != requested_form:
        errors.append("receipt form does not match requested form")
    stage = raw.get("stage")
    if not _stage(stage):
        errors.append("stage must be one of " + ", ".join(STAGES))
        stage_value = None
    else:
        stage_value = stage
    if requested_stage is not None and stage != requested_stage:
        errors.append("receipt stage does not match requested stage")
    scope = raw.get("scope")
    scope_ok, scope_error = _scope_valid(scope)
    if not scope_ok:
        errors.append(scope_error or "invalid scope")
    elif stage_value in {"text-review", "prefix-preview", "recording"} and not isinstance(scope, dict):
        errors.append(f"{stage_value} scope must be a structured object")
    elif isinstance(scope, dict) and stage_value in {"text-review", "recording"}:
        if scope.get("kind", scope.get("type")) != "full":
            errors.append(f"{stage_value} scope.kind must be 'full'")
        if float(scope.get("start_s", scope.get("start", -1))) != 0.0:
            errors.append(f"{stage_value} full scope must start at 0")
    elif isinstance(scope, dict) and stage_value == "prefix-preview":
        if scope.get("kind", scope.get("type")) != "prefix":
            errors.append("prefix-preview scope.kind must be 'prefix'")
        if float(scope.get("start_s", scope.get("start", -1))) != 0.0:
            errors.append("prefix-preview scope must start at 0")
    reviewers = raw.get("reviewers")
    if not isinstance(reviewers, list) or not reviewers:
        errors.append("reviewers must be a non-empty list of identities")
        reviewer_ids: set[str] = set()
    else:
        reviewer_ids = set()
        reviewer_roles: dict[str, str] = {}
        reviewer_runs: dict[str, str] = {}
        for index, reviewer in enumerate(reviewers):
            if not _reviewer_ok(reviewer):
                errors.append(f"reviewers[{index}] must include non-empty id, role and run_id")
            else:
                reviewer_id = str(reviewer.get("id", reviewer.get("reviewer_id")))
                reviewer_ids.add(reviewer_id)
                reviewer_roles[reviewer_id] = str(reviewer.get("role"))
                reviewer_runs[reviewer_id] = str(reviewer.get("run_id"))
        required_roles = {"semantic-reviewer", "blind-viewer", "independent-reviewer"}
        role_to_ids = {role: [identity for identity, actual in reviewer_roles.items() if actual == role]
                       for role in required_roles}
        for role, identities in role_to_ids.items():
            if len(identities) != 1:
                errors.append(f"reviewers must include exactly one {role}")
        required_ids = [identities[0] for identities in role_to_ids.values() if len(identities) == 1]
        required_runs = [reviewer_runs[identity] for identity in required_ids]
        if len(required_runs) == len(required_roles) and len(set(required_runs)) != len(required_runs):
            errors.append("semantic, blind-viewer and independent review must use distinct run_id values")
    if not isinstance(reviewers, list) or not reviewers:
        reviewer_roles = {}

    all_rows: list[contract.Obligation] = []
    if form_value:
        try:
            all_rows = contract.obligations(script_text, form_value, craft_map, screens)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            all_rows = []
            errors.append(f"contract inventory unavailable: {exc}")
    else:
        all_rows = []
    expected_rows = all_rows
    due_rows = contract.due_by(expected_rows, stage_value) if stage_value else []
    full_contract_digest = contract.contract_digest(all_rows)
    receipt_contract_digest = raw.get("contract_digest")
    if not _is_sha(receipt_contract_digest):
        errors.append("contract_digest must be a lowercase SHA-256 hex string")
    elif receipt_contract_digest != full_contract_digest:
        errors.append("contract_digest is stale or does not match the current contract inventory")
    expected = {row.id: row for row in due_rows}

    rows = raw.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("rows must be a non-empty list")
        rows = []
    seen: set[str] = set()
    actual_ids: set[str] = set()
    semantic_rationales: dict[str, str] = {}
    for index, row in enumerate(rows):
        label = f"rows[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        row_extra = set(row) - _ROW_KEYS
        if row_extra:
            errors.append(f"{label} has unexpected field(s): " + _format_set(row_extra))
        row_id = row.get("obligation_id", row.get("id"))
        if not isinstance(row_id, str) or not row_id.strip():
            errors.append(f"{label}.obligation_id must be a non-empty exact obligation ID")
            continue
        actual_ids.add(row_id)
        if row_id in seen:
            errors.append(f"duplicate review row: {row_id}")
        seen.add(row_id)
        if row_id not in expected:
            unexpected.append(row_id)
            errors.append(f"unexpected obligation row: {row_id}")
            continue
        obligation = expected[row_id]
        status = row.get("status")
        if status not in STATUSES:
            errors.append(f"{label} {row_id}.status must be one of {', '.join(sorted(STATUSES))}")
            continue
        rationale = row.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(f"{label} {row_id}.rationale must be non-empty")
        evidence = row.get("evidence")
        if evidence is not None and not isinstance(evidence, (str, list, dict)):
            errors.append(f"{label} {row_id}.evidence must be a string, list, or object")
        reviewer = row.get("reviewer")
        if reviewer is not None and (not isinstance(reviewer, str) or reviewer not in reviewer_ids):
            errors.append(f"{label} {row_id}.reviewer must name a declared reviewer identity")

        # Semantic rows need a source-bound quote or span.  Tool rows may use
        # an evidence artifact instead, because no spoken sentence is their
        # source.  Declared beats, map, reader, and viewer rows are always
        # source-bound by this rule.
        needs_span = obligation.owner in {"judge", "blind-viewer", "independent-reviewer"} or \
            obligation.id.startswith(("declared:", "map:"))
        if needs_span:
            expected_role = {"judge": "semantic-reviewer", "blind-viewer": "blind-viewer",
                             "independent-reviewer": "independent-reviewer"}.get(obligation.owner,
                                                                                  "semantic-reviewer")
            if not isinstance(reviewer, str):
                errors.append(f"{label} {row_id}.reviewer is required for semantic findings")
            elif reviewer_roles.get(reviewer) != expected_role:
                errors.append(f"{label} {row_id}.reviewer must have role {expected_role}")
            if not isinstance(rationale, str) or row_id not in rationale:
                errors.append(f"{label} {row_id}.rationale must name its exact obligation ID")
            elif rationale in semantic_rationales:
                errors.append(f"{label} {row_id}.rationale duplicates {semantic_rationales[rationale]}")
            else:
                semantic_rationales[rationale] = row_id
            if not isinstance(evidence, dict) or evidence.get("finding_id") != row_id or not evidence.get("source"):
                errors.append(f"{label} {row_id}.evidence must be an obligation-specific finding object")
        quote = row.get("quote")
        span = row.get("span")
        if quote is not None and (not isinstance(quote, str) or not quote.strip()):
            errors.append(f"{label} {row_id}.quote must be a non-empty string when supplied")
        if isinstance(quote, str) and quote.strip() and quote not in spoken:
            errors.append(f"{label} {row_id}.quote is not an exact substring of the spoken script")
        char_span: tuple[int, int] | None = None
        if span is not None:
            if isinstance(span, dict):
                start, end = span.get("start_char", span.get("start")), span.get("end_char", span.get("end"))
            elif isinstance(span, (list, tuple)) and len(span) == 2:
                start, end = span
            else:
                start = end = None
            if (isinstance(start, bool) or isinstance(end, bool) or
                    not isinstance(start, int) or not isinstance(end, int) or
                    start < 0 or end < start or end > len(spoken)):
                errors.append(f"{label} {row_id}.span must be an in-bounds character span")
            else:
                char_span = (start, end)
                if isinstance(quote, str) and quote and spoken[start:end] != quote:
                    errors.append(f"{label} {row_id}.span does not exactly match quote")
        if needs_span and not (isinstance(quote, str) and quote.strip()) and char_span is None:
            errors.append(f"{label} {row_id} requires an exact quote or span")
        if needs_span and char_span == (0, len(spoken)):
            errors.append(f"{label} {row_id}.span cannot cite the entire script")
        if needs_span and isinstance(quote, str) and len(quote) == len(spoken):
            errors.append(f"{label} {row_id}.quote cannot cite the entire script")

        dependencies = row.get("dependencies")
        if dependencies is not None:
            if not isinstance(dependencies, dict):
                errors.append(f"{label} {row_id}.dependencies must be an object")
            else:
                _validate_hash_field(errors, annotated_hash, dependencies, f"{label} annotated_script_hash", "annotated_script_hash", "annotated_sha256")
                _validate_hash_field(errors, spoken_hash, dependencies, f"{label} spoken_script_hash", "spoken_script_hash", "spoken_sha256")
                if actual_map_hash is not None:
                    _validate_hash_field(errors, actual_map_hash, dependencies, f"{label} map_hash", "map_hash", "map_sha256")
                _validate_hash_field(errors, full_contract_digest, dependencies, f"{label} contract_digest", "contract_digest")

        if status == "PASS":
            pass
        elif status == "WARN":
            warnings.append(row_id)
        elif status == "INFO":
            if row_id not in {"viewer:V04", "viewer:V05"}:
                errors.append(f"{label} {row_id}.status INFO is allowed only for viewer:V04 or viewer:V05")
        elif status == "FAIL":
            failed.append(row_id)
        elif status == "NOT_RUN":
            missing.append(row_id)
        elif status == "STALE":
            stale.append(row_id)
        elif status == "NA":
            basis = row.get("na_basis")
            if not isinstance(basis, str) or not basis.strip():
                errors.append(f"{label} {row_id}.na_basis is required for NA")
            elif obligation.source not in basis:
                errors.append(f"{label} {row_id}.na_basis must cite {obligation.source}")
            else:
                errors.append(f"{label} {row_id} is applicable to this form/stage; NA cannot clear it")
        elif status == "DEFERRED":
            target = row.get("deferred_to", row.get("defer_to"))
            if not _stage(target):
                errors.append(f"{label} {row_id}.deferred_to must name a later allowed stage")
            elif stage_value is not None and STAGE_ORDER[target] > STAGE_ORDER[stage_value]:
                errors.append(f"{label} {row_id} defers past requested stage {stage_value}")
            elif STAGE_ORDER[target] <= STAGE_ORDER[obligation.due_stage]:
                errors.append(f"{label} {row_id} must defer to a later stage than {obligation.due_stage}")
            else:
                deferred.append(row_id)

    missing.extend(sorted(set(expected) - actual_ids))
    if missing:
        errors.append("missing required obligation row(s): " + _format_set(missing))
    if _dependency_hashes(raw) is None:
        errors.append("dependencies must include receipt-level input hashes")
    else:
        dependencies = _dependency_hashes(raw) or {}
        _validate_hash_field(errors, annotated_hash, dependencies, "dependencies.annotated_script_hash", "annotated_script_hash", "annotated_sha256")
        _validate_hash_field(errors, spoken_hash, dependencies, "dependencies.spoken_script_hash", "spoken_script_hash", "spoken_sha256")
        if actual_map_hash is not None:
            _validate_hash_field(errors, actual_map_hash, dependencies, "dependencies.map_hash", "map_hash", "map_sha256")
        _validate_hash_field(errors, full_contract_digest, dependencies, "dependencies.contract_digest", "contract_digest")
        if stage_value in {"prefix-preview", "recording"}:
            if raw.get("timing_source") != "measured":
                errors.append(f"{stage_value} receipt timing_source must be 'measured'")
            if timeline is None or not Path(timeline).is_file():
                errors.append("recording receipt requires the measured word-clock file")
            else:
                try:
                    timeline_path = Path(timeline)
                    normalized = normalize_word_clock(timeline_path)
                    _validate_hash_field(errors, sha256_bytes(timeline_path.read_bytes()), dependencies,
                                         "dependencies.timeline_hash", "timeline_hash")
                    _validate_hash_field(errors, word_clock_digest(normalized), dependencies,
                                         "dependencies.normalized_timeline_hash", "normalized_timeline_hash")
                    clock_text = " ".join(str(row["w"]) for row in normalized)
                    if _alignment_tokens(clock_text) != _alignment_tokens(spoken):
                        errors.append("measured word clock does not align to the canonical spoken script")
                    if stage_value == "recording":
                        measured_end = float(normalized[-1]["end"])
                        scope_end = float(scope.get("end_s", scope.get("end", -1))) if isinstance(scope, dict) else -1.0
                        map_runtime = map_object.get("runtime_s") if isinstance(map_object, dict) else None
                        if not _number(map_runtime) or abs(float(map_runtime) - measured_end) > 0.01:
                            errors.append("recording narrative-map runtime must match the measured word clock")
                        if abs(scope_end - measured_end) > 0.01:
                            errors.append("recording full scope must end at the measured runtime")
                    if stage_value == "prefix-preview" and isinstance(scope, dict):
                        boundary = float(scope.get("end_s", scope.get("end", -1)))
                        ends = [float(row["end"]) for row in normalized]
                        if not any(abs(boundary - end) <= 0.001 for end in ends[:-1]):
                            errors.append("prefix-preview scope.end_s must match a measured word boundary before the full runtime")
                except (OSError, ValueError, json.JSONDecodeError) as exc:
                    errors.append(f"measured word clock invalid: {exc}")
            if scratch_take is None or not Path(scratch_take).is_file():
                if stage_value == "recording":
                    errors.append("recording receipt requires the aligned scratch take")
            else:
                if stage_value == "recording":
                    _validate_hash_field(errors, sha256_bytes(Path(scratch_take).read_bytes()), dependencies,
                                         "dependencies.scratch_take_hash", "scratch_take_hash")
        if stage_value is not None and STAGE_ORDER[stage_value] >= STAGE_ORDER["text-review"]:
            if screens is None or not Path(screens).is_file():
                errors.append(f"{stage_value} receipt requires the emitted strength-screens artifact")
            else:
                _validate_hash_field(errors, sha256_bytes(Path(screens).read_bytes()), dependencies,
                                     "dependencies.screens_hash", "screens_hash")
            if viewer_artifact is None or not Path(viewer_artifact).is_file():
                errors.append(f"{stage_value} receipt requires the complete blind-viewer artifact")
            else:
                viewer_path = Path(viewer_artifact)
                viewer_bytes = viewer_path.read_bytes()
                _validate_hash_field(errors, sha256_bytes(viewer_bytes), dependencies,
                                     "dependencies.viewer_artifact_hash", "viewer_artifact_hash")
                viewer_text = viewer_bytes.decode("utf-8")
                if f"script_hash: {spoken_hash}" not in viewer_text or f"annotated_script_hash: {annotated_hash}" not in viewer_text:
                    errors.append("blind-viewer artifact is stale or lacks script custody")
                viewer_matches = list(re.finditer(
                    r"^\s*\[(FAIL |WARN |PASS |INFO )\]\s+(V\d\d)\b", viewer_text, re.M))
                viewer_ids = [match.group(2) for match in viewer_matches]
                if len(viewer_ids) != len(set(viewer_ids)):
                    errors.append("blind-viewer artifact contains duplicate V-row IDs")
                viewer_rows = {match.group(2): match.group(1).strip() for match in viewer_matches}
                present = set(viewer_rows)
                missing_viewer = sorted({"V01", "V02", "V03", "V04", "V05"} - present)
                if missing_viewer:
                    errors.append("blind-viewer artifact is partial: missing " + ", ".join(missing_viewer))
                if viewer_windows is None or viewer_reports is None or not Path(viewer_windows).is_file() or not Path(viewer_reports).is_file():
                    errors.append("blind-viewer artifact requires its windows and reports custody files")
                else:
                    try:
                        import viewer_score as viewer_score_module
                        windows_bytes = Path(viewer_windows).read_bytes()
                        windows_doc = json.loads(windows_bytes.decode("utf-8"))
                        reports_doc = json.loads(Path(viewer_reports).read_text(encoding="utf-8"))
                        custody_errors = viewer_score_module.validate_custody(
                            script_text, windows_doc, reports_doc, windows_bytes)
                        errors.extend("blind-viewer custody: " + item for item in custody_errors)
                        _validate_hash_field(errors, sha256_bytes(windows_bytes), dependencies,
                                             "dependencies.viewer_windows_hash", "viewer_windows_hash")
                        _validate_hash_field(errors, sha256_bytes(Path(viewer_reports).read_bytes()), dependencies,
                                             "dependencies.viewer_reports_hash", "viewer_reports_hash")
                        artifact_windows = re.search(r"^windows_hash:\s*([0-9a-f]{64})\s*$", viewer_text, re.M)
                        if not artifact_windows or artifact_windows.group(1) != reports_doc.get("windows_hash"):
                            errors.append("blind-viewer artifact windows_hash does not match the reports custody")
                        if not custody_errors:
                            recomputed = viewer_score_module.score(windows_doc, reports_doc, script_text)
                            recomputed["script_hash"] = windows_doc["script_hash"]
                            recomputed["annotated_script_hash"] = windows_doc["annotated_script_hash"]
                            recomputed["windows_hash"] = reports_doc["windows_hash"]
                            script_name = Path(script).name if isinstance(script, Path) else str(
                                windows_doc.get("script") or "script")
                            expected_viewer = viewer_score_module.render(recomputed, script_name)
                            if viewer_text.replace("\r\n", "\n") != expected_viewer.replace("\r\n", "\n"):
                                errors.append(
                                    "blind-viewer artifact does not match the deterministic score of raw reports")
                    except (OSError, ValueError, json.JSONDecodeError) as exc:
                        errors.append(f"blind-viewer custody invalid: {exc}")
                receipt_rows = {str(row.get("obligation_id", row.get("id"))): row
                                for row in rows if isinstance(row, dict)}
                for viewer_id, artifact_status in viewer_rows.items():
                    receipt_row = receipt_rows.get(f"viewer:{viewer_id}")
                    if receipt_row is not None and receipt_row.get("status") != artifact_status:
                        errors.append(f"viewer:{viewer_id} receipt status does not match blind-viewer artifact")
                    if artifact_status == "FAIL":
                        failed.append(f"viewer:{viewer_id}")
                    elif artifact_status == "WARN":
                        warnings.append(f"viewer:{viewer_id}")
    if map_object is not None:
        map_result = validate_narrative_map(map_object, spoken_script=spoken)
        if not map_result.ok:
            errors.extend("narrative map: " + error for error in map_result.errors)
    return _result(errors, missing=missing, unexpected=unexpected, failed=failed, warnings=warnings,
                   deferred=deferred, stale=stale, receipt=raw, receipt_path=receipt_path)


def normalize_word_clock(value: Any) -> list[dict[str, Any]]:
    """Normalize native take/build clocks and enforce ordered measured timing."""
    raw = _load_object(value, label="timeline")
    rows = raw.get("words") if isinstance(raw, dict) else raw
    if not isinstance(rows, list) or not rows:
        raise ValueError("timeline words must be a non-empty JSON array")
    normalized: list[dict[str, Any]] = []
    previous_start = -1.0
    previous_end = -1.0
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("w"), str) or not row["w"].strip():
            raise ValueError(f"timeline word {index} must contain non-empty w")
        start = _first(row, "start", "start_s", "s")
        end = _first(row, "end", "end_s", "e")
        if not _number(start) or not _number(end) or float(end) < float(start):
            raise ValueError(f"timeline word {index} has invalid timing")
        start_f, end_f = float(start), float(end)
        if start_f < previous_start or end_f < previous_end:
            raise ValueError(f"timeline word {index} is not monotonic")
        if row.get("estimated"):
            raise ValueError(f"timeline word {index} is estimated")
        normalized.append({"w": row["w"], "start": start_f, "end": end_f})
        previous_start, previous_end = start_f, end_f
    return normalized


def word_clock_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    return sha256_bytes(canonical_json(list(rows)).encode("utf-8"))


def _alignment_tokens(text: str) -> list[str]:
    return [token.replace("’", "'").lower()
            for token in re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)?", text)]


def _validate_unique_ids(items: Sequence[Any], label: str, errors: list[str], ids: set[str]) -> None:
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not _ID.fullmatch(item_id):
            errors.append(f"{label}[{index}].id must be a stable identifier")
            continue
        if item_id in seen or item_id in ids:
            errors.append(f"duplicate narrative ID: {item_id}")
        seen.add(item_id)
        ids.add(item_id)


def validate_narrative_map(map_value: Any, *, spoken_script: str | None = None,
                           runtime_s: float | None = None) -> ReviewResult:
    """Validate semantic micro/macro map relationships and coverage windows."""
    errors: list[str] = []
    try:
        raw = _load_object(map_value, label="narrative_map")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _result([str(exc)], status="INCOMPLETE")
    if not isinstance(raw, dict):
        return _result(["narrative map must be a JSON object"], status="INCOMPLETE")
    if raw.get("schema") != MAP_SCHEMA:
        errors.append(f"schema must be {MAP_SCHEMA!r}")
    if spoken_script is not None:
        expected_script_hash = sha256_bytes(spoken_script.encode("utf-8"))
        if raw.get("script_hash") != expected_script_hash:
            errors.append("narrative map script_hash is required and must match the spoken script")
    extra_map = set(raw) - _MAP_TOP_KEYS
    if extra_map:
        errors.append("unexpected narrative-map field(s): " + _format_set(extra_map))
    loops = raw.get("micro_loops", raw.get("micro"))
    phases = raw.get("macro_phases", raw.get("macro"))
    if not isinstance(loops, list) or not loops:
        errors.append("micro_loops must be a non-empty list")
        loops = []
    if not isinstance(phases, list) or not phases:
        errors.append("macro_phases must be a non-empty list")
        phases = []
    ids: set[str] = set()
    _validate_unique_ids(loops, "micro_loops", errors, ids)
    _validate_unique_ids(phases, "macro_phases", errors, ids)
    loop_by_id = {row.get("id"): row for row in loops if isinstance(row, dict) and isinstance(row.get("id"), str)}
    phase_by_id = {row.get("id"): row for row in phases if isinstance(row, dict) and isinstance(row.get("id"), str)}
    intervals: list[tuple[float, float, str]] = []
    phase_intervals: list[tuple[float, float, str]] = []
    loop_intervals: dict[str, tuple[float, float]] = {}
    next_links: dict[str, str] = {}
    for index, row in enumerate(loops):
        if not isinstance(row, dict):
            continue
        label = f"micro_loops[{index}]"
        extra = set(row) - _MICRO_KEYS
        if extra:
            errors.append(f"{label} has unexpected field(s): " + _format_set(extra))
        required = ("setup", "tension", "advance", "payoff")
        for key in required:
            if key not in row:
                errors.append(f"{label} missing {key}")
        spans = {key: _span(row.get(key)) for key in required}
        if any(value is None for value in spans.values()):
            errors.append(f"{label} setup/tension/advance/payoff must have valid ordered spans")
        else:
            ordered = [spans[key] for key in required if spans[key] is not None]
            if any(ordered[pos][0] > ordered[pos + 1][0] or ordered[pos][1] > ordered[pos + 1][1]
                   for pos in range(len(ordered) - 1)):
                errors.append(f"{label} spans are not temporally ordered")
            intervals.append((ordered[0][0], ordered[-1][1], str(row.get("id"))))
            if isinstance(row.get("id"), str):
                loop_intervals[str(row["id"])] = (ordered[0][0], ordered[-1][1])
        next_value = _first(row, "next_loop", "next_loop_id", "next")
        if not isinstance(next_value, str) or not next_value.strip():
            errors.append(f"{label}.next_loop must name the next relationship (use 'end' for the final loop)")
        elif next_value != "end" and next_value not in loop_by_id:
            errors.append(f"{label}.next_loop references unknown loop {next_value!r}")
        elif isinstance(row.get("id"), str):
            next_links[str(row["id"])] = next_value
        shared = _first(row, "shared_object_or_person", "shared_object", "shared_person", "shared")
        if not isinstance(shared, str) or not shared.strip():
            errors.append(f"{label} requires a shared object or person")
    for index, row in enumerate(phases):
        if not isinstance(row, dict):
            continue
        label = f"macro_phases[{index}]"
        extra = set(row) - _MACRO_KEYS
        if extra:
            errors.append(f"{label} has unexpected field(s): " + _format_set(extra))
        start = row.get("start_s", row.get("start"))
        end = row.get("end_s", row.get("end"))
        if not (_number(start) and _number(end)) or float(end) < float(start):
            errors.append(f"{label} requires an ordered start_s/end_s")
        else:
            phase_intervals.append((float(start), float(end), str(row.get("id"))))
        intent = row.get("intent", row.get("phase"))
        if not isinstance(intent, str) or not intent.strip():
            errors.append(f"{label}.intent must be non-empty")
        for relation_name in ("callbacks", "callback", "foreshadows", "foreshadow"):
            relations = row.get(relation_name, [])
            if relations is None:
                continue
            if not isinstance(relations, list):
                relations = [relations]
            for relation_index, relation in enumerate(relations):
                refs = _relationship_refs(relation)
                if len(refs) < 2:
                    errors.append(f"{label}.{relation_name}[{relation_index}] must name from and to IDs")
                for ref in refs:
                    if ref not in ids:
                        errors.append(f"{label}.{relation_name}[{relation_index}] references unknown ID {ref!r}")
    declared_runtime = raw.get("runtime_s", runtime_s)
    if declared_runtime is None:
        declared_runtime = max((end for _start, end, _id in intervals), default=0.0)
    if not _number(declared_runtime):
        errors.append("runtime_s must be a finite non-negative number")
        declared_runtime = 0.0
    runtime_value = float(declared_runtime)
    for start, end, item_id in [*intervals, *phase_intervals]:
        if start < 0 or end > runtime_value:
            errors.append(
                f"narrative span {item_id!r} ({start:g}-{end:g}s) must stay within runtime_s {runtime_value:g}s")
    diagnostics = coverage_diagnostics(intervals, runtime_value)
    full_gaps = _coverage_gaps(intervals, runtime_value)
    diagnostics["full"] = {"effective_end_s": runtime_value, "gaps": full_gaps, "ok": not full_gaps}
    if full_gaps:
        errors.append("micro-loop coverage must span the full runtime without gaps")

    if loop_intervals and len(loop_intervals) == len(loop_by_id):
        terminals = [loop_id for loop_id, target in next_links.items() if target == "end"]
        if len(terminals) != 1:
            errors.append("micro-loop graph must have exactly one terminal next_loop='end'")
        for loop_id, target in next_links.items():
            if target == "end" or target not in loop_intervals:
                continue
            if target == loop_id:
                errors.append(f"micro-loop {loop_id!r} cannot point to itself")
            elif loop_intervals[target][0] <= loop_intervals[loop_id][0]:
                errors.append(f"micro-loop {loop_id!r}.next_loop must advance forward in time")
        first = min(loop_intervals, key=lambda item: (loop_intervals[item][0], loop_intervals[item][1], item))
        visited: set[str] = set()
        cursor = first
        while cursor in next_links and cursor not in visited:
            visited.add(cursor)
            target = next_links[cursor]
            if target == "end":
                break
            cursor = target
        if cursor in visited and next_links.get(cursor) != "end":
            errors.append("micro-loop graph contains a cycle")
        if visited != set(loop_intervals):
            errors.append("every micro loop must be reachable exactly once from the opening loop")
    return _result(errors, diagnostics={"coverage": diagnostics}, receipt=raw)


def _coverage_gaps(intervals: Iterable[Any], runtime_s: float) -> list[dict[str, float | str]]:
    """Return uncovered spans across the entire runtime, not only 90/180/300 previews."""
    normalized: list[tuple[float, float]] = []
    for item in intervals:
        try:
            start, end = float(item[0]), float(item[1])
        except (TypeError, ValueError, IndexError):
            continue
        if end >= start:
            normalized.append((max(0.0, start), min(float(runtime_s), end)))
    normalized.sort()
    gaps: list[dict[str, float | str]] = []
    cursor = 0.0
    for start, end in normalized:
        if end < cursor or start > runtime_s:
            continue
        if start > cursor:
            gaps.append({"start_s": cursor, "end_s": start, "kind": "gap"})
        cursor = max(cursor, end)
    if cursor < runtime_s:
        gaps.append({"start_s": cursor, "end_s": float(runtime_s), "kind": "endpoint_tail"})
    return gaps


def coverage_diagnostics(intervals: Iterable[Any], runtime_s: float) -> dict[str, Any]:
    """Report loop coverage for 90/180/300s, retaining endpoint tails.

    ``intervals`` accepts ``(start, end)`` or ``(start, end, id)`` tuples.
    The endpoint tail is intentionally explicit: an interval ending at 87s
    does not falsely cover the remainder of the 90s window.
    """
    normalized: list[tuple[float, float, str]] = []
    for item in intervals:
        try:
            if len(item) == 2:
                start, end = item
                item_id = "loop"
            else:
                start, end, item_id = item[0], item[1], item[2]
        except (TypeError, IndexError):
            continue
        if _number(start) and _number(end) and float(end) >= float(start):
            normalized.append((float(start), float(end), str(item_id)))
    normalized.sort()
    result: dict[str, Any] = {"runtime_s": float(runtime_s), "windows": {}}
    for window in (90, 180, 300):
        end = min(float(runtime_s), float(window))
        gaps: list[dict[str, Any]] = []
        cursor = 0.0
        for start, finish, item_id in normalized:
            if start > end:
                break
            start = max(0.0, start)
            finish = min(end, finish)
            if finish < 0 or start > end or finish < start:
                continue
            if start > cursor:
                gaps.append({"start_s": cursor, "end_s": start, "kind": "gap"})
            cursor = max(cursor, finish)
        if cursor < end:
            gaps.append({"start_s": cursor, "end_s": end, "kind": "endpoint_tail"})
        covered = max(0.0, end - sum(float(gap["end_s"]) - float(gap["start_s"]) for gap in gaps))
        result["windows"][str(window)] = {
            "requested_end_s": float(window),
            "effective_end_s": end,
            "covered_s": covered,
            "uncovered_s": sum(float(gap["end_s"]) - float(gap["start_s"]) for gap in gaps),
            "gaps": gaps,
            "ok": not gaps,
        }
    return result


def validate_map(*args: Any, **kwargs: Any) -> ReviewResult:
    return validate_narrative_map(*args, **kwargs)


# Stable noun aliases make the adapter easy for the existing runner to adopt
# without creating a second validation implementation.
validate_script_review = validate_receipt
validate_review_receipt = validate_receipt
map_hash = map_digest


def render_receipt_markdown(receipt: Mapping[str, Any], result: ReviewResult | None = None) -> str:
    """Render a readable, non-authoritative companion for a receipt."""
    rows = receipt.get("rows", []) if isinstance(receipt, Mapping) else []
    lines = [
        f"# Script review receipt `{receipt.get('schema', '?')}`",
        "",
        f"- Form: `{receipt.get('form', '?')}`",
        f"- Stage: `{receipt.get('stage', '?')}`",
        f"- Scope: `{receipt.get('scope', '?')}`",
        f"- Annotated script: `{receipt.get('annotated_script_hash', receipt.get('annotated_sha256', '?'))}`",
        f"- Spoken script: `{receipt.get('spoken_script_hash', receipt.get('spoken_sha256', '?'))}`",
        f"- Narrative map: `{receipt.get('map_hash', receipt.get('map_sha256', '?'))}`",
        f"- Contract: `{receipt.get('contract_digest', '?')}`",
        "",
        "## Review rows",
        "",
        "| Obligation | Status | Quote/span | Rationale |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, Mapping):
            lines.append("| invalid row | FAIL | — | invalid row shape |")
            continue
        ident = row.get("obligation_id", row.get("id", "?"))
        status = row.get("status", "?")
        quote = str(row.get("quote", ""))
        if len(quote) > 80:
            quote = quote[:77] + "..."
        span = row.get("span")
        source = quote or (str(span) if span is not None else "—")
        rationale = str(row.get("rationale", "")).replace("|", "\\|").replace("\n", " ")
        source = source.replace("|", "\\|")
        lines.append(f"| `{ident}` | `{status}` | {source} | {rationale} |")
    if result is not None:
        lines.extend(["", f"**Validator:** `{result.status}`"])
        if result.errors:
            lines.extend(["", "### Validator findings", ""])
            lines.extend(f"- {error}" for error in result.errors)
    return "\n".join(lines) + "\n"


def render_narrative_map_markdown(map_value: Any, result: ReviewResult | None = None) -> str:
    raw = _load_object(map_value, label="narrative_map")
    loops = raw.get("micro_loops", raw.get("micro", [])) if isinstance(raw, dict) else []
    phases = raw.get("macro_phases", raw.get("macro", [])) if isinstance(raw, dict) else []
    lines = [f"# Narrative map `{raw.get('schema', '?') if isinstance(raw, dict) else '?'}`", "", "## Micro loops", "", "| ID | Setup | Tension | Advance | Payoff | Next | Shared |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in loops if isinstance(loops, list) else []:
        if not isinstance(row, Mapping):
            continue
        lines.append("| {id} | {setup} | {tension} | {advance} | {payoff} | {next} | {shared} |".format(
            id=row.get("id", "?"), setup=_span_text(row.get("setup")), tension=_span_text(row.get("tension")),
            advance=_span_text(row.get("advance")), payoff=_span_text(row.get("payoff")),
            next=row.get("next_loop", row.get("next", "?")),
            shared=row.get("shared_object_or_person", row.get("shared", "?")),
        ))
    lines.extend(["", "## Macro phases", "", "| ID | Window | Intent | Callbacks | Foreshadows |", "| --- | --- | --- | --- | --- |"])
    for row in phases if isinstance(phases, list) else []:
        if not isinstance(row, Mapping):
            continue
        lines.append(f"| {row.get('id', '?')} | {_span_text(row)} | {row.get('intent', row.get('phase', '?'))} | {row.get('callbacks', row.get('callback', '—'))} | {row.get('foreshadows', row.get('foreshadow', '—'))} |")
    if result is not None:
        lines.extend(["", f"**Validator:** `{result.status}`"])
        coverage = result.diagnostics.get("coverage", {}) if result.diagnostics else {}
        windows = coverage.get("windows", {}) if isinstance(coverage, dict) else {}
        if windows:
            lines.extend(["", "## Coverage diagnostics", "", "| Window | Covered | Uncovered | Endpoint/gaps |", "| --- | ---: | ---: | --- |"])
            for key, item in windows.items():
                gaps = ", ".join(f"{gap['start_s']:g}–{gap['end_s']:g}s {gap['kind']}" for gap in item.get("gaps", [])) or "—"
                lines.append(f"| {key}s | {item.get('covered_s', 0):g}s | {item.get('uncovered_s', 0):g}s | {gaps} |")
    return "\n".join(lines) + "\n"


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


render_markdown = render_receipt_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a complete script review receipt or narrative map")
    sub = parser.add_subparsers(dest="command", required=True)
    receipt_parser = sub.add_parser("receipt")
    receipt_parser.add_argument("script", type=Path)
    receipt_parser.add_argument("receipt", type=Path)
    receipt_parser.add_argument("--map", dest="map_path", type=Path, required=True)
    receipt_parser.add_argument("--craft-map", type=Path, default=contract.CRAFT_MAP)
    receipt_parser.add_argument("--timeline", type=Path)
    receipt_parser.add_argument("--scratch-take", type=Path)
    receipt_parser.add_argument("--viewer-artifact", type=Path)
    receipt_parser.add_argument("--screens", type=Path)
    receipt_parser.add_argument("--viewer-windows", type=Path)
    receipt_parser.add_argument("--viewer-reports", type=Path)
    receipt_parser.add_argument("--markdown", type=Path)
    map_parser = sub.add_parser("map")
    map_parser.add_argument("map", type=Path)
    map_parser.add_argument("--script", type=Path)
    map_parser.add_argument("--markdown", type=Path)
    args = parser.parse_args(argv)
    if args.command == "receipt":
        result = validate_receipt(args.script, args.receipt, narrative_map=args.map_path,
                                  craft_map=args.craft_map, timeline=args.timeline,
                                  scratch_take=args.scratch_take,
                                  viewer_artifact=args.viewer_artifact, screens=args.screens,
                                  viewer_windows=args.viewer_windows,
                                  viewer_reports=args.viewer_reports)
        if args.markdown:
            write_markdown(args.markdown, render_receipt_markdown(result.receipt or {}, result))
    else:
        spoken = contract.canonical_spoken(_script_text(args.script)) if args.script else None
        result = validate_narrative_map(args.map, spoken_script=spoken)
        if args.markdown:
            write_markdown(args.markdown, render_narrative_map_markdown(result.receipt or {}, result))
    print(f"{args.command.upper()} REVIEW: {result.status}")
    for error in result.errors:
        print(f"  - {error}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
