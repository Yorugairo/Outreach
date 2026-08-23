from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from content.video_engine.src.services.semantic_evidence_binding import (
    canonical_sha256,
    compile_semantic_evidence_binding,
    file_sha256,
    load_plate_layout_profiles,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = REPO_ROOT / "content" / "video_engine"
PROFILE_HASH = "b807c53afb48f24840ddfe92fbf303669c5f3e472abfa05bc541791a9cc9e90c"


def _asset(
    tmp_path: Path,
    asset_id: str,
    *,
    cue_refs: list[str] | None = None,
    claim_refs: list[str] | None = None,
    what_it_is: str = "A reviewed HBM capacity comparison crop showing constrained wafer supply.",
    visual_role: str = "mechanism",
    review_state: str = "approved_reusable",
    rights_state: str = "approved",
    render_eligible: bool = True,
    path: str | None = None,
    declared_hash: str | None = None,
) -> dict[str, object]:
    file_name = path or f"{asset_id}.png"
    file_path = tmp_path / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(asset_id.encode("utf-8"))
    actual_hash = file_sha256(file_path)
    return {
        "asset_id": asset_id,
        "kind": "semantic_crop",
        "path": file_name,
        "sha256": declared_hash or actual_hash,
        "deck_id": "silicon-antidote",
        "slide_id": f"silicon-antidote-{asset_id}",
        "slide_number": 9,
        "parent_source_image_id": "silicon-antidote-s09-cleaned",
        "source_variant": "cleaned",
        "extraction": {
            "method": "rect_crop",
            "bbox_px": [10, 10, 600, 400],
            "bbox_norm": [0.05, 0.10, 0.72, 0.58],
            "polygon_norm": None,
            "mask_path": None,
            "source_sha256": "a" * 64,
        },
        "context": {
            "what_it_is": what_it_is,
            "visual_role": visual_role,
            "representation_mode": "literal_evidence",
            "factual_text": True,
            "claim_refs": claim_refs or [],
            "cue_refs": cue_refs or [],
            "not_what_it_means": ["The crop remains source-bound evidence."],
            "context_status": "operator_verified",
            "reuse_policy": {
                "scope": "scene",
                "max_total_uses": 1,
                "min_nonadjacent_gap": 0,
                "allowed_reasons": ["evidence_hold"],
                "claim_bound": True,
            },
        },
        "rights_state": rights_state,
        "review_state": review_state,
        "render_eligible": render_eligible,
    }


def _cue() -> dict[str, object]:
    return {
        "schema_version": "finance_visual_cue_sheet.v1",
        "cue_id": "cbm-cue-054",
        "start_s": 178.096,
        "end_s": 181.754,
        "excerpt": "As manufacturers devote more capacity to HBM,",
        "claim_refs": ["hbm-capacity-trade-ratio"],
        "state_type": "mechanism",
        "visual_world": "mechanism",
        "representation_mode": "literal_evidence",
        "entry_action": "hard semantic cut",
        "exit_transition": "hard cut on the next semantic phrase",
        "semantic_target": {
            "subject": "HBM capacity",
            "relationship": "manufacturing capacity shifts toward HBM and pressures supply",
            "viewer_takeaway": "The shortage becomes physical inside a constrained production system.",
            "required_visual_anchors": ["capacity", "wafer", "supply"],
            "prohibited_implications": ["guaranteed stock return"],
        },
    }


def _beat() -> dict[str, object]:
    return {
        "schema_version": "finance_semantic_beat_ledger.v1",
        "beat_id": "cbm-beat-054",
        "excerpt": "As manufacturers devote more capacity to HBM, they pressure conventional supply.",
        "claim_refs": ["hbm-capacity-trade-ratio"],
        "viewer_understanding": "The viewer should see the production tradeoff rather than infer a price chart.",
        "active_nouns": [{"surface": "capacity", "canonical": "capacity"}],
        "causal_verb": {"surface": "pressure", "lemma": "pressure"},
        "visual_job": {"kind": "constrain", "description": "Show a physical capacity tradeoff."},
    }


def _claim() -> dict[str, object]:
    return {
        "schema_version": "finance_claim_ledger.v1",
        "claim_id": "hbm-capacity-trade-ratio",
        "text": "HBM growth and increasing trade ratio pressure non-HBM supply while greenfield fabs remain slow and complex to build.",
        "classification": "observed_fact",
        "qualifier": "The directional manufacturer statement is not a price forecast.",
        "review_state": "source_checked",
    }


def _world() -> dict[str, object]:
    return {
        "asset_id": "memory-skepticism-v2",
        "sha256": PROFILE_HASH,
        "what_it_is": "A memory stack and skeptical figure with three reserved lower evidence callouts.",
        "visual_role": "hero",
        "semantic_tags": ["memory", "skepticism", "working memory"],
    }


def _snapshot() -> dict[str, object]:
    return {"snapshot_id": "current-bubble-snapshot-v2", "project_profile": {"fps": 30}}


def _motion() -> dict[str, object]:
    return {
        "shots": [
            {
                "shot_id": "finance-shot-054",
                "parent_beat_ids": ["cbm-beat-054"],
                "narration_excerpt": "As manufacturers devote more capacity to HBM",
                "visual_intent": "mechanism",
                "purpose": "reveal",
                "subject_action": "capacity shifts toward a constrained wafer line",
            }
        ]
    }


def _compile(tmp_path: Path, assets: list[dict[str, object]], **overrides: object) -> dict[str, object]:
    approval_assets: list[dict[str, object]] = []
    for asset in assets:
        if isinstance(asset.get("assets"), list):
            approval_assets.extend(item for item in asset["assets"] if isinstance(item, dict))
        else:
            approval_assets.append(asset)
    args: dict[str, object] = {
        "project_id": "current-bubble-mechanism",
        "snapshot": _snapshot(),
        "motion_plan": _motion(),
        "asset_root": tmp_path,
        "approval_ledger": [
            {"asset_id": str(asset["asset_id"]), "status": "approved", "sha256": asset["sha256"]}
            for asset in approval_assets
        ],
    }
    world = overrides.pop("world", _world())
    args.update(overrides)
    return compile_semantic_evidence_binding(_cue(), _beat(), _claim(), world, assets, **args)


def test_reviewed_profiles_are_hash_bound_and_keep_both_current_bubble_plates() -> None:
    profiles = load_plate_layout_profiles()
    assert profiles["memory-skepticism-v2"]["status"] == "reviewed"
    assert profiles["hero-fab-constraint-v1"]["status"] == "reviewed"
    assert profiles["memory-skepticism-v2"]["world_asset_sha256"] == PROFILE_HASH
    assert profiles["hero-fab-constraint-v1"]["evidence_slots"][0]["rect"]["x"] > 0.5
    assert profiles["generic-off-center-v1"]["status"] == "manual_only"


def test_existing_deck_context_is_not_render_eligible_without_promotion(tmp_path: Path) -> None:
    source = ENGINE_ROOT / "projects" / "systems-and-blowups" / "sources" / "decks" / "silicon-antidote" / "semantic-assets" / "asset-context.json"
    context = json.loads(source.read_text(encoding="utf-8"))
    asset = copy.deepcopy(context["assets"][2])
    asset["path"] = "source-context.png"
    source_path = tmp_path / "source-context.png"
    source_path.write_bytes(b"source-context-fixture")
    asset["sha256"] = file_sha256(source_path)
    result = _compile(tmp_path, [asset])
    assert result["recommendation_state"] == "unmatched"
    reasons = result["rejected_candidates"][0]["rejection_reasons"]
    assert "render_not_eligible" in reasons
    assert "review_not_approved_reusable" in reasons
    assert "rights_not_approved" in reasons
    assert "semantic_context_not_operator_verified" in reasons


def test_ranking_is_deterministic_transparent_and_uses_the_next_memory_slot(tmp_path: Path) -> None:
    exact = _asset(
        tmp_path,
        "capacity-penalty-approved",
        cue_refs=["cbm-cue-054"],
        claim_refs=["hbm-capacity-trade-ratio"],
    )
    decoy = _asset(
        tmp_path,
        "valuation-decoy-approved",
        what_it_is="A reviewed valuation balloon with broad market return language.",
        visual_role="evidence",
    )
    first = _compile(tmp_path, [decoy, exact])
    second = _compile(tmp_path, [exact, decoy])
    assert first == second
    assert first["recommendation_state"] == "recommended"
    assert first["proposed_binding"]["asset_id"] == "capacity-penalty-approved"
    assert first["proposed_binding"]["slot_id"] == "teal-callout"
    assert first["proposed_binding"]["frame_range"] == {"start_frame": 5342, "end_frame": 5453}
    assert first["eligible_candidates"][0]["rank"] == 1
    assert first["eligible_candidates"][0]["lead_margin"] > 10
    breakdown = first["eligible_candidates"][0]["score_breakdown"]
    assert breakdown["exact_cue_reference"]["points"] == 26
    assert breakdown["exact_claim_reference"]["points"] == 24
    assert breakdown["concept_overlap"]["details"]
    schema = json.loads((ENGINE_ROOT / "configs" / "semantic_evidence_binding.v1.schema.json").read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(first)) == []

    next_slot = _compile(tmp_path, [exact], occupied_slot_ids=["teal-callout"])
    assert next_slot["recommendation_state"] == "recommended"
    assert next_slot["proposed_binding"]["slot_id"] == "navy-callout"


def test_unapproved_rights_stale_hash_and_path_escape_are_rejected(tmp_path: Path) -> None:
    unapproved = _asset(tmp_path, "review-only", review_state="review_only")
    wrong_rights = _asset(tmp_path, "wrong-rights", rights_state="source_review_only")
    stale_hash = _asset(tmp_path, "stale-hash", declared_hash="b" * 64)
    escaped = _asset(tmp_path, "path-escape", path="../outside.png")
    result = _compile(tmp_path, [unapproved, wrong_rights, stale_hash, escaped])
    assert result["recommendation_state"] == "unmatched"
    by_id = {item["asset_id"]: item["rejection_reasons"] for item in result["rejected_candidates"]}
    assert "review_not_approved_reusable" in by_id["review-only"]
    assert "rights_not_approved" in by_id["wrong-rights"]
    assert "asset_hash_mismatch" in by_id["stale-hash"]
    assert "asset_path_escape" in by_id["path-escape"]
    missing_root = _compile(tmp_path, [_asset(tmp_path, "missing-root")], asset_root=None)
    assert missing_root["recommendation_state"] == "unmatched"
    assert "asset_root_missing" in missing_root["rejected_candidates"][0]["rejection_reasons"]


def test_ambiguous_candidates_fail_closed_and_generic_profile_is_manual_only(tmp_path: Path) -> None:
    first = _asset(tmp_path, "same-a", cue_refs=["cbm-cue-054"], claim_refs=["hbm-capacity-trade-ratio"])
    second = _asset(tmp_path, "same-b", cue_refs=["cbm-cue-054"], claim_refs=["hbm-capacity-trade-ratio"])
    ambiguous = _compile(tmp_path, [first, second])
    assert ambiguous["recommendation_state"] == "unmatched"
    assert ambiguous["recommendation_reason"] == "ambiguous_lead_margin"
    assert ambiguous["proposed_binding"] is None
    assert ambiguous["eligible_candidates"][0]["lead_margin"] == 0

    generic_world = {"asset_id": "unreviewed-world", "sha256": "c" * 64, "what_it_is": "An unreviewed world plate."}
    generic = compile_semantic_evidence_binding(
        _cue(),
        _beat(),
        _claim(),
        generic_world,
        [first],
        project_id="current-bubble-mechanism",
        snapshot=_snapshot(),
        motion_plan=_motion(),
        asset_root=tmp_path,
        profiles=load_plate_layout_profiles(),
    )
    assert generic["recommendation_state"] == "manual_only"
    assert generic["recommendation_reason"] == "generic_profile_requires_manual_review"
    assert generic["world_plate"]["profile_id"] == "generic-off-center-v1"


def test_world_hash_and_deck_context_hash_mismatch_fail_closed(tmp_path: Path) -> None:
    exact = _asset(tmp_path, "valid-candidate", cue_refs=["cbm-cue-054"], claim_refs=["hbm-capacity-trade-ratio"])
    bad_world = dict(_world(), sha256="d" * 64)
    result = _compile(tmp_path, [exact], world=bad_world)
    assert result["recommendation_state"] == "manual_only"
    assert "world_asset_hash_mismatch" in result["binding_errors"]

    stale_container = {
        "schema_version": "deck_asset_context.v1",
        "deck_id": "silicon-antidote",
        "assets": [exact],
        "artifact_hash": "e" * 64,
    }
    result = _compile(tmp_path, [stale_container])
    assert result["recommendation_state"] == "manual_only"
    assert "deck_context_artifact_hash_mismatch:silicon-antidote" in result["binding_errors"]
    assert "deck_context_artifact_hash_mismatch:silicon-antidote" in result["rejected_candidates"][0]["rejection_reasons"]
