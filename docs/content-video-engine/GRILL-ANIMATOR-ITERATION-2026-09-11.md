# Grill: the animator's loop — decision ledger (2026-09-11)

`/grill-me let's find the most powerful features we could add to make you a better animator, and improve our iteration
speeds/time-to-production.` Two rounds, one research spike (`docs/research/runs/grill_animator-iteration/findings_r1.md`),
the operator's answers verbatim where they bind. The plan that implements it: `.claude/PRPs/plans/P51-THE-ANIMATORS-LOOP.plan.md`
(draft). The horizon beyond it is §5.

## 1. Settled

| decision | the operator's words | what it binds |
|---|---|---|
| **The time goes into the watch-then-cut rounds, because the first pass is not close enough.** | *"B. because we don't come close enough to a first pass, then we spend a lot of time improving and iterating takes too long."* | The lever is the first pass's quality and the agent's own loop, not the operator's hands. |
| **The agent's loop first, the operator's editor second.** | *"C, a first."* | Probes, a layout gate, hot reload and the self-watch precede any editor surface. |
| **The player stays a pure function of t; the editor is a client. A ghost outline may follow the hand while dragging; the real frame on release.** | *"Option A with the ghost outline B sounds ideal."* | No runtime state in the engine, ever; the editor writes data and asks for the frame. |
| **A human's or a flash agent's edit is a sidecar of overrides keyed by row id and field, layered over the shot table the agent authors.** | *"Q1. A."* | The agent sees a change as the diff line, the two frames at the affected instant and the gate delta. The Motion Canvas pattern (a named-event sidecar), not Remotion's write-into-source, not Theatre's random-id state. |
| **Hot reload proves determinism on every edit** - the changed instants re-render warm and cold and hash-compare. | *"I would say A"* | Option A becomes a check, not a rule. |
| **Goldens are consistency, not quality.** | *"'goldens' is just the term that becomes 'consistent rebuild' right? ... those early examples will be far superceded."* | Yes. A golden pins that nothing moved that we did not mean to move (the OFF state of every mechanism is byte-identical); it is regenerated on purpose, in a commit that says why, whenever a mechanism changes by design. It never freezes taste. |
| **The one-shot bar: gates green plus a self-watch before the operator watches** - the layout gate, the species-by-sentence lint, the blind viewer, and a contact sheet of the opening at two-second steps read against a checklist. **The opening is the first 3 minutes on long form, the first 60 seconds on a short.** | *"A except I think it needs to be the first 3 minutes on long format/horizontal, first 60 seconds on shorts."* | The self-watch report is a build artifact; the operator's watch begins only when it is clean. |
| **The ledger/chart page is the world - the main character. Plates are narration plates: B-roll that links ideas, decompresses, grounds, and differentiates.** | *"the ledger/chart plate is the world that we build on, it's the main character. plates become narration plates ... it basically becomes B-roll. In a way, the plates exist because we didn't know how to hold animation or time with charts or tell the narrative over a long-format. Now we have much more capability in that."* | The next long is authored on the page; the chart-to-chart family carries the scenes; a plate appears where the story needs a picture. The package leads with the ledger look. |
| **The three uses of a plate, once the chart is the world.** | *"the chart playing main character, sometime we throw a plate onto the art world, and then dock evidence on it. Sometimes we just dock evidence by itself ... Plates just get used as needed kind of between ideas if it's a one-dimensional video ... othertimes I imagine we go to a plate as essentially a transition to cover the world, we reset the evidence, and come back clean or on a completely different topic."* | (1) a LANDING SURFACE: a plate thrown onto the art world and evidence docked on it (P50 T7, the art embed) - or evidence docked straight onto the chart world (B3); (2) a BRIDGE: a narration plate between ideas, B-roll; (3) a RESET: a plate that covers the world so the evidence clears and the next page mounts clean or on a new topic (the surface grammar's C1 wipe with a plate as the departing world, E47's dip/mount as the seam). Each plate still lives (E21, the idle) and never carries the package alone. |
| **No reproductions.** | *"as soon as we build 50, we will want to re-build the videos ... it's better to reach the new level and produce new content before releasing reproductions."* | Capability work ships in NEW content; old cuts are not re-rendered. The render tail must therefore be one command with zero rounds. |
| **The "AI slop" comment was about the package and the amount of generated art, not malformed hands.** | *"i don't think there's a single malformed hand anywhere in the video ... he was being metaphorical about ai everywhere/too much generated plates and primarily the thumbnail."* | A hand-count gate is NOT the answer; fewer plates and a package that does not read as generated is. |

## 2. Rejected

- **An editor that holds live state** (option B): the documented killer is a change that passes preview and dies in render (Remotion's own docs: tweens on plain objects "animate in the Player but freeze in renders because nothing re-reads the object after a seek"). Only the cosmetic ghost outline is allowed.
- **The editor first.** Most of this week's rounds were the agent's blind spots (a light over the page, a card over the bars, a citation under a card), not the operator's missing hands.
- **Vision as the agent's eyes.** Numbers first: a DOM probe at t costs ~150 text tokens and answers overlaps, sizes and clearances; a full frame costs ~2,800 and answers them worse. Frames only as contact sheets at instants the timeline chose, crops only to verify a number.
- **Writing the human's edit into the shot table** (Remotion-style): it erases the line between the agent's structure and the human's tuning and makes a flash agent's edit indistinguishable from the author's.
- **A generic generator or a GUI-first tool for agents.** The engine's value is determinism plus provenance plus the operator's taste; agents don't drag.
- **A hand-count gate on plates.** See the last settled row.

## 3. Verified gotchas (from the spike)

1. Preview-versus-render desync is structural, not a bug class you fix once: HyperFrames gates capture on the same runtime both sides and still warns that fonts and Chrome versions shift a render by a pixel between machines (Docker for exactness). Our goldens are per-machine until then; a cross-machine golden must pin the browser.
2. Random ids defeat diffs: Theatre.js keyframes carry random ids, so "what changed" needs a semantic diff keyed on the prop path. Our sidecar is keyed by row id and field from the start.
3. The replay cost does not apply to us: Remotion re-renders the timeline forward from zero every frame; ours evaluates t in closed form. Keep it that way - every mechanism is a function of t, never an integrator.
4. Retention: 39 % average viewed on 13:27 sits a hair under the published "strong" band (40-50 %) and far above the platform median (23.7 %); 60 % at 0:30 IS the published hook target. The leak is 0:30 to 1:13 (12 points in 43 s) - the promise window E24 already guards. No Bravos retention figure exists in any published source; do not invent one.
5. The only documented agent-plus-human timeline loop (Remotion + Claude Code) proceeds "diff review, validation, apply, frame checks, human approval for the render" - the order our sidecar loop should keep.

## 4. Immediate build order (P51, after P50 T1 the map)

1. **The authoring kit** - the eleven helpers the two shorts copy, plus the outro/bed/pauses assembly, become one library both doors (short and long) call; the shot table becomes data with word anchors. (R26-17 step 0.)
2. **Eyes: the probe CLI and the layout gate** - `probe <build> <t...>` returns boxes, overlaps, sizes at phone scale, the camera state and every mark as JSON, plus a contact sheet on request; M25 refuses overlaps, under-size type and safe-zone breaches at build. Zero tokens per build after the first.
3. **The self-watch** - the one-shot bar as a build artifact (`SELF-WATCH.md`): gates, the lint, the viewer, the opening's sheet at 2 s steps (3:00 long / 0:60 short) with the checklist verdicts. The operator's watch starts here.
4. **The runtime apart from the document** - the painter and the kinetics as a module the page loads; the timeline and the asset map fetched, not embedded (today's player is 32 MB of data URIs). Render path unchanged; goldens byte-identical. (R26-17 step 1.)
5. **Hot reload with the determinism check** - a watcher; the changed instants re-rendered warm and cold and hashed; under a second. (R26-17 step 2 + Q2.)
6. **The override sidecar and the change report** - `overrides.json` keyed by row id and field; the compiler layers it; a diff produces the before/after frames at the changed instants and the gate delta as one artifact. This is what lets the agent respond to a human's or a flash agent's cut when summoned. (Q1.)
7. **The editor, thin** - scrub, scene list, species per scene, the dials as live controls writing the sidecar; the ghost outline on drag; the remotion-ui components as the shell. (R26-17 step 3.)
8. **The chart-as-world doctrine** - in parallel, as docs: the ledger page as the main character across a long form's phases (the equation spine, scene extension, the park/un-park, the burst), plates as narration plates, and the package rule (the thumbnail leads with the ledger look). Steers the next long.

## 5. The horizon: AnimatorOS

The operator: *"we need like an 'AnimatorOS' where we start a component library + editor similar to how i built with codex for
react but also with a canvas layer and built-in agents. Almost like our own local version of Google Flow, with Gemini doing
research and building composites/evidence/drafting, GPT doing image generation, and claude for refinement."* Reference points:
vidrush.ai (pulls real clips and A/B roll, generates images and elements in-session, drops them onto the player) and a
timeline-editor shell (elements panel, preview canvas, a track timeline with a waveform and a named cursor).

What P51 builds is the spine that shell needs: a deterministic engine with a query surface, authoring as data, a diffable edit
layer, and a self-watch. The agents in the operator's picture (research and composites, image generation, refinement) are
clients of that spine exactly as the editor is; the asset pulls (real clips, B-roll, generated elements) land as docks and
plates through the same evidence intake (a URL or a generation becomes a sourced object with provenance) - the "never
fabricate" rule is the contract that makes an OS of it rather than a slop machine. The thin editor of step 7 is the first
panel of that shell; the flash agent is its second user. Not planned until P51 stands.
