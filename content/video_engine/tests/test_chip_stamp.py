"""Approved raster props are an explicit opt-in chip form, not generic icons."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402


PLATE = "world-spike-desk-v1"
STILL = (0, 0, 0)
APPROVED = "prop-badge-dram-memory-etf-v1"
APPROVED_ICON = "prop-icon-bear-market-v1"
APPROVED_PROP = "prop-liquidity-drain-pump-v1"


def _stamp(**overrides):
    entry = {
        "kind": "chip",
        "form": "stamp",
        "at": 10.0,
        "dur": 6.0,
        "icon": APPROVED,
        "label": "DRAM ETF",
        "target": {"kind": "region", "x0": 0.25, "y0": 0.35, "x1": 0.75, "y1": 0.85},
    }
    entry.update(overrides)
    return entry


def test_stamp_accepts_catalogued_raster_and_registers_prop_uri():
    entry = _stamp(size=260, ink="charcoal")
    assert B.validate_species([entry], STILL, PLATE) == []
    assert B.species_props(entry) == [APPROVED]
    assert B.species_icons(entry) == []


def test_stamp_accepts_approved_prop_icon_from_icons_catalogue():
    entry = _stamp(icon=APPROVED_ICON, label="BEAR MARKET")
    resolved = B.catalogue_stamp_asset(APPROVED_ICON)
    compiled, asset = B._with_stamp_catalogue(entry)
    assert B.validate_species([entry], STILL, PLATE) == []
    assert resolved["_catalogue"] == asset["_catalogue"] == compiled["_catalogue"] == "icons"
    assert compiled["icon"] == APPROVED_ICON
    assert "_catalogue" not in entry, "compiled provenance must not mutate the authored shot-table species"
    assert B.species_props(entry) == [APPROVED_ICON]
    assert B.catalogue_stamp_uri(APPROVED_ICON).startswith("data:image/png;base64,")


def test_stamp_refuses_approved_non_badge_finance_prop():
    entry = _stamp(icon=APPROVED_PROP, label="LIQUIDITY DRAIN", size=500)
    errors = B.validate_species([entry], STILL, PLATE)
    assert any(APPROVED_PROP in error and "E99 s87" in error for error in errors)
    # Asset provenance remains valid; only the chip presentation is refused.
    resolved = B.catalogue_stamp_asset(APPROVED_PROP)
    assert resolved["_catalogue"] == "props"
    assert resolved["file"].name == "prop-liquidity-drain-pump-v1.png"
    assert B.catalogue_stamp_uri(APPROVED_PROP).startswith("data:image/png;base64,")


def test_icon_stamp_keeps_420px_bound_while_prop_reaches_700px():
    assert any("size" in error and "420" in error
               for error in B.validate_species([_stamp(size=421)], STILL, PLATE))
    assert any("E99 s87" in error
               for error in B.validate_species([_stamp(icon=APPROVED_PROP, size=700)], STILL, PLATE))
    assert any("size" in error and "700" in error
               for error in B.validate_species([_stamp(icon=APPROVED_PROP, size=701)], STILL, PLATE))


@pytest.mark.parametrize("field, value, phrase", [
    ("sha256", "0" * 64, "hashes"),
    ("path", "assets/props/not-cutouts/prop-liquidity-drain-pump-v1.png", "not under assets/props/cutouts"),
])
def test_finance_prop_catalogue_refuses_path_or_hash_drift(monkeypatch, tmp_path, field, value, phrase):
    data = json.loads(B.PROP_CATALOG.read_text(encoding="utf-8"))
    row = next(p for p in data["props"] if p["id"] == APPROVED_PROP)
    row[field] = value
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(B, "PROP_CATALOG", manifest)
    monkeypatch.setattr(B, "_PROP_CATALOG_CACHE", None)
    with pytest.raises(ValueError, match=phrase):
        B.catalogue_prop(APPROVED_PROP)


def test_stamp_rejects_unapproved_or_legacy_icon_fallbacks():
    errors = B.validate_species([_stamp(icon="factory")], STILL, PLATE)
    assert any("chip stamp" in error and "not in finance_icons_catalog" in error for error in errors), errors


def test_stamp_closes_size_ink_and_label_contract():
    assert any("size" in error for error in B.validate_species([_stamp(size=179)], STILL, PLATE))
    assert any("ink" in error for error in B.validate_species([_stamp(ink="blue")], STILL, PLATE))
    assert any("at most 3 lines" in error
               for error in B.validate_species([_stamp(label="A\nB\nC\nD")], STILL, PLATE))
    assert any("state/cross_at" in error
               for error in B.validate_species([_stamp(cross_at=18)], STILL, PLATE))
