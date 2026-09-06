---
id: P45-CORPUS-RECONCILIATION
title: Reconcile the doctrine corpus with what is built - registries, triage, the operator's decisions
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-05
updated: 2026-09-05 (rulings 1-8 in)
---

# Reconcile the doctrine corpus with what is built

## Summary

Everything in the docs came from research, filtered at least twice by models and partly by the
operator, never fully checked (operator, 2026-09-05). Some of it is implemented under other names
(the two-thirds power law is the curvature stroke), some is tracked but unbuilt (FK/IK, zero-slip,
multi-plane inpainting), some is orphaned (the on-1s/on-2s cadence rule), some carries derived numbers
(the 0.22 secondary-motion ratio is a computed extrapolation, a starting reference to test, not a
finding), and "superseded by X" labels came from document compression, not from bad documents - the
compressed docs still hold detail the compressed-into doc dropped.

The plan: let the generated registries (gates, animation and maths, manifest, topics, citations) do the
mechanical review, then one judgment pass that triages every non-implemented item by the operator's
rule - **a recent stumbling gap → top priority; otherwise → backlog or explore; a derived number →
test it as a starting reference, never cite it as research** - and returns the specific decisions only
the operator can make. Output: a triage table with a recommendation per item, backlog and explore rows,
a `[DERIVED]` provenance convention, the craft map, and the discoverability delta measured on the same
ten benchmark questions that were run before any of these layers existed.

## Intent And Acceptance

- Every formula, dial, law and device in the animation docs (29, 42-53, 47, the animation brief, the
  sources bundle) and every script/speech gate and craft device has a registry row with a status
  (implemented / tracked / retired / orphaned) and evidence lines. Acceptance: the registries `--check`
  green, the smoke rows from the 2026-09-05 lead review hold (two-thirds power law implemented, FK/IK
  tracked, on-1s cadence orphaned, 0.22 retired-as-derived).
- Every `orphaned` and `tracked` row is triaged into exactly one of: TOP (addresses a gap we stumbled
  on in the last two weeks - evidence: a ruling E35-E41, a BACKLOG evening read, a memory note, or a
  benchmark finding), BACKLOG, EXPLORE, RETIRE - with the evidence named. Acceptance: `docs/content-video-engine/TRIAGE-2026-09-05.md`
  lists them all; BACKLOG.md carries the TOP rows at the head of its next list and the BACKLOG/EXPLORE
  rows in the right sections; no row without evidence.
- Numbers that are computations over research rather than research carry a `[DERIVED: from <sources>,
  <how>]` marker in the doc where they appear, and the registry surfaces `derived` as a provenance
  field. Acceptance: 0.22 and every other derived figure the pass finds carry it; the intake contract
  in GEMINI.md names the tag.
- The "superseded / record only" labels on docs 15 and 16 (and any others the pass finds) are reworded
  as "compressed into <doc>; consult for detail", and any rule present only in the compressed doc that
  the pass judges still binding is either restored into the target doc or listed for the operator.
- The craft map exists: every literary/speech device with scale (L0-L6), the gate that enforces it (by
  id, from the gates registry), the doc section, one exemplar - generated where possible, curated where
  not, with a `--check` on the generated part.
- The discoverability delta is measured: the ten benchmark questions (rounds 1-2) re-run on the Opus
  `explorer` with the layers present, same prompts; tool calls and tokens compared in
  `evals/RETRIEVAL-BENCHMARK-2026-09-05.md` round 4.

## Scope

Docs under `docs/content-video-engine/**`, `docs/portable/**`, `docs/runbooks/**`, the animation brief,
the sources bundle; the registries and their tests under `content/video_engine/scripts` and `tests`;
BACKLOG.md, CAPABILITIES.md, GEMINI.md (the `[DERIVED]` line), AGENTS.md (the superseded wording).

## Not Building

- No implementation of any triaged item in this plan (each TOP item becomes its own order).
- No renumbering of existing sections (citations depend on them); no rewording of operator quotes.
- No embeddings / semantic search: the deterministic layers are measured first (T7); embeddings are a
  separate exploration only if the delta is insufficient.
- No changes to the SEO-platform specs.

## Human Gates

- HG1 - the triage priorities (T3): the operator ratifies TOP / BACKLOG / EXPLORE / RETIRE per item; the
  parent recommends, never sets `approved`.
- HG2 - the superseded-doc wording and any rule restored from docs 15/16 into doc 29 (T4).
- HG3 - the `[DERIVED]` convention (T5) - a doctrine change to the proof-line format.
- Push stays the operator's decision (B3).

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md` (dispatch mapping, hand-off policy, lane write sets)
- `docs/content-video-engine/47-FINDINGS-TO-CHECKS.md` (the finding → check ledger, the reclassified rows)
- `docs/content-video-engine/BACKLOG.md` (the 2026-09-05 evening read, R1-R6, X-rows, G-rows)
- `docs/portable/OPERATOR-RULINGS.md` E35-E41 (the recent stumbles, in the operator's words)
- `docs/GATES-REGISTRY.md`, `docs/ANIMATION-REGISTRY.md`, `docs/DOCS-MANIFEST.md`, `docs/DOCS-TOPICS.md`,
  `docs/DOCS-CITATIONS.jsonl` (the mechanical review, once T1 lands)
- `evals/RETRIEVAL-BENCHMARK-2026-09-05.md` (the questions and the before numbers)
- memory notes: caption-energy-lessons, soak-ink-is-a-plate, gate-fit-mangles-prose (the stumbles not yet in a doc)

## Execution Path

1. T1 lands the registries (in flight). 2. T2 `architect_sol` reads the registries' orphaned/tracked/
retired lists against the stumble evidence and drafts the triage with a recommendation per row and the
list of decisions only the operator can make. 3. HG1. 4. T3 writes the ratified rows into BACKLOG/
CAPABILITIES; T4 rewords the superseded labels and restores/lists binding rules (HG2); T5 marks derived
numbers and names the tag in the intake (HG3). 5. T6 the craft map. 6. T7 the benchmark re-run. Parent
owns HG decisions, integration and every diff review; `reviewer` before each commit of doctrine.

## Patterns To Mirror

- `content/video_engine/scripts/build_docs_index.py` / `build_topic_index.py` / `build_docs_manifest.py`:
  stdlib, deterministic, `--write/--check`, generated outputs excluded from the index walk via
  `docs/DOCS-INDEX.config.json`, real-tree smoke tests naming today's findings.
- `evals/RETRIEVAL-BENCHMARK-2026-09-05.md`: held answers, per-run tokens / tools / seconds, labelled for
  what it establishes.
- BACKLOG row shape: `| id | **title** — what and where | why / cost |`; struck rows keep their original text.

## Task Slices

### T1: Registries land (gates, animation and maths, layers wrapper)
- Status: complete
- Owner: implementation_luna / junior_developer (dispatched 2026-09-05), parent verifies and commits
- Depends on: none
- Write set: `content/video_engine/scripts/build_gates_registry.py`, `build_animation_registry.py`, `build_docs_layers.py` + tests; `docs/GATES-REGISTRY.*`, `docs/ANIMATION-REGISTRY.*`, `docs/DOCS-MANIFEST.*` (headings field), `docs/DOCS-STANDARD.md`
- Acceptance: each `--check` green; the four smoke statuses hold; `build_docs_layers.py --check` green on the committed tree
- Validate: `python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: pending

### T2: The triage draft and the operator's decision list
- Status: complete
- Owner: architect_sol (Opus, read-only except the plan evidence file)
- Depends on: T1
- Write set: `docs/content-video-engine/TRIAGE-2026-09-05.md` (draft), this plan's Evidence section
- Acceptance: every `orphaned` and `tracked` registry row plus every rule found only in a "superseded" doc appears once with: what it is, where (path | heading), status evidence, the recent-stumble evidence if any, a recommendation (TOP / BACKLOG / EXPLORE / RETIRE) and the one-line reason; a closing "Decisions only the operator can make" list with the parent's recommendation on each; no item invented, every claim cites a path
- Validate: `rg -c "^\| " docs/content-video-engine/TRIAGE-2026-09-05.md` equals the count of orphaned+tracked rows in `docs/ANIMATION-REGISTRY.jsonl` plus the listed compressed-doc rules; `reviewer` pass: no citation fails a grep
- Evidence: pending

### T3: Backlog and capabilities rows from the ratified triage
- Status: complete
- Owner: junior_developer, parent integrates
- Depends on: T2, HG1
- Write set: `docs/content-video-engine/BACKLOG.md`, `docs/content-video-engine/CAPABILITIES.md` (rows only)
- Acceptance: TOP rows at the head of the next list with their evidence; BACKLOG/EXPLORE rows in their sections; RETIRE rows struck with the reason; `build_docs_layers.py --write` run in the same commit
- Validate: `python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: rows landed 83a472f (reviewer-verified); the two held rows and the D6 row resolved 2026-09-06 by E42 (`OPERATOR-RULINGS.md` E42; BACKLOG "D3 / D6 — ruled"; TRIAGE D3/D6 annotated). O9 and T5 stay BACKLOG; D6 → tag all thirteen, executed by P45 T5.

### T4: Compressed docs - lift the differences out, dedupe, relabel
- Status: complete (deterministic half + the four lifted rules; the remaining 418 delta rule lines are the operator's lift list in docs/DOC-OVERLAP.md)
- Owner: implementation_luna (the overlap report, deterministic), parent + reviewer (the restored deltas)
- Depends on: T1, HG2 (ruled 2026-09-05: "we compressed the docs because we didn't have a proper search system; now that we do we shouldn't kill everything in the compressed docs - lift the differences out and dedupe")
- Write set: `content/video_engine/scripts/report_doc_overlap.py` + test, `docs/DOC-OVERLAP.md` (generated: for each compressed doc → target pair, sections whose labels/terms match a target section = DUPLICATE, sections with no match = DELTA, with `path:line` both sides); then, per ratified delta: the target doc (additive, cited back), the compressed doc's status line ("compressed into <doc>; the deltas below were lifted on <date>"), `AGENTS.md` (the docs 15/16 sentence)
- Acceptance: the overlap report exists for docs 15 → 29, 16 → 29 and every other "superseded / record only" pair the manifest's bylines name; every DELTA row is either lifted into the target (additive-only diff, `git diff --numstat` 0 deletions on the target) or listed for the operator with a reason; DUPLICATE sections are struck in the compressed doc with a pointer, never deleted; no operator quote reworded
- Validate: `python content/video_engine/scripts/report_doc_overlap.py --check; git diff --numstat -- docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md`
- Evidence: pending

### T5: Derived-number provenance
- Status: complete
- Owner: junior_developer, parent for GEMINI.md
- Depends on: T2, HG3
- Write set: the docs carrying derived figures (from the triage), `GEMINI.md` (intake step 3), `content/video_engine/scripts/build_animation_registry.py` (+ test: `provenance: derived` when a `[DERIVED:` tag is within the section)
- Acceptance: 0.22 in doc 47 / the brief carries `[DERIVED: from …, how]`; each tag links the sources it was computed from when they are readily available in the sources bundle / research docs, or says `sources: not on file`; the registry lists every derived figure; the intake names the tag (ruled 2026-09-05)
- Validate: `rg -c "\[DERIVED:" docs/ | tail -1; python -m pytest content/video_engine/tests/test_build_animation_registry.py -q -p no:cacheprovider`
- Evidence: 2026-09-06 (junior_developer; parent reviewed and reworded one tag). 14 `[DERIVED:` tags for the thirteen figures across the brief, docs 45/46/47/48/50 (the 0.22 in the brief and doc 47); one R6 sentence per doc. The triage's brief line numbers were 2 off and several targets sat inside code fences or `$$` math, so tags went on the nearest prose line of the same section - the registry reads provenance over the section. The 0.45 s row IS in doc 46 §46.3 and is tagged there. Detection needed no change (`animation_registry_chain.provenance` already reads the section); a test pins it (`36 passed`). Registry provenance 296/2/50 → 295/12/42 (sourced/derived/unsourced), 348 formula records unchanged after the parent removed a law name from one tag that had minted a phantom record. `GEMINI.md` intake step 3 carries the E42 rule.

### T6: The craft map
- Status: complete
- Owner: implementation_luna (generated part), parent + reviewer (curated part)
- Depends on: T1 (gate ids)
- Write set: `content/video_engine/scripts/build_craft_map.py` + test, `docs/CRAFT-MAP.jsonl`, `docs/CRAFT-MAP.md`, `docs/content-video-engine/patterns/CRAFT-DEVICES.md` (curated seed: device → scale, gate id, doc section, exemplar)
- Acceptance: every device named in FULL-VIDEO-MAP, KNOWLEDGE-GRAPH, the phase guides, STRENGTH-LOOP, SENTENCE-STRENGTH-CHECK and VOICE-PACK has one row; the gate column is filled from `docs/GATES-REGISTRY.jsonl` where a gate exists and says `judge` or `none` otherwise; `--check` green; `reviewer`: no exemplar invented (each quotes a script or doc line by path)
- Validate: `python content/video_engine/scripts/build_craft_map.py --check`
- Evidence: pending

### T7: The discoverability delta
- Status: complete (rounds 4-5)
- Owner: parent (dispatches `explorer`, grades against the held answers)
- Depends on: T1, T6
- Write set: `evals/RETRIEVAL-BENCHMARK-2026-09-05.md` (round 4), the explorer role's retrieval-discipline text (manifest → index → topics order)
- Acceptance: the ten questions re-run with identical prompts on the Opus `explorer`; tokens / tool calls / seconds tabulated against rounds 1-2; the false-negative case passes; labelled for what it establishes (same harness, layers added)
- Validate: `rg -c "Round 4" evals/RETRIEVAL-BENCHMARK-2026-09-05.md`
- Evidence: pending

### T8: Measure the secondary-motion ratio - per motion, per scene, per screen
- Status: complete
- Owner: implementation_luna (the measurement), explorer (the buried research), parent (the read)
- Depends on: T1
- Write set: `content/video_engine/scripts/measure_motion_energy.py` + test, `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short/MOTION-ENERGY.md` (generated), a BACKLOG X11 update
- Acceptance: on the Tokyo short's compiled timeline, `E = ∫|v|² dt` is reported for every motion piece (each kinetic: pops, lifts, the ledger build/retract/spiral, the soak, captions' boil) classified primary vs secondary by the shot table's roles, then aggregated per scene and for the whole screen; the 0.22 reference is printed beside each measured ratio with the difference; the explorer first answers, via the layers, whether the research docs already hold anything on motion cohesion (motions working together vs individually) and cites it or reports not found where it looked (roots named)
- Validate: `python content/video_engine/scripts/measure_motion_energy.py content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short/tokyo-short.timeline.json --report`
- Evidence: pending

## Verification

```
python content/video_engine/scripts/build_docs_layers.py --check
python -m pytest content/video_engine/tests/test_build_gates_registry.py content/video_engine/tests/test_build_animation_registry.py content/video_engine/tests/test_build_craft_map.py content/video_engine/tests/test_build_docs_layers.py -q -p no:cacheprovider
python scripts/prp_validate.py .claude/PRPs/plans/P45-CORPUS-RECONCILIATION.plan.md
```

## Evidence And Handoff

- 2026-09-05: layers shipped before this plan - index (e208bbf, 5aecab0), manifest (eaaf780), topics + citations (98447ba, 91deb0b), audit (fad2f29); lead-line review findings in the session record and `docs/DOCS-STANDARD.md`.
- Rulings, operator 2026-09-05 (HG1 partial, HG2, HG3): (1) restore the motion-authoring order into doc 29 now, gate after one measured episode; (2) the cadence rule is TOP as a kinetics module; (3) yes - measure the 0.22 on every individual motion piece AND per scene AND for total on-screen motion, and look for buried research on motion cohesion (T8); (4) the stick lane is in flight → FK/IK + zero-slip are TOP; (5) multi-plane inpainting → BACKLOG unless it gives capability beyond parallax ("our other local generation stuff kind of failed on us, except for parallax, which isn't much better than Ken Burns"); (6) adopt `[DERIVED]`, link sources when readily available or say they are not on file; (7) compressed docs: lift the differences out and dedupe, never kill (T4 reshaped). (8) M13 as a built gate in the edit pass: TOP (operator, 2026-09-05).
- TOP seeds for T3, from the rulings: the cadence kinetics module (on-1s/2s/3s by translation speed); FK/IK boundary + zero-slip anchoring (G-j) for the stick lane; the motion-authoring order restored into doc 29; the M13 cut-gap gate in the edit pass (>= 0.30 s, cut at 0.8 of the gap, mid-word <= 25 %; the measurement exists in `measure_cut_gaps.py`, the constant in `build_short.py`).
- T2 landed 2026-09-05 (86c46f5): `docs/content-video-engine/TRIAGE-2026-09-05.md` - 54 decisions (5 TOP all pre-ruled, 31 BACKLOG, 6 EXPLORE, 12 RETIRE), four registry misreads corrected (FK/IK and closed-chain 'retired' were graduations; 38 of the 128 research orphans are CITATION orphans - the modules cite our numbered docs, never the research file). Parent rulings on the architect's eight (the operator asked the parent to judge): D2 Deegan rim -> BACKLOG (this week's ink verdict was 'paint it with ink', not another filter term); D4 'a camera move alone is not a visual event' -> restore the prose into 29, change no threshold until one episode is measured both ways; D5 the 2-6 s plate ceiling -> lift into 29 as the first-minute rule M10 already is, no runtime-wide 6 s without a measurement; D7 cadence threshold -> test BOTH 250 and 100 px/s against our stepped clocks, adopt neither on the page; D8 gates-registry scope -> state it in the header now, extend the scan when the comfy/grounding gates next change; D1 the fourteen unowned judge-only devices -> add the block to CHECK-RESPONSIBILITIES §3 (the craft map is generated; a second roster would drift). **Open for the operator: D3** (does the stick lane animate a rig or swap approved poses? recommendation: poses first per E40, rig only what the first shot cannot fake) and **D6** (does `[DERIVED]` also tag our own computed thresholds such as G-c 0.18 and G-o 12 px, not only research-derived figures? recommendation: yes - E38 says our own practice is never the calibration source).
- Registry follow-up queued: propagate `implemented` through the citation chain (module -> our doc section -> the research section it cites) so the 38 citation orphans stop reading as gaps.
- 2026-09-05 late: T1 83a472f/33ec81e/a994f82/4247c65, T2 86c46f5, T3+T4 83a472f (reviewer-verified doctrine lift; CHECK-RESP 3i), T6 4247c65, T7 rounds 4-5 cd59717/bb00b1b (9/9, false negative gone, tool calls -7%, tokens +16% then -18% with docs_find on multi-layer hunts; the ~30k dispatch floor is the always-loaded layer), T8 cc60a52 (translation ratio 0.026, opacity ratio 2.4, s06 121x over, corpus is pairwise only). Registry chain fix: orphaned 107 -> 66. Open: D3 (rig vs poses), D6 (tag our own thresholds), T5.
- Regression check 2026-09-05 (whole `content/video_engine/tests`): 1447 passed, 53 failed, 2 collection errors - all failures in lanes untouched by P45 and pre-dating it (finance whiteboard proofs, production console, audio synth, remotion editorial fixture, history v4 pipeline, test_pipeline; last changed 2026-08-02..08-23; causes: a missing untracked deck slide, `duration_s` unbound in the synth, a 409 from the console, an asset-roster count 19 vs 15). Not P45's write set; reported to the operator as carried debt for those lanes. The ten docs-layer suites: 213/213 after the manifest ceiling fix (2c0227f).
- Decisions surfaced at draft time (8, the last added after the gates registry landed) (the parent's recommendation in brackets):
  1. The motion-authoring order (docs 15 §5 / 16 §3: character or prop action, then camera, then secondary) lives only in the compressed docs and doc 29 does not carry it - restore into doc 29 and encode as a motion-gate check? [restore; gate only after one episode is measured against it]
  2. The on-1s / on-2s / on-3s cadence rule (animation brief) - orphaned, yet `SOAK_STEP` FPS 8 and `LIFE_FPS` 10 are already stepped clocks and the operator asked for "more step-motion / jitter" on 2026-09-05 - TOP as a kinetics module (cadence by translation speed), or EXPLORE? [TOP: it names a stumble we had this week]
  3. The 0.22 secondary-motion budget - test as a starting reference on the Tokyo short's spring velocities (X11 exists) - EXPLORE with a measurement, and the number marked `[DERIVED]`? [yes, both]
  4. FK/IK boundary and zero-slip (G-j, doc 48) - tracked; is the stick lane (E39, doc 53) the next production lane, which would make these TOP? [operator's call on lane order]
  5. Multi-plane inpainting SAM 2 + LaMa (45 §45.5, B6 "load-bearing") - E40 says stills are the asset and clips only by frames; multi-plane cards from stills is that rule's positive form - TOP or BACKLOG? [BACKLOG until a plate needs parallax the current species cannot give]
  6. The `[DERIVED]` tag - adopt in the proof-line format, or fold into `[UNVERIFIED]`? [adopt: derived-from-sources is a different class from unverified]
  7. Docs marked "record only": reword to "compressed into 29" everywhere, and should the citation graph treat a compressed doc's sections as aliases of the target? [reword yes; aliasing only where T2 finds identical rules]
  8. **M13 is not a built gate** (gates registry, 2026-09-05): doc 47 row 202 says "the gate lands with the edit pass"; what exists is the measurement (`measure_cut_gaps.py`) and a per-project constant (`build_short.py` `CUT_AT = 0.8`). The cut thresholds were settled from the reference on 2026-09-04 (E38) - a recent stumble by the rule. Build the gate in the edit pass now (TOP), or leave it as a measurement until the edit pass is itself built? [TOP: the numbers are settled and a project already hard-codes one of them]
