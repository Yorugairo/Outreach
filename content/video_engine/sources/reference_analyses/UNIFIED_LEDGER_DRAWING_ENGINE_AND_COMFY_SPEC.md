# Unified System Specification: The 3 ComfyUI Engines & The Ledger Page Drawing/Animation Architecture

*Generated: 2026-09-04 | Status: Authoritative Architecture Specification | Scope: Video Engine Compositing, ComfyUI Local Pipeline, and Ledger Page Drawing System*

---

## Executive Architectural Synthesis

We are not merely patching a parallax shader or stringing together disparate AI tools. **We are building a unified 2.5D Drawing and Animation Engine centered around the Ledger Page.**

Under our core channel doctrine (Operator Ruling E22, Doc 29 §9.26, and the 2026-09-04 doctrine mandate `RULE-the-page-is-the-ground.md`):
> *"The ledger page is our white... We have been treating it as a chart surface. It is a working surface — a ledger is where a thing is worked out, which is the channel's whole posture. Metaphors are drawn ON the page, in ink, on the cream. Then the page becomes the chart."*

This changes the entire production equation:
Instead of prompting an AI model for 15 disconnected raster images per episode (which suffer from hallucinations, character warping, and melted charts), an episode is built upon **1 to 3 World Plates** (the environment) and **a living Ledger Page** (the working ground). 

Our local ComfyUI GPU stack (`127.0.0.1:8188`) provides the three physical engines that lift this system into institutional 3D broadcast reality:
1. **Comfy Engine 1 (Depthflow + Depth Anything v2 Large FP32):** An image-space ray-marching camera displacement engine for continuous atmospheric camera sweeps.
2. **Comfy Engine 2 (SAM 2 + LaMa FFC):** A 50ms multi-plane segmentation and clean-plate inpainter that lifts foreground cards (actors, props, ledger boards) off the ground with zero occlusion tearing.
3. **Comfy Engine 3 (LTX-Video 2B DiT):** A mask-pinned latent diffusion transformer providing organic ambient physical motion (drifting smoke, dust motes, haze, light flicker) while keeping characters and data 100% frozen.

Below is the complete deduplicated technical specification, dial calibration matrix, and data contract.

---

## 1. The Unified 4-Layer Engine Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: DETERMINISTIC FRAME CLOCK & AUDIO-GAP SYNCHRONIZATION         │
│ • Remotion Frame Law: S = f(frame, fps)                                │
│ • Gate M13: Cuts, rolls, and spring entrances strictly locked to       │
│   Whisper acoustic silence gaps (Δt ≥ 0.30s). Zero speech collisions.  │
├────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: VECTOR INK & DATA LAYER (Remotion / SVG / GSAP)               │
│ • Ink strokes drawn via SVG getTotalLength() & strokeDashoffset        │
│ • Kalam per-glyph handwriting with deterministic tilt (±1.6°)          │
│ • Inked metaphor props (tipping balance scales, toll levers, crates)   │
│ • Real-data numeric counters landing verbatim on FRED/Treasury tokens  │
├────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: MULTI-PLANE 2.5D CANVAS (SAM 2 Cutouts + LaMa Clean Plate)    │
│ • Meta SAM 2 isolates foreground subjects (Alpha RGBA PNG)             │
│ • LaMa FFC synthesizes occluded background plate in ~50ms              │
│ • Depthflow / Remotion 3D camera projection (perspective, rotateX/Y)   │
│ • Zero "rubber sheet" edge tearing; independent parallax rates         │
├────────────────────────────────────────────────────────────────────────┤
│ LAYER 1: ATMOSPHERIC GROUND (ComfyUI-LTXVideo 2B DiT)                  │
│ • Mask-pinned latent ambient motion (woodblock smoke, haze, embers)    │
│ • 121-frame / 161-frame seamless physical loops (~10s render time)     │
│ • Foreground actor / ledger surface pinned 100% frozen                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Engine 1: 2.5D Parallax Ray-Marcher (`Depthflow` + `Depth Anything v2`)

### 2.1 Mechanics Under the Hood
`Depthflow` is an **image-space continuous heightfield ray marcher** (`depthflow.glsl`). It projects camera rays from `camera.position` to screen coordinates and performs a two-stage search:
1. **Coarse Forward Probe:** Steps forward across virtual heightfield $Z_{	ext{surf}} = 	ext{height} 	imes D(u, v)$ until penetrating the surface.
2. **Fine Backward Refinement:** Steps backward to identify sub-texel UV coordinates `depthflow.gluv`.

### 2.2 Forensic Bug Discovery in Our Previous Runner
In `tools/google-flow-driver/src/parallax-runner.mjs`, user parameter `strength` was passed to the `BaseFlex` modulation input (which does nothing without an active audio feature), while actual camera displacement `intensity` was **hardcoded to `1.0`** (maximum displacement). Furthermore, `vits_fp16` collapsed depth gradients into blurry ramps, forcing the ray marcher to stretch edge pixels into melted rubber.

### 2.3 Mathematical Disocclusion Limit
In pinhole camera projection, the disocclusion gap $\Delta$ created when translating a camera horizontally by $T_x$ across foreground depth $Z_{	ext{near}}$ and background $Z_{	ext{far}}$ is:
$$\Delta = f \cdot T_x \left( rac{1}{Z_{	ext{near}}} - rac{1}{Z_{	ext{far}}} ight)$$
- If $\Delta \le 8	ext{px}$, the stretched cliff is imperceptible.
- If $\Delta > 20	ext{px}$, the shader stretches silhouette edge pixels across the gap, melting straight pillars and whiteboard borders.

### 2.4 Calibrated Dial Matrix for Engine 1
- **Model:** `depth_anything_v2_vitl_fp32.safetensors` (ViT-Large in FP32; FP16 is strictly banned due to logit underflow).
- **`intensity`:** **`0.08` – `0.15`** (Hard ceiling `0.18`).
- **`steady_value`:** **`0.35` – `0.45`** (Fixed pivot plane where pixels do not drift).
- **`edge_fix`:** **`4` – `6` px** (Morphological dilation pushing cliff edges into background).
- **`quality`:** **`80` – `85`** (Allocates 100 forward probe steps, 1500 backward steps).
- **`ssaa`:** **`1.5` – `2.0`** (Super-sample anti-aliasing eliminating edge crawl).
- **`tiling_mode`:** **`"none"`** (Paired with a 1.10x pre-zoom crop to prevent border mirror artifacts).

---

## 3. Engine 2: Multi-Plane Segmentation & Clean Plate Inpainter (`SAM 2` + `LaMa`)

### 3.1 Mechanics Under the Hood
1. **Meta SAM 2.1 (Hiera Architecture):** Replaces standard ViT with Hierarchical Vision Transformers featuring multi-scale feature pyramids ($1/4, 1/8, 1/16, 1/32$) and windowed spatial attention. Provides sub-pixel boundary acuity on complex silhouettes (deckle paper edges, hair, props).
2. **LaMa (`big-lama.pt`):** Fast Fourier Convolution (FFC) architecture. Unlike standard convolutions that scale locally, FFC performs 2D Real Fast Fourier Transforms (RFFT) in the frequency domain, providing an **image-wide receptive field in layer 1**.

### 3.2 Performance & Speed Benchmarks on Local RTX 4070
- **LaMa Execution Time:** **~50 ms (0.05 seconds)** in a single feedforward pass (50x faster than SDXL inpainting).
- **VRAM Footprint:** **~1.2 GB** (Leaves full GPU headroom for rendering).
- **Determinism:** 100% deterministic, zero prompt variation.

### 3.3 Boundary Bleed & Color Preservation Rules
- **Mask Dilation:** Mask must expand past optical blur radius: $R_{	ext{grow}} = \lceil 2 	imes \sigma_{	ext{optical}} ceil + 12	ext{px}$ (Typically `grow: 18px`, `blur: 7px`).
- **Color Matching:** `INPAINT_ColorMatch` computes mean ($\mu$) and standard deviation ($\sigma$) across $L^*a^*b^*$ perceptual color space on unmasked background, normalizing inpainted pixels to match ambient lighting and grain.

### 3.4 14-Node ComfyUI Execution Graph
An end-to-end headless graph (`POST /prompt`):
`LoadImage` $	o$ `SAM 2 Model` + `Florence-2 Detection` $	o$ `Sam2Segmentation` $	o$ `InvertMask` + `JoinImageWithAlpha` ($	o$ `Layer1_Foreground_Cutout.png`) $	o$ `INPAINT_ExpandMask` + `INPAINT_LoadInpaintModel (big-lama.pt)` $	o$ `INPAINT_InpaintWithModel` $	o$ `INPAINT_ColorMatch` ($	o$ `Layer0_Background_CleanPlate.png`).

---

## 4. Engine 3: Mask-Pinned Ambient Motion Engine (`LTX-Video 2B DiT`)

### 4.1 Mechanics Under the Hood
- **Spatiotemporal Video-VAE:** Employs a custom 3D VAE with a **1:192 compression ratio** ($32	imes 32$ spatial, $8	imes$ temporal).
- **Mathematical Frame Rule:** Frame counts must satisfy:
  $$	ext{num\_frames} = 8n + 1 \quad (n \in \mathbb{N})$$
  *Standard Production Settings:* **121 frames** (~5.04s @ 24fps) or **97 frames** (~4.04s @ 24fps).
- **Latent Space Noise Masking:**
  SAM 2 binary mask $M_{	ext{lat}}$ is broadcast across latent frames:
  $$\mathbf{z}_t = (1 - M_{	ext{lat}}) \odot \mathbf{z}_{	ext{clean}} + M_{	ext{lat}} \odot \mathbf{z}_t^{	ext{diffused}}$$
  Where $M=0$, latents are clamped to the pristine image (zero diffusion noise). Where $M=1$, the model synthesizes atmospheric smoke, drifting haze, or water ripples.

### 4.2 Calibrated Dial Profile for LTX-Video
- **Sampling Steps:** **25 steps** (Euler FlowMatch solver).
- **Guidance Scale (CFG):** **`2.5` – `3.2`** (Strict ceiling `3.5`; higher values cause plastic skinning).
- **STG (Spatio-Temporal Skip Guidance):** Scale `1.0` applied to middle DiT layers (14–20).
- **VRAM / Speed:** FP8 weights (`torch.float8_e4m3fn`) with tiled VAE decode execute in **~8–12 seconds** on local RTX 4070/4090.
- **Compositor Re-Stitch:** To guarantee 0% character/text morphing, Remotion layers the pristine cutout PNG directly over the decoded LTX ambient video.

---

## 5. The Ledger Page as the Core Drawing & Animation Engine

### 5.1 Doctrine Shift: From Chart Template to Working Ground
Under `RULE-the-page-is-the-ground.md`:
1. **WORLD (Woodblock Vox Newsprint):** 3 to 5 hero plates per episode establishing the thematic arena.
2. **PAGE (Cream Ledger `#F4E6C7`):** The working majority of the episode. Inked metaphors are drawn on the page, in ink, on the cream. Then the page evolves into the evidence chart.
3. **ACTOR (@Mike):** Full cutout on World plates; on the Ledger Page, his presence is manifested through **hands, fountain pens, and highlighters** working the surface.

### 5.2 The 6-Stage Visual Choreography
1. **Roll-Out (0.7s):** Washi cream page unrolls onto the screen during an acoustic breath pause.
2. **Savor (0.8s):** Clean working surface is held steady as the narrator begins speaking.
3. **Ink Field (2.4s):** Charcoal ink washes across the board to a defined deckle edge.
4. **Draw Inked Prop (1.5s):** SVG stroke draw animates the physical metaphor (e.g. tipping balance scale, toll gate, wooden pen crate).
5. **Transform to Chart (2.5s):** Prop transitions seamlessly into an official FRED/Treasury data chart (story bars or dense line).
6. **Focus Callout (1.2s):** Skew-pivot highlighter sweeps across the critical datum with an accent tag.

---

## 6. Master Data Contract: `ledger_page.v2.json`

```json
{
  "$schema": "https://outreach.internal/schemas/ledger_page.v2.json",
  "scene_id": "s03_debt_spread_engine",
  "clock": {
    "start_sec": 42.35,
    "end_sec": 54.10,
    "acoustic_gap_start": 41.90,
    "pre_roll_duration": 0.70
  },
  "ground": {
    "kind": "cream_deckle",
    "base_plate_id": "world-ledger-blank-cream-v1",
    "ambient_motion_video": "runtime/jobs/ambient/s03_ambient_dust_121f.mp4",
    "board_rect": { "x": 0.0635, "y": 0.0694, "w": 0.8693, "h": 0.8602 }
  },
  "stage_flow": [
    { "beat": "roll_out", "t_offset": 0.0, "duration": 0.7 },
    { "beat": "savor", "t_offset": 0.7, "duration": 0.8 },
    { "beat": "ink_field", "t_offset": 1.5, "mode": "soak", "duration": 2.4 },
    { "beat": "draw_prop", "t_offset": 3.9, "prop_id": "prop_balance_scale_v1", "duration": 1.8 },
    { "beat": "transform_to_chart", "t_offset": 5.7, "builder": "story_bars", "duration": 2.5 },
    { "beat": "focus_callout", "t_offset": 8.2, "datum_index": 2, "accent": "coral" }
  ],
  "prop_layer": {
    "id": "prop_balance_scale_v1",
    "svg_component": "DynamicBalanceScale",
    "initial_tilt": 0.0,
    "target_tilt": -14.5,
    "spring_physics": { "stiffness": 120, "damping": 14, "mass": 1.0 },
    "parallax_depth": 0.15
  },
  "evidence_chart": {
    "series_id": "ev-debt-spread-v1",
    "source": "Federal Reserve Board / US Treasury (2026)",
    "unit": "%",
    "labels": ["Cost of Debt", "Return on Asset", "Net Spread"],
    "values": [4.2, 9.8, 5.6],
    "value_strings": ["4.2%", "9.8%", "+5.6%"],
    "emphasize": 2
  }
}
```

---

## 7. End-to-End Pipeline Execution Protocol

```
[VOICE TRACK & WORDS] ────────> [WHISPER ALIGNMENT] ───> Acoustic Silence Gaps (≥0.30s)
                                                                 │
[STORYBOARD GENERATOR] <─────────────────────────────────────────┘
  • Snaps scene cuts to acoustic gaps (Gate M13)
  • Allocates World Plates (3-5) vs Ledger Pages (majority)
         │
         ├───> [WORLD PLATES] ───> [COMFY PIPELINE]
         │                          1. SAM 2 isolates actor/subject
         │                          2. LaMa synthesizes clean background plate (~50ms)
         │                          3. LTX-Video generates masked ambient loop (~10s)
         │                          4. Depthflow applies subtle 2.5D push (intensity: 0.12)
         │                                 │
         └───> [LEDGER PAGES] ─────────────┤
               1. Base cream washi plate   │
               2. Inked prop SVG component │
               3. Series JSON chart data   │
               4. Kalam typography         │
                                           ▼
                            [REMOTION / HYPERFRAMES COMPOSITOR]
                            • Layer 0: LTX-Video Ambient Ground
                            • Layer 1: LaMa Inpainted Background Card
                            • Layer 2: SAM 2 Cutout Card / Floating Ledger Board
                            • Layer 3: Vector Ink, Dynamic Props & SVG Charts
                            • Layer 4: Floating Kinetic Captions (No background pill)
                                           │
                                           ▼
                                [DETERMINISTIC 4K RENDER]
```

---

## 8. Summary Engineering Action Items
1. **Patch `parallax-runner.mjs`:** Map caller `strength` to preset `intensity` (clamped to `0.12`), set `tiling_mode: "none"`, and upgrade model to `vitl_fp32`.
2. **Wire the SAM 2 + LaMa 14-Node Graph:** Create `tools/google-flow-driver/src/inpaint-runner.mjs` exposing `create_multiplane_cards` via MCP server.
3. **Wire LTX-Video Masked Latent Node:** Create `tools/google-flow-driver/src/ltx-ambient-runner.mjs` to generate 121-frame ambient background loops with frozen subjects.
4. **Standardize `ledger_page.v2.json`:** Adopt the new specification as the unified data contract between python builders and Remotion renderers.
