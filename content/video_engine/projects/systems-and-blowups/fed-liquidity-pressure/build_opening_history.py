"""Build a matched, source-bound opening history; never interpolate endpoints."""
from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
START, END = date(2022, 6, 1), date(2025, 6, 11)
SERIES = (("WALCL", "Total assets", "crimson"), ("WRBWFRBL", "Bank reserves", "teal"))
DEFAULT_INTAKE = REPO / "docs/research/runs/fed-opening-histories-2026-09-18"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observations(raw: bytes, series: str) -> dict[date, Decimal]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields = reader.fieldnames or []
    date_column = "observation_date" if "observation_date" in fields else "DATE"
    if date_column not in fields or series not in fields:
        raise ValueError(f"{series}: missing FRED date/value columns")
    values = {}
    for row in reader:
        day = date.fromisoformat(row[date_column])
        if not START <= day <= END:
            continue
        if day in values:
            raise ValueError(f"{series}: duplicate observation {day}")
        try:
            value = Decimal(row[series])
        except InvalidOperation as exc:
            raise ValueError(f"{series}: missing/non-numeric observation {day}") from exc
        if not value.is_finite():
            raise ValueError(f"{series}: non-finite observation {day}")
        values[day] = value
    expected = {START + timedelta(days=7*i) for i in range((END-START).days // 7 + 1)}
    if set(values) != expected:
        raise ValueError(f"{series}: requires every actual Wednesday in the exact window")
    return dict(sorted(values.items()))


def decimal_year(day: date) -> float:
    start, end = date(day.year, 1, 1), date(day.year + 1, 1, 1)
    return day.year + (day-start).days / (end-start).days


def verified_entry(intake: Path, manifest: dict, name: str) -> tuple[Path, dict]:
    matches = [e for e in manifest.get("entries", [])
               if e.get("path") and Path(e["path"]).name == name and e.get("status") != "not-fetched"]
    if len(matches) != 1:
        raise ValueError(f"{name}: expected one archived successful response")
    entry = matches[0]
    path = Path(entry["path"])
    if not path.is_absolute():
        path = intake / path
    path = path.resolve()
    if not path.is_relative_to(intake.resolve()):
        raise ValueError(f"{name}: source escapes intake")
    if urlparse(entry.get("url", "")).hostname != "fred.stlouisfed.org":
        raise ValueError(f"{name}: expected official FRED source")
    if sha(path) != entry.get("sha256") or path.stat().st_size != entry.get("bytes"):
        raise ValueError(f"{name}: hash/byte count mismatch")
    return path, entry


def build(intake: Path = DEFAULT_INTAKE, *, write: bool = False) -> dict:
    manifest = json.loads((intake / "MANIFEST.json").read_text(encoding="utf-8"))
    histories, proof, files, endpoint_changes = [], [], [], {}
    for code, label, color in SERIES:
        data_path, entry = verified_entry(intake, manifest, f"fred_{code.lower()}.csv")
        meta_path, meta = verified_entry(intake, manifest, f"fred_{code.lower()}_meta.html")
        metadata = re.sub(r"<[^>]+>", " ", meta_path.read_text(encoding="utf-8"))
        metadata = " ".join(metadata.split()).lower()
        for required in ("millions of u.s. dollars", "wednesday", code.lower()):
            if required not in metadata:
                raise ValueError(f"{code}: official metadata lacks {required}")
        values = observations(data_path.read_bytes(), code)
        # Millions -> trillions; subtract the ACTUAL baseline, never a rounded table value.
        points = [[decimal_year(day), float((value-values[START])/Decimal(1000000))]
                  for day, value in values.items()]
        histories.append({"label": label, "color": color, "pts": points})
        endpoint_changes[code] = str((values[END]-values[START])/Decimal(1000))
        for path, item in ((data_path, entry), (meta_path, meta)):
            files.append(path)
            proof.append({"path": f"evidence/sources/opening-history/{path.name}",
                          "sha256": item["sha256"], "url": item["url"],
                          "fetched_at": item.get("fetched_at"), "series": code})
    obj = {
        "title": "Assets fell. Reserves barely changed.",
        "readability": "landscape-phone",
        "sub": "Change since 1 Jun 2022 · through 11 Jun 2025",
        "src": "Fed H.4.1 / FRED · WALCL + WRBWFRBL · Jun 2022–Jun 2025",
        "unit": "", "ylabel": "Change ($ trillions)", "domain": [-2.5, 0.5],
        "xticks": [[decimal_year(d), label] for d, label in
                   ((START, "Jun 2022"), (date(2024, 1, 1), "2024"), (END, "Jun 2025"))],
        "series": histories, "status": "DERIVED", "proof": proof,
        "facts": {"window_start": START.isoformat(), "window_end": END.isoformat(),
                  "basis": "Weekly Wednesday level; millions USD in source",
                  "derivation": "(observation - 2022-06-01 observation) / 1000000",
                  "observation_dates": [d.isoformat() for d in values],
                  "endpoint_changes_usd_billions": endpoint_changes,
                  "interpolation": False, "decimation": False},
    }
    if write:
        destination = HERE / "evidence/sources/opening-history"
        destination.mkdir(parents=True, exist_ok=True)
        for path in files:
            target = destination / path.name
            if target.exists() and sha(target) != sha(path):
                raise ValueError(f"refusing to overwrite changed retained source {target.name}")
        for path in files:
            shutil.copyfile(path, destination / path.name)
        output = HERE / "evidence/objects/fed-assets-reserves-history.series.json"
        output.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return obj


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build(args.intake, write=args.write)
    print(json.dumps({"observations_per_series": len(result["series"][0]["pts"]),
                      "endpoint_changes_usd_billions": result["facts"]["endpoint_changes_usd_billions"],
                      "written": args.write}, indent=2))
