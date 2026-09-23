"""Render the single letter-B thumbnail concept and its first-frame mock.

All marks are authored SVG primitives. The thumbnail has no percentage or
other mathematical figures; the separate first-frame mock carries the
illustrative ledger evidence required by the B package. Running this module
rewrites only files in this thumbnail-b directory.
"""
from __future__ import annotations

import html
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont


THUMB_W, THUMB_H = 1280, 720
COVER_W, COVER_H = 720, 1280
FRAME_W, FRAME_H = 1280, 720
PHONE_W, PHONE_H = 168, 299

# Money Physics tokens, copied from channel-assets/money-physics/brand-tokens.json.
CREAM = "#F4E6C7"
CHARCOAL = "#25313C"
COBALT = "#1769C2"
TEAL = "#178C83"
CORAL = "#ED6A4A"
SUNFLOWER = "#F5B72E"
EVIDENCE_GROUND = "#1B1E23"
EVIDENCE_INK = "#F2F2F2"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def text(
    x: float,
    y: float,
    value: str,
    size: float,
    fill: str,
    *,
    anchor: str = "start",
    family: str = "Impact, Arial Black, Arial, sans-serif",
    weight: int | None = None,
    spacing: float | None = None,
    opacity: float | None = None,
) -> str:
    attrs = [
        f'x="{x:g}"',
        f'y="{y:g}"',
        f'fill="{fill}"',
        f'font-family="{family}"',
        f'font-size="{size:g}px"',
        f'text-anchor="{anchor}"',
    ]
    if weight is not None:
        attrs.append(f'font-weight="{weight}"')
    if spacing is not None:
        attrs.append(f'letter-spacing="{spacing:g}px"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity:g}"')
    return f'<text {" ".join(attrs)}>{esc(value)}</text>'


def rect(
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str,
    *,
    stroke: str = "none",
    sw: float = 0,
    radius: float = 0,
) -> str:
    return (
        f'<rect x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" '
        f'rx="{radius:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"/>'
    )


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    stroke: str,
    sw: float,
    *,
    dash: str | None = None,
) -> str:
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
        f'stroke="{stroke}" stroke-width="{sw:g}" stroke-linecap="round"{extra}/>'
    )


def circle(cx: float, cy: float, radius: float, fill: str, *, stroke: str = "none", sw: float = 0) -> str:
    return f'<circle cx="{cx:g}" cy="{cy:g}" r="{radius:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"/>'


def polygon(points: str, fill: str, *, stroke: str = "none", sw: float = 0) -> str:
    return f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"/>'


def svg_document(width: int, height: int, bg: str, body: list[str]) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        + "".join([rect(0, 0, width, height, bg)] + body)
        + "</svg>\n"
    )


def thumbnail_svg() -> str:
    """A single click-contract image: the work is not finished at the gate."""
    b: list[str] = []

    # The central safe column is deliberately preserved so a 9:16 cover crop
    # retains the complete headline and the human-check bottleneck.
    b += [line(290, 46, 990, 46, CHARCOAL, 6)]
    b += [text(640, 82, "AI WORKFLOW", 25, COBALT, anchor="middle",
               family="Arial, sans-serif", weight=700, spacing=4)]
    b += [text(450, 220, "STILL", 142, CHARCOAL, spacing=2)]
    b += [text(450, 355, "NEEDS", 142, CHARCOAL, spacing=2)]
    b += [text(450, 490, "YOU", 142, CORAL, spacing=2)]
    b += [line(450, 515, 620, 515, CORAL, 9)]

    # A compact authored workflow, not a software screenshot: draft -> gate ->
    # unfinished page. The gate is the visual subject that explains the words.
    b += [line(545, 574, 790, 574, CHARCOAL, 13)]
    b += [circle(545, 574, 18, TEAL, stroke=CHARCOAL, sw=5)]
    b += [text(545, 628, "DRAFT", 21, CHARCOAL, anchor="middle",
               family="Arial, sans-serif", weight=700, spacing=1)]
    b += [rect(625, 514, 64, 120, CORAL, radius=10)]
    b += [line(657, 530, 657, 618, CREAM, 10)]
    b += [text(657, 674, "HUMAN CHECK", 22, CHARCOAL, anchor="middle",
               family="Arial, sans-serif", weight=700, spacing=1)]

    # The document has a deliberately open final mark: unfinished, but not a
    # faux product UI or a fabricated screenshot.
    b += [rect(714, 505, 102, 130, CREAM, stroke=CHARCOAL, sw=6, radius=4)]
    b += [polygon("790,505 816,505 816,531", CHARCOAL)]
    b += [line(735, 535, 780, 535, CHARCOAL, 5)]
    b += [line(735, 559, 795, 559, CHARCOAL, 5)]
    b += [line(735, 583, 775, 583, CHARCOAL, 5)]
    b += [rect(735, 601, 17, 17, CREAM, stroke=CORAL, sw=4, radius=2)]
    b += [text(780, 628, "OPEN", 18, CORAL, anchor="middle",
               family="Consolas, monospace", weight=700, spacing=1)]

    # Small outer marks make the 16:9 master feel intentional without entering
    # the vertical safe column. They do not add another concept or promise.
    b += [rect(294, 560, 64, 14, SUNFLOWER, radius=7)]
    b += [rect(928, 560, 64, 14, COBALT, radius=7)]
    b += [text(640, 710, "MONEY PHYSICS", 19, CHARCOAL, anchor="middle",
               family="Arial, sans-serif", weight=700, spacing=5)]
    return svg_document(THUMB_W, THUMB_H, CREAM, b)


def first_frame_svg() -> str:
    """A cheap first-frame evidence mock for the human-review bottleneck."""
    b: list[str] = []

    b += [line(72, 56, 1208, 56, CORAL, 7)]
    b += [text(72, 98, "THE WORK STOPS AT THE HUMAN CHECK", 30, CHARCOAL,
               family="Arial, sans-serif", weight=700, spacing=2)]
    b += [text(1208, 98, "ILLUSTRATIVE", 22, COBALT, anchor="end",
               family="Consolas, monospace", weight=700, spacing=2)]

    # Left page: a model output that has structure but still needs a person.
    b += [rect(72, 136, 382, 384, CREAM, stroke=CHARCOAL, sw=7, radius=6)]
    b += [polygon("390,136 454,136 454,200", CHARCOAL)]
    b += [text(108, 190, "MODEL OUTPUT", 25, CHARCOAL, family="Arial, sans-serif",
               weight=700, spacing=1)]
    b += [line(108, 224, 392, 224, CHARCOAL, 5)]
    for y, width in ((270, 226), (306, 262), (342, 204), (378, 240)):
        b += [line(108, y, 108 + width, y, CHARCOAL, 5)]
    b += [rect(108, 424, 18, 18, TEAL, radius=3)]
    b += [line(137, 438, 278, 438, CHARCOAL, 5)]
    b += [text(108, 488, "DRAFT", 23, CORAL, family="Consolas, monospace",
               weight=700, spacing=2)]

    # Centre gate: the unresolved human decision is a state, not a fake app
    # status. The red bar makes the bottleneck legible at a glance.
    b += [line(454, 326, 528, 326, CHARCOAL, 12)]
    b += [rect(528, 206, 174, 240, CORAL, radius=18)]
    b += [circle(615, 274, 27, CREAM)]
    b += [line(615, 259, 615, 281, CHARCOAL, 8)]
    b += [circle(615, 292, 5, CHARCOAL)]
    b += [text(615, 366, "HUMAN", 28, CHARCOAL, anchor="middle",
               family="Impact, Arial Black, Arial, sans-serif", spacing=1)]
    b += [text(615, 402, "CHECK", 28, CHARCOAL, anchor="middle",
               family="Impact, Arial Black, Arial, sans-serif", spacing=1)]
    b += [text(615, 483, "WAITING", 22, CHARCOAL, anchor="middle",
               family="Consolas, monospace", weight=700, spacing=2)]
    b += [line(702, 326, 770, 326, CHARCOAL, 12, dash="10 16")]

    # Right page: the final field is intentionally open.
    b += [rect(770, 136, 438, 384, CREAM, stroke=CHARCOAL, sw=7, radius=6)]
    b += [polygon("1144,136 1208,136 1208,200", CHARCOAL)]
    b += [text(806, 190, "UNFINISHED DOCUMENT", 25, CHARCOAL,
               family="Arial, sans-serif", weight=700, spacing=1)]
    b += [line(806, 224, 1136, 224, CHARCOAL, 5)]
    for y, width in ((270, 286), (306, 244), (342, 310)):
        b += [line(806, y, 806 + width, y, CHARCOAL, 5)]
    b += [rect(806, 390, 22, 22, CREAM, stroke=CORAL, sw=5, radius=3)]
    b += [text(846, 410, "FINAL HUMAN PASS", 24, CORAL,
               family="Consolas, monospace", weight=700, spacing=1)]
    b += [line(806, 460, 1020, 460, CHARCOAL, 5)]
    b += [text(806, 494, "NOT DONE", 22, CORAL, family="Consolas, monospace",
               weight=700, spacing=2)]

    # Ledger evidence, explicitly illustrative and tied to the same-step model.
    b += [rect(72, 566, 1136, 124, EVIDENCE_GROUND, radius=10)]
    b += [text(104, 600, "ILLUSTRATIVE MODEL", 21, SUNFLOWER,
               family="Consolas, monospace", weight=700, spacing=2)]
    b += [text(104, 643, "95% / STEP", 28, EVIDENCE_INK,
               family="Consolas, monospace", weight=700)]
    b += [line(300, 634, 392, 634, EVIDENCE_INK, 5)]
    b += [polygon("392,634 374,622 374,646", EVIDENCE_INK)]
    b += [text(432, 643, "35.8% CLEAN JOB", 28, CORAL,
               family="Consolas, monospace", weight=700)]
    b += [line(760, 592, 760, 668, CHARCOAL, 3)]
    b += [text(800, 621, "TWENTY REQUIRED STEPS", 20, EVIDENCE_INK,
               family="Arial, sans-serif", weight=700, spacing=1)]
    b += [text(800, 657, "INDEPENDENT · NO RETRIES", 19, CREAM,
               family="Consolas, monospace", weight=700, spacing=1)]
    return svg_document(FRAME_W, FRAME_H, CREAM, b)


def rasterize(svg: str, out: Path, width: int, height: int) -> None:
    cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        write_to=str(out),
        output_width=width,
        output_height=height,
    )


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        Path(path),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def write_cover(full_png: Path, out: Path) -> None:
    """Cover-crop the same 16:9 render to 9:16; no re-layout or new concept."""
    image = Image.open(full_png).convert("RGB")
    crop_width = round(THUMB_H * 9 / 16)
    left = (THUMB_W - crop_width) // 2
    crop = image.crop((left, 0, left + crop_width, THUMB_H))
    crop.resize((COVER_W, COVER_H), Image.Resampling.LANCZOS).save(
        out, format="PNG", optimize=False
    )


def contact_sheet(out_dir: Path) -> None:
    thumb = Image.open(out_dir / "still-needs-you.png").convert("RGB")
    cover = Image.open(out_dir / "still-needs-you-cover-9x16.png").convert("RGB")
    frame = Image.open(out_dir / "first-frame-human-review.png").convert("RGB")
    label = font("C:/Windows/Fonts/arialbd.ttf", 24)
    small = font("C:/Windows/Fonts/arialbd.ttf", 18)
    sheet = Image.new("RGB", (1360, 860), CREAM)
    draw = ImageDraw.Draw(sheet)
    draw.text((36, 24), "B PACKAGE · THUMBNAIL + FIRST-FRAME GEOMETRY CHECK", fill=CHARCOAL, font=label)

    thumb_preview = thumb.resize((640, 360), Image.Resampling.LANCZOS)
    frame_preview = frame.resize((640, 360), Image.Resampling.LANCZOS)
    sheet.paste(thumb_preview, (36, 76))
    sheet.paste(frame_preview, (684, 76))
    draw.text((36, 446), "16:9 thumbnail · 1280×720", fill=CHARCOAL, font=small)
    draw.text((684, 446), "first-frame mock · 1280×720", fill=CHARCOAL, font=small)

    cover_preview = cover.resize((270, 480), Image.Resampling.LANCZOS)
    sheet.paste(cover_preview, (545, 490))
    draw.rectangle((543, 488, 816, 972), outline=CHARCOAL, width=2)
    draw.text((852, 620), "9:16 cover crop", fill=CHARCOAL, font=label)
    draw.text((852, 660), "720×1280 · same source render", fill=CHARCOAL, font=small)
    draw.text((852, 700), "No percentage figures on thumbnail", fill=CHARCOAL, font=small)
    sheet.save(out_dir / "contact-sheet.png", format="PNG", optimize=False)

    thumb.resize((PHONE_W, PHONE_H), Image.Resampling.LANCZOS).save(
        out_dir / "still-needs-you-phone-168.png", format="PNG", optimize=False
    )
    cover.resize((PHONE_W, PHONE_H), Image.Resampling.LANCZOS).save(
        out_dir / "still-needs-you-cover-phone-168.png", format="PNG", optimize=False
    )


def main() -> None:
    out_dir = Path(__file__).resolve().parent

    thumb_svg = thumbnail_svg()
    (out_dir / "still-needs-you.svg").write_text(thumb_svg, encoding="utf-8", newline="\n")
    rasterize(thumb_svg, out_dir / "still-needs-you.png", THUMB_W, THUMB_H)
    write_cover(
        out_dir / "still-needs-you.png",
        out_dir / "still-needs-you-cover-9x16.png",
    )

    frame_svg = first_frame_svg()
    (out_dir / "first-frame-human-review.svg").write_text(
        frame_svg, encoding="utf-8", newline="\n"
    )
    rasterize(
        frame_svg,
        out_dir / "first-frame-human-review.png",
        FRAME_W,
        FRAME_H,
    )
    contact_sheet(out_dir)
    print(f"Thumbnail: {out_dir / 'still-needs-you.png'} ({THUMB_W}x{THUMB_H})")
    print(f"Cover crop: {out_dir / 'still-needs-you-cover-9x16.png'} ({COVER_W}x{COVER_H})")
    print(f"First frame: {out_dir / 'first-frame-human-review.png'} ({FRAME_W}x{FRAME_H})")
    print(f"Contact sheet: {out_dir / 'contact-sheet.png'}")


if __name__ == "__main__":
    main()
