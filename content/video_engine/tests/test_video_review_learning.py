from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.video_review_learning import (
    VideoReviewValidationError,
    aggregate_review_learnings,
    compile_review_packet,
    file_sha256,
    review_requires_prp,
    validate_artifact,
    with_artifact_hash,
)


ZERO_HASH = "0" * 64


def _finding(
    *,
    finding_id: str = "finding-001",
    scope: str = "episode",
    status: str = "open",
    recurrence_count: int = 1,
    promotion_state: str = "observation",
) -> dict:
    return {
        "finding_id": finding_id,
        "start_s": 1.0,
        "end_s": 3.0,
        "transcript_excerpt": "The mechanism begins here.",
        "evidence_frames": [
            {"path": "evidence/frame.jpg", "sha256": "a" * 64, "timestamp_s": 2.0}
        ],
        "kind": "semantic_mismatch",
        "scope": scope,
        "severity": "high",
        "symptom": "The visual does not explain the spoken mechanism.",
        "root_cause": "The fallback asset was selected without an exact call cue.",
        "impact": "The viewer receives motion without explanatory value.",
        "proposed_fix": "Replace the fallback with a cue-specific mechanism state.",
        "acceptance": "A focused rewatch shows the spoken relationship on screen.",
        "confidence": "confirmed",
        "recurrence_key": "require-exact-semantic-call-cue",
        "recurrence_count": recurrence_count,
        "learning_trigger": "When selecting an asset for a narration cue",
        "learning_action": "Require the asset to depict the cue's subject and relationship",
        "requires_human_decision": False,
        "promotion_state": promotion_state,
        "status": status,
    }


def _review(
    *,
    review_id: str = "review-001",
    episode_id: str = "episode-001",
    lane_id: str = "finance",
    finding: dict | None = None,
) -> dict:
    return with_artifact_hash(
        {
            "schema_version": "video_watch_review.v1",
            "review_id": review_id,
            "project_id": "outreach-program",
            "lane_id": lane_id,
            "episode_id": episode_id,
            "created_at": "2026-08-08T00:00:00Z",
            "reviewer": "operator-and-watch",
            "review_purpose": "Review the current composition.",
            "watch_detail": "balanced",
            "source": {
                "kind": "local",
                "uri": "renders/review.mp4",
                "sha256": "b" * 64,
                "duration_s": 10.0,
            },
            "transcript": None,
            "summary": {
                "assessment": "The render needs one semantic correction.",
                "strengths": ["Narration is clear."],
                "priority_issues": ["Visual-semantic fit."],
                "overall_state": "revision_required",
            },
            "findings": [finding or _finding()],
            "operator_decision": {"state": "draft", "approved_at": None, "notes": ""},
        }
    )


def _draft(tmp_path: Path) -> Path:
    source = tmp_path / "review.mp4"
    source.write_bytes(b"review video")
    transcript = tmp_path / "transcript.txt"
    transcript.write_text("The mechanism begins here.", encoding="utf-8")
    frame = tmp_path / "frame.jpg"
    frame.write_bytes(b"selected frame")
    payload = _review()
    payload["source"] = {
        "kind": "local",
        "uri": source.name,
        "sha256": ZERO_HASH,
        "duration_s": 10.0,
    }
    payload["transcript"] = {
        "path": transcript.name,
        "sha256": ZERO_HASH,
        "source": "manual",
    }
    payload["findings"][0]["evidence_frames"] = [
        {"path": frame.name, "sha256": ZERO_HASH, "timestamp_s": 2.0}
    ]
    payload["artifact_hash"] = ZERO_HASH
    draft = tmp_path / "draft.json"
    draft.write_text(json.dumps(payload), encoding="utf-8")
    return draft


def test_compile_review_packet_copies_selected_evidence_and_writes_durable_outputs(
    tmp_path: Path,
) -> None:
    draft = _draft(tmp_path)
    output_dir = tmp_path / "packet"

    outputs = compile_review_packet(draft, output_dir, repo_root=tmp_path)

    assert set(outputs) == {
        "review_json",
        "review_markdown",
        "edit_delta",
        "learning_json",
        "learning_markdown",
    }
    review = json.loads(outputs["review_json"].read_text(encoding="utf-8"))
    validate_artifact(review)
    assert review["source"]["sha256"] == file_sha256(tmp_path / "review.mp4")
    assert review["transcript"]["path"] == "evidence/transcript.txt"
    frame_path = output_dir / review["findings"][0]["evidence_frames"][0]["path"]
    assert frame_path.read_bytes() == b"selected frame"
    assert "PRP recommended: `no`" in outputs["review_markdown"].read_text(encoding="utf-8")
    assert "Keep the correction episode-local" in outputs["edit_delta"].read_text(encoding="utf-8")


def test_compile_rejects_output_outside_declared_repository_root(tmp_path: Path) -> None:
    draft = _draft(tmp_path)
    with pytest.raises(VideoReviewValidationError, match="must stay inside repository root"):
        compile_review_packet(draft, tmp_path / "packet", repo_root=tmp_path / "different-root")


def test_review_rejects_invalid_timing_and_stale_hash() -> None:
    review = _review()
    review["findings"][0]["end_s"] = 0.5
    with pytest.raises(VideoReviewValidationError, match="artifact_hash is stale"):
        validate_artifact(review)

    review = with_artifact_hash({key: value for key, value in review.items() if key != "artifact_hash"})
    with pytest.raises(VideoReviewValidationError, match="end_s must be greater"):
        validate_artifact(review)


def test_scope_routes_episode_delta_and_systemic_prp() -> None:
    assert review_requires_prp(_review()) is False
    assert review_requires_prp(_review(finding=_finding(scope="engine"))) is True


def test_learning_promotes_repeated_lane_pattern_but_keeps_operator_gate() -> None:
    first = _review(review_id="review-001", episode_id="episode-001")
    second = _review(review_id="review-002", episode_id="episode-002")

    learning = aggregate_review_learnings([first, second])

    candidate = learning["candidates"][0]
    assert candidate["confidence"] == 0.7
    assert candidate["distinct_episode_count"] == 2
    assert candidate["distinct_lane_count"] == 1
    assert candidate["recommended_destination"] == "lane_skill"
    assert candidate["promotion_state"] == "candidate_rule"
    assert candidate["operator_gate"] == "required"


def test_learning_does_not_count_duplicate_review_input_as_recurrence() -> None:
    review = _review()
    candidate = aggregate_review_learnings([review, review])["candidates"][0]
    assert candidate["confidence"] == 0.3
    assert candidate["distinct_episode_count"] == 1
    assert len(candidate["observations"]) == 1


def test_learning_requires_cross_lane_evidence_for_global_instinct() -> None:
    global_finding = _finding(scope="global")
    first = _review(review_id="review-001", episode_id="episode-001", lane_id="finance", finding=global_finding)
    second = _review(
        review_id="review-002",
        episode_id="episode-002",
        lane_id="martial-history",
        finding=_finding(scope="global"),
    )

    candidate = aggregate_review_learnings([first, second])["candidates"][0]

    assert candidate["confidence"] == 0.8
    assert candidate["recommended_destination"] == "global_instinct"
    assert candidate["operator_gate"] == "required"


def test_approved_learning_satisfies_operator_gate() -> None:
    finding = _finding(promotion_state="approved_rule")
    candidate = aggregate_review_learnings([_review(finding=finding)])["candidates"][0]
    assert candidate["promotion_state"] == "approved_rule"
    assert candidate["operator_gate"] == "satisfied"


def test_recurrence_key_rejects_conflicting_actions() -> None:
    first = _review(review_id="review-001")
    second_finding = _finding(finding_id="finding-002")
    second_finding["learning_action"] = "Use a conflicting action"
    second = _review(review_id="review-002", episode_id="episode-002", finding=second_finding)

    with pytest.raises(VideoReviewValidationError, match="conflicting trigger, action, or kind"):
        aggregate_review_learnings([first, second])
