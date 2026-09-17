# Survivorship matrix and memory audit (2026-09-17)

Explorer run for the Fable parent, on the operator's question the same day: *"I think maybe using the japan short
version where we implemented the door orginally might be better, since it has more recent mechanics and includes
more of our polishes, though not all of them. Currently is the script builder referencing memories? probably those
currently 100 items are an important part. Plus maybe seeing what survives across various shorts helps better
understand which parts should be carried forward first"*. The explorer's file write was refused by the harness; the
parent persisted its report here unchanged. Ruling: `docs/portable/OPERATOR-RULINGS.md` E99 s73.

## Headline

**In every cut (A Tokyo 09-09, B Japan 09-10, C Bridge 09-12, D Japan DOOR 09-15, E Calendar 09-16):** `mount`,
`dip`, `cut`, `hold`, `card` (weakening), `caption_style: "phrase"` + modes `["stage","anchor"]`, the electric inks
(engine-level palette), the outro card. `km_ink:false` in all five.

**Only in the latest two (D, E):** a named idle on *every* world (`idle=drift`/`live`, 12/12 scenes), page badges as
the figure carrier, plate-led worlds, light-not-ring.

**What D (the door) adds over Tokyo:** `door:right` as an authored exit (the only instance on disk), idle on every
world, two throw-then-zoom pairs (`arrival:throw`/`paper` -> `page_enter:snap`), 5 plates + 2 clips, trace x6 /
callout x6 / spotlight x4 (Tokyo 1/2/1), the wafer light.

**What E adds over D:** `enter=axes` x4, Ken Burns plate life `(0.06, 6, -4)` on all 5 plates (every other cut has
`ken.scale = 0`), the compare melt (`chart_to compare, form melt, then splash`), `peel`/`span`/`share` variant,
spiral + suck, and a written BEAT-PLAN with comparator + capability + recipe per row.

**The regression:** `rescale`, `recast`, `park`, `unpark`, `ticker` exist **only in Tokyo** and have not been carried
since 09-10. `morph`, `remake`, `object-becomes-chart`, the verdict wall are in **no short at all** - their `cut=`
citations point at proofs and lab builds.

**Memory audit: 89 files -> 55 ruling/CAPABILITIES/gate, 17 doc-only, 3 ephemeral, 14 NOT in the record.**

## 1. Method

`content/video_engine/scripts/recipe_walk.py` (docstring lines 1-60) is the contract; `events()` was imported and
each timeline walked, then the raw JSON re-read for what the walk does not emit as cards (`caption_style`, `sound[]`,
`kinetics{}`, `world.layers`, `page.badges`, `page.series[].color`). Vocabulary = the 20 `const`s of
`content/video_engine/configs/shape_skeleton.schema.json:25+`, each of which already carries `record=` and `cut=`
citations (E99 s70 Apply 2).

## 2. The cuts

| id | cut | build script | timeline | scenes | runtime |
|---|---|---|---|---|---|
| A | Tokyo | `.../tokyo-tea-break/build_short.py` (594 ln) | `tokyo-tea-break/build-short/tokyo-short.timeline.json` | 7 | 88.82 s |
| B | Japan approved | `.../japan-tariff-trick/build_short.py` (409) | `japan-tariff-trick/build-short/japan-short.timeline.json` | 12 | 85.28 s |
| C | Normal For Which (one-shot #1) | `.../normal-for-which-bridge/build_short.py` (217) | `normal-for-which-bridge/review-v1/bridge-short.timeline.json` (09-12 13:10) | 6 | 56.90 s |
| D | **Japan DOOR** | `.../japan-tariff-trick/build_short_door.py` (113) | `japan-tariff-trick/build-p58-door/japan-short.timeline.json` | 12 | 85.28 s |
| D' | Japan 2.5D | `.../japan-tariff-trick/build_short_p58.py` (123) | `japan-tariff-trick/build-p58-2-5d/japan-short.timeline.json` | 12 | 85.28 s |
| E | Calendar (one-shot #3) | `.../memory-trades-the-calendar/build_short.py` (382) | `memory-trades-the-calendar/build-oneshot-3/calendar-short.timeline.json` | 12 | 77.64 s |

**Coverage limit on C.** `normal-for-which-bridge/build-short/bridge-short.timeline.json` (mtime 09-15 21:47, 5
scenes, 69.78 s) is a later rebuild on the other take, **not** the 09-12 one-shot: three of five pages carry
`enter: null` and there is no plate row, while the live `build_short.py:112` authors a bridge plate with
`ken=(0.04, 0, -10)`. `review-v1/` was used. The served bridge build and its build script have drifted apart.

**D and D' in their own words.** `build_short_door.py:1-18` - "the same script, take, docks, captions, sound and
kinetics - with TWO changes": row 6 pinned to the approved flat `snap` (`:34`, refusal at `:56` if `depth=`/`plane=`
appear), row 7 `rows[6][5] = DOOR` (`:43,:59`), `HINGE = "right"` (`:33`, chosen off the 45.40 s frame so the door
opens away from the spotlit Detroit bar). `build_short_p58.py:1-19` - FOUR changes: layered `plate-ship` copy with 4
b-SAM planes, `TARIFF_CHART_ARRIVAL=camera` (`:36`), `;depth=1.15;plane=tilt:14,y` (`:43`), `;form=extruded_bar`
(`:45`).

## 3. Survivorship matrix - the 20 signature words

| mechanism | A 09-09 | B 09-10 | C 09-12 | D DOOR 09-15 | E 09-16 | carried forward? |
|---|---|---|---|---|---|---|
| **axes** | . | . | `s01:0.0`,`s02:10.89` (`build_short.py:86,98`) | . | x4 `s01/s05/s06/s08` (`:197,225,234,244`) | **YES - E only** |
| **mount** | `s02:1.99` (`:285`) | x3 (`:271,293,313`) | `s05` | x3 | `s04:16.91` (`:211`) | **YES (all)** |
| **spiral** | `s04:44.88` (`:338`) | . | `s04`,`s06` (`:115,136`) | . | `s11:67.82` (`:261`) | **YES - E** |
| **snap** | `s06` w/ `TOKYO_CAMERA=0` (`:420`) | `s02:1.82`,`s06:35.26` (`:256,285`) | . | same 2 (pinned `:34`) | . | **NO - last in D** |
| **throw-then-zoom** | . | `s01` `arrival:throw/paper` (`:243-248`) -> `s02` snap | . | **yes** | . | **NO - last in D** |
| **throw-then-push** | `s06:76.83` `page_enter:camera` (`:420`) | . | . | . (D': `s02`,`s06`) | . | **NO - last in D'** |
| **door** | . | . | . | **`s07:47.57 exit:door:right`** | . | **NO - D only, the only instance on disk** |
| **suck** | `s03` `suck:0.49,0.55` (`:328`) | . | `s01` (`:98`) | . | `s04` `suck:0.5,0.5` (`:213`) | **YES - E** |
| **dip** | x2 | x7 | x1 | x5 | x7 | **YES** |
| **cut** | x4 | x5 | x3 | x6 | x4 | **YES** |
| **card** | 6 docks (3 image/3 video; chart+deck+record) | 6 docks (image; chart+deck) | **0 docks** | 6 docks | 5 docks (**deck only**) | **YES, weakened** |
| **hold** | `s02` 36.97 s | `s08` 12.53 s | `s05` 13.95 s | `s08` 12.53 s | `s04` 13.79 s | **YES** |
| **rescale** | `chart_to:rescale` (`:311`) | . | . | . | . | **NO - A only** |
| **recast** | x2 (`:383,389`) | . | . | . | . | **NO - A only** |
| **park** | x3 (`:314,367,394`) | . | . | . | . | **NO - A only** |
| **unpark** | `:394` (back to `scale 1.0`) | . | . | . | . | **NO - A only** |
| **melt** | . | . | **`s04 exit:melt`** (`:126`) | . | **`chart_to compare, form:melt, then:splash`** (`:217`) | **YES - E (as compare melt); melt EXIT is C only** |
| **morph** | . | . | . | . | . | **NO - in no cut** (`cut=` -> `scripts/proof_chart_transitions.py:81`) |
| **remake** | . | . | . | . | . | **NO - in no cut** (`cut=` -> `scripts/render_baseline.py:253`) |
| **object-becomes-chart** | . | . | . | . | . | **NO - in no cut** (`cut=` -> `build-p61-planted/build_planted.py:119-133`) |

## 4. Survivorship matrix - the polishes

| polish | A | B | C | D | E | carried forward? |
|---|---|---|---|---|---|---|
| **electric inks (E67, CAPABILITIES:34)** | crimson x5, cobalt x2 | crimson x9, teal, deemph | crimson x5, deemph | = B | crimson x11, teal x5 | **YES - engine-level.** `samples/scene-evidence-engine.mjs:6323` `PAL = { crimson:"#e5484d", teal:"#1fa892", cobalt:"#4a7fd6" }`; all five build dirs' `player.html` carry `#e5484d`. **The approved 09-06 Tokyo render predates E67 (09-12).** |
| **held light / spotlight** | x1 (`:303`) | x4 | x1 | x4 | **x8** | **YES - E heaviest** |
| **badge rail (page badges)** | 3 on `s05` | 1+1 | none | 1+1 | 1+2 | **YES.** No cut uses a *dock* badge rail; E states `"no badge rails at 9:16 (B3, generalised)"` (`:84`) |
| **ticker** | **`s03:39.16`** (`:331`) | . | . | . | . | **NO - A only** |
| **compare melt** | . | . | . | . | `s04` (`:217`) | **YES - E only** |
| **verdict wall (`dock_payload:stack`)** | . | . | . | . | . | **NO - in no short** (only `steel-and-paper/build-f`) |
| **ring (`species:ring`)** | . | . | **`s06:66.99`** (`:140`) | . | . | **NO - C only.** E's ROW_PLAN (`:284`) records the ring was cut (the punch took the title off, M43) |
| **plate life, Ken Burns + drift (E99 s65)** | scale 0 x7 | 0 x12 | **0.04** on the one plate (`:112`) | 0 x12 | **`KEN=(0.06,6,-4)`** x5 (`:61`,`:194`) | **YES - E only** (`plate_option:ken` fires 5x in E, 1x in C, 0 in A/B/D) |
| **named idle (E49)** | `life` on outro only | drift x5, live x6 | - | = B | drift x5, live x6 | **YES, B onward** |
| **caption style** | phrase / stage+anchor | same | same | same | same | **YES (identical)** |
| **sound cue map** | 9 cues (`:454-472`) | 4 | 7 (`:150-173`) | 4 (derived + **compared**, never rewritten - `build_short_door.py:12-14`) | 3 (`:305-317`) | **YES but thinning 9->4->3** |
| **outro + brand line** | `s07` `outro-v2`+`life` (`:444`) | `s12` (`:322`) | **absent** | `s12` | `s12` (`:266`) | **YES** |
| **2.5D depth planes** | . | . | . | . (D refuses them, `:56`) | . | **NO - D' only:** `s05.world.layers` = 4 planes k 1.0/1.15/1.275/1.4 |

Kinetics flags identical across all five: `idle, stop_action, arap_morph, analytic_spring, min_jerk, area_squash,
curvature_stroke = true`; **`km_ink: false`**; `camera: true` in A/C/D/D'/E (absent in B). E alone adds
`span_tone:"dark"`, `span_alpha:0.3`.

## 5. The two short lists

**D (door) carries that Tokyo does not:** (1) `door:<hinge>` as an authored exit - `s07:47.57`, the only instance
anywhere; (2) a named idle on all 12 worlds (Tokyo: `life` on the outro alone); (3) two throw-then-zoom pairs
(`arrival:throw`/`mass:paper` at `s01`,`s05` -> `page_enter:snap` at `s02`,`s06`); (4) a plate-led world grammar (5
plates + 2 clips vs 1+2), with the dip as the primary world change; (5) a dense pointing layer - `trace` x6,
`callout` x6, `spotlight` x4 vs 1/2/1 - incl. the crossings map's six hops and six stamps (`build_short.py:267`); (6)
the light on the picture, never a ring (`:293-305`); (7) measured `centre`/`card_aspect`/`centre_x/y/w` on both story
docks.

**E (one-shot #3) carries that D does not:** (1) `enter=axes` x4 - the open *is* the chart; (2) directional plate
life `KEN=(0.06,6,-4)` on all 5 plates (D's ken is `(0,0,0)` x12); (3) the compare melt - `chart_to compare / form
melt / then splash / hold gone` (D carries no `chart_to` at all); (4) `peel` (`:229`), `span` (`:248`), `retitle` x2,
and a **share/donut** page variant (`:225`) - D has only line+bars; (5) spiral return (`:261`) and suck exit
(`:213`); (6) a written **BEAT PLAN** - `ROW_PLAN` (`:273-289`) gives every beat an act, a `compared_to` comparator,
a capability list and a recipe or explicit `why_none`, emitted to `<build>/BEAT-PLAN.jsonl` for M41; plus
`CRITIC.md` and `SELF-WATCH.md`; (7) 8 spotlights vs 4, 3 page badges vs 2.

**What E loses vs D** (matters, since D is the operator's pick): no card arrival of any kind (no `arrival:throw`, no
`page_enter:snap`, no `page_enter:camera`), no chart-card dock (`dock_payload:chart` absent - deck only), no door, no
melt exit, no `species:trace`, 3 sound cues vs 4 vs Tokyo's 9.

**Rank for the shape compiler:** (1) universal - mount, dip, cut, hold, card, phrase captions, inks, outro, named
idle. (2) latest-two - idle on every world, page badges, plate-led worlds, light-not-ring. (3) E only - axes, Ken
Burns plate life, compare melt, peel/span/share, beat plan. (4) **the regression** - rescale/recast/park/unpark/ticker
(A only, dropped since 09-10). (5) once each - door (D), melt exit (C), ring (C), 2.5D (D'), throw-then-push (A, D').
(6) never shipped - morph, remake, object-becomes-chart, verdict wall.

## 6. Memory audit - counts

89 memory files in `C:/Users/Snipe/.claude/projects/C--Users-Snipe-Downloads-Outreach-Program/memory/`. Searched
doctrine first (`docs/portable/OPERATOR-RULINGS.md`, `docs/content-video-engine/CAPABILITIES.md`,
`docs/GATES-REGISTRY.md`, `docs/ANIMATION-REGISTRY.md`, `docs/CRAFT-MAP.md`, `docs/portable/DOCTRINE-CORE.md`), then
the rest of `docs/` **excluding** `docs/agent-memory/**` and `docs/research/**`.

`docs/agent-memory/operator/` mirrors **75 of 89**; excluded deliberately - a mirrored memory reaches an agent
through `docs_find` but is not a ruling, a CAPABILITIES row or a gate, so it never reaches the compiler or the
critic. **14 are not even mirrored** (drift since the last `sync_operator_memory.py --export`):
agent-turn-limits-opus, check-rulings-before-asking, field-entry-by-job, frames-inward-not-tokens-outward,
generated-images-stay-out-of-git, name-the-short-not-the-bridge, no-paid-generators, one-shot-lessons-2026-09-16,
pathspec-commit-never-records-deletions, plate-life-is-directional, proof-is-a-scene, rebuild-is-not-a-base,
throw-then-zoom-light-never-the-move, visible-difference-and-local-life.

| bucket | n |
|---|---|
| RULING / CAPABILITIES / GATE (binds compiler, critic, dispatched agent) | **55** |
| DOC only (a doc/runbook carries it; no ruling) | **17** |
| EPHEMERAL by design (`resume-*` x3) | **3** |
| **NOT IN THE RECORD** | **14** |

### In the record - representative citations (55 rows)

animators-loop-p51 -> `OPERATOR-RULINGS.md:2015-2016` + `CAPABILITIES.md:94` . caption-energy-lessons ->
`OPERATOR-RULINGS.md:2732` + `BACKLOG.md:192` . channel-structure -> `DOCTRINE-CORE.md:26` .
chart-form-rulings-e50-e53 -> `GATES-REGISTRY.md:139` (M21/E50) . chart-proof-not-homework ->
`GATES-REGISTRY.md:131` (M12/E25) + `29-EVIDENCE-MOTION-STANDARDS.md:2058` . chart-reads-at-a-glance-e28 ->
`OPERATOR-RULINGS.md:835` . check-rulings-before-asking -> `:2903` . comfy-local-models-layout ->
`CAPABILITIES.md:145` . composite-effects-keep-every-phase -> `CAPABILITIES.md:189` . dip-is-a-world-change ->
`CAPABILITIES.md:70` + `ANIMATION-REGISTRY.md:729` . docs-layers-and-registries -> `CAPABILITIES.md:203` .
field-entry-by-job -> `OPERATOR-RULINGS.md:3165` (E99 s35) . first-pass-additive-capability-led ->
`GATES-REGISTRY.md:159-163` (M36/M37/M40) . flow-driver-traps -> `CAPABILITIES.md:159` + `OPERATOR-RULINGS.md:1850`
. flow-driving-consent -> `:1177` . flow-stills-first-image-to-video -> `:1246` (E40) .
frames-inward-not-tokens-outward -> `:3258` (E99 s70) . gate-fit-mangles-prose -> `:1273` (E41) .
generated-images-stay-out-of-git -> `:3094` (E99 s31) . gpt-image-2-5-generator -> `:2862` . japan-tariff-trick-v1
-> `:1810` . judge-the-frame-not-the-diff -> `:2300` . judging-is-codex-cli-batch -> `:1193` .
ledger-page-signature -> `CAPABILITIES.md:56` (E22) . mp-host-identity -> `CAPABILITIES.md:181` .
name-the-short-not-the-bridge -> `:3139` . never-pipe-gated-steps-to-tail -> `CAPABILITIES.md:282` .
no-paid-generators -> `:3185` (E99 s37) . nothing-ever-goes-truly-still -> `:1494` (E49) + `CAPABILITIES.md:71` .
one-shot-floor-recipes-not-events -> `GATES-REGISTRY.md:159-163` + `scripts/gate_one_shot_floor.py` .
one-shot-lessons-2026-09-16 -> `:3250` (E99 s66) . opening-minute-e24 -> `scripts/gate_opening_structure.py:397`
(G45) + `:749` . orphan-tracking-registry -> `ANIMATION-REGISTRY.md` . package-first-e27 -> `:743` .
plate-life-is-directional -> `:3248` (E99 s65) . production-standards-universal -> doc 29 . proof-is-a-scene ->
`:3238` (E99 s60) . rebuild-is-not-a-base -> `:3262` (E99 s72) . recall-before-propose ->
`docs/runbooks/RECALL-RECEIPT.md` + `CLAUDE.md` . recall-system -> `CAPABILITIES.md:1` . research-gate-tiers,
rings-retired-e56 (E56), steal-now, thresholds-from-the-reference (Wealth Logic), soak-ink-is-a-plate,
screen-never-still (E21 + `gate_motion_density.py`) -> `OPERATOR-RULINGS.md` . scml-ledger-evidence ->
`CAPABILITIES.md:227` . throw-then-zoom-light-never-the-move -> `:3260` (E99 s71) + `:3252` (s67) .
viewer-perception-test -> `:949` (E26) . visible-difference-and-local-life -> `:3194` (E99 s38) . voice-lane-split
(E70), worktree-read-scope, worktree-sprawl -> `:528` . youtube-retention-clock -> `DOCTRINE-CORE.md:51`.

### DOC only (17)

bravos-reference (`sources/reference_analyses/bravos-.../REPORT.claude.md`, doc 46 s46.7; `GATES-REGISTRY.md:163`
M40 cites "the reference measured at") . claude-md-imports-agents-md (**only `CLAUDE.md:3` at repo root**) .
codex-fulfillment-flow (`docs/runbooks/HEADLESS_CLAIM_RESUME.md`) . ear-writing-priorities (`DOCTRINE-CORE.md:82` +
`patterns/HIGHLIGHT-SESSION-2026-08-24.md` + doc 32) . fable-parent-opus-roles (`docs/AGENT_START_HERE.md:39` +
`docs/runbooks/PRP_EXECUTION.md`) . full-video-map-location (the file itself) . money-physics-brand-sheet (`:2537`
cites BRAND-SHEET) . notebooklm-omni-opener . operator-bio (doc 36) . p46-bridge-state (plan +
`docs/runbooks/WORK-ORDER-GEMINI-BRIDGE-SHAPES-2026-09-07.md`) . remotion-ui-registry (`REMOTION-UI-HARVEST.md`,
`REMOTION-UI-INTAKE-2026-09-07.md`) . review-link-frozen-copy (build docstrings/E45; no ruling row found) .
review-server-no-store (**code only**, `scripts/serve_player.py`) . script-changes-go-to-next-letter
(`REWRITE-ORDER-*.md`; `:2963` approves one instance, not the rule) . shorts-lane-brand-essence .
shorts-lane-phase1-standard . three-lane-harness (`WORK-ORDER-GEMINI-PROFILES-2026-09-05.md` + AGENTS.md section 9) .
tokyo-short-render.

### NOT IN THE RECORD - the gap (14)

| memory | claim | in the record? |
|---|---|---|
| ai-baselines-operator-corrects | never hand the operator a work item; ship a completed draft they correct | **NO** |
| our-artifacts-beat-outside-advice | grep our own artifacts before recording a tutorial - or my recollection - as fact | **NO** as a rule (only `DOCS-INDEX.md:3367`, one settled instance) |
| gate-extraction-orders | an on-disk extraction order ships with a mechanical `--verify` gate, small chunks, a coverage table, no crib | **NO** |
| ep1-lifetime-curve | all of ep1's loss is the first 90 s; flat 40-48 % 2:00-11:00 | **NO** |
| search-intent-cohort | broad topical search bounces at 9 % viewed, intent search 96 % | **NO** |
| local-whisper-no-paid-stt | Whisper runs locally; never a paid STT | **NO** - only code comments that cite the memory (`scripts/align_take.py:9`, `align_take_whisper.py:11`) |
| install-permission | standing permission to install anything improving performance/testing/animation | **NO** |
| open-local-apps-yourself | launch the local app yourself; never ask the operator to click | **NO** |
| agent-turn-limits-opus | maxTurns raised 09-15 (explorer 120, luna 200, steward 60); no "Turn budget" lines | **NO** (`maxTurns` in no doc) |
| pathspec-commit-never-records-deletions | `git commit -- <paths>` drops staged `git rm --cached` deletions | **NO** |
| gitignored-artifacts-live-in-worktree | which build inputs git does not carry and where they live | **NO** (an aside in `STUDIO-READINESS-REVIEW-2026-09-13.md`) |
| file-links-never-open | the app resolves file links against the main checkout; deliver over localhost | **NO** |
| claude-login-google-account | the subscribed Claude account is the Google login | **NO** |
| cause-outcome-brevity | lead with cause -> outcome -> impact, one line each | **NO** |

**The five most important NOT rows:** (1) `ai-baselines-operator-corrects` (governs the shape of every deliverable;
every new agent re-learns it by being corrected). (2) `our-artifacts-beat-outside-advice` (the general form of
`recall-before-propose`, which *is* in the record - its absence is exactly the failure E99 s70 named on 09-17). (3)
`gate-extraction-orders` (without it the next ungated order repeats 13/14 invented paths). (4) `ep1-lifetime-curve` +
`search-intent-cohort` (the only retention evidence we own; the rulings are in the record, the evidence is not). (5)
`local-whisper-no-paid-stt` (a spend rule enforced today only by two code comments that cite the memory). Honourable
mentions: `agent-turn-limits-opus`, `pathspec-commit-never-records-deletions` - both have already cost a run and live
nowhere durable.

## 7. Coverage limits

Roots searched: `docs/` (excluding `docs/agent-memory/**`, `docs/research/**`), `content/video_engine/scripts/`, the
six doctrine files, the five projects' build dirs. `.claude/PRPs/plans/` only where a memory named a plan.
`content/video_engine/sources/reference_analyses/` reached via `docs_find` only. Absent rows in sections 3/4 mean "no
such card in that compiled timeline", not "the engine cannot do it" - all 20 signature words have a LIVE/WIRED
`record=`.
