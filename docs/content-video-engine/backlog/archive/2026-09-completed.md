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

## P72 T0 closing pass - 2026-09-25

Rows archived by P72 T0 (`.claude/PRPs/plans/P72-THE-BACKLOG-BURNDOWN.plan.md`), one per id, with the evidence
copied from the plan's inventory (every sha resolved with `git log -1` before the batch). `hist:N` is
[`../../BACKLOG-HISTORY-2026-09.md`](../../BACKLOG-HISTORY-2026-09.md) line N. The history file is not edited - its
banner pins the source slice's sha256 - so this row is the closure. A row with an open half is not archived here;
the P72 slice that names it carries the half.

### Batch 1 - DONE-UNCLOSED (70 rows)

| ID | Verified outcome | Evidence / follow-up |
|---|---|---|
| R26-0 | The short's viewer sees the screens. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-12 P52 T14 `45f17c2`; `hist:542`. |
| R26-1 | Field-coloured halo on direct labels. Closed by P72 T0 (DONE-UNCLOSED). | engine `LP_HALO` (`scene-evidence-engine.mjs:11722` at e43c3d8), P50 T8/T11; `hist:543`. |
| R26-3 | Euler spirals. Closed by P72 T0 (DONE-UNCLOSED). | P50 T14 BUILT; ANSWERED P52 T17 `c14caeb`; `hist:545`. |
| R26-4 | The chart on the hook (E44). Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T12 `2e6740d`; `hist:539`. |
| R26-5 | Transient cues at a cut. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T13 `d16155e`; `hist:540`. |
| R26-6 | A returning character mounts. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T13 `d16155e` (M30); `hist:541`. |
| R26-7 | The world is the stage; the clips dock. Closed by P72 T0 (DONE-UNCLOSED). | doctrine E44; CAPABILITIES "Video dock, WIRED - LIVE - ruling E44 / backlog R26-7" (`:68`); `hist:444`. |
| R26-8 | Cross-posting from one master. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T16 `b00cba7` (`publish_package.py`); `hist:443`. |
| R26-10 | The cut ledger and the page's performance. Closed by P72 T0 (DONE-UNCLOSED). | P47 T2 BUILT 2026-09-06; `hist:528`. |
| R26-12 | The idle (E49). Closed by P72 T0 (DONE-UNCLOSED). | P47 T5 BUILT; `hist:445`. |
| R26-13 | M18 per layer. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T15 `161c558`; `hist:446`. |
| R26-16 | The morph's source is a real element. Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-16 (P61 T3, P48 T5b); `hist:448`. |
| R26-17 | Build the actual engine (P51). Closed by P72 T0 (DONE-UNCLOSED). | step 0 the kit DONE; P51 T1-T5 built; gates 2/3 closed as not yet meaningful (REVIEWED 2026-09-14, R26-87); `hist:526`. |
| R26-18 | A chart's deployed life (E50). Closed by P72 T0 (DONE-UNCLOSED). | P47 T6 BUILT (`undraw`, `figure`, M21); `hist:525`. |
| R26-19 | A second chart of value. Closed by P72 T0 (DONE-UNCLOSED). | P47 T6 BUILT (the Fed-vs-yields object); `hist:524`. |
| R26-20 | Badge-stamp's two-spring landing. Closed by P72 T0 (DONE-UNCLOSED). | BUILT `1a18cc7` / `4756d9d` (E99 s87/s88); `hist:522`. |
| R26-22 | Centred placement by E50's clock. Closed by P72 T0 (DONE-UNCLOSED). | each "CLOSED 2026-09-11 - SHIPPED with P50 T<n>" in its own id cell; this row: "SHIPPED with P50 T16"; `hist:521`. |
| R26-23 | Chart-to-chart transitions. Closed by P72 T0 (DONE-UNCLOSED). | P48 T1-T8 (the verbs ship); P48 closes in T0; `hist:449`. |
| R26-24 | N-tier pages (small multiples, shared x). Closed by P72 T0 (DONE-UNCLOSED). | each "CLOSED 2026-09-11 - SHIPPED with P50 T<n>" in its own id cell; this row: "SHIPPED with P50 T9"; `hist:518`. |
| R26-25 | A `span` species: a shaded region with a label. Closed by P72 T0 (DONE-UNCLOSED). | each "CLOSED 2026-09-11 - SHIPPED with P50 T<n>" in its own id cell; this row: "SHIPPED with P50 T4"; `hist:519`. |
| R26-26 | The divergence spread. Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-07 (the `spread` species); `hist:520`. |
| R26-27 | `page_boxes` disagrees with the player's own layout on a portrait page. Closed by P72 T0 (DONE-UNCLOSED). | each "CLOSED 2026-09-11 - SHIPPED with P50 T<n>" in its own id cell; this row: "FIXED by P50 T16 for every page on file"; `hist:517`. |
| R26-28 | Brackets and spreads follow the active state. Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-10 (P48 T7); `hist:516`. |
| R26-30 | The breakthrough blend - a stop-motion burst. Closed by P72 T0 (DONE-UNCLOSED). | each "CLOSED 2026-09-11 - SHIPPED with P50 T<n>" in its own id cell; this row: "SHIPPED as `break_cadence: \"stop\"` (P50 T13)"; `hist:514`. |
| R26-32 | The studio display stage. Closed by P72 T0 (DONE-UNCLOSED). | P50 T7 built 2026-09-12 (the ART-embed world, gate 3 GRANTED); `hist:450`. |
| R26-34 | The tip-riding pill. Closed by P72 T0 (DONE-UNCLOSED). | each "CLOSED 2026-09-11 - SHIPPED with P50 T<n>" in its own id cell; this row: "SHIPPED with P50 T11"; `hist:452`. |
| R26-37 | The template's own probes answer for the FIRST ledger world. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T3 `8186f1a`; `hist:455`. |
| R26-38 | A world's `__lp` can point at the previous page after a backward seek. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T3 `8186f1a`; `hist:456`. |
| R26-39 | A recast into an overflow state paints the breaking bar TALL during its build phase. Closed by P72 T0 (DONE-UNCLOSED). | each "CLOSED 2026-09-11 - SHIPPED with P50 T<n>" in its own id cell; this row: "FIXED the same day" (`lpPaintChart` runs `lpPaintBreakthrough` for the build phase; `test_mid_build_the_breaking_bar_rises_to_the_comparator_s_level`); `hist:457`. |
| R26-40 | M26 - the printed value and the drawn height agree at every instant. Closed by P72 T0 (DONE-UNCLOSED). | each "CLOSED 2026-09-11 - SHIPPED with P50 T<n>" in its own id cell; this row: "SHIPPED as M26"; `hist:458`. |
| R26-41 | One painter registry for page species. Closed by P72 T0 (DONE-UNCLOSED). | BUILT P52 T5 `c115f81`; `hist:459`. |
| R26-42 | The tip pill's leader. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T2 `4f698cd`; `hist:460`. |
| R26-46 | The retitle's state depends on the seek PATH. Closed by P72 T0 (DONE-UNCLOSED). | "closed 2026-09-11" in each status cell; `hist:464`. |
| R26-47 | A 0.16 % drift on the fab card at its exit (59.57), warm vs cold. Closed by P72 T0 (DONE-UNCLOSED). | "closed 2026-09-11" in each status cell; `hist:465`. |
| R26-48 | The sub-pixel text class. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T4 `81ccef9`; `hist:466`. |
| R26-49 | E64: the recast re-writes or morphs, never cuts. Closed by P72 T0 (DONE-UNCLOSED). | "closed 2026-09-11" in each status cell; `hist:467`. |
| R26-50 | The page mount reads as a dip to black at 1:01. Closed by P72 T0 (DONE-UNCLOSED). | "closed 2026-09-11" in each status cell; `hist:468`. |
| R26-51 | The measured page-boxes fixture is stale against the template. Closed by P72 T0 (DONE-UNCLOSED). | "closed 2026-09-11" in each status cell; `hist:469`. |
| R26-53 | Value labels crash on a bars page. Closed by P72 T0 (DONE-UNCLOSED). | "closed 2026-09-11" in each status cell; `hist:471`. |
| R26-54 | E65: the placer's base level - the plot's empty room, the axis band, scale; never "no place". Closed by P72 T0 (DONE-UNCLOSED). | "closed 2026-09-11" in each status cell; `hist:472`. |
| R26-55 | The press card's phrase as live type. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T18 `dce2e71`; `hist:473`. |
| R26-56 | The treemap golden source stale. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED P52 T1 `5c076e0`; `hist:474`. |
| R26-58 | A thrown dock's in-flight state depends on the path. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-12; `hist:475`. |
| R26-60 | A transition that TAKES the world needs the page's `:cut`. Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-12; `hist:477`. |
| R26-76 | The melt reworked to E88. Closed by P72 T0 (DONE-UNCLOSED). | BUILT P61 T6; RULED E99 s51 / s56; `hist:494`. |
| R26-80 | The numbered agenda, beautified. Closed by P72 T0 (DONE-UNCLOSED). | BUILT P61 T8; RULED E99 s44; `hist:498`. |
| R26-82 | The verdict stack on a short. Closed by P72 T0 (DONE-UNCLOSED). | BUILT P61 T7; RULED E99 s43 / s59; `hist:500`. |
| R26-83 | Commit the 09-13 batch. Closed by P72 T0 (DONE-UNCLOSED). | DONE 2026-09-13 night (five commits named); `hist:501`. |
| R26-84 | Astra back on the engine. Closed by P72 T0 (DONE-UNCLOSED). | RULED E99 s47; CLOSED 2026-09-16 (P62); `hist:502`. |
| R26-86 | P55 the effects catalogue. Closed by P72 T0 (DONE-UNCLOSED). | HG9 CLOSED P61 T9; P55 plan status complete; `hist:504`. |
| R26-87 | Open human gates across plans (09-13). Closed by P72 T0 (DONE-UNCLOSED). | REVIEWED 2026-09-14: P52 gate 3 approved (E99 s16), P51 gates 2/3 closed as not yet meaningful; `hist:505`. |
| R26-89 | Two bridge replies. Closed by P72 T0 (DONE-UNCLOSED). | DONE 2026-09-13 night; `hist:507`. |
| R26-91 | Pre-existing reds. Closed by P72 T0 (DONE-UNCLOSED). | TRIAGED + FIXED 2026-09-14; `hist:509`. |
| R26-103 | Recipe cards. Closed by P72 T0 (DONE-UNCLOSED). | LANDED P56 T1-T5 + T9; `hist:547`. |
| R26-104 | The one-shot floor v2. Closed by P72 T0 (DONE-UNCLOSED). | LANDED P56 T6-T7; `hist:548`. |
| R26-108 | Catalogue gaps the mining found. Closed by P72 T0 (DONE-UNCLOSED). | PART LANDED P56 T8; REV 1 citation for the open half ("the long form speaks no species vocabulary"): H itself resolves it - `build-h/steel-and-paper-h.timeline.json` has 25 scenes, 23 carrying species and 14 carrying pages (counted 2026-09-25). Draft 1's DOCS-BL-01 / R26-239 citation was wrong; re-counted 2026-09-25 on lane A's working `build-h` at 311aad7: 27 scenes, 25 carrying species, 15 carrying pages (row 24 and the outro landed after the inventory's count); `hist:552`. |
| R26-109 | The Myth of Historical Normal requests. Closed by P72 T0 (DONE-UNCLOSED). | DRAFTED; REVIEWED 2026-09-14: approved (E99 s12); `hist:553`. |
| R26-117 | The melt's third ending (morph). Closed by P72 T0 (DONE-UNCLOSED). | BUILT; RULED s53 / s58; card created; `hist:561`. |
| R26-118 | The melt's ball has mass. Closed by P72 T0 (DONE-UNCLOSED). | BUILT P61 T5; RULED E99 s42 / s49; `hist:562`. |
| R26-119 | RESEARCH: the living metallic drop - Rayleigh modes, damping, the highlight, the stop-motion craft of a heavy ball. Closed by P72 T0 (DONE-UNCLOSED). | SENT and REVIEWED 2026-09-14: RELEASED; `hist:563`. |
| R26-120 | RESEARCH: the morph that handles holes and topology - implicit / SDF blends vs ring correspondence. Closed by P72 T0 (DONE-UNCLOSED). | SENT and REVIEWED 2026-09-14: RELEASED; `hist:564`. |
| R26-121 | RESEARCH: the relation layer - what 2D rigs and constraint systems get right, harvested. Closed by P72 T0 (DONE-UNCLOSED). | SENT and REVIEWED 2026-09-14: RELEASED; `hist:565`. |
| R26-122 | The 2.5D stage. Closed by P72 T0 (DONE-UNCLOSED). | BUILT P58 T1-T8; P58 plan complete; `hist:566`. |
| R26-126 | The push word. Closed by P72 T0 (DONE-UNCLOSED). | PUSHED 2026-09-14 on the operator's word; `hist:570`. |
| R26-127 | Session-local state (the bridge daemon). Closed by P72 T0 (DONE-UNCLOSED). | closed at `bf539e3` ("the daemon is started by the bridge_inbox hook when its lock is missing"); no scheduler entry. P72 T31 carries R26-336 in its place; the history's own closing row `hist:955` ("the daemon now restarts itself ... Verified: started pid 62772"); `hist:571`. |
| R26-131 | The operator's judgements after P58. Closed by P72 T0 (DONE-UNCLOSED). | reviewed item by item 2026-09-14/15; P58 complete; `hist:575`. |
| R26-133 | A plate's drift paints nothing. Closed by P72 T0 (DONE-UNCLOSED). | RULED E99 s38/s55; the `plate_idle_paints` dial (R26-228 CLOSED); long form withdrawn by s84; `hist:577`. |
| R26-134 | The evidence door. Closed by P72 T0 (DONE-UNCLOSED). | BUILT + WATCHED 2026-09-14; `hist:578`. |
| R26-156 | The alive plate as a plate-life route. Closed by P72 T0 (DONE-UNCLOSED). | `plate_option:alive` (`81210d8`, E99 s55; CAPABILITIES); `hist:600`. |
| R26-158 | The docs layers were source. Closed by P72 T0 (DONE-UNCLOSED). | closed (P63); `hist:602`. |

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
