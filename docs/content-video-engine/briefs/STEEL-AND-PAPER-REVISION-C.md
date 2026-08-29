# Steel and Paper — Revision C

Script B adapted to the rules established 2026-08-25 → 08-28. Structure,
beats and the five hardest lines are **unchanged** — B won a seed-locked
A/B by ear and its peaks are earned. Everything here is fact correction,
one cut, and two structural additions.

Runtime impact: **+17s** (audit beat +25s, Microsoft cut −8s) → ~463s.
Plate target rises 38 → 39. We have 39. No plate work needed.

---

## 1. MANDATORY — facts

### 1a. The railway crash figure

**Cut:** "Then the stocks crashed seventy percent."
**Use:** "Then the stocks crashed by nearly two-thirds."

Campbell & Turner's index: 2,062 peak (6 Oct 1845) → 741 trough (Apr
1850) = **64.1%**. "Seventy" is not defensible. "Nearly two-thirds" is
both accurate and more spoken than "sixty-four percent."

### 1b. Karp — use the verbatim

**Cut:** "Alex Karp of Palantir, on national television: companies buying
AI tokens can't yet see a clear return."
**Use:** "Alex Karp of Palantir, live on CNBC: enterprises are — his
words — paying for tokens that create no value. Something, he says, has
gone completely wrong."

The paraphrase is weaker than what he actually said, and the record
document (`ev-doc-karp`) carries the quote on screen. Narration and dock
must agree verbatim (doc 39 §10).

### 1c. Microsoft — CUT ENTIRELY

**Cut:** "Microsoft now rations AI tools inside its own walls — the bills
got hard to justify."

Not adequately sourced. Only a forum thread and LinkedIn posts surfaced;
Microsoft's published behaviour is usage-based Copilot billing with admin
spending caps, which is a product feature, not evidence of internal
rationing. It goes to SOURCES-TO-VERIFY, and the beat survives its removal
— Karp and Uber carry it. Then adjust the next line: **"But look at what
those three stories actually are"** → **"But look at what those two
stories actually are."**

### 1d. Uber — keep the two people straight

**Cut:** "Uber burned its whole annual AI budget by April. Its own COO
admits the spending hasn't shown up in the product."
**Use:** "Uber's CTO says they burned the entire annual AI budget by
April. Four months. And the COO's line on whether it's showing up in the
product: if you can't draw a direct line to what you're shipping, that
trade gets harder to justify."

The CTO disclosed the budget (The Information); the COO made the separate
productivity remark (The Verge). "Its own COO" implied one person.

---

## 2. ADD — the audit beat (doc 40)

Goes in **P2**, immediately after the GDP-share claim, in the steelman.
This is the head-fake position: a number arrives, the viewer believes it,
and the check happens in the open.

**After:** "...And by Bravos' math, AI spending just crossed eight."
**Insert:**

> So I went and pulled a version of that myself — equipment and software
> investment as a share of GDP, straight off the BEA. `[pre-key]` The
> dot-com peak was eleven point five four, back in 2000. Today we're at
> eleven point five one. `[post-key]` Three hundredths of a point short.
> So we're not past that peak. We're level with it — which is still the
> story, just not the bigger one I went looking for.

Why it belongs here, and why it is the strongest single addition:

- It **audits our own eagerness**, not Bravos. Credit-before-dissent gets
  stronger, not weaker, because the first number we check is the one we
  wanted to be true.
- It sits in explanatory register, per VOICE-PACK §4b — plain speech, no
  personification, and still lands on terminal stress ("went looking
  for").
- It is a real check, not performed scepticism: the figure genuinely
  changed what we could claim.
- Evidence: `ev-equip-ipp-gdp-v1` docks here.

**Budget note:** this is the video's ONE audit beat. Doc 40 caps at one or
two; the tell (§3) is the second, and that is the ceiling.

---

## 3. UPGRADE — the tell becomes an instrument

The tell is the channel's standing audit and now has real apparatus
behind it (doc 39 §12).

**Cut:** "The threshold: contract memory prices falling for two straight
quarters while the buildout continues. The position: prices have climbed
all year on sold-out supply — sources pinned in the description."

**Use:**

> The variable is memory — the RAM inside every one of these data
> centers. And I don't take that one on trust. I built a monitor for it:
> it reads what memory costs leaving Korea, by the kilo, straight off
> customs export data. `[pre-key]` The threshold is that number falling
> below its own trailing average, two quarters running, while the
> buildout keeps going. `[post-key]` Right now it's going the other way —
> DRAM up seventeen percent, and the stacked memory the AI racks actually
> need up fourteen. That's the July release; customs runs about a month
> behind. The flip: if memory breaks while the buildout holds, the
> scarcity story is wrong — and so am I. That week, I de-risk the
> builders on camera.

- The lag is **spoken, not buried** — finance runs the strictest evidence
  precision (ruling A5), and a reading without its as-of is an assertion.
- **Figures re-verified 2026-08-29** against the rebuilt ledger. The
  earlier draft cited May 2026 at +51.1% / +26.5%; the corrected store
  reads **July 2026, DRAM 86,970 $/kg (+17.4%), HBM-class 95,408 $/kg
  (+14.1%)**, value-weighted (total USD ÷ total kg across partners), and
  the publication lag is about a month rather than three. Both figures on
  screen and in narration must come from the same pull.
- Evidence: `ev-instrument-memory` docks here; `ev-dram-contract-v1`
  (TrendForce) is the confirming series alongside.
- "I built a monitor for it" is the moat stated plainly — process as the
  product (ruling A4), in one clause, without a methodology lecture.

---

## 4. UNCHANGED — do not touch

The microhook, the promise, the reversal, the thesis, the ring echo and
the final triad all won the A/B by ear. Their density is earned because
they sit at structural peaks (VOICE-PACK §4b). Specifically:

- "In 1845, the smartest trade in England was this iron spike."
- "A bubble is not a technology failing. A bubble is ownership outrunning
  understanding."
- "The steel kept working. The paper stopped pretending."
- "That's what a top actually looks like: not euphoria — accidental
  concentration, sold as safety."

The referent test passes on all of these: "paper," "the tourists," "paper
holders," "the market" each stand for people, not for artifacts we built.

---

## 5. Evidence attachment (12 documents + 1 instrument)

| Beat | Document |
|---|---|
| P2 steelman — railway overshoot | `ev-railway-index-v1` (−64.1%), `ev-railway-gdp-tile` (7% of GDP) |
| P2 steelman — authorised vs built | `ev-railway-mileage-v1` |
| P2 audit beat | `ev-equip-ipp-gdp-v1` |
| P3 ROI — Karp | `ev-doc-karp` (record document) |
| P3 ROI — Uber | `ev-doc-macdonald`, `ev-uber-adoption-v1` |
| P4 concentration | `ev-mega-vs-spy-v3`, `ev-listing-barge` plate |
| P4 the paper you don't see | `ev-doc-leases` ($822B), `ev-capex-consensus-v1` |
| P5 divergence re-read | `ev-smh-drawdown-v3`, `ev-tnx-two-eras-v3` |
| P5 the tell | `ev-instrument-memory`, `ev-dram-contract-v1`, `ev-hbm-export-series` |

Bare-plate stretches: recompute after the master take. The 83s deficit
should close — 39 plates against a ~463s runtime is 11.9s per plate, just
inside the 12s target.

---

## 6. Order of operations

1. Apply §1–§3 to the script text.
2. Re-run `lint_script_pattern.py` (CTA budget, triads, pause ration).
3. Sentence-strength pass on the **new** lines only — the rest already
   passed.
4. Master take, one ElevenLabs request, seed 4242 (doc 37 §8).
5. Rebuild the timeline from the new word timings.
