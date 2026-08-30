"""Regenerate caption-pages.json from the CURRENT timeline - stage 6b.

The kinetic caption layer reads short pages (~3 words) with per-word
times and a k flag (emphasis: numerals, proper nouns, the thesis pair).
The original pages were built for the old take; this rebuilds them from
build-f/timeline.json so captions ride the new clock.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUILD = REPO / ("content/video_engine/projects/systems-and-blowups/"
                "steel-and-paper/build-f")

CHAR_BUDGET = 18
GAP_BREAK = 0.45
NUM = {"one", "two", "three", "four", "five", "six", "seven", "eight",
       "nine", "ten", "eleven", "twelve", "twenty", "thirty", "forty",
       "fifty", "sixty", "seventy", "eighty", "ninety", "hundred",
       "thousand", "million", "billion", "trillion", "percent", "half",
       "quarter", "third", "fifth", "cents", "quarter-billion",
       "two-thirds"}
THESIS = {"steel", "paper"}


def is_k(word: str, sent_start: bool) -> bool:
    bare = re.sub(r"[^A-Za-z0-9'-]", "", word)
    low = bare.lower().rstrip(".,")
    if re.search(r"\d", bare):
        return True
    if low in NUM or low.rstrip("s") in NUM or low in THESIS:
        return True
    if bare[:1].isupper() and not sent_start and low not in ("i",):
        return True
    return False


def main() -> int:
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    pages, cur = [], []
    prev_end = None
    sent_start = True
    for w in tl["words"]:
        gap = (w["start"] - prev_end) if prev_end is not None else 0.0
        cur_len = sum(len(t["w"]) + 1 for t in cur)
        if cur and (cur_len + len(w["w"]) > CHAR_BUDGET or gap > GAP_BREAK):
            pages.append({"s": cur[0]["s"], "e": cur[-1]["e"], "t": cur})
            cur = []
        cur.append({"w": w["w"], "s": round(w["start"], 2),
                    "e": round(w["end"], 2),
                    "k": is_k(w["w"], sent_start)})
        sent_start = w["w"].rstrip('"”').endswith((".", "!", "?"))
        prev_end = w["end"]
    if cur:
        pages.append({"s": cur[0]["s"], "e": cur[-1]["e"], "t": cur})
    (BUILD / "caption-pages.json").write_text(json.dumps(pages),
                                              encoding="utf-8")
    kn = sum(t["k"] for p in pages for t in p["t"])
    print(f"{len(pages)} pages, {kn} k-words, "
          f"to {pages[-1]['e']:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
