# 45 — Parallax and plate motion: what may move, how much, and what is banned

Extracted from `05_comfyui_parallax_technical_standards.md` and
`06_unified_ledger_drawing_engine_and_comfy_spec.md` §2–4. Status: **reference — not yet
folded to portable.**

`06` supersedes `05` where they differ: the operator confirms `05` was written first and
`06` followed a further pass on the same code.

---

## 45.1 Why our parallax melted

Depthflow is an **image-space heightfield ray marcher**, not a scene. It coarse-probes
forward across `Z_surf = height × D(u,v)`, then refines backward for sub-texel UV.

In a single flattened image **there are zero pixels behind the foreground.** When the
camera translates, the shader must either stretch the foreground's edge pixels across the
revealed gap or smear background forward. The gap is:

```
Δ = f · Tₓ · (1/Z_near − 1/Z_far)
```

- `Δ ≤ 8 px` — imperceptible.
- `Δ > 20 px` — the shader melts straight pillars and whiteboard borders.

## 45.2 The viability matrix — a gate, not advice

| plate content | depth discontinuity | verdict |
|---|---|---|
| distant landscape, skyline, vista | ≈ 0 | **viable** — gentle dolly |
| receding architecture, hallway | smooth gradient | **viable** — slow push |
| room interior, no foreground | ΔZ < 0.2 | **conditional** — subtle sway only |
| sharp foreground silhouette | ΔZ > 0.8 | **BANNED** — layer inpainting only |
| character presenter | ΔZ ≈ 1.0 | **BANNED** |
| vector evidence, charts, text | discontinuous | **BANNED** — code animation only |

> **Depthflow is an environmental atmosphere tool, not an object animator.** It is never
> applied to a plate containing a foreground character, an isolated prop, or text.

**This closes backlog R5.** Parallax must never be applied to the ledger page — the page
is vector evidence and text, the bottom row of the matrix. Depth on the page comes from
the §43.3 Z-stack instead, which costs no shader and cannot tear.

## 45.3 Our current dials, and what they should be

Read from `tools/google-flow-driver/src/parallax-runner.mjs` on 2026-09-04.

A `DERIVED` tag marks a computed figure: a starting reference to test, never a research finding (R6; E42 2026-09-06).

| dial | our value | target | consequence of ours |
|---|---|---|---|
| `strength` (default, line 11) | `1.0` | see §45.4 | mathematical ceiling |
| `intensity` (lines 35/49/62/76/90/108) | `1.0` hardcoded | `0.08`–`0.15`, ceiling `0.18` [DERIVED: from content/video_engine/sources/reference_analyses/COMFYUI_PARALLAX_TECHNICAL_STANDARDS_RESEARCH.md, a recommended band; the exact ceiling's derivation is not stated there] | maximum displacement |
| `tiling_mode` (line 157) | `"mirror"` | `"none"` + 1.10× pre-zoom crop | **the kaleidoscope ceiling glitch** |
| `ssaa` (line 155) | `1.0` | `1.5`–`2.0` | edge crawl on thin silhouettes |
| `quality` (line 154) | `75` | `80`–`95` | compression around displacement vectors |
| `edge_fix` (line 158) | `5` | `4`–`8` | — |
| model (line 129) | `vits_fp16` | ViT-**Large** | fuzzy depth boundaries blend fg into bg |
| `steady_value` | unset | `0.35`–`0.45` | no fixed pivot plane |

**Banned presets:** `Circle` (orbital wobble), `Orbital` on single-layer (exposes extreme
occlusion holes).

## 45.4 RESOLVED from source — `intensity` is the displacement, `strength` is dead

`05` said `strength` was the killer; `06` said `strength` feeds an inert modulation input
and `intensity` is the real displacement. **Settled 2026-09-04 by reading the installed
node, which is the authority both reports were guessing at:**

`custom_nodes/ComfyUI-Depthflow-Nodes/src/`

- **`base_flex.py:25`** — `"optional": {"feature": ("FEATURE", {"default": None})}`.
  The feature input is optional and defaults to `None`.
- **`base_flex.py:66`** — `if feature is None: return (self.create(0.0, strength, ...),)`
  — the single-preset path.
- **`base_flex.py:103`** — `if feature is not None:` gates the whole modulation block.
  `strength` is consumed *only* inside `modulate_param`, which is only reachable from
  that branch.
- **`motion/depthflow_motion_presets.py:13`** — `intensity` is a **required** FLOAT on
  `DepthflowMotionPreset`, `default 1.0, min 0.0, max 10.0`, passed to `create_internal`.

**Conclusion: `06` is right and `05` is wrong.** Our `strength = 1.0` does nothing at
all — we supply no `feature`, so it is never read. `intensity`, hardcoded to `1.0` in all
six presets, is the actual camera displacement and is 7–12× the recommended range.

This also means **`08`'s targeting was correct** on this one point, and that
`05`'s "`intensity: 1.0` is the correct dolly value" line is wrong and must not be
followed.

**What does not change:** `tiling_mode`, `ssaa`, `quality` and the depth model are
independent of this dispute, both reports agree on them, and `08` never mentions the
first three. They remain defects.

Model precision stays open: `05` says `vitl_fp16`, `06` says `vitl_fp32` with fp16
"strictly banned due to logit underflow." Take ViT-Large; settle precision on a test roll.

## 45.5 The professional standard — multi-plane inpainting

Instead of stretching one mesh:

1. **SAM 2.1** (Hiera, multi-scale pyramids) isolates the foreground to RGBA.
2. **LaMa** (`big-lama.pt`, Fast Fourier Convolution — image-wide receptive field in
   layer 1) reconstructs the occluded background. **~50 ms, ~1.2 GB VRAM, deterministic.**
   Mask dilation `R_grow = ⌈2σ_optical⌉ + 12 px`; `INPAINT_ColorMatch` normalises μ/σ in
   L\*a\*b\* so the fill matches ambient grain.
3. Composite as **cards at different Z in the renderer**, per §43.3.

Zero tearing, because the background behind the subject is real pixels. This is the
correct path for any plate the matrix bans.

## 45.6 Ambient motion without diffusing the subject

LTX-Video 2B DiT with latent noise masking:

```
z_t = (1 − M_lat) ⊙ z_clean + M_lat ⊙ z_t^diffused
```

Where the mask is 0 the latents are clamped to the pristine image — **the actor and the
page do not move at all** — and where it is 1 the model synthesises haze, smoke, drift.

- Frame count must satisfy **`num_frames = 8n + 1`** (121 frames ≈ 5.04 s @ 24 fps).
- CFG `2.5`–`3.2`, hard ceiling `3.5` (higher plasticises).
- 25 steps, Euler FlowMatch. ~8–12 s on local hardware.
- **Re-stitch the pristine cutout over the decoded video** to guarantee zero text or
  character morphing.

This is how a world plate breathes under narration without violating §45.2.

## 45.7 Sources

Depth Anything v2 (ByteDance/HKU) · `akatz-ai/ComfyUI-Depthflow-Nodes` · Shih et al.,
Layered Depth Images, CVPR · Suvorov et al., LaMa · Meta SAM 2.1. Primary: `05` whole,
`06` §2–4.
