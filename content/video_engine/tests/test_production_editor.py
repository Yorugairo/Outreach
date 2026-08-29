from __future__ import annotations

from pathlib import Path
import hashlib
import json

import pytest

from content.video_engine.src.services.production_console_snapshot import compile_production_console_snapshot
from content.video_engine.src.services.production_editor import (
    ProductionEditorError,
    _canonical_hash,
    _compile_semantic_evidence_assets,
    compile_production_editor_snapshot,
    validate_production_editor_snapshot,
)


ROOT = Path(__file__).resolve().parents[3]
PROJECT = (
    ROOT
    / "content"
    / "video_engine"
    / "projects"
    / "systems-and-blowups"
    / "pilots"
    / "current-bubble-mechanism"
)
CATALOG = (
    ROOT
    / "content"
    / "video_engine"
    / "projects"
    / "systems-and-blowups"
    / "sources"
    / "decks"
    / "teacher-stamped-production-visuals"
    / "teacher-stamped-production-visuals-manifest.v1.json"
)


def test_real_current_bubble_snapshot_v2_is_deterministic_and_complete(tmp_path: Path) -> None:
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"
    first = compile_production_editor_snapshot(PROJECT, output_path=first_path)
    second = compile_production_editor_snapshot(PROJECT, output_path=second_path)

    assert first == second
    assert first_path.read_bytes() == second_path.read_bytes()
    assert first["schema_version"] == "production_console_snapshot.v2"
    assert first["project_profile"] == {
        **first["project_profile"],
        "fps": 30,
        "width": 1920,
        "height": 1080,
        "duration_s": 980.806,
        "duration_frames": 29425,
    }
    assert len(first["scenes"]) == 11
    assert len(first["cues"]) == 290
    assert len(first["words"]) == 2445
    assert first["scenes"][0]["start_frame"] == 0
    assert first["scenes"][-1]["end_frame"] == 29425
    assert first["cues"][0]["start_frame"] == 0
    assert first["words"][-1]["end_frame"] == 29425
    assert [track["kind"] for track in first["tracks"]] == [
        "scenes",
        "cues",
        "captions",
        "overlays",
        "teacher_stamp",
        "evidence",
        "world_plates",
        "narration",
    ]
    assert all(track["items"] for track in first["tracks"])
    cue_by_id = {cue["cue_id"]: cue for cue in first["cues"]}
    overlay_items = {
        item["item_id"]: item
        for track in first["tracks"]
        if track["kind"] == "overlays"
        for item in track["items"]
    }
    assert overlay_items["overlay-return-002-1"]["start_frame"] >= cue_by_id["cbm-cue-002"]["start_frame"]
    assert overlay_items["citation-197"]["start_frame"] >= cue_by_id["cbm-cue-197"]["start_frame"]
    assert all(item["overlay_kind"] in {"text", "annotation", "shape", "arrow"} for item in overlay_items.values())
    assert overlay_items["citation-197"]["overlay_kind"] == "annotation"
    assert overlay_items["citation-197"]["citation_id"] == "generational-wealth-return-hurdle"
    assert overlay_items["citation-197"]["diagnostic_label"].endswith("generational-wealth-return-hurdle")
    assert "text" not in overlay_items["citation-197"]
    assert "display_text" not in overlay_items["citation-197"]
    assert all(
        item.get("display_text") not in {item.get("citation_id"), item.get("source_ref")}
        for item in overlay_items.values()
    )
    assert len(first["approved_assets"]) >= 86
    assert len(first["assets"]) >= len(first["approved_assets"])
    assert any(asset["source_kind"] == "project_asset" for asset in first["assets"])
    assert len(first["reviews"]) == 2
    assert first["reviews"][0]["state"] == "approved"
    assert all(asset["approval_scope"] == "production_visuals" for asset in first["approved_assets"])
    assert all(asset["evidence_eligible"] for asset in first["approved_assets"])
    assert first["waveform"]["status"] == "derived"
    assert first["waveform"]["sample_count"] == 256
    assert len(first["waveform"]["peaks"]) == 256
    assert len(first["component_catalog"]["components"]) == 19
    assert sum(item["source"] == "remotion_bits" for item in first["component_catalog"]["components"]) == 11
    assert first["component_catalog"]["catalog_hash"] == first["component_catalog_hash"]
    profiles = {profile["profile_id"]: profile for profile in first["plate_layout_profiles"]["profiles"]}
    assert profiles["memory-skepticism-v2"]["status"] == "reviewed"
    assert [slot["slot_id"] for slot in profiles["memory-skepticism-v2"]["evidence_slots"]] == ["teal-callout", "navy-callout", "orange-callout"]
    assert profiles["hero-fab-constraint-v1"]["evidence_slots"][0]["slot_id"] == "fab-lower-right-inset"
    assert any(asset["asset_id"] == "hero-fab-constraint-v1" for asset in first["assets"])
    asset_map = json.loads((PROJECT / "edit/word-timed-v1/asset-map.v1.json").read_text(encoding="utf-8"))
    expected_plate_ids = {
        asset_id
        for asset_id, record in asset_map["assets"].items()
        if record.get("render_eligible") is True
        and record.get("kind") in {"hero_plate", "generated_hero", "world_board", "mechanism"}
    }
    assert expected_plate_ids <= {asset["asset_id"] for asset in first["assets"]}
    assert all(
        asset["approval_scope"] != "production_visuals"
        for asset in first["assets"]
        if asset["asset_id"] in expected_plate_ids
    )
    sentence_native = [
        asset for asset in first["assets"]
        if str(asset["asset_id"]).startswith("sentence-native-")
    ]
    assert len(sentence_native) == 40
    assert all(asset["approval_scope"] == "review_only" for asset in sentence_native)
    assert all(asset["evidence_eligible"] is False for asset in sentence_native)
    binding = next(record for record in first["semantic_evidence_bindings"] if record["cue_id"] == "cbm-cue-002")
    assert binding["recommendation_state"] == "recommended"
    assert binding["proposed_binding"]["asset_id"] == "silicon-antidote-s02-valuation-bubble-v1"
    assert binding["proposed_binding"]["slot_id"] == "teal-callout"
    caption = next(item for item in first["tracks"][2]["items"] if item["cue_id"] == "cbm-cue-002")
    assert caption["layout"] == {"x": -0.31, "y": -0.42, "width": 0.38, "height": 0.12}
    assert any(record["recommendation_state"] == "unmatched" for record in first["semantic_evidence_bindings"])
    assert any("audio_media: missing" in item for item in first["degraded_inputs"])
    validate_production_editor_snapshot(first)


def test_citation_identifier_cannot_be_promoted_to_display_text(tmp_path: Path) -> None:
    snapshot = compile_production_editor_snapshot(PROJECT, output_path=tmp_path / "snapshot.json")
    citation = next(
        item
        for track in snapshot["tracks"]
        if track["kind"] == "overlays"
        for item in track["items"]
        if item.get("citation_id")
    )
    citation["display_text"] = citation["citation_id"]
    snapshot["artifact_hash"] = _canonical_hash(snapshot, {"artifact_hash"})
    with pytest.raises(ProductionEditorError, match="citation metadata cannot enter normal display text"):
        validate_production_editor_snapshot(snapshot)


def test_semantic_crop_inherits_approval_from_hash_bound_parent_slide(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    project = repository / "content/video_engine/projects/systems-and-blowups/pilots/demo"
    semantic_root = project.parents[1] / "sources/decks/demo-deck/semantic-assets"
    crop = semantic_root / "assets/demo-deck-s03-capacity-v1.png"
    crop.parent.mkdir(parents=True)
    png_header = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + (640).to_bytes(4, "big") + (360).to_bytes(4, "big")
    crop.write_bytes(png_header)
    digest = hashlib.sha256(png_header).hexdigest()
    context = {
        "schema_version": "deck_asset_context.v1",
        "deck_id": "demo-deck",
        "assets": [{
            "asset_id": "demo-deck-s03-capacity-v1",
            "path": "demo-deck/semantic-assets/assets/demo-deck-s03-capacity-v1.png",
            "sha256": digest,
            "slide_number": 3,
            "context": {"what_it_is": "A readable capacity comparison.", "claim_refs": ["claim-1"], "cue_refs": ["cue-1"]},
        }],
    }
    (semantic_root / "asset-context.json").write_text(json.dumps(context), encoding="utf-8")
    parent = {
        "asset_id": "demo-deck-s03-teacher-stamped",
        "deck_id": "demo-deck",
        "slide_number": 3,
        "approval_scope": "production_visuals",
        "evidence_eligible": True,
        "rights_state": "operator_authorized",
    }

    assets, artifacts, degraded = _compile_semantic_evidence_assets(
        [parent], project_root=project, repository_root=repository
    )

    assert degraded == []
    assert assets == [{
        "asset_id": "demo-deck-s03-capacity-v1",
        "label": "demo-deck · Capacity",
        "path_root": "project_family",
        "path": "sources/decks/demo-deck/semantic-assets/assets/demo-deck-s03-capacity-v1.png",
        "sha256": digest,
        "source_kind": "evidence_surface",
        "approval_scope": "production_visuals",
        "evidence_eligible": True,
        "rights_state": "operator_authorized",
        "context_status": "operator_verified",
        "deck_id": "demo-deck",
        "slide_number": 3,
        "width": 640,
        "height": 360,
        "what_it_is": "A readable capacity comparison.",
        "claim_refs": ["claim-1"],
        "cue_refs": ["cue-1"],
    }]
    assert artifacts[0]["artifact_id"] == "semantic_asset_context_demo-deck"


def test_v2_compilation_does_not_change_v1_output() -> None:
    before = compile_production_console_snapshot(
        PROJECT,
        repository_root=ROOT,
        production_visual_catalog=CATALOG,
    )
    compile_production_editor_snapshot(PROJECT)
    after = compile_production_console_snapshot(
        PROJECT,
        repository_root=ROOT,
        production_visual_catalog=CATALOG,
    )
    assert before == after


def test_waveform_cache_is_bound_to_canonical_audio_and_trim_is_frame_bounded() -> None:
    baseline = compile_production_editor_snapshot(PROJECT)
    audio_sha256 = baseline["project_profile"]["audio"]["sha256"]
    cached = compile_production_editor_snapshot(
        PROJECT,
        audio_trim={"start_frame": 30, "end_frame": 60},
        waveform_cache={"audio_sha256": audio_sha256, "peaks": [0.0, 0.25, 1.0]},
    )
    assert cached["project_profile"]["audio_trim"] == {
        "start_s": 1.0,
        "end_s": 2.0,
        "start_frame": 30,
        "end_frame": 60,
    }
    assert cached["waveform"]["status"] == "cached"
    assert cached["waveform"]["sample_count"] == 3
    assert cached["waveform"]["audio_sha256"] == audio_sha256

    with pytest.raises(ProductionEditorError, match="waveform cache is stale"):
        compile_production_editor_snapshot(
            PROJECT,
            waveform_cache={"audio_sha256": "0" * 64, "peaks": [0.5]},
        )
