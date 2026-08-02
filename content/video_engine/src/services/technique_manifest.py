"""Rights-aware technique visual manifest discovery and validation.

The visual manifest is deliberately a sidecar to the canonical corpus.  It can
describe how an operator-reviewed action should be rendered, but it never
changes transcript facts.  The service is deterministic, has no provider
dependencies, and writes only the job-local ``technique_manifest.json``
artifact.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft7Validator

from content.video_engine.src.models import StageContext, StageOutput, VideoRun


MANIFEST_VERSION = "technique_visual_manifest.v1"
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_PERMISSIONS = {
    "operator_owned",
    "licensed",
    "internal",
    "public_domain",
    "cc0",
}
_PERMISSION_ALIASES = {
    "operator-owned": "operator_owned",
    "operator owned": "operator_owned",
    "operator": "operator_owned",
    "owned": "operator_owned",
    "licensed_material": "licensed",
    "public-domain": "public_domain",
    "public domain": "public_domain",
    "approved": "operator_owned",
    "cleared": "operator_owned",
}
_DEFAULT_CAST: dict[str, dict[str, Any]] = {
    "attacker": {
        "id": "attacker",
        "color": "#E8F1FF",
        "gi": "white_gi",
        "belt": "blue_belt",
        "depth": 1,
    },
    "defender": {
        "id": "defender",
        "color": "#596273",
        "gi": "black_gi",
        "belt": "purple_belt",
        "depth": 0,
    },
}
_DEFAULT_STYLE = "flat_vector_bjj"
_DEFAULT_FUNCTIONS = {
    "result_preview",
    "wide_setup",
    "contact_closeup",
    "mechanic_transition",
    "wrong_right_compare",
    "force_diagram",
    "result_hold",
    "story_or_persona_cutaway",
}


class TechniqueManifestValidationError(ValueError):
    """Raised when a sidecar cannot safely drive instructional rendering.

    ``errors`` intentionally contains every actionable violation rather than
    stopping at the first invalid action.  Operators can therefore fix one
    sidecar in one review pass.
    """

    def __init__(self, errors: Iterable[str], *, slug: str | None = None):
        self.errors = list(errors)
        self.slug = slug
        detail = "; ".join(self.errors) or "invalid technique visual manifest"
        super().__init__(detail)


class TechniqueManifestService:
    """Discover, normalize, validate, and persist a visual manifest sidecar."""

    def __init__(
        self,
        manifest_root: str | Path | None = None,
        *,
        schema_path: str | Path | None = None,
    ) -> None:
        self.manifest_root = Path(manifest_root) if manifest_root is not None else None
        self.schema_path = (
            Path(schema_path)
            if schema_path is not None
            else Path(__file__).resolve().parents[2]
            / "configs"
            / "technique_visual_manifest.schema.json"
        )

    # ------------------------------------------------------------------
    # Public discovery/validation API.  The small aliases make this service
    # convenient for direct callers as well as the pipeline stage adapter.
    # ------------------------------------------------------------------
    def discover(
        self,
        slug: str,
        *,
        manifest_root: str | Path | None = None,
        explicit_input: Any | None = None,
    ) -> Path | dict[str, Any] | None:
        """Return an explicit sidecar or deterministic slug-matched sidecar.

        ``explicit_input`` may be a mapping, a JSON path, or a JSON string.  A
        mapping is returned as a deep copy so callers cannot mutate the input
        object while validation is running.  Roots are searched in a fixed
        order and only slug-matched file names are accepted.
        """

        slug = str(slug).strip().casefold()
        if not _SLUG_RE.fullmatch(slug):
            raise ValueError(f"unsafe technique manifest slug: {slug!r}")
        if explicit_input is not None:
            if isinstance(explicit_input, Mapping):
                return copy.deepcopy(dict(explicit_input))
            return self._coerce_path(explicit_input, purpose="explicit technique manifest")

        root = Path(manifest_root) if manifest_root is not None else self.manifest_root
        if root is None:
            return None
        if not root.exists():
            return None
        if root.is_file():
            return root if self._is_slug_match(root, slug) else None

        # Sidecars normally use ``<slug>.json``.  The suffix variants keep the
        # discovery contract friendly to existing assets without accepting an
        # arbitrary JSON file from the references directory.
        candidates = (
            root / f"{slug}.json",
            root / f"{slug}.technique.json",
            root / f"{slug}.visual.json",
            root / f"{slug}.manifest.json",
            root / slug / "manifest.json",
            root / slug / "technique_visual_manifest.json",
        )
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        for candidate in sorted(root.rglob("*.json")):
            if self._is_slug_match(candidate, slug):
                return candidate
        return None

    find = discover

    def load(
        self,
        slug: str,
        *,
        manifest_root: str | Path | None = None,
        explicit_input: Any | None = None,
    ) -> dict[str, Any] | None:
        """Load a discovered sidecar without mutating or validating it."""

        discovered = self.discover(
            slug, manifest_root=manifest_root, explicit_input=explicit_input
        )
        if discovered is None:
            return None
        payload, _source = self._load_input(discovered)
        return payload

    def validate(
        self,
        manifest: Mapping[str, Any],
        *,
        slug: str | None = None,
    ) -> dict[str, Any]:
        """Return a normalized manifest or raise with all per-action errors."""

        raw = copy.deepcopy(dict(manifest))
        errors: list[str] = []
        raw_version = raw.get("schema_version")
        if raw_version is not None and str(raw_version) != MANIFEST_VERSION:
            errors.append(
                f"manifest schema_version {raw_version!r} is not {MANIFEST_VERSION!r}"
            )
        resolved_slug = str(raw.get("slug") or slug or "").strip().casefold()
        if not resolved_slug:
            errors.append("manifest is missing slug")
        elif not _SLUG_RE.fullmatch(resolved_slug):
            errors.append(f"manifest slug {resolved_slug!r} is not a safe slug")
        if slug and resolved_slug and resolved_slug != str(slug).strip().casefold():
            errors.append(
                f"manifest slug {resolved_slug!r} does not match requested slug {slug!r}"
            )

        rights = self._normalize_rights(raw.get("rights"), raw)
        rights_errors = self._validate_rights(rights)
        errors.extend(rights_errors)

        references = self._normalize_references(raw.get("references"), rights)
        reference_errors = self._validate_references(references)
        errors.extend(reference_errors)

        states = self._normalize_states(raw.get("states"))
        actions = raw.get("actions")
        if actions is None:
            actions = raw.get("action_states")
        if not isinstance(actions, list) or not actions:
            errors.append("manifest actions must be a non-empty array")
            actions = []

        normalized_actions: list[dict[str, Any]] = []
        action_ids: set[str] = set()
        for index, candidate in enumerate(actions):
            prefix = self._action_prefix(candidate, index)
            if not isinstance(candidate, Mapping):
                errors.append(f"{prefix}: action must be an object")
                continue
            action = self._normalize_action(candidate)
            action_id = str(action.get("id") or "").strip()
            if not action_id:
                errors.append(f"{prefix}: missing action id")
            elif action_id in action_ids:
                errors.append(f"action {action_id!r}: duplicate action id")
            else:
                action_ids.add(action_id)
            for field in ("state_from", "action", "state_to", "contact", "motion_path"):
                if not self._has_value(action.get(field)):
                    errors.append(f"action {action_id or index!r}: missing {field}")
            if action.get("reviewed") is not True:
                errors.append(f"action {action_id or index!r}: reviewed action state is required")
            for state_field in ("state_from", "state_to"):
                state_id = str(action.get(state_field) or "").strip()
                if state_id and states and state_id not in states:
                    errors.append(
                        f"action {action_id or index!r}: {state_field} {state_id!r} is not declared"
                    )
                elif state_id and states and states[state_id].get("reviewed") is not True:
                    errors.append(
                        f"action {action_id or index!r}: {state_field} {state_id!r} is not reviewed"
                    )
            refs = list(action.get("reference_refs") or [])
            if not refs and rights_errors:
                errors.append(f"action {action_id or index!r}: missing permission")
            if "permission" in candidate:
                action_permission = self._normalize_permission(candidate.get("permission"))
                if action_permission not in _PERMISSIONS:
                    errors.append(f"action {action_id or index!r}: permission is not rights-cleared")
            for ref_id in refs:
                if ref_id not in references:
                    errors.append(
                        f"action {action_id or index!r}: reference {ref_id!r} is not declared"
                    )
                elif not self._reference_is_cleared(references[ref_id]):
                    errors.append(
                        f"action {action_id or index!r}: reference {ref_id!r} lacks permission/review"
                    )
            # A sidecar may put a per-action permission object next to the
            # recipe; validate it too when present rather than silently trusting
            # a local override.
            if "rights" in candidate:
                local_rights = self._normalize_rights(candidate.get("rights"), candidate)
                if self._validate_rights(local_rights):
                    errors.extend(
                        f"action {action_id or index!r}: {message}"
                        for message in self._validate_rights(local_rights)
                    )
            normalized_actions.append(action)

        normalized: dict[str, Any] = {
            "schema_version": MANIFEST_VERSION,
            "slug": resolved_slug,
            "name": str(raw.get("name") or resolved_slug.replace("-", " ").title()),
            "style_preset": str(
                raw.get("style_preset") or raw.get("style") or _DEFAULT_STYLE
            ),
            "cast": self._normalize_cast(raw.get("cast")),
            "rights": rights,
            "provenance": dict(raw.get("provenance") or {}),
            "references": list(references.values()),
            "states": states,
            "actions": normalized_actions,
        }
        for key in ("beat_actions", "beat_map", "compile_policy"):
            if key in raw:
                normalized[key] = copy.deepcopy(raw[key])
        # Keep non-contract metadata useful to a human reviewer while avoiding
        # accidental transcript changes.  These fields are deterministic and
        # are ignored by the renderer.
        for key in ("description", "notes", "review", "source_ref"):
            if key in raw:
                normalized[key] = copy.deepcopy(raw[key])

        if errors:
            raise TechniqueManifestValidationError(errors, slug=resolved_slug or slug)
        self._validate_schema(normalized)
        return normalized

    validate_manifest = validate

    def persist(
        self,
        manifest: Mapping[str, Any],
        output_path: str | Path,
        *,
        slug: str | None = None,
    ) -> dict[str, Any]:
        """Validate and atomically persist ``manifest`` to ``output_path``."""

        normalized = self.validate(manifest, slug=slug)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_text(
            json.dumps(normalized, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
        return normalized

    write = persist

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        """Discover and persist the manifest for one video job.

        A missing sidecar is an explicit, non-error skip for non-instructional
        or legacy jobs.  The artifact records that absence so a downstream
        shot planner can fail closed when it sees an instructional beat.
        """

        slug = self._slug_from_job(job, ctx)
        explicit = self._explicit_from_job(job, ctx)
        root = self._root_from_context(ctx)
        discovered = self.discover(slug, manifest_root=root, explicit_input=explicit)
        output_path = ctx.job_dir / "technique_manifest.json"

        if discovered is None:
            missing = {
                "schema_version": MANIFEST_VERSION,
                "slug": slug,
                "style_preset": _DEFAULT_STYLE,
                "cast": copy.deepcopy(_DEFAULT_CAST),
                "rights": {
                    "permission": "internal",
                    "source": "none",
                    "reviewed": False,
                    "reviewed_by": None,
                    "reviewed_at": None,
                },
                "provenance": {"status": "missing", "source": None},
                "references": [],
                "states": [],
                "actions": [],
                "available": False,
            }
            self._atomic_write(output_path, missing)
            return StageOutput(
                {
                    "artifact_path": "technique_manifest.json",
                    "slug": slug,
                    "available": False,
                    "action_count": 0,
                    "reason": "no slug-matched technique visual sidecar",
                    "cost_usd": 0.0,
                }
            )

        raw, source = self._load_input(discovered)
        normalized = self.validate(raw, slug=slug)
        provenance = dict(normalized.get("provenance") or {})
        provenance.setdefault("status", "validated")
        provenance.setdefault("sidecar", self._display_path(source, ctx))
        normalized["provenance"] = provenance
        normalized["available"] = True
        self._atomic_write(output_path, normalized)
        return StageOutput(
            {
                "artifact_path": "technique_manifest.json",
                "slug": slug,
                "available": True,
                "action_count": len(normalized["actions"]),
                "reference_count": len(normalized["references"]),
                "source": provenance.get("sidecar"),
                "cost_usd": 0.0,
            }
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _validate_schema(self, manifest: Mapping[str, Any]) -> None:
        if not self.schema_path.exists():
            return
        schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        errors = sorted(
            Draft7Validator(schema).iter_errors(dict(manifest)),
            key=lambda error: list(error.absolute_path),
        )
        if errors:
            detail = [
                f"manifest {'.'.join(str(part) for part in error.absolute_path) or 'root'}: {error.message}"
                for error in errors
            ]
            raise TechniqueManifestValidationError(detail, slug=str(manifest.get("slug") or ""))

    @staticmethod
    def _has_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, tuple, dict, set)):
            return bool(value)
        return True

    @staticmethod
    def _action_prefix(candidate: Any, index: int) -> str:
        if isinstance(candidate, Mapping):
            identifier = candidate.get("id") or candidate.get("action_id") or candidate.get("name")
            if identifier:
                return f"action {str(identifier)!r}"
        return f"action {index!r}"

    @staticmethod
    def _coerce_path(value: Any, *, purpose: str) -> Path:
        try:
            path = Path(value)
        except TypeError as exc:
            raise TypeError(f"{purpose} must be a mapping or JSON path") from exc
        if not path.is_file():
            raise FileNotFoundError(f"{purpose} does not exist: {path}")
        return path

    @staticmethod
    def _is_slug_match(path: Path, slug: str) -> bool:
        normalized_slug = str(slug).casefold()
        stem = path.name.casefold()
        for suffix in (".technique.json", ".visual.json", ".manifest.json", ".json"):
            if stem == f"{normalized_slug}{suffix}":
                return True
        return False

    @staticmethod
    def _load_input(value: Path | Mapping[str, Any]) -> tuple[dict[str, Any], Path | None]:
        if isinstance(value, Path):
            try:
                loaded = json.loads(value.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise TechniqueManifestValidationError([f"sidecar is not valid JSON: {exc}"]) from exc
            if not isinstance(loaded, Mapping):
                raise TechniqueManifestValidationError(["sidecar JSON root must be an object"])
            return dict(loaded), value
        if isinstance(value, Mapping):
            return dict(value), None
        raise TypeError("technique manifest input must be a path or mapping")

    @staticmethod
    def _display_path(path: Path | None, ctx: StageContext) -> str | None:
        if path is None:
            return "explicit_input"
        try:
            return str(path.resolve().relative_to(ctx.job_dir.resolve().parents[1]))
        except (ValueError, OSError):
            return str(path)

    @staticmethod
    def _normalize_rights(value: Any, raw: Mapping[str, Any]) -> dict[str, Any]:
        candidate = dict(value) if isinstance(value, Mapping) else {}
        permission = (
            candidate.get("permission")
            or candidate.get("rights")
            or candidate.get("status")
            or candidate.get("owner")
            or candidate.get("license")
            or raw.get("permission")
            or raw.get("rights_status")
            or raw.get("owner")
        )
        normalized_permission = TechniqueManifestService._normalize_permission(permission)
        source = (
            candidate.get("source")
            or candidate.get("source_ref")
            or candidate.get("source_url")
            or candidate.get("provenance")
            or raw.get("source_ref")
            or raw.get("source_url")
            or raw.get("source")
        )
        reviewed = candidate.get("reviewed")
        if reviewed is None:
            reviewed = raw.get("reviewed")
        if reviewed is None:
            reviewed = (
                candidate.get("approved") is True
                or candidate.get("operator_approved") is True
                or candidate.get("review_status") in {"reviewed", "approved"}
                or raw.get("operator_approved") is True
                or raw.get("review_status") in {"reviewed", "approved"}
            )
        result = dict(candidate)
        result["permission"] = normalized_permission
        result["source"] = str(source).strip() if source is not None else ""
        result["reviewed"] = reviewed is True
        result.setdefault("reviewed_by", candidate.get("reviewer") or raw.get("reviewed_by"))
        result.setdefault("reviewed_at", candidate.get("reviewed_at") or raw.get("reviewed_at"))
        if "license" not in result:
            result["license"] = candidate.get("license_name") or raw.get("license")
        return result

    @staticmethod
    def _normalize_permission(value: Any) -> str | None:
        if value is None or isinstance(value, Mapping):
            return None
        text = str(value).strip().casefold().replace("_", "_")
        return _PERMISSION_ALIASES.get(text, text)

    @staticmethod
    def _validate_rights(rights: Mapping[str, Any]) -> list[str]:
        errors: list[str] = []
        permission = rights.get("permission")
        if permission not in _PERMISSIONS:
            errors.append(
                "manifest rights permission must be one of " + ", ".join(sorted(_PERMISSIONS))
            )
        if not TechniqueManifestService._has_value(rights.get("source")):
            errors.append("manifest rights source is required")
        # A rights declaration itself is review evidence.  Deterministic
        # internal assets still need an explicit operator review marker.
        if rights.get("reviewed") is not True:
            errors.append("manifest rights must be reviewed")
        return errors

    @staticmethod
    def _normalize_references(value: Any, rights: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        if isinstance(value, Mapping):
            value = [
                {"id": key, **dict(item)} if isinstance(item, Mapping) else {"id": key, "source": item}
                for key, item in value.items()
            ]
        elif not isinstance(value, list):
            value = []
        for index, item in enumerate(value):
            if not isinstance(item, Mapping):
                result[f"reference-{index + 1}"] = {"id": f"reference-{index + 1}", "source": "", "permission": None, "reviewed": False}
                continue
            ref = dict(item)
            ref_id = str(ref.get("id") or ref.get("reference_id") or f"reference-{index + 1}").strip()
            ref["id"] = ref_id
            ref["permission"] = TechniqueManifestService._normalize_permission(
                ref.get("permission") or ref.get("rights") or rights.get("permission")
            )
            ref["source"] = str(
                ref.get("source") or ref.get("source_ref") or ref.get("source_url") or ""
            ).strip()
            ref["reviewed"] = (
                ref.get("reviewed") is True
                or ref.get("approved") is True
                or ref.get("operator_approved") is True
                or ref.get("review_status") in {"reviewed", "approved"}
            )
            ref.setdefault("reviewed_by", ref.get("reviewer"))
            ref.setdefault("reviewed_at", ref.get("reviewed_at"))
            result[ref_id] = ref
        return result

    @staticmethod
    def _validate_references(references: Mapping[str, Mapping[str, Any]]) -> list[str]:
        errors: list[str] = []
        for ref_id, ref in references.items():
            if not TechniqueManifestService._has_value(ref.get("source")):
                errors.append(f"reference {ref_id!r}: source is required")
            if ref.get("permission") not in _PERMISSIONS:
                errors.append(f"reference {ref_id!r}: permission is not rights-cleared")
            if ref.get("reviewed") is not True:
                errors.append(f"reference {ref_id!r}: reviewed permission is required")
        return errors

    @staticmethod
    def _reference_is_cleared(reference: Mapping[str, Any]) -> bool:
        return (
            reference.get("permission") in _PERMISSIONS
            and TechniqueManifestService._has_value(reference.get("source"))
            and reference.get("reviewed") is True
        )

    @staticmethod
    def _normalize_states(value: Any) -> dict[str, dict[str, Any]]:
        if isinstance(value, Mapping):
            result: dict[str, dict[str, Any]] = {}
            for key, item in value.items():
                if isinstance(item, Mapping):
                    state = dict(item)
                else:
                    state = {"description": str(item)}
                state.setdefault("id", str(key))
                state["id"] = str(state["id"])
                state["reviewed"] = (
                    state.get("reviewed") is True
                    or state.get("approved") is True
                    or state.get("operator_approved") is True
                    or state.get("review_status") in {"reviewed", "approved"}
                )
                result[state["id"]] = state
            return result
        if isinstance(value, list):
            result = {}
            for index, item in enumerate(value):
                if not isinstance(item, Mapping):
                    continue
                state = dict(item)
                state_id = str(state.get("id") or state.get("state_id") or f"state-{index + 1}")
                state["id"] = state_id
                state["reviewed"] = (
                    state.get("reviewed") is True
                    or state.get("approved") is True
                    or state.get("operator_approved") is True
                    or state.get("review_status") in {"reviewed", "approved"}
                )
                result[state_id] = state
            return result
        return {}

    @staticmethod
    def _normalize_action(candidate: Mapping[str, Any]) -> dict[str, Any]:
        action = copy.deepcopy(dict(candidate))
        action["id"] = str(action.get("id") or action.get("action_id") or action.get("name") or "").strip()
        state_pair = action.get("states") if isinstance(action.get("states"), Mapping) else {}
        if not state_pair and isinstance(action.get("state"), Mapping):
            state_pair = action.get("state")
        state_from = (
            action.get("state_from")
            or action.get("from_state")
            or action.get("start_state")
            or state_pair.get("from")
            or ""
        )
        action["state_from"] = str(state_from).strip()
        action["action"] = str(
            action.get("action") or action.get("action_name") or ""
        ).strip()
        state_to = (
            action.get("state_to")
            or action.get("to_state")
            or action.get("end_state")
            or state_pair.get("to")
            or ""
        )
        action["state_to"] = str(state_to).strip()
        if not TechniqueManifestService._has_value(action.get("contact")):
            action["contact"] = copy.deepcopy(
                action.get("contact_anchor")
                or action.get("contact_anchors")
                or action.get("contacts")
            )
        if not TechniqueManifestService._has_value(action.get("motion_path")):
            path = action.get("path")
            motion = action.get("motion")
            if isinstance(motion, Mapping):
                path = path or motion.get("path") or motion.get("motion_path")
            elif isinstance(motion, str):
                path = path or motion
            action["motion_path"] = copy.deepcopy(path)
        if "reviewed" not in action:
            action["reviewed"] = (
                action.get("review_status") in {"reviewed", "approved"}
                or action.get("operator_reviewed") is True
                or action.get("operator_approved") is True
                or action.get("approved") is True
            )
        else:
            action["reviewed"] = action.get("reviewed") is True
        action["reference_refs"] = list(
            action.get("reference_refs")
            or action.get("references")
            or action.get("reference_ids")
            or []
        )
        action["overlays"] = list(action.get("overlays") or [])
        action["sound_cues"] = list(action.get("sound_cues") or [])
        if not isinstance(action.get("motion"), Mapping):
            action["motion"] = {"path": copy.deepcopy(action.get("motion_path")), "phases": []}
        else:
            action["motion"] = dict(action["motion"])
            action["motion"].setdefault("path", copy.deepcopy(action.get("motion_path")))
            action["motion"].setdefault("phases", [])
        action.setdefault("camera", {})
        return action

    @staticmethod
    def _normalize_cast(value: Any) -> dict[str, dict[str, Any]]:
        result = copy.deepcopy(_DEFAULT_CAST)
        if not isinstance(value, Mapping):
            return result
        for role in ("attacker", "defender"):
            candidate = value.get(role)
            if isinstance(candidate, str):
                result[role]["id"] = candidate
            elif isinstance(candidate, Mapping):
                result[role].update(copy.deepcopy(dict(candidate)))
                result[role].setdefault("id", role)
        # Preserve explicitly named additional cast roles (e.g. coach/cutaway)
        # while keeping attacker/defender deterministic defaults.
        for role, candidate in value.items():
            if role in result:
                continue
            if isinstance(candidate, Mapping):
                member = copy.deepcopy(dict(candidate))
                member.setdefault("id", str(role))
                result[str(role)] = member
        return result

    @staticmethod
    def _slug_from_job(job: VideoRun, ctx: StageContext) -> str:
        candidates: list[Any] = [
            job.input_payload.get("source_slug"),
            job.input_payload.get("slug"),
        ]
        bundle_path = ctx.job_dir / "source_bundle.json"
        if bundle_path.exists():
            try:
                bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
                candidates.append(bundle.get("slug"))
            except (OSError, json.JSONDecodeError):
                pass
        candidates.append(job.source_ref)
        for candidate in candidates:
            if candidate is None:
                continue
            text = str(candidate).strip().casefold()
            if not text:
                continue
            if "/" in text or "\\" in text:
                text = Path(text).stem
            elif text.endswith(".json"):
                text = Path(text).stem
            text = re.sub(r"\.(?:technique|visual|manifest)$", "", text)
            text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
            if text:
                return text
        raise ValueError("unable to determine technique slug for visual manifest")

    def _root_from_context(self, ctx: StageContext) -> Path | None:
        if self.manifest_root is not None:
            return self.manifest_root
        for key in (
            "technique_manifest_root",
            "technique_visual_manifest_root",
            "visual_manifest_root",
            "reference_manifest_root",
            "technique_visual_manifest_dir",
            "technique_manifest_dir",
            "reference_dir",
            "reference_root",
            "manifest_root",
        ):
            value = ctx.configs.get(key)
            if value:
                return Path(value)
        engine_root = ctx.configs.get("video_engine_root")
        if engine_root:
            return Path(engine_root) / "src" / "assets" / "references"
        return None

    @staticmethod
    def _explicit_from_job(job: VideoRun, ctx: StageContext) -> Any | None:
        for key in (
            "technique_manifest",
            "technique_manifest_path",
            "technique_visual_manifest",
            "technique_visual_manifest_path",
            "visual_manifest",
            "visual_manifest_path",
            "manifest",
            "manifest_path",
            "reference_manifest",
            "reference_manifest_path",
        ):
            if key in job.input_payload and job.input_payload[key] is not None:
                return job.input_payload[key]
        for key in (
            "technique_manifest",
            "technique_manifest_path",
            "technique_visual_manifest",
            "technique_visual_manifest_path",
            "visual_manifest",
            "visual_manifest_path",
            "manifest",
            "manifest_path",
        ):
            if key in ctx.configs and ctx.configs[key] is not None:
                return ctx.configs[key]
        return None

    @staticmethod
    def _atomic_write(path: Path, payload: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_text(
            json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)


def run_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    """Module-level adapter used by pipeline registries."""

    return TechniqueManifestService().run_stage(job, ctx)


# Descriptive aliases keep the service easy to discover for callers that use
# the domain term rather than the shorter module name.
TechniqueVisualManifestService = TechniqueManifestService
TechniqueManifestError = TechniqueManifestValidationError


def discover_manifest(
    slug: str,
    *,
    manifest_root: str | Path | None = None,
    explicit_input: Any | None = None,
) -> Path | dict[str, Any] | None:
    return TechniqueManifestService(manifest_root=manifest_root).discover(
        slug, explicit_input=explicit_input
    )


def validate_manifest(manifest: Mapping[str, Any], *, slug: str | None = None) -> dict[str, Any]:
    return TechniqueManifestService().validate(manifest, slug=slug)


__all__ = [
    "MANIFEST_VERSION",
    "TechniqueManifestService",
    "TechniqueVisualManifestService",
    "TechniqueManifestError",
    "TechniqueManifestValidationError",
    "discover_manifest",
    "validate_manifest",
    "run_stage",
]
