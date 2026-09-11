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
    html = RB.player_text()
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


# ---- E45 §1: a dock on a ledger page parks in the page's quiet space -------------------------
# "A dock never covers the chart ... a small card - about half the stage width, not the 800px solo
# card - in the page's least busy space ... never over the plot or the source line, and never in
# the caption's anchor. The placement is computed from the page's own geometry by the compiler,
# not hand-placed per shot. A dock on a plain plate keeps the solo card."
#
# THE TITLE IS ALLOWED (E45, the choreography, 2026-09-06): "shrinking it while we slide it to the
# corner OR OVER THE TITLE, so that the graph gains its readability back". The heading is read
# before the card parks, so the title block and the sub are fair ground; the plot (basis label and
# tick labels included), the source line, the badge rail and the caption's anchor are not.
#
# The 9:16 page these cases use is the golden ledger source with ONE change: an E28 sub long enough
# that the band between the title's foot and the plot's head can hold a half-width 16:9 card (a
# card 518 px wide stands 315 px tall, so the band must clear ~347 px, and a portrait page's band
# is `138 + sub height - the basis label`). The golden page's own 2-line sub leaves 186 px, so it
# is covered separately: the compiler shrinks the card rather than covering the chart.

import ledger_page as LPG  # noqa: E402

TALL_SUB = ("Every close from August 2025 to today, four layers on one log axis, indexed to 100 at "
            "the start so the shapes can be compared rather than the prices, and the window chosen "
            "because it is where the divergence begins")
PLACE_T = DOCK_IN + 2.0          # a beat after the card has settled


def _portrait_ledger_timeline(tall_sub: bool = True) -> tuple[dict, dict]:
    """The golden ledger scene as a 9:16 short, with one video dock over the page."""
    tl = json.loads((SOURCES / "ledger-page-mid-build.timeline.json").read_text(encoding="utf-8"))
    uris = json.loads((SOURCES / "ledger-page-mid-build.uris.json").read_text(encoding="utf-8"))
    tl["aspect"] = "9:16"
    page = tl["scenes"][0]["world"]["page"]
    if tall_sub:
        page["sub"] = TALL_SUB
        page["axes"].pop("ylabel", None)
        page.pop("focus", None)          # the sunflower callout would tint the chart the clip's own colours
    return tl, uris


def _overlap(a: dict, b: dict) -> bool:
    return (a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]
            and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"])


def test_a_dock_on_a_ledger_page_takes_a_half_width_card_in_the_quiet_space():
    tl, _ = _portrait_ledger_timeline()
    world = tl["scenes"][0]["world"]
    place = B.dock_place(world, "9:16")
    assert place is not None, "a dock on a ledger page must be placed by the compiler"
    assert abs(place["w"] - round(B.DOCK_ON_PAGE_W * 1080)) <= 20, place    # ~518px: about half the stage
    assert place["h"] == B.dock_card_h(place["w"])                          # the card's own 16:9 height
    boxes = LPG.page_boxes(world["page"], "9:16")
    for name in ("plot", "source", "caption_anchor", "rail"):
        assert not _overlap(place, boxes[name]), f"the card crosses the page's {name}: {place} vs {boxes[name]}"
    safe = boxes["safe"]
    assert safe["x"] <= place["x"] and place["x"] + place["w"] <= safe["x"] + safe["w"], (place, safe)
    # the declared quiet zone picks the END of the band: `right` hugs the safe box's right edge
    assert boxes["quiet_zone"] == "right"
    assert place["x"] + place["w"] > safe["x"] + safe["w"] / 2, "a right quiet zone parks the card right"


def test_the_placement_is_a_pure_function_of_the_page_and_never_mutates_it():
    tl, _ = _portrait_ledger_timeline()
    page = tl["scenes"][0]["world"]["page"]
    before = json.dumps(page, sort_keys=True)
    assert B.page_place(page, "9:16") == B.page_place(page, "9:16")
    assert json.dumps(page, sort_keys=True) == before


def test_a_tight_page_shrinks_the_card_rather_than_covering_the_chart():
    """The golden page's own sub leaves a 186px band. E45 is 'a dock never covers the chart', so the
    card shrinks to what the band holds - it does not fall back to the 800px solo card."""
    tl, _ = _portrait_ledger_timeline(tall_sub=False)
    world = tl["scenes"][0]["world"]
    place = B.dock_place(world, "9:16")
    boxes = LPG.page_boxes(world["page"], "9:16")
    assert place is not None and place["w"] < round(B.DOCK_ON_PAGE_W * 1080)
    assert place["w"] >= B.DOCK_ON_PAGE_MIN_W
    for name in ("plot", "source", "caption_anchor"):
        assert not _overlap(place, boxes[name]), f"the shrunk card crosses the page's {name}"


def test_the_landscape_page_still_places_its_dock_in_the_declared_quiet_zone():
    """16:9 keeps working: there the page's own layout reserves the quiet zone (the chart takes 60%
    of the board), so the card lands in that column, clear of the plot."""
    tl, _ = _portrait_ledger_timeline(tall_sub=False)
    world = tl["scenes"][0]["world"]
    place = B.dock_place(world, "16:9")
    boxes = LPG.page_boxes(world["page"], "16:9")
    assert place is not None and place["w"] >= B.DOCK_ON_PAGE_MIN_W
    assert place["x"] >= boxes["plot"]["x"] + boxes["plot"]["w"], "a right quiet zone is right of the plot"
    for name in ("plot", "source", "caption_anchor"):
        assert not _overlap(place, boxes[name]), f"the landscape card crosses the page's {name}"


def test_a_dock_on_a_plain_plate_keeps_the_solo_card():
    plate = {"asset_id": "p-desk", "ken_burns": {"scale": 0.04, "x": 0, "y": 0}}
    assert B.dock_place(plate, "9:16") is None
    assert B.dock_place({"kind": "clip", "asset_id": "c"}, "9:16") is None
    entry = B.dock_entry("ev-still", 0, 4.0, 20.0, 0, B.DOCK_KIND_IMAGE, None)
    assert "place" not in entry, "a plain-plate dock must compile exactly as it did before E45"
    for key in ("read_s", "park_s", "park"):
        assert key not in entry, f"a plain-plate dock has no {key}: it keeps the 0.75s solo rise"


def test_the_dock_entry_carries_the_placement_and_its_choreography():
    """E45: `place` never arrives alone - the card SPRINGS in at reading size, holds `read_s`, then
    shrinks and slides to `place` over `park_s`. The clock rides on the entry so a gate, a test or
    a later per-dock override can read it without re-deriving the player's constants."""
    place = {"x": 346, "y": 435, "w": 518, "h": 315}
    entry = B.dock_entry("clip-a", 0, 4.0, 20.0, 0, B.DOCK_KIND_VIDEO, place)
    assert entry == {"slide": "clip-a", "slot": 0, "enter": 4.0, "exit": 20.0,
                     "badge_at": [], "kind": "video", "place": place,
                     "read_s": B.DOCK_READ_S, "park_s": B.DOCK_PARK_S, "park": True}
    assert (B.DOCK_READ_S, B.DOCK_PARK_S) == (1.2, 0.7)


def test_a_dock_too_short_to_read_and_park_says_park_false():
    """"If a dock's live span is shorter than READ + PARK, skip the park" - the card stays at
    reading size for its whole life rather than parking the instant it has been read."""
    place = {"x": 346, "y": 435, "w": 518, "h": 315}
    short = B.dock_entry("clip-a", 0, 4.0, 4.0 + B.DOCK_READ_S + B.DOCK_PARK_S - 0.1, 0,
                         B.DOCK_KIND_VIDEO, place)
    assert short["park"] is False
    exact = B.dock_entry("clip-a", 0, 4.0, 4.0 + B.DOCK_READ_S + B.DOCK_PARK_S, 0,
                         B.DOCK_KIND_VIDEO, place)
    assert exact["park"] is True, "a span exactly long enough parks"


def test_the_player_reads_place_and_overrides_the_solo_defaults():
    html = RB.player_text()
    for prop, expr in (("width", "G.w"), ("left", "G.x"), ("top", "G.y")):
        assert f"el.style.{prop} = G ? {expr}.toFixed(2)" in html, (
            f"the card's {prop} must come from the choreography")
    assert "const G = dockGeom(el, d, t);" in html
    # the frame keeps the clip's aspect and the image case keeps its intrinsic height
    assert ".dock.video .slide-frame { aspect-ratio: 16 / 9;" in html
    assert ".slide-frame img { display: block; width: 100%; height: auto; }" in html


def test_the_park_is_the_engines_own_kinetics_not_a_cut_or_a_dissolve():
    """E45: "you're just cutting the docks in instead of using our strong maths/springs". The
    arrival is the analytic spring's POP preset (42 s42.2, Mp = 4%, settle 6); the shrink and the
    slide are Flash & Hogan's minimum-jerk quintic, width and position on ONE clock."""
    html = RB.player_text()
    assert "const j = minJerk(clamp01((t - d.enter - readS) / parkS));" in html
    assert "R.x + (P.x - R.x) * j" in html and "R.w + (P.w - R.w) * j" in html
    assert "const pk = springPop(clamp01((t - d.enter) / DOCK_POP_S));" in html
    assert "const rk = t > d.exit ? springPop(clamp01((t - d.exit) / DOCK_RETRACT_S)) : 0;" in html
    assert "const DOCK_READ_S = 1.2, DOCK_PARK_S = 0.7;" in html
    assert "DOCK_POP_S = 0.45, DOCK_POP_FROM = 0.85, DOCK_FADE_S = 0.12, DOCK_RETRACT_S = 0.35" in html
    # a dissolve or a cut into the parked box is exactly what the ruling forbids
    assert "el.style.width = d.place ? d.place.w" not in html


def test_the_title_block_is_ground_the_parked_card_may_take():
    """The choreography opens the top band: the card may park OVER THE TITLE (and the sub), which
    on a 9:16 page is the difference between the 240px floor card and a readable one."""
    tl, _ = _portrait_ledger_timeline(tall_sub=False)
    world = tl["scenes"][0]["world"]
    boxes = LPG.page_boxes(world["page"], "9:16")
    bands = {b["band"]: b for b in B.free_bands(boxes)}
    assert bands["above"]["y"] == boxes["safe"]["y"], "the top band starts at the safe box's head"
    assert bands["above"]["y"] < boxes["title"]["y"] + boxes["title"]["h"], "the band reaches the title"
    place = B.dock_place(world, "9:16")
    assert place["w"] > B.DOCK_ON_PAGE_MIN_W, (
        "with the title allowed the golden page holds more than the floor card")
    assert _overlap(place, boxes["title"]), "the golden page parks its card over the title"


def _synthetic_portrait_build(tmp_path: Path) -> tuple[Path, dict, dict]:
    """The 9:16 ledger scene with one placed video dock - self-contained, like _synthetic_build."""
    tl, uris = _portrait_ledger_timeline()
    clip = _make_clip(tmp_path / "clip-p.mp4")
    aid = "clip-p"
    tl["evidence"] = {aid: {"kind": "video", "title": "docked clip", "source": "synthetic",
                            "species": "clip", "badges": []}}
    place = B.dock_place(tl["scenes"][0]["world"], "9:16")
    tl["scenes"][0]["docks"] = [B.dock_entry(aid, 0, DOCK_IN, DOCK_OUT, 0, B.DOCK_KIND_VIDEO, place)]
    uris[aid] = B.dock_uri(clip)
    html = tmp_path / "video-dock-portrait.html"
    html.write_text(RB.instantiate(tl, uris, TEMPLATE), encoding="utf-8")
    return html, place, LPG.page_boxes(tl["scenes"][0]["world"]["page"], "9:16")


def _clip_pixel_bbox(png: bytes) -> tuple[int, int, int, int] | None:
    """The bounding box of the CLIP's own pixels. testsrc's bars carry cyan and magenta - a
    saturated primary pair the ledger page's register (cream, charcoal, sunflower, the sign
    colours) contains nowhere, so a cyan/magenta pixel is a clip pixel and nothing else."""
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(png)).convert("RGB")
    w, h = im.size
    px = im.load()
    xs, ys = [], []
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b = px[x, y]
            if (r < 90 and g > 170 and b > 170) or (r > 170 and g < 90 and b > 170):
                xs.append(x); ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


@needs_ffmpeg
@needs_browser
def test_the_placed_clip_paints_inside_its_rectangle_and_never_on_the_plot(tmp_path: Path):
    """The frame proof for E45 §1: on a 9:16 ledger page the docked clip's own pixels lie inside
    the compiler's `place` rectangle, and not one of them lands inside the page's plot box."""
    html, place, boxes = _synthetic_portrait_build(tmp_path)
    png = RB.render_frame(html, PLACE_T, "9:16")
    box = _clip_pixel_bbox(png)
    assert box is not None, "no clip pixels on the frame - the card did not mount"
    x, y, w, h = box
    assert w > 200 and h > 100, box
    assert place["x"] <= x and x + w <= place["x"] + place["w"], (box, place)
    assert place["y"] <= y and y + h <= place["y"] + place["h"], (box, place)
    plot = boxes["plot"]
    assert not _overlap({"x": x, "y": y, "w": w, "h": h}, plot), (
        f"clip pixels at {box} reach into the plot {plot} - the dock is covering the chart")


# ---- E45 the choreography: spring in, read, park by minimum jerk -----------------------------
# Operator, 2026-09-06: "drawing on the heading, springing the dock, then shrinking it while we
# slide it to the corner or over the title, so that the graph gains its readability back" and
# "you're just cutting the docks in instead of using our strong maths/springs".
#
# The card's LAYOUT box carries the move (width/left/top per frame), so the parked box is `place`
# to the pixel and the browser can be asked what it is. Measured here, never assumed.

READ_S, PARK_S = B.DOCK_READ_S, B.DOCK_PARK_S
MJ_TOL, PARK_TOL = 3.0, 2.0        # px: the min-jerk curve, and the parked rectangle


def _min_jerk(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return u * u * u * (10 - 15 * u + 6 * u * u)


def _dock_rects(html: Path, ts, aspect: str = "9:16") -> dict:
    """`#dock-1`'s box in STAGE pixels at each t, one browser, the renderer's own seek path."""
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE[aspect]
    srv, port = RB.serve(html.parent)
    out = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            for t in ts:
                RB.frame_png(page, t, (w, h))
                out[round(t, 3)] = page.evaluate("""() => {
                    const st = document.getElementById('stage').getBoundingClientRect();
                    const d = document.getElementById('dock-1').getBoundingClientRect();
                    return [d.x - st.x, d.y - st.y, d.width, d.height]; }""")
            browser.close()
    finally:
        srv.shutdown()
    return out


def _portrait_dock_build(tmp_path: Path, name: str, exitt: float = DOCK_OUT):
    """The 9:16 ledger page with one placed video dock, its span the caller's."""
    tl, uris = _portrait_ledger_timeline()
    clip = _make_clip(tmp_path / f"{name}.mp4")
    aid = f"clip-{name}"
    tl["evidence"] = {aid: {"kind": "video", "title": "docked clip", "source": "synthetic",
                            "species": "clip", "badges": []}}
    place = B.dock_place(tl["scenes"][0]["world"], "9:16")
    tl["scenes"][0]["docks"] = [B.dock_entry(aid, 0, DOCK_IN, exitt, 0, B.DOCK_KIND_VIDEO, place)]
    uris[aid] = B.dock_uri(clip)
    html = tmp_path / f"{name}.html"
    html.write_text(RB.instantiate(tl, uris, TEMPLATE), encoding="utf-8")
    return html, place, tl["scenes"][0]["docks"][0]


@needs_ffmpeg
@needs_browser
def test_the_card_reads_at_full_size_then_parks_on_the_minimum_jerk_path(tmp_path: Path):
    """The whole choreography in one browser session: reading size while it is being read, the
    parked rectangle after the park, and the three samples between them on the min-jerk curve."""
    html, place, entry = _portrait_dock_build(tmp_path, "choreo")
    assert entry["park"] is True
    # the harness drives #scrub, an <input type=range step=0.01>, so a sample t off the 10ms grid
    # is snapped by the browser before the player ever sees it; these three land on it exactly
    mids = [round(DOCK_IN + READ_S + PARK_S * f, 2) for f in (0.2, 0.5, 0.8)]
    assert all(abs(m * 100 - round(m * 100)) < 1e-9 for m in mids)
    ts = [DOCK_IN + 0.6, *mids, DOCK_IN + READ_S + PARK_S + 0.2]
    rects = _dock_rects(html, ts)

    read = rects[round(DOCK_IN + 0.6, 3)]
    # PHASE A: the solo card, 800px in the mobile safe box - and the spring has settled on 1
    assert abs(read[2] - 800) <= PARK_TOL, f"reading size is the 800px solo card, got {read}"
    assert read[2] > place["w"] * 1.5, (read, place)

    parked = rects[round(DOCK_IN + READ_S + PARK_S + 0.2, 3)]
    for i, key in enumerate(("x", "y", "w")):
        assert abs(parked[i] - place[key]) <= PARK_TOL, (
            f"parked {key} is {parked[i]}, the compiler placed it at {place[key]}")
    assert abs(parked[3] - place["h"]) <= PARK_TOL, (
        f"the parked card stands {parked[3]}px, the compiler predicted {place['h']}")

    # PHASE B: x, y and width all on minJerk(u) between the two rectangles - one clock, one move
    for t in mids:
        got = rects[round(t, 3)]
        j = _min_jerk((t - DOCK_IN - READ_S) / PARK_S)
        for i, key in enumerate(("x", "y", "w")):
            want = read[i] + (place[key] - read[i]) * j
            assert abs(got[i] - want) <= MJ_TOL, (
                f"t={t:.3f} {key}={got[i]:.1f}, minimum jerk wants {want:.1f} (u={j:.3f})")


@needs_ffmpeg
@needs_browser
def test_a_dock_too_short_for_read_plus_park_never_parks(tmp_path: Path):
    """A card that would park the instant it had been read does not park at all - it holds at
    reading size for its whole life, which is what `park: false` means on the entry."""
    short = DOCK_IN + READ_S + PARK_S - 0.15
    html, place, entry = _portrait_dock_build(tmp_path, "short", exitt=short)
    assert entry["park"] is False
    rects = _dock_rects(html, [DOCK_IN + 0.6, short - 0.05])
    for t, got in rects.items():
        assert abs(got[2] - 800) <= PARK_TOL, f"t={t}: the card shrank to {got[2]} - it parked"
        assert got[2] > place["w"] * 1.5, (t, got, place)


@needs_ffmpeg
@needs_browser
def test_the_parking_card_is_the_same_frame_in_two_browsers(tmp_path: Path):
    """Determinism (P39 T2) at the hardest t there is: mid-park, where the layout box, the clip's
    seek and the spring all resolve from t. Two fresh browsers, one hash."""
    import hashlib
    html, _, _ = _portrait_dock_build(tmp_path, "det")
    t = DOCK_IN + READ_S + PARK_S * 0.5
    a = RB.rgb_bytes(RB.render_frame(html, t, "9:16"))
    b = RB.rgb_bytes(RB.render_frame(html, t, "9:16"))
    assert a[0] == b[0] == RB.STAGE["9:16"]
    assert hashlib.sha256(a[1]).hexdigest() == hashlib.sha256(b[1]).hexdigest(), (
        "the parking card differs between two renders of the same t - the move is not pure in t")


# ---- P50 T16: one placement truth - every placer cuts its bands from the same boxes --------------
import itertools  # noqa: E402

import ledger_page as LPG  # noqa: E402
import measure_page_boxes as MPB  # noqa: E402

PLACE_CASES = list(itertools.product(MPB.BUILDERS, MPB.ASPECTS))


def _overlap(a: dict, b: dict) -> float:
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    h = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return max(0, w) * max(0, h)


@pytest.mark.parametrize("builder, aspect", PLACE_CASES)
def test_a_dock_on_a_measured_page_never_covers_the_chart_the_player_drew(builder, aspect):
    """E45 §1 against the PLAYER's own boxes, not against an estimate of them (R26-27): on every
    measured page, at both aspects, the parked card clears the plot, the source line, the badge rail
    and the caption's anchor - and sits inside one of the bands `free_bands` cut."""
    page = MPB.representative(builder)
    boxes = LPG.page_boxes(page, aspect)
    assert boxes["measured"] is True, f"{builder} {aspect}: the fixture should hold this page"
    place = B.page_place(page, aspect)
    if place is None:
        pytest.skip(f"{builder} {aspect}: no band wide enough for a card - the dock keeps its solo geometry")
    for forbidden in ("plot", "source", "rail", "caption_anchor"):
        assert _overlap(place, boxes[forbidden]) == 0, (
            f"{builder} {aspect}: the card {place} covers the {forbidden} {boxes[forbidden]}")
    bands = B.free_bands(boxes)
    assert any(_overlap(place, bd) == place["w"] * place["h"] for bd in bands), (
        f"{builder} {aspect}: the card {place} is not wholly inside any free band {bands}")


@pytest.mark.parametrize("builder, aspect", PLACE_CASES)
def test_the_parked_card_and_the_centred_card_read_the_same_bands(builder, aspect):
    """The two placers cannot disagree: `page_place` and `centred_place` both cut `free_bands` out of
    the same `page_boxes`, so a centred card lands in a band the parked card could also have used."""
    page = MPB.representative(builder)
    place = B.page_place(page, aspect)
    if place is None:
        pytest.skip(f"{builder} {aspect}: no band wide enough for a card")
    bands = B.free_bands(LPG.page_boxes(page, aspect))
    centred = B.centred_place(place, aspect, 1.0, page)
    assert any(bd["y"] - 1 <= centred["y"] and centred["y"] + centred["h"] <= bd["y"] + bd["h"] + 1
               for bd in bands if bd["band"] in ("above", "below", "foot")), (
        f"{builder} {aspect}: the centred card {centred} is in none of {bands}")
