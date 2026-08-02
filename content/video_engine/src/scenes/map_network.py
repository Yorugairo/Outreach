"""Deterministic map/network overlay scene."""

from __future__ import annotations

from typing import Any

from .base import Create, Dot, FadeIn, Line, Text, ThemedScene


class MapNetworkScene(ThemedScene):
    """Show named nodes and migration/relationship edges from scene parameters."""

    def __init__(
        self,
        scene_spec: dict[str, Any] | None = None,
        layout: str = "landscape",
        audio_duration: float = 0.0,
        theme: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(scene_spec, layout, audio_duration, theme)
        self._nodes: dict[str, Any] = {}

    @property
    def map_data(self) -> dict[str, Any]:
        params = self.scene_spec.get("parameters") or {}
        return dict(params.get("map") or params)

    def _position(self, index: int, total: int) -> tuple[float, float, float]:
        # No random jitter: the same storyboard always produces the same map.
        if total <= 1:
            return (0.0, 0.0, 0.0)
        span = 5.0 if self.aspect == "landscape" else 3.0
        x = -span / 2 + span * (index / max(1, total - 1))
        y = 0.7 if index % 2 == 0 else -0.7
        return (x, y, 0.0)

    def entrance(self) -> None:
        data = self.map_data
        nodes = data.get("nodes") or []
        if isinstance(nodes, dict):
            nodes = list(nodes)
        for index, item in enumerate(nodes):
            if isinstance(item, dict):
                node_id = str(item.get("id") or item.get("name") or index)
                label = str(item.get("name") or node_id)
            else:
                node_id = label = str(item)
            position = self._position(index, len(nodes))
            dot = Dot(position, color=self._theme_color("accent_color"))
            text = Text(
                label,
                color=self._theme_color("primary_text"),
                use_svg_cache=True,
            )
            try:
                text.next_to(dot, direction=(0.0, -1.0, 0.0))
            except Exception:
                pass
            self._nodes[node_id] = dot
            self.add(dot, text)
        if self._nodes:
            self.play(FadeIn(next(iter(self._nodes.values()))), run_time=0.2)
        else:
            marker = Text(
                "NETWORK",
                color=self._theme_color("accent_color"),
                use_svg_cache=True,
            )
            self.add(marker)
            self.play(FadeIn(marker), run_time=0.2)

    def body(self, audio_duration: float) -> None:
        data = self.map_data
        edges = data.get("edges") or data.get("links") or []
        total = max(float(audio_duration or self.audio_duration or 1.0), 0.3)
        elapsed = max(0.0, self._play_timeline - self._section_start)
        remaining = max(0.05, total - elapsed)
        edge_time = remaining / max(1, len(edges))
        for edge in edges:
            if isinstance(edge, dict):
                source = str(edge.get("source") or edge.get("from") or "")
                target = str(edge.get("target") or edge.get("to") or "")
            elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
                source, target = str(edge[0]), str(edge[1])
            else:
                continue
            start = self._nodes.get(source)
            end = self._nodes.get(target)
            if start is None or end is None:
                continue
            line = Line(start, end, color=self._theme_color("secondary_accent"))
            self.add(line)
            self.play(Create(line), run_time=max(0.05, edge_time))
        spent = edge_time * len(edges)
        self.wait(max(0.05, remaining - spent))


__all__ = ["MapNetworkScene"]
