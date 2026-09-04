---
id: P38-KINETICS-CAPABILITY-LAYER
title: The kinetics layer - the six designed-out capabilities, each with the test that fails without it
status: draft
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-04
updated: 2026-09-04
---

# The Kinetics Capability Layer

## Summary

[47-FINDINGS-TO-CHECKS](../../../docs/content-video-engine/47-FINDINGS-TO-CHECKS.md) §1
names six findings that should be **designed out** rather than gated — once built, the
wrong path stops existing and there is nothing to route around. This PRP builds them.

P37 is the enforcement half; this is the capability half. **It is the one that changes
what the video looks like.**

Written now, while the five research passes are in working memory, because a PRP's job is
to survive context loss — and leaving this unwritten would repeat the mistake that opened
the backlog this morning.

> **Depends on [P39-RENDER-BASELINE-AND-KILL-SWITCH](P39-RENDER-BASELINE-AND-KILL-SWITCH.plan.md).**
> T2 changes every drawn object, and today there is no golden-frame test, no tag, and no way to turn a capability
> off. P39 supplies all three. **Do not start this plan first.**

## Intent And Acceptance

**Intent.** Six pure-math capabilities land as a node-testable module, each with a test
that fails against the pre-finding implementation, and the stroke is wired into the
renderer so every drawn object inherits it.

**Acceptance:**

1. A stroke drawn over a path with one sharp corner and one long straight satisfies
   `v(max κ) < v(min κ)`, and `w(max κ) > w(min κ)`. **A straight path returns finite
   velocity** (the κ₀ regulariser).
2. The spring evaluator returns identical state for frame N evaluated directly and frame N
   reached by stepping 0..N. Peak overshoot matches `M_p = exp(−πζ/√(1−ζ²))` within
   tolerance, across all three damping regimes.
3. `det(A(t)) == 1` for the squash tensor at every t and every α.
4. A morph carrying >90° of rotation holds `det(J(t)) > 0` at every t.
5. A joint flexed 180° at w=0.5 holds `det(T_blend) == 1`. **The same case under linear
   blend skinning returns the zero matrix** — that contrast is the test.
6. A prop picked up mid-move is positionally continuous across the handover frame, and its
   scene-graph parent never changed.
7. `drawOn` in the template routes through the curvature profile; the 16:9 render of ep1
   is visually diffed and approved before merge.

**Anti-goals.** No capability ships without its failing test demonstrated first. **Every capability that alters rendered output ships behind its P39 flag, defaulting to current behaviour** - a bad result must be one timeline field away from the old render, never a debugging session. No
tunable is presented as a finding — `γ`, `λ_w`, `κ_v`, per-material `ζ`/`ω₀` are ours
(42 §42.5). No change to the standalone-openability of the template.

## Scope

`content/video_engine/scripts/kinetics/` (new), `content/video_engine/tests/`, and the
`drawOn` call site in `docs/content-video-engine/samples/scene-evidence-player.template.html`.

## Not Building

- **Every gate.** They are P37. This PRP produces capability; P37 produces enforcement.
- **FABRIK, pseudo-3D head turns, two-handed closed chains** (48/09) — deferred with
  triggers in the backlog, and no shot needs them.
- **The Kubelka-Munk ink compositor** (44). It is a rendering-pipeline change, not a
  kinetics one, and 44 §44.5 puts it below the motion work: it is worth nothing on a page
  that still draws like a plotter.
- **The prop art library** (backlog A2). This builds the machinery that draws props, not
  the props.

## Human Gates

| gate | why |
|---|---|
| **T2 before merge** | The curvature stroke changes how **every drawn object in the engine** looks — charts, callouts, squiggles, props. That is the largest single visual change we have made. Operator sees a before/after on one ledger page and one chart before it lands. |
| **T8 before merge** | Re-renders ep1. Visual review, not a metric. |
| **T1's inlining decision** | It changes how the template is assembled. Reversible, but it touches the one file everything renders through. |

## Mandatory Reads

- [`docs/runbooks/PRP_EXECUTION.md`](../../../docs/runbooks/PRP_EXECUTION.md)
- [`47-FINDINGS-TO-CHECKS.md`](../../../docs/content-video-engine/47-FINDINGS-TO-CHECKS.md) §1 — the six items and their tests
- [`42-DRAWING-KINETICS.md`](../../../docs/content-video-engine/42-DRAWING-KINETICS.md) — stroke, springs, squash, and §42.5's list of what is *ours to tune*
- [`43-SCENE-GRAPH-AND-TRANSFORM.md`](../../../docs/content-video-engine/43-SCENE-GRAPH-AND-TRANSFORM.md) §43.5 — both morph methods and the decision rule between them
- [`48-THE-FIGURE-AND-THE-GROUND.md`](../../../docs/content-video-engine/48-THE-FIGURE-AND-THE-GROUND.md) §48.3, §48.5 — DQS and cached-offset attachment
- `docs/content-video-engine/samples/scene-evidence-player.template.html:1940` — `drawOn`, one line, currently `spEase(k)`

`backend-patterns` and `frontend-patterns` are **not** routed: this is pure math in ES
modules plus one template call site. No server boundary, no datastore, no React.

## Execution Path

| slice | route | why |
|---|---|---|
| T1 | **parent** | an architecture decision about how the template is assembled |
| T2 | **parent** | largest visual change in the engine; human gate attached |
| T3, T4 | `implementation_luna` | bounded math with exact acceptance |
| T5, T6, T7 | `implementation_luna` | bounded math with exact acceptance |
| T8 | **parent** | integration and visual review |

T2–T7 write disjoint files and can run in parallel once T1 lands.

## Patterns To Mirror

- **`content/video_engine/editor/fixtures/editorial-motion-two-shot/render.mjs`** and
  `production_console/scripts/e2e-smoke.mjs` — `.mjs` is already normal here, and node
  v24.16 is available, so `node --test` needs **zero new dependencies**.
- **`build_scene_timeline_f.py:44`** reads the template and emits a per-build player.
  That existing generation step is where T1's sync belongs — no new build stage.
- **`gate_motion_density.py`'s `SRC_*` constants** — every behaviour carries the doc
  section that justifies it. The kinetics functions do the same in their docstrings.

## Task Slices

### T1: make the template's math testable at all
- Status: pending
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/kinetics/` (new dir), `content/video_engine/scripts/sync_kinetics.py`, `content/video_engine/tests/test_kinetics_sync.py`
- Acceptance: **there is currently no test path to the template's JavaScript — no test file references it, and the math lives inline in a 2000-line HTML file.** TDD is impossible until that changes. The module directory becomes the source of truth; `sync_kinetics.py` inlines each module into the template between `/* KINETICS:BEGIN <name> */` and `/* KINETICS:END */` markers; a test asserts the inlined copy is byte-identical to the module. **The template stays standalone-openable** — the code is physically present, not imported at runtime.
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check` then `python -m pytest content/video_engine/tests/test_kinetics_sync.py -q`
- Evidence: pending

### T2: the curvature-reparameterised stroke
- Status: pending
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/scripts/kinetics/stroke.mjs`, `content/video_engine/tests/kinetics/stroke.test.mjs`
- Acceptance: `v(s) = γ·(|κ(s)| + κ₀)^(−1/3)·ψ(s)`, inverted to `s(t)` by Newton-Raphson, with `w(s)` and ink density coupled to the same profile (42 §42.1). Tests: on a path with one corner and one straight, `v(max κ) < v(min κ)` and `w(max κ) > w(min κ)`; a straight path returns finite `v` (κ₀); endpoints start and end at rest (ψ). **The current one-line `spEase(k)` implementation fails the first two.**
- Validate: `node --test content/video_engine/tests/kinetics/stroke.test.mjs`
- Evidence: pending

### T3: the analytic spring evaluator
- Status: pending
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/scripts/kinetics/spring.mjs`, `content/video_engine/tests/kinetics/spring.test.mjs`
- Acceptance: all three damping regimes returning position **and velocity** (velocity is needed by T4). Tests: **the seek test** — frame N direct equals frames 0..N stepped, bit-identical; measured peak overshoot matches `M_p = exp(−πζ/√(1−ζ²))` at `t_p = π/ω_d`; `ζ=1` overshoots zero. Serves settle, secondary motion and placement (48 §48.6) — one evaluator, three callers.
- Validate: `node --test content/video_engine/tests/kinetics/spring.test.mjs`
- Evidence: pending

### T4: area-preserving squash
- Status: pending
- Owner: implementation_luna
- Depends on: T1, T3
- Write set: `content/video_engine/scripts/kinetics/squash.mjs`, `content/video_engine/tests/kinetics/squash.test.mjs`
- Acceptance: `A(t) = R(θ)·diag(1+α, 1/(1+α))·R(−θ)` with α driven by speed and deceleration (42 §42.3). Test: `det(A(t)) == 1` within float tolerance across a sweep of t and α, including α → 0 and large α.
- Validate: `node --test content/video_engine/tests/kinetics/squash.test.mjs`
- Evidence: pending

### T5: the ARAP morph
- Status: pending
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/scripts/kinetics/morph.mjs`, `content/video_engine/tests/kinetics/morph.test.mjs`
- Acceptance: closed-form 2D polar decomposition `θ = atan2(j₂₁−j₁₂, j₁₁+j₂₂)`, rotation interpolated on SO(2) and stretch on Sym⁺(2) (43 §43.5B). Test: **morph a shape through >90° of rotation and assert `det(J(t)) > 0` at every t; the same morph under naive vertex lerp goes non-positive.** Ship Method A (vertex resampling + rotational alignment) alongside, per 43 §43.5's decision rule.
- Validate: `node --test content/video_engine/tests/kinetics/morph.test.mjs`
- Evidence: pending

### T6: DQS joint blending
- Status: pending
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/scripts/kinetics/skin.mjs`, `content/video_engine/tests/kinetics/skin.test.mjs`
- Acceptance: unit dual-complex blending on SE(2), normalised (48 §48.3). Test: **flex a joint 180° at w=0.5; assert `det(T_blend) == 1`. Assert the linear-blend-skinning comparison returns the zero matrix on the same input** — the candy-wrapper elbow as a one-line contrast, and the cleanest failing test in the set.
- Validate: `node --test content/video_engine/tests/kinetics/skin.test.mjs`
- Evidence: pending

### T7: cached-offset prop attachment
- Status: pending
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/scripts/kinetics/attach.mjs`, `content/video_engine/tests/kinetics/attach.test.mjs`
- Acceptance: `M_offset = M_hand⁻¹(t*)·M_world,prop(t*)` cached at pickup; `M_world,prop(t) = M_hand(t)·M_offset` while held; release inherits `v_hand + ω_hand × r_offset` (48 §48.5). Tests: world position continuous across the handover frame (no one-frame pop) with the hand mid-move; **the prop's parent is never mutated**; release velocity is non-zero when the hand is rotating.
- Validate: `node --test content/video_engine/tests/kinetics/attach.test.mjs`
- Evidence: pending

### T8: wire the stroke into the renderer and diff the render
- Status: pending
- Owner: parent
- Depends on: T2, and P37's T0 if that has not already landed
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html`
- Acceptance: `drawOn` routes through `stroke.mjs`'s profile instead of `spEase(k)`. Ep1 and one Tokyo ledger page re-render; a before/after frame pair goes to the operator. **Charts, callouts, squiggles and props all change at once because `drawOn` is object-agnostic** — that breadth is the point, and it is also the risk.
- Validate: `python content/video_engine/scripts/build_scene_timeline_f.py` then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f` — no new FAILs
- Evidence: pending

## Verification

```powershell
node --test content/video_engine/tests/kinetics/
python -m pytest content/video_engine/tests/test_kinetics_sync.py -q
python content/video_engine/scripts/sync_kinetics.py --check
python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f
python scripts/prp_validate.py .claude/PRPs/plans/P38-KINETICS-CAPABILITY-LAYER.plan.md
```

**Every capability is shown failing before it is shown passing.** For T2, T5 and T6 the
failing case is not synthetic — the current `spEase` stroke, naive vertex lerp, and linear
blend skinning are the real prior art, and each fails its test by construction.

## Evidence And Handoff

- Per slice: the test file and its RED output against the prior implementation.
- T2 and T8 additionally carry a before/after frame pair — the only slices whose evidence
  is visual rather than numeric.
- On completion, 47 §1's six rows say *shipped* and name their module, and `CAPABILITIES.md`
  records the kinetics layer in the same commit (its own recall rule).
- **T1 is the unlock and it is not optional.** There is no test path to the template's JS
  today, so without it none of the other six tests can be written at all.
