"""Focused source-bound tests for the Fed episode's corporate debt-wall object."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
SOURCE = EPISODE / "evidence/sources/sp_global_corporate_maturities_2025_snapshot.html"
DERIVED = EPISODE / "evidence/derived/debt-wall-2025-2027.json"
OBJECT = EPISODE / "evidence/objects/debt-wall-2025-2027.series.json"
sys.path.insert(0, str(EPISODE))

import debt_wall_evidence as B  # noqa: E402

sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import ledger_page as L  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_committed_debt_wall_is_source_bound_and_ledger_valid() -> None:
    assert SOURCE.is_file()
    assert _sha256(SOURCE) == B.SOURCE_SHA256
    chart = _read_json(OBJECT)
    derived = _read_json(DERIVED)

    assert L.validate(chart, "bars") == []
    assert chart["unit"] == " bn"
    assert chart["ylabel"] == "USD billions"
    assert chart["left_gutter"] == B.CHART_LEFT_GUTTER == 200
    assert chart["from_zero"] is True
    assert chart["domain"] == [0, 1400]
    assert chart["xticks"] == [[2025, "2025"], [2026, "2026"], [2027, "2027"]]
    assert [(bar["label"], bar["value"]) for bar in chart["bars"]] == [
        ("2025", 816),
        ("2026", 1167),
        ("2027", 1201),
    ]
    assert chart["facts"]["maturities_usd_billions"] == 3184
    assert chart["facts"]["snapshot_date"] == "2025-01-01"
    assert chart["facts"]["included_instruments"] == [
        "bonds",
        "loans",
        "revolving credit facilities",
    ]
    assert chart["proof"][0]["sha256"] == B.SOURCE_SHA256
    assert derived["selected_year_total_usd_billions"] == 3184
    assert derived["source"]["path"] == B.SOURCE_RELATIVE_PATH
    assert derived["source"]["sha256"] == B.SOURCE_SHA256
    assert "not a claim" in derived["claim_boundary"]
    assert L.pick_builder(chart, "bars") == "story"
    assert isinstance(chart["bars"][0]["value"], int)
    assert " bn" in chart["notes"][-1]


def test_builder_reproduces_committed_artifacts_byte_for_byte(tmp_path: Path) -> None:
    output = tmp_path / "objects"
    generated = B.build_objects(EPISODE, output)
    assert generated[B.OBJECT_NAME]["bars"][1]["value"] == 1167
    assert (output / B.OBJECT_NAME).read_bytes() == OBJECT.read_bytes()
    assert (tmp_path / "derived" / B.DERIVED_NAME).read_bytes() == DERIVED.read_bytes()


def test_wrong_source_hash_rejects_before_emission(tmp_path: Path) -> None:
    output = tmp_path / "objects"
    with pytest.raises(B.EvidenceError, match="SHA-256 mismatch"):
        B.build_objects(EPISODE, output, "0" * 64)
    assert not output.exists()
    assert not (tmp_path / "derived").exists()


def test_source_metadata_retains_snapshot_and_rating_scope() -> None:
    derived = B.derive(EPISODE)
    selection = derived["selection"]
    assert selection["issuer_scope"] == "financial and nonfinancial corporate issuers"
    assert selection["rating_scope"] == "rated by S&P Global Ratings"
    assert selection["included_instruments"] == list(B.INCLUDED_INSTRUMENTS)
    assert derived["source"]["snapshot_date"] == "2025-01-01"
    assert derived["rows"] == [
        {"year": 2025, "value_usd_billions": 816},
        {"year": 2026, "value_usd_billions": 1167},
        {"year": 2027, "value_usd_billions": 1201},
    ]
