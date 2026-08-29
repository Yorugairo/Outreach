from __future__ import annotations

import copy
from pathlib import Path

import pytest

from content.video_engine.src.services.finance_channel import (
    FinanceChannelValidationError,
    file_sha256,
    validate_artifact,
    validate_asset_catalog,
    validate_semantic_visual_package,
    with_artifact_hash,
)
from content.video_engine.src.services.finance_visual_selection import resolve_cue


HASH = "a" * 64


def _cue() -> dict:
    return {
        "cue_id": "index-inflows", "start_word": 0, "end_word": 3, "start_s": 0.0, "end_s": 4.0,
        "excerpt": "Passive cash enters the weighted fund.", "claim_refs": ["claim-index"],
        "state_type": "mechanism", "visual_world": "mechanism", "call_cue_id": "show-passive-inflow-allocation",
        "representation_mode": "accurate_mechanism",
        "semantic_target": {
            "subject": "index fund container", "relationship": "cash enters weighted holdings",
            "viewer_takeaway": "The fund allocates one inflow across a weighted basket.",
            "required_visual_anchors": ["cash-inflow", "weighted-holdings", "fund-container"],
            "prohibited_implications": ["automatic-price-causation"], "prior_state": None,
            "next_state": "holdings weights separate",
        },
        "entry_action": "cash tokens enter", "micro_events": [{"at_s": 1.5, "action": "weighted tiles separate"}],
        "exit_transition": "weights open", "fact_surface": "index-weight-page",
        "evidence_surface_ids": ["index-weight-page"], "short_membership": [],
    }


def _cue_sheet() -> dict:
    return with_artifact_hash(
        {
            "schema_version": "finance_visual_cue_sheet.v2", "episode_id": "fixture",
            "narration": {"audio_sha256": HASH, "words_sha256": HASH, "word_count": 4, "duration_s": 4.0},
            "caption_safe_band": {"top": 0.84, "bottom": 0.94}, "short_ranges": [], "cues": [_cue()],
        }
    )


def _asset(tmp_path: Path, *, anchors: list[str] | None = None) -> dict:
    image = tmp_path / "index-basket.png"
    image.write_bytes(b"index basket")
    return {
        "asset_id": "index-basket-clear", "path": image.name, "sha256": file_sha256(image), "kind": "mechanism",
        "visual_worlds": ["mechanism"], "semantic_tags": ["index", "basket"],
        "capability_anchors": anchors or ["cash-inflow", "weighted-holdings", "fund-container"],
        "representation_modes": ["accurate_mechanism"], "prohibited_implications": [], "claim_refs": ["claim-index"],
        "reuse_policy": {"max_total_uses": 2, "min_nonadjacent_gap": 1, "allowed_reasons": ["continuation", "callback"], "allow_adjacent_continuation": True, "claim_bound": True},
        "resolution_tier": 3, "generated": True, "contains_factual_text": False,
        "rights_state": "approved", "review_state": "approved_reusable", "render_eligible": True,
    }


def _catalog(tmp_path: Path, *, anchors: list[str] | None = None) -> dict:
    return with_artifact_hash(
        {
            "schema_version": "finance_asset_catalog.v2", "channel_id": "fixture", "project_root": ".",
            "resolution_order": ["exact_semantic_match", "reusable_component_composition", "deterministic_evidence_or_mechanism", "bespoke_plate"],
            "assets": [_asset(tmp_path, anchors=anchors)],
        }
    )


def _numeric_register() -> dict:
    return with_artifact_hash(
        {
            "schema_version": "finance_numeric_evidence_register.v1", "episode_id": "fixture", "claim_ledger_hash": HASH,
            "verified_report": {"report_id": "verified-input", "title": "Verified report", "location": "section 2"},
            "items": [{
                "surface_id": "index-weight-page", "claim_id": "claim-index", "display_value": 7.5,
                "unit": "percent", "as_of": "2026-08-01", "report_locator": "page 4, table 1",
                "format": "one decimal percent", "qualifier": "selected period", "permitted_surface_types": ["report_page", "weight_diagram"],
            }],
        }
    )


def _resolution(cue_sheet: dict, catalog: dict, numeric: dict, *, asset_ids: list[str] | None = None) -> dict:
    return with_artifact_hash(
        {
            "schema_version": "finance_visual_resolution.v1", "episode_id": "fixture",
            "cue_sheet_hash": cue_sheet["artifact_hash"], "asset_catalog_hash": catalog["artifact_hash"],
            "numeric_evidence_register_hash": numeric["artifact_hash"], "review_state": "operator_approved", "render_eligible": True,
            "resolutions": [{
                "resolution_id": "resolve-index-inflows", "cue_id": "index-inflows", "call_cue_id": "show-passive-inflow-allocation",
                "status": "resolved", "representation_mode": "accurate_mechanism", "strategy": "exact_asset",
                "selected_asset_ids": asset_ids or ["index-basket-clear"], "composition_recipe_id": None,
                "reuse_reason": None, "evidence_surface_ids": ["index-weight-page"], "demand": None,
            }],
        }
    )


def test_v2_catalog_and_resolver_require_all_visual_anchors(tmp_path: Path) -> None:
    cue = _cue()
    exact = _asset(tmp_path)
    selected = resolve_cue(cue, [exact], require_promoted=True)
    assert selected.status == "resolved"
    assert selected.asset_ids == ("index-basket-clear",)

    near_match = _asset(tmp_path, anchors=["cash-inflow", "fund-container"])
    unresolved = resolve_cue(cue, [near_match], require_promoted=True)
    assert unresolved.status == "unresolved"
    assert unresolved.demand["required_visual_anchors"] == ["cash-inflow", "weighted-holdings", "fund-container"]


def test_semantic_package_binds_exact_assets_and_verified_numbers(tmp_path: Path) -> None:
    cue_sheet, catalog, numeric = _cue_sheet(), _catalog(tmp_path), _numeric_register()
    resolution = _resolution(cue_sheet, catalog, numeric)
    assert validate_asset_catalog(catalog, tmp_path)["schema_version"] == "finance_asset_catalog.v2"
    result = validate_semantic_visual_package(cue_sheet, resolution, catalog, numeric, tmp_path)
    assert result == {"status": "valid", "episode_id": "fixture", "cue_count": 1, "unresolved_count": 0}


def test_semantic_package_rejects_tag_only_asset_and_unbound_statistic(tmp_path: Path) -> None:
    cue_sheet, catalog, numeric = _cue_sheet(), _catalog(tmp_path, anchors=["cash-inflow", "fund-container"]), _numeric_register()
    resolution = _resolution(cue_sheet, catalog, numeric)
    with pytest.raises(FinanceChannelValidationError, match="required visual anchors"):
        validate_semantic_visual_package(cue_sheet, resolution, catalog, numeric, tmp_path)

    catalog = _catalog(tmp_path)
    bad_numeric = copy.deepcopy(numeric)
    bad_numeric["items"][0]["claim_id"] = "claim-other"
    bad_numeric = with_artifact_hash({key: value for key, value in bad_numeric.items() if key != "artifact_hash"})
    resolution = _resolution(cue_sheet, catalog, bad_numeric)
    with pytest.raises(FinanceChannelValidationError, match="not bound to a cue claim"):
        validate_semantic_visual_package(cue_sheet, resolution, catalog, bad_numeric, tmp_path)


def test_unresolved_resolution_requires_complete_demand_and_blocks_render() -> None:
    cue_sheet = _cue_sheet()
    numeric = _numeric_register()
    unresolved = with_artifact_hash(
        {
            "schema_version": "finance_visual_resolution.v1", "episode_id": "fixture", "cue_sheet_hash": cue_sheet["artifact_hash"],
            "asset_catalog_hash": HASH, "numeric_evidence_register_hash": numeric["artifact_hash"],
            "review_state": "operator_approved", "render_eligible": True,
            "resolutions": [{
                "resolution_id": "resolve-index-inflows", "cue_id": "index-inflows", "call_cue_id": "show-passive-inflow-allocation",
                "status": "unresolved", "representation_mode": "accurate_mechanism", "strategy": "original_generation_request",
                "selected_asset_ids": [], "composition_recipe_id": None, "reuse_reason": None, "evidence_surface_ids": ["index-weight-page"],
                "demand": {"demand_id": "demand-index-inflows", "kind": "original_generation_request", "brief": "Create a clear weighted index-fund mechanism with a separate cash inflow.", "required_visual_anchors": ["cash-inflow"], "prohibited_implications": [], "depth_layers": ["foreground"], "review_state": "draft"},
            }],
        }
    )
    with pytest.raises(FinanceChannelValidationError, match="cannot contain unresolved"):
        validate_artifact(unresolved)
