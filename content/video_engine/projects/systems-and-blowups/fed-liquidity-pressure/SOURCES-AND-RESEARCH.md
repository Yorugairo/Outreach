# Sources, research gaps and proposal status

Checked 2026-09-18. These are source notes, not narration. Gemini's files have returned; 14/14 manifest artifact hashes were independently verified, but claim intake is PARTIAL / QUARANTINED. See RESEARCH-INTAKE-REVIEW.md for the unsupported threshold, missing rate-response evidence and chronology correction. Final CSV/claim bindings have NOT been completed. Do not use this document as a release receipt.

## Claim map

| ID / scenes | Claim and primary source | Production constraint |
|---|---|---|
| C1 · S01/S09 | ON RRP reached a year-end 2022 daily peak of approximately $2.55 trillion. [New York Fed, 2022 Open Market Operations report](https://www.newyorkfed.org/medialibrary/media/markets/omo/omo2022-pdf.pdf). | Peak, not average. Narration rounds to two and a half trillion. Acquire daily history, exact peak date and local report excerpt before plotting. |
| C2 · S01/S09 | RRPONTSYD observation 2026-09-18: 0.576, units billions of dollars, equivalent to $576 million. [FRED, underlying New York Fed series](https://fred.stlouisfed.org/series/RRPONTSYD). | Not literal zero. Refresh before production; annotate observation date, units and source. Do not interpolate a history from endpoints. |
| C3 · S01/S10/S12 | June 11, 2025 versus June 1, 2022: Fed assets change −$2,238bn; reserve balances +$72bn; other reverse repos −$1,760bn; TGA −$504bn. [Federal Reserve, June 2025 Monetary Policy Report, part 2](https://www.federalreserve.gov/monetarypolicy/2025-06-mpr-part2.htm). | These are changes over the SAME window, not four current balances. Selected rows do not exhaust the liability reconciliation. Keep foreign official reverse repos distinct from the domestic ON RRP story. |
| C4 · S15/S16/S20 | Policy timeline, July 1 snapshot and calm-market counterexample. [Federal Reserve, July 2026 Monetary Policy Report, part 2](https://www.federalreserve.gov/monetarypolicy/2026-07-mpr-part2.htm). | July observations cannot be labelled September current. Source the three passages separately; do not equate reserve-management purchases with a new QE claim. |
| C5 · S14/S17/S19 | Treasury supply, dealer funding, money-fund alternatives and TGCR–IORB analysis. [Federal Reserve staff, Repo Markets and the Fed's Balance Sheet, August 26, 2026](https://www.federalreserve.gov/econres/notes/feds-notes/repo-markets-and-the-feds-balance-sheet-implications-for-monetary-policy-implementation-20260826.html). | Staff analysis, not an official crisis prediction. It does not establish a universal stress threshold or deterministic transmission to business lending. |
| C6 · S05/S06/S07 | Fed balance-sheet accounting and movement between Treasury cash and reserves. [Federal Reserve staff, The Central Bank Balance Sheet Trilemma](https://www.federalreserve.gov/econres/notes/feds-notes/the-central-bank-balance-sheet-trilemma-20260114.html). | Holding other balances fixed is essential to the illustrated debit/credit. Archive source and bind the final transaction diagram during intake. |
| C7 · S03/S11 | Analyst proxy: Fed assets − TGA − domestic ON RRP. The $100bn example is explicitly hypothetical accounting, not a historical observation. | Derived example: Δproxy = −100 − 0 − (−100) = 0. With other liabilities fixed, the matching asset/ON RRP decline leaves reserve balances unchanged. The proxy is neither an official Fed series nor money available to buy stocks. |
| C8 · S02/S21/S24 | Workshop owner, refinancing decision and expansion consequences. | Illustrative conditional transmission; no real borrower or measured loan increase claimed. Next episode topic is proposed, not a production commitment already fulfilled. |

## Additional numbers requested from Gemini

1. Matched-date Fed assets, reserves, TGA and domestic ON RRP; exact vintage/units/frequencies.
2. ON RRP peak and current daily data with full CSV, not endpoint reconstruction.
3. Current policy chronology: runoff, reserve-management purchases, relevant amounts and dates.
4. One documented Treasury cash/settlement episode AND one calm counterexample, with daily funding observations.
5. TGCR, SOFR, IORB and standing-repo use, plus a defensible observation window/threshold if evidence supports one. If no defensible threshold exists, report that; do not invent a trading rule.
6. Limits of the proxy and evidence for, or against, the proposed transmission chain.

D6 funding chart construction remains OPEN; its raw data and exact-date extraction are now verified (execution update below). No calibrated crisis threshold is supported. S22 now uses zero only as an arithmetic funding-rate comparison and requires separate borrower evidence. Script mechanics, recording readiness and rendered correctness remain separate gates.

## Work order / dispatch evidence

Order: `docs/runbooks/WORK-ORDER-GEMINI-FED-LIQUIDITY-2026-09-18.md`.

Dry run created packet `1f8d2e4a0e4a3e14c8af9ea780ad350b14390ef8f880fa96c4f5da9d69a69176` under `docs/research/runs/bridge/queue/`.

The first real send failed before dispatch: `cannot send: ANTIGRAVITY_LS_ADDRESS, ANTIGRAVITY_CSRF_TOKEN not found where I looked (is Antigravity running?)`. After the user started Antigravity, the second real attempt succeeded at `2026-09-18T18:06:01-07:00`. Conversation: `fcc2a092-1105-4c5f-9ca6-8eb088ef801e`. Packet is now under `docs/research/runs/bridge/sent/1f8d2e4a0e4a3e14c8af9ea780ad350b14390ef8f880fa96c4f5da9d69a69176/`. First watcher snapshot: `working`, 37 steps, 50 seconds after send. The order is FROZEN; do not resend or edit it while running.

The run subsequently ended (398 steps at 18:20:57 -07:00). Artifacts exist but are not blanket verified; see RESEARCH-INTAKE-REVIEW.md. This command is the recorded collection route, not an instruction to keep polling or resend:

```powershell
python content/video_engine/scripts/bridge_watch.py --lane gemini --id fcc2a092-1105-4c5f-9ca6-8eb088ef801e --packet 1f8d2e4a0e4a3e14c8af9ea780ad350b14390ef8f880fa96c4f5da9d69a69176 --once --json
```

Review landed files against primary evidence, not the agent summary. Asset approval remains separate from source verification. Nothing in the work order authorizes production rendering or publishes the episode.

## Recall and review

- Recall: `docs_find.py "net liquidity"` found relevant existing props/icons but no dedicated research blueprint for this episode. `docs_find.py "Blender"` returned no hits; installation alone establishes no repository integration.
- Recall: `docs/portable/OPERATOR-RULINGS.md`, E99 s82–s84, governs full-stage evidence, motion and current recipe decisions. Older catalogue labels do not override these rulings.
- Recall: `docs/WORKTREE-REGISTER.md`, Hand-off 2026-09-18, identifies full-stage fixture, bands, compiler fixes and outstanding HG3 design choices. Those remain prerequisites for building, not blockers to this authored proposal.
- Recall: effect-card reads of `read-park-build-write`, `badge-ladder`, `chart_to:extend` and `page_enter:mount` informed the map; new combinations are expressly unproved.
- Read-only inventory agent verified manifest/hash matches for reusable props and identified approved worlds. The authored four-world treatment budgets new masters where exact composition matters.
- Read-only editorial review moved the contradiction into the opening, removed a deterministic adjustment claim, and consolidated repeated caveats. The numerical tell remains an explicit evidence gap.

## Execution update — source verification

Fresh run `docs/research/runs/fed-liquidity-raw-fetch-2026-09-18/`:15 fetched artifacts hash/byte verified; two failed alternatives retained. Parent-reviewed extractor and12 tests pass, including strict manifests, URL date bounds and relocation determinism. `evidence/derived/` contains1176 RRP observations,261 exact-date funding joins and26 Repo operations. `claims.v1.json` now binds all planned-script claim IDs to retained sources or explicit illustrations.

September17 latest funding: TGCR3.83%,SOFR3.85%,IORB3.90%, spreads−7bp/−5bp. No September18 daily funding observation fabricated. Repo cumulative accepted take-up is not outstanding balance; Repo and Reverse Repo remain separate. The unsupported14-day threshold/three-day exclusion remain excluded. Formal bridge-check failures are retained in the intake receipt and not rewritten as PASS.

Script mechanical gates PASS; semantic amendments resolve catalyst/debate/ring concerns, with frame judgments and actual blind viewer still outstanding. Seven-layer Flow claim dispatched under zero-paid-credit and quarantine constraints; no successful media generation, narration or Blender render asserted here. Scene correspondence and planning counts are checked separately from production gates.
