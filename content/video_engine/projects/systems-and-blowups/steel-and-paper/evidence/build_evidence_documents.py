"""Steel and Paper evidence documents — built against doc 39 Evidence Chart System.

Every figure traces to EVIDENCE-DOSSIER.md. Nothing here is estimated.
Real series are fetched live (FRED / Yahoo); cited figures are marked CITED
and carry their source on the document itself.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np, os, io, csv, urllib.request, datetime as dt

# ---- doc 39 tokens (validated palette; see doc 39 §2) --------------------
SURFACE, INK_1, INK_2 = "#16181c", "#f2f2ef", "#b9bcc4"
INK_MUTE, DEEMPH      = "#8b8f98", "#6b6f78"
GRID, BASELINE        = "#24262b", "#33363d"
CRIMSON, TEAL, AMBER, COBALT = "#e5484d", "#1fa892", "#c98500", "#4a7fd6"

W, H, DPI = 2112, 960, 100
FW, FH = W / DPI, H / DPI
size_pt = lambda frac: (frac * W) / (DPI / 72.0)
T_TITLE, T_SUB   = size_pt(0.030), size_pt(0.019)
T_LABEL, T_LEG   = size_pt(0.024), size_pt(0.018)
T_TICK, T_SOURCE = size_pt(0.017), size_pt(0.014)
T_HERO           = size_pt(0.085)
FAM = ["Segoe UI", "DejaVu Sans", "sans-serif"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "objects")
os.makedirs(OUT, exist_ok=True)


def esc(t):
    """matplotlib reads $...$ as mathtext; literal dollars must be escaped."""
    return t.replace("$", r"\$")

def frame(h=H):
    fig = plt.figure(figsize=(FW, h / DPI), dpi=DPI)
    fig.patch.set_facecolor(SURFACE)
    return fig

def chrome(ax, ygrid=True):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(BASELINE); ax.spines[s].set_linewidth(2)
    ax.tick_params(colors=INK_MUTE, labelsize=T_TICK, length=0, pad=14)
    if ygrid:
        ax.grid(True, axis="y", color=GRID, linewidth=2, linestyle="-")
    ax.set_axisbelow(True)
    for t in ax.get_xticklabels() + ax.get_yticklabels(): t.set_fontfamily(FAM)

def titles(fig, title, sub=None):
    h = fig.get_size_inches()[1] * DPI
    fig.text(0.045, 1 - 62 / h, esc(title), color=INK_1, fontsize=T_TITLE,
             fontweight=600, fontfamily=FAM, va="center")
    if sub:
        fig.text(0.045, 1 - 126 / h, esc(sub), color=INK_2, fontsize=T_SUB,
                 fontfamily=FAM, va="center")

def source(fig, text, y=None):
    h = fig.get_size_inches()[1] * DPI
    fig.text(0.045, 44 / h if y is None else y, esc(text), color=INK_MUTE,
             fontsize=T_SOURCE, fontfamily=FAM, va="center")

def save(fig, name):
    p = os.path.join(OUT, name + ".png")
    fig.savefig(p, facecolor=fig.patch.get_facecolor(), dpi=DPI)
    plt.close(fig); print("  ->", name)

def rounded_bars(ax, xs, vals, colors, bw=0.44, radius_frac=0.022):
    top = max(vals) if max(vals) else 1
    R = top * radius_frac
    for x, v, c in zip(xs, vals, colors):
        ax.add_patch(FancyBboxPatch((x - bw/2, 0), bw, max(v - R, 1e-6),
                     boxstyle=f"round,pad=0,rounding_size={R}",
                     mutation_aspect=0.02, fc=c, ec="none", zorder=3))
        ax.add_patch(Rectangle((x - bw/2, 0), bw, min(R*2, v),
                     fc=c, ec="none", zorder=3))

# ---- data helpers --------------------------------------------------------
def fred(series):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    raw = urllib.request.urlopen(url, timeout=30).read().decode()
    out = {}
    for row in list(csv.reader(io.StringIO(raw)))[1:]:
        try: out[row[0]] = float(row[1])
        except (ValueError, IndexError): pass
    return out


# =========================================================================
# 1. Equipment + IPP investment as a share of GDP  (REAL — BEA via FRED)
# =========================================================================

def emit_sidecar(name, payload):
    """Live-chart sidecar: the SAME data the PNG was drawn from, so the
    player can DRAW the chart instead of pasting it (operator, 2026-08-30:
    the animated evidence layer comes back for every chart)."""
    import json as _json
    from pathlib import Path as _P
    (_P(__file__).parent / "objects" / (name + ".series.json")).write_text(
        _json.dumps(payload), encoding="utf-8")
    print(f"     + {name}.series.json")


def dec_pts(xs, ys, n=140):
    step = max(1, len(xs) // n)
    return [[round(float(x), 4), round(float(y), 3)]
            for x, y in list(zip(xs, ys))[::step]]


def equip_ipp_gdp():
    eq, ipp, gdp = fred("Y033RC1Q027SBEA"), fred("Y001RC1Q027SBEA"), fred("GDP")
    keys = sorted(set(eq) & set(ipp) & set(gdp))
    keys = [k for k in keys if k >= "1970-01-01"]
    xs = [dt.date.fromisoformat(k).year + (int(k[5:7]) - 1) / 12 for k in keys]
    ys = [(eq[k] + ipp[k]) / gdp[k] * 100 for k in keys]

    peak90 = max(y for x, y in zip(xs, ys) if 1995 <= x <= 2001)
    latest = ys[-1]

    fig = frame(); ax = fig.add_axes([0.075, 0.155, 0.885, 0.655]); chrome(ax)
    ax.axhline(peak90, color=INK_MUTE, lw=2, ls=(0, (7, 6)))
    ax.text(xs[0] + 0.6, peak90 + 0.10, f"Q2 2000 peak · {peak90:.2f}%",
            color=INK_MUTE, fontsize=T_TICK, fontfamily=FAM, va="bottom")
    ax.fill_between(xs, ys, min(ys) - 0.4, color=CRIMSON, alpha=0.10, lw=0)
    ax.plot(xs, ys, color=CRIMSON, lw=5, solid_capstyle="round")
    ax.plot([xs[-1]], [latest], "o", ms=22, color=CRIMSON, mec=SURFACE, mew=5, zorder=5)
    ax.annotate(f"{latest:.2f}%", xy=(xs[-1], latest),
                xytext=(xs[-1] - 6.5, latest + 0.55),
                color=INK_1, fontsize=T_LABEL, fontweight=600, fontfamily=FAM,
                arrowprops=dict(arrowstyle="-", color=INK_MUTE, lw=2))
    ax.set_ylim(min(ys) - 0.4, max(ys) + 1.0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}%"))
    ax.set_xticks([1975, 1985, 1995, 2005, 2015, 2025])
    ax.set_xticklabels(["1975","1985","1995","2005","2015","2025"], fontfamily=FAM)
    titles(fig, "Equipment and IP investment is back at its dot-com peak",
           "US private nonresidential investment, share of GDP · "
           "latest quarter sits 0.03pp below the Q2 2000 high")
    source(fig, "BEA via FRED · (Y033RC1Q027SBEA + Y001RC1Q027SBEA) ÷ GDP · "
                f"quarterly, 1970–{keys[-1][:4]}")
    save(fig, "ev-equip-ipp-gdp-v1")
    emit_sidecar("ev-equip-ipp-gdp-v1", {
        "title": "Equipment and IP investment is back at its dot-com peak",
        "sub": "US private nonresidential investment, share of GDP",
        "src": "BEA via FRED - quarterly since 1970",
        "series": [{"label": f"{latest:.2f}%", "color": "crimson",
                    "fill": True, "pts": dec_pts(xs, ys)}],
        "hline": {"y": round(peak90, 2), "label": f"Q2 2000 peak - {peak90:.2f}%"},
    })


# =========================================================================
# 2. Hyperscaler capex consensus  (CITED — PIMCO)
# =========================================================================
def capex_trajectory():
    labels = ["Start-of-year\nestimate", "2026\nconsensus", "2027\nconsensus"]
    vals, notes = [480, 690, 870], ["$480B", "$690B", "$870B"]
    fig = frame(); ax = fig.add_axes([0.075, 0.215, 0.885, 0.585])
    chrome(ax, ygrid=False)
    xs = np.arange(3)
    rounded_bars(ax, xs, vals, [DEEMPH, CRIMSON, CRIMSON])
    for x, v, n in zip(xs, vals, notes):
        ax.text(x, v + 22, esc(n), color=INK_1, fontsize=T_LABEL, fontweight=600,
                fontfamily=FAM, ha="center", va="bottom")
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=T_TICK,
                                          fontfamily=FAM, color=INK_MUTE)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_ylim(0, 1090); ax.set_xlim(-0.62, 2.62)
    titles(fig, "Hyperscaler capital spending, consensus estimates",
           "Five largest hyperscalers · expected to absorb 94% of operating cash flow")
    source(fig, "PIMCO, “AI Credit Expansion: Assessing the Micro and Macro Risks”, "
                "Figures 2–3 · consensus estimates, not actuals")
    save(fig, "ev-capex-consensus-v1")
    emit_sidecar("ev-capex-consensus-v1", {
        "title": "Hyperscaler capital spending, consensus estimates",
        "sub": "Five largest hyperscalers - 94% of operating cash flow",
        "src": "PIMCO, Figures 2-3 - consensus estimates, not actuals",
        "bars": [{"label": "Start of year", "value": 480, "note": "$480B", "color": "deemph"},
                 {"label": "2026 consensus", "value": 690, "note": "$690B", "color": "crimson"},
                 {"label": "2027 consensus", "value": 870, "note": "$870B", "color": "crimson"}],
    })


# =========================================================================
# 3. DRAM contract prices  (CITED — TrendForce / Counterpoint / Gartner)
# =========================================================================
def dram_prices():
    labels = ["Conventional\nDRAM", "Server\nDRAM", "Consumer\nDRAM"]
    vals, notes = [57.5, 60, 89], ["+55–60%", "+60%", "+89%"]
    fig = frame(); ax = fig.add_axes([0.075, 0.215, 0.885, 0.585])
    chrome(ax, ygrid=False)
    xs = np.arange(3)
    rounded_bars(ax, xs, vals, [DEEMPH, DEEMPH, CRIMSON])
    for x, v, n in zip(xs, vals, notes):
        ax.text(x, v + 2.2, n, color=INK_1, fontsize=T_LABEL, fontweight=600,
                fontfamily=FAM, ha="center", va="bottom")
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=T_TICK,
                                          fontfamily=FAM, color=INK_MUTE)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_ylim(0, 112); ax.set_xlim(-0.62, 2.62)
    titles(fig, "Memory contract prices, quarter over quarter",
           "2026 · SK hynix reports HBM, DRAM and NAND “essentially sold out” for the year")
    source(fig, "TrendForce (conventional, server) · Counterpoint / TrendForce (consumer peak) "
                "· quarterly contract price change")
    save(fig, "ev-dram-contract-v1")
    emit_sidecar("ev-dram-contract-v1", {
        "title": "Memory contract prices, quarter over quarter",
        "sub": "2026 - HBM, DRAM and NAND essentially sold out for the year",
        "src": "TrendForce - Counterpoint - quarterly contract price change",
        "bars": [{"label": "Conventional DRAM", "value": 57.5, "note": "+55-60%", "color": "deemph"},
                 {"label": "Server DRAM", "value": 60, "note": "+60%", "color": "deemph"},
                 {"label": "Consumer DRAM", "value": 89, "note": "+89%", "color": "crimson"}],
    })


# =========================================================================
# 4. Uber Claude Code adoption  (CITED — The Information) — dumbbell
# =========================================================================
def uber_adoption():
    fig = frame(640); ax = fig.add_axes([0.075, 0.30, 0.885, 0.40])
    ax.set_facecolor(SURFACE)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(0, 100); ax.set_ylim(-1, 1)
    ax.plot([32, 84], [0, 0], color=DEEMPH, lw=8, solid_capstyle="round", zorder=2)
    ax.plot([32], [0], "o", ms=34, color=DEEMPH, mec=SURFACE, mew=6, zorder=3)
    ax.plot([84], [0], "o", ms=34, color=CRIMSON, mec=SURFACE, mew=6, zorder=3)
    ax.text(32, 0.34, "32%", color=INK_2, fontsize=T_LABEL, fontweight=600,
            fontfamily=FAM, ha="center")
    ax.text(84, 0.34, "84%", color=INK_1, fontsize=T_LABEL, fontweight=600,
            fontfamily=FAM, ha="center")
    ax.text(32, -0.52, "before", color=INK_MUTE, fontsize=T_TICK,
            fontfamily=FAM, ha="center")
    ax.text(84, -0.52, "by April 2026", color=INK_MUTE, fontsize=T_TICK,
            fontfamily=FAM, ha="center")
    titles(fig, "AI coding-tool adoption across Uber engineering",
           "Roughly 5,000 engineers · $500–$2,000 per engineer per month")
    source(fig, "The Information, April 2026 · Uber exhausted its full-year 2026 AI budget "
                "by April")
    save(fig, "ev-uber-adoption-v1")


# =========================================================================
# 5. Railway mileage authorised vs built  (CITED — Jackman 1916)
# =========================================================================
def railway_mileage():
    fig = frame(); ax = fig.add_axes([0.075, 0.215, 0.885, 0.585])
    chrome(ax, ygrid=False)
    xs = np.arange(2); vals = [8470, 2823]
    rounded_bars(ax, xs, vals, [CRIMSON, DEEMPH], bw=0.40)
    for x, v, n in zip(xs, vals, ["8,470 miles", "≈ 2,800 miles"]):
        ax.text(x, v + 210, esc(n), color=INK_1, fontsize=T_LABEL, fontweight=600,
                fontfamily=FAM, ha="center", va="bottom")
    ax.set_xticks(xs)
    ax.set_xticklabels(["Authorised by Parliament", "Actually constructed"],
                       fontsize=T_TICK, fontfamily=FAM, color=INK_MUTE)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_ylim(0, 10400); ax.set_xlim(-0.60, 1.60)
    titles(fig, "Parliament authorised three times the railway ever built",
           "Bills sanctioned 1844–46, against mileage actually constructed")
    source(fig, "Jackman (1916), p. 585 · 1845 alone authorised ~3,000 miles — "
                "about as much as the previous 15 years combined")
    save(fig, "ev-railway-mileage-v1")
    emit_sidecar("ev-railway-mileage-v1", {
        "title": "Parliament authorised three times the railway ever built",
        "sub": "Bills sanctioned 1844-46, against mileage actually constructed",
        "src": "Jackman (1916), p. 585",
        "bars": [{"label": "Authorised by Parliament", "value": 8470, "note": "8,470 miles", "color": "crimson"},
                 {"label": "Actually constructed", "value": 2823, "note": "~2,800 miles", "color": "deemph"}],
    })


# =========================================================================
# 6-9. Market series  (REAL — Yahoo Finance via yfinance)
# =========================================================================
def _px(ticker, start):
    import yfinance as yf
    d = yf.download(ticker, start=start, progress=False, auto_adjust=True)
    c = d["Close"]
    if hasattr(c, "columns"):          # yfinance returns MultiIndex columns
        c = c.iloc[:, 0]
    return c.dropna()

def _yr(idx):
    return [t.year + (t.dayofyear - 1) / 365.25 for t in idx]

def _year_ticks(ax, idx, step=1):
    """Axis must show years, not decimal-year floats."""
    yrs = list(range(idx[0].year, idx[-1].year + 1, step))
    ax.set_xticks(yrs)
    ax.set_xticklabels([str(y) for y in yrs], fontfamily=FAM)

def _endlabel(ax, x, y, text, color, dy=0):
    ax.plot([x], [y], "o", ms=20, color=color, mec=SURFACE, mew=5, zorder=6)
    ax.annotate(text, xy=(x, y), xytext=(10, dy), textcoords="offset points",
                color=INK_1, fontsize=T_LABEL, fontweight=600,
                fontfamily=FAM, va="center", ha="left")

def _legend(ax, entries):
    """Legend is mandatory for >=2 series; a coloured key beside text ink."""
    h = [plt.Line2D([0], [0], color=c, lw=6, solid_capstyle="round")
         for _, c in entries]
    lg = ax.legend(h, [n for n, _ in entries], loc="upper left",
                   frameon=False, fontsize=T_LEG, labelcolor=INK_2,
                   handlelength=1.1, handletextpad=0.7, borderaxespad=0.9)
    for t in lg.get_texts(): t.set_fontfamily(FAM)


def krx_memory():
    a, b = _px("000660.KS", "2024-01-01"), _px("MU", "2024-01-01")
    ai, bi = a / a.iloc[0] * 100, b / b.iloc[0] * 100
    fig = frame(); ax = fig.add_axes([0.075, 0.155, 0.845, 0.645]); chrome(ax)
    ax.plot(_yr(ai.index), ai.values, color=CRIMSON, lw=5, solid_capstyle="round")
    ax.plot(_yr(bi.index), bi.values, color=TEAL, lw=5, solid_capstyle="round")
    _endlabel(ax, _yr(ai.index)[-1], ai.iloc[-1], f"{ai.iloc[-1]:,.0f}", CRIMSON, dy=24)
    _endlabel(ax, _yr(bi.index)[-1], bi.iloc[-1], f"{bi.iloc[-1]:,.0f}", TEAL, dy=-24)
    _year_ticks(ax, ai.index)
    _legend(ax, [("SK hynix (000660.KS)", CRIMSON), ("Micron (MU)", TEAL)])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v):,}"))
    titles(fig, "The memory trade, live",
           "SK hynix and Micron, indexed to 100 at January 2024")
    source(fig, f"Data: Yahoo Finance, 000660.KS, MU · 2024-01 to "
                f"{ai.index[-1].date().isoformat()}")
    save(fig, "ev-krx-memory-v3")
    emit_sidecar("ev-krx-memory-v3", {
        "title": "The memory trade, live",
        "sub": "SK hynix and Micron, indexed to 100 at January 2024",
        "src": f"Yahoo Finance, 000660.KS, MU - to {ai.index[-1].date().isoformat()}",
        "series": [
            {"label": f"{ai.iloc[-1]:,.0f}", "color": "crimson",
             "pts": dec_pts(_yr(ai.index), ai.values)},
            {"label": f"{bi.iloc[-1]:,.0f}", "color": "teal",
             "pts": dec_pts(_yr(bi.index), bi.values)}],
    })


def mega_vs_spy():
    names = ["AMZN", "MSFT", "GOOGL", "META"]
    ser = [_px(t, "2023-01-01") for t in names]
    idx = ser[0].index
    for x in ser[1:]: idx = idx.intersection(x.index)
    basket = sum((x.reindex(idx) / x.reindex(idx).iloc[0]) for x in ser) / len(ser) * 100
    spy = _px("SPY", "2023-01-01").reindex(idx).ffill()
    spy = spy / spy.iloc[0] * 100
    fig = frame(); ax = fig.add_axes([0.075, 0.155, 0.845, 0.645]); chrome(ax)
    ax.plot(_yr(idx), basket.values, color=CRIMSON, lw=5, solid_capstyle="round")
    ax.plot(_yr(idx), spy.values, color=TEAL, lw=5, solid_capstyle="round")
    _endlabel(ax, _yr(idx)[-1], basket.iloc[-1], f"{basket.iloc[-1]:,.0f}", CRIMSON)
    _endlabel(ax, _yr(idx)[-1], spy.iloc[-1], f"{spy.iloc[-1]:,.0f}", TEAL)
    _legend(ax, [("Equal-weight AMZN / MSFT / GOOGL / META", CRIMSON),
                 ("S&P 500 (SPY)", TEAL)])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v):,}"))
    _year_ticks(ax, idx)
    titles(fig, "The builders against the index",
           "Equal-weight mega-cap basket vs the S&P 500, indexed to 100 at January 2023")
    source(fig, f"Data: Yahoo Finance, AMZN, MSFT, GOOGL, META, SPY · 2023-01 to "
                f"{idx[-1].date().isoformat()}")
    save(fig, "ev-mega-vs-spy-v3")


def divergence():
    """Bravos' actual chart (operator, 2026-08-29): MAMAA index vs a
    semiconductor index. We recreate their pairing faithfully and ADD the
    two layers the episode argues it needed - the S&P 500 (which the MAMAA
    line lands exactly on: the hyperscalers have gone market-rate) and the
    memory builders inside the semis (where the whole move lives). Log
    scale, stated - a +600% line on linear crushes their pairing into the
    bottom fifth, which hides the very chart we are crediting."""
    import numpy as np
    import pandas as pd
    start = (pd.Timestamp.today() - pd.DateOffset(months=12)).strftime("%Y-%m-%d")
    def basket(ticks):
        ser = [_px(t, start) for t in ticks]
        idx = ser[0].index
        for x in ser[1:]: idx = idx.intersection(x.index)
        return sum(x.reindex(idx).ffill() / x.reindex(idx).ffill().iloc[0]
                   for x in ser) / len(ser) * 100
    mem   = basket(["000660.KS", "MU"])
    mamaa = basket(["META", "AAPL", "MSFT", "AMZN", "GOOGL"]).reindex(mem.index).ffill()
    sox   = basket(["^SOX"]).reindex(mem.index).ffill()
    spy   = basket(["SPY"]).reindex(mem.index).ffill()
    fig = frame(); ax = fig.add_axes([0.075, 0.155, 0.845, 0.645]); chrome(ax)
    x = _yr(mem.index)
    ax.set_yscale("log")
    ax.plot(x, spy.values,   color=DEEMPH,  lw=3.5, ls=(0, (5, 3)), solid_capstyle="round")
    ax.plot(x, mamaa.values, color=COBALT,  lw=5,   solid_capstyle="round")
    ax.plot(x, sox.values,   color=TEAL,    lw=5,   solid_capstyle="round")
    ax.plot(x, mem.values,   color=CRIMSON, lw=5,   solid_capstyle="round")
    # Their pairing ends 5pts apart on a log axis - stagger the labels.
    _endlabel(ax, x[-1], mem.iloc[-1],   f"+{mem.iloc[-1]-100:,.0f}%",   CRIMSON)
    _endlabel(ax, x[-1], sox.iloc[-1],   f"+{sox.iloc[-1]-100:,.0f}%",   TEAL)
    _endlabel(ax, x[-1], mamaa.iloc[-1], f"+{mamaa.iloc[-1]-100:,.0f}%", COBALT, dy=16)
    _endlabel(ax, x[-1], spy.iloc[-1],   f"+{spy.iloc[-1]-100:,.0f}%",   DEEMPH, dy=-16)
    _legend(ax, [("Memory builders - SK hynix / Micron (our layer)", CRIMSON),
                 ("Semiconductors - PHLX SOX (their line)", TEAL),
                 ("MAMAA - META / AAPL / MSFT / AMZN / GOOGL (their line)", COBALT),
                 ("S&P 500 (our layer)", DEEMPH)])
    ax.set_yticks([100, 200, 400, 800])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v):,}"))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, p: ""))
    mt = pd.date_range(mem.index[0].normalize() + pd.offsets.MonthBegin(1),
                       mem.index[-1], freq="2MS")
    ax.set_xticks([t.year + (t.dayofyear - 1) / 365.25 for t in mt])
    ax.set_xticklabels([t.strftime("%b '%y") for t in mt], fontfamily=FAM)
    ax.set_xlim(x[0], x[-1] + 0.055)
    titles(fig, "The sharpest chart on YouTube - plus the layer it needed",
           "Their pairing, plus the S&P 500 and the memory builders. "
           "100 = Aug '25, log scale")
    source(fig, f"Data: Yahoo Finance - 000660.KS, MU, ^SOX, META, AAPL, MSFT, "
                f"AMZN, GOOGL, SPY - {start} to {mem.index[-1].date().isoformat()} "
                f"- pairing after Bravos Research")
    save(fig, "ev-divergence-v1")
    # LIVE-CHART SIDECAR: the same series, decimated, so the player can DRAW
    # the chart instead of pasting the PNG (the data-document motion pattern;
    # the PNG stays as the fallback and the review artifact).
    import json as _json
    from pathlib import Path
    def dec(sr, n=140):
        step = max(1, len(sr) // n)
        return [[_yr([i])[0], round(float(v), 2)]
                for i, v in list(zip(sr.index, sr.values))[::step]]
    (Path(__file__).parent / "objects/ev-divergence-v1.series.json").write_text(
        _json.dumps({
            "title": "The sharpest chart on YouTube - plus the layer it needed",
            "sub": "Their pairing, plus the S&P 500 and the memory builders. "
                   "100 = Aug '25, log scale",
            "src": "Yahoo Finance - pairing after Bravos Research",
            "log": True,
            "series": [
                {"label": f"+{mem.iloc[-1]-100:,.0f}%", "color": "crimson", "pts": dec(mem)},
                {"label": f"+{sox.iloc[-1]-100:,.0f}%", "color": "teal", "pts": dec(sox)},
                {"label": f"+{mamaa.iloc[-1]-100:,.0f}%", "color": "cobalt", "pts": dec(mamaa)},
                {"label": f"+{spy.iloc[-1]-100:,.0f}%", "color": "deemph", "pts": dec(spy)},
            ]}), encoding="utf-8")
    print(f"  VERBATIM  memory +{mem.iloc[-1]-100:,.0f}%  semis +{sox.iloc[-1]-100:,.0f}%  "
          f"MAMAA +{mamaa.iloc[-1]-100:,.0f}%  S&P +{spy.iloc[-1]-100:,.0f}%")

def smh_drawdown():
    s = _px("SMH", "2024-01-01")
    dd = (s / s.cummax() - 1) * 100
    x = _yr(dd.index)
    fig = frame(); ax = fig.add_axes([0.075, 0.155, 0.885, 0.645]); chrome(ax)
    ax.fill_between(x, dd.values, 0, color=CRIMSON, alpha=0.10, lw=0)
    ax.plot(x, dd.values, color=CRIMSON, lw=5, solid_capstyle="round")
    ax.axhline(0, color=BASELINE, lw=2)
    worst = dd.min()
    ax.set_ylim(worst - 7.5, 2.2)
    ax.annotate(f"worst {worst:.0f}%", xy=(x[int(dd.values.argmin())], worst),
                xytext=(0, -40), textcoords="offset points",
                color=INK_2, fontsize=T_TICK, fontfamily=FAM, ha="center")
    _year_ticks(ax, dd.index)
    _endlabel(ax, x[-1], dd.iloc[-1], f"{dd.iloc[-1]:.0f}%", CRIMSON)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v)}%"))
    titles(fig, "Semiconductors, distance from their own peak",
           "SMH drawdown from running high — a single series, so no legend")
    source(fig, f"Data: Yahoo Finance, SMH · 2024-01 to {dd.index[-1].date().isoformat()}")
    save(fig, "ev-smh-drawdown-v3")
    emit_sidecar("ev-smh-drawdown-v3", {
        "title": "Semiconductors, distance from their own peak",
        "sub": "SMH drawdown from running high",
        "src": f"Yahoo Finance, SMH - 2024-01 to {dd.index[-1].date().isoformat()}",
        "series": [{"label": f"{dd.iloc[-1]:.0f}%", "color": "crimson",
                    "fill": True, "pts": dec_pts(x, dd.values)}],
        "hline": {"y": 0, "label": ""},
    })


def tnx_two_eras():
    """Two eras = small multiples, never a dual axis (doc 39 §6)."""
    a = _px("^TNX", "1998-01-01")
    a = a[a.index < "2002-01-01"]
    b = _px("^TNX", "2021-01-01")
    fig = frame()
    for i, (ser, lbl) in enumerate(((a, "Dot-com era · 1998–2001"),
                                    (b, "AI era · 2021–today"))):
        ax = fig.add_axes([0.075 + i * 0.475, 0.175, 0.395, 0.545]); chrome(ax)
        x = _yr(ser.index)
        ax.plot(x, ser.values, color=CRIMSON, lw=5, solid_capstyle="round")
        _endlabel(ax, x[-1], ser.iloc[-1], f"{ser.iloc[-1]:.1f}%", CRIMSON)
        ax.set_title(lbl, color=INK_2, fontsize=T_LEG, fontfamily=FAM,
                     loc="left", pad=22)
        ax.set_ylim(0, 7.2)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v)}%"))
        if i: ax.set_yticklabels([])
    titles(fig, "The 10-year Treasury yield, two eras",
           "Same scale, side by side — never two y-axes on one plot")
    source(fig, f"Data: Yahoo Finance, ^TNX · 1998-01 to 2001-12 and 2021-01 to "
                f"{b.index[-1].date().isoformat()}")
    save(fig, "ev-tnx-two-eras-v3")
    emit_sidecar("ev-tnx-two-eras-v3", {
        "title": "The 10-year Treasury yield, two eras",
        "sub": "Same scale, side by side - never two y-axes on one plot",
        "src": "Yahoo Finance, ^TNX",
        "ymax": 7.2,
        "panels": [
            {"sub": "Dot-com era - 1998-2001",
             "series": [{"label": f"{a.iloc[-1]:.1f}%", "color": "crimson",
                         "pts": dec_pts(_yr(a.index), a.values)}]},
            {"sub": "AI era - 2021-today",
             "series": [{"label": f"{b.iloc[-1]:.1f}%", "color": "crimson",
                         "pts": dec_pts(_yr(b.index), b.values)}]}],
    })


# =========================================================================
# 10. Tech's share of the investment-grade index  (CITED - MS IM / LPL)
# =========================================================================
def ig_credit_weighting():
    labels = ["2024", "Now", "Projected"]
    vals, notes = [9.0, 10.0, 12.0], ["9%", "10%", ">12%"]
    fig = frame(); ax = fig.add_axes([0.075, 0.215, 0.885, 0.585])
    chrome(ax, ygrid=False)
    xs = np.arange(3)
    rounded_bars(ax, xs, vals, [DEEMPH, CRIMSON, CRIMSON], bw=0.42)
    for x, v, n in zip(xs, vals, notes):
        ax.text(x, v + 0.25, esc(n), color=INK_1, fontsize=T_LABEL, fontweight=600,
                fontfamily=FAM, ha="center", va="bottom")
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=T_TICK,
                                          fontfamily=FAM, color=INK_MUTE)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_ylim(0, 14.6); ax.set_xlim(-0.62, 2.62)
    titles(fig, "Technology's share of the investment-grade bond index",
           "The pool a bond fund buys from - reweighting toward data centres")
    source(fig, "Morgan Stanley Investment Management; LPL / Investing.com - "
                "Bloomberg Corporate Bond Index; the third bar is a projection")
    save(fig, "ev-ig-credit-weighting-v1")
    emit_sidecar("ev-ig-credit-weighting-v1", {
        "title": "Technology's share of the investment-grade bond index",
        "sub": "The pool a bond fund buys from - reweighting toward data centres",
        "src": "Morgan Stanley IM; LPL - the third bar is a projection",
        "bars": [{"label": "2024", "value": 9.0, "note": "9%", "color": "deemph"},
                 {"label": "Now", "value": 10.0, "note": "10%", "color": "crimson"},
                 {"label": "Projected", "value": 12.0, "note": ">12%", "color": "crimson"}],
    })


# =========================================================================
# 11. HBM wafer ratio  (CITED - Micron) - a stat tile, not a chart
# =========================================================================
def hbm_wafer_ratio():
    fig = frame(640)
    fig.text(0.055, 0.815, "Wafer capacity per gigabyte, HBM against standard DRAM",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.text(0.055, 0.525, "3x", color=CRIMSON, fontsize=T_HERO,
             fontweight=600, fontfamily=FAM, va="center")
    fig.text(0.225, 0.525, "the silicon, for the same gigabyte",
             color=INK_1, fontsize=T_TITLE, fontweight=600, fontfamily=FAM, va="center")
    fig.text(0.055, 0.245,
             "Stacking the dies is what makes it scarce - every accelerator fed",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.text(0.055, 0.175,
             "takes wafer away from everything else on the line.",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.add_artist(plt.Line2D([0.055, 0.945], [0.108, 0.108],
                              color=GRID, lw=2, transform=fig.transFigure))
    fig.text(0.045, 0.045, "Micron, via industry reporting - approximate ratio",
             color=INK_MUTE, fontsize=T_SOURCE, fontfamily=FAM, va="center")
    save(fig, "ev-hbm-wafer-ratio-v1")


if __name__ == "__main__":
    print("building evidence documents ->", OUT)
    for fn in (equip_ipp_gdp, capex_trajectory, dram_prices,
               uber_adoption, railway_mileage,
               krx_memory, mega_vs_spy, smh_drawdown, tnx_two_eras,
               ig_credit_weighting, hbm_wafer_ratio):
        try:
            fn()
        except Exception as e:
            print("  !! FAILED", fn.__name__, "-", e)
