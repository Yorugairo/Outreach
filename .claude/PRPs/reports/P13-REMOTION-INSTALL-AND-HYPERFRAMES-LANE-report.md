# Implementation Report: Remotion Install Hardening + HyperFrames Render Lane

*Date: 2026-08-08 · Plan: `P13-REMOTION-INSTALL-AND-HYPERFRAMES-LANE.plan.md` · Branch: `claude/content-generation-system-52f077`*

## Summary

Hardened the existing Remotion editor (pinned 4.0.502, typecheck + smoke render verified) and
integrated HyperFrames (pinned 0.7.101) as the short/caption/motion **unit lane**: asset-ID-only
`hyperframes_unit.v1` contract → deterministic HTML compile → check → render → duration QC.
First real unit rendered from approved episode-1 archive plates with 0.14% duration drift.

## Assessment vs Reality

| Metric | Predicted (Plan) | Actual |
|---|---|---|
| Complexity | Large, ~12–16 files | Large — 17 files (incl. scaffold) |
| Confidence | 7/10 | Landed; both flagged uncertainties materialized mildly (npx-in-project wrapper quirk; editor already pinned) |

## Tasks

| # | Task | Status | Notes |
|---|---|---|---|
| T1 | Harden Remotion install | ✅ | Versions were already exactly pinned — task reduced to smoke script + `npm ci` + INSTALL.md. **Deviation:** smoke target is `Documentary` (60-frame default), not `Editorial` (1-frame default) |
| T2 | Scaffold HyperFrames project | ✅ | `--example=blank --non-interactive`; check: 0 issues/9 samples. **Deviation:** bare `npx hyperframes` fails inside project — use the scaffold's npm-script wrappers (pinned `npx --yes hyperframes@0.7.101`) |
| T3 | `hyperframes_unit.v1` schema | ✅ | As planned + semantic checks in service (holds 2–6s, contiguity, max duration) |
| T4 | Service + CLI wiring | ✅ | `render-unit` + `verify-editor` commands added in repo dispatch style |
| T5 | First unit render | ✅ | **Deviation:** no canonical ElevenLabs word timings exist (paid synthesis gated) → rendered as `animatic_preview` with deterministic 140wpm estimated timings hash-bound to the approved narration source. Publishable kinds require canonical timings by rule (19-doc §3) |
| T6 | Port-evaluation spike | ⚠️ **DEFERRED** | Not executed; recorded as NOT RUN in 19-doc §6 with standing verdict "keep Remotion". No migration licensed |
| T7 | Docs/env/QC closure | ✅ | **Deviation:** QC lives in the service summary; `guards/qc_checks.py` not modified (recorded as v1 limitation) |

## Validation Results

| Level | Status | Notes |
|---|---|---|
| Static (editor typecheck) | ✅ | `tsc --noEmit` 0 errors |
| Unit tests | ✅ | 11 new tests, all pass (`test_hyperframes_render.py`) |
| Full fast suite | ⚠️ | 348 passed, **5 pre-existing failures** in `test_history_v4_pipeline.py` — **verified pre-existing via `git stash` (identical failures on the clean tree)**; out of plan scope, spun off as a separate task |
| Smoke render (Remotion) | ✅ | `editor/out/smoke.mp4`, 1.088s, 70,685 B |
| Integration (real unit) | ✅ | `ep1-teaser-animatic-v1`: check pass, 6.867s vs 6.857s expected, drift 0.14% (< 2% gate), QC pass |

## Files Changed

CREATE: `configs/hyperframes_unit.schema.json` · `src/services/hyperframes_render.py` ·
`tests/test_hyperframes_render.py` · `editor/INSTALL.md` · `hyperframes/` scaffold (7 files +
`.gitignore`) · `projects/history-of-bjj/units/ep1-teaser-animatic-v1.unit.json` ·
`docs/content-video-engine/19-HYPERFRAMES-LANE.md` · this report
UPDATE: `editor/package.json` (render:smoke) · `cli.py` (render-unit, verify-editor) ·
`docs/content-video-engine/08-TOOLING-ALTERNATIVES.md` (§8) · `.env.example` (HYPERFRAMES_*)

## Issues Encountered

1. `npx hyperframes check` inside the scaffolded project → "could not determine executable";
   resolved by honoring the project's pinned npm-script wrappers (skill contract says obey wrappers).
2. `doctor` reports ok=false from optional-only components (whisper/Kokoro/MusicGen) — hard
   dependencies all pass; documented in 19-doc §7.

## Next Steps

- [ ] Run T6 port spike when a migration decision is actually needed
- [ ] Generate canonical ElevenLabs audio (operator-gated) to unlock publishable unit kinds
- [ ] Fold unit QC into `guards/qc_checks.py` (v2)
- [ ] Fix pre-existing history_v4 failures (separate spun-off task)
