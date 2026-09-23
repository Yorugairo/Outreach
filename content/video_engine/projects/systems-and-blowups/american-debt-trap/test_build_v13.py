from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[5]
BUILDER_PATH = ROOT / "content/video_engine/projects/systems-and-blowups/american-debt-trap/build_v13.py"
SPEC = importlib.util.spec_from_file_location("american_debt_trap_build_v13_test", BUILDER_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


def _words(*rows: tuple[str, float]) -> list[dict[str, object]]:
    out = []
    previous = 0.0
    for token, end in rows:
        out.append({"w": token, "start_s": previous, "end_s": end})
        previous = end
    return out


def test_segment_boundary_chooses_latest_complete_sentence_under_each_cap() -> None:
    words = _words(
        ("Opening.", 12.0),
        ("Bed.", 28.0),
        ("Over-cap.", 31.0),
        ("Unit.", 89.0),
        ("Unit-over-cap.", 95.0),
        ("Pilot.", 170.0),
        ("Pilot-over-cap.", 181.0),
    )
    assert BUILDER.complete_sentence_boundary(words, "bed").end_s == 28.0
    assert BUILDER.complete_sentence_boundary(words, "unit").end_s == 89.0
    assert BUILDER.complete_sentence_boundary(words, "pilot").end_s == 170.0


def test_segment_boundary_rejects_a_prefix_without_a_complete_sentence() -> None:
    words = _words(("Only", 10.0), ("a", 20.0), ("fragment", 29.0))
    with pytest.raises(BUILDER.BuildInputError, match="no complete sentence"):
        BUILDER.complete_sentence_boundary(words, "bed")


def test_canonical_alignment_rejects_take_token_drift(tmp_path: Path) -> None:
    script = tmp_path / "V13-VO.txt"
    script.write_text("[post-key] One measured sentence.\n", encoding="utf-8")
    words = _words(("One", 0.6), ("measured", 1.1), ("sentence.", 1.8))
    assert BUILDER.verify_canonical_alignment(words, script)
    words[1]["w"] = "wrong"
    with pytest.raises(BUILDER.BuildInputError, match="canonical narration token alignment"):
        BUILDER.verify_canonical_alignment(words, script)


def test_measured_timeline_normalizes_start_end_for_gates(tmp_path: Path) -> None:
    project = BUILDER._project(tmp_path / "build", tmp_path / "take")
    words = _words(("One.", 0.8), ("Two.", 1.7))
    path = BUILDER._write_measured_timeline(project, words, 1.7)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["runtime_s"] == 1.7
    assert payload["words"] == [
        {"w": "One.", "start": 0.0, "end": 0.8, "part": 1},
        {"w": "Two.", "start": 0.8, "end": 1.7, "part": 1},
    ]
    assert "start_s" not in payload["words"][0]


def test_asset_manifest_verifies_items_hashes_and_approval(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    episode = tmp_path / "episode"
    episode.mkdir()
    asset = tmp_path / "assets" / "world.png"
    approval = tmp_path / "approvals" / "world.json"
    asset.parent.mkdir()
    approval.parent.mkdir()
    asset.write_bytes(b"approved bytes")
    approval.write_text(json.dumps({"operator_approved": ["world-v1"]}), encoding="utf-8")
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = episode / "ASSET-CANDIDATES.json"
    manifest.write_text(json.dumps({
        "items": [{
            "asset_id": "world-v1",
            "path": "assets/world.png",
            "sha256": digest(asset),
            "approval_path": "approvals/world.json",
            "approval_sha256": digest(approval),
            "approval_field": "operator_approved",
            "approval_value": "world-v1",
        }],
    }), encoding="utf-8")
    monkeypatch.setattr(BUILDER, "REPO", tmp_path)
    monkeypatch.setattr(BUILDER, "HERE", episode)
    entries = BUILDER.load_asset_manifest(manifest)
    assert entries[0]["asset_id"] == "world-v1"
    assert entries[0]["path"] == asset.resolve()


def test_opening_gate_report_preserves_warn_without_force(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = tmp_path / "V13-VO.txt"
    timeline = tmp_path / "timeline.json"
    report = tmp_path / "GATES-OPENING.md"
    script.write_text("One.\n", encoding="utf-8")
    timeline.write_text("{\"words\": []}", encoding="utf-8")

    class Completed:
        returncode = 0
        stdout = "[WARN] G20 advisory\nRESULT: 0 FAIL / 1 WARN / 2 PASS / 0 JUDGE\n"
        stderr = ""

    monkeypatch.setattr(BUILDER.subprocess, "run", lambda *args, **kwargs: Completed())
    result = BUILDER._run_opening_gate(script, timeline, report)
    assert result.exit_code == 0
    assert result.fail_count == 0
    assert result.warn_count == 1
    assert "G20 advisory" in report.read_text(encoding="utf-8")
    assert "--force" not in report.read_text(encoding="utf-8")


def test_check_inputs_requires_explicit_take_dir() -> None:
    assert BUILDER.check_inputs(take_dir=None) == [
        "--take-dir is required; scratch generation is not part of this builder"
    ]


def test_effective_shot_table_is_quarantined_literal(tmp_path: Path) -> None:
    rows = [(0.0, 1.0, "world-internal-memo-v1;idle=none", (0, 0, 0), [], None)]
    path = BUILDER._write_effective_shot_table(tmp_path, rows)
    assert path == tmp_path / "SHOT-TABLE-V13-EFFECTIVE.py"
    assert BUILDER.T.load_rows(path) == rows
    assert "quarantined V13 row hand-off" in path.read_text(encoding="utf-8")
