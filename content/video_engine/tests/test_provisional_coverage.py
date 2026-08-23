from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.director import validate_director_proposal
from content.video_engine.src.services.provisional_coverage import (
    ProvisionalCoverageError,
    assert_render_ready,
    compile_and_write,
    compile_provisional_coverage,
    duration_drift_ratio,
)
from content.video_engine.tests.conftest import build_proposal


@pytest.fixture()
def proposal(paste_brief):
    return validate_director_proposal(build_proposal(paste_brief), brief=paste_brief)


def test_coverage_is_marked_estimated_and_bound_to_the_proposal(paste_brief, proposal):
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)

    assert coverage["timing_basis"] == "estimated"
    assert coverage["source_artifact_kind"] == "director_proposal"
    assert coverage["source_shot_plan_hash"] == proposal["artifact_hash"]


def test_every_slot_duration_derives_from_word_count_over_wpm(paste_brief, proposal):
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)
    wpm = paste_brief["words_per_minute"]

    for slot in coverage["slots"]:
        words = len(slot["narration_excerpt"].split())
        assert slot["duration_s"] == pytest.approx(words / wpm * 60.0, abs=0.5)


def test_total_duration_matches_the_brief_estimate_within_one_percent(paste_brief, proposal):
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)

    assert duration_drift_ratio(coverage, paste_brief) <= 0.01


def test_no_slot_exceeds_the_coverage_contract_cap(paste_brief, proposal):
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)

    assert all(slot["duration_s"] <= 8.0 for slot in coverage["slots"])


def test_long_beats_split_rather_than_overrun_the_hold(paste_brief, proposal):
    # One beat carrying the whole script must become several slots, not one long one.
    single = dict(proposal)
    single["beats"] = [
        {
            **proposal["beats"][0],
            "narration_text": paste_brief["script"]["text"],
        }
    ]
    coverage = compile_provisional_coverage(single, brief=paste_brief)

    assert coverage["slot_count"] > 1
    assert all(slot["duration_s"] <= paste_brief["target_slot_hold_s"] + 0.001
               for slot in coverage["slots"])


def test_render_timing_refuses_estimated_coverage(paste_brief, proposal):
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)

    with pytest.raises(ProvisionalCoverageError) as excinfo:
        assert_render_ready(coverage)

    assert any("canonical" in error for error in excinfo.value.errors)


def test_render_timing_accepts_canonical_coverage(paste_brief, proposal):
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)
    coverage["timing_basis"] = "canonical"

    assert_render_ready(coverage)


def test_lane_drives_the_visual_archetype(paste_brief, proposal):
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)
    archetypes = {slot["visual_archetype"] for slot in coverage["slots"]}

    assert "lofi_stick_figure_comic" in archetypes


def test_slot_ids_are_unique_and_parented_to_beats(paste_brief, proposal):
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)
    slot_ids = [slot["slot_id"] for slot in coverage["slots"]]
    beat_ids = {beat["beat_id"] for beat in proposal["beats"]}

    assert len(slot_ids) == len(set(slot_ids))
    assert all(slot["parent_shot_id"] in beat_ids for slot in coverage["slots"])


def test_deferred_copy_survives_into_the_slot(paste_brief, proposal):
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)

    assert all(slot["copy_deferred"] is True for slot in coverage["slots"])
    assert any(
        event["kind"] == "type_in_deferred"
        for slot in coverage["slots"]
        for event in slot["micro_events"]
    )


def test_compile_and_write_persists_a_schema_valid_artifact(paste_brief, proposal, tmp_path):
    summary = compile_and_write(proposal, brief=paste_brief, output_dir=tmp_path / "job")
    payload = json.loads(Path(summary["coverage_path"]).read_text(encoding="utf-8"))

    assert payload["schema_version"] == "editorial_coverage.v1"
    assert summary["timing_basis"] == "estimated"
    assert summary["slot_count"] == payload["slot_count"]


def test_empty_proposal_is_rejected(paste_brief, proposal):
    empty = dict(proposal)
    empty["beats"] = []

    with pytest.raises(ProvisionalCoverageError):
        compile_provisional_coverage(empty, brief=paste_brief)
