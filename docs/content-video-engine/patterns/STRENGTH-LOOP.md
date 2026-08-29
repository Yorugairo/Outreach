# THE STRENGTH LOOP — gates at every scale, and across them

`SENTENCE-STRENGTH-CHECK.md` gates L0. The phase guides gate L4. The duty
roster gates L5. **L1, L2 and L3 had no gates at all, and nothing checked
*between* scales** — which is the defect class that survived six passes on
Script E: a fix at one scale silently breaking an adjacent one.

Established 2026-08-29, from the operator's diagnosis: *"what we need is
sentence strength + phrase strength + section strength loop checks."*

---

## 0. Why the loop exists

Every edit at scale N can break N−1 and N+1. Observed on Script E in one
session:

| Fix at | Broke at | How |
|---|---|---|
| L0 sentence split (terminal stress) | L1 connective | "Then" left following a currency aside, not an event |
| L0 splits (S1/S5) | L5 distribution | raw sentence mean fell below its band |
| L0 split (S113) | L1 antecedent | "And calls it the market" lost its subject |
| L3 insertion (enumeratio) | L4 geometry | pivot moved 50.1% → 47.9% |
| L0 hook rewrite | L5 roster | F1/A1 positions shifted |

None of these is findable by the gate that caused them. **Only a loop that
re-verifies every scale after every change finds this class.**

## 1. The scales and their gates

| Scale | Unit | Gate | Status |
|---|---|---|---|
| **L0** | Line | `SENTENCE-STRENGTH-CHECK.md` S1–S10 | exists |
| **L1** | Phrase | §2 below | **new** |
| **L2** | Beat / STR loop | §3 below | **new** |
| **L3** | Unit / section | §4 below | **new** |
| **L4** | Phase | the six QC lines, phase guides | exists |
| **L5** | Video | duty roster, geometry, ring | exists |
| **L6** | Catalogue | §6 below | **new** |
| **X** | Cross-scale | §5 below — **the orphan class** | **new** |

## 2. L1 — PHRASE strength

Sub-sentence craft. A sentence can pass all ten S-gates and still be built
of dead clauses.

| # | Gate | Fails when |
|---|---|---|
| **P1** | **Connective integrity** | beats join with AND-THEN instead of BUT or THEREFORE. Every connective must carry a turn or a consequence. |
| **P2** | **Figure referent** | a figure of speech attaches to nothing real in the sentence's world (VOICE-PACK §4b). "The average never noticed" is good about investors, bad about a number we computed. |
| **P3** | **Clause earns its place** | a subordinate clause carries no information the main clause lacks — throat-clearing, restated setup, hedging. |
| **P4** | **Cadence wave** | long sentences and short ones merely alternate instead of building and resolving. The gears form a wave, not a metronome. |
| **P5** | **Phonetic anchor placement** | alliteration or assonance appears anywhere other than the promise, the payoff, or the tell. Decoration elsewhere spends the device. |
| **P6** | **Deixis resolves** | "this", "that", "it", "these" points at nothing on screen or in the immediately preceding sentence. |

**P6 is the one that catches orphans at the phrase level.** P1 is the one
that catches them at the beat level — see X1.

## 3. L2 — BEAT strength

The STR micro loop: setup → tension → resolution, closing every 30–60s and
opening the next immediately.

| # | Gate | Fails when |
|---|---|---|
| **B1** | **The loop closes** | a setup or tension opens and never resolves inside 60s. |
| **B2** | **New-info cadence** | more than 30s passes with no new information (relaxing to 45s in P5 reflection stretches, never to zero). |
| **B3** | **Charge shifts** | a beat leaves the value charge where it found it — nothing was gained, lost, or reversed. |
| **B4** | **Connected, not listed** | consecutive beats read as a list. Every junction is BUT or THEREFORE. |

## 4. L3 — SECTION strength (the pattern unit)

The P3/P5 unit, 2:00–2:30, five steps.

| # | Gate | Fails when |
|---|---|---|
| **U1** | **All five steps** | u1 anecdote → u2 BUT/gap → u3 THEREFORE/deeper → u4 reflection → u5 rehook out. A unit missing u4 is a shallow list. |
| **U2** | **Register shifts at u4** | the reflection beat lands in the same emotional register as the anecdote. |
| **U3** | **One breathing dip** | the unit runs without a dip, or piles on more than one. |
| **U4** | **Anaphora evolves** | the anaphora phrase recurs with an identical tail instead of an evolved one. |
| **U5** | **Best evidence late** | the strongest material sits in an early unit rather than the final unit before the pivot. |

## 5. X — CROSS-SCALE checks (run after EVERY edit)

**This is the section that did not exist, and it is the whole point.**

| # | Check | What it catches |
|---|---|---|
| **X1** | **Antecedent integrity** | every sentence opening on a connective or bare pronoun resolves to the sentence *directly before it*. Splits sever these. |
| **X2** | **Position drift** | after any edit, re-verify the timed anchors: F1/F2/F3, A1–A4, the pivot pin, the CTA window, the paradox boundary. |
| **X3** | **Count drift** | re-verify the duty roster: rehooks, foreshadows, tricolon terminality, CTA budget, break tags per part. |
| **X4** | **Distribution drift** | sentence mean (carrying), spread, over-20 share, break ration. Splitting moves all four. |
| **X5** | **Split integrity** | for a chained take, the split still lands on a `[post-key]` and both parts stay under cap and under 12 tags. |

## 6. L6 — CATALOGUE

Across videos, not within one.

| # | Gate | Fails when |
|---|---|---|
| **C1** | **Thesis lens** | the script argues none of T1–T12, so it does not compound the worldview. |
| **C2** | **Instrument continuity** | the tell uses an instrument the channel has not stood on before, with no explanation. |
| **C3** | **No self-contradiction** | a claim contradicts a prior episode's registered claim without saying so. |

---

## 7. The loop protocol

Operator rulings, 2026-08-29.

```
loop:
  1. Run every scale L0..L6. Collect findings.
  2. Run X. Collect findings.
  3. If ZERO findings AND zero edits were made this round -> CONVERGED.
  4. Apply fixes, respecting the rewrite budget.
  5. Go to 1.
```

**Convergence is a fixpoint, not an empty gate list.** A round that fires no
gates but made an edit runs again — because the edit is exactly what might
have broken something nothing checked yet. This is the rule that would have
caught the "Then" orphan five passes earlier.

**No cost ceiling.** The full loop runs every time. A bad take costs more
than a long review, and the episode is public.

### Precedence when scales conflict

**Comprehension > structure > line-craft.**

A listener who loses the thread loses the argument; a soft terminal costs
only emphasis. This is the standing resolution of the S23 case — a split
made for terminal stress (line-craft) that severed a temporal link
(comprehension). Comprehension won and the line-craft exception was logged.

### Rewrite budget — the over-smoothing guard

**Any sentence rewritten more than twice stops and goes to the operator
with its full history.**

A line that keeps failing is usually a line the gates are wrong about. The
"target-date fund" clause is the worked example: it fails S3 permanently,
it is operator-approved, and the correct outcome is a logged exception, not
a third rewrite. Fixpoint plus no ceiling would otherwise sand it away.

### Oscillation

**If a sentence reverts to a prior state, stop.** Name both gates, state the
trade-off, and escalate as a DECISION. Apply the precedence rule only where
it settles the case cleanly; where it does not, the operator decides.
Oscillation usually means two gates are in genuine conflict, which is a
doctrine finding, not a script problem.

### Generation order

**All six phases, then loop the whole thing** (operator's call over
phase-by-phase gating). The accepted trade-off: a structural error in P2
propagates through everything downstream before anything checks it. The
loop must therefore treat **L3 and L4 findings as first-class**, not as
polish after the sentences are clean — a unit missing its reflection beat
is a bigger defect than any number of terminal-stress misses.

## 8. What stays human

No gate in L1, L2 or L3 is safely automatable end to end. A regex proxy for
"concrete" returned confident wrong verdicts; a proxy for "charge shifts"
would be worse. Mechanical screens propose candidates; **the reader
decides.** Automate only what is unambiguous — counts, positions,
durations, antecedent adjacency — and surface the rest.
