"""P61 T5 / E99 s3 + P61 T5b / E99 s42 - THE BALL'S SHADOWS, and the surface the operator kept.

T5's ruling, `docs/portable/OPERATOR-RULINGS.md:2922-2925`:

    "We definitely need more shadows. The shadows are where the weight/mass largely come from
    i think, dark fresnel rim + metallic band and I imagine incorporating at least one point of
    deep shadow depth."

T5b's, on the frames that answered it, `docs/portable/OPERATOR-RULINGS.md:3202` (E99 s42):

    "This doesn't work, the ball is too blurred so the prior work is actually better. this slice
    is pixelated on the edges now, the darkness feels right, but the blur is wrong,  and i think
    the rim is wrong. the oter ball was better, I would be interested in seeing it just melt to
    the slate gray or the reference color also to see what that looks like."

SO, NAMED FROM THE FRAMES BEFORE ANY DIAL MOVED:

  THE BLUR was the RIM'S OWN RAMP, and no filter at all. `dropRimAlpha` runs from `DROP.RIM_AT`
  0.42 to `RIM_A` 0.97 in near-black ink, so the outer 58 % of the radius was one continuous
  darkening: the ball's board-to-body transition went from 1 px (prior) to over 100 px (T5),
  measured on the settle frame's scanline. A surface with no terminator anywhere is soft focus.
  The BAND was the second smear. There is no `feGaussianBlur` and no CSS `blur()` on the ball in
  either build - the only blur is on the occlusion ellipse, which is on the BOARD.

  THE PIXELATED EDGE was four antialiased copies of the SAME path composited (body + band + pit +
  rim, each handed `st.body` in `paintMelt`): a boundary pixel of coverage `a` ends at
  1 - (1 - a)^4. Measured on one pixel: 0.567 covered on the prior ball, 0.988 on T5's, and
  1 - (1 - 0.567)^4 = 0.965. The rim is the only overlay carrying alpha AT the silhouette, so it
  is the one that destroyed the antialiasing.

So the rim and the band are OFF (`MELT.W_RIM_ON` / `W_BAND_ON`, both false; every profile dial
kept and still tested here), the darkness the operator kept stays, and the ball's BODY COLOUR
becomes an authored option (`melt:weight:...:body=slate|reference`, `MELT_BODIES`).

P61 T5c / E99 s49, on those three balls: *"Otherwise, I like the reference."* So the WEIGHT ball's
DEFAULT body is `reference` (resolved once per side - `meltOpts` after its loop, `_melt_parts`'s
return), the restored orange stays authorable as `body=chart`, and a melt with no weight token has
no ball surface to shade and is byte for byte the melt that shipped.

Four things, each a NAMED dial with a measured default:

  (a) more cast/contact shadow   `MELT.W_OCCL_*`  - the OCCLUSION CORE over the cast slit  [ON]
  (b) a DARK grazing rim         `DROP.RIM_*` + `MELT.W_RIM_*`  - grazing-angle DARKENING toward the
                                 silhouette, never a bright ring                           [OFF, E99 s42]
  (c) a metallic band            `DROP.BAND_*` + `MELT.W_BAND_*`                           [OFF, E99 s42]
  (d) one point of deep shadow   `DROP.PIT_*` + `MELT.W_PIT_*`                             [ON]

THE NAME. `docs_find "Fresnel"` returns three hits and not one is a shading term - `clothoid.mjs:115
fresnel`, `:147 fresnelMoments` and `CAPABILITIES.md:96` are the CLOTHOID fitter's Fresnel INTEGRAL.
Nothing in this slice reuses that name or that module, and a test below refuses it if it ever does.

THE SOURCES. Every dial names its research-gate tier beside it. The gate is
`docs/research/runs/p58-2-5d/research-gate-2026-09-14.md` (R26-119: PLAUSIBLE overall, usable as dial
seeds under [DERIVED], NOTHING CONFIRMED - the run fetched no page to disk; the galinstan sigma and
the whole ink row are EXCLUDED). E99 s24: a dial whose only source is an excluded finding gets a
DERIVED default and says so.

THE OPT-IN. All of it ships behind the existing `melt:weight` token until HG5: a melt that does not ask
for weight mounts no gradient, no overlay path and no shadow ellipse, so its markup is the markup that
shipped and every flag-off golden is byte-identical. The three flag-off melt surfaces are rendered and
compared byte for byte below; `test_golden_frames.py` carries the rest.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import tempfile
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import render_baseline as RB  # noqa: E402

DROP_MJS = ROOT / "content/video_engine/scripts/kinetics/drop.mjs"
MELT_MJS = ROOT / "content/video_engine/scripts/species/melt.mjs"
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
GATE = "docs/research/runs/p58-2-5d/research-gate-2026-09-14.md"
BLUEPRINT = "docs/research/motion/LIVING_METALLIC_DROP_RESEARCH_BLUEPRINT.md"

# the flag-ON surfaces - the `melt:weight` opt-in's OWN goldens, and the only ones this slice may move
WEIGHT_SURFACES = ["melt-ball-roll", "melt-ball-roll@proof-land", "melt-ball-roll@proof-settle",
                   "melt-depth", "melt-depth@proof-ball"]
# P61 T5b / E99 s42: the two BODY COLOURS, at the settle - the same instant as `melt-ball-roll@proof-settle`
BODY_SURFACES = {"slate": "melt-ball-slate@proof-settle", "reference": "melt-ball-reference@proof-settle"}
# and the colour each one must land on. SLATE is the BOARD's own ink token: `--lp-char: #25313C`,
# docs/content-video-engine/samples/scene-evidence-player.template.html:50, the same charcoal the brand
# tokens carry as `color.charcoal` (channel-assets/money-physics/brand-tokens.json:12). REFERENCE is the
# blueprint's near-black metal: LIVING_METALLIC_DROP_RESEARCH_BLUEPRINT.md s3.3 (:198-201, gate tier
# PLAUSIBLE) - "Zero Diffuse Reflectance (k_d = 0) ... The albedo base color is pure black".
BODY_TARGET = {"slate": (0x25, 0x31, 0x3C), "reference": (0x00, 0x00, 0x00)}
# the flag-OFF melt surfaces - a melt that never asked for weight. These must not move by one byte.
FLAG_OFF_SURFACES = ["melt-page", "melt-page@proof-045", "melt-splash", "melt-plate"]


def _node(expr: str):
    """Evaluate an expression against the two modules and return its JSON."""
    src = (
        f'import {{ DROP, dropRimAlpha, dropBandAlpha, dropPitAlpha, dropDeepPoint, dropLightAxis }} '
        f'from {json.dumps(DROP_MJS.as_uri())};\n'
        f'import {{ MELT, MELT_BODIES, meltOpts, meltOcclusion, meltRimGradientMarkup, meltBandGradientMarkup, '
        f'meltPitGradientMarkup, meltBodyGradientMarkup, meltBodyInk, meltShade, meltSheen, meltInkOf }} '
        f'from {json.dumps(MELT_MJS.as_uri())};\n'
        f'console.log(JSON.stringify(({expr})));\n'
    )
    out = subprocess.run([("node.exe" if sys.platform == "win32" else "node"), "--input-type=module", "-e", src],
                         capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


# ---- 1. THE DIALS ARE DECLARED, AND EACH ONE NAMES ITS SOURCE -----------------------------------

MATERIAL_DIALS = ["RIM_AT", "RIM_GAMMA", "RIM_A", "BAND_P", "BAND_H", "BAND_A",
                  "PIT_AT", "PIT_R", "PIT_GAMMA", "PIT_A"]
PAINT_DIALS = ["W_OCCL_A", "W_OCCL_W", "W_OCCL_FLAT", "W_OCCL_BLUR", "W_RIM_SHADE", "W_RIM_STOPS",
               "W_BAND_K", "W_BAND_STOPS", "W_PIT_SHADE", "W_PIT_STOPS",
               "W_BODY_SHADE"]   # P61 T5b / E99 s42: how far the ball's ink goes to its named body colour
# P61 T5b / E99 s42: the two GATES. Not in PAINT_DIALS because they are booleans, not measured numbers -
# every profile dial above them is kept exactly as T5 measured it, and these are what turn them off.
GATE_DIALS = ["W_RIM_ON", "W_BAND_ON"]


def test_every_dial_is_declared_with_a_measured_default() -> None:
    drop, melt = DROP_MJS.read_text(encoding="utf-8"), MELT_MJS.read_text(encoding="utf-8")
    for name in MATERIAL_DIALS:
        assert re.search(rf"^\s+{name}: -?[\d.]+,", drop, re.M), f"{name}: not declared in DROP"
    for name in PAINT_DIALS:
        assert re.search(rf"^\s+{name}: -?[\d.]+,", melt, re.M), f"{name}: not declared in MELT"
    values = _node("{ mat: Object.fromEntries(%s.map(k => [k, DROP[k]])), "
                   "paint: Object.fromEntries(%s.map(k => [k, MELT[k]])) }"
                   % (json.dumps(MATERIAL_DIALS), json.dumps(PAINT_DIALS)))
    for k, v in {**values["mat"], **values["paint"]}.items():
        assert isinstance(v, (int, float)) and math.isfinite(v), f"{k} = {v!r}"
    # P61 T5b / E99 s42: the refused overlays keep every dial they had, and the gates are what is off
    gates = _node("Object.fromEntries(%s.map(k => [k, MELT[k]]))" % json.dumps(GATE_DIALS))
    assert gates == {"W_RIM_ON": False, "W_BAND_ON": False}, \
        f"E99 s42 turned the rim and the band OFF, and they are {gates}"
    for name in GATE_DIALS:
        assert re.search(rf"^\s+{name}: false,", melt, re.M), f"{name}: not declared in MELT"


def test_every_dial_carries_a_source_or_says_it_is_derived() -> None:
    """E99 s24: a finding the gate did not mark usable stays excluded, and a dial whose only source is
    an excluded finding gets a DERIVED default AND SAYS SO. Each dial's own comment carries a tag."""
    for path, dials in [(DROP_MJS, MATERIAL_DIALS), (MELT_MJS, PAINT_DIALS)]:
        text = path.read_text(encoding="utf-8")
        for name in dials:
            start = text.index(f"  {name}: ")
            end = text.index("*/", start)
            comment = text[start:end]
            assert "[DERIVED" in comment or "MEASURED" in comment, f"{name}: no evidentiary tag on its comment"


def test_the_source_block_names_the_blueprint_the_gate_and_the_tiers() -> None:
    drop = DROP_MJS.read_text(encoding="utf-8")
    assert BLUEPRINT.rsplit("/", 1)[-1] in drop or "blueprint" in drop.lower()
    assert GATE in drop, "the dial block must name the research gate it was read through"
    assert "PLAUSIBLE" in drop, "the tier of the finding the rim and the band lean on"
    assert "EXCLUDED" in drop, "and the findings that stay excluded (E99 s24)"
    assert "CONFIRMED" in drop and "NOTHING in it is CONFIRMED" in drop, \
        "the gate's decisive fact: the run fetched no page to disk, so nothing is CONFIRMED"


def test_the_clothoid_fresnel_name_is_not_reused() -> None:
    """The plan's recall warning: `docs_find "Fresnel"` returns the CLOTHOID fitter's Fresnel INTEGRAL
    and nothing else. This slice must not reuse the name or the module."""
    for path in (DROP_MJS, MELT_MJS):
        text = path.read_text(encoding="utf-8")
        code = "\n".join(re.sub(r"/\*.*?\*/", "", text, flags=re.S).splitlines())
        assert "fresnel" not in code.lower(), f"{path.name}: a symbol named for the clothoid integral"
        assert "clothoid" not in code.lower(), f"{path.name}: imports the clothoid module"


# ---- 2. THE PROFILES: a dark rim, a band, a point ------------------------------------------------

def test_the_rim_darkens_MONOTONE_toward_the_silhouette_and_is_never_a_bright_ring() -> None:
    d = _node("({ dials: { RIM_AT: DROP.RIM_AT, RIM_A: DROP.RIM_A }, "
              "  a: Array.from({ length: 401 }, (_, i) => dropRimAlpha(i / 400)), "
              "  shade: meltShade('#fe5a2d', MELT.W_RIM_SHADE), lit: '#fe5a2d' })")
    a = d["a"]
    assert a[0] == 0 and a[int(400 * d["dials"]["RIM_AT"])] == 0, "nothing inside the band's start"
    for i in range(1, len(a)):
        assert a[i] >= a[i - 1] - 1e-12, f"the rim lightens at s={i / 400}: {a[i]} after {a[i - 1]}"
    assert abs(a[-1] - d["dials"]["RIM_A"]) < 1e-9, "darkest AT the silhouette"
    # a DARK rim: the ink it is painted in is DARKER than the ball's own ink. Read in LINEAR light,
    # which is where meltShade works - and it is exactly why the rim is a SHADE and not a Kubelka-Munk
    # concentration: K-M mixing saturates an orange stroke toward a bright RED (`meltInkOf` gives
    # #fd1a08 at CORE 12 and #fc0c03 at 34, both at full luminance) and can never reach a shadow at
    # all. The first build of this slice drew the rim at K-M 34, the silhouette stayed bright, and that
    # is what sent the dial to a shade.
    def lin(hexstr):
        v = [int(hexstr[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        v = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v]
        return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
    assert lin(d["shade"]) < 0.15 * lin(d["lit"]), f"the rim's ink is not dark: {d['shade']}"
    km = _node("[meltInkOf(['#fe5a2d'], MELT.CORE), meltInkOf(['#fe5a2d'], 34)]")
    assert all(lin(c) > 0.5 * lin(d["lit"]) for c in km),         f"K-M concentration has become a way to make a shadow ({km}) - re-read the dial's comment"

def test_the_metallic_band_is_one_stripe_normal_to_the_light() -> None:
    d = _node("({ peak: DROP.BAND_P, amp: DROP.BAND_A, "
              "  a: Array.from({ length: 501 }, (_, i) => dropBandAlpha(i / 500)), ax: dropLightAxis(), "
              "  deg: DROP.LIGHT_DEG })")
    a = d["a"]
    assert abs(max(a) - d["amp"]) < 1e-9 and abs(a.index(max(a)) / 500 - d["peak"]) < 0.005
    rises = sum(1 for i in range(1, len(a)) if a[i] > a[i - 1] + 1e-12 and a[i - 1] <= a[i - 2] if i > 1)
    assert rises <= 1, "more than one band"
    assert a[0] < 0.02 * d["amp"] and a[-1] < 0.02 * d["amp"], "the poles are clear of the band"
    th = math.radians(d["deg"])
    assert abs(d["ax"]["x1"] - (0.5 + 0.5 * math.cos(th))) < 1e-9
    assert abs(d["ax"]["y1"] - (0.5 + 0.5 * math.sin(th))) < 1e-9


def test_the_point_of_deep_shadow_depth_is_seated_opposite_the_light() -> None:
    d = _node("({ seat: dropDeepPoint([0, 0], 60), deg: DROP.LIGHT_DEG, at: DROP.PIT_AT, "
              "  a: Array.from({ length: 401 }, (_, i) => dropPitAlpha(i / 400)), amp: DROP.PIT_A })")
    seat = d["seat"]
    want = math.radians(d["deg"] + 180)
    got = math.atan2(seat["y"], seat["x"])
    assert abs(math.atan2(math.sin(got - want), math.cos(got - want))) < 1e-9, "not opposite the light"
    assert abs(math.hypot(seat["x"], seat["y"]) / 60 - d["at"]) < 1e-9
    a = d["a"]
    assert abs(a[0] - d["amp"]) < 1e-9 and a[-1] == 0
    for i in range(1, len(a)):
        assert a[i] <= a[i - 1] + 1e-12, f"the well is not monotone at s={i / 400}"


def test_the_occlusion_core_is_tighter_and_darker_than_the_cast_slit_and_gone_in_flight() -> None:
    d = _node("({ near: meltOcclusion({ scale: 1.05, alpha: 0.85, blur: 0.8 }, 60), "
              "  far: meltOcclusion({ scale: 0.55, alpha: 0.55, blur: 16 }, 60), "
              "  none: meltOcclusion(null, 60), castW: MELT.W_SHADOW_W, castA: MELT.W_SHADOW_A })")
    near, far = d["near"], d["far"]
    assert d["none"] is None, "a melt without weight has no shadow, so it has no core"
    assert near["rx"] < 60 * d["castW"], "the core must be SMALLER than the cast slit it sits on"
    assert near["alpha"] > 0.85 * d["castA"], "and DARKER than it, or it is not more shadow"
    assert near["ry"] < near["rx"], "it is a patch on the board, seen flat"
    assert far["alpha"] < 0.25 * near["alpha"], "in flight it is all but gone"
    assert far["rx"] < near["rx"], "and tighter at the contact than away from it"


# ---- 3. THE FRAMES -------------------------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _melt_dom(surface: str, t: float) -> dict:
    """P61 T5b: the melt overlay's LIVE DOM at one instant - how many paths the ball wears, whether any
    of them carries a filter, and how many gradients the ball's defs hold. `render_baseline` renders a
    PNG; this walks the same page the same way and reads the markup instead, so "no blur on the ball" is
    an assertion about what the player built and not about what the source says."""
    import tempfile
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface(surface)
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / f"{surface}.html"
        html.write_text(RB.instantiate(tl, uris, RB.TEMPLATE), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                browser_ = pw.chromium.launch(headless=True)
                page = browser_.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                page.evaluate("t => { const s = document.getElementById('scrub');"
                              " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                out = page.evaluate(
                    "() => { const g = document.querySelector('svg.meltov g.meltbody');"
                    " if (!g) return { paths: 0, filters: ['no meltbody group'], grads: 0 };"
                    " const paths = [...g.querySelectorAll('path')].filter(p => (p.getAttribute('d') || '').length > 1);"
                    " const filters = [];"
                    " for (const n of [g, ...g.children]) {"
                    "   const f = n.getAttribute('filter') || (n.style && n.style.filter) || '';"
                    "   if (f) filters.push(n.tagName + ':' + f); }"
                    r" const ids = new Set(paths.map(p => (p.getAttribute('fill') || '').replace(/^url\(#|\)$/g, '')));"
                    " const defs = document.querySelector('svg.meltov defs');"
                    " const grads = [...defs.children].filter(n => /Gradient$/.test(n.tagName) && ids.has(n.id)).length;"
                    " return { paths: paths.length, filters, grads }; }")
                browser_.close()
        finally:
            srv.shutdown()
    return out


@browser
@pytest.mark.parametrize("surface", FLAG_OFF_SURFACES)
def test_a_melt_that_never_asked_for_weight_renders_the_bytes_it_always_did(surface: str) -> None:
    """THE OPT-IN GATE. No approved cut's frames move: the new look mounts nothing at all unless the
    exit string carried `:weight`."""
    golden = (RB.FRAMES / f"{surface}.png").read_bytes()
    actual = RB.render_surface(surface)
    assert hashlib.sha256(actual).hexdigest() == hashlib.sha256(golden).hexdigest(), \
        f"{surface}: a flag-OFF melt changed - the opt-in leaked"


def _ball(png: bytes):
    """The ball's centre and radius in a rendered melt frame, and a luminance reader."""
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(png)).convert("RGB")
    px, (w, h) = im.load(), im.size
    board = px[100, 100]
    pts = [(x, y) for y in range(h // 2, h - 20, 2) for x in range(40, w - 40, 2)
           if sum(abs(px[x, y][i] - board[i]) for i in range(3)) > 120]
    assert pts, "no ball on the frame"
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    cx, cy, r = (min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2, (max(xs) - min(xs)) // 2
    lum = lambda x, y: 0.2126 * px[x, y][0] + 0.7152 * px[x, y][1] + 0.0722 * px[x, y][2]
    return cx, cy, r, lum, im.size


def _render_body(word: str, t: float) -> bytes:
    """`melt-ball-roll` at one instant with the ball's BODY word forced, rendered in memory: the golden
    source is read, its one exit string rewritten, and the page instantiated in a temp dir - the file on
    disk is never touched and no new golden surface is added. P61 T5c / E99 s49 made `reference` the
    default, so a measurement that needs a legible body renders `body=chart` - the prior ball exactly."""
    tl, uris, _t, aspect = RB.load_surface("melt-ball-roll")
    src = json.dumps(tl)
    assert src.count('"melt:weight"') == 1, "melt-ball-roll no longer carries exactly one bare weight exit"
    tl = json.loads(src.replace('"melt:weight"', f'"melt:weight:body={word}"'))
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / f"melt-ball-body-{word}.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        return RB.render_frame(html, t, aspect)


@browser
def test_the_rim_and_the_band_are_OFF_so_the_silhouette_is_NOT_darker_than_the_body() -> None:
    """E99 s42, the INVERSE of T5's rim assertion. T5 asserted `rim < 0.75 * body` and the operator
    refused the look it produced. The silhouette must now be back where the prior ball had it: not
    darker than the body, because the grazing rim is off. Measured on the frame, not on the diff.

    P61 T5c / E99 s49 moved the DEFAULT ball to the reference black, whose body AND silhouette both
    sit at luminance 0 - a ratio there is 0 > 0.8 * 0, degenerate, and proves nothing either way. The
    two gates are body-independent (`MELT.W_RIM_ON` / `W_BAND_ON` are read before any colour), so the
    ramp is measured on the `body=chart` ball - the prior ball exactly, rendered IN MEMORY so no new
    golden surface is needed and the source on disk is never touched - and the default black ball is
    then held to the only claim it can still carry: its silhouette is not DARKER than its body."""
    png = _render_body("chart", RB.PROOF_FRAMES["melt-ball-roll@proof-settle"][2])
    cx, cy, r, lum, _ = _ball(png)
    ring = [lum(int(cx + 0.96 * r * math.cos(a)), int(cy + 0.96 * r * math.sin(a)))
            for a in [i * math.pi / 18 for i in range(36)]]
    body = [lum(int(cx + 0.20 * r * math.cos(a)), int(cy + 0.20 * r * math.sin(a)))
            for a in [i * math.pi / 6 for i in range(12)]]
    rim, mid = sum(ring) / len(ring), sum(body) / len(body)
    assert rim > 0.80 * mid, f"the silhouette is dark again - the rim is back on: rim {rim:.1f} against body {mid:.1f}"
    th = math.radians(_node("DROP.LIGHT_DEG"))
    axis = [(p, lum(int(cx + (0.5 - p) * 2 * r * 0.88 * math.cos(th)),
                    int(cy + (0.5 - p) * 2 * r * 0.88 * math.sin(th))))
            for p in [i / 100 for i in range(20, 90)]]
    # T5 asserted a RIDGE at DROP.BAND_P (`max(win) > mean(out) + 6`). With the band off, the light axis
    # falls off MONOTONICALLY across the band's own window, so a local maximum in it is a band coming
    # back. The window stops at +-0.12 of BAND_P on purpose: further out on the dark side the light axis
    # climbs again out of the POINT OF DEEP SHADOW DEPTH, which is the darkness E99 s42 kept.
    band_p, band_h = _node("DROP.BAND_P"), _node("DROP.BAND_H")
    seg = [(p, v) for p, v in axis if abs(p - band_p) <= 0.12]
    assert len(seg) > 2 * 0.12 / 0.01 - 2 and 0.12 > 2 * band_h, (len(seg), band_h)
    for i in range(1, len(seg)):
        assert seg[i][1] <= seg[i - 1][1] + 2.0, \
            f"a ridge on the light axis at p={seg[i][0]:.2f} (BAND_P is {band_p}): {seg[i - 1][1]:.1f} -> {seg[i][1]:.1f}"
    # P61 T5c: and the DEFAULT (reference) ball - both readings at 0, so the inequality is the whole claim
    cx, cy, r, lum, _ = _ball(RB.render_surface("melt-ball-roll@proof-settle"))
    ring = [lum(int(cx + 0.96 * r * math.cos(a)), int(cy + 0.96 * r * math.sin(a)))
            for a in [i * math.pi / 18 for i in range(36)]]
    body = [lum(int(cx + 0.20 * r * math.cos(a)), int(cy + 0.20 * r * math.sin(a)))
            for a in [i * math.pi / 6 for i in range(12)]]
    rim, mid = sum(ring) / len(ring), sum(body) / len(body)
    assert rim >= mid - 2.0, f"the default ball's silhouette is darker than its body: rim {rim:.1f} against body {mid:.1f}"


@browser
def test_the_darkness_the_operator_kept_is_still_there() -> None:
    """E99 s42: "the darkness feels right". The contact/occlusion core and the point of deep shadow
    depth are the two that stayed, and both are measured on the frame."""
    import io
    from PIL import Image
    png = RB.render_surface("melt-ball-roll@proof-settle")
    cx, cy, r, lum, _ = _ball(png)
    d = _node("({ seat: dropDeepPoint([0, 0], 1), at: DROP.PIT_AT })")
    sx, sy = cx + d["seat"]["x"] * r, cy + d["seat"]["y"] * r
    pit = sum(lum(int(sx + dx), int(sy + dy)) for dx in (-6, 0, 6) for dy in (-6, 0, 6)) / 9
    around = [lum(int(cx + d["at"] * r * math.cos(a)), int(cy + d["at"] * r * math.sin(a)))
              for a in [i * math.pi / 12 for i in range(24)]]
    assert pit < sum(around) / len(around), f"no well at the seat: {pit:.1f} against {sum(around) / len(around):.1f}"
    im = Image.open(io.BytesIO(png)).convert("RGB")
    bl = lambda x, y: 0.2126 * im.getpixel((x, y))[0] + 0.7152 * im.getpixel((x, y))[1] + 0.0722 * im.getpixel((x, y))[2]
    floor = min(bl(x, cy + r + 8) for x in range(cx - r, cx + r, 3))
    assert floor < 0.35 * bl(100, 100), f"the contact shadow does not read: {floor:.1f} against the board (T5 took it to 21%, E99 s42 kept it)"


@browser
def test_the_ball_carries_no_blur_filter_in_its_markup_by_default() -> None:
    """E99 s42: "the blur is wrong". The ball's own DOM - the body group and every path in it - must
    carry no filter at all. The only blur a melt writes is on the two shadow ELLIPSES, which are on
    the BOARD. Read off the live DOM at the settle, not off the source."""
    dom = _melt_dom("melt-ball-roll", 16.98)
    assert dom["paths"] >= 1, "no ball in the body group at the settle"
    assert dom["filters"] == [], f"the ball's own markup carries a filter: {dom['filters']}"
    assert dom["paths"] == 2, f"the ball wears {dom['paths']} stacked paths - E99 s42 left it the body and the pit"
    assert dom["grads"] == 2, f"the ball's gradients are {dom['grads']} - the body's and the pit's, no rim and no band"


@browser
@pytest.mark.parametrize("word", sorted(BODY_SURFACES))
def test_the_two_body_colours_land_on_the_colour_they_name(word: str) -> None:
    """E99 s42: "I would be interested in seeing it just melt to the slate gray or the reference
    color". Measured on the rendered ball at the settle, away from the specular spot and the well:
    the body's own colour IS the token it names."""
    import io
    from PIL import Image
    png = RB.render_surface(BODY_SURFACES[word])
    cx, cy, r, _, _ = _ball(RB.render_surface("melt-ball-roll@proof-settle"))   # the DEFAULT ball's geometry: same instant, same drop
    im = Image.open(io.BytesIO(png)).convert("RGB")
    th = math.radians(_node("DROP.LIGHT_DEG"))
    pts = [im.getpixel((int(cx + 0.62 * r * math.cos(th + a)), int(cy + 0.62 * r * math.sin(th + a))))
           for a in [-0.9, -0.45, 0.45, 0.9]]
    got = tuple(round(sum(p[i] for p in pts) / len(pts)) for i in range(3))
    want = BODY_TARGET[word]
    assert max(abs(got[i] - want[i]) for i in range(3)) <= 12, f"the {word} ball's body is {got}, not {want}"


def test_an_unknown_material_or_body_word_is_refused_BY_NAME() -> None:
    """R26-118 / E88 s7 for the material, E99 s42 for the body: a word this engine does not have is
    refused BY NAME on both sides of the grammar, never painted as the default."""
    import build_scene_timeline_f as B
    for bad in ("bronze", "steel"):
        with pytest.raises(ValueError) as e:
            B.parse_exit("melt:weight:" + bad)
        assert bad in str(e.value) and "material" in str(e.value), str(e.value)
    for bad in ("charcoal", "orange", "gray"):
        with pytest.raises(ValueError) as e:
            B.parse_exit("melt:weight:body=" + bad)
        assert bad in str(e.value) and "body colour" in str(e.value), str(e.value)
    assert B.melt_body("melt") == "chart" and B.melt_body("melt:weight") == "reference"
    assert B.melt_body("melt:weight:body=slate") == "slate"
    assert B.melt_body("melt:weight:metal:body=reference:2.8") == "reference"
    with pytest.raises(ValueError):
        B.parse_exit("melt:weight:body=slate:body=reference")
    said = _node("(() => { const out = []; for (const w of ['charcoal', 'orange', 'gray']) { "
                 "try { meltOpts('melt:weight:body=' + w); out.push(null); } catch (e) { out.push(e.message); } } "
                 "return { said: out, bodies: Object.keys(MELT_BODIES), "
                 "def: meltOpts('melt').wbody, weight: meltOpts('melt:weight').wbody, "
                 "chart: meltOpts('melt:weight:body=chart').wbody, "
                 "slate: meltOpts('melt:weight:body=slate').wbody }; })()")
    assert said["bodies"] == list(B.MELT_BODIES), "the two sides name different body colours"
    assert all(m and "is not a body colour" in m for m in said["said"]), said["said"]
    assert said["def"] == "chart" and said["slate"] == "slate"


def test_the_weight_ball_s_DEFAULT_BODY_is_the_reference_black_and_both_sides_agree() -> None:
    """P61 T5c / E99 s49 (the operator, 2026-09-16, on the three balls: *"Otherwise, I like the
    reference."*): a `melt:weight` that names no `body=` word wears the REFERENCE black - the
    blueprint's near-black metal - and the restored orange stays authorable as `body=chart`.
    The default is resolved in ONE place per side (`meltOpts` after its loop, `_melt_parts`'s
    return), and this pins the two to each other over the whole grammar. A melt with NO weight
    token has no ball surface to shade, so it stays `chart` and its frames cannot move."""
    import build_scene_timeline_f as B
    want = {"melt": "chart", "melt:morph": "chart", "melt:gather:morph": "chart",
            "melt:splash:chart": "chart", "melt:splash:plate": "chart",
            "melt:weight": "reference", "melt:weight:metal": "reference",
            "melt:weight:depth=1.15": "reference", "melt:gather:weight:splash:plate": "reference",
            "melt:weight:body=chart": "chart", "melt:weight:body=slate": "slate",
            "melt:weight:body=reference": "reference"}
    got = _node("(() => { const o = {}; for (const e of " + json.dumps(sorted(want))
                + ") o[e] = meltOpts(e).wbody; return o; })()")
    for exit_id, word in want.items():
        assert B.melt_body(exit_id) == word, f"the compiler paints {exit_id} {B.melt_body(exit_id)}, not {word}"
        assert got[exit_id] == word, f"the player paints {exit_id} {got[exit_id]}, not {word}"


def test_the_default_body_writes_the_string_the_ball_always_had() -> None:
    """The byte-identity the flag-off goldens rest on: `chart` has no target, so `meltBodyInk` IS
    `meltInkOf` and every default string is character for character the one that shipped."""
    d = _node("({ same: meltBodyGradientMarkup('g', ['#fe5a2d']) === meltBodyGradientMarkup('g', ['#fe5a2d'], { wbody: 'chart' }), "
              "  chart: meltBodyInk(['#fe5a2d'], MELT.CORE), km: meltInkOf(['#fe5a2d'], MELT.CORE), "
              "  slate: meltBodyInk(['#fe5a2d'], MELT.LIGHT, { wbody: 'slate' }), "
              "  ref: meltBodyInk(['#fe5a2d'], MELT.LIGHT, { wbody: 'reference' }), "
              "  targets: MELT_BODIES, rim: MELT.W_RIM_ON, band: MELT.W_BAND_ON })")
    assert d["same"], "a `chart` body writes a different gradient from no body at all"
    assert d["chart"] == d["km"], "the default ball's ink is no longer meltInkOf's"
    assert d["targets"]["chart"] is None, "the default must have NO target"
    assert d["slate"].lower() == "#25313c", "slate is not the board's ink: " + d["slate"]
    assert d["ref"] == "#000000", "reference is not the blueprint's pure-black albedo: " + d["ref"]
    assert d["rim"] is False and d["band"] is False, "E99 s42: the rim and the band are OFF by default"


@browser
def test_two_seeks_to_one_t_are_the_same_frame() -> None:
    """P39 T2 / E97: a scrubbed frame IS the played frame. The shading is a pure function of t, so the
    same instant rendered twice is the same bytes."""
    a = RB.render_surface("melt-ball-roll@proof-settle")
    b = RB.render_surface("melt-ball-roll@proof-settle")
    assert hashlib.sha256(a).hexdigest() == hashlib.sha256(b).hexdigest()


# ---- 4. THE ENGINE CARRIES THE SAME CODE ---------------------------------------------------------

def test_the_inlined_engine_carries_every_dial_and_mounts_nothing_without_weight() -> None:
    engine = ENGINE.read_text(encoding="utf-8")
    for name in MATERIAL_DIALS + PAINT_DIALS:
        assert re.search(rf"^\s+{name}: -?[\d.]+,", engine, re.M), f"{name}: not inlined into the player"
    for fn in ["meltRimGradientMarkup", "meltBandGradientMarkup", "meltPitGradientMarkup", "meltOcclusion",
               "dropRimAlpha", "dropBandAlpha", "dropPitAlpha", "dropDeepPoint", "dropLightAxis", "meltShade"]:
        assert fn in engine, f"{fn}: not inlined into the player"
    # the gate itself: every overlay and the core hang off `st.mass` / `st.occl`, which only a
    # `melt:weight` ever sets - so a melt without it writes no gradient and no path
    assert "if (st.mass && !m.pit)" in engine, "the overlays are not behind the opt-in"
    assert "if (st.occl || m.occl)" in engine, "the occlusion core is not behind the opt-in"
    assert "band: null, rim: null, pit: null, occl: null" in engine, "the mount must start with none of them"
    # P61 T5b / E99 s42: the two refused overlays are gated OFF in the player too, and the body
    # colours are the same three words the compiler validates
    assert "W_RIM_ON: false" in engine and "W_BAND_ON: false" in engine, "the rim / band gates are not inlined, or not off"
    assert "if (W.W_BAND_ON) {" in engine and "if (W.W_RIM_ON) {" in engine, "the player paints them unconditionally"
    for fn in ["meltBodyInk", "MELT_BODIES"]:
        assert fn in engine, f"{fn}: not inlined into the player"
    import build_scene_timeline_f as B
    assert _node("Object.keys(MELT_BODIES)") == list(B.MELT_BODIES), "the two sides name different body colours"
