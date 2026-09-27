"""P72 T53 (a) (R26-412 (a)) - THE ICEBERG'S EVIDENCE: one object pairing the borrowing you can see with what sits under it.

    python content/video_engine/projects/_proofs/p72-t53/derive_iceberg.py            # --check (the default): exit 1 when stale
    python content/video_engine/projects/_proofs/p72-t53/derive_iceberg.py --write    # (re)write the committed object

Steel and Paper H row 16: "And that's the borrowing you can see. Go into the filings and there's another eight hundred and
twenty-two billion in lease commitments ... that have never landed on a balance sheet." P71 T34 stopped `the-hidden-base`
because no committed object paired the two stocks (its lab page re-derived them in a gitignored dir). This writes ONE:
`evidence/objects/ev-leases-iceberg-v1.series.json`, a bars page of one stacked bar - the hidden part (the leases) at the
base, under a water rule at their top (`hlines[0].water`, the balance sheet), the visible part (the bonds) above it - and
`pair` naming each figure's basis. Every value is READ, never typed:

  hidden   the leases record's "Latest filings" row (`evidence/ev-doc-leases.html`: "Latest filings $822 billion" - the
           script's figure is the latest; the record's end-February $675B row is the earlier print, P71 T34's draft 1 read
           that one by mistake)
  visible  the issuance series' own points 2020-2025, summed (`ev-debt-issuance-line-v1`: 2020-24 at the dossier's $28B
           a-year average, 2025's $121B) - OUR arithmetic, named as such on the page's source line and in `basis`

Nothing else is read or written. The object records `derived_from`, `basis`, `proof` (each quote verbatim in its record)
and its provenance, the convention `ev-memory-monitor-row22-v1` set.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
ISSUANCE = EP / "evidence/objects/ev-debt-issuance-line-v1.series.json"
LEASES = EP / "evidence/ev-doc-leases.html"
OUT = EP / "evidence/objects/ev-leases-iceberg-v1.series.json"
LEASES_ROW = re.compile(r"Latest filings\s*\$(\d[\d,]*)\s*billion")
FIRST, LAST = 2020, 2025          # the years "the borrowing you can see" covers: the series' own 2020-24 average and 2025


def _rel(p: Path) -> str:
    return p.relative_to(REPO).as_posix()


def _leases_text() -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", LEASES.read_text(encoding="utf-8")))


def leases_latest() -> int:
    """The filings' lease commitments, US$ billions - the record's "Latest filings" row."""
    m = LEASES_ROW.search(_leases_text())
    if not m:
        raise SystemExit(f"FAIL: no 'Latest filings $<n> billion' row in {_rel(LEASES)}")
    return int(m.group(1).replace(",", ""))


def _issuance_pts() -> list:
    obj = json.loads(ISSUANCE.read_text(encoding="utf-8"))
    return next(s["pts"] for s in obj["series"] if s.get("label") == "issuance")


def bonds_2020_25() -> int:
    """The bonds the builders issued 2020-25, US$ billions - the issuance series' own yearly points, summed."""
    vals = [v for x, v in _issuance_pts() if FIRST <= x <= LAST]
    if len(vals) != LAST - FIRST + 1:
        raise SystemExit(f"FAIL: {_rel(ISSUANCE)} has {len(vals)} yearly issuance points in {FIRST}-{LAST}, not {LAST - FIRST + 1}")
    return int(sum(vals))


def quote_holds(proof: dict) -> bool:
    """A proof entry's quote stands verbatim in its record (an HTML record read as its text)."""
    path = REPO / proof["path"]
    text = _leases_text() if path == LEASES else path.read_text(encoding="utf-8")
    return proof["quote"] in text


def derive() -> dict:
    hidden, visible = leases_latest(), bonds_2020_25()
    pts = [p for p in _issuance_pts() if FIRST <= p[0] <= LAST]
    issuance = json.loads(ISSUANCE.read_text(encoding="utf-8"))
    row = LEASES_ROW.search(_leases_text()).group(0)
    return {
        "title": "The borrowing you can see - and what sits under it",
        "sub": "US$ billions: bonds the builders issued 2020-25, over lease commitments not yet on a balance sheet",
        "src": f"Bonds: {issuance['src']} - {FIRST}-{LAST} summed (our arithmetic); leases: hyperscaler 10-Q filings, latest",
        "unit": "$", "unit_suffix": "B",
        "hlines": [{"y": hidden, "label": "the balance sheet", "color": "deemph", "water": True}],
        "bars": [{"label": "What they owe", "value": hidden + visible, "color": "deemph",
                  "segments": [{"name": "Lease commitments", "value": hidden, "color": "crimson"},
                               {"name": "Bonds issued", "value": visible, "color": "deemph"}]}],
        "pair": {"hidden": {"value": hidden, "name": "Lease commitments", "basis": "the filings' latest row - not yet on a balance sheet"},
                 "visible": {"value": visible, "name": "Bonds issued", "basis": f"{FIRST}-{LAST} issuance, summed - on the balance sheet"}},
        "derived_from": ["ev-debt-issuance-line-v1", "ev-doc-leases"],
        "basis": [{"figure": f"${visible}B", "says": f"the issuance series' {len(pts)} yearly points {FIRST}-{LAST} summed: "
                                                      + " + ".join(str(v) for _, v in pts), "from": pts},
                  {"figure": f"${hidden}B", "says": "the leases record's 'Latest filings' row, read as written"},
                  {"figure": f"${hidden + visible}B", "says": "the two parts, the bar's whole"}],
        "proof": [{"kind": "object", "path": _rel(ISSUANCE), "locator": "series[label=issuance].pts", "quote": '"label": "issuance"'},
                  {"kind": "html", "path": _rel(LEASES), "locator": "the 'Latest filings' row", "quote": row}],
        "provenance_note": "P72 T53 (a), 2026-09-27: derived by content/video_engine/projects/_proofs/p72-t53/derive_iceberg.py "
                           "from the two committed records named in derived_from - every value read, none typed; the two "
                           "sources are unchanged. The visible total is our sum of the series' yearly points (the 2020-24 "
                           "years carry the dossier's $28B a-year average), named on the page's source line.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="(re)write the committed object")
    args = ap.parse_args()
    text = json.dumps(derive(), indent=1, ensure_ascii=False) + "\n"
    if args.write:
        OUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {_rel(OUT)}")
        return 0
    if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
        print(f"STALE: {_rel(OUT)} is not the derivation - run with --write")
        return 1
    print(f"in sync: {_rel(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
