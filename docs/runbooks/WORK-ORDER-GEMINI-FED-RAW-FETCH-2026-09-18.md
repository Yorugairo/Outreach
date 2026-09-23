# Fed liquidity raw primary fetch — T1 follow-up

Repository: C:/Users/Snipe/Downloads/Outreach Program

Question: what do the retained primary observations establish for ON RRP history and overnight funding spreads through 2026-09-18? This is a new bounded fetch, not a rerun or rewrite of the completed research order. Choose your best research/fetch skills and name them. No design, narration, threshold invention, or causal interpretation.

Read episode `RESEARCH-INTAKE-REVIEW.md` and `docs/research/runs/fed-liquidity-2026-09-18/findings_track5.md`. Existing docs_find full-stage hits are production geometry, not financial data; the previous financial archive is the relevant existing evidence. Its exact rates lack archived responses; its claimed 14-business-day rule is unsupported and must not be rescued with invention.

Write ONLY `docs/research/runs/fed-liquidity-raw-fetch-2026-09-18/`. Preserve all earlier research files unchanged. Save verbatim primary responses, response metadata/status, exact request URL, retrieval timestamp, bytes and SHA-256 in MANIFEST.json using the `entries` schema of docs/runbooks/BRIDGE-SHAPES.md. Never substitute a helper script or model-produced CSV for the response bytes.

Fetch these primary sources:

1. FRED RRPONTSYD full historical CSV through 2026-09-18 using its public series download; archive metadata proving unit (billions USD), frequency and meaning. Compare latest date and 2022-12-30 peak with the prior archive. Do not include observations after the cutoff in any derived view.
2. NY Fed `https://markets.newyorkfed.org/api/rates/all/latest.json`; also locate/document the official dated historical API for TGCR and SOFR from 2025-09-01 through 2026-09-18 and retain its raw result plus API documentation. No guessed successful endpoint claims; preserve HTTP errors as not-fetched.
3. Federal Reserve `https://www.federalreserve.gov/monetarypolicy/prates/PRATES.json`; retain historical IORB observations for the same period from official Fed/FRED sources with unit/frequency metadata. We need effective dates, not retrieval dates, to match daily spreads.
4. NY Fed standing-repo results for 2026-09-01 through 2026-09-18 from its official API, distinguish operation date, amount, domestic/foreign and unit. Use the prior query_rates.py only as a readable URL hint, not an executable source.

Batch size one source: checkpoint manifest after each fetched source. Max two documented retrieval alternatives per failed source; explicitly mark unavailable, never synthesize data. No login, paid API, credentials or installs. Budget/time is not a reason to invent completion. No broad research or unsupported 14-day/three-day calendar protocol.

Output `reply.md` with the five bridge heads, <=250 words, and `FETCH-NOTES.md` mapping files to series/coverage/units and unresolved fetches. All files remain research quarantine. Validation: independently recompute every manifest entry hash/size and run `python content/video_engine/scripts/bridge_check.py --shape fetch --reply docs/research/runs/fed-liquidity-raw-fetch-2026-09-18/reply.md`; record any format/tool limitation truthfully. Return exact absolute paths.
