---
id: P16-CONSOLE-EDITOR-CONVERGENCE
title: One operator surface — console shells, links, and round-trips the Remotion editor
status: draft
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-08-23
updated: 2026-08-23
---

# Console + Editor Convergence

## Summary

The console (Python/FastAPI, P15) and the Remotion editor
(`content/video_engine/editor/`, Node, pinned 4.0.502) are two windows onto the
same artifacts. They should not become one program — fusing processes couples
review tooling to the render toolchain's versioning and re-imports the build
step P15 excluded — but they should become **one surface**: one entrypoint, one
nav, deep links from any slot or run into the right editor context, and a
headless round-trip that makes Studio the exception surface rather than the
default one.

The unifying identity is the job artifact on disk, not the process.

## Intent And Acceptance

Accepted when:

1. `python -m content.video_engine.console --with-editor` starts the console
   and Remotion Studio together, and stopping the console stops Studio — no
   orphaned Node process on Windows.
2. The console shows Studio's state (stopped / starting / serving on port N /
   failed with stderr) and can start and stop it from the UI.
3. Any board slot or run offers "Open in editor," landing on the correct
   composition in Studio; the link degrades to Studio's root when a deeper URL
   is not supported by the pinned version — verified, not assumed.
4. A headless render round-trip works from the console: props composed from job
   artifacts by a service, render executed through the editor's own npm
   scripts, output visible in Runs. The console composes props; it never
   implements camera, timing or easing (the P15 T10 rule, held by the same
   structural test).
5. No file under `editor/src/` changes in this plan.
6. All process handling goes through one monkeypatchable boundary per module,
   mirroring `console/routes/preview.py::_run_command`.

## Scope

- A studio lifecycle service and console controls for it.
- `--with-editor` on the console entrypoint.
- Deep links from board and runs views into Studio.
- A props-composition service and a headless-render trigger in the console.
- A timeboxed embedding evaluation with a recorded go/no-go.

## Not Building

- **No changes to `editor/src/`** — compositions, camera behaviour and props
  contracts stay owned by the render lane.
- No React, no bundler in the console; the console remains no-build.
- No motion logic in the console package (structural test from P15 T10 stays).
- No HyperFrames changes; its lane is already reachable via T10.
- No remote or multi-user anything. Loopback only, both processes.
- No paid provider calls.

## Human Gates

| Gate | Who | Rule |
| --- | --- | --- |
| Embedding decision (T6) | Operator | Spike result presented; iframe ships only on explicit approval, otherwise deep links stand |
| Render triggers | Operator | UI-initiated only; no route renders on page load |
| Gate A / Gate B | Operator | Unchanged; convergence adds no new approval surface |

## Mandatory Reads

- `backend-patterns` — service boundaries, process handling at the edge
- `.claude/PRPs/plans/P15-OPERATOR-CONSOLE.plan.md` — the console's rules this extends (routes compute nothing; lanes own motion; offline chrome)
- `content/video_engine/console/routes/preview.py` — the `_run_command` single-boundary pattern and threaded pending-state pattern to mirror
- `content/video_engine/editor/package.json` — the npm scripts that are the only editor interface (`start`, `render`, `render:smoke`, `typecheck`)
- `content/video_engine/cli.py` — `verify-editor` shows the existing npm-wrapping convention (shutil.which("npm"), cwd=editor, timeout)
- `content/video_engine/editor/src/Root.tsx` — composition ids and the defaultProps/input-props merge the round-trip relies on
- `docs/content-video-engine/19-HYPERFRAMES-LANE.md` — renderer ownership table

## Execution Path

Order: T1 → (T2, T3 parallel) → T4 → T5 → T6. T2 and T3 have disjoint write
sets. T4 begins with a read-only verification step because Studio deep-link URL
support in 4.0.502 must be established from the pinned version's docs, not
assumed.

```
content/video_engine/src/services/
  editor_studio.py      lifecycle: start/stop/status/health of `npm run start`
  editor_render.py      compose props JSON from job artifacts; build render cmd
content/video_engine/console/routes/
  editor.py             controls + status; thin over the services
runtime/console-state/  studio.pid.json (tracked state, never hand-edited)
```

## Patterns To Mirror

- **Single process boundary** — `preview.py::_run_command`; tests monkeypatch it.
- **Pending state without JS frameworks** — `preview.py` daemon thread + polled view.
- **npm wrapping** — `cli.py` verify-editor: resolve npm via `shutil.which`, run with `cwd=editor_dir`, surface stderr tails verbatim.
- **Read-only status views** — `routes/runs.py`: probe before constructing anything that writes.
- **Compile/record split** — props composition emits a file; the render command consumes it; no hidden state.

## Task Slices

### T1: Studio lifecycle service
- Status: pending
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/src/services/editor_studio.py`, `content/video_engine/tests/test_editor_studio.py`
- Acceptance: `start()` launches `npm run start` in the editor directory and records pid + port + started_at under `runtime/console-state/studio.pid.json`; `status()` reports stopped / starting / serving / failed, probing the recorded pid and port without spawning anything; `stop()` terminates the **process tree** (Windows: `taskkill /T`; POSIX: process group) and proves the pid is gone before returning; a stale pid file (machine rebooted, pid reused) is detected rather than trusted, by matching process identity, and reported as stale; a second `start()` while serving is a no-op returning the existing state; npm missing on PATH is a named error, not a stack trace. All process operations pass through one module-level boundary that tests monkeypatch; tests use a fake long-running process, never real npm.
- Validate: `python -m pytest content/video_engine/tests/test_editor_studio.py -q`
- Evidence: pending

### T2: Console editor controls
- Status: pending
- Owner: junior_developer (dispatches as `general-purpose`)
- Depends on: T1
- Write set: `content/video_engine/console/routes/editor.py`, `content/video_engine/console/templates/editor.html`, `content/video_engine/tests/test_console_editor.py`
- Acceptance: an Editor view shows Studio state with the existing chip vocabulary (glyph + text + colour), start and stop as explicit POST forms, the serving URL as a plain link when up, and stderr verbatim on failure; routes are thin over T1 and contain no process logic; the offline template scan passes; a status GET constructs nothing and writes nothing (byte-snapshot test). Parent wires router and nav.
- Validate: `python -m pytest content/video_engine/tests/test_console_editor.py -q`
- Evidence: pending

### T3: --with-editor entrypoint
- Status: pending
- Owner: junior_developer (dispatches as `general-purpose`)
- Depends on: T1
- Write set: `content/video_engine/console/__main__.py`, `content/video_engine/tests/test_console_entrypoint.py`
- Acceptance: `--with-editor` starts Studio via T1 before serving and stops it on shutdown (normal exit and KeyboardInterrupt both covered); without the flag behaviour is byte-for-byte today's; startup failure of Studio is reported and the console still serves — a dead editor never takes the review surface down with it.
- Validate: `python -m pytest content/video_engine/tests/test_console_entrypoint.py -q`
- Evidence: pending

### T4: Deep links into Studio
- Status: pending
- Owner: parent (verification step routed as `Explore`/docs check first)
- Depends on: T2
- Write set: `content/video_engine/console/routes/board.py`, `content/video_engine/console/routes/runs.py`, `content/video_engine/console/templates/board.html`, `content/video_engine/console/templates/runs.html`, `content/video_engine/tests/test_console_deeplinks.py`
- Acceptance: **first, a recorded verification** of what Studio 4.0.502 actually supports in URLs (composition path, props payload, neither) — from the pinned version's documentation or the installed package, cited in evidence; then board slots and runs render "Open in editor" links using the deepest supported form, falling back to Studio root; links appear only while Studio reports serving; link construction lives in one tested helper, not in templates.
- Validate: `python -m pytest content/video_engine/tests/test_console_deeplinks.py -q`
- Evidence: pending

### T5: Headless render round-trip
- Status: pending
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/src/services/editor_render.py`, `content/video_engine/console/routes/editor.py`, `content/video_engine/tests/test_editor_render.py`
- Acceptance: `compose_props()` builds an `EditorialMotion` input-props JSON from a job's artifacts (coverage, catalogue-resolved assets, canonical audio when present) and writes it under `runtime/`; composition is pure translation — any timing or camera value is copied from artifacts, never computed, and the P15 structural motion-arithmetic test is extended to cover the new modules; the render route invokes `npm run render` (or `npx remotion render` with explicit args) through the T1-style boundary with `--props` pointing at the composed file; output lands under `runtime/` and appears in Runs; failures surface the renderer's stderr verbatim; a render is operator-triggered, with the threaded pending-state pattern from preview.py.
- Validate: `python -m pytest content/video_engine/tests/test_editor_render.py content/video_engine/tests/test_console_motion_preview.py -q`
- Evidence: pending

### T6: Embedding spike — decide, don't drift
- Status: pending
- Owner: parent
- Depends on: T2
- Write set: `docs/content-video-engine/25-EDITOR-EMBEDDING-SPIKE.md`
- Acceptance: a timeboxed evaluation of iframing Studio into a console tab — same-origin constraints, CSP, WebSocket behaviour, and whether it beats a deep link on a dual-monitor desktop — written up with a recommendation and **presented to the operator as a gate**; no iframe ships in this plan regardless of outcome; the doc records the decision either way so it is not relitigated.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P16-CONSOLE-EDITOR-CONVERGENCE.plan.md`
- Evidence: pending

## Verification

```bash
python -m pytest content/video_engine/tests/ -q
python scripts/prp_validate.py .claude/PRPs/plans/P16-CONSOLE-EDITOR-CONVERGENCE.plan.md
```

- Full suite green apart from the five pre-existing `test_history_v4_pipeline.py` failures (`task_5672544a`).
- Manual: `--with-editor` up, editor state visible, kill the console, verify no orphaned node.exe in Task Manager; trigger one headless render from the console and see the output in Runs.
- The P15 motion-arithmetic structural test passes over the enlarged console/service surface.

## Risks

| Risk | Level | Mitigation |
| --- | --- | --- |
| Orphaned Node processes on Windows | Medium | T1 kills the tree and proves death; stale-pid detection; Runs surfaces orphans |
| Studio URL scheme narrower than hoped at 4.0.502 | Medium | T4 verifies before building; root-link fallback is acceptable |
| Props drift between console-composed and pipeline-composed renders | Medium | `compose_props` is pure translation with the structural no-arithmetic test extended over it |
| Scope creep toward "console renders video" | High if unwatched | Lanes render; console presses buttons — the T10 rule, restated as acceptance |
| Editor upgrade breaks lifecycle assumptions | Low | Only npm scripts are the interface; no Studio internals parsed |

## Evidence And Handoff

Pending. Nothing implements while `status: draft`.
