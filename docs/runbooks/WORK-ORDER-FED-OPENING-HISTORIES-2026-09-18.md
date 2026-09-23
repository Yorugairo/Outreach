# Fed opening: historical observations, not interpolated endpoints

Repository: C:/Users/Snipe/Downloads/Outreach Program

Question: which official weekly observations faithfully reproduce the Federal Reserve June 2025 Monetary Policy Report Table A comparison for total assets and reserve balances, 2022-06-01 to 2025-06-11? We need the full actual history to replace an endpoint-only chart. Choose your best primary-source fetch/research skills and name them. No design or script rewriting.

Existing evidence: content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure/evidence/sources/mpr_2025_06.html and evidence/objects/fed-assets-reserves-change.series.json under that episode. Table A reports -2238 and +72 USD billions. These are retained endpoint deltas, NOT a time series. docs/content-video-engine/39-EVIDENCE-CHART-SYSTEM.md sections 6-8 require actual data, comparable units and dated sources. Do not repeat the existing ON RRP fetch.

Write ONLY docs/research/runs/fed-opening-histories-2026-09-18/. Fetch and archive verbatim official Fed/FRED observations and metadata for total assets and reserve balances, inclusive of both dates. WALCL is a discovery hint; verify the correct Wednesday-level reserves counterpart, NOT a weekly-average series silently paired with Wednesday assets. Confirm definitions, frequency, observation convention, units, and revisions. If the relevant series is WRESBAL or WRESBAL-like, verify rather than assume its basis.

Save raw response bytes (never a model-authored CSV), URLs, retrieval times, HTTP status, bytes, SHA-256, and metadata in MANIFEST.json using docs/runbooks/BRIDGE-SHAPES.md fetch entries schema. Preserve failed retrievals. Max two retrieval alternatives per missing source. No installs, logins, paid APIs, credentials, or browser/Flow interaction. This research task must not touch an active Flow composer.

Checkpoint manifest after each source. FETCH-NOTES.md must report exact first/last observations, units, sample count, gaps, and whether unrounded historical differences reconcile with the published rounded Table A deltas. If revisions or series basis prevent reconciliation, state the discrepancy; never adjust data to force a match. No interpolated observations, fabricated endpoints, causal assertions, or replacement of prior evidence.

Return reply.md with the five bridge heads, <=250 words. Run python content/video_engine/scripts/bridge_check.py --shape fetch --reply docs/research/runs/fed-opening-histories-2026-09-18/reply.md and independently verify every entry hash/byte count. Research remains quarantined pending parent intake. Return exact paths and any unresolved dependency.
