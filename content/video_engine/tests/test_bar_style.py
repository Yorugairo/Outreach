"""P69 T10b - A BAR WITH ROUNDED SHOULDERS AND A HATCHED SHADOW, as a row option (`;bar_style=soft`).

The operator (2026-09-22), on the T6 frames: "that bar can't be that wide ... it reads like a giant block" (the cap,
T6 / T6c) and "I think it should also have some sort of rounded edges, maybe shadows". AMENDED the same day: the
bar's shadow is the SAME cross-hatch as the prop's (T6b v2, E99 s92), cast from the ONE stage light (DROP -125), so
props, cards and bars share one light and one texture. Under the option, measured on the served player:

  (1) THE SHOULDERS   every bar's two corners AWAY from zero are rounded at LPBAR_SOFT.SHOULDER_PX on the stage; the
                      two ON zero stay square, so a bar still stands on its baseline (a negative bar rounds its
                      bottom) - read on the rendered pixels at both ends of the bar.
  (2) THE SHADOW      a hatch layer UNDER the bars, cut to each bar's own silhouette thrown PROP_SHADOW.OFFSET_PX along
                      LIGHT_DEG + 180, drawn by the prop's own painter (`propHatchLines`) at the prop's own dials -
                      the same pitch, line width, crossing, ink and alpha, read back off the layer and compared with
                      stopaction.mjs's PROP_SHADOW. It never falls past zero (E28: the sign is geometry), it follows
                      the bar as it grows, it READS (the strip beside the bar is darker than the bare panel), and a
                      seek lands the same silhouettes whatever the order.
  (3) CLEARANCES      the value label, the figure, the category name and every rule's label keep clear of the
                      shadow's visible strip, and a number written inside its bar stays inside the rounded shape.
  (4) COMPOSES        with `;readability=longform` (the panel stays; the bars take the shoulders and the shadow on it).
  (5) OFF             without the option the world each row compiles is the one pinned before this slice, and a bar
                      is the builder's rect as it was (rx 6, no foot, no hatch layer).

Fixtures: the three H bars beats `test_compare_on_bars` already carries (the 94, the halving, the 1 vs 3) and the
longform suite's synthetic zero-crossing row (a negative bar). The browser half needs playwright + chromium.
"""
from __future__ import annotations

import copy
import io
import json
import math
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

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402
from test_compare_on_bars import FIXTURES, LAND_T, OBJ_94  # noqa: E402
from test_longform_profile import CROSS, LINE, WORLD_PINS  # noqa: E402

ASPECT = "16:9"
SOFT = ";bar_style=soft"
LONG = ";readability=longform:middle"
STOPACTION = ROOT / "content/video_engine/scripts/kinetics/stopaction.mjs"
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
T_GROW = 5.0          # mid-build: the bars grow 4.4-7.4 s on a page entered at 0 (test_compare_on_bars' own clock)
GEOM_TOL = 1.5        # stage px: a silhouette is its bar thrown along the light to within the page's idle and rounding
DARKEN_MIN = 8.0      # levels of mean luminance (0-255): the shadow's strip against the bare panel beside it - the
                      # prop's own floor on the charcoal page (test_prop_shadow.DARKEN_MIN["page"]); measured 11.0-14.3

# name -> (object id, object, species): the three H beats and a zero-crossing SHAPE (never a figure about the world)
PAGES = {name: (oid, obj, species) for name, (oid, obj, species, _bar) in FIXTURES.items()}
PAGES["cross"] = ("fx-soft-cross", CROSS, [])
PAGES["line"] = ("fx-soft-line", LINE, [])


def _node(src: str):
    r = subprocess.run(["node", "--input-type=module", "-e", src], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@pytest.fixture(scope="module")
def prop_shadow() -> dict:
    return _node(f"""const s = await import({json.dumps(STOPACTION.as_uri())});
      console.log(JSON.stringify(s.PROP_SHADOW));""")


def _world(name: str, tmp: Path, opt: str = "", aspect: str = ASPECT) -> tuple[dict, list[dict]]:
    oid, obj, species = PAGES[name]
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    variant = "line" if name == "line" else "bars"
    saved = B.ASPECT
    B.ASPECT = aspect
    try:
        world = B.world_for_plate(f"ledger:{oid}:{variant}{opt}", (0, 0, 0), tmp)
        if aspect == "16:9":
            B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world, copy.deepcopy(species)


def _sha(world: dict) -> str:
    import hashlib
    return hashlib.sha256(json.dumps(world, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


# ---- the row (no browser) -----------------------------------------------------------------------------------------

def test_soft_is_a_named_row_option_on_a_bars_page(tmp_path):
    world, _ = _world("row17-94", tmp_path, SOFT)
    assert world["page"]["builder"] == "story"
    assert world["page"]["bar_style"] == "soft"
    assert LPG.BAR_STYLES == ("soft",)
    assert "bar_style" not in json.loads((tmp_path / "evidence/objects/fx-capex-ocf-94-bars.series.json").read_text(encoding="utf-8"))


def test_an_unknown_style_another_builder_and_the_prism_are_refused_by_name(tmp_path):
    with pytest.raises(ValueError, match=r"bar_style 'round' is not one of soft"):
        _world("row17-94", tmp_path / "a", ";bar_style=round")
    with pytest.raises(ValueError, match=r"bar_style=soft.*'dense-line'"):
        _world("line", tmp_path / "b", SOFT)
    with pytest.raises(ValueError, match=r"bar_style=soft.*extruded_bar"):
        _world("row17-94", tmp_path / "c", ";form=extruded_bar" + SOFT)


def test_soft_composes_with_the_long_form_profile(tmp_path):
    both, _ = _world("row18-halving", tmp_path / "both", LONG + SOFT)
    lone, _ = _world("row18-halving", tmp_path / "lone", LONG)
    assert both["page"]["bar_style"] == "soft" and both["page"]["axes"]["readability"] == "longform"
    both["page"].pop("bar_style")
    assert _sha(both) == _sha(lone), "the option adds its one key and nothing else"


def test_without_the_option_every_world_is_byte_identical(tmp_path):
    """The 94 and the halving objects are the longform suite's own; their no-option worlds are pinned there at the
    lane's HEAD before this slice."""
    for name, pin in (("row17-94", "94"), ("row18-halving", "halving")):
        oid = {"94": "fx-lf-94", "halving": "fx-lf-halving"}[pin]
        (tmp_path / pin / "evidence/objects").mkdir(parents=True, exist_ok=True)
        obj = PAGES[name][1]
        (tmp_path / pin / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
        saved = B.ASPECT
        B.ASPECT = ASPECT
        try:
            world = B.world_for_plate(f"ledger:{oid}:bars", (0, 0, 0), tmp_path / pin)
            B.stamp_full_stage(world["page"])
        finally:
            B.ASPECT = saved
        assert _sha(world) == WORLD_PINS[pin], name
        assert "bar_style" not in world["page"]


def test_a_portrait_row_takes_the_option_too(tmp_path):
    world, _ = _world("row17-94", tmp_path, SOFT, aspect="9:16")
    assert world["page"]["bar_style"] == "soft"


# ---- the player -----------------------------------------------------------------------------------------------------

PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, stage = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect(); return [r.x - stage.x, r.y - stage.y, r.width, r.height]; };
  const M = st.chart.getScreenCTM();
  const S = (b) => { const p = new DOMPoint(b.x, b.y).matrixTransform(M), q = new DOMPoint(b.x + b.width, b.y + b.height).matrixTransform(M);
                     return [p.x - stage.x, p.y - stage.y, q.x - p.x, q.y - p.y]; };
  const kids = [...st.chart.children], L = st.soft || null;
  const hatch = st.chart.querySelector('g.lp-bar-hatch');
  const lines = hatch ? [...hatch.querySelectorAll('path.lp-hatch-lines')].map(p => ({ d: p.getAttribute('d'), m: p.getAttribute('transform'),
                   fam: p.dataset.family })) : [];
  const sil = L ? L.sil.map(p => { const d = p.getAttribute('d') || ''; return d ? { box: S(p.getBBox()), d } : null; }) : [];
  const vis = (el) => el && +(el.getAttribute('opacity') || 1) > 0.01 && getComputedStyle(el).opacity !== '0';
  const PF = st.perform || { figures: [] };
  return {
    soft: !!L, stagePx: st.stagePx,
    bars: (st.bars || []).map(b => ({ rx: b.bar.getAttribute('rx'), box: R(b.bar), neg: b.neg, idx: kids.indexOf(b.bar),
      foot: b.foot ? { box: R(b.foot), idx: kids.indexOf(b.foot) } : null,
      val: vis(b.val) && +(b.val.getAttribute('opacity') || 0) > 0.01 ? R(b.val) : null, lab: vis(b.lab) ? R(b.lab) : null })),
    base: L ? S({ x: 0, y: L.base, width: 0, height: 0 })[1] : null,
    hatch: hatch ? { idx: kids.indexOf(hatch), fill: hatch.getAttribute('fill'), opacity: +hatch.getAttribute('opacity'),
                     clip: hatch.getAttribute('clip-path'), mask: hatch.getAttribute('mask'), display: hatch.style.display,
                     scale: hatch.firstElementChild ? hatch.firstElementChild.getAttribute('transform') : null } : null,
    lines, sil,
    feet: st.chart.querySelectorAll('rect.lp-bar-foot').length,
    panel: !!st.chart.querySelector('rect.lp-panel'),
    figs: (PF.figures || []).filter(fg => +(fg.g.getAttribute('opacity') || 0) > 0.01).map(fg => R(fg.label)),
    rules: (st.hlines || []).filter(h => h.lab && vis(h.lab)).map(h => R(h.lab)),
    pill: st.callout && +(st.callout.getAttribute('opacity') || 0) > 0.01 ? R(st.callout) : null,
  };
}"""


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

# key -> (page, row options)
CASES = {
    "94-off": ("row17-94", LONG),
    "94-soft": ("row17-94", LONG + SOFT),
    "halving-soft": ("row18-halving", LONG + SOFT),
    "wafer-soft": ("row21-wafer", LONG + SOFT),
    "cross-soft": ("cross", LONG + SOFT),
    "94-classic-soft": ("row17-94", SOFT),     # the charcoal page, no profile: the option stands alone
}


@pytest.fixture(scope="module")
def painted(tmp_path_factory):
    """Each case served once and read at LAND_T (the compare landed) - plus the 94 read mid-build, and the seek round
    trip LAND -> GROW -> LAND on the halving."""
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    from playwright.sync_api import sync_playwright
    from PIL import Image

    tmp = tmp_path_factory.mktemp("soft")
    out = {}
    w, h = RB.STAGE[ASPECT]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for key, (name, opt) in CASES.items():
                world, species = _world(name, tmp / key, opt)
                scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
                           "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
                tl = G._timeline("P69 T10b " + key, scenes, {}, ASPECT)
                uris = G._base_uris()
                uris.update(B.longform_assets(tl))
                html = tmp / f"{key}.html"
                html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
                srv, port = RB.serve(html.parent)
                page = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                errors: list[str] = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                try:
                    page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                    RB.prepare_page(page, w, h)
                    page.wait_for_function("document.fonts.status === 'loaded'")
                    RB.frame_png(page, LAND_T, (w, h))
                    page.wait_for_timeout(120)
                    png = RB.frame_png(page, LAND_T, (w, h))
                    got = {"probe": page.evaluate(PROBE), "img": Image.open(io.BytesIO(png)).convert("RGB"), "errors": errors}
                    if key in ("94-soft", "halving-soft"):
                        RB.frame_png(page, T_GROW, (w, h))
                        got["grow"] = page.evaluate(PROBE)
                        RB.frame_png(page, LAND_T, (w, h))
                        got["back"] = page.evaluate(PROBE)
                    out[key] = got
                finally:
                    page.context.close()
                    srv.shutdown()
        finally:
            browser.close()
    return out


SOFT_CASES = [k for k in CASES if k.endswith("soft")]


def _lum(px) -> float:
    return 0.2126 * px[0] + 0.7152 * px[1] + 0.0722 * px[2]


def _dist(a, b) -> float:
    return math.dist(a[:3], b[:3])


def _meets(a, b) -> bool:
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def _throw(ps: dict) -> tuple[float, float]:
    th = math.radians(ps["LIGHT_DEG"] + 180)
    return ps["OFFSET_PX"] * math.cos(th), ps["OFFSET_PX"] * math.sin(th)


def _shoulder_px() -> float:
    m = re.search(r"const LPBAR_SOFT = Object\.freeze\(\{ SHOULDER_PX: ([\d.]+)", ENGINE.read_text(encoding="utf-8"))
    assert m, "the engine carries no LPBAR_SOFT.SHOULDER_PX dial"
    return float(m.group(1))


@needs_browser
def test_without_the_option_a_bar_is_the_builders_rect_as_it_was(painted):
    got = painted["94-off"]
    assert not got["errors"], got["errors"]
    p = got["probe"]
    assert not p["soft"] and p["hatch"] is None and p["feet"] == 0
    assert [b["rx"] for b in p["bars"]] == ["6"]


@needs_browser
@pytest.mark.parametrize("key", SOFT_CASES)
def test_every_bar_has_rounded_shoulders_away_from_zero_and_square_corners_on_it(painted, key):
    got = painted[key]
    assert not got["errors"], got["errors"]
    p, img, r = got["probe"], got["img"], _shoulder_px()
    assert p["soft"] and p["feet"] == len(p["bars"])
    for b in p["bars"]:
        x, y, w, h = b["box"]
        if h < 3 * r:
            continue   # a bar shorter than its two shoulders is all shoulder
        mid = img.getpixel((int(x + w / 2), int(y + h / 2)))
        far_y, zero_y = (y + h - 3, y + 1.5) if b["neg"] else (y + 3, y + h - 1.5)
        near_zero_y = y + 4 if b["neg"] else y + h - 4
        for fx in (x + 3, x + w - 4):
            far = img.getpixel((int(fx), int(far_y)))
            assert _dist(far, mid) > 25, (key, "a shoulder away from zero is rounded off", b, far, mid)
        for fx in (x + 1.5, x + w - 2.5):
            on = img.getpixel((int(fx), int(near_zero_y)))
            assert _dist(on, mid) < 12, (key, "the corner on zero is square: the bar stands on its baseline", b, on, mid)
        assert b["foot"]["idx"] == b["idx"] - 1, "the foot squaring the zero end sits right under its bar"


@needs_browser
@pytest.mark.parametrize("key", SOFT_CASES)
def test_the_shadow_is_the_props_hatch_by_its_own_painter_and_dials(painted, key, prop_shadow):
    p = painted[key]["probe"]
    hatch, ps = p["hatch"], prop_shadow
    assert hatch and hatch["clip"] and hatch["mask"], "a hatch layer, cut to the silhouettes and tapered"
    assert hatch["idx"] < min(b["idx"] for b in p["bars"]) and hatch["idx"] < min(b["foot"]["idx"] for b in p["bars"]), "under every bar"
    assert hatch["fill"] == "rgb(" + ",".join(str(v) for v in ps["INK"]["page"]) + ")"
    assert hatch["opacity"] == pytest.approx(ps["ALPHA"]["page"])
    fams = {ln["fam"]: ln for ln in p["lines"]}
    assert set(fams) == {"primary", "cross"}
    H = ps["HATCH"]
    for fam, deg, pitch, width in (("primary", ps["LIGHT_DEG"], H["PITCH_PX"], H["WIDTH_PX"]),
                                   ("cross", ps["LIGHT_DEG"] + H["CROSS_DEG"], H["CROSS_PITCH_PX"], H["CROSS_WIDTH_PX"])):
        a, b = [float(v) for v in re.match(r"matrix\(([-\d.e]+),([-\d.e]+)", fams[fam]["m"]).groups()]
        assert math.degrees(math.atan2(b, a)) == pytest.approx(((deg + 180) % 360) - 180, abs=1e-3), fam
        ys = [float(v) for v in re.findall(r"M[-\d.]+ ([-\d.]+)h", fams[fam]["d"])]
        hs = {round(float(v), 4) for v in re.findall(r"v([\d.]+)h", fams[fam]["d"])}
        assert hs == {round(width, 4)}, fam
        assert {round(q - p0, 3) for p0, q in zip(ys, ys[1:])} == {round(pitch, 3)}, fam
    assert hatch["scale"] and hatch["scale"].startswith("scale("), "the lines are laid in STAGE px of the chart at rest"


@needs_browser
@pytest.mark.parametrize("key", SOFT_CASES)
def test_the_silhouette_is_the_bar_thrown_along_the_light_and_never_past_zero(painted, key, prop_shadow):
    p = painted[key]["probe"]
    dx, dy = _throw(prop_shadow)
    assert p["hatch"]["display"] != "none"
    for b, s in zip(p["bars"], p["sil"]):
        assert s is not None, b
        x, y, w, h = b["box"]
        sx, sy, sw, sh = s["box"]
        assert sx == pytest.approx(x + dx, abs=GEOM_TOL) and sw == pytest.approx(w, abs=GEOM_TOL), (b, s)
        if b["neg"]:
            assert sy == pytest.approx(y + dy, abs=GEOM_TOL) and sy + sh == pytest.approx(y + h + dy, abs=GEOM_TOL), (b, s)
            assert sy >= p["base"] - GEOM_TOL, "a negative bar's weight hangs on its own side of zero"
        else:
            assert sy == pytest.approx(y + dy, abs=GEOM_TOL), (b, s)
            assert sy + sh == pytest.approx(p["base"], abs=GEOM_TOL), "E28: a standing bar's weight never falls past zero"


@needs_browser
@pytest.mark.parametrize("key", SOFT_CASES)
def test_the_shadow_reads_beside_every_bar(painted, key, prop_shadow):
    p, img = painted[key]["probe"], painted[key]["img"]
    dx, dy = _throw(prop_shadow)
    r = _shoulder_px()
    for b in p["bars"]:
        x, y, w, h = b["box"]
        top, bot = (y + dy + r + 2, y + h - 3) if not b["neg"] else (y + dy + 3, y + h + dy - r - 2)
        if bot - top < 6:
            continue
        strip = [_lum(img.getpixel((int(xx), int(yy)))) for xx in range(int(x + w + 1), int(x + w + dx - 1))
                 for yy in range(int(top), int(bot))]
        bare = [_lum(img.getpixel((int(xx), int(yy)))) for xx in range(int(x + w + dx + 4), int(x + w + dx + 14))
                for yy in range(int(top), int(bot))]
        dark = sum(bare) / len(bare) - sum(strip) / len(strip)
        assert dark >= DARKEN_MIN, (key, b, round(dark, 2))


@needs_browser
@pytest.mark.parametrize("key", SOFT_CASES)
def test_labels_figures_and_rules_keep_clear_of_the_shadow(painted, key):
    p = painted[key]["probe"]
    r = _shoulder_px()
    for b, s in zip(p["bars"], p["sil"]):
        x, y, w, h = b["box"]
        sx, sy, sw, sh = s["box"]
        strip = [x + w, sy, sx + sw - (x + w), sh]   # the part the bar does not cover: the light falls down and right
        words = [b2["val"] for b2 in p["bars"]] + [b2["lab"] for b2 in p["bars"]] + p["figs"] + p["rules"] + [p["pill"]]
        for box in [q for q in words if q]:
            assert not _meets(strip, box), (key, "a word on the shadow", strip, box)
        v = b["val"]
        if v and y + 2 < v[1] and v[1] + v[3] < y + h - 2:   # a number written INSIDE its bar ...
            assert v[1] >= y + r or (v[0] >= x + r and v[0] + v[2] <= x + w - r), (key, "... stays inside the shoulders", v, b)


@needs_browser
@pytest.mark.parametrize("key", ["94-soft", "halving-soft"])
def test_the_shadow_follows_the_bar_as_it_grows_and_a_seek_lands_the_same(painted, key, prop_shadow):
    got = painted[key]
    g, land, back = got["grow"], got["probe"], got["back"]
    dx, dy = _throw(prop_shadow)
    b, s = g["bars"][0], g["sil"][0]
    assert b["box"][3] < land["bars"][0]["box"][3] - 20, "mid-build: the bar is still growing"
    assert s["box"][1] == pytest.approx(b["box"][1] + dy, abs=GEOM_TOL), (b, s)
    assert s["box"][1] + s["box"][3] == pytest.approx(g["base"], abs=GEOM_TOL)
    assert [q["d"] for q in back["sil"]] == [q["d"] for q in land["sil"]], "a pure function of t"
    assert [q["d"] for q in g["lines"]] == [q["d"] for q in land["lines"]], "the engraving is fixed to the page"


@needs_browser
def test_it_composes_with_the_long_form_panel(painted):
    assert painted["94-soft"]["probe"]["panel"] and painted["94-off"]["probe"]["panel"]
    assert not painted["94-classic-soft"]["probe"]["panel"] and painted["94-classic-soft"]["probe"]["soft"]
