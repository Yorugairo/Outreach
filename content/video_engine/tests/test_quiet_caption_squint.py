"""P71 T8b - THE QUIET CAPTION READS AT THE SQUINT (E99 s126 (2); found by P71 T7, left to this slice by P72 T14).

M48 (the squint gate, P71 T7) FAILs the committed H door on its captions: every one of its cap faults is a QUIET
caption - the long form's anchored strip at 33 px / 600, whose cap reads 4.00-4.21 px at 320 px wide against the
reference's 4.285 (Wealth Logic's burned-in strip, `caption-squint-floor.v1.json`, n = 82; E38: the floor is the
reference's, never one fitted to ours) - and every contrast fault is a quiet caption too (down to 1.79 against 3.97:
the strip's pale words and soft shadow on a cream ledger page or a bright plate). The stage captions all pass.

Owed, and pinned here on the frames, read by M48's own caption read (`measure_line_bloom.caption_read`) at 320 px:

  THE SIZE      the landscape quiet strip takes the anchored strip's own size (the template's `#caption`, 40 px)
                at the stage caption's weight (800) - it stays one line inside the strip
                `ledger_page.CAPTION_ANCHOR["16:9"]` (878-960), so no page layout kept clear of the strip moves;
  THE CONTRAST  the strip's words carry the reference's own form, a dark STROKE in the text shadow (Wealth Logic's
                white caps in a black stroke) - doc 29 Part 5: "transparent glyphs + text shadow; no pill, no
                panel", so never a box - on every world, since the strip crosses a page, a plate and a map alike;
  THE SHORTS    the 9:16 quiet strip (48 px / 800, E62) is not this slice's: it paints exactly what it painted.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import measure_line_bloom as MLB  # noqa: E402
import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

TEMPLATE = (ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html").read_text(encoding="utf-8")
FLOOR_FILE = ROOT / "content/video_engine/assets/caption-squint-floor.v1.json"
WORDS = ["The", "desk", "held", "Tuesday", "night."]
LONGEST = "but the paper that financed it was".split()   # 34 characters - H's longest caption page
PAGE_S = 2.0
T_READ = PAGE_S + 2.4      # every word written, the page still up (M48 reads a page once its last word is written)


def _chromium_available() -> bool:
    try:
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

CAP_PROBE = """() => {
  const sb = document.getElementById('stage').getBoundingClientRect(), cap = document.getElementById('caption');
  const R = (r) => [r.left - sb.left, r.top - sb.top, r.right - sb.left, r.bottom - sb.top];
  const ws = [...cap.querySelectorAll('.cw')].filter((w) => w.getBoundingClientRect().width > 0);
  let u = null;
  for (const w of ws) { const r = R(w.getBoundingClientRect());
    u = u ? [Math.min(u[0], r[0]), Math.min(u[1], r[1]), Math.max(u[2], r[2]), Math.max(u[3], r[3])] : r; }
  const cs = getComputedStyle(cap);
  return { cls: cap.className, box: u, words: ws.map((w) => [R(w.getBoundingClientRect()), w.textContent]),
           strip: R(cap.getBoundingClientRect()), fontSize: cs.fontSize, fontWeight: cs.fontWeight,
           shadow: cs.textShadow, inline: cap.style.textShadow, background: cs.backgroundColor,
           lines: new Set(ws.map((w) => Math.round(w.getBoundingClientRect().top))).size };
}"""


def _pages(words: list[str]) -> list[dict]:
    """One caption page the strip holds: `cap_reserve: readable-species` pins it to the anchored strip (the quiet
    class, R26-235) on any world - the page H's ledger rows reach through `page.caption: anchor`."""
    return [{"s": PAGE_S, "e": PAGE_S + 3.0, "cap_mode": "anchor", "cap_reserve": "readable-species",
             "t": [{"w": w, "k": j == 1, "s": round(PAGE_S + 0.3 * j, 2), "e": round(PAGE_S + 0.3 * j + 0.28, 2)}
                   for j, w in enumerate(words)]}]


def _plate_tl(rgb: tuple, aspect: str = "16:9", words: list[str] = WORDS) -> tuple[dict, dict]:
    uris = G._base_uris()
    uris["plate-test"] = G.uri("image/png", G.png_solid(64, 36, rgb))
    world = {"asset_id": "plate-test", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
    tl = G._timeline("quiet caption", scenes, {}, aspect)
    tl["caption_pages"], tl["captions"] = _pages(words), []
    return json.loads(json.dumps(tl)), uris


def _page_tl() -> tuple[dict, dict]:
    """A 16:9 LEDGER PAGE row as the compiler stamps it (R26-205: `caption: anchor` on every 16:9 page row) - the
    cream page H's 56 ledger contrast faults stood on."""
    tl, uris = G.ledger_page_mid_build()
    tl["scenes"][0]["world"]["page"]["caption"] = "anchor"
    tl["caption_pages"] = [{k: v for k, v in p.items() if k != "cap_reserve"} for p in _pages(WORDS)]
    tl["captions"] = []
    return json.loads(json.dumps(tl)), uris


class _Player:
    def __init__(self, browser, tl: dict, uris: dict):
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / "p.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.size = RB.STAGE[tl.get("aspect") or "16:9"]
        self._srv, port = RB.serve(html.parent)
        self.page = browser.new_context(viewport={"width": self.size[0], "height": self.size[1]}).new_page()
        self.errors: list[str] = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, *self.size)

    def read(self, t: float) -> tuple[dict, bytes]:
        png = RB.frame_png(self.page, t, self.size)
        return self.page.evaluate(CAP_PROBE), png

    def close(self) -> None:
        self.page.context.close(); self._srv.shutdown(); self._td.cleanup()


def _read(tl: dict, uris: dict, t: float = T_READ) -> tuple[dict, bytes, list]:
    with SP.browser() as br:
        pl = _Player(br, tl, uris)
        try:
            got, png = pl.read(t)
            return got, png, list(pl.errors)
        finally:
            pl.close()


def _m48(png: bytes, got: dict, text: str) -> dict:
    """M48's own caption read (measure_line_bloom._caption_rec's grow of the box and the words)."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "f.png"
        p.write_bytes(png)
        grow = lambda b, k: [b[0] - k, b[1] - k, b[2] + k, b[3] + k]   # noqa: E731
        return MLB.caption_read(p, grow(got["box"], 4), text, words=[(grow(b, 3), w) for b, w in got["words"]])


def _floor() -> dict:
    return json.loads(FLOOR_FILE.read_text(encoding="utf-8"))["lanes"]["16:9"]


CREAM = (236, 229, 214)     # a pale cream wall - H row 17's desk
MID = (128, 128, 128)       # a mid-grey ground: pale words hold least against it
CHARCOAL = (43, 52, 60)     # the golden plate's own colour


@needs_browser
@pytest.mark.parametrize("world", ["cream plate", "mid-grey plate", "charcoal plate", "ledger page"])
def test_the_quiet_strip_reads_at_the_references_floor_on_every_world(world):
    """The acceptance on the frame: the landscape quiet strip holds Wealth Logic's caption floor at 320 px - its
    cap AND its contrast - over a bright plate, a mid ground, a dark plate and a cream ledger page."""
    tl, uris = _page_tl() if world == "ledger page" else _plate_tl(
        {"cream plate": CREAM, "mid-grey plate": MID, "charcoal plate": CHARCOAL}[world])
    got, png, errs = _read(tl, uris)
    assert errs == []
    assert "quiet" in got["cls"].split() and "stage" not in got["cls"].split(), got["cls"]
    r, fl = _m48(png, got, " ".join(WORDS)), _floor()
    assert r["cap_px"] is not None and r["cap_px"] >= fl["cap_px"]["min"], (world, r, fl["cap_px"])
    assert r["contrast"] >= fl["contrast"]["min"], (world, r, fl["contrast"])


@needs_browser
def test_the_quiet_strip_is_a_text_shadow_never_a_box_and_takes_no_inline_backing():
    """doc 29 Part 5: transparent glyphs + text shadow, no pill, no panel. The stroke is the template's class rule
    (the same on every world); P72 T14's measured inline backing stays the STAGE caption's."""
    got, _png, errs = _read(*_plate_tl(CREAM))
    assert errs == []
    assert got["background"] in ("rgba(0, 0, 0, 0)", "transparent"), got["background"]
    assert got["inline"] == "", "the inline backing is the stage caption's (P72 T14)"
    assert got["shadow"].count("rgb") >= 4, ("a stroke: the dark shadow ringing the glyph", got["shadow"])


@needs_browser
def test_the_longest_page_stays_one_line_inside_the_anchored_strip():
    """E41's pages are untouched (the pager is not this slice's) and the strip keeps its box: H's longest page (34
    characters) is ONE line at the new size, inside CAPTION_ANCHOR["16:9"] - so no page layout kept clear of the strip
    (the x ticks, the source line, the key rail) moves."""
    got, _png, errs = _read(*_plate_tl(CHARCOAL, words=LONGEST))
    assert errs == []
    x, y, w, h = LPG.CAPTION_ANCHOR["16:9"]
    assert got["lines"] == 1, got
    assert y - 0.5 <= got["box"][1] and got["box"][3] <= y + h + 0.5, (got["box"], (x, y, w, h))
    assert x <= got["box"][0] and got["box"][2] <= x + w, (got["box"], (x, y, w, h))


@needs_browser
def test_the_shorts_quiet_strip_paints_exactly_what_it_painted():
    """The 9:16 quiet strip is E62's (48 px / 800 in the safe box) and has no reference floor yet (M48's INFO):
    its size, weight and shadow are the base's to the string."""
    got, _png, errs = _read(*_plate_tl(CREAM, aspect="9:16"))
    assert errs == []
    assert "quiet" in got["cls"].split()
    assert (got["fontSize"], got["fontWeight"]) == ("48px", "800"), got
    assert got["shadow"] == "rgba(0, 0, 0, 0.94) 0px 2px 14px, rgba(0, 0, 0, 0.85) 0px 0px 5px", got["shadow"]


def test_the_landscape_quiet_rule_is_scoped_off_the_shorts():
    """The stroke is declared for the landscape strip only - a 9:16 player never matches it."""
    assert 'html:not([data-aspect="9:16"]) #caption.quiet' in TEMPLATE


def test_the_strips_stroke_is_the_stage_backings_at_full_strength():
    """One form of contrast in the long form's captions: the quiet strip's stroke is P72 T14's measured backing
    (engine CAPTION_BACKING: its stroke reach, core and halo in em, its ink) at k = 1 - the two cannot drift apart."""
    import re
    engine = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")
    blk = engine[engine.index("const CAPTION_BACKING = Object.freeze({"):]
    blk = blk[:blk.index("});")]
    stroke = float(re.search(r"STROKE_EM:\s*([0-9.]+)", blk).group(1))
    core, halo = (float(v) for v in re.search(r"HALO_EM:\s*\[([0-9.]+),\s*([0-9.]+)\]", blk).groups())
    ink = re.search(r'INK:\s*"([0-9,]+)"', blk).group(1)
    rule = TEMPLATE[TEMPLATE.index('html:not([data-aspect="9:16"]) #caption.quiet {'):]
    rule = rule[:rule.index("}")].replace(" ", "")
    fmt = lambda v: f"{v:g}".lstrip("0")   # noqa: E731 - CSS writes .1em
    assert f"{fmt(stroke)}em00rgb({ink})" in rule, (stroke, ink, rule)
    assert f"-{fmt(round(stroke * 0.7071, 4))}em-{fmt(round(stroke * 0.7071, 4))}em0rgb({ink})" in rule, rule
    assert rule.count(f"00{fmt(core)}emrgb({ink})") == 2, "the core, painted twice"
    assert f"00{fmt(halo)}emrgba({ink},.85)" in rule, rule
