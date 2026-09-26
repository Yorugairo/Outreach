"""P72 T46a - the engine-correctness follow-ups (lane B), one test per clause.

R26-385  the standing line reads through an extend's rescale on a long-form page (the arriving state's opaque plot
         panel was raised over it on the clock's first frame, so the plot stood empty for the whole rescale phase).
R26-400  (pinned by test_prop_shadow::test_the_CONTACT_hands_over_to_the_HATCH_at_settle_with_no_pop - the test was right).
R26-341  a `spread` paints on a long-form page (it was inserted as the chart's first child, UNDER the opaque plot panel).
R26-386  a series' `dash` is drawn on a line page (it was accepted and ignored: three committed objects drew solid), and a
         malformed or misplaced `dash` is refused by name (s106).
R26-390  the two-plate ground under a morph obeys E99 s52 like the soak does: its first frame carries at most a twentieth
         of the board, no frame more than an eighth (it arrived at 0.087 on its first frame: expoOut from b = 0).
R26-325 / R26-397  its own file and patch: test_page_layer_raster.py (the template decision moves golden bytes).
R26-399  the purity fixes' stale notes: determinism_check's "known R26-21" class (T21 made the snap pure in t) is gone,
         and a world's transform-origin is the frame's own (a landing's dip left wA's `50% 100%` set after play).
R26-401  `lpVarHex` reads the sign inks where the template declares them (`.lp`, not `:root`): a lone sign-inked primary
         line's halo floods its own green / red, not the raw `var(...)` string (an invalid flood-color).
R26-402  a reference rule's fade-in shows: its reveal is written on the rule's STYLE (the template's `.hrule { opacity:
         .9 }` outranks the attribute lpPaintChart wrote, so the rule stood at .9 from the page's first frame).
"""
from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))


def _chromium_available() -> bool:
    try:
        import served_player as SP
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


class _Served:
    """One served page of a timeline: seek, shoot the stage, evaluate."""

    def __init__(self, tl: dict, uris: dict, aspect: str = "16:9"):
        import render_baseline as RB
        import served_player as SP
        self.RB = RB
        self.size = RB.STAGE[aspect]
        td = tempfile.TemporaryDirectory()
        html = Path(td.name) / "probe.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.page, self.errs, self._close = SP.open_served(html, *self.size, cleanup=td.cleanup)

    def shot(self, t: float):
        from PIL import Image
        return Image.open(io.BytesIO(self.RB.frame_png(self.page, t, self.size))).convert("RGB")

    def ev(self, js: str, arg=None):
        return self.page.evaluate(js, arg)

    def close(self):
        self._close()


# ---- R26-385: the standing line through an extend's rescale on a long-form page ------------------------------------
# The standing (state 0) series paths, sampled along their DRAWN length in stage pixels (the path's own screen CTM,
# less the stage's origin): what a viewer sees of the line is the ink at those points.
LINE_SAMPLES_JS = """(n) => {
  const w = [wA, wB].filter(e => e.__lp && e.classList.contains('ledger')).pop();
  const S = w.__lp.states[0], stage = document.getElementById('stage').getBoundingClientRect(), out = [];
  for (const pp of S.paths || []) {
    const len = pp.p.getTotalLength(), off = parseFloat(pp.p.getAttribute('stroke-dashoffset')) || 0, drawn = Math.max(0, len - off);
    const m = pp.p.getScreenCTM();
    for (let i = 1; i < n; i++) {
      const q = pp.p.getPointAtLength(drawn * i / n), s = new DOMPoint(q.x, q.y).matrixTransform(m);
      out.push([s.x - stage.x, s.y - stage.y]);
    }
    return {stroke: pp.p.getAttribute('stroke'), pts: out, drawn: drawn / (len || 1)};
  }
  return null;
}"""


def _hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _ink_share(img, pts, rgb) -> float:
    """The share of sample points whose 3x3 neighbourhood holds the stroke's WARM ink: a primary line blooms (s117: a hot
    core over its ink), so its centre reads (255, 202, 174) for #FF8A4C - red at least 170 and red over blue by 50, which
    the long-form panel (34, 40, 48), the board and the grey furniture never are."""
    hit = 0
    for x, y in pts:
        xi, yi = int(round(x)), int(round(y))
        near = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                px = img.getpixel((min(max(xi + dx, 0), img.width - 1), min(max(yi + dy, 0), img.height - 1)))
                if px[0] >= 170 and px[0] - px[2] >= 50 and (rgb[0] - rgb[2]) >= 50:
                    near = True
        hit += near
    return hit / max(1, len(pts))


def _issuance(longform: bool):
    import build_golden_sources as G
    saved = G.PROJ_PLATE
    try:
        if not longform:
            G.PROJ_PLATE = saved.replace(";readability=longform", "")
        return G.project_issuance_2026e()
    finally:
        G.PROJ_PLATE = saved


@needs_browser
@pytest.mark.parametrize("longform", [True, False], ids=["longform", "plain"])
def test_R26_385_the_standing_line_reads_through_an_extends_rescale(longform):
    """project-issuance-2026e: the extend's rescale phase is the first XF_EXTEND.RESCALE (0.45) of its clock
    (8.00-8.53 s). Before it (7.8) and through it (8.10, 8.30, 8.50) the issuance line stands on the plot in its ink.
    Base: on the long form the plot is EMPTY through the phase (the arriving panel covers it); the plain profile draws it."""
    import build_golden_sources as G
    tl, uris = _issuance(longform)
    at, dur = G.PROJ_AT, G.PROJ_DUR
    s = _Served(tl, uris)
    try:
        reads = {}
        for t in (round(at - 0.2, 2), round(at + 0.1, 2), round(at + 0.25, 2), round(at + 0.45 * dur - 0.03, 2)):
            img = s.shot(t)
            smp = s.ev(LINE_SAMPLES_JS, 40)
            assert smp and smp["pts"], t
            reads[t] = round(_ink_share(img, smp["pts"], _hex_rgb(smp["stroke"])), 3)
        assert not s.errs, s.errs
    finally:
        s.close()
    low = {t: v for t, v in reads.items() if v < 0.9}
    assert not low, f"the standing line does not read on the plot at {low} (all reads {reads})"


# ---- R26-341: a spread on a long-form page -----------------------------------------------------------------------
DIV_PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
DIV_PLATE = "ledger:ev-divergence-v1:line:234:right:axes:cut"   # row 24's page (the divergence, all four lines drawn), still
SPREAD = {"kind": "spread", "at": 3.0, "dur": 2.0, "from": 2, "to": 0}   # the giants -> the memory makers (row 1's)
SPREAD_BEFORE, SPREAD_AFTER = 2.9, 6.0

# interior points of the spread's own polygon (isPointInFill), in stage px, kept 12 px clear of every drawn series
SPREAD_INTERIOR_JS = """() => {
  const w = [wA, wB].filter(e => e.__lp && e.classList.contains('ledger')).pop(), sp = w.querySelector('.lp-spread');
  const stage = document.getElementById('stage').getBoundingClientRect(), m = sp.getScreenCTM(), svg = sp.ownerSVGElement;
  const b = sp.getBBox(), sers = [...svg.querySelectorAll('path.ser')], out = [];
  for (let i = 1; i < 24; i++) for (let j = 1; j < 12; j++) {
    const p = svg.createSVGPoint(); p.x = b.x + b.width * i / 24; p.y = b.y + b.height * j / 12;
    if (!sp.isPointInFill(p)) continue;
    const s = new DOMPoint(p.x, p.y).matrixTransform(m), sx = s.x - stage.x, sy = s.y - stage.y;
    const near = sers.some((q) => { const r = q.getBoundingClientRect(); if (sx + stage.x < r.left - 12 || sx + stage.x > r.right + 12) return false;
      const L = q.getTotalLength(), mm = q.getScreenCTM(); for (let k = 0; k <= 200; k++) { const a = q.getPointAtLength(L * k / 200), z = new DOMPoint(a.x, a.y).matrixTransform(mm);
        if (Math.hypot(z.x - stage.x - sx, z.y - stage.y - sy) < 12) return true; } return false; });
    if (!near) out.push([sx, sy]);
  }
  return out;
}"""


def _divergence_spread(plate: str):
    import build_golden_sources as G
    import build_scene_timeline_f as BST
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        assert not BST.validate_species([SPREAD], (0, 0, 0), plate)
        world = BST.world_for_plate(plate, (0, 0, 0), DIV_PROJECT)
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, 10.0], "docks": [], "species": [dict(SPREAD)]}]
    tl = G._timeline("R26-341: a spread on the divergence", scenes, {}, "16:9")
    return tl, dict(G._base_uris(), **BST.longform_assets(tl))


@needs_browser
@pytest.mark.parametrize("profile", ["", ";readability=longform"], ids=["plain", "longform"])
def test_R26_341_a_spread_paints_on_the_divergence_in_either_profile(profile):
    """The same spread, the same page: where the fill stands (inside its polygon, clear of every line) the frame after
    it bleeds must differ from the frame before it by a visible tint. Base: the plain profile tints (~40 levels), the
    long form does not move a level - its fill is painted UNDER the opaque plot panel."""
    s = _Served(*_divergence_spread(DIV_PLATE + profile))
    try:
        before = s.shot(SPREAD_BEFORE)
        after = s.shot(SPREAD_AFTER)
        pts = s.ev(SPREAD_INTERIOR_JS)
        assert not s.errs, s.errs
    finally:
        s.close()
    assert len(pts) >= 20, f"the spread's interior was found: {len(pts)} points"
    diffs = sorted(sum(abs(a - b) for a, b in zip(before.getpixel((int(x), int(y))), after.getpixel((int(x), int(y)))))
                   for x, y in pts)
    median = diffs[len(diffs) // 2]
    assert median >= 20, f"the spread does not show: the median change inside it is {median} levels over {len(pts)} points"


# ---- R26-386: a series' `dash` ------------------------------------------------------------------------------------
MEMORY_PLATE = "ledger:ev-memory-monitor-v1:line::right"   # series 2 is the "12m avg", "dash": "7 6" (the object's own)


def _line_page(**extra) -> dict:
    return {"title": "t", "src": "s", "series": [
        {"label": "a", "color": "teal", "pts": [[2020 + k, 10 + k] for k in range(20)]},
        dict({"label": "b", "color": "deemph", "pts": [[2020 + k, 12 + k] for k in range(20)]}, **extra)]}


@pytest.mark.parametrize("dash", ["7 6", "7,6", "4", 5, 2.5, "7 6 2 6"])
def test_R26_386_a_well_formed_dash_validates(dash):
    import ledger_page as LPG
    assert LPG.validate(_line_page(dash=dash), "line") == []


@pytest.mark.parametrize("dash", ["seven", "7 -6", "", "0", "0 0", [7, 6], True, "7 6 x", -3])
def test_R26_386_a_malformed_dash_is_refused_by_name(dash):
    import ledger_page as LPG
    errs = LPG.validate(_line_page(dash=dash), "line")
    assert any("series[1]" in e and "`dash`" in e for e in errs), errs


def test_R26_386_a_dash_on_a_projection_is_refused_the_projection_owns_its_dashes():
    import ledger_page as LPG
    page = {"title": "t", "src": "s", "series": [
        {"label": "a", "color": "teal", "pts": [[2020 + k, 10 + k] for k in range(6)]},
        {"label": "b", "color": "teal", "pts": [[2021 + k, 12 + k] for k in range(6)]},
        {"color": "teal", "later": True, "pts": [[2025, 15], [2026, 20]], "dash": "7 6",
         "projection": {"label": "2026E", "tier": "PLAUSIBLE", "src": "the range"}}]}
    errs = LPG.validate(page, "line")
    assert any("series[2]" in e and "`dash`" in e and "projection" in e for e in errs), errs


def test_R26_386_a_dash_on_a_page_that_does_not_draw_a_line_series_is_refused():
    import ledger_page as LPG
    page = {"title": "t", "src": "s", "series": [{"label": "a", "color": "teal", "pts": [[2020, 1], [2021, 2]], "dash": "7 6"}]}
    errs = LPG.validate(page, "bars")
    assert any("series[0]" in e and "`dash`" in e for e in errs), errs


def test_R26_386_the_committed_objects_that_carry_a_dash_validate():
    import json
    import ledger_page as LPG
    objs = DIV_PROJECT / "evidence/objects"
    for name in ("ev-debt-issuance-line-v1", "ev-capex-funding-v1", "ev-memory-monitor-v1"):
        obj = json.loads((objs / f"{name}.series.json").read_text(encoding="utf-8"))
        assert any("dash" in s for s in obj["series"]), name
        assert [e for e in LPG.validate(obj, "line") if "`dash`" in e] == [], name


DASH_READ_JS = """(si) => {
  const w = [wA, wB].filter(e => e.__lp && e.classList.contains('ledger')).pop(), S = w.__lp.states ? w.__lp.states[0] : w.__lp;
  const pp = S.paths.find(q => (q.si | 0) === si), m = pp.p.getAttribute('mask'), mk = m ? document.getElementById(m.slice(5, -1)) : null;
  const tw = mk ? mk.querySelector('path') : null, stage = document.getElementById('stage').getBoundingClientRect(), ctm = pp.p.getScreenCTM();
  const L = pp.p.getTotalLength(), pts = [];
  for (let k = 0; k <= 400; k++) { const q = pp.p.getPointAtLength(L * k / 400), z = new DOMPoint(q.x, q.y).matrixTransform(ctm); pts.push([z.x - stage.x, z.y - stage.y]); }
  return {dash: tw ? tw.getAttribute('stroke-dasharray') : null, off: pp.p.getAttribute('stroke-dashoffset'), len: L, stroke: pp.p.getAttribute('stroke'), pts};
}"""


def _memory_monitor():
    import build_golden_sources as G
    import build_scene_timeline_f as BST
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(MEMORY_PLATE, (0, 0, 0), DIV_PROJECT)
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, 12.0], "docks": [], "species": []}]
    tl = G._timeline("R26-386: the memory monitor's 12m avg", scenes, {}, "16:9")
    return tl, dict(G._base_uris(), **BST.longform_assets(tl))


@needs_browser
def test_R26_386_a_dashed_series_draws_dashed_on_a_dense_line_page():
    """ev-memory-monitor-v1's "12m avg" carries `dash: "7 6"`. Built (10 s), its stroke is masked by a twin dashed on the
    authored pattern, and along its drawn length the ink shows in dashes: the share of the path's own points that land
    on ink is the pattern's (7 / 13 ~ 0.54), never the solid line's ~1. Base: no mask, the ink share ~1."""
    s = _Served(*_memory_monitor())
    try:
        img = s.shot(10.0)
        r = s.ev(DASH_READ_JS, 2)
        solid = s.ev(DASH_READ_JS, 0)
        assert not s.errs, s.errs
    finally:
        s.close()
    rgb = _hex_rgb(r["stroke"])   # the 12m avg's own ink (#b8c4d0); a gap shows the board (~37, 48, 61)

    def ink(px):
        return sum(abs(a - b) for a, b in zip(px, rgb)) <= 120
    on = [ink(img.getpixel((int(x), int(y)))) for x, y in r["pts"] if 0 <= x < img.width and 0 <= y < img.height]
    share = sum(on) / max(1, len(on))
    assert 0.3 < share < 0.8, f"the 12m avg reads dashed along its length: ink on {share:.2f} of its points"
    assert r["dash"] == "7 6", f"the 12m avg's stroke is masked by its authored dashes: {r['dash']}"
    assert solid["dash"] is None, "a series without the key carries no mask"


# ---- R26-390: the two-plate ground under a morph, on E99 s52's own metric -------------------------------------------
@needs_browser
def test_R26_390_the_plates_ground_under_a_morph_never_snaps_in():
    """test_melt_morph's s52 sweep (its metric, its thresholds, its window - imported, never copied) on the golden whose
    ground is the two-plate cross-fade. Base: the first frame carries 0.087 of the board (the plate's expoOut from b 0)."""
    import test_melt_morph as MM
    groundS = MM._morph_dial("S") * MM._morph_dial("GROUND")
    with MM._player("morph-planted-plates", MM.FLAGS) as (page, size):
        rows = MM._sweep(page, size, MM.CUT, MM.CUT + 2.0)
    base = rows[0][1]
    full = max(c for t, c in rows if t <= MM.CUT + groundS + 1e-9)
    span = full - base
    assert span > 0.3, f"the board never filled: base {base:.4f} full {full:.4f}"
    fill = [(t, (c - base) / span) for t, c in rows]
    steps = [(fill[i][0], round(fill[i][1] - fill[i - 1][1], 4)) for i in range(1, len(fill))]
    worst_t, worst = max(steps, key=lambda r: abs(r[1]))
    during = [f for t, f in fill if t <= MM.CUT + groundS + 1e-9]
    assert fill[1][1] <= MM.GROUND_FIRST_MAX, f"the board is {fill[1][1]:.3f} filled on the page's first frame (steps {steps[:8]})"
    assert abs(worst) <= MM.GROUND_STEP_MAX, f"the board's fill jumped {worst:+.3f} at t={worst_t}"
    # (s52's third clause, 'whole when the window closes', is not this row's: on this golden the coverage peaks mid-window
    # and eases ~0.03 before the punch - 0.9685 at 16.50 on the base engine and the patched alike; only never-contracting)
    assert min(during[i] - during[i - 1] for i in range(1, len(during))) > -0.02, during


# ---- R26-399: the stale notes the purity fixes left -------------------------------------------------------------
ORIGINS_JS = "() => [wA, wB].map((w) => [w.style.transformOrigin, w.style.display])"


@needs_browser
def test_R26_399_a_played_world_carries_no_origin_a_cold_seek_would_not():
    """prop-stamp: the stamp's landing dips the ground (worldAnswer.y > 0), and the outgoing world is scaled about its
    bottom edge while it rides down - `transform-origin: 50% 100%` on wA. Base: that origin stays after the dip on the
    played path (a cold seek past it has none); the next transform written on wA would turn about it."""
    import render_baseline as RB
    tl, uris, _t, _a = RB.load_surface("prop-stamp")
    t_end = 12.0
    s = _Served(tl, uris)
    try:
        for k in range(int(9.5 * 24), int(t_end * 24) + 1):
            s.shot(round(k / 24, 4))
        played = s.ev(ORIGINS_JS)
    finally:
        s.close()
    c = _Served(tl, uris)
    try:
        c.shot(round(int(t_end * 24) / 24, 4))
        cold = c.ev(ORIGINS_JS)
    finally:
        c.close()
    assert played == cold, f"the worlds' origins after play {played} vs a cold seek {cold}"


def test_R26_399_the_determinism_check_names_no_known_class():
    """T21 (7263013) made the snap window pure in t (boundaryFirst, snapCardBox), so the check's "known R26-21" class
    excuses nothing real: every warm/cold mismatch is a mismatch, and the module says so."""
    import inspect
    import determinism_check as DC
    assert not hasattr(DC, "known_class") and not hasattr(DC, "snap_windows"), "the R26-21 class is retired"
    assert "R26-21" not in (DC.__doc__ or "").split("R26-21 was", 1)[0], "the docstring no longer names R26-21 an exception"
    assert "strict" not in inspect.signature(DC.run).parameters, "--strict failed on a class that no longer exists"


def test_R26_399_the_melt_snapshot_docstring_names_the_boundary_on_both_paths():
    import test_melt_snapshot_is_current as MS
    doc = MS.__doc__ or ""
    assert "which this slice leaves as it was" not in doc, "point 3 still describes the cause T21 removed"
    assert "span[0]" in doc, "point 3 names the clone's frame: the boundary's, played and seeked"


# ---- R26-401: lpVarHex and the sign inks ---------------------------------------------------------------------------
def _object_page(series: dict, plate_tail: str, species: list | None = None, span: float = 12.0):
    """A one-scene timeline of a page built from `series` (written as a temporary evidence object)."""
    import json
    import build_golden_sources as G
    import build_scene_timeline_f as BST
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objs = Path(td) / "evidence/objects"
            objs.mkdir(parents=True)
            (objs / "ev-t46a-probe.series.json").write_text(json.dumps(series), encoding="utf-8")
            world = BST.world_for_plate("ledger:ev-t46a-probe:" + plate_tail, (0, 0, 0), Path(td))
            BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, span], "docks": [], "species": list(species or [])}]
    tl = G._timeline("P72 T46a probe", scenes, {}, "16:9")
    return tl, dict(G._base_uris(), **BST.longform_assets(tl))


LONE_UP = {"title": "One line, rising", "src": "s", "ylabel": "index",
           "series": [{"label": "the index", "pts": [[2000 + k / 4, 100 + 2 * k] for k in range(40)]}]}
HALO_JS = r"""() => {
  const w = [wA, wB].filter(e => e.__lp && e.classList.contains('ledger')).pop(), S = w.__lp.states ? w.__lp.states[0] : w.__lp;
  const pp = S.paths[0], f = (pp.p.style.filter || '').match(/url\(["']?#([^"')]+)/);
  const fl = f ? [...document.getElementById(f[1]).querySelectorAll('feFlood')].map(e => e.getAttribute('flood-color')) : [];
  return {stroke: pp.p.getAttribute('stroke'), filter: pp.p.style.filter, floods: fl, pos: getComputedStyle(w.querySelector('.lp')).getPropertyValue('--lp-pos').trim()};
}"""


@needs_browser
def test_R26_401_a_lone_sign_inked_line_blooms_in_its_own_ink():
    """A lone undeclared series takes its SIGN colour (`var(--lp-pos)` rising). Its primary bloom's halos flood in that
    ink, read off the template (`.lp`'s --lp-pos, #3DDC84). Base: the flood-color is the raw "var(--lp-pos)" string - an
    invalid flood-color, which Chromium drops for the default (black)."""
    s = _Served(*_object_page(LONE_UP, "line::right"))
    try:
        s.shot(8.0)
        r = s.ev(HALO_JS)
        assert not s.errs, s.errs
    finally:
        s.close()
    assert r["stroke"] == "var(--lp-pos)", r
    assert r["floods"], f"the primary carries its hot filter's halos: {r}"
    assert all(f.lower() == r["pos"].lower() for f in r["floods"]), f"the halos flood the sign ink {r['pos']}: {r['floods']}"


# ---- R26-402: the reference rule's fade-in ---------------------------------------------------------------------------
RULED = {"title": "A line and its rule", "src": "s", "ylabel": "index",
         "series": [{"label": "the index", "color": "teal", "pts": [[2000 + k / 4, 100 + 2 * k] for k in range(40)]}],
         "hlines": [{"y": 150, "label": "the rule"}]}
RULE_OP_JS = """() => { const w = [wA, wB].filter(e => e.__lp && e.classList.contains('ledger')).pop(), r = w.querySelector('line.hrule');
  return r ? +getComputedStyle(r).opacity : null; }"""


@needs_browser
def test_R26_402_a_reference_rule_fades_in_with_its_page():
    """The rule's reveal is `0.9 * clamp01(c / 0.25)` on the page's build clock c. Sampled across the build, its COMPUTED
    opacity takes values between 0 and 0.9 and lands at the template's 0.9. Base: 0.9 on every frame (the CSS wins)."""
    s = _Served(*_object_page(RULED, "line::right:axes"))
    try:
        ops = []
        for k in range(0, 61):
            s.shot(round(k * 0.1, 2))
            ops.append(round(s.ev(RULE_OP_JS), 3))
        assert not s.errs, s.errs
    finally:
        s.close()
    assert ops[-1] == 0.9, f"the rule lands at the template's .9: {ops[-1]}"
    assert ops[0] < 0.05, f"the rule is not on the page before its build: {ops[:5]}"
    assert any(0.05 < o < 0.85 for o in ops), f"the rule fades in - it never stands between: {ops}"
