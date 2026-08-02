"""Pre-Gate-A animatic generation from an immutable storyboard draft."""

from __future__ import annotations

import json
import hashlib
import math
import re
import shutil
import subprocess
import textwrap
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from PIL import Image, ImageDraw, ImageFont, ImageOps

from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.services.editorial_beats import (
    compile_editorial_beat_plan,
)
from content.video_engine.src.services.generated_visuals import (
    motion_candidates_by_role,
)
from content.video_engine.src.services.generated_block_images import (
    validate_generated_block_batch,
)
from content.video_engine.src.services.plate_motion import (
    PlateMotionError,
    validate_plate_motion_manifest,
)
from content.video_engine.src.services.editorial_motion import (
    validate_editorial_motion_plan,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


class AnimaticError(RuntimeError):
    """Raised when the local review artifact cannot be produced."""


Runner = Callable[..., subprocess.CompletedProcess[str]]


def _run(runner: Runner, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return runner(
        list(command),
        check=True,
        capture_output=True,
        text=True,
    )


def _json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _contained_file(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise AnimaticError(f"{label} path must be a non-empty string")
    relative = Path(value)
    candidate = relative.resolve() if relative.is_absolute() else (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise AnimaticError(f"{label} path escapes the approved root") from exc
    if not candidate.is_file():
        raise AnimaticError(f"{label} file does not exist")
    return candidate


def _resolve_local_segment(job_dir: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise AnimaticError("Manim segment path must be a non-empty string")
    relative = Path(value)
    if relative.is_absolute():
        raise AnimaticError("Manim segment path must be relative to the job")
    candidate = (job_dir / relative).resolve()
    try:
        candidate.relative_to(job_dir.resolve())
    except ValueError as exc:
        raise AnimaticError(
            f"Manim segment path escapes the job directory: {value}"
        ) from exc
    if candidate.suffix.casefold() != ".mp4":
        raise AnimaticError(f"Manim segment must be an MP4 file: {value}")
    if not candidate.is_file():
        raise AnimaticError(f"Manim segment does not exist: {value}")
    return candidate


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _scene_function(scene: Mapping[str, Any]) -> str:
    parameters = scene.get("parameters") or {}
    if isinstance(parameters, Mapping):
        return str(
            scene.get("visual_function")
            or parameters.get("function")
            or parameters.get("shot_function")
            or scene.get("visual_type")
            or "scene"
        )
    return str(scene.get("visual_function") or scene.get("visual_type") or "scene")


def _scene_camera(scene: Mapping[str, Any]) -> Mapping[str, Any]:
    parameters = scene.get("parameters") or {}
    if isinstance(parameters, Mapping) and isinstance(parameters.get("camera"), Mapping):
        return parameters["camera"]
    return {}


_DOCUMENTARY_ROLE_BY_FUNCTION = {
    "artifact_cold_open": "cold_open",
    "archival_portrait": "archive",
    "illustrated_reconstruction": "illustration",
    "document_quote_closeup": "document",
    "migration_map_timeline": "map_timeline",
    "lineage_graph": "lineage_concept",
    "concept_mechanics_cutaway": "cold_open",
    "chapter_cta": "illustration",
}

_RELATIONSHIP_ENTITIES = (
    "Jigoro Kano",
    "Kano",
    "Kodokan",
    "Mitsuyo Maeda",
    "Maeda",
    "Soshihiro Satake",
    "Satake",
    "Carlos Gracie",
    "Jacyntho Ferro",
    "George Gracie",
    "Lotus Club",
)
_RELATIONSHIP_LABELS = (
    (re.compile(r"\b(?:established|founded)\b", re.IGNORECASE), "FOUNDED"),
    (re.compile(r"\bsenior student\b", re.IGNORECASE), "SENIOR STUDENT"),
    (re.compile(r"\b(?:student|trained|training)\b", re.IGNORECASE), "TRAINING RELATIONSHIP"),
    (re.compile(r"\b(?:taught|teaching|teacher)\b", re.IGNORECASE), "TEACHING RELATIONSHIP"),
    (re.compile(r"\b(?:worked with|partnered with)\b", re.IGNORECASE), "WORKED WITH"),
    (re.compile(r"\b(?:member|joined)\b", re.IGNORECASE), "MEMBERSHIP"),
)


def extract_typed_relationship(value: str) -> dict[str, str] | None:
    """Return a renderer-safe relationship or fail closed.

    A relationship diagram is not a keyword cloud. It needs at least two
    recognized named entities and an explicit relationship phrase in the same
    evidence-bound narration fragment.
    """

    text = " ".join(str(value or "").split())
    if not text:
        return None
    matches: list[tuple[int, str]] = []
    occupied: list[tuple[int, int]] = []
    for entity in sorted(_RELATIONSHIP_ENTITIES, key=len, reverse=True):
        match = re.search(rf"\b{re.escape(entity)}\b", text, re.IGNORECASE)
        if match is None:
            continue
        if any(match.start() < end and match.end() > start for start, end in occupied):
            continue
        occupied.append((match.start(), match.end()))
        matches.append((match.start(), entity))
    matches.sort()
    unique: list[str] = []
    for _, entity in matches:
        canonical = {
            "Kano": "Jigoro Kano",
            "Maeda": "Mitsuyo Maeda",
            "Satake": "Soshihiro Satake",
        }.get(entity, entity)
        if canonical not in unique:
            unique.append(canonical)
    if len(unique) < 2:
        return None
    label = next(
        (
            relationship_label
            for pattern, relationship_label in _RELATIONSHIP_LABELS
            if pattern.search(text)
        ),
        "",
    )
    if not label:
        return None
    return {"source": unique[0], "target": unique[1], "label": label}
_EDITORIAL_STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "because",
    "before",
    "could",
    "does",
    "from",
    "have",
    "into",
    "later",
    "more",
    "other",
    "should",
    "that",
    "their",
    "there",
    "these",
    "they",
    "this",
    "through",
    "under",
    "what",
    "when",
    "where",
    "which",
    "while",
    "with",
    "would",
}
_CONCEPT_VOCABULARY = (
    "education",
    "disciplined practice",
    "efficient use of energy",
    "mutual benefit",
    "techniques",
    "sporting rules",
    "professional contests",
    "educational ideals",
)
_EVIDENCE_FIELD_VOCABULARY = (
    "professional wrestling",
    "prizefighting",
    "Kodokan pedagogical structure",
    "techniques",
    "labels",
    "teaching methods",
    "immigrant teachers",
    "professional fighters",
    "community networks",
    "different regions",
    "forgotten branches",
    "research questions",
)


class AnimaticService:
    """Render storyboard cards, a shot strip, and a local timing preview."""

    def __init__(
        self,
        *,
        runner: Runner = subprocess.run,
        width: int = 854,
        height: int = 480,
        fps: int = 15,
    ) -> None:
        self.runner = runner
        self.width = int(width)
        self.height = int(height)
        self.fps = int(fps)

    def build(
        self,
        storyboard: Mapping[str, Any],
        output_dir: str | Path,
    ) -> dict[str, Any]:
        scenes = list(storyboard.get("scenes") or [])
        if not scenes:
            raise AnimaticError("storyboard has no scenes")
        root = Path(output_dir)
        frames_dir = root / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        theme = (storyboard.get("global_settings") or {}).get("theme") or {}
        background = str(theme.get("background_color") or "#0F0F12")
        primary = str(theme.get("primary_text") or "#FFFFFF")
        accent = str(theme.get("accent_color") or "#3B82F6")
        secondary = str(theme.get("secondary_accent") or "#10B981")

        frame_entries: list[dict[str, Any]] = []
        for scene in scenes:
            scene_id = int(scene["scene_id"])
            target_s = float((scene.get("timing") or {}).get("target_s") or 1.5)
            function = _scene_function(scene)
            parameters = scene.get("parameters") or {}
            action = str(parameters.get("action") or parameters.get("action_id") or "—")
            state_from = str(parameters.get("state_from") or "—")
            state_to = str(parameters.get("state_to") or "—")
            camera = _scene_camera(scene)
            framing = str(camera.get("framing") or camera.get("shot") or "wide")
            narration = str(scene.get("narration_text") or "")
            image = Image.new("RGB", (self.width, self.height), background)
            draw = ImageDraw.Draw(image)
            title_font = _font(30)
            body_font = _font(20)
            small_font = _font(16)

            draw.rectangle((0, 0, self.width, 58), fill=accent)
            draw.text(
                (24, 13),
                f"{scene_id:02d}  {function.replace('_', ' ').upper()}",
                font=title_font,
                fill="#FFFFFF",
            )
            draw.rounded_rectangle(
                (24, 82, self.width - 24, 224),
                radius=18,
                outline=secondary,
                width=4,
            )
            draw.text((46, 100), state_from, font=body_font, fill=primary)
            draw.line(
                (self.width // 2 - 70, 155, self.width // 2 + 70, 155),
                fill=accent,
                width=6,
            )
            draw.polygon(
                [
                    (self.width // 2 + 70, 155),
                    (self.width // 2 + 48, 143),
                    (self.width // 2 + 48, 167),
                ],
                fill=accent,
            )
            draw.text(
                (self.width // 2 - 80, 174),
                action,
                font=small_font,
                fill=secondary,
            )
            state_to_width = draw.textlength(state_to, font=body_font)
            draw.text(
                (self.width - 46 - state_to_width, 100),
                state_to,
                font=body_font,
                fill=primary,
            )
            draw.text(
                (24, 242),
                f"CAMERA  {framing}",
                font=small_font,
                fill=secondary,
            )
            y = 280
            for line in textwrap.wrap(narration, width=72)[:5]:
                draw.text((24, y), line, font=body_font, fill=primary)
                y += 28

            frame_path = frames_dir / f"scene_{scene_id:03d}.png"
            image.save(frame_path)
            frame_entries.append(
                {
                    "scene_id": scene_id,
                    "path": frame_path.relative_to(root).as_posix(),
                    "duration_s": max(1.5, target_s),
                    "function": function,
                    "framing": framing,
                    "action": action,
                    "reference_refs": list(parameters.get("reference_refs") or []),
                }
            )

        strip_path = root / "shot-strip.png"
        self._write_strip(root, frame_entries, strip_path)
        preview_path = root / "preview.mp4"
        concat_path = root / "frames.ffconcat"
        concat_lines = ["ffconcat version 1.0"]
        for entry in frame_entries:
            absolute = (root / entry["path"]).resolve().as_posix().replace("'", "'\\''")
            concat_lines.append(f"file '{absolute}'")
            concat_lines.append(f"duration {float(entry['duration_s']):.6f}")
        last = (root / frame_entries[-1]["path"]).resolve().as_posix().replace("'", "'\\''")
        concat_lines.append(f"file '{last}'")
        concat_path.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
        _run(
            self.runner,
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_path),
                "-vf",
                f"fps={self.fps},format=yuv420p",
                "-c:v",
                "libx264",
                "-movflags",
                "+faststart",
                str(preview_path),
            ],
        )
        if not preview_path.is_file():
            raise AnimaticError("ffmpeg did not produce animatic/preview.mp4")

        packet = {
            "schema_version": "animatic.v1",
            "preview_path": preview_path.relative_to(root.parent).as_posix(),
            "shot_strip_path": strip_path.relative_to(root.parent).as_posix(),
            "scene_count": len(frame_entries),
            "duration_s": round(
                sum(float(entry["duration_s"]) for entry in frame_entries), 3
            ),
            "functions": [entry["function"] for entry in frame_entries],
            "shots": frame_entries,
            "provider_calls": 0,
            "approval_granted": False,
        }
        _json(root / "review-packet.json", packet)
        return packet

    def _write_strip(
        self,
        root: Path,
        entries: list[dict[str, Any]],
        output_path: Path,
    ) -> None:
        thumb_width = 320
        thumb_height = round(thumb_width * self.height / self.width)
        columns = min(3, len(entries))
        rows = math.ceil(len(entries) / columns)
        canvas = Image.new("RGB", (columns * thumb_width, rows * thumb_height), "#000000")
        for index, entry in enumerate(entries):
            image = Image.open(root / entry["path"]).convert("RGB")
            image.thumbnail((thumb_width, thumb_height))
            x = (index % columns) * thumb_width
            y = (index // columns) * thumb_height
            canvas.paste(image, (x, y))
        canvas.save(output_path)

    def _documentary_frame(
        self,
        source: Path,
        scene: Mapping[str, Any],
        output: Path,
        *,
        beat: Mapping[str, Any] | None = None,
        beat_index: int = 0,
        beat_count: int = 1,
        generated_role: str | None = None,
        transparent_overlay: bool = False,
    ) -> None:
        intent = str((beat or {}).get("visual_intent") or "")
        function_name = str(
            (beat or {}).get("function") or _scene_function(scene)
        )
        excerpt = str(
            (beat or {}).get("narration_excerpt")
            or scene.get("narration_text")
            or ""
        ).strip()
        with Image.open(source) as opened:
            world = ImageOps.fit(
                opened.convert("RGB"),
                (self.width, self.height),
                method=Image.Resampling.LANCZOS,
            )
        if generated_role == "generated_block":
            # Generated plates are complete editorial worlds. Keep their
            # composition intact and add only evidence-safe post overlays;
            # do not replace them with a deterministic legacy folio.
            image = world
        elif generated_role == "map_timeline":
            image = self._migration_world_frame(world, excerpt, beat_index)
        elif generated_role == "lineage_concept":
            image = self._lineage_scroll_frame(world, excerpt, beat_index)
        elif generated_role == "concept_mechanics":
            image = self._concept_world_frame(world, excerpt, beat_index)
        elif intent == "battlefield_legend":
            image = self._cold_open_world_frame(world, 0)
        elif intent == "tranquil_institution":
            image = self._cold_open_world_frame(world, 1)
        elif intent == "lofi_editorial_aside":
            image = self._lofi_editorial_aside_frame(excerpt, beat_index)
        elif function_name == "artifact_cold_open":
            image = self._cold_open_world_frame(world, beat_index)
        elif function_name == "migration_map_timeline":
            image = self._migration_context_frame(world, excerpt, beat_index)
        elif function_name == "lineage_graph":
            image = self._lineage_context_frame(world, excerpt, beat_index)
        elif function_name == "document_quote_closeup":
            image = self._document_context_frame(world, excerpt, beat_index)
        elif function_name == "concept_mechanics_cutaway":
            institution_world = self._cold_open_world_frame(world, 1)
            image = self._concept_context_frame(
                institution_world,
                excerpt,
                beat_index,
            )
        elif function_name == "chapter_cta":
            image = self._chapter_context_frame(world, excerpt, beat_index)
        elif function_name == "archival_portrait" and source.suffix.casefold() in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        } and "style_board" not in source.as_posix():
            image = self._archive_context_frame(source, excerpt)
        else:
            image = world
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        label_font = _font(18)
        body_font = _font(19)
        source_font = _font(13)
        function = function_name.replace("_", " ").upper()
        scene_id = int(scene["scene_id"])
        narration = excerpt
        summary_lines = textwrap.wrap(narration, width=72)[:2]
        citation_ids = [
            str(value).removeprefix("citation-").replace("-", " ").upper()
            for value in list(
                (beat or {}).get("citation_refs")
                or scene.get("citation_refs")
                or []
            )[:2]
        ]
        draw.rounded_rectangle(
            (18, 16, min(self.width - 18, 430), 52),
            radius=8,
            fill=(11, 15, 20, 220),
        )
        draw.text(
            (32, 25),
            (
                f"SCENE {scene_id:02d}  /  CUT {beat_index + 1:02d}"
                f" OF {beat_count:02d}  /  {function}"
            ),
            fill="#F4F7FA",
            font=label_font,
        )
        illustration_label = str(
            (beat or {}).get("illustration_label") or ""
        )
        if illustration_label:
            draw.rounded_rectangle(
                (18, 62, 398, 91),
                radius=5,
                fill=(164, 74, 50, 235),
            )
            draw.text(
                (30, 68),
                illustration_label,
                fill="#F4EBDD",
                font=source_font,
            )
        lower_top = self.height - 112
        draw.rectangle(
            (0, lower_top, self.width, self.height),
            fill=(11, 15, 20, 225),
        )
        y = lower_top + 14
        for line in summary_lines:
            draw.text((26, y), line, fill="#F4F7FA", font=body_font)
            y += 25
        draw.text(
            (26, self.height - 24),
            "SOURCE  " + ("  •  ".join(citation_ids) or "EDITORIAL CTA"),
            fill="#20D69B",
            font=source_font,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        if transparent_overlay:
            overlay.save(output, format="PNG")
        else:
            Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB").save(
                output,
                format="PNG",
            )

    def _cold_open_world_frame(
        self,
        world: Image.Image,
        variant: int,
    ) -> Image.Image:
        """Turn the approved contrast spread into sentence-level cuts.

        The approved cold-open still contains a mythic battlefield on the left
        and an institutional reconstruction on the right. Alternating the two
        halves gives the opening sentence a real visual contrast without
        resolving an unapproved generated source.
        """

        width, height = world.size
        mode = variant % 3
        if mode == 2:
            return world.copy()
        split = max(1, width // 2)
        focus = world.crop(
            (0, 0, split, height)
            if mode == 0
            else (split, 0, width, height)
        )
        background = ImageOps.fit(
            focus,
            (self.width, self.height),
            method=Image.Resampling.LANCZOS,
        ).convert("RGBA")
        wash = Image.new("RGBA", background.size, (11, 15, 20, 118))
        background = Image.alpha_composite(background, wash)
        foreground = ImageOps.contain(
            focus,
            (round(self.width * 0.72), self.height),
            method=Image.Resampling.LANCZOS,
        ).convert("RGBA")
        x = (self.width - foreground.width) // 2
        background.alpha_composite(foreground, (x, 0))
        draw = ImageDraw.Draw(background)
        accent = "#A44A32" if mode == 0 else "#20D69B"
        draw.rectangle((x - 6, 0, x, self.height), fill=accent)
        draw.rectangle(
            (x + foreground.width, 0, x + foreground.width + 6, self.height),
            fill=accent,
        )
        return background.convert("RGB")

    def _battlefield_contrast_frame(self) -> Image.Image:
        image = Image.new("RGB", (self.width, self.height), "#251515")
        draw = ImageDraw.Draw(image)
        for y in range(self.height):
            ratio = y / max(1, self.height - 1)
            color = (
                round(52 + 43 * ratio),
                round(26 + 11 * ratio),
                round(25 + 8 * ratio),
            )
            draw.line((0, y, self.width, y), fill=color)
        draw.ellipse((570, 64, 760, 254), fill="#A44A32")
        draw.rectangle((0, 300, self.width, self.height), fill="#1B1718")
        for index, x in enumerate((80, 190, 310, 450, 595, 715, 810)):
            ground = 368 + (index % 3) * 13
            scale = 0.75 + (index % 2) * 0.18
            head = round(18 * scale)
            draw.ellipse(
                (x - head, ground - 116, x + head, ground - 80),
                fill="#080A0C",
            )
            draw.polygon(
                [
                    (x, ground - 134),
                    (x - 31 * scale, ground - 102),
                    (x + 31 * scale, ground - 102),
                ],
                fill="#080A0C",
            )
            draw.polygon(
                [
                    (x - 39 * scale, ground - 82),
                    (x + 39 * scale, ground - 82),
                    (x + 54 * scale, ground),
                    (x - 54 * scale, ground),
                ],
                fill="#0B0F14",
            )
            spear_x = x + (30 if index % 2 else -28)
            draw.line(
                (spear_x, ground - 155, spear_x + 42, ground + 8),
                fill="#E7D8C2",
                width=4,
            )
        for x, y, radius in (
            (145, 417, 21),
            (365, 431, 14),
            (655, 409, 26),
            (760, 448, 17),
        ):
            draw.ellipse(
                (x - radius, y - radius // 3, x + radius, y + radius // 3),
                fill="#7C2524",
            )
        draw.text(
            (35, 112),
            "BATTLEFIELD LEGEND",
            fill="#F4EBDD",
            font=_font(42),
        )
        draw.text(
            (38, 164),
            "the mythic origin we are testing",
            fill="#DABEA8",
            font=_font(23),
        )
        return image

    @staticmethod
    def _editorial_keywords(value: str, *, limit: int = 5) -> list[str]:
        words = re.findall(r"\b[A-Za-z][A-Za-z'-]{3,}\b", value)
        result: list[str] = []
        for word in words:
            lowered = word.casefold()
            if lowered in _EDITORIAL_STOPWORDS or lowered in {
                item.casefold() for item in result
            }:
                continue
            result.append(word)
            if len(result) == limit:
                break
        return result or ["Evidence", "Context", "Change"]

    def _semantic_terms(
        self,
        value: str,
        vocabulary: Sequence[str],
        *,
        limit: int,
    ) -> list[str]:
        lowered = value.casefold()
        matched = sorted(
            (
                (lowered.find(term.casefold()), term)
                for term in vocabulary
                if term.casefold() in lowered
            ),
            key=lambda item: item[0],
        )
        result = [term for _, term in matched[:limit]]
        if len(result) < limit:
            for keyword in self._editorial_keywords(value, limit=limit):
                if any(
                    keyword.casefold() in term.casefold()
                    or term.casefold() in keyword.casefold()
                    for term in result
                ):
                    continue
                result.append(keyword)
                if len(result) == limit:
                    break
        return result[:limit]

    def _archive_context_frame(
        self,
        source: Path,
        excerpt: str,
    ) -> Image.Image:
        image = Image.new("RGB", (self.width, self.height), "#11171D")
        with Image.open(source) as opened:
            portrait = ImageOps.contain(
                opened.convert("RGB"),
                (round(self.width * 0.48), self.height),
                method=Image.Resampling.LANCZOS,
            )
        image.paste(
            portrait,
            (self.width - portrait.width - 34, 0),
        )
        draw = ImageDraw.Draw(image)
        keywords = self._editorial_keywords(excerpt, limit=3)
        draw.rectangle((0, 0, 410, self.height), fill="#151C24")
        draw.rectangle((405, 0, 412, self.height), fill="#20D69B")
        draw.text((34, 112), "ARCHIVE / PERSON", fill="#20D69B", font=_font(18))
        title = "\n".join(textwrap.wrap(" ".join(keywords), width=19)[:3])
        draw.multiline_text(
            (34, 158),
            title.upper(),
            fill="#F4F7FA",
            font=_font(34),
            spacing=4,
        )
        return image

    def _migration_world_frame(
        self,
        world: Image.Image,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        """Use the generated travel world as atmosphere, not as a map source.

        The plate supplies the period paper, ports, ship, and composition. The
        route, place labels, dates, and citation rail are authored here from
        the reviewed narration so generated geography cannot become evidence.
        """

        image = world.copy().convert("RGBA")
        draw = ImageDraw.Draw(image)
        places = [
            place
            for place in ("Japan", "Americas", "Brazil", "Belém", "Rio", "São Paulo")
            if place.casefold() in excerpt.casefold()
        ]
        if len(places) < 2:
            places = ["Japan", "global circuit", "Brazil"]
        places = places[:3]
        dates = re.findall(r"\b(?:18|19|20)\d{2}\b", excerpt)[:3]
        draw.rectangle((22, 20, self.width - 22, 66), fill=(11, 15, 20, 196))
        draw.text(
            (38, 32),
            "GENERATED TRAVEL WORLD  /  REVIEWED ROUTE OVERLAY",
            fill="#F4F7FA",
            font=_font(15),
        )
        points = [
            (round(self.width * 0.20), round(self.height * 0.37)),
            (round(self.width * 0.50), round(self.height * 0.37) + (12 if variant % 2 else 0)),
            (round(self.width * 0.80), round(self.height * 0.37)),
        ][: len(places)]
        if len(points) > 1:
            draw.line(points, fill="#20D69B", width=4, joint="curve")
        for index, ((x, y), place) in enumerate(zip(points, places)):
            radius = 16
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill="#A44A32", outline="#F4EBDD", width=3)
            label = place.upper()
            draw.rounded_rectangle((x - 72, y + 22, x + 72, y + 47), radius=4, fill=(11, 15, 20, 218))
            draw.text((x, y + 34), label, fill="#F4F7FA", font=_font(13), anchor="mm")
            if index < len(dates):
                draw.text((x, y - 32), dates[index], fill="#FF8A3D", font=_font(14), anchor="mm")
        draw.rectangle((24, self.height - 70, self.width - 24, self.height - 22), fill=(244, 235, 215, 232))
        draw.text(
            (self.width // 2, self.height - 46),
            "THE PLATE SETS THE TONE. THE RECORD SETS THE ROUTE.",
            fill="#1F252A",
            font=_font(15),
            anchor="mm",
        )
        return image.convert("RGB")

    def _lineage_scroll_frame(
        self,
        world: Image.Image,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        """Turn a generated lineage scroll into a legible evidence prompt."""

        image = world.copy().convert("RGBA")
        draw = ImageDraw.Draw(image)
        relationship = extract_typed_relationship(excerpt)
        if relationship is not None:
            labels = (
                relationship["source"],
                relationship["target"],
                "RECORDED BRANCH",
            )
            cartouche = relationship["label"]
        else:
            labels = ("INSTITUTION", "TEACHING NETWORK", "RESEARCH QUESTION")
            cartouche = "NO SOURCED VERB — DO NOT DRAW AN ARROW"
        centers = (
            (round(self.width * 0.50), round(self.height * 0.28)),
            (round(self.width * 0.31), round(self.height * 0.62)),
            (round(self.width * 0.69), round(self.height * 0.62)),
        )
        draw.rectangle((22, 18, self.width - 22, 64), fill=(11, 15, 20, 200))
        draw.text(
            (38, 30),
            "WOODBLOCK LINEAGE SCROLL  /  RELATIONSHIPS, NOT MYTHIC BLOODLINES",
            fill="#F4F7FA",
            font=_font(14),
        )
        for index, (center, label) in enumerate(zip(centers, labels)):
            x, y = center
            ring = "#20D69B" if index == variant % 3 else "#F4EBDD"
            draw.ellipse((x - 86, y - 30, x + 86, y + 30), outline=ring, width=3)
            draw.rounded_rectangle((x - 76, y - 20, x + 76, y + 20), radius=5, fill=(23, 28, 32, 210))
            draw.text(
                (x, y),
                textwrap.shorten(label.upper(), width=22, placeholder="…"),
                fill="#F4F7FA",
                font=_font(13),
                anchor="mm",
            )
        draw.rectangle((round(self.width * 0.24), self.height - 72, round(self.width * 0.76), self.height - 22), fill=(244, 235, 215, 236), outline="#A44A32", width=2)
        draw.text(
            (self.width // 2, self.height - 47),
            textwrap.shorten(cartouche, width=62, placeholder="…"),
            fill="#1F252A",
            font=_font(14),
            anchor="mm",
        )
        return image.convert("RGB")

    def _concept_world_frame(
        self,
        world: Image.Image,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        """Use the generated lever scene to explain adaptation, not technique."""

        image = world.copy().convert("RGBA")
        draw = ImageDraw.Draw(image)
        draw.rectangle((24, 28, round(self.width * 0.36), self.height - 82), fill=(11, 15, 20, 216), outline="#A44A32", width=2)
        draw.text((42, 48), "CONCEPT / ADAPTATION", fill="#20D69B", font=_font(15))
        draw.multiline_text(
            (42, 84),
            "A SYSTEM\nCHANGES\nIN CONTEXT.",
            fill="#F4F7FA",
            font=_font(28),
            spacing=4,
        )
        terms = self._semantic_terms(excerpt, _CONCEPT_VOCABULARY, limit=3)
        for index, term in enumerate(terms):
            y = self.height - 182 + index * 30
            draw.text((42, y), f"{index + 1}. {textwrap.shorten(term, width=24, placeholder='…').upper()}", fill="#F4D35E", font=_font(13))
        draw.rectangle((24, self.height - 64, self.width - 24, self.height - 22), fill=(244, 235, 215, 230))
        draw.text(
            (self.width // 2, self.height - 43),
            "ILLUSTRATION EXPLAINS AN IDEA; IT IS NOT A TECHNIQUE DEMO.",
            fill="#1F252A",
            font=_font(13),
            anchor="mm",
        )
        return image.convert("RGB")

    def _migration_context_frame(
        self,
        world: Image.Image,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        image = world.copy().convert("RGBA")
        wash = Image.new("RGBA", image.size, (11, 15, 20, 54))
        image = Image.alpha_composite(image, wash)
        draw = ImageDraw.Draw(image)
        known_places = (
            "Japan",
            "Americas",
            "Brazil",
            "Belém",
            "Rio",
            "São Paulo",
        )
        places = [
            place
            for place in known_places
            if place.casefold() in excerpt.casefold()
        ]
        if len(places) < 2:
            defaults = (
                ("Japan", "global circuit", "Brazil"),
                ("Belém", "Rio", "Brazil"),
                ("Japan", "Americas", "Belém"),
            )[variant % 3]
            places = list(defaults)
        dates = re.findall(r"\b(?:18|19|20)\d{2}\b", excerpt)
        draw.rounded_rectangle(
            (24, 74, self.width - 24, 168),
            radius=8,
            fill=(11, 15, 20, 214),
        )
        draw.text((42, 90), "MOVEMENT / PLACE / TIME", fill="#20D69B", font=_font(18))
        headline = " → ".join(places[:3])
        draw.text((42, 124), headline.upper(), fill="#F4F7FA", font=_font(30))
        baseline = 304
        left = 92
        right = self.width - 92
        points = [
            (
                round(left + index * (right - left) / max(1, len(places[:3]) - 1)),
                baseline - (44 if (index + variant) % 2 else 0),
            )
            for index in range(len(places[:3]))
        ]
        for index, (x, y) in enumerate(points):
            if index:
                previous = points[index - 1]
                draw.line((*previous, x, y), fill="#20D69B", width=5)
            draw.ellipse((x - 13, y - 13, x + 13, y + 13), fill="#FF8A3D", outline="#F4F7FA", width=3)
            draw.text(
                (x - 42, y + 25),
                places[index].upper(),
                fill="#F4F7FA",
                font=_font(14),
            )
        if dates:
            draw.rounded_rectangle((650, 82, 820, 130), radius=8, fill="#A44A32")
            draw.text((678, 94), " / ".join(dates[:2]), fill="#F4EBDD", font=_font(20))
        return image.convert("RGB")

    def _lineage_context_frame(
        self,
        world: Image.Image,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        relationship = extract_typed_relationship(excerpt)
        if relationship is None:
            return self._evidence_field_frame(world, excerpt, variant)
        image = world.copy().convert("RGBA")
        image = Image.alpha_composite(
            image,
            Image.new("RGBA", image.size, (244, 235, 215, 224)),
        )
        draw = ImageDraw.Draw(image)
        draw.text((34, 88), "A RELATIONSHIP NEEDS A VERB", fill="#2C7666", font=_font(18))
        positions = ((220, 250), (640, 250))
        for index, ((x, y), label) in enumerate(
            zip(
                positions,
                (relationship["source"], relationship["target"]),
            )
        ):
            width = 220
            draw.rounded_rectangle(
                (x - width // 2, y - 34, x + width // 2, y + 34),
                radius=10,
                fill="#151C24" if index else "#324C73",
                outline="#F4F7FA",
                width=3,
            )
            fitted = textwrap.shorten(label, width=20, placeholder="…")
            draw.text(
                (x, y),
                fitted,
                fill="#F4F7FA",
                font=_font(16),
                anchor="mm",
            )
        draw.line((338, 250, 522, 250), fill="#20D69B", width=5)
        draw.polygon(
            [(522, 250), (505, 241), (505, 259)],
            fill="#20D69B",
        )
        label_width = 230
        draw.rounded_rectangle(
            (
                self.width // 2 - label_width // 2,
                222,
                self.width // 2 + label_width // 2,
                278,
            ),
            radius=7,
            fill="#F4EBDD",
            outline="#20D69B",
            width=2,
        )
        draw.text(
            (self.width // 2, 250),
            relationship["label"],
            fill="#1F252A",
            font=_font(15),
                anchor="mm",
            )
        return image.convert("RGB")

    def _evidence_field_frame(
        self,
        world: Image.Image,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        """Render a sourced evidence field when narration supports no edge."""

        image = world.copy().convert("RGBA")
        image = Image.alpha_composite(
            image,
            Image.new("RGBA", image.size, (244, 235, 215, 232)),
        )
        draw = ImageDraw.Draw(image)
        draw.text(
            (38, 82),
            "A FIELD, NOT A SINGLE ARROW.",
            fill="#1F252A",
            font=_font(34),
        )
        draw.text(
            (40, 126),
            "No relationship is drawn unless the record supplies names and a verb.",
            fill="#A44A32",
            font=_font(17),
        )
        terms = self._semantic_terms(
            excerpt,
            _EVIDENCE_FIELD_VOCABULARY,
            limit=4,
        )
        positions = (
            (152, 242),
            (426, 214 + (8 if variant % 2 else -8)),
            (702, 260),
            (426, 342),
        )
        colors = ("#324C73", "#C18B45", "#A44A32", "#2C7666")
        for index, term in enumerate(terms[:4]):
            x, y = positions[index]
            draw.rounded_rectangle(
                (x - 102, y - 34, x + 102, y + 34),
                radius=8,
                fill=colors[index],
                outline="#1F252A",
                width=3,
            )
            draw.text(
                (x, y),
                textwrap.shorten(term, width=18, placeholder="…").upper(),
                fill="#F4F7FA",
                font=_font(16),
                anchor="mm",
            )
        draw.text(
            (38, 414),
            "RELATIONSHIP STATUS  /  UNASSERTED",
            fill="#A44A32",
            font=_font(15),
        )
        return image.convert("RGB")

    def _lofi_relationship_fallback_frame(
        self,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        """Use an authored aside when narration cannot support a graph."""

        image = Image.new("RGB", (self.width, self.height), "#F1E3C5")
        draw = ImageDraw.Draw(image)
        jitter = 4 if variant % 2 else -4
        draw.text((35, 78), "AUTO-GRAPH HAD ONE JOB.", fill="#171A1D", font=_font(34))
        boxes = ((125, 220, "word"), (430, 170 + jitter, "other word"), (710, 260, "vibes"))
        for x, y, label in boxes:
            draw.rounded_rectangle(
                (x - 82, y - 30, x + 82, y + 30),
                radius=5,
                fill="#D9C59F",
                outline="#171A1D",
                width=3,
            )
            draw.text((x, y), label, fill="#171A1D", font=_font(16), anchor="mm")
        draw.line((205, 220, 350, 178 + jitter), fill="#171A1D", width=3)
        draw.line((512, 180 + jitter, 628, 250), fill="#171A1D", width=3)
        draw.line((78, 135, 770, 350), fill="#D7533F", width=12)
        draw.line((770, 135, 78, 350), fill="#D7533F", width=12)
        draw.rectangle((35, 372, self.width - 35, 430), fill="#171A1D")
        draw.text(
            (52, 389),
            "NO TWO NAMES + NO SOURCED VERB = NO RELATIONSHIP GRAPH",
            fill="#F1E3C5",
            font=_font(18),
        )
        short = textwrap.shorten(excerpt, width=78, placeholder="…")
        draw.text((38, 447), short, fill="#304F78", font=_font(15))
        return image

    def _lofi_editorial_aside_frame(
        self,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        """Render a cheap, readable joke instead of manufacturing a diagram."""

        image = Image.new("RGB", (self.width, self.height), "#F1E3C5")
        draw = ImageDraw.Draw(image)
        wobble = 5 if variant % 2 else -5
        draw.rectangle((44, 66, self.width - 44, 410), fill="#E2CDA5", outline="#171A1D", width=4)
        draw.text((72, 92), "HISTORY SHORTCUT™", fill="#171A1D", font=_font(32))
        # A literal date stamp tries, and fails, to swallow everything before it.
        draw.ellipse((120, 180 + wobble, 250, 310 + wobble), fill="#F4D35E", outline="#171A1D", width=4)
        draw.text((185, 245 + wobble), "1882", fill="#171A1D", font=_font(27), anchor="mm")
        draw.rectangle((520, 185 - wobble, 735, 304 - wobble), fill="#304F78", outline="#171A1D", width=4)
        draw.text((627, 220 - wobble), "EVERYTHING", fill="#F1E3C5", font=_font(20), anchor="mm")
        draw.text((627, 262 - wobble), "BEFORE IT", fill="#F1E3C5", font=_font(20), anchor="mm")
        draw.line((270, 244, 500, 244), fill="#171A1D", width=5)
        draw.polygon([(500, 244), (480, 232), (480, 256)], fill="#171A1D")
        draw.line((93, 154, 773, 344), fill="#D7533F", width=12)
        draw.text((82, 352), "No. A date marks a claim—not the whole past.", fill="#B54832", font=_font(23))
        short = textwrap.shorten(excerpt, width=82, placeholder="…")
        draw.text((47, 438), short, fill="#304F78", font=_font(15))
        return image

    def _document_context_frame(
        self,
        world: Image.Image,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        image = world.copy().convert("RGBA")
        image = Image.alpha_composite(
            image,
            Image.new("RGBA", image.size, (11, 15, 20, 42)),
        )
        draw = ImageDraw.Draw(image)
        paper = "#F5EBD7"
        panel = (
            (388, 72, 824, 352)
            if variant % 2
            else (30, 72, 466, 352)
        )
        draw.rounded_rectangle(
            panel,
            radius=7,
            fill=paper,
            outline="#302D2B",
            width=4,
        )
        left, top, right, bottom = panel
        draw.text(
            (left + 26, top + 24),
            "WHAT DOES THE RECORD SUPPORT?",
            fill="#A44A32",
            font=_font(18),
        )
        lines = textwrap.wrap(excerpt, width=36)[:5]
        for index, line in enumerate(lines):
            y = top + 72 + index * 36
            if index == variant % max(1, len(lines)):
                draw.rounded_rectangle(
                    (left + 18, y - 4, right - 18, y + 28),
                    radius=4,
                    fill="#F2BE73",
                )
            draw.text((left + 28, y), line, fill="#1F252A", font=_font(17))
        draw.text(
            (right - 132, bottom - 28),
            "SOURCE CHECK",
            fill="#324C73",
            font=_font(14),
        )
        return image.convert("RGB")

    def _concept_context_frame(
        self,
        world: Image.Image,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        image = world.copy().convert("RGBA")
        image = Image.alpha_composite(
            image,
            Image.new("RGBA", image.size, (11, 15, 20, 178)),
        )
        draw = ImageDraw.Draw(image)
        keywords = self._semantic_terms(
            excerpt,
            _CONCEPT_VOCABULARY,
            limit=4,
        )
        draw.text((34, 86), "CONCEPT LENS / NOT A LINEAGE", fill="#20D69B", font=_font(18))
        title = "\n".join(
            textwrap.wrap(
                textwrap.shorten(excerpt, width=78, placeholder="…"),
                width=42,
            )[:2]
        )
        draw.multiline_text(
            (34, 126),
            title,
            fill="#F4F7FA",
            font=_font(30),
            spacing=6,
        )
        x_positions = (145, 380, 615, 770)
        colors = ("#324C73", "#C18B45", "#A44A32")
        for index, x in enumerate(x_positions[: len(keywords)]):
            label = keywords[index % len(keywords)]
            draw.rounded_rectangle(
                (x - 78, 286, x + 78, 348),
                radius=31,
                fill=colors[(index + variant) % len(colors)],
                outline="#F4F7FA",
                width=3,
            )
            draw.text(
                (x, 317),
                textwrap.shorten(label, width=16, placeholder="…"),
                fill="#F4F7FA",
                font=_font(16),
                anchor="mm",
            )
        draw.text(
            (34, 380),
            "Parallel ideas are grouped; no causal arrow is implied.",
            fill="#C8D1D8",
            font=_font(15),
        )
        return image.convert("RGB")

    def _chapter_context_frame(
        self,
        world: Image.Image,
        excerpt: str,
        variant: int,
    ) -> Image.Image:
        image = world.copy().convert("RGBA")
        image = Image.alpha_composite(
            image,
            Image.new("RGBA", image.size, (11, 15, 20, 176)),
        )
        draw = ImageDraw.Draw(image)
        accent = "#FF8A3D" if variant % 2 else "#20D69B"
        draw.rectangle((38, 72, 46, 344), fill=accent)
        draw.text(
            (72, 88),
            "COMBAT HISTORY / CHAPTER CLOSE",
            fill=accent,
            font=_font(17),
        )
        headline = "\n".join(
            textwrap.wrap(
                textwrap.shorten(excerpt, width=112, placeholder="…"),
                width=34,
            )[:4]
        )
        draw.multiline_text(
            (72, 132),
            headline.upper(),
            fill="#F4F7FA",
            font=_font(34),
            spacing=8,
        )
        draw.text(
            (72, 370),
            "THE RECORD CHANGES THE STORY.",
            fill="#F4EBDD",
            font=_font(16),
        )
        return image.convert("RGB")

    def _tranquil_institution_frame(self) -> Image.Image:
        image = Image.new("RGB", (self.width, self.height), "#EADDC7")
        draw = ImageDraw.Draw(image)
        draw.ellipse((600, 55, 770, 225), fill="#C7684D")
        draw.rectangle((0, 330, self.width, self.height), fill="#C8B48F")
        draw.polygon(
            [(145, 285), (427, 180), (709, 285), (650, 307), (204, 307)],
            fill="#302D2B",
        )
        draw.polygon(
            [(195, 324), (427, 238), (659, 324), (620, 339), (234, 339)],
            fill="#5A4A3B",
        )
        draw.rectangle((224, 304, 630, 432), fill="#F4EBDD", outline="#302D2B", width=6)
        for x in (278, 370, 462, 554):
            draw.rectangle((x, 326, x + 45, 432), fill="#D9C6A5", outline="#5A4A3B", width=3)
        for x in range(0, self.width, 84):
            draw.line((427, 432, x, self.height), fill="#8E7A5C", width=2)
        draw.text(
            (40, 106),
            "AN INSTITUTION",
            fill="#1F252A",
            font=_font(46),
        )
        draw.text(
            (43, 160),
            "a durable home for teaching",
            fill="#5A4A3B",
            font=_font(24),
        )
        return image

    def _write_editorial_contact_sheet(
        self,
        frames: list[Path],
        output: Path,
    ) -> None:
        thumb_width = 256
        thumb_height = round(thumb_width * self.height / self.width)
        columns = 4
        rows = math.ceil(len(frames) / columns)
        canvas = Image.new(
            "RGB",
            (columns * thumb_width, rows * thumb_height),
            "#0B0F14",
        )
        for index, frame in enumerate(frames):
            with Image.open(frame) as opened:
                image = ImageOps.fit(
                    opened.convert("RGB"),
                    (thumb_width, thumb_height),
                    method=Image.Resampling.LANCZOS,
                )
            canvas.paste(
                image,
                (
                    (index % columns) * thumb_width,
                    (index // columns) * thumb_height,
                ),
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output, format="PNG")

    @staticmethod
    def _zoompan_filter(
        motion: str,
        frames: int,
        width: int,
        height: int,
        fps: int,
    ) -> str:
        divisor = max(1, frames - 1)
        if motion in {"pan_left", "masked_reveal", "paper_transition"}:
            movement = (
                "z='1.07':x='(iw-iw/zoom)*(on/"
                f"{divisor})':y='ih/2-(ih/zoom/2)'"
            )
        elif motion in {"pan_right", "map_trace", "split_compare"}:
            movement = (
                "z='1.07':x='(iw-iw/zoom)*(1-on/"
                f"{divisor})':y='ih/2-(ih/zoom/2)'"
            )
        elif motion in {"lift", "type_build", "comic_pop"}:
            movement = (
                "z='1.06':x='iw/2-(iw/zoom/2)':"
                f"y='(ih-ih/zoom)*(1-on/{divisor})'"
            )
        elif motion in {"pull_back", "evidence_highlight"}:
            movement = (
                "z='if(eq(on,1),1.08,max(zoom-0.00022,1.0))':"
                "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            )
        else:  # push_in, parallax_push, detail_punch
            movement = (
                "z='min(zoom+0.00022,1.08)':"
                "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            )
        return (
            f"zoompan={movement}:d={frames}:"
            f"s={width}x{height}:fps={fps},format=yuv420p"
        )

    def _render_documentary_motion(
        self,
        storyboard: Mapping[str, Any],
        job_dir: Path,
        packet: dict[str, Any],
        *,
        project_root: str | Path | None = None,
        style_board_path: Path | None = None,
        generated_visuals_path: Path | None = None,
        generated_block_batch_path: Path | None = None,
        plate_motion_manifest_path: Path | None = None,
        output_root: Path | None = None,
    ) -> dict[str, Any]:
        board_path = style_board_path or (job_dir / "style_board" / "style_board.json")
        if not board_path.is_file():
            raise AnimaticError(
                "History V4 editorial animatic requires style_board/style_board.json"
            )
        board = json.loads(board_path.read_text(encoding="utf-8"))
        style_root = board_path.parent
        stills = {
            str(item.get("role")): item
            for item in board.get("stills", [])
            if isinstance(item, Mapping)
        }
        resolved_asset_sources: dict[str, Path] = {}
        selected_resolved = (
            job_dir
            / "asset_selection"
            / "resolved"
            / "resolved_assets.json"
        )
        resolved_path = (
            selected_resolved
            if selected_resolved.is_file()
            else job_dir / "resolved_assets.json"
        )
        project = Path(project_root or Path.cwd()).resolve()
        if resolved_path.is_file():
            resolved_payload = json.loads(
                resolved_path.read_text(encoding="utf-8")
            )
            for item in resolved_payload.get("assets") or []:
                if not isinstance(item, Mapping):
                    continue
                asset_id = str(item.get("asset_id") or "")
                raw = item.get("local_path") or item.get("path")
                if not asset_id or not isinstance(raw, str):
                    continue
                raw_path = Path(raw)
                roots = (project, job_dir.resolve())
                candidates = (
                    (raw_path,)
                    if raw_path.is_absolute()
                    else tuple(root / raw_path for root in roots)
                )
                for candidate in candidates:
                    candidate = candidate.resolve()
                    contained = False
                    for root in roots:
                        try:
                            candidate.relative_to(root)
                        except ValueError:
                            continue
                        contained = True
                        break
                    if (
                        contained
                        and candidate.is_file()
                        and candidate.suffix.casefold()
                        in {".jpg", ".jpeg", ".png", ".webp"}
                    ):
                        resolved_asset_sources[asset_id] = candidate
                        break
        generated_by_role: dict[str, list[dict[str, Any]]] = {}
        generated_batch_hash = ""
        generated_batch_path = generated_visuals_path or (
            job_dir / "generated_visuals" / "candidate_batch.json"
        )
        if generated_batch_path.is_file():
            generated_by_role, generated_batch = motion_candidates_by_role(
                generated_batch_path,
                job_root=job_dir,
            )
            generated_batch_hash = str(generated_batch.get("artifact_hash") or "")
        generated_blocks_by_slot: dict[str, dict[str, Any]] = {}
        generated_blocks_by_excerpt: dict[str, dict[str, Any]] = {}
        generated_block_batch_hash = ""
        block_batch_path = generated_block_batch_path or (
            job_dir / "generated_blocks" / "batch.json"
        )
        block_plan_path = job_dir / "generated_blocks" / "plan.json"
        if block_batch_path.is_file():
            try:
                block_batch = validate_generated_block_batch(
                    block_batch_path,
                    job_root=job_dir,
                    expected_plan=block_plan_path if block_plan_path.is_file() else None,
                )
            except ValueError as exc:
                raise AnimaticError(f"generated block batch is invalid: {exc}") from exc
            generated_block_batch_hash = str(block_batch.get("artifact_hash") or "")
            for item in block_batch.get("blocks", []):
                if not isinstance(item, Mapping):
                    continue
                path = (job_dir / str(item.get("path") or "")).resolve()
                if not path.is_file():
                    continue
                normalized = " ".join(str(item.get("narration_excerpt") or "").split()).casefold()
                for slot_id in item.get("coverage_slot_ids") or []:
                    generated_blocks_by_slot[str(slot_id)] = {**dict(item), "_resolved_path": path}
                if normalized:
                    generated_blocks_by_excerpt[normalized] = {**dict(item), "_resolved_path": path}
        motion_by_block: dict[str, Path] = {}
        motion_manifest_hash = ""
        motion_path = plate_motion_manifest_path or (
            job_dir / "generated_blocks" / "motion" / "manifest.json"
        )
        if motion_path.is_file():
            try:
                motion_manifest = validate_plate_motion_manifest(
                    motion_path,
                    job_root=job_dir,
                )
            except PlateMotionError as exc:
                raise AnimaticError(f"plate motion manifest is invalid: {exc}") from exc
            motion_manifest_hash = str(motion_manifest.get("artifact_hash") or "")
            for item in motion_manifest.get("items", []):
                if not isinstance(item, Mapping):
                    continue
                resolved = item.get("_resolved_path")
                if isinstance(resolved, Path) and resolved.is_file():
                    motion_by_block[str(item.get("id") or "")] = resolved
        render_root = output_root or (job_dir / "animatic")
        frame_root = render_root / "editorial-frames"
        segment_root = render_root / "editorial-segments"
        frame_root.mkdir(parents=True, exist_ok=True)
        segment_root.mkdir(parents=True, exist_ok=True)
        segment_paths: list[Path] = []
        scenes = list(storyboard.get("scenes") or [])
        scenes_by_id = {
            int(scene["scene_id"]): scene
            for scene in scenes
            if isinstance(scene, Mapping)
        }
        beat_plan = compile_editorial_beat_plan(storyboard)
        _json(
            render_root / "editorial-beat-plan.json",
            beat_plan,
        )
        rendered_frames: list[Path] = []
        for index, beat in enumerate(beat_plan["beats"]):
            scene = scenes_by_id[int(beat["parent_scene_id"])]
            function = str(beat["function"])
            role = _DOCUMENTARY_ROLE_BY_FUNCTION.get(function)
            still = stills.get(str(role))
            if not isinstance(still, Mapping):
                raise AnimaticError(
                    f"style board has no representative still for {function}"
                )
            source = (style_root / str(still.get("path") or "")).resolve()
            try:
                source.relative_to(style_root.resolve())
            except ValueError as exc:
                raise AnimaticError(
                    f"style-board still escapes its artifact root: {source}"
                ) from exc
            if not source.is_file():
                raise AnimaticError(f"style-board still is missing: {source}")
            normalized_excerpt = " ".join(str(beat.get("narration_excerpt") or "").split()).casefold()
            generated_block = generated_blocks_by_slot.get(str(beat.get("coverage_slot_id")))
            if generated_block is None and normalized_excerpt:
                generated_block = generated_blocks_by_excerpt.get(normalized_excerpt)
            generated_role = {
                "migration_map_timeline": "map_timeline",
                "lineage_graph": "lineage_concept",
                "concept_mechanics_cutaway": "concept_mechanics",
            }.get(function)
            generated_records = generated_by_role.get(generated_role or "", [])
            if generated_block is not None:
                block_source = Path(str(generated_block["_resolved_path"]))
                if block_source.is_file():
                    source = block_source
                    generated_role = "generated_block"
                    generated_records = [generated_block]
            if generated_records:
                generated_source = Path(str(generated_records[0]["_resolved_path"]))
                if generated_source.is_file():
                    source = generated_source
            # The approved style-board still remains the fallback world. A
            # motion-selected generated plate may replace it only for the
            # three explicitly world-first documentary roles above; it is
            # still preview-only and never becomes a rights-cleared asset.
            if function == "archival_portrait" and generated_block is None:
                for asset_id in beat.get("asset_ids") or []:
                    candidate = resolved_asset_sources.get(str(asset_id))
                    if candidate is not None:
                        source = candidate
                        break
            beat_id = str(beat["beat_id"])
            frame = frame_root / f"{index + 1:03d}_{beat_id}.png"
            self._documentary_frame(
                source,
                scene,
                frame,
                beat=beat,
                beat_index=index,
                beat_count=int(beat_plan["beat_count"]),
                generated_role=generated_role if generated_records else None,
            )
            rendered_frames.append(frame)
            duration = max(1.5, float(beat["duration_s"]))
            segment = segment_root / f"{index + 1:03d}_{beat_id}.mp4"
            motion_source = (
                motion_by_block.get(str(generated_block.get("block_id") or ""))
                if generated_block is not None
                else None
            )
            if motion_source is not None:
                overlay = frame_root / f"{index + 1:03d}_{beat_id}.overlay.png"
                self._documentary_frame(
                    source,
                    scene,
                    overlay,
                    beat=beat,
                    beat_index=index,
                    beat_count=int(beat_plan["beat_count"]),
                    generated_role=generated_role if generated_records else None,
                    transparent_overlay=True,
                )
                video_filter = (
                    f"[0:v]scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
                    f"crop={self.width}:{self.height},fps={self.fps},"
                    f"trim=duration={duration:.6f},setpts=PTS-STARTPTS[base];"
                    "[1:v]format=rgba[caption];"
                    "[base][caption]overlay=0:0:format=auto,format=yuv420p"
                )
                command = [
                    "ffmpeg",
                    "-y",
                    "-stream_loop",
                    "-1",
                    "-i",
                    str(motion_source),
                    "-loop",
                    "1",
                    "-i",
                    str(overlay),
                    "-filter_complex",
                    video_filter,
                    "-t",
                    f"{duration:.6f}",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-movflags",
                    "+faststart",
                    str(segment),
                ]
            else:
                frames = max(1, round(duration * self.fps))
                video_filter = self._zoompan_filter(
                    str(beat.get("motion") or "push_in"),
                    frames,
                    self.width,
                    self.height,
                    self.fps,
                )
                command = [
                    "ffmpeg",
                    "-y",
                    "-loop",
                    "1",
                    "-i",
                    str(frame),
                    "-vf",
                    video_filter,
                    "-t",
                    f"{duration:.6f}",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-movflags",
                    "+faststart",
                    str(segment),
                ]
            if motion_source is None:
                vf_index = command.index("-vf") + 1
                fades: list[str] = []
                if index == 0:
                    fades.append("fade=t=in:st=0:d=0.25")
                if index == int(beat_plan["beat_count"]) - 1:
                    fades.append(
                        f"fade=t=out:st={max(0.0, duration - 0.3):.6f}:d=0.3"
                    )
                if fades:
                    command[vf_index] = command[vf_index] + "," + ",".join(fades)
            _run(self.runner, command)
            if not segment.is_file():
                raise AnimaticError(
                    f"FFmpeg did not produce editorial segment {beat_id}"
                )
            segment_paths.append(segment)

        contact_sheet = render_root / "motion-contact-sheet.png"
        self._write_editorial_contact_sheet(rendered_frames, contact_sheet)
        concat_path = render_root / "editorial-motion.ffconcat"
        lines = ["ffconcat version 1.0"]
        for source in segment_paths:
            escaped = source.resolve().as_posix().replace("'", "'\\''")
            lines.append(f"file '{escaped}'")
        concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        preview = render_root / "motion-preview.mp4"
        _run(
            self.runner,
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_path),
                "-an",
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(preview),
            ],
        )
        if not preview.is_file():
            raise AnimaticError(
                "FFmpeg did not produce animatic/motion-preview.mp4"
            )
        packet["card_preview_path"] = packet["preview_path"]
        packet["preview_path"] = preview.relative_to(job_dir).as_posix()
        packet["motion_preview_path"] = packet["preview_path"]
        packet["renderer"] = "editorial_ffmpeg"
        packet["render_profile"] = "landscape_draft"
        packet["resolved_style_board_roles"] = sorted(stills)
        packet["composition_order"] = "approved_world_then_deterministic_overlay"
        packet["generated_world_plate_functions"] = sorted(
            function
            for function, role_name in (
                ("migration_map_timeline", "map_timeline"),
                ("lineage_graph", "lineage_concept"),
                ("concept_mechanics_cutaway", "concept_mechanics"),
            )
            if generated_by_role.get(role_name)
        )
        if generated_batch_hash:
            packet["generated_visual_batch_hash"] = generated_batch_hash
        if generated_block_batch_hash:
            packet["generated_block_batch_hash"] = generated_block_batch_hash
            packet["generated_block_count"] = len(generated_blocks_by_excerpt)
            packet["one_generated_plate_per_block"] = True
        if motion_manifest_hash:
            packet["plate_motion_manifest_hash"] = motion_manifest_hash
            packet["plate_motion_clip_count"] = len(motion_by_block)
            packet["motion_mode"] = "provider_image_to_video"
        else:
            packet["motion_mode"] = "deterministic_fallback"
        packet["world_first_functions"] = sorted(_DOCUMENTARY_ROLE_BY_FUNCTION)
        packet["editorial_beat_plan_path"] = (
            (render_root / "editorial-beat-plan.json").relative_to(job_dir).as_posix()
        )
        packet["motion_contact_sheet_path"] = (
            (render_root / "motion-contact-sheet.png").relative_to(job_dir).as_posix()
        )
        packet["parent_scene_count"] = len(scenes)
        packet["editorial_beat_count"] = int(beat_plan["beat_count"])
        packet["cut_count"] = max(0, int(beat_plan["beat_count"]) - 1)
        packet["editorial_duration_s"] = float(beat_plan["duration_s"])
        _json(render_root / "review-packet.json", packet)
        return packet

    def render_documentary_revision(
        self,
        storyboard: Mapping[str, Any],
        *,
        job_dir: str | Path,
        style_board_path: str | Path,
        generated_visuals_path: str | Path,
        output_dir: str | Path,
        project_root: str | Path | None = None,
        generated_block_batch_path: str | Path | None = None,
        plate_motion_manifest_path: str | Path | None = None,
    ) -> dict[str, Any]:
        """Render a review-only documentary revision without changing the job.

        The revision can swap a style board and generated world-plate batch,
        while all outputs remain under a job-local evidence directory. It does
        not update the active Gate A snapshot or promote any provider output.
        """

        root = Path(job_dir).resolve()
        style_board = Path(style_board_path).resolve()
        generated_batch = Path(generated_visuals_path).resolve()
        output = Path(output_dir).resolve()
        output.relative_to(root)
        style_board.relative_to(root)
        generated_batch.relative_to(root)
        block_batch = (
            Path(generated_block_batch_path).resolve()
            if generated_block_batch_path is not None
            else None
        )
        if block_batch is not None:
            block_batch.relative_to(root)
        motion_manifest = (
            Path(plate_motion_manifest_path).resolve()
            if plate_motion_manifest_path is not None
            else None
        )
        if motion_manifest is not None:
            motion_manifest.relative_to(root)
        packet: dict[str, Any] = {
            "schema_version": "animatic.v1",
            "preview_path": "",
            "provider_calls": 0,
            "approval_granted": False,
            "revision_only": True,
        }
        return self._render_documentary_motion(
            storyboard,
            root,
            packet,
            project_root=project_root,
            style_board_path=style_board,
            generated_visuals_path=generated_batch,
            generated_block_batch_path=block_batch,
            plate_motion_manifest_path=motion_manifest,
            output_root=output,
        )

    def render_editorial_motion_revision(
        self,
        plan: Mapping[str, Any] | str | Path,
        *,
        asset_map: Mapping[str, Any] | str | Path,
        pacing_recipe: Mapping[str, Any] | str | Path,
        audio_manifest: Mapping[str, Any] | str | Path,
        asset_root: str | Path,
        job_dir: str | Path,
        output_dir: str | Path,
        editor_root: str | Path | None = None,
        overlay_map: Mapping[str, Any] | None = None,
        browser_executable: str | Path | None = None,
        width: int = 854,
        height: int = 480,
        fps: int = 15,
    ) -> dict[str, Any]:
        """Render normal and diagnostic editorial previews under revisions only."""

        root = Path(job_dir).resolve()
        output = Path(output_dir).resolve()
        revision_root = (root / "animatic" / "revisions").resolve()
        try:
            output.relative_to(revision_root)
        except ValueError as exc:
            raise AnimaticError(
                "editorial motion output must stay under animatic/revisions"
            ) from exc
        if output == revision_root:
            raise AnimaticError("editorial motion output requires a named revision directory")

        def load_object(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
            if isinstance(value, Mapping):
                return dict(value)
            path = Path(value).resolve()
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise AnimaticError(f"{label} could not be read: {exc}") from exc
            if not isinstance(payload, Mapping):
                raise AnimaticError(f"{label} must be an object")
            return dict(payload)

        assets_payload = load_object(asset_map, "editorial asset map")
        raw_assets = assets_payload.get("assets")
        if isinstance(raw_assets, Mapping):
            assets = {
                str(asset_id): record if isinstance(record, Mapping) else {}
                for asset_id, record in raw_assets.items()
            }
        elif isinstance(raw_assets, Sequence) and not isinstance(
            raw_assets, (str, bytes, bytearray)
        ):
            assets = {
                str(record.get("id") or record.get("asset_id") or ""): record
                for record in raw_assets
                if isinstance(record, Mapping)
                and (record.get("id") or record.get("asset_id"))
            }
        else:
            raise AnimaticError("editorial asset map requires an assets object or array")
        validated = validate_editorial_motion_plan(plan, known_asset_ids=set(assets))
        if validated["asset_map_hash"] != canonical_sha256(assets_payload):
            raise AnimaticError("editorial asset map hash does not match the motion plan")

        audio = load_object(audio_manifest, "canonical audio manifest")
        audio_hash = canonical_sha256(audio)
        if str(audio.get("artifact_hash") or "") != audio_hash:
            raise AnimaticError("canonical audio manifest artifact_hash is stale")
        if validated["audio_manifest_hash"] != audio_hash:
            raise AnimaticError("canonical audio manifest does not match the motion plan")
        if audio.get("status") != "ready":
            raise AnimaticError("canonical audio must be ready")

        from content.video_engine.src.guards.editorial_motion_qc import (
            run_editorial_motion_qc,
        )

        qc = run_editorial_motion_qc(
            validated,
            pacing_recipe=pacing_recipe,
            asset_map=assets_payload,
            asset_root=asset_root,
            revision_dir=output,
            job_dir=root,
            check_files=True,
        )
        if qc["overall"] != "pass":
            failures = [
                item["detail"]
                for item in qc["checks"]
                if item.get("status") == "fail"
            ]
            raise AnimaticError("editorial motion QC failed: " + "; ".join(failures))

        protected: dict[str, str] = {}
        for candidate in [root / "storyboard.json", *(root / "animatic").glob("**/*")]:
            if not candidate.is_file():
                continue
            try:
                candidate.resolve().relative_to(revision_root)
            except ValueError:
                protected[candidate.relative_to(root).as_posix()] = _file_sha256(candidate)

        output.mkdir(parents=True, exist_ok=True)
        public = output / "public"
        public_assets = public / "assets"
        public_audio = public / "audio"
        public_assets.mkdir(parents=True, exist_ok=True)
        public_audio.mkdir(parents=True, exist_ok=True)
        approved_root = Path(asset_root).resolve()
        renderer_assets: dict[str, str] = {}
        used_asset_ids = {
            str(layer["asset_id"])
            for shot in validated["shots"]
            for layer in shot["layers"]
        }
        for asset_id in sorted(used_asset_ids):
            record = assets[asset_id]
            if record.get("render_eligible") is not True:
                raise AnimaticError(f"editorial asset {asset_id!r} is not render eligible")
            source = _contained_file(
                approved_root,
                record.get("path") or record.get("local_path"),
                f"editorial asset {asset_id!r}",
            )
            expected = str(record.get("sha256") or record.get("content_hash") or "")
            if not expected or _file_sha256(source) != expected:
                raise AnimaticError(f"editorial asset {asset_id!r} has a stale content hash")
            suffix = source.suffix.casefold()
            if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
                raise AnimaticError(f"editorial asset {asset_id!r} has an unsupported format")
            destination = public_assets / f"{asset_id}{suffix}"
            shutil.copy2(source, destination)
            renderer_assets[asset_id] = destination.relative_to(public).as_posix()

        audio_source = _contained_file(root, audio.get("audio_path"), "canonical audio")
        if _file_sha256(audio_source) != str(audio.get("audio_sha256") or ""):
            raise AnimaticError("canonical audio content hash is stale")
        if audio_source.suffix.casefold() not in {".mp3", ".wav", ".m4a", ".aac"}:
            raise AnimaticError("canonical audio has an unsupported format")
        audio_destination = public_audio / f"canonical{audio_source.suffix.casefold()}"
        shutil.copy2(audio_source, audio_destination)

        renderer_sound_effects: dict[str, str] = {}
        planned_effects: dict[str, Mapping[str, Any]] = {}
        for shot in validated["shots"]:
            for effect in shot.get("sound_effects") or []:
                if not isinstance(effect, Mapping):
                    continue
                effect_id = str(effect.get("id") or "")
                previous = planned_effects.setdefault(effect_id, effect)
                if previous != effect:
                    raise AnimaticError(
                        f"sound effect {effect_id!r} has inconsistent declarations"
                    )
        for effect_id, effect in sorted(planned_effects.items()):
            # Job-local authored SFX remain behind the same revision boundary as
            # the canonical narration. The plan stores only the stable ID and
            # digest; it cannot choose arbitrary renderer paths.
            source = _contained_file(
                root,
                (Path("audio") / "sfx" / f"{effect_id}.wav").as_posix(),
                f"sound effect {effect_id!r}",
            )
            if _file_sha256(source) != str(effect.get("sha256") or ""):
                raise AnimaticError(f"sound effect {effect_id!r} has a stale content hash")
            destination = public_audio / f"{effect_id}.wav"
            shutil.copy2(source, destination)
            renderer_sound_effects[effect_id] = destination.relative_to(public).as_posix()

        profile = {"width": int(width), "height": int(height), "fps": int(fps), "label": "proof"}
        props = {
            "plan": validated,
            "asset_map": renderer_assets,
            "canonical_audio": {
                "path": audio_destination.relative_to(public).as_posix(),
                "start_s": float(validated.get("source_start_s") or 0),
                "volume": 1,
            },
            "sound_effect_map": renderer_sound_effects,
            "overlay_map": dict(overlay_map or {}),
            "caption_policy": "platform",
            "citation_policy": "credits_only",
            "diagnostic": False,
            "render_profile": profile,
        }
        normal_props = output / "remotion-props.json"
        diagnostic_props = output / "remotion-props-diagnostic.json"
        _json(normal_props, props)
        _json(diagnostic_props, {**props, "diagnostic": True})
        _json(output / "editorial-motion-plan.json", validated)
        _json(output / "pacing-recipe.json", load_object(pacing_recipe, "pacing recipe"))
        _json(output / "asset-map.json", assets_payload)
        _json(output / "structural-qc.json", qc)

        editor = (
            Path(editor_root).resolve()
            if editor_root is not None
            else (Path(__file__).resolve().parents[2] / "editor").resolve()
        )
        entry = editor / "src" / "index.tsx"
        if not entry.is_file():
            raise AnimaticError("Remotion editor entrypoint is missing")
        normal_preview = output / "revised-preview.mp4"
        diagnostic_preview = output / "diagnostic-preview.mp4"
        npx = shutil.which("npx.cmd") or shutil.which("npx")
        if not npx:
            raise AnimaticError("npx is required for Remotion rendering")
        for props_path, destination in (
            (normal_props, normal_preview),
            (diagnostic_props, diagnostic_preview),
        ):
            command = [
                npx,
                "remotion",
                "render",
                str(entry),
                "EditorialMotion",
                f"--props={props_path}",
                f"--public-dir={public}",
            ]
            if browser_executable:
                command.append(f"--browser-executable={Path(browser_executable)}")
            command.append(str(destination))
            result = self.runner(
                command,
                check=True,
                capture_output=True,
                text=True,
                cwd=str(editor),
            )
            if result.returncode != 0 or not destination.is_file():
                raise AnimaticError(f"Remotion did not produce {destination.name}")

        after = {
            relative: _file_sha256(root / relative)
            for relative in protected
            if (root / relative).is_file()
        }
        if protected != after:
            raise AnimaticError("active Gate A artifacts changed during revision rendering")

        packet = {
            "schema_version": "editorial_motion_revision.v1",
            "revision_only": True,
            "approval_granted": False,
            "provider_calls": 0,
            "cost_usd": 0.0,
            "motion_plan_hash": validated["artifact_hash"],
            "asset_map_hash": validated["asset_map_hash"],
            "audio_manifest_hash": validated["audio_manifest_hash"],
            "normal_preview_path": normal_preview.relative_to(root).as_posix(),
            "diagnostic_preview_path": diagnostic_preview.relative_to(root).as_posix(),
            "normal_preview_sha256": _file_sha256(normal_preview),
            "diagnostic_preview_sha256": _file_sha256(diagnostic_preview),
            "duration_s": validated["duration_s"],
            "source_start_s": float(validated.get("source_start_s") or 0),
            "protected_gate_a_hashes_before": protected,
            "protected_gate_a_hashes_after": after,
            "gate_a_unchanged": protected == after,
            "structural_qc": "pass",
            "human_review_required": True,
        }
        _json(output / "review-packet.json", packet)
        return packet

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        storyboard_path = ctx.job_dir / "storyboard.json"
        if not storyboard_path.is_file():
            raise FileNotFoundError("storyboard.json is required before animatic rendering")
        storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
        packet = self.build(storyboard, ctx.job_dir / "animatic")
        if bool(ctx.configs.get("animatic_motion_render", True)):
            source = storyboard.get("source") or {}
            if (
                storyboard.get("schema_version") in {"2.2.0", "2.3.0"}
                and isinstance(source, Mapping)
                and source.get("kind") == "history_episode"
            ):
                packet = self._render_documentary_motion(
                    storyboard,
                    ctx.job_dir,
                    packet,
                    project_root=ctx.configs.get("project_root"),
                )
            else:
                from content.video_engine.src.services.manim_render import (
                    ManimRenderService,
                )

                renderer = ManimRenderService(
                    ctx.job_dir,
                    profiles=ctx.configs.get("render_profiles"),
                )
                manifest = renderer.render_storyboard(
                    storyboard,
                    "landscape_draft",
                    audio_dir=ctx.job_dir / "audio",
                )
                motion_concat = ctx.job_dir / "animatic" / "motion.ffconcat"
                lines = ["ffconcat version 1.0"]
                for segment in manifest["segments"]:
                    source_path = _resolve_local_segment(
                        ctx.job_dir,
                        segment.get("path"),
                    )
                    escaped = source_path.as_posix().replace("'", "'\\''")
                    lines.append(f"file '{escaped}'")
                motion_concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
                motion_preview = ctx.job_dir / "animatic" / "motion-preview.mp4"
                _run(
                    self.runner,
                    [
                        "ffmpeg",
                        "-y",
                        "-f",
                        "concat",
                        "-safe",
                        "0",
                        "-i",
                        str(motion_concat),
                        "-an",
                        "-c",
                        "copy",
                        "-movflags",
                        "+faststart",
                        str(motion_preview),
                    ],
                )
                if not motion_preview.is_file():
                    raise AnimaticError(
                        "Manim did not produce animatic/motion-preview.mp4"
                    )
                packet["card_preview_path"] = packet["preview_path"]
                packet["preview_path"] = motion_preview.relative_to(
                    ctx.job_dir
                ).as_posix()
                packet["motion_preview_path"] = packet["preview_path"]
                packet["renderer"] = "manim"
                packet["render_profile"] = "landscape_draft"
                _json(ctx.job_dir / "animatic" / "review-packet.json", packet)
        return StageOutput(
            {
                "review_packet_path": "animatic/review-packet.json",
                "preview_path": packet["preview_path"],
                "shot_strip_path": packet["shot_strip_path"],
                "scene_count": packet["scene_count"],
                "duration_s": packet["duration_s"],
                "renderer": packet.get("renderer", "storyboard_cards"),
                "cost_usd": 0.0,
            }
        )


def run_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    return AnimaticService().run_stage(job, ctx)


__all__ = [
    "AnimaticError",
    "AnimaticService",
    "_resolve_local_segment",
    "run_stage",
]
