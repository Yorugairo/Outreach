"""P71 T21 (was P69 T73) - FILLS TO A LEVEL: a spread against a reference rule keeps ONE SIDE of it.

The Bravos harvest v2's A46 ("fill below zero at a negative spike", D40 12:54), R29 ("the negative spike and its
glowing trough", D40 12:46-13:08) and A45 ("the underwater fill", BOOM 02:23.0 and 02:48.5, VERIFY.md): the region
between a line and a LEVEL, filled only where the line is on the named side of it - the dip below zero, the stretch
under a prior peak. The spread already takes a reference rule as its second edge (`to_rule`, the fifth watch); what it
could not do is keep one side: a rule edge filled the whole gap, above the rule and below it alike.

  side    `side: "below" | "above"` on a `to_rule` spread: the fill is clipped to where the series is strictly on that
          side of the rule - crossings interpolated, each excursion its own closed region along the rule - so its
          bounds are still the true series and the true rule. Refused by name when malformed, or on a spread between
          two series (there is no side to keep). Absent, the spread is the spread it was, to the byte.
  glow    the clip is GEOMETRIC, so P72 T49's spread glow (lpSpreadGlow: the halo cut to the fill's OUTSIDE) rings the
          clipped fill: the halo never lies inside it, and a clipped spread still blooms.
  peak    A45: `peak: true` - the rule IS the prior peak's level. The compiler reads the peak datum (`from_index`) and
          refuses a rule that is not its value at the rule's written precision (E28; level_join's `to: {y}` rule),
          WARNs when the datum is not the series' high to that point, and the fill ENDS where the series regains the
          level (the engine cuts there too).
  label   a peak spread's `label` carries `{years}` or `{months}`: the compiler COMPUTES the time under water - the
          peak datum to the first datum back at the level, or to the last datum with a "+" when it never is - on a
          dated x axis, and writes it as `text`. A duration is never typed: a digit outside the placeholder is refused.

The pages are committed objects read in place: the fed liquidity project's reserves change since June 2022 (a DERIVED
series that crosses zero; the A46 reference beat - no H row carries a signed series), Steel and Paper's railway index
(A45: the October 1845 peak, never regained in the record) and the memory monitor (H row 22's "one soft month in June":
May's print is the prior high, June dips under it, July regains it).
"""
from __future__ import annotations

import io
import json
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
FED_PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
SNP_PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
FED_PLATE = "ledger:fed-assets-reserves-history:line;idle=live;domain=-0.5,0.3"
RAIL_PLATE = "ledger:ev-railway-index-v1:line:139:right;idle=live"
MEM_PLATE = "ledger:ev-memory-monitor-v1:line:42:right;idle=live"
ASSETS, RESERVES = 0, 1          # fed-assets-reserves-history's two series
RAIL_PEAK, MEM_MAY = 53, 40      # the railway's October 1845 high; the memory monitor's May '26 print
SPREAD_AT, SPREAD_DUR, REST = 4.0, 2.0, 8.0
CARDS = ROOT / "content/video_engine/effects/cards/page_species.json"
RECIPE = ROOT / "content/video_engine/effects/recipes/the-glowing-trough.json"


def _v(sp: dict, plate: str = RAIL_PLATE) -> list[str]:
    return B.validate_species([dict(sp)], (0, 0, 0), plate)


RULE = {"kind": "spread", "at": 1.0, "dur": 1.0, "from": 0, "to_rule": 0}
PEAK = dict(RULE, side="below", peak=True, from_index=RAIL_PEAK, to_rule=1)


# ---- the grammar: every key the slice adds is refused BY NAME when malformed or misplaced -------------------------


def test_a_side_on_a_rule_edged_spread_is_accepted():
    assert _v(dict(RULE, side="below")) == []
    assert _v(dict(RULE, side="above")) == []


def test_a_side_that_is_not_below_or_above_is_refused_by_name():
    errs = _v(dict(RULE, side="sideways"))
    assert any("side" in e and "below|above" in e for e in errs), errs


def test_a_side_between_two_series_is_refused_by_name():
    errs = _v({"kind": "spread", "at": 1.0, "dur": 1.0, "from": 0, "to": 1, "side": "below"})
    assert any("side" in e and "to_rule" in e for e in errs), errs


def test_a_level_target_stays_refused_a_rule_carries_both_forms():
    """The plan's fallback `to: {level}` is not built: a zero hline + to_rule is A46, a rule at the peak is A45."""
    for to in ({"level": 53}, {"level": "zero"}):
        assert _v({"kind": "spread", "at": 1.0, "dur": 1.0, "from": 0, "to": to}), to


def test_peak_is_refused_by_name_unless_it_is_an_underwater_fill():
    assert _v(PEAK) == []
    for bad in (dict(PEAK, peak="yes"), dict(PEAK, side="above"), {k: v for k, v in PEAK.items() if k != "from_index"},
                {k: v for k, v in PEAK.items() if k != "side"}):
        errs = _v(bad)
        assert any(e.startswith("spread: peak") for e in errs), (bad, errs)


def test_a_label_is_a_peak_spreads_and_its_number_is_computed_never_typed():
    assert _v(dict(PEAK, label="{years} years under water")) == []
    assert _v(dict(PEAK, label="under water for {months} months")) == []
    for bad, why in ((dict(RULE, side="below", label="{years} years"), "only a peak"),
                     (dict(PEAK, label=""), "non-empty"),
                     (dict(PEAK, label="4 years under water"), "never typed"),
                     (dict(PEAK, label="{days} days"), "{years}"),
                     (dict(PEAK, label="{years} years, {months} months"), "one")):
        errs = _v(bad)
        assert any(e.startswith("spread: label") and why in e for e in errs), (bad, errs)


def test_text_is_the_compilers_and_refused_without_a_label():
    errs = _v(dict(PEAK, text="4+ years"))
    assert any(e.startswith("spread: text") for e in errs), errs
    assert _v(dict(PEAK, label="{years} years", text="4+ years")) == []   # re-validated after the compiler wrote it


# ---- the compiler's page check: the peak's level read from the datum, the duration computed ------------------------


def _world(plate: str, project: Path, rules: list[dict] | None = None) -> dict:
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(plate, (0, 0, 0), project)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    if rules is not None:
        world["page"].setdefault("axes", {})["hlines"] = rules
    return world


def _value(world: dict, si: int, i: int) -> float:
    return float(world["page"]["series"][si]["pts"][i][1])


def _rail(rule_y=None) -> tuple[dict, dict]:
    w = _world(RAIL_PLATE, SNP_PROJECT)
    peak = _value(w, 0, RAIL_PEAK) if rule_y is None else rule_y
    w["page"]["axes"]["hlines"] = [dict(w["page"]["axes"]["hline"]), {"y": peak}]
    return w, dict(PEAK)


def test_the_peak_rule_is_the_peak_datums_own_value_or_refused_with_its_numbers():
    w, sp = _rail()
    assert B.check_spread_levels(w, [sp]) == []
    w, sp = _rail(rule_y=2062)   # the object's DAILY high (its mark) - not the drawn datum, 2057.5
    with pytest.raises(ValueError, match=r"2057\.5"):
        B.check_spread_levels(w, [sp])


def test_a_labelled_peak_rule_is_warned_a45s_dont():
    w, sp = _rail()
    w["page"]["axes"]["hlines"][1]["label"] = "the 1845 peak"
    notes = B.check_spread_levels(w, [sp])
    assert any("A45's don't" in n and "C14" in n for n in notes), notes


def test_a_peak_that_is_not_the_series_high_to_that_point_is_warned_with_its_numbers():
    w = _world(RAIL_PLATE, SNP_PROJECT)
    i = 60   # after the October 1845 high: the fall is under way
    w["page"]["axes"]["hlines"] = [dict(w["page"]["axes"]["hline"]), {"y": _value(w, 0, i)}]
    notes = B.check_spread_levels(w, [dict(PEAK, from_index=i)])
    assert any("not the series' high" in n and "2057.5" in n for n in notes), notes


def test_the_time_under_water_is_computed_to_the_last_datum_with_a_plus_when_never_regained():
    w, sp = _rail()
    sp["label"] = "{years} years under water"
    B.check_spread_levels(w, [sp])
    pts = w["page"]["series"][0]["pts"]
    dx = float(pts[-1][0]) - float(pts[RAIL_PEAK][0])   # 1845.749 -> 1850.209: 4.46 years, never regained
    assert int(dx) == 4 and sp["text"] == "4+ years under water", sp


def test_the_time_under_water_is_computed_to_the_regain_when_the_series_regains_the_level():
    w = _world(MEM_PLATE, SNP_PROJECT)
    w["page"].setdefault("axes", {})["hlines"] = [{"y": _value(w, 0, MEM_MAY)}]
    sp = dict(PEAK, from_index=MEM_MAY, to_rule=0, label="{months} months under water")
    assert B.check_spread_levels(w, [sp]) == []
    assert sp["text"] == "2 months under water", sp   # May (the high) -> June under it -> July back over it


def test_a_duration_on_an_undated_x_axis_is_refused():
    w, sp = _rail()
    w["page"]["axes"]["xticks"] = [[1845, "peak"], [1848, "fall"]]
    sp["label"] = "{years} years"
    with pytest.raises(ValueError, match="dated"):
        B.check_spread_levels(w, [sp])


def test_a_spread_without_the_new_keys_is_untouched_by_the_check():
    w, _sp = _rail()
    plain = dict(RULE, to_rule=1, side="below", from_index=RAIL_PEAK)
    before = json.dumps(plain, sort_keys=True)
    assert B.check_spread_levels(w, [plain, dict(RULE)]) == []
    assert json.dumps(plain, sort_keys=True) == before


def test_the_compile_chain_runs_the_check():
    """derive_rescale_states - the per-row page checks main() runs - resolves the label like check_level_join's truth."""
    w, sp = _rail()
    sp["label"] = "{years} years under water"
    B.derive_rescale_states(w, [sp], RAIL_PLATE, SNP_PROJECT)
    assert sp["text"] == "4+ years under water"


# ---- the engine: the clip, the regain, the label, the glow ----------------------------------------------------------


def _chromium_available() -> bool:
    try:
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = r"""(k) => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp, PF = st.perform || { spreads: [] }, sd = PF.spreads[0];
  const S = (st.states && st.states[st.active | 0]) || st;
  const lab = sd.lab ? { text: sd.lab.label.textContent, opacity: +sd.lab.label.getAttribute('opacity'),
    x: +sd.lab.label.getAttribute('x'), y: +sd.lab.label.getAttribute('y'),
    glyphs: [...sd.lab.label.querySelectorAll('tspan')].map(t => +t.getAttribute('opacity')) } : null;
  const pts = (S.linePts || st.linePts || [])[k] || [];
  return { d: sd.path.getAttribute('d') || '', alpha: +(sd.path.getAttribute('fill-opacity') || 0),
           filter: sd.path.style.filter || '', rules: (S.hlines || []).map(r => r.y), lab,
           pts: pts.map(p => [p[0], p[1]]), plotT: (S.plot || st.plot || {}).T };
}"""

# the screen points of a filled region: inside it (every neighbour 6 px round inside too), and the ring just outside
# it (4-12 px from the nearest inside point) - sampled on the path's own geometry, never on pixels; in the frame's own
# pixels (frame_png clips the page at the stage's rectangle)
REGIONS = r"""() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const p = world.__lp.perform.spreads[0].path, m = p.getScreenCTM().inverse(), svg = p.ownerSVGElement;
  const r = p.getBoundingClientRect(), inside = (x, y) => { const q = svg.createSVGPoint(); q.x = x; q.y = y;
    const u = q.matrixTransform(m); const d = svg.createSVGPoint(); d.x = u.x; d.y = u.y; return p.isPointInFill(d); };
  const sb = document.getElementById('stage').getBoundingClientRect(), ox = Math.round(sb.x), oy = Math.round(sb.y);   /* frame_png's clip */
  const deep = [], ring = [];
  for (let y = Math.floor(r.top) - 16; y <= r.bottom + 16; y += 2) for (let x = Math.floor(r.left) - 16; x <= r.right + 16; x += 2) {
    if (inside(x, y)) { if ([[6,0],[-6,0],[0,6],[0,-6],[4,4],[-4,-4],[4,-4],[-4,4]].every(([a, b]) => inside(x + a, y + b))) deep.push([x - ox, y - oy]); continue; }
    let near = 99; for (const [a, b] of [[4,0],[-4,0],[0,4],[0,-4],[8,0],[-8,0],[0,8],[0,-8],[12,0],[-12,0],[0,12],[0,-12]])
      if (inside(x + a, y + b)) near = Math.min(near, Math.abs(a) + Math.abs(b));
    if (near >= 4 && near <= 12 && !inside(x + 2, y) && !inside(x - 2, y) && !inside(x, y + 2) && !inside(x, y - 2)) ring.push([x - ox, y - oy]);
  }
  const q = svg.createSVGPoint(); q.x = 0; q.y = world.__lp.perform.spreads[0].lo[0][1];
  return { deep, ring, box: [r.left - ox, r.top - oy, r.right - ox, r.bottom - oy], ruleY: q.matrixTransform(p.getScreenCTM()).y - oy };
}"""


def _timeline(world: dict, species: list, title: str) -> tuple[dict, dict]:
    import build_golden_sources as G
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    return G._timeline(title, scenes, {}, "16:9"), G._base_uris()


def _fed(spread: dict | None = None) -> tuple[dict, dict]:
    """The reserves change since June 2022 against a zero rule; total assets held at nothing (its line is not the claim)."""
    w = _world(FED_PLATE, FED_PROJECT, [{"y": 0, "label": "no change since June 2022"}])
    d = lambda i, s: {"kind": "datum", "index": i, "series": s}  # noqa: E731
    species = [{"kind": "build_to", "at": 0.0, "dur": 0.4, "series": s, "target": d(0, s)} for s in (ASSETS, RESERVES)]
    species += [{"kind": "build_to", "at": 0.6, "dur": 2.4, "series": RESERVES, "target": d(158, RESERVES)}]
    species += [dict({"kind": "spread", "at": SPREAD_AT, "dur": SPREAD_DUR, "from": RESERVES, "to_rule": 0}, **(spread or {}))]
    assert not B.validate_species(species, (0, 0, 0), FED_PLATE), B.validate_species(species, (0, 0, 0), FED_PLATE)
    return _timeline(w, species, "probe: a fill to a level")


def _memory() -> tuple[dict, dict]:
    w = _world(MEM_PLATE, SNP_PROJECT)
    w["page"].setdefault("axes", {})["hlines"] = [{"y": _value(w, 0, MEM_MAY)}]
    species = [{"kind": "build_to", "at": 0.0, "dur": 0.4, "series": s, "target": {"kind": "datum", "index": 42}} for s in (0, 1, 2)]
    species += [dict(PEAK, at=SPREAD_AT, dur=SPREAD_DUR, from_index=MEM_MAY, to_rule=0, label="{months} months under water")]
    assert not B.validate_species(species, (0, 0, 0), MEM_PLATE)
    assert B.check_spread_levels(w, species) == []
    return _timeline(w, species, "probe: the soft month under water")


def _serve(tl: dict, uris: dict, *, level: float | None = None):
    import render_baseline as RB
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    text = RB.instantiate(tl, uris)
    if level is not None:   # P72 T49's dial, turned in this probe's copy only
        text, n = re.subn(r"(const LP_SPREAD_GLOW = Object\.freeze\(\{\s*LEVEL: )1,", r"\g<1>%g," % level, text)
        assert n == 1, "LP_SPREAD_GLOW.LEVEL"
    html.write_text(text, encoding="utf-8")
    page, errs, close = SP.open_served(html, 1920, 1080, cleanup=td.cleanup)

    def at(t: float, k: int = 0) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE, k)

    def png(t: float) -> bytes:
        return RB.frame_png(page, t, (1920, 1080))

    def regions(t: float) -> dict:
        at(t)
        return page.evaluate(REGIONS)

    return at, png, regions, errs, close


def _verts(d: str) -> list[tuple[float, float]]:
    return [(float(a), float(b)) for a, b in re.findall(r"[ML](-?[\d.]+) (-?[\d.]+)", d)]


@needs_browser
def test_a_spread_to_a_zero_rule_with_side_below_fills_only_the_dips():
    """THE CLIP (the RED): over a series that is above zero and then dips below it, the fill keeps the dips only - every
    vertex of its path on or below the rule, the fill not empty, and it reaches the series' true lows."""
    at, _png, _r, errs, close = _serve(*_fed({"side": "below"}))
    try:
        got = at(REST, RESERVES)
    finally:
        close()
    assert not errs, errs
    ry = got["rules"][0]
    vs = _verts(got["d"])
    assert vs and got["alpha"] > 0, got
    assert all(y >= ry - 0.06 for _x, y in vs), [v for v in vs if v[1] < ry - 0.06][:5]
    low = max(p[1] for p in got["pts"])   # the lowest the line goes (SVG y down)
    assert max(y for _x, y in vs) == pytest.approx(low, abs=0.06)
    assert got["d"].count("M") > 3, "each excursion below zero is its own closed region"


@needs_browser
def test_without_a_side_the_rule_edged_spread_fills_both_sides_as_it_did():
    at, _png, _r, errs, close = _serve(*_fed())
    try:
        got = at(REST, RESERVES)
    finally:
        close()
    assert not errs, errs
    ry = got["rules"][0]
    ys = [y for _x, y in _verts(got["d"])]
    assert min(ys) < ry - 5 and max(ys) > ry + 5 and got["d"].count("M") == 1, "the old fill: above and below the rule"


@needs_browser
def test_side_above_keeps_the_humps_over_the_rule():
    at, _png, _r, errs, close = _serve(*_fed({"side": "above"}))
    try:
        got = at(REST, RESERVES)
    finally:
        close()
    assert not errs, errs
    ry, vs = got["rules"][0], _verts(got["d"])
    assert vs and all(y <= ry + 0.06 for _x, y in vs)
    assert min(y for _x, y in vs) == pytest.approx(min(p[1] for p in got["pts"]), abs=0.06)


@needs_browser
def test_the_fill_begins_at_from_index_and_bleeds_left_to_right_on_its_word():
    at, _png, _r, errs, close = _serve(*_fed({"side": "below", "from_index": 148}))
    try:
        before, mid, rest = at(SPREAD_AT - 0.1, RESERVES), at(SPREAD_AT + 0.3 * SPREAD_DUR, RESERVES), at(REST, RESERVES)
    finally:
        close()
    assert not errs, errs
    assert before["alpha"] == 0 and before["filter"] == "", before
    x148 = rest["pts"][148][0]
    xs_rest, xs_mid = [x for x, _y in _verts(rest["d"])], [x for x, _y in _verts(mid["d"])]
    assert min(xs_rest) >= x148 - 0.06, "nothing is filled before the datum the argument starts at"
    assert max(xs_mid) < max(xs_rest), "mid-bleed the fill has not reached the end yet"


@needs_browser
def test_a_clipped_spread_still_blooms_and_its_halo_stays_outside_the_fill():
    """P72 T49's glow on the CLIPPED fill: the filter is on (it blooms); against the dial at 0 the pixels deep inside the
    fill are unchanged (the halo never lies inside it, the fill keeps its own ink), the ring just outside the fill is
    lit in its ink, and away from the fill - over the humps the clip took away - nothing glows."""
    tl, uris = _fed({"side": "below", "from_index": 70})   # from late 2023: over the 2024 hump above zero, then the dips
    at, png, regions, errs, close = _serve(tl, uris)
    try:
        on = at(REST, RESERVES)
        lit = np.asarray(Image.open(io.BytesIO(png(REST))).convert("RGB")).astype(int)
        reg = regions(REST)
    finally:
        close()
    at0, png0, _r0, errs0, close0 = _serve(tl, uris, level=0)
    try:
        off = at0(REST, RESERVES)
        dark = np.asarray(Image.open(io.BytesIO(png0(REST))).convert("RGB")).astype(int)
    finally:
        close0()
    assert not errs and not errs0, (errs, errs0)
    assert "#lpfill-" in on["filter"] and off["filter"] == "", (on["filter"], off["filter"])
    assert len(reg["deep"]) > 40 and len(reg["ring"]) > 40, (len(reg["deep"]), len(reg["ring"]))
    assert all(y > reg["ruleY"] for _x, y in reg["deep"]), "the glowing fill is the CLIPPED one: none of it over the rule"
    inside = np.array([np.abs(lit[y, x] - dark[y, x]).max() for x, y in reg["deep"]])
    ring = np.array([(lit[y, x] - dark[y, x]).sum() for x, y in reg["ring"]])
    assert np.median(inside) <= 1 and np.percentile(inside, 95) <= 3, (np.median(inside), np.percentile(inside, 95))
    assert np.median(ring) >= 6, ("the clipped fill blooms outside its edge", np.median(ring))
    x0, _y0, _x1, _y1 = reg["box"]
    far = np.abs(lit[:, : max(0, int(x0) - 140)] - dark[:, : max(0, int(x0) - 140)])
    assert far.max() <= 2, ("nothing glows where the clip took the fill away", far.max())


@needs_browser
def test_the_underwater_fill_ends_where_the_series_regains_the_peak_and_writes_its_time():
    at, _png, _r, errs, close = _serve(*_memory())
    try:
        before, rest = at(SPREAD_AT - 0.1), at(REST)
    finally:
        close()
    assert not errs, errs
    xs = [x for x, _y in _verts(rest["d"])]
    ry, pts = rest["rules"][0], rest["pts"]
    assert min(xs) == pytest.approx(pts[MEM_MAY][0], abs=0.06), "the fill begins at the peak"
    assert pts[MEM_MAY + 1][0] < max(xs) < pts[MEM_MAY + 2][0], "it ends where July crosses back over May's level"
    assert all(y >= ry - 0.06 for _x, y in _verts(rest["d"]))
    lab = rest["lab"]
    assert lab and lab["text"].replace(" ", " ") == "2 months under water", lab
    assert before["lab"]["opacity"] == 0 or max(before["lab"]["glyphs"]) == 0, before["lab"]
    assert min(lab["glyphs"]) == 1 and lab["opacity"] == 1, "written whole by the end of its word"
    assert lab["x"] == pytest.approx((min(xs) + max(xs)) / 2, abs=0.2), "centred over the fill it names (BOOM 02:49.5)"


@needs_browser
def test_a_regained_series_is_not_filled_again_after_the_regain():
    """The railway never regains its 1845 high, so its fill runs to the record's end; on the fed page a peak at the
    June-2022 start (0) is regained at the 2023 hump - nothing after it is under water, however far it falls later."""
    w = _world(FED_PLATE, FED_PROJECT, [{"y": 0.0}])
    species = [{"kind": "build_to", "at": 0.0, "dur": 0.4, "series": ASSETS, "target": {"kind": "datum", "index": 0, "series": ASSETS}},
               {"kind": "build_to", "at": 0.6, "dur": 2.4, "series": RESERVES, "target": {"kind": "datum", "index": 158, "series": RESERVES}},
               dict(PEAK, at=SPREAD_AT, dur=SPREAD_DUR, **{"from": RESERVES}, from_index=0, to_rule=0)]
    assert B.check_spread_levels(w, species) == []   # June 2022's zero is the high to that point: it is the start
    at, _png, _r, errs, close = _serve(*_timeline(w, species, "probe: regained"))
    try:
        got = at(REST, RESERVES)
    finally:
        close()
    assert not errs, errs
    first_up = next(i for i, p in enumerate(w["page"]["series"][RESERVES]["pts"]) if i > 0 and float(p[1]) >= 0)
    assert max(x for x, _y in _verts(got["d"])) <= got["pts"][first_up][0] + 0.06


SEEK_CASES = [("bleed", SPREAD_AT + SPREAD_DUR * 0.4), ("rest", REST)]


@needs_browser
@pytest.mark.parametrize("name,t", SEEK_CASES, ids=[c[0] for c in SEEK_CASES])
def test_a_cold_seek_and_a_played_frame_paint_the_same_clipped_fill(name, t):
    """The law: the clip, the regain cut and the label are a pure function of t - forward play into the instant
    writes the cold seek's path, alpha, filter and label."""
    tl, uris = _memory()
    at, _png, _r, errs, close = _serve(tl, uris)
    try:
        cold = at(t)
    finally:
        close()
    at, _png, _r, errs2, close = _serve(tl, uris)
    try:
        for x in [round(t - 1.0 + 0.1 * i, 2) for i in range(10)]:
            at(x)
        played = at(t)
    finally:
        close()
    assert not errs and not errs2, (errs, errs2)
    assert played == cold, name


# ---- the registries: the card, the recipe, the goldens -------------------------------------------------------------


def test_the_spread_card_names_the_side_and_the_underwater_fill():
    cards = json.loads(CARDS.read_text(encoding="utf-8"))
    card = next(c for c in (cards if isinstance(cards, list) else cards.get("cards", [])) if c.get("id") == "page_species:spread")
    text = json.dumps(card)
    assert "side" in text and "peak" in text and "{years}" in text, card.get("options") or card


def test_the_glowing_trough_recipe_is_a_candidate_with_its_use_when():
    rec = json.loads(RECIPE.read_text(encoding="utf-8"))
    assert rec["id"] == "recipe:the-glowing-trough" and rec.get("status") == "candidate", rec
    assert rec.get("use_when"), "the recipe carries BRAVOS-USE-WHEN's A46 / R29 entry"
    spread = [m for m in rec["members"] if m["card"] == "page_species:spread"]
    assert spread and spread[0]["options"].get("side") == "below", rec["members"]
    assert "golden" in rec["source"] or "projects/_proofs/" in rec["source"], rec["source"]


def test_the_two_goldens_are_registered():
    import build_golden_sources as G
    for name in ("fill-below-zero", "fill-underwater"):
        assert name in G.SURFACES and name in G.FRAME_T, name
    src = (ROOT / "content/video_engine/tests/test_golden_frames.py").read_text(encoding="utf-8")
    assert '"fill-below-zero"' in src and '"fill-underwater"' in src
