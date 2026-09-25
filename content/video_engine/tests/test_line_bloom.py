"""P69 T37b - THE LINES BLOOM, THEIR NAMES WEAR THEIR INK, THE TITLE IS ONE DIAL, AND THE SQUINT IS MEASURED (E99 s117-s120).

The operator, on our solo beside Bravos JPN 05:20 / 05:23.5: Bravos's primary line is "a higher vibrancy/contrast/
electricity than we do ... then fades theirs to a higher contrast" (s117); "we use plain white text which is pretty low
visibility" (s118); "we need a louder color the titles" (s119); and shrunk small, "not clear what we're immediately
talking about" (s120). Every number is MEASURED by one tool (measure_line_bloom.py) - on Bravos first, then on ours:

  the tool       a synthetic frame whose stroke, halo and gap are known is read back right; the Bravos band file
                 re-measures (when the research frames are on disk - they are gitignored research)
  the bloom      the solo golden's PRIMARY before its solo, read at the Bravos frames' own 1024 px width, has a hot core
                 and a halo inside the band's three 1024 px frames; at 390 px (the phone) the stroke is still a line
  the solo       the named line against the muted ones inside the band's lit/muted ratio, and it carries the plot's
                 contrast at 320 px as Bravos's lit lines do
  the names      every end tag is drawn in its own line's ink; context never blooms, a history never blooms
  the WARN       a name whose ink reads under the text floor (4.5:1) on its ground is reported with its ratio
  the title      one dial, unset: every page's title draws as it did
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import measure_line_bloom as M  # noqa: E402
import series_inks as SI  # noqa: E402

BAND_FILE = ROOT / "content/video_engine/assets/bravos-line-bloom.v1.json"
TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
SURFACE = "solo-chipmakers"
BOX = [152, 250, 1097, 818]          # the divergence page's plot at 16:9 full stage (inside the axes, clear of the tags)
BEFORE_T = 11.7                      # every line at its ink: series 0 (the memory makers, orange) is the primary
PRIMARY_INK, SOLO_INK = "#FF8A4C", "#34F5C5"
CHARCOAL = "#25313C"


def band() -> dict:
    return json.loads(BAND_FILE.read_text(encoding="utf-8"))


def within(v: float, b: dict) -> bool:
    return b["min"] <= v <= b["max"]


# ---- the tool, on a frame whose answers are known ----------------------------------------------------------------


def _synthetic(tmp: Path, halo_sigma: float, muted_alpha: float = 0.3) -> Path:
    """1920 x 1080 charcoal, a teal line 6 px wide with a gaussian halo of its ink, a thin dim cobalt line below it."""
    w, h = 1920, 1080
    ground = Image.new("RGB", (w, h), (37, 49, 60))
    halo = Image.new("RGB", (w, h), (0, 0, 0))
    ImageDraw.Draw(halo).line([(200, 400), (1700, 520)], fill=(52, 245, 197), width=6)
    halo = halo.filter(ImageFilter.GaussianBlur(halo_sigma))
    a = np.asarray(ground).astype(float) + np.asarray(halo).astype(float) * 0.9
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.line([(200, 400), (1700, 520)], fill=(52, 245, 197), width=6)
    mut = tuple(round(37 * (1 - muted_alpha) + c * muted_alpha) for c in (79, 195, 255))
    d.line([(200, 800), (1700, 760)], fill=mut, width=3)
    p = tmp / f"synthetic-{halo_sigma}.png"
    im.save(p)
    return p


def test_the_tool_reads_a_known_stroke_its_halo_and_the_gap_to_a_muted_line(tmp_path):
    tight, wide = (M.measure(_synthetic(tmp_path, s), "#34F5C5", [150, 300, 1750, 900]) for s in (3.0, 12.0))
    for got in (tight, wide):
        assert 4.5 <= got["stroke_px"] <= 7.5, got["stroke_px"]              # a 6 px stroke
        assert got["core_sat"] > 0.6 and got["core_L"] > 80, got                # the ink itself, no white core drawn
        assert got["muted_lum"] is not None and got["lit_muted_ratio"] > 3, got   # the thin cobalt at 0.3 is the muted mark
    assert wide["halo_r50_px1080"] > tight["halo_r50_px1080"] + 3, (tight, wide)   # a wider glow reads wider
    assert wide["halo_area_1080"] > tight["halo_area_1080"], (tight, wide)
    assert wide["squint"]["lit_share"] > 0.5, wide["squint"]


def test_the_tool_reads_a_white_hot_core_as_bright_and_unsaturated(tmp_path):
    p = _synthetic(tmp_path, 6.0)
    im = Image.open(p)
    ImageDraw.Draw(im).line([(200, 400), (1700, 520)], fill=(225, 252, 245), width=3)   # a near-white core down the middle
    im.save(p)
    got = M.measure(p, "#34F5C5", [150, 300, 1750, 900])
    assert got["core_sat"] < 0.3 and got["core_L"] > 95, got


def test_the_tool_measures_a_cap_height_and_scales_it_to_the_squint_width(tmp_path):
    im = Image.new("RGB", (1920, 1080), (37, 49, 60))
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 100)
    except OSError:
        pytest.skip("no Arial on this machine to set a known cap")
    ImageDraw.Draw(im).text((100, 100), "HEIGHT", font=font, fill=(242, 242, 242))
    p = tmp_path / "cap.png"
    im.save(p)
    cap = M.cap_height(M.luma(M.load_rgb(p)), [90, 90, 700, 260])
    assert 68 <= cap <= 76, cap                                                  # Arial's cap height is 0.716 em
    got = M.measure(_synthetic(tmp_path, 4.0), "#34F5C5", [150, 300, 1750, 900])
    assert got["squint"]["width"] == 320


# ---- the Bravos band: recorded, and reproducible ------------------------------------------------------------------


def test_the_band_records_five_bravos_frames_with_every_number_and_where_it_came_from():
    b = band()
    assert b["schema"] == "bravos-line-bloom.v1"
    ids = [f["id"] for f in b["frames"]]
    assert ids[:2] == ["jpn-0520", "jpn-0523"] and len(ids) == 5, ids              # the T37 sheet's two, and three more
    for f in b["frames"]:
        assert f["frame"].startswith("docs/research/runs/bravos-watch/"), f["frame"]
        for k in ("core_L", "core_sat", "ink_sat", "halo_r50_px1080", "halo_area_1080", "lit_share", "title_cap_px",
                  "label_cap_px", "plot_words"):
            assert f["measured"][k] is not None, (f["id"], k)
    for k in ("halo_r50_px1080", "halo_area_1080", "halo_edge", "core_L", "lit_muted_ratio", "lit_muted_excess", "lit_share"):
        assert b["band_1024"][k]["n"] >= 2 and b["band_1024"][k]["min"] < b["band_1024"][k]["max"], k


def _frames_root() -> Path | None:
    """The gitignored research frames: BRAVOS_FRAMES_ROOT, this checkout, or the main checkout a worktree hangs off."""
    cands = [os.environ.get("BRAVOS_FRAMES_ROOT"), str(ROOT)]
    if ".claude" in ROOT.parts:
        cands.append(str(Path(*ROOT.parts[:ROOT.parts.index(".claude")])))
    first = band()["frames"][0]["frame"]
    for c in cands:
        if c and (Path(c) / first).exists():
            return Path(c)
    return None


def test_the_tool_reproduces_every_recorded_bravos_number():
    root = _frames_root()
    if root is None:
        pytest.skip("the Bravos research frames are not on disk (gitignored): set BRAVOS_FRAMES_ROOT")
    assert M.check_band(BAND_FILE, root) == []


# ---- ours, rendered ------------------------------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


@pytest.fixture(scope="module")
def frames():
    import render_baseline as RB
    with tempfile.TemporaryDirectory() as td:
        out = {}
        for tag, t in (("before", BEFORE_T), ("solo", None)):
            p = Path(td) / f"{tag}.png"
            p.write_bytes(RB.render_surface(SURFACE, t))
            out[tag] = p
        yield out


@needs_browser
def test_the_primary_line_blooms_inside_the_bravos_band_at_its_own_width(frames):
    """s117 (1): the page's primary - series 0 before the solo - read at 1024 px, the band's own width."""
    b = band()["band_1024"]
    got = M.measure(frames["before"], PRIMARY_INK, BOX, at_width=1024)
    assert got["core_L"] >= b["core_L"]["min"], got["core_L"]
    assert got["core_sat"] < 0.5, got["core_sat"]                                   # a near-white core, not the bare ink
    for k in ("halo_r50_px1080", "halo_area_1080", "halo_edge"):
        assert within(got[k], b[k]), (k, got[k], b[k])


@needs_browser
def test_on_the_phone_the_bloomed_line_is_still_a_line(frames):
    """s117 (3): at 390 px wide the stroke is found and its core stays hot - the halo has not smeared it into the ground."""
    got = M.measure(frames["before"], PRIMARY_INK, BOX, at_width=390)
    assert got["core_L"] >= band()["band_1024"]["core_L"]["min"], got["core_L"]
    assert got["halo_r50_px1080"] <= band()["band_1024"]["halo_r50_px1080"]["max"], got["halo_r50_px1080"]


@needs_browser
def test_a_solo_opens_the_gap_between_the_lit_and_the_muted_to_bravos_band(frames):
    """s117 (2) + s120 (1): the named line against the muted three, and its share of the plot's contrast at 320 px."""
    b = band()["band_1024"]
    got = M.measure(frames["solo"], SOLO_INK, BOX, at_width=1024)
    assert within(got["lit_muted_ratio"], b["lit_muted_ratio"]), (got["lit_muted_ratio"], b["lit_muted_ratio"])
    assert within(got["lit_muted_excess"], b["lit_muted_excess"]), (got["lit_muted_excess"], b["lit_muted_excess"])
    assert got["squint"]["lit_share"] >= b["lit_share"]["min"], got["squint"]
    assert within(got["halo_r50_px1080"], b["halo_r50_px1080"]), got["halo_r50_px1080"]   # the lifted line blooms too


PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp;
  return (st.paths || []).map(pp => ({ si: pp.si | 0, muted: !!pp.muted, hot: !!pp.hot, context: !!pp.context,
    stroke: getComputedStyle(pp.p).stroke, filter: pp.p.style.filter,
    name: pp.name ? getComputedStyle(pp.name).fill : null, text: pp.name ? pp.name.textContent : "" }));
}"""


def _probe(tl: dict, uris: dict, t: float, aspect: str = "16:9") -> list:
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "probe.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE[aspect]
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True)
                page = br.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                got = page.evaluate(PROBE)
                br.close()
        finally:
            srv.shutdown()
    return got


@needs_browser
def test_every_end_tag_wears_its_own_lines_ink_and_only_the_primary_is_hot():
    """s118: the name's fill IS its line's stroke; s117: series 0 carries the hot core, its peers E67's neon, context none."""
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface(SURFACE)
    paths = _probe(tl, uris, BEFORE_T, aspect)
    named = [p for p in paths if p["text"]]
    assert len(named) == 4, paths
    for p in named:
        assert p["name"] == p["stroke"], p                                            # a teal line's name is teal
    hot = [p for p in paths if p["hot"]]
    assert [p["si"] for p in hot] == [0] and "#lphot-" in hot[0]["filter"], hot   # Chromium writes url("#...")
    for p in paths:
        if p["context"] or p["muted"]:
            assert p["filter"] == "", p                                              # context and history never bloom
        elif not p["hot"]:
            assert p["filter"].count("drop-shadow") == 1 and "url(" not in p["filter"], p   # E67's own neon, untouched


# ---- the WARN and the title dial -----------------------------------------------------------------------------------


def test_a_name_under_the_text_floor_on_its_ground_is_reported_with_its_ratio():
    falling = {"builder": "dense-line", "series": [{"name": "Yen", "pts": [[0, 5], [1, 3]]}]}
    rising = {"builder": "dense-line", "series": [{"name": "Yen", "pts": [[0, 3], [1, 5]]}]}
    w = SI.ink_contrast_warnings(falling)
    assert len(w) == 1 and w[0].startswith(SI.WARN) and "4.06:1" in w[0] and "#FF4D4D" in w[0], w
    assert SI.ink_contrast_warnings(rising) == []                                   # the rise's green reads 7.4:1
    longform = dict(falling, axes={"readability": "longform:bravos"})
    assert SI.ink_contrast_warnings(longform) == []                                 # 5.45:1 on the long form's darker ground
    multi = {"builder": "dense-line", "series": [{"name": n, "pts": [[0, 1], [1, 2]]} for n in "ABCD"]}
    assert SI.ink_contrast_warnings(multi) == []                                    # E67's four inks all clear 4.5:1
    assert SI.ink_contrast_warnings({"builder": "story", "series": falling["series"]}) == []


def test_the_warn_reads_the_engine_and_the_template_never_a_copy():
    pal = SI.palette()
    src = ENGINE.read_text(encoding="utf-8")
    assert pal["ink"]["teal"] in src and pal["ink"]["crimson"] == "#FF8A4C", pal
    assert pal["ground"]["page"] == CHARCOAL and pal["ground"]["longform"] == "#14181E", pal
    assert abs(SI.contrast("#FFFFFF", "#000000") - 21) < 0.01


def test_the_title_colour_is_one_dial_left_unset():
    """s119: both page styles read ONE token; no page's title changes until the operator's pick sets it."""
    css = TEMPLATE.read_text(encoding="utf-8")
    assert "color: var(--lp-title-ink, var(--lp-chalk));" in css
    assert ".lp-readability-longform .lp-title { color: var(--lp-title-ink, #DB8497);" in css
    live = re.sub(r"/\*.*?\*/", "", css, flags=re.S)                                  # the sheet's rules, its comments out
    assert not re.search(r"--lp-title-ink\s*:", live), "the default changes only on the operator's pick"


def test_the_primary_s_dials_are_named_and_the_history_keeps_e67s_alpha():
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const LP_HOT = Object\.freeze\(\{(.*?)\}\);", src, re.S)
    assert m, "LP_HOT"
    for k in ("CORE_W", "CORE_MIX", "INNER_PX", "INNER_A", "OUTER_PX", "OUTER_A"):
        assert re.search(k + r": [0-9.]+", m.group(1)), k
    assert "lpInkA(declared, 0.45)" in src                                          # E99 s78 (2): the history's 0.45 stands
    assert 'const LINE_BLOOM = 0.35;' in src                                         # E67's neon on a live peer, unchanged
