"""Focused source-bound tests for the C3 runoff-offset comparison object."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
OBJECT = EPISODE / "evidence/objects/fed-runoff-offsets.series.json"
DERIVED = EPISODE / "evidence/derived/fed-runoff-offsets.json"
sys.path.insert(0, str(EPISODE))
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_runoff_comparison as B  # noqa: E402
import ledger_page as L  # noqa: E402


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_retained_table_rows_are_exact_and_source_bound() -> None:
    derived = B.derive(EPISODE)

    assert derived["source"]["sha256"] == B.SOURCE_SHA256
    assert derived["source"]["table"] == B.TABLE_ID
    assert derived["source"]["column"] == B.COLUMN_ID
    assert derived["source"]["window"] == B.WINDOW
    assert [(row["row"], row["change_usd_billions"]) for row in derived["rows"]] == [
        ("xsheetr13", -2238),
        ("xsheetr15", 72),
        ("xsheetr18", -1760),
        ("xsheetr19", -504),
        ("xsheetr17", 106),
    ]
    assert derived["selection"]["selected_rows_not_exhaustive_reconciliation"] is True
    assert derived["selection"]["other_reverse_repos_row_is_not_total"] is True
    assert "not total reverse repos" in derived["claim_boundary"]


def test_native_object_is_zero_centered_and_ledger_valid() -> None:
    series = B.series_from_derivation(B.derive(EPISODE))

    assert L.validate(series, "bars") == []
    assert series["unit"] == " bn"
    assert series["ylabel"] == "USD billions"
    assert series["left_gutter"] == B.CHART_LEFT_GUTTER == 140
    assert series["sub"] == "Selected Table A changes · 01 Jun 2022 → 11 Jun 2025 · USD billions"
    assert series["from_zero"] is True
    assert series["domain"] == [-2400, 2400]
    assert [(bar["label"], bar["value"]) for bar in series["bars"]] == [
        ("Fed assets", -2238),
        ("Reserves", 72),
        ("Other RRP", -1760),
        ("TGA", -504),
        ("Foreign", 106),
    ]
    assert series["facts"]["selected_rows_not_exhaustive_reconciliation"] is True
    assert series["facts"]["other_reverse_repos_row_is_not_total"] is True
    assert L.pick_builder(series, "bars") == "story"
    assert "presentation" not in series
    assert "horizontal signed bars" in series["notes"][-1]
    assert "series" not in series and "svg" not in series


def test_story_page_passes_left_gutter_to_native_axes() -> None:
    series = B.series_from_derivation(B.derive(EPISODE))
    page = L.build_spec(series, "bars")
    assert page["axes"]["left_gutter"] == 140


def test_renderer_has_opt_in_gutter_with_legacy_defaults() -> None:
    renderer = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")
    block = renderer[renderer.index("const buildLedgerBars"):renderer.index("const buildLedgerLine")]
    assert "left_gutter" in block
    assert "P ? 150 : 60" in block
    assert "Math.max(defaultGutter, requestedGutter)" in block


def test_builder_output_is_byte_deterministic_and_native_files_match(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    B.build_objects(EPISODE, first_root / "objects")
    B.build_objects(EPISODE, second_root / "objects")

    first_object = first_root / "objects" / B.OBJECT_NAME
    second_object = second_root / "objects" / B.OBJECT_NAME
    first_derived = first_root / "derived" / B.DERIVED_NAME
    second_derived = second_root / "derived" / B.DERIVED_NAME
    assert first_object.read_bytes() == second_object.read_bytes()
    assert first_derived.read_bytes() == second_derived.read_bytes()
    assert _read_json(first_object) == B.series_from_derivation(B.derive(EPISODE))
    assert _read_json(first_derived) == B.derive(EPISODE)


def test_wrong_source_hash_fails_before_output_writes(tmp_path: Path) -> None:
    output = tmp_path / "objects"
    output.mkdir()
    sentinel = output / "sentinel.txt"
    sentinel.write_text("untouched", encoding="utf-8")

    with pytest.raises(B.EvidenceError, match="SHA-256 mismatch"):
        B.build_objects(EPISODE, output, "0" * 64)

    assert sentinel.read_text(encoding="utf-8") == "untouched"
    assert not (tmp_path / "derived").exists()
    assert not (output / B.OBJECT_NAME).exists()


def test_committed_artifacts_reproduce_builder_and_validate() -> None:
    assert OBJECT.is_file(), OBJECT
    assert DERIVED.is_file(), DERIVED
    assert _read_json(OBJECT) == B.series_from_derivation(B.derive(EPISODE))
    assert _read_json(DERIVED) == B.derive(EPISODE)
    assert L.validate(_read_json(OBJECT), "bars") == []
