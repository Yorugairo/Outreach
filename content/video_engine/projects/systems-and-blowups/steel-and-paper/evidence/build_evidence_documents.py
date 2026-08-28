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


if __name__ == "__main__":
    print("building evidence documents ->", OUT)
    for fn in (equip_ipp_gdp, capex_trajectory, dram_prices,
               uber_adoption, railway_mileage):
        try:
            fn()
        except Exception as e:
            print("  !! FAILED", fn.__name__, "-", e)
