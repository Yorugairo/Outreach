"""Deterministic six-frame style board for History Documentary V4."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.services.documentary_treatment import canonical_sha256
from content.video_engine.src.services.generated_visuals import (
    style_board_candidates_by_role,
)


DOCUMENTARY_STYLE_BOARD_VERSION = "style_board.v2"
STYLE_BOARD_VERSION = DOCUMENTARY_STYLE_BOARD_VERSION
DOCUMENTARY_STYLE_BOARD_ROLES: tuple[str, ...] = (
    "cold_open",
    "archive",
    "illustration",
    "document",
    "map_timeline",
    "lineage_concept",
)
STYLE_BOARD_ROLES = DOCUMENTARY_STYLE_BOARD_ROLES
DOCUMENTARY_RUBRIC_DIMENSIONS: tuple[str, ...] = (
    "originality",
    "hierarchy",
    "asset_integration",
    "typography",
    "citation_legibility",
    "audience_clarity",
)

_DEFAULT_PALETTE = {
    "paper": "#F4EBDD",
    "ink": "#1F252A",
    "background": "#171B20",
    "surface": "#2B3136",
    "rust": "#A44A32",
    "indigo": "#324C73",
    "jade": "#2C7666",
    "ochre": "#C18B45",
    "muted": "#A7A092",
}


class DocumentaryStyleBoardError(ValueError):
    """Raised when a style board cannot be produced deterministically."""


def _font(size: int, *, mono: bool = False) -> ImageFont.ImageFont:
    root = Path(__file__).resolve().parents[1] / "assets" / "fonts"
    names = (
        (root / "RobotoMono-Variable.ttf", "DejaVuSansMono.ttf")
        if mono
        else (root / "Inter-Variable.ttf", "DejaVuSans.ttf", "arial.ttf")
    )
    for name in names:
        try:
            return ImageFont.truetype(str(name), max(8, int(size)))
        except OSError:
            continue
    return ImageFont.load_default()


def _color(value: Any, fallback: str) -> str:
    text = str(value or "")
    return text if len(text) == 7 and text.startswith("#") else fallback


def _phash(image: Image.Image) -> str:
    sample = image.convert("L").resize((8, 8), Image.Resampling.LANCZOS)
    values = list(
        sample.get_flattened_data()
        if hasattr(sample, "get_flattened_data")
        else sample.getdata()
    )
    mean = sum(values) / max(1, len(values))
    bits = 0
    for value in values:
        bits = (bits << 1) | int(value >= mean)
    return f"{bits:016x}"


def _normalize_treatments(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        value = value.get("shots") or value.get("treatments") or [value]
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            continue
        item = dict(item)
        function = str(item.get("function") or item.get("visual_type") or item.get("visual_function") or "")
        item["function"] = function
        item.setdefault("treatment_id", item.get("id") or f"treatment-documentary-{index + 1:02d}")
        if not str(item["treatment_id"]).startswith("treatment-"):
            item["treatment_id"] = f"treatment-{item['treatment_id']}"
        result.append(item)
    return result


def _function_for_role(role: str, treatments: Sequence[Mapping[str, Any]], index: int) -> tuple[str, dict[str, Any]]:
    preferences = {
        "cold_open": ("artifact_cold_open", "chapter_cta"),
        "archive": ("archival_portrait",),
        "illustration": ("illustrated_reconstruction",),
        "document": ("document_quote_closeup",),
        "map_timeline": ("migration_map_timeline",),
        "lineage_concept": ("lineage_graph", "concept_mechanics_cutaway"),
    }
    for preferred in preferences.get(role, (role,)):
        matching = [
            item
            for item in treatments
            if str(item.get("function") or "").casefold() == preferred
        ]
        if matching:
            selected = max(
                matching,
                key=lambda item: int(
                    any(
                        str(asset_id).startswith("magnific-")
                        for asset_id in item.get("asset_ids") or []
                    )
                ),
            )
            return str(selected.get("function")), dict(selected)
    defaults = {
        "cold_open": "artifact_cold_open",
        "archive": "archival_portrait",
        "illustration": "illustrated_reconstruction",
        "document": "document_quote_closeup",
        "map_timeline": "migration_map_timeline",
        "lineage_concept": "lineage_graph",
    }
    function = defaults[role]
    if treatments:
        item = dict(treatments[index % len(treatments)])
    else:
        item = {}
    item.setdefault("function", function)
    item.setdefault("treatment_id", f"treatment-{function.replace('_', '-')}")
    return function, item


def _asset_records(
    value: Mapping[str, Any] | str | Path | None,
    *,
    project_root: Path,
    job_root: Path | None = None,
) -> dict[str, Path]:
    if isinstance(value, (str, Path)):
        path = Path(value)
        if not path.is_file():
            return {}
        value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, Path] = {}
    for item in value.get("assets", []) or []:
        if not isinstance(item, Mapping) or item.get("render_eligible") is not True:
            continue
        asset_id = str(item.get("asset_id") or item.get("id") or "").strip()
        raw_path = str(item.get("local_path") or item.get("path") or "").strip()
        if not asset_id or not raw_path:
            continue
        raw = Path(raw_path)
        roots = [project_root.resolve()]
        if job_root is not None:
            roots.append(job_root.resolve())
        candidates = (
            [raw]
            if raw.is_absolute()
            else [root / raw for root in roots]
        )
        asset_path: Path | None = None
        for candidate in candidates:
            try:
                resolved = candidate.resolve(strict=True)
            except OSError:
                continue
            if resolved.is_file() and any(
                _inside_root(resolved, root) for root in roots
            ):
                asset_path = resolved
                break
        if asset_path is None:
            continue
        if asset_path.is_file():
            result[asset_id] = asset_path
    return result


def _inside_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _open_asset(path: Path, *, width: int, height: int) -> Image.Image:
    if path.suffix.casefold() == ".svg":
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise DocumentaryStyleBoardError(
                "Playwright is required to rasterize approved local SVG assets"
            ) from exc
        svg = path.read_text(encoding="utf-8")
        document = (
            "<style>"
            "html,body{margin:0;width:100%;height:100%;overflow:hidden;"
            "background:#0B0F14}"
            "svg{display:block;width:100vw!important;height:100vh!important}"
            "</style>"
            + svg
        )
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                java_script_enabled=False,
                viewport={
                    "width": max(96, int(width)),
                    "height": max(96, int(height)),
                },
                device_scale_factor=1,
            )
            context.route("**/*", lambda route: route.abort())
            page = context.new_page()
            page.set_content(document, wait_until="domcontentloaded")
            rendered = page.screenshot(type="png", animations="disabled")
            context.close()
            browser.close()
        with Image.open(io.BytesIO(rendered)) as source:
            return source.convert("RGB")
    with Image.open(path) as source:
        return ImageOps.exif_transpose(source).convert("RGB")


def _cover(source: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(
        source.convert("RGB"),
        size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.43),
    )


def _contain(
    source: Image.Image,
    size: tuple[int, int],
    *,
    background: str,
) -> Image.Image:
    fitted = ImageOps.contain(
        source.convert("RGB"),
        size,
        method=Image.Resampling.LANCZOS,
    )
    result = Image.new("RGB", size, background)
    result.paste(
        fitted,
        ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2),
    )
    return result


def _citation_label(treatment: Mapping[str, Any]) -> str:
    citations = treatment.get("citations") or []
    if isinstance(citations, (str, Mapping)):
        citations = [citations]
    labels: list[str] = []
    for citation in list(citations)[:2]:
        if isinstance(citation, Mapping):
            text = str(citation.get("citation_id") or citation.get("id") or "")
        else:
            text = str(citation)
        text = text.removeprefix("citation-").replace("-", " ").upper()
        if text:
            labels.append(text)
    return "  •  ".join(labels) or "SOURCE LOCATOR PENDING FRAME"


def _role_title(role: str) -> tuple[str, str]:
    return {
        "cold_open": ("1882", "A system begins to take shape"),
        "archive": ("THE SYSTEM\nBEFORE THE EXPORT", "Archive, context, consequence"),
        "illustration": ("MOVEMENT CHANGES THE ART", "Illustrated reconstruction"),
        "document": ("WHAT CAN THE\nRECORD PROVE?", "Claim, locator, qualification"),
        "map_timeline": ("AN ART IN MOTION", "Japan  →  global circuit  →  Brazil"),
        "lineage_concept": ("A NETWORK, NOT A MYTH", "Relationships, branches, uncertainty"),
    }[role]


def _literature_mode_for_role(role: str) -> str:
    return {
        "cold_open": "lofi_comedy",
        "archive": "archive_evidence",
        "illustration": "historical_comic",
        "document": "archive_evidence",
        "map_timeline": "historical_comic",
        "lineage_concept": "lofi_comedy",
    }[role]


def _draw_wobbly_line(
    draw: ImageDraw.ImageDraw,
    points: Sequence[tuple[int, int]],
    *,
    fill: str,
    width: int,
) -> None:
    """Draw a deterministic handmade-looking line without random state."""

    for offset in (-1, 1):
        shifted = [
            (x + offset * (index % 2), y - offset * ((index + 1) % 2))
            for index, (x, y) in enumerate(points)
        ]
        draw.line(shifted, fill=fill, width=max(1, width // 2), joint="curve")
    draw.line(points, fill=fill, width=width, joint="curve")


def _draw_branded_literature_frame(
    role: str,
    treatment: Mapping[str, Any],
    *,
    width: int,
    height: int,
    palette: Mapping[str, Any],
    asset_images: Sequence[Image.Image] = (),
    profile_fork: bool = False,
) -> Image.Image:
    """Render the three-mode tone board for the Branded Literature identity."""

    paper = _color(palette.get("paper"), "#F1E3C5")
    ink = _color(palette.get("ink"), "#171A1D")
    background = _color(palette.get("background"), "#0D1117")
    surface = _color(palette.get("surface"), "#202630")
    rust = _color(palette.get("comic_red") or palette.get("rust"), "#D7533F")
    indigo = _color(palette.get("indigo"), "#304F78")
    jade = _color(palette.get("jade"), "#2F806C")
    ochre = _color(palette.get("ochre"), "#D49A3A")
    highlighter = _color(palette.get("highlighter"), "#F4D35E")
    mode = _literature_mode_for_role(role)
    image = Image.new("RGB", (width, height), paper if mode != "archive_evidence" else background)
    draw = ImageDraw.Draw(image)
    heading = _font(max(12, width // 25))
    body = _font(max(9, width // 43))
    mono = _font(max(8, width // 67), mono=True)
    rail_height = max(23, height // 10)
    content_bottom = height - rail_height
    margin = max(12, width // 30)
    line_width = max(2, width // 220)

    # A recurring folio and mode slug make the contrast feel like one authored
    # publication rather than a bag of unrelated templates.
    draw.text((margin, max(7, height // 45)), "COMBAT HISTORY  /  VOL. 01", fill=rust, font=mono)
    draw.text(
        (width - max(150, width // 3), max(7, height // 45)),
        (
            {
                "cold_open": "COMIC CUTOUT",
                "archive": "ARCHIVE PROOF",
                "illustration": "HISTORY TABLEAU",
                "document": "DOCUMENT PROOF",
                "map_timeline": "MAP TO SCENE",
                "lineage_concept": "EVIDENCE DIAGRAM",
            }[role]
            if profile_fork
            else mode.replace("_", " ").upper()
        ),
        fill=jade if mode == "archive_evidence" else indigo,
        font=mono,
    )

    if role == "cold_open":
        # The joke is intentionally cheap; the correction is visually decisive.
        panel_top = max(35, height // 8)
        panel_bottom = content_bottom - max(16, height // 22)
        split = int(width * 0.55)
        draw.rectangle((margin, panel_top, split, panel_bottom), fill="#E6D1AA", outline=ink, width=line_width)
        draw.rectangle((split + 8, panel_top, width - margin, panel_bottom), fill=surface, outline=ink, width=line_width)
        ground = panel_bottom - max(18, height // 16)
        for index, x in enumerate(
            range(margin + 38, split - 18, max(50, width // 8))
        ):
            head = max(7, width // 72)
            figure_ground = ground + (index % 2) * max(3, height // 70)
            draw.ellipse(
                (
                    x - head,
                    figure_ground - 84,
                    x + head,
                    figure_ground - 64,
                ),
                fill=ink,
            )
            draw.polygon(
                [
                    (x - head - 4, figure_ground - 80),
                    (x + head + 4, figure_ground - 80),
                    (x, figure_ground - 101),
                ],
                fill=ink,
            )
            draw.polygon(
                [
                    (x, figure_ground - 64),
                    (x - 19, figure_ground - 21),
                    (x + 17, figure_ground - 21),
                ],
                fill=indigo if index % 2 else rust,
                outline=ink,
            )
            draw.polygon(
                [
                    (x - 18, figure_ground - 21),
                    (x - 6, figure_ground),
                    (x + 1, figure_ground - 21),
                ],
                fill=ink,
            )
            draw.polygon(
                [
                    (x + 2, figure_ground - 21),
                    (x + 15, figure_ground),
                    (x + 18, figure_ground - 21),
                ],
                fill=ink,
            )
            draw.line(
                (
                    x - 18,
                    figure_ground - 48,
                    x + 30,
                    figure_ground - 95,
                ),
                fill=ink,
                width=max(2, line_width),
            )
        draw.text((margin + 12, panel_top + 10), "SAMURAI LORE?", fill=ink, font=body)
        draw.line((margin + 10, panel_top + 44, split - 12, panel_bottom - 10), fill=rust, width=max(4, line_width * 2))
        draw.line((split - 12, panel_top + 44, margin + 10, panel_bottom - 10), fill=rust, width=max(4, line_width * 2))
        dojo_x = split + max(32, width // 14)
        dojo_y = panel_top + max(35, height // 10)
        draw.polygon(
            [(dojo_x, dojo_y + 35), (width - margin - 20, dojo_y + 35), (width - margin - 55, dojo_y), (dojo_x + 30, dojo_y)],
            fill=paper,
            outline=ink,
        )
        draw.rectangle((dojo_x + 18, dojo_y + 35, width - margin - 40, panel_bottom - 22), fill="#F7F0DF", outline=ink, width=line_width)
        draw.text((split + 22, panel_top + 10), "THE BORING ANSWER:", fill=highlighter, font=body)
        draw.text((split + 24, panel_bottom - max(50, height // 8)), "AN INSTITUTION.", fill=paper, font=heading)
        draw.text((margin, content_bottom - 4), "cheap joke  →  hard correction", fill=indigo, font=mono, anchor="ls")
    elif role == "archive":
        draw.rectangle((margin, max(42, height // 8), width - margin, content_bottom - 12), fill=surface, outline=paper, width=line_width)
        image_area = (
            margin + 12,
            max(54, height // 7),
            int(width * 0.57),
            content_bottom - 24,
        )
        if asset_images:
            asset = _contain(
                ImageEnhance.Contrast(asset_images[0].convert("L").convert("RGB")).enhance(1.18),
                (image_area[2] - image_area[0], image_area[3] - image_area[1]),
                background=surface,
            )
            image.paste(asset, (image_area[0], image_area[1]))
            draw = ImageDraw.Draw(image)
            if len(asset_images) > 1:
                inset_width = max(90, width // 4)
                inset_height = max(58, height // 4)
                inset = _cover(
                    ImageEnhance.Color(asset_images[1]).enhance(0.72),
                    (inset_width, inset_height),
                )
                inset_x = image_area[2] - inset_width
                inset_y = image_area[3] - inset_height
                image.paste(inset, (inset_x, inset_y))
                draw = ImageDraw.Draw(image)
                draw.rectangle(
                    (
                        inset_x,
                        inset_y,
                        inset_x + inset_width,
                        inset_y + inset_height,
                    ),
                    outline=paper,
                    width=line_width,
                )
                draw.rectangle(
                    (inset_x, inset_y, inset_x + inset_width, inset_y + 20),
                    fill=ink,
                )
                draw.text(
                    (inset_x + 6, inset_y + 4),
                    "REVIEWED B-ROLL CUT-IN",
                    fill=paper,
                    font=mono,
                )
        else:
            draw.rectangle(image_area, fill="#343A40", outline=paper, width=line_width)
            draw.ellipse(
                (
                    image_area[0] + (image_area[2] - image_area[0]) // 3,
                    image_area[1] + 18,
                    image_area[2] - (image_area[2] - image_area[0]) // 3,
                    image_area[1] + max(55, height // 5),
                ),
                fill="#787878",
            )
            draw.text((image_area[0] + 12, image_area[3] - 24), "RIGHTS-REVIEWED IMAGE", fill=paper, font=mono)
        text_x = int(width * 0.62)
        draw.text((text_x, max(62, height // 6)), "ARCHIVE", fill=jade, font=mono)
        draw.multiline_text((text_x, max(88, height // 4)), "THE RECORD\nGETS THE\nLAST WORD.", fill=paper, font=heading, spacing=3)
        draw.text((text_x, content_bottom - max(40, height // 9)), "quiet motion • exact source", fill="#B9C0C7", font=mono)
    elif role == "illustration":
        top = max(44, height // 8)
        bottom = content_bottom - 14
        gap = max(6, width // 90)
        panel_width = (width - 2 * margin - 2 * gap) // 3
        captions = ("A SYSTEM", "CROSSES WATER", "CHANGES SHAPE")
        for index, caption in enumerate(captions):
            left = margin + index * (panel_width + gap)
            right = left + panel_width
            panel_fill = ("#E4C88E", "#9AB4C8", "#C76B50")[index]
            draw.rectangle((left, top, right, bottom), fill=panel_fill, outline=ink, width=line_width)
            for dot_y in range(top + 12, bottom - 12, max(14, height // 28)):
                for dot_x in range(left + 10, right - 10, max(14, width // 75)):
                    draw.ellipse(
                        (dot_x, dot_y, dot_x + 1, dot_y + 1),
                        fill="#756653",
                    )
            if index == 0:
                dojo_top = top + max(42, height // 10)
                draw.rectangle(
                    (left + 18, dojo_top, right - 18, bottom - 34),
                    fill=paper,
                    outline=ink,
                    width=line_width,
                )
                draw.polygon(
                    [
                        (left + 8, dojo_top + 3),
                        (right - 8, dojo_top + 3),
                        ((left + right) // 2, top + 14),
                    ],
                    fill=ink,
                )
                figure_x = (left + right) // 2
                head = max(8, width // 90)
                draw.ellipse(
                    (
                        figure_x - head,
                        dojo_top + 26,
                        figure_x + head,
                        dojo_top + 26 + head * 2,
                    ),
                    fill=ink,
                )
                draw.polygon(
                    [
                        (figure_x, dojo_top + 42),
                        (figure_x - 24, bottom - 62),
                        (figure_x + 24, bottom - 62),
                    ],
                    fill=indigo,
                    outline=ink,
                )
                for mat_x in range(left + 24, right - 20, max(30, panel_width // 4)):
                    draw.line(
                        (figure_x, bottom - 34, mat_x, bottom - 34),
                        fill="#9B805A",
                        width=max(1, line_width // 2),
                    )
            elif index == 1:
                sea_y = bottom - max(52, height // 8)
                for wave in range(3):
                    draw.arc(
                        (
                            left + 15 + wave * panel_width // 4,
                            sea_y - 8,
                            left + 75 + wave * panel_width // 4,
                            sea_y + 18,
                        ),
                        180,
                        355,
                        fill=paper,
                        width=max(2, line_width),
                    )
                ship_left = left + panel_width // 5
                ship_right = right - panel_width // 7
                ship_y = sea_y - max(26, height // 14)
                draw.polygon(
                    [
                        (ship_left, ship_y),
                        (ship_right, ship_y),
                        (ship_right - 20, ship_y + 25),
                        (ship_left + 14, ship_y + 25),
                    ],
                    fill=ink,
                )
                draw.rectangle(
                    (
                        ship_left + 32,
                        ship_y - 31,
                        ship_right - 30,
                        ship_y,
                    ),
                    fill=paper,
                    outline=ink,
                    width=max(1, line_width // 2),
                )
                draw.rectangle(
                    (
                        ship_left + 48,
                        ship_y - 52,
                        ship_left + 61,
                        ship_y - 31,
                    ),
                    fill=rust,
                    outline=ink,
                    width=max(1, line_width // 2),
                )
                route_bottom = max(top + 48, sea_y - 8)
                draw.arc(
                    (left + 18, top + 32, right - 18, route_bottom),
                    195,
                    345,
                    fill=paper,
                    width=max(3, line_width * 2),
                )
                draw.polygon(
                    [
                        (right - 26, top + 83),
                        (right - 43, top + 75),
                        (right - 37, top + 95),
                    ],
                    fill=paper,
                )
            else:
                horizon = bottom - max(62, height // 7)
                draw.rectangle(
                    (left + 18, horizon - 42, left + panel_width // 2, horizon),
                    fill=ochre,
                    outline=ink,
                    width=line_width,
                )
                draw.polygon(
                    [
                        (left + 10, horizon - 40),
                        (left + panel_width // 2 + 8, horizon - 40),
                        (left + panel_width // 3, horizon - 72),
                    ],
                    fill=ink,
                )
                palm_x = right - max(38, panel_width // 5)
                draw.line(
                    (palm_x, horizon, palm_x + 8, horizon - 78),
                    fill=ink,
                    width=max(3, line_width),
                )
                for angle in (-34, -16, 9, 28):
                    draw.line(
                        (
                            palm_x + 8,
                            horizon - 78,
                            palm_x + 8 + angle,
                            horizon - 98 + abs(angle) // 3,
                        ),
                        fill=ink,
                        width=max(2, line_width),
                    )
                figure_x = left + int(panel_width * 0.62)
                draw.ellipse(
                    (figure_x - 10, horizon - 78, figure_x + 10, horizon - 58),
                    fill=paper,
                    outline=ink,
                    width=line_width,
                )
                draw.polygon(
                    [
                        (figure_x, horizon - 58),
                        (figure_x - 22, horizon),
                        (figure_x + 22, horizon),
                    ],
                    fill=indigo,
                    outline=ink,
                )
                draw.text(
                    (left + 16, top + 18),
                    "BELÉM",
                    fill=paper,
                    font=heading,
                )
            draw.rectangle((left + 8, bottom - 30, right - 8, bottom - 7), fill=ink)
            draw.text((left + 14, bottom - 26), caption, fill=paper, font=mono)
        draw.rectangle((margin, top - 25, margin + max(210, width // 3), top - 3), fill=rust)
        draw.text((margin + 8, top - 22), "ILLUSTRATION / RECONSTRUCTION", fill=paper, font=mono)
    elif role == "document":
        paper_left = int(width * 0.18)
        paper_top = max(45, height // 9)
        paper_right = int(width * 0.82)
        paper_bottom = content_bottom - 12
        draw.rectangle((paper_left + 8, paper_top + 8, paper_right + 8, paper_bottom + 8), fill="#050708")
        draw.rectangle((paper_left, paper_top, paper_right, paper_bottom), fill="#F8EED7", outline="#4B4033", width=line_width)
        draw.text((paper_left + 22, paper_top + 18), "WHAT THE RECORD ACTUALLY SUPPORTS", fill=rust, font=mono)
        for index, width_fraction in enumerate((0.78, 0.66, 0.82, 0.58, 0.72)):
            y = paper_top + 58 + index * max(22, height // 14)
            if index == 2:
                draw.rectangle((paper_left + 18, y - 3, paper_left + int((paper_right - paper_left) * width_fraction), y + 16), fill=highlighter)
            draw.line((paper_left + 24, y + 7, paper_left + int((paper_right - paper_left) * width_fraction), y + 7), fill=ink, width=max(2, line_width))
        draw.text((paper_right - max(150, width // 4), paper_bottom - 30), "locator • page • date", fill=indigo, font=mono)
    elif role == "map_timeline":
        top = max(46, height // 8)
        draw.rectangle((margin, top, width - margin, content_bottom - 14), fill="#D9C59F", outline=ink, width=line_width)
        if asset_images:
            photo_width = max(150, int(width * 0.40))
            photo_height = max(90, content_bottom - top - 34)
            photo = _cover(
                ImageEnhance.Color(asset_images[0]).enhance(0.62),
                (photo_width, photo_height),
            )
            photo_x = width - margin - photo_width - 10
            photo_y = top + 10
            image.paste(photo, (photo_x, photo_y))
            draw = ImageDraw.Draw(image)
            draw.rectangle(
                (
                    photo_x,
                    photo_y,
                    photo_x + photo_width,
                    photo_y + photo_height,
                ),
                outline=ink,
                width=line_width,
            )
            draw.rectangle(
                (photo_x, photo_y, photo_x + photo_width, photo_y + 21),
                fill=ink,
            )
            draw.text(
                (photo_x + 6, photo_y + 4),
                "PERIOD TRAVEL B-ROLL",
                fill=paper,
                font=mono,
            )
        # Abstract coastlines: visibly editorial, not cartographic evidence.
        coast = [
            (margin + 20, top + 65),
            (int(width * 0.25), top + 35),
            (int(width * 0.38), top + 78),
            (int(width * 0.52), top + 52),
            (int(width * 0.67), top + 92),
            (width - margin - 32, top + 55),
        ]
        _draw_wobbly_line(draw, coast, fill=indigo, width=line_width)
        start = (int(width * 0.23), content_bottom - max(60, height // 6))
        end = (int(width * 0.76), content_bottom - max(92, height // 5))
        draw.arc((start[0], top + 25, end[0], content_bottom - 38), 185, 350, fill=rust, width=max(4, line_width * 2))
        draw.polygon([(end[0], end[1]), (end[0] - 15, end[1] - 8), (end[0] - 10, end[1] + 12)], fill=rust)
        for point, label in ((start, "JAPAN"), (end, "BELÉM")):
            draw.ellipse((point[0] - 9, point[1] - 9, point[0] + 9, point[1] + 9), fill=ochre, outline=ink, width=line_width)
            draw.text((point[0] - 26, point[1] + 15), label, fill=ink, font=mono)
        draw.rectangle((margin + 12, top + 10, margin + max(195, width // 3), top + 36), fill=ink)
        draw.text((margin + 20, top + 15), "AN ART IN MOTION", fill=paper, font=mono)
    elif role == "lineage_concept":
        draw.text((margin, max(48, height // 7)), "RELATIONSHIPS NEED VERBS.", fill=ink, font=heading)
        rows = (
            ("JIGORO KANO", "FOUNDED • 1882", "KODOKAN"),
            ("MITSUYO MAEDA", "TAUGHT IN", "BELÉM"),
        )
        for index, (source, relation, target) in enumerate(rows):
            y = max(105, height // 3) + index * max(78, height // 4)
            box_w = int(width * 0.25)
            source_x = margin
            target_x = width - margin - box_w
            draw.rounded_rectangle((source_x, y, source_x + box_w, y + 48), radius=4, fill=indigo, outline=ink, width=line_width)
            draw.rounded_rectangle((target_x, y, target_x + box_w, y + 48), radius=4, fill=rust if index else ochre, outline=ink, width=line_width)
            draw.text((source_x + box_w // 2, y + 24), source, fill=paper, font=mono, anchor="mm")
            draw.text((target_x + box_w // 2, y + 24), target, fill=ink if index == 0 else paper, font=mono, anchor="mm")
            line_y = y + 24
            draw.line((source_x + box_w + 8, line_y, target_x - 8, line_y), fill=jade, width=max(3, line_width))
            draw.polygon([(target_x - 8, line_y), (target_x - 20, line_y - 6), (target_x - 20, line_y + 6)], fill=jade)
            label_w = max(112, width // 5)
            label_x = (width - label_w) // 2
            draw.rectangle((label_x, line_y - 14, label_x + label_w, line_y + 14), fill=paper, outline=jade, width=max(1, line_width // 2))
            draw.text((width // 2, line_y), relation, fill=ink, font=mono, anchor="mm")
        draw.text((margin, content_bottom - 8), "No names + no sourced verb = no graph.", fill=rust, font=mono, anchor="ls")

    draw.rectangle((0, height - rail_height, width, height), fill=ink)
    draw.text((margin, height - rail_height + max(5, rail_height // 4)), f"SOURCE  {_citation_label(treatment)}", fill=paper, font=mono)
    draw.text((width - max(78, width // 7), height - rail_height + max(5, rail_height // 4)), f"FOLIO {DOCUMENTARY_STYLE_BOARD_ROLES.index(role) + 1:02d}", fill=jade, font=mono)
    return image


def _draw_frame(
    role: str,
    function: str,
    treatment: Mapping[str, Any],
    *,
    width: int,
    height: int,
    palette: Mapping[str, Any],
    asset_images: Sequence[Image.Image] = (),
) -> Image.Image:
    paper = _color(palette.get("paper"), _DEFAULT_PALETTE["paper"])
    ink = _color(palette.get("ink"), _DEFAULT_PALETTE["ink"])
    background = _color(palette.get("background"), _DEFAULT_PALETTE["background"])
    surface = _color(palette.get("surface"), _DEFAULT_PALETTE["surface"])
    rust = _color(palette.get("rust"), _DEFAULT_PALETTE["rust"])
    indigo = _color(palette.get("indigo"), _DEFAULT_PALETTE["indigo"])
    jade = _color(palette.get("jade"), _DEFAULT_PALETTE["jade"])
    ochre = _color(palette.get("ochre"), _DEFAULT_PALETTE["ochre"])
    muted = _color(palette.get("muted"), _DEFAULT_PALETTE["muted"])
    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    heading = _font(max(10, width // 30))
    body = _font(max(8, width // 46))
    mono = _font(max(8, width // 66), mono=True)
    title, subtitle = _role_title(role)
    asset = asset_images[0] if asset_images else None
    rail_height = max(20, height // 11)
    content_height = height - rail_height

    if asset is not None and role in {
        "cold_open",
        "archive",
        "illustration",
        "document",
        "lineage_concept",
    }:
        image.paste(_cover(asset, (width, content_height)), (0, 0))
        draw = ImageDraw.Draw(image)

    if role == "cold_open":
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        layer = ImageDraw.Draw(overlay)
        layer.rectangle((0, 0, width, height), fill=(11, 15, 20, 54))
        layer.rectangle((0, 0, max(5, width // 80), height), fill=rust)
        image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(image)
    elif role == "archive":
        if asset is not None:
            portrait_width = max(1, int(width * 0.54))
            portrait = _contain(
                ImageEnhance.Contrast(asset.convert("L").convert("RGB")).enhance(1.22),
                (portrait_width, content_height),
                background=surface,
            )
            blurred = _cover(asset, (width, content_height)).filter(
                ImageFilter.GaussianBlur(max(2, width // 80))
            )
            blurred = ImageEnhance.Brightness(blurred).enhance(0.23)
            image.paste(blurred, (0, 0))
            image.paste(portrait, (width - portrait_width, 0))
            draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, int(width * 0.48), content_height), fill=background)
        draw.line(
            (int(width * 0.48), 0, int(width * 0.48), content_height),
            fill=jade,
            width=max(2, width // 180),
        )
        draw.text(
            (max(12, width // 25), int(height * 0.23)),
            "ARCHIVE / CONTEXT",
            fill=jade,
            font=mono,
        )
    elif role == "illustration" and asset is None:
        draw.rounded_rectangle(
            (
                max(10, width // 30),
                max(10, height // 18),
                int(width * 0.39),
                int(height * 0.18),
            ),
            max(3, width // 120),
            fill=ochre,
        )
        draw.text(
            (max(16, width // 24), max(14, height // 13)),
            "ILLUSTRATION / RECONSTRUCTION",
            fill=background,
            font=mono,
        )
    elif role == "document":
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        layer = ImageDraw.Draw(overlay)
        layer.rectangle(
            (0, 0, int(width * 0.34), height),
            fill=(11, 15, 20, 226),
        )
        layer.rectangle(
            (int(width * 0.33), 0, int(width * 0.34), height),
            fill=rust,
        )
        image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(image)
    elif role == "map_timeline":
        draw.rectangle((0, 0, width, height), fill=background)
        draw.arc(
            (
                int(width * 0.13),
                int(height * 0.28),
                int(width * 0.89),
                int(height * 0.78),
            ),
            195,
            342,
            fill=jade,
            width=max(3, width // 130),
        )
        nodes = (
            (0.15, "JAPAN", "1882"),
            (0.42, "GLOBAL CIRCUIT", "1900s"),
            (0.76, "BELÉM", "1910s"),
        )
        baseline = int(height * 0.66)
        draw.line(
            (int(width * 0.12), baseline, int(width * 0.88), baseline),
            fill=muted,
            width=max(2, width // 250),
        )
        for index, (fraction, label, date) in enumerate(nodes):
            x = int(width * fraction)
            radius = max(5, width // 58)
            draw.ellipse(
                (x - radius, baseline - radius, x + radius, baseline + radius),
                fill=ochre if index == 1 else rust,
                outline=paper,
                width=max(1, width // 320),
            )
            draw.text(
                (x - radius * 2, baseline + radius + 5),
                date,
                fill=paper,
                font=mono,
            )
            draw.text(
                (x - radius * 2, baseline - radius - max(18, height // 13)),
                label,
                fill=paper,
                font=mono,
            )
    elif role == "lineage_concept" and asset is None:
        points = [
            (width * 0.20, height * 0.56),
            (width * 0.48, height * 0.42),
            (width * 0.78, height * 0.55),
            (width * 0.48, height * 0.73),
        ]
        for first, second in ((0, 1), (1, 2), (1, 3)):
            draw.line((*points[first], *points[second]), fill=jade, width=max(2, width // 150))
        for index, point in enumerate(points):
            radius = max(7, width // 32) if index == 1 else max(5, width // 44)
            draw.ellipse(
                (
                    point[0] - radius,
                    point[1] - radius,
                    point[0] + radius,
                    point[1] + radius,
                ),
                fill=indigo if index != 3 else ochre,
                outline=paper,
                width=max(1, width // 260),
            )

    # Editorial hierarchy remains consistent while each role retains a unique
    # composition. Citations stay in a dedicated bottom rail, never over the
    # primary subject.
    draw = ImageDraw.Draw(image)
    text_x = max(14, width // 24)
    if role == "archive":
        title_y = int(height * 0.34)
    elif role == "document":
        title_y = int(height * 0.27)
    else:
        title_y = int(height * 0.17)
    if role in {"archive", "document", "map_timeline"}:
        draw.multiline_text(
            (text_x, max(10, title_y)),
            title,
            fill=paper,
            font=heading,
            spacing=max(2, height // 70),
        )
        title_lines = title.count("\n") + 1
        draw.text(
            (
                text_x,
                max(
                    24,
                    title_y
                    + title_lines * max(18, height // 13),
                ),
            ),
            subtitle,
            fill=muted if role != "map_timeline" else jade,
            font=body,
        )
    elif role == "cold_open":
        draw.text(
            (text_x, max(12, height // 18)),
            "HISTORY OF BJJ  /  EPISODE 1",
            fill=paper,
            font=mono,
        )
    draw.rectangle(
        (0, height - rail_height, width, height),
        fill=ink,
    )
    draw.text(
        (text_x, height - rail_height + max(4, rail_height // 4)),
        f"SOURCE  {_citation_label(treatment)}",
        fill=paper,
        font=mono,
    )
    draw.text(
        (width - max(90, width // 5), max(7, height // 40)),
        role.replace("_", " ").upper(),
        fill=jade,
        font=mono,
    )
    return image


def _draw_generated_editorial_frame(
    role: str,
    treatment: Mapping[str, Any],
    *,
    width: int,
    height: int,
    palette: Mapping[str, Any],
    asset_images: Sequence[Image.Image],
) -> Image.Image:
    """Compose reviewed generated plates without treating them as evidence."""

    if role not in {
        "archive",
        "cold_open",
        "concept_mechanics",
        "illustration",
        "lineage_concept",
        "document",
        "map_timeline",
    }:
        raise DocumentaryStyleBoardError(
            f"generated editorial preview is not supported for role {role!r}"
        )
    paper = _color(palette.get("paper"), "#F1E3C5")
    ink = _color(palette.get("ink"), "#171A1D")
    rust = _color(
        palette.get("comic_red") or palette.get("rust"),
        "#D7533F",
    )
    jade = _color(palette.get("jade"), "#2F806C")
    background = _color(palette.get("background"), "#0D1117")
    mono = _font(max(8, width // 67), mono=True)
    heading = _font(max(12, width // 25))
    rail_height = max(23, height // 10)
    content_height = height - rail_height
    image = Image.new("RGB", (width, height), background)

    if role == "cold_open":
        if len(asset_images) != 2:
            raise DocumentaryStyleBoardError(
                "generated cold_open preview requires battlefield and institution plates"
            )
        split = int(width * 0.56)
        image.paste(_cover(asset_images[0], (split, content_height)), (0, 0))
        image.paste(
            _cover(asset_images[1], (width - split, content_height)),
            (split, 0),
        )
        wash = Image.new("RGBA", (width, content_height), (0, 0, 0, 0))
        wash_draw = ImageDraw.Draw(wash)
        wash_draw.rectangle((0, 0, split, content_height), fill=(10, 8, 7, 34))
        wash_draw.rectangle(
            (split, 0, width, content_height),
            fill=(15, 20, 24, 22),
        )
        image.paste(
            Image.alpha_composite(
                image.crop((0, 0, width, content_height)).convert("RGBA"),
                wash,
            ).convert("RGB"),
            (0, 0),
        )
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            (split - max(2, width // 320), 0, split + max(2, width // 320), content_height),
            fill=paper,
        )
        draw.rectangle((0, 0, split, max(30, height // 11)), fill=ink)
        draw.rectangle(
            (split, 0, width, max(30, height // 11)),
            fill=background,
        )
        draw.text(
            (max(12, width // 35), max(8, height // 50)),
            "THE LEGEND",
            fill=rust,
            font=mono,
        )
        draw.text(
            (split + max(12, width // 45), max(8, height // 50)),
            "THE INSTITUTION",
            fill=jade,
            font=mono,
        )
        draw.multiline_text(
            (max(14, width // 35), content_height - max(90, height // 4)),
            "THE USEFUL\nSTARTING POINT",
            fill=paper,
            font=heading,
            spacing=2,
        )
    elif role == "archive":
        if len(asset_images) != 1:
            raise DocumentaryStyleBoardError(
                "generated archive preview requires exactly one period plate"
            )
        image.paste(_cover(asset_images[0], (width, content_height)), (0, 0))
        overlay = Image.new("RGBA", (width, content_height), (0, 0, 0, 0))
        layer = ImageDraw.Draw(overlay)
        layer.rectangle((0, 0, width, max(42, height // 8)), fill=(13, 17, 23, 196))
        layer.rectangle((0, content_height - max(66, height // 6), width, content_height), fill=(13, 17, 23, 145))
        image.paste(
            Image.alpha_composite(
                image.crop((0, 0, width, content_height)).convert("RGBA"),
                overlay,
            ).convert("RGB"),
            (0, 0),
        )
        draw = ImageDraw.Draw(image)
        draw.text(
            (max(14, width // 32), max(10, height // 45)),
            "ARCHIVE / ILLUSTRATED CONTEXT",
            fill=jade,
            font=mono,
        )
        draw.multiline_text(
            (max(14, width // 32), content_height - max(58, height // 7)),
            "THE RECORD\nSETS THE TONE.",
            fill=paper,
            font=heading,
            spacing=2,
        )
    elif role == "illustration":
        if not asset_images:
            raise DocumentaryStyleBoardError(
                "generated illustration preview requires an image"
            )
        image.paste(_cover(asset_images[0], (width, content_height)), (0, 0))
        overlay = Image.new("RGBA", (width, content_height), (0, 0, 0, 0))
        layer = ImageDraw.Draw(overlay)
        layer.rectangle(
            (0, 0, width, max(46, height // 8)),
            fill=(13, 17, 23, 208),
        )
        layer.rectangle(
            (0, content_height - max(72, height // 5), width, content_height),
            fill=(13, 17, 23, 145),
        )
        image.paste(
            Image.alpha_composite(
                image.crop((0, 0, width, content_height)).convert("RGBA"),
                overlay,
            ).convert("RGB"),
            (0, 0),
        )
        draw = ImageDraw.Draw(image)
        draw.text(
            (max(14, width // 32), max(10, height // 45)),
            "ILLUSTRATION / RECONSTRUCTION",
            fill=paper,
            font=mono,
        )
        draw.multiline_text(
            (max(14, width // 32), content_height - max(62, height // 6)),
            "THE ART\nCROSSES WATER.",
            fill=paper,
            font=heading,
            spacing=2,
        )
    elif role == "document":
        if len(asset_images) != 1:
            raise DocumentaryStyleBoardError(
                "generated document world requires exactly one background plate"
            )
        image.paste(_cover(asset_images[0], (width, content_height)), (0, 0))
        dimmer = Image.new(
            "RGBA",
            (width, content_height),
            (8, 10, 12, 82),
        )
        image.paste(
            Image.alpha_composite(
                image.crop((0, 0, width, content_height)).convert("RGBA"),
                dimmer,
            ).convert("RGB"),
            (0, 0),
        )
        draw = ImageDraw.Draw(image)
        card_left = int(width * 0.42)
        card_top = max(42, height // 9)
        card_right = width - max(24, width // 24)
        card_bottom = content_height - max(20, height // 18)
        draw.rectangle(
            (
                card_left + max(5, width // 150),
                card_top + max(5, width // 150),
                card_right + max(5, width // 150),
                card_bottom + max(5, width // 150),
            ),
            fill="#090B0D",
        )
        draw.rectangle(
            (card_left, card_top, card_right, card_bottom),
            fill="#F5E8C9",
            outline=ink,
            width=max(2, width // 250),
        )
        draw.text(
            (card_left + 18, card_top + 16),
            "WHAT THE RECORD ACTUALLY SUPPORTS",
            fill=rust,
            font=mono,
        )
        for index, fraction in enumerate((0.82, 0.68, 0.88, 0.59, 0.74)):
            y = card_top + 55 + index * max(24, height // 14)
            if index == 2:
                draw.rectangle(
                    (
                        card_left + 15,
                        y - 4,
                        card_left
                        + int((card_right - card_left) * fraction),
                        y + 14,
                    ),
                    fill="#F4D35E",
                )
            draw.line(
                (
                    card_left + 22,
                    y + 5,
                    card_left
                    + int((card_right - card_left) * fraction),
                    y + 5,
                ),
                fill=ink,
                width=max(2, width // 260),
            )
        draw.rectangle(
            (0, 0, max(205, width // 3), max(34, height // 10)),
            fill=ink,
        )
        draw.text(
            (max(12, width // 35), max(9, height // 45)),
            "ILLUSTRATED ARCHIVE SET",
            fill=paper,
            font=mono,
        )
        draw.text(
            (max(16, width // 30), content_height - max(72, height // 5)),
            "THE WORLD\nSETS THE TONE.",
            fill=paper,
            font=heading,
            spacing=2,
        )
        draw.text(
            (card_right - max(165, width // 4), card_bottom - 25),
            "locator • page • date",
            fill="#324C73",
            font=mono,
        )
    elif role == "lineage_concept":
        if len(asset_images) != 1:
            raise DocumentaryStyleBoardError(
                "generated lineage scroll requires exactly one background plate"
            )
        image.paste(_cover(asset_images[0], (width, content_height)), (0, 0))
        overlay = Image.new("RGBA", (width, content_height), (0, 0, 0, 0))
        layer = ImageDraw.Draw(overlay)
        layer.rectangle((0, 0, width, max(42, height // 8)), fill=(13, 17, 23, 196))
        image.paste(
            Image.alpha_composite(
                image.crop((0, 0, width, content_height)).convert("RGBA"),
                overlay,
            ).convert("RGB"),
            (0, 0),
        )
        draw = ImageDraw.Draw(image)
        draw.text(
            (max(14, width // 32), max(10, height // 45)),
            "LINEAGE SCROLL / RELATIONSHIPS, NOT A SINGLE ARROW",
            fill=paper,
            font=mono,
        )
        medallions = (
            (0.50, 0.29, "INSTITUTION"),
            (0.31, 0.62, "TEACHING NETWORK"),
            (0.69, 0.62, "RECORDED BRANCH"),
        )
        for fraction_x, fraction_y, label in medallions:
            x = int(width * fraction_x)
            y = int(content_height * fraction_y)
            box_width = max(88, width // 5)
            draw.rounded_rectangle(
                (x - box_width // 2, y - 14, x + box_width // 2, y + 14),
                radius=5,
                fill=(23, 28, 32, 212),
                outline=jade,
                width=max(1, width // 320),
            )
            draw.text((x, y), label, fill=paper, font=mono, anchor="mm")
        draw.rectangle(
            (int(width * 0.33), content_height - max(42, height // 9), int(width * 0.67), content_height - 12),
            fill=(244, 235, 215, 226),
            outline=rust,
            width=max(1, width // 320),
        )
        draw.text(
            (width // 2, content_height - max(26, height // 16)),
            "READ THE BRANCHES AS QUESTIONS",
            fill=ink,
            font=mono,
            anchor="mm",
        )
    elif role == "concept_mechanics":
        if len(asset_images) != 1:
            raise DocumentaryStyleBoardError(
                "generated concept cutaway requires exactly one background plate"
            )
        image.paste(_cover(asset_images[0], (width, content_height)), (0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            (max(10, width // 36), max(14, height // 18), int(width * 0.36), content_height - max(26, height // 12)),
            fill=(13, 17, 23, 214),
            outline=rust,
            width=max(1, width // 320),
        )
        draw.text(
            (max(20, width // 25), max(28, height // 12)),
            "CONCEPT / ADAPTATION",
            fill=jade,
            font=mono,
        )
        draw.multiline_text(
            (max(20, width // 25), max(58, height // 7)),
            "A SYSTEM\nCHANGES\nIN CONTEXT.",
            fill=paper,
            font=heading,
            spacing=2,
        )
        draw.text(
            (max(20, width // 25), content_height - max(54, height // 8)),
            "FORCE  •  LEVER  •  CHOICE",
            fill=ochre,
            font=mono,
        )
    else:
        if len(asset_images) != 1:
            raise DocumentaryStyleBoardError(
                "generated map world requires exactly one background plate"
            )
        image.paste(_cover(asset_images[0], (width, content_height)), (0, 0))
        tint = Image.new(
            "RGBA",
            (width, content_height),
            (7, 12, 15, 36),
        )
        image.paste(
            Image.alpha_composite(
                image.crop((0, 0, width, content_height)).convert("RGBA"),
                tint,
            ).convert("RGB"),
            (0, 0),
        )
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            (max(14, width // 35), max(14, height // 30), int(width * 0.42), max(54, height // 7)),
            fill=ink,
        )
        draw.text(
            (max(24, width // 28), max(25, height // 17)),
            "AN ART IN MOTION",
            fill=paper,
            font=mono,
        )
        start = (int(width * 0.16), int(content_height * 0.70))
        middle = (int(width * 0.49), int(content_height * 0.48))
        end = (int(width * 0.83), int(content_height * 0.67))
        route_points = [
            start,
            (int(width * 0.32), int(content_height * 0.43)),
            middle,
            (int(width * 0.67), int(content_height * 0.42)),
            end,
        ]
        _draw_wobbly_line(
            draw,
            route_points,
            fill=jade,
            width=max(5, width // 120),
        )
        labels = (
            (start, "JAPAN", "1882"),
            (middle, "GLOBAL CIRCUIT", "1900s"),
            (end, "BELÉM", "1910s"),
        )
        for point, label, date in labels:
            radius = max(7, width // 70)
            draw.ellipse(
                (
                    point[0] - radius,
                    point[1] - radius,
                    point[0] + radius,
                    point[1] + radius,
                ),
                fill=rust,
                outline=paper,
                width=max(2, width // 300),
            )
            draw.rectangle(
                (
                    point[0] - max(40, width // 15),
                    point[1] + radius + 5,
                    point[0] + max(48, width // 13),
                    point[1] + radius + max(42, height // 9),
                ),
                fill=(13, 17, 23),
            )
            draw.text(
                (
                    point[0] - max(34, width // 18),
                    point[1] + radius + 9,
                ),
                label,
                fill=paper,
                font=mono,
            )
            draw.text(
                (
                    point[0] - max(34, width // 18),
                    point[1] + radius + max(24, height // 17),
                ),
                date,
                fill=paper,
                font=mono,
            )
        draw.text(
            (width - max(250, width // 2), max(16, height // 25)),
            "ILLUSTRATED WORLD  •  DATA OVERLAY IS DETERMINISTIC",
            fill=paper,
            font=mono,
        )

    draw = ImageDraw.Draw(image)
    draw.rectangle((0, height - rail_height, width, height), fill=ink)
    draw.text(
        (max(12, width // 30), height - rail_height + max(5, rail_height // 4)),
        (
            f"SOURCE  {_citation_label(treatment)}"
            if role in {"document", "map_timeline"}
            else "EDITORIAL ILLUSTRATION  •  NOT HISTORICAL EVIDENCE"
        ),
        fill=paper,
        font=mono,
    )
    draw.text(
        (width - max(96, width // 5), height - rail_height + max(5, rail_height // 4)),
        (
            "EVIDENCE OVERLAY"
            if role in {"document", "map_timeline"}
            else "REVIEW PLATE"
        ),
        fill=jade,
        font=mono,
    )
    return image


class DocumentaryStyleBoardService:
    """Build a six-role board and review packet without provider calls."""

    def __init__(self, *, width: int = 640, height: int = 360) -> None:
        if int(width) < 96 or int(height) < 96:
            raise ValueError("documentary style-board dimensions must be at least 96px")
        self.width = int(width)
        self.height = int(height)

    def build(
        self,
        art_bible: Mapping[str, Any] | str | Path | None = None,
        output_dir: str | Path | None = None,
        *,
        treatments: Mapping[str, Any] | Sequence[Any] | str | Path | None = None,
        asset_manifest: Mapping[str, Any] | str | Path | None = None,
        generated_visuals: Mapping[str, Any] | str | Path | None = None,
        current_art_bible_hash: str | None = None,
        project_root: str | Path | None = None,
        job_root: str | Path | None = None,
    ) -> dict[str, Any]:
        bible: dict[str, Any]
        if isinstance(art_bible, Mapping):
            bible = copy.deepcopy(dict(art_bible))
        elif isinstance(art_bible, (str, Path)) and Path(art_bible).is_file():
            bible = json.loads(Path(art_bible).read_text(encoding="utf-8"))
        else:
            bible = {}
        if isinstance(treatments, (str, Path)) and Path(treatments).is_file():
            treatments = json.loads(Path(treatments).read_text(encoding="utf-8"))
        treatment_list = _normalize_treatments(treatments)
        resolved_root = Path(project_root or Path.cwd()).resolve()
        assets = _asset_records(
            asset_manifest,
            project_root=resolved_root,
            job_root=Path(job_root).resolve() if job_root is not None else None,
        )
        generated_by_role: dict[str, list[dict[str, Any]]] = {}
        generated_batch: dict[str, Any] = {}
        if generated_visuals is not None:
            if job_root is None:
                raise DocumentaryStyleBoardError(
                    "job_root is required for generated visual candidates"
                )
            generated_by_role, generated_batch = style_board_candidates_by_role(
                generated_visuals,
                job_root=job_root,
            )
        palette = dict(_DEFAULT_PALETTE)
        if isinstance(bible.get("palette"), Mapping):
            palette.update({str(key): str(value) for key, value in bible["palette"].items()})
        art_hash = str(current_art_bible_hash or bible.get("artifact_hash") or canonical_sha256(bible)).lower()
        if len(art_hash) != 64:
            raise DocumentaryStyleBoardError("art_bible_hash must be a SHA-256 digest")
        output = Path(output_dir or "style_board")
        output.mkdir(parents=True, exist_ok=True)
        still_root = output / "stills"
        still_root.mkdir(parents=True, exist_ok=True)
        stills: list[dict[str, Any]] = []
        art_bible_id = str(
            bible.get("id") or "combat-history-longform-cutout-fork-v1"
        )
        branded_literature = art_bible_id in {
            "combat-history-branded-literature-v1",
            "combat-history-longform-cutout-fork-v1",
        }
        profile_derivation = (
            bible.get("profile_derivation")
            if isinstance(bible.get("profile_derivation"), Mapping)
            else {}
        )
        profile_fork = bool(profile_derivation)
        for index, role in enumerate(DOCUMENTARY_STYLE_BOARD_ROLES):
            function, treatment = _function_for_role(role, treatment_list, index)
            asset_ids = treatment.get("asset_ids") or []
            if isinstance(asset_ids, str):
                asset_ids = [asset_ids]
            asset_images = [
                _open_asset(
                    assets[str(asset_id)],
                    width=self.width,
                    height=self.height,
                )
                for asset_id in asset_ids
                if str(asset_id) in assets
            ]
            generated_records = generated_by_role.get(role, [])
            generated_images = [
                _open_asset(
                    Path(str(item["_resolved_path"])),
                    width=self.width,
                    height=self.height,
                )
                for item in generated_records
            ]
            image = (
                _draw_generated_editorial_frame(
                    role,
                    treatment,
                    width=self.width,
                    height=self.height,
                    palette=palette,
                    asset_images=generated_images,
                )
                if generated_images
                and role
                in {
                    "archive",
                    "cold_open",
                    "lineage_concept",
                    "illustration",
                    "document",
                    "map_timeline",
                }
                else
                _draw_branded_literature_frame(
                    role,
                    treatment,
                    width=self.width,
                    height=self.height,
                    palette=palette,
                    asset_images=asset_images,
                    profile_fork=profile_fork,
                )
                if branded_literature
                else _draw_frame(
                    role,
                    function,
                    treatment,
                    width=self.width,
                    height=self.height,
                    palette=palette,
                    asset_images=asset_images,
                )
            )
            path = still_root / f"{index + 1:02d}_{role}.png"
            image.save(path, format="PNG", optimize=False, compress_level=9)
            citations = treatment.get("citations") or []
            if isinstance(citations, (str, Mapping)):
                citations = [citations]
            record: dict[str, Any] = {
                "still_id": f"still-{index + 1:02d}",
                "role": role,
                "function": function,
                "visual_type": function,
                "treatment_id": str(treatment.get("treatment_id") or f"treatment-{function.replace('_', '-')}") ,
                "asset_ids": [str(value) for value in asset_ids],
                "selected_stock_asset_ids": [
                    str(value)
                    for value in asset_ids
                    if str(value).startswith("magnific-")
                ],
                "generated_candidate_ids": [
                    str(item["id"]) for item in generated_records
                ],
                "resolved_asset_count": len(asset_images),
                "citations": copy.deepcopy(list(citations)),
                "path": path.relative_to(output).as_posix(),
                "width": image.width,
                "height": image.height,
                "image_hash": hashlib.sha256(path.read_bytes()).hexdigest(),
                "phash": _phash(image),
                "art_bible_hash": art_hash,
                "safe_zones": {"landscape": {"action_zone": "center", "caption_zone": "top"}, "vertical": {"action_zone": "middle", "caption_zone": "top"}},
                "signature": f"history:{role}:{function}",
                "uniqueness_signature": f"{role}:{function}:{index + 1}",
                "source": "deterministic_documentary_style_board",
            }
            if generated_records:
                record["source"] = "generated_editorial_preview"
                record["generated_visual_batch_hash"] = str(
                    generated_batch.get("artifact_hash") or ""
                )
                record["illustration_label"] = (
                    "AI-ASSISTED ILLUSTRATION / RECONSTRUCTION"
                )
            if branded_literature:
                record["literature_mode"] = _literature_mode_for_role(role)
            if profile_fork:
                record["production_profile_id"] = str(
                    profile_derivation.get("base_profile_id") or ""
                )
                record["production_profile_hash"] = str(
                    profile_derivation.get("base_profile_hash") or ""
                )
            if role == "illustration":
                record["illustration_label"] = str(treatment.get("illustration_label") or "ILLUSTRATION / RECONSTRUCTION")
            stills.append(record)
        sheet = Image.new("RGB", (self.width * 2, self.height * 3), _color(palette.get("paper"), _DEFAULT_PALETTE["paper"]))
        for index, still in enumerate(stills):
            with Image.open(output / still["path"]) as source:
                sheet.paste(source.convert("RGB"), ((index % 2) * self.width, (index // 2) * self.height))
        sheet_path = output / "style_board.png"
        sheet.save(sheet_path, format="PNG", optimize=False, compress_level=9)
        board_core: dict[str, Any] = {
            "schema_version": DOCUMENTARY_STYLE_BOARD_VERSION,
            "documentary_version": art_bible_id,
            "source_kind": "documentary",
            "art_bible_id": art_bible_id,
            "art_bible_hash": art_hash,
            "required_roles": list(DOCUMENTARY_STYLE_BOARD_ROLES),
            "roles": list(DOCUMENTARY_STYLE_BOARD_ROLES),
            "rubric_dimensions": list(DOCUMENTARY_RUBRIC_DIMENSIONS),
            "stills": stills,
            "still_count": len(stills),
            "selected_stock_asset_count": len(
                {
                    asset_id
                    for still in stills
                    for asset_id in still["selected_stock_asset_ids"]
                }
            ),
            "contact_sheet_path": "style_board.png",
            "contact_sheet_hash": hashlib.sha256(sheet_path.read_bytes()).hexdigest(),
            "approval_granted": False,
            "provider_calls": 0,
            "source": "deterministic_documentary_style_board",
        }
        if generated_batch:
            board_core["generated_visual_batch_hash"] = str(
                generated_batch["artifact_hash"]
            )
            board_core["generated_visual_candidate_count"] = len(
                generated_batch["items"]
            )
            board_core["selected_generated_visual_count"] = sum(
                len(values) for values in generated_by_role.values()
            )
            board_core["generation_provider"] = str(
                generated_batch.get("provider") or ""
            )
            board_core["provider_calls"] = int(
                generated_batch.get("provider_calls") or 0
            )
            board_core["source"] = "hybrid_documentary_style_board"
        if branded_literature:
            board_core["literature_modes"] = [
                "lofi_comedy",
                "historical_comic",
                "archive_evidence",
            ]
        if profile_fork:
            board_core["production_profile"] = {
                "id": str(profile_derivation.get("base_profile_id") or ""),
                "hash": str(
                    profile_derivation.get("base_profile_hash") or ""
                ),
                "contract": str(
                    profile_derivation.get("contract") or ""
                ),
            }
        board = {**board_core, "artifact_hash": canonical_sha256(board_core)}
        artifact_path = output / "style_board.json"
        artifact_path.write_text(json.dumps(board, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        review_core = {
            "schema_version": "documentary_style_board_review.v1",
            "style_board_artifact": "style_board.json",
            "contact_sheet_path": "style_board.png",
            "contact_sheet_hash": board["contact_sheet_hash"],
            "style_board_hash": board["artifact_hash"],
            "art_bible_id": board["art_bible_id"],
            "art_bible_hash": art_hash,
            "required_roles": list(DOCUMENTARY_STYLE_BOARD_ROLES),
            "rubric_dimensions": list(DOCUMENTARY_RUBRIC_DIMENSIONS),
            "approval_granted": False,
            "provider_calls": 0,
        }
        if generated_batch:
            review_core["generated_visual_batch_hash"] = str(
                generated_batch["artifact_hash"]
            )
            review_core["generated_visual_candidate_count"] = len(
                generated_batch["items"]
            )
            review_core["provider_calls"] = int(
                generated_batch.get("provider_calls") or 0
            )
        review = {**review_core, "artifact_hash": canonical_sha256(review_core)}
        review_path = output / "review-packet.json"
        review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {**board, "artifact_path": artifact_path.as_posix(), "review_packet_path": review_path.as_posix(), "contact_sheet_path": sheet_path.as_posix()}

    render = build
    create = build

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        payload = job.input_payload if isinstance(job.input_payload, Mapping) else {}
        configs = ctx.configs if isinstance(ctx.configs, Mapping) else {}
        bible = payload.get("art_bible") or payload.get("art_bible_path") or configs.get("art_bible") or ctx.job_dir / "art_bible.json"
        treatments = payload.get("treatments") or payload.get("visual_treatment") or ctx.job_dir / "visual_treatment.v2.json"
        selected_assets = (
            ctx.job_dir
            / "asset_selection"
            / "resolved"
            / "resolved_assets.json"
        )
        assets = payload.get("asset_manifest")
        if not assets:
            assets = (
                selected_assets
                if selected_assets.is_file()
                else ctx.job_dir / "resolved_assets.json"
            )
        generated_visuals = ctx.job_dir / "generated_visuals" / "candidate_batch.json"
        result = self.build(
            bible,
            ctx.job_dir / "style_board",
            treatments=treatments,
            asset_manifest=assets,
            generated_visuals=(
                generated_visuals if generated_visuals.is_file() else None
            ),
            current_art_bible_hash=payload.get("art_bible_hash"),
            project_root=configs.get("project_root", Path.cwd()),
            job_root=ctx.job_dir,
        )
        return StageOutput({"artifact_path": "style_board/style_board.json", "review_packet_path": "style_board/review-packet.json", "still_count": len(result["stills"]), "art_bible_hash": result["art_bible_hash"], "approval_granted": False, "provider_calls": int(result.get("provider_calls") or 0), "generated_visual_candidate_count": int(result.get("generated_visual_candidate_count") or 0)})


def run_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    return DocumentaryStyleBoardService().run_stage(job, ctx)


__all__ = [
    "DOCUMENTARY_RUBRIC_DIMENSIONS",
    "DOCUMENTARY_STYLE_BOARD_ROLES",
    "DOCUMENTARY_STYLE_BOARD_VERSION",
    "STYLE_BOARD_ROLES",
    "STYLE_BOARD_VERSION",
    "DocumentaryStyleBoardError",
    "DocumentaryStyleBoardService",
    "run_stage",
]
