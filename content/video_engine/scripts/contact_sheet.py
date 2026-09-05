"""A contact sheet from a folder of generated stills - one labelled grid PNG for the operator's
review (quarantine rule: nothing leaves review until a sheet is approved).

    python contact_sheet.py <dir> [--out sheet.png] [--cols 3] [--width 360] [--glob "*.png"]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--width", type=int, default=360)
    ap.add_argument("--glob", default="*.png")
    args = ap.parse_args()
    files = sorted(p for p in args.dir.glob(args.glob) if not re.search(r"(_frame_|-raw|contact-sheet)", p.name))
    if not files:
        print("no stills"); return 1
    tiles = []
    for f in files:
        im = Image.open(f).convert("RGB")
        h = round(im.height * args.width / im.width)
        tiles.append((f.stem, im.resize((args.width, h), Image.LANCZOS)))
    th = max(t.height for _, t in tiles) + 26
    rows = (len(tiles) + args.cols - 1) // args.cols
    sheet = Image.new("RGB", (args.cols * (args.width + 12) + 12, rows * (th + 12) + 12), (244, 230, 199))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    for i, (name, t) in enumerate(tiles):
        x = 12 + (i % args.cols) * (args.width + 12); y = 12 + (i // args.cols) * (th + 12)
        sheet.paste(t, (x, y + 22)); d.text((x, y + 2), f"{i + 1}. {name[:44]}", fill=(37, 49, 60), font=font)
    out = args.out or (args.dir / "contact-sheet.png")
    sheet.save(out); print(f"{len(tiles)} stills -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
