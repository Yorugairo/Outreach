"""Deterministic v3 art-direction contracts.

The visual v3 boundary has two deliberately separate domains:

* ``reference_study.v1`` is a reviewed, abstract research note.  It is never
  a render input and may not contain media provenance.
* ``art_bible.v1`` and ``visual_treatment.v1`` are renderer-facing contracts
  made only from internal style atoms and reviewed shot-plan mechanics.

This module keeps those domains separate, validates every JSON boundary with
strict Draft 7 schemas, and supplies a stable canonical SHA-256 used by run
artifacts.  It performs no network or provider work.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft7Validator, FormatChecker

from content.video_engine.src.models import StageContext, StageOutput, VideoRun


REFERENCE_STUDY_VERSION = "reference_study.v1"
ART_BIBLE_VERSION = "art_bible.v1"
VISUAL_TREATMENT_VERSION = "visual_treatment.v1"
ART_DIRECTION_VERSION = "art_direction.v1"

DEFAULT_STUDY_ID = "reference-pack-abstract-v1"
DEFAULT_ART_BIBLE_ID = "combat-science-technical-cinematic-v1"

_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_HASH_RE = re.compile(r"^[a-f0-9]{64}$")
_BAD_TEXT = re.compile(
    r"(?:youtube(?:\.com|\.be|_?id)?|youtu\.be|watch\s*\?\s*v=|"
    r"in\s+the\s+style\s+of|style\s+of|imitat(?:e|ion|ing)|clone\s+the\s+style|"
    r"\bcreator(?:'s)?\b|"
    r"(?:^|[\\/])(?:stud(?:y|ies)|frames?|source)(?:[\\/]|$)|"
    r"\bsource[_ -]?frames?(?:[_ -]?\d+)?\b|\bframe[_ -]?\d+\b|"
    r"\.(?:mp4|mov|avi|mkv|png|jpe?g|webp)(?:$|[?#])|"
    r"(?:^|[\\/])frame[_-]?\d+\b)",
    re.IGNORECASE,
)
_BAD_KEYS = {
    "youtube",
    "youtube_id",
    "youtube_url",
    "source_frame",
    "source_frames",
    "source_frame_path",
    "study_path",
    "study_file",
    "renderable_source",
    "creator",
    "creator_name",
    "creator_id",
    "author",
    "author_name",
    "imitation_prompt",
    "renderer_prompt",
    "negative_prompt",
}
_HASH_KEYS = {"artifact_hash", "content_hash", "canonical_sha256", "sha256", "hash"}
_SHOT_FUNCTIONS = (
    "result_preview",
    "wide_setup",
    "contact_closeup",
    "mechanic_transition",
    "wrong_right_compare",
    "force_diagram",
    "result_hold",
    "story_or_persona_cutaway",
)
_DEFAULT_PHASES = ["anticipation", "action", "contact", "recovery"]


class ArtDirectionValidationError(ValueError):
    """Raised when an art-direction contract fails closed."""

    def __init__(
        self,
        errors: Iterable[str],
        *,
        contract: str | None = None,
    ) -> None:
        self.errors = list(errors)
        self.contract = contract
        label = f"invalid {contract}" if contract else "invalid art-direction contract"
        detail = "; ".join(self.errors) or label
        super().__init__(f"{label}: {detail}")


# Friendly aliases used by callers that prefer a domain-specific name.
ArtDirectionError = ArtDirectionValidationError
ArtBibleValidationError = ArtDirectionValidationError
ReferenceStudyValidationError = ArtDirectionValidationError
VisualTreatmentValidationError = ArtDirectionValidationError


def canonical_json(value: Any) -> str:
    """Return the stable JSON representation used for artifact hashes.

    A caller may pass an artifact that already carries ``artifact_hash`` (or
    one of the historical hash aliases); the top-level hash is excluded to
    avoid a circular digest and make retries idempotent.
    """

    if isinstance(value, Mapping):
        payload = dict(value)
        for key in _HASH_KEYS:
            payload.pop(key, None)
    else:
        payload = value
    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise TypeError(f"value is not canonical JSON: {exc}") from exc


def canonical_sha256(value: Any) -> str:
    """Return the stable SHA-256 digest of :func:`canonical_json`."""

    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    """Byte form for callers that feed canonical data directly to hashlib."""

    return canonical_json(value).encode("utf-8")


# Descriptive aliases make the helper easy to find from tests and CLI code.
stable_sha256 = canonical_sha256
canonical_hash = canonical_sha256
hash_canonical_json = canonical_sha256
sha256_json = canonical_sha256
stable_hash = canonical_sha256
artifact_hash = canonical_sha256


def _load_json(value: Any, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    if isinstance(value, (str, Path)):
        path = Path(value)
        if not path.is_file():
            raise FileNotFoundError(f"{label} does not exist: {path}")
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ArtDirectionValidationError([f"{label} is not valid JSON: {exc}"], contract=label) from exc
        if not isinstance(loaded, Mapping):
            raise ArtDirectionValidationError([f"{label} root must be an object"], contract=label)
        return copy.deepcopy(dict(loaded))
    raise TypeError(f"{label} must be a mapping or JSON path")


def _schema_path(name: str, explicit: str | Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit)
    return Path(__file__).resolve().parents[2] / "configs" / name


def _format_schema_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path) or "root"
    return f"schema {path}: {error.message}"


def _schema_errors(payload: Mapping[str, Any], path: Path) -> list[str]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"schema: unable to load {path}: {exc}"]
    errors = sorted(
        Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    return [_format_schema_error(error) for error in errors]


def _is_safe_id(value: Any) -> bool:
    return isinstance(value, str) and bool(_ID_RE.fullmatch(value))


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and bool(_HASH_RE.fullmatch(value))


def _provenance_errors(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    """Find source/provenance leakage before a renderer receives an artifact.

    The abstract study's ``prohibited_inputs`` list intentionally contains
    words such as ``source_frames``.  Those declarations are policy data, not
    source provenance, so known policy paths are exempt from the recursive
    key/value scan.
    """

    errors: list[str] = []
    # Lists recurse through an integer path component, so retain policy
    # context for values below ``prohibited_inputs``/``allowed_inputs``.
    policy_path = any(
        part in {"prohibited_inputs", "allowed_inputs", "allowed_asset_kinds"}
        for part in path
    )
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            lower = key.casefold().replace("-", "_")
            child_path = (*path, key)
            allowed_policy_key = (
                lower in {"renderable", "allow_external_assets", "allow_creator_imitation"}
                and path[-1:] == ("render_policy",)
            )
            if lower in _BAD_KEYS and not (policy_path and lower in {"source_frames", "source_video", "source_images"}):
                errors.append(f"{'.'.join(child_path)} is prohibited renderer provenance")
            if lower in {"source_path", "source_url", "media_path", "asset_path", "study_path"}:
                errors.append(f"{'.'.join(child_path)} is a source path and cannot be rendered")
            if lower == "renderable" and not allowed_policy_key:
                errors.append(f"{'.'.join(child_path)} may not mark a renderer artifact renderable")
            if lower == "allow_external_assets" and not allowed_policy_key:
                errors.append(f"{'.'.join(child_path)} may not enable external assets")
            if lower == "allow_creator_imitation" and not allowed_policy_key:
                errors.append(f"{'.'.join(child_path)} may not enable imitation")
            if lower == "allow_creator_imitation" and child is not False:
                errors.append("render_policy.allow_creator_imitation must be false")
            if lower == "allow_external_assets" and child is not False:
                errors.append("render_policy.allow_external_assets must be false")
            errors.extend(_provenance_errors(child, child_path))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            errors.extend(_provenance_errors(child, (*path, str(index))))
    elif isinstance(value, str) and not policy_path:
        text = value.strip()
        if _BAD_TEXT.search(text):
            errors.append(f"{'.'.join(path) or 'value'} contains prohibited source or imitation language")
        # Paths are not renderer inputs even when an extension is omitted.
        if ("\\" in text or ("/" in text and not text.startswith("#"))) and any(
            token in text.casefold() for token in ("study", "frame", "source", "artifact", "runtime")
        ):
            errors.append(f"{'.'.join(path) or 'value'} appears to be a source/study path")
    return errors


def _with_hash(payload: Mapping[str, Any], *, contract: str) -> dict[str, Any]:
    result = copy.deepcopy(dict(payload))
    provided = result.get("artifact_hash")
    expected = canonical_sha256(result)
    if provided is not None and provided != expected:
        raise ArtDirectionValidationError(
            [f"artifact_hash {provided!r} does not match canonical SHA-256 {expected}"],
            contract=contract,
        )
    result["artifact_hash"] = expected
    return result


def _validate_payload(
    payload: Mapping[str, Any],
    *,
    schema: str,
    contract: str,
) -> dict[str, Any]:
    errors = _provenance_errors(payload)
    errors.extend(_schema_errors(payload, _schema_path(schema)))
    if errors:
        raise ArtDirectionValidationError(errors, contract=contract)
    return _with_hash(payload, contract=contract)


class ArtDirectionService:
    """Load and resolve the curated study and the internal art bible."""

    def __init__(
        self,
        configs_root: str | Path | None = None,
        *,
        study_path: str | Path | None = None,
        art_bible_path: str | Path | None = None,
        study_schema_path: str | Path | None = None,
        art_bible_schema_path: str | Path | None = None,
    ) -> None:
        self.configs_root = (
            Path(configs_root)
            if configs_root is not None
            else Path(__file__).resolve().parents[2] / "configs"
        )
        self.study_path = Path(study_path) if study_path is not None else None
        self.art_bible_path = Path(art_bible_path) if art_bible_path is not None else None
        self.study_schema_path = (
            Path(study_schema_path)
            if study_schema_path is not None
            else self.configs_root / "reference_study.schema.json"
        )
        self.art_bible_schema_path = (
            Path(art_bible_schema_path)
            if art_bible_schema_path is not None
            else self.configs_root / "art_bible.schema.json"
        )

    # ---- strict contract validators ---------------------------------
    def validate_reference_study(
        self,
        value: Mapping[str, Any] | str | Path,
    ) -> dict[str, Any]:
        payload = _load_json(value, "reference study")
        if payload.get("schema_version") != REFERENCE_STUDY_VERSION:
            # The schema also reports this, but the explicit message is useful
            # when a caller passes a legacy study contract.
            payload.setdefault("schema_version", payload.get("version"))
        return self._validate_reference_study_payload(payload)

    def _validate_reference_study_payload(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._validate_with_schema_path(
            payload,
            schema_path=self.study_schema_path,
            contract=REFERENCE_STUDY_VERSION,
        )

    def validate_art_bible(
        self,
        value: Mapping[str, Any] | str | Path,
        *,
        study: Mapping[str, Any] | str | Path | None = None,
    ) -> dict[str, Any]:
        payload = _load_json(value, "art bible")
        if study is None and isinstance(payload.get("study_ref"), Mapping):
            # The curated bible intentionally stores only the study identity;
            # fill its deterministic digest from the curated study when a
            # caller validates the bible directly.
            if not payload["study_ref"].get("hash"):
                study = self.load_reference_study()
        if study is not None:
            study_payload = self.validate_reference_study(study)
            study_ref = payload.get("study_ref")
            if isinstance(study_ref, Mapping):
                payload.setdefault("study_ref", {})
                if not study_ref.get("hash"):
                    payload["study_ref"] = dict(study_ref)
                    payload["study_ref"]["hash"] = study_payload["artifact_hash"]
                elif study_ref.get("hash") != study_payload["artifact_hash"]:
                    raise ArtDirectionValidationError(
                        ["art_bible.study_ref.hash does not match the reference study"],
                        contract=ART_BIBLE_VERSION,
                    )
        return self._validate_art_bible_payload(payload)

    def _validate_art_bible_payload(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._validate_with_schema_path(
            payload,
            schema_path=self.art_bible_schema_path,
            contract=ART_BIBLE_VERSION,
        )

    def validate_visual_treatment(
        self,
        value: Mapping[str, Any] | str | Path,
        *,
        art_bible: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = _load_json(value, "visual treatment")
        result = self._validate_with_schema_path(
            payload,
            schema_path=self.configs_root / "visual_treatment.schema.json",
            contract=VISUAL_TREATMENT_VERSION,
        )
        if art_bible is None and result.get("art_bible_id") == DEFAULT_ART_BIBLE_ID:
            art_bible = self.load_art_bible()
        if art_bible is not None:
            bible = self.validate_art_bible(art_bible)
            atom_ids = {
                str(atom.get("id"))
                for atom in bible.get("style_atoms", [])
                if isinstance(atom, Mapping)
            }
            functions = set((bible.get("composition") or {}).get("functions") or {})
            errors: list[str] = []
            if result.get("art_bible_id") != bible.get("id"):
                errors.append("visual treatment art_bible_id does not match art bible")
            if result.get("art_bible_hash") != bible.get("artifact_hash"):
                errors.append("visual treatment art_bible_hash does not match art bible")
            for index, shot in enumerate(result.get("shots") or []):
                unknown = sorted(set(shot.get("style_atom_ids") or []) - atom_ids)
                if unknown:
                    errors.append(f"shots[{index}] references unknown style atoms {unknown!r}")
                if shot.get("function") not in functions:
                    errors.append(f"shots[{index}] function {shot.get('function')!r} is not in art bible")
            if errors:
                raise ArtDirectionValidationError(errors, contract=VISUAL_TREATMENT_VERSION)
        return result

    def _validate_with_schema_path(
        self,
        payload: Mapping[str, Any],
        *,
        schema_path: Path,
        contract: str,
    ) -> dict[str, Any]:
        errors = _provenance_errors(payload)
        errors.extend(_schema_errors(payload, schema_path))
        if errors:
            raise ArtDirectionValidationError(errors, contract=contract)
        return _with_hash(payload, contract=contract)

    # Common aliases used by task/CLI callers.
    validate_study = validate_reference_study
    validate_art_bible_file = validate_art_bible
    validate_treatment = validate_visual_treatment

    def check_reference_study(self, value: Mapping[str, Any] | str | Path) -> list[str]:
        return self._check(value, self.validate_reference_study)

    def check_art_bible(self, value: Mapping[str, Any] | str | Path) -> list[str]:
        return self._check(value, self.validate_art_bible)

    def check_visual_treatment(self, value: Mapping[str, Any] | str | Path) -> list[str]:
        return self._check(value, self.validate_visual_treatment)

    @staticmethod
    def hash_artifact(value: Any) -> str:
        """Hash a contract without including its existing top-level digest."""

        return canonical_sha256(value)

    canonical_sha256 = staticmethod(canonical_sha256)
    stable_hash = staticmethod(canonical_sha256)

    @staticmethod
    def _check(value: Any, validator: Any) -> list[str]:
        try:
            validator(value)
        except ArtDirectionValidationError as exc:
            return list(exc.errors)
        return []

    # ---- loading and resolution -------------------------------------
    def load_reference_study(
        self,
        value: Mapping[str, Any] | str | Path | None = None,
    ) -> dict[str, Any]:
        path = Path(value) if isinstance(value, (str, Path)) else value
        if path is None and self.study_path is not None:
            path = self.study_path
        if path is None:
            path = self.configs_root / "studies" / f"{DEFAULT_STUDY_ID}.json"
        return self.validate_reference_study(path if not isinstance(path, Mapping) else path)

    load_study = load_reference_study

    def load_art_bible(
        self,
        value: Mapping[str, Any] | str | Path | None = None,
        *,
        study: Mapping[str, Any] | str | Path | None = None,
    ) -> dict[str, Any]:
        path = Path(value) if isinstance(value, (str, Path)) else value
        if path is None and self.art_bible_path is not None:
            path = self.art_bible_path
        if path is None:
            path = self.configs_root / "art_bibles" / f"{DEFAULT_ART_BIBLE_ID}.json"
        study_payload = self.load_reference_study(study)
        return self.validate_art_bible(path if not isinstance(path, Mapping) else path, study=study_payload)

    load_bible = load_art_bible

    def resolve(
        self,
        *,
        study: Mapping[str, Any] | str | Path | None = None,
        art_bible: Mapping[str, Any] | str | Path | None = None,
    ) -> dict[str, Any]:
        study_payload = self.load_reference_study(study)
        bible_payload = self.load_art_bible(art_bible, study=study_payload)
        # The resolved artifact deliberately carries no study body/path.  It
        # contains only the study's stable identity and the internal atoms the
        # renderer needs.
        resolved: dict[str, Any] = {
            "schema_version": ART_DIRECTION_VERSION,
            "reference_study": {
                "id": study_payload["id"],
                "hash": study_payload["artifact_hash"],
            },
            "reference_study_id": study_payload["id"],
            "reference_study_hash": study_payload["artifact_hash"],
            "art_bible": copy.deepcopy(bible_payload),
            "id": bible_payload["id"],
            "art_bible_id": bible_payload["id"],
            "art_bible_hash": bible_payload["artifact_hash"],
            "style_atoms": copy.deepcopy(bible_payload["style_atoms"]),
            "palette": copy.deepcopy(bible_payload["palette"]),
            "typography": copy.deepcopy(bible_payload["typography"]),
            "composition": copy.deepcopy(bible_payload["composition"]),
            "motion": copy.deepcopy(bible_payload["motion"]),
            "render_policy": copy.deepcopy(bible_payload["render_policy"]),
        }
        resolved["artifact_hash"] = canonical_sha256(resolved)
        _prohibited = _provenance_errors(resolved)
        if _prohibited:
            raise ArtDirectionValidationError(_prohibited, contract=ART_DIRECTION_VERSION)
        return resolved

    def resolve_art_direction(
        self,
        *,
        study: Mapping[str, Any] | str | Path | None = None,
        art_bible: Mapping[str, Any] | str | Path | None = None,
        study_path: Mapping[str, Any] | str | Path | None = None,
        art_bible_path: Mapping[str, Any] | str | Path | None = None,
    ) -> dict[str, Any]:
        return self.resolve(
            study=study if study is not None else study_path,
            art_bible=art_bible if art_bible is not None else art_bible_path,
        )

    resolve_direction = resolve_art_direction

    def compile_visual_treatment(
        self,
        shot_plan: Mapping[str, Any] | str | Path,
        art_direction: Mapping[str, Any] | str | Path | None = None,
    ) -> dict[str, Any]:
        """Convenience bridge for callers that keep one direction service."""

        return VisualTreatmentService(self).compile(shot_plan, art_direction)

    compile_treatment = compile_visual_treatment

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        config = ctx.configs.get("art_direction")
        config_map = dict(config) if isinstance(config, Mapping) else {}
        payload = job.input_payload if isinstance(job.input_payload, Mapping) else {}
        study = (
            config_map.get("study")
            or config_map.get("study_path")
            or ctx.configs.get("reference_study_path")
            or ctx.configs.get("study_path")
            or payload.get("reference_study")
            or payload.get("study_path")
        )
        art_bible = (
            config_map.get("art_bible")
            or config_map.get("art_bible_path")
            or ctx.configs.get("art_bible_path")
            or payload.get("art_bible")
            or payload.get("art_bible_path")
        )
        direction = self.resolve(study=study, art_bible=art_bible)
        output_path = ctx.job_dir / "art_direction.json"
        _atomic_write(output_path, direction)
        return StageOutput(
            {
                "artifact_path": "art_direction.json",
                "schema_version": ART_DIRECTION_VERSION,
                "reference_study_id": direction["reference_study"]["id"],
                "reference_study_hash": direction["reference_study"]["hash"],
                "art_bible_id": direction["art_bible_id"],
                "art_bible_hash": direction["art_bible_hash"],
                "style_atom_count": len(direction["style_atoms"]),
                "cost_usd": 0.0,
            }
        )


class VisualTreatmentService:
    """Compile a shot plan into deterministic internal style treatments."""

    def __init__(
        self,
        art_direction: ArtDirectionService | None = None,
        *,
        configs_root: str | Path | None = None,
    ) -> None:
        self.art_direction = art_direction or ArtDirectionService(configs_root)
        self.configs_root = self.art_direction.configs_root

    def compile(
        self,
        shot_plan: Mapping[str, Any] | str | Path,
        art_direction: Mapping[str, Any] | str | Path | None = None,
    ) -> dict[str, Any]:
        plan = _load_json(shot_plan, "shot plan")
        direction = (
            _load_json(art_direction, "art direction")
            if art_direction is not None
            else self.art_direction.resolve()
        )
        if direction.get("schema_version") == ART_DIRECTION_VERSION:
            resolved = direction
            bible = _load_json(direction.get("art_bible"), "art bible") if isinstance(direction.get("art_bible"), (str, Path)) else dict(direction.get("art_bible") or direction)
            bible = self.art_direction.validate_art_bible(bible)
        else:
            bible = self.art_direction.validate_art_bible(direction)
            resolved = self.art_direction.resolve(art_bible=bible)
        atom_map = {
            str(atom["id"]): atom
            for atom in bible.get("style_atoms", [])
            if isinstance(atom, Mapping) and atom.get("id")
        }
        functions = (bible.get("composition") or {}).get("functions") or {}
        if not isinstance(plan.get("shots"), list) or not plan["shots"]:
            raise ArtDirectionValidationError(["shot plan shots must be a non-empty array"], contract="shot_plan")
        shots: list[dict[str, Any]] = []
        errors: list[str] = []
        living_mechanic_assigned = False
        for index, candidate in enumerate(plan["shots"]):
            if not isinstance(candidate, Mapping):
                errors.append(f"shots[{index}] must be an object")
                continue
            shot = dict(candidate)
            function = str(
                shot.get("function")
                or shot.get("visual_function")
                or shot.get("shot_function")
                or shot.get("visual_type")
                or "story_or_persona_cutaway"
            )
            if function not in _SHOT_FUNCTIONS:
                errors.append(f"shots[{index}] unknown visual function {function!r}")
                continue
            rule = functions.get(function) if isinstance(functions, Mapping) else None
            rule = rule if isinstance(rule, Mapping) else {}
            requested_atoms = shot.get("style_atom_ids") or shot.get("atom_ids") or rule.get("atom_ids")
            atom_ids = [str(atom) for atom in requested_atoms] if isinstance(requested_atoms, Sequence) and not isinstance(requested_atoms, (str, bytes)) else []
            if not atom_ids:
                atom_ids = [str(atom) for atom in rule.get("atom_ids") or []]
            unknown_atoms = sorted(set(atom_ids) - set(atom_map))
            if unknown_atoms:
                errors.append(f"shots[{index}] references unknown style atoms {unknown_atoms!r}")
                continue
            camera_raw = shot.get("camera") if isinstance(shot.get("camera"), Mapping) else {}
            camera = {
                "framing": str(camera_raw.get("framing") or camera_raw.get("shot") or rule.get("framing") or "wide_context"),
                "anchor": str(camera_raw.get("anchor") or camera_raw.get("focus") or "center"),
                "move": str(camera_raw.get("move") or "hold"),
                "safe_zone": str(camera_raw.get("safe_zone") or "center"),
            }
            motion_raw = shot.get("motion") if isinstance(shot.get("motion"), Mapping) else {}
            phase_values = motion_raw.get("phases") or shot.get("phases") or _DEFAULT_PHASES
            phases = [str(value) for value in phase_values] if isinstance(phase_values, Sequence) and not isinstance(phase_values, (str, bytes)) else list(_DEFAULT_PHASES)
            allowed_phases = {"anticipation", "action", "contact", "recovery", "hold"}
            phases = [phase for phase in phases if phase in allowed_phases] or list(_DEFAULT_PHASES)
            transition = str(
                motion_raw.get("transition")
                or shot.get("transition_motif")
                or (
                    (shot.get("transition") or {}).get("motif")
                    if isinstance(shot.get("transition"), Mapping)
                    else shot.get("transition")
                )
                or "arc_match"
            )
            shot_id = str(shot.get("shot_id") or shot.get("scene_id") or index + 1)
            composition = {
                "result_preview": "result_hero",
                "wide_setup": "wide_spatial_setup",
                "contact_closeup": "contact_macro_context_inset",
                "mechanic_transition": "mechanic_transition",
                "wrong_right_compare": "wrong_right_matched_split",
                "force_diagram": "living_geometry_reveal",
                "result_hold": "held_recognition_frame",
                "story_or_persona_cutaway": "cta_card",
            }[function]
            living_diagram = function == "force_diagram"
            if (
                function == "mechanic_transition"
                and str(shot.get("action") or "") == "hip_angle_and_leg_swing"
                and not living_mechanic_assigned
            ):
                composition = "living_geometry_reveal"
                living_diagram = True
                living_mechanic_assigned = True
            signature = "|".join(
                [
                    composition,
                    function,
                    camera["framing"],
                    camera["anchor"],
                    str(shot.get("state_from") or ""),
                    str(shot.get("action") or ""),
                    str(shot.get("state_to") or ""),
                    *[str(value) for value in (shot.get("overlays") or [])],
                ]
            )
            entry: dict[str, Any] = {
                "shot_id": shot_id,
                "treatment_id": str(
                    shot.get("treatment_id") or f"treatment-shot-{index + 1:03d}"
                ),
                "function": function,
                "purpose": str(
                    rule.get("emphasis")
                    or f"Answer the {function.replace('_', ' ')} visual question"
                ),
                "composition": composition,
                "rig": (
                    "graphic-card-v1"
                    if function == "story_or_persona_cutaway"
                    else "filled-cutout-v3"
                ),
                "style_atom_ids": atom_ids,
                "palette_roles": self._palette_roles(atom_ids, atom_map, bible.get("palette") or {}),
                "camera": camera,
                "depth": {"attacker": 20, "defender": 10, "overlay": 120},
                "motion": {
                    "phases": phases,
                    "transition": transition,
                    "easing": str(motion_raw.get("easing") or "ease_in_out"),
                },
                "overlays": [str(value) for value in (shot.get("overlays") or []) if str(value).strip()],
                "typography": {
                    "caption_font": "Inter",
                    "measurement_font": "Roboto Mono",
                },
                "signature": signature,
                "uniqueness_signature": signature,
                "living_diagram": living_diagram,
            }
            for field in ("state_from", "action", "state_to", "duration_s"):
                if shot.get(field) is not None:
                    entry[field] = copy.deepcopy(shot[field])
            shots.append(entry)
        if errors:
            raise ArtDirectionValidationError(errors, contract=VISUAL_TREATMENT_VERSION)
        treatment = {
            "schema_version": VISUAL_TREATMENT_VERSION,
            "art_bible_id": bible["id"],
            "art_bible_hash": bible["artifact_hash"],
            "shot_plan_hash": canonical_sha256(plan),
            "shots": shots,
        }
        return self.art_direction.validate_visual_treatment(treatment, art_bible=bible)

    build = compile
    compile_treatment = compile

    @staticmethod
    def _palette_roles(
        atom_ids: Sequence[str],
        atom_map: Mapping[str, Mapping[str, Any]],
        palette: Mapping[str, Any],
    ) -> list[str]:
        roles: list[str] = []
        for atom_id in atom_ids:
            tokens = atom_map.get(atom_id, {}).get("tokens") or {}
            for value in tokens.values():
                if isinstance(value, str) and value in palette and value not in roles:
                    roles.append(value)
        return roles or ([next(iter(palette))] if palette else ["ink"])

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        shot_plan_path = ctx.job_dir / "shot_plan.json"
        if not shot_plan_path.is_file():
            raise FileNotFoundError("shot_plan.json is required before visual treatment compilation")
        direction_path = ctx.job_dir / "art_direction.json"
        direction: Mapping[str, Any] | str | Path | None = direction_path if direction_path.is_file() else None
        if direction is None:
            config = ctx.configs.get("art_direction")
            if isinstance(config, Mapping):
                direction = config.get("art_bible") or config.get("art_bible_path")
        if direction is None:
            direction = ctx.configs.get("art_bible_path") or ctx.configs.get("art_bible")
        treatment = self.compile(shot_plan_path, direction)
        output_path = ctx.job_dir / "visual_treatment.json"
        _atomic_write(output_path, treatment)
        return StageOutput(
            {
                "artifact_path": "visual_treatment.json",
                "schema_version": VISUAL_TREATMENT_VERSION,
                "art_bible_id": treatment["art_bible_id"],
                "art_bible_hash": treatment["art_bible_hash"],
                "shot_plan_hash": treatment["shot_plan_hash"],
                "shot_count": len(treatment["shots"]),
                "cost_usd": 0.0,
            }
        )


# Explicit names are useful to small command adapters while retaining one
# resolver implementation and one immutable source of truth.
ReferenceStudyService = ArtDirectionService
ArtBibleService = ArtDirectionService


def _atomic_write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ArtDirectionValidationError(
                [f"existing immutable artifact is unreadable: {path}: {exc}"],
                contract="artifact_immutability",
            ) from exc
        if canonical_sha256(existing) != canonical_sha256(payload):
            raise ArtDirectionValidationError(
                [f"immutable artifact differs from existing {path}"],
                contract="artifact_immutability",
            )
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def validate_reference_study(
    value: Mapping[str, Any] | str | Path,
    *,
    schema_path: str | Path | None = None,
) -> dict[str, Any]:
    return ArtDirectionService(study_schema_path=schema_path).validate_reference_study(value)


def validate_art_bible(
    value: Mapping[str, Any] | str | Path,
    *,
    study: Mapping[str, Any] | str | Path | None = None,
    schema_path: str | Path | None = None,
) -> dict[str, Any]:
    return ArtDirectionService(art_bible_schema_path=schema_path).validate_art_bible(value, study=study)


def validate_visual_treatment(
    value: Mapping[str, Any] | str | Path,
    *,
    art_bible: Mapping[str, Any] | None = None,
    schema_path: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(schema_path).parent if schema_path is not None else None
    return ArtDirectionService(configs_root=root).validate_visual_treatment(value, art_bible=art_bible)


def check_reference_study(value: Mapping[str, Any] | str | Path) -> list[str]:
    """Return validation errors for CLI/reporting callers (never raise)."""

    return ArtDirectionService().check_reference_study(value)


def check_art_bible(value: Mapping[str, Any] | str | Path) -> list[str]:
    """Return validation errors for CLI/reporting callers (never raise)."""

    return ArtDirectionService().check_art_bible(value)


def check_visual_treatment(value: Mapping[str, Any] | str | Path) -> list[str]:
    """Return validation errors for CLI/reporting callers (never raise)."""

    return ArtDirectionService().check_visual_treatment(value)


validate_study = validate_reference_study
validate_art_bible_file = validate_art_bible
validate_treatment = validate_visual_treatment


def run_art_direction_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    return ArtDirectionService().run_stage(job, ctx)


def run_visual_treatment_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    return VisualTreatmentService().run_stage(job, ctx)


# A module-level ``run_stage`` is intentionally the art-direction stage
# adapter, matching the existing service modules.  The treatment adapter has
# an explicit name to avoid an ambiguous registry entry.
run_stage = run_art_direction_stage


__all__ = [
    "REFERENCE_STUDY_VERSION",
    "ART_BIBLE_VERSION",
    "VISUAL_TREATMENT_VERSION",
    "ART_DIRECTION_VERSION",
    "DEFAULT_STUDY_ID",
    "DEFAULT_ART_BIBLE_ID",
    "ArtDirectionValidationError",
    "ArtDirectionError",
    "ArtBibleValidationError",
    "ReferenceStudyValidationError",
    "VisualTreatmentValidationError",
    "canonical_json",
    "canonical_json_bytes",
    "canonical_sha256",
    "stable_sha256",
    "canonical_hash",
    "hash_canonical_json",
    "sha256_json",
    "stable_hash",
    "artifact_hash",
    "ArtDirectionService",
    "ReferenceStudyService",
    "ArtBibleService",
    "VisualTreatmentService",
    "validate_reference_study",
    "validate_study",
    "validate_art_bible",
    "validate_art_bible_file",
    "validate_visual_treatment",
    "validate_treatment",
    "check_reference_study",
    "check_art_bible",
    "check_visual_treatment",
    "run_art_direction_stage",
    "run_visual_treatment_stage",
    "run_stage",
]
