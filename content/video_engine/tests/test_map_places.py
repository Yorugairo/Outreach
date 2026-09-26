"""P73 T5 - MAP POINTS: Hong Kong and Singapore on the vector map.

`world-110m.paths.json` (Natural Earth 1:110m) has no Hong Kong, Singapore or Macau - at that scale they have no shape
- so the AMD RFSoC episode's route (United States -> Hong Kong -> China) had nowhere to land but a typed `mappoint`,
and a mappoint cannot LIGHT. A map POINT is a named place with a SOURCED longitude / latitude (Natural Earth 1:10m
populated places at the world map's own commit, blob-verified - `build_map_places.py`), projected through the map's own
projection, that an arc starts or ends at, a stamp writes at, and a light lights as a DOT and its NAME, pinging on its
word through T46d's ping. These tests pin the data contract (never fetching), the compiler's grammar - a place by its
id, refused by name when unknown or when its point is typed - the resolution the player reads, and the golden.
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "scripts"))
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "tests" / "golden"))
import build_scene_timeline_f as B  # noqa: E402
import build_map_places as MP  # noqa: E402
import build_world_map as WM  # noqa: E402

MAPS = ROOT / "content" / "video_engine" / "assets" / "maps"
PLACES_PATH = MAPS / "places.json"
WORLD_PATH = MAPS / "world-110m.paths.json"
NODE_TEST = "content/video_engine/tests/kinetics/vecmap_places.test.mjs"
PLATE = "vecmap:USA,CHN;fit=tight"
HKG = {"kind": "place", "id": "HKG"}


@pytest.fixture(scope="module")
def places() -> dict:
    return json.loads(PLACES_PATH.read_text(encoding="utf-8"))


def light(target=None, **extra) -> dict:
    entry = {"kind": "light", "at": 5.9, "dur": 10.0, "target": copy.deepcopy(target or HKG)}
    entry.update(extra)
    return entry


def errors(*entries: dict, plate: str = PLATE) -> list[str]:
    return B.validate_species(list(entries), (0, 0, 0), plate)


# ---------------------------------------------------------------- the data: sourced, projected by the map's own law
def test_the_places_file_names_hong_kong_singapore_macau_and_hsinchu(places):
    assert set(places["places"]) >= {"HKG", "SGP", "MAC", "HSINCHU"}
    assert places["places"]["HKG"]["label"] == "Hong Kong" and places["places"]["SGP"]["label"] == "Singapore"


def test_the_source_is_pinned_at_the_world_maps_own_commit_by_its_blob_hash(places):
    src = places["source"]
    world_src = json.loads(WORLD_PATH.read_text(encoding="utf-8"))["source"]
    assert src["commit"] == world_src["commit"] == MP.COMMIT, "the points and the outlines are one dataset's, one commit"
    assert re.fullmatch(r"[0-9a-f]{40}", src["blob_sha1"]) and src["blob_sha1"] == MP.BLOB_SHA1
    assert src["url"].endswith(MP.GEOJSON_REL) and MP.COMMIT in src["url"], "fetched at the pin, never at master"
    assert "public domain" in src["license"]
    assert (MAPS / "SOURCES-places.md").is_file()
    note = (MAPS / "SOURCES-places.md").read_text(encoding="utf-8")
    for pid, p in places["places"].items():
        assert f"| {pid} | {p['label']} |" in note and str(p["ne_id"]) in note, pid


def test_every_point_is_the_world_maps_projection_of_its_own_lon_lat(places):
    assert places["box"] == json.loads(WORLD_PATH.read_text(encoding="utf-8"))["box"]
    for pid, p in places["places"].items():
        assert (p["x"], p["y"]) == WM.project(p["lon"], p["lat"]), pid
        assert 0 <= p["x"] <= 1000 and 0 <= p["y"] <= 500, pid


def test_the_recorded_rows_are_the_gazetteers(places):
    """The four rows as Natural Earth 1:10m carries them at 9380cca8 (read off the fetched file, NOTES.md) - a typed
    latitude would drift from these; the geometry, not the lat/long columns (Macau's differ by 0.014 deg)."""
    want = {"HKG": (1159151629, 114.183064, 22.306927), "SGP": (1159151627, 103.853875, 1.294979),
            "MAC": (1159149085, 113.544375, 22.189135), "HSINCHU": (1159146175, 120.976739, 24.816791)}
    for pid, (ne_id, lon, lat) in want.items():
        p = places["places"][pid]
        assert (p["ne_id"], p["lon"], p["lat"]) == (ne_id, lon, lat), pid


def test_no_place_shadows_a_country_and_every_id_is_uppercase(places):
    countries = json.loads(WORLD_PATH.read_text(encoding="utf-8"))["countries"]
    for pid in places["places"]:
        assert pid not in countries, f"{pid}: a place id must never be a country's - the two target kinds would collide"
        assert re.fullmatch(r"[A-Z][A-Z0-9-]*", pid), pid


def test_hong_kong_sits_on_chinas_south_coast_and_singapore_below_malaysia(places):
    """A spot check that the projection is the map's: Hong Kong inside China's bbox near its southern edge, Singapore at
    the tip of the peninsula, just south of Malaysia's bbox top and inside its x span."""
    countries = json.loads(WORLD_PATH.read_text(encoding="utf-8"))["countries"]
    hk, sg = places["places"]["HKG"], places["places"]["SGP"]
    x0, y0, x1, y1 = countries["CHN"]["bbox"]
    assert x0 < hk["x"] < x1 and y0 < hk["y"] < y1 and hk["y"] > (y0 + y1) / 2
    mx0, my0, mx1, my1 = countries["MYS"]["bbox"]
    assert mx0 < sg["x"] < mx1 and my0 < sg["y"]


def test_the_builder_selects_by_ne_id_and_refuses_a_row_that_is_not_the_place():
    feats = [{"properties": {"ne_id": 1, "name": "Hong Kong", "adm0_a3": "HKG", "featurecla": "x"},
              "geometry": {"coordinates": [114.183064, 22.306927]}}]
    got = MP.select_places({"features": feats}, (("HKG", 1, "Hong Kong"),))
    assert got["HKG"]["x"] == WM.project(114.183064, 22.306927)[0] and got["HKG"]["label"] == "Hong Kong"
    with pytest.raises(ValueError, match="not 'Singapore'"):
        MP.select_places({"features": feats}, (("SGP", 1, "Singapore"),))
    with pytest.raises(ValueError, match="not in the gazetteer"):
        MP.select_places({"features": feats}, (("SGP", 2, "Singapore"),))
    with pytest.raises(ValueError, match="named twice"):
        MP.select_places({"features": feats}, (("HKG", 1, "Hong Kong"), ("HKG", 1, "Hong Kong")))


def test_the_builder_refuses_a_changed_gazetteer(tmp_path):
    cache = tmp_path / "places.geojson"
    cache.write_bytes(b'{"features": []}')
    with pytest.raises(SystemExit, match="re-pin deliberately"):
        MP.fetch(cache, offline=True)


# ---------------------------------------------------------------- the grammar: a place by NAME
def test_a_place_lights_stamps_and_ends_an_arc():
    usa = {"kind": "country", "id": "USA"}
    assert errors(light(ping=True)) == []
    assert errors({"kind": "stamp", "at": 7.0, "dur": 6.0, "text": "customs", "target": copy.deepcopy(HKG)}) == []
    assert errors({"kind": "arc", "at": 5.0, "dur": 12.0, "from": usa, "to": copy.deepcopy(HKG)},
                  {"kind": "arc", "at": 7.2, "dur": 10.0, "from": copy.deepcopy(HKG), "to": {"kind": "country", "id": "CHN"},
                   "tokens": {"from_at": 8.4, "n": 1}}) == []


def test_an_unknown_place_is_refused_by_name_and_the_message_names_the_known_ones():
    errs = errors(light({"kind": "place", "id": "ATLANTIS"}))
    assert len(errs) == 1 and "'ATLANTIS' is not a place" in errs[0], errs
    assert "HKG" in errs[0] and "SGP" in errs[0] and "build_map_places.py" in errs[0], errs
    for bad in ({"kind": "place"}, {"kind": "place", "id": 7}, {"kind": "place", "id": "hkg"}):
        assert errors(light(bad)), bad
    arc = {"kind": "arc", "at": 5.0, "dur": 12.0, "from": {"kind": "country", "id": "USA"}, "to": {"kind": "place", "id": "XXX"}}
    assert any("arc: to place 'XXX' is not a place" in e for e in errors(arc)), errors(arc)


def test_a_typed_point_on_a_place_is_refused_unless_it_is_the_gazetteers(places):
    hk = places["places"]["HKG"]
    errs = errors(light({"kind": "place", "id": "HKG", "x": 820, "y": 188}))
    assert any("the gazetteer's" in e and "mappoint" in e for e in errs), errs
    assert errors(light({"kind": "place", "id": "HKG", "x": hk["x"], "y": hk["y"]})) == [], "a resolved target re-validates clean"


def test_a_place_label_is_the_gazetteers_by_default_and_may_be_rewritten_as_a_word():
    assert errors(light({"kind": "place", "id": "HKG", "label": "HONG KONG"})) == []
    for bad in ("", "   ", 7, None):
        assert any("label" in e for e in errors(light({"kind": "place", "id": "HKG", "label": bad}))), bad


def test_the_names_side_is_the_authors_and_mirrors_the_painters():
    for side in B.PLACE_SIDES:
        assert errors(light({"kind": "place", "id": "HKG", "side": side})) == [], side
    assert any("side must be one of right|below|left|above" in e
               for e in errors(light({"kind": "place", "id": "HKG", "side": "sideways"})))
    src = (ROOT / "content" / "video_engine" / "scripts" / "species" / "vecmap.mjs").read_text(encoding="utf-8")
    m = re.search(r"PLACE_SIDES = Object\.freeze\(\[([^\]]*)\]\)", src)
    assert m and tuple(re.findall(r'"(\w+)"', m.group(1))) == B.PLACE_SIDES, "the compiler and the painter agree on the sides"


def test_a_mappoint_still_cannot_light_and_a_place_is_a_map_target_only():
    errs = errors(light({"kind": "mappoint", "x": 640, "y": 168}))
    assert errs == ["light: target kind 'mappoint' not allowed (takes country|place)"], errs
    spot = {"kind": "spotlight", "at": 5.0, "dur": 3.0, "target": copy.deepcopy(HKG)}
    assert any("not allowed" in e for e in B.validate_species([spot], (0, 0, 0), "plate-plain")), "a place is the map's"


# ---------------------------------------------------------------- the resolution the player reads
def test_the_compiler_writes_the_point_and_the_label_onto_every_place_target(places):
    hk, sg = places["places"]["HKG"], places["places"]["SGP"]
    row = [light(ping=True),
           {"kind": "arc", "at": 5.0, "dur": 12.0, "from": {"kind": "country", "id": "USA"}, "to": {"kind": "place", "id": "SGP"}},
           light({"kind": "place", "id": "SGP", "label": "SINGAPORE"}),
           {"kind": "light", "at": 4.0, "dur": 8.0, "target": {"kind": "country", "id": "USA"}}]
    before_country = copy.deepcopy(row[3])
    B.resolve_place_targets(row)
    assert row[0]["target"] == {"kind": "place", "id": "HKG", "x": hk["x"], "y": hk["y"], "label": "Hong Kong"}
    assert row[1]["to"] == {"kind": "place", "id": "SGP", "x": sg["x"], "y": sg["y"], "label": "Singapore"}
    assert row[2]["target"]["label"] == "SINGAPORE", "an authored label is the author's"
    assert row[3] == before_country, "a country target is untouched"
    again = copy.deepcopy(row)
    B.resolve_place_targets(again)
    assert again == row, "resolution is idempotent"
    assert errors(*row) == [], "and the resolved row re-validates clean"


class _PastThePlaces(Exception):
    """Raised once the row loop has resolved the row's places - the test needs nothing after."""


def test_a_vecmap_row_resolves_its_places_in_the_compilers_own_row_loop(tmp_path, monkeypatch):
    """main() on a one-row bed (test_ledger_panels._row_path's door): the row validates, and the loop - not the author, not
    the player - writes Hong Kong's point and label onto the light's target and the arc's end, beside the embeds."""
    ep, build = tmp_path / "ep", tmp_path / "ep" / "build"
    (build / "audio").mkdir(parents=True)
    (build / "audio/episode.mp3").write_bytes(b"")
    (build / "timeline.json").write_text(json.dumps({"runtime_s": 30.0, "words": []}), encoding="utf-8")
    (build / "caption-pages.json").write_text("[]", encoding="utf-8")
    species = [{"kind": "arc", "at": 5.0, "dur": 12.0, "from": {"kind": "country", "id": "USA"}, "to": {"kind": "place", "id": "HKG"}},
               light(ping=True)]
    (ep / "SHOT-ROW-PATH.py").write_text("W = " + repr([(0.0, 30.0, PLATE, (0, 0, 0), [], None, species)]) + "\n", encoding="utf-8")
    seen: dict = {}
    real = B.resolve_place_targets

    def stop(row_species):
        real(row_species)
        seen["species"] = row_species
        raise _PastThePlaces

    for name, value in (("BUILD", build), ("EP", ep), ("SHOT_TABLE_FILE", "SHOT-ROW-PATH.py"), ("ASPECT", "16:9"),
                        ("resolve_place_targets", stop)):
        monkeypatch.setattr(B, name, value)
    with pytest.raises(_PastThePlaces):
        B.main()
    hk = B.map_places()["HKG"]
    arc, lit = seen["species"]
    assert arc["to"]["x"] == hk["x"] and arc["to"]["label"] == "Hong Kong"
    assert (lit["target"]["x"], lit["target"]["y"], lit["target"]["label"]) == (hk["x"], hk["y"], "Hong Kong")


def test_resolution_refuses_an_unknown_place_by_name():
    with pytest.raises(ValueError, match="'NOWHERE' is not a place"):
        B.resolve_place_targets([light({"kind": "place", "id": "NOWHERE"})])


def test_the_painter_module_pins_its_place_law():
    r = subprocess.run(["node", "--test", NODE_TEST], cwd=ROOT, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-2000:]


def test_the_engine_carries_the_module_as_synced():
    engine = (ROOT / "docs" / "content-video-engine" / "samples" / "scene-evidence-engine.mjs").read_text(encoding="utf-8")
    assert "paintPlaceLight" in engine and "PLACE = Object.freeze" in engine


def test_the_look_is_the_painters_inline_and_the_template_names_none_of_it():
    """The dot and the name carry their look inline (the ping's practice, pingStyle), so the reviewed shell is untouched and
    a build with no place compiles to the same player.html; the light's ink is the template's own --sunflower."""
    tpl = (ROOT / "docs" / "content-video-engine" / "samples" / "scene-evidence-player.template.html").read_text(encoding="utf-8")
    assert "vmplace" not in tpl and "vmplabel" not in tpl
    assert "--sunflower: #F5B72E" in tpl
    src = (ROOT / "content" / "video_engine" / "scripts" / "species" / "vecmap.mjs").read_text(encoding="utf-8")
    assert '"fill:var(--sunflower);"' in src and "fill:var(--sunflower);paint-order:stroke;" in src


# ---------------------------------------------------------------- the golden
def test_the_transshipment_golden_is_built_through_the_compilers_own_route():
    import build_golden_sources as G
    tl, uris = G.SURFACES["vecmap-transship"]()
    sc = tl["scenes"][0]
    assert sc["world"]["focus"] == ["USA", "CHN"] and sc["world"].get("fit") == "tight"
    hk = [s for s in sc["species"] if s["kind"] == "light" and s["target"]["kind"] == "place"]
    assert len(hk) == 1 and hk[0]["target"]["id"] == "HKG" and hk[0]["ping"] is True
    assert "x" in hk[0]["target"] and hk[0]["target"]["label"] == "Hong Kong", "resolved by the compiler, not typed"
    arcs = [s for s in sc["species"] if s["kind"] == "arc"]
    assert [(a["from"].get("id"), a["to"].get("id")) for a in arcs] == [("USA", "HKG"), ("HKG", "CHN")]
    assert hk[0]["at"] == arcs[0]["at"] + B.VECMAP_ARC_DRAW_S, "Hong Kong lights on the word the route lands on it"
    assert B.MAP_PREFIX + "world-110m" in uris
    assert tl.get("aspect") in (None, "16:9")


def test_the_singapore_golden_lights_and_pings_singapore():
    import build_golden_sources as G
    tl, _ = G.SURFACES["vecmap-place-singapore"]()
    sp = [s for s in tl["scenes"][0]["species"] if s["kind"] == "light" and s["target"].get("id") == "SGP"]
    assert len(sp) == 1 and sp[0]["ping"] is True and sp[0]["target"]["label"] == "Singapore"


def test_the_goldens_are_registered():
    src = (ROOT / "content" / "video_engine" / "tests" / "test_golden_frames.py").read_text(encoding="utf-8")
    assert '"vecmap-transship"' in src and '"vecmap-place-singapore"' in src
