"""P71 T32 (was P69 T80) - THE CAMERA PEDESTAL AND THE MAGNIFIER LENS.

Two Bravos verbs (the harvest v2's A33 and A57), one slice because both change the VIEW and never the data:

- the PEDESTAL (`kinetics/camera.mjs` `camPedestalState`): a row's camera names `pedestal: {at, dur, by, ease?}`; until
  its word the camera stands RAISED by `by` of the stage's height (the stage is taller than the frame: the page's lower
  part is below it), and on its word it travels straight DOWN to the identity and holds there (BUB 0:00, "pedestal down
  through the waterline"). It moves only after the build has settled: a pedestal over a page build or a card's build is
  REFUSED by name (M14, "the camera never moves over a build"), and the motion gate's camera mirror reads the same
  window. Absent, every frame is the frame it was.
- the LENS (`species/lens.mjs`, a PAGE species): a magnifier glass travels a stretch of one drawn line on its word and,
  inside its ring, redraws the page's OWN points at `zoom` about the glass's centre - the same series, no value invented
  (BRAVOS-USE-WHEN A57's don't: "invent zoomed values"). Bravos's glass measured k = 1.0 (STK 9:16-9:18), so `zoom` is the
  author's dial, default 1.

The engine's laws are pinned by tests/kinetics/camera.test.mjs and tests/kinetics/lens.test.mjs; this file pins the
compiler's grammar and refusals, the gate's mirror, the engine's wiring, the cards, and both read on the SERVED player
(the golden `lens-over-the-line`: the memory monitor's long customs line, "one soft month in June", Steel and Paper H
row 22).
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
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CAMERA = ROOT / "content/video_engine/scripts/kinetics/camera.mjs"
MODULE = ROOT / "content/video_engine/scripts/species/lens.mjs"
CARDS = ROOT / "content/video_engine/effects/cards"
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
PLATE = "ledger:ev-memory-monitor-v1:line:42:right"
PED = {"at": 12.0, "dur": 2.0, "by": 0.21}
LENS = {"kind": "lens", "at": 12.69, "dur": 2.5, "from": 40, "to": 41, "zoom": 2}


def _cam_errs(cam, species=()):
    return B.validate_camera_row(cam, list(species), "p")


def _scene(ped=None, docks=(), build_windows=None, span=(0.0, 20.0), keys=None, species=()):
    cam = {"keys": list(keys or [])}
    if ped is not None:
        cam["pedestal"] = dict(ped)
    sc = {"scene_id": "s01", "span": list(span), "camera": cam, "docks": [dict(d) for d in docks],
          "species": [dict(s) for s in species], "world": {"kind": "ledger", "ken_burns": {"scale": 0}}}
    if build_windows is not None:
        sc["build_windows"] = [list(w) for w in build_windows]
    return sc


DOCK = {"slide": "ev-card", "enter": 12.5, "exit": 18.0, "arrive": "slide", "place": {"x": 100, "y": 100, "w": 400, "h": 300}}


# ---- the pedestal: the grammar -------------------------------------------------------------------------------


def test_a_well_formed_pedestal_is_accepted_and_the_identity_camera_is_untouched():
    assert _cam_errs({"pedestal": dict(PED)}) == []
    assert _cam_errs({"pedestal": dict(PED, ease="cubic")}) == []
    assert _cam_errs(None) == [] and _cam_errs(B.camera_identity()) == []
    assert B.CAMERA_PEDESTAL_KEYS == ("at", "dur", "by", "ease")


@pytest.mark.parametrize("ped, needle", [
    ("down", "camera pedestal must be a dict"),
    ({"dur": 2.0, "by": 0.2}, "camera pedestal: 'at' must be a number"),
    ({"at": True, "dur": 2.0, "by": 0.2}, "camera pedestal: 'at' must be a number"),
    ({"at": 12.0, "by": 0.2}, "camera pedestal: 'dur' must be a number > 0"),
    ({"at": 12.0, "dur": 0, "by": 0.2}, "camera pedestal: 'dur' must be a number > 0"),
    ({"at": 12.0, "dur": 2.0}, "camera pedestal: 'by' must be a share of the stage's height"),
    ({"at": 12.0, "dur": 2.0, "by": 0}, "camera pedestal: 'by' must be a share of the stage's height"),
    ({"at": 12.0, "dur": 2.0, "by": 1.0}, "camera pedestal: 'by' must be a share of the stage's height"),
    ({"at": 12.0, "dur": 2.0, "by": 0.2, "ease": "hold"}, "camera pedestal: ease must be one of cubic|inout|linear"),
    ({"at": 12.0, "dur": 2.0, "by": 0.2, "ease": "bounce"}, "camera pedestal: ease must be one of cubic|inout|linear"),
    ({"at": 12.0, "dur": 2.0, "by": 0.2, "up": True}, "camera pedestal: 'up' - a pedestal takes only at|dur|by|ease"),
])
def test_a_malformed_pedestal_is_refused_by_name(ped, needle):
    errs = _cam_errs({"pedestal": ped})
    assert any(needle in e for e in errs), errs


def test_a_pedestal_shares_its_row_with_no_other_camera_move():
    keys = [{"t": 1.0, "zoom": 1.1, "look": [0.5, 0.5]}, {"t": 3.0, "zoom": 1.0, "look": [0.5, 0.5]}]
    assert any("camera keys and a pedestal on one row" in e for e in _cam_errs({"keys": keys, "pedestal": dict(PED)}))
    punch = {"kind": "punch", "at": 5.0, "dur": 1.0, "target": {"kind": "point", "x": 0.5, "y": 0.5}}
    assert any("a pedestal and a punch species on one row" in e for e in _cam_errs({"pedestal": dict(PED)}, [punch]))
    assert any("attention landings and a pedestal on one row" in e
               for e in _cam_errs({"attention": "landings", "pedestal": dict(PED)}))


# ---- the pedestal: after the settle (M14), inside its row ------------------------------------------------------


def test_a_pedestal_after_the_settle_passes():
    sc = _scene(PED, docks=[dict(DOCK, enter=15.0)], build_windows=[[0.0, 3.2], [6.0, 7.5]])
    assert B.pedestal_errors(sc) == []
    assert B.pedestal_errors(_scene(None)) == [], "no pedestal: nothing to say"


def test_a_pedestal_over_the_page_build_is_refused_by_name():
    errs = B.pedestal_errors(_scene(PED, build_windows=[[0.0, 3.2], [11.5, 12.6]]))
    assert len(errs) == 1 and "s01: camera pedestal 12.0-14.0s moves over the page's build 11.5-12.6s" in errs[0], errs
    assert "M14" in errs[0] and "after the build has settled" in errs[0], errs


def test_a_pedestal_over_a_card_build_is_refused_by_name():
    errs = B.pedestal_errors(_scene(PED, docks=[DOCK]))
    assert len(errs) == 1 and "moves over ev-card's build 12.5-" in errs[0] and "M14" in errs[0], errs


def test_a_pedestal_outside_its_row_is_refused_by_name():
    errs = B.pedestal_errors(_scene(dict(PED, at=19.0), span=(0.0, 20.0)))
    assert any("camera pedestal 19.0-21.0s runs past its row (0.0-20.0s)" in e for e in errs), errs
    errs = B.pedestal_errors(_scene(dict(PED, at=-1.0), span=(0.0, 20.0)))
    assert any("runs past its row" in e for e in errs), errs


# ---- the pedestal: the gate's camera mirror (M14, M09, the state) ---------------------------------------------


def test_the_gate_reads_the_pedestal_as_the_player_draws_it():
    sc = _scene(PED)
    raised = G.camera_state_at(sc, 5.0, 1920, 1080, None)
    assert raised["s"] == 1.0 and raised["at"] == (960.0, 540.0)
    assert abs(raised["look"][1] - (540.0 - 0.21 * 1080)) < 1e-9 and raised["look"][0] == 960.0
    mid = G.camera_state_at(sc, 13.0, 1920, 1080, None)
    assert abs(mid["look"][1] - (540.0 - 0.21 * 1080 * 0.5)) < 1e-9, "the in-out ease: half the clock is half the travel"
    landed = G.camera_state_at(sc, 14.0, 1920, 1080, None)
    assert landed == {"s": 1.0, "look": (960.0, 540.0), "at": (960.0, 540.0)}, landed
    assert G.camera_state_at(_scene(None), 13.0, 1920, 1080, None) == landed, "absent: the identity, as before"


def test_m14_fails_a_pedestal_over_a_build_and_passes_one_after_the_settle():
    over = G._build_clashes([_scene(PED, docks=[DOCK])], [])
    assert over and "camera pedestal 12.0-14.0s over ev-card build" in over[0][1], over
    page = G._build_clashes([_scene(PED, build_windows=[[11.5, 12.6]])], [])
    assert page and "camera pedestal 12.0-14.0s over the page build 11.5-12.6s" in page[0][1], page
    assert G._build_clashes([_scene(PED, docks=[dict(DOCK, enter=15.0)], build_windows=[[0.0, 3.2]])], []) == []
    keyed = _scene(None, docks=[DOCK], build_windows=[[11.5, 12.6]])
    assert G._build_clashes([keyed], []) == [], "a row with no pedestal reads exactly as before (the page build is the pedestal's)"


def test_m09_reads_a_pedestal_stacked_on_another_camera_move():
    sc = _scene(PED)
    sc["world"]["ken_burns"] = {"scale": 0.04}
    assert G._camera_clashes([sc]) == [("s01", "camera pedestal over Ken Burns scale 0.04")]
    assert G._camera_clashes([_scene(PED)]) == []


def test_r26_209_reads_a_landed_pedestal_as_a_closed_camera():
    a, b = _scene(PED, span=(0.0, 20.0)), dict(_scene(None, span=(20.0, 30.0)), scene_id="s02")
    notes = B.camera_boundary_notes([a, b], "16:9")
    assert notes == [("INFO", "1 scene boundary, 0 open - every key set is back at identity by its row's end")], notes


# ---- the pedestal: the engine's one call, synced ----------------------------------------------------------------


def test_the_engine_applies_the_pedestal_in_its_one_camera_call():
    src = ENGINE.read_text(encoding="utf-8")
    assert "export const camPedestalState" in CAMERA.read_text(encoding="utf-8")
    assert "const camPedestalState = (ped, t, st, H) =>" in src, "the camera region is synced (sync_kinetics.py --write)"
    cam_now = src[src.index("const camNow = (sc, t) => {"):src.index("const camCss = (xf) =>")]
    assert "camPedestalState((sc.camera || {}).pedestal, t, st, STAGE_H)" in cam_now, cam_now[-600:]


# ---- the lens: the grammar and the page ---------------------------------------------------------------------------


def _lens_errs(entries, plate=PLATE):
    return B.validate_species([dict(e) for e in entries], (0, 0, 0), plate)


def _monitor_world() -> dict:
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        return B.world_for_plate(PLATE + ";idle=live", (0, 0, 0), PROJECT)
    finally:
        B.ASPECT = saved


def test_the_lens_is_a_page_species_with_its_when():
    assert B.SPECIES_LENS == "lens"
    assert "lens" in B.SPECIES_KINDS and "lens" in B.PAGE_SPECIES
    assert "lens" not in B.PANEL_SPECIES, "one page's line; a panel's lens is not built"
    assert "small region of a long line" in B.SPECIES_WHEN["lens"]
    assert _lens_errs([LENS]) == []
    assert _lens_errs([{"kind": "lens", "at": 1.0, "dur": 2.0, "from": 5}]) == [], "a glass may stand on ONE datum"


@pytest.mark.parametrize("patch, needle", [
    ({"from": None}, "lens: 'from' must be a datum index"),
    ({"from": -1}, "lens: 'from' must be a datum index"),
    ({"from": 0.5}, "lens: 'from' must be a datum index"),
    ({"to": "june"}, "lens: 'to' must be a datum index"),
    ({"to": 40}, "lens: from and to are both datum 40"),
    ({"series": -1}, "lens: series must be a non-negative integer"),
    ({"zoom": 0.5}, "lens: zoom must be a number from 1"),
    ({"zoom": 9}, "lens: zoom must be a number from 1"),
    ({"zoom": True}, "lens: zoom must be a number from 1"),
    ({"label": "June"}, "lens: 'label' - a lens writes nothing and takes only"),
])
def test_a_malformed_lens_is_refused_by_name(patch, needle):
    e = {k: v for k, v in dict(LENS, **patch).items() if v is not None}
    errs = _lens_errs([e])
    assert any(needle in x for x in errs), errs


def test_the_lens_reads_the_page_it_magnifies():
    world = _monitor_world()
    assert B.check_lens(world, [dict(LENS)]) == []
    with pytest.raises(ValueError, match=r"lens at 12.69: 'to' 43 is past series 0's last datum \(42\)"):
        B.check_lens(world, [dict(LENS, to=43)])
    with pytest.raises(ValueError, match=r"lens at 12.69: series 3 is past the page's last series \(2\)"):
        B.check_lens(world, [dict(LENS, series=3)])
    bars = dict(world, page=dict(world["page"], builder="story"))
    with pytest.raises(ValueError, match=r"lens at 12.69: a story page has no line to magnify"):
        B.check_lens(bars, [dict(LENS)])


def test_the_compiler_mirrors_the_modules_dials():
    src = MODULE.read_text(encoding="utf-8")
    zoom = float(re.search(r"\bZOOM:\s*([0-9.]+)", src).group(1))
    zmax = float(re.search(r"\bZOOM_MAX:\s*([0-9.]+)", src).group(1))
    assert (B.LENS_ZOOM_DEFAULT, B.LENS_ZOOM_MAX) == (zoom, zmax)
    assert zoom == 1.0, "E38: Bravos's glass measured k = 1.0 (STK 9:16-9:18) - the default magnifies nothing"


def test_the_lens_is_wired_through_the_page_registry():
    src = ENGINE.read_text(encoding="utf-8")
    assert "/* KINETICS:BEGIN lens */" in src
    assert src.index("/* KINETICS:BEGIN lit_stretch */") < src.index("/* KINETICS:BEGIN lens */") < src.index("const paintPerform =")
    build = src[src.index("const buildPerform ="):src.index("const paintPerform =")]
    assert 'pageSpecies(scene, "lens")' in build
    perform = src[src.index("const paintPerform ="):]
    assert "PAGE_PAINTERS.lens" in perform[:perform.index("const ", 200)] or "PAGE_PAINTERS.lens" in perform[:20000]
    assert G.SPECIES_EVENTS["lens"] == ("at", "end"), "the glass TRAVELS (s99): it counts as motion"


def test_the_cards():
    pages = {c["id"]: c for c in json.loads((CARDS / "page_species.json").read_text(encoding="utf-8"))["cards"]}
    card = pages["page_species:lens"]
    assert card["token"] == "lens" and card["lives"]["path"] == "content/video_engine/scripts/species/lens.mjs"
    assert card["dials"] == {"module": "content/video_engine/scripts/species/lens.mjs", "object": "LENS"}
    assert {"source": "docs/research/bravos-style/BRAVOS-USE-WHEN.md:1103"}.items() <= card["aliases"][1].items(), "its USE-WHEN (A57)"
    assert "invent" in card["aliases"][1]["name"] and card["proof"]["golden"] == "lens-over-the-line"
    cams = {c["id"]: c for c in json.loads((CARDS / "camera.json").read_text(encoding="utf-8"))["cards"]}
    ped = cams["camera:pedestal"]
    assert ped["dials"] == {"module": "content/video_engine/scripts/kinetics/camera.mjs", "object": "PEDESTAL"}
    assert ped["aliases"][1]["source"] == "docs/research/bravos-style/BRAVOS-USE-WHEN.md:489", "its USE-WHEN (A33)"
    assert "M14" in ped["when"] and "M14" in ped["aliases"][1]["name"]


# ---- both, read on the served player -------------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

LENS_PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp, PF = st.perform || {}, L = (PF.lenses || [])[0];
  if (!L) return null;
  const S = (st.states && st.states[st.active | 0]) || st;
  const ser = (S.markBy || {}).s0, pts = ser && ser.geom && ser.geom.pts, k0 = (ser && ser.geom.k0) | 0, off = (S.windowOffsets || [])[0] | 0;
  const nums = (d) => (d || '').replace(/[ML]/g, ' ').trim().split(/\\s+/).filter(Boolean).map(Number);
  const line = L.lines.find(q => q.si === 0), d = nums(line && line.path.getAttribute('d'));
  const xy = []; for (let j = 0; j + 1 < d.length; j += 2) xy.push([d[j], d[j + 1]]);
  return { g: parseFloat(L.g.getAttribute('opacity') || '0'), cx: +L.ring.getAttribute('cx'), cy: +L.ring.getAttribute('cy'),
           r: +L.ring.getAttribute('r'), clipR: +L.clip.getAttribute('r'), zoom: L.zoom, xy,
           page: pts ? pts.map((p, j) => ({ i: off + k0 + j, p })) : [] };
}"""

CAM_PROBE = """() => { const st = window.__camera(arguments[0]); return st; }"""


def _serve_timeline(tl: dict, uris: dict):
    import render_baseline as RB
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)   # R26-351: guarded

    def at(t: float, probe: str = LENS_PROBE):
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(probe)

    return at, errs, close, page


@needs_browser
def test_the_lens_travels_the_stretch_and_redraws_the_same_points_at_its_zoom():
    import build_golden_sources as GS
    tl, uris = GS.lens_over_the_line()
    at, errs, close, _page = _serve_timeline(tl, uris)
    try:
        a0, dur = GS.LENS_AT, GS.LENS_DUR
        before, early, mid, after = at(a0 - 0.2), at(a0 + 0.35 * dur), at(GS.FRAME_T["lens-over-the-line"]), at(a0 + dur + 0.2)
    finally:
        close()
    assert not errs, errs
    assert before["g"] == 0 and after["g"] == 0, "the glass is up only on its word - it arrives, travels and leaves"
    assert mid["g"] == 1 and mid["zoom"] == 2 and abs(mid["clipR"] - mid["r"]) < 30, mid
    assert (early["cx"], early["cy"]) != (mid["cx"], mid["cy"]), "the glass MOVES between two instants (s99: it travels)"
    page = {q["i"]: q["p"] for q in mid["page"]}
    c, k = (mid["cx"], mid["cy"]), mid["zoom"]
    mapped = [(c[0] + k * (p[0] - c[0]), c[1] + k * (p[1] - c[1])) for p in page.values()]
    assert len(mid["xy"]) >= 3, mid["xy"]
    for x, y in mid["xy"]:   # acceptance 2: every vertex inside the glass is one of the page's OWN points, magnified
        assert min(abs(x - mx) + abs(y - my) for mx, my in mapped) < 0.2, ("a vertex no datum makes: an invented value", x, y)
    june = page[41]
    assert (june[0] - c[0]) ** 2 + (june[1] - c[1]) ** 2 < (mid["r"] / k) ** 2 * 4, "the soft June is in the glass"


@needs_browser
def test_the_pedestal_on_the_served_player_raises_then_lands_on_the_identity():
    import build_golden_sources as GS
    tl, uris = GS.lens_over_the_line()
    tl = json.loads(json.dumps(tl))
    tl["scenes"][0]["camera"] = {"keys": [], "pedestal": {"at": 6.0, "dur": 2.0, "by": 0.21}}
    tl["kinetics"] = {"camera": True}   # the persistent camera is ON for every compiled timeline (CAPABILITIES :102)
    at, errs, close, _page = _serve_timeline(tl, uris)
    probe = "() => { const s = window.__camera(document.getElementById('scrub').value * 1); return s; }"
    try:
        raised, mid, landed = at(3.0, probe), at(7.0, probe), at(9.0, probe)
    finally:
        close()
    assert not errs, errs
    fr = lambda s: s.get("frustum") or s.get("frame") or s   # noqa: E731
    assert abs(fr(raised)["y0"] + 0.21 * 1080) < 0.6, raised
    assert abs(fr(mid)["y0"] + 0.105 * 1080) < 0.6, mid
    assert abs(fr(landed)["y0"]) < 1e-6 and abs(fr(landed)["y1"] - 1080) < 1e-6, landed
