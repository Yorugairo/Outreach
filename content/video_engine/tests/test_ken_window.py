"""P72 T25 (R26-165, R26-164) - THE PLATE'S MOVES TAKE A WINDOW.

Two rows, one rule (E99 s65: "ken burns + drift gives us directionally controlled motion, which can matter for peoples
perception of the story"; s84: the long form's plate life is Ken Burns alone):

- R26-165, THE KEN'S WINDOW. A shot row's ken was `(scale, x, y)` on the scene's own 0 -> 1 clock, so a lean could not
  start on a word (P61 T14c: B's zoom matched A's 1.0 -> 1.14 but not its timing). A row may now write
  `(scale, x, y, t0, t1)` - the lean's window in episode seconds, like the authored camera key: still until `t0`, the
  same linear lean across `[t0, t1]`, held after `t1`. A three-tuple is the dict it always wrote; any other arity, a
  window outside the row, backwards, on no push, or on a vector map is REFUSED by name (s106: a silent drop is neither
  advice nor refusal - at the base a five-tuple was truncated to its first three).
- R26-164, THE LAYERED PLATE'S DRIFT. Each plane of a layered plate took its share k of ONE free Lissajous walk, so the
  planes slid against each other in a direction nothing on screen gave them (s65: "parallax + drift can read as random
  motion"). The drift on a layered plate now FOLLOWS THE CAMERA: the walk projected onto the camera's own displacement of
  the stage, on the camera's side, never against it - and with no camera direction it is OFF, and the compiler says so
  by name. A flat plate's bare drift is untouched.

The engine is read on the served player (served_player, the one guarded Playwright opener).
"""
from __future__ import annotations

import io
import json
import math
import re
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
FPS = 24
FRAME = 1.0 / FPS
KEN = (0.06, 20, -12)
T0, T1 = 4.0, 7.0
SPAN = (0.0, 10.0)
PLATE_WORLD = {"asset_id": "plate-ken", "sha256": "0" * 64, "ken_burns": {"scale": 0.06, "x": 20, "y": -12}}


# ---- R26-165: the grammar (pure) -------------------------------------------------------------------------------


def test_a_ken_of_three_is_the_dict_it_always_wrote():
    assert B.ken_window_errors(KEN, SPAN, PLATE_WORLD) == []
    kb = {"scale": 0.06, "x": 20, "y": -12}
    out = B.ken_burns_windowed(kb, KEN)
    assert out == {"scale": 0.06, "x": 20, "y": -12} and list(out) == ["scale", "x", "y"], out
    assert B.ken_window_of(KEN) is None and B.ken_window_of((0, 0, 0)) is None


def test_a_windowed_ken_writes_its_window_after_the_three_it_always_wrote():
    ken = KEN + (T0, T1)
    assert B.ken_window_errors(ken, SPAN, PLATE_WORLD) == []
    assert B.ken_window_of(ken) == (T0, T1)
    kb = {"scale": 0.06, "x": 20, "y": -12}
    out = B.ken_burns_windowed(kb, ken)
    assert out == {"scale": 0.06, "x": 20, "y": -12, "t0": 4.0, "t1": 7.0} and kb == {"scale": 0.06, "x": 20, "y": -12}, \
        "a new dict - the world's own is not mutated"
    assert B.KEN_WINDOW_ARITY == 5


@pytest.mark.parametrize("ken, world, needle", [
    ((0.06, 90, 4.0, 7.0), PLATE_WORLD, "ken_burns takes (scale, x, y) or (scale, x, y, t0, t1) - got 4 values"),
    (KEN + (4.0, 7.0, 1.0), PLATE_WORLD, "ken_burns takes (scale, x, y) or (scale, x, y, t0, t1) - got 6 values"),
    (KEN + ("4", 7.0), PLATE_WORLD, "ken_burns window: t0 must be a finite number of episode seconds"),
    (KEN + (True, 7.0), PLATE_WORLD, "ken_burns window: t0 must be a finite number of episode seconds"),
    (KEN + (4.0, float("nan")), PLATE_WORLD, "ken_burns window: t1 must be a finite number of episode seconds"),
    (KEN + (7.0, 4.0), PLATE_WORLD, "ken_burns window 7.00-4.00s runs backwards"),
    (KEN + (4.0, 4.0), PLATE_WORLD, "ken_burns window 4.00-4.00s runs backwards"),
    (KEN + (-1.0, 4.0), PLATE_WORLD, "ken_burns window -1.00-4.00s runs past its row (0.00-10.00s)"),
    (KEN + (4.0, 10.5), PLATE_WORLD, "ken_burns window 4.00-10.50s runs past its row (0.00-10.00s)"),
    ((0, 0, 0, 4.0, 7.0), PLATE_WORLD, "ken_burns window 4.00-7.00s on no push"),
    ((0, 12, -4, 4.0, 7.0), {"kind": "ledger", "page": {}}, "ken_burns window 4.00-7.00s on no push"),
    ((0.02, 0, 0, 4.0, 7.0), {"kind": "vecmap"}, "a vector map takes no Ken Burns"),
])
def test_a_malformed_ken_is_refused_by_name(ken, world, needle):
    errs = B.ken_window_errors(ken, SPAN, world)
    assert any(needle in e for e in errs), errs


def test_a_page_takes_its_window_on_its_scale():
    assert B.ken_window_errors((0.03, 0, 0, 4.0, 7.0), SPAN, {"kind": "ledger", "page": {}}) == []


class _PastTheWorld(Exception):
    """Raised once the row path has built the scene's world - the test needs nothing after."""


def _one_row_bed(tmp_path, monkeypatch, ken):
    """`main()` on a one-row bed (the `test_chip_stamp_arrival` door), stopped once the scene's world is final."""
    import build_golden_sources as BGS
    ep, build = tmp_path / "ep", tmp_path / "ep" / "build"
    (ep / "evidence/objects").mkdir(parents=True)
    (build / "audio").mkdir(parents=True)
    shutil.copy2(BGS.SERIES, ep / "evidence/objects" / "ev-row-path.series.json")
    (build / "audio/episode.mp3").write_bytes(b"")
    (build / "timeline.json").write_text(json.dumps({"runtime_s": 30.0, "words": []}), encoding="utf-8")
    (build / "caption-pages.json").write_text("[]", encoding="utf-8")
    row = (0.0, 30.0, "ledger:ev-row-path:line", ken, [], None, [])
    (ep / "SHOT-ROW-PATH.py").write_text("W = " + repr([row]) + "\n", encoding="utf-8")
    seen: dict = {}

    def stop(world, row_species, a):
        seen["world"] = world
        raise _PastTheWorld

    for name, value in (("BUILD", build), ("EP", ep), ("SHOT_TABLE_FILE", "SHOT-ROW-PATH.py"), ("ASPECT", "16:9"),
                        ("page_build_windows", stop)):
        monkeypatch.setattr(B, name, value)
    return seen


def test_a_row_COMPILES_its_window_onto_the_world(tmp_path, monkeypatch):
    seen = _one_row_bed(tmp_path, monkeypatch, (0.03, 0, 0, 12.0, 16.0))
    with pytest.raises(_PastTheWorld):
        B.main()
    assert seen["world"]["ken_burns"] == {"scale": 0.03, "x": 0, "y": 0, "t0": 12.0, "t1": 16.0}, seen["world"]["ken_burns"]


def test_a_row_without_a_window_compiles_the_ken_it_always_did(tmp_path, monkeypatch):
    seen = _one_row_bed(tmp_path, monkeypatch, (0.03, 0, 0))
    with pytest.raises(_PastTheWorld):
        B.main()
    assert seen["world"]["ken_burns"] == {"scale": 0.03, "x": 0, "y": 0}


def test_a_row_with_a_malformed_window_FAILS_by_name(tmp_path, monkeypatch):
    _one_row_bed(tmp_path, monkeypatch, (0.03, 0, 0, 12.0, 31.0))
    with pytest.raises(SystemExit) as exc:
        B.main()
    msg = str(exc.value)
    assert "shot row 1 (0.0-30.0s)" in msg and "ken_burns window 12.00-31.00s runs past its row (0.00-30.00s)" in msg, msg


# ---- R26-165: the engine's windowed clock, served ---------------------------------------------------------------


_WORLD_TR = """t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true}));
  const w = [...document.querySelectorAll('.world')].find(e => e.style.backgroundImage && e.style.backgroundImage !== 'none');
  return w ? w.style.transform : null; }"""


FREEZE = {"kind": "freeze", "at": 5.0, "dur": 0.8, "target": {"kind": "point", "x": 0.5, "y": 0.5}}


def _ken_timeline(kb: dict, species: tuple = ()) -> tuple[dict, dict]:
    import build_golden_sources as BGS
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-ken", "sha256": "0" * 64, "ken_burns": kb},
               "exit": "cut", "span": list(SPAN), "docks": [], "species": [dict(s) for s in species]}]
    uris = BGS._base_uris()
    uris["plate-ken"] = B.data_uri(BGS.DOCK_PLATE)
    tl = BGS._timeline("T25: a windowed ken", scenes, {}, None)
    tl["runtime_s"] = SPAN[1]
    tl["captions"], tl["caption_pages"] = [], []
    tl["kinetics"] = {}   # no idle: the ken is the only thing that moves the plate
    return tl, uris


@pytest.fixture(scope="module")
def ken_reads():
    """The world's transform and the stage frame at the instants the acceptance names, windowed and not."""
    import render_baseline as RB
    ts = [3.0, T0 - 2 * FRAME, T0 - FRAME, T0, T0 + FRAME, 5.0, 5.4, 5.5, 5.8, T1 - FRAME, T1, T1 + FRAME, 9.0]
    out = {}
    win = {"scale": 0.06, "x": 20, "y": -12, "t0": T0, "t1": T1}
    with tempfile.TemporaryDirectory() as td:
        for tag, kb, species in (("win", win, ()), ("whole", {"scale": 0.06, "x": 20, "y": -12}, ()),
                                 ("freeze", win, (FREEZE,))):
            tl, uris = _ken_timeline(kb, species)
            html = Path(td) / f"ken-{tag}.html"
            html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
            with SP.served(html, 1920, 1080) as (page, errs):
                trs = {t: page.evaluate(_WORLD_TR, t) for t in ts}
                pngs = {t: RB.frame_png(page, t, (1920, 1080)) for t in ts}
                assert not errs, errs
            out[tag] = (trs, pngs)
    return out


def _rest(tr: str) -> str:
    return tr.split("translateX(")[1]


def test_a_windowed_ken_holds_still_until_its_word_and_moves_on_the_next_frame(ken_reads):
    trs, pngs = ken_reads["win"]
    before = {_rest(trs[t]) for t in (3.0, T0 - 2 * FRAME, T0 - FRAME, T0)}
    assert len(before) == 1 and "scale(1)" in trs[T0] and "translate(0px, 0px)" in trs[T0], before
    assert pngs[T0 - FRAME] == pngs[T0] == pngs[3.0], "still until t0"
    assert _rest(trs[T0 + FRAME]) != _rest(trs[T0]), "the lean starts on its word: the first moving frame is t0 + 1 frame"
    assert pngs[T0 + FRAME] != pngs[T0], "... in PIXELS, not only in the string"


def test_a_windowed_ken_holds_its_pose_after_t1(ken_reads):
    trs, pngs = ken_reads["win"]
    held = {_rest(trs[t]) for t in (T1, T1 + FRAME, 9.0)}
    assert len(held) == 1 and "scale(1.06)" in trs[T1] and "translate(20px, -12px)" in trs[T1], held
    assert pngs[T1] == pngs[T1 + FRAME] == pngs[9.0], "still after t1"
    assert _rest(trs[T1 - FRAME]) != _rest(trs[T1]), "still leaning on the frame before t1"


def _lean(tr: str) -> tuple[float, float, float]:
    """(zoom, x, y) of the world's rest term - the ken's pose, read back off the element."""
    rest = _rest(tr)
    z = float(re.search(r"scale\(([\d.]+)\)", rest).group(1))
    m = re.search(r"translate\((-?[\d.]+)px, (-?[\d.]+)px\)", rest)
    return z, float(m.group(1)), float(m.group(2))


def _assert_lean(tr: str, p: float, t: float) -> None:
    z, x, y = _lean(tr)
    assert abs(z - (1 + p * 0.06)) < 1e-4 and abs(x - p * 20) < 0.06 and abs(y + p * 12) < 0.06, (t, p, tr)


def test_a_windowed_ken_is_linear_across_its_window(ken_reads):
    trs, _ = ken_reads["win"]
    for t in (T0 + FRAME, 5.5, T1 - FRAME):
        _assert_lean(trs[t], (t - T0) / (T1 - T0), t)


def test_a_freeze_beat_inside_the_window_holds_the_lean_and_it_still_lands_on_t1(ken_reads):
    """P69 T49's freeze holds every life on the LIFE clock; the window is normalised by its own life length, so the lean
    stops for the beat (5.0-5.8) and still arrives whole at t1."""
    trs, _ = ken_reads["freeze"]
    assert _lean(trs[5.0]) == _lean(trs[5.4]) == _lean(trs[5.8]), (trs[5.0], trs[5.4], trs[5.8])
    live = (T1 - T0) - FREEZE["dur"]
    _assert_lean(trs[5.0], (5.0 - T0) / live, 5.0)
    _assert_lean(trs[T1], 1.0, T1)
    assert _lean(trs[T1 - FRAME])[0] < _lean(trs[T1])[0], "still leaning on the frame before t1"


def test_a_ken_with_no_window_runs_the_scene_clock_it_always_ran(ken_reads):
    trs, _ = ken_reads["whole"]
    for t in (3.0, T0, 5.5, T1, 9.0):
        _assert_lean(trs[t], (t - SPAN[0]) / (SPAN[1] - SPAN[0]), t)


def test_the_seal_ground_reads_the_same_ken_clock_as_the_paint():
    """P72 T11's `worldXfAt` and paint's pose read ONE ken clock - since P72 T46b (R26-361 (c)) through one function,
    `worldPoseAt`, which both call."""
    src = ENGINE.read_text(encoding="utf-8")
    body = src[src.index("const worldXfAt = "):src.index("const cssMatrix = ")]
    assert "worldPoseAt(scene, t0)" in body, "worldXfAt reads the pose paint writes"
    pose = src[src.index("const worldPoseAt = "):src.index("const worldXfAt = ")]
    assert "kenProgress(scene, t)" in pose, "... and the pose reads the ken through the shared windowed clock"
    paint = src[src.index("const paint = (el, scene, dx = 0) => {"):src.index("paintPlanes(el, plies, camXfNow")]
    assert "worldPoseAt(scene, t, dx)" in paint
    clock = src[src.index("const kenProgress = "):src.index("const worldXfAt = ")]
    assert src.count("clamp01((lifeFrom(scene.span[0], t") == 1 and "clamp01((lifeFrom(scene.span[0], t" in clock, \
        "the scene's own ken clock lives in kenProgress alone - no second, unwindowed copy is left"


# ---- R26-164: a layered plate's drift follows the camera or is off --------------------------------------------


_PLANES = r"""t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true}));
  const el = [...document.querySelectorAll('.world')].find(e => e.querySelector('.wly')); if (!el) return null;
  const cam = (el.dataset.worldPose || '').split('translateX(')[0].trim();
  const c = new DOMMatrix(cam || 'matrix(1,0,0,1,0,0)').transformPoint(new DOMPoint(0, 0));
  return { D: [c.x, c.y], planes: [...el.querySelectorAll('.wly')].map(d => {
    const ms = [...(d.style.transform.split('translateX(')[1] || '').matchAll(/translate\((-?[\d.e]+)px,\s*(-?[\d.e]+)px\)/g)];
    return ms.length > 1 ? [+ms[ms.length - 1][1], +ms[ms.length - 1][2]] : [0, 0]; }) }; }"""


@pytest.fixture(scope="module")
def alive_planes():
    import render_baseline as RB
    tl, uris, _t, _aspect = RB.load_surface("plate-alive")
    ts = [round(5.0 + 0.25 * i, 2) for i in range(17)]   # 5.0 .. 9.0: before, across and after the focus zoom (6.0-8.0)
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "plate-alive.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SP.served(html, 1920, 1080) as (page, errs):
            reads = {t: page.evaluate(_PLANES, t) for t in ts}
            assert not errs, errs
    return reads


def test_a_layered_plates_drift_never_runs_against_or_across_the_camera(alive_planes):
    moving = 0
    for t, r in alive_planes.items():
        D = r["D"]
        nD = math.hypot(*D)
        for dx, dy in r["planes"]:
            nd = math.hypot(dx, dy)
            if nd == 0:
                continue
            assert nD > 0.5, f"t={t}: a plane drifts ({dx}, {dy}) with no camera direction - the drift is OFF there"
            assert dx * D[0] + dy * D[1] > 0, f"t={t}: a plane drifts ({dx}, {dy}) AGAINST the camera {D}"
            assert abs(dx * D[1] - dy * D[0]) <= 0.02 * nd * nD + 0.02 * nD, \
                f"t={t}: a plane drifts ({dx}, {dy}) ACROSS the camera {D} - it must ride the camera's line"
            moving += 1
    assert moving >= 12, f"the drift still paints while the camera moves ({moving} plane reads)"


def test_a_layered_plates_drift_is_off_where_the_camera_gives_no_direction(alive_planes):
    for t in (5.0, 5.5, 5.75, 8.5, 9.0):
        assert math.hypot(*alive_planes[t]["D"]) < 0.5, (t, alive_planes[t]["D"])
        assert all(p == [0, 0] for p in alive_planes[t]["planes"]), (t, alive_planes[t]["planes"])


def test_the_planes_move_one_way_the_nearer_plane_further(alive_planes):
    r = alive_planes[7.0]
    along = [dx * r["D"][0] + dy * r["D"][1] for dx, dy in r["planes"]]
    assert all(a > 0 for a in along) and along == sorted(along), along


def test_a_flat_plates_bare_drift_is_the_walk_it_always_was():
    """R26-164's own line: "a bare drift stays the flat plate's" - the flat plate's pose is idleDriftCss of the free walk."""
    src = ENGINE.read_text(encoding="utf-8")
    paint = src[src.index("const paint = (el, scene, dx = 0) => {"):src.index("paintPlanes(el, plies, camXfNow")]
    pose = src[src.index("const worldPoseAt = "):src.index("const worldXfAt = ")]   # P72 T46b: paint's pose lives here
    assert 'const idleDrift = (k) => (KIN.plate_idle_paints === true ? idleDriftCss(idlePose, k) : "");' in pose
    assert "const restFlat = worldRest + idleDrift(PARALLAX.FLAT);" in pose, "the flat world's rest is the free walk"
    assert "worldPoseAt(scene, t, dx)" in paint
    assert "const planePose = plies.length ? driftAlongCam(idlePose, camXfNow, idleAmp) : null;" in paint
    assert "paintPlanes(el, plies, camXfNow, worldRest, planeDrift," in src, "the planes read the walk that follows"


def test_the_compiler_names_a_layered_drift_the_camera_turns_off():
    layered = {"asset_id": "p", "idle": "drift", "layers": [{"key": "ly:p:background", "k": 1.0, "role": "background"}]}
    ws = B.layered_drift_warnings(layered, [], None)
    assert len(ws) == 1 and "R26-164" in ws[0] and "drift is OFF" in ws[0] and "E99 s65" in ws[0], ws
    zoom = {"kind": "focus_zoom", "at": 1.0, "dur": 2.0, "target": {"kind": "point", "x": 0.7, "y": 0.6}}
    assert B.layered_drift_warnings(layered, [zoom], None) == [], "a camera move gives the drift its direction"
    keys = {"keys": [{"t": 1.0, "zoom": 1.1, "look": [0.6, 0.5]}, {"t": 3.0, "zoom": 1.2, "look": [0.6, 0.5]}]}
    assert B.layered_drift_warnings(layered, [], keys) == []
    assert B.layered_drift_warnings(layered, [], {"attention": "landings"}) == []
    assert B.layered_drift_warnings(layered, [], {"pedestal": {"at": 1.0, "dur": 2.0, "by": 0.2}}) == []
    assert B.layered_drift_warnings(dict(layered, idle="breath"), [], None) == [], "no walk, nothing to turn off"
    flat = {"asset_id": "p", "idle": "drift"}
    assert B.layered_drift_warnings(flat, [], None) == [], "a flat plate keeps its bare drift"
    assert "raise" not in __import__("inspect").getsource(B.layered_drift_warnings), "a finding WARNs (s106)"


def test_the_long_form_door_keeps_ken_burns_alone():
    """s84: the long form's plates are Ken Burns alone - its kinetics keep the painted drift off, so nothing here moves it."""
    door = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py"
    if not door.is_file():
        pytest.skip("the H door is lane A's")
    src = door.read_text(encoding="utf-8")
    assert '"plate_idle_paints": False' in src
