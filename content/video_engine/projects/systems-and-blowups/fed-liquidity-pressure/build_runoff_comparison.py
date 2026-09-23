"""Build the retained-source C3 runoff-offset comparison object.

This builder reads only the episode-local June 2025 Monetary Policy Report
copy.  It verifies the retained source hash before it creates or writes an
output directory, extracts the selected Table A change rows, and emits an
ordinary native ledger ``bars`` object plus deterministic derivation metadata.
The selected rows are a comparison, not a balance-sheet reconciliation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


EPISODE_ROOT = Path(__file__).resolve().parent
SOURCE_RELATIVE_PATH = "evidence/sources/mpr_2025_06.html"
SOURCE_SHA256 = "7a201f7cad0a75ae840e93d5fc386c501e4774c31e8d1631d99dc9dc0c057da0"
SOURCE_URL = "https://www.federalreserve.gov/monetarypolicy/2025-06-mpr-part2.htm"
OBJECT_NAME = "fed-runoff-offsets.series.json"
DERIVED_NAME = "fed-runoff-offsets.json"
TABLE_ID = "xtable_balancesheet"
TABLE_TITLE = "Table A. Balance sheet comparison"
COLUMN_ID = "xsheeta5"
COLUMN_LABEL = "Change (since Fed's balance sheet reduction began on June 1, 2022)"
WINDOW = {"start": "2022-06-01", "end": "2025-06-11"}
CHART_VALUE_UNIT = " bn"  # ledger painter appends this token directly to value_strings
CHART_YLABEL = "USD billions"  # full basis belongs on the axis, not after each value
CHART_LEFT_GUTTER = 140  # reserve room for signed USD-billion y-ticks in the landscape native bars page

# The order follows the C3 claim manifest.  ``source_label`` is the literal
# row text; ``label`` is the short, viewer-facing label used by the chart.
SELECTED_ROWS: tuple[dict[str, Any], ...] = (
    {
        "row": "xsheetr13",
        "source_label": "Total assets",
        "label": "Fed assets",
        "change": -2238,
        "color": "crimson",
    },
    {
        "row": "xsheetr15",
        "source_label": "Reserves held by depository institutions",
        "label": "Reserves",
        "change": 72,
        "color": "teal",
    },
    {
        "row": "xsheetr18",
        "source_label": "Others",
        "label": "Other RRP",
        "change": -1760,
        "color": "cobalt",
    },
    {
        "row": "xsheetr19",
        "source_label": "U.S. Treasury General Account",
        "label": "TGA",
        "change": -504,
        "color": "amber",
    },
    {
        "row": "xsheetr17",
        "source_label": "Foreign official and international accounts",
        "label": "Foreign",
        "change": 106,
        "color": "sunflower",
    },
)


class EvidenceError(RuntimeError):
    """Raised when the retained source or extraction contract drifts."""


def sha256(path: Path) -> str:
    """Hash a file without changing it."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
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


def verify_source(root: Path = EPISODE_ROOT, expected_source_sha256: str = SOURCE_SHA256) -> Path:
    """Resolve and verify the retained source before any output-side effect."""
    if not isinstance(expected_source_sha256, str) or not re.fullmatch(
        r"[0-9a-fA-F]{64}", expected_source_sha256
    ):
        raise EvidenceError("source: expected SHA-256 is invalid")
    path = _episode_path(Path(root), SOURCE_RELATIVE_PATH, "source")
    if not path.is_file():
        raise EvidenceError(f"source: file missing: {SOURCE_RELATIVE_PATH}")
    actual = sha256(path)
    if actual.lower() != expected_source_sha256.lower():
        raise EvidenceError(
            f"source: SHA-256 mismatch (expected {expected_source_sha256}, got {actual})"
        )
    return path


def _load_parser() -> type:
    """Reuse the episode pilot parser while extending its declared row set."""
    try:
        import build_pilot_objects as pilot  # type: ignore
    except ModuleNotFoundError:
        sys.path.insert(0, str(EPISODE_ROOT))
        import build_pilot_objects as pilot  # type: ignore

    class ContributionTableParser(pilot._BalanceTableParser):  # type: ignore[attr-defined]
        TARGET_ROWS = {row["row"] for row in SELECTED_ROWS}

    return ContributionTableParser


def _number_token(raw: str, label: str) -> int | float:
    """Parse the source's signed billion token using the pilot's rules."""
    try:
        import build_pilot_objects as pilot  # type: ignore
    except ModuleNotFoundError:
        sys.path.insert(0, str(EPISODE_ROOT))
        import build_pilot_objects as pilot  # type: ignore
    try:
        return pilot._number_token(raw, label)  # type: ignore[attr-defined]
    except Exception as exc:  # normalize the private helper's implementation detail
        raise EvidenceError(str(exc)) from exc


def _extract_rows(source_path: Path) -> tuple[dict[str, int], dict[str, str]]:
    try:
        html = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise EvidenceError(f"source: cannot read HTML: {exc}") from exc

    required_markers = (
        f'id="{TABLE_ID}"',
        TABLE_TITLE,
        f'id="{COLUMN_ID}"',
        COLUMN_LABEL,
        "June 11, 2025",
        "Billions of dollars",
    )
    missing = [marker for marker in required_markers if marker not in html]
    if missing:
        raise EvidenceError(f"source: Table A marker missing: {missing[0]!r}")

    parser = _load_parser()()
    try:
        parser.feed(html)
        parser.close()
    except (AssertionError, ValueError) as exc:
        raise EvidenceError(f"source: malformed Table A HTML: {exc}") from exc

    values: dict[str, int] = {}
    labels: dict[str, str] = {}
    for expected in SELECTED_ROWS:
        row_id = expected["row"]
        if row_id not in parser.labels or row_id not in parser.changes:
            raise EvidenceError(f"source: Table A row {row_id} or its {COLUMN_ID} cell is missing")
        actual_label = parser.labels[row_id]
        if actual_label != expected["source_label"]:
            raise EvidenceError(
                f"source: row {row_id} label drifted ({actual_label!r}; expected {expected['source_label']!r})"
            )
        value = _number_token(parser.changes[row_id], f"source {row_id} {COLUMN_ID}")
        if type(value) is not int:
            raise EvidenceError(f"source: row {row_id} is not a whole USD-billion value: {value!r}")
        if value != expected["change"]:
            raise EvidenceError(
                f"source: row {row_id} value changed ({value!r}; expected {expected['change']!r})"
            )
        labels[row_id] = actual_label
        values[row_id] = value
    return values, labels


def derive(root: Path = EPISODE_ROOT, expected_source_sha256: str = SOURCE_SHA256) -> dict[str, Any]:
    """Return deterministic, source-bound extraction metadata."""
    root = Path(root).resolve()
    source_path = verify_source(root, expected_source_sha256)
    source_sha = sha256(source_path)
    values, labels = _extract_rows(source_path)
    rows = [
        {
            "row": row["row"],
            "source_label": labels[row["row"]],
            "label": row["label"],
            "change_usd_billions": values[row["row"]],
        }
        for row in SELECTED_ROWS
    ]
    return {
        "schema": "mp-fed-liquidity.runoff-offsets-derivation.v1",
        "series_id": "fed-runoff-offsets",
        "source": {
            "publisher": "Federal Reserve Board",
            "url": SOURCE_URL,
            "path": SOURCE_RELATIVE_PATH,
            "sha256": source_sha,
            "table": TABLE_ID,
            "table_title": TABLE_TITLE,
            "column": COLUMN_ID,
            "column_label": COLUMN_LABEL,
            "window": dict(WINDOW),
            "units": "USD billions",
        },
        "selection": {
            "rows": [row["row"] for row in SELECTED_ROWS],
            "selected_rows_not_exhaustive_reconciliation": True,
            "other_reverse_repos_row_is_not_total": True,
            "scope": "Selected Table A balance-sheet rows; not an exhaustive reconciliation.",
        },
        "rows": rows,
        "derivation": "Direct transcription of the same source-table change column; no current-balance subtraction or residual inference.",
        "claim_boundary": (
            "The xsheetr18 value is the Others row inside Reverse repurchase agreements, not total reverse repos. "
            "These selected rows share one historical window but do not sum to a balance-sheet reconciliation."
        ),
    }


def series_from_derivation(derivation: dict[str, Any]) -> dict[str, Any]:
    """Build the native zero-centred signed-bars page from verified rows."""
    source = derivation.get("source")
    rows = derivation.get("rows")
    selection = derivation.get("selection")
    if not isinstance(source, dict) or not isinstance(rows, list) or not isinstance(selection, dict):
        raise EvidenceError("derivation: source, rows, and selection are required")
    if source.get("sha256") != SOURCE_SHA256:
        raise EvidenceError("derivation: source SHA-256 does not match the retained source")
    if source.get("column") != COLUMN_ID or source.get("window") != WINDOW:
        raise EvidenceError("derivation: source column/window drifted")
    if selection.get("selected_rows_not_exhaustive_reconciliation") is not True:
        raise EvidenceError("derivation: selected-row boundary is missing")
    if selection.get("other_reverse_repos_row_is_not_total") is not True:
        raise EvidenceError("derivation: reverse-repo non-total boundary is missing")
    expected_rows = list(SELECTED_ROWS)
    if len(rows) != len(expected_rows):
        raise EvidenceError("derivation: selected row count changed")
    bars: list[dict[str, Any]] = []
    for actual, expected in zip(rows, expected_rows):
        if not isinstance(actual, dict):
            raise EvidenceError("derivation: selected row is not an object")
        if (
            actual.get("row") != expected["row"]
            or actual.get("source_label") != expected["source_label"]
            or actual.get("label") != expected["label"]
            or actual.get("change_usd_billions") != expected["change"]
        ):
            raise EvidenceError(f"derivation: selected row drifted: {actual!r}")
        bars.append({"label": expected["label"], "value": expected["change"], "color": expected["color"]})

    return {
        "title": "WHERE THE OFFSET SHOWS UP",
        "sub": "Selected Table A changes · 01 Jun 2022 → 11 Jun 2025 · USD billions",
        "src": "Federal Reserve Board · Monetary Policy Report June 2025 · Table A · USD billions",
        "src_style": "compact",
        "unit": CHART_VALUE_UNIT,
        "ylabel": CHART_YLABEL,
        "left_gutter": CHART_LEFT_GUTTER,
        "from_zero": True,
        "domain": [-2400, 2400],
        "bars": bars,
        "status": "REAL",
        "facts": {
            "window_start": WINDOW["start"],
            "window_end": WINDOW["end"],
            "same_source": True,
            "same_change_column": COLUMN_ID,
            "scale": "common zero-centered USD billions",
            "selected_rows_not_exhaustive_reconciliation": True,
            "other_reverse_repos_row_is_not_total": True,
        },
        "proof": [
            {
                "kind": "primary_source",
                "publisher": source["publisher"],
                "url": source["url"],
                "path": source["path"],
                "sha256": source["sha256"],
                "table": source["table"],
                "column": source["column"],
                "window": dict(source["window"]),
                "units": source["units"],
                "rows": [row["row"] for row in SELECTED_ROWS],
            }
        ],
        "notes": [
            "Selected rows are direct values from one Table A change column; they are not an exhaustive reconciliation.",
            "Other reverse repos is the xsheetr18 Others row, not total reverse repos.",
            "This page compares signed changes over the stated historical window; it is not a time curve or current-balance chart.",
            "Native ledger bars are vertical story bars; horizontal signed bars are not a supported native builder. Display labels are shortened for the five-column layout; source row names remain in proof.",
        ],
    }


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build_objects(
    root: Path = EPISODE_ROOT,
    output_dir: Path | None = None,
    expected_source_sha256: str = SOURCE_SHA256,
) -> dict[str, dict[str, Any]]:
    """Verify, derive, and write the object and its sidecar deterministically."""
    root = Path(root).resolve()
    # derive() performs the hash check before this function touches output paths.
    derivation = derive(root, expected_source_sha256)
    series = series_from_derivation(derivation)
    object_dir = Path(output_dir).resolve() if output_dir is not None else root / "evidence" / "objects"
    derived_dir = object_dir.parent / "derived"
    object_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)
    (derived_dir / DERIVED_NAME).write_bytes(_json_bytes(derivation))
    (object_dir / OBJECT_NAME).write_bytes(_json_bytes(series))
    return {OBJECT_NAME: series}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the hash-bound C3 runoff-offset ledger object.")
    parser.add_argument("--project-root", type=Path, default=EPISODE_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--output-dir", type=Path, default=None, help="object output directory")
    parser.add_argument("--expected-sha256", default=SOURCE_SHA256, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        build_objects(args.project_root, args.output_dir, args.expected_sha256)
    except (EvidenceError, OSError) as exc:
        print(f"runoff comparison: BLOCKED: {exc}", file=sys.stderr)
        return 2
    output_dir = (args.output_dir or (args.project_root / "evidence" / "objects")).resolve()
    values = ",".join(f"{row['label']}={row['change']}" for row in SELECTED_ROWS)
    print(f"runoff comparison: PASS ({OBJECT_NAME}; {values}; source={SOURCE_SHA256[:12]}; output={output_dir})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
