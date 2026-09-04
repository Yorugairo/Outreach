---
id: P39-RENDER-BASELINE-AND-KILL-SWITCH
title: Freeze the shippable player, catch regressions mechanically, and give every new capability an off switch
status: draft
operation: chore
risk: standard
owner: parent
branch: main
created: 2026-09-04
updated: 2026-09-04
---

# Render Baseline And Kill Switch

## Summary

**Prerequisite for P37 and P38.** Written in response to the operator, 2026-09-04:

> *"We're adding a LOT of complexity, and moving pieces. Especially as a non-animator,
> non-mathematician. Everything we're adding now is well beyond my realm of expertise, so
> if it goes wrong, I'm afraid I won't be the best troubleshooter."*

That is the correct concern and the plans did not answer it. Verified today:

- **No golden-frame or visual-regression test exists** for the player.
- **No git tag** marks a known-good template.
- P38's T2 changes how **every drawn object in the engine** looks, and P37's T0 edits the
  template before any of that protection exists.

The current player produces a shippable product. Nothing should be able to take that away
silently, and **the operator should never be the troubleshooter for animation math.** The
system's job is to say what broke and offer a switch.

## Intent And Acceptance

**Intent.** Make the current player a frozen, restorable, mechanically-verified baseline,
and require every capability that changes rendered output to ship behind a flag that
defaults to the old behaviour.

**Acceptance:**

1. A git tag marks the last known-good template, and `docs` records the one command that
   restores it.
2. `render_episode.py` produces byte-identical frames across two runs of the same
   timeline — determinism proven, not assumed (the template seeds in 33 places).
3. A committed set of golden frames covers the surfaces at risk: a ledger page mid-build,
   a chart with a callout, a 16:9 dock pair, a 9:16 dock pair.
4. A test re-renders those frames and fails on **any** pixel difference, naming the frame
   and writing a side-by-side diff image.
5. Every capability in P38 that alters rendered output reads a flag from the timeline,
   **defaulting to current behaviour**. Turning the flag off restores the old render
   exactly — proven by the golden frames passing with flags off.
6. A one-page runbook tells the operator, in plain terms: how to see what changed, how to
   turn a capability off, and how to get back to the tagged baseline.

**Anti-goals.** No judgment calls in the regression check — a pixel diff is mechanical, so
it never asks the operator whether something "looks right." No flag that defaults to the
new behaviour. No golden frame whose source timeline is not committed alongside it.

## Scope

`content/video_engine/tests/golden/` (new), `content/video_engine/scripts/render_baseline.py`,
a flag read in `scene-evidence-player.template.html`, and one runbook page.

## Not Building

- **A visual-diff *review* tool.** The check is pass/fail on pixels. Perceptual diffing is
  a rabbit hole and the operator should not be reading heatmaps.
- **Golden frames for every scene.** Four surfaces, chosen because they are what P37 and
  P38 actually touch. Breadth here costs render time on every test run.
- **Rollback automation.** A tag plus a documented `git checkout` is enough; scripted
  rollback is a thing that can itself break.

## Human Gates

| gate | why |
|---|---|
| **T2 golden-frame selection** | The operator picks the four surfaces, because they are the four they would notice being wrong. This is the one judgment in the PRP and it belongs to them. |

## Mandatory Reads

- [`docs/runbooks/PRP_EXECUTION.md`](../../../docs/runbooks/PRP_EXECUTION.md)
- `content/video_engine/scripts/render_episode.py` - the existing headless chromium path
- `content/video_engine/tests/test_production_console_snapshot.py` - the nearest existing snapshot pattern
- [`47-FINDINGS-TO-CHECKS.md`](../../../docs/content-video-engine/47-FINDINGS-TO-CHECKS.md) §1 - the six capabilities that will each need a flag

`backend-patterns` / `frontend-patterns` not routed: test tooling and one template flag.

## Execution Path

| slice | route | why |
|---|---|---|
| T1 | `speedster` | a tag and a doc line |
| T2 | **parent** | determinism has to be proven before anything is built on it |
| T3 | `implementation_luna` | bounded harness work |
| T4 | **parent** | the flag contract shapes how P38 is written |
| T5 | `junior_developer` | one runbook page |

## Patterns To Mirror

- **`test_production_console_snapshot.py`** - the repo's existing snapshot idiom; match its
  naming and its failure output rather than inventing a second style.
- **`gate_motion_density.py`'s `Gate` dataclass** - a failure names the artifact and the
  rule. A golden-frame failure names the frame and the diff path.
- **M08's INFO-then-FAIL ladder** - if determinism proves flaky in T2, the harness lands as
  INFO with the variance reported, rather than blocking on a flapping test.

## Task Slices

### T1: tag the known-good state
- Status: pending
- Owner: speedster
- Depends on: none
- Write set: git tag, `docs/content-video-engine/CAPABILITIES.md`
- Acceptance: an annotated tag (`player-baseline-2026-09-04`) on the current template commit, and one line in CAPABILITIES giving the exact restore command. **This alone removes the worst case** - it makes "get back to what worked" a single command rather than an archaeology exercise.
- Validate: `git tag -l player-baseline-*` and the documented command restores the file byte-identically
- Evidence: pending

### T2: prove the render is deterministic
- Status: pending
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/scripts/render_baseline.py`, `content/video_engine/tests/test_render_determinism.py`
- Acceptance: the same timeline rendered twice through `render_episode.py` yields byte-identical frames. The template seeds in 33 places, so this **should** hold - but golden frames are worthless if it does not, so it is proven before anything depends on it. If it does not hold, this slice's real output is the list of what is non-deterministic.
- Validate: `python -m pytest content/video_engine/tests/test_render_determinism.py -q`
- Evidence: pending

### T3: the golden-frame harness
- Status: pending
- Owner: implementation_luna
- Depends on: T2
- Write set: `content/video_engine/tests/golden/` (frames + their source timelines), `content/video_engine/tests/test_golden_frames.py`
- Acceptance: four committed surfaces - a ledger page mid-build, a chart carrying a callout, a 16:9 dock pair, a 9:16 dock pair - each with its source timeline committed beside it. The test re-renders and fails on any pixel difference, **naming the frame and writing a side-by-side diff PNG** so the failure is legible without reading code.
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py -q`, then perturb one CSS value and confirm it FAILs and names that surface
- Evidence: pending

### T4: the flag contract
- Status: pending
- Owner: parent
- Depends on: T3
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html`, `content/video_engine/tests/test_kinetics_flags.py`
- Acceptance: the template reads `timeline.kinetics` - a map of capability name to boolean - **defaulting every one to `false`, meaning current behaviour**. With all flags off the golden frames pass unchanged. **P38 is amended so each of its capabilities ships behind its flag.** This is the piece that means a bad result is one field away from the old render instead of a debugging session.
- Validate: `python -m pytest content/video_engine/tests/test_kinetics_flags.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T5: the runbook
- Status: pending
- Owner: junior_developer
- Depends on: T4
- Write set: `docs/runbooks/RENDER-REGRESSION.md`
- Acceptance: one page, no jargon, answering three questions - *what changed and where do I see it*, *how do I turn a capability off*, *how do I get back to the baseline*. Written for someone who does not read the animation math and should not have to. Names the exact commands.
- Validate: a reader who has not seen this PRP can restore the baseline from the runbook alone
- Evidence: pending

## Verification

```powershell
python -m pytest content/video_engine/tests/test_render_determinism.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_flags.py -q
git tag -l player-baseline-*
python scripts/prp_validate.py .claude/PRPs/plans/P39-RENDER-BASELINE-AND-KILL-SWITCH.plan.md
```

**The harness is proven by breaking it.** T3 is not accepted until a deliberate one-value
CSS change has been shown to FAIL it by name - the same discipline the research-extraction
gate was held to.

## Evidence And Handoff

- T1: the tag, and a demonstrated restore.
- T3: the FAIL output from the deliberate perturbation, with its diff image.
- T4: golden frames passing with all flags off - the proof that new capability is opt-in.
- **P37 and P38 both gain a dependency on this plan**, and P38's slices are amended to
  ship behind flags. Neither should start first.
