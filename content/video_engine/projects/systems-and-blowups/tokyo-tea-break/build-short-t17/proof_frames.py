"""P52 T17 - the PAIRED frames the operator judges gate 5 on. Renders nothing but this private build.

Six instants across the race, each shot from BOTH arms at the same t off the same data: two of them
are period JOINS (where the clock stops the marks dead and where the path's knots are) and four are
mid-period. `race-A-<t>.png` / `race-B-<t>.png` are the frames themselves; `race-strip.png` stacks
them A over B, instant by instant, so the two arms can be read side by side without a viewer.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO / "content/video_engine/scripts"))

import render_baseline as RB   # noqa: E402

# 5.7 / 6.9 are period joins (4.5 + 1.2 i); the rest are mid-period, where the marks are at speed
INSTANTS = (5.7, 6.3, 6.9, 7.5, 8.7, 9.9)
JOINS = (5.7, 6.9)
PROOF = HERE / "proof"


def render_pairs() -> dict:
    PROOF.mkdir(parents=True, exist_ok=True)
    out = {}
    for arm, letter in (("arm-a", "A"), ("arm-b", "B")):
        for t in INSTANTS:
            png = RB.render_frame(HERE / arm / "player.html", t, "16:9")
            path = PROOF / f"race-{letter}-{t:g}.png"
            path.write_bytes(png)
            out[(letter, t)] = path
            print(f"{letter} {t:g}s -> {path.name}")
    return out


def strip(paths: dict) -> Path:
    from PIL import Image, ImageDraw
    scale, pad, head = 0.30, 10, 34
    w, h = int(1920 * scale), int(1080 * scale)
    sheet = Image.new("RGB", (pad + len(INSTANTS) * (w + pad), head + 2 * (h + pad) + pad), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 8), "P52 T17 - the race A/B.  TOP: arm A, the engine as is.  "
                        "BOTTOM: arm B, the race path fitted by clothoidFit.  "
                        "Same data, same clock, same instants.  * = a period join.",
              fill=(235, 235, 235))
    for i, t in enumerate(INSTANTS):
        x = pad + i * (w + pad)
        for row, letter in ((0, "A"), (1, "B")):
            im = Image.open(paths[(letter, t)]).convert("RGB").resize((w, h), Image.LANCZOS)
            sheet.paste(im, (x, head + row * (h + pad)))
        draw.text((x + 4, head - 14), f"{letter and ''}{t:g}s{' *' if t in JOINS else ''}",
                  fill=(245, 200, 90) if t in JOINS else (200, 200, 200))
    path = PROOF / "race-strip.png"
    sheet.save(path)
    print(path)
    return path


if __name__ == "__main__":
    strip(render_pairs())
