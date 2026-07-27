"""Validated remediation blueprints and deterministic offline prototypes.

The agentic runtime is deliberately kept at the boundary of this module.  A
model may produce a :class:`RemediationBlueprintSnapshot`, but it never gets
to provide markup, CSS, JavaScript, links, or a filesystem path.  The renderer
turns the reviewed, structured snapshot into a small, portable bundle whose
bytes are deterministic and whose manifest can be checked without the
application, a provider, or the network.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from src.models import (
    REMEDIATION_BLUEPRINT_VERSION,
    RemediationBlueprintSnapshot,
    canonical_sha256,
)


OFFLINE_PROTOTYPE_VERSION = "offline-prototype.v1"
PROTOTYPE_MANIFEST_VERSION = "prototype-manifest.v1"
PLACEHOLDER_TEXT = "[Confirm with operator]"


class BlueprintValidationError(ValueError):
    """Raised when a blueprint cannot safely become customer-facing output."""


class PrototypeSafetyError(ValueError):
    """Raised when a prototype request attempts to leave the offline boundary."""


@dataclass(frozen=True, slots=True)
class PrototypeBundle:
    """Immutable metadata for a rendered prototype bundle.

    The actual files remain ordinary portable artifacts.  This value object is
    intentionally not a persistence model: a bundle is a derived rendering of
    an immutable blueprint and can always be reproduced from that snapshot.
    """

    id: str
    snapshot_id: str
    run_id: str
    root: Path
    manifest_sha256: str
    files: tuple[dict[str, Any], ...]
    renderer_version: str = OFFLINE_PROTOTYPE_VERSION
    status: str = "complete"

    @property
    def bundle_dir(self) -> Path:
        return self.root

    @property
    def manifest_artifact_ref(self) -> str:
        return f"prototypes/{self.id}/manifest.json"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "snapshot_id": self.snapshot_id,
            "run_id": self.run_id,
            "root": self.root.as_posix(),
            "manifest_sha256": self.manifest_sha256,
            "manifest_artifact_ref": self.manifest_artifact_ref,
            "files": [dict(item) for item in self.files],
            "renderer_version": self.renderer_version,
            "status": self.status,
        }


_CANONICAL_SECTIONS = (
    "sitemap",
    "pages",
    "navigation",
    "answer_blocks",
    "cta_flows",
    "schema_recommendations",
    "embeds",
    "crm",
    "limitations",
)
_SECTION_ALIASES = {
    "sitemap_changes": "sitemap",
    "sitemap_plan": "sitemap",
    "page_plan": "pages",
    "cta_flow": "cta_flows",
    "cta": "cta_flows",
    "schema": "schema_recommendations",
    "structured_data": "schema_recommendations",
    "vertical_embed": "embeds",
    "vertical_functionality": "embeds",
    "crm_placement": "crm",
}
_ALLOWED_TOP_LEVEL = {
    "schema_version",
    "target",
    "title",
    "summary",
    "executive_summary",
    "service_fit",
    "sitemap",
    "sitemap_changes",
    "sitemap_plan",
    "pages",
    "page_plan",
    "navigation",
    "answer_blocks",
    "cta_flows",
    "cta_flow",
    "cta",
    "schema_recommendations",
    "schema",
    "structured_data",
    "embeds",
    "vertical_embed",
    "vertical_functionality",
    "crm",
    "crm_placement",
    "limitations",
    "placeholder_fields",
    "evidence_refs",
}

_UNKNOWN_VALUES = {
    "",
    "unknown",
    "not observed",
    "not_observed",
    "unavailable",
    "tbd",
    "n/a",
    "na",
    "null",
    "none",
}
_POSITIVE_STATUSES = {
    "observed",
    "supported",
    "confirmed",
    "recommended",
    "action",
    "complete",
}
_DANGEROUS_TEXT = (
    re.compile(r"<\s*(?:script|iframe|object|embed|svg|style|link|meta)\b", re.I),
    re.compile(r"(?:javascript|vbscript|data):", re.I),
    re.compile(r"\bon[a-z]+\s*=", re.I),
)


def _is_unknown(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().casefold() in _UNKNOWN_VALUES or value.strip().casefold().startswith("unknown:")
    return False


def _contains_dangerous_text(value: Any, *, path: str = "") -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            # Field names that would be executable or represent a raw model
            # artifact are disallowed even if their value is currently empty.
            normalized = key_text.casefold().replace("-", "_")
            if normalized in {
                "html",
                "raw_html",
                "javascript",
                "script",
                "code",
                "css",
                "executable",
                "template",
                "source_code",
            }:
                return f"{path}.{key_text}" if path else key_text
            found = _contains_dangerous_text(child, path=f"{path}.{key_text}" if path else key_text)
            if found:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = _contains_dangerous_text(child, path=f"{path}[{index}]")
            if found:
                return found
    elif isinstance(value, str):
        for pattern in _DANGEROUS_TEXT:
            if pattern.search(value):
                return path or "value"
    return None


def _placeholder_paths(value: Any, *, path: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if _is_unknown(child):
                paths.append(child_path)
            else:
                paths.extend(_placeholder_paths(child, path=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            if _is_unknown(child):
                paths.append(child_path)
            else:
                paths.extend(_placeholder_paths(child, path=child_path))
    return paths


def _safe_json(value: Any) -> Any:
    """Return a stable JSON-compatible deep copy with no custom objects."""

    if isinstance(value, Mapping):
        return {str(key): _safe_json(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_safe_json(child) for child in value]
    if isinstance(value, tuple):
        return [_safe_json(child) for child in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise BlueprintValidationError(f"blueprint contains unsupported value type: {type(value).__name__}")


class RemediationBlueprintService:
    """Validate and construct structured blueprint snapshots.

    This service never executes a blueprint.  ``evidence_resolver`` is an
    optional application callback used by integrations that want to re-check
    references against their repository before approval; structural validation
    remains useful for offline tests and worker review mode.
    """

    CONTRACT_VERSION = REMEDIATION_BLUEPRINT_VERSION
    RENDERER_VERSION = OFFLINE_PROTOTYPE_VERSION

    def __init__(self, *, evidence_resolver: Any | None = None) -> None:
        self.evidence_resolver = evidence_resolver

    def normalize(self, blueprint: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(blueprint, Mapping) or not blueprint:
            raise BlueprintValidationError("remediation blueprint must be a non-empty object")
        candidate = _safe_json(blueprint)
        dangerous = _contains_dangerous_text(candidate)
        if dangerous:
            raise BlueprintValidationError(f"blueprint contains executable or external field: {dangerous}")
        unknown_keys = sorted(set(candidate) - _ALLOWED_TOP_LEVEL)
        if unknown_keys:
            raise BlueprintValidationError(f"blueprint contains unsupported top-level fields: {unknown_keys}")
        normalized: dict[str, Any] = {}
        for key, value in candidate.items():
            canonical = _SECTION_ALIASES.get(key, key)
            if canonical in normalized and canonical != key:
                # Prefer the explicit canonical key and reject ambiguous input
                # instead of silently selecting one model branch.
                raise BlueprintValidationError(f"blueprint provides both {canonical!r} and alias {key!r}")
            normalized[canonical] = value
        normalized.setdefault("schema_version", REMEDIATION_BLUEPRINT_VERSION)
        if normalized["schema_version"] != REMEDIATION_BLUEPRINT_VERSION:
            raise BlueprintValidationError("unsupported remediation blueprint schema")
        for section in _CANONICAL_SECTIONS:
            if section not in normalized:
                normalized[section] = [] if section != "limitations" else []
        for section in _CANONICAL_SECTIONS:
            if section == "limitations":
                if not isinstance(normalized[section], list):
                    raise BlueprintValidationError("blueprint limitations must be a list")
            elif section == "crm":
                if not isinstance(normalized[section], (list, dict)):
                    raise BlueprintValidationError("blueprint CRM placement must be structured")
            elif isinstance(normalized[section], Mapping):
                # A section-level object is a useful shorthand for one
                # recommendation and remains unambiguous after normalization.
                normalized[section] = [normalized[section]]
            elif not isinstance(normalized[section], list):
                raise BlueprintValidationError(f"blueprint {section} must be a list")
        self._validate_items(normalized)
        normalized["placeholder_fields"] = sorted(set(_placeholder_paths(normalized)))
        return normalized

    def _validate_items(self, blueprint: Mapping[str, Any]) -> None:
        for section in _CANONICAL_SECTIONS:
            value = blueprint.get(section)
            if section in {"limitations", "crm"}:
                continue
            for index, item in enumerate(value or []):
                if not isinstance(item, Mapping):
                    raise BlueprintValidationError(f"{section}[{index}] must be an object")
                item_id = str(item.get("id") or item.get("key") or item.get("slug") or "").strip()
                if not item_id:
                    raise BlueprintValidationError(f"{section}[{index}] requires an id or key")
                status = str(item.get("status") or "recommended").strip().casefold()
                if status in _POSITIVE_STATUSES and not item.get("evidence_refs") and not item.get("evidence_ref_ids"):
                    raise BlueprintValidationError(f"{section}[{index}] positive recommendation requires evidence")
                if item.get("evidence_refs") is not None and not isinstance(item.get("evidence_refs"), list):
                    raise BlueprintValidationError(f"{section}[{index}] evidence_refs must be a list")
                for ref in item.get("evidence_refs", []) or []:
                    if not isinstance(ref, Mapping) or not str(ref.get("artifact_ref") or "").strip():
                        raise BlueprintValidationError(f"{section}[{index}] contains an invalid evidence reference")
                    if self.evidence_resolver is not None and not self.evidence_resolver(ref):
                        raise BlueprintValidationError(f"{section}[{index}] evidence cannot be resolved")

    def validate(
        self,
        snapshot: RemediationBlueprintSnapshot,
        *,
        require_approved: bool = False,
    ) -> dict[str, Any]:
        if not isinstance(snapshot, RemediationBlueprintSnapshot):
            raise BlueprintValidationError("renderer input must be RemediationBlueprintSnapshot")
        if snapshot.renderer_version != OFFLINE_PROTOTYPE_VERSION:
            raise BlueprintValidationError("unsupported offline prototype renderer")
        if require_approved and snapshot.review_state != "approved":
            raise BlueprintValidationError("prototype rendering requires an approved blueprint")
        normalized = self.normalize(snapshot.blueprint)
        declared = set(snapshot.placeholder_fields)
        observed = set(normalized["placeholder_fields"])
        if declared and not observed.issubset(declared):
            raise BlueprintValidationError("snapshot placeholder fields omit unknown blueprint values")
        # The snapshot's immutable content hash was checked by its model.  A
        # second comparison catches callers that mutate the dict after model
        # construction, which is especially important before customer export.
        if snapshot.content_sha256:
            expected = canonical_sha256(
                {
                    "contract_version": snapshot.contract_version,
                    "run_id": snapshot.run_id,
                    "attempt_id": snapshot.attempt_id,
                    "work_item_id": snapshot.work_item_id,
                    "mode": snapshot.mode,
                    "source_snapshot_ids": snapshot.source_snapshot_ids,
                    "source_sha256": snapshot.source_sha256,
                    "blueprint": snapshot.blueprint,
                    "evidence_refs": snapshot.evidence_refs,
                    "renderer_version": snapshot.renderer_version,
                    "placeholder_fields": snapshot.placeholder_fields,
                    "limitations": snapshot.limitations,
                }
            )
            if expected != snapshot.content_sha256:
                raise BlueprintValidationError("blueprint content hash no longer matches snapshot")
        return {
            "valid": True,
            "snapshot_id": snapshot.id,
            "run_id": snapshot.run_id,
            "mode": snapshot.mode,
            "review_state": snapshot.review_state,
            "blueprint": normalized,
            "placeholder_fields": sorted(observed),
            "source_snapshot_ids": sorted(set(snapshot.source_snapshot_ids)),
            "source_sha256": snapshot.source_sha256,
            "limitations": sorted(set(snapshot.limitations + normalized.get("limitations", []))),
        }

    validate_snapshot = validate

    def build_snapshot(self, **kwargs: Any) -> RemediationBlueprintSnapshot:
        """Create a snapshot after validating the structured candidate."""

        blueprint = self.normalize(kwargs.get("blueprint", {}))
        kwargs = dict(kwargs)
        kwargs["blueprint"] = blueprint
        kwargs.setdefault("renderer_version", OFFLINE_PROTOTYPE_VERSION)
        kwargs.setdefault("placeholder_fields", blueprint["placeholder_fields"])
        snapshot = RemediationBlueprintSnapshot(**kwargs)
        self.validate(snapshot)
        return snapshot

    create_snapshot = build_snapshot
    create = build_snapshot


class OfflinePrototypeRenderer:
    """Render an approved blueprint into a deterministic offline bundle."""

    RENDERER_VERSION = OFFLINE_PROTOTYPE_VERSION
    MANIFEST_VERSION = PROTOTYPE_MANIFEST_VERSION

    def __init__(self, output_root: str | Path, *, validator: RemediationBlueprintService | None = None) -> None:
        self.output_root = Path(output_root)
        self.validator = validator or RemediationBlueprintService()

    def render(self, snapshot: RemediationBlueprintSnapshot, *, bundle_id: str | None = None) -> PrototypeBundle:
        validation = self.validator.validate(snapshot, require_approved=True)
        blueprint = validation["blueprint"]
        rendering_hash = canonical_sha256(
            {
                "snapshot_id": snapshot.id,
                "content_sha256": snapshot.content_sha256,
                "renderer_version": self.RENDERER_VERSION,
                "blueprint": blueprint,
            }
        )
        resolved_id = bundle_id or f"{snapshot.id}-{rendering_hash[:16]}"
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,180}", resolved_id):
            raise PrototypeSafetyError("prototype bundle ID must be a safe relative name")
        root = (self.output_root / "prototypes" / resolved_id).resolve()
        output_root = self.output_root.resolve()
        if output_root != root and output_root not in root.parents:
            raise PrototypeSafetyError("prototype output escapes configured root")
        root.mkdir(parents=True, exist_ok=True)
        (root / "data").mkdir(exist_ok=True)
        (root / "assets").mkdir(exist_ok=True)

        payload = {
            "contract_version": REMEDIATION_BLUEPRINT_VERSION,
            "renderer_version": self.RENDERER_VERSION,
            "snapshot_id": snapshot.id,
            "run_id": snapshot.run_id,
            "attempt_id": snapshot.attempt_id,
            "mode": snapshot.mode,
            "visibility": "private_owner_only" if snapshot.mode == "owner_verified" else "prospect",
            "source_snapshot_ids": sorted(set(snapshot.source_snapshot_ids)),
            "source_sha256": snapshot.source_sha256,
            "content_sha256": snapshot.content_sha256,
            "blueprint": blueprint,
            "placeholder_fields": validation["placeholder_fields"],
            "limitations": validation["limitations"],
        }
        json_bytes = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n"
        (root / "data" / "blueprint.json").write_bytes(json_bytes)
        html_bytes = self._html(payload)
        self._assert_offline_html(html_bytes)
        (root / "index.html").write_bytes(html_bytes)

        files = [self._file_entry(root, "index.html", role="html"), self._file_entry(root, "data/blueprint.json", role="json")]
        manifest = self._manifest(resolved_id, snapshot, payload, files)
        manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n"
        (root / "manifest.json").write_bytes(manifest_bytes)
        manifest_entry = self._file_entry(root, "manifest.json", role="manifest")
        all_hash_entries = files + [manifest_entry]
        hashes = "".join(f"{entry['sha256']}  {entry['path']}\n" for entry in sorted(all_hash_entries, key=lambda item: item["path"]))
        (root / "hashes.sha256").write_text(hashes, encoding="utf-8")
        hash_entry = self._file_entry(root, "hashes.sha256", role="hashes")
        self._write_bundle_manifest(root, resolved_id, all_hash_entries, manifest)
        # The manifest intentionally excludes itself from its own file list;
        # otherwise there would be no stable fixed point for its SHA-256.
        return PrototypeBundle(
            id=resolved_id,
            snapshot_id=snapshot.id,
            run_id=snapshot.run_id,
            root=root,
            manifest_sha256=self._sha256((root / "manifest.json").read_bytes()),
            files=tuple(files + [manifest_entry, hash_entry]),
        )

    generate = render
    build = render

    def validate(self, bundle: PrototypeBundle | str | Path) -> dict[str, Any]:
        expected_manifest_hash = bundle.manifest_sha256 if isinstance(bundle, PrototypeBundle) else None
        root = bundle.root if isinstance(bundle, PrototypeBundle) else Path(bundle)
        root = root.resolve()
        manifest_path = root / "manifest.json"
        if not manifest_path.is_file():
            raise PrototypeSafetyError("prototype manifest is missing")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("manifest_version") != self.MANIFEST_VERSION:
            raise PrototypeSafetyError("unsupported prototype manifest")
        actual_manifest_hash = self._sha256(manifest_path.read_bytes())
        if expected_manifest_hash is not None and actual_manifest_hash != expected_manifest_hash:
            raise PrototypeSafetyError("prototype manifest hash does not match its immutable bundle record")
        # The manifest intentionally does not list itself (a recursive hash
        # would have no fixed point); it is covered by hashes.sha256 below.
        required_paths = {"index.html", "data/blueprint.json"}
        listed_paths = {str(entry.get("path", "")) for entry in manifest.get("files", [])}
        if not required_paths.issubset(listed_paths):
            raise PrototypeSafetyError("prototype manifest is missing required files")
        for entry in manifest.get("files", []):
            path = self._safe_path(root, str(entry.get("path", "")))
            if not path.is_file():
                raise PrototypeSafetyError(f"prototype manifest file is missing: {entry.get('path')}")
            actual = self._sha256(path.read_bytes())
            if actual != entry.get("sha256") or path.stat().st_size != entry.get("bytes"):
                raise PrototypeSafetyError(f"prototype manifest hash mismatch: {entry.get('path')}")
        html_path = root / "index.html"
        self._assert_offline_html(html_path.read_bytes())
        payload_path = root / "data" / "blueprint.json"
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        if payload.get("renderer_version") != self.RENDERER_VERSION:
            raise PrototypeSafetyError("prototype payload renderer mismatch")
        if payload.get("visibility") == "public_owner_only":
            raise PrototypeSafetyError("invalid prototype visibility")
        if not manifest.get("blueprint_sha256") or manifest.get("blueprint_sha256") != payload.get("content_sha256"):
            raise PrototypeSafetyError("prototype manifest blueprint hash does not match payload")
        hashes_path = root / "hashes.sha256"
        if not hashes_path.is_file():
            raise PrototypeSafetyError("prototype checksum file is missing")
        checksum_lines = [line.strip() for line in hashes_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        checksum_map: dict[str, str] = {}
        for line in checksum_lines:
            parts = line.split(None, 1)
            if len(parts) != 2 or not re.fullmatch(r"[a-f0-9]{64}", parts[0]):
                raise PrototypeSafetyError("prototype checksum file is malformed")
            checksum_map[PurePosixPath(parts[1]).as_posix()] = parts[0]
        if checksum_map.get("manifest.json") != actual_manifest_hash:
            raise PrototypeSafetyError("prototype checksum is missing: manifest.json")
        for entry in manifest.get("files", []):
            if checksum_map.get(str(entry.get("path"))) != entry.get("sha256"):
                raise PrototypeSafetyError(f"prototype checksum is missing: {entry.get('path')}")
        return {
            "valid": True,
            "bundle_id": manifest.get("bundle_id"),
            "snapshot_id": manifest.get("snapshot_id"),
            "checked_files": len(manifest.get("files", [])),
            "manifest_version": manifest.get("manifest_version"),
            "offline": True,
            "published": False,
        }

    validate_bundle = validate

    def publish(self, *_args: Any, **_kwargs: Any) -> None:
        raise PrototypeSafetyError("offline prototypes cannot be published or deployed by this service")

    def _manifest(self, bundle_id: str, snapshot: RemediationBlueprintSnapshot, payload: Mapping[str, Any], files: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "manifest_version": self.MANIFEST_VERSION,
            "bundle_id": bundle_id,
            "snapshot_id": snapshot.id,
            "run_id": snapshot.run_id,
            "attempt_id": snapshot.attempt_id,
            "blueprint_contract": REMEDIATION_BLUEPRINT_VERSION,
            "renderer_version": self.RENDERER_VERSION,
            "mode": snapshot.mode,
            "visibility": payload["visibility"],
            "source_snapshot_ids": sorted(set(snapshot.source_snapshot_ids)),
            "source_sha256": snapshot.source_sha256,
            "blueprint_sha256": snapshot.content_sha256,
            "files": sorted(files, key=lambda item: item["path"]),
            "assets": [],
            "publication": {"published": False, "deployment": False, "external_writes": False},
            "limitations": sorted(set(snapshot.limitations + ["Offline prototype only; no production changes were made."])),
        }

    @staticmethod
    def _write_bundle_manifest(root: Path, bundle_id: str, entries: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
        # The initial write is already deterministic.  Keep this hook explicit
        # so callers can inspect a stable manifest and future versions can add
        # an atomic write without changing the renderer API.
        if manifest.get("bundle_id") != bundle_id or not entries:
            raise PrototypeSafetyError("prototype manifest identity is invalid")

    @staticmethod
    def _sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def _file_entry(cls, root: Path, relative: str, *, role: str) -> dict[str, Any]:
        path = cls._safe_path(root, relative)
        data = path.read_bytes()
        return {"path": PurePosixPath(relative).as_posix(), "sha256": cls._sha256(data), "bytes": len(data), "role": role}

    @staticmethod
    def _safe_path(root: Path, relative: str) -> Path:
        parts = PurePosixPath(relative).parts
        if not relative or PurePosixPath(relative).is_absolute() or ".." in parts:
            raise PrototypeSafetyError("prototype bundle paths must be relative and contained")
        path = (root / Path(*parts)).resolve()
        if path != root and root not in path.parents:
            raise PrototypeSafetyError("prototype bundle path escapes its root")
        return path

    @classmethod
    def _assert_offline_html(cls, content: bytes) -> None:
        text = content.decode("utf-8")
        if re.search(r"<\s*script\b|\bon[a-z]+\s*=|(?:javascript|vbscript|data):", text, re.I):
            raise PrototypeSafetyError("prototype HTML contains executable or external content")
        if re.search(r"\b(?:src|href)\s*=\s*['\"](?:https?:|//)", text, re.I):
            raise PrototypeSafetyError("prototype HTML references an external resource")

    @classmethod
    def _html(cls, payload: Mapping[str, Any]) -> bytes:
        blueprint = payload["blueprint"]
        target = cls._display(blueprint.get("target"), "Target")
        title = cls._display(blueprint.get("title") or blueprint.get("summary"), "Offline prototype")
        summary = cls._display(blueprint.get("summary") or blueprint.get("executive_summary"), "Evidence-backed remediation preview.")

        def text(value: Any, fallback: str = PLACEHOLDER_TEXT) -> str:
            return html.escape(cls._display(value, fallback))

        def item_label(item: Mapping[str, Any]) -> str:
            return str(item.get("title") or item.get("label") or item.get("name") or item.get("id") or item.get("key") or "item")

        def render_items(section: str, heading: str) -> str:
            items = blueprint.get(section, [])
            if isinstance(items, Mapping):
                items = [items]
            rows: list[str] = []
            for item in sorted((dict(value) for value in items if isinstance(value, Mapping)), key=lambda value: (item_label(value).casefold(), str(value.get("id", "")))):
                label = text(item_label(item))
                status = text(item.get("status"), "recommended")
                description = text(item.get("description") or item.get("summary") or item.get("value"))
                refs = item.get("evidence_refs") or item.get("evidence_ref_ids") or []
                evidence_note = f"Evidence references: {len(refs)}" if refs else "Evidence: review required"
                rows.append(f'<article class="card"><h3>{label}</h3><p class="status">{status}</p><p>{description}</p><p class="evidence">{html.escape(evidence_note)}</p></article>')
            if not rows:
                rows.append(f'<p class="unknown">{html.escape(PLACEHOLDER_TEXT)}</p>')
            return f'<section id="{html.escape(section)}"><h2>{html.escape(heading)}</h2>{"".join(rows)}</section>'

        navigation = blueprint.get("navigation", [])
        if isinstance(navigation, Mapping):
            navigation = [navigation]
        nav_rows: list[str] = []
        for item in sorted((dict(value) for value in navigation if isinstance(value, Mapping)), key=lambda value: item_label(value).casefold()):
            label = text(item_label(item))
            destination = text(item.get("destination") or item.get("path") or item.get("url"))
            nav_rows.append(f'<li><a href="#navigation">{label}</a><span>{destination}</span></li>')
        nav_html = "".join(nav_rows) or f'<li class="unknown">{html.escape(PLACEHOLDER_TEXT)}</li>'
        limitations = blueprint.get("limitations", []) or []
        if not isinstance(limitations, list):
            limitations = [limitations]
        unknowns = payload.get("placeholder_fields", []) or []
        limitation_html = "".join(f"<li>{text(value)}</li>" for value in sorted([*limitations, *unknowns], key=lambda value: str(value).casefold())) or f'<li>{html.escape(PLACEHOLDER_TEXT)}</li>'
        visibility = "Private owner prototype" if payload.get("visibility") == "private_owner_only" else "Prospect prototype"
        body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{text(title)}</title>
<style>
:root{{color-scheme:light;--ink:#172033;--muted:#667085;--line:#d9dee8;--accent:#2557d6;--soft:#f5f7fb;--warn:#8a5a00}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--soft);color:var(--ink);font:16px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{max-width:1100px;margin:0 auto;padding:32px 20px 64px}}header,section{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px;margin-bottom:20px;box-shadow:0 8px 24px rgba(23,32,51,.05)}}h1,h2,h3{{line-height:1.2;margin-top:0}}h1{{font-size:clamp(2rem,5vw,3.5rem);margin-bottom:8px}}h2{{font-size:1.4rem;border-bottom:1px solid var(--line);padding-bottom:12px}}h3{{font-size:1.05rem;margin-bottom:4px}}p{{margin:8px 0}}.eyebrow,.status,.evidence{{color:var(--muted);font-size:.85rem;letter-spacing:.02em}}.banner{{border-left:4px solid var(--warn);background:#fff8e7;padding:12px 16px;border-radius:8px}}.card{{border:1px solid var(--line);border-radius:12px;padding:16px;margin:12px 0;background:#fff}}.status{{text-transform:uppercase;font-weight:700}}.evidence{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}ul{{padding-left:24px}}li{{margin:8px 0}}li span{{display:block;color:var(--muted);font-size:.9rem}}a{{color:var(--accent);text-decoration:none}}footer{{color:var(--muted);font-size:.8rem;padding:8px}}
</style>
</head>
<body><main>
<header><p class="eyebrow">{html.escape(visibility)} · {html.escape(OFFLINE_PROTOTYPE_VERSION)}</p><h1>{text(target)}</h1><p>{text(summary)}</p><div class="banner">This is an offline, evidence-backed prototype. Unknown facts are placeholders and no production site was changed.</div></header>
{render_items("sitemap", "Sitemap and page plan")}
<section id="navigation"><h2>Navigation</h2><ul>{nav_html}</ul></section>
{render_items("pages", "Page recommendations")}
{render_items("answer_blocks", "Answer blocks")}
{render_items("cta_flows", "CTA flow")}
{render_items("schema_recommendations", "Structured-data recommendations")}
{render_items("embeds", "Vertical functionality and embeds")}
{render_items("crm", "CRM placement")}
<section id="limitations"><h2>Limitations and unknowns</h2><ul>{limitation_html}</ul></section>
<footer>Snapshot {text(payload.get("snapshot_id"))} · Source-bound; not for publication or deployment.</footer>
</main></body></html>"""
        return body.encode("utf-8")

    @staticmethod
    def _display(value: Any, fallback: str = PLACEHOLDER_TEXT) -> str:
        if _is_unknown(value):
            return fallback
        if isinstance(value, Mapping):
            for key in ("value", "label", "name", "title", "text", "description"):
                if key in value and not _is_unknown(value[key]):
                    return OfflinePrototypeRenderer._display(value[key], fallback)
            return fallback
        if isinstance(value, list):
            return ", ".join(OfflinePrototypeRenderer._display(item, fallback) for item in value) or fallback
        return str(value) if value is not None else fallback


# Names used by callers and future API slices.  Keeping aliases here avoids
# coupling the renderer to a single route-specific service name.
RemediationBlueprintRenderer = OfflinePrototypeRenderer
PrototypeBundleService = OfflinePrototypeRenderer
