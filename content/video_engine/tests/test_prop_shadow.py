"""P69 T6b / E99 s92 - A PROP IS BARE OF PAPER, NOT OF WEIGHT, measured ON THE RENDERED FRAME.

The operator (2026-09-22): *"We don't put the props on cards. Also, the props should have shadow added to them to
give them some depth/weight."* And on the first cut's soft blur: *"The shadow doesn't look great, I think we need like
cross hatch markings as shadow for texture."* So a prop (`dock_kind:prop`) at rest carries a CROSS-HATCHED shadow -
engraved lines, the woodcut plates' own texture - in its own SILHOUETTE, thrown along the stage light's fall, and the
stamp's contact shadow hands over to it at settle instead of vanishing.

What this file reads, through the served player on the committed `prop-stamp` golden's own page:

  (1) THE HATCH LAYER     a `.dock-hatch` canvas under the mark in the dock layer (never a box, never a filter): the
                          dock's `box-shadow` stays "none" and the picture's frame carries no filter.
  (2) THE SILHOUETTE      every hatch pixel lies inside the prop's own painted alpha thrown by PROP_SHADOW.OFFSET_PX
                          along LIGHT_DEG + 180 - read by drawing the dock's own <img> through the dock's own resolved
                          transform, independently of the painter.
  (3) FIXED TO THE PAGE   the hatch lines stand on the same stage pixels (on/off) while the mark is still turning 2.4 deg
                          off its rest and at rest: the silhouette follows the mark, the engraving does not spin.
  (4) IT READS            on the rendered frame, in the part of the shadow the mark does not cover, the gaps between
                          the lines are brighter than the lines by at least CONTRAST_MIN levels of luminance (0-255) -
                          20 on the charcoal page, 60 on a light ground - so the texture is visible on both grounds.
  (5) THE HANDOVER        the contact shadow falls to 0 exactly as the hatch reaches full, both continuous across the
                          stamp's contact -> settle window: no frame-to-frame pop, and the weight never drops out.
  (6) A CARD              creates no hatch and keeps its own shadow exactly (the goldens hold the bytes).
  (7) THE PLACEMENT       the hatch's whole reach lies inside the disc the stamp fit already keeps clear of the page's
                          ink (the painted half-diagonal + STAMP_RING_GAP_PX + the stroke), and inside
                          `stamp_reserved_box`, so nothing lands on it and the compiler's box needs no change.
"""
from __future__ import annotations

import base64
import contextlib
import copy
import io
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

SURFACE = "prop-stamp"
CARD_SURFACE = "dock-pair-16x9"   # two plain cards on a plate - a card's shadow, untouched
ENTER = G.PROP_STAMP_ENTER        # the stamp's own t = 0
STEP = 0.01                       # the scrub's step
T_TURN = ENTER + 0.30             # the scale has landed, the free rotation spring is still well off its rest
T_REST = ENTER + 1.30             # the golden's own settled instant
STOPACTION = ROOT / "content/video_engine/scripts/kinetics/stopaction.mjs"
DROP_MJS = ROOT / "content/video_engine/scripts/kinetics/drop.mjs"
CREAM = (244, 230, 199)           # the template's --cream: a LIGHT ground
CHARCOAL = (37, 49, 60)           # the template's --charcoal
CONTRAST_MIN = {"page": 20.0, "ground": 60.0}   # gap minus line luminance, 0-255, in the uncovered shadow (4)


def _node(src: str):
    r = subprocess.run(["node", "--input-type=module", "-e", src], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def _stamp_clock() -> tuple[float, float]:
    """(contact, settle) in seconds from the stamp's own zero: the clamped scale spring's crossing `tc` and the free
    rotation spring's SETTLE_Z / (zeta w0) - read off the module, never retyped."""
    tc, ts = _node(f"""const m = await import({json.dumps(STOPACTION.as_uri())});
      console.log(JSON.stringify([m.STAMP_LAND.tc, m.STAMP_TURN.ts]));""")
    return tc, ts


@pytest.fixture(scope="module")
def dials() -> dict:
    got = _node(f"""const s = await import({json.dumps(STOPACTION.as_uri())});
      const d = await import({json.dumps(DROP_MJS.as_uri())});
      console.log(JSON.stringify({{ ps: s.PROP_SHADOW ?? null, light: d.DROP.LIGHT_DEG }}));""")
    assert got["ps"] is not None, "stopaction.mjs exports no PROP_SHADOW dial block"
    return got


def _throw(ps: dict) -> tuple[float, float]:
    th = math.radians(ps["LIGHT_DEG"] + 180)
    return ps["OFFSET_PX"] * math.cos(th), ps["OFFSET_PX"] * math.sin(th)


def _reach(ps: dict) -> float:
    """How far the hatch reaches past the painted edge: the throw, half its widest line, and 1 px of antialiasing
    (the hatch has no blur)."""
    h = ps["HATCH"]
    return ps["OFFSET_PX"] + max(h["WIDTH_PX"], h["CROSS_WIDTH_PX"]) / 2 + 1.0


# ---- the dials and the placement (no browser) ---------------------------------------------------


def test_the_resting_shadow_is_a_CROSS_HATCH_thrown_from_the_STAGE_LIGHT(dials):
    ps = dials["ps"]
    assert ps["LIGHT_DEG"] == dials["light"], "the drop's own light - never a second one"
    dx, dy = _throw(ps)
    assert dx > 0 and dy > 0, "the light is up and to the left, so the shadow falls down and right"
    assert "BLUR_PX" not in ps, "engraved lines, never a soft blur"
    h = ps["HATCH"]
    assert 4 <= h["PITCH_PX"] <= 6 and 1 <= h["WIDTH_PX"] <= 1.5, "fine lines at an engraver's pitch"
    assert h["CROSS_PITCH_PX"] > h["PITCH_PX"] and h["CROSS_DEG"] % 180 != 0, "a second family crossing it, sparser"


def test_the_hatch_ink_is_picked_per_ground(dials):
    ps = dials["ps"]
    assert max(ps["INK"]["page"]) <= 20, "on the charcoal page: near-black, deeper than the page"
    assert tuple(ps["INK"]["ground"]) == CHARCOAL, "on a light ground: the template's own charcoal"
    assert ps["ALPHA"]["page"] >= ps["ALPHA"]["ground"] > 0.5, "strong enough to read on either ground"


def test_the_hatch_lies_inside_what_the_stamp_fit_already_keeps_clear(dials):
    """(7) `_stamp_scale` keeps the disc of the painted half-diagonal + STAMP_RING_GAP_PX + STAMP_RING_W_PX clear of
    every obstacle, and `stamp_reserved_box` holds at least that disc for the row's other docks. The hatch of the
    turned mark, at every angle it passes through, reaches no further - so the fit already includes it."""
    ps = dials["ps"]
    room = B.STAMP_RING_GAP_PX + B.STAMP_RING_W_PX
    assert _reach(ps) <= room, f"the budget: the hatch reaches {_reach(ps)} px past the painted edge, {room} px kept clear"
    dock = RB.load_surface(SURFACE)[0]["scenes"][0]["docks"][0]
    pl, (p0, p1, p2, p3) = dock["place"], dock["paint"]
    pw, ph = pl["w"] * (p2 - p0), pl["h"] * (p3 - p1)
    cx, cy = pl["x"] + pl["w"] * (p0 + p2) / 2, pl["y"] + pl["h"] * (p1 + p3) / 2
    rp = 0.5 * math.hypot(pw, ph)
    dx, dy = _throw(ps)
    edge = _reach(ps) - ps["OFFSET_PX"]
    lo, hi = B.STAMP_TURN_RANGE
    reach = 0.0
    for i in range(int((hi - lo) / 0.25) + 1):
        a = math.radians(lo + 0.25 * i)
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            x, y = sx * pw / 2, sy * ph / 2
            rx, ry = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
            reach = max(reach, math.hypot(rx + dx, ry + dy) + edge)
    assert reach <= rp + room, f"the hatch reaches {reach - rp:.2f} px past the mark's half-diagonal, {room} kept clear"
    box = B.stamp_reserved_box({**pl, "centre": [cx, cy], "painted": [pw, ph], "ring_to": dock["ring_to"]})
    assert box["x"] <= cx - reach and box["x"] + box["w"] >= cx + reach, (box, cx, reach)
    assert box["y"] <= cy - reach and box["y"] + box["h"] >= cy + reach, (box, cy, reach)


# ---- the frame ----------------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """() => {
  const dock = document.querySelector('.dock[data-slide]');
  const frame = dock ? dock.querySelector('.slide-frame') : null;
  const contact = document.getElementById('dock-contact-0'), hatch = document.getElementById('dock-hatch-0');
  const m = dock ? new DOMMatrix(getComputedStyle(dock).transform === 'none' ? undefined : getComputedStyle(dock).transform) : null;
  return { filter: frame ? getComputedStyle(frame).filter : null, box: dock ? dock.style.boxShadow : null,
           img: dock ? getComputedStyle(dock.querySelector('.slide-frame img')).filter : null,
           deg: m ? Math.atan2(m.b, m.a) * 180 / Math.PI : null,
           contact: contact ? +contact.style.opacity : null, opacity: dock ? +dock.style.opacity : null,
           hatch: hatch ? { opacity: +hatch.style.opacity, under: !!(hatch.compareDocumentPosition(dock) & Node.DOCUMENT_POSITION_FOLLOWING) }
                        : null,
           hatches: document.querySelectorAll('.dock-hatch').length };
}"""

# The hatch canvas's own alpha, and the prop's silhouette drawn INDEPENDENTLY of the painter: the dock's <img> through
# the dock's resolved transform about its resolved origin, thrown (dx, dy) and not - on the hatch canvas's own grid.
PLANES = """([dx, dy]) => {
  const dock = document.querySelector('.dock[data-slide]'), img = dock.querySelector('.slide-frame img');
  const cv = document.getElementById('dock-hatch-0');
  const cs = getComputedStyle(dock), org = cs.transformOrigin.split(' ').map(parseFloat);
  const F = new DOMMatrix().translate(dock.offsetLeft + org[0], dock.offsetTop + org[1])
    .multiply(new DOMMatrix(cs.transform === 'none' ? undefined : cs.transform)).translate(img.offsetLeft - org[0], img.offsetTop - org[1]);
  const bx = parseFloat(cv.style.left), by = parseFloat(cv.style.top), W = cv.width, H = cv.height;
  const off = document.createElement('canvas'); off.width = W; off.height = H; const c = off.getContext('2d');
  const alpha = (d) => { const out = new Uint8Array(W * H); for (let i = 0; i < W * H; i++) out[i] = d[4 * i + 3]; return out; };
  const sil = (sx, sy) => { c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, W, H);
    c.setTransform(F.a, F.b, F.c, F.d, F.e + sx - bx, F.f + sy - by); c.drawImage(img, 0, 0, img.offsetWidth, img.offsetHeight);
    c.setTransform(1, 0, 0, 1, 0, 0); return alpha(c.getImageData(0, 0, W, H).data); };
  const b64 = (u8) => { let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); };
  return { bx, by, W, H, hatch: b64(alpha(cv.getContext('2d').getImageData(0, 0, W, H).data)),
           thrown: b64(sil(dx, dy)), own: b64(sil(0, 0)) };
}"""


def _planes(page, throw) -> dict:
    import numpy as np
    p = page.evaluate(PLANES, list(throw))
    shape = (p["H"], p["W"])
    for k in ("hatch", "thrown", "own"):
        p[k] = np.frombuffer(base64.b64decode(p[k]), dtype=np.uint8).reshape(shape)
    return p


class _Player:
    """One timeline, served and mounted the way the golden harness mounts it."""

    def __init__(self, browser, tl: dict, uris: dict, aspect: str = "16:9"):
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / "p.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.size = RB.STAGE[aspect]
        self._srv, port = RB.serve(html.parent)
        self.page = browser.new_context(viewport={"width": self.size[0], "height": self.size[1]}).new_page()
        self.errors: list[str] = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, *self.size)

    def at(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                           "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE)

    def shot(self, t: float):
        """The rendered stage at t, as luminance (0-255)."""
        import numpy as np
        from PIL import Image
        rgb = np.asarray(Image.open(io.BytesIO(RB.frame_png(self.page, t, self.size))).convert("RGB"), dtype=float)
        return rgb @ np.array([0.2126, 0.7152, 0.0722])

    def close(self) -> None:
        self.page.context.close(); self._srv.shutdown(); self._td.cleanup()


def light_ground(surface: str = SURFACE) -> tuple[dict, dict]:
    """The same stamped prop on a LIGHT ground: the golden's own timeline, its world swapped for a cream plate."""
    tl, uris, _t, _a = RB.load_surface(surface)
    tl, uris = copy.deepcopy(tl), dict(uris)
    tl["scenes"][0]["world"] = {"asset_id": "plate-light", "ken_burns": {"scale": 0, "x": 0, "y": 0}, "sha256": "0" * 64}
    uris["plate-light"] = G.uri("image/png", G.png_solid(64, 36, CREAM))
    return tl, uris


@contextlib.contextmanager
def _browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    try:
        yield br
    finally:
        br.close(); pw.stop()


def _q(t: float) -> float:
    return round(round(t / STEP) * STEP, 2)


def _contrast(player: _Player, t: float, throw) -> dict:
    """(4) On the rendered frame at t: the uncovered shadow (inside the thrown silhouette, outside the mark's own),
    split into LINE pixels (hatch alpha >= 200) and GAP pixels (hatch alpha 0); their mean luminances and counts."""
    player.at(t)
    pl = _planes(player.page, throw)
    lum = player.shot(t)
    ys, xs = pl["by"], pl["bx"]
    frame = lum[int(ys):int(ys) + pl["H"], int(xs):int(xs) + pl["W"]]
    free = (pl["thrown"] == 255) & (pl["own"] == 0)
    line, gap = free & (pl["hatch"] >= 200), free & (pl["hatch"] == 0)
    return {"line": float(frame[line].mean()) if line.any() else None, "gap": float(frame[gap].mean()) if gap.any() else None,
            "n_line": int(line.sum()), "n_gap": int(gap.sum())}


@pytest.fixture(scope="module")
def frames(dials):
    """Every instant read through ONE browser: the `own` surface on every scrub step from the frame after the contact
    to 0.3 s past the settle, at the turn and at rest (with the planes); the `page`-ink surface and the light ground
    at rest (with their contrast); a card at its own instant."""
    contact, settle = _stamp_clock()
    throw = _throw(dials["ps"])
    t0, t1 = _q(ENTER + contact + STEP), _q(ENTER + settle + 0.30)
    sweep = [round(t0 + STEP * i, 2) for i in range(int(round((t1 - t0) / STEP)) + 1)]
    with _browser() as br:
        players = []
        try:
            tl, uris, _t, _a = RB.load_surface(SURFACE)
            own = _Player(br, tl, uris); players.append(own)
            tl, uris, _t, _a = RB.load_surface("prop-stamp-ink")
            inked = _Player(br, tl, uris); players.append(inked)
            light = _Player(br, *light_ground()); players.append(light)
            tl, uris, t_card, _a = RB.load_surface(CARD_SURFACE)
            card = _Player(br, tl, uris); players.append(card)
            out = {"contact": ENTER + contact, "settle": ENTER + settle,
                   "sweep": [(t, own.at(t)) for t in sweep]}
            out["turn"] = own.at(T_TURN); out["turn_planes"] = _planes(own.page, throw)
            out["rest"] = own.at(T_REST); out["rest_planes"] = _planes(own.page, throw)
            out["page_contrast"] = _contrast(own, T_REST, throw)
            out["ink"] = inked.at(T_REST); out["ink_contrast"] = _contrast(inked, T_REST, throw)
            out["light"] = light.at(T_REST); out["light_contrast"] = _contrast(light, T_REST, throw)
            out["card"] = card.at(t_card)
            for pl in players:
                assert not pl.errors, pl.errors
            yield out
        finally:
            for pl in players:
                pl.close()


@needs_browser
def test_a_SETTLED_prop_carries_a_HATCH_layer_under_it_and_no_box(frames, dials):
    """(1) On the charcoal page at rest: the hatch canvas, beneath the mark, at the ground's full alpha - and no box
    and no filter anywhere on the dock."""
    rest = frames["rest"]
    assert rest["hatch"] is not None, "no hatch layer on the settled prop"
    assert rest["hatch"]["under"], "the hatch paints BENEATH the mark, in the dock layer"
    assert abs(rest["hatch"]["opacity"] - dials["ps"]["ALPHA"]["page"]) < 0.005, rest["hatch"]
    assert rest["box"] == "none", "a prop casts no card's lift"
    assert rest["filter"] == "none", "the soft drop-shadow is gone: the weight is the engraving"


@needs_browser
def test_the_hatch_is_MASKED_by_the_props_own_silhouette_thrown_along_the_light(frames):
    """(2) Every inked hatch pixel lies inside the prop's painted alpha thrown along the light's fall; and the hatch
    covers that silhouette - it is not a sliver of a box."""
    pl = frames["rest_planes"]
    ink = pl["hatch"] > 0
    stray = int((ink & (pl["thrown"] == 0)).sum())
    assert stray <= 0.001 * int(ink.sum()), f"{stray} hatch pixels outside the thrown silhouette"
    inside = pl["thrown"] == 255
    share = float(ink[inside].mean())
    assert share > 0.2, f"the hatch inks {share:.2%} of the silhouette's interior - too sparse to read as a shadow"


@needs_browser
def test_the_hatch_is_FIXED_TO_THE_PAGE_while_the_silhouette_follows_the_mark(frames):
    """(3) At T_TURN the mark is still turning, 2.4 deg off its rest; at T_REST it is off-square at rest. On every stage
    pixel inside both thrown silhouettes the hatch is ON or OFF alike - an engraving's lines do not spin with the thing
    they shade. The check is shown to bite: the same hatch turned WITH the mark by that 2.4 deg agrees on ~52 %.
    (On/off, not byte equality: the canvas is sized to the silhouette's bounds, and a line clipped to a different
    rectangle re-rounds its antialiased edge by a few levels - measured 2026-09-23, 99.2 % on/off agreement.)"""
    import numpy as np
    from PIL import Image
    turn, rest = frames["turn"], frames["rest"]
    turned = turn["deg"] - rest["deg"]
    assert abs(turned) >= 1.5, f"the mark must have turned between the two reads: {turn['deg']} vs {rest['deg']}"
    a, b = frames["turn_planes"], frames["rest_planes"]
    x0, y0 = max(a["bx"], b["bx"]), max(a["by"], b["by"])
    x1, y1 = min(a["bx"] + a["W"], b["bx"] + b["W"]), min(a["by"] + a["H"], b["by"] + b["H"])
    cut = lambda p, k: p[k][int(y0 - p["by"]):int(y1 - p["by"]), int(x0 - p["bx"]):int(x1 - p["bx"])]  # noqa: E731
    both = (cut(a, "thrown") == 255) & (cut(b, "thrown") == 255)
    assert both.sum() > 10000, "the two silhouettes overlap enough to compare"
    ha, hb = cut(a, "hatch"), cut(b, "hatch")
    agree = float(((ha >= 128) == (hb >= 128))[both].mean())
    spun = np.asarray(Image.fromarray(hb).rotate(-turned, resample=Image.BILINEAR, center=(hb.shape[1] / 2, hb.shape[0] / 2)))
    spun_agree = float(((ha >= 128) == (spun >= 128))[both].mean())
    print(f"\nhatch on/off agreement: page-fixed {agree:.4f}, turned with the mark {spun_agree:.4f}")
    assert agree >= 0.97, f"the hatch moved with the mark: only {agree:.2%} of pixels agree"
    assert spun_agree <= 0.8, f"the check cannot tell a spinning hatch: {spun_agree:.2%}"


@needs_browser
@pytest.mark.parametrize("which,ground", [("page_contrast", "page"), ("ink_contrast", "page"), ("light_contrast", "ground")])
def test_the_hatch_READS_as_texture_on_both_grounds(frames, which, ground):
    """(4) The texture is visible: in the shadow the mark does not cover, the gaps between the lines are brighter than
    the lines by CONTRAST_MIN[ground] luminance levels - 20 on the charcoal page, 60 on a light ground."""
    c = frames[which]
    assert c["n_line"] > 300 and c["n_gap"] > 300, f"the uncovered shadow is too small to read: {c}"
    got = c["gap"] - c["line"]
    print(f"\n{which}: gap {c['gap']:.1f} - line {c['line']:.1f} = {got:.1f} levels (min {CONTRAST_MIN[ground]}), "
          f"{c['n_line']} line px, {c['n_gap']} gap px")
    assert got >= CONTRAST_MIN[ground], f"{which}: the lines differ from the gaps by only {got:.1f} levels"


@needs_browser
def test_the_CONTACT_hands_over_to_the_HATCH_at_settle_with_no_pop(frames, dials):
    """(5) From the contact to past the settle, one sample per scrub step: neither shadow jumps between two frames,
    the contact is 0 and the hatch full from the settle on, and the weight - the two shares summed - never drops out."""
    full = dials["ps"]["ALPHA"]["page"]
    rows = [(t, p["contact"] or 0.0, (p["hatch"] or {}).get("opacity", 0.0) / full) for t, p in frames["sweep"]]
    c0 = rows[0][1]
    assert c0 > 0.5, f"at the contact the mark presses on its contact shadow: {c0}"
    pops = [(b[0], round(b[1] - a[1], 3)) for a, b in zip(rows, rows[1:]) if abs(b[1] - a[1]) >= 0.03]
    assert not pops, f"the contact shadow pops between two frames: {pops}"
    pops = [(b[0], round(b[2] - a[2], 3)) for a, b in zip(rows, rows[1:]) if abs(b[2] - a[2]) >= 0.04]
    assert not pops, f"the hatch pops between two frames: {pops}"
    after = [r for r in rows if r[0] >= frames["settle"] + STEP]
    assert after and all(r[1] == 0 for r in after), "from the settle on, the contact is spent"
    assert all(abs(r[2] - 1) < 0.005 for r in after), f"... and the hatch holds at full: {after[:3]}"
    weight = [r[1] / c0 + r[2] for r in rows]
    assert min(weight) > 0.95, f"the weight dips to {min(weight):.3f} mid-handover"


@needs_browser
def test_a_CARD_creates_no_hatch_and_keeps_its_own_shadow(frames):
    """(6) The paper dock is untouched: no hatch layer, no filter on its frame, its own hard offset lift."""
    card = frames["card"]
    assert card["hatches"] == 0, "a card never creates a hatch layer"
    assert card["filter"] in ("none", None, ""), card["filter"]
    assert card["box"] and card["box"] != "none", "a card keeps its lift"
