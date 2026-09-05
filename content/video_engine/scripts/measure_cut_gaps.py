"""P40 T1, reference-first: where do the reference's cuts land relative to the speech, and
where do ours? The gap threshold for M13 comes from Wealth Logic's practice, not from ours
(operator, 2026-09-04: "is basing the gap threshold off our own work really the right way?").

Inputs: a word timeline (Whisper words with s/e) and a list of cut times. For every cut the
script finds the acoustic gap it lands in - the silence between the previous word's end and
the next word's start - or reports it as mid-word (gap 0) when it falls inside a word.

    python measure_cut_gaps.py --words <words.json> --cuts <ledger.md | timeline.json> [--label X] [--json out]
"""
from __future__ import annotations

import argparse
import json
import re
import statistics as st
import sys
from pathlib import Path

THRESHOLDS = (0.20, 0.30, 0.45, 0.60)


def load_words(path: Path) -> list[tuple[float, float]]:
    d = json.loads(path.read_text(encoding="utf-8"))
    words = d["words"] if isinstance(d, dict) else d
    out = []
    for w in words:
        s = w.get("s", w.get("start")); e = w.get("e", w.get("end"))
        if s is not None and e is not None:
            out.append((float(s), float(e)))
    return sorted(out)


def load_cuts(path: Path) -> list[float]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        tl = json.loads(text)
        cuts = {float(s["span"][0]) for s in tl["scenes"]} | {float(d["enter"]) for s in tl["scenes"] for d in s.get("docks", [])}
        return sorted(c for c in cuts if c > 0)
    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*(\d\d):(\d\d\.\d)\s*\|", text, re.M)
    return sorted(int(m) * 60 + float(s) for _, m, s in rows)[1:]   # shot 1 starts at 0 - not a cut


def gaps(words: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """(start, end) of every silence between consecutive words."""
    return [(a_e, b_s) for (_, a_e), (b_s, _) in zip(words, words[1:]) if b_s > a_e]


def land(cut: float, words: list[tuple[float, float]], tol: float = 0.05) -> dict:
    """The gap a cut lands in (with tol for frame/Whisper jitter), else mid-word."""
    for a, b in gaps(words):
        if a - tol <= cut <= b + tol:
            width = b - a
            pos = 0.0 if width <= 0 else max(0.0, min(1.0, (cut - a) / width))
            return {"cut": cut, "gap": round(width, 3), "pos": round(pos, 2), "mid_word": False}
    return {"cut": cut, "gap": 0.0, "pos": None, "mid_word": True}


def measure(words: list[tuple[float, float]], cuts: list[float]) -> dict:
    rows = [land(c, words) for c in cuts]
    in_gap = [r for r in rows if not r["mid_word"]]
    widths = sorted(r["gap"] for r in in_gap)
    all_gaps = sorted(b - a for a, b in gaps(words))
    runtime = words[-1][1] if words else 0.0
    q = lambda xs, p: xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None
    return {
        "cuts": len(cuts), "mid_word": len(rows) - len(in_gap), "mid_word_share": round((len(rows) - len(in_gap)) / max(1, len(rows)), 3),
        "cut_gap_p25_p50_p75": [q(widths, .25), q(widths, .5), q(widths, .75)],
        "cut_gap_p10_p20": [q(widths, .10), q(widths, .20)],
        "share_of_cuts_in_gap_at_least": {str(t): round(sum(1 for r in in_gap if r["gap"] >= t) / max(1, len(rows)), 3) for t in THRESHOLDS},
        "cut_position_in_gap_mean": round(st.mean(r["pos"] for r in in_gap), 2) if in_gap else None,
        "cut_position_in_gap_median": round(st.median(r["pos"] for r in in_gap), 2) if in_gap else None,
        "gaps_per_minute_at_least": {str(t): round(sum(1 for g in all_gaps if g >= t) / max(1e-9, runtime / 60), 1) for t in THRESHOLDS},
        "all_gaps_p50_p90": [q(all_gaps, .5), q(all_gaps, .9)],
        "runtime_s": round(runtime, 1), "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", required=True); ap.add_argument("--cuts", required=True)
    ap.add_argument("--label", default=""); ap.add_argument("--json")
    args = ap.parse_args()
    m = measure(load_words(Path(args.words)), load_cuts(Path(args.cuts)))
    rows = m.pop("rows")
    print(f"== {args.label or args.cuts}")
    for k, v in m.items():
        print(f"  {k:<34} {v}")
    if args.json:
        Path(args.json).write_text(json.dumps({**m, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
