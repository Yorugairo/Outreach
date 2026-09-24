"""P69 T26f / E99 s108 - THE PAGE'S CHROME IS OBJECTS: THE TITLE RESCALES AND MOVES, AND RIDES THE CAMERA.

The operator (2026-09-23), told that a camera push on a full-stage page reaches only ~1.04 because the title spans the
stage: *"Why can't the title re-scale? we have full rescaling capabilities, we should have free dynamic movement between
camera and objects."* What this file holds the compiler, the player and the gate to:

  (1) OBJECTS      the title, sub, source, y ticks, x ticks, axis names, key rail and badge rail are each an object with a
                   transform. A row moves or rescales any of them on a word, in T26d's key grammar mirrored at the data
                   level - `{"at": <word or s>, "x", "y", "scale" | "w", "rot", "dur", "ease"}` - under the row camera's
                   `chrome` (x, y: where the object's top-left lands, stage fractions; a key inherits what it does not
                   name). A tick column never leaves its gridlines (E28): a y tick takes no `y`, an x tick no `x`.
  (2) THE CAMERA   `chrome: "screen"` puts the chrome on the camera's depth-0 plane (it stays where it stands, at its own
                   size); `chrome: "fit"` on the largest plane k in [0, 1] that keeps each object whole (the counter-
                   scale into the pushed frame); a number is that k. It is P58 T3's law (CAPABILITIES:153,
                   `camLayerState`): plane zoom 1 + (s - 1) k, landing look + (at - look) k. The plot stays at k 1. A
                   tick label keeps its data coordinate at k 1 (it stays on its gridline) and its pinned one at the
                   chrome's k; a label whose gridline leaves the frame is hidden whole.
  (3) THE REACH    with `chrome` named, T26b's reach limits a push only by the claim's data - the key's own target;
                   what the chrome and the drawn end tags would have done is a WARN with its numbers. A 1.2x push on
                   the two-eras page and on row 18's index page is reachable.
  (4) SEEK-SAFE    a cold seek lands the frame forward play lands; the gate's camera mirror (`plane_state`,
                   `chrome_fit_k`) reads the same k as the player.
  (5) BYTE-IDENTICAL  a camera that names no `chrome` compiles, paints and gates exactly as before.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as MG  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

ASPECT = "16:9"
W, H = LPG.STAGE_PX[ASPECT]
EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
TWO_ERAS = "ledger:ev-tnx-two-eras-v4:line:142:right:axes:cut;idle=live;readability=longform"
DOTCOM_PEAK = {"kind": "datum", "series": 0, "index": 73}   # the dot-com era's 6.725 % in January 2000
SURFACE = "ledger-page-mid-build"                           # the divergence page, a committed golden (no project dir read)


def _two_eras_world(tmp: Path) -> dict:
    """H's row 15 page (`ev-tnx-two-eras-v4`, tracked), stamped full-stage as the door stamps it."""
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    src = EP / "evidence/objects/ev-tnx-two-eras-v4.series.json"
    shutil.copy(src, tmp / "evidence/objects" / src.name)
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        world = B.world_for_plate(TWO_ERAS, (0, 0, 0), tmp)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


def _push(zoom: float = 1.2, look=None, **kw) -> dict:
    look = look if look is not None else DOTCOM_PEAK
    return dict({"keys": [{"t": 225.5, "zoom": 1.0, "look": look, "ease": "inout"},
                          {"t": 226.7, "zoom": zoom, "look": look, "ease": "inout"}],
                 "attention": "locked"}, **kw)


# ---- (1) the grammar ------------------------------------------------------------------------------------------------

def test_the_chrome_objects_and_the_camera_modes_are_named():
    assert B.CHROME_ELEMENTS == ("title", "sub", "source", "yticks", "xticks", "axis_names", "key", "rail")
    assert B.CHROME_MODES == ("screen", "fit")
    for ok in ("screen", "fit", 0, 0.35, 1, {"camera": "screen"}, {"title": [{"at": 1.0, "scale": 0.5}]},
               {"camera": "fit", "title": [{"at": 1.0, "x": 0.02, "y": 0.03, "scale": 0.45, "dur": 0.6, "ease": "inout"}],
                "yticks": [{"at": 2.0, "x": 0.01, "scale": 0.8}], "xticks": [{"at": 2.0, "y": 0.9}]}):
        assert B.validate_camera(_push(chrome=ok), "p", ASPECT) == [], ok


@pytest.mark.parametrize("bad, why", [
    ("crop", "chrome"), (1.5, "chrome"), (-0.1, "chrome"), (True, "chrome"),
    ({"camera": "zoom"}, "chrome"), ({"headline": [{"at": 1.0}]}, "headline"),
    ({"title": {"at": 1.0}}, "list"), ({"title": [{"x": 0.1}]}, "at"),
    ({"title": [{"at": 1.0, "scale": 0}]}, "scale"), ({"title": [{"at": 1.0, "scale": 0.5, "w": 0.2}]}, "scale"),
    ({"title": [{"at": 1.0, "ease": "bounce"}]}, "ease"), ({"title": [{"at": 1.0, "dur": 0}]}, "dur"),
    ({"title": [{"at": 1.0, "x": 1.4}]}, "stage"), ({"title": [{"at": 1.0, "tilt": 3}]}, "tilt"),
    ({"yticks": [{"at": 1.0, "y": 0.4}]}, "E28"), ({"xticks": [{"at": 1.0, "x": 0.4}]}, "E28"),
    ({"yticks": [{"at": 1.0, "rot": 5}]}, "E28"),
])
def test_a_malformed_chrome_is_refused_by_name(bad, why):
    errs = B.validate_camera(_push(chrome=bad), "p", ASPECT)
    assert errs and any(why in e for e in errs), (bad, errs)


def test_chrome_moves_compile_to_whole_keys_each_inheriting_what_it_does_not_name():
    words = [{"w": "the", "start": 220.0}, {"w": "Fed", "start": 221.4}, {"w": "at", "start": 221.8}, {"w": "six", "start": 224.2}]
    cam = _push(chrome={"camera": "screen", "title": [{"at": "Fed at", "x": 0.02, "y": 0.03, "scale": 0.45, "dur": 0.6},
                                                      {"at": 224.2, "rot": -2}]})
    out, notes = B.compile_chrome(cam, words, (195.82, 242.38), "p")
    ch = out["chrome"]
    assert ch["mode"] == "screen" and ch["k"] == 0
    a, b = ch["moves"]["title"]
    assert set(a) == {"at", "dur", "ease", "x", "y", "scale", "w", "rot"}
    assert a["at"] == 221.4 and a["x"] == 0.02 and a["y"] == 0.03 and a["scale"] == 0.45 and a["rot"] == 0
    assert a["ease"] == B.CHROME_MOVE_EASES[0] and a["w"] is None
    assert (b["x"], b["y"], b["scale"]) == (a["x"], a["y"], a["scale"]) and b["rot"] == -2 and b["dur"] == B.CHROME_MOVE_S
    assert out["keys"] == cam["keys"], "the camera's own keys are not touched"
    with pytest.raises(ValueError, match="not in the take|never said"):
        B.compile_chrome(_push(chrome={"title": [{"at": "never said"}]}), words, (195.82, 242.38), "p")


@pytest.mark.parametrize("moves, why", [
    ([{"at": 190.0, "scale": 0.5}], "before"),                                   # before the page is on screen
    ([{"at": 242.0, "scale": 0.5, "dur": 1.0}], "after"),                        # runs past the page
    ([{"at": 220.0, "scale": 0.5, "dur": 2.0}, {"at": 221.0, "x": 0.1}], "overlap"),
    ([{"at": 222.0, "scale": 0.5}, {"at": 221.0, "x": 0.1}], "ascending"),
])
def test_a_move_that_cannot_be_played_is_refused(moves, why):
    with pytest.raises(ValueError, match=why):
        B.compile_chrome(_push(chrome={"title": moves}), None, (195.82, 242.38), "p")


def test_the_modes_compile_to_their_plane():
    span = (195.82, 242.38)
    assert B.compile_chrome(_push(chrome="screen"), None, span, "p")[0]["chrome"] == {"mode": "screen", "k": 0.0, "moves": {}}
    assert B.compile_chrome(_push(chrome="fit"), None, span, "p")[0]["chrome"] == {"mode": "fit", "k": None, "moves": {}}
    assert B.compile_chrome(_push(chrome=0.4), None, span, "p")[0]["chrome"] == {"mode": "depth", "k": 0.4, "moves": {}}
    moved = B.compile_chrome(_push(chrome={"sub": [{"at": 230.0, "y": 0.9}]}), None, span, "p")[0]["chrome"]
    assert moved["mode"] == "world" and moved["k"] == 1.0 and list(moved["moves"]) == ["sub"]


def test_a_camera_that_names_no_chrome_compiles_untouched():
    for cam in (_push(), {"keys": [], "attention": "landings"}, None):
        out, notes = B.compile_chrome(cam, None, (195.82, 242.38), "p")
        assert out is cam and notes == []


# ---- (3) the reach ------------------------------------------------------------------------------------------------

def test_the_1_2_push_on_the_two_eras_page_is_refused_without_chrome(tmp_path):
    world = _two_eras_world(tmp_path)
    errs = B.camera_zoom_errors(world, [], _push(), TWO_ERAS, ASPECT)
    assert errs and "1.2" in errs[0] and "reachable zoom" in errs[0], errs


@pytest.mark.parametrize("mode", ["screen", "fit"])
def test_with_chrome_the_1_2_push_on_the_two_eras_page_is_reachable_and_the_chrome_warns(tmp_path, mode):
    world = _two_eras_world(tmp_path)
    cam = _push(chrome=mode)
    assert B.camera_zoom_errors(world, [], cam, TWO_ERAS, ASPECT) == [], "the chrome moves; it no longer limits the push"
    errs, notes, out = B.camera_reach(world, [], cam, TWO_ERAS, ASPECT)
    assert errs == [] and [k["zoom"] for k in out["keys"]] == [1.0, 1.2], (errs, out)
    warns = [n for n in notes if n.startswith("WARN")]
    assert warns and any("title" in n and f"chrome: {mode}" in n for n in warns), notes
    assert all("refused" not in n for n in notes)


def test_row_18s_index_page_takes_a_1_2_push_with_chrome(tmp_path):
    sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
    from test_camera_keeps_the_page import _halving_world
    world = _halving_world(tmp_path)
    plate = "ledger:fx-index-concentration-bars:bars"
    look = {"kind": "point", "x": 0.42, "y": 0.5}
    cam = _push(look=look, chrome="screen")
    assert B.camera_zoom_errors(world, [], _push(look=look), plate, ASPECT), "without chrome the page's own type refuses the push"
    assert B.camera_zoom_errors(world, [], cam, plate, ASPECT) == []
    errs, _notes, out = B.camera_reach(world, [], cam, plate, ASPECT)
    assert errs == [] and out["keys"][1]["zoom"] == 1.2


def test_the_claims_own_data_still_limits_the_push(tmp_path):
    world = _two_eras_world(tmp_path)
    wide = {"kind": "region", "x0": 0.05, "y0": 0.2, "x1": 0.95, "y1": 0.7}   # the sentence points at most of the plot
    errs, _n, _o = B.camera_reach(world, [], _push(look=wide, chrome="screen"), TWO_ERAS, ASPECT)
    assert errs and "claim" in errs[0] and "region" in errs[0], errs
    errs, notes, out = B.camera_reach(world, [], _push(look=wide, chrome="screen", reach="clamp"), TWO_ERAS, ASPECT)
    assert errs == [] and 1.0 < out["keys"][1]["zoom"] < 1.2 and any("CLAMPED" in n for n in notes), (out, notes)


def test_a_landing_pull_with_chrome_is_not_refused_by_the_page(tmp_path):
    sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
    from test_camera_keeps_the_page import FED_PLACE, PLATE, _dock, _landings, _world
    errs, _n, _c = B.camera_reach(_world(), [_dock(FED_PLACE)], _landings(), PLATE, ASPECT)
    assert errs, "T26b: without chrome the Fed's pull that cuts the title is refused"
    errs, notes, cam = B.camera_reach(_world(), [_dock(FED_PLACE)], _landings(chrome="screen"), PLATE, ASPECT)
    assert errs == [] and "landing_zoom" not in cam and any(n.startswith("WARN") for n in notes), (errs, notes)


def test_the_compile_loop_compiles_the_chrome_with_the_takes_words():
    import inspect
    src = inspect.getsource(B.main)
    assert "compile_chrome(" in src and 'tl.get("words")' in src[src.index("compile_chrome("):][:200]


# ---- (4) the gate's mirror ----------------------------------------------------------------------------------------

def test_the_gates_plane_is_p58s_law():
    st = {"s": 1.2, "look": (700.0, 300.0), "at": (900.0, 500.0)}
    assert MG.plane_state(st, 1.0) is st
    k0 = MG.plane_state(st, 0.0)
    assert k0["s"] == 1.0 and k0["at"] == k0["look"] == (700.0, 300.0), "k 0 is the frame itself"
    kh = MG.plane_state(st, 0.5)
    assert kh["s"] == pytest.approx(1.1) and kh["at"] == pytest.approx((800.0, 400.0)) and kh["look"] == st["look"]


def test_the_fit_is_the_largest_plane_that_keeps_the_object_whole():
    st = {"s": 1.2, "look": (732.0, 300.0), "at": (732.0, 300.0)}
    title = {"x": 67.0, "y": 44.0, "w": 900.0, "h": 48.0}
    k = MG.chrome_fit_k(title, st, W, H)
    assert 0.0 <= k < 1.0
    fr = MG.camera_frustum(MG.plane_state(st, k), W, H)
    pad = min(MG.CHROME_FIT_PAD_PX, title["x"], title["y"])
    x0 = (title["x"] - fr["x0"]) * (W / (fr["x1"] - fr["x0"]))
    y0 = (title["y"] - fr["y0"]) * (H / (fr["y1"] - fr["y0"]))
    assert x0 >= pad - 1e-6 and y0 >= pad - 1e-6, (k, x0, y0)
    assert MG.chrome_fit_k({"x": 700.0, "y": 280.0, "w": 40.0, "h": 20.0}, st, W, H) == 1.0, "room enough: it rides the world"
    assert MG.chrome_fit_k(title, {"s": 1.0, "look": (960.0, 540.0), "at": (960.0, 540.0)}, W, H) == 1.0


def test_the_fit_never_parks_chrome_on_the_anchored_caption():
    band = MG._chrome_band({"world": {"page": {"caption": "anchor"}}}, ASPECT)
    assert band == (878.0, 960.0) and MG._chrome_band({"world": {"page": {}}}, ASPECT) is None
    xticks = {"x": 150.0, "y": 830.0, "w": 1200.0, "h": 36.0}            # the date row, standing above the strip
    st = {"s": 1.2, "look": (572.0, 280.0), "at": (572.0, 280.0)}        # the push onto the dot-com peak
    free, kept = MG.chrome_fit_k(xticks, st, W, H), MG.chrome_fit_k(xticks, st, W, H, band=band)
    assert kept < free, (kept, free)
    fr = MG.camera_frustum(MG.plane_state(st, kept), W, H)
    foot = (xticks["y"] + xticks["h"] - fr["y0"]) * (H / (fr["y1"] - fr["y0"]))
    assert foot <= band[0] - min(MG.CHROME_FIT_PAD_PX, band[0] - (xticks["y"] + xticks["h"])) + 1e-6, foot


def _crop_scene(chrome=None) -> dict:
    cam = {"keys": [{"t": 10.0, "zoom": 1.0, "look": [0.4, 0.3], "ease": "inout"},
                    {"t": 11.0, "zoom": 1.2, "look": [0.4, 0.3], "ease": "inout"}], "attention": "locked"}
    if chrome is not None:
        cam["chrome"] = chrome
    return {"scene_id": "s01", "span": [0.0, 30.0], "camera": cam, "species": [], "docks": [],
            "world": {"kind": "ledger", "page": {}}}


PROBE_TEXTS = {"title": ({"title": [40, 30, 1200, 60]}, []),
               "tick": ({}, [{"role": "tick", "text": "6%", "box": [100, 220, 50, 26]}]),
               "val": ({}, [{"role": "val", "text": "6.7%", "box": [1700, 400, 90, 30]}])}


def _probe_doc(which: str = "title") -> dict:
    page, labels = PROBE_TEXTS[which]   # one text per doc: M43 prints one line per landing (`_dedupe`)
    return {"instants": [{"t": 10.5, "camera": {"zoom": 1.0}, "page": page, "labels": labels}]}


def test_m43_measures_the_chrome_on_its_own_plane():
    for which, name in (("title", "page.title"), ("tick", "tick:6%"), ("val", "val:6.7%")):
        fails, measured, _boxes = MG._crop_faults(_probe_doc(which), [_crop_scene()], ASPECT)
        assert measured == 1 and len(fails) == 1 and name in fails[0], (which, fails)
    for mode in ({"mode": "screen", "k": 0.0, "moves": {}}, {"mode": "fit", "k": None, "moves": {}},
                 {"mode": "depth", "k": 0.05, "moves": {}}):
        for which in ("title", "tick"):
            fails, measured, _boxes = MG._crop_faults(_probe_doc(which), [_crop_scene(mode)], ASPECT)
            assert measured == 1 and fails == [], (mode, which, fails)
        fails, _m, _b = MG._crop_faults(_probe_doc("val"), [_crop_scene(mode)], ASPECT)
        assert len(fails) == 1 and "val:6.7%" in fails[0], "a data label is not chrome: the plot's frame still judges it"
    fails, _m, _b = MG._crop_faults(_probe_doc("title"), [_crop_scene({"mode": "depth", "k": 0.8, "moves": {}})], ASPECT)
    assert len(fails) == 1 and "page.title" in fails[0], "a plane near the plot's still cuts what it cuts"


def test_a_scene_with_no_chrome_gates_as_before():
    doc, sc = _probe_doc(), _crop_scene()
    assert MG._crop_faults(doc, [sc], ASPECT) == MG._crop_faults(doc, [copy.deepcopy(sc)], ASPECT)
    assert MG.chrome_of(sc) is None and MG.chrome_of(_crop_scene({"mode": "screen", "k": 0.0, "moves": {}}))["k"] == 0.0


# ---- (2) (4) (5) the player ---------------------------------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


LOOK = {"kind": "point", "x": 0.62, "y": 0.4}   # a POINT: a datum look resolves differently on a cold seek than in play, chrome or not (reported)
T0, T1, HELD = 20.0, 21.2, 22.5          # the push starts, lands, holds (the divergence page is built by 20 s)
MOVE_AT, MOVE_DUR = 17.0, 0.8             # the title shrinks to its corner tag before the push


def _timeline(chrome=None, keys=True) -> tuple[dict, dict]:
    tl, uris, _t, _asp = RB.load_surface(SURFACE)
    tl = copy.deepcopy(tl)
    sc = tl["scenes"][0]
    sc["world"]["page"].update(full_stage=True, caption="anchor")   # the long form's page: its caption anchored (the fit keeps off it)
    cam = {"keys": [{"t": T0, "zoom": 1.0, "look": LOOK, "ease": "inout"},
                    {"t": T1, "zoom": 1.2, "look": LOOK, "ease": "inout"}] if keys else [], "attention": "locked"}
    if chrome is not None:
        cam["chrome"] = chrome
    sc["camera"] = cam
    tl["kinetics"] = dict(tl.get("kinetics") or {}, camera=True)
    return tl, uris


READ = """t => {
  const s = document.getElementById('stage').getBoundingClientRect();
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - s.x, r.y - s.y, r.width, r.height]; };
  const vis = (e) => { for (let q = e; q && q !== document.body; q = q.parentNode) { const cs = q.nodeType === 1 ? getComputedStyle(q) : null;
    if (cs && (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0)) return false; } return true; };
  const world = [...document.querySelectorAll('.world.ledger')].find((w) => w.__lp) || null;
  const lp = world && world.__lp;
  const page = lp ? lp.page : document;
  const one = (sel) => { const e = page.querySelector(sel); return e ? R(e) : null; };
  const S = lp ? ((lp.states && lp.states[lp.active | 0]) || lp) : null;
  const ticks = S ? (S.marks || []).filter((m) => m.role === 'ylabel').map((m) => {
    const g = (S.marks || []).find((q) => q.role === 'tick' && q.geom && q.geom.v === m.geom.v);
    return { v: m.geom.v, box: R(m.el), shown: vis(m.el), grid: g ? R(g.el) : null }; }) : [];
  return { cam: window.__camera(t), chrome: window.__chrome ? window.__chrome(t) : null,
           title: one('.lp-title'), sub: one('.lp-sub'), src: one('.lp-src'), ticks,
           titleXf: page.querySelector('.lp-title') ? page.querySelector('.lp-title').style.transform : null,
           wrappers: page.querySelectorAll('.lp-chrome-w').length };
}"""


def _run(tl: dict, uris: dict, times, cold: float | None = None) -> dict:
    from playwright.sync_api import sync_playwright
    out = {"reads": {}, "png": {}}
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        try:
            with tempfile.TemporaryDirectory() as td:
                html = Path(td) / "chrome.html"
                html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
                srv, port = RB.serve(html.parent)
                try:
                    for seq, label in ((list(times), "play"), ([cold] if cold is not None else [], "cold")):
                        if not seq:
                            continue
                        page = br.new_context(viewport={"width": W, "height": H}).new_page()
                        page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=180000)
                        RB.prepare_page(page, W, H)
                        for t in seq:
                            RB.frame_png(page, t, (W, H))   # the harness's settle: an async decode can land after the first capture
                            page.wait_for_timeout(150)
                            png = RB.frame_png(page, t, (W, H))
                            key = t if label == "play" else ("cold", t)
                            out["png"][key] = hashlib.sha256(png).hexdigest()
                            out["reads"][key] = page.evaluate(READ, t)
                        page.context.close()
                finally:
                    srv.shutdown()
        finally:
            br.close()
    return out


def _inside(box, pad=0.0) -> bool:
    x, y, w, h = box
    return x >= pad - 0.5 and y >= pad - 0.5 and x + w <= W - pad + 0.5 and y + h <= H - pad + 0.5


needs_chromium = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


@needs_chromium
def test_screen_chrome_stands_still_while_the_plot_is_pushed():
    base = _run(*_timeline(keys=False), [HELD])["reads"][HELD]
    pushed = _run(*_timeline(chrome={"mode": "screen", "k": 0.0, "moves": {}}), [HELD])["reads"][HELD]
    plain = _run(*_timeline(), [HELD])["reads"][HELD]
    assert pushed["cam"]["zoom"] == pytest.approx(1.2, abs=1e-4)
    for k in ("title", "sub", "src"):
        assert pushed[k] == pytest.approx(base[k], abs=0.6), (k, pushed[k], base[k])
        assert plain[k] != pytest.approx(base[k], abs=0.6), f"without chrome the {k} rides the push (the frame's old answer)"
    shown = [tk for tk in pushed["ticks"] if tk["shown"]]
    assert shown, pushed["ticks"]
    by_v = {tk["v"]: tk for tk in base["ticks"]}
    for tk in shown:
        assert _inside(tk["box"]), tk
        rest = by_v[tk["v"]]["box"]
        assert tk["box"][0] + tk["box"][2] == pytest.approx(rest[0] + rest[2], abs=1.0), "the column is pinned to the frame"
        gy = tk["grid"][1] + tk["grid"][3] / 2
        assert abs((tk["box"][1] + tk["box"][3] / 2) - gy) < 0.6 * tk["box"][3], "... and every label stays on its gridline (E28)"
    for tk in pushed["ticks"]:
        if not tk["shown"]:
            gy = tk["grid"][1] + tk["grid"][3] / 2
            assert gy < tk["box"][3] or gy > H - tk["box"][3], ("a label is hidden only when its gridline has left", tk)


@needs_chromium
def test_fit_chrome_keeps_every_object_whole_and_the_gate_reads_the_same_k():
    got = _run(*_timeline(chrome={"mode": "fit", "k": None, "moves": {}}), [HELD])["reads"][HELD]
    ch = got["chrome"]
    assert ch and ch["mode"] == "fit", ch
    st = {"s": got["cam"]["zoom"], "look": tuple(got["cam"]["look"]), "at": tuple(got["cam"]["at"])}
    for name in ("title", "sub", "source"):
        e = ch["objects"][name]
        assert 0.0 <= e["k"] <= 1.0 and _inside(e["box"]), (name, e)
        rest = dict(zip("xywh", e["rest"]))
        band = MG._chrome_band(_timeline()[0]["scenes"][0], ASPECT)
        assert e["k"] == pytest.approx(MG.chrome_fit_k(rest, st, W, H, band=band), abs=1e-3), (name, e["k"])
    assert _inside(got["title"]) and _inside(got["src"])


@needs_chromium
def test_the_title_shrinks_to_a_corner_tag_on_its_word_and_a_cold_seek_agrees():
    moves = {"title": [{"at": MOVE_AT, "dur": MOVE_DUR, "ease": "inout", "x": 0.02, "y": 0.03, "scale": 0.45, "w": None, "rot": 0}]}
    mid = MOVE_AT + MOVE_DUR / 2
    tl, uris = _timeline(chrome={"mode": "screen", "k": 0.0, "moves": moves})
    got = _run(tl, uris, [MOVE_AT - 0.5, mid, MOVE_AT + MOVE_DUR + 0.5, HELD], cold=HELD)
    before, during, after, held = (got["reads"][t] for t in (MOVE_AT - 0.5, mid, MOVE_AT + MOVE_DUR + 0.5, HELD))
    tag = (0.02 * W, 0.03 * H)
    assert after["title"][0] == pytest.approx(tag[0], abs=1.0) and after["title"][1] == pytest.approx(tag[1], abs=1.0)
    assert after["title"][2] == pytest.approx(0.45 * before["title"][2], rel=0.02)
    assert before["title"][2] > during["title"][2] > after["title"][2], "the title rescales on its own clock"
    still = _run(*_timeline(chrome={"mode": "screen", "k": 0.0, "moves": moves}, keys=False), [HELD])["reads"][HELD]
    assert held["cam"]["zoom"] == pytest.approx(1.2, abs=1e-4) and still["cam"]["zoom"] == 1.0
    assert held["title"] == pytest.approx(still["title"], abs=0.6), "the tag rides the camera: the push does not move it"
    assert got["png"][("cold", HELD)] == got["png"][HELD], "a cold seek lands the frame forward play lands"


@needs_chromium
def test_a_camera_with_no_chrome_writes_nothing_on_the_chrome():
    got = _run(*_timeline(), [HELD])["reads"][HELD]
    assert got["titleXf"] == "" and got["wrappers"] == 0 and got["chrome"] is None


# ---- P69 T8e (5): A PANEL'S OWN SUB AND TICKS ARE CHROME, ADDRESSED BY PANEL INDEX ---------------------------------------
# Row 21 (T29): camera 4's 1.2 push onto the hynix tip (at the line panel's right edge) cut the panel's OWN sub ("hare
# price vs its own operating profit") and its y ticks for ~5 s under `chrome: fit` - T26f's chrome moved the PAGE's
# objects, and a panel's sub and ticks live inside the panel's svg. Now each panel's sub, y ticks and x ticks are chrome
# objects too: `chrome: fit` keeps them whole like the page's own, and a row may MOVE one by its panel index -
# `sub@<i>`, `yticks@<i>`, `xticks@<i>` (the tick locks of E28 kept).

def test_a_panels_objects_are_named_by_its_index_and_keep_the_tick_locks_T8e():
    assert B.CHROME_PANEL_ELEMENTS == ("sub", "yticks", "xticks")
    ok = {"camera": "fit", "sub@0": [{"at": 1.0, "x": 0.02, "y": 0.2, "scale": 0.8}], "yticks@1": [{"at": 2.0, "x": 0.01}],
          "xticks@3": [{"at": 2.0, "y": 0.9}]}
    assert B.validate_camera(_push(chrome=ok), "p", ASPECT) == [], ok
    for bad, why in (({"yticks@0": [{"at": 1.0, "y": 0.4}]}, "E28"), ({"sub@4": [{"at": 1.0}]}, "sub@4"),
                     ({"title@0": [{"at": 1.0}]}, "title@0"), ({"sub@x": [{"at": 1.0}]}, "sub@x")):
        errs = B.validate_camera(_push(chrome=bad), "p", ASPECT)
        assert errs and any(why in e for e in errs), (bad, errs)


def _panels_world(n: int = 2) -> dict:
    series = LPG.load_series(EP / "evidence/objects/ev-tnx-two-eras-v3.series.json")
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        return {"kind": B.SPECIES_LEDGER, "page": B.stamp_full_stage(LPG.build_spec(series, "line", None, "right"))}
    finally:
        B.ASPECT = saved


def test_a_panel_move_compiles_by_its_index_and_a_page_without_that_panel_refuses_it_T8e():
    span = (195.82, 242.38)
    cam = _push(chrome={"camera": "fit", "sub@1": [{"at": 230.0, "x": 0.55, "y": 0.2}]})
    ch = B.compile_chrome(cam, None, span, "p", _panels_world(), ASPECT)[0]["chrome"]
    assert ch["mode"] == "fit" and list(ch["moves"]) == ["sub@1"] and ch["moves"]["sub@1"][0]["x"] == 0.55
    with pytest.raises(ValueError, match="panel 2"):
        B.compile_chrome(_push(chrome={"sub@2": [{"at": 230.0, "y": 0.2}]}), None, span, "p", _panels_world(), ASPECT)
    world = _two_eras_world_plain()
    with pytest.raises(ValueError, match="PANELS page"):
        B.compile_chrome(_push(chrome={"sub@0": [{"at": 230.0, "y": 0.2}]}), None, span, "p", world, ASPECT)


def _two_eras_world_plain() -> dict:
    series = LPG.load_series(EP / "evidence/objects/ev-tnx-two-eras-v4.series.json")
    return {"kind": B.SPECIES_LEDGER, "page": LPG.build_spec(series, "line")}


def _row21_page() -> dict:
    """Row 21's shape, as `test_ledger_panels` draws it: the line panel ALONE from the page's first frame (a longform
    panels page), the two bars panels hidden - its tip at the plot's right edge."""
    import test_ledger_panels as TLP
    page = TLP._longform_panels(TLP._row21_shape())
    (fs,) = TLP._focus_states(3, [(0.0, 0.05, TLP.LINE_ALONE)])
    return page, fs


TIP = {"kind": "point", "x": 0.86, "y": 0.49}   # row 21's look: the tip's rest (1652, 532) px, a POINT (seek-safe)
PANEL_READ = """t => {
  const s = document.getElementById('stage').getBoundingClientRect(), W = document.getElementById('wB').__lp;
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - s.x, r.y - s.y, r.width, r.height]; };
  const vis = (e) => { for (let q = e; q && q !== document.body; q = q.parentNode) { const cs = q.nodeType === 1 ? getComputedStyle(q) : null;
    if (cs && (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0)) return false; } return true; };
  const S = W.panels[0], sub = S.marks.find((m) => m.role === 'axislabel');
  return { cam: window.__camera(t), chrome: window.__chrome ? window.__chrome(t) : null, sub: R(sub.el), subShown: vis(sub.el),
           ticks: S.marks.filter((m) => m.role === 'ylabel').map((m) => ({ box: R(m.el), shown: vis(m.el) })) }; }"""


def _panel_run(chrome, times, cold=None):
    import measure_page_boxes as MP
    page, fs = _row21_page()
    tl = MP._timeline(page, ASPECT)
    tl["runtime_s"] = 40.0
    sc = tl["scenes"][0]
    sc["span"], sc["species"] = [0.0, 40.0], [fs]
    cam = {"keys": [{"t": T0, "zoom": 1.0, "look": TIP, "ease": "inout"}, {"t": T1, "zoom": 1.2, "look": TIP, "ease": "inout"}],
           "attention": "locked"}
    if chrome is not None:
        cam["chrome"] = chrome
    sc["camera"] = cam
    tl["kinetics"] = dict(tl.get("kinetics") or {}, camera=True)
    uris = {"__audio__": MP._silence(), **B.longform_assets(tl)}
    global READ
    saved, READ = READ, PANEL_READ
    try:
        return _run(tl, uris, times, cold=cold)
    finally:
        READ = saved


@needs_chromium
def test_fit_chrome_keeps_the_focused_panels_sub_and_ticks_whole_and_a_cold_seek_agrees_T8e():
    """The row-21 push (1.2 onto the tip at the line panel's right edge): without chrome the panel's sub runs off the
    frame's left edge; under `fit` it stands whole, every y tick it shows stands inside the frame (one whose gridline has
    left is hidden whole), the report names each panel object by its index - and a cold seek lands the same frame."""
    plain = _panel_run(None, [HELD])["reads"][HELD]
    assert plain["cam"]["zoom"] == pytest.approx(1.2, abs=1e-4)
    assert plain["sub"][0] < 0, ("the push cuts the panel's sub without chrome (row 21's frame)", plain["sub"])
    got = _panel_run({"mode": "fit", "k": None, "moves": {}}, [HELD], cold=HELD)
    fit = got["reads"][HELD]
    assert fit["subShown"] and _inside(fit["sub"], pad=MG.CHROME_FIT_PAD_PX - 1), fit["sub"]
    shown = [tk for tk in fit["ticks"] if tk["shown"]]
    assert shown and all(_inside(tk["box"]) for tk in shown), fit["ticks"]
    objs = fit["chrome"]["objects"]
    assert {"sub@0", "yticks@0"} <= set(objs) and all(0.0 <= objs[k]["k"] <= 1.0 for k in ("sub@0", "yticks@0")), objs
    assert got["png"][("cold", HELD)] == got["png"][HELD], "a cold seek lands the frame forward play lands"


@needs_chromium
def test_a_panels_sub_moves_on_its_own_index_T8e():
    moves = {"sub@0": [{"at": MOVE_AT, "dur": MOVE_DUR, "ease": "inout", "x": 0.04, "y": 0.2, "scale": 0.8, "w": None, "rot": 0}]}
    got = _panel_run({"mode": "screen", "k": 0.0, "moves": moves}, [MOVE_AT - 0.5, MOVE_AT + MOVE_DUR + 0.3])["reads"]
    before, after = got[MOVE_AT - 0.5], got[MOVE_AT + MOVE_DUR + 0.3]
    assert after["sub"][0] == pytest.approx(0.04 * W, abs=1.5) and after["sub"][1] == pytest.approx(0.2 * H, abs=1.5), after["sub"]
    assert after["sub"][2] == pytest.approx(0.8 * before["sub"][2], rel=0.03)
