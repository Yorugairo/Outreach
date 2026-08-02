"""Original, deterministic scene grammar for History Documentary V4.

The scene module is intentionally provider neutral.  It exposes eight small
shot factories that return renderer-safe scene records and a generic Manim
``DocumentaryScene`` for maps, timelines, lineage graphs, and conceptual
cutaways.  Archival photographs and illustrations are composited by Remotion;
Manim receives only labels, vectors, and approved asset IDs.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Mapping

from .base import Circle, Create, Dot, FadeIn, Line, Text, ThemedScene, VGroup, Write


DOCUMENTARY_FUNCTIONS: tuple[str, ...] = (
    "artifact_cold_open",
    "archival_portrait",
    "illustrated_reconstruction",
    "document_quote_closeup",
    "migration_map_timeline",
    "lineage_graph",
    "concept_mechanics_cutaway",
    "chapter_cta",
)

_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_HASH_OR_PATH_RE = re.compile(
    r"(?:https?://|file://|data:|blob:|\\|\.(?:png|jpe?g|webp|gif|mp4|mov)(?:$|[?#]))",
    re.IGNORECASE,
)
_PROHIBITED_KEYS = {
    "url",
    "source_url",
    "path",
    "source_path",
    "asset_path",
    "media_path",
    "study_path",
    "study_ref",
    "creator",
    "creator_name",
    "creator_id",
    "imitation_prompt",
    "renderer_prompt",
    "negative_prompt",
    "source_frame",
    "source_frames",
}


class DocumentarySceneError(ValueError):
    """Raised when a documentary scene would cross the renderer boundary."""


def _assert_renderer_safe(value: Any, path: tuple[str, ...] = ()) -> None:
    """Reject provenance and remote media before a scene reaches Manim."""

    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key).casefold().replace("-", "_")
            if key in _PROHIBITED_KEYS:
                raise DocumentarySceneError(
                    f"{'.'.join((*path, str(raw_key)))} is not a renderer-safe field"
                )
            _assert_renderer_safe(child, (*path, str(raw_key)))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_renderer_safe(child, (*path, str(index)))
    elif isinstance(value, str) and _HASH_OR_PATH_RE.search(value.strip()):
        raise DocumentarySceneError(
            f"{'.'.join(path) or 'value'} contains a URL, path, or media source"
        )


def _asset_ids(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set)):
        raise DocumentarySceneError("asset_ids must be a list of approved IDs")
    result: list[str] = []
    for item in value:
        asset_id = str(item).strip()
        if not _ID_RE.fullmatch(asset_id):
            raise DocumentarySceneError(f"invalid approved asset ID: {asset_id!r}")
        if asset_id not in result:
            result.append(asset_id)
    return result


def _citations(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, Mapping)):
        value = [value]
    if not isinstance(value, (list, tuple)):
        raise DocumentarySceneError("citations must be citation IDs or objects")
    result: list[Any] = []
    for item in value:
        if isinstance(item, str):
            citation = item.strip()
            if not citation:
                raise DocumentarySceneError("citation IDs may not be empty")
            result.append(citation)
        elif isinstance(item, Mapping):
            citation = dict(item)
            if not citation.get("citation_id"):
                raise DocumentarySceneError("citation object is missing citation_id")
            result.append(citation)
        else:
            raise DocumentarySceneError("citation values must be strings or objects")
    return result


def _scene_record(
    function: str,
    scene_spec: Mapping[str, Any] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    if function not in DOCUMENTARY_FUNCTIONS:
        raise DocumentarySceneError(f"unknown documentary function: {function}")
    incoming = copy.deepcopy(dict(scene_spec or {}))
    incoming.update(copy.deepcopy(overrides))
    _assert_renderer_safe(incoming)
    parameters = incoming.get("parameters")
    if not isinstance(parameters, Mapping):
        parameters = {}
    parameters = copy.deepcopy(dict(parameters))
    # Factories deliberately copy only renderer-facing fields from a caller's
    # parameters.  Research packets and resolved asset paths never cross this
    # boundary.
    ids = _asset_ids(incoming.get("asset_ids", parameters.pop("asset_ids", [])))
    citations = _citations(incoming.get("citations", parameters.pop("citations", [])))
    label = incoming.get("illustration_label", parameters.pop("illustration_label", None))
    if function == "illustrated_reconstruction":
        label = str(label or "ILLUSTRATION / RECONSTRUCTION")
    elif label is not None:
        label = str(label)
    duration = incoming.get("duration_s", incoming.get("timing", {}).get("target_s", 2.0) if isinstance(incoming.get("timing"), Mapping) else 2.0)
    try:
        duration_s = max(0.1, float(duration))
    except (TypeError, ValueError):
        duration_s = 2.0
    treatment_id = str(incoming.get("treatment_id") or f"treatment-{function.replace('_', '-')}")
    if not treatment_id.startswith("treatment-"):
        treatment_id = f"treatment-{treatment_id}"
    camera = incoming.get("camera")
    if not isinstance(camera, Mapping):
        camera = {}
    camera = {
        "framing": str(camera.get("framing") or function),
        "anchor": str(camera.get("anchor") or "centerline"),
        "move": str(camera.get("move") or "restrained_drift"),
        "safe_zone": str(camera.get("safe_zone") or "center"),
    }
    depth = incoming.get("depth")
    if not isinstance(depth, Mapping):
        depth = {}
    depth = {
        "background": int(depth.get("background", 0)),
        "subject": int(depth.get("subject", 1)),
        "overlay": int(depth.get("overlay", 2)),
    }
    motion = incoming.get("motion")
    if not isinstance(motion, Mapping):
        motion = {}
    motion = {
        "phases": list(motion.get("phases") or ["anticipation", "reveal", "recovery", "hold"]),
        "transition": str(motion.get("transition") or "paper_wipe"),
        "easing": str(motion.get("easing") or "ease_in_out"),
    }
    typography = incoming.get("typography")
    if not isinstance(typography, Mapping):
        typography = {}
    typography = {
        "caption_font": str(typography.get("caption_font") or "Inter (local OFL)"),
        "measurement_font": str(typography.get("measurement_font") or "Roboto Mono (local OFL)"),
    }
    # The caller may provide useful renderer parameters (map nodes, quote
    # text, etc.), but the factory adds the function discriminator itself.
    parameters["documentary_function"] = function
    parameters.setdefault("source_kind", "documentary")
    record: dict[str, Any] = {
        "source_kind": "documentary",
        "scene_class": "DocumentaryScene",
        "manim_class": "DocumentaryScene",
        "visual_type": function,
        "visual_function": function,
        "function": function,
        "scene_id": incoming.get("scene_id", function),
        "treatment_id": treatment_id,
        "purpose": str(incoming.get("purpose") or function.replace("_", " ").capitalize()),
        "composition": str(incoming.get("composition") or function),
        "style_atom_ids": list(incoming.get("style_atom_ids") or [function.replace("_", "-")]),
        "palette_roles": list(incoming.get("palette_roles") or ["paper", "ink", "rust"]),
        "camera": camera,
        "depth": depth,
        "motion": motion,
        "asset_ids": ids,
        "citations": citations,
        "credit_ids": list(incoming.get("credit_ids") or []),
        "typography": typography,
        "signature": str(incoming.get("signature") or f"history:{function}:editorial"),
        "uniqueness_signature": str(incoming.get("uniqueness_signature") or f"{function}:{treatment_id}"),
        "duration_s": duration_s,
        "parameters": parameters,
    }
    if label is not None:
        record["illustration_label"] = label
    if "phash" in incoming:
        record["phash"] = str(incoming["phash"])
    return record


def artifact_cold_open(scene_spec: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, Any]:
    """Open on an artifact and establish the historical question."""

    return _scene_record("artifact_cold_open", scene_spec, **overrides)


def archival_portrait(scene_spec: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, Any]:
    """Reveal an approved archival portrait with restrained parallax."""

    return _scene_record("archival_portrait", scene_spec, **overrides)


def illustrated_reconstruction(scene_spec: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, Any]:
    """Show a visibly labelled interpretation, never evidence."""

    return _scene_record("illustrated_reconstruction", scene_spec, **overrides)


def document_quote_closeup(scene_spec: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, Any]:
    """Focus a document or short quotation with a citation rail."""

    return _scene_record("document_quote_closeup", scene_spec, **overrides)


def migration_map_timeline(scene_spec: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, Any]:
    """Animate a migration route and dated timeline using Manim primitives."""

    return _scene_record("migration_map_timeline", scene_spec, **overrides)


def lineage_graph(scene_spec: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, Any]:
    """Reveal a sparse relationship/lineage graph with uncertainty labels."""

    return _scene_record("lineage_graph", scene_spec, **overrides)


def concept_mechanics_cutaway(scene_spec: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, Any]:
    """Explain one historical concept; this is not an instructional sequence."""

    return _scene_record("concept_mechanics_cutaway", scene_spec, **overrides)


def chapter_cta(scene_spec: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, Any]:
    """Close a chapter with a neutral thesis/CTA card."""

    return _scene_record("chapter_cta", scene_spec, **overrides)


_FACTORIES = {
    name: globals()[name]
    for name in DOCUMENTARY_FUNCTIONS
}


class DocumentaryScene(ThemedScene):
    """Generic Manim scene for documentary vectors and editorial labels."""

    def __init__(
        self,
        scene_spec: Mapping[str, Any] | None = None,
        layout: str = "landscape",
        audio_duration: float = 0.0,
        theme: Mapping[str, Any] | None = None,
    ) -> None:
        self.record = _scene_record(
            str((scene_spec or {}).get("function") or (scene_spec or {}).get("visual_type") or "chapter_cta"),
            scene_spec,
        )
        super().__init__(self.record, layout, audio_duration, dict(theme or {}))
        self.function = str(self.record["function"])

    def _activate_scene(
        self,
        scene_spec: dict[str, Any],
        layout: str | None = None,
        audio_duration: float | None = None,
        theme: dict[str, Any] | None = None,
    ) -> None:
        """Refresh the normalized documentary record for sequence renders."""

        super()._activate_scene(
            scene_spec,
            layout=layout,
            audio_duration=audio_duration,
            theme=theme,
        )
        self.record = _scene_record(
            str(
                scene_spec.get("function")
                or scene_spec.get("visual_function")
                or scene_spec.get("visual_type")
                or "chapter_cta"
            ),
            scene_spec,
        )
        self.function = str(self.record["function"])

    @property
    def parameters(self) -> Mapping[str, Any]:
        value = self.record.get("parameters")
        return value if isinstance(value, Mapping) else {}

    def entrance(self) -> None:
        # Documentary shots are editorial cuts even when they share a Manim
        # render unit. Retaining prior mobjects causes the first treatment to
        # ghost through every later shot.
        if self._section_start > 0 and self.mobjects:
            self.remove(*tuple(self.mobjects))
        title = Text(
            str(self.record.get("purpose") or self.function.replace("_", " ").title()),
            color=self._theme_color("primary_text"),
        )
        try:
            title.to_edge((0.0, 1.0, 0.0))
        except Exception:
            pass
        self.add(title)
        self.play(FadeIn(title), run_time=0.2)

    def _label(self, value: Any) -> Any:
        label = Text(str(value), color=self._theme_color("primary_text"))
        self.add(label)
        return label

    def _draw_nodes(self, nodes: list[Any], *, graph: bool = False) -> None:
        points: dict[str, Any] = {}
        total = max(1, len(nodes))
        for index, raw in enumerate(nodes):
            item = raw if isinstance(raw, Mapping) else {"id": str(raw), "label": str(raw)}
            node_id = str(item.get("id") or item.get("name") or index)
            label = str(item.get("label") or item.get("name") or node_id)
            x = -4.0 + 8.0 * index / max(1, total - 1) if total > 1 else 0.0
            y = 0.45 if index % 2 == 0 else -0.45
            point = Dot((x, y, 0.0), color=self._theme_color("secondary_accent"))
            caption = Text(label, color=self._theme_color("primary_text"))
            try:
                caption.next_to(point, direction=(0.0, -1.0, 0.0))
            except Exception:
                pass
            points[node_id] = point
            self.add(point, caption)
        edges = self.parameters.get("edges") or self.parameters.get("links") or []
        for raw in edges:
            if isinstance(raw, Mapping):
                source = str(raw.get("source") or raw.get("from") or "")
                target = str(raw.get("target") or raw.get("to") or "")
            elif isinstance(raw, (list, tuple)) and len(raw) >= 2:
                source, target = str(raw[0]), str(raw[1])
            else:
                continue
            if source in points and target in points:
                line = Line(points[source], points[target], color=self._theme_color("secondary_accent"))
                self.add(line)
                self.play(Create(line), run_time=0.2)
        if points:
            self.play(FadeIn(next(iter(points.values()))), run_time=0.2)

    def body(self, audio_duration: float) -> None:
        params = self.parameters
        if self.function in {"migration_map_timeline", "lineage_graph"}:
            raw_nodes = params.get("nodes") or params.get("locations") or params.get("points") or []
            nodes = list(raw_nodes) if isinstance(raw_nodes, (list, tuple)) else list(raw_nodes) if isinstance(raw_nodes, Mapping) else []
            self._draw_nodes(nodes, graph=self.function == "lineage_graph")
        elif self.function == "concept_mechanics_cutaway":
            left = Circle(radius=0.55, color=self._theme_color("secondary_accent"))
            right = Circle(radius=0.35, color=self._theme_color("active_emphasis"))
            arrow = Line((-1.5, 0.0, 0.0), (1.5, 0.0, 0.0), color=self._theme_color("secondary_accent"))
            self.add(left, right, arrow)
            self.play(Create(arrow), run_time=0.3)
        else:
            value = params.get("quote") or params.get("label") or self.record.get("visual_type")
            self._label(value)
            self.play(Write(self.mobjects[-1]), run_time=0.25)
        total = max(float(audio_duration or self.audio_duration or 0.4), 0.4)
        elapsed = max(0.0, self._play_timeline - self._section_start)
        if total > elapsed:
            self.wait(total - elapsed)


def scene_factory(function: str, scene_spec: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, Any]:
    """Resolve a documentary function without dynamic imports."""

    try:
        factory = _FACTORIES[str(function)]
    except KeyError as exc:
        raise DocumentarySceneError(f"unknown documentary function: {function}") from exc
    return factory(scene_spec, **overrides)


__all__ = [
    "DOCUMENTARY_FUNCTIONS",
    "DocumentaryScene",
    "DocumentarySceneError",
    "artifact_cold_open",
    "archival_portrait",
    "illustrated_reconstruction",
    "document_quote_closeup",
    "migration_map_timeline",
    "lineage_graph",
    "concept_mechanics_cutaway",
    "chapter_cta",
    "scene_factory",
]
