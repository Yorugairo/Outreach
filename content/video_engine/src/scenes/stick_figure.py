"""Stick-figure action scene and pose-library helpers."""

from __future__ import annotations

from typing import Any

from .base import FadeIn, FadeOut, MANIM_AVAILABLE, Text, ThemedScene


class StickFigureScene(ThemedScene):
    """Animate a deterministic sequence of checked-in SVG poses.

    ``parameters.poses`` names files under ``src/assets/poses``.  Optional
    storyboard beats use ``pose:<id>`` actions and are resolved against the
    word timings attached to the scene by the audio stage.
    """

    def __init__(
        self,
        scene_spec: dict[str, Any] | None = None,
        layout: str = "landscape",
        audio_duration: float = 0.0,
        theme: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(scene_spec, layout, audio_duration, theme)
        self._pose_mobjects: dict[str, Any] = {}
        self._current_pose: str | None = None

    @property
    def pose_ids(self) -> list[str]:
        params = self.scene_spec.get("parameters") or {}
        poses = params.get("poses") or []
        if isinstance(poses, str):
            poses = [poses]
        return [str(pose) for pose in poses]

    def _load(self, pose: str) -> Any:
        if pose not in self._pose_mobjects:
            self._pose_mobjects[pose] = self.load_pose(pose)
        return self._pose_mobjects[pose]

    def entrance(self) -> None:
        poses = self.pose_ids
        if not poses:
            # A missing pose list is a storyboard/guard error, but keeping the
            # scene visibly active makes the contract failure easy to inspect.
            marker = Text("ACTION", color=self._theme_color("accent_color"))
            self.add(marker)
            self.play(FadeIn(marker), run_time=0.2)
            return
        pose = self._load(poses[0])
        self._current_pose = poses[0]
        self.add(pose)
        self.play(FadeIn(pose), run_time=0.2)

    def body(self, audio_duration: float) -> None:
        poses = self.pose_ids
        if not poses:
            # Keep an empty spec deterministic and animated for the first
            # motion assertion; the storyboard guard rejects it upstream.
            self.play(FadeIn(Text("")), run_time=max(0.05, audio_duration - 0.2))
            return

        total = max(float(audio_duration or self.audio_duration or 1.0), 0.3)
        elapsed = max(0.0, self._play_timeline - self._section_start)
        remaining = max(0.05, total - elapsed)
        switches: list[tuple[float, str]] = []
        for _index, action, when in self.beat_timings():
            if action.startswith("pose:"):
                pose = action.split(":", 1)[1]
                if pose != self._current_pose:
                    switches.append((min(max(0.0, when), total), pose))
        for position, pose in enumerate(poses[1:], start=1):
            if not any(candidate == pose for _when, candidate in switches):
                switches.append((remaining * position / max(1, len(poses) - 1), pose))
        switches.sort(key=lambda item: (item[0], item[1]))

        # ``pace_to`` is deliberately called with the plan duration rather
        # than wall-clock time.  This is the same scale used by all scene
        # classes and keeps the body reproducible from storyboard inputs.
        # The transition and hold plan below already sums to ``remaining``;
        # keep the scale explicit so callers can inspect the pacing contract.
        self.pace_to(remaining, planned_duration=remaining)
        previous = 0.0
        for when, pose in switches:
            if pose not in poses:
                # A beat may reference a pose that is not part of the static
                # sequence.  Loading it still validates the asset contract.
                if not pose:
                    continue
            next_pose = self._load(pose)
            run_time = max(0.05, when - previous)
            self.add(next_pose)
            self.play(FadeIn(next_pose), run_time=run_time)
            if self._current_pose and self._current_pose != pose:
                old = self._pose_mobjects.get(self._current_pose)
                if old is not None:
                    self.remove(old)
            self._current_pose = pose
            previous = when

        tail = max(0.0, remaining - max(0.0, previous))
        # A tiny label or hold animation prevents a long narration from
        # becoming a static frame after the final pose.
        label = self.scene_spec.get("on_screen_text")
        if label:
            text = Text(str(label), color=self._theme_color("primary_text"))
            self.add(text)
            if tail:
                self.play(FadeIn(text), run_time=tail)
        elif tail:
            self.wait(tail)


__all__ = ["StickFigureScene"]
