---
id: P36-VIEWER-PERCEPTION-TEST
title: The viewer - a blind, windowed perception test that measures whether the declared structure survives the read
status: complete
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-09-03
updated: 2026-09-03
---

# The Viewer

## Summary

Three roles check a script. The **gates** (mechanical) enforce structure
from text and timing. The **judge** (an agent that knows the doctrine)
verdicts the declared beats and the JUDGE rows against our criteria with
the ledger and the dossier open (CHECK-RESPONSIBILITIES §3). This plan adds
the third: the **viewer**, an agent that knows nothing - no doctrine, no
tags, no ledger - and reads the script cold in 15-second windows with a
rolling two-window memory, reporting per window what it now knows, what
question it is holding, what it was asked to do, and what it could not
follow. A deterministic scorer turns those perception reports into two
measures: **beat recall** (does every declared beat show up in the viewer's
felt questions / new information within ±1 window - rule R2's laundering
measured from the outside) and **information gain per window** (new
concrete things; dead windows and two-dead-in-a-row). The viewer is never
asked when it would drop: an LLM's patience and inference speed are not a
human's, so the instrument asks only for perception reports it can give
stably, and the scorer does the judging.

Operator framing (2026-09-03): *"The judge is judging our criteria and
needs to know what to judge against. … We can't ask an agent 'when would
you drop?' and get a valuable answer. It has to be a time-bounded,
information-gain or quality-based measurement. The gates + judge force
our structure; the viewer tests if it's perceptible."*

Decisions taken by click (2026-09-03): window 15s with a rolling
TWO-window memory (*"that makes us have to argue it if we're really going
30 seconds without value"*); primary score undecided between recall-as-FAIL
and both-gated → resolved by the promotion rule: **advisory until ep1
calibrates, then recall FAIL / gain WARN**; lane **Codex headless**,
strongest available model, reasoning **high** (the plates' low effort was
for orchestration, not reading); calibration = **ep1's windows must match
the analytics drop** before anything FAILs.

## Intent And Acceptance

Intent: a script whose declared beats a blind reader cannot feel does not
record, once the instrument has proved itself on the episode whose
analytics we hold.

Acceptance:
- `python content/video_engine/scripts/viewer_windows.py <script> [--timeline build-f/timeline.json] [--window 15 --memory 2]`
  cuts the script into windows on the take's word timings (or the kit's
  speech rate before a take) and writes `<script>-VIEWER-WINDOWS.json`:
  window index, mm:ss span, the words, and the two-window memory each
  call may see.
- `python content/video_engine/scripts/viewer_run.py <script> [--lane codex] [--model <m>] [--effort high]`
  runs the four perception questions per window through Codex headless
  (one call per window, memory = the previous two windows' text, nothing
  else), writing `<script>-VIEWER-REPORTS.json` (per window: new_things[],
  held_question, asked_of_me, could_not_follow[]). Prompt text lives in
  `content/video_engine/configs/viewer_prompt.v1.md` and is versioned.
- `python content/video_engine/scripts/viewer_score.py <script>` joins the
  reports with the declared beats (`beat_tags.find_beats` + the opening
  gate's clocks) and emits `<script>-VIEWER.md` with: BEAT RECALL (each
  declared tag → perceived / not perceived within ±1 window, with the
  viewer's line that matched), INFO GAIN per window (count of new concrete
  things - a number, a name, an object, a mechanism), OPEN-LOOP coverage
  (share of windows holding a question), DEAD windows (gain 0) and
  dead-runs (two in a row), CONFUSION flags; a summary line in the gates
  report's shape.
- `run_script_gates.py` gains a VIEWER block (advisory: INFO rows) and the
  CHECK-RESPONSIBILITIES §5 report contract gains the block; the runner's
  VERDICT ignores the viewer until promotion (Human Gate 1).
- Calibration on Script G as recorded (`SCRIPT-G-VO.txt` + build-f
  timeline): the windows covering 0:45–1:00 and the dock-held stills the
  motion gate lists (0:33, 0:57, 2:24, 6:53, 8:14, 12:24) come back low on
  gain and/or empty on held questions relative to the script's median;
  the declared-beat recall of the conforming test fixture is ≥ 90%. The
  calibration report is `steel-and-paper/SCRIPT-G-VIEWER-CALIBRATION.md`
  with the per-window numbers beside the retention curve's drop points.
- After Human Gate 1: beat recall < 100% of required beats → FAIL in the
  runner; a dead-run → WARN; gain per window reported.

## Scope

- `content/video_engine/scripts/viewer_windows.py`, `viewer_run.py`,
  `viewer_score.py`, `content/video_engine/configs/viewer_prompt.v1.md`
- `content/video_engine/scripts/run_script_gates.py` (VIEWER block)
- `content/video_engine/tests/test_viewer_windows.py`,
  `test_viewer_score.py` (the runner is tested with a recorded fixture of
  reports; no live calls in tests)
- Docs: `patterns/CHECK-RESPONSIBILITIES.md` (§0 a fourth verdict kind:
  PERCEIVED; §2 viewer row; §5 VIEWER block), `PIPELINE.md` (stage 4b),
  `29-EVIDENCE-MOTION-STANDARDS.md` cross-reference only, `CAPABILITIES.md`
  row, `docs/portable/OPERATOR-RULINGS.md` (E26: the three roles)

## Not Building

- A drop-off predictor. The viewer never says when it would leave.
- Teaching the viewer the doctrine, the ledger, the dossier or the tags.
  If it can see them the test is void.
- A judge agent. The judge stays the runtime agent per
  CHECK-RESPONSIBILITIES §3 (a later PRP may automate it separately).
- Live LLM calls inside pytest.
- Promotion to FAIL before the ep1 calibration passes (Human Gate 1).

## Human Gates

1. **Promotion** - GRANTED 2026-09-03 (operator, on the calibration report:
   *"your recommendations sound correct, implement"*): beat recall binds as a
   FAIL, confusion as a WARN, information gain stays INFO with no authority
   because it read green on ep1. Gating is the runner's default;
   `--no-viewer-gate` reports without binding. History: the operator confirms
   the instrument agrees with the analytics drop; only then does beat
   recall become a FAIL row and gain a WARN row. Until then the VIEWER
   block is advisory (INFO). DECIDED by click 2026-09-03: this is the
   rule; the confirmation itself waits on the calibration numbers.
2. **The questions** - the four perception questions in
   `viewer_prompt.v1.md` are shown to the operator with the first ep1 run's
   sample answers before the calibration is trusted; wording changes bump
   the prompt version.
3. **Window and memory** - DECIDED by click: 15s, rolling two-window
   memory. Revisit only if calibration shows the instrument blind to the
   8–30s gap beat.

## Mandatory Reads

- `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md` (§0 the
  verdict kinds, R2 laundering, §5 the report contract the VIEWER block
  joins)
- `docs/content-video-engine/patterns/STRENGTH-LOOP.md` §8/§8a (automate
  only the unambiguous; the enumeration is the deliverable)
- `docs/portable/OPERATOR-RULINGS.md` E27 (the order of what matters: the package answered, then the voice)
- `docs/content-video-engine/31-FACELESS-CHANNEL-DOCTRINE.md` (the
  retention clock: new information every 15–30s; the One Minute Wall)
- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §9.29–9.30
  (E24/E25: the drop-off diagnosis the calibration is measured against)
- `content/video_engine/scripts/beat_tags.py`, `gate_opening_structure.py`
  (declared beats and their clocks), `kit_spec.py` (speech rate),
  `run_script_gates.py` (the runner's tool shape), `audit_script_doctrine.py`
  (`load_timings`, the `words` timeline shape: `[{w, start, end, part}]`)
- `docs/runbooks/HEADLESS_CLAIM_RESUME.md` and the memory
  `codex-fulfillment-flow` (Codex headless: four binaries, `--approve-for-me`,
  stdin from /dev/null, stdout to a log; `-m <model>` and
  `-c model_reasoning_effort=high`)
- No `backend-patterns` / `frontend-patterns` routing: Python CLI + one
  prompt file.

## Execution Path

1. T1 windows (pure, tested) and T2 the prompt + runner (Codex headless)
   in parallel - disjoint write sets.
2. T3 the scorer after T1 (needs the window shape) using a recorded
   fixture of reports; T4 the runner block after T3.
3. T5 calibration on ep1 after T2+T3: a real run, the report beside the
   analytics drop points; Human Gate 1 reads it.
4. Docs ride in each slice.

## Patterns To Mirror

- Tool shape: `Gate`/`Finding` rows, `RESULT:` line, exit code; the runner
  cites each tool's own line (R5) - `gate_opening_structure.py`,
  `run_script_gates.py`.
- Windowing from word timings with the dual estimator fallback -
  `audit_script_doctrine.load_timings`, `kit_spec.CHARS_PER_SEC`.
- Headless generation: the claim runbook's `codex exec` invocation, log to
  a file, never interactive.
- Tests: red on the known-real ep1 artifact (skip if absent), green on the
  conforming fixture in `tests/test_gate_opening_structure.py`; recorded
  reports as fixtures under `tests/fixtures/viewer/`.
- Doctrine-cited constants at the top (`WINDOW_S = 15.0  # P36 click 2026-09-03; doc 31 retention clock`).

## Task Slices

### T1: Windows
- Status: done
- Owner: junior_developer (→ `general-purpose`)
- Depends on: none
- Write set: `content/video_engine/scripts/viewer_windows.py`, `content/video_engine/tests/test_viewer_windows.py`
- Acceptance: windows of `WINDOW_S` cut on word boundaries from the take's `words` (never mid-word), or from the kit rate when no take exists (reported as estimated); each window carries its mm:ss span, its words, and the memory text of the previous `MEMORY_WINDOWS` windows; beat tags and pause marks are stripped from what the viewer sees (`beat_tags.strip_marks`); ep1 → ~54 windows; the conforming fixture → its window count; JSON written beside the script.
- Validate: `python -m pytest content/video_engine/tests/test_viewer_windows.py -q`
- Evidence: commit fbfcd7f; `viewer_windows.py` (word-boundary cut on the take's own times, `--timeline` > `load_timings` > kit rate, `beat_tags.strip_marks` applied inside `build_windows` so every path into the viewer is stripped, empty windows kept so index i always means the same clock); `pytest test_viewer_windows.py -q` 17 passed; ep1 -> 54 windows, `timing_source: measured`, runtime 806.5s, `SCRIPT-G-VIEWER-WINDOWS.json` committed as the calibration input. Deviation: none to the JSON shape

### T2: The prompt and the headless runner
- Status: done
- Owner: implementation_luna (→ `general-purpose`)
- Depends on: none (T1's JSON shape is fixed in this plan)
- Write set: `content/video_engine/configs/viewer_prompt.v1.md`, `content/video_engine/scripts/viewer_run.py`
- Acceptance: WINDOW 0 is the package: the viewer is shown the thumbnail (`--thumb-file`) and the title and asked one question - "what were you promised?" - and window 1's report adds "was the promise answered, and by which sentence?" (E27: the package answered is the first measure; E24's G45 is only the proxy); then the prompt gives the viewer ONLY the memory text and the window text and asks the four questions, answering in strict JSON; `viewer_run.py` calls Codex headless once per window (`-m` strongest available, `-c model_reasoning_effort=high`, `--approve-for-me`, stdin /dev/null, per-window log), retries a malformed JSON once, records model + prompt version + timestamps, and writes `<script>-VIEWER-REPORTS.json`; a `--dry-run` writes the prompts without calling; a `--limit N` runs the first N windows.
- Validate: `python content/video_engine/scripts/viewer_run.py <conforming fixture> --limit 3` produces three well-formed reports; `--dry-run` on ep1 writes 54 prompts
- Evidence: commit ccafd99; `viewer_prompt.v1.md` (v1, three sendable blocks; a leak scan of the sendable text finds none of beat/tag/doctrine/phase/retention/hook/gate/structure - the worked example is about a bakery so it primes nothing of ours) and `viewer_run.py` (pure `render_prompt`/`parse_response` seams, one call per window, retry-once then record the error and continue, reports rewritten after every window). Deviation, and it matters: the call's `--cd` points at an EMPTY directory outside the repo - codex discovers AGENTS.md by walking upward, so running it inside the checkout would hand the viewer the whole doctrine and void the test. Fixed live during the smoke test: `-i/--image` is VARIADIC and swallowed the positional prompt, so the package call fell back to stdin and failed twice; the image now precedes the non-variadic `-c` that closes the list

### T3: The scorer
- Status: done
- Owner: implementation_luna (→ `general-purpose`)
- Depends on: T1
- Write set: `content/video_engine/scripts/viewer_score.py`, `content/video_engine/tests/test_viewer_score.py`, `content/video_engine/tests/fixtures/viewer/`
- Acceptance: joins reports with declared beats and clocks; BEAT RECALL per tag (perceived within ±1 window when the viewer's held_question or new_things matches the beat's sentence by token overlap ≥ the constant, listing the matching viewer line); INFO GAIN per window (concrete = contains a numeral, a capitalised name, or a noun the window introduces - the rule is constant-cited and crude on purpose); OPEN-LOOP coverage; DEAD windows and dead-runs; CONFUSION; a `RESULT:` summary line; `<script>-VIEWER.md`. Tests: a recorded fixture where a declared [rehook] is never perceived → recall < 100%; a fixture with a dead-run → flagged; determinism (same input, same file).
- Validate: `python -m pytest content/video_engine/tests/test_viewer_score.py -q`
- Evidence: commit fbfcd7f; `viewer_score.py` - BEAT RECALL joins the writer's declarations to the blind reports by content-token overlap (floor of 2 tokens AND 20% of a long beat sentence; the ratio alone let one shared word like 'steel' count as feeling a beat, caught by the fixture and tightened), INFO GAIN by the CONCRETE_RULE constant, plus open-loop coverage, dead-runs, confusion; levels are always computed here and bound only by the runner. `pytest test_viewer_score.py -q` 14 passed; recorded fixtures under tests/fixtures/viewer/. Verified against the real ep1 windows: all 37 declared beats place, recall 0% on an empty report set

### T4: The VIEWER block in the runner and the report contract
- Status: done
- Owner: junior_developer (→ `general-purpose`)
- Depends on: T3
- Write set: `content/video_engine/scripts/run_script_gates.py`, `content/video_engine/tests/test_run_script_gates.py`, `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md`, `docs/content-video-engine/PIPELINE.md`
- Acceptance: when `<script>-VIEWER.md` exists beside the script the runner appends a VIEWER block (recall %, dead windows, open-loop coverage) as INFO rows that never change the VERDICT (advisory); a `--viewer-gate` flag (off by default; on after Human Gate 1) makes recall < 100% a FAIL and a dead-run a WARN; §5 gains the block; PIPELINE stage 4b.
- Validate: `python -m pytest content/video_engine/tests/test_run_script_gates.py -q`
- Evidence: commit fbfcd7f; `viewer_rows` / `viewer_block` / `viewer_path` in run_script_gates.py; advisory by default (every row shown at INFO, counts returned zero, the block says Human Gate 1 is not granted), `--viewer-gate` promotes FAIL/WARN and `verdict_line` gains a viewer term; `pytest test_run_script_gates.py -q` 18 passed (5 new). CHECK-RESPONSIBILITIES §5 and PIPELINE stage 4b ride with T5's docs commit

### T5: Calibration on Script G
- Status: done (Human Gate 1 open: the promotion ruling is the operator's)
- Owner: parent
- Depends on: T2, T3
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-G-VIEWER-REPORTS.json`, `SCRIPT-G-VIEWER.md`, `SCRIPT-G-VIEWER-CALIBRATION.md`, `docs/portable/OPERATOR-RULINGS.md` (E26), `docs/content-video-engine/CAPABILITIES.md`
- Acceptance: the full ep1 run (54 windows, high effort); the calibration report places each window's gain and held-question beside the retention curve's drop points (0:45–1:00; the dock-held stills) and states, window by window, whether the instrument agrees; the four questions and three sample answers are shown to the operator (Human Gate 2); the operator's promotion ruling (Human Gate 1) is recorded in E26 and, if granted, `--viewer-gate` becomes the runner's default in a follow-up commit.
- Validate: the three files exist; `viewer_score.py` on ep1 exits 0; the calibration report cites the analytics drop points by mm:ss
- Evidence: commit follows; full ep1 run 54/54 windows + the package window, high effort, 0 errored; `SCRIPT-G-VIEWER-REPORTS.json`, `SCRIPT-G-VIEWER.md`, `SCRIPT-G-VIEWER-CALIBRATION.md`. RESULT 1 FAIL / 1 WARN / 2 PASS / 1 INFO. Calibration verdict PARTIAL: the package measure and beat recall agree with the analytics (the reader is promised 'why the AI boom may be a bubble and what endures', reports the promise 'not yet' answered at w1, and four of the twelve unperceived beats - payoff, reflect, opponent, rehook - are exactly the beats the annotated gate placed outside their windows); INFORMATION GAIN DOES NOT - w3 (0:45-1:00, where viewers actually leave) scores 5 against a median of 3, every dock-held still scores at or above median, and there is no dead window in the episode, so promoting gain would add a row that stays green on the one episode we know failed. Confusion DOES track: 22 real misses after filtering 20 window-cut artifacts (that filter is now in the scorer), ten of them unresolved referents, and one finding no other instrument produced - 'Bravos' is unfollowable at 6:45, 9:00, 12:00 and 13:00, i.e. the counterparty evaporates mid-argument. Recommendation to Human Gate 1: promote recall to FAIL, keep gain at INFO, promote confusion to WARN in gain's place. The runner shows the block advisory on ep1 and the VERDICT is unchanged (2 failing tools, none of them the viewer)

## Verification

```powershell
python -m pytest content/video_engine/tests/test_viewer_windows.py content/video_engine/tests/test_viewer_score.py content/video_engine/tests/test_run_script_gates.py -q
python content/video_engine/scripts/viewer_windows.py content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-G-VO.txt --timeline content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/timeline.json
python scripts/prp_validate.py .claude/PRPs/plans/P36-VIEWER-PERCEPTION-TEST.plan.md
```

Baselines: Script G was annotated with its 37 real beats on 2026-09-03 (the
gate-calibration pass, commit 977fb36), so ep1 now carries declared beats and
recall IS measurable on it - the calibration uses BOTH: the conforming fixture
for a clean-recall control and ep1 for recall plus the gain/open-loop agreement
with the analytics drop.

## Evidence And Handoff

- Per slice: test output, the artifact path, the commit sha.
- T5: the calibration report and the operator's promotion ruling.
- Close: `main` fast-forwarded; CAPABILITIES row; the re-script work order
  (REWRITE-ORDER-G) gains the VIEWER block as part of its acceptance once
  promoted; memory `viewer-perception-test` written with the three roles
  and the "never ask when it would drop" rule.
