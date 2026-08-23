from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.director import validate_director_proposal
from content.video_engine.src.services.provisional_coverage import (
    compile_provisional_coverage,
)
from content.video_engine.src.services.scene_board import build_board
from content.video_engine.src.services.scene_selection import (
    SceneSelectionError,
    build_selection_review,
    build_video_intents,
    record_scene_selection,
)
from content.video_engine.src.services.visual_prompt_pack import compile_visual_prompt_pack
from content.video_engine.tests.conftest import build_candidate_batch, build_proposal


@pytest.fixture()
def board(paste_brief, paste_attestation, tmp_path):
    proposal = validate_director_proposal(build_proposal(paste_brief), brief=paste_brief)
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)
    pack = compile_visual_prompt_pack(coverage, lane="stick_explainer")
    batch = build_candidate_batch(pack, job_root=tmp_path)
    attestation = {
        **paste_attestation,
        "schema_version": "source_attestation.v1",
        "script_sha256": "a" * 64,
        "artifact_hash": "b" * 64,
    }
    return build_board(
        coverage=coverage,
        pack=pack,
        batch=batch,
        brief=paste_brief,
        attestation=attestation,
    )


def test_a_full_board_records_with_zero_operator_input(board):
    review = build_selection_review(board=board, reviewed_by="operator")

    assert len(review["selections"]) == board["slot_count"]
    assert len(review["auto_selected_slot_ids"]) == board["slot_count"]
    assert all(entry["selection_source"] == "auto" for entry in review["selections"])


def test_operator_choice_overrides_only_the_named_slot(board):
    target = board["slots"][0]
    other = next(c["id"] for c in target["candidates"] if c["id"] != target["selected_candidate_id"])
    payload = {"selections": [{"slot_id": target["slot_id"], "candidate_id": other}]}

    review = build_selection_review(board=board, reviewed_by="operator", operator_payload=payload)

    chosen = next(e for e in review["selections"] if e["slot_id"] == target["slot_id"])
    assert chosen["candidate_id"] == other
    assert chosen["selection_source"] == "operator"
    assert len(review["auto_selected_slot_ids"]) == board["slot_count"] - 1


def test_review_validates_against_the_existing_contract(board):
    review = build_selection_review(board=board, reviewed_by="operator")

    assert review["schema_version"] == "asset_selection_review.v1"
    assert review["coverage_hash"] == board["coverage_hash"]
    assert review["candidate_batch_hash"] == board["candidate_batch_hash"]


def test_multiple_explicit_selections_for_one_slot_are_rejected(board):
    slot_id = board["slots"][0]["slot_id"]
    ids = [c["id"] for c in board["slots"][0]["candidates"]][:2]
    payload = {
        "selections": [
            {"slot_id": slot_id, "candidate_id": ids[0]},
            {"slot_id": slot_id, "candidate_id": ids[1]},
        ]
    }

    with pytest.raises(SceneSelectionError) as excinfo:
        build_selection_review(board=board, reviewed_by="operator", operator_payload=payload)

    assert any(slot_id in error and "exactly one" in error for error in excinfo.value.errors)


def test_selection_of_a_candidate_from_another_slot_is_rejected(board):
    foreign = board["slots"][1]["candidates"][0]["id"]
    payload = {"selections": [{"slot_id": board["slots"][0]["slot_id"], "candidate_id": foreign}]}

    with pytest.raises(SceneSelectionError) as excinfo:
        build_selection_review(board=board, reviewed_by="operator", operator_payload=payload)

    assert any("not" in error and "candidates" in error for error in excinfo.value.errors)


def test_unknown_slot_is_rejected(board):
    payload = {"selections": [{"slot_id": "ghost-slot", "candidate_id": "x"}]}

    with pytest.raises(SceneSelectionError) as excinfo:
        build_selection_review(board=board, reviewed_by="operator", operator_payload=payload)

    assert any("unknown slot" in error for error in excinfo.value.errors)


def test_slot_with_no_default_and_no_choice_blocks_the_review(board):
    board["slots"][0]["selected_candidate_id"] = None
    board["slots"][0]["candidates"] = []

    with pytest.raises(SceneSelectionError) as excinfo:
        build_selection_review(board=board, reviewed_by="operator")

    assert any("no selection and no usable default" in error for error in excinfo.value.errors)


def test_approval_is_never_set_by_product_code(board):
    review = build_selection_review(board=board, reviewed_by="operator")

    assert review["approved"] is False


def test_approval_requires_an_explicit_operator_flag(board):
    review = build_selection_review(board=board, reviewed_by="operator", approved=True)

    assert review["approved"] is True
    assert review["reviewed_by"] == "operator"


def test_reviewed_by_is_required(board):
    with pytest.raises(SceneSelectionError):
        build_selection_review(board=board, reviewed_by="  ")


def test_video_intents_bind_no_provider_and_release_no_job(board):
    review = build_selection_review(board=board, reviewed_by="operator")
    intents = build_video_intents(board, review)

    assert intents["intent_count"] == board["slot_count"]
    assert all(intent["provider"] is None for intent in intents["intents"])
    assert all(intent["status"] == "not_requested" for intent in intents["intents"])


def test_record_writes_both_artifacts(board, tmp_path):
    summary = record_scene_selection(
        board=board, output_dir=tmp_path / "job", reviewed_by="operator"
    )
    review = json.loads(Path(summary["review_path"]).read_text(encoding="utf-8"))
    intents = json.loads(Path(summary["video_intents_path"]).read_text(encoding="utf-8"))

    assert summary["auto_selected"] == summary["selection_count"]
    assert summary["operator_selected"] == 0
    assert review["timing_basis"] == "estimated"
    assert intents["schema_version"] == "video_intent.v1"
