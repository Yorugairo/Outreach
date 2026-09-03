---
id: P34-GATE-IMPROVEMENTS
title: Gate improvements - one runner, no silent skips, the motion gate wired into the build
status: draft
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-09-02
updated: 2026-09-02
---

# Gate Improvements

## Summary

Episode one shipped past two checks that existed on paper. The script
gates (lint, audit, opening structure, screens) run as four separate
commands nobody is required to chain, and recording does not ask whether
they ran; the motion-density gate (E21) runs on the built timeline but
nothing in the build or render lane calls it. This PRP makes the gate
system a pipeline the artifacts cannot bypass: one script-gate runner that
emits the CHECK-RESPONSIBILITIES §5 TOOLS block and blocks recording on
FAIL, the motion gate called by the build and consulted by the render, an
enumeration artifact for declared-beat verification (rule R2), the A3
doctrine conflict resolved once, and caption STAGE mode in the player so
gate M08 can enforce instead of listing.

Research note: SigMap does not index `content/video_engine/` (every hit
scored on penalty alone), so tracing was by grep per the standing search
order. Roles below map to harness types per the runbook's dispatch table
(`general-purpose` for implementers, `Explore` for read-only, parent for
reviewed shots and git).

## Intent And Acceptance

Intent: no script records and no episode renders without every gate
having run and passed, with the report on disk; the agent's remaining
verdicts have an artifact to verdict against.

Acceptance (all observable):
- `python content/video_engine/scripts/run_script_gates.py <script> --ring <t> --counterparty <n> [--timeline …]`
  runs lint → audit → opening gate → screens, writes `<script>-GATES.md`
  with the §5 TOOLS block (exit + counts per tool, timing source, screens
  count), and exits 1 on any FAIL.
- `record_chained_take.py` / `record_master_take.py` refuse to record a
  script whose `-GATES.md` is missing, stale (script hash mismatch) or
  carries a FAIL; `--force "<reason>"` records anyway and writes the reason
  into the take's metadata.
- `enumerate_strength_screens.py` emits a DECLARED section: every beat tag,
  its window verdict from the gate, and the quoted sentence under it, so
  the R2 true/laundered verdict is enumerated, not remembered.
- The audit's A3 anchor follows the operator's decision (Human Gate 1)
  and the opening gate's G25 source line no longer prints a conflict.
- The audit stops issuing a second verdict on rows the opening gate owns
  (promise window, 3s hook, 8s paradox, "you" by 0:30, greetings) when a
  gates report is present; one row, one verdict (R1).
- `build_scene_timeline_f.py` calls `gate_motion_density.run` after
  compiling and writes `build-f/GATES-MOTION.md`; `render_episode.py`
  refuses a full render when that report carries a FAIL unless `--force`.
- The player renders caption STAGE mode when no dock is active (inverse
  of the existing `quiet` toggle), the compiled timeline declares
  `caption_modes: ["stage","anchor"]`, and gate M08 enforces (FAIL) on
  builds that declare it while counting stage-caption windows as visual
  events. The 0:57 still stretch is rendered side by side (anchor vs
  stage) and the operator picks before the template change is kept
  (Human Gate 2).
- Steel and Paper as recorded/built stays RED on both gates (the
  known-real baseline: opening 26 FAIL, motion 4 FAIL); the synthetic
  conforming cases stay GREEN; all gate tests pass.

## Scope

- `content/video_engine/scripts/`: new `run_script_gates.py`; edits to
  `record_chained_take.py`, `record_master_take.py`,
  `enumerate_strength_screens.py`, `audit_script_doctrine.py`,
  `kit_spec.py` (A3), `build_scene_timeline_f.py`, `render_episode.py`,
  `gate_motion_density.py`, `gate_opening_structure.py` (G25 source line).
- `docs/content-video-engine/samples/scene-evidence-player.template.html`:
  `#caption.stage` CSS + toggle (T5 only).
- `content/video_engine/tests/`: one test module per slice.
- Docs: `PIPELINE.md` (stages 3-4 runner, 7c, 8 refusal),
  `patterns/CHECK-RESPONSIBILITIES.md` (§2 runner row, §4 sequence),
  `patterns/phase-guides/P2.md` + `29-EVIDENCE-MOTION-STANDARDS.md` §9.25
  (A3 resolution; stage mode shipped), `docs/portable/OPERATOR-RULINGS.md`
  (A3 ruling entry).

## Not Building

- The Steel and Paper re-script itself (separate work order; it consumes
  these gates).
- Any Remotion port, remotion-ui install, or video-dock species.
- New doctrine rows. Every gate here enforces a rule already written
  (doc 38, P1/P2, doc 29 §8.19/§9.13/§9.25, E20, E21).
- A CI service. Validation is local pytest + the runners' exit codes.
- Changing the wipe, dock choreography, or any reviewed shot other than
  the caption layer in T5.

## Human Gates

1. **A3 anchor** - DECIDED 2026-09-02: 10% of runtime ("A3 at 10% of
   runtime is correct"). The audit's 180s hard-code goes; `kit_spec`
   computes it. Operator's rider: "then we still have to set the next
   microhook and the cycle continues, but the way our structure is
   written that should already be self-healing regardless of when the
   hook lands." True in doctrine (the clock repeats per beat) and in the
   opening gate (G36, no >60s without a cycle beat, across the opening
   window); NOT yet mechanical past the opening - the per-unit rehook is a
   by-hand roster row. T2 therefore also extends the cycle check to the
   whole runtime.
2. **Caption stage mode** (blocks keeping T5): a change to how a reviewed
   shot looks is a proposal (REMOTION-UI-HARVEST lesson). T5 renders the
   0:57-1:11 window twice from the same timeline and the operator picks.
3. **Recording refusal semantics** - DECIDED 2026-09-02: hard refuse.
   Cause: a script whose gates report is missing, stale, or failing.
   Outcome: the recorder does not spend a take; it prints the report
   path. `--force "<reason>"` overrides and writes the reason into the
   take metadata. Impact: episode one's promise-at-1:20 could not have
   been recorded.

## Mandatory Reads

- `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md` (the
  contract every slice serves; §5 is the report format T1 emits)
- `docs/content-video-engine/PIPELINE.md` (stages 3-4, 7c, 8)
- `docs/content-video-engine/patterns/STRENGTH-LOOP.md` §8a (enumeration
  mandate - T3's reason to exist)
- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §8.19,
  §9.13, §9.15, §9.25 (T4/T5)
- `docs/content-video-engine/REMOTION-UI-HARVEST.md` (T5: harvested
  values; the side-by-side rule)
- `docs/content-video-engine/patterns/phase-guides/P2.md` (A3 at ~10%)
- `docs/portable/OPERATOR-RULINGS.md` E13 (probe-then-gate every take),
  E20, E21
- `content/video_engine/scripts/gate_opening_structure.py`,
  `gate_motion_density.py`, `beat_tags.py`, `audit_script_doctrine.py`
  (existing checker contracts; do not re-derive their verdicts)
- No `backend-patterns` / `frontend-patterns` routing: this is a Python
  CLI + one static HTML template, no server or React surface.

## Execution Path

1. T1 (runner + refusal) and T3 (declared-beat enumeration) in parallel:
   disjoint write sets.
2. T6 (audit defers to the gate) after T1, because it keys on the gates
   report's presence.
3. T2 (A3) after Human Gate 1; small, independent write set.
4. T4 (motion gate in the build/render) independent of 1-3; can run in
   parallel with T1/T3.
5. T5 (stage mode) last: parent-owned, ends in the side-by-side render
   and Human Gate 2; T4 must be in so M08 has a build to enforce on.
6. Doc updates ride in each slice's commit (same-commit rule), never as a
   trailing docs slice.

## Patterns To Mirror

- Gate shape: `Gate(id, src, level, message)` dataclass, `run()` returns
  `(gates, stats)`, `main()` prints sorted by level and exits 1 on FAIL -
  `gate_opening_structure.py` / `gate_motion_density.py`.
- Doctrine-cited constants at the top of the module with the doc line in
  the comment (`GRAB_S = 3.0  # 38 B1`).
- Tests: red on the known-real episode-one artifact (skip if absent),
  green on a synthetic conforming case -
  `tests/test_gate_opening_structure.py`, `tests/test_gate_motion_density.py`;
  `conftest.py` fixtures style.
- Take metadata and hashing: `record_chained_take.py` (canonical hash of
  the spoken text; the same hash keys the gates report).
- Player toggles: the `quiet` class keyed on `active.length > 0`
  (template :1339, :1376) - stage mode is its inverse, not a new system.
- Report artifacts beside the input: `<script>-SCREENS.md` from
  `enumerate_strength_screens.py`.

## Task Slices

### T1: Script-gate runner and recording refusal
- Status: pending
- Owner: implementation_luna (→ `general-purpose`)
- Depends on: Human Gate 3 (refusal semantics)
- Write set: `content/video_engine/scripts/run_script_gates.py`,
  `content/video_engine/scripts/record_chained_take.py`,
  `content/video_engine/scripts/record_master_take.py`,
  `content/video_engine/tests/test_run_script_gates.py`,
  `docs/content-video-engine/PIPELINE.md`,
  `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md` (§2 row, §4)
- Acceptance: runner executes the four checkers in order, writes
  `<script>-GATES.md` with the §5 TOOLS block and the script's canonical
  hash, exits 1 on any FAIL; both record scripts refuse on missing/stale/
  FAIL report and honour `--force "<reason>"` by recording the reason in
  the take metadata; ep1 script produces a FAIL report (baseline).
- Validate: `python -m pytest content/video_engine/tests/test_run_script_gates.py -q`
  and `python content/video_engine/scripts/run_script_gates.py content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-G-VO.txt --ring spike --counterparty Bravos --timeline content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/timeline.json; echo exit=$?`
  (expect exit=1 and the report on disk)
- Evidence: pending

### T2: A3 at 10% of runtime, and the cycle check runs the whole video
- Status: pending
- Owner: junior_developer (→ `general-purpose`)
- Depends on: none (Human Gate 1 decided)
- Write set: `content/video_engine/scripts/audit_script_doctrine.py`
  (REHOOK_ANCHORS / message), `content/video_engine/scripts/kit_spec.py`
  (A3 helper; unit geometry helper), `content/video_engine/scripts/gate_opening_structure.py`
  (G25 source line; G36 gains `--cycle-s` defaulting to the full runtime;
  new G44 per-unit rehook: every P3/P5 unit window per `kit_spec.unit_count`
  carries at least one rehook-family line or `[rehook]`), `content/video_engine/tests/test_audit_a3_anchor.py`,
  `content/video_engine/tests/test_gate_opening_structure.py`,
  `docs/portable/OPERATOR-RULINGS.md` (ruling entry: A3 10%; cycle whole-video),
  `docs/content-video-engine/patterns/phase-guides/P2.md` (QC note)
- Acceptance: audit and gate compute the same A3 target for the same
  runtime (1:20 at 13:26; 3:00 at 30:00); the gate's G25 source no longer
  says "audit hard-codes 3:00"; G36 reports the longest cycle gap over
  the whole runtime and FAILs above 60s anywhere; G44 FAILs a unit with
  no rehook; ep1 red baseline gains whatever these find past 5:00 (report
  the numbers); the conforming synthetic still passes.
- Validate: `python -m pytest content/video_engine/tests/test_audit_a3_anchor.py content/video_engine/tests/test_gate_opening_structure.py -q`
- Evidence: pending

### T3: Declared-beat enumeration (rule R2 artifact)
- Status: pending
- Owner: junior_developer (→ `general-purpose`)
- Depends on: none
- Write set: `content/video_engine/scripts/enumerate_strength_screens.py`,
  `content/video_engine/tests/test_enumerate_declared_beats.py`,
  `docs/content-video-engine/patterns/STRENGTH-LOOP.md` (§8a one line)
- Acceptance: `<script>-SCREENS.md` gains a DECLARED section: one row per
  beat tag (tag, mm:ss, gate window verdict, quoted sentence, verdict
  column blank for the agent); a script with no tags emits an explicit
  "no declared beats" line; runs on ep1 and on the conforming test text.
- Validate: `python -m pytest content/video_engine/tests/test_enumerate_declared_beats.py -q`
- Evidence: pending

### T4: Motion gate wired into build and render
- Status: pending
- Owner: implementation_luna (→ `general-purpose`)
- Depends on: none
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py`,
  `content/video_engine/scripts/render_episode.py`,
  `content/video_engine/tests/test_motion_gate_wiring.py`,
  `docs/content-video-engine/PIPELINE.md` (stage 8 refusal line)
- Acceptance: compiling a timeline writes `build-f/GATES-MOTION.md`
  (the gate's stdout, verbatim); `render_episode.py` exits 2 with the
  report path when it carries a FAIL, renders with `--force`, and never
  blocks the `--range` / shard preview modes; ep1's build-f produces the
  4-FAIL report.
- Validate: `python -m pytest content/video_engine/tests/test_motion_gate_wiring.py -q`
- Evidence: pending

### T5: Caption STAGE mode in the player, M08 enforced
- Status: pending
- Owner: parent
- Depends on: T4, Human Gate 2
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html`
  (`#caption.stage` CSS + toggle), `content/video_engine/scripts/build_scene_timeline_f.py`
  (`caption_modes` declaration), `content/video_engine/scripts/gate_motion_density.py`
  (M08 FAIL path; stage windows as events), `content/video_engine/tests/test_gate_motion_density.py`,
  `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` (§9.25 "shipped")
- Acceptance: with no dock active the caption sits centred in the quiet
  zone at 64px, each word entering scale 1.16 → 1.0 with the alternating
  ±2.5° tilt settling in ~6 frames, keywords accented, weight stepped not
  ramped; on dock enter it demotes to the anchor inside 0.75s; the
  side-by-side of 0:57-1:11 is rendered to `build-f/render/stage-vs-anchor-0057.mp4`
  and the operator's pick is recorded in §9.25; M08 FAILs a declaring
  build whose still stretches lack stage rows and PASSes one that has them.
- Validate: `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q`
  then `python content/video_engine/scripts/render_episode.py --range 57 71 --out build-f/render/stage-vs-anchor-0057.mp4`
  (two passes, one per mode) and the operator's pick
- Evidence: pending

### T6: One row, one verdict - the audit defers to the opening gate
- Status: pending
- Owner: speedster (→ `general-purpose`)
- Depends on: T1
- Write set: `content/video_engine/scripts/audit_script_doctrine.py`
  (doc-38 beat 1-4 rows print "owned by gate_opening_structure" when
  `<script>-GATES.md` exists beside the script), `content/video_engine/tests/test_audit_defers.py`
- Acceptance: with a gates report present the audit emits zero doc-38
  beat 1-4 findings and one INFO pointer; without it, behaviour is
  unchanged; no other audit rows move.
- Validate: `python -m pytest content/video_engine/tests/test_audit_defers.py -q`
- Evidence: pending

## Verification

```powershell
python -m pytest content/video_engine/tests -q -k "gate or audit or enumerate or motion"
python content/video_engine/scripts/run_script_gates.py content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-G-VO.txt --ring spike --counterparty Bravos --timeline content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/timeline.json
python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f --timeline steel-and-paper.timeline.json
python scripts/prp_validate.py .claude/PRPs/plans/P34-GATE-IMPROVEMENTS.plan.md
```

Baselines that must stay red: opening gate on ep1 = 26 FAIL (G09 promise
1:20, G02 no breath, G34 concession run 3:10, G35 hedged proof 2:44, the
undeclared classical beats); motion gate on ep1 build-f = 4 FAIL (M01 23%
still, M03 197s without evidence from 10:09, M05 four plates > 20s, M07
opening minute rank 5/14).

## Evidence And Handoff

- Per slice: the test run output, the report file path
  (`<script>-GATES.md`, `<script>-SCREENS.md` DECLARED section,
  `build-f/GATES-MOTION.md`), and the commit sha.
- T5: the side-by-side render path and the operator's recorded pick.
- Close: `main` fast-forwarded to the branch; the memory
  `screen-never-still` and `claude-md-imports-agents-md` updated with the
  runner command; the Steel and Paper re-script work order cites both
  gate reports as its acceptance.
