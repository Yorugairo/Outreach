---
id: P13-REMOTION-INSTALL-AND-HYPERFRAMES-LANE
title: Remotion Install Hardening + HyperFrames Render Lane
status: draft
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-08-08
updated: 2026-08-08
---

# Plan: Remotion Install Hardening + HyperFrames Render Lane

## Summary

Two bounded deliverables: (1) verify, pin, and smoke-validate the **existing** Remotion editor at
`content/video_engine/editor/` (it is already the documentary renderer of record per doc 16 —
this is install hardening, not a scaffold); (2) integrate the newly installed **HyperFrames**
toolchain as a *complementary* render lane for short/vertical/caption-led units, driven by the
same canonical narration timings and asset-ID-only contracts the Remotion lane obeys, plus one
bounded port-evaluation spike. No migration of the documentary lane.

## User Story

As the operator, I want the Remotion install verified and HyperFrames wired into the creation
process, so short-form and motion-graphic units render through a fast HTML lane while the
documentary lane stays on its spec-of-record renderer.

## Problem → Solution

Remotion editor exists but has no pinned/validated install contract or smoke render; HyperFrames
skills + CLI (via `npx`, Node v24.16.0 confirmed) are installed but disconnected from the
pipeline. → A healthy, version-pinned `editor/` with typecheck + render smoke, and a
`hyperframes_render` service + unit schema that turns approved assets and word timings into
rendered vertical/short units through the HyperFrames CLI.

## Metadata

- **Complexity**: Large (two toolchains, but bounded scopes; ~12–16 files)
- **Source PRD**: `docs/content-video-engine/01-PRD.md`; supersedes nothing — extends
  `P13-EDITORIAL-MOTION-SYSTEM.plan.md`'s renderer boundary
- **UX**: N/A — operator CLI + artifacts

## Standing decisions this plan MUST respect (from repo instincts + doc 16)

1. Remotion owns the documentary editorial timeline; renderers never invent motion, transitions,
   or overlays — they execute plans.
2. Plans are **asset-ID-only**; raw renderer paths never enter contracts
   (`editorial_motion.py` docstring, verified).
3. Canonical narration word timings are the render clock; hash-matched
   (`canonical_sha256` in `history_contracts.py`).
4. Generated media are hash-recorded, **non-renderable candidates** until approved; only
   approved manifest assets may bind into a renderable unit.
5. Primary plates hold 2–6s (6s hard ceiling); camera defaults to locked (doc 16 §2–3).

---

## Mandatory Reading

| Priority | File | Why |
|---|---|---|
| P0 | `docs/content-video-engine/16-EDITORIAL-MOTION-SYSTEM.md` | Renderer ownership boundary this plan extends |
| P0 | `content/video_engine/src/services/editorial_motion.py` | The compile-plan-then-render pattern to mirror |
| P0 | `content/video_engine/editor/src/{Root,Editorial,EditorialMotion,Documentary}.tsx` + `types.ts` + `package.json` | The existing Remotion surface being hardened — mirror its prop/типing conventions; do NOT invent new ones |
| P0 | `~/.claude/skills/hyperframes/SKILL.md` + `~/.claude/skills/hyperframes-core/SKILL.md` | Entry contract + composition authoring contract (`data-*` timing, seek-safe runtime) |
| P1 | `~/.claude/skills/hyperframes-cli/SKILL.md` | init / check / render / batch commands used by the service |
| P1 | `~/.claude/skills/hyperframes/references/routes/remotion-to-hyperframes.md` | Port-evaluation spike route (T6) |
| P1 | `content/video_engine/src/services/animatic.py`, `compositor.py`, `qc_checks.py` | Where render outputs get validated today |
| P2 | `content/video_engine/configs/asset_manifest.schema.json`, `editorial_motion_plan.schema.json` | Contract style to mirror for the unit schema |
| P2 | `docs/content-video-engine/15-LIVING-SCENE-COMMUNICATION-LANGUAGE.md`, `18-GRAPHIC-SILHOUETTE-WOODBLOCK-EXPLAINER-SPEC.md` | Visual language the units must stay inside |

## External Documentation

| Topic | Source | Key takeaway |
|---|---|---|
| HyperFrames CLI | local skills (above) | Runs via `npx hyperframes@latest`; projects pin `hyperframes@<version>` in package.json scripts for reproducible renders; `upgrade --project . --check` probes pin vs latest; `check` validates compositions |
| HyperFrames routing | `hyperframes` SKILL.md §2 | Short unnarrated motion units → `/motion-graphics`; custom/longer → `/general-video`; explicit Remotion port → `/remotion-to-hyperframes` |
| Remotion | remotion.dev/docs | `npx remotion render <entry> <comp-id> out.mp4 --frames=0-30` for smoke; pin exact versions (all `@remotion/*` packages must share one version) |

KEY_INSIGHT: HyperFrames compositions are HTML whose DOM declares timing via `data-*`; media
playback is framework-owned. APPLIES_TO: T3 schema + T5 composition. GOTCHA: framework-owned
playback means the unit contract must hand HyperFrames asset files + timings and let it own
sequencing — do not pre-bake motion into assets.

## Patterns to Mirror (verified this session)

### SERVICE_CONTRACT_HEADER
```python
# SOURCE: content/video_engine/src/services/editorial_motion.py:1-27
"""Deterministic editorial-motion contracts for narration-led documentaries.
The compiler accepts explicit shot decisions and binds them to canonical word
timings.  It never decides what the edit should mean and never receives raw
renderer paths.  Remotion executes the resulting asset-ID-only plan."""
EDITORIAL_MOTION_PLAN_VERSION = "editorial_motion_plan.v1"
_HASH_RE = re.compile(r"^[a-f0-9]{64}$")
_SAFE_ID_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
```
→ `hyperframes_render.py` opens with the same style: docstring stating what it will NOT decide,
a `HYPERFRAMES_UNIT_VERSION = "hyperframes_unit.v1"` constant, the same `_HASH_RE`/`_SAFE_ID_RE`.

### SCHEMA_VALIDATION
```python
# SOURCE: content/video_engine/src/services/editorial_motion.py:17
from jsonschema import Draft7Validator
```
→ unit schema validated with `Draft7Validator`, all errors collected (repo guard convention).

### ENV_CONFIG  — `LLMConfig.from_env` shape (`content/bjj-registry/src/llm_writer.py:31-49`,
verified earlier): dataclass + `from_env()` classmethod, `os.environ.get` with defaults.
→ `HyperframesConfig.from_env()`: `HYPERFRAMES_NPX` (default `npx`), `HYPERFRAMES_VERSION_PIN`,
`HYPERFRAMES_TIMEOUT_S`.

### TEST_STRUCTURE — builder helpers + determinism assertion
(`tests/test_conversion_readiness.py:12-53`, verified earlier): `_unit(**overrides)` builders,
plain test functions, `first == second` determinism check, `@pytest.mark` for slow/render tests.

## Files to Change

| File | Action | Justification |
|---|---|---|
| `content/video_engine/editor/package.json` | UPDATE | Pin exact versions; add `typecheck` + `render:smoke` scripts |
| `content/video_engine/editor/INSTALL.md` | CREATE | Node/npm version contract, install + smoke commands, recorded versions |
| `content/video_engine/hyperframes/` | CREATE (via `npx hyperframes@latest init`) | The HyperFrames lane project (pinned by scaffold) |
| `content/video_engine/configs/hyperframes_unit.schema.json` | CREATE | Asset-ID-only unit contract (v1) |
| `content/video_engine/src/services/hyperframes_render.py` | CREATE | Compile unit → composition inputs; invoke CLI check/render; validate output |
| `content/video_engine/src/guards/qc_checks.py` | UPDATE | Accept hyperframes-lane outputs (duration vs word timings, safe zones) |
| `content/video_engine/cli.py` | UPDATE | `render-unit <unit.json>` + `verify-editor` commands |
| `content/video_engine/tests/test_hyperframes_render.py` | CREATE | Mocked-CLI unit tests |
| `content/video_engine/tests/test_editor_install.py` | CREATE | `@pytest.mark.render_smoke` Remotion typecheck/smoke wrapper |
| `docs/content-video-engine/19-HYPERFRAMES-LANE.md` | CREATE | Lane spec + port-spike verdict |
| `docs/content-video-engine/08-TOOLING-ALTERNATIVES.md` | UPDATE | §: HyperFrames adopted for unit lane; Remotion unchanged as documentary renderer |
| `.env.example` | UPDATE | `HYPERFRAMES_*` keys (empty-value style) |

## NOT Building

- No migration of Documentary/Editorial compositions off Remotion (T6 produces a **verdict
  document only**).
- No new `create-video` scaffold — the editor exists.
- No changes to `editorial_motion_plan.v1` or any approved schema.
- No publishing, no paid provider calls, no rendering of unapproved/candidate media.
- No HyperFrames cloud/lambda/publish surfaces — local render only.

---

## Step-by-Step Tasks

### T1: Harden the Remotion install
- **ACTION**: In `editor/`: `npm ci` (fall back `npm install` if lock drift, then commit lock);
  pin exact `remotion`/`@remotion/*` versions (strip `^`); add scripts
  `"typecheck": "tsc --noEmit"`, `"render:smoke": "remotion render src/index.tsx <first-comp-id> out/smoke.mp4 --frames=0-30"`
  (read the real composition ids from `Root.tsx` first).
- **MIRROR**: existing package.json script style. **GOTCHA**: all `@remotion/*` packages must be
  the same exact version or the render fails cryptically; Windows paths — quote everything.
- **VALIDATE**: `npm run typecheck` → 0 errors; `npm run render:smoke` → mp4 exists; record
  versions in `editor/INSTALL.md`.

### T2: Scaffold the HyperFrames lane project
- **ACTION**: `npx hyperframes@latest init` under `content/video_engine/hyperframes/`; then
  `npx hyperframes@latest upgrade --project . --check` and `npx hyperframes check`; commit the
  scaffold with its version pin.
- **GOTCHA**: keep the explicit `.` after `--project` (older CLIs eat the next flag); the
  scaffold pins its own version — do not hand-edit the pin.
- **VALIDATE**: `npx hyperframes check` passes on the fresh project; `hyperframes info` output
  recorded in 19-doc.

### T3: `hyperframes_unit.v1` schema
- **ACTION**: Author `configs/hyperframes_unit.schema.json`: `unit_id` (`_SAFE_ID_RE`),
  `unit_kind` enum (`vertical_short`, `title_card`, `caption_unit`, `animatic_preview`),
  `narration` (canonical hash + word-interval selection — same shape editorial_motion binds),
  `assets[]` (manifest asset IDs + sha256 only — no paths), `layout` (aspect, safe zones),
  `holds` (2–6s plate rule inherited), `output` (profile, max_duration_s).
- **MIRROR**: `asset_manifest.schema.json` conventions (versioned `$id`, additionalProperties
  false). **GOTCHA**: no renderer paths in the contract — the service resolves IDs via
  `asset_resolver.py` at render time.
- **VALIDATE**: schema parses; a fixture unit built from episode-1 approved manifest validates.

### T4: `hyperframes_render.py` service + CLI wiring
- **ACTION**: Service compiles a valid unit → composition input files (HTML data-* timings from
  word intervals; assets copied/linked into the project's media dir via `asset_resolver`), runs
  `npx hyperframes check` then `render`, captures stdout/exit, ffprobe-validates duration vs the
  unit's word interval (±2%), writes outputs + summary under `runtime/jobs/<id>/video/hyperframes/`.
  Wire `cli.py render-unit` and `verify-editor`.
- **MIRROR**: SERVICE_CONTRACT_HEADER + stage `StageOutput.summary` conventions;
  fail-closed on CLI nonzero exit (guard style: collect all errors).
- **IMPORTS**: `subprocess`, `jsonschema.Draft7Validator`, `asset_resolver`, `history_contracts.canonical_sha256`.
- **GOTCHA**: framework owns media playback — pass raw assets + timings; never pre-composite.
  Non-interactive shell: always `npx --yes`, explicit timeouts.
- **VALIDATE**: `pytest content/video_engine/tests/test_hyperframes_render.py -q` (CLI mocked)
  — compile determinism (`first == second`), path-rejection, hash-rejection, timeout handling.

### T5: First real unit — vertical teaser from episode-1 approved plates
- **ACTION**: Build one `vertical_short` unit (9:16) from approved episode-1 manifest plates +
  canonical narration slice; render via T4; run qc_checks (duration, safe zones, holds ≤6s).
- **GOTCHA**: candidates outside the approved manifest must hard-fail (instinct #4); woodblock/
  silhouette visual language per doc 18 — no new styles invented in composition CSS.
- **VALIDATE**: rendered mp4 + `qc/report.json` pass on disk; evidence path recorded here.

### T6: Port-evaluation spike (verdict only)
- **ACTION**: Follow `/remotion-to-hyperframes` route against `Editorial.tsx` on a ~15s slice;
  time the effort; compare output vs Remotion render (visual parity, determinism, render time).
- **VALIDATE**: §"Port verdict" written into `19-HYPERFRAMES-LANE.md` with keep/migrate/defer
  recommendation and measured numbers. **No code migration in this plan regardless of verdict.**

### T7: Docs + env + guard closure
- **ACTION**: Write `19-HYPERFRAMES-LANE.md` (lane spec, ownership table extending doc 16 §1:
  Remotion=documentary timeline · HyperFrames=short/caption/motion units · Manim=exact
  diagrams/maps · FFmpeg=inspection/encode); update 08 §1 table; `.env.example` keys; qc_checks
  update + tests.
- **VALIDATE**: full fast suite `python -m pytest content/video_engine/tests -q -m "not render_smoke"` green.

## Validation Commands

```bash
cd content/video_engine/editor && npm run typecheck && npm run render:smoke
```
```bash
cd content/video_engine/hyperframes && npx hyperframes check
```
```bash
python -m pytest content/video_engine/tests -q -m "not render_smoke"
```
```bash
python content/video_engine/cli.py render-unit content/video_engine/tests/fixtures/unit_vertical_teaser.json
```

## Acceptance Criteria
- [ ] Editor: pinned, typecheck 0 errors, smoke render artifact exists, INSTALL.md recorded
- [ ] HyperFrames project scaffolded, pinned, `check` green
- [ ] Unit schema + service merged with mocked tests green; determinism asserted
- [ ] One approved-asset vertical unit rendered with QC pass (evidence on disk)
- [ ] Port verdict written; docs 08/19 updated; no documentary-lane changes

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| HyperFrames CLI behavior differs from skill docs on Windows | Medium | Medium | T2 validates the toolchain before any service code; service treats CLI as black box behind config |
| Remotion version drift breaks existing compositions on `npm ci` | Low-Med | High | Pin exact versions from the working lockfile; smoke render is the tripwire |
| Two JS toolchains sprawl | Medium | Medium | Lane boundaries fixed in 19-doc; NOT-building list forbids migration; spike is verdict-only |
| Unit lane leaks unapproved candidates | Low | High | Schema forbids paths; resolver validates manifest membership + sha256; test covers rejection |

## Notes
- Interpretation recorded: "the remotion install" = harden the **existing** `editor/` install
  (discovered during exploration), not a new `create-video` scaffold. If a separate greenfield
  Remotion project was intended, say so and T1 becomes a scaffold task instead.
- HyperFrames invocation is always `npx hyperframes@latest` for tooling and the project pin for
  renders — never a global install (none exists; Node v24.16.0 verified).

## Confidence Score
**7/10** — repo side is fully patterned; the two uncertainty sources are HyperFrames CLI
behavior on this machine (mitigated by T2-first ordering) and unread `editor/` package.json
internals (mitigated by T1 reading before pinning).
