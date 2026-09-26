"""MAP PLACES - the named POINTS of the vector map: places too small for its outlines, from a sourced gazetteer.

P73 T5 (the AMD RFSoC episode's route: United States -> Hong Kong -> China). `world-110m.paths.json` is Natural Earth
1:110m, and at that scale Hong Kong, Singapore and Macau have no shape (Natural Earth drops them; Hsinchu is a city,
never a country). A map POINT is a named place with a SOURCED longitude / latitude, projected through the map's OWN
projection (build_world_map.project - the same equirectangular box, to the bit), that an arc may start or end at, that a
stamp may write at, and that a `light` lights as a dot and its name (species/vecmap.mjs `paintPlaceLight`):

    python content/video_engine/scripts/build_map_places.py

  in   Natural Earth 1:10m Cultural Vectors - Populated Places (simple), the SAME repository and the SAME commit as the
       world's outlines (`nvkelso/natural-earth-vector` @ 9380cca8, public domain; ~4.9 MB), fetched at the pinned
       commit and VERIFIED against its git blob SHA-1 - a changed file is refused, never silently re-pinned. Cached
       OUTSIDE the repo; the raw GeoJSON is never committed.
  out  `content/video_engine/assets/maps/places.json` (+ `SOURCES-places.md`).

WHICH PLACES: the ones PLACES names, each by its Natural Earth `ne_id` (a row id that survives a re-sort) and the name
that row must carry (a mismatch is refused - the row was not the place we meant). A new place is one line here, from
this gazetteer, and a rebuild; never a typed latitude. The ID: the place's own ISO 3166-1 alpha-3 where Natural Earth
gives it one as an Admin-0 entity (HKG, MAC, SGP - codes world-110m never uses, so a place cannot shadow a country),
else its ASCII name uppercased (HSINCHU). The POINT: the feature's own geometry (Natural Earth's `latitude` /
`longitude` columns differ from it by up to 0.014 deg for Macau; the geometry is the point Natural Earth draws).
Standard library only; deterministic (places sorted by id, coordinates rounded once).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

import build_world_map as WM

DATASET = "Natural Earth 1:10m Cultural Vectors - Populated Places (simple)"
GEOJSON_REL = "geojson/ne_10m_populated_places_simple.geojson"
COMMIT = "9380cca83db5f9aef52d5e762765100745f84b27"   # the commit world-110m.paths.json is pinned at (SOURCES.md)
RAW_URL = f"https://raw.githubusercontent.com/{WM.REPO_SLUG}/{COMMIT}/{GEOJSON_REL}"
BLOB_SHA1 = "534edbb72fee39f476239e24fd4b24acf6f965d5"   # git's own hash of the file at COMMIT (GitHub contents API, 2026-09-26)
OUT_REL = "content/video_engine/assets/maps/places.json"
SOURCES_REL = "content/video_engine/assets/maps/SOURCES-places.md"

# (id, Natural Earth ne_id, the name that row must carry) - the story's transshipment points and the brief's four
PLACES = (
    ("HKG", 1159151629, "Hong Kong"),   # Admin-0 region capital (adm0_a3 HKG, sov CHN)
    ("SGP", 1159151627, "Singapore"),   # Admin-0 capital
    ("MAC", 1159149085, "Macau"),       # Admin-0 region capital (adm0_a3 MAC, sov CHN)
    ("HSINCHU", 1159146175, "Hsinchu"),  # Admin-1 capital, Taiwan (the science park's city)
)
KEPT_FIELDS = ("adm0_a3", "featurecla", "ne_id")   # `name` is the label


def select_places(geojson: dict, wanted: Sequence[tuple[str, int, str]] = PLACES) -> dict[str, dict[str, Any]]:
    """The named rows, projected. ValueError names a missing row, a name that does not match its row, or an id twice."""
    rows = {f.get("properties", {}).get("ne_id"): f for f in geojson.get("features", [])}
    out: dict[str, dict[str, Any]] = {}
    for pid, ne_id, name in wanted:
        if pid in out:
            raise ValueError(f"place {pid!r} is named twice")
        feat = rows.get(ne_id)
        if feat is None:
            raise ValueError(f"place {pid!r}: ne_id {ne_id} is not in the gazetteer")
        props = feat["properties"]
        if props.get("name") != name:
            raise ValueError(f"place {pid!r}: ne_id {ne_id} is {props.get('name')!r}, not {name!r}")
        lon, lat = (float(v) for v in feat["geometry"]["coordinates"][:2])
        x, y = WM.project(lon, lat)
        out[pid] = {"label": name, "lon": round(lon, 6), "lat": round(lat, 6), "x": x, "y": y,
                    **{k: props.get(k) for k in KEPT_FIELDS}}
    return dict(sorted(out.items()))


def fetch(cache: Path, offline: bool) -> bytes:
    """The raw file at the pinned commit, from the cache when present; refused unless it hashes to BLOB_SHA1."""
    if cache.exists():
        payload = cache.read_bytes()
    elif offline:
        raise SystemExit(f"--offline but no cache at {cache}")
    else:
        cache.parent.mkdir(parents=True, exist_ok=True)
        payload = WM.http_get(RAW_URL)
        cache.write_bytes(payload)
    got = WM.git_blob_sha1(payload)
    if got != BLOB_SHA1:
        raise SystemExit(f"{cache}: blob SHA-1 {got} is not the pinned {BLOB_SHA1} - the gazetteer changed; re-pin deliberately")
    return payload


def document(places: dict[str, dict[str, Any]], nbytes: int) -> dict[str, Any]:
    return {"source": {"dataset": DATASET, "url": RAW_URL, "commit": COMMIT, "blob_sha1": BLOB_SHA1, "bytes": nbytes,
                       "license": WM.LICENSE, "point": "the feature's own geometry (lon, lat)"},
            "box": [WM.BOX_W, WM.BOX_H], "projection": "equirectangular (build_world_map.project)", "places": places}


def render_json(doc: dict[str, Any]) -> str:
    """One place per line, as the world file carries one country per line."""
    compact = {"separators": (",", ":"), "ensure_ascii": False}
    lines = ["{"] + [f" {json.dumps(k)}: {json.dumps(v, **compact)}," for k, v in doc.items() if k != "places"]
    lines.append(' "places": {')
    items = list(doc["places"].items())
    lines += [f"  {json.dumps(k)}: {json.dumps(v, **compact)}{',' if i < len(items) - 1 else ''}" for i, (k, v) in enumerate(items)]
    return "\n".join(lines + [" }", "}"]) + "\n"


def sources_markdown(doc: dict[str, Any]) -> str:
    s = doc["source"]
    rows = "\n".join(f"| {pid} | {p['label']} | {p['featurecla']} | {p['adm0_a3']} | {p['ne_id']} | {p['lon']} | {p['lat']} "
                     f"| {p['x']} | {p['y']} |" for pid, p in doc["places"].items())
    return (f"# Map places - sources\n\n## `places.json`\n\n| field | value |\n|---|---|\n| dataset | {s['dataset']} |\n"
            f"| license | **{s['license']}** |\n| source | `{s['url']}` |\n| commit | `{s['commit']}` (the commit "
            f"`world-110m.paths.json` is pinned at) |\n| raw bytes | {s['bytes']} |\n| raw blob SHA-1 | `{s['blob_sha1']}` "
            "(verified on every build: the bytes must hash to it) |\n| point | the feature's own geometry |\n"
            "| projection | build_world_map.project - x = (lon + 180) / 360 * 1000, y = (90 - lat) / 180 * 500 |\n\n"
            "| id | label | Natural Earth class | adm0_a3 | ne_id | lon | lat | x | y |\n|---|---|---|---|---|---|---|---|---|\n"
            f"{rows}\n\nRebuild with\n\n    python content/video_engine/scripts/build_map_places.py\n")


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", type=Path, default=None, help="where the raw GeoJSON is cached (never inside the repo)")
    ap.add_argument("--offline", action="store_true", help="use the cache, do not fetch")
    ap.add_argument("--out", type=Path, default=WM.REPO / OUT_REL)
    args = ap.parse_args(argv)
    cache = args.cache or (WM.default_cache_dir() / f"ne_10m_populated_places_simple-{BLOB_SHA1[:12]}.geojson")
    if WM.REPO in cache.resolve().parents:
        raise SystemExit(f"refusing to cache the raw dataset inside the repo: {cache}")
    payload = fetch(cache, args.offline)
    doc = document(select_places(json.loads(payload.decode("utf-8"))), len(payload))
    args.out.write_text(render_json(doc), encoding="utf-8", newline="\n")
    (WM.REPO / SOURCES_REL).write_text(sources_markdown(doc), encoding="utf-8", newline="\n")
    print(f"places  {', '.join(doc['places'])} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
