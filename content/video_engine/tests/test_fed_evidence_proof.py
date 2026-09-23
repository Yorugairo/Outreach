"""Authored diagnostic invariants; not pilot acceptance tests."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EP = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
SPEC = importlib.util.spec_from_file_location("fed_evidence_proof", EP / "build_evidence_proof.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_diagnostic_rows_have_continuous_authored_boundaries():
    rows = MODULE.build_rows()
    assert [(row[0], row[1]) for row in rows] == [(0, 8), (8, 18)]
    assert rows[1][5] == "slide:right"
    assert all(":axes:cut" in row[2] for row in rows)
    assert all(row[3] == (0, 0, 0) and row[4] == [] for row in rows)
    assert "domain=-2238,2238" in rows[0][2]


def test_callout_uses_actual_positive_reserve_datum():
    callout = MODULE.build_rows()[0][6][0]
    assert callout["label"] == "+72 USD billions"
    assert callout["target"] == {"kind": "datum", "index": 1}
    assert 4 < callout["at"] < callout["at"] + callout["dur"] < 8


def test_proof_formatting_preserves_source_values_and_files(tmp_path, monkeypatch):
    before = {p: p.read_bytes() for p in (MODULE.BAR_SOURCE, MODULE.RRP_SOURCE)}
    monkeypatch.setattr(MODULE, "PROOF_OBJECTS", tmp_path)
    monkeypatch.setattr(MODULE, "BAR_OBJECT", tmp_path / "bars.json")
    monkeypatch.setattr(MODULE, "RRP_OBJECT", tmp_path / "line.json")
    objects = MODULE.prepare_proof_objects()
    assert [bar["value"] for bar in objects["bars"]["bars"]] == [-2238, 72]
    assert "USD billions" in objects["bars"]["sub"] or "USD billions" in objects["bars"]["src"]
    assert len(objects["rrp"]["series"][0]["pts"]) == 1176
    assert objects["rrp"]["series"][0]["pts"][-1][1] == 0.576
    assert before == {p: p.read_bytes() for p in before}


def test_diagnostic_identity_cannot_be_mistaken_for_pilot():
    assert MODULE.TIMELINE_NAME == "fed-evidence-proof.timeline.json"
    assert MODULE.BUILD.name == "build-evidence-proof"
    assert "NOT FINAL NARRATION" in MODULE.DIAGNOSTIC_SUBTITLE
