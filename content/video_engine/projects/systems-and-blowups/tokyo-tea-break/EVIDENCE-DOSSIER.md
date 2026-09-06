# Tokyo Tea Break — evidence dossier

Every figure the script speaks, its source, and the date it was fetched. Nothing here
is estimated. Regenerate with:

```bash
python content/video_engine/projects/systems-and-blowups/tokyo-tea-break/evidence/build_tokyo_evidence.py
```

The builder fails loudly if any source is unreachable rather than emitting a number
nobody can check. Machine-readable output: `evidence/FIGURES.json`.

**Fetched 2026-09-03. Every row re-verified against the live source on that date.**

---

## Spoken figures

| the script says | actual | source | verdict |
|---|---|---|---|
| "over a trillion dollars of American debt" | $1,116.7 B | TIC Table 5, 2026-06 | **PASS** |
| "more than anyone" | UK $939.9 B is #2; China $633.4 B #3 | TIC Table 5, 2026-06 | **PASS** |
| "a hundred and twenty-two billion" | −$122.6 B from the 2026-02 peak | TIC Table 5 | **PASS** |
| "hedging costs half what it did" | 5.54% (2023-05) → 2.42% (2026-05) | FRED, derived | **PASS** |
| "the trade pays two full points" | +2.03% net hedged | FRED, derived | **PASS** |
| "two years ago that was right" | last negative month 2024-11 | FRED, derived | **PASS** |
| "pull up Meta… find its P/E" | 23.0 trailing — **the script asserts no value** | Yahoo via yfinance | **PASS** |
| "sixty-three stick figures" | rhetorical, not a count | — | JOKE, marked |

## Sources

| id | what | cadence |
|---|---|---|
| `ticdata.treasury.gov/…/slt_table5.txt` | TIC Table 5, Major Foreign Holders of Treasury Securities | monthly |
| FRED `DGS10` | US 10-year Treasury constant maturity | daily |
| FRED `DGS3MO` | US 3-month Treasury | daily |
| FRED `IR3TIB01JPM156N` | Japan 3-month interbank rate | monthly |
| Yahoo via `yfinance` | META trailing P/E | live |

**Derived, not quoted:** FX hedge cost = US 3M − JPY 3M (the rate differential, ex
cross-currency basis). Net hedged yield = US 10Y − hedge cost. Both computed in the
builder and shown with their inputs on the chart's source line, so the arithmetic is
visible rather than asserted.

## Charts built

| sidecar | proves | form |
|---|---|---|
| `ev-japan-holdings-v1` | "our biggest customer is selling" | line, 26 months, peak → latest |
| `ev-hedged-yield-v1` | "the reason everyone gives stopped being true" | line, 2022→now, zero crossing |
| `ev-hedge-then-now-v1` | the head-fake, compressed | ledger bars, worst vs now |
| `ev-discount-rate-v1` | "a high yield is what discounts it" | ledger bars, $1 of year-10 profit at 3/4/5/6% |

`ev-hedge-then-now-v1` and `ev-discount-rate-v1` both validate through
`ledger_page.py --variant bars` clean.

### The discount-rate chart is arithmetic, deliberately

It plots the discount identity **1/(1+r)^10** — what $1 of profit arriving in ten
years is worth today at each rate. $0.744 at 3%, $0.614 at 5%: **−18%**. No growth
assumption, no terminal value, no fair-value claim about Meta. A viewer can redo it on
a phone.

Meta's real multiple rides as a **badge**, not as a model input: the P/E says how much
of the price is profit that hasn't happened yet, the bars say what that profit is worth
as the yield moves. Two facts side by side, no forecast joining them — which is also
why the script tells the viewer to look the P/E up rather than quoting it.

**E28 caught the first version.** I had put the −18% in a bar *note* while the bar's
value stayed an unsigned magnitude, and the validator refused it: a signed claim beside
an unsigned bar. The signed change now lives on a badge and the bars are pure present
values whose descending heights are the argument.

## Corrections this dossier forces on `player.html`

Three figures currently rendered are wrong and must not ship:

| player.html asserts | actual (2026-06) |
|---|---|
| Japan = 14.5% of foreign holdings | **12.0%** |
| China $770.2 B | **$633.4 B** |
| UK $745.8 B, ranked #3 | **$939.9 B, ranked #2** |

The old `tokyo-hedged-yield.{page,series}.json` (5.0 / −5.5 / −0.5) is superseded by
`ev-hedge-then-now-v1` and must not be rendered — its numbers were typed, and the
premise they encoded (the trade is underwater) has been false since 2024-11.

## Standing exposure

The TIC release lags by roughly two months and updates monthly; FRED's Japan interbank
series is monthly. **Re-run the builder before recording.** If the holdings turn back up
before publication, the script's own tell fires — "they buy again, and if yields don't
fall I was wrong" — and the video needs re-cutting, not patching.

---

## Addendum 2026-09-04 — the rewrite's hook, sourced (SCRIPT-90S-VO.claude.txt)

Re-ran the builder the same day: TIC still prints 2026-06 (no July release yet), Japan
$1,116.7 B, −$122.6 B from the February peak (−9.9 %), net hedged +2.03 %. Every dossier
row above still PASSes. Two hook lines were new and needed their own sources:

| the script says | actual | source | verdict |
|---|---|---|---|
| "The Fed didn't move an inch this month" | upper target 3.75 % on every day 2026-08-30 → 2026-09-04 | FRED `DFEDTARU` | **PASS** |
| "your borrowing cost climbed anyway" | 30-year mortgage 6.55 % (07-16) → 6.71 % (09-03); 10-year 4.63 % (08-04) → 4.79 % (09-01) | FRED `MORTGAGE30US`, `DGS10` | **PASS** — a 16 bp rise; the script says *climbed*, not *jumped*, on purpose |
| "a tenth of the pile" | −9.9 % | TIC Table 5 | **PASS** |
| "two years ago it cost Tokyo more than our bond paid" | last negative month 2024-11 (22 months) | FRED, derived | **PASS** |
| "hedging now costs half" | 5.54 % → 2.42 % (less than half) | FRED, derived | **PASS** |
| "The threshold: the pile grows, or shrinks. Where we sit: a tenth below February." | monthly prints Mar −47.7 / Apr **+18.3** / May −66.8 / Jun −26.4 | TIC Table 5 | **PASS** — worded against the *peak*, because "four straight months of selling" would be false: April was up |

Dropped from the spoken text, deliberately: the Meta P/E beat and the discount-rate
arithmetic (doc 51: one mechanism per short — the number the viewer reads is the holdings
print; `ev-discount-rate-v1` stays built for the long-form P1), and any sell instruction
(operator, 2026-09-03: "exiting 20-year Treasuries is useless advice on a short").

| "Tokyo has pledged ten trillion yen to chips and AI" | PM Ishiba's plan: support worth ¥10 trillion (~$65 B) or more by fiscal 2030 for semiconductors and AI (Rapidus + onshored fabs) | CNBC 2024-11-13, "Japan is ramping up efforts to revive its once dominant chip industry"; Bloomberg 2024-11-29, "Japan earmarks extra $9.9 billion for chips and AI this year" | **CITED** — a pledge, spoken as a pledge; "if that works" keeps the return claim conditional. **"My read: the money went home" is the narrator's read, attributed as such, not a sourced flow-of-funds claim** (operator, 2026-09-04: no commitment to Japan buying again) |

| "the second number is on your phone... a higher yield discounts it" | **`ev-meta-yield-v1`** (2026-09-04): Meta trailing P/E **23.0x** (Yahoo via yfinance) at the 10-year's **4.77 %** (FRED DGS10); the same year-10 dollar supports **24.8 / 23.6 / 22.5 / 21.5x** at 4 / 4.5 / 5 / 5.5 %, shown as a PRICE on the page: trailing EPS $26.83 x the multiple = **$665 / $633 / $604 / $577** against **$617 now** - **-$40 a share, -$647 on $10,000, -6.5 % at 5.5 %** | builder `meta_yield()`; validates through `ledger_page.py --variant bars` | **CITED + derived** - the "now" bar is live, the others are arithmetic on it; no growth, no forecast. Operator, 2026-09-04: the signpost beat shows this chart, not a phone |

## Addendum 2026-09-06 — the description's history claim, sourced (SCRIPT-90S-DESCRIPTION.md)

The draft description said "40 years of accumulation, with 4 years of it gone" (linear arithmetic on "a tenth of the
pile"). The pile did not grow evenly, so the arithmetic is not a figure. Checked against the TIC historical table
(`https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/mfhhis01.txt`, fetched 2026-09-06,
columns run Dec → Jan within each year):

| the description says | actual | source | verdict |
|---|---|---|---|
| "4 years of it gone in 4 months" | Japan's holdings were last at or below June's $1,116.7 B in **January 2025 ($1,079.3 B)**; the February 2026 peak undid **about 17 months** of buying, not four years | mfhhis01.txt 2025 row (Jan 2025 = last column) vs TIC Table 5 2026-06 | **FAIL as written → reworded "back to where it stood in January 2025"** |
| "40 years of accumulation" | the historical file starts in 2000 (Japan $317.7 B, Jan 2000); a 40-year span is plausible from other TIC series but is not on file here | mfhhis01.txt | **[VERIFY]** — say "decades" or source the 1980s series first |
| the February 2026 peak | $1,239.3 B is the recent peak, not the record: the all-time high is **$1,325.5 B, November 2021**; June 2026's level was exceeded through most of 2015–16 and 2020–22 | mfhhis01.txt 2021 row | context for any "record" wording — never say record |
