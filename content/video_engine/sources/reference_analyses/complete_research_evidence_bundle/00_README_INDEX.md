# Complete Research & Evidence Bundle: Master Index

This directory consolidates the full research, engineering specifications, forensic breakdowns, and visual evidence gathered for the **Outreach Video Engine**, benchmarking against industry-leading financial explainer channels (*Wealth Logic*) and standardizing our **Ledger Page 2.5D Drawing & Animation Engine**.

---

## File Inventory & Agent Navigation Guide

| File | Purpose & Contents | Recommended Consumer |
|---|---|---|
| [`MASTER_RESEARCH_INDEX.md`](MASTER_RESEARCH_INDEX.md) | **The Master Encyclopedia.** Exhaustive index of all 5 research domains, formulas, dial tables, schemas, code blueprints, and file inventories. | Universal Entry Point / All Agents |
| [`MASTER_RESEARCH_AND_EVIDENCE_DOSSIER.md`](MASTER_RESEARCH_AND_EVIDENCE_DOSSIER.md) | **The Master Synthesis.** 360+ lines covering the 4 Core Pillars, comparative scorecard, forensic compositing proof, coordinate transform pipeline, spring physics formulas, cutout rigging, and 100-shot pacing ledger. | Claude / Lead Architect / Orchestrator |

| [`01_wealth_logic_production_report.md`](01_wealth_logic_production_report.md) | Forensic teardown of *Wealth Logic*'s episode (*6 Ways Rich People Make Money With Debt*). Breakdown of their 3-layer architecture, 6-phase narrative spine, sound design, and 100-cut timing metrics. | Script Writer / Video Director |
| [`02_drawing_engine_and_transforms_research.md`](02_drawing_engine_and_transforms_research.md) | In-depth research into drawing engines (*Motion Canvas, Remotion, Flubber*), affine matrices, path drawing, continuous vector morphing, spring physics, and slot-swapped host rigs. | Motion Designer / Frontend Engineer |
| [`03_tutorial_master_prompt.txt`](03_tutorial_master_prompt.txt) | Raw master prompt from the viral tutorial analyzed against production standards. Documents why monolithic AI image generation fails for financial explainers ("The Diffusion Slideshow Trap"). | Prompt Engineer / Asset Curator |
| [`04_shot_ledger_100_cuts.md`](04_shot_ledger_100_cuts.md) | Exact 100-cut shot ledger for the 16m53s reference episode. Timestamps, durations, cut types, visual descriptions, and phase mappings ($P_1 \to P_6$). | Editor / Assembler |
| [`05_comfyui_parallax_technical_standards.md`](05_comfyui_parallax_technical_standards.md) | Deep technical investigation into ComfyUI's 2.5D Depthflow + Depth Anything v2 engine. Forensic bug diagnosis in `parallax-runner.mjs`, GLSL shader math, disocclusion limits, and calibrated parameter ranges. | ComfyUI Engineer / Node Developer |
| [`06_unified_ledger_drawing_engine_and_comfy_spec.md`](06_unified_ledger_drawing_engine_and_comfy_spec.md) | **The Unified Specification.** Synthesizes all 3 ComfyUI engines (`Depthflow`, `SAM 2 + LaMa`, `LTX-Video`) into our core Ledger Page drawing engine. Contains the 14-node ComfyUI graph, dial matrix, and `ledger_page.v2.json` schema. | Full-Stack Pipeline Agent / System Builder |
| [`07_academic_literature_drawing_and_2_5d_animation_engine.md`](07_academic_literature_drawing_and_2_5d_animation_engine.md) | **The Deep Academic Treatise.** Comprehensive mathematical codification: Two-Thirds Power Law, Minimum-Jerk quintics, Euler spirals ($G^2$), Kubelka-Munk optical transfer, ARAP zero-collapse morphing, Bounded Biharmonic Weights (BBW), $O(1)$ analytic spring ODEs, and cognitive psychophysics (Tversky/Mayer). | Math & Animation Engine Specialist / Core Architect |
| [`08_answers_animation_craft_brief.md`](08_answers_animation_craft_brief.md) | **Answers to Research Brief: Animation Craft.** Direct answers to Claude's brief and the operator's questions across 5 tracks: calibrated timing charts (@24fps), ease equivalence, spring ODEs by material, neuromotor 2/3 power law pen-drawing, Gate M13 acoustic gap cuts, ARAP morph bounds, minimum 5-constraint rigging, 9:16 safe zones, and frame-sequence quality gates. | Animation Builder / Editorial Lead / Claude Interop |
| [`09_2d_and_2_5d_body_animation_object_handling_and_grounding.md`](09_2d_and_2_5d_body_animation_object_handling_and_grounding.md) | **2D & 2.5D Body Animation, Object Handling, & Grounding.** Deep monograph on character biomechanics, Hof's XCOM, 2-bone closed-form analytical IK, BBW / 2D DQS skinning, Feix 33-grasp taxonomy, Flash-Hogan minimum-jerk reaching, matrix re-parenting, Jim Blinn's planar shadow matrices, dual-component AO contact slits, and vanishing point eye-line alignment. | Character Animator / Rigging Lead / Compositor |
| [`10_generative_video_tools_and_cross_platform_composition.md`](10_generative_video_tools_and_cross_platform_composition.md) | **Generative Video Foundations & 9:16 vs. 16:9 Architecture.** Comprehensive technical mastery of Wan 2.1 (Flow Matching DiT, 4k+1 frame clock, TeaCache), LTX-Video (2B DiT, N=8n+1, STG layer 19, mask-pinned latents), Depth Suite (Depth Anything V2, DepthCrafter, Depthflow GLSL dials), and 9:16 vs. 16:9 cross-platform composition (3-Zone Vertical Stage, mobile safe zones, short vs. long form). | Video Engine Architect / Cross-Platform Lead / Motion Designer |
| [`key_evidence_frames/`](key_evidence_frames/) | High-resolution extracted reference frames proving 2.5D layer stacking, persistent vector ink, and isolated host hands. | Visual QC / Reviewer |


---

## Key Architectural Decisions

1. **The Page is the Ground (`RULE-the-page-is-the-ground.md`):** The cream Ledger Page (`#F4E6C7`) is not just a chart card; it is the entire drawing canvas and primary world ground.
2. **Decoupled 3-Layer Scene Graph:** Background (World/Desk) $\to$ Evidence Surface (Ledger Page with Vector Ink & Charts) $\to$ Host Rig (@Mike hands/pen/body).
3. **No Unconstrained Diffusion on Text or Actors:** Text, numbers, and human figures are 100% deterministic vectors and transparent PNG cutouts. Diffusion (LTX-Video) is restricted to mask-pinned ambient backgrounds.
4. **Fast Inpainting Over Heavy Parallax:** Use Meta SAM 2.1 + LaMa FFC (~50ms) to split scenes into card layers rather than stretching single meshes with high displacement intensity.
