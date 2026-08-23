from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.director import (
    DirectorError,
    compile_director_request,
    load_recorded_proposal,
    record_director_proposal,
    validate_director_proposal,
)
from content.video_engine.tests.conftest import build_proposal


def test_request_carries_the_response_schema_and_the_rules(paste_brief):
    request = compile_director_request(paste_brief)

    assert request["response_schema"]["properties"]["schema_version"]["const"] == (
        "director_proposal.v1"
    )
    assert request["brief_hash"] == paste_brief["artifact_hash"]
    assert request["suggested_beat_count"] >= 1
    joined = " ".join(request["rules"])
    assert "Never place text inside a plate" in joined
    assert "silhouette" in joined


def test_stick_explainer_defers_on_screen_copy_to_the_operator(paste_brief):
    # Model-written humour is unreliable, so this lane proposes structure only.
    request = compile_director_request(paste_brief)

    assert request["operator_writes_on_screen_copy"] is True


def test_valid_proposal_round_trips(paste_brief):
    validated = validate_director_proposal(build_proposal(paste_brief), brief=paste_brief)

    assert validated["lane"] == paste_brief["lane"]
    assert len(validated["beats"]) >= 3
    assert validated["artifact_hash"]


def test_director_may_not_rewrite_the_script(paste_brief):
    proposal = build_proposal(paste_brief)
    proposal["beats"][1]["narration_text"] = "A punchier line the model preferred."

    with pytest.raises(DirectorError) as excinfo:
        validate_director_proposal(proposal, brief=paste_brief)

    assert any("never rewrite" in error for error in excinfo.value.errors)


def test_truncated_coverage_is_named_as_truncation(paste_brief):
    proposal = build_proposal(paste_brief)
    proposal["beats"] = proposal["beats"][:-1]

    with pytest.raises(DirectorError) as excinfo:
        validate_director_proposal(proposal, brief=paste_brief)

    assert any("truncated" in error for error in excinfo.value.errors)


def test_added_narration_is_named_as_addition(paste_brief):
    proposal = build_proposal(paste_brief)
    proposal["beats"].append(
        {
            "beat_id": "extra",
            "act": "cta",
            "narration_text": "Subscribe for more trading psychology.",
            "visual_intent": "end card",
            "semantic_purpose": "transition",
            "motion_recipe": "type_build",
            "on_screen_text": None,
            "copy_deferred": True,
        }
    )

    with pytest.raises(DirectorError) as excinfo:
        validate_director_proposal(proposal, brief=paste_brief)

    assert any("beyond the script" in error for error in excinfo.value.errors)


def test_operator_copy_lane_rejects_model_written_on_screen_text(paste_brief):
    proposal = build_proposal(paste_brief, copy_deferred=False)

    with pytest.raises(DirectorError) as excinfo:
        validate_director_proposal(proposal, brief=paste_brief)

    assert any("requires copy_deferred" in error for error in excinfo.value.errors)


def test_brief_hash_mismatch_is_rejected(paste_brief):
    proposal = build_proposal(paste_brief)
    proposal["brief_hash"] = "b" * 64

    with pytest.raises(DirectorError) as excinfo:
        validate_director_proposal(proposal, brief=paste_brief)

    assert any("brief_hash" in error for error in excinfo.value.errors)


def test_duplicate_beat_ids_are_rejected(paste_brief):
    proposal = build_proposal(paste_brief)
    proposal["beats"][1]["beat_id"] = proposal["beats"][0]["beat_id"]

    with pytest.raises(DirectorError) as excinfo:
        validate_director_proposal(proposal, brief=paste_brief)

    assert any("duplicates" in error for error in excinfo.value.errors)


def test_recorded_proposal_replays_without_resoliciting(paste_brief, tmp_path):
    job = tmp_path / "job"
    summary = record_director_proposal(
        build_proposal(paste_brief), brief=paste_brief, output_dir=job
    )
    replayed = load_recorded_proposal(job)

    assert replayed is not None
    assert replayed["artifact_hash"] == summary["proposal_hash"]


def test_recording_is_byte_identical_across_runs(paste_brief, tmp_path):
    proposal = build_proposal(paste_brief)
    first = record_director_proposal(proposal, brief=paste_brief, output_dir=tmp_path / "a")
    second = record_director_proposal(proposal, brief=paste_brief, output_dir=tmp_path / "b")

    assert Path(first["proposal_path"]).read_bytes() == Path(second["proposal_path"]).read_bytes()


def test_engine_does_not_call_a_provider(paste_brief, monkeypatch):
    # The model sits upstream of the pipeline. If this module ever opened a
    # socket, the request compile would fail here.
    import socket

    def _forbidden(*args, **kwargs):  # pragma: no cover - only runs on regression
        raise AssertionError("director must not make network calls")

    monkeypatch.setattr(socket.socket, "connect", _forbidden)
    request = compile_director_request(paste_brief)

    assert json.dumps(request)
