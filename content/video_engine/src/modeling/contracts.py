"""Validation for immutable model assets, authored scenes and inspections.

These contracts point at the existing asset catalogue and approval records. A
model descriptor cannot grant itself approval or make an ineligible catalogue
asset renderable.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from jsonschema import Draft7Validator

_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_ROOT = _ENGINE_ROOT / "configs"
_SCHEMA_FILES = {
    "asset": "model_asset.v1.schema.json",
    "scene": "model_scene.v1.schema.json",
    "inspection": "model_inspection.v1.schema.json",
}
_ASSET_CATALOG_SCHEMA = _CONFIG_ROOT / "asset_catalog.schema.json"
_APPROVED_REVIEW_STATES = {"approved_reusable", "operator_approved"}


class ModelContractError(ValueError):
    """A model contract failed schema, linkage, path, hash or capability checks."""

    def __init__(self, errors: list[str] | tuple[str, ...]):
        self.errors = tuple(str(error) for error in errors)
        super().__init__("; ".join(self.errors) or "invalid model contract")


def _load_document(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    path = Path(value)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ModelContractError([f"{label}: cannot read JSON document: {exc}"]) from exc
    if not isinstance(document, dict):
        raise ModelContractError([f"{label}: document must be a JSON object"])
    return document


def _finite_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, float) and not math.isfinite(value):
        errors.append(f"{path}: number must be finite")
    elif isinstance(value, Mapping):
        for key, child in value.items():
            errors.extend(_finite_errors(child, f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            errors.extend(_finite_errors(child, f"{path}[{index}]"))
    return errors


def _schema_errors(payload: Mapping[str, Any], schema_name: str) -> list[str]:
    schema_path = _CONFIG_ROOT / _SCHEMA_FILES[schema_name]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft7Validator.check_schema(schema)
    except Exception as exc:
        # A broken checked-in contract must fail closed with a useful location.
        return [f"{schema_name}: cannot load schema {schema_path}: {exc}"]
    validator = Draft7Validator(schema)
    return [
        f"{schema_name}{''.join(f'[{part!r}]' for part in error.absolute_path)}: {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda err: tuple(str(part) for part in err.absolute_path))
    ]


def _safe_file(root: Path, relative_path: Any, expected_sha256: Any, label: str) -> tuple[Path | None, bytes | None, list[str]]:
    errors: list[str] = []
    if not isinstance(relative_path, str) or not relative_path:
        return None, None, [f"{label}: path must be a non-empty relative path"]
    if "\\" in relative_path or ":" in relative_path or relative_path.startswith("/"):
        return None, None, [f"{label}: path must be a normalized root-relative POSIX path"]
    pure = PurePosixPath(relative_path)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        return None, None, [f"{label}: path escapes or is not normalized under the project root"]
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        return None, None, [f"{label}: expected SHA-256 must be 64 lowercase hexadecimal characters"]
    try:
        root_resolved = root.resolve(strict=True)
        candidate = root_resolved.joinpath(*pure.parts).resolve(strict=True)
        candidate.relative_to(root_resolved)
    except (OSError, ValueError):
        return None, None, [f"{label}: path is missing or resolves outside the project root"]
    if not candidate.is_file():
        return None, None, [f"{label}: path is not a file"]
    try:
        contents = candidate.read_bytes()
    except OSError as exc:
        return None, None, [f"{label}: cannot read file: {exc}"]
    digest = hashlib.sha256(contents).hexdigest()
    if digest != expected_sha256:
        errors.append(f"{label}: SHA-256 does not match local bytes")
    return candidate, contents, errors


def _trusted_anchor(root: Path, value: str | Path | None, label: str) -> tuple[Path | None, list[str]]:
    """Resolve a caller-owned trust anchor and require it to live under root."""
    if value is None:
        return None, [f"{label}: caller-supplied trusted path is required"]
    try:
        root_resolved = root.resolve(strict=True)
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = root_resolved / candidate
        candidate = candidate.resolve(strict=True)
        candidate.relative_to(root_resolved)
    except (OSError, ValueError):
        return None, [f"{label}: trusted path is missing or resolves outside the project root"]
    if not candidate.is_file():
        return None, [f"{label}: trusted path is not a file"]
    return candidate, []


def _json_file(contents: bytes | None, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    if contents is None:
        return None, [f"{label}: referenced JSON bytes are unavailable"]
    try:
        value = json.loads(contents.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        return None, [f"{label}: referenced file is not valid UTF-8 JSON: {exc}"]
    if not isinstance(value, dict):
        return None, [f"{label}: referenced document must be a JSON object"]
    return value, []


def _resource_map(payload: Mapping[str, Any], label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    resources = payload.get("resources")
    if not isinstance(resources, list):
        return {}
    found: dict[str, dict[str, Any]] = {}
    seen_paths: set[str] = set()
    for index, resource in enumerate(resources):
        if not isinstance(resource, Mapping):
            continue
        resource_id = resource.get("resource_id")
        path = resource.get("path")
        if isinstance(resource_id, str):
            if resource_id in found:
                errors.append(f"{label}: duplicate resource_id {resource_id!r}")
            found[resource_id] = dict(resource)
        if isinstance(path, str):
            if path in seen_paths:
                errors.append(f"{label}: resource path {path!r} is repeated")
            seen_paths.add(path)
    return found


def _approval_id(record: Mapping[str, Any]) -> Any:
    for key in ("approval_id", "authorization_id", "record_id"):
        if key in record:
            return record[key]
    return None


def _approval_covers(record: Mapping[str, Any], *, asset_id: str, resource: Mapping[str, Any]) -> bool:
    path = resource.get("path")
    digest = resource.get("sha256")
    rows: list[Mapping[str, Any]] = []
    for key in ("assets", "approved_assets", "selected_assets"):
        values = record.get(key)
        if isinstance(values, list):
            rows.extend(row for row in values if isinstance(row, Mapping))
    single = record.get("asset")
    if isinstance(single, Mapping):
        rows.append(single)

    # Approval documents may bind one asset at the top level or list it in
    # selected_assets, but every match must name the exact asset ID and bytes.
    top_level = dict(record)
    top_level.setdefault("path", record.get("candidate_path"))
    top_level.setdefault("sha256", record.get("asset_sha256"))
    rows.append(top_level)
    for row in rows:
        row_id = row.get("asset_id", row.get("id"))
        row_path = row.get("path", row.get("candidate_path", row.get("resource_path")))
        row_hash = row.get("sha256", row.get("asset_sha256"))
        if row_path == path and row_hash == digest and row_id == asset_id:
            return True
    return False


def _validate_asset_payload(
    payload: Mapping[str, Any],
    project_root: Path,
    *,
    for_render: bool = False,
    trusted_catalog_path: str | Path | None = None,
    trusted_approval_path: str | Path | None = None,
) -> list[str]:
    errors = _finite_errors(payload) + _schema_errors(payload, "asset")
    if errors:
        return errors

    asset_id = str(payload["asset_id"])
    coordinate_system = payload["coordinate_system"]
    if coordinate_system.get("space") == "world_3d" and coordinate_system.get("up_axis") == coordinate_system.get("forward_axis"):
        errors.append("model_asset: up_axis and forward_axis must be distinct")
    resources = _resource_map(payload, "model_asset", errors)
    catalog_ref = payload["catalog_reference"]
    approval_ref = payload["approval_reference"]
    if catalog_ref.get("resource_id") != approval_ref.get("resource_id"):
        errors.append("model_asset: catalog and approval references must bind the same resource_id")
    trusted_catalog: Path | None = None
    trusted_approval: Path | None = None
    if for_render:
        trusted_catalog, anchor_errors = _trusted_anchor(project_root, trusted_catalog_path, "trusted_catalog_path")
        errors.extend(anchor_errors)
        trusted_approval, anchor_errors = _trusted_anchor(project_root, trusted_approval_path, "trusted_approval_path")
        errors.extend(anchor_errors)
    for ref_name, ref, label in (
        ("catalog_reference", catalog_ref, "asset catalog"),
        ("approval_reference", approval_ref, "approval record"),
    ):
        resource_id = ref.get("resource_id")
        if resource_id not in resources:
            errors.append(f"model_asset: {ref_name} points at missing resource_id {resource_id!r}")

    for resource_id, resource in resources.items():
        _, _, file_errors = _safe_file(project_root, resource.get("path"), resource.get("sha256"), f"resource {resource_id}")
        errors.extend(file_errors)
    resource_ids = set(resources)
    uv_sets = payload.get("uv_sets", [])
    uv_ids = {uv_set.get("uv_set_id") for uv_set in uv_sets if isinstance(uv_set, Mapping)}
    for index, uv_set in enumerate(uv_sets):
        if isinstance(uv_set, Mapping):
            missing = sorted(set(uv_set.get("texture_resource_ids", [])) - resource_ids)
            if missing:
                errors.append(f"uv_sets[{index}]: unknown texture resource id(s): {', '.join(missing)}")
    for index, material in enumerate(payload.get("materials", [])):
        if not isinstance(material, Mapping):
            continue
        if material.get("uv_set_id") not in uv_ids:
            errors.append(f"materials[{index}]: uv_set_id does not resolve to a declared UV set")
        missing = sorted(set(material.get("texture_resource_ids", [])) - resource_ids)
        if missing:
            errors.append(f"materials[{index}]: unknown texture resource id(s): {', '.join(missing)}")
    envelope = payload.get("view_envelope")
    if isinstance(envelope, Mapping):
        for range_name, angle_range in envelope.items():
            if isinstance(angle_range, Mapping) and angle_range.get("minimum", 0) > angle_range.get("maximum", 0):
                errors.append(f"view_envelope.{range_name}: minimum must not exceed maximum")
    for index, source in enumerate(payload["source_lineage"]):
        _, _, file_errors = _safe_file(project_root, source.get("path"), source.get("sha256"), f"source_lineage[{index}]")
        errors.extend(file_errors)

    catalog_path, catalog_bytes, file_errors = _safe_file(
        project_root, catalog_ref.get("path"), catalog_ref.get("sha256"), "catalog_reference"
    )
    errors.extend(file_errors)
    catalog: dict[str, Any] | None = None
    if not file_errors:
        catalog, json_errors = _json_file(catalog_bytes, "catalog_reference")
        errors.extend(json_errors)
    catalog_row: dict[str, Any] | None = None
    if catalog is not None:
        try:
            catalog_schema = json.loads(_ASSET_CATALOG_SCHEMA.read_text(encoding="utf-8"))
            catalog_errors = [
                f"catalog_reference{''.join(f'[{part!r}]' for part in error.absolute_path)}: {error.message}"
                for error in sorted(
                    Draft7Validator(catalog_schema).iter_errors(catalog),
                    key=lambda err: tuple(str(part) for part in err.absolute_path),
                )
            ]
            errors.extend(catalog_errors)
        except Exception as exc:
            errors.append(f"catalog_reference: cannot load existing catalogue schema: {exc}")
        rows = catalog.get("assets")
        if not isinstance(rows, list):
            errors.append("catalog_reference: existing catalogue has no assets array")
        else:
            matches = [row for row in rows if isinstance(row, Mapping) and row.get("asset_id") == catalog_ref.get("asset_id")]
            if len(matches) != 1:
                errors.append("catalog_reference: asset_id must resolve to exactly one existing catalogue row")
            else:
                catalog_row = dict(matches[0])
                if catalog_ref.get("asset_id") != asset_id:
                    errors.append("catalog_reference: asset_id does not match the model descriptor")
                if for_render and trusted_catalog is not None and catalog_path != trusted_catalog:
                    errors.append("catalog_reference: path does not match caller-supplied trusted catalogue")
                linked = resources.get(catalog_ref.get("resource_id"))
                if linked is not None and (catalog_row.get("path") != linked.get("path") or catalog_row.get("sha256") != linked.get("sha256")):
                    errors.append("catalog_reference: catalogue row path/hash does not match the referenced immutable resource")
                if for_render:
                    if catalog_row.get("render_eligible") is not True:
                        errors.append("catalog_reference: existing catalogue row is not render eligible")
                    review_state = catalog_row.get("review_state")
                    if review_state not in _APPROVED_REVIEW_STATES:
                        errors.append("catalog_reference: existing catalogue row has no approved review_state")
                    if review_state == "operator_approved":
                        provenance = catalog_row.get("provenance")
                        if not isinstance(provenance, Mapping) or not provenance.get("approved_by") or not provenance.get("approved_on"):
                            errors.append("catalog_reference: operator_approved row requires provenance.approved_by and approved_on")

    approval_path, approval_bytes, file_errors = _safe_file(
        project_root, approval_ref.get("path"), approval_ref.get("sha256"), "approval_reference"
    )
    errors.extend(file_errors)
    approval: dict[str, Any] | None = None
    if not file_errors:
        approval, json_errors = _json_file(approval_bytes, "approval_reference")
        errors.extend(json_errors)
    if approval is not None:
        if _approval_id(approval) != approval_ref.get("record_id"):
            errors.append("approval_reference: record_id does not match the existing approval document")
        linked = resources.get(approval_ref.get("resource_id"))
        if linked is not None and not _approval_covers(approval, asset_id=asset_id, resource=linked):
            errors.append("approval_reference: existing record is not linked to the exact asset id/path/hash")
        if for_render and trusted_approval is not None and approval_path != trusted_approval:
            errors.append("approval_reference: path does not match caller-supplied trusted approval record")

    return errors


def validate_model_asset(
    value: Mapping[str, Any] | str | Path,
    *,
    project_root: str | Path,
    for_render: bool = False,
    trusted_catalog_path: str | Path | None = None,
    trusted_approval_path: str | Path | None = None,
) -> dict[str, Any]:
    """Validate one immutable model revision and its existing source records.

    ``for_render`` additionally checks the existing catalogue's eligibility and
    review state. The trusted paths must come from caller-owned project config,
    never from this descriptor. This cannot grant approval by itself.
    """

    payload = _load_document(value, "model_asset")
    errors = _validate_asset_payload(
        payload,
        Path(project_root),
        for_render=for_render,
        trusted_catalog_path=trusted_catalog_path,
        trusted_approval_path=trusted_approval_path,
    )
    if errors:
        raise ModelContractError(errors)
    return payload


def _load_bound_assets(
    payload: Mapping[str, Any],
    root: Path,
    errors: list[str],
    *,
    for_render: bool = False,
    trusted_catalog_path: str | Path | None = None,
    trusted_approval_path: str | Path | None = None,
) -> dict[str, dict[str, Any]]:
    binding_map: dict[str, dict[str, Any]] = {}
    for index, binding in enumerate(payload.get("bindings", [])):
        if not isinstance(binding, Mapping):
            continue
        binding_id = binding.get("binding_id")
        if not isinstance(binding_id, str):
            continue
        if binding_id in binding_map:
            errors.append(f"model_scene: duplicate binding_id {binding_id!r}")
            continue
        _, descriptor_bytes, file_errors = _safe_file(
            root, binding.get("descriptor_path"), binding.get("descriptor_sha256"), f"bindings[{index}].descriptor"
        )
        errors.extend(file_errors)
        descriptor: dict[str, Any] | None = None
        if not file_errors:
            descriptor, json_errors = _json_file(descriptor_bytes, f"bindings[{index}].descriptor")
            errors.extend(json_errors)
        if descriptor is not None:
            asset_errors = _validate_asset_payload(
                descriptor,
                root,
                for_render=for_render,
                trusted_catalog_path=trusted_catalog_path,
                trusted_approval_path=trusted_approval_path,
            )
            errors.extend(f"bindings[{index}]: {error}" for error in asset_errors)
            if descriptor.get("asset_id") != binding.get("asset_id"):
                errors.append(f"bindings[{index}]: asset_id does not match the referenced descriptor")
            if (descriptor.get("revision") or {}).get("revision_id") != binding.get("revision_id"):
                errors.append(f"bindings[{index}]: revision_id does not match the referenced descriptor")
        binding_map[binding_id] = {**dict(binding), "descriptor": descriptor}
    return binding_map


def _capabilities(binding: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not binding:
        return {}
    descriptor = binding.get("descriptor")
    if not isinstance(descriptor, Mapping):
        return {}
    capabilities = descriptor.get("capabilities")
    return capabilities if isinstance(capabilities, Mapping) else {}


def _validate_scene_payload(
    payload: Mapping[str, Any],
    project_root: Path,
    *,
    for_render: bool = False,
    trusted_catalog_path: str | Path | None = None,
    trusted_approval_path: str | Path | None = None,
) -> list[str]:
    errors = _finite_errors(payload) + _schema_errors(payload, "scene")
    if errors:
        return errors
    bindings = _load_bound_assets(
        payload,
        project_root,
        errors,
        for_render=for_render,
        trusted_catalog_path=trusted_catalog_path,
        trusted_approval_path=trusted_approval_path,
    )
    duration = int(payload["duration_frames"])
    fps = payload["fps"]
    if fps["denominator"] <= 0 or fps["numerator"] <= 0:
        errors.append("model_scene: fps numerator and denominator must be positive")

    for index, mapping in enumerate(payload["source_time_mappings"]):
        _, _, file_errors = _safe_file(project_root, mapping.get("path"), mapping.get("sha256"), f"source_time_mappings[{index}]")
        errors.extend(file_errors)
        start, end = mapping["scene_frame_start"], mapping["scene_frame_end"]
        if start >= end or end > duration:
            errors.append(f"source_time_mappings[{index}]: interval must satisfy 0 <= start < end <= duration_frames")
        if mapping["source_seconds_per_scene_frame"]["numerator"] <= 0:
            errors.append(f"source_time_mappings[{index}]: source-time scale must be positive")
    participant_ids: set[str] = set()
    for index, participant in enumerate(payload["participants"]):
        participant_id = participant["participant_id"]
        if participant_id in participant_ids:
            errors.append(f"participants[{index}]: duplicate participant_id {participant_id!r}")
        participant_ids.add(participant_id)
        binding = bindings.get(participant["binding_id"])
        descriptor = binding.get("descriptor") if binding else None
        if not binding:
            errors.append(f"participants[{index}]: unknown binding_id {participant['binding_id']!r}")
            continue
        if not isinstance(descriptor, Mapping) or descriptor.get("asset_kind") != "character":
            errors.append(f"participants[{index}]: participant binding must reference a character asset")
            continue
        capabilities = _capabilities(binding)
        missing_joints = sorted(set(participant["semantic_joint_requirements"]) - set(capabilities.get("semantic_joints", [])))
        missing_face = sorted(set(participant["face_control_requirements"]) - set(capabilities.get("face_controls", [])))
        if missing_joints:
            errors.append(f"participants[{index}]: unsupported semantic joint(s): {', '.join(missing_joints)}")
        if missing_face:
            errors.append(f"participants[{index}]: unsupported face control(s): {', '.join(missing_face)}")

    for index, attachment in enumerate(payload["attachments"]):
        parent = bindings.get(attachment["parent_binding_id"])
        child = bindings.get(attachment["child_binding_id"])
        if not parent or not child:
            errors.append(f"attachments[{index}]: parent and child binding ids must resolve")
            continue
        parent_sockets = set(_capabilities(parent).get("sockets", []))
        child_sockets = set(_capabilities(child).get("sockets", []))
        if attachment["parent_socket"] not in parent_sockets:
            errors.append(f"attachments[{index}]: parent socket {attachment['parent_socket']!r} is not declared by its asset")
        if attachment["child_socket"] not in child_sockets:
            errors.append(f"attachments[{index}]: child socket {attachment['child_socket']!r} is not declared by its asset")

    for index, surface in enumerate(payload.get("environment_collision_surfaces", [])):
        binding = bindings.get(surface["binding_id"])
        descriptor = binding.get("descriptor") if binding else None
        if not isinstance(descriptor, Mapping) or descriptor.get("asset_kind") != "environment":
            errors.append(f"environment_collision_surfaces[{index}]: binding must reference an environment asset")
            continue
        declared = [
            item for item in _capabilities(binding).get("surfaces", [])
            if isinstance(item, Mapping) and item.get("surface_id") == surface["surface_id"]
        ]
        if len(declared) != 1:
            errors.append(f"environment_collision_surfaces[{index}]: surface_id is not declared by the environment asset")
        elif declared[0].get("collision_role") == "visual_only" and surface["collision_mode"] != "disabled":
            errors.append(f"environment_collision_surfaces[{index}]: visual-only surface cannot be enabled for collision")

    camera = payload.get("camera")
    if isinstance(camera, Mapping):
        clip_near, clip_far = camera["clip_planes_m"]
        if clip_near >= clip_far:
            errors.append("camera.clip_planes_m must satisfy near < far")

    channel_ids: set[str] = set()
    for index, channel in enumerate(payload.get("motion_channels", [])):
        channel_id = channel["channel_id"]
        if channel_id in channel_ids:
            errors.append(f"motion_channels[{index}]: duplicate channel_id {channel_id!r}")
        channel_ids.add(channel_id)
        binding = bindings.get(channel["binding_id"])
        if not binding:
            errors.append(f"motion_channels[{index}]: unknown binding_id {channel['binding_id']!r}")
            continue
        capabilities = _capabilities(binding)
        supported = {
            "semantic_joint": set(capabilities.get("semantic_joints", [])),
            "face_control": set(capabilities.get("face_controls", [])),
            "articulation": set(capabilities.get("articulations", [])),
            "object_transform": {channel["semantic_target"]},
        }[channel["target_kind"]]
        if channel["semantic_target"] not in supported:
            errors.append(f"motion_channels[{index}]: target is not supported by the bound asset capability profile")
        previous_frame = -1
        expected_shape = {"vector3_m": 3, "quaternion": 4}.get(channel["value_unit"])
        for keyframe_index, keyframe in enumerate(channel["keyframes"]):
            frame = keyframe["frame"]
            if frame >= duration:
                errors.append(f"motion_channels[{index}].keyframes[{keyframe_index}]: frame must be less than duration_frames")
            if frame <= previous_frame:
                errors.append(f"motion_channels[{index}]: keyframe frames must be strictly increasing")
            previous_frame = frame
            value = keyframe["value"]
            if expected_shape is None and not isinstance(value, (int, float)):
                errors.append(f"motion_channels[{index}].keyframes[{keyframe_index}]: scalar value_unit requires a number")
            elif expected_shape is not None and (not isinstance(value, list) or len(value) != expected_shape):
                errors.append(f"motion_channels[{index}].keyframes[{keyframe_index}]: value shape does not match value_unit")

    for index, contact in enumerate(payload["contacts"]):
        start, end = contact["start_frame"], contact["end_frame"]
        if start >= end or end > duration:
            errors.append(f"contacts[{index}]: interval must satisfy 0 <= start < end <= duration_frames")
        actor = bindings.get(contact["actor_binding_id"])
        target = bindings.get(contact["target_binding_id"])
        if not actor or not target:
            errors.append(f"contacts[{index}]: actor and target bindings must resolve")
            continue
        actor_descriptor = actor.get("descriptor")
        if not isinstance(actor_descriptor, Mapping) or actor_descriptor.get("asset_kind") != "character":
            errors.append(f"contacts[{index}]: actor binding must be a character")
        actor_joints = set(_capabilities(actor).get("semantic_joints", []))
        if contact["semantic_effector"] not in actor_joints:
            errors.append(f"contacts[{index}]: semantic effector {contact['semantic_effector']!r} is not declared by actor")
        target_capabilities = _capabilities(target)
        target_descriptor = target.get("descriptor")
        if "target_surface_id" in contact:
            if not isinstance(target_descriptor, Mapping) or target_descriptor.get("asset_kind") != "environment":
                errors.append(f"contacts[{index}]: surface target must be an environment asset")
            surface_ids = {item.get("surface_id") for item in target_capabilities.get("surfaces", []) if isinstance(item, Mapping)}
            if contact["target_surface_id"] not in surface_ids:
                errors.append(f"contacts[{index}]: target surface {contact['target_surface_id']!r} is not declared")
        else:
            if not isinstance(target_descriptor, Mapping) or target_descriptor.get("asset_kind") != "character":
                errors.append(f"contacts[{index}]: semantic-joint target must be a character asset")
            if contact["target_semantic_joint"] not in set(target_capabilities.get("semantic_joints", [])):
                errors.append(f"contacts[{index}]: target semantic joint is not declared")

    for index, event in enumerate(payload["events"]):
        if event["frame"] >= duration:
            errors.append(f"events[{index}]: frame must be less than duration_frames")
        binding_id = event.get("binding_id")
        if binding_id is not None and binding_id not in bindings:
            errors.append(f"events[{index}]: unknown binding_id {binding_id!r}")
    return errors


def validate_model_scene(
    value: Mapping[str, Any] | str | Path,
    *,
    project_root: str | Path,
    for_render: bool = False,
    trusted_catalog_path: str | Path | None = None,
    trusted_approval_path: str | Path | None = None,
) -> dict[str, Any]:
    """Validate authored scene timing and resolve each exact model revision.

    Render-ready validation requires caller-supplied trusted catalogue and
    approval-record paths; descriptor-selected references alone are not trust.
    """

    payload = _load_document(value, "model_scene")
    errors = _validate_scene_payload(
        payload,
        Path(project_root),
        for_render=for_render,
        trusted_catalog_path=trusted_catalog_path,
        trusted_approval_path=trusted_approval_path,
    )
    if errors:
        raise ModelContractError(errors)
    return payload


def _validate_inspection_payload(
    payload: Mapping[str, Any],
    project_root: Path,
    *,
    trusted_catalog_path: str | Path | None = None,
    trusted_approval_path: str | Path | None = None,
) -> list[str]:
    errors = _finite_errors(payload) + _schema_errors(payload, "inspection")
    if errors:
        return errors
    for geometry_name in ("stored", "evaluated"):
        counts = payload["geometry"][geometry_name]
        if counts["faces"] > 0 and counts["triangles"] == 0:
            errors.append(f"geometry.{geometry_name}: non-empty faces require at least one triangle")
    _, descriptor_bytes, file_errors = _safe_file(
        project_root, payload.get("descriptor_path"), payload.get("descriptor_sha256"), "inspection descriptor"
    )
    errors.extend(file_errors)
    if not file_errors:
        descriptor, json_errors = _json_file(descriptor_bytes, "inspection descriptor")
        errors.extend(json_errors)
        if descriptor is not None:
            operator_approved = payload["verdicts"]["operator"] == "approved"
            errors.extend(
                _validate_asset_payload(
                    descriptor,
                    project_root,
                    for_render=operator_approved,
                    trusted_catalog_path=trusted_catalog_path,
                    trusted_approval_path=trusted_approval_path,
                )
            )
            if descriptor.get("asset_id") != payload.get("asset_id"):
                errors.append("inspection: asset_id does not match the descriptor")
            if (descriptor.get("revision") or {}).get("revision_id") != payload.get("revision_id"):
                errors.append("inspection: revision_id does not match the descriptor")
    for index, artifact in enumerate(payload["render_artifacts"]):
        _, _, file_errors = _safe_file(project_root, artifact.get("path"), artifact.get("sha256"), f"render_artifacts[{index}]")
        errors.extend(file_errors)
    return errors


def validate_model_inspection(
    value: Mapping[str, Any] | str | Path,
    *,
    project_root: str | Path,
    trusted_catalog_path: str | Path | None = None,
    trusted_approval_path: str | Path | None = None,
) -> dict[str, Any]:
    """Validate a hash-bound inspection with separate verdicts.

    An ``operator=approved`` claim requires caller-owned trusted record paths;
    this receipt cannot authorize its own asset.
    """

    payload = _load_document(value, "model_inspection")
    errors = _validate_inspection_payload(
        payload,
        Path(project_root),
        trusted_catalog_path=trusted_catalog_path,
        trusted_approval_path=trusted_approval_path,
    )
    if errors:
        raise ModelContractError(errors)
    return payload
