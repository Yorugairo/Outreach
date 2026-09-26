"""P72 T49 (R26-378) - THE SPREAD GLOWS: the fill between two lines carries an emissive halo in its own ink, set by a
DIAL measured off Bravos, never a recipe change.

The operator, 2026-09-25, on P71 T36's divergence spread beside Bravos D40 04:48: "their red fill has more of a bloom
than ours t36, but that should just be a dial not a recipe change". Every number is MEASURED by one tool
(measure_line_bloom.py `--spread`, the sibling of T10's `--fill`) - on Bravos first, then on ours (E38):

  the tool     a synthetic spread whose halo is known reads back in order (none < a tight one < a wide one), read PAST
               THE FILL'S END (its two long edges are its two lines, each with a bloom of its own); `--spread` is a
               mode of the same command line; an end that is not "right" / "left" is refused by name
  the band     two Bravos spreads recorded in `assets/bravos-line-bloom.v1.json` `spreads` (D40 04:48, the frame the
               operator named, and BOOM 08:38's wedge), each with a halo; re-measured from the videos when on disk
  the dial     LP_SPREAD_GLOW: LEVEL (1 every spread glows; 0 none) and the two halos, each carrying its frame; and the
               fill's own alpha PS.SPREAD_A (the coordinator's ruling on T49: the fill's brightness over its ground,
               `fill_luma`, is a band key too - D40's fill is the lever the operator was seeing)
  ours         T36's divergence spread - its halo AND its fill - lands inside that band at 1920 and at the 256 px
               thumbnail, its fill on D40's own brightness; before its word it
               has no glow; a `deemph` spread never glows; a solo on a series that is neither of its edges sheds the
               glow on the solo's own ease, a solo on one of its edges keeps it; LEVEL 0 is the spread with no glow
  the law      a cold seek and a played frame are byte-identical mid-bleed, at rest and mid-solo
"""
from __future__ import annotations

import io
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
ALLOWED_BRAVOS = {"d40-spread-0448", "boom-wedge-0838"}
# T36's beat (proof_t36.py `_spread_row`) on its own clock: memory held at nothing, the chips drawn, the giants and the
# index drawn, the gap between the giants (2) and the chips (1) bled on its word
PLATE = "ledger:ev-divergence-v1:line::right:axes:cut;idle=live;domain=80,277"
MEMORY, SEMIS, MEGA, INDEX = 0, 1, 2, 3
LAST = 234
SPREAD_AT, SPREAD_DUR = 4.0, 2.0
REST = 8.0                                            # the spread held: two lines, their tags, the gap
SOLO_AT, SOLO_DUR = 9.0, 0.6
BOX = [140, 250, 1300, 700]                           # the plot and 200 px past the fill's end (the ground past the halo)


def band() -> dict:
    return json.loads(BAND_FILE.read_text(encoding="utf-8"))


def within(v: float, b: dict, key: str | None = None) -> bool:
    """Inside the band; with `key`, widened by the tool's own reproduction tolerance for that key (the --check drift
    rule: max(BAND_TOL x the value, FILL_ABS[key])) - two frames make each end of the band ONE read, and our dim
    fill's halo is a few luma levels over its ground, so a read jitters by that much between two honest renders."""
    tol = 0.0 if key is None else max(M.BAND_TOL * abs(v), M.FILL_ABS.get(key, 0.05))
    return b["min"] - tol <= v <= b["max"] + tol


# ---- the tool, on a frame whose answers are known ----------------------------------------------------------------


def _synthetic(tmp: Path, sigma: float, alpha: float = 0.8) -> Path:
    """1920 x 1080 ground; a wedge 300..900 x between a rising line and a flat one, filled in a red, its end a vertical
    cut at x 900; a gaussian halo of its ink (sigma px); the two lines in other inks over it."""
    ground, ink = (37, 49, 60), (151, 30, 55)
    poly = [(300, 600), (900, 350), (900, 640), (300, 640)]
    im = Image.new("RGB", (1920, 1080), ground)
    if sigma > 0:
        glow = Image.new("L", (1920, 1080), 0)
        ImageDraw.Draw(glow).polygon(poly, fill=255)
        glow = glow.filter(ImageFilter.GaussianBlur(sigma))
        a = np.asarray(glow).astype(np.float64)[..., None] / 255.0 * alpha
        base = np.asarray(im).astype(np.float64)
        im = Image.fromarray((base * (1 - a) + np.array(ink) * a).round().astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.polygon(poly, fill=ink)
    d.line([(300, 600), (900, 350)], fill=(52, 245, 197), width=4)
    d.line([(300, 640), (900, 640)], fill=(79, 195, 255), width=4)
    p = tmp / f"spread-{sigma}.png"
    im.save(p)
    return p


def test_a_known_spread_halo_reads_back_in_order_none_tight_wide():
    with tempfile.TemporaryDirectory() as td:
        box = [200, 250, 1200, 760]
        none, tight, wide = (M.measure_spread(_synthetic(Path(td), s), "#971E37", box) for s in (0, 4, 14))
    assert none["halo_reach10_px1080"] <= M.SPREAD_SKIP_1080 + 1.0 and none["halo_area_x_fill"] < 0.5, none
    assert tight["halo_reach10_px1080"] < wide["halo_reach10_px1080"], (tight, wide)
    assert tight["halo_area_x_fill"] < wide["halo_area_x_fill"], (tight, wide)
    assert wide["halo_edge"] > 0.2, wide
    lo, hi = wide["end_rows"]
    assert 350 < lo < hi < 640, "the read is the END's middle rows, never a line's"


def test_the_spread_read_is_a_mode_of_the_same_command_line(capsys):
    with tempfile.TemporaryDirectory() as td:
        p = _synthetic(Path(td), 6)
        assert M.main([str(p), "--spread", "--ink", "#971E37", "--box", "200,250,1200,760", "--end", "right"]) == 0
    got = json.loads(capsys.readouterr().out)
    assert got["mode"] == "spread" and got["end"] == "right" and got["halo_reach10_px1080"] > 6.0, got


def test_an_end_that_is_not_right_or_left_is_refused_by_name():
    with tempfile.TemporaryDirectory() as td:
        p = _synthetic(Path(td), 6)
        with pytest.raises(ValueError, match="end is 'right' or 'left'"):
            M.measure_spread(p, "#971E37", [200, 250, 1200, 760], end="top")


# ---- the Bravos band -----------------------------------------------------------------------------------------------


def test_the_band_records_the_bravos_spreads_each_with_a_halo():
    """E38: the spreads band is the reference's - D40 04:48 (the frame the operator named) and BOOM 08:38's wedge."""
    sb = band()["spreads"]
    assert {f["id"] for f in sb["frames"]} == ALLOWED_BRAVOS, sb["frames"]
    for f in sb["frames"]:
        assert f["video"] and isinstance(f["t"], (int, float)) and len(f["frame_sha256"]) == 64, f
        assert f["measured"]["halo_reach10_px1080"] >= 8.0, (f["id"], f["measured"])   # a halo, not an edge
        assert f["measured"]["halo_area_x_fill"] >= 1.5, (f["id"], f["measured"])
    for side in ("full", "thumb"):
        for k in M.SPREAD_KEYS:
            b = sb["band"][side][k]
            assert b["n"] == 2 and b["min"] < b["max"], (side, k, b)
    assert "fill_luma" in M.SPREAD_KEYS and sb["keys"] == list(M.SPREAD_KEYS), sb["keys"]
    assert sb["band"] == M.spreads_band(sb["frames"]), "the band is the recorded frames' own min / max"
    assert "fills" in band() and len(band()["fills"]["frames"]) == 4, "T10's fills band is untouched"


def _video_root() -> Path | None:
    """The gitignored videos: BRAVOS_FRAMES_ROOT, this checkout, or the main checkout a worktree hangs off."""
    cands = [os.environ.get("BRAVOS_FRAMES_ROOT"), str(ROOT)]
    if ".claude" in ROOT.parts:
        cands.append(str(Path(*ROOT.parts[:ROOT.parts.index(".claude")])))
    vids = {f["video"] for f in band()["spreads"]["frames"]}
    for c in cands:
        if c and all((Path(c) / v).exists() for v in vids):
            return Path(c)
    return None


def test_the_tool_reproduces_every_recorded_bravos_spread():
    root = _video_root()
    if root is None:
        pytest.skip("the Bravos videos are not on disk (gitignored): set BRAVOS_FRAMES_ROOT")
    assert M.check_spreads(BAND_FILE, root) == []


# ---- the dial ------------------------------------------------------------------------------------------------------


def _dials() -> str:
    m = re.search(r"const LP_SPREAD_GLOW = Object\.freeze\(\{(.*?)\}\);", ENGINE.read_text(encoding="utf-8"), re.S)
    assert m, "LP_SPREAD_GLOW"
    return m.group(1)


def test_the_spread_glow_dials_are_named_and_each_carries_its_measured_frame():
    block = _dials()
    assert re.search(r"LEVEL: 1,", block), "the glow is ON by default for every spread"
    for k in ("INNER_PX", "INNER_A", "OUTER_PX", "OUTER_A"):
        assert re.search(k + r": [0-9.]+,?\s*/\*[^*]*\[MEASURED: [^\]]+\]", block), k
    src = ENGINE.read_text(encoding="utf-8")
    outside = re.search(r"OUTSIDE: ([0-9.]+),", block)
    spread_a = re.search(r"const PS = \{ SPREAD_A: ([0-9.]+),", src)
    assert outside and spread_a and float(outside.group(1)) == float(spread_a.group(1)), "OUTSIDE is PS.SPREAD_A"
    assert "const lpSpreadGlow = " in src and src.index("const lpSpreadGlow = ") > src.index("const lpFillGlow = "), \
        "the spread reuses T10's filter (lpFillFilter / lpFillGlow) - no second glow system"


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
  const PF = world.__lp.perform || { spreads: [] };
  return { spreads: (PF.spreads || []).map(sd => ({ filter: sd.path.style.filter || '', alpha: +(sd.path.getAttribute('fill-opacity') || 0) })),
           fills: world.querySelectorAll('filter[id^="lpfill-"]').length };
}"""


def _timeline(species_extra: list | None = None, color: str | None = None) -> tuple[dict, dict]:
    import build_golden_sources as G
    import build_scene_timeline_f as B
    d = lambda i, s: {"kind": "datum", "index": i, "series": s}  # noqa: E731
    species = [{"kind": "build_to", "at": 0.0, "dur": 0.4, "series": s, "target": d(0, s)} for s in range(4)]
    species += [{"kind": "build_to", "at": 0.6, "dur": 1.2, "series": SEMIS, "target": d(LAST, SEMIS)},
                {"kind": "build_to", "at": 2.0, "dur": 1.2, "series": MEGA, "target": d(LAST, MEGA)},
                {"kind": "build_to", "at": 2.0, "dur": 1.2, "series": INDEX, "target": d(LAST, INDEX)},
                dict({"kind": "spread", "at": SPREAD_AT, "dur": SPREAD_DUR, "from": MEGA, "to": SEMIS},
                     **({"color": color} if color else {}))]
    species += species_extra or []
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(PLATE, (0, 0, 0), PROJECT)
        B.stamp_full_stage(world["page"])
        B.check_solo(world, [s for s in species if s["kind"] == "solo"])
    finally:
        B.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    return G._timeline("probe: the spread's glow", scenes, {}, "16:9"), G._base_uris()


def _serve(tl: dict, uris: dict, *, level: float | None = None):
    import render_baseline as RB
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    text = RB.instantiate(tl, uris)
    if level is not None:   # the dial, turned: the engine's own LEVEL line, rewritten in this probe's copy only
        text, n = re.subn(r"(const LP_SPREAD_GLOW = Object\.freeze\(\{\s*LEVEL: )1,", r"\g<1>%g," % level, text)
        assert n == 1, "LP_SPREAD_GLOW.LEVEL"
    html.write_text(text, encoding="utf-8")
    page, errs, close = SP.open_served(html, 1920, 1080, cleanup=td.cleanup)

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE)

    def png(t: float) -> bytes:
        return RB.frame_png(page, t, (1920, 1080))

    return at, png, errs, close


def _fill_ink(png: Path) -> str:
    """The spread's own ink as it lands (its alpha over the page's ground), read at the middle of its end."""
    a = np.asarray(Image.open(png).convert("RGB")).astype(int)
    fill = a[480:560, 1040:1080].reshape(-1, 3)
    r, g, b = (int(v) for v in np.median(fill, axis=0))
    return "#%02X%02X%02X" % (r, g, b)


@needs_browser
def test_the_spread_glows_in_its_own_ink_from_its_word_and_not_before():
    at, _png, errs, close = _serve(*_timeline())
    try:
        before, mid, rest = at(SPREAD_AT - 0.2), at(SPREAD_AT + SPREAD_DUR / 2), at(REST)
    finally:
        close()
    assert not errs, errs
    assert before["spreads"][0]["filter"] == "" and before["fills"] == 0, before
    assert "#lpfill-" in mid["spreads"][0]["filter"] and "#lpfill-" in rest["spreads"][0]["filter"], (mid, rest)
    spread_a = float(re.search(r"const PS = \{ SPREAD_A: ([0-9.]+),", ENGINE.read_text(encoding="utf-8")).group(1))
    assert rest["spreads"][0]["alpha"] == pytest.approx(spread_a), "the fill lands at PS.SPREAD_A"


@needs_browser
def test_our_spread_lands_inside_the_bravos_spread_band_at_full_size_and_at_the_thumbnail(tmp_path):
    _at, png, errs, close = _serve(*_timeline())
    try:
        (tmp_path / "rest.png").write_bytes(png(REST))
    finally:
        close()
    assert not errs, errs
    sb = band()["spreads"]["band"]
    ink = _fill_ink(tmp_path / "rest.png")
    for side, width in (("full", None), ("thumb", M.THUMB_W)):
        got = M.measure_spread(tmp_path / "rest.png", ink, BOX, at_width=width)
        for k in M.SPREAD_KEYS:
            assert within(got[k], sb[side][k], k), (side, k, got[k], sb[side][k])
        d40 = band()["spreads"]["frames"][0]
        assert d40["id"] == "d40-spread-0448"
        rec = d40["measured" if side == "full" else "measured_thumb"]
        # THE FILL on D40's own brightness (BOOM's opaque wedge, 179, is the band's other end - a translucent spread
        # never goes there): within the tool's reproduction tolerance of D40's read
        assert abs(got["fill_luma"] - rec["fill_luma"]) <= max(M.BAND_TOL * rec["fill_luma"], 0.05), (side, got["fill_luma"], rec)
        if side == "full":   # the glow the operator asked for: D40's side of the band, never its tight end
            assert got["halo_area_x_fill"] > 0.6 * rec["halo_area_x_fill"], got


@needs_browser
def test_the_dial_at_zero_is_the_spread_with_no_glow(tmp_path):
    _at, png, errs, close = _serve(*_timeline(), level=0)
    at = _at
    try:
        got = at(REST)
        (tmp_path / "off.png").write_bytes(png(REST))
    finally:
        close()
    assert not errs, errs
    assert got["spreads"][0]["filter"] == "" and got["fills"] == 0, got
    off = M.measure_spread(tmp_path / "off.png", _fill_ink(tmp_path / "off.png"), BOX)
    assert off["halo_reach10_px1080"] <= M.SPREAD_SKIP_1080 + 1.0 and off["halo_area_x_fill"] < 0.5, off


@needs_browser
def test_a_deemph_spread_never_glows():
    at, _png, errs, close = _serve(*_timeline(color="deemph"))
    try:
        got = at(REST)
    finally:
        close()
    assert not errs, errs
    assert got["spreads"][0]["filter"] == "" and got["spreads"][0]["alpha"] > 0, got


@needs_browser
def test_a_solo_on_neither_edge_sheds_the_glow_on_its_ease_and_on_an_edge_keeps_it():
    """The solo's own law (soloAlpha): the index named, both the spread's edges (the giants, the chips) mute, and the
    spread's glow eases out with them - lit before the word, part-way mid-ease, none at rest. The chips named, one
    edge keeps its ink, and the glow stays."""
    at, _png, errs, close = _serve(*_timeline([{"kind": "solo", "at": SOLO_AT, "dur": SOLO_DUR, "series": INDEX}]))
    try:
        before, after = at(SOLO_AT - 0.2), at(SOLO_AT + SOLO_DUR + 0.3)
    finally:
        close()
    at, _png, errs2, close = _serve(*_timeline([{"kind": "solo", "at": SOLO_AT, "dur": SOLO_DUR, "series": SEMIS}]))
    try:
        kept = at(SOLO_AT + SOLO_DUR + 0.3)
    finally:
        close()
    assert not errs and not errs2, (errs, errs2)
    assert "#lpfill-" in before["spreads"][0]["filter"], before
    assert after["spreads"][0]["filter"] == "", "a spread whose edges are both muted carries no glow"
    assert "#lpfill-" in kept["spreads"][0]["filter"], kept


SEEK_CASES = [
    ("bleed", lambda: _timeline(), SPREAD_AT + SPREAD_DUR * 0.4),
    ("rest", lambda: _timeline(), REST),
    ("solo-mid", lambda: _timeline([{"kind": "solo", "at": SOLO_AT, "dur": SOLO_DUR, "series": INDEX}]), SOLO_AT + SOLO_DUR / 2),
]
# THE BASE'S OWN DIFFERENCE (found by this slice at 861d8de, before any glow): on this page, forward play and a cold seek
# at the rest (5.0 and 8.0 alike) differ at 12-14 px, <= 17 levels, all on the flat pair's two ENDS - the giants' and the
# index's first pixels (x 150-166, y 716-723) and the index's lead point (x 1098-1099, y 628-633). Not the spread's: the
# comparison leaves those two boxes out and reads the rest of the frame exactly.
LINE_ENDS = ((140, 700, 180, 735), (1085, 615, 1112, 645))


def _masked(png: bytes, boxes=LINE_ENDS) -> bytes:
    a = np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).copy()
    for x0, y0, x1, y1 in boxes:
        a[y0:y1, x0:x1] = 0
    return a.tobytes()


@needs_browser
@pytest.mark.parametrize("name,make,t", SEEK_CASES, ids=[c[0] for c in SEEK_CASES])
def test_a_cold_seek_and_a_played_frame_are_byte_identical_at_the_glow(name, make, t):
    """The lpHotFilter rule: forward play in 0.1 s steps into each instant paints the cold seek's pixels (outside the
    base's own two line ends, above). Mid-solo the lines themselves are FILTERED marks under the solo's opacity (T10:
    <= 1 level apart at the base, the line solo's own case), so there the spread's end - the fill and 100 px of its
    halo past it, clear of every line - is the region read."""
    tl, uris = make()
    _at, png, errs, close = _serve(tl, uris)
    try:
        cold = png(t)
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
    if name == "solo-mid":
        crop = lambda b: Image.open(io.BytesIO(b)).convert("RGB").crop((1000, 450, 1200, 580)).tobytes()  # noqa: E731
        assert crop(played) == crop(cold), f"{name} at {t}: the spread's end differs after forward play"
    else:
        assert _masked(played) == _masked(cold), f"{name} at {t}: forward play paints another frame than the cold seek"
