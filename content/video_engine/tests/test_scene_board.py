from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from content.video_engine.src.services.director import validate_director_proposal
from content.video_engine.src.services.provisional_coverage import (
    compile_provisional_coverage,
)
from content.video_engine.src.services.scene_board import (
    SceneBoardError,
    build_board,
    render_board_html,
    render_scene_board,
)
from content.video_engine.src.services.visual_prompt_pack import compile_visual_prompt_pack
from content.video_engine.tests.conftest import build_candidate_batch, build_proposal

_REMOTE_URL = re.compile(r"""(?:src|href)\s*=\s*["'](?:https?:)?//""", re.IGNORECASE)


@pytest.fixture()
def artifacts(paste_brief, paste_attestation, tmp_path):
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
    return {
        "coverage": coverage,
        "pack": pack,
        "batch": batch,
        "brief": paste_brief,
        "attestation": attestation,
    }


def test_every_slot_gets_an_auto_selected_default(artifacts):
    board = build_board(**artifacts)

    assert board["slot_count"] > 0
    assert all(row["auto_selected"] for row in board["slots"])
    assert all(row["selected_candidate_id"] for row in board["slots"])


def test_a_clean_board_needs_no_operator_decisions(artifacts):
    board = build_board(**artifacts)

    assert board["exception_count"] == 0


def test_auto_selection_is_deterministic(artifacts):
    first = build_board(**artifacts)
    second = build_board(**artifacts)

    assert first["artifact_hash"] == second["artifact_hash"]


def test_qc_flagged_default_becomes_an_exception(artifacts, tmp_path):
    pack = artifacts["pack"]
    first_slot = pack["groups"][0]["slot_id"]
    flagged_id = f"{first_slot}-v0".lower().replace("_", "-")
    artifacts["batch"] = build_candidate_batch(
        pack,
        job_root=tmp_path,
        flags={flagged_id: ["identity_anchor_violation"]},
    )
    board = build_board(**artifacts)

    row = next(r for r in board["slots"] if r["slot_id"] == first_slot)
    # A clean sibling exists, so the flagged variant is not chosen at all.
    assert row["selected_candidate_id"] != flagged_id
    assert row["exceptions"] == []


def test_all_variants_flagged_surfaces_the_slot_for_review(artifacts, tmp_path):
    pack = artifacts["pack"]
    slot_id = pack["groups"][0]["slot_id"]
    prefix = slot_id.lower().replace("_", "-")
    artifacts["batch"] = build_candidate_batch(
        pack,
        job_root=tmp_path,
        flags={f"{prefix}-v{index}": ["suspected_generated_text"] for index in range(3)},
    )
    board = build_board(**artifacts)

    row = next(r for r in board["slots"] if r["slot_id"] == slot_id)
    assert "suspected_generated_text" in row["exceptions"]
    assert board["exception_count"] == 1


def test_low_confidence_default_is_flagged(artifacts, tmp_path):
    pack = artifacts["pack"]
    prefix = pack["groups"][0]["slot_id"].lower().replace("_", "-")
    artifacts["batch"] = build_candidate_batch(
        pack,
        job_root=tmp_path,
        confidence={f"{prefix}-v{index}": 0.2 for index in range(3)},
    )
    board = build_board(**artifacts)

    assert any("low_confidence" in row["exceptions"] for row in board["slots"])


def test_slot_with_no_candidates_is_flagged_not_silently_dropped(artifacts):
    dropped = artifacts["pack"]["groups"][0]["slot_id"]
    artifacts["batch"]["items"] = [
        item for item in artifacts["batch"]["items"] if item["slot_id"] != dropped
    ]
    board = build_board(**artifacts)

    row = next(r for r in board["slots"] if r["slot_id"] == dropped)
    assert row["exceptions"] == ["no_candidate"]
    assert row["selected_candidate_id"] is None


def test_exceptions_render_first(artifacts, tmp_path):
    pack = artifacts["pack"]
    last_slot = pack["groups"][-1]["slot_id"]
    prefix = last_slot.lower().replace("_", "-")
    artifacts["batch"] = build_candidate_batch(
        pack,
        job_root=tmp_path,
        flags={f"{prefix}-v{index}": ["identity_anchor_violation"] for index in range(3)},
    )
    markup = render_board_html(build_board(**artifacts))

    first_section = markup.index('<section class="slot')
    assert f'id="slot-{last_slot}"' in markup[first_section : first_section + 400]


def test_page_is_offline_and_uses_relative_image_paths(artifacts, tmp_path):
    summary = render_scene_board(**artifacts, output_dir=tmp_path / "job")
    markup = Path(summary["board_path"]).read_text(encoding="utf-8")

    assert not _REMOTE_URL.search(markup), "board must not reference any remote host"
    assert 'src="assets/' in markup


def test_tier_three_renders_disabled_video_slots(artifacts, tmp_path):
    summary = render_scene_board(**artifacts, output_dir=tmp_path / "job")
    markup = Path(summary["board_path"]).read_text(encoding="utf-8")

    assert markup.count("Tier 3") == summary["slot_count"]
    assert "no provider bound" in markup


def test_board_json_is_written_beside_the_page(artifacts, tmp_path):
    summary = render_scene_board(**artifacts, output_dir=tmp_path / "job")
    payload = json.loads(Path(summary["board_json_path"]).read_text(encoding="utf-8"))

    assert payload["schema_version"] == "scene_board.v1"
    assert payload["coverage_hash"] == artifacts["coverage"]["artifact_hash"]


def test_estimated_timing_is_disclosed_on_the_page(artifacts, tmp_path):
    summary = render_scene_board(**artifacts, output_dir=tmp_path / "job")
    markup = Path(summary["board_path"]).read_text(encoding="utf-8")

    assert "render clock still comes from audio" in markup


def test_tier_one_shows_the_attested_source(artifacts, tmp_path):
    summary = render_scene_board(**artifacts, output_dir=tmp_path / "job")
    markup = Path(summary["board_path"]).read_text(encoding="utf-8")

    assert "internal-notes/trading-energy-drains.md" in markup
    assert "decks/energy-drains.pdf" in markup


def test_empty_coverage_is_rejected(artifacts):
    artifacts["coverage"] = {**artifacts["coverage"], "slots": []}

    with pytest.raises(SceneBoardError):
        build_board(**artifacts)
