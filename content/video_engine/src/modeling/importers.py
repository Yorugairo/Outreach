"""Inspect local model bundles before review-only asset intake.

No DCC is launched here. In particular, a Blender file is copied as opaque
bytes and a glTF file is parsed only to identify its local resource files.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import struct
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

from content.video_engine.src.modeling.assets import (
    AssetIntakeError,
    DEFAULT_MAX_DEPENDENCIES,
    DEFAULT_MAX_FILE_BYTES,
    DEFAULT_MAX_TOTAL_BYTES,
    _check_limits,
    _inside,
    _safe_source,
    intake_asset_candidate,
)

_MODEL_SUFFIXES = {".blend", ".gltf", ".glb", ".png", ".psd", ".kra"}
_LAYER_ROLES = {"background", "board", "mid", "subject", "occluder"}
_LAYER_DEFAULT_DEPTH = {"background": 1.0, "board": 1.05, "mid": 1.15, "subject": 1.275, "occluder": 1.4}
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_MAX_DOCUMENT_BYTES = 16 * 1024**2
_RAW_DECLARATION_MULTIPLIER = 4
_MIN_RAW_DECLARATIONS = 16


def _check_raw_declarations(count: int, max_dependencies: int) -> None:
    """Bound repeated reuse to four declarations per allowed dependency, floor 16."""
    limit = max(_MIN_RAW_DECLARATIONS, _RAW_DECLARATION_MULTIPLIER * max_dependencies)
    if count > limit:
        raise AssetIntakeError("raw dependency declarations exceed quota before resource lookup")


def _local_uri(uri: str, label: str) -> str | None:
    """Return a local relative path, None for embedded data, or refuse it."""
    if not isinstance(uri, str) or not uri:
        raise AssetIntakeError(f"{label} must be a nonempty URI")
    if uri.startswith("data:"):
        return None
    parsed = urlsplit(uri)
    decoded = unquote(uri)
    path = PurePosixPath(decoded)
    if (
        parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
        or decoded.startswith("/") or "\\" in decoded or ":" in decoded
        or any(value in uri.lower() for value in ("%2e", "%2f", "%5c"))
        or not path.parts
    ):
        raise AssetIntakeError(f"{label} must be a local relative resource URI")
    return path.as_posix()


def _read_limited(path: Path, max_bytes: int, label: str) -> bytes:
    with path.open("rb") as handle:
        data = handle.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise AssetIntakeError(f"{label} exceeds document byte quota")
    return data


def _json_object(data: bytes, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise AssetIntakeError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise AssetIntakeError(f"{label} must be a JSON object")
    return payload


def _gltf_document(source: Path, max_file_bytes: int) -> dict[str, Any]:
    if source.stat().st_size > max_file_bytes:
        raise AssetIntakeError("glTF source exceeds per-file byte quota")
    if source.suffix.lower() == ".gltf":
        return _json_object(_read_limited(source, min(max_file_bytes, _MAX_DOCUMENT_BYTES), "glTF"), "glTF")
    with source.open("rb") as handle:
        header = handle.read(20)
        if len(header) < 20 or header[:4] != b"glTF":
            raise AssetIntakeError("GLB has no valid glTF header")
        magic, version, length = struct.unpack_from("<4sII", header)
        chunk_length, chunk_type = struct.unpack_from("<I4s", header, 12)
        if magic != b"glTF" or version != 2 or length != source.stat().st_size:
            raise AssetIntakeError("GLB header version or byte length is invalid")
        if chunk_type != b"JSON" or chunk_length % 4 or 20 + chunk_length > length or chunk_length > _MAX_DOCUMENT_BYTES:
            raise AssetIntakeError("GLB JSON chunk is invalid or exceeds document byte quota")
        data = handle.read(chunk_length)
    if len(data) != chunk_length:
        raise AssetIntakeError("GLB has no valid glTF header")
    return _json_object(data.rstrip(b" \t\r\n\x00"), "GLB JSON chunk")


def _declared_uris(node: Any):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "uri":
                yield value
            else:
                yield from _declared_uris(value)
    elif isinstance(node, list):
        for value in node:
            yield from _declared_uris(value)


def _resource_spec(path: Path, allowed: Path, resource_id: str, kind: str) -> dict[str, str]:
    source, _ = _safe_source(path, allowed)
    return {"source_path": str(source), "resource_id": resource_id, "resource_kind": kind}


def _local_dependency(base: Path, relative: str, allowed: Path) -> Path:
    current = base
    for part in PurePosixPath(relative).parts:
        current = current.parent if part == ".." else current / part
        if not _inside(current, allowed):
            raise AssetIntakeError("resource URI escapes allowed_source_root")
        if current.is_symlink():
            raise AssetIntakeError("resource URI traverses a symlink")
    source, _ = _safe_source(current, allowed)
    return source


def _lexical_key(base: Path, relative: str) -> str:
    """Deduplicate declared paths without resolving or opening their targets."""
    return os.path.normcase(os.path.normpath(str(base / relative)))


def _layer_bundle(source: Path, allowed: Path, max_file_bytes: int, max_dependencies: int) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    sidecar = source.with_suffix(".layers.json")
    if not sidecar.exists() and not sidecar.is_symlink():
        return [], []
    sidecar, _ = _safe_source(sidecar, allowed)
    payload = _json_object(_read_limited(sidecar, min(max_file_bytes, _MAX_DOCUMENT_BYTES), "layer sidecar"), "layer sidecar")
    foreground = payload.get("foreground", {})
    layers = payload.get("layers", [])
    if not isinstance(foreground, dict) or not isinstance(layers, list):
        raise AssetIntakeError("layer sidecar foreground and layers must be collections")
    raw_count = len(foreground)
    for entry in layers:
        raw_count += 1
        if isinstance(entry, dict) and isinstance(entry.get("life"), dict):
            raw_count += len(entry["life"])
    _check_raw_declarations(raw_count, max_dependencies)
    if max_dependencies < 1:
        raise AssetIntakeError("dependency count exceeds max_dependencies quota")
    resources = [_resource_spec(sidecar, allowed, "layer-sidecar", "layer_manifest")]
    provenance: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    seen_keys: set[str] = set()

    def add(uri: str, label: str, details: dict[str, Any]) -> None:
        relative = _local_uri(uri, label)
        if relative is None:
            raise AssetIntakeError(f"{label} must reference a local layer file")
        lexical = _lexical_key(source.parent, relative)
        if lexical not in seen_keys:
            if len(seen_keys) + 1 >= max_dependencies:
                raise AssetIntakeError("dependency count exceeds max_dependencies quota")
            seen_keys.add(lexical)
        dep = _local_dependency(source.parent, relative, allowed)
        key = str(dep)
        if key not in seen_paths:
            seen_paths.add(key)
            resource_id = f"layer-{len(seen_paths)}"
            resources.append(_resource_spec(dep, allowed, resource_id, "texture" if dep.suffix.lower() == ".png" else "other"))
        else:
            resource_id = next(spec["resource_id"] for spec in resources if spec["source_path"] == key)
        provenance.append({"resource_id": resource_id, "source_uri": relative, **details})

    for name, uri in foreground.items():
        if not isinstance(name, str) or not name.strip():
            raise AssetIntakeError("foreground layer name must be nonempty")
        add(uri, f"foreground {name}", {"role": "foreground", "name": name})

    if layers:
        roles: set[str] = set()
        last_depth = 0.0
        for index, entry in enumerate(layers):
            if not isinstance(entry, dict) or entry.get("role") not in _LAYER_ROLES:
                raise AssetIntakeError(f"layers[{index}] has an unsupported role")
            role = entry["role"]
            depth = entry.get("depth", _LAYER_DEFAULT_DEPTH[role])
            if role in roles or not isinstance(depth, (int, float)) or isinstance(depth, bool) or not math.isfinite(depth) or not last_depth < depth <= 4:
                raise AssetIntakeError("layer roles must be unique and depth must ascend back to front")
            alpha = entry.get("alpha", role != "background")
            if not isinstance(alpha, bool) or not isinstance(entry.get("generator"), str) or not entry["generator"]:
                raise AssetIntakeError(f"layers[{index}] needs valid alpha and generator provenance")
            roles.add(role)
            last_depth = float(depth)
            add(entry.get("path"), f"layers[{index}]", {"role": role, "depth": depth, "alpha": alpha, "generator": entry["generator"]})
            life = entry.get("life", {})
            if life:
                if not isinstance(life, dict) or any(key not in life for key in ("still", "mask", "job")):
                    raise AssetIntakeError(f"layers[{index}] life record is incomplete")
                for key in ("still", "mask", "job"):
                    add(life[key], f"layers[{index}].life.{key}", {"role": f"life-{key}", "plane": role})
        if "background" not in roles:
            raise AssetIntakeError("layer sidecar needs a background plane")
    return resources, provenance


def _blend_bundle(source: Path, allowed: Path, max_file_bytes: int, max_dependencies: int) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Require an explicit dependency declaration; Blender must later verify it."""
    manifest = source.with_name(source.name + ".dependencies.json")
    if manifest.is_symlink() or not manifest.is_file():
        raise AssetIntakeError(".blend requires a local .blend.dependencies.json manifest")
    manifest, _ = _safe_source(manifest, allowed)
    data = _read_limited(manifest, min(max_file_bytes, _MAX_DOCUMENT_BYTES), "Blender dependency manifest")
    payload = _json_object(data, "Blender dependency manifest")
    packed = payload.get("packed")
    entries = payload.get("dependencies")
    if payload.get("schema_version") != "blend_dependencies.v1" or not isinstance(packed, bool) or not isinstance(entries, list):
        raise AssetIntakeError("Blender dependency manifest needs schema_version, packed and dependencies")
    if (packed and entries) or (not packed and not entries):
        raise AssetIntakeError("Blender manifest must declare packed or list external dependencies")
    if len(entries) + 1 > max_dependencies:
        raise AssetIntakeError("dependency count exceeds max_dependencies quota")
    resources = [{
        **_resource_spec(manifest, allowed, "blend-dependency-manifest", "other"),
        "expected_sha256": hashlib.sha256(data).hexdigest(),
    }]
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"uri", "sha256"} or not isinstance(entry.get("sha256"), str) or not _SHA256.fullmatch(entry["sha256"]):
            raise AssetIntakeError(f"Blender dependency {index} needs URI and sha256")
        relative = _local_uri(entry["uri"], f"Blender dependency {index}")
        if relative is None:
            raise AssetIntakeError("Blender dependency must be a local file")
        dep = _local_dependency(source.parent, relative, allowed)
        resources.append({
            **_resource_spec(dep, allowed, f"blend-dependency-{index + 1}", "texture" if dep.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} else "other"),
            "expected_sha256": entry["sha256"],
        })
    claim = {
        "manifest_resource_id": "blend-dependency-manifest",
        "packed_claim": packed,
        "declared_dependency_count": len(entries),
        "inspection_state": "unverified_blender_inspection",
    }
    return resources, claim


def intake_model_bundle(
    source_path: str | Path,
    *,
    allowed_source_root: str | Path,
    **candidate_options: Any,
) -> dict[str, Any]:
    """Intake a model, prop, environment or layered plate as a candidate."""
    allowed = Path(allowed_source_root).expanduser().resolve(strict=True)
    if not allowed.is_dir():
        raise AssetIntakeError("allowed_source_root must be a directory")
    max_file_bytes = candidate_options.get("max_file_bytes", DEFAULT_MAX_FILE_BYTES)
    max_total_bytes = candidate_options.get("max_total_bytes", DEFAULT_MAX_TOTAL_BYTES)
    max_dependencies = candidate_options.get("max_dependencies", DEFAULT_MAX_DEPENDENCIES)
    _check_limits(max_file_bytes, max_total_bytes, max_dependencies)
    source, _ = _safe_source(source_path, allowed)
    if source.suffix.lower() not in _MODEL_SUFFIXES:
        raise AssetIntakeError(f"unsupported model bundle suffix: {source.suffix}")
    resources: list[dict[str, str]] = []
    layers: list[dict[str, Any]] = []
    dependency_claim: dict[str, Any] | None = None
    if source.suffix.lower() in {".gltf", ".glb"}:
        document = _gltf_document(source, max_file_bytes)
        raw_count = 0
        for _ in _declared_uris(document):
            raw_count += 1
            _check_raw_declarations(raw_count, max_dependencies)
        seen: set[str] = set()
        seen_keys: set[str] = set()
        for uri in _declared_uris(document):
            relative = _local_uri(uri, "glTF resource")
            if relative is None:
                continue
            lexical = _lexical_key(source.parent, relative)
            if lexical not in seen_keys:
                if len(seen_keys) >= max_dependencies:
                    raise AssetIntakeError("dependency count exceeds max_dependencies quota")
                seen_keys.add(lexical)
            dep = _local_dependency(source.parent, relative, allowed)
            if str(dep) in seen:
                continue
            seen.add(str(dep))
            kind = "texture" if dep.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} else "mesh"
            resources.append(_resource_spec(dep, allowed, f"gltf-resource-{len(seen)}", kind))
    if source.suffix.lower() in {".png", ".psd", ".kra"}:
        resources, layers = _layer_bundle(source, allowed, max_file_bytes, max_dependencies)
    if source.suffix.lower() == ".blend":
        resources, dependency_claim = _blend_bundle(source, allowed, max_file_bytes, max_dependencies)
    caller_resources = candidate_options.pop("additional_resources", ())
    if not isinstance(caller_resources, (list, tuple)):
        raise AssetIntakeError("additional_resources must be a list")
    if "dependency_claim" in candidate_options or "layer_provenance" in candidate_options:
        raise AssetIntakeError("bundle provenance is derived from the source files")
    return intake_asset_candidate(
        source,
        allowed_source_root=allowed,
        additional_resources=[*resources, *caller_resources],
        layer_provenance=layers,
        dependency_claim=dependency_claim,
        **candidate_options,
    )


__all__ = ["intake_model_bundle"]
