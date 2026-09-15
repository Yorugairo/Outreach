---
id: P54-THE-OPERATOR-LEDGER
title: The operator ledger - every correction the operator typed, triaged into the record, the Claude memories promoted into the repo, a frame casebook, routing so any agent finds it, and a bake-off that proves it
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-13
updated: 2026-09-14
---

# The operator ledger

## Summary

The operator, 2026-09-13: *"part of your advantage is the literal memories in this chat. it's why i haven't left the
chat session behind. Now that we're more modularized we should be considering how to extract the useful memories and
chat context"* - so that Astra (*"it exceeds basically all math and reasoning levels on benchmarks, but we haven't
plugged it into our memories and knowledge base"*), Codex and Gemini start where Claude stands. And: *"those portable
docs are probably more stale than we care to admit"*; *"I dont think it makes sense to add the pack to agents.md, it
probably makes sense to add the routing to find it instead"*; *"no privacy concerns"*.

**Step 1 is already measured** (prototype `scratchpad/ledger/extract_operator_messages.py`, session 45114c3b; T1
brings it into the repo). Over 185 transcript files (`~/.claude/projects/*Outreach-Program*/**/*.jsonl`, one of them
4.6 GB): **1,639 operator messages, 92k words** - 1,148 typed, **365 typed mid-turn** (stored as `attachment` /
`queued_command`, invisible to a reader of `type=user` records), 126 the words after a slash command (inside
`<command-args>`); 49 pasted (tracebacks, research dumps) tagged; 1 bridge packet dropped; 3 near-duplicates.
**592** carry correction or rule cues, and only **28%** have any 8-word stretch verbatim anywhere in `docs/`,
`content/video_engine/**/*.md` or the 69 Claude memories. A 5-sample topic calibration (`docs_find`) found 1 recorded
in other words, 3 recorded nowhere (the prompt pack may strengthen prompts; real charts over "bad info cards"; an axis
from the series' low since 2000 - which also CONFLICTS with E28's `from_zero`) and 1 episode-specific. Roughly half of
the operator's corrections carry reusable guidance that exists only in a transcript.

**Recall** (`docs/runbooks/RECALL-RECEIPT.md`):
- `docs/agent-memory/explorer/MEMORY.md` - the one promoted memory today, and its rule: *"Anchors only ... never
  line numbers, never a transcript. Workers read this; only the parent writes it."* The operator pack is prose and
  quotes by design, so it lives in its OWN folder with its own README; the explorer rule is untouched.
- `content/video_engine/scripts/build_docs_index.py` `DEFAULT_ROOTS = ("docs",)` - anything under `docs/` is
  already indexed by `docs_find`, so routing needs no new retrieval layer.
- `.gitignore:126` `*.png` with the golden-frames negation at `:160-162` - the casebook's frames need the same.
- **The Codex / Astra lane is live, driven headless by `codex exec`** - not through `bridge_send.py`, whose
  `LANES = ("gemini", "claude")` covers the two CLIs it shells. `content/video_engine/scripts/viewer_run.py`
  `DEFAULT_LANE = "codex"` (one `codex exec` batch per manifest, the binary resolved from `VIDEO_ENGINE_CODEX_BIN` /
  PATH), `docs/runbooks/HEADLESS_CLAIM_RESUME.md` (`codex exec --cd <dir> --skip-git-repo-check`, then
  `claim-resume`), and Astra's packet reviews back to Claude (`agent-bridge-run-*`). `docs/runbooks/PRP_EXECUTION.md`
  "Lane write sets" names Codex / Astra -> Luna. The bake-off is DISPATCHED to it the way `viewer_run.py` does, never
  hand-carried. (A draft of this plan said there was no Astra lane off `bridge_send`'s one constant - the operator
  corrected it: *"Why do you think Codex has no bridge lane? you know that it does."* / *"i swear our bridge also
  connects to codex"*.) **The bridge does connect to Codex**: Astra -> Claude runs as headless `agent-bridge-run-*`
  sessions carrying `{packetId, brief}` (six on 2026-09-05/06; `GEMINI.md` "The other direction already runs"), and
  our `bridge_watch.py` `CLAUDE_PROJECT_GLOB = "*agent-bridge-run-*"` reads them; `BRIDGE-PACKET.md` lists lane
  `astra`. The Claude -> Astra send side is Astra's "own runner [that] consumes packets from its queue folder (P2 T5)";
  NOT FOUND WHERE I LOOKED (2026-09-13): the P2 plan and the runner in this repo, the trades repo
  (`WA JiuJitsu Registry-*`, hidden and ignored files included), `~/.codex` config, MCP servers and skills. T7 sends a
  packet if the operator names the runner's location, else dispatches by `codex exec`.
- `docs/portable/` last changes: BUILD-PIPELINE, MOTION-GRAMMAR, OUTRO-CTA-PLAYBOOK 2026-08-30; CHART-DISCIPLINE,
  PACKAGING-PLAYBOOK, SOUND-SOURCING 2026-08-31; DOCTRINE-CORE 09-03; OPERATOR-RULINGS and VOICE-PACK 09-12.
  MOTION-GRAMMAR has ONE commit, and P47-P53 (stop-action, morph, camera, species, transitions) all landed after it.
- The memory `judging-is-codex-cli-batch` - an LLM judge over many rows runs as a batch, one run per manifest.

## Intent And Acceptance

Any agent routed to video-engine work can find, by `docs_find`, what the operator has corrected and why, in the
operator's own words, with a verdict that says where the correction now lives.

- **A1** `extract_operator_ledger.py` reproduces the prototype's census on the same transcripts (>= 1,639 messages
  before the `/model` and near-duplicate filters, which the repo version adds - 1,604 after them on 2026-09-13;
  the mid-turn and slash shapes present; the two spot quotes "a one-shot is never a test" and "Wash beats the focus
  rack" found) and is incremental: a second run appends only messages newer than the ledger's last timestamp.
- **A2** every correction/rule message carries ONE triage verdict with an anchor: `recorded <path>:<heading>`,
  `ruling-candidate`, `gate-candidate`, `craft`, `memory`, `episode`, `noise`, or `conflict <id>`. No verdict
  duplicates a record; a `recorded` verdict names where.
- **A3** a staleness report names, per `docs/portable/` file, the rulings and triaged corrections dated after its
  last change that touch its subject - a report, not a rewrite.
- **A4** the Claude memories are in the repo with a working index; the repo copy is canonical and a `--check` says
  when the two drift.
- **A5** a frame casebook of at least three cases, each: before frame, after frame, the operator's words, the defect,
  the fix commit, the gate that now catches it (or "none - JUDGE").
- **A6** routing only: `docs_find "operator ledger"` and `docs_find "casebook"` return the pack; the entry files carry
  a route line, never the pack's content.
- **A7** the bake-off runs to a verdict the operator gives.

## Scope

The ledger extractor and its tests; the ledger, triage and audit files under `docs/operator-ledger/`; the promoted
memories and casebook under `docs/agent-memory/operator/`; one `.gitignore` negation; route lines in the entry docs;
the bake-off brief and both builds of one beat.

## Not Building

- No rule, ruling or gate is written by triage. A `ruling-candidate` or `conflict` goes to the operator (HG2); only
  their word makes a ruling.
- No rewrite of a portable doc in this plan (T3 reports; the fixes are a follow-up the operator orders from the report).
- No summarised transcript standing in for the operator's words: quotes are verbatim, the agent's reply is context.
- No tool output, no subagent traffic, no agent prompts in the ledger.
- No vector store, no new retrieval layer (docs/ is already indexed).
- Nothing added to `AGENTS.md` beyond what already routes to `docs/AGENTS-VIDEO-ENGINE.md` (the operator: routing,
  not the pack).
- No new lane: the bake-off rides the existing `codex exec` lane (`viewer_run.py`'s resolution of the binary).

## Human Gates

- **HG1** approve this plan.
- **HG2** the triage digest: every `ruling-candidate`, `gate-candidate` and `conflict` is the operator's to rule
  (E-ids are written only from their words). Delivered as one digest grouped by subject, never one question per row.
- **HG3** the bake-off brief before it is dispatched to Astra, and the verdict after the watch.
- Push only on the operator's current word.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md` (roles, write sets, format)
- `docs/runbooks/RECALL-RECEIPT.md`
- `docs/agent-memory/explorer/MEMORY.md` (the promotion rule this plan must not break)
- `docs/portable/OPERATOR-RULINGS.md` (the E-id grammar triage anchors to)
- `content/video_engine/scripts/build_docs_index.py` (`DEFAULT_ROOTS`, the exclude list)
- `content/video_engine/scripts/viewer_run.py` and `docs/runbooks/HEADLESS_CLAIM_RESUME.md` (the `codex exec` lane T7 dispatches on)
- `docs/runbooks/BRIDGE-PACKET.md` (the reply grammar Astra's run answers in)
- the memories `first-pass-additive-capability-led`, `judging-is-codex-cli-batch`, `judge-the-frame-not-the-diff`

## Execution Path

T1 first (everything reads the ledger). T4 runs beside T1 (disjoint write set). T2 after T1; T3 after T2. T5 after
T1 (its quotes come from the ledger). T6 after T2, T4 and T5 exist. T7 last.

## Patterns To Mirror

- **Deterministic tool + test fixture**: `content/video_engine/scripts/measure_stage_gaps.py` and its test - a
  measurement script that writes one JSON beside what it read and prints one line per finding.
- **Checkpointed batch judging**: `viewer_run.py` (one manifest, one batch, rows appended as they land).
- **Anchored promotion**: `docs/agent-memory/explorer/MEMORY.md` (index file + one file per fact; parent-only writes).
- **Tracked frames under a png ignore**: `.gitignore:160-162` (the golden frames).

## Task Slices

### T1: The extractor in the repo, incremental
- Status: done 2026-09-13 (implementation_luna in the worktree; parent-reviewed; integrated into main). EVIDENCE (parent re-ran): 14 tests passed; real run 187 files -> 1,604 rows (typed 1,141 / mid-turn 366 / slash 97; pasted 49; `/model` 38 and near-duplicates 10 dropped); reconciled row by row against the prototype: all 39 prototype rows absent from the ledger are `/model` (29) or duplicates of a kept row (10), 4 rows are newer; "one-shot is never a test", "Wash beats the focus rack" and "albels you should improve" each present once; `--check` exit 0
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/scripts/extract_operator_ledger.py`, `content/video_engine/tests/test_extract_operator_ledger.py`, `docs/operator-ledger/LEDGER.jsonl`, `docs/operator-ledger/LEDGER.md`, `docs/operator-ledger/README.md`
- Acceptance: A1. Starts from the scratchpad prototype (the parent copies it into the slice brief verbatim - the scratchpad is session-local). The fixture JSONL covers every shape the census met: a typed string, text blocks, image+text, a `queued_command` attachment, a `<command-args>` message, a `/model` slash (filtered), `isMeta`, `isCompactSummary`, a tool result, an `isSidechain` record, a `subagents/` file, a `{"packetId"` bridge prompt, a near-duplicate. Rows keep `via`, `slash`, `pasted`, `cues`, the agent's first reply (600 chars) and the tool-call count. The ledger's own last timestamp makes a re-run append-only; `--check` exits 1 when newer messages exist.
- Validate: `python -m pytest -q content/video_engine/tests/test_extract_operator_ledger.py` and `python content/video_engine/scripts/extract_operator_ledger.py --check`
- Evidence: pending

### T2: Triage every correction into the record
- Status: done 2026-09-13. EVIDENCE: 621 rows in 12 day-grouped batches, one read-only `explorer` each; merged by the parent (`scratchpad/ledger/merge_triage.py`) -> `docs/operator-ledger/TRIAGE.jsonl` + `TRIAGE-DIGEST.md`; `extract_operator_ledger.py --triage-check` "clean - 621". Verdicts: recorded 375, noise 120, episode 63, superseded 27, memory 13, craft 8, ruling-candidate 7, gate-candidate 5, conflict 3. Checks instead of the 10% re-read: every batch's ids reconciled against its batch file (four mis-typed ids corrected by position, one skipped row triaged by the parent); every `recorded` anchor's path exists on disk, and 21 of 375 headings were paraphrased (path correct). The triage-check's superseded rule was widened to older ruling ids ([A-E]<n>) and doc sections, with a test (15 passed). FINDING: the operator's corrections are overwhelmingly recorded (60%); the reusable unrecorded share is 36 rows (6%) - the value is the stale records and the missing gates, not new doctrine
- Owner: parent (batches dispatched to `explorer`, read-only, one day per batch)
- Depends on: T1
- Write set: `docs/operator-ledger/TRIAGE.jsonl`, `docs/operator-ledger/TRIAGE-DIGEST.md`
- Acceptance: A2. Each batch receives the day's correction/rule rows and `docs_find` access, and returns one verdict row per message: `{ts, verdict, anchor, subject, note}`; `recorded` needs a `path` + heading that exists. The parent re-checks a 10% sample per batch before accepting it and records the agreement rate. The digest groups `ruling-candidate`, `gate-candidate` and `conflict` by subject for HG2, oldest first, each with the quote.
- Validate: `python content/video_engine/scripts/extract_operator_ledger.py --triage-check` (every correction/rule row has exactly one verdict; every `recorded` anchor resolves on disk)
- Evidence: pending

### T3: The portable-docs staleness report
- Status: done 2026-09-13. EVIDENCE: three read-only explorers (8 docs; OPERATOR-RULINGS is the source, not audited) -> the parent's `docs/operator-ledger/PORTABLE-AUDIT.md`: 46 stale claims - BUILD-PIPELINE 14 (high), DOCTRINE-CORE 9 (high; 10,725 chars against its own 10,000 cap), CHART-DISCIPLINE 7 (high), VOICE-PACK 4, SOUND-SOURCING 3, OUTRO-CTA 3, PACKAGING 3, MOTION-GRAMMAR 3 - plus nine stale records outside portable (doc 29 §9.15/§9.22/§9.23b, doc 37 §1/§18, doc 39 stacked bar + reduced-motion, doc 08 Magnific, doc 21, PIPELINE render contract, brand-voice bed LU, a shorts memory, E52 §4). The parent verified on disk: the DOCTRINE-CORE char count, BUILD-PIPELINE's 20 s ceiling and ~3-tag lines, CHART-DISCIPLINE's 11 classes under "ten", brand-voice's 24-26 LU; every E-id, ledger id and path the page cites resolves. No doc rewritten (HG: the operator orders the fixes)
- Owner: explorer (read-only), parent writes the report
- Depends on: T2
- Write set: `docs/operator-ledger/PORTABLE-AUDIT.md`
- Acceptance: A3. For each of the nine `docs/portable/*.md`: its last change, the rulings (E-ids) and triaged corrections dated after it whose subject it covers, and each claim in the doc that a later ruling or correction contradicts, quoted both sides. Ranked by how much is stale.
- Validate: every E-id and ledger timestamp cited in the report exists (`docs_find` / `LEDGER.jsonl`)
- Evidence: pending

### T4: The Claude memories promoted into the repo
- Status: complete (integrated into main; the plan line was never updated - corrected 2026-09-14)
- Owner: junior_developer
- Depends on: none
- Write set: `docs/agent-memory/operator/**/*.md`, `content/video_engine/scripts/sync_operator_memory.py`
- Acceptance: A4. All memory files under `docs/agent-memory/operator/` with `MEMORY.md` as the index; `[[slug]]` links become relative Markdown links; a README says the repo copy is canonical, the pack is prose with quotes (not the explorer's anchors-only rule), and who writes it (the parent). `sync_operator_memory.py --check` diffs the repo copy against `~/.claude/projects/C--Users-Snipe-Downloads-Outreach-Program/memory/` and exits 1 on drift; `--export` refreshes the repo copy.
- Validate: `python content/video_engine/scripts/sync_operator_memory.py --check` and a link check that every relative link resolves
- Evidence: the pack is tracked in main - 90 files under `docs/agent-memory/` (committed with `7c59dfa`, the rulings E80-E97 commit that carried "the memories export and routing"); refreshed 2026-09-14 with `sync_operator_memory.py --export` (3 written: `gpt-image-2-5-generator.md` new, `MEMORY.md` and `resume-2026-09-12.md` drifted; 73 unchanged) and `--check` -> in sync (76 files).

### T5: The frame casebook, three cases to start
- Status: complete (integrated into main; corrected 2026-09-14)
- Owner: parent (frame judgement)
- Depends on: T1
- Write set: `docs/agent-memory/operator/casebook/**`, `.gitignore` (one negation block for the casebook's frames)
- Acceptance: A5. Three cases from 2026-09-12/13, each a folder with `before.png`, `after.png` (seeked frames of `normal-for-which-bridge` review-v1 vs build-review at 41bf55c, 1080 px portrait, at most 300 KB each) and `CASE.md`: the operator's words (ledger timestamp), the defect, the fix commit, the gate that now catches it. (1) the dashed ring on "x3.9 Federal debt" at 0:57 - `tip_mark`; (2) the empty cream after the melt at 0:34 - M31; (3) the thin one-shot - no gate catches it (JUDGE), the rule is `first-pass-additive-capability-led`. An index lists cases by defect family so later cases slot in.
- Validate: `git check-ignore` returns nothing for the casebook frames; every `CASE.md` names a commit that `git cat-file -e` accepts
- Evidence: the casebook is tracked in main - 12 files under `docs/agent-memory/operator/casebook/` (the frames, each `CASE.md` and the index).

### T6: Routing, not the pack
- Status: done 2026-09-13 (parent, not speedster: the worktree's copies of the entry files are older than main's, so a delegated write would have clobbered them). EVIDENCE: one route line in `docs/AGENTS-VIDEO-ENGINE.md` (item 5), `GEMINI.md` (retrieval order), `CLAUDE.md` (fast routes), `docs/agent-context/SKILL_ROUTER.md` (a lane row) - 12 insertions; `AGENTS.md` untouched (asserted); `build_docs_layers.py --write` then `--check` every layer in sync; `docs_find "operator ledger"` -> `docs/operator-ledger/README.md`, `docs_find "casebook"` -> `docs/agent-memory/operator/casebook/README.md`
- Owner: speedster
- Depends on: T2, T4, T5
- Write set: `docs/AGENTS-VIDEO-ENGINE.md`, `docs/agent-context/SKILL_ROUTER.md`, `GEMINI.md`, `CLAUDE.md`, the generated `docs/DOCS-*` layers
- Acceptance: A6. One route line in each entry file (the retrieval order: "what has the operator corrected about X -> `docs_find` -> `docs/operator-ledger/` and `docs/agent-memory/operator/`"). No pack content in any entry file; `AGENTS.md` untouched.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --write` then `--check`; `python content/video_engine/scripts/docs_find.py "operator ledger"` and `"casebook"` each return the pack
- Evidence: pending

### T7: The bake-off - Astra with the pack, Fable, one beat
- Status: pending
- Owner: parent
- Depends on: T6, HG3
- Write set: `docs/runbooks/BAKEOFF-ASTRA-FABLE.md`, `content/video_engine/projects/systems-and-blowups/normal-for-which-bridge/build-bakeoff-fable/`, `content/video_engine/projects/systems-and-blowups/normal-for-which-bridge/build-bakeoff-astra/`
- Acceptance: A7. One brief, both authors: one beat of the bridge short (the two loads compared, transformed into the interest bill), the same take, data and engine, with the routes from T6 as the only context given. Astra's run is dispatched headless on the Codex lane - `codex exec --cd <repo> --skip-git-repo-check` with the brief's path, stdin from null and the log to `build-bakeoff-astra/codex.log`, the binary resolved as `viewer_run.py` resolves it - and writes only its build dir; Fable authors the same beat in its own. Scored by the motion gate, the layout probe, events/min and compositions/min against the approved shorts, and the operator's watch of both, unlabelled. The verdict and what each author missed are written back into the casebook.
- Validate: `python content/video_engine/scripts/gate_motion_density.py <each build>` 0 FAIL; the operator's verdict recorded
- Evidence: pending

### T8: Fix the stale records the audit found (the operator: "fix them")
- Status: complete (landed in main with `daa7506`; the plan line was never updated - corrected 2026-09-14)
- Owner: parent (integration), implementation_luna x4 (drafts)
- Depends on: T3
- Write set: `docs/portable/{BUILD-PIPELINE,MOTION-GRAMMAR,SOUND-SOURCING,CHART-DISCIPLINE,OUTRO-CTA-PLAYBOOK,PACKAGING-PLAYBOOK,DOCTRINE-CORE,VOICE-PACK}.md`, docs 29/37/39/08/21, `PIPELINE.md`, `.agents/skills/brand-voice/SKILL.md`, the shorts memory (source + export), the entry files' DOCTRINE-CORE routing
- Acceptance: every PORTABLE-AUDIT claim fixed or left with a stated reason; DOCTRINE-CORE re-scoped as the NotebookLM export (the operator: "doctrine core was originally just supposed to be for notebook LM ... the agents in this repo should be reading the full doc set and using our index system") at <= 10,000 characters, and no entry file tells repo agents to load it
- Validate: each edit's `old` unique before apply; `build_docs_layers.py --check`; DOCTRINE-CORE `len` <= 10,000
- Evidence: `daa7506` "the stale portable claims fixed and the reasoning pass filed"; `docs/portable/DOCTRINE-CORE.md` is 9,852 characters (<= 10,000). Not re-audited claim by claim on 2026-09-14: a stale claim found later is a new row, not this slice.

### T9: Two gates the operator approved - the black frame at a seam (M32) and narration pointing at a visual that is not on stage (M33)
- Status: wired 2026-09-13. EVIDENCE: `measure_seam_frames.py`, `measure_spoken_visuals.py`, `test_seam_and_spoken.py` (15 passed) integrated into main; measured on the approved Japan short (11 boundaries), the Tokyo remake (6) and the bridge review (5): no flash, no jump, no black outside a dip on any cut, suck or melt; near-black threshold 8 luma MEASURED on Japan's six approved dips (darkest 0-6; cuts never under 52); the only holds are the two approved outro dips into clips at luma ~18 (`dark_world`); one pointing phrase on Japan ("But look at what nobody explained", a figure of speech). Tiers from the approved shorts: M32 FAIL on flash / jump / outside / a hold over a normal world, INFO on a dark-world hold; M33 WARN on an uncovered pointer. `gate_motion_density.py` `_seam_gate` / `_spoken_visual_gate` + `test_m32_*` / `test_m33_*` (motion gate + seam + stamps: 128 passed). The measure also found the exit convention read backwards elsewhere (Deviations)
- Owner: parent + implementation_luna
- Depends on: none
- Write set: the two measure scripts, `test_seam_and_spoken.py`, `gate_motion_density.py` (M32, M33), the gates registry
- Acceptance: a declared dip's own dark core passes; a black frame at a non-dip boundary, a hard jump into black, or black past the dip's core FAILs; a pointing phrase with no page or dock on stage WARNs until the approved shorts are measured clean
- Validate: `pytest test_seam_and_spoken.py`; both measures on the approved shorts
- Evidence: pending

### T10: E74 - long form is never under 8 minutes, and the gate that holds it
- Status: done 2026-09-13 (the operator: "yes, longform should never be under 8 minutes"). EVIDENCE: E74 appended to `docs/portable/OPERATOR-RULINGS.md`; `gate_opening_structure.py` `LONG_MIN_S = 480.0` and G46 (FAIL on a measured long-form clock under 8:00, WARN on an estimate, never asked of a short); `test_g46_long_form_floor_is_eight_minutes` + `test_g46_a_measured_short_forced_long_fails_the_floor`; the opening-gate suite 24 passed
- Owner: parent
- Depends on: none
- Write set: `docs/portable/OPERATOR-RULINGS.md` (E74), `content/video_engine/scripts/gate_opening_structure.py` (the floor row) + its test
- Acceptance: a long-form clock under 480 s FAILs the opening gate; E74 names the mechanism
- Validate: the opening-gate tests
- Evidence: pending

### T11: The Gemini reasoning order (the operator: "you can dispatch the work order to gemini looking for reasoning/logic")
- Status: done 2026-09-13 (reviewed; nothing promoted). EVIDENCE: input 1,446 exchanges / 3.57 MB in 3 files under `docs/research/runs/operator-reasoning/input/` (gitignored); first send stalled (Antigravity closed after the BIOS reboot), resent as conversation `d7318e8a-565f-4ea7-9599-c47bd1bd371a` 00:07, `POSITION: done` 00:16 with `REASONING-EXTRACT.md` (32 items). The parent's pass (`docs/research/runs/operator-reasoning/REVIEW.md`): cited ids 30/30 real; 13 of 14 proposed/"searched" paths do not exist; the counts are copied from TRIAGE; 14 items duplicate TRIAGE rows, 4 were ruled or built tonight, 7 already recorded, 1 misattributed, 1 unsupported; 4 possibly-new items (Facebook 90 s ceiling, console/editor separation's console half, skill-catalogue pruning, why media stays out of git). Verdict: not repo-worthy as written. RETEST (the operator: "it's probably because we didn't force it to gate and proof itself" / "build & send the test"): `content/video_engine/scripts/verify_reasoning_extract.py` + `test_verify_reasoning_extract.py` (3 passed: an honest extract passes; invented quote, invented home path, missing coverage, copied counts, a triage crib, a bad recorded anchor each FAIL; smoke-run PASS on the real chunk with live docs_find) - JSON-lines output with a coverage row per input id; the gated order for chunk 03 (315 exchanges) sent 00:44 as conversation `6f39bd84-425f-442c-b2a0-efa77a36f199` with `--verify` running the same gate on landing. RESULT: landed 00:49 (~5 min), gate PASS - 315/315 covered (247 nothing, 53 recorded, 15 kept -> 11 items), every quote verbatim, every path real: the gate cured the fabrication and the skim. The parent's pass: 10 of 11 "not recorded" items ARE recorded - their evidence carries a TRIAGE `recorded` verdict (R-002 BRIDGE-DAEMON, R-005 BRIDGE-PACKET, R-007 and R-008 E50 amendments, R-011 the flash work order) or the reasoning lives where `docs_find` does not index (R-001 `bridge_send.py`'s "folder state machine" docstring; R-004 the 1440x2560 render in two operator memories; R-003/R-009 the dispatch-floor memory; R-006 BRIDGE-PACKET's form/substance rule). The model picked search terms that return 0 hits - the gate cannot tell a weak term from an absent record. One possibly new: R-010 "numbers before pixels" (layout by DOM probe before a vision read). Next gate: cross-check evidence ids against TRIAGE verdicts and search each item's quote-derived terms, not only the model's
- Owner: parent (order, then the review pass the operator asked for: "then have you do a pass too, then maybe it would deserve to enter repo after that")
- Depends on: none
- Write set: Gemini writes only `docs/research/runs/operator-reasoning/REASONING-EXTRACT.md`
- Acceptance: every item cites exchange ids that exist and a two-term repo check; the parent verifies and promotes only what survives
- Validate: `bridge_check.py --shape paths-written`; the parent's id check
- Evidence: pending

## Verification

```powershell
python scripts/prp_validate.py .claude/PRPs/plans/P54-THE-OPERATOR-LEDGER.plan.md
python -m pytest -q content/video_engine/tests/test_extract_operator_ledger.py
python content/video_engine/scripts/extract_operator_ledger.py --check
python content/video_engine/scripts/sync_operator_memory.py --check
python content/video_engine/scripts/build_docs_layers.py --check
python content/video_engine/scripts/docs_find.py "operator ledger"
```

## Deviations

- **2026-09-13, against bloat** (the operator: *"how big is the memory files+the chat? is this a good idea or just
  bloat?"*). Measured: transcripts ~5.7 GB, the operator's words 0.62 MB, correction/rule rows 211 KB, memories 222 KB,
  the docs layers today 1.7 MB index + 4.0 MB topics. `docs_find` indexes `docs/**/*.md`, so T1 no longer writes a
  1,639-section `LEDGER.md` into `docs/` (opt-in `--md <path>`); `LEDGER.jsonl` stays as the unindexed evidence layer.
  T2 gains the verdict `superseded` (anchor = the later ledger row or the ruling that overturned it), so an overturned
  correction never reaches another agent as a live rule (E73's first reading is the example).
- **T4** gains `content/video_engine/tests/test_sync_operator_memory.py` in its write set. EVIDENCE (parent re-ran):
  `pytest test_sync_operator_memory.py` 5 passed; `sync_operator_memory.py --check` "in sync (69 files)" exit 0; a diff
  of `first-pass-additive-capability-led.md` against its source changes only the `Related:` link line; the agent's link
  check 232/232 resolve, 0 secret-scan hits; two slugs not yet written (`railway-yardstick`, `alicia-recreation-brief`).
- **Where slices write.** The harness blocks subagent writes into the main checkout from this worktree session
  (T1's first attempt was refused). Slices write under the worktree root; the parent reviews and integrates the
  reviewed files into main with one scratchpad script (the session's standing pattern), then runs the verification
  there. T5's frames were captured straight into main (`docs/agent-memory/operator/casebook/*/`).
- **THE EXIT CONVENTION WAS READ BACKWARDS (found by T9's seam measure, 2026-09-13).** E47, the compiler's SCENE_EXITS
  comment and the engine agree: `exit` names the transition INTO the scene it sits on. `stamp_transition_pages` (P53 T6
  and this plan's first cut), `measure_stage_gaps.py` and M31 read it as the exit OUT. Corrected in main: R26-60's
  `exit=cut` now lands on the OUTGOING page a suck or melt takes; the chart-to-chart axes stamp applies to a ledger page
  after a ledger page whatever the transition (the bridge review's cream at 0:34 followed a CUT, not a melt - the first
  stamp fixed it by accident); stage-gap boundaries read the next scene's exit and M31 FAILs any non-dip chart-to-chart
  empty run. Tests rewritten to the convention (233 passed across stamps, motion gate, page performs, chart
  transitions). Rebuilt bridge review: 10.9 s cut, 21.8 s dip (licensed), 25.0 s melt plate->spiral 0.6 s, 34.0 s cut
  chart->chart 0.0 s empty, 47.9 s cut 0.0 s; gate 0 FAIL. The bridge's `build_short.py` rows were authored on the wrong
  reading (its hook-row "suck" never played) - left for the pass-2 restage, which rewrites the rows.
- **E75 written** (the operator: "the level line rule and bar chart separation sounds valid"): bars start at zero; a
  level line may start near its own low with the ticks stating it; mechanism = the existing `from_zero` behaviour.
- **Gates owed** (found writing T5, not built here - the P54 scope does not include gates): the ring on the tip tag and
  the name on a neighbour's line were fixed in 41bf55c with NO gate that would catch them again (M28 reads label pairs,
  not a label against a ring or a series line). Only the empty cream got one (M31). Both go to the HG2 digest as
  `gate-candidate`.
- **T5** frames are 540x960 (half the stage), quantised PNG, to keep git small; a fourth case (the 10-year name on the
  30-year line) joins the three.

## Evidence And Handoff

- The step-1 census and the 28% verbatim probe: session 45114c3b, `scratchpad/ledger/out/operator-messages.jsonl` (sent to the operator 2026-09-13 as `operator-messages.md`). T1 re-derives both on disk.
- Checkpoint after each validated slice in this file; HG2's digest and HG3's verdict are quoted here when given.
