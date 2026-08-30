# THE RAILWAY YARDSTICK — recurring instrument

Adopted by the operator 2026-08-30: *"almost a central piece to the episode...
maybe even a regular piece of my tracking... few people have that analysis
layer... simultaneously very sharp and easy to understand."*

## The measurement

**What share of ALL US private capital formation does the tech buildout
take?** — the same question Campbell & Turner's railway-mania literature
answers for Britain 1844–47 (~50%, one technology).

| Line | Definition | FRED series |
|---|---|---|
| **narrow** (the claim) | information-processing equipment + software / GPDI | (Y034RC1Q027SBEA + B985RC1Q027SBEA) / GPDI |
| **broad** (the context) | all equipment + intellectual property / GPDI | (Y033RC1Q027SBEA + Y001RC1Q027SBEA) / GPDI |

**The definitional caveat rides with every reading:** the railway 50% was
ONE technology against Britain's total capital formation. Neither US line
is single-technology; the broad line crossing 50% is NOT "AI exceeds
railway mania." The narrow line is the honest internet/AI-era claim.

## Cadence and method

- Quarterly (BEA data, revised; a new quarter lands ~1 month after quarter
  end). Run `update_yardstick.py`: fetches FRED (keyless), appends the
  dated reading to `readings.jsonl`, regenerates the chart PNG + live
  sidecar through the episode builder.
- Every reading is dated and kept — the log IS the tracking.

## Tripwire — DECISION, operator-owned

An instrument carries four parts (doc 35): one variable, one threshold,
where we sit now, what flips us. Variable: the narrow line. Now: 28%
(above the 23% dot-com high). **The threshold and what-flips-us are the
operator's to set, not generated** — candidates to choose from, not
defaults: (a) a fixed level (30%?), (b) the dot-com high held for N
quarters, (c) rate-of-change over 4 quarters. Until set, episodes cite
the reading, never a tripwire.

## First readings

See `readings.jsonl`. Baseline 2026-08-30: narrow 28%, broad 65%,
dot-com high on the narrow line 23% (2000).
