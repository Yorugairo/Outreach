# Grill: where the pipeline leaves value on the table - decision ledger (2026-09-13)

`/grill-me to find the weaknesses in our pipeline, where are we blatantly leaving value on the table?` - two rounds, three
research spikes (rigging relations in production tools; the true vector brush and the generate -> vectorize -> draw pipeline;
the effect combinations mined from the approved cuts), one played reference (Bravos, "The Bubble's Final Phase Has Begun.",
downloaded with the operator's permission and deleted after the read). Preceded by the operator's two framing questions: whether
the studio's "middle ground" (session link, sidecar grammar, per-effect proof players) improves abilities or adds complexity, and
`/grill-me` on stronger animations, brush strokes and higher-quality one-shots. Artefacts: `docs/research/runs/grill_pipeline-value/`
(findings_rig.md, findings_brush.md, recipes_r1.md + .jsonl, BRAVOS-RIG-VERIFIED.md, OPERATOR-RULINGS-R1.md; gitignored).

## 0. What the operator settled (verbatim where it is a ruling)

- **Overbuilding is deliberate; the grind comes when capabilities stabilise.** *"we overbuild on purpose: because we need you to have
  variety to choose from to make the one-shots worth grading and iterating is slow, so it makes more sense to build capability,
  then sit down and grind once we can get GPT back in the mix and capabilities are somewhat stabilizied ... Once we stabilize
  upgrading our capabilities, and improve iteration speed, episodes naturally ship faster."* -> the shipping count is NOT a leak.
- **The one-shot's quality is lost in authoring, tools AND self-critique** - *"especially ... minimal motion/transformation, and
  mixing of narrative panels and charts. You mostly changed words and used only 2 charts."*
- **Effect recipes are the missing key.** *"the individual effect is not really the key, it's blending a few of them together
  that creates the effect ... I think we need the effect recipe and the capability comparator ... a mini engine in itself where we
  require a capability and comparator plan per beat, effective combinations build the effective recipe, and what the
  director-critic is actually auditing is if the effect recipes are effective."* -> **Round 2 Q1: A + C** - recipe CARDS in the
  P55 catalogue (ordered card ids, offsets, the sentence act, a played instant as proof), generated into authoring-kit presets.
- **The one-shot floor is measured.** -> **Round 2 Q2: (a)** - floors per short before the watch (chart forms, a chart-to-chart
  transform, docks on beats, recipe coverage, narrative:chart), JUDGE for the rest against the best approved short.
- **The brush: a true vector brush plus several brushes; out-compete the doodle tools.** *"We have all of the math and the local
  capability and own the engine, there's no reason we shouldn't be able to do all of the brush options ... Need a thing? generate
  the thing. need to vectorize it? vectorize it. Need to pass it through Comfy to get it to draw? do that. We get stuck on things
  that shouldn't be blockers and just put out boring work unless I direct ... it's just about empowering agents and finding how to
  give them proper selections and teach taste, and not choosing the nearest answer."* -> **Round 2 Q4: a, then b, then c** -
  the hand-drawn species first (callouts, squiggles, underlines), then the chart's own paths, then whole-image draw-reveals.
- **The rig joins the plan; relations win.** *"rigging ... can also be used to move evidence around the screen and manipulate
  camera perspective ... If relations is feasible then that's clearly the winner."* -> **Round 2 Q3: both defaults** -
  translate-only inheritance unless widened; parents scale uniformly only.
- **Research must be ingested.** *"I think we need a process that immediately ingests the gemini research and adds to backlog or
  exploration"* -> a run is landed only when a backlog row or a plan slice cites it, checked by a test.
- The studio's "middle ground": mostly complexity for THIS goal (a session link speeds the loop, not the frame); keep the
  per-effect proof player (it makes a component visible) and fold the rest into the studio plan (readiness review, R26-102).

## 1. What the measurements showed (the record, not opinion)

| measure | Bravos | Steel and Paper 806 s | Japan 85 s | Tokyo v2 89 s | the thin one-shot 57 s |
|---|---|---|---|---|---|
| events / min | 6.0 | 14.8 (the spike's 16.8 was a hand-entry error; re-derived 2026-09-13, P56 T2: 124 builds / 199 events) | 28.1 | 18.2 | 17.9 |
| compositions / min | 2.5 | 5.58 | 8.44 | 5.40 | 6.33 |
| distinct chart forms | ~6 | 5 | 2 | 2 | **1** |
| narrative : chart | - | 2.34 : 1 | 1.40 : 1 | 1.00 : 1 | **0.20 : 1** |
| docks (held across a cut) | 50 | 43 (20) | 6 | 4 | **0** |
| `chart_to` verbs fired | - | 0 | 0 | 0 | 0 |
| recurring 3-5 effect combinations | - | 13x max | 4x max | - | **0 - every one fires once** |

- The thin one-shot was not slow. It had no grammar: 12 of the 15 measured recipes never fired, and 9 of those 12 need a dock -
  zero docks is the single structural cause. "Minimal motion" was word changes counted as events.
- **`chart_to` has never shipped in an approved cut** (all five verbs `wired`): "transforms should lead to new charts" is an
  unexercised capability, not a regression.
- **67 of 73 `wired` cards never fired in an approved cut**; every one maps to a slot in one of the 15 seeds (recipes_r1.md s4).
- Two laws the cuts obey without a rule: Steel's badge ladder is dock_enter + 2.05 s then + 1.30 s (40/40 gaps); `emphasize`
  equals the spotlight's / punch's datum index (3/3, Japan + Tokyo).
- Catalogue gaps the mining found: `exit:wipe_right` (32 Steel uses) and the Ken Burns pair have no card.
- The long form and the shorts speak disjoint vocabularies (Steel's timeline carries no `species` array); no recipe fires in both.
- Research ingestion: of 16 runs under `docs/research/runs/`, 2 have a backlog row; 6 are cited by nothing under their run path.
  The 09-04 bundle WAS ingested (85 `tracked` formulas in the animation registry; TRIAGE-2026-09-05 verdicts); the rig was parked on
  the operator's own ruling (R26-61) with no trigger to re-surface it when its reason changed (Bravos now rigs).
- The full test suite: 66 failed / 2,734 passed; three were P55 pins, fixed; the P30 lane's 9 reds stand (readiness review s7).

## 2. Verified gotchas and precedents (tiered; the spikes' findings files hold the sources)

**The rig (findings_rig.md).** The Bravos prop is five relations - group scale, ball pinned under the elephant, elephant pinned
to the ball's top with translate-only inheritance, the wire bending under the ball's contact point, cards aimed at nodes - and
every one resolves at COMPILE time (no measured box), so goldens stay byte-identical. Played at 2 fps: the ball poofs in (~0.5 s),
the wire draws on left-then-right (~0.8 s), the group pushes in, cards attach one at a time, the group pulls back, the ball alone
scales to giant (~1.5 s) while the elephant keeps its size and the kink deepens; NO rotation, NO wobble, NO travel, camera locked
(Gemini's account said otherwise; the frames rule). Industry: parenting is transitive and acyclic (Lottie); inheritance is
opt-in per channel (Spine's Inherit Scale toggle, Rive's Translation constraint, Duik's Position constraint); a path bending
under a pinned child is a primitive only as an AE expression - a compiler is that case natively (`derive:`); a label pins, never
parents; Z stays authored; only closed-form relations survive seeks; SVG's `non-scaling-stroke` exists, `non-scaling-size` was
never implemented - the counter-scale is ours to compute. It replaces `resolveTarget`'s six-kind switch, `camArrivalState` and the
`extend_camera_cards` patch. Our 0.45 s min-jerk arrival is already the standard ease.

**The brush (findings_brush.md).** SVG has no variable stroke width (W3C ISSUE-2271 idle since ~2013): a brush is a FILLED
OUTLINE (perfect-freehand's outline polygon; Canva ships it as SVG paths). `stroke.mjs` already computes the pen's width along the
path; nothing draws it (`drawOn` offsets a dash on a constant-width stroke). The seek-safe reveal is to regrow the outline from
the path prefix each frame, keeping the dash-offset as the flag-off branch. The doodle tools do not animate strokes at all
(VideoScribe draws SVG layers in file order and forbids brush strokes; Doodly scribbles a zigzag); none has curvature-aware
speed, variable width, data binding or determinism - we ship four of five. Vectorize: a Comfy lineart pass then a medial-axis
skeleton (centreline PLUS a measured width per pixel); potrace/vtracer give fills (a dashed "line" traces its own perimeter).
Grain is the vector/raster line: geometry ours, tooth from a generated plate (the soak ruling generalised).

**The recipes (recipes_r1.md).** 15 seeds with members, offsets, first-fire instants and the act each serves; s4 slots every
unused card; s3 states the thin cut's gap as recipes never used.

## 3. Decisions - effect recipes, the one-shot floor, the relation layer (the rig), the vector brush, research ingestion

1. **Recipe cards** (P55 extension): `content/video_engine/effects/recipes/*.json`, one recipe = ordered card ids + offsets + the
   act + `proof: {project, build, t}`; status `proven` (a played instant in an approved cut) | `candidate` (no cut yet); the drift
   gate refuses a proven recipe without an instant; generated into `docs/EFFECTS-CATALOG.md` and into authoring-kit presets
   (`authoring/recipes.py`). Seeds: the 15 measured; candidates: the 67 unused cards in their slots. The comparator plan per beat
   picks recipes, not effects; the critic audits whether the recipe worked (the frames at its instant vs its proof).
2. **The one-shot floor v2**, measured before the watch: >= 3 chart forms; >= 1 chart-to-chart transform; docks on >= 1/3 of beats;
   >= 60% of beats on a proven recipe; narrative : chart >= 1 : 1; parity with the best approved short on those five. A cut under a
   floor is not offered for a watch. JUDGE keeps sequence and taste, read against the best approved short (never against the gates).
3. **The relation layer** (the rig as relations, evidence and camera first): grammar `pin / aim / group / path / derive /
   camera / weight` with `parent` as sugar; defaults translate-only inheritance and uniform parent scale; a label pins never
   parents; Z authored; closed-form only; compile-time resolution wherever the target is authored. First proofs: a card pinned to a
   bar's tip with the camera following (evidence), then the metaphor prop as a recipe (poof + wire draw-on + pin + derive).
4. **The vector brush**: pen via outline regrow fed by `prof.w`, behind a flag; five brushes (marker, pen, highlighter, charcoal,
   dry brush); order a) hand-drawn species, b) the chart's own paths, c) whole-image draw-reveals through generate -> lineart ->
   skeleton -> ordered strokes; grain only from a generated plate.
5. **Research ingestion gate**: a run is landed when a backlog row or plan slice cites it; a docs-layer test lists orphans; a
   parked row carries a `trigger:` that names what re-surfaces it.
6. **Catalogue gaps**: cards for `exit:wipe_right` (or an alias on `exit:wipe` the gate accepts as a use) and the Ken Burns pair;
   the badge ladder's 2.05 / 1.30 and `emphasize == datum index` lifted into their recipes as dials.

## 4. Rejected

- Raster brushes and filter chains as ink (p5.brush, Procreate-style grain, K-M on the soak) - the soak ruling.
- Rive-style vector feathering - renderer-only, not SVG.
- Physics, iterative IK and order-dependent constraint blending in the rig - stateful, not seek-safe.
- Full parenting by default - reproduces the elephant scaling with the ball.
- Events/min as the one-shot floor - the thin cut would have passed it.
- The session link and sidecar grammar as answers to animation quality - they speed the loop, not the frame (studio plan).

## 5. Immediate build order (each a plan slice; none started here)

1. Recipe cards + the drift gate's proof rule + `authoring/recipes.py` (P55's own generator and gate extend; no engine work).
2. The one-shot floor v2 as a gate script the self-watch bar runs; the reference-parity table against Japan.
3. The relation layer in the compiler (`build_scene_timeline_f.py` grammar + a compile-time resolver), its two proofs as
   recipes, goldens byte-identical.
4. The pen brush behind a flag on the hand-drawn species, then the chart paths; the vectorize pipeline last.
5. The ingestion gate and the catalogue gaps (small; can ride with 1).
Prerequisite for all engine work: the commit batch (R26-83) so lanes work from a commit.
