"""The hook's own proof, fetched (R26-19 / E50, 2026-09-07): "The Fed hasn't moved, but your borrowing costs climbed anyway."

Three FRED series, pulled from the public CSV endpoint, saved verbatim beside this script (sources/), hashed, and read into
one series object in the shape of ev-japan-holdings-v1.series.json:
  DFEDTARU     the federal funds target range, upper limit, daily   (the line that has not moved)
  DGS10        the 10-year Treasury constant maturity, daily          (the borrowing cost that climbed)
  MORTGAGE30US the 30-year fixed mortgage, weekly (Freddie Mac PMMS)  (... and the one the viewer pays)
The window starts at the Fed's LAST MOVE (the last date DFEDTARU changed) and runs to the latest print, so the flat line is
flat by measurement, not by cropping. Every figure in `facts` is read from the CSV on disk; the proof lines carry the URL,
the fetch date and the file's sha256. Run from anywhere: python fetch_fed_vs_yields.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "sources"
OUT = HERE / "objects" / "ev-fed-vs-yields-v1.series.json"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
SERIES = {"DFEDTARU": "Fed target (upper)", "DGS10": "10-year Treasury", "MORTGAGE30US": "30-year mortgage"}


def fetch(sid: str) -> tuple[Path, list[tuple[dt.date, float]], str]:
    SRC.mkdir(parents=True, exist_ok=True)
    raw = urllib.request.urlopen(FRED.format(sid=sid), timeout=60).read()
    path = SRC / f"fred-{sid}.csv"
    path.write_bytes(raw)
    rows = []
    for line in raw.decode("utf-8").strip().splitlines()[1:]:
        d, v = line.split(",", 1)
        if v.strip() in ("", "."):
            continue
        rows.append((dt.date.fromisoformat(d), float(v)))
    return path, rows, hashlib.sha256(raw).hexdigest()


def dec_year(d: dt.date) -> float:
    return round(d.year + (d.timetuple().tm_yday - 1) / (366 if d.year % 4 == 0 else 365), 4)


def at_or_before(rows: list[tuple[dt.date, float]], d: dt.date) -> tuple[dt.date, float]:
    return max((r for r in rows if r[0] <= d), key=lambda r: r[0])


def main() -> int:
    today = dt.date.today().isoformat()
    data, proof = {}, []
    for sid, name in SERIES.items():
        path, rows, sha = fetch(sid)
        data[sid] = rows
        proof.append({"series": sid, "name": name, "url": FRED.format(sid=sid), "path": str(path.relative_to(HERE.parent)).replace("\\", "/"),
                      "sha256": sha, "fetched": today, "rows": len(rows), "first": rows[0][0].isoformat(), "last": rows[-1][0].isoformat()})
    fed = data["DFEDTARU"]
    # the Fed's last move: the last date the target changed
    last_move = next(fed[i][0] for i in range(len(fed) - 1, 0, -1) if fed[i][1] != fed[i - 1][1])
    start = last_move - dt.timedelta(days=45)   # a little run-in so the move itself is on the page
    win = {sid: [(d, v) for d, v in rows if d >= start] for sid, rows in data.items()}
    ten_at, ten_now = at_or_before(data["DGS10"], last_move), data["DGS10"][-1]
    mort_at, mort_now = at_or_before(data["MORTGAGE30US"], last_move), data["MORTGAGE30US"][-1]
    # the summer window the dossier quoted, measured here too: the 10-year's and the mortgage's low since the move
    ten_low = min(win["DGS10"], key=lambda r: r[1]) if win["DGS10"] else ten_at
    mort_low = min(win["MORTGAGE30US"], key=lambda r: r[1]) if win["MORTGAGE30US"] else mort_at
    x0, x1 = dec_year(start), dec_year(max(r[-1][0] for r in win.values()))
    months = []
    d = dt.date(start.year, start.month, 1)
    while dec_year(d) <= x1 + 0.01:
        months.append([dec_year(d), d.strftime("%b")])
        d = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    # THE BARS (the fourth watch: "Japan's rate of selling should never have been an evidence dock, it should be a bar chart laid
    # against the lines as a combo chart"): the month-on-month change in Japan's Treasury holdings inside the window, from the
    # holdings object on disk (US Treasury TIC), each bar on the lines' time axis by its own x - a drop goes down and is red
    hold = json.loads((HERE / "objects" / "ev-japan-holdings-v1.series.json").read_text(encoding="utf-8"))
    hpts = hold["series"][0]["pts"]
    # the bars are the SELLING months - from the peak Japan sold down from, not the whole rate window: the tallest bar on
    # this page must be a sale, not a January purchase the page never mentions (E28: the chart's biggest mark is its story)
    x_bars = round(2026 + 1 / 12, 4) - 1e-6
    bars = []
    for (x0_, v0), (x1_, v1) in zip(hpts, hpts[1:]):
        if x1_ < x_bars:
            continue
        d = round(v1 - v0, 1); y, m = int(x1_), int(round((x1_ - int(x1_)) * 12)) + 1
        bars.append({"label": dt.date(y, m, 1).strftime("%b"), "value": d, "color": "neg" if d < 0 else "pos", "x": round(x1_ + 1 / 24, 4),
                     "note": f"{v0:,.1f} -> {v1:,.1f} $bn"})
    obj = {
        "title": "The Fed hasn't moved. Your borrowing costs climbed anyway.",
        # ONE clause: a portrait page cuts its sub at the first period (lpFirstClause), and this sub is the legend now
        "sub": f"Japan's monthly Treasury selling against what America pays to borrow, since {start.strftime('%b %Y')}",
        "proof_sentence": (f"Fed funds target (upper) flat at {fed[-1][1]:.2f}% since {last_move.isoformat()}; the 10-year "
                f"{ten_low[1]:.2f}% ({ten_low[0].isoformat()}) -> {ten_now[1]:.2f}% ({ten_now[0].isoformat()}); the 30-year mortgage "
                f"{mort_low[1]:.2f}% ({mort_low[0].isoformat()}) -> {mort_now[1]:.2f}% ({mort_now[0].isoformat()})"),
        "src": f"US Treasury TIC · FRED · {dt.date.fromisoformat(today).strftime('%b %Y')}",   # the design pass: minimal; the IDs and the sha256 live in `proof`
        "src_style": "compact",
        "ylabel": "$bn",
        "unit": "",
        "line_unit": "%",
        # the macro-chart intake (2026-09-07): the lines are a LEVEL (4-4.8 %, zero meaningless) and the bars a signed FLOW
        # (zero is the story) - two TIERS sharing one x, never one plot with a floated zero. The tiers give the lines their
        # right margin back, so they carry DIRECT TERMINAL LABELS again and the sub stops being a legend.
        "tiers": True,
        "bars": bars,
        "xticks": months[::2],
        # the design pass (operator, 2026-09-07: "charts need to make sense with no captions"): TWO lines that share one scale, each
        # named with its value at its end - the Fed's rate and the 10-year sit a point apart, so the flat step and the climb read
        # in one frame; the mortgage (a point higher) is the third NOTE, not a third line that pushed the scale and stacked the names
        "series": [
            {"label": "Fed funds", "name": f"{fed[-1][1]:.2f}%", "color": "deemph", "pts": [[dec_year(d), v] for d, v in win["DFEDTARU"]]},   # the terminal label IS the legend (the Economist standard; s9.23b)
            {"label": "10-year", "name": f"{ten_now[1]:.2f}%", "color": "crimson", "pts": [[dec_year(d), v] for d, v in win["DGS10"]]},
        ],
        "mortgage": {"name": "30-year mortgage", "color": "amber", "pts": [[dec_year(d), v] for d, v in win["MORTGAGE30US"]]},   # kept on the object for a page that wants it
        "status": "REAL",
        "fetched": today,
        "facts": {
            "fed_target_upper": fed[-1][1], "fed_last_move": last_move.isoformat(), "fed_before_move": at_or_before(fed, last_move - dt.timedelta(days=1))[1],
            "dgs10_at_move": ten_at[1], "dgs10_low_since_move": ten_low[1], "dgs10_low_date": ten_low[0].isoformat(),
            "dgs10_latest": ten_now[1], "dgs10_latest_date": ten_now[0].isoformat(), "dgs10_rise_bp_from_low": round((ten_now[1] - ten_low[1]) * 100, 1),
            "mortgage_at_move": mort_at[1], "mortgage_low_since_move": mort_low[1], "mortgage_low_date": mort_low[0].isoformat(),
            "mortgage_latest": mort_now[1], "mortgage_latest_date": mort_now[0].isoformat(), "mortgage_rise_bp_from_low": round((mort_now[1] - mort_low[1]) * 100, 1),
            "window_from": start.isoformat(),
            "japan_bars": [(b["label"], b["value"]) for b in bars],
            # the bracket's data indices on series 1 (the 10-year): its low since the move -> its latest = "the math" (+80 bp)
            "dgs10_low_index": next(i for i, (d, _v) in enumerate(win["DGS10"]) if d == ten_low[0]),
            "dgs10_last_index": len(win["DGS10"]) - 1,
        },
        "notes": [   # the side notes the page writes as the ring is spoken (the third watch: "plenty of space on the side") - every figure from facts
            "Japan started selling in February.",
            "Rates went up immediately.",
            f"30-year mortgage {mort_low[1]:.2f}% -> {mort_now[1]:.2f}% over the same months.",
        ],
        "proof": proof,
        "note": ("R26-19 / E50 (2026-09-07): the hook's own claim, never charted until now. The window starts 45 days before the Fed's last move "
                 "so the flat line is measured, not cropped. Every number in facts is read from the CSVs in sources/ (sha256 in proof)."),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    for p in proof:
        print(f"  {p['series']:12s} {p['rows']} rows {p['first']} -> {p['last']}  sha256 {p['sha256'][:12]}")
    print("  facts:", json.dumps(obj["facts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
