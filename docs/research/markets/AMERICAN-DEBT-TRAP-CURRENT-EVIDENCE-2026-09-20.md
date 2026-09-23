# Inside the Great American Debt Trap: How It Becomes Your Problem

Research snapshot: 2026-09-20. Status: first primary-source pass complete; not approved narration or investment advice. VidIQ attachment is editorial input, not evidence. Existing pilot approvals and script remain unchanged.

## Editorial finding

Build around the cost of replacing cheap debt, not a guaranteed monetary reset. The tension is already measurable: federal interest expense consumes a substantial share of revenue while households encounter expensive new borrowing. The institutional-risk perspective is to follow the transmission and distinguish debt already locked at a fixed rate from debt that must reset. National debt does not mechanically determine every household rate; inflation, monetary policy, expected future rates, credit risk and loan terms also matter.

Reverse repo can support a later mechanism episode rather than carry this opening. Historical yield caps illustrate one possible policy response, not proof that today's government has chosen it.

## Primary observation ledger

FRED snapshots: [manifest](../runs/american-debt-trap-20260920/fred-manifest.json), containing exact retrieval times, URLs, hashes, dates and raw CSV paths. Latest means latest returned observation, not a September 20 trading quote. Rates are percent per annum unless noted.

| Claim | Observation date | Value | Source / qualification |
|---|---|---|---|
| Federal funds target | Sep 20 | 3.75–4.00% | [Lower](https://fred.stlouisfed.org/series/DFEDTARL), [upper](https://fred.stlouisfed.org/series/DFEDTARU); policy range, not market yield |
| Bank prime | Sep 17 | 7.00% | [DPRIME](https://fred.stlouisfed.org/series/DPRIME); not every borrower's offered rate |
| Treasury 2-year | Sep 17 | 4.67% | [DGS2](https://fred.stlouisfed.org/series/DGS2) |
| Treasury 10-year | Sep 17 | 4.94% | [DGS10](https://fred.stlouisfed.org/series/DGS10); Sep 16 was 5.01% |
| Treasury 20-year | Sep 17 | 5.32% | [DGS20](https://fred.stlouisfed.org/series/DGS20) |
| Treasury 30-year | Sep 17 | 5.29% | [DGS30](https://fred.stlouisfed.org/series/DGS30) |
| Average 30-year fixed mortgage | Sep 17 | 6.95% | [MORTGAGE30US](https://fred.stlouisfed.org/series/MORTGAGE30US); weekly survey, not guaranteed quote |
| Credit cards, accounts assessed interest | May observation | 22.15% | [TERMCBCCINTNS](https://fred.stlouisfed.org/series/TERMCBCCINTNS); lagged quarterly data |
| Credit cards, all accounts | May observation | 20.94% | [TERMCBCCALLNS](https://fred.stlouisfed.org/series/TERMCBCCALLNS); different population |
| National deposit rate, savings | August | 0.38% | [SNDR](https://fred.stlouisfed.org/series/SNDR); not a competitive high-yield offer |
| Fed total assets | Sep 16 | $6.746548T | [WALCL](https://fred.stlouisfed.org/series/WALCL); original units millions USD |
| Overnight reverse repo | Sep 18 | $0.576B | [RRPONTSYD](https://fred.stlouisfed.org/series/RRPONTSYD); not the standing repo facility |
| Gross federal debt | Sep 17 | $40.093343T | Treasury Debt to the Penny API, saved below |
| Debt held by public | Sep 17 | $32.392787T | Same API; do not interchange with gross debt |

Treasury raw [snapshot](../runs/american-debt-trap-20260920/data/treasury-debt.json) and [derived evidence](../runs/american-debt-trap-20260920/derived-evidence.json) retain API URL and SHA-256. Complete returned window: January 2025 through September 20, 2026; script asserts pagination completeness.

The first crossings in that window are $38T on October 21, 2025, $39T on March 17, 2026, and $40T on August 18, 2026. The last interval is **154 calendar days**. Do not use 'a trillion every 70 days' as the latest measured interval or extrapolate a constant pace.

## Federal budget evidence

[CBO's September 9 review](https://www.cbo.gov/publication/61984), [PDF tables 1 and 3](https://www.cbo.gov/system/files/2026-09/61984-MBR.pdf), estimates October–August FY2026 receipts at $4,845B, outlays at $6,812B, deficit at $1,967B, and net interest at $1,052B. These are preliminary fiscal-year-to-date estimates, not a completed annual total.

Derived: 1,052 / 4,845 = **21.71% of revenue**; 1,052 / 6,812 = **15.44% of outlays**. Suggested plain-language expression: 'About 22 cents of every federal revenue dollar went to net interest through August.' This is a ratio, not an earmarking claim. Keep the same denominator throughout a comparison. CBO attributes the rise in interest expense to larger debt and higher long-term rates, partly offset by lower short-term rates.

## Current event and historical audit

- [September 16 Fed statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm): use the dated decision rather than an undated 'just raised' hook that ages rapidly.
- [Treasury August 19 announcement](https://home.treasury.gov/news/press-releases/sb0607): maximum sizes for nominal 10–20-year and 20–30-year liquidity-support buybacks increased from $2B to at least $4B per operation, beginning September 9. This is not a doubling of every buyback, Fed QE, or a declared yield cap. A daily yield chart cannot establish that the program 'failed within 24 hours.'
- [Federal Reserve history](https://www.federalreservehistory.org/essays/treasury-fed-accord): short Treasury bill rates were pegged at 0.375% beginning in April 1942 and long bond yields implicitly capped at 2.5%; the 1951 Accord ended this arrangement. This supports a historical scene, not inevitable repetition. Do not retain the draft's 'cash halved in 1941–47' or '1942 debt/GDP 120%' without a separate historical series check.
- [New York Fed, June 25](https://tellerwindow.newyorkfed.org/2026/06/25/the-strategy-and-the-goals/): reserve-management purchases maintain ample reserves and adjust to demand. Projected portfolio growth is not a commitment to suppress long yields or monetize deficits.

## Household math: reproducible illustrations

[Calculation script](../runs/american-debt-trap-20260920/derive_evidence.py) and [results](../runs/american-debt-trap-20260920/derived-evidence.json). These are scenarios, not observed borrower histories.

- A $417,700 illustrative home with 20% down means $334,160 principal. Over 360 months, principal and interest are $2,005.61 at 6.01%, $2,169.58 at 6.76%, and **$2,211.97 at 6.95%**. Comparing 6.01% with 6.95% adds **$206.36/month**. Taxes, insurance, fees and mortgage insurance excluded. Do not call that house price the current median without a dated source. Do not date 6.01% to February without checking the exact observation.
- A 25-basis-point increase on an unchanged $6,610 card balance adds $16.53 in simple annual interest. At an illustrative 22.40%, simple annual interest is $1,480.64. The latest retrieved measured assessed-interest average is 22.15%; adding 0.25 is a scenario, not a newly published average. Actual payments and compounding change the result.
- $8,000 at 0.38% earns $30.40 annually; at an illustrative 3.49%, $279.20, a $248.80 gap before tax. The 3.49% product yield remains unverified and can change; money-market funds are not bank deposits.
- Paying off $6,610 at 22.40% rather than retaining it at 3.49% has an illustrative $1,249.95 annual interest difference, but leaves only $1,390 of an $8,000 cash balance. Liquidity needs and emergency borrowing risk prevent this being a universal instruction.
- A fixed-rate mortgage's contractual rate does not reset because the Fed raises rates. Variable debt and new/refinanced loans have different exposure. Extra principal generally shortens repayment rather than lowering the scheduled payment without a recast/refinance.

## Hold or replace these claims

Not release-ready from this pass: $41.1T statutory ceiling; 92% of mortgages fixed; HELOC average 7.26% becoming 7.51%; 2020 interest/revenue comparison; historical 'highest since' yield records; corporate $3T maturity wall and its precise window; nationwide 2%-to-7% refinancing claim; demographic workforce contraction forecast. Locate their actual underlying tables before using precise numbers. Existing user research may support them; absence from this packet is not a finding that they are false.

Reject deterministic leaps: moderate-long-rate mandate forces monetization; r exceeds g means immediate crisis; a rate hike automatically raises grocery prices; Treasury buybacks prove yield control; a forecasted SOMA balance is policy certainty.

Debt-ratio arithmetic must include the primary deficit: change in debt/GDP is approximately ((r-g)/(1+g)) times prior debt/GDP plus primary deficit/GDP, absent other adjustments. Use a consistent debt definition and effective interest cost, not a current 10-year yield applied instantly to all outstanding debt. A crossover year needs a reproducible scenario, not narration as fact.

Use only the operator-confirmed credential: Business Risk at JPMorgan. Do not inherit invented portfolio-risk duties from the draft. CTA remains subscribe for the next breakdown.

## Evidence and chart priorities

1. Debt timeline: Treasury gross debt, dated $38T/$39T/$40T crossings; trillion-dollar y-axis, calendar x-axis. Show the interval rather than a racing debt counter.
2. Interest burden: one revenue dollar, 21.71 cents allocated to net-interest comparison; label FY2026 October–August, preliminary. A full ledger is useful for calculation, then dock the result into the narrative world.
3. Rate timeline: separate or clearly labeled policy range and 10-/20-/30-year yields, Jan 2025 onward, percent axis. Never imply same-day movement proves a single cause.
4. Household receipt: same principal and term, two rate/payment states; animate the $206 monthly difference, not a fully built static chart. Label illustrative comparison.
5. Exposure map: fixed existing mortgage / variable card or HELOC / new refinancing; follow one character's obligations rather than switching to unrelated stock icons.
6. Optional later historical scene: 1942–1951 rate-cap timeline, explicitly historical; current policy stays a separate layer.

Keep the six narrative-art candidates per minute rule as an inventory floor, not a mandatory cutting rhythm. Source IDs and exact observations belong in the evidence ledger and description; essential period, units and scenario labels must remain visible. Animate toward specific endpoint values/labels, not generic bar lighting.

## Execution / limitations

Direct FRED: 18 series fetched successfully, raw CSVs preserved. Treasury daily data and reproducible arithmetic saved. Primary CBO, Treasury and Federal Reserve pages inspected. No yfinance dependency was needed for these claims. Gemini work order is saved but **not dispatched**: bridge discovery lacked ANTIGRAVITY_LS_ADDRESS and ANTIGRAVITY_CSRF_TOKEN. No external research completion is claimed.

Next production decision: build the narrative outline from the verified debt-cost and household-transmission spine. Any held precise claim must gain a source before narration freeze; historical cash-loss and demographic branches are optional and need not block the core episode.
