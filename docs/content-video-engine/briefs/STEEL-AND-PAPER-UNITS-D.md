# Steel and Paper — the two extension units (Revision D)

Two P3/P5 pattern units taking Script C from 8m 24s to ~12m 50s. Units go
on **both sides of the pivot** — loading them all into P3 would push the
pivot to ~76% of runtime and break the 45–55% pin (doc 38).

Requires a **two-part chained take** — 12,400 characters exceeds mv2's
10,000 cap. See §3.

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

**Verified inputs only.** "More than five hundred percent" is +517.5%
measured. "Essentially sold out" is verbatim from the earnings call
(dossier E1). "Selling product, not issuing stock" is a characterisation,
not a financial claim — do not upgrade it to a number without pulling the
filing.

---

## 3. What this actually costs — measured, not estimated

| | |
|---|---|
| P3 debt unit | **969 chars** (~1m 0s) |
| P5 winner unit | **869 chars** (~0m 54s) |
| Script D total | **9,916 chars** → **~10m 19s** |
| mv2 cap 10,000 | **fits — single master take**, with 84 characters of headroom |
| Plates | 39 at 10m 19s = **15.9s each** (target 12, ceiling 20) |

**These units are half the doctrinal length.** Doc 38 specifies a P3
pattern unit at **2:00–2:30**; these run 1:00 and 0:54. They have the
correct five-step shape but only one anecdote loop each where the spec
calls for two or three.

That leaves a genuine fork:

**A — ship them as drafted.** 9,916 characters, ~10m 19s, **one master
take**, 84 characters under the cap. Misses the 11–13 minute ad target by
about a minute. No chaining risk.

**B — build them to spec** (2:00–2:30 each, ~2,100 chars apiece).
Script D becomes ~12,400 characters, **~12m 50s**, which hits the ad
target — and **exceeds mv2's 10,000 cap**, so it needs the two-part
chained take in §4. Each unit gains two more anecdote loops; the debt unit
has the material (the bond market's tech weighting, the 94%-of-cash-flow
figure), the winner unit would need one more verified case.

I would take **B**. The units are under-built against our own spec, the
runtime target is a real business constraint, and chaining is the
provider's supported path rather than a workaround. But A is genuinely
safer and available today.

**Plate density is the binding cost either way.** 39 plates was sized for
8 minutes. At 10m 19s that is 15.9s per plate; at 12m 50s it is 19.7s —
at the ceiling. Option A wants ~12 more plates, option B ~25. A wave-5
claim is required before either ships.

## 4. Delivery

| | |
|---|---|
| Characters | ~12,400 (Script C 8,078 + ~2,050 + ~2,270) |
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
