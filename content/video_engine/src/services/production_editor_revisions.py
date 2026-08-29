"""Fail-closed immutable P30 editorial timeline revisions."""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from jsonschema import Draft202012Validator


ALLOWED_EASINGS = {"linear", "ease_in", "ease_out", "ease_in_out"}
ALLOWED_SPRINGS = {"gentle", "snappy", "bouncy"}
ANIMATABLE_PROPERTIES = {"x", "y", "scaleX", "scaleY", "rotation", "opacity", "zIndex"}
VISUAL_TYPES = {"caption", "overlay", "teacher_stamp", "evidence", "world_plate", "remotion_bit"}


class ProductionEditorRevisionError(RuntimeError):
    def __init__(self, code: str, message: str, *, path: str | None = None) -> None:
        self.code = code
        self.message = message
        self.path = path
        super().__init__(message)


def _canonical_bytes(value: Mapping[str, Any], *, exclude: Sequence[str] = ()) -> bytes:
    core = {key: item for key, item in value.items() if key not in set(exclude)}
    return json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _canonical_hash(value: Mapping[str, Any], *, exclude: Sequence[str] = ()) -> str:
    return hashlib.sha256(_canonical_bytes(value, exclude=exclude)).hexdigest()


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "configs" / "editorial_timeline_revision.schema.json"


def _load_schema() -> dict[str, Any]:
    value = json.loads(_schema_path().read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProductionEditorRevisionError("SCHEMA_INVALID", "timeline revision schema is invalid")
    return value


def _stable_item(raw: Mapping[str, Any], track_id: str) -> dict[str, Any]:
    item = {
        "id": str(raw["item_id"]),
        "track_id": track_id,
        "kind": str(raw["item_type"]),
        "start_frame": int(raw["start_frame"]),
        "end_frame": int(raw["end_frame"]),
        "locked": bool(raw["locked"]),
        "locked_fields": list(raw.get("locked_fields", [])),
        **{key: raw[key] for key in raw if key not in {"item_id", "item_type", "start_frame", "end_frame", "locked", "locked_fields"}},
    }
    kind = item["kind"]
    if kind in VISUAL_TYPES:
        layout = raw.get("layout") if isinstance(raw.get("layout"), Mapping) else {}
        default_y = 0.3 if kind == "caption" else 0
        default_height = 0.2 if kind == "caption" else 1
        z_index = {"caption": 50, "overlay": 60, "teacher_stamp": 80, "evidence": 40, "world_plate": 0, "remotion_bit": 70}[kind]
        item["transform"] = {
            "x": float(layout.get("x", 0)),
            "y": float(layout.get("y", default_y)),
            "scaleX": 1,
            "scaleY": 1,
            "rotation": 0,
            "opacity": 1,
            "zIndex": z_index,
            "crop": {
                "x": 0,
                "y": 0,
                "width": float(layout.get("width", 1)),
                "height": float(layout.get("height", default_height)),
            },
        }
    return item


def timeline_from_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    tracks: list[dict[str, Any]] = []
    for raw_track in snapshot["tracks"]:
        tracks.append(
            {
                "track_id": raw_track["track_id"],
                "kind": raw_track["kind"],
                "label": raw_track["label"],
                "editable": raw_track["editable"],
                "item_ids": [item["item_id"] for item in raw_track["items"]],
            }
        )
    items = {
        item["item_id"]: _stable_item(item, track["track_id"])
        for track in snapshot["tracks"]
        for item in track["items"]
    }
    for item in items.values():
        if item["kind"] == "cue" and not item.get("scene_id"):
            scene = next(
                (
                    candidate
                    for candidate in snapshot["scenes"]
                    if int(candidate["start_frame"]) <= item["start_frame"]
                    and item["end_frame"] <= int(candidate["end_frame"])
                ),
                None,
            )
            if scene is not None:
                item["scene_id"] = scene["scene_id"]
    return {
        "schema_version": "editorial_timeline_document.v1",
        "project_id": snapshot["project_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "base_snapshot_hash": snapshot["artifact_hash"],
        "fps": snapshot["project_profile"]["fps"],
        "width": snapshot["project_profile"]["width"],
        "height": snapshot["project_profile"]["height"],
        "duration_frames": snapshot["project_profile"]["duration_frames"],
        "tracks": tracks,
        "items": items,
        "source_item_ids": sorted(items),
        "review_notes": [],
        "review_status": "draft",
    }


def _require_item(document: Mapping[str, Any], item_id: Any) -> dict[str, Any]:
    if not isinstance(item_id, str) or item_id not in document["items"]:
        raise ProductionEditorRevisionError("UNKNOWN_ITEM", "revision references an unknown timeline item", path="item_id")
    return document["items"][item_id]


def _frame_range(operation: Mapping[str, Any], duration: int) -> tuple[int, int]:
    start = operation.get("start_frame")
    end = operation.get("end_frame")
    if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= duration:
        raise ProductionEditorRevisionError("INVALID_FRAME_RANGE", "frame range is outside the episode", path="start_frame")
    return start, end


def _validate_transform(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ProductionEditorRevisionError("INVALID_PROPS", "transform must be an object", path="props.transform")
    allowed = {"x", "y", "scaleX", "scaleY", "rotation", "opacity", "zIndex", "crop"}
    if set(value) - allowed:
        raise ProductionEditorRevisionError("UNSUPPORTED_PROP", "transform contains an unsupported field", path="props.transform")
    result = dict(value)
    for key in allowed - {"crop"}:
        if key in result and (isinstance(result[key], bool) or not isinstance(result[key], (int, float))):
            raise ProductionEditorRevisionError("INVALID_PROPS", f"transform {key} must be numeric", path=f"props.transform.{key}")
    if "opacity" in result and not 0 <= float(result["opacity"]) <= 1:
        raise ProductionEditorRevisionError("INVALID_PROPS", "opacity must be in [0, 1]", path="props.transform.opacity")
    if "crop" in result:
        crop = result["crop"]
        if not isinstance(crop, Mapping) or set(crop) - {"x", "y", "width", "height"}:
            raise ProductionEditorRevisionError("INVALID_PROPS", "crop is invalid", path="props.transform.crop")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in crop.values()):
            raise ProductionEditorRevisionError("INVALID_PROPS", "crop values must be numeric", path="props.transform.crop")
    return result


def _word_gap(frame: int, words: Sequence[Mapping[str, Any]]) -> bool:
    return not any(int(word["start_frame"]) < frame < int(word["end_frame"]) for word in words)


def _validate_inserted_item(item: Any, snapshot: Mapping[str, Any], document: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(item, Mapping):
        raise ProductionEditorRevisionError("INVALID_ITEM", "inserted item must be an object", path="item")
    required = {"id", "trackId", "kind", "range", "label", "locked"}
    if not required <= set(item):
        raise ProductionEditorRevisionError("INVALID_ITEM", "inserted item is missing required fields", path="item")
    item_id = item["id"]
    if not isinstance(item_id, str) or item_id in document["items"]:
        raise ProductionEditorRevisionError("INVALID_ITEM", "inserted item ID is invalid or already exists", path="item.id")
    if item["kind"] not in VISUAL_TYPES or item["kind"] == "caption" or item["locked"] is not False:
        raise ProductionEditorRevisionError("PROTECTED_ITEM", "only unlocked authored visual items may be inserted", path="item.kind")
    track = next((candidate for candidate in document["tracks"] if candidate["track_id"] == item["trackId"]), None)
    if track is None or not track["editable"]:
        raise ProductionEditorRevisionError("PROTECTED_TRACK", "target track is not editable", path="item.trackId")
    range_value = item["range"]
    if not isinstance(range_value, Mapping):
        raise ProductionEditorRevisionError("INVALID_FRAME_RANGE", "inserted item range is invalid", path="item.range")
    start, end = _frame_range({"start_frame": range_value.get("startFrame"), "end_frame": range_value.get("endFrame")}, int(document["duration_frames"]))
    known_assets = {asset["asset_id"] for asset in snapshot["assets"]}
    if item["kind"] in {"evidence", "world_plate"} and item.get("assetId") not in known_assets:
        raise ProductionEditorRevisionError("UNKNOWN_ASSET", "inserted visual references an unknown asset", path="item.assetId")
    if item["kind"] == "evidence":
        source = next(asset for asset in snapshot["assets"] if asset["asset_id"] == item["assetId"])
        if bool(item.get("evidenceEligible")) != bool(source["evidence_eligible"]):
            raise ProductionEditorRevisionError("APPROVAL_CHANGE", "evidence eligibility cannot be changed", path="item.evidenceEligible")
        binding = item.get("binding")
        if binding is not None:
            if not isinstance(binding, Mapping):
                raise ProductionEditorRevisionError("INVALID_BINDING", "evidence binding must be an object", path="item.binding")
            record = next(
                (
                    candidate
                    for candidate in snapshot.get("semantic_evidence_bindings", [])
                    if candidate.get("binding_id") == binding.get("bindingId")
                ),
                None,
            )
            proposed = record.get("proposed_binding") if isinstance(record, Mapping) else None
            if (
                record is None
                or record.get("artifact_hash") != binding.get("bindingHash")
                or record.get("recommendation_state") != "recommended"
                or not isinstance(proposed, Mapping)
                or proposed.get("asset_id") != item.get("assetId")
                or proposed.get("slot_id") != binding.get("slotId")
                or record.get("world_plate", {}).get("asset_id") != binding.get("worldAssetId")
            ):
                raise ProductionEditorRevisionError("STALE_BINDING", "evidence recommendation is stale or was altered", path="item.binding")
    if item["kind"] == "remotion_bit":
        known_components = {component["component_id"] for component in snapshot["component_catalog"]["components"] if component["source"] == "remotion_bits"}
        if item.get("componentId") not in known_components:
            raise ProductionEditorRevisionError("UNKNOWN_COMPONENT", "Remotion Bit is not enabled", path="item.componentId")
    return {
        "id": item_id,
        "track_id": item["trackId"],
        "kind": item["kind"],
        "start_frame": start,
        "end_frame": end,
        "label": str(item["label"]),
        "locked": False,
        "locked_fields": [],
        **{key: value for key, value in item.items() if key not in {"id", "trackId", "kind", "range", "label", "locked"}},
    }


def _apply_operation(document: dict[str, Any], snapshot: Mapping[str, Any], operation: Mapping[str, Any]) -> None:
    name = operation["op"]
    duration = int(document["duration_frames"])
    if name == "set_scene_boundary":
        scene_id = operation["scene_id"]
        item = next((value for value in document["items"].values() if value["kind"] == "scene" and value.get("scene_id") == scene_id), None)
        if item is None:
            raise ProductionEditorRevisionError("UNKNOWN_SCENE", "revision references an unknown scene")
        item["start_frame"], item["end_frame"] = _frame_range(operation, duration)
    elif name == "set_cue_range":
        cue_id = operation["cue_id"]
        item = next((value for value in document["items"].values() if value["kind"] == "cue" and value.get("cue_id") == cue_id), None)
        if item is None:
            raise ProductionEditorRevisionError("UNKNOWN_CUE", "revision references an unknown cue")
        item["start_frame"], item["end_frame"] = _frame_range(operation, duration)
    elif name == "set_narration_trim_volume":
        item = _require_item(document, operation["item_id"])
        if item["kind"] != "narration":
            raise ProductionEditorRevisionError("PROTECTED_ITEM", "narration controls target narration only")
        start, end = _frame_range(operation, duration)
        if not _word_gap(start, snapshot["words"]) or not _word_gap(end, snapshot["words"]):
            raise ProductionEditorRevisionError("WORD_CUT", "narration trim cannot cut through a spoken word")
        volume = operation["volume"]
        if isinstance(volume, bool) or not isinstance(volume, (int, float)) or not 0 <= volume <= 1:
            raise ProductionEditorRevisionError("INVALID_VOLUME", "narration volume must be in [0, 1]")
        item["start_frame"], item["end_frame"], item["volume"] = start, end, float(volume)
    elif name == "insert_item":
        item = _validate_inserted_item(operation["item"], snapshot, document)
        document["items"][item["id"]] = item
        next(track for track in document["tracks"] if track["track_id"] == item["track_id"])["item_ids"].append(item["id"])
    elif name == "remove_item":
        item = _require_item(document, operation["item_id"])
        if item["locked"] or item["kind"] in {"scene", "cue", "caption", "narration"}:
            raise ProductionEditorRevisionError("PROTECTED_ITEM", "canonical timeline items cannot be removed")
        document["items"].pop(item["id"])
        next(track for track in document["tracks"] if track["track_id"] == item["track_id"])["item_ids"].remove(item["id"])
    elif name == "move_trim_item":
        item = _require_item(document, operation["item_id"])
        if item["locked"] or item["kind"] not in VISUAL_TYPES:
            raise ProductionEditorRevisionError("PROTECTED_ITEM", "item range is protected")
        item["start_frame"], item["end_frame"] = _frame_range(operation, duration)
    elif name == "set_item_props":
        item = _require_item(document, operation["item_id"])
        if item["locked"] or item["kind"] not in VISUAL_TYPES:
            raise ProductionEditorRevisionError("PROTECTED_ITEM", "item properties are protected")
        props = operation["props"]
        if not isinstance(props, Mapping):
            raise ProductionEditorRevisionError("INVALID_PROPS", "item props must be an object")
        allowed = {"label", "transform"}
        if item["kind"] == "overlay":
            allowed.add("text")
        if item["kind"] == "remotion_bit":
            allowed |= {"component_id", "preset_id", "props"}
        if set(props) - allowed:
            raise ProductionEditorRevisionError("PROTECTED_FIELD", "item props attempt to change a protected field")
        if "transform" in props:
            props = {**props, "transform": _validate_transform(props["transform"])}
        item.update(dict(props))
    elif name == "set_item_keyframes":
        item = _require_item(document, operation["item_id"])
        if item["locked"] or item["kind"] not in VISUAL_TYPES:
            raise ProductionEditorRevisionError("PROTECTED_ITEM", "item keyframes are protected")
        tracks = operation["keyframes"]
        if not isinstance(tracks, Mapping) or set(tracks) - ANIMATABLE_PROPERTIES:
            raise ProductionEditorRevisionError("INVALID_KEYFRAMES", "keyframe properties are not allowlisted")
        for property_name, keyframes in tracks.items():
            if not isinstance(keyframes, list):
                raise ProductionEditorRevisionError("INVALID_KEYFRAMES", "keyframe track must be an array")
            frames: list[int] = []
            for keyframe in keyframes:
                if not isinstance(keyframe, Mapping) or not isinstance(keyframe.get("frame"), int) or not isinstance(keyframe.get("value"), (int, float)):
                    raise ProductionEditorRevisionError("INVALID_KEYFRAMES", "keyframe is malformed")
                if not item["start_frame"] <= keyframe["frame"] <= item["end_frame"]:
                    raise ProductionEditorRevisionError("INVALID_KEYFRAMES", "keyframe is outside its item")
                if keyframe.get("easing", "linear") not in ALLOWED_EASINGS or ("springPreset" in keyframe and keyframe["springPreset"] not in ALLOWED_SPRINGS):
                    raise ProductionEditorRevisionError("INVALID_KEYFRAMES", "keyframe easing is not approved")
                frames.append(keyframe["frame"])
            if len(frames) != len(set(frames)) or frames != sorted(frames):
                raise ProductionEditorRevisionError("INVALID_KEYFRAMES", "keyframes must be unique and ordered")
        item["keyframes"] = dict(tracks)
    elif name == "reorder_item":
        track = next((candidate for candidate in document["tracks"] if candidate["track_id"] == operation["track_id"]), None)
        if track is None or not track["editable"]:
            raise ProductionEditorRevisionError("PROTECTED_TRACK", "track order is protected")
        item_ids = operation["item_ids"]
        if not isinstance(item_ids, list) or set(item_ids) != set(track["item_ids"]) or len(item_ids) != len(set(item_ids)):
            raise ProductionEditorRevisionError("INVALID_ORDER", "reorder operation must preserve the exact item set")
        track["item_ids"] = list(item_ids)
    elif name == "apply_component_preset":
        item = _require_item(document, operation["item_id"])
        catalog = snapshot["component_catalog"]
        preset = next((candidate for candidate in catalog["presets"] if candidate["preset_id"] == operation["preset_id"] and candidate["component_id"] == operation["component_id"]), None)
        if item["locked"] or preset is None:
            raise ProductionEditorRevisionError("UNKNOWN_PRESET", "component preset is not enabled")
        item["component_id"], item["preset_id"], item["component_props"] = operation["component_id"], operation["preset_id"], preset["props"]
    elif name == "set_caption_layout":
        item = _require_item(document, operation["item_id"])
        if item["kind"] != "caption":
            raise ProductionEditorRevisionError("PROTECTED_TRANSCRIPT", "caption layout target is invalid")
        item["style_id"] = operation["style_id"]
        item["line_breaks"] = list(operation.get("line_breaks", []))
        item["group_id"] = operation.get("group_id")
    elif name == "add_review_note":
        document["review_notes"].append({"text": operation["text"], "item_id": operation.get("item_id")})
    elif name == "set_review_status":
        document["review_status"] = operation["status"]
    else:
        raise ProductionEditorRevisionError("UNKNOWN_OPERATION", "revision operation is not supported", path="op")


def _validate_semantics(document: Mapping[str, Any], snapshot: Mapping[str, Any]) -> None:
    duration = int(document["duration_frames"])
    scenes = sorted((item for item in document["items"].values() if item["kind"] == "scene"), key=lambda item: item["start_frame"])
    if not scenes or scenes[0]["start_frame"] != 0 or scenes[-1]["end_frame"] != duration:
        raise ProductionEditorRevisionError("SCENE_CONTIGUITY", "scenes must cover the complete episode")
    for left, right in zip(scenes, scenes[1:]):
        if left["end_frame"] != right["start_frame"]:
            raise ProductionEditorRevisionError("SCENE_CONTIGUITY", "scenes must remain contiguous and ordered")
    scene_by_id = {item.get("scene_id"): item for item in scenes}
    for cue in (item for item in document["items"].values() if item["kind"] == "cue"):
        scene = scene_by_id.get(cue.get("scene_id"))
        if scene is None or not scene["start_frame"] <= cue["start_frame"] < cue["end_frame"] <= scene["end_frame"]:
            raise ProductionEditorRevisionError("CUE_CONTAINMENT", "cue must remain inside its parent scene")
    known_assets = {asset["asset_id"]: asset for asset in snapshot["assets"]}
    for item in document["items"].values():
        asset_id = item.get("assetId") or item.get("asset_id")
        if item["id"] not in document["source_item_ids"] and item["kind"] in {"evidence", "world_plate"} and asset_id is not None and asset_id not in known_assets:
            raise ProductionEditorRevisionError("UNKNOWN_ASSET", "timeline contains an unknown asset")
    authored_evidence = sorted(
        (item for item in document["items"].values() if item["kind"] == "evidence" and item["id"] not in document["source_item_ids"]),
        key=lambda item: (item["start_frame"], item["end_frame"], item["id"]),
    )
    for left, right in zip(authored_evidence, authored_evidence[1:]):
        if right["start_frame"] < left["end_frame"]:
            raise ProductionEditorRevisionError("CLUTTER_BUDGET", "only one evidence card may be active at a frame")


def validate_and_replay_revision(revision: Mapping[str, Any], snapshot: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(revision, Mapping):
        raise ProductionEditorRevisionError("INVALID_REVISION", "revision must be an object")
    errors = sorted(Draft202012Validator(_load_schema()).iter_errors(dict(revision)), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        raise ProductionEditorRevisionError("SCHEMA_INVALID", error.message, path="/".join(map(str, error.absolute_path)))
    if revision["artifact_hash"] != _canonical_hash(revision, exclude=("artifact_hash",)):
        raise ProductionEditorRevisionError("HASH_MISMATCH", "revision artifact hash does not match its content")
    if revision["base_snapshot_hash"] != snapshot["artifact_hash"]:
        raise ProductionEditorRevisionError("STALE_SNAPSHOT", "revision base snapshot is stale")
    if dict(revision["base_artifact_hashes"]) != dict(snapshot["base_artifact_hashes"]) or dict(revision["source_artifact_hashes"]) != dict(snapshot["base_artifact_hashes"]):
        raise ProductionEditorRevisionError("STALE_SOURCE", "revision source artifact hashes are stale")
    try:
        datetime.fromisoformat(str(revision["operator"]["created_at"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProductionEditorRevisionError("INVALID_OPERATOR", "operator timestamp is invalid") from exc
    document = timeline_from_snapshot(snapshot)
    for operation in revision["operations"]:
        _apply_operation(document, snapshot, operation)
    _validate_semantics(document, snapshot)
    timeline_hash = _canonical_hash(document)
    document["artifact_hash"] = timeline_hash
    return dict(revision), document


def _write_new(path: Path, payload: Mapping[str, Any]) -> None:
    if path.exists():
        raise ProductionEditorRevisionError("REVISION_EXISTS", "immutable revision artifact already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _composition_render_input(document: Mapping[str, Any], snapshot: Mapping[str, Any], revision_id: str) -> dict[str, Any]:
    """Compile replayed state into the same prop shape used by the Player."""
    items: list[dict[str, Any]] = []
    for source in document["items"].values():
        kind = source["kind"]
        if kind in {"scene", "cue"}:
            continue
        transform = source.get("transform", {})
        crop = transform.get("crop", {}) if isinstance(transform, Mapping) else {}
        layout = {
            "x": transform.get("x", 0), "y": transform.get("y", 0),
            "width": crop.get("width", 1), "height": crop.get("height", 1),
            "scaleX": transform.get("scaleX", 1), "scaleY": transform.get("scaleY", 1),
            "rotate": transform.get("rotation", 0),
        }
        item: dict[str, Any] = {
            "id": source["id"], "type": kind, "from": source["start_frame"],
            "durationInFrames": source["end_frame"] - source["start_frame"],
            "zIndex": transform.get("zIndex", 0), "opacity": transform.get("opacity", 1), "layout": layout,
        }
        asset_id = source.get("assetId") or source.get("asset_id")
        if kind == "caption":
            item["text"] = source.get("text") or source.get("excerpt", "")
            item["caption_preset"] = "word_by_word" if source.get("style_id") == "word_by_word" else "compact"
            start_word = int(source.get("start_word", 0))
            end_word = int(source.get("end_word", start_word))
            item["word_tokens"] = [
                {
                    "text": word["text"],
                    "startFrame": int(word["start_frame"]) - int(source["start_frame"]),
                    "endFrame": int(word["end_frame"]) - int(source["start_frame"]),
                }
                for word in snapshot["words"][start_word : end_word + 1]
            ]
        elif kind == "overlay":
            item["type"] = "overlay" if source.get("overlayKind", "text") == "text" else "annotation"
            if source.get("text"):
                item["display_text"] = source["text"]
            if asset_id:
                item["assetId"] = asset_id
        elif kind == "teacher_stamp":
            item.update({"assetId": asset_id, "text": source.get("label", "Teacher stamp")})
        elif kind == "evidence":
            item.update({"assetId": asset_id, "label": source.get("label", "Evidence")})
        elif kind == "world_plate":
            item.update({"assetId": asset_id, "label": source.get("label", "World plate")})
            item["layout"]["fit"] = source.get("fit", "cover")
        elif kind == "remotion_bit":
            item.update({"bit_id": source.get("componentId") or source.get("component_id"), "bit_props": source.get("props") or source.get("component_props", {}), "keyframes": source.get("keyframes", {})})
        elif kind == "narration":
            item.update({"assetId": asset_id or source.get("source_ref"), "volume": source.get("volume", 1)})
        items.append(item)

    asset_map = {asset["asset_id"]: f"/media/{quote(str(asset['asset_id']), safe='')}" for asset in snapshot["assets"]}
    audio_id = snapshot["project_profile"]["audio"]["audio_id"]
    asset_map[audio_id] = f"/media/{quote(str(audio_id), safe='')}"
    return {
        "schema_version": "production_console_snapshot.v2", "revision_id": revision_id,
        "base_snapshot_hash": snapshot["artifact_hash"], "timeline_hash": document["artifact_hash"],
        "width": document["width"], "height": document["height"], "fps": document["fps"],
        "durationInFrames": document["duration_frames"], "items": items, "assetMap": asset_map,
        "backgroundColor": "#0b1015",
    }


def persist_revision(revision: Mapping[str, Any], snapshot: Mapping[str, Any], runtime_root: str | Path) -> dict[str, Any]:
    validated, document = validate_and_replay_revision(revision, snapshot)
    root = Path(runtime_root).resolve()
    revision_id = str(validated["revision_id"])
    destination = (root / "editorial-revisions" / revision_id).resolve()
    if root not in destination.parents:
        raise ProductionEditorRevisionError("UNSAFE_PATH", "revision destination is unsafe")
    revision_path = destination / "revision.json"
    if revision_path.exists():
        existing = json.loads(revision_path.read_text(encoding="utf-8"))
        if existing.get("artifact_hash") == validated["artifact_hash"]:
            return revision_receipt(destination, validated, document)
        raise ProductionEditorRevisionError("REVISION_EXISTS", "revision ID already exists with different content")
    destination.mkdir(parents=True, exist_ok=False)
    try:
        _write_new(revision_path, validated)
        _write_new(destination / "timeline.json", document)
        _write_new(destination / "scene-ranges.v1.json", {"schema_version": "editor_scene_ranges.v1", "base_snapshot_hash": snapshot["artifact_hash"], "scenes": [item for item in document["items"].values() if item["kind"] == "scene"]})
        _write_new(destination / "cue-ranges.v1.json", {"schema_version": "editor_cue_ranges.v1", "base_snapshot_hash": snapshot["artifact_hash"], "cues": [item for item in document["items"].values() if item["kind"] == "cue"]})
        _write_new(destination / "render-input-props.json", _composition_render_input(document, snapshot, revision_id))
    except Exception:
        for child in destination.glob("*"):
            child.unlink(missing_ok=True)
        destination.rmdir()
        raise
    return revision_receipt(destination, validated, document)


def revision_receipt(destination: Path, revision: Mapping[str, Any], document: Mapping[str, Any]) -> dict[str, Any]:
    artifacts = []
    for path in sorted(destination.glob("*.json")):
        artifacts.append({"artifact_id": path.stem, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return {"schema_version": "editorial_timeline_revision_receipt.v1", "revision_id": revision["revision_id"], "artifact_hash": revision["artifact_hash"], "timeline_hash": document["artifact_hash"], "artifacts": artifacts}


def list_revisions(runtime_root: str | Path) -> list[dict[str, Any]]:
    root = Path(runtime_root).resolve() / "editorial-revisions"
    if not root.is_dir():
        return []
    result = []
    for path in sorted(root.glob("*/revision.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            result.append({"revision_id": value["revision_id"], "artifact_hash": value["artifact_hash"], "operator": value["operator"], "note": value.get("note")})
        except (OSError, KeyError, json.JSONDecodeError):
            continue
    return result


__all__ = ["ProductionEditorRevisionError", "list_revisions", "persist_revision", "timeline_from_snapshot", "validate_and_replay_revision"]
