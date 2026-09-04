# The stronger story, from the Treasury's own release

Fetched 2026-09-03 from `ticdata.treasury.gov/…/slt_table5.txt` — TIC Table 5, Major
Foreign Holders of Treasury Securities. Monthly, authoritative, re-fetchable, and the
viewer can open it.

## Japan is selling. Hard. Right now.

| month | Japan holdings | m/m |
|---|---|---|
| 2026-02 | **$1,239.3 B** ← peak | +14.0 |
| 2026-03 | 1,191.6 | −47.7 |
| 2026-04 | 1,209.9 | +18.3 |
| 2026-05 | 1,143.1 | **−66.8** |
| 2026-06 | **1,116.7** ← latest | −26.4 |

**−$122.6 B in four months. −9.9%.** Still the #1 foreign holder (UK $939.9 B, China
$633.4 B), still over a trillion, now 12.0% of all foreign holdings.

## And the hedge explanation does not fit

This is the part nobody is reporting, and it is the opposite of what the script
assumed:

| | at the worst (2023-05) | now (2026-09) |
|---|---|---|
| FX hedge cost | 5.35% | **2.42%** |
| net hedged yield on a US 10Y | **−1.90%** | **+2.14%** |

**Hedging is less than half what it cost, the trade pays two points, and they are
selling anyway.** The mechanism every explanation reaches for — the one the script
was built on — stopped applying in November 2024. The selling started fifteen months
later.

## Why this is the better video, not the weaker one

The original frame ("hedging costs too much so Tokyo stopped") was a *true story about
2023* told in the present tense. The operator's proposed fallback ("it might go
negative again, and the setup looks structurally worse") is weaker still — it needs a
forecast, and "structurally worse" is a claim with no series behind it.

What the data actually supports is stronger than both, and it is present tense:

> **Our biggest customer is selling — and the reason everyone gives is two years out
> of date.**

Every load-bearing line survives untouched. "Our biggest customer just stopped
buying" is now *literally* true and quantified. "Tokyo took a tea break" — true.
"Unfunded bar tab" — true. "Over a trillion" — true. And it gains a **head-fake**,
which the script never had: the hedge-cost explanation is set up, credited, and then
demolished by its own numbers. That is this channel's core move — the opponent is a
mechanism, and here the mechanism everyone names turns out to be innocent.

## What changes in the script

Only the tell's variable. It moves from the hedge cost to the holdings themselves —
which is *better*, because the viewer can check it monthly on a government page:

> The variable: what Japan actually holds, published every month by the US Treasury.
> The threshold: they were adding; now they're selling. Where we sit: down a hundred
> and twenty billion since February. The flip: they start buying again — and if they
> do and yields don't fall, I was wrong, and I'll say it here.

The hedge cost becomes the head-fake, spoken as a steelman before it is taken apart:
credit the explanation, show it was right in 2023, show it stopped being right, and
leave the real question open. **This is not a claim about why** — the honest position
is that the consensus mechanism does not explain it, not that we know what does.

## Corrections this forces

- `player.html` asserts Japan is **14.5%** of foreign holdings. Actual: **12.0%**.
- `player.html` asserts China **$770.2 B**, UK **$745.8 B**. Actual: China **$633.4 B**,
  UK **$939.9 B** — the UK figure is wrong by ~$194 B and the ranking is wrong: the UK
  is #2, not #3.
- The hedged-yield chart's `5.0 / −5.5 / −0.5` is replaced by the real series.

## Charts this makes

1. **Japan's holdings, monthly** — the peak, the four-month slide, the latest print.
   One sentence: "our biggest customer is selling."
2. **Net hedged yield, 2022→now** — crossing zero in late 2024 and sitting at +2.14%.
   One sentence: "and the reason everyone gives stopped being true two years ago."

Two charts, two sentences, both re-fetchable, both checkable by the viewer. The P/E
payoff and the `$1.1T · #1` badge are unaffected.
