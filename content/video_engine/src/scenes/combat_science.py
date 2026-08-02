"""Original Combat Science composition grammar.

This module is the V3 scene-facing vocabulary around :mod:`bjj_action`.
Instructional geometry is still resolved from the reviewed Armbar cast and
its contact anchors; composition helpers only choose a camera question and
add explanatory overlays.  The helpers are intentionally usable without
Manim so storyboard/QC tests can inspect deterministic contracts on a clean
operator machine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .base import Arrow, Circle, FadeIn, Line, Text, ThemedScene, VGroup, color_value
from .bjj_action import (
    ARM_BAR_ACTION_CHAIN,
    BJJActionScene,
    BJJCast,
    CONTACT_ANCHOR_ALIASES,
    ContactAnchor,
    PHASE_NAMES,
    STATE_ALIASES,
    STATE_POSES,
    _safe_move_to,
    _safe_set_z_index,
    build_bjj_cast,
)


Point = tuple[float, float, float]


COMPOSITION_FUNCTION_NAMES: tuple[str, ...] = (
    "result_preview",
    "wide_setup",
    "contact_closeup",
    "mechanic_transition",
    "wrong_right_compare",
    "force_diagram",
    "result_hold",
    "story_or_persona_cutaway",
)

# The V3 cast deliberately reuses the reviewed mechanics library; aliases
# make that ownership explicit to callers without creating a second source of
# truth for joint positions.
CombatScienceCast = BJJCast
build_combat_science_cast = build_bjj_cast

# Alias names used by shot-plan and style-board callers.
COMPOSITION_NAMES = COMPOSITION_FUNCTION_NAMES
SHOT_FUNCTION_NAMES = COMPOSITION_FUNCTION_NAMES


@dataclass(frozen=True, slots=True)
class CompositionSpec:
    """Stable explanation contract for one shot function."""

    function: str
    viewer_question: str
    framing: str
    focus: str
    anchors: tuple[str, ...]
    state_from: str
    action: str
    state_to: str
    overlays: tuple[str, ...] = ()
    transition: str = "cut"

    @property
    def name(self) -> str:
        return self.function

    @property
    def contact_anchors(self) -> tuple[str, ...]:
        return self.anchors

    def to_dict(self) -> dict[str, Any]:
        return {
            "function": self.function,
            "viewer_question": self.viewer_question,
            "camera": {
                "framing": self.framing,
                "focus": self.focus,
                "transition": self.transition,
            },
            "anchors": list(self.anchors),
            "state_from": self.state_from,
            "action": self.action,
            "state_to": self.state_to,
            "overlays": list(self.overlays),
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


_COMPOSITION_SPEC_DATA: tuple[CompositionSpec, ...] = (
    CompositionSpec(
        "result_preview",
        "What are we building toward?",
        "wide_action",
        "result",
        ("hip_fulcrum", "knee_over_head", "elbow_line"),
        "closed_guard_posture_broken",
        "armbar_from_guard",
        "armbar_extension_held",
        ("result_badge", "rewind_motif"),
        "rewind",
    ),
    CompositionSpec(
        "wide_setup",
        "Who is where?",
        "wide_action",
        "cast",
        ("wrist_control", "hip_fulcrum", "knee_over_head"),
        "closed_guard_posture_broken",
        "two_on_one_wrist_control",
        "wrist_control_hip_frame",
        ("support_points",),
        "cut",
    ),
    CompositionSpec(
        "contact_closeup",
        "What exactly connects?",
        "grip_closeup",
        "wrist_control",
        ("wrist_control", "hip_fulcrum"),
        "closed_guard_posture_broken",
        "two_on_one_wrist_control",
        "wrist_control_hip_frame",
        ("contact_ring", "context_inset"),
        "push_in",
    ),
    CompositionSpec(
        "mechanic_transition",
        "What changes the position?",
        "wide_action",
        "hip_fulcrum",
        ("wrist_control", "hip_fulcrum", "knee_over_head"),
        "wrist_control_hip_frame",
        "hip_angle_and_leg_swing",
        "hip_angle_and_leg_control",
        ("motion_path",),
        "inherit_subject",
    ),
    CompositionSpec(
        "wrong_right_compare",
        "Why does the common attempt fail?",
        "split",
        "elbow_line",
        ("elbow_line", "hip_fulcrum"),
        "wrist_control_hip_frame",
        "leg_over_head_elbow_pin",
        "hip_angle_and_leg_control",
        ("matched_frame", "decisive_variable"),
        "match_cut",
    ),
    CompositionSpec(
        "force_diagram",
        "Why does it work?",
        "medium",
        "hip_fulcrum",
        ("hip_fulcrum", "elbow_load", "wrist_control"),
        "hip_angle_and_leg_control",
        "leg_over_head_elbow_pin",
        "armbar_extension_contact",
        ("fulcrum", "load", "effort"),
        "reveal_geometry",
    ),
    CompositionSpec(
        "result_hold",
        "What should I recognize?",
        "wide_action",
        "result",
        ("hip_fulcrum", "elbow_line", "knee_over_head"),
        "armbar_extension_contact",
        "extend_and_settle",
        "armbar_extension_held",
        ("recognition_checklist",),
        "hold",
    ),
    CompositionSpec(
        "story_or_persona_cutaway",
        "Why keep watching?",
        "medium",
        "knee_over_head",
        ("knee_over_head",),
        "hip_angle_and_leg_control",
        "hip_angle_and_leg_swing",
        "hip_angle_and_leg_control",
        ("persona_card",),
        "cut",
    ),
)

COMPOSITION_SPECS: dict[str, CompositionSpec] = {
    spec.function: spec for spec in _COMPOSITION_SPEC_DATA
}
COMPOSITION_GRAMMAR = COMPOSITION_SPECS


@dataclass(frozen=True, slots=True)
class ContactMacro:
    """A close-up that retains enough cast context to preserve ownership."""

    macro_id: str
    anchor_id: str
    focus: str
    context_joints: tuple[str, ...]
    framing: str
    label: str

    @property
    def id(self) -> str:
        return self.macro_id

    @property
    def anchor(self) -> str:
        return self.anchor_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "macro_id": self.macro_id,
            "anchor_id": self.anchor_id,
            "focus": self.focus,
            "context_joints": list(self.context_joints),
            "framing": self.framing,
            "label": self.label,
            "context_preserved": True,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


CONTACT_MACRO_SPECS: dict[str, ContactMacro] = {
    "wrist_control": ContactMacro(
        "wrist_control",
        "wrist_control",
        "attacker:wrist_right",
        (
            "attacker:elbow_right",
            "attacker:shoulder_right",
            "defender:elbow_left",
            "defender:shoulder_left",
        ),
        "grip_closeup",
        "TWO-ON-ONE WRIST",
    ),
    "hip_fulcrum": ContactMacro(
        "hip_fulcrum",
        "hip_fulcrum",
        "attacker:hip_right",
        (
            "attacker:shoulder_right",
            "attacker:knee_right",
            "defender:elbow_right",
            "defender:hip_right",
        ),
        "contact_closeup",
        "HIP AS FULCRUM",
    ),
}

class _SpecCollection(tuple):
    """Tuple-like deterministic collection with mapping-style lookup."""

    def __new__(cls, values: Sequence[Any]):
        return super().__new__(cls, values)

    def __getitem__(self, key: int | slice | str) -> Any:
        if isinstance(key, str):
            for item in self:
                if getattr(item, "id", None) == key or getattr(item, "name", None) == key:
                    return item
            aliases = {
                "grip": "wrist_control",
                "wrist": "wrist_control",
                "frame": "hip_fulcrum",
                "hip": "hip_fulcrum",
                "fulcrum": "hip_fulcrum",
                "force_diagram": "fulcrum_load_effort",
                "force": "fulcrum_load_effort",
                "leverage": "fulcrum_load_effort",
                "living_leverage": "fulcrum_load_effort",
                "contact": "contact_to_leverage",
            }
            alias = aliases.get(key)
            if alias:
                for item in self:
                    if getattr(item, "id", None) == alias or getattr(item, "name", None) == alias:
                        return item
            raise KeyError(key)
        return super().__getitem__(key)

    def keys(self) -> tuple[str, ...]:
        return tuple(str(getattr(item, "id", getattr(item, "name", ""))) for item in self)

    def values(self) -> tuple[Any, ...]:
        return tuple(self)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default


# Several integrations prefer a tuple for coverage checks, while others need
# lookup by ID.  This collection supports both without introducing mutable
# module state.
CONTACT_MACROS: _SpecCollection = _SpecCollection(tuple(CONTACT_MACRO_SPECS.values()))
CONTACT_MACRO_IDS: tuple[str, ...] = tuple(CONTACT_MACRO_SPECS)
CONTACT_MACRO_ALIASED_IDS: tuple[str, ...] = ("grip", "frame")
CONTACT_MACRO_ALIASES: dict[str, str] = {
    "grip": "wrist_control",
    "wrist": "wrist_control",
    "frame": "hip_fulcrum",
    "hip": "hip_fulcrum",
    "fulcrum": "hip_fulcrum",
}


@dataclass(frozen=True, slots=True)
class MatchedComparison:
    """Wrong/right panels sharing one start state and camera framing."""

    comparison_id: str
    start_state: str
    wrong_anchor: str
    right_anchor: str
    decisive_variable: str
    framing: str = "split"

    @property
    def id(self) -> str:
        return self.comparison_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "comparison_id": self.comparison_id,
            "start_state": self.start_state,
            "wrong": {
                "state": self.start_state,
                "anchor": self.wrong_anchor,
                "label": "WRONG",
            },
            "right": {
                "state": self.start_state,
                "anchor": self.right_anchor,
                "label": "RIGHT",
            },
            "decisive_variable": self.decisive_variable,
            "framing": self.framing,
            "matched_start_state": True,
            "matched_framing": True,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


MATCHED_WRONG_RIGHT = MatchedComparison(
    "armbar_elbow_line",
    "wrist_control_hip_frame",
    "elbow_load",
    "elbow_line",
    "elbow_alignment",
)
MATCHED_COMPARISON = MATCHED_WRONG_RIGHT


@dataclass(frozen=True, slots=True)
class LivingDiagramSpec:
    """Geometry that is revealed on top of the persistent cast."""

    diagram_id: str
    anchor_ids: tuple[str, ...]
    labels: tuple[str, ...]
    state_from: str
    state_to: str
    transition: str

    @property
    def id(self) -> str:
        return self.diagram_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "diagram_id": self.diagram_id,
            "anchor_ids": list(self.anchor_ids),
            "labels": list(self.labels),
            "state_from": self.state_from,
            "state_to": self.state_to,
            "transition": self.transition,
            "derived_from_reviewed_anchors": True,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


LIVING_DIAGRAM_SPECS: dict[str, LivingDiagramSpec] = {
    "fulcrum_load_effort": LivingDiagramSpec(
        "fulcrum_load_effort",
        ("hip_fulcrum", "elbow_load", "wrist_control"),
        ("FULCRUM", "LOAD", "EFFORT"),
        "hip_angle_and_leg_control",
        "armbar_extension_contact",
        "reveal_geometry",
    ),
    "contact_to_leverage": LivingDiagramSpec(
        "contact_to_leverage",
        ("wrist_control", "hip_fulcrum", "knee_over_head"),
        ("CONTACT", "FULCRUM", "FRAME"),
        "wrist_control_hip_frame",
        "hip_angle_and_leg_control",
        "inherit_subject",
    ),
}
LIVING_DIAGRAMS: _SpecCollection = _SpecCollection(tuple(LIVING_DIAGRAM_SPECS.values()))
LIVING_DIAGRAM_IDS: tuple[str, ...] = tuple(LIVING_DIAGRAM_SPECS)
LIVING_DIAGRAM_TRANSITIONS = tuple(spec.transition for spec in LIVING_DIAGRAMS)
LIVING_DIAGRAM_TRANSITION_ALIASES: dict[str, str] = {
    "resume_action": "inherit_subject",
    "resume": "inherit_subject",
    "reveal": "reveal_geometry",
}
LIVING_DIAGRAM_ALIASES: dict[str, str] = {
    "force_diagram": "fulcrum_load_effort",
    "force": "fulcrum_load_effort",
    "leverage": "fulcrum_load_effort",
    "living_leverage": "fulcrum_load_effort",
    "contact": "contact_to_leverage",
}


def _set_metadata(value: Any, **metadata: Any) -> Any:
    for key, item in metadata.items():
        try:
            setattr(value, key, item)
        except Exception:
            pass
    return value


def _point_tuple(value: Sequence[float]) -> Point:
    values = tuple(float(item) for item in value)
    if len(values) == 2:
        return values[0], values[1], 0.0
    if len(values) != 3:
        raise ValueError(f"point must contain two or three values: {value!r}")
    return values  # type: ignore[return-value]


def _resolve_function(scene: Any, function: str | None = None) -> str:
    if function:
        value = str(function)
    else:
        spec = getattr(scene, "scene_spec", {}) or {}
        params = spec.get("parameters") or {}
        value = str(
            spec.get("visual_function")
            or spec.get("composition_function")
            or spec.get("function")
            or spec.get("shot_function")
            or params.get("function")
            or params.get("composition_function")
            or params.get("shot_function")
            or "mechanic_transition"
        )
    if value not in COMPOSITION_SPECS:
        raise ValueError(
            f"unknown Combat Science composition function {value!r}; "
            f"expected one of {', '.join(COMPOSITION_FUNCTION_NAMES)}"
        )
    return value


def _resolve_anchor(scene: Any, anchor_id: str) -> str:
    canonical = CONTACT_ANCHOR_ALIASES.get(anchor_id, anchor_id)
    if canonical not in scene.contact_anchors:
        raise KeyError(f"unknown reviewed contact anchor: {anchor_id}")
    return canonical


def _anchor_point(scene: Any, anchor_id: str, state: str | None = None) -> Point:
    return _point_tuple(scene.contact_anchor(_resolve_anchor(scene, anchor_id), state))


def composition_contract(scene: Any, function: str | None = None) -> dict[str, Any]:
    """Return the deterministic renderer contract for one composition path."""

    function_id = _resolve_function(scene, function)
    spec = COMPOSITION_SPECS[function_id]
    # Resolve every anchor now: an unresolved instructional contact must fail
    # before an optional paid/render dependency is reached.
    anchors = tuple(_resolve_anchor(scene, anchor) for anchor in spec.anchors)
    phases = tuple(getattr(scene, "phases", ()) or ())
    phase_by_name = {getattr(phase, "name", ""): phase for phase in phases}
    state_from = STATE_ALIASES.get(spec.state_from, spec.state_from)
    state_to = STATE_ALIASES.get(spec.state_to, spec.state_to)
    if state_from not in STATE_POSES or state_to not in STATE_POSES:
        raise KeyError(f"unknown reviewed composition state: {state_from} -> {state_to}")
    action = spec.action
    if action in {getattr(phase, "action", None) for phase in phases}:
        resolved_action = action
    elif phase_by_name:
        resolved_action = str(getattr(next(iter(phase_by_name.values())), "action", action))
    else:
        resolved_action = action
    camera = {
        "framing": spec.framing,
        "focus": spec.focus,
        "transition": spec.transition,
    }
    return {
        "contract_version": "combat_science_composition.v1",
        "composition_version": "combat_science_composition.v1",
        "function": function_id,
        "function_id": function_id,
        "viewer_question": spec.viewer_question,
        "cast": {
            "attacker": scene.cast.members["attacker"].variant_id,
            "defender": scene.cast.members["defender"].variant_id,
        },
        "state_from": state_from,
        "action": resolved_action,
        "state_to": state_to,
        "camera": camera,
        "camera_focus": spec.focus,
        "motion": {
            "path": getattr(getattr(scene, "phase_for_action", lambda _x: None)(resolved_action), "motion_path", spec.transition),
            "phases": list(PHASE_NAMES),
        },
        "reviewed_anchors": list(anchors),
        "anchors": list(anchors),
        "contact_anchors": list(anchors),
        "overlays": list(spec.overlays),
        "contact_macro": function_id == "contact_closeup",
        "context_preserved": function_id == "contact_closeup",
        "matched_comparison": function_id == "wrong_right_compare",
        "living_diagram": function_id == "force_diagram",
        "reference_refs": [],
    }


def _label(
    value: str,
    position: Point,
    color: Any,
    *,
    size: float = 24,
    z: int = 125,
    font: str = "Inter",
) -> Any:
    label = Text(value, font_size=size, color=color, font=font)
    _safe_move_to(label, position)
    _safe_set_z_index(label, z)
    return label


def build_contact_macro(
    scene: Any,
    macro: str | ContactMacro = "wrist_control",
    *,
    state: str | None = None,
) -> Any:
    """Build a contact close-up while retaining an ownership context inset."""

    macro_spec = macro if isinstance(macro, ContactMacro) else CONTACT_MACRO_SPECS.get(str(macro))
    if macro_spec is None:
        alias = CONTACT_MACRO_ALIASES.get(str(macro), CONTACT_ANCHOR_ALIASES.get(str(macro), str(macro)))
        macro_spec = CONTACT_MACRO_SPECS.get(alias)
    if macro_spec is None:
        raise KeyError(f"unknown contact macro: {macro!r}")
    anchor_id = _resolve_anchor(scene, macro_spec.anchor_id)
    state_id = STATE_ALIASES.get(state or getattr(scene, "initial_state", ""), state or getattr(scene, "initial_state", ""))
    focus = _anchor_point(scene, anchor_id, state_id)
    layers: list[Any] = []
    focus_marker = Circle(radius=0.18, color=color_value("#20D69B"), fill_opacity=0.22, stroke_width=3.0)
    _safe_move_to(focus_marker, scene._view_point(focus, state_id))
    layers.append(focus_marker)
    context_positions: dict[str, Point] = {}
    for index, token in enumerate(macro_spec.context_joints):
        owner, joint = token.split(":", 1)
        position = _point_tuple(scene.cast.position(owner, joint, state_id))
        context_positions[token] = position
        # Thin context rays and low-opacity markers keep the surrounding body
        # readable without turning the close-up back into a line skeleton.
        ray = Line(
            scene._view_point(focus, state_id),
            scene._view_point(position, state_id),
            color=color_value("#8B5CF6"),
            stroke_width=1.2,
        )
        try:
            ray.set_opacity(0.38)
        except Exception:
            ray.opacity = 0.38
        layers.extend([ray, Circle(radius=0.05, color=color_value("#F4F7FA"))])
        _safe_move_to(layers[-1], scene._view_point(position, state_id))
    layers.append(_label(macro_spec.label, (0.0, 3.1 if scene.aspect == "landscape" else 5.4, 0.0), color_value("#20D69B")))
    group = VGroup(*layers)
    return _set_metadata(
        group,
        composition_function="contact_closeup",
        macro_id=macro_spec.macro_id,
        anchor_id=anchor_id,
        focus_anchor=anchor_id,
        anchor_position=focus,
        context_joints=tuple(macro_spec.context_joints),
        context_anchors=tuple(macro_spec.context_joints),
        context_positions=context_positions,
        context_preserved=True,
        ownership_preserved=True,
        body_ownership=dict(scene.body_ownership),
        state=state_id,
        framing=macro_spec.framing,
    )


def build_matched_comparison(
    scene: Any,
    comparison: MatchedComparison = MATCHED_WRONG_RIGHT,
    *,
    state: str | None = None,
) -> Any:
    """Build matched wrong/right panels from one reviewed start state."""

    state_id = STATE_ALIASES.get(state or comparison.start_state, state or comparison.start_state)
    if state_id not in STATE_POSES:
        raise KeyError(f"unknown comparison state: {state_id}")
    wrong_anchor = _resolve_anchor(scene, comparison.wrong_anchor)
    right_anchor = _resolve_anchor(scene, comparison.right_anchor)
    panel_layers: list[Any] = []
    panel_meta: list[dict[str, Any]] = []
    for side, anchor_id, color, x, label in (
        ("wrong", wrong_anchor, "#EF5B5B", -3.0, "WRONG  / ELBOW DROPS"),
        ("right", right_anchor, "#20D69B", 3.0, "RIGHT  / ELBOW ALIGNED"),
    ):
        point = _anchor_point(scene, anchor_id, state_id)
        marker = Circle(radius=0.16, color=color_value(color), fill_opacity=0.22, stroke_width=3.0)
        _safe_move_to(marker, (x, point[1], point[2]))
        panel_label = _label(label, (x, 3.05 if scene.aspect == "landscape" else 5.4, 0.0), color_value(color), size=20)
        panel = VGroup(marker, panel_label)
        _set_metadata(
            panel,
            comparison_side=side,
            state=state_id,
            anchor_id=anchor_id,
            framing=comparison.framing,
            matched_start_state=True,
            matched_framing=True,
            decisive_variable=comparison.decisive_variable,
            body_ownership=dict(scene.body_ownership),
        )
        panel_layers.append(panel)
        panel_meta.append({"side": side, "state": state_id, "anchor_id": anchor_id})
    group = VGroup(*panel_layers)
    return _set_metadata(
        group,
        composition_function="wrong_right_compare",
        comparison_id=comparison.comparison_id,
        panels=tuple(panel_meta),
        matched_start_state=True,
        matched_framing=True,
        decisive_variable=comparison.decisive_variable,
        context_preserved=True,
        wrong_panel=panel_layers[0],
        right_panel=panel_layers[1],
    )


def build_living_diagram(
    scene: Any,
    diagram: str | LivingDiagramSpec = "fulcrum_load_effort",
    *,
    state: str | None = None,
    progress: float = 1.0,
) -> Any:
    """Reveal force geometry on top of the same reviewed action state."""

    diagram_id = str(diagram)
    diagram_id = LIVING_DIAGRAM_ALIASES.get(diagram_id, diagram_id)
    spec = diagram if isinstance(diagram, LivingDiagramSpec) else LIVING_DIAGRAM_SPECS.get(diagram_id)
    if spec is None:
        raise KeyError(f"unknown living diagram: {diagram!r}")
    state_id = STATE_ALIASES.get(state or spec.state_from, state or spec.state_from)
    if state_id not in STATE_POSES:
        raise KeyError(f"unknown living diagram state: {state_id}")
    progress_value = max(0.0, min(1.0, float(progress)))
    points = {anchor: _anchor_point(scene, anchor, state_id) for anchor in spec.anchor_ids}
    layers: list[Any] = []
    anchor_positions: dict[str, Point] = {}
    for index, anchor_id in enumerate(spec.anchor_ids):
        point = points[anchor_id]
        anchor_positions[anchor_id] = point
        marker = Circle(radius=0.11, color=color_value("#20D69B"), fill_opacity=0.18, stroke_width=2.0)
        _safe_move_to(marker, scene._view_point(point, state_id))
        layers.append(marker)
        if index:
            previous = points[spec.anchor_ids[index - 1]]
            # The endpoint is interpolated only for the reveal; both anchors
            # themselves always come directly from the reviewed cast.
            target = (
                previous[0] + (point[0] - previous[0]) * progress_value,
                previous[1] + (point[1] - previous[1]) * progress_value,
                previous[2] + (point[2] - previous[2]) * progress_value,
            )
            arrow = Arrow(
                scene._view_point(previous, state_id),
                scene._view_point(target, state_id),
                color=color_value("#20D69B" if index == 1 else "#FF8A3D"),
                stroke_width=4.0,
            )
            layers.append(arrow)
        label_position = (point[0] + 0.2, point[1] + 0.32, point[2])
        layers.append(_label(spec.labels[index], scene._view_point(label_position, state_id), color_value("#F4F7FA"), size=17, font="Roboto Mono"))
    group = VGroup(*layers)
    return _set_metadata(
        group,
        composition_function="force_diagram",
        diagram_id=spec.diagram_id,
        anchor_ids=tuple(spec.anchor_ids),
        anchor_positions=anchor_positions,
        anchor_points=anchor_positions,
        derived_from_reviewed_anchors=True,
        body_ownership=dict(scene.body_ownership),
        state=state_id,
        state_from=STATE_ALIASES.get(spec.state_from, spec.state_from),
        state_to=STATE_ALIASES.get(spec.state_to, spec.state_to),
        progress=progress_value,
        transition=spec.transition,
        context_preserved=True,
    )


def build_living_diagram_transition(
    scene: Any,
    transition: str = "reveal_geometry",
    *,
    state: str | None = None,
) -> Any:
    """Build one of the two deterministic living-geometry transitions."""

    transition_id = LIVING_DIAGRAM_TRANSITION_ALIASES.get(str(transition), str(transition))
    candidates = [spec for spec in LIVING_DIAGRAMS if spec.transition == transition_id]
    if not candidates:
        raise KeyError(f"unknown living diagram transition: {transition}")
    group = build_living_diagram(scene, candidates[0], state=state, progress=1.0)
    return _set_metadata(
        group,
        transition_from=transition_id,
        transition_to="resume_action" if transition_id == "reveal_geometry" else "action",
    )


def _composition_result_preview(scene: Any) -> Any:
    point = _anchor_point(scene, "hip_fulcrum", "armbar_extension_held")
    marker = Circle(radius=0.22, color=color_value("#FF8A3D"), fill_opacity=0.25, stroke_width=3.0)
    _safe_move_to(marker, scene._view_point(point, "armbar_extension_held"))
    label = _label("RESULT  /  REWIND", (0.0, 3.2 if scene.aspect == "landscape" else 5.5, 0.0), color_value("#FF8A3D"))
    return _set_metadata(VGroup(marker, label), composition_function="result_preview", anchor_ids=("hip_fulcrum", "knee_over_head", "elbow_line"), context_preserved=True)


def _composition_wide_setup(scene: Any) -> Any:
    ground = Line((-5.8, -2.2, 0.0), (5.8, -2.2, 0.0), color=scene._theme_color("primary_text"), stroke_width=1.2)
    label = _label("POSITION  /  SUPPORT POINTS", (0.0, 3.2 if scene.aspect == "landscape" else 5.5, 0.0), scene._theme_color("accent_color"))
    return _set_metadata(VGroup(ground, label), composition_function="wide_setup", anchor_ids=("wrist_control", "hip_fulcrum", "knee_over_head"), context_preserved=True)


def _composition_contact_closeup(scene: Any) -> Any:
    spec = getattr(scene, "scene_spec", {}) or {}
    params = spec.get("parameters") or {}
    requested = (
        spec.get("contact_macro")
        or spec.get("contact")
        or params.get("contact_macro")
        or params.get("contact")
        or "wrist_control"
    )
    if isinstance(requested, Sequence) and not isinstance(requested, str):
        requested = next(iter(requested), "wrist_control")
    return build_contact_macro(scene, str(requested))


def _composition_mechanic_transition(scene: Any) -> Any:
    start = _anchor_point(scene, "wrist_control", "wrist_control_hip_frame")
    end = _anchor_point(scene, "hip_fulcrum", "hip_angle_and_leg_control")
    path = Arrow(scene._view_point(start, "wrist_control_hip_frame"), scene._view_point(end, "hip_angle_and_leg_control"), color=scene._theme_color("secondary_accent"), stroke_width=5.0)
    label = _label("HIP ANGLE  →  LEG CONTROL", (0.0, 3.2 if scene.aspect == "landscape" else 5.5, 0.0), scene._theme_color("secondary_accent"), size=22)
    return _set_metadata(VGroup(path, label), composition_function="mechanic_transition", anchor_ids=("wrist_control", "hip_fulcrum", "knee_over_head"), path="arc", context_preserved=True)


def _composition_wrong_right_compare(scene: Any) -> Any:
    return build_matched_comparison(scene)


def _composition_force_diagram(scene: Any) -> Any:
    return build_living_diagram(scene, "fulcrum_load_effort")


def _composition_result_hold(scene: Any) -> Any:
    point = _anchor_point(scene, "hip_fulcrum", "armbar_extension_held")
    marker = Circle(radius=0.18, color=scene._theme_color("secondary_accent"), fill_opacity=0.2, stroke_width=3.0)
    _safe_move_to(marker, scene._view_point(point, "armbar_extension_held"))
    label = _label("CONTROLLED RESULT", (0.0, 3.2 if scene.aspect == "landscape" else 5.5, 0.0), scene._theme_color("secondary_accent"))
    checklist = _label("HIP  •  ELBOW LINE  •  LEG FRAME", (0.0, -3.1 if scene.aspect == "landscape" else -5.5, 0.0), scene._theme_color("primary_text"), size=18)
    return _set_metadata(VGroup(marker, label, checklist), composition_function="result_hold", anchor_ids=("hip_fulcrum", "elbow_line", "knee_over_head"), context_preserved=True)


def _composition_story_cutaway(scene: Any) -> Any:
    point = _anchor_point(scene, "knee_over_head", "hip_angle_and_leg_control")
    frame = Circle(radius=0.38, color=scene._theme_color("accent_color"), fill_opacity=0.12, stroke_width=3.0)
    _safe_move_to(frame, scene._view_point(point, "hip_angle_and_leg_control"))
    label = _label("THE DETAIL THAT HOLDS", (0.0, 3.2 if scene.aspect == "landscape" else 5.5, 0.0), scene._theme_color("accent_color"), size=22)
    return _set_metadata(VGroup(frame, label), composition_function="story_or_persona_cutaway", anchor_ids=("knee_over_head",), context_preserved=True)


# Public module-level composition functions are useful to style-board tests
# and keep the grammar independent of a concrete Scene subclass.
result_preview = _composition_result_preview
wide_setup = _composition_wide_setup
contact_closeup = _composition_contact_closeup
mechanic_transition = _composition_mechanic_transition
wrong_right_compare = _composition_wrong_right_compare
force_diagram = _composition_force_diagram
result_hold = _composition_result_hold
story_or_persona_cutaway = _composition_story_cutaway

COMPOSITION_FUNCTIONS: dict[str, Callable[[Any], Any]] = {
    "result_preview": result_preview,
    "wide_setup": wide_setup,
    "contact_closeup": contact_closeup,
    "mechanic_transition": mechanic_transition,
    "wrong_right_compare": wrong_right_compare,
    "force_diagram": force_diagram,
    "result_hold": result_hold,
    "story_or_persona_cutaway": story_or_persona_cutaway,
}
_COMPOSITION_RENDERERS: dict[str, Callable[[Any], Any]] = dict(COMPOSITION_FUNCTIONS)


def render_composition(scene: Any, function: str | None = None) -> Any:
    function_id = _resolve_function(scene, function)
    output = _COMPOSITION_RENDERERS[function_id](scene)
    _set_metadata(output, composition_contract=composition_contract(scene, function_id))
    return output


def _public_composition(function_id: str) -> Callable[[Any], Any]:
    def render(scene: Any) -> Any:
        return render_composition(scene, function_id)

    render.__name__ = function_id
    render.__qualname__ = function_id
    return render


class _CompositionRenderer:
    """Callable composition entry that also exposes static spec fields."""

    __slots__ = ("function",)

    def __init__(self, function: str) -> None:
        self.function = function

    @property
    def __name__(self) -> str:
        return self.function

    @property
    def name(self) -> str:
        return self.function

    def __call__(self, scene: Any) -> Any:
        return render_composition(scene, self.function)

    def __getitem__(self, key: str) -> Any:
        return COMPOSITION_SPECS[self.function].to_dict()[key]

    def to_dict(self) -> dict[str, Any]:
        return COMPOSITION_SPECS[self.function].to_dict()


CompositionRenderer = _CompositionRenderer


# Public functions carry their contract metadata too; the raw renderers above
# stay private so ``render_composition`` never recurses through this map.
result_preview = _public_composition("result_preview")
wide_setup = _public_composition("wide_setup")
contact_closeup = _public_composition("contact_closeup")
mechanic_transition = _public_composition("mechanic_transition")
wrong_right_compare = _public_composition("wrong_right_compare")
force_diagram = _public_composition("force_diagram")
result_hold = _public_composition("result_hold")
story_or_persona_cutaway = _public_composition("story_or_persona_cutaway")
COMPOSITION_FUNCTIONS = {
    name: _CompositionRenderer(name) for name in COMPOSITION_FUNCTION_NAMES
}


# Renderer/service naming variants kept as aliases so contracts remain stable
# when callers describe the operation as a build or a render.
build_composition_contract = composition_contract
render_contact_macro = build_contact_macro
render_matched_comparison = build_matched_comparison
render_living_diagram = build_living_diagram
render_living_diagram_transition = build_living_diagram_transition


class CombatScienceScene(BJJActionScene):
    """Filled-cast Armbar scene with all eight V3 composition functions."""

    visual_type = "combat_science"
    composition_functions = COMPOSITION_FUNCTION_NAMES
    composition_actions = COMPOSITION_FUNCTION_NAMES

    @property
    def composition_function(self) -> str:
        return _resolve_function(self)

    @property
    def composition_names(self) -> tuple[str, ...]:
        return COMPOSITION_FUNCTION_NAMES

    @property
    def required_composition_functions(self) -> tuple[str, ...]:
        return COMPOSITION_FUNCTION_NAMES

    @property
    def contact_macros(self) -> _SpecCollection:
        return CONTACT_MACROS

    @property
    def living_diagrams(self) -> _SpecCollection:
        return LIVING_DIAGRAMS

    @property
    def matched_comparison_spec(self) -> MatchedComparison:
        return MATCHED_WRONG_RIGHT

    def composition_contract(self, function: str | None = None) -> dict[str, Any]:
        return composition_contract(self, function)

    def action_contract(self) -> dict[str, Any]:
        contract = dict(super().action_contract())
        function_id = self.composition_function
        contract["function"] = function_id
        contract["composition"] = self.composition_contract(function_id)
        return contract

    def render_composition(self, function: str | None = None) -> Any:
        return render_composition(self, function)

    # Short aliases keep the renderer-facing API pleasant for direct scene
    # tests and for storyboard adapters that call a function by its grammar
    # name rather than by a ``render_`` prefix.
    render_function = render_composition
    composition_for = render_composition

    def function_contract(self, function: str | None = None) -> dict[str, Any]:
        return self.composition_contract(function)

    def _function_overlay(self) -> Any:
        return self.render_composition(self.composition_function)

    def render_result_preview(self) -> Any:
        return self.render_composition("result_preview")

    def render_wide_setup(self) -> Any:
        return self.render_composition("wide_setup")

    def render_contact_closeup(self) -> Any:
        return self.render_composition("contact_closeup")

    def render_mechanic_transition(self) -> Any:
        return self.render_composition("mechanic_transition")

    def render_wrong_right_compare(self) -> Any:
        return self.render_composition("wrong_right_compare")

    def render_force_diagram(self) -> Any:
        return self.render_composition("force_diagram")

    def render_result_hold(self) -> Any:
        return self.render_composition("result_hold")

    def render_story_or_persona_cutaway(self) -> Any:
        return self.render_composition("story_or_persona_cutaway")

    def result_preview(self) -> Any:
        return self.render_result_preview()

    def wide_setup(self) -> Any:
        return self.render_wide_setup()

    def contact_closeup(self) -> Any:
        return self.render_contact_closeup()

    def mechanic_transition(self) -> Any:
        return self.render_mechanic_transition()

    def wrong_right_compare(self) -> Any:
        return self.render_wrong_right_compare()

    def force_diagram(self) -> Any:
        return self.render_force_diagram()

    def result_hold(self) -> Any:
        return self.render_result_hold()

    def story_or_persona_cutaway(self) -> Any:
        return self.render_story_or_persona_cutaway()

    def contact_macro(self, macro: str = "wrist_control", *, state: str | None = None) -> Any:
        return build_contact_macro(self, macro, state=state)

    def matched_wrong_right(self, *, state: str | None = None) -> Any:
        return build_matched_comparison(self, state=state)

    def living_diagram(self, diagram: str = "fulcrum_load_effort", *, state: str | None = None, progress: float = 1.0) -> Any:
        return build_living_diagram(self, diagram, state=state, progress=progress)

    def living_diagram_transition(self, transition: str = "reveal_geometry", *, state: str | None = None) -> Any:
        return build_living_diagram_transition(self, transition, state=state)

    living_geometry = living_diagram
    contact_macro_group = contact_macro
    matched_comparison = matched_wrong_right


__all__ = [
    "COMPOSITION_FUNCTION_NAMES",
    "COMPOSITION_NAMES",
    "SHOT_FUNCTION_NAMES",
    "COMPOSITION_FUNCTIONS",
    "COMPOSITION_SPECS",
    "COMPOSITION_GRAMMAR",
    "CompositionSpec",
    "CompositionRenderer",
    "CONTACT_MACROS",
    "CONTACT_MACRO_IDS",
    "CONTACT_MACRO_ALIASED_IDS",
    "CONTACT_MACRO_ALIASES",
    "CONTACT_MACRO_SPECS",
    "ContactMacro",
    "MATCHED_WRONG_RIGHT",
    "MATCHED_COMPARISON",
    "MatchedComparison",
    "LIVING_DIAGRAMS",
    "LIVING_DIAGRAM_IDS",
    "LIVING_DIAGRAM_ALIASES",
    "LIVING_DIAGRAM_SPECS",
    "LIVING_DIAGRAM_TRANSITIONS",
    "LIVING_DIAGRAM_TRANSITION_ALIASES",
    "LivingDiagramSpec",
    "build_contact_macro",
    "build_matched_comparison",
    "build_living_diagram",
    "build_living_diagram_transition",
    "composition_contract",
    "build_composition_contract",
    "render_composition",
    "render_contact_macro",
    "render_matched_comparison",
    "render_living_diagram",
    "render_living_diagram_transition",
    "result_preview",
    "wide_setup",
    "contact_closeup",
    "mechanic_transition",
    "wrong_right_compare",
    "force_diagram",
    "result_hold",
    "story_or_persona_cutaway",
    "CombatScienceScene",
    "CombatScienceCast",
    "build_combat_science_cast",
]
