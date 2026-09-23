"""Review-only, content-addressed intake for model asset candidates.

Intake writes only below a caller-selected run directory.  It creates a local
content-addressed copy and immutable review records; it never promotes into the
authoritative asset catalogue or grants render approval.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping

from content.video_engine.src.modeling.contracts import validate_model_asset
from content.video_engine.src.services.asset_store import (
    AssetStore,
    AssetStoreError,
    LocalDirClient,
)

_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_CATALOG_KIND = {"character": "actor", "prop": "prop", "environment": "world"}
DEFAULT_MAX_FILE_BYTES = 2 * 1024**3
DEFAULT_MAX_TOTAL_BYTES = 8 * 1024**3
DEFAULT_MAX_DEPENDENCIES = 256
_MAX_MANIFEST_BYTES = 16 * 1024**2


class AssetIntakeError(ValueError):
    """Raised when a candidate cannot be staged without violating intake rules."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash_limited(path: Path, max_bytes: int) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            total += len(chunk)
            if total > max_bytes:
                raise AssetIntakeError(f"resource exceeds per-file byte quota: {path}")
            digest.update(chunk)
    return digest.hexdigest(), total


def _check_limits(max_file_bytes: int, max_total_bytes: int, max_dependencies: int) -> None:
    for name, value, allow_zero in (
        ("max_file_bytes", max_file_bytes, False),
        ("max_total_bytes", max_total_bytes, False),
        ("max_dependencies", max_dependencies, True),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value < (0 if allow_zero else 1):
            raise AssetIntakeError(f"{name} must be a finite nonnegative integer quota")


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _root_dir(value: str | Path, name: str) -> Path:
    path = Path(value).expanduser().resolve(strict=True)
    if not path.is_dir():
        raise AssetIntakeError(f"{name} must be an existing directory: {path}")
    return path


def _run_dir(project_root: Path, value: str | Path) -> Path:
    requested = Path(value).expanduser()
    candidate = requested if requested.is_absolute() else project_root / requested
    candidate = candidate.resolve(strict=False)
    if candidate == project_root or not _inside(candidate, project_root):
        raise AssetIntakeError("run_dir must be a strict child of project_root")
    candidate.mkdir(parents=True, exist_ok=True)
    resolved = candidate.resolve(strict=True)
    if resolved == project_root or not _inside(resolved, project_root) or not resolved.is_dir():
        raise AssetIntakeError("resolved run_dir must remain a strict child of project_root")
    return resolved


def _safe_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise AssetIntakeError(f"{label} must be a lowercase safe identifier")
    return value


def _safe_source(path: str | Path, allowed_root: Path) -> tuple[Path, str]:
    raw = Path(path).expanduser()
    candidate = raw if raw.is_absolute() else allowed_root / raw
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise AssetIntakeError(f"source does not resolve to a local file: {path}: {exc}") from exc
    if not _inside(resolved, allowed_root):
        raise AssetIntakeError("source path or symlink target escapes allowed_source_root")
    if not resolved.is_file():
        raise AssetIntakeError(f"source must be a regular file: {path}")
    return resolved, str(candidate.absolute())


def _ensure_output_dir(run_dir: Path, relative: str | Path) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
        raise AssetIntakeError(f"unsafe output path: {relative}")
    current = run_dir
    for part in rel.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if current.is_symlink() or not current.is_dir():
                raise AssetIntakeError(f"output directory is not a real directory: {current}")
        else:
            current.mkdir()
        resolved = current.resolve(strict=True)
        if not _inside(resolved, run_dir):
            raise AssetIntakeError("output path resolves outside run_dir")
        current = resolved
    return current


def _output_path(run_dir: Path, relative: str | Path) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
        raise AssetIntakeError(f"unsafe output path: {relative}")
    parent = _ensure_output_dir(run_dir, rel.parent)
    target = parent / rel.name
    if target.is_symlink():
        raise AssetIntakeError(f"refusing symlink output file: {target}")
    if not _inside(target.resolve(strict=False), run_dir):
        raise AssetIntakeError("output file resolves outside run_dir")
    return target


def _copy_immutable(source: Path, destination: Path, digest: str, max_bytes: int) -> None:
    if destination.exists() or destination.is_symlink():
        if destination.is_symlink() or not destination.is_file():
            raise AssetIntakeError(f"existing staged resource is not a regular file: {destination}")
        if _hash_limited(destination, max_bytes)[0] != digest:
            raise AssetIntakeError(f"refusing to overwrite different staged bytes at {destination}")
        return

    created = False
    try:
        with source.open("rb") as incoming, destination.open("xb") as outgoing:
            created = True
            copied = hashlib.sha256()
            copied_bytes = 0
            for chunk in iter(lambda: incoming.read(1 << 20), b""):
                copied_bytes += len(chunk)
                if copied_bytes > max_bytes:
                    raise AssetIntakeError("source grew beyond per-file byte quota while staging")
                copied.update(chunk)
                outgoing.write(chunk)
            outgoing.flush()
            os.fsync(outgoing.fileno())
        if copied.hexdigest() != digest:
            raise AssetIntakeError("source bytes changed while they were being staged")
    except FileExistsError:
        if destination.is_symlink() or not destination.is_file() or _hash_limited(destination, max_bytes)[0] != digest:
            raise AssetIntakeError(f"refusing to overwrite different staged bytes at {destination}") from None
    except Exception:
        if created:
            destination.unlink(missing_ok=True)
        raise


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise AssetIntakeError(f"candidate metadata must be JSON serializable: {exc}") from exc


def _write_immutable_json(run_dir: Path, relative: str, payload: Mapping[str, Any]) -> Path:
    destination = _output_path(run_dir, relative)
    data = _json_bytes(payload)
    if destination.exists():
        if not destination.is_file() or destination.read_bytes() != data:
            raise AssetIntakeError(f"refusing to overwrite different candidate metadata at {destination}")
        return destination
    try:
        with destination.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        if not destination.is_file() or destination.read_bytes() != data:
            raise AssetIntakeError(f"refusing to overwrite different candidate metadata at {destination}") from None
    return destination


def _relative_to_project(path: Path, project_root: Path) -> str:
    if not _inside(path.resolve(strict=True), project_root):
        raise AssetIntakeError("staged resource is outside project_root")
    return path.resolve(strict=True).relative_to(project_root).as_posix()


def _verify_local_store(store: AssetStore, run_dir: Path, digest: str, max_bytes: int) -> None:
    verify_dir = _ensure_output_dir(run_dir, ".verification")
    fd, name = tempfile.mkstemp(prefix=f"{digest}-", suffix=".verify", dir=verify_dir)
    os.close(fd)
    temporary = Path(name)
    try:
        store.fetch(digest, temporary)
        if _hash_limited(temporary, max_bytes)[0] != digest:
            raise AssetIntakeError("content-addressed store verification returned stale bytes")
    except AssetStoreError as exc:
        raise AssetIntakeError(f"content-addressed store verification failed: {exc}") from exc
    finally:
        temporary.unlink(missing_ok=True)


def intake_asset_candidate(
    source_path: str | Path,
    *,
    project_root: str | Path,
    run_dir: str | Path,
    allowed_source_root: str | Path,
    asset_id: str,
    revision_id: str,
    asset_kind: str,
    coordinate_system: Mapping[str, Any],
    capabilities: Mapping[str, Any],
    revision_number: int = 1,
    parent_revision_id: str | None = None,
    resource_id: str = "primary-source",
    resource_kind: str = "editable_source",
    expected_sha256: str | None = None,
    additional_resources: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]] = (),
    layer_provenance: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]] = (),
    dependency_claim: Mapping[str, Any] | None = None,
    provenance: Mapping[str, Any] | None = None,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_dependencies: int = DEFAULT_MAX_DEPENDENCIES,
) -> dict[str, Any]:
    """Stage a source bundle and emit a T2-validated review-only candidate.

    ``source_path`` may be absolute or relative to ``allowed_source_root``.
    Each item in ``additional_resources`` has ``source_path``, ``resource_id``
    and ``resource_kind`` keys, with an optional ``expected_sha256``. The source
    and its dependencies are copied beneath ``run_dir`` while preserving paths
    relative to the allowed root, then separately verified in an ``AssetStore``
    backed only by a local directory inside that run. The returned descriptor
    references candidate records in the same run. Neither record constitutes
    approval, and this API never updates the authoritative asset catalogue.

    Model bytes (including ``.blend``) are treated as opaque data; no DCC or
    embedded code is executed.
    """

    _check_limits(max_file_bytes, max_total_bytes, max_dependencies)
    project = _root_dir(project_root, "project_root")
    allowed = _root_dir(allowed_source_root, "allowed_source_root")
    asset_id = _safe_id(asset_id, "asset_id")
    revision_id = _safe_id(revision_id, "revision_id")
    resource_id = _safe_id(resource_id, "resource_id")
    if asset_kind not in _CATALOG_KIND:
        raise AssetIntakeError("asset_kind must be character, prop, or environment")
    if not isinstance(revision_number, int) or isinstance(revision_number, bool) or revision_number < 1:
        raise AssetIntakeError("revision_number must be a positive integer")
    if resource_kind not in {"editable_source", "mesh", "texture", "layer_manifest", "motion_clip", "other"}:
        raise AssetIntakeError("resource_kind is not supported by model_asset.v1")

    revision_dir = f"model-assets/candidates/{asset_id}/{revision_id}"
    record_relative = f"{revision_dir}/intake-record.json"

    resource_specs = [
        {
            "source_path": source_path,
            "resource_id": resource_id,
            "resource_kind": resource_kind,
            "expected_sha256": expected_sha256,
        },
        *[dict(spec) for spec in additional_resources],
    ]
    if len(resource_specs) - 1 > max_dependencies:
        raise AssetIntakeError("dependency count exceeds max_dependencies quota")
    resources: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    total_bytes = 0
    for index, spec in enumerate(resource_specs):
        current_id = _safe_id(str(spec.get("resource_id", "")), "resource_id")
        current_kind = str(spec.get("resource_kind", ""))
        if current_kind not in {"editable_source", "mesh", "texture", "layer_manifest", "motion_clip", "other"}:
            raise AssetIntakeError(f"resource {current_id!r} has an unsupported resource_kind")
        if current_id in seen_ids:
            raise AssetIntakeError(f"resource_id is repeated: {current_id}")
        source, original_path = _safe_source(str(spec.get("source_path", "")), allowed)
        source_relative = source.relative_to(allowed).as_posix()
        if source_relative in seen_paths:
            raise AssetIntakeError(f"source resource path is repeated: {source_relative}")
        seen_ids.add(current_id)
        seen_paths.add(source_relative)
        digest, size_bytes = _hash_limited(source, max_file_bytes)
        total_bytes += size_bytes
        if total_bytes > max_total_bytes:
            raise AssetIntakeError("resource bundle exceeds aggregate byte quota")
        declared = spec.get("expected_sha256")
        if declared is not None and (not isinstance(declared, str) or not _SHA256.fullmatch(declared) or declared != digest):
            label = "expected_sha256" if index == 0 else f"resource {current_id} expected_sha256"
            raise AssetIntakeError(f"source hash does not match {label}")
        resources.append(
            {
                "resource_id": current_id,
                "resource_kind": current_kind,
                "source": source,
                "source_path": original_path,
                "source_relative": source_relative,
                "sha256": digest,
                "size_bytes": size_bytes,
                "stage_relative": f"{revision_dir}/resources/{source_relative}",
            }
        )
    primary = resources[0]
    digest = primary["sha256"]
    original_source_path = primary["source_path"]
    source = primary["source"]

    if source.suffix.lower() == ".blend":
        manifest_id = "blend-dependency-manifest"
        manifest = next((item for item in resources[1:] if item["resource_id"] == manifest_id), None)
        if (
            not isinstance(dependency_claim, Mapping)
            or dependency_claim.get("manifest_resource_id") != manifest_id
            or dependency_claim.get("inspection_state") != "unverified_blender_inspection"
            or not isinstance(dependency_claim.get("packed_claim"), bool)
            or manifest is None or manifest["resource_kind"] != "other"
            or manifest["source"] != source.with_name(source.name + ".dependencies.json")
        ):
            raise AssetIntakeError(".blend intake requires a declared dependency manifest pending Blender inspection")
        try:
            with manifest["source"].open("rb") as handle:
                data = handle.read(_MAX_MANIFEST_BYTES + 1)
            if len(data) > _MAX_MANIFEST_BYTES:
                raise AssetIntakeError("Blender dependency manifest exceeds document byte quota")
            declaration = json.loads(data.decode("utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            raise AssetIntakeError(f"Blender dependency manifest is unreadable: {exc}") from exc
        if not isinstance(declaration, dict):
            raise AssetIntakeError("Blender dependency manifest must be a JSON object")
        entries = declaration.get("dependencies")
        if (
            declaration.get("schema_version") != "blend_dependencies.v1"
            or not isinstance(entries, list)
            or not isinstance(declaration.get("packed"), bool)
            or (declaration["packed"] and bool(entries))
            or (not declaration["packed"] and not entries)
            or declaration.get("packed") != dependency_claim["packed_claim"]
            or dependency_claim.get("declared_dependency_count") != len(entries)
            or len(resources) != len(entries) + 2
        ):
            raise AssetIntakeError("Blender dependency manifest and staged resource set disagree")
        for index, entry in enumerate(entries):
            linked = next((item for item in resources[1:] if item["resource_id"] == f"blend-dependency-{index + 1}"), None)
            if not isinstance(entry, dict) or linked is None or entry.get("sha256") != linked["sha256"]:
                raise AssetIntakeError("Blender dependency manifest hash does not match staged resource")
    elif dependency_claim is not None:
        raise AssetIntakeError("dependency_claim is reserved for .blend intake")

    run = _run_dir(project, run_dir)

    parent_lineage: dict[str, str] | None = None
    if parent_revision_id is not None:
        parent_revision_id = _safe_id(parent_revision_id, "parent_revision_id")
        if parent_revision_id == revision_id:
            raise AssetIntakeError("parent_revision_id must differ from revision_id")
        parent_relative = f"model-assets/candidates/{asset_id}/{parent_revision_id}/model_asset.v1.json"
        parent_path = run / parent_relative
        if parent_path.is_symlink() or not parent_path.is_file() or not _inside(parent_path.resolve(), run):
            raise AssetIntakeError("parent revision must be an existing local candidate")
        parent = validate_model_asset(parent_path, project_root=project)
        if parent["asset_id"] != asset_id or parent["revision"]["revision_id"] != parent_revision_id:
            raise AssetIntakeError("parent revision identity does not match")
        parent_resource = parent["resources"][0]
        parent_lineage = {
            "source_id": f"parent-{parent_revision_id}",
            "relation": "derived_from",
            "path": parent_resource["path"],
            "sha256": parent_resource["sha256"],
        }

    record_path = run / record_relative
    if record_path.is_symlink() or not _inside(record_path.resolve(strict=False), run):
        raise AssetIntakeError("refusing symlink or escaped intake record")

    if record_path.exists():
        try:
            existing_record = json.loads(record_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise AssetIntakeError(f"existing revision intake record is unreadable: {exc}") from exc
        existing_resources = [
            {
                "resource_id": item.get("resource_id"),
                "resource_kind": item.get("resource_kind"),
                "source_path": item.get("source_path"),
                "source_sha256": item.get("source_sha256"),
                "size_bytes": item.get("size_bytes"),
            }
            for item in existing_record.get("resources", [])
            if isinstance(item, dict)
        ]
        proposed_resources = [
            {
                "resource_id": item["resource_id"],
                "resource_kind": item["resource_kind"],
                "source_path": item["source_path"],
                "source_sha256": item["sha256"],
                "size_bytes": item["size_bytes"],
            }
            for item in resources
        ]
        if existing_record.get("source_sha256") != digest or existing_resources != proposed_resources:
            raise AssetIntakeError("asset revision already exists with different source bytes")
        if existing_record.get("source_path") != original_source_path:
            raise AssetIntakeError("asset revision already exists from a different source path")
        if existing_record.get("parent_revision_id") != parent_revision_id:
            raise AssetIntakeError("asset revision already exists with different parent lineage")
        if existing_record.get("layers") != [dict(layer) for layer in layer_provenance]:
            raise AssetIntakeError("asset revision already exists with different layer provenance")
        if existing_record.get("dependency_claim") != (dict(dependency_claim) if dependency_claim else None):
            raise AssetIntakeError("asset revision already exists with different dependency declaration")

    for item in resources:
        staged = _output_path(run, item["stage_relative"])
        _copy_immutable(item["source"], staged, item["sha256"], max_file_bytes)
        item["staged_path"] = staged
        item["path"] = _relative_to_project(staged, project)

    store_root = _ensure_output_dir(run, "content-addressed-store")
    store = AssetStore(LocalDirClient(store_root), "run-local-review-only")
    _ensure_output_dir(run, Path("content-addressed-store") / "sha256")
    for item in resources:
        store_object = store_root / "sha256" / item["sha256"]
        if store_object.is_symlink():
            raise AssetIntakeError("refusing symlink in the local content-addressed store")
        if store_object.exists() and store_object.stat().st_size > max_file_bytes:
            raise AssetIntakeError("content-addressed store object exceeds per-file byte quota")
        try:
            store.ensure(item["sha256"], item["staged_path"])
            _verify_local_store(store, run, item["sha256"], max_file_bytes)
        except AssetStoreError as exc:
            raise AssetIntakeError(f"could not stage content-addressed resource: {exc}") from exc

    catalog_relative = f"{revision_dir}/candidate-catalog.json"
    record_id = f"intake-{asset_id}-{revision_id}"
    catalog = {
        "schema_version": "asset_catalog.v1",
        "project_root": ".",
        "resolution_order": ["exact_semantic_match"],
        "assets": [
            {
                "asset_id": asset_id,
                "revision_id": revision_id,
                "path": primary["path"],
                "sha256": digest,
                "kind": _CATALOG_KIND[asset_kind],
                "style_version": "model-asset-intake-v1",
                "semantic_tags": [asset_kind, "candidate"],
                "resolution_tier": 1,
                "rights_state": "review_only",
                "review_state": "review_only",
                "render_eligible": False,
            }
        ],
    }
    catalog_path = _write_immutable_json(run, catalog_relative, catalog)
    catalog_hash = _sha256_file(catalog_path)

    record = {
        "schema_version": "model_asset_intake_record.v1",
        "record_id": record_id,
        "asset_id": asset_id,
        "revision_id": revision_id,
        "parent_revision_id": parent_revision_id,
        "resource_id": primary["resource_id"],
        "path": primary["path"],
        "sha256": digest,
        "source_path": original_source_path,
        "source_sha256": digest,
        "source_format": source.suffix.lower().lstrip("."),
        "resources": [
            {
                "resource_id": item["resource_id"],
                "resource_kind": item["resource_kind"],
                "path": item["path"],
                "source_path": item["source_path"],
                "source_sha256": item["sha256"],
                "size_bytes": item["size_bytes"],
            }
            for item in resources
        ],
        "layers": [dict(layer) for layer in layer_provenance],
        "dependency_claim": dict(dependency_claim) if dependency_claim else None,
        "total_source_bytes": total_bytes,
        "review_state": "review_only",
        "render_eligible": False,
        "status": "candidate",
    }
    record_path = _write_immutable_json(run, record_relative, record)
    record_hash = _sha256_file(record_path)

    source_provenance = dict(provenance or {})
    licenses = dict(source_provenance.get("licenses") or {})
    for license_kind in ("tool", "mesh", "texture", "motion"):
        licenses.setdefault(license_kind, "unknown_pending_review")
    normalized_provenance = {
        "authoring_method": source_provenance.get("authoring_method", "imported"),
        "tool_name": source_provenance.get("tool_name", "model-asset-intake"),
        "tool_version": source_provenance.get("tool_version", "1"),
        "licenses": licenses,
    }
    descriptor = {
        "schema_version": "model_asset.v1",
        "asset_id": asset_id,
        "revision": {
            "revision_id": revision_id,
            "revision_number": revision_number,
            **({"parent_revision_id": parent_revision_id} if parent_revision_id else {}),
        },
        "asset_kind": asset_kind,
        "resources": [
            {
                "resource_id": item["resource_id"],
                "resource_kind": item["resource_kind"],
                "path": item["path"],
                "sha256": item["sha256"],
            }
            for item in resources
        ],
        "catalog_reference": {
            "asset_id": asset_id,
            "path": _relative_to_project(catalog_path, project),
            "sha256": catalog_hash,
            "resource_id": primary["resource_id"],
        },
        "approval_reference": {
            "record_id": record_id,
            "path": _relative_to_project(record_path, project),
            "sha256": record_hash,
            "resource_id": primary["resource_id"],
        },
        "coordinate_system": dict(coordinate_system),
        "capabilities": dict(capabilities),
        "source_lineage": ([parent_lineage] if parent_lineage else []) + [
            {
                "source_id": "source-original" if index == 0 else item["resource_id"],
                "relation": "created_from",
                "path": item["path"],
                "sha256": item["sha256"],
            }
            for index, item in enumerate(resources)
        ],
        "provenance": normalized_provenance,
    }
    descriptor_relative = f"{revision_dir}/model_asset.v1.json"
    descriptor_path = _write_immutable_json(run, descriptor_relative, descriptor)
    validated = validate_model_asset(descriptor_path, project_root=project)
    if validated.get("asset_id") != asset_id:
        raise AssetIntakeError("T2 validator returned a different asset identity")
    return {
        "asset_id": asset_id,
        "revision_id": revision_id,
        "descriptor": validated,
        "descriptor_path": str(descriptor_path),
        "catalog_path": str(catalog_path),
        "intake_record_path": str(record_path),
        "staged_source_path": str(primary["staged_path"]),
        "source_path": original_source_path,
        "source_sha256": digest,
        "total_source_bytes": total_bytes,
        "store_path": str(store_root / "sha256" / digest),
        "store_paths": [str(store_root / "sha256" / item["sha256"]) for item in resources],
        "staged_resources": [
            {
                "resource_id": item["resource_id"],
                "resource_kind": item["resource_kind"],
                "path": str(item["staged_path"]),
                "sha256": item["sha256"],
                "source_path": item["source_path"],
            }
            for item in resources
        ],
        "store_result": "verified",
        "dependency_claim": dict(dependency_claim) if dependency_claim else None,
        "review_state": "review_only",
        "render_eligible": False,
    }


__all__ = ["AssetIntakeError", "intake_asset_candidate"]
