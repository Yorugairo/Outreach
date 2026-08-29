from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECT = REPO_ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
BUILDER_PATH = REPO_ROOT / "content/video_engine/scripts/build_current_bubble_six_minute_p32_demo.py"


def _builder_module():
    spec = importlib.util.spec_from_file_location("p33_builder", BUILDER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p33_first_five_minute_factual_holds_have_evidence_or_an_exemption() -> None:
    builder = _builder_module()
    coverage = json.loads(builder.COVERAGE_PATH.read_text(encoding="utf-8"))
    worlds = builder._build_world_beats(coverage)
    evidence = builder._build_evidence_beats(coverage, worlds)
    records = builder._validate_first_five_evidence_obligations(worlds, evidence)

    assert not [record for record in records if record["status"] == "missing"]
    bakery = next(record for record in records if record["asset_id"] == "fixed-oven-capacity-wedding-cake-v1")
    assert bakery["status"] == "exempt"
    assert bakery["exemption"]["permitted_future_evidence"] == "silicon-antidote-s09-teacher-stamped"


def test_p33_replaces_weak_opening_plates_and_adds_exact_evidence() -> None:
    builder = _builder_module()
    coverage = json.loads(builder.COVERAGE_PATH.read_text(encoding="utf-8"))
    worlds = builder._build_world_beats(coverage)
    evidence = builder._build_evidence_beats(coverage, worlds)

    opening_worlds = [world for world in worlds if world["start_s"] < builder.FIRST_FIVE_MINUTES_SECONDS]
    assert not {"wrong-bubble-elevators-v2", "belief-versus-support-v2"}.intersection(
        world["asset_id"] for world in opening_worlds
    )
    assert any(world["asset_id"] == "two-elevator-mechanism-v1" for world in opening_worlds)
    assert {
        "silicon-reality-gap-s12-teacher-stamped",
        "silicon-antidote-s14-teacher-stamped",
        "silicon-antidote-s02-teacher-stamped",
        "memory-supercycle-s06-teacher-stamped",
    }.issubset({item["asset_id"] for item in evidence})
    assert all(item["end_s"] - item["start_s"] <= builder.EVIDENCE_HOLD_SECONDS + 1e-6 for item in evidence)
    assert any(abs((item["end_s"] - item["start_s"]) - builder.EVIDENCE_HOLD_SECONDS) < 1e-6 for item in evidence)
    assert all(item["sourceCrop"] == builder.TEACHER_STAMP_SAFE_SOURCE_CROP for item in evidence)
    ordered = sorted(evidence, key=lambda item: item["start_s"])
    for world_id in {item["world_id"] for item in ordered}:
        world_evidence = [item for item in ordered if item["world_id"] == world_id]
        assert all(
            right["start_s"] - left["start_s"] + 1e-6 >= builder.EVIDENCE_REVEAL_SECONDS + builder.EVIDENCE_REVEAL_GAP_SECONDS
            for left, right in zip(world_evidence, world_evidence[1:])
        )
    assert max(
        sum(item["start_s"] <= point < item["end_s"] for item in evidence)
        for point in {item["start_s"] for item in evidence}
    ) <= builder.MAX_SIMULTANEOUS_EVIDENCE


def test_p33_obligation_fails_without_required_evidence() -> None:
    builder = _builder_module()
    coverage = json.loads(builder.COVERAGE_PATH.read_text(encoding="utf-8"))
    worlds = builder._build_world_beats(coverage)
    evidence = builder._build_evidence_beats(coverage, worlds)
    without_safe_index = [item for item in evidence if item["asset_id"] != "silicon-reality-gap-s12-teacher-stamped"]
    records = builder._validate_first_five_evidence_obligations(worlds, without_safe_index)

    assert any(record["asset_id"] == "sentence-native-beat-01-013-hidden-safe-index-loop-v1" and record["status"] == "missing" for record in records)
