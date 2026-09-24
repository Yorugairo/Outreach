"""P69 T26e / E99 s107 - PROPS, PAGES AND CHARTS MORPH INTO EACH OTHER, BOTH WAYS, MID-PAGE.

The operator (2026-09-23): *"we should also be able to morph/transform to/from props to pages and charts."* What this
file holds the compiler, the kinetics and the engine to:

  (1) PROP -> PAGE/CHART   `;morph=prop:<id>` on a page ENTER (the prop standing at the boundary becomes the area under
                           the page's first series), and a mid-page `chart_to {to: "morph", from: "prop:<id>", mark}` on a
                           word (the prop standing in the row becomes a bar `b:<i>` or the area).
  (2) PAGE/CHART -> PROP   `exit: morph:prop:<id>[:<s>]` and a mid-page `chart_to {to: "prop", prop: <id>, place?}` - the
                           page panel or a named mark becomes the prop, which then STANDS as a T26d prop dock (its place,
                           its moves, its T6b hatch).
  (3) ONE OBJECT           the prop's own pixels ride the ARAP mesh (texture-mapped, triangle by triangle) and hand over to
                           the chart's own ink by the landing - never a cross-fade between two pictures.
  (4) SEEK-SAFE            a cold seek lands the frame forward play lands; det J > 0 at every t; the match-cut invariants
                           are a WARN with their numbers when they fail (s106), never a refusal.
  (5) BYTE-IDENTICAL       a row that names none of it compiles exactly as before (the goldens and the H door hold the rest).
  (6) NOT STAR-SHAPED      a traced silhouette the fan cannot carry is triangulated (ear-clipping) or the fan is refused BY
                           NAME and the strip carries it.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import math
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

DC = "prop-hyperscale-datacenter-v1"
DC_PATH = ROOT / "content/video_engine/assets/props/cutouts" / f"{DC}.png"
SW, SH = 1920, 1080
WHERE = "shot row 1 (0-30s)"


def _stamp_dock(enter=10.0, exit_=29.0, **extra):
    return (DC, 0, enter, exit_, {"prop": True, "arrive": "stamp", "place": {"x": 0.84, "y": 0.47, "w": 0.2}, **extra})


# ---- (1) + (2) THE GRAMMAR -------------------------------------------------------------------------------------------


def test_a_PROP_is_a_morph_source_on_a_page_enter():
    """RED before T26e: `;morph=prop:<id>` was refused as an unknown morph shape (MORPH_SHAPES: tab|plate|card)."""
    _bare, opts = B.split_plate_opts(f"ledger:ev-x:line;morph=prop:{DC}")
    assert opts["morph"] == f"prop:{DC}"
    assert B.morph_prop_id(f"prop:{DC}") == DC and B.morph_prop_id("tab") is None
    with pytest.raises(ValueError, match="catalogue|not in"):
        B.split_plate_opts("ledger:ev-x:line;morph=prop:prop-no-such-thing-v9")
    with pytest.raises(ValueError, match="tab"):
        B.split_plate_opts("ledger:ev-x:line;morph=blob")   # a bad name is still refused by name


def test_the_mid_page_PROP_TO_CHART_verb_is_read_off_the_row_and_hands_the_standing_dock_over():
    """`chart_to {to: morph, from: prop:<id>}` leaves the row's species (the gates never read it as a state change) and
    becomes a prop morph on the scene; the prop dock that stands at its word is HANDED to it - its exit is the word."""
    sp = [{"kind": "retitle", "at": 12.0, "dur": 1.0, "text": "x"},
          {"kind": "chart_to", "to": "morph", "from": f"prop:{DC}", "at": 20.0, "mark": "b:1", "id": "s01.species.1"}]
    r = B.prop_morph_row(sp, [_stamp_dock()], None, 0.0, 30.0, WHERE)
    assert [e["kind"] for e in r["species"]] == ["retitle"], "the verb is not a chart_to state change"
    (m,) = r["morphs"]
    assert m["way"] == "in" and m["prop"] == DC and m["at"] == 20.0 and m["dur"] == B.PROP_MORPH_S and m["mark"] == "b:1"
    assert m["id"] == "s01.species.1"
    assert r["ds"][0][3] == 20.0 and r["handed"] == {0}, "the standing dock's life ends on the word"
    assert r["exit"] is None and r["born"] == set()


def test_the_mid_page_CHART_TO_PROP_verb_writes_the_prop_that_STANDS_as_a_T26d_dock():
    place = {"x": 0.8, "y": 0.5, "w": 0.18}
    sp = [{"kind": "chart_to", "to": "prop", "prop": DC, "at": 22.0, "dur": 1.5, "mark": "b:0", "place": place, "rot": -3,
           "moves": [{"at": 26.0, "x": 0.7, "dur": 0.8}], "id": "s01.species.0"}]
    r = B.prop_morph_row(sp, [], None, 0.0, 30.0, WHERE)
    (m,) = r["morphs"]
    assert m["way"] == "out" and m["mark"] == "b:0" and m["dur"] == 1.5
    (d,) = r["ds"]
    aid, slot, enter, exit_, opts = d
    assert (aid, slot, enter, exit_) == (DC, 0, 23.5, 30.0), "born on the landing, standing to the row's end"
    assert opts == {"prop": True, "place": place, "rot": -3, "moves": [{"at": 26.0, "x": 0.7, "dur": 0.8}]}
    assert B.dock_opts(opts) == opts, "the born dock is an ordinary T26d prop dock"
    assert r["born"] == {0}


def test_a_CHART_TO_PROP_with_no_place_stands_at_the_default_and_SAYS_so():
    r = B.prop_morph_row([{"kind": "chart_to", "to": "prop", "prop": DC, "at": 5.0}], [], None, 0.0, 30.0, WHERE)
    assert r["ds"][0][4]["place"] == {"x": 0.5, "y": 0.5, "w": B.PROP_MORPH_W}
    assert r["morphs"][0]["mark"] == "page", "the page panel is the default source"
    assert any("no place" in n for n in r["notes"])


def test_the_EXIT_morph_prop_is_the_ENTRY_the_page_before_collapses_into_the_prop_this_row_stands():
    """A row's `exit` is the transition INTO it (the player reads `sc.exit` against the scene before, as melt:morph
    does): `morph:prop:<id>[:<s>]` ARRIVES ON THE CUT - over THIS row's first s seconds the page of the row before
    stands over this row's world and collapses into the prop, which lands STANDING (its dock's enter is the landing:
    born standing, no second arrival) - never a beat of bare cream (the parent's review, (c))."""
    row2 = [(DC, 0, 30.0, 40.0, {"prop": True, "place": {"x": 0.7, "y": 0.5, "w": 0.2}})]
    r = B.prop_morph_row([], row2, f"morph:prop:{DC}:1.5", 30.0, 40.0, "shot row 2 (30-40s)", sid="s02", prev_a=0.0)
    assert r["exit"] == "cut" and r["born"] == {0} and r["morphs"] == []
    assert r["enter_morph"] == {"id": "s02.enter", "way": "out", "prop": DC, "at": 30.0, "dur": 1.5, "mark": "page", "over": True}
    assert r["ds"][0][2] == 31.5 and row2[0][2] == 30.0, "the born dock stands from the landing; the row is not mutated"
    with pytest.raises(ValueError, match="before the collapse lands"):
        B.prop_morph_row([], [(DC, 0, 30.0, 31.0, {"prop": True})], f"morph:prop:{DC}:1.5", 30.0, 40.0, "r", prev_a=0.0)
    r2 = B.prop_morph_row([], row2, f"morph:prop:{DC}", 30.0, 40.0, "r", prev_a=0.0)
    assert r2["enter_morph"]["dur"] == B.PROP_MORPH_S
    with pytest.raises(ValueError, match="first frame"):
        B.prop_morph_row([], [], f"morph:prop:{DC}", 30.0, 40.0, "r", prev_a=0.0)
    with pytest.raises(ValueError, match="first row"):
        B.prop_morph_row([], row2, f"morph:prop:{DC}", 30.0, 40.0, "r", prev_a=None)
    # ... played by the scene before: appended to ITS prop morphs, its page's leave is the collapse
    prev = {"scene_id": "s01", "span": [0.0, 30.0], "species": [],
            "world": {"kind": "ledger", "page": {"builder": "story", "values": [1, 2]}}}
    B.attach_enter_morph(r["enter_morph"], prev, None, "16:9", "r", lambda aid: DC_PATH)
    assert prev[B.PROP_MORPH_KEY] == [{**r["enter_morph"], "state": 0}] and prev["world"]["page"]["exit"] == "cut"
    assert B.prop_morph_hold_warns(r["enter_morph"], None, [], 0, 30.0, "r") == [], "a page made into a prop holds no mark"
    with pytest.raises(ValueError, match="only a PAGE"):
        B.attach_enter_morph(r["enter_morph"], {"world": {"asset_id": "x"}}, None, "16:9", "r", lambda aid: DC_PATH)


@pytest.mark.parametrize("entry, match", [
    ({"kind": "chart_to", "to": "morph", "from": "prop:prop-no-such-thing-v9", "at": 20.0, "mark": "b:1"}, "catalogue|not in"),
    ({"kind": "chart_to", "to": "morph", "from": f"prop:{DC}", "at": 20.0, "mark": "bar one"}, "mark"),
    ({"kind": "chart_to", "to": "morph", "from": f"prop:{DC}", "at": 20.0, "mark": "b:1", "state": 1}, "state"),
    ({"kind": "chart_to", "to": "morph", "from": f"prop:{DC}", "at": 2.0, "mark": "b:1"}, "stands"),
    ({"kind": "chart_to", "to": "prop", "at": 20.0}, "prop"),
    ({"kind": "chart_to", "to": "prop", "prop": DC, "at": 20.0, "place": {"x": 0.5}}, "place"),
    ({"kind": "chart_to", "to": "prop", "prop": DC, "at": 20.0, "dur": -1}, "dur"),
    ({"kind": "chart_to", "to": "prop", "prop": DC, "at": 29.5, "dur": 2.0}, "row"),
])
def test_what_cannot_be_played_is_refused_BY_NAME(entry, match):
    with pytest.raises(ValueError, match=match):
        B.prop_morph_row([entry], [_stamp_dock()], None, 0.0, 30.0, WHERE)


def test_a_morph_from_the_OUTGOING_scenes_prop_resolves_the_page_enter_source():
    """`;morph=prop:<id>` reads the prop dock standing at the boundary in the scene before: its canvas box, its angle and
    its traced outline (stage fractions - the planted poly the soak seeds on). None standing: placed on the target, WARNed."""
    prev = {"scene_id": "s01", "span": [0.0, 20.0], "docks": [B.dock_entry(DC, 0, 5.0, 20.0, 0, B.DOCK_KIND_PROP,
            {"x": 1500.0, "y": 380.0, "w": 320.0, "h": 198.6}, "stamp", None, True, prop=True, rot=-6.0)]}
    world = {"kind": "ledger", "page": {"enter": "morph"}, "morph": f"prop:{DC}"}
    src, notes = B.resolve_morph_prop(world, prev, 20.0, WHERE, lambda aid: DC_PATH)
    assert src["prop"] == DC and src["box"] == [1500.0, 380.0, 320.0, 198.6] and src["rot"] == -6.0
    assert len(src["poly"]) >= 3 and all(0 <= x <= 1 and 0 <= y <= 1 for x, y in src["poly"])
    assert B.morph_source_error({"morph": src}, "t") is None
    alone, notes2 = B.resolve_morph_prop(world, None, 20.0, WHERE, lambda aid: DC_PATH)
    assert alone == {"prop": DC} and any("no dock" in n for n in notes2)
    assert B.resolve_morph_prop({"kind": "ledger", "morph": "tab"}, prev, 20.0, WHERE, lambda aid: DC_PATH) == ("tab", [])


# ---- (3) the silhouette the texture rides ----------------------------------------------------------------------------


def test_the_silhouette_strip_is_CONSERVATIVE_every_painted_pixel_is_inside_it():
    """The strip is the one the texture is mapped on, so no painted pixel may fall outside it (a pixel outside is a pixel
    the morph's first frame would drop)."""
    from PIL import Image
    sil = B.prop_silhouette(DC_PATH, 48)
    with Image.open(DC_PATH) as im:
        a = im.convert("RGBA").getchannel("A")
        W, H = a.size
        px = a.load()
    xs, top, bot = sil["x"], sil["top"], sil["bot"]
    assert len(xs) == len(top) == len(bot) == 48
    miss = 0
    for x in range(W):
        for y in range(H):
            if px[x, y] <= B.STAMP_ALPHA_MIN:
                continue
            for xx in (x + 0.02, x + 0.98):   # the pixel's two sides
                u = xx / W
                k = max(0, min(46, int((u - xs[0]) / (xs[-1] - xs[0]) * 47)))
                f = (u - xs[k]) / (xs[k + 1] - xs[k])
                t_ = top[k] + (top[k + 1] - top[k]) * f
                b_ = bot[k] + (bot[k + 1] - bot[k]) * f
                if not (t_ * H <= y + 0.02 and y + 0.98 <= b_ * H):
                    miss += 1
    assert miss == 0, f"{miss} painted pixel sides outside the strip"


# ---- (4) THE INVARIANTS ADVISE ----------------------------------------------------------------------------------------


def _rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def test_the_match_cut_invariants_are_the_kinetics_own_and_a_failure_is_a_WARN_with_its_numbers():
    near = B.prop_morph_invariants(_rect(900, 300, 200, 400), _rect(905, 310, 190, 380), SW)
    assert near["centroid_ok"] and near["axis_ok"] and near["area_ok"]
    far = B.prop_morph_invariants(_rect(1500, 380, 320, 200), _rect(900, 380, 200, 420), SW)
    assert not far["centroid_ok"] and abs(far["centroid_shift"] - math.hypot(660, 110) / SW) < 1e-9, far   # (1660, 480) -> (1000, 590)
    assert not far["axis_ok"] and far["axis_deg"] > 45, "a wide prop into a tall bar turns its dominant axis"
    warns = B.prop_morph_warns(far, "s10 prop morph at 297.49 (in, b:1)")
    assert len(warns) == 1 and not warns[0].startswith("[WARN]") and "centroid" in warns[0] and "34.8% W" in warns[0], warns
    assert "axis" in warns[0] and "area" in warns[0]
    assert B.prop_morph_warns(near, "x") == []


# ---- (5) BYTE-IDENTICAL -----------------------------------------------------------------------------------------------


def test_a_bar_held_hidden_LONGER_THAN_2s_before_its_morph_is_a_WARN_with_its_numbers():
    """(b) A bar a prop becomes is held hidden (rect, value tag, callout) from its state's arrival to the landing. Past
    PROP_MORPH_HOLD_WARN_S before the morph begins the slot stands empty: a WARN with the numbers, never a refusal -
    H's row 16 as first authored (the recast into the capex state on 287.59 + 1.2, the morph on "six" at 297.49)."""
    sp = [{"kind": "chart_to", "to": "recast", "state": 2, "at": 287.59, "dur": 1.2}]
    m = {"way": "in", "mark": "b:1", "at": 297.49, "dur": 2.0}
    (w,) = B.prop_morph_hold_warns(m, {"page_states": [{}, {}]}, sp, 2, 242.38, "row 16")
    assert "held hidden 8.70s" in w and "288.79" in w and "297.49" in w and "299.49" in w and "> 2s" in w, w
    assert B.PROP_MORPH_HOLD_WARN_S == 2.0
    assert B.prop_morph_hold_warns({**m, "at": 289.27}, {}, sp, 2, 242.38, "row 16") == [], "0.48 s: no WARN"
    assert B.prop_morph_hold_warns({**m, "mark": "area"}, {}, sp, 2, 242.38, "r") == []


def test_a_row_that_names_none_of_it_is_returned_UNTOUCHED():
    sp = [{"kind": "chart_to", "to": "recast", "state": 1, "at": 3.0}, {"kind": "chart_to", "to": "morph", "state": 2, "at": 9.0}]
    ds = [_stamp_dock()]
    before = copy.deepcopy((sp, ds))
    r = B.prop_morph_row(sp, ds, "dip", 0.0, 30.0, WHERE)
    assert (r["species"], r["ds"], r["exit"]) == (before[0], before[1], "dip") and not r["morphs"] and not r["notes"]
    assert (sp, ds) == before, "nothing mutated"
    e = B.dock_entry(DC, 0, 1.0, 2.0, 0, B.DOCK_KIND_PROP, {"x": 1, "y": 2, "w": 3, "h": 4}, "stamp", None, True, prop=True)
    assert "handed" not in e, "a dock nobody hands writes the entry it always wrote"
    assert B.dock_entry(DC, 0, 1.0, 2.0, 0, B.DOCK_KIND_PROP, None, handed=True)["handed"] == "morph"


# ---- (6) the kinetics: the strip, the fan's refusal by name, the ears, the texture's affine ----------------------------


# (6) and the kinetics (the band strip, the rect strip, the texture's affine, the clip's growth, the fan's refusal by
# name, the ears, det J > 0 on a bay-cut silhouette into a bar) live in the kinetics suite: tests/kinetics/arap.test.mjs.


# ---- (3) + (4) ON THE FRAME: the two goldens -------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """(key) => {
  const P = window.__propMorph ? window.__propMorph(key) : null;
  const sb = document.getElementById('stage').getBoundingClientRect();
  const d = [...document.querySelectorAll('.dock')].find((x) => x.dataset.slide === 'prop-hyperscale-datacenter-v1');
  const img = d && d.querySelector('.slide-frame img'), r = img ? img.getBoundingClientRect() : null;
  const lps = [...document.querySelectorAll('.lp')], hid = lps.find((e) => getComputedStyle(e).visibility === 'hidden'),
        cut = lps.find((e) => e.style.clipPath), lp = hid || cut || lps[0];
  return { pm: P, dock: d ? { op: +getComputedStyle(d).opacity, vis: getComputedStyle(d).visibility,
                              img: r ? [r.left - sb.left, r.top - sb.top, r.width, r.height] : null } : null,
           root: lp ? { vis: getComputedStyle(lp).visibility, clip: lp.style.clipPath || '' } : null };
}"""


class _Player:
    def __init__(self, browser, tl: dict, uris: dict):
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / "p.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.size = RB.STAGE[tl.get("aspect") or "16:9"]
        self._srv, port = RB.serve(html.parent)
        self.page = browser.new_context(viewport={"width": self.size[0], "height": self.size[1]}).new_page()
        self.errors: list[str] = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, *self.size)

    def at(self, t: float, key: str) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                           "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE, key)

    def png(self, t: float) -> bytes:
        return RB.frame_png(self.page, t, self.size)

    def close(self) -> None:
        self.page.context.close(); self._srv.shutdown(); self._td.cleanup()


@contextlib.contextmanager
def _browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    try:
        yield br
    finally:
        br.close(); pw.stop()


def _crop_diff(a: bytes, b: bytes, box) -> float:
    from PIL import Image, ImageChops, ImageStat
    x, y, w, h = [int(round(v)) for v in box]
    ia = Image.open(io.BytesIO(a)).convert("RGB").crop((x, y, x + w, y + h))
    ib = Image.open(io.BytesIO(b)).convert("RGB").crop((x, y, x + w, y + h))
    return sum(ImageStat.Stat(ImageChops.difference(ia, ib)).mean) / 3


def _surface(name):
    tl, uris = G.SURFACES[name]()
    return json.loads(json.dumps(tl)), uris


def _run(name: str) -> dict:
    tl, uris = _surface(name)
    (pm,) = tl["scenes"][0]["prop_morphs"]
    at, dur, key = pm["at"], pm["dur"], pm["id"]
    ts = [round(at - 0.02, 2)] + [round(at + dur * k / 20, 3) for k in range(21)] + [round(at + dur + 0.6, 2)]
    out = {"pm": pm, "reads": {}, "png": {}, "cold": {}}
    with _browser() as br:
        fwd = _Player(br, tl, uris)
        try:
            for t in ts:
                out["reads"][t] = fwd.at(t, key)
            for t in (ts[0], round(at + 0.02, 2), round(at + dur * 0.5, 3), ts[-1]):
                out["png"][t] = fwd.png(t)
                out["reads"][t] = fwd.at(t, key)
            out["errors"] = list(fwd.errors)
        finally:
            fwd.close()
        for t in (round(at + dur * 0.5, 3), ts[-1]):
            cold = _Player(br, tl, uris)
            try:
                out["cold"][t] = hashlib.sha256(cold.png(t)).hexdigest()
            finally:
                cold.close()
    return out


@pytest.fixture(scope="module")
def to_bar():
    return _run("prop-morph-bar")


@pytest.fixture(scope="module")
def to_prop():
    return _run("prop-morph-page")


@needs_browser
def test_PROP_TO_BAR_the_prop_hands_over_to_the_mesh_with_no_cut(to_bar):
    pm, R = to_bar["pm"], to_bar["reads"]
    at = pm["at"]
    assert to_bar["errors"] == []
    before, after = R[round(at - 0.02, 2)], R[round(at + 0.02, 2)]
    assert before["dock"]["op"] > 0.99 and not (before["pm"] or {}).get("shown"), "before the word: the prop dock, no mesh"
    assert after["dock"] is None or after["dock"]["op"] == 0 or after["dock"]["vis"] == "hidden", "on the word the dock is HANDED"
    assert after["pm"]["shown"] and after["pm"]["texture"] == 1 and after["pm"]["ink"] == 0
    box = before["dock"]["img"]
    d = _crop_diff(to_bar["png"][round(at - 0.02, 2)], to_bar["png"][round(at + 0.02, 2)], box)
    assert d < 6.0, f"the prop's own pixels stand where the dock stood (mean diff {d:.2f} over its box)"


@needs_browser
def test_PROP_TO_BAR_one_object_the_texture_rides_the_mesh_then_hands_to_the_bars_own_ink(to_bar):
    pm, R = to_bar["pm"], to_bar["reads"]
    at, dur = pm["at"], pm["dur"]
    mids = [R[round(at + dur * k / 20, 3)]["pm"] for k in range(1, 20)]
    assert all(m["shown"] and m["mesh"] == "strip" and m["tris"] == 94 for m in mids)
    assert all(m["texture"] + m["ink"] <= 1.0 + 1e-9 for m in mids), "never two pictures at full strength: a hand-over, not a cross-fade"
    assert all(m["texture"] == 1 for m in mids if m["u"] < B.PROP_MORPH_HAND), "the prop's own pixels carry the shape until the hand"
    assert mids[-1]["ink"] > 0.5 and mids[-1]["texture"] < 0.5
    assert all(m["target"] > 0 and m["solved"] > 0 for m in mids), "det J > 0 at every sampled t (target and solved)"
    landed = R[round(at + dur + 0.6, 2)]["pm"]
    assert not landed["shown"] and landed["bar"] == "visible", "landed: the bar's own ink, the mesh gone"
    assert R[round(at - 0.02, 2)]["pm"]["bar"] == "hidden", "before its word the bar the prop becomes is not drawn twice"
    held = R[round(at - 0.02, 2)]["pm"]["held"]
    assert len(held) >= 2 and set(held) == {"hidden"}, f"(b) its value tag is held with it - no figure over an empty slot: {held}"
    assert set(landed["held"]) == {"visible"}, "landed: the bar and its tag stand"
    # (6): the chooser's verdict on the traced silhouette rides the probe - the engine's textured mesh is the strip either way,
    # and a strip chosen over the fan names what it refused (the C-shaped proof is the kinetics test above)
    assert mids[0]["admitted"] in ("fan", "ears", "strip")
    assert mids[0]["admitted"] != "strip" or any(x.startswith("fan") for x in mids[0]["refused"])


@needs_browser
def test_PROP_TO_BAR_a_COLD_SEEK_lands_the_frame_forward_play_lands(to_bar):
    for t, h in to_bar["cold"].items():
        assert h == hashlib.sha256(to_bar["png"][t]).hexdigest(), f"at {t} the cold seek differs from forward play"


@needs_browser
def test_PAGE_TO_PROP_the_page_collapses_into_the_prop_which_then_STANDS(to_prop):
    pm, R = to_prop["pm"], to_prop["reads"]
    at, dur = pm["at"], pm["dur"]
    assert to_prop["errors"] == []
    pre = R[round(at - 0.02, 2)]
    assert pre["root"]["clip"] == "" and (pre["dock"] is None or pre["dock"]["op"] == 0), "before the word: the page, no prop"
    mids = [R[round(at + dur * k / 20, 3)]["pm"] for k in range(1, 20)]
    assert all(m["shown"] and m["target"] > 0 and m["solved"] > 0 for m in mids)
    assert all(m["texture"] + m["ink"] <= 1.0 + 1e-9 for m in mids)
    assert mids[0]["ink"] == 1 and mids[-1]["texture"] > 0.5, "the page's own ink first, the prop's pixels by the landing"
    assert R[round(at + dur * 0.5, 3)]["root"]["clip"].startswith("polygon"), "the page is CARVED to the shape it is becoming"
    landed = R[round(at + dur + 0.6, 2)]
    assert not landed["pm"]["shown"] and landed["root"]["vis"] == "hidden"
    assert landed["dock"]["op"] > 0.99, "the prop STANDS as a dock"
    born = next(d for d in _surface("prop-morph-page")[0]["scenes"][0]["docks"] if d.get("arrive") == "morph")
    x, y, w, h = landed["dock"]["img"]
    assert abs(x - born["place"]["x"]) < 1.5 and abs(w - born["place"]["w"]) < 1.5, "at its authored place"


@needs_browser
def test_PAGE_TO_PROP_a_COLD_SEEK_lands_the_frame_forward_play_lands(to_prop):
    for t, h in to_prop["cold"].items():
        assert h == hashlib.sha256(to_prop["png"][t]).hexdigest(), f"at {t} the cold seek differs from forward play"


@needs_browser
@pytest.mark.parametrize("surface", ["prop-morph-bar", "prop-morph-page"])
def test_the_two_goldens_are_pinned_and_unchanged(surface):
    assert (RB.SOURCES / f"{surface}.timeline.json").exists() and (RB.FRAMES / f"{surface}.png").exists()
    failures = RB.check([surface])
    assert not failures, "\n".join(failures)


# ---- (1) the PAGE ENTER from a prop: the prop standing at the boundary becomes the area under the page's first series ----


ENTER_CUT = 12.0


def _enter_timeline() -> tuple[dict, dict]:
    """Scene 1: a plain plate with the data centre stamped at an authored place, standing to the cut. Scene 2: a line page
    entering by `morph` with `;morph=prop:<id>` resolved by the compiler's own door (`resolve_morph_prop`), which HANDS
    the standing dock to the page on the boundary; the boundary rules run over it (`stamp_transition_pages`)."""
    world1 = {"asset_id": "plate-plain", "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    opts = B.dock_opts({"prop": True, "arrive": "stamp", "mass": "ink", "place": {"x": 0.62, "y": 0.5, "w": 0.24}})
    paint = B.painted_box(DC_PATH)
    fit = B.stamp_dock_place(world1, "16:9", opts, paint, None, None, "t")
    dock = B.dock_entry(DC, 0, 3.0, ENTER_CUT, 0, B.DOCK_KIND_PROP, {k: fit[k] for k in ("x", "y", "w", "h", "room")},
                        "stamp", "ink", True, prop=True, ring_to=fit["ring_to"], from_to=fit["from_to"], paint=fit["paint"])
    s1 = {"scene_id": "s01", "world": world1, "exit": "cut", "span": [0.0, ENTER_CUT], "docks": [dock], "species": []}
    page2 = G._morph_target_page()
    page2["enter"] = "morph"
    world2 = {"kind": "ledger", "page": page2, "morph": f"prop:{DC}", "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    src, notes = B.resolve_morph_prop(world2, s1, ENTER_CUT, "t", lambda aid: DC_PATH)
    assert notes == [] and src["box"]
    world2["morph"] = src
    d = B.standing_prop_dock(s1, DC, ENTER_CUT)
    d["exit"], d["handed"] = ENTER_CUT, "morph"   # what the row loop writes on the boundary
    s2 = {"scene_id": "s02", "world": world2, "exit": "cut", "span": [ENTER_CUT, G.RUNTIME], "docks": [], "species": []}
    B.stamp_transition_pages([s1, s2])
    ev = {DC: {"title": "A hyperscale data centre", "source": "cutout", "species": "prop",
               "document": {"path": "x", "sha256": "0" * 64}, "badges": [], "kind": B.DOCK_KIND_PROP}}
    uris = G._base_uris()
    uris[DC] = G.uri("image/png", G.png_proxy(DC_PATH, G.PROP_PROXY_PX))
    tl = G._timeline("prop enter", [s1, s2], ev, "16:9")
    tl["kinetics"] = {"stop_action": True, **G.MORPH_KINETICS}
    return json.loads(json.dumps(tl)), uris


TEX_BOX = """() => { const s = document.getElementById('stage').getBoundingClientRect(), e = document.querySelector('#pmorph .pm-mesh:not([style*="none"]) .pm-tex');
  const d = [...document.querySelectorAll('.dock')].find((x) => x.dataset.slide === 'prop-hyperscale-datacenter-v1');
  const r = (q) => { if (!q) return null; const b = q.getBoundingClientRect(); return [b.left - s.left, b.top - s.top, b.width, b.height]; };
  return { tex: r(e), dock: d && +getComputedStyle(d).opacity > 0 ? r(d.querySelector('img')) : null }; }"""


@needs_browser
def test_PAGE_ENTER_the_standing_prop_becomes_the_area_under_the_series():
    tl, uris = _enter_timeline()
    with _browser() as br:
        pl = _Player(br, tl, uris)
        try:
            before = (pl.at(ENTER_CUT - 0.05, "enter:s02"), pl.page.evaluate(TEX_BOX))
            start = (pl.at(ENTER_CUT + 0.01, "enter:s02"), pl.page.evaluate(TEX_BOX))
            mid = pl.at(ENTER_CUT + 1.0, "enter:s02")["pm"]
            mid_png = pl.png(ENTER_CUT + 1.0)
            end = pl.at(ENTER_CUT + 2.6, "enter:s02")["pm"]
            errors = list(pl.errors)
        finally:
            pl.close()
        cold = _Player(br, tl, uris)
        try:
            cold_png = cold.png(ENTER_CUT + 1.0)
        finally:
            cold.close()
    assert errors == []
    assert before[1]["dock"] and not before[1]["tex"], "before the cut: the prop dock, no mesh"
    assert start[0]["pm"]["shown"] and start[0]["pm"]["texture"] == 1 and start[1]["dock"] is None, "on the cut the dock is HANDED to the page's mesh"
    assert all(abs(a - b) < 3.0 for a, b in zip(start[1]["tex"], before[1]["dock"])), \
        f"the prop's pixels stand where the dock stood: {start[1]['tex']} vs {before[1]['dock']}"
    assert mid["shown"] and mid["mark"] == "area" and mid["target"] > 0 and mid["solved"] > 0
    assert not end["shown"], "landed: the page's own area and line"
    assert hashlib.sha256(mid_png).hexdigest() == hashlib.sha256(cold_png).hexdigest(), "a cold seek lands the frame forward play lands"


# ---- (2) the EXIT: the page collapses ON THE CUT over the next row's world, and the prop lands standing on it ---------


EXIT_CUT, EXIT_S = 12.0, 1.6


def _exit_timeline() -> tuple[dict, dict]:
    """Scene 1: the golden's capex page. Scene 2: a plain plate whose row names `exit: morph:prop:<id>:1.6` and carries
    the data centre from its first frame - compiled by the row loop's own functions (`prop_morph_row`, `dock_entry`
    with `arrive: morph`, `attach_enter_morph`)."""
    world1 = G._prop_morph_world()
    s1 = {"scene_id": "s01", "world": world1, "exit": "cut", "span": [0.0, EXIT_CUT], "docks": [], "species": []}
    row2 = [(DC, 0, EXIT_CUT, G.RUNTIME, {"prop": True, "place": {"x": 0.62, "y": 0.5, "w": 0.24}})]
    r = B.prop_morph_row([], row2, f"morph:prop:{DC}:{EXIT_S}", EXIT_CUT, G.RUNTIME, "t", sid="s02", prev_a=0.0)
    aid, slot, enter, exitt, raw = r["ds"][0]
    opts = {**B.dock_opts(raw), "arrive": "morph"}
    world2 = {"asset_id": "plate-plain", "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    fit = B.prop_place_fit(world2, "16:9", opts, B.painted_box(DC_PATH), None, "t")
    dock = B.dock_entry(aid, slot, enter, exitt, 0, B.DOCK_KIND_PROP, {k: fit[k] for k in ("x", "y", "w", "h", "room")},
                        "morph", None, True, prop=True)
    B.attach_enter_morph(r["enter_morph"], s1, dock, "16:9", "t", lambda a: DC_PATH)
    s2 = {"scene_id": "s02", "world": world2, "exit": r["exit"], "span": [EXIT_CUT, G.RUNTIME], "docks": [dock], "species": []}
    ev = {DC: {"title": "A hyperscale data centre", "source": "cutout", "species": "prop",
               "document": {"path": "x", "sha256": "0" * 64}, "badges": [], "kind": B.DOCK_KIND_PROP}}
    uris = G._base_uris()
    uris[DC] = G.uri("image/png", G.png_proxy(DC_PATH, G.PROP_PROXY_PX))
    tl = G._timeline("prop exit", [s1, s2], ev, "16:9")
    tl["kinetics"] = {"stop_action": True}
    return json.loads(json.dumps(tl)), uris


def _px(png: bytes, x: int, y: int) -> tuple:
    from PIL import Image
    return Image.open(io.BytesIO(png)).convert("RGB").getpixel((x, y))


@needs_browser
def test_EXIT_the_page_collapses_over_the_NEXT_world_and_the_prop_lands_standing_on_it():
    tl, uris = _exit_timeline()
    plate = (43, 52, 60)   # the plain plate's own colour (build_golden_sources._base_uris)
    with _browser() as br:
        pl = _Player(br, tl, uris)
        try:
            before, before_png = pl.at(EXIT_CUT - 0.05, "s02.enter"), pl.png(EXIT_CUT - 0.05)
            mid = pl.at(EXIT_CUT + EXIT_S * 0.5, "s02.enter")
            mid_png = pl.png(EXIT_CUT + EXIT_S * 0.5)
            late_png = pl.png(EXIT_CUT + EXIT_S * 0.9)
            landed = pl.at(EXIT_CUT + EXIT_S + 0.3, "s02.enter")
            errors = list(pl.errors)
        finally:
            pl.close()
        cold = _Player(br, tl, uris)
        try:
            cold_png = cold.png(EXIT_CUT + EXIT_S * 0.5)
        finally:
            cold.close()
    assert errors == []
    assert not (before["pm"] or {}).get("shown"), "before the cut: the page, whole - the collapse arrives ON the cut"
    assert _px(before_png, 20, 20) != plate
    assert mid["pm"]["shown"] and mid["pm"]["target"] > 0 and mid["pm"]["solved"] > 0
    for png in (mid_png, late_png):   # the corners the collapsing page has left show the NEXT world, never bare cream
        assert all(_px(png, x, y) == plate for x, y in ((12, 12), (1908, 12), (12, 1068), (1908, 1068))), \
            [_px(png, x, y) for x, y in ((12, 12), (1908, 12), (12, 1068), (1908, 1068))]
    assert landed["dock"] and landed["dock"]["op"] > 0.99, "the prop stands on the next world from the landing"
    assert hashlib.sha256(mid_png).hexdigest() == hashlib.sha256(cold_png).hexdigest(), "a cold seek lands the frame forward play lands"
