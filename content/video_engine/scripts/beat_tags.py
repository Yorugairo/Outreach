"""Structural beat tags - the one place the tag set lives.

The script kit marks delivery with `[pre-key]` / `[post-key]` (Humes' pauses).
The opening-structure gate (gate_opening_structure.py) needs the WRITER to
declare the structural beats the doc-38 / P1 / P2 shape requires - the fused
classical layer (Truby / McKee / Snyder / Glass / ring composition, doc 32
s4-s6) and the platform layer - because most of them have no reliable
textual signature: a head-fake looks like a sentence. A declared beat is a
checkable beat - presence AND window. An undeclared required beat FAILS;
that is the contract that turns the "by hand" roster rows into gates.

Tags are written inline, immediately BEFORE the sentence that IS the beat.

  P1 - THE OPEN (doc 38 s2 / P1.md)          classical node
    [archetype]  a person-in-a-setting enters (0:08-0:30)   Truby Weakness/Need as people; McKee archetype
    [stakes]     stakes named by ~0:25                      hook anatomy (target + transformation + risk)
    [payoff]     mini-payoff - real value BEFORE the ask    One Minute Wall
    [promise]    the dated/calculable promise               F1 + A1 + macro-loop-1 SETUP
    [tricolon]   the thesis-grade triad (P1: exactly one)   rhetoric (doc 32 s3)
    [desire]     the goal the video pursues, named          Truby Desire
    [opponent]   the opponent named - a MECHANISM           Truby Opponent / McKee antagonism
    [map]        map-not-territory signpost (tease WHAT)    auditory handrail (doc 32 s1)
    [ring]       the ring token planted / touched / closed  ring composition (doc 32 s5)
    [reflect]    a Glass reflection dab                     Glass anecdote<->reflection
    [rehook]     a positional rehook (A2 ~1:00, A3 ~10%)    platform layer
  P2 - THE ENGINE (P2.md)
    [catalyst]   the inciting fact/event, as a story beat   Snyder Catalyst / McKee inciting incident
    [loop]       a micro story loop CLOSED (STR close)      L2 loop (MAP s0)
    [new]        a new-information beat (every 15-30s)      platform layer
    [head-fake]  the obvious answer offered STRAIGHT        Truby Plan v1 planted
    [debate]     the obvious answer tried and found wanting Snyder Debate / Truby Plan v1 FAILS (as a gap)
    [foreshadow] F2 (~10%) / F3 (~27%) sightings of F1      foreshadow schedule
    [loop-close] macro loop 1 closing on a partial answer   macro loop (LIFO ledger)
    [dip]        the breathing dip after the macro close    platform layer
    [signpost]   the transition signpost out of P2          auditory handrail
    [anaphora]   the anaphora phrase (debut / recurrence)   rhetoric (doc 32 s3)
  Cross-cutting (STRENGTH-LOOP U6 / ruling E20)
    [concede]    a deliberate, budgeted concession run
    [turn]       the turn out of a concession into our own claim

Every consumer that strips marks before speech must strip these too;
they are never spoken. Import from here rather than re-listing.
"""
from __future__ import annotations

import re

BEAT_TAGS = frozenset({
    "archetype", "stakes", "payoff", "promise", "tricolon", "desire", "opponent",
    "map", "ring", "reflect", "rehook",
    "catalyst", "loop", "new", "head-fake", "debate", "foreshadow", "loop-close",
    "dip", "signpost", "anaphora",
    "concede", "turn",
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
