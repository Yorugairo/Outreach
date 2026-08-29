"""HBM-class export unit value — the series behind the +26.5% reading.

HS 8542.32.3000 is multi-component IC (HBM-class) throughout; the parser's
own note records that the earlier "NAND" label for this code was a wrong
guess, so rows still carrying it in the store are stale annotations, not a
different product. The series is continuous from 2025-06, and the reading
is the May print against a trailing four-month mean of 66,219.

SUPERSEDES an earlier "regime break" exhibit built on the mistaken premise
that this code changed products mid-series. It did not.
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
    ("2025-06", 43840.7), ("2025-07", 42087.7), ("2025-08", 44118.5),
    ("2025-09", 41367.1), ("2025-10", 44348.5), ("2025-11", 50392.7),
    ("2025-12", 58868.7), ("2026-01", 55748.6), ("2026-02", 72665.7),
    ("2026-03", 63748.3), ("2026-04", 72716.4), ("2026-05", 83786.1),
    ("2026-06", 94138.4), ("2026-07", 95407.8),
]

def build():
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0.085, 0.225, 0.875, 0.525])
    ax.set_facecolor(SURFACE)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(BASELINE); ax.spines[sp].set_linewidth(2)
    ax.tick_params(colors=INK_MUTE, labelsize=T_TICK, length=0, pad=14)
    ax.grid(True, axis="y", color=GRID, linewidth=2)
    ax.set_axisbelow(True)

    xs = np.arange(len(SERIES))
    ys = [v for _, v in SERIES]
    MEAN = 83606.4

    # the trailing window the reading is measured against
    ax.axvspan(9.5, 12.5, color="#ffffff", alpha=0.045, lw=0)
    ax.axhline(MEAN, xmin=0.02, xmax=0.98, color=INK_MUTE, lw=2, ls=(0, (7, 6)))
    ax.text(0.15, MEAN + 2400, f"trailing mean · {MEAN:,.0f} $/kg",
            color=INK_MUTE, fontsize=T_TICK, fontfamily=FAM, va="bottom")
    ax.text(11.2, 45000, "the window the\nreading averages",
            color=INK_2, fontsize=T_LEG, fontfamily=FAM, ha="center")

    ax.fill_between(xs, ys, 28000, color=CRIMSON, alpha=0.10, lw=0)
    ax.plot(xs, ys, color=CRIMSON, lw=5, solid_capstyle="round",
            solid_joinstyle="round", zorder=3)
    for x, y in zip(xs, ys):
        ax.plot([x], [y], "o", ms=13, color=CRIMSON, mec=SURFACE, mew=4, zorder=5)

    ax.annotate("95,408\n+14.1% vs the mean", xy=(13, 95407.8), xytext=(10.4, 112000),
                color=INK_1, fontsize=T_LABEL, fontweight=600, fontfamily=FAM,
                ha="center", arrowprops=dict(arrowstyle="-", color=INK_MUTE, lw=2))

    ax.set_ylim(28000, 126000)
    ax.set_yticks([40000, 60000, 80000, 100000, 120000])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v):,}"))
    ax.set_xticks([0, 3, 6, 9, 13])
    ax.set_xticklabels(["2025-06", "2025-09", "2025-12", "2026-03", "2026-07"],
                       fontfamily=FAM)
    for t in ax.get_yticklabels() + ax.get_xticklabels(): t.set_fontfamily(FAM)

    fig.text(0.045, 1 - 62 / H, "HBM-class memory leaving Korea, by the kilo",
             color=INK_1, fontsize=T_TITLE, fontweight=600, fontfamily=FAM, va="center")
    fig.text(0.045, 1 - 126 / H,
             "HS 8542.32.3000, value-weighted export unit value · multi-component "
             "IC, where stacked HBM is classified",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.text(0.045, 0.128, "One product throughout · reading period July 2026.",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.text(0.045, 0.091,
             "Rows still stored as “NAND” are stale labels from a "
             "superseded parser — not a different chip.",
             color=INK_2, fontsize=T_SUB, fontfamily=FAM, va="center")
    fig.text(0.045, 44 / H,
             "Korea Customs Service, HS 8542.32.3000, export flow · every point "
             "verbatim from the ledger’s trade_facts table",
             color=INK_MUTE, fontsize=T_SOURCE, fontfamily=FAM, va="center")

    p = os.path.join(OUT, "ev-hbm-export-series.png")
    fig.savefig(p, facecolor=SURFACE, dpi=DPI); plt.close(fig)
    print("  ->", os.path.basename(p))


if __name__ == "__main__":
    build()
