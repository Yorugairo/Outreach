---
id: P18-DURABILITY-AND-PATH-CONTRACT
title: Durability classes, one path contract, and content-addressed backup for the video engine
status: complete
operation: feature
risk: high
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-08-23
updated: 2026-08-24
---

# Durability And Path Contract

## Summary

The engine's directory tree grew one feature at a time: `EXPORT_SUBPATH` in
one module, `QUARANTINE_DIR` in another, `assets/generated/review/` by
convention, `_CONFIG_DIR` duplicated across five services. Meanwhile the
binary policy (commit `808eb14`) untracked all generated imagery — correctly —
which leaves every irreplaceable asset on exactly one disk with no durability
story: the catalogue records sha256 digests of files nothing protects.

This plan establishes one principle and builds three things from it.

**The principle: a file's durability class is readable from its path alone.**
Three classes — `runtime/` (disposable: regenerable previews, quarantine,
derived artifacts), `review/` (in-flight: deliveries and claim output, losable
but annoying), `canonical/` (catalogue-referenced: must survive hardware
death). The embryo already exists: `composite_preview.py` refuses any output
not under a `runtime/` directory. P18 generalises that rule and gives it an
owner.

The three builds: (1) a `paths.py` contract module every service resolves
through, held by a structural test in the style of the P15 motion-arithmetic
test; (2) a migration that moves existing directories into the class layout
with the catalogue rewrite atomic against the file moves; (3) a
content-addressed Cloudflare R2 store, synced **on promote** — the moment an
asset becomes canonical is the moment it becomes irreplaceable, so that is the
moment it uploads. The catalogue's existing sha256 field becomes the store
key, making backup a checkable invariant: every digest the catalogue names
exists in the store.

**Scope: video engine only** (operator decision 2026-08-23). The principle is
written to port to other products later; no cross-repo machinery is built now.

**Sequencing: P18 gates P17's build slices (T3+).** P17 is about to hardcode a
claims registry, delivery dirs, watchdog watch-paths, and a motion library
location; landing structure afterwards would make P17 the newest layer of
sprawl. The P17 probe (two-image work order) has no structural dependency and
may run at any time.

## Intent And Acceptance

Accepted when:

1. `content/video_engine/src/services/paths.py` is the single owner of class
   roots and resolution: `runtime_dir()`, `review_dir()`, `canonical_dir()`,
   `class_of(path)` returning the durability class or refusing paths outside
   the contract. Project-scoped: every resolver takes the project root the
   console already resolves via `VIDEO_ENGINE_PROJECT_ROOT`.
2. A structural test fails when any service or console module builds a
   class-root path by hand instead of through `paths.py` — enforced, not
   documented. `composite_preview`'s local "runtime" check is replaced by the
   central rule; `QUARANTINE_DIR` and `EXPORT_SUBPATH` resolve through the
   contract.
3. Existing directories are migrated into the class layout by an idempotent
   script; the catalogue path rewrite commits atomically with the moves
   (write-new, verify digests, swap, never a window where the catalogue names
   paths that do not exist); a dry-run mode prints the full move plan first.
4. `.gitignore`'s per-feature patterns collapse to class-prefix rules; git
   status is clean before and after migration.
5. Promotion syncs the promoted asset to R2, keyed by its sha256, before the
   catalogue write completes; sync failure fails the promotion loudly rather
   than leaving an unprotected canonical asset. Store credentials come from
   environment variables only; a missing configuration degrades to an explicit
   "unsynced promote" warning mode only when the operator has set an explicit
   opt-out flag — silence is never the failure mode.
6. An audit command walks the catalogue and verifies every named sha256 exists
   in the store; a restore command fetches by digest and rebuilds the
   canonical tree from a bare catalogue. Both are read-only against the
   catalogue.
7. Full test suite green apart from the five known `test_history_v4_pipeline`
   failures.

## Scope

- The `paths.py` contract module and its structural enforcement.
- Retrofit of the modules that hand-built class paths.
- Layout migration with atomic catalogue rewrite; `.gitignore` collapse.
- Content-addressed R2 store, sync-on-promote, audit and restore CLI.
- The durability doc and its indexing.

## Patterns To Mirror

- **Structural enforcement** — the P15 motion-arithmetic test: a grep-shaped
  test that names offenders beats a convention.
- **Fail-closed with a named fix** — `hyperframes_render`'s gate errors: the
  message states the env vars or flag that unblock, never a bare refusal.
- **Single monkeypatchable boundary** — `preview.py::_run_command`; here the
  store's `_build_client` and the `StoreClient` protocol.
- **Copy-verify-swap** — `artifact_io.write_artifact`'s temp-then-replace,
  extended across files plus catalogue in the migration.

## Not Building

- No cross-repo or cross-product structure (bjjregistry, tradesinsights port
  the principle later, not the code).
- No Google Drive integration — R2 is the durability mechanism; Drive
  mirroring for human browsing is parked.
- No scheduled/background sync daemon: sync-on-promote plus on-demand audit is
  the whole mechanism. Nothing to forget, no drift window.
- No git-lfs, no re-tracking of binaries in git.
- No changes to review-state semantics or the promotion gate itself — only a
  sync step inside the existing promote path.
- No worktree/branch strategy changes.

## Human Gates

| Gate | Who | Rule |
| --- | --- | --- |
| R2 bucket + credentials | Operator | Provisioned by the operator; the plan supplies the required env var names and bucket layout, never creates accounts |
| Migration execution | Operator | Dry-run plan reviewed and approved before any file moves |
| Unsynced-promote opt-out | Operator | Explicit config flag; default is fail-closed |

## Mandatory Reads

- `backend-patterns` — service boundaries; configuration at the edge
- `content/video_engine/src/services/composite_preview.py` — the local "runtime" check being generalised (`_fit_to_frame` module, output guard near line 330)
- `content/video_engine/src/services/hyperframes_render.py` — `QUARANTINE_DIR` and the quarantine non-promotion tests that must keep passing verbatim
- `content/video_engine/console/routes/generate.py` — `EXPORT_SUBPATH`
- `content/video_engine/console/settings.py` — project-root resolution the contract extends
- `content/video_engine/src/services/asset_catalog.py` + `delivery_intake.py` — catalogue path/sha256 binding the migration must hold atomic
- `content/video_engine/tests/test_hyperframes_preview_gate.py` — quarantine-laundering tests as the model for class-boundary tests
- `.claude/PRPs/plans/P17-AGENT-GENERATION-LOOP.plan.md` — the consumer this plan gates

## Execution Path

Order: T1 → T2 → T3 → (T4, T5 parallel) → T6. T4 and T5 have disjoint write
sets. Nothing in T4+ runs until the operator has approved the T3 dry-run.

```
content/video_engine/src/services/
  paths.py                the contract: class roots, resolution, class_of
  asset_store.py          R2 content-addressed store: put/head/get by sha256
scripts/
  migrate_layout.py       idempotent migration with dry-run
content/video_engine/cli.py
  store-audit / store-restore subcommands
```

## Task Slices

### T1: The path contract
- Status: complete
- Depends on: none
- Evidence: 16 tests green (`test_paths.py`); module docstring is the layout of record
- Owner: parent
- Write set: `content/video_engine/src/services/paths.py`, `content/video_engine/tests/test_paths.py`
- Acceptance: three class roots per project root; resolvers return absolute paths inside the project; `class_of` classifies any project-relative path or refuses; escape attempts (.., absolute injections) are named errors; the module holds no I/O beyond mkdir-on-request; class names and layout are documented in the module docstring as the single source of truth.
- Validate: `python -m pytest content/video_engine/tests/test_paths.py -q`

### T2: Enforcement and retrofit
- Status: complete
- Evidence: structural sweep caught 4 real hand-built paths before the retrofit (intake, runs, plus two false positives now regex-excluded/allowlisted); quarantine, preview and generate tests pass unmodified
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/tests/test_path_contract_structural.py`, `content/video_engine/src/services/composite_preview.py`, `content/video_engine/src/services/hyperframes_render.py`, `content/video_engine/console/routes/generate.py`, `content/video_engine/src/services/asset_catalog.py` (shared `_CONFIG_DIR` extraction)
- Acceptance: a structural test sweeps `src/services` and `console` for hand-built class-root paths (string literals joining into `runtime`, `review`, `canonical`, quarantine subpaths) outside `paths.py` and fails naming the offender; `composite_preview`'s local check delegates to the contract with its error message preserved; `QUARANTINE_DIR`/`EXPORT_SUBPATH` become contract-resolved with their public names kept; every existing test that asserts quarantine or runtime behaviour passes unmodified — the retrofit changes resolution, never semantics.
- Validate: `python -m pytest content/video_engine/tests/ -q`

### T3: Migration with atomic catalogue rewrite
- Status: complete (execution operator-gated)
- Evidence: 6 tests green incl. tamper, resume and deep-path cases; real-tree dry-run saved to `.claude/PRPs/evidence/P18-T3-dryrun-systems-and-blowups.txt` (143 operations) awaiting operator approval; .gitignore collapsed to class prefixes with legacy patterns retained until migration executes
- Owner: parent
- Depends on: T2
- Write set: `scripts/migrate_layout.py`, `content/video_engine/tests/test_migrate_layout.py`, `.gitignore`
- Acceptance: dry-run prints every planned move and the catalogue diff, then exits; execution copies files to the class layout, re-verifies each sha256 against bytes at the destination, writes the rewritten catalogue to a temp file, swaps both into place, and only then removes originals — at no point does the live catalogue name a missing path; idempotent (re-run is a no-op); interrupted runs resume safely; `.gitignore` per-feature binary patterns collapse to class prefixes with the p29-restored rules untouched; long-path safety verified on Windows (the `core.longpaths` lesson).
- Validate: `python -m pytest content/video_engine/tests/test_migrate_layout.py -q`, then operator-approved dry-run and execution against the real tree.

### T4: Content-addressed store and sync-on-promote
- Status: complete (bucket provisioning operator-gated)
- Evidence: 9 tests green over a fake client; commit route fails closed without a store; opt-out marks entries `unsynced: true` and the marker survives `register_assets`; boto3 imported lazily at the single client boundary
- Owner: parent
- Depends on: T3
- Write set: `content/video_engine/src/services/asset_store.py`, promotion path in `content/video_engine/console/routes/intake.py` (or the promotion service it calls), `content/video_engine/tests/test_asset_store.py`
- Acceptance: store keys are `sha256/<digest>` in an operator-provisioned R2 bucket (S3-compatible client; endpoint, bucket, key id, secret from env only — never logged, never in config files); `put` is idempotent (head-then-skip on existing digest); promotion uploads before the catalogue write completes and fails the promotion on sync failure unless the explicit opt-out flag is set, in which case the promote is recorded with an `unsynced: true` marker the audit surfaces; tests run against a fake S3 boundary, never the network.
- Validate: `python -m pytest content/video_engine/tests/test_asset_store.py -q`

### T5: Audit and restore
- Status: complete
- Evidence: 7 tests green; `store-audit` exits 1 on missing digests and reports unsynced debt separately; `store-restore` refuses overwrite without --force and verifies every fetched byte
- Owner: junior_developer
- Depends on: T4 (interface only; may build against the fake boundary in parallel once T4's interface is committed)
- Write set: `content/video_engine/cli.py` (store-audit, store-restore subcommands), `content/video_engine/tests/test_store_audit.py`
- Acceptance: `store-audit` walks the catalogue, heads every sha256, and reports missing/unsynced/ok counts with per-asset detail on failure — read-only everywhere; `store-restore` fetches named digests (or all) into the canonical layout and verifies bytes against the catalogue digest before placing; a restore over existing files refuses unless `--force`; both work from a bare catalogue plus credentials and nothing else — that pair is the disaster-recovery contract.
- Validate: `python -m pytest content/video_engine/tests/test_store_audit.py -q`

### T6: Docs
- Status: complete
- Evidence: `docs/content-video-engine/27-DURABILITY-AND-LAYOUT.md` written; indexed in the docs README and `content/video_engine/AGENTS.md`; P17 path dependencies mapped onto the classes
- Owner: junior_developer
- Depends on: T5
- Write set: `docs/content-video-engine/27-DURABILITY-AND-LAYOUT.md`, `AGENTS.md` (layout row)
- Acceptance: the class principle stated with its one-line test ("class readable from path alone"); the tree documented; the promote-sync invariant and the audit/restore disaster contract documented; the porting note for other products (principle, not code); P17's path dependencies (claims, deliveries, motion library, watchdog) mapped onto the classes so P17 implements against this doc.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P18-DURABILITY-AND-PATH-CONTRACT.plan.md`

## Verification

```bash
python -m pytest content/video_engine/tests/ -q
python scripts/prp_validate.py .claude/PRPs/plans/P18-DURABILITY-AND-PATH-CONTRACT.plan.md
```

- Full suite green apart from the five pre-existing `test_history_v4_pipeline.py` failures.
- Manual: operator-reviewed dry-run before migration; one real promote observed to land its digest in R2; `store-audit` reports zero missing; a spot `store-restore` of one asset byte-matches the original.

## Risks

| Risk | Level | Mitigation |
| --- | --- | --- |
| Migration breaks catalogue path/sha256 bindings | High | Copy-verify-swap-remove ordering; dry-run gate; digest re-verification at destination; idempotent resume |
| Promote latency grows by an upload round-trip | Medium | Idempotent head-then-put; assets are single-digit MB; failure is loud, not slow-and-silent |
| Credentials leak into logs or config | Medium | Env-only, never logged; structural test greps for the env var names in tracked files |
| Retrofit silently changes quarantine semantics | Medium | Existing quarantine/runtime tests must pass unmodified — acceptance, not hope |
| Class names bikeshed into churn | Low | Names fixed in T1's docstring as the single source; changing them is a migration, priced accordingly |
| Windows long paths break moves | Low | Explicitly tested in T3; `core.longpaths` already enabled |

## Evidence And Handoff

All six slices implemented and validated: 728 tests pass (5 pre-existing
`test_history_v4_pipeline` failures unrelated, `task_5672544a`).

Two operator gates remain open, by design — the code is complete and waiting
on decisions only the operator can make:

1. **Migration execution** — review
   `.claude/PRPs/evidence/P18-T3-dryrun-systems-and-blowups.txt` (143
   operations against the systems-and-blowups tree in the p29 worktree), then
   `python scripts/migrate_layout.py <root> --execute`.
2. **R2 provisioning** — create the bucket and set the four
   `VIDEO_ENGINE_R2_*` variables (doc 27 lists them). Until then, commits use
   the explicit `VIDEO_ENGINE_ALLOW_UNSYNCED_PROMOTE=1` opt-out and carry
   auditable `unsynced` markers; `store-audit` names the debt.
