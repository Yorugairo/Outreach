"""The THIRD PERSPECTIVE (the design pass, 2026-09-07): Japan's RATE of selling - the month-on-month change in its Treasury
holdings, $bn, as SIGNED bars (E28: a drop goes DOWN and is blood red; a rise goes up and is green) - built from the holdings
object on disk (ev-japan-holdings-v1.series.json, US Treasury TIC), never fetched twice. Every bar is a difference of two
printed monthly totals; the facts carry the net. Run: python build_japan_selling.py"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "objects" / "ev-japan-holdings-v1.series.json"
OUT = HERE / "objects" / "ev-japan-selling-v1.series.json"


def month_of(x: float) -> dt.date:
    y = int(x); m = int(round((x - y) * 12)) + 1
    return dt.date(y, m, 1)


def main() -> int:
    h = json.loads(SRC.read_text(encoding="utf-8"))
    pts = h["series"][0]["pts"]
    peak_i = next(i for i, (x, _v) in enumerate(pts) if abs(x - (2026 + 1 / 12)) < 1e-3)   # February 2026, the peak
    window = pts[peak_i - 1: len(pts)]   # January's total as the base, then each month's change through the latest print
    bars = []
    for (x0, v0), (x1, v1) in zip(window, window[1:]):
        d = round(v1 - v0, 1)
        bars.append({"label": month_of(x1).strftime("%b"), "value": d, "color": "neg" if d < 0 else "pos",
                     "note": f"{month_of(x0).strftime('%b')} {v0:,.1f} -> {month_of(x1).strftime('%b')} {v1:,.1f}"})
    net = round(window[-1][1] - window[0][1], 1)
    sold = round(sum(b["value"] for b in bars if b["value"] < 0), 1)
    obj = {
        "title": "Japan's rate of selling",
        "sub": f"Month-on-month change in Japan's Treasury holdings, $bn, {month_of(window[1][0]).strftime('%b')}-{month_of(window[-1][0]).strftime('%b %Y')}",
        "src": f"US Treasury TIC · {h.get('fetched', '')}",
        "src_style": "compact",
        "yunit": "$bn",
        "bars": bars,
        "status": "REAL",
        "fetched": h.get("fetched"),
        "facts": {"net_change_bn": net, "since_peak_bn": round(window[-1][1] - window[1][1], 1), "sold_in_down_months_bn": sold, "months": len(bars),
                  "from_total": window[0][1], "to_total": window[-1][1], "peak_month": h["facts"].get("peak_month"), "latest_month": h["facts"].get("latest_month")},
        "note": "The design pass (2026-09-07): the third perspective on the holdings - the RATE of selling. Each bar is the difference of two "
                "printed monthly totals in ev-japan-holdings-v1 (US Treasury TIC); the sign is the geometry (E28).",
        "derived_from": "ev-japan-holdings-v1.series.json",
    }
    OUT.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    print(f"wrote {OUT}: {[(b['label'], b['value']) for b in bars]} net {net} sold {sold}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
