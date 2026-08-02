from __future__ import annotations

import copy
import hashlib
from io import BytesIO
from pathlib import Path

from PIL import Image

from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.living_editorial import (
    compile_editorial_coverage,
    split_semantic_units,
    validate_editorial_coverage,
)
from content.video_engine.src.services.stock_assets import (
    StockCandidateService,
    score_stock_candidate,
    validate_asset_selection,
    validate_flow_snapshot,
    validate_provider_reference_registry,
    validate_stock_candidate_batch,
)


def _shot_plan() -> dict:
    core = {
        "schema_version": "shot_plan.v3",
        "shots": [
            {
                "shot_id": "history-001",
                "chapter_id": "chapter-one",
                "narration_text": (
                    "The useful starting point is not a battlefield legend but "
                    "an institution. In 1882, Jigoro Kano established the Kodokan."
                ),
                "claim_refs": ["claim-one"],
                "citations": ["citation-one"],
                "function": "illustrated_reconstruction",
                "visual_function": "illustrated_reconstruction",
                "asset_ids": [],
                "duration_s": 24.0,
            },
            {
                "shot_id": "history-002",
                "chapter_id": "chapter-one",
                "narration_text": (
                    "The record shows a teaching network, while the myth prefers "
                    "one clean handoff."
                ),
                "claim_refs": ["claim-two"],
                "citations": ["citation-two"],
                "function": "document_quote_closeup",
                "visual_function": "document_quote_closeup",
                "asset_ids": ["archive-kano"],
                "duration_s": 12.0,
            },
        ],
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def test_semantic_split_uses_sentences_and_clauses_not_every_noun() -> None:
    units = split_semantic_units(
        "Kano built a school, a curriculum, and a public institution."
    )

    assert len(units) < 4
    assert "school" in " ".join(units)
    assert "curriculum" in " ".join(units)


def test_coverage_enforces_living_editorial_cadence() -> None:
    coverage = compile_editorial_coverage(_shot_plan())

    assert validate_editorial_coverage(coverage) == []
    assert coverage["duration_s"] == 36.0
    assert all(slot["duration_s"] <= 8 for slot in coverage["slots"])
    assert all(slot["micro_events"][0]["at_s"] == 0 for slot in coverage["slots"])
    assert any(
        slot["preferred_visual_source"] == "stock_vector"
        for slot in coverage["slots"]
    )
    assert all(slot["visual_archetype"] for slot in coverage["slots"])
    assert all(
        slot["preferred_visual_source"] in {"stock_photo", "stock_vector"}
        for slot in coverage["slots"]
        if slot["stock_eligible"]
    )
    assert all(
        left["uniqueness_signature"] != right["uniqueness_signature"]
        for left, right in zip(coverage["slots"], coverage["slots"][1:])
    )


def test_coverage_does_not_search_abstract_words_or_stock_chapter_cards() -> None:
    plan = copy.deepcopy(_shot_plan())
    plan["shots"] = [
        {
            **plan["shots"][0],
            "narration_text": (
                "That date does not mean every older jujutsu practice vanished "
                "overnight."
            ),
        },
        {
            **plan["shots"][1],
            "shot_id": "history-014",
            "function": "chapter_cta",
            "visual_function": "chapter_cta",
            "narration_text": (
                "International travel changed its setting and emphasis."
            ),
            "asset_ids": [],
        },
    ]
    plan["artifact_hash"] = canonical_sha256(
        {key: value for key, value in plan.items() if key != "artifact_hash"}
    )

    coverage = compile_editorial_coverage(plan)
    old_practice = [
        slot
        for slot in coverage["slots"]
        if slot["parent_shot_id"] == "history-001"
    ]
    chapter_cards = [
        slot
        for slot in coverage["slots"]
        if slot["parent_shot_id"] == "history-014"
    ]

    assert all(" older " not in f" {slot['search_query'].casefold()} " for slot in old_practice)
    assert all(" date " not in f" {slot['search_query'].casefold()} " for slot in old_practice)
    assert all(slot["visual_archetype"] == "chapter_card" for slot in chapter_cards)
    assert all(slot["stock_eligible"] is False for slot in chapter_cards)


def test_historical_martial_archive_requires_period_and_subject_facets() -> None:
    plan = copy.deepcopy(_shot_plan())
    plan["shots"] = [
        {
            **plan["shots"][1],
            "narration_text": (
                "Kano drew from multiple jujutsu schools and reorganized "
                "practice at the Kodokan."
            ),
            "function": "archival_portrait",
            "visual_function": "archival_portrait",
            "duration_s": 18.0,
        }
    ]
    plan["artifact_hash"] = canonical_sha256(
        {key: value for key, value in plan.items() if key != "artifact_hash"}
    )

    coverage = compile_editorial_coverage(plan)
    historical = [
        slot
        for slot in coverage["slots"]
        if slot["visual_archetype"] == "historical_martial_archive"
    ]

    assert historical
    assert all("historical judo" in slot["search_query"] for slot in historical)
    assert all(len(slot["required_term_groups"]) == 2 for slot in historical)


def test_scholarship_does_not_match_ship_travel_broll() -> None:
    plan = copy.deepcopy(_shot_plan())
    plan["shots"] = [
        {
            **plan["shots"][0],
            "narration_text": (
                "Scholarship names intermediaries that a simple lineage graph "
                "would otherwise delete."
            ),
            "function": "migration_map_timeline",
            "visual_function": "migration_map_timeline",
            "duration_s": 12.0,
        }
    ]
    plan["artifact_hash"] = canonical_sha256(
        {key: value for key, value in plan.items() if key != "artifact_hash"}
    )

    coverage = compile_editorial_coverage(plan)

    assert all(
        slot["visual_archetype"] != "historical_travel_broll"
        for slot in coverage["slots"]
    )
    assert all("ship" not in slot["search_concepts"] for slot in coverage["slots"])


def test_stock_relevance_rejects_category_mismatches() -> None:
    slot = {
        "required_terms": [
            "judo",
            "jujutsu",
            "martial arts",
            "dojo",
            "tatami",
        ],
        "blocked_terms": ["couple", "golf", "hotel", "resort"],
        "search_concepts": ["Jigoro Kano", "judo"],
    }

    good = score_stock_candidate(
        slot,
        {
            "title": "Vintage Japanese judo training inside a traditional dojo",
            "keywords": ["martial arts", "tatami", "Japan"],
        },
    )
    senior_couple = score_stock_candidate(
        slot,
        {"title": "Senior couple opening a gift bag at an outdoor cafe"},
    )
    disc_golf = score_stock_candidate(
        slot,
        {"title": "Disc golf basket on a sandy forest course"},
    )

    assert good["accepted"] is True
    assert good["score"] >= 3
    assert senior_couple["accepted"] is False
    assert disc_golf["accepted"] is False


def test_period_comic_requires_both_subject_and_style() -> None:
    slot = {
        "required_terms": [
            "samurai",
            "battlefield",
            "comic",
            "halftone",
            "woodblock",
        ],
        "required_term_groups": [
            ["samurai", "battlefield", "martial arts"],
            ["comic", "halftone", "woodblock", "vintage"],
        ],
        "blocked_terms": ["photo effect", "animal"],
        "search_concepts": ["battlefield"],
    }

    subject_only = score_stock_candidate(
        slot, {"title": "Fearless samurai warriors in armor"}
    )
    style_only = score_stock_candidate(
        slot, {"title": "Halftone comic photo effect template"}
    )
    matched = score_stock_candidate(
        slot,
        {"title": "Vintage woodblock comic of samurai on a battlefield"},
    )

    assert subject_only["accepted"] is False
    assert style_only["accepted"] is False
    assert matched["accepted"] is True


def test_stock_batch_deduplicates_provider_resources_across_slots(
    tmp_path: Path,
) -> None:
    coverage = compile_editorial_coverage(_shot_plan())
    template = copy.deepcopy(
        next(slot for slot in coverage["slots"] if slot["stock_eligible"])
    )
    template.update(
        {
            "visual_archetype": "martial_arts_broll",
            "preferred_visual_source": "stock_photo",
            "fallback_visual_source": "typography",
            "search_query": "judo training dojo tatami documentary photo",
            "search_concepts": ["judo", "dojo"],
            "required_terms": ["judo", "jujutsu", "jiu jitsu"],
            "required_term_groups": [["judo", "jujutsu", "jiu jitsu"]],
            "blocked_terms": ["aikido", "karate"],
        }
    )
    first = {**template, "slot_id": "slot-one", "uniqueness_signature": "one"}
    second = {**template, "slot_id": "slot-two", "uniqueness_signature": "two"}
    core = {
        key: value
        for key, value in coverage.items()
        if key not in {"artifact_hash", "slots", "slot_count"}
    }
    core.update({"slots": [first, second], "slot_count": 2})
    coverage = {**core, "artifact_hash": canonical_sha256(core)}

    buffer = BytesIO()
    Image.new("RGB", (2, 2), "white").save(buffer, format="PNG")
    png = buffer.getvalue()

    class FakeTransport:
        def search(self, term: str, *, limit: int = 8) -> list[dict]:
            base = [
                {
                    "id": "same-resource",
                    "title": "Judo training inside a traditional dojo",
                    "image": {
                        "type": "photo",
                        "source": {"url": "https://stock.invalid/preview.png"},
                    },
                    "licenses": [
                        {"type": "licensed", "url": "https://stock.invalid/license"}
                    ],
                }
            ]
            return [
                *base,
                {
                    **base[0],
                    "id": "different-id-same-preview",
                },
            ]

        def download_bytes(self, url: str, *, maximum: int) -> tuple[bytes, str]:
            return png, "image/png"

    batch = StockCandidateService(transport=FakeTransport()).build_batch(
        coverage,
        job_dir=tmp_path,
        live_search=True,
        candidates_per_slot=1,
    )

    remote = [item for item in batch["candidates"] if item["provider"] == "magnific"]
    assert len(remote) == 1
    assert batch["duplicate_rejection_count"] == 2


def test_coverage_rejects_static_gap_and_hash_drift() -> None:
    coverage = compile_editorial_coverage(_shot_plan())
    broken = copy.deepcopy(coverage)
    broken["slots"][0]["micro_events"] = [
        {
            "at_s": 0,
            "action": "establish",
            "recipe": broken["slots"][0]["motion_recipe"],
        }
    ]

    errors = validate_editorial_coverage(broken)

    assert any("static interval" in error for error in errors)
    assert any("artifact_hash" in error for error in errors)


def test_stock_batch_contains_quarantined_local_fallbacks(tmp_path: Path) -> None:
    coverage = compile_editorial_coverage(_shot_plan())
    batch = StockCandidateService().build_batch(
        coverage,
        job_dir=tmp_path,
        live_search=False,
    )

    assert validate_stock_candidate_batch(batch, job_dir=tmp_path) == []
    assert batch["stock_slot_ids"]
    assert all(item["render_eligible"] is False for item in batch["candidates"])
    assert all(item["provider"] == "local" for item in batch["candidates"])
    assert (tmp_path / "asset_selection" / "contact-sheet.png").is_file()
    assert (tmp_path / "asset_selection" / "review-template.json").is_file()


def test_asset_selection_is_hash_cost_and_slot_bound(tmp_path: Path) -> None:
    coverage = compile_editorial_coverage(_shot_plan())
    batch = StockCandidateService().build_batch(
        coverage,
        job_dir=tmp_path,
        live_search=False,
    )
    by_slot = {
        item["slot_id"]: item
        for item in batch["candidates"]
        if item["provider"] == "local"
    }
    review = {
        "schema_version": "asset_selection_review.v1",
        "coverage_hash": coverage["artifact_hash"],
        "candidate_batch_hash": batch["artifact_hash"],
        "approved": True,
        "reviewed_by": "operator",
        "reviewed_at": "2026-07-31T00:00:00Z",
        "selections": [
            {
                "slot_id": slot_id,
                "candidate_id": candidate["candidate_id"],
                "approved_cost_usd": 0.0,
            }
            for slot_id, candidate in by_slot.items()
        ],
    }

    assert (
        validate_asset_selection(
            review,
            batch,
            expected_coverage_hash=coverage["artifact_hash"],
        )
        == []
    )
    stale = copy.deepcopy(review)
    stale["candidate_batch_hash"] = "0" * 64
    assert any("stale" in error for error in validate_asset_selection(stale, batch))


def test_unknown_stock_cost_and_missing_attribution_fail() -> None:
    candidate = {
        "candidate_id": "slot-one-magnific-1",
        "slot_id": "slot-one",
        "provider": "magnific",
        "resource_id": "1",
        "license_type": "freemium",
        "license_url": "https://license.invalid/1",
        "attribution_required": True,
        "attribution": "",
        "estimated_cost_usd": None,
    }
    core = {
        "schema_version": "stock_candidate_batch.v1",
        "provider": "magnific",
        "coverage_hash": "a" * 64,
        "stock_slot_ids": ["slot-one"],
        "candidate_count": 1,
        "candidates": [candidate],
    }
    batch = {**core, "artifact_hash": canonical_sha256(core)}
    review = {
        "schema_version": "asset_selection_review.v1",
        "coverage_hash": "a" * 64,
        "candidate_batch_hash": batch["artifact_hash"],
        "approved": True,
        "reviewed_by": "operator",
        "reviewed_at": "2026-07-31T00:00:00Z",
        "selections": [
            {
                "slot_id": "slot-one",
                "candidate_id": candidate["candidate_id"],
                "approved_cost_usd": 0,
            }
        ],
    }

    errors = validate_asset_selection(review, batch)

    assert any("unknown cost" in error for error in errors)
    assert any("requires attribution" in error for error in errors)


def test_premium_entitlement_resolves_cost_and_enforces_daily_cap() -> None:
    candidate = {
        "candidate_id": "slot-one-magnific-1",
        "slot_id": "slot-one",
        "provider": "magnific",
        "resource_id": "1",
        "license_type": "premium",
        "license_url": "https://license.invalid/1",
        "attribution_required": True,
        "attribution": "",
        "estimated_cost_usd": None,
    }
    core = {
        "schema_version": "stock_candidate_batch.v1",
        "provider": "magnific",
        "coverage_hash": "a" * 64,
        "stock_slot_ids": ["slot-one"],
        "candidate_count": 1,
        "candidates": [candidate],
    }
    batch = {**core, "artifact_hash": canonical_sha256(core)}
    review = {
        "schema_version": "asset_selection_review.v1",
        "coverage_hash": "a" * 64,
        "candidate_batch_hash": batch["artifact_hash"],
        "approved": True,
        "reviewed_by": "operator",
        "reviewed_at": "2026-07-31T00:00:00Z",
        "entitlement_snapshot": {
            "account_plan": "premium",
            "downloads_included": True,
            "daily_download_limit": 100,
            "confirmed_by": "operator",
        },
        "selections": [
            {
                "slot_id": "slot-one",
                "candidate_id": candidate["candidate_id"],
                "approved_cost_usd": 0,
            }
        ],
    }

    assert validate_asset_selection(review, batch) == []
    review["entitlement_snapshot"]["daily_download_limit"] = 0
    assert any(
        "daily download limit" in error
        for error in validate_asset_selection(review, batch)
    )


def test_reference_and_flow_contracts_keep_provider_inputs_non_renderable() -> None:
    digest = hashlib.sha256(b"original-input").hexdigest()
    registry = {
        "schema_version": "provider_reference_registry.v1",
        "references": [
            {
                "id": "combat-history-paper",
                "provider": "magnific",
                "kind": "style",
                "provider_id": None,
                "input_hashes": [digest],
                "rights_reviewed": True,
                "render_eligible": False,
            }
        ],
    }
    flow = {
        "schema_version": "provider_flow_snapshot.v1",
        "provider": "magnific",
        "flow_id": "history-still",
        "flow_version": "1",
        "input_types": ["text", "image"],
        "output_types": ["image"],
        "evaluator_required": True,
        "cost_ceiling_usd": 0,
        "can_approve_assets": False,
        "can_establish_facts": False,
    }

    assert validate_provider_reference_registry(registry) == []
    assert validate_flow_snapshot(flow) == []

    registry["references"][0]["render_eligible"] = True
    flow["can_establish_facts"] = True
    assert validate_provider_reference_registry(registry)
    assert validate_flow_snapshot(flow)
