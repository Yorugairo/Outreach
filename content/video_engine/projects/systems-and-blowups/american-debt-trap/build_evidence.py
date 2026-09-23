"""Build the American Debt Trap opening's three native ledger objects.

The builder is deliberately source-bound and deterministic.  It reads only the
retained Treasury/FRED inputs named by the 2026-09-20 evidence packet plus the
dated evidence snapshot for the CBO comparison.  It never fetches, interpolates,
decimates, or assembles a scene.  The emitted objects are ordinary
``series.json`` files consumed by ``ledger_page.py``.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


EPISODE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EPISODE_ROOT.parents[4]
RUN_ROOT = REPO_ROOT / "docs" / "research" / "runs" / "american-debt-trap-20260920"
CURRENT_EVIDENCE = REPO_ROOT / "docs" / "research" / "markets" / "AMERICAN-DEBT-TRAP-CURRENT-EVIDENCE-2026-09-20.md"
TREASURY_DATA = RUN_ROOT / "data" / "treasury-debt.json"
DGS20_DATA = RUN_ROOT / "data" / "DGS20.csv"
FRED_MANIFEST = RUN_ROOT / "fred-manifest.json"
DERIVED_EVIDENCE = RUN_ROOT / "derived-evidence.json"
OBJECTS_ROOT = EPISODE_ROOT / "evidence" / "objects"
RECEIPT_PATH = EPISODE_ROOT / "EVIDENCE-RECEIPT.json"

TREASURY_START = date(2025, 1, 1)
TREASURY_END = date(2026, 9, 17)
DGS20_START = date(2025, 1, 1)
DGS20_END = date(2026, 9, 17)

OBJECT_NAMES = (
    "debt-gross-history.series.json",
    "cbo-interest-revenue.series.json",
    "treasury-20y-yield.series.json",
)


class EvidenceError(RuntimeError):
    """Raised when a retained evidence input cannot be verified safely."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _read_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"{label}: cannot read JSON: {exc}") from exc


def _require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise EvidenceError(f"{label}: file missing: {_repo_relative(path)}")
    return path


def _verified_file(path: Path, expected: Any, label: str) -> dict[str, Any]:
    _require_file(path, label)
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        raise EvidenceError(f"{label}: expected SHA-256 is invalid")
    actual = _sha256(path)
    if actual.lower() != expected.lower():
        raise EvidenceError(f"{label}: SHA-256 mismatch (expected {expected}, got {actual})")
    return {
        "path": _repo_relative(path),
        "sha256": actual,
        "bytes": path.stat().st_size,
        "expected_sha256": expected.lower(),
        "hash_match": True,
    }


def _number(raw: Any, label: str) -> Decimal:
    try:
        value = Decimal(str(raw).strip())
    except (InvalidOperation, AttributeError) as exc:
        raise EvidenceError(f"{label}: expected a numeric value, got {raw!r}") from exc
    if not value.is_finite():
        raise EvidenceError(f"{label}: value is not finite")
    return value


def _decimal_year(day: date) -> float:
    start = date(day.year, 1, 1)
    next_year = date(day.year + 1, 1, 1)
    return round(day.year + (day - start).days / (next_year - start).days, 10)


def _date_ticks(first: date, last: date) -> list[list[float | str]]:
    """Return readable, endpoint-inclusive calendar ticks for the native line page."""
    candidates = [
        first,
        date(2025, 7, 1),
        date(2026, 1, 1),
        last,
    ]
    ticks: list[list[float | str]] = []
    seen: set[date] = set()
    for day in candidates:
        if not first <= day <= last or day in seen:
            continue
        seen.add(day)
        label = day.strftime("%b %Y") if day not in (first, last) else day.strftime("%b %d, %Y")
        ticks.append([_decimal_year(day), label])
    return ticks


def _load_verified_inputs() -> dict[str, Any]:
    derived = _read_json(DERIVED_EVIDENCE, "derived evidence")
    if not isinstance(derived, dict) or not isinstance(derived.get("treasury"), dict):
        raise EvidenceError("derived evidence: missing treasury block")
    treasury_expected = derived["treasury"].get("sha256")
    treasury_file = _verified_file(TREASURY_DATA, treasury_expected, "Treasury debt data")

    manifest = _read_json(FRED_MANIFEST, "FRED manifest")
    if not isinstance(manifest, list):
        raise EvidenceError("FRED manifest: expected an array")
    dgs_entries = [entry for entry in manifest if isinstance(entry, dict) and entry.get("series") == "DGS20"]
    if len(dgs_entries) != 1:
        raise EvidenceError(f"FRED manifest: expected one DGS20 entry, found {len(dgs_entries)}")
    dgs_entry = dgs_entries[0]
    if dgs_entry.get("status") != "fetched":
        raise EvidenceError("FRED manifest: DGS20 entry is not marked fetched")
    if not str(dgs_entry.get("url", "")).startswith("https://fred.stlouisfed.org/"):
        raise EvidenceError("FRED manifest: DGS20 source is not official FRED")
    manifest_path = Path(str(dgs_entry.get("path", "")))
    if manifest_path.name != DGS20_DATA.name or manifest_path.resolve() != DGS20_DATA.resolve():
        raise EvidenceError("FRED manifest: DGS20 path does not point to the retained run input")
    dgs_file = _verified_file(DGS20_DATA, dgs_entry.get("sha256"), "DGS20 data")
    manifest_file = {
        "path": _repo_relative(FRED_MANIFEST),
        "sha256": _sha256(FRED_MANIFEST),
        "bytes": FRED_MANIFEST.stat().st_size,
    }
    current_file = {
        "path": _repo_relative(_require_file(CURRENT_EVIDENCE, "current evidence")),
        "sha256": _sha256(CURRENT_EVIDENCE),
        "bytes": CURRENT_EVIDENCE.stat().st_size,
    }
    derived_file = {
        "path": _repo_relative(_require_file(DERIVED_EVIDENCE, "derived evidence")),
        "sha256": _sha256(DERIVED_EVIDENCE),
        "bytes": DERIVED_EVIDENCE.stat().st_size,
    }
    current_text = CURRENT_EVIDENCE.read_text(encoding="utf-8")
    required_cbo_fragments = (
        "receipts at $4,845B",
        "net interest at $1,052B",
        "preliminary fiscal-year-to-date estimates",
        "This is a ratio, not an earmarking claim.",
    )
    missing = [fragment for fragment in required_cbo_fragments if fragment not in current_text]
    if missing:
        raise EvidenceError(f"current evidence: CBO statement drifted; missing {missing!r}")
    return {
        "derived": derived,
        "manifest": manifest,
        "dgs_entry": dgs_entry,
        "treasury_file": treasury_file,
        "dgs_file": dgs_file,
        "manifest_file": manifest_file,
        "current_file": current_file,
        "derived_file": derived_file,
        "current_text": current_text,
    }


def _treasury_rows(inputs: dict[str, Any]) -> tuple[list[tuple[date, Decimal]], dict[str, Any]]:
    payload = _read_json(TREASURY_DATA, "Treasury debt data")
    rows = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or not rows:
        raise EvidenceError("Treasury debt data: data must be a non-empty array")
    meta = payload.get("meta") if isinstance(payload, dict) else None
    expected_count = _number(meta.get("total-count"), "Treasury metadata total-count") if isinstance(meta, dict) else None
    if expected_count is None or expected_count != len(rows):
        raise EvidenceError(f"Treasury debt data: metadata count {expected_count} != {len(rows)} rows")

    out: list[tuple[date, Decimal]] = []
    previous: date | None = None
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise EvidenceError(f"Treasury debt data: row {index} is not an object")
        raw_day = str(row.get("record_date", ""))
        try:
            day = date.fromisoformat(raw_day)
        except ValueError as exc:
            raise EvidenceError(f"Treasury debt data: invalid record_date {raw_day!r}") from exc
        if previous is not None and day <= previous:
            raise EvidenceError(f"Treasury debt data: dates are not strictly increasing at {raw_day}")
        previous = day
        if not TREASURY_START <= day <= TREASURY_END:
            raise EvidenceError(f"Treasury debt data: row {raw_day} is outside the requested window")
        value = _number(row.get("tot_pub_debt_out_amt"), f"Treasury total public debt row {raw_day}")
        out.append((day, value))

    derived_treasury = inputs["derived"]["treasury"]
    latest = derived_treasury.get("latest") or {}
    if out[-1][0].isoformat() != latest.get("record_date"):
        raise EvidenceError("Treasury debt data: latest date disagrees with derived-evidence.json")
    if out[-1][1] != _number(latest.get("tot_pub_debt_out_amt"), "derived treasury latest"):
        raise EvidenceError("Treasury debt data: latest gross debt disagrees with derived-evidence.json")

    crossings: dict[str, str] = {}
    for threshold in (Decimal("38"), Decimal("39"), Decimal("40")):
        threshold_dollars = threshold * Decimal(10) ** 12
        crossings[str(int(threshold))] = next(day.isoformat() for day, value in out if value >= threshold_dollars)
    if crossings != derived_treasury.get("first_crossings_in_window"):
        raise EvidenceError(f"Treasury debt data: crossing dates disagree ({crossings!r})")
    days_39_to_40 = (date.fromisoformat(crossings["40"]) - date.fromisoformat(crossings["39"])).days
    if days_39_to_40 != derived_treasury.get("days_39_to_40"):
        raise EvidenceError("Treasury debt data: crossing interval disagrees with derived-evidence.json")
    return out, {"crossings": crossings, "days_39_to_40": days_39_to_40}


def _build_treasury_object(inputs: dict[str, Any]) -> dict[str, Any]:
    rows, derived_facts = _treasury_rows(inputs)
    values = [value / (Decimal(10) ** 12) for _, value in rows]
    min_domain = int(min(values).to_integral_value(rounding="ROUND_FLOOR"))
    max_domain = int((max(values) + Decimal("0.5")).to_integral_value(rounding="ROUND_CEILING"))
    points = [[_decimal_year(day), float(value)] for (day, _), value in zip(rows, values)]
    first_day, latest_day = rows[0][0], rows[-1][0]
    latest_value = values[-1]
    source = inputs["treasury_file"]
    derived_source = inputs["derived_file"]
    return {
        "title": "THE DEBT HAS TO BE REFINANCED",
        "sub": "Gross federal debt · Jan 2025 → Sep 17, 2026 · daily Treasury records · USD trillions",
        "src": "U.S. Treasury · Debt to the Penny API · total public debt outstanding",
        "src_style": "compact",
        "unit": "USD trillions",
        "ylabel": "USD trillions",
        "domain": [min_domain, max_domain],
        "xticks": _date_ticks(first_day, latest_day),
        "series": [{"name": "Gross debt", "color": "crimson", "pts": points}],
        "status": "REAL",
        "no_interpolation": True,
        "selection": "Every returned Treasury record in the requested window; total public debt outstanding divided by 1,000,000,000,000; no interpolation or counter extrapolation",
        "facts": {
            "series": "tot_pub_debt_out_amt",
            "source_units": "USD",
            "display_units": "USD trillions",
            "window_start": TREASURY_START.isoformat(),
            "window_end": TREASURY_END.isoformat(),
            "first_observation_date": first_day.isoformat(),
            "last_observation_date": latest_day.isoformat(),
            "observations": len(rows),
            "latest_date": latest_day.isoformat(),
            "latest_value_usd_trillions": float(latest_value),
            "first_crossings_in_window": derived_facts["crossings"],
            "days_39_to_40": derived_facts["days_39_to_40"],
            "date_encoding": "decimal year derived from each record_date",
        },
        "proof": [
            {
                "kind": "primary_source",
                "publisher": "U.S. Treasury",
                "url": inputs["derived"]["treasury"]["url"],
                "path": source["path"],
                "sha256": source["sha256"],
                "rows": len(rows),
                "window": {"start": TREASURY_START.isoformat(), "end": TREASURY_END.isoformat()},
            },
            {
                "kind": "derivation_manifest",
                "path": derived_source["path"],
                "sha256": derived_source["sha256"],
                "field": "treasury.sha256",
            },
        ],
        "notes": [
            "Gross federal debt uses Treasury total public debt outstanding; it is not debt held by the public.",
            "The chart shows the returned daily records and does not extrapolate a constant trillion-dollar pace.",
        ],
    }


def _cbo_values(current_text: str) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    match = re.search(
        r"receipts at \$([0-9,]+)B, outlays at \$([0-9,]+)B, deficit at \$([0-9,]+)B, and net interest at \$([0-9,]+)B",
        current_text,
    )
    if not match:
        raise EvidenceError("current evidence: cannot parse the CBO October-August values")
    return tuple(_number(token.replace(",", ""), "CBO value") for token in match.groups())  # type: ignore[return-value]


def _build_interest_object(inputs: dict[str, Any]) -> dict[str, Any]:
    revenue, outlays, deficit, net_interest = _cbo_values(inputs["current_text"])
    ratio = net_interest / revenue
    ratio_percent = (ratio * Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    cents = int((ratio * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    snapshot = inputs["current_file"]
    return {
        "title": "NET INTEREST IS 21.71% OF REVENUE",
        "sub": "FY2026 October–August · preliminary CBO estimates · USD billions · ratio, not an earmark",
        "src": "Congressional Budget Office · Monthly Budget Review, September 9, 2026 · Tables 1 and 3",
        "src_style": "compact",
        "unit": "USD billions",
        "ylabel": "USD billions",
        "from_zero": True,
        "domain": [0, 5200],
        "left_gutter": 200,
        "bars": [
            {"label": "Federal revenue", "value": int(revenue), "color": "cobalt"},
            {"label": "Net interest", "value": int(net_interest), "color": "crimson"},
        ],
        "badges": [
            {"label": "SHARE OF REVENUE", "value": f"{ratio_percent}%", "tag": f"about {cents}¢ / $1", "accent": "crimson"}
        ],
        "status": "DERIVED",
        "facts": {
            "budget_window": "FY2026 October–August",
            "preliminary": True,
            "revenue_usd_billions": int(revenue),
            "outlays_usd_billions": int(outlays),
            "deficit_usd_billions": int(deficit),
            "net_interest_usd_billions": int(net_interest),
            "ratio_fraction": float(ratio),
            "ratio_percent": float(ratio_percent),
            "plain_language": f"About {cents} cents of every federal revenue dollar went to net interest through August.",
            "denominator": "federal revenue",
            "interpretation": "This is a ratio, not an earmarking claim.",
        },
        "proof": [
            {
                "kind": "evidence_snapshot",
                "publisher": "Current American Debt Trap evidence packet",
                "path": snapshot["path"],
                "sha256": snapshot["sha256"],
                "locator": "Federal budget evidence; CBO September 9 review and PDF Tables 1 and 3",
                "url": "https://www.cbo.gov/system/files/2026-09/61984-MBR.pdf",
                "values": {"revenue_usd_billions": int(revenue), "net_interest_usd_billions": int(net_interest)},
            }
        ],
        "notes": [
            "Revenue is the denominator: 1,052 / 4,845 = 21.71%, expressed as about 22 cents per revenue dollar.",
            "These are preliminary fiscal-year-to-date estimates, not a completed annual total.",
            "The ratio is not an earmarking claim; it compares net interest with total federal revenue.",
        ],
    }


def _fred_rows(inputs: dict[str, Any]) -> tuple[list[tuple[date, Decimal]], int]:
    expected_numeric = inputs["dgs_entry"].get("observations")
    try:
        expected_numeric = int(expected_numeric)
    except (TypeError, ValueError) as exc:
        raise EvidenceError("FRED manifest: DGS20 observations is not an integer") from exc
    rows: list[tuple[date, Decimal]] = []
    numeric_total = 0
    previous: date | None = None
    try:
        handle = DGS20_DATA.open(newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise EvidenceError(f"DGS20 data: cannot open CSV: {exc}") from exc
    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["observation_date", "DGS20"]:
            raise EvidenceError(f"DGS20 data: expected columns observation_date,DGS20, got {reader.fieldnames!r}")
        for index, row in enumerate(reader, start=2):
            raw_day = (row.get("observation_date") or "").strip()
            try:
                day = date.fromisoformat(raw_day)
            except ValueError as exc:
                raise EvidenceError(f"DGS20 data: invalid date at CSV row {index}: {raw_day!r}") from exc
            if previous is not None and day <= previous:
                raise EvidenceError(f"DGS20 data: dates are not strictly increasing at {raw_day}")
            previous = day
            raw_value = (row.get("DGS20") or "").strip()
            if not raw_value or raw_value == ".":
                continue
            value = _number(raw_value, f"DGS20 value on {raw_day}")
            numeric_total += 1
            if DGS20_START <= day <= DGS20_END:
                rows.append((day, value))
    if numeric_total != expected_numeric:
        raise EvidenceError(f"DGS20 data: {numeric_total} numeric rows != manifest {expected_numeric}")
    if not rows:
        raise EvidenceError("DGS20 data: no numeric observations in requested window")
    manifest_latest = inputs["dgs_entry"].get("latest") or {}
    if rows[-1][0].isoformat() != manifest_latest.get("observation_date"):
        raise EvidenceError("DGS20 data: latest date disagrees with FRED manifest")
    if rows[-1][1] != _number(manifest_latest.get("DGS20"), "FRED manifest DGS20 latest"):
        raise EvidenceError("DGS20 data: latest value disagrees with FRED manifest")
    return rows, numeric_total


def _build_dgs20_object(inputs: dict[str, Any]) -> dict[str, Any]:
    rows, numeric_total = _fred_rows(inputs)
    values = [value for _, value in rows]
    min_domain = int(min(values).to_integral_value(rounding="ROUND_FLOOR"))
    max_domain = int((max(values) + Decimal("0.5")).to_integral_value(rounding="ROUND_CEILING"))
    first_day, latest_day = rows[0][0], rows[-1][0]
    latest_value = values[-1]
    source = inputs["dgs_file"]
    manifest = inputs["manifest_file"]
    entry = inputs["dgs_entry"]
    return {
        "title": "TWENTY YEARS COSTS MORE THAN FIVE PERCENT",
        "sub": "20-year U.S. Treasury constant-maturity yield · Jan 2025 → Sep 17, 2026 · daily · percent per annum",
        "src": "FRED DGS20 · U.S. Treasury constant maturity yield",
        "src_style": "compact",
        "unit": "%",
        "ylabel": "Percent per annum",
        "domain": [min_domain, max_domain],
        "xticks": _date_ticks(first_day, latest_day),
        "series": [{"name": "20Y Treasury", "color": "amber", "pts": [[_decimal_year(day), float(value)] for day, value in rows]}],
        "badges": [{"label": "LATEST", "value": f"{latest_value:.2f}%", "tag": latest_day.strftime("%b %d, %Y"), "accent": "amber"}],
        "status": "REAL",
        "no_interpolation": True,
        "selection": "Numeric DGS20 observations in the requested window; blank FRED rows remain absent; no interpolation or decimation",
        "facts": {
            "series": "DGS20",
            "source_units": "percent per annum",
            "window_start": DGS20_START.isoformat(),
            "window_end": DGS20_END.isoformat(),
            "first_observation_date": first_day.isoformat(),
            "last_observation_date": latest_day.isoformat(),
            "observations": len(rows),
            "numeric_rows_in_source": numeric_total,
            "latest_date": latest_day.isoformat(),
            "latest_value_percent": float(latest_value),
            "date_encoding": "decimal year derived from each observation_date",
        },
        "proof": [
            {
                "kind": "primary_source",
                "publisher": "Federal Reserve Bank of St. Louis FRED",
                "series": "DGS20",
                "url": entry["url"],
                "retrieved_at": entry.get("retrieved_at"),
                "path": source["path"],
                "sha256": source["sha256"],
                "rows": len(rows),
                "window": {"start": DGS20_START.isoformat(), "end": DGS20_END.isoformat()},
            },
            {
                "kind": "manifest",
                "path": manifest["path"],
                "sha256": manifest["sha256"],
                "entry_sha256": entry["sha256"],
            },
        ],
        "notes": [
            "The latest returned observation is Sep 17, 2026 at 5.32%; this is not a Sep 20 trading quote.",
            "Blank FRED observations are retained as absent rather than interpolated.",
        ],
    }


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _run_ledger_checks(output_dir: Path) -> list[dict[str, Any]]:
    ledger = REPO_ROOT / "content" / "video_engine" / "scripts" / "ledger_page.py"
    checks: list[dict[str, Any]] = []
    for name, variant in zip(OBJECT_NAMES, ("line", "bars", "line")):
        path = output_dir / name
        command = [sys.executable, str(ledger), str(path), "--variant", variant, "--check"]
        result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise EvidenceError(f"ledger_page check failed for {name}: {detail}")
        checks.append({"path": _repo_relative(path), "variant": variant, "status": "PASS"})
    return checks


def _build_objects(inputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        OBJECT_NAMES[0]: _build_treasury_object(inputs),
        OBJECT_NAMES[1]: _build_interest_object(inputs),
        OBJECT_NAMES[2]: _build_dgs20_object(inputs),
    }


def _receipt(inputs: dict[str, Any], objects: dict[str, dict[str, Any]], checks: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    output_rows = []
    for name in OBJECT_NAMES:
        path = output_dir / name
        output_rows.append({
            "path": _repo_relative(path),
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
            "status": "REAL" if objects[name].get("status") == "REAL" else "DERIVED",
        })
    return {
        "schema_version": "american_debt_trap_evidence_receipt.v1",
        "episode_id": "american-debt-trap",
        "snapshot_date": "2026-09-20",
        "builder": _repo_relative(Path(__file__)),
        "inputs": {
            "current_evidence": inputs["current_file"],
            "treasury_data": inputs["treasury_file"],
            "derived_evidence": inputs["derived_file"],
            "dgs20_data": inputs["dgs_file"],
            "fred_manifest": inputs["manifest_file"],
        },
        "source_verification": {
            "treasury": {
                "source_path": inputs["treasury_file"]["path"],
                "expected_sha256": inputs["treasury_file"]["expected_sha256"],
                "actual_sha256": inputs["treasury_file"]["sha256"],
                "manifest_binding": "derived-evidence.json treasury.sha256",
                "status": "PASS",
            },
            "dgs20": {
                "source_path": inputs["dgs_file"]["path"],
                "expected_sha256": inputs["dgs_file"]["expected_sha256"],
                "actual_sha256": inputs["dgs_file"]["sha256"],
                "manifest_binding": "fred-manifest.json series=DGS20 sha256",
                "status": "PASS",
            },
        },
        "outputs": output_rows,
        "ledger_page_checks": checks,
        "source_gaps": [
            "The cited CBO September 9 HTML/PDF is not retained as local hash-bound source bytes in this run; the CBO values are taken only from the dated current evidence snapshot, whose path and SHA-256 are recorded above.",
            "No missing Treasury or DGS20 source bytes were found after manifest verification.",
        ],
        "scope_notes": [
            "The CBO comparison is a ratio of preliminary FY2026 October–August estimates; the denominator is total federal revenue, not an earmark.",
            "All line points retain the source observation window and omit blank observations without interpolation.",
        ],
    }


def build(output_dir: Path = OBJECTS_ROOT, *, write: bool = True) -> dict[str, Any]:
    inputs = _load_verified_inputs()
    objects = _build_objects(inputs)
    output_dir = Path(output_dir).resolve()
    if not write:
        return {"objects": objects, "inputs": inputs}
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, obj in objects.items():
        (output_dir / name).write_bytes(_json_bytes(obj))
    checks = _run_ledger_checks(output_dir)
    receipt = _receipt(inputs, objects, checks, output_dir)
    RECEIPT_PATH.write_bytes(_json_bytes(receipt))
    return {"objects": objects, "inputs": inputs, "checks": checks, "receipt": receipt}


def check(output_dir: Path = OBJECTS_ROOT) -> dict[str, Any]:
    expected = build(output_dir, write=False)
    output_dir = Path(output_dir).resolve()
    for name, expected_obj in expected["objects"].items():
        path = _require_file(output_dir / name, name)
        actual_obj = _read_json(path, name)
        if actual_obj != expected_obj:
            raise EvidenceError(f"{name}: existing object differs from deterministic builder output")
    checks = _run_ledger_checks(output_dir)
    receipt = _read_json(RECEIPT_PATH, "evidence receipt")
    if not isinstance(receipt, dict) or receipt.get("schema_version") != "american_debt_trap_evidence_receipt.v1":
        raise EvidenceError("evidence receipt: schema mismatch")
    return {"checks": checks, "receipt": receipt}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build hash-bound American Debt Trap native ledger objects.")
    parser.add_argument("--output-dir", type=Path, default=OBJECTS_ROOT, help="series.json destination")
    parser.add_argument("--check", action="store_true", help="verify existing deterministic objects without writing")
    args = parser.parse_args(argv)
    try:
        result = check(args.output_dir) if args.check else build(args.output_dir)
    except (EvidenceError, OSError) as exc:
        print(f"american debt trap evidence: BLOCKED: {exc}", file=sys.stderr)
        return 2
    names = ", ".join(OBJECT_NAMES)
    action = "checked" if args.check else "wrote"
    print(f"american debt trap evidence: {action} {names}; ledger checks PASS")
    if not args.check:
        print(f"receipt: {_repo_relative(RECEIPT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
