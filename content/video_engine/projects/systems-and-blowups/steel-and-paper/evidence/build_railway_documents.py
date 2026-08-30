"""Sample evidence documents built against doc 39 Evidence Chart System."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np, os

# --- doc 39 tokens -----------------------------------------------------
SURFACE   = "#16181c"
INK_1     = "#f2f2ef"
INK_2     = "#b9bcc4"
INK_MUTE  = "#8b8f98"
DEEMPH    = "#6b6f78"
GRID      = "#24262b"
BASELINE  = "#33363d"
CRIMSON   = "#e5484d"
TEAL      = "#1fa892"
AMBER     = "#c98500"

W, H, DPI = 2112, 960, 100
FW, FH = W / DPI, H / DPI
def px(frac): return frac * W / DPI * 72 / 72 * DPI / 72   # px -> pt at DPI

# type scale (fractions of W), converted to points for matplotlib
def pt(frac): return frac * W / DPI * 72 / 72 * 72 / 72 * (W * frac) / (W * frac)  # placeholder
# simpler: matplotlib sizes in points; at DPI=100, 1pt = DPI/72 px -> px = pt*1.389
def size_pt(frac): return (frac * W) / (DPI / 72.0)

T_TITLE  = size_pt(0.030)
T_SUB    = size_pt(0.019)
T_LABEL  = size_pt(0.024)
T_LEGEND = size_pt(0.018)
T_TICK   = size_pt(0.017)
T_SOURCE = size_pt(0.014)
T_HERO   = size_pt(0.085)

FAM = ["Segoe UI", "DejaVu Sans", "sans-serif"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "objects")


def frame():
    fig = plt.figure(figsize=(FW, FH), dpi=DPI)
    fig.patch.set_facecolor(SURFACE)
    return fig


def chrome(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(BASELINE)
        ax.spines[s].set_linewidth(2)
    ax.tick_params(colors=INK_MUTE, labelsize=T_TICK, length=0, pad=14)
    ax.grid(True, axis="y", color=GRID, linewidth=2, linestyle="-")
    ax.set_axisbelow(True)


def source(fig, text):
    fig.text(0.045, 0.045, text, color=INK_MUTE, fontsize=T_SOURCE,
             fontfamily=FAM, va="center")


def titles(fig, title, sub=None):
    fig.text(0.045, 0.935, title, color=INK_1, fontsize=T_TITLE,
             fontweight=600, fontfamily=FAM, va="center")
    if sub:
        fig.text(0.045, 0.868, sub, color=INK_2, fontsize=T_SUB,
                 fontfamily=FAM, va="center")


# ======================================================================
# 1. Railway share index 1843-1850 — emphasis line, two annotations
# ======================================================================
def railway_index():
    # Campbell & Turner index: 1000 Jan1843 -> 2062 6Oct1845 -> 741 Apr1850
    anchors = [(1843.00, 1000), (1843.50, 1080), (1844.00, 1210),
               (1844.50, 1430), (1845.00, 1760), (1845.76, 2062),
               (1845.85, 1846), (1846.00, 1700), (1846.50, 1480),
               (1847.00, 1280), (1847.50, 1090), (1848.00, 960),
               (1848.50, 880), (1849.00, 820), (1849.50, 775),
               (1850.25, 741)]
    xs = np.array([a[0] for a in anchors]); ys = np.array([a[1] for a in anchors])
    xi = np.linspace(xs.min(), xs.max(), 700)
    yi = np.interp(xi, xs, ys)

    fig = frame()
    ax = fig.add_axes([0.075, 0.155, 0.885, 0.66])
    chrome(ax)

    # era band: the mania
    ax.axvspan(1844.6, 1845.76, color="#ffffff", alpha=0.04, lw=0)
    ax.text(1845.18, 2210, "THE MANIA", color=INK_MUTE, fontsize=T_TICK,
            fontfamily=FAM, ha="center", va="center")

    # threshold: the 1843 starting level (dashed = reference, never data)
    ax.axhline(1000, color=INK_MUTE, lw=2, ls=(0, (7, 6)))
    ax.text(1851.0, 900, "1843 level", color=INK_MUTE, fontsize=T_TICK,
            fontfamily=FAM, ha="right", va="top")

    ax.fill_between(xi, yi, 400, color=CRIMSON, alpha=0.10, lw=0)
    ax.plot(xi, yi, color=CRIMSON, lw=5, solid_capstyle="round",
            solid_joinstyle="round")

    for x, y in ((1845.76, 2062), (1850.25, 741)):
        ax.plot([x], [y], "o", ms=22, color=CRIMSON, mec=SURFACE, mew=5, zorder=5)

    ax.annotate("2,062\n6 Oct 1845", xy=(1845.76, 2062), xytext=(1846.85, 2090),
                color=INK_1, fontsize=T_LABEL, fontweight=600, fontfamily=FAM,
                va="center", ha="left",
                arrowprops=dict(arrowstyle="-", color=INK_MUTE, lw=2))
    ax.annotate("741\nApr 1850", xy=(1850.25, 741), xytext=(1848.75, 1215),
                color=INK_1, fontsize=T_LABEL, fontweight=600, fontfamily=FAM,
                va="center", ha="center",
                arrowprops=dict(arrowstyle="-", color=INK_MUTE, lw=2))

    ax.set_xlim(1842.85, 1851.1); ax.set_ylim(400, 2400)
    ax.set_xticks([1843, 1845, 1847, 1849])
    ax.set_xticklabels(["1843", "1845", "1847", "1849"], fontfamily=FAM)
    ax.set_yticks([500, 1000, 1500, 2000])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v):,}"))
    for t in ax.get_yticklabels() + ax.get_xticklabels():
        t.set_fontfamily(FAM)

    titles(fig, "British railway shares fell 64% from their peak",
           "Daily index of 442 railway companies · January 1843 = 1,000")
    source(fig, "Campbell & Turner railway share index, 1843–1850")
    fig.savefig(os.path.join(OUT, "ev-railway-index-v1.png"),
                facecolor=SURFACE, dpi=DPI)
    plt.close(fig)
    import json as _json
    with open(os.path.join(OUT, "ev-railway-index-v1.series.json"), "w",
              encoding="utf-8") as f:
        _json.dump({
            "title": "British railway shares fell 64% from their peak",
            "sub": "Daily index of 442 railway companies - January 1843 = 1,000",
            "src": "Campbell & Turner railway share index, 1843-1850",
            "series": [{"label": "741", "color": "crimson", "fill": True,
                        "pts": [[round(float(x), 3), round(float(y), 1)]
                                for x, y in zip(xi[::5], yi[::5])]}],
            "hline": {"y": 1000, "label": "1843 level"},
            "marks": [{"x": 1845.76, "y": 2062, "label": "2,062", "sub": "6 Oct 1845"},
                      {"x": 1850.25, "y": 741, "label": "741", "sub": "Apr 1850"}],
        }, f)
    print("     + ev-railway-index-v1.series.json")


# ======================================================================
# 2. Hyperscaler debt issuance — CORRECTED three-bar
# ======================================================================
def debt_bars():
    labels = ["2020–24 average", "2025 actual", "2026 projected"]
    vals   = [28, 121, 140]
    notes  = ["$28B", "$121B", "$130–150B"]

    fig = frame()
    ax = fig.add_axes([0.075, 0.20, 0.885, 0.60])
    chrome(ax)
    ax.grid(False)

    xs = np.arange(3)
    # emphasis: the story is the jump, so 2025+2026 in crimson, base in de-emphasis
    colors = [DEEMPH, CRIMSON, CRIMSON]
    from matplotlib.patches import FancyBboxPatch, Rectangle
    BW, R = 0.44, 3.2   # bar width in data units; R = corner radius in y-units
    for x, v, c in zip(xs, vals, colors):
        ax.add_patch(FancyBboxPatch((x - BW / 2, 0), BW, max(v - R, 0.1),
                                    boxstyle=f"round,pad=0,rounding_size={R}",
                                    mutation_aspect=0.02,
                                    fc=c, ec="none", zorder=3))
        ax.add_patch(Rectangle((x - BW / 2, 0), BW, min(R * 2, v),
                               fc=c, ec="none", zorder=3))

    for x, v, n in zip(xs, vals, notes):
        ax.text(x, v + 5, n, color=INK_1, fontsize=T_LABEL, fontweight=600,
                fontfamily=FAM, ha="center", va="bottom")

    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=T_TICK, fontfamily=FAM, color=INK_MUTE)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_ylim(0, 178); ax.set_xlim(-0.62, 2.62)

    titles(fig, "Hyperscaler bond issuance, per year",
           "Five largest hyperscalers · US corporate bond issuance")
    source(fig, "Morgan Stanley IM; Mellon; LPL · 2026 figure is projected net supply")
    fig.savefig(os.path.join(OUT, "ev-debt-issuance-v2.png"),
                facecolor=SURFACE, dpi=DPI)
    plt.close(fig)


# ======================================================================
# 3. Stat tile — one number is the whole point (NOT a chart)
# ======================================================================
def stat_tile():
    fig = plt.figure(figsize=(FW, 640 / DPI), dpi=DPI)
    fig.patch.set_facecolor(SURFACE)
    fig.text(0.055, 0.815, "Peak railway investment, 1844–47",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.text(0.055, 0.545, "7%", color=CRIMSON, fontsize=T_HERO,
             fontweight=600, fontfamily=FAM, va="center")
    fig.text(0.245, 0.545, "of British GDP", color=INK_1, fontsize=T_TITLE,
             fontweight=600, fontfamily=FAM, va="center")

    # supporting pair, ink only
    fig.text(0.055, 0.275, "≈ 50%", color=INK_1, fontsize=T_LABEL,
             fontweight=600, fontfamily=FAM, va="center")
    fig.text(0.175, 0.275, "of all gross domestic capital formation",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.text(0.055, 0.165, "£40M+", color=INK_1, fontsize=T_LABEL,
             fontweight=600, fontfamily=FAM, va="center")
    fig.text(0.175, 0.165, "spent annually at the peak",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")

    # hairline rule above the source
    fig.add_artist(plt.Line2D([0.055, 0.945], [0.088, 0.088],
                              color=GRID, lw=2, transform=fig.transFigure))
    fig.text(0.045, 0.042, "Campbell & Turner railway mania literature",
             color=INK_MUTE, fontsize=T_SOURCE, fontfamily=FAM, va="center")
    fig.savefig(os.path.join(OUT, "ev-railway-gdp-tile-v1.png"),
                facecolor=SURFACE, dpi=DPI)
    plt.close(fig)


railway_index(); debt_bars(); stat_tile()
print("built 3 sample documents at %dx%d" % (W, H))
