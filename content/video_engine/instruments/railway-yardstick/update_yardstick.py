"""Update THE RAILWAY YARDSTICK - the operator's recurring instrument.

Fetches the four FRED series (keyless), appends a dated reading to
readings.jsonl, and regenerates the chart + live sidecar through the
episode's own builder so the instrument and the evidence never diverge.

    python update_yardstick.py
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EV = HERE.parents[1] / "projects/systems-and-blowups/steel-and-paper/evidence"
sys.path.insert(0, str(EV))


def main() -> int:
    import warnings; warnings.filterwarnings("ignore")
    import build_evidence_documents as B
    B.capital_formation_share()          # regenerates PNG + sidecar

    sc = json.loads((EV / "objects/ev-capital-formation-v1.series.json")
                    .read_text(encoding="utf-8"))
    narrow = sc["series"][0]["pts"][-1]
    broad = sc["series"][1]["pts"][-1]
    rec = {"date": dt.date.today().isoformat(),
           "quarter_x": narrow[0],
           "narrow_pct": narrow[1], "broad_pct": broad[1]}
    log = HERE / "readings.jsonl"
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"yardstick reading appended: narrow {narrow[1]:.1f}%  "
          f"broad {broad[1]:.1f}%  ({rec['date']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
