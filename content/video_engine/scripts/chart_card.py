"""CHART CARD (R26-19 / E50, 2026-09-07): a ledger page rendered once, at its landing, to a PNG that docks as a card.

A fresh ledger page needs ~7.4 s to land its chart (ROLL + SAVOR + FIELD + PUNCH + BUILD), so a 2-3 s beat cannot carry a
new page. A CARD can: the page is compiled from its series object by ledger_page.py, instantiated in the player on the
golden ledger skeleton, seeked to its landing, and the page's own rectangle is screenshotted - the same painter, the same
fonts, the same chalk - then the card is thrown or landed onto the page like any dock (stopaction). The card is a CHART
dock (species "chart"): M11/M12's rules apply to it - it proves one sentence and leaves (E25).

    python content/video_engine/scripts/chart_card.py <series.json> <out.png> [--variant line] [--emphasize N] [--width 720] [--t 8.6]
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render_baseline as RB  # noqa: E402

SKELETON = "ledger-soak-page"   # the golden one-scene ledger timeline: its world.page is replaced by ours (16:9); a portrait card sets aspect 9:16 on it
LAND_T = 8.6                    # ROLL .7 + SAVOR .8 + FIELD 2.4 + PUNCH .5 + BUILD 3.0 = 7.4, plus the badges' settle


def page_spec(series: Path, variant: str, emphasize: int | None, quiet_zone: str = "right") -> dict:
    """ledger_page.py's spec for the object - the compiler's own path, never a hand-built page."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "card.page.json"
        cmd = [sys.executable, str(HERE / "ledger_page.py"), str(series), "--variant", variant, "--quiet-zone", quiet_zone, "--out", str(out)]
        if emphasize is not None:
            cmd += ["--emphasize", str(emphasize)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return json.loads(out.read_text(encoding="utf-8"))


def page_box(im) -> tuple[int, int, int, int]:
    """The charcoal page's bounding box on the rendered stage: the run of dark, low-saturation pixels (the page's ground)
    that is neither the stage's black nor the cream deckle. Scans the middle row and column."""
    px = im.load(); W, H = im.size
    def is_page(p):
        r, g, b = p; return 18 <= r <= 60 and 24 <= g <= 70 and 30 <= b <= 90 and b >= r
    cy, cx = H // 2, W // 2
    xs = [x for x in range(W) if is_page(px[x, cy])]
    ys = [y for y in range(H) if is_page(px[cx, y])]
    if not xs or not ys:
        return 0, 0, W, H
    return xs[0], ys[0], xs[-1] - xs[0] + 1, ys[-1] - ys[0] + 1


def render_card(series: Path, out: Path, variant: str = "line", emphasize: int | None = None, width: int = 720, t: float = LAND_T,
                aspect: str | None = None, quiet_zone: str = "right") -> Path:
    """`aspect` 9:16 renders the PORTRAIT page (the layout a short's live page takes), so a card that later SNAPS up to become
    the world matches it to the pixel; the default keeps the skeleton's own 16:9."""
    from PIL import Image
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect0 = RB.load_surface(SKELETON)
    aspect = aspect or aspect0
    sc = tl["scenes"][0]
    page = page_spec(series, variant, emphasize, quiet_zone)
    scenes = [dict(sc, species=[], docks=[], world=dict(sc["world"], page=page, ken_burns={"scale": 0, "x": 0, "y": 0}))]
    tl2 = dict(tl, aspect=aspect, scenes=scenes, caption_pages=[], captions=[], kinetics=dict(tl.get("kinetics") or {}, idle=False))
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "card.html"
        html.write_text(RB.instantiate(tl2, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                b = pw.chromium.launch(headless=True)
                pg = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2).new_page()
                pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(pg, w, h)
                pg.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                png = RB.frame_png(pg, t, (w, h))
                b.close()
        finally:
            srv.shutdown()
    im = Image.open(io.BytesIO(png)).convert("RGB")
    x, y, pw_, ph = page_box(im)   # the charcoal page's own rectangle, found on the pixels (device_scale_factor 2: crisp at dock size)
    card = im.crop((x, y, x + pw_, y + ph))
    card = card.resize((width, round(ph * width / pw_)), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    card.save(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("series"); ap.add_argument("out")
    ap.add_argument("--variant", default="line"); ap.add_argument("--emphasize", type=int, default=None)
    ap.add_argument("--width", type=int, default=720); ap.add_argument("--t", type=float, default=LAND_T)
    ap.add_argument("--aspect", default=None, choices=[None, "16:9", "9:16"])
    a = ap.parse_args()
    p = render_card(Path(a.series), Path(a.out), a.variant, a.emphasize, a.width, a.t, a.aspect)
    from PIL import Image
    print(f"card {p} {Image.open(p).size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
