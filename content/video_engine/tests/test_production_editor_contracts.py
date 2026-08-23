from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "content" / "video_engine" / "configs"


def _schema(name: str) -> dict:
    return json.loads((CONFIG / name).read_text(encoding="utf-8"))


def _valid(schema_name: str, payload: dict) -> None:
    errors = sorted(Draft202012Validator(_schema(schema_name)).iter_errors(payload), key=str)
    assert not errors, "; ".join(error.message for error in errors)


def _sha(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _catalog_fixture() -> dict:
    component = {
        "component_id": "text-overlay",
        "label": "Text overlay",
        "kind": "text",
        "adapter_id": "text-overlay",
        "source": "builtin",
        "version": "1.0.0",
        "deterministic": True,
        "allowed_prop_keys": ["style_id", "font_size", "color"],
        "preset_ids": ["text-overlay-default"],
    }
    preset = {
        "preset_id": "text-overlay-default",
        "component_id": "text-overlay",
        "label": "Text overlay default",
        "props": {"style_id": "default", "font_size": 48, "color": "#ffffff"},
    }
    core = {
        "schema_version": "editor_component_catalog.v1",
        "catalog_id": "contract-catalog-v1",
        "catalog_version": "1.0.0",
        "remotion_version": "4.0.502",
        "components": [component],
        "presets": [preset],
    }
    digest = _sha(json.dumps(core, sort_keys=True, separators=(",", ":")))
    return {**core, "catalog_hash": digest, "artifact_hash": digest}


def _snapshot_fixture() -> dict:
    digest = "0" * 64
    scene = {
        "scene_id": "scene-001",
        "title": "Opening",
        "start_s": 0,
        "end_s": 1,
        "start_frame": 0,
        "end_frame": 30,
        "cue_refs": ["cue-001"],
        "claim_refs": [],
        "asset_ids": [],
        "review_state": "unreviewed",
    }
    cue = {
        "cue_id": "cue-001",
        "start_word": 0,
        "end_word": 0,
        "start_s": 0,
        "end_s": 1,
        "start_frame": 0,
        "end_frame": 30,
        "excerpt": "Opening",
        "claim_refs": [],
        "state_type": "mechanism",
        "visual_world": "mechanism",
        "entry_action": "cut",
        "exit_transition": "cut",
        "micro_events": [],
        "short_membership": [],
    }
    word = {
        "word_id": "word-00000",
        "text": "Opening",
        "start_s": 0,
        "end_s": 1,
        "start_frame": 0,
        "end_frame": 30,
    }
    tracks = []
    for order, kind in enumerate(
        ["scenes", "cues", "captions", "overlays", "teacher_stamp", "evidence", "world_plates", "narration"]
    ):
        tracks.append(
            {
                "track_id": f"track-{kind}",
                "kind": kind,
                "label": kind.replace("_", " ").title(),
                "order": order,
                "editable": kind not in {"scenes", "cues", "narration"},
                "items": [
                    {
                        "item_id": f"{kind}-001",
                        "item_type": "narration" if kind == "narration" else kind.rstrip("s"),
                        "start_frame": 0,
                        "end_frame": 30,
                        "locked": kind == "narration",
                        "locked_fields": ["audio_source"] if kind == "narration" else [],
                    }
                ],
            }
        )
    # The plural-to-singular conversion above needs the explicit teacher stamp and
    # world plate spellings used by the contract.
    tracks[4]["items"][0]["item_type"] = "teacher_stamp"
    tracks[6]["items"][0]["item_type"] = "world_plate"
    return {
        "schema_version": "production_console_snapshot.v2",
        "snapshot_id": "contract-snapshot-v2",
        "project_id": "contract-project",
        "composition_id": "EditorialMotion",
        "project_profile": {
            "profile_id": "landscape-final-v1",
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "duration_s": 1,
            "duration_frames": 30,
            "audio": {
                "audio_id": "canonical-narration",
                "path": "audio/narration.mp3",
                "sha256": digest,
                "duration_s": 1,
                "status": "missing",
            },
            "audio_trim": {"start_s": 0, "end_s": 1, "start_frame": 0, "end_frame": 30},
        },
        "base_artifact_hashes": {"audio": digest},
        "artifacts": [],
        "scenes": [scene],
        "cues": [cue],
        "words": [word],
        "tracks": tracks,
        "assets": [],
        "approved_assets": [],
        "reviews": [
            {
                "review_id": "teacher-stamped-decks",
                "scope": "production_visuals",
                "state": "approved",
                "artifact_path": "review/approval.json",
                "sha256": digest,
            }
        ],
        "locks": {
            "narration": True,
            "transcript": True,
            "word_timing": True,
            "canonical_audio": True,
            "source_artifacts": True,
            "approved_assets": True,
            "evidence_eligibility": True,
        },
        "waveform": {
            "audio_sha256": digest,
            "source_audio_sha256": digest,
            "cache_key": digest,
            "sample_count": 1,
            "peaks": [0],
            "algorithm": "word_timing_envelope",
            "status": "derived",
        },
        "component_catalog": _catalog_fixture(),
        "component_catalog_hash": _catalog_fixture()["catalog_hash"],
        "plate_layout_profiles": {
            "schema_version": "plate_layout_profiles.v1",
            "profiles": [{"profile_id": "contract-profile"}],
            "artifact_hash": digest,
        },
        "semantic_evidence_bindings": [],
        "degraded_inputs": [],
        "artifact_hash": digest,
    }


def _revision_fixture() -> dict:
    core = {
        "schema_version": "editorial_timeline_revision.v1",
        "revision_id": "revision-001",
        "revision_only": True,
        "base_snapshot_hash": "0" * 64,
        "base_artifact_hashes": {"audio": "0" * 64},
        "source_artifact_hashes": {"audio": "0" * 64},
        "operator": {"operator_id": "operator", "created_at": "2026-08-10T12:00:00Z"},
        "operations": [
            {
                "op": "set_item_props",
                "item_id": "overlay-001",
                "props": {"text": "Reviewed annotation"},
            }
        ],
    }
    return {**core, "artifact_hash": _sha(json.dumps(core, sort_keys=True, separators=(",", ":")))}


def _preset_fixture() -> dict:
    core = {
        "schema_version": "editor_component_preset.v1",
        "preset_id": "text-overlay-default",
        "component_id": "text-overlay",
        "label": "Text overlay default",
        "props": {"style_id": "default", "font_size": 48, "color": "#ffffff"},
        "protected_props": ["asset_sha256"],
    }
    return {**core, "artifact_hash": _sha(json.dumps(core, sort_keys=True, separators=(",", ":")))}


def test_all_p30_contract_fixtures_validate() -> None:
    _valid("production_console_snapshot.v2.schema.json", _snapshot_fixture())
    _valid("editorial_timeline_revision.schema.json", _revision_fixture())
    _valid("editor_component_catalog.schema.json", _catalog_fixture())
    _valid("editor_component_preset.schema.json", _preset_fixture())


def test_timeline_revision_rejects_protected_and_unbounded_fields() -> None:
    protected = _revision_fixture()
    protected["transcript"] = "cannot replace canonical narration"
    assert list(Draft202012Validator(_schema("editorial_timeline_revision.schema.json")).iter_errors(protected))

    unbounded = _revision_fixture()
    unbounded["operations"][0]["value"] = {"arbitrary": {"nested": True}}
    assert list(Draft202012Validator(_schema("editorial_timeline_revision.schema.json")).iter_errors(unbounded))

    too_many = _revision_fixture()
    too_many["operations"] = too_many["operations"] * 1001
    assert list(Draft202012Validator(_schema("editorial_timeline_revision.schema.json")).iter_errors(too_many))


def test_component_contracts_reject_unknown_props_and_protected_snapshot_fields() -> None:
    catalog = _catalog_fixture()
    catalog["components"][0]["execute"] = "javascript:alert(1)"
    assert list(Draft202012Validator(_schema("editor_component_catalog.schema.json")).iter_errors(catalog))

    preset = _preset_fixture()
    preset["props"]["asset_id"] = "untrusted-path"
    assert list(Draft202012Validator(_schema("editor_component_preset.schema.json")).iter_errors(preset))

    snapshot = copy.deepcopy(_snapshot_fixture())
    snapshot["project_profile"]["source_artifacts"] = {"command": "run"}
    assert list(Draft202012Validator(_schema("production_console_snapshot.v2.schema.json")).iter_errors(snapshot))
