"""Deterministic, rights-aware asset resolution for History Documentary V4.

The asset manifest is the only contract that may introduce external media into
the documentary renderer.  This module deliberately keeps the boundary small:
it verifies a local file's path and bytes, applies the rights/likeness/logo and
alteration gates, and emits two immutable job-local JSON artifacts.  The
renderer-facing artifact contains asset IDs and local paths only; provenance
URLs and attribution live in ``credits.json`` instead.

The service has no network or provider dependencies.  ``validate_assets`` and
``main`` are intentionally usable by a future CLI without requiring the CLI to
import implementation details from the resolver.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlsplit

from jsonschema import Draft7Validator

from content.video_engine.src.models import StageContext, StageOutput, VideoRun


ASSET_MANIFEST_VERSION = "asset_manifest.v1"
RESOLVED_ASSETS_VERSION = "resolved_assets.v1"
CREDITS_VERSION = "credits.v1"
# Mirror the version constant naming used by the older video-engine services.
MANIFEST_VERSION = ASSET_MANIFEST_VERSION

# ``original`` is used when a creator made the asset for the project.  The
# explicit ``operator_owned`` spelling is retained for reviewed local assets.
CLEARED_PERMISSIONS = frozenset(
    {
        "original",
        "operator_owned",
        "licensed",
        "public_domain",
        "cc_by",
        "cc_by_sa",
    }
)
QUARANTINED_PERMISSIONS = frozenset(
    {"fair_use", "unverified", "research_only", "research-only", "research only"}
)
SUPPORTED_PERMISSIONS = CLEARED_PERMISSIONS | QUARANTINED_PERMISSIONS
ATTRIBUTION_PERMISSIONS = frozenset({"cc_by", "cc_by_sa"})
_HEX64 = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_REMOTE_PREFIX = re.compile(r"^(?:https?|data|blob|ftp|file):", re.IGNORECASE)


class AssetManifestValidationError(ValueError):
    """Raised when an asset manifest cannot be safely normalized.

    Every actionable error is retained in ``errors`` so an operator can fix a
    manifest in one pass rather than iterating on the first failure.
    """

    def __init__(self, errors: Iterable[str], *, asset_id: str | None = None):
        self.errors = list(errors)
        self.asset_id = asset_id
        detail = "; ".join(self.errors) or "invalid asset manifest"
        super().__init__(detail)


class AssetResolutionError(AssetManifestValidationError):
    """Raised when a manifest cannot be resolved into renderable assets."""


class AssetManifestImmutableError(ValueError):
    """Raised when a job-local artifact would change on a retry."""


def canonical_json(value: Any) -> str:
    """Return deterministic JSON used for artifact hashing and comparisons."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_sha256(path: str | Path) -> str:
    """Hash a local file in bounded chunks."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (Mapping, Sequence)) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _permission(value: Any) -> str:
    text = str(value or "").strip().casefold()
    return text.replace("-", "_").replace(" ", "_")


def _is_remote(value: str) -> bool:
    text = value.strip()
    if _REMOTE_PREFIX.match(text):
        return True
    # ``urlsplit`` treats a Windows drive as a scheme; only reject schemes
    # followed by ``//`` (or the explicitly handled data/blob prefixes).
    parsed = urlsplit(text)
    return bool(parsed.scheme and parsed.netloc)


def _as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AssetManifestValidationError([f"{label} must be an object"])
    return value


def _atomic_json_write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _write_immutable_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Atomically write an artifact, rejecting a changed retry."""

    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise AssetManifestImmutableError(
                f"existing asset artifact is unreadable: {path}"
            ) from exc
        if canonical_sha256(existing) != canonical_sha256(payload):
            raise AssetManifestImmutableError(
                f"asset artifact is immutable and differs: {path}"
            )
        return
    _atomic_json_write(path, payload)


def _strip_hash(payload: Mapping[str, Any], key: str = "artifact_hash") -> dict[str, Any]:
    result = copy.deepcopy(dict(payload))
    result.pop(key, None)
    return result


class AssetResolverService:
    """Validate an asset manifest and emit local resolver/credits artifacts."""

    def __init__(
        self,
        project_root: str | Path | None = None,
        job_dir: str | Path | None = None,
        *,
        schema_path: str | Path | None = None,
    ) -> None:
        self.project_root = Path(project_root).resolve() if project_root is not None else None
        self.job_dir = Path(job_dir).resolve() if job_dir is not None else None
        self.schema_path = (
            Path(schema_path).resolve()
            if schema_path is not None
            else Path(__file__).resolve().parents[2]
            / "configs"
            / "asset_manifest.schema.json"
        )

    # ------------------------------------------------------------------
    # Public contract API
    # ------------------------------------------------------------------
    def validate(
        self,
        manifest: Mapping[str, Any],
        *,
        project_root: str | Path | None = None,
        job_dir: str | Path | None = None,
        check_files: bool | None = None,
    ) -> dict[str, Any]:
        """Normalize and validate a manifest.

        Quarantined assets are valid manifest entries, but are normalized with
        ``render_eligible: false`` and a deterministic reason.  An explicit
        ``render_eligible: true`` declaration never overrides a failed rights,
        likeness, logo, alteration, or quarantine check.
        """

        raw = copy.deepcopy(dict(_as_mapping(manifest, "manifest")))
        errors: list[str] = []
        version = raw.get("schema_version", ASSET_MANIFEST_VERSION)
        if str(version) != ASSET_MANIFEST_VERSION:
            errors.append(
                f"manifest schema_version must be {ASSET_MANIFEST_VERSION!r}"
            )

        project = self._root(project_root, self.project_root)
        job = self._root(job_dir, self.job_dir)
        if check_files is None:
            check_files = bool(project or job)

        assets = raw.get("assets")
        if not isinstance(assets, list) or not assets:
            errors.append("manifest assets must be a non-empty array")
            assets = []

        normalized_assets: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for index, candidate in enumerate(assets):
            label = f"assets[{index}]"
            if not isinstance(candidate, Mapping):
                errors.append(f"{label} must be an object")
                continue
            normalized, asset_errors = self._normalize_asset(
                candidate,
                label=label,
                project_root=project,
                job_dir=job,
                check_files=bool(check_files),
            )
            asset_id = str(normalized.get("id") or "").strip()
            if not asset_id:
                errors.append(f"{label}.id is required")
            elif not _SAFE_ID.fullmatch(asset_id):
                errors.append(f"{label}.id contains unsafe characters: {asset_id!r}")
            elif asset_id in seen_ids:
                errors.append(f"duplicate asset id: {asset_id!r}")
            else:
                seen_ids.add(asset_id)
            errors.extend(asset_errors)
            normalized_assets.append(normalized)

        normalized: dict[str, Any] = {
            "schema_version": ASSET_MANIFEST_VERSION,
            "assets": normalized_assets,
        }
        for key in (
            "manifest_id",
            "project_id",
            "episode_id",
            "job_id",
            "project_root",
            "review",
            "notes",
        ):
            if key in raw:
                normalized[key] = copy.deepcopy(raw[key])
        # The source manifest may carry a hash from another system.  It is
        # checked below instead of being trusted as provenance.
        expected_hash = canonical_sha256(self._public_manifest(normalized))
        declared_hash = str(raw.get("artifact_hash") or "").strip().casefold()
        if declared_hash and declared_hash != expected_hash:
            errors.append(
                f"manifest artifact_hash {declared_hash!r} does not match canonical SHA-256 {expected_hash}"
            )
        normalized["artifact_hash"] = expected_hash

        self._validate_schema(self._public_manifest(normalized), errors)
        if errors:
            raise AssetManifestValidationError(errors)
        return normalized

    validate_manifest = validate

    def resolve(
        self,
        manifest: Mapping[str, Any] | str | Path,
        *,
        project_root: str | Path | None = None,
        job_dir: str | Path | None = None,
        output_dir: str | Path | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        """Resolve eligible assets and write immutable job-local artifacts.

        The returned mapping is the renderer-facing ``resolved_assets``
        payload.  Its entries contain no source URL, source citation, or raw
        rights object; consumers should use ``credits.json`` for credits.
        """

        loaded = self._load_manifest(manifest)
        project = self._root(project_root, self.project_root)
        job = self._root(job_dir, self.job_dir)
        if job is None:
            raise AssetResolutionError(["job_dir is required to resolve assets"])
        if not job.exists():
            job.mkdir(parents=True, exist_ok=True)
        if project is None:
            # A job-local manifest is a valid project root when no separate
            # project root was supplied.  This still gives us a containment
            # boundary and avoids silently resolving arbitrary CWD paths.
            project = job
        normalized = self.validate(
            loaded,
            project_root=project,
            job_dir=job,
            check_files=True,
        )
        effective_job_id = str(job_id or normalized.get("job_id") or job.name)
        if not effective_job_id:
            raise AssetResolutionError(["job_id is required to resolve assets"])

        resolved_items: list[dict[str, Any]] = []
        quarantined: list[dict[str, Any]] = []
        eligible_by_id: dict[str, dict[str, Any]] = {}
        for asset in normalized["assets"]:
            asset_id = str(asset["id"])
            if asset.get("render_eligible") is not True:
                reasons = asset.get("quarantine_reason") or ["asset is not render eligible"]
                if isinstance(reasons, str):
                    reasons = [reasons]
                quarantined.append(
                    {"asset_id": asset_id, "reasons": [str(reason) for reason in reasons]}
                )
                continue
            path = Path(str(asset["_resolved_path"]))
            relative_path = self._renderer_path(path, project_root=project, job_dir=job)
            item: dict[str, Any] = {
                "asset_id": asset_id,
                "id": asset_id,
                "path": relative_path,
                "local_path": relative_path,
                "sha256": str(asset["sha256"]).casefold(),
                "kind": str(asset.get("kind") or "illustration"),
                "role": str(asset.get("role") or asset.get("kind") or "asset"),
                "render_eligible": True,
            }
            # No arbitrary manifest fields are copied here.  In particular,
            # ``source``, ``origin``, ``source_url``, ``license``, and rights
            # details cannot leak into a renderer instruction.
            resolved_items.append(item)
            eligible_by_id[asset_id] = asset

        resolved_core: dict[str, Any] = {
            "schema_version": RESOLVED_ASSETS_VERSION,
            "manifest_version": ASSET_MANIFEST_VERSION,
            "job_id": effective_job_id,
            "asset_ids": [item["asset_id"] for item in resolved_items],
            "assets": resolved_items,
            "quarantined_assets": quarantined,
            "manifest_hash": str(normalized["artifact_hash"]),
        }
        resolved_payload = dict(resolved_core)
        resolved_payload["artifact_hash"] = canonical_sha256(resolved_core)

        credits_core = self._build_credits(
            normalized,
            eligible_by_id,
            effective_job_id,
            resolved_payload["artifact_hash"],
        )
        credits_payload = dict(credits_core)
        credits_payload["artifact_hash"] = canonical_sha256(credits_core)

        target_dir = self._output_dir(output_dir, job)
        resolved_path = target_dir / "resolved_assets.json"
        credits_path = target_dir / "credits.json"
        _write_immutable_json(resolved_path, resolved_payload)
        _write_immutable_json(credits_path, credits_payload)

        # Keep the service result useful to a stage caller without exposing
        # source metadata to a renderer.  Paths are job-local artifact paths.
        return {
            **resolved_payload,
            "resolved_assets_path": str(resolved_path.relative_to(job).as_posix()),
            "credits_path": str(credits_path.relative_to(job).as_posix()),
            "credits": credits_payload.get("credits", []),
        }

    resolve_assets = resolve
    resolve_manifest = resolve

    def persist(
        self,
        manifest: Mapping[str, Any],
        output_dir: str | Path,
        *,
        project_root: str | Path | None = None,
        job_dir: str | Path | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        """Compatibility alias for callers that call artifact writes ``persist``."""

        return self.resolve(
            manifest,
            project_root=project_root,
            job_dir=job_dir,
            output_dir=output_dir,
            job_id=job_id,
        )

    write = persist

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        """Pipeline-compatible adapter; callers may register it as a stage."""

        manifest_input = self._manifest_from_context(job, ctx)
        project_root = (
            ctx.configs.get("asset_project_root")
            or ctx.configs.get("project_root")
            or ctx.configs.get("video_engine_root")
            or ctx.job_dir
        )
        result = self.resolve(
            manifest_input,
            project_root=project_root,
            job_dir=ctx.job_dir,
            output_dir=ctx.job_dir,
            job_id=job.id,
        )
        return StageOutput(
            {
                "artifact_path": result["resolved_assets_path"],
                "credits_path": result["credits_path"],
                "asset_count": len(result.get("assets", [])),
                "quarantined_count": len(result.get("quarantined_assets", [])),
                "asset_manifest_hash": result.get("manifest_hash"),
                "resolved_assets_hash": result.get("artifact_hash"),
                "cost_usd": 0.0,
            }
        )

    # ------------------------------------------------------------------
    # Normalization and validation helpers
    # ------------------------------------------------------------------
    def _normalize_asset(
        self,
        candidate: Mapping[str, Any],
        *,
        label: str,
        project_root: Path | None,
        job_dir: Path | None,
        check_files: bool,
    ) -> tuple[dict[str, Any], list[str]]:
        errors: list[str] = []
        asset = copy.deepcopy(dict(candidate))
        asset_id = str(
            asset.get("id") or asset.get("asset_id") or asset.get("name") or ""
        ).strip().casefold()
        path_value = (
            asset.get("path")
            or asset.get("local_path")
            or asset.get("asset_path")
            or asset.get("source_path")
            or asset.get("file")
        )
        path_text = str(path_value or "").strip()
        sha = str(
            asset.get("sha256")
            or asset.get("content_sha256")
            or asset.get("hash")
            or asset.get("content_hash")
            or ""
        ).strip().casefold()

        rights_raw = asset.get("rights")
        rights = dict(rights_raw) if isinstance(rights_raw, Mapping) else {}
        permission = _permission(
            rights.get("permission")
            or rights.get("status")
            or asset.get("permission")
            or asset.get("rights_status")
            or asset.get("license")
        )
        license_name = str(
            rights.get("license") or asset.get("license") or ""
        ).strip()
        reviewed = rights.get("reviewed") is True
        if not reviewed:
            reviewed = (
                rights.get("approved") is True
                or rights.get("operator_approved") is True
                or rights.get("review_status") in {"reviewed", "approved"}
                or asset.get("rights_reviewed") is True
                or asset.get("reviewed") is True
            )
        source = rights.get("source") or rights.get("source_ref") or asset.get("source")
        if not _has_value(source):
            source = asset.get("origin")
        source_url = rights.get("source_url") or asset.get("source_url")
        attribution = rights.get("attribution") or asset.get("attribution")
        attribution_required = (
            rights.get("attribution_required") is True
            or asset.get("attribution_required") is True
            or permission in ATTRIBUTION_PERMISSIONS
        )
        normalized_rights: dict[str, Any] = {
            "permission": permission,
            "reviewed": reviewed,
            "reviewed_by": rights.get("reviewed_by") or asset.get("reviewed_by"),
            "reviewed_at": rights.get("reviewed_at") or asset.get("reviewed_at"),
            "license": license_name or None,
            "source": copy.deepcopy(source) if _has_value(source) else None,
            "source_url": str(source_url).strip() if _has_value(source_url) else None,
            "attribution_required": attribution_required,
            "attribution": copy.deepcopy(attribution) if _has_value(attribution) else None,
        }

        if not asset_id:
            errors.append(f"{label}.id is required")
        if not path_text:
            errors.append(f"{label}.path must reference a local file")
        elif _is_remote(path_text):
            errors.append(f"{label}.path must be a local path; URLs are not allowed")
        if not _HEX64.fullmatch(sha):
            errors.append(f"{label}.sha256 must be a 64-character hexadecimal digest")
        if permission not in SUPPORTED_PERMISSIONS:
            errors.append(
                f"{label}.rights.permission must be one of "
                + ", ".join(sorted(SUPPORTED_PERMISSIONS))
            )
        if permission in CLEARED_PERMISSIONS:
            if not reviewed:
                errors.append(f"{label}.rights must be reviewed before rendering")
            if not _has_value(source):
                errors.append(f"{label}.rights.source/origin is required for auditability")

        resolved_path: Path | None = None
        if path_text and not _is_remote(path_text) and (project_root or job_dir):
            try:
                resolved_path = self._resolve_local_path(
                    path_text,
                    project_root=project_root,
                    job_dir=job_dir,
                )
            except AssetManifestValidationError as exc:
                errors.extend(f"{label}: {error}" for error in exc.errors)
        if check_files and resolved_path is None and path_text and not _is_remote(path_text):
            errors.append(f"{label}.path could not be resolved inside project/job roots")
        if resolved_path is not None:
            actual = file_sha256(resolved_path)
            if actual != sha:
                errors.append(
                    f"{label}.sha256 does not match local bytes (declared {sha}, actual {actual})"
                )

        quarantine: list[str] = []
        if permission in QUARANTINED_PERMISSIONS:
            quarantine.append(f"permission:{permission}")
        if permission not in CLEARED_PERMISSIONS:
            quarantine.append("rights_not_cleared")
        if permission in CLEARED_PERMISSIONS and not reviewed:
            quarantine.append("rights_not_reviewed")

        likeness, living, likeness_approved = self._likeness(candidate)
        if living and not likeness_approved:
            quarantine.append("living_person_likeness_requires_operator_approval")
        logo, logo_present, logo_approved = self._logo(candidate)
        if logo_present and not logo_approved:
            quarantine.append("logo_permission_required")
        alteration, altered, alteration_allowed = self._alteration(candidate)
        if altered and not alteration_allowed:
            quarantine.append("alteration_not_permitted_by_policy")
        if attribution_required and not self._valid_attribution(attribution):
            quarantine.append("attribution_required_for_license")

        explicit_render = asset.get("render_eligible")
        render_eligible = explicit_render is True
        # A missing declaration is intentionally conservative: only a fully
        # rights-cleared, reviewed, verified local asset becomes renderable.
        if explicit_render is None:
            render_eligible = not quarantine and not errors
        elif explicit_render is False:
            render_eligible = False
        elif quarantine or errors:
            errors.append(
                f"{label}.render_eligible=true conflicts with failed asset gates: "
                + ", ".join(quarantine or errors)
            )
            render_eligible = False

        normalized: dict[str, Any] = {
            "id": asset_id,
            "path": path_text,
            "sha256": sha,
            "kind": str(asset.get("kind") or asset.get("asset_kind") or "illustration"),
            "role": str(asset.get("role") or asset.get("use") or asset.get("kind") or "asset"),
            "origin": copy.deepcopy(asset.get("origin") or source),
            "rights": normalized_rights,
            "license": license_name or None,
            "attribution": copy.deepcopy(attribution) if _has_value(attribution) else None,
            "likeness": likeness,
            "logo": logo,
            "alteration_policy": alteration,
            "altered": altered,
            "render_eligible": bool(render_eligible),
        }
        if _has_value(asset.get("title")):
            normalized["title"] = str(asset["title"])
        if _has_value(asset.get("creator") or asset.get("author")):
            normalized["creator"] = str(asset.get("creator") or asset.get("author"))
        if _has_value(source_url):
            # Source URLs remain in the validated manifest/credits domain only.
            normalized["source_url"] = str(source_url).strip()
        if quarantine:
            normalized["quarantine_reason"] = sorted(set(quarantine))
        if resolved_path is not None:
            # Private normalization detail removed before renderer output.
            normalized["_resolved_path"] = str(resolved_path)
        if isinstance(asset.get("metadata"), Mapping):
            normalized["metadata"] = copy.deepcopy(dict(asset["metadata"]))
        return normalized, errors

    @staticmethod
    def _root(value: str | Path | None, fallback: Path | None) -> Path | None:
        if value is None:
            return fallback
        return Path(value).resolve()

    @staticmethod
    def _resolve_local_path(
        value: str,
        *,
        project_root: Path | None,
        job_dir: Path | None,
    ) -> Path:
        raw = Path(value)
        if raw.is_absolute():
            candidates = [raw]
        else:
            candidates = []
            if project_root is not None:
                candidates.append(project_root / raw)
            if job_dir is not None:
                candidates.append(job_dir / raw)
        roots = [root.resolve() for root in (project_root, job_dir) if root is not None]
        if not roots:
            raise AssetManifestValidationError(["project_root or job_dir is required for path containment"])
        for candidate in candidates:
            try:
                resolved = candidate.resolve(strict=True)
            except (OSError, RuntimeError):
                continue
            if not resolved.is_file():
                continue
            if any(AssetResolverService._is_within(resolved, root) for root in roots):
                return resolved
        raise AssetManifestValidationError(
            [f"path {value!r} does not resolve to a local file inside project/job roots"]
        )

    @staticmethod
    def _is_within(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
        except ValueError:
            return False
        return True

    @staticmethod
    def _renderer_path(path: Path, *, project_root: Path, job_dir: Path) -> str:
        # Prefer a job-relative path when the source is already job-local;
        # otherwise use a project-relative path.  Both are safe local paths and
        # never contain a URL or a traversal component.
        try:
            relative = path.relative_to(job_dir)
        except ValueError:
            try:
                relative = path.relative_to(project_root)
            except ValueError as exc:
                raise AssetResolutionError(
                    [f"resolved asset escapes project/job roots: {path}"]
                ) from exc
        return relative.as_posix()

    @staticmethod
    def _likeness(asset: Mapping[str, Any]) -> tuple[dict[str, Any], bool, bool]:
        raw = asset.get("likeness")
        likeness = dict(raw) if isinstance(raw, Mapping) else {}
        living = bool(
            asset.get("living_person") is True
            or likeness.get("living") is True
            or likeness.get("living_person") is True
            or bool(likeness.get("living_persons"))
        )
        subjects = likeness.get("subjects")
        if isinstance(subjects, list):
            living = living or any(
                isinstance(subject, Mapping)
                and (subject.get("living") is True or subject.get("living_person") is True)
                for subject in subjects
            )
        approved = bool(
            asset.get("likeness_approved") is True
            or likeness.get("approved") is True
            or likeness.get("operator_approved") is True
            or likeness.get("reference_approved") is True
        )
        return (
            {
                "living": living,
                "approved": approved,
                "subjects": copy.deepcopy(subjects or []),
            },
            living,
            approved,
        )

    @staticmethod
    def _logo(asset: Mapping[str, Any]) -> tuple[dict[str, Any], bool, bool]:
        raw = asset.get("logo")
        if isinstance(raw, Mapping):
            logo = dict(raw)
            present = bool(
                asset.get("is_logo") is True
                or logo.get("is_logo") is True
                or logo.get("contains_logo") is True
                or logo.get("name")
                or logo.get("id")
            )
        else:
            present = bool(asset.get("is_logo") is True or asset.get("contains_logo") is True or raw)
            logo = {"name": str(raw)} if isinstance(raw, str) and raw.strip() else {}
        approved = bool(
            asset.get("logo_permission") is True
            or logo.get("permission") is True
            or str(logo.get("permission") or "").casefold() in {"approved", "granted", "licensed"}
            or logo.get("approved") is True
            or logo.get("operator_approved") is True
            or logo.get("trademark_permission") is True
        )
        return ({"present": present, "approved": approved, **logo}, present, approved)

    @staticmethod
    def _alteration(asset: Mapping[str, Any]) -> tuple[dict[str, Any], bool, bool]:
        raw = asset.get("alteration_policy")
        if raw is None:
            raw = asset.get("alteration")
        if isinstance(raw, Mapping):
            policy = dict(raw)
            allowed = policy.get("allowed", policy.get("permitted")) is True
            altered = asset.get("altered") is True or policy.get("altered") is True
        elif isinstance(raw, bool):
            policy = {"allowed": raw}
            allowed = raw
            altered = asset.get("altered") is True
        elif _has_value(raw):
            policy = {"policy": str(raw)}
            allowed = False
            altered = True
        else:
            policy = {"allowed": False}
            allowed = False
            altered = asset.get("altered") is True
        return ({"allowed": allowed, **policy}, altered, allowed)

    @staticmethod
    def _valid_attribution(value: Any) -> bool:
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, Mapping):
            return any(_has_value(value.get(key)) for key in ("text", "title", "creator", "author"))
        if isinstance(value, list):
            return bool(value) and all(AssetResolverService._valid_attribution(item) for item in value)
        return False

    def _validate_schema(self, manifest: Mapping[str, Any], errors: list[str]) -> None:
        if not self.schema_path.exists():
            return
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
            schema_errors = sorted(
                Draft7Validator(schema).iter_errors(dict(manifest)),
                key=lambda error: list(error.absolute_path),
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"asset manifest schema could not be loaded: {exc}")
            return
        errors.extend(
            "manifest "
            + (".".join(str(part) for part in error.absolute_path) or "root")
            + f": {error.message}"
            for error in schema_errors
        )

    @staticmethod
    def _public_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
        """Remove private absolute paths before hashing/schema validation."""

        result = copy.deepcopy(dict(manifest))
        assets = result.get("assets")
        if isinstance(assets, list):
            for asset in assets:
                if isinstance(asset, dict):
                    asset.pop("_resolved_path", None)
        return result

    def _build_credits(
        self,
        manifest: Mapping[str, Any],
        eligible_by_id: Mapping[str, Mapping[str, Any]],
        job_id: str,
        resolved_hash: str,
    ) -> dict[str, Any]:
        credits: list[dict[str, Any]] = []
        for asset in manifest.get("assets", []):
            if not isinstance(asset, Mapping) or asset.get("id") not in eligible_by_id:
                continue
            asset_id = str(asset["id"])
            rights = asset.get("rights") if isinstance(asset.get("rights"), Mapping) else {}
            permission = str(rights.get("permission") or asset.get("license") or "")
            license_name = str(rights.get("license") or asset.get("license") or permission).strip()
            attribution = asset.get("attribution") or rights.get("attribution")
            attribution_text = self._attribution_text(asset, attribution, permission)
            credit: dict[str, Any] = {
                "asset_id": asset_id,
                "id": asset_id,
                "credit": attribution_text,
                "attribution": attribution_text,
                "license": license_name or None,
            }
            source_url = (
                asset.get("source_url")
                or rights.get("source_url")
                or self._attribution_url(attribution)
            )
            if _has_value(source_url):
                credit["source_url"] = str(source_url).strip()
            credits.append(credit)
        core: dict[str, Any] = {
            "schema_version": CREDITS_VERSION,
            "manifest_version": ASSET_MANIFEST_VERSION,
            "job_id": job_id,
            "resolved_assets_hash": resolved_hash,
            "asset_ids": [str(item["asset_id"]) for item in credits],
            "credits": credits,
        }
        return core

    @staticmethod
    def _attribution_text(
        asset: Mapping[str, Any], attribution: Any, permission: str
    ) -> str:
        if isinstance(attribution, str) and attribution.strip():
            return attribution.strip()
        if isinstance(attribution, Mapping):
            text = attribution.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
            pieces: list[str] = []
            title = attribution.get("title") or asset.get("title")
            creator = attribution.get("creator") or attribution.get("author") or asset.get("creator")
            if title:
                pieces.append(str(title).strip())
            if creator:
                pieces.append(f"by {str(creator).strip()}")
            if pieces:
                return " ".join(pieces)
        title = str(asset.get("title") or asset.get("id") or "Asset").strip()
        if permission:
            return f"{title} ({permission})"
        return title

    @staticmethod
    def _attribution_url(attribution: Any) -> str | None:
        if isinstance(attribution, Mapping):
            value = attribution.get("url") or attribution.get("source_url")
            if _has_value(value):
                return str(value).strip()
        return None

    @staticmethod
    def _load_manifest(value: Mapping[str, Any] | str | Path) -> dict[str, Any]:
        if isinstance(value, Mapping):
            return copy.deepcopy(dict(value))
        path = Path(value)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise AssetManifestValidationError([f"asset manifest is not valid JSON: {exc}"]) from exc
        if not isinstance(loaded, Mapping):
            raise AssetManifestValidationError(["asset manifest JSON root must be an object"])
        return dict(loaded)

    @staticmethod
    def _output_dir(value: str | Path | None, job_dir: Path) -> Path:
        target = Path(value).resolve() if value is not None else job_dir
        if not AssetResolverService._is_within(target, job_dir):
            raise AssetResolutionError([f"output_dir escapes job directory: {target}"])
        target.mkdir(parents=True, exist_ok=True)
        return target

    @staticmethod
    def _manifest_from_context(job: VideoRun, ctx: StageContext) -> Mapping[str, Any] | str | Path:
        for key in ("asset_manifest", "asset_manifest_path", "assets_manifest", "assets_manifest_path"):
            if key in job.input_payload and job.input_payload[key] is not None:
                return job.input_payload[key]
        for key in ("asset_manifest", "asset_manifest_path", "assets_manifest", "assets_manifest_path"):
            if key in ctx.configs and ctx.configs[key] is not None:
                return ctx.configs[key]
        local = ctx.job_dir / "asset_manifest.json"
        if local.is_file():
            return local
        raise AssetResolutionError(["asset manifest input is required"])


# Friendly aliases used by callers that name the domain object rather than the
# implementation service.
AssetManifestService = AssetResolverService
AssetResolver = AssetResolverService
AssetManifestError = AssetManifestValidationError
ImmutableAssetArtifactError = AssetManifestImmutableError


def validate_asset_manifest(
    manifest: Mapping[str, Any] | str | Path,
    *,
    project_root: str | Path | None = None,
    job_dir: str | Path | None = None,
    schema_path: str | Path | None = None,
    check_files: bool | None = None,
) -> dict[str, Any]:
    """CLI-callable validation helper returning a canonical manifest."""

    service = AssetResolverService(
        project_root=project_root,
        job_dir=job_dir,
        schema_path=schema_path,
    )
    return service.validate(
        AssetResolverService._load_manifest(manifest),
        check_files=check_files,
    )


validate_assets = validate_asset_manifest


def run_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    return AssetResolverService().run_stage(job, ctx)


def main(argv: Sequence[str] | None = None) -> int:
    """Small validation command for operators and future CLI integration."""

    parser = argparse.ArgumentParser(description="Validate a local asset manifest")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--job-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--resolve", action="store_true")
    args = parser.parse_args(argv)
    try:
        service = AssetResolverService(args.project_root, args.job_dir)
        if args.resolve:
            result = service.resolve(
                args.manifest,
                output_dir=args.output_dir,
            )
        else:
            result = service.validate(
                AssetResolverService._load_manifest(args.manifest),
                check_files=bool(args.project_root or args.job_dir),
            )
    except (AssetManifestValidationError, AssetManifestImmutableError, OSError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by CLI callers
    raise SystemExit(main())


__all__ = [
    "ASSET_MANIFEST_VERSION",
    "MANIFEST_VERSION",
    "AssetManifestError",
    "AssetManifestImmutableError",
    "AssetManifestService",
    "AssetManifestValidationError",
    "AssetResolutionError",
    "AssetResolver",
    "AssetResolverService",
    "CLEARED_PERMISSIONS",
    "CREDITS_VERSION",
    "QUARANTINED_PERMISSIONS",
    "RESOLVED_ASSETS_VERSION",
    "canonical_json",
    "canonical_sha256",
    "file_sha256",
    "main",
    "run_stage",
    "validate_asset_manifest",
    "validate_assets",
]
