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

`ev-hedge-then-now-v1` validates through `ledger_page.py --variant bars` clean.

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
