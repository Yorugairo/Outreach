"""Render the two authored thumbnail candidates for the AI usefulness short.

The artwork is deliberately procedural: every figure is copied from the
project's illustrative model, and no image-generation or network dependency is
used.  Running this file rewrites only sibling thumbnail assets.
"""
from __future__ import annotations

import html
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont


W, H = 1080, 1920
SQUARE = 1200
PHONE_W = 168
PHONE_H = round(H * PHONE_W / W)

# Money Physics brand tokens (brand-tokens.json / BRAND-SHEET.md).
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
    family: str = "Impact, Arial, sans-serif",
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


def rect(x: float, y: float, w: float, h: float, fill: str, *, stroke: str = "none", sw: float = 0, r: float = 0) -> str:
    return (
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
        f'rx="{r:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"/>'
    )


def line(x1: float, y1: float, x2: float, y2: float, stroke: str, sw: float, *, dash: str | None = None) -> str:
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{sw:g}" stroke-linecap="round"{extra}/>'


def circle(cx: float, cy: float, radius: float, fill: str, *, stroke: str = "none", sw: float = 0) -> str:
    return f'<circle cx="{cx:g}" cy="{cy:g}" r="{radius:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"/>'


def svg_document(width: int, height: int, bg: str, body: list[str]) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">' + "".join([rect(0, 0, width, height, bg)] + body) + "</svg>\n"
    )


def svg_doc(bg: str, body: list[str]) -> str:
    return svg_document(W, H, bg, body)


def candidate_a() -> str:
    """Charcoal canvas: the 36% to 82% contrast is the hero."""
    b: list[str] = []
    # Quiet top rule and two-line package question.
    b += [line(90, 104, 990, 104, SUNFLOWER, 7)]
    b += [text(90, 158, "AI DEVELOPMENT", 31, SUNFLOWER, family="Arial, sans-serif", weight=700, spacing=5)]
    b += [text(90, 315, "SLOWER.", 160, EVIDENCE_INK, spacing=2)]
    b += [text(90, 483, "MORE USEFUL?", 142, SUNFLOWER, spacing=1)]
    b += [text(90, 558, "ILLUSTRATIVE · INDEPENDENT STEPS", 34, CREAM, family="Arial, sans-serif", weight=700, spacing=3)]

    # One measured-looking exhibit, with no card pile: the comparison is the image.
    b += [rect(90, 600, 900, 840, EVIDENCE_GROUND, stroke=CREAM, sw=4, r=28)]
    b += [text(135, 690, "SAME 20 STEPS", 62, EVIDENCE_INK, spacing=2)]
    b += [text(135, 758, "TASKS FINISHED CLEANLY", 32, CREAM, family="Arial, sans-serif", weight=700, spacing=2)]
    b += [line(135, 800, 945, 800, CHARCOAL, 4)]

    # Numeric labels occupy their own row; each bar sits below its percentage,
    # so no geometry or glyph can collide at thumbnail scale.
    b += [text(135, 995, "36%", 170, CORAL)]
    b += [text(895, 985, "95% / STEP", 31, CREAM, anchor="end", family="Consolas, monospace", weight=700, spacing=1)]
    b += [rect(135, 1018, 810, 92, CHARCOAL, stroke=CREAM, sw=3, r=18)]
    b += [rect(135, 1018, 292, 92, CORAL, r=18)]
    b += [line(427, 1032, 427, 1096, CREAM, 4)]

    # Second illustrative scenario; the longer bar and teal percentage are the
    # visual payoff, not a claim about any actual model.
    b += [text(135, 1265, "82%", 170, TEAL)]
    b += [text(895, 1255, "99% / STEP", 31, CREAM, anchor="end", family="Consolas, monospace", weight=700, spacing=1)]
    b += [rect(135, 1288, 810, 92, CHARCOAL, stroke=CREAM, sw=3, r=18)]
    b += [rect(135, 1288, 664, 92, TEAL, r=18)]
    b += [line(799, 1302, 799, 1366, CREAM, 4)]

    # One honest model line; the repeated bottom comparison is intentionally
    # omitted so the mechanism stays dominant.
    b += [line(135, 1410, 945, 1410, CHARCOAL, 4)]
    b += [text(540, 1550, "ILLUSTRATIVE: P(clean) = p²⁰", 50, EVIDENCE_INK, anchor="middle", family="Consolas, monospace", weight=700, spacing=1)]
    b += [text(540, 1800, "MONEY PHYSICS", 36, CREAM, anchor="middle", family="Arial, sans-serif", weight=700, spacing=8)]
    return svg_doc(CHARCOAL, b)


def candidate_b() -> str:
    """Cream canvas: a clean twenty-step rail plus the result."""
    b: list[str] = []
    b += [line(90, 104, 990, 104, CHARCOAL, 7)]
    b += [text(90, 158, "AI DEVELOPMENT", 31, COBALT, family="Arial, sans-serif", weight=700, spacing=5)]
    b += [text(90, 315, "SLOWER.", 160, CHARCOAL, spacing=2)]
    b += [text(90, 483, "MORE USEFUL?", 142, SUNFLOWER, spacing=1)]
    b += [text(90, 558, "ILLUSTRATIVE · INDEPENDENT STEPS", 34, CHARCOAL, family="Arial, sans-serif", weight=700, spacing=3)]

    # The twenty blocks are a single authored motif, not twenty decorative cards.
    b += [rect(90, 600, 900, 470, CREAM, stroke=CHARCOAL, sw=5, r=28)]
    b += [text(135, 690, "SAME 20 STEPS", 62, CHARCOAL, spacing=2)]
    b += [text(135, 758, "ONE ERROR CAN BREAK THE RUN", 31, CHARCOAL, family="Arial, sans-serif", weight=700, spacing=1)]
    start_x, start_y, step_w, step_h, gap = 140, 835, 72, 72, 16
    for row in range(2):
        for col in range(10):
            x = start_x + col * (step_w + gap)
            y = start_y + row * (step_h + 18)
            # Neutral steps show the repeated structure. One coral step marks
            # the model's single-error premise without implying a measured
            # 50% failure pattern.
            fill = CORAL if (row == 0 and col == 4) else CHARCOAL
            b += [rect(x, y, step_w, step_h, fill, stroke=CHARCOAL, sw=4, r=12)]
    b += [text(540, 1040, "p × p × p × … × p", 40, CHARCOAL, anchor="middle", family="Consolas, monospace", weight=700)]

    # Bottom result rail. The arrow is a state change between two exact model
    # cases; the boxes remain one diagram rather than separate information cards.
    b += [text(135, 1205, "95% EACH STEP", 34, CORAL, family="Consolas, monospace", weight=700, spacing=1)]
    b += [text(135, 1350, "36%", 178, CHARCOAL)]
    b += [text(135, 1410, "FINISH CLEANLY", 30, CHARCOAL, family="Arial, sans-serif", weight=700, spacing=2)]
    # Keep the arrow in the clear gap between the result glyph boxes.
    b += [line(455, 1320, 655, 1320, CHARCOAL, 10)]
    b += [line(605, 1265, 655, 1320, CHARCOAL, 10)]
    b += [line(605, 1375, 655, 1320, CHARCOAL, 10)]
    b += [text(735, 1205, "99% EACH STEP", 34, TEAL, family="Consolas, monospace", weight=700, spacing=1)]
    b += [text(735, 1350, "82%", 178, CHARCOAL)]
    b += [text(735, 1410, "FINISH CLEANLY", 30, CHARCOAL, family="Arial, sans-serif", weight=700, spacing=2)]

    b += [rect(90, 1515, 900, 165, CHARCOAL, r=22)]
    b += [text(540, 1615, "ILLUSTRATIVE MODEL · NO BENCHMARK CLAIM", 34, CREAM, anchor="middle", family="Arial, sans-serif", weight=700, spacing=2)]
    b += [text(540, 1810, "MONEY PHYSICS", 36, CHARCOAL, anchor="middle", family="Arial, sans-serif", weight=700, spacing=8)]
    return svg_doc(CREAM, b)


def square_chart() -> str:
    """Companion square chart using the same illustrative p^20 exhibit."""
    b: list[str] = []
    b += [line(84, 76, 1116, 76, CHARCOAL, 7)]
    b += [text(84, 210, "Small reliability gains.", 94, CHARCOAL, spacing=1)]
    b += [text(84, 314, "More finished work.", 94, TEAL, spacing=1)]
    b += [text(84, 382, "Illustration, not an AI benchmark", 32, CHARCOAL, family="Arial, sans-serif", weight=700, spacing=1)]

    # One compact chart, with both exact probability cases from the dossier.
    b += [rect(84, 450, 1032, 590, EVIDENCE_GROUND, stroke=CHARCOAL, sw=5, r=24)]
    b += [text(132, 526, "SAME 20 INDEPENDENT STEPS", 39, EVIDENCE_INK, family="Arial, sans-serif", weight=700, spacing=2)]
    b += [text(132, 588, "CLEAN COMPLETION (%)", 27, CREAM, family="Consolas, monospace", weight=700, spacing=2)]
    # Grid line marks the 100% reference without adding any unsupported data.
    b += [line(370, 625, 1016, 625, CHARCOAL, 3)]
    for x in (370, 532, 694, 856, 1016):
        b += [line(x, 625, x, 990, CHARCOAL, 2)]

    b += [text(132, 734, "95% / STEP", 34, CORAL, family="Consolas, monospace", weight=700)]
    b += [rect(370, 674, 646, 86, CHARCOAL, stroke=CREAM, sw=3, r=14)]
    b += [rect(370, 674, 232, 86, CORAL, r=14)]
    b += [text(1042, 740, "36%", 86, EVIDENCE_INK, anchor="end")]
    b += [text(132, 904, "99% / STEP", 34, TEAL, family="Consolas, monospace", weight=700)]
    b += [rect(370, 844, 646, 86, CHARCOAL, stroke=CREAM, sw=3, r=14)]
    b += [rect(370, 844, 530, 86, TEAL, r=14)]
    b += [text(1042, 910, "82%", 86, EVIDENCE_INK, anchor="end")]

    b += [text(600, 1104, "p²⁰  =  clean completion", 45, CHARCOAL, anchor="middle", family="Consolas, monospace", weight=700)]
    b += [text(600, 1162, "No retries or recovery included.", 28, CHARCOAL, anchor="middle", family="Arial, sans-serif", weight=700, spacing=1)]
    return svg_document(SQUARE, SQUARE, CREAM, b)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [Path(path), Path("C:/Windows/Fonts/arialbd.ttf"), Path("C:/Windows/Fonts/arial.ttf")]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def rasterize(svg: str, out: Path) -> None:
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(out), output_width=W, output_height=H)


def contact_sheet(out_dir: Path) -> None:
    a = Image.open(out_dir / "candidate-a-charcoal.png").convert("RGB")
    b = Image.open(out_dir / "candidate-b-cream.png").convert("RGB")
    full_w, full_h = 520, round(H * 520 / W)
    phone_w, phone_h = PHONE_W, PHONE_H
    label_font = font("C:/Windows/Fonts/arialbd.ttf", 28)
    small_font = font("C:/Windows/Fonts/arialbd.ttf", 22)
    pad = 40
    title_h = 54
    gap = 26
    width = pad * 3 + full_w * 2
    height = pad + title_h + full_h + gap + 60 + phone_h + pad
    sheet = Image.new("RGB", (width, height), CREAM)
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 18), "AI USEFULNESS THUMBNAIL CONTACT SHEET", fill=CHARCOAL, font=label_font)
    top = pad + title_h
    for idx, (im, name) in enumerate(((a, "A · CHARCOAL / 36 → 82"), (b, "B · CREAM / 20 STEPS"))):
        x = pad + idx * (full_w + pad)
        preview = im.resize((full_w, full_h), Image.Resampling.LANCZOS)
        sheet.paste(preview, (x, top))
        draw.text((x, top + full_h + 8), name, fill=CHARCOAL, font=small_font)
        phone = im.resize((phone_w, phone_h), Image.Resampling.LANCZOS)
        phone_x = x + (full_w - phone_w) // 2
        phone_y = top + full_h + 42
        sheet.paste(phone, (phone_x, phone_y))
        draw.rectangle((phone_x - 2, phone_y - 2, phone_x + phone_w + 1, phone_y + phone_h + 1), outline=CHARCOAL, width=2)
        draw.text((phone_x, phone_y + phone_h + 8), "168 px phone check", fill=CHARCOAL, font=small_font)
    sheet.save(out_dir / "contact-sheet.png", format="PNG", optimize=False)
    a.resize((phone_w, phone_h), Image.Resampling.LANCZOS).save(out_dir / "candidate-a-charcoal-phone-168.png", format="PNG", optimize=False)
    b.resize((phone_w, phone_h), Image.Resampling.LANCZOS).save(out_dir / "candidate-b-cream-phone-168.png", format="PNG", optimize=False)


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    assets = {
        "candidate-a-charcoal": candidate_a(),
        "candidate-b-cream": candidate_b(),
    }
    for stem, svg in assets.items():
        (out_dir / f"{stem}.svg").write_text(svg, encoding="utf-8", newline="\n")
        rasterize(svg, out_dir / f"{stem}.png")
    square_svg = square_chart()
    (out_dir / "square-reliability-chart.svg").write_text(square_svg, encoding="utf-8", newline="\n")
    cairosvg.svg2png(bytestring=square_svg.encode("utf-8"), write_to=str(out_dir / "square-reliability-chart.png"), output_width=SQUARE, output_height=SQUARE)
    contact_sheet(out_dir)
    print(f"Rendered {len(assets)} candidates at {W}x{H}; phone previews at {PHONE_W}x{PHONE_H}")
    print(f"Square companion: {out_dir / 'square-reliability-chart.png'} ({SQUARE}x{SQUARE})")
    print(f"Contact sheet: {out_dir / 'contact-sheet.png'}")


if __name__ == "__main__":
    main()
