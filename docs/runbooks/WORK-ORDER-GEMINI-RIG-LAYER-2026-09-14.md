# Work order - the relation layer: what 2D rigs and constraint systems get right, harvested (2026-09-14)

**To:** the Gemini research lane (profile `video-researcher`). **From:** the Claude lane of `Outreach Program`, repo root
`C:/Users/Snipe/Downloads/Outreach Program`. Reply shape: `report-landed`. **Skills: use the `/research` skill** - run it as
`/research --deep what 2D rig and constraint systems get right - Rive state machines, Spine and DragonBones constraints, After Effects expressions and the graph editor, Theatre.js - harvested for a relation layer that moves evidence and the camera` (the deep two-pass form: discovery, then full-page primary extraction). Use
`python content/video_engine/scripts/docs_find.py "<term>"` for every claim you check against our docs. A QUESTION, never a design
(RECALL-RECEIPT s3 step 5): the answer is quarantined until the operator approves it, and lands only through a BACKLOG row (R26-121).


## Why

The operator (2026-09-13, the grill): Bravos started using rigging - *"rigging was thought of as a 'move humans' thing, but it can
also move evidence around the screen and manipulate camera perspective - it might be time to develop that aspect."* BACKLOG
R26-105 names the relation layer (`rel: {pin | aim | group | path | derive | camera | weight}`), unbuilt. Everything we have moves a
thing by an authored clock (a pure function of t); nothing yet moves a thing BECAUSE another moved. The memory
`steal-now-harvest-not-replace` binds: we harvest mechanisms, we never swap out a reviewed one. Do not propose an editor; answer the
questions.

## The questions

1. Rive's state machine + constraints (IK, distance, transform, follow-path): the constraint set, how targets are declared, how
   blending between states is specified - and what of it is a MECHANISM (harvestable) versus a product shell.
2. Spine and DragonBones: the constraint types (IK, transform, path), their evaluation order, and how they resolve two constraints
   on one bone - the rule, with a citation.
3. After Effects expressions + the graph editor: the small set of expression idioms motion designers actually use to move evidence
   (`wiggle`, `loopOut`, `valueAtTime`, parenting, null objects, the camera's point of interest) and what a 2D "camera rig" for a
   chart-and-card scene looks like in practice - Bravos-style: the camera pushes into evidence, evidence follows a lead.
4. Theatre.js and similar code-first timelines: how they expose keyframes and easing to code, what a pure function of t looks like
   in them, and whether any lets a value DERIVE from another (a data-driven constraint) - the closest thing to our `derive`.
5. The math: a minimal 2D constraint solver (pin, aim, follow-path, two-bone IK, a weight/lag) as pure functions of the targets'
   states - the standard formulations, cited, so our layer can be derived rather than copied.

## Form (the intake's proof discipline - `docs/content-video-engine/HYPERFRAMES-INTAKE-2026-09-06.md` s1)

Every statement tagged `[source on file | practitioner doctrine | DERIVED | UNVERIFIED]`; every figure with a proof line
`[Metric | value | authority | URL | Verified 2026-09-14]` quoting the page it is on; the numbers in ONE table at the top (question, cue,
number, source, tag); a NOT FOUND block naming the roots you searched; no design proposals - questions answered, sources on disk under
`docs/research/runs/rig_layer/`. Tiers: CONFIRMED (primary fetched and quoted) / PLAUSIBLE (secondary) / UNSOURCED-editorial / REJECTED.
