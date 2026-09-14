# SELF-WATCH - the one-shot bar a cut clears before anybody watches it

The operator's watch begins only when this file is clean. The grill of 2026-09-11: *"we don't come close enough to a
first pass, then we spend a lot of time improving and iterating."* So the bar is a build artifact, not a habit:

```
python content/video_engine/scripts/self_watch.py <build> --project <project dir> --script <report stem> [--long|--short] [--step 2] [--tile 360]
python content/video_engine/scripts/self_watch.py <build> --html [--player-url http://127.0.0.1:8738/player.html]
```

It writes `<build>/SELF-WATCH.md` (the agent's copy), `<build>/SELF-WATCH.html` (the operator's: one plain question per
row, every named instant as a frame that links into the served player), `<build>/self-watch/` (the opening at 2 s steps,
12 tiles a sheet, and the recipe audit sheets) and `<build>/publish/` (the posting side, R26-8). Exit 1 when section 1
carries a FAIL. It renders nothing and re-authors nothing: every number is a tool's, read through that tool's own rows.

- **section 1 - the gates.** Mechanical, every verdict filled by a tool. A FAIL here ends the report.
- **section 2 - the opening, read.** O1-O11, the AGENT's read of the sheets (`Read` on the PNGs, one at a time). The
  runner writes them as TODO; it never fills a read it did not do.
- **section 3 - one verdict line.** `NOT CLEAN - <the first failing row>: <detail>`, or
  `TODO - the agent reads the sheets and fills O1-O11`. **CLEAN is the agent's word**, written after the read; a build
  handed to the operator carries CLEAN.

## Section 1: what fills each row

| row | filled by |
| --- | --- |
| motion gate (M01-M24) | `gate_motion_density.py`, one subprocess; its FAIL and WARN rows plus its `RESULT:` line |
| M25 layout | the same gate's layout row, over `probe.py --gate`'s `layout-probe.json` (written first, keyed to this player) |
| species by sentence | `lint_species_choice.report` - the counts and every `no row` sentence |
| E61 plates (long) | the same lint's plate WARNs (a short reads `n/a`) |
| the viewer (P36) | the last verdict line of `<project>/<stem>-VIEWER.md` |
| the script gates | the last verdict line of `<project>/<stem>-GATES.md` |
| **the one-shot floor (M35-M42)** | `gate_one_shot_floor.py`, ONE subprocess, one section-1 row per id (below) |
| **the recipe audit sheets (O11)** | the sheets this run wrote - INFO, or WARN naming a proof cut it could not read |
| the publish package (R26-8) | `publish_package.write_package` - it reads the build, it never gates it (a missing description WARNs) |

## The one-shot floor (E96, P56)

Whole-cut aggregates, not a rate: the thin one-shot was offered for a watch at 0 FAIL because it ran 17.9 events/min -
as busy as Tokyo - with 1 chart form and 0 docks. The gate is `content/video_engine/scripts/gate_one_shot_floor.py`
(its header carries every definition: what a beat, a form, a transform, a dock-carrying beat and an event ARE); the bar
runs it as a subprocess and parses its rows, so the floor has exactly one implementation.

| row | the floor | levels |
| --- | --- | --- |
| M35 | distinct chart forms >= 3 (a page's `(builder, variant)`, a chart dock's own discriminator) | FAIL / PASS |
| M36 | chart-to-chart transforms >= 1 (a `chart_to` species, or a `morph`/`stamped` page on a page) | FAIL / PASS |
| M37 | docks on >= `max(1/3, the reference's own)` of the beats, ON SCREEN (HG1's reading) | FAIL / PASS |
| M38 | proven-recipe coverage >= 0.60 of the beats, the reference's own coverage printed beside it | FAIL / PASS |
| M39 | narrative : chart >= `max(1.0, the reference's own)` | FAIL / PASS |
| M40 | parity with the best approved short (measured at run time) + Bravos (quoted) | **JUDGE, never FAIL** |
| M41 | the beat plan (`<build>/BEAT-PLAN.jsonl`) covers every beat | FAIL / PASS, WARN with no plan on disk |
| M42 | events/min, compositions/min, builds:compositions | **INFO, never a floor** (E96 (3)) |

- **HG1's predates-E96 reading (2026-09-13, recommendation A).** The four cuts on disk when the floors landed
  (`japan-tariff-trick/build-short`, `tokyo-tea-break/build-short.v2`, `steel-and-paper/build-f`,
  `normal-for-which-bridge/review-v1`) are **never re-judged**: on them M35 and M36 print `INFO ... predates E96` with
  the measured number. M37-M39 still PASS/FAIL there. That tuple is an exemption, not a knob - adding a build to it
  needs a ruling.
- **The thresholds come from the reference, not from taste.** The parity floors are additionally held to the best
  approved short's OWN numbers, measured at run time from its timeline by the same functions
  (`docs/agent-memory/operator/thresholds-from-the-reference.md`). Bravos is the one quoted column.
- **A floor is a floor, never a target.** Clearing M35-M42 says the cut is not thin; it never says the cut is good.
  Sequence, taste and the package stay JUDGE (M40) and the agent's read (O1-O11), read against the best approved short
  and never against the gates.

### What the verdict says

A floor FAIL is `NOT CLEAN` like any other section-1 FAIL, and it names the id:

```
NOT CLEAN - the one-shot floor (M37): docks on 0.28 of 25 beats (7 on screen, 5 entering) - the floor is 0.33 ...
  · also under the floor: M38, M39
```

The FIRST failing row is the one the line quotes (the motion gate's FAIL still comes first when there is one); every
other failing floor id is listed after it, so one read names the whole gap. M40 (JUDGE) and M42 (INFO) ride as rows and
can never end the report, and a floor gate that is missing, cannot be run, or prints no row is ONE WARN row naming it -
the bar never crashes on it, and an unmeasured floor never reads as a pass.

## The recipe audit sheet (O11)

`<build>/self-watch/recipes/beat<NN>-<recipe-slug>.png`, one per **beat that carries a proven recipe** (one per beat per
recipe - the beat the fire STARTS in, from `recipe_walk.match` over this build's compiled timeline against every
`proven` recipe in `docs/EFFECTS-CATALOG.jsonl`). Each sheet is two labelled rows of frames:

- **top row - `this cut`**: this build's frames at the fire's own member instants (`Fire.members_at`).
- **bottom row - `the proof`**: the PROOF cut's frames at its `proof.members_at` - the instants that earned the recipe
  the word `proven`.

The header names the beat, the instant, the scene, the recipe and the proof build. The proof cut is read where it lies,
READ-ONLY, through `probe.Probe` (one session per proof build, after this build's own - playwright allows one session
per thread): **it is never rebuilt, never re-compiled, never re-rendered**
(`docs/agent-memory/operator/review-link-frozen-copy.md`). A recipe whose proof cut is not on disk, or a proof cut that
cannot be probed, is a WARN row naming it and no sheet - never a FAIL, and never a reason to rebuild anything.

The sheets are the critic's raw material; **no judge rides here** (E96: the audit is a read, and JUDGE stays where it
is). The read itself is O11, verbatim:

> **O11** - the recipe fired as its proof does: the members in order, at their offsets - name the beat where it did not.

Its plain question, for the operator's HTML copy: *"On each recipe sheet, does the top row (this cut) do what the
bottom row (the proof) does: the same members, in order, at the same offsets?"* A PASS looks like two rows that read as
the same move, beat by beat; a FAIL is a member missing, out of order, or arriving so late the combination reads as two
unrelated things. Sheets are bounded (the first 24 (beat, recipe) pairs; the row says so when it capped) because a
sheet is frames.

## What the bar never does

- It never fills an O-row, and it never writes CLEAN. Both are the agent's, after the read.
- It never rebuilds, re-compiles or re-renders anything - this build or the proof cut.
- It never re-implements a gate: every number is parsed from the tool that owns it.
- It never turns a JUDGE or an INFO row into a verdict.

## See also

- `docs/GATES-REGISTRY.md` - every row id by family (the floor is family `floor`, M35-M42).
- `.claude/PRPs/plans/P56-EFFECT-RECIPES-AND-THE-ONE-SHOT-FLOOR.plan.md` - the floors, HG1, HG2 and the recipe data
  family; `docs/portable/OPERATOR-RULINGS.md` **E96** is the ruling underneath them.
- `docs/content-video-engine/PIPELINE.md` - where the bar sits in stages 1-8;
  `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` - what the rows are defending.
