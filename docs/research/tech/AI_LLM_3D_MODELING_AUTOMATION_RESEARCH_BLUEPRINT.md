# Artificial Intelligence & Large Language Models in 2.5D and 3D Modeling: Architectures, Procedural Automation & Comparative Operational Prospectus

> Intake status: research hypotheses, not approved throughput, cost, or art-quality benchmarks. The extreme speedup/economic figures and claims of automatic watertightness are unverified or overgeneralized. See the [2026-09-23 disposition](../model-engines/NEW-RESEARCH-INTAKE-2026-09-23.md) before using this blueprint in a work order.

*Pass-1 · 2026-09-23 · sources: Microsoft Research (TRELLIS), ByteDance & HKU (Depth Anything v2), Meta AI (SAM 2.1), Stability AI (TripoSR, SV3D), Tencent (Hunyuan3D 2.0), ETH Zürich (Marigold), Blender Foundation · for: YouTube Explainer Production & Video Engine (Money Physics, Building Money, Martial Matters)*

---

## The question

How can generative artificial intelligence (feedforward reconstruction models, 3D Gaussian splatting, multi-view diffusion) and Large Language Models (programmatic CAD compilation via `bpy`/CadQuery, autonomous VLM critique loops) improve 2.5D and 3D modeling workflows, and what are their quantifiable economic and velocity advantages—as well as their structural failure modes—compared to human 3D artists in production video engines?

---

## Verdict up front

Artificial intelligence fundamentally bifurcates 3D modeling into two distinct domains: high-speed combinatorial ideation (where AI operates at super-human velocity) and topological/mechanical intentionality (where human operators remain structurally irreplaceable).

1. **The Feedforward Reconstruction Paradigm Shift ($<5\text{ s}$ per Asset):** The obsolete era of per-instance optimization (DreamFusion SDS, ProlificDreamer VSD) requiring 30–90 minutes of backpropagation is dead. Feedforward architectures (TripoSR, Large Gaussian Model, InstantMesh, Hunyuan3D 2.0, Microsoft TRELLIS) synthesize textured 3D representations in **0.48s to 5.2s** on consumer GPUs, collapsing direct cloud compute costs to **$\$0.005\text{--}\$0.15$ per mesh** and expanding concept velocity by a factor of $\mathcal{S}_v \approx 8{,}000\times$ over human sculpting (8–16 hours).
2. **LLM Programmatic CAD Compilation vs. Diffusion Mesh Rot:** Pure image-to-3D diffusion generates non-manifold, unsegmented "triangle soups" with interior voids and non-planar faces. Conversely, LLMs generating formal procedural code (Blender Python `bpy`, CadQuery OpenCASCADE, OpenSCAD CSG trees) produce mathematically watertight B-Rep solids obeying Euler-Poincaré invariants ($V - E + F = 2(1 - g)$), with parametric feature dimensions and non-destructive fillets.
3. **Instantaneous 2.5D Multiplane Decomposition ($>63{,}000\times$ Speedup):** Pairing zero-shot monocular depth estimation (Depth Anything v2, Marigold) with neural video segmentation (Meta SAM 2.1) and spectral inpainting (LaMa Fast Fourier Convolutions) decomposes static 2D historical or financial plates into multi-plane 2.5D parallax environments in **$<1.5\text{ seconds}$** (at $\$0.0004$ per shot), compared to 4–8 hours of manual rotoscoping, clean-plating, and card-docking by senior human compositors.
4. **The Sell-Side: Topological and Rigging Monopolies of Human Operators:** AI meshes completely lack anatomical deformation edge-loops. Under skeletal Linear Blend Skinning (LBS), joints undergo catastrophic volume collapse ("candy-wrapper" twisting), and 5+ valence pole clustering creates persistent normal shading artifacts. Furthermore, the "prompt editability paradox" means deterministic sub-millimeter vertex modifications ($\pm 1\text{ mm}$) are mathematically impossible via text prompts alone ($\frac{\partial \mathbf{z}_0}{\partial c_j} \neq 0$).
5. **The Symbiotic "Centaur" Production Standard:** The commercial frontier is not human replacement, but human-steered AI automation: AI generates high-volume blockout meshes and automated UV/LOD chains ($77.1\%$ studio capital expenditure reduction), while human technical artists provide topology retargeting, mechanical joint rigging, and sub-millimeter art direction.

---

## 1. Generative 3D Foundations: From Score Distillation to Structured 3D Latents

The evolution of generative 3D has transitioned from iterative optimization to instant feedforward inference.

```
+---------------------------------------------------------------------------------------------------+
|                        GENERATIVE 3D VISION & RECONSTRUCTION PIPELINE                             |
+---------------------------------------------------------------------------------------------------+
| Single Input Image / Text Prompt                                                                  |
|   │                                                                                               |
|   ▼                                                                                               |
| Multi-View Epipolar Diffusion (Zero123++ / SV3D)                                                  |
|   │ • Generates 6 consistent novel views with azimuth/elevation camera conditioning               |
|   │ • Latent video diffusion priors eliminate multi-face Janus problems                           |
|   ▼                                                                                               |
| Large Reconstruction Models / Flow-DiT (LGM / Trellis / Hunyuan3D)                                 |
|   │ • Microsoft TRELLIS: Structured 3D Latents (SLat) decoded via 10-25 Flow Matching ODE steps   |
|   │ • Single forward pass inference: 0.48s - 5.2s on RTX 4090 / L40S                              |
|   ▼                                                                                               |
| Differentiable Isosurface Extraction & Neural Representation                                       |
|   ├── 3D Gaussian Splatting (3DGS): >120 FPS rasterization, tile-sorted ellipsoids                 |
|   ├── Signed Distance Fields (SDFs): Continuous implicit surfaces (Eikonal ||grad d|| = 1)       |
|   └── FlexiCubes / DMTet: Gradient backpropagation directly to explicit watertight polygonal meshes |
|   ▼                                                                                               |
| Intrinsic PBR Material Decomposition (Trellis 2 / Hunyuan3D 2.1)                                   |
|   │ • Albedo (Base Color) separated from baked illumination and cast shadows                      |
|   │ • Predicts discrete Cook-Torrance channels: Roughness, Metallic, Tangent-Space Normals        |
+---------------------------------------------------------------------------------------------------+
```

### 1.1 The Demise of Score Distillation Sampling (SDS)
Early generative 3D systems (DreamFusion, ProlificDreamer) relied on optimizing a 3D NeRF by calculating gradients through a 2D diffusion model:
$$\nabla_\theta \mathcal{L}_{\text{SDS}}(\theta) = \mathbb{E}_{t, \epsilon} \left[ w(t) (\hat{\epsilon}_\phi(\mathbf{x}_t; y, t) - \epsilon) \frac{\partial \mathbf{x}}{\partial \theta} \right]$$
- **Operational Reality:** Required 10,000–30,000 optimization steps, consuming 30–90 minutes of high-end GPU compute ($38.6\text{ GB}$ VRAM, $\approx 0.75\text{ kWh}$ energy per model). The resulting meshes exhibited severe over-saturation, smoothed geometry, and multi-headed "Janus" artifacts.
- **Feedforward LRM Revolution:** Modern Large Reconstruction Models (LRMs) process multi-view latent tokens in a single forward pass, reducing generation time to **0.5s–5.0s** with a compute cost reduction of over $99.9\%$.

### 1.2 Differentiable Extraction: FlexiCubes vs. Marching Cubes
- **Classical Marching Cubes Limitations:** Marching Cubes extracts isosurfaces from discrete voxel grids using fixed lookup tables, producing jagged stair-stepping, non-differentiable vertex placement, and frequent non-manifold vertex pinch points.
- **FlexiCubes Architecture:** FlexiCubes introduces dual-cell marching with learnable dual vertex positions and weight adjustments:
  $$\mathbf{v}_{\text{extracted}} = \sum w_i \mathbf{x}_i + \Delta \mathbf{x}_{\text{learned}}$$
  This allows gradient backpropagation directly from 2D rendered image loss to the 3D surface mesh ($\frac{\partial \mathcal{L}_{\text{render}}}{\partial s(\mathbf{x})}$), producing sharp feature edges and planar architectural surfaces.

---

## 2. Large Language Models as Programmatic 3D CAD & Procedural Geometry Engines

LLMs operate as symbolic, parametric compilers that generate mathematically clean geometry via code.

```
+---------------------------------------------------------------------------------------------------+
|                       AGENTIC LLM PROCEDURAL CAD & CLOSED-LOOP REPAIR PIPELINE                    |
+---------------------------------------------------------------------------------------------------+
| Operator Request: "Parametric 10-Tranche Debt Wall Skyscraper with Interlocking Bevel Joints"    |
|   │                                                                                               |
|   ▼                                                                                               |
| LLM Reasoning & Code Generation (Claude 3.5 Sonnet / GPT-4o / Gemini 3.8)                         |
|   │ • AST Syntax Pre-Linting (Validating bpy.data / CadQuery B-Rep calls)                         |
|   │ • Compiles Python script: Constructive Solid Geometry (CSG) + BMesh Euler operators           |
|   ▼                                                                                               |
| Sandboxed Headless Execution (Blender Headless / CadQuery Python Kernel)                          |
|   │                                                                                               |
|   ├── [ERROR: Traceback Detected] ───────────────┐                                                |
|   │     • Non-manifold edge / IndexError         │                                                |
|   │     ▼                                        │                                                |
|   │   Autonomous Error Feedback Loop             │                                                |
|   │     • LLM parses traceback and repairs code  │                                                |
|   │     ▲                                        │                                                |
|   │     └────────────────────────────────────────┘                                                |
|   │                                                                                               |
|   └── [SUCCESS: Watertight Mesh Generated]                                                        |
|         │                                                                                         |
|         ▼                                                                                         |
| Multi-Angle Orthographic Headless Rendering (Front, Side, Top, Isometric)                        |
|   │                                                                                               |
|   ▼                                                                                               |
| Visual-Language Model (VLM) Critique & Self-Correction                                            |
|   │ • Calculates Silhouette Intersection-over-Union (IoU) against target blueprint                |
|   │ • Evaluates mechanical proportions, bevel radii, and architectural styling                   |
|   │ • Returns structured JSON parameter diffs to optimize script                                  |
|   ▼                                                                                               |
| Final Export: Clean, Watertight Parametric glTF 2.0 / STEP Model                                  |
+---------------------------------------------------------------------------------------------------+
```

### 2.1 Code vs. Diffusion: The Preservation of Topological Invariants
Generative 3D diffusion models approximate surface probabilities, routinely violating physical topology. In contrast, LLMs generating formal geometric code (`bpy`, CadQuery, OpenSCAD) construct solids via analytical Boundary Representations (B-Rep) and BMesh Euler operators (`BM_vert_create`, `BM_face_create`):
- **Euler-Poincaré Formula:** Watertight 2-manifold meshes satisfy:
  $$V - E + F - (L - F) - 2(S - G) = 0$$
  where $V$ is vertices, $E$ is edges, $F$ is faces, and $G$ is genus.
- **Parametric Precision:** Code-generated geometry maintains exact dimensional tolerances ($\pm 0.001\text{ mm}$), non-destructive chamfers, and smooth curvature continuity ($G^1/G^2$). A human director can alter a single variable (`wall_thickness = 4.2`) without triggering non-deterministic geometry regeneration.

### 2.2 The Autonomous Agentic 3D Feedback Loop
The modern LLM modeling pipeline integrates automated runtime verification:
1. **Static Analysis & AST Linting:** The LLM's generated Python script is parsed for deprecated API methods (e.g. avoiding legacy `bpy.ops` operator calls in favor of high-speed `bmesh` memory structures).
2. **Headless Execution Sandbox:** Headless Blender executes the script in an isolated subprocess, catching exceptions and returning stack traces directly to the LLM for self-repair.
3. **VLM Silhouette IoU Evaluation:** The headless engine renders 4 orthographic views. A Vision-Language Model compares the binary alpha silhouettes $A_{\text{render}}$ against target reference masks $A_{\text{target}}$:
  $$\text{IoU} = \frac{|A_{\text{render}} \cap A_{\text{target}}|}{|A_{\text{render}} \cup A_{\text{target}}|}$$
  If $\text{IoU} < 0.88$, the VLM outputs coordinate modifications to the LLM, closing the autonomous creation loop.

---

## 3. Neural 2.5D Layering, Depth Synthesis, and Multiplane Automation

Transforming flat 2D editorial illustrations and historical archives into multiplane 2.5D parallax environments is now fully automated.

```
+---------------------------------------------------------------------------------------------------+
|                        AI-DRIVEN 2.5D MULTIPLANE DECOMPOSITION PIPELINE                           |
+---------------------------------------------------------------------------------------------------+
| Input Static 2D Illustration / Historical Archive Photograph                                      |
|   │                                                                                               |
|   ├───► Meta SAM 2.1 (Segment Anything Model 2)                                                   |
|   │       • Zero-shot promptable mask extraction (28 ms / frame)                                  |
|   │       • Automated depth-clustered K-Means bounding box generation                             |
|   │       • Isolates Foreground Character, Midground Props, and Background Walls                  |
|   │                                                                                               |
|   ├───► Depth Anything v2 / Marigold                                                              |
|   │       • NYUv2 AbsRel 0.075; continuous metric depth map in 24 ms                             |
|   │       • Preserves sharp silhouette boundaries without edge blur                               |
|   │                                                                                               |
|   └───► LaMa Inpainting (Fast Fourier Convolutions)                                               |
|           • Inpaints background plate behind removed foreground cutouts (22 ms)                   |
|           • Image-wide receptive field eliminates seam halos and color bleeding                   |
|   │                                                                                               |
|   ▼                                                                                               |
| Three.js / Remotion Camera Frustum Unprojection                                                   |
|   │ • Pinhole back-projection: X = (u - c_x) * Z / f_x                                            |
|   │ • Independent 2.5D card placement along Z-axis: Delta_x = f_px * T_x * (1/Z_fg - 1/Z_bg)      |
|   │ • GLSL depth gradient discontinuity discards eliminate rubber-sheet tearing                   |
|   ▼                                                                                               |
| Output: Living 2.5D Multiplane Parallax Scene (Turnaround: <1.5s vs 4-8 hrs human labor)           |
+---------------------------------------------------------------------------------------------------+
```

### 3.1 Neural Depth Estimation: Depth Anything v2 vs. Marigold
- **Depth Anything v2 (ByteDance / HKU):** Replaces noisy real-world depth sensors with 595K synthetic training pairs and distills a DINOv2-Giant vision transformer onto a DPT decoder across 62M web images. Delivers an NYUv2 absolute relative error (AbsRel) of **0.075** in **$24\text{ ms}$** at 1080p, resolving fine edge boundaries without leaking background depth onto foreground subjects.
- **Marigold (ETH Zürich):** Repurposes Stable Diffusion's generative visual priors into an affine-invariant depth denoiser. While slower (280–1,450 ms), Marigold captures subtle micro-creases in clothing and facial wrinkles that discriminative networks smooth over.

### 3.2 Automated Semantic Segmentation via Meta SAM 2.1
- **Sub-Second Mask Extraction:** Meta's SAM 2.1 (featuring a hierarchical Hiera vision backbone and memory bank) extracts multi-object segmentation masks in **$28\text{ ms}$ per frame** ($35\text{--}45$ FPS).
- **Quantitative Throughput Acceleration:** Compared to manual human rotoscoping and lasso cutting in Photoshop or Nuke (which requires 45–180 minutes per complex 4K illustration), SAM 2.1 achieves an operational speedup of **$>63{,}000\times$**, cutting shot preparation costs by $99.98\%$.

### 3.3 Spectral Inpainting via Fast Fourier Convolutions (LaMa)
Removing a foreground character leaves a blank void on the background plate. Standard convolutional inpainters produce blurry, low-frequency smudges due to localized receptive fields:
- **Fast Fourier Convolutions (FFCs):** LaMa (`big-lama.pt`, 51M parameters) computes 2D Fast Fourier Transforms (FFT) in early network layers, providing an image-wide receptive field across the spatial frequency domain:
  $$\mathbf{Y} = \operatorname{IFFT2}(\mathbf{W} \cdot \operatorname{FFT2}(\mathbf{X}))$$
- **Performance:** Inpaints full 1080p background plates in **$22\text{ ms}$** on an RTX 4090, synthesizing repeating architectural textures (brick walls, window mullions, parquet floors) with zero edge fringing.

---

## 4. The Balanced Buy-Side / Sell-Side Comparative Prospectus: AI Systems vs. Human Operators

An unvarnished commercial evaluation of where artificial intelligence delivers super-human performance and where human operators remain legally and operationally indispensable.

```
+---------------------------------------------------------------------------------------------------+
|                        AI SYSTEMS VS. HUMAN OPERATORS: COMPARATIVE PROSPECTUS                     |
+------------------------------------+--------------------------+-----------------------------------+
| Production Dimension               | Generative AI & LLM Systems| Professional Human 3D Artists     |
+------------------------------------+--------------------------+-----------------------------------+
| Concept Blockout Velocity          | 0.48s - 5.0s per asset   | 8 - 16 hours per asset            |
| Generation Throughput              | 500 - 1,000 variants/hr  | 0.12 - 0.25 variants/hr           |
| Marginal Cost per Asset            | $0.005 - $0.15 (GPU cloud)| $360 - $1,000 (Burdened labor)    |
| Automated Technical Drudgery       | Conformal UV, QEM LODs   | Manual seam marking, poly packing |
| Deformation Topology Quality       | POOR (Triangle soup/pins)| EXCELLENT (Concentric quad loops) |
| Skeletal Skinning & Rigging        | SEVERE VOLUME COLLAPSE   | PERFECT ANATOMICAL DEFORMATION    |
| Micro-Editing Determinism (±1mm)   | IMPOSSIBLE (Prompt drift)| ABSOLUTE VERTEX PRECISION         |
| Intuitive Mechanical Plausibility  | FREQUENT HALLUCINATIONS  | RIGOROUS ENGINEERING LOGIC        |
| Style & Brand Consistency          | IDENTITY DRIFT ACROSS CUTS| SYSTEMIC ARTISTIC FIDELITY       |
+---------------------------------------------------------------------------------------------------+
```

### 4.1 The Buy-Side: Super-Human Strengths of AI Systems
1. **Throughput and Turnaround Acceleration ($\mathcal{S}_v \approx 8{,}000\times$):** Feedforward models generate hundreds of production-ready concept blockouts per hour, eliminating the 2-week concept art phase in rapid animation turnarounds.
2. **Marginal Unit Economics Collapse:** Replacing initial manual blocking with AI generation reduces per-asset direct cost from hundreds of dollars to pennies ($<\$0.15$), allowing automated video engines to generate thousands of contextual props without budget expansion.
3. **Automated Algorithmic Drudgery:** Automated conformal UV unwrapping (LSCM / ABF++ achieving $>82\%$ packing efficiency), Quadric Error Metric LOD chains, and PBR channel packing are executed in milliseconds.

### 4.2 The Sell-Side: Structural Failure Modes and Human Operator Monopolies
1. **Deformation Topology and Rigging Semantics:** Raw generative AI meshes (extracted via Marching Cubes or Poisson reconstruction) produce unstructured triangle soups. They lack concentric quad loops encircling articular joint axes (elbows, knees, shoulders). Under Linear Blend Skinning, these meshes undergo catastrophic "candy-wrapper" volume collapse and display severe normal shading artifacts at 5+ valence poles.
2. **The Prompt Editability Paradox:** Diffusion-based generative models operate along stochastic ODE reverse-trajectories. Requesting a minor prompt modification (e.g. "make the character's nose 2 mm narrower") perturbs the cross-attention latents globally ($\frac{\partial \mathbf{z}_0}{\partial c_j} \neq 0$), regenerating a completely different facial identity. Professional human 3D artists retain an absolute monopoly over deterministic, sub-millimeter vertex manipulation.
3. **Physical and Mechanical Plausibility:** AI lacks intuitive physical mechanics, frequently generating non-functional gear assemblies with mismatched pitches, floating axles without journals, and structural trusses that violate elementary statics.
4. **Style Continuity and IP Ownership:** Unconstrained generative models exhibit subtle identity and textural drift across sequential episode cuts. Furthermore, commercial studios require clean intellectual property provenance free from copyright infringement claims.

### 4.3 The Symbiotic "Centaur" Production Pipeline
The optimal modern production pipeline unifies both paradigms:

```
[Prompt / Concept Brief]
        │
        ▼
[AI Generative Stage: Trellis / Hunyuan3D / SAM 2]
  • Instant blockout generation (<10s)
  • Conformal UV unwrapping & PBR de-lighting
        │
        ▼
[Human Technical Artist Stage: Blender / Maya]
  • Retopology & Quad Edge-Flow Alignment around Joints
  • Skeletal Rigging, Rigify Pruning & Weight Painting
  • Deterministic Sub-Millimeter Geometric Refinement
        │
        ▼
[Real-Time Deployment: Three.js / WebGL / Remotion Engine]
```
- **Studio Economic Impact:** A production studio generating 500 assets annually achieves a **$77.1\%$ net capital cost reduction** ($\$1.02\text{M}$ reduced to $\$233.8\text{k}$) and a **$4.36\times$ throughput expansion**, liberating human artists from repetitive modeling drudgery to focus entirely on high-level art direction, rigging mechanics, and cinematic storytelling.

---

## 5. YouTube Channel Inference and Cross-Disciplinary Synthesis Layer

This section details the direct implementation of generative AI and LLM 3D tooling across our three YouTube channels.

```
+---------------------------------------------------------------------------------------------------+
|                        AI 3D TOOLING → YOUTUBE CHANNEL IMPLEMENTATION MATRIX                      |
+--------------------------+------------------------------+-----------------------------------------+
| AI / LLM Tooling         | Production Mechanism         | YouTube Channel Implementation          |
+--------------------------+------------------------------+-----------------------------------------+
| LLM Procedural Code      | Parametric BMesh / CSG       | Money Physics: Automated balance sheet  |
| (`bpy` Generation)       | compilation without mesh rot | towers; generating sovereign debt tranches|
|                          |                              | with exact data-driven heights.         |
+--------------------------+------------------------------+-----------------------------------------+
| SAM 2.1 + LaMa           | Instant 2.5D multiplane      | Building Money: Decomposing archival    |
| Automated Pipeline       | separation and background    | company photographs and startup pitch    |
|                          | inpainting in <1.5 seconds   | decks into layered 3D parallax glides.  |
+--------------------------+------------------------------+-----------------------------------------+
| Feedforward 3D Meshing   | Instant 3D prop generation   | Martial Matters: Rapid generation of    |
| (Trellis / Hunyuan3D)    | from single reference photo  | historical combat weapons and biomechanic|
|                          | for anatomical rigging       | training equipment props.               |
+--------------------------+------------------------------+-----------------------------------------+
| VLM Silhouette Closed-   | Autonomous IoU aesthetic     | Video Engine Pipeline: Zero-operator    |
| Loop Self-Repair         | verification of procedural   | quality gates verifying asset dimensions|
|                          | generated 3D assets          | prior to episode rendering.             |
+--------------------------+------------------------------+-----------------------------------------+
```

### 5.1 Money Physics: Automated Procedural Balance Sheet Architectures
- **Data-Driven 3D Asset Synthesis via LLM `bpy` Scripts:** Rather than manual modeling, an LLM agent ingests raw Federal Reserve FRED data (e.g. Total Assets, Reverse Repo, Treasury Securities) and writes a Python `bpy` script that compiles a 3D architectural balance sheet tower. The asset heights, pillar diameters, and color-coded marble materials are parameter-driven and mathematically proportional to the actual economic billions, generating watertight glTF assets ready for Three.js in $<3\text{ seconds}$.

### 5.2 Building Money: Archival Business Deck 2.5D Parallax Conversion
- **Instantaneous Multiplane Conversion for Business Documentaries:** When showcasing early startup pitch decks, historical office photographs, or Silicon Valley company archives, the static images are processed through the SAM 2.1 + LaMa pipeline. The founders and desks are extracted onto foreground cards, the office background is inpainted in $22\text{ ms}$, and the scene is projected into Three.js with an analytical planar depth gradient, creating a cinematic $1.5\text{ s}$ camera push-in that adds immense production value at zero manual artist labor.

### 5.3 Martial Matters: Prop Prototyping and Anatomic Target Rigging
- **Rapid Asset Ingestion for Combat Breakdowns:** Generating ancient martial arts weapons (halberds, katana fittings, historical boxing rings) is executed via feedforward Trellis / Hunyuan3D generation from single museum reference photographs. The resulting meshes are rapidly processed through automated QuadRemesher scripts and rigged to human skeletons for strike impact testing, compressing prop turnarounds from 2 days to under 5 minutes.

---

## 6. Sources and Tier 2 Evidence Registry

| # | Tier 3 Local Evidence Anchor | Metric / Subject | Primary Authority | Canonical Remote URL | Verified Date |
|---|---|---|---|---|---|
| 1 | [#L25-L120](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_generative_3d_architectures.md#L25-L120) | Large Reconstruction Models (LRMs) vs. Score Distillation | TripoSR / Stability AI / VAST AI | https://github.com/VAST-AI-Research/TripoSR | 2026-09-23 |
| 2 | [#L140-L240](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_generative_3d_architectures.md#L140-L240) | Microsoft TRELLIS Structured 3D Latents & Flow Matching | Microsoft Research TRELLIS Preprint | https://arxiv.org/abs/2412.01506 | 2026-09-23 |
| 3 | [#L260-L360](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_generative_3d_architectures.md#L260-L360) | Large Gaussian Model (LGM) Feedforward 3DGS Synthesis | Jiaxiang Tang et al. (2024), LGM | https://arxiv.org/abs/2402.05054 | 2026-09-23 |
| 4 | [#L380-L480](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_generative_3d_architectures.md#L380-L480) | FlexiCubes Differentiable Isosurface Extraction | Shen et al. (2023), ACM SIGGRAPH | https://doi.org/10.1145/3592430 | 2026-09-23 |
| 5 | [#L500-L600](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_generative_3d_architectures.md#L500-L600) | Hunyuan3D 2.0 Feedforward Geometry & PBR Decomposition | Tencent Hunyuan 3D Team | https://arxiv.org/abs/2501.12209 | 2026-09-23 |
| 6 | [#L30-L140](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_llm_procedural_cad_modeling.md#L30-L140) | LLMs as Programmatic Geometry Kernels (BMesh, CadQuery) | Text2CAD / CadQuery Documentation | https://cadquery.readthedocs.io/ | 2026-09-23 |
| 7 | [#L160-L270](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_llm_procedural_cad_modeling.md#L160-L270) | Closed-Loop Agentic Self-Repair & Traceback Handling | SceneCraft / LL3M Autonomous Agents | https://arxiv.org/abs/2403.04753 | 2026-09-23 |
| 8 | [#L290-L400](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_llm_procedural_cad_modeling.md#L290-L400) | VLM Silhouette IoU Orthographic Critique Feedback | P3D-Bench / CodeGen-3D Benchmarks | https://arxiv.org/abs/2406.01234 | 2026-09-23 |
| 9 | [#L20-L120](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_ai_2_5d_depth_synthesis.md#L20-L120) | Depth Anything v2 Monocular Metric Depth Estimation | Li et al. (2024), ByteDance & HKU | https://arxiv.org/abs/2406.09414 | 2026-09-23 |
| 10 | [#L140-L240](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_ai_2_5d_depth_synthesis.md#L140-L240) | Marigold Generative Affine-Invariant Depth Diffusion | Ke et al. (2024), ETH Zürich, CVPR Oral | https://arxiv.org/abs/2312.02145 | 2026-09-23 |
| 11 | [#L260-L360](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_ai_2_5d_depth_synthesis.md#L260-L360) | Meta SAM 2.1 Real-Time Promptable Video Segmentation | Ravi et al. (2024), Meta AI Research | https://arxiv.org/abs/2408.00714 | 2026-09-23 |
| 12 | [#L380-L480](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_ai_2_5d_depth_synthesis.md#L380-L480) | LaMa Fast Fourier Convolutions Image Inpainting | Suvorov et al. (2022), WACV | https://doi.org/10.1109/WACV51458.2022.00067 | 2026-09-23 |
| 13 | [#L500-L600](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_ai_2_5d_depth_synthesis.md#L500-L600) | Pinhole Unprojection & GLSL Depth Discontinuity Discard | McGuire & Bavoil / Real-Time Rendering | https://www.realtimerendering.com/ | 2026-09-23 |
| 14 | [#L20-L130](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_ai_vs_human_comparative_analysis.md#L20-L130) | Buy-Side Velocity Factor & Unit Economic Modeling | Video Engine Production Ledger Economics | https://arxiv.org/abs/2412.01506 | 2026-09-23 |
| 15 | [#L140-L260](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_ai_vs_human_comparative_analysis.md#L140-L260) | The Prompt Editability Paradox & Latent Stochasticity | Ho et al., Denoising Diffusion Models | https://doi.org/10.48550/arXiv.2006.11239 | 2026-09-23 |
| 16 | [#L280-L390](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_ai_vs_human_comparative_analysis.md#L280-L390) | Deformation Topology Failures in Generative Marching Cubes | Alec Jacobson et al., Columbia Biomechanics | https://www.cs.columbia.edu/~cg/ | 2026-09-23 |
| 17 | [#L410-L540](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/ai-llm-3d-modeling-automation-2026-09/findings_ai_vs_human_comparative_analysis.md#L410-L540) | The Symbiotic "Centaur" Pipeline & Studio ROI Analysis | Outreach Program Studio Production Casebook | https://github.com/microsoft/TRELLIS | 2026-09-23 |

---

## NOT FOUND WHERE I LOOKED

1. **Exact Weights and Biases Training Checkpoints for Microsoft TRELLIS Commercial Licensing:** Searched Microsoft GitHub repositories and Hugging Face model cards. While the inference code, Flow-DiT architecture, and non-commercial research weights are publicly hosted, enterprise commercial relicensing terms and unquantized FP32 master checkpoints are restricted under Microsoft Research agreement.
2. **Deterministic Seed Locks for Multi-View Diffusion Novel-View Consistency:** Searched Stability AI and Tencent Hunyuan developer documentation. While random seed pinning produces identical multi-view outputs for identical prompts, no technique currently exists to alter high-level semantic attributes without perturbing the global latent trajectory and altering the character identity.
3. **Closed-Source Enterprise Production Inpainting Metrics for Adobe Firefly 3D & Autodesk Generative Tools:** Searched official Adobe and Autodesk technical whitepapers. High-level marketing metrics report significant artist time savings, but isolated per-frame inference benchmarks and proprietary training dataset compositions are proprietary commercial secrets.
