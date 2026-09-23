"""Validate the episode-local, pilot-only viewer-recall exception.

The original blind-reader markdown remains a historical record. This consumer
recomputes its score with ``viewer_score.score``, validates the dated current
recheck, and accepts only the current two V01 misses for an explicitly
approved bed/unit/minute/pilot prefix preflight. It never writes or changes
either markdown record, the JSON reports, or the viewer score.
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
SCHEMA = "fed-liquidity.pilot-viewer-review.v1"
REVIEW_PATH = Path("review/PILOT-VIEWER-REVIEW.json")
SCRIPT_NAME = "SCRIPT-VO.txt"
VIEWER_NAME = "SCRIPT-VIEWER-RECHECK-2026-09-22.md"
HISTORICAL_VIEWER_NAME = "SCRIPT-VIEWER.md"
WINDOWS_NAME = "SCRIPT-VIEWER-WINDOWS.json"
REPORTS_NAME = "SCRIPT-VIEWER-REPORTS.json"
WINDOWS_SCHEMA = "viewer_windows.v1"
REPORTS_SCHEMA = "viewer_reports.v1"
ELIGIBLE_SEGMENTS = frozenset({"bed", "unit", "minute", "pilot"})
ALLOWED_VERDICTS = frozenset({"MANUALLY_REVIEWED", "DEFERRED_TO_FULL_EPISODE"})
EXPECTED_MISSES = (
    ("archetype:w1", "archetype", 1),
    ("ring:w2", "ring", 2),
)
EXPECTED_MISS_IDS = frozenset(item[0] for item in EXPECTED_MISSES)
_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SCREEN_LINE_RE = re.compile(r"^\[screen\].*$", re.M)
_VIEWER_ROW_RE = re.compile(r"^\s*\[(?P<level>FAIL|WARN|PASS|INFO)\s*\]\s+(?P<id>V\d\d)\s+(?P<message>.*)$", re.M)
_VIEWER_RESULT_RE = re.compile(
    r"^RESULT:\s*(?P<fail>\d+)\s+FAIL\s*/\s*(?P<warn>\d+)\s+WARN\s*/\s*"
    r"(?P<pass>\d+)\s+PASS\s*/\s*(?P<info>\d+)\s+INFO\s*$",
    re.M,
)

_TOP_LEVEL_KEYS = frozenset(
    {
        "schema",
        "episode_id",
        "accepted_for",
        "script_hash",
        "artifacts",
        "operator_authorization",
        "misses",
    }
)
_AUTH_KEYS = frozenset({"quote", "reference"})
_ARTIFACT_KEYS = frozenset({"viewer", "windows", "reports"})
_ARTIFACT_REF_KEYS = frozenset({"path", "sha256"})
_MISS_KEYS = frozenset({"tag", "window", "script_quote", "reader_quote", "rationale", "verdict"})


@dataclass(frozen=True)
class ValidationResult:
    """Read-only result for one operator-authored viewer sidecar."""

    ok: bool
    errors: tuple[str, ...]
    score: dict[str, Any] | None = None

    @property
    def blockers(self) -> tuple[str, ...]:
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


def _load_tools() -> tuple[Any, Any, Any]:
    scripts_dir = Path(__file__).resolve().parents[3] / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import run_script_gates as gates  # type: ignore  # noqa: PLC0415
    import viewer_score  # type: ignore  # noqa: PLC0415
    import viewer_windows  # type: ignore  # noqa: PLC0415

    return gates, viewer_score, viewer_windows


def _validate_pair(
    *,
    script_text: str,
    windows_doc: Any,
    reports_doc: Any,
    viewer_windows: Any,
    errors: list[str],
) -> None:
    if not isinstance(windows_doc, dict) or not isinstance(reports_doc, dict):
        return
    if windows_doc.get("schema_version") != WINDOWS_SCHEMA or windows_doc.get("script") != SCRIPT_NAME:
        errors.append("viewer windows: invalid schema/script identity")
    if reports_doc.get("schema_version") != REPORTS_SCHEMA or reports_doc.get("script") != SCRIPT_NAME:
        errors.append("viewer reports: invalid schema/script identity")
    if reports_doc.get("windows_file") != WINDOWS_NAME:
        errors.append("viewer reports: windows_file is not SCRIPT-VIEWER-WINDOWS.json")

    windows = windows_doc.get("windows")
    reports = reports_doc.get("reports")
    if not isinstance(windows, list) or not isinstance(reports, list):
        errors.append("viewer: windows and reports must be arrays")
        return
    if len(windows) != 51:
        errors.append(f"viewer: expected 51 windows, got {len(windows)}")
    if len(reports) != 51:
        errors.append(f"viewer: expected 51 reports, got {len(reports)}")
    if reports_doc.get("windows_run") != len(windows):
        errors.append("viewer: windows_run does not cover all windows")

    for label, rows in (("windows", windows), ("reports", reports)):
        ids = [row.get("i") if isinstance(row, dict) else None for row in rows]
        if ids != list(range(len(rows))):
            errors.append(f"viewer: {label} indices must be contiguous and unique")
    if any(not isinstance(row, dict) or "error" in row for row in reports):
        errors.append("viewer reports: error entry present")
    if any(not isinstance(row, dict) or not isinstance(row.get("text"), str) for row in windows):
        errors.append("viewer windows: text is missing")
    for window, report in zip(windows, reports):
        if isinstance(window, dict) and isinstance(report, dict) and window.get("span") != report.get("span"):
            errors.append("viewer: report/window span mismatch")

    if all(isinstance(row, dict) and isinstance(row.get("text"), str) for row in windows):
        expected = viewer_windows.spoken(script_text).split()
        observed = " ".join(_SCREEN_LINE_RE.sub("", row["text"]) for row in windows).split()
        if expected != observed:
            errors.append("viewer windows: text does not match current spoken script")


def _validate_viewer_markdown(viewer_text: str, score: dict[str, Any], errors: list[str]) -> None:
    rows = [match.groupdict() for match in _VIEWER_ROW_RE.finditer(viewer_text)]
    failures = [row for row in rows if row["level"] == "FAIL"]
    score_rows = score.get("rows") or []
    expected_counts = {level: sum(1 for row in score_rows if row.get("level") == level) for level in ("FAIL", "WARN", "PASS", "INFO")}
    result_rows = list(_VIEWER_RESULT_RE.finditer(viewer_text))
    if len(result_rows) != 1:
        errors.append("viewer markdown: RESULT row is missing or malformed")
    else:
        result = result_rows[0]
        actual_counts = {level: int(result.group(level.lower())) for level in expected_counts}
        if actual_counts != expected_counts:
            errors.append("viewer markdown: RESULT counts do not match viewer_score.score")
    expected_by_id = {row.get("id"): row for row in score_rows if isinstance(row, dict)}
    actual_ids = [row["id"] for row in rows]
    if len(rows) != len(expected_by_id) or len(set(actual_ids)) != len(actual_ids) or set(actual_ids) != set(expected_by_id):
        errors.append("viewer markdown: raw rows must contain each recomputed V01-V05 row exactly once")
    for row in rows:
        expected = expected_by_id.get(row["id"])
        if expected is not None and (
            row["level"] != expected.get("level") or row["message"] != expected.get("message")
        ):
            errors.append(f"viewer markdown: {row['id']} row does not match recomputed viewer_score output")
    if len(failures) != 1 or failures[0]["id"] != "V01":
        errors.append("viewer markdown: only V01 may remain FAIL in the pilot exception")
    expected_v01 = next((row for row in score_rows if row.get("id") == "V01"), None)
    if expected_v01 is None:
        errors.append("viewer score: V01 row is missing")
    elif not any(row["id"] == "V01" and row["message"] == expected_v01.get("message") for row in rows):
        errors.append("viewer markdown: V01 row does not match recomputed viewer_score output")


def _validate_artifact(
    *,
    root: Path,
    actual_script_hash: str,
    spoken_script: str,
    file_hashes: dict[str, str],
    score: dict[str, Any],
    reports_doc: dict[str, Any],
    errors: list[str],
) -> None:
    path = root / REVIEW_PATH
    try:
        payload = _read_json(path)
    except FileNotFoundError:
        errors.append(f"pilot viewer review: missing ({REVIEW_PATH.as_posix()})")
        return
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"pilot viewer review: malformed JSON ({exc})")
        return

    _check_exact_keys(payload, _TOP_LEVEL_KEYS, "pilot viewer review", errors)
    if not isinstance(payload, dict):
        return
    if payload.get("schema") != SCHEMA:
        errors.append(f"pilot viewer review: schema must be {SCHEMA!r}")
    if payload.get("episode_id") != EPISODE_ID:
        errors.append(f"pilot viewer review: episode_id must be {EPISODE_ID!r}")
    if payload.get("accepted_for") != "pilot_only":
        errors.append("pilot viewer review: accepted_for must be 'pilot_only'")
    if payload.get("script_hash") != actual_script_hash:
        errors.append("pilot viewer review: script_hash is stale")

    artifacts = payload.get("artifacts")
    _check_exact_keys(artifacts, _ARTIFACT_KEYS, "pilot viewer review.artifacts", errors)
    if isinstance(artifacts, dict):
        for name, key in (("viewer", VIEWER_NAME), ("windows", WINDOWS_NAME), ("reports", REPORTS_NAME)):
            label = f"pilot viewer review.artifacts.{name}"
            reference = artifacts.get(name)
            _check_exact_keys(reference, _ARTIFACT_REF_KEYS, label, errors)
            if not isinstance(reference, dict):
                continue
            if reference.get("path") != key:
                errors.append(f"{label}.path must be {key!r}")
            value = reference.get("sha256")
            if not isinstance(value, str) or not _HEX_SHA256.fullmatch(value):
                errors.append(f"{label}.sha256 must be a lowercase SHA-256 hex string")
            elif value != file_hashes[key]:
                errors.append(f"{label}.sha256 is stale")

    authorization = payload.get("operator_authorization")
    _check_exact_keys(authorization, _AUTH_KEYS, "pilot viewer review.operator_authorization", errors)
    if isinstance(authorization, dict):
        quote = authorization.get("quote")
        reference = authorization.get("reference")
        if not isinstance(quote, str) or not quote.strip() or not re.search(r"\byes\b", quote, re.I):
            errors.append("pilot viewer review.operator_authorization.quote must quote an explicit YES")
        if not isinstance(reference, str) or not reference.strip():
            errors.append("pilot viewer review.operator_authorization.reference must be non-empty")

    score_rows = score.get("rows") or []
    v01 = next((row for row in score_rows if row.get("id") == "V01"), {})
    recall = score.get("recall") or []
    scored = [row for row in recall if row.get("window") is not None]
    missed = [f"{row.get('tag')}:w{row.get('window')}" for row in scored if not row.get("perceived")]
    report_rows_for_score = reports_doc.get("reports", [])
    if not isinstance(report_rows_for_score, list):
        report_rows_for_score = []
    expected_summary = {
        "score": sum(1 for row in scored if row.get("perceived")),
        "total": len(scored),
        "errors": sum(1 for row in report_rows_for_score if isinstance(row, dict) and "error" in row),
        "windows": score.get("windows"),
        "misses": len(missed),
    }
    if expected_summary != {"score": 61, "total": 63, "errors": 0, "windows": 51, "misses": 2}:
        errors.append("viewer score: expected exactly V01 61/63, two misses, 51 windows, and zero errors")
    if v01.get("level") != "FAIL" or missed != [item[0] for item in EXPECTED_MISSES]:
        errors.append("viewer score: raw V01 failure set is not the current two misses")

    rows = payload.get("misses")
    if not isinstance(rows, list):
        errors.append("pilot viewer review.misses must be a JSON array")
        rows = []
    elif len(rows) != len(EXPECTED_MISS_IDS):
        errors.append(f"pilot viewer review.misses must contain exactly {len(EXPECTED_MISS_IDS)} rows")
    row_ids: list[tuple[str, int]] = []
    report_rows = reports_doc.get("reports", [])
    if not isinstance(report_rows, list):
        report_rows = []
    reports_by_index: dict[int, dict[str, Any]] = {}
    for report in report_rows:
        if not isinstance(report, dict) or "i" not in report:
            continue
        report_index = report.get("i")
        if isinstance(report_index, bool) or not isinstance(report_index, int):
            errors.append("pilot viewer review: report indices must be integers")
            continue
        reports_by_index[report_index] = report
    for index, row in enumerate(rows):
        label = f"pilot viewer review.misses[{index}]"
        _check_exact_keys(row, _MISS_KEYS, label, errors)
        if not isinstance(row, dict):
            continue
        tag = row.get("tag")
        window = row.get("window")
        if not isinstance(tag, str) or isinstance(window, bool) or not isinstance(window, int):
            errors.append(f"{label}.tag must be a string and window must be an integer")
            continue
        expected = next((item for item in EXPECTED_MISSES if item[1] == tag and item[2] == window), None)
        if expected is None:
            errors.append(f"{label}.tag/window is not an allowed V01 miss")
            continue
        row_ids.append((tag, window))
        if row.get("verdict") not in ALLOWED_VERDICTS:
            errors.append(f"{label}.verdict must be MANUALLY_REVIEWED or DEFERRED_TO_FULL_EPISODE")
        script_quote = row.get("script_quote")
        expected_script_quote = next(
            (
                entry.get("sentence", "")
                for entry in scored
                if entry.get("tag") == expected[1]
                and entry.get("window") == expected[2]
                and not entry.get("perceived")
            ),
            "",
        )
        if not isinstance(script_quote, str) or not script_quote.strip():
            errors.append(f"{label}.script_quote must be non-empty spoken evidence")
        else:
            if script_quote not in spoken_script:
                errors.append(f"{label}.script_quote is not an exact quote from current spoken script")
            if expected_script_quote and expected_script_quote not in script_quote:
                errors.append(f"{label}.script_quote does not identify the recomputed missed beat")
        quote = row.get("reader_quote")
        report = reports_by_index.get(expected[2], {})
        reader_lines = []
        if isinstance(report, dict):
            reader_lines = [line for line in (list(report.get("new_things") or []) + [report.get("held_question") or "", report.get("asked_of_me") or ""]) if isinstance(line, str) and line.strip()]
        if not isinstance(quote, str) or not quote.strip():
            errors.append(f"{label}.reader_quote must be non-empty reader evidence")
        elif quote not in reader_lines:
            errors.append(f"{label}.reader_quote is not an exact reader quote from window {expected[2]}")
        rationale = row.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(f"{label}.rationale must be non-empty")
    if len(set(row_ids)) != len(row_ids):
        errors.append("pilot viewer review: duplicate miss tag/window")
    expected_pairs = {(tag, window) for _, tag, window in EXPECTED_MISSES}
    if set(row_ids) != expected_pairs:
        errors.append("pilot viewer review: miss rows do not match recomputed V01 misses")


def validate(project_root: Path, *, expected_script_hash: str | None = None) -> ValidationResult:
    """Validate raw viewer artifacts and the operator sidecar without writing."""

    root = Path(project_root).resolve()
    errors: list[str] = []
    paths = {
        "script": root / SCRIPT_NAME,
        VIEWER_NAME: root / VIEWER_NAME,
        WINDOWS_NAME: root / WINDOWS_NAME,
        REPORTS_NAME: root / REPORTS_NAME,
    }
    for label, path in paths.items():
        if not path.is_file():
            errors.append(f"viewer review: missing {label} ({path.name})")
    if errors:
        return ValidationResult(False, tuple(errors))
    try:
        script_text = paths["script"].read_text(encoding="utf-8")
        viewer_text = paths[VIEWER_NAME].read_text(encoding="utf-8")
        windows_doc = _read_json(paths[WINDOWS_NAME])
        reports_doc = _read_json(paths[REPORTS_NAME])
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        return ValidationResult(False, (f"viewer review: malformed source artifact ({exc})",))

    gates, scorer, windower = _load_tools()
    actual_script_hash = gates.script_hash(script_text)
    if expected_script_hash is not None and expected_script_hash != actual_script_hash:
        errors.append("pilot viewer review: supplied current script hash is stale")
    file_hashes = {key: _sha256(path) for key, path in paths.items() if key != "script"}
    _validate_pair(script_text=script_text, windows_doc=windows_doc, reports_doc=reports_doc, viewer_windows=windower, errors=errors)

    score: dict[str, Any] | None = None
    if isinstance(windows_doc, dict) and isinstance(reports_doc, dict):
        try:
            score = scorer.score(windows_doc, reports_doc, script_text)
            _validate_viewer_markdown(viewer_text, score, errors)
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            errors.append(f"viewer score: cannot recompute ({exc})")
    if score is None:
        score = {}
    _validate_artifact(
        root=root,
        actual_script_hash=actual_script_hash,
        spoken_script=gates.spoken_text(script_text),
        file_hashes=file_hashes,
        score=score,
        reports_doc=reports_doc if isinstance(reports_doc, dict) else {},
        errors=errors,
    )
    return ValidationResult(not errors, tuple(dict.fromkeys(errors)), score)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate the pilot-only viewer review sidecar")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args(argv)
    result = validate(args.project_root)
    if result.ok:
        print(f"pilot viewer review: PASS ({SCHEMA}; accepted_for=pilot_only)")
        return 0
    print("pilot viewer review: FAIL")
    for error in result.errors:
        print(f"  - {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
