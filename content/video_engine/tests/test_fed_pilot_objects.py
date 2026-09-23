"""Source-bound regression tests for the Fed pilot evidence objects.

The tests deliberately exercise the retained episode copies, not a network
fetch.  The builder must fail before writing an object when one of the bound
inputs drifts, while the emitted files remain ordinary ``ledger_page``
series objects.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
OBJECTS = EPISODE / "evidence/objects"
SOURCES = EPISODE / "evidence/sources"
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(EPISODE))

import build_pilot_objects as B  # noqa: E402
import ledger_page as L  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bound_paths(value: object) -> set[str]:
    """Collect every episode-relative file referenced by the claims manifest."""
    paths: set[str] = set()
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and "sha256" in value:
            paths.add(value["path"])
        if isinstance(value.get("metadata_path"), str) and "metadata_sha256" in value:
            paths.add(value["metadata_path"])
        for child in value.values():
            paths.update(_bound_paths(child))
    elif isinstance(value, list):
        for child in value:
            paths.update(_bound_paths(child))
    return paths


def _copy_bound_episode(destination: Path) -> Path:
    """Make a minimal, isolated copy of the manifest and every bound file."""
    claims_path = EPISODE / "claims.v1.json"
    claims = json.loads(claims_path.read_text(encoding="utf-8"))
    for relative in {"claims.v1.json", *_bound_paths(claims)}:
        source = EPISODE / relative
        assert source.is_file(), relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return destination


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_emitted_objects_are_source_bound_and_ledger_valid():
    assets = _read_json(OBJECTS / B.OBJECT_NAMES[0])
    rrp = _read_json(OBJECTS / B.OBJECT_NAMES[1])

    assert L.validate(assets, "bars") == []
    assert assets["sub"] == "Fed balance-sheet change · 01 Jun 2022 → 11 Jun 2025"
    assert assets["src"].startswith("Federal Reserve Board")
    assert assets["facts"] == {
        "window_start": "2022-06-01",
        "window_end": "2025-06-11",
        "same_source": True,
        "scale": "common zero-centered USD billions",
    }
    assert assets["domain"] == [-2238, 2238]
    assert [(bar["label"], bar["value"]) for bar in assets["bars"]] == [
        ("Total assets", -2238),
        ("Reserve balances", 72),
    ]
    assert any("no time curve" in note for note in assets["notes"])
    assert assets["proof"][0]["sha256"] == _sha256(SOURCES / "mpr_2025_06.html")

    assert L.validate(rrp, "line") == []
    points = rrp["series"][0]["pts"]
    assert len(points) == 1176
    assert rrp["title"] == "WHERE THE CASH WAS PARKED"
    assert rrp["sub"].startswith("Daily ON RRP balance · 03 Jan 2022 → 18 Sep 2026")
    assert rrp["src"] == "FRED RRPONTSYD · daily observations · USD billions"
    assert rrp["facts"]["series"] == "RRPONTSYD"
    assert rrp["facts"]["peak_date"] == "2022-12-30"
    assert rrp["facts"]["peak_value"] == 2553.716
    assert rrp["facts"]["latest_date"] == "2026-09-18"
    assert rrp["facts"]["latest_value"] == 0.576
    assert rrp["no_interpolation"] is True
    assert rrp["proof"][0]["sha256"] == _sha256(SOURCES / "fred_rrpontsyd.csv")


def test_production_rrp_uses_phone_profile_without_redundant_end_tag():
    generated = B.build_objects()[B.OBJECT_NAMES[1]]
    retained = _read_json(OBJECTS / B.OBJECT_NAMES[1])
    assert generated["readability"] == retained["readability"] == "landscape-phone"
    assert "name" not in generated["series"][0]
    assert generated["series"][0]["label"] == "ON RRP"
    assert generated["unit"] == generated["ylabel"] == "USD billions"
    assert L.validate(generated, "line") == []
    assert generated == retained


def test_rrp_points_match_every_retained_numeric_source_row():
    expected: list[tuple[date, float]] = []
    with (SOURCES / "fred_rrpontsyd.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if not row["RRPONTSYD"].strip():
                continue
            day = date.fromisoformat(row["observation_date"])
            if B.RRP_START <= day <= B.RRP_END:
                expected.append((day, float(row["RRPONTSYD"])))

    actual = _read_json(OBJECTS / B.OBJECT_NAMES[1])["series"][0]["pts"]
    assert len(actual) == len(expected) == 1176
    for point, (day, value) in zip(actual, expected):
        assert point[0] == B._decimal_year(day)
        assert point[1] == value
    assert actual[0] == [B._decimal_year(date(2022, 1, 3)), expected[0][1]]
    assert actual[-1] == [B._decimal_year(date(2026, 9, 18)), 0.576]
    assert max(actual, key=lambda point: point[1]) == [B._decimal_year(date(2022, 12, 30)), 2553.716]


def test_builder_output_is_byte_deterministic_and_sources_are_untouched(tmp_path):
    tracked = [
        EPISODE / "claims.v1.json",
        SOURCES / "fred_rrpontsyd.csv",
        SOURCES / "fred_rrpontsyd_meta.html",
        SOURCES / "mpr_2025_06.html",
        EPISODE / "evidence/derived/extraction_metadata.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    first = tmp_path / "first"
    second = tmp_path / "second"
    B.build_objects(EPISODE, first)
    B.build_objects(EPISODE, second)
    for name in B.OBJECT_NAMES:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    assert {path: path.read_bytes() for path in tracked} == before


def test_hash_drift_blocks_before_emission(tmp_path):
    root = _copy_bound_episode(tmp_path / "episode")
    source = root / "evidence/sources/mpr_2025_06.html"
    source.write_text(source.read_text(encoding="utf-8") + "\n<!-- drift -->\n", encoding="utf-8")
    output = tmp_path / "objects"
    with pytest.raises(B.EvidenceError, match="SHA-256 mismatch"):
        B.build_objects(root, output)
    assert not output.exists()


def test_rrp_missing_latest_or_duplicate_date_blocks(tmp_path):
    source = tmp_path / "rrp.csv"
    original = (SOURCES / "fred_rrpontsyd.csv").read_text(encoding="utf-8")
    rows = list(csv.DictReader(original.splitlines()))
    rows[-1]["RRPONTSYD"] = ""
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["observation_date", "RRPONTSYD"])
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(B.EvidenceError, match="latest numeric observation"):
        B._build_rrp_history(ROOT, source, source, "0" * 64, "0" * 64, "0" * 64)

    duplicate_source = tmp_path / "rrp-duplicate.csv"
    duplicate_rows = rows[:-1] + [dict(rows[-2])]
    with duplicate_source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["observation_date", "RRPONTSYD"])
        writer.writeheader()
        writer.writerows(duplicate_rows)
    with pytest.raises(B.EvidenceError, match="strictly increasing"):
        B._build_rrp_history(ROOT, duplicate_source, duplicate_source, "0" * 64, "0" * 64, "0" * 64)


def test_contract_drift_blocks_units_and_window(tmp_path):
    root = _copy_bound_episode(tmp_path / "episode")
    claims_path = root / "claims.v1.json"
    claims = _read_json(claims_path)
    claims["claims"][0]["units"] = "USD"
    claims_path.write_text(json.dumps(claims), encoding="utf-8")
    with pytest.raises(B.EvidenceError, match="C1-C2: expected USD billions"):
        B.build_objects(root)

    root = _copy_bound_episode(tmp_path / "episode-window")
    claims_path = root / "claims.v1.json"
    claims = _read_json(claims_path)
    claims["claims"][1]["window"]["end"] = "2025-06-12"
    claims_path.write_text(json.dumps(claims), encoding="utf-8")
    with pytest.raises(B.EvidenceError, match="C3: expected USD billions window"):
        B.build_objects(root)
