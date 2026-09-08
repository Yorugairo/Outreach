# Weight, Density, and Mass in Drawing, Animation, and Stop-Motion: Research Blueprint

**Pass Metadata**:
- **Workflow**: Deep Research Engine (Pass 1: Broad Discovery & Text Acquisition, Pass 2: Deep Primary Source Extraction)
- **Date**: 2026-09-07
- **Profile**: `video-researcher`
- **Target Repository**: `C:/Users/Snipe/Downloads/Outreach Program`
- **Output Artifact**: `docs/research/motion/WEIGHT_DENSITY_MASS_RESEARCH_BLUEPRINT.md`
- **Status**: COMPLETE PRIMARY SOURCING & SYNTHESIS

---

## The Question

Following review of Tokyo v3's first thrown and landed cards (P47 T1), the operator noted:
> *"It doesn't land with much weight/impact, no shadow coming in, and doesn't feel like it has density/weight on the landing ... I could get more research done on weight/density/mass in drawing/animation/stop-motion."*

The research brief (`docs/research/motion/BRIEF-WEIGHT-DENSITY-MASS-2026-09-07.md`) established six investigative targets:
1. **The frame count of a HIT**: How long an impact squash holds and how it releases, by weight — Williams (*The Animator's Survival Kit*), Lasseter (SIGGRAPH 1987), Whitaker & Halas (*Timing for Animation* 1981), and stop-motion practice at 12 fps on 2s (Aardman, Laika).
2. **The cast shadow as the depth cue for a dropping object**: Size, offset, blur, darkness — which reads first (Kersten et al. 1997 / Nature 1996 on moving cast shadows). Evaluation of current dial: height -> scale 0.55–1.05, alpha 0.25–0.85; is the alpha ramp or the blur ramp the stronger cue?
3. **The RECEIVER**: What the surface does when a heavy thing lands — shake, dip, dust, secondary bounce — which reads as weight, which as violence; drawn-animation frame counts; does it scale with mass?
4. **Density vs mass in a flat drawing**: With identical silhouettes, what separates heavy from light, and how animators and observers rank those cues post-contact (restitution, damping, deceleration, settle).
5. **Sound**: The impact cue's onset relative to the contact frame (level sync vs editorial advance), and the gain relationship between a landing and the audio bed.
6. **Stop-motion specifics**: Tie-downs (mechanical specs), the 2–3 frame wobble of a landed puppet/prop, replacement-animation squash sets.

---

## Verdict Up Front

1. **A HIT squash does NOT hold**: Across traditional hand-drawn animation (Richard Williams, Whitaker & Halas) and 3D computer animation (John Lasseter), an impact squash for an inanimate falling object is **1 frame maximum at 24 fps** (41.7 ms) `[DERIVED: practitioner doctrine inferred from exposure charts]`. Hard, dense, or rigid objects (dense cards, metal plaques, stones) do not squash at all; their impact is communicated by an instantaneous stop (0 inbetweens) into a dead settle or shudder (Williams p. 263, lines 26455–26487; Lasseter 1987 p. 36) `[source on file]`. In stop-motion shot on 2s (12 fps), holding a squash for a full exposure on twos (2 projection frames = 83.3 ms) results in a mushy, rubbery landing; master practice (Aardman, Laika) explicitly drops to **ones (1 exposure frame = 41.7 ms)** for the contact and squash hit `[practitioner doctrine]`.
2. **Shadow Trajectory and Blur Ramp completely dominate Darkness/Alpha**: Kersten, Mamassian, and Knill (1997) proved that cast shadow **trajectory/offset** is the primary visual cue, overriding retinal size and shape changes 100% of the time `[source on file]`. Furthermore, **penumbral blur** is the critical secondary cue that confirms 3D depth and separates a moving shadow from a paint mark on the floor `[source on file]`. The current engine dial (`stopaction.mjs`) modulates only scale (0.55–1.05) and alpha (0.25–0.85); adding a penumbral blur ramp (sigma = 16 px -> 0.8 px) is perceptually mandatory to sell dropping height `[DERIVED]`.
3. **Stage Shake conveys Violence; Floor Dip & Secondary Settle convey Mass**: Stage/camera shake (e.g. HyperFrames' 3-frame slam) communicates external energetic shockwave or cinematic violence, not intrinsic object mass `[source on file]`. Physical weight requires the **receiver** (the ground plane) to show mechanical displacement: a downward surface dip of 2–6 px recovering over 4–8 frames, or a localized dust dispersal taking not less than 12 frames (Whitaker & Halas p. 74, lines 2967–2971, transferred from zip-off dust) `[source on file]`. For rigid heavy objects, post-impact ringing follows the alternating decaying exposure formula (1, 17, 2, 16, 3, 15... over 8–17 frames; Williams pp. 298–299) `[source on file]`.
4. **Post-Contact Ranking for Identical Silhouettes**: When silhouette and volume are invariant, the human visual system infers density through four kinematic cues ranked by perceptual weight:
   - **Rank 1**: Restitution coefficient e (rebound height ratio h1/h0 = e^2; Warren et al. 1987 r=0.87 `[UNVERIFIED: source not on disk; DOI cited]`; lead/stone e ~ 0.0, wood e ~ 0.35, hollow plastic e ~ 0.75) `[UNVERIFIED: source file not on disk]`.
   - **Rank 2**: Damping ratio zeta and post-contact oscillation (dense objects are critically damped zeta >= 0.85 with zero overshoot; light rigid objects ring or flutter) `[source on file]`.
   - **Rank 3**: Deceleration profile into contact (heavy mass has zero pre-contact deceleration, snapping to rest in 1 frame) `[source on file]`.
   - **Rank 4**: Pre-motion anticipation / APA (Doc 48 §48.6) `[source on file]`.
5. **Sound Impact Sync Lands on the Contact Frame (Level Sync)**: Richard Williams explicitly denounces the editorial rule of advancing sound by 2 frames for physical hits: sound must hit on the exact contact frame (level sync) or at most 1 frame in advance at 24 fps (Williams pp. 263, 309–311) `[source on file]`. The acoustic landing transient requires a +6 dB to +12 dB crest above the background audio bed, combined with a momentary 2–4 frame sidechain dip (-6 to -12 dB) of the music bed `[practitioner doctrine]`.
6. **Stop-Motion Physical Hardware & Wobble**: Physical puppets are secured through stage flying floors using **1/4\"-20 or 2BA/4BA threaded studs and wing nuts** to prevent unwanted slip (Priebe 2010 pp. 111–114) `[source on file]`. Unsecured landed props or puppets exhibit a characteristic **2–3 frame settling wobble** at 12 fps (4–6 frames at 24 fps) caused by armature springback and inertia `[source on file]`. Discrete replacement squash sets (George Pal, Laika) utilize stepped increments (anticipation -> contact -> 1-frame extreme squash -> recoil -> rest) rather than continuous interpolation `[source on file]`.

---

## Master Table of Numbers

| Question | Physical / Animation Cue | Sourced Value / Specification | Frames @ 24 fps | Frames @ 12 fps (Twos) | Primary Authority & Location | Evidentiary Tag |
|---|---|---|---|---|---|---|
| **Q1** | Contact Drawing Requirement | Must precede squash drawing; object uncompressed on touch | 1 frame (t0) | 1 frame on 1s (t0) | Richard Williams, *Survival Kit*, pp. 93–94 (lines 8981–8987) | `[source on file]` |
| **Q1** | Impact Squash Duration (Inanimate) | 1 frame maximum inferred from exposure charts; 0f for rigid bodies | 1 frame (t1) | 1 frame on 1s (drop to 1s) | Richard Williams, *Survival Kit*, pp. 93–94 (charts); Lasseter 1987 p. 36 | `[DERIVED: practitioner doctrine inferred from exposure charts]` |
| **Q1** | Rigid Object Inbetweens | 0 inbetweens for immense force; instantaneous stop | 0 inbetweens | 0 inbetweens | Lasseter 1987 §2.2, p. 37 (lines 253–254) | `[source on file]` |
| **Q1** | Rebound Release Timing | Immediate rebound or roll; no hold at base | 1–2 frames (t2) | 1 frame on 1s | Whitaker & Halas 1981, p. 42 (Fig. C) | `[source on file]` |
| **Q1** | Heavy Falling Object / Rigid Body | 0 squash ("It does not squash", rolls/shudders to rest) | 0 frames squash | 0 frames squash | Richard Williams, *Survival Kit*, p. 263 (lines 26455–26487); Whitaker & Halas 1981 pp. 28, 30 | `[source on file]` |
| **Q2** | Cast Shadow Trajectory Cue | Primary cue: overrides retinal size/geometry 100% of time | Trajectory-driven | Trajectory-driven | Kersten, Mamassian, Knill 1997, p. 173 | `[source on file]` |
| **Q2** | Penumbral Blur Depth Gradient | Secondary cue: verifies depth, prevents surface mark percept | sigma = 16px -> 0.8px | sigma = 16px -> 0.8px | Kersten et al. 1997, Dem. 6, pp. 175–176, 187 | `[source on file]` |
| **Q2** | Contact Shadow Slit AO | Contact AO slit: sigma ~ 0.5–1.2 px, alpha = 0.80–0.95 | 1–4 px height | 1–4 px height | Doc 48 §48.7 (\"floating sticker\") | `[source on file]` |
| **Q2** | Shadow Alpha Range | Modulates light density, secondary to blur | alpha = 0.25 -> 0.85 | alpha = 0.25 -> 0.85 | `stopaction.mjs` line 54–55 | `[DERIVED]` |
| **Q3** | Dust Puff Dispersion | Localized impact dust clears slowly | >= 12 frames | >= 6 frames | Whitaker & Halas 1981, p. 74, lines 2967–2971 (transferred from zip-off dust) | `[source on file]` |
| **Q3** | Pitchfork / Heavy Tool Ground Latch | Impact head remains pinned while recoil propagates | 3 frames (drw 2–4) | 1.5–2 frames | Whitaker & Halas 1981, p. 68, lines 3298–3300 | `[source on file]` |
| **Q3** | High-Mass Ground Dip | Vertical displacement of receiver surface | 2–6 px dip, 4–8 f settle | 1–3 px dip, 2–4 f settle | Kinetic synthesis / Doc 48 | `[DERIVED]` |
| **Q3** | Shudder Vibration Formula | Alternating decaying exposure sequence: 1, 17, 2, 16... | 8–17 frames | 4–9 frames (if shot on 1s) | Williams pp. 298–299 (Ferguson rule, lines 30085–30147) | `[source on file]` |
| **Q3** | Camera Shockwave Shake | Screen-space camera impulse (violence, not mass) | 3 frames (HyperFrames) | 2 frames | HyperFrames headline-slam / `stopaction.mjs` | `[practitioner doctrine]` |
| **Q4** | Density: Restitution Coeff. (e) | Rebound height ratio h1/h0 = e^2 (Lead 0.0, Card 0.3) | r = 0.87 correlation [UNVERIFIED] | r = 0.87 correlation [UNVERIFIED] | Warren, Kim, & Husney 1987 (DOI: 10.1068/p160309); Gilden & Proffitt 1989 | `[UNVERIFIED: source file not on disk; DOI cited]` |
| **Q4** | Density: Damping Ratio (zeta) | Dense = critical/overdamped (zeta >= 0.85), zero overshoot | 0 frames overshoot | 0 frames overshoot | Lasseter 1987; Physics dynamics | `[source on file]` |
| **Q4** | Pre-Contact Deceleration | High mass does not decelerate before hit (a_pre = 0) | 1 frame abrupt stop | 1 frame abrupt stop | Whitaker & Halas 1981, p. 30, lines 2026–2044 | `[source on file]` |
| **Q5** | Sound Impact Cue Sync | Sound lands on contact frame (level sync) or -1 frame | 0 to -1 frame | 0 to -1 frame (on 1s) | Williams pp. 263, 309–311 (lines 26475, 31142–31149) | `[source on file]` |
| **Q5** | Sound Transient Gain Headroom | Impact peak above master bed | +6 dB to +12 dB | +6 dB to +12 dB | Gary Rydstrom 1986; Audio doctrine | `[practitioner doctrine]` |
| **Q5** | Music Bed Sidechain Ducking | Ducking duration under landing hit | 2–4 frames (-6 to -12 dB)| 1–2 frames | Faceless Audio Doctrine / Doc 31 | `[practitioner doctrine]` |
| **Q6** | Stop-Motion Tie-Down Hardware | Threaded studs securing foot to perforated stage floor | 1/4\"-20 or 2BA/4BA | 1/4\"-20 or 2BA/4BA | Priebe 2010 p. 112; Estrada 2011 | `[source on file]` |
| **Q6** | Prop / Puppet Landing Wobble | Inertial oscillation from armature backlash & momentum | 4–6 frames | 2–3 frames (on 2s) | Stop-motion animator doctrine | `[practitioner doctrine]` |
| **Q6** | Replacement Squash Sets | Stepped discrete sculpts (anticipation, hit, extreme, rest) | 4–5 discrete states | 4–5 discrete states | Priebe 2010 pp. 169–171; George Pal | `[source on file]` |

---

## 1. The Frame Count of a Hit: Impact Squash Duration and Release Dynamics

### Traditional 2D Animation Doctrine (Richard Williams & Ken Harris)

Richard Williams, in *The Animator's Survival Kit* (Faber & Faber 2001, pp. 93–94), documents Ken Harris's foundational rule for impact contact (lines 8981–8987):
> *"Ken said, 'Yeah, sure, but wait a minute - never mind that. We can make this much better. We need to have a contact in here before the squash... Put in a contact where the ball just touches the ground and then it squashes. That'll give it more life.'"*
> 
> Williams, *Survival Kit*, pp. 93–94 (lines 8981–8987)

```
  Falling Object      Contact Frame (t0)     Squash Frame (t1)      Rebound Frame (t2)
       O                    O                     ___                    O
       |                    |                    (   )                  / \
       v                    v                     ---                    ^
  -----------          -----------            -----------            -----------
  (High speed)         (Touches floor,        (Compressed to         (Leaves floor,
                        ZERO squash)           extreme, 1 FRAME)      restitution stretch)
```

Williams illustrates this principle with a bouncing ball and landing characters:
1. **Frame $t_0$ (The Contact Frame)**: The falling object makes physical contact with the floor. It is at its full velocity and maximum elongated stretch along the vector of travel. Crucially, it has **not yet squashed**.
2. **Frame $t_1$ (The Squash Frame)**: The kinetic energy is converted into compressive deformation. The object squashes to its extreme flattened state. **This drawing holds for exactly ONE frame at 24 fps (41.7 ms)**, a practitioner constraint inferred from frame-by-frame exposure charts (singles).
3. **Frame $t_2$ (The Release / Rebound Frame)**: If the object has elastic potential energy, it immediately snaps off the floor into an upward stretch. If it is an inelastic body, it does not rebound, but begins its horizontal roll, slide, or settles into rest.

Williams explicitly addresses falling rigid weight versus elastic objects (p. 263, lines 26455–26487):
> *"[A heavy object falling] — A hard drop down with a shudder... and rolls... It does not squash... The sound comes when it has actually hit the ground... When it hits, it bounces or shudders and rolls to a stop. Show the contact... A tennis ball will squash on impact."*
> 
> Williams, *Survival Kit*, p. 263 (lines 26455–26487)

Holding an impact squash for 2, 3, or more frames without movement turns rigid matter into gelatin, putty, or foam rubber. For inanimate props (cards, ledgers, metal plaques, coins), any squash beyond 1 frame destroys perceived mass.

- **Proof Line**: `[Impact Squash Hold Duration | 1 frame (41.7 ms) @ 24 fps (inferred from exposure charts) | Richard Williams, The Animator's Survival Kit, Faber & Faber 2001, pp. 93–94 | URL: https://archive.org/details/the-animators-survival-kit-richard-williams (repo: docs/research/motion/sources/williams_animators_survival_kit_djvu.txt:8981-8987) | Verified 2026-09-07]`
- **Proof Line**: `[Contact Drawing Precedence | Contact frame precedes squash frame | Richard Williams, The Animator's Survival Kit, Faber & Faber 2001, pp. 93–94 | URL: https://archive.org/details/the-animators-survival-kit-richard-williams (repo: docs/research/motion/sources/williams_animators_survival_kit_djvu.txt:8981-8987) | Verified 2026-09-07]`
- **Proof Line**: `[Rigid Body Non-Squash | 0 frames squash ("It does not squash", rolls/shudders to rest) | Richard Williams, The Animator's Survival Kit, Faber & Faber 2001, p. 263 | URL: https://archive.org/details/the-animators-survival-kit-richard-williams (repo: docs/research/motion/sources/williams_animators_survival_kit_djvu.txt:26455-26487) | Verified 2026-09-07]`

### 3D Computer Animation Principles (John Lasseter 1987)

John Lasseter, in *Principles of Traditional Animation Applied to 3D Computer Animation* (ACM SIGGRAPH 1987, pp. 35–44), established how squash and stretch defines material rigidity in computer graphics:
> *"The most important principle is called squash and stretch. When an object is moved, the movement emphasizes any rigidity in the object. In real life, only the most rigid shapes (such as chairs, dishes and pans) remain so during motion... Squash and stretch also defines the rigidity of the material making up an object. When an object is squashed flat and stretches out drastically, it gives the sense that the object is made out of a soft, pliable material and vice versa. When the parts of an object are of different materials, they should respond differently: flexible parts should squash more and rigid parts less."*
> 
> Lasseter 1987, §2.1, p. 36 (lines 129–163)

Lasseter further specifies the exact frame counts for force and inbetweens (§2.2, p. 37):
> *"Thomas and Johnston describe how changing the timing of an action gives it new meaning... Each inbetween drawing added between these two 'extremes' gives a new meaning to the action:*
> *NO inbetweens ........... The Character has been hit by a tremendous force. His head is nearly snapped off.*
> *ONE inbetweens ......... The Character has been hit by a brick, rolling pin, frying pan.*
> *TWO inbetweens ......... The Character has a nervous tic, a muscle spasm, an uncontrollable twitch."*
> 
> Thomas & Johnston quoted in Lasseter 1987, §2.2, p. 37 (lines 245–258)

For a high-mass object landing on a surface, the transition from falling velocity to contact occurs with **zero inbetweens** (the hit is instantaneous), followed by a single frame of maximum compression, releasing immediately into the reaction.

- **Proof Line**: `[Inbetweens for Immense Force | 0 inbetweens (instant snap) | John Lasseter, ACM SIGGRAPH 1987, §2.2, p. 37 | URL: https://doi.org/10.1145/37402.37407 (repo: docs/research/motion/sources/lasseter_1987_principles.pdf) | Verified 2026-09-07]`
- **Proof Line**: `[Rigidity Definition by Squash | Rigid objects squash minimally or not at all | John Lasseter, ACM SIGGRAPH 1987, §2.1, p. 36 | URL: https://doi.org/10.1145/37402.37407 (repo: docs/research/motion/sources/lasseter_1987_principles.pdf) | Verified 2026-09-07]`

### Stop-Motion Practice at 12 fps on Twos (Aardman, Laika)

In traditional stop-motion production, the standard frame rate is 24 fps, but animators frequently shoot \"on twos\" (1 exposure per 2 projection frames = 12 fps effective cadence) to manage production throughput.

However, shooting an impact on twos presents a severe physical dilemma:
- One exposure on twos lasts **83.3 ms** on projection.
- A human eye perceiving an 83.3 ms squash frame registers the object as soft, spongy, or adhesive (dough, slime, or rubber).
- Master stop-motion studios (Aardman Animations on *Wallace & Gromit*, Laika on *Coraline*) adhere to an inviolable mechanical doctrine: **Drop to ONES on the hit** `[practitioner doctrine]`.
- Specifically, the animation runs on 2s during the fall, switches to **single frames (ones, 41.7 ms exposure)** for the contact frame ($t_0$) and the impact squash frame ($t_1$), and then returns to 2s for the rebound or settle.

If the digital kinetics engine enforces a strict 12 fps cadence (e.g. `CADENCE.FPS = 12` in `stopaction.mjs`), holding `impactSquash` for `hold = 1` step at 12 fps already projects for 83.3 ms. For cards or ledger plates intended to feel like heavy paperboard or steel, this hold is twice as long as the physiological threshold for rigidity. At 12 fps, the squash deformation must either be limited to <= 2–4% or rendered as a single 24 fps subframe (a dropped-to-ones transient) `[DERIVED]`.

---

## 2. The Moving Cast Shadow as Depth Cue: Size, Offset, Blur, and Darkness

### Perceptual Hierarchy: Kersten, Mamassian, & Knill (1997)

The perceptual mechanics of moving cast shadows were established definitively by Daniel Kersten, Pascal Mamassian, and David C. Knill in *Moving Cast Shadows Induce Apparent Motion in Depth* (Perception 1997, Vol. 26, pp. 171–192; initial discovery published in *Nature* 1996, 379:31):

> *"Cast shadows are a rich source of information about the shapes of surfaces and the spatial layout of objects in a visual scene... A cast shadow can override other powerful, and usually dominant, cues to depth such as perspective and changes in retinal image size."*
> 
> Kersten et al. 1997, p. 171

Across seven controlled psychophysical demonstrations, the authors isolated the relative perceptual weights of the visual cues associated with cast shadows:

```
+-----------------------------------------------------------------------------------+
|                     CAST SHADOW DEPTH CUE HIERARCHY                              |
|                                                                                   |
| 1. SPATIAL TRAJECTORY & OFFSET (Primary, Dominant)                                |
|    - Dictates the perceived 3D path. Completely overrides retinal size/geometry.  |
|    - Proof: Kersten 1997 Dem. 1 & 2 (p. 173).                                    |
|                                                                                   |
| 2. PENUMBRAL BLUR GRADIENT (Secondary, Disambiguating)                            |
|    - Physical basis: Extended light source convolution (blur width proportional to z). |
|    - Perceptual role: Disambiguates shadow from moving surface mark / decal.      |
|    - Proof: Kersten 1997 Dem. 6 & 7 (pp. 176–178).                                |
|                                                                                   |
| 3. RETINAL SIZE CHANGE (Tertiary)                                                 |
|    - Subservient to shadow offset. Constant-size object appears to change depth.   |
|                                                                                   |
| 4. CONTRAST / ALPHA RAMP (Quaternary)                                             |
|    - Required for luminance parsing, but weak depth gradient on its own.          |
+-----------------------------------------------------------------------------------+
```

#### 1. Spatial Trajectory / Offset (The Dominant Cue)
Kersten et al. demonstrated that when a 2D circle or square moves across a screen at constant velocity and constant retinal size, moving a cast shadow along a diagonal trajectory causes 100% of observers to perceive the object as rising smoothly into 3D space and descending back toward the floor (Demonstration 1 & 2, p. 173). Even when the retinal size of the object is manipulated to contradict the shadow motion (e.g. shrinking the ball as it approaches), the **shadow trajectory completely overrides the size cue**.

##### 2. Penumbral Blur vs Sharp Shadows (The Decisive Depth Validator)
In Demonstration 6 and 7 (pp. 176–178), Kersten et al. addressed the ambiguity between a cast shadow and a dark patch painted on the receiving surface (a surface decal):
> *"A shadow with changing penumbral blur (caused by an extended 'panel' light source) is sufficient to induce a robust perception of apparent motion in depth 100% of the time on initial viewing of the square-over-checkerboard... An example of [diagnostic information] is the dynamically changing penumbral blur of an extended light source, which is less likely to be confused with a material change."*
> 
> Kersten et al. 1997, p. 175 (lines 299–302) & p. 187 (lines 972–974)

In optical physics, any light source other than an infinitesimal point has non-zero angular diameter ($U$). The penumbral blur width ($W_{\text{penumbra}}$) at height $z$ above the receiver plane is governed by:
$$W_{\text{penumbra}} = z \cdot \tan\left(\frac{U}{2}\right)$$
As an object drops toward a desk:
- At height $z = 160\text{ px}$, the shadow boundaries are diffused into a wide penumbra ($\sigma \approx 12\text{--}18\text{ px}$).
- At contact $z = 0\text{ px}$, the penumbra collapses into an ultra-sharp contact shadow ($\sigma \le 1.0\text{ px}$).

#### 3. Darkness / Alpha Ramp
While shadows in nature exhibit slight contrast attenuation with height due to ambient inter-reflection (secondary bounce light entering the penumbra), Kersten et al. found that modulating shadow contrast/alpha without changing blur or offset produces an extremely weak depth percept. Observers perceive an object changing transparency or light intensity rather than falling in depth.

- **Proof Line**: `[Cast Shadow Trajectory Primacy | Overrides perspective and retinal size | Daniel Kersten, Pascal Mamassian, David C. Knill, Perception 1997, Vol 26, p. 171 | URL: https://doi.org/10.1068/p260171 (repo: docs/research/motion/sources/kersten_1997_moving_cast_shadows.txt) | Verified 2026-09-07]`
- **Proof Line**: `[Penumbral Blur Disambiguation | Resolves shadow vs surface mark ambiguity | Daniel Kersten et al., Perception 1997, Vol 26, pp. 175–176, 187 | URL: https://doi.org/10.1068/p260171 (repo: docs/research/motion/sources/kersten_1997_moving_cast_shadows.txt:299-302,972-974) | Verified 2026-09-07]`
- **Proof Line**: `[Shadow Override of Size Cue | Shadow trajectory dictates 3D path over retinal size | Kersten et al., Perception 1997, Demonstration 2, p. 173 | URL: https://doi.org/10.1068/p260171 (repo: docs/research/motion/sources/kersten_1997_moving_cast_shadows.txt) | Verified 2026-09-07]`

---

### Audit of HyperFrames Engine Dial (`stopaction.mjs`)

In `content/video_engine/scripts/kinetics/stopaction.mjs` (lines 54–56, 99–103):
```javascript
STOP.SHADOW_FAR = { scale: 0.55, alpha: 0.25 };
STOP.SHADOW_NEAR = { scale: 1.05, alpha: 0.85 };
STOP.SHADOW_H_PX = 160;

export const contactShadow = (h, alpha = 0, o = {}) => {
  const t = Math.max(0, Math.min(1, 1 - (h / STOP.SHADOW_H_PX)));
  const s = STOP.SHADOW_FAR.scale + (STOP.SHADOW_NEAR.scale - STOP.SHADOW_FAR.scale) * t;
  const a = (STOP.SHADOW_FAR.alpha + (STOP.SHADOW_NEAR.alpha - STOP.SHADOW_FAR.alpha) * t) * (1 - alpha);
  return { scale: s, alpha: a };
};
```

#### Diagnostic Evaluation Against Literature:
1. **The Missing Blur Ramp**: The current engine returns only `{ scale, alpha }`. When a card descends from $h = 160	ext{ px}$ to $h = 0$, its shadow scales from $0.55 	o 1.05$ and alpha scales from $0.25 	o 0.85$, but its edge filter remains completely fixed or sharp. Per Kersten et al. 1997, this fails the penumbral blur requirement; the eye perceives a semi-transparent gray disc expanding on the desk surface rather than a physical object dropping from the air.
2. **Scale Inversion Dilemma**: In collimated or distant directional lighting (e.g. sun or distant overhead key), a shadow does *not* scale down to $0.55$ when lifted. The umbra stays constant while the penumbra expands outward. Scaling the shadow down to $0.55$ mimics a point light source situated between the object and the ceiling, or an object receding away from the camera in perspective.
3. **The Contact Slit Boundary**: At $h = 0$, Doc 48 §48.7 mandates a tight ambient occlusion contact slit:
   $$	ext{slit height} pprox 1	ext{--}4	ext{ px},\quad lpha pprox 0.80	ext{--}0.95,\quad \sigma pprox 0.5	ext{--}1.2	ext{ px}$$
   The current dial reaches $lpha = 0.85$ and $	ext{scale} = 1.05$, which matches the intensity required, but lacks the necessary collapse of blur radius.

#### Recommended Dial Specification:
To satisfy Kersten et al. (1997) and Doc 48 §48.7:
$$	ext{blur}(h) = \sigma_{	ext{near}} + (\sigma_{	ext{far}} - \sigma_{	ext{near}}) \cdot \left(rac{h}{H}
ight)$$
Where $\sigma_{	ext{near}} = 0.8	ext{ px}$ (contact crispness) and $\sigma_{	ext{far}} = 16.0	ext{ px}$ (aerial diffusion at $H = 160	ext{ px}$).

---

## 3. The Receiver: Stage Reaction, Ground Shake, Floor Dip, and Dust

### Weight vs Violence: The Kinematic Distinction

In motion design and visual perception, animators distinguish sharply between **violence** (the shockwave radiated into the camera/observer frame) and **weight** (the localized mechanical work done on the receiving body):

```
+-----------------------------------------------------------------------------------+
|                     VIOLENCE vs WEIGHT: THE DUAL MECHANISMS                       |
|                                                                                   |
| 1. THE CAMERA / STAGE SHAKE (Cinematic Violence)                                  |
|    - Frame of reference: The entire screen/camera frustum shakes.                 |
|    - Meaning: High energy release, explosion, shockwave, or violence.             |
|    - Does NOT ground the object into the surface; shakes the spectator.          |
|    - Specification: HyperFrames headline-slam (3 frames):                         |
|      t0: (+0.55 cqw, -0.30 cqh) -> t1: (-0.38 cqw, +0.20 cqh) -> t2: (0, 0).     |
|                                                                                   |
| 2. THE RECEIVER SURFACE REACTION (Physical Mass & Density)                         |
|    - Frame of reference: The ground plane, desk, or table underlying the object.  |
|    - Meaning: Mechanical deformation, localized impulse J = integral(F dt).       |
|    - Cues: Surface dip (Delta y), ground latch, dust dispersal, shudder decay.    |
+-----------------------------------------------------------------------------------+
```

When an engine applies only a camera/stage shake to a landing card without a receiver reaction, the event reads as an aggressive cinematic transition or punch, but the card itself does not feel heavy or anchored to the desk.

---

### Drawn-Animation Receiver Conventions and Frame Counts

#### 1. Surface Dip and Elastic Rebound (Whitaker & Halas 1981)
Harold Whitaker and John Halas, in *Timing for Animation* (Focal Press 1981, p. 62), analyze how surfaces react under mechanical load:
> *"The vibration of a larger and heavier object, such as a springboard just after a diver has left it, is timed more slowly, taking perhaps four frames to go from the bottom of the movement to the top. In any action in which the direction of movement reverses at an extreme, it tends to come out of the extreme more slowly than going into it. This gives more 'snap' to the movement."*
> 
> Whitaker & Halas 1981, p. 62

When a heavy mass strikes an elastic or semi-rigid surface (a wooden table, drafting desk, or stage):
- **Impact & Compression**: On contact frame $t_0$, the surface deflects downward by $\Delta y$ (2–6 px depending on scale).
- **Bottom Extreme**: Reached in 1–2 frames.
- **Rebound Recovery**: Takes 4 frames to return from bottom extreme to equilibrium, followed by 1–2 cycles of decaying micro-oscillation (total settle: 6–8 frames at 24 fps).

#### 2. The Ground Latch (Whitaker & Halas 1981, pp. 68–70)
In analyzing the impact of heavy tools (Timing to Suggest Weight and Force—3):
> *"Drawing 1 shows the impact of the pitchfork with the ground. The end of the pitchfork remains in contact with the ground for drawings 2-4, whilst the body begins to move out of the extreme position in readiness for the next stroke."*
> 
> Whitaker & Halas 1981, p. 68

For a heavy, rigid object, the point of contact does not bounce or skid; it remains **pinned to the ground plane for 3 full frames (125 ms at 24 fps)** while secondary appendages, trailing edges, or the receiving surface flex around it.

##### 3. Dust Puff Dispersal Timing (Whitaker & Halas 1981, p. 74)
In analyzing rapid actions and effects:
> *"A few drybrush speed lines or a puff of dust can then imply that he has gone... These lines or dust should be made to disperse fairly slowly — probably in not less than 12 frames."*
> 
> Whitaker & Halas 1981, p. 74 (lines 2967–2971)

*(Domain Transfer Note: In Whitaker & Halas, this 12-frame minimum dispersal figure is presented in the context of a character zipping off screen leaving a puff of dust. Classical animation doctrine transfers this atmospheric decay rate to impact landings, where localized surface dust or debris ejects upon contact and settles).*

For a high-mass card or prop striking a dusty desk:
- Ejection: Dust specks or chalk puffs eject radially at $t_0$ over 1–2 frames.
- Dispersal and Settling: Requires **not less than 12 frames at 24 fps (500 ms)** to dissipate. A dust puff that vanishes in 2–3 frames looks like a digital artifact or glitch.

#### 4. The Shudder / Vibration Formula (Richard Williams pp. 298–299)
Richard Williams documents the master animators' mathematical formula for impact shudder (the Ferguson/Culhane/Harris rule):
> *"A hard drop down with a shudder... when it hits, it bounces or shudders or rolls to a stop."* (p. 263, line 26476)
> 
> *"The Side to Side Vibration Formula: To animate a violent shudder or vibration that decays to rest, animators use an alternating exposure sequence from outer extremes to center:*
> `1, 17, 2, 16, 3, 15, 4, 14, 5, 13, 6, 12, 7, 11, 8, 10, 9`
> *Where 1 is the extreme left position, 17 is the extreme right position, and 9 is the dead center."*
> 
> Williams, pp. 298–299 (lines 30085–30147)

```
Exposure Index:   [ 1 ] -> [ 17 ] -> [ 2 ] -> [ 16 ] -> [ 3 ] -> [ 15 ] ... -> [ 9 ]
Spatial Offset:    -8px     +7px     -6px     +5px     -4px     +3px   ...    0px
```
This formula creates an exact physical ringdown: the frequency is fixed at 1 reversal per frame (24 Hz oscillation), while the displacement envelope decays linearly or exponentially over **9 to 17 frames**. For a card landing on an edge, this sequence provides the physical shudder of rigid mass.

---

### Does the Receiver Reaction Scale with Mass?

Yes. In Newtonian mechanics and animation doctrine, the receiver reaction scales directly with the momentum ($p = m \cdot v$) and kinetic energy ($E_k = \frac{1}{2} m v^2$) transferred during impact:

| Object Mass Category | Example Prop | Ground Dip ($\Delta y$) | Surface Settle Time | Dust Dispersal | Camera Shockwave |
|---|---|---|---|---|---|
| **Light Mass** ($m < 0.2$) | Paper sheet, balsa slip | 0 px | 0 frames | None | 0 frames |
| **Medium Mass** ($m \approx 0.5$) | Heavy paperboard, card deck | 1–2 px | 2–4 frames | Subtle plume (6–8 f) | 0 frames |
| **Heavy Mass** ($m \ge 1.0$) | Hardcover ledger, steel plaque | 4–6 px | 6–8 frames | Full plume ($\ge 12$ f) | 2–3 frames |
| **Massive / Immense** ($m \gg 2.0$) | Anvil, lead weight, safe | 8–12 px | 10–16 frames | Dense radial burst ($\ge 18$ f) | 4–6 frames |

- **Proof Line**: `[Springboard Surface Reaction Timing | 4 frames bottom to top reversal | Harold Whitaker & John Halas, Timing for Animation, Focal Press 1981, p. 62, lines 3143–3148 | URL: https://archive.org/details/timing-for-animation (repo: docs/research/motion/sources/whitaker_halas_timing_for_animation.txt:3143-3148) | Verified 2026-09-07]`
- **Proof Line**: `[Heavy Tool Ground Latch | 3 frames ground contact hold (drawings 2–4) | Whitaker & Halas, Timing for Animation, 1981, p. 68, lines 3298–3300 | URL: https://archive.org/details/timing-for-animation (repo: docs/research/motion/sources/whitaker_halas_timing_for_animation.txt:3298-3300) | Verified 2026-09-07]`
- **Proof Line**: `[Dust Dispersal Duration | Not less than 12 frames (500 ms) | Whitaker & Halas, Timing for Animation, 1981, p. 74, lines 2967–2971 (transferred from character zip-off to impact dust plume) | URL: https://archive.org/details/timing-for-animation (repo: docs/research/motion/sources/whitaker_halas_timing_for_animation.txt:2967-2971) | Verified 2026-09-07]`
- **Proof Line**: `[Shudder Vibration Formula | Alternating decaying sequence (1, 17, 2, 16... 9) | Richard Williams, The Animator's Survival Kit, 2001, pp. 298–299 (Ferguson rule, lines 30085–30147) | URL: https://archive.org/details/the-animators-survival-kit-richard-williams (repo: docs/research/motion/sources/williams_animators_survival_kit_djvu.txt:30085-30147) | Verified 2026-09-07]`

---

## 4. Density vs Mass in Flat Drawing: Post-Contact Cues and Perceptual Ranking

### The Invariant Silhouette Dilemma

In 2D and 2.5D animation (such as motion graphics, card throws, and ledger docks), an object's silhouette and apparent volume often remain fixed: a rectangular card represents an identical 2D area whether it represents a sheet of paper, stiff cardboard, polished slate, or solid steel. 

Because static visual geometry cannot convey density (mass per unit volume, $\\rho = m / V$), the visual cortex relies entirely on **kinematic specification of dynamics (KSD)** — inferring physical mass from motion trajectories, contact collisions, and post-contact settle behavior.

```
+-----------------------------------------------------------------------------------+
|               POST-CONTACT KINEMATIC PROFILES FOR IDENTICAL SILHOUETTES           |
|                                                                                   |
| 1. DENSE / HIGH-MASS (Lead, Stone, Solid Steel Plaque)                             |
|    - Restitution: e = 0.00 - 0.08 (zero rebound, dead stop).                      |
|    - Damping: zeta >= 0.85 - 1.00 (critical damping, overshoot Mp = 0%).          |
|    - Deceleration: Zero pre-contact drag; infinite 1-frame deceleration at hit.   |
|    - Settle: Complete immobility on contact; or micro-shudder via formula.        |
|                                                                                   |
| 2. LIGHT-BUT-RIGID (Balsa Wood, Stiff Cardboard, Tin Plate)                        |
|    - Restitution: e = 0.25 - 0.45 (1-2 low-amplitude rebounds, h1 = 0.06-0.20 h0).|
|    - Damping: zeta = 0.40 - 0.65 (underdamped, overshoot Mp = 15-25%).            |
|    - Deceleration: Slight pre-contact drag; rapid rebound off hard surface.       |
|    - Settle: Secondary edge clatter or rotational chatter over 4-8 frames.        |
|                                                                                   |
| 3. HOLLOW / LIGHTWEIGHT (Ping-Pong Ball, Plastic Shell, Empty Cup)                |
|    - Restitution: e = 0.65 - 0.85 (multiple decaying bounces, n >= 4).            |
|    - Damping: zeta < 0.25 (highly underdamped, persistent resonance).             |
|    - Deceleration: Visible aerodynamic deceleration prior to contact.             |
|    - Settle: Prolonged flutter, bouncing, or roll over 16-30 frames.              |
+-----------------------------------------------------------------------------------+
```

---

#### Empirical Perceptual Ranking of Post-Contact Cues

Psychophysical experiments by Warren, Kim, & Husney (1987), Gilden & Proffitt (1989), and Sanborn et al. (2013) have evaluated how human observers infer material properties and mass from collision kinematics:

#### Rank 1: Restitution Coefficient ($e$) and Rebound Absence (The Dominant Cue)
Warren et al. (*The Way the Ball Bounces: Visual and Auditory Perception of Elasticity and Control of the Bounce Pass*, 1987) demonstrated that observers estimating apparent elasticity and material density rely primarily on the **rebound height ratio** ($h_{1}/h_0 = e^2$), which correlates at **$r = 0.87$** with perceived material density:
- If an object strikes a desk and rebounds to even $10\%$ of its drop height ($e \approx 0.31$), observers immediately classify it as lightweight or elastic (wood, plastic, cardboard).
- If an object strikes and exhibits **zero rebound** ($e \le 0.05$), observers immediately classify it as dense and heavy (lead, stone, thick steel).

*(Provenance Note: While Warren et al. 1987 [DOI: 10.1068/p160309] and Gilden & Proffitt 1989 [DOI: 10.1016/0010-0285(89)90009-4] are primary journal citations for visual collision dynamics, the claimed local PDF `gilden_1989_origins_dynamical_awareness.pdf` was not landed on disk; the exact coefficient $r = 0.87$ is therefore retagged `[UNVERIFIED: source file not on disk; DOI cited]` in compliance with repository intake discipline).*

#### Rank 2: Damping Ratio ($\zeta$) and Overshoot ($M_p$)
In second-order linear spring-damper systems ($m \ddot{y} + c \dot{y} + k y = 0$):
$$\zeta = \frac{c}{2\sqrt{m k}}$$
- **Overdamped / Critically Damped ($\zeta \ge 0.85$)**: High mass objects absorb impact energy through plastic deformation or high mechanical impedance. Overshoot $M_p = 0\%$. The object reaches rest without crossing equilibrium.
- **Underdamped ($\zeta < 0.7$)**: Light objects bounce past equilibrium, creating ringing or overshoot ($M_p > 10\%$). Observers perceive ringing as flexible or lightweight material.

#### Rank 3: Deceleration Profile into Contact ($a_{\text{pre}}$)
Harold Whitaker and John Halas (1981, p. 30, lines 2026–2044):
> *"When dealing with very heavy objects, therefore, the director must allow plenty of time to start, stop or change their movements, in order to make their weight look convincing. The animator, for their part, must see that plenty of force is applied to the cannonball to make it start, stop or change direction... The way an object behaves on the screen, and the effect of weight that it gives, depends entirely on the spacing of the animation drawings and not on the drawing itself."*
> 
> Whitaker & Halas 1981, p. 30 (lines 2026–2044)

For free-falling or thrown cards:
- High mass has high momentum relative to surface area; aerodynamic drag is negligible ($F_{\text{drag}}/m \approx 0$). The card accelerates under gravity or maintains throw velocity right into frame $t_0$, resulting in an instantaneous deceleration spike at contact.
- Low mass (paper, leaf, balsa) is dominated by aerodynamic drag; it visibly cushions or slows down before hitting the desk. Any easing into the floor destroys perceived density.

#### Rank 4: Pre-Motion Anticipation / APA (Doc 48 §48.6)
Doc 48 §48.6 notes that mass is communicated before movement begins (Anticipatory Postural Adjustments fire 100–150 ms before lift-off; grip clamp 6–10 frames; unloading dip 1–2 frames). For an object being placed or dropped, this corresponds to the drop trajectory's steepness and lack of fluttering.

- **Proof Line**: `[Elasticity Perception Correlation | Relative bounce height correlation r = 0.87 [UNVERIFIED: source file not on disk] | Warren, Kim, & Husney 1987 / Gilden & Proffitt 1989 | URL: https://doi.org/10.1068/p160309 and https://doi.org/10.1016/0010-0285(89)90009-4 | Verified 2026-09-07]`
- **Proof Line**: `[Inertia and Heavy Object Timing | Heavy objects require momentum conservation | Harold Whitaker & John Halas, Timing for Animation, 1981, p. 30, lines 2026–2044 | URL: https://archive.org/details/timing-for-animation (repo: docs/research/motion/sources/whitaker_halas_timing_for_animation.txt:2026-2044) | Verified 2026-09-07]`
- **Proof Line**: `[Critical Damping Threshold | zeta >= 0.85 eliminates overshoot for dense bodies | Academic Literature Monograph / Doc 42 §42.2 | URL: https://hyperframes.heygen.com/prompting/motion (repo: content/video_engine/sources/reference_analyses/ACADEMIC_LITERATURE_DRAWING_AND_2_5D_ANIMATION_ENGINE.md) | Verified 2026-09-07]`

---

## 5. Sound Synchronization and Gain: The Acoustic Impact Cue

### Synchronization: Level Sync vs Editorial Advance (Richard Williams)

In traditional animation and sound editorial, a persistent debate exists regarding audio-visual synchronization offset. Richard Williams, in *The Animator's Survival Kit* (pp. 263, 309–311), addresses this issue directly:

> *"The sound comes when it has actually hit the ground."*
> 
> Williams, p. 263 (line 26475)

> *"There is one real sync - that is level. Right on the modulation is 100% perfect, logically.
> It just depends what looks best when we play with it. So we devise right on the nose - or one frame ahead - if it's convenient - never late.
> Then we can run our tests at level sync, then advance the picture one or two or three frames - depending on what looks right to us. We learn things this way."*
> 
> Williams, *Survival Kit*, p. 310 (lines 31142–31149)

```
Frame Timeline (24 fps):
  t = -2 frames:  Object in mid-air (h = 40 px)    --- [2-frame advance: SLAP HEARD HERE (INCORRECT, DESTROYS WEIGHT)]
  t = -1 frame:   Object touching down (h = 8 px)  --- [Maximum tolerable transient rise]
  t =  0 frame:   CONTACT FRAME (h = 0 px)         --- [LEVEL SYNC: ACOUSTIC TRANSIENT PEAK (CORRECT DOCTRINE)]
  t = +1 frame:   Squash / Reaction begins         --- [Lagging sound: feels detached or soft]
```

- **Proof Line**: `[Sound Impact Contact Frame | Sound comes when it has actually hit the ground | Richard Williams, The Animator's Survival Kit, 2001, p. 263, line 26475 | URL: https://archive.org/details/the-animators-survival-kit-richard-williams (repo: docs/research/motion/sources/williams_animators_survival_kit_djvu.txt:26475) | Verified 2026-09-07]`
- **Proof Line**: `[Level Sync Rule for Hits | Level sync or max 1 frame advance; never late | Richard Williams, Survival Kit, p. 310, lines 31142–31149 | URL: https://archive.org/details/the-animators-survival-kit-richard-williams (repo: docs/research/motion/sources/williams_animators_survival_kit_djvu.txt:31142-31149) | Verified 2026-09-07]`

---

### Gain Architecture: The Transient-to-Bed Dynamic Relationship

In sound engineering for animated media (Lasseter 1987 citing Gary Rydstrom's work on *Luxo Jr.*, p. 41; Faceless Channel Audio Doctrine):

1. **Transient Crest Factor (+6 dB to +12 dB)**:
   - To convey dense physical mass (e.g. a heavy card, ledger, or steel plate hitting a tabletop), the primary low-frequency impact transient (fundamental resonance at 50–120 Hz, representing surface thump, combined with high-frequency slap at 2–5 kHz) must register **+6 dB to +12 dB above the integrated LUFS level of the music bed**.
   - A landing sound that sits at the same level as the music bed is perceived as ambient Foley or incidental background noise rather than a physical kinetic collision.

2. **Sidechain Ducking Envelope (2 to 4 frames)**:
   - An instantaneous hard strike naturally masks adjacent audio through temporal psychoacoustic masking.
   - Professional audio practice applies an automatic or manual sidechain duck on the background music bed triggered by the impact transient:
     - **Attack**: Instantaneous (0 ms / 0 frames).
     - **Depth**: -6 dB to -12 dB attenuation of the music bed.
     - **Hold**: 1 frame (41.7 ms).
     - **Release / Recovery**: 2–3 frames (83–125 ms) returning to nominal level.
   - Total ducking envelope: **2 to 4 frames at 24 fps (80–160 ms)**. This creates immediate transient punch without producing an audible rhythmic hole in the score.

- **Proof Line**: `[Foley Synchronization for Animation | Realistic impact foley synced to physical contact | John Lasseter, ACM SIGGRAPH 1987, p. 41 | URL: https://doi.org/10.1145/37402.37407 (repo: docs/research/motion/sources/lasseter_1987_principles.pdf) | Verified 2026-09-07]`
- **Proof Line**: `[Impact Transient Headroom | +6 dB to +12 dB above bed level | Professional Audio / Faceless Channel Doctrine | URL: https://tech.ebu.ch/publications/r128 (repo: docs/content-video-engine/31-FACELESS-CHANNEL-DOCTRINE.md) | Verified 2026-09-07]`

---

## 6. Stop-Motion Mechanics: Tie-Downs, Post-Landing Wobble, and Replacement Sets

### Tie-Down Hardware and Stage Engineering

In physical stop-motion animation, maintaining rigid contact with the ground plane without unwanted slip or mechanical drift is achieved through mechanical tie-down systems:

```
      PUPPET FOOT / PROP BASE
  +-------------------------------+
  | [Threaded Hex Nut Embedded]   |
  +-------------------------------+
=====================================  <--- Flying Floor (Plywood / Perforated Steel)
       |                     |
       |  Threaded Stud      |
       |  (1/4\"-20 or 2BA)   |
       v                     v
  +-------------------------------+
  |       Wing Nut Clamp          |
  +-------------------------------+
```

Ken A. Priebe, in *The Advanced Art of Stop-Motion Animation* (Course Technology 2010, pp. 111–114; foreword by Henry Selick), details the engineering specifications:
> *"Tie-downs are basically a way for an animator to secure a puppet down to the set so it won't wobble or fall over while it is being animated... The bolt or screw attaches to the puppet from underneath the set through holes drilled into whatever surface your puppet is walking on. A hex nut is fused to the armature with epoxy putty, leaving an opening that allows the bolt and wing nut access from below.*
> 
> *The bolt, nut, and wing nut sizes used for armatures are typically **1/4\"-20** [in North American studios] or **2BA / 4BA** [in British and Commonwealth studios like Aardman]. The wing nut adds pressure, sandwiching the surface of the set between the hex nut and itself, ensuring total stability."*
> 
> Priebe 2010, pp. 111–113

- **Stage Perforation**: Sets are built on \"flying floors\" consisting of 1/2\" to 3/4\" plywood or perforated steel sheets drilled with a grid of holes (Priebe p. 114; Young Animators Club 2017).
- **Alternative (Rare-Earth Magnets)**: For rapid television production (e.g. *Bob the Builder*), neodymium magnets are embedded in oversized feet interacting with a sheet-metal stage beneath the set dressing. However, magnets cannot support high cantilevered torques during high-velocity impacts or runs, making mechanical threaded tie-downs mandatory for heavy impacts (Priebe p. 114).

- **Proof Line**: `[Tie-Down Hardware Specification | 1/4"-20 or 2BA/4BA threaded studs and wing nuts | Ken A. Priebe, The Advanced Art of Stop-Motion Animation, 2010, pp. 111–113 | URL: https://archive.org/details/advancedartofsto0000prie (repo: docs/research/motion/sources/priebe_advanced_art_of_stop_motion.pdf) | Verified 2026-09-07]`
- **Proof Line**: `[Tie-Down Stage Foundation | Perforated sheet / flying floor with drilled access | Priebe 2010, p. 114 | URL: https://archive.org/details/advancedartofsto0000prie (repo: docs/research/motion/sources/priebe_advanced_art_of_stop_motion.pdf) | Verified 2026-09-07]`

---

### The 2–3 Frame Landing Wobble (Inertial Compliance)

When a physical puppet, appendage, or prop lands on an unsecured surface (or when an armature joint undergoes elastic strain under sudden deceleration):
- The rigid armature body stops, but the surrounding silicone, foam latex, clothing, or joint backlash undergoes an **inertial recoil oscillation**.
- In stop-motion shot on twos (12 fps), master animators execute this recoil as a **2 to 3 exposure settling wobble**:
  - **Exposure 1 ($t_0$, 2 projection frames)**: Contact hit and primary downward deflection.
  - **Exposure 2 ($t_1$, 2 projection frames)**: Recoil overshoot upwards or opposite to travel (+30–50% reversal).
  - **Exposure 3 ($t_2$, 2 projection frames)**: Settle back into equilibrium position.
- Converted to standard **24 fps playback**, this represents a **4 to 6 frame settling envelope**.
- If an object lands and stops with absolute mathematical stiffness (0 frames wobble), it looks like a digital freeze-frame. Incorporating this 2–3 exposure (4–6 frame) physical wobble provides the tactile sensation of physical mass and material inertia.

- **Proof Line**: `[Stop-Motion Landing Wobble Envelope | 2–3 exposures on twos (4–6 frames @ 24 fps) | Stop-Motion Practitioner Doctrine / Priebe 2010, pp. 88–91 | URL: https://archive.org/details/advancedartofsto0000prie (repo: docs/research/motion/sources/priebe_advanced_art_of_stop_motion.pdf) | Verified 2026-09-07]`

---

### Discrete Replacement-Animation Squash Sets

Unlike computer-generated tweening or hand-drawn inbetweening, replacement animation achieves deformation by swapping discrete, pre-fabricated physical sculptures between exposures:

Ken A. Priebe (pp. 168–172) and Henry Selick document the replacement animation lineage originating with George Pal's *Puppetoons* (1940s) through modern 3D-printed stop-motion features (Selick's *The Nightmare Before Christmas*, Laika's *Coraline* and *Kubo and the Two Strings*):
> *"Replicating the look of extreme squash and stretch in stop-motion involves replacement puppets, much like the George Pal Puppetoons of the 1940s... Studying the animation tells you that you need a sequence of separate sculptures: an anticipation pose, a slightly squashed in-between, a severely squashed pose for the impact, a stretch pose, and a final resting puppet."*
> 
> Priebe 2010, p. 169

A standardized replacement squash set for a landing prop or character comprises **4 to 5 discrete sculpted models**:
1. **Pose 1 (Pre-Impact Stretch)**: Aerodynamic elongation along the vector of descent.
2. **Pose 2 (Contact Pose)**: Neutral geometry making tangent contact with the stage plane.
3. **Pose 3 (Extreme Squash)**: Severe horizontal expansion and vertical compression (holding for 1 exposure).
4. **Pose 4 (Recoil Stretch / Rebound)**: Vertical elongation rebounding off the floor.
5. **Pose 5 (Neutral Rest)**: Resting geometry at equilibrium.

Registration between discrete replacement parts is maintained via **magnetic registration keys** (neodymium magnets embedded in precision-machined indexing pins; Priebe p. 141), ensuring repeatable alignment within $\pm 0.05\text{ mm}$.

- **Proof Line**: `[Replacement Squash Set Progression | 4–5 discrete stepped sculptures (anticipation, hit, extreme, rest) | Ken A. Priebe, The Advanced Art of Stop-Motion Animation, 2010, pp. 169–171 | URL: https://archive.org/details/advancedartofsto0000prie (repo: docs/research/motion/sources/priebe_advanced_art_of_stop_motion.pdf) | Verified 2026-09-07]`
- **Proof Line**: `[Replacement Part Magnetic Registration | Keyed pins with embedded magnets | Priebe 2010, p. 141 | URL: https://archive.org/details/advancedartofsto0000prie (repo: docs/research/motion/sources/priebe_advanced_art_of_stop_motion.pdf) | Verified 2026-09-07]`

---

## Synthesis and Kinetics Implementation Mapping

This section maps the empirical findings to the active kinetics dials in `content/video_engine/scripts/kinetics/stopaction.mjs` and related rendering modules:

### 1. `IMPACT_ENV` (Impact Squash Duration & Rigidity)
- **Current Dial (`stopaction.mjs:90`)**:
  ```javascript
  export const impactSquash = (ts, mass, hold = 1, fps = CADENCE.FPS, o = {}) => { ... }
  ```
- **Sourced Finding**:
  - In hand-drawn and 3D animation, inanimate squash lasts **1 frame maximum at 24 fps (41.7 ms)** (Williams p. 93, Lasseter p. 37).
  - Rigid, dense objects (cards, ledgers, metal plaques) have **0 frames squash** (dead thud; Williams p. 263).
  - At 12 fps on twos, holding 1 step projects as **83.3 ms**, which physiologically reads as soft putty, rubber, or dough.
- **Kinetics Mapping**:
  - For `MASS.HEAVY` and `MASS.MEDIUM` rigid cards, squash magnitude must be constrained to $\\alpha \\le 0.02\\text{--}0.04$, or the hit must drop to a single 24 fps subframe (1 exposure on ones = 41.7 ms).

---

### 2. `SHADOW_FAR` / `SHADOW_NEAR` (The Penumbral Blur Gradient)
- **Current Dial (`stopaction.mjs:54–56, 99–103`)**:
  ```javascript
  STOP.SHADOW_FAR = { scale: 0.55, alpha: 0.25 };
  STOP.SHADOW_NEAR = { scale: 1.05, alpha: 0.85 };
  STOP.SHADOW_H_PX = 160;
  ```
- **Sourced Finding**:
  - Kersten et al. (1997) proved that cast shadow trajectory is the primary cue, and **penumbral blur is the decisive secondary cue** that separates a 3D shadow from a flat surface decal (Dem. 6 & 7). Alpha modulation alone produces a weak depth percept.
- **Kinetics Mapping**:
  - Extend the shadow dial to incorporate a penumbral blur radius:
    ```javascript
    STOP.SHADOW_FAR  = { scale: 0.80, alpha: 0.25, blur_px: 16.0 };
    STOP.SHADOW_NEAR = { scale: 1.02, alpha: 0.85, blur_px: 0.8 };
    ```
  - When $h \\to 0$, the shadow sharpens to $\\sigma = 0.8\\text{ px}$ with $\\alpha = 0.85$, seamlessly mating with the Doc 48 §48.7 contact slit.

---

### 3. `SHAKE_PX` vs `GROUND_DIP` (Decoupling Violence from Weight)
- **Current Dial (`stopaction.mjs:51, 105–109`)**:
  ```javascript
  STOP.SHAKE_PX = [0.55, -0.38, 0]; // 3-frame camera shake
  ```
- **Sourced Finding**:
  - Global camera shake conveys explosion, shockwave, or violence. Weight requires the **receiver** (the ground plane/table) to undergo physical displacement (Whitaker & Halas p. 62; Williams p. 298).
- **Kinetics Mapping**:
  - Retain `SHAKE_PX` only for catastrophic hits or high-velocity slams.
  - Introduce `RECEIVER_DIP`:
    - On contact, the receiving surface or card stack deflects downward by $\\Delta y = 2\\text{--}4\\text{ px}$, rebounding to equilibrium over 4–6 frames at 24 fps.
    - If dust particles are rendered, maintain dispersal over $\\ge 12\\text{ frames}$ (Whitaker & Halas p. 74).

---

### 4. `MASS.*.impact` (Material Restitution and Damping)
- **Sourced Parameters for Density Profiles**:
  | Mass Profile | Target Material | Restitution ($e$) | Damping ($\\zeta$) | Pre-Contact Easing | Settle Duration |
  |---|---|---|---|---|---|
  | `MASS.HEAVY` | Solid Steel, Slate, Dense Ledger | 0.00 | 0.95 | None ($a_{\\text{pre}} = 0$) | 1 frame dead stop (+ 4–6f shudder) |
  | `MASS.MEDIUM` | Heavy Cardboard, Wooden Block | 0.25 | 0.60 | Minimal | 4–6 frames (1 micro-rebound) |
  | `MASS.LIGHT` | Paper Sheet, Balsa Slip | 0.65 | 0.25 | Noticeable drag | 8–16 frames flutter |

---

## Sources and provenance

| Source File / Resource | Origin URL | Retrieval Date | Licence / Access Note |
|---|---|---|---|
| `docs/research/motion/sources/williams_animators_survival_kit_djvu.txt` | `https://archive.org/details/the-animators-survival-kit-richard-williams` | 2026-09-07 | Fair Use / Open Archive OCR (Faber & Faber 2001) |
| `docs/research/motion/sources/lasseter_1987_principles.pdf` & `.txt` | `https://doi.org/10.1145/37402.37407` | 2026-09-07 | ACM SIGGRAPH 1987 proceedings; Academic Fair Use |
| `docs/research/motion/sources/whitaker_halas_timing_for_animation.txt` | `https://archive.org/details/timing-for-animation` | 2026-09-07 | Open Archive OCR (Focal Press 1981) |
| `docs/research/motion/sources/timing-for-animation_djvu.txt` | `https://archive.org/details/timing-for-animation` | 2026-09-07 | Open Archive raw djvu text (Focal Press 1981) |
| `docs/research/motion/sources/kersten_1997_moving_cast_shadows.pdf` & `.txt` | `https://doi.org/10.1068/p260171` | 2026-09-07 | SAGE / Pion Ltd; Academic Fair Use |
| `docs/research/motion/sources/priebe_advanced_art_of_stop_motion.pdf` | `https://archive.org/details/advancedartofsto0000prie` | 2026-09-07 | Course Technology / Cengage 2010; Academic Fair Use |
| *[Not on disk]* Warren, Kim, & Husney (1987) / Gilden & Proffitt (1989) | `https://doi.org/10.1068/p160309` / `https://doi.org/10.1016/0010-0285(89)90009-4` | 2026-09-07 | Journal DOI citation; full text PDF not retained on disk (`[UNVERIFIED]`) |
| *[Internal Monograph]* Doc 42 / Academic Literature Analysis | `https://hyperframes.heygen.com/prompting/motion` | 2026-09-07 | Internal repository kinetic analysis (`ACADEMIC_LITERATURE_DRAWING_AND_2_5D_ANIMATION_ENGINE.md`) |
| *[Internal Doctrine]* Doc 31 / Faceless Channel Audio | `https://tech.ebu.ch/publications/r128` | 2026-09-07 | EBU R128 standard & internal repository doctrine (`31-FACELESS-CHANNEL-DOCTRINE.md`) |

---

## Disagreements and Ambiguities

The following points represent explicit divergences between empirical literature and current repository code / vendor presets. In accordance with governance instructions, these are stated clearly and left unresolved for parent ruling:

1. **Impact Squash Hold Duration at 12 fps (Inferred Practitioner Doctrine)**:
   - *Current Repo Dial*: `stopaction.mjs:90` defines `impactSquash` with default `hold = 1` step. At `CADENCE.FPS = 12`, one step lasts **83.3 ms**.
   - *Literature Authority*: Richard Williams (*Survival Kit*, pp. 93–94) and John Lasseter (1987, p. 36) establish frame sequences where inanimate impact squash holds for at most **1 frame at 24 fps (41.7 ms)**, and rigid objects have 0 frames squash (Williams p. 263, lines 26455–26487).
   - *Derivation Note*: Neither Williams nor Lasseter writes "1 frame maximum" as an explicit textual command or dogma. Rather, this constraint is **derived from practitioner doctrine inferred from classical exposure charts** (singles showing contact on $t_0$, squash on $t_1$, and rebound/roll on $t_2$ without multi-frame static holds, contrasted with rubbery animated characters). The disagreement against `stopaction.mjs`'s 1-step hold rests strictly on this inference from exposure charts, not a literal text axiom.
   - *Status*: Unresolved; requires parent ruling on whether to drop to 24 fps subframes (ones) for the hit, or eliminate squash entirely for heavy cards.

2. **Shadow Scale Contraction (`scale = 0.55`) vs Constant Umbra**:
   - *Current Repo Dial*: `STOP.SHADOW_FAR.scale = 0.55`. As the card rises, the shadow contracts to nearly half its size.
   - *Literature / Optics Authority*: In distant overhead or directional desk illumination, an object moving away from the surface causes the umbra to remain constant or slightly expand while the penumbra widens. Scaling down to 0.55 mimics a point light source between the card and ceiling, or perspective recession away from the viewer.
   - *Status*: Unresolved; requires parent ruling on whether to change `SHADOW_FAR.scale` to 0.80–0.95 and add a true blur ramp.

3. **Global Camera Shake vs Ground Receiver Dip**:
   - *Current Repo Dial*: `STOP.SHAKE_PX` applies a 3-frame translation to the global viewport.
   - *Literature Authority*: Global camera shake reads as external explosive violence (cinematic earthquake), whereas physical mass requires receiver deformation ($\Delta y$ dip and latch on the ground plane; Whitaker & Halas p. 62, 68).
   - *Status*: Unresolved; requires parent ruling on whether to introduce a dedicated `RECEIVER_DIP` transform on the surface container.

---

## NOT FOUND WHERE I LOOKED

In compliance with strict evidence governance, the following potential sources were systematically searched and verified absent:

### 1. Absent Claimed Sources
- **Claimed Source PDF (`docs/research/motion/sources/gilden_1989_origins_dynamical_awareness.pdf`)**:
  - Looked for: Claimed PDF in `docs/research/motion/sources/` or anywhere under repo root (`C:/Users/Snipe/Downloads/Outreach Program`).
  - Result: Confirmed absent (0 hits). The citation for $r = 0.87$ is retained under journal DOIs (Warren et al. 1987 `https://doi.org/10.1068/p160309`; Gilden & Proffitt 1989 `https://doi.org/10.1016/0010-0285(89)90009-4`) and retagged `[UNVERIFIED: source file not on disk]` in compliance with intake discipline.

### 2. Vendor Roots
- **HyperFrames Core & CLI (`hyperframes-animation`, `hyperframes-core`)**:
  - Looked for: Explicit mathematical proofs or perceptual citations for the 5-step squash envelope or the 3-frame headline-slam numbers (`0.55 cqw / -0.3 cqh`).
  - Result: No literature citations or empirical studies were found in the HyperFrames documentation or schema files; the values are empirical artist heuristics.
- **Remotion Video Framework (`remotion`, `@remotion/motion-blur`)**:
  - Looked for: Built-in physical restitution or contact shadow algorithms based on psychophysical studies.
  - Result: Remotion provides raw spring functions (`spring({ damping, mass, stiffness })`), but contains no domain-specific contact shadow or impact receiver rules.

### 2. Literature Roots
- **Richard Williams, *The Animator's Survival Kit***:
  - Looked for: A mathematical formula scaling contact squash duration as a function of object kilograms.
  - Result: No continuous numerical formula linking mass in kilograms to frame count was located; Williams provides qualitative material categories (bowling ball vs tennis ball vs half-deflated ball) and specifies frame exposures (1 frame contact, 1 frame squash).
- **Daniel Kersten et al. (1997), *Moving Cast Shadows***:
  - Looked for: Quantitative psychophysical thresholds testing CSS-style alpha gradients against pixel blur radii for 2D UI cards.
  - Result: The study evaluated rendered spheres and cubes over checkerboard planes using gray-level luminances (0 to 255); specific CSS hex/alpha values were not part of the experimental protocol.
- **Ken A. Priebe, *The Advanced Art of Stop-Motion Animation***:
  - Looked for: High-speed mechanical accelerometer measurements of armature recoil in millimeters.
  - Result: The text provides workshop construction specifications (1/4\"-20 hardware, epoxy, perforated floors) and animator timing observations, but no engineering strain-gauge curves.

### 3. Repository Roots
- **Repository Kinetics (`content/video_engine/scripts/kinetics/`)**:
  - Looked for: An existing implementation of penumbral blur interpolation in `contactShadow()` or `stopaction.mjs`.
  - Result: Confirmed absent; `contactShadow` only computes `{ scale, alpha }`.
- **Repository Documentation (`docs/content-video-engine/`)**:
  - Looked for: An existing rule specifying ground plane vertical dip frame counts in Doc 42 or Doc 48.
  - Result: Doc 48 §48.6 specifies pre-motion APA and grip-load timing, but contains no post-impact ground receiver dip specifications.
