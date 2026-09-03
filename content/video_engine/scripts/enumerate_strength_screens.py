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

    python enumerate_strength_screens.py <VO.txt> [--timeline build-f/timeline.json]
                                                  [--ring spike] [--counterparty Bravos]

Emits <script>-SCREENS.md beside the input:
  X1  every connective/pronoun-opening sentence WITH its predecessor
  P6  every this/that/it/these opener (deixis candidates)
  P1J every And/Then-opening junction (AND-THEN risk)
  P5A repeated-initial bigrams (phonetic-anchor candidates + placement)
  P4C per-paragraph sentence-length runs (cadence wave vs metronome)
  DECLARED  every beat tag with its clock, the opening gate's window verdict
            for the tag's owning gate, the sentence under the tag, and an
            EMPTY verdict column - CHECK-RESPONSIBILITIES R2 / s3a: a declared
            beat is a claim; the agent verdicts each tag true / laundered.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_script_doctrine as A          # noqa: E402  (load_timings: a take on disk beats the estimate)
import beat_tags                            # noqa: E402  (the ONLY tag parser)
import gate_opening_structure as G          # noqa: E402  (window verdicts are the gate's, never re-derived)

# Tag -> owning gate id(s), read from gate_opening_structure.run() 2026-09-02:
#   G37 archetype . G07 stakes . G08 payoff . G09 promise . G12 (P1) / G32 (P2)
#   tricolon . G38 desire . G14 opponent . G39 map . G15 (P1) / G27 (P2) ring .
#   G16 (P1) / G31 (P2) reflect . G13 (A2, P1) / G25 (A3, P2) rehook .
#   G40 catalyst . G19 + G21 loop . G20 + G22 new . G24 head-fake . G41 debate .
#   G26 foreshadow . G28 loop-close . G29 dip . G42 signpost . G32 anaphora.
# [concede] / [turn] have no owning gate: G34 / G35 read the sentences, not
# the tags, so those rows report n/a and the agent verdicts them by hand.
TAG_GATES: dict[str, tuple[str, ...]] = {
    "archetype": ("G37",), "stakes": ("G07",), "payoff": ("G08",), "promise": ("G09",),
    "tricolon": ("G12", "G32"), "desire": ("G38",), "opponent": ("G14",), "map": ("G39",),
    "ring": ("G15", "G27"), "reflect": ("G16", "G31"), "rehook": ("G13", "G25"),
    "catalyst": ("G40",), "loop": ("G19", "G21"), "new": ("G20", "G22"),
    "head-fake": ("G24",), "debate": ("G41",), "foreshadow": ("G26",),
    "loop-close": ("G28",), "dip": ("G29",), "signpost": ("G42",), "anaphora": ("G32",),
}
# tuples that are (P1 gate, P2 gate): one is chosen by the beat's clock
# against the gate's own geometry; every other tuple applies in full.
PHASE_SPLIT = frozenset({"tricolon", "ring", "reflect", "rehook"})
QUOTE_MAX = 110
NO_BEATS_LINE = ("- no declared beats — every declared-kind gate FAILs by absence (R2); "
                 "tag the beats or record the reason")
# the gate's sentence chunking (gate_opening_structure._sentences_timed)
SENT_CHUNK = re.compile(r"[^.!?]*[.!?]+(?:\s+|$)", re.S)
MD_LINE = re.compile(r"^\s*(?:#|\||>|---|```).*$", re.M)


def sentences(text: str) -> list[str]:
    t = re.sub(r"`\[[a-z-]+\]`", "", text)
    t = " ".join(t.split())
    return [s.strip() for s in
            re.split(r"(?<=[.!?\"”])\s+(?=[A-Z\"“])", t) if s.strip()]


def _lexical_sections(sents: list[str]) -> tuple[list[str], dict]:
    out: list[str] = []
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
    return out, {"X1": len(x1), "deixis": len(dx), "junctions": len(j), "anchors": len(pa)}


def _cadence_section(raw: str) -> list[str]:
    out = ["", "## P4C — cadence runs (words per sentence, per paragraph)", ""]
    body = re.sub(r"`\[[a-z-]+\]`", "", raw)
    for n, para in enumerate([p for p in body.split("\n\n") if p.strip()], 1):
        runs = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences(para)]
        flat = (" ← FLAT?" if len(runs) >= 4 and
                max(runs) - min(runs) <= 4 else "")
        out += [f"- ¶{n}: {runs}{flat}"]
    return out


# ---- DECLARED beats (CHECK-RESPONSIBILITIES R2 / s3a) ----------------------
def _secs(clock: str) -> float:
    m, _, s = clock.partition(":")
    return int(m) * 60 + int(s)


def _host_sentence(text: str, off: int) -> str:
    """The sentence carrying the tag at `off`, marks stripped, <= QUOTE_MAX."""
    for m in SENT_CHUNK.finditer(text):
        if m.start() <= off < m.end():
            s = MD_LINE.sub("", beat_tags.strip_marks(m.group(0)))
            s = " ".join(s.split())
            return s if len(s) <= QUOTE_MAX else s[:QUOTE_MAX - 1] + "…"
    return ""


def _mmss(s: float) -> str:
    return f"{int(s // 60)}:{int(s % 60):02d}"


def _window_cell(tag: str, t_s: float, levels: dict[str, str], geo: dict, tol: float) -> str:
    ids = TAG_GATES.get(tag)
    if not ids:
        return "n/a — no owning gate"
    # the gate's own reach: in_p2 = p2_end * tol; G28 / G42 alone allow p2_end + REHOOK_TOL
    slack = G.REHOOK_TOL if tag in ("loop-close", "signpost") else 0.0
    if t_s > max(geo["p2_end"] * tol, geo["p2_end"] + slack):
        return f"n/a — outside opening window (P2 ends {_mmss(geo['p2_end'])})"
    if tag in PHASE_SPLIT:
        ids = (ids[0],) if t_s <= geo["p1_end"] * tol else (ids[1],)
    return ", ".join(f"{levels[i]} — {i}" if i in levels else f"n/a — {i} not emitted"
                     for i in ids)


def declared_section(text: str, timeline: list[dict] | None,
                     ring: str | None, counterparty: str | None) -> tuple[list[str], int]:
    found = beat_tags.find_beats(text)
    out = [f"## DECLARED — beat tags ({len(found)})", "",
           "One row per tag, script order. `window` is the opening gate's verdict",
           "for the tag's owning gate (R1: final, never re-derived). `verdict` is",
           "the agent's, per tag: **true / laundered** (CHECK-RESPONSIBILITIES R2,",
           "§3a) - a laundered tag is a FAIL at the phase, not a note.", ""]
    if not found:
        return out + [NO_BEATS_LINE], 0
    gates, stats = G.run(text, timeline, counterparty, ring)
    levels = {g.id: g.level for g in gates}
    runtime = _secs(stats["runtime"])
    geo, tol = G.geometry(runtime), (1.0 if timeline else G.EST_TOL)
    seen: Counter = Counter()
    for tag, off in found:
        clocks = stats["beats_declared"].get(tag, [])
        clock = clocks[seen[tag]] if seen[tag] < len(clocks) else "?:??"
        seen[tag] += 1
        t_s = _secs(clock) if clock[0].isdigit() else runtime
        win = _window_cell(tag, t_s, levels, geo, tol)
        out.append(f'- [{tag}]@{clock}  window: {win}  "{_host_sentence(text, off)}"  → verdict: ____')
    return out, len(found)


# ---- entry -----------------------------------------------------------------
def build_screens(src: Path, timeline: list[dict] | None = None, ring: str | None = None,
                  counterparty: str | None = None) -> tuple[Path, dict]:
    raw = src.read_text(encoding="utf-8")
    sents = sentences(raw)
    out = [f"# STRENGTH SCREENS — {src.name}",
           "",
           f"{len(sents)} sentences. Every candidate below requires a",
           "per-item verdict in the strength log (ok / FIXED / licensed /",
           "carryover). A convergence claim without this file walked is",
           "invalid — the enumeration IS the review.",
           ""]
    lex, counts = _lexical_sections(sents)
    out += lex + _cadence_section(raw)
    if timeline is None:
        timeline = A.load_timings(src)
    decl, n_decl = declared_section(raw, timeline, ring, counterparty)
    out += [""] + decl
    counts = {**counts, "declared": n_decl}
    dest = src.with_name(src.stem.replace("-VO", "") + "-SCREENS.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    return dest, counts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("script", type=Path)
    ap.add_argument("--timeline", type=Path, help="build-f/timeline.json (measured word times)")
    ap.add_argument("--ring", help="the ring token object, e.g. spike (passed to the opening gate)")
    ap.add_argument("--counterparty", help="named counterparty, e.g. Bravos (passed to the opening gate)")
    args = ap.parse_args()
    tl = G.load_timeline(args.timeline) if args.timeline else None
    dest, c = build_screens(args.script, tl, args.ring, args.counterparty)
    print(f"{dest.name}: X1={c['X1']} deixis={c['deixis']} junctions={c['junctions']} "
          f"anchors={c['anchors']} declared={c['declared']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
