# Deep Technical Monograph 10: Generative Video Foundations (Wan 2.1, LTX-Video, Depth Suite) & 9:16 vs. 16:9 Cross-Platform Architecture

**Authoritative Technical Treatise, Dial Calibration Dictionary, and Production Blueprints**  
*Operation: Outreach Video Engine (Money Physics, Building Money, Martial Matters)*  
*Target Stack: ComfyUI (Local GPU), Remotion / HyperFrames (Render Engine), Whisper Acoustic Gate M13*  
*Document Classification: Tier 1 (Engineering Specifications) & Tier 2 (Calibrated Dials & Design Blueprints)*

---

## Executive Overview: The Generative Video & Cross-Platform Triad

This monograph standardizes the technical mastery, mathematical mechanics, and best practices of our core generative video models alongside responsive cross-platform stage composition:

1. **Alibaba Wan 2.1 Family (`Wan2.1-1.3B` & `Wan2.1-14B`):** Rectified Flow Matching DiT, 3D Causal Wan-VAE ($4k+1$ frame clock), UMT5-XXL + CLIP-Vision dual conditioning, TeaCache 2.2x acceleration, and resolution-dependent scheduler shift calibration.
2. **Lightricks LTX-Video (`LTX-Video 0.9.1 / 0.9.5 2B DiT`):** Spatio-Temporal Attention, 1:192 compression Causal VAE ($N = 8n + 1$ frame rule), sub-12s consumer GPU generation, Spatio-Temporal Guidance (STG layer 19 perturbation), CFG Star Rescaling, and mask-pinned latent inpainting for 100% frozen character/data boundaries.
3. **The Depth & Spatial Guidance Suite ("Deep..."):** Depth Anything V2 (synthetic ray-traced DINOv2+DPT, zero gradient haze), DepthCrafter (CVPR 2025 highlight: temporally consistent video depth diffusion), ComfyUI-Depthflow-Nodes GLSL ray-marching shader calibration (`intensity` vs `strength` bug resolution), and Wan 2.1 Fun-Control depth-guided video generation for 0% character morphing.
4. **9:16 vs. 16:9 Cross-Platform Composition & Short vs. Long Form:** Exact mobile UI dead zones (TikTok, YouTube Shorts, Instagram Reels), the Universal Clean Canvas ($800 \times 1060\text{ px}$), resolution of the $68.4\%$ horizontal area loss via the 3-Zone Vertical Stage, short-form swipe-retention kinetics vs. long-form six-phase ($P_1 \to P_6$) dialectic, and dual-format Remotion/HyperFrames execution blueprints.

---

## Part 1: Alibaba Wan 2.1 (Wan-Video) Technical Mastery

### 1.1 Model Taxonomy & Clarifications
- **Primary Reference:** *Wan: Open and Advanced Large-Scale Video Generative Models* (Alibaba Group, arXiv:2503.20314, Apache 2.0).
- **Core Models:**
  1. `Wan2.1-T2V-1.3B`: Text-to-Video lightweight DiT (1.3B params). Optimized for native 480P ($832 \times 480$). Fits in ~8.2 GB VRAM in FP16.
  2. `Wan2.1-T2V-14B`: Text-to-Video flagship DiT (14.2B params). Supports native 480P and 720P ($1280 \times 720$).
  3. `Wan2.1-I2V-14B-480P` & `Wan2.1-I2V-14B-720P`: Dedicated Image-to-Video flagship checkpoints.
  4. Specialized variants: `Wan2.1-VACE` (Video Creation and Editing: inpainting/outpainting), `Wan2.1-FLF2V-14B-720P` (First-and-Last-Frame interpolation), and `Wan2.1-Fun-1.3B-InP` (Alibaba-PAI lightweight inpainting).
  *(Note on 1.3B I2V: Alibaba did not release a base `Wan2.1-I2V-1.3B` checkpoint; consumer 1.3B I2V is achieved via `Wan2.1-Fun-1.3B-InP` or `Wan2.1-VACE-1.3B`).*

### 1.2 Mathematical Foundations: Rectified Flow Matching
Wan 2.1 replaces curved DDPM Gaussian diffusion with straight-line probability trajectories:
$$x_t = t \cdot x_1 + (1 - t) \cdot x_0, \quad v_t = \frac{dx_t}{dt} = x_1 - x_0$$
$$\mathcal{L}_{\text{FM}}(\theta) = \mathbb{E}_{t, x_0, x_1} \left[ \| v_\theta(x_t, t, c) - (x_1 - x_0) \|^2 \right]$$
Timesteps $t$ are sampled from a logit-normal distribution. Because probability trajectories are straight, high-order solvers (UniPC, Flow Euler) converge cleanly in **20 to 30 steps**, cutting computational cost in half compared to curved Gaussian ODEs.

### 1.3 DiT Architecture & 3D Causal Wan-VAE
- **DiT Dimensions:**
  - 1.3B: 30 layers, hidden dim 1536, 12 heads, FFN dim 8960.
  - 14B: 40 layers, hidden dim 5120, 40 heads, FFN dim 13824.
- **3D Causal Wan-VAE (127M params):**
  - Spatial compression: $8\times \times 8\times$. Temporal compression: $4\times$ ($s=4$). Latent channels: $C=16$.
  - Uses RMSNorm to eliminate cross-frame normalization drift.
  - Temporal feature caching enables streaming video decode of arbitrary lengths without seam lines.
  - **The $4k+1$ Frame Clock Rule:** Given temporal stride $s=4$ with an isolated frame-0 anchor, valid frame counts must satisfy:
    $$T = 4k + 1 \quad (k \in \mathbb{Z}^+) \implies 17, 33, 49, 65, \mathbf{81}, 97, 113$$
    *Standard baseline: 81 frames @ 16 fps = 5.06 seconds.*

### 1.4 Dual Conditioning Architecture (I2V)
1. **Latent Scaffolding (Spatial Concatenation):** First frame $I$ is padded with $T-1$ zero frames, encoded to $z_c$ (16 channels), and concatenated with noisy latent $z_t$ (16 channels) and rearranged binary mask $m$ (4 channels) $\to$ **36 total input channels**.
2. **Decoupled Cross-Attention:** umT5-XXL text embeddings (4.4B params) and OpenCLIP ViT-H/14 visual embeddings are injected via separate cross-attention projections in every DiT block.

### 1.5 Acceleration & VRAM Profiles
- **Precision:** FP8 e4m3fn (~14.5 GB weights) or GGUF Q5_K_M (~10.8 GB weights).
- **Sequential Offloading:** ComfyUI automatically offloads text encoder (umT5) to CPU before DiT forward pass, bounding peak VRAM to model weight + activation memory.
- **TeaCache (Timestep Embedding Aware Cache):**
  $$\Delta t_{\text{emb}} = \frac{\| \text{emb}(t_k) - \text{emb}(t_{k-1}) \|_1}{\| \text{emb}(t_{k-1}) \|_1}$$
  If $\Delta t_{\text{emb}} < \text{threshold}$, transformer forward passes are skipped.
  - `threshold = 0.15` + 10% step warmup retention yields a **~2.2x speedup** with zero perceptual loss.
- **SageAttention:** INT8/FP8 QK matrix multiplication delivers a 2x-3x speedup over FlashAttention-2.

### 1.6 Calibrated Dials & Failure Fixes (Wan 2.1)
| Parameter / Dial | Production Default | Function & Bounds |
|---|---|---|
| **Steps** | **25** | 20–30 optimal for Flow Matching. >35 yields diminishing returns. |
| **CFG (T2V)** | **6.0** | 5.0–6.0 for clean prompt adherence. |
| **CFG (I2V)** | **3.5 – 4.0** | **Strictly keep $\le 4.5$**. CFG $>5.5$ causes frame burning and visual jitter. |
| **Scheduler Shift** | **`3.0`** (480P) / **`5.0`** (720P) | $\sigma_{\text{shifted}} = \frac{\text{shift} \cdot \sigma}{1 + (\text{shift} - 1) \cdot \sigma}$. Stretches high-noise region for macro geometry. |
| **Text Encoder** | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | Must use **scaled** FP8. Unscaled weights produce NaNs and black frames. |
| **VAE Weights** | Unquantized FP16/BF16 | Never quantize Wan-VAE; quantized VAE causes blotchy color banding. |

---

## Part 2: Lightricks LTX-Video (0.9.1 / 0.9.5 2B DiT) Technical Mastery

### 2.1 Architecture & Spatio-Temporal Attention
- **Primary Reference:** *LTX-Video: Realtime Video Latent Diffusion* (Lightricks Research, arXiv:2501.00103).
- **Core Backbone:** 28 transformer blocks, hidden dim 2048, 32 heads, FFN inner dim 8192 (~1.9B to 2.0B params).
- **Unified 3D Token Attention:** Unifies spatial and temporal attention into a single 3D sequence. Tokens carry fractional spatio-temporal coordinates $\text{coord} = (t/\text{FPS}, y, x)$ modulated via 3D Rotary Position Embeddings (3D RoPE).
- **Ultra-High Compression 3D Causal VAE:**
  - Spatial compression: $32\times \times 32\times$ ($8\times$ conv hierarchy $+ 4\times$ patchifier).
  - Temporal compression: $8\times$.
  - Latent depth: 128 channels.
  - Overall compression ratio: **1:192** (1 latent token per $32 \times 32 \times 8 \times 3 = 24,576$ RGB values).

### 2.2 The $N = 8n + 1$ Frame Rule
Because the causal 3D VAE encodes frame 0 as an isolated anchor and then groups every subsequent 8 frames into a single temporal latent step:
$$F_{\text{latent}} = 1 + \frac{N - 1}{8} \implies \mathbf{N = 8n + 1} \quad (n \in \mathbb{N}_0)$$
- $n = 3 \implies \mathbf{25\text{ frames}}$ (~1.0s @ 25 fps)
- $n = 6 \implies \mathbf{49\text{ frames}}$ (~2.0s @ 24/25 fps)
- $n = 9 \implies \mathbf{73\text{ frames}}$ (~3.0s @ 24/25 fps)
- $n = 12 \implies \mathbf{97\text{ frames}}$ (~4.0s @ 24 fps)
- $n = 15 \implies \mathbf{121\text{ frames}}$ (~5.0s @ 24 fps, 16 latent steps)
*Violation Penalty: Supplying arbitrary counts (e.g. 50 or 100 frames) causes temporal phase misalignment, leading to frame flashing and severe end-of-clip corruption.*

### 2.3 Spatio-Temporal Guidance (STG) Mechanics
To prevent character and structural melting over time without blowing out contrast:
$$\epsilon_{\text{final}} = \epsilon_{\text{uncond}} + w_{\text{cfg}}(\epsilon_{\text{text}} - \epsilon_{\text{uncond}}) + w_{\text{stg}}(\epsilon_{\text{text}} - \epsilon_{\text{perturb}})$$
- **Perturbation Block:** Attention computation on **Layer 19** is bypassed, substituting raw values $V$. Guiding away from this uncoordinated state forces the model to synthesize rigid, temporally cohesive motion.
- **CFG Star Rescaling:** Normalizes guidance vectors to prevent contrast blowout:
  $$\alpha = \frac{\langle\epsilon_{\text{text}}, \epsilon_{\text{uncond}}\rangle}{\|\epsilon_{\text{uncond}}\|^2 + \epsilon}, \quad \text{rescaling\_scale} = 0.70$$

### 2.4 Mask-Pinned Inpainting (100% Frozen Subject Latents)
To freeze foreground characters and charts while generating organic background atmospheric motion:
$$\text{current\_timestep} = \min(\text{current\_timestep}, 1.0 - \text{conditioning\_mask})$$
- Foreground mask $M=0$ clamps the denoising timestep to $0.0$, freezing latent pixels bit-for-bit.
- Background mask $M=1$ denoises freely.
- Edge rule: Snap mask boundaries to $32 \times 32$ latent blocks (`BlockifyMask`) with a 4px blur to prevent edge fringing.

### 2.5 Calibrated Dials & Benchmarks (LTX-Video)
| Parameter | Full Model Setting | Distilled Model Setting | Purpose |
|---|---|---|---|
| **Steps** | 25 | 8 | Denoising steps. |
| **CFG Scale** | 3.2 – 3.5 | 1.0 – 1.2 | Text adherence. Strictly avoid $>4.5$. |
| **STG Scale** | 1.0 (`skip=[19]`) | Disabled | Spatio-temporal motion stabilizer. |
| **CRF on Guide Image** | 28 – 32 | 28 – 32 | H.264 compression on input image to free motion dynamics. |
| **Inference Time (5s clip)** | **~9.5 – 12.0s** (RTX 4090) | **~3.2 – 4.5s** (RTX 4090) | Ultra-low-compute generation. |
| **VRAM Footprint** | ~8–10 GB (FP8) | ~6–8 GB (GGUF) | Fits on consumer 8GB–12GB cards. |

---

## Part 3: The Depth & Spatial Geometry Suite ("Deep...")

### 3.1 Depth Anything V2 (NeurIPS 2024)
- **Paper:** *Depth Anything V2* (Yang et al., HKU & TikTok, arXiv:2406.09414).
- **Core Breakthrough:** Replaced noisy real sensor depth (LiDAR dropouts, transparent glass voids) with **595K synthetic ray-traced images** + 62M pseudo-labeled real images distilled from a 1.3B ViT-Giant teacher.
- **Acuity:** Completely eliminates the 5–15px gradient haze of V1. Preserves razor-thin structures (antennas, fingers, pen tips, washi paper deckle edges) with step-function depth boundaries.
- **Model Choice:** Production standard is `depth_anything_v2_vitl_fp32.safetensors` (~335M params, 2.8 GB VRAM).

### 3.2 DepthCrafter: Temporally Consistent Video Depth (CVPR 2025 Highlight)
- **Paper:** *DepthCrafter: Generating Consistent Long Depth Sequences for Open-world Videos* (Hu et al., Tencent AI Lab & HKUST, arXiv:2409.02095).
- **The Flicker Problem:** Per-frame Depth Anything V2 suffers from scale/shift drift $D_t = s_t D^* + t_t$ and patch-attention jitter ($14 \times 14$ tokens), causing scenes to violently breathe along the Z-axis.
- **The DepthCrafter Solution:** Fine-tunes Stable Video Diffusion (SVD-xt) into a conditional video-to-depth diffusion model:
  - 3D spatio-temporal convolutions enforce multi-frame geometric smoothness.
  - Native 110-frame training window.
  - Sliding-window stitching ($W=110, O=25$) with noise initialization anchoring enables infinite-length temporally locked video depth.
  - Speed: **~465 ms/frame** @ 1024×576 on RTX 4090.

### 3.3 ComfyUI-Depthflow-Nodes Mastery & Bug Resolution
ComfyUI-Depthflow-Nodes (`depthflow.glsl`) executes an image-space continuous heightfield ray-march:
1. **Ray March Mechanics:** Pinhole camera rays march forward through $Z_{surf}(u,v) = \text{height} \cdot D(u,v)$ until penetration, followed by binary secant search refinement.
2. **The Disocclusion Gap Formula:**
   $$\Delta = f \cdot T_x \left( \frac{1}{Z_{near}} - \frac{1}{Z_{far}} \right)$$
   - $\Delta \le 8\text{ px}$: Clean, imperceptible parallax cliff.
   - $\Delta > 20\text{ px}$: Single-mesh stretches foreground edge pixels, causing rubber-sheet melting.
3. **The `strength` vs. `intensity` Bug Resolution:**
   - In `custom_nodes/ComfyUI-Depthflow-Nodes/src/base_flex.py:66`, `strength` is bypassed when `feature is None`.
   - `intensity` in `depthflow_motion_presets.py:13` is the actual camera translation multiplier.
   - **Fix:** In `tools/google-flow-driver/src/parallax-runner.mjs`, clamp `intensity` from `1.0` down to `0.10 - 0.12`.

### 3.4 Geometry-Locked Depth-to-Video Generation (0% Character Morphing)
- **Architecture:** Alibaba's `Wan2.1-Fun-14B-Control` (or AnimateDiff Depth ControlNet).
- **Decoupling Geometry from Appearance:**
  1. Author pure 3D camera move as a video depth sequence $\mathbf{D}(x, y, t)$ via DepthCrafter or Blender.
  2. Inject depth latents into DiT blocks via zero-convolution ControlNet layers with control strength $0.85 - 0.95$.
  3. The diffusion model is constrained to synthesizing surface albedo and lighting *over the locked geometry*, completely eliminating facial morphing, finger mutations, and perspective popping.

---

## Part 4: 9:16 vs. 16:9 Cross-Platform Architecture & Short vs. Long Form

### 4.1 Mobile UI Safe Zones (1080 × 1920)
Mobile platforms overlay aggressive, asynchronous UI elements on vertical video. All critical text, vector ink, numbers, and evidence must reside within the intersection of all three platforms:

```
0 px ───────────────────────────────────────────────────────────── (Top of 1080x1920 Frame)
     │  TOP UI DEAD ZONE (Y: 0 to 280 px | 14.6%)                 │
     │  - Platform search, headers, status bar, phone notch       │
280 px ──────────────────────────────────────────────────────────── (Universal Upper Boundary)
     │                                                     │      │
     │  UNIVERSAL CLEAN CANVAS                             │ R    │
     │  (X: 80 to 880 px, Y: 280 to 1340 px)               │ I    │
     │  - Area: 800 x 1060 px (40.9% total canvas area)     │ G    │
     │  - THE CREAM LEDGER PAGE (#F4E6C7):                 │ H    │
     │    All charts, FRED lines, balance scales, vector   │ T    │
     │    ink, equations, callouts, and primary evidence   │      │
     │                                                     │ R    │
     │                                                     │ A    │
     │                                                     │ I    │
1340 px ───────────────────────────────────────────────────│ L    │
     │  DYNAMIC KINETIC CAPTION STRIP                      │      │
     │  (X: 80 to 880 px, Y: 1340 to 1440 px | Height: 100px)    │ (200px)
1440 px ───────────────────────────────────────────────────┴──────│ (Universal Lower Boundary)
     │  BOTTOM UI DEAD ZONE (Y: 1440 to 1920 px | 25.0%)          │
     │  - Subscribe pill button, captions, audio marquee, scrub   │
1920 px ────────────────────────────────────────────────────────── (Bottom of Frame)
```

- **Active Safe Bounding Box:** $x \in [80, 880]$, $y \in [280, 1340]$ ($800 \times 1060\text{ px}$).
- **Feed & Grid Protection:** Nests perfectly within Instagram's 1:1 profile grid ($1080 \times 1080$, $y \in [420, 1500]$) and 4:5 feed display ($1080 \times 1350$, $y \in [285, 1635]$).

### 4.2 Aspect Ratio Transformation Strategies
#### The Failure of Center-Crop / Dynamic Pan & Scan
Cropping a 16:9 frame ($1920 \times 1080$) to 9:16 ($607.5 \times 1080$) results in an immediate **$68.36\%$ horizontal area loss**:
$$\text{Area Lost} = 1 - \frac{607.5}{1920} = 1 - \frac{81}{256} = \mathbf{68.36\%}$$
This amputates macroeconomic time-series charts (FRED), destroys side-by-side balance scale metaphors (Lakoff & Johnson), and triggers high ocular search saccades ($180\text{--}220\text{ms}$ latency).

#### The 3-Zone Vertical Stage Solution
Partition the $1080 \times 1920$ canvas into three distinct vertical zones:
1. **Zone 1: Hook & Metric Headline ($y \in [140, 480]\text{ px}$, $H=340\text{ px}$):** Category tag + bold narrative hook + live delta metric.
2. **Zone 2: 16:9 Evidence Canvas / Ledger Card ($y \in [480, 1340]\text{ px}$, $H=860\text{ px}$):** Houses our signature Cream Ledger Page (`#F4E6C7`) card ($1000 \times 562.5\text{ px}$) centered at $y=628.75\text{ px}$. Retains 100% of data charts with zero horizontal crop.
3. **Zone 3: Kinetic Captions & Host Rig ($y \in [1340, 1800]\text{ px}$, $H=460\text{ px}$):** Word-level kinetic typography ($y=1380\text{ px}$) + host hand pointing rig docked to the card bottom.

---

### 4.3 Short-Form vs. Long-Form Production Architecture

| Dimension | Short-Form (15–60s Shorts/TikTok) | Long-Form (8–20m+ Video Essay) |
| :--- | :--- | :--- |
| **Hook Window** | **0.0–3.0s**: Immediate visual anomaly, high stakes. | **0–90s ($P_1$)**: Atmospheric setup, systemic tension. |
| **Algorithmic Threshold** | **Viewed vs. Swiped Away $>75\%$**. | **CTR $>7\%$ + AVD $>50\%$**. |
| **Visual Pulse Rhythm** | **Every 1.2–2.5 seconds** (reset fixation decay). | **Average Shot Length (ASL) 6–10 seconds**. |
| **Cognitive Scope** | **Cognitive Atomicity**: Exactly 1 mechanism/claim. | **6-Phase Architecture ($P_1 \to P_6$)**: Compound proof. |
| **Subtitle Standards** | 1–3 words kinetic pop, $56\text{px}$ font, $7\text{px}$ halo. | Conventional subtitle bar or clean documentary VO. |
| **Acoustic Snapping** | Whisper silence $\ge 0.30\text{s}$ (Gate M13). | Whisper silence $\ge 0.30\text{s}$ (Gate M13). |

---

## Part 5: Production Code Blueprints

### Blueprint 1: Unified Remotion Root (`Root.tsx`)
Configures dual rendering from a single scene contract:
```tsx
import React from "react";
import { Composition } from "remotion";
import { LedgerSceneMaster } from "./compositions/LedgerSceneMaster";
import { LedgerSceneVertical } from "./compositions/LedgerSceneVertical";
import ledgerData from "./data/s03_debt_spread_engine.json";

const FPS = 30;
const DURATION_FRAMES = Math.round((ledgerData.clock.end_sec - ledgerData.clock.start_sec) * FPS);

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 16:9 Long-Form Master */}
      <Composition
        id="Master16x9"
        component={LedgerSceneMaster}
        durationInFrames={DURATION_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{ sceneData: ledgerData, aspect: "16:9" as const }}
      />

      {/* 9:16 Short-Form Vertical */}
      <Composition
        id="Vertical9x16"
        component={LedgerSceneVertical}
        durationInFrames={DURATION_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{ sceneData: ledgerData, aspect: "9:16" as const }}
      />
    </>
  );
};
```

### Blueprint 2: Affine Coordinate Remapping Matrix
Converts normalized coordinates $(u, v) \in [0, 1]^2$ on the Ledger Board between formats:
- **16:9 Master ($1920 \times 1080$):**
  $$X_{16:9}(u) = 122 + 1669 u, \quad Y_{16:9}(v) = 75 + 929 v$$
- **9:16 Vertical 3-Zone Stage ($1080 \times 1920$):**
  $$\begin{bmatrix} X_{9:16} \\ Y_{9:16} \\ 1 \end{bmatrix} = \begin{bmatrix} 1000 & 0 & 40 \\ 0 & 562.5 & 628.75 \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} u \\ v \\ 1 \end{bmatrix}$$

---

## Part 6: Cross-Model Capability Comparison

| Feature / Metric | Alibaba Wan 2.1 (14B / 1.3B) | Lightricks LTX-Video (2B DiT) | Depthflow + Depth Anything V2 |
|---|---|---|---|
| **Underlying Math** | Flow Matching (Rectified Flow) | Spatio-Temporal Diffusion DiT | GLSL Heightfield Ray Marching |
| **Model Size** | 14.2B / 1.3B params | 2.0B params | ~335M params (ViT-Large) |
| **VRAM Footprint** | 10.8 GB (Q5_K_M) – 14.5 GB (FP8) | 6.0 GB (GGUF) – 8.5 GB (FP8) | 2.8 GB VRAM |
| **Inference Time (5s)** | ~45–70s (14B) / ~12–18s (1.3B) | **~9.5 – 12.0s** (Full) / **~3.5s** (Distilled) | **~2.5 – 4.0s** |
| **Native Frame Rate** | 16 fps | 24 fps / 25 fps | Arbitrary (driven by timeline) |
| **Frame Clock Rule** | **$T = 4k + 1$** (81 frames) | **$N = 8n + 1$** (121 frames) | N/A |
| **Best Pipeline Role** | High-fidelity photoreal world plates & cinematic actions | Mask-pinned ambient ground motion (drifting smoke/lighting) | Lightweight continuous background parallax ($\Delta \le 8\text{px}$) |
| **Character Stability** | High (with ControlNet Depth) | 100% frozen via latent masking ($M=0$) | Banned on foreground characters |
| **In-Video Text** | Moderate (umT5 layout capability) | Poor (scrambles text into noise) | Banned (stretches text pixels) |

---

## Authoritative Engineering Directives

1. **Enforce the Frame Arithmetic:**
   - For Wan 2.1: strictly submit $T = 4k + 1$ frames ($17, 33, 49, 65, \mathbf{81}$).
   - For LTX-Video: strictly submit $N = 8n + 1$ frames ($25, 49, 73, 97, \mathbf{121}$).
2. **Apply Latent Mask-Pinning ($M=0$):**
   - In LTX-Video and Wan-InP pipelines, clamp foreground character and ledger latents to $t=0.0$ to guarantee **0% text/character drift**.
3. **Calibrate Depthflow Intensity:**
   - In `tools/google-flow-driver/src/parallax-runner.mjs`, clamp `intensity` to `0.10 - 0.12` and set backbone to `depth_anything_v2_vitl_fp32.safetensors`.
4. **Deploy the 3-Zone Vertical Stage:**
   - For 9:16 vertical exports, dock the 16:9 Cream Ledger Card into Zone 2 ($y \in [480, 1340]$) and constrain all text to the Universal Clean Canvas ($800 \times 1060\text{ px}$), preventing $68.4\%$ area loss and clearing all mobile UI overlays.
