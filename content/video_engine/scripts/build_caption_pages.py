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

# CHAR_BUDGET raised 18 -> 34 (operator/watch feedback 2026-09-01: pages
# were reading 2-3 words; wants 4-6 at a time). MAX_WORDS is the hard cap
# so a run of short words can't overfill a page past readability.
CHAR_BUDGET = 34   # a build may override these (the Tokyo short: 28 / 6 - two lines of 25-28 chars on the 800 px strip, operator 2026-09-05)
MAX_WORDS = 6
GAP_BREAK = 0.60
SENTENCE_END = (".", "!", "?")   # E41 #3 (2026-09-05): "the caption pages are built from the punctuation" - a page never runs past a sentence's end
CLAUSE_MARK = (",", ":", ";")    # ... and breaks at the clause once it holds a phrase (CLAUSE_MIN_WORDS), so a page is one readable phrase
CLAUSE_MIN_WORDS = 3
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


# R26-278 (P72 T14): the take's aligner writes every straight quote onto the word BEFORE it (H 237 s: `And"` `don't`
# ... `top"`), so a page read `And" don't try to call the` - a typo on screen. A quote belongs to the word it opens
# or ends, and which it does is the stream's own parity: a straight quote trailing a word while none is open OPENS -
# it rides the word after it; one trailing a word while a quote is open CLOSES and stays. A curly quote says which it
# is: a trailing opening one rides forward, everything else stays. Only the character moves, never a word's clock.
STRAIGHT_QUOTE, OPEN_QUOTE, CLOSE_QUOTE = '"', "“", "”"
QUOTE_MARKS = STRAIGHT_QUOTE + OPEN_QUOTE + CLOSE_QUOTE


def _trail(word: str) -> int:
    """Where the word's trailing marks begin (every character after its last letter or digit)."""
    i = len(word)
    while i > 0 and not word[i - 1].isalnum():
        i -= 1
    return i


def place_quotes(words: list[str]) -> list[str]:
    """R26-278: each word's text with every OPENING quote moved onto the word it opens. Pure; same length."""
    out, carry, is_open = [], "", False
    for n, word in enumerate(words):
        word = carry + word
        carry = ""
        cut = _trail(word)
        head, tail = word[:cut], word[cut:]
        for ch in head:   # the marks in front of (and inside) the word: an opening quote here is already home
            if ch in (STRAIGHT_QUOTE, OPEN_QUOTE):
                is_open = True if ch == OPEN_QUOTE else not is_open
            elif ch == CLOSE_QUOTE:
                is_open = False
        kept = ""
        for ch in tail:
            opens = ch == OPEN_QUOTE or (ch == STRAIGHT_QUOTE and not is_open)
            if ch in (STRAIGHT_QUOTE, OPEN_QUOTE) and opens and n + 1 < len(words):
                carry += ch                  # it opens the NEXT word: ride forward (that word's head opens it)
                continue
            if ch in QUOTE_MARKS:
                is_open = opens
            kept += ch
        out.append(head + kept)
    return out


def main() -> int:
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    pages, cur = [], []
    prev_end = None
    sent_start = True
    texts = place_quotes([w["w"] for w in tl["words"]])
    for w, text in zip(tl["words"], texts):
        w = {**w, "w": text}
        gap = (w["start"] - prev_end) if prev_end is not None else 0.0
        cur_len = sum(len(t["w"]) + 1 for t in cur)
        last = cur[-1]["w"].rstrip('"”') if cur else ""
        # one-shot #3 (the operator, 2026-09-16: "the captions are wrong"): a retimed take caps its sentence gaps under
        # GAP_BREAK, so the pages ran across sentence ends ("the news. They trade the" | "calendar. Around the") - the
        # punctuation IS the break (E41 #3), the gap only its fallback
        at_sentence_end = last.endswith(SENTENCE_END)
        at_clause = last.endswith(CLAUSE_MARK) and len(cur) >= CLAUSE_MIN_WORDS
        if cur and (cur_len + len(w["w"]) > CHAR_BUDGET
                    or len(cur) >= MAX_WORDS or gap > GAP_BREAK
                    or at_sentence_end or at_clause):
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
