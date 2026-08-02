"""Shared scene primitives for the content video engine.

The project keeps Manim at the edge of the system.  Importing the scene
library must therefore remain safe on an operator machine that has not yet
installed Manim; render jobs fail explicitly at the renderer boundary while
contract tests can still exercise scene construction and timing logic.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


try:  # pragma: no cover - exercised by the optional render smoke test
    from manim import (  # type: ignore
        BLACK,
        BLUE,
        GREEN,
        RED,
        WHITE,
        Arrow,
        Circle,
        Create,
        Dot,
        FadeIn,
        FadeOut,
        GrowArrow,
        Line,
        SVGMobject,
        Scene,
        Text,
        VGroup,
        Wait,
        Write,
        tempconfig,
    )

    MANIM_AVAILABLE = True
except ImportError:  # pragma: no cover - the normal unit-test path here
    MANIM_AVAILABLE = False

    class _FallbackMobject:
        """Tiny fluent stand-in used only for non-rendering contract tests."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs
            self.submobjects: list[Any] = []

        def add(self, *mobjects: Any) -> "_FallbackMobject":
            self.submobjects.extend(mobjects)
            return self

        def copy(self) -> "_FallbackMobject":
            return _FallbackMobject(*self.args, **self.kwargs)

        def scale(self, *_args: Any, **_kwargs: Any) -> "_FallbackMobject":
            return self

        def move_to(self, *_args: Any, **_kwargs: Any) -> "_FallbackMobject":
            return self

        def shift(self, *_args: Any, **_kwargs: Any) -> "_FallbackMobject":
            return self

        def set_color(self, *_args: Any, **_kwargs: Any) -> "_FallbackMobject":
            return self

        def set_fill(self, *_args: Any, **_kwargs: Any) -> "_FallbackMobject":
            return self

        def set_stroke(self, *_args: Any, **_kwargs: Any) -> "_FallbackMobject":
            return self

        def arrange(self, *_args: Any, **_kwargs: Any) -> "_FallbackMobject":
            return self

        def to_edge(self, *_args: Any, **_kwargs: Any) -> "_FallbackMobject":
            return self

        def next_to(self, *_args: Any, **_kwargs: Any) -> "_FallbackMobject":
            return self

    class Scene:  # type: ignore[no-redef]
        """Fallback subset of :class:`manim.Scene` used by fast tests."""

        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            self.mobjects: list[Any] = []
            self._fallback_sections: list[str | None] = []

        def add(self, *mobjects: Any) -> None:
            self.mobjects.extend(mobjects)

        def remove(self, *mobjects: Any) -> None:
            for mobject in mobjects:
                if mobject in self.mobjects:
                    self.mobjects.remove(mobject)

        def play(self, *_animations: Any, **_kwargs: Any) -> None:
            return None

        def wait(self, *_args: Any, **_kwargs: Any) -> None:
            return None

        def next_section(self, name: str | None = None, **_kwargs: Any) -> None:
            self._fallback_sections.append(name)

        def render(self, *_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError("missing local dependency: manim")

    class _FallbackAnimation(_FallbackMobject):
        pass

    class Wait(_FallbackAnimation):  # type: ignore[no-redef]
        pass

    class SVGMobject(_FallbackMobject):  # type: ignore[no-redef]
        pass

    class Text(_FallbackMobject):  # type: ignore[no-redef]
        pass

    class VGroup(_FallbackMobject):  # type: ignore[no-redef]
        def __init__(self, *mobjects: Any, **kwargs: Any) -> None:
            super().__init__(*mobjects, **kwargs)
            self.submobjects = list(mobjects)

    class Circle(_FallbackMobject):  # type: ignore[no-redef]
        pass

    class Dot(_FallbackMobject):  # type: ignore[no-redef]
        pass

    class Line(_FallbackMobject):  # type: ignore[no-redef]
        pass

    class Arrow(_FallbackMobject):  # type: ignore[no-redef]
        pass

    class _FallbackCamera:
        frame_width = 14.222
        frame_height = 8.0

    class _FallbackColor:
        def __init__(self, value: str) -> None:
            self.value = value

    BLACK = _FallbackColor("#000000")  # type: ignore[assignment]
    BLUE = _FallbackColor("#3B82F6")  # type: ignore[assignment]
    GREEN = _FallbackColor("#10B981")  # type: ignore[assignment]
    RED = _FallbackColor("#EF4444")  # type: ignore[assignment]
    WHITE = _FallbackColor("#FFFFFF")  # type: ignore[assignment]

    Create = FadeIn = FadeOut = GrowArrow = Write = _FallbackAnimation  # type: ignore[assignment]

    @contextmanager
    def tempconfig(_config: dict[str, Any]) -> Iterator[None]:  # type: ignore[no-redef]
        yield


ENGINE_ROOT = Path(__file__).resolve().parents[2]
POSE_ROOT = ENGINE_ROOT / "src" / "assets" / "poses"
FONT_ROOT = ENGINE_ROOT / "src" / "assets" / "fonts"

if MANIM_AVAILABLE:  # pragma: no cover - optional render dependency path
    try:
        import manimpango  # type: ignore

        for font_path in (
            FONT_ROOT / "Inter-Variable.ttf",
            FONT_ROOT / "RobotoMono-Variable.ttf",
        ):
            if font_path.is_file():
                manimpango.register_font(str(font_path))
    except Exception:
        # Renderer validation reports missing fonts; importing contracts stays
        # safe on machines without native font registration support.
        pass

DEFAULT_THEME: dict[str, str] = {
    "background_color": "#0B0F14",
    "surface_color": "#151C24",
    "primary_text": "#F4F7FA",
    "accent_color": "#3B82F6",
    "secondary_accent": "#20D69B",
    "defender_accent": "#8B5CF6",
    "active_emphasis": "#FF8A3D",
    "error_color": "#EF5B5B",
    "font": "Inter",
    "measurement_font": "Roboto Mono",
}

DEFAULT_FRAME_CONFIG: dict[str, dict[str, float]] = {
    "landscape": {"frame_width": 14.222, "frame_height": 8.0},
    "vertical": {"frame_width": 8.0, "frame_height": 14.222},
}


def aspect_for_layout(layout: str) -> str:
    """Return ``landscape`` or ``vertical`` for a profile/aspect label."""

    value = str(layout or "landscape").casefold()
    return "vertical" if "vertical" in value or value in {"portrait", "9:16"} else "landscape"


def color_value(value: str | None, fallback: Any = WHITE) -> Any:
    """Resolve a theme color without making fallback tests depend on Manim."""

    if not value:
        return fallback
    if not MANIM_AVAILABLE:
        return value
    # Manim's colour constructors are intentionally imported lazily.  The
    # string is accepted by most mobject APIs, but a Color gives better
    # compatibility across Manim CE versions.
    try:  # pragma: no cover - optional dependency path
        from manim import ManimColor  # type: ignore

        return ManimColor(value)
    except Exception:
        return value


class ThemedScene(Scene):
    """Base scene enforcing layout, theme, and first-motion contracts.

    Subclasses implement :meth:`entrance` and :meth:`body`.  ``construct``
    calls them in that order and records the first ``play`` start.  The first
    animation must begin within 0.5 seconds; this catches static openings
    before a render consumes any provider or compute budget.
    """

    def __init__(
        self,
        scene_spec: dict[str, Any] | None = None,
        layout: str = "landscape",
        audio_duration: float = 0.0,
        theme: dict[str, Any] | None = None,
    ) -> None:
        try:
            super().__init__()
        except TypeError:  # pragma: no cover - version-specific Manim API
            super().__init__(scene_spec=scene_spec)
        self.scene_spec = dict(scene_spec or {})
        self.layout = str(layout or "landscape")
        self.aspect = aspect_for_layout(self.layout)
        self.audio_duration = float(audio_duration or 0.0)
        self.theme = {**DEFAULT_THEME, **dict(theme or {})}
        self.layout_hints = dict(self.scene_spec.get("layout_hints", {}).get(self.aspect, {}))
        self._play_timeline = 0.0
        self._section_start = 0.0
        self._first_animation_start: float | None = None
        self._animation_log: list[dict[str, float]] = []
        self._pace_scale = 1.0
        self._pace_target: float | None = None
        self._active_section_scene_id: int | None = None
        self._ensure_camera_frame()

    def _ensure_camera_frame(self) -> None:
        """Apply profile frame dimensions when a camera is available."""

        frame = DEFAULT_FRAME_CONFIG[self.aspect]
        camera = getattr(self, "camera", None)
        if camera is not None:
            # ``tempconfig`` is authoritative during a real render.  Setting
            # these attributes here also keeps direct scene tests meaningful.
            for name, value in frame.items():
                try:
                    setattr(camera, name, value)
                except Exception:
                    pass

    def _activate_scene(
        self,
        scene_spec: dict[str, Any],
        layout: str | None = None,
        audio_duration: float | None = None,
        theme: dict[str, Any] | None = None,
    ) -> None:
        """Update scene inputs for a continuous sequence render unit."""

        self.scene_spec = dict(scene_spec)
        if layout is not None:
            self.layout = str(layout)
            self.aspect = aspect_for_layout(self.layout)
        if audio_duration is not None:
            self.audio_duration = float(audio_duration)
        if theme is not None:
            self.theme = {**DEFAULT_THEME, **dict(theme)}
        self.layout_hints = dict(self.scene_spec.get("layout_hints", {}).get(self.aspect, {}))
        self._section_start = self._play_timeline
        self._first_animation_start = None
        self._pace_scale = 1.0
        self._pace_target = None
        self._active_section_scene_id = self.scene_spec.get("scene_id")
        self._ensure_camera_frame()

    def play(self, *animations: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        """Track animation starts and apply the active pacing scale."""

        run_time = kwargs.get("run_time")
        if run_time is None:
            run_time = 1.0
        try:
            run_time_f = max(0.0, float(run_time)) * self._pace_scale
        except (TypeError, ValueError):
            run_time_f = 1.0 * self._pace_scale
        kwargs["run_time"] = run_time_f
        relative_start = self._play_timeline - self._section_start
        if self._first_animation_start is None:
            self._first_animation_start = relative_start
        self._animation_log.append(
            {
                "start_s": round(relative_start, 6),
                "run_time_s": round(run_time_f, 6),
            }
        )
        self._play_timeline += run_time_f
        try:
            return super().play(*animations, **kwargs)
        except RuntimeError:
            # The fallback Scene never raises, but this keeps direct contract
            # tests usable with a partially configured Manim renderer.
            if MANIM_AVAILABLE:
                raise
            return None

    def wait(self, duration: float = 1.0, **kwargs: Any) -> Any:  # type: ignore[override]
        try:
            value = max(0.0, float(duration))
        except (TypeError, ValueError):
            value = 0.0
        self._play_timeline += value
        if MANIM_AVAILABLE:
            # ``Scene.wait`` dispatches back through ``self.play``.  Calling
            # it directly would make this class's pacing wrapper replace the
            # requested wait with its default one-second animation.  Bypass
            # that redispatch so the rendered clock matches the tracked clock.
            return super().play(Wait(run_time=value, **kwargs), run_time=value)
        try:
            return super().wait(value, **kwargs)
        except RuntimeError:
            if MANIM_AVAILABLE:
                raise
            return None

    def construct(self) -> None:  # pragma: no cover - tested through subclasses
        entrance = getattr(self, "entrance", None)
        body = getattr(self, "body", None)
        if not callable(entrance) or not callable(body):
            raise TypeError("scene subclasses must implement entrance() and body(audio_duration)")
        entrance()
        if self._first_animation_start is None:
            raise AssertionError("entrance contract violated: no animation started")
        if self._first_animation_start > 0.5:
            raise AssertionError(
                "entrance contract violated: first animation starts "
                f"at {self._first_animation_start:.3f}s (> 0.5s)"
            )
        body(self.audio_duration)

    def entrance(self) -> None:
        raise NotImplementedError

    def body(self, audio_duration: float) -> None:
        raise NotImplementedError

    def pace_to(self, duration: float, *, planned_duration: float | None = None) -> float:
        """Scale subsequent ``play`` run times to the audio clock.

        The public shorthand ``pace_to(duration)`` treats ``duration`` as the
        unscaled animation plan and computes ``audio_duration / duration`` —
        the wording used by the storyboard contract.  Internal scene code can
        pass ``planned_duration`` when it is targeting a section remainder;
        in that form ``duration`` is the desired target and the keyword is the
        unscaled baseline.  The returned ratio is useful for deterministic
        contract tests and beat schedulers.
        """

        if planned_duration is None:
            baseline = float(duration)
            target = self.audio_duration if self.audio_duration > 0 else baseline
        else:
            target = float(duration)
            baseline = float(planned_duration)
        if target <= 0 or baseline <= 0:
            raise ValueError("duration must be positive")
        self._pace_scale = target / float(baseline)
        self._pace_target = target
        return self._pace_scale

    def animation_log(self) -> tuple[dict[str, float], ...]:
        return tuple(self._animation_log)

    def _theme_color(self, key: str, fallback: Any = WHITE) -> Any:
        return color_value(self.theme.get(key), fallback)

    def _theme_font(self, key: str = "font") -> str:
        value = str(self.theme.get(key) or "").strip()
        return "" if not value or value == "default" else value

    def pose_path(self, pose: str) -> Path:
        """Resolve a checked-in SVG pose, rejecting path traversal."""

        name = str(pose).strip()
        if not name or Path(name).name != name or Path(name).suffix:
            raise ValueError(f"invalid pose id: {pose!r}")
        path = POSE_ROOT / f"{name}.svg"
        if not path.is_file():
            raise FileNotFoundError(f"pose asset not found: {name}")
        return path

    def load_pose(self, pose: str) -> Any:
        return SVGMobject(str(self.pose_path(pose)))

    def beat_timings(self) -> list[tuple[int, str, float]]:
        """Resolve beat word indices into measured seconds when available."""

        words = self.scene_spec.get("words") or self.scene_spec.get("word_timings") or []
        resolved: list[tuple[int, str, float]] = []
        for beat in self.scene_spec.get("beats", []) or []:
            try:
                index = int(beat.get("at_word", 0))
            except (TypeError, ValueError):
                index = 0
            when = 0.0
            if words and 0 <= index < len(words):
                item = words[index]
                if isinstance(item, dict):
                    when = float(item.get("start_s", item.get("start", 0.0)) or 0.0)
                elif isinstance(item, (list, tuple)) and len(item) > 1:
                    when = float(item[1])
            resolved.append((index, str(beat.get("action", "")), max(0.0, when)))
        return resolved


__all__ = [
    "Arrow",
    "BLACK",
    "BLUE",
    "Circle",
    "Create",
    "Dot",
    "FadeIn",
    "FadeOut",
    "GREEN",
    "GrowArrow",
    "Line",
    "MANIM_AVAILABLE",
    "FONT_ROOT",
    "POSE_ROOT",
    "RED",
    "SVGMobject",
    "Scene",
    "Text",
    "ThemedScene",
    "VGroup",
    "Wait",
    "WHITE",
    "Write",
    "aspect_for_layout",
    "color_value",
    "tempconfig",
]
