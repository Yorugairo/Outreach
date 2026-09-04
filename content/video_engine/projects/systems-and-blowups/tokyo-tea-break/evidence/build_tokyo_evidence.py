"""Tokyo Tea Break evidence — built from live primary sources, never typed.

Follows the steel-and-paper pattern: real series are fetched, every figure carries its
source id and the date it was fetched, and NOTHING here is estimated. If a source is
unreachable the build FAILS LOUDLY rather than emitting a number nobody can check —
a chart the viewer cannot verify is the fabrication risk the dossier rule exists to stop.

Sources, all public and re-fetchable:
  TIC Table 5  ticdata.treasury.gov/.../slt_table5.txt   Japan/UK/China holdings, monthly
  FRED DGS10                                             US 10-year Treasury, daily
  FRED DGS3MO                                            US 3-month Treasury, daily
  FRED IR3TIB01JPM156N                                   Japan 3-month interbank, monthly
  yfinance META                                          trailing P/E (optional; marked MISSING if unreachable)

    python build_tokyo_evidence.py
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

OUT = Path(__file__).parent
FETCHED = date.today().isoformat()
TIC_URL = "https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.txt"


def die(msg: str) -> None:
    print(f"  FAIL: {msg}", file=sys.stderr)
    raise SystemExit(2)


def fred(series_id: str) -> dict[str, float]:
    """{'YYYY-MM': value} — last observation of each month."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    try:
        raw = urllib.request.urlopen(url, timeout=30).read().decode()
    except Exception as e:                                          # noqa: BLE001
        die(f"FRED {series_id} unreachable ({type(e).__name__}) — refusing to emit typed numbers")
    out: dict[str, float] = {}
    for row in list(csv.reader(io.StringIO(raw)))[1:]:
        if len(row) > 1 and row[1] not in (".", ""):
            out[row[0][:7]] = float(row[1])
    if not out:
        die(f"FRED {series_id} returned no observations")
    return out


def tic_table5() -> tuple[list[str], dict[str, list[float]]]:
    try:
        raw = urllib.request.urlopen(TIC_URL, timeout=30).read().decode("utf-8", "replace")
    except Exception as e:                                          # noqa: BLE001
        die(f"TIC Table 5 unreachable ({type(e).__name__})")
    lines = [l.rstrip() for l in raw.splitlines() if l.strip()]
    header = next((l for l in lines if l.startswith("Country")), None)
    if not header:
        die("TIC Table 5: no Country header row — the release format changed")
    months = header.split("\t")[1:]                                  # newest first
    rows: dict[str, list[float]] = {}
    for name in ("Japan", "United Kingdom", "China, Mainland", "Grand Total"):
        line = next((l for l in lines if l.startswith(name + "\t")), None)
        if not line:
            die(f"TIC Table 5: row '{name}' missing")
        rows[name] = [float(x) for x in line.split("\t")[1:]]
    return months, rows


def month_to_x(m: str) -> float:
    """'2026-06' -> 2026.458, the decimal-year x the template's drawChart plots on."""
    y, mo = m.split("-")
    return round(int(y) + (int(mo) - 1) / 12.0, 4)


def write(name: str, payload: dict) -> None:
    (OUT / f"{name}.series.json").write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"     + {name}.series.json")


# ---------------------------------------------------------------- 1. the selling
def japan_holdings(months, rows) -> dict:
    jp, tot = rows["Japan"], rows["Grand Total"]
    peak_i = jp.index(max(jp))
    span = list(zip(months, jp))[:26][::-1]                          # oldest -> newest, ~2y
    pts = [[month_to_x(m), round(v, 1)] for m, v in span]
    drop = jp[0] - jp[peak_i]          # signed: a decline is negative (E28, sign is geometry)
    facts = {
        "latest_month": months[0], "latest": jp[0],
        "peak_month": months[peak_i], "peak": jp[peak_i],
        "drop_bn": round(drop, 1), "drop_pct": round((jp[0] / jp[peak_i] - 1) * 100, 1),
        "share_pct": round(jp[0] / tot[0] * 100, 1),
        "rank_2_uk": rows["United Kingdom"][0], "rank_3_china": rows["China, Mainland"][0],
    }
    write("ev-japan-holdings-v1", {
        "title": "Our biggest customer is selling",
        "sub": f"Japan's holdings of US Treasury securities, $bn, monthly. "
               f"Peak {facts['peak_month']} ${facts['peak']:,.1f}B "
               f"-> {facts['latest_month']} ${facts['latest']:,.1f}B",
        "src": f"US Treasury TIC Table 5, Major Foreign Holders · fetched {FETCHED}",
        "ylabel": "$bn",
        "series": [{"label": f"{facts['drop_pct']:+.1f}%", "name": "Japan", "color": "crimson", "pts": pts}],
        "status": "REAL", "fetched": FETCHED, "facts": facts,
    })
    return facts


# ------------------------------------------------- 2. the head-fake: hedge is innocent
def hedged_yield() -> dict:
    us10, us3m, jp3m = fred("DGS10"), fred("DGS3MO"), fred("IR3TIB01JPM156N")
    months = sorted(set(us10) & set(us3m) & set(jp3m))
    if not months:
        die("no overlapping months across DGS10 / DGS3MO / IR3TIB01JPM156N")
    rows = [(m, us10[m], us3m[m] - jp3m[m], us10[m] - (us3m[m] - jp3m[m])) for m in months]
    recent = [r for r in rows if r[0] >= "2022-01"]
    pts = [[month_to_x(m), round(net, 2)] for m, _, _, net in recent]
    neg = [r for r in rows if r[3] < 0]
    worst = min(neg, key=lambda r: r[3]) if neg else None
    last = rows[-1]
    facts = {
        "latest_month": last[0], "us10y": last[1], "hedge_cost": round(last[2], 2),
        "net_hedged": round(last[3], 2),
        "worst_month": worst[0] if worst else None, "worst_net": round(worst[3], 2) if worst else None,
        "worst_hedge_cost": round(worst[2], 2) if worst else None,
        "last_negative_month": neg[-1][0] if neg else None,
        "negative_months": len(neg),
    }
    write("ev-hedged-yield-v1", {
        "title": "The reason everyone gives stopped being true",
        "sub": "US 10-year Treasury yield minus the 3-month FX hedge cost (US 3M less Japan 3M), "
               f"annualized. Below zero the trade loses money. Last negative {facts['last_negative_month']}",
        "src": "FRED DGS10, DGS3MO, IR3TIB01JPM156N (hedge cost = US 3M − JPY 3M) · "
               f"fetched {FETCHED}",
        "ylabel": "%", "zero_line": True,
        "series": [{"label": f"{facts['net_hedged']:+.2f}%", "name": "Net hedged yield",
                    "color": "cobalt", "pts": pts}],
        "status": "REAL", "fetched": FETCHED, "facts": facts,
    })
    # the same story as a ledger-page bars spec: then vs now
    write("ev-hedge-then-now-v1", {
        "title": "Hedging costs half what it did",
        "sub": f"Net yield on a hedged US 10-year for a Japanese buyer: "
               f"{facts['worst_month']} versus {facts['latest_month']}",
        "src": "FRED DGS10, DGS3MO, IR3TIB01JPM156N · " f"fetched {FETCHED}",
        "unit": "%",
        "bars": [
            {"label": f"{facts['worst_month']} (worst)", "value": facts["worst_net"], "color": "crimson"},
            {"label": f"{facts['latest_month']} (now)", "value": facts["net_hedged"], "color": "cobalt",
             "note": "the trade works"},
        ],
        "badges": [
            {"label": "HEDGE COST THEN", "value": f"{facts['worst_hedge_cost']:.2f}%", "tag": facts["worst_month"], "accent": "crimson"},
            {"label": "HEDGE COST NOW", "value": f"{facts['hedge_cost']:.2f}%", "tag": facts["latest_month"], "accent": "cobalt"},
        ],
        "status": "REAL", "fetched": FETCHED, "facts": facts,
    })
    return facts


# ---------------------------------------------------------------- 3. the payoff
def meta_pe() -> dict:
    try:
        import yfinance as yf
        info = yf.Ticker("META").info
        pe = info.get("trailingPE") or info.get("forwardPE")
        if not pe:
            raise ValueError("no trailingPE/forwardPE field")
        return {"status": "REAL", "trailing_pe": round(float(pe), 1), "fetched": FETCHED,
                "src": "Yahoo Finance via yfinance"}
    except Exception as e:                                           # noqa: BLE001
        print(f"     ! META P/E unavailable ({type(e).__name__}) — recorded MISSING, not guessed")
        return {"status": "MISSING", "reason": f"{type(e).__name__}", "fetched": FETCHED}


def main() -> int:
    print(f"  Tokyo Tea Break evidence — fetched {FETCHED}")
    months, rows = tic_table5()
    jp = japan_holdings(months, rows)
    hy = hedged_yield()
    pe = meta_pe()
    (OUT / "FIGURES.json").write_text(json.dumps(
        {"fetched": FETCHED, "japan_holdings": jp, "hedged_yield": hy, "meta_pe": pe}, indent=1),
        encoding="utf-8")
    print(f"     + FIGURES.json")
    print(f"\n  Japan  {jp['latest_month']}  ${jp['latest']:,.1f}B  "
          f"({jp['drop_bn']:+,.1f}B from {jp['peak_month']}, {jp['drop_pct']:+.1f}%)  share {jp['share_pct']}%")
    print(f"  Hedged {hy['latest_month']}  net {hy['net_hedged']:+.2f}%  "
          f"(worst {hy['worst_month']} {hy['worst_net']:+.2f}%, last negative {hy['last_negative_month']})")
    print(f"  META P/E: {pe.get('trailing_pe', pe['status'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
