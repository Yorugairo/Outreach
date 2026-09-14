from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from content.video_engine.src.services.finance_channel import (
    FinanceChannelValidationError,
    canonical_sha256,
    file_sha256,
    generated_asset_file_errors,
    generated_source_is_struck,
    load_json,
    score_topic,
    select_asset_strategy,
    validate_artifact,
    validate_asset_catalog,
    validate_project,
    with_artifact_hash,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECT_ROOT = REPO_ROOT / "content" / "video_engine" / "projects" / "systems-and-blowups"


def _rehash(payload: dict) -> dict:
    result = copy.deepcopy(payload)
    result["artifact_hash"] = canonical_sha256(result)
    return result


def _valid_claim_ledger() -> dict:
    return with_artifact_hash(
        {
            "schema_version": "finance_claim_ledger.v1",
            "episode_id": "fixture",
            "research_state": "source_locked",
            "contrarian_frame": True,
            "countercase": "The conventional explanation may still dominate when the selected comparison window changes.",
            "failure_conditions": ["The primary data contradict the proposed mechanism."],
            "claims": [
                {
                    "claim_id": "claim-1",
                    "text": "The selected primary series changed over the measured interval.",
                    "classification": "observed_fact",
                    "temporal_kind": "numeric",
                    "as_of": "2026-08-01",
                    "source_locators": [
                        {
                            "source_id": "source-1",
                            "publisher": "Federal Reserve Bank of St. Louis",
                            "title": "Fixture primary series",
                            "url": "https://fred.stlouisfed.org/",
                            "location": "observation table",
                            "published_at": "2026-08-01",
                            "accessed_at": "2026-08-07",
                            "primary": True,
                        }
                    ],
                    "calculation": None,
                    "qualifier": "The claim applies only to the selected series and interval.",
                    "counterevidence_refs": [],
                    "review_state": "source_checked",
                }
            ],
        }
    )


def _valid_cue_sheet() -> dict:
    digest = "a" * 64
    return with_artifact_hash(
        {
            "schema_version": "finance_visual_cue_sheet.v1",
            "episode_id": "fixture",
            "narration": {"audio_sha256": digest, "words_sha256": digest, "word_count": 4, "duration_s": 4.0},
            "caption_safe_band": {"top": 0.84, "bottom": 0.94},
            "short_ranges": [{"short_id": "short-1", "start_word": 0, "end_word": 3, "start_s": 0.0, "end_s": 4.0}],
            "cues": [
                {
                    "cue_id": "cue-1", "start_word": 0, "end_word": 1, "start_s": 0.0, "end_s": 2.0,
                    "excerpt": "A lived contradiction", "claim_refs": [], "state_type": "narrative", "visual_world": "story",
                    "entry_action": "household enters", "micro_events": [{"at_s": 1.0, "action": "rent token moves"}],
                    "exit_transition": "hard causal cut", "fact_surface": None, "short_membership": ["short-1"],
                },
                {
                    "cue_id": "cue-2", "start_word": 2, "end_word": 3, "start_s": 2.0, "end_s": 4.0,
                    "excerpt": "The machine opens", "claim_refs": ["claim-1"], "state_type": "mechanism", "visual_world": "mechanism",
                    "entry_action": "ledger opens", "micro_events": [{"at_s": 3.0, "action": "flow separates"}],
                    "exit_transition": "evidence lock", "fact_surface": "chart-1", "short_membership": ["short-1"],
                },
            ],
        }
    )


def test_project_and_all_three_pilots_validate() -> None:
    result = validate_project(PROJECT_ROOT, include_pilots=True)
    assert result["status"] == "valid"
    assert len([path for path in result["validated"] if path.endswith("episode-brief.v1.json")]) == 3
    assert len([path for path in result["validated"] if path.endswith("claim-ledger.v1.json")]) == 3


def test_weekend_first_schedule_and_short_parentage_are_enforced() -> None:
    schedule = load_json(PROJECT_ROOT / "programming-schedule.v1.json")
    assert validate_artifact(schedule)["timezone"] == "America/New_York"
    broken = copy.deepcopy(schedule)
    next(item for item in broken["releases"] if item["format"] == "current_mechanism")["day"] = "Wednesday"
    with pytest.raises(FinanceChannelValidationError, match="Friday current"):
        validate_artifact(_rehash(broken))

    broken = copy.deepcopy(schedule)
    next(item for item in broken["releases"] if item["slot_id"] == "monday-short")["parent_slot_id"] = "saturday-anatomy"
    with pytest.raises(FinanceChannelValidationError, match="one-to-one"):
        validate_artifact(_rehash(broken))


def test_channel_profile_locks_three_worlds_and_complexity_budget() -> None:
    profile = load_json(PROJECT_ROOT / "channel-profile.v1.json")
    assert set(validate_artifact(profile)["visual_worlds"]) == {"story", "mechanism", "evidence"}
    broken = copy.deepcopy(profile)
    broken["complexity_budget"]["bespoke_percent"] = 15
    with pytest.raises(FinanceChannelValidationError, match="total 100"):
        validate_artifact(_rehash(broken))


def test_nuhu_learning_is_identity_architecture_not_visual_imitation() -> None:
    learnings = validate_artifact(load_json(PROJECT_ROOT / "reference-learnings.v1.json"))
    nuhu = next(item for item in learnings["references"] if item["reference_id"] == "moses-speaks-nuhu")
    adopted = " ".join(nuhu["adopt"]).lower()
    forbidden = " ".join(nuhu["do_not_copy"]).lower()
    assert "black household" in adopted
    assert "avatar" in forbidden and "trade dress" in forbidden


def test_pilots_remain_draft_and_not_render_eligible_until_all_human_gates_pass() -> None:
    briefs = sorted((PROJECT_ROOT / "pilots").glob("*/episode-brief.v1.json"))
    assert len(briefs) == 3
    for path in briefs:
        brief = validate_artifact(load_json(path))
        assert brief["state"] == "draft"
        assert brief["thesis_state"] in {"research_question", "operator_approved"}
        assert brief["render_eligible"] is False
        assert brief["research_blockers"]
        assert brief["embedded_short"]["recorded_in_long_master"] is True


def test_package_variants_must_resolve_to_one_promise() -> None:
    brief = load_json(PROJECT_ROOT / "pilots" / "index-fund-risk" / "episode-brief.v1.json")
    broken = copy.deepcopy(brief)
    broken["packages"][1]["promise_key"] = "different-video"
    with pytest.raises(FinanceChannelValidationError, match="same episode promise"):
        validate_artifact(_rehash(broken))


def test_personalized_buy_sell_instruction_is_rejected() -> None:
    brief = load_json(PROJECT_ROOT / "pilots" / "index-fund-risk" / "episode-brief.v1.json")
    broken = copy.deepcopy(brief)
    broken["thesis"] = "You should buy this now because the index mechanism guarantees the result."
    with pytest.raises(FinanceChannelValidationError, match="buy/sell"):
        validate_artifact(_rehash(broken))


def test_current_or_numeric_claim_requires_as_of_and_primary_locator() -> None:
    ledger = _valid_claim_ledger()
    assert validate_artifact(ledger)["research_state"] == "source_locked"
    missing_date = copy.deepcopy(ledger)
    missing_date["claims"][0]["as_of"] = None
    with pytest.raises(FinanceChannelValidationError, match="as_of"):
        validate_artifact(_rehash(missing_date))

    secondary_only = copy.deepcopy(ledger)
    secondary_only["claims"][0]["source_locators"][0]["primary"] = False
    with pytest.raises(FinanceChannelValidationError, match="primary source"):
        validate_artifact(_rehash(secondary_only))


def test_contrarian_ledger_requires_countercase_and_failure_conditions() -> None:
    ledger = _valid_claim_ledger()
    ledger["countercase"] = ""
    ledger["failure_conditions"] = []
    with pytest.raises(FinanceChannelValidationError) as caught:
        validate_artifact(_rehash(ledger))
    assert "countercase" in str(caught.value)
    assert "failure conditions" in str(caught.value)


def test_cue_sheet_rejects_gaps_and_long_static_holds() -> None:
    cue_sheet = _valid_cue_sheet()
    assert validate_artifact(cue_sheet)["narration"]["word_count"] == 4

    gap = copy.deepcopy(cue_sheet)
    gap["cues"][1]["start_s"] = 2.5
    with pytest.raises(FinanceChannelValidationError, match="gap or overlap"):
        validate_artifact(_rehash(gap))

    long_hold = copy.deepcopy(cue_sheet)
    long_hold["narration"]["duration_s"] = 5.0
    long_hold["cues"] = [
        {
            "cue_id": "cue-1", "start_word": 0, "end_word": 3, "start_s": 0.0, "end_s": 5.0,
            "excerpt": "One static frame", "claim_refs": [], "state_type": "narrative", "visual_world": "story",
            "entry_action": "actor enters", "micro_events": [{"at_s": 1.0, "action": "actor waits"}],
            "exit_transition": "hard cut", "fact_surface": None, "short_membership": ["short-1"],
        }
    ]
    long_hold["short_ranges"][0]["end_s"] = 5.0
    with pytest.raises(FinanceChannelValidationError, match="two timed micro-events"):
        validate_artifact(_rehash(long_hold))


def test_asset_catalog_hashes_paths_and_promotion_state() -> None:
    catalog = load_json(PROJECT_ROOT / "asset-catalog.v1.json")
    validated = validate_asset_catalog(catalog, PROJECT_ROOT)
    # 2026-09-14 (E94/E95): the catalogue declares the style-versioned schema and
    # carries 45 assets after the operator's 2026-09-13 pass (was 15).
    assert validated["schema_version"] == "finance_asset_catalog_styled.v1"
    assert len(validated["assets"]) == 45
    # The operator approved two host model sheets. Approving the picture is not a
    # grant of rights: both still ship rights_state original_review_only, so the
    # render-eligible set on disk is still empty. Assert the exact ids, not a mood.
    assert {
        asset["asset_id"] for asset in validated["assets"]
        if asset["review_state"] == "operator_approved"
    } == {"finance-host-v1-model-sheet", "finance-host-stick-v1-model-sheet"}
    assert {asset["asset_id"] for asset in validated["assets"] if asset["render_eligible"]} == set()
    # 2026-09-14 (operator ruling): the catalogue still carries 45 rows, but one plate
    # is absent from every checkout and is marked for regeneration. The row keeps its
    # sha256 as the record, is not required on disk, and is not render-eligible.
    regenerate = {
        asset["asset_id"] for asset in validated["assets"]
        if asset.get("file_state") == "regenerate"
    }
    assert regenerate == {"mechanism-town-v1"}
    assert regenerate.isdisjoint(
        {asset["asset_id"] for asset in validated["assets"] if asset["render_eligible"]}
    )
    town = next(asset for asset in validated["assets"] if asset["asset_id"] == "mechanism-town-v1")
    assert not (PROJECT_ROOT / town["path"]).exists()
    assert len(town["sha256"]) == 64 and "operator ruling" in town["file_note"]

    escaped = copy.deepcopy(catalog)
    escaped["assets"][0]["path"] = "../outside.svg"
    with pytest.raises(FinanceChannelValidationError, match="escapes project root"):
        validate_asset_catalog(_rehash(escaped), PROJECT_ROOT)


def test_friendly_crinkle_cut_style_is_canonical() -> None:
    style = load_json(PROJECT_ROOT / "style-profile.v1.json")
    assert style["style_id"] == "friendly-crinkle-cut-economy-v1"
    assert set(style["palette"]) == {"charcoal", "cobalt", "teal", "sunflower", "coral", "cream"}
    assert "independent tactile raster assets" in style["construction_rule"]
    assert "does not authorize toy proportions" in style["friendliness_rule"]
    assert not list((PROJECT_ROOT / "assets" / "review").glob("economic-paper-theatre-*.svg"))


def test_generated_asset_manifest_binds_sources_and_cutouts() -> None:
    root = PROJECT_ROOT / "assets" / "generated"
    manifest = load_json(root / "generation-manifest.v1.json")
    assert manifest["generation_mode"] == "built-in-imagegen"
    assert manifest["promotion_state"] == "review_only"
    assert manifest["render_eligible"] is False
    # 2026-09-14 (E94/E95): 19 generated assets on disk (was 15); the four host and
    # stealth-wealth plates added by the 2026-09-13 pass are still render_state draft.
    assert len(manifest["assets"]) == 19
    assert {
        asset["asset_id"] for asset in manifest["assets"]
        if asset.get("render_state") == "draft"
    } == {
        "finance-host-presenter-plate-v1", "finance-host-presenter-direct-v1",
        "stealth-wealth-warm-study-v1", "stealth-wealth-cool-wafer-v1",
    }
    # 2026-09-14 (operator ruling): three pre-cutout SOURCE intermediates are absent
    # from every checkout and are struck - null source_path, sha kept as the record.
    # Their cutouts are on disk and still verify, which is what the reader enforces.
    assert {
        asset["asset_id"] for asset in manifest["assets"]
        if generated_source_is_struck(asset)
    } == {
        "mechanism-index-basket-v2", "mechanism-balance-ledger-v1",
        "mechanism-economic-elevator-v1",
    }
    # The absent world plate is one asset in two ledgers: the manifest marks it for
    # regeneration exactly as the catalogue row does, and no reader opens it.
    assert {
        asset["asset_id"] for asset in manifest["assets"]
        if asset.get("file_state") == "regenerate"
    } == {"mechanism-town-v1"}
    assert manifest["artifact_hash"] == canonical_sha256(manifest)
    for asset in manifest["assets"]:
        assert generated_asset_file_errors(asset, root) == [], asset["asset_id"]


def test_a_struck_source_is_skipped_but_its_cutout_is_still_hashed(tmp_path: Path) -> None:
    """2026-09-14 operator ruling: strike the source, keep verifying the picture."""
    (tmp_path / "cutouts").mkdir()
    cutout = tmp_path / "cutouts" / "plate.png"
    cutout.write_bytes(b"cutout-bytes")
    absent = tmp_path / "source" / "plate-source.png"
    absent.parent.mkdir()
    absent.write_bytes(b"source-bytes")
    source_sha = file_sha256(absent)
    absent.unlink()  # the intermediate is absent from every checkout

    struck = {
        "asset_id": "fixture-mechanism",
        "request": "A fixture mechanism.",
        "source_path": None,
        "source_sha256": source_sha,
        "source_state": "struck",
        "source_note": "source intermediate absent from every checkout 2026-09-14; the cutout verifies; struck by the operator's ruling",
        "cutout_path": "cutouts/plate.png",
        "cutout_sha256": file_sha256(cutout),
    }
    assert generated_source_is_struck(struck)
    assert generated_asset_file_errors(struck, tmp_path) == []

    # The strike covers the source only: the cutout is still hashed against bytes.
    tampered = {**struck, "cutout_sha256": "0" * 64}
    assert generated_asset_file_errors(tampered, tmp_path) == [
        "fixture-mechanism cutout sha256 does not match local bytes"
    ]
    # And an unstruck entry still has to open the file it points at.
    unstruck = {**struck, "source_state": "generated", "source_path": "source/plate-source.png"}
    assert generated_asset_file_errors(unstruck, tmp_path) == [
        "fixture-mechanism source file does not exist"
    ]
    nulled = {**struck, "source_state": "generated"}
    assert generated_asset_file_errors(nulled, tmp_path) == [
        "fixture-mechanism has a null source_path but is not struck"
    ]


def test_a_regenerate_asset_validates_without_the_file_and_never_renders(tmp_path: Path) -> None:
    """2026-09-14 operator ruling: a plate absent from every checkout is not a failure."""
    plate = tmp_path / "world.png"
    plate.write_bytes(b"world-bytes")
    plate_sha = file_sha256(plate)
    plate.unlink()  # absent from every checkout

    def _catalog(asset: dict) -> dict:
        return with_artifact_hash(
            {
                "schema_version": "finance_asset_catalog_styled.v1",
                "channel_id": "fixture",
                "project_root": ".",
                "resolution_order": ["exact_semantic_match", "reusable_component_composition", "deterministic_evidence_or_mechanism", "bespoke_plate"],
                "assets": [asset],
            }
        )

    row = {
        "asset_id": "fixture-world", "path": "world.png", "sha256": plate_sha, "kind": "world",
        "style_version": "crinkle-cut-v1", "visual_worlds": ["mechanism"], "semantic_tags": ["fixture"],
        "identity_lenses": [], "resolution_tier": 2, "generated": True, "contains_factual_text": False,
        "rights_state": "original_review_only", "review_state": "review_only", "render_eligible": False,
        "file_state": "regenerate",
        "file_note": "plate absent from every checkout 2026-09-14; regenerate from its request when a cut needs it (operator ruling)",
    }
    validated = validate_asset_catalog(_catalog(row), tmp_path)
    assert validated["assets"][0]["sha256"] == plate_sha

    approved_and_eligible = {
        **row, "render_eligible": True, "review_state": "operator_approved", "rights_state": "approved",
    }
    with pytest.raises(FinanceChannelValidationError, match="regenerate asset can never be render-eligible"):
        validate_asset_catalog(_catalog(approved_and_eligible), tmp_path)

    # `present` is the default, and a present row still has to be on disk.
    present = {key: value for key, value in row.items() if key != "file_state"}
    with pytest.raises(FinanceChannelValidationError, match="file does not exist"):
        validate_asset_catalog(_catalog(present), tmp_path)


def test_generated_asset_cannot_embed_factual_text(tmp_path: Path) -> None:
    asset = tmp_path / "plate.svg"
    asset.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
    catalog = with_artifact_hash(
        {
            "schema_version": "finance_asset_catalog.v1",
            "channel_id": "fixture",
            "project_root": ".",
            "resolution_order": ["exact_semantic_match", "reusable_component_composition", "deterministic_evidence_or_mechanism", "bespoke_plate"],
            "assets": [
                {
                    "asset_id": "fixture-plate", "path": "plate.svg", "sha256": file_sha256(asset), "kind": "hero_plate",
                    "visual_worlds": ["story"], "semantic_tags": ["fixture", "story"], "identity_lenses": [], "resolution_tier": 4,
                    "generated": True, "contains_factual_text": True, "rights_state": "original_review_only",
                    "review_state": "review_only", "render_eligible": False,
                }
            ],
        }
    )
    with pytest.raises(FinanceChannelValidationError, match="factual text"):
        validate_asset_catalog(catalog, tmp_path)


def test_topic_scoring_is_deterministic_and_penalizes_cost_and_risk() -> None:
    candidate = {
        "audience_contradiction": 0.9, "ordinary_financial_importance": 0.9, "primary_evidence": 0.8,
        "hidden_mechanism": 0.9, "visualizability": 0.8, "shelf_life": 0.7,
        "graph_connection": 0.8, "defensible_conclusion": 0.9, "production_cost": 0.2, "editorial_risk": 0.2,
    }
    low_risk = score_topic(candidate)
    high_risk = score_topic({**candidate, "production_cost": 1.0, "editorial_risk": 1.0})
    assert low_risk == score_topic(candidate)
    assert low_risk["score"] > high_risk["score"]


def test_asset_resolution_uses_cheapest_semantically_valid_tier() -> None:
    assert select_asset_strategy([4, 2, 3]) == 2
    assert select_asset_strategy([1, 4]) == 1
    with pytest.raises(FinanceChannelValidationError, match="no viable"):
        select_asset_strategy([])


def test_schema_contracts_are_strict_and_hashes_are_current() -> None:
    profile = load_json(PROJECT_ROOT / "channel-profile.v1.json")
    assert profile["artifact_hash"] == canonical_sha256(profile)
    extra = dict(profile)
    extra["undeclared"] = True
    with pytest.raises(FinanceChannelValidationError, match="Additional properties"):
        validate_artifact(_rehash(extra))
