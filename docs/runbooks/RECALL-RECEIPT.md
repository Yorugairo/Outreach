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

**Installed 2026-09-08** (operator: "install the hooks") in `.git/hooks/commit-msg`, which the main checkout and every worktree share; the script resolves from the main checkout so a worktree on an older branch is gated too. Hooks are local to a clone - a fresh clone re-runs: (a WORKTREE shares them and needs nothing; P62: the number a ruling takes is claimed in `docs/WORKTREE-REGISTER.md` before it is written, and `test_worktree_register.py` fails the merge on a duplicate)

```bash
printf '#!/bin/sh\npython scripts/hooks/recall_receipt.py "$1"\n' > .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg
```

**Why a receipt and not an instruction.** An instruction degrades over a long session: the manifest-grep
rule already existed when E47 was re-derived twenty hours in (2026-09-08, LEDGER `eaff6ce7dcf0`). The
receipt is a visible artifact and the hook refuses its absence, so it cannot fade the same way. It still
proves only that the look happened, not that it came before the build (`9cdf34cb04b1`) - the order in §3
stays a discipline.

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

The layers in step 1 and step 3 are BUILD OUTPUT (gitignored since P63 T4, 2026-09-16; `docs_find.py` rebuilds a stale one by
input digest before it reads, so a receipt is always current): `build_docs_layers.py --write` is only a full pass after an
engine or doctrine lane settles - never while `scene-evidence-engine.mjs` is mid-edit (the animation registry reads
the engine), and never inside a slice that does not own the layers (R26-92).

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


## The second receipt, beside this one - test deletions (2026-09-16)

Same shape, same refusal-not-reminder principle, chained into the same `commit-msg` hook: **a commit that
removes a test names it**, or it does not land.

    Tests-removed: <test name> - <why it went>

A removed `def test_*` that still exists somewhere in the staged tree is a move or a rename; the gate lets
it through silently. Only a name that exists NOWHERE after the commit has to be declared.

**What earned it.** An agent rewrote `content/video_engine/tests/test_authoring_kit.py` - a patch took
`t.index(marker)` and sliced to END OF FILE - appended nineteen tests and dropped the file's last ten
(HEAD lines 234-323: the shot table, plate `use` options, the kit's module list, the TR13 gap rules; four
unrelated subjects, one contiguous tail). It was invisible for two reasons worth remembering: the test
COUNT rose, 36 -> 45, so "45 passed" read as success; and a passing suite structurally cannot see a test
that no longer exists. Nothing in the suite noticed. `build_docs_layers.py` did - an effects card named
`test_a_plate_may_name_its_use` as its on-disk proof and the proof had gone, which is the registry
discipline doing the job the tests could not.

**The rule for an agent, before the hook ever fires:** when you rewrite a test file, diff the FUNCTION-NAME
list before and after, never the count.

    git show HEAD:<file> | grep -o "^def test_[a-z0-9_]*" | sort > /tmp/h.txt
    grep -o "^def test_[a-z0-9_]*" <file> | sort > /tmp/n.txt
    comm -23 /tmp/h.txt /tmp/n.txt        # anything printed is lost

Tool: `scripts/hooks/test_deletions.py` (`--message "<msg>" --staged` to check by hand).
Tests: `content/video_engine/tests/test_hook_test_deletions.py`.

## The third receipt, at the compile door - the BUILD receipt (P67, 2026-09-17)

The commit receipt (s2) asks one thing of a mechanism commit: a `Recall:` line naming a record that exists. The BUILD
receipt asks nine things of a cut, and verifies each: the project's `PRODUCTION-LEDGER.md` carries, under its last
`## Recall` heading, `- Recall(<stage>): <path>:<line> "<verbatim span>" (<note>)` lines (or `docs_find 0 hits for
"<term>"`) for every stage of `docs/runbooks/ONE-SHOT.md` step 0 - package, script, voice, world, evidence, motion,
sound, publish, rulings. `content/video_engine/scripts/recall_verify.py <project>` re-reads every cited path and line
and matches the span verbatim on the EXACT line (a one-line window would double the false-accept surface for the
short spans that are easiest to fabricate, and the layers are build output that move by digest - so the strict check
repairs itself instead: "the span moved to `<path>:<N>` - cite that"), refuses a stage with no citation, a span under
12 characters, a path not in the repo, a line past the end, and a zero-hit claim `docs_find.py` answers with a hit;
a legacy `- Recall: <path>:<line> (note)` line is reported UNSTAGED, never dropped. `authoring/table.py`
`compile_timeline` runs it on a build dir's FIRST compile and refuses without a pass; `no_receipt="<reason>"` is the
lab's and the test bed's escape and prints itself into `player.json`'s `compile.recall_receipt`; a recompile of an
existing build carries its block; a build made before P67 is stamped `legacy build (pre-P67)`. The commit hook grew
with it: `build_caption_pages.py` and `authoring/` are mechanisms, `Recall(<stage>):` parses, and a `Recall:` line
that carries a quoted span is checked against its line (a spanless line keeps the path-exists check - older commits
carry none). Why a verifier and not a reminder: "document-level citation may hide unsupported or partially supported
claims" (arXiv 2606.04990) - a text-only receipt was rejected as a fabrication surface (E99 s68, the grill's Q6 A);
the critic (`docs/content-video-engine/CRITIC-REPORT.md`) then scores whether the rows obey the lines cited, claim by
claim, as a second reader. s1-s6 above stand as written; this receipt is the order's proof, not its replacement.
