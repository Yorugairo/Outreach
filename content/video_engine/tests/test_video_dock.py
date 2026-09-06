"""THE VIDEO DOCK (ruling E44 / backlog R26-7, operator 2026-09-06: "use the chart plate/ledger
AND THEN DOCK the animation videos").

A dock asset may be a clip. The compiler embeds it raw - the way a CLIP WORLD is embedded - and
declares `kind: "video"` on the dock entry and the evidence map; the player mounts the pooled
<video> inside the card's slide-frame and seeks it on the SAME code path the world clip uses
(`seekVideo`), from the dock's own clock (t - enter, looping); the motion gate credits a live
video dock as continuous motion (test_gate_motion_density covers the gate half).

The browser half builds a real synthetic episode - one ledger scene from the golden sources, one
2s testsrc clip docked over it - and renders it through `render_baseline.render_frame`, which is
the harness the shipped renderer uses. Skipped where ffmpeg or chromium is absent.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"
SOURCES = ROOT / "content/video_engine/tests/golden/sources"
CLIP_S = 2.0            # the synthetic clip's length: short enough that a 16s dock proves the loop
DOCK_IN, DOCK_OUT = 4.0, 20.0


def _ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_ffmpeg = pytest.mark.skipif(_ffmpeg() is None, reason="ffmpeg not on PATH")
needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _make_clip(path: Path, seconds: float = CLIP_S) -> Path:
    """A 2s testsrc: every frame differs from the one before it, which is what a still card is not."""
    subprocess.run([_ffmpeg(), "-y", "-loglevel", "error", "-f", "lavfi",
                    "-i", f"testsrc=size=640x360:rate=25:duration={seconds}",
                    "-pix_fmt", "yuv420p", "-c:v", "libx264", str(path)], check=True)
    return path


def _make_png(path: Path) -> Path:
    from PIL import Image
    Image.new("RGB", (320, 180), (12, 40, 90)).save(path)
    return path


# ---- the compiler: a clip docks like a clip world, and says so ------------------------------


@needs_ffmpeg
def test_a_video_dock_asset_embeds_raw_like_a_world_clip(tmp_path: Path):
    clip = _make_clip(tmp_path / "clip-a.mp4")
    assert B.is_video_asset(clip) and B.is_video_asset(tmp_path / "x.WEBM")
    uri = B.dock_uri(clip)
    assert uri.startswith("data:video/mp4;base64,")
    # byte for byte the clip world's embedding: data_uri with no downscale cap
    assert uri == B.data_uri(clip)


def test_an_image_dock_asset_still_embeds_as_a_capped_jpeg(tmp_path: Path):
    png = _make_png(tmp_path / "ev-still.png")
    assert not B.is_video_asset(png)
    assert B.dock_uri(png).startswith("data:image/jpeg;base64,")
    assert B.dock_uri(png) == B.data_uri(png, B.CARD_W)


def test_the_dock_entry_declares_video_and_leaves_an_image_dock_untouched():
    video = B.dock_entry("clip-a", 0, 4.0, 20.0, 0, B.DOCK_KIND_VIDEO)
    assert video == {"slide": "clip-a", "slot": 0, "enter": 4.0, "exit": 20.0,
                     "badge_at": [], "kind": "video"}
    image = B.dock_entry("ev-still", 1, 4.0, 20.0, 2)
    assert image == {"slide": "ev-still", "slot": 1, "enter": 4.0, "exit": 20.0,
                     "badge_at": [6.05, 7.35]}
    assert "kind" not in image, "an image build must compile exactly as it did before E44"


@needs_ffmpeg
def test_dock_asset_path_takes_a_clip_path_or_goes_through_the_resolver(tmp_path: Path):
    clip = _make_clip(tmp_path / "docked.mp4")
    assert B.dock_asset_path(f"clip:{clip}", tmp_path) == clip                       # absolute
    assert B.dock_asset_path("clip:docked.mp4", tmp_path) == tmp_path / "docked.mp4"  # episode-relative
    with pytest.raises(ValueError, match="dock clip missing"):
        B.dock_asset_path("clip:nowhere.mp4", tmp_path)
    with pytest.raises(ValueError, match="no dock asset found"):
        B.dock_asset_path("no-such-asset-anywhere", tmp_path)


@needs_ffmpeg
def test_the_asset_resolver_reaches_a_docked_clip_so_the_motion_plan_never_calls_it_missing(tmp_path: Path):
    """build_render_f.find_asset backs the motion plan's missing-asset check; a `clip:` dock id has
    to resolve there too, or a docked clip is reported as an asset that is not on disk."""
    import build_render_f as R
    clip = _make_clip(tmp_path / "docked.mp4")
    assert R.find_asset(f"clip:{clip}") == clip
    assert R.find_asset("clip:no/such/file.mp4") is None


# ---- the template: ONE seek, shared with the world clip -------------------------------------


def test_the_world_clip_and_the_video_dock_share_one_seek():
    html = TEMPLATE.read_text(encoding="utf-8")
    assert html.count("const seekVideo = (v, want) =>") == 1
    assert html.count("seekVideo(v,") == 2, "paintClip and paintDockClip, and nothing else, seek"
    # the awaited-seek machinery the renderer waits on exists exactly once
    assert html.count('v.addEventListener("seeked", done);') == 1
    assert html.count("window.__clipsSeeked = () =>") == 1
    # the dock's clip comes from the SAME pool as the world's, so it is decoded before it mounts
    assert "v = clipFor(d.slide); v.pause(); v.loop = true; frame.appendChild(v);" in html
    # the mount/retract choreography is untouched: the <video> only replaces the <img>
    assert '$("i" + n).src = (ev.record || ev.chart || isVideo) ? "" : (A[aid] || "");' in html


def test_the_caption_still_takes_the_anchor_under_a_video_dock():
    """s9.25 #2 is about the STAGE POSITION, not about the card being still: the caption's stage is
    the centre of the frame, which is exactly where any dock lands. A video dock demotes it too."""
    scenes = [{"scene_id": "s01", "span": [0.0, 30.0], "world": {"asset_id": "p"},
               "docks": [{"slide": "clip-a", "slot": 0, "enter": 4.0, "exit": 20.0, "kind": "video"}]}]
    assert B._dock_live_at(scenes, 5.0) is True
    assert B._dock_live_at(scenes, 2.0) is False


# ---- the browser: the clip paints inside the card and resolves from t -----------------------


def _synthetic_build(tmp_path: Path) -> Path:
    """One ledger scene (the golden source) with one video dock over it, self-contained."""
    tl = json.loads((SOURCES / "ledger-page-mid-build.timeline.json").read_text(encoding="utf-8"))
    uris = json.loads((SOURCES / "ledger-page-mid-build.uris.json").read_text(encoding="utf-8"))
    clip = _make_clip(tmp_path / "clip-a.mp4")
    aid = "clip-a"
    tl["evidence"] = {aid: {"kind": "video", "title": "docked clip", "source": "synthetic",
                            "species": "clip", "badges": []}}
    tl["scenes"][0]["docks"] = [B.dock_entry(aid, 0, DOCK_IN, DOCK_OUT, 0, B.DOCK_KIND_VIDEO)]
    uris[aid] = B.dock_uri(clip)
    html = tmp_path / "video-dock.html"
    html.write_text(RB.instantiate(tl, uris, TEMPLATE), encoding="utf-8")
    return html


def _card_rect(html: Path) -> tuple[int, int, int, int]:
    """The slide-frame's box in stage pixels - measured, never assumed (the dock's geometry is CSS)."""
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE["16:9"]
    srv, port = RB.serve(html.parent)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            page.evaluate("t => { const s = document.getElementById('scrub');"
                          " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", DOCK_IN + 1.0)
            r = page.evaluate("""() => {
                const st = document.getElementById('stage').getBoundingClientRect();
                const f = document.querySelector('#dock-1 .slide-frame').getBoundingClientRect();
                return [f.x - st.x, f.y - st.y, f.width, f.height]; }""")
            browser.close()
    finally:
        srv.shutdown()
    return tuple(round(v) for v in r)


def _crop(png: bytes, box: tuple[int, int, int, int]):
    from PIL import Image
    import io
    x, y, w, h = box
    return Image.open(io.BytesIO(png)).convert("RGB").crop((x, y, x + w, y + h))


@needs_ffmpeg
@needs_browser
def test_the_clip_paints_inside_the_card_and_the_frame_changes_with_t(tmp_path: Path):
    html = _synthetic_build(tmp_path)
    box = _card_rect(html)
    assert box[2] > 200 and box[3] > 100, box
    before = _crop(RB.render_frame(html, DOCK_IN - 1.0), box)     # the card has not mounted yet
    first = _crop(RB.render_frame(html, DOCK_IN + 0.9), box)      # clip-local 0.9s
    second = _crop(RB.render_frame(html, DOCK_IN + 1.7), box)     # clip-local 1.7s
    assert first.tobytes() != before.tobytes(), "the card mounted but the frame did not change"
    assert first.tobytes() != second.tobytes(), "a video dock held one frame - it is a still card"
    # testsrc is saturated colour bars; the ledger page is cream on charcoal and never is
    def saturation(im):
        px = im.tobytes()
        return max(max(px[i:i + 3]) - min(px[i:i + 3]) for i in range(0, len(px), 3))
    assert saturation(first) > 120, "no clip pixels inside the slide-frame"
    assert saturation(before) < saturation(first)


@needs_ffmpeg
@needs_browser
def test_the_dock_clip_runs_on_the_dock_clock_and_loops(tmp_path: Path):
    """The clip starts at its own 0 when the card mounts (offset = t - enter) and wraps when the
    dock outlives it - a card holding a frozen last frame is the still card E44 exists to remove."""
    from playwright.sync_api import sync_playwright
    html = _synthetic_build(tmp_path)
    w, h = RB.STAGE["16:9"]
    srv, port = RB.serve(html.parent)
    seen = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            for t in (DOCK_IN + 0.5, DOCK_IN + 1.5, DOCK_IN + 2.5, DOCK_IN + 9.25, DOCK_IN + 0.5):
                RB.frame_png(page, t, (w, h))
                seen[round(t, 2)] = page.evaluate(
                    "() => { const v = document.querySelector('#dock-1 .slide-frame video.clipv');"
                    " return v ? [v.currentTime, v.loop, v.muted, v.controls, v.playsInline] : null; }")
            browser.close()
    finally:
        srv.shutdown()
    for t, got in seen.items():
        assert got is not None, f"no <video> inside the card at t={t}"
        want = (t - DOCK_IN) % CLIP_S
        assert abs(got[0] - want) < 0.06, f"t={t}: clip at {got[0]:.3f}s, dock clock wants {want:.3f}s"
        assert got[1:] == [True, True, False, True], f"t={t}: loop/muted/controls/playsinline {got[1:]}"
    assert seen[round(DOCK_IN + 2.5, 2)][0] < CLIP_S     # 2.5s into a 2s clip: it wrapped


@needs_ffmpeg
@needs_browser
def test_a_video_dock_frame_is_the_same_frame_on_every_seek(tmp_path: Path):
    """Determinism (P39 T2), with a <video> in the card: the same t in two fresh browsers is the
    same pixels - the renderer awaits __clipsSeeked, which the dock's seek registers on."""
    import hashlib
    html = _synthetic_build(tmp_path)
    t = DOCK_IN + 1.1
    a = RB.rgb_bytes(RB.render_frame(html, t))
    b = RB.rgb_bytes(RB.render_frame(html, t))
    assert a[0] == b[0] == RB.STAGE["16:9"]
    assert hashlib.sha256(a[1]).hexdigest() == hashlib.sha256(b[1]).hexdigest(), (
        "a video dock frame differs between two renders of the same t - the seek is not awaited")
