# 49 — Generative video and the vertical stage

Extracted from `10_generative_video_tools_and_cross_platform_composition.md`.
Status: **reference — not yet folded to portable.**

**Closes X12 and X13**, the two gaps named four hours ago: Wan was absent from every prior
pass, and nothing had addressed 9:16 composition against mobile UI.

**§49.1 found a live defect in shipped code — ours.**

---

## 49.1 The vertical safe box, and the defect it exposed

Mobile platforms overlay UI on up to **59.1 %** of a vertical frame. The intersection that
survives all three platforms:

```
Universal Clean Canvas:  x ∈ [80, 880]   y ∈ [280, 1340]   → 800 × 1060 px
  top dead zone     y ∈ [0, 280]       search, status bar, notch          14.6 %
  bottom dead zone  y ∈ [1440, 1920]   subscribe pill, description, scrub 25.0 %
  right rail        x ∈ [880, 1080]    like, comment, share, avatar       200 px
```

It nests inside Instagram's 1:1 profile grid and 4:5 feed crop, so one box serves all.

### Our 9:16 docks are outside it

`scene-evidence-player.template.html:155-162` — which I wrote:

```css
html[data-aspect="9:16"] .dock   { width: 952px; top: 690px; }
html[data-aspect="9:16"] #dock-1 { left: 64px; }
html[data-aspect="9:16"] #dock-2 { left: 64px; top: 1180px; }
```

| | ours | safe | verdict |
|---|---|---|---|
| left edge | 64 | ≥ 80 | 16 px outside |
| right edge | **1016** | ≤ 880 | **136 px into the right rail — under the like/comment/share buttons** |
| width | **952** | ≤ 800 | **152 px too wide** |
| dock-2 top | 1180 | — | only 160 px of safe height left below it |

**Every evidence dock on every short would be partly covered by platform chrome.** I
placed those numbers by scaling the 16:9 proportions, because I did not know the safe
zones existed. The corrected geometry is `width: 800px; left: 80px`, with the second dock
placed so its bottom clears 1340.

**This is the clearest single payoff of the research week**: a defect in code I wrote,
caught before it shipped a short.

### The 3-zone vertical stage

Centre-cropping 16:9 → 9:16 destroys **68.36 %** of horizontal area
(`1 − 607.5/1920`), which amputates a FRED time series and a balance-scale metaphor
alike. Do not crop; **re-stage**:

| zone | y | holds |
|---|---|---|
| 1 · hook & metric | 140–480 | category chip, headline, live delta |
| 2 · evidence | 480–1340 | **the chart, rebuilt for the portrait frame** — 100 % of the series, on the page's own ground |
| 3 · captions & host | 1340–1800 | word-level kinetic type, host hands docked to the page |

~~The ledger page keeps its own 16:9 proportion *inside* the vertical frame.~~ **Amended
2026-09-05 (operator: "I have no idea why 49.1 would say that").** A 16:9 card floating in a
9:16 frame is the landscape stage shrunk, and it failed on sight on the first Tokyo render:
a chart at 60 % scale, type at 20 px on a phone, the page bleed unfinished, a highlight over
the build. **In portrait the chart IS the world**: the page fills the frame to its deckle,
the charcoal fills the page (E22), the series is re-laid for the tall frame, and every label
clears doc 50's 59 px floor on the 1920 stage. The chart is never cropped; it is re-staged.

## 49.2 Wan 2.1 — the dials

| dial | setting | why |
|---|---|---|
| **frame count** | **`T = 4k+1`** → 17, 33, 49, 65, **81**, 97, 113 | the 3D causal VAE compresses 4× temporally. 81 @ 16 fps = 5.06 s |
| steps | 25 (20–30) | rectified flow matching converges on straight trajectories; >35 is waste |
| **CFG (I2V)** | **3.5–4.0, hard ceiling 4.5** | above ~5.0–5.5 → frame burning and edge strobing |
| CFG (T2V) | 6.0 | |
| scheduler shift | 3.0 @ 480p / 5.0 @ 720p | allocates early steps to macro geometry |
| TeaCache | threshold 0.15, 10 % warmup | **~2.2× speedup, no visual loss** |
| **text encoder** | `umt5_xxl_fp8_e4m3fn_**scaled**` | **unscaled weights produce NaNs and black frames** |
| **VAE** | unquantized FP16/BF16 | **never quantize — quantized VAE gives blotchy colour banding** |

**Note on 1.3B I2V:** there is no standalone `Wan2.1-I2V-1.3B` checkpoint. Consumer 1.3B
image-to-video runs on `Wan2.1-Fun-1.3B-InP` or `Wan2.1-VACE-1.3B`.

The last two rows are the ones that waste a night if you get them wrong — both fail
loudly and non-obviously.

## 49.3 LTX-Video — the dials, and mask pinning

`N = 8n + 1` → 25, 49, 73, 97, **121**, 161. 121 @ 24 fps = 5.04 s. Off-law counts break
causal VAE alignment and cause frame flashing.

| dial | full | distilled |
|---|---|---|
| steps | 25 | 8 |
| CFG | 3.2–3.5 (never > 4.5) | 1.0–1.2 |
| **STG** | **1.0, `skip_block_list=[19]`** | disabled |
| CFG-star rescale | `True`, 0.70 | |
| CRF on the guide image | 28–32 | 28–32 |
| 5 s clip on a 4090 | ~9.5–12 s | ~3.2–4.5 s |

**STG is the anti-melt mechanism.** Attention on layer 19 is bypassed and the model is
guided *away* from that uncoordinated state, which forces temporally cohesive motion.
CFG-star rescaling then normalises the guidance vector so contrast does not blow out.

**Mask pinning is exact, not approximate:**

```
current_timestep = min(current_timestep, 1.0 − conditioning_mask)
```

Foreground `M = 0` clamps the timestep to 0.0 — latents frozen **bit-for-bit**. Background
`M = 1` denoises freely. Snap mask edges to 32×32 latent blocks with a 4 px blur or you
get fringing.

> That is how atmosphere moves behind a chart while **the numbers cannot drift**.

`CRF 28–32 on the guide image` is the counter-intuitive one: deliberately compressing the
input frees motion dynamics in I2V.

## 49.4 The depth suite

- **Depth Anything V2** — `vitl_fp32`, ~335 M params, 2.8 GB. Trained on 595 K synthetic
  ray-traced images plus 62 M pseudo-labelled reals distilled from a ViT-Giant teacher.
  Kills V1's 5–15 px gradient haze and preserves step-function edges on thin structures —
  fingers, pen tips, **the washi deckle**.
- **DepthCrafter** (CVPR 2025) — video depth, not per-frame. Fixes flicker and affine
  scale-shift drift (`D_t = s_t D* + t_t`) with an SVD-xt backbone and overlapping
  windows (W=110, O=25). ~465 ms/frame at 1024×576.
- **Geometry-locked generation** — author the camera move as a depth sequence, inject via
  zero-conv ControlNet at strength 0.85–0.95, and diffusion is restricted to albedo and
  lighting over locked geometry. **Zero facial morph, zero finger mutation, zero
  perspective pop.** This is the real answer to character drift under motion.

## 49.5 The parallax question, now settled three ways

§3.3 cites `base_flex.py:66` and `depthflow_motion_presets.py:13` — the exact lines I read
from the installed node source on 2026-09-04 (45 §45.4). Independent agreement:
**`strength` is bypassed when `feature is None`; `intensity` is the camera translation
multiplier.** Clamp `intensity` to **0.10–0.12**, `tiling_mode: "none"`, 1.10× crop.

Δ ≤ 8 px is imperceptible; Δ > 20 px melts. That bound is now stated identically in `05`,
`06`, `09` and `10`.

## 49.6 Short-form is a different machine

| | short (15–60 s) | long (8–20 m) |
|---|---|---|
| **hook window** | **0.0–3.0 s** — immediate visual anomaly, zero throat-clearing | 0–90 s (P1) atmospheric build |
| **threshold** | **viewed-vs-swiped > 75 %** | CTR > 7 %, AVD > 50 % |
| **visual pulse** | **every 1.2–2.5 s** | ASL 6–10 s |
| **scope** | **cognitive atomicity — exactly one mechanism** | six-phase compound proof |
| captions | 1–3 word kinetic pop, 56 px, 7 px halo | conventional bar |
| cut placement | acoustic gap (M13) | acoustic gap (M13) |

**The visual-pulse row is the one that bites.** A short needs a visual event every
1.2–2.5 s; our long-form ASL is 6–10 s. Those are different engines, and our shorts have
been built on long-form cadence.

**Cognitive atomicity** — exactly one mechanism per short — is the other. It is the
short-form form of the equation spine (46 §46.4): not six variants, but one.

## 49.7 What this changes

| | |
|---|---|
| **closes** | **X12** (Wan absent) and **X13** (9:16 composition) |
| **exposes** | a live defect in `scene-evidence-player.template.html:155-162` — our 9:16 docks sit under platform chrome |
| **adds a gate** | the mobile safe box is mechanically checkable against any 9:16 timeline |
| **confirms** | the parallax resolution, now agreed by four documents and the node source |
| **contradicts nothing** | every dial here is additive; no prior doc is overturned |
| **flags for the shorts lane** | our visual pulse is long-form cadence; shorts want 1.2–2.5 s |

## 49.8 Sources

Wan-Video 2.1 (Alibaba) · Lightricks LTX-Video 0.9.1/0.9.5 · Depth Anything V2 (NeurIPS
2024) · DepthCrafter (CVPR 2025) · `akatz-ai/ComfyUI-Depthflow-Nodes` · platform UI safe
zones (YouTube Shorts, TikTok, Instagram Reels). Primary: `10` whole.
