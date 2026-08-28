"""Audit exhibit — the evidence document that shows what a number is MADE OF.

Worked example: HS 8542.32.3000 export unit value. The tripwire's
"HBM +26.5% vs trailing mean" compared a single HBM print against a
trailing window that is eleven months of NAND. This chart makes the
regime break visible, which no amount of prose does as fast.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np, os

SURFACE, INK_1, INK_2 = "#16181c", "#f2f2ef", "#b9bcc4"
INK_MUTE, DEEMPH      = "#8b8f98", "#6b6f78"
GRID, BASELINE        = "#24262b", "#33363d"
CRIMSON, TEAL, AMBER  = "#e5484d", "#1fa892", "#c98500"

W, H, DPI = 2112, 1060, 100
size_pt = lambda f: (f * W) / (DPI / 72.0)
T_TITLE, T_SUB, T_LABEL = size_pt(0.030), size_pt(0.019), size_pt(0.024)
T_TICK, T_SOURCE, T_LEG = size_pt(0.017), size_pt(0.014), size_pt(0.018)
FAM = ["Segoe UI", "DejaVu Sans", "sans-serif"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "objects")

# HS 8542.32.3000, export flow, verbatim from trade_facts
SERIES = [
    ("2025-03", 226.3, "hbm"), ("2025-03", 230.9, "hbm"), ("2025-03", 237.3, "hbm"),
    ("2025-04", 239.6, "hbm"), ("2025-04", 244.4, "hbm"), ("2025-04", 236.4, "hbm"),
    ("2025-05", 232.1, "hbm"),
    ("2025-06", 43840.7, "nand"), ("2025-07", 42087.7, "nand"),
    ("2025-08", 44118.5, "nand"), ("2025-09", 41367.1, "nand"),
    ("2025-10", 44348.5, "nand"), ("2025-11", 50392.7, "nand"),
    ("2025-12", 58868.7, "nand"), ("2026-01", 55748.6, "nand"),
    ("2026-02", 72665.7, "nand"), ("2026-03", 63748.3, "nand"),
    ("2026-04", 72712.3, "nand"),
    ("2026-05", 83779.3, "hbm"),
]

def build():
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0.075, 0.205, 0.885, 0.545])
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(BASELINE); ax.spines[s].set_linewidth(2)
    ax.tick_params(colors=INK_MUTE, labelsize=T_TICK, length=0, pad=14)
    ax.grid(True, axis="y", color=GRID, linewidth=2)
    ax.set_axisbelow(True)

    xs = np.arange(len(SERIES))
    ys = [v for _, v, _ in SERIES]
    kinds = [k for _, _, k in SERIES]

    # the trailing window behind "+26.5%" — eleven months of NAND
    ax.axvspan(6.5, 17.5, color="#ffffff", alpha=0.045, lw=0)
    ax.text(12.3, 1150000, "the trailing mean behind “+26.5%”",
            color=INK_2, fontsize=T_LEG, fontfamily=FAM, ha="center")
    ax.annotate("", xy=(7, 700000), xytext=(17.6, 700000),
                arrowprops=dict(arrowstyle="<->", color=INK_MUTE, lw=2))
    ax.text(12.3, 400000, "11 months of NAND", color=AMBER,
            fontsize=T_LABEL, fontweight=600, fontfamily=FAM, ha="center")

    # segments, coloured by what the row is actually labelled
    for i in range(len(xs) - 1):
        if kinds[i] == kinds[i + 1]:
            c = CRIMSON if kinds[i] == "hbm" else AMBER
            ax.plot(xs[i:i + 2], ys[i:i + 2], color=c, lw=5,
                    solid_capstyle="round", zorder=3)
        else:   # the regime break itself — never draw a continuous line across it
            ax.plot(xs[i:i + 2], ys[i:i + 2], color=DEEMPH, lw=3,
                    ls=(0, (4, 5)), zorder=2)
    for x, y, k in zip(xs, ys, kinds):
        ax.plot([x], [y], "o", ms=13, color=CRIMSON if k == "hbm" else AMBER,
                mec=SURFACE, mew=4, zorder=5)

    ax.annotate("one HBM print,\nno baseline behind it",
                xy=(18, 83779), xytext=(15.4, 3800),
                color=INK_1, fontsize=T_LABEL, fontweight=600, fontfamily=FAM,
                ha="center", arrowprops=dict(arrowstyle="-", color=INK_MUTE, lw=2))
    ax.text(3, 700, "labelled HBM-class,\nbut ~230 $/kg", color=INK_2,
            fontsize=T_LEG, fontfamily=FAM, ha="center")

    ax.set_yscale("log")
    ax.set_ylim(120, 3000000)
    ax.set_yticks([1000, 10000, 100000])
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda v, p: f"{int(v):,}" if v < 100000 else "100,000"))
    ax.set_xticks([0, 7, 11, 15, 18])
    ax.set_xticklabels(["2025-03", "2025-06", "2025-10", "2026-02", "2026-05"],
                       fontfamily=FAM)
    for t in ax.get_yticklabels() + ax.get_xticklabels(): t.set_fontfamily(FAM)

    # legend — identity never carried by colour alone
    keys = [plt.Line2D([0], [0], color=CRIMSON, lw=6),
            plt.Line2D([0], [0], color=AMBER, lw=6),
            plt.Line2D([0], [0], color=DEEMPH, lw=3, ls=(0, (4, 5)))]
    lg = ax.legend(keys, ["rows labelled HBM-class", "rows labelled NAND",
                          "regime break — not a movement"],
                   loc="upper left", frameon=False, fontsize=T_LEG,
                   labelcolor=INK_2, handlelength=1.4, handletextpad=0.7,
                   borderaxespad=0.6)
    for t in lg.get_texts(): t.set_fontfamily(FAM)

    fig.text(0.045, 1 - 62 / H, "One customs code, three different products",
             color=INK_1, fontsize=T_TITLE, fontweight=600, fontfamily=FAM,
             va="center")
    fig.text(0.045, 1 - 126 / H,
             "HS 8542.32.3000 export unit value · log scale, because the "
             "regimes differ by 300×",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.text(0.045, 0.125,
             "A trailing average is only meaningful over rows that share a product.",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.text(0.045, 0.088,
             "This one does not — so the change it produced was measuring HBM "
             "against NAND.",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.text(0.045, 44 / H,
             "Korea Customs Service, HS 8542.32.3000, export flow · every point "
             "verbatim from the ledger's own trade_facts table",
             color=INK_MUTE, fontsize=T_SOURCE, fontfamily=FAM, va="center")

    p = os.path.join(OUT, "ev-audit-regime-break.png")
    fig.savefig(p, facecolor=SURFACE, dpi=DPI); plt.close(fig)
    print("  ->", p)


if __name__ == "__main__":
    build()
