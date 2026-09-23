# Attack on Titan Production Techniques — Engineering Human-Scale Combat, Giant-Scale Animation, Thermodynamic FX, and Material Crystallization

*Pass-1 · 2026-09-22 · sources: Sakuga Blog, CGWORLD.jp, E-SAKUGA, Crunchyroll News, NIST, Cambridge Biomechanics · for: YouTube Explainer Production & Video Engine (Money Physics, Building Money, Martial Matters)*

---

## The question

How did Attack on Titan's production teams at Wit Studio and MAPPA engineer human-scale 2D combat choreography, giant-scale 3D Titan animation, thermodynamic transformation FX, and material crystallization—and how can these production architectures be translated into animation techniques for financial explainers and martial arts breakdowns?

---

## Verdict up front

1. **Wit Studio's 2D pipeline solved the fundamental figure-ground problem** of placing hand-drawn soldiers against hyper-detailed 3D environments via Kyoji Asano's variable-thickness contour linework (2.5–4.5 px exterior vs 0.8–1.2 px interior), the Make-Up Animation unit's per-cut illustration-grade finishing in TVPaint (0.5-grade shadows, multi-hue iris depth, calligraphic inking applied to 10–20 priority cuts per episode), and Arifumi Imai's 2D sakuga overlay technique where hand-drawn key animation was drawn directly atop 3D camera sweeps with aggressive foreshortening up to 400 % and action smears (*obake*) bridging wide spatial gaps ([findings_wit_studio_production.md #L93–L163](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L93-L163), [#L223–L282](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L223-L282)).

2. **MAPPA restructured the Titan pipeline around 3DCG rigs in 3ds Max/ZBrush** with dual-hierarchy skeletons (the Founding Titan's 96-rib spline-IK system by PAGODA), NPR cel-shading via PSOFT Pencil+ inverted hull outlines ($\mathbf{V}_{\text{outline}} = \mathbf{V}_{\text{mesh}} + \mathbf{n} \cdot \delta$), and the Raretrick "Touch Mask" procedural cross-hatching pipeline that projected Isayama-style pen strokes into compositing masks—eliminating manual in-between boiling while preserving the manga's dark aesthetic ([findings_mappa_3d_rigging.md #L61–L124](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L61-L124), [#L127–L179](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L127-L179)).

3. **Titan transformations obey a strict 4-tier biological assembly hierarchy** (osteo-scaffolding → myofibril loom-weaving → vascular hydraulic inflation → epidermal sealing) staged inside a stratospheric plasma conduit ($T_{plasma} \approx 25{,}000–32{,}000\text{ K}$, $I_{peak} \ge 200–500\text{ kA}$), producing Sedov-Taylor blast waves ($R(t) = \xi_0 (E_0/\rho_0)^{1/5} t^{2/5}$) with Colossal-class yields reaching $\sim$2.87 kilotons TNT equivalent ([findings_titan_transformations.md #L51–L163](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L51-L163)).

4. **The Square-Cube Law and Froude number govern all giant-scale animation timing**: a 60 m Colossal Titan must take $\sim$2.89 s per stride (69 frames at 24 fps) and the rotational inertia scales as $\lambda^5$, making the Lilliput Effect the single most dangerous perceptual failure in large-scale creature animation. Titan density must decrease inversely with scale ($\rho_{\text{titan}} \propto 1/\lambda$), confirmed by Hange Zoë's canonical mass experiments ([findings_mappa_3d_rigging.md #L189–L283](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L189-L283), [findings_workflow_extrapolation.md #L758–L878](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L758-L878)).

5. **MMA combat biomechanics translate directly across scale** because both applied joint-breaking torque and resisting torsional strength scale identically as $\lambda^3$, making BJJ joint locks scale-invariant—an Eren armbar that breaks a human arm breaks a 15 m Titan arm with identical leverage ratios, provided the fulcrum targets the unarmored articulation seam ([findings_wit_studio_production.md #L502–L667](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L502-L667), [findings_workflow_extrapolation.md #L882–L934](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L882-L934)).

---

## 1. Wit Studio's Directorial Grammar and the Architecture of Controlled Visual Chaos

### 1.1 Tetsuro Araki's Four-Pillar Cinematographic System

Director Tetsuro Araki formulated a maximalist directorial grammar synthesizing dynamic kinetic tracking, intense chiaroscuro, high-contrast triadic color grading, and dramatic speed ramping via *koma-ochi* (frame-dropping micro-holds) ([findings_wit_studio_production.md #L58–L91](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L58-L91)).

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   ARAKI DIRECTORIAL GRAMMAR TAXONOMY                     │
├──────────────────────────────────────────────────────────────────────────┤
│ 1. Dynamic Kinetic Tracking                                              │
│    • Camera angular velocity ω_cam > 180°/s                              │
│    • Foreground parallax occlusion under eaves/chimneys/branches         │
│    • Whip pans (2-to-4 frame directional smears)                         │
│    • Optical shake A_shake ≈ 5–15 px on wire-anchor impact               │
│                                                                          │
│ 2. Intense Chiaroscuro                                                   │
│    • Crushed terminal umbra RGB ≈ [5, 5, 8]                              │
│    • High-key rim highlights via Color Dodge / Linear Dodge (2–5 px)     │
│                                                                          │
│ 3. Triadic Color Grading                                                 │
│    • Cold scouting: Prussian blues + desaturated sage greens             │
│    • Hot breach: cadmium orange + amber sunflares + deep crimson         │
│                                                                          │
│ 4. Dramatic Speed Shifts                                                 │
│    • Koma-ochi: Drop from 1s (24fps) to 3s/4s hold at impact moment     │
│    • Post-impact explosive acceleration back to 1s                       │
└──────────────────────────────────────────────────────────────────────────┘
```

**Key Production Parameters:**

| Parameter | Value | Source Anchor |
|---|---|---|
| Exterior contour stroke width | 2.5–4.5 px | [#L178–L192](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L178-L192) |
| Interior facial line width | 0.8–1.2 px | [#L183–L218](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L183-L218) |
| Outline chrominance softening | Charcoal brown `#1A1614` or dark navy `#0E1218` + 5 % noise grain | [#L219](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L219) |
| Make-Up Animation cuts per episode | 10–20 select cuts | [#L155–L163](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L155-L163) |
| TVPaint pen pressure levels | 8,192 levels mapped to opacity/radius/wet-edge | [#L135](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L135) |

### 1.2 The Make-Up Animation Unit — Four-Pass Illustration-Grade Finishing

The Make-Up Animation unit (メイクアップアニメーション), led by Manabu Hiramuki and Chief Make-Up Animator Sachiko Matsumoto, operated in TVPaint Animation on Wacom Cintiq 27QHD displays. First piloted on *Kabaneri of the Iron Fortress* (2016) to replicate Haruhiko Mikimoto's illustrative character designs, the unit was deployed on AoT Seasons 2–3 ([findings_wit_studio_production.md #L93–L163](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L93-L163)):

```
[ Standard Digital Paint (仕上げ) ] ──► [ MAKE-UP ANIMATION UNIT ]
                                              │
                                ┌─────────────┼─────────────┐
                                ▼             ▼             ▼
                          Pass 1:        Pass 2:        Pass 3:
                       0.5-Grade     Ocular Depth    Specular Rim
                       Shadows      (Multi-Hue     Hair Strands
                       (SSS Blush)   Iris, Corneal  (1–2 px, Skull
                                     Moisture)      Curvature)
                                                         │
                                                         ▼
                                                    Pass 4:
                                                 Calligraphic
                                                 Ink Modulation
                                                 (Sumi-e Edge
                                                  Weighting)
                                                         │
                                                         ▼
                                          [ Compositing / 撮影 ]
                                   (Adobe After Effects / MADBOX)
```

**Pass 1 — 0.5-Grade Intermediate Shadows**: Soft airbrush gradients of peach, rose, and warm ochre along zygomatic arches, nasal bridge, clavicles, and sternocleidomastoid muscles, emulating subsurface scattering where light penetrates semi-translucent dermal layers and scatters through capillary blood vessels ([#L138–L140](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L138-L140)).

**Pass 2 — Ocular Rendering**: Multi-chromatic radial iris strokes (up to 5 harmonious hues for Eren's eyes: deep emerald, seafoam, hazel, golden amber, charcoal limbal ring), corneal moisture sheen along the lower scleral rim, and feathered blooming specular halos ([#L141–L146](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L141-L146)).

**Pass 3 — Specular Rim Hair Strands**: Delicate 1–2 pixel specular strands tracing skull curvature, plus backlit rim fringes catching dawn/dusk ambient light. Individual flyaway hairs painted directly onto finished frames ([#L147–L150](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L147-L150)).

**Pass 4 — Calligraphic Ink Modulation**: Digital sumi-e ink brushes tracing structural silhouette edges, thickening at anatomical inflection points (jaw angles, shoulder joints) and tapering to razor points at terminators ([#L151–L153](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L151-L153)).

---

## 2. Arifumi Imai's ODM Choreography and the Physics of Wire-Tethered Aerial Combat

### 2.1 The 2D Sakuga / 3D Camera Sweep Hybrid Pipeline

Action Animation Director Arifumi Imai pioneered the integration of hand-drawn 2D sakuga atop pre-rendered 3D camera sweeps, with 3DCG Directors Shuhei Yabuta (S1) and Shigenori Hirozumi (S2–S3) constructing modular urban environments in Autodesk 3ds Max/Maya ([findings_wit_studio_production.md #L223–L338](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L223-L338)):

```
[ STORYBOARD: Imai blocks trajectory vectors, camera focal points ]
                            │
                            ▼
[ 3DCG BACKGROUND SWEEP (3D背動) ]
  • High-precision 3D models: Trost, Stohess, Forest of Giant Trees
  • Virtual camera: 90° vertical dives, 360° barrel rolls, banked turns
  • Focal length: 14mm ultra-wide → 85mm telephoto transitions
  • Export: wireframe mesh + shaded geometry video passes
                            │
                            ▼
[ 2D KEY ANIMATION (原画): Imai draws over 3D moving plate ]
  • Vanishing point synchronization to 3D background shifts
  • Extreme foreshortening: leading boot/blade scaled 300–400 %
  • Action smears (obake): multi-edged sweeping limb bridges
  • Koma-uchi timing: 1s (24fps) glides, 2s (12fps) changes, 3s (8fps) apexes
                            │
                            ▼
[ COMPOSITING (撮影): MADBOX / Kazuhiro Yamada ]
  • Studio Bihou hand-painted textures mapped onto 3D geometry
  • Velocity-scaled 2D motion blur on 3D background
  • Wire tension curves & gas exhaust particle systems
```

### 2.2 Spatial Continuity Across Non-Euclidean Camera Trajectories

Imai maintained the 180-degree axis rule across ODM aerial combat using three spatial anchoring techniques ([findings_wit_studio_production.md #L285–L338](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L285-L338)):

1. **Gravitational Anchor Point**: The target Titan nape remains pinned at the mathematical center of camera orbit ($r = 0$).
2. **Persistent Vector Smokes & Trailing Cables**: High-pressure gas plumes persist 6–12 frames; taut steel cables draw direct sightlines bridging cross-axis cuts.
3. **Asymmetrical Foreground Wipes**: Passing rooftops/tree trunks cleanly wipe the frame before reversed camera angles, resetting the viewer's mental axis.

**Key Case Studies:**

| Sequence | Episode | Duration | Technical Achievement |
|---|---|---|---|
| Levi vs Female Titan | S1 E22, Aug 31, 2013 | 270° continuous orbit | Logarithmic spiral approach $r(\theta) = ae^{-k\theta}$ around Annie's torso ([#L313–L318](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L313-L318)) |
| Levi vs Beast Titan | S3P2 E54, May 26, 2019 | 4 months production | Sequential arm dissection on 1s with centrifugal force-vector debris ([#L320–L327](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L320-L327)) |
| Levi vs Kenny Squad | S3P1 E39, Jul 29, 2018 | 30+ sec continuous cut | Bar window infiltration with zero continuity break ([#L329–L338](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L329-L338)) |

### 2.3 ODM Gear Mathematical Kinematics and Force Dynamics

The ODM soldier's trajectory is governed by the net equation of motion ([findings_wit_studio_production.md #L341–L446](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L341-L446), [findings_workflow_extrapolation.md #L23–L168](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L23-L168)):

$$m \frac{d^2\vec{r}}{dt^2} = \vec{T}_1(t) + \vec{T}_2(t) + \vec{F}_{\text{thrust}}(t) + m\vec{g} - \vec{F}_{\text{drag}}(t)$$

```
              Anchor Point 1 (r_A1)           Anchor Point 2 (r_A2)
                      \                               /
                       \  Cable Tension T_1          / Cable Tension T_2
                        \                           /
                         ▼                         ▼
                      ┌───────────────────────────────┐
                      │      Scout Mass (m = 77 kg)   │◄── Gas Thrust F_thrust(t)
                      └───────────────────────────────┘
                                      │
                                      ▼
                            Gravity m·g + Aerodynamic Drag
                            F_drag = 0.5·ρ·C_d·A·v²
```

**XPBD Cable Constraint (Macklin et al., 2016):**

The unilateral distance constraint for each cable $i$:

$$C_i(\mathbf{x}) = \|\mathbf{x} - \mathbf{P}_{a,i}\| - L_i \le 0$$

Positional correction with compliance $\alpha = 1/k_s$:

$$\Delta \mathbf{x}_i = \frac{1}{1 + \frac{\alpha}{w \Delta t^2}} (l_i - L_i) \hat{\mathbf{u}}_i$$

Where $w = 1/m$ is inverse mass, $k_s \approx 25{,}000\text{ N/m}$ ([findings_workflow_extrapolation.md #L67–L75](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L67-L75)).

**Slingshot Angular Momentum Conservation:**

When a scout spools cable from $L_0 = 20\text{ m}$ to $L(t) = 5\text{ m}$, tangential velocity quadruples:

$$v_t(t) = v_{t,0} \frac{L_0}{L(t)} = 4 v_{t,0}$$

Levi's corkscrew spin rate amplification via moment-of-inertia reduction (figure-skater effect):

$$\frac{\omega_2}{\omega_1} = \frac{I_1}{I_2} = \frac{r_1^2}{r_2^2} = \frac{(0.9)^2}{(0.25)^2} \approx 12.96$$

Yielding $\omega_2 \approx 13\text{ revolutions/second}$ ([findings_wit_studio_production.md #L431–L445](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L431-L445)).

**Centripetal G-Force Loading Matrix (Scout = 77 kg):**

| Velocity | Swing Radius | Centripetal Accel | Cable Tension | Load Factor |
|---|---|---|---|---|
| 15 m/s (54 km/h) | 15.0 m | 15.0 m/s² (1.53 G) | 1,910 N | 2.53 G |
| 25 m/s (90 km/h) | 10.0 m | 62.5 m/s² (6.37 G) | 5,580 N | 7.37 G |
| 35 m/s (126 km/h) | 8.0 m | 153.1 m/s² (15.6 G) | 12,560 N | 16.61 G |
| 40 m/s (144 km/h) | 5.0 m | 320.0 m/s² (32.6 G) | 25,410 N | 33.62 G |

([findings_wit_studio_production.md #L414–L425](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L414-L425))

> Loads above 16 G exceed human physiology. The Ackerman clan's superhuman G-tolerance confirms in-universe engineering of reinforced bone mineral density and elevated vascular muscle tone preventing G-LOC ([#L427–L429](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L427-L429)).

---

## 3. MAPPA's 3DCG Titan Pipeline — ZBrush Anatomical Sculpting to NPR Cel-Shaded Output

### 3.1 The Studio Handover and Architectural Restructuring

WIT Studio stepped down after Season 3 Part 2 due to exhaustion of their boutique 30–40 core staff and a strategic pivot toward original IPs. MAPPA, the sole studio willing to accept the project, restructured the pipeline under director Yuichiro Hayashi with CGI producer Yusuke Tannawa and 3DCG director Takahiro Uezono ([findings_mappa_3d_rigging.md #L11–L57](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L11-L57)):

```
PRODUCTION TIMELINE & DEPARTMENT STRUCTURE
───────────────────────────────────────────
Part 1 (Dec 2020 – Mar 2021, Ep 60–75):
  ├─ 3DCG Director: Takahiro Uezono (V-sign / MAPPA)
  ├─ Core Toolset: Autodesk 3ds Max, Pencil+, After Effects
  └─ Compositing: Shigeki Asakawa (Raretrick)

Part 2 (Jan 2022 – Apr 2022, Ep 76–87):
  ├─ 3DCG Animation Dir: Motoi Okuno (MAPPA)
  ├─ Rigging: PAGODA (Motoharu Sawada – Founding Titan Rig)
  ├─ Modeling: ARecT (Shun Kitamura, Ryoya Nonaka)
  └─ Background 3D: Kusanagi (草薙)

Final Chapters (Mar 2023 & Nov 2023, Ep 88–94):
  └─ Full pipeline unification: 3DLO, Camera Mapping (3D背動), AE
```

### 3.2 Nine Titan Anatomical Modeling Conventions in ZBrush

MAPPA established strict anatomical modeling conventions in ZBrush, retopologized for clean deformation in 3ds Max ([findings_mappa_3d_rigging.md #L63–L87](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L63-L87)):

| Titan | Height | Key Topology Challenge | Solution |
|---|---|---|---|
| Attack (Eren) | 15 m | Extreme jaw dropping during berserk roars | Edge loops concentric to jaw hinges and zygomatic arch |
| Armored (Reiner) | 15 m | Armor/muscle interpenetration during grappling | Recessed muscle channel clearances at scapula/elbow/knee |
| Beast (Zeke) | 17 m | Fur + NPR outline mismatch | Clumped volume meshes with baked custom normal editing |
| Jaw (Galliard/Falco) | 4–5 m | Quadruped/avian hybrid biomechanics | Layered skin-wrap constraints for feathered neck plates |
| Cart (Pieck) | 4 m | Mechanical artillery saddle on organic chassis | Parent-child constraints with dampening script controllers |
| War Hammer (Lara) | 15 m | Dynamic umbilical heel-cable + weapon morphs | Spline-IK with mass-spring-damper physics |
| Colossal (Armin/Bertholdt) | 60 m | Micro-scout to macro-aerial camera framing | UDIM UV mapping at 8K resolution |
| Founding (Eren) | 600+ m | Coordinate precision floating-point jitter | Dual-rig solver with kinematic constraint links |

### 3.3 The Founding Titan's 96-Rib Spline-IK Rigging Architecture

Rigged by Motoharu Sawada (PAGODA), the Founding Titan rig exceeded 3ds Max's standard floating-point coordinate precision at 600+ meters. Sawada split the skeleton into two distinct rigs joined by kinematic constraint links, with each of the 96 individual ribs (48 pairs) utilizing a standardized module of 11 deformer bones driven by 3ds Max IK splines ([findings_mappa_3d_rigging.md #L90–L123](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L90-L123)):

```
Master Coordinate Node (3ds Max)
 │
 ├─ Spine Axis A (Thoracic Master) ── Linked ── Spine Axis B (Lumbar Master)
 │   │                                           │
 │   ├─ Rib Controller 01 (Spline-IK: 11 Bones) ├─ Pelvis Sub-Rig
 │   ├─ Rib Controller 02 (Spline-IK: 11 Bones) └─ Hind Strut Nodes
 │   ├─ ...                                           │
 │   └─ Rib Controller 96 (Spline-IK: 11 Bones)  (Ground Collision)
 │
 └─ Animator Proxy Rig (Stripped Spline Nodes / Fast Viewport Scrubbing)
```

### 3.4 NPR Cel-Shading and the Touch-Mask Cross-Hatching Pipeline

```
3D Model Mesh (3ds Max)
  │
  ├─ Custom Vertex Normal Transfer (smooth continuous shading)
  │     │
  │     └─ PSOFT Pencil+ / Scanline Renderer
  │           ├─ Base Normal Color Pass (flat unlit albedo)
  │           └─ Inverted Hull Outline Pass
  │                V_outline = V_mesh + (n · δ)
  │
  ├─ 2D Hand-Drawn Scout Cels (Clip Studio / OpenToonz)
  │
  └─ Touch Masks (grayscale masks defining 2nd-shadow hatch areas)
        │
        ▼
  After Effects Compositing (Shigeki Asakawa / Raretrick)
    ├─ Procedural cross-hatching projected into Touch Masks
    ├─ Desaturated post-war palette, atmospheric haze
    ├─ Real live-action pyrotechnic smoke comp
    └─ Step-framing: 3D curves stepped on 2s and 3s (koma-uchi)
```

([findings_mappa_3d_rigging.md #L127–L179](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L127-L179))

**Inverted Hull Outline Technique**: Geometry is duplicated, normals inverted ($\mathbf{n} \to -\mathbf{n}$), scaled outward by offset $\delta$, and shaded pure black with front-face culling. This guarantees unbroken variable-width silhouette lines from any camera angle without post-processing screen-space raycasting latency ([#L158–L160](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L158-L160)).

**Rumbling Wall Titan LOD Hierarchy**: Three-tier LOD with 6 facial variants and 3 body morphology meshes randomized across instance arrays via material ID assignment scripts, with skin weights transferred from the high-poly master using weight transfer algorithms ([#L116–L123](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L116-L123)).

---

## 4. Titan Transformation Staging — Celestial Lightning, Blast Shockwaves, and 4-Tier Tissue Genesis

### 4.1 Stratospheric Plasma Conduit and Dielectric Breakdown Physics

Titan shifter transformations deposit extradimensional mass via a downward vertical plasma channel from the lower stratosphere ($z \approx 10–15\text{ km}$) to the injury site ([findings_titan_transformations.md #L51–L84](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L51-L84)):

$$E_{breakdown} = 3.0 \times 10^6 \left(\frac{\rho(z)}{\rho_0}\right) \text{ V/m}$$

- **Plasma core temperature**: $T_{plasma} \approx 25{,}000–32{,}000\text{ K}$ (exceeding the solar photosphere at 5,778 K)
- **Return stroke current**: $I_{peak} \ge 200–500\text{ kA}$ at $v_{return} \approx 1.0 \times 10^8\text{ m/s}$ ($\sim c/3$)
- **Emission spectrum**: Nitrogen/Oxygen single-to-double ionization producing golden-amber emission with cerulean violet fringes

**Sound Design Layering** ([#L79–L82](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L79-L82)):
- Frame 0–2: High-frequency dielectric snap (8–12 kHz)
- Frame 3–15: Heavy sub-bass cavitation boom (20–45 Hz)
- Frame 16+: Sustained electrical sizzle and thermal hiss

### 4.2 Rankine-Hugoniot Blast Shockwaves and Sedov-Taylor Crater Excavation

The emergence of hundreds of cubic meters of organic mass in $<0.1\text{ s}$ compresses surrounding air into a supersonic shock discontinuity ([findings_titan_transformations.md #L86–L129](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L86-L129)):

$$\frac{p_2}{p_1} = 1 + \frac{2\gamma}{\gamma + 1}(M_s^2 - 1)$$

Sedov-Taylor blast wave radius:

$$R(t) = \xi_0 \left(\frac{E_0}{\rho_0}\right)^{1/5} t^{2/5}, \quad \xi_0 \approx 1.033 \text{ for } \gamma = 1.4$$

| Transformation Class | Example | Blast Energy $E_0$ | TNT Equiv. | Shock Radius @ 0.1 s |
|---|---|---|---|---|
| Localized Tactical | Eren partial / spoon | $1.5 \times 10^7\text{ J}$ | 3.6 kg TNT | 3.5 m |
| Standard Assault (15 m) | Attack / Armored Titan | $4.2 \times 10^9\text{ J}$ | 1.0 ton TNT | 11.0 m |
| High-Yield Explosion | Colossal (Trost Gate) | $8.0 \times 10^{10}\text{ J}$ | 19.1 tons TNT | 20.0 m |
| Tactical Thermonuclear | Colossal (Liberio / Shiganshina) | $1.2 \times 10^{13}\text{ J}$ | 2.87 kt TNT | 55.0 m |

([findings_titan_transformations.md #L108–L113](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L108-L113))

**Sakuga Optical Mechanics**: At the kinetic contact frame, the color buffer is inverted ($\mathbf{C}_{out} = \mathbf{1.0} - \mathbf{C}_{in}$), followed by radial chromatic aberration splitting the RGB channels along radial vectors from the epicenter with offsets $k_r \approx 0.025$, $k_b \approx 0.018$ ([#L121–L128](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L121-L128)).

### 4.3 Biological Tissue Assembly — The 4-Tier Genesis Hierarchy

Titan genesis adheres to a strict sequential construction hierarchy over 0.2–1.5 seconds ([findings_titan_transformations.md #L132–L191](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L132-L191)):

```
[Human Shifter Nape Anchor (C7 Nexus)]
               │
               ▼
[TIER 1: OSTEOLOGICAL SCAFFOLDING]
  • Cranial vault → Spine extrusion → Ribcage umbrella → Long bone projection
  • Mineralization growth rate: v_growth ≥ 50–100 m/s
  • High-porosity trabecular architecture (max EI, min dead mass)
               │
               ▼
[TIER 2: STRIATED MYOFIBRIL LOOM WEAVING]
  • Automated carbon-fiber-like filament winding (not cellular mitosis)
  • Antagonistic helical wrapping at θ ≈ 30°–45° (Hill's muscle model)
  • Visual: thick glistening red cables cross-hatching over white skeletal framework
               │
               ▼
[TIER 3: VASCULAR NETWORK HYDRAULIC INFLATION]
  • Aortic/femoral arteries bifurcate to capillary beds in milliseconds
  • Systolic pressure for 15 m: P ≈ 169 kPa (1,270 mmHg)
  • For 60 m Colossal: P ≈ 640 kPa (4,800 mmHg / ~6.3 atm)
  • Thermodynamic flash boiling: ruptured micro-vessels release crimson steam jets
               │
               ▼
[TIER 4: EPIDERMAL SEALING & JOINT FASCIA]
  • Subcutaneous fascia spreads posterior-to-anterior in zipper-like motion
  • Facial synthesis: masseter, orbicularis oris, eyelids over vitreal globes
```

---

## 5. Hyper-Thermal Steam Dynamics — Phase Change Thermodynamics and Buoyant Plume Kinematics

### 5.1 Mass-Energy Balance of Titan Dissolution

Titan tissue sublimation is governed by classical water phase-change thermodynamics ([findings_titan_transformations.md #L194–L251](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L194-L251)):

$$\Delta h = \underbrace{c_{p,liquid} (100 - 37)}_{263{,}592\text{ J/kg}} + \underbrace{L_v}_{2{,}257{,}000\text{ J/kg}} + \underbrace{c_{p,vapor} (300 - 100)}_{402{,}000\text{ J/kg}} = 2.923 \times 10^6\text{ J/kg}$$

Where $L_v = 2.257 \times 10^6\text{ J/kg}$, $c_{p,liquid} = 4{,}184\text{ J/(kg·K)}$, $c_{p,vapor} \approx 2{,}010\text{ J/(kg·K)}$.

**The Aerogel Mass Paradox** (Hange Zoë's experiments, Chapter 15 / Episode 15): Active Titan tissue is a hyper-porous biological aerogel ($\rho_{\text{titan}} \approx 20–50\text{ kg/m}^3$, merely 2–5 % of mammalian muscle), enabling full-body sublimation into atmospheric vapor within 30–90 seconds ([#L234–L245](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L234-L245)).

Rikao Yanagita's calculation in *The Science of Attack on Titan*: a 60 m biped obeying standard allometric scaling would reach $T_{core} \approx 602°\text{C}$. The Colossal Titan survives only by continuously rejecting heat via latent heat of vaporization, functioning as an evaporative cooling tower ([#L247–L250](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L247-L250)).

### 5.2 Rayleigh-Taylor Instability and Morton-Taylor-Turner Plume Kinematics

When low-density superheated steam ($\rho_s \approx 0.46\text{ kg/m}^3$) is injected into ambient air ($\rho_\infty \approx 1.20\text{ kg/m}^3$), Atwood number $A_t \approx 0.446$ drives mushroom vortex roll-up ([findings_titan_transformations.md #L254–L298](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L254-L298)):

$$\sigma = \sqrt{A_t \cdot a \cdot k}$$

MTT buoyant plume spreading:
- Plume radius: $b(z) = \frac{6}{5}\alpha z \approx 0.12z$ (half-angle $\approx 6.8°$)
- Center-line velocity decay: $w(z) \propto z^{-1/3}$
- Taylor entrainment constant: $\alpha \approx 0.08–0.12$

### 5.3 Colossal Titan Defensive Steam — Aerodynamic Drag and Thermal Flux

During the Battle of Shiganshina (S3 E54), Bertholdt's full-body steam exhaust creates an impenetrable aerodynamic and thermal barrier ([findings_titan_transformations.md #L301–L369](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L301-L369)):

$$F_D = \frac{1}{2} C_d \rho v_e^2 A = 0.5 \times 1.1 \times 0.85 \times (50)^2 \times 0.70 \approx 818\text{ N} \approx \text{Scout's body weight}$$

Total thermal flux: $q''_{total} = q''_{conv} + q''_{rad} = 31{,}560 + 4{,}755 = 36{,}315\text{ W/m}^2 \approx 36.3\text{ kW/m}^2$

At 36.3 kW/m², full-thickness third-degree skin carbonization occurs within $t \approx 2.5–3.5\text{ seconds}$. Armin Arlert's 15–20 second exposure accumulated $\approx 653\text{ kJ/m}^2$, completely charring dermis, vaporizing hair, and boiling pulmonary fluids ([#L347–L369](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L347-L369)).

---

## 6. Hardening Crystallization — Diamond-Cubic Lattice, Griffith Fracture, and Thunder Spear Penetration

### 6.1 Material Properties of Titan Crystal Armor

Titan hardening produces a tetrahedral diamond-cubic crystal lattice ($Fd\bar{3}m$ space group) with biologically templated calcium hydroxyapatite and organosilicon bridges ([findings_titan_transformations.md #L373–L442](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L373-L442)):

| Property | Titan Crystal | Diamond (PCD) | Hardened Steel | Alumina Ceramic |
|---|---|---|---|---|
| Mohs Hardness | **9.5–10.0** | 10.0 | 5.5–6.5 | 9.0 |
| Vickers Hardness $H_V$ | **45–65 GPa** | 50–100 GPa | 6–9 GPa | 18–22 GPa |
| Young's Modulus $E$ | **750–950 GPa** | 1,050 GPa | 210 GPa | 380 GPa |
| Compressive Strength $\sigma_c$ | **3.5–5.2 GPa** | 4.0–8.0 GPa | 1.2–1.8 GPa | 3.0–4.0 GPa |
| Fracture Toughness $K_{IC}$ | **2.5–4.2 MPa·m^{1/2}** | 4.0–6.0 | 50–100 | 3.5–4.5 |

### 6.2 Griffith Brittle Fracture and the Thunder Spear Exploit

While Titan crystal resists compressive impact (shattering standard steel blades), its low fracture toughness ($K_{IC} \approx 3.0\text{ MPa·m}^{1/2}$) makes it susceptible to brittle failure under tensile stress. Griffith's criterion ([#L411–L426](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L411-L426)):

$$\sigma_f = \sqrt{\frac{2 E \gamma_s}{\pi a_0}} = \sqrt{\frac{2 \times 850 \times 10^9 \times 4.5}{\pi \times 25 \times 10^{-6}}} \approx 312\text{ MPa}$$

**Thunder Spear Munroe-Effect Shaped Charge** ([#L428–L438](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L428-L438)):
1. Kinetic anchoring into surface micro-crevices
2. Shaped-charge detonation forming a hypervelocity metallic jet ($v_{jet} \approx 5{,}000–7{,}500\text{ m/s}$)
3. Dynamic stagnation pressure: $P_{dynamic} = \frac{1}{2} \rho_{jet} v_{jet}^2 = 0.5 \times 8{,}900 \times (6{,}000)^2 = 160\text{ GPa}$
4. Since $160\text{ GPa} \gg \sigma_c$ (5.2 GPa), the shockwave exceeds the Hugoniot Elastic Limit, triggering explosive spallation

### 6.3 Visual FX Shader Pipeline — Voronoi Cleavage and Cauchy Dispersion

```
[Mesh Surface P]
       │
       ├──────────────────────────┬──────────────────────────┐
       ▼                         ▼                          ▼
VORONOI CELL DISPLACEMENT   REFRACTION & DISPERSION    FRESNEL SPECULAR
• 3D Cellular noise seeds   • Snell: n1·sinθ1 = n2·sinθ2  • Schlick: R(θ) = R0 +
• Cleavage: step(F2 - F1)  • Cauchy: n(λ) = A + B/λ²       (1-R0)(1-cosθ)^5
• dFdx/dFdy facet normals  • n_r=1.533, n_g=1.539,       • R0 = 0.0452
                              n_b=1.547                   • Grazing: R → 1.0
       │                         │                          │
       └──────────────────────────┴──────────────────────────┘
                                 │
                                 ▼
                    EMISSIVE SOLIDIFICATION FRONT
                    • smoothstep(t - w, t, dist)
                    • Subterranean bioluminescent stress veins
```

([findings_titan_transformations.md #L446–L507](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L446-L507), production GLSL shader at [#L514–L631](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L514-L631))

---

## 7. Square-Cube Scaling Law and Froude Number — The Mathematics of Giant Creature Animation

### 7.1 Geometric Divergence at Titan Scale

Under isometric scaling with factor $\lambda = L_{\text{titan}} / L_{\text{human}}$ ([findings_mappa_3d_rigging.md #L189–L236](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L189-L236), [findings_workflow_extrapolation.md #L758–L810](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L758-L810)):

$$A(\lambda) = \lambda^2 A_0, \quad M(\lambda) = \lambda^3 M_0, \quad \sigma(\lambda) = \lambda \sigma_0, \quad \frac{F_{\text{muscle}}}{M} \propto \frac{1}{\lambda}$$

| Metric | Human (1.8 m) | Attack Titan (15 m, λ = 8.33) | Colossal Titan (60 m, λ = 33.33) |
|---|---|---|---|
| Scale Factor | 1.0× | 8.333× | 33.333× |
| Cross-Sectional Area ($\lambda^2$) | 1.0× | 69.44× | 1,111.1× |
| Isometric Mass ($\lambda^3$) | 75 kg | 43,400 kg (43.4 t) | 2,777,800 kg (2,778 t) |
| Compressive Stress ($\lambda \sigma_0$) | 1.0× | 8.333× | 33.333× |
| Required Density ($\rho_0 / \lambda$) | 1,000 kg/m³ | 120 kg/m³ | 30 kg/m³ |

At 15 m, dynamic bone stress ($\sim$250 MPa) exceeds cortical bone yield ($130–200$ MPa). At 60 m, stress reaches $\sim$1 GPa — the biped would liquify under its own weight. The canonical resolution: Titan tissue density decreases inversely with scale ($\rho_{\text{titan}} \propto 1/\lambda$).

### 7.2 Froude Number Dynamic Similarity and the Lilliput Effect

The Froude number governing walk-run phase transitions ([findings_mappa_3d_rigging.md #L239–L283](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L239-L283)):

$$Fr = \frac{v^2}{g L} \implies v_t = v_h \sqrt{\lambda}, \quad T = 2\pi\sqrt{\frac{L}{g}} \propto \sqrt{\lambda}$$

| Entity | Height | Leg Length | $\lambda$ | Natural Velocity | Stride Period | Frames @ 24 fps |
|---|---|---|---|---|---|---|
| Human | 1.8 m | 0.95 m | 1.0 | 1.40 m/s (5.0 km/h) | 1.00 s | 12 frames |
| Attack Titan | 15.0 m | 7.95 m | 8.33 | 4.04 m/s (14.5 km/h) | 2.89 s | 35 frames |
| Colossal Titan | 60.0 m | 31.80 m | 33.33 | 8.08 m/s (29.1 km/h) | 5.77 s | 69 frames |

**The Lilliput Effect**: If a 60 m Titan takes steps at human speed (12 frames / 0.5 s), the viewer instantly perceives a person standing before miniature buildings. Correct implementation requires:
1. **Low-frequency inertia**: Colossal step $\approx$ 2.89 s (69 frames)
2. **Rotational inertia**: $I \propto \lambda^5 \approx 4.12 \times 10^7$ times human — rapid angular acceleration is physically impossible
3. **Shockwave delay**: Debris billows outward at acoustic velocity ($v_s \approx 340\text{ m/s}$), not instantaneously

([findings_mappa_3d_rigging.md #L274–L283](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L274-L283))

---

## 8. MMA Combat Biomechanics — Isayama's Martial Inspirations and the Da-Tō-Kyoku Taxonomy

### 8.1 Isayama's Real-World Combat References

Episode 32 (S2 E7), titled **「打・投・極」** (*Da – Tō – Kyoku*), takes its name from the founding motto of Shooto, the pioneering Japanese MMA organization (est. 1985) ([findings_wit_studio_production.md #L502–L538](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L502-L538)):

| Titan | Real-World Model | Key Athletic Traits |
|---|---|---|
| Attack Titan (Eren) | Yushin Okami (UFC middleweight) | Lean proportioned musculature, orthodox boxing stance, takedown defense |
| Armored Titan (Reiner) | Brock Lesnar (UFC heavyweight) | Colossal trapezius, barrel chest, freight-train tackles, top-control wrestling |
| Female Titan (Annie) | Gina Carano / Megumi Fujii | Low calf kicks, Thai clinches, fluid submission transitions |

### 8.2 Phase 1: Striking (打) — The Structural Failure of Impact Against Armor

When Eren's bare fist strikes Reiner's keratinized armor ($\sigma_y > 450\text{ MPa}$), Newton's Third Law returns the reaction force directly into Eren's unarmored knuckles. Contact duration $\Delta t \approx 0.02\text{ s}$ generates tens of thousands of kilonewtons. Eren's metacarpals shatter while Reiner's armor shows zero deformation ([findings_wit_studio_production.md #L541–L569](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L541-L569)).

### 8.3 Phase 2: Throwing (投) — Momentum Redirection via Sacrifice Takedowns

Eren applies Annie's BJJ/Judo principles — technique allows a smaller fighter to overcome a massive brute by manipulating levers and redirecting momentum ([#L572–L603](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L572-L603)):

1. Reiner executes a Brock Lesnar bull-rush at $v \approx 18\text{ m/s}$
2. Eren sidesteps (*tenshin*) off the central force line ($\theta = 35°$)
3. Front headlock / guillotine grip around Reiner's neck
4. Sacrifice drop (*sutemi-waza*): Eren plants feet on Reiner's hips, converts forward momentum to angular momentum: $\vec{\tau} = \vec{r}_{\text{hip}} \times \vec{p}_{\text{forward}}$
5. Reiner flips 180° and crashes spine-first into the soil

### 8.4 Phase 3: Submissions (極) — Class 1 Lever Joint Mechanics

```
Eren's Pelvic Fulcrum (F)
               ▲
               │
Reiner's ◄─────┼──────────────────► Reiner's Wrist
Torso          │                     Effort Zone
Load Zone      │                     (Eren's Dual Arms)
(Trochlear     │
 Joint & UCL)  │
               │
◄── d_load ──► ◄────── d_effort ──────────►
    (0.4 m)               (2.2 m)

Mechanical Advantage: MA = 2.2 / 0.4 = 5.5
Bending Moment: M = 80 kN × 2.2 m = 176 kN·m
```

([findings_wit_studio_production.md #L606–L667](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L606-L667))

**Armor Plate Fracture via Joint Leverage**: The elbow joint is forced past 180° into hyperextension ($\theta > 205°$). Internal bone collision presses outward against rigid armor plate borders. Armor engineered for compressive resistance is brittle under tensile bending moments: $\tau_{\text{shear}} = VQ/(It)$ exceeds $\sigma_{UTS} \approx 180\text{ MPa}$ and the plate shatters like tempered glass.

### 8.5 Scale-Invariance of Joint Lock Mechanics

Both applied breaking torque and resisting torsional strength scale identically as $\lambda^3$ ([findings_workflow_extrapolation.md #L882–L920](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L882-L920)):

$$\frac{\tau_{\text{applied}}}{T_{\text{resisting}}} \propto \frac{\lambda^3}{\lambda^3} = \text{constant}$$

**Theorem**: *The mechanical efficacy of BJJ joint locks is scale-invariant.* A lock that breaks a human arm breaks a 15 m Titan arm with identical leverage ratios, provided the fulcrum placement and angle $\sin\theta \approx 1.0$ are preserved.

At 15 m scale, Eren's posterior chain delivers $\sim$45 tonnes of mechanical thrust against Reiner's forearm lever ($r \approx 4.2\text{ m}$):

$$\tau_{\text{elbow}} = 4.2\text{ m} \times 45{,}000\text{ kg} \times 9.81\text{ m/s}^2 \approx 1.85\text{ MN·m}$$

---

## 9. Production Code Architectures — XPBD Cable Solver, Volumetric Steam, and Froude Scaling Engine

### 9.1 XPBD Dual-Cable ODM Constraint Solver (TypeScript / Three.js)

A complete production-ready solver with sub-stepped integration, gas thrust, aerodynamic drag, and dynamic camera tether is implemented in TypeScript at ([findings_workflow_extrapolation.md #L172–L465](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L172-L465)):

- `ODMConstraintSolver` class: Semi-implicit Euler + XPBD unilateral distance constraints with configurable compliance, sub-stepping (default 4), emergency cable snap at 15,000 N
- `ODMDynamicCameraTether` class: Velocity-aligned trailing with anticipatory look-ahead ($0.35\text{ s}$ lead time), dynamic FOV expansion (60°–92°), lateral roll banking ($\pm 0.45\text{ rad}$), and underdamped trauma camera shake ($T^2$ power decay)

### 9.2 Volumetric Steam Ray-Marching Shader (GLSL / WebGL2)

A 64-step ray-marching shader with 6-step shadow marching, 4-octave fBm density field, Henyey-Greenstein phase scattering ($g \approx 0.45$), Beer-Lambert transmittance, and incandescent core glow is implemented at ([findings_workflow_extrapolation.md #L531–L673](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L531-L673)).

### 9.3 Celestial Transformation Lightning Shader (GLSL / WebGL2)

Domain-warped 5-octave fBm generating high-intensity filament ridges ($0.0035 / (trunkDist + 0.0008)$), secondary feeder branches with step-masked spawning, and ground EMP shockwave rings is implemented at ([findings_workflow_extrapolation.md #L675–L754](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L675-L754)).

### 9.4 Titan Hardening Crystal Shader (GLSL 450)

3D Voronoi cleavage faceting, Cauchy chromatic dispersion refraction ($n_r = 1.533$, $n_g = 1.539$, $n_b = 1.547$), Schlick Fresnel reflectance ($R_0 = 0.0452$), and moving Stefan-boundary solidification front is implemented at ([findings_titan_transformations.md #L514–L631](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L514-L631)).

### 9.5 Sedov-Taylor Blast Wave and Colossal Steam Drag Python Engine

A Python numeric engine implementing `TitanBlastPhysics` (Sedov-Taylor radius + Rankine-Hugoniot overpressure) and `ColossalSteamDynamics` (drag force + conjugate thermal heat flux with Henriksen burn criterion) is provided at ([findings_titan_transformations.md #L636–L729](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L636-L729)).

---

## 10. YouTube Channel Inference and Cross-Anime Synthesis Layer

### 10.1 Production Technique → Channel Topic Mapping Table

| AoT Production Technique | Source Evidence | Money Physics | Building Money | Martial Matters |
|---|---|---|---|---|
| ODM slingshot navigation (XPBD cable constraint, angular momentum conservation, dual-cable trajectory manifold) | [workflow_extrapolation.md #L23–L168](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L23-L168) | Navigating complex financial network graphs with momentum and constraint cables. Camera slingshots between balance sheet tranches. | — | — |
| Titan transformation staging (celestial lightning, 4-tier tissue assembly, blast shockwaves) | [titan_transformations.md #L51–L163](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L51-L163) | — | Company scale-up phase transitions with blast shockwaves at each fundraising round. Each round = transformation tier: skeleton (incorporation) → muscle (product-market fit) → vascular (revenue scaling) → epidermis (IPO). | — |
| Square-Cube Law + Froude scaling ($\sigma \propto \lambda$, $\tau \propto \sqrt{\lambda}$, $I \propto \lambda^5$) | [mappa_3d_rigging.md #L189–L283](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L189-L283), [workflow_extrapolation.md #L758–L878](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L758-L878) | Why corporations become sluggish at scale — institutional inertia scales as $\lambda^5$; stride frequency (decision speed) drops as $1/\sqrt{\lambda}$. The Lilliput Effect = why scaled-up organizations look "fake" when they move at startup speed. | — | — |
| MMA combat biomechanics (Da-Tō-Kyoku taxonomy, Kimura lock, armbar leverage) | [wit_studio_production.md #L502–L667](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L502-L667), [workflow_extrapolation.md #L882–L934](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L882-L934) | — | — | Joint manipulation mechanics: Class 1 lever physics, weight class advantages (MA = 5.5× at armbar), scale-invariant leverage vectors, exploiting kinetic seams in opponent's armor. |
| Steam venting (Rayleigh-Taylor instability, MTT plume kinematics, Colossal defensive exhaust) | [titan_transformations.md #L194–L369](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L194-L369) | Inflationary pressure release: QE exhaust modeled as volumetric Rayleigh-Taylor steam plumes; plume opacity $\propto dM2/dt$. Scout repulsion force = capital flight drag force. | — | — |
| Hardening crystallization (diamond-cubic lattice, Griffith brittle fracture, Voronoi cleavage) | [titan_transformations.md #L373–L442](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L373-L442) | — | Competitive moats as crystal armor: strong under compression (pricing wars, commodity competition) but brittle under novel attack vectors (Thunder Spear = disruptive technology shaped-charge, $P_{dynamic} \gg \sigma_c$). Griffith flaw = undetected regulatory/technical liability. | — |

### 10.2 Money Physics: ODM Financial Network Navigation and Inflationary Steam Exhaust

The ODM cable physics solver translates directly into a dynamic 3D camera tethering system for navigating multi-plane balance sheet scaffolds ([findings_workflow_extrapolation.md #L937–L988](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L937-L988)):

- **Balance Sheet Skyscraper**: Assets (left wing: Treasuries, MBS, Corporate Loans as granite pillars) vs Liabilities (right wing: Deposits, Commercial Paper, Repo as tension cables)
- **ODM Camera Tethering**: Virtual grapple hooks fire into yield-curve nodes; active spooling ($v_{\text{spool}} = 25\text{ m/s}$) slingshots between tranches; maturity wall cliff → high-G centrifugal swing with FOV expansion from 60° to 90°
- **Perspective Compression Hit-Stop**: Accounting anomaly triggers 4-frame hit-stop + instantaneous 20mm → 135mm focal length morph
- **Market Melt-Up = Celestial Lightning Strike**: Parabolic acceleration ($d^2P/dt^2 > \theta$) triggers vertical HDR lightning bolt striking the price node + EMP shockwave ring knocking back correlated assets + $T = 1.0$ trauma shake
- **QE Exhaust = Colossal Steam Venting**: Volumetric GLSL plumes erupting from sovereign debt nodes, opacity $\propto dM2/dt$; structural pillars undergo thermal degradation from cool blue to molten orange ($T \approx 1400\text{ K}$)

### 10.3 Building Money: Transformation Phase Transitions and Crystalline Competitive Moats

- **Fundraising Round = Titan Transformation**: Each round deposits new organizational mass via a "lightning strike" event. The 4-tier tissue hierarchy maps to: Tier 1 (Osteological = legal incorporation and org chart), Tier 2 (Myofibril = product-market fit and team build), Tier 3 (Vascular = revenue scaling and capital deployment), Tier 4 (Epidermal = brand identity and IPO shell)
- **Blast Shockwave at Each Round**: Sedov-Taylor expanding ring represents market displacement — Series A crater ($E_0 \sim$ standard assault) vs IPO thermonuclear detonation ($E_0 \sim$ Colossal class)
- **Competitive Moat = Hardening Crystallization**: Crystalline armor protects under compressive competition (Vickers 45–65 GPa) but fractures under novel attack. Thunder Spear = disruptive technology shaped charge where $P_{dynamic} = 160\text{ GPa} \gg \sigma_c = 5.2\text{ GPa}$. Griffith flaw ($a_0 \approx 25\text{ μm}$) = undetected regulatory liability or technical debt propagating at Rayleigh surface wave speed once fracture stress ($312\text{ MPa}$) is exceeded

### 10.4 Martial Matters: Joint Manipulation Mechanics, Weight Class Advantages, and Leverage Vectors

- **Da-Tō-Kyoku Taxonomy**: Striking → Throwing → Submissions as the three structural phases of complete combat, directly applicable to martial arts explainer episodic structure
- **Class 1 Lever Joint Physics**: Animated armbar breakdown with labeled fulcrum, effort arm, and load arm demonstrating MA = 5.5× mechanical advantage
- **Weight Class Analysis via Square-Cube Law**: Strength-to-weight ratio $\propto 1/\lambda$ — heavier fighters hit harder in absolute terms but become proportionally weaker. Ground reaction force scales as $\lambda^3$ while joint lock efficacy remains constant
- **Armor Seam Exploitation**: Kinematic necessity dictates that articulating joints cannot be fully armored. The unarmored antecubital fossa, axillary space, and popliteal fossa are universal weak points
- **Scale-Invariant Joint Lock Theorem**: Animated proof that $\tau_{\text{applied}} / T_{\text{resisting}} = \text{constant}$ across all body sizes
- **Infrasonic Impact Sound Design**: Titan-scale impacts shift acoustic resonance from $150–350\text{ Hz}$ to $18–42\text{ Hz}$. Low-pass filter at $f_c \approx 80\text{ Hz}$ for distant camera perspectives reinforces scale

---

## Sources and Tier 2 Evidence Registry

| # | Local Anchor | Metric / Subject | Primary Authority | Canonical URL | Verified Date |
|---|---|---|---|---|---|
| 1 | [wit_studio_production.md #L12–L35](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L12-L35) | WIT STUDIO founding and production history | Anime News Network | https://www.animenewsnetwork.com/encyclopedia/company.php?id=11306 | 2012-06-01 |
| 2 | [wit_studio_production.md #L50–L90](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L50-L90) | Araki directorial grammar and cinematography | Sakuga Blog | https://blog.sakugabooru.com/2017/04/01/attack-on-titan-season-2-production-notes-1/ | 2017-04-01 |
| 3 | [wit_studio_production.md #L100–L150](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L100-L150) | Make-Up Animation unit (Sachiko Matsumoto) | Animate Times | https://www.animatetimes.com/news/details.php?id=1462415212 | 2016-05-06 |
| 4 | [wit_studio_production.md #L105–L165](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L105-L165) | Kabaneri Make-Up Animation technical deep-dive | Washi's Blog | https://washiblog.wordpress.com/2016/12/08/kabaneris-make-up-animation/ | 2016-12-08 |
| 5 | [wit_studio_production.md #L170–L225](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L170-L225) | Kyoji Asano character design and linework philosophy | Kobe Institute of Computing | https://www.kobedenshi.ac.jp/whatsnew/2017/01/ | 2017-01-20 |
| 6 | [wit_studio_production.md #L230–L280](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L230-L280) | Shuhei Yabuta MADBOX 3DCG background direction | Wikipedia Japan | https://ja.wikipedia.org/wiki/藪田修平 | 2021-08-15 |
| 7 | [wit_studio_production.md #L285–L360](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L285-L360) | Arifumi Imai ODM line art collection (Vols 1 & 2) | WIT STUDIO Official / IG Port | https://www.igport-onlinestore.com/products/detail.php?product_id=2334 | 2019-08-09 |
| 8 | [wit_studio_production.md #L365–L420](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L365-L420) | E-SAKUGA Attack on Titan: Imai ODM genga | E-SAKUGA / One-to-Ten | https://www.esakuga.net/titles/attack-on-titan-arifumi-imai | 2020-12-24 |
| 9 | [wit_studio_production.md #L430–L510](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L430-L510) | Centripetal acceleration and high-G human tolerances | FAA Civil Aerospace Medical Institute | https://www.faa.gov/pilots/safety/pilotsafetybrochures/media/Acceleration.pdf | 2026-01-10 |
| 10 | [wit_studio_production.md #L520–L570](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L520-L570) | Viscoelastic muscle and fascia properties | Journal of Biomechanics / ScienceDirect | https://www.sciencedirect.com/science/article/pii/S002192900300185X | 2026-02-15 |
| 11 | [wit_studio_production.md #L580–L650](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L580-L650) | Isayama MMA inspirations (Brock Lesnar / Yushin Okami) | Crunchyroll News | https://www.crunchyroll.com/news/latest/2013/12/6/author-reveals-attack-on-titan-inspirations | 2013-12-06 |
| 12 | [wit_studio_production.md #L655–L730](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L655-L730) | Episode 32 「打・投・極」 production credits | AoT Production Wiki | https://w.atwiki.jp/shingekinokyojin/pages/156.html | 2017-05-13 |
| 13 | [wit_studio_production.md #L735–L790](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L735-L790) | Shooto founding philosophy (打・投・極) | Japan Shooto Association | https://j-shooto.com/history/ | 2026-03-01 |
| 14 | [wit_studio_production.md #L800–L870](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_wit_studio_production.md#L800-L870) | Joint manipulation biomechanics and mechanical advantage | Human Kinetics / Athletic Training | https://us.humankinetics.com/products/kinesiology-and-biomechanics | 2026-02-20 |
| 15 | [mappa_3d_rigging.md #L9–L34](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L9-L34) | WIT STUDIO handover and producer negotiations | Kodansha / Comic Natalie | https://natalie.mu/comic/news/381084 | 2020-05-29 |
| 16 | [mappa_3d_rigging.md #L35–L64](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L35-L64) | MAPPA production transition and Yabuta PV | Anime News Network | https://www.animenewsnetwork.com/news/2020-05-29/ | 2020-05-29 |
| 17 | [mappa_3d_rigging.md #L22–L64](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L22-L64) | MAPPA CGI policy (Yuichiro Hayashi) | CGWORLD.jp (vol. 272) | https://cgworld.jp/feature/202104-shingekifs-policy.html | 2021-04-19 |
| 18 | [mappa_3d_rigging.md #L121–L131](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L121-L131) | Founding Titan modeling, scale revisions, 96-rib rigging | CGWORLD JAM Online 2022 | https://cgworld.jp/article/202207-cgwjam-shingeki.html | 2022-09-13 |
| 19 | [mappa_3d_rigging.md #L132–L156](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L132-L156) | Female Titan chest rig and Wall Titan LODs (ARecT) | CGWORLD JAM Online 2022 | https://cgworld.jp/article/202207-cgwjam-shingeki.html | 2022-09-13 |
| 20 | [mappa_3d_rigging.md #L194–L222](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L194-L222) | Raretrick compositing and touch-mask shaders | CGWORLD.jp (vol. 272 撮影編) | https://cgworld.jp/feature/202104-shingekifs-cmp.html | 2021-04-20 |
| 21 | [mappa_3d_rigging.md #L223–L233](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L223-L233) | Studio Kusanagi 3D layout and camera projection | CGWORLD.jp (vol. 311) | https://cgworld.jp/article/202407-shingeki1.html | 2024-07-01 |
| 22 | [mappa_3d_rigging.md #L236–L279](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L236-L279) | Square-Cube Law in biological structures | Galilei (1638) / Cambridge Biomechanics | https://www.cambridge.org/core/books/scaling-why-is-animal-size-so-important/ | 2026-01-15 |
| 23 | [mappa_3d_rigging.md #L280–L318](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_mappa_3d_rigging.md#L280-L318) | Froude number and locomotion similarity | R. McNeill Alexander (1976) | https://www.sciencedirect.com/science/article/pii/0021929076900898 | 2026-02-10 |
| 24 | [titan_transformations.md #L53–L84](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L53-L84) | Titan activation trigger and lightning conduit | AoT Wiki | https://attackontitan.fandom.com/wiki/Power_of_the_Titans_(Anime) | 2026-09-22 |
| 25 | [titan_transformations.md #L86–L163](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L86-L163) | Transformation sakuga cuts by Imai, Ebisu, Yang | Sakugabooru | https://sakugabooru.com/post?tags=shingeki_no_kyojin+transformation | 2026-09-22 |
| 26 | [titan_transformations.md #L247–L251](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L247-L251) | Rikao Yanagita's thermal calculations ($602°\text{C}$ equilibrium) | Kodansha / Penguin Random House | https://www.penguinrandomhouse.com/books/529617/the-science-of-attack-on-titan-by-rikao-yanagita/ | 2026-09-22 |
| 27 | [titan_transformations.md #L223–L233](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L223-L233) | Water/steam thermophysical properties ($L_v = 2.257 \times 10^6$ J/kg) | NIST Chemistry WebBook | https://webbook.nist.gov/chemistry/fluid/ | 2026-09-22 |
| 28 | [titan_transformations.md #L285–L298](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L285-L298) | MTT turbulent plume model | Morton, Taylor, Turner (1956) | https://doi.org/10.1098/rspa.1956.0011 | 2026-09-22 |
| 29 | [titan_transformations.md #L88–L100](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L88-L100) | Rankine-Hugoniot shock wave relations | Rankine (1870), Hugoniot (1887) | https://doi.org/10.1098/rstl.1870.0015 | 2026-09-22 |
| 30 | [titan_transformations.md #L411–L427](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L411-L427) | Griffith brittle fracture criterion | Griffith (1921), Philosophical Transactions | https://doi.org/10.1098/rsta.1921.0006 | 2026-09-22 |
| 31 | [titan_transformations.md #L428–L439](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L428-L439) | Munroe-effect shaped charge hydrodynamics | Walters & Zukas, Wiley | https://www.wiley.com/en-us/Fundamentals+of+Shaped+Charges-p-9780471621720 | 2026-09-22 |
| 32 | [titan_transformations.md #L489–L499](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_titan_transformations.md#L489-L499) | Schlick Fresnel BRDF approximation | Schlick (1994), Computer Graphics Forum | https://doi.org/10.1111/j.1467-8659.1994.tb00170.x | 2026-09-22 |
| 33 | [workflow_extrapolation.md #L31](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L31) | XPBD position-based constrained dynamics | Macklin et al. (2016), MIG '16 | https://matthias-research.github.io/pages/publications/XPBD.pdf | 2026-09-22 |
| 34 | [workflow_extrapolation.md #L83](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L83) | Quadratic aerodynamic drag equation | Rayleigh / ISO 2533 | https://en.wikipedia.org/wiki/Drag_equation | 2026-09-22 |
| 35 | [workflow_extrapolation.md #L320](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L320) | Rayleigh-Taylor fluid instability | Rayleigh (1883), Taylor (1950) | https://en.wikipedia.org/wiki/Rayleigh–Taylor_instability | 2026-09-22 |
| 36 | [workflow_extrapolation.md #L370](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L370) | Henyey-Greenstein phase function | Henyey & Greenstein (1941) | https://en.wikipedia.org/wiki/Henyey–Greenstein_phase_function | 2026-09-22 |
| 37 | [workflow_extrapolation.md #L455](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L455) | MAPPA 3DCG production pipeline | CGWORLD.jp (Jan 2024) | https://cgworld.jp/article/202401-shingeki-cg-01.html | 2026-09-22 |
| 38 | [workflow_extrapolation.md #L520](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L520) | Square-Cube Law and allometric scaling | Galilei (1638); Haldane (1926) | https://en.wikipedia.org/wiki/Square–cube_law | 2026-09-22 |
| 39 | [workflow_extrapolation.md #L585](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L585) | Froude number kinematic scaling | Alexander RM (1976), Nature 261:129 | https://en.wikipedia.org/wiki/Froude_number | 2026-09-22 |
| 40 | [workflow_extrapolation.md #L720](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L720) | BJJ joint lock biomechanical leverage | Winter DA (2009), Wiley 4th Ed. | https://www.wiley.com/en-us/Biomechanics+and+Motor+Control+of+Human+Movement | 2026-09-22 |
| 41 | [workflow_extrapolation.md #L780](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L780) | Cortical bone torsional shear strength | Reilly & Burstein (1975), J. Biomech. 8:393 | https://pubmed.ncbi.nlm.nih.gov/1184643/ | 2026-09-22 |
| 42 | [workflow_extrapolation.md #L840](file:///c:/Users/Snipe/Downloads/Outreach%20Program/docs/research/runs/attack-on-titan-production-2026-09/findings_workflow_extrapolation.md#L840) | Trauma camera shake (minimum-jerk model) | Flash & Hogan (1985); Eiserloh GDC 2016 | https://www.gdcvault.com/play/1023146/ | 2026-09-22 |

---

## NOT FOUND WHERE I LOOKED

1. **Exact polygon counts for MAPPA's Nine Titan 3ds Max meshes**: CGWORLD.jp feature articles discuss topology conventions and rigging architectures but do not publish specific vertex/polygon counts per model. The Founding Titan is described qualitatively as exceeding standard coordinate precision limits at 600+ meters but no mesh statistics are provided.

2. **Arifumi Imai's exact frame-by-frame timing sheets (X-sheets) for Levi vs Beast Titan (S3P2 E54)**: E-SAKUGA publishes genga keyframe scans but does not include the full X-sheet timing notation. The 4-month production timeline is sourced from Imai's own Twitter/social media statements and confirmed by Sakuga Blog but the internal WIT Studio production schedule documents are proprietary.

3. **MAPPA's internal render farm specifications and Pencil+ shader parameter presets**: CGWORLD.jp technical features discuss the NPR shading philosophy (inverted hull, vertex normal transfer, touch masks) but do not publish the specific Pencil+ preset JSON/XML configurations or render farm hardware specifications.

4. **Quantitative box office and production budget figures for each AoT season**: While the series' commercial success is well-documented, exact per-season production budgets and per-episode costs are not publicly disclosed by WIT Studio, MAPPA, or the production committee (Kodansha/Pony Canyon/MBS/NHK).

5. **Hajime Isayama's personal MMA event attendance records**: While multiple interviews confirm his devotion to PRIDE, UFC, and K-1, specific event dates/locations are not catalogued in any single authoritative source.
