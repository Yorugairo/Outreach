---
id: P13-CONTENT-VIDEO-FLYWHEEL
title: Content-to-Video Flywheel Engine — Phase 0 thin slice + pilot
status: draft
operation: feature
risk: standard
branch: claude/content-generation-system-52f077
created: 2026-07-28
updated: 2026-07-28
---

# Content-to-Video Flywheel Engine — Phase 0 Thin Slice + Pilot

## Summary

Build the minimal end-to-end render pipeline (`content/video-engine/`) that turns corpus
technique records and registry articles into landscape + native-vertical stick-figure explainer
videos, gated by two human approvals, and use it to produce the pilot season
(`docs/content-video-engine/07-PILOT-SEASON.md`). Architecture, contract, and strategy are fixed
by the doc set in `docs/content-video-engine/` — this plan implements them; it does not relitigate
them.

## Intent And Acceptance

- Intent: prove format retention (assumption A1) and embed value (A2) with the cheapest real
  pipeline, instrumented for cost and human-time.
- Accepted when: `python content/video-engine/cli.py run --source content/bjj-registry/corpus/armbar-from-guard.json`
  produces, after Gate A/B approvals, the full DoD artifact set (architecture §9) for both
  aspects; and the pilot cohort (5 long-form + 12–16 shorts) is produced through the pipeline
  with analytics snapshots scheduled.

## Scope

Stages `ingesting_source` → `publishing` (manual upload mode), scene classes needed by the pilot
(StickFigure, TitleConceptCard, JointLeverage, MapNetwork), guards, packaging, QC, CLI, tests.

## Not Building

Per PRD §5: upload API/OAuth, monetization work, finance lane, trades lane, registry table
writes, realistic re-creations, orchestration frameworks, parallel rendering. Also deferred to
P1+: reference-recipe extraction (pacing presets from curated videos) and the MCP agent-access
server.

## Human Gates

1. **Plan approval** — operator confirms this plan before any code (in effect for the whole doc set).
2. **Gate A / Gate B per video** — storyboard approval; publish approval (never automated).
3. **Operator inputs before T5 completes:** corpus inventory (≥12 usable records), voice
   decision (cloned-own-voice recommended), music library choice.
4. **Registry embed placement** goes through the registry's existing gated import — this engine
   only emits `embed_payload.json`.

## Mandatory Reads

`docs/content-video-engine/00`–`07` + `storyboard.schema.json`; `AGENTS.md` (repo playbook);
`src/pipeline.py` + `src/repositories/base.py` (patterns to mirror); `content/bjj-registry/src/llm_guard.py`
(guard pattern); `content/bjj-registry/corpus/armbar-from-guard.json` (source shape).

## Execution Path

Implementation spec: **`P13-VIDEO-ENGINE-IMPLEMENTATION.plan.md`** — sizes T1–T8 into seven
agent-assignable work packages (WP-A…WP-G) with frozen interface contracts, real codebase
pattern snippets, and per-package validation. This file remains the status/evidence ledger.

Thin slice first (T1–T7 sequential, each validated), then pilot production (T8) interleaved with
remaining scene classes. TDD per repo testing rules (RED → GREEN → IMPROVE, 80%+ on pure-python
modules; render/TTS integration tests marked slow with mocked providers by default).

## Patterns To Mirror

| Category | Source | Pattern |
|---|---|---|
| Run + stage events | `src/models.py`, `src/pipeline.py` | dataclass run object; append-only stage events; single orchestrator |
| Repository | `src/repositories/base.py`, `file_repository.py` | Protocol + file-backed impl under `runtime/` |
| Guarded LLM w/ fallback | `content/bjj-registry/src/llm_writer.py`, `llm_guard.py` | env-var model config; guard rejects, pipeline falls back / fails closed |
| CLI entrypoint | `scripts/run_insight_pipeline.py` | one entrypoint, explicit flags, no hidden state |
| Evidence-first DoD | `AGENTS.md` §5 | verify artifacts on disk before reporting done |

## Task Slices

### T1: Scaffold + configs
- Status: pending
- Depends on: plan approval
- Write set: `content/video-engine/{configs,content_queue,src,runtime}/…`, `content/video-engine/AGENTS.md`
- Acceptance: tree exists; `configs/storyboard.schema.json` (copied from docs) validates the
  worked example from `04-STORYBOARD-CONTRACT.md` §4 via `jsonschema`; channel + render-profile
  configs load.
- Validate: `python -m pytest content/video-engine/tests/test_configs.py`
- Evidence: pending

### T2: Models, repository, pipeline skeleton, CLI
- Status: pending
- Depends on: T1
- Write set: `src/models.py`, `src/repositories/`, `src/pipeline.py`, `cli.py`, tests
- Acceptance: `cli.py run` with stubbed stages creates `runtime/jobs/<id>/job.json` + ordered
  stage events; `resume` restarts at first incomplete stage; `approve --gate a|b` transitions
  the awaiting stages; per-stage wall-time + cost fields recorded.
- Validate: `python -m pytest content/video-engine/tests/test_pipeline.py -q`
- Evidence: pending

### T3: Storyboard guard (TDD)
- Status: pending
- Depends on: T1
- Write set: `src/guards/storyboard_guard.py`, tests
- Acceptance: rejects — schema violations; unledgered numeric/medical/financial narration;
  claims with `verified: false`; conflict-loop arc violations (missing conflict/comeback pairing
  on >90s runs, order errors); credential framing without `expert`;
  `realistic_recreation` without disclosure; unknown poses/manim_class; pacing-budget breaches;
  shorts referencing missing scenes. Accepts the worked example.
- Validate: `python -m pytest content/video-engine/tests/test_storyboard_guard.py -q`
- Evidence: pending

### T4: Audio synthesis service
- Status: pending
- Depends on: T2
- Write set: `src/services/audio_synth.py`, tests (mocked ElevenLabs)
- Acceptance: per-scene mp3 + `words.json` (character→word grouping) from `/with-timestamps`
  responses; sha256 cache keyed on voice+text+settings; retry ×3 then fail-closed with stage
  event; startup validation of `ELEVENLABS_API_KEY`.
- Validate: `python -m pytest content/video-engine/tests/test_audio_synth.py -q`
- Evidence: pending

### T5: Scene library v1 + render service
- Status: pending
- Depends on: T2; operator voice decision for real-audio smoke test
- Write set: `src/scenes/{base,stick_figure,title_card}.py`, `src/assets/poses/` (initial set incl.
  `closed_guard`, `armbar_extension`, `tap_frantic`), `src/services/manim_render.py`, tests
- Acceptance: ThemedScene handles both aspect frame configs; scenes fill `audio_duration` ±1%
  (asserted); consecutive `transition.in: continuous` scenes of compatible classes render as ONE
  sequence via the section API (no cut); every scene opens in motion within 0.5s (entrance
  contract test); draft ladder renders the armbar storyboard's stick-figure + title scenes
  headless.
- Validate: slow test `pytest -m render_smoke` renders `landscape_draft` for 2 scenes
- Evidence: pending

### T6: Compositor + captions
- Status: pending
- Depends on: T4, T5
- Write set: `src/services/compositor.py`, `src/services/captions.py`, tests
- Acceptance: per-aspect finals with narration + optional music bed (−18 dB rel, ducked,
  continuous across the whole video), −14 LUFS normalize; transition types honored at boundaries
  (crossfade/match/hard only where the storyboard says); burned captions (vertical) from word
  timings, `.srt` (landscape); duration drift vs storyboard ≤2%.
- Validate: `pytest -m assembly` on rendered draft scenes; ffprobe assertions on output
- Evidence: pending

### T7: Packaging + QC + publish (manual mode)
- Status: pending
- Depends on: T6
- Write set: `src/services/{packaging,publish}.py`, `src/guards/qc_checks.py`, tests
- Acceptance: thumbnail stills, `metadata.json` (title variants, UTM-injected description,
  chapters, disclosure determination), `embed_payload.json` (VideoObject JSON-LD + target slugs);
  `qc/report.json` gates Gate B; publish emits upload checklist.
- Validate: full thin-slice run on armbar-from-guard reaches Gate B with QC pass; DoD checklist
  (architecture §9) verified on disk
- Evidence: pending

### T8: Pilot scene classes + pilot production
- Status: pending
- Depends on: T7; corpus inventory
- Write set: `src/scenes/{joint_leverage,map_network}.py`, pose additions (`gym_enforcer`,
  `bowler_hat_maeda`, anatomy poses), pilot storyboards under `content_queue/`
- Acceptance: E5 → E2 → E4 → E1 → E3 produced per `07-PILOT-SEASON.md` order + technique
  shorts; per-episode DoD met; analytics snapshot capture scheduled (day 7/28).
- Validate: per-episode DoD checklist; weekly pilot report exists
- Evidence: pending

## Verification

- `python -m pytest content/video-engine/tests -q` green; coverage ≥80% on pure-python modules
  (guards, services logic, pipeline) — render smoke tests excluded from coverage gate.
- One full evidence-verified run (T7 acceptance) before any pilot storyboard is authored.
- Kill/pivot evaluation at pilot end per `00-BRAINSTORM-AND-DECISIONS.md` §5 — recorded as a
  dated addendum to that doc.

## Evidence And Handoff

Each slice records its validate-command output path under `Evidence:` when completed. Handoff to
P1 (productization) requires: pilot metrics table filled in `07`, cost/human-time table filled,
kill-criteria verdict written.
