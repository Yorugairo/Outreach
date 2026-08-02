from __future__ import annotations

import copy
import hashlib

import pytest

from content.video_engine.src.services.asset_resolver import AssetResolverService
from content.video_engine.src.services.generated_block_images import (
    GeneratedBlockImageError,
    compile_generated_block_plan,
    compile_timestamped_plate_asset_manifest,
    compile_timestamped_plate_plan,
    replace_timestamped_plate_candidate,
    validate_generated_block_batch,
    validate_timestamped_plate_plan,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


def _coverage() -> dict:
    return {
        "schema_version": "editorial_coverage.v1",
        "artifact_hash": "coverage-hash",
        "slots": [
            {
                "slot_id": "history-001-a",
                "narration_excerpt": "One sentence, one plate.",
                "function": "artifact_cold_open",
                "visual_archetype": "period_comic_block",
                "duration_s": 4.0,
                "motion_recipe": "parallax_push",
            },
            {
                "slot_id": "history-001-b",
                "narration_excerpt": "One sentence, one plate.",
                "function": "artifact_cold_open",
                "visual_archetype": "period_comic_block",
                "duration_s": 2.0,
                "motion_recipe": "detail_punch",
            },
        ],
    }


def _batch(tmp_path):
    plan = compile_generated_block_plan(_coverage())
    image = tmp_path / "generated_blocks" / "001.png"
    image.parent.mkdir()
    image.write_bytes(b"original-generated-plate")
    digest = hashlib.sha256(image.read_bytes()).hexdigest()
    block = plan["blocks"][0]
    core = {
        "schema_version": "generated_image_block_batch.v1",
        "provider": "openai-built-in-image-generation",
        "plan_hash": plan["artifact_hash"],
        "one_generated_plate_per_block": True,
        "blocks": [
            {
                **block,
                "path": block["planned_path"],
                "sha256": digest,
                "source_kind": "ai_assisted_illustration",
                "status": "candidate",
            }
        ],
        "policy": {
            "generated_pixels_are_not_evidence": True,
            "factual_overlay_owner": "remotion",
            "provider_output_render_eligible": False,
        },
    }
    batch = {**core, "artifact_hash": canonical_sha256(core)}
    return plan, batch


def _timestamped_coverage() -> dict:
    core = {
        "schema_version": "editorial_coverage.v1",
        "slots": [
            {
                "slot_id": "history-001-a",
                "chapter_id": "chapter-one",
                "start_s": 0.0,
                "duration_s": 2.5,
                "narration_excerpt": "An institution changes the story.",
                "function": "artifact_cold_open",
                "visual_archetype": "period_comic_block",
                "selected_visual_source": "original_illustration",
                "motion_recipe": "locked_hold",
                "parent_shot_id": "history-001",
            },
            {
                "slot_id": "history-001-b",
                "chapter_id": "chapter-one",
                "start_s": 2.5,
                "duration_s": 2.0,
                "narration_excerpt": "The system travels through people and places.",
                "function": "illustrated_reconstruction",
                "visual_archetype": "travel_world",
                "selected_visual_source": "original_illustration",
                "motion_recipe": "detail_punch",
                "parent_shot_id": "history-001",
            },
        ],
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def _prompt_spine() -> dict:
    core = {
        "schema_version": "timestamped_plate_prompt_spine.v1",
        "episode_id": "episode-one",
        "global_continuity": {
            "output": "16:9 landscape production plate",
            "locks": [
                "warm fibrous paper and carved indigo ink",
                "no embedded factual text",
            ],
        },
        "chapters": [
            {
                "chapter_id": "chapter-one",
                "story_world": "a period study and travel world",
                "visual_arc": "institution becomes movement",
                "entry_motif": "paper seal",
                "exit_motif": "route ribbon",
                "character_staging": "reserve the lower-left edge for a cutout learner",
                "recurring_motifs": ["paper seal", "route ribbon"],
            }
        ],
        "shot_sequences": [
            {
                "parent_shot_id": "history-001",
                "plate_directions": [
                    "A quiet institutional gate appears through dawn steam, leaving a calm fact anchor.",
                    "A traveler carries a closed folio from the gate toward a route ribbon.",
                ],
            }
        ],
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def test_plan_groups_continuation_slots_into_one_generated_plate():
    plan = compile_generated_block_plan(_coverage())
    assert plan["block_count"] == 1
    assert plan["blocks"][0]["coverage_slot_ids"] == [
        "history-001-a",
        "history-001-b",
    ]
    assert plan["one_generated_plate_per_block"] is True
    assert "do not place any words" in plan["blocks"][0]["prompt"].casefold()


def test_timestamped_plate_plan_keeps_one_distinct_prompt_per_slot() -> None:
    coverage = _timestamped_coverage()
    spine = _prompt_spine()
    plan = compile_timestamped_plate_plan(coverage, prompt_spine=spine)

    assert plan["plate_count"] == 2
    assert [block["coverage_slot_ids"] for block in plan["blocks"]] == [
        ["history-001-a"],
        ["history-001-b"],
    ]
    assert plan["blocks"][0]["start_s"] == 0.0
    assert plan["blocks"][1]["end_s"] == 4.5
    assert "00:00.000–00:02.500" in plan["blocks"][0]["prompt"]
    assert "distinct" in plan["blocks"][1]["prompt"]
    assert validate_timestamped_plate_plan(
        plan,
        expected_coverage=coverage,
        expected_prompt_spine=spine,
    )["artifact_hash"] == plan["artifact_hash"]


def test_timestamped_plate_plan_rejects_slot_reuse() -> None:
    coverage = _timestamped_coverage()
    plan = compile_timestamped_plate_plan(coverage, prompt_spine=_prompt_spine())
    invalid = copy.deepcopy(plan)
    invalid["blocks"][1]["coverage_slot_ids"] = ["history-001-a"]
    invalid["artifact_hash"] = canonical_sha256(
        {key: value for key, value in invalid.items() if key != "artifact_hash"}
    )

    with pytest.raises(GeneratedBlockImageError, match="reuses timestamp slot"):
        validate_timestamped_plate_plan(invalid)


def test_timestamped_plate_plan_rejects_missing_visual_direction() -> None:
    coverage = _timestamped_coverage()
    plan = compile_timestamped_plate_plan(coverage, prompt_spine=_prompt_spine())
    invalid = copy.deepcopy(plan)
    invalid["blocks"][0]["visual_direction"] = ""
    invalid["artifact_hash"] = canonical_sha256(
        {key: value for key, value in invalid.items() if key != "artifact_hash"}
    )

    with pytest.raises(GeneratedBlockImageError, match="visual_direction"):
        validate_timestamped_plate_plan(invalid)


def test_batch_validator_accepts_hashed_local_plate(tmp_path):
    plan, batch = _batch(tmp_path)
    path = tmp_path / "batch.json"
    path.write_text(__import__("json").dumps(batch), encoding="utf-8")
    validated = validate_generated_block_batch(
        path,
        job_root=tmp_path,
        expected_plan=plan,
    )
    assert validated["artifact_hash"] == batch["artifact_hash"]
    assert validated["blocks"][0]["source_kind"] == "ai_assisted_illustration"


def test_batch_validator_rejects_stale_hash_and_renderable_plate(tmp_path):
    plan, batch = _batch(tmp_path)
    batch["blocks"][0]["render_eligible"] = True
    path = tmp_path / "batch.json"
    path.write_text(__import__("json").dumps(batch), encoding="utf-8")
    with pytest.raises(GeneratedBlockImageError) as exc_info:
        validate_generated_block_batch(path, job_root=tmp_path, expected_plan=plan)
    assert any("render_eligible" in error for error in exc_info.value.errors)


def _timestamped_inventory(tmp_path, plan: dict) -> tuple[dict, object]:
    job_root = tmp_path / "job"
    image_dir = job_root / "plates"
    image_dir.mkdir(parents=True)
    first = image_dir / "001.png"
    second = image_dir / "002.png"
    first.write_bytes(b"original-reviewed-generated-plate")
    second.write_bytes(b"review-only-archive-plate")
    blocks = plan["blocks"]
    items = [
        {
            "order": 1,
            "slot_id": blocks[0]["coverage_slot_ids"][0],
            "start_s": blocks[0]["start_s"],
            "end_s": blocks[0]["end_s"],
            "source_path": "plates/001.png",
            "sha256": hashlib.sha256(first.read_bytes()).hexdigest(),
            "status": "candidate",
            "render_eligible": False,
        },
        {
            "order": 2,
            "slot_id": blocks[1]["coverage_slot_ids"][0],
            "start_s": blocks[1]["start_s"],
            "end_s": blocks[1]["end_s"],
            "source_path": "plates/002.png",
            "sha256": hashlib.sha256(second.read_bytes()).hexdigest(),
            "status": "review_only_archive",
            "render_eligible": False,
        },
    ]
    core = {
        "schema_version": "timestamped_plate_candidate_inventory.v1",
        "plan_hash": plan["artifact_hash"],
        "coverage_plan_hash": plan["coverage_plan_hash"],
        "prompt_spine_hash": plan["prompt_spine_hash"],
        "plate_count": 2,
        "candidate_count": 1,
        "review_only_archive_count": 1,
        "render_eligible": False,
        "items": items,
    }
    return {**core, "artifact_hash": canonical_sha256(core)}, job_root


def test_timestamped_plate_promotion_creates_render_manifest_and_quarantines_archive(
    tmp_path,
) -> None:
    plan = compile_timestamped_plate_plan(
        _timestamped_coverage(), prompt_spine=_prompt_spine()
    )
    inventory, job_root = _timestamped_inventory(tmp_path, plan)

    manifest = compile_timestamped_plate_asset_manifest(
        inventory,
        job_root=job_root,
        project_root=tmp_path,
        expected_plan=plan,
        manifest_id="history-of-bjj-episode-1-timestamped-plates-v1",
        project_id="history-of-bjj",
        episode_id="episode-one",
        approved_by="Operator candidate-pack approval",
        approved_at="2026-08-01",
    )

    assert manifest["review"]["approved_generated_plate_count"] == 1
    assert manifest["review"]["quarantined_archive_count"] == 1
    assert manifest["assets"][0]["render_eligible"] is True
    assert manifest["assets"][0]["path"] == "job/plates/001.png"
    assert manifest["assets"][1]["render_eligible"] is False
    resolved = AssetResolverService(tmp_path, job_root).resolve(manifest)
    assert resolved["asset_ids"] == [manifest["assets"][0]["id"]]
    assert resolved["quarantined_assets"][0]["asset_id"] == manifest["assets"][1]["id"]


def test_timestamped_plate_promotion_rejects_pre_renderable_candidates(tmp_path) -> None:
    plan = compile_timestamped_plate_plan(
        _timestamped_coverage(), prompt_spine=_prompt_spine()
    )
    inventory, job_root = _timestamped_inventory(tmp_path, plan)
    inventory["items"][0]["render_eligible"] = True
    inventory["artifact_hash"] = canonical_sha256(
        {key: value for key, value in inventory.items() if key != "artifact_hash"}
    )

    with pytest.raises(GeneratedBlockImageError, match="render_eligible"):
        compile_timestamped_plate_asset_manifest(
            inventory,
            job_root=job_root,
            project_root=tmp_path,
            expected_plan=plan,
            manifest_id="history-of-bjj-episode-1-timestamped-plates-v1",
            project_id="history-of-bjj",
            episode_id="episode-one",
            approved_by="Operator candidate-pack approval",
            approved_at="2026-08-01",
        )


def test_timestamped_plate_replacement_creates_new_all_original_inventory(
    tmp_path,
) -> None:
    plan = compile_timestamped_plate_plan(
        _timestamped_coverage(), prompt_spine=_prompt_spine()
    )
    inventory, job_root = _timestamped_inventory(tmp_path, plan)
    replacement = job_root / "plates" / "002-original.png"
    replacement.write_bytes(b"new-original-illustration")

    updated = replace_timestamped_plate_candidate(
        inventory,
        job_root=job_root,
        expected_plan=plan,
        order=2,
        replacement_path="plates/002-original.png",
    )

    assert updated["candidate_count"] == 2
    assert updated["review_only_archive_count"] == 0
    assert updated["items"][1]["status"] == "candidate"
    assert updated["items"][1]["source_path"] == "plates/002-original.png"
    assert updated["items"][1]["replaces"]["status"] == "review_only_archive"
    manifest = compile_timestamped_plate_asset_manifest(
        updated,
        job_root=job_root,
        project_root=tmp_path,
        expected_plan=plan,
        manifest_id="history-of-bjj-episode-1-timestamped-plates-v2",
        project_id="history-of-bjj",
        episode_id="episode-one",
        approved_by="Operator replacement approval",
        approved_at="2026-08-01",
    )
    assert all(asset["render_eligible"] for asset in manifest["assets"])
