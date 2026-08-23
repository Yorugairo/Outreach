from __future__ import annotations

import copy
import json
from pathlib import Path

from content.video_engine.src.services.full_episode_evidence_coverage import (
    compile_full_episode_evidence_coverage,
    validate_full_episode_evidence_coverage,
    write_full_episode_evidence_coverage,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECT = REPO_ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"


def test_compiles_the_full_canonical_episode_deterministically() -> None:
    first = compile_full_episode_evidence_coverage(PROJECT)
    second = compile_full_episode_evidence_coverage(PROJECT)

    assert first == second
    assert validate_full_episode_evidence_coverage(first) == []
    assert first["summary"] == {
        "duration_s": 980.806,
        "word_count": 2445,
        "cue_count": 290,
        "scene_count": 11,
        "evidence_asset_count": 95,
        "production_ready_source_surface_count": 86,
        "context_crop_count": 9,
        "composition_world_plate_count": 76,
        "base_resolution_segment_count": 60,
        "over_twenty_second_hold_count": 14,
        "cadence_turn_count": 19,
        "new_world_art_gap_count": 1,
        "evidence_status_counts": {"existing_context_needed": 25, "manual_only": 161, "source_pack_needed": 104},
    }
    assert all(cue["requires_editorial_acceptance"] for cue in first["cues"])
    assert all(cue["maximum_simultaneous_evidence"] == 2 for cue in first["cues"])
    assert all(cue["maximum_sequential_evidence"] == 3 for cue in first["cues"])
    assert {turn["state"] for turn in first["cadence_turns"]} >= {"sentence_native_candidate", "scene_authority_candidate", "new_world_art_gap"}


def test_writes_review_artifacts_and_detects_stale_output(tmp_path: Path) -> None:
    paths = write_full_episode_evidence_coverage(PROJECT, tmp_path)
    payload = json.loads(paths["coverage"].read_text(encoding="utf-8"))

    assert validate_full_episode_evidence_coverage(payload) == []
    assert "Gate A Review" in paths["summary"].read_text(encoding="utf-8")
    contact_sheet = paths["contact_sheet"].read_text(encoding="utf-8")
    assert "World plate first" in contact_sheet
    assert "teacher-stamped-production-visuals" in contact_sheet

    stale = copy.deepcopy(payload)
    stale["summary"]["cue_count"] = 1
    assert "artifact_hash is stale" in validate_full_episode_evidence_coverage(stale)
