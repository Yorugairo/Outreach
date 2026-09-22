"""Explicit native bar gutters retain units without clipping their ticks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ledger_page as L


def source():
    return {"title": "Comparison", "src": "Source", "unit": " bn",
            "bars": [{"label": "A", "value": -2238}, {"label": "B", "value": 72}]}


def test_gutter_is_optional_and_keyed():
    raw = source()
    base = L.build_spec(raw, "bars")
    raw["left_gutter"] = 140
    assert not L.validate(raw, "bars")
    wide = L.build_spec(raw, "bars")
    assert "left_gutter" not in base.get("axes", {})
    assert wide["axes"]["left_gutter"] == 140
    assert L.page_ink_key(base) != L.page_ink_key(wide)
    assert wide["values"] == base["values"]


def test_gutter_rejects_invalid_geometry():
    for value in [True, None, "140", -1, 999, float("nan")]:
        raw = source()
        raw["left_gutter"] = value
        assert any("left_gutter" in e for e in L.validate(raw, "bars"))
