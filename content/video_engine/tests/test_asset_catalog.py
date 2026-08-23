from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.asset_catalog import (
    AssetCatalogError,
    load_catalog,
    register_assets,
    resolve_episode_assets,
    resolve_slot,
)

STYLE_V2 = "paper-cut-reduced-density-v2"


def _asset(asset_id: str, *, kind="actor", tier=1, tags=None, style=STYLE_V2,
           render_eligible=True, last_used=None) -> dict:
    asset = {
        "asset_id": asset_id,
        "path": f"assets/generated/cutouts/{asset_id}.png",
        "sha256": "a" * 64,
        "kind": kind,
        "style_version": style,
        "semantic_tags": tags or ["worker"],
        "visual_worlds": ["story"],
        "identity_lenses": ["working-household"],
        "resolution_tier": tier,
        "render_eligible": render_eligible,
    }
    if last_used is not None:
        asset["last_used_episode"] = last_used
    return asset


def _catalog(*assets) -> dict:
    return {
        "schema_version": "finance_asset_catalog.v1",
        "project_root": "content/video_engine/projects/systems-and-blowups",
        "resolution_order": [
            "exact_semantic_match",
            "reusable_component_composition",
            "deterministic_evidence_or_mechanism",
            "bespoke_plate",
        ],
        "assets": list(assets),
    }


def _slot(slot_id: str, intent: str, **extra) -> dict:
    slot = {
        "slot_id": slot_id,
        "narration_excerpt": "line",
        "visual_intent": intent,
        "visual_archetype": "typography_explainer",
        "motion_recipe": "detail_punch",
        "duration_s": 4.0,
    }
    slot.update(extra)
    return slot


def _coverage(*slots) -> dict:
    return {
        "schema_version": "editorial_coverage.v1",
        "artifact_hash": "b" * 64,
        "slots": list(slots),
    }


def test_cascade_prefers_the_earliest_tier():
    catalog = _catalog(
        _asset("actor-worker-v1", tier=1, tags=["worker"]),
        _asset("prop-worker-kit-v1", kind="prop", tier=2, tags=["worker"]),
    )

    result = resolve_slot(_slot("s1", "a worker at the desk"), catalog)

    assert result["asset_id"] == "actor-worker-v1"
    assert result["resolved_tier"] == "exact_semantic_match"


def test_falls_through_to_the_next_tier_when_the_first_is_empty():
    catalog = _catalog(_asset("prop-basket-v1", kind="prop", tier=2, tags=["index", "basket"]))

    result = resolve_slot(_slot("s1", "an index basket of shares"), catalog)

    assert result["asset_id"] == "prop-basket-v1"
    assert result["resolved_tier"] == "reusable_component_composition"


def test_unmatched_slot_falls_through_to_bespoke():
    catalog = _catalog(_asset("actor-worker-v1", tags=["worker"]))

    result = resolve_slot(_slot("s1", "a lunar orbital transfer"), catalog)

    assert result["asset_id"] is None
    assert result["resolved_tier"] == "bespoke_plate"


def test_evidence_tier_only_matches_mechanism_or_board_kinds():
    catalog = _catalog(
        _asset("prop-decoy-v1", kind="prop", tier=3, tags=["ownership"]),
        _asset("mechanism-ownership-tree-v1", kind="mechanism", tier=3, tags=["ownership"]),
    )

    result = resolve_slot(_slot("s1", "an ownership structure"), catalog)

    assert result["asset_id"] == "mechanism-ownership-tree-v1"


def test_render_never_resolves_a_non_promoted_asset():
    catalog = _catalog(_asset("actor-worker-v1", tags=["worker"], render_eligible=False))
    slot = _slot("s1", "a worker at the desk")

    assert resolve_slot(slot, catalog, for_render=False)["asset_id"] == "actor-worker-v1"
    assert resolve_slot(slot, catalog, for_render=True)["asset_id"] is None


def test_mixed_style_versions_in_one_episode_are_rejected_naming_both():
    catalog = _catalog(
        _asset("actor-worker-v1", tags=["worker"], style=STYLE_V2),
        _asset("actor-founder-v1", tags=["founder"], style="crinkle-cut-v1"),
    )
    coverage = _coverage(_slot("s1", "a worker"), _slot("s2", "a founder"))

    with pytest.raises(AssetCatalogError) as excinfo:
        resolve_episode_assets(coverage, catalog)

    joined = " ".join(excinfo.value.errors)
    assert STYLE_V2 in joined
    assert "crinkle-cut-v1" in joined


def test_single_style_version_passes():
    catalog = _catalog(
        _asset("actor-worker-v1", tags=["worker"]),
        _asset("actor-founder-v1", tags=["founder"]),
    )
    report = resolve_episode_assets(
        _coverage(_slot("s1", "a worker"), _slot("s2", "a founder")), catalog
    )

    assert report["style_version"] == STYLE_V2


def test_gap_report_is_the_generation_worklist():
    catalog = _catalog(_asset("actor-worker-v1", tags=["worker"]))
    coverage = _coverage(
        _slot("s1", "a worker at the desk"),
        _slot("s2", "a lunar orbital transfer"),
        _slot("s3", "a deep sea trench"),
    )

    report = resolve_episode_assets(coverage, catalog)

    assert report["slot_count"] == 3
    assert report["resolved_count"] == 1
    assert {gap["slot_id"] for gap in report["gaps"]} == {"s2", "s3"}
    assert report["gaps"][0]["visual_intent"]


def test_coverage_ratio_reports_library_reach():
    catalog = _catalog(_asset("actor-worker-v1", tags=["worker"]))
    report = resolve_episode_assets(
        _coverage(_slot("s1", "a worker"), _slot("s2", "something unknown")), catalog
    )

    assert report["coverage_ratio"] == 0.5


def test_resolution_is_deterministic_across_runs():
    catalog = _catalog(
        _asset("actor-worker-a-v1", tags=["worker"]),
        _asset("actor-worker-b-v1", tags=["worker"]),
    )
    coverage = _coverage(_slot("s1", "a worker at the desk"))

    first = resolve_episode_assets(coverage, catalog)
    second = resolve_episode_assets(coverage, catalog)

    assert first["artifact_hash"] == second["artifact_hash"]
    assert first["resolutions"] == second["resolutions"]


def test_pruning_candidates_surface_idle_assets():
    catalog = _catalog(
        _asset("actor-worker-v1", tags=["worker"], last_used=12),
        _asset("actor-stale-v1", tags=["founder"], last_used=2),
    )
    report = resolve_episode_assets(
        _coverage(_slot("s1", "a worker")), catalog, episode_number=12
    )

    assert [entry["asset_id"] for entry in report["pruning_candidates"]] == ["actor-stale-v1"]
    assert report["pruning_candidates"][0]["episodes_idle"] == 10


def test_missing_style_version_is_rejected_by_the_schema():
    asset = _asset("actor-worker-v1")
    del asset["style_version"]

    with pytest.raises(AssetCatalogError) as excinfo:
        load_catalog(_catalog(asset))

    assert any("style_version" in error for error in excinfo.value.errors)


def test_duplicate_asset_id_is_rejected():
    catalog = _catalog(_asset("actor-worker-v1"), _asset("actor-worker-v1"))

    with pytest.raises(AssetCatalogError) as excinfo:
        load_catalog(catalog)

    assert any("more than once" in error for error in excinfo.value.errors)


def test_registration_grows_the_library(tmp_path):
    catalog = _catalog(_asset("actor-worker-v1", tags=["worker"]))
    summary = register_assets(
        catalog,
        [_asset("prop-index-basket-v1", kind="prop", tier=2, tags=["index", "basket"])],
        output_path=tmp_path / "asset-catalog.v1.json",
    )
    grown = json.loads(Path(summary["catalog_path"]).read_text(encoding="utf-8"))

    assert summary["added"] == ["prop-index-basket-v1"]
    assert summary["asset_count"] == 2
    assert len(grown["assets"]) == 2


def test_accretion_closes_the_gap_it_reported(tmp_path):
    # The loop that makes each episode cheaper than the last.
    catalog = _catalog(_asset("actor-worker-v1", tags=["worker"]))
    coverage = _coverage(_slot("s1", "a worker"), _slot("s2", "an index basket of shares"))

    before = resolve_episode_assets(coverage, catalog)
    assert [gap["slot_id"] for gap in before["gaps"]] == ["s2"]

    summary = register_assets(
        catalog,
        [_asset("prop-index-basket-v1", kind="prop", tier=2, tags=["index", "basket"])],
        output_path=tmp_path / "asset-catalog.v1.json",
    )
    after = resolve_episode_assets(coverage, summary["catalog_path"])

    assert after["gaps"] == []
    assert after["coverage_ratio"] == 1.0


def test_registering_a_duplicate_is_rejected(tmp_path):
    catalog = _catalog(_asset("actor-worker-v1"))

    with pytest.raises(AssetCatalogError) as excinfo:
        register_assets(
            catalog, [_asset("actor-worker-v1")], output_path=tmp_path / "c.json"
        )

    assert any("already in the catalogue" in error for error in excinfo.value.errors)


def test_registering_without_style_version_is_rejected(tmp_path):
    catalog = _catalog(_asset("actor-worker-v1"))
    incoming = _asset("prop-new-v1", kind="prop")
    del incoming["style_version"]

    with pytest.raises(AssetCatalogError) as excinfo:
        register_assets(catalog, [incoming], output_path=tmp_path / "c.json")

    assert any("style_version is required" in error for error in excinfo.value.errors)


def test_a_one_word_coincidence_does_not_pre_empt_a_real_match_at_a_later_tier():
    """The cascade breaks ties; it does not let a weak match win on position.

    Regression from the episode-1 library build: 15 host and civilian poses were
    registered at the composition tier carrying pose-purpose tags such as
    "comparison", "caution" and "risk". A mechanism slot then resolved to
    ``actor-host-explain-both-hands-v1`` on the single word "comparison",
    because the composition tier is walked before the mechanism tier and the
    first tier with *any* candidate returned immediately. The actor overlapped
    on one term; the mechanism overlapped on two.
    """

    catalog = _catalog(
        _asset(
            "actor-host-explain-v1",
            kind="actor",
            tier=2,
            tags=["finance-host", "presenter", "comparison"],
        ),
        _asset(
            "mechanism-growth-comparison-v1",
            kind="mechanism",
            tier=3,
            tags=["growth-comparison", "comparison", "bar-comparison"],
        ),
    )
    slot = {
        "slot_id": "slot-1",
        "visual_intent": "two bars, one taller",
        "visual_archetype": "mechanism",
        "semantic_tags": ["comparison", "bar-comparison"],
        "narration_excerpt": "one grew faster than the other",
    }

    resolved = resolve_slot(slot, catalog)

    assert resolved["asset_id"] == "mechanism-growth-comparison-v1"
    assert resolved["resolved_tier"] == "deterministic_evidence_or_mechanism"


def test_the_cascade_still_wins_when_the_overlap_is_equal():
    """Equal strength must still resolve to the earlier tier."""

    catalog = _catalog(
        _asset("actor-worker-v1", kind="actor", tier=2, tags=["worker"]),
        _asset("mechanism-worker-v1", kind="mechanism", tier=3, tags=["worker"]),
    )
    slot = {
        "slot_id": "slot-1",
        "visual_intent": "a worker",
        "semantic_tags": ["worker"],
        "narration_excerpt": "",
    }

    assert resolve_slot(slot, catalog)["asset_id"] == "actor-worker-v1"


def test_declared_style_families_let_compatible_directions_composite():
    """A label mismatch is not a compositing failure.

    The episode-1 library proved the guard was too crude: the host carried
    ``paper-cut-reduced-density-v2`` and the civilians ``woodblock-finance-
    editorial-v3``, yet they were generated as one cast and composite cleanly on
    a shared world. Exact-string equality blocked a frame that visibly reads as
    one picture. A catalogue may therefore declare which versions belong to the
    same family; the guard compares families and only then falls back to the
    version string.
    """

    catalog = _catalog(
        _asset("actor-host-v1", kind="actor", tier=2, tags=["host"],
               style="paper-cut-reduced-density-v2"),
        _asset("actor-civilian-v1", kind="actor", tier=2, tags=["civilian"],
               style="woodblock-finance-editorial-v3"),
    )
    catalog["style_families"] = {
        "ep1-cast": ["paper-cut-reduced-density-v2", "woodblock-finance-editorial-v3"]
    }
    coverage = _coverage(
        {"slot_id": "s1", "visual_intent": "host", "semantic_tags": ["host"],
         "narration_excerpt": ""},
        {"slot_id": "s2", "visual_intent": "civilian", "semantic_tags": ["civilian"],
         "narration_excerpt": ""},
    )

    report = resolve_episode_assets(coverage, catalog)

    assert report["resolved_count"] == 2


def test_versions_in_different_families_are_still_rejected():
    catalog = _catalog(
        _asset("actor-host-v1", kind="actor", tier=2, tags=["host"],
               style="paper-cut-reduced-density-v2"),
        _asset("actor-old-v1", kind="actor", tier=2, tags=["civilian"],
               style="crinkle-cut-v1"),
    )
    catalog["style_families"] = {
        "ep1": ["paper-cut-reduced-density-v2", "woodblock-finance-editorial-v3"],
        "legacy": ["crinkle-cut-v1"],
    }
    coverage = _coverage(
        {"slot_id": "s1", "visual_intent": "host", "semantic_tags": ["host"],
         "narration_excerpt": ""},
        {"slot_id": "s2", "visual_intent": "civilian", "semantic_tags": ["civilian"],
         "narration_excerpt": ""},
    )

    with pytest.raises(AssetCatalogError) as excinfo:
        resolve_episode_assets(coverage, catalog)

    joined = " ".join(excinfo.value.errors)
    assert "ep1" in joined and "legacy" in joined


def test_without_declared_families_the_version_string_still_governs():
    catalog = _catalog(
        _asset("actor-a-v1", kind="actor", tier=2, tags=["host"], style="style-a"),
        _asset("actor-b-v1", kind="actor", tier=2, tags=["civilian"], style="style-b"),
    )
    coverage = _coverage(
        {"slot_id": "s1", "visual_intent": "host", "semantic_tags": ["host"],
         "narration_excerpt": ""},
        {"slot_id": "s2", "visual_intent": "civilian", "semantic_tags": ["civilian"],
         "narration_excerpt": ""},
    )

    with pytest.raises(AssetCatalogError):
        resolve_episode_assets(coverage, catalog)


def _world(asset_id, *, figure_height=0.50, ref=None) -> dict:
    asset = _asset(asset_id, kind="world_board", tier=2, tags=["room"])
    asset["placement"] = {
        "figure_zone": [0.55, 1.0],
        "baseline_y": 0.98,
        "figure_height": figure_height,
    }
    if ref is not None:
        asset["scale_reference"] = ref
    return asset


def test_a_world_drawn_at_the_wrong_human_scale_is_rejected():
    """Furniture size is what sets figure size, and nothing was checking it.

    The episode-1 interiors were drawn as close-up rooms: their chair and sofa
    backs occupy 0.45 of frame height, which puts a correctly-scaled adult at
    ~0.92 of the frame. Composited at the 0.50 standard the figures read as dolls
    beside furniture built for giants. The defect is in the plate, not the
    compositor, and it is arithmetic — so it is caught here rather than on screen.
    """

    catalog = _catalog(
        _world(
            "world-office-desk-v1",
            figure_height=0.50,
            ref={"object": "chair back", "real_height_m": 0.85, "drawn_height": 0.45},
        )
    )

    with pytest.raises(AssetCatalogError) as excinfo:
        load_catalog(catalog)

    joined = " ".join(excinfo.value.errors)
    assert "0.9" in joined, joined      # names the implied height
    assert "0.5" in joined, joined      # and the declared one


def test_a_world_drawn_at_the_right_human_scale_passes():
    # A balustrade rail at 0.32 of frame implies an adult at 0.53 — within
    # tolerance of the 0.50 standard.
    catalog = _catalog(
        _world(
            "world-exchange-floor-v1",
            figure_height=0.50,
            ref={"object": "balustrade rail", "real_height_m": 1.05, "drawn_height": 0.32},
        )
    )

    assert load_catalog(catalog)["assets"][0]["asset_id"] == "world-exchange-floor-v1"


def test_a_world_without_a_declared_scale_reference_is_not_blocked():
    """Backwards compatible: the check runs only where a reference is declared."""

    assert load_catalog(_catalog(_world("world-plain-v1")))


def _layered(asset_id, layers) -> dict:
    asset = _asset(asset_id, kind="world_board", tier=2, tags=["room"])
    asset["placement"] = {"figure_zone": [0.55, 1.0], "baseline_y": 0.98,
                          "figure_height": 0.50}
    asset["layers"] = layers
    return asset


def test_a_2_5d_world_must_declare_its_layers_back_to_front():
    """Parallax needs separated planes; a flat plate has nothing to move.

    P13 already renders bounded foreground parallax and P14 already names the
    depth layers. The missing piece was that worlds shipped as one flat image, so
    the renderer had nothing to separate. A layered world declares its planes in
    back-to-front order and every plane must be a declared depth layer.
    """

    catalog = _catalog(_layered("world-hall-v1", [
        {"depth_layer": "building_or_environment", "path": "a-far.png", "sha256": "a"*64},
        {"depth_layer": "not_a_layer", "path": "a-mid.png", "sha256": "b"*64},
    ]))

    with pytest.raises(AssetCatalogError) as excinfo:
        load_catalog(catalog)

    assert any("not_a_layer" in e for e in excinfo.value.errors)


def test_a_layered_world_needs_a_background_plane():
    catalog = _catalog(_layered("world-hall-v1", [
        {"depth_layer": "actor_or_machine", "path": "a-mid.png", "sha256": "a"*64},
        {"depth_layer": "foreground_cutout", "path": "a-near.png", "sha256": "b"*64},
    ]))

    with pytest.raises(AssetCatalogError) as excinfo:
        load_catalog(catalog)

    assert any("building_or_environment" in e for e in excinfo.value.errors)


def test_a_well_formed_layered_world_passes():
    catalog = _catalog(_layered("world-hall-v1", [
        {"depth_layer": "building_or_environment", "path": "a-far.png", "sha256": "a"*64},
        {"depth_layer": "actor_or_machine", "path": "a-mid.png", "sha256": "b"*64},
        {"depth_layer": "foreground_cutout", "path": "a-near.png", "sha256": "c"*64},
    ]))

    assert load_catalog(catalog)["assets"][0]["layers"][0]["depth_layer"] == "building_or_environment"


def test_a_flat_world_is_still_valid():
    assert load_catalog(_catalog(_world("world-flat-v1")))
