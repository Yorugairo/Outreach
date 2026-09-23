# Research work order: Fed liquidity episode numbers

Repo: C:/Users/Snipe/Downloads/Outreach Program
Use your finance research skills and name them. QUESTION ONLY: which dated primary-source observations support, qualify, or contradict the proposed explanation of ON RRP depletion, bank reserves, Treasury cash swings and repo funding pressure as of 2026-09-18?

Context: Money Physics playlist episode, working title The Hidden Fed Metric Breaking the Economy. The broader playlist supplies wider macro context. Do not write a script or design. The parent owns the episode's argument. Output is research in quarantine.

Existing evidence: docs_find.py "net liquidity" found only the Fed building, liquidity printing icon and drain-pump assets; no dedicated research source. The prior session surfaced the following URLs; independently verify every date and observation, including whether these pages are accessible:
- https://www.newyorkfed.org/medialibrary/media/markets/omo/omo2022-pdf.pdf (year-end 2022 ON RRP daily peak versus December average)
- https://fred.stlouisfed.org/series/RRPONTSYD
- https://www.federalreserve.gov/monetarypolicy/2026-07-mpr-part2.htm (end of runoff, reserve-management purchases, reserves)
- https://www.federalreserve.gov/econres/notes/feds-notes/repo-markets-and-the-feds-balance-sheet-implications-for-monetary-policy-implementation-20260826.html

Answer in six rows/tracks, checkpoint to disk after each:
1. Exact ON RRP peak date/value, December 2022 monthly mean, and latest published observation on/before Sep 18 2026. Explain daily/year-end distortion. CSV: original units and observation dates.
2. Latest matched-date Fed assets, reserve balances, TGA and ON RRP; cash/frequency conventions. Distinguish domestic ON RRP from total H.4.1 reverse repos including foreign accounts. Do not combine daily values and weekly averages unlabelled.
3. Verify current QT/RMP policy and dates; quantify balance sheet/reserves changes since runoff ended if supported. Reserve-management purchases are not automatically QE.
4. One documented event during which TGA moved materially, alongside reserve/ON RRP changes and repo spreads. Find one counterexample with low ON RRP but orderly funding. Use identical date windows; no causal claim from coincidence.
5. Latest TGCR, SOFR, IORB and standing-repo usage; a defensible comparison window for persistence versus temporary tax/quarter-end stress. Do not invent a predictive threshold or backtest. Explain what an indicator can and cannot establish.
6. Why assets minus TGA minus domestic ON RRP is NOT spendable market cash or exact reserves; destination of MMF reallocation, collateral/intermediation, and evidence for any link to borrowing costs. No assertion that a proxy mechanically predicts stocks/crashes.

Allowed writes ONLY:
- docs/research/macro/FED_LIQUIDITY_2026_09_18_RESEARCH_BLUEPRINT.md
- docs/research/macro/FED_LIQUIDITY_2026_09_18_INTAKE.md
- docs/research/runs/fed-liquidity-2026-09-18/ (raw sources, CSVs, SHA-256 manifest, reply)
Do not edit doctrine, rulings, plans, skills, code, or existing episode files. Do not commit.

Read GEMINI.md research intake; docs/runbooks/BRIDGE-PACKET.md and BRIDGE-SHAPES.md. Every figure: exact value + units + as-of observation + primary URL + verified date + local evidence path/anchor. Derived values explicitly [DERIVED: inputs, formula]. Fetch raw primary sources locally; manifest url/path/sha256/fetched_at. Unavailable data is [UNVERIFIED] with reason, not substituted from memory. Include a NOT FOUND WHERE I LOOKED block and intake held/new/contradicts/unsourced table. Keep unknown rows; do not fabricate completion.

Validation: refresh retrieval via docs_find.py "Fed liquidity"; run audit_research_provenance.py (report pre-existing failures separately) and bridge_check.py --shape report-landed --reply <your reply file>. Final reply follows five-head bridge grammar and cites artifacts. Continue until all six rows are complete or explicitly UNVERIFIED. No paid data purchases.
