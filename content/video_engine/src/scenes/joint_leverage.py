"""Simple joint-leverage diagram scene."""

from __future__ import annotations

from typing import Any

from .base import Arrow, Circle, FadeIn, GrowArrow, Line, Text, ThemedScene


class JointLeverageScene(ThemedScene):
    """Explain fulcrum/load/effort relationships with deterministic geometry."""

    def __init__(
        self,
        scene_spec: dict[str, Any] | None = None,
        layout: str = "landscape",
        audio_duration: float = 0.0,
        theme: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(scene_spec, layout, audio_duration, theme)
        self._diagram: list[Any] = []

    @property
    def lever(self) -> dict[str, Any]:
        return dict((self.scene_spec.get("parameters") or {}).get("lever") or {})

    def _label(self, value: Any, position: tuple[float, float, float], color: Any) -> Any:
        label = Text(str(value or ""), color=color)
        try:
            label.move_to(position)
        except Exception:
            pass
        return label

    def entrance(self) -> None:
        lever = self.lever
        fulcrum = Circle(radius=0.18, color=self._theme_color("accent_color"))
        bar = Line((-3.0, 0.0, 0.0), (3.0, 0.0, 0.0), color=self._theme_color("primary_text"))
        self._diagram = [bar, fulcrum]
        self.add(bar, fulcrum)
        self.play(FadeIn(bar), run_time=0.2)
        self.add(
            self._label(
                lever.get("fulcrum", "fulcrum"),
                (0.0, -0.6, 0.0),
                self._theme_color("accent_color"),
            )
        )

    def body(self, audio_duration: float) -> None:
        lever = self.lever
        total = max(float(audio_duration or self.audio_duration or 1.0), 0.3)
        elapsed = max(0.0, self._play_timeline - self._section_start)
        remaining = max(0.05, total - elapsed)
        effort_arrow = Arrow(
            (2.1, 1.25, 0.0),
            (2.1, 0.15, 0.0),
            color=self._theme_color("secondary_accent"),
        )
        load_arrow = Arrow(
            (-2.0, 0.15, 0.0),
            (-2.0, 1.1, 0.0),
            color=self._theme_color("accent_color"),
        )
        self.add(effort_arrow, load_arrow)
        arrow_time = min(0.35, remaining / 2)
        self.play(GrowArrow(effort_arrow), run_time=arrow_time)
        self.play(GrowArrow(load_arrow), run_time=arrow_time)
        self.add(
            self._label(
                lever.get("load", "load"),
                (-2.0, 1.45, 0.0),
                self._theme_color("accent_color"),
            ),
            self._label(
                lever.get("effort", "effort"),
                (2.1, 1.55, 0.0),
                self._theme_color("secondary_accent"),
            ),
        )
        spent = arrow_time * 2
        self.wait(max(0.05, remaining - spent))


__all__ = ["JointLeverageScene"]
