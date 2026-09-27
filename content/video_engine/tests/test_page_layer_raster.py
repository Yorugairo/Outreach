"""P72 T46a (R26-325 / R26-397) - A PLAYED FRAME EQUALS ITS COLD SEEK ON A PAGE THAT BREATHED, THEN STOOD STILL.

The template's `.lp-page { will-change: transform }` made every page a compositor layer, and Chromium keeps such a
layer's RASTER SCALE across frames: a page that breathed larger (the live idle's ~1.012) is later drawn from the old,
larger raster, so a played frame differed from a cold seek by ~66k px with an identical DOM and identical transforms
(H row 12, 333.42; P72 T21's diagnosis). The decision: the page is not promoted (the world still is). Kept in its own
file and patch because it moves golden BYTES (raster-level) - the parent takes it or leaves it on its frames.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

from test_wave3_engine_correctness import DIV_PROJECT, _Served, needs_browser  # noqa: E402


# ---- R26-325 / R26-397: played == cold on a page that breathed, then stood still (H row 12's own page) ---------------
ROW12_PLATE = "ledger:ev-capex-ocf-94-bars-v1:bars::right:axes:cut;idle=live;readability=longform"   # page_arith()
ROW12_RELIGHT = {"kind": "relight", "at": 7.59, "dur": 1.2, "ref": "title"}   # H 332.21 - 324.62 (the scene's zero)
ROW12_TS, ROW12_FROM = (7.5, 9.5), 5.0   # two instants the base diffs at on this bed (63,882 / 44,470 px - logs/scan325-base.log)
ROW12_KINETICS = {"idle": True, "stop_action": True, "arap_morph": True, "camera": True, "span_tone": "dark", "span_alpha": 0.3,
                  "analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False, "curvature_stroke": True,
                  "plate_idle_paints": False}   # Steel and Paper H's timeline `kinetics`, verbatim


def _row12():
    import build_golden_sources as G
    import build_scene_timeline_f as BST
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(ROW12_PLATE, (0, 0, 0), DIV_PROJECT)
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, 13.8], "docks": [], "species": [dict(ROW12_RELIGHT)]}]
    tl = G._timeline("R26-325: row 12's page, played vs cold", scenes, {}, "16:9")
    tl["kinetics"] = dict(ROW12_KINETICS)   # the door's own flags: `idle` is what makes the page breathe
    return tl, dict(G._base_uris(), **BST.longform_assets(tl))


def test_R26_397_the_template_promotes_the_world_not_the_page():
    """The decision, pinned where it is written: `.lp-page` carries no will-change (a page is re-rastered at the scale it
    stands at, so a seek is the play); the world keeps its own (its ken and camera moves stay composited)."""
    import re
    import render_baseline as RB
    css = RB.TEMPLATE.read_text(encoding="utf-8")
    page = re.search(r"\.lp-page \{([^}]*)\}", css)
    world = re.search(r"\.world \{([^}]*)\}", css)
    assert page and "will-change" not in page.group(1), page.group(1) if page else "no .lp-page rule"
    assert world and "will-change" in world.group(1), "the world is still its own layer"


@needs_browser
def test_R26_325_row_12s_page_played_through_equals_its_cold_seek():
    """Played at 24 fps from 5.0 s, the page breathing (1.0001 .. 1.0119), vs a fresh page seeked to the same instant.
    Base: 63,882 px (max 61) at 7.5 and 44,470 (max 63) at 9.5 on this bed - on the H door 66,327 at 333.42 - with an
    identical DOM: the page's compositor layer keeps the raster scale of an earlier, larger breath."""
    import numpy as np
    tl, uris = _row12()
    s = _Served(tl, uris)
    played = {}
    try:
        grid = sorted(set(round(ROW12_FROM + i / 24, 4) for i in range(int((max(ROW12_TS) - ROW12_FROM) * 24) + 1)) | set(ROW12_TS))
        for t in grid:
            im = s.shot(t)
            if t in ROW12_TS:
                played[t] = im
        assert not s.errs, s.errs
    finally:
        s.close()
    diffs = {}
    for t in ROW12_TS:
        c = _Served(tl, uris)
        try:
            cold = c.shot(t)
        finally:
            c.close()
        d = np.abs(np.asarray(played[t]).astype(int) - np.asarray(cold).astype(int)).max(axis=2)
        diffs[t] = (int((d > 0).sum()), int(d.max()))
    assert all(n == 0 for n, _m in diffs.values()), f"played vs cold (px, max): {diffs}"


# ---- R26-397's seam: unpromoted, a sliding page's clip edge and its own edge are one antialiased line --------------------
SEAM_SURFACE = "slide-depth@proof-mid"   # H-like: a dense-line page slides left through the depth to a story page, u ~ 0.5
SEAM_BAND = (560, 680)                   # the incoming page's leading edge sits at x 619.5 on this frame (probed)
SEAM_TOL = 12                            # grey levels: the seam read 117 against a ~45 board; cured it reads within 1


def _column_outliers(png: bytes, band: tuple[int, int], tol: float) -> list[tuple[int, float, float]]:
    """Columns whose mean luminance (every row) stands off the median of their six neighbours by more than `tol`."""
    import io

    import numpy as np
    from PIL import Image
    lum = np.asarray(Image.open(io.BytesIO(png)).convert("L")).astype(float).mean(axis=0)
    out = []
    for x in range(band[0], band[1]):
        near = float(np.median(np.r_[lum[x - 3:x], lum[x + 1:x + 4]]))
        if abs(lum[x] - near) > tol:
            out.append((x, round(float(lum[x]), 1), round(near, 1)))
    return out


@needs_browser
def test_R26_397_a_page_sliding_through_the_depth_leaves_no_seam():
    """Through the depth a sliding world is scaled, so its clip edge - which IS its page's edge - falls between device
    pixels. Unpromoted, the page's and the clip's antialiasing stacked and the world's cream ground bled through: a
    full-height 1-px light line at x 619 (mean 117 on a ~45 board). While a slide runs the ground is clear
    (`.world.ledger.sliding`), so no column of the seam's band stands off its neighbours."""
    import render_baseline as RB
    assert _column_outliers(RB.render_surface(SEAM_SURFACE), SEAM_BAND, SEAM_TOL) == []
