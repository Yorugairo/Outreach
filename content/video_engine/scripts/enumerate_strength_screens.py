"""Emit the strength loop's ENUMERATION ARTIFACTS - the anti-skip mechanism.

Operator diagnosis (2026-08-30): "why did you not run the full gates and
process? this has been a recurring issue." The mechanism behind every
recurrence: gates that emit artifacts run; gates that live in the
reviewer's reading get compressed into a claim of having run. A summary
of a review is indistinguishable from a review UNLESS the enumeration is
itself a required deliverable.

This script automates exactly what STRENGTH-LOOP s8 licenses - counts,
positions, adjacency - and emits candidate lists the reviewer must walk
and verdict PER ITEM. The loop's convergence claim is invalid without
these files and their verdicts in the strength log.

    python enumerate_strength_screens.py <VO.txt>

Emits <script>-SCREENS.md beside the input:
  X1  every connective/pronoun-opening sentence WITH its predecessor
  P6  every this/that/it/these opener (deixis candidates)
  P1J every And/Then-opening junction (AND-THEN risk)
  P5A repeated-initial bigrams (phonetic-anchor candidates + placement)
  P4C per-paragraph sentence-length runs (cadence wave vs metronome)
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


def sentences(text: str) -> list[str]:
    t = re.sub(r"`\[[a-z-]+\]`", "", text)
    t = " ".join(t.split())
    return [s.strip() for s in
            re.split(r"(?<=[.!?\"”])\s+(?=[A-Z\"“])", t) if s.strip()]


def main() -> int:
    src = Path(sys.argv[1])
    raw = src.read_text(encoding="utf-8")
    sents = sentences(raw)
    out = [f"# STRENGTH SCREENS — {src.name}",
           "",
           f"{len(sents)} sentences. Every candidate below requires a",
           "per-item verdict in the strength log (ok / FIXED / licensed /",
           "carryover). A convergence claim without this file walked is",
           "invalid — the enumeration IS the review.",
           ""]

    starters = (r"^(And|But|So|Which|Then|That's|That|This|These|Those|It|"
                r"It's|They|He|She|His|Her|Their|Now|Not|Because|Or|Nor|Yet)\b")
    x1 = [(i, sents[i-1], s) for i, s in enumerate(sents)
          if i and re.match(starters, s)]
    out += [f"## X1 — antecedent pairs ({len(x1)})", ""]
    for i, prev, s in x1:
        out += [f"- [{i}] `…{prev[-55:]}` → **{s[:80]}**"]

    dx = [(i, s) for i, s in enumerate(sents)
          if re.match(r"^(This|That|These|Those|It)\b", s)]
    out += ["", f"## P6 — deixis openers ({len(dx)})", ""]
    out += [f"- [{i}] {s[:90]}" for i, s in dx]

    j = [(i, sents[i-1][-40:], s) for i, s in enumerate(sents)
         if i and re.match(r"^(And|Then)\b", s)]
    out += ["", f"## P1J — additive junctions, AND-THEN risk ({len(j)})", ""]
    out += [f"- [{i}] `…{p}` → {s[:80]}" for i, p, s in j]

    # phonetic-anchor candidates: >=3 words sharing an initial in one sentence
    pa = []
    for i, s in enumerate(sents):
        words = [w.lower() for w in re.findall(r"[A-Za-z']+", s) if len(w) > 3]
        for ch, n in Counter(w[0] for w in words).items():
            if n >= 3:
                pa.append((i, ch, s))
                break
    out += ["", f"## P5A — phonetic-anchor candidates ({len(pa)}) — "
            "legal ONLY at promise / payoff / tell", ""]
    out += [f"- [{i}] ({c}×) {s[:88]}" for i, c, s in pa]

    out += ["", "## P4C — cadence runs (words per sentence, per paragraph)", ""]
    body = re.sub(r"`\[[a-z-]+\]`", "", raw)
    for n, para in enumerate([p for p in body.split("\n\n") if p.strip()], 1):
        runs = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences(para)]
        flat = (" ← FLAT?" if len(runs) >= 4 and
                max(runs) - min(runs) <= 4 else "")
        out += [f"- ¶{n}: {runs}{flat}"]

    dest = src.with_name(src.stem.replace("-VO", "") + "-SCREENS.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{dest.name}: X1={len(x1)} deixis={len(dx)} junctions={len(j)} "
          f"anchors={len(pa)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
