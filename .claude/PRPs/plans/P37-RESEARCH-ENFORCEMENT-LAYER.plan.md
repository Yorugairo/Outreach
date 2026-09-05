---
id: P37-RESEARCH-ENFORCEMENT-LAYER
title: The enforcement layer - the checks that prove today's research reached production
status: complete
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-04
updated: 2026-09-04
supersedes_note: amended twice - docs 48 and 49 added six gates and one urgent fix
---

# The Enforcement Layer

## Summary

The 2026-09-04 research read produced docs 42-46 and, in
[47-FINDINGS-TO-CHECKS](../../../docs/content-video-engine/47-FINDINGS-TO-CHECKS.md), a
per-finding verdict on what can actually be enforced. This PRP builds the enforcement
half: **thirteen mechanical gates and one agent-judged check.**

**Amended twice on 2026-09-04.** Doc 48 added three gates (T7) and moved two Tier-1 items
to the capability PRP. Doc 49 added three more (T8) — **and one of them fails code we
already ship**, so T0 jumps the queue.

It exists because condensing research into a doc is not adoption. The bundle proved that
in miniature - eleven documents were commissioned, one was read, and two backlog items
sat answered in the unread files for a day. A finding with no check is a finding that
silently stops being true.

**Not in scope: the Tier-1 capability builds** (curvature stroke, analytic springs,
area-preserving squash, ARAP morph). Those are code that does not exist yet, and 47 §1
says they should be *designed out* rather than gated - there is nothing to check until
they land. They get their own PRP: **[P38-KINETICS-CAPABILITY-LAYER](P38-KINETICS-CAPABILITY-LAYER.plan.md)**, drafted 2026-09-04.

> **Depends on [P39-RENDER-BASELINE-AND-KILL-SWITCH](P39-RENDER-BASELINE-AND-KILL-SWITCH.plan.md).**
> T0 edits the template, and today there is no golden-frame test, no tag, and no way to turn a capability
> off. P39 supplies all three. **Do not start this plan first.**

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
7. A grounding gate FAILs a composited figure whose eye height misses the plate horizon,
   a grounded sprite not anchored at `50% 100%`, and a contact beat with no declared
   solver (G-i, G-j, G-k).
8. `47-FINDINGS-TO-CHECKS.md` rows for shipped checks say *shipped* and name the script.

**Anti-goals.** No check ships against a threshold we invented. No gate blocks a pipeline
stage that cannot see its artifact. No new gate is added to `run_script_gates.py` without
a fixture proving it fails on the defect it names.

## Scope

`content/video_engine/scripts/` (gate additions and two new scripts),
`content/video_engine/tests/`, and the 47 doc's status column.

## Not Building

- **Tier-1 capability** (47 §1): the curvature stroke, spring evaluator, squash tensor,
  ARAP morph, **DQS joint blending and cached-offset prop attachment** (added by doc 48).
  Separate PRP; they are designed out, not gated. Note the DQS test is the cleanest
  failing test in the whole set - linear blend skinning returns the zero matrix at 180°
  and w=0.5 - so P38 leads with it (its T6).
- **M13** (cut lands in an acoustic gap) - blocked on exploration X3, which settles
  0.30s/onset vs 0.45s/midpoint. Building it now would encode a coin-flip.
- **E1 frame metrics** - blocked on X2. The metric set is right; the thresholds must come
  from measuring ep1 and both references, and adopting a guessed threshold is the exact
  error the metrics exist to catch.
- **G-h** (Kubelka-Munk compositing) - deferred with a trigger. It would FAIL every build
  today because we alpha-blend, and a permanently-red gate is noise until 44's ink work
  lands.
- Nothing is excluded on ownership grounds. An earlier draft deferred `parallax-runner.mjs`
  to "the Flow lane"; there is no such lane. **T9 fixes it here**, and G-c uses the pre-fix
  file as its fixture — the same pattern as T0 and G-l.

## Human Gates

| gate | why |
|---|---|
| **T4 (G-g) before merge** | It modifies a **shipped** gate. Strengthening G15 can retroactively FAIL scripts that previously passed. The operator decides whether prior PASSes are grandfathered or re-run. |
| **T5 (V-a) before wiring to a build** | Each run costs a model call per scene pair. The operator decides cadence: every build, on demand, or opening-minute only. Ships as a CLI first, unwired. |
| **T9 before merge** | `parallax-runner.mjs` currently carries ~86 lines of uncommitted work from a concurrent session. Rebase or coordinate before editing, or the fix collides. |

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
| **T0** | `junior_developer` | **urgent - fixes shipped geometry; run first** |
| T7 | `implementation_luna` | new script; needs shot-table fields that may not exist yet |
| T8 | `implementation_luna` | new script plus comfy-gate additions; T0 is its fixture |
| T9 | `junior_developer` | six literal values plus a model string; fully specified |
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

### T0: fix the 9:16 dock geometry - it sits under platform chrome
- Status: complete
- Owner: parent (kept - shipped geometry, goldens refreshed)
- Depends on: none
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html`, `content/video_engine/tests/test_vertical_safe_box.py`
- Acceptance: `.dock` under `html[data-aspect="9:16"]` is `width: 800px; left: 80px`, and the second dock's bottom clears y=1340. **Current CSS (lines 155-162) puts the docks 136 px into the right rail and 152 px over width** (49 §49.1). 16:9 rendering is byte-identical after the change.
- Validate: `python -m pytest content/video_engine/tests/test_vertical_safe_box.py -q` and a 9:16 render whose dock bounding boxes all sit inside `x[80,880] y[280,1340]`
- Evidence: 2026-09-04 - measured before: docks 952 wide at x=64, dock-2 y 1180-1780 (under the caption bar), caption at y=1759. After: `.dock` 800px at x=80, dock-1 y 280-794, dock-2 y 806-1320, solo centred at 553; **the anchored caption also moved** into its strip (`#caption.quiet { bottom: 480px }` -> y ~1399), same finding, same block. `test_vertical_safe_box.py` 3/3: static CSS values, rendered rectangles inside the box with no overlap, **16:9 byte-identical**. The golden harness caught the change on exactly one surface (`dock-pair-9x16`) and the 9:16 golden was refreshed deliberately in the same commit; the other three goldens unchanged.

### T1: G-a - a camera move may not overlap an evidence build
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/gate_motion_density.py`, `content/video_engine/tests/test_gate_punch_build_overlap.py`
- Acceptance: a scene whose camera species window intersects a dock build window FAILs; the same timeline with the build starting after the move settles PASSes. Verdict carries `SRC_M14` naming 47 §2 G-a and doc 07 Pillar 4 (saccadic suppression).
- Validate: `python -m pytest content/video_engine/tests/test_gate_punch_build_overlap.py -q`
- Evidence: 2026-09-04 - M14 in `gate_motion_density.py`: a build window is the card's entrance (1.5 s) through its last badge reveal + 0.6 s; any `punch | focus_zoom | pull_back` window intersecting one FAILs, naming scene, move, slide and both windows; `SRC_M14` carries 47 s2 G-a / doc 07 Pillar 4. Five tests: window arithmetic, punch on the entrance FAILs, on a badge FAILs, after the settle PASSes, the evidence-dock.json shape is read too. Ep1: M14 PASS (it carries no species rows); the wiring baseline gains the row (4 PASS).

### T2: G-b, G-c, G-e - the comfy/parallax config gate
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/gate_comfy_config.py`, `content/video_engine/tests/test_gate_comfy_config.py`
- Acceptance: FAILs on the current `parallax-runner.mjs` naming all five defects (`tiling_mode`, `ssaa`, `quality`, `intensity`, model); FAILs `num_frames` not `8n+1`; FAILs a parallax job whose plate kind is `actor`/`prop`/`evidence` or that carries text, per the 45 §45.2 matrix. Reads only - never edits the runner.
- Validate: `python content/video_engine/scripts/gate_comfy_config.py tools/google-flow-driver/src/parallax-runner.mjs` (expect FAIL, 5 findings) then `python -m pytest content/video_engine/tests/test_gate_comfy_config.py -q`
- Evidence: 2026-09-04 - run on the runner as shipped: `VERDICT: FAIL (5 findings)` naming intensity (6 presets at 1.0), tiling_mode mirror, ssaa 1.0, quality 75, vits model, each with its ruling. The shipped dials are a fixture in `test_gate_comfy_config.py` so the gate keeps proving it catches them; frame laws (Wan 4k+1 / LTX 8n+1), CFG <= 4.5, unscaled FP8 encoder, quantized Wan VAE and the plate-kind matrix each have a passing and a failing case. 4 passed. Also carries G-m/G-n from T8's brief, since they are the same reader.

### T3: G-d - unanchored transform lint
- Status: complete
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/scripts/lint_template_transforms.py`, `content/video_engine/tests/test_lint_template_transforms.py`
- Acceptance: reports every `scale(`/`rotate(` applied without an explicit `transformOrigin` or anchor, as **INFO** on first landing (M08 ladder). A synthetic fixture with one anchored and one unanchored transform reports exactly one.
- Validate: `python content/video_engine/scripts/lint_template_transforms.py docs/content-video-engine/samples/scene-evidence-player.template.html`
- Evidence: 2026-09-04 - INFO ladder. CSS reader (a state rule inherits its base selector's origin) + JS reader (the origin must be set on the same receiver within 40 lines, or the element's CSS anchors it). Fixture: one anchored, one loose in each reader -> exactly one finding each. **First landing on the template: 11 unanchored transforms** - `.lp-ink .g` rotate, `.pill`/`.pill.on` scale, the story-bar `scaleY` builds (1798/1864), badge pop 1887, plate-life `rotate` 2024, the camera `scale` 2066, caption words 2237/2241/2253. That list is P38's anchor work; promoting to FAIL waits on it.

### T4: G-g - G15 closes on the mechanism, not the token
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/gate_opening_structure.py`, `content/video_engine/tests/test_gate_ring_mechanism.py`
- Acceptance: G15 keeps its existing token check and adds a mechanism check - the causal claim named in P1 recurs in the close. A script that echoes a P1 *phrase* while the argument has drifted FAILs the new half and PASSes the old. **Human gate: operator decides grandfathering before merge.**
- Validate: `python -m pytest content/video_engine/tests/test_gate_ring_mechanism.py -q` then `python content/video_engine/scripts/run_script_gates.py <ep1 script>` to confirm no unintended regression
- Evidence: 2026-09-04 - G15b in `gate_opening_structure.py`: the P1 sentence carrying the token yields its content stems (token and stopwords removed, `ring_claim_stems`); the last 12% of the runtime is the close; the token sentence there is read with its two neighbours; PASS at >= 2 shared stems. Landed as WARN behind the human gate; **operator ruling 2026-09-04: no grandfathering, FAIL from here** - both scripts are being rewritten, so the rewrite is held to the ring-closes-on-the-mechanism bar from its first draft. `RING_MECHANISM_LEVEL = "FAIL"`. Tests: return-of-the-argument PASSes both halves; token echo with a drifted argument PASSes G15 and WARNs G15b; token absent from the close is named. Opening-structure suite still green. **Ep1 as shipped: G15 PASS, G15b WARN - the P1 sentence that plants `spike` has one content stem (`iron`), so there is no claim for the close to return to.** That is a rewrite note, not a gate defect: the ring must be planted inside the claim.

### T5: V-a - the muted-caption judge
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/judge_muted_caption.py`, `content/video_engine/tests/test_judge_muted_caption.py`
- Acceptance: given a prior scene (captions on) and a test scene (captions off), returns PASS/FAIL **and a diagnosis** - `scenery` when the model can only describe the frame, `over-dense` when it cannot resolve the claim at all. Ships as a CLI, **not wired to any build**. Tests use recorded model responses, no live call.
- Validate: `python -m pytest content/video_engine/tests/test_judge_muted_caption.py -q`
- Evidence: 2026-09-04 - `judge_muted_caption.py`: CLI, unwired. **Corrected on the operator's ruling the same day: no API call - the judge is the Codex CLI, driven exactly as the viewer is (`viewer_run.find_codex` / `call_codex`, headless `--approve-for-me`, images first because `-i` is variadic), and ONE run judges the whole manifest** - every prior/test pair attached in order, one JSON array back. The verdict stays code: `scenery` when the judge can only describe, `over-dense` when confidence < 0.6 or the read shares < 2 terms with the claim. Tests pin the verdicts, the prompt's image order, the command shape and the replay CLI (manifest -> report JSON, exit 1 on any FAIL). Cadence remains the operator's.

### T9: apply the parallax dials - every current value is wrong
- Status: complete
- Owner: parent
- Depends on: none (but see the human gate - the file has uncommitted concurrent work)
- Write set: `tools/google-flow-driver/src/parallax-runner.mjs`
- Acceptance: `intensity` clamped to `0.10-0.12` in all six presets (resolved from the node source, 45 §45.4 - `strength` is inert without a `feature`), `tiling_mode: "none"` with a 1.10x pre-zoom crop, `ssaa: 2.0`, `quality: 85`, model `depth_anything_v2_vitl` (precision per X6). One test roll on a landscape plate shows no kaleidoscope ceiling and no rubber-sheet tearing.
- Validate: `python content/video_engine/scripts/gate_comfy_config.py tools/google-flow-driver/src/parallax-runner.mjs` (expect PASS after; it FAILed with 5 findings before)
- Evidence: 2026-09-04 - applied on top of the runner's uncommitted concurrent work (E30: unowned code is corrected, not planned around): `intensity` is a named parameter defaulting to 0.11 in all six presets, `strength` annotated inert, `steady_value` 0.40, model `depth_anything_v2_vitl_fp16` (precision per X6), `quality` 85, `ssaa` 2.0, `tiling_mode` none, and the 1.10x crop implemented as `ImageScaleBy` -> `ImageCrop` on the Depthflow frames back to the plate's own size (read from the PNG/JPEG header by `imageSize()`; the crop hides the bare border that tiling none leaves). Gate: `VERDICT: PASS (0 findings)`; `node --check` clean. **Test roll done** (ComfyUI 0.34.2, all seven node types present, `vitl_fp16` in the model list): `world-banker-apartment-v2` 1536x1024 through the dolly preset, 30 frames -> 1536x1024 x 30 back at the plate's size. Measured: first-vs-last mean delta 1.2 (the move is real and restrained), **0 dark pixels on every 8px edge strip** (the crop covers the reveal that tiling none leaves), top-band mirror similarity 134 (a kaleidoscope reads ~0). No tearing by eye on frames 0/15/29. Clip in the session's scratchpad `parallax-t9-dolly.mp4`; X6 (fp16 vs fp32 depth) stays open - the fp16 boundaries looked clean on this plate.

### T8: G-l, G-m, G-n - the vertical and generative gates
- Status: complete
- Owner: parent
- Depends on: T0
- Write set: `content/video_engine/scripts/gate_vertical_safe_box.py`, `content/video_engine/tests/test_gate_vertical_safe_box.py`, and additions to `gate_comfy_config.py`
- Acceptance: **G-l** FAILs any 9:16 element outside `x[80,880] y[280,1340]` — and must FAIL the pre-T0 template as its fixture, which is the strongest evidence in this PRP. **G-m** FAILs a Wan job not on `4k+1` or an LTX job not on `8n+1`. **G-n** FAILs Wan I2V CFG > 4.5, LTX CFG > 4.5, an unscaled FP8 text encoder, or a quantized Wan VAE (49 §49.2-49.3).
- Validate: `python -m pytest content/video_engine/tests/test_gate_vertical_safe_box.py -q`
- Evidence: 2026-09-04 - `gate_vertical_safe_box.py` reads the template's 9:16 CSS (dock width/left/top, height derived at 514/800 per px of width, caption bottom) and judges rendered rectangles by the same rule. **It FAILs the pre-T0 CSS verbatim** (`#dock-1`/`#dock-2` x 64-1016 into the rail, dock-2 y past 1340, no 9:16 caption rule -> bottom dead zone) and PASSes the template now. G-m/G-n landed in T2's `gate_comfy_config.py` (same reader). 3 tests.

### T7: G-i, G-j, G-k - the grounding gates
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/gate_grounding.py`, `content/video_engine/tests/test_gate_grounding.py`
- Acceptance: **G-i** FAILs a shot whose composited figure's eye height misses the plate's declared horizon beyond tolerance (48 §48.7 defect 4 - the "standing in a pit" read). **G-j** FAILs a grounded sprite not anchored `transform-origin: 50% 100%` or bound to an independent screen-space tween rather than floor velocity. **G-k** FAILs a beat that declares contact without declaring a solver, per the FK/IK boundary (48 §48.1). Each needs the shot table to carry a horizon and a contact declaration - if it does not yet, land on the **M08 INFO-then-FAIL ladder** rather than blocking.
- Validate: `python -m pytest content/video_engine/tests/test_gate_grounding.py -q`
- Evidence: 2026-09-04 - `gate_grounding.py` on the INFO-then-FAIL ladder: G-i reads `world.horizon` + cutout `eye_y` (tolerance 0.04), G-j reads the template's `#plife img` anchor (`50% 100%`, present today) and any cutout `tween: screen`, G-k requires `solver: fk|ik` on a beat declaring `contact`. INFO while a timeline declares nothing, FAIL on a wrong declaration, PASS on a right one - each state tested. Ep1: G-i INFO, G-j PASS, G-k INFO - the shot table carries no horizon or contact yet, as the brief predicted.

### T6: status the 47 rows and register the gates
- Status: complete
- Owner: parent
- Depends on: T0, T1, T2, T3, T4, T5, T7, T8, T9
- Write set: `docs/content-video-engine/47-FINDINGS-TO-CHECKS.md`, `docs/content-video-engine/CAPABILITIES.md`, `content/video_engine/scripts/run_script_gates.py`
- Acceptance: every shipped check's row names its script and reads *shipped*; CAPABILITIES records the new capability in the same commit (its own recall rule); G-g is registered in the composed runner. Deferred items (M13, E1, G-h) keep their blocking reason.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P37-RESEARCH-ENFORCEMENT-LAYER.plan.md`
- Evidence: 2026-09-04 - 47 §5b tables every row with its script, state and the failing case shown; the scoreboard line updated; BACKLOG's Tier-2 table headed with the shipped/open split; CAPABILITIES gains "The enforcement layer" (seven rows). G15b needs no registration - it lives inside the gate the composed runner already calls. Deferred with reasons: G-h (44 ink), G-o (X0), M13 (P40 T1).

## Verification

```powershell
python -m pytest content/video_engine/tests/ -q -k "gate_punch or comfy_config or template_transforms or ring_mechanism or muted_caption or grounding or vertical_safe_box"
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
