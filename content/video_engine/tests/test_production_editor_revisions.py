from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from content.video_engine.src.services.production_editor import compile_production_editor_snapshot
from content.video_engine.src.services.production_editor_revisions import (
    ProductionEditorRevisionError,
    list_revisions,
    persist_revision,
    validate_and_replay_revision,
)


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "content" / "video_engine" / "projects" / "systems-and-blowups" / "pilots" / "current-bubble-mechanism"


@pytest.fixture(scope="module")
def snapshot() -> dict:
    return compile_production_editor_snapshot(PROJECT, repository_root=ROOT)


def _hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _revision(snapshot: dict, operations: list[dict], revision_id: str = "revision-proof-001") -> dict:
    core = {
        "schema_version": "editorial_timeline_revision.v1",
        "revision_id": revision_id,
        "revision_only": True,
        "base_snapshot_hash": snapshot["artifact_hash"],
        "base_artifact_hashes": snapshot["base_artifact_hashes"],
        "source_artifact_hashes": snapshot["base_artifact_hashes"],
        "operator": {"operator_id": "test-operator", "created_at": "2026-08-10T12:00:00Z"},
        "operations": operations,
        "note": "P30 round trip",
    }
    return {**core, "artifact_hash": _hash(core)}


def _overlay_item(snapshot: dict) -> dict:
    return {
        "id": "authored-overlay-001",
        "trackId": "track-overlays",
        "kind": "overlay",
        "range": {"startFrame": 30, "endFrame": 180},
        "label": "Operator annotation",
        "locked": False,
        "overlayKind": "text",
        "text": "The valuation paradox",
        "transform": {"x": 0, "y": -0.3, "scaleX": 1, "scaleY": 1, "rotation": 0, "opacity": 1, "zIndex": 60, "crop": {"x": 0, "y": 0, "width": 0.7, "height": 0.2}},
        "keyframes": {},
    }


def _bound_evidence_item(snapshot: dict) -> dict:
    binding = next(record for record in snapshot["semantic_evidence_bindings"] if record["recommendation_state"] == "recommended")
    proposed = binding["proposed_binding"]
    asset = next(record for record in snapshot["approved_assets"] if record["asset_id"] == proposed["asset_id"])
    rect = proposed["slot_rect"]
    return {
        "id": "semantic-evidence-001",
        "trackId": "track-evidence",
        "kind": "evidence",
        "range": {"startFrame": proposed["frame_range"]["start_frame"], "endFrame": proposed["frame_range"]["end_frame"]},
        "label": f'{asset["label"]} · {proposed["slot_id"]}',
        "locked": False,
        "assetId": asset["asset_id"],
        "claimRefs": asset["claim_refs"],
        "evidenceEligible": asset["evidence_eligible"],
        "binding": {
            "bindingId": binding["binding_id"],
            "bindingHash": binding["artifact_hash"],
            "slotId": proposed["slot_id"],
            "worldAssetId": binding["world_plate"]["asset_id"],
        },
        "transform": {
            "x": rect["x"] + rect["width"] / 2 - 0.5,
            "y": rect["y"] + rect["height"] / 2 - 0.5,
            "scaleX": 1,
            "scaleY": 1,
            "rotation": 0,
            "opacity": 1,
            "zIndex": 40,
            "crop": {"x": 0, "y": 0, "width": rect["width"], "height": rect["height"]},
        },
        "keyframes": {},
    }


def test_revision_replays_and_persists_immutable_artifacts(snapshot: dict, tmp_path: Path) -> None:
    revision = _revision(snapshot, [{"op": "insert_item", "item": _overlay_item(snapshot)}])
    validated, document = validate_and_replay_revision(revision, snapshot)
    assert validated["artifact_hash"] == revision["artifact_hash"]
    assert document["items"]["authored-overlay-001"]["text"] == "The valuation paradox"

    receipt = persist_revision(revision, snapshot, tmp_path)
    assert receipt["revision_id"] == "revision-proof-001"
    assert {artifact["artifact_id"] for artifact in receipt["artifacts"]} == {"cue-ranges.v1", "render-input-props", "revision", "scene-ranges.v1", "timeline"}
    assert len(list_revisions(tmp_path)) == 1
    render_input = json.loads((tmp_path / "editorial-revisions" / "revision-proof-001" / "render-input-props.json").read_text(encoding="utf-8"))
    assert render_input["schema_version"] == "production_console_snapshot.v2"
    assert render_input["durationInFrames"] == snapshot["project_profile"]["duration_frames"]
    assert all(item["type"] not in {"scene", "cue"} for item in render_input["items"])
    authored_overlay = next(item for item in render_input["items"] if item["id"] == "authored-overlay-001")
    assert authored_overlay["display_text"] == "The valuation paradox"
    assert "text" not in authored_overlay
    assert render_input["assetMap"][snapshot["project_profile"]["audio"]["audio_id"]].startswith("/media/")
    caption = next(item for item in render_input["items"] if item["id"] == "caption-item-cbm-cue-002")
    assert caption["zIndex"] == 50
    assert caption["layout"] == {"x": -0.31, "y": -0.42, "width": 0.38, "height": 0.12, "scaleX": 1, "scaleY": 1, "rotate": 0}
    assert persist_revision(revision, snapshot, tmp_path) == receipt

    changed = deepcopy(revision)
    changed["note"] = "different immutable content"
    changed["artifact_hash"] = _hash({key: value for key, value in changed.items() if key != "artifact_hash"})
    with pytest.raises(ProductionEditorRevisionError, match="already exists"):
        persist_revision(changed, snapshot, tmp_path)


def test_revision_fails_closed_for_stale_hashes_and_protected_transcript(snapshot: dict) -> None:
    stale = _revision(snapshot, [{"op": "insert_item", "item": _overlay_item(snapshot)}])
    stale["base_snapshot_hash"] = "0" * 64
    stale["artifact_hash"] = _hash({key: value for key, value in stale.items() if key != "artifact_hash"})
    with pytest.raises(ProductionEditorRevisionError, match="stale"):
        validate_and_replay_revision(stale, snapshot)

    caption = snapshot["tracks"][2]["items"][0]["item_id"]
    protected = _revision(snapshot, [{"op": "set_item_props", "item_id": caption, "props": {"text": "rewritten transcript"}}], "revision-protected")
    with pytest.raises(ProductionEditorRevisionError, match="protected"):
        validate_and_replay_revision(protected, snapshot)


def test_revision_rejects_unknown_assets_components_and_word_cuts(snapshot: dict) -> None:
    item = _overlay_item(snapshot)
    item.update({"id": "evidence-unknown", "trackId": "track-evidence", "kind": "evidence", "assetId": "unknown-asset", "claimRefs": [], "evidenceEligible": True})
    item.pop("overlayKind")
    item.pop("text")
    unknown = _revision(snapshot, [{"op": "insert_item", "item": item}], "revision-unknown-asset")
    with pytest.raises(ProductionEditorRevisionError, match="unknown asset"):
        validate_and_replay_revision(unknown, snapshot)

    narration = snapshot["tracks"][-1]["items"][0]["item_id"]
    spoken = next(word for word in snapshot["words"] if word["end_frame"] - word["start_frame"] > 1)
    cut = _revision(snapshot, [{"op": "set_narration_trim_volume", "item_id": narration, "start_frame": spoken["start_frame"] + 1, "end_frame": snapshot["project_profile"]["duration_frames"], "volume": 1}], "revision-word-cut")
    with pytest.raises(ProductionEditorRevisionError, match="spoken word"):
        validate_and_replay_revision(cut, snapshot)


def test_revision_accepts_hash_bound_semantic_evidence_and_rejects_tampering(snapshot: dict) -> None:
    item = _bound_evidence_item(snapshot)
    valid = _revision(snapshot, [{"op": "insert_item", "item": item}], "revision-semantic-evidence")
    _, document = validate_and_replay_revision(valid, snapshot)
    assert document["items"][item["id"]]["binding"]["bindingHash"] == item["binding"]["bindingHash"]

    altered = deepcopy(item)
    altered["binding"]["slotId"] = "unreviewed-slot"
    invalid = _revision(snapshot, [{"op": "insert_item", "item": altered}], "revision-stale-semantic-evidence")
    with pytest.raises(ProductionEditorRevisionError, match="stale or was altered"):
        validate_and_replay_revision(invalid, snapshot)
