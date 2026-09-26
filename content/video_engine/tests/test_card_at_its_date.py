"""P71 T23 - a card joins its date on the line (was P69 T67; harvest v2 A19, R4).

The Bravos form, measured first (E38): STK 8:07 parks a chip BESIDE the latest peak with an arced leader whose arrowhead
lands on the peak; BOOM 00:45 (VERIFY.md A19) reads the card in the plot's EMPTY upper-right with a dashed ring on the
datum and a short straight leader from the card to the ring. "A headline belongs to one date on the line, and the join
IS the claim" (BRAVOS-USE-WHEN A19).

`park_at: {datum, series?, side?}` on a held CARD dock:
- the card READS in the plot's empty room at the date's side (E65's own `read_in_room`, read and never edited: the room
  that holds the park), hovering when the author names `under: "hover"` (s124 amended: the author's);
- then PARKS to a chip at its datum - E45's floor width (`DOCK_ON_PAGE_MIN_W`) beside the datum, the side and anchor the
  compiler found clear of the data's ink and the page's words (the author's `side` wins, s106) - the park target is the
  datum's LIVE position (the engine's `resolveTarget`, so it follows a rescale);
- and a leader draws from the chip to a ring on the datum, on the chart's layer (#species-under: a mark on a datum
  paints beneath the docks, E49 amended 2026-09-08).
Over the ink only by the author's `under` + `read` (s124 (3)); M25 / M27 report that as a WARN with its numbers (T15).
Byte-identical absent the key.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
COMPILER = ROOT / "content/video_engine/scripts/build_scene_timeline_f.py"
CARDS = ROOT / "content/video_engine/effects/cards/dock_option.json"
RECIPE = ROOT / "content/video_engine/effects/recipes/the-proof-walk.json"
STEEL = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
RAILWAY = "ledger:ev-railway-index-v1:line:139:right;idle=live"   # Steel and Paper H row 5 / 9's own page
PEAK, TROUGH = 53, 139
ASPECT = "16:9"


@pytest.fixture(scope="module")
def railway() -> dict:
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        world = B.world_for_plate(RAILWAY, (0, 0, 0), STEEL)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


# ------------------------------------------------------------------ the option (refused by name, common rule (h))
def test_park_at_is_a_dock_option_naming_a_datum():
    assert "park_at" in B.DOCK_OPTS
    assert B.PARK_AT_KEYS == ("datum", "series", "side", "anchor") and B.PARK_AT_SIDES == ("right", "left", "above", "below")
    assert B.dock_opts({"park_at": {"datum": PEAK}})["park_at"] == {"datum": PEAK}
    got = B.dock_opts({"park_at": {"datum": PEAK, "series": 0, "side": "left", "anchor": 0.5}, "read": {"centre_w": 0.4},
                       "under": "hover"})
    assert got["park_at"] == {"datum": PEAK, "series": 0, "side": "left", "anchor": 0.5}, "read and under ride beside it (no centre)"


@pytest.mark.parametrize("bad", [53, "53", None, [], {}, {"series": 0}, {"datum": -1}, {"datum": True}, {"datum": 5.5},
                                 {"datum": 3, "series": -1}, {"datum": 3, "series": "0"}, {"datum": 3, "side": "up"},
                                 {"datum": 3, "at": 4.0}, {"datum": 3, "anchor": 1.5}, {"datum": 3, "anchor": "top"},
                                 {"datum": 3, "anchor": True}])
def test_a_malformed_park_at_is_refused_by_name(bad):
    with pytest.raises(ValueError, match=r"^dock: park_at") as e:
        B.dock_opts({"park_at": bad})
    assert "is not one of arrive" not in str(e.value), "refused BY NAME, not as an unknown key"


@pytest.mark.parametrize("other", [{"prop": True}, {"arrive": "stamp"}, {"cutout": True}, {"press": {"source": "s", "phrase": {}}},
                                   {"embed": "tv"}, {"centre": True}, {"centre_x": 0.5}, {"centre_y": 0.5},
                                   {"centre_w": 0.3}, {"centre_band": "top"}, {"moves": [{"at": 1, "x": 0.5}]}])
def test_park_at_is_a_held_cards_and_is_refused_by_name_beside_another_park(other):
    with pytest.raises(ValueError, match=r"park_at.*cannot be combined|cannot be combined.*park_at"):
        B.dock_opts(dict({"park_at": {"datum": PEAK}}, **other))


def test_a_dock_that_names_no_park_at_is_the_entry_it_always_was():
    plain = B.dock_entry("ev-a", 0, 4.0, 14.0, 0, B.DOCK_KIND_IMAGE, {"x": 10, "y": 20, "w": 300, "h": 180})
    assert "park_at" not in plain
    assert plain == B.dock_entry("ev-a", 0, 4.0, 14.0, 0, B.DOCK_KIND_IMAGE, {"x": 10, "y": 20, "w": 300, "h": 180}, park_at=None)
    joined = B.dock_entry("ev-a", 0, 4.0, 14.0, 0, B.DOCK_KIND_IMAGE, {"x": 10, "y": 20, "w": 300, "h": 180},
                          park_at={"datum": PEAK, "series": 0, "side": "right", "anchor": 0.44})
    assert joined["park_at"] == {"datum": PEAK, "series": 0, "side": "right", "anchor": 0.44}
    assert {k: v for k, v in joined.items() if k != "park_at"} == plain


# ------------------------------------------------------------------ the chip at its datum (the compiler's estimate)
def test_the_chip_parks_beside_its_datum_clear_of_the_ink_and_the_words(railway):
    pk = B.park_at_place(railway, {"datum": 20}, ASPECT, 0.6657)   # a date on the rise with room round it
    X, Y = pk["datum"]
    assert pk["w"] == B.DOCK_ON_PAGE_MIN_W and pk["h"] == round(B.DOCK_ON_PAGE_MIN_W * 0.6657), "E45's floor: a chip still evidence"
    assert pk["side"] in B.PARK_AT_SIDES and pk["notes"] == [] and pk["room"] == "empty", pk
    assert pk == dict(pk, **B.park_at_box(pk["side"], pk["ay"], X, Y, pk["w"], pk["h"])), "the engine's own geometry, mirrored"
    near = {"right": pk["x"] - X, "left": X - pk["x"] - pk["w"], "above": Y - pk["y"] - pk["h"], "below": pk["y"] - Y}[pk["side"]]
    assert abs(near - B.PARK_AT_GAP_PX) <= 1, "the chip's near edge is the leader's length off the datum"
    boxes = B.LPG.page_boxes(railway["page"], ASPECT)
    assert B.mask_is_clear(boxes, pk), "the chip touches no cell of the data's ink (E65)"
    words = B.page_text_boxes(railway["page"], ASPECT) + B.park_at_rule_boxes(railway["page"], ASPECT)
    assert not [n for n, r in words if B._overlap_area(pk, r) > 0]
    plot = boxes["plot"]
    assert plot["x"] <= X <= plot["x"] + plot["w"] and plot["y"] <= Y <= plot["y"] + plot["h"], "the datum is on the plot"


def test_the_datum_estimate_sits_on_the_lines_ink(railway):
    """The estimate (the mask-calibrated scale) puts the peak at the top of the rise and the trough at the foot of the fall,
    each inside the mask's inked rows - the engine rings the LIVE datum; this chooses where the chip goes."""
    boxes = B.LPG.page_boxes(railway["page"], ASPECT)
    mask, plot = boxes["data_mask"], boxes["plot"]
    ch = plot["h"] / len(mask)
    rows = [r for r, line in enumerate(mask) if "1" in line]
    (_x0, y_peak), (_x1, y_trough) = B.park_at_datum_px(railway["page"], 0, PEAK, ASPECT), B.park_at_datum_px(railway["page"], 0, TROUGH, ASPECT)
    assert plot["y"] + rows[0] * ch <= y_peak <= plot["y"] + (rows[0] + 1) * ch
    assert plot["y"] + rows[-1] * ch <= y_trough <= plot["y"] + (rows[-1] + 1) * ch
    rule = B.park_at_rule_boxes(railway["page"], ASPECT)
    assert [n for n, _r in rule] == ["the rule label '1843 level'"] and y_peak < rule[0][1]["y"] < y_trough


def test_the_authors_side_is_honoured_and_a_crowded_one_is_reported_with_its_numbers(railway):
    pk = B.park_at_place(railway, {"datum": TROUGH, "side": "right"}, ASPECT, 0.6657)
    assert pk["side"] == "right" and pk["room"] == "overlap", "s106: where the chip sits is the author's"
    assert pk["notes"] and "px^2" in pk["notes"][0] and "s106" in pk["notes"][0], pk
    free = B.park_at_place(railway, {"datum": TROUGH}, ASPECT, 0.6657)
    assert free["side"] == "above" and free["notes"] == [], free   # the last datum's right is the end tag, its left the fall
    assert abs(free["y"] + free["h"] + B.PARK_AT_GAP_PX - free["datum"][1]) <= 1, "above: the chip's foot the leader's length up"


@pytest.mark.parametrize("pa, word", [({"datum": 140}, "last datum"), ({"datum": 3, "series": 1}, "series")])
def test_a_date_the_chart_does_not_have_is_refused_by_name(railway, pa, word):
    with pytest.raises(ValueError, match=rf"park_at.*{word}"):
        B.park_at_place(railway, pa, ASPECT, 0.57)


def test_a_picture_plate_has_no_date_to_join():
    with pytest.raises(ValueError, match=r"park_at.*ledger page"):
        B.park_at_place({"asset_id": "plate-x"}, {"datum": 3}, ASPECT, 0.57)


# ------------------------------------------------------------------ the read in the plot's empty room (E65's placer, READ)
def test_the_read_takes_the_plots_empty_room_that_holds_the_chip(railway):
    pk = B.park_at_place(railway, {"datum": PEAK}, ASPECT, 0.57)
    solo = B.dock_read_box(ASPECT, None, 0.57)
    got, note = B.park_at_read(railway, pk, solo, ASPECT, 0.57, {}, {})
    rd = got["read_place"]
    boxes = B.LPG.page_boxes(railway["page"], ASPECT)
    assert rd == B.read_in_room(boxes, pk, solo, ASPECT, 0.57, [r for _n, r in B.page_text_boxes(railway["page"], ASPECT)]), \
        "the read IS E65's own read_in_room with the chip as its park - read, never re-placed"
    assert B.mask_is_clear(boxes, rd) and rd["w"] > pk["w"] and note is None
    assert "P71 T23" in got["read_moved"]["why"] and "E65" in got["read_moved"]["why"]
    assert B._overlap_share(rd, boxes["plot"]) > B.READ_OVER_PLOT_SHARE, "it reads ON the plot - in its empty room"


def test_an_authored_read_over_the_ink_with_under_stands(railway):
    pk = B.park_at_place(railway, {"datum": PEAK}, ASPECT, 0.6657)
    e63 = {"read_place": {"x": 1, "y": 2, "w": 3, "h": 4}}
    got, note = B.park_at_read(railway, pk, {"x": 300, "y": 300, "w": 600, "h": 342}, ASPECT, 0.6657, e63,
                               {"under": "blur", "read": {"centre_w": 0.3}})
    assert got is e63 and note is None, "s124 (3): a dock that names under and its read keeps them (T15)"


def test_no_room_for_the_read_falls_back_to_today_and_says_so():
    page = {"builder": "dense-line"}   # nothing measured: no mask, no room
    got, note = B.park_at_read({"kind": "ledger", "page": page}, {"x": 0, "y": 0, "w": 240, "h": 137}, {"x": 0, "y": 0, "w": 800, "h": 456},
                               ASPECT, 0.57, {"read_deferred": True}, {})
    assert got == {"read_deferred": True} and "empty room" in note and "under" in note and "s124" in note


def test_the_main_loop_places_the_chip_reads_the_room_and_writes_the_entry():
    src = COMPILER.read_text(encoding="utf-8")
    assert re.search(r"_pk = park_at_place\(world, dopt\[\"park_at\"\], ASPECT", src), "the row resolves its datum"
    i_e63 = src.index('e63 = read_over_build(')
    i_pk = src.index("e63, _pkn = park_at_read(")
    assert i_pk > i_e63, "the room read follows E63's decision and overrides it"
    assert re.search(r"docks\.append\(dock_entry\([^;]*?park_at=", src, re.S), "the entry carries the join"


# ------------------------------------------------------------------ the engine
def test_the_park_target_is_the_compiled_chip_moved_by_its_datums_travel():
    src = ENGINE.read_text(encoding="utf-8")
    geom = src[src.index("const dockGeom = (el, d, t) =>"):]
    geom = geom[:geom.index("};") + 2]
    assert "dockParkBox(d, d.place)" in geom, "dockGeom parks a joined card at its chip"
    box = src[src.index("const dockParkBox = (d, P) =>"):]
    box = box[:box.index("};") + 2]
    assert "P.x + m.now[0] - m.home[0]" in box and "P.y + m.now[1] - m.home[1]" in box, \
        "the chip IS its compiled place on the page as built, and travels with its datum (M25 reads it at its place)"
    pts = src[src.index("const dockParkAtPts = (d) =>"):]
    pts = pts[:pts.index("\n  };") + 5]
    assert "lpDatumNow(st, pk.series | 0, pk.datum | 0)" in pts, "now: the resolver's own datum law, lerped across a rescale"
    assert "lpMarkDatumOn((st.states && st.states[0]) || st" in pts, "home: the datum on the page's first chart state"
    m = re.search(r"const DOCK_PARK_AT = Object\.freeze\(\{ GAP_PX: (\d+)", src)
    assert m and int(m.group(1)) == B.PARK_AT_GAP_PX, "one dial written twice"


def test_the_join_is_painted_on_the_charts_layer_after_the_species():
    src = ENGINE.read_text(encoding="utf-8")
    assert re.search(r"paintSpecies\(sc, t\);\s*\n\s*paintDockJoins\(live, t\);", src), \
        "paintSpecies clears #species-under every frame: the join is drawn right after it"
    assert re.search(r"const parkSvg = \(tag, at\) => \{[^\n]*return spUnder\.appendChild\(n\); \};", src), \
        "a mark on a datum paints beneath the docks (E49 amended 2026-09-08)"
    body = src[src.index("const paintDockJoins = (live, t) =>"):]
    body = body[:body.index("\n  };") + 5]
    assert body.count("parkSvg(") == 3 and "stageBox(L.el)" in body, \
        "the leader, its head and the ring; the leader meets the chip AS DRAWN (a hover's lift and step included)"


# ------------------------------------------------------------------ the card and the recipe
def test_the_dock_option_card_and_the_proof_walk_recipe():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    c = cards["dock_option:park_at"]
    assert c["token"] == "park_at" and c["proof"]["golden"] == "card-parks-at-its-date" and c["status"] == "draft"
    assert "A19" in json.dumps(c) and "E65" in c["doctrine"]
    r = json.loads(RECIPE.read_text(encoding="utf-8"))
    assert r["id"] == "recipe:the-proof-walk" and r["status"] == "candidate"
    assert any(m["card"] == "dock_option:park_at" for m in r["members"])
    assert {"act", "moment", "shape", "use", "dont"} <= set(r["use_when"]), "common rule (b): its USE-WHEN"


# ------------------------------------------------------------------ the frames (chromium)
def _chromium() -> bool:
    try:
        import served_player as SP
        with SP.browser():
            return True
    except Exception:  # noqa: BLE001 - no browser on this machine: the frame tests skip, never pass
        return False


needs_chromium = pytest.mark.skipif(not _chromium(), reason="chromium not available")

READ_JOIN = """() => {
  const s = document.getElementById('stage').getBoundingClientRect(), k = 1920 / s.width;
  const el = document.getElementById('dock-1'), b = el.getBoundingClientRect();
  const ring = document.querySelector('#species-under .parkring'), lead = document.querySelector('#species-under .parklead');
  const w = [...document.querySelectorAll('.world')].find((e) => e.__lp && e.classList.contains('ledger'));
  const st = w && w.__lp, S = st && ((st.states && st.states[st.active | 0]) || st);
  const q = window.__lpDatum(null, 0, DATUM), svg = S && S.chart;
  let datum = null;
  if (q && svg) { const p = new DOMPoint(q[0], q[1]).matrixTransform(svg.getScreenCTM()); datum = [(p.x - s.left) * k, (p.y - s.top) * k]; }
  return {left: parseFloat(el.style.left), top: parseFloat(el.style.top), width: parseFloat(el.style.width),
          drawn: {x: (b.x - s.left) * k, y: (b.y - s.top) * k, w: b.width * k, h: b.height * k},
          ring: ring ? [+ring.getAttribute('cx'), +ring.getAttribute('cy'), +ring.getAttribute('r')] : null,
          lead: lead ? [+lead.getAttribute('x1'), +lead.getAttribute('y1'), +lead.getAttribute('x2'), +lead.getAttribute('y2')] : null,
          datum};
}"""


def _read(tl: dict, uris: dict, ts: list[float], layers: str = "page,docks") -> list[tuple[bytes, dict]]:
    datum = tl["scenes"][0]["docks"][0]["park_at"]["datum"]
    import render_baseline as RB
    import served_player as SP
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    out = []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "join.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SP.served(html, w, h) as (page, errs):
            if layers:   # the shell's own layer switch (R26-13): the caption is the viewer's layer, not the chart
                page.goto(page.url.split("?")[0] + f"?layers={layers}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
            for t in ts:
                png = RB.frame_png(page, t, (w, h))
                out.append((png, page.evaluate(READ_JOIN.replace("DATUM", str(datum)))))
            assert not errs, errs
    return out


@pytest.fixture(scope="module")
def GS():
    import build_golden_sources as gs
    return gs



@needs_chromium
def test_the_card_reads_in_the_empty_room_then_parks_at_its_date_with_a_leader(GS):
    tl, uris = GS.card_at_date_surface()
    d = tl["scenes"][0]["docks"][0]
    t_read, t_join = GS.FRAME_T["card-reads-in-the-empty-room"], GS.FRAME_T["card-parks-at-its-date"]
    (_p1, r), (_p2, j) = _read(tl, uris, [t_read, t_join])
    rp, pl, pk = d["read_place"], d["place"], d["park_at"]
    assert abs(r["left"] - rp["x"]) < 0.6 and abs(r["top"] - rp["y"]) < 0.6 and abs(r["width"] - rp["w"]) < 0.6, (r, rp)
    assert r["ring"] is None and r["lead"] is None, "no join while the card reads"
    assert j["datum"] and j["ring"], j
    assert abs(j["ring"][0] - j["datum"][0]) < 0.6 and abs(j["ring"][1] - j["datum"][1]) < 0.6, "the ring sits ON the datum"
    assert (j["left"], j["top"], j["width"]) == (pl["x"], pl["y"], pl["w"]), "on the page as built the chip IS its place (M25's box)"
    assert pk["side"] == "right" and abs(j["left"] - j["datum"][0] - B.PARK_AT_GAP_PX) < 20, \
        "right of its datum, the leader's length off it (the estimate within 20 px of the live datum)"
    x1, y1, x2, y2 = j["lead"]
    assert abs(x1 - j["drawn"]["x"]) < 1.0, "the leader leaves the chip AS DRAWN (the hover's lift and step included)"
    assert j["drawn"]["y"] <= y1 <= j["drawn"]["y"] + j["drawn"]["h"]
    assert abs(((x2 - j["ring"][0]) ** 2 + (y2 - j["ring"][1]) ** 2) ** 0.5 - j["ring"][2]) < 1.0, "... and stops at the ring"


@needs_chromium
def test_the_chip_follows_its_datum_across_a_rescale(GS):
    tl, uris = GS.card_at_date_surface(rescale=True, datum=GS.DATE_PEAK)
    before, during, after = (GS.DATE_RESCALE_AT - 0.2, GS.DATE_RESCALE_AT + GS.DATE_RESCALE_S * 0.5,
                             GS.DATE_RESCALE_AT + GS.DATE_RESCALE_S + 0.3)
    b0, mid, b1 = [j for _p, j in _read(tl, uris, [before, during, after])]
    assert abs(b0["datum"][0] - b1["datum"][0]) > 40, "the rescale moves the peak"
    for j in (mid, b1):
        assert abs((j["left"] - b0["left"]) - (j["datum"][0] - b0["datum"][0])) < 0.6, (b0, j)
        assert abs((j["top"] - b0["top"]) - (j["datum"][1] - b0["datum"][1])) < 0.6, (b0, j)
        assert abs(j["ring"][0] - j["datum"][0]) < 0.6 and abs(j["ring"][1] - j["datum"][1]) < 0.6, j


@needs_chromium
def test_the_join_is_pure_in_t(GS):
    tl, uris = GS.card_at_date_surface()
    t1, t2 = GS.FRAME_T["card-parks-at-its-date"], GS.DATE_ENTER + 1.5
    a, _b, c = _read(tl, uris, [t1, t2, t1], layers="")
    assert a[1] == c[1] and a[0] == c[0], "a seek back lands on the same chip, the same leader, the same bits"


def _probe(tl: dict, uris: dict, instants: list[tuple[float, str]]) -> dict:
    import probe as PR
    import render_baseline as RB
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        (b / "t23.timeline.json").write_text(json.dumps(tl), encoding="utf-8")
        (b / "player.html").write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with PR.Probe(b, "t23.timeline.json") as p:
            return PR.probe_doc(b, probe=p, instants=instants)


@needs_chromium
def test_m25_and_m27_pass_the_card_in_the_empty_room_and_at_its_date(GS):
    """The same card and chip with no `under`: the probe reads the card AT its read box and AT its place (a hover lifts
    the card 10 px off both - past the probe's STATE_TOL_PX - which is P71 T15's pose, not this join's). M27: no fault;
    its one line is E65's own tier - "inside the plot's box, clear of the ink". M25: the chip at its date, no fault."""
    tl, uris = GS.card_at_date_surface(under=None)
    doc = _probe(tl, uris, [(GS.FRAME_T["card-reads-in-the-empty-room"], "read"),
                            (GS.FRAME_T["card-parks-at-its-date"], "parked")])
    assert [d["state"] for i in doc["instants"] for d in i["docks"]] == ["reading", "parked"], doc["instants"]
    fails, warns, _n = G._over_build_faults(doc, tl["scenes"])
    assert fails == [] and len(warns) == 1 and "inside the plot's box, clear of the ink" in warns[0], (fails, warns)
    assert G._layout_faults(doc, tl["scenes"]) == ([], []), "M25: the chip at its date is on no ink and no word"
    hits = [o["b"] for i in doc["instants"] for o in i.get("overlaps") or [] if o["a"] == tl["scenes"][0]["docks"][0]["slide"]]
    assert set(hits) <= {"page.plot"}, hits


@needs_chromium
def test_the_same_card_blurring_over_the_ink_blurs_the_plot_and_m27_warns_with_its_numbers(GS):
    tl, uris = GS.card_at_date_surface(under="blur", read=GS.DATE_OVER_INK_READ)
    t = GS.FRAME_T["card-reads-in-the-empty-room"]
    doc = _probe(tl, uris, [(t, "read")])
    fails, warns, _n = G._over_build_faults(doc, tl["scenes"])
    assert fails == [] and any("under: blur" in w and " px, " in w for w in warns), (fails, warns)
    plain, _uris = GS.card_at_date_surface(read=GS.DATE_OVER_INK_READ)   # the same authored read, hovering: no veil
    assert plain["scenes"][0]["docks"][0]["read_place"] == tl["scenes"][0]["docks"][0]["read_place"]
    veil = _read(tl, uris, [t])[0][0]
    bare = _read(plain, uris, [t])[0][0]
    import io
    from PIL import Image
    a, b = Image.open(io.BytesIO(veil)).convert("L"), Image.open(io.BytesIO(bare)).convert("L")
    x0, y0, x1, y1 = GS.DATE_BLUR_REGION

    def energy(im) -> float:
        return sum((im.getpixel((x + 1, y)) - im.getpixel((x, y))) ** 2
                   for y in range(y0, y1, 2) for x in range(x0, x1 - 1)) / max(1, (x1 - x0) * (y1 - y0) // 2)

    assert energy(a) < 0.6 * energy(b), "the plot beside the reading card is blurred"


def test_a_second_joined_card_parks_and_reads_clear_of_the_first(railway):
    """R4, the proof walk: one card per episode, the earlier ones still parked at their dates - the next card's chip and
    its read are placed round the chips already on stage (the row loop hands them in), never over them."""
    first = B.park_at_place(railway, {"datum": PEAK}, ASPECT, 0.6657)
    chip = {k: first[k] for k in ("x", "y", "w", "h")}
    second = B.park_at_place(railway, {"datum": 60}, ASPECT, 0.6657, [chip])
    assert B._overlap_area(second, chip) == 0, (second, chip)
    alone = B.park_at_place(railway, {"datum": 60}, ASPECT, 0.6657)
    assert B._overlap_area(alone, chip) > 0, "the control: placed alone, the next date's chip would stack on the first"
    solo = B.dock_read_box(ASPECT, None, 0.6657)
    got, _note = B.park_at_read(railway, second, solo, ASPECT, 0.6657, {}, {}, [chip])
    if got.get("read_place"):
        assert B._overlap_area(got["read_place"], chip) == 0, "the next card reads clear of the first's chip"
    src = COMPILER.read_text(encoding="utf-8")
    assert src.count('[_d["place"] for _d in docks if _d.get("park_at") and float(_d["exit"]) > float(enter)]') == 2, \
        "the row loop hands the chips still on stage to the chip search and to the read"


def test_the_compiled_join_reads_back_as_the_option_it_was(railway):
    """derive_beat_moves copies every DOCK_OPTS key off the compiled dock: the entry's `park_at` carries the option's own
    keys, resolved, so the read-back option compiles to the same chip (the author's side and anchor are the search's)."""
    import derive_beat_moves as DBM
    pk = B.park_at_place(railway, {"datum": PEAK}, ASPECT, 0.6657)
    entry = B.dock_entry("ev-a", 0, 4.0, 14.0, 0, B.DOCK_KIND_IMAGE, {k: pk[k] for k in ("x", "y", "w", "h")},
                         park_at={"datum": PEAK, "series": 0, "side": pk["side"], "anchor": pk["ay"]})
    back = DBM.dock_move(entry, "at its peak", DBM.dock_option_fields())["options"]["park_at"]
    again = B.park_at_place(railway, B.dock_opts({"park_at": back})["park_at"], ASPECT, 0.6657)
    assert {k: again[k] for k in ("x", "y", "w", "h", "side", "ay")} == {k: pk[k] for k in ("x", "y", "w", "h", "side", "ay")}
