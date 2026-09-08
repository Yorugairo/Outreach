# The recall receipt — recall before you build

Operator, 2026-09-08, after a day in which the wipe's retirement (E47), the throw-then-snap (the third
watch, P47 T7) and the camera (doc 16 §4, brief C3, doc 43, HyperFrames Rule 2, D1, doc 24) were each
re-derived while the record held them: *"how come you just now found all of that research/doc
information? The whole point of making this information retrieval cheap and easy was to get you to
use it. How do we gate for that or make it part of your standardized processes?"*

The failure is at the moment of **proposing**, not answering. "Do we have X?" already triggered recall;
"let's build X" did not. This page is the gate.

## 1. The triggers

Any of these opens a recall before anything else is said or built:

- **"let's build / add / try / what if we …"** — a proposal of a mechanism: a transition, an arrival,
  a camera move, a chart form, a species, a kinetics law, a sound cue, a plate prompt, a design rule.
- **"try"** — an attempt IS a proposal; the receipt comes before the attempt, not after it fails.
- **"iterate"** — every round of an iteration re-checks the record for the thing being iterated; the
  second round is not exempt because the first one recalled.
- **"review the docs"** — literal: the order in §3, quoted back with `path:line`, before any opinion.

## 2. The receipt

The proposal (and the commit that lands it) opens with `Recall:` lines — one per hit — before the
proposal itself:

```
Recall: docs/portable/OPERATOR-RULINGS.md:1411  (E47 - the wipe is retired as the world-change default)
Recall: docs/content-video-engine/16-EDITORIAL-MOTION-SYSTEM.md:59  (a moving shot names a focal point, amount, phases)
Recall: docs_find 0 hits for "camera arrival"
```

`docs_find 0 hits for <term>` is a valid receipt; silence is not. A commit that touches the player
template, `content/video_engine/scripts/kinetics/`, `build_scene_timeline_f.py`, `gate_motion_density.py`
or a short's `build_short.py` without a `Recall:` line is refused by `scripts/hooks/recall_receipt.py`.

**Installed 2026-09-08** (operator: "install the hooks") in `.git/hooks/commit-msg`, which the main checkout and every worktree share; the script resolves from the main checkout so a worktree on an older branch is gated too. Hooks are local to a clone - a fresh clone re-runs:

```bash
printf '#!/bin/sh\npython scripts/hooks/recall_receipt.py "$1"\n' > .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg
```

## 3. The order — cheapest first; stop at the first layer that answers

1. `python content/video_engine/scripts/docs_find.py "<noun>"` — one line per hit, cheapest layer first.
2. `docs/portable/OPERATOR-RULINGS.md` — overrides everything (E47/E48 transitions, E50–E53 charts, E39 the
   style atom) — and the review docs it points to (e.g. `TRANSITIONS-REVIEW-2026-09-06.md`).
3. `docs/content-video-engine/CAPABILITIES.md`, `docs/ANIMATION-REGISTRY.md`, `docs/GATES-REGISTRY.md`,
   `docs/CRAFT-MAP.md` — what is built, every dial and law with its status, every gate, every device.
4. The research bundle (`content/video_engine/sources/reference_analyses/`, the briefs) and
   `docs/research/*/…_BLUEPRINT.md`.
5. A Gemini research **WORK-ORDER over the bridge** — scoped as a **question**, never a design. Its answer
   is quarantined until the operator approves it, and integrating it is this same rule again.

Never say "we don't have it" before step 1. Never reach step 5 before step 4. My recollection and the
code in front of me are not sources: a hit outranks what I remember; if the operator's memory disagrees
with the record, show the `path:line` and let them rule (E39 was amended that way, 2026-09-08).

## 4. Inspect AND measure

No visual or audio artifact is delivered, and no "fixed" is said, until both:

- **the frames** — rendered at the instants that matter and read as a viewer
  (`render_baseline.serve` + `frame_png` on the built player; the scratch `beat_frames.py` pattern);
- **the geometry** — element rectangles, transforms, luminance, shas — read in the pane
  (`javascript_tool` on the served player) or by script at the same instants.

A frame is a picture; most defects are geometry. "Cut off" was a page 2969 px tall in a 2485 px stage
(the motion squash), found by rects after four rounds of looking. When the operator says *cut off*, *too
fast*, *wrong*, the first move is to measure the element at that instant, not to turn a dial.

## 5. When the record is silent

Say so in the receipt; propose the smallest **opt-in** that leaves the goldens byte-identical
(`test_golden_frames.py`); and when the operator rules, write the ruling into `OPERATOR-RULINGS.md` with
their words in the same commit — so the next session finds it at step 1. A failed approach gets its
failure written down before moving on (what was tried, why it failed), in the same commit.

## 6. Cheap candidates first

For a subjective media edit — a plate, a look, a motion — generate two or three cheap preview candidates
before committing to one; image generation is cheap, a re-roll is a new order file, the operator picks.
