"""P61 T5 / E99 s3 - THE BALL'S SHADOWS: the material the melt's ball is made of.

The operator, `docs/portable/OPERATOR-RULINGS.md:2922-2925`:

    "We definitely need more shadows. The shadows are where the weight/mass largely come from
    i think, dark fresnel rim + metallic band and I imagine incorporating at least one point of
    deep shadow depth."

Four things, each a NAMED dial with a measured default:

  (a) more cast/contact shadow   `MELT.W_OCCL_*`  - the OCCLUSION CORE over the cast slit
  (b) a DARK grazing rim         `DROP.RIM_*` + `MELT.W_RIM_*`  - grazing-angle DARKENING toward the
                                 silhouette, never a bright ring
  (c) a metallic band            `DROP.BAND_*` + `MELT.W_BAND_*`
  (d) one point of deep shadow   `DROP.PIT_*` + `MELT.W_PIT_*`

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
# the flag-OFF melt surfaces - a melt that never asked for weight. These must not move by one byte.
FLAG_OFF_SURFACES = ["melt-page", "melt-page@proof-045", "melt-splash", "melt-plate"]


def _node(expr: str):
    """Evaluate an expression against the two modules and return its JSON."""
    src = (
        f'import {{ DROP, dropRimAlpha, dropBandAlpha, dropPitAlpha, dropDeepPoint, dropLightAxis }} '
        f'from {json.dumps(DROP_MJS.as_uri())};\n'
        f'import {{ MELT, meltOcclusion, meltRimGradientMarkup, meltBandGradientMarkup, meltPitGradientMarkup, '
        f'meltShade, meltSheen, meltInkOf }} from {json.dumps(MELT_MJS.as_uri())};\n'
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
               "W_BAND_K", "W_BAND_STOPS", "W_PIT_SHADE", "W_PIT_STOPS"]


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


@browser
def test_the_flag_on_ball_wears_a_DARK_rim_a_band_and_a_deep_point() -> None:
    import io
    from PIL import Image
    png = RB.render_surface("melt-ball-roll@proof-settle")
    cx, cy, r, lum, _ = _ball(png)
    ring = [lum(int(cx + 0.96 * r * math.cos(a)), int(cy + 0.96 * r * math.sin(a)))
            for a in [i * math.pi / 18 for i in range(36)]]
    body = [lum(int(cx + 0.20 * r * math.cos(a)), int(cy + 0.20 * r * math.sin(a)))
            for a in [i * math.pi / 6 for i in range(12)]]
    rim, mid = sum(ring) / len(ring), sum(body) / len(body)
    # (b) the DARK rim: the silhouette is the dark part and the body is the lit part - the opposite of
    # what shipped, where the silhouette read BRIGHTER than nothing (120.7 against a body of 141.4)
    assert rim < 0.75 * mid, f"the silhouette is not dark: rim {rim:.1f} against body {mid:.1f}"
    # and it darkens MONOTONICALLY outward over the rim's own band, read on the frame
    prof = [sum(lum(int(cx + s * r * math.cos(a)), int(cy + s * r * math.sin(a)))
                for a in [i * math.pi / 18 for i in range(36)]) / 36
            for s in [0.50, 0.65, 0.80, 0.90, 0.96]]
    for i in range(1, len(prof)):
        assert prof[i] <= prof[i - 1] + 1.0, f"the rim lightens outward: {prof}"
    # (d) the point of deep shadow depth: the disc at its seat is darker than its own iso-radius ring
    d = _node("({ seat: dropDeepPoint([0, 0], 1), at: DROP.PIT_AT })")
    sx, sy = cx + d["seat"]["x"] * r, cy + d["seat"]["y"] * r
    pit = sum(lum(int(sx + dx), int(sy + dy)) for dx in (-6, 0, 6) for dy in (-6, 0, 6)) / 9
    around = [lum(int(cx + d["at"] * r * math.cos(a)), int(cy + d["at"] * r * math.sin(a)))
              for a in [i * math.pi / 12 for i in range(24)]]
    assert pit < sum(around) / len(around), f"no well at the seat: {pit:.1f} against {sum(around) / len(around):.1f}"
    # (c) the metallic band: a luminance RIDGE along the light axis, past the equator, not the highlight
    th = math.radians(_node("DROP.LIGHT_DEG"))
    axis = [(p, lum(int(cx + (0.5 - p) * 2 * r * 0.88 * math.cos(th)),
                    int(cy + (0.5 - p) * 2 * r * 0.88 * math.sin(th))))
            for p in [i / 100 for i in range(20, 90)]]
    band_p = _node("DROP.BAND_P")
    win = [v for p, v in axis if abs(p - band_p) < 0.06]
    out = [v for p, v in axis if 0.12 < abs(p - band_p) < 0.24]
    assert max(win) > sum(out) / len(out) + 6, f"no band ridge: peak {max(win):.1f} against {sum(out) / len(out):.1f}"
    # (a) more cast/contact shadow: the board under the ball is darker than the board itself
    im = Image.open(io.BytesIO(png)).convert("RGB")
    bl = lambda x, y: 0.2126 * im.getpixel((x, y))[0] + 0.7152 * im.getpixel((x, y))[1] + 0.0722 * im.getpixel((x, y))[2]
    floor = min(bl(x, cy + r + 8) for x in range(cx - r, cx + r, 3))
    assert floor < 0.5 * bl(100, 100), f"the contact shadow does not read: {floor:.1f} against the board"


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
    assert "if (st.mass && !m.band)" in engine, "the overlays are not behind the opt-in"
    assert "if (st.occl || m.occl)" in engine, "the occlusion core is not behind the opt-in"
    assert "band: null, rim: null, pit: null, occl: null" in engine, "the mount must start with none of them"
