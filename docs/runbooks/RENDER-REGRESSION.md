# When a render looks wrong

Status: current
Last reviewed: 2026-09-04 (P39 T5)

You do not need to read any animation math to use this page. Three questions, three
commands. Run everything from the repository root.

## 1. What changed, and where do I see it?

```bash
python content/video_engine/scripts/render_baseline.py --check
```

- `PASS 4 golden frames identical` — the player draws exactly what it drew when the
  baseline was approved. Whatever you are looking at is not a renderer regression; look at
  the episode's timeline, its assets, or the audio instead.
- One line per changed surface, like `dock-pair-9x16: pixels changed - see
  content/video_engine/tests/golden/diffs/dock-pair-9x16.diff.png` — open that PNG. It
  is three panels: **GOLDEN** (approved), **ACTUAL** (now), **DIFF ×8** (every changed
  pixel, brightened). Bright dots show you exactly what moved.

The four surfaces are the ones the new work touches: a ledger page mid-build, a chart
with a callout, a 16:9 dock pair, a 9:16 dock pair.

## 2. How do I turn a capability off?

Every new drawing capability reads a flag from the episode's timeline and is **off unless
the timeline says otherwise**. In `<episode>/build-f/<episode>.timeline.json` (or the
timeline the build writes), add or edit:

```json
"kinetics": {
  "curvature_stroke": false,
  "analytic_spring":  false,
  "area_squash":      false,
  "arap_morph":       false,
  "dqs_skinning":     false,
  "prop_attach":      false
}
```

Set the suspect one to `false` and rebuild the player. If you are not sure which, set all
six to `false` — that is exactly the approved baseline. A name that is not in this list is
ignored (the player logs `kinetics: unknown flag ignored`), so a typo cannot switch
anything on.

| flag | what it changes |
|---|---|
| `curvature_stroke` | how a line is drawn on: slows in the corners, speeds on the straights |
| `analytic_spring` | how things settle after they move |
| `area_squash` | the squash-and-stretch on a landing |
| `arap_morph` | how one shape becomes another |
| `dqs_skinning` | how a figure's joints bend |
| `prop_attach` | how a held prop follows a hand |

## 3. How do I get back to the baseline?

The last approved player is tagged. One command restores its file exactly:

```bash
git checkout player-baseline-2026-09-04 -- docs/content-video-engine/samples/scene-evidence-player.template.html
```

Then rebuild the episode's player (the build copies the template) and render. To confirm
you are on the baseline:

```bash
python content/video_engine/scripts/render_baseline.py --check
```

It must say `PASS`. If it does not, the golden frames themselves were refreshed after the
tag — `git log --oneline -- content/video_engine/tests/golden/frames` shows when and why.

## If you approved a change and want it to become the new baseline

```bash
python content/video_engine/scripts/render_baseline.py --update
git add content/video_engine/tests/golden/frames
git commit -m "chore(golden): refresh after <what you approved>"
git tag -a player-baseline-<date> -m "<what you approved>"
```

Refreshing is a decision, never a reflex: `--check` failing is the harness doing its job.

## What the harness cannot see

It renders four synthetic surfaces from committed sources, at native size, with wall-clock
effects switched off. It does not render your episode. A regression that lives only in an
episode's timeline, its assets, its audio, or the encoder is outside it — for those, the
motion gate (`build-f/GATES-MOTION.md`) and the review contact sheet still apply.
