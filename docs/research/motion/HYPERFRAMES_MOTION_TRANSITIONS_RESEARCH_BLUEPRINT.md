# HyperFrames Motion, Transitions, and Kinetic Transformations — Research Blueprint

*Pass-3 deep extraction · 2026-09-06 · sources: HeyGen HyperFrames official documentation (overview, motion, transitions, storyboards, capstone, rules-and-anti-patterns), Remotion documentation, GreenSock, SIGGRAPH literature · for: video engine motion, transitions & drawing doctrine*

## The question

How does HeyGen HyperFrames structure motion design, scene transitions, stop-motion physics, and transformations, and how can these patterns be formalized, deduplicated, and unified with Remotion, GSAP, and our 2.5D Ledger Page drawing doctrine? Specifically, how do we solve the "slideshow failure mode" (isolated scenes that feel like independent slides), eliminate unsourced transition constants, and ensure deterministic, reproducible animation across both continuous and stepped (on-twos) workflows?

## Verdict up front

**Motion is an epistemic claim, not a decorative layer.** When a video feels cheap or disconnected, the instinct is to add transitions or amplify movement. HyperFrames decisively demonstrates that more movement without semantic motivation increases cognitive friction and creates a "slideshow" effect.

1. **The Four Functions of Video Motion:** Movement can only honestly do four things in video: (1) *Direct attention*, (2) *Carry continuity*, (3) *Show change*, and (4) *Express character*. If an animation cannot finish the sentence *"This moves because..."*, it must be cut.
2. **Solving the Slideshow:** A sequence of well-animated scenes still plays like a slideshow if scenes are independent and uniform in energy. The architectural fix requires:
   - **Persistent Elements:** At least one visual element (a baseline ruler, a data wire, a hero prop, or a HUD frame) that crosses the seam continuously.
   - **The Dwell-and-Sweep Camera Rhythm:** The camera sweeps across spaces between beats, but comes to a genuine **1.5–2.5 second rest (dwell)** at each hero moment. During a dwell, the *camera* rests while the *world* continues resolving (numbers tick, status indicators pulse, secondary motion lives).
3. **Seeded Stop-Motion Determinism:** True hand-drawn or stop-motion cadence (on-twos / 12fps) requires quantizing motion to the **integer frame index** rather than the time domain, driven by a seeded 32-bit PRNG (Mulberry32). Time-domain quantization (`t / 0.0667`) drifts due to floating-point imprecision, causing irregular stutter.
4. **WebGL Shader vs CSS Transitions:** HyperFrames introduces 14 typed WebGL shader transitions (`@hyperframes/shader-transitions`) for high-impact structural handoffs, while delegating 60–70% of standard scene continuations to lightweight CSS container transforms. The cardinal failure mode is fading scene A out to black/cream and then fading scene B in; transitions must be simultaneous handoffs.
5. **Cross-Engine Interoperability:** Remotion's `<TransitionSeries>` (`@remotion/transitions`) and HyperFrames' `@hyperframes/shader-transitions` share identical underlying mathematics: both drive a normalized progress scalar ($p \in [0, 1]$) through a deterministic seek clock (`seekFrame(n)` vs `useCurrentFrame()`).

---

## 1. The Core Law: Every Movement Makes a Claim

In video production, viewers unconsciously interpret every kinematic displacement as a physical or informational statement:
- A number that breathes asserts that the metric is live and actively streaming.
- An element entering from screen-right asserts that more content exists offscreen in that direction.
- An overshoot assert that the object has physical mass and inertia.
- A sudden freeze asserts that the data feed has disconnected.

[Four allowable motion jobs in video | 4 functions (Direct attention, Carry continuity, Show change, Express character) | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/motion | Verified 2026-09-06]

**The Litmus Test:** Every declared movement must complete a definitive rationale:
$$\text{Motion Justification} = \text{"[Element] moves by [Vector] because [Data/Narrative Cause]"}$$
If the sentence cannot be completed, the motion is decorative noise and must be eliminated.

---

## 2. The Eight Rules of Motion

HyperFrames formalizes an eight-rule grammar governing execution within a scene. Each rule has an exact measurable standard:

### Rule 1 — Nothing Ever Fully Stops
Every static "hold" must carry a subtle ambient idle: a 1–2% breathing scale, a slow directional drift, or a soft luminescence pulse. A bit-identical freeze frame across the final 1–2 seconds is the single most prevalent indicator of amateur production.
[Final second encoder size difference | 211 KB (frozen) vs 2.5 MB (ambient live idle) | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/motion | Verified 2026-09-06]

### Rule 2 — The Camera is an Actor
Every scene must maintain a continuous camera movement: a 4–8% push-in, a slow orbital pan, or parallax translation. Camera motion must never decay to a dead stop at the scene boundary; eases must be computed over a temporal window slightly longer than the render span. Translating the entire scene content past a fixed viewport is mathematically identical to camera translation.

### Rule 3 — Overlapping Action
No two elements may share an identical start frame or end frame. Entrances must stagger at irregular offsets.
- **The Stagger Ratio:** Each offset must be strictly shorter than the duration of the animation it offsets:
  $$\tau_{\text{offset}} < \tau_{\text{duration}}$$
  If $\tau_{\text{offset}} \ge \tau_{\text{duration}}$, the animation ceases to be a stagger and degrades into a sequential queue.
- **Focal Priority:** Delay supporting background elements; never delay the focal element. A focal element that hesitates reads as system latency or lag.

### Rule 4 — Compound Properties Only When Telling One Story
Animate multiple properties (position, scale, opacity, rotation) simultaneously only if they reinforce a single physical claim. Combining translation with opacity communicates "arrival." Stacking translation, rotation, scale, and blur creates visual smearing and degrades legibility.
- **Directional Easing Grammar:**
  - *Entrances:* Ease **out** (fast entry, gentle deceleration into rest).
  - *Exits:* Ease **in** (gradual start, decisive departure).
  - *On-screen state shifts:* Ease **in-out**.
  - *Impacts / Stamps:* Ease **in** (acceleration culminating at contact).

### Rule 5 — Overshoot and Follow-Through
Overshoot communicates mass and kinetic momentum. Objects pass their resting target and settle back via spring or `back.out` physics.
- **One-Frame Shadow Lag:** Dragged secondary elements (e.g. drop shadows, trailing brackets, support housings) must settle exactly **one frame later** than the primary object (a lag of 0.033s at 30 fps).
- **The Numerical Metric Invariant:** Overshoot applies strictly to spatial transforms. **A numerical metric or financial counter must NEVER overshoot its target value.** An overshoot on a counter displays a figure that was never true, violating factual integrity.
[Physical shadow follow-through lag | 0.033 s (exactly 1 frame at 30 fps) | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/motion | Verified 2026-09-06]

### Rule 6 — Depth Planes and Occlusion Proofs
Scene layers must translate at rates proportional to their virtual z-depth:
- Far background: $0.20\times$ camera rate.
- Main content: $1.00\times$ camera rate.
- Foreground element: $6.00\times$ camera rate.
[Multi-plane parallax displacement ratios | 0.20x background / 1.00x content / 6.00x near-plane | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/motion | Verified 2026-09-06]
The definitive cue for spatial depth is **occlusion** (a foreground element passing directly in front of and clipping behind-layer content), not Gaussian blur. A single blurred foreground occlusion element definitively establishes 3D spatial separation.

### Rule 7 — Match Pacing to Genre
Showreel and fast-paced mobile shorts operate at **1.1 to 4.0 seconds per idea/beat**. Stretching an idea to 8 seconds produces perceptual lethargy regardless of ease fluidity.

### Rule 8 — Handmade Imperfection Stays Reproducible
Handmade, woodblock, paper-cutout, or stop-motion aesthetics require discrete stepped holds (on-twos). To prevent non-deterministic render corruption, unseeded `Math.random()` is banned. Imperfections must be driven by a seeded PRNG (Section 5).

---

## 3. Avoiding the Slideshow: Continuity and Energy Contrast

A multi-scene composition where each card enters, holds, and exits cleanly inevitably degrades into a "slideshow." This failure stems from two architectural deficits: (1) scenes are structurally independent, and (2) energy is uniform.

```
SLIDESHOW DEFECT (Anti-Pattern):
[ Scene 1: Enters -> Sits -> Fades ] -> [ Scene 2: Enters -> Sits -> Fades ] -> [ Scene 3: ... ]
Result: Viewer re-orients at every boundary; reads as disconnected slides.

CONTINUOUS WORLD-CAMERA (HyperFrames Standard):
[ World Track: Scene 1 ======= Wire / Horizon Line Crosses Seam =======> Scene 2 ]
               |                                                              |
          [DWELL 1.8s]                                                  [DWELL 2.0s]
          Camera rests                                                  Camera rests
          Counters tick                                                 Data renders
```

### The Cinematography Contract (The Unbroken Camera):
The fix for the slideshow defect is not more animation, but a strict **cinematography contract**:

1. **Regions Change by Arriving, Not Cutting:**
   - The next region is already visible at the edge of frame before the camera reaches it.
   - The previous region leaves via **parallax**, not by fading out.
   - Fading an outgoing card to black or cream and fading the incoming card in creates a 2-frame perceptual dip ("black hole cut") that resets viewer orientation.

2. **The Dwell-and-Sweep Camera Rhythm:**
   The camera accelerates across the transition seam between regions, then settles into a **1.5 to 2.5 second dwell** at each region's hero moment. During the dwell:
   - The *camera* rests.
   - The *film* never freezes: counters tick, labels stamp, secondary particles drift.
   [Hero dwell duration window | 1.5 to 2.5 seconds | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/capstone | Verified 2026-09-06]

3. **Three Persistent Elements Threading the Entire Film:**
   - **The Wire:** A continuous horizontal line acting as the spine. It is the typed underline, the track lane, the chart baseline, the great-circle map route, the canvas wire, the iris center, the waveform, and the 3D coil.
   - **The Ruler:** A chrome strip across the top with tick marks, running timecode, and a playhead marker tracking real-time playback.
   - **The Protagonist Clip Card:** A designated element (e.g. `<div class="clip">`) that rides the wire's actual path geometry (sampled path, seek-safe) throughout the whole film.
   [Continuous camera journey with 3 persistent elements | 1 unbroken camera move, 3 continuous threads (wire, ruler, protagonist chip) | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/capstone | Verified 2026-09-06]

4. **The Two Sanctioned Seams:**
   - *Seam #1 (Shader Lens):* Pushing through an `sdf-iris` shader transition where the wire remains visible through the iris aperture throughout.
   - *Seam #2 (Beat-Grid Hard Cuts):* Fast card content cuts snapped directly to musical beats analyzed via `hyperframes beats`, executed while camera dolly motion remains continuous.

5. **Footage Processing Pipeline Order of Operations:**
   When integrating live-action or avatar footage into the 2.5D world:
   - Background removal peels away the background *before* the person speaks, sliding off along the travel vector.
   - Cutout stands isolated on brand ground.
   - Spoken keywords land word-synced as display text *behind* the cutout silhouette (two-layer text-behind-subject plate with occlusion).

6. **Single Composition File and Single Variable Scope:**
   - Authored in a single root `index.html` exposing `data-composition-variables="ground,ink"`.
   - Re-skins the entire journey (including charts, maps, glass, and even raster assets via grayscale raster + CSS duotone blend modes) with a single CLI `--variables` flag.

---

## 4. WebGL Shader Transitions and `@hyperframes/shader-transitions`

HyperFrames exposes a specialized WebGL fragment-shader pipeline (`@hyperframes/shader-transitions`) that operates directly on GPU textures of incoming and outgoing DOM trees.

### The 14 Standard WebGL Shaders:
[Registered shader transition blocks | 14 named shaders (domain-warp, ridged-burn, whip-pan, sdf-iris, ripple-waves, gravitational-lens, cinematic-zoom, chromatic-split, glitch, swirl-vortex, thermal-distortion, flash-through-white, cross-warp-morph, light-leak) | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/packages/shader-transitions | Verified 2026-09-06]

| Shader Identifier | Kinematic / Optical Behavior | Ideal Energy / Genre |
| :--- | :--- | :--- |
| `domain-warp` | Multi-octave Perlin noise warping with radiant boundary edge | Editorial, Structural pivot |
| `ridged-burn` | High-frequency thermal edge burn with glowing embers | Tense, Climax, High-stakes finance |
| `whip-pan` | Directional horizontal motion blur simulating high-speed swish | Medium, Explainer, Next-point |
| `sdf-iris` | Signed Distance Field circular aperture wipe with chromatic rim | Hero reveal, Perspective shift |
| `ripple-waves` | Concentric wavefront displacement radiating from center | Playful, Liquid, Macro shocks |
| `gravitational-lens`| Spacetime curvature distortion with chromatic aberration | Heavy macro shifts, Shock events |
| `cinematic-zoom` | Radial velocity zoom with perimeter color fringing | High energy, Climax, Reveal |
| `chromatic-split` | Lateral RGB channel shearing across the boundary | Tech, Data breakdown, Cyber |
| `glitch` | Discrete scanline tearing and pseudo-random block displacement | High energy, Fracture, Disruption |
| `swirl-vortex` | Centripetal angular rotation with noise displacement | Dynamic spiral, System vortex |
| `thermal-distortion`| Vertical convective heat haze rising across plate | Calm, Atmospheric, Warm finance |
| `flash-through-white`| Optical luminance blow-out to 100% white, revealing next plate | Impact cut, Downbeat accent |
| `cross-warp-morph` | Bi-directional noise displacement blending both scenes | Calm, Luxury, Fluid metamorphism |
| `light-leak` | Anamorphic warm optical glare sweeping diagonally | Warm, Heritage, Archival |

### Duration & Easing Dial Presets:
- **Calm / Editorial:** $0.50\text{ s} - 0.80\text{ s}$ (`transitions-blur`, `cross-warp-morph`).
- **Medium / Explainer:** $0.30\text{ s} - 0.50\text{ s}$ (`whip-pan`, `transitions-push`).
- **High / Promo:** $0.15\text{ s} - 0.30\text{ s}$ (`ridged-burn`, `glitch`, `flash-through-white`).

[Transition duration ranges by energy tier | Calm: 0.5-0.8s, Medium: 0.3-0.5s, High: 0.15-0.3s | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/transitions | Verified 2026-09-06]

### The Cardinal Transition Anti-Pattern:
Never fade the outgoing scene to black or cream and subsequently fade the incoming scene in. That creates a 2-frame perceptual dip ("black hole cut"). A true transition must execute a simultaneous, continuous handoff where both scenes exist concurrently in the compositor.

---

## 5. Stop-Motion Physics and Deterministic Frame Quantization

For paper-cutout, woodblock, and hand-animated aesthetics (e.g. Money Physics / Tokyo Tea Break), continuous floating-point tweens feel artificially computerized. The animation requires discrete holds ("on-twos").

### The Floating-Point Quantization Trap:
Dividing time by duration (`Math.floor(t / 0.0667)`) fails because renderer seek-times do not land on exact $1/30\text{s}$ doubles. Over a 60-second timeline, IEEE-754 rounding errors drift across boundaries, causing the hold to alternate erratically between 1 frame, 2 frames, and 3 frames.

### The Exact Frame Quantization Formula:
Quantization must be evaluated strictly against the **integer frame index**:
$$\text{frameIndex} = \text{round}(t \times \text{fps})$$
$$\text{quantizedStep} = \left\lfloor \frac{\text{frameIndex}}{\text{holdFrames}} \right\rfloor$$

```typescript
// Deterministic On-Twos Frame Quantization (Hold for 2 frames at 30 fps)
export function getQuantizedHold(timeSeconds: number, fps: number = 30, holdFrames: number = 2): number {
  const frameIndex = Math.round(timeSeconds * fps);
  return Math.floor(frameIndex / holdFrames);
}
```

### Deterministic PRNG Implementation (Mulberry32):
To generate organic, hand-drawn path wobbles without breaking multi-pass render caching:
```typescript
export function createMulberry32(seed: number): () => number {
  return function(): number {
    seed = (seed + 0x6D2B79F5) >>> 0;
    let t = seed;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
```

---

## 6. Vector Path Morphing and Non-Rigid 2D Transformations

Transforming an editorial metaphor (a tea cup, an index fund basket, a balance scale) into an institutional financial chart without area collapse requires non-linear geometric interpolation.

| Technology | Implementation Architecture | Strengths | Failure Modes |
| :--- | :--- | :--- | :--- |
| **Flubber** | Open-source SVG path string interpolator | Arbitrary shape matching, MIT license | Requires external timeline driver; can twist complex paths |
| **GSAP MorphSVGPlugin** | Commercial GreenSock plugin | Automatic primitive conversion, rotational indexing | Proprietary license; closed source |
| **ARAP (Alexa et al. SIGGRAPH 2000)** | As-Rigid-As-Possible 2D triangulation energy minimization | **Zero volume collapse**, preserves local rigidity | High computational overhead for complex SVGs |

[ARAP 2D morphing volume preservation proof | Jacobian polar decomposition J = R * S | Marc Alexa, Daniel Cohen-Or, David Levin (SIGGRAPH 2000) | URL: https://doi.org/10.1145/344779.344859 | Verified 2026-09-06]

### ARAP Invariants for Evidence Morphing:
When morphing an inked prop into a data chart on the Ledger Page:
1. Centroid displacement: $\Delta C \le 0.06 \times W$.
2. Principal axis rotation: $|\Delta \theta| \le 15^\circ$.
3. Area preservation ratio: $A(t) / \min(A_0, A_1) \ge 0.60$.

---

## 7. Cross-Engine Transition Integration (Remotion vs HyperFrames vs GSAP)

Remotion and HyperFrames address the same fundamental video composition problem through different architectural lenses:

```
REMOTION ARCHITECTURE (React Virtual DOM):
[ Frame Clock: useCurrentFrame() ] ---> [ <TransitionSeries> ] ---> [ Presentation: slide/wipe ] ---> [ Canvas / DOM ]

HYPERFRAMES ARCHITECTURE (Paused DOM + WebGL):
[ FrameAdapter: seekFrame(n) ] ---> [ GSAP Paused Timeline ] ---> [ @hyperframes/shader-transitions ] ---> [ WebGL Canvas ]
```

### Remotion `@remotion/transitions` Standard:
In Remotion, scene transitions are declared functionally via `<TransitionSeries>`:
- `slide()`, `wipe()`, `flip()`, `fade()`, `clockWipe()`, `pushCut()`.
- Timing is driven by `linearTiming({ durationInFrames })` or `springTiming({ config })`.
- **`<TransitionSeries.Overlay>`:** Executes full-bleed optical flashes, light leaks, or burns across a straight butt-cut without contracting the underlying scene durations.

[Remotion TransitionSeries component API | TransitionSeries.Sequence, TransitionSeries.Transition, TransitionSeries.Overlay | Remotion Official Documentation | URL: https://www.remotion.dev/docs/transitions | Verified 2026-09-06]

### FrameAdapter Seek Contract:
HyperFrames enforces deterministic seekability via the `FrameAdapter` interface:
```typescript
export interface FrameAdapter {
  id: string;
  init?: (context: FrameAdapterContext) => Promise<void> | void;
  getDurationFrames: () => number;
  seekFrame: (frame: number) => Promise<void> | void;
  destroy?: () => Promise<void> | void;
}
```
Seeking to frame $N$ must always produce the bit-identical DOM state regardless of execution order or seek direction.

---

## 8. Resolution of Video-Engine Transition Queries (`TRANSITIONS-REVIEW-2026-09-06.md`)

This research directly answers and settles the open transition queries tracked in `docs/content-video-engine/TRANSITIONS-REVIEW-2026-09-06.md`:

1. **TR-1 & TR-11 (The "Slideshow" Retention Defect):**  
   The Tokyo short's retention curve (holding 40% throughout the ledger page, but dipping at clip cuts) was caused by unmotivated cuts between disconnected spaces. Adopting HyperFrames' **Dwell-and-Sweep Rhythm** and carrying a **persistent horizontal evidence wire** through the seam eliminates the reset cost of the cut.
2. **TR-3 (Unsourced Transition Constants):**  
   - `DISSOLVE_S`: Previous value of $0.80\text{ s}$ was too slow. Calibrate to **$0.35\text{ s} - 0.45\text{ s}$** matching HyperFrames' Medium Explainer tier.
   - `WIPE_S`: $0.62\text{ s}$ is validated against HyperFrames' $0.50\text{ s}$ calm / $0.35\text{ s}$ fast wipe benchmarks.
   - `MIN_JERK`: Enable `min_jerk` as the default kinetic ease for all directional camera moves and wipes.
3. **TR-8 (M13 Acoustic-Visual Alignment):**  
   Major transition onsets must lock to acoustic silence intervals ($\ge 0.30\text{ s}$ Whisper gaps). The transition duration must fit within the gap window so speech never collides with a high-energy visual warp.
4. **TR-9 (The Wipe-Onto-Stable-Cream Mount):**  
   Implement the simultaneous handoff: the outgoing scene wipes off via an inverted horizontal mask while the incoming cream washi board scales by $1.02 \to 1.00$ with an umber-tinted shadow.

---

## 9. The Storyboard Planning Contract & Pacing Architecture

Prompting scenes one by one from a blank page causes narrative drift and structural disconnection across scene boundaries. HyperFrames formalizes a multi-scene planning contract that prompts the plan rather than individual scenes.

[Storyboard 3-part schema | 1 arc, 1 direction block, light per-frame spec | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/storyboards | Verified 2026-09-06]

### The 4 Film-Level State Invariants:
Before authoring individual frames, four film-level invariants must be declared:
1. **Message:** The one-sentence thesis the entire film must prove. If a frame does not directly advance this thesis, cut the frame, not the message.
2. **Arc:** The explicit beat sequence (e.g., `Hook → Substance → Landing` or `Hook → Problem → Solution → Proof → CTA`). Parallel entries use shape descriptors such as "listicle".
3. **Audience:** The exact target audience in a phrase; calibrates technical jargon, pacing, and visual density across all frames simultaneously.
4. **Mood:** One energy or musical descriptor (e.g., "tense synth pulse, resolving to warm").

### The Inherited Direction Block:
A storyboard's direction block sets rules that every frame obeys without restating them:
- **Two-Color Discipline:** Declare a ground color (e.g. deep navy `#0b1220`) and one ink color (e.g. warm off-white `#f4efe6`). Emphasis is achieved strictly through inversion, scale, weight, or spatial density — never by introducing a third hue.
  [Two-color brand constraint | Ground + 1 Ink color (emphasis via scale/density) | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/storyboards | Verified 2026-09-06]
- **VO-Paced vs. Timestamp Reveals:** At $t=0$, only the initial spoken element is visible. Subsequent elements arrive on their spoken cues. If the piece is silent, reveals land on explicit timestamps. Holds must stay still; slow drifting or artificial "breathing" reads as unfinished work.
- **The "One Breather" Rule:** Across the entire film, designate exactly **ONE frame** as the breather (the deliberately calmer, static beat or longest read). Naming it prevents over-animating the rest to compensate.
  [Single breather designation | Exactly 1 calmer/static frame across film | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/storyboards | Verified 2026-09-06]
- **The Negative List:** A standing blacklist of visual clichés (no purple-blue AI gradients, no bokeh, no faux browser/OS chrome, no drop-shadow cards, no unseeded randomness).

### Per-Frame Job Schema:
Each individual frame specifies only its differentiated parameters:
```text
[type]        category: hook · benefit_highlight · social_proof · cta
[persuasion]  device: before/after · numbered enumeration · counterexample · callback + distillation
[beat]        emotion: recognition + tension · aha · resolve + inevitability
[focal]       the single entity the eye lands on
[roles]       explicit foreground / supporting / background assignment
```

### The Callback Motif:
Plant a subtle motif early (a mark, geometric chip, accent dot, or phrase) and have it return later denser, larger, or completed as a deliberate narrative payoff.

---

## 10. Seek-Order Safety, Cold Render Workers, and SVG Draw-On Hazards

In programmatic video frameworks (Remotion, HyperFrames), headless render workers seek frames non-linearly across parallel processes. Code that appears correct in sequential browser preview can silently fail on a cold render worker.

[Cold-seek hidden state rule | Explicit opacity: 1 in destination vars | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/rules-and-anti-patterns | Verified 2026-09-06]

### The 7 Mandatory Production Rules:
1. Register all GSAP timelines on `window.__timelines` (renderers cannot seek unindexed timelines).
2. Video elements must be `muted` (mix audio in separate `<audio>` elements).
3. No `Math.random()` — use seeded PRNG (Mulberry32) and quantize on **integer frame index** (`Math.floor(frameIndex / holdFrames)`), never elapsed seconds.
4. Synchronous timeline construction — no `async`/`await` or `fetch()` during GSAP setup.
5. Timed elements require `class="clip"`, `data-start`, `data-duration`, and `data-track-index`.
6. Explicit entrance animations for every scene.
7. Meaningful transitions between scenes.

### Cold-Seek Visibility & GSAP Hazards:
- **Reveal Destination Vars (`gsap_cold_seek_hidden_fromto_missing_reveal`):** When using `gsap.fromTo()` on an element that starts hidden, the destination vars must explicitly state `opacity: 1` (or `autoAlpha: 1`). Cold render workers restore authored hidden states upon direct seek.
- **Initial Hidden State Outside Timeline (`gsap_timeline_set_initial_hide`):** Do not rely on `tl.set(...)` at position 0 inside the timeline to hide elements. Author the initial hidden state in HTML/CSS or via a bare `gsap.set()` outside the timeline.
- **`immediateRender` Pre-Render Hazard:** A `fromTo()` tween pre-renders its `from` state at all frames earlier than its start time by default. Use `to()` with keyframes or zero-duration sets at beat boundaries to prevent early pop-in.
- **Relative Tween Collisions (`gsap_relative_value_second_writer`):** Never stack a relative tween (`"+=50"`, `"-=20"`) on a property while another writer is animating it. Relative offsets capture bases at tween initialization, causing non-linear seeks to diverge.
  [Relative tween collision hazard | Never stack relative tweens on concurrently animated properties | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/rules-and-anti-patterns | Verified 2026-09-06]
- **`repeatRefresh: true` with Relative Offsets (`gsap_repeat_refresh_relative_value`):** Relative offsets accumulate per loop iteration. Seeking directly into iteration $N$ misses previous iterations' accumulations. Use absolute `fromTo()` endpoints.
- **Function-Valued Tween Vars (`gsap_function_value_hazard`):** GSAP function-valued vars receive `(index, target, targets)`. The first argument is the **numerical index**, not the element.
- **Banned DOM Measurements in Callbacks (`gsap_callback_dom_measurement`):** Never call `getBoundingClientRect()`, `getTotalLength()`, or `getComputedStyle()` inside timeline callbacks. Compute geometry once at build time.

### SVG Draw-On Pitfalls:
- **CSS `stroke-dasharray` Conflicts (`svg_drawon_css_dasharray_conflict`):** Do not declare multi-value CSS dasharrays on elements animated with GSAP draw-on; GSAP merges dash lists per component, preserving gaps.
- **Round Caps Paint at Zero Length:** `stroke-linecap: round` paints a visible dot even when `stroke-dashoffset` equals total length. Gate group opacity until draw onset or use butt caps.
- **Static `d` Attribute Requirement (`svg_measure_before_path_d`):** Paths must carry a static `d` attribute before measurement. In Chromium, `getTotalLength()` returns 0 on paths lacking a static `d` attribute, silently breaking draw animations.
  [SVG static path d requirement | Path must have static d attribute before measurement or getTotalLength returns 0 | HeyGen HyperFrames Documentation | URL: https://hyperframes.heygen.com/prompting/rules-and-anti-patterns | Verified 2026-09-06]

### Layout Waivers and Contrast Gates:
- `data-layout-allow-overlap`: Scope locally to the specific text element participating in intentional layering; never apply to root containers.
- `data-layout-allow-occlusion`: Silences WCAG contrast auditing for its entire subtree. Scope to the narrowest possible node.

---

## Sources

- HeyGen HyperFrames Documentation: *Prompt Guide: Overview*. https://hyperframes.heygen.com/prompting/overview
- HeyGen HyperFrames Documentation: *Motion that reads premium*. https://hyperframes.heygen.com/prompting/motion
- HeyGen HyperFrames Documentation: *Transitions*. https://hyperframes.heygen.com/prompting/transitions
- HeyGen HyperFrames Documentation: *Storyboards*. https://hyperframes.heygen.com/prompting/storyboards
- HeyGen HyperFrames Documentation: *Capstone — every technique, one journey*. https://hyperframes.heygen.com/prompting/capstone
- HeyGen HyperFrames Documentation: *Rules and anti-patterns*. https://hyperframes.heygen.com/prompting/rules-and-anti-patterns
- HeyGen HyperFrames Documentation: *Frame Adapters*. https://hyperframes.heygen.com/concepts/frame-adapters
- HeyGen HyperFrames Documentation: *@hyperframes/shader-transitions*. https://hyperframes.heygen.com/packages/shader-transitions
- Remotion Documentation: *@remotion/transitions*. https://www.remotion.dev/docs/transitions
- GreenSock Animation Platform: *MorphSVGPlugin Documentation*. https://gsap.com/docs/v3/Plugins/MorphSVGPlugin/
- Marc Alexa, Daniel Cohen-Or, David Levin: *As-Rigid-As-Possible Shape Interpolation*. ACM SIGGRAPH 2000. https://doi.org/10.1145/344779.344859
- Tommy Flash, Neville Hogan: *The Coordination of Arm Movements: An Experimentally Confirmed Mathematical Model*. Journal of Neuroscience, 1985.

---

## NOT FOUND WHERE I LOOKED

- **HeyGen Proprietary Neural Transition Weights:** Searched `hyperframes.heygen.com` documentation and packages for proprietary neural video-to-video AI transition models; not found. HyperFrames exclusively utilizes deterministic WebGL fragment shaders (`@hyperframes/shader-transitions`) and CSS container transforms.
- **Native Real-Time Navier-Stokes Fluid Shaders in HyperFrames:** Searched HyperFrames catalog for native 3D Navier-Stokes fluid transition shaders; not found. All fluid/morph transitions (e.g. `domain-warp`, `swirl-vortex`, `ripple-waves`) utilize analytical 2D trigonometric and simplex noise equations rather than volumetric fluid simulations.
