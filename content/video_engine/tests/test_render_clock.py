"""P61 T12 - THE FRAME CLOCK. E99 s36, the operator verbatim: *"yes, render should be 24 fps. align plate
life to 12 fps."*

One clock, four dials, and a probe that proves the jitter is gone:

  - `render_episode.FPS` is 24 - the base the stop-action cadence already counts its holds in.
  - the engine's plate-life dial `LIFE_FPS` is 12, read out of the engine text (it is INLINE engine code,
    not a kinetics module, so there is nothing to import - the number is asserted where it lives).
  - the stop-action split is UNCHANGED: `CADENCE.FPS` 24, `ON1_PX_S` 154 (kinetics/stopaction.mjs) and the
    soak's own `SOAK_STEP.FPS` 8 (kinetics/ink.mjs), each read out of its module.
  - THE EVEN-HOLD PROBE: a stepped element, in a headless page, over one second at the render clock. Every
    hold on 2s must be exactly two rendered frames and every hold on 3s exactly three - no 2/3 alternation.
    The probe is proven by breaking it: the same element on the OLD dials (a 12 fps hold on a 30 fps render,
    and plate life's old 10 fps on the new 24 fps render) alternates 2 and 3, and the probe says so.

The probe drives the SHIPPED `stepped()` out of kinetics/stopaction.mjs (copied whole into a served temp
dir, so the modules under test are the ones on disk) and the engine's own plate-life quantiser
(`Math.floor(t * LIFE_FPS) / LIFE_FPS`, scene-evidence-engine.mjs's `lpLife`/boil step), and reads the hold
off the ELEMENT's computed transform, never off the formula in python.
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import render_baseline as RB  # noqa: E402
import render_episode as RE  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
KINETICS = ROOT / "content/video_engine/scripts/kinetics"

RENDER_FPS = 24        # E99 s36
PLATE_LIFE_FPS = 12    # E99 s36: "align plate life to 12 fps"
CADENCE_FPS = 24       # P47 T1 / P53 T5 - unchanged by this slice
ON1_PX_S = 154         # E99 s30, the cinema-parity threshold - unchanged by this slice
SOAK_FPS = 8           # the soak's own step - unchanged by this slice


def _dial(path: Path, name: str) -> float:
    """The numeric value of `<name>: <number>` in a source file - the dial read where it lives."""
    m = re.search(rf"\b{re.escape(name)}\s*:\s*(-?\d+(?:\.\d+)?)", path.read_text(encoding="utf-8"))
    assert m, f"{name} not found in {path.name}"
    return float(m.group(1))


# ---- the dials -----------------------------------------------------------------------------------------

def test_the_render_clock_is_24_fps():
    assert RE.FPS == RENDER_FPS


def test_every_frame_count_the_renderer_derives_comes_from_the_clock_and_durations_stay_in_seconds():
    """A duration in seconds must still render the right number of frames, and the audio mux must not move."""
    src = (ROOT / "content/video_engine/scripts/render_episode.py").read_text(encoding="utf-8")
    assert src.count("int(round((t1 - t0) * FPS))") == 2      # capture() and main() - both derived, neither hard-coded
    assert "t = t0 + i / FPS" in src and "capture(f0 / FPS, f1 / FPS, video_out)" in src
    assert '"-framerate", str(FPS)' in src
    assert '"-ss", f"{t0:.3f}"' in src and '"-t", f"{t1 - t0:.3f}"' in src   # the mux is SECONDS
    # a duration in SECONDS still renders the right count: 10.0 s is 240 frames, the last one t = 239/24 s,
    # one frame short of the end - and the four shards of a 240-frame render still tile it exactly
    assert int(round(10.0 * RE.FPS)) == 240
    assert 239 / RE.FPS < 10.0 <= 240 / RE.FPS
    chunk = -(-240 // 4)
    assert [(w * chunk, min((w + 1) * chunk, 240)) for w in range(4)] == [(0, 60), (60, 120), (120, 180), (180, 240)]


def test_plate_life_sits_on_the_2s_grid_of_the_render_clock():
    life = _dial(ENGINE, "LIFE_FPS")
    assert life == PLATE_LIFE_FPS, "E99 s36: plate life is 12 fps"
    assert RE.FPS / life == 2.0, "a plate-life hold is exactly two rendered frames"


def test_the_stop_action_split_is_unchanged():
    assert _dial(KINETICS / "stopaction.mjs", "FPS") == CADENCE_FPS
    assert _dial(KINETICS / "stopaction.mjs", "ON1_PX_S") == ON1_PX_S
    assert _dial(KINETICS / "ink.mjs", "FPS") == SOAK_FPS, "the soak's own step, SOAK_STEP.FPS"
    # the render clock IS the cadence clock now, and every hold the cadence rule names divides it exactly
    assert RE.FPS == CADENCE_FPS
    for hold in (1, 2, 3):
        assert CADENCE_FPS % hold == 0 and RE.FPS % hold == 0
    assert CADENCE_FPS / 3 == SOAK_FPS, "an on-3s boil and the soak step are the same 8 fps, carried exactly by 24"


# ---- the even-hold probe -------------------------------------------------------------------------------

def _browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="playwright chromium not installed")

PROBE_HTML = """<!doctype html><meta charset="utf-8"><title>the frame clock</title>
<style>div { position: absolute; width: 10px; height: 10px; background: #000; }</style>
<div id="on1"></div><div id="on2"></div><div id="on3"></div><div id="life"></div>
<script type="module">
  import { CADENCE, stepped } from "./stopaction.mjs";
  /* the cadence rule's three holds, driven by the SHIPPED stepped(); on 1s the renderer's own clock is the
     cadence clock, so the element takes t quantised to the render frame. */
  const CAD = { on1: 1, on2: 2, on3: 3 };
  const place = (id, v) => { document.getElementById(id).style.transform =
    "translateX(" + (v * 1000).toFixed(4) + "px)"; };
  window.__seek = (t, lifeFps) => {
    for (const [id, hold] of Object.entries(CAD))
      place(id, hold > 1 ? stepped(t, hold, CADENCE.FPS) : Math.round(t * CADENCE.FPS) / CADENCE.FPS);
    /* the engine's plate-life quantiser, verbatim (scene-evidence-engine.mjs: Math.floor(t * SP.LIFE_FPS) / SP.LIFE_FPS) */
    place("life", Math.floor(t * lifeFps) / lifeFps);
  };
  window.__pose = (id) => getComputedStyle(document.getElementById(id)).transform;
  window.__ready = true;
</script>
"""


class _Probe:
    """A served page holding one stepped element per hold, driven frame by frame at a named render clock."""

    def __init__(self):
        from playwright.sync_api import sync_playwright
        self.td = tempfile.TemporaryDirectory()
        d = Path(self.td.name)
        for mjs in KINETICS.glob("*.mjs"):      # the modules under test, as they stand on disk
            shutil.copy2(mjs, d / mjs.name)
        (d / "probe.html").write_text(PROBE_HTML, encoding="utf-8")
        self.srv, port = RB.serve(d)
        self.pw = sync_playwright().start()
        self.br = self.pw.chromium.launch(headless=True)
        self.page = self.br.new_context(viewport={"width": 320, "height": 240}).new_page()
        self.errs: list[str] = []
        self.page.on("pageerror", lambda e: self.errs.append(str(e)))
        self.page.goto("http://127.0.0.1:%d/probe.html" % port, wait_until="networkidle", timeout=120000)
        self.page.wait_for_function("() => window.__ready === true", timeout=30000)

    def holds(self, ids: list[str], fps: float, life_fps: float, seconds: float = 1.0) -> dict[str, list[int]]:
        """Run lengths of the identical poses each element holds, over `seconds` of the render grid k / fps."""
        poses: dict[str, list[str]] = {i: [] for i in ids}
        for k in range(int(round(seconds * fps))):
            self.page.evaluate("([t, l]) => window.__seek(t, l)", [k / fps, life_fps])
            for i in ids:
                poses[i].append(self.page.evaluate("i => window.__pose(i)", i))
        out = {}
        for i in ids:
            runs, prev = [], object()
            for p in poses[i]:
                if p == prev:
                    runs[-1] += 1
                else:
                    runs.append(1)
                    prev = p
            out[i] = runs
        return out

    def close(self) -> None:
        self.br.close(); self.pw.stop(); self.srv.shutdown(); self.td.cleanup()


@pytest.fixture(scope="module")
def probe():
    p = _Probe()
    yield p
    p.close()


@needs_browser
def test_every_hold_is_even_at_the_render_clock(probe):
    """One second at 24 fps: on 1s every frame, on 2s exactly two frames, on 3s exactly three, plate life two."""
    runs = probe.holds(["on1", "on2", "on3", "life"], RE.FPS, PLATE_LIFE_FPS)
    assert not probe.errs, probe.errs
    assert set(runs["on1"]) == {1} and len(runs["on1"]) == 24, runs["on1"]
    assert set(runs["on2"]) == {2} and len(runs["on2"]) == 12, runs["on2"]
    assert set(runs["on3"]) == {3} and len(runs["on3"]) == 8, runs["on3"]
    assert set(runs["life"]) == {2} and len(runs["life"]) == 12, runs["life"]


@needs_browser
def test_the_probe_catches_the_jitter_it_says_is_gone(probe):
    """Proven by breaking it. The SAME element on the clocks E99 s36 retired alternates 2 and 3 frames:
    a 12 fps hold resampled onto a 30 fps render, and plate life's old 10 fps on the 24 fps render."""
    old_render = probe.holds(["on2", "on3"], 30.0, PLATE_LIFE_FPS)
    assert set(old_render["on2"]) == {2, 3}, old_render["on2"]        # the operator's jitter, at 30
    assert set(old_render["on3"]) == {3, 4}, old_render["on3"]        # an on-3s boil was uneven at 30 too
    old_life = probe.holds(["life"], RE.FPS, 10.0)                    # LIFE_FPS 10 on the new clock
    assert set(old_life["life"]) == {2, 3}, old_life["life"]
    # and 10 fps was even on the retired 30 fps render - the dial had to move BECAUSE the render moved
    assert set(probe.holds(["life"], 30.0, 10.0)["life"]) == {3}
