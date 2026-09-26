"""P72 T10 - FILLED MARKS GLOW (E99 s130 (1)): a fill gauge's fill and a bars page's PRIMARY bar carry an emissive halo
in their own ink, measured off Bravos's fills first, seek-exact like the primary line's (`lpHotFilter`).

The ruling: "a fill gauge's fill and bars (the lit / primary ones) carry an emissive halo in their own ink, measured off
Bravos's fills first (the `measure_line_bloom` band, E38), seek-exact like `lpHotFilter`, a solo / focus still widening
the lit-vs-muted gap". Every number is MEASURED by one tool (measure_line_bloom.py `--fill`) - on Bravos first, then on
ours (E38: thresholds from the reference):

  the tool     a synthetic fill whose halo is known reads back in order (none < a tight one < a wide one); a neighbour
               left out of the halo read by name never raises it; `--fill` is a mode of the same command line
  the band     four Bravos fills recorded in `assets/bravos-line-bloom.v1.json` `fills` (BOOM's two capsules, D40's
               capsule and D40's lit bar), each with a halo at 1080; re-measured from the videos when they are on disk
  ours         the gauge-94 golden and an emphasized bar land inside that band at 1920 and at the 256 px thumbnail;
               the glow is on the gauge's fill and the PRIMARY bar only (the emphasized one; on its word the solo'd
               one) - a muted bar under a solo carries none, and the solo still widens the lit-vs-muted gap
  the law      a cold seek and a played frame are byte-identical at the glow's instants
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

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

BAND_FILE = ROOT / "content/video_engine/assets/bravos-line-bloom.v1.json"
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
GAUGE = "gauge-94"
GAUGE_INK = "#FF8A4C"                                # the page's `crimson` slot (E67's Claude orange)
GAUGE_BOX = [566, 257, 936, 782]                     # the capsule's column: its fill +- 130 px, from 60 px over the whole to its foot
BARS_OBJ = "ev-hbm-wafer-ratio-bars-v1"              # H row 21's wafer compare: two bars (test_solo's own page)
SOLO_AT, SOLO_DUR = 10.0, 0.5
BAR_INKS = ("teal", "crimson")                       # E67's primary pair on the two bars
ALLOWED_BRAVOS = {"boom-return-1100", "boom-losses-1105", "d40-gauge-1730", "d40-litbar-1432"}


def band() -> dict:
    return json.loads(BAND_FILE.read_text(encoding="utf-8"))


def within(v: float, b: dict) -> bool:
    return b["min"] <= v <= b["max"]


# ---- the tool, on a frame whose answers are known ----------------------------------------------------------------


def _synthetic(tmp: Path, sigma: float, alpha: float = 0.8, neighbour: bool = False) -> Path:
    """1920 x 1080 long-form ground, a 110 x 420 fill of D40's pink with a gaussian halo of its ink (sigma px)."""
    ground, ink = (20, 24, 30), (241, 74, 133)
    im = Image.new("RGB", (1920, 1080), ground)
    if sigma > 0:
        glow = Image.new("L", (1920, 1080), 0)
        ImageDraw.Draw(glow).rectangle([700, 300, 809, 719], fill=255)
        glow = glow.filter(ImageFilter.GaussianBlur(sigma))
        a = np.asarray(glow).astype(np.float64)[..., None] / 255.0 * alpha
        base = np.asarray(im).astype(np.float64)
        im = Image.fromarray((base * (1 - a) + np.array(ink) * a).round().astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.rectangle([700, 300, 809, 719], fill=ink)
    if neighbour:
        d.rectangle([840, 300, 869, 719], fill=(90, 40, 60))    # a dim bar 30 px beside the fill
    p = tmp / f"fill-{sigma}-{int(neighbour)}.png"
    im.save(p)
    return p


def test_a_known_halo_reads_back_in_order_none_tight_wide():
    with tempfile.TemporaryDirectory() as td:
        box = [560, 200, 1000, 820]
        none, tight, wide = (M.measure_fill(_synthetic(Path(td), s), "#F14A85", box) for s in (0, 4, 14))
    assert none["fill_px1080"] == pytest.approx(110, abs=2), none
    assert none["halo_reach10_px1080"] <= 2.0 and none["halo_area_x_fill"] < 1.0, none
    assert tight["halo_reach10_px1080"] < wide["halo_reach10_px1080"], (tight, wide)
    assert tight["halo_area_x_fill"] < wide["halo_area_x_fill"], (tight, wide)
    assert wide["halo_edge"] > 0.2, wide


def test_a_neighbour_left_out_of_the_halo_read_never_raises_it():
    with tempfile.TemporaryDirectory() as td:
        box = [560, 200, 1000, 820]
        clean = M.measure_fill(_synthetic(Path(td), 6), "#F14A85", box)
        beside = M.measure_fill(_synthetic(Path(td), 6, neighbour=True), "#F14A85", box, halo_exclude=[[836, 280, 874, 740]])
    assert beside["halo_reach10_px1080"] == pytest.approx(clean["halo_reach10_px1080"], abs=1.0), (clean, beside)
    assert beside["muted_px"] > 0 and beside["lit_muted_ratio"] > 1.0, beside     # the neighbour is still a muted mark


def test_the_fill_read_is_a_mode_of_the_same_command_line(capsys):
    with tempfile.TemporaryDirectory() as td:
        p = _synthetic(Path(td), 6)
        assert M.main([str(p), "--fill", "--ink", "#F14A85", "--box", "560,200,1000,820"]) == 0
    got = json.loads(capsys.readouterr().out)
    assert got["mode"] == "fill" and got["halo_reach10_px1080"] > 2.0, got
    assert got["thumb"]["width"] == M.THUMB_W == 256, got["thumb"]


# ---- the Bravos band -----------------------------------------------------------------------------------------------


def test_the_band_records_four_bravos_fills_each_with_a_halo_at_1080():
    """E38: the fills band is the reference's, read off four frames; the stop condition (no measurable halo) is not met."""
    fb = band()["fills"]
    assert {f["id"] for f in fb["frames"]} == ALLOWED_BRAVOS, fb["frames"]
    for f in fb["frames"]:
        assert f["video"] and isinstance(f["t"], (int, float)) and len(f["frame_sha256"]) == 64, f
        assert f["measured"]["halo_reach10_px1080"] >= 6.0, (f["id"], f["measured"])   # a halo, not an edge
        assert f["measured"]["halo_area_x_fill"] >= 1.5, (f["id"], f["measured"])
    for side in ("full", "thumb"):
        for k in M.FILL_KEYS:
            b = fb["band"][side][k]
            assert b["n"] == 4 and b["min"] < b["max"], (side, k, b)
    assert fb["band"] == M.fills_band(fb["frames"]), "the band is the recorded frames' own min / max"


def _video_root() -> Path | None:
    """The gitignored videos: BRAVOS_FRAMES_ROOT, this checkout, or the main checkout a worktree hangs off."""
    cands = [os.environ.get("BRAVOS_FRAMES_ROOT"), str(ROOT)]
    if ".claude" in ROOT.parts:
        cands.append(str(Path(*ROOT.parts[:ROOT.parts.index(".claude")])))
    first = band()["fills"]["frames"][0]["video"]
    for c in cands:
        if c and (Path(c) / first).exists():
            return Path(c)
    return None


def test_the_tool_reproduces_every_recorded_bravos_fill():
    root = _video_root()
    if root is None:
        pytest.skip("the Bravos videos are not on disk (gitignored): set BRAVOS_FRAMES_ROOT")
    assert M.check_fills(BAND_FILE, root) == []


# ---- the dials -----------------------------------------------------------------------------------------------------


def test_the_fill_glow_dials_are_named_and_each_carries_its_measured_frame():
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const LP_FILL_GLOW = Object\.freeze\(\{(.*?)\}\);", src, re.S)
    assert m, "LP_FILL_GLOW"
    for k in ("INNER_PX", "INNER_A", "OUTER_PX", "OUTER_A"):
        line = re.search(k + r": [0-9.]+,?\s*/\*[^*]*\[MEASURED: [^\]]+\]", m.group(1))
        assert line, k
    assert "const lpFillGlow = " in src and src.index("const lpFillGlow = ") > src.index("const lpHotFilter = ")


# ---- ours, rendered ------------------------------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = r"""() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp;
  const glow = world.querySelectorAll('.lp-gauge-glow');
  const hex = (c) => { const m = /rgba?\((\d+), (\d+), (\d+)/.exec(c); return m ? '#' + [m[1], m[2], m[3]].map(v => (+v).toString(16).padStart(2, '0')).join('').toUpperCase() : c; };
  const g = document.getElementById('stage').getBoundingClientRect();
  const rect = (e) => { const r = e.getBoundingClientRect(); return [r.x - g.x, r.y - g.y, r.right - g.x, r.bottom - g.y]; };
  const gf = (b) => { const p = b.bar.parentNode; return ((p && p.classList && p.classList.contains('lp-bar-glow') ? p : b.bar).style.filter) || ''; };
  return { bars: (st.bars || []).map(b => ({ i: b.i, filter: gf(b), op: b.bar.getAttribute('opacity'),
                                            ink: hex(getComputedStyle(b.bar).fill), rect: rect(b.bar) })),
           gauges: Array.from(glow).map(g => g.style.filter || ''), callout: st.callout ? rect(st.callout) : null,
           fills: world.querySelectorAll('filter[id^="lpfill-"]').length };
}"""


def _serve(tl: dict, uris: dict, aspect: str = "16:9"):
    import render_baseline as RB
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[aspect]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)   # R26-351: guarded

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE)

    def png(t: float) -> bytes:
        return RB.frame_png(page, t, (w, h))

    at.page = page                                    # a test's own read: at.page.evaluate(...)
    return at, png, errs, close


def _bars_timeline(emph: int | None, species: list, *, longform: bool = False) -> tuple[dict, dict]:
    """H row 21's two-bar page as a scene of its own (test_solo's page), an emphasis and species of the test's."""
    import build_golden_sources as G
    import build_scene_timeline_f as B
    plate = "ledger:%s:bars" % BARS_OBJ
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(plate, (0, 0, 0), PROJECT)
        B.stamp_full_stage(world["page"])
        if species:
            B.check_solo(world, [s for s in species if s["kind"] == "solo"])
    finally:
        B.ASPECT = saved
    world["page"]["emphasize"] = emph
    world["page"]["colors"] = list(BAR_INKS)          # two coloured bars: a neutral grey has no hue for the tool to find
    if longform:
        world["page"].setdefault("axes", {})["readability"] = "longform"
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    return G._timeline("probe: a primary bar's glow", scenes, {}, "16:9"), G._base_uris()


@needs_browser
def test_the_gauge_fill_carries_the_glow_in_its_own_ink():
    import render_baseline as RB
    tl, uris, t, aspect = RB.load_surface(GAUGE)
    at, _png, errs, close = _serve(tl, uris, aspect)
    try:
        got = at(t)
    finally:
        close()
    assert not errs, errs
    assert len(got["gauges"]) == 1 and "#lpfill-" in got["gauges"][0], got
    assert got["bars"][0]["filter"] == "", "the glow is the capsule's (outside its clip), never the clipped rect's"


@needs_browser
def test_only_the_emphasized_bar_glows_and_a_page_with_no_emphasis_has_no_glow():
    at, _png, errs, close = _serve(*_bars_timeline(1, []))
    try:
        lit = at(9.0)
    finally:
        close()
    at, _png, errs2, close = _serve(*_bars_timeline(None, []))
    try:
        plain = at(9.0)
    finally:
        close()
    assert not errs and not errs2, (errs, errs2)
    assert "#lpfill-" in lit["bars"][1]["filter"] and lit["bars"][0]["filter"] == "", lit
    assert plain["fills"] == 0 and all(b["filter"] == "" for b in plain["bars"]), plain


@needs_browser
def test_our_gauge_lands_inside_the_bravos_fill_band_at_full_size_and_at_the_thumbnail(tmp_path):
    import render_baseline as RB
    fb = band()["fills"]["band"]
    p = tmp_path / "gauge.png"
    p.write_bytes(RB.render_surface(GAUGE))
    for side, width in (("full", None), ("thumb", M.THUMB_W)):
        got = M.measure_fill(p, GAUGE_INK, GAUGE_BOX, at_width=width)
        for k in M.FILL_KEYS:
            assert within(got[k], fb[side][k]), (side, k, got[k], fb[side][k])


@needs_browser
def test_a_solo_moves_the_glow_to_the_named_bar_and_a_muted_bar_carries_none():
    """Before the word the emphasized bar (0) glows; on the word the named bar (1) takes the glow and the emphasized
    one, muted, sheds it - no filter at all, only the solo's alpha."""
    at, _png, errs, close = _serve(*_bars_timeline(0, [{"kind": "solo", "at": SOLO_AT, "dur": SOLO_DUR, "bar": 1}]))
    try:
        before, after = at(SOLO_AT - 0.2), at(SOLO_AT + SOLO_DUR + 0.3)
    finally:
        close()
    assert not errs, errs
    assert "#lpfill-" in before["bars"][0]["filter"] and before["bars"][1]["filter"] == "", before
    assert "#lpfill-" in after["bars"][1]["filter"], after
    assert after["bars"][0]["filter"] == "" and after["bars"][0]["op"] is not None, "a muted bar carries no glow"


def _column(bars: list, lit: int) -> tuple[list, list]:
    """The box rule the band states for a bar: the lit bar +- 130 px from 10 px over its top to its foot, here widened
    to both bars so the other is a muted mark; the other's column is out of the halo read."""
    x0 = min(b["rect"][0] for b in bars) - 130
    x1 = max(b["rect"][2] for b in bars) + 130
    top, foot = bars[lit]["rect"][1] - 10, bars[lit]["rect"][3] - 4
    other = bars[1 - lit]["rect"]
    return [x0, top, x1, foot], [[other[0] - 3, 0, other[2] + 3, 2000]]


@needs_browser
def test_on_the_word_the_lit_bar_glows_and_the_gap_to_the_muted_one_widens(tmp_path):
    """A page with no emphasis: before the word no bar glows (the D40 14:28 page); on it the named bar lights inside the
    Bravos band and the lit-vs-muted gap, read by the same tool at 1920 and at the 256 px thumbnail, widens."""
    at, png, errs, close = _serve(*_bars_timeline(None, [{"kind": "solo", "at": SOLO_AT, "dur": SOLO_DUR, "bar": 1}]))
    try:
        before, after = at(SOLO_AT - 0.2), at(SOLO_AT + SOLO_DUR + 0.3)
        (tmp_path / "b.png").write_bytes(png(SOLO_AT - 0.2))
        (tmp_path / "a.png").write_bytes(png(SOLO_AT + SOLO_DUR + 0.3))
    finally:
        close()
    assert not errs, errs
    assert all(b["filter"] == "" for b in before["bars"]), before
    assert "#lpfill-" in after["bars"][1]["filter"] and after["bars"][0]["filter"] == "", after
    box, hx = _column(after["bars"], 1)
    ink = after["bars"][1]["ink"]
    gb = M.measure_fill(tmp_path / "b.png", ink, box, halo_exclude=hx)
    ga = M.measure_fill(tmp_path / "a.png", ink, box, halo_exclude=hx)
    fb = band()["fills"]["band"]["full"]
    assert gb["halo_reach10_px1080"] < fb["halo_reach10_px1080"]["min"], gb     # no glow before the word
    for k in M.FILL_KEYS:
        assert within(ga[k], fb[k]), (k, ga[k], fb[k])
    assert ga["lit_muted_ratio"] > gb["lit_muted_ratio"], (gb["lit_muted_ratio"], ga["lit_muted_ratio"])
    assert ga["thumb_lit_muted_ratio"] > gb["thumb_lit_muted_ratio"], (gb["thumb"], ga["thumb"])
    assert ga["thumb_lit_share"] > gb["thumb_lit_share"], (gb["thumb"], ga["thumb"])


def _surface(name: str):
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface(name)
    return tl, uris, aspect


def _solo_bars():
    return (*_bars_timeline(None, [{"kind": "solo", "at": SOLO_AT, "dur": SOLO_DUR, "bar": 1}]), "16:9")


# the glow's instants and the region the glow paints (the capsule); None = the whole frame. The gauge mid-grow (4.9) is
# read on the capsule's region: at the base, before any glow, the page's translucent words over it (the title's sub,
# the whole's name, "100%") already raster <= 2 levels apart after forward play - not the glow's; at the hold (9.0) the
# whole frame is exact. The bars page lights bar 1 on the word: mid-ease and at rest, the whole frame is exact.
SEEK_CASES = [
    ("gauge-94", lambda: _surface(GAUGE), ((4.9, [600, 330, 900, 800]), (9.0, None))),
    ("solo-bars", _solo_bars, ((SOLO_AT + SOLO_DUR / 2, None), (SOLO_AT + SOLO_DUR + 0.3, None))),
]


def _crop(png: bytes, region) -> bytes:
    import io
    if region is None:
        return png
    return Image.open(io.BytesIO(png)).convert("RGB").crop(tuple(region)).tobytes()


@needs_browser
@pytest.mark.parametrize("name,make,instants", SEEK_CASES, ids=[c[0] for c in SEEK_CASES])
def test_a_cold_seek_and_a_played_frame_are_byte_identical_at_the_glow(name, make, instants):
    """The lpHotFilter rule: forward play in 0.1 s steps into each instant paints the cold seek's pixels exactly."""
    tl, uris, aspect = make()
    for t, region in instants:
        _at, png, errs, close = _serve(tl, uris, aspect)
        try:
            cold = png(t)
        finally:
            close()
        _at, png, errs2, close = _serve(tl, uris, aspect)
        try:
            for x in [round(t - 1.0 + 0.1 * i, 2) for i in range(10)]:
                png(x)
            played = png(t)
        finally:
            close()
        assert not errs and not errs2, (errs, errs2)
        assert _crop(played, region) == _crop(cold, region), f"{name} at {t}: forward play paints another frame than the cold seek"


@needs_browser
def test_the_emphasized_bars_hand_over_is_exact_at_rest_and_the_line_solos_raster_mid_ease():
    """The emphasized bar (0) sheds its glow as the solo mutes it. At rest after the ease the frame is exact; mid-ease
    the muting bar is a FILTERED mark under the solo's own opacity - the line solo's case exactly (lpHotFilter on a
    muting series: solo-chipmakers at 12.35 rasters <= 1 level apart after forward play at the BASE) - and holds to it.
    The callout pill of the emphasized bar is left out: at the base, with no glow, one of its pixels already differs
    after forward play (13 levels at (445, 562), a finding of this slice - not the glow's)."""
    import io
    tl, uris = _bars_timeline(0, [{"kind": "solo", "at": SOLO_AT, "dur": SOLO_DUR, "bar": 1}])
    for t, tol in ((SOLO_AT + SOLO_DUR / 2, 1), (SOLO_AT + SOLO_DUR + 0.3, 0)):
        at, png, errs, close = _serve(tl, uris)
        try:
            cold, probe = png(t), at(t)
        finally:
            close()
        _at, png, errs2, close = _serve(tl, uris)
        try:
            for x in [round(t - 1.0 + 0.1 * i, 2) for i in range(10)]:
                png(x)
            played = png(t)
        finally:
            close()
        assert not errs and not errs2, (errs, errs2)
        a, b = (np.asarray(Image.open(io.BytesIO(x)).convert("RGB")).astype(int) for x in (cold, played))
        d = np.abs(a - b).max(axis=2)
        x0, y0, x1, y1 = (int(round(v)) for v in probe["callout"])
        d[max(0, y0 - 4):y1 + 4, max(0, x0 - 4):x1 + 4] = 0
        assert d.max() <= tol, (t, int(d.max()), np.argwhere(d > tol)[:5].tolist())


STACK = "stacked-outlays"   # one emphasized stacked bar: "Paid by revenue" (teal) under "Borrowed" (crimson)
SEG_PROBE = r"""() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')), st = w.__lp;
  const g = document.getElementById('stage').getBoundingClientRect();
  const hex = (c) => { const m = /rgba?\((\d+), (\d+), (\d+)/.exec(c); return m ? '#' + [m[1], m[2], m[3]].map(v => (+v).toString(16).padStart(2, '0')).join('').toUpperCase() : c; };
  const flood = (el) => { const m = /#(lpfill-[\w-]+)/.exec(el.style.filter || ''); const f = m && document.getElementById(m[1]);
    return f ? Array.from(f.querySelectorAll('feFlood[result^="f"]')).map(x => hex(x.getAttribute('flood-color'))) : []; };
  const b = st.bars[st.emph];
  const p = b.bar.parentNode, wrap = p && p.classList && p.classList.contains('lp-bar-glow');
  return { bar: (wrap ? p : b.bar).style.filter || '', segs: b.segs.map(s => { const r = s.el.getBoundingClientRect();
    return { j: s.j, filter: s.el.style.filter || '', ink: hex(getComputedStyle(s.el).fill), flood: flood(s.el),
             rect: [r.x - g.x, r.y - g.y, r.right - g.x, r.bottom - g.y] }; }) };
}"""


@needs_browser
def test_an_emphasized_stacked_bar_glows_per_segment_each_in_its_own_ink():
    """s130 (1) "in their own ink": a stack has one ink per part, so each part carries its own halo (the bar under the
    parts carries none), and a part's halo stays beside its own part - the part above it keeps its ink up to the seam."""
    import io
    import render_baseline as RB
    tl, uris, t, aspect = RB.load_surface(STACK)
    at, png, errs, close = _serve(tl, uris, aspect)
    try:
        page_png = png(t)
        at(t)
        got = at.page.evaluate(SEG_PROBE)
    finally:
        close()
    assert not errs, errs
    assert got["bar"] == "", "the bar under the parts carries no glow of its own"
    assert len(got["segs"]) == 2
    for s in got["segs"]:
        assert "#lpfill-" in s["filter"], s
        assert s["flood"] and all(f == s["ink"] for f in s["flood"]), s          # the halo is the part's own ink
    im = np.asarray(Image.open(io.BytesIO(page_png)).convert("RGB")).astype(int)
    low, high = sorted(got["segs"], key=lambda s: s["j"])
    x0, x1 = int(high["rect"][0]) + 8, int(high["rect"][2]) - 8
    seam = int(round(low["rect"][1]))
    band = im[seam - 14:seam - 4, x0:x1].reshape(-1, 3)                           # the upper part, just over the seam
    ink = np.array([int(high["ink"][k:k + 2], 16) for k in (1, 3, 5)])
    assert np.abs(np.median(band, axis=0) - ink).max() <= 3, (np.median(band, axis=0), high["ink"])
    # the seam's separator keeps its FULL width (review round 3): the top part runs its foot under the lower part and has
    # no stroke there, so the lower part's top stroke is the seam's only one - its region opens by half of it. Inside the
    # stack the seam's rows are the committed (pre-glow) golden's, within 2 levels.
    gold = np.asarray(Image.open(RB.FRAMES / f"{STACK}.png").convert("RGB")).astype(int)
    cx = int(high["rect"][0]) + 25
    rows = slice(seam - 4, seam + 5)
    assert np.abs(im[rows, cx] - gold[rows, cx]).max() <= 2, (im[rows, cx].tolist(), gold[rows, cx].tolist())



# ---- round 3 (the review): the solo page's two exceptions ----------------------------------------------------------

BT_PLATE = "ledger:ev-bonds-vs-chips-10y-v1:bars:1:right"   # test_breakthrough's page: bar 1 (Chips) breaks the scale
BT_EP = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
BT_JS = r"""() => { const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')), st = w.__lp;
  const gf = (b) => { const p = b.bar.parentNode; return ((p && p.classList && p.classList.contains('lp-bar-glow') ? p : b.bar).style.filter) || ''; };
  return (st.bars || []).map(b => ({ i: b.i, over: !!b.over, filter: gf(b) })); }"""


def _bt_timeline(solo_bar: int) -> tuple[dict, dict]:
    import build_scene_timeline_f as B
    import render_baseline as RB
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = json.loads(json.dumps(B.world_for_plate(BT_PLATE, (0, 0, 0), BT_EP)))
    world["page"]["axes"]["overflow"] = "stack"
    sp = [{"kind": "solo", "at": 11.0, "dur": 0.5, "bar": solo_bar}]
    scene = dict(tl["scenes"][0], species=sp, span=[0.0, 16.0], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    return dict(tl, aspect="9:16", runtime_s=16.0, scenes=[scene], caption_pages=[], captions=[]), uris


@needs_browser
@pytest.mark.skipif(not (BT_EP / "evidence/objects/ev-bonds-vs-chips-10y-v1.series.json").exists(), reason="the object is not on disk")
@pytest.mark.parametrize("solo_bar", [0, 1], ids=["solo-on-the-other", "solo-on-the-breaking-bar"])
def test_a_breaking_bar_on_a_solo_page_never_takes_the_fill_glow(solo_bar):
    """The breakthrough keeps its own glow law (the burst's ramp, none on the stack) on a page that also carries a solo -
    the emphasized breaking bar, muted or named, carries no fill glow at any instant."""
    at, _png, errs, close = _serve(*_bt_timeline(solo_bar), "9:16")
    try:
        reads = []
        for t in (6.0, 8.0, 10.0, 11.25, 12.0, 14.0):
            at(t)
            reads.append(at.page.evaluate(BT_JS))
    finally:
        close()
    assert not errs, errs
    for r in reads:
        brk = [b for b in r if b["over"]]
        assert brk and all("lpfill-" not in b["filter"] for b in brk), r


GAUGE_JS = r"""() => { const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')), st = w.__lp;
  return (st.bars || []).map(b => ({ i: b.i, glow: b.gauge ? (b.gauge.glow.style.filter || '') : null, op: b.bar.getAttribute('opacity') })); }"""


def _two_gauges(solo_bar: int) -> tuple[dict, dict]:
    import render_baseline as RB
    tl, uris, _t, _a = RB.load_surface(GAUGE)
    tl = json.loads(json.dumps(tl))
    pg = tl["scenes"][0]["world"]["page"]
    pg.update(values=[94.0, 60.0], value_strings=["94", "60"], labels=["Capex, next two years", "Buybacks"],
              colors=["crimson", "teal"])
    tl["scenes"][0]["species"] = [{"kind": "solo", "at": SOLO_AT, "dur": SOLO_DUR, "bar": solo_bar}]
    return tl, uris


@needs_browser
def test_a_muted_gauge_sheds_its_glow_and_the_named_one_keeps_it():
    """Acceptance (4) on a gauge page: a solo names capsule 0; capsule 1, muted, carries no glow once the mute has eased
    (its glow group's filter removed), capsule 0 keeps its; before the word both glow."""
    at, _png, errs, close = _serve(*_two_gauges(0))
    try:
        at(SOLO_AT - 0.2)
        before = at.page.evaluate(GAUGE_JS)
        at(SOLO_AT + SOLO_DUR / 2)
        mid = at.page.evaluate(GAUGE_JS)
        at(SOLO_AT + SOLO_DUR + 0.3)
        after = at.page.evaluate(GAUGE_JS)
    finally:
        close()
    assert not errs, errs
    assert all("#lpfill-" in g["glow"] for g in before), before
    assert "#lpfill-" in mid[1]["glow"], mid                          # easing out, not snapped off
    assert "#lpfill-" in after[0]["glow"] and after[1]["glow"] == "" and after[1]["op"] is not None, after


@needs_browser
def test_an_extruded_bar_takes_no_glow():
    """form=extruded_bar + emphasize (round 3's frame read, frames/r3/extruded-corner-zoom.png): the face's halo lay over
    its own prism's side face and cap and flattened the 2.5D shading - the extruded form keeps its own light, no glow."""
    import render_baseline as RB
    tl, uris, t, aspect = RB.load_surface("form-extruded-bar")
    tl = json.loads(json.dumps(tl))
    tl["scenes"][0]["world"]["page"]["emphasize"] = 0
    at, _png, errs, close = _serve(tl, uris, aspect)
    try:
        got = at(t)
    finally:
        close()
    assert not errs, errs
    assert got["fills"] == 0 and all(b["filter"] == "" for b in got["bars"]), got
