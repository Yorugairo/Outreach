"""P58 T1's PROBE COMPOSITOR - one identical push over every route, so HG1 judges the layering and not the move.

    python probe_2_5d.py --build <build-p58-probe> [--frames] [--manifest]

This is NOT the engine. The camera over layers lands in T3 (`kinetics/camera.mjs`); until then the probe
composites four RGBA layers with PIL under doc 24's law so route (a) (prompted in four layers) and route
(b) (the depth split) are read under exactly the same camera.

THE PUSH IS FROZEN - one authored key list, identical for every route and every plate:

    PUSH = {"s": (1.00, 1.12), "look_drift_px": (40.0, 0.0), "ease": "cubic", "instants": (0.0, 0.5, 1.0)}

`at` is the frame centre and never moves; `look` starts at the frame centre and drifts 40 px RIGHT, so the
world slides LEFT under a 12 % push. The ease is the cubic in-out the engine uses.

THE LAW (doc 43 s43.2 as `kinetics/camera.mjs` states it, `screen = at + s * (p - look)`), with one depth
term per layer - the same form T3 will implement:

    s_k    = 1 + (s - 1) * k          (doc 24 :166-171 parallax factors: far 1.00 / board 1.05 / mid 1.15 / near 1.40)
    look_k = at + (look - at) * k
    screen = at + s_k * (p - look_k)

so the per-layer translate is `at - s_k * look_k` and a nearer layer both grows faster and slides further -
parallax as a consequence of the camera, never as a mechanism (E49, E59).

Reads every `<build>/<route-dir>/<plate>/` that holds four RGBA layers. Route (b) writes
`<stem>-far/-mid/-subject/-near.png`; route (a) may name them `background/mid/subject/occluder` and is
mapped onto the same four roles. Writes `<build>/frames/<route>-<plate>-u{000,050,100}.png`, a labelled
`contact-sheet.png` and `probe-geometry.json` (per frame, per layer: k, translate, scale, the rect after
the transform), plus the per-route cost table read from each split json / lane A's manifest.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

# THE frozen push. Every route and every plate is judged under this and nothing else.
PUSH = {
    "s": (1.00, 1.12),
    "look_drift_px": (40.0, 0.0),
    "ease": "cubic",
    "instants": (0.0, 0.5, 1.0),
    "law": "screen = at + s_k * (p - look_k); s_k = 1 + (s-1)*k; look_k = at + (look-at)*k",
}
# doc 24 :166-171 - the four planes back to front and their parallax factors.
ROLE_K = {"far": 1.00, "board": 1.05, "mid": 1.15, "subject": 1.15, "near": 1.40}
ROLES = ("far", "mid", "subject", "near")
# route (a) (GPT Image 2.5 / Flow) names its four assets by content; doc 24 names them by plane.
ALIASES = {"far": "far", "background": "far", "backdrop": "far", "bg": "far",
           "mid": "mid", "midground": "mid", "board": "mid",
           "subject": "subject", "actor": "subject", "hero": "subject",
           "occluder": "near", "near": "near", "foreground": "near", "fg": "near"}
ROUTE_OF_DIR = {"split": "b-split", "split-sam": "b-sam", "prompted": "a-prompted"}


def ease_cubic(u: float) -> float:
    """The cubic in-out: 4u^3 below the half, its mirror above."""
    u = min(1.0, max(0.0, float(u)))
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def camera_at(u: float, size: tuple[int, int]) -> dict:
    """The camera state at u: the anchor, the look point and the scale."""
    w, h = size
    at = (w / 2.0, h / 2.0)
    e = ease_cubic(u)
    s0, s1 = PUSH["s"]
    dx, dy = PUSH["look_drift_px"]
    return {"at": at, "look": (at[0] + dx * e, at[1] + dy * e), "s": s0 + (s1 - s0) * e, "e": round(e, 6)}


def layer_transform(cam: dict, k: float) -> dict:
    """The per-layer similarity: scale, translate, and the rect the full-frame layer lands on."""
    at, look, s = cam["at"], cam["look"], cam["s"]
    s_k = 1.0 + (s - 1.0) * k
    look_k = (at[0] + (look[0] - at[0]) * k, at[1] + (look[1] - at[1]) * k)
    tx, ty = at[0] - s_k * look_k[0], at[1] - s_k * look_k[1]
    return {"k": k, "scale": round(s_k, 6), "look_k": [round(look_k[0], 3), round(look_k[1], 3)],
            "translate": [round(tx, 3), round(ty, 3)]}


def rect_of(tr: dict, size: tuple[int, int]) -> list[float]:
    """[x0, y0, x1, y1] of a `size` layer after the transform - what the camera actually shows of it."""
    w, h = size
    s, (tx, ty) = tr["scale"], tr["translate"]
    return [round(tx, 3), round(ty, 3), round(tx + s * w, 3), round(ty + s * h, 3)]


def warp(layer: Image.Image, tr: dict, canvas: tuple[int, int]) -> Image.Image:
    """PIL wants the INVERSE map: out(x,y) <- in(a x + b y + c, d x + e y + f)."""
    s, (tx, ty) = tr["scale"], tr["translate"]
    inv = (1.0 / s, 0.0, -tx / s, 0.0, 1.0 / s, -ty / s)
    return layer.convert("RGBA").transform(canvas, Image.AFFINE, inv, resample=Image.BICUBIC)


# ---------------------------------------------------------------- reading a route


def find_layers(folder: Path) -> dict[str, Path]:
    """The four planes in `folder`, back to front, whichever of the two naming conventions was used."""
    found: dict[str, Path] = {}
    for png in sorted(folder.glob("*.png")):
        suffix = png.stem.rsplit("-", 1)[-1].lower()
        role = ALIASES.get(suffix)
        if role and role not in found:
            found[role] = png
    return {r: found[r] for r in ROLES if r in found}


def cost_row(folder: Path, route: str, plate: str) -> dict:
    """The cost table fields, read from route (b)'s split json or route (a)'s manifest."""
    row = {"route": route, "plate": plate, "generator": "?", "wall_clock_s": None, "peak_vram_mb": None,
           "inpainter": None, "re_roll": None, "notes": []}
    for js in sorted(folder.glob("*.split.json")):
        m = json.loads(js.read_text(encoding="utf-8"))
        row.update({"generator": m.get("model"), "wall_clock_s": m.get("timings_s", {}).get("wall_clock"),
                    "inpainter": m.get("inpainter"), "notes": m.get("notes", []),
                    "re_roll": "one server call per layer; a re-roll is the whole split (~{}s)".format(
                        m.get("timings_s", {}).get("wall_clock"))})
        peak = m.get("vram_free_bytes", {}).get("peak_used", -1)
        row["peak_vram_mb"] = round(peak / 1e6, 1) if peak and peak > 0 else None
        row["edges"] = m.get("edges")
        break
    for js in sorted(folder.glob("*manifest.json")):
        m = json.loads(js.read_text(encoding="utf-8"))
        row.update({k: m[k] for k in ("generator", "wall_clock_s", "re_roll", "notes") if k in m})
        break
    return row


def routes(build: Path) -> list[tuple[str, str, Path]]:
    """(route, plate, folder) for every folder under the build that holds four planes."""
    out = []
    for route_dir in sorted(p for p in build.iterdir() if p.is_dir() and p.name in ROUTE_OF_DIR):
        for plate_dir in sorted(p for p in route_dir.iterdir() if p.is_dir()):
            if len(find_layers(plate_dir)) == 4:
                out.append((ROUTE_OF_DIR[route_dir.name], plate_dir.name, plate_dir))
    return out


# ---------------------------------------------------------------- the frames


def render(folder: Path, u: float) -> tuple[Image.Image, list[dict]]:
    layers = find_layers(folder)
    base = Image.open(layers["far"]).convert("RGBA")
    canvas_size = base.size
    cam = camera_at(u, canvas_size)
    frame = Image.new("RGBA", canvas_size, (0, 0, 0, 255))
    geo = []
    for role in ROLES:
        im = Image.open(layers[role]).convert("RGBA")
        tr = layer_transform(cam, ROLE_K[role])
        frame.alpha_composite(warp(im, tr, canvas_size))
        geo.append({"layer": role, "source": layers[role].name, "size": list(im.size),
                    "rect": rect_of(tr, im.size), **tr})
    return frame, geo


def contact_sheet(frames: dict[tuple[str, str], list[Path]], out: Path, cell_w: int = 512) -> Path:
    keys = sorted(frames)
    first = Image.open(frames[keys[0]][0])
    cell_h = int(cell_w * first.height / first.width)
    pad, head = 6, 26
    sheet = Image.new("RGB", (3 * cell_w + 4 * pad, len(keys) * (cell_h + head + pad) + pad), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    for r, key in enumerate(keys):
        y = pad + r * (cell_h + head + pad)
        d.text((pad + 2, y + 6), f"{key[1]}  |  route {key[0]}", fill=(240, 236, 226))
        for c, png in enumerate(frames[key]):
            im = Image.open(png).convert("RGB").resize((cell_w, cell_h), Image.LANCZOS)
            x = pad + c * (cell_w + pad)
            sheet.paste(im, (x, y + head))
            d.text((x + 6, y + head + 6), f"u = {PUSH['instants'][c]:.2f}", fill=(255, 220, 120))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def build_frames(build: Path) -> dict:
    found = routes(build)
    if not found:
        raise SystemExit(f"no four-layer folder under {build} (looked in {'/'.join(ROUTE_OF_DIR)})")
    frames_dir = build / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    geometry: dict = {"push": PUSH, "role_parallax": ROLE_K, "frames": [], "cost_table": []}
    sheet_rows: dict[tuple[str, str], list[Path]] = {}
    for route, plate, folder in found:
        geometry["cost_table"].append(cost_row(folder, route, plate))
        sheet_rows[(route, plate)] = []
        for u in PUSH["instants"]:
            frame, geo = render(folder, u)
            name = f"{route}-{plate}-u{int(round(u * 100)):03d}.png"
            frame.convert("RGB").save(frames_dir / name)
            sheet_rows[(route, plate)].append(frames_dir / name)
            geometry["frames"].append({"file": name, "route": route, "plate": plate, "u": u,
                                       "camera": camera_at(u, frame.size), "layers": geo})
    sheet = contact_sheet(sheet_rows, build / "frames" / "contact-sheet.png")
    geometry["contact_sheet"] = sheet.name
    (build / "probe-geometry.json").write_text(json.dumps(geometry, indent=2), encoding="utf-8")
    return geometry


def print_manifest(build: Path) -> None:
    geo = json.loads((build / "probe-geometry.json").read_text(encoding="utf-8"))
    print(f"PUSH  {json.dumps(geo['push'])}")
    print(f"\n{'route':<12}{'plate':<34}{'wall s':>8}{'VRAM MB':>9}  inpainter / generator")
    for row in geo["cost_table"]:
        print(f"{row['route']:<12}{row['plate']:<34}{str(row['wall_clock_s'] or '-'):>8}"
              f"{str(row['peak_vram_mb'] or '-'):>9}  {row.get('inpainter') or '-'} / {row.get('generator') or '-'}")
        for n in row.get("notes") or []:
            print(f"{'':<12}note: {n}")
    print(f"\n{'frame':<46}{'layer':<9}{'k':>6}{'scale':>9}{'translate':>22}{'rect x0..x1':>24}")
    for fr in geo["frames"]:
        for lay in fr["layers"]:
            print(f"{fr['file']:<44}{lay['layer']:<9}{lay['k']:>6.2f}{lay['scale']:>9.4f}"
                  f"{str(lay['translate']):>22}{str([lay['rect'][0], lay['rect'][2]]):>24}")
    print(f"\n{len(geo['frames'])} frames + {geo['contact_sheet']} under {build / 'frames'}")


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--frames", action="store_true", help="composite the three instants for every route x plate")
    ap.add_argument("--manifest", action="store_true", help="print the cost table and the per-layer geometry")
    a = ap.parse_args()
    if a.frames:
        geo = build_frames(a.build)
        print(f"wrote {len(geo['frames'])} frames + {geo['contact_sheet']} + probe-geometry.json under {a.build}")
    if a.manifest:
        print_manifest(a.build)
    if not (a.frames or a.manifest):
        ap.error("nothing to do: pass --frames and/or --manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
