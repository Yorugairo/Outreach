"""Derive pause candidates from the PAUSE GRAMMAR - the generative pass.

Operator (2026-08-30, the 'two-thirds' miss): the grammar (doc 37
s18-19) DESCRIBES pause classes but nothing GENERATES sites from it -
the plan is hand-placed from probe listens, so any site never
ear-flagged silently gets the tightened default. This pass scans the
VO script for grammar classes, diffs against the standing plan, and
prints the sites the plan is missing. The operator adjudicates; the
ear stays the instrument of record.

Classes detected (text-only, deliberately conservative):
  stat-settle -> era-shift : sentence lands on a number, next opens a
                             new time frame ........... FULL 1.0
  stat-settle              : sentence lands on a number 0.45 half
  era-shift breath         : next sentence opens a time frame
                             without a landed stat .... 0.45 half
  paragraph breath         : VO paragraph boundary ..... 0.6 lead

    python derive_pauses.py
"""
import json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"

NUM = set("""zero one two three four five six seven eight nine ten eleven
    twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen
    twenty thirty forty fifty sixty seventy eighty ninety hundred thousand
    million billion trillion percent quarter-billion two-thirds third half
    """.split())
FRAME = ("in ", "by ", "then ", "today", "that was", "and in", "somewhere",
         "back in", "now ")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()


def main() -> int:
    vo = (EP / "SCRIPT-G-VO.txt").read_text(encoding="utf-8")
    vo = re.sub(r"`\[[a-z-]+\]`", " ", vo)
    plan = json.loads((EP / "SCRIPT-G-EDIT-PAUSES.json")
                      .read_text(encoding="utf-8"))
    covered = [norm(p.get("after") or p.get("before") or "")
               for p in plan["pauses"]]

    def is_covered(*texts: str) -> bool:
        blob = " ".join(norm(t) for t in texts)
        return any(c and c in blob for c in covered)

    cands = []
    paras = [p.strip() for p in vo.split("\n") if p.strip()]
    for para in paras:
        sents = [s.strip() for s in
                 re.split(r"(?<=[.!?])\s+", para) if s.strip()]
        for s1, s2 in zip(sents, sents[1:]):
            tail = norm(s1).split()[-4:]
            lands_num = any(t in NUM or any(c.isdigit() for c in t)
                            for t in tail)
            opens_frame = norm(s2).startswith(
                tuple(f.strip() + " " for f in FRAME)) or \
                any(norm(s2).startswith(f) for f in FRAME)
            if is_covered(s1[-60:], s2[:60]):
                continue
            if lands_num and opens_frame:
                cands.append((1.0, "savor settle -> era shift", s1, s2))
            elif lands_num and len(norm(s1).split()) <= 8:
                cands.append((0.45, "stat settle (snap)", s1, s2))
            elif opens_frame and len(norm(s1).split()) <= 6:
                cands.append((0.45, "era-shift breath", s1, s2))

    for s, kind, s1, s2 in cands:
        print(f"{s:4.2f}s {kind:28s} after: ...{s1[-45:]}")
        print(f"{'':34s}before: {s2[:45]}...")
    print(f"\n{len(cands)} candidate sites not in the plan "
          f"(plan holds {len(plan['pauses'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
