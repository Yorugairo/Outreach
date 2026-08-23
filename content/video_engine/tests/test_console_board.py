"""Interactive scene board routes.

The board is built by ``scene_board.build_board`` and selections are recorded
through ``scene_selection.record_scene_selection`` — these tests hold the route
to being a window onto those services, not a second implementation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from content.video_engine.console.app import create_app
from content.video_engine.console.routes import board as board_routes
from content.video_engine.console.settings import load_settings
from content.video_engine.src.services.director import validate_director_proposal
from content.video_engine.src.services.provisional_coverage import (
    compile_provisional_coverage,
)
from content.video_engine.src.services.scene_board import build_board, render_board_html
from content.video_engine.src.services.visual_prompt_pack import compile_visual_prompt_pack
from content.video_engine.tests.conftest import build_candidate_batch, build_proposal


def _client(tmp_path: Path) -> TestClient:
    app = create_app(load_settings(project_root=tmp_path))
    # The parent wires the router into ``app.py``; the tests wire it the same way.
    app.include_router(board_routes.router)
    return TestClient(app)


@pytest.fixture()
def job_dir(paste_brief, paste_attestation, tmp_path) -> Path:
    """A job directory holding the five artifacts by their conventional names."""

    proposal = validate_director_proposal(build_proposal(paste_brief), brief=paste_brief)
    coverage = compile_provisional_coverage(proposal, brief=paste_brief)
    pack = compile_visual_prompt_pack(coverage, lane="stick_explainer")

    job = tmp_path / "job"
    job.mkdir(exist_ok=True)
    batch = build_candidate_batch(pack, job_root=job)

    attestation = {
        **paste_attestation,
        "schema_version": "source_attestation.v1",
        "script_sha256": "a" * 64,
        "artifact_hash": "b" * 64,
    }

    (job / "director_brief.json").write_text(json.dumps(paste_brief), encoding="utf-8")
    (job / "source_attestation.json").write_text(json.dumps(attestation), encoding="utf-8")
    (job / "provisional_coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
    (job / "visual_prompt_pack.json").write_text(json.dumps(pack), encoding="utf-8")
    generated = job / "generated_visuals"
    generated.mkdir(exist_ok=True)
    (generated / "candidate_batch.json").write_text(json.dumps(batch), encoding="utf-8")
    return job


def _artifacts(job: Path) -> dict[str, Any]:
    return {
        "coverage": job / "provisional_coverage.json",
        "pack": job / "visual_prompt_pack.json",
        "batch": job / "generated_visuals" / "candidate_batch.json",
        "brief": job / "director_brief.json",
        "attestation": job / "source_attestation.json",
    }


def _flag_all_variants_of_last_slot(job: Path) -> str:
    """Rewrite the batch so the last slot has no clean candidate.

    The last slot, deliberately: the builder keeps script order, so a leading
    flagged slot would prove nothing about the flagged-first partition.
    """

    batch_path = job / "generated_visuals" / "candidate_batch.json"
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    slot_id = batch["items"][-1]["slot_id"]
    for item in batch["items"]:
        if item["slot_id"] == slot_id:
            item["qc_flags"] = ["suspected_generated_text"]
    batch_path.write_text(json.dumps(batch), encoding="utf-8")
    return slot_id


def test_without_a_job_the_empty_state_documents_the_filename_convention(tmp_path):
    body = _client(tmp_path).get("/board").text

    assert "director_brief.json" in body
    assert "provisional_coverage.json" in body
    assert "visual_prompt_pack.json" in body
    assert "candidate_batch.json" in body


def test_the_board_renders_the_service_build_with_defaults_intact(tmp_path, job_dir):
    board = build_board(**_artifacts(job_dir))

    body = _client(tmp_path).get("/board", params={"job": str(job_dir)}).text

    for row in board["slots"]:
        assert row["slot_id"] in body
        assert row["selected_candidate_id"] in body  # the auto-selected default
    assert "(auto default)" in body


def test_flagged_slots_sort_first(tmp_path, job_dir):
    flagged_slot = _flag_all_variants_of_last_slot(job_dir)
    board = build_board(**_artifacts(job_dir))
    clean_slot = next(
        row["slot_id"] for row in board["slots"] if not row["exceptions"]
    )
    # In builder order the flagged slot comes last; it only leads if the view
    # applies the flagged-first partition.
    assert board["slots"][-1]["slot_id"] == flagged_slot

    body = _client(tmp_path).get("/board", params={"job": str(job_dir)}).text

    assert body.index(f'id="slot-{flagged_slot}"') < body.index(f'id="slot-{clean_slot}"')
    assert "needs review" in body


def test_estimated_timing_is_visible_chrome_with_the_audio_clock_warning(
    tmp_path, job_dir
):
    body = _client(tmp_path).get("/board", params={"job": str(job_dir)}).text

    assert "timing_basis: estimated" in body
    assert "the render clock still comes from audio" in body


def test_changing_a_selection_is_recorded_through_the_selection_service(
    tmp_path, job_dir
):
    client = _client(tmp_path)
    board = build_board(**_artifacts(job_dir))
    row = board["slots"][0]
    default = row["selected_candidate_id"]
    other = next(c["id"] for c in row["candidates"] if c["id"] != default)

    r = client.post(
        "/board/select",
        data={
            "job": str(job_dir),
            "slot_id": row["slot_id"],
            "candidate_id": other,
            "reviewed_by": "operator-a",
        },
        follow_redirects=False,
    )

    assert r.status_code == 303
    review = json.loads(
        (job_dir / "selection" / "asset_selection_review.json").read_text(encoding="utf-8")
    )
    assert review["schema_version"] == "asset_selection_review.v1"
    assert review["reviewed_by"] == "operator-a"
    assert review["approved"] is False  # Gate A/B stay operator actions elsewhere
    entry = next(e for e in review["selections"] if e["slot_id"] == row["slot_id"])
    assert entry["candidate_id"] == other
    assert entry["selection_source"] == "operator"
    # Every untouched slot still records its auto default.
    assert row["slot_id"] not in review["auto_selected_slot_ids"]
    assert len(review["selections"]) == board["slot_count"]
    # The intents artifact is the service's, written alongside.
    assert (job_dir / "selection" / "video_intents.json").is_file()

    body = client.get("/board", params={"job": str(job_dir)}).text
    assert "operator-selected" in body


def test_an_invalid_selection_surfaces_the_service_error_and_records_nothing(
    tmp_path, job_dir
):
    client = _client(tmp_path)
    board = build_board(**_artifacts(job_dir))
    row = board["slots"][0]

    r = client.post(
        "/board/select",
        data={
            "job": str(job_dir),
            "slot_id": row["slot_id"],
            "candidate_id": "not-a-candidate",
            "reviewed_by": "operator-a",
        },
    )

    assert "not-a-candidate" in r.text and "not" in r.text  # service text, verbatim
    assert not (job_dir / "selection").exists()
    # The rejected choice is not held: the board shows no operator selection.
    body = client.get("/board", params={"job": str(job_dir)}).text
    assert "operator-selected" not in body


def test_the_static_board_route_serves_render_board_html_unchanged(tmp_path, job_dir):
    expected = render_board_html(build_board(**_artifacts(job_dir)))

    r = _client(tmp_path).get("/board/static", params={"job": str(job_dir)})

    assert r.status_code == 200
    assert r.text == expected


def test_a_job_directory_with_missing_artifacts_is_reported_by_name(tmp_path, job_dir):
    (job_dir / "visual_prompt_pack.json").unlink()

    body = _client(tmp_path).get("/board", params={"job": str(job_dir)}).text

    assert "visual_prompt_pack.json" in body
    assert "Traceback" not in body


def test_a_missing_job_directory_is_reported_not_a_stack_trace(tmp_path):
    body = _client(tmp_path).get("/board", params={"job": str(tmp_path / "nope")}).text

    assert "job directory not found" in body


def test_the_route_never_writes_the_board_artifact_itself(tmp_path, job_dir):
    client = _client(tmp_path)
    before = sorted(p.relative_to(job_dir) for p in job_dir.rglob("*") if p.is_file())

    client.get("/board", params={"job": str(job_dir)})
    client.get("/board/static", params={"job": str(job_dir)})

    after = sorted(p.relative_to(job_dir) for p in job_dir.rglob("*") if p.is_file())
    assert after == before  # rendering writes nothing; only recording does
