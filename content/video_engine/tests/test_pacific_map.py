"""P73 T6 (R26-406) - A PACIFIC-CENTRED MAP: `;meridian=<deg>` on a vector map.

The world map on disk is Natural Earth 1:110m already projected on a 1000 x 500 equirectangular box centred on
Greenwich and cut at +-180, so a United States -> Hong Kong arc crossed the Atlantic and Europe, not the Pacific the
shipment crosses. `vecmap[:<A3 list>];meridian=150` re-centres the projection on 150 E: ONE FORMULA in map units
(`build_world_map.recentre_x`, x' = wrap(x - xm + W/2), xm the meridian's own x - `project(lon - m)` to the bit) moves
the world's rings, its centroids, the gazetteer's places and a typed mappoint alike; every ring the NEW seam cuts is
split into one ring at each edge (no polygon streaks across the frame), and the rings Natural Earth cut at the OLD seam
(+-180: Russia's Chukotka, Fiji, Antarctica) are JOINED back along it, so no hairline runs through the middle of a
Pacific map. The compiler ships the re-centred world once under its own key (`map:world-110m@150`); the player's world
branch reads it as it always read `map:world-110m`, and its one new line (`vmRecentreX`) moves the points the asset
does not carry. No option (or `meridian=0`): the world, the key and every frame are what they were.
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
import build_world_map as WM  # noqa: E402

MAPS = ROOT / "content" / "video_engine" / "assets" / "maps"
WORLD_PATH = MAPS / "world-110m.paths.json"
NODE_TEST = "content/video_engine/tests/kinetics/vecmap_meridian.test.mjs"
PACIFIC = "vecmap:USA,CHN;meridian=150;fit=tight"
PATH_RE = re.compile(r"^M -?[\d.]+ -?[\d.]+( L -?[\d.]+ -?[\d.]+)+ Z$")
MERIDIANS = (150, -90, 180, -180, 90, 30, -150, 10, 120.5)


@pytest.fixture(scope="module")
def world() -> dict:
    return json.loads(WORLD_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def pacific(world) -> dict:
    return WM.recentre(world, 150)


def rings_of(country: dict) -> list[list[tuple[float, float]]]:
    return [WM.parse_path(d) for d in country["paths"]]



# ---------------------------------------------------------------- the one formula
def test_the_formula_is_the_identity_at_greenwich():
    for x in (0.0, 0.001, 123.456, 500.0, 817.175, 999.999, 1000.0):
        assert WM.recentre_x(x, 0) == x
    for lon, lat in ((114.183064, 22.306927), (-98.5, 39.8), (180.0, -90.0), (-180.0, 90.0)):
        assert WM.project(lon, lat, 0) == WM.project(lon, lat)


def test_meridian_150_puts_150_east_in_the_middle_and_the_seam_at_30_west():
    assert WM.project(150.0, 0.0, 150)[0] == 500.0
    assert WM.project(-29.999, 0.0, 150)[0] == pytest.approx(0.003, abs=1e-3)   # just east of the seam: the left edge
    assert WM.project(-30.001, 0.0, 150)[0] == pytest.approx(999.997, abs=1e-3)  # just west of it: the right edge
    assert WM.project(180.0, 0.0, 150)[0] == pytest.approx(583.333, abs=1e-3)   # the OLD seam, now inside the frame
    assert WM.project(-98.5, 39.8, 150)[1] == WM.project(-98.5, 39.8)[1], "a meridian moves x, never y"


def test_the_places_go_through_the_same_formula_as_the_rings():
    places = json.loads((MAPS / "places.json").read_text(encoding="utf-8"))["places"]
    for m in MERIDIANS:
        for p in places.values():
            x, y = WM.project(p["lon"], p["lat"], m)
            assert y == p["y"]
            assert x == pytest.approx(WM.recentre_x(p["x"], m), abs=1e-3)
            assert x == pytest.approx(((p["lon"] - m + 180.0) % 360.0) / 360.0 * 1000.0, abs=1.5e-3), (m, p["label"])
    # Hong Kong on the Pacific map: 114.18 E is 35.8 deg west of the centre - the value the node test pins too
    assert WM.recentre_x(places["HKG"]["x"], 150) == pytest.approx(400.508, abs=1e-3)


def test_an_out_of_range_meridian_is_refused_by_the_formula():
    for bad in (180.5, -181, 360, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="meridian"):
            WM.recentre_x(10.0, bad)


# ---------------------------------------------------------------- the re-centred world
def test_greenwich_is_the_document_itself(world):
    assert WM.recentre(world, 0) is world
    assert "meridian" not in world, "the file on disk carries no meridian: the player reads that as Greenwich"


def test_the_recentred_world_keeps_the_files_contract(world, pacific):
    assert pacific["box"] == world["box"] and pacific["meridian"] == 150
    assert set(pacific["countries"]) == set(world["countries"])
    assert world == json.loads(WORLD_PATH.read_text(encoding="utf-8")), "the file's own document is never mutated"
    for cid, c in pacific["countries"].items():
        assert c["name"] == world["countries"][cid]["name"]
        assert c["paths"] and all(PATH_RE.match(d) for d in c["paths"]), cid
        assert len(c["centroid"]) == 2 and len(c["bbox"]) == 4


def test_no_ring_streaks_across_the_frame_at_any_meridian(world):
    """A streak is an edge that jumps the frame: every ring of every re-centred world lies inside the box, and no edge
    runs more than half the box across - except along the map's own top or bottom border (Antarctica's pole edge)."""
    W, H = world["box"]
    for m in MERIDIANS:
        doc = WM.recentre(world, m)
        for cid, c in doc["countries"].items():
            for ring in rings_of(c):
                assert all(0.0 <= x <= W and 0.0 <= y <= H for x, y in ring), (m, cid)
                for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
                    border = y0 == y1 and y0 in (0.0, float(H))
                    assert border or abs(x1 - x0) <= W / 2, f"meridian {m}: {cid} streaks ({x0},{y0})->({x1},{y1})"


def test_every_country_keeps_its_area_at_every_meridian(world):
    """Nothing is lost or doubled by the cut and the join: each country's summed ring area is the file's."""
    for m in MERIDIANS:
        doc = WM.recentre(world, m)
        for cid, c in world["countries"].items():
            a0 = sum(abs(WM.ring_area(r)) for r in rings_of(c))
            a1 = sum(abs(WM.ring_area(r)) for r in rings_of(doc["countries"][cid]))
            assert a1 == pytest.approx(a0, rel=1e-4, abs=1e-3), (m, cid)


def test_the_seam_at_30_west_cuts_greenland_and_antarctica_and_nothing_else(world, pacific):
    assert pacific["seam"]["lon"] == -30.0
    assert pacific["seam"]["split"] == ["ATA", "GRL"]
    grl = pacific["countries"]["GRL"]
    assert grl["bbox"][0] == 0.0 and grl["bbox"][2] == 1000.0, "Greenland's halves stand at the two edges"
    left = [r for r in rings_of(grl) if max(x for x, _ in r) < 500]
    right = [r for r in rings_of(grl) if min(x for x, _ in r) > 500]
    assert left and right and len(left) + len(right) == len(grl["paths"])


def test_the_old_seam_is_joined_so_russia_is_one_shape_across_180(world, pacific):
    """Natural Earth cut Russia at 180 twice (Chukotka on the far left of the file, the mainland on the far right; Wrangel
    Island's two halves). On a Pacific map 180 is inside the frame: each pair is joined along it - two rings fewer, and
    no edge left lying on it."""
    seam = WM.recentre_x(0.0, 150)   # the old +-180, where it now stands
    assert seam == pytest.approx(583.333, abs=1e-3)
    assert pacific["seam"]["joined"] == ["ATA", "FJI", "RUS"]
    for cid in ("RUS", "FJI", "ATA"):
        c = pacific["countries"][cid]
        on_line = [((x0, y0), (x1, y1)) for r in rings_of(c) for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1])
                   if x0 == x1 == seam]
        assert on_line == [], f"{cid}: a hairline on the old seam {on_line[:2]}"
    assert len(pacific["countries"]["RUS"]["paths"]) == len(world["countries"]["RUS"]["paths"]) - 2
    assert len(pacific["countries"]["FJI"]["paths"]) == len(world["countries"]["FJI"]["paths"]) - 1
    rus = pacific["countries"]["RUS"]["bbox"]
    assert rus[2] - rus[0] < 500, "Russia is one compact shape on the Pacific map, not a strip across the world"


def test_a_centroid_is_the_point_recentred_and_the_bbox_holds_the_rings(world, pacific):
    for cid, c in pacific["countries"].items():
        c0 = world["countries"][cid]["centroid"]
        assert c["centroid"] == [WM.recentre_x(c0[0], 150), c0[1]], cid
        pts = [p for r in rings_of(c) for p in r]
        assert c["bbox"] == [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]


def test_the_pacific_route_is_short_and_the_greenwich_one_long(world, pacific):
    """The United States and China: 307 deg apart the Greenwich way (the box runs Alaska to Beijing across Europe), and
    much less on the Pacific map - the fit=tight focus box shrinks with it."""
    def span(doc):
        b = [doc["countries"][c]["bbox"] for c in ("USA", "CHN")]
        return max(x[2] for x in b) - min(x[0] for x in b)
    assert span(world) > 800 and span(pacific) < 650


# ---------------------------------------------------------------- the grammar
def test_meridian_is_a_vector_map_plate_option():
    assert "meridian" in B.PLATE_OPTS
    w = B.world_for_plate(PACIFIC, (0, 0, 0), None)
    assert w["meridian"] == 150 and w["map"] == "world-110m@150" and w["fit"] == "tight" and w["focus"] == ["USA", "CHN"]
    assert B.world_for_plate("vecmap;meridian=-90.5", (0, 0, 0), None)["map"] == "world-110m@-90.5"


def test_no_option_and_meridian_zero_are_the_map_that_was():
    base = B.world_for_plate("vecmap:USA,CHN;fit=tight", (0, 0, 0), None)
    assert "meridian" not in base and base["map"] == B.WORLD_MAP
    assert B.world_for_plate("vecmap:USA,CHN;fit=tight;meridian=0", (0, 0, 0), None) == base
    raw = json.dumps(json.loads(WORLD_PATH.read_text(encoding="utf-8")), separators=(",", ":"))
    assert B.world_map_json() == raw == B.world_map_json(B.WORLD_MAP), "the Greenwich asset is the file's bytes"


@pytest.mark.parametrize("bad", ["181", "-180.01", "360", "east", "", "nan", "inf", "1e3", "150deg"])
def test_a_meridian_that_is_not_a_longitude_is_refused_by_name(bad):
    with pytest.raises(ValueError, match=r"meridian .*-180\.\.180"):
        B.world_for_plate(f"vecmap:USA,CHN;meridian={bad}", (0, 0, 0), None)


def test_a_meridian_off_a_vector_map_is_refused_by_name():
    import build_golden_sources as G
    with pytest.raises(ValueError, match="meridian=150 is a VECTOR MAP option"):
        B.world_for_plate(G.LIT_PLATE + ";meridian=150", (0, 0, 0), G.LIT_PROJECT)


def test_the_build_ships_the_recentred_world_under_its_own_key():
    doc = json.loads(B.world_map_json("world-110m@150"))
    assert doc["meridian"] == 150 and doc["seam"]["split"] == ["ATA", "GRL"]
    assert B.world_map("world-110m@150") is B.world_map("world-110m@150"), "built once per build"
    with pytest.raises(ValueError, match="meridian"):
        B.world_map("world-110m@200")


# ---------------------------------------------------------------- the findings (s106: WARN, never refuse)
def _arc(frm, to):
    return {"kind": "arc", "at": 5.0, "dur": 12.0, "from": frm, "to": to}


USA, CHN, HKG = {"kind": "country", "id": "USA"}, {"kind": "country", "id": "CHN"}, {"kind": "place", "id": "HKG"}


def test_an_arc_that_goes_the_long_way_warns_with_the_meridian_that_carries_it_short():
    greenwich = B.world_for_plate("vecmap:USA,CHN;fit=tight", (0, 0, 0), None)
    warns = B.vecmap_seam_warns(greenwich, [_arc(USA, HKG)])
    assert len(warns) == 1 and "LONG way" in warns[0] and "meridian=" in warns[0], warns
    m = int(re.search(r"meridian=(-?\d+)", warns[0]).group(1))
    fixed = B.world_for_plate(f"vecmap:USA,CHN;fit=tight;meridian={m}", (0, 0, 0), None)
    assert B.vecmap_seam_warns(fixed, [_arc(USA, HKG)]) == [], "the meridian it names carries the arc the short way"
    pacific = B.world_for_plate(PACIFIC, (0, 0, 0), None)
    assert B.vecmap_seam_warns(pacific, [_arc(USA, HKG), _arc(HKG, CHN)]) == []


def test_a_focus_country_the_seam_cuts_warns():
    warns = B.vecmap_seam_warns(B.world_for_plate("vecmap:GRL;meridian=150", (0, 0, 0), None), [])
    assert len(warns) == 1 and "GRL" in warns[0] and "cuts" in warns[0], warns
    assert B.vecmap_seam_warns(B.world_for_plate("vecmap:RUS;meridian=150", (0, 0, 0), None), []) == [], \
        "Russia is joined on the Pacific map, not cut"


def test_the_row_loop_ships_the_recentred_key_and_prints_the_findings(tmp_path, monkeypatch, capsys):
    """main() on a one-row bed (test_map_places' door): the loop asks for the row's own map key and prints the finding."""
    class _Past(Exception):
        pass
    ep, build = tmp_path / "ep", tmp_path / "ep" / "build"
    (build / "audio").mkdir(parents=True)
    (build / "audio/episode.mp3").write_bytes(b"")
    (build / "timeline.json").write_text(json.dumps({"runtime_s": 30.0, "words": []}), encoding="utf-8")
    (build / "caption-pages.json").write_text("[]", encoding="utf-8")
    species = [_arc(copy.deepcopy(USA), copy.deepcopy(HKG))]
    plate = "vecmap:USA,CHN;meridian=-30"   # the Atlantic map: the Pacific route is the long way round on it
    (ep / "SHOT-ROW-PATH.py").write_text("W = " + repr([(0.0, 30.0, plate, (0, 0, 0), [], None, species)]) + "\n",
                                         encoding="utf-8")
    keys: list = []
    real_json = B.world_map_json

    def record(name=B.WORLD_MAP):
        keys.append(name)
        return real_json(name)

    def stop(row_species):
        raise _Past

    for name, value in (("BUILD", build), ("EP", ep), ("SHOT_TABLE_FILE", "SHOT-ROW-PATH.py"), ("ASPECT", "16:9"),
                        ("world_map_json", record), ("resolve_place_targets", stop)):
        monkeypatch.setattr(B, name, value)
    with pytest.raises(_Past):
        B.main()
    assert keys == ["world-110m@-30"]
    out = capsys.readouterr().out
    assert "[WARN] P73 T6" in out and "LONG way" in out, out[-2000:]


# ---------------------------------------------------------------- the player and the goldens
def test_the_node_tests_pass():
    r = subprocess.run(["node", "--test", NODE_TEST], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-2000:]


def test_the_engine_carries_the_recentring_line():
    eng = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")
    assert "vmRecentreX" in eng, "sync_kinetics.py copies species/vecmap.mjs into the engine"


def test_the_goldens_are_registered():
    import build_golden_sources as G
    src = (ROOT / "content/video_engine/tests/test_golden_frames.py").read_text(encoding="utf-8")
    for name in ("vecmap-pacific", "vecmap-seam-split"):
        assert name in G.SURFACES and name in G.FRAME_T and f'"{name}"' in src
    tl, uris = G.SURFACES["vecmap-pacific"]()
    world = tl["scenes"][0]["world"]
    assert world["map"] == "world-110m@150" and "map:world-110m@150" in uris and "map:world-110m" not in uris
    tl2, uris2 = G.SURFACES["vecmap-seam-split"]()
    assert json.loads(uris2["map:" + tl2["scenes"][0]["world"]["map"]])["seam"]["split"]
