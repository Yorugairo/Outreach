# BLOCKING FINDING — the short's central arithmetic does not hold on current data

Fetched live from FRED, 2026-09-03. Every figure below is re-fetchable.

## What the script says

> "But now it costs **five and a half percent** to hedge the currency on a **five
> percent** Treasury… Where we sit: **five and a half against five — underwater.**"

…and frames it as **this month** ("Bond yields crossed critical levels **this month**").

## What the data says

| figure | script | actual | series | as of |
|---|---|---|---|---|
| US 10-year Treasury | 5.0% | **4.79%** | `DGS10` | 2026-09-02 |
| US 3-month | — | 3.92% | `DGS3MO` | 2026-09-02 |
| Japan 3-month interbank | — | 1.27% | `IR3TIB01JPM156N` | 2026-05-01 |
| FX hedge cost (US 3M − JPY 3M) | 5.5% | **~2.65%** | derived | 2026-09 |
| **Net hedged yield** | **−0.5% (underwater)** | **+2.14% (positive)** | derived | 2026-09 |

Two separate problems:

1. **The 10-year has not printed 5.00% since 2007-07-19.** Not in 2023 either — it
   peaked just under. "A five percent Treasury" has no date on which it is true.
2. **The trade is not underwater. It is comfortably positive, and has been for two
   years.** The hedge cost collapsed from 5.35% to 2.42% because the Fed cut and the
   BoJ hiked — the two legs converged.

## When it WAS true — the real story is dated, and it is better

Net hedged yield was negative in **35 months**, ending **2024-11**:

| | month | net hedged |
|---|---|---|
| first negative | 2006-10 | −0.02% |
| **worst** | **2023-05** | **−1.90%** |
| last negative | 2024-11 | −0.04% |
| today | 2026-05 (latest aligned) | **+2.03%** |

So the premise is real history, not current events. The honest versions:

- **Retrospective:** "For two years Tokyo *couldn't* buy — hedged, our bonds paid them
  less than nothing. That's over. The hedge cost fell from five and a third to two and
  a half, and Tokyo came back." That is the script's own tell **already firing** — the
  flip condition it names ("the hedge drops back under the yield, and Tokyo comes
  back") has *happened*, which is a stronger, checkable story than a warning.
- **Or** re-target: if the claim is that Japanese demand is still absent for a
  different reason, the evidence for *that* reason has to be fetched, and the hedge
  arithmetic is no longer the mechanism.

## What this blocks

The tell — variable, threshold, where we sit, the flip — is the spine of the close and
**"where we sit" is wrong by ~2.6 points, with the sign inverted.** Recording it as
written would put a false, checkable claim on the channel's first Facebook short.

The chart cannot be built to match the script; the script has to move to the data.
That is a DECISION, not a fix I should make silently.

## Recommendation

Take the retrospective. It costs one paragraph, it keeps the tea-break ring and the
"unfunded bar tab" line intact, and it upgrades the tell from a prediction to a
**receipt** — the mechanism this channel exists to show, with the flip already
observable in the series. The chart then plots the real thing: net hedged yield,
2022→now, crossing zero in late 2024, with the trough at −1.90% in May 2023.

Nothing else in the script depends on the wrong figures — the trillion, the "biggest
customer," and the P/E payoff all survive unchanged.
