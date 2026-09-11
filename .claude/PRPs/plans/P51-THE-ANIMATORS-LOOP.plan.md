---
id: P51-THE-ANIMATORS-LOOP
title: The animator's loop - the engine apart from the editor, eyes that cost nothing, a one-shot bar, and a diffable edit layer a human or a flash agent can write
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-11
updated: 2026-09-11
---

# The animator's loop

## Summary

The operator's grill of 2026-09-11 (`docs/content-video-engine/GRILL-ANIMATOR-ITERATION-2026-09-11.md`, the decision
ledger; the spike `docs/research/runs/grill_animator-iteration/findings_r1.md`): *"we don't come close enough to a first
pass, then we spend a lot of time improving and iterating takes too long"*; the agent's loop first, the operator's editor
second; the player a pure function of t with a ghost outline allowed on a drag; a human's or a flash agent's edit as a
sidecar of overrides the agent can diff; a one-shot bar the cut clears before the operator watches (the first 3:00 of a
long, the first 0:60 of a short, at higher scrutiny); the ledger page as the main character, plates as narration plates.

**Recall** (`docs/runbooks/RECALL-RECEIPT.md`):
- `docs/content-video-engine/BACKLOG.md` R26-17 TOP (the operator, 2026-09-07: *"build the actual engine so that the editor
  is not the engine"*) - its four steps are this plan's T1, T3, T5, T6; its diagnosis (a 4,000-line template instantiated
  per build with every asset embedded; no live edit) still holds: the Tokyo player is 32 MB.
- `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build_short.py` (785 lines, 25 helpers) and
  `japan-tariff-trick/build_short.py` (537, 25): eleven helpers copied between them by name; the long form is authored
  through `steel-and-paper/SHOT-TABLE-F.py` + `build_scene_evidence_cut.py` and cannot reach them. Both call
  `build_scene_timeline_f.py`; the format is `aspect`.
- `docs/content-video-engine/CAPABILITIES.md` (the golden-frame harness; the gate rows M01-M24; the Remotion Production
  Console - a different runtime, its remotion-ui components the earmarked shell); `tests/test_camera.py` `_Player`,
  `test_chart_transitions.py` `_player`, `test_breakthrough.py` PROBE - the DOM probes the eyes are made of.
- `docs/portable/OPERATOR-RULINGS.md` E24 (the promise by 0:45), E27 (package first), E45 (the shorts standard), E50,
  E52, E53, E58-E60; `29-EVIDENCE-MOTION-STANDARDS.md` §9.27-9.28; `46-REFERENCE-RHYTHM.md` §46.7.
- `docs_find "layout gate"` 0 hits; `docs_find "overrides"` 0 hits in the engine docs; `docs_find "self-watch"` 0 hits.
  The eyes, the sidecar and the bar are gaps in the record, not only in the code.
- The spike's precedents: Motion Canvas writes a dragged timing to a named event in a `.meta` sidecar; Theatre.js
  keeps a state JSON with random keyframe ids (a semantic diff is needed); Remotion writes into source and its docs
  name the preview-versus-render desync; HyperFrames gates capture on one runtime and warns of per-machine pixel drift.

**APPROVED 2026-09-11** (the operator: *"approve both plans"*). The order by slice across the two plans stands as written in the Execution Path: P50 T1 -> P51 T0, T2, T3 -> P50's species as modules -> P51 T1, T4-T7; P51 T8 in parallel.

## Intent And Acceptance

Intent: the agent's first pass clears a bar the operator can trust before watching; every cut the operator or a flash
agent makes is a diff the agent can read and answer; a shot-table edit is on screen in a second and provably the same
frame the render will make; the two formats share one authoring door; the render tail is one command.

Acceptance:
- **The one-shot bar exists and is a build artifact.** `SELF-WATCH.md` beside every build: gate results, the layout gate,
  the species-by-sentence lint (P50 T1), the blind viewer's verdict on the script, and the opening's contact sheet (3:00
  long / 0:60 short at 2 s steps) with the checklist verdicts. The operator's watch begins only on a clean one.
- **Eyes cost nothing after the first build.** `probe.py <build> <t...> --json [--sheet]` returns every dock, pill, label,
  caption and chart box at t with overlaps, sizes at phone scale, clearances, the camera state and the marks; M25 (the
  layout gate) refuses an overlap, an under-size type or a safe-zone breach; the three defects of 2026-09-10 (the light
  over the burst's page, the card over the bars' feet, the citation under the cards) each reproduce as an M25 FAIL on
  the commit before their fix.
- **One authoring door.** `content/video_engine/scripts/authoring/` holds the kit; Tokyo's and the tariff's build scripts
  shrink to their rows + facts and produce byte-identical builds (the gate reports and timelines diff empty); the long
  form's door imports the same kit.
- **The engine apart from the document.** The page loads the painter and the kinetics as a module and fetches the
  timeline and the asset map; a build writes data only; `render_episode.py` seeks the same pure function; the goldens
  are byte-identical (the golden surfaces are re-instantiated through the new loader and hash the same).
- **Hot reload proves determinism.** A shot-table or sidecar edit reaches the served page in under a second; the
  affected instants are rendered warm and cold and their hashes compared; a mismatch is shown, never hidden.
- **The sidecar.** `<build>/overrides.json` keyed by row id and field; the compiler layers it over the shot table; a diff
  of it yields `CHANGE-REPORT.md`: each line, the before/after frames at the affected instant, the gate delta.
- **The editor, thin.** Scrub, scene list, species per scene, the dials as live controls writing the sidecar; a ghost
  outline while dragging, the real frame on release; no runtime state (the determinism check runs on every commit of a
  drag).
- **The doctrine.** Doc 29 gains the chart-as-world section for long form and the package rule; E61 drafted with the
  operator's words for their ruling.

## Scope

- `content/video_engine/scripts/authoring/` (new package: the kit), the two shorts' build scripts (thinned), the F door.
- The player template split into a runtime module + a document shell; `render_baseline.py` / `sync_kinetics.py` /
  `render_episode.py` adjusted; the golden harness re-pointed.
- `probe.py` (new), `gate_motion_density.py` (M25), `serve_player.py` (reload + the determinism check),
  `build_scene_timeline_f.py` (the sidecar layer), `self_watch.py` (new), `change_report.py` (new).
- The editor page (`editor.html`, a client of the served player), the remotion-ui components as its shell.
- Docs: CAPABILITIES rows, BACKLOG R26-17 closed by slices, doc 29 §9.30 (chart as world), E61 draft, PIPELINE stage 7-8.

## Not Building

- Any runtime state in the engine (the ghost outline is the editor's, drawn over the frame, never in it).
- A GUI-first tool for agents; the agent's surface is the probe, the report and the sidecar diff.
- Vision as the primary eye: frames are contact sheets at instants the timeline chose; crops only to verify a number.
- Reproductions: no re-render of shipped cuts on these mechanisms (the operator: new content at the new level).
- AnimatorOS (the component library + canvas + built-in agents; the vidrush-style asset pulls): the horizon, recorded in
  the ledger §5; P51 is its spine, not its shell.
- The Remotion Production Console: a different runtime; only its remotion-ui components are reused, as a shell.
- Cross-machine golden exactness (browser pinning / Docker): recorded as a gotcha; goldens stay per-machine.

## Human Gates

1. **The one-shot checklist** (T3): the operator reads the first `SELF-WATCH.md` on a real build and says whether it is
   the bar - what it should refuse that it passed, what it flagged that it should not.
2. **The change report's shape** (T6): the operator makes three edits in the sidecar by hand (a box, a beat's word, a
   variant) and reads the report the agent gets; does it say what they changed?
3. **The editor's first three controls** (T7) by eye, on the Tokyo cut.
4. **E61** (T8): RULED 2026-09-11 in the operator's words; the package rule struck (an open A/B test). Gate closed.
5. Push authorization per commit, as standing.

## Mandatory Reads

- `docs/runbooks/RECALL-RECEIPT.md`, `docs/runbooks/PRP_EXECUTION.md`; the ledger and the spike named above.
- `docs/portable/OPERATOR-RULINGS.md` E24, E27, E45, E50, E52, E53, E58, E59, E60.
- `docs/content-video-engine/CAPABILITIES.md` §"The golden-frame harness", §"The frozen baseline"; `BACKLOG.md` R26-17.
- `content/video_engine/scripts/build_scene_timeline_f.py` (`dock_entry`, `dock_opts`, `centred_place`, `world_for_plate`,
  the species registry); `render_baseline.py` (`instantiate`, `load_surface`, `serve`, `frame_png`, `prepare_page`);
  `sync_kinetics.py`; `gate_motion_density.py` (`_landings`, `_deployed_lives`, the M-rows); the template's dock loop
  (`dockGeom`, `dockReadRect`), `lpPaintPark`, `camNow`, `window.__lpProbe` / `__camera` / `__camArr`.
- The two shorts' build scripts end to end; `steel-and-paper/build_scene_evidence_cut.py`.
- Skills: `evidence-motion-engine`, `episode-build`. No `backend-patterns` / `frontend-patterns` (no server framework,
  no React in the engine; the editor is plain HTML over the served player).

## Execution Path

1. T0 the authoring kit, then T2 the eyes, then T3 the bar - the three that make a one-shot possible on the engine as it
   stands, none of them needing the split. T8 the doctrine in parallel (docs only; it steers the next long).
   **Against P50:** P50 T1 (the map) precedes T0; P50's species (T2-T16) follow T3 and are written as MODULES under
   `scripts/species/` inlined by `sync_kinetics.py` (P50's module rule), so T1 here changes how modules load and ports
   nothing; T4-T7 follow the species or interleave with them - they do not depend on them.
2. T1 the split, proven by the goldens; then T4 hot reload with the determinism check; then T5 the sidecar and T6 the
   change report (the human-and-flash-agent loop).
3. T7 the editor last, thin, as a client.
4. Every slice: goldens byte-identical, the two shorts' builds diff-empty (or the diff named and approved), a
   CAPABILITIES row in the same commit, a `Recall:` line, the backlog row closed or re-pointed in the same commit.

## Patterns To Mirror

- The DOM probes of `test_camera.py` / `test_breakthrough.py` (a JSON of the state at t, then assertions) - the probe CLI
  is those probes with a command line.
- The gate's `_landings` / `_deployed_lives` (the instants that matter come from the timeline, not from guessing).
- The golden harness (`load_surface` / `instantiate` / hash) - the determinism check is the same three calls at the
  changed instants, warm then cold.
- The dock tuple's options dict (`dock_opts`, checked with a named reason) - the sidecar's fields are validated the same
  way, by the same code.
- Motion Canvas's `.meta` sidecar (a named event, one line per tuning) - the shape of `overrides.json`.
- The Remotion + Claude Code loop's order: diff review, validation, apply, frame checks, human approval for the render.

## Task Slices

### T0: The authoring kit - one door for both formats
- Status: complete (2026-09-11)
- Owner: `implementation_luna`; parent reviews the diff-empty proof
- Depends on: none
- Write set: `content/video_engine/scripts/authoring/__init__.py`, `words.py` (`words`, `shifted_words`, `phrase_start`,
  `word_time`, `cut_before`, `at`), `docks.py` (`dock_png`, `dock_still`, `dock_zoom`, `dock_card`, `record_dock`,
  `record_words`, `centred_card_point`, `card_aspect`, `clip_dock`, `seekable_clip`, `zoom_clip`), `audio.py` (the
  outro stitch, the brand line, `BED_LU` / `env`, `insert_edit_pauses` glue), `table.py` (the shot table as data: rows
  with word anchors resolved by the kit; the tuple form kept as the compiled shape); the two shorts' `build_short.py`
  reduced to rows + facts; `steel-and-paper/build_scene_evidence_cut.py` importing the kit; `tests/test_authoring_kit.py`.
- Acceptance: both shorts rebuild byte-identical (timeline JSON, evidence-dock JSON, GATES-MOTION.md diff empty); the F
  door builds unchanged; the kit has no per-project constant in it (every episode fact stays in the episode).
- Validate: rebuild both shorts and `git diff --stat` on their build folders; `python -m pytest content/video_engine/tests/test_authoring_kit.py -q`
- Evidence: `content/video_engine/scripts/authoring/{__init__,words,docks,audio,table}.py` (588 lines); `tests/test_authoring_kit.py` (31 tests, with the hygiene grep); Tokyo `build_short.py` 785 -> 573, the tariff 537 -> 404; the proof: both shorts rebuilt into `build-short-t0/` before and after, `cmp -s` IDENTICAL on timeline.json / evidence-dock.json / caption-pages.json / GATES-MOTION.md / the compiled timeline / SHOT-TABLE-SHORT.py / SOUND-PLAN.json (the parent repeated the Tokyo rebuild against the agent's baseline: identical); `PLATE_USES` + `;use=` in the compiler (the lint imports it). Deviations: the F door shares nothing importable without changing its output (ep1's legacy door: own WINDOWS, inline SVG evidence, a hardcoded worktree REPO path) - left untouched; the kit preserves two quirks of the approved cuts on purpose, logged as BACKLOG R26-35 (the Tokyo bed swell keys on `:snap=` only) and R26-36 (the `:cut` suffix test misses `;then=` rows). CAPABILITIES row added.

### T1: The runtime apart from the document (R26-17 step 1)
- Status: pending
- Owner: parent (the split is architecture); `implementation_luna` for the loader
- Depends on: T0
- Write set: the template split into `engine.mjs` (the painter, the species, the kinetics inlined today by
  `sync_kinetics.py`) and `player.html` (a shell that fetches `timeline.json` and `assets.json` and mounts the engine);
  `render_baseline.instantiate` keeps writing the single-file form for the goldens AND writes the split form for builds;
  `render_episode.py` seeks the split form; `serve_player.py` serves both; `sync_kinetics.py` targets the module;
  `test_golden_frames.py` gains one parity test (the split form of a golden surface hashes the same as the single file).
- Acceptance: the Tokyo build folder holds a ~200 KB player and a fetched asset map instead of a 32 MB file; every
  golden byte-identical in both forms; the gate unchanged.
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_performs.py -q`; a Tokyo rebuild + its gate
- Evidence: pending

### T2: Eyes - the probe CLI and the layout gate M25
- Status: complete (2026-09-11)
- Owner: `implementation_luna` (the probe); parent (the gate's thresholds, measured on the three defects)
- Depends on: none
- Write set: `content/video_engine/scripts/probe.py` (`probe <build> <t...> --json [--sheet out.png --tile 360]`: every
  dock / pill / label / caption / chart box at t from the page's own DOM, overlaps as pairs with the overlap area, type
  sizes at the phone scale (1080 -> 390 CSS px), clearances to the caption strip and the safe zone, the camera state,
  the marks); `gate_motion_density.py` M25 (the layout gate: at every landing, transition end and species onset - the
  instants `_landings` already knows - a dock over a chart's plot, a label or citation under a card, a pill or paper
  in the caption strip, type under 11 CSS px on a short: FAIL with the boxes named); `tests/test_probe.py`,
  `test_gate_motion_density.py` (+3: the three defects of 2026-09-10 rebuilt from the commits before their fixes each
  FAIL M25 with the right pair named); CAPABILITIES row; `docs/GATES-REGISTRY` regenerated.
- Acceptance: as the acceptance above; the probe's JSON for one instant is under 2 KB.
- Validate: `python content/video_engine/scripts/probe.py content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short 58.6 --json`; the gate tests
- Evidence: `content/video_engine/scripts/probe.py` (625 lines), `gate_motion_density.py` M25 (+132), `tests/test_probe.py` (8), `tests/test_gate_motion_density.py` (+4: the three 2026-09-10 defects rebuilt as fixtures from the Tokyo compiled timeline each FAIL with the right pair named, the untouched build PASSes). Measured: Tokyo 58.6 JSON 1,092 bytes in 2.2 s; `--gate` 61 instants in 7.8 s; the gate `[PASS ] M25 ... smallest type read 11.6 CSS px on a phone (floor 11) | INFO ... source parked 4.9, chart.lab parked 7.5 ...`; 145 tests green across probe / gate / camera / lint / kit (the parent's run). Four scope decisions, measured and named in code: settled cards only (the Fed card crosses the page mid-throw in the approved cut); the chart's DATA, not its plot box (the approved tea cup parks in the plot's empty corner); ink line by line (a two-line sub is mostly air); the type floor skips parked runs and the citation (the 2026-09-07 design pass set .lp-src.compact at 9.4 CSS px on purpose) and lists them. Two template findings logged, not fixed here (out of the write set): R26-37 (the template's probes take the first ledger world), R26-38 (stale `__lp` after a backward seek). CAPABILITIES row; PIPELINE 7c; GATES-REGISTRY regenerated.

### T3: The one-shot bar - the self-watch as a build artifact
- Status: pending (human gate 1 on its first real report)
- Owner: parent (the checklist); `junior_developer` (the runner)
- Depends on: T2, P50 T1 (the species-by-sentence lint)
- Write set: `content/video_engine/scripts/self_watch.py` (runs the gate, M25, the lint, the viewer's last verdict for the
  script, then grabs the opening's contact sheet - 3:00 at 2 s on a long, 0:60 at 2 s on a short, 360 px tiles, 12 per
  sheet - and writes `SELF-WATCH.md` with a checklist the agent fills by reading the sheets: the package answered on the
  first sentence (E24/E27), the promise by 0:45, every sentence-act with its species, no dead band, no overlap, the
  citations readable; a verdict line); `build_short.py` / the F door call it last; the `episode-build` skill's last step
  reads it; CAPABILITIES row; `PIPELINE.md` stage 8.
- Acceptance: a build the agent hands over carries a clean `SELF-WATCH.md`; the operator's first read (gate 1) names what
  the bar should have refused, and those become rows.
- Validate: `python content/video_engine/scripts/self_watch.py <build>` on the Tokyo cut; the file exists and every row has a verdict
- Evidence: pending

### T4: Hot reload with the determinism check (R26-17 step 2)
- Status: pending
- Owner: `implementation_luna`
- Depends on: T1
- Write set: `serve_player.py` (a file watcher on the shot table / sidecar / dials; a `/reload` endpoint the page long-polls;
  the compiler re-run in-process, the timeline pushed); the engine (a `reload(timeline)` entry that rebuilds state
  without a page load); `determinism_check.py` (the changed instants - the diff of the two timelines names them -
  rendered warm then cold through `render_baseline`, hashed, the mismatch printed with the frames); `tests/test_reload.py`.
- Acceptance: a `centre_y` edit lands on the served page in under a second; a deliberate stateful bug (a test fixture
  that caches a box) is caught as a warm/cold mismatch at the instant.
- Validate: `python -m pytest content/video_engine/tests/test_reload.py -q`
- Evidence: pending

### T5: The override sidecar
- Status: pending
- Owner: `implementation_luna`; parent (the schema)
- Depends on: T0
- Write set: `build_scene_timeline_f.py` (`apply_overrides(rows, overrides)`: a sidecar `<build>/overrides.json` keyed by
  row id (`s04.dock.dock-k-pledge-record`, `s04.species.3`) and field, validated by the same `dock_opts` /
  `_validate_page_fields` code, layered before compile; a row id written into every compiled scene/dock/species so the
  key is stable); the kit's `table.py` (row ids); `tests/test_overrides.py`; CAPABILITIES row.
- Acceptance: an override of `centre_y`, of a species' `at` (by word), and of `TOKYO_CAMERA` produces the same build as
  editing the source would; an unknown key or a bad value is refused with the row named.
- Validate: `python -m pytest content/video_engine/tests/test_overrides.py -q`
- Evidence: pending

### T6: The change report - what a human or a flash agent changed, as the agent sees it
- Status: pending (human gate 2)
- Owner: `implementation_luna`; parent reads the first report
- Depends on: T2, T5
- Write set: `content/video_engine/scripts/change_report.py` (`change_report <build> [--since <sha>|--against <overrides.json>]`:
  the sidecar diff line by line; for each changed key the instants it touches (from the timeline: the dock's span, the
  species' at) and a before/after crop pair at each from the probe's sheet; the gate delta M01-M25; one
  `CHANGE-REPORT.md`); the `episode-build` skill: "when summoned after an edit, read CHANGE-REPORT.md first".
- Acceptance: gate 2 - the operator's three hand edits are each described correctly by the report the agent gets, with
  the frame pair, and the agent's reply cites it.
- Validate: `python content/video_engine/scripts/change_report.py <build> --against <a hand-edited overrides.json>`
- Evidence: pending

### T7: The editor, thin (R26-17 step 3)
- Status: pending (human gate 3)
- Owner: parent (the controls); `implementation_luna` (the page)
- Depends on: T4, T5
- Write set: `content/video_engine/editor/editor.html` (a client of the served player: the scrub, the scene list, the
  species per scene, the dock boxes as draggable outlines, the dials LP / DOCK_* / LPX.BT_* / ATTN as controls - every
  control writes `overrides.json` through `serve_player.py`, the page reloads by T4; a ghost outline follows the hand
  during a drag, the real frame on release; the determinism check runs on each committed edit); the remotion-ui
  components as the shell where they fit; `.claude/launch.json` entry.
- Acceptance: gate 3 - the three edits of 2026-09-10 (the record 0.015 up, the plant 0.04 down, the camera on) made by
  hand in the editor, each landing as a sidecar line and a frame, no rebuild by the agent.
- Validate: by eye on the Tokyo cut; `python -m pytest content/video_engine/tests/test_overrides.py content/video_engine/tests/test_reload.py -q`
- Evidence: pending

### T8: The chart-as-world doctrine and the package rule
- Status: complete (2026-09-11) - E61 ruled in the operator's words; the doctrine written as doc 29 **§9.33** (§9.30 was already "the chart is the PROOF" - the plan's number was stale)
- Owner: parent
- Depends on: none (docs)
- Write set: `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §9.30 (the ledger page as the main character of a
  long form: the equation spine across phases, scene extension by the chart-to-chart family, the park/un-park as the
  breath, the burst as the payoff, a plate where the story needs a picture - a narration plate, B-roll; the operator's
  three uses of a plate, verbatim in the ledger: a LANDING SURFACE for docked evidence (the art embed) or evidence docked
  straight on the chart, a BRIDGE between ideas, a RESET that covers the world so the evidence clears and the next page
  mounts clean or on a new topic - each with its surface-grammar letter and its seam); NO package rule (struck
  2026-09-11: thumbnails are under A/B test, our own plates untested - E61 records it as not ruled);
  `docs/portable/OPERATOR-RULINGS.md` E61 drafted in the operator's words of 2026-09-11; `patterns/FULL-VIDEO-MAP.md`
  one paragraph; `episode-build` skill B-rules; the docs layers.
- Acceptance: E61 reads as the operator's; the next long's shot table is authored on pages by default and the lint (P50
  T1) reports plates as exceptions with their reason.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §9.33 (the page across the phases, the park/un-park as the breath, the burst as the payoff, the three plate uses verbatim with their §9.28 letters and seams, the package explicitly not ruled); `patterns/FULL-VIDEO-MAP.md` §2 one paragraph; the episode-build skill's plate-cadence rule (home, not the repo); docs layers regenerated. The lint's WARN on an unnamed long-form plate shipped with P50 T1 (ea4dac2).

## Verification

- `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_performs.py content/video_engine/tests/test_authoring_kit.py content/video_engine/tests/test_probe.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_overrides.py content/video_engine/tests/test_reload.py -q`
- Both shorts rebuilt after every slice: timelines and gate reports diff-empty unless the diff is named and approved.
- `python scripts/prp_validate.py .claude/PRPs/plans/P51-THE-ANIMATORS-LOOP.plan.md`; `build_docs_layers.py --check`.
- The four human gates, in order; judgement stays the operator's.

## Evidence And Handoff

- Evidence lands per slice in this file; commit SHAs; the first `SELF-WATCH.md`, the first `CHANGE-REPORT.md`, the
  editor's first three edits as frames.
- Handoff: CAPABILITIES rows per slice; BACKLOG R26-17 closed by T1/T4/T7 in their commits; the ledger updated with what
  the gates changed; the next long authored through the one door with the bar in front of it.
