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

### Batch 2 - DONE-UNCLOSED (53 rows)

| ID | Verified outcome | Evidence / follow-up |
|---|---|---|
| R26-159 | Gates registry 15 s. Closed by P72 T0 (DONE-UNCLOSED). | `31ebf09` (P64 T2: `--check` 14.7 s -> 0.8 s, byte-identical); the row itself says CLOSED; `hist:603`. |
| R26-172 | `chart_to park` shrinks the pills. Closed by P72 T0 (DONE-UNCLOSED). | WITHDRAWN 2026-09-17; `hist:616`. |
| R26-177 | Recall the motion doctrine before authoring. Closed by P72 T0 (DONE-UNCLOSED). | both halves DONE in the row: M45 (`bf6f737`, P66 T5 + P65 T7) and the verified receipt (`4b0343d`, P67 T6); `hist:621`. |
| R26-179 | Caption pages never read the punctuation. Closed by P72 T0 (DONE-UNCLOSED). | fixed (one-shot #3); `hist:623`. |
| R26-184 | A gate guides, never dismisses (s69). Closed by P72 T0 (DONE-UNCLOSED). | the lab diagnoses (`lab_build.py:54` "buildable with a companion"); `HELD_BUILT_S = 4.0` (gate `:245`, E99 s69); reproof-r2 carded and ruled (s84); `hist:627`. |
| R26-190 | The compare melt never painted on a bars page. Closed by P72 T0 (DONE-UNCLOSED). | engine `:14571` "P69 T6 / R26-190 (E99 s74) - A FIGURE ON A BARS PAGE"; kept by s77 (2); `hist:633`. |
| R26-191 | A collision is fixed, never named. Closed by P72 T0 (DONE-UNCLOSED). | BUILT (a) `9e30f2a`, (b) the thinning; `hist:634`. |
| R26-201 | A punch on a 9:16 page. Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18 (with R26-220); `hist:644`. |
| R26-205 | The 16:9 caption strip. Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18; `hist:648`. |
| R26-210 | No 16:9 outro card. Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18 (`OutroLandscape`); `hist:653`. |
| R26-211 | `idle.mjs`'s comment contradicts s64/s65 (G-07). Closed by P72 T0 (DONE-UNCLOSED). | `kinetics/idle.mjs` at e43c3d8 reads "20 px is the named long-form setting (E99 s64 / s65 amended s55's 30) ... PLATE_DRIFT_LONG 20"; the string first appears in `3a9d82e` (`git log -S`); `hist:654`. |
| R26-213 | Ep1's five SVGs have no port into the kit (G-09). Closed by P72 T0 (DONE-UNCLOSED). | H re-authored the charts as ledger pages from committed objects (`build_episode_h.py` `page_open` :1029, `page_rail`, `page_snap`, `page_yard` .. `page_arith` :1180); "owed: nothing in the engine"; `hist:656`. |
| R26-218 | A MARK CANNOT NAME ITS SERIES ON A MULTI-LINE PAGE (2026-09-18, Steel and Paper H unit). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18 each (P68 T5b evidence); this row: "BUILT 2026-09-18"; `hist:661`. |
| R26-220 | `focus_zoom` IS A FIXED 1.32 AND CROPS A 16:9 PAGE'S TITLE (2026-09-18). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18 each (P68 T5b evidence); this row: "BUILT 2026-09-18 (with R26-201 - one door)"; `hist:663`. |
| R26-221 | A CARD CANNOT TAKE AN AUTHORED SLOT ON A PICTURE PLATE (2026-09-18). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18 each (P68 T5b evidence); this row: "BUILT 2026-09-18"; `hist:664`. |
| R26-222 | M28 READS A Y-ONLY RESCALE'S TICK HAND-OVER AS A COLLISION WITH ITSELF (2026-09-18, H unit). Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-22 each (P69 T7 / `0d15009` / P69 T1); this row: "CLOSED 2026-09-22 (P69 T7)"; `hist:665`. |
| R26-223 | A PAGE CANNOT BE BORN WITH A DOMAIN (2026-09-18). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18 each (P68 T5b evidence); this row: "BUILT 2026-09-18"; `hist:666`. |
| R26-224 | FIFTEEN TESTS FAIL ON THE COMMITTED TREE BEFORE ANY CHANGE (2026-09-18, measured by the R26-218/219 lane). Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-22 each (P69 T7 / `0d15009` / P69 T1); this row: "CLOSED 2026-09-22"; `hist:667`. |
| R26-225 | A GATE TEST REWRITES `build-f/GATES-MOTION.md` DURING A FULL SUITE RUN (2026-09-18). Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-22 each (P69 T7 / `0d15009` / P69 T1); this row: "CLOSED 2026-09-22"; `hist:668`. |
| R26-226 | A MULTI-LINE PAGE BUILDS LINE BY LINE (E99 s82, 2026-09-18). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18 each (P68 T5b evidence); this row: "BUILT 2026-09-18"; `hist:669`. |
| R26-228 | LIFE IS SEEN, NOT PASSED - the 16:9 page renders no tip spark, no glow, no pulse, no label breath, and the plate's drift + Ken Burns read as still (E99 s82, the operator on copy d). Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-22 each (P69 T7 / `0d15009` / P69 T1); this row: "CLOSED 2026-09-22"; `hist:671`. |
| R26-230 | THE FULL-STAGE 16:9 PAGE KEEPS ITS TOP AND BOTTOM BANDS FOR CAPTIONS AND THE 9:16 RE-STAGE (E99 s82). Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-22 each (P69 T7 / `0d15009` / P69 T1); this row: "CLOSED 2026-09-22 (P69 T7)"; `hist:673`. |
| R26-231 | A PAGE'S BUILD IS NEVER CHECKED AGAINST ITS ROW'S SPAN (2026-09-18, found by the R26-226 lane). Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-22 each (P69 T7 / `0d15009` / P69 T1); this row: "CLOSED 2026-09-22 (P69 T7) WITH ITS SCOPE STATED"; `hist:674`. |
| R26-232 | THE PULSE ROWS READ A LIVING FULL-STAGE PAGE AS DEAD (2026-09-18, the H bed on the new doors). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18 each (P68 T5b evidence); this row: "BUILT 2026-09-18"; `hist:677`. |
| R26-233 | THE REVEAL RESCALE DRAGS LANDED INK; THE AXIS SHOULD YIELD TO THE LINE THAT PUSHES IT (2026-09-18, the H bed, the critic on copy e). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18 each (P68 T5b evidence); this row: "BUILT 2026-09-18"; `hist:678`. |
| R26-234 | THE INTERIOR WORD WALK GOES; THE ELECTRIC CARRIES THE LIFE (E99 s83, 2026-09-18). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-18 each (P68 T5b evidence); this row: "BUILT 2026-09-18"; `hist:679`. |
| R26-235 | A FULL-STAGE PAGE IS NEVER SERVED THE MEASURED FIXTURE (2026-09-18, found by the R26-220 lane). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-22 each; this row: "BUILT 2026-09-22 (the Fable worktree)"; `hist:680`. |
| R26-236 | THE PLATE'S LIFE IS KEN BURNS ALONE - the drift withdrawn for long form (E99 s84). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-22 each; this row: "BUILT 2026-09-22 (the Fable worktree)"; `hist:681`. |
| R26-241 | THE PAGE-BOX FIXTURE'S PIN IS THE PLAYER'S BYTES, SO EVERY ENGINE COMMIT REDDENS IT (2026-09-18, found by the R26-224 lane). Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-22 each (P69 T7 / `0d15009` / P69 T1); this row: "CLOSED 2026-09-22 at the root (P69 T1)"; `hist:686`. |
| R26-245 | THE IDLE-TOKEN COUNTER DOES NOT COUNT A KEN AS LIFE (E99 s84, 2026-09-22). Closed by P72 T0 (DONE-UNCLOSED). | BUILT 2026-09-22 each; this row: "BUILT 2026-09-22 (the Fable worktree)"; `hist:692`. |
| R26-246 | "PROP STAMP" IS NOT A `stamp`: the 24 prop cutouts have no route into a cut except a DOCKED CARD (2026-09-22). Closed by P72 T0 (DONE-UNCLOSED). | CLOSED 2026-09-22 each (P69 T7 / `0d15009` / P69 T1); this row: "CLOSED 2026-09-22"; `hist:693`. |
| R26-247 | A stamp is a landing to the gate, the cues, the camera. Closed by P72 T0 (DONE-UNCLOSED). | `7965c05` (P69 T2) + P69 T3-T5 done; `hist:694`. |
| R26-263 | `ledger_page` refuses area forms by name. Closed by P72 T0 (DONE-UNCLOSED). | `f63b569` "P69 T50 - forms judged by honesty, not type (E99 s100, s109 (5); R26-263)" - on both lanes; `hist:705`. |
| R26-272 | A bracket on a bars page draws nothing. Closed by P72 T0 (DONE-UNCLOSED). | `f63b569` "... and a bracket on a bars page (R26-272)"; `hist:714`. |
| R26-273 | A BAR CANNOT CHANGE ITS OWN VALUE (2026-09-23, found by P69 T35). Closed by P72 T0 (DONE-UNCLOSED). | `af869b7`, `5c6871c`, `afd8b3d`; this row: "closed (P69 T26a, af869b7)"; `hist:715`. |
| R26-276 | Scrubbing from one melt to another paints the wrong page. Closed by P72 T0 (DONE-UNCLOSED). | `7789afa` (P71 T4, the mount keyed per boundary); `tests/test_melt_snapshot_is_current.py:180` `test_a_seek_from_the_first_melt_straight_into_the_second_throws_page_b`; `hist:882`. |
| R26-279 | A ROW'S STAMP AND DOCKS ARE FITTED TO THE ROW'S FIRST CHART, NOT THE STATE ON SCREEN WHEN THEY LAND (2026-09-23, found by P69 T24). Closed by P72 T0 (DONE-UNCLOSED). | `af869b7`, `5c6871c`, `afd8b3d`; this row: "closed (P69 T26d, 5c6871c)"; `hist:885`. |
| R26-280 | THE MOTION GATE'S LONGEST WAIT (M03) NEVER COUNTS A RECAST (2026-09-23, found by P69 T24). Closed by P72 T0 (DONE-UNCLOSED). | `af869b7`, `5c6871c`, `afd8b3d`; this row: "closed (P69 T26c, afd8b3d)"; `hist:886`. |
| R26-282 | The IG and capex objects carry no unit. Closed by P72 T0 (DONE-UNCLOSED). | `7d43e43` "P69 T25 - ... the IG and capex objects get their units (v2)": `ev-ig-credit-weighting-v2` (`unit: %`, a sub stating what the bars show) and `ev-capex-consensus-v2` (`unit: $`, "US$ billions"); the `$...B` form is R26-287's; `hist:888`. |
| R26-290 | THE DESK CARD'S +105% LINE HAS NO NAME (2026-09-23, P69 rows 15-18 refresh). Closed by P72 T0 (DONE-UNCLOSED). | closed 2026-09-23 (T27); this row: "closed 2026-09-23 (T27: the desk card draws from its own derived object, the +105% line named 'chips' from its series' anchor text)"; `hist:896`. |
| R26-291 | PROP 3 SITS IN THE PUSHED PANEL'S CORNER (2026-09-23, P69 rows 15-18 refresh). Closed by P72 T0 (DONE-UNCLOSED). | closed 2026-09-23 (T27); this row: "closed 2026-09-23 (T27: PROP 3 placed and moved up into the top-right corner in step with the 1.2x push; M27 cleared, M25 WARN named)"; `hist:897`. |
| R26-293 | THE AUTHORING KIT REFUSES A PROP MORPH (2026-09-23, P69 T26e review). Closed by P72 T0 (DONE-UNCLOSED). | `0c606d6`; this row: "closed 2026-09-23 (lane B 0c606d6: the kit validates a prop morph with the compiler's own checks; pinned to its CHART_TO_KINDS)"; `hist:899`. |
| R26-295 | THE ONE-SHOT FLOOR TESTS NEED GITIGNORED INPUTS (2026-09-23, P69 T26e review). Closed by P72 T0 (DONE-UNCLOSED). | `0c606d6`; this row: "closed 2026-09-23 (lane B 0c606d6: the two floor tests skip with the missing gitignored path named)"; `hist:901`. |
| R26-296 | THE FLOOR'S TIMELINE HASH PINS ARE LINE-ENDING BOUND (2026-09-23, P69 fixes5 review). Closed by P72 T0 (DONE-UNCLOSED). | `83b89fd`; this row: "closed 2026-09-23 (lane B 83b89fd: timeline_sha256 hashes line-ending-normalised bytes; the four pins replaced, proven against the committed blobs)"; `hist:902`. |
| R26-297 | A lane that never takes main back. Closed by P72 T0 (DONE-UNCLOSED). | `d4ec5eb`; `hist:903`. |
| R26-298 | A READ-BACK PLAN LOSES A PROP'S AUTHORED PLACE (2026-09-23, P69 fixes5b). Closed by P72 T0 (DONE-UNCLOSED). | `83b89fd`; this row: "closed 2026-09-23 (lane B 83b89fd: the compiled dock records authored_place / authored_moves; the deriver copies them back; the compiler accepts the ..."; `hist:904`. |
| R26-300 | Row 20's test card below the phone floor. Closed by P72 T0 (DONE-UNCLOSED). | `b449e9f` (P69 T28b); `hist:906`. |
| R26-305 | The plate prompt guides still say "no text". Closed by P72 T0 (DONE-UNCLOSED). | `3473082` "docs: R26-305 - the plate-prompt guides take E99 s113" (lane A); `hist:911`. |
| R26-306 | Research NVDA's share and the railway-GDP series. Closed by P72 T0 (DONE-UNCLOSED). | `b67df03`: five objects verified and tiered (`docs/research/markets/r26-306-nvda-share-railway-gdp-VERIFY-2026-09-24.md`); the rejected remainder is R26-311; `hist:912`. |
| R26-308 | A title relight reads sunflower on its last frame. Code landed (`11b94d1`); the operator's read at P71-HG1. | `11b94d1` (P71 T2); REV 1: archived as "code landed; the operator's read at P71-HG1" (BACKLOG-DISCIPLINE `:20`); `hist:914`. |
| R26-310 | A recast hand-writes its ticks over an empty plot. Code landed (`e6aaa30`); the operator's read at P71-HG1. | `e6aaa30` (P71 T3); REV 1: archived as "code landed; the operator's read at P71-HG1"; `hist:916`. |
| R26-312 | The second melt shows the wrong page. Code landed (`7789afa`); the operator's read at P71-HG1. | `7789afa` (P71 T4); REV 1: archived as "code landed; the operator's read at P71-HG1"; `hist:918`. |
| R26-314 | A figure's subtitle never writes its last letter. Code landed (`ef96cee`); the operator's read at P71-HG1. | `ef96cee` (P71 T1); REV 1: archived as "code landed; the operator's read at P71-HG1"; `hist:920`. |

### Batch 3 - CLOSE-STALE / CLOSE-SUPERSEDED / CLOSE-DUPLICATE (20 rows)

| ID | Verified outcome | Evidence / follow-up |
|---|---|---|
| R26-11 | The HyperFrames intake. Closed by P72 T0 (CLOSE-SUPERSEDED). | the harvest `hyperframes/HARVEST-2026-09-07.md` (R26-15) took it over; HF lessons ported per slice (P47 T1, P70 T13 drift-hold); `hist:527`. |
| R26-31 | The Bravos exploration review, the next selection. Closed by P72 T0 (CLOSE-SUPERSEDED). | the selection was made: `BRAVOS-VOCABULARY-HARVEST-v2.md` -> P69 T36-T80 -> P70 / P71; `hist:513`. |
| R26-45 | The approved shorts' pages placed by the estimate. Closed by P72 T0 (CLOSE-SUPERSEDED). | the approved cuts are frozen (E45); every new page is measured (P69 T1 fixture); H's unmeasured pages are R26-274; `hist:463`. |
| R26-59 | The head above the newsreel. Closed by P72 T0 (CLOSE-SUPERSEDED). | RULED E99 s45 ("both should be options"); both exist (the card, and P53 T7's `cutout`); `hist:476`. |
| R26-62 | The ground's physics, tracked. Closed by P72 T0 (CLOSE-SUPERSEDED). | deprioritised under E22 and 44 s44.3's JUDGE row (in the row); `hist:479`. |
| R26-65 | The page CAN land built; a default. Closed by P72 T0 (CLOSE-SUPERSEDED). | E99 s67: "a chart never lands fully built: every page BUILDS ... then holds built" - the default is ruled; `enter=axes` shipped (P53 T1); E99 s9 "the opening register is the axes register"; `hist:483`. |
| R26-81 | The three-question test card on a short. Closed by P72 T0 (CLOSE-STALE). | the card is live on H row 20 (`b449e9f`, `checklist.profile: "phone"`); a short uses it when a script asks; `hist:499`. |
| R26-102 | The agentic-first production studio. Closed by P72 T0 (CLOSE-SUPERSEDED). | REV 1 citation: E99 s13 (`OPERATOR-RULINGS.md:2965`: "the 2026-09-13 readiness review is superseded; plans are written to be executed by either Claude or GPT"); parent confirms in T0 (D5); `hist:546`. |
| R26-124 | The race path default. Closed by P72 T0 (CLOSE-STALE). | E99 s8 chose no default ("the race reads as separate rules"); the row's own next action allows "leave both selectable if no default was chosen" - T0 records both selectable and the engine's current default, no ask; recorded by P72 T0: both paths stay selectable and no default was ruled; the engine's current default is `eased` (`LPX.RACE_PATH: "eased"`, `docs/content-video-engine/samples/scene-evidence-engine.mjs:11313` at 0d2e705), `clothoid` opt-in by the page's `path`; `hist:568`. |
| R26-155 | `melt:weight` rolls away from the landing. Closed by P72 T0 (CLOSE-STALE). | "left deliberately" in the row; REV 1 citation: E99 s56 (`OPERATOR-RULINGS.md:3230`, "P61 HG6-2 closed" on approval); `hist:599`. |
| R26-180 | THE SHAPE COMPILER. Closed by P72 T0 (CLOSE-SUPERSEDED). | E99 s77 (`OPERATOR-RULINGS.md:3272`): "the compiler is stopped"; P66 plan status `retired`; its HG1 cards ruled (queue `p66-hg1-*` ruled); `hist:624`. |
| R26-185 | The choreography vocabulary is the record's (s70). Closed by P72 T0 (CLOSE-SUPERSEDED). | E99 s77: the compiler is stopped; the engine truths it found are kept by s77 (2); the vocabulary now lives in CAPABILITIES + the Bravos USE-WHEN, cited by the receipt; `hist:628`. |
| R26-186 | A light is never the move; the throw is a signature (s71). Closed by P72 T0 (CLOSE-SUPERSEDED). | the compiler/lab clause superseded by s77; throw-then-zoom is built (P69 T15b; R26-260 names it in forward play); the rule is in the rulings (s71, s76); `hist:629`. |
| R26-187 | A rebuild of the original is not a base (s72). Closed by P72 T0 (CLOSE-SUPERSEDED). | E99 s77 stopped the base generator (P66 retired); the base rules (E67 inks, cues bound, outro, arrivals) are the builder's checklist - carried by R26-195's doc slice; `hist:630`. |
| R26-192 | A SHORT PLATE IS FOLDED INTO ITS NEIGHBOUR (E99 s75, 2026-09-17). Closed by P72 T0 (CLOSE-DUPLICATE). | "RE-HOMED to R26-195" in each row (E99 s77); `hist:635`. |
| R26-194 | A LIGHT ONLY WHERE THERE IS A SPECIFIC CALLOUT TO MAKE (E99 s76, 2026-09-17). Closed by P72 T0 (CLOSE-DUPLICATE). | "RE-HOMED to R26-195" in each row (E99 s77); `hist:637`. |
| R26-196 | The re-proof's two faults before HG2. Closed by P72 T0 (CLOSE-SUPERSEDED). | HG2 RULED (s84): the faults on the four DENIED recipes are moot; the two approved recipes' notes (even pills; the retitle's edge) fold into R26-237's recipe edit; `hist:639`. |
| R26-199 | Tokyo v2 approved to upload. Closed by P72 T0 (CLOSE-SUPERSEDED). | "AMENDED by s79"; v3b built, ruled and uploaded; `hist:642`. |
| R26-204 | P68 audit pointer row. Closed by P72 T0 (CLOSE-DUPLICATE). | a pointer: its thirteen children are R26-205..217, each inventoried on its own line; `hist:647`. |
| R26-216 | Ep1's report prints 16 of 35 rows (G-12). Closed by P72 T0 (CLOSE-DUPLICATE). | "nothing to fix ... the baseline H is measured against" - REV 1: a computation PRINTED on P68 HG4's card (the H report's motion rows diffed against `build-f`'s), never asked; `hist:659`. |

### Part 2 - the rows closed with their leftovers (3 rows)

| ID | Verified outcome | Evidence / follow-up |
|---|---|---|
| R26-176 | The recipe lab. Closed by P72 T0 (DONE-UNCLOSED) with its residual. | BUILT 09-17 P65 T1-T4/T7/T8 (`cf8a930`); the residual (P65 T6 promotion, HG1) is carried by the P65 items in section D - closed by P72 T0: P65 T6 closed by decision D3 (recipes are proved as beats in proof doors; the defaults come from rulings), P65 HG1's two cards `lab-smoke-r2-plate-carries-a-card` and `lab-batch-r1-plate-carries-a-card` withdrawn (E99 s82: no candidate-by-candidate cards; s84); `hist:620`. |
| R26-181 | The verified receipt and the critic. Closed by P72 T0 (DONE-UNCLOSED) with its residual. | BUILT P67 T1-T6 (`4b0343d`); HG1's card `one-shot-3-fable-memory-calendar` is RULED (E99 s71). The P67 HG1 question ("did the two scores say something the gates did not") was not the question s71 answered; it folds into P69-HG4, where the critic's read sits (P72 Human Gates, the P69-HG4 row) and is asked once there; `hist:718`. |
| LEGACY-REVALIDATION-2026-09 | The legacy rows revalidated; the board row closed by P72 T0. | P72's inventory section B read every non-archived R26 row against plan, commit, artifact and ruling evidence (the shas spot-checked with `git log -1`); batches 1-3 above archived its DONE and CLOSE rows, the five triggered rows are `⏸️` rows on the board with their triggers, and every still-open row points at the P72 slice that carries it. The second-pass report is in [`../../BACKLOG-DISCIPLINE.md`](../../BACKLOG-DISCIPLINE.md#second-pass-report--p72-t0-2026-09-25). |

## Remaining close-marked legacy rows

This was a census for parent review, not a second archive and not a completion
claim: among the 274 bold R26 detail row headers it listed 71 close-marked rows
(`CLOSED`, `DONE`, `BUILT` and the like in a trailing status cell) that the first
pass left unreconciled, because a token alone does not prove closure.

**Reconciled by P72 T0 (2026-09-25).** Each of the 71 was read against its
evidence. 64 are archived above, in the P72 T0 closing pass (batches 1-3 and part
2), each with its sha, file:line or ruling. The other seven are open work with a
carrier, and none of them is archived: R26-105 (P72 T19, `rel: pin` only, decision
D2), R26-132 (its part 2, the depth card in frame, P72 T7), R26-135 (its item 4,
the calibration one-shot, P72 T37), R26-161 (the fold, P72 T30), R26-168 (M38's
open question, the operator's, on P72-HG1's sheet), R26-175 (the one-shot
comparison, P72 T37 behind P54-HG3's two steps) and R26-219 (the bracket's label
room, P72 T43, and the note's `keep`, P72 T3).

The source also mentions R26-248 without a matching detail-row header. It stays
an unresolved source anomaly; this pass does not synthesize a task from it.

## P72 closing pass - batch 4 (2026-09-25): rows closed by P72's landed slices

| ID | Verified outcome | Evidence / follow-up |
|---|---|---|
| R26-116 | A melt recipe carries the melt stack. Closed by P72 T3. | lane B `80fa2f5`: `melt-then-rewrite` (a candidate, the compare `streak` form); neither approved cut plays it. |
| R26-128 | The research profiles never run the layer regen. Closed by P72 T31. | lane B `8f8106b`: 'Tier 0 - never run the layer regen' in the four profiles, `test_research_profile_rules.py`; its second half (the verdict up front) is R26-354, the sync source R26-353 (P72 T45). |
| R26-129 | The research ledger counts runs, not transport. Closed by P72 T31. | lane B `8f8106b`: `bridge/` is transport; 64 runs -> 63 over the main checkout. |
| R26-141 | The drift gate validates the card schema. Closed by P72 T2. | lane B `a4bfe6a`: `effects_catalog_check` check 13, `test_effects_catalog_schema.py`. |
| R26-144 | A moved packet's path resolves. Closed by P72 T31. | lane A `6e9ba30` follow_moved_packet (`test_bridge_moved_packet.py`). |
| R26-162 | The committed-tree test reads HEAD, not the working copy. Closed by P72 T2. | lane B `a4bfe6a`: a scratch copy of HEAD; a planted dirty card no longer fails it. |
| R26-174 | One host per cut is on the builder's checklist. Closed by P72 T4. | lane A `526096a`: `docs/runbooks/ONE-SHOT.md` 'One host per cut'. |
| R26-195 | s74 / s75 / s76 are on the builder's checklist; the compiler is STOPPED. Closed by P72 T4. | lane A `526096a`: ONE-SHOT.md's editing rules; CAPABILITIES THE SHAPE COMPILER RETIRED (s77). |
| R26-200 | s79 Apply 5 (idle tokens, the camera on named things, the axes open) is on the checklist. Closed by P72 T4. | lane A `526096a`. |
| R26-237 | The four s84 denials leave the proven set. Closed by P72 T3. | lane B `80fa2f5`: `status: denied`, `ruled_by: E99 s84`, the words verbatim; 11 proven; M38 on the approved Japan cut 0.76 -> 0.48 on P72-HG1 item 8. |
| R26-238 | Every `when` under the 260 ceiling. Closed by P72 T2. | lane B `a4bfe6a`: remake + six species trimmed, the strict xfail retired. |
| R26-240 | The effects layer ranks by field. Closed by P72 T2. | lane B `a4bfe6a`: `docs_find "Ken Burns" --layer effects` puts `plate_option:ken` first. |
| R26-244 | The lab-log pins read s84. Closed by P72 T2. | lane B `a4bfe6a`: `test_lab_log.py` 17 passed. |
| R26-252 | The lab lands a stamp on a stamp's clock. Closed by P72 T3. | lane B `80fa2f5`: 0.1542 s with `ink`, read from `authoring.audio`. |
| R26-337 | A dock never covers the schematic's plot at 9:16. Closed by P72 T40. | lane B `d509ed7`: the phase names counted as ink, a band outside the plot before the corner; test_video_dock 64 + 2 skip. |
| R26-313 | A stamped chip's seal is reserved; a card stays legible and off the page's words. Closed by P71 T5. | lane B `3d6e8e5`: `chip_stamp_reserved_box`, the legibility-first placer (words > ink > seals), bed b 0 px2 on seals and words. |
| R26-354 | A report-landed reply with no verdict up front fails tier 0. Closed by P72 T45. | lane A `d07fec2`: `verdict-up-front`, one repair. |
| R26-355 | Astra packets land from their own reply.md. Closed by P72 T45. | lane A `d07fec2`: `bridge_watch.FILE_LANES`, the provenance checks; the three live packets closed by hand (their work in main). |
| R26-340 | The bridge holds on a restart: one summary toast, no packet lost, echoed or sent down the wrong lane. Closed by P72 T44. | lane A `78c884f` (`test_bridge_restart.py`, the rebuilt 02:17 restart 10 toasts -> 1); the live daemon runs it from the merge to main. |
| R26-206 | The landscape safe box. Closed by P72 T8. | lane B `02e9b83`: `--aspect 16:9`, the bottom 120 px measured on YouTube's player. |
| R26-207 | The long-form floor names its reference. Closed by P72 T8. | lane B `02e9b83`: --reference required over 3:00; the SHORT caveat. |
| R26-208 | M46 honest over 3:00. Closed by P72 T8. | lane B `02e9b83`: INFO until a long form is approved. |
| R26-203 | The opening gate runs on its own take. Closed by P72 T8. | lane B `02e9b83`: a take under 0.95 in-order overlap is refused (H's borrowed take was `vo/`, not G's as the row said). |
| R26-212 | The brand line in the long shape. Closed by P72 T8. | lane B `02e9b83`: S07 runs in both shapes. |
| R26-242 | Cites resolve by row title. Closed by P72 T29. | lane B `47d87a0`: `resolve_cite`, the decoy-row test; 587 of 645 cites. |
| R26-301 | The skeleton vocabulary's cites follow their rows. Closed by P72 T29. | lane B `47d87a0`. |
| R26-318 | The value gate reads every page; an unreadable page FAILs by name. Closed by P72 T6. | lane B `9dc5bb6` (`test_value_gate_longform.py` 80; three review rounds). |
| R26-303 | A range is judged at both ends. Closed by P72 T6. | lane B `9dc5bb6` (`test_value_gate_longform.py` 80; three review rounds). |
| R26-264 | A card's own badge is never page ink. Closed by P72 T6. | lane B `9dc5bb6` (`test_value_gate_longform.py` 80; three review rounds). |
| R26-319 | The horizontal gauge is read by width; `gauge:h` admitted. Closed by P72 T6. | lane B `9dc5bb6` (`test_value_gate_longform.py` 80; three review rounds). |
| R26-334 | A balance side carries its sign ink. Closed by P72 T41 (code landed). | lane B `a29e67a`: `tone: neg|pos|neutral`; the pill FORM is the operator's pick at P72-HG1 item (6) (sheet `_proofs/p72-sign-and-hatch/sheet-r26-334-pill-forms.png`). |
| R26-140 | A repeat capture of one golden differs. Closed by P72 T9. | lane B `ae5f6b8`: `render_baseline.py --repeat N [--surface S]` - fresh captures against the golden (exit 1), warm against the first, each drift named by bytes / box / cause; data-to-bars drifts 13 B warm by raster (same DOM), so the goldens keep the fresh-page rule. |
| R26-243 | A capture under load shoots the fallback face. Closed by P72 T9. | lane B `ae5f6b8`: the cause was the hand fetched from Google, not CPU (6x throttle 0 bytes); `prepare_page` waits on `window.__fontsSettled()`, reloads a failed face (3 loads), then `FontsUnsettled` names it. The local font file is R26-360 (P72 T27). |
| R26-251 | The fixed 250 ms font wait. Closed by P72 T9. | lane B `ae5f6b8`: replaced by `__fontsSettled` (both faces, two painted frames, one task); pre-template players keep the old wait. |
| R26-151 | A second golden-source build differs. Closed by P72 T9. | lane B `ae5f6b8`: not non-determinism - two builds under hash seeds 1 / 2 are byte-identical; 9 committed sources predate the builder and are named in `STALE_SOURCES` (re-pinning them is its own golden change). |
| R26-323 | Golden sources written with CR. Closed by P72 T9. | lane B `ae5f6b8`: `build_golden_sources.py` writes LF; `test_golden_frames` pins a second build byte-identical and LF. |
| R26-351 | Unguarded Playwright starts leak the asyncio loop. Closed by P72 T9. | lane B `ae5f6b8`: `tests/served_player.py` is the one guarded start; 39 files migrated; `test_render_determinism` fails on any unguarded start. |
| R26-145 | Two browser suites interfere in one pytest process. Closed by P72 T2 + T9. | lane B `a4bfe6a` (T2: the leaking fixture named and closed) and `ae5f6b8` (T9: every Playwright start through the guarded `tests/served_player.py`; a raising prepare no longer leaves the loop running, RED at the base in `logs/red-r26-351-leak.txt`). |
| R26-309 | A prop's authored exit near its page's end is kept on the page. Closed by P71 T6. | lane B `43363ea`: the engine's load-time boundary snap (0.05-1.4 s) skips a dock that owns its exit (`dockOwnsExit`: a stamped mark or a prop), and the wipe's `swept` never takes it back to full; cards keep the snap. The compiler was right; no refusal (s106). `test_prop_exit_near_page_end` 8; H door identical. |
| R26-268 | A plate's caption crosses its subject or sinks into a light plate. Closed by P72 T14. | lane B `7c2258d`: `;caption_room=x,y,w,h` on a picture plate; the stage caption's measured backing below the reference's 3.97 floor (a text-shadow stroke / core / halo, never a box, doc 29 Part 5): cream 2.55 -> 12.08, all 32 of H's plate stage captions up. The quiet strip stays P71 T8b's; no H row declares a room yet (P69's retrofit, HG3). |
| R26-278 | An opening quote hangs on the word before it. Closed by P72 T14. | lane B `7c2258d`: `build_caption_pages.place_quotes` moves it onto the word it opens; no timing moved (H: four quote pages). |
| R26-292 | The next caption jumps in while a page collapses into a prop. Closed by P72 T14. | lane B `7c2258d`: `exit: morph:prop` keeps the caption in the strip for the collapse window (`_prop_collapse_at` / `pmOver`, one window for compiler and engine). |
| R26-315 | A hidden panel fades in already built. Closed by P72 T12. | lane B `1bbaded`: `lpPanelBuildAt` - the panel builds from the reveal's landing, frame and axes standing empty while it fades in; a figure on it runs from the same build (H row 21's "3x" lands with its bars). |
| R26-299 | A panel's tick labels read as a lone "%". Closed by P72 T12. | lane B `1bbaded`: not a glyph write - the shrinking front panel's opaque ground cut them; `lpPanelOcclude` hides a word a front panel covers in part. |
| R26-339 | The one-bar stacked page overprints at longform:phone. Closed by P72 T12. | lane B `1bbaded`: the bars page runs to the safe edge at phone (`lpLongformBarsVW` / `longform_bars_vw`), names wrap at their slot, nothing under the 59.08 px floor. |
| R26-316 | The panels page at longform:phone does not hold. Closed (its advice) by P72 T12. | lane B `1bbaded`: a `WARN fit:` per panels page at phone naming the region against the ~327 px a panel needs and the faults (s106 - never refused). The BUILD half is R26-366 (P72 T47). |
| R26-57 | Stage-space text renders at `auto`. Closed by P72 T27. | lane B `244f129`: the species text and the dock chart tier at `geometricPrecision`; 15 goldens re-pinned (edge antialiasing only). |
| R26-142 | The agenda page's palette is hex in the painter. Closed by P72 T27 (16:9). | lane B `83c3a98`: template classes `.agplate/.agmed/.agtitle/.agfig`; 16:9 byte-identical; the 9:16 form is R26-369 (T46). |
| R26-72 | The engine's tierDomain ignores shared_tier_domains. Closed by P72 T27. | lane B `3a3924c`: `tierShared` -> `tierDomain`; same-unit tiers on one scale when the page carries the key; the compiler's default is R26-370 (T46). |
| R26-360 | The hand is fetched from Google at every capture. Closed by P72 T27. | lane B `4b54f77`: the six Kalam faces (OFL, the v18 build byte-identical) served locally, inlined or copied beside a split build; no capture touches the network; every golden byte-identical. |
| R26-9 | The transitions review's open items. Closed with TR-3 by P72 T27. | lane B `b5fb270`: every untagged transition constant carries an [UNSOURCED - ...] tag with its commit, doc line and why kept (TR-4 was `e96059d`, E46); a retune is its own row off the reference (E38). |
| R26-257 | The extruded prism's light is not the stage's. Closed (code) by P72 T27. | lane B `73625e2`: `EXTRUDE.LIGHT_DEG` = `DROP.LIGHT_DEG`, `VIEW_DEG` 35 keeps the shape, the shadow along the light + 180 (55.0 measured); three goldens re-pinned; the before / after is P72-HG1 item (2) for the operator's read (the shadow nearly hides at `SHADOW_K` 0.55). |
| R26-2 | A composited sprite has no harmonisation pass. Closed by P72 T27. | lane B `033d418`: the opt-in `harmonise` dial (light wrap + substrate grain, off byte-identical); golden `newsreel-band@harmonise`; the wrap's dials read heavy - tune by eye. |
| R26-286 | The suck has no cue. Closed (the kit) by P72 T20. | lane B `4e077e4`: `fired` books the suck at the START of its scene over the engine's SUCK_S (it sat 25 s off, at the scene's end); `suck_cues` gives one cue per suck row; H's door names them at the lane merge (the held patch), P72-HG1 item (10) listens. |
| R26-329 | The hand-off cue plays before the card is seen. Closed by P72 T20. | lane B `4e077e4`: `first_seen` / `seen_contact` mirror the engine's slot painter (the 0.72 s live tail, one card per slot, the 0.01 s scrub); H's 12 hand-off cues move 0.33-0.48 s onto the card's first frame (frames 12 of 12); the drop itself is never shown - the dock painter's (T19). |
| R26-326 | The verdict stack's beats earn no motion events. Closed by P72 T7. | lane B `9fe66e9`: `_stack_beats` credits every flight, landing, recede, gather and burst off the painters' clocks; the stack build FAIL -> PASS on M01 / M05 / M08 (widest gap 3.24 s). |
| R26-269 | A record's typing earns no events. Closed by P72 T7. | lane B `9fe66e9`: `_record_beats` - each word on its onset, the attribution and the source; the Karp window 3 -> 30 events (worst gap 6.67 -> 2.76 s). H's 2:00 gap is the COO window's (R26-374). |
| R26-167 | No window mode for one beat's claim. Closed by P72 T7. | lane B `9fe66e9`: `--beat t0,t1` judges M11 on the window. |
| R26-189 | No gate row names the transform a cut refused. Closed by P72 T7. | lane B `9fe66e9`: M50 (INFO) lists every cut and dip with `refused: <x>` off `exit_why`; `(unnamed)` everywhere until the compiler writes the why. |
| R26-132 | A dock at a depth overshoots the move that aimed at it. Closed (the gate) by P72 T7. | lane B `9fe66e9`: M24 WARNs a settled depth card carried off the frame, measured off the probe (dock-depth: 79 px); the seek purity and the placement it implies are R26-376 (T21). |
| R26-338 | A braced middle bar's label lands on its neighbour. Closed by P72 T43. | lane B `a0396db`: with no clean side the label goes above the bar; `check_brace` WARNs the room by number; every golden unchanged; the loose ends are R26-375 (T46). |
| R26-342 | M21 counts only build marks. Closed by P72 T7b. | lane B `8c699a6`: a park ends a chart's life, an un-park starts one; rings and cards restart nothing (E50). |
| R26-345 | The life count misses a declared life species. Closed by P72 T7b. | lane B `8c699a6`: `life_tokens` names `life <dur>s`; H reads Life 27 of 27. |
| R26-253 | The E65 room lands on the page's words. Closed by P72 T15. | lane B `400cf89`: `page_boxes` carries the basis and the bar names; the room is cut round them (the card was fixed by `3d6e8e5`). |
| R26-270 | A wrapped bar name is not measured. Closed by P72 T15. | lane B `400cf89`: bar names measured; one into the source or caption band WARNs (the 9:16 room is R26-380). |
| R26-274 | Pages without measured boxes. Closed (both halves). | the fixture half by d11e919 / 54bd650 (P72 T15's step 0); the units half by P72 T13 `6c349b0`. |
| R26-287 | A unit with a prefix and a suffix (`$` + `B`) cannot be written. Closed by P72 T13. | lane B `6c349b0`: `unit_suffix` beside `unit: "$"` writes "$480B" on values, ticks, pill and card; refused by name when malformed or off a bars page. |
| R26-250 | A comparator rule's label covers a bar. Closed by P72 T13. | lane B `6c349b0`: the label slides, wraps, shrinks (>= 0.7) or goes past the rule's end; `st.ruleFit` reports. |
| R26-170 | A signed page's category labels sit under the bars that point down. Closed by P72 T13. | already fixed at `2b7b6a4` (M28 PASS); T13 confirmed it, not rebuilt. |
| R26-217 | The treemap / tiers legibility constants ignore the stage. Closed by P72 T13. | lane B `6c349b0`: treemap floors per stage; the tiers ceiling states its measure. |
| R26-164 | A layered plate's drift ignores the camera. Closed by P72 T25. | lane B `2b37127`: the walk projected onto the camera's move, on its side; off with a WARN when the camera gives none; a flat plate keeps its free drift (s65). |
| R26-165 | A ken has no window - a lean cannot start on a word. Closed by P72 T25. | lane B `2b37127`: `(scale, x, y, t0, t1)`; holds, leans, holds; a freeze pauses the lean; the clash check's window is R26-392. |
| R26-21 | The snap's card box is not a pure function of t. Closed by P72 T21. | lane B `7263013`: with R26-260 - the page grows from the card's placed box, about its own origin. |
| R26-260 | Forward play and a cold seek disagree at the snap (+137 / +100 px). Closed by P72 T21. | lane B `7263013`: a stale `transform-origin: 0 0` after the snap; now about the page's origin. |
| R26-294 | The dock slot's state is not pure (H 306.34 on a jump seek). Closed by P72 T21. | lane B `7263013`: a stamp's pivot leaked into the next card; reset every frame. |
| R26-321 | The melt's clone is taken from the live frame. Closed by P72 T21. | lane B `7263013`: the page as painted at `span[0]`; no melt golden moved. |
| R26-322 | `melt:morph`'s hand ring is read before the outgoing page paints. Closed by P72 T21. | lane B `7263013`: read after `paint(wA, prev)`, from a mount keyed to this boundary. |
| R26-324 | The title glow is not repainted after a colour change (6/255). Closed by P72 T21. | lane B `7263013`: the title leaves layout and returns in the same frame. |
| R26-376 | The dock-depth card seeks 69 px higher than it plays. Closed by P72 T21. | lane B `7263013`: `dockCam` from the placed height; its badge row off the stage is R26-398. |
| R26-328 | A re-docking of the same id keeps the first box. Closed by P72 T19. | lane B `89de388`: the coalescer merges only a same box; a new box is a new docking (H row 23's workaround no longer needed). |
| R26-285 | A dip's docks retract over the incoming scene. Closed by P72 T19. | lane B `89de388`: the docks ending on its boundary, and their wash, go at the black; the snap never crosses a landing. |
| R26-271 | The prop hatch ignores the dock camera. Closed by P72 T19. | lane B `89de388`: the hatch lines ride the arrival prefix and a depth dock's plane, and take the arrival's blur. |
| R26-320 | A press card cannot hold with the drift-hold. Closed by P72 T19. | lane B `89de388`: `idle: hold` on a press card drifts on its own span with the light band. |
| R26-267 | A dock cannot ride another dock's read and park. Closed by P72 T19. | lane B `89de388`: `rel: {pin, inherit?}` (E97; translation by default); a bad pin refused across the cut. |
| R26-202 | A throw cannot pick its entry edge (b); the over-build landing (a). Closed by P72 T19 (b) and P72 T7 (a). | lane B `89de388`: `side: left|right|bottom` on a throw; `top` refused (a drop). |
| R26-343 | A park leaves the long form's key rail at full size. Closed by P72 T19. | lane B `89de388`: the key rail scales about the chart's anchor on a park and returns on the un-park. |
| R26-157 | The splash has no off-screen pitch. Closed by P72 T23. | lane B `151636d`: `melt:splash:...:offscreen` - out of the frame, 6 empty frames, back flatter and faster (E99 s56). |
| R26-146 | The ball cannot blend the page's inks. Closed by P72 T23. | lane B `151636d`: `body=blend` (Kubelka-Munk, each series ink one arm); its green on the golden is P72-HG1 (3). |
| R26-139 | The gather swings the axis hairlines as straight sticks. Closed by P72 T23. | lane B `151636d`: they curl into the spiral (`MELT.G_LINE_CURL`, on; P72-HG1 (12)). |
| R26-389 | The two-ink hand goes muddy. Closed by P72 T23. | lane B `151636d`: a sweep hands the ink over, chroma 200 -> 57 with no dip (`MELT.HAND_INK_ON`, on; P72-HG1 (12)). |
| R26-361 | The seal's name keyline and gold ignore the ground. Closed by P72 T46b. | lane B `976fcc4`: the keyline reads the latched ground (1.57:1 -> 6.85:1 on the mid photo); the compiler's gold twin WARNs when no gold holds 3:1; one `worldPoseAt`. |
| R26-362 | The choreography mirror snaps a stamp and a prop to the boundary. Closed by P72 T46b. | lane B `976fcc4`: a stamp or prop owns its exit; a WARN names an owned exit running past its page's end; (c) a spring cutout keeps the card's rule by decision. |
| R26-391 | The verdict tile earns no gate credit; the seal's verdict refusal is unclear. Closed by P72 T46b. | lane B `976fcc4`: the motion gate credits the tile's landing on its word; the refusal points to the chart card's `verdict` tile. |
| R26-368 | (b) The cadence rule is in 1080 px, not picture widths. Closed by P72 T46e. | lane B `7f5ead9`: `cadence(v, kind, {stage_w})` - 154 px/s on 1080, 273.8 on 1920; M20 reads the aspect. |
| R26-403 | The gate does not credit a bars extend as new data. Closed by P72 T46e. | lane B `7f5ead9`: `EXTEND_NEW_DATA` credits `field` and `bar`. |
| R26-392 | The ken-vs-camera clash ignores the ken's window. Closed by P72 T46e. | lane B `7f5ead9`: compiler `ken_lean_window` and gate `_ken_window` agree on (t0, t1). |
| R26-349 | M25 misses a schematic's words. Closed by P72 T46e. | lane B `7f5ead9`: it already failed them; now it names them (a phase name, the schematic's tag). |
| R26-356 | The effect cards' CAPABILITIES cites are by line and rot. Closed by P72 T46e. | lane B `7f5ead9`: 92 cites are `CAPABILITIES[<span>]`, resolved to `row_cites`, a bad cite refused by name. |
| R26-352 | The ingester does not re-apply the operator's hand scrub. Closed in code by P72 T46e. | lane B `7f5ead9`: reads `scrub-terms.txt` from the operator's folder (outside git); docket 12 re-scrubs once the operator writes it. |
| R26-358 | The strength screens read a take that is not the script's. Closed by P72 T46e. | lane B `7f5ead9`: `screens_take` refuses a foreign take by name (0.95), as the opening gate does. |
| R26-359 | The audit crashes on a kokoro words file. Closed by P72 T46e. | lane B `7f5ead9`: `take_groups` reads numbered scenes as one take and a named words file as its own. |
| R26-393 | The probe misreads a hover; the blur veil hides the park's join. Closed by P72 T46c. | lane B `16ecb98`: the probe mirrors DOCK_HOVER; a parking blurred card clears its veil over the park. |
| R26-394 | M26 cannot read a bar's re-counted figure. Closed by P72 T46c. | lane B `16ecb98`: `vs: fig` when the figure speaks for its bar (`__barMorphs`). |
| R26-344 | A callout ring on a parked page stays stage size. Closed by P72 T46c (with R26-404). | lane B `16ecb98`: ring, stroke and label scale about the datum with the park (ctx `parkScale`). |
| R26-404 | The ring under a park (R26-344's twin). Closed by P72 T46c. | lane B `16ecb98`: as R26-344. |
| R26-398 | A depth dock's badge rail falls off the stage. Closed by P72 T46c. | lane B `16ecb98`: the whole card stays 24 px inside the stage; `dock-depth` re-pinned. |
| R26-369 | The agenda at 9:16 crowds its words. Closed by P72 T46c (the icon size at P72-HG1 (16)). | lane B `16ecb98`: narrow rows shrink icon and medallion (floor 0.4); the title fits its rule. |
| R26-219 | A span stands inside the end-tag column. Closed by P72 T46d. | lane B `095c3ad`: it steps back to the column's inner edge; T43's WARN names the move. |
| R26-375 | The brace's lifted label has no leader; copied constants drift; a WARN crashes cp1252. Closed by P72 T46d. | lane B `095c3ad`: a leader from the point; a pin test; `_console_safe`. |
| R26-379 | The level's figure cannot sit on the axis. Closed by P72 T46d (an option). | lane B `095c3ad`: `label_at: "axis"`. |
| R26-382 | No chart beside the map. Closed by P72 T46d (the map side). | lane B `095c3ad`: `;room=` - the map fits the strip beside the card's room. |
| R26-383 | The map's framing is loose and its ping does not glow. Closed by P72 T46d. | lane B `095c3ad`: `;fit=tight`; the ping blooms (measured off CHN 02:21.4); `vecmap-route-tokens` re-pinned. |
| R26-384 | The hub's failed-link badge is too small. Closed by P72 T46d. | lane B `095c3ad`: 46 stage px; `look: "seal"`; `hub-spoke-fail` re-pinned. |
| R26-395 | A solo cannot light two bars. Closed by P72 T46d. | lane B `095c3ad`: `add: true`. |
| R26-396 | The lit end badge has no box. Closed by P72 T46d. | lane B `095c3ad`: a filled accent box, charcoal type. |
| R26-370 | Same-unit tiers do not share a scale by default. Closed by P72 T46d. | lane B `095c3ad`: `shared_tier_domains` written unless `independent`. |
| R26-400 | A stamped prop's contact shadow dips with the stamp's ink (regression, P70 T1b 50b2f85). Closed by P72 T46a. | lane B `81f39ae`: the prop's contact keeps its weight; test_prop_shadow 13/13. |
| R26-341 | The spread paints under the long-form panel. Closed by P72 T46a. | lane B `81f39ae`: `lpGroundInsert`. |
| R26-386 | A series cannot be dashed. Closed by P72 T46a. | lane B `81f39ae`: `dash` through the projection's mask twin. |
| R26-390 | The morph's two-plate ground pops in. Closed by P72 T46a. | lane B `81f39ae`: `MORPH_PLATE.IN` 0.1. |
| R26-399 | Stale notes and a stale transform-origin. Closed by P72 T46a. | lane B `81f39ae`: paint() clears it; determinism_check's known class retired. |
| R26-401 | `lpVarHex` returns a raw var(). Closed by P72 T46a. | lane B `81f39ae`: reads the template's palette. |
| R26-402 | The reference rule pops in at .9. Closed by P72 T46a. | lane B `81f39ae`: it fades with its page's build. |
| R26-380 | (a) A portrait bars page has no room for a name's second line. Closed by P72 T51b. | lane B `c5b508c`: `lpBarNameRoom` raises the floor one name line when a name wraps; (b) the placement cost order waits for a ruling. |
| R26-284 | A figure double-prints its bar's value. Closed by P72 T18. | lane B `4b07424`: the figure hands over in place; a restating figure WARNs (s106). |
| R26-288 | A ring on a bar has no value target. Closed by P72 T18. | lane B `4b07424`: `part: value` rings the printed value as drawn. |
| R26-255 | A bar figure drifts on a page with states. Closed by P72 T18. | lane B `4b07424`: it rides its bar through a rescale. |
| R26-256 | The pill and the figure are both up. Closed by P72 T18. | lane B `4b07424`: the pill yields on the figure's clock. |
| R26-366 | The panels page at phone is not built. Closed by P72 T47 (where it holds). | lane B `9c4cac1`: the two-era page holds; four panels cannot (R26-381). |
| R26-227 | The take's rate is not measured. Closed by P72 T28. | lane B `c7f133c`: `scratch_take.py --measure --wpm`; the runner reports `measured_rate:`. |
| R26-215 | `--table` takes no bare name. Closed by P72 T28. | lane B `c7f133c`: resolves in the project, then the build; the default follows the build. |
| R26-130 | A plate-library rebuild loses records silently. Closed by P72 T28. | lane B `c7f133c`: refused by plate id; `--drop`, `--sweep`. |
| R26-183 | `verdict_line` misreads the heading. Closed by P72 T28. | lane B `c7f133c`: the `## N. Verdict` shape read; a round-trip test. |
| R26-188 | The door cut / survivorship order; the mirror check. Closed. | the P66 parts superseded, doc 50 s50.7 exists; the mirror check by P72 T28 `c7f133c` (+ `33c6d9c`). |
| R26-33 | The dual-lane map and the sonar ping. Closed by P71 T22. | lane B `28eddf5`: `ping: true` - ONE ring as a place lands (CHN 02:21.1 / D40 13:56.5 measured; the repeating sonar withdrawn on the frames); the chart-beside-the-map layout is R26-382 (T46). |
| R26-148 | No morph golden across two inks. Closed by P72 T24. | lane B `0927f90`: golden `melt-morph-two-inks`; its muddy mid-hand ink is R26-389 (T23). |
| R26-150 | `polyStrip` fills a C-shaped bay silently. Closed by P72 T24. | lane B `0927f90`: bays listed; the axis turns only for a filled bay; an S-shape refused as "bay". |
| R26-152 | No `field=plates` morph golden. Closed by P72 T24. | lane B `0927f90`: golden `morph-planted-plates`; its front-loaded first frame is R26-390 (T46). |
| R26-153 | A short morph's soak snaps. Closed by P72 T24. | lane B `0927f90`: `MORPH.GROUND_MIN_S` 0.6 s; a 0.3 s morph's worst frame 0.085. |
| R26-163 | M17 judges a planted source by a named prop's invariants; the tie folds. Closed by P72 T24. | lane B `0927f90`: M17 judges det only and names the fold; the tie stays upright (its approved beat). |
| R26-169 | A portrait member shows only its header. Closed by P72 T22. | lane B `42d0fab`: a tall member takes its own box at the same area. |
| R26-173 | The burst's cards stand after a seek. Closed by P72 T22. | lane B `42d0fab`: hidden, not removed - no ghost on a seek, repainted on a seek back. |
| R26-304 | The rails move under a freeze. Closed by P72 T22. | lane B `42d0fab`: the life clock; the dock door refuses an enter / exit / beat inside a freeze. |
| R26-327 | A never-docked member paints a blank card. Closed by P72 T22. | lane B `42d0fab`: members by name (a docked document or a shown page); anything else refused; a live member is R26-388. |
| R26-378 | The spread's fill has no bloom. Closed by P72 T49. | lane B `9a59dd4`: the fill at D40's measured brightness (`PS.SPREAD_A` 0.51) and a halo inside D40's band (`LP_SPREAD_GLOW`); the hue is P72-HG1 item (11). |
| R26-123 | The caption-life default is not the blend. Closed by P72 T27. | lane B `2a6d887`: an unauthored build writes `cap_life: blend` (E99 s6), `base` pins the shipped caption; the blend's keyword box stays on the shorts' phrase caption (E99 s6 judged no keyword; on H the box under #c98500 was 1.25:1) - the long form gets the rise and stagger only. Follow-ups R26-371 / 372. |
| R26-73 | The newsreel's 9:16 default contradicts E84. Closed by P72 T27. | lane B `19f5546`: a crawl with no target takes the top of the bottom third; the caption goes one strip above it, docked or not; the two refusals E84 retires are gone; authored bands stand. E84 (1) not built. |
| R26-367 | A ring authored at a stage point misses the line it means (the operator's question). Closed by P72 T48. | lane B `dcf1b8d`: a datum on a docked chart (`{kind: datum, dock, series, index}`) rings the card's own drawn line, drawn above the card; the chart-callout golden bound (0.1 px from datum 152, was 39.6 px above); M49 WARNs a point mark off every drawn line; follow-ups R26-373 (T46). |
| R26-307 | `y2` is accepted and ignored. Closed by P71 T13. | lane B `f956fd7`: a line page's second axis (and an inverted one) for a co-movement claim draws; `y2` is refused by name wherever it would not be a reading (other builders, no claim / units, levels or gaps across the scales, a level claim on the inverted line, 9:16 not built); golden `dual-axis-inverted`; two review rounds. |
| R26-249 | An unauthored page's build is never checked against its row. Closed by P72 T17. | lane B `79c075f`: the builder's own entry + build + leave checked; an overrun WARNs with the numbers (s106). |
| R26-317 | A door never prints the page's E79 WARN. Closed by P72 T17. | lane B `79c075f`: `page_warning_lines`: every warning a page or a later state carries reaches the build log (E79 as `R26-317 E79`). |
| R26-154 | The melt's throw and morph lengths have no compiler twins. Closed by P72 T17. | lane B `79c075f`: `MELT_T_S` 0.77 / `MELT_M_S` 1.3 twin `melt.mjs`, pinned in e47. |
| R26-43 | A tag wider than its chart drops its tip pill silently. Closed by P72 T17. | lane B `79c075f`: `tip_pill_width_warns` WARNs by name with the estimate. |
| R26-149 | `world.morph` cannot choose its series. Closed by P72 T17. | lane B `79c075f`: `;morph_series=<n>` (the engine's `buildMorph`), refused by name out of range or off a line page. |
| R26-214 | The builder's checklist and `;idle=figure` on a world plate. Closed by P72 T17. | lane B `79c075f`: (a) closed by P72 T4; (b) `plate_idle_error` refuses `;idle=figure` on a picture plate by name. |
| R26-209 | An open zoom at a scene boundary is never named. Closed by P72 T17. | lane B `79c075f`: `camera_boundary_notes`: an INFO line per build; a zoom held into a cut WARNs. |
| R26-258 | `dock_place` ignores a prop's resting shadow. Closed by P72 T17. | lane B `79c075f`: `prop_dock_box`: a thrown or sprung prop's room gives up the shadow's reach; stamped and authored props untouched. |
| R26-143 | `compare` beside `remake` on one page is neither refused nor proven. Closed by P72 T17. | lane B `79c075f`: the probe showed a dropped state, so `compare_remake_errors` refuses the pair by name (the first half closed earlier). |
| R26-333 | A decade ruler over a freeze beat is neither refused nor warned. Closed by P72 T17. | lane B `79c075f`: `freeze_ruler_advice` WARNs with the ruler, the beat and the overlap (s106). |
| R26-85 | The strobe's sharpness on real motion is unmeasured. Closed by P72 T32 (a measurement). | lane B `514b465`: `measure_strobe_sharpness.py`; H vs Bravos / Wealth Logic - the step rate separates them, not the sharpness; the operator's question and the cadence unit are R26-368 (P72-HG1 item 9, T46). The record: main checkout `docs/research/runs/p72-t32/`. |
