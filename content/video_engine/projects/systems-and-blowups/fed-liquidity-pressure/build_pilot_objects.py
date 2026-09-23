"""Build the two source-bound Fed pilot evidence objects.

The builder is intentionally narrower than episode assembly: it reads the
retained, hash-bound episode sources and emits ordinary ``series.json``
objects accepted by ``ledger_page.py``.  It never fetches, interpolates,
decimates, invents endpoints, or invokes the timeline compiler.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any


EPISODE_ROOT = Path(__file__).resolve().parent
OBJECT_NAMES = (
    "fed-assets-reserves-change.series.json",
    "fed-on-rrp-history.series.json",
)
RRP_START = date(2022, 1, 1)
RRP_END = date(2026, 9, 18)
MPR_START = "2022-06-01"
MPR_END = "2025-06-11"
RRP_SERIES = "RRPONTSYD"


class EvidenceError(RuntimeError):
    """Raised when a source-bound input cannot be safely emitted."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _episode_path(root: Path, raw: Any, label: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise EvidenceError(f"{label}: missing relative path")
    supplied = Path(raw)
    if supplied.is_absolute():
        raise EvidenceError(f"{label}: path must be episode-relative")
    root = root.resolve()
    path = (root / supplied).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise EvidenceError(f"{label}: path escapes episode root") from exc
    return path


def _read_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"{label}: cannot read JSON: {exc}") from exc


def _hash_ref(root: Path, raw_path: Any, expected: Any, label: str) -> Path:
    path = _episode_path(root, raw_path, label)
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        raise EvidenceError(f"{label}: invalid SHA-256")
    if not path.is_file():
        raise EvidenceError(f"{label}: file missing: {raw_path}")
    actual = _sha256(path)
    if actual.lower() != expected.lower():
        raise EvidenceError(f"{label}: SHA-256 mismatch (expected {expected}, got {actual})")
    return path


def _verify_claim_hashes(root: Path, value: Any, label: str = "claims") -> None:
    """Verify every direct path/hash binding in claims.v1 before emission."""
    if isinstance(value, dict):
        if "path" in value or "sha256" in value:
            if "path" not in value or "sha256" not in value:
                raise EvidenceError(f"{label}: path and sha256 must be paired")
            _hash_ref(root, value["path"], value["sha256"], f"{label}.path")
        if "metadata_path" in value or "metadata_sha256" in value:
            if "metadata_path" not in value or "metadata_sha256" not in value:
                raise EvidenceError(f"{label}: metadata_path and metadata_sha256 must be paired")
            _hash_ref(root, value["metadata_path"], value["metadata_sha256"], f"{label}.metadata_path")
        for key, child in value.items():
            _verify_claim_hashes(root, child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _verify_claim_hashes(root, child, f"{label}[{index}]")


def _claim_by_id(claims: dict[str, Any], claim_id: str) -> dict[str, Any]:
    rows = claims.get("claims")
    if not isinstance(rows, list):
        raise EvidenceError("claims manifest: claims must be an array")
    for row in rows:
        if isinstance(row, dict) and row.get("id") == claim_id:
            return row
    raise EvidenceError(f"claims manifest: missing {claim_id}")


def _load_verified_inputs(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    claims_path = root / "claims.v1.json"
    claims = _read_json(claims_path, "claims manifest")
    if not isinstance(claims, dict) or claims.get("schema") != "mp-fed-liquidity.claims.v1":
        raise EvidenceError("claims manifest: schema must be mp-fed-liquidity.claims.v1")
    _verify_claim_hashes(root, claims)

    c1 = _claim_by_id(claims, "C1-C2")
    c3 = _claim_by_id(claims, "C3")
    c5 = _claim_by_id(claims, "C5-funding-data")
    if c1.get("units") != "USD billions" or c1.get("cutoff") != "2026-09-18":
        raise EvidenceError("C1-C2: expected USD billions with cutoff 2026-09-18")
    if c3.get("units") != "USD billions" or c3.get("window") != {"start": MPR_START, "end": MPR_END}:
        raise EvidenceError("C3: expected USD billions window 2022-06-01 through 2025-06-11")

    c1_source = c1.get("source")
    c3_source = c3.get("source")
    c5_source = c5.get("source")
    if not isinstance(c1_source, dict) or not isinstance(c3_source, dict) or not isinstance(c5_source, dict):
        raise EvidenceError("claims manifest: C1-C2, C3, and C5 sources must be objects")
    rrp_source = _hash_ref(root, c1_source.get("path"), c1_source.get("sha256"), "C1-C2 source")
    rrp_meta = _hash_ref(root, c1_source.get("metadata_path"), c1_source.get("metadata_sha256"), "C1-C2 metadata")
    mpr_source = _hash_ref(root, c3_source.get("path"), c3_source.get("sha256"), "C3 source")
    extraction_path = _hash_ref(root, c5_source.get("path"), c5_source.get("sha256"), "C5 extraction metadata")

    metadata = _read_json(extraction_path, "extraction metadata")
    if not isinstance(metadata, dict) or metadata.get("schema") != "mp-fed-liquidity.extraction.v1":
        raise EvidenceError("extraction metadata: schema must be mp-fed-liquidity.extraction.v1")
    rrp_meta_info = metadata.get("rrp")
    if not isinstance(rrp_meta_info, dict):
        raise EvidenceError("extraction metadata: rrp block is missing")
    if rrp_meta_info.get("series") != RRP_SERIES or rrp_meta_info.get("units") != "USD billions":
        raise EvidenceError("extraction metadata: RRP series or units mismatch")
    if rrp_meta_info.get("window") != {"start": "2022-01-01", "end": "2026-09-18"}:
        raise EvidenceError("extraction metadata: RRP window mismatch")
    if rrp_meta_info.get("interpolation") is not False or rrp_meta_info.get("duplicate_dates") != 0:
        raise EvidenceError("extraction metadata: interpolation or duplicate-date contract failed")
    source_info = rrp_meta_info.get("source")
    if not isinstance(source_info, dict):
        raise EvidenceError("extraction metadata: RRP source binding is missing")
    extracted_source = _hash_ref(
        root / "evidence", source_info.get("path"), source_info.get("sha256"), "extraction RRP source"
    )
    if extracted_source != rrp_source.resolve():
        raise EvidenceError("extraction metadata: RRP source binding does not match claims/source")
    metadata_info = rrp_meta_info.get("metadata_source")
    if not isinstance(metadata_info, dict):
        raise EvidenceError("extraction metadata: RRP metadata binding is missing")
    extracted_meta = _hash_ref(
        root / "evidence", metadata_info.get("path"), metadata_info.get("sha256"), "extraction RRP metadata"
    )
    if extracted_meta != rrp_meta.resolve():
        raise EvidenceError("extraction metadata: RRP metadata binding does not match claims/source")

    if b"billion" not in rrp_meta.read_bytes().lower():
        raise EvidenceError("C1-C2 metadata: expected USD-billion unit evidence")
    return claims, {"rrp": rrp_source, "rrp_meta": rrp_meta}, {"mpr": mpr_source, "extraction": extraction_path}


class _BalanceTableParser(HTMLParser):
    """Read only the two declared Table A rows and the declared change column."""

    TARGET_ROWS = {"xsheetr13", "xsheetr15"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.labels: dict[str, str] = {}
        self.changes: dict[str, str] = {}
        self._capture: tuple[str, str, str] | None = None
        self._depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}
        if self._capture is not None:
            self._depth += 1
            return
        if tag == "th" and attrs_dict.get("id") in self.TARGET_ROWS:
            self._capture = ("label", attrs_dict["id"], tag)
            self._depth = 1
            self._parts = []
        elif tag == "td":
            headers = set(attrs_dict.get("headers", "").split())
            row = next((candidate for candidate in self.TARGET_ROWS if candidate in headers), None)
            if row and "xsheeta5" in headers:
                self._capture = ("change", row, tag)
                self._depth = 1
                self._parts = []

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._capture is None:
            return
        self._depth -= 1
        if self._depth:
            return
        kind, row, _ = self._capture
        value = " ".join("".join(self._parts).split())
        if kind == "label":
            self.labels[row] = value
        else:
            self.changes[row] = value
        self._capture = None
        self._parts = []


def _number_token(raw: str, label: str) -> int | float:
    normalized = raw.replace("−", "-").replace(",", "").strip()
    try:
        value = Decimal(normalized)
    except InvalidOperation as exc:
        raise EvidenceError(f"{label}: non-numeric source value {raw!r}") from exc
    if not value.is_finite():
        raise EvidenceError(f"{label}: non-finite source value")
    return int(value) if value == value.to_integral() else float(value)


def _build_assets_reserves(root: Path, source_path: Path, source_sha: str) -> dict[str, Any]:
    try:
        html = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise EvidenceError(f"MPR source: cannot read: {exc}") from exc
    if "June 11, 2025" not in html or "Change (since Fed's balance sheet reduction began on June 1, 2022)" not in html:
        raise EvidenceError("MPR source: expected Table A dates/column are missing")
    parser = _BalanceTableParser()
    parser.feed(html)
    expected = {"xsheetr13": ("Total assets", "crimson"), "xsheetr15": ("Reserves held by depository institutions", "teal")}
    bars: list[dict[str, Any]] = []
    for row_id, (expected_label, color) in expected.items():
        if row_id not in parser.labels or row_id not in parser.changes:
            raise EvidenceError(f"MPR source: Table A row {row_id} is missing")
        if parser.labels[row_id] != expected_label:
            raise EvidenceError(f"MPR source: row {row_id} label drifted ({parser.labels[row_id]!r})")
        bars.append({
            "label": "Total assets" if row_id == "xsheetr13" else "Reserve balances",
            "value": _number_token(parser.changes[row_id], f"MPR {row_id}"),
            "color": color,
        })
    values = {bar["label"]: bar["value"] for bar in bars}
    if values != {"Total assets": -2238, "Reserve balances": 72}:
        raise EvidenceError(f"MPR source: authored values changed ({values!r})")
    return {
        "title": "WHERE DID IT GO?",
        "sub": "Fed balance-sheet change · 01 Jun 2022 → 11 Jun 2025",
        "src": "Federal Reserve Board · Monetary Policy Report June 2025 · Table A · USD billions",
        "src_style": "compact",
        "unit": "USD billions",
        "ylabel": "USD billions",
        "from_zero": True,
        "domain": [-2238, 2238],
        "bars": bars,
        "status": "REAL",
        "facts": {
            "window_start": MPR_START,
            "window_end": MPR_END,
            "same_source": True,
            "scale": "common zero-centered USD billions",
        },
        "proof": [{
            "kind": "primary_source",
            "path": str(source_path.relative_to(root)).replace("\\", "/"),
            "sha256": source_sha,
            "table": "xtable_balancesheet",
            "column": "xsheeta5",
            "window": {"start": MPR_START, "end": MPR_END},
        }],
        "notes": ["Both deltas are direct values from the same Table A change column; no time curve is implied."],
    }


def _decimal_year(day: date) -> float:
    start = date(day.year, 1, 1)
    next_year = date(day.year + 1, 1, 1)
    return round(day.year + (day - start).days / (next_year - start).days, 10)


def _build_rrp_history(root: Path, source_path: Path, metadata_path: Path, source_sha: str, metadata_sha: str, extraction_sha: str) -> dict[str, Any]:
    try:
        with source_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != ["observation_date", RRP_SERIES]:
                raise EvidenceError(f"RRP source: expected columns observation_date,{RRP_SERIES}")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise EvidenceError(f"RRP source: cannot read CSV: {exc}") from exc
    observations: list[tuple[date, Decimal]] = []
    seen: set[date] = set()
    previous: date | None = None
    for index, row in enumerate(rows, start=2):
        raw_date = (row.get("observation_date") or "").strip()
        try:
            day = date.fromisoformat(raw_date)
        except ValueError as exc:
            raise EvidenceError(f"RRP source: invalid date at CSV row {index}: {raw_date!r}") from exc
        if previous is not None and day <= previous:
            raise EvidenceError(f"RRP source: dates are not strictly increasing at {raw_date}")
        previous = day
        if RRP_START <= day <= RRP_END:
            if day in seen:
                raise EvidenceError(f"RRP source: duplicate date {raw_date}")
            seen.add(day)
            raw_value = (row.get(RRP_SERIES) or "").strip()
            if not raw_value:
                continue
            try:
                value = Decimal(raw_value)
            except InvalidOperation as exc:
                raise EvidenceError(f"RRP source: non-numeric value on {raw_date}") from exc
            if not value.is_finite():
                raise EvidenceError(f"RRP source: non-finite value on {raw_date}")
            observations.append((day, value))
    if not observations:
        raise EvidenceError("RRP source: no numeric observations in requested window")
    if observations[-1][0] != RRP_END:
        raise EvidenceError(f"RRP source: latest numeric observation must be {RRP_END.isoformat()}")
    peak_day, peak_value = max(observations, key=lambda pair: pair[1])
    latest_day, latest_value = observations[-1]
    if peak_day != date(2022, 12, 30) or peak_value != Decimal("2553.716"):
        raise EvidenceError(f"RRP source: expected peak 2553.716 on 2022-12-30, got {peak_value} on {peak_day}")
    if latest_value != Decimal("0.576"):
        raise EvidenceError(f"RRP source: expected latest 0.576, got {latest_value}")

    pts = [[_decimal_year(day), float(value)] for day, value in observations]
    if any(not (math.isfinite(point[0]) and math.isfinite(point[1])) for point in pts):
        raise EvidenceError("RRP source: generated points contain non-finite values")
    tick_days = [observations[0][0], peak_day, latest_day]
    xticks = [[_decimal_year(day), day.strftime("%b %Y")] for day in tick_days]
    return {
        "title": "WHERE THE CASH WAS PARKED",
        "readability": "landscape-phone",
        "sub": "Daily ON RRP balance · 03 Jan 2022 → 18 Sep 2026 · USD billions",
        "src": "FRED RRPONTSYD · daily observations · USD billions",
        "src_style": "compact",
        "unit": "USD billions",
        "ylabel": "USD billions",
        "xticks": xticks,
        "series": [{"label": "ON RRP", "color": "cobalt", "pts": pts}],
        "status": "REAL",
        "no_interpolation": True,
        "selection": "numeric RRPONTSYD observations with non-empty values; no interpolation or decimation",
        "facts": {
            "series": RRP_SERIES,
            "units": "USD billions",
            "window_start": RRP_START.isoformat(),
            "window_end": RRP_END.isoformat(),
            "first_observation_date": observations[0][0].isoformat(),
            "last_observation_date": latest_day.isoformat(),
            "observations": len(observations),
            "peak_date": peak_day.isoformat(),
            "peak_value": float(peak_value),
            "latest_date": latest_day.isoformat(),
            "latest_value": float(latest_value),
            "date_encoding": "decimal year derived from each observation_date",
        },
        "proof": [
            {
                "kind": "primary_source",
                "series": RRP_SERIES,
                "path": str(source_path.relative_to(root)).replace("\\", "/"),
                "sha256": source_sha,
                "rows": len(observations),
                "window": {"start": RRP_START.isoformat(), "end": RRP_END.isoformat()},
            },
            {
                "kind": "metadata",
                "path": str(metadata_path.relative_to(root)).replace("\\", "/"),
                "sha256": metadata_sha,
                "units": "USD billions",
            },
            {
                "kind": "extraction",
                "path": "evidence/derived/extraction_metadata.json",
                "sha256": extraction_sha,
                "interpolation": False,
            },
        ],
        "notes": ["Every point is one retained numeric FRED observation; blank source rows remain absent."],
    }


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build_objects(root: Path = EPISODE_ROOT, output_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Verify inputs and return deterministic objects; write only when requested."""
    root = Path(root).resolve()
    claims, sources, other = _load_verified_inputs(root)
    c1 = _claim_by_id(claims, "C1-C2")
    c3 = _claim_by_id(claims, "C3")
    c1_source = c1["source"]
    c3_source = c3["source"]
    rrp = _build_rrp_history(
        root,
        sources["rrp"],
        sources["rrp_meta"],
        str(c1_source["sha256"]),
        str(c1_source["metadata_sha256"]),
        str(_claim_by_id(claims, "C5-funding-data")["source"]["sha256"]),
    )
    assets = _build_assets_reserves(root, other["mpr"], str(c3_source["sha256"]))
    objects = {OBJECT_NAMES[0]: assets, OBJECT_NAMES[1]: rrp}
    if output_dir is not None:
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, obj in objects.items():
            (output_dir / name).write_bytes(_json_bytes(obj))
    return objects


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit hash-bound Fed pilot series objects; no rendering or assembly.")
    parser.add_argument("--project-root", type=Path, default=EPISODE_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--output-dir", type=Path, default=None, help="output directory (default: episode/evidence/objects)")
    args = parser.parse_args(argv)
    output_dir = args.output_dir or (args.project_root / "evidence" / "objects")
    try:
        objects = build_objects(args.project_root, output_dir)
    except (EvidenceError, OSError) as exc:
        print(f"pilot objects: BLOCKED: {exc}", file=sys.stderr)
        return 2
    counts = ", ".join(f"{name}={len(obj.get('bars') or obj.get('series', [{}])[0].get('pts', []))}" for name, obj in objects.items())
    print(f"pilot objects: wrote {counts} to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
