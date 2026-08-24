"""Trace-cut both hand poses off their black ground and calibrate each nib.

Edge flood-fill rather than a luminance key: the heather sleeve is dark and a
threshold key eats it. Full image height is kept so the forearm still runs off
the frame edge — cropping to the alpha bbox ends the arm mid-canvas, which the
skill names as the number-one amateur tell.
"""
import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter

SRC = Path(__file__).parent.parent / "hand-delivery"
DST = Path(__file__).parent / "assets"
BG_MAX = 30      # channel ceiling that still counts as the black ground
DOWNSCALE = 3

out_nibs = {}
for pose, name in (("a", "hand-pose-a.png"), ("b", "hand-pose-b.png")):
    im = Image.open(SRC / name).convert("RGB")
    w, h = im.size
    small = im.resize((w // DOWNSCALE, h // DOWNSCALE), Image.BILINEAR)
    sw, sh = small.size
    px = small.load()

    def is_bg(x, y):
        r, g, b = px[x, y]
        return r < BG_MAX and g < BG_MAX and b < BG_MAX

    bg = bytearray(sw * sh)
    q = deque()
    for x in range(sw):
        for y in (0, sh - 1):
            if is_bg(x, y) and not bg[y * sw + x]:
                bg[y * sw + x] = 1
                q.append((x, y))
    for y in range(sh):
        for x in (0, sw - 1):
            if is_bg(x, y) and not bg[y * sw + x]:
                bg[y * sw + x] = 1
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < sw and 0 <= ny < sh and not bg[ny * sw + nx] and is_bg(nx, ny):
                bg[ny * sw + nx] = 1
                q.append((nx, ny))

    mask = (Image.frombytes("L", (sw, sh), bytes(255 - v * 255 for v in bg))
            .resize((w, h), Image.BILINEAR)
            .filter(ImageFilter.GaussianBlur(1.1)))
    cut = im.convert("RGBA")
    cut.putalpha(mask)

    # trim horizontal slack only; keep full height so the sleeve exits the frame
    bb = mask.point(lambda p: 255 if p > 10 else 0).getbbox()
    cut = cut.crop((bb[0], 0, bb[2], h))

    # nib = lowest opaque run (the marker tip)
    a = cut.load()
    W, H = cut.size
    nib = None
    for y in range(H - 1, -1, -1):
        row = [x for x in range(W) if a[x, y][3] > 140]
        if row:
            nib = (sum(row) // len(row), y)
            break
    out_nibs[pose] = {"x": round(nib[0] / W, 4), "y": round(nib[1] / H, 4),
                      "w": W, "h": H, "aspect": round(W / H, 4)}
    cut.save(DST / f"draw-hand-{pose}.png")
    op = cut.getchannel("A").histogram()
    tot = W * H
    print(f"pose {pose}: {W}x{H}  nib=({nib[0]},{nib[1]}) "
          f"frac=({nib[0]/W:.3f},{nib[1]/H:.3f})  "
          f"opaque {op[255]/tot:.0%} transparent {op[0]/tot:.0%}  "
          f"{(DST / f'draw-hand-{pose}.png').stat().st_size//1024}KB")

(Path(__file__).parent / "nibs.json").write_text(json.dumps(out_nibs, indent=1), encoding="utf-8")
print("nib calibration:", json.dumps(out_nibs))
