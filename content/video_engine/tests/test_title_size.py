"""P69 T37c (step 1) - BRAVOS'S TITLE SIZE, MEASURED AT FULL RESOLUTION (E99 s122).

The operator, on T37b's title sheet: "bravos title font is also bigger than ours ... we should bring our title font up
to their size". s122: the size is "the cap height as a fraction of the frame height, read off the full-resolution
Bravos frames (the T37b band's five, at 1024 px), never eyeballed (E38)". T37b's squint read quantised the cap to whole
px at 320 wide (5.0 on every frame), too coarse to set a size by, so the tool reads each GLYPH at the frame's own size:

  the tool   a title set in a known face at a known size is read back: its capitals' height, its x-height and its stroke;
             a word whose glyphs do not map (a hand face's joined pair) costs only that word
  the band   every band frame records its title's text, character count, cap / x-height / stroke as a fraction of the
             frame height, and the band's 1024 px frames (the resolvable ones) are summarised apart from the 512 px pair
  reproduce  the tool re-reads every recorded title number off the research frames (when they are on disk)

AMENDED (s122, the same day): the size stays (parity); the title GLOWS in its own ink and the shorts face goes BOLDER:
  the halo   the s117 halo read in a title mode finds a known glow and none where there is none; Bravos's title has
             none, so the glow's strength is our 390 px legibility bound, recorded beside it in the band
  the dials  the glow ON by default as one text-shadow dial in currentColor, the ink still unset, the face one token
             (ledger_page.TITLE_FACE: hand | heavy | sans; `sans` ships the long form's face)
  rendered   the glow is there and the counters stay open at 390 px; a cold seek paints the glowing title exactly as
             forward play does (mid-write and at rest); the bolder faces keep the hand's size within 5 %
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import measure_line_bloom as M  # noqa: E402

BAND_FILE = ROOT / "content/video_engine/assets/bravos-line-bloom.v1.json"
TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
GAP_BOUND = 0.16               # s122 amended: the glow within 3 px of the letters at 390 px, as a share of the ink's excess
ARIAL_BOLD_CAP_EM = 0.716      # Arial Bold's capHeight 1467 / unitsPerEm 2048
ARIAL_BOLD_X_EM = 0.519        # ... its xHeight 1062 / 2048


def _set_title(tmp: Path, text: str, size: int, frame=(1920, 1080)) -> tuple[Path, list[int]]:
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arialbd.ttf", size)
    except OSError:
        pytest.skip("no Arial Bold on this machine to set a known cap")
    im = Image.new("RGB", frame, (20, 24, 30))
    d = ImageDraw.Draw(im)
    d.text((120, 80), text, font=font, fill=(219, 132, 151))
    x0, y0, x1, y1 = d.textbbox((120, 80), text, font=font)
    p = tmp / f"title-{size}.png"
    im.save(p)
    return p, [x0 - 8, y0 - 8, x1 + 8, y1 + 8]


def test_the_tool_reads_a_titles_capitals_x_height_and_stroke_off_its_glyphs(tmp_path):
    text = "Foreign Holdings of US Treasuries"
    for size in (40, 60):
        p, box = _set_title(tmp_path, text, size)
        got = M.title_size(p, box, text)
        assert got["method"] == "glyphs", got
        assert got["chars"] == len(text) and got["capitals"] == 5, got
        assert abs(got["cap_px"] - ARIAL_BOLD_CAP_EM * size) <= 1.0, (size, got["cap_px"])
        assert abs(got["x_px"] - ARIAL_BOLD_X_EM * size) <= 0.08 * ARIAL_BOLD_X_EM * size, (size, got["x_px"])   # round letters overshoot
        assert got["cap_frac"] == pytest.approx(got["cap_px"] / 1080, abs=1e-5)
        assert got["cap_px1080"] == pytest.approx(got["cap_frac"] * 1080, abs=0.01)
        assert 0.08 * size <= got["stroke_px"] <= 0.2 * size, got["stroke_px"]


def test_a_word_whose_glyphs_do_not_map_costs_only_that_word(tmp_path):
    p, box = _set_title(tmp_path, "Foreign Holdings of US Treasuries", 60)
    got = M.title_size(p, box, "Foreign Holdings of USA Treasuries")   # a hand face's joined pair: one word off by one
    assert got["method"] == "words 4/5", got
    assert got["capitals"] == 3 and abs(got["cap_px"] - ARIAL_BOLD_CAP_EM * 60) <= 1.0, got


def test_a_title_whose_glyphs_do_not_map_falls_back_to_the_tall_cluster_and_says_so(tmp_path):
    p, box = _set_title(tmp_path, "HEIGHT", 60)
    got = M.title_size(p, box, "a different text")
    assert got["method"] == "cluster", got
    assert abs(got["cap_px"] - ARIAL_BOLD_CAP_EM * 60) <= 1.5, got


def test_the_tool_reads_the_same_fraction_at_any_frame_width(tmp_path):
    text = "AI Builders Versus AI Spenders"
    big, bbox = _set_title(tmp_path, text, 60)
    small = tmp_path / "small.png"
    Image.open(big).resize((1024, 576), Image.LANCZOS).save(small)
    k = 1024 / 1920
    got_big = M.title_size(big, bbox, text)
    got_small = M.title_size(small, [v * k for v in bbox], text)
    assert got_small["cap_frac"] == pytest.approx(got_big["cap_frac"], rel=0.03)


def band() -> dict:
    return json.loads(BAND_FILE.read_text(encoding="utf-8"))


def test_every_band_frame_records_its_titles_size_as_a_share_of_the_frame_height():
    b = band()
    for f in b["frames"]:
        t = f["title"]
        assert t["text"] and t["chars"] == len(t["text"]), f["id"]
        for k in ("cap_px", "cap_frac", "cap_px1080", "x_frac", "stroke_frac"):
            assert isinstance(t["measured"][k], float), (f["id"], k)
        assert t["measured"]["method"] == "glyphs", f["id"]
    s = b["title_size"]
    assert s["band_1024"]["n"] == 3 and s["band_512"]["n"] == 2
    assert 0.02 <= s["band_1024"]["cap_frac"]["mean"] <= 0.04
    assert s["band_1024"]["cap_frac"]["max"] - s["band_1024"]["cap_frac"]["min"] < 0.001   # one title size, three frames


def test_the_tool_reproduces_every_recorded_bravos_title_number():
    from test_line_bloom import _frames_root  # noqa: PLC0415 - one resolver for the gitignored frames
    root = _frames_root()
    if root is None:
        pytest.skip("the Bravos research frames are not on disk (gitignored): set BRAVOS_FRAMES_ROOT")
    for f in band()["frames"]:
        t = f["title"]
        got = M.title_size(M.resolve(f["frame"], root), f["title_box"], t["text"])
        for k in ("cap_frac", "x_frac"):
            assert got[k] == pytest.approx(t["measured"][k], rel=0.02), (f["id"], k, got[k])


# ---- s122 amended: THE GLOW - Bravos's title halo read by the s117 tool in a title mode --------------------------------


def _set_glow_title(tmp: Path, sigma: float, alpha: float = 0.9) -> tuple[Path, list[int]]:
    """A title in a known face whose own ink is blurred UNDER it (the glow the tool must find), or none at sigma 0."""
    from PIL import ImageFilter, ImageFont  # noqa: PLC0415
    try:
        font = ImageFont.truetype("arialbd.ttf", 56)
    except OSError:
        pytest.skip("no Arial Bold on this machine")
    ink = (255, 138, 76)
    text = Image.new("L", (1920, 1080), 0)
    d = ImageDraw.Draw(text)
    d.text((140, 90), "Foreign Holdings", font=font, fill=255)
    x0, y0, x1, y1 = d.textbbox((140, 90), "Foreign Holdings", font=font)
    im = Image.new("RGB", (1920, 1080), (37, 49, 60))
    if sigma:
        halo = text.filter(ImageFilter.GaussianBlur(sigma)).point(lambda v: int(v * alpha))
        im = Image.composite(Image.new("RGB", im.size, ink), im, halo)
    im = Image.composite(Image.new("RGB", im.size, ink), im, text)
    p = tmp / f"glow-{sigma}.png"
    im.save(p)
    return p, [x0 - 6, y0 - 6, x1 + 6, y1 + 6]


def test_the_title_halo_read_finds_a_known_glow_and_reads_none_where_there_is_none(tmp_path):
    none = M.title_halo(*_set_glow_title(tmp_path, 0.0))
    soft, wide = (M.title_halo(*_set_glow_title(tmp_path, s)) for s in (3.0, 7.0))
    assert abs(none["glow_3_12"]) < 0.5, none                     # rings 1-2 are the antialiased edge; past them, nothing
    assert soft["glow_3_12"] > 3.0 and wide["glow_3_12"] > soft["glow_3_12"], (soft, wide)
    assert wide["halo_area_1080"] > soft["halo_area_1080"] > none["halo_area_1080"]


def test_the_band_says_bravos_title_has_no_halo_and_records_our_glow_by_its_legibility_bound():
    b = band()
    s = b["title_size"]["halo"]
    for f in b["frames"]:
        assert f["title"]["halo"]["glow_3_12"] <= 0.5, f["id"]    # at or under the ground on every band frame
    assert s["band_1024"]["glow_3_12"]["max"] <= 0.5 and s["band_512"]["glow_3_12"]["max"] <= 0.5
    rows, chosen = s["ours_candidates"]["rows"], s["ours_candidates"]["chosen"]
    stronger = [r["gap_share_390"] for r in rows.values() if r["glow_3_12"] > rows[chosen]["glow_3_12"]]
    assert rows[chosen]["gap_share_390"] <= GAP_BOUND < min(stronger)    # the strongest glow inside the bound
    assert rows[chosen]["css"] in TEMPLATE.read_text(encoding="utf-8")   # the recorded choice IS the template's default


def test_the_tool_reproduces_every_recorded_bravos_title_halo():
    from test_line_bloom import _frames_root  # noqa: PLC0415
    root = _frames_root()
    if root is None:
        pytest.skip("the Bravos research frames are not on disk (gitignored): set BRAVOS_FRAMES_ROOT")
    for f in band()["frames"]:
        got = M.title_halo(M.resolve(f["frame"], root), f["title_box"])
        assert got["glow_3_12"] == pytest.approx(f["title"]["halo"]["glow_3_12"], abs=0.3), f["id"]


# ---- the dials: the glow ON (s122 decided it), the face one token, the ink still unset ----------------------------------


def test_the_glow_is_one_dial_on_by_default_in_the_titles_own_ink_and_the_ink_stays_unset():
    css = TEMPLATE.read_text(encoding="utf-8")
    assert re.search(r"\.lp-title \{[^}]*text-shadow: var\(--lp-title-glow, 0 0 [.\d]+em currentColor, 0 0 [.\d]+em currentColor\)", css)
    assert re.search(r"\.lp-title \.g \{ padding: var\(--lp-title-glow-pad, ([.\d]+)em\); margin: calc\(-1 \* var\(--lp-title-glow-pad, \1em\)\)", css)
    assert not re.search(r"--lp-title-ink:\s*#", css), "s122: the operator picks the orange from the sheet - the ink stays unset"
    assert "filter: var(--lp-title-glow" not in css      # a filter over the glyphs is not seek-exact (T37c)


def test_the_face_is_one_token_hand_by_default_and_a_hand_build_carries_no_field():
    import build_scene_timeline_f as BST  # noqa: PLC0415
    import ledger_page as LPG  # noqa: PLC0415
    assert LPG.TITLE_FACE == "hand" and LPG.TITLE_FACES == ("hand", "heavy", "sans")
    assert BST.title_face_field() == {}
    assert BST.title_face_field("sans") == {"title_face": "sans"}
    with pytest.raises(ValueError, match="TITLE_FACE"):
        BST.title_face_field("bold")
    assert 'LP_TITLE_FACES = Object.freeze(["hand", "heavy", "sans"])' in ENGINE.read_text(encoding="utf-8")
    css = TEMPLATE.read_text(encoding="utf-8")
    for face in ("heavy", "sans"):
        assert f".lp-title-face-{face} .lp-title" in css


def test_a_sans_title_ships_the_long_forms_face_in_either_aspect_and_a_hand_one_does_not():
    import build_scene_timeline_f as BST  # noqa: PLC0415
    page = {"scenes": [{"world": {"page": {"builder": "dense-line", "title": "t"}}}]}
    for aspect in ("16:9", "9:16"):
        tl = dict(page, aspect=aspect)
        assert BST.longform_assets(tl) == {}
        assert list(BST.longform_assets(dict(tl, title_face="sans"))) == [BST.LONGFORM_FONT_ASSET]
    assert BST.longform_assets(dict(page, title_face="heavy")) == {}


# ---- rendered: the glow is there, legible, seek-exact; the faces keep the size ----------------------------------------


def _chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa: PLC0415
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:  # noqa: BLE001 - any failure means no browser here
        return False


needs_browser = pytest.mark.skipif(not _chromium(), reason="playwright chromium not installed")
SOLO_TITLE_BOX = [40, 40, 1400, 105]
SOLO_TITLE = "The sharpest chart on YouTube - plus the layer it needed"


def _render(tmp: Path, name: str, *, face: str | None = None, css: str = "") -> Path:
    import base64  # noqa: PLC0415
    import build_scene_timeline_f as BST  # noqa: PLC0415
    import render_baseline as RB  # noqa: PLC0415
    tl, uris, t0, aspect = RB.load_surface(name)
    if face:
        tl = dict(tl, title_face=face)
        if face == "sans":
            uris = dict(uris, **{BST.LONGFORM_FONT_ASSET: "data:font/ttf;base64,"
                                 + base64.b64encode(BST.LONGFORM_FONT_FILE.read_bytes()).decode()})
    src = TEMPLATE.read_text(encoding="utf-8")
    if css:
        i = src.index("</style>")
        src = src[:i] + "  .lp { " + css + " }\n" + src[i:]
    tag = f"{name}-{face or 'hand'}-{len(css)}"
    tpl = tmp / f"t-{tag}.html"
    tpl.write_text(src, encoding="utf-8")
    html = tmp / f"{tag}.html"
    html.write_text(RB.instantiate(tl, uris, tpl), encoding="utf-8")
    out = tmp / f"{tag}.png"
    out.write_bytes(RB.render_frame(html, t0, aspect))
    return out


@needs_browser
def test_the_rendered_title_glows_and_at_390_px_its_counters_stay_open(tmp_path):
    from scipy import ndimage  # noqa: PLC0415
    on = _render(tmp_path, "solo-chipmakers")
    off = _render(tmp_path, "solo-chipmakers", css="--lp-title-glow: none;")
    h_on, h_off = M.title_halo(on, SOLO_TITLE_BOX), M.title_halo(off, SOLO_TITLE_BOX)
    assert h_off["glow_3_12"] < 0.5 and h_on["glow_3_12"] > 2.0, (h_off["glow_3_12"], h_on["glow_3_12"])
    k = 390 / 1920
    x0, y0, x1, y1 = (int(round(v * k)) for v in SOLO_TITLE_BOX)
    l_off = M.luma(M.load_rgb(off, 390))[y0:y1 + 1, x0:x1 + 1]
    l_on = M.luma(M.load_rgb(on, 390))[y0:y1 + 1, x0:x1 + 1]
    g = float(np.median(l_off))
    text = (l_off - g) >= 0.5 * np.percentile(l_off - g, 99.5)
    gaps = (ndimage.distance_transform_edt(~text) <= 3) & ~text
    share = float(l_on[gaps].mean() - g) / float(np.percentile(l_on[text], 90) - g)
    assert share <= GAP_BOUND, share                              # the band's legibility bound, on the default ink


@needs_browser
def test_a_cold_seek_paints_the_glowing_title_exactly_as_forward_play_does():
    import io  # noqa: PLC0415
    import render_baseline as RB  # noqa: PLC0415
    from playwright.sync_api import sync_playwright  # noqa: PLC0415
    tl, uris, _, aspect = RB.load_surface("solo-chipmakers")
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "p.html").write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(d)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True)

                def page():
                    pg = br.new_context(viewport={"width": w, "height": h}).new_page()
                    pg.goto(f"http://127.0.0.1:{port}/p.html", wait_until="networkidle", timeout=120000)
                    RB.prepare_page(pg, w, h)
                    return pg
                fwd, shots = page(), {}
                for i in range(84, 145):                           # 3.5 .. 6.0 s at 24 fps: the title writes 3.9 - 4.7 s
                    png = RB.frame_png(fwd, i / 24, (w, h))
                    if i in (102, 108, 144):                       # mid-write 4.25 and 4.5 s; at rest 6.0 s
                        shots[i / 24] = png
                for t, png in shots.items():
                    cold = page()
                    a = Image.open(io.BytesIO(RB.frame_png(cold, t, (w, h)))).convert("RGB").crop((0, 0, 1920, 112))
                    cold.context.close()
                    b = Image.open(io.BytesIO(png)).convert("RGB").crop((0, 0, 1920, 112))
                    assert a.tobytes() == b.tobytes(), f"the title band at {t:.3f} s: forward play paints another frame than a cold seek"
                br.close()
        finally:
            srv.shutdown()


@needs_browser
def test_the_bolder_faces_keep_the_hands_size_within_five_percent_and_heavy_is_heavier(tmp_path):
    off = "--lp-title-glow: none;"
    base = M.title_size(_render(tmp_path, "solo-chipmakers", css=off), SOLO_TITLE_BOX, SOLO_TITLE)
    got = {f: M.title_size(_render(tmp_path, "solo-chipmakers", face=f, css=off), SOLO_TITLE_BOX, SOLO_TITLE) for f in ("heavy", "sans")}
    for face, r in got.items():
        assert r["x_px"] == pytest.approx(base["x_px"], rel=0.06), (face, r["x_px"], base["x_px"])
        if r["method"] != "cluster":                              # a joined hand falls back to capitals + ascenders
            assert r["cap_px"] == pytest.approx(base["cap_px"], rel=0.05), (face, r["cap_px"], base["cap_px"])
    assert got["heavy"]["stroke_px"] >= 1.2 * base["stroke_px"], (got["heavy"]["stroke_px"], base["stroke_px"])
