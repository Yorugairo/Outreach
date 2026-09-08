"""The top five foreign holders of US Treasuries, and the slice Japan sold (P48 T4, the recast's beat).

The operator, 2026-09-07: *"rotate it into a pie chart for example that shows the holdings of top 5 foreign investors of USA
including the japan holdings and animate it to show the 1/10 of the pie that got sold - it's literally all there for us."*

One source, the same file the holdings page already reads - TIC Table 5, the Major Foreign Holders release - fetched whole,
saved verbatim beside this script (sources/), hashed, and parsed for EVERY country row rather than the four the holdings
build names. The five biggest holders at the latest month are the page's whole; Japan's wedge then splits into what it still
holds and what it has sold since its peak, and that sold piece is the page's claim.

E53 s1 as amended 2026-09-07 bounds this page: ONE named slice is the claim (Japan's), every other slice is muted context,
the figure the claim turns on is WRITTEN, and the slice count is five. Nothing here compares one country's angle to another.

    python fetch_top_holders.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "sources"
OUT = HERE / "objects" / "ev-top-holders-v1.series.json"
TIC_URL = "https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.txt"
HOLDINGS = HERE / "objects" / "ev-japan-holdings-v1.series.json"
# not a country: the release's own totals and its "Of Which:" aggregates, each of which would out-rank every real holder
AGGREGATES = ("grand total", "all other", "of which")
# a wedge is narrow, so a name that will not fit in one is shortened FOR THE PAGE; the release's own name stays on the object
SHORT = {"United Kingdom": "UK", "China, Mainland": "China", "Korea, South": "Korea", "United Arab Emirates": "UAE"}


def month_label(m: str) -> str:
    """'2026-02' -> "February 2026" - the page names its month in words, never as a code (E28)."""
    y, mo = m.split("-")
    return dt.date(int(y), int(mo), 1).strftime("%B %Y")


def die(msg: str) -> None:
    raise SystemExit(f"  FAIL: {msg}")


def fetch() -> tuple[Path, str, list[str]]:
    SRC.mkdir(parents=True, exist_ok=True)
    try:
        raw = urllib.request.urlopen(TIC_URL, timeout=60).read()
    except Exception as e:                                          # noqa: BLE001
        die(f"TIC Table 5 unreachable ({type(e).__name__}) - refusing to emit typed numbers")
    path = SRC / "tic-slt-table5.txt"
    path.write_bytes(raw)
    lines = [l.rstrip() for l in raw.decode("utf-8", "replace").splitlines() if l.strip()]
    return path, hashlib.sha256(raw).hexdigest(), lines


def parse(lines: list[str]) -> tuple[list[str], dict[str, list[float]]]:
    """Every country row in the release, not only the named four: {'Japan': [newest, ...], ...}."""
    header = next((l for l in lines if l.startswith("Country")), None)
    if not header:
        die("TIC Table 5: no Country header row - the release format changed")
    months = header.split("\t")[1:]                                  # newest first
    rows: dict[str, list[float]] = {}
    for l in lines:
        cells = l.split("\t")
        if len(cells) < 2 or not cells[0].strip():
            continue
        name = cells[0].strip()
        try:
            vals = [float(x.replace(",", "")) for x in cells[1:len(months) + 1]]
        except ValueError:
            continue                                                 # a header, a footnote, a blank block
        if len(vals) == len(months):
            rows[name] = vals
    for want in ("Japan", "Grand Total"):
        if want not in rows:
            die(f"TIC Table 5: row '{want}' missing - the release format changed")
    return months, rows


def main() -> int:
    today = dt.date.today().isoformat()
    path, sha, lines = fetch()
    months, rows = parse(lines)
    holders = {k: v for k, v in rows.items() if not any(k.lower().startswith(a) for a in AGGREGATES)}

    # Japan's own peak and what it has sold since - read from the holdings object already on disk (the same TIC release),
    # so the pie's claim and the line's claim are the SAME number and cannot drift apart
    hold = json.loads(HOLDINGS.read_text(encoding="utf-8"))
    hf = hold["facts"]
    sold = abs(float(hf["drop_bn"]))                                 # $bn, positive: the size of the slice that went
    jp_now, jp_peak = float(hf["latest"]), float(hf["peak"])

    # THE PIE'S MONTH IS THE PEAK, not the latest. The claim is "a tenth of this went", and a slice can only be shown
    # leaving a whole it was still part of: at Feb 2026 Japan holds 1,239.3 and the sold 122.6 is INSIDE its wedge, so the
    # peel is exact geometry and what remains is exactly what Japan holds today. Drawn at June the sold slice would have to
    # be added back to a pie it is not in - a picture of a number rather than of the thing.
    pie_month = hf["peak_month"]
    if pie_month not in months:
        die(f"the peak month {pie_month} is not in this release ({months[0]} .. {months[-1]}) - refetch the holdings")
    mi = months.index(pie_month)
    top = sorted(holders.items(), key=lambda kv: -kv[1][mi])[:5]
    if len(top) < 5:
        die(f"only {len(top)} country rows parsed - the release format changed")
    total = rows["Grand Total"][mi]

    names = [k for k, _v in top]
    vals = [round(v[mi], 1) for _k, v in top]
    ji = names.index("Japan")
    if abs(vals[ji] - jp_peak) > 0.05:
        die(f"Japan at {pie_month} is {vals[ji]} in the table and {jp_peak} on the holdings page - one of them is stale")
    latest = pie_month
    five = sum(vals)
    obj = {
        "title": "Who owns America's debt",
        "sub": f"The five biggest foreign holders of US Treasuries, ${five:,.0f}B of a ${total:,.0f}B total, {month_label(pie_month)}",
        "src": f"US Treasury TIC Table 5 - {dt.date.fromisoformat(today).strftime('%b %Y')}",
        "src_style": "compact",
        "unit": "$bn",
        # the SHARES the page draws. E53 s1 (amended): five slices, one of them the claim, the rest muted context.
        # Japan's wedge is TEAL, not red: the piece that LEAVES is what goes blood red (E28), and a wedge already red
        # could not then show a loss. Each slice carries its own figure string, so the page never formats a number.
        "shares": [{"label": n, "short": SHORT.get(n, n), "value": v, "value_string": f"${v:,.1f}B",
                    "color": ("teal" if n == "Japan" else "deemph")} for n, v in zip(names, vals)],
        "emphasize": ji,
        # the claim: a tenth of Japan's own wedge, gone since the peak. The figure is WRITTEN, so no angle is estimated.
        "peel": {"index": ji, "value": round(-sold, 1), "value_string": f"-${sold:,.1f}B",
                 "label": f"sold since {month_label(pie_month)}", "of_pct": round(sold / jp_peak * 100, 1),
                 "leaves": round(jp_peak - sold, 1), "leaves_string": f"${jp_peak - sold:,.1f}B left"},
        "status": "REAL",
        "fetched": today,
        "facts": {
            "month": pie_month, "grand_total": total, "top5_total": round(five, 1), "japan_latest_month": hf["latest_month"],
            "top5": [{"name": n, "value": v, "share_of_total_pct": round(v / total * 100, 1)} for n, v in zip(names, vals)],
            "japan_index": ji, "japan_now": jp_now, "japan_peak": jp_peak, "japan_peak_month": hf["peak_month"],
            "sold_bn": round(sold, 1), "sold_pct_of_japan_peak": round(sold / jp_peak * 100, 1),
            "sold_pct_of_top5": round(sold / five * 100, 1),
            "country_rows_parsed": len(holders),
        },
        "proof": [{"source": "US Treasury TIC Table 5", "url": TIC_URL, "path": str(path.relative_to(HERE.parent)).replace("\\", "/"),
                   "sha256": sha, "fetched": today, "month": latest, "country_rows": len(holders)}],
        "note": ("P48 T4 / E53 s1 as amended 2026-09-07: a pie is allowed here because the claim is about ONE named slice "
                 "(Japan's), every other slice is muted, the figure is written on the page, and there are five slices. "
                 "Japan's holdings figure is read from ev-japan-holdings-v1 so the two pages cannot disagree."),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  TIC Table 5  {len(holders)} country rows, month {latest}, sha256 {sha[:12]}")
    for n, v in zip(names, vals):
        print(f"    {n:22s} ${v:>9,.1f}B  {v / total * 100:5.1f}% of all foreign holdings")
    print(f"  Japan sold ${sold:,.1f}B since {month_label(pie_month)} = {obj['facts']['sold_pct_of_japan_peak']}% of its "
          f"own wedge; what is left, ${jp_peak - sold:,.1f}B, is what it holds today ({hf['latest_month']}: ${jp_now:,.1f}B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
