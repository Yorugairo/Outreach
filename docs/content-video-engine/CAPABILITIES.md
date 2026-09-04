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
| **Caption STAGE mode** — when no dock is up the caption IS the motion: centred at 40% in the plate's quiet zone (a ledger page's declared zone), 64px/800, each word pops at its own spoken time (scale 1.16→1.0, alternating ±2.5° tilt); a live dock demotes it to the anchor via `quiet`. The build stamps `cap_mode` per page and declares `caption_modes`; gate M08 counts stage pages as events and FAILs a declaring build's bare >12s stretches | template `#caption.stage` + `build_scene_timeline_f.py` (`_dock_live_at`) + `gate_motion_density.py` M08 | LIVE 2026-09-03 (P34 T5) — operator's pick on the side-by-side: STAGE is the default ("awesome") | doc 29 §9.25 "Shipped"; ep1 rebuilt: 110 stage / 354 anchor pages |
| **LEDGER PAGE species** — the channel signature (E22): a world plate that IS a chart. `world.kind == "ledger"` + `world.page` (a `ledger_page.v1` spec): plain cream page rolls out (a GENERATED washi plate via `page.plate`; CSS cream is the fallback) → half savor → the FIELD (generated inked plate cross-faded via `page.field_plate`; fallback `page.field` = scribble strokes with a nib, or soak) fills the board to a definite rounded edge → the outline draws EXACTLY on that edge → ink writes title/source per glyph (seeded tilt) → the crisp build: story bars landing on the exact value strings with the accent callout, or the dense line (dash-offset, tip head, de-collided inline names). All from `t`, seeded by `lpHash`; identical stage hash from any seek order | template (`const LP`, `buildLedger`/`paintLedger`; the species block only) + `scripts/ledger_page.py` (series.json → spec; builder by data shape; values verbatim) + shot row `ledger:<series>:<variant>[:<emphasize>[:<quiet_zone>]]` (`world_for_plate`) | LIVE 2026-09-03 (P35 T3/T4) — the field DECIDED: on the cream ground the charcoal fills the generated page to its DECKLE and the line is the deckle's innermost rectangle (`page.field_plate` + `page.board`; `edge_path` optional); then PUNCH IN on the board, the build on the punched page, and the page's declared FOCUS action (callout / spotlight / punch) on the datum at the build's end (E22 addendum 6, E25: the page ends pointing at the proof); refused on sight: blob bleed, ink/outline gap, coffee stains, uneven halo, fibre | proof `build-f/ledger-species-proof.html`; doc 29 §9.26 + E22 addenda; hyperframes candidates `compositions/ledger-page-v1-{A,B,C}.html` |
| **Motion-density gate, WIRED** — E21 on the built timeline: M01 no stretch >12s without a visual event, M03 evidence ≤45s apart, M04/M05 plate density and hold, M06 caption cadence, M07 the opening minute never the thinnest, M08 stage captions; dock events from the timeline's OWN `scenes[].docks` (evidence-dock.json sat on an older clock); page beats count as events, page start as an evidence entry. The build writes `build-f/GATES-MOTION.md`; `render_episode.py` refuses a FULL render on FAIL (exit 2) unless `--force`; slices and shards never block | `scripts/gate_motion_density.py` (`write_report`) + `build_scene_timeline_f.py` + `render_episode.py` | LIVE (P34 T4, P35 T4) — ep1 baseline 5 FAIL (M01 15% still, M03 54s, M05, M07, M08 six dock-held/silent stretches) | `build-f/GATES-MOTION.md`; tests `test_gate_motion_density.py`, `test_motion_gate_wiring.py` |
| **Surface grammar + census** — page vs dock vs plate-life vs none, decided by rule (A1–A3 earn the page, B1–B4 keep the dock, C1–C6 choreography at a boundary, D1–D4 the E21 density link); the ep1 census classifies all 75 shot rows with rule letters and a builder | doc 29 §9.28; `build-f/SURFACE-CENSUS.md`; CHECK-RESPONSIBILITIES §3g | LIVE (P35 T0) — the re-script's shot table starts from the census | 6 pages / 49 docks / 4 plate-life / 14 none; 4 defect rows |
| **MOTION MENU species** — the targeting law as code: shot rows carry `species` entries with DECLARED targets (datum \| point \| region \| span); `validate_species` fails the build on a pointing species without a target or two camera moves in one window (gate M09 mirrors it); the player resolves targets at render time. Shipped: plate life (10 fps stepped, squash on land, seeded boil, our cutouts), camera punch / focus zoom / pull-back (one world transform, docks fixed), scribble callout, feathered spotlight glide, squiggle under caption spans. Not yet: beat-freeze exit, radial reveal, push hand-off, weight-shift captions | template (`const SP`, `resolveTarget`, `paintSpecies`) + `build_scene_timeline_f.validate_species` + `gate_motion_density.py` (SPECIES_EVENTS, M09) | BUILT (P35 T6/T7) — each species needs its range render for the operator | proof `build-f/ledger-species-proof.html`; `tests/test_targeted_species.py` (14) |
| **Page sound cues** — paper slide (roll-out), drop settle (bleed), chalk stroke (outline draw-complete): CC0 Freesound, trimmed ≤1.5s, matched to the whoosh at −14 LUFS ±1 LU; page-relative `page_cues` in SOUND-PLAN (the `cues` list is flattened onto the episode clock by the mixer) | `sound/fs-page-*.mp3` (gitignored) + `sound/SOURCES.md` + `configs/sound_palette.json` | BUILT (P35 T9) — no CC0 ink sound under 4s exists; the bleed slot is a water drop, flag at the contact sheet | loudness table in SOURCES.md |
| **Choreography ledger + gates** — every enter/exit/side/how-it-leaves, gated per slot; FAIL blocks the build | `content/video_engine/scripts/emit_choreography.py` → `build-f/CHOREOGRAPHY.md` | LIVE — constants mirror the template; change together | caught tnx re-landing on first run |
| **Whiteboard reveal engine** — serpentine SVG mask + hand follower, pose set with per-pose nib calibration | git history `7880c01`, `1e6612f`; poses `hyperframes/assets/hands/` + `nib-calibration.v1.json` | RETIRED from this lane (doc 29 8.17) — earns its place when artwork is drawn, not sourced | doc 29 8.10–8.16 |
| **Remotion Production Console** — local timeline/canvas editor + Python bridge (`127.0.0.1:4317`): scrub/zoom/drag/trim, hash-bound immutable revisions, recompiles without touching narration or evidence approvals; semantic-evidence binding tests | `content/video_engine/production_console/` + `configs/production_console_snapshot*.schema.json` (merged from p31, 2026-08-29) | BUILT — the doc 29 §9.3 production route | P29/P31 gate screenshots in `.claude/PRPs/evidence/` |
| **Remotion composition registry** — single source of truth for editor compositions (Editorial, Documentary, motion variants, finance proofs, production evidence/timeline, 3D prototypes) | `content/video_engine/editor/src/compositions.ts` | LIVE — register here, never in Root.tsx | typecheck + vitest |
| **Editor fixtures** — editorial-motion two-shot with render harness (`render.mjs`), canonical audio fixture | `content/video_engine/editor/fixtures/` (merged from p16) | BUILT | `npm run render:editorial-motion-fixture` |
| **remotion-ui registry** (external, MIT) — ~200 copy-in `.tsx` components: captions, data/live metrics, SVG draw-on paths, TransitionSeries transitions, motion primitives; MCP server (`npx remotion-ui-mcp`) exposes list/search/detail/install to agents | github.com/riaz37/remotion-ui · remotionui.com/docs/components/browse | MCP INSTALLED (.mcp.json, loads on session start); registry index + 8 key components read; THREE techniques already ported into the review player (feathered wipe edge, under-wipe parallax, active-word caption pop). Their EASING.pop == our badge spring — same motion school. Full sweep when the Remotion port opens | port commit 2026-08-30 |
| **Hyperframes** — HTML-to-video rendering framework & motion system (DOM `data-*` timeline, clips, tracks, sub-compositions, 7 runtime adapters [GSAP, Lottie, Three.js, Anime.js, CSS, WAAPI, TypeGPU], seek-safe keyframes, registry blocks, Remotion-to-HyperFrames compilation) | `.agents/skills/hyperframes*`, `content/video_engine/review/hyperframes_assets`, `npx hyperframes` (0.8.27) | LIVE & STANDARDIZED — 8 skills synced across master, global Codex and all worktrees; PLANE ONE preserved (operator 2026-08-30) alongside the Remotion plane | CLI `npx hyperframes --version` -> 0.8.27, doc 29 Part 7 |

## Generative video, 2.5D parallax & driver automation (2026-09)

Rescued onto main 2026-09-03: this stack was written UNTRACKED in the main checkout
while it sat on `claude/outreach-api-and-tooling` (299 commits behind), so it belonged
to no branch. ComfyUI is the host for the first three - they are custom nodes on the
local instance at `127.0.0.1:8188`, not standalone tools.

| Capability | Where | State | Proof |
|---|---|---|---|
| **ComfyUI 2.5D Parallax Engine** - zero-hallucination monocular metric depth (`Depth Anything v2`) + virtual 3D camera trajectory displacement (`Depthflow` GLSL: dolly, zoom, circle, horizontal, vertical, orbital); turns an approved still plate into a camera sweep without AI shape drift, so it never re-generates locked art | `tools/google-flow-driver/src/parallax-runner.mjs`, `comfy-client.mjs`, workflow `content/video_engine/workflows/2_5d_parallax_inpaint.json`, ComfyUI `127.0.0.1:8188` | LIVE - benchmarked on RTX 4070 (3.1s / 30 frames @ 1024x768) | `content/video_engine/assets/test_parallax_dolly.mp4` (untracked - `*.mp4` is gitignored by the binary policy) |
| **SAM 2 + LaMa occlusion inpainting** (ComfyUI nodes) - the precondition for parallax on any plate carrying an actor: SAM 2 cuts the subject to an alpha PNG, LaMa fills the hole behind it (~0.3s), and the camera then moves two clean layers instead of stretching edge pixels into smears | `custom_nodes/ComfyUI-segment-anything-2`, `custom_nodes/comfyui-inpaint-nodes` | INSTALLED & VERIFIED | ComfyUI node initialization ledger |
| **LTX-Video 2B DiT ambient engine** (ComfyUI node) - local physical motion loops (haze, embers, drifting cloud, water) on a still plate, ~12s on the local GPU, zero cloud credits; SAM 2's mask pins the subject so the model animates only the ground - which is what protects the Graphic Silhouette actor from morphing | `custom_nodes/ComfyUI-LTXVideo` | INSTALLED & LOADED | ComfyUI node initialization ledger |
| **Google Flow driver** - zero-credit multi-reference generative diffusion over an ACTIVE Chrome CDP session (port 9222); the CDP path is the ONLY live one - `src/cdp-driver.mjs` + `dag-engine.mjs` behind `mcp/server.mjs`; preserves project canvas ratio or enforces 9:16 / 16:9; optional FFmpeg `-vf reverse` for pixel-exact ending-frame handoffs, which is what makes a SEQUENTIAL plate chain possible (plate N seeds plate N+1) | `tools/google-flow-driver/src/cdp-driver.mjs`, `flow-batch-runner.mjs` | LIVE - needs Chrome running with remote debugging | CDP handshake, resolution & duration capture |
| **Video engine MCP - TWO surfaces, verified by live handshake 2026-09-03** | `tools/google-flow-driver/mcp/` | **`server.mjs` -> `video-engine`** (4 tools): `create_flow_video`, `create_flow_batch` (`scenes[]` + `outputDir`), `get_flow_status`, and **`create_comfy_parallax_video` (`imagePath` + `outputPath`) - the ONLY MCP route to the parallax engine**. **`index.mjs`** (11 tools) drove the queue/bridge pipeline and is **RETIRED** with the extension lane below  Both registered in the tracked `.mcp.json`; they load on session start and resolve the SDK from the driver's own `node_modules`, so a fresh checkout needs `npm install` in `tools/google-flow-driver` first | both answered `tools/list` over stdio; the 4-tool and 11-tool sets above are what they actually returned, not what a doc claimed |
| **Chrome extension + native messaging host + the `flow-queue` MCP surface** - the pre-CDP bridge: a packaged extension (`extension/`), a native messaging host (`native-host/`) and 11 queue/bridge tools (`flow_enqueue_batch`, `flow_bridge_status`, `flow_capture_*`, ...) behind `mcp/index.mjs` + `mcp/tools.mjs` | `tools/google-flow-driver/` - 17 files, 238 KB, plus 8 tests (`capability-capture`, `content-bridge`, `native-protocol`, `image-runner`, `video-runner`, `selectors`, `state-machine`, `media-observer`) | **RETIRED 2026-09-03 (operator): obsolete to the MCP.** The CDP driver reaches Flow directly, so the browser-extension bridge it was built to cross no longer exists as a boundary. Unregistered from `.mcp.json`; the code is kept in git rather than deleted, on the same rule as the whiteboard reveal engine - a superseded mechanism is recorded with its reason, and the reason is what generalises | `server.mjs` imports `dag-engine` + `parallax-runner` and holds zero bridge references; `tools.mjs` is bridge-shaped throughout |
| **Video perception (`/watch`)** - acquisition via `yt-dlp`, frame extraction via `ffmpeg` (scene-aware or keyframe), timestamped transcript from native captions or Whisper | `.agents/skills/watch/` | LIVE & STANDARDIZED | yt-dlp 2026.08.19, ffmpeg 8.1.2 |

**Motion-gate standing:** ambient loops are TEXTURE, not authored events - they never
satisfy M01/M03/M08/M12, or they launder the stillness those gates were built to catch
(E21, E25). A parallax move counts as plate life only when it is bound to a narration
anchor, the same rule as narration-keyed chart draw and `narration_key_delays`.

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
| **Opening-minute gates (E24)** — the analyst's drop-off review (operator-verified against analytics) as gates, doc 29 §9.29–9.30: G45 packaging echo — the title/thumbnail content words (`--title`, `--thumb`) as the mechanical proxy for "the first sentence answers the thumbnail", J12 prints `--thumb-file` for the agent to open; G09 WARNs a promise past 0:45 (DECISION R7 vs doc 38's 0:60, the FAIL past 0:60 stands); M10 no still stretch > 6s begins in the first 60s; M11 the first chart enters 0:08–0:20 with a spotlight / callout / punch / focus_zoom within 1.5s (+ sound cue or WARN); M12 a chart dock never spans a scene boundary and holds ≤ 10s / ≤ 6s in the opening — re-enter it spotlit (E25: the chart is the proof, not the homework); the runner passes `--title/--thumb/--thumb-file` through | `scripts/gate_opening_structure.py` (G45 / J12 / G09) + `scripts/gate_motion_density.py` (M10–M12) + `run_script_gates.py` | LIVE 2026-09-03 — ep1 red on every row: G45 (none of ai / bubble / real / survives / steel / paper in the first two sentences), M10 3 stretches (0:16+10s, 0:33+16s, 0:57+14s), M11 ev-bravos-original-v1 at 9.5s full and unannotated, M12 25 chart docks held as homework (bravos 0:09–0:50 across 3 plates); opening gate 28 FAIL, motion gate 8 FAIL | `tests/test_gate_opening_structure.py`, `test_gate_motion_density.py`, `test_motion_gate_wiring.py`, `test_run_script_gates.py`; OPERATOR-RULINGS E24 / E25 |
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
| **The viewer (P36)** — a blind, windowed perception test: an agent that knows no doctrine reads the script cold in 15s windows with a two-window memory; a deterministic scorer measures beat recall (a declared beat the reader never felt was laundered) and information gain | `scripts/viewer_windows.py` · `viewer_run.py` (Codex headless) · `viewer_score.py`; `run_script_gates.py --viewer-gate` | **shipped and binding** (P36 HG1 granted 2026-09-03 on the ep1 calibration: recall FAILs, confusion WARNs, gain INFO-only) | ep1: 54 windows on measured timings, all 37 declared beats placed; `test_viewer_windows.py` 17 + `test_viewer_score.py` 14 |

## The research reference layer (2026-09-04)

Docs **42–46** condense the research evidence bundle into what is applicable here.
[`RESEARCH-INDEX.md`](RESEARCH-INDEX.md) dispositions **every heading of every bundle
document** — coverage is the proof of reading — and
`python scripts/check_research_extraction.py` enforces it.

| doc | what it settles |
|---|---|
| [42-DRAWING-KINETICS](42-DRAWING-KINETICS.md) | why our stroke reads as a plotter, and the closed-form overshoot that replaces guessed timing |
| [43-SCENE-GRAPH-AND-TRANSFORM](43-SCENE-GRAPH-AND-TRANSFORM.md) | the anchor sandwich, the Z-stack, both morph methods, the cutout rig |
| [44-INK-AND-SURFACE](44-INK-AND-SURFACE.md) | alpha blending is the wrong operator for layered ink |
| [45-PARALLAX-AND-PLATE-MOTION](45-PARALLAX-AND-PLATE-MOTION.md) | the viability matrix — parallax is banned on the page — and our dial audit |
| [46-REFERENCE-RHYTHM](46-REFERENCE-RHYTHM.md) | the shot distribution recomputed, and the equation spine |
| [47-FINDINGS-TO-CHECKS](47-FINDINGS-TO-CHECKS.md) | which findings can be designed out, gated, judged — or demoted |
| [48-THE-FIGURE-AND-THE-GROUND](48-THE-FIGURE-AND-THE-GROUND.md) | how an actor moves, holds a prop, and stands on a plate without looking pasted |
| [49-GENERATIVE-VIDEO-AND-THE-VERTICAL-STAGE](49-GENERATIVE-VIDEO-AND-THE-VERTICAL-STAGE.md) | Wan/LTX/depth dials, mask pinning, and the mobile safe box our 9:16 layout violates |
| [50-THE-PHONE-IS-THE-SCREEN](50-THE-PHONE-IS-THE-SCREEN.md) | **ep1's real analytics** — the cold cohort leaves at 1:05, 75 % watch on a phone, and our type is illegible there |
| [51-THE-SHORTS-FORMAT](51-THE-SHORTS-FORMAT.md) | **one page, ship in an afternoon** — the four numbers, the shape, and a deliberately lower production bar |

These are **reference, not portable**. A rule graduates to `docs/portable/` once proven
in a shipped build, and its index row says so.

## What is NOT built yet

[`BACKLOG.md`](BACKLOG.md) — the hand-maintained open work, and the scope shift
behind it. This file says what exists; the backlog says what is asked for and
what is blocked on an operator decision. `STATE-OF-WORK.md` is neither: it is
the auto-generated worktree census.

## The recall rule

1. `ls` and read the index before searching (PIPELINE.md, this file, PLATE-LIBRARY, CHOREOGRAPHY).
2. When a doc cites a source artifact, the audit reads the artifact.
3. A capability added or retired updates this file **in the same commit**.
4. A capability that ships **closes its BACKLOG.md row in the same commit** — a
   backlog that outlives its work is worse than none.
