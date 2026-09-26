"""P72 T24 - THE MORPH: the soak's floor in seconds, M17 honest on a planted source, the strip beyond x-monotone,
and the morph's two untested goldens.

R26-153  `MORPH.GROUND` was a SHARE of the morph's seconds, so a 0.3 s `morph=` soaked its board in 0.225 s - its crisp
         rect in about two frames and its steepest frame carrying 0.22 of the board, the snap E99 s52 refused. The
         ground now has a floor in seconds, `MORPH.GROUND_MIN_S`, read by the page's own ground clock.
R26-163  M17's centroid / axis / area invariants are unreachable by construction for a PLANTED source (it stands where
         the element stood - R26-16 - never re-placed on the chart's box), so they are reported, not judged; det J > 0
         stays the one real invariant - and a strip FOLD (the tie's, min det -0.183: a tall, slanted silhouette read
         by vertical columns) is WARNed by name with its window: the parent's ruling keeps the tie's approved upright
         strip (its fold is invisible) - `arap.stripFor` turns the strip only for a bay.
R26-150  a C-shaped horseshoe keeps its bay (the strip runs the way the shape is one interval per column), and a
         shape that is one interval along no axis is REFUSED BY NAME (`refused: "bay"`, its columns and share) - the
         gate names it.
R26-148  `melt-morph-two-inks`: the ball hands its ring to an area in another series' ink - a golden, read here.
R26-152  `morph-planted-plates`: a planted morph page whose ground is the two-plate cross-fade - a golden, read here.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_golden_sources as GS  # noqa: E402
import gate_motion_density as G  # noqa: E402
import render_baseline as RB  # noqa: E402
import served_player as SPL  # noqa: E402

ARAP_MJS = ROOT / "content/video_engine/scripts/kinetics/arap.mjs"
ENGINE_SRC = RB.ENGINE.read_text(encoding="utf-8")
PLANTED = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-p61-planted"
NODE = "node.exe" if sys.platform == "win32" else "node"
# test_melt_morph's own E99 s52 metric and thresholds (section 8 there): ink coverage from the page's cream to the
# field's charcoal, normalised to the page's first frame (0) and the board once whole (1)
CREAM_L, INK_L, FRAME_S = 230.0, 47.0, 0.02
GROUND_STEP_MAX, GROUND_FIRST_MAX = 0.125, 0.05
SHORT_MORPH_S = 0.3   # the row's own example


def _node(src: str):
    out = subprocess.run([NODE, "--input-type=module", "-e", src], capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def _arap(body: str):
    return _node(f"import * as K from {json.dumps(ARAP_MJS.as_uri())};\n{body}\n")


def _chromium_available() -> bool:
    try:
        with SPL.browser():
            return True
    except Exception:
        return False


browser_only = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _morph_dials() -> str:
    m = re.search(r"const MORPH = \{(.*?)\};", ENGINE_SRC, re.S)
    assert m, "the engine has no MORPH dials"
    return m.group(1)


def _dial(name: str) -> float:
    d = re.search(rf"\b{re.escape(name)}:\s*([0-9.]+)", _morph_dials())
    assert d, f"MORPH has no dial {name}"
    return float(d.group(1))


# ---- 1. R26-153: THE SOAK'S FLOOR IN SECONDS ------------------------------------------------------------------------
def test_the_ground_has_a_floor_in_seconds_and_the_page_reads_it() -> None:
    assert _dial("GROUND_MIN_S") > 0, "the soak's own minimum is a dial in seconds"
    assert "Math.max(MORPH.GROUND_MIN_S, morphS * MORPH.GROUND)" in ENGINE_SRC, \
        "the morph page's ground clock takes the floor, not a share alone"
    assert _dial("S") * _dial("GROUND") >= _dial("GROUND_MIN_S"), \
        "the 2.0 s default keeps the window it had (every golden's)"


def _coverage(png: bytes) -> float:
    import io

    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(io.BytesIO(png)).convert("RGB"), dtype=np.float32)
    lum = 0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2]
    return float(np.clip((CREAM_L - lum) / (CREAM_L - INK_L), 0.0, 1.0).mean())


def _ground_fill(surface: str, morph_s: float | None, span: float) -> list[tuple[float, float]]:
    """(seconds from the cut, the board's fill share) at the scrub's own step over `span`."""
    tl, uris, _t, aspect = RB.load_surface(surface)
    tl = json.loads(json.dumps(tl))
    page = next(s for s in tl["scenes"] if ((s["world"].get("page") or {}).get("enter") == "morph"))
    cut = float(page["span"][0])
    if morph_s is not None:
        page["world"]["page"]["morph_s"] = morph_s
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "short-morph.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SPL.served(html, w, h) as (pg, _errs):
            rows = [(round(i * FRAME_S, 4), _coverage(RB.frame_png(pg, cut + i * FRAME_S, (w, h))))
                    for i in range(int(round(span / FRAME_S)) + 1)]
    base, full = rows[0][1], max(c for _t, c in rows)
    assert full - base > 0.3, f"the board never filled: base {base:.4f} full {full:.4f}"
    return [(t, (c - base) / (full - base)) for t, c in rows]


@browser_only
def test_a_short_morph_soaks_for_the_floor_and_never_snaps() -> None:
    """A 0.3 s planted morph: the page's first frame is not the board, no frame delivers more than an eighth of it
    (test_melt_morph's E99 s52 thresholds), and the board is whole only once most of the floor has run - never at
    0.2 s, where the share alone put it. (The soak's stains cover the board by ~0.8 of their window - measured 0.50 s
    of 0.6 - and the crisp rect finishes it; before the floor: whole at 0.20 s, the steepest frame 0.22 of the board.)"""
    floor = _dial("GROUND_MIN_S")
    fill = _ground_fill("morph-planted", SHORT_MORPH_S, floor + 0.4)
    assert fill[1][1] <= GROUND_FIRST_MAX, f"the board is {fill[1][1]:.3f} filled on the page's first frame"
    steps = [(fill[i][0], fill[i][1] - fill[i - 1][1]) for i in range(1, len(fill))]
    worst_t, worst = max(steps, key=lambda r: abs(r[1]))
    assert abs(worst) <= GROUND_STEP_MAX, f"the board's fill jumped {worst:+.3f} at +{worst_t:.2f} s (max {GROUND_STEP_MAX})"
    whole = next(t for t, f in fill if f > 0.98)
    assert whole >= 0.75 * floor, f"the board is whole at +{whole:.2f} s - under the {floor} s floor"


# ---- 2. R26-163: M17 ON A PLANTED SOURCE ------------------------------------------------------------------------------
TIE_POLY = [[0.345, 0.417], [0.36, 0.42], [0.36, 0.46], [0.35, 0.46]]


def _page_scene(morph=None, exit_: str = "cut") -> dict:
    world = {"kind": "ledger", "page": {"surface": "ledger", "enter": "morph"}}
    if morph is not None:
        world["morph"] = morph
    return {"scene_id": "s02", "span": [11.79, 18.9], "world": world, "exit": exit_, "species": [], "docks": []}


def _reading(**over) -> dict:
    r = {"centroid_shift": 0.2754, "centroid_ok": False, "axis_deg": 40.74, "axis_ok": False, "area_ratio": 0.011,
         "area_ok": False, "end_error": 0, "min_det": 1.0, "n": 96, "u": 0.5, "method": "arap"}
    r.update(over)
    return {"scenes": {"s02": r}}


def test_m17_on_a_planted_source_judges_only_det() -> None:
    g = G._morph_gate([_page_scene({"poly": TIE_POLY})], _reading())
    assert g.level == "PASS", g.message
    assert "planted" in g.message and "min det 1.000" in g.message
    assert "FAILS" not in g.message
    assert "not judged" in g.message, "the three are REPORTED with their numbers, and said to be unjudged"


def test_m17_on_a_planted_source_still_fails_a_fold_and_names_only_that() -> None:
    g = G._morph_gate([_page_scene({"poly": TIE_POLY})], _reading(min_det=-0.183))
    assert g.level == "WARN", g.message
    fails = g.message.split(" - FAILS ", 1)[1].split(" - ", 1)[0]
    assert fails == "det J <= 0", f"only the fold is failed: {fails!r}"
    assert "move the prop onto the chart's box" not in g.message, "a planted prop is never told to move where it stood"


def test_m17_reads_a_handed_or_planted_source_off_the_measurement() -> None:
    """The melt's ball is handed at run time (the timeline carries no world.morph), so the measurement names it."""
    g = G._morph_gate([_page_scene(None, "melt:morph")], _reading(source="handed"))
    assert g.level == "PASS", g.message
    assert "handed" in g.message


def test_m17_on_a_named_prop_is_judged_as_it_always_was() -> None:
    g = G._morph_gate([_page_scene("tab")], _reading(source="named"))
    assert g.level == "WARN" and "FAILS centroid, axis, area" in g.message, g.message
    g = G._morph_gate([_page_scene()], _reading())
    assert g.level == "WARN" and "FAILS centroid, axis, area" in g.message, g.message


def test_m17_names_the_bay_a_planted_strip_fills() -> None:
    strip = {"axis_deg": 0.0, "bays": [{"from": 0, "to": 47, "share": 0.5231}], "refused": "bay", "tried": []}
    g = G._morph_gate([_page_scene({"poly": TIE_POLY})], _reading(source="planted", strip=strip))
    assert g.level == "WARN", g.message
    assert "fills a bay" in g.message and "columns 0-47" in g.message and "52 %" in g.message


# ---- 3. R26-163 + R26-150: WHICH WAY THE STRIP RUNS --------------------------------------------------------------------
HORSESHOE = [[400, 200], [500, 200], [500, 235], [430, 235], [430, 285], [500, 285], [500, 320], [400, 320]]   # opens right
S_SHAPE = [[400, 200], [500, 200], [500, 260], [420, 260], [420, 280], [500, 280], [500, 340], [400, 340], [400, 320],
           [480, 320], [480, 300], [400, 300], [400, 240], [480, 240], [480, 220], [400, 220]]
TARGET_JS = """const n = 48, xs = [...Array(n).keys()].map((i) => 100 + (i / (n - 1)) * 800);
const T = [...xs.map((x, i) => [x, 400 - 120 * Math.sin(i / 6) - i]), ...xs.map((x) => [x, 500])];
const inside = (pt, poly) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const a = poly[i], b = poly[j];
  if ((a[1] > pt[1]) !== (b[1] > pt[1]) && pt[0] < (b[0] - a[0]) * (pt[1] - a[1]) / (b[1] - a[1]) + a[0]) c = !c; } return c; };"""


def test_the_x_strip_names_the_horseshoes_bay() -> None:
    r = _arap(f"const S = K.polyStrip({json.dumps(HORSESHOE)}, 48); console.log(JSON.stringify({{bays: S.bays, axis: S.axis}}));")
    assert r["axis"] == 0
    assert len(r["bays"]) == 1 and r["bays"][0]["from"] > 0 and r["bays"][0]["to"] == 47 and r["bays"][0]["share"] > 0.3


def test_a_horseshoe_keeps_its_bay_and_never_inverts() -> None:
    r = _arap(TARGET_JS + f"""
const P = {json.dumps(HORSESHOE)}, S = K.stripFor(P, T, n, n + (n >> 1)), out = K.stripOutline([...S.top, ...S.bot], n);
console.log(JSON.stringify({{axis: S.axis, det: S.det, refused: S.refused, bays: S.bays,
  bay: inside([465, 260], out), arm: inside([465, 215], out), arm2: inside([465, 305], out), back: inside([415, 260], out)}}));""")
    assert r["refused"] is None and r["bays"] == []
    assert r["det"] > 0, "the strip that keeps the bay never inverts on the area under a series"
    assert not r["bay"], "the bay stays open: its centre is outside the strip"
    assert r["arm"] and r["arm2"] and r["back"], "and both arms and the back are carried"
    assert abs(abs(r["axis"]) - 1.5707963) < 1e-6, "its columns run across the opening"


def test_a_shape_one_interval_along_no_axis_is_refused_by_name() -> None:
    r = _arap(TARGET_JS + f"""
const S = K.stripFor({json.dumps(S_SHAPE)}, T, n, n + (n >> 1));
console.log(JSON.stringify({{refused: S.refused, bays: S.bays, det: S.det, tried: S.tried.length}}));""")
    assert r["refused"] == "bay", r
    assert r["bays"] and r["bays"][0]["share"] > 0.05, "the columns it fills are named with the share"
    assert r["det"] > 0, "a refused strip is still one that does not fold"
    assert r["tried"] > 3, "every axis was read before the refusal"


def test_every_sound_x_strip_is_the_strip_it_always_was() -> None:
    """The ball and the lobed blob (the goldens' own sources) keep the x strip, vertex for vertex."""
    r = _arap(TARGET_JS + """
const circle = [...Array(96).keys()].map((i) => { const t = i / 96 * Math.PI * 2; return [500 + 80 * Math.cos(t), 300 + 80 * Math.sin(t)]; });
const lobed = [...Array(120).keys()].map((i) => { const t = i / 120 * Math.PI * 2, R = 80 * (1 + 0.22 * Math.cos(3 * t + 0.6) + 0.12 * Math.sin(5 * t - 0.3));
  return [500 + R * Math.cos(t), 300 + R * Math.sin(t)]; });
const same = (p) => { const a = K.stripFor(p, T, n, n + (n >> 1)), b = K.polyStrip(p, n);
  return a.axis === 0 && a.refused === null && JSON.stringify([a.top, a.bot]) === JSON.stringify([b.top, b.bot]); };
console.log(JSON.stringify({ circle: same(circle), lobed: same(lobed) }));""")
    assert r == {"circle": True, "lobed": True}


def test_a_turned_strip_keeps_every_triangles_winding() -> None:
    r = _arap(f"""
const P = {json.dumps(HORSESHOE)}, S = K.polyStrip(P, 48, {{ axis: Math.PI / 3 }}), M = K.stripMesh(S.top, S.bot);
const sgn = M.tris.map(([i, j, k]) => {{ const a = M.verts[i], b = M.verts[j], c = M.verts[k];
  return Math.sign((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])); }});
const X = K.stripMesh(K.polyStrip(P, 48).top, K.polyStrip(P, 48).bot);
const sx = Math.sign((X.verts[X.tris[0][1]][0] - X.verts[X.tris[0][0]][0]) * (X.verts[X.tris[0][2]][1] - X.verts[X.tris[0][0]][1]) -
  (X.verts[X.tris[0][1]][1] - X.verts[X.tris[0][0]][1]) * (X.verts[X.tris[0][2]][0] - X.verts[X.tris[0][0]][0]));
console.log(JSON.stringify({{ all: [...new Set(sgn)], x: sx }}));""")
    assert r["all"] == [r["x"]], "a proper rotation: one winding, the x strip's"


@browser_only
def test_the_tie_keeps_its_upright_strip_and_m17_names_the_fold() -> None:
    """The real beat (P61 T3d), measured in the player as measure_morph.py does. The parent's ruling: the tie was
    approved growing upright (E99 s62) and its fold is invisible, so the x strip STANDS (a turn would be a visible change
    to an approved motion for an invisible fault) and M17 WARNs the fold BY NAME - its min det, triangle, column and
    window - with the planted advice, never "move the prop"; the three planted invariants are reported, unjudged."""
    tl = json.loads((PLANTED / "tokyo-planted.timeline.json").read_text(encoding="utf-8"))
    sc = next(s for s in tl["scenes"] if (s.get("world") or {}).get("kind") == "ledger")
    w, h = RB.STAGE[tl.get("aspect") or "16:9"]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "tie.html"
        html.write_text(RB.instantiate(tl, {}), encoding="utf-8")   # the plate is scene 1's; the morph reads the page alone
        with SPL.served(html, w, h) as (page, errs):
            RB.frame_png(page, float(sc["span"][0]) + 1.0, (w, h))   # measure_morph.py's own instant: MORPH.S / 2
            inv = page.evaluate("() => window.__morphInvariants()")
    assert errs == [], errs
    assert inv["source"] == "planted"
    strip = inv["strip"]
    assert strip["axis_deg"] == 0 and strip["refused"] == "fold" and strip["bays"] == [], strip
    fold = strip["fold"]
    assert fold["min_det"] < 0 and abs(fold["min_det"] - inv["min_det"]) < 0.01, (fold, inv["min_det"])
    assert fold["column"] == fold["triangle"] >> 1 and 0 < fold["u0"] <= fold["u1"] < 1, fold
    g = G._morph_gate(tl["scenes"], {"scenes": {sc["scene_id"]: inv}})
    assert g.level == "WARN", g.message
    fails = g.message.split(" - FAILS ", 1)[1].split(" - ", 1)[0]
    assert fails == "det J <= 0", f"only the fold is failed: {fails!r}"
    assert f"a strip fold on the planted source: triangle {fold['triangle']} (strip column {fold['column']})" in g.message
    assert "of the morph (" in g.message and " s)" in g.message, "the window, in the morph's u and in seconds"
    assert "move the prop onto the chart's box" not in g.message and "never moved to pass" in g.message


def test_m17_names_a_strip_fold_with_its_window_in_seconds() -> None:
    fold = {"min_det": -0.183, "triangle": 6, "column": 3, "worst_t": 0.3333, "t0": 0.2083, "t1": 0.4167, "u0": 0.36, "u1": 0.49}
    scene = _page_scene({"poly": TIE_POLY})
    g = G._morph_gate([scene], _reading(min_det=-0.183, source="planted",
                                        strip={"axis_deg": 0, "bays": [], "refused": "fold", "tried": [], "fold": fold}))
    assert g.level == "WARN", g.message
    assert "triangle 6 (strip column 3), min det -0.183, over u 0.36-0.49 of the morph" in g.message
    assert "12.51-12.77 s" in g.message   # 11.79 + u x MORPH_S 2.0


# ---- 4. R26-148 + R26-152: THE TWO GOLDENS, READ ------------------------------------------------------------------------
@pytest.mark.parametrize("name", ["melt-morph-two-inks", "morph-planted-plates"])
def test_the_two_morph_goldens_are_on_disk_and_registered(name: str) -> None:
    import test_golden_frames as TGF
    assert name in GS.SURFACES and name in GS.FRAME_T
    assert name in TGF.SURFACES, "the golden frame test pins it"
    for suffix in ("timeline", "uris"):
        p = ROOT / f"content/video_engine/tests/golden/sources/{name}.{suffix}.json"
        assert p.exists() and b"\r" not in p.read_bytes(), f"{p.name}: committed, LF"
    assert (ROOT / f"content/video_engine/tests/golden/frames/{name}.png").exists()


def test_the_two_inks_golden_hands_the_ball_to_another_series() -> None:
    tl, _uris, _t, _a = RB.load_surface("melt-morph-two-inks")
    s1, s2 = tl["scenes"]
    assert s2["exit"].startswith("melt:") and s2["world"]["page"]["enter"] == "morph"
    si = s2["world"]["morph_series"]
    assert s2["world"]["page"]["series"][si]["color"] != s1["world"]["page"]["series"][0]["color"]


PROBE_MORPH = """() => { const w = [...document.querySelectorAll('.world')].find((e) => e.__lp && e.__lp.morph);
  const M = w && w.__lp.morph; if (!M) return null;
  return { fill: M.path.getAttribute('fill'), fop: +M.path.getAttribute('fill-opacity'), u: M.u,
           plate: w.__lp.fieldPlate ? +w.__lp.fieldPlate.style.opacity : null,
           lines: (w.__lp.paths || []).map((pp) => ({ si: pp.si, muted: !!pp.muted, stroke: pp.p ? pp.p.getAttribute('stroke') : null })) }; }"""


def _probe_at(surface: str, ts: list[float]) -> list[dict]:
    tl, uris, _t, aspect = RB.load_surface(surface)
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / f"{surface}.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SPL.served(html, w, h) as (page, _errs):
            out = []
            for t in ts:
                RB.frame_png(page, t, (w, h))
                out.append(page.evaluate(PROBE_MORPH))
    return out


@browser_only
def test_the_two_inks_area_wears_the_incoming_series_ink_through_the_hand() -> None:
    tl, _uris, t, _a = RB.load_surface("melt-morph-two-inks")
    si = tl["scenes"][1]["world"]["morph_series"]
    mid, = _probe_at("melt-morph-two-inks", [t])
    assert mid and 0 < mid["u"] < 1, mid
    ink = next(ln["stroke"] for ln in mid["lines"] if ln["si"] == si and not ln["muted"])
    first = next(ln["stroke"] for ln in mid["lines"] if ln["si"] == 0)
    assert mid["fill"] == ink != first, f"the area wears series {si}'s own line ink ({ink}), not series 0's ({first}): {mid}"
    assert mid["fop"] > 0, "and it is already carrying the shape half way through the hand"


@browser_only
def test_the_plates_ground_cross_fades_under_the_planted_morph() -> None:
    """R26-152: the inked plate arrives OVER the cream on the morph's own ground clock - rising, never falling, whole
    when the ground's window closes, and the morph carrying the planted prop the whole time."""
    cut, ground = GS.MORPH_CUT, _dial("S") * _dial("GROUND")
    ts = [cut + 0.02, cut + 0.15, cut + 0.5, cut + ground, cut + ground + 0.3]
    rows = _probe_at("morph-planted-plates", ts)
    ops = [r["plate"] for r in rows]
    assert all(o is not None for o in ops), "the page carries the field plate"
    assert all(b >= a for a, b in zip(ops, ops[1:])), f"the cross-fade never falls: {ops}"
    assert 0 < ops[0] < 0.2 and 0.3 < ops[1] < 0.7 and ops[3] > 0.99, f"it ARRIVES over the ground's window: {ops}"
    assert all(0 < r["u"] for r in rows[:3]), "the morph runs under it"
