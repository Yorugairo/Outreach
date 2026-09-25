"""P72 T11 (E99 s130 (2)): a seal's gold on the ground MEASURED under it, read in the player.

chip.test.mjs pins the law (sealGoldOn / sealGoldReport, the contact latch) with the engine's readers stubbed; these
tests run the real engine in Chromium:

- THE LATCH: the seal-on-photo golden's source with a strong Ken Burns authored on its plate - the world pushes and
  slides under the seal for its whole life - read at the approach, the contact, the squash, the rest and the exit.
  The gold is fixed once, from the ground as the world stood at the contact, so every instant names ONE gold.
- THE FLOOR IS ON THE INK: the committed seal-on-photo frame's outer ring as composited (the ink eases to 0.86 at
  rest, s121 (4)) against the plate just outside it, printed as INFO; the INK holds CONTRAST_MIN at the worst sample
  the seal names (its data-ground-* attributes), the pixel is reported, not floored (acceptance (2) keeps the cream
  seal at #A07F4B, which composites to 2.5:1).
"""
from __future__ import annotations

import copy
import io
import math
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import render_baseline as RB  # noqa: E402

CONTRAST_MIN = 3.0
KEN_BURNS = {"scale": 0.3, "x": -150, "y": 60}   # a strong push and slide: the plate moves ~30 px under the seal in its life

PROBE = """() => {
  const st = document.getElementById('stage').getBoundingClientRect(), seal = document.querySelector('.chipseal');
  if (!seal) return null;
  const tr = /translate\\(([-0-9.]+) ([-0-9.]+)\\)/.exec(seal.parentNode.getAttribute('transform'));
  const a = (k) => seal.getAttribute(k);
  return { stroke: a('stroke'), opacity: +a('opacity'), r: +a('r'), cx: +tr[1], cy: +tr[2],
           min: a('data-ground-min'), max: a('data-ground-max'), worst: a('data-ground-worst'), holds: a('data-ground-holds'),
           world: document.getElementById('wB').style.transform };
}"""


def _chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _chromium(), reason="needs Playwright Chromium")


def _source(ken_burns: dict | None = None) -> tuple[dict, dict]:
    import build_golden_sources as G
    tl, uris = G._chip_stamp(True, ring=True, ground=(G.SEAL_PHOTO_PLATE, G.png_photo(240, 135, G.SEAL_PHOTO_BASE)))
    tl = copy.deepcopy(tl)
    if ken_burns:
        tl["scenes"][0]["world"]["ken_burns"] = dict(ken_burns)
    return tl, uris


def _read(tl: dict, uris: dict, ts: list[float]) -> list[tuple[float, bytes, dict]]:
    import served_player as SP  # R26-351 (P72 T9): the one guarded Playwright start
    out = []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "seal.html"
        html.write_text(RB.instantiate(tl, uris, RB.TEMPLATE), encoding="utf-8")
        with SP.served(html, 1920, 1080) as (page, _errs):
            for t in ts:
                png = RB.frame_png(page, t, (1920, 1080))
                out.append((t, png, page.evaluate(PROBE)))
    return out


def _lum(c) -> float:
    v = [x / 255 for x in c[:3]]
    v = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def _con(a: float, b: float) -> float:
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def test_the_seals_gold_is_fixed_at_its_contact_and_held_under_ken_burns():
    import build_golden_sources as G
    tl, uris = _source(KEN_BURNS)
    at, dur = G.CHIP_STAMP_ENTRY["at"], G.CHIP_STAMP_ENTRY["dur"]
    tc = at + G._STAMP_CONTACT_S
    ts = [round(at + 0.05, 3), round(tc, 3), round(tc + 0.04, 3), round(at + 0.6, 3), round(at + 1.3, 3),
          round(at + 3.0, 3), round(at + 5.0, 3), round(at + dur - 0.25, 3)]
    rows = _read(tl, uris, ts)
    golds = {r[2]["stroke"] for r in rows if r[2]}
    worlds = {r[2]["world"] for r in rows if r[2]}
    for t, _, p in rows:
        print(f"INFO t {t}: seal {p and p['stroke']} | ground {p and p['min']}..{p and p['max']} worst {p and p['worst']} "
              f"holds {p and p['holds']} | world {p and p['world']}")
    assert len([r for r in rows if r[2]]) == len(ts), "the seal is drawn at every instant of its life"
    assert len(worlds) == len(ts), "Ken Burns moves the plate under the seal at every instant read"
    assert len(golds) == 1, f"one gold for the seal's life under Ken Burns: {golds}"
    assert {r[2]["worst"] for r in rows} == {rows[0][2]["worst"]}, "... from one measure (the contact's)"


def test_the_floor_is_on_the_ink_and_the_composited_ring_is_reported():
    import build_golden_sources as G
    from PIL import Image
    tl, uris = _source()
    t = G.FRAME_T["seal-on-photo"]
    ((_, png, p),) = _read(tl, uris, [t])
    golden = (ROOT / "content/video_engine/tests/golden/frames/seal-on-photo.png").read_bytes()
    assert png == golden, "the frame read is the committed seal-on-photo golden"
    im = Image.open(io.BytesIO(png)).convert("RGB")
    ink = _lum([int(p["stroke"][i:i + 2], 16) for i in (1, 3, 5)])
    ring, out = [], []
    for i in range(16):
        a = 2 * math.pi * i / 16
        ring.append(_lum(im.getpixel((round(p["cx"] + p["r"] * math.cos(a)), round(p["cy"] + p["r"] * math.sin(a))))))
        out.append(_lum(im.getpixel((round(p["cx"] + (p["r"] + 12) * math.cos(a)), round(p["cy"] + (p["r"] + 12) * math.sin(a))))))
    composited = sorted(_con(x, y) for x, y in zip(ring, out))
    worst_ink = min(_con(ink, float(p["min"])), _con(ink, float(p["max"])))
    print(f"INFO seal-on-photo: ink {p['stroke']} {worst_ink:.2f}:1 at the worst measured ground ({p['min']}..{p['max']}), "
          f"named {p['worst']} | composited ring (opacity {p['opacity']}) vs the plate beside it: median "
          f"{composited[len(composited) // 2]:.2f}:1, min {composited[0]:.2f}:1")
    assert p["holds"] == "1" and float(p["worst"]) >= CONTRAST_MIN, "the INK holds the floor at the worst sample"
    assert worst_ink >= CONTRAST_MIN - 0.005
    assert composited[len(composited) // 2] < float(p["worst"]), "the pixel is reported, not floored (the floor is on the ink)"
