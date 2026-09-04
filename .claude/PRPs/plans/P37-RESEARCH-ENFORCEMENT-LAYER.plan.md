---
id: P37-RESEARCH-ENFORCEMENT-LAYER
title: The enforcement layer - the checks that prove today's research reached production
status: draft
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-04
updated: 2026-09-04
---

# The Enforcement Layer

## Summary

The 2026-09-04 research read produced docs 42-46 and, in
[47-FINDINGS-TO-CHECKS](../../../docs/content-video-engine/47-FINDINGS-TO-CHECKS.md), a
per-finding verdict on what can actually be enforced. This PRP builds the enforcement
half: **seven mechanical gates and one agent-judged check.**

It exists because condensing research into a doc is not adoption. The bundle proved that
in miniature - eleven documents were commissioned, one was read, and two backlog items
sat answered in the unread files for a day. A finding with no check is a finding that
silently stops being true.

**Not in scope: the Tier-1 capability builds** (curvature stroke, analytic springs,
area-preserving squash, ARAP morph). Those are code that does not exist yet, and 47 §1
says they should be *designed out* rather than gated - there is nothing to check until
they land. They get their own PRP.

## Intent And Acceptance

**Intent.** Every finding in 47 §2 and §2b becomes a runnable check, wired into the
pipeline stage that can actually see the artifact it reads.

**Acceptance** - all must hold:

1. `gate_motion_density.py` FAILs on a timeline where a camera move overlaps an evidence
   build, and PASSes when they are serialised (G-a).
2. A new comfy-config gate FAILs on the current `parallax-runner.mjs` (`tiling_mode:
   "mirror"`, `ssaa 1.0`, `quality 75`, `intensity 1.0`, `vits`) and on a `num_frames`
   that is not `8n+1` (G-c, G-e), and FAILs when a parallax job names a plate whose kind
   is actor/prop/evidence or that carries text (G-b).
3. A template-transform lint reports every `scale`/`rotate` without an explicit anchor,
   INFO on first landing (G-d).
4. `gate_opening_structure.py`'s G15 additionally verifies the close lands on P1's
   **mechanism**, not only its token (G-g).
5. `judge_muted_caption.py` returns PASS/FAIL **plus a diagnosis** (scenery vs
   over-dense) for a scene pair (V-a).
6. Every new check has a test that fails against the pre-finding artifact.
7. `47-FINDINGS-TO-CHECKS.md` rows for shipped checks say *shipped* and name the script.

**Anti-goals.** No check ships against a threshold we invented. No gate blocks a pipeline
stage that cannot see its artifact. No new gate is added to `run_script_gates.py` without
a fixture proving it fails on the defect it names.

## Scope

`content/video_engine/scripts/` (gate additions and two new scripts),
`content/video_engine/tests/`, and the 47 doc's status column.

## Not Building

- **Tier-1 capability** (47 §1): the curvature stroke, spring evaluator, squash tensor and
  ARAP morph. Separate PRP; they are designed out, not gated.
- **M13** (cut lands in an acoustic gap) - blocked on exploration X3, which settles
  0.30s/onset vs 0.45s/midpoint. Building it now would encode a coin-flip.
- **E1 frame metrics** - blocked on X2. The metric set is right; the thresholds must come
  from measuring ep1 and both references, and adopting a guessed threshold is the exact
  error the metrics exist to catch.
- **G-h** (Kubelka-Munk compositing) - deferred with a trigger. It would FAIL every build
  today because we alpha-blend, and a permanently-red gate is noise until 44's ink work
  lands.
- Any change to `parallax-runner.mjs` itself. G-c **reads** it. The file is the Flow lane
  and currently carries uncommitted work from another agent.

## Human Gates

| gate | why |
|---|---|
| **T4 (G-g) before merge** | It modifies a **shipped** gate. Strengthening G15 can retroactively FAIL scripts that previously passed. The operator decides whether prior PASSes are grandfathered or re-run. |
| **T5 (V-a) before wiring to a build** | Each run costs a model call per scene pair. The operator decides cadence: every build, on demand, or opening-minute only. Ships as a CLI first, unwired. |
| **T2 (G-c) if it is ever made blocking** | It reads a file another lane owns and is actively editing. Report-only until that lane confirms. |

## Mandatory Reads

- [`docs/runbooks/PRP_EXECUTION.md`](../../../docs/runbooks/PRP_EXECUTION.md)
- [`47-FINDINGS-TO-CHECKS.md`](../../../docs/content-video-engine/47-FINDINGS-TO-CHECKS.md) - the source of every check here
- [`45-PARALLAX-AND-PLATE-MOTION.md`](../../../docs/content-video-engine/45-PARALLAX-AND-PLATE-MOTION.md) §45.2-45.4 - the viability matrix and the resolved `intensity` question
- [`CHECK-RESPONSIBILITIES.md`](../../../docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md) - three verdict kinds; a tool's verdict is final, a declared tag is a claim
- `content/video_engine/scripts/gate_motion_density.py` - M08 and M09 are the two patterns this mirrors

`backend-patterns` and `frontend-patterns` are **not** routed: this is Python CLI checks
over JSON and HTML artifacts, with no server boundary, no datastore, and no React surface.

## Execution Path

Recommended route by task shape, per the runbook's dispatch mapping. This session would
execute all slices as parent; the routes are recorded for whichever system runs them.

| slice | route | why |
|---|---|---|
| T1, T3 | `junior_developer` | bounded, exact file, pattern already in the file |
| T2 | `implementation_luna` | new script plus a plate-kind lookup; moderate |
| T4 | **parent** | modifies a shipped gate; human gate attached |
| T5 | **parent** | new judged-check category, model harness, cost decision |
| T6 | `speedster` | deterministic doc status update |

Write sets are disjoint except T1 and T3, which are sequenced rather than parallel.

## Patterns To Mirror

- **M09 `_camera_clashes`** (`gate_motion_density.py:215-227`) - collects `(scene_id, why)`
  by walking `scene["species"]` for camera kinds. G-a is the same walk, intersected with
  dock spans. Mirror the shape and the reporting.
- **M08's INFO-then-FAIL ladder** (`gate_motion_density.py:348-354`) - lands as INFO while
  the artifact cannot yet carry the declaration, promotes to FAIL once it can. **G-d ships
  on this ladder**: the template is 2000 lines and a first pass will surface unknowns.
- **`run_script_gates.py`'s `_call_main` / `ToolResult`** - how a gate joins the composed
  runner without owning its own exit protocol.
- **`gate_motion_density.py`'s `Gate` dataclass + `SRC_*` constants** - every verdict
  carries the ruling it enforces. New gates do the same.

## Task Slices

### T1: G-a - a camera move may not overlap an evidence build
- Status: pending
- Owner: junior_developer
- Depends on: none
- Write set: `content/video_engine/scripts/gate_motion_density.py`, `content/video_engine/tests/test_gate_punch_build_overlap.py`
- Acceptance: a scene whose camera species window intersects a dock build window FAILs; the same timeline with the build starting after the move settles PASSes. Verdict carries `SRC_M14` naming 47 §2 G-a and doc 07 Pillar 4 (saccadic suppression).
- Validate: `python -m pytest content/video_engine/tests/test_gate_punch_build_overlap.py -q`
- Evidence: pending

### T2: G-b, G-c, G-e - the comfy/parallax config gate
- Status: pending
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/scripts/gate_comfy_config.py`, `content/video_engine/tests/test_gate_comfy_config.py`
- Acceptance: FAILs on the current `parallax-runner.mjs` naming all five defects (`tiling_mode`, `ssaa`, `quality`, `intensity`, model); FAILs `num_frames` not `8n+1`; FAILs a parallax job whose plate kind is `actor`/`prop`/`evidence` or that carries text, per the 45 §45.2 matrix. Reads only - never edits the runner.
- Validate: `python content/video_engine/scripts/gate_comfy_config.py tools/google-flow-driver/src/parallax-runner.mjs` (expect FAIL, 5 findings) then `python -m pytest content/video_engine/tests/test_gate_comfy_config.py -q`
- Evidence: pending

### T3: G-d - unanchored transform lint
- Status: pending
- Owner: junior_developer
- Depends on: T1
- Write set: `content/video_engine/scripts/lint_template_transforms.py`, `content/video_engine/tests/test_lint_template_transforms.py`
- Acceptance: reports every `scale(`/`rotate(` applied without an explicit `transformOrigin` or anchor, as **INFO** on first landing (M08 ladder). A synthetic fixture with one anchored and one unanchored transform reports exactly one.
- Validate: `python content/video_engine/scripts/lint_template_transforms.py docs/content-video-engine/samples/scene-evidence-player.template.html`
- Evidence: pending

### T4: G-g - G15 closes on the mechanism, not the token
- Status: pending
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/gate_opening_structure.py`, `content/video_engine/tests/test_gate_ring_mechanism.py`
- Acceptance: G15 keeps its existing token check and adds a mechanism check - the causal claim named in P1 recurs in the close. A script that echoes a P1 *phrase* while the argument has drifted FAILs the new half and PASSes the old. **Human gate: operator decides grandfathering before merge.**
- Validate: `python -m pytest content/video_engine/tests/test_gate_ring_mechanism.py -q` then `python content/video_engine/scripts/run_script_gates.py <ep1 script>` to confirm no unintended regression
- Evidence: pending

### T5: V-a - the muted-caption judge
- Status: pending
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/judge_muted_caption.py`, `content/video_engine/tests/test_judge_muted_caption.py`
- Acceptance: given a prior scene (captions on) and a test scene (captions off), returns PASS/FAIL **and a diagnosis** - `scenery` when the model can only describe the frame, `over-dense` when it cannot resolve the claim at all. Ships as a CLI, **not wired to any build**. Tests use recorded model responses, no live call.
- Validate: `python -m pytest content/video_engine/tests/test_judge_muted_caption.py -q`
- Evidence: pending

### T6: status the 47 rows and register the gates
- Status: pending
- Owner: speedster
- Depends on: T1, T2, T3, T4, T5
- Write set: `docs/content-video-engine/47-FINDINGS-TO-CHECKS.md`, `docs/content-video-engine/CAPABILITIES.md`, `content/video_engine/scripts/run_script_gates.py`
- Acceptance: every shipped check's row names its script and reads *shipped*; CAPABILITIES records the new capability in the same commit (its own recall rule); G-g is registered in the composed runner. Deferred items (M13, E1, G-h) keep their blocking reason.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P37-RESEARCH-ENFORCEMENT-LAYER.plan.md`
- Evidence: pending

## Verification

```powershell
python -m pytest content/video_engine/tests/ -q -k "gate_punch or comfy_config or template_transforms or ring_mechanism or muted_caption"
python content/video_engine/scripts/gate_comfy_config.py tools/google-flow-driver/src/parallax-runner.mjs
python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f
python scripts/prp_validate.py .claude/PRPs/plans/P37-RESEARCH-ENFORCEMENT-LAYER.plan.md
```

**Every new check must be shown failing before it is shown passing.** A gate whose failing
case has not been demonstrated is not evidence that anything is enforced - that is the
whole premise of this PRP, and the coverage gate
(`scripts/check_research_extraction.py`) was negative-tested the same way.

## Evidence And Handoff

- Per-slice: the test file, and the FAIL output against the pre-finding artifact.
- T2 carries the strongest evidence available: the current `parallax-runner.mjs` is a real
  defective artifact, so its FAIL output is proof rather than a fixture.
- On completion, 47's scoreboard updates and `BACKLOG.md`'s Tier-2 table closes its rows.
- **Open, deliberately:** M13, the E1 metrics, and G-h each carry their blocking
  exploration (X3, X2, and 44's ink work). They are not oversights.
