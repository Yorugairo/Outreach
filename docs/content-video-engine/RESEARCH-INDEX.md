# Research extraction index

Every heading of every document in the research evidence bundle, with what happened to
it. **Coverage is the proof of reading**: a heading with no disposition fails
`scripts/check_research_extraction.py`, and you cannot account for a section you did not
open.

Bundle: `content/video_engine/sources/reference_analyses/complete_research_evidence_bundle/`
Read completed 2026-09-04. Reference layer: docs **42–46**.

## Disposition vocabulary

| tag | meaning |
|---|---|
| `EXTRACTED -> NN` | landed in reference doc NN at the named section |
| `RECORD` | read; contextual or structural, nothing actionable to lift |
| `DUPLICATE` | synthesis of other primaries; extracted at the primary instead |
| `PRIOR` | already extracted before this pass |
| `FILTERED OUTPUT` | not a primary — a pass over the primaries, triaged separately |
| `REJECTED` | read and refused, with the reason stated inline |

## The reference layer

| doc | covers | primaries behind it |
|---|---|---|
| [42-DRAWING-KINETICS](42-DRAWING-KINETICS.md) | stroke reparameterisation, closed-form springs and the overshoot inverse, squash, Euler spirals | 07 Pillars 1 & 3, 02 §2 |
| [43-SCENE-GRAPH-AND-TRANSFORM](43-SCENE-GRAPH-AND-TRANSFORM.md) | anchor sandwich, Z-stack, dirty flags, both morph methods, the cutout rig | 02 §1/§3/§4, 07 Pillar 2, dossier §3 |
| [44-INK-AND-SURFACE](44-INK-AND-SURFACE.md) | Kubelka-Munk compositing, coffee-ring edge, anisotropic wicking — bounded by E22 | 07 §1.4 |
| [45-PARALLAX-AND-PLATE-MOTION](45-PARALLAX-AND-PLATE-MOTION.md) | disocclusion limit, the viability matrix, our dial audit, multi-plane inpainting, masked ambient motion | 05 whole, 06 §2–4 |
| [46-REFERENCE-RHYTHM](46-REFERENCE-RHYTHM.md) | shot distribution recomputed, gap thresholds, the equation spine, phase map | 04 (recomputed), 01, dossier §10 |

## Declared conflicts and rejections

These are the load-bearing disagreements found by reading the primaries against each
other and against our code. **A conflict can only be found by reading both sides.**

1. **RESOLVED — `strength` vs `intensity` in the parallax runner.** Settled 2026-09-04
   from the installed node source, which is the authority both reports were guessing at.
   `base_flex.py:25` makes `feature` an optional input defaulting to `None`;
   `base_flex.py:103` gates all modulation behind `if feature is not None:`; `strength` is
   consumed *only* inside `modulate_param`, reachable only from that branch. We supply no
   feature, so **`strength` is dead code in our pipeline.** `intensity`
   (`depthflow_motion_presets.py:13`, required FLOAT, default 1.0, max 10.0) is the real
   displacement. **`06` is right, `05` is wrong** — and `05`'s "intensity: 1.0 is the
   correct dolly value" must not be followed. Recorded in 45 §45.4.
2. **Depth model precision.** `05` says `vitl_fp16`; `06` says `vitl_fp32` with fp16
   "strictly banned due to logit underflow." Take ViT-Large, leave precision to a test roll.
3. **Acoustic gap threshold.** `01` and the dossier's `gap_detector.py` use **0.45 s**
   with the cut at the gap **midpoint**; `06` and `08` use **0.30 s** at gap **onset**.
   Different gates. **Settle from our own word timeline before M13 ships** (46 §46.3).
4. **REJECTED — the per-phase word counts in `01` and dossier §10.** They sum to 3952
   against a stated 3101 total and imply an unspeakable 299 WPM in P1. This is the
   YouTube caption over-count (rolling carryover), already known to the operator. Phase
   *boundaries* are used; the word and WPM figures are not.
5. **REJECTED — the numeric claims of `08`.** `08` is a filter pass over these primaries,
   not research. Its fabricated figures are catalogued in
   [VERDICT-research-brief-animation-craft.md](briefs/VERDICT-research-brief-animation-craft.md);
   everything adopted from it is re-sourced from a primary here.
6. **SOURCES-TO-VERIFY — two citations in the pass-2 rewrite of `08`.** Neither is
   used by docs 42-46, so nothing here depends on them; they are logged because `08` now
   presents them as empirical.
   - *Martinez-Conde, Macknik & Hubel (2006), Nature Reviews Neuroscience 7(10):732-740,
     "The role of fixational eye movements in visual perception"* - that title is
     associated with **NRN 5:229-240 (2004)**. Flagged once before pass 2 and returned
     unchanged with an issue number added. Verify the year/volume pairing.
   - *Hasson et al. (2008), NeuroImage 28:1026* - NeuroImage volume 28 is 2005; a 2008
     paper falls in volumes 39-43. Verify.

7. **`08` §8 covers one of five parallax defects.** The pass-2 code audit gets its line
   coordinates right (line 142 *is* `"inputs": motionInputs`) but addresses only
   `intensity` and the model. The strings `tiling_mode`, `ssaa` and `quality` appear
   **nowhere** in its 612 lines, so its proposed fix leaves `tiling_mode: "mirror"` in
   place - the kaleidoscope glitch `05` names as a specific observed artifact. This is
   why 45 is sourced from `05`/`06` and not from `08`.

8. **Our parallax dials do not match any target.** Read from
   `tools/google-flow-driver/src/parallax-runner.mjs` on 2026-09-04: `strength=1.0`,
   `intensity=1.0` hardcoded in all six presets, `tiling_mode="mirror"` (the kaleidoscope
   glitch), `ssaa=1.0`, `quality=75`, model `vits_fp16`. Left to the Flow lane; recorded
   in 45 §45.3.

## Full disposition table


### `00_README_INDEX.md` — 2 headings
| heading | disposition |
|---|---|
| File Inventory & Agent Navigation Guide | RECORD - bundle navigation; consumed to route this read |
| Key Architectural Decisions | RECORD - bundle navigation; consumed to route this read |

### `01_wealth_logic_production_report.md` — 18 headings
| heading | disposition |
|---|---|
| Executive Summary & Production Benchmarks | EXTRACTED -> 46 SS46.1 |
| Core Production Metrics | EXTRACTED -> 46 SS46.1 |
| Comparative Scorecard: Tutorial vs. Wealth Logic vs. Outreach Doctrine | EXTRACTED -> 46 SS46.1/SS46.6 (tutorial column = negative control) |
| The 5 Foundational Takeaways for Our Channels (*Money Physics* / *Building Money*) | RECORD - section header over the five below |
| 1. Audio Gaps as Structural Scene Dividers (The Breath Pause Rule) | EXTRACTED -> 46 SS46.3 |
| 2. The Unifying Equation Spine (Curing "Listicle Fatigue") | EXTRACTED -> 46 SS46.4 - closes backlog R2a |
| 3. Evidence Screen Time (The ~10s Rule) | EXTRACTED -> 46 SS46.1 |
| 4. Persistent Cast & Metaphorical Physical Props | EXTRACTED -> 43 SS43.6 |
| 5. Kinetic Floating Captions (No Background Pill) | EXTRACTED -> 46 SS46.7 - confirms current treatment |
| 6-Phase Retention Architecture Deconstruction | EXTRACTED -> 46 SS46.5 - boundaries only; word counts REJECTED (YouTube caption over-count, operator-known) |
| P1: The Open (00:00 – 01:30) / Hook & Contract | EXTRACTED -> 46 SS46.5 - boundaries only; word counts REJECTED (YouTube caption over-count, operator-known) |
| P2: The Engine (01:30 – 02:52) / Foundational Model | EXTRACTED -> 46 SS46.5 - boundaries only; word counts REJECTED (YouTube caption over-count, operator-known) |
| P3: The Gap (02:52 – 07:36) / Mounting Contradiction & Initial Mechanisms | EXTRACTED -> 46 SS46.5 - boundaries only; word counts REJECTED (YouTube caption over-count, operator-known) |
| P4: The Pivot (07:36 – 09:17) / 45–55% Chiastic Turn | EXTRACTED -> 46 SS46.5 - boundaries only; word counts REJECTED (YouTube caption over-count, operator-known) |
| P5: The Payoff & The Tell (09:17 – 14:21) / Climax & Accessible Counterparts | EXTRACTED -> 46 SS46.5 - boundaries only; word counts REJECTED (YouTube caption over-count, operator-known) |
| P6: The Close (14:21 – 16:53) / Resolution & Ring Echo | EXTRACTED -> 46 SS46.5 - boundaries only; word counts REJECTED (YouTube caption over-count, operator-known) |
| Visual Evidence Manifest | RECORD - frame paths; underpins the 43 SS43.6 forensic argument |
| Actionable Takeaways for Outreach Engine Pipelines | EXTRACTED -> 46 SS46.2/SS46.3 |

### `02_drawing_engine_and_transforms_research.md` — 29 headings
| heading | disposition |
|---|---|
| Executive Summary | EXTRACTED -> 43 SS43.1/SS43.3 |
| Architecture Diagram & The 4 Core Mechanical Pillars | EXTRACTED -> 43 SS43.1/SS43.3 |
| Pillar 1: The Coordinate Transform Pipeline & Anchor Normalization | EXTRACTED -> 43 SS43.2 |
| Pillar 2: Deterministic Clocking & Closed-Form Spring Physics | EXTRACTED -> 42 SS42.2 |
| Pillar 3: Retained 2.5D Scene Graph & Dirty Flags | EXTRACTED -> 43 SS43.3/SS43.4 |
| Pillar 4: Modular Vector Cutout Rigging (The Host Solution) | EXTRACTED -> 43 SS43.6 |
| 5 Actionable Upgrades for Our Pipeline | EXTRACTED -> 42 SS42.1, 43 SS43.2/SS43.6, 46 SS46.3 |
| 1. Mechanics of 2D/2.5D Drawing Engines | RECORD - structural heading; content extracted at its subsections |
| 1.1 Immediate Mode vs. Retained Mode | EXTRACTED -> 43 SS43.1 |
| 1.2 The Coordinate Transform Pipeline | EXTRACTED -> 43 SS43.2 |
| 2. Animation Mechanics & Deterministic Clocking | EXTRACTED -> 42 SS42.2 |
| 2.1 The Deadly Flaw of Wall-Clock Animations in Headless Video | EXTRACTED -> 42 SS42.2 |
| 2.2 Closed-Form Analytic Spring Physics (O(1) Seekable Dynamics) | EXTRACTED -> 42 SS42.2 |
| 2.3 Vector Path Morphing Algorithms (Flubber & d3-interpolate-path) | EXTRACTED -> 43 SS43.5 Method A |
| 3. Object Management & 2.5D Scene Graphs | EXTRACTED -> 43 SS43.3 |
| 3.1 Hierarchical Scene Graph Structure | EXTRACTED -> 43 SS43.3 |
| 3.2 Matrix Concatenation & The Dirty Flag Pattern | EXTRACTED -> 43 SS43.4 |
| 3.3 2.5D Perspective Projection & Z-Stacking | EXTRACTED -> 43 SS43.3 |
| 4. Character Rigging & Vector Cutout Systems | EXTRACTED -> 43 SS43.6 |
| 4.1 Why Skeletal Mesh Deformation is Wrong for Faceless Finance | EXTRACTED -> 43 SS43.6 |
| 4.2 The Winning Standard: Vector Cutout + Slot-Swapping | EXTRACTED -> 43 SS43.6 |
| 5. Architectural Blueprint for Outreach Video Engine | RECORD - sequencing, superseded by our own build order |
| Improvement 1: Unified Affine Scene Node Interface | EXTRACTED -> 43 SS43.2 |
| Improvement 2: The Analytic Spring Damper Hook | EXTRACTED -> 42 SS42.2 |
| Improvement 3: The Modular Host Cutout Rig Component | EXTRACTED -> 43 SS43.6 |
| Improvement 4: Dynamic SVG Balance Scale Component | RECORD - balance-scale component; a worked example of 43 SS43.3, build when a page needs it |
| Improvement 5: Word-Gap Boundary Snapping Engine | EXTRACTED -> 46 SS46.3 |
| 6. Implementation Roadmap for Outreach Video Engine | RECORD - sequencing, superseded by our own build order |
| Sources & Reference Material | RECORD - structural heading; content extracted at its subsections |

### `03_tutorial_master_prompt.txt` — 21 headings
| heading | disposition |
|---|---|
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| CHANNEL KNOWLEDGE BASE (Pre-loaded — Do Not Ask Again) | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| CONTENT & SCRIPT DNA | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| PROVEN VIRAL TOPIC ANGLES | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| VISUAL STYLE DNA | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| STAGE 1 — GENERATE 5 VIRAL TOPIC IDEAS | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| STAGE 2 — GENERATE FULL NARRATION SCRIPT | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| STAGE 3 — GENERATE IMAGE PROMPTS FOR EVERY TIMESTAMP | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| STAGE 4 — GENERATE FINAL VIRAL METADATA | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| OPERATOR RULES (Always Active) | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |
| ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted |

### `04_shot_ledger_100_cuts.md` — 1 headings
| heading | disposition |
|---|---|
| Visual Species Taxonomy Legend | EXTRACTED -> 46 SS46.1/SS46.2 - PRIMARY MEASUREMENT, recomputed here rather than quoted |

### `05_comfyui_parallax_technical_standards.md` — 16 headings
| heading | disposition |
|---|---|
| Executive Summary & Root-Cause Diagnosis | EXTRACTED -> 45 SS45.1 |
| The Root Cause: | EXTRACTED -> 45 SS45.1 |
| 1. Technical Anatomy of Our Current ComfyUI Stack | EXTRACTED -> 45 SS45.3 |
| The 5 Technical Failures in Our Configuration: | EXTRACTED -> 45 SS45.3 |
| 2. The Mathematical Limit: The Disocclusion Problem | EXTRACTED -> 45 SS45.1 |
| The Core Deficit: | EXTRACTED -> 45 SS45.1 |
| 3. The Artistic Viability Matrix: When to Use What | EXTRACTED -> 45 SS45.2 - closes backlog R5 |
| The Golden Rule of Depthflow: | EXTRACTED -> 45 SS45.2 - closes backlog R5 |
| 4. Dial Calibration Guide for ComfyUI Depthflow | EXTRACTED -> 45 SS45.3 |
| 4.1 Master Node Inputs (`Depthflow`) | EXTRACTED -> 45 SS45.3 |
| 4.2 Motion Presets & Strength Bounds | EXTRACTED -> 45 SS45.3 |
| 5. The Professional Standard: Two-Plane Layer Inpainting | EXTRACTED -> 45 SS45.5 |
| The 3-Step Protocol: | EXTRACTED -> 45 SS45.5 |
| 6. Actionable Implementation Changes for Our Pipeline | EXTRACTED -> 45 SS45.3 - left to the Flow lane to apply |
| File Updates Required in `content/video_engine`: | EXTRACTED -> 45 SS45.3 - left to the Flow lane to apply |
| Sources & Authoritative References | RECORD |

### `06_unified_ledger_drawing_engine_and_comfy_spec.md` — 21 headings
| heading | disposition |
|---|---|
| Executive Architectural Synthesis | EXTRACTED -> 45 SS45.5/SS45.6, 43 SS43.3 |
| 1. The Unified 4-Layer Engine Architecture | EXTRACTED -> 45 SS45.5/SS45.6, 43 SS43.3 |
| 2. Engine 1: 2.5D Parallax Ray-Marcher (`Depthflow` + `Depth Anything v2`) | EXTRACTED -> 45 SS45.1 |
| 2.1 Mechanics Under the Hood | EXTRACTED -> 45 SS45.1 |
| 2.2 Forensic Bug Discovery in Our Previous Runner | EXTRACTED -> 45 SS45.4 - CONFLICT with 05, held as SOURCES-TO-VERIFY |
| 2.3 Mathematical Disocclusion Limit | EXTRACTED -> 45 SS45.1 |
| 2.4 Calibrated Dial Matrix for Engine 1 | EXTRACTED -> 45 SS45.1 |
| 3. Engine 2: Multi-Plane Segmentation & Clean Plate Inpainter (`SAM 2` + `LaMa`) | EXTRACTED -> 45 SS45.5 |
| 3.1 Mechanics Under the Hood | EXTRACTED -> 45 SS45.1 |
| 3.2 Performance & Speed Benchmarks on Local RTX 4070 | EXTRACTED -> 45 SS45.5 |
| 3.3 Boundary Bleed & Color Preservation Rules | EXTRACTED -> 45 SS45.5 |
| 3.4 14-Node ComfyUI Execution Graph | EXTRACTED -> 45 SS45.5 |
| 4. Engine 3: Mask-Pinned Ambient Motion Engine (`LTX-Video 2B DiT`) | EXTRACTED -> 45 SS45.6 |
| 4.1 Mechanics Under the Hood | EXTRACTED -> 45 SS45.1 |
| 4.2 Calibrated Dial Profile for LTX-Video | EXTRACTED -> 45 SS45.3/SS45.4 |
| 5. The Ledger Page as the Core Drawing & Animation Engine | RECORD - restates RULE-the-page-is-the-ground, already ours |
| 5.1 Doctrine Shift: From Chart Template to Working Ground | RECORD - restates RULE-the-page-is-the-ground, already ours |
| 5.2 The 6-Stage Visual Choreography | EXTRACTED -> 42 SS42.1 context; independently confirms the shipped LP clock |
| 6. Master Data Contract: `ledger_page.v2.json` | RECORD - schema proposal; read before building the object-page renderer (backlog N6) |
| 7. End-to-End Pipeline Execution Protocol | RECORD - sequencing |
| 8. Summary Engineering Action Items | RECORD - sequencing |

### `07_academic_literature_drawing_and_2_5d_animation_engine.md` — 26 headings
| heading | disposition |
|---|---|
| Executive Summary: "Math Displaying as Art" | EXTRACTED -> 42/43/44 - the four-pillar map this read followed |
| 1.1 The Two-Thirds Power Law of Human Drawing | EXTRACTED -> 42 SS42.1 |
| Neuromuscular Origin: The Minimum-Jerk Hypothesis | EXTRACTED -> 42 SS42.1 |
| Physical & Neurological Mandates: | EXTRACTED -> 42 SS42.1 |
| 1.2 Kinematic Arc-Length Reparameterization for SVG & Canvas | EXTRACTED -> 42 SS42.1 |
| 1.3 Procedural Fair Curves: Euler Spirals vs. Cubic Béziers | EXTRACTED -> 42 SS42.4 |
| 1.4 Physical Ink Synthesis, Coffee Rings, & Radiative Transfer | EXTRACTED -> 44 SS44.2 |
| The Coffee Ring Effect (Deegan et al. 1997, 2000) | EXTRACTED -> 44 SS44.2 |
| Anisotropic Darcy Flow in Washi Paper (Chu & Tai 2005) | EXTRACTED -> 44 SS44.3 |
| Kubelka-Munk Radiative Transfer (1931) | EXTRACTED -> 44 SS44.1 |
| 2.1 The Mathematics of Zero Volume Collapse | EXTRACTED -> 43 SS43.5 Method B |
| Polar Decomposition in $\mathbb{R}^{2 	imes 2}$ | EXTRACTED -> 43 SS43.5 Method B |
| Riemannian Geodesic Interpolation (Alexa, Cohen-Or, & Levin 2000) | EXTRACTED -> 43 SS43.5 Method B |
| 2.2 ARAP Local-Global Energy Optimization (Sorkine & Alexa 2007) | EXTRACTED -> 43 SS43.5 |
| 2.3 Bounded Biharmonic Weights (BBW) & 2D Dual Quaternion Skinning | EXTRACTED -> 43 SS43.7 - deferred until a prop needs it |
| 2.4 Multi-Plane Geometry & Planar Homography | EXTRACTED -> 43 SS43.3, 45 SS45.5 |
| 3.1 Closed-Form Physics vs. Numerical Integration | EXTRACTED -> 42 SS42.2 |
| Derivation of Damped Harmonic Oscillator Step Response | EXTRACTED -> 42 SS42.2 |
| 3.2 Area-Preserving Squash and Stretch Tensors | EXTRACTED -> 42 SS42.3 |
| 3.3 Spacetime Constraints & Elastic Paper Mechanics | RECORD - Witkin & Kass carried into 42 SS42.6; paper-curl mechanics deferred |
| 4.1 Cognitive Load Theory & Diagram Comprehension | EXTRACTED -> 46 SS46.2 (savor beat), 44 SS44.4 (restraint clause) |
| 4.2 Cross-Modal Phase Locking: Syllable Rates & Gate M13 | EXTRACTED -> backlog N8(b) - STAGE type should key to syllables, not words |
| 5.1 The Master 6-Beat Kinetic Timeline | EXTRACTED -> 46 SS46.2 + backlog N8(a); independently confirms the shipped LP clock |
| 5.2 Deterministic Bit-Level Hash: `lpHash` | RECORD - seeded-tilt hash; our template already seeds |
| 5.3 O(1) Seek-Safe Analytic Spring Evaluator | EXTRACTED -> 42 SS42.2 - working three-regime implementation |
| 6. Authoritative Academic Citations | RECORD - structural / bibliography |

### `08_answers_animation_craft_brief.md` — 42 headings
| heading | disposition |
|---|---|
| 0. Pass 1 Audit & Retrospective: The Honest Correction | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 0.1 Specific Errors Conceded & Corrected | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 1. Pipeline & Doctrine Triage: What Goes Where | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 2. Executive Synthesis: Synergies & The Free High-Leverage Wins | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 2.1 The 5 Overlapping Synergies to Capitalize On | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 2.2 The 5 Disproportionately Easy Free Wins | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 3. Track A — The Animator (Timing and Motion) | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| A1: The Timing Charts [RECLASSIFIED: Design Proposal] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| A2: Ease Equivalence [RECLASSIFIED: Design Proposal] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| A3: Spring vs. Curve [RECLASSIFIED: Design Proposal] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| A4: The Threshold of "Alive" [RE-ASK 1 ★: Audited & Answered] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| A5: Drawing-On [CLOSED & RECLASSIFIED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| A6: The Secondary-Motion Budget [RECLASSIFIED: Design Proposal] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 4. Track B — The Editor (Cutting and Rhythm) | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| B1: The Gap-Cut Finding, Generalised [RE-ASK 4: Audited & Answered] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| B2: Shot Length & Reading Floors [RE-ASK 2: Audited & Answered] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| B3: L-Cuts / J-Cuts under Continuous Narration [RECLASSIFIED: Design Proposal] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| B4: Graphic Match Cuts (ARAP Invariants) [Tier 1 Math — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| B5: Rhythm as a Distribution [Tier 1 Science — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 5. Track C — The Drawing-Engine Builder | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| C1: Shape Interpolation (ARAP) [Tier 1 Math — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| C2: Rigging Without a Rig (The 5 Core Constraints) [Tier 1 Architecture — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| C3: Nested Coordinate Spaces [Tier 1 Architecture — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| C4: Deterministic Runtime Under Seek [Tier 1 Architecture — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| C5: Ink on Paper, Specifically [Tier 1 Math & Shaders — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| C6: What Rive / Lottie / Flash Got Right [Tier 1 Architecture — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 6. Track D — Placement (The "Where" Question) | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| D1: Eye-Trace & Fixation Decay [Tier 1 Psychophysics — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| D2: Non-Decorative Composition for 9:16 [Candidate Doctrine] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| D3: Saliency Hierarchy & Mayer's Spatial Contiguity [Tier 1 Cognitive Science — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| D4: Motion-Graphics Grids (12-Column Vertical) [Tier 2 Proposal] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| D5: The Abstract $	o$ Concrete Metaphor Library [Tier 1 Cognitive Linguistics — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 7. Track E — The Feedback Loop (The Structural Gap) | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| E1: Frame Sequence Quality Metrics [Metrics: Tier 1 CLOSED; Thresholds: Tier 2 Proposal] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| E2: Diagnosing "The Race Feels Choppy" [Tier 1 Psychophysics — CLOSED] | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 8. Procedural Code Audit: `parallax-runner.mjs` | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 8.1 Current Code & Line Coordinates | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 8.2 The Precise Defect & Proposed Fix | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 9. Sourcing Integrity & Bibliography | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 9.1 Empirical Psychophysics & Mathematics (Primary Scientific Evidence) | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 9.2 Practitioner Doctrine (Editorial & Animation Craft) | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |
| 9.3 Internal Repository Measurements | FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here |

### `MASTER_RESEARCH_AND_EVIDENCE_DOSSIER.md` — 29 headings
| heading | disposition |
|---|---|
| Table of Contents | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| 1. Executive Summary & The 4 Core Pillars | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| The 4 Pillars: | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| 2. Comparative Scorecard & Production Benchmarks | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| 3. Forensic Visual Evidence & Proof of 2.5D Compositing | EXTRACTED -> 43 SS43.6 - the three-styles-on-one-canvas proof |
| 4. Tutorial Master Prompt Audit & The "Diffusion Slideshow" Trap | EXTRACTED -> 45 SS45.2, 46 SS46.1 |
| The 4 Fatal Flaws: | EXTRACTED -> 45 SS45.2, 46 SS46.1 |
| What We Steal from the Prompt: | EXTRACTED -> 45 SS45.2, 46 SS46.1 |
| 5. Drawing Engine Mechanics & Coordinate Transform Pipeline | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| 2D Affine Transformation Matrix (Homogeneous $3 \times 3$) | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| Anchor Normalization | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| 6. Deterministic Clocking & Closed-Form Spring Physics | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| 7. Object Management & 2.5D Layer Stacking | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| 8. Modular Vector Cutout Rigging (Host System) | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| 9. Production-Ready Code Blueprints | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| Blueprint 1: `SceneNode.ts` (Unified Affine Transforms) | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| Blueprint 2: `useAnalyticSpring.ts` (Closed-Form $O(1)$ Dynamics) | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| Blueprint 3: `DynamicBalanceScale.tsx` (Kinetic Evidence Component) | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| Blueprint 4: Audio Breath-Gap Scene Boundary Detector (`gap_detector.py`) | EXTRACTED -> 46 SS46.3 - the 0.45s/midpoint variant |
| 10. 100-Shot Pacing Ledger & 6-Phase Script Map | EXTRACTED -> 46 SS46.5 |
| 11. Sources & Authoritative References | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| 12. Unified Ledger Drawing Engine & ComfyUI Specification | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| The 3 Local ComfyUI Engines & Role Matrix | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| The 6-Stage Ledger Choreography | DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead |
| 13. Animation Craft Breakthroughs & Three-Tier Pipeline Triage | RECORD - added 2026-09-04 after our response; its Tier1/Tier2/Tier3 split matches our ADOPT / ADOPT-AS-OURS / candidate-doctrine triage independently |
| 13.1 The Three-Tier Governance Framework | RECORD - added 2026-09-04 after our response; its Tier1/Tier2/Tier3 split matches our ADOPT / ADOPT-AS-OURS / candidate-doctrine triage independently |
| 13.2 The 5 Grand Synergies to Capitalize On | RECORD - restates 42/43/45 content; its parallax item now correctly targets intensity but still omits tiling_mode, ssaa and quality (see conflict 7) |
| 13.3 The 5 Disproportionately Easy Free Wins | RECORD - restates 42/43/45 content; its parallax item now correctly targets intensity but still omits tiling_mode, ssaa and quality (see conflict 7) |
| 13.4 Primary Academic & Empirical Citations | EXTRACTED -> 46 SS46.1 - the Cutting log-normal claim; the rest duplicate 42-45 sources |

### `MASTER_RESEARCH_INDEX.md` — 32 headings
| heading | disposition |
|---|---|
| Quick Navigation: Thematic Research Domains | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 1. Master File & Artifact Inventory | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 1.1 Complete Evidence Bundle (`complete_research_evidence_bundle/`) | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 1.2 Standalone Reference Documents (`content/video_engine/sources/reference_analyses/`) | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 2. Domain 1: Reference Channel Forensic Deconstruction | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| Core Finding: Composited 2.5D Scene Graph vs. The Diffusion Slideshow Trap | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| Forensic Proof Points: | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 3. Domain 2: Drawing Engines, Affine Transforms, & Cutout Rigging | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 3.1 The 2.5D Retained Scene Graph | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 3.2 Affine Coordinate Transforms & Matrix Math | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 3.3 Slot-Swapped Cutout Rigging (Host System) | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 4. Domain 3: Local ComfyUI GPU Stack | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 4.1 Comfy Engine 1: Parallax & Ray-Marcher | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 4.2 Comfy Engine 2: SAM 2 + LaMa Inpainting | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 4.3 Comfy Engine 3: LTX-Video 2B DiT Ambient Ground | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 5. Domain 4: The Unified Ledger Page Drawing & Animation Engine | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| Core Doctrine Mandate: The Page is the Ground | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 5.1 The 6-Stage Visual Choreography | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 6. Domain 5: Academic Literature & Mathematical Foundations | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 6.1 Biomechanical Motor Control | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 6.2 Spline Fairness & Differential Geometry | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 6.3 Non-Rigid Shape Morphing (ARAP) & Skinning | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 6.4 Analytic Second-Order Dynamical Systems | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 6.5 Physical Ink & Paper Interaction | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 6.6 Perceptual Psychophysics & Audio-Visual Entrainment | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 7. Mathematical Formulas & Theoretical Laws Quick-Lookup | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 8. Calibrated Parameter Dials & Node Contracts | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 8.1 Depthflow & Depth Anything v2 (Engine 1) | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 8.2 SAM 2 + LaMa Inpainting (Engine 2) | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 8.3 LTX-Video 2B DiT Ambient Ground (Engine 3) | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 9. Production Code Blueprints & Data Schemas | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |
| 10. Doctrine Rules, Operating Rulings, & Quality Gates | DUPLICATE - index over the same primaries; used to confirm this read covered every domain |

---

**237 headings across 11 documents, all dispositioned.**
Verified by `python scripts/check_research_extraction.py`.
