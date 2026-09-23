# Fed liquidity evidence dossier

Working claim review, 2026-09-18. This is not a release or render-eligibility receipt. Retained research is reviewed claim by claim; archive integrity does not confer blanket factual approval.

## Custody

Original archive: `docs/research/runs/fed-liquidity-2026-09-18/`, 14/14 declared hashes and byte counts independently matched. Fresh raw archive: `docs/research/runs/fed-liquidity-raw-fetch-2026-09-18/`, 15/15 fetched hashes and byte counts independently matched. Both manifests remain immutable. Original helper scripts were not executed. Episode-local source copies preserve hashes; `claims.v1.json` binds the planned script, including derived funding observations.

The original `rrp_history.csv` is excluded from production: seven duplicate dates, missing raw operation response and aggregation rule. The fresh FRED daily CSV is its candidate replacement, not an endpoint-interpolated series. Formal bridge checks remain FAIL for separately recorded orchestration/catalogue reasons; see `RESEARCH-INTAKE-REVIEW.md` and `PRODUCTION-LEDGER.md`.

## Opening historical comparison: accepted source reading

Source: original `sources/mpr_2025_06.html`, Table A (`xtable_balancesheet`). Column `xsheeta5` is change since June 1, 2022; comparison date `xsheeta2` is June 11, 2025; table unit is billions of dollars. Parent read the retained primary table directly.

| Row identifier | Printed row | Change, USD billions |
|---|---|---:|
| xsheetr13 | Total assets | -2238 |
| xsheetr15 | Reserves held by depository institutions | +72 |
| xsheetr18 | Reverse repurchase agreements: Others | -1760 |
| xsheetr19 | U.S. Treasury General Account | -504 |
| xsheetr17 | Reverse repurchase agreements: Foreign official and international accounts | +106 |

Bind all historical comparison marks to this one window. Do not call these current balances. The -1760 row is **Others**, not total reverse repos; retain the foreign-account distinction. These selected rows do not exhaust the balance-sheet reconciliation. A rebuild may compare asset and reserve changes; a complete balancing waterfall must include all relevant liabilities and capital, not manufacture a residual explanation.

## Remaining claim dispositions

- C1/C2, S01/S09: parent independently selected 3,329 numeric FRED observations through September 18; zero duplicate dates. Maximum: December 30, 2022, $2,553.716 billion. Latest: September 18, 2026, $0.576 billion. CSV and metadata now copied into episode custody with matching hashes and bound in `claims.v1.json`. Missing cells remain gaps; never label $576 million literal zero. Chart extraction/build still pending.
- C4: July 2026 MPR is a dated historical snapshot, not September current. Its reserve-management purchase initiation is December 2025; January describes continuation. Keep proposed December wording, not the research summary's January initiation.
- C5: date/type/units audit and deterministic extraction verified. 261 exact-date TGCR/SOFR/IORB joins, September 2, 2025–September 17, 2026. Latest TGCR3.83%, SOFR3.85%, IORB3.90% give -7bp/-5bp. September 18 daily funding observation is absent; no forward fill. Three future IORB rows excluded. Standing Repo:26 operations/13 business dates, $430m summed accepted take-up, not outstanding balance or ON RRP. Offering rate3.75% through September16,4.00% thereafter. Raw responses and metadata copied with verified hashes.
- C6: tax/payment diagrams are accounting illustrations with other balances held fixed, not documentary records of a particular taxpayer or contractor.
- C7: assets minus TGA minus domestic ON RRP is an analyst proxy, not official reserves, not an official Fed series, and not cash mechanically available for stocks. The $100 billion example remains explicitly hypothetical. No historical proxy chart until frequency/date/units are matched.
- C8: workshop borrower and expansion decisions are illustrative and conditional, not a measured business-loan result.

## Held interpretations

The proposed 14-business-day spread rule and three-day tax-date exclusion have no verified primary support and remain excluded. A zero-spread reference line can express an arithmetic comparison, but cannot be relabelled an empirically validated crisis threshold. Persistent funding pressure and loan transmission require separate evidence; a low ON RRP balance alone proves neither.

## Visual binding contract

Each rebuilt chart must carry source ID, source hash, observation date/window, units, extraction/derivation and the exact narrated claim. Source dates remain visible at comparison boundaries. Missing observations remain gaps, never silently forward-filled. Illustrations use an explicit label. Generated plates contain no evidentiary numbers or source text; those are authored from verified bindings in code. Parent extraction check PASS (1176 RRP observations,261 rate joins,26 Repo operations) and12 tests PASS; chart-object construction and visual/source reconciliation remain required before eligible rendering.
