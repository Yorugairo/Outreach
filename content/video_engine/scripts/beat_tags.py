"""Structural beat tags - the one place the tag set lives.

The script kit already marks delivery with `[pre-key]` / `[post-key]`. The
opening-structure gate (gate_opening_structure.py) needs the WRITER to
declare the structural beats the doc-38 / P1 / P2 shape requires, because
most of them have no reliable textual signature: a head-fake looks like a
sentence. A declared beat is a checkable beat - presence AND window. An
undeclared required beat FAILS; that is the contract that turns the "by
hand" roster rows into gates.

Tags are written inline, immediately BEFORE the sentence that IS the beat:

  P1 (doc 38 s2 / P1.md)
    [stakes]     stakes named (target + transformation + what's at risk), by ~0:25
    [payoff]     the mini-payoff - real value delivered BEFORE the ask (0:30-0:60)
    [promise]    the dated/calculable promise = A1 + F1 + macro-loop-1 setup
    [tricolon]   the thesis-grade triad (P1: exactly one; P2: at most one)
    [opponent]   the opponent named as a MECHANISM (0:60-P1 end)
    [ring]       the ring token: planted (P1) / touched once (P2) / closed (P6)
    [reflect]    a Glass reflection dab (P1: exactly one; P2: never consecutive)
    [rehook]     a positional rehook (A2 ~1:00, A3 ~10%, unit exits)
  P2 (P2.md)
    [loop]       a micro story loop CLOSED (STR close); the first one is the catalyst
    [new]        a new-information beat (something genuinely new, every 15-30s)
    [head-fake]  head-fake #1 planted STRAIGHT; demolition reserved for the pivot
    [foreshadow] F2 (~10%) / F3 (~27%) sightings of the F1 promise
    [loop-close] macro loop 1 closing on a partial answer
    [dip]        the breathing dip immediately after the macro close
    [anaphora]   the anaphora phrase (debut or recurrence)
  Cross-cutting (STRENGTH-LOOP U6 / ruling E20)
    [concede]    a deliberate, budgeted concession run
    [turn]       the turn out of a concession into our own claim

Every consumer that strips marks before speech must strip these too;
they are never spoken. Import from here rather than re-listing.
"""
from __future__ import annotations

import re

BEAT_TAGS = frozenset({
    "stakes", "payoff", "promise", "tricolon", "opponent", "ring", "reflect",
    "rehook", "loop", "new", "head-fake", "foreshadow", "loop-close", "dip",
    "anaphora", "concede", "turn",
})
DELIVERY_MARKS = frozenset({"pre-key", "post-key", "verify"})
ALL_MARKS = BEAT_TAGS | DELIVERY_MARKS

_alt = lambda names: "|".join(sorted(names, key=len, reverse=True))
TAG_RE = re.compile(r"`?\[(" + _alt(ALL_MARKS) + r")\]`?")
BEAT_TAG_RE = re.compile(r"`?\[(" + _alt(BEAT_TAGS) + r")\]`?")
MARK_RE = re.compile(r"`?\[(" + _alt(ALL_MARKS) + r")\]`?")


def strip_marks(text: str) -> str:
    """Remove every known mark/tag; what remains is what gets spoken."""
    return TAG_RE.sub("", text)


def strip_beat_tags(text: str) -> str:
    """Remove ONLY the structural beat tags, keeping delivery marks.

    The record scripts call this before compiling pause marks: beat tags are
    authoring metadata for the structure gate and must never reach synthesis,
    while [pre-key]/[post-key] still compile to breaks/edit pauses.
    """
    return re.sub(r"[ \t]{2,}", " ", BEAT_TAG_RE.sub("", text))


def find_marks(text: str) -> list[tuple[str, int]]:
    """(mark, char offset in the ORIGINAL text) for every mark/tag, in order."""
    return [(m.group(1), m.start()) for m in MARK_RE.finditer(text)]


def find_beats(text: str) -> list[tuple[str, int]]:
    return [(t, o) for t, o in find_marks(text) if t in BEAT_TAGS]


def unknown_marks(text: str) -> set[str]:
    """Bracketed marks that are not in the allow-list - they would be spoken."""
    return set(re.findall(r"\[([a-z][a-z-]*)\]", text)) - ALL_MARKS
