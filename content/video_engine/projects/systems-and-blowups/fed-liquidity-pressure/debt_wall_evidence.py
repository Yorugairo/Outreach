"""Build the retained-source corporate debt-wall evidence object.

This is an evidence-prep builder, not an episode or renderer builder.  It
reads the episode-local byte copy of the retained S&P Global Ratings HTML,
checks its expected SHA-256, extracts the ``Total United States`` row from
the ``Global Maturity Schedule`` table, and emits the ordinary series shape
consumed by the existing ledger-page engine.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


EPISODE_ROOT = Path(__file__).resolve().parent
SOURCE_RELATIVE_PATH = "evidence/sources/sp_global_corporate_maturities_2025_snapshot.html"
SOURCE_URL = "https://investorfactbook.spglobal.com/sp-global-ratings/global-corporate-debt-maturities-through-2029/"
SOURCE_SHA256 = "43c79cc86247923cdc7b5de7986b5ceb1e81471b9fe4fc3a578921fe700b0993"
OBJECT_NAME = "debt-wall-2025-2027.series.json"
DERIVED_NAME = "debt-wall-2025-2027.json"
YEARS = (2025, 2026, 2027)
EXPECTED_VALUES = {2025: 816, 2026: 1167, 2027: 1201}
EXPECTED_TOTAL = sum(EXPECTED_VALUES.values())
SNAPSHOT_DATE = "2025-01-01"
INCLUDED_INSTRUMENTS = ("bonds", "loans", "revolving credit facilities")
CHART_VALUE_UNIT = " bn"  # ledger painter appends this token directly to value_strings
CHART_YLABEL = "USD billions"  # full basis belongs on the axis, not after each value
CHART_LEFT_GUTTER = 200  # measured recast retains the host page's larger axis face


class EvidenceError(RuntimeError):
    """Raised when the retained source or its declared extraction drifts."""


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file without changing it."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _episode_path(root: Path, relative: str, label: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise EvidenceError(f"{label}: missing relative path")
    candidate = Path(relative)
    if candidate.is_absolute():
        raise EvidenceError(f"{label}: path must be episode-relative")
    root = root.resolve()
    path = (root / candidate).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise EvidenceError(f"{label}: path escapes episode root") from exc
    return path


def verify_source(root: Path = EPISODE_ROOT, expected_sha256: str = SOURCE_SHA256) -> Path:
    """Resolve and hash-check the episode-local retained source copy."""
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
        raise EvidenceError("source: expected SHA-256 is invalid")
    path = _episode_path(Path(root), SOURCE_RELATIVE_PATH, "source")
    if not path.is_file():
        raise EvidenceError(f"source: file missing: {SOURCE_RELATIVE_PATH}")
    actual = sha256(path)
    if actual.lower() != expected_sha256.lower():
        raise EvidenceError(f"source: SHA-256 mismatch (expected {expected_sha256}, got {actual})")
    return path


class _TableParser(HTMLParser):
    """Collect plain-text rows from each HTML table, including nested ``p`` tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self._table_depth = 0
        self._rows: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._cell_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag == "table":
            if self._table_depth == 0:
                self._rows = []
            self._table_depth += 1
            return
        if not self._table_depth:
            return
        if self._cell is not None:
            self._cell_depth += 1
        elif tag == "tr":
            self._row = []
        elif tag in ("th", "td") and self._row is not None:
            self._cell = []
            self._cell_depth = 1

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._table_depth:
            return
        if self._cell is not None:
            self._cell_depth -= 1
            if self._cell_depth == 0:
                if self._row is not None:
                    self._row.append(" ".join("".join(self._cell).split()))
                self._cell = None
            return
        if tag == "tr":
            if self._row and self._rows is not None:
                self._rows.append(self._row)
            self._row = None
        elif tag == "table":
            self._table_depth -= 1
            if self._table_depth == 0 and self._rows is not None:
                self.tables.append(self._rows)
                self._rows = None


class _TextParser(HTMLParser):
    """Collect visible text for source-footnote checks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _normalise(value: str) -> str:
    return " ".join(value.split())


def _integer(value: str, label: str) -> int:
    token = value.replace("$", "").replace(",", "").replace("−", "-").strip()
    try:
        number = Decimal(token)
    except InvalidOperation as exc:
        raise EvidenceError(f"{label}: non-numeric source value {value!r}") from exc
    if not number.is_finite() or number != number.to_integral_value():
        raise EvidenceError(f"{label}: expected a finite whole USD-billion value, got {value!r}")
    return int(number)


def _extract_total_us_rows(source_path: Path) -> tuple[dict[int, int], int]:
    try:
        html = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise EvidenceError(f"source: cannot read HTML: {exc}") from exc

    table_parser = _TableParser()
    try:
        table_parser.feed(html)
        table_parser.close()
    except (ValueError, AssertionError) as exc:
        raise EvidenceError(f"source: malformed HTML table: {exc}") from exc

    candidates: list[tuple[dict[int, int], int]] = []
    expected_header = {str(year) for year in (2025, 2026, 2027, 2028, 2029)} | {"Total"}
    for rows in table_parser.tables:
        header_index = next(
            (
                index
                for index, row in enumerate(rows)
                if expected_header.issubset(set(row))
            ),
            None,
        )
        if header_index is None:
            continue
        header = rows[header_index]
        columns = {str(year): header.index(str(year)) for year in (2025, 2026, 2027)}
        total_index = header.index("Total")
        for row in rows[header_index + 1 :]:
            if not row or _normalise(row[0]).casefold() != "total united states":
                continue
            if max(*columns.values(), total_index) >= len(row):
                raise EvidenceError("source: Total United States row is shorter than its declared header")
            values = {
                year: _integer(row[index], f"source Total United States {year}")
                for year, index in ((year, columns[str(year)]) for year in YEARS)
            }
            row_total = _integer(row[total_index], "source Total United States total")
            candidates.append((values, row_total))

    if not candidates:
        raise EvidenceError("source: Global Maturity Schedule Total United States row not found")
    unique = {(tuple(values.items()), total) for values, total in candidates}
    if len(unique) != 1:
        raise EvidenceError(f"source: duplicate Total United States rows disagree: {sorted(unique)!r}")
    values, row_total = candidates[0]
    if values != EXPECTED_VALUES:
        raise EvidenceError(f"source: 2025–2027 values changed: {values!r}")
    if sum(values.values()) != EXPECTED_TOTAL:
        raise EvidenceError(f"source: selected-year sum changed: {sum(values.values())}")
    return values, row_total


def _verify_source_footnotes(source_path: Path) -> None:
    try:
        html = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise EvidenceError(f"source: cannot read HTML: {exc}") from exc
    parser = _TextParser()
    parser.feed(html)
    visible = _normalise(" ".join(parser.parts)).casefold()
    required = (
        "data as of january 1, 2025",
        "includes bonds, loans, and revolving credit facilities that are rated by s&p global ratings",
    )
    for phrase in required:
        if phrase not in visible:
            raise EvidenceError(f"source: required provenance text missing: {phrase!r}")
    if SOURCE_URL not in html:
        raise EvidenceError("source: canonical S&P URL missing")


def derive(root: Path = EPISODE_ROOT, expected_source_sha256: str = SOURCE_SHA256) -> dict[str, Any]:
    """Return deterministic derivation metadata after verifying the retained source."""
    root = Path(root).resolve()
    source_path = verify_source(root, expected_source_sha256)
    _verify_source_footnotes(source_path)
    values, _full_row_total = _extract_total_us_rows(source_path)
    return {
        "schema": "mp-fed-liquidity.debt-wall-derivation.v1",
        "series_id": "debt-wall-2025-2027",
        "source": {
            "publisher": "S&P Global Ratings",
            "url": SOURCE_URL,
            "path": SOURCE_RELATIVE_PATH,
            "sha256": sha256(source_path),
            "table": "Global Maturity Schedule",
            "row": "Total United States",
            "units": "USD billions",
            "snapshot_date": SNAPSHOT_DATE,
        },
        "selection": {
            "years": list(YEARS),
            "columns": [str(year) for year in YEARS],
            "geography": "United States",
            "issuer_scope": "financial and nonfinancial corporate issuers",
            "included_instruments": list(INCLUDED_INSTRUMENTS),
            "rating_scope": "rated by S&P Global Ratings",
        },
        "rows": [
            {"year": year, "value_usd_billions": values[year]}
            for year in YEARS
        ],
        "selected_year_total_usd_billions": EXPECTED_TOTAL,
        "derivation": {
            "formula": "816 + 1167 + 1201",
            "operation": "sum selected Total United States row values for 2025–2027",
            "rounding": "none; source values are whole USD billions",
            "excluded_years": [2028, 2029],
        },
        "claim_boundary": (
            "This is a January 1, 2025 maturity-schedule snapshot for S&P-rated debt; "
            "it is not a claim that the full amount remained due in September 2026."
        ),
    }


def series_from_derivation(derivation: dict[str, Any]) -> dict[str, Any]:
    """Build the existing ledger-page story-bars shape from verified derivation data."""
    rows = derivation.get("rows")
    if not isinstance(rows, list) or [row.get("year") for row in rows if isinstance(row, dict)] != list(YEARS):
        raise EvidenceError("derivation: rows must contain 2025, 2026, 2027 in order")
    source = derivation.get("source")
    if not isinstance(source, dict):
        raise EvidenceError("derivation: source provenance is missing")
    values = [row.get("value_usd_billions") for row in rows]
    if values != [EXPECTED_VALUES[year] for year in YEARS]:
        raise EvidenceError(f"derivation: unexpected selected values: {values!r}")
    proof = {
        "kind": "primary_source",
        "publisher": source["publisher"],
        "url": source["url"],
        "path": source["path"],
        "sha256": source["sha256"],
        "table": source["table"],
        "row": source["row"],
        "columns": [str(year) for year in YEARS],
        "snapshot_date": source["snapshot_date"],
        "units": source["units"],
    }
    return {
        "title": "THE CORPORATE DEBT WALL",
        "sub": "U.S. maturities · 2025–2027 · Jan 2025 snapshot · USD billions",
        "src": "S&P Global Ratings · S&P-rated corporate debt",
        "src_style": "compact",
        "unit": CHART_VALUE_UNIT,
        "ylabel": CHART_YLABEL,
        "left_gutter": CHART_LEFT_GUTTER,
        "from_zero": True,
        "domain": [0, 1400],
        "xticks": [[year, str(year)] for year in YEARS],
        "bars": [
            {"label": str(row["year"]), "value": row["value_usd_billions"], "color": "cobalt"}
            for row in rows
        ],
        "status": "REAL",
        "facts": {
            "geography": "United States",
            "issuer_scope": "financial and nonfinancial corporate issuers",
            "included_instruments": list(INCLUDED_INSTRUMENTS),
            "rating_scope": "rated by S&P Global Ratings",
            "snapshot_date": SNAPSHOT_DATE,
            "window_start": "2025",
            "window_end": "2027",
            "maturities_usd_billions": EXPECTED_TOTAL,
            "not_current_as_of": "2026-09-19",
        },
        "proof": [proof],
        "derivation": derivation["derivation"],
        "notes": [
            "Values are the source table's Total United States row; financial and nonfinancial issuers are combined.",
            "The source includes S&P-rated bonds, loans, and revolving credit facilities.",
            "January 1, 2025 snapshot; do not present the full schedule as still due in September 2026.",
            "Native ledger bars are vertical story bars; value labels use the compact bn suffix while the axis states USD billions.",
        ],
    }


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build_objects(
    root: Path = EPISODE_ROOT,
    output_dir: Path | None = None,
    expected_source_sha256: str = SOURCE_SHA256,
) -> dict[str, dict[str, Any]]:
    """Verify inputs and emit the derived sidecar plus one ledger series object."""
    root = Path(root).resolve()
    derivation = derive(root, expected_source_sha256)
    series = series_from_derivation(derivation)
    object_dir = Path(output_dir).resolve() if output_dir is not None else root / "evidence" / "objects"
    derived_dir = object_dir.parent / "derived"
    object_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)
    (derived_dir / DERIVED_NAME).write_bytes(_json_bytes(derivation))
    (object_dir / OBJECT_NAME).write_bytes(_json_bytes(series))
    return {OBJECT_NAME: series}


def build_evidence(
    root: Path = EPISODE_ROOT,
    output_dir: Path | None = None,
    expected_source_sha256: str = SOURCE_SHA256,
) -> dict[str, dict[str, Any]]:
    """Named entry point for evidence-prep callers; equivalent to ``build_objects``."""
    return build_objects(root, output_dir, expected_source_sha256)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the hash-bound corporate debt-wall ledger object.")
    parser.add_argument("--project-root", type=Path, default=EPISODE_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--output-dir", type=Path, default=None, help="object output directory")
    parser.add_argument("--expected-sha256", default=SOURCE_SHA256, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        build_objects(args.project_root, args.output_dir, args.expected_sha256)
    except (EvidenceError, OSError) as exc:
        print(f"debt wall evidence: BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(f"debt wall evidence: PASS ({OBJECT_NAME}; {EXPECTED_TOTAL} USD billions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
