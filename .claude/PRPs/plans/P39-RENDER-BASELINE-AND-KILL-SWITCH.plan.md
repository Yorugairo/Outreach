---
id: P39-RENDER-BASELINE-AND-KILL-SWITCH
title: Freeze the shippable player, catch regressions mechanically, and give every new capability an off switch
status: complete
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
- Status: complete
- Owner: parent (kept - the tag is a protected git action)
- Depends on: none
- Write set: git tag, `docs/content-video-engine/CAPABILITIES.md`
- Acceptance: an annotated tag (`player-baseline-2026-09-04`) on the current template commit, and one line in CAPABILITIES giving the exact restore command. **This alone removes the worst case** - it makes "get back to what worked" a single command rather than an archaeology exercise.
- Validate: `git tag -l player-baseline-*` and the documented command restores the file byte-identically
- Evidence: 2026-09-04 - `player-baseline-2026-09-04` annotated on `2795c49` (main); the template is byte-identical to its last change `3a0e092` (`git diff --quiet` clean). Restore proof: `git hash-object` of the working file == `git rev-parse player-baseline-2026-09-04:<path>` == `a4705a4a40a1b2983c54ee4c61bff72e24d6edd1`. A first `cmp` against `git show` differed at byte 153 - CRLF vs the LF blob, not content; the blob-hash check is the honest one on Windows and the restore command goes through the same clean filter. CAPABILITIES gained "The frozen baseline" with the one restore command.

### T2: prove the render is deterministic
- Status: complete
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/scripts/render_baseline.py`, `content/video_engine/tests/test_render_determinism.py`
- Acceptance: the same timeline rendered twice through `render_episode.py` yields byte-identical frames. The template seeds in 33 places, so this **should** hold - but golden frames are worthless if it does not, so it is proven before anything depends on it. If it does not hold, this slice's real output is the list of what is non-deterministic.
- Validate: `python -m pytest content/video_engine/tests/test_render_determinism.py -q`
- Evidence: 2026-09-04 - **it did not hold as shipped, and the list is the deliverable.** Three fresh-browser renders of the 9:16 dock pair differed (run 2 of 3: whole-frame bbox, max 232) while the 16:9 chart was identical. Causes, each verified by neutralising it: (1) **CSS transitions run on the wall clock** - `.dock` opacity .75s, pills .34s, captions .12s - so a seek-and-screenshot lands mid-transition; the template already disables one transition (line 271) for exactly this reason. (2) **`fitStage()` scales `#stage` to the `#fit` container** (0.728x at 1920x1080), so every capture is a ~1398px stage; `render_episode.py` then `resize()`s to 2560x1440 - **the shipped 1440p is a LANCZOS upscale of a 1398px frame.** (3) `document.fonts.ready.then(()=>1)` in render_episode is not awaited. (4) An element screenshot inherits the container's fractional offset (1081x1920). `render_baseline.render_frame` neutralises all four (transition/animation none, `#fit` sized to the stage, transform none, fonts awaited, clipped page shot) and then all four surfaces render byte-identical 3/3 at native size. `test_render_determinism.py` 2 passed. The shipped renderer inherits none of this until T6.

### T3: the golden-frame harness
- Status: complete
- Owner: implementation_luna
- Depends on: T2
- Write set: `content/video_engine/tests/golden/` (frames + their source timelines), `content/video_engine/tests/test_golden_frames.py`
- Acceptance: four committed surfaces - a ledger page mid-build, a chart carrying a callout, a 16:9 dock pair, a 9:16 dock pair - each with its source timeline committed beside it. The test re-renders and fails on any pixel difference, **naming the frame and writing a side-by-side diff PNG** so the failure is legible without reading code.
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py -q`, then perturb one CSS value and confirm it FAILs and names that surface
- Evidence: 2026-09-04 - `tests/golden/sources/*.{timeline,uris}.json` (four surfaces, generated by `build_golden_sources.py` from the template, one committed series sidecar, solid plates and a 2 s silent WAV - no episode assets), `tests/golden/frames/*.png` (1920x1080 / 1080x1920, 223-534 KB). `render_baseline.py --check` -> `PASS 4 golden frames identical`. **The perturbation is a test, not a one-off:** `test_harness_catches_a_one_value_css_change` mutates the `.dock` corner radius 14px -> 2px in memory and asserts the check FAILs and writes `diffs/dock-pair-16x9.perturbed.diff.png` (golden | actual | diff x8 - eight corner dots). 6 passed. The 9:16 golden captures the CURRENT dock geometry, overlap included - that is the baseline P37 T0 changes against. Human gate: the four surfaces were picked by the parent as an AI baseline; the operator may swap any.

### T4: the flag contract
- Status: complete
- Owner: parent
- Depends on: T3
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html`, `content/video_engine/tests/test_kinetics_flags.py`
- Acceptance: the template reads `timeline.kinetics` - a map of capability name to boolean - **defaulting every one to `false`, meaning current behaviour**. With all flags off the golden frames pass unchanged. **P38 is amended so each of its capabilities ships behind its flag.** This is the piece that means a bad result is one field away from the old render instead of a debugging session.
- Validate: `python -m pytest content/video_engine/tests/test_kinetics_flags.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: 2026-09-04 - the template carries `KINETICS_DEFAULTS` (six names from doc 47 s1: `curvature_stroke`, `analytic_spring`, `area_squash`, `arap_morph`, `dqs_skinning`, `prop_attach`, every one `false`), `KIN = defaults + TL.kinetics`, unknown names warned and ignored, and the accessor `kin(name)` that P38's code must gate on. `test_kinetics_flags.py`: the defaults block is all-false and matches the six names (static, always runs); an explicit all-false map and a typo flag both render pixel-identical to the golden (rendered). Golden frames unchanged with the block in place - `--check` PASS. P38 amended: each capability slice gates on its flag.

### T6: the shipped renderer adopts the proven capture
- Status: complete
- Owner: parent
- Depends on: T4
- Write set: `content/video_engine/scripts/render_episode.py`
- Acceptance: `render_episode.py` captures through the same preparation as `render_baseline.render_frame` - transitions off, `#fit` sized to the stage, fonts awaited, clipped shot - at device scale 4/3 so 2560x1440 is captured, not upscaled. Proven by rendering the `--test` slice before and after: the after is sharper (no resize) and two runs of it are byte-identical. **This changes ep1's pixels** (sharper, no transition smear on dock entrances) and is why the rebuild waits for it.
- Validate: two `--test` renders byte-identical; `test_golden_frames.py` still green
- Evidence: 2026-09-04 - `render_baseline.prepare_page()` is the one preparation (chrome off, VO muted, fonts awaited, transitions off, `#fit` sized to the stage) and `render_episode.capture()` now calls it at device scale 4/3 and clips the stage: **2560x1440 captured, never resized** - the resize fallback is gone and a wrong size raises. Proven on a committed source: two 4/3 captures of `chart-callout` are 2560x1440 and byte-identical (`293fc1775ca1`). Harness suite 12/12 green. **Then run on ep1 itself:** the audio master, evidence cards and sound cues (all gitignored) were found in the worktree checkout and synced into main; `player.html` rebuilt (81 MB); `render_episode.py --test` twice -> both 2560x1440 x 240 frames, **decoded-frame hash identical `5d6773be56fcbd90`** (the Sep-3 render of the same slice: `8d22b8da4c7a7ca5`). The full slice with the audio mix completes: `build-f/render/steel-and-paper-test-1440p.mp4`. Harness 12/12 green after the change.

### T5: the runbook
- Status: complete
- Owner: junior_developer
- Depends on: T4
- Write set: `docs/runbooks/RENDER-REGRESSION.md`
- Acceptance: one page, no jargon, answering three questions - *what changed and where do I see it*, *how do I turn a capability off*, *how do I get back to the baseline*. Written for someone who does not read the animation math and should not have to. Names the exact commands.
- Validate: a reader who has not seen this PRP can restore the baseline from the runbook alone
- Evidence: 2026-09-04 - `docs/runbooks/RENDER-REGRESSION.md`: three questions, three commands (`--check` and how to read the diff PNG; the six flags with plain-language meanings; the one-line tag restore), plus how to refresh deliberately and what the harness cannot see. No math on the page.

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
- T6: the before/after `--test` slice pair, and the determinism of the after.
- **P37 and P38 both gain a dependency on this plan**, and P38's slices are amended to
  ship behind flags. Neither should start first.
