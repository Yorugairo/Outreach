# Federal Reserve Liquidity, Balance Sheet Dynamics, and Money Market Pressure (As of September 18, 2026)

Generated: 2026-09-18  
Scope: Primary-source audit of Federal Reserve Overnight Reverse Repo (ON RRP) depletion, bank reserve balances, Treasury General Account (TGA) swings, quantitative tightening (QT) cessation, Reserve-Management Purchases (RMP), and repo rate spreads (TGCR/SOFR/IORB).  
Status: Grounded, fully verified primary data.

## Verdict up front
Primary-source Federal Reserve observations as of September 18, 2026 contradict the mechanical thesis that ON RRP depletion and Treasury cash swings inevitably trigger a repo crisis or drain bank reserves into economic collapse. While ON RRP take-up has indeed drained from a year-end 2022 peak of $2,553.716 billion ($2.55 trillion) to $0.576 billion ($576 million) as of September 18, 2026, bank reserves have remained ample ($2,921.536 billion spot / $3,013.794 billion weekly average) because balance sheet runoff (QT) terminated on December 1, 2025 and the Fed initiated technical Reserve-Management Purchases (RMPs) of Treasury bills in January 2026. Money market funding rates remain completely orderly with TGCR (3.83%) and SOFR (3.85%) trading comfortably below IORB (3.90%), confirming that the popular retail formula "Assets minus TGA minus ON RRP" is an invalid proxy that overstates bank reserves by $2.828 trillion and conflates money-market plumbing frictions with macroeconomic liquidity.

---

## 1. Track 1: ON RRP Peak, Monthly Mean, and Latest Observation

### Core Observations
- **All-Time Daily Peak Date**: `2022-12-30`
- **All-Time Daily Peak Value**: `$2,553,716,000,000` ($2,553.716 billion = $2.553716 trillion).
  - Proof: [New York Fed 2022 Open Market Operations Report | URL: https://www.newyorkfed.org/medialibrary/media/markets/omo/omo2022-pdf.pdf | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track1.md#L7).
  - Underlying API: [New York Fed Markets Repo API | URL: https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json?startDate=2022-12-01&endDate=2022-12-31 | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track1.md#L30).
- **December 2022 Monthly Mean Across All 21 Operations**: `$2,184,700,190,476.19` ($2,184.700 billion = $2.1847 trillion).
  - [DERIVED: Sum of totalAmtAccepted across all 21 operations in December 2022 ($45,878,704,000,000) divided by 21 operations = $2,184,700,190,476.19] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track1.md#L8).
- **Latest Published Observation on/before September 18, 2026**: `2026-09-18`
- **Latest Observation Value**: `$576,000,000` ($0.576 billion).
  - Proof: [FRED Economic Data Series RRPONTSYD | URL: https://fred.stlouisfed.org/series/RRPONTSYD | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track1.md#L41).
  - Cross-Verification: [New York Fed Markets Repo API | URL: https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json?startDate=2026-09-01&endDate=2026-09-18 | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track1.md#L9).
  - Authoritative Daily History CSV: docs/research/runs/fed-liquidity-2026-09-18/rrp_history.csv (955 rows).

### Daily vs. Period-Average Distortion Mechanics
1. **Window-Dressing Contraction**: Commercial banks and foreign banking organizations face stringent balance-sheet regulatory metrics on year-ends and quarter-ends (Basel III Leverage Ratios, Supplementary Leverage Ratio / SLR, and G-SIB capital surcharges). To minimize regulatory scores, banks shed repo borrowing and reduce non-deposit liabilities at year-end.
2. **Flight to the Facility**: Government Money Market Funds (MMFs), facing severe reductions in private dealer repo capacity, redirect cash into the Federal Reserve's ON RRP facility as a counterparty of last resort.
3. **Quantified Distortion**:
   - [DERIVED: Year-end distortion magnitude = December 30 peak ($2,553.716B) minus December monthly mean ($2,184.700B) = +$369.016 billion (+16.89% spike)] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track1.md#L55).
   - This spike unwound by $253.805 billion on the very next business day (January 3, 2023: $2,299.911 billion).

---

## 2. Track 2: Matched-Date Federal Reserve Balance Sheet Liabilities

### Core Observations
- **Primary Release**: Board of Governors of the Federal Reserve System, Statistical Release H.4.1 ("Factors Affecting Reserve Balances"), published September 17, 2026.
- **Matched As-Of Date**: `Wednesday September 16, 2026` (Spot Levels) and `Week Ended September 16, 2026` (Weekly Averages).
- Proof: [Federal Reserve Statistical Release H.4.1 | URL: https://www.federalreserve.gov/releases/h41/current/ | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track2.md#L7).

### Matched-Date Balance Sheet Accounting (September 16, 2026)
*Units: Millions of US Dollars (original H.4.1 reporting units)*

| Item | H.4.1 Table | Wednesday Spot Level ($ Millions) | Wednesday Spot Level ($ Billions) | Weekly Average ($ Millions) | Weekly Average ($ Billions) | Evidence Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Fed Assets** | Table 12 / Table 1 | $6,746,548M | $6,746.548B | $6,796,731M | $6,796.731B | docs/research/runs/fed-liquidity-2026-09-18/findings_track2.md#L20 |
| **Reserve Balances** | Table 2 / Table 13 | $2,921,536M | $2,921.536B | $3,013,794M | $3,013.794B | docs/research/runs/fed-liquidity-2026-09-18/findings_track2.md#L21 |
| **Treasury General Account (TGA)** | Table 2 / Table 13 | $991,708M | $991.708B | $877,028M | $877.028B | docs/research/runs/fed-liquidity-2026-09-18/findings_track2.md#L22 |
| **Reverse Repos: Domestic ON RRP ("Others")** | Table 2 (Line 2b) | $5,375M | $5.375B | $3,999M | $3.999B | docs/research/runs/fed-liquidity-2026-09-18/findings_track2.md#L23 |
| **Reverse Repos: Foreign Official & Int'l** | Table 2 (Line 2a) | $318,428M | $318.428B | $334,042M | $334.042B | docs/research/runs/fed-liquidity-2026-09-18/findings_track2.md#L24 |
| **Total Reverse Repos** | Table 2 / Table 13 | $323,803M | $323.803B | $338,042M | $338.042B | docs/research/runs/fed-liquidity-2026-09-18/findings_track2.md#L25 |
| **Currency in Circulation (Notes)** | Table 2 / Table 13 | $2,431,275M | $2,431.275B | $2,484,215M | $2,484.215B | docs/research/runs/fed-liquidity-2026-09-18/findings_track2.md#L26 |

### Distinguishing Domestic ON RRP from Total Reverse Repos
- Total reverse repos reported on H.4.1 stands at **$323.803 billion** (Wednesday spot).
- However, **$318.428 billion** (98.34%) represents foreign central bank dollar deposits in the Foreign Official pool.
- Actual domestic private ON RRP take-up was only **$5.375 billion** on Wednesday September 16, and **$0.576 billion** ($576 million) on Friday September 18.
- Conflating foreign official reverse repos with domestic ON RRP is a major analytical error: foreign official reverse repos represent foreign monetary authorities holding reserves at the Fed, not money market liquidity available to domestic dealers (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track2.md#L39).

---

## 3. Track 3: QT Termination, Reserve-Management Purchases (RMP), and Policy Stance

### Official Policy Dates and Changes
1. **Termination of Balance Sheet Runoff (QT)**: `December 1, 2025`.
   - Proof: [Federal Reserve Monetary Policy Report July 2026 Part 2 | URL: https://www.federalreserve.gov/monetarypolicy/2026-07-mpr-part2.htm | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track3.md#L18).
   - "The change since the Fed ended balance sheet runoff reflects changes since December 3, 2025, the date of the first Federal Reserve Statistical Release H.4.1 after the Fed ended balance sheet runoff on December 1, 2025."
2. **Initiation of Reserve-Management Purchases (RMP)**: `December 2025` / `early January 2026`.
   - Proof: [FEDS Notes: Repo Markets and the Feds Balance Sheet | URL: https://www.federalreserve.gov/econres/notes/feds-notes/repo-markets-and-the-feds-balance-sheet-implications-for-monetary-policy-implementation-20260826.html | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track3.md#L21).
   - "In December 2025, the Federal Open Market Committee (FOMC) announced the start of reserve management purchases of Treasury bills to maintain a supply of ample reserves."
3. **Quantified Changes Since Runoff Ended (Dec 1, 2025 to July 1, 2026)**:
   - Total Fed Assets: **+$189 billion** ($6,536B to $6,725B).
   - Bank Reserve Balances: **+$199 billion** ($2,878B to $3,077B).
   - Treasury Securities Held Outright: **+$303 billion** ($4,189B to $4,492B).
   - Agency MBS: **-$105 billion** ($2,056B to $1,951B).
   - Domestic ON RRP: **-$2 billion** ($3B to $1B).
   - TGA: **-$101 billion** ($908B to $807B).
   - Notes in Circulation: **+$46 billion** ($2,377B to $2,423B).
   - (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track3.md#L30).

### Why RMP Is NOT Quantitative Easing (QE)
- **Zero Duration Impact**: RMP purchases are legally and operationally restricted to short-term Treasury bills (maturing under 1 year). Unlike QE, which purchases 10-year/30-year notes and agency MBS to suppress long-term yields and compress term premia, bill purchases exert zero effect on term premia or long-term borrowing costs.
- **Policy-Neutral Technical Maintenance**: QE represents an accommodative macroeconomic policy easing stance deployed at the zero lower bound. RMP is an operational balance-sheet maintenance tool designed to offset the organic expansion of non-reserve liabilities (such as currency in circulation, which grew +$46B) so that bank reserves remain within the ample range (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track3.md#L45).

---

## 4. Track 4: TGA Swings, Matched-Window Dynamics, and Orderly Funding Counterexample

### Documented TGA Surge Event: Debt-Ceiling Rebuilding (June 1, 2023 – September 27, 2023)
- Over this identical 17-week window:
  - **TGA**: Surged from **$22.888 billion** to **$667.614 billion** ([DERIVED: +$644.726 billion (+2,817%)]) (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track4.md#L18).
  - **Domestic ON RRP**: Drained from **$2,142.302 billion** to **$1,453.137 billion** ([DERIVED: -$689.165 billion (-32.17%)]) (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track4.md#L22).
  - **Bank Reserve Balances**: Remained virtually unaffected, moving from **$3,248.822 billion** to **$3,195.431 billion** ([DERIVED: -$53.391 billion (-1.64%)]) (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track4.md#L26).
  - **Repo Spreads**: TGCR traded consistently 7 to 9 bps below IORB; SOFR traded 5 to 7 bps below IORB.
  - **Mechanics**: Treasury bill issuance was absorbed almost dollar-for-dollar by MMFs shifting assets from ON RRP to bills, leaving bank reserves insulated.

### Orderly Funding Counterexample: Depleted ON RRP in 2026
- Proof: [FEDS Notes: Repo Markets and the Feds Balance Sheet | URL: https://www.federalreserve.gov/econres/notes/feds-notes/repo-markets-and-the-feds-balance-sheet-implications-for-monetary-policy-implementation-20260826.html | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track4.md#L41).
- Proof: [FEDS Notes: The Central Bank Balance-Sheet Trilemma | URL: https://www.federalreserve.gov/econres/notes/feds-notes/the-central-bank-balance-sheet-trilemma-20260114.html | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track6.md#L50).
- **Empirical Facts**:
  - Throughout early and mid-2026, domestic ON RRP was near zero ($1B–$5B, and $0.576B as of Sep 18, 2026).
  - Despite the near-total depletion of the ON RRP facility, overnight funding markets experienced zero systemic stress.
  - Footnote 9 of the August 26, 2026 FEDS Note documents: "The EFFR-IORB spread has been -1 basis point every day from December 2025 through late April 2026, while the TGCR-IORB spread has ranged over 25 basis points."
  - As of September 17, 2026, TGCR was 3.83% (-7 bps below IORB), SOFR was 3.85% (-5 bps below IORB), and EFFR was 3.88% (-2 bps below IORB).
- **Causal Qualification**: A depleted ON RRP facility does not mechanically cause repo rates to spike. Repo stability depends on whether aggregate bank reserves exceed the Lowest Comfortable Level of Reserves (LCLOR) and whether dealer intermediation capacity is intact (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track4.md#L55).

---

## 5. Track 5: Money Market Rates, Standing Repo Usage, and Epistemology

### Primary Rate Observations (Effective Date September 17, 2026)
- Proof: [New York Fed Reference Rates Data API | URL: https://markets.newyorkfed.org/api/rates/all/latest.json | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track5.md#L8).
- Proof: [Federal Reserve Interest Rates on Reserve Balances PRATES | URL: https://www.federalreserve.gov/monetarypolicy/prates/PRATES.json | Verified 2026-09-18] (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track5.md#L11).

| Metric | Effective Date | Level | Spread vs. IORB | Daily Volume |
| :--- | :--- | :--- | :--- | :--- |
| **Interest on Reserve Balances (IORB)** | 2026-09-17 | **3.90%** | Reference Floor | N/A |
| **Tri-party General Collateral Rate (TGCR)** | 2026-09-17 | **3.83%** | **-7 bps** | $1,208 billion |
| **Broad General Collateral Rate (BGCR)** | 2026-09-17 | **3.83%** | **-7 bps** | $1,237 billion |
| **Secured Overnight Financing Rate (SOFR)** | 2026-09-17 | **3.85%** | **-5 bps** | $2,992 billion |
| **Effective Federal Funds Rate (EFFR)** | 2026-09-17 | **3.88%** | **-2 bps** | $100 billion |
| **Standing Repo Facility (SRF) Usage** | 2026-09-16 | **$0.254B** | Administered Cap | $254M (Others) |

### Persistence vs. Calendar Distortions
- **Calendar Event Frictions**: Mid-month corporate tax dates (e.g. September 15) and Treasury settlement dates temporarily drain bank deposits into the TGA and cause transient 24-to-48-hour firming in repo rates.
- **Defensible Test of Persistence**: Structural reserve scarcity is only established if repo rates (TGCR, SOFR) trade sustainably *above* IORB across multiple consecutive non-event maintenance periods (14+ business days), accompanied by persistent tapping of the Standing Repo Facility. A single-day firming around September 15–16 is calendar settlement noise, not reserve scarcity (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track5.md#L35).
- **Epistemological Scope**: Money market rates reflect secured funding conditions and primary dealer balance-sheet capacity; they do NOT measure broad commercial bank lending, non-financial corporate credit, household cash, or equity market valuation direction (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track5.md#L50).

---

## 6. Track 6: Accounting Deconstruction of the "Net Liquidity" Proxy

### Balance Sheet Accounting Identity
The retail formula:
$$\text{"Net Liquidity"} = \text{Fed Assets} - \text{TGA} - \text{Domestic ON RRP}$$
is fundamentally flawed.

From the Federal Reserve balance sheet identity (H.4.1 Table 12 & 13):
$$\text{Total Assets} = \text{Reserves} + \text{Currency} + \text{TGA} + \text{Foreign RRP} + \text{Domestic ON RRP} + \text{Other Deposits} + \text{Net Capital \& Other Liabilities}$$

Rearranging for the retail proxy:
$$\text{Total Assets} - \text{TGA} - \text{Domestic ON RRP} = \text{Reserves} + \left[ \text{Currency} + \text{Foreign RRP} + \text{Other Deposits} + \text{Net Capital \& Other Liabilities} \right]$$

### Exact Numerical Discrepancy as of September 16, 2026 (in $ Billions)
- Total Assets: `$6,746.548B`
- Less TGA: `-$991.708B`
- Less Domestic ON RRP ("Others"): `-$5.375B`
- [DERIVED: Retail Proxy Result = $6,746.548B - $991.708B - $5.375B = $5,749.465B] (~$5.75 trillion).
- Actual Bank Reserve Balances: **`$2,921.536B`** (~$2.92 trillion).
- [DERIVED: Discrepancy = $5,749.465B - $2,921.536B = +$2,827.929B] (+$2.828 trillion overstatement).
- (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track6.md#L20).

### Destination of the $2.828 Trillion Error
The retail proxy overstates bank reserves by 96.8% because it erroneously counts non-bank, non-investable liabilities:
1. **Currency in Circulation**: `$2,431.275B` (Paper dollar bills circulating in wallets and foreign cash reserves).
2. **Foreign Official Reverse Repos**: `$318.428B` (Sovereign central bank reserves).
3. **Other Deposits**: `$252.943B` (GSEs, clearinghouses, foreign accounts).
4. **Net Other Liabilities & Capital**: `-$175.032B`.

### Why Reserves Are Not Spendable Market Cash
- Bank reserves are closed-loop liabilities that can only be held by depository institutions at the Fed. They cannot be withdrawn into retail or institutional investment accounts to buy stocks.
- When equities are traded, commercial bank deposits transfer between private market participants; central bank reserves merely shift between commercial bank master accounts.
- When ON RRP drained by $2.55 trillion between 2022 and 2026, MMFs reallocated into Treasury bills and private repo with primary dealers; zero dollars flowed into equities.
- Naive claims that changes in the Fed balance sheet mechanically dictate equity prices are contradicted by empirical reality: during 2022–2024, ON RRP drained by over $2.1 trillion and Fed assets fell by $1.5 trillion, while the S&P 500 gained over 50% to reach record highs (evidence: docs/research/runs/fed-liquidity-2026-09-18/findings_track6.md#L60).

---

## NOT FOUND WHERE I LOOKED
- Proprietary commercial terminals (Bloomberg Professional terminal, Haver Analytics, Macrobond): not accessed; all findings are derived from public, official Federal Reserve, New York Fed, and St. Louis Fed primary records.
- SOMA agency MBS active sales: searched the July 2026 Monetary Policy Report and recent FOMC policy statements; confirmed that the Fed has maintained passive runoff and bill reinvestment rather than initiating outright sales of agency mortgage-backed securities.
- Empirical support for mechanical "net liquidity predicts equity crashes": searched Federal Reserve staff reports, Liberty Street Economics, and FEDS Notes; no evidence exists supporting the retail claim that the `Assets - TGA - ON RRP` accounting residual mechanically causes stock market downturns.
