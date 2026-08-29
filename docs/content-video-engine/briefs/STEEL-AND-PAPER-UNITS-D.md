# Steel and Paper — the two extension units (Revision D)

Two P3/P5 pattern units extending Script C. Units go on **both sides of
the pivot** — loading them all into P3 would push the pivot to ~76% of
runtime and break the 45–55% pin (doc 38).

**As drafted: 9,916 characters, ~10m 19s, one master take.** Built out to
the doctrinal 2:00–2:30 unit length: ~12,400 characters, ~12m 50s, needing
a chained take. See §3 for the fork.

---

## 0. A claim that died in verification

The Korea unit was going to run on the ledger's own example: *"Samsung SDI
+125%/yr while posting losses"* — the affiliate froth outrunning the
parents. **Checked it against the tape, and it is false today:**

| | 1-year return |
|---|---|
| SK hynix | **+517.5%** |
| Samsung Electronics | +273.9% |
| Samsung SDI (affiliate) | **+164.4%** |

The affiliates are not frothing past the giants — they are **lagging them
badly.** SK hynix alone is up more than five-fold. The ledger's figure was
stale, and the "froth outruns the parents" story is the wrong way round
right now. The contagion monitor agrees: no divergence trigger is lit.

So the P5 unit was rebuilt around what is actually true, and it turns out
to be the stronger beat: **run the test on the biggest winner in the
complex and watch it pass.**

---

## 1. P3 — THE DEBT UNIT

Placement: after the existing P3 unit, before *"And that's where most
people — including, this one time, Bravos — get the whole thing wrong."*

Evidence: `ev-capex-consensus-v1` · `ev-doc-leases` (record document)

> For years the giants paid for this out of pocket. Cash on hand, no
> borrowing — that was the whole flex. Then the bills got bigger than the
> cash.
>
> Between 2020 and 2024, the five of them borrowed about twenty-eight
> billion dollars a year, between them. Last year: a hundred and
> twenty-one billion. This year they're tracking toward a hundred and
> fifty.
>
> `[pre-key]` And that's the borrowing you can see. `[post-key]`
>
> Go into the filings and there's another eight hundred and twenty-two
> billion in lease commitments. Data centers they've already agreed to pay
> for, on contracts already signed, that haven't landed on a balance sheet
> yet. Not hidden — the number's right there in the filing. Just not
> counted where anyone looks.
>
> So when you hear these companies are funding the buildout out of
> profits: that was true. It stopped being true about eighteen months ago.
>
> Nobody committed fraud here. They signed a promise, in a year that
> looked good. And promises are the part of this nobody's charting.

Shape check — anecdote run (paid cash → bills outgrew cash → borrowed),
BUT the gap opens (that's the borrowing you can *see*), THEREFORE the
deeper move (the profit story expired), reflection (a promise made in a
good year), rehook out (nobody's charting promises → sets up the pivot).

Register: plain throughout. "Not hidden — the number's right there in the
filing" addresses the viewer as competent (VOICE-PACK). The one figure of
speech, "the whole flex," attaches to the companies — people making a
boast — so it passes the referent test. Nothing borrows the pivot's
language; "priced off the best year" stays unspent for P4.

## 2. P5 — THE BIGGEST WINNER

Placement: after *"It's the test, administered in public"*, before the
tell.

Evidence: `ev-krx-memory-v3` · `ev-instrument-memory` · the SK hynix
"essentially sold out" line from the October earnings call.

> Run it on the most extreme number in this whole trade and see what
> happens.
>
> SK hynix. They make the stacked memory the AI racks need. Over the last
> year the stock is up more than five hundred percent. Not fifty. Five
> hundred. `[pre-key]` If anything in this story is a bubble, it should be
> that. `[post-key]`
>
> So ask it the three questions. Scarce? Their own earnings call says
> capacity is essentially sold out for the year — you cannot buy what they
> haven't got. Cash or paper? They're selling product, not issuing stock
> to survive. Used tomorrow morning? The memory is going into racks that
> are already under construction.
>
> Scarce, cash, used. It passes. The most vertical line on the board is
> steel.
>
> That's the uncomfortable part of this test — it doesn't care what you
> were hoping to conclude. Run it honestly and it'll clear names you
> wanted to short, and flag things you're already holding.

Shape check — anecdote (the most extreme number), BUT the gap (if anything
is a bubble it should be this), THEREFORE the move (it passes), reflection
(the test doesn't care what you hoped), rehook (it'll flag things you
hold → straight into the tell).

Why it beats the affiliate-froth version: it applies the episode's own
instrument to the hardest case rather than a convenient one, and it earns
P6's "more bullish than Bravos" instead of merely asserting it. It also
avoids naming a specific stock as froth, which was the highest-risk
content in the episode.

**It ADDS to the divergence beat, it does not replace it** (operator,
2026-08-29 — correcting an earlier call of mine that the two were
duplicative). They are a general→specific escalation and only work as a
pair: the divergence beat proves scarcity is being repriced across the
whole sector; this one takes the single most vertical name on the board
and shows the test *still* clears it. The sector sets it up; the name
lands it. Cutting either weakens the other.

**Verified inputs only.** "More than five hundred percent" is +517.5%
measured. "Essentially sold out" is verbatim from the earnings call
(dossier E1). "Selling product, not issuing stock" is a characterisation,
not a financial claim — do not upgrade it to a number without pulling the
filing.

---

## 3. Measured, built out

The debt unit is now built to the doctrinal 2:00–2:30 (doc 38) using three
verified figures the episode has never used: the bond market's tech
weighting, the capex consensus trajectory, and the 94%-of-operating-cash-
flow number. Draft: `steel-and-paper/unit-debt-draft.txt`.

| | chars | runtime |
|---|---|---|
| Script C | 8,078 | 8m 24s |
| P3 debt unit (built out) | **1,920** | ~2m 0s |
| P5 winner unit (as drafted) | 869 | ~0m 54s |
| **Script D** | **10,867** | **~11m 18s** |
| with the winner unit given one more loop | 11,268 | ~11m 43s |

**Exceeds the 10,000 mv2 cap → two-part chained take** (§4). That is the
cost of the runtime target, and it is a real one — but chaining is the
provider's supported long-form path, not a workaround.

**Plate density is the binding constraint, not credits.** 39 plates were
sized for eight minutes. At 11m 18s that is 17.4s per plate — inside the
20s ceiling but well past the 12s target. Hitting target needs **56
plates, so ~17 more**. A wave-5 claim is required before this ships, and
it is the longest pole in the job.

## 4. Delivery — only if option B

| | |
|---|---|
| Characters | ~12,400 (Script C 8,078 + two units at ~2,100 each) |
| Runtime | **~12m 50s** at 16.02 chars/sec |
| mv2 cap | 10,000 — **exceeded** |
| Delivery | **two chained requests**, part two conditioned on part one's `previous_request_ids` |
| Split point | at a phase boundary, ideally P4 → P5 |
| Plates | 39 at 12m 50s = 19.7s each — **at the 20s ceiling**; wants ~25 more plates or a wave-5 |
| Pivot position | recheck against the 45–55% pin after the split |

**Chaining is not splice-repair.** Doc 37 §8 bans stitching fixes into a
broken take — that produced the 6:20 fragment artifacts, which came from
raw MP3 concat of independently generated segments. A planned two-part
take passing `previous_request_ids` is the provider's supported long-form
path and carries prosody across the join. Worth writing into §8 explicitly
so the ban is not misread.

**Plate density is the real cost.** 39 plates was sized for ~8 minutes. At
12m 50s we are at the ceiling, not the target. Extending the script means
a wave-5 plate claim before this can ship.
