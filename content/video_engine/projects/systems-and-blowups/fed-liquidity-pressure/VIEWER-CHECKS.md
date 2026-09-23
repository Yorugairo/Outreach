# Three checks — source handout and end-card contract

Working production artifact, not published. This is the concrete deliverable promised in the opening. Link this handout's source list in the eventual description and show source names on the corresponding evidence frames. Do not ask viewers to trust an unnamed dashboard.

## 1. Follow the money

Identify the account the headline actually measures. Compare its dated observations with bank reserves, rather than treating every decline as money vanishing.

- Overnight cash parked by money funds: [FRED RRPONTSYD data](https://fred.stlouisfed.org/graph/fredgraph.csv?id=RRPONTSYD).
- Bank reserve balances: [FRED WRBWFRBL](https://fred.stlouisfed.org/series/WRBWFRBL).
- Total Fed assets: [FRED WALCL](https://fred.stlouisfed.org/series/WALCL).
- Historical account reconciliation: [Federal Reserve June 2025 Monetary Policy Report, Part 2](https://www.federalreserve.gov/monetarypolicy/2025-06-mpr-part2.htm).

Chart handling: display each observation date and units. Daily and weekly data are not interchangeable; compare matched dates where a relationship is asserted. Missing observations remain missing. The episode's historical June 2025 comparison is not a current reserve-balance reading.

## 2. Check the price

Look at what institutions pay to borrow overnight against Treasury collateral, then compare it with the rate the Fed pays on reserve balances. The detailed calculation belongs to the next breakdown; this episode supplies the check and its sources.

- [New York Fed TGCR observations used in this episode](https://markets.newyorkfed.org/api/rates/secured/tgcr/search.json?startDate=2025-09-01&endDate=2026-09-18).
- [FRED interest on reserve balances](https://fred.stlouisfed.org/series/IORB).

Compare the same effective date. For rates expressed in percent, `(TGCR − IORB) × 100` gives the difference in basis points. Zero is a comparison line, not a proven crisis trigger. The owner's refinancing quote remains a separate price with credit risk and loan terms in it.

## 3. Check whether it lasts

Read successive dated observations, not a single dramatic screenshot. Ask whether the premium recedes after the cash movement or keeps returning. This episode does not invent a fixed number of days that turns pressure into a crisis.

Then return to the borrower: when does the old loan expire, what is the replacement quote, and how much cash is left after the new payment? This connects the market story to the human stakes without pretending an overnight rate is a business's actual loan offer.

## Production binding

Source URLs are drawn from this episode's `claims.v1.json` and retained extraction metadata. Live URLs may update; on-screen historical claims remain bound to the archived bytes and dates in the evidence ledger. This file is not a new claim approval or a substitute for the actual ledger.

End-card copy: **Follow the money. Check the price. Check whether it lasts.**

CTA stays: **Subscribe for the next breakdown.** No strategy-call booking.
