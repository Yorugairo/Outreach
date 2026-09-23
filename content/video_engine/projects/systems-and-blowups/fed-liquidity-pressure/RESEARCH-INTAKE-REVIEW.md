# Gemini intake review — 2026-09-18

Status: **PARTIAL / QUARANTINED**, not research-complete for production.

Order packet: `1f8d2e4a0e4a3e14c8af9ea780ad350b14390ef8f880fa96c4f5da9d69a69176`. Conversation: `fcc2a092-1105-4c5f-9ca6-8eb088ef801e`. Successful send: 18:06:01 -07:00. Final observed watcher: done, 398 steps, 18:20:57 -07:00. The watcher first mistook a waiting message for completion at 18:16:26; parent rechecked instead of resending. Final remote message says background curl finished; that statement is not proof of claim accuracy.

## What landed

- `docs/research/macro/FED_LIQUIDITY_2026_09_18_RESEARCH_BLUEPRINT.md`
- `docs/research/macro/FED_LIQUIDITY_2026_09_18_INTAKE.md`
- `docs/research/runs/fed-liquidity-2026-09-18/`: six track notes, local primary sources, RRP CSV, manifest and helper scripts. Helpers were NOT executed by the parent/auditor.
- Parent independently checked all **14/14 declared artifact SHA-256 hashes**. Independent audit also checked **14/14 byte counts**. This proves custody against the submitted manifest, not that every claim has supporting data.

## Dispositions

| Item | Parent disposition | Evidence / next step |
|---|---|---|
| Downloaded sources and report custody | Accepted as retained artifacts, not blanket claim approval | MANIFEST.json artifact paths/hashes match disk. Archive is usable for claim-by-claim review. |
| RMP start date | Correct blueprint before narration use | `sources/mpr_2026_07.html:1376-1380`: purchases initiated at December 2025 meeting; early January describes continuation. Blueprint line 8's January initiation does not match it. Existing proposed narration's December wording is retained. |
| 14+ business-day threshold and three-day tax exclusion | HELD / unsupported as a primary finding | `findings_track5.md:39-43`, blueprint:126-129 give an analyst protocol without primary support. No matching threshold in the archived primary sources checked. Do not place it in the script as an established crisis test. |
| Exact Sep 17 TGCR/SOFR/IORB figures | HELD pending raw rate evidence | Track 5 cites remote APIs, but archive contains no rate JSON/CSV supporting the quoted values. `query_rates.py` is a helper, not its fetched output. Fetch dated primary responses before plotting or stating current spreads. |
| Full RRP series and derived proxy | NOT fully audited by this bounded pass | Verify CSV values/coverage against retained source response, sampling/vintage/units and calculation; matching a file hash alone cannot establish data correctness. |
| Absolute claims about no equity flows / invalid proxy / crisis inevitability | NOT accepted wholesale | These exceed this audit; any usable explanation must distinguish accounting identity, imperfect proxy and empirical causal claim. No absolute causal conclusion is adopted from the report summary. |

## Formal check

`bridge_check.py --packet <id> --reply docs/research/runs/fed-liquidity-2026-09-18/reply.md --json` found the report, 11 proof lines and the not-found block, but **FAILed** the docs-layer stage: effects-catalog coverage/staleness, including missing `labelfit` card coverage. This is separate from the substantive holds above. Do not mark the research landed/PASS merely because the report calls itself done, and do not patch unrelated catalogue code in this episode planning task.

Use the local five-head reply for format checks; the last conversational bridge reply is only a concluding sentence. Do not resend the completed order. Next source work is a fresh, bounded fetch of the missing rate responses and CSV provenance; no request to manufacture a threshold. Report wording corrections stay distinct from new evidence.

The PRP's T1 remains in review. HG1 can approve the build plan while affected production claims remain blocked. No generated asset or research output is promoted by this intake review.

## Fresh raw-source supplement

Packet `d49ea3a8c83ad5d8563b42e1ed3e9ebc8692656cb267226f34359f29c0f9c824` completed; archive `docs/research/runs/fed-liquidity-raw-fetch-2026-09-18/`. Parent and independent audit matched all 15 fetched hashes/byte counts; two failed alternatives remain recorded. Detailed receipt: `.context/fed-raw-source-audit.md`.

- Release the **raw evidence availability** hold for TGCR/SOFR/IORB, not every research interpretation. Parent independently checked 261 exact-type rows per rate and the latest September 17 join: TGCR 3.83%, SOFR 3.85%, IORB 3.90%; spreads -7bp and -5bp. No September 18 TGCR/SOFR observation exists in the response. Exclude IORB's future-dated September 19-21 rows.
- Use fresh FRED RRP CSV, not original `rrp_history.csv`. Parent independently verified zero duplicate dates, 3,329 numeric observations through cutoff, peak 2,553.716 billion on December 30, 2022, and latest 0.576 billion on September 18. Episode custody copies and bindings exist in `claims.v1.json`.
- Audit reports 26 Repo operations totaling $430 million accepted across the window, **not outstanding**. It corrects the fetch notes: offering rates rise to 4.00% on September 17-18, not 3.75% throughout. Programmatic extraction/validation is still pending before chart use.
- The fresh formal packet check remains **FAIL** because the parent omitted dispatch `--fetch-dir` metadata. Do not edit the frozen packet or resend a completed order to conceal this error. Local source validation is separately reported, not a substitute formal PASS.
- No newly supported 14-day threshold, three-day exclusion, automatic crisis claim or deterministic borrower transmission. Those interpretation holds remain.
