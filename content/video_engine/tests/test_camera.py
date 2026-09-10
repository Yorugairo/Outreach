"""P49 T1-T3 - the camera as a first-class component: the model on the timeline (identity by default, authored keys
validated), one camera state per frame behind `kinetics.camera` (the three species pixel-identical to the path they
shipped on), and the probe `__camera(t, target)` - the engine knows what it is seeing before a frame is rendered."""
from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

PLATE = "ledger:golden:line"
POINT = {"kind": "point", "x": 0.62, "y": 0.41}


def _browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="playwright chromium not installed")


# ---- T1: the model ----------------------------------------------------------------------------------------------------

def test_identity_is_the_default_and_a_compiled_timeline_carries_the_flag():
    assert B.camera_identity() == {"keys": [], "attention": "locked"}
    assert B.build_kinetics()["camera"] is True
    assert B.CAMERA_ATTENTION == ("locked", "landings") and B.CAMERA_EASES == ("cubic", "inout", "linear", "hold")
    assert B.validate_camera(None, PLATE) == [] and B.validate_camera(B.camera_identity(), PLATE) == []


@pytest.mark.parametrize("cam, needle", [
    ({"keys": [{"t": 4.0, "zoom": 1.2}, {"t": 3.0, "zoom": 1.0}]}, "ascending t"),
    ({"keys": [{"t": 4.0, "zoom": 0}]}, "zoom must be a number > 0"),
    ({"keys": [{"t": "four", "zoom": 1.2}]}, "'t' must be a number"),
    ({"keys": [{"t": 4.0, "zoom": 1.2, "ease": "bounce"}]}, "ease must be one of"),
    ({"keys": [{"t": 4.0, "zoom": 1.2, "look": [1.5, 0.2]}]}, "stage fractions 0..1"),
    ({"keys": [{"t": 4.0, "zoom": 1.2, "look": {"kind": "datum"}}]}, "datum"),
    ({"keys": [], "attention": "wander"}, "attention must be one of"),
    ({"keys": "no"}, "keys must be a list"),
    ("locked", "camera must be a dict"),
])
def test_an_authored_camera_is_validated_by_name(cam, needle):
    errs = B.validate_camera(cam, PLATE)
    assert errs and any(needle in e for e in errs), (needle, errs)


def test_a_good_key_list_passes_and_keys_never_share_a_row_with_a_camera_species():
    cam = {"keys": [{"t": 2.0, "zoom": 1.0, "look": [0.5, 0.5]}, {"t": 4.0, "zoom": 1.5, "look": {"kind": "point", "x": 0.7, "y": 0.3}, "at": [0.5, 0.5], "ease": "inout"}], "attention": "locked"}
    assert B.validate_camera(cam, PLATE) == []
    errs = B.validate_camera_row(cam, [{"kind": "punch", "at": 3.0, "dur": 1.0, "target": POINT}], PLATE)
    assert len(errs) == 1 and "camera keys and a punch" in errs[0] and "s9.28 C3" in errs[0], errs
    assert B.validate_camera_row(cam, [{"kind": "callout", "at": 3.0, "dur": 1.0, "target": POINT}], PLATE) == []
    assert B.validate_camera_row(None, [{"kind": "punch", "at": 3.0, "dur": 1.0, "target": POINT}], PLATE) == []


# ---- T2 / T3: the player ----------------------------------------------------------------------------------------------

def _timeline(scenes_species: list[list[dict]], cameras: list[dict | None], flag: bool, span: float = 8.0):
    """The golden soak page repeated per scene, each scene with its own species list and camera; the flag as named."""
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    base = tl["scenes"][0]
    scenes = []
    for i, (sp, cam) in enumerate(zip(scenes_species, cameras)):
        sc = dict(base, scene_id=f"s{i + 1:02d}", species=sp, span=[i * span, (i + 1) * span], world=dict(base["world"], ken_burns={"scale": 0, "x": 0, "y": 0}))
        if cam is not None:
            sc["camera"] = cam
        scenes.append(sc)
    runtime = span * len(scenes)
    timeline = dict(tl, aspect="9:16", runtime_s=runtime, scenes=scenes, caption_pages=[], captions=[], kinetics={"camera": flag})
    return timeline, uris


class _Player:
    def __init__(self, timeline, uris):
        from playwright.sync_api import sync_playwright
        self.td = tempfile.TemporaryDirectory()
        html = Path(self.td.name) / "cam.html"
        html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
        self.w, self.h = RB.STAGE["9:16"]
        self.srv, port = RB.serve(html.parent)
        self.pw = sync_playwright().start()
        self.br = self.pw.chromium.launch(headless=True)
        self.page = self.br.new_context(viewport={"width": self.w, "height": self.h}).new_page()
        self.errs: list[str] = []
        self.page.on("pageerror", lambda e: self.errs.append(str(e)))
        self.page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, self.w, self.h)

    def seek(self, t: float) -> None:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)

    def transform(self) -> str:
        return self.page.evaluate("() => [wA, wB].find(e => getComputedStyle(e).opacity !== '0' && e.style.display !== 'none').style.transform")

    def cam(self) -> str:
        """The camera's own part of the world transform (the Ken Burns suffix stripped; the browser normalises numbers)."""
        return self.transform().split("translateX(")[0].strip()

    def frame(self, t: float) -> str:
        return hashlib.sha256(RB.frame_png(self.page, t, (self.w, self.h))).hexdigest()

    def camera(self, t: float, target=None) -> dict:
        return self.page.evaluate("([t, tg]) => window.__camera(t, tg)", [t, target])

    def close(self) -> None:
        self.br.close(); self.pw.stop(); self.srv.shutdown(); self.td.cleanup()


SPECIES = [[{"kind": "punch", "at": 2.0, "dur": 2.0, "target": POINT}],
           [{"kind": "focus_zoom", "at": 10.0, "dur": 2.5, "target": {"kind": "datum", "index": 12}}],
           [{"kind": "pull_back", "at": 17.0, "dur": 1.6, "target": {"kind": "region", "x0": 0.2, "y0": 0.3, "x1": 0.6, "y1": 0.5}}]]
INSTANTS = [1.0, 2.3, 3.0, 3.8, 4.5, 10.4, 11.2, 12.4, 17.2, 17.9, 18.7]


@needs_browser
def test_the_three_species_are_pixel_identical_through_the_camera():
    """Flag off (the path they shipped on) and flag on (kinetics/camera.mjs): the same transform string and the same
    frame at every sampled instant of a punch, a focus zoom and a pull-back - a flag flip changes no pixel. (One
    browser at a time: two sync Playwright sessions in one thread refuse each other.)"""
    def capture(flag):
        p = _Player(*_timeline(SPECIES, [None, None, None], flag))
        try:
            out = []
            for t in INSTANTS:
                p.seek(t); out.append((t, p.transform(), p.frame(t)))
            p.seek(3.0); hold = p.cam()
            assert not p.errs, p.errs
            return out, hold
        finally:
            p.close()
    off, _ = capture(False)
    on, hold = capture(True)
    for (t, tr0, h0), (_t, tr1, h1) in zip(off, on):
        assert tr0 == tr1, (t, tr0, tr1)
        assert h0 == h1, t
    assert "scale(1.14)" in hold and hold.startswith("translate("), ("the punch's hold, a zoom in place", hold)


@needs_browser
def test_the_probe_knows_the_frustum_and_whether_a_target_is_in_frame():
    p = _Player(*_timeline(SPECIES, [None, None, None], True))
    try:
        p.seek(1.0)
        c = p.camera(1.0, POINT)
        assert c["on"] and c["zoom"] == 1 and c["frustum"] == {"x0": 0, "y0": 0, "x1": 1080, "y1": 1920}, c
        assert c["target"]["visible"] == 1 and c["target"]["inside"], c["target"]
        p.seek(3.0)   # the punch's hold: a 1.14 zoom about the point
        c = p.camera(3.0, POINT)
        assert abs(c["zoom"] - 1.14) < 1e-9 and c["look"] == c["at"], c
        fr = c["frustum"]
        assert fr["x0"] > 0 and fr["y0"] > 0 and fr["x1"] < 1080 and fr["y1"] < 1920, "the frustum is inside the stage"
        assert abs((fr["x1"] - fr["x0"]) - 1080 / 1.14) < 0.01 and abs((fr["y1"] - fr["y0"]) - 1920 / 1.14) < 0.01
        assert c["target"]["inside"] and c["target"]["scale"] == c["zoom"], "the punch's own target is in frame"
        far = p.camera(3.0, {"kind": "point", "x": 0.02, "y": 0.02})
        assert far["target"]["visible"] == 0 and not far["target"]["inside"], "the far corner has left the frame"
        assert far["target"]["screen"][0] < 0 or far["target"]["screen"][1] < 0, "and projects off screen"
        assert not p.errs, p.errs
    finally:
        p.close()


@needs_browser
def test_authored_keys_pan_and_zoom_and_the_frustum_follows_the_look():
    cam = {"keys": [{"t": 2.0, "zoom": 1.0, "look": [0.5, 0.5]},
                    {"t": 4.0, "zoom": 1.5, "look": {"kind": "point", "x": 0.7, "y": 0.3}, "at": [0.5, 0.5], "ease": "linear"}], "attention": "locked"}
    p = _Player(*_timeline([[]], [cam], True))
    try:
        p.seek(1.0)
        assert p.cam() == "" and p.camera(1.0)["zoom"] == 1, "identity before the first key"
        p.seek(4.5)
        c = p.camera(4.5)
        assert abs(c["zoom"] - 1.5) < 1e-9 and c["look"] == [0.7 * 1080, 0.3 * 1920] and c["at"] == [540, 960], c
        fr = c["frustum"]
        assert abs((fr["x0"] + fr["x1"]) / 2 - 0.7 * 1080) < 0.01 and abs((fr["y0"] + fr["y1"]) / 2 - 0.3 * 1920) < 0.01, "the frustum is centred on the look point"
        tr = p.cam()
        assert tr.startswith("translate(") and "scale(1.5)" in tr and tr.count("translate(") == 1, ("a pan takes the general form", tr)
        p.seek(3.0)
        m = p.camera(3.0)
        assert abs(m["zoom"] - 1.25) < 1e-9, "linear between the keys"
        p.seek(9.0)
        assert abs(p.camera(9.0)["zoom"] - 1.5) < 1e-9, "holds after the last key"
        p.seek(1.0); p.seek(4.5); assert p.cam() == tr, "a seek is the play"
        assert not p.errs, p.errs
    finally:
        p.close()
