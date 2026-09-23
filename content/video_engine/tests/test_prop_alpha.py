"""P69 T6d (1) - A PROP KEEPS ITS ALPHA THROUGH THE COMPILER (found on T23's frames, 2026-09-23).

`build_scene_timeline_f.data_uri` embedded every capped still as `Image.open(p).convert("RGB")` saved JPEG, and
`dock_uri` sends every dock still through it - so a `dock_kind:prop` cutout (the Fed, 282 x 259 RGBA) arrived on the
page as a BLACK SQUARE and T6b's hatch was cut to the square. Now a picture that USES transparency keeps it (a PNG at
the card width, its own bytes when it is already a PNG under the cap); a picture without alpha is the JPEG it always
was, to the byte; and the compiler's embed of the Fed paints the same pixels as the golden's own direct embed does
(`build_golden_sources._prop_stamp`: the page shows through the cutout's sky)."""
from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import render_baseline as RB  # noqa: E402

FED = ROOT / "content/video_engine/assets/props/cutouts/prop-federal-reserve-building-v1.png"


def _decode(uri: str):
    from PIL import Image
    head, data = uri.split(",", 1)
    return head, Image.open(io.BytesIO(base64.b64decode(data)))


def _old_jpeg(p: Path, cap: int) -> str:
    """The embed as it was before this slice - the pin a picture without alpha must still produce, to the byte."""
    from PIL import Image
    im = Image.open(p).convert("RGB")
    if im.width > cap:
        im = im.resize((cap, round(im.height * cap / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=B.Q, optimize=True, progressive=True)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"


def test_the_feds_cutout_embeds_as_a_png_with_its_own_alpha():
    from PIL import Image
    uri = B.dock_uri(FED)
    head, im = _decode(uri)
    assert head == "data:image/png;base64", head
    src = Image.open(FED).convert("RGBA")
    assert im.convert("RGBA").tobytes() == src.tobytes(), "under the cap: the cutout's own pixels, alpha and all"
    assert im.convert("RGBA").getpixel((0, 0))[3] == 0, "its corner is transparent - the page shows through"


def test_a_large_cutout_is_resized_to_the_cap_and_keeps_its_alpha(tmp_path):
    from PIL import Image
    big = Image.new("RGBA", (2400, 1200), (0, 0, 0, 0))
    big.paste((200, 60, 40, 255), (600, 300, 1800, 900))
    p = tmp_path / "big-cutout.png"
    big.save(p)
    head, im = _decode(B.data_uri(p, 800))
    assert head == "data:image/png;base64" and im.size == (800, 400)
    rgba = im.convert("RGBA")
    assert rgba.getpixel((10, 10))[3] == 0 and rgba.getpixel((400, 200)) == (200, 60, 40, 255)
    edge = rgba.getpixel((200, 200))   # the rect's corner, resampled: never darkened by the transparent black
    assert edge[3] == 0 or edge[0] >= 150, edge


def test_a_picture_without_alpha_is_the_jpeg_it_always_was(tmp_path):
    from PIL import Image
    photo = Image.new("RGB", (1600, 900), (90, 120, 150))
    photo.paste((220, 200, 180), (100, 100, 900, 600))
    p = tmp_path / "photo.png"
    photo.save(p)
    assert B.data_uri(p, 800) == _old_jpeg(p, 800)
    opaque = photo.convert("RGBA")                    # an RGBA container whose alpha is all 255 is still a photo
    q = tmp_path / "opaque-rgba.png"
    opaque.save(q)
    assert B.data_uri(q, 800) == _old_jpeg(q, 800)
    j = tmp_path / "photo.jpg"
    photo.save(j, "JPEG", quality=90)
    assert B.data_uri(j, 800) == _old_jpeg(j, 800)


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
def test_the_compilers_fed_paints_what_the_goldens_direct_embed_paints(tmp_path):
    """The prop-stamp golden's own timeline, served twice - with the golden's direct PNG embed and with the compiler's
    `dock_uri` of the same cutout: at the settled instant the card's corner is the PAGE (no square), in both."""
    from PIL import Image
    from playwright.sync_api import sync_playwright
    tl, uris = G._prop_stamp("own")
    aid = next(d["slide"] for sc in tl["scenes"] for d in sc.get("docks") or [])
    shots = {}
    w, h = RB.STAGE[tl.get("aspect") or "16:9"]
    PROBE = """(aid) => { const d = [...document.querySelectorAll('.dock')].find(e => e.dataset.slide === aid);
      const s = document.getElementById('stage').getBoundingClientRect(); const im = d && d.querySelector('img');
      const r = im.getBoundingClientRect(); return [r.x - s.x, r.y - s.y, r.width, r.height]; }"""
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        for tag, u in (("golden", dict(uris)), ("compiler", dict(uris, **{aid: B.dock_uri(FED)}))):
            html = tmp_path / f"{tag}.html"
            html.write_text(RB.instantiate(tl, u), encoding="utf-8")
            srv, port = RB.serve(html.parent)
            try:
                pg = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(pg, w, h)
                t = G.FRAME_T["prop-stamp"]
                RB.frame_png(pg, t, (w, h))
                pg.wait_for_timeout(120)
                png = RB.frame_png(pg, t, (w, h))
                shots[tag] = (Image.open(io.BytesIO(png)).convert("RGB"), pg.evaluate(PROBE, aid))
                pg.context.close()
            finally:
                srv.shutdown()
        br.close()
    for tag, (img, box) in shots.items():
        x, y, bw, bh = box
        corner = img.getpixel((int(x + 3), int(y + 3)))
        outside = img.getpixel((int(x - 12), int(y + 3)))
        assert sum(abs(a - b) for a, b in zip(corner, outside)) < 30, (tag, "the corner is the page, not a square", corner, outside)
    (gi, gb), (ci, cb) = shots["golden"], shots["compiler"]
    assert abs(gb[0] - cb[0]) < 1 and abs(gb[2] - cb[2]) < 1, (gb, cb)
    # the golden embeds a box-filtered PROXY (141 x 129) and the compiler the cutout itself (282 x 259): the same
    # picture at the same place, read as the mean colour of each quarter of the card (the detail differs, not the art)
    x, y, w, h = (int(v) for v in gb)
    for qx in (0, 1):
        for qy in (0, 1):
            box = (x + qx * w // 2, y + qy * h // 2, x + (qx + 1) * w // 2, y + (qy + 1) * h // 2)
            mg = [sum(c) / (len(c) or 1) for c in zip(*gi.crop(box).getdata())]
            mc = [sum(c) / (len(c) or 1) for c in zip(*ci.crop(box).getdata())]
            assert sum(abs(a - b) for a, b in zip(mg, mc)) < 12, ("the same picture at the same place", box, mg, mc)
