"""Extract the Fed-liquidity episode's retained primary data, locally and deterministically.

The extractor never fetches.  It accepts the original and fresh raw run
directories explicitly, verifies each fetched manifest artifact before reading
any source payload, and emits only normalized evidence under ``evidence/derived``.
``--check`` performs the complete validation without touching output files.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import parse_qs, urlparse


SCHEMA = "mp-fed-liquidity.extraction.v1"
CUTOFF = dt.date(2026, 9, 18)
RRP_START = dt.date(2022, 1, 1)
RATE_UNIT_MAX = Decimal("100")
RRP_QUANTUM = Decimal("0.001")
RATE_QUANTUM = Decimal("0.01")
BPS_QUANTUM = Decimal("0.01")


class ExtractionError(ValueError):
    """Raised when retained evidence fails a closed validation rule."""


@dataclass(frozen=True)
class Artifact:
    root: Path
    relative_path: str
    path: Path
    url: str
    sha256: str
    bytes: int
    fetched_at: str | None


@dataclass(frozen=True)
class ManifestAudit:
    root: Path
    manifest_path: Path
    manifest_sha256: str
    declared_entries: int
    verified_entries: int
    not_fetched_entries: int
    artifacts: tuple[Artifact, ...]

    def find(self, filename: str, *, url_contains: str | None = None) -> Artifact:
        matches = [a for a in self.artifacts if Path(a.relative_path).name == filename]
        if url_contains:
            matches = [a for a in matches if url_contains in a.url]
        if len(matches) != 1:
            detail = ", ".join(a.relative_path for a in matches) or "none"
            raise ExtractionError(
                f"expected one manifest artifact {filename!r} ({url_contains or 'any URL'}), got {detail}"
            )
        return matches[0]


@dataclass(frozen=True)
class ExtractionBundle:
    metadata: dict[str, Any]
    outputs: dict[str, bytes]


def _fail(message: str) -> None:
    raise ExtractionError(message)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _posix_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        _fail(f"manifest path escapes archive root: {path}")
        raise AssertionError from exc


def _entry_path(root: Path, entry: Mapping[str, Any]) -> tuple[Path, str]:
    """Resolve a manifest entry without accepting a path outside its archive."""
    declared = entry.get("file")
    if declared:
        path = root / str(declared)
        relative = Path(str(declared)).as_posix()
    else:
        raw_path = str(entry.get("path", ""))
        if not raw_path:
            _fail("manifest entry has neither file nor path")
        path = Path(raw_path)
        if not path.is_absolute():
            path = root / path
        relative = _posix_relative(path, root)
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        _fail(f"manifest entry path is outside archive root: {path}")
        raise AssertionError from exc
    return resolved, relative


def verify_manifest(run_dir: Path) -> ManifestAudit:
    """Verify every fetched artifact declared by one immutable run manifest."""
    root = run_dir.expanduser().resolve()
    manifest_path = root / "MANIFEST.json"
    if not manifest_path.is_file():
        _fail(f"manifest missing: {manifest_path}")
    manifest_bytes = manifest_path.read_bytes()
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail(f"manifest is not valid UTF-8 JSON: {manifest_path}: {exc}")
    entries = manifest.get("entries") or manifest.get("artifacts")
    if not isinstance(entries, list) or not entries:
        _fail(f"manifest has no entries: {manifest_path}")

    artifacts: list[Artifact] = []
    not_fetched = 0
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            _fail(f"manifest entry {index} is not an object")
        url = entry.get("url")
        if not isinstance(url, str) or not url.strip():
            _fail(f"manifest entry {index} requires a non-empty url")
        fetched_at = entry.get("fetched_at")
        if not isinstance(fetched_at, str) or not fetched_at.strip():
            _fail(f"manifest entry {index} requires a non-empty fetched_at timestamp")
        try:
            dt.datetime.fromisoformat(fetched_at.strip().replace("Z", "+00:00"))
        except ValueError as exc:
            _fail(f"manifest entry {index} has invalid fetched_at timestamp: {fetched_at!r}")
            raise AssertionError from exc
        if entry.get("status") == "not-fetched":
            not_fetched += 1
            continue
        path, relative = _entry_path(root, entry)
        if not path.is_file():
            _fail(f"manifest artifact missing: {relative}")
        expected_sha_value = entry.get("sha256")
        if not isinstance(expected_sha_value, str):
            _fail(f"manifest artifact {relative} requires a string sha256")
        expected_sha = expected_sha_value.lower()
        if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
            _fail(f"manifest artifact {relative} has invalid sha256")
        expected_bytes = entry.get("bytes")
        if type(expected_bytes) is not int or expected_bytes < 0:
            _fail(f"manifest artifact {relative} requires a non-negative integer bytes field")
        if expected_bytes != path.stat().st_size:
            _fail(
                f"manifest byte mismatch for {relative}: expected {expected_bytes}, got {path.stat().st_size}"
            )
        actual_sha = _sha256(path)
        if actual_sha != expected_sha:
            _fail(f"manifest hash mismatch for {relative}: expected {expected_sha}, got {actual_sha}")
        artifacts.append(
            Artifact(
                root=root,
                relative_path=relative,
                path=path,
                url=url,
                sha256=actual_sha,
                bytes=path.stat().st_size,
                fetched_at=fetched_at,
            )
        )
    if not artifacts:
        _fail(f"manifest contains no fetched artifacts: {manifest_path}")
    return ManifestAudit(
        root=root,
        manifest_path=manifest_path,
        manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        declared_entries=len(entries),
        verified_entries=len(artifacts),
        not_fetched_entries=not_fetched,
        artifacts=tuple(sorted(artifacts, key=lambda item: item.relative_path)),
    )


def _read_text(artifact: Artifact) -> str:
    try:
        return artifact.path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        _fail(f"source is not UTF-8 text: {artifact.relative_path}: {exc}")
        raise AssertionError from exc


def _metadata_contains(artifact: Artifact, *terms: str) -> None:
    text = _read_text(artifact).casefold()
    for term in terms:
        if term.casefold() not in text:
            _fail(f"metadata {artifact.relative_path} lacks required unit/meaning text: {term!r}")


def _parse_date(value: Any, context: str) -> dt.date:
    if not isinstance(value, str):
        _fail(f"{context}: date is not a string")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        _fail(f"{context}: invalid ISO date {value!r}")
        raise AssertionError from exc


def _decimal(value: Any, context: str) -> Decimal:
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        _fail(f"{context}: not a decimal value: {value!r}")
        raise AssertionError from exc
    if not number.is_finite():
        _fail(f"{context}: non-finite decimal value: {value!r}")
    return number


def _money(value: Any, context: str) -> Decimal:
    number = _decimal(value, context)
    if number < 0 or number != number.to_integral_value():
        _fail(f"{context}: expected non-negative whole USD amount, got {value!r}")
    return number


def _percent(value: Any, context: str) -> Decimal:
    number = _decimal(value, context)
    # The archived metadata/schema define these fields as percentages.  Keep
    # valid sub-one-percent historical rates; reject only negative, non-finite,
    # or impossible >100-percent values rather than imposing an economic floor.
    if number < 0 or number > RATE_UNIT_MAX:
        _fail(f"{context}: expected percent units in [0, 100], got {value!r}")
    if number != number.quantize(RATE_QUANTUM):
        _fail(f"{context}: unsupported precision; source percent must be at most 2 decimals: {value!r}")
    return number


def _rrp_value(value: str, context: str) -> Decimal | None:
    stripped = value.strip()
    if not stripped or stripped == ".":
        return None
    number = _decimal(stripped, context)
    if number < 0:
        _fail(f"{context}: negative RRP value")
    if number != number.quantize(RRP_QUANTUM):
        _fail(f"{context}: unsupported precision; source RRP must be at most 3 decimals: {value!r}")
    return number


def _load_csv(artifact: Artifact, expected_header: list[str]) -> list[dict[str, str]]:
    try:
        with artifact.path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != expected_header:
                _fail(
                    f"{artifact.relative_path}: expected header {expected_header!r}, got {reader.fieldnames!r}"
                )
            return list(reader)
    except OSError as exc:
        _fail(f"cannot read {artifact.relative_path}: {exc}")
        raise AssertionError from exc


def _load_json(artifact: Artifact) -> Any:
    try:
        return json.loads(artifact.path.read_text(encoding="utf-8"), parse_float=Decimal, parse_int=Decimal)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail(f"invalid JSON {artifact.relative_path}: {exc}")
        raise AssertionError from exc


def _rows_from_ref_rates(artifact: Artifact, expected_type: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    data = _load_json(artifact)
    rows = data.get("refRates") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        _fail(f"{artifact.relative_path}: expected non-empty refRates list")
    start, end = _required_url_window(artifact.url, artifact.relative_path)
    seen: set[dt.date] = set()
    parsed: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            _fail(f"{artifact.relative_path}: refRates[{index}] is not an object")
        if row.get("type") != expected_type:
            _fail(
                f"{artifact.relative_path}: requested type {expected_type!r}, got {row.get('type')!r}"
            )
        date = _parse_date(row.get("effectiveDate"), f"{artifact.relative_path}:refRates[{index}]")
        _check_url_date(date, start, end, f"{artifact.relative_path}:refRates[{index}]")
        if date in seen:
            _fail(f"{artifact.relative_path}: duplicate effectiveDate {date}")
        seen.add(date)
        rate = _percent(row.get("percentRate"), f"{artifact.relative_path}:{date}:percentRate")
        volume = row.get("volumeInBillions")
        volume_decimal = None
        if volume is not None:
            volume_decimal = _decimal(volume, f"{artifact.relative_path}:{date}:volumeInBillions")
            if volume_decimal < 0:
                _fail(f"{artifact.relative_path}:{date}: negative volume")
        parsed.append({"date": date, "type": expected_type, "rate": rate, "volume": volume_decimal})
    parsed.sort(key=lambda row: row["date"])
    return parsed, {
        "source": _artifact_metadata(artifact),
        "type": expected_type,
        "requested_window": {"start": start.isoformat(), "end": end.isoformat()} if start and end else None,
        "source_count": len(parsed),
        "source_window": {"start": parsed[0]["date"].isoformat(), "end": parsed[-1]["date"].isoformat()},
    }


def _url_window(url: str) -> tuple[dt.date | None, dt.date | None]:
    query = parse_qs(urlparse(url).query)
    try:
        start = _parse_date(query["startDate"][0], "source URL startDate") if query.get("startDate") else None
        end = _parse_date(query["endDate"][0], "source URL endDate") if query.get("endDate") else None
    except KeyError:
        return None, None
    return start, end


def _required_url_window(url: str, context: str) -> tuple[dt.date, dt.date]:
    start, end = _url_window(url)
    if start is None or end is None or start > end:
        _fail(f"{context}: URL must provide a valid startDate/endDate window")
    return start, end


def _check_url_date(date: dt.date, start: dt.date, end: dt.date, context: str) -> None:
    if date < start or date > end:
        _fail(f"{context}: observation date {date} is outside requested URL window {start}..{end}")


def _artifact_metadata(artifact: Artifact) -> dict[str, Any]:
    return {
        "path": artifact.relative_path,
        "url": artifact.url,
        "sha256": artifact.sha256,
        "bytes": artifact.bytes,
        "fetched_at": artifact.fetched_at,
    }


def _expected_weekdays(start: dt.date, end: dt.date) -> list[dt.date]:
    return [
        start + dt.timedelta(days=offset)
        for offset in range((end - start).days + 1)
        if (start + dt.timedelta(days=offset)).weekday() < 5
    ]


def _csv_bytes(headers: list[str], rows: Iterable[Mapping[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in headers})
    return stream.getvalue().encode("utf-8")


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, separators=(",", ": ")) + "\n").encode(
        "utf-8"
    )


def _decimal_text(value: Decimal) -> str:
    return format(value, "f")


def _parse_rrp(artifact: Artifact, metadata_artifact: Artifact, start: dt.date, cutoff: dt.date) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    _metadata_contains(
        metadata_artifact,
        "Billions of US Dollars",
        "Not Seasonally Adjusted",
        "Daily",
        "aggregated daily amount",
    )
    source_rows = _load_csv(artifact, ["observation_date", "RRPONTSYD"])
    seen: set[dt.date] = set()
    rows: list[dict[str, Any]] = []
    missing = 0
    post_cutoff = 0
    for index, raw in enumerate(source_rows, 2):
        date = _parse_date(raw["observation_date"], f"{artifact.relative_path}:{index}")
        if date in seen:
            _fail(f"{artifact.relative_path}: duplicate observation_date {date}")
        seen.add(date)
        value = _rrp_value(raw["RRPONTSYD"], f"{artifact.relative_path}:{index}")
        if date > cutoff:
            if value is not None:
                post_cutoff += 1
            continue
        if date < start:
            continue
        if value is None:
            missing += 1
            continue
        rows.append({"observation_date": date, "value_usd_billions": value})
    rows.sort(key=lambda row: row["observation_date"])
    if not rows:
        _fail("RRP extraction produced no observations")
    return rows, {
        "source": _artifact_metadata(artifact),
        "metadata_source": _artifact_metadata(metadata_artifact),
        "series": "RRPONTSYD",
        "units": "USD billions",
        "window": {"start": start.isoformat(), "end": cutoff.isoformat()},
        "observations": len(rows),
        "missing_value_rows_excluded": missing,
        "post_cutoff_nonempty_excluded": post_cutoff,
        "duplicate_dates": 0,
        "interpolation": False,
    }


def _parse_iorb(artifact: Artifact, metadata_artifact: Artifact, cutoff: dt.date) -> tuple[dict[dt.date, Decimal], dict[str, Any]]:
    _metadata_contains(
        metadata_artifact,
        "Interest Rate on Reserve Balances",
        "Percent, Not Seasonally Adjusted",
        "Board of Governors",
        "Daily",
    )
    source_rows = _load_csv(artifact, ["observation_date", "IORB"])
    seen: set[dt.date] = set()
    all_values: dict[dt.date, Decimal] = {}
    missing = 0
    post_cutoff_nonempty = 0
    for index, raw in enumerate(source_rows, 2):
        date = _parse_date(raw["observation_date"], f"{artifact.relative_path}:{index}")
        if date in seen:
            _fail(f"{artifact.relative_path}: duplicate observation_date {date}")
        seen.add(date)
        value = raw["IORB"].strip()
        if not value or value == ".":
            missing += 1
            continue
        rate = _percent(value, f"{artifact.relative_path}:{index}:IORB")
        all_values[date] = rate
        if date > cutoff:
            post_cutoff_nonempty += 1
    filtered = {date: value for date, value in all_values.items() if date <= cutoff}
    if not filtered:
        _fail("IORB extraction produced no observations through cutoff")
    return filtered, {
        "source": _artifact_metadata(artifact),
        "metadata_source": _artifact_metadata(metadata_artifact),
        "series": "IORB",
        "units": "percent",
        "all_nonempty_observations": len(all_values),
        "observations_through_cutoff": len(filtered),
        "excluded_post_cutoff_nonempty": post_cutoff_nonempty,
        "missing_value_rows": missing,
        "window_through_cutoff": {"start": min(filtered).isoformat(), "end": max(filtered).isoformat()},
        "cutoff": cutoff.isoformat(),
    }


def _parse_details(details: Any, context: str) -> list[dict[str, Any]]:
    if not isinstance(details, list) or not details:
        _fail(f"{context}: expected non-empty details list")
    parsed: list[dict[str, Any]] = []
    allowed = {"Treasury", "Agency", "Mortgage-Backed", "SRF"}
    for index, detail in enumerate(details):
        if not isinstance(detail, dict):
            _fail(f"{context}: details[{index}] is not an object")
        security = detail.get("securityType")
        if security not in allowed:
            _fail(f"{context}: unexpected securityType {security!r}")
        submitted = _money(detail.get("amtSubmitted"), f"{context}:{security}:amtSubmitted")
        accepted = _money(detail.get("amtAccepted"), f"{context}:{security}:amtAccepted")
        rate = _percent(detail.get("percentOfferingRate"), f"{context}:{security}:percentOfferingRate")
        parsed.append({"security_type": security, "submitted": submitted, "accepted": accepted, "rate": rate})
    return parsed


def _operation_rows(data: Any, context: str) -> list[dict[str, Any]]:
    try:
        rows = data["repo"]["operations"]
    except (KeyError, TypeError):
        _fail(f"{context}: expected $.repo.operations")
    if not isinstance(rows, list) or not rows:
        _fail(f"{context}: expected non-empty operations list")
    return rows


def _parse_repo_results(artifact: Artifact, cutoff: dt.date) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = _operation_rows(_load_json(artifact), artifact.relative_path)
    start, end = _required_url_window(artifact.url, artifact.relative_path)
    seen_ids: set[str] = set()
    parsed: list[dict[str, Any]] = []
    excluded_future = 0
    for index, raw in enumerate(rows):
        if not isinstance(raw, dict):
            _fail(f"{artifact.relative_path}: operations[{index}] is not an object")
        operation_id = str(raw.get("operationId", ""))
        if not operation_id or operation_id in seen_ids:
            _fail(f"{artifact.relative_path}: duplicate/missing operationId {operation_id!r}")
        seen_ids.add(operation_id)
        if raw.get("operationType") != "Repo":
            _fail(f"{artifact.relative_path}: expected operationType Repo, got {raw.get('operationType')!r}")
        if raw.get("auctionStatus") != "Results":
            _fail(f"{artifact.relative_path}:{operation_id}: expected auctionStatus Results")
        if raw.get("operationMethod") != "Full Allotment":
            _fail(f"{artifact.relative_path}:{operation_id}: expected Full Allotment")
        if raw.get("term") != "Overnight":
            _fail(f"{artifact.relative_path}:{operation_id}: expected Overnight term")
        date = _parse_date(raw.get("operationDate"), f"{artifact.relative_path}:{operation_id}:operationDate")
        _check_url_date(date, start, end, f"{artifact.relative_path}:{operation_id}")
        if date > cutoff:
            excluded_future += 1
            continue
        details = _parse_details(raw.get("details"), f"{artifact.relative_path}:{operation_id}")
        submitted = _money(raw.get("totalAmtSubmitted"), f"{artifact.relative_path}:{operation_id}:totalAmtSubmitted")
        accepted = _money(raw.get("totalAmtAccepted"), f"{artifact.relative_path}:{operation_id}:totalAmtAccepted")
        if sum((detail["submitted"] for detail in details), Decimal(0)) != submitted:
            _fail(f"{artifact.relative_path}:{operation_id}: detail submitted sum does not equal total")
        if sum((detail["accepted"] for detail in details), Decimal(0)) != accepted:
            _fail(f"{artifact.relative_path}:{operation_id}: detail accepted sum does not equal total")
        parsed.append(
            {
                "operation_id": operation_id,
                "operation_date": date,
                "settlement_date": _parse_date(raw.get("settlementDate"), f"{operation_id}:settlementDate"),
                "maturity_date": _parse_date(raw.get("maturityDate"), f"{operation_id}:maturityDate"),
                "auction_status": raw["auctionStatus"],
                "operation_type": raw["operationType"],
                "operation_method": raw["operationMethod"],
                "settlement_type": str(raw.get("settlementType", "")),
                "term_calendar_days": int(raw.get("termCalenderDays")),
                "term": raw["term"],
                "release_time": str(raw.get("releaseTime", "")),
                "close_time": str(raw.get("closeTime", "")),
                "submitted": submitted,
                "accepted": accepted,
                "details": details,
            }
        )
    parsed.sort(key=lambda row: (row["operation_date"], row["operation_id"]))
    if not parsed:
        _fail("Repo extraction produced no operations through cutoff")
    return parsed, {
        "source": _artifact_metadata(artifact),
        "requested_window": {"start": start.isoformat(), "end": end.isoformat()} if start and end else None,
        "operations": len(parsed),
        "excluded_post_cutoff_operations": excluded_future,
        "operation_dates": len({row["operation_date"] for row in parsed}),
        "units": "USD",
        "take_up_field": "totalAmtAccepted",
        "outstanding_balance": False,
    }


def _parse_all_results(artifact: Artifact, cutoff: dt.date) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = _operation_rows(_load_json(artifact), artifact.relative_path)
    start, end = _required_url_window(artifact.url, artifact.relative_path)
    repos: list[dict[str, Any]] = []
    reverses: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(rows):
        if not isinstance(raw, dict):
            _fail(f"{artifact.relative_path}: operations[{index}] is not an object")
        operation_id = str(raw.get("operationId", ""))
        if not operation_id or operation_id in seen_ids:
            _fail(f"{artifact.relative_path}: duplicate/missing operationId {operation_id!r}")
        seen_ids.add(operation_id)
        operation_type = raw.get("operationType")
        if operation_type not in {"Repo", "Reverse Repo"}:
            _fail(f"{artifact.relative_path}:{operation_id}: unexpected operationType {operation_type!r}")
        date = _parse_date(raw.get("operationDate"), f"{artifact.relative_path}:{operation_id}:operationDate")
        _check_url_date(date, start, end, f"{artifact.relative_path}:{operation_id}")
        if date > cutoff:
            continue
        accepted = _money(raw.get("totalAmtAccepted"), f"{artifact.relative_path}:{operation_id}:totalAmtAccepted")
        record = {"operation_id": operation_id, "operation_date": date, "operation_type": operation_type, "accepted": accepted}
        (repos if operation_type == "Repo" else reverses).append(record)
    return sorted(repos, key=lambda row: (row["operation_date"], row["operation_id"])), sorted(
        reverses, key=lambda row: (row["operation_date"], row["operation_id"])
    )


def _parse_reverse_props(artifact: Artifact, cutoff: dt.date) -> list[dict[str, Any]]:
    rows = _operation_rows(_load_json(artifact), artifact.relative_path)
    start, end = _required_url_window(artifact.url, artifact.relative_path)
    seen_ids: set[str] = set()
    parsed: list[dict[str, Any]] = []
    for index, raw in enumerate(rows):
        if not isinstance(raw, dict):
            _fail(f"{artifact.relative_path}: operations[{index}] is not an object")
        operation_id = str(raw.get("operationId", ""))
        if not operation_id or operation_id in seen_ids:
            _fail(f"{artifact.relative_path}: duplicate/missing operationId {operation_id!r}")
        seen_ids.add(operation_id)
        if raw.get("operationType") != "Reverse Repo":
            _fail(f"{artifact.relative_path}:{operation_id}: expected Reverse Repo")
        date = _parse_date(raw.get("operationDate"), f"{artifact.relative_path}:{operation_id}:operationDate")
        _check_url_date(date, start, end, f"{artifact.relative_path}:{operation_id}")
        if date <= cutoff:
            parsed.append(
                {
                    "operation_id": operation_id,
                    "operation_date": date,
                    "operation_type": raw["operationType"],
                    "accepted": _money(raw.get("totalAmtAccepted"), f"{artifact.relative_path}:{operation_id}:totalAmtAccepted"),
                }
            )
    parsed.sort(key=lambda row: (row["operation_date"], row["operation_id"]))
    if not parsed:
        _fail("Reverse Repo extraction produced no operations through cutoff")
    return parsed


def _same_operation_amounts(left: list[dict[str, Any]], right: list[dict[str, Any]], context: str) -> None:
    left_map = {row["operation_id"]: row["accepted"] for row in left}
    right_map = {row["operation_id"]: row["accepted"] for row in right}
    if left_map != right_map:
        _fail(f"{context}: operation IDs/accepted amounts disagree")


def _manifest_metadata(audit: ManifestAudit) -> dict[str, Any]:
    return {
        "manifest": "MANIFEST.json",
        "declared_entries": audit.declared_entries,
        "verified_entries": audit.verified_entries,
        "not_fetched_entries": audit.not_fetched_entries,
    }


def build_extraction(
    original_run_dir: Path,
    raw_fetch_dir: Path,
    *,
    cutoff: dt.date = CUTOFF,
    rrp_start: dt.date = RRP_START,
) -> ExtractionBundle:
    """Verify both archives, parse retained raw sources, and build bytes in memory."""
    if rrp_start > cutoff:
        _fail("RRP start date must not be after cutoff")
    original = verify_manifest(original_run_dir)
    raw = verify_manifest(raw_fetch_dir)

    # Both manifests are verified before any source payload is read.  Fresh
    # raw sources are the production inputs; the original archive remains a
    # separately bound custody input and is intentionally not substituted.
    rrp_csv = raw.find("fred_rrpontsyd.csv", url_contains="RRPONTSYD")
    rrp_meta = raw.find("fred_rrpontsyd_meta.html", url_contains="RRPONTSYD")
    tgcr_artifact = raw.find("nyfed_tgcr_search_20250901_20260918.json", url_contains="/tgcr/")
    sofr_artifact = raw.find("nyfed_sofr_search_20250901_20260918.json", url_contains="/sofr/")
    iorb_csv = raw.find("fred_iorb_history.csv", url_contains="id=IORB")
    iorb_meta = raw.find("fred_iorb_meta.html", url_contains="/series/IORB")
    repo_artifact = raw.find("nyfed_srf_repo_results_20260901_20260918.json", url_contains="operationTypes=Repo")
    all_rp_artifact = raw.find("nyfed_all_rp_results_20260901_20260918.json", url_contains="/api/rp/results/search.json")
    reverse_artifact = raw.find("nyfed_rrp_propositions_20260901_20260918.json", url_contains="reverserepo/propositions")
    api_spec = raw.find("nyfed_markets_api_spec.yml", url_contains="markets-api.yml")
    # The OpenAPI archive names the repo fields but does not spell out the
    # reference-rate response member ``percentRate``; rate units are checked
    # against the preserved endpoint payloads below.
    _metadata_contains(api_spec, "totalAmtAccepted", "operationType")

    rrp_rows, rrp_meta_out = _parse_rrp(rrp_csv, rrp_meta, rrp_start, cutoff)
    iorb_values, iorb_meta_out = _parse_iorb(iorb_csv, iorb_meta, cutoff)
    tgcr_rows, tgcr_meta_out = _rows_from_ref_rates(tgcr_artifact, "TGCR")
    sofr_rows, sofr_meta_out = _rows_from_ref_rates(sofr_artifact, "SOFR")

    tgcr_by_date = {row["date"]: row for row in tgcr_rows if row["date"] <= cutoff}
    sofr_by_date = {row["date"]: row for row in sofr_rows if row["date"] <= cutoff}
    if set(tgcr_by_date) != set(sofr_by_date):
        _fail("TGCR and SOFR effective-date sets differ; exact join would hide an observation")
    rate_dates = sorted(tgcr_by_date)
    if not rate_dates:
        _fail("no TGCR/SOFR observations through cutoff")
    missing_iorb = sorted(date for date in rate_dates if date not in iorb_values)
    if missing_iorb:
        _fail(f"exact-date IORB join missing {len(missing_iorb)} dates: {missing_iorb[:5]}")

    rate_rows: list[dict[str, Any]] = []
    for date in rate_dates:
        iorb = iorb_values[date]
        tgcr = tgcr_by_date[date]
        sofr = sofr_by_date[date]
        tgcr_spread = (tgcr["rate"] - iorb) * Decimal("100")
        sofr_spread = (sofr["rate"] - iorb) * Decimal("100")
        if tgcr_spread != tgcr_spread.quantize(BPS_QUANTUM) or sofr_spread != sofr_spread.quantize(BPS_QUANTUM):
            _fail(f"rate spread on {date} has unsupported precision")
        rate_rows.append(
            {
                "effective_date": date,
                "iorb_percent": iorb,
                "tgcr_percent": tgcr["rate"],
                "tgcr_spread_bps": tgcr_spread,
                "tgcr_volume_billions": tgcr["volume"],
                "sofr_percent": sofr["rate"],
                "sofr_spread_bps": sofr_spread,
                "sofr_volume_billions": sofr["volume"],
            }
        )

    repo_rows, repo_meta_out = _parse_repo_results(repo_artifact, cutoff)
    all_repos, all_reverses = _parse_all_results(all_rp_artifact, cutoff)
    _same_operation_amounts(repo_rows, all_repos, "SRF Repo results vs all RP results")
    reverse_rows = _parse_reverse_props(reverse_artifact, cutoff)
    _same_operation_amounts(reverse_rows, all_reverses, "Reverse Repo propositions vs all RP results")

    repo_daily_map: dict[dt.date, dict[str, Any]] = {}
    for row in repo_rows:
        day = repo_daily_map.setdefault(
            row["operation_date"], {"operation_date": row["operation_date"], "operation_count": 0, "submitted": Decimal(0), "accepted": Decimal(0)}
        )
        day["operation_count"] += 1
        day["submitted"] += row["submitted"]
        day["accepted"] += row["accepted"]
    reverse_daily_map: dict[dt.date, dict[str, Any]] = {}
    for row in reverse_rows:
        day = reverse_daily_map.setdefault(
            row["operation_date"], {"operation_date": row["operation_date"], "operation_count": 0, "accepted": Decimal(0)}
        )
        day["operation_count"] += 1
        day["accepted"] += row["accepted"]

    rate_request_start, rate_request_end = _url_window(tgcr_artifact.url)
    rate_start = rate_request_start or min(rate_dates)
    rate_end = min(rate_request_end or cutoff, cutoff)
    expected_weekdays = _expected_weekdays(rate_start, rate_end)
    rate_gap_dates = [date for date in expected_weekdays if date not in set(rate_dates)]
    rate_meta = {
        "cutoff": cutoff.isoformat(),
        "exact_date_join": True,
        "joined_observations": len(rate_rows),
        "joined_window": {"start": min(rate_dates).isoformat(), "end": max(rate_dates).isoformat()},
        "missing_iorb_join_dates": [],
        "expected_weekdays_in_requested_window": len(expected_weekdays),
        "missing_weekday_count": len(rate_gap_dates),
        "missing_weekday_dates": [date.isoformat() for date in rate_gap_dates],
        "excluded_future_rate_rows": sum(row["date"] > cutoff for row in tgcr_rows),
        "tgcr": tgcr_meta_out,
        "sofr": sofr_meta_out,
        "iorb": iorb_meta_out,
        "units": {"rates": "percent", "spreads": "basis points", "volumes": "USD billions"},
        "interpolation": False,
    }
    repo_meta_out.update(
        {
            "total_submitted_usd": _decimal_text(sum((row["submitted"] for row in repo_rows), Decimal(0))),
            "total_accepted_usd": _decimal_text(sum((row["accepted"] for row in repo_rows), Decimal(0))),
            "daily_totals_are": "accepted take-up, not outstanding balance",
            "rate_by_date": {
                date.isoformat(): sorted({_decimal_text(detail["rate"]) for row in repo_rows if row["operation_date"] == date for detail in row["details"]})
                for date in sorted({row["operation_date"] for row in repo_rows})
            },
        }
    )
    reverse_meta = {
        "source": _artifact_metadata(reverse_artifact),
        "operations": len(reverse_rows),
        "operation_dates": len({row["operation_date"] for row in reverse_rows}),
        "total_accepted_usd": _decimal_text(sum((row["accepted"] for row in reverse_rows), Decimal(0))),
        "units": "USD",
        "separate_from_repo_take_up": True,
    }

    def rrp_output_rows() -> Iterable[dict[str, str]]:
        for row in rrp_rows:
            yield {"observation_date": row["observation_date"].isoformat(), "value_usd_billions": _decimal_text(row["value_usd_billions"])}

    def rate_output_rows() -> Iterable[dict[str, str]]:
        for row in rate_rows:
            yield {
                "effective_date": row["effective_date"].isoformat(),
                "iorb_percent": _decimal_text(row["iorb_percent"]),
                "tgcr_percent": _decimal_text(row["tgcr_percent"]),
                "tgcr_spread_bps": _decimal_text(row["tgcr_spread_bps"]),
                "tgcr_volume_billions": "" if row["tgcr_volume_billions"] is None else _decimal_text(row["tgcr_volume_billions"]),
                "sofr_percent": _decimal_text(row["sofr_percent"]),
                "sofr_spread_bps": _decimal_text(row["sofr_spread_bps"]),
                "sofr_volume_billions": "" if row["sofr_volume_billions"] is None else _decimal_text(row["sofr_volume_billions"]),
            }

    def repo_output_rows() -> Iterable[dict[str, str]]:
        for row in repo_rows:
            yield {
                "operation_id": row["operation_id"],
                "operation_date": row["operation_date"].isoformat(),
                "settlement_date": row["settlement_date"].isoformat(),
                "maturity_date": row["maturity_date"].isoformat(),
                "operation_type": row["operation_type"],
                "auction_status": row["auction_status"],
                "operation_method": row["operation_method"],
                "settlement_type": row["settlement_type"],
                "term_calendar_days": str(row["term_calendar_days"]),
                "term": row["term"],
                "release_time": row["release_time"],
                "close_time": row["close_time"],
                "total_amt_submitted_usd": _decimal_text(row["submitted"]),
                "total_amt_accepted_usd": _decimal_text(row["accepted"]),
            }

    def repo_detail_rows() -> Iterable[dict[str, str]]:
        for row in repo_rows:
            for detail in row["details"]:
                yield {
                    "operation_id": row["operation_id"],
                    "operation_date": row["operation_date"].isoformat(),
                    "security_type": detail["security_type"],
                    "amt_submitted_usd": _decimal_text(detail["submitted"]),
                    "amt_accepted_usd": _decimal_text(detail["accepted"]),
                    "percent_offering_rate": _decimal_text(detail["rate"]),
                }

    def repo_daily_rows() -> Iterable[dict[str, str]]:
        for date in sorted(repo_daily_map):
            row = repo_daily_map[date]
            yield {
                "operation_date": date.isoformat(),
                "operation_count": str(row["operation_count"]),
                "total_amt_submitted_usd": _decimal_text(row["submitted"]),
                "total_amt_accepted_usd": _decimal_text(row["accepted"]),
            }

    def reverse_output_rows() -> Iterable[dict[str, str]]:
        for row in reverse_rows:
            yield {
                "operation_id": row["operation_id"],
                "operation_date": row["operation_date"].isoformat(),
                "operation_type": row["operation_type"],
                "total_amt_accepted_usd": _decimal_text(row["accepted"]),
            }

    def reverse_daily_rows() -> Iterable[dict[str, str]]:
        for date in sorted(reverse_daily_map):
            row = reverse_daily_map[date]
            yield {
                "operation_date": date.isoformat(),
                "operation_count": str(row["operation_count"]),
                "total_amt_accepted_usd": _decimal_text(row["accepted"]),
            }

    outputs: dict[str, bytes] = {
        "rrp_daily.csv": _csv_bytes(["observation_date", "value_usd_billions"], rrp_output_rows()),
        "funding_rates.csv": _csv_bytes(
            [
                "effective_date",
                "iorb_percent",
                "tgcr_percent",
                "tgcr_spread_bps",
                "tgcr_volume_billions",
                "sofr_percent",
                "sofr_spread_bps",
                "sofr_volume_billions",
            ],
            rate_output_rows(),
        ),
        "repo_operations.csv": _csv_bytes(
            [
                "operation_id",
                "operation_date",
                "settlement_date",
                "maturity_date",
                "operation_type",
                "auction_status",
                "operation_method",
                "settlement_type",
                "term_calendar_days",
                "term",
                "release_time",
                "close_time",
                "total_amt_submitted_usd",
                "total_amt_accepted_usd",
            ],
            repo_output_rows(),
        ),
        "repo_operation_details.csv": _csv_bytes(
            ["operation_id", "operation_date", "security_type", "amt_submitted_usd", "amt_accepted_usd", "percent_offering_rate"],
            repo_detail_rows(),
        ),
        "repo_daily.csv": _csv_bytes(
            ["operation_date", "operation_count", "total_amt_submitted_usd", "total_amt_accepted_usd"], repo_daily_rows()
        ),
        "reverse_repo_operations.csv": _csv_bytes(
            ["operation_id", "operation_date", "operation_type", "total_amt_accepted_usd"], reverse_output_rows()
        ),
        "reverse_repo_daily.csv": _csv_bytes(
            ["operation_date", "operation_count", "total_amt_accepted_usd"], reverse_daily_rows()
        ),
    }

    metadata: dict[str, Any] = {
        "schema": SCHEMA,
        "cutoff": cutoff.isoformat(),
        "rrp_start": rrp_start.isoformat(),
        "local_only": True,
        "no_interpolation": True,
        "verified_manifests": {
            "original": _manifest_metadata(original),
            "raw_fetch": _manifest_metadata(raw),
        },
        "source_artifacts": [
            _artifact_metadata(artifact)
            for artifact in sorted(
                [rrp_csv, rrp_meta, tgcr_artifact, sofr_artifact, iorb_csv, iorb_meta, repo_artifact, all_rp_artifact, reverse_artifact, api_spec],
                key=lambda item: item.relative_path,
            )
        ],
        "rrp": rrp_meta_out,
        "rates": rate_meta,
        "repo": repo_meta_out,
        "reverse_repo": reverse_meta,
        "outputs": sorted([*outputs, "extraction_metadata.json"]),
    }
    outputs["extraction_metadata.json"] = _json_bytes(metadata)
    return ExtractionBundle(metadata=metadata, outputs=outputs)


def write_outputs(bundle: ExtractionBundle, output_dir: Path) -> None:
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in sorted(bundle.outputs):
        (output_dir / name).write_bytes(bundle.outputs[name])


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-run-dir", type=Path, required=True, help="immutable original research run archive")
    parser.add_argument("--raw-fetch-dir", type=Path, required=True, help="immutable fresh raw-fetch archive")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "derived",
        help="derived artifact directory (default: episode evidence/derived)",
    )
    parser.add_argument("--rrp-start", type=dt.date.fromisoformat, default=RRP_START)
    parser.add_argument("--cutoff", type=dt.date.fromisoformat, default=CUTOFF)
    parser.add_argument("--check", action="store_true", help="validate and extract in memory without writing outputs")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        bundle = build_extraction(args.original_run_dir, args.raw_fetch_dir, cutoff=args.cutoff, rrp_start=args.rrp_start)
        if not args.check:
            write_outputs(bundle, args.output_dir)
        print(
            f"extract_sources: PASS {'(check-only)' if args.check else 'wrote ' + str(args.output_dir.resolve())}; "
            f"RRP={bundle.metadata['rrp']['observations']} rate_join={bundle.metadata['rates']['joined_observations']} "
            f"repo_ops={bundle.metadata['repo']['operations']}"
        )
        return 0
    except (ExtractionError, OSError, ValueError, TypeError) as exc:
        print(f"extract_sources: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
