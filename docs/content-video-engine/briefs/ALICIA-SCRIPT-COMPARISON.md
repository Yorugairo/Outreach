# Four-Way Script Comparison — "Why a Budtender Retires Before a Banker"

The decisive AOY-trial test, expanded: same title, same references, same
3-minute target. Panel B was written **before** panel C arrived — a
falsifiable prediction of their output from extracted doctrine. If B ≈ C,
the extraction is complete and the $3,800/mo question is answered.

| Panel | Script | Status |
| --- | --- | --- |
| A | Ours — recreation brief (humanizer + retention curve + operator voice) | `ALICIA-FORMAT-RECREATION-BRIEF.md` |
| B | **Predicted-theirs** — written from extracted doctrine, below | 2026-08-24, before C landed |
| C | Theirs — `write_script_v2` | https://ai.theartofyt.com/reports/ee363e00d37f459f.html |
| D | Ground truth — Alicia 0:00–3:00 | transcript on file, patterns in the brief |

## Panel B — predicted write_script_v2 output

Falsifiable tells predicted (score C against these when it lands):

1. Opens with a third-person vignette in the Alicia register ("There's a
   banker in…") — **not** first-person testimony.
2. **The persona gets diluted**: ex-JPMorgan/dispensary survives as a fact
   about the narrator, not as the narrative spine — advice-rules compliance
   pushes toward named-source attribution and away from "I know this because
   I was there."
3. ≥2 named-source statistics (Federal Reserve / BLS / a paycheck-to-paycheck
   survey).
4. Rhetorical-question re-hooks at roughly beats 3/5/7 ("But here's where it
   gets strange…").
5. At least one stock commentary line ("Let that sink in" family).
6. A compound-dollar math beat.
7. Ending: soft twist plus an implied continue/CTA — not a hard cut.
8. Register: competent, polished, 10–15% AI-tell density (the "screams
   success / whispers survival" chiasmus family their reviewer produces).

### The predicted script (~600 words)

There's a banker in Manhattan who makes ninety-five thousand dollars a year.
Nice apartment, designer suits, a watch that costs more than most people's
rent. And there's a budtender in Denver making about half that, ringing up
customers at a dispensary counter. Here's what nobody would guess: the
budtender is on track to retire comfortably. The banker is one missed
paycheck from crisis. How is that possible? Let's break it down.

According to the Federal Reserve's most recent household survey, nearly four
in ten Americans couldn't cover a four-hundred-dollar emergency expense with
cash. And here's the part that surprises people — that number doesn't
improve much as income rises. High earners are living paycheck to paycheck
too. The banker is one of them.

Walk into his apartment and you can see why. The seventy-five-inch
television. The espresso machine still in its box. A closet full of clothes
with tags still attached. Every purchase made sense in the moment. Together,
they've built something dangerous: a lifestyle that consumes every dollar he
earns. Let that sink in — ninety-five thousand a year, and nothing left at
the end of the month.

Now the budtender. Her apartment is smaller, and honestly? It's nicer to be
in. Space. A couch she actually uses. And a habit she picked up from
handling cash all day: she tracks every dollar. Eighteen months of expenses
saved. Twenty percent of every paycheck invested. On half the banker's
income.

But here's where it gets strange. The difference between them isn't
discipline, and it isn't intelligence. It's a single concept that financial
educators call the second price — and once you see it, you can't unsee it.

Everything you buy costs you twice. The first price is on the receipt. The
second price is what the thing costs to own: the space it occupies, the
maintenance it demands, the attention it steals. Consumer research suggests
the average American home contains hundreds of thousands of items — and
every one of them is quietly charging rent.

Do the math on just one. A piece of exercise equipment takes up roughly
twenty square feet. In a city where housing runs two dollars per square foot
each month, that's forty dollars a month — nearly five hundred dollars a
year — to store something that's probably being used as a coat rack. Now
multiply that thinking across everything you own. That's the second price,
and most people are paying it on hundreds of items at once.

The budtender figured this out early. Before anything comes into her home,
she asks one question: what will this cost me to keep? It sounds simple.
It's the reason she'll retire first.

So here's the rule that separates them — and it's the first of several the
budtender follows without ever having written them down. Rule one: pay
attention to the second price. Because the banker isn't failing at money.
He's succeeding at spending. And in the next rule, we'll look at what the
budtender does with the money her lifestyle never claims — because it's not
what most people think. Stick around.

### Panel B self-notes

Deliberately embedded their tells: third-person cold open (D-pattern), two
named-ish sources, "Let that sink in," rhetorical re-hooks, compound math,
"financial educators call" attribution hedge, "once you see it you can't
unsee it," soft-CTA ending ("Stick around"), persona reduced to zero — the
dispensary survives only as "handling cash all day."

## Scoring axes (for the four-way)

1. Hook mechanics — time-to-tension, concreteness
2. Retention architecture — open loops planted and priced, re-hook quality
3. Voice — could anyone else have written this? (the moat test)
4. Factual grounding — verifiable vs. hedged ("research suggests")
5. Shootability — how directly it maps to coverage slots in our pipeline
6. AI-tell density — humanizer violations per 100 words

## Panel C landed — prediction scorecard (2026-08-24)

| Tell | Predicted | Actual | Score |
| --- | --- | --- | --- |
| Third-person vignette open | yes | "Two people are counting money…" | **HIT** |
| Persona diluted to zero | yes | No "I" anywhere; dispensary is a set, not a biography | **HIT (the core bet)** |
| ≥2 named-source stats | yes | Four (Comptroller, Marijuana Herald, ERD, LendingClub) | **HIT** |
| Rhetorical-question re-hooks | yes | Declarative re-hooks instead ("Here is where the bonus ambushes him") | MISS |
| Stock AI commentary line | yes | None; repetition device instead ("Fifty one years. Fifty one.") | MISS |
| Compound-dollar math beat | yes | $200/mo → $60,000 off the finish line | **HIT** |
| Soft CTA ending | yes | "Tell me in the comments… hit the like button" | **HIT** |
| 10–15% AI-tell density | yes | Cleaner than predicted; genuinely decent prose | PARTIAL |

5 hits, 1 partial, 2 misses — structure fully predicted; prose quality above
the predicted floor.

## Backend prompting, inferred from the output

1. **Numbers written as words** ("two thousand twenty five", "two hundred and
   forty five thousand") — the script is pre-formatted for TTS. Their writer
   knows a voiceover pipeline sits downstream.
2. **Verbatim quotation as policy armor** — claims embedded as literal quoted
   sentences with dates and named sources, exactly matching the
   advice-rules disclosure at submission. The writer is instructed to quote,
   not paraphrase, anything factual.
3. **Research is search-first, not primary-source** — the Comptroller figure
   cites a Spectrum News reprint, not osc.ny.gov; the retirement model cites
   a blog reproducing another blog's model; budtender wages cite The
   Marijuana Herald. The researcher takes the first quotable credible-ish
   hit. Our provenance gate would flag two of the six.
4. **Pool-then-discard research** — the sources block lists a "Not used"
   entry (IRS 280E cannabis-business guidance). The pipeline researches a
   pool, the writer selects, the audit reports discards. Ironic detail: 280E
   means they researched the dispensary-OWNER angle — the operator's actual
   biography — and threw it away.
5. **Reference-following is structural, not conceptual** — Alicia's video is
   about stuff-vs-money; their script pivoted to savings-rate math and bonus
   volatility. The "reading your references" stage extracted pacing, not the
   thesis.

## Four-way verdict

- **Voice (the moat test):** A wins by construction; C scored zero first-person
  sentences — the system erased the one non-replicable asset, as predicted.
  D has her own signature; B predicted C's erasure exactly.
- **Best single idea:** C, credit where due — "promises get signed in a good
  year… priced at the top of the swing" (bonus volatility vs. fixed wage) is
  genuinely sharp and worth adapting into A's rule two.
- **Retention:** A plants and prices open loops; C's refrain ("a number small
  enough to fit on a receipt") is good but its quote blocks read stiff aloud.
- **Grounding:** C has real URLs but weak tiering; A is self-contained
  arithmetic + one flagged claim.
- **Shootability:** A maps 1:1 to coverage slots by design; C offers a
  spreadsheet, a till, a drawer, a receipt — thin scene material.
- **Extraction status:** complete. Adopt from C: TTS number-spelling, the
  research-pool/discard pattern, the bonus-volatility insight. Everything
  else we already do or do better.

**Process lesson (operator-caught):** panels A and B both violated "open
with concrete action" — a rule sitting in our own extracted rubric. C
followed it ("Two people are counting money…"). Extracting a rule is not
applying it; A's hook is rewritten to open in-scene (counting the drawer)
with the first-person moat intact. Also adopted from C: naming Mr. Money
Mustache — passed authority plus algorithmic topic-graph adjacency to the
FIRE cluster, seeded into A's rule-two tease.

**Reviewer-tool finding (second pass):** re-scoring the revised A dropped
7 → 6.5 while suggesting, as its hook fix, our own sentence reordered
verb-first — a valid syntax note, applied. But the judge is **stateless**: it
scored a 3-minute opening segment as a complete video (ending 5/10 for
"setting up the next topic" — which is the serialization device Tim's own
doctrine prescribes), counts stage directions as script words, and its
rewrite suggestions remain slop. Conclusion for the build-vs-buy file: the
rubric is worth keeping; the judge is one-pass-useful, then noise. Our own
review skill should score *segments in context*, which theirs cannot.

**$3,800/month verdict input:** the flagship's structure was predictable from
one day of doctrine extraction; its genuinely good ideas are one-time
learnings now recorded here.
