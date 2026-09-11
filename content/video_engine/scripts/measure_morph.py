"""THE MORPH'S INVARIANTS - the measurement behind the motion gate's M17 row (P47 T3; the brief B4).

A page that enters by `morph` turns a prop outline into the area under its series by ARAP. Whether that reads as ONE
thing changing is the brief's three match-cut invariants - centroid shift <= 6 % of W, dominant axis turn <= 15 deg,
bounding area min/max >= 0.60 - plus det J(t) > 0 (the ARAP guarantee, checked on the solved mesh too). The player
computes them from its own morph (`window.__morphInvariants`, 25 frames of the outline); this tool drives a built player
through render_baseline's harness, seeks into each morph page, and writes them beside the timeline for the gate.

    python measure_morph.py <build-dir> [--timeline NAME.timeline.json] [--html player.html] [--out morph-invariants.json]

Writes <build-dir>/morph-invariants.json: {"html_sha256", "timeline", "scenes": {scene_id: {...invariants}}}.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render_baseline as RB  # noqa: E402
from gate_motion_density import _morph_events as morph_events  # noqa: E402  (P48 T5: the morph_to species, keyed scene@at)

MORPH_INVARIANTS_NAME = "morph-invariants.json"
MORPH_TO_SAMPLE = 0.65   # where in a morph_to's clock the strip is measured: past the leave (XF_MORPH.LEAVE 0.3), mid-morph


def morph_scenes(tl: dict) -> list[dict]:
    """Every ledger page with a morph on it: an ENTER by morph, or a `chart_to morph` species (P48 T5)."""
    return [s for s in tl.get("scenes", []) if (s.get("world") or {}).get("kind") == "ledger"
            and (((s["world"].get("page") or {}).get("enter") == "morph") or morph_events(s))]


def measure_html(html: Path, aspect: str, scenes: list[dict]) -> dict:
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE[aspect]
    srv, port = RB.serve(html.parent)
    out: dict = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            for sc in scenes:
                if ((sc["world"].get("page") or {}).get("enter") == "morph"):
                    ms = float((sc["world"].get("page") or {}).get("morph_s") or 2.0)
                    t = float(sc["span"][0]) + ms / 2
                    RB.frame_png(page, t, (w, h))   # seek: the page builds its morph on first paint
                    inv = page.evaluate("() => window.__morphInvariants ? window.__morphInvariants() : null")
                    out[sc.get("scene_id", "?")] = inv or {"error": "no morph on the page at its midpoint"}
                for ev in morph_events(sc):   # P48 T5: each morph_to, measured mid-morph, keyed scene@at
                    RB.frame_png(page, ev["at"] + ev["dur"] * MORPH_TO_SAMPLE, (w, h))
                    inv = page.evaluate("k => window.__morphInvariants ? window.__morphInvariants(k) : null", f"{ev['from']}>{ev['to']}")
                    out[ev["key"]] = inv or {"error": f"no morph_to strip on the page at {ev['at']:.2f}+{ev['dur'] * MORPH_TO_SAMPLE:.2f} s"}
            browser.close()
    finally:
        srv.shutdown()
    return out


def measure(build: Path, timeline_name: str | None = None, html_name: str = "player.html", out_name: str = MORPH_INVARIANTS_NAME) -> tuple[Path, dict]:
    tls = [build / timeline_name] if timeline_name else sorted(build.glob("*.timeline.json"))
    if not tls or not tls[0].exists():
        raise SystemExit(f"no timeline in {build}")
    tl = json.loads(tls[0].read_text(encoding="utf-8"))
    html = build / html_name
    if not html.exists():
        raise SystemExit(f"no {html_name} in {build}")
    scenes = morph_scenes(tl)
    res = measure_html(html, str(tl.get("aspect") or "16:9"), scenes) if scenes else {}
    doc = {"timeline": tls[0].name, "html_sha256": hashlib.sha256(html.read_bytes()).hexdigest(), "scenes": res}
    out = build / out_name
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return out, res


# ---- THE PAIR, MEASURED WITHOUT A BROWSER (P50 T12; TR-7) --------------------------------------
# The player measures a morph it has ALREADY built. The compiler must refuse a bad pair BEFORE the
# player exists, so the same three invariants are computed here from the two shapes alone - a port of
# arap.mjs's centroid / inertia / dominantAxis / orientedArea / morphInvariants, with the frames being
# the two ENDS (neither method leaves the corridor between them: the ARAP solve pins the centroid on
# the chord and the vertex lerp is the chord, so the pair is a fair test of both).
# The dials are arap.mjs's own ARAP freeze, pinned by test_morph.py so the two languages cannot drift.
MORPH_DIALS = {"CENTROID_MAX": 0.06, "AXIS_MAX_DEG": 15.0, "AREA_MIN_RATIO": 0.60, "N": 96}
STRIP_COLS = 48   # MORPH.COLS in the template: the columns the morph's strip carries
LAND = {"W": 1000, "H": 560, "L": 70, "R": 220, "T": 40, "B": 470}   # the landscape chart's viewBox and the dense-line margins (the template's buildLedgerLine)


def _finite(v) -> bool:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return False
    return f == f and abs(f) != float("inf")


def poly_area(pts: list) -> float:
    """The shoelace area, signed."""
    n, a = len(pts), 0.0
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        a += p[0] * q[1] - q[0] * p[1]
    return a / 2


def ring_centroid(pts: list) -> list:
    """The AREA centroid (the shape's mass), the vertex mean on a degenerate ring."""
    n, a, cx, cy = len(pts), 0.0, 0.0, 0.0
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        w = p[0] * q[1] - q[0] * p[1]
        a += w
        cx += (p[0] + q[0]) * w
        cy += (p[1] + q[1]) * w
    if abs(a) < 1e-9:
        return [sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n]
    return [cx / (3 * a), cy / (3 * a)]


def inertia(pts: list) -> dict:
    """The polygon's second moments about its area centroid - the SHAPE's inertia, not its vertices'
    spread (a strip's two rows of vertices would read as a vertical axis by vertex covariance)."""
    c, n = ring_centroid(pts), len(pts)
    ixx = iyy = ixy = a = 0.0
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        x0, y0, x1, y1 = p[0] - c[0], p[1] - c[1], q[0] - c[0], q[1] - c[1]
        w = x0 * y1 - x1 * y0
        a += w
        ixx += w * (x0 * x0 + x0 * x1 + x1 * x1)
        iyy += w * (y0 * y0 + y0 * y1 + y1 * y1)
        ixy += w * (x0 * y1 + 2 * x0 * y0 + 2 * x1 * y1 + x1 * y0)
    sgn = -1.0 if a < 0 else 1.0   # orientation-free
    return {"xx": sgn * ixx / 12, "yy": sgn * iyy / 12, "xy": sgn * ixy / 24, "area": abs(a) / 2}


def dominant_axis(pts: list) -> float:
    """The angle (radians, in [-pi/2, pi/2)) of the area's major principal axis."""
    I = inertia(pts)
    ang = 0.5 * math.atan2(2 * I["xy"], I["xx"] - I["yy"])
    if ang >= math.pi / 2:
        ang -= math.pi
    if ang < -math.pi / 2:
        ang += math.pi
    return ang


def extent_along(pts: list, ang: float) -> float:
    c, s = math.cos(ang), math.sin(ang)
    vals = [p[0] * c + p[1] * s for p in pts]
    return max(vals) - min(vals)


def oriented_area(pts: list, ang: float) -> float:
    """The bounding area read in a given frame - a shape turned to the chart's axis is not charged for
    the screen-axis box its tilt inflates."""
    return extent_along(pts, ang) * extent_along(pts, ang + math.pi / 2)


def ring_invariants(A: list, B: list, W: float = LAND["W"], dials: dict | None = None) -> dict:
    """The three match-cut invariants for a PAIR of rings, in the keys the player's __morphInvariants
    reports: the centroid shift as a share of W, the dominant-axis turn in degrees, and the min/max of
    the oriented bounding area read in the TARGET's principal frame."""
    P = dict(MORPH_DIALS, **(dials or {}))
    c0, c1 = ring_centroid(A), ring_centroid(B)
    shift = math.hypot(c1[0] - c0[0], c1[1] - c0[1]) / max(1.0, float(W))
    da = abs(dominant_axis(B) - dominant_axis(A))
    if da > math.pi / 2:
        da = math.pi - da
    ang = dominant_axis(B)
    areas = [oriented_area(A, ang), oriented_area(B, ang)]
    ratio = min(areas) / max(1e-9, max(areas))
    deg = da * 180 / math.pi
    return {"centroid_shift": shift, "centroid_ok": shift <= P["CENTROID_MAX"],
            "axis_deg": deg, "axis_ok": deg <= P["AXIS_MAX_DEG"],
            "area_ratio": ratio, "area_ok": ratio >= P["AREA_MIN_RATIO"]}


def _line_scale(spec: dict):
    """The landscape dense-line page's own projection - the MIRROR of the template's buildLedgerLine
    (its margins, the 6 % pad, from_zero, axes.domain / axes.xdomain). (mx, my, axis_b) or None."""
    ax = spec.get("axes") or {}
    series = [s for s in (spec.get("series") or []) if not s.get("later")]
    log = bool(ax.get("log"))

    def Y(v):
        return math.log10(float(v)) if log else float(v)

    xs = [float(x) for s in series for x, _v in (s.get("pts") or [])]
    ys = [Y(v) for s in series for _x, v in (s.get("pts") or [])]
    hl = [h for h in (ax.get("hlines") or ([ax["hline"]] if ax.get("hline") else [])) if h and _finite(h.get("y"))]
    ys += [Y(h["y"]) for h in hl]
    if not xs or not ys:
        return None
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = (y1 - y0) * 0.06 or 1
    y0, y1 = y0 - pad, y1 + pad
    if ax.get("from_zero") and not log:
        y0 = 0
    dom = ax.get("domain")
    if isinstance(dom, (list, tuple)) and len(dom) == 2:
        if _finite(dom[0]):
            y0 = Y(dom[0])
        if _finite(dom[1]):
            y1 = Y(dom[1])
    xd = ax.get("xdomain")
    if isinstance(xd, (list, tuple)) and len(xd) == 2 and _finite(xd[0]) and _finite(xd[1]):
        x0, x1 = float(xd[0]), float(xd[1])
    L, R, T, B, W = LAND["L"], LAND["R"], LAND["T"], LAND["B"], LAND["W"]
    return (lambda x: L + (float(x) - x0) / ((x1 - x0) or 1) * (W - L - R),
            lambda v: T + (1 - (Y(v) - y0) / ((y1 - y0) or 1)) * (B - T), float(B))


def line_strip(spec: dict, cols: int = STRIP_COLS) -> list | None:
    """The ring a morph_to moves: the AREA UNDER the page's first series, built as the player builds it
    (lpStrip) - cols columns at equal x, the top on the line, the bottom on the axis, the ring closing
    back along the axis. Landscape geometry on both sides: the invariants are two ratios and an angle,
    so one fixed frame measures the pair."""
    sc = _line_scale(spec)
    series = [s for s in (spec.get("series") or []) if not s.get("later")]
    if sc is None or not series:
        return None
    mx, my, axis_b = sc
    pts = [[mx(x), my(v)] for x, v in (series[0].get("pts") or [])]
    if len(pts) < 2:
        return None
    x_l, x_r = pts[0][0], pts[-1][0]

    def y_at(x: float) -> float:
        for i in range(len(pts) - 1):
            a, q = pts[i], pts[i + 1]
            if a[0] - 1e-9 <= x <= q[0] + 1e-9:
                u = 0.0 if q[0] == a[0] else (x - a[0]) / (q[0] - a[0])
                return a[1] + (q[1] - a[1]) * min(1.0, max(0.0, u))
        return pts[-1][1]

    xs = [x_l + (i / (cols - 1)) * (x_r - x_l) for i in range(cols)]
    top = [[x, y_at(x)] for x in xs]
    return top + [[x, axis_b] for x in xs][::-1]


def pair_invariants(a_spec: dict, b_spec: dict, cols: int = STRIP_COLS) -> dict | None:
    """The three invariants for two dense-line page specs - the strips a morph_to would move between."""
    A, B = line_strip(a_spec, cols), line_strip(b_spec, cols)
    if A is None or B is None:
        return None
    return ring_invariants(A, B, LAND["W"])


def invariant_line(inv: dict) -> str:
    """One line for a pair, in the gate's M17 wording, with every limit named beside its measurement."""
    return (f"centroid {100 * inv['centroid_shift']:.1f} % W ({'ok' if inv['centroid_ok'] else 'FAIL'}, limit "
            f"{100 * MORPH_DIALS['CENTROID_MAX']:.0f} %), axis {inv['axis_deg']:.1f} deg "
            f"({'ok' if inv['axis_ok'] else 'FAIL'}, limit {MORPH_DIALS['AXIS_MAX_DEG']:.0f} deg), "
            f"area ratio {inv['area_ratio']:.2f} ({'ok' if inv['area_ok'] else 'FAIL'}, floor "
            f"{MORPH_DIALS['AREA_MIN_RATIO']:.2f})")


def _pair_main(a: Path, b: Path, cols: int) -> int:
    """--pair A B: two JSON files, each either a RING (a list of [x, y]) or a page spec / series object
    (whose first series' area under the line is the ring). Exit 1 when an invariant fails."""
    shapes = []
    for p in (a, b):
        doc = json.loads(Path(p).read_text(encoding="utf-8"))
        if isinstance(doc, list):
            shapes.append([[float(q[0]), float(q[1])] for q in doc])
            continue
        ring = line_strip(doc, cols)
        if ring is None:
            print(f"{p}: no series to read a ring from (hand it a list of [x, y], a page spec or a .series.json)")
            return 2
        shapes.append(ring)
    inv = ring_invariants(shapes[0], shapes[1], LAND["W"])
    print(f"{Path(a).name} -> {Path(b).name}: " + invariant_line(inv))
    return 0 if (inv["centroid_ok"] and inv["axis_ok"] and inv["area_ok"]) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("build", type=Path, nargs="?")
    ap.add_argument("--pair", type=Path, nargs=2, metavar=("A", "B"),
                    help="the three invariants for a PAIR of shapes, printed (no browser, no build)")
    ap.add_argument("--cols", type=int, default=STRIP_COLS)
    ap.add_argument("--timeline")
    ap.add_argument("--html", default="player.html")
    ap.add_argument("--out", default=MORPH_INVARIANTS_NAME)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a.pair:
        return _pair_main(a.pair[0], a.pair[1], a.cols)
    if a.build is None:
        ap.error("name a build dir, or --pair A B")
    out, res = measure(a.build, a.timeline, a.html, a.out)
    print(f"morph-invariants: {out}")
    for sid, r in res.items():
        print(f"  {sid}: " + (r.get("error") or f"centroid {100 * r['centroid_shift']:.1f} % W ({'ok' if r['centroid_ok'] else 'FAIL'}), axis {r['axis_deg']:.1f} deg ({'ok' if r['axis_ok'] else 'FAIL'}), area {r['area_ratio']:.2f} ({'ok' if r['area_ok'] else 'FAIL'}), min det {r['min_det']:.3f}, end error {r['end_error']:.4f}"))
    if not res:
        print("  no morph page in the timeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
