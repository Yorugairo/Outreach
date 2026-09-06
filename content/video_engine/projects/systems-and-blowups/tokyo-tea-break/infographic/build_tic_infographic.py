"""The TIC Table 5 infographic for the Tokyo Tea Break post - the light (ledger-page) version.

One page proves one sentence: Japan sold a tenth of its Treasuries in four months, and the auction sets
your price. Cream ground, charcoal ink, coral for the drop, one sunflower callout, one cobalt block
(brand-tokens.json). Every figure is a TIC Table 5 row fetched 2026-09-06; nothing is typed in from memory.

    python build_tic_infographic.py            # writes the HTML files and renders the PNGs
    python build_tic_infographic.py --no-render

Outputs, beside this file: tic-table5-light-4x5.html/.png (1080x1350, the feed),
tic-table5-light-9x16.html/.png (1080x1920, the story).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- the data: TIC Table 5, https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.txt
# fetched 2026-09-06 (the June 2026 print). Billions of dollars, holdings at month end, oldest first.
MONTHS = ["Jun '25", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec '25", "Jan '26", "Feb", "Mar", "Apr", "May", "Jun '26"]
JAPAN = [1154.8, 1155.4, 1183.9, 1189.3, 1200.0, 1202.7, 1185.5, 1225.3, 1239.3, 1191.6, 1209.9, 1143.1, 1116.7]
PEAK_I, LAST_I = 8, 12
HOLDERS = [("Japan", 1116.7), ("United Kingdom", 939.9), ("China", 633.4)]
FETCHED = "2026-09-06"
SOURCE_URL = "ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.txt"

DROP = round(JAPAN[PEAK_I] - JAPAN[LAST_I], 1)          # 122.6
DROP_PCT = round(100 * DROP / JAPAN[PEAK_I], 1)          # 9.9
assert DROP == 122.6 and DROP_PCT == 9.9, (DROP, DROP_PCT)

# --- the tokens (channel-assets/money-physics/brand-tokens.json)
CREAM, CHARCOAL, COBALT, CORAL, SUNFLOWER = "#F4E6C7", "#25313C", "#1769C2", "#ED6A4A", "#F5B72E"
INK_SOFT = "rgba(37,49,60,.62)"
GRID = "rgba(37,49,60,.16)"


def fmt_b(v: float) -> str:
    return f"${v:,.1f}B"


def line_chart(w: int, h: int) -> str:
    """The 13-month line: charcoal to the peak, coral after it; two halo labels; one sunflower bracket."""
    pad_l, pad_r, pad_t, pad_b = 96, 250, 56, 64
    x0, x1, y0, y1 = pad_l, w - pad_r, pad_t, h - pad_b
    lo, hi = 1100.0, 1250.0
    ticks = [1100, 1150, 1200, 1250]

    def X(i: int) -> float:
        return x0 + (x1 - x0) * i / (len(JAPAN) - 1)

    def Y(v: float) -> float:
        return y1 - (y1 - y0) * (v - lo) / (hi - lo)

    pts = [(X(i), Y(v)) for i, v in enumerate(JAPAN)]
    path_up = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts[: PEAK_I + 1])
    path_down = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts[PEAK_I:])
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Japan holdings of U.S. Treasuries, June 2025 to June 2026">']
    # grid + y ticks (Kalam, the ledger hand)
    for t in ticks:
        y = Y(t)
        out.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1.5"/>')
        out.append(f'<text x="{x0 - 14}" y="{y + 8:.1f}" text-anchor="end" class="hand tick">{t:,}</text>')
    # x labels, every month (Kalam)
    for i, m in enumerate(MONTHS):
        if i in (0, 2, 4, 6, 8, 10, 12):
            out.append(f'<text x="{X(i):.1f}" y="{y1 + 34}" text-anchor="middle" class="hand tick">{m}</text>')
    # the lines
    out.append(f'<path d="{path_up}" fill="none" stroke="{CHARCOAL}" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append(f'<path d="{path_down}" fill="none" stroke="{CORAL}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>')
    # the two datum points with halo labels (paint-order: stroke fill; stroke = the page colour)
    px, py = pts[PEAK_I]
    lx, ly = pts[LAST_I]
    out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="{CHARCOAL}"/>')
    out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="8" fill="{CORAL}"/>')
    out.append(f'<text x="{px:.1f}" y="{py - 20:.1f}" text-anchor="middle" class="hand label halo">Feb 2026 &#183; {fmt_b(JAPAN[PEAK_I])}</text>')
    out.append(f'<text x="{lx - 16:.1f}" y="{ly + 44:.1f}" text-anchor="end" class="hand label halo coral">Jun 2026 &#183; {fmt_b(JAPAN[LAST_I])}</text>')
    # the one sunflower callout: a bracket at the right from the peak level to the June level
    bx = x1 + 34
    out.append(f'<line x1="{bx}" y1="{py:.1f}" x2="{bx}" y2="{ly:.1f}" stroke="{SUNFLOWER}" stroke-width="6" stroke-linecap="round"/>')
    out.append(f'<line x1="{bx - 10}" y1="{py:.1f}" x2="{bx + 10}" y2="{py:.1f}" stroke="{SUNFLOWER}" stroke-width="4" stroke-linecap="round"/>')
    out.append(f'<line x1="{bx - 10}" y1="{ly:.1f}" x2="{bx + 10}" y2="{ly:.1f}" stroke="{SUNFLOWER}" stroke-width="4" stroke-linecap="round"/>')
    my = (py + ly) / 2
    out.append(f'<text x="{bx + 22}" y="{my - 6:.1f}" class="hand callout">&#8722;{fmt_b(DROP)}</text>')
    out.append(f'<text x="{bx + 22}" y="{my + 26:.1f}" class="hand callout-sub">a tenth of the pile</text>')
    out.append("</svg>")
    return "\n".join(out)


def bar_chart(w: int, h: int) -> str:
    """Three bars: the biggest lender, more than the UK or China. Values on the bar end, haloed."""
    label_w, pad_r, row_h, gap = 250, 170, 46, 16
    top = 8
    scale = (w - label_w - pad_r) / HOLDERS[0][1]
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Top three foreign holders of U.S. Treasuries, June 2026">']
    for i, (name, v) in enumerate(HOLDERS):
        y = top + i * (row_h + gap)
        bw = v * scale
        fill = CHARCOAL if i == 0 else INK_SOFT
        out.append(f'<text x="{label_w - 18}" y="{y + row_h / 2 + 9:.1f}" text-anchor="end" class="hand barlabel">{name}</text>')
        out.append(f'<rect x="{label_w}" y="{y}" width="{bw:.1f}" height="{row_h}" fill="{fill}" rx="3"/>')
        out.append(f'<text x="{label_w + bw + 16:.1f}" y="{y + row_h / 2 + 10:.1f}" class="hand barvalue halo">{fmt_b(v)}</text>')
    out.append("</svg>")
    return "\n".join(out)


def page(w: int, h: int, tall: bool) -> str:
    chart_w = w - 2 * (64 if tall else 48)
    line_h = 560 if tall else 400
    bars_h = 3 * 46 + 2 * 16 + 16
    section_gap = 64 if tall else 28
    source_line = (
        f"Source: U.S. Department of the Treasury, TIC Table 5 (Major Foreign Holders of Treasury Securities), {SOURCE_URL}, "
        f"fetched {FETCHED}. Peak {fmt_b(JAPAN[PEAK_I])} (Feb 2026) to {fmt_b(JAPAN[LAST_I])} (Jun 2026): &#8722;{fmt_b(DROP)}, &#8722;{DROP_PCT}%."
        if tall else
        f"Source: U.S. Treasury, TIC Table 5 (Major Foreign Holders), ticdata.treasury.gov, fetched {FETCHED}. Full link in the first comment."
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Japan sold a tenth of its Treasuries in four months</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Kalam:wght@400;700&display=swap">
<style>
  :root {{ --cream:{CREAM}; --ink:{CHARCOAL}; --cobalt:{COBALT}; --coral:{CORAL}; --sun:{SUNFLOWER}; --soft:{INK_SOFT}; }}
  * {{ box-sizing: border-box; margin: 0; }}
  html, body {{ width:{w}px; height:{h}px; background: var(--cream); color: var(--ink); overflow: hidden; }}
  body {{ font-family: Inter, Arial, sans-serif; font-variant-numeric: tabular-nums; padding: {64 if tall else 48}px; display: flex; flex-direction: column; gap: {section_gap}px; }}
  .hand {{ font-family: Kalam, Inter, cursive; fill: var(--ink); }}
  .eyebrow {{ font-weight: 700; font-size: 21px; letter-spacing: .14em; text-transform: uppercase; color: var(--soft); }}
  h1 {{ font-family: Kalam, Inter, cursive; font-weight: 700; font-size: {66 if tall else 54}px; line-height: 1.08; margin-top: 12px; text-wrap: balance; }}
  .sub {{ font-size: 25px; line-height: 1.35; margin-top: 10px; color: var(--ink); }}
  .rule {{ height: 3px; background: var(--ink); margin-top: 20px; }}
  .chart-title {{ font-size: 22px; font-weight: 700; margin-bottom: 4px; }}
  .chart-rule {{ font-size: 18px; color: var(--soft); margin-bottom: 8px; }}
  .tick {{ font-size: 21px; fill: var(--soft); }}
  .label {{ font-size: 26px; font-weight: 700; }}
  .coral {{ fill: var(--coral); }}
  .halo {{ paint-order: stroke fill; stroke: var(--cream); stroke-width: 9px; stroke-linejoin: round; }}
  .callout {{ font-size: 32px; font-weight: 700; fill: var(--ink); }}
  .callout-sub {{ font-size: 22px; fill: var(--soft); }}
  .barlabel {{ font-size: 26px; }}
  .barvalue {{ font-size: 26px; font-weight: 700; }}
  .mech {{ display: flex; align-items: center; gap: 18px; font-size: {30 if tall else 27}px; font-weight: 700; letter-spacing: -.01em; }}
  .mech .arrow {{ color: var(--soft); font-weight: 400; }}
  .mech .you {{ background: var(--cobalt); color: var(--cream); padding: 10px 22px; border-radius: 6px; }}
  .mech-sub {{ font-size: 21px; color: var(--soft); margin-top: 12px; line-height: 1.4; }}
  footer {{ margin-top: auto; display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; }}
  .source {{ font-size: {17 if tall else 16}px; color: var(--soft); line-height: 1.45; max-width: {640 if tall else 600}px; }}
  .brand {{ font-weight: 900; font-size: 19px; letter-spacing: .12em; text-transform: uppercase; white-space: nowrap; }}
</style></head>
<body>
  <header>
    <div class="eyebrow">TIC Table 5 &#183; June 2026 print</div>
    <h1>Japan sold a tenth of its Treasuries in four months.</h1>
    <div class="sub">And the auction sets your price.</div>
    <div class="rule"></div>
  </header>

  <section>
    <div class="chart-title">Japan's holdings of U.S. Treasuries</div>
    <div class="chart-rule">$ billions, holdings at month end, June 2025 to June 2026. The drop is the coral segment; drops go down.</div>
    {line_chart(chart_w, line_h)}
  </section>

  <section>
    <div class="chart-title">The biggest lender: more than the UK or China</div>
    <div class="chart-rule">Top three foreign holders, June 2026, $ billions.</div>
    {bar_chart(chart_w, bars_h)}
  </section>

  <section>
    <div class="mech"><span>Tokyo sells</span><span class="arrow">&#8594;</span><span>fewer bids at auction</span><span class="arrow">&#8594;</span><span>higher yield</span><span class="arrow">&#8594;</span><span class="you">your rate</span></div>
    <div class="mech-sub">When the biggest buyer walks, the auction has to raise the yield to find new buyers. The Fed has not moved.</div>
  </section>

  <footer>
    <div class="source">{source_line}</div>
    <div class="brand">Not a panic. Not a plot. Mechanics.</div>
  </footer>
</body></html>
"""


FORMATS = {"4x5": (1080, 1350, False), "9x16": (1080, 1920, True)}


def render(html_path: Path, png_path: Path, w: int, h: int) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        pg.goto(html_path.as_uri())
        pg.evaluate("document.fonts.ready.then(() => true)")
        pg.wait_for_timeout(600)
        pg.screenshot(path=str(png_path), full_page=False)
        browser.close()


def main(argv: list[str]) -> int:
    do_render = "--no-render" not in argv
    for tag, (w, h, tall) in FORMATS.items():
        html_path = HERE / f"tic-table5-light-{tag}.html"
        html_path.write_text(page(w, h, tall), encoding="utf-8")
        print("wrote", html_path.name)
        if do_render:
            png = html_path.with_suffix(".png")
            render(html_path, png, w, h)
            print("rendered", png.name, png.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
