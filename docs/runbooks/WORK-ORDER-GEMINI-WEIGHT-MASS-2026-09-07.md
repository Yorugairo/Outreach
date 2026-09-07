# Work order — weight, density and mass in drawing, animation and stop-motion (2026-09-07)

**To:** the Gemini research lane (profile `video-researcher`). **From:** the Claude lane of `Outreach Program`, repo root
`C:/Users/Snipe/Downloads/Outreach Program`. Reply shape: `report-landed`. **Skills: use the `/research` skill** — run it as
`/research --deep weight, density and mass in drawing, animation and stop-motion: the impact frame, the contact shadow, the
receiver, the settle` (the deep two-pass form: discovery, then full-page primary extraction). Use
`python content/video_engine/scripts/docs_find.py "<term>"` for every claim you check against our docs.

## Why

The operator watched Tokyo v3's first thrown and landed cards (P47 T1) and said: *"it doesn't land with much weight/impact,
no shadow coming in, and doesn't feel like it has density/weight on the landing ... I could get more research done on
weight/density/mass in drawing/animation/stop-motion."* The parent diagnosed four missing mechanisms against the HyperFrames
stop-motion-cadence and headline-slam references and built them as dials (`content/video_engine/scripts/kinetics/stopaction.mjs`:
`impactSquash`, `contactShadow`, `groundShake`, `MASS.*.impact`). Every number there is `[DERIVED]` from a vendor demo. We
need the numbers from the sources.

The full brief, with the six questions and what we already hold, is
`docs/research/motion/BRIEF-WEIGHT-DENSITY-MASS-2026-09-07.md`. Read it first and do not re-research what it lists as held
(doc 48 §48.6, doc 42 §42.3, the material presets, the floating-sticker rule, the two vendor components).

## The six questions, in the brief's order

1. The frame count of a HIT: how long an impact squash holds and how it releases, by weight — Williams (*The Animator's
   Survival Kit*), Lasseter 1987, and stop-motion practice at 12 fps on 2s (Aardman, Laika).
2. The cast shadow as the depth cue for a thing dropping onto a surface: size, offset, blur, darkness — which reads first
   (Kersten et al. 1997 on moving cast shadows, and after).
3. The RECEIVER: what the surface does when a heavy thing lands — shake, dip, dust, a secondary bounce — which reads as
   weight, which as violence; a drawn-animation frame count if one exists; does it scale with mass.
4. Density vs mass in a flat drawing: with no volume, what separates heavy from light in the same silhouette, and how
   animators rank those cues after the contact (the pre-motion ranking is doc 48's; we want the post-contact one).
5. Sound: the impact cue's onset relative to the contact frame, and the gain relationship between a landing and the bed.
6. Stop-motion specifics: tie-downs, the 2–3 frame wobble of a landed thing, replacement-animation squash sets — anything
   with a number.

## Form (the intake's proof discipline — `docs/content-video-engine/HYPERFRAMES-INTAKE-2026-09-06.md` §1)

Every statement tagged `[source on file | practitioner doctrine | DERIVED | UNVERIFIED]`; every figure with a proof line
`[Metric | value | authority | URL | Verified 2026-09-07]` quoting the page it is on; the numbers in ONE table at the top
(question, cue, number, frames at 24 / 12 fps, source, tag); a NOT FOUND block naming the roots you searched, ours and the
web's. Wrong-by-omission is worse than "not found": say what could not be sourced. Where a source contradicts what we hold,
say so and do not resolve it — the parent does.

## Loop discipline

This is a large job: run it as a loop with checkpoints. After each question, append its section to the landing file and
write a one-line checkpoint to `docs/research/runs/weight_mass/CHECKPOINTS.md` (question number, sources opened, done or
blocked). If a page will not fetch, record it in NOT FOUND and move on; never stop the loop on one page. Do not abstain on
budget — deliver what is sourced, mark the rest.

## Landing

`docs/research/motion/WEIGHT_DENSITY_MASS_RESEARCH_BLUEPRINT.md` (new); sources saved under `docs/research/motion/sources/`
when the licence allows, otherwise the URL and the quoted line; working files under `docs/research/runs/weight_mass/`. Then
`python content/video_engine/scripts/build_docs_layers.py --write` and `--check` green. Do not touch the engine, the template,
the kinetics modules or any doctrine file.

## Reply

`POSITION`, `PATHS WRITTEN` (absolute, bare paths one per line), `DISAGREEMENTS` (where a source contradicts doc 48 or the
vendor numbers), `PREREQUISITES`, `NOT FOUND WHERE I LOOKED`; then the count: how many of the six questions got a sourced
number, how many practitioner doctrine only, how many nothing. Under 150 words after the grammar.
