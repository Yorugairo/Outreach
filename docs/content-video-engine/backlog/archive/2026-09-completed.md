# Completed video-engine backlog — September 2026

Source board: [`../../BACKLOG.md`](../../BACKLOG.md). Archived 2026-09-23.
This index contains rows removed from the canonical active queue on direct
completion, measurement, retirement, or operator-review evidence. Detailed
rationale remains in the source board's historical ledger. Follow-ups are
split to active IDs before the completed portion is archived.

| ID | Verified outcome | Evidence / follow-up |
|---|---|---|
| R26-63 | Research triage withdrawal and retirement recorded. | P57 T5; withdrawal and registry retirement recorded in the source row. |
| R26-64 | Dead `IMPACT_S` removed; constants’ unsupported derivation retired. | P57 T5; `dd859b6`, E99 s30. Remaining motion-sharpness question is tracked under active R26-85. |
| R26-67 | Ring flag placement accepted. | P57 HG1; E99 s19 operator acceptance. |
| R26-68 | Span shading reviewed and ruled. | P57 review; E99 s46, `span_alpha` default decision. |
| R26-69 | Script-aligned authoring clock closed. | P57 T1; `3642f2a`; alignment test evidence in the source row. |
| R26-70 | Whole-chart compare/remake behavior accepted. | P57 T11/T12 and P61 T2/T2b; E99 s50 approval, both directions recorded. |
| R26-71 | Figure/line collision fixed and accepted. | P57 T10: 20 measured collisions to 0; 47 goldens unchanged; E99 s19. |
| R26-74 | Embed surface built and verified. | P57 T1; `3a6a645` + `364ecb9`; 102 golden frames byte-identical. |
| R26-75 | Slide transition built and reviewed. | P57 T13; `slide-mid`/`slide-landed`; E99 s8 operator review. |
| R26-77 | Caption-life variants built and reviewed; selected blend recorded. | P57 T14; E99 s6. The compiler-default follow-up remains active under R26-123. |
| R26-78 | Eased and clothoid race-path variants built. | P57 T15; golden A/B pair and period-clock evidence. The default question remains active under R26-124. |
| R26-79 | Rank-swap collision fix built and measured. | P57 T16; M28 changed FAIL to PASS at the crossing; `race-swap` proof; E99 s8 review. |
| R26-90 | Required CAPABILITIES rows written. | P57 T3; eight rows recorded in `CAPABILITIES.md`. |
| R26-92 | Docs-layer/review-server housekeeping and regeneration rule completed. | P57 T4; launch configs 13→5, manifest 79,178/80,000 B, ten layers in sync. |
| R26-93 | `idle=live` regression fixed. | P57 T1; `3a6a645`; idle tests and 102 golden files unchanged. |
| R26-94 | `cutout` dock option fixed. | P57 T1; `3a6a645`; 13 focused tests and 102 golden files unchanged. |
| R26-95 | `species:trace` promoted to module. | P57 T18; `trace-hop`; 55 goldens identical; sync/test evidence in P57. |
| R26-96 | `species:spotlight` promoted to module. | P57 T19; spotlight and idle proofs; 55 goldens identical; sync/test evidence in P57. |
| R26-97 | `species:callout` promoted to module. | P57 T17; 55 goldens identical; sync/test evidence in P57. |
| R26-98 | Page `figure` promoted to module. | P57 T20; `page-figure`; 60 goldens identical; sync/test evidence in P57. |
| R26-99 | Dock `record` promoted to module. | P57 T21; `record-typewriter`; 62 goldens identical; sync/test evidence in P57. |
| R26-100 | `exit:dip` promoted to transitions module. | P57 T23; 67 goldens identical; Japan motion gate unchanged; sync/test evidence in P57. |
| R26-101 | `page_enter:spiral` and retract promoted. | P57 T22; 62 goldens identical; equivalence run reported zero differences; sync/test evidence in P57. |
| R26-107 | Research-ledger intake and parked-row triggers built. | P57 plan/T2; 16 tests and the completed intake results recorded in the source row. R26-110 tracks the initial six-run triage. |
| R26-110 | Six unlanded research runs triaged; ledger has no orphan. | P57 T2; `build_research_ledger.py`: 20 runs, 0 orphan, 4 referenced, 16 landed. |
| R26-112 | Still-image motion-graphics research retired. | E32 and P57 T2 retirement recorded in the source row. |
| R26-113 | Weight/density/mass research landed in the stop-action dials. | P57 T2; source module cites the research blueprint. |
| R26-114 | Retention-zone opening question resolved by correction. | E99 s10 records that opening on a full chart was never refused. |
| R26-125 | P57 HG1 review event recorded. | E99 s19 accepted R26-67/71; its unresolved hand-off observation is split into active R26-66. |
| R26-262 | GDP-share page now carries year ticks and a `% of GDP` label; the recast page was parent-read. | P69 T17; `ev-equip-ipp-gdp-v2` preserves v1 data and adds the labels; `ledger_page --check --variant line` and door exit passed. No operator gate is recorded on this child. |
| DOCS-BL-01 | The over-length `dock_kind:prop` description was shortened without changing its mechanism; all eight missing source-token cards were recorded. | 2026-09-23: `build_effects_catalog.py --check`, `effects_catalog_check.py` (0 failures), and `build_docs_layers.py --write` (12 layers in sync). Source cards: `dock_kind.json`, `page_enter.json`, `plate_option.json`, `kinetics.json`. |
| R26-239 | Compiler/kinetics token coverage debt closed without inventing unproved beat recipes. | Eight source cards now cover `room`, `domain`, `build`, `labelfit`, `readability`, `bar_style`, `surface`, and `page_surface`; `effects_catalog_check.py` reports 0 failures and the two strict xfails were removed (2026-09-23). |

## Remaining close-marked legacy rows

This is a census for parent review, not a second archive and not a completion
claim. The method is intentionally mechanical: among the 274 bold R26 detail
row headers, identify trailing status cell(s) containing an explicit
completion-like token (`CLOSED`, `DONE`, `BUILT`, `FIXED`, `RETIRED`,
`APPROVED`, `ACCEPTED`, `SHIPPED`, `PROMOTED`, `RESOLVED`, `LANDED`,
`COMPLETE`, or `WITHDRAWN`). It found 102 rows. R26-63/64/67/68/69/70/71/74/
75/77/78/79/90/92/93/94/95-101/110/112-114/125/262 account for 29 of the 30
archive IDs at the first pass; R26-107 was also archived on direct evidence although its trailing
cell does not match this token list. R26-239 was subsequently closed on direct
catalogue evidence above. R26-123 remains active because its
compiler-default follow-up is unresolved. These 71 other close-marked rows
remain unreconciled; a token alone does not prove closure:

R26-13, R26-32, R26-37, R26-38, R26-41, R26-42, R26-46, R26-47, R26-48,
R26-49, R26-50, R26-51, R26-53, R26-54, R26-55, R26-56, R26-58, R26-59,
R26-60, R26-76, R26-80, R26-82, R26-84, R26-86, R26-87, R26-105, R26-109,
R26-117, R26-118, R26-119, R26-120, R26-121, R26-122, R26-132, R26-133,
R26-134, R26-135, R26-158, R26-159, R26-161, R26-168, R26-172, R26-175,
R26-176, R26-177, R26-179, R26-180, R26-181, R26-191, R26-201, R26-218,
R26-219, R26-220, R26-221, R26-222, R26-223, R26-224, R26-225, R26-226,
R26-228, R26-230, R26-231, R26-232, R26-233, R26-234, R26-235, R26-236,
R26-241, R26-245, R26-246, R26-247.

The source also mentions R26-248 without a matching detail-row header. It stays
an unresolved source anomaly; this pass does not synthesize a task from it.
