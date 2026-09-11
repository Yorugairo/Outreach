"""WORLD MAP PATHS - Natural Earth 1:110m countries as SVG paths on a 1000 x 500 box.

The DATA half of P50 T5 ("the vector map"). The species (`vecmap`: the outline in the
muted ink, `light` on a word, the `arc` with its X, the `stamp`) is built elsewhere; this
tool only produces the geometry it aims at, once, into the repo:

    python content/video_engine/scripts/build_world_map.py

  in   `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/
        ne_110m_admin_0_countries.geojson` (public domain; ~820 KB), cached OUTSIDE the
        repo - the raw GeoJSON is never committed.
  out  `content/video_engine/assets/maps/world-110m.paths.json` (+ `SOURCES.md`).

THE FOUR DECISIONS, and why:

  the projection    equirectangular, x = (lon + 180) / 360 * 1000, y = (90 - lat) / 180 *
                    500, 3 decimals. Plate carree keeps the arithmetic the template needs
                    reversible (a centroid is a lon/lat away), and a centroid stays where
                    the eye expects it on a stage-wide map.
  the node budget   <= 450 nodes per COUNTRY, all rings summed - the C4 seek envelope. The
                    epsilon is TIGHTENED (raised) per country until it fits, never the
                    country dropped: Canada, Antarctica and Russia are the only three that
                    need it at 1:110m. Polygons are ranked by |area| so a fjord island
                    never eats the mainland's budget, and a polygon's holes ride with it
                    (Lesotho stays a hole in South Africa, not a filled blot).
  the ring split    Douglas-Peucker on a CLOSED ring would anchor both ends on the same
                    point and let the far side wander, so each ring is cut at the point
                    farthest from its start and the two chains are simplified separately.
  the id            ISO_A3, and ADM0_A3 where Natural Earth carries `-99` (Norway, France,
                    N. Cyprus, Somaliland, Kosovo at this commit). Every fallback is named
                    in the output's `notes`, so a downstream `light: ["FRA"]` can be traced
                    to the reason its id is not an ISO code.

Standard library only (no shapely, no pyproj - a pure-Python Douglas-Peucker is 30 lines).
The output is deterministic: countries sorted by id, coordinates rounded before they are
compared, no timestamp inside `countries`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO = Path(__file__).resolve().parents[3]

DATASET = "Natural Earth 1:110m Cultural Vectors - Admin 0 Countries"
REPO_SLUG = "nvkelso/natural-earth-vector"
GEOJSON_REL = "geojson/ne_110m_admin_0_countries.geojson"
RAW_URL = f"https://raw.githubusercontent.com/{REPO_SLUG}/master/{GEOJSON_REL}"
API_COMMITS = f"https://api.github.com/repos/{REPO_SLUG}/commits?path={GEOJSON_REL}&per_page=1"
API_BLOB = f"https://api.github.com/repos/{REPO_SLUG}/contents/{GEOJSON_REL}?ref={{ref}}"
LICENSE = "public domain (Natural Earth terms of use)"

OUT_REL = "content/video_engine/assets/maps/world-110m.paths.json"
SOURCES_REL = "content/video_engine/assets/maps/SOURCES.md"

BOX_W, BOX_H = 1000, 500
NODE_BUDGET = 450
DECIMALS = 3
EPS_BASE = 0.02          # box units; 1 unit = 0.36 deg of longitude
EPS_GROWTH = 1.6
EPS_STEPS = 48
MIN_RING_NODES = 3
USER_AGENT = "outreach-program/build_world_map (+repo-local tool)"
HTTP_TIMEOUT = 60


# --------------------------------------------------------------------------- fetching

def default_cache_dir() -> Path:
    env = os.environ.get("WORLD_MAP_CACHE")
    if env:
        return Path(env)
    tmp = os.environ.get("TEMP") or os.environ.get("TMPDIR") or "/tmp"
    return Path(tmp) / "natural-earth-cache"


def http_get(url: str, timeout: int = HTTP_TIMEOUT) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def git_blob_sha1(payload: bytes) -> str:
    """The SHA-1 git itself would give the file, so the pin can be VERIFIED, not trusted."""
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def fetch_geojson(cache: Path, offline: bool) -> tuple[bytes, bool]:
    """Return (payload, from_cache). The raw dataset never enters the repo."""
    cache.parent.mkdir(parents=True, exist_ok=True)
    if offline or cache.exists():
        if cache.exists():
            return cache.read_bytes(), True
        raise SystemExit(f"--offline but no cache at {cache}")
    payload = http_get(RAW_URL)
    cache.write_bytes(payload)
    return payload, False


def resolve_pin(payload: bytes, fetched: str) -> dict[str, Any]:
    """The commit the raw file came from, verified against its blob SHA where possible.

    The API is best-effort: when it cannot be reached the date and the URL are recorded
    instead, which is what the brief asks for.
    """
    blob = git_blob_sha1(payload)
    pin: dict[str, Any] = {
        "dataset": DATASET,
        "url": RAW_URL,
        "license": LICENSE,
        "blob_sha1": blob,
        "fetched": fetched,
        "bytes": len(payload),
    }
    try:
        commits = json.loads(http_get(API_COMMITS, timeout=20).decode("utf-8"))
        commit = commits[0]
        pin["commit"] = commit["sha"]
        pin["commit_date"] = commit["commit"]["committer"]["date"]
    except (urllib.error.URLError, OSError, ValueError, KeyError, IndexError) as exc:
        pin["commit"] = None
        pin["pin_note"] = f"GitHub API unreachable ({type(exc).__name__}); pinned by date + blob SHA-1"
        return pin
    try:
        meta = json.loads(http_get(API_BLOB.format(ref=pin["commit"]), timeout=20).decode("utf-8"))
        pin["blob_verified"] = meta.get("sha") == blob
    except (urllib.error.URLError, OSError, ValueError) as exc:
        pin["blob_verified"] = None
        pin["pin_note"] = f"blob not cross-checked ({type(exc).__name__})"
    return pin


# ------------------------------------------------------------------------- projection

Point = tuple[float, float]


def project(lon: float, lat: float) -> Point:
    """Equirectangular onto the 1000 x 500 box, rounded once, at the source."""
    lon = min(180.0, max(-180.0, float(lon)))
    lat = min(90.0, max(-90.0, float(lat)))
    x = (lon + 180.0) / 360.0 * BOX_W
    y = (90.0 - lat) / 180.0 * BOX_H
    return (round(x, DECIMALS), round(y, DECIMALS))


def dedupe(points: Sequence[Point]) -> list[Point]:
    """Drop consecutive repeats (rounding creates them) and the closing duplicate."""
    out: list[Point] = []
    for p in points:
        if not out or p != out[-1]:
            out.append(p)
    while len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


# ------------------------------------------------------------------- Douglas-Peucker

def _perpendicular_distance(p: Point, a: Point, b: Point) -> float:
    if a == b:
        return ((p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2) ** 0.5
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = (dx * dx + dy * dy) ** 0.5
    return abs(dy * p[0] - dx * p[1] + b[0] * a[1] - b[1] * a[0]) / length


def simplify_chain(points: Sequence[Point], eps: float) -> list[Point]:
    """Douglas-Peucker, iterative (no recursion limit on a 600-node coastline)."""
    if len(points) < 3:
        return list(points)
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        start, end = stack.pop()
        if end <= start + 1:
            continue
        worst, worst_at = -1.0, start
        for i in range(start + 1, end):
            d = _perpendicular_distance(points[i], points[start], points[end])
            if d > worst:
                worst, worst_at = d, i
        if worst > eps:
            keep[worst_at] = True
            stack.append((start, worst_at))
            stack.append((worst_at, end))
    return [p for p, k in zip(points, keep) if k]


def _farthest_from(origin: Point, points: Sequence[Point]) -> int:
    best, best_at = -1.0, 0
    for i, p in enumerate(points):
        d = (p[0] - origin[0]) ** 2 + (p[1] - origin[1]) ** 2
        if d > best:
            best, best_at = d, i
    return best_at


def simplify_ring(ring: Sequence[Point], eps: float) -> list[Point]:
    """A ring is cut at its farthest point from the start, so both halves keep their shape.

    Simplifying a closed ring in one pass anchors start and end on the SAME coordinate:
    the perpendicular distance then measures from a degenerate segment and the far side of
    the country collapses. Two chains, two anchors, no collapse.
    """
    if len(ring) < 4:
        return list(ring)
    far = _farthest_from(ring[0], ring)
    first = simplify_chain(ring[: far + 1], eps)
    second = simplify_chain(ring[far:] + [ring[0]], eps)
    merged = first + second[1:-1]
    return dedupe(merged)


def coarse_ring(ring: Sequence[Point]) -> list[Point]:
    """The last resort: the triangle of the three most distant points. Never a dropped country."""
    if len(ring) < 3:
        return list(ring)
    a = ring[_farthest_from(ring[0], ring)]
    b = ring[_farthest_from(a, ring)]
    c_at, best = 0, -1.0
    for i, p in enumerate(ring):
        d = _perpendicular_distance(p, a, b)
        if d > best:
            best, c_at = d, i
    return dedupe([a, b, ring[c_at]])


# ---------------------------------------------------------------------------- geometry

def ring_area(points: Sequence[Point]) -> float:
    """Twice the signed shoelace area; sign carries winding, callers use abs()."""
    total = 0.0
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        total += x0 * y1 - x1 * y0
    return total / 2.0


def ring_centroid(points: Sequence[Point]) -> Point:
    """The area-weighted centroid; the mean of the nodes when the ring has no area."""
    area = ring_area(points)
    if abs(area) < 1e-9:
        n = max(1, len(points))
        return (round(sum(p[0] for p in points) / n, DECIMALS),
                round(sum(p[1] for p in points) / n, DECIMALS))
    cx = cy = 0.0
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    factor = 1.0 / (6.0 * area)
    return (round(cx * factor, DECIMALS), round(cy * factor, DECIMALS))


def bbox_of(points: Iterable[Point]) -> list[float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def _num(value: float) -> str:
    text = f"{value:.{DECIMALS}f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def path_string(points: Sequence[Point]) -> str:
    head = f"M {_num(points[0][0])} {_num(points[0][1])}"
    tail = "".join(f" L {_num(x)} {_num(y)}" for x, y in points[1:])
    return f"{head}{tail} Z"


# -------------------------------------------------------------------- the node budget

def polygons_of(geometry: dict) -> list[list[list[Point]]]:
    """Every polygon as [exterior, *holes], projected, de-duplicated, largest first."""
    if geometry["type"] == "Polygon":
        raw = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        raw = geometry["coordinates"]
    else:
        raise ValueError(f"unsupported geometry {geometry['type']!r}")
    polygons: list[list[list[Point]]] = []
    for poly in raw:
        rings = [dedupe([project(lon, lat) for lon, lat, *_ in ring]) for ring in poly]
        rings = [r for r in rings if len(r) >= MIN_RING_NODES]
        if rings:
            polygons.append(rings)
    polygons.sort(key=lambda rings: abs(ring_area(rings[0])), reverse=True)
    return polygons


def _simplified(polygons: Sequence[Sequence[Sequence[Point]]], eps: float) -> list[list[list[Point]]]:
    out: list[list[list[Point]]] = []
    for rings in polygons:
        simplified = [simplify_ring(r, eps) for r in rings]
        simplified = [r for r in simplified if len(r) >= MIN_RING_NODES]
        if simplified:
            out.append(simplified)
    return out


def _take_within_budget(polygons: Sequence[Sequence[Sequence[Point]]], budget: int) -> list[list[Point]]:
    """Largest polygon first; a polygon is taken whole (with its holes) or not at all."""
    taken: list[list[Point]] = []
    used = 0
    for rings in polygons:
        cost = sum(len(r) for r in rings)
        if used + cost > budget:
            continue
        taken.extend(rings)
        used += cost
    return taken


def fit_country(polygons: Sequence[Sequence[Sequence[Point]]], budget: int) -> tuple[list[list[Point]], float, int]:
    """Raise epsilon until every ring of the country fits the budget together.

    Returns (rings, epsilon, steps) where steps counts how many times the epsilon had to
    be tightened past the base - 0 means the country was already inside the envelope.
    """
    eps = EPS_BASE
    for step in range(EPS_STEPS):
        simplified = _simplified(polygons, eps)
        total = sum(len(r) for rings in simplified for r in rings)
        if simplified and total <= budget:
            return [r for rings in simplified for r in rings], eps, step
        eps *= EPS_GROWTH
    # Nothing fit whole: keep the largest polygons that do, and failing even that, the
    # coarse triangle of the biggest ring. A country is never dropped.
    simplified = _simplified(polygons, eps)
    taken = _take_within_budget(simplified, budget)
    if not taken:
        taken = [coarse_ring(polygons[0][0])]
    return taken, eps, EPS_STEPS


# ------------------------------------------------------------------------------ build

def country_id(properties: dict) -> tuple[str, str]:
    """(id, source) - ISO_A3 unless Natural Earth carries `-99` there."""
    iso = (properties.get("ISO_A3") or "").strip()
    if len(iso) == 3 and iso.isalpha() and iso.isupper():
        return iso, "ISO_A3"
    adm = (properties.get("ADM0_A3") or "").strip()
    if len(adm) == 3 and adm.isalpha() and adm.isupper():
        return adm, "ADM0_A3"
    return "", "none"


def build(geojson: dict, budget: int) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    countries: dict[str, Any] = {}
    notes: list[str] = []
    tightened: list[tuple[str, int]] = []
    skipped: list[str] = []
    for feature in geojson["features"]:
        properties = feature["properties"]
        name = properties.get("NAME") or properties.get("NAME_LONG") or properties.get("SOVEREIGNT")
        code, source = country_id(properties)
        if not code:
            skipped.append(str(name))
            continue
        polygons = polygons_of(feature["geometry"])
        if not polygons:
            skipped.append(str(name))
            continue
        rings, eps, steps = fit_country(polygons, budget)
        points = [p for ring in rings for p in ring]
        entry = {
            "name": name,
            "centroid": list(ring_centroid(rings[0])),
            "bbox": bbox_of(points),
            "paths": [path_string(r) for r in rings],
        }
        if code in countries:  # defensive: two features under one id would silently lose one
            merged = countries[code]
            merged["paths"].extend(entry["paths"])
            merged["bbox"] = bbox_of(points + [(merged["bbox"][0], merged["bbox"][1]),
                                               (merged["bbox"][2], merged["bbox"][3])])
            notes.append(f"{code} ({name}): two Natural Earth features share this id; their rings are merged")
        else:
            countries[code] = entry
        if source == "ADM0_A3":
            notes.append(
                f"{code} ({name}): id taken from ADM0_A3 because ISO_A3 is -99 in Natural Earth 1:110m"
            )
        if steps:
            tightened.append((code, steps))
    stats = {
        "tightened": sorted(tightened),
        "skipped": skipped,
        "epsilon_base": EPS_BASE,
    }
    return dict(sorted(countries.items())), sorted(notes), stats


def sources_markdown(pin: dict[str, Any], budget: int, countries: int, notes: Sequence[str]) -> str:
    commit = pin.get("commit") or "(GitHub API unreachable - pinned by date + blob SHA-1)"
    verified = pin.get("blob_verified")
    verified_line = {
        True: "verified: the downloaded bytes hash to the blob SHA git records at that commit",
        False: "NOT verified: the blob at that commit differs from the bytes downloaded",
        None: "not cross-checked (the contents API was unreachable)",
    }[verified if verified in (True, False) else None]
    note_lines = "\n".join(f"- {n}" for n in notes) or "- (none)"
    return f"""# Map sources

## `world-110m.paths.json`

| field | value |
|---|---|
| dataset | {DATASET} |
| license | **{LICENSE}** - no attribution required, none withheld |
| source | `{pin['url']}` |
| commit | `{commit}` |
| commit date | {pin.get('commit_date', '(unknown)')} |
| fetched | {pin['fetched']} |
| raw bytes | {pin['bytes']} |
| raw blob SHA-1 | `{pin['blob_sha1']}` ({verified_line}) |
| countries | {countries} |
| projection | equirectangular (plate carree), x = (lon + 180) / 360 * {BOX_W}, y = (90 - lat) / 180 * {BOX_H} |
| box | {BOX_W} x {BOX_H} units, 3 decimals |
| node budget | {budget} nodes per country, all rings summed (the C4 seek envelope, P50 T5) |
| simplification | Douglas-Peucker, pure Python, epsilon raised per country until the budget fits; a ring is cut at its farthest point from the start so neither half collapses |
| ids | ISO_A3, falling back to ADM0_A3 where Natural Earth carries `-99` |

The raw GeoJSON is **not** in the repo: the builder caches it outside the tree
(`WORLD_MAP_CACHE`, else the system temp dir). Rebuild with

    python content/video_engine/scripts/build_world_map.py

Natural Earth's terms: "All versions of Natural Earth raster + vector map data found on
this website are in the public domain."

### ids that did not come from ISO_A3

{note_lines}
"""


def render_json(document: dict[str, Any]) -> str:
    """One country per LINE: compact enough to ship, readable enough to diff.

    A 186 KB single line would make the next Natural Earth bump an unreviewable diff;
    indenting every coordinate would triple the file. One line per country is the seam.
    """
    compact = {"separators": (",", ":"), "ensure_ascii": False}
    head = {k: v for k, v in document.items() if k != "countries"}
    lines = ["{"]
    for key, value in head.items():
        lines.append(f" {json.dumps(key)}: {json.dumps(value, indent=None, **compact)},")
    lines.append(' "countries": {')
    entries = list(document["countries"].items())
    for i, (code, entry) in enumerate(entries):
        comma = "," if i < len(entries) - 1 else ""
        lines.append(f"  {json.dumps(code)}: {json.dumps(entry, **compact)}{comma}")
    lines.append(" }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cache", type=Path, default=None,
                        help="where the raw GeoJSON is cached (never inside the repo)")
    parser.add_argument("--offline", action="store_true", help="use the cache, do not fetch")
    parser.add_argument("--budget", type=int, default=NODE_BUDGET, help="nodes per country")
    parser.add_argument("--out", type=Path, default=REPO / OUT_REL)
    args = parser.parse_args(argv)

    cache = args.cache or (default_cache_dir() / "ne_110m_admin_0_countries.geojson")
    if REPO in cache.resolve().parents:
        raise SystemExit(f"refusing to cache the raw dataset inside the repo: {cache}")

    payload, from_cache = fetch_geojson(cache, args.offline)
    # The DOWNLOAD's date, not today's: rebuilding from an unchanged cache must not
    # churn the committed file.
    fetched = date.fromtimestamp(cache.stat().st_mtime).isoformat()
    pin = resolve_pin(payload, fetched)
    geojson = json.loads(payload.decode("utf-8"))

    countries, notes, stats = build(geojson, args.budget)
    pin_out = dict(pin)
    pin_out["node_budget"] = args.budget
    document = {
        "source": pin_out,
        "box": [BOX_W, BOX_H],
        "projection": "equirectangular",
        "notes": notes,
        "countries": countries,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_json(document), encoding="utf-8", newline="\n")
    (REPO / SOURCES_REL).write_text(
        sources_markdown(pin, args.budget, len(countries), notes), encoding="utf-8", newline="\n")

    counts = sorted(sum(d.count(" L ") + 1 for d in e["paths"]) for e in countries.values())
    size = args.out.stat().st_size
    print(f"cache      {cache} ({'reused' if from_cache else 'fetched'}, {pin['bytes']} bytes)")
    print(f"commit     {pin.get('commit')} ({pin.get('commit_date')}), blob verified={pin.get('blob_verified')}")
    print(f"countries  {len(countries)}  (skipped: {stats['skipped'] or 'none'})")
    print(f"nodes      min {counts[0]} / median {statistics.median(counts)} / max {counts[-1]} "
          f"/ total {sum(counts)}")
    print(f"tightened  {len(stats['tightened'])}: {stats['tightened'] or 'none'}")
    print(f"ADM0_A3    {[n.split(' ', 1)[0] for n in notes] or 'none'}")
    print(f"out        {args.out} ({size} bytes)")
    print(f"sources    {REPO / SOURCES_REL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
