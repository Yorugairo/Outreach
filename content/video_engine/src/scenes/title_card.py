"""Title/CTA card scene."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import FadeIn, Text, ThemedScene, Write


class TitleConceptCard(ThemedScene):
    """Render a high-contrast title or CTA without a static opening."""

    def __init__(
        self,
        scene_spec: dict[str, Any] | None = None,
        layout: str = "landscape",
        audio_duration: float = 0.0,
        theme: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(scene_spec, layout, audio_duration, theme)
        self._headline: Any | None = None

    @property
    def headline(self) -> str:
        params = self.scene_spec.get("parameters") or {}
        return str(
            self.scene_spec.get("on_screen_text")
            or params.get("headline")
            or self.scene_spec.get("narration_text")
            or ""
        )

    def entrance(self) -> None:
        self._headline = Text(
            self.headline,
            color=self._theme_color("primary_text"),
        )
        self.add(self._headline)
        self.play(FadeIn(self._headline), run_time=0.2)

    def body(self, audio_duration: float) -> None:
        total = max(float(audio_duration or self.audio_duration or 1.0), 0.3)
        elapsed = max(0.0, self._play_timeline - self._section_start)
        remaining = max(0.05, total - elapsed)
        # A short write pass after the entrance creates immediate movement;
        # the remaining interval holds the card for the narration clock.
        self.pace_to(remaining, planned_duration=remaining)
        if self._headline is not None:
            self.play(Write(self._headline), run_time=min(0.35, remaining))
        hold = max(0.05, remaining - min(0.35, remaining))
        self.wait(hold)

    @classmethod
    def render_thumbnail(
        cls,
        output_path: str | Path,
        *,
        headline: str,
        concept: str,
        theme: dict[str, Any],
    ) -> Path:
        """Render a deterministic 16:9 still using the title-card visual language."""
        from PIL import Image, ImageDraw, ImageFont

        width, height = 1280, 720
        background = str(theme.get("background_color") or "#0F0F12")
        primary = str(theme.get("primary_text") or "#FFFFFF")
        accent = str(theme.get("accent_color") or "#3B82F6")
        secondary = str(theme.get("secondary_accent") or "#10B981")
        image = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(image)

        def font(*names: str, size: int):
            for name in names:
                try:
                    return ImageFont.truetype(name, size=size)
                except OSError:
                    continue
            return ImageFont.load_default(size=size)

        headline_font = font("DejaVuSans-Bold.ttf", "arialbd.ttf", size=92)
        label_font = font("DejaVuSans-Bold.ttf", "arialbd.ttf", size=28)
        concept_font = font("DejaVuSans.ttf", "arial.ttf", size=30)

        draw.rounded_rectangle((68, 62, 382, 116), radius=14, fill=accent)
        draw.text((92, 72), "COMBAT SCIENCE", font=label_font, fill=primary)

        # A compact lever diagram keeps the thumbnail tied to the title-card
        # scene family without requiring a full Manim render for packaging.
        draw.line((840, 154, 1092, 552), fill=secondary, width=24)
        draw.ellipse((786, 99, 894, 207), fill=accent, outline=primary, width=8)
        draw.ellipse((1038, 498, 1146, 606), fill=secondary, outline=primary, width=8)
        draw.line((734, 598, 1168, 598), fill=primary, width=10)

        words = headline.upper().split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=headline_font)[2] <= 650:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        for index, line in enumerate(lines[:3]):
            draw.text(
                (68, 180 + index * 108),
                line,
                font=headline_font,
                fill=primary,
                stroke_width=2,
                stroke_fill=background,
            )

        if concept:
            draw.text((72, 590), concept[:72], font=concept_font, fill=secondary)

        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.tmp")
        image.save(temporary, format="PNG", optimize=True)
        temporary.replace(destination)
        return destination


__all__ = ["TitleConceptCard"]
