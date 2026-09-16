---
id: P63-THE-LAYERS-ARE-BUILD-OUTPUT
title: The layers are build output - the docs retrieval layers leave git and the commit path, rebuild lazily by input digest on the reader's side, and the animation registry stops costing a minute; the docs half of the dual bottleneck removed, the engine half left to P62
status: running
operation: refactor
risk: standard
owner: parent
branch: main
created: 2026-09-16
updated: 2026-09-16
---

# The layers are build output

> **APPROVED 2026-09-16** - the operator: *"plan approved you can /prp-implement after T7c's commit"*. HG1 granted (the layers leave git); runs after P61 T7c's commit lands.

## Summary

The operator, 2026-09-16, on the P61 lanes waiting on each other: *"the way we handle the layer rebuild makes for a
really slow and inefficient process when we have multiple agents working. we need a better process"* and *"anything we
do makes it stale underneath, so everybody has to wait on BOTH the engine lock AND the doc layer to stabilize. we have
created a dual bottleneck production system."*

Measured on the main checkout the same morning (`build_docs_layers.py --check`, one layer at a time):

| measure | value |
| --- | --- |
| the whole `--check`, which `~/.claude/hooks/context_guard.py` runs on EVERY `git commit` | 91 s |
| of which `build_animation_registry.py --check` / `build_gates_registry.py --check` | 68 s / 15 s |
| commits of the last 60 that rewrote generated layers | 60 of 60 |
| generated layer bytes tracked in git (`docs/DOCS-*.jsonl` + twins, the registries, the catalogue) | 15 MB |
| layers stale from ONE lane's uncommitted engine edits (T7c, `species/verdict.mjs`) | 6 of 11 |

The design flaw: twelve derived artifacts are treated as source - committed, byte-checked against their inputs, and
gated at commit time. Staleness is therefore a property of the shared checkout, not of anyone's change: a species edit
by the engine lane makes the audio lane's commit fail; whoever rebuilds to unblock captures the other lane's half-done
state; the next edit makes it stale again (the ping-pong of 2026-09-16, `docs/LANE-REGISTER.md` "layers build"
column). The animation registry's minute is a hot loop, not a big input: `code_lines_only` re-classifies the same
eighteen module files once per exported KEY (3294 calls, 124 s cumulative of a 219 s profiled run; `in_spans` 8.3 M
calls; `str.startswith` 378 M calls) - the session scratchpad's `anim_profile.txt`.

The fix is structural, not a faster lock: **the layers become build output.** Gitignored, rebuilt on the reader's side
only when the digest of that layer's inputs changed, never checked at commit. The lane register's "layers build" column
retires. The engine lock is a different animal - one synced engine, goldens byte-identical against it - and stays
serialized until P62 puts each engine lane in its own worktree; this plan does not touch it.

## Intent And Acceptance

- A `git commit` by any lane pays nothing for the docs layers: the hook's layers gate is gone, and no generated layer
  is tracked, so no commit can be blocked or conflicted by one.
- `docs_find.py "<term>"` on a checkout where a docs file, a kinetics module or a test changed since the last build
  answers from CURRENT layers without the agent running a build: the layers it scans are ensured by input digest
  before the scan, and only the layers whose inputs changed are rebuilt.
- Every runtime reader of a layer (the one-shot floor gate, the player server's catalogue route, `authoring.effects`,
  the effects gallery, the provenance audit) ensures its layer the same way, so a fresh worktree works on first use.
- `build_animation_registry.py --check` on this corpus under 5 s, byte-identical output to today's.
- `build_docs_layers.py --check` reports by digest in under 2 s when nothing changed; `--write` still rebuilds
  everything in dependency order for the record slices that want a full pass.
- The record: `docs/LANE-REGISTER.md` rules, `docs/runbooks/PRP_EXECUTION.md`, the `retrieval-layers` skill, `CLAUDE.md`
  fast route, `GEMINI.md` Tier 4, CAPABILITIES + BACKLOG rows.

## Scope

- `content/video_engine/scripts/docs_layers.py` (NEW library): the layer table with each layer's INPUT globs and OUTPUT
  paths; `digest(layer)`; `ensure(layer | "all", repo) -> list[Path]` (rebuild iff the stored digest differs, in the
  table's dependency order, upstream first); the cache under `docs/.layers/<name>.digest` (gitignored).
- `build_docs_layers.py`: `--check` compares digests; `--write` unchanged; `--ensure [--only <name>]` added;
  `LAYERS` moves to the library.
- `docs_find.py` + the readers named above: `ensure()` before the read.
- `build_animation_registry.py`: the per-file precompute (code-line masks, template sites, test files once per corpus).
- `.gitignore` + `git rm --cached` of the tracked layer files; the docs that describe the layers.
- `~/.claude/hooks/context_guard.py` (the operator's user-level hook, outside the repo): the layers gate removed -
  parent, on the operator's word, since it is their private config.

## Not Building

- The engine lock. It is real (one synced `scene-evidence-engine.mjs`, goldens byte-identical against it) and P62's.
- A committed snapshot of the layers "for the remote". Nothing reads them from origin: the Gemini lane and every role
  run `docs_find.py` in the main checkout (`GEMINI.md:84`, the eight role files). If a snapshot is ever wanted it is a
  separate decision, never `git add -f` (E99 s31's rule for images applies to generated text).
- The alternative considered and rejected: keep the layers tracked, drop only the commit gate, and let the steward
  commit a rebuild once per plan. It halves the churn but keeps 15 MB of generated text in every merge, and under P62's
  per-lane worktrees every merge would conflict on it. Build output does not belong in the tree.
- A daemon / file watcher. The digest at read time is enough and has no process to die.
- A faster gates registry (15 s). Bounded, but not on the critical path once the check leaves the commit; a backlog row.

## Human Gates

- **HG1 - the approval of this plan** is the operator's word that the layers leave git. Decision recorded here: build
  output, gitignored (recommended; the rejected alternative above).
- **HG2 - the hook edit** (`~/.claude/hooks/context_guard.py`): outside the repo, the operator's config; the parent
  edits it only after HG1 and shows the diff.
- No card on the review queue: nothing here is visual. The proof is the commit path and the timings.

## Mandatory Reads

- `content/video_engine/scripts/build_docs_layers.py` (the table, the order, the subprocess shape), `docs_find.py`
  (`LAYERS` spec at :171-221, `render` at :466), `build_animation_registry.py` (`Corpus` :182-194, `code_status` :606,
  `code_lines_only` :619, `key_uses` :644, `template_sites` :473, `test_files` :486).
- `content/video_engine/tests/test_build_docs_layers.py`, `test_docs_find.py` (the `tree` fixture hand-writes layer
  records into `tmp_path` - the ensure path must never rebuild a fixture tree from the real repo),
  `test_build_animation_registry.py`.
- `docs/LANE-REGISTER.md` (the rules while a lane is live), `docs/runbooks/PRP_EXECUTION.md:133-138` (the guard as
  documented), `.claude/skills/retrieval-layers/SKILL.md`, `CLAUDE.md` "Do we have X" fast route, `GEMINI.md:84`.
- `~/.claude/hooks/context_guard.py` (`index_stale` :38-48, the deny at :70-72).
- `docs/portable/OPERATOR-RULINGS.md` E99 s23 / s47 (parallel work is the requirement; awareness pays for it).

## Execution Path

Runs AFTER P61 T7c's commit lands and BEFORE P61 T14 takes the engine lock (T14 is the next lane that would pay the
91 s on every commit). No engine file in any write set, so it may run beside an engine lane. Order: T1 -> T2 -> T4;
T3 beside T1/T2 (disjoint files); T4 is the switch, one steward commit; T5 the record.

Until T4 lands the standing rule holds: one `build_docs_layers.py --write` at a time, claimed in the register.

## Patterns To Mirror

- The effects gallery is already build output, gitignored (`.gitignore:184`, P55 T9): the precedent.
- The clip sidecar of `review_queue_proofs.py` (`clip_key` + `source_sha256`; `clip_is_current` re-renders on a
  changed source): the same "digest of the inputs beside the artifact" shape.
- `sync_kinetics.py --write/--check`: a generated artifact whose check is a byte comparison, not a re-render.

## Task Slices

### T1: THE LIBRARY - one table of layers with inputs, outputs, digest and ensure
- Status: complete (2026-09-16, af0d363)
- Owner: `implementation_luna`
- Depends on: none
- Write set: `content/video_engine/scripts/docs_layers.py` (NEW), `content/video_engine/scripts/build_docs_layers.py`,
  `content/video_engine/tests/test_build_docs_layers.py`, `content/video_engine/tests/test_docs_layers.py` (NEW),
  `.gitignore` (the `docs/.layers/` cache line ONLY - the layer files themselves are T4's)
- Acceptance: `LAYERS` lives in `docs_layers.py` as `Layer(name, script, inputs, outputs, depends_on, write_args,
  check_args, repo_flag)`; the inputs are the globs each builder actually reads (from the builders' own roots:
  `build_docs_index` the docs `**/*.md`; `build_effects_catalog` `effects/cards/*.json` + `effects/recipes/*.json` +
  the scripts it cites; `build_animation_registry` `scripts/kinetics/*.mjs` + `species/*.mjs` + the engine + `tests/**`
  + `gate_*.py`; and so on - each named in the file beside the builder line it came from) PLUS the upstream layers'
  outputs (the manifest reads the index). `digest(layer, repo)` = sha256 over (sorted relative path, size, content sha)
  of every input and of the builder script itself. `ensure(names, repo)` walks the table in order, rebuilds a layer
  when `docs/.layers/<name>.digest` is absent or differs, writes the digest after a clean build, returns what it
  rebuilt; a builder failure raises with the builder's last line. `build_docs_layers.py --check` = every digest
  current (exit 1 naming the first stale, under 2 s when current); `--ensure [--only name]`; `--write` unchanged and
  it stamps digests. Standard library only; deterministic; LF.
- Validate: `python -m pytest content/video_engine/tests/test_build_docs_layers.py content/video_engine/tests/test_docs_layers.py -q`;
  then `python content/video_engine/scripts/build_docs_layers.py --write` (stamps), then `--check` timed (under 2 s);
  then touch one docs file and `--check` names exactly the layers downstream of it
- Evidence: report `scratchpad/assembly/P63-T1.md`. `docs_layers.py` (508 lines): `Input(pattern, content, exclude)`, `Layer(...)`, the twelve-row
  `LAYERS` with a builder-line citation beside every tuple, `digest` over (path, size, content sha) + the builder script, LISTING inputs
  (`docs/research/runs/**`, the assets tree - the ledger dates a run by mtime and never reads it) keyed (path, size, mtime_ns),
  `docs/.layers/<name>.digest` (gitignored), `ordered`/`selection` topological, `ensure`/`stamp`/`stale`, `LayerError`; a no-op on a tree
  without `build_docs_index.py`. Two corrections to this plan's own input list: the animation registry does NOT read `species/*.mjs`
  (the effects catalogue does - `dial_values` opens each card's module); the docs index indexes `docs/CAPABILITIES-INDEX.md`, so
  docs-index depends on capabilities-index. Measured: `--check` 1.04 / 0.99 s when current (was 91 s); one touched docs file -> `--check`
  names docs-index in 0.55 s, `--ensure` rebuilds exactly the nine downstream layers in 27 s, `--check` clean; the digest itself 0.77 s.
  Tests 53 passed (one old test retired with a receipt: `--check` no longer runs any tool). The parent's own use the same afternoon:
  `--ensure` rebuilt seven layers in 18 s before the T7d commit, and the commit hook's check ran in about a second.

### T2: THE READERS ENSURE - docs_find and the runtime readers rebuild what they read, by digest
- Status: complete (2026-09-16)
- Owner: `implementation_luna`
- Depends on: T1
- Write set: `content/video_engine/scripts/docs_find.py`, `content/video_engine/scripts/authoring/effects.py`,
  `content/video_engine/scripts/gate_one_shot_floor.py`, `content/video_engine/scripts/serve_player.py`,
  `content/video_engine/scripts/build_effects_gallery.py`, `content/video_engine/scripts/audit_research_provenance.py`,
  `content/video_engine/scripts/effects_card.py`, their tests (`test_docs_find.py`, `test_authoring_effects.py`,
  `test_gate_one_shot_floor.py`, `test_build_effects_gallery.py`)
- Acceptance: `docs_find.py` calls `ensure()` for the layers it is about to scan (all by default; `--layer X` only X
  and its upstream; `--no-ensure` for a fixture tree and the tests), prints one line `[layers] rebuilt: a, b` to
  stderr when it rebuilt anything (hits stay one per line on stdout), and the "not built" line becomes unreachable on
  a real checkout. `authoring.effects.load_catalog` ensures `effects-catalog`; the one-shot floor gate, the gallery
  builder, the provenance audit and the player server's catalogue route ensure theirs at read time (the server on
  each GET of the route - the digest is cheap). A fixture tree (`tmp_path` with hand-written layer records) is never
  rebuilt: `ensure` is a no-op when the repo has no `content/video_engine/scripts/build_docs_index.py`, and every
  test tree is such.
- Validate: `python -m pytest content/video_engine/tests/test_docs_find.py content/video_engine/tests/test_authoring_effects.py content/video_engine/tests/test_gate_one_shot_floor.py content/video_engine/tests/test_build_effects_gallery.py -q`;
  then edit a kinetics comment, run `docs_find.py "<a dial in that file>"`: the answer is current, `[layers] rebuilt:
  animation-registry` on stderr, no manual build
- Evidence: report `scratchpad/assembly/P63-T2.md`. `docs_find.py` ensures the layers it scans (all; `--layer X` = `selection(X)`; `--capabilities`
  only capabilities-index; `--no-ensure`), the builder of each layer DERIVED from `docs_layers.LAYERS` by artifact so a renamed artifact
  fails loudly; one stderr line `[layers] rebuilt: ...`, stdout untouched. `authoring.effects` ensures the catalogue ONCE per process per
  repo (a digest per `load()` took its test module 1.2 s -> 10.3 s; the memo keeps 1.2 s); the one-shot floor gate and the gallery ensure
  only when the catalogue path resolves to this repo's own; `serve_player` on each GET of the catalogue route; the provenance audit
  before its sync check; `effects_card` needs nothing (it reads only through `authoring.effects`). Every reader catches `LayerError`,
  names it on stderr and reads the artifact as it sits (the six-line helper repeats in five files - a fold into `docs_layers.py`, a
  backlog row). LIVE PROOF: a blank line on BACKLOG.md, `docs_find.py "verdict stack"` current with `[layers] rebuilt: docs-index,
  effects-catalog, docs-manifest, topic-index, gates-registry, animation-registry, craft-map` on stderr, no manual build, the file
  restored byte-identical. Costs on a current tree: docs_find 0.12 -> 0.73 s (`--layer index` 0.48; `--no-ensure` 0.12); the catalogue
  GET 1 ms -> 418 ms median of 7 (a per-server TTL is a three-line change if the editor's open feels it - backlog). Tests 31->37,
  23->28, 35->38, 11->14; 155 passed. The two failures it found and left were T7c's (the verdict card has SIX phases since the gather
  and three tests pinned five) - the parent moved them to six with receipts in the same commit.

### T3: THE MINUTE - the animation registry classifies each file once
- Status: complete (2026-09-16, e3defc1)
- Owner: `junior_developer`
- Depends on: none (may run beside T1/T2; disjoint files)
- Write set: `content/video_engine/scripts/build_animation_registry.py`,
  `content/video_engine/tests/test_build_animation_registry.py`
- Acceptance: `Corpus` precomputes, once per file, the per-line code mask (`code_lines_only`), `header_lines`, the
  split lines, and the template's sites/spans; `key_uses`, `module_uses`, `template_sites`, `test_files`, `in_spans`
  read the precomputed tables and allocate nothing per key. Output byte-identical: `--check` against the committed
  `docs/ANIMATION-REGISTRY.jsonl` + `.md` passes BEFORE T4 removes them from git (and after T4 against a `--write`
  from HEAD~ saved to the scratchpad). `--check` under 5 s on this corpus (was 68 s). A test pins the byte identity on
  the fixture corpus and a timing ceiling on it.
- Validate: `python content/video_engine/scripts/build_animation_registry.py --check` timed;
  `python -m pytest content/video_engine/tests/test_build_animation_registry.py -q`
- Evidence: report `scratchpad/assembly/P63-T3.md`. A `FileScan` per module / template / test on the `Corpus` (lines, lower lines, header,
  code mask, inlined spans as a frozenset, name -> lines and kin-flag -> lines tables); `key_uses`, `module_uses`, `template_sites`,
  `test_files`, `token_hits` read the tables and allocate nothing per key; `in_spans` answers from an lru-cached frozenset; `--check`
  builds the corpus once (it built it twice). The equivalence hinge `word_tokens(text)` = every maximal [\w$]+ run not preceded by a dot,
  exactly what `word_re(name)` can find; tables are candidate filters, every candidate still faces the original predicate. PROOF A/B/A in
  one process while two lanes moved the tree: HEAD 64.23 s, patched 2.37 s, HEAD 66.15 s, all three renders sha256-identical (jsonl
  616b2cbf..., md 01cc6025...). `--check` 126.75 s -> 3.36 s (under the 5 s ceiling, including the ndiff on a stale tree). Tests 36 -> 39
  (a sha256 pin of the fixture render taken before the edit; the tables vs direct scans; a 2 s ceiling), none deleted; the module's own
  test file 60 s -> 3.7 s. Parent's run: 39 passed in 3.74 s. Named: the script is 932 lines against the 800-line cap its docstring cites
  - the FileScan / word_tokens split is a backlog row (T5).

### T4: THE SWITCH - the layers leave git; the docs say so
- Status: complete (2026-09-16) - commits d7448ca (the docs, the test, .gitignore) + 26db00c (the 24 index entries; a pathspec commit records working-tree
  content and dropped the staged deletions - memory `pathspec-commit-never-records-deletions`); T2 is 70c47d4
- Owner: parent (the `git rm --cached` is a tree change every lane sees; the steward commits)
- Depends on: T1, T2, T3
- Write set: `.gitignore` (the twelve layers' `.jsonl` + `.md` twins + `docs/DOCS-STANDARD.md`), the index entries via
  `git rm --cached` (the files stay on disk), `docs/LANE-REGISTER.md` (the "layers build" column and rule retired),
  `docs/runbooks/PRP_EXECUTION.md:133-138` (the guard's layers clause), `.claude/skills/retrieval-layers/SKILL.md`,
  `CLAUDE.md` (the fast route's "Regenerate all" line becomes "the layers rebuild themselves on read;
  `build_docs_layers.py --write` for a full pass"), `GEMINI.md:84`, `content/video_engine/tests/test_docs_layers.py`
  (a test that every layer output is ignored and none is tracked), `~/.claude/hooks/context_guard.py` (HG2: the
  `index_stale` gate removed; the Read / cat guards stay)
- Acceptance: `git ls-files docs/` lists none of the twelve layers' files; the files are on disk and current; a
  `git commit` of a docs edit completes with no layers check (timed: the hook's cost gone); a fresh
  `git worktree add` + `docs_find.py "<term>"` builds and answers. ONE steward commit, pathspec-limited to this
  write set; the message names the removed index entries.
- Validate: `git ls-files docs/ | grep -E "DOCS-(INDEX|MANIFEST|TOPICS|CITATIONS)|GATES-REGISTRY|ANIMATION-REGISTRY|CRAFT-MAP|EFFECTS-CATALOG|CAPABILITIES-INDEX|ASSETS-INDEX|RESEARCH-LEDGER|DOC-OVERLAP|DOCS-STANDARD"`
  prints nothing; `python -m pytest content/video_engine/tests/test_docs_layers.py -q`; the timed commit;
  `python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: `scratchpad/assembly/p63_t4_switch.py`. `.gitignore` lists the 24 outputs under a dated comment (`docs/DOCS-INDEX.config.json` is an
  INPUT and stays tracked); `git rm --cached` of the 24 (all still on disk, verified); CLAUDE.md's fast route, GEMINI.md Tier 4,
  PRP_EXECUTION.md's guard clause, LANE-REGISTER.md's rule (the "layers build" column retired), the retrieval-layers skill and
  RECALL-RECEIPT.md say build output; `test_every_layer_output_is_build_output_ignored_and_untracked` (git check-ignore on every
  output, git ls-files empty, the config still tracked). HG2: `~/.claude/hooks/context_guard.py` loses the docstring line, `index_stale`
  and the `git commit` branch (91 -> 72 lines; the Read / cat guards stay); pipe-tested: a `git commit` payload now exits 0; the
  before-copy at `scratchpad/assembly/context_guard.before.py`, the diff shown to the operator in the report. `build_docs_layers.py
  --check` 0.70 s wall on the switched tree. One test the parent left failing on purpose while T14 runs:
  `test_the_committed_tree_passes_check` runs the real ensure over the live checkout and met T14's in-flight `effects/cards/idle.json`
  (`dials.note` is not in the card schema) - another lane's half-done state seen by a TEST now, never by a commit; it passes once T14's
  card validates.

### T5: THE RECORD
- Status: pending
- Owner: parent
- Depends on: T4
- Write set: `docs/content-video-engine/CAPABILITIES.md` (the retrieval-layers row: "build output, ensured by digest on
  read"), `docs/content-video-engine/BACKLOG.md` (this plan's row with the measurements; a row for the 15 s gates
  registry), `docs/portable/OPERATOR-RULINGS.md` ONLY if the operator's words above are not yet a ruling (the number is
  read from disk at run time), `evals/LAYERS-TIMING-2026-09-16.md` (the per-layer timings and the profile), this plan
  to complete
- Acceptance: every row cites the numbers in the Summary; `build_docs_layers.py --write` once (a full pass, the last
  one anyone has to claim in the register) and `--check` clean;
  `npm run prp:validate -- .claude/PRPs/plans/P63-THE-LAYERS-ARE-BUILD-OUTPUT.plan.md`
- Validate: as above
- Evidence: pending

## Verification

- `python -m pytest content/video_engine/tests -q -k "docs_layers or docs_find or animation_registry or authoring_effects or one_shot_floor or effects_gallery"` green.
- `python content/video_engine/scripts/build_docs_layers.py --check` under 2 s when current; names the right layers
  after a touched input.
- `python content/video_engine/scripts/build_animation_registry.py --check` under 5 s, byte-identical.
- A `git commit` in the main checkout with a stale layer on disk succeeds (the gate is gone) and the layer is rebuilt
  on the next `docs_find`.
- No engine file, golden, or shot table in any diff: `git diff --stat <base>..HEAD -- content/video_engine/scripts/kinetics content/video_engine/scripts/species content/video_engine/tests/golden` empty.

## Evidence And Handoff

Timings recorded per slice in this file; the profile and the per-layer timings from the session scratchpad are copied
into `evals/LAYERS-TIMING-2026-09-16.md` by T5. Handoff: P62 (per-lane worktrees) inherits a checkout where a worktree
has no tracked generated text to merge, which is the precondition it needed.
