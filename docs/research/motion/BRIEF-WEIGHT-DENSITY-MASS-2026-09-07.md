# Research brief — weight, density and mass in drawing, animation and stop-motion

**Asked by:** the operator, 2026-09-07, on Tokyo v3's first throw and landing (P47 T1, HG2): *"The throw comes on, but it
doesn't land with much weight/impact, no shadow coming in, and doesn't feel like it has density/weight on the landing ... I
could get more research done on weight/density/mass in drawing/animation/stop-motion."*

**What we already hold (do not re-research):** doc 48 §48.6 (mass is communicated BEFORE the object moves: APA 100–150 ms,
the grip–load clamp, the unloading dip); doc 42 §42.3 (area-preserving squash driven by velocity and deceleration); the
brief's material presets (mass-spring-damper by material, `ANSWERS-RESEARCH-BRIEF-animation-craft.md:226-232`); doc 48's
"floating sticker" rule (a contact shadow is two components: a tight AO slit and a directional cast shadow); the HyperFrames
stop-motion-cadence reference (a 5-step squash envelope on the hit, the contact shadow pinned to the landing spot growing
1.05→0.55 in scale and 0.25→0.85 in alpha with height) and headline-slam (a three-frame stage shake on the landing) — both
verbatim in `content/video_engine/hyperframes/compositions/components/`. What T1's follow-up built on 2026-09-07:
`stopaction.mjs` `impactSquash` (the stepped envelope, scaled by the material's `impact`), `contactShadow`, `groundShake`.

**What we need answered, with sources on file (papers, animator texts, stop-motion practice), numbers where they exist:**

1. **The frame count of a hit.** In hand-drawn and stop-motion practice, how many frames does an impact squash HOLD, and how
   is it released — the shape of the envelope (peak on the contact frame, or one frame after?), by the weight of the thing?
   Williams (*The Animator's Survival Kit*) and Lasseter (1987) are on the reading list but not on file; what do they give
   as numbers, and what does stop-motion (Aardman, Laika practice) do differently at 12 fps on 2s?
2. **The cast shadow as the depth cue.** For a thing dropping onto a surface, what sells height — the shadow's SIZE, its
   OFFSET from the object, its BLUR, its DARKNESS — and in what order do viewers read them? Is there perceptual work on
   shadow-driven depth in 2-D compositing (Kersten et al. 1997 "moving cast shadows" and after)? Our dial is
   height → scale 0.55–1.05, alpha 0.25–0.85; is the alpha ramp or the blur ramp the stronger cue?
3. **The receiver.** When a heavy thing lands, what does the SURFACE do in practice — a camera shake, a surface dip, dust,
   a secondary object bouncing? Which cue reads as weight and which reads as violence? The three-frame stage shake is
   HyperFrames' answer; is there a drawn-animation convention with a frame count, and does it scale with mass?
4. **Density vs. mass in a flat drawing.** With no volume, what separates a HEAVY flat thing from a LIGHT one in the same
   silhouette — the deceleration curve into the contact, the settle's damping, the anticipation's length, the overshoot's
   absence? Which of these do animators rank first? (Doc 48 §48.6 says the pre-motion; we want the post-contact ranking.)
5. **Sound.** The impact cue's onset relative to the contact frame (before, on, after) in animation sound practice, and
   the gain relationship between a landing and the bed — E44 already sets a gain ceiling for a cue on a short.
6. **Stop-motion specifics.** Real stop-motion weight tricks: the "tie-down" (a puppet pinned to the set so the contact is
   absolute), the wobble of a landed thing over the next 2–3 frames, replacement-animation squash sets — anything with a
   number we can turn into a dial on the stepped clock.

**Form of the answer:** the intake's proof-gate form (`docs/content-video-engine/HYPERFRAMES-INTAKE-2026-09-06.md` §1): every
statement tagged [source on file | practitioner doctrine | DERIVED], the numbers in a table, the sources' file paths under
`docs/research/motion/sources/`. Wrong-by-omission is worse than "not found": say what could not be sourced.

**Where it lands:** dials on `stopaction.mjs` `STOP` / `MASS` (the envelope, the shadow ramps, the shake, the per-material
`impact`), each `[DERIVED: …]` until measured on ours; the T1 evidence in P47; and, when the operator's ear agrees, a ruling.
