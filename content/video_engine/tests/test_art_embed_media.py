"""THE ART-EMBED SURFACE HOLDS PICTURES AND CLIPS (the operator, 2026-09-13: "yes thats the tv surface should
definitely be prepared to hold video and images - that would be silly if it didn't").

Bravos shows someone else's words as the whole broadcast clip playing on a TV on a studio wall. A declared surface
(E66: used whole) now takes an IMAGE dock and a VIDEO dock as a PICTURE, not only a press card: the dock row names
`{"embed": "tv"}` and, optionally, `{"fit": "cover" | "contain"}`; a still or a clip on a surface is `cover` unless the
row says `contain` (E95, 2026-09-13: "stills should probably fill the tv surface"). The picture fills the surface's quad corner to corner through the same homography the press card rides,
under the room's darken and a screen's sheen; a clip seeks on the dock's clock (t - enter), muted; and a camera push
into the surface (E59 reason 4) carries the picture with the wall it is on.

A PRESS card on a surface, and a CARD whose evidence carries badges, a record, a chart or a stack, is the reflowed
CARD it always was (E66) - its entry carries no `fit`, byte-for-byte, and a `fit` on one is refused: a card is not a
picture (the parent, 2026-09-13).

The browser half renders the APPROVED washi-tv plate with its measured `tv` quad, a still and a clip already on disk
(the evidence clip and its own contact sheet), and judges the pixels against the SAME build whose two docks carry a
transparent picture - the same wash, sheen, falloff and camera, nothing on the glass - so every changed pixel is the
picture, and it must live inside the TV's quad. Set EMBED_MEDIA_PROOF_DIR to keep the frames.
"""
from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

SOURCES = ROOT / "content/video_engine/tests/golden/sources"
TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"
PLATES = ROOT / "content/video_engine/channel-assets/money-physics/plates"
PLATE = PLATES / "stills/art-embed-washi-tv.png"
PLATE_ID = PLATES / "art-embed-washi-tv.png"          # plate_embeds reads <stem>.layers.json beside this name
EVIDENCE = ROOT / "content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/assets/evidence_clips"
CLIP = EVIDENCE / "clip_cnbc_yield_495.mp4"
STILL = EVIDENCE / "contact_sheets/clip_cnbc_yield_495_contact_sheet.jpg"
WHERE = "shot row 2 (4-12s) dock ev-clip"
QUAD = [[0.2, 0.2], [0.9, 0.2], [0.9, 0.5], [0.2, 0.5]]


# ---- the compiler: `fit` is a surface's option, and a clip on a surface covers it -------------------------

def test_fit_is_a_dock_option_that_names_how_a_picture_takes_its_surface():
    assert "fit" in B.DOCK_OPTS and B.EMBED_FITS == ("cover", "contain")
    for fit in B.EMBED_FITS:
        assert B.dock_opts({"embed": "tv", "fit": fit}) == {"embed": "tv", "fit": fit}
    for bad in ("fill", "", None, 1, True):
        with pytest.raises(ValueError) as e:
            B.dock_opts({"embed": "tv", "fit": bad})
        assert "fit" in str(e.value) and "cover|contain" in str(e.value)


def test_fit_without_a_surface_or_on_a_press_card_is_refused_by_name():
    with pytest.raises(ValueError) as bare:
        B.dock_opts({"fit": "cover"})
    assert "fit is how a picture takes a SURFACE" in str(bare.value)
    with pytest.raises(ValueError) as press:
        B.dock_opts({"embed": "tv", "fit": "cover",
                     "press": {"source": "THE HERALD", "phrase": {"x0": 0.1, "y0": 0.2, "x1": 0.6, "y1": 0.4}}})
    assert "a press card REFLOWS to its surface" in str(press.value)


def test_a_clip_on_a_surface_covers_it_by_default_unchanged(tmp_path):
    mp4 = tmp_path / "clip.mp4"; mp4.write_bytes(b"\x00\x00\x00\x18ftypmp42")
    assert B.embed_fit({"embed": "tv"}, mp4) == "cover", "a clip on a TV is the broadcast, whole"
    assert B.embed_fit({"embed": "tv", "fit": "contain"}, mp4) == "contain"
    assert B.embed_fit({}, mp4) is None, "no surface, no fit"


def test_e95_a_still_on_a_surface_covers_it_by_default_as_a_clip_does(tmp_path):
    png = tmp_path / "still.png"; png.write_bytes(b"\x89PNG\r\n\x1a\n")
    assert B.embed_fit({"embed": "tv"}, png) == "cover", "E95: a still on a surface fills it, exactly as a clip does"
    assert B.embed_fit({}, png) is None, "no surface, no fit"


def test_e95_a_still_letterboxes_only_by_name(tmp_path):
    png = tmp_path / "still.png"; png.write_bytes(b"\x89PNG\r\n\x1a\n")
    assert B.embed_fit({"embed": "tv", "fit": "contain"}, png) == "contain"
    assert B.embed_fit({"embed": "tv", "fit": "cover"}, png) == "cover"


def test_e95_the_press_card_on_a_surface_is_still_the_reflowed_card(tmp_path):
    png = tmp_path / "press.png"; png.write_bytes(b"\x89PNG\r\n\x1a\n")
    press = {"source": "THE HERALD", "phrase": {"x0": 0.1, "y0": 0.2, "x1": 0.6, "y1": 0.4}}
    dopt = B.dock_opts({"embed": "tv", "press": press})
    assert B.embed_fit(dopt, png) is None, "E66: a press card REFLOWS to its surface - never a fitted picture"
    assert "fit" not in B.embed_entry("tv", {"quad": QUAD, "kind": "screen"}, card_aspect=0.3,
                                      fit=B.embed_fit(dopt, png)), "the press card's entry is byte-identical"

def test_e95_a_still_carrying_badges_on_a_surface_stays_the_card(tmp_path):
    png = tmp_path / "record.png"; png.write_bytes(b"\x89PNG\r\n\x1a\n")
    badges = {"badges": [{"label": "MAMAA", "value": "+20%", "tag": "matches the index", "accent": "cobalt"}]}
    assert B.embed_fit({"embed": "paper"}, png, badges) is None, "a card with a badge rail is not a picture"
    assert B.embed_fit({"embed": "paper"}, png, {"badges": []}) == "cover", "an empty rail is a bare still"


def test_e95_a_record_chart_or_stack_payload_on_a_surface_stays_the_card(tmp_path):
    png = tmp_path / "card.png"; png.write_bytes(b"\x89PNG\r\n\x1a\n")
    for key, payload in (("record", {"rows": [1]}), ("chart", {"series": [1]}), ("stack", ["a", "b"])):
        assert B.embed_fit({"embed": "tv"}, png, {"badges": [], key: payload}) is None, key


def test_e95_an_explicit_fit_on_a_card_is_refused_by_name(tmp_path):
    png = tmp_path / "card.png"; png.write_bytes(b"\x89PNG\r\n\x1a\n")
    for ev in ({"badges": [{"label": "S&P 500", "value": "+21%"}]}, {"chart": {"series": [1]}}):
        with pytest.raises(ValueError) as e:
            B.embed_fit({"embed": "tv", "fit": "cover"}, png, ev)
        assert "a card is not a picture" in str(e.value)


def test_the_entry_carries_fit_only_when_there_is_one():
    e = B.embed_entry("tv", {"quad": QUAD, "kind": "screen"}, fit="cover")
    assert e["fit"] == "cover" and e["kind"] == "screen"
    assert "fit" not in B.embed_entry("tv", {"quad": QUAD, "kind": "screen"}), "byte-identical without it"
    with pytest.raises(ValueError):
        B.embed_entry("tv", {"quad": QUAD}, fit="stretch")


def test_the_compiler_still_lets_a_clip_and_a_still_land_and_still_refuses_what_it_refused():
    embeds = B.plate_embeds(PLATE_ID)
    assert "tv" in embeds and embeds["tv"]["kind"] == "screen"
    world = {"asset_id": "art-embed-washi-tv", "sha256": "0" * 64}
    for species in ("clip", "deck", "photo", None):
        assert B.embed_error(world, embeds, "tv", WHERE, species=species) is None, species
    assert "never embed" in B.embed_error(world, embeds, "tv", WHERE, species="chart")
    assert "no painted surface" in B.embed_error({"kind": B.SPECIES_CLIP, "asset_id": "c"}, embeds, "tv", WHERE)
    assert "not a surface" in B.embed_error(world, embeds, "poster", WHERE)


# ---- the browser: the picture fills the TV's quad, the clip moves with t, the push carries it --------------

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
needs_assets = pytest.mark.skipif(not (PLATE.exists() and CLIP.exists() and STILL.exists()),
                                  reason="the approved plate, the evidence clip or its contact sheet is not on disk")

IMG_IN, IMG_OUT = 1.0, 6.0
CLIP_IN, CLIP_OUT = 7.0, 20.0
PUNCH_AT, PUNCH_DUR = 14.0, 2.6
T_IMG, T_V1, T_V2, T_PUNCH = 4.0, 9.0, 11.5, 15.2     # the punch holds at full scale from 14.42 to 16.1
PUNCH_SCALE = 1.14                                    # the engine's SP.PUNCH_SCALE
THRESH = 12                                           # a changed pixel: any channel moved by more than this
SPILL_MAX = 150                                       # px changed outside the quad grown by MARGIN - an edge's antialias, not a picture
MARGIN = 6.0


def _blank_png() -> bytes:
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGBA", (16, 9), (0, 0, 0, 0)).save(buf, "PNG")
    return buf.getvalue()


def _build(tmp_path: Path, blank: bool) -> Path:
    """The two docks on the approved plate's TV - or, `blank`, the same two docks carrying a transparent picture."""
    import base64
    tl = json.loads((SOURCES / "art-embed.timeline.json").read_text(encoding="utf-8"))
    uris = json.loads((SOURCES / "art-embed.uris.json").read_text(encoding="utf-8"))
    tv = B.plate_embeds(PLATE_ID)["tv"]
    still, clip = "ev-embed-still", "ev-embed-clip"
    video = B.DOCK_KIND_IMAGE if blank else B.DOCK_KIND_VIDEO
    tl["runtime_s"] = 20.0
    tl["captions"], tl["caption_pages"], tl["sound"] = [], [], []
    tl["evidence"] = {
        still: {"title": "a still on the screen", "source": "contact sheet", "species": "deck",
                "document": {"path": "evidence", "sha256": "0" * 64}, "badges": []},
        clip: {**({} if blank else {"kind": B.DOCK_KIND_VIDEO}), "title": "a clip on the screen",
               "source": "evidence clip", "species": "clip", "document": {"path": "evidence", "sha256": "0" * 64},
               "badges": []},
    }
    docks = [
        B.dock_entry(still, 0, IMG_IN, IMG_OUT, 0, B.DOCK_KIND_IMAGE,
                     embed=B.embed_entry("tv", tv, fit=B.embed_fit({"embed": "tv"}, STILL),   # E95: the default
                                         card_aspect=B.image_aspect(STILL))),
        B.dock_entry(clip, 0, CLIP_IN, CLIP_OUT, 0, video,
                     embed=B.embed_entry("tv", tv, fit=B.embed_fit({"embed": "tv"}, CLIP))),
    ]
    species = [{"kind": "punch", "at": PUNCH_AT, "dur": PUNCH_DUR, "target": {"kind": "embed", "name": "tv"}}]
    B.resolve_embed_targets(species, {"tv": tv}, "embed media proof")
    tl["scenes"] = [{"scene_id": "s01", "world": {"asset_id": "art-embed-washi-tv", "sha256": "0" * 64,
                                                  "ken_burns": {"scale": 0, "x": 0, "y": 0}},
                     "exit": "cut", "span": [0.0, 20.0], "docks": docks, "species": species}]
    for k in ("plate-study", "ev-embed-quote", "ev-embed-record"):
        uris.pop(k, None)
    uris["art-embed-washi-tv"] = B.data_uri(PLATE)
    if blank:
        uris[still] = uris[clip] = "data:image/png;base64," + base64.b64encode(_blank_png()).decode("ascii")
    else:
        uris[still], uris[clip] = B.dock_uri(STILL), B.dock_uri(CLIP)
    html = tmp_path / ("embed-blank.html" if blank else "embed-media.html")
    html.write_text(RB.instantiate(tl, uris, TEMPLATE), encoding="utf-8")
    return html


def _frames(html: Path, ts) -> dict:
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE["9:16"]
    srv, port = RB.serve(html.parent)
    out = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=180000)
            RB.prepare_page(page, w, h)
            for t in ts:
                RB.frame_png(page, t, (w, h))          # one settle pass: a pooled clip's first seek lands
                out[t] = RB.frame_png(page, t, (w, h))
            browser.close()
    finally:
        srv.shutdown()
    return out


def _img(png: bytes):
    from PIL import Image
    return Image.open(io.BytesIO(png)).convert("RGB")


def _px_quad(quad, s: float = 1.0):
    W, H = RB.STAGE["9:16"]
    pts = [(x * W, y * H) for x, y in quad]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    ox, oy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2     # a punch zooms about the surface's box centre
    return [(ox + s * (x - ox), oy + s * (y - oy)) for x, y in pts]


def _grow(pts, px: float):
    cx = sum(p[0] for p in pts) / 4
    cy = sum(p[1] for p in pts) / 4
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        n = max(1e-6, (dx * dx + dy * dy) ** 0.5)
        out.append((x + dx / n * px, y + dy / n * px))
    return out


def _count(mask) -> int:
    return mask.histogram()[255]


def _judge(a, b, quad_pts, thresh: int = THRESH) -> tuple[float, float, int]:
    """(share of the quad that changed, share of the 24 px band just inside its edges that changed, changed px
    OUTSIDE the quad grown by MARGIN). The band is the letterbox test: an inscribed or contained picture leaves it."""
    from PIL import Image, ImageChops, ImageDraw

    def poly(pts):
        m = Image.new("L", a.size, 0)
        ImageDraw.Draw(m).polygon(pts, fill=255)
        return m

    r, g, bl = ImageChops.difference(a, b).split()
    diff = ImageChops.lighter(ImageChops.lighter(r, g), bl).point(lambda v: 255 if v > thresh else 0)
    inner, outer = poly(_grow(quad_pts, -MARGIN)), poly(_grow(quad_pts, MARGIN))
    band = ImageChops.subtract(inner, poly(_grow(quad_pts, -MARGIN - 24)))
    inside = _count(ImageChops.multiply(diff, inner)) / max(1, _count(inner))
    edge = _count(ImageChops.multiply(diff, band)) / max(1, _count(band))
    return inside, edge, _count(ImageChops.subtract(diff, outer))


def _keep(frames: dict, prefix: str) -> None:
    keep = os.environ.get("EMBED_MEDIA_PROOF_DIR")
    if not keep:
        return
    d = Path(keep)
    d.mkdir(parents=True, exist_ok=True)
    for t, png in frames.items():
        (d / f"{prefix}@{t:05.2f}.png").write_bytes(png)


@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    if not (_chromium_available() and PLATE.exists() and CLIP.exists() and STILL.exists()):
        pytest.skip("browser or assets absent")
    tmp = tmp_path_factory.mktemp("embed-media")
    ts = (T_IMG, T_V1, T_V2, T_PUNCH)
    full, blank = _frames(_build(tmp, False), ts), _frames(_build(tmp, True), ts)
    _keep(full, "media")
    _keep(blank, "blank")
    return full, blank


@needs_browser
@needs_assets
def test_an_image_on_the_tv_fills_its_quad_whole_and_nothing_spills(rendered):
    full, blank = rendered
    inside, edge, spill = _judge(_img(full[T_IMG]), _img(blank[T_IMG]), _px_quad(B.plate_embeds(PLATE_ID)["tv"]["quad"]))
    assert inside > 0.9, f"only {inside:.0%} of the TV's quad carries the picture"
    assert edge > 0.95, f"only {edge:.0%} of the band inside the bezel carries it - letterboxed or inscribed, not whole"
    assert spill < SPILL_MAX, f"{spill} px changed outside the TV's quad - the picture spills off the bezel"


@needs_browser
@needs_assets
def test_a_clip_on_the_tv_fills_its_quad_and_shows_a_different_frame_at_a_later_t(rendered):
    full, blank = rendered
    quad = _px_quad(B.plate_embeds(PLATE_ID)["tv"]["quad"])
    for t in (T_V1, T_V2):
        inside, edge, spill = _judge(_img(full[t]), _img(blank[t]), quad)
        assert inside > 0.9 and edge > 0.95, f"t={t}: the clip covers {inside:.0%} of the quad, {edge:.0%} of its edge band"
        assert spill < SPILL_MAX, f"t={t}: {spill} px of the clip outside the TV's quad"
    moved, _, spill = _judge(_img(full[T_V1]), _img(full[T_V2]), quad)
    assert moved > 0.1, f"the clip held one frame across {T_V2 - T_V1}s ({moved:.0%} changed) - a still card"
    assert spill < SPILL_MAX


@needs_browser
@needs_assets
def test_a_push_into_the_tv_carries_the_clip_with_the_wall(rendered):
    full, blank = rendered
    pushed = _px_quad(B.plate_embeds(PLATE_ID)["tv"]["quad"], PUNCH_SCALE)
    inside, edge, spill = _judge(_img(full[T_PUNCH]), _img(blank[T_PUNCH]), pushed)
    assert inside > 0.9 and edge > 0.95, \
        f"mid-push the clip covers {inside:.0%} of the pushed TV, {edge:.0%} of its edge band - it stayed in screen space"
    assert spill < SPILL_MAX, f"mid-push {spill} px of the clip outside the pushed TV"
