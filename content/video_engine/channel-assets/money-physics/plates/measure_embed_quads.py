"""MEASURE A PLATE'S ART-EMBED SURFACES ON THE RENDERED STAGE (P50 T7).

    python measure_embed_quads.py stills/art-embed-study-poster.png
    python measure_embed_quads.py stills/art-embed-study-tv-laptop.png --surfaces tv laptop
    python measure_embed_quads.py stills/art-embed-washi-tv.png --no-write

A generated plate has no addressable coordinate space (E33): a diffusion model decided where the wall is. The
ART-embed grammar answers that by MEASURING one flat surface in the painting and declaring its four corners on
`<plate>.layers.json`, which `build_scene_timeline_f.plate_embeds` reads and `embed_quad_error` polices. This is
the tool that does the measuring, committed beside the plates so a RE-ROLL is measured the same way rather than
by eye - the numbers in a layers file are a measurement with a stated method and a stated residual, not a guess.

WHAT IT MEASURES, AND IN WHOSE COORDINATES. The quad is STAGE fractions: the engine reads it as
`quad.map(p => [p[0] * STAGE_W, p[1] * STAGE_H])` (scene-evidence-engine.mjs, embedQuadPx). The stage is NOT the
still. The player paints the world plate on `.world`, which is `inset: -5%` - 110 % of the stage, centred - with
`background-size: cover`. So a 768 x 1376 still (0.55814) on a 9:16 stage (0.5625) is scaled 1.546875x to fill
the 110 % box by WIDTH and overflows in height, and every still pixel lands at

    stage_x = (x * s + ox) / STAGE_W      s  = 1.546875
    stage_y = (y * s + oy) / STAGE_H      ox = -54.0, oy = -104.25   (9:16, 768 x 1376)

which is a 5 % crop on each side plus ~0.4 % more in y. `cover_placement` computes it exactly for any still and
either aspect, so the corners this tool prints are the stage fractions the engine will use - measure on the RAW
still and the card lands inset 5 % from the surface it was supposed to sit on.

THE FIT. The golden's poster (tests/golden/build_golden_sources.py) was read by a luminance threshold inside a
window, the largest connected component, per-edge least squares over the middle 80 % and corners at the
intersections. Everything here is that, with ONE part replaced, for a reason the TV states plainly: the lamp's
cone falls across the TV's screen as a hard diagonal wedge (art-embed-study-tv-laptop.png, row 600: the screen
reads 175 at x=198 under the wedge and 10 at x=420 past it, while the wall outside reads 225), so no single
threshold puts the whole screen in one connected component - a dark threshold keeps the unlit triangle and a
bright one keeps the lit one, and either way the fit follows the WEDGE instead of the bezel. So the edge
LOCATOR is local: along each scanline, inside a band, the edge is a luminance STEP of at least EDGE_STEP, and
two passes pick the right one:

  pass 1  the OUTERMOST step in an asymmetric band around the declared window (BAND_OUT px outside it,
          BAND_IN px in): coming from the wall, the first thing that happens is the frame's or the bezel's
          OUTER line. It is parallel to the inner edge, so this pass recovers the SLANT - which the window,
          a bounding box, cannot carry (the study poster's top edge falls 49 px across its own width).
  pass 2/3  the INNERMOST step in a band around that line, twice, tightening: crossing the frame face, the
          last step before the interior goes quiet is the edge the card must sit inside. That reads the
          bezel's inner edge whatever the bezel is made of - a dark line on the study TV's left, a bright
          highlight on its right, a lit frame face on the washi TV - and never the wedge, whose own step lies
          outside so tight a band.

A hard-trimmed least squares after each pass, so one bad scanline cannot tilt an edge, and the RMS residual of
each edge is reported: under RESIDUAL_LIMIT the four lines ARE the surface, over it they are an opinion.

CROSS-CHECK. Run on art-embed-study-poster.png this reads the poster's sides at x = 282.5 / 639.2 and its top
and bottom at y = 266.4 / 213.5 and 840.4 / 860.4 still px - the same corners the golden's own earlier fit read
off this still (build_golden_sources.py, ART_POSTER: 283 / 638, 267.1 / 214.7, 840.1 / 859.6), every one inside
1.2 px. Two methods, one poster. The golden's quad stays as it is: it is a committed test fixture in RAW still
fractions, and what this tool writes is the same surface in the STAGE fractions a build needs.

The WINDOW per surface, in still fractions, is the only hand-read number here: the approximate bounding box
that says WHICH surface (and excludes the lamp). Everything reported is measured from it.

A surface with no straight edges to fit - the washi's paper ground - is measured by its own stated rule instead
(`deckle`); the rule is in the table beside it.

Deterministic: pure arithmetic on the committed PNG, no sampling and no randomness. Two runs, one output.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STILLS = HERE / "stills"
STAGE = {"16:9": (1920, 1080), "9:16": (1080, 1920)}
WORLD_OVERHANG = 0.05      # .world is inset:-5% - the plate is painted over 110 % of the stage and cropped to it
EDGE_STEP = 12.0           # the luminance step (0..255) that counts as an edge rather than paint
EDGE_SPAN = 5              # px averaged either side of a step: enough that the plates' grain is not an edge
# each pass: (take the innermost step?, px searched outside the previous line, px searched inside it). Pass 1
# starts from the declared window and reaches far enough IN to carry the slant a bounding box cannot; passes 2
# and 3 walk the line onto the inner edge and then settle on it.
PASSES = ((False, 12, 60), (True, 30, 30), (True, 10, 10))
MIDDLE = 0.80              # the share of each edge that is fitted: the middle 80 %, corners excluded
TRIM = (8.0, 4.0, 2.0, 1.2)   # px: the line is refitted after dropping everything outside each of these in turn
RESIDUAL_LIMIT = 1.0       # still px, on an edge's RMS residual: the fit is a measurement only while it is this
                           # tight. The max residual is reported beside it and runs to about 1.4 px on the two
                           # TVs, where a 2 px bezel line is the edge and a scanline can read either side of it.

# ---- the surfaces, by plate. The window is the hand-read approximate rectangle in STILL fractions ----------
SURFACES = {
    "art-embed-study-poster": {
        "poster": {"kind": "edges", "window": (0.368, 0.156, 0.831, 0.625),
                   "note": "the bright poster face inside its thin dark frame; the lamp and the desk are outside the window"},
    },
    "art-embed-study-tv-laptop": {
        "tv": {"kind": "edges", "window": (0.256, 0.237, 0.925, 0.502),
               "note": "the dark screen inside the thin bezel; the lamp's wedge crosses it and is never the edge"},
        "laptop": {"kind": "edges", "window": (0.594, 0.631, 0.912, 0.749),
                   "note": "the bright blank screen inside the dark lid, tilted back on the desk"},
    },
    "art-embed-washi-tv": {
        "tv": {"kind": "edges", "window": (0.150, 0.176, 0.849, 0.401),
               "note": "the dark screen inside the thin bezel, square-on; the lamp's cone crosses its lower left"},
        "paper": {"kind": "deckle", "bright": 180.0, "run": 24, "margin": 2, "search": (0.40, 0.60),
                  "note": "the washi ground: full stage width, from just under the deckle's LOWEST tear to the "
                          "frame's bottom edge - below that y every column is paper, so a record lies flat on it"},
    },
}
SIDES = ("left", "right", "top", "bottom")


# ---- the still ---------------------------------------------------------------------------------------------

def load_luma(path: Path) -> tuple[int, int, list[int]]:
    """The still as ITU-R 601-2 luminance (PIL's own `convert("L")`), width, height, row-major."""
    from PIL import Image
    with Image.open(path) as im:
        g = im.convert("L")
        return g.width, g.height, bytearray(g.tobytes())


def cover_placement(iw: int, ih: int, aspect: str = "9:16", overhang: float = WORLD_OVERHANG) -> dict:
    """Where every still pixel lands on the stage: `stage_px = still_px * scale + offset`. The player's
    `.world` is inset by `overhang` on every side and takes the plate as `background-size: cover`, so the
    plate is scaled to cover that larger box and centred in it."""
    sw, sh = STAGE[aspect]
    bw, bh = sw * (1 + 2 * overhang), sh * (1 + 2 * overhang)
    scale = max(bw / iw, bh / ih)
    return {"aspect": aspect, "stage": (sw, sh), "scale": scale,
            "ox": (bw - iw * scale) / 2 - overhang * sw,
            "oy": (bh - ih * scale) / 2 - overhang * sh}


def to_stage(pt: tuple[float, float], place: dict) -> list[float]:
    sw, sh = place["stage"]
    return [(pt[0] * place["scale"] + place["ox"]) / sw, (pt[1] * place["scale"] + place["oy"]) / sh]


# ---- the edge locator --------------------------------------------------------------------------------------

def _luma_at(L, w: int, h: int, x: int, y: int) -> int:
    return L[y * w + x]


def _profile(L, w: int, h: int, side: str, s: int, p0: int, p1: int) -> list[int]:
    """The luminance along one scanline, p0..p1 inclusive."""
    if side in ("left", "right"):
        row = s * w
        return [L[row + x] for x in range(p0, p1 + 1)]
    return [L[y * w + s] for y in range(p0, p1 + 1)]


def _edge_on_scanline(L, w: int, h: int, side: str, s: int, p0: int, p1: int, innermost: bool) -> float | None:
    """A STEP EDGE along one scanline inside [p0, p1] - the INNERMOST one (the last thing before the interior
    goes quiet) or the OUTERMOST (the first thing coming in off the wall). `side` says which way "inward"
    points: into the surface from outside it.

    The detector is a matched filter for a step, not a single-pixel difference: S(k) = the mean of the
    EDGE_SPAN pixels after k minus the mean of the EDGE_SPAN pixels up to k. These plates are painted with
    visible grain - a dark TV screen swings 3..23 pixel to pixel - and a one-pixel difference of EDGE_STEP
    fires on that grain deep inside the surface, which is what makes a naive fit follow the paint. A mean over
    EDGE_SPAN averages grain away and survives a real edge. The edge is then the PEAK of |S| across the
    contiguous run of same-signed, over-threshold k around the first one found, so a thin frame line beside
    the edge (a different sign) cannot capture the pick."""
    limit = (h - 1) if side in ("top", "bottom") else (w - 1)
    p0, p1 = max(EDGE_SPAN, p0), min(limit - EDGE_SPAN, p1)
    if p1 - p0 < 3:
        return None
    prof = _profile(L, w, h, side, s, p0 - EDGE_SPAN, p1 + EDGE_SPAN)
    base = p0 - EDGE_SPAN
    step = {}
    for k in range(p0, p1):
        i = k - base
        step[k] = (sum(prof[i + 1:i + 1 + EDGE_SPAN]) - sum(prof[i + 1 - EDGE_SPAN:i + 1])) / EDGE_SPAN
    inward_up = side in ("left", "top")     # inward is the increasing coordinate
    ks = list(range(p1 - 1, p0 - 1, -1)) if (inward_up == innermost) else list(range(p0, p1))
    first = next((i for i, k in enumerate(ks) if abs(step[k]) >= EDGE_STEP), None)
    if first is None:
        return None
    sign = 1 if step[ks[first]] > 0 else -1
    last = first
    while last + 1 < len(ks) and abs(step[ks[last + 1]]) >= EDGE_STEP \
            and (1 if step[ks[last + 1]] > 0 else -1) == sign:
        last += 1
    return max(ks[first:last + 1], key=lambda k: abs(step[k])) + 0.5


def _lsq(pts: list[tuple[float, float]]) -> tuple[float, float]:
    n = len(pts)
    ms = sum(p[0] for p in pts) / n
    mp = sum(p[1] for p in pts) / n
    den = sum((p[0] - ms) ** 2 for p in pts)
    a = (sum((p[0] - ms) * (p[1] - mp) for p in pts) / den) if den > 1e-9 else 0.0
    return a, mp - a * ms


def _fit(points: list[tuple[float, float]]) -> tuple[float, float, float, float, int]:
    """Least squares `pos = a * s + b` over (s, pos), trimmed hard: the line is refitted after dropping every
    scanline outside each TRIM threshold in turn. A painted edge is straight to about a pixel, so a scanline
    two pixels off is not a noisy reading of the edge - it is a reading of something else (the lamp's wedge
    crossing a corner, a cable, a shadow) and it is dropped rather than allowed to tilt the line. The floor on
    how many may go keeps a genuinely curved or wrongly-windowed edge from being trimmed into a straight one.
    Returns a, b, rms, max |residual|, the number of scanlines the line was finally fitted to."""
    pts = list(points)
    floor = max(8, int(0.25 * len(points)))
    a, b = _lsq(pts)
    for thr in TRIM:
        keep = [p for p in pts if abs(p[1] - (a * p[0] + b)) <= thr]
        if len(keep) < floor:
            break
        pts = keep
        a, b = _lsq(pts)
    res = [abs(p[1] - (a * p[0] + b)) for p in pts]
    n = len(pts)
    return a, b, (sum(r * r for r in res) / n) ** 0.5 if n else float("inf"), max(res) if res else float("inf"), n


def _scanlines(lo: float, hi: float) -> range:
    """The middle MIDDLE of an edge: the corners are rounded in every painting, so they are never fitted."""
    pad = (hi - lo) * (1 - MIDDLE) / 2
    return range(int(round(lo + pad)), int(round(hi - pad)) + 1)


def fit_surface(L, w: int, h: int, window: tuple[float, float, float, float]) -> dict:
    """The four edges of the surface inside `window` (still fractions), each as a line in STILL pixels, and
    the four corners at their intersections. Two passes: the declared window, then the first fit."""
    box = {"left": window[0] * w, "top": window[1] * h, "right": window[2] * w, "bottom": window[3] * h}
    lines: dict[str, tuple] = {}
    for innermost, out, inn in PASSES:
        nxt = {}
        for side in SIDES:
            vertical = side in ("left", "right")
            inward_up = side in ("left", "top")
            lo, hi = (box["top"], box["bottom"]) if vertical else (box["left"], box["right"])
            pts = []
            for s in _scanlines(lo, hi):
                if not (0 <= s < (h if vertical else w)):
                    continue
                centre = (lines[side][0] * s + lines[side][1]) if lines else box[side]
                a, b = (centre - out, centre + inn) if inward_up else (centre - inn, centre + out)
                p = _edge_on_scanline(L, w, h, side, s, int(a), int(b) + 1, innermost)
                if p is not None:
                    pts.append((float(s), p))
            if len(pts) < 8:
                raise SystemExit(f"measure: the {side} edge gave only {len(pts)} scanlines inside its band - "
                                 "widen or move the surface's window")
            nxt[side] = _fit(pts)
        lines = nxt
    xs = {k: (lines[k][0], lines[k][1]) for k in ("left", "right")}      # x = a y + b
    ys = {k: (lines[k][0], lines[k][1]) for k in ("top", "bottom")}      # y = a x + b
    corners = {}
    for name, (vx, hy) in (("tl", ("left", "top")), ("tr", ("right", "top")),
                           ("br", ("right", "bottom")), ("bl", ("left", "bottom"))):
        a, b = xs[vx]
        c, d = ys[hy]
        den = 1 - a * c
        if abs(den) < 1e-9:
            raise SystemExit(f"measure: the {vx} and {hy} edges do not meet - the window is not on a surface")
        x = (a * d + b) / den
        corners[name] = (x, c * x + d)
    return {"lines": lines, "corners": [corners["tl"], corners["tr"], corners["br"], corners["bl"]]}


# ---- the washi ground: its own stated rule -------------------------------------------------------------------

def fit_deckle(L, w: int, h: int, spec: dict) -> dict:
    """The paper's top edge: per column the first y from which `run` pixels are all brighter than `bright`,
    then the LOWEST of those over every column (the deepest tear) plus `margin`. At that y and below, every
    column of the still is paper - which is the whole claim the surface makes."""
    y0, y1 = int(spec["search"][0] * h), int(spec["search"][1] * h)
    tops = []
    for x in range(w):
        top = None
        for y in range(y0, y1 - spec["run"]):
            if all(_luma_at(L, w, h, x, y + k) > spec["bright"] for k in range(spec["run"])):
                top = y
                break
        if top is None:
            raise SystemExit(f"measure: column {x} never turns to paper inside the search band - "
                             "the still is not a deckle plate")
        tops.append(top)
    return {"tops": tops, "lowest": max(tops), "highest": min(tops), "y": max(tops) + spec["margin"]}


# ---- the report and the file ----------------------------------------------------------------------------------

def measure(still: Path, names: list[str], aspect: str = "9:16") -> dict:
    stem = still.stem
    table = SURFACES.get(stem)
    if not table:
        raise SystemExit(f"measure: {stem} declares no surfaces - add it to SURFACES with a window per surface")
    w, h, L = load_luma(still)
    place = cover_placement(w, h, aspect)
    out = {"still": still, "stem": stem, "size": (w, h), "place": place, "surfaces": {}}
    for name in names or sorted(table):
        spec = table.get(name)
        if not spec:
            raise SystemExit(f"measure: {stem} has no surface {name!r} - it declares {', '.join(sorted(table))}")
        if spec["kind"] == "edges":
            fit = fit_surface(L, w, h, spec["window"])
            quad = [to_stage(p, place) for p in fit["corners"]]
            rec = {"spec": spec, "fit": fit, "quad": quad,
                   "residual": {s: (fit["lines"][s][2], fit["lines"][s][3], fit["lines"][s][4]) for s in SIDES}}
        else:
            d = fit_deckle(L, w, h, spec)
            top = to_stage((0.0, float(d["y"])), place)[1]
            quad = [[0.0, max(0.0, top)], [1.0, max(0.0, top)], [1.0, 1.0], [0.0, 1.0]]
            rec = {"spec": spec, "deckle": d, "quad": quad, "residual": {}}
        rec["quad"] = [[round(x, 5), round(y, 5)] for x, y in rec["quad"]]
        out["surfaces"][name] = rec
    return out


def report(m: dict) -> None:
    w, h = m["size"]
    p = m["place"]
    print(f"{m['still'].name}  {w} x {h}  ->  stage {p['stage'][0]} x {p['stage'][1]} ({p['aspect']})")
    print(f"  cover on .world (inset -{WORLD_OVERHANG:.0%}): stage_px = still_px * {p['scale']:.6f} + "
          f"({p['ox']:.3f}, {p['oy']:.3f})")
    for name, rec in m["surfaces"].items():
        print(f"\n  [{name}] {rec['spec']['note']}")
        if rec["residual"]:
            for side in SIDES:
                rms, mx, n = rec["residual"][side]
                flag = "" if rms < RESIDUAL_LIMIT else f"   <-- rms OVER {RESIDUAL_LIMIT} px"
                print(f"    {side:<6} rms {rms:.3f} px   max {mx:.3f} px   over {n} scanlines{flag}")
            print("    corners (still px): " + "  ".join(f"({x:.1f}, {y:.1f})" for x, y in rec["fit"]["corners"]))
        else:
            d = rec["deckle"]
            print(f"    deckle: the tear runs y {d['highest']}..{d['lowest']} still px; the ground starts at "
                  f"y {d['y']} (the lowest tear + {rec['spec']['margin']} px)")
        q = rec["quad"]
        print("    quad (stage fractions, TL TR BR BL): " + json.dumps(q))
        width = ((q[1][0] - q[0][0]) + (q[2][0] - q[3][0])) / 2
        print(f"    width on the stage: {width:.1%}" + ("" if width >= 0.25 else "   <-- UNDER the 25 % floor"))


def _dumps(data: dict) -> str:
    """JSON indented 2, except that a quad stays on ONE line - four corners read as four corners, and a diff
    of a re-measured plate is four lines rather than thirty-two."""
    marks: dict[str, str] = {}

    def mark(o):
        if isinstance(o, list) and len(o) == 4 and all(isinstance(p, list) and len(p) == 2 for p in o):
            key = f"@@quad{len(marks)}@@"
            marks[key] = "[" + ", ".join("[" + ", ".join(json.dumps(v) for v in p) + "]" for p in o) + "]"
            return key
        if isinstance(o, list):
            return [mark(x) for x in o]
        if isinstance(o, dict):
            return {k: mark(v) for k, v in o.items()}
        return o

    text = json.dumps(mark(data), indent=2)
    for k, v in marks.items():
        text = text.replace(f'"{k}"', v)
    return text


def write_layers(m: dict, plates: Path) -> Path:
    """`<stem>.layers.json` beside the plate: the `embed` key rewritten from this measurement, every other key
    the file carries (a foreground layer, say) left exactly as it was."""
    path = plates / f"{m['stem']}.layers.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            raise SystemExit(f"measure: {path.name} is not JSON - move it aside rather than lose what it holds")
        if not isinstance(data, dict):
            raise SystemExit(f"measure: {path.name} is not an object")
    embed = dict(data.get("embed") or {})
    for name, rec in m["surfaces"].items():
        entry = {"quad": rec["quad"], "darken": None}
        keep = embed.get(name) or {}
        for k, v in keep.items():
            if k not in ("quad", "darken"):
                entry[k] = v
        embed[name] = entry
    data["embed"] = embed
    path.write_text(_dumps(data) + "\n", encoding="utf-8")
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("still", type=Path, help="the plate still, e.g. stills/art-embed-study-poster.png")
    ap.add_argument("--surfaces", nargs="*", default=None, help="which declared surfaces (default: all)")
    ap.add_argument("--aspect", default="9:16", choices=sorted(STAGE), help="the stage the plate is painted on")
    ap.add_argument("--no-write", action="store_true", help="measure and report, write nothing")
    a = ap.parse_args(argv)
    still = a.still if a.still.exists() else (STILLS / a.still.name)
    if not still.exists():
        raise SystemExit(f"measure: no still at {a.still}")
    m = measure(still, a.surfaces, a.aspect)
    report(m)
    if not a.no_write:
        print(f"\nwrote {write_layers(m, HERE)}")
    bad = [n for n, r in m["surfaces"].items() if r["residual"]
           and max(v[0] for v in r["residual"].values()) >= RESIDUAL_LIMIT]
    if bad:
        print(f"\nRMS RESIDUAL OVER {RESIDUAL_LIMIT} px on: {', '.join(bad)} - that is not a measurement yet")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
