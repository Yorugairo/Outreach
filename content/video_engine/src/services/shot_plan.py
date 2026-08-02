"""Deterministic compilation of transcript beats and reviewed action recipes."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

from content.video_engine.src.models import StageContext, StageOutput, VideoRun


SHOT_PLAN_VERSION = "shot_plan.v1"
SHOT_PLAN_V2_VERSION = "shot_plan.v2"
INSTRUCTIONAL_FUNCTIONS = {
    "result_preview",
    "wide_setup",
    "contact_closeup",
    "mechanic_transition",
    "wrong_right_compare",
    "force_diagram",
    "result_hold",
}
SHOT_FUNCTIONS = INSTRUCTIONAL_FUNCTIONS | {"story_or_persona_cutaway"}
_VISUAL_DIAGRAM_TYPES = {
    "joint_leverage_diagram",
    "diagram",
    "force_diagram",
    "map_data_overlay",
    "chart_data",
    "timeline",
}
_VISUAL_TITLE_TYPES = {"title_card", "title"}
_DEFAULT_CAST = {
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
_DEFAULT_PHASES = ["anticipation", "action", "contact", "recovery"]


class ShotPlanValidationError(ValueError):
    """Raised when an instructional beat cannot resolve reviewed mechanics."""

    def __init__(self, errors: Iterable[str], *, slug: str | None = None):
        self.errors = list(errors)
        self.slug = slug
        super().__init__("; ".join(self.errors) or "invalid shot plan")


class ShotPlanService:
    """Compile a beat sheet into an immutable, renderer-facing shot plan."""

    def compile(
        self,
        beat_sheet: Mapping[str, Any] | list[Any] | str | Path,
        technique_manifest: Mapping[str, Any] | str | Path,
        *,
        source_slug: str | None = None,
        art_direction: Mapping[str, Any] | str | Path | None = None,
    ) -> dict[str, Any]:
        beats_payload = self._load_json_object(beat_sheet, "beat sheet")
        manifest = self._load_json_object(technique_manifest, "technique manifest")
        resolved_art_direction = (
            self._load_json_object(art_direction, "art direction")
            if art_direction is not None
            else None
        )
        slug = self._source_slug(beats_payload, manifest, source_slug)
        actions = self._action_map(manifest.get("actions"))
        references = self._reference_map(manifest.get("references"))
        cast = self._normalize_cast(manifest.get("cast"))
        style = str(manifest.get("style_preset") or manifest.get("style") or "flat_vector_bjj")
        beats = beats_payload.get("beats")
        errors: list[str] = []
        if not isinstance(beats, list) or not beats:
            raise ShotPlanValidationError(["beat sheet beats must be a non-empty array"], slug=slug)

        shots: list[dict[str, Any]] = []
        manifest_rights_errors = self._manifest_rights_errors(manifest)
        for beat_index, beat_candidate in enumerate(beats):
            if not isinstance(beat_candidate, Mapping):
                errors.append(f"beat {beat_index}: beat must be an object")
                continue
            beat = dict(beat_candidate)
            instructional = self._is_instructional(beat)
            action_id = self._action_id_for_beat(beat, beat_index, manifest, actions)
            action = actions.get(action_id) if action_id else None
            function = self._function_for_beat(beat, action, beat_index)
            if function not in SHOT_FUNCTIONS:
                errors.append(f"beat {beat_index}: unknown visual function {function!r}")
                function = "mechanic_transition" if instructional else "story_or_persona_cutaway"
            if function in INSTRUCTIONAL_FUNCTIONS and (
                instructional
                or str(beat.get("visual_type") or "").casefold()
                in {"bjj_action", "technique_action", "grappling_action"}
                or str(beat.get("manim_class") or "") == "BJJActionScene"
            ):
                instructional = True

            if instructional:
                errors.extend(
                    f"beat {beat_index}: {message}" for message in manifest_rights_errors
                )
                errors.extend(self._instructional_errors(beat_index, action_id, action, references))

            shot = self._build_shot(
                beat,
                beat_index=beat_index,
                slug=slug,
                style=style,
                cast=cast,
                function=function,
                action=action,
                action_id=action_id,
                references=references,
                instructional=instructional,
                manifest=manifest,
            )
            if resolved_art_direction is not None:
                shot["treatment_id"] = f"treatment-{shot['shot_id']}"
                if shot.get("manim_class") == "BJJActionScene":
                    shot["manim_class"] = "CombatScienceScene"
            shots.append(shot)

        if errors:
            raise ShotPlanValidationError(errors, slug=slug)

        manifest_provenance = copy.deepcopy(manifest.get("provenance") or {})
        top_provenance = {
            "manifest_schema_version": str(manifest.get("schema_version") or "unknown"),
            "manifest_slug": str(manifest.get("slug") or slug),
            "rights": copy.deepcopy(manifest.get("rights") or {}),
            **manifest_provenance,
        }
        payload = {
            "schema_version": (
                SHOT_PLAN_V2_VERSION
                if resolved_art_direction is not None
                else SHOT_PLAN_VERSION
            ),
            "source_slug": slug,
            "style_preset": style,
            "cast": cast,
            "provenance": top_provenance,
            "shots": shots,
        }
        if resolved_art_direction is not None:
            payload["art_direction_id"] = str(
                resolved_art_direction.get("art_bible_id")
                or resolved_art_direction.get("id")
                or ""
            )
            payload["art_bible_hash"] = str(
                resolved_art_direction.get("art_bible_hash") or ""
            )
        return payload

    build = compile
    plan = compile

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        beat_path = ctx.job_dir / "beat_sheet.json"
        manifest_path = ctx.job_dir / "technique_manifest.json"
        if not beat_path.exists():
            raise FileNotFoundError("beat_sheet.json is required before shot planning")
        if not manifest_path.exists():
            raise FileNotFoundError(
                "technique_manifest.json is required before instructional shot planning"
            )
        art_direction_path = ctx.job_dir / "art_direction.json"
        plan = self.compile(
            beat_path,
            manifest_path,
            art_direction=art_direction_path if art_direction_path.is_file() else None,
        )
        output_path = ctx.job_dir / "shot_plan.json"
        self._atomic_write(output_path, plan)
        return StageOutput(
            {
                "artifact_path": "shot_plan.json",
                "source_slug": plan["source_slug"],
                "shot_count": len(plan["shots"]),
                "instructional_shot_count": sum(
                    1
                    for shot in plan["shots"]
                    if shot.get("visual_type") == "bjj_action"
                    or shot.get("manim_class") == "BJJActionScene"
                ),
                "cost_usd": 0.0,
            }
        )

    # ------------------------------------------------------------------
    # Beat/action resolution
    # ------------------------------------------------------------------
    @staticmethod
    def _action_map(value: Any) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        if isinstance(value, Mapping):
            iterable = list(value.values())
        elif isinstance(value, list):
            iterable = value
        else:
            iterable = []
        for item in iterable:
            if not isinstance(item, Mapping):
                continue
            action = copy.deepcopy(dict(item))
            identifier = str(
                action.get("id") or action.get("action_id") or action.get("name") or action.get("action") or ""
            ).strip()
            if identifier:
                action["id"] = identifier
                state_pair = action.get("states") if isinstance(action.get("states"), Mapping) else {}
                if not state_pair and isinstance(action.get("state"), Mapping):
                    state_pair = action.get("state")
                action["state_from"] = str(
                    action.get("state_from")
                    or action.get("from_state")
                    or action.get("start_state")
                    or state_pair.get("from")
                    or ""
                ).strip()
                action["action"] = str(
                    action.get("action") or action.get("action_name") or ""
                ).strip()
                action["state_to"] = str(
                    action.get("state_to")
                    or action.get("to_state")
                    or action.get("end_state")
                    or state_pair.get("to")
                    or ""
                ).strip()
                if not ShotPlanService._has_value(action.get("contact")):
                    action["contact"] = copy.deepcopy(
                        action.get("contact_anchors") or action.get("contacts")
                    )
                if not ShotPlanService._has_value(action.get("motion_path")):
                    motion = action.get("motion")
                    path = action.get("path")
                    if isinstance(motion, Mapping):
                        path = path or motion.get("path") or motion.get("motion_path")
                    elif isinstance(motion, str):
                        path = path or motion
                    action["motion_path"] = copy.deepcopy(path)
                result[identifier] = action
        return result

    @staticmethod
    def _reference_map(value: Any) -> dict[str, dict[str, Any]]:
        if isinstance(value, Mapping):
            result = {
                str(key): copy.deepcopy(dict(item))
                for key, item in value.items()
                if isinstance(item, Mapping)
            }
        elif isinstance(value, list):
            result = {
                str(item.get("id") or item.get("reference_id")): copy.deepcopy(dict(item))
                for item in value
                if isinstance(item, Mapping) and (item.get("id") or item.get("reference_id"))
            }
        else:
            return {}
        for reference in result.values():
            permission = str(
                reference.get("permission")
                or reference.get("rights")
                or reference.get("rights_status")
                or ""
            ).strip().casefold().replace("-", "_").replace(" ", "_")
            if permission in {"operator", "owned", "operator_owned"}:
                permission = "operator_owned"
            elif permission == "public_domain":
                permission = "public_domain"
            reference["permission"] = permission
            reference["source"] = str(
                reference.get("source")
                or reference.get("source_ref")
                or reference.get("source_url")
                or ""
            ).strip()
            reference["reviewed"] = (
                reference.get("reviewed") is True
                or reference.get("approved") is True
                or reference.get("operator_approved") is True
                or reference.get("review_status") in {"reviewed", "approved"}
            )
        return result

    @staticmethod
    def _action_id_for_beat(
        beat: Mapping[str, Any],
        beat_index: int,
        manifest: Mapping[str, Any],
        actions: Mapping[str, Mapping[str, Any]],
    ) -> str | None:
        parameters = beat.get("parameters") if isinstance(beat.get("parameters"), Mapping) else {}
        candidates: list[Any] = [
            beat.get("action_id"),
            beat.get("action_ref"),
            beat.get("technique_action"),
            beat.get("action"),
            parameters.get("action_id"),
            parameters.get("action_ref"),
            parameters.get("technique_action"),
            parameters.get("action"),
        ]
        nested = beat.get("bjj_action") or parameters.get("bjj_action")
        if isinstance(nested, Mapping):
            candidates.extend([nested.get("id"), nested.get("action_id"), nested.get("action")])
        markers = beat.get("beats")
        if isinstance(markers, list):
            for marker in markers:
                if isinstance(marker, Mapping):
                    candidates.append(marker.get("action"))
        saw_explicit = False
        for candidate in candidates:
            if isinstance(candidate, Mapping):
                candidate = candidate.get("id") or candidate.get("action_id") or candidate.get("action")
            if candidate is None:
                continue
            text = str(candidate).strip()
            if text:
                saw_explicit = True
            text = re.sub(r"^(?:bjj_action|action|recipe):", "", text, flags=re.IGNORECASE)
            if text in actions:
                return text

        # An explicit but unknown action marker must never be replaced by a
        # positional guess.  This is the fail-closed boundary for instructional
        # rendering.
        if saw_explicit:
            return None

        # Explicit beat maps are preferred over positional guesses.  Both a
        # map keyed by integer and a map keyed by ``beat_<n>`` are accepted.
        beat_map = manifest.get("beat_actions") or manifest.get("beat_map")
        if isinstance(beat_map, Mapping):
            for key in (beat_index, str(beat_index), f"beat_{beat_index}", beat.get("id")):
                if key in beat_map:
                    mapped = str(beat_map[key])
                    mapped = re.sub(r"^(?:bjj_action|action|recipe):", "", mapped, flags=re.IGNORECASE)
                    if mapped in actions:
                        return mapped
        for identifier, action in actions.items():
            indices = action.get("beat_indices") or action.get("beat_indexes") or []
            if action.get("beat_index") == beat_index or beat_index in indices:
                return identifier
            beat_ids = action.get("beat_ids") or []
            if beat.get("id") in beat_ids or beat.get("beat_id") in beat_ids:
                return identifier
        # A one-action manifest is unambiguous even when a legacy beat omitted
        # the marker.  Multiple actions without a marker remain unresolved and
        # fail closed rather than guessing choreography.
        if len(actions) == 1:
            return next(iter(actions))
        return None

    @staticmethod
    def _is_instructional(beat: Mapping[str, Any]) -> bool:
        if beat.get("instructional") is False:
            return False
        if beat.get("instructional") is True:
            return True
        parameters = beat.get("parameters") if isinstance(beat.get("parameters"), Mapping) else {}
        if parameters.get("instructional") is True:
            return True
        visual_type = str(beat.get("visual_type") or "").casefold()
        manim_class = str(beat.get("manim_class") or "")
        if visual_type in {"bjj_action", "technique_action", "grappling_action"}:
            return True
        if manim_class == "BJJActionScene":
            return True
        values = [
            beat.get("action"),
            beat.get("action_id"),
            beat.get("action_ref"),
            beat.get("technique_action"),
            parameters.get("action_id"),
            parameters.get("action_ref"),
            parameters.get("technique_action"),
            parameters.get("action"),
            beat.get("bjj_action"),
            parameters.get("bjj_action"),
        ]
        return any(value is not None and value != "" for value in values)

    @staticmethod
    def _function_for_beat(
        beat: Mapping[str, Any],
        action: Mapping[str, Any] | None,
        beat_index: int,
    ) -> str:
        parameters = beat.get("parameters") if isinstance(beat.get("parameters"), Mapping) else {}
        raw = (
            beat.get("function")
            or beat.get("visual_function")
            or beat.get("shot")
            or parameters.get("function")
            or parameters.get("visual_function")
            or (action or {}).get("function")
        )
        if raw:
            return str(raw)
        visual_type = str(beat.get("visual_type") or "")
        if visual_type in _VISUAL_DIAGRAM_TYPES:
            return "force_diagram"
        if visual_type in _VISUAL_TITLE_TYPES:
            return "story_or_persona_cutaway"
        act = str(beat.get("act") or "").casefold()
        if act == "hook" or beat_index == 0:
            return "result_preview"
        if act == "conflict":
            return "wrong_right_compare"
        if act == "payoff":
            return "result_hold"
        if act == "cta":
            return "story_or_persona_cutaway"
        return "mechanic_transition"

    @staticmethod
    def _instructional_errors(
        beat_index: int,
        action_id: str | None,
        action: Mapping[str, Any] | None,
        references: Mapping[str, Mapping[str, Any]],
    ) -> list[str]:
        if action is None:
            return [f"beat {beat_index}: unresolved reviewed action{f' {action_id!r}' if action_id else ''}"]
        identifier = str(action.get("id") or action_id or beat_index)
        errors: list[str] = []
        for field in ("state_from", "action", "state_to", "contact", "motion_path"):
            value = action.get(field)
            if value is None or (isinstance(value, str) and not value.strip()) or (
                isinstance(value, (list, dict)) and not value
            ):
                errors.append(f"action {identifier!r}: missing {field}")
        if action.get("reviewed") is not True:
            errors.append(f"action {identifier!r}: reviewed action state is required")
        refs = list(action.get("reference_refs") or action.get("references") or [])
        for ref in refs:
            ref_id = str(ref)
            reference = references.get(ref_id)
            if reference is None:
                errors.append(f"action {identifier!r}: unresolved reference {ref_id!r}")
                continue
            if reference.get("permission") not in {
                "operator_owned",
                "licensed",
                "internal",
                "public_domain",
                "cc0",
            }:
                errors.append(f"action {identifier!r}: reference {ref_id!r} lacks permission")
            if reference.get("reviewed") is not True:
                errors.append(f"action {identifier!r}: reference {ref_id!r} is unreviewed")
        return errors

    @staticmethod
    def _manifest_rights_errors(manifest: Mapping[str, Any]) -> list[str]:
        rights = manifest.get("rights")
        if not isinstance(rights, Mapping):
            return ["manifest rights are required"]
        permission = str(
            rights.get("permission")
            or rights.get("rights")
            or rights.get("status")
            or rights.get("owner")
            or ""
        ).strip().casefold().replace("-", "_").replace(" ", "_")
        if permission in {"operator", "owned", "approved", "cleared"}:
            permission = "operator_owned"
        if permission not in {
            "operator_owned",
            "licensed",
            "internal",
            "public_domain",
            "cc0",
        }:
            return ["manifest rights permission is not rights-cleared"]
        source = rights.get("source") or rights.get("source_ref") or rights.get("source_url")
        if not source:
            return ["manifest rights source is required"]
        reviewed = (
            rights.get("reviewed") is True
            or rights.get("approved") is True
            or rights.get("operator_approved") is True
            or rights.get("review_status") in {"reviewed", "approved"}
        )
        if not reviewed:
            return ["manifest rights must be reviewed"]
        return []

    # ------------------------------------------------------------------
    # Shot shape and persistence
    # ------------------------------------------------------------------
    def _build_shot(
        self,
        beat: Mapping[str, Any],
        *,
        beat_index: int,
        slug: str,
        style: str,
        cast: Mapping[str, Any],
        function: str,
        action: Mapping[str, Any] | None,
        action_id: str | None,
        references: Mapping[str, Mapping[str, Any]],
        instructional: bool,
        manifest: Mapping[str, Any],
    ) -> dict[str, Any]:
        parameters = beat.get("parameters") if isinstance(beat.get("parameters"), Mapping) else {}
        recipe = action or {}
        shot_cast = recipe.get("cast") or beat.get("cast") or cast
        state_from = recipe.get("state_from") or beat.get("state_from")
        state_to = recipe.get("state_to") or beat.get("state_to")
        resolved_action = recipe.get("action") or beat.get("action") or action_id
        camera = self._camera_for(function, beat, recipe)
        motion = self._motion_for(function, beat, recipe, instructional)
        overlays = self._list_value(
            beat.get("overlays") or parameters.get("overlays") or recipe.get("overlays")
        )
        sound_cues = self._list_value(
            beat.get("sound_cues") or parameters.get("sound_cues") or recipe.get("sound_cues")
        )
        if instructional and not sound_cues:
            sound_cues = ["movement", "contact", "aftermath"]
        refs = self._dedupe(
            [
                *self._list_value(beat.get("reference_refs")),
                *self._list_value(parameters.get("reference_refs")),
                *self._list_value(recipe.get("reference_refs") or recipe.get("references")),
            ]
        )
        transition = self._transition_for(beat, recipe, function, action_id)
        reference_provenance = {
            "manifest_slug": str(manifest.get("slug") or slug),
            "manifest_schema_version": str(manifest.get("schema_version") or "unknown"),
            "reference_refs": refs,
            "rights": copy.deepcopy(manifest.get("rights") or {}),
        }
        action_source = str(
            recipe.get("action_source")
            or ("reviewed_reference" if refs else "deterministic_library")
        )
        return {
            "shot_id": f"{slug}-shot-{beat_index + 1:03d}",
            "beat_index": beat_index,
            "act": str(beat.get("act") or "develop"),
            "narration_text": str(beat.get("narration_text") or ""),
            "function": function,
            "visual_type": "bjj_action" if instructional else self._visual_type(beat, function),
            "style_preset": style,
            "cast": copy.deepcopy(dict(shot_cast)) if isinstance(shot_cast, Mapping) else copy.deepcopy(dict(cast)),
            "manim_class": "BJJActionScene" if instructional else str(beat.get("manim_class") or ""),
            "state_from": state_from,
            "action": resolved_action,
            "state_to": state_to,
            "contact": copy.deepcopy(recipe.get("contact") or beat.get("contact")),
            "camera": camera,
            "motion": motion,
            "overlays": overlays,
            "transition": transition,
            "sound_cues": sound_cues,
            "reference_refs": refs,
            "action_source": action_source,
            "provenance": reference_provenance,
        }

    @staticmethod
    def _visual_type(beat: Mapping[str, Any], function: str) -> str:
        if function == "force_diagram":
            return "diagram"
        value = str(beat.get("visual_type") or "")
        if value in _VISUAL_TITLE_TYPES:
            return "title_card"
        return value or "title_card"

    @staticmethod
    def _camera_for(
        function: str,
        beat: Mapping[str, Any],
        action: Mapping[str, Any],
    ) -> dict[str, Any]:
        candidate = beat.get("camera") or action.get("camera") or {}
        camera = dict(candidate) if isinstance(candidate, Mapping) else {}
        defaults = {
            "result_preview": {"framing": "wide", "move": "static", "focus": "result"},
            "wide_setup": {"framing": "wide", "move": "static", "focus": "cast"},
            "contact_closeup": {"framing": "grip_closeup", "move": "push_in", "focus": "contact"},
            "mechanic_transition": {"framing": "medium", "move": "track", "focus": "action"},
            "wrong_right_compare": {"framing": "split", "move": "static", "focus": "decisive_variable"},
            "force_diagram": {"framing": "medium", "move": "push_in", "focus": "leverage"},
            "result_hold": {"framing": "wide", "move": "static", "focus": "result"},
            "story_or_persona_cutaway": {"framing": "medium", "move": "static", "focus": "subject"},
        }.get(function, {"framing": "medium", "move": "static", "focus": "subject"})
        for key, value in defaults.items():
            camera.setdefault(key, value)
        return camera

    @staticmethod
    def _motion_for(
        function: str,
        beat: Mapping[str, Any],
        action: Mapping[str, Any],
        instructional: bool,
    ) -> dict[str, Any]:
        candidate = beat.get("motion") or action.get("motion") or {}
        motion = dict(candidate) if isinstance(candidate, Mapping) else {}
        path = motion.get("path") or motion.get("motion_path") or action.get("motion_path") or beat.get("motion_path")
        if not path:
            path = "none" if not instructional else {
                "wide_setup": "linear",
                "contact_closeup": "compression",
                "mechanic_transition": "arc",
                "wrong_right_compare": "pivot",
                "force_diagram": "linear",
                "result_preview": "release",
                "result_hold": "release",
            }.get(function, "linear")
        phases = motion.get("phases") or action.get("phases") or []
        phases = list(phases) if isinstance(phases, (list, tuple)) else [str(phases)]
        if instructional and not phases:
            phases = list(_DEFAULT_PHASES)
        motion["path"] = path
        motion["phases"] = phases
        return motion

    @staticmethod
    def _transition_for(
        beat: Mapping[str, Any],
        action: Mapping[str, Any],
        function: str,
        action_id: str | None,
    ) -> dict[str, Any]:
        candidate = beat.get("transition") or action.get("transition") or {}
        transition = dict(candidate) if isinstance(candidate, Mapping) else {}
        transition.setdefault("in", "continuous")
        transition.setdefault(
            "motif",
            f"action:{action_id}" if action_id and function in INSTRUCTIONAL_FUNCTIONS else None,
        )
        return transition

    @staticmethod
    def _list_value(value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value.strip() else []
        if isinstance(value, (list, tuple, set)):
            return [item for item in value if item is not None and str(item).strip()]
        return [value]

    @staticmethod
    def _has_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, tuple, set, dict)):
            return bool(value)
        return True

    @staticmethod
    def _dedupe(values: Iterable[Any]) -> list[Any]:
        result: list[Any] = []
        seen: set[str] = set()
        for value in values:
            key = str(value)
            if key in seen:
                continue
            seen.add(key)
            result.append(value)
        return result

    @staticmethod
    def _source_slug(
        beat_sheet: Mapping[str, Any],
        manifest: Mapping[str, Any],
        explicit: str | None,
    ) -> str:
        manifest_value = manifest.get("slug")
        beat_value = beat_sheet.get("source_slug") or beat_sheet.get("slug")
        if manifest_value and beat_value:
            manifest_slug = re.sub(r"[^a-z0-9]+", "-", str(manifest_value).casefold()).strip("-")
            beat_slug = re.sub(r"[^a-z0-9]+", "-", str(beat_value).casefold()).strip("-")
            if manifest_slug != beat_slug:
                raise ShotPlanValidationError(
                    [
                        "shot plan manifest slug "
                        f"{manifest_slug!r} does not match beat sheet slug {beat_slug!r}"
                    ]
                )
        if explicit and manifest_value:
            explicit_slug = re.sub(r"[^a-z0-9]+", "-", str(explicit).casefold()).strip("-")
            manifest_slug = re.sub(r"[^a-z0-9]+", "-", str(manifest_value).casefold()).strip("-")
            if explicit_slug != manifest_slug:
                raise ShotPlanValidationError(
                    [
                        "shot plan explicit slug "
                        f"{explicit_slug!r} does not match manifest slug {manifest_slug!r}"
                    ]
                )
        value = explicit or manifest_value or beat_value
        if not value:
            raise ShotPlanValidationError(["shot plan source slug is required"])
        text = str(value).strip().casefold()
        text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
        if not text:
            raise ShotPlanValidationError(["shot plan source slug is empty"])
        return text

    @staticmethod
    def _normalize_cast(value: Any) -> dict[str, Any]:
        cast = copy.deepcopy(_DEFAULT_CAST)
        if not isinstance(value, Mapping):
            return cast
        for role, member in value.items():
            if isinstance(member, str):
                cast[str(role)] = {"id": member}
            elif isinstance(member, Mapping):
                entry = copy.deepcopy(dict(member))
                entry.setdefault("id", str(role))
                cast[str(role)] = entry
        return cast

    @staticmethod
    def _load_json_object(
        value: Mapping[str, Any] | list[Any] | str | Path, label: str
    ) -> dict[str, Any]:
        if isinstance(value, Mapping):
            return copy.deepcopy(dict(value))
        if isinstance(value, list):
            if label == "beat sheet":
                return {"beats": copy.deepcopy(value)}
            raise ShotPlanValidationError([f"{label} JSON root must be an object"])
        path = Path(value)
        if not path.exists():
            raise FileNotFoundError(f"{label} does not exist: {path}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ShotPlanValidationError([f"{label} is not valid JSON: {exc}"]) from exc
        if not isinstance(payload, Mapping):
            raise ShotPlanValidationError([f"{label} JSON root must be an object"])
        return copy.deepcopy(dict(payload))

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
    """Module-level pipeline adapter."""

    return ShotPlanService().run_stage(job, ctx)


ShotPlanCompiler = ShotPlanService
DeterministicShotPlanner = ShotPlanService
ShotPlanError = ShotPlanValidationError


def compile_shot_plan(
    beat_sheet: Mapping[str, Any] | list[Any] | str | Path,
    technique_manifest: Mapping[str, Any] | str | Path,
    *,
    source_slug: str | None = None,
) -> dict[str, Any]:
    return ShotPlanService().compile(
        beat_sheet, technique_manifest, source_slug=source_slug
    )


__all__ = [
    "INSTRUCTIONAL_FUNCTIONS",
    "SHOT_FUNCTIONS",
    "SHOT_PLAN_VERSION",
    "ShotPlanService",
    "ShotPlanCompiler",
    "DeterministicShotPlanner",
    "ShotPlanError",
    "ShotPlanValidationError",
    "compile_shot_plan",
    "run_stage",
]
