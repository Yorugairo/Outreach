"""P72 T46f (1)-(3) - the wave-3 carries T46a-e could not close (lane B), one section per row.

R26-385 (clause 2)  an extend that reveals a later series AFTER A WINDOWED RESCALE reveals it in the NEW window: the
                    window grows to the revealed series' last datum (it was sliced to the standing window - a 2026E
                    projection lost its 2026 point, or the extend was refused as "chart_to rescale ... keeps 1 point");
                    a standing series' own data past the old window draw on at the pen with it, from its shared datum.
R26-373 (c)         a punch / focus_zoom whose target is a datum on a DOCKED chart card: the camera resolves after the
                    frame's docks are laid out (render() lays them out first when, and only when, a camera move this
                    frame names a dock datum), so a cold seek is the played frame and the look is the datum as drawn.
R26-106 (b)         under kinetics.stroke_width a ledger page's series lines draw as the width-varying brush (a filled
                    outline regrown from the drawn prefix every frame, every datum a vertex of it); flag off, the dash.
"""
from __future__ import annotations

import copy
import io
import json
import math
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402


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

    def seek(self, t: float) -> None:
        for _ in range(2):
            self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                               "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)

    def ev(self, js: str, arg=None):
        return self.page.evaluate(js, arg)

    def close(self):
        self._close()


# ---- R26-385 clause 2: an extend after a WINDOWED rescale ---------------------------------------------------------
def _projection(pts3: bool = False) -> dict:
    """The golden issuance page's object (the 2025 actual and its 2026E continuation); `pts3` gives the estimate a
    mid-point, so a window that keeps two of its points would CUT it rather than refuse it."""
    import build_golden_sources as G
    s = G.projection_series()
    if pts3:
        s = copy.deepcopy(s)
        a, b = s["series"][1]["pts"]
        s["series"][1]["pts"] = [a, [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], b]
    return s


def _derive(series: dict, species: list[dict]) -> dict:
    """The compiler's derived page states for `species` on the golden issuance page (its plate, a temp episode)."""
    import build_golden_sources as G
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{G.PROJ_ID}.series.json").write_text(json.dumps(series), encoding="utf-8")
            world = B.world_for_plate(G.PROJ_PLATE, (0, 0, 0), Path(td))
            B.stamp_full_stage(world["page"])
            B.derive_rescale_states(world, species, G.PROJ_PLATE, Path(td))
    finally:
        B.ASPECT = saved
    return world


RESCALE_AT, EXTEND_AT, XF_DUR = 8.0, 10.5, 1.2


def _rescale(window) -> dict:
    return {"kind": "chart_to", "at": RESCALE_AT, "dur": XF_DUR, "to": "rescale", "window": list(window)}


def _extend_series(k: int = 1) -> dict:
    return {"kind": "chart_to", "at": EXTEND_AT, "dur": XF_DUR, "to": "extend", "series": k}


def _xs(state: dict, i: int) -> list[float]:
    return [float(p[0]) for p in state["series"][i]["pts"]]


def test_R26_385_the_revealed_series_keeps_its_points_past_the_standing_window():
    """A three-point estimate after window [2021, 2025.5]: base kept [2025, 2025.5] (its 2026 point cut); the NEW window
    runs to the estimate's last datum and the state draws all three."""
    species = [_rescale([2021, 2025.5]), _extend_series()]
    world = _derive(_projection(pts3=True), species)
    ext = world["page_states"][-1]
    assert ext["derived"] == "extend"
    assert ext["axes"]["xdomain"] == [2021.0, 2026.0], ext["axes"].get("xdomain")
    assert _xs(ext, 1) == [2025.0, 2025.5, 2026.0], _xs(ext, 1)
    assert species[1]["from_series"] == 1


def test_R26_385_the_real_projection_after_a_windowed_rescale_compiles_and_reveals_2026():
    """The golden's own two-point estimate after window [2022, 2025]: base REFUSED it ("chart_to rescale: the window
    [2022.0, 2025.0] keeps 1 point(s) of the series" - an extend named a rescale); it reveals [2025, 2026]."""
    species = [_rescale([2022, 2025]), _extend_series()]
    world = _derive(_projection(), species)
    ext = world["page_states"][-1]
    assert ext["axes"]["xdomain"] == [2022.0, 2026.0]
    assert _xs(ext, 1) == [2025.0, 2026.0]
    assert _xs(ext, 0) == [2022.0, 2023.0, 2024.0, 2025.0]   # the standing series in the new window, nothing added
    assert species[1].get("from_index") == 5   # the standing series' last shared datum (2025), in the page's index space


def test_R26_385_a_standing_series_past_the_old_window_is_capped_at_its_shared_datum():
    """Window [2021, 2023], then the estimate: the new window [2021, 2026] also holds the actual's 2024 and 2025 - the
    species names the shared datum (2023, index 3) so the player draws them on at the pen rather than popping them."""
    species = [_rescale([2021, 2023]), _extend_series()]
    world = _derive(_projection(), species)
    ext = world["page_states"][-1]
    assert ext["axes"]["xdomain"] == [2021.0, 2026.0]
    assert _xs(ext, 0) == [2021.0, 2022.0, 2023.0, 2024.0, 2025.0]
    assert species[1]["from_index"] == 3 and species[1]["from_series"] == 1


def test_R26_385_a_later_series_inside_the_window_keeps_the_window():
    """Control (holds at base): a later series with nothing past the standing window's end is revealed IN that window -
    the story's window stands, nothing is grown and no cap is named."""
    s = copy.deepcopy(_projection())
    s["series"][1] = {"label": "later", "color": s["series"][0]["color"], "later": True,
                      "pts": [[2021, 40], [2023, 60], [2025, 90]]}   # a plain later series (not an estimate)
    species = [_rescale([2022, 2025]), _extend_series()]
    world = _derive(s, species)
    ext = world["page_states"][-1]
    assert ext["axes"]["xdomain"] == [2022.0, 2025.0]
    assert _xs(ext, 1) == [2023.0, 2025.0]
    assert "from_index" not in species[1]


def test_R26_385_an_extend_with_no_windowed_rescale_is_unchanged():
    """Control: the golden's own row (no rescale) derives exactly the state it always did - no window, no cap."""
    species = [_extend_series()]
    world = _derive(_projection(), species)
    ext = world["page_states"][-1]
    assert "xdomain" not in (ext.get("axes") or {}) and "from_index" not in species[0]


def _issuance_tl(species: list[dict]):
    import build_golden_sources as G
    world = _derive(_projection(), species)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    tl = G._timeline("T46f: an extend after a windowed rescale", scenes, {}, "16:9")
    return tl, dict(G._base_uris(), **B.longform_assets(tl))


# every series path of the ACTIVE state: its drawn share, its drawn end and its first point in stage px, the plot's box
SERIES_JS = """() => {
  const w = [wA, wB].filter(e => e.__lp && e.classList.contains('ledger')).pop(), lp = w.__lp;
  const S = lp.states[lp.active | 0], stage = document.getElementById('stage').getBoundingClientRect(), k = 1920 / stage.width;
  const px = (p, q) => { const s = new DOMPoint(q.x, q.y).matrixTransform(p.getScreenCTM()); return [(s.x - stage.x) * k, (s.y - stage.y) * k]; };
  const panel = S.lfPanelEl ? S.lfPanelEl.getBoundingClientRect() : S.chart.getBoundingClientRect();
  return { active: lp.active | 0, plot: [(panel.left - stage.x) * k, (panel.right - stage.x) * k],
    paths: (S.paths || []).map(pp => { const len = pp.p.getTotalLength(), off = parseFloat(pp.p.getAttribute('stroke-dashoffset')) || 0;
      const f = Math.max(0, Math.min(1, 1 - off / (len || 1)));
      return { si: pp.si, f, n: (pp.data || []).length, x0: (pp.data || [[null]])[0][0], end: px(pp.p, pp.p.getPointAtLength(len * f)),
               full: px(pp.p, pp.p.getPointAtLength(len)), op: pp.p.style.opacity }; }) };
}"""


@needs_browser
def test_R26_385_the_revealed_estimate_draws_to_2026_in_the_new_window():
    """In the player: after the windowed rescale the extend's state is the GROWN window, the estimate draws whole to
    its 2026 datum (inside the plot, right of the 2025 actual) and the actual stands whole."""
    tl, uris = _issuance_tl([_rescale([2022, 2025]), _extend_series()])
    s = _Served(tl, uris)
    try:
        s.seek(EXTEND_AT + XF_DUR + 0.5)
        r = s.ev(SERIES_JS)
        assert not s.errs, s.errs
    finally:
        s.close()
    assert r["active"] == 2, r
    by = {p["si"]: p for p in r["paths"]}
    assert by[1]["n"] == 2 and by[1]["x0"] == 2025 and by[1]["f"] > 0.999, by[1]
    assert by[0]["f"] > 0.999, by[0]
    x_act, x_est = by[0]["full"][0], by[1]["full"][0]
    assert x_est > x_act + 40 and r["plot"][0] <= x_est <= r["plot"][1] + 1, (x_act, x_est, r["plot"])


@needs_browser
def test_R26_385_the_standing_series_draws_on_from_its_shared_datum():
    """Window [2021, 2023] then the estimate: at the pen's start (just past the rescale phase) the actual is drawn to
    its shared 2023 datum and no further - its 2024-25 are not popped on - and whole at the extend's end."""
    tl, uris = _issuance_tl([_rescale([2021, 2023]), _extend_series()])
    s = _Served(tl, uris)
    try:
        s.seek(EXTEND_AT + XF_DUR * 0.47)   # just past XF_EXTEND.RESCALE (0.45): the pen has barely left
        early = s.ev(SERIES_JS)
        s.seek(EXTEND_AT + XF_DUR + 0.5)
        late = s.ev(SERIES_JS)
        assert not s.errs, s.errs
    finally:
        s.close()
    a0 = {p["si"]: p for p in early["paths"]}[0]
    a1 = {p["si"]: p for p in late["paths"]}[0]
    assert a0["n"] == 5, a0   # 2021..2025 in the grown window
    assert a0["f"] < 0.62, f"the actual popped on past its shared datum: drawn {a0['f']:.3f} (2023 is ~0.5 of it)"
    assert a1["f"] > 0.999, a1


@needs_browser
def test_R26_385_the_estimate_opens_from_the_real_line_never_from_nowhere():
    """E77 / E99 s93 on the grown reveal: one pen - while the actual is still drawing its 2024-25 the estimate has drawn
    nothing, and the estimate draws only once the actual stands at 2025 (a dashed line began in mid-air beside a line
    still climbing: the first cut of this slice, frames/385 11.22)."""
    tl, uris = _issuance_tl([_rescale([2021, 2023]), _extend_series()])
    s = _Served(tl, uris)
    reads = []
    try:
        for k in range(12):
            t = round(EXTEND_AT + XF_DUR * (0.46 + 0.05 * k), 3)
            s.seek(t)
            by = {p["si"]: p for p in s.ev(SERIES_JS)["paths"]}
            reads.append((t, round(by[0]["f"], 3), round(by[1]["f"], 3)))
        assert not s.errs, s.errs
    finally:
        s.close()
    bad = [r for r in reads if r[2] > 0.01 and r[1] < 0.995]
    assert not bad, f"the estimate drew before the actual reached it (t, actual, estimate): {bad} of {reads}"
    assert any(0.05 < r[1] < 0.99 for r in reads) and any(0.05 < r[2] < 0.99 for r in reads), reads   # both drew on the pen


# ---- R26-373 (c): a punch / focus_zoom on a datum of a DOCKED chart ------------------------------------------------
DOCK_DATUM = {"kind": "datum", "dock": 0, "series": 1, "index": 152}   # the chart-callout golden's bound datum (P72 T48)
PUNCH_AT, PUNCH_DUR, T_HOLD = 10.0, 2.0, 10.9   # mid-hold: the punch is at its full scale


@pytest.mark.parametrize("kind", ["punch", "focus_zoom"])
@pytest.mark.parametrize("dock", [0, "ev-golden-chart"])
def test_R26_373c_a_camera_move_may_name_a_datum_on_a_dock(kind, dock):
    tgt = dict(DOCK_DATUM, dock=dock)
    assert B._validate_target(kind, tgt, B.SPECIES_TARGETS[kind]) == []


@pytest.mark.parametrize("kind", ["pull_back", "build_to", "figure"])
def test_R26_373c_other_kinds_still_refuse_a_dock_datum_by_name(kind):
    allowed = B.SPECIES_TARGETS.get(kind, B.TARGET_KINDS)
    errs = B._validate_target(kind, dict(DOCK_DATUM), allowed)
    assert errs and any("dock" in e and kind in e for e in errs), errs


def _docks() -> list[dict]:
    return [{"slide": "ev-golden-chart", "slot": 0, "enter": 2.0, "exit": 30.0}]


def _evidence() -> dict:
    chart = {"series": [{"pts": [[i, i] for i in range(10)]}, {"pts": [[i, 2 * i] for i in range(6)]}]}
    return {"ev-golden-chart": {"species": "chart", "chart": chart, "badges": []}}


def test_R26_373c_a_camera_move_that_outlives_its_dock_is_refused_by_name():
    """The move reads its datum on EVERY frame of its window; a card that leaves mid-move leaves the eye nothing to hold
    (the zoom would drop to 1 in one frame) - a truth rule, refused naming the move, the window and the dock's leave."""
    tg = dict(DOCK_DATUM, index=5)
    ok = B.dock_datum_errors([{"kind": "punch", "at": 10.0, "dur": 2.0, "target": tg}], _docks(), _evidence(), "row 1")
    bad = B.dock_datum_errors([{"kind": "focus_zoom", "at": 29.0, "dur": 2.0, "target": tg}], _docks(), _evidence(), "row 1")
    assert ok == [], ok
    assert len(bad) == 1 and "focus_zoom" in bad[0] and "31" in bad[0] and "30" in bad[0] and "R26-373" in bad[0], bad
    ring = B.dock_datum_errors([{"kind": "callout", "at": 29.0, "dur": 2.0, "target": tg}], _docks(), _evidence(), "row 1")
    assert ring == [], ring   # a painted mark still only needs its dock on the stage at `at` (dock_ring_targets' clamp rule)


def _punch_tl(kind: str = "punch") -> tuple[dict, dict]:
    import build_golden_sources as G
    tl, uris = G.chart_callout()
    tl = copy.deepcopy(tl)
    tl["scenes"][0]["species"] = [{"kind": kind, "at": PUNCH_AT, "dur": PUNCH_DUR, "target": dict(DOCK_DATUM)}]
    return tl, uris


# the world's camera as PAINTED (its transform's camera prefix: translate(ox - W/2, oy - H/2) scale(s) ...) and the datum
# on the card as drawn this frame, both in stage px
CAM_JS = r"""() => {
  const sb = document.getElementById('stage').getBoundingClientRect(), k = 1920 / Math.max(1, sb.width);
  const w = [wA, wB].find(e => e.style.opacity !== '0' && e.style.visibility !== 'hidden') || wB;
  const m = /translate\((-?[\d.]+)px, (-?[\d.]+)px\) scale\(([\d.]+)\)/.exec(w.style.transform || '');
  const cam = m ? { ox: +m[1] + 960, oy: +m[2] + 540, s: +m[3] } : { s: 1 };
  const p = document.querySelector('.chartbox path[data-si="1"]'); let datum = null;
  if (p) { const n = (p.getAttribute('d').match(/-?\d+(\.\d+)?/g) || []).map(Number);
    const q = new DOMPoint(n[2 * 152], n[2 * 152 + 1]).matrixTransform(p.getScreenCTM());
    datum = [(q.x - sb.left) * k, (q.y - sb.top) * k]; }
  return { cam, datum, tf: w.style.transform };
}"""


@needs_browser
@pytest.mark.parametrize("kind", ["punch", "focus_zoom"])
def test_R26_373c_a_cold_seek_aims_the_camera_at_the_datum_as_drawn(kind):
    """ONE seek from the page's load to mid-move: the world's camera is at its zoom and its look is the docked chart's
    datum as the card is drawn THIS frame. Base: the camera resolved before the dock loop had laid the card out, so a
    cold seek found no dock on the stage and the eye stood still (scale 1)."""
    tl, uris = _punch_tl(kind)
    s = _Served(tl, uris)
    try:
        s.page.evaluate("t => { const e = document.getElementById('scrub'); e.value = t; e.dispatchEvent(new Event('input', {bubbles:true})); }", T_HOLD)
        r = s.ev(CAM_JS)
        assert not s.errs, s.errs
    finally:
        s.close()
    assert r["cam"]["s"] > 1.05, f"the eye stood still on a cold seek: {r}"
    dx, dy = r["cam"]["ox"] - r["datum"][0], r["cam"]["oy"] - r["datum"][1]
    assert math.hypot(dx, dy) < 1.5, f"the look {r['cam']} is not the datum {r['datum']}"


@needs_browser
def test_R26_373c_the_played_frame_is_the_sought_frame():
    """Played frame by frame into the hold and sought cold to the same instant: the same camera, to a tenth of a px."""
    tl, uris = _punch_tl()
    s = _Served(tl, uris)
    try:
        t = PUNCH_AT - 0.2
        while t < T_HOLD - 1e-9:
            s.page.evaluate("t => { const e = document.getElementById('scrub'); e.value = t; e.dispatchEvent(new Event('input', {bubbles:true})); }", round(t, 4))
            t += 1 / 24
        s.page.evaluate("t => { const e = document.getElementById('scrub'); e.value = t; e.dispatchEvent(new Event('input', {bubbles:true})); }", T_HOLD)
        played = s.ev(CAM_JS)
    finally:
        s.close()
    s = _Served(tl, uris)
    try:
        s.page.evaluate("t => { const e = document.getElementById('scrub'); e.value = t; e.dispatchEvent(new Event('input', {bubbles:true})); }", T_HOLD)
        sought = s.ev(CAM_JS)
    finally:
        s.close()
    assert played["tf"] == sought["tf"], (played["tf"], sought["tf"])


# ---- R26-106 (b): the chart's own series under kinetics.stroke_width --------------------------------------------------
STROKE_MJS = ROOT / "content/video_engine/scripts/kinetics/stroke.mjs"


def _node(src: str):
    import subprocess
    r = subprocess.run(["node", "--input-type=module", "-e", src], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_R26_106b_the_chart_brush_keeps_every_datum_as_a_vertex():
    """kinetics/stroke.mjs strokeWidthsPoly: the equal-arclength samples carry the width profile but cut a corner at the
    sample pitch - a datum's peak would be drawn short of its value. The chart's outline walks the samples AND every
    vertex, merged by arclength, each vertex exactly where its datum is; the tip at the drawn length on the polyline; the
    widths prof.w about its mean (the whole stroke keeps the authored weight)."""
    got = _node(f"""const S = await import({json.dumps(STROKE_MJS.as_uri())});
      const V = [{{x: 0, y: 100}}, {{x: 37, y: 20}}, {{x: 61, y: 90}}, {{x: 140, y: 85}}, {{x: 171, y: 5}}, {{x: 260, y: 60}}];
      let len = 0; const cum = [0]; for (let i = 1; i < V.length; i++) {{ len += Math.hypot(V[i].x - V[i-1].x, V[i].y - V[i-1].y); cum.push(len); }}
      const at = (s) => {{ let i = 1; while (i < V.length - 1 && cum[i] < s) i++; const u = (s - cum[i-1]) / (cum[i] - cum[i-1]);
        return {{ x: V[i-1].x + u * (V[i].x - V[i-1].x), y: V[i-1].y + u * (V[i].y - V[i-1].y) }}; }};
      const n = 40, pts = []; for (let i = 0; i < n; i++) pts.push(at(len * i / (n - 1)));
      const prof = S.strokeProfile(pts), part = S.strokeWidthsPoly(prof, pts, len, V, cum[4] + 10, 4), all = S.strokeWidthsPoly(prof, pts, len, V, len, 4);
      console.log(JSON.stringify({{ len, cum, part, all, tip: at(cum[4] + 10) }}));""")
    part, all_, cum = got["part"], got["all"], got["cum"]
    has = lambda w, v: any(abs(p["x"] - v[0]) < 1e-9 and abs(p["y"] - v[1]) < 1e-9 for p in w["pts"])
    V = [(0, 100), (37, 20), (61, 90), (140, 85), (171, 5), (260, 60)]
    assert all(has(part, v) for v in V[:5]) and not has(part, V[5]), "every drawn datum is a vertex of the outline, none undrawn"
    assert all(has(all_, v) for v in V), all_["pts"][-3:]
    tip = part["pts"][-1]
    assert abs(tip["x"] - got["tip"]["x"]) < 1e-9 and abs(tip["y"] - got["tip"]["y"]) < 1e-9 and abs(part["s"] - (cum[4] + 10)) < 1e-9
    assert len(part["hw"]) == len(part["pts"]) and max(all_["hw"]) > min(all_["hw"]) * 1.02, "the width is a profile"
    ss = [0.0]
    for a, b in zip(all_["pts"], all_["pts"][1:]):
        ss.append(ss[-1] + math.hypot(b["x"] - a["x"], b["y"] - a["y"]))
    mean = sum((ss[i] - ss[i - 1]) * (all_["hw"][i - 1] + all_["hw"][i]) for i in range(1, len(ss))) / ss[-1]
    assert abs(mean - 4.0) < 0.12, f"the whole stroke keeps about its authored weight: mean width {mean:.3f}"


BRUSH_JS = r"""() => {
  const w = [wA, wB].filter(e => e.__lp && e.classList.contains('ledger')).pop(), lp = w.__lp;
  const S = lp.states ? lp.states[lp.active | 0] : lp;
  return (S.paths || []).map(pp => { const p = pp.p, b = p.nextElementSibling && p.nextElementSibling.classList.contains('lp-brush') ? p.nextElementSibling : null;
    const len = p.getTotalLength(), off = parseFloat(p.getAttribute('stroke-dashoffset')) || 0, cs = getComputedStyle(p);
    const nums = (p.getAttribute('d').match(/-?\d+(\.\d+)?/g) || []).map(Number), verts = [];
    for (let i = 0; i + 1 < nums.length; i += 2) verts.push([nums[i], nums[i + 1]]);
    let s = 0; const inFill = []; for (let i = 0; i < verts.length; i++) { if (i) s += Math.hypot(verts[i][0] - verts[i-1][0], verts[i][1] - verts[i-1][1]);
      if (b && s < len - off - 1) inFill.push(b.isPointInFill(new DOMPoint(verts[i][0], verts[i][1]))); }
    return { si: pp.si, muted: !!pp.muted, len, off, vis: cs.visibility, stroke: cs.stroke, sw: parseFloat(cs.strokeWidth),
             brush: b ? { fill: b.style.fill, stroke: b.style.stroke, drawn: +b.dataset.drawn, wmin: +b.dataset.wMin, wmax: +b.dataset.wMax,
                          op: b.style.opacity, pop: p.style.opacity, filter: b.style.filter === p.style.filter, inFill } : null,
             nBrush: document.querySelectorAll('path.lp-brush').length };
  });
}"""


def _page_brush(t: float, kinetics: dict | None) -> list[dict]:
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface("ledger-page-mid-build")
    if kinetics is not None:
        tl = dict(tl, kinetics=kinetics)
    s = _Served(tl, uris, aspect)
    try:
        s.seek(t)
        got = s.ev(BRUSH_JS)
        assert not s.errs, s.errs
    finally:
        s.close()
    return got


@needs_browser
@pytest.mark.parametrize("flags", [{"stroke_width": True}, {"stroke_width": True, "curvature_stroke": True}])
def test_R26_106b_under_the_flag_the_page_series_draw_as_the_brush(flags):
    """ledger-page-mid-build at its golden instant (5.6, the lines mid-draw) and landed (12.0): every series is a filled
    outline in its own ink (`path.lp-brush`, the sibling right after it), its centreline hidden, drawn exactly as far as
    the dash says, its width a profile, every drawn datum inside the ink, and it wears the line's bloom."""
    for t in (5.6, 12.0):
        got = _page_brush(t, flags)
        assert got, t
        for r in got:
            b = r["brush"]
            assert b is not None, f"t {t}: series {r['si']} has no brush: {r}"
            assert r["vis"] == "hidden" and b["stroke"] == "none" and b["fill"] == r["stroke"], (t, r)
            assert b["drawn"] == pytest.approx(max(0.0, min(r["len"], r["len"] - r["off"])), abs=0.2), (t, r)
            assert b["op"] == r["brush"]["pop"] and b["filter"], (t, r)
            assert all(b["inFill"]), f"t {t}: a drawn datum outside the brush's ink: {r}"
        drawn = [r for r in got if r["brush"]["drawn"] > 40]
        assert drawn and all(r["brush"]["wmax"] > r["brush"]["wmin"] * 1.02 for r in drawn), (t, got)
        if t == 12.0:
            assert all(r["brush"]["drawn"] == pytest.approx(r["len"], abs=0.2) for r in got if r["brush"]["pop"] != "0"), got


@needs_browser
def test_R26_106b_flag_off_the_page_series_are_the_dash():
    """Control (holds at base): no brush, the centreline visible and drawn by its dash."""
    got = _page_brush(5.6, {"curvature_stroke": True})
    assert got and all(r["brush"] is None and r["vis"] == "visible" and r["nBrush"] == 0 for r in got), got


def test_R26_106b_one_flag_golden():
    import render_baseline as RB
    surface, flags, t = RB.FLAG_FRAMES["ledger-page-mid-build@stroke_width"]
    assert surface == "ledger-page-mid-build" and flags == {"curvature_stroke": True, "stroke_width": True} and t == 5.6
