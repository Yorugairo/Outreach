from __future__ import annotations

import copy

from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.producer_orchestration import (
    compile_producer_plan,
    validate_producer_plan,
)


def _coverage() -> dict:
    return {
        "schema_version": "editorial_coverage.v1",
        "artifact_hash": "coverage-hash",
        "slots": [
            {
                "slot_id": "history-001-unit-01-part-01",
                "narration_excerpt": "Kano built an institution, not a battlefield legend.",
                "duration_s": 4.5,
                "semantic_purpose": "correction",
                "visual_archetype": "period_comic_block",
                "selected_visual_source": "original_illustration",
                "claim_refs": ["kano-founded-kodokan-1882"],
                "citation_refs": ["citation-ijf-1882"],
                "asset_ids": [],
                "motion_recipe": "comic_pop",
                "micro_events": [
                    {"at_s": 0.0, "action": "reveal", "recipe": "comic_pop"}
                ],
                "uniqueness_signature": "illustration:comic_pop:01",
            }
        ],
    }


def test_compiler_emits_stable_typed_blocks_for_external_producers() -> None:
    coverage = _coverage()
    first = compile_producer_plan(
        coverage,
        art_bible_id="combat-history-archival-editorial-v1",
        art_bible_hash="a" * 64,
    )
    second = compile_producer_plan(
        coverage,
        art_bible_id="combat-history-archival-editorial-v1",
        art_bible_hash="a" * 64,
    )

    assert first == second
    assert validate_producer_plan(first) == []
    block = first["blocks"][0]
    assert block["producer_kind"] == "image"
    assert {item["id"] for item in block["still_producers"]} == {
        "gpt_image",
        "magnific_nano_banana_2",
    }
    assert "magnific_kling_2_5" in {
        item["id"] for item in block["motion_producers"]
    }
    assert block["render_eligible"] is False
    assert block["prompt"]["audio"].startswith("Silent provider output")


def test_validator_rejects_provider_leakage_and_stale_hash() -> None:
    plan = compile_producer_plan(_coverage(), art_bible_hash="b" * 64)

    leaked = copy.deepcopy(plan)
    leaked["blocks"][0]["prompt"]["scene"] = "in the style of a creator name"
    assert any("prohibited provider input" in error for error in validate_producer_plan(leaked))

    stale = copy.deepcopy(plan)
    stale["art_bible_hash"] = "c" * 64
    stale["artifact_hash"] = canonical_sha256(
        {key: value for key, value in stale.items() if key != "artifact_hash"}
    )
    errors = validate_producer_plan(
        stale,
        expected_art_bible_hash=plan["art_bible_hash"],
    )
    assert "producer plan art_bible_hash is stale" in errors


def test_validator_rejects_renderable_provider_output_and_unknown_producer() -> None:
    plan = compile_producer_plan(_coverage())
    plan["blocks"][0]["render_eligible"] = True
    plan["blocks"][0]["still_producers"][0]["id"] = "unapproved-provider"
    errors = validate_producer_plan(plan)
    assert any("must not be render eligible" in error for error in errors)
    assert any("invalid producer" in error for error in errors)


def test_world_first_documentary_roles_route_to_image_plates_with_fact_overlays() -> None:
    coverage = _coverage()
    coverage["slots"][0].update(
        {
            "selected_visual_source": "map",
            "visual_archetype": "distance_map",
        }
    )
    plan = compile_producer_plan(coverage)
    block = plan["blocks"][0]
    assert block["producer_kind"] == "image"
    assert {item["id"] for item in block["still_producers"]} == {
        "gpt_image",
        "magnific_nano_banana_2",
    }
    assert [item["id"] for item in block["motion_producers"]] == ["remotion"]
    assert block["world_plate_policy"] == {
        "plate_role": "migration_world",
        "overlay_owner": "remotion",
        "overlay_fields": [
            "reviewed_places",
            "reviewed_route",
            "reviewed_dates",
            "citation_rail",
        ],
        "generated_geometry_is_evidence": False,
    }
    assert block["assembly"]["fact_overlay_owner"] == "remotion"
    assert block["prompt"]["world_plate_policy"]["generated_geometry_is_evidence"] is False


def test_lineage_and_concept_world_plates_have_distinct_roles() -> None:
    coverage = _coverage()
    coverage["slots"].extend(
        [
            {
                **coverage["slots"][0],
                "slot_id": "lineage-01",
                "function": "lineage_graph",
                "selected_visual_source": "graph",
                "visual_archetype": "entity_graph",
            },
            {
                **coverage["slots"][0],
                "slot_id": "concept-01",
                "function": "concept_mechanics_cutaway",
                "selected_visual_source": "stock_photo",
                "visual_archetype": "concept_cutaway",
            },
        ]
    )
    blocks = compile_producer_plan(coverage)["blocks"]
    assert blocks[1]["world_plate_policy"]["plate_role"] == "lineage_scroll"
    assert blocks[2]["world_plate_policy"]["plate_role"] == "concept_cutaway"
