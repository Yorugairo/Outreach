from __future__ import annotations

import copy
import json
from pathlib import Path

from content.video_engine.src.guards.research_gate import (
    RESEARCH_GATE_DIMENSIONS,
    research_gate_ok,
    validate_research_approval,
)
from content.video_engine.src.services.history_contracts import validate_research_packet


ENGINE_ROOT = Path(__file__).resolve().parents[1]


def _packet() -> dict:
    return json.loads((ENGINE_ROOT / "templates" / "research_packet.json").read_text(encoding="utf-8"))


def _rubric(research_hash: str, score: float = 4) -> dict:
    return {
        "research_hash": research_hash,
        "scores": {dimension: score for dimension in RESEARCH_GATE_DIMENSIONS},
        "reviewer": "operator",
    }


def test_research_gate_requires_all_six_scores_at_current_hash() -> None:
    packet = _packet()
    packet_hash = validate_research_packet(packet)["artifact_hash"]
    assert validate_research_approval(packet, _rubric(packet_hash), packet_hash) == []
    assert research_gate_ok(packet, _rubric(packet_hash), packet_hash)


def test_research_gate_rejects_low_score_stale_hash_and_missing_dimension() -> None:
    packet = _packet()
    packet_hash = validate_research_packet(packet)["artifact_hash"]

    low = _rubric(packet_hash, score=3)
    errors = validate_research_approval(packet, low, packet_hash)
    assert any("below the 4/5 threshold" in error for error in errors)

    stale = _rubric("0" * 64)
    errors = validate_research_approval(packet, stale, packet_hash)
    assert any("does not match" in error for error in errors)

    missing = _rubric(packet_hash)
    missing["scores"].pop("rights_readiness")
    errors = validate_research_approval(packet, missing, packet_hash)
    assert any("six Research Gate dimensions" in error for error in errors)


def test_research_gate_accepts_job_directory_and_rejects_changed_packet(tmp_path: Path) -> None:
    packet = _packet()
    packet_path = tmp_path / "research_packet.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    packet_hash = validate_research_packet(packet)["artifact_hash"]
    rubric = _rubric(packet_hash)
    assert validate_research_approval(tmp_path, rubric, packet_hash) == []

    changed = copy.deepcopy(packet)
    changed["title"] = "Changed after review"
    packet_path.write_text(json.dumps(changed), encoding="utf-8")
    errors = validate_research_approval(tmp_path, rubric, packet_hash)
    assert any("does not match current" in error for error in errors)
