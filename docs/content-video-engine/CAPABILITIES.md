# CAPABILITIES — what is already built

**Check this file before building anything.** Three asset classes were
rediscovered in one session (2026-08-29) — the curtain-era wipe grammar, the
typewriter record document, the live chart draw — each rebuilt or nearly
rebuilt because nothing indexed what existed. The plate library indexes
plates; the choreography ledger indexes motion events; this file indexes
**capabilities** — renderers, engines, gates, prototypes.

Format: what it does · where it lives · state · proof. Update it in the same
commit that adds or retires a capability. A capability that is not in this
file will be rebuilt by someone who doesn't know it exists.

## Rendering & playback

| Capability | Where | State | Proof |
|---|---|---|---|
| **Scene-evidence player** — the review renderer: cross-reveal wipe with carried light, coalesced docks, snap-to-boundary, dock-owned sides, interval wash, finance geometry (864/1056), one-baseline spring pills, text-tier palette | `docs/content-video-engine/samples/scene-evidence-player.template.html` | LIVE — the lane | Steel and Paper build F |
| **Record-document species** — typewriter + per-word highlighter, stroke synced to the NARRATOR's word timings | template (`drawRecord`) + prototype `steel-and-paper/evidence/prototypes/record-document-motion.html` | LIVE (Karp wired); leases/macdonald await payloads | 3:10 in build F |
| **Live-chart species** — the ANIMATED EVIDENCE LAYER: line draw (+area fill revealed with the line), BAR charts (staggered grow, notes land with bars), two-panel small multiples, annotation MARKS that land when the line reaches them, reference hlines (list, per-color), SHARES proportion bars (the fill IS the claim - replaces the banned stat-tile species) — all from `.series.json` sidecars emitted by the chart builders from the same data as the PNGs (PNG = fallback + review artifact) | template (`drawChart`) + `emit_sidecar` in both evidence builders | LIVE — 10 of 10 charts draw themselves; narration-keyed draw binds post-re-record | railway marks 1:27, capex bars 4:46, tnx panels 2:14 |
| **Narration-keyed chart draw** — DRAW_KEYS bound to word timings ("the crash lands on the words") | prototype `evidence/prototypes/data-document-motion.html` | BUILT, unwired — binds after re-record | prototype replays |
| **Kinetic + quiet captions** — word-punch groups at canonical timings; quiet mode under any docked evidence | template + `caption-pages.json` from the words sidecar | LIVE | doc 29 Part 5 |
| **Caption STAGE mode** — when no dock is up the caption IS the motion: centred at 40% in the plate's quiet zone (a ledger page's declared zone), 64px/800, each word pops at its own spoken time (scale 1.16→1.0, alternating ±2.5° tilt); a live dock demotes it to the anchor via `quiet`. The build stamps `cap_mode` per page and declares `caption_modes`; gate M08 counts stage pages as events and FAILs a declaring build's bare >12s stretches | template `#caption.stage` + `build_scene_timeline_f.py` (`_dock_live_at`) + `gate_motion_density.py` M08 | SHIPPED 2026-09-03 (P34 T5) — Human Gate 2: the operator picks from the 3:11–3:31 stage-vs-anchor side-by-side before it is the default | doc 29 §9.25 "Shipped"; ep1 rebuilt: 110 stage / 354 anchor pages |
| **LEDGER PAGE species** — the channel signature (E22): a world plate that IS a chart. `world.kind == "ledger"` + `world.page` (a `ledger_page.v1` spec): plain cream page rolls out (a GENERATED washi plate via `page.plate`; CSS cream is the fallback) → half savor → the FIELD (generated inked plate cross-faded via `page.field_plate`; fallback `page.field` = scribble strokes with a nib, or soak) fills the board to a definite rounded edge → the outline draws EXACTLY on that edge → ink writes title/source per glyph (seeded tilt) → the crisp build: story bars landing on the exact value strings with the accent callout, or the dense line (dash-offset, tip head, de-collided inline names). All from `t`, seeded by `lpHash`; identical stage hash from any seek order | template (`const LP`, `buildLedger`/`paintLedger`; the species block only) + `scripts/ledger_page.py` (series.json → spec; builder by data shape; values verbatim) + shot row `ledger:<series>:<variant>[:<emphasize>[:<quiet_zone>]]` (`world_for_plate`) | BUILT 2026-09-03 (P35 T3/T4) — Human Gate 1 (the pick) and the plate contact sheet (claim `steel-and-paper-ledger-page-v1`) are the operator's; refused on sight: blob bleed, ink/outline gap, coffee stains, uneven halo, fibre | proof `build-f/ledger-species-proof.html`; doc 29 §9.26 + E22 addenda; hyperframes candidates `compositions/ledger-page-v1-{A,B,C}.html` |
| **Motion-density gate, WIRED** — E21 on the built timeline: M01 no stretch >12s without a visual event, M03 evidence ≤45s apart, M04/M05 plate density and hold, M06 caption cadence, M07 the opening minute never the thinnest, M08 stage captions; dock events from the timeline's OWN `scenes[].docks` (evidence-dock.json sat on an older clock); page beats count as events, page start as an evidence entry. The build writes `build-f/GATES-MOTION.md`; `render_episode.py` refuses a FULL render on FAIL (exit 2) unless `--force`; slices and shards never block | `scripts/gate_motion_density.py` (`write_report`) + `build_scene_timeline_f.py` + `render_episode.py` | LIVE (P34 T4, P35 T4) — ep1 baseline 5 FAIL (M01 15% still, M03 54s, M05, M07, M08 six dock-held/silent stretches) | `build-f/GATES-MOTION.md`; tests `test_gate_motion_density.py`, `test_motion_gate_wiring.py` |
| **Surface grammar + census** — page vs dock vs plate-life vs none, decided by rule (A1–A3 earn the page, B1–B4 keep the dock, C1–C6 choreography at a boundary, D1–D4 the E21 density link); the ep1 census classifies all 75 shot rows with rule letters and a builder | doc 29 §9.28; `build-f/SURFACE-CENSUS.md`; CHECK-RESPONSIBILITIES §3g | LIVE (P35 T0) — the re-script's shot table starts from the census | 6 pages / 49 docks / 4 plate-life / 14 none; 4 defect rows |
| **Page sound cues** — paper slide (roll-out), drop settle (bleed), chalk stroke (outline draw-complete): CC0 Freesound, trimmed ≤1.5s, matched to the whoosh at −14 LUFS ±1 LU; page-relative `page_cues` in SOUND-PLAN (the `cues` list is flattened onto the episode clock by the mixer) | `sound/fs-page-*.mp3` (gitignored) + `sound/SOURCES.md` + `configs/sound_palette.json` | BUILT (P35 T9) — no CC0 ink sound under 4s exists; the bleed slot is a water drop, flag at the contact sheet | loudness table in SOURCES.md |
| **Choreography ledger + gates** — every enter/exit/side/how-it-leaves, gated per slot; FAIL blocks the build | `content/video_engine/scripts/emit_choreography.py` → `build-f/CHOREOGRAPHY.md` | LIVE — constants mirror the template; change together | caught tnx re-landing on first run |
| **Whiteboard reveal engine** — serpentine SVG mask + hand follower, pose set with per-pose nib calibration | git history `7880c01`, `1e6612f`; poses `hyperframes/assets/hands/` + `nib-calibration.v1.json` | RETIRED from this lane (doc 29 8.17) — earns its place when artwork is drawn, not sourced | doc 29 8.10–8.16 |
| **Remotion Production Console** — local timeline/canvas editor + Python bridge (`127.0.0.1:4317`): scrub/zoom/drag/trim, hash-bound immutable revisions, recompiles without touching narration or evidence approvals; semantic-evidence binding tests | `content/video_engine/production_console/` + `configs/production_console_snapshot*.schema.json` (merged from p31, 2026-08-29) | BUILT — the doc 29 §9.3 production route | P29/P31 gate screenshots in `.claude/PRPs/evidence/` |
| **Remotion composition registry** — single source of truth for editor compositions (Editorial, Documentary, motion variants, finance proofs, production evidence/timeline, 3D prototypes) | `content/video_engine/editor/src/compositions.ts` | LIVE — register here, never in Root.tsx | typecheck + vitest |
| **Editor fixtures** — editorial-motion two-shot with render harness (`render.mjs`), canonical audio fixture | `content/video_engine/editor/fixtures/` (merged from p16) | BUILT | `npm run render:editorial-motion-fixture` |
| **remotion-ui registry** (external, MIT) — ~200 copy-in `.tsx` components: captions, data/live metrics, SVG draw-on paths, TransitionSeries transitions, motion primitives; MCP server (`npx remotion-ui-mcp`) exposes list/search/detail/install to agents | github.com/riaz37/remotion-ui · remotionui.com/docs/components/browse | MCP INSTALLED (.mcp.json, loads on session start); registry index + 8 key components read; THREE techniques already ported into the review player (feathered wipe edge, under-wipe parallax, active-word caption pop). Their EASING.pop == our badge spring — same motion school. Full sweep when the Remotion port opens | port commit 2026-08-30 |
| **Hyperframes** — production vector animation (alpha overlays, compositions); Remotion port path | skills in codex worktree `f10b/.agents/skills/hyperframes*`, assets `content/video_engine/review/hyperframes_assets` | BUILT, not in the review loop — PLANE ONE, preserved by operator decision 2026-08-30: hyperframes-first stays alongside the Remotion plane while the hand-built editor works out its kinks | pinned CLI renders alpha natively (doc 29 Part 7) |

## Evidence & assets

**Martial Matters episode 1** (merged from p16, 2026-08-29): 192 asset files
(1080p plates), recorded narration + word timings
(`projects/martial-matters/.../transcript/narration.words.json`), the
Marshall Monday editing handoff. The third channel's pilot — indexed in the
plate library under channel `martial-matters` (2026-08-29), semantics from
the word-timed cue ledger, state `candidate` until an approval manifest is
read.


| Capability | Where | State | Proof |
|---|---|---|---|
| **THE RAILWAY YARDSTICK** — recurring channel instrument: tech share of ALL US capital formation (narrow 28% all-time high vs 23% dot-com; broad 65%; UK railways ~50% one-technology reference); quarterly updater + dated readings log | `content/video_engine/instruments/railway-yardstick/` | LIVE — operator-adopted 2026-08-30; tripwire pending operator decision | readings.jsonl seeded |
| **Plate library** — 326 plates indexed by SEMANTIC across all worktrees and CHANNEL-AWARE (money-physics 134 / martial-matters 192); channels are identity walls — the resolver refuses cross-channel plates; status from manifests, never paths | `content/video_engine/scripts/build_plate_library.py` → `sources/PLATE-LIBRARY.json` | LIVE — rebuild after any plate wave | resolver falls through to it |
| **Chart builders** — real-data charts (yfinance/FRED), verbatim end labels, month/year axes, series sidecars | `steel-and-paper/evidence/build_evidence_documents.py` (+ railway, HBM builders) | LIVE | ev-divergence-v1 |
| **Live HTML evidence sources** — karp/leases/macdonald records, instrument-memory, mechanism-ladder, three-manias | `steel-and-paper/evidence/*.html` | BUILT — PNGs are flattened renders of these | files on disk |
| **Teacher-stamped catalog** — 86 production slides keyed `image_id` → `extracted_path` | `sources/decks/teacher-stamped-production-visuals/` + manifest (MAIN checkout) | LIVE | episode-build skill §5 |
| **Two-tier palette** — graphic tier for lines/fills, lifted text tier for numerals on dark pills | template `:root` + BUILD-PIPELINE.md | LIVE — never graphic-tier text on dark | contrast 5.7–7.4:1 measured |

| **VERDICT STACK species** — N proofs fly in from depth over the world plate, word-matched; hyperframes focus hand-off (active card LARGE center-stage for its phrase, recedes to rail on the next beat); radial burst on the pivot | `samples/scene-evidence-player.template.html` (stackbox / drawStack; dock species `stack`, member ids resolve against asset-data) | LIVE — nine-proof wall at s67-70, operator-approved | doc 29 §9.24-9.24b |
| **Chart self-containment gates** — auto-fit checklist columns, skew-pivot highlighter sweeps, nowrap pills, mark backing chips + dotted leaders, named reference series, log-chart date ticks, header shrink-then-squeeze, recap fill (sub-12s checklist hold = 0.8s/row) | `samples/scene-evidence-player.template.html` (template-enforced, every chart inherits) | LIVE — mute-the-narration test is the acceptance gate | doc 29 §9.23 |

## Script & voice

| Capability | Where | State | Proof |
|---|---|---|---|
| **Strength loop** — multi-scale fixpoint (L0–L6 + X1–X5), rewrite budget, oscillation escalation | `patterns/STRENGTH-LOOP.md` + script-writer skill | LIVE | Script F |
| **Doctrine audit + pattern lint** — timed gates from text via dual rate estimators (16.29 c/s, 170.9 wpm) | `scripts/audit_script_doctrine.py`, `lint_script_pattern.py`, `kit_spec.py` | LIVE | |
| **Opening-structure gate** — G01–G44 + J01–J11: the doc-38 / P1 / P2 shape as a real gate (3s grab, 8s paradox, "you" by 0:30, mini-payoff then the promise by 0:60, A1/A2/A3 with A3 = 10% of runtime (E23), classical nodes as DECLARED beats via `beat_tags.py` — archetype, desire, opponent, map, catalyst, debate, signpost, head-fake, loop/loop-close, tricolon, anaphora, reflect, dip — G36 the retention cycle over the WHOLE runtime, G44 one rehook per unit, G34/G35 concession + hedge, JUDGE rows printed never passed) | `scripts/gate_opening_structure.py` + `beat_tags.py` + `kit_spec.a3_anchor_s` / `unit_windows` | LIVE — ep1 baseline 27 FAIL (promise at 1:20, no declared beats, G36 352s from 7:33, G44 unit 4) | `tests/test_gate_opening_structure.py`; CHECK-RESPONSIBILITIES §2 |
| **Script-gate RUNNER + recording refusal** — ONE command runs lint → audit → opening gate → screens through each tool's own `main()`, writes `<script>-GATES.md` (the §5 TOOLS block, every stdout verbatim, `script_hash` of the spoken text, `VERDICT`), exit 1 on any FAIL; both recorders REFUSE a missing / stale / FAIL report (`--force "<reason>"` records and logs the reason into the take manifest); the audit defers doc-38 beats 1–4 to the gate when the report exists (one row, one verdict) | `scripts/run_script_gates.py` + `record_chained_take.py` / `record_master_take.py` + `audit_script_doctrine.py` (`_doc38_opening`) | LIVE (P34 T1/T6) — ep1's promise-at-1:20 could not have been recorded | `steel-and-paper/SCRIPT-G-GATES.md`; `tests/test_run_script_gates.py`, `test_audit_defers.py` |
| **Declared-beat enumeration** — `<script>-SCREENS.md` gains a DECLARED section: every beat tag with its clock, the gate's window verdict, the sentence under it and a blank verdict column the agent fills true / laundered (rule R2 is enumerated, not remembered) | `scripts/enumerate_strength_screens.py` (`build_screens`, `--timeline/--ring/--counterparty`) | LIVE (P34 T3) — ep1 declares zero beats | `tests/test_enumerate_declared_beats.py`; STRENGTH-LOOP §8a |
| **Recorder preflight** — 16 gates: split-on-pause, tag cap, paragraph density, stacked pauses, credits-for-both-parts | `scripts/record_chained_take.py` | LIVE — both new gates FAIL on the take that shipped bad | doc 37 |
| **Pause compilation** — marks → break tags, backticks consumed, dirty-tag guard RAISES | `src/services/audio_synth.py` `compile_pause_marks` | LIVE | the 0:08 artifact class is unshippable |
| **Scratch take (stage zero)** — free full-script render before any credit: Chirp 3 HD (fast listen, key in local.env) + Kokoro-82M local (word timestamps, jump index, real chars/sec) | `scripts/scratch_take.py` | LIVE | doc 37 §16; Kokoro hook timing 1.8% off the EL take |
| **Tempo field edit** — one-pass PCM edit: dead-space caps, tighten runs, pauses, and a continuous tempo curve (speed limits at reveal anchors, 1.10x cruise, 1.6s ramps; words never split, cuts only in silence gaps) | `scripts/tempo_edit.py` | PROVEN on the probe (operator: "This is it"); chain promotion = warped-timeline emission | doc 37 §20 |
| **Checklist species** — live procedural cards: rows land narration-keyed; question cells TYPE on, answer cells take a marker-highlight sweep (technique ported from remotion-ui: cap-height band, chisel-tilt edge); per-row status colors | template `C.checklist` + build-time `narration_key_delays` | LIVE — test scorecard, tripwire board | doc 29; f428993+ |
| **SCML monitor cards** — the ledger's instruments as evidence: tripwire board (FRED DFF vs Bravos' 5.50 trigger + memory trigger, contagion status verbatim) and the memory monitor (customs $/kg m/m readings) | `ev-tripwire-board-v1`, `ev-memory-monitor-v1` | LIVE | s60-s62 |
| **Whisper gate** — transcribe the take blind, diff vs script; FAIL on insertions/deletions, WER > 5% | `scripts/verify_take_whisper.py` (faster-whisper base.en) | LIVE — caught a real vocalized tail tone on its FIRST run | doc 37 §12; Script G take |
| **Defended join** — part-1 tail faded to silence after last word + generated settle; provider-appended junk dies by construction | `scripts/join_chained_take.py` | LIVE — seam measures −91 dB | doc 37; Script G |
| **Edit-pause insertion** — the ~3-tag practice's owed silences cut into the take at verbatim anchors; timeline shifted | `scripts/insert_edit_pauses.py` | LIVE — 15 pauses, +15.0s | Script G |
| **Retime pass** — docks pin to anchors' new word times; plates warp between control points; same-slide gaps stitch | `scripts/retime_to_take.py` | LIVE — 32 pins; MUST be followed by the topic-exit audit (durations carry, topics move) | Script G |
| **Caption pages regen** — ~3-word kinetic pages with k-flags from the current timeline | `scripts/build_caption_pages.py` | LIVE | 832 pages |
| **Topic-exit audit** — E11 enumeration of every dock vs the narration it serves; exits authored to topic ends | `build-f/TOPIC-EXIT-AUDIT.md` procedure (doc 29 §9.20) | STANDING — runs after every retime or script change | 47 docks walked 2026-08-30 |
| **Choreography clash gates** — same-slot overlap + >2 concurrent docks FAIL | `scripts/emit_choreography.py` | LIVE — caught a real slot clash on first run | |

| **Pause grammar, GENERATIVE** — scans the VO for grammar classes (stat-settle→era-shift FULL; snap settles / era breaths / reveal leads HALF), diffs against the standing plan; run before every master record | `scripts/derive_pauses.py` | LIVE — Script G: 18 candidates, 1 operator full + 7 ratified halves | doc 37 §19b |
| **Micro-repair** — sub-word provider stutters excised free: envelope-localize, fade-free preview candidates, zero-cross butt splice, words.json shifted, verify from the EDITED master | `scripts/repair_microcut.py` | PROVEN — 'Builted it' two-round fix | doc 37 §23-23c |
| **Stutter auto-scan** — NEGATIVE result, do not rebuild: three envelope detectors all failed validation against the known case; ear detects, envelope localizes | (tool deleted by design) | CLOSED | doc 37 §23b |

## External evidence sources

| Source | Where | Gives | Rule |
|---|---|---|---|
| **SCML ledger** — the operator's Korea/memory intelligence base | `~/.claude/Claude Work/Claude Files/scml-ledger/scml-ledger/data/scml.db` | DART-filed financials (cross-validate Yahoo to the won), USDKRW series, **memory export tracker** (customs value-per-kg — primary-source "sold out" pricing), short interest, NPS flows, catalyst calendar | read-only for evidence; .env keys never printed; cite as "cross-checked vs DART filings" |

## Reference builds (locked)

| Reference | Where | Governs |
|---|---|---|
| **current-bubble-five-minute-v4** | `samples/current-bubble-five-minute-v4.timeline.json` (+ rendered build) | THE motion gold standard (doc 29 §9.16) — side-by-side before any motion change ships |
| **Gemini showcases** | `samples/gemini-decoupled-evidence-showcase.html`, `gemini-scene-evidence-pipeline-showcase.html` | ancestor artifacts — where doctrine CAME from; a reviewed refinement outranks them |

## The recall rule

1. `ls` and read the index before searching (PIPELINE.md, this file, PLATE-LIBRARY, CHOREOGRAPHY).
2. When a doc cites a source artifact, the audit reads the artifact.
3. A capability added or retired updates this file **in the same commit**.
