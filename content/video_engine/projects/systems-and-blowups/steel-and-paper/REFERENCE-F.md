# REFERENCE F - episode one as it shipped (FROZEN; never compiled again)

The operator, 2026-09-22: "should we have the original build-f saved isolated along with the version we are
modernizing?" - yes. Steel and Paper H (`build-h/`, `build_episode_h.py`) is the modernization; THIS is what
it is read beside, and a reference is only worth anything if it does not move.

## What the original is

| part | where | pinned by |
|---|---|---|
| the full cut, 806.472 s, 2560x1440 @ 30 fps | `build-f/render/steel-and-paper-full-1440p.mp4` (rendered 2026-09-01, gitignored, 906 MB) | sha256 `9a27de1c3d675547d98616e7e6878291f20c5755325db3787123c6d541680dd3` |
| the compiled timeline | `build-f/steel-and-paper.timeline.json` | git blob `df21da93182f` at `bd2a000` (last written by `fce7a8f`) |
| the words timeline | `build-f/timeline.json` | git blob `f41278cc16b6` at `bd2a000` |
| the gate report | `build-f/GATES-MOTION.md` | git blob `9b48b5acfd1b` at `bd2a000` |
| the review sheet | `build-f/frames-review.png` | on disk |

**The render is the reference, not the player.** `build-f/player.html` is gitignored and was REBUILT in place on
2026-09-18 20:58, so the original interactive player no longer exists anywhere. Read the original on the mp4.

## What happened to `build-f/` (measured 2026-09-22, read-only)

In the MAIN checkout, `build-f/` was recompiled in place on 2026-09-18 20:58 - episode one's table through
that day's compiler (R26-225: a gate test that could write a build dir). Against the committed original, the
recompiled timeline carries 233 differences: 75 scene camera moves ADDED, 67 exits changed (35 `cut` and 32
`wipe_right` became `dip`), dock ids and caption bands added, a kinetics block added, four sound envelopes
added. A 15-second render (`build-f/render/*-0-15*`, `part-0*.mp4`, 2026-09-20) was made from that
recompile. None of it is the original, and none of it is H - it is neither the reference nor the
modernization.

The goldens that moved this month are a different thing: test pictures of the engine, re-rendered on purpose
in the commit that built each capability. `build-f` is the opposite kind of file - its whole value is that it
does not change.

## The rule

- Nothing compiles into `build-f/`. A build that wants episode one's table on today's engine writes its own
  dir (`build-f-modern/` or similar), never this one.
- Restoring the two committed files in the main checkout (`git checkout bd2a000 -- build-f/steel-and-paper.timeline.json build-f/GATES-MOTION.md`)
  waits for the operator's word: that checkout carries another lane's live, uncommitted work.
- Before any comparison is read, the render's sha256 is checked against the one above.
