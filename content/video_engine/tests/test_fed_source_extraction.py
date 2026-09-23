"""Focused local tests for the fed-liquidity evidence extractor."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure/evidence/extract_sources.py"
SPEC = importlib.util.spec_from_file_location("fed_extract_sources", SCRIPT)
assert SPEC and SPEC.loader
EXTRACT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = EXTRACT
SPEC.loader.exec_module(EXTRACT)


def _write(path: Path, content: str | bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8", newline="")
    return path


def _manifest_entry(path: Path, root: Path, url: str, *, old: bool = False) -> dict:
    data = path.read_bytes()
    base = {"url": url, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "fetched_at": "2026-09-18T00:00:00Z"}
    if old:
        base["file"] = path.relative_to(root).as_posix()
    else:
        base["path"] = str(path)
    return base


def _write_manifest(root: Path, entries: list[dict]) -> None:
    _write(root / "MANIFEST.json", json.dumps({"entries": entries}, indent=2) + "\n")


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    original = tmp_path / "original"
    old_source = _write(original / "sources" / "old.txt", "retained original\n")
    _write_manifest(original, [_manifest_entry(old_source, original, "local://old", old=True)])

    raw = tmp_path / "raw"
    sources = raw / "sources"
    rrp_meta = _write(sources / "fred_rrpontsyd_meta.html", "Billions of US Dollars, Not Seasonally Adjusted Daily aggregated daily amount")
    rrp_csv = _write(
        sources / "fred_rrpontsyd.csv",
        "observation_date,RRPONTSYD\n2021-12-31,\n2022-01-03,100.000\n2022-01-04,99.500\n2026-09-18,0.576\n",
    )
    iorb_meta = _write(
        sources / "fred_iorb_meta.html",
        "Interest Rate on Reserve Balances Percent, Not Seasonally Adjusted Board of Governors Daily",
    )
    iorb_csv = _write(
        sources / "fred_iorb_history.csv",
        "observation_date,IORB\n2025-09-02,3.65\n2025-09-03,3.65\n2026-09-19,3.90\n",
    )
    tgcr = _write(
        sources / "nyfed_tgcr_search_20250901_20260918.json",
        json.dumps({"refRates": [
            {"effectiveDate": "2025-09-03", "type": "TGCR", "percentRate": 3.60, "volumeInBillions": 1191},
            {"effectiveDate": "2025-09-02", "type": "TGCR", "percentRate": 3.63, "volumeInBillions": 1153},
        ]}),
    )
    sofr = _write(
        sources / "nyfed_sofr_search_20250901_20260918.json",
        json.dumps({"refRates": [
            {"effectiveDate": "2025-09-03", "type": "SOFR", "percentRate": 3.62, "volumeInBillions": 2931},
            {"effectiveDate": "2025-09-02", "type": "SOFR", "percentRate": 3.64, "volumeInBillions": 2900},
        ]}),
    )
    detail = [
        {"securityType": "Treasury", "amtSubmitted": 1000000, "amtAccepted": 1000000, "percentOfferingRate": 3.75},
        {"securityType": "Agency", "amtSubmitted": 0, "amtAccepted": 0, "percentOfferingRate": 3.75},
        {"securityType": "Mortgage-Backed", "amtSubmitted": 0, "amtAccepted": 0, "percentOfferingRate": 3.75},
    ]
    repo_row = {
        "operationId": "RP 090326 27", "auctionStatus": "Results", "operationDate": "2026-09-03",
        "settlementDate": "2026-09-03", "maturityDate": "2026-09-04", "operationType": "Repo",
        "operationMethod": "Full Allotment", "settlementType": "Same Day", "termCalenderDays": 1,
        "term": "Overnight", "releaseTime": "13:30", "closeTime": "13:45", "totalAmtSubmitted": 1000000,
        "totalAmtAccepted": 1000000, "details": detail,
    }
    reverse_row = {
        "operationId": "RP 090326 26", "auctionStatus": "Results", "operationDate": "2026-09-03",
        "settlementDate": "2026-09-03", "maturityDate": "2026-09-04", "operationType": "Reverse Repo",
        "operationMethod": "Fixed Rate", "settlementType": "Same Day", "termCalenderDays": 1,
        "term": "Overnight", "totalAmtSubmitted": 2000000, "totalAmtAccepted": 2000000, "details": detail,
    }
    srf = _write(sources / "nyfed_srf_repo_results_20260901_20260918.json", json.dumps({"repo": {"operations": [repo_row]}}))
    all_rp = _write(sources / "nyfed_all_rp_results_20260901_20260918.json", json.dumps({"repo": {"operations": [repo_row, reverse_row]}}))
    reverse = _write(
        sources / "nyfed_rrp_propositions_20260901_20260918.json",
        json.dumps({"repo": {"operations": [{"operationId": "RP 090326 26", "operationDate": "2026-09-03", "operationType": "Reverse Repo", "totalAmtAccepted": 2000000}]}}),
    )
    api_spec = _write(sources / "nyfed_markets_api_spec.yml", "totalAmtAccepted\noperationType\n")
    selected = [
        (rrp_csv, "https://fred.stlouisfed.org/graph/fredgraph.csv?id=RRPONTSYD"),
        (rrp_meta, "https://fred.stlouisfed.org/series/RRPONTSYD"),
        (iorb_csv, "https://fred.stlouisfed.org/graph/fredgraph.csv?id=IORB"),
        (iorb_meta, "https://fred.stlouisfed.org/series/IORB"),
        (tgcr, "https://markets.newyorkfed.org/api/rates/secured/tgcr/search.json?startDate=2025-09-01&endDate=2026-09-18"),
        (sofr, "https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate=2025-09-01&endDate=2026-09-18"),
        (srf, "https://markets.newyorkfed.org/api/rp/results/search.json?startDate=2026-09-01&endDate=2026-09-18&operationTypes=Repo"),
        (all_rp, "https://markets.newyorkfed.org/api/rp/results/search.json?startDate=2026-09-01&endDate=2026-09-18"),
        (reverse, "https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json?startDate=2026-09-01&endDate=2026-09-18"),
        (api_spec, "https://markets.newyorkfed.org/static/docs/markets-api.yml"),
    ]
    _write_manifest(raw, [_manifest_entry(path, raw, url) for path, url in selected])
    return original, raw


def _args(original: Path, raw: Path, output: Path, *extra: str) -> list[str]:
    return ["--original-run-dir", str(original), "--raw-fetch-dir", str(raw), "--output-dir", str(output), *extra]


def _refresh_manifest_entry(raw: Path, path: Path) -> None:
    manifest_path = raw / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest["entries"]:
        if entry.get("path") == str(path):
            payload = path.read_bytes()
            entry.update(sha256=hashlib.sha256(payload).hexdigest(), bytes=len(payload))
            break
    else:
        raise AssertionError(f"manifest entry missing for {path}")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def test_synthetic_extraction_is_hash_bound_exact_join_and_separates_repo(tmp_path: Path) -> None:
    original, raw = _fixture(tmp_path)
    bundle = EXTRACT.build_extraction(original, raw)
    assert bundle.metadata["rrp"]["observations"] == 3
    assert bundle.metadata["rates"]["joined_observations"] == 2
    assert bundle.metadata["repo"]["operations"] == 1
    assert bundle.metadata["repo"]["total_accepted_usd"] == "1000000"
    assert bundle.metadata["reverse_repo"]["total_accepted_usd"] == "2000000"
    assert b"2025-09-02,3.65,3.63,-2.00" in bundle.outputs["funding_rates.csv"]
    assert b"RP 090326 27" in bundle.outputs["repo_operations.csv"]
    assert b"RP 090326 26" in bundle.outputs["reverse_repo_operations.csv"]

    again = EXTRACT.build_extraction(original, raw)
    assert bundle.outputs == again.outputs


def test_check_mode_does_not_overwrite_or_create_outputs(tmp_path: Path) -> None:
    original, raw = _fixture(tmp_path)
    output = tmp_path / "derived"
    sentinel = _write(output / "sentinel.txt", "keep\n")
    assert EXTRACT.main(_args(original, raw, output, "--check")) == 0
    assert sentinel.read_text(encoding="utf-8") == "keep\n"
    assert not (output / "extraction_metadata.json").exists()


def test_manifest_tamper_fails_before_payload_parse(tmp_path: Path) -> None:
    original, raw = _fixture(tmp_path)
    target = raw / "sources" / "fred_rrpontsyd.csv"
    target.write_text(target.read_text(encoding="utf-8") + "2026-09-17,0.5\n", encoding="utf-8")
    with pytest.raises(EXTRACT.ExtractionError, match="manifest (byte|hash) mismatch"):
        EXTRACT.build_extraction(original, raw)


def test_wrong_rate_type_is_rejected_even_when_date_matches(tmp_path: Path) -> None:
    original, raw = _fixture(tmp_path)
    path = raw / "sources" / "nyfed_sofr_search_20250901_20260918.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["refRates"][0]["type"] = "SOFRAI"
    path.write_text(json.dumps(data), encoding="utf-8")
    _refresh_manifest_entry(raw, path)
    with pytest.raises(EXTRACT.ExtractionError, match="requested type 'SOFR'"):
        EXTRACT.build_extraction(original, raw)


def test_missing_iorb_exact_date_fails_closed(tmp_path: Path) -> None:
    original, raw = _fixture(tmp_path)
    path = raw / "sources" / "fred_iorb_history.csv"
    path.write_text("observation_date,IORB\n2025-09-02,3.65\n", encoding="utf-8")
    _refresh_manifest_entry(raw, path)
    with pytest.raises(EXTRACT.ExtractionError, match="missing 1 dates"):
        EXTRACT.build_extraction(original, raw)


def test_rate_url_lower_bound_is_enforced(tmp_path: Path) -> None:
    original, raw = _fixture(tmp_path)
    path = raw / "sources" / "nyfed_tgcr_search_20250901_20260918.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["refRates"][0]["effectiveDate"] = "2025-08-29"
    path.write_text(json.dumps(data), encoding="utf-8")
    _refresh_manifest_entry(raw, path)
    with pytest.raises(EXTRACT.ExtractionError, match="outside requested URL window"):
        EXTRACT.build_extraction(original, raw)


def test_repo_url_lower_bound_is_enforced(tmp_path: Path) -> None:
    original, raw = _fixture(tmp_path)
    path = raw / "sources" / "nyfed_srf_repo_results_20260901_20260918.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["repo"]["operations"][0]["operationDate"] = "2025-08-31"
    path.write_text(json.dumps(data), encoding="utf-8")
    _refresh_manifest_entry(raw, path)
    with pytest.raises(EXTRACT.ExtractionError, match="outside requested URL window"):
        EXTRACT.build_extraction(original, raw)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("url", "", "requires a non-empty url"),
        ("fetched_at", "not-a-timestamp", "invalid fetched_at timestamp"),
        ("bytes", 100.9, "requires a non-negative integer bytes field"),
    ],
)
def test_manifest_requires_strict_fetch_fields(tmp_path: Path, field: str, value: object, message: str) -> None:
    original, raw = _fixture(tmp_path)
    manifest_path = raw / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["entries"][0][field] = value
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(EXTRACT.ExtractionError, match=message):
        EXTRACT.build_extraction(original, raw)


def test_metadata_is_stable_when_archives_are_relocated(tmp_path: Path) -> None:
    original_a, raw_a = _fixture(tmp_path / "a")
    original_b = tmp_path / "b" / "original"
    raw_b = tmp_path / "b" / "raw"
    shutil.copytree(original_a, original_b)
    shutil.copytree(raw_a, raw_b)
    manifest_path = raw_b / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest["entries"]:
        entry["path"] = str(raw_b / Path(entry["path"]).relative_to(raw_a))
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    first = EXTRACT.build_extraction(original_a, raw_a)
    relocated = EXTRACT.build_extraction(original_b, raw_b)
    assert first.outputs == relocated.outputs


def test_real_archives_validate_read_only() -> None:
    original = ROOT / "docs/research/runs/fed-liquidity-2026-09-18"
    raw = ROOT / "docs/research/runs/fed-liquidity-raw-fetch-2026-09-18"
    if not (original / "MANIFEST.json").is_file() or not (raw / "MANIFEST.json").is_file():
        pytest.skip("retained research archives are not present")
    bundle = EXTRACT.build_extraction(original, raw)
    assert bundle.metadata["rrp"]["observations"] == 1176
    assert bundle.metadata["rates"]["joined_observations"] == 261
    assert bundle.metadata["repo"]["total_accepted_usd"] == "430000000"
    assert bundle.metadata["repo"]["outstanding_balance"] is False
