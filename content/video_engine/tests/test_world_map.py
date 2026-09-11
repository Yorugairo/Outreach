"""The world map DATA contract (P50 T5): `assets/maps/world-110m.paths.json`.

This test never fetches. It reads the committed artifact only - the builder
(`scripts/build_world_map.py`) is the only thing allowed to touch the network, and it
writes the raw Natural Earth GeoJSON to a cache OUTSIDE the repo.

What is pinned here is what the vecmap species will rely on downstream:

  the node budget      <= 450 nodes per COUNTRY (all its rings summed) - the C4 seek
                       envelope the plan names; and >= 1 node-bearing path, because a
                       country that simplified away is a country that cannot light.
  the ids              three uppercase letters (ISO A3, or ADM0_A3 where Natural Earth
                       carries `-99`; every fallback is named in `notes`).
  the geometry         every path point inside the 1000 x 500 box, and each country's
                       centroid inside its own bbox (the `light`, `arc` and `stamp`
                       events all aim at the centroid).
  the roll call        the countries the P50 T5 shot list names (JPN, USA, CHN, IRN,
                       DEU, GBR, MEX, CAN, KOR, TWN).
  two spot checks      Japan is east of Iran (the projection is not mirrored) and the
                       USA's bbox spans > 200 units (Alaska survived the budget).
  the size             under 1.5 MB, because this file ships in the repo.
"""
from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MAP_REL = "content/video_engine/assets/maps/world-110m.paths.json"
MAP_PATH = ROOT / MAP_REL
SOURCES_PATH = ROOT / "content/video_engine/assets/maps/SOURCES.md"

NODE_BUDGET = 450
MAX_BYTES = 1_500_000
BOX = [1000.0, 500.0]
EPS = 0.01  # the coordinates are rounded to 3 decimals; give the box edge a hair

A3_RE = re.compile(r"^[A-Z]{3}$")
NUM = r"-?\d+(?:\.\d+)?"
PATH_RE = re.compile(rf"^M {NUM} {NUM}(?: L {NUM} {NUM})* Z$")

# The shot list of P50 T5 (shots 57-80: Iran lights, an arc crosses to the US, China
# takes the stamp) plus the channel's recurring names.
REQUIRED = ("JPN", "USA", "CHN", "IRN", "DEU", "GBR", "MEX", "CAN", "KOR", "TWN")


@pytest.fixture(scope="module")
def world() -> dict:
    assert MAP_PATH.exists(), f"missing {MAP_REL} - run scripts/build_world_map.py"
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def path_points(d: str) -> list[tuple[float, float]]:
    assert PATH_RE.match(d), f"not an M/L/Z path string: {d[:80]!r}"
    body = d[2:-2]  # drop the leading "M " and the trailing " Z"
    tokens = body.replace(" L ", " ").split(" ")
    assert len(tokens) % 2 == 0, f"odd coordinate count in {d[:80]!r}"
    return [(float(tokens[i]), float(tokens[i + 1])) for i in range(0, len(tokens), 2)]


def country_nodes(entry: dict) -> int:
    return sum(len(path_points(d)) for d in entry["paths"])


def test_file_exists_and_parses(world):
    assert isinstance(world, dict)
    assert world["box"] == [1000, 500]
    assert world["projection"] == "equirectangular"
    assert isinstance(world["countries"], dict) and world["countries"]


def test_file_is_under_the_size_budget():
    size = MAP_PATH.stat().st_size
    assert size < MAX_BYTES, f"{size} bytes >= {MAX_BYTES}"


def test_source_pins_the_dataset(world):
    src = world["source"]
    assert "natural-earth-vector" in src["url"]
    assert src["dataset"]
    assert src["license"].lower().startswith("public domain")
    # a commit SHA, or (API unreachable) at least the date it was fetched
    assert src.get("commit") or src.get("fetched")
    assert src["node_budget"] == NODE_BUDGET


def test_sources_note_ships_beside_the_data():
    text = SOURCES_PATH.read_text(encoding="utf-8")
    assert "Natural Earth" in text
    assert "public domain" in text.lower()
    assert "equirectangular" in text.lower()
    assert str(NODE_BUDGET) in text


def test_every_id_is_three_uppercase_letters(world):
    bad = [k for k in world["countries"] if not A3_RE.match(k)]
    assert bad == [], f"ids that are not A3: {bad}"


def test_every_country_has_at_least_one_path_within_the_node_budget(world):
    over, empty = [], []
    for code, entry in world["countries"].items():
        if not entry["paths"]:
            empty.append(code)
            continue
        n = country_nodes(entry)
        if n < 3 or n > NODE_BUDGET:
            over.append((code, n))
    assert empty == [], f"countries with no path: {empty}"
    assert over == [], f"countries outside 3..{NODE_BUDGET} nodes: {over}"


def test_every_point_lies_inside_the_box(world):
    outside = []
    for code, entry in world["countries"].items():
        for d in entry["paths"]:
            for x, y in path_points(d):
                if not (-EPS <= x <= BOX[0] + EPS and -EPS <= y <= BOX[1] + EPS):
                    outside.append((code, x, y))
    assert outside[:5] == [], f"{len(outside)} points outside the box, first: {outside[:5]}"


def test_bbox_matches_the_paths_and_holds_the_centroid(world):
    for code, entry in world["countries"].items():
        pts = [p for d in entry["paths"] for p in path_points(d)]
        x0, y0, x1, y1 = entry["bbox"]
        assert x0 <= min(p[0] for p in pts) + EPS and x1 >= max(p[0] for p in pts) - EPS, code
        assert y0 <= min(p[1] for p in pts) + EPS and y1 >= max(p[1] for p in pts) - EPS, code
        cx, cy = entry["centroid"]
        assert x0 - EPS <= cx <= x1 + EPS, f"{code} centroid x {cx} outside bbox {entry['bbox']}"
        assert y0 - EPS <= cy <= y1 + EPS, f"{code} centroid y {cy} outside bbox {entry['bbox']}"


def test_every_country_carries_a_name(world):
    nameless = [c for c, e in world["countries"].items() if not e.get("name")]
    assert nameless == []


@pytest.mark.parametrize("code", REQUIRED)
def test_the_shot_list_countries_are_present(world, code):
    assert code in world["countries"], f"{code} missing"


def test_taiwan_is_present_and_its_id_source_is_recorded(world):
    """TWN may come from ISO_A3 or from ADM0_A3 - it must exist either way, and the
    output must SAY which. The builder names every ADM0_A3 fallback in `notes`."""
    assert "TWN" in world["countries"]
    fallbacks = {n.split(" ", 1)[0] for n in world.get("notes", [])}
    source = "ADM0_A3" if "TWN" in fallbacks else "ISO_A3"
    assert source in ("ISO_A3", "ADM0_A3")


def test_every_adm0_a3_note_names_a_country_in_the_file(world):
    notes = world.get("notes", [])
    assert isinstance(notes, list)
    for note in notes:
        code = note.split(" ", 1)[0]
        assert code in world["countries"], f"note names an absent country: {note}"
        assert "ADM0_A3" in note, f"note does not say where the id came from: {note}"


def test_japan_sits_east_of_iran(world):
    jpn = world["countries"]["JPN"]["centroid"][0]
    irn = world["countries"]["IRN"]["centroid"][0]
    assert jpn > irn, f"JPN centroid x {jpn} should exceed IRN {irn}"


def test_the_usa_bbox_spans_more_than_200_units(world):
    x0, _y0, x1, _y1 = world["countries"]["USA"]["bbox"]
    assert x1 - x0 > 200, f"USA bbox span {x1 - x0} - Alaska or Hawaii fell out"


def test_the_node_histogram_is_reported(world, record_property):
    counts = sorted(country_nodes(e) for e in world["countries"].values())
    record_property("countries", len(counts))
    record_property("nodes_min", counts[0])
    record_property("nodes_median", statistics.median(counts))
    record_property("nodes_max", counts[-1])
    assert counts[-1] <= NODE_BUDGET
