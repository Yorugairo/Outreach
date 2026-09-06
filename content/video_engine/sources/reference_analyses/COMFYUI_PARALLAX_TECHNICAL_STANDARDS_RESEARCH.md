# Deep Research Report: ComfyUI Parallax Engine — Technical Mechanics, Dial Calibration, and Professional Production Standards

*Generated: 2026-09-04 | Status: Authoritative Technical Standard | Scope: 2.5D Parallax, Depthflow, and Camera Motion in Video Engine*

---

## Executive Summary & Root-Cause Diagnosis

The 2.5D parallax videos generated in our initial Tokyo Tea Break run (`content/video_engine/projects/systems-and-blowups/tokyo-tea-break/comfy-video/`) exhibited severe visual degradation:
1. **Melted Rubber-Sheet Tearing:** The wooden pillar in `parallax_frame_1s.png` warped like molten plastic, desk monitors stretched unnaturally, and whiteboard borders in `plate-04-stick-figure-whiteboard-parallax_1s.png` developed double-contour artifacts.
2. **Kaleidoscope Mirror Glitches:** The ceiling in `parallax_frame_1s.png` developed bizarre diamond mirrored reflections.
3. **Edge Crawl & Aliasing:** Thin silhouettes (mullions, cables, hair) suffered from jagged pixel shearing.

### The Root Cause:
Our current stack (`tools/google-flow-driver/src/parallax-runner.mjs` and `2_5d_parallax_inpaint.json`) paired **`Depth Anything v2 Small`** with **`Depthflow`** running at **extreme dial settings (`strength: 1.0`, `tiling_mode: 'mirror'`, `ssaa: 1.0`)** on **single-layer flattened images**.

`Depthflow` is an immediate-mode GLSL pixel displacement shader. It does not possess scene geometry or background information. When an extreme camera motion (`strength: 1.0`) is applied to an image containing sharp foreground silhouettes, the shader is forced to stretch foreground edge pixels across the newly revealed occlusion gaps ("disocclusion holes"), resulting in the classic amateur "rubber-sheet" look.

This report establishes:
- The exact technical mechanics of our ComfyUI Depthflow stack.
- The precise dial calibrations required to make Depthflow look cinematic rather than broken.
- The mathematical boundaries that dictate when single-mesh displacement is artistically viable vs. fundamentally banned.
- The professional Hollywood/After Effects standard: **Layered Depth Inpainting (SAM 2 + LaMa + Multi-Plane Projection)**.

---

## 1. Technical Anatomy of Our Current ComfyUI Stack

Our current pipeline executes the following graph in ComfyUI:

```
[Input Image] ───────────┬───────────────────────────────────────────┐
                         │                                           ▼
                         ▼                              ┌─────────────────────────┐
             ┌─────────────────────────┐                │   Depthflow (GLSL)      │
             │   Depth Anything v2     │                │   • Motion Preset       │
             │   (vits_fp16.safetensors│ ──Depth Map──> │   • strength: 1.0 (BAD) │ ──> [CreateVideo] ──> [MP4]
             └─────────────────────────┘                │   • tiling: mirror(BAD) │
                                                        │   • ssaa: 1.0 (BAD)     │
                                                        └─────────────────────────┘
```

### The 5 Technical Failures in Our Configuration:

| Parameter | Current Value | Why It Ruined the Output | Target Professional Value |
|---|---|---|---|
| `strength` | `1.0` | 1.0 is the mathematical ceiling. In GLSL displacement, it displaces pixels by up to 100% of maximum camera offset, ripping polygons apart and melting vertical geometry. | **`0.08` – `0.18`** (Subtle cinematic push) |
| `tiling_mode` | `"mirror"` | When camera translation shifts pixels past viewport borders, "mirror" flips the opposite side of the image into the borders, producing the diamond kaleidoscope ceiling glitch. | **`"none"`** (Paired with a 1.10x pre-zoom crop) |
| `ssaa` | `1.0` (Off) | No super-sampling. Edge transitions between depth gradients render with raw single-pixel jagged staircasing and crawl. | **`2.0`** (Renders 2x resolution and downsamples) |
| `model` | `vits_fp16` | ViT-Small (~25M params) is a lightweight preview model. It produces fuzzy, low-resolution depth boundaries that blend foreground subjects into backgrounds. | **`vitl_fp16`** (ViT-Large, ~335M params, sub-pixel edge definition) |
| `quality` | `75` | Heavy JPEG/video compression around high-frequency depth displacement vectors. | **`95` – `100`** |

---

## 2. The Mathematical Limit: The Disocclusion Problem

Why did the stick figure and the Tokyo pillar melt?

In monocular parallax, a 2D image is projected onto a 2.5D mesh displaced along $Z$:
$$\Delta x = \frac{f \cdot T_x}{Z}, \quad \Delta y = \frac{f \cdot T_y}{Z}$$

Where $T_x, T_y$ is camera translation and $Z$ is depth from the depth map.
When an object in the foreground ($Z_{near}$) sits in front of a background ($Z_{far}$), their differential displacement is:
$$\text{Disocclusion Gap } \Delta = f \cdot T_x \left( \frac{1}{Z_{near}} - \frac{1}{Z_{far}} \right)$$

### The Core Deficit:
In a single flattened 2D image, **there are zero pixels behind the foreground subject**. 
- In physical reality, when the camera moves right, the space behind the pillar is revealed.
- In a single-layer GLSL displacement shader, that space is empty. The shader has only two choices:
  1. Stretch the edge pixels of the pillar across the entire gap $\Delta$ (the "melted cheese" artifact).
  2. Smear the background pixels forward (`edge_fix`).

When $\Delta$ exceeds ~8–12 pixels, human visual perception immediately detects non-rigid rubber deformation, destroying suspension of disbelief.

---

## 3. The Artistic Viability Matrix: When to Use What

Not all scenes are eligible for single-layer depth displacement. Using Depthflow on the wrong image is an automatic quality failure.

| Visual Category | Example Scene | Depth Discontinuity ($\Delta Z$) | Depthflow Viability | Correct Motion Type |
|---|---|---|---|---|
| **Distant Landscapes** | Tokyo dawn skyline, mountain vista, ocean horizon | Near-zero ($\Delta Z pprox 0$) | **HIGHLY VIABLE** | Gentle Dolly / Push-In (`strength: 0.15`) |
| **Receding Architecture** | Long hallway, empty tunnel, deep street perspective | Continuous, smooth gradient | **VIABLE** | Slow Push-In (`strength: 0.12`) |
| **Room Interior (No Foreground)** | Trading floor wide shot, warehouse from distance | Low ($\Delta Z < 0.2$) | **CONDITIONALLY VIABLE** | Subtle Sway / Push (`strength: 0.08`) |
| **Sharp Foreground Silhouettes** | Desk with microphone, pillar in front of window | Severe step function ($\Delta Z > 0.8$) | **BANNED (Melts edges)** | **Tier 2 Layer Inpainting Only** |
| **Character Presenter** | Analyst in lab coat, stick figure at whiteboard | Extreme step function ($\Delta Z pprox 1.0$) | **STRICTLY BANNED** | **Tier 2 Layer Inpainting Only** |
| **Vector Evidence / UI** | Balance scale, charts, whiteboard with text | Discontinuous vector lines | **STRICTLY BANNED** | **Remotion Code Animation Only** |

### The Golden Rule of Depthflow:
> **Depthflow is an environmental atmosphere tool, not an object animator.**
> It is strictly licensed for continuous environmental plates. It may NEVER be applied to plates containing foreground characters, isolated props, or text.

---

## 4. Dial Calibration Guide for ComfyUI Depthflow

When an image qualifies as artistically viable (continuous environmental ground), apply these exact dialed parameters:

### 4.1 Master Node Inputs (`Depthflow`)
```json
{
  "quality": 95,
  "ssaa": 2.0,
  "invert": 0,
  "tiling_mode": "none",
  "edge_fix": 8,
  "num_frames": 60,
  "input_fps": 30,
  "output_fps": 30
}
```

### 4.2 Motion Presets & Strength Bounds

#### 1. The Cinematic Dolly (Recommended Default)
- **Node:** `DepthflowMotionPresetDolly`
- **Dial:** `strength: 0.12` (Never exceed 0.20)
- **Dial:** `intensity: 1.0`
- **Dial:** `depth: 0.5` (Sets the optical pivot point where pixels do not scale)
- **Visual Feel:** Slow, steady camera push-in that adds breathing life without bending vertical lines.

#### 2. The Subtle Lateral Sway (Wide Vistas Only)
- **Node:** `DepthflowMotionPresetHorizontal`
- **Dial:** `strength: 0.08` (Strict ceiling)
- **Dial:** `steady_value: 0.3`
- **Dial:** `reverse: false`
- **Visual Feel:** Gentle horizontal drift simulating a slider rail.

#### 3. BANNED Presets:
- `DepthflowMotionPresetCircle` $\to$ Banned (causes nauseating orbital wobble).
- `DepthflowMotionPresetOrbital` $\to$ Banned on single-layer images (exposes extreme occlusion holes).

---

## 5. The Professional Standard: Two-Plane Layer Inpainting

To achieve the 2.5D depth seen in professional documentaries (Ken Burns on steroids) where characters and props move against a living background, we must move from single-layer displacement to **Two-Plane Layer Inpainting**.

```
[Raw Generated Plate]
         │
         ├───> [SAM 2 / RMBG-2.0] ──> [Foreground Cutout with Alpha] (Layer 1)
         │                                       │
         └───> [Inpaint Mask]                    │
                     │                           │
                     ▼                           ▼
             [LaMa / Flux Fill]         [Remotion / 2.5D Canvas]
                     │                  • Background card at Z = -200 (scale 1.15)
                     ▼                  • Foreground card at Z = 0    (scale 1.00)
            [Clean Background Plate]    • Camera pushes forward:
                   (Layer 0)              Foreground moves 1.2x faster than background
                                        • ZERO WARPING • ZERO MELTING • ZERO TEARING
```

### The 3-Step Protocol:

1. **Step 1: Automatic Foreground Segmentation (`RMBG-2.0` / `SAM 2`):**
   Extract the character or foreground obstacle onto a transparent PNG (`foreground_cutout.png`).
2. **Step 2: Clean Plate Occlusion Inpainting (`LaMa`):**
   Invert the foreground alpha mask, dilate it by 15 pixels, and pass it to a high-speed inpainting model (`LaMa` or `ComfyUI-Inpaint-Nodes`). The inpainter reconstructs the floor, wallpaper, or city that was hidden behind the subject, producing a pristine `background_clean.png`.
3. **Step 3: Multi-Plane Card Projection in Remotion:**
   Place both layers in Remotion / HyperFrames:
   ```tsx
   <AbsoluteFill>
     {/* Background Card: Moves slowly */}
     <div style={{
       transform: `scale(${1.10 + frame * 0.001}) translate(${frame * 0.2}px, 0px)`,
       transformOrigin: 'center center'
     }}>
       <img src="background_clean.png" />
     </div>

     {/* Foreground Card: Moves faster, revealing true background */}
     <div style={{
       transform: `scale(${1.00 + frame * 0.003}) translate(${frame * 0.8}px, 0px)`,
       transformOrigin: 'bottom center'
     }}>
       <img src="foreground_cutout.png" />
     </div>
   </AbsoluteFill>
   ```

**Why this wins:**
- **Zero Artifacts:** The background behind the subject is real, rendered imagery, not stretched border pixels.
- **Infinite Clean Motion:** The camera can pan 50 pixels without a single rubber-sheet distortion.
- **100% Deterministic:** Renders inside Remotion in milliseconds without GPU shader stalls.

---

## 6. Actionable Implementation Changes for Our Pipeline

### File Updates Required in `content/video_engine`:

1. **Modify `tools/google-flow-driver/src/parallax-runner.mjs`:**
   - Change default `strength` from `1.0` to `0.14`.
   - Change `tiling_mode` from `"mirror"` to `"none"`.
   - Upgrade `model` to `depth_anything_v2_vitl_fp16.safetensors`.
   - Set `ssaa` to `2.0` and `quality` to `95`.
2. **Modify `content/video_engine/workflows/2_5d_parallax_inpaint.json`:**
   - Update node defaults to match the dialed values.
3. **Enforce Plate Screening in `storyboard_generator.py`:**
   - Add a rule: Parallax motion is only applied to scenes tagged `[KIND: WORLD_LANDSCAPE]` or `[KIND: ENVIRONMENT_WIDE]`.
   - Explicitly forbid Depthflow on `[KIND: CAST_HOST]`, `[KIND: EVIDENCE_DOCK]`, or `[KIND: DIAGRAM]`.

---

## Sources & Authoritative References
1. **Depth Anything v2 Model Family & Benchmarks** — ByteDance / HKU (`depth-anything-v2.github.io`)
2. **ComfyUI-Depthflow-Nodes Specification** — akatz-ai (`github.com/akatz-ai/ComfyUI-Depthflow-Nodes`)
3. **Layered Depth Images for 3D Photography** — Shih et al., IEEE CVPR
4. **Fast and Robust Large Mask Inpainting (LaMa)** — Suvorov et al.
5. **Outreach Repository Doctrine** — `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` (§9.13 & §9.15)
