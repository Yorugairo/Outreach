# 2D & 2.5D Body Animation, Object Handling, and Background Grounding
**Deep Academic, Biomechanical, and Compositing Synthesis for Institutional Video Engines**

- **Author / Pass**: Gemini Deep-Research Pass (Multi-Agent Synthesis)
- **Scope**: Character Biomechanics, Grasp Dynamics, Scene Graph Re-Parenting, 2.5D Planar Homographies, Shadow Physics, and Multiplane Compositing
- **Target Channels**: *Money Physics*, *Building Money*, *Yorugairo Content Video Engine*
- **Date**: 2026-09-04
- **Status**: Authoritative Technical Research Monograph (Bundle Item 09)
- **Companion Artifacts**:
  - Academic Literature Monograph: [`07_academic_literature_drawing_and_2_5d_animation_engine.md`](07_academic_literature_drawing_and_2_5d_animation_engine.md)
  - Answers to Animation Craft Brief: [`08_answers_animation_craft_brief.md`](08_answers_animation_craft_brief.md)
  - Master Evidence Dossier: [`MASTER_RESEARCH_AND_EVIDENCE_DOSSIER.md`](MASTER_RESEARCH_AND_EVIDENCE_DOSSIER.md)
  - Master Research Index: [`MASTER_RESEARCH_INDEX.md`](MASTER_RESEARCH_INDEX.md)

---

## Table of Contents
1. [Executive Summary & The Three Pillars of Character Believability](#1-executive-summary--the-three-pillars-of-character-believability)
2. [Track 1: 2D/2.5D Body Animation & Biomechanics](#2-track-1-2d25d-body-animation--biomechanics)
   - 2.1 [Center of Mass (COM), Base of Support (BOS), and Hof's XCOM](#21-center-of-mass-com-base-of-support-bos-and-hofs-xcom)
   - 2.2 [Postural Equilibrium: Ankle vs. Hip Gesturing Strategies](#22-postural-equilibrium-ankle-vs-hip-gesturing-strategies)
   - 2.3 [Inverse Kinematics (IK) in 2D: FABRIK vs. Analytical 2-Bone Trigonometry](#23-inverse-kinematics-ik-in-2d-fabrik-vs-analytical-2-bone-trigonometry)
   - 2.4 [Kinematic Control Boundaries: When to Use FK vs. IK](#24-kinematic-control-boundaries-when-to-use-fk-vs-ik)
   - 2.5 [2.5D Cutout Rigging vs. Mesh Deformation: LBS Collapse vs. 2D DQS & BBW](#25-25d-cutout-rigging-vs-mesh-deformation-lbs-collapse-vs-2d-dqs--bbw)
   - 2.6 [Pseudo-3D Head Turns & Facial Cylindrical Projection](#26-pseudo-3d-head-turns--facial-cylindrical-projection)
   - 2.7 [Natural Idling: Respiration Rhythms, Postural Sway, and Contrapposto](#27-natural-idling-respiration-rhythms-postural-sway-and-contrapposto)
   - 2.8 [Secondary Motion: Driven Damped Oscillators & Continuum Drag](#28-secondary-motion-driven-damped-oscillators--continuum-drag)
3. [Track 2: Object Handling, Grasp Dynamics, and Hand-Prop Interaction](#3-track-2-object-handling-grasp-dynamics-and-hand-prop-interaction)
   - 3.1 [The Cutkosky & Feix (2016) 33-Grasp Taxonomies Mapped to Props](#31-the-cutkosky--feix-2016-33-grasp-taxonomies-mapped-to-props)
   - 3.2 [Reaching Kinematics: Flash & Hogan Minimum-Jerk Quintic Trajectories](#32-reaching-kinematics-flash--hogan-minimum-jerk-quintic-trajectories)
   - 3.3 [Visuomotor Channels & Jeannerod's Hand Aperture Preshaping](#33-visuomotor-channels--jeannerods-hand-aperture-preshaping)
   - 3.4 [Scene Graph Re-Parenting Math & Virtual Constraint Caching](#34-scene-graph-re-parenting-math--virtual-constraint-caching)
   - 3.5 [Visual Communication of Mass: APAs, Force Coupling, and Lift Recoil](#35-visual-communication-of-mass-apas-force-coupling-and-lift-recoil)
   - 3.6 [Placement Dynamics: Damped Harmonic Settling Profiles](#36-placement-dynamics-damped-harmonic-settling-profiles)
   - 3.7 [Two-Handed Manipulation: Closed Kinematic Chains (CKC)](#37-two-handed-manipulation-closed-kinematic-chains-ckc)
4. [Track 3: Animating Over a 2D Background (Grounding & Parallax)](#4-track-3-animating-over-a-2d-background-grounding--parallax)
   - 4.1 [Kinematic Zero-Slip & The Ground-Plane Homography Invariant](#41-kinematic-zero-slip--the-ground-plane-homography-invariant)
   - 4.2 [The Dual-Component Contact Shadow Model: AO Slit vs. Diffuse Cast](#42-the-dual-component-contact-shadow-model-ao-slit-vs-diffuse-cast)
   - 4.3 [Blinn's Planar Shadow Matrix & 2.5D Affine Shear Projections](#43-blinns-planar-shadow-matrix--25d-affine-shear-projections)
   - 4.4 [Multi-Plane Disparity Sampling: LDIs and MPIs in 2.5D](#44-multi-plane-disparity-sampling-ldis-and-mpis-in-25d)
   - 4.5 [Vanishing Point Alignment & The Norling Eye-Line Theorem](#45-vanishing-point-alignment--the-norling-eye-line-theorem)
   - 4.6 [Parallax Differentials & Resolving the Floor-Shear Paradox](#46-parallax-differentials--resolving-the-floor-shear-paradox)
   - 4.7 [Visual Harmonization: Koschmieder's Law, Light Wrap, and Substrate Bleed](#47-visual-harmonization-koschmieders-law-light-wrap-and-substrate-bleed)
5. [Production Code Blueprints](#5-production-code-blueprints)
   - Blueprint A: Flash-Hogan Minimum-Jerk Reach-to-Grasp Generator (TypeScript)
   - Blueprint B: Affine $3 	imes 3$ Matrix Re-Parenting & Attachment Solver (TypeScript)
   - Blueprint C: Two-Handed Closed Kinematic Chain Rig (TypeScript)
   - Blueprint D: Placement Settling Damped Spring Evaluator (TypeScript)
   - Blueprint E: Dual-Shadow SVG Filter & Washi Substrate Blend (SVG/XML)
   - Blueprint F: Ground-Locked Parallax Hook (Remotion / React)
   - Blueprint G: Analytical 2-Bone Trigonometric IK Solver (TypeScript)
6. [Master Citation & Authority Registry](#6-master-citation--authority-registry)
7. [Pipeline Triage & Doctrine Recommendations](#7-pipeline-triage--doctrine-recommendations)

---

## 1. Executive Summary & The Three Pillars of Character Believability

In an evidence-driven, institutional video engine (e.g., our faceless educational channels *Money Physics* and *Building Money*), characters and props must communicate **unshakable authority and physical weight**. Unlike stylized entertainment cartoons, where visual exaggeration and rubber-hose physics are rewarded, an explainer channel deconstructing US Treasury yields, margin calls, or banking mechanics collapses if the host character looks like a disconnected paper puppet hovering above the desk, or if props snap weightlessly into the hand.

Realism in 2D and 2.5D character motion is governed by **Three Coupled Physical Pillars**:

```
                              THE THREE COUPLED PILLARS
                                          │
       ┌──────────────────────────────────┼──────────────────────────────────┐
       ▼                                  ▼                                  ▼
┌──────────────────────────────┐┌──────────────────────────────┐┌──────────────────────────────┐
│     1. BIOMECHANICAL FLOW    ││      2. OBJECT INTERACTION   ││     3. OPTICAL GROUNDING     │
│ • COM / BOS Stability (Hof)  ││ • Feix 33-Grasp Taxonomy     ││ • Zero-Slip Homography (H_π) │
│ • 2-Bone Closed-Form IK      ││ • Flash-Hogan Min-Jerk Reach ││ • Dual-Component Shadows     │
│ • BBW / DQS Joint Integrity  ││ • Jeannerod Hand Preshaping  ││   (Tight AO + Diffuse Cast)  │
│ • Contrapposto S-Curves      ││ • Re-Parenting Matrix Invert ││ • Eye-Line Horizon Lock      │
│ • Asymmetric Breathing Waves ││ • Pre-Lift APAs & Mass Recoil││ • Substrate Paper Bleed      │
└──────────────────────────────┘└──────────────────────────────┘└──────────────────────────────┘
```

1. **Biomechanical Flow (The Body)**: The human body is a multi-link pendulum governed by gravity and inertia. It never moves limbs in linear Cartesian paths, never rests in symmetrical poses, and never stands completely still. Center of Mass (COM) shifts precede every gesture; joints bend with strict area preservation (DQS) rather than linear collapse; and quiet standing exhibits involuntary breathing waves ($0.2	ext{--}0.3	ext{ Hz}$) and stochastic postural sway.
2. **Object Interaction (The Hands)**: Grasping an object is not an instantaneous boolean attachment. Hand trajectories minimize jerk (Flash & Hogan 1985 quintics); finger aperture preshapes to a maximum opening ($0.68	au$) before decelerating to contact; heavy props trigger Anticipatory Postural Adjustments (APAs) $120	ext{ms}$ *before* lift-off; and placing props onto surfaces excites damped harmonic oscillations.
3. **Optical Grounding (The Surface)**: A 2D sprite standing on a receding 2.5D background plane skates across the screen unless its baseline is kinematically locked to the ground-plane homography ($\mathbf{H}_{oldsymbol{\pi}}$). Contact requires two distinct shadow phenomena: a pitch-dark, sub-pixel **Ambient Occlusion (AO) slit** that roots the object, coupled with a geometrically sheared **diffuse directional cast shadow** that conveys light elevation and azimuth.

---

## 2. Track 1: 2D/2.5D Body Animation & Biomechanics

### 2.1 Center of Mass (COM), Base of Support (BOS), and Hof's XCOM

#### A. Mathematical Formulation
In human biomechanics, balance is defined by the spatial relationship between the **Center of Mass (COM)** and the **Base of Support (BOS)**:

1. **Center of Mass (COM)**:
   $$\mathbf{r}_{	ext{COM}} = rac{\sum_{i=1}^N m_i \mathbf{r}_i}{\sum_{i=1}^N m_i}$$
   where $m_i$ and $\mathbf{r}_i$ represent segment masses and segment COM coordinates (Winter 2009 anthropometric norms: trunk $pprox 49.7\%$, thighs $pprox 10\% 	imes 2$, shanks $pprox 4.65\% 	imes 2$, head/neck $pprox 8.1\%$). In quiet standing, $\mathbf{r}_{	ext{COM}}$ sits at approximately $55\%	ext{--}57\%$ of total body height, directly anterior to the second sacral vertebra ($S_2$).

2. **Base of Support (BOS)**:
   The convex polygon $\mathcal{H}$ bounded by the outer perimeter of the contact surfaces (the feet on the ground plane):
   $$	ext{BOS} = \operatorname{ConvexHull}\left(igcup_{k} \mathbf{p}_{	ext{contact}, k}ight)$$

3. **Static vs. Dynamic Stability & The Extrapolated Center of Mass (XCOM)**:
   - *Static Stability*: Requires the vertical projection of the COM to lie within the BOS:
     $$\mathbf{r}_{	ext{COM}, xy} \in \operatorname{int}(	ext{BOS})$$
   - *Dynamic Stability (Hof, Gazendam, & Sinke 2005)*: During active movement or gesturing, static COM is insufficient because momentum will carry the body outside the BOS even if the instantaneous COM is within bounds. **Hof et al. (2005)** formulated the **Extrapolated Center of Mass ($\mathbf{XCOM}$)**:
     $$\mathbf{XCOM} = \mathbf{r}_{	ext{COM}} + rac{\mathbf{v}_{	ext{COM}}}{\omega_0}, \quad \omega_0 = \sqrt{rac{g}{l}}$$
     where $\mathbf{v}_{	ext{COM}}$ is the horizontal velocity of the COM, $g = 9.81\,	ext{m/s}^2$, and $l$ is the effective pendulum length ($pprox 1.0	imes$ trochanter major height $pprox 0.85	imes H$).
   - *Margin of Stability (MOS)*:
     $$	ext{MOS} = \min_{\mathbf{e} \in \partial 	ext{BOS}} \|\mathbf{XCOM} - \mathbf{e}\|$$
     Equilibrium requires $	ext{MOS} > 0$. If $\mathbf{XCOM}$ crosses outside $\partial 	ext{BOS}$, the character must take a corrective step to widen the BOS or lose balance.

#### B. Weight Shifting Mechanics & Anticipatory Postural Adjustments (APAs)
When a character shifts weight from bilateral standing to a unilateral stance (or lifts a foot):
- **Anticipatory Postural Adjustments (APAs)** (**Bouisset & Do 2008**; **Winter 1995**): The nervous system pre-activates abductor muscles on the *stance* leg $pprox 100	ext{--}250\,	ext{ms}$ *before* the contralateral foot breaks ground.
- **Center of Pressure (COP) Pre-shift**: The COP briefly shifts *laterally toward the swing foot* to push the COM acceleratively toward the stance foot. Once the COM is securely positioned over the stance foot's BOS, the swing leg unweights and lifts. Animating foot lifting without this prior lateral COM shift produces an immediate "anti-gravity puppet" artifact.

---

### 2.2 Postural Equilibrium: Ankle vs. Hip Gesturing Strategies

When a standing character extends an arm ($m_{	ext{arm}} pprox 0.05 M$) horizontally by $\Delta x_{	ext{arm}}$ (e.g., pointing to an evidence chart):
$$\Delta x_{	ext{COM}} = rac{m_{	ext{arm}}}{M_{	ext{total}}} \Delta x_{	ext{arm}}$$

To maintain equilibrium without stepping, the Central Nervous System employs two distinct biomechanical strategies (**Horak & Nashner 1986**; **Nashner & McCollum 1985**):
1. **Ankle Strategy (Small/Slow Gestures)**: The feet exert a restorative ankle torque $	au_{	ext{ankle}} = \Delta x_{	ext{COM}} \cdot M g$. The entire body sways back as a nearly rigid inverted pendulum by angle $\Delta 	heta pprox -rac{\Delta x_{	ext{COM}}}{l}$.
2. **Hip Strategy (Rapid/Large Gestures)**: For rapid gestures or reaching across a table, the pelvis translates posteriorly in anti-phase to the arm reach:
   $$\Delta x_{	ext{pelvis}} pprox -rac{m_{	ext{arm}} \Delta x_{	ext{arm}}}{m_{	ext{pelvis}} + m_{	ext{legs}}}$$
   This creates a classic counter-balance fold at the hip joints: the upper torso leans forward while the buttocks translate backward, keeping total $\mathbf{XCOM}$ stationary over the mid-foot.

---

### 2.3 Inverse Kinematics (IK) in 2D: FABRIK vs. Analytical 2-Bone Trigonometry

```
+-------------------+----------------------------+-----------------------+---------------------------+
| Algorithm         | Mathematical Approach      | Time Complexity       | Joint Limit Handling      |
+-------------------+----------------------------+-----------------------+---------------------------+
| 2-Bone Analytical | Law of Cosines / Closed    | O(1) instantaneous    | Direct parametric clamp   |
| (Trigonometric)   | form geometric inversion   | Zero iterations       | on elbow/knee angles      |
| FABRIK            | Iterative forward/backward | O(N) per iteration;   | Projection onto angular   |
| (Aristidou 2011)  | point projection along ray | 1-5 iterations to eps | sectors during passes     |
| CCD               | Coordinate descent; rotates| O(N) per iteration;   | Local angle clamping      |
| (Wang & Chen 1991)| joint-by-joint to target   | 5-20 iterations; curl | immediately after step    |
+-------------------+----------------------------+-----------------------+---------------------------+
```

#### A. 2-Bone Analytical Trigonometric IK (Law of Cosines)
For human limbs (upper arm + forearm, thigh + shank), the 2-bone chain is mathematically determined. Let root joint be $\mathbf{p}_0$, mid joint $\mathbf{p}_1$, end-effector $\mathbf{p}_2$, with bone lengths $l_1 = \|\mathbf{p}_1 - \mathbf{p}_0\|$ and $l_2 = \|\mathbf{p}_2 - \mathbf{p}_1\|$, reaching for target $\mathbf{p}_t$.

1. **Target Distance & Reach Clamping**:
   $$d = \|\mathbf{p}_t - \mathbf{p}_0\|, \quad \hat{\mathbf{u}} = rac{\mathbf{p}_t - \mathbf{p}_0}{d}$$
   $$d_{	ext{clamped}} = \operatorname{clamp}(d, |l_1 - l_2| + \epsilon, \; l_1 + l_2 - \epsilon)$$
2. **Interior Joint Angles via Law of Cosines**:
   $$\cos eta = rac{l_1^2 + l_2^2 - d_{	ext{clamped}}^2}{2 l_1 l_2}, \quad eta = rccos(\operatorname{clamp}(\coseta, -1, 1))$$
   $$\cos lpha = rac{l_1^2 + d_{	ext{clamped}}^2 - l_2^2}{2 l_1 d_{	ext{clamped}}}, \quad lpha = rccos(\operatorname{clamp}(\coslpha, -1, 1))$$
3. **Mid-Joint Coordinate Determination with Pole/Hinge Sign**:
   Let base direction angle be $\phi = \operatorname{atan2}(y_t - y_0, x_t - x_0)$ and hinge parity $s \in \{+1, -1\}$ ($s=+1$ for elbow-up/knee-right, $s=-1$ for elbow-down/knee-left):
   $$	heta_{	ext{shoulder}} = \phi + s \cdot lpha$$
   $$\mathbf{p}_1 = \mathbf{p}_0 + l_1 egin{pmatrix} \cos(	heta_{	ext{shoulder}}) \ \sin(	heta_{	ext{shoulder}}) \end{pmatrix}$$
   $$\mathbf{p}_2 = \mathbf{p}_1 + l_2 egin{pmatrix} \cos(	heta_{	ext{shoulder}} - s(\pi - eta)) \ \sin(	heta_{	ext{shoulder}} - s(\pi - eta)) \end{pmatrix}$$
- **Evaluation**: Strictly $\mathcal{O}(1)$ time and space. Zero convergence delay, zero iteration jitter, zero singularity drift. The optimal choice for human arms and legs.

#### B. FABRIK (Forward And Backward Reaching Inverse Kinematics)
**Aristidou & Lasenby (2011)** (*Graphical Models* 73(5): 243–260; extended with constraints in **Aristidou, Chrysanthou, & Lasenby 2016**):
Instead of calculating joint angles or Jacobian matrices, FABRIK treats joints as positions $\mathbf{p}_0, \mathbf{p}_1, \dots, \mathbf{p}_n$ with fixed inter-joint link lengths $d_i = \|\mathbf{p}_{i+1} - \mathbf{p}_i\|$.
- **Forward Reaching**: Move end-effector $\mathbf{p}_n$ directly to target $\mathbf{p}_t$, then pull each joint along the line connecting it to its successor.
- **Backward Reaching**: Reset root $\mathbf{p}_0$ to fixed base origin, then push each joint along the line connecting it to its predecessor.
- **Joint Constraints**: Angular limits are enforced by projecting out-of-bounds joint vectors back onto the boundary of valid conic/angular sectors during the backward pass.
- **Performance**: Converges within $2	ext{--}3$ iterations with $\mathcal{O}(N)$ complexity. Ideal for multi-joint spines, flexible cables, and branching kinematic trees.

---

### 2.4 Kinematic Control Boundaries: When to Use FK vs. IK

1. **The Kinematic Arc Law (Disney Principle 7: Arcs)**:
   - When a limb rotates freely in space under muscle torque, the end-effector naturally traces **circular or elliptical arcs** in Cartesian space.
   - **FK Boundary**: Free gestures, arm swings, waving, tossing, and head nodding MUST be authored or solved in FK. Attempting to animate expressive gestures via linear interpolation of IK Cartesian targets flattens natural curvilinear sweeps into robotic straight lines and creates erratic elbow popping.
2. **The Environmental Contact Law**:
   - **IK Boundary**: The instant an extremity establishes rigid physical contact with a fixed or moving external object, it MUST lock to an IK solver:
     - **Pinned Feet**: Foot planting during stance phase to eliminate foot sliding / skating.
     - **Props & Desks**: Palms resting on a podium, fingers gripping a balance scale or holding an evidence document.
3. **FK/IK Seamless Handover (Blending Architecture)**:
   Transitioning between FK and IK requires a dynamic blending parameter $lpha(t) \in [0, 1]$ evaluated via a minimum-jerk profile:
   $$lpha(	au) = 10	au^3 - 15	au^4 + 6	au^5, \quad 	au = rac{t - t_0}{\Delta t_{	ext{trans}}}$$
   - **IK $	o$ FK Transition**: At the frame of release ($t_0$), the FK joint angles $oldsymbol{	heta}_{	ext{FK}}$ are matched instantly to the IK solver's current state: $oldsymbol{	heta}_{	ext{FK}}(t_0) = oldsymbol{	heta}_{	ext{IK}}(t_0)$. The solver switches to FK, continuing the momentum along a tangential arc.
   - **FK $	o$ IK Transition**: Over $\Delta t_{	ext{trans}} pprox 100	ext{--}150\,	ext{ms}$, joint transformations blend: $\mathbf{T}(t) = \operatorname{slerp}(\mathbf{T}_{	ext{FK}}, \mathbf{T}_{	ext{IK}}, lpha(t))$.

---

### 2.5 2.5D Cutout Rigging vs. Mesh Deformation: LBS Collapse vs. 2D DQS & BBW

#### A. Linear Blend Skinning (LBS) Volume Loss
In 2D LBS, a mesh vertex $\mathbf{v} \in \mathbb{R}^2$ is deformed by $M$ bones with scalar weights $w_j$:
$$\mathbf{v}' = \sum_{j=1}^M w_j \mathbf{T}_j egin{pmatrix} \mathbf{v} \ 1 \end{pmatrix}, \quad \mathbf{T}_j = egin{bmatrix} \mathbf{R}_j & \mathbf{t}_j \ \mathbf{0}^T & 1 \end{bmatrix}$$
- **The Collapse Defect**: The set of rotation matrices $\operatorname{SO}(2)$ is not a linear subspace. When a character's elbow or knee bends by angle $\Delta 	heta$, the linear combination of rotation matrices:
  $$\mathbf{R}_{	ext{blend}} = (1 - w) \mathbf{R}_0 + w \mathbf{R}_1$$
  has a determinant $\det(\mathbf{R}_{	ext{blend}}) < 1$. When $\Delta 	heta = 180^\circ$ and $w = 0.5$, $\mathbf{R}_{	ext{blend}} = \mathbf{0}$, causing total area collapse. In 2D character rigging, this causes the elbow or knee to pinch shut into an unappealing, paper-thin crease.

#### B. 2D Dual Quaternion Skinning (DQS)
**Kavan, Collins, Žára, & O'Sullivan (2007, 2008)** (*IEEE TVCG* 14(5): 1055–1071):
In 2D, rigid planar motions form the Special Euclidean group $\operatorname{SE}(2)$, isomorphic to unit dual complex numbers:
$$\hat{z} = z_0 + \epsilon z_\epsilon, \quad \epsilon^2 = 0$$
where $z_0 = \cos(	heta/2) + i \sin(	heta/2) \in \operatorname{SO}(2)$ represents rotation, and $z_\epsilon = rac{1}{2}(t_x + i t_y) z_0$ represents translation.
- **Dual Complex Blending (DLB)**:
  $$\hat{b} = rac{\sum_{j=1}^M w_j \hat{z}_j}{\|\sum_{j=1}^M w_j \hat{z}_j\|}$$
- **Zero Volume Collapse Guarantee**: Because normalized dual complex blending interpolates along shortest geodesic screw paths in $\operatorname{SE}(2)$, $\det(\mathbf{T}_{	ext{blend}}) \equiv 1$ across all rotation angles. The elbow retains full circumference and cross-sectional volume throughout a $120^\circ$ flex.

#### C. Bounded Biharmonic Weights (BBW)
**Jacobson, Baran, Popović, & Sorkine (2011)** (*ACM Trans. Graph. / SIGGRAPH 2011*, 30(4): 78:1–8):
BBW solves the biharmonic PDE $\Delta^2 w_j = 0$ over a Delaunay triangulation subject to hard box constraints:
$$\min_{w_j} rac{1}{2} \int_\Omega \|\Delta w_j(\mathbf{x})\|^2 \, d\mathbf{x} \quad 	ext{s.t.} \quad 0 \le w_j(\mathbf{x}) \le 1, \quad \sum_j w_j = 1, \quad w_j|_{H_k} = \delta_{jk}$$
- **The Breakthrough**: Eliminates the "skin webbing" of Euclidean inverse-distance weights (where vertices bleed across limbs) and prevents the negative-weight mesh tearing of unconstrained biharmonic splines. Elbows, knees, and coat folds deform with $C^1$ smoothness and strict locality.

---

### 2.6 Pseudo-3D Head Turns & Facial Cylindrical Projection

In a 2.5D explainer engine, rendering characters as full 3D polygon models looks sterile and violates hand-drawn brand doctrine (cream washi, sumi ink, editorial graphic identity). Authentic 2.5D relies on **projective pseudo-3D transforms**:

```
                 [ 2.5D CYLINDRICAL HEAD PROJECTION ]
                          
                           Direct Vision
                                 │
                                 ▼
                     . - ~ ~ ~ - .  (Yaw θ)
                 .-'       |       '-.
               /     [E1]  |  [E2]                   /       \    |    /                    |-----[Nose]--+---|---------|   <- Cylinder Surface (Radius R)
              \           / \           /
               \         /   \         /
                 '-.   [Ear]   '-.   .-'
                     ' - ~ ~ ~ - '
```

1. **Cylindrical Coordinate Projection**:
   Let a facial feature (eye, nose, mouth) have rest angular position $\phi_i \in [-\pi/2, \pi/2]$ along the cranial circumference. Under head yaw angle $	heta(t)$:
   $$x_{	ext{proj}, i} = x_{	ext{center}} + R_x \sin(\phi_i + 	heta(t))$$
   $$z_{	ext{depth}, i} = -R_z \cos(\phi_i + 	heta(t))$$
2. **Dynamic Lateral Foreshortening**:
   The instantaneous lateral scale (width compression factor) of the facial feature is given by the spatial derivative:
   $$s_{x, i} = rac{\partial x_{	ext{proj}, i}}{\partial \phi} = \cos(\phi_i + 	heta(t))$$
   As a feature turns away from the camera ($\phi_i + 	heta 	o \pm \pi/2$), its horizontal dimension automatically compresses to zero according to true cosine foreshortening, while vertical height remains constant ($s_{y, i} = 1$).
3. **Multi-Plane Parallax Layering**:
   Facial components are assigned discrete depth offsets: $z_{	ext{skull}} < z_{	ext{eyes}} < z_{	ext{nose\_base}} < z_{	ext{nose\_tip}}$. Under head rotation, the nose translates laterally faster than the eyes ($\Delta x \propto 1/z$), creating genuine 3D parallax without polygon meshes.
4. **Three-Quarters Gate & Sprite Swap**:
   When head yaw crosses $35^\circ	ext{--}45^\circ$, front-facing nose and mouth sprites reach their foreshortening limit. The system cross-fades or slot-swaps to a dedicated $45^\circ$ drawn plate over $2	ext{--}3$ frames ($83	ext{--}125\,	ext{ms}$) locked to peak angular velocity $\dot{	heta}_{\max}$ to mask the transition under motion blur.

---

### 2.7 Natural Idling: Respiration Rhythms, Postural Sway, and Contrapposto

#### A. Physiological Respiration Dynamics
- **Respiratory Rate**: $12	ext{--}18	ext{ breaths/minute}$, corresponding to a fundamental frequency:
  $$f_{	ext{breath}} \in [0.20, 0.30]\,	ext{Hz} \quad (	ext{Period } T_{	ext{breath}} pprox 3.3	ext{--}5.0\,	ext{s})$$
- **Asymmetric I:E Timing Ratio**: Normal physiological breathing is never a symmetric sine wave. It follows an **Inspiratory-to-Expiratory (I:E) ratio of $1:1.5$ to $1:2$**:
  - Active Inspiration ($T_{	ext{insp}} pprox 1.2	ext{--}1.5\,	ext{s}$): Elevation of clavicles by $\Delta y pprox 1.5	ext{--}3.0\,	ext{mm}$ and thoracic kyphosis flattening.
  - Passive Expiration ($T_{	ext{exp}} pprox 2.0	ext{--}2.5\,	ext{s}$): Elastic recoil of chest wall.
  - Post-Expiratory Pause ($T_{	ext{pause}} pprox 0.5	ext{--}1.0\,	ext{s}$): Static hold at rest.

#### B. Postural Sway (Inverted Pendulum Model)
Even when standing perfectly still, humans undergo continuous **postural sway** (**Winter 1995**; **Peterka 2002**; **Collins & De Luca 1993**):
- Sway follows a **two-regime fractional Brownian motion**: short-term open-loop drift ($<1.0\,	ext{s}$) followed by long-term closed-loop neuromuscular correction ($>1.0\,	ext{s}$).
- Spectral peak: $0.10	ext{--}0.35\,	ext{Hz}$ (dominant at $pprox 0.20\,	ext{Hz}$).
- Head displacement amplitude: Anterior-Posterior $\pm 5	ext{--}12\,	ext{mm}$, Mediolateral $\pm 2	ext{--}5\,	ext{mm}$.
- In the video engine, idling motion is generated by combining two low-frequency pink-noise oscillators ($0.15\,	ext{Hz}$ and $0.25\,	ext{Hz}$) coupled with breathing thoracic lift, avoiding robotic looping.

#### C. Contrapposto: Biomechanics vs. Animator Craft
- **Biomechanical Reality (Winter 2009, Trendelenburg Mechanism)**: Casual standing shifts $>85\%$ of weight onto one stance leg. The stance hip tilts **UP by $4^\circ	ext{--}7^\circ$**; the lumbar spine flexes toward the stance leg; the shoulder girdle tilts in opposition **DOWN by $3^\circ	ext{--}5^\circ$**; and the cervical spine counter-tilts the head level to the horizon ($0^\circ$).
- **Animator Craft Doctrine (Preston Blair 1994, Richard Williams 2001)**:
  - *Preston Blair's Line of Action*: Figures must be unified along a dynamic C-curve or S-curve. Straight vertical lines read as stiff, dead, and robotic.
  - *Richard Williams' Master Law*: *"Hips tilt one way, shoulders tilt the other. NEVER draw hips and shoulders parallel unless the character is a stiff mechanical robot."*
  - *Thomas & Johnston's Anti-Twinning Principle*: Symmetrical limb placement destroys the illusion of life; contrapposto breaks symmetry and communicates relaxed authority.

---

### 2.8 Secondary Motion: Driven Damped Oscillators & Continuum Drag

Secondary appendages (coat tails, ties, hair, identification badges) behave as **driven second-order damped harmonic oscillators**:
$$\ddot{y}_i(t) + 2\zeta \omega_0 \dot{y}_i(t) + \omega_0^2 y_i(t) = -\ddot{x}_{	ext{base}}(t)$$
where $\omega_0 = \sqrt{k/m}$ and damping ratio $\zeta = rac{c}{2\sqrt{km}}$.
- **Phase Lag in Motion**: During continuous movement, the appendage lags the torso by phase angle $\phi = rctan\left(rac{2\zeta (\omega_{	ext{drive}}/\omega_0)}{1 - (\omega_{	ext{drive}}/\omega_0)^2}ight)$.
- **Transient Settle Upon Stopping**: Peak overshoot occurs at $t_p = \pi / \omega_d$ with amplitude $M_p = \exp(-\pi\zeta / \sqrt{1 - \zeta^2})$.
- **Animator Craft Principle (Thomas & Johnston 1981, Richard Williams 2001)**:
  - *Follow Through*: Appendages continue moving after the main body stops.
  - *Overlapping Action*: Secondary settles overlap into the start of the next primary gesture.
  - *Principle of Drag*: "The root moves first, the tip follows last." Appendages bend into reverse C-curves during acceleration, straighten at constant speed, and overshoot into S-curves during deceleration.

---

## 3. Track 2: Object Handling, Grasp Dynamics, and Hand-Prop Interaction

### 3.1 The Cutkosky & Feix (2016) 33-Grasp Taxonomies Mapped to Props

**Cutkosky (1989)** established the classic robotics tree; **Feix et al. (2016)** (*IEEE Trans. Human-Machine Systems* 46(1): 66–77) consolidated all human prehension into **33 discrete grasp types** based on Opposition Type (Pad, Palm, Side) and Thumb State (Abducted vs. Adducted).

```
+-------------------+----------------------------+-----------------------+---------------------------+
| Prop Item         | Primary Grasp Name         | Feix ID / Cutkosky ID | Thumb State & Opposition  |
+-------------------+----------------------------+-----------------------+---------------------------+
| Pen / Stylus      | Writing Tripod (Dynamic)   | Feix #20 / Cutkosky #14| Abducted; Pad + Side      |
| Document / Sheet  | Tip Pinch / Inferior Pincer| Feix #24 / Cutkosky #9 | Abducted; Pad Opposition  |
| Ledger Board / Card| Lateral Pinch / Prismatic 3| Feix #16 or Feix #7   | Adducted; Side Opposition |
| Scale Fulcrum     | Prismatic 2-Finger / Pad   | Feix #8 / Cutkosky #8  | Abducted; Pad Opposition  |
| Scale Counterweight| Tip Pinch (Micro-knob)    | Feix #24 / Cutkosky #9 | Abducted; Pad Opposition  |
| Coin (Table Lift) | Pincer / Fingertip Hook    | Feix #24 / Cutkosky #9 | Abducted; Pad Opposition  |
| Coin (Display)    | Lateral Key Pinch          | Feix #16 / Cutkosky #16| Adducted; Side Opposition |
| Gold Bar (1-Hand) | Prismatic 4-Finger Overhead| Feix #6 / Cutkosky #6  | Abducted; Pad Opposition  |
| Gold Bar (2-Hand) | Bilateral Medium Palm Wrap | Feix #3 / Cutkosky #2  | Abducted; Palm Opposition |
+-------------------+----------------------------+-----------------------+---------------------------+
```

---

### 3.2 Reaching Kinematics: Flash & Hogan Minimum-Jerk Quintic Trajectories

**Flash & Hogan (1985)** (*Journal of Neuroscience* 5(7): 1688–1703):
Voluntary arm reaches optimize kinematic smoothness in Cartesian space by minimizing total jerk $C_J = rac{1}{2} \int_0^{t_f} \|\dddot{\mathbf{r}}(t)\|^2 dt$. The unique mathematical solution is a **5th-degree (quintic) polynomial**:

$$x(	au) = x_0 + (x_f - x_0)\left(10	au^3 - 15	au^4 + 6	au^5ight), \quad 	au = rac{t}{t_f} \in [0, 1]$$

Differentiating yields the **bell-shaped velocity profile**:
$$v(	au) = rac{x_f - x_0}{t_f} \left(30	au^2 - 60	au^3 + 30	au^4ight) = rac{x_f - x_0}{t_f} 30	au^2(1 - 	au)^2$$

- **Peak Velocity**: Occurs precisely at midpoint $	au = 0.50$ ($t = t_f / 2$).
- **Peak-to-Average Velocity Ratio**:
  $$v_{\max} = rac{15}{8} rac{x_f - x_0}{t_f} = 1.875 \cdot ar{v}$$
  Human reaching consistently conforms to this $1.8	ext{--}1.9$ ratio. Paths in Cartesian coordinates are straight lines regardless of target distance.

---

### 3.3 Visuomotor Channels & Jeannerod's Hand Aperture Preshaping

**Jeannerod (1981, 1984)** (*Journal of Motor Behavior* 16(3): 235–254):
Reach-to-grasp movements operate across two parallel, coupled visuomotor channels:
1. **Transport Component** (Proximal arm: shoulder/elbow): Governs arm trajectory toward target coordinates.
2. **Grasp Component** (Distal hand: wrist/fingers): Shapes finger aperture based on intrinsic object size.
- **Maximum Grip Aperture (MGA)**: As the hand approaches the prop, the fingers widen beyond object diameter: $	ext{MGA} = d_{	ext{object}} + 20	ext{--}40\,	ext{mm}$.
- **Temporal Landmark**: MGA occurs at **$60\%	ext{--}75\%$ of total reach duration** ($	au pprox 0.68$), synchronized with peak deceleration of the wrist. During the final $30\%$ of time, the fingers close smoothly around the prop, decelerating to zero velocity at contact.

---

### 3.4 Scene Graph Re-Parenting Math & Virtual Constraint Caching

In a retained 2D/2.5D scene graph, objects cannot be physically moved between layer containers without breaking rendering order or triggering 1-frame position popping.

#### A. Re-Parenting Invariant Matrix Equation
Let Parent $A$ be the World/Table and Parent $B$ be the Character Hand. At handover frame $t^*$, world-space position must remain continuous:
$$\mathbf{M}_{	ext{world, prop}}(t^{*+}) \equiv \mathbf{M}_{	ext{world, prop}}(t^{*-})$$
$$\mathbf{M}_{	ext{world, hand}}(t^*) \cdot \mathbf{M}_{	ext{local-new}} = \mathbf{M}_{	ext{world, prop}}(t^*)$$
$$\mathbf{M}_{	ext{local-new}} = \left(\mathbf{M}_{	ext{world, hand}}(t^*)ight)^{-1} \cdot \mathbf{M}_{	ext{world, prop}}(t^*)$$

#### B. Virtual Parent Constraints with Cached Offsets
Industrial animation engines do not mutate DOM/layer hierarchies. They use **Virtual Parent Constraints**:
1. At pickup frame $t_{	ext{pickup}}$, cache the static offset matrix:
   $$\mathbf{M}_{	ext{offset}} = \mathbf{M}_{	ext{hand}}^{-1}(t_{	ext{pickup}}) \cdot \mathbf{M}_{	ext{world, prop}}(t_{	ext{pickup}})$$
2. While attached, evaluate the prop's world transform directly from the hand:
   $$\mathbf{M}_{	ext{world, prop}}(t) = \mathbf{M}_{	ext{hand}}(t) \cdot \mathbf{M}_{	ext{offset}}$$
3. On release, the prop inherits instantaneous linear and angular velocities:
   $$\mathbf{v}_{	ext{rel}} = \mathbf{v}_{	ext{hand}} + oldsymbol{\omega}_{	ext{hand}} 	imes \mathbf{r}_{	ext{offset}}, \quad oldsymbol{\omega}_{	ext{rel}} = oldsymbol{\omega}_{	ext{hand}}$$

---

### 3.5 Visual Communication of Mass: APAs, Force Coupling, and Lift Recoil

#### A. Anticipatory Postural Adjustments (APAs) Before Lift-Off
**Bouisset & Zattara (1981, 1987)**; **Massion (1992)**:
For heavy props (gold bullion, heavy ledgers), the central nervous system fires postural muscles **$100	ext{--}150\,	ext{ms}$ before the prop leaves the surface**. The torso and pelvis translate backward to counteract the destabilizing forward gravitational torque $\mathbf{r}_{	ext{load}} 	imes m_{	ext{prop}}\mathbf{g}$. If a heavy object lifts without prior trunk recoil, it reads as a weightless Styrofoam replica.

#### B. Grip Force ($F_G$) to Load Force ($F_L$) Coupling
**Johansson & Westling (1984)**; **Johansson & Flanagan (2009)**:
Fingertip grip force increases in parallel with vertical lifting force to prevent slip: $F_G \ge rac{F_L}{2\mu}$. For heavy objects, an extended isometric loading phase occurs: fingers clamp and flesh squashes for $6	ext{--}10$ frames *before* the prop moves a single pixel.

#### C. Lift Recoil ("The Unloading Dip")
When vertical lifting force overcomes object weight, tendon elasticity in the arms causes a momentary visual dip ($1	ext{--}2$ frames of downward deflection) before upward acceleration commences.

---

### 3.6 Placement Dynamics: Damped Harmonic Settling Profiles

When a prop is placed back onto a table, impact dynamics obey a second-order damped harmonic oscillator:
$$m \ddot{y} + c \dot{y} + k (y - y_{	ext{rest}}) = 0, \quad \zeta = rac{c}{2\sqrt{km}}, \quad \omega_n = \sqrt{rac{k}{m}}$$
- **Heavy Rigid Prop (Gold Bar, Iron Vault Box)**: High mass $\implies$ near-critical damping ($\zeta pprox 0.85$). Zero bouncing; a sharp downward compression ($1	ext{--}3	ext{px}$) followed by an immediate rigid halt.
- **Medium Semi-Flexible Prop (Ledger Board, Folio)**: Moderate mass $\implies \zeta pprox 0.60$. Single overshoot rebound ($5\%	ext{--}8\%$) settling in $8	ext{--}12$ frames.
- **Light Rigid Prop (Brass Coin, Weight Token)**: Low mass $\implies$ underdamped metallic rattle ($\zeta pprox 0.35$, $2	ext{--}3$ decaying cycles at high frequency $\omega_n pprox 50\,	ext{rad/s}$).

---

### 3.7 Two-Handed Manipulation: Closed Kinematic Chains (CKC)

When both hands grasp a single rigid object (e.g. a wide ledger board or heavy vault box), independent FK/IK arm control breaks down, causing hands to drift apart and tear object geometry.
- **Kinematic Loop Closure**:
  $$\mathbf{M}_{	ext{torso}} \cdot \mathbf{M}_{	ext{armL}}(oldsymbol{	heta}_L) \cdot \mathbf{M}_{	ext{socketL}} = \mathbf{M}_{	ext{torso}} \cdot \mathbf{M}_{	ext{armR}}(oldsymbol{	heta}_R) \cdot \mathbf{M}_{	ext{socketR}} \cdot \mathbf{M}_{	ext{prop-span}}^{-1}$$
- **Master-Slave Virtual Linkage**:
  1. The prop transform $\mathbf{M}_{	ext{prop}}(t)$ is animated as the master driver.
  2. The prop defines two local hand sockets $\mathbf{S}_L$ and $\mathbf{S}_R$.
  3. Left and right wrists lock to $\mathbf{M}_{	ext{prop}}(t) \cdot \mathbf{S}_L$ and $\mathbf{M}_{	ext{prop}}(t) \cdot \mathbf{S}_R$ using independent 2-bone analytical IK solvers. Panning or tilting the prop automatically articulates elbows, shoulders, and clavicles with $100\%$ zero hand drift.

---

## 4. Track 3: Animating Over a 2D Background (Grounding & Parallax)

### 4.1 Kinematic Zero-Slip & The Ground-Plane Homography Invariant

In 2.5D multiplane systems, foot-sliding and prop drift occur whenever the screen coordinate velocity of the sprite contact point does not match the image velocity of the physical ground surface directly beneath it:
$$\Delta \mathbf{v}(t) = \dot{\mathbf{p}}_{	ext{sprite\_base}}(t) - \dot{\mathbf{p}}_{	ext{ground\_surface}}(t) 
eq \mathbf{0}$$

#### Kinematic Zero-Slip Condition (Kovar, Schreiner, & Gleicher 2002)
During support/contact phases, relative velocity against the contact plane must remain strictly zero:
$$\mathbf{v}_{	ext{rel}} = \dot{\mathbf{p}}_{	ext{contact}} - \dot{\mathbf{p}}_{	ext{surface}} = \mathbf{0}, \quad orall t \in [t_{	ext{plant}}, t_{	ext{lift}}]$$

#### Ground-Plane Homography Invariant (Hartley & Zisserman 2004)
For a camera observing a planar ground surface $oldsymbol{\pi} = [\mathbf{n}^T, d]^T$, image points transform strictly via planar homography:
$$\mathbf{p}' \sim \mathbf{H}_{oldsymbol{\pi}} \mathbf{p} = \mathbf{K} \left( \mathbf{R} - rac{\mathbf{t} \mathbf{n}^T}{d} ight) \mathbf{K}^{-1} \mathbf{p}$$
- **Implementation Rule**: Characters and props must set `transform-origin: 50% 100%` (anchored at the baseline). Translation must bind to $\mathbf{H}_{oldsymbol{\pi}} \mathbf{p}_{	ext{contact}}$, never to independent linear screen-space tweens.

---

### 4.2 The Dual-Component Contact Shadow Model: AO Slit vs. Diffuse Cast

A single blurred ellipse or uniform CSS `drop-shadow` is the primary reason composited elements look like "floating stickers". VFX compositing science (**Brinkmann 2008**; **Wright 2017**) requires splitting shadows into two distinct physical phenomena:

```
[ Character / Prop Cutout ]
           │
           ▼
=======================  <--- 1. Ambient Occlusion Contact Slit (Tight, pitch-dark, 0-2px blur)
 \                   /
  \  Cast Shadow    /    <--- 2. Directional Diffuse Shadow (Elongated, blurred penumbra)
   \_______________/
```

1. **Ambient Occlusion (AO) Contact Slit (Zhukov et al. 1998, Landis 2002)**:
   - *Physics*: As distance $h 	o 0$, ambient hemisphere visibility $A(\mathbf{p}) = rac{1}{\pi} \int_{\Omega} V(\mathbf{p}, oldsymbol{\omega})(\mathbf{n}\cdotoldsymbol{\omega})doldsymbol{\omega} 	o 0$. All environmental diffuse skylight is occluded.
   - *Parameters*: Height $1	ext{--}4	ext{px}$ at 1080p; opacity $lpha \in [0.80, 0.95]$; dark ink tone (`#141B22` or `#25313C`); Gaussian blur $\sigma pprox 0.5	ext{--}1.2	ext{px}$; zero directional offset.
2. **Directional Diffuse Cast Shadow (Penumbra Expansion)**:
   - *Physics*: Extended light sources produce distance-dependent penumbra widening: $w_p(z) pprox k_{	ext{penumbra}} \cdot z$.
   - *Parameters*: Blur kernel expands with distance from baseline: $\sigma(y) = \sigma_0 + k(y_{	ext{base}} - y)$; opacity decays exponentially: $lpha(y) = lpha_0 \exp(-k_{	ext{decay}}(y_{	ext{base}} - y))$.

---

### 4.3 Blinn's Planar Shadow Matrix & 2.5D Affine Shear Projections

#### Blinn's $4 	imes 4$ Planar Projection Matrix (Jim Blinn 1988)
In *"Me and My (Fake) Shadow"* (*IEEE CG&A*, Jan 1988), Jim Blinn derived the projective transformation projecting 3D vertices onto plane $\mathbf{P} = [\mathbf{n}^T, d]^T$ from light source $\mathbf{L} = [l_x, l_y, l_z, l_w]^T$:
$$\mathbf{M}_{	ext{shadow}} = (\mathbf{n} \cdot \mathbf{l} + d \cdot l_w) \mathbf{I}_{4 	imes 4} - \mathbf{l} \mathbf{n}^T$$

#### 2.5D Affine Ground Projection Matrix ($\mathbf{S}_{	ext{shadow}}$)
In 2D/2.5D compositing engines, projecting a vertical 2D sprite onto a horizontal receding ground surface is computed via an affine shear-compression transform:
$$\mathbf{S}_{	ext{shadow}} = \mathbf{T}(x_0, y_{	ext{base}}) \cdot egin{bmatrix} 1 & -k_x & 0 \ 0 & k_y & 0 \ 0 & 0 & 1 \end{bmatrix} \cdot \mathbf{T}(-x_0, -y_{	ext{base}})$$
where:
$$k_x = rac{\cos \phi_{	ext{light}}}{	an lpha_{	ext{light}}} \quad (	ext{horizontal shear}), \quad k_y = -rac{\sin \phi_{	ext{light}} \cdot \cos 	heta_{	ext{cam}}}{	an lpha_{	ext{light}}} \quad (	ext{vertical compression})$$

---

### 4.4 Multi-Plane Disparity Sampling: LDIs and MPIs in 2.5D

- **Layered Depth Images (LDI)** (**Shade et al., SIGGRAPH 1998**): Store layered depth cards to render parallax without 3D geometry (`far`, `board`, `mid`, `cast`, `near`).
- **Multi-Plane Images (MPI)** (**Zhou et al., SIGGRAPH 2018**): Sample scene planes uniformly in **disparity (inverse depth $1/Z$)**, rather than linear distance:
  $$d_i = rac{1}{Z_i} = d_{	ext{min}} + rac{i}{D - 1}(d_{	ext{max}} - d_{	ext{min}})$$
  Uniform disparity sampling guarantees constant perceptual parallax increments across all layers, eliminating unnatural clustering in the foreground.

---

### 4.5 Vanishing Point Alignment & The Norling Eye-Line Theorem

#### The Perspective Horizon Invariant (Hartley & Zisserman 2004)
For a pinhole camera with vertical focal length $f_y$, principal point $c_y$, and tilt angle $	heta_{	ext{tilt}}$:
$$y_{	ext{horizon}} = c_y + f_y 	an(	heta_{	ext{tilt}})$$

#### The Eye-Line Theorem (Norling; Brinkmann 2008)
> **Theorem**: If a camera is level ($	heta_{	ext{tilt}} = 0$) at camera height $h_{	ext{cam}}$, and characters stand on that horizontal ground plane with eye height $h_{	ext{eye}} = h_{	ext{cam}}$, then **the horizon line passes through the eyes of EVERY character**, regardless of distance from the camera!

If character height is $H_{	ext{char}}$ at distance $Z$:
$$y_{	ext{feet}}(Z) = y_{	ext{horizon}} + f_y rac{h_{	ext{cam}}}{Z}, \quad y_{	ext{head}}(Z) = y_{	ext{horizon}} + f_y rac{h_{	ext{cam}} - H_{	ext{char}}}{Z}$$
- **Failure Mode**: If an AI-generated background has vanishing lines converging to $y = 0.50$ (screen center), but the character is composited with eyes at $y = 0.30$ and feet at $y = 0.98$, the viewer subconsciously perceives the character leaning backward or standing in a pit. The horizon line must remain the invariant anchor across all composited layers.

---

### 4.6 Parallax Differentials & Resolving the Floor-Shear Paradox

Lateral camera movement at speed $v_{	ext{cam}} = T_x$ creates layer velocity differentials:
$$v_{	ext{layer}} = -rac{f \cdot T_x}{Z_{	ext{layer}}} = v_{	ext{cam}} \cdot \left(rac{Z_{	ext{near}}}{Z_{	ext{layer}}}ight)$$

#### The Floor-Shear Paradox
If the background floor belongs to layer `-far` (moving at $1.00	imes$) while the character stands in layer `[cast]` (moving at $1.25	imes$), the character's feet will shear across the floorboards at $0.25 	imes v_{	ext{cam}}$.
- **The Ground Anchor Resolution**: The character's sprite translation must be dynamically locked to the local floor image velocity directly beneath its contact baseline:
  $$v_{	ext{sprite}}(t) \equiv v_{	ext{floor}}(y_{	ext{baseline}}, t)$$
  Floor velocity interpolates continuously from horizon ($1.00	imes$) to bottom screen margin ($1.40	imes$).

---

### 4.7 Visual Harmonization: Koschmieder's Law, Light Wrap, and Substrate Bleed

1. **Aerial Perspective & Koschmieder's Law (Koschmieder 1924)**:
   Radiance attenuates over distance $d$: $L(d) = L_0 e^{-eta d} + L_{	ext{airlight}}(1 - e^{-eta d})$. In our video engine, background layers undergo contrast attenuation and chromatic drift toward the cream washi ground (`#F4E6C7`), while the hero host retains maximum saturation ($0.665$) and rich woodblock ink line contrast ($2:1$ rendering-weight hierarchy).
2. **Light Wrap Edge Convolution (Brinkmann 2008, Wright 2017)**:
   Extract an inward edge matte $M_{	ext{edge}} = lpha_{	ext{fg}} \cdot \operatorname{clamp}((1 - lpha_{	ext{fg}}) * G_{\sigma_{	ext{wrap}}}, 0, 1)$ with $\sigma pprox 4	ext{--}12	ext{px}$. Bleeding blurred background color onto the character's outer perimeter eliminates the sharp "sticker cutout" look.
3. **Substrate Paper Grain Bleed**:
   Vector characters must not look like smooth digital plastic. Modulate vector fills with high-frequency washi paper noise ($T_{	ext{washi}}$):
   $$C_{	ext{integrated}} = C_{	ext{vector}} \cdot [1.0 + \kappa_{	ext{grain}} (T_{	ext{washi}} - 0.5)], \quad \kappa_{	ext{grain}} pprox 0.12	ext{--}0.16$$
   Strokes use woodblock charcoal (`#25313C`) rather than raw `#000000`, with a sub-pixel $0.6	ext{--}0.8	ext{px}$ alpha feather to emulate ink fiber soaking.

---

## 5. Production Code Blueprints

### Blueprint A: Flash-Hogan Minimum-Jerk Reach-to-Grasp Generator (TypeScript)
```typescript
/**
 * Evaluates Flash & Hogan (1985) Minimum-Jerk kinematic reach trajectory
 * with Jeannerod (1984) hand aperture preshaping.
 */
export function evaluateReachToGrasp(
  p0: [number, number],
  p1: [number, number],
  t: number,
  d: number,
  objectWidth: number
) {
  const tau = Math.max(0, Math.min(1, t / d));
  
  // Quintic polynomial basis: x(tau) = 10*tau^3 - 15*tau^4 + 6*tau^5
  const tau3 = tau * tau * tau;
  const tau4 = tau3 * tau;
  const tau5 = tau4 * tau;
  
  const polyPos = 10 * tau3 - 15 * tau4 + 6 * tau5;
  const polyVel = (30 * tau * tau - 60 * tau3 + 30 * tau4) / d;
  const polyAcc = (60 * tau - 180 * tau * tau + 120 * tau3) / (d * d);
  
  const dx = p1[0] - p0[0];
  const dy = p1[1] - p0[1];
  
  const pos: [number, number] = [p0[0] + dx * polyPos, p0[1] + dy * polyPos];
  const vel: [number, number] = [dx * polyVel, dy * polyVel];
  const acc: [number, number] = [dx * polyAcc, dy * polyAcc];
  
  // Jeannerod (1984) Hand Aperture Preshaping:
  // MGA peaks at tau = 0.68 (objectWidth + 28px), then closes smoothly to objectWidth
  const mga = objectWidth + 28;
  let aperture: number;
  if (tau < 0.68) {
    const s = tau / 0.68;
    aperture = objectWidth * 0.4 + (mga - objectWidth * 0.4) * Math.sin((s * Math.PI) / 2);
  } else {
    const s = (tau - 0.68) / (1.0 - 0.68);
    const easeOut = 1 - Math.pow(1 - s, 2);
    aperture = mga - (mga - objectWidth) * easeOut;
  }
  
  return { pos, vel, acc, aperture, tau };
}
```

### Blueprint B: Affine $3 	imes 3$ Matrix Re-Parenting & Attachment Solver (TypeScript)
```typescript
export interface Matrix3x3 {
  a: number; b: number; c: number; d: number; tx: number; ty: number;
}

export function invertMatrix3x3(m: Matrix3x3): Matrix3x3 {
  const det = m.a * m.d - m.b * m.c;
  if (Math.abs(det) < 1e-9) throw new Error("Singular transform matrix");
  const invDet = 1.0 / det;
  return {
    a:  m.d * invDet,
    b: -m.b * invDet,
    c: -m.c * invDet,
    d:  m.a * invDet,
    tx: (m.c * m.ty - m.d * m.tx) * invDet,
    ty: (m.b * m.tx - m.a * m.ty) * invDet
  };
}

export function multiplyMatrix3x3(m1: Matrix3x3, m2: Matrix3x3): Matrix3x3 {
  return {
    a: m1.a * m2.a + m1.c * m2.b,
    b: m1.b * m2.a + m1.d * m2.b,
    c: m1.a * m2.c + m1.c * m2.d,
    d: m1.b * m2.c + m1.d * m2.d,
    tx: m1.a * m2.tx + m1.c * m2.ty + m1.tx,
    ty: m1.b * m2.tx + m1.d * m2.ty + m1.ty
  };
}

/**
 * Computes the cached offset matrix: M_offset = inv(M_hand) * M_world_prop
 */
export function cacheAttachmentOffset(mHandWorld: Matrix3x3, mPropWorld: Matrix3x3): Matrix3x3 {
  const invHand = invertMatrix3x3(mHandWorld);
  return multiplyMatrix3x3(invHand, mPropWorld);
}

/**
 * Evaluates active follower constraint: M_prop_world = M_hand_world * M_offset
 */
export function evaluateAttachedProp(mHandWorld: Matrix3x3, mOffset: Matrix3x3): Matrix3x3 {
  return multiplyMatrix3x3(mHandWorld, mOffset);
}
```

### Blueprint C: Analytical 2-Bone Trigonometric IK Solver (TypeScript)
```typescript
/**
 * Closed-form analytical 2-bone IK solver (O(1) time and space).
 */
export function solve2BoneIK(
  root: [number, number],
  target: [number, number],
  l1: number,
  l2: number,
  hingeDir: number // +1 = elbow up, -1 = elbow down
) {
  const dx = target[0] - root[0];
  const dy = target[1] - root[1];
  const d = Math.sqrt(dx * dx + dy * dy);
  
  // Clamp target distance within reach envelope
  const dClamped = Math.max(Math.abs(l1 - l2) + 1e-4, Math.min(l1 + l2 - 1e-4, d));
  
  const baseAngle = Math.atan2(dy, dx);
  const cosElbow = (l1 * l1 + l2 * l2 - dClamped * dClamped) / (2 * l1 * l2);
  const elbowAngle = Math.PI - Math.acos(Math.max(-1, Math.min(1, cosElbow)));
  
  const cosShoulder = (l1 * l1 + dClamped * dClamped - l2 * l2) / (2 * l1 * dClamped);
  const shoulderOffset = Math.acos(Math.max(-1, Math.min(1, cosShoulder)));
  const shoulderAngle = baseAngle + hingeDir * shoulderOffset;
  
  const midJoint: [number, number] = [
    root[0] + l1 * Math.cos(shoulderAngle),
    root[1] + l1 * Math.sin(shoulderAngle)
  ];
  
  return {
    shoulderAngle,
    elbowAngle: shoulderAngle + hingeDir * (Math.PI - elbowAngle),
    midJoint,
    endJoint: target
  };
}
```

### Blueprint D: Placement Settling Damped Spring Evaluator (TypeScript)
```typescript
export function evaluatePlacementSettling(
  tAfterContact: number,
  massType: "HEAVY_GOLD" | "MEDIUM_LEDGER" | "LIGHT_COIN"
) {
  const configs = {
    HEAVY_GOLD:    { omega_n: 18.0, zeta: 0.85, v0: 45.0, squash: 0.15 },
    MEDIUM_LEDGER: { omega_n: 24.0, zeta: 0.60, v0: 30.0, squash: 0.08 },
    LIGHT_COIN:    { omega_n: 52.0, zeta: 0.35, v0: 20.0, squash: 0.02 }
  };
  
  const c = configs[massType];
  const t = Math.max(0, tAfterContact);
  if (t > 0.4) return { deltaY: 0, squashScaleY: 1.0 };
  
  const omega_d = c.omega_n * Math.sqrt(Math.max(0, 1 - c.zeta * c.zeta));
  const envelope = Math.exp(-c.zeta * c.omega_n * t);
  const deltaY = (c.v0 / (omega_d || 1)) * envelope * Math.sin(omega_d * t);
  const squashScaleY = 1.0 - (c.squash * envelope * Math.cos(omega_d * t));
  
  return { deltaY, squashScaleY };
}
```

### Blueprint E: Dual-Shadow SVG Filter & Substrate Grain Blend (SVG/XML)
```html
<svg width="0" height="0" style="position: absolute;">
  <defs>
    <!-- Contact Slit (Tight Ambient Occlusion) -->
    <filter id="ao-contact-slit" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="0.8" result="blur" />
      <feColorMatrix in="blur" type="matrix" values="
        0 0 0 0 0.145
        0 0 0 0 0.192
        0 0 0 0 0.235
        0 0 0 0.90 0" result="coloredSlit" />
      <feMerge>
        <feMergeNode in="coloredSlit" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- Substrate Paper Grain Blend -->
    <filter id="washi-substrate-blend">
      <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" result="noise" />
      <feColorMatrix type="matrix" values="
        0 0 0 0 0.957
        0 0 0 0 0.902
        0 0 0 0 0.780
        0 0 0 0.14 0" result="washiColor" />
      <feComposite in="SourceGraphic" in2="washiColor" operator="arithmetic" k1="0" k2="1" k3="0.15" k4="0" />
    </filter>
  </defs>
</svg>
```

### Blueprint F: Remotion/React Ground-Locked Parallax Hook
```typescript
import { interpolate } from "remotion";

interface GroundLockConfig {
  cameraPanX: number;     // px
  yBaseline: number;      // 0.98
  yHorizon: number;       // 0.50
  farParallax: number;    // 1.00
  nearParallax: number;   // 1.40
}

export function useGroundLockedTransform(config: GroundLockConfig) {
  const { cameraPanX, yBaseline, yHorizon, farParallax, nearParallax } = config;

  // Intercept ground disparity at character contact baseline
  const groundFactor = interpolate(
    yBaseline,
    [yHorizon, 1.0],
    [farParallax, nearParallax],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const spriteTranslateX = -cameraPanX * groundFactor;

  return {
    transform: `translateX(${spriteTranslateX}px)`,
    transformOrigin: "50% 100%",
  };
}
```

---

## 6. Master Citation & Authority Registry

### 6.1 Biomechanics, Motor Control & Mathematics
1. **Hof, A. L., Gazendam, M. G. J., & Sinke, W. E.** (2005). *The condition for dynamic stability*. **Journal of Biomechanics**, 38(1), 1–8. DOI: 10.1016/j.jbiomech.2004.03.025. *(Mathematical formulation of XCOM and Margin of Stability)*.
2. **Aristidou, Andreas, & Joan Lasenby** (2011). *FABRIK: a fast, iterative solver for the inverse kinematics problem*. **Graphical Models**, 73(5), 243–260. DOI: 10.1016/j.gmod.2011.05.003.
3. **Flash, Tamar, & Neville Hogan** (1985). *The coordination of arm movements: an experimentally confirmed mathematical model*. **Journal of Neuroscience**, 5(7), 1688–1703. DOI: 10.1523/JNEUROSCI.05-07-01688.1985. *(Minimum-jerk quintic trajectory derivation)*.
4. **Feix, Thomas, Javier Romero, Heinz-Bodo Schmiedmayer, Aaron M. Dollar, & Danica Kragić** (2016). *The GRASP Taxonomy of Human Grasp Types*. **IEEE Transactions on Human-Machine Systems**, 46(1), 66–77. DOI: 10.1109/THMS.2015.2470657. *(Comprehensive 33-grasp taxonomy)*.
5. **Cutkosky, Mark R.** (1989). *On grasp choice, grasp models, and the design of hands for manufacturing tasks*. **IEEE Transactions on Robotics and Automation**, 5(3), 269–279. DOI: 10.1109/70.34763.
6. **Jeannerod, Marc** (1984). *The timing of natural prehension movements*. **Journal of Motor Behavior**, 16(3), 235–254. DOI: 10.1080/00222895.1984.10735319. *(Hand aperture preshaping & visuomotor channels)*.
7. **Jacobson, Alec, Ilya Baran, Jovan Popović, & Olga Sorkine** (2011). *Bounded biharmonic weights for real-time deformation*. **ACM Transactions on Graphics (SIGGRAPH 2011)**, 30(4), Art. 78. DOI: 10.1145/2010324.1964973.
8. **Kavan, Ladislav, Steven Collins, Jiří Žára, & Carol O'Sullivan** (2008). *Geometric Skinning with Dual Quaternions*. **IEEE Transactions on Visualization and Computer Graphics**, 14(5), 1055–1071. DOI: 10.1109/TVCG.2008.59. *(Zero-volume-collapse 2D/3D skinning)*.
9. **Winter, David A.** (2009). *Biomechanics and Motor Control of Human Movement* (4th ed.). John Wiley & Sons. ISBN: 978-0-470-39818-0. *(Anthropometric tables, COM mechanics, Trendelenburg contrapposto)*.
10. **Bouisset, S., & M. C. Do** (2008). *Posture, dynamic stability, and voluntary movement*. **Neurophysiologie Clinique**, 38(6), 345–362. DOI: 10.1016/j.neucli.2008.10.001. *(Anticipatory Postural Adjustments - APAs)*.
11. **Johansson, Roland S., & J. Randall Flanagan** (2009). *Coding and use of tactile signals from the fingertips in object manipulation tasks*. **Nature Reviews Neuroscience**, 10(5), 345–359. DOI: 10.1038/nrn2621. *(Grip-to-load force coupling)*.
12. **Blinn, James F.** (1988). *Jim Blinn’s Corner: Me and My (Fake) Shadow*. **IEEE Computer Graphics and Applications**, 8(1), 82–86. DOI: 10.1109/38.30. *(Foundational derivation of the 4x4 planar shadow projection matrix)*.
13. **Hartley, Richard, & Andrew Zisserman** (2004). *Multiple View Geometry in Computer Vision* (2nd ed.). Cambridge University Press. ISBN: 978-0521540513. *(Ground-plane homographies and vanishing line geometry)*.
14. **Kovar, Lucas, John Schreiner, & Michael Gleicher** (2002). *Footskate Cleanup for Motion Capture Editing*. **Proceedings of ACM SIGGRAPH/Eurographics SCA 2002**, 97–104. DOI: 10.1145/545261.545277. *(Kinematic zero-slip condition)*.
15. **Koschmieder, Harald** (1924). *Theorie der horizontalen Sichtweite*. **Beiträge zur Physik der freien Atmosphäre**, 12, 33–53. *(Atmospheric optical attenuation)*.

### 6.2 Animator Craft & Compositing Doctrine
16. **Williams, Richard** (2001). *The Animator's Survival Kit*. Faber & Faber. *(Opposing angles, weight anticipation, follow-through drag)*.
17. **Thomas, Frank, & Ollie Johnston** (1981). *The Illusion of Life: Disney Animation*. Abbeville Press. *(Squash & stretch, anticipation, anti-twinning)*.
18. **Blair, Preston** (1994). *Cartoon Animation*. Walter Foster Publishing. *(Dynamic Line of Action)*.
19. **Brinkmann, Ron** (2008). *The Art and Science of Digital Compositing* (2nd ed.). Morgan Kaufmann. ISBN: 978-0123706386. *(Matte manipulation, light wrap, and contact shadows)*.
20. **Wright, Steve** (2017). *Digital Compositing for Film and Video* (4th ed.). Routledge. ISBN: 978-1138240377. *(Edge halation and matchmoving contact)*.

---

## 7. Pipeline Triage & Doctrine Recommendations

```
+----------------------------------------------------------------------------------------------------+
|                                    THREE-TIER PIPELINE TRIAGE                                      |
+-------------------+----------------------------+-----------------------+---------------------------+
| Triage Tier       | Definition & Standard      | Artifacts in this Tier| Immediate Action          |
+-------------------+----------------------------+-----------------------+---------------------------+
| TIER 1:           | Mathematically proven      | • 2-Bone Analytical IK| Merge directly into       |
| Implemented       | algorithms and physical    | • Flash-Hogan Min-Jerk| Remotion / HyperFrames    |
| Engineering       | equations with zero        | • Matrix Re-Parenting | drawing engine and scene  |
| (Ready for Code)  | empirical ambiguity.       | • Blinn Shadow Matrix | graph modules.            |
|                   |                            | • Ground Homography H |                           |
|                   |                            | • BBW / DQS Skinning  |                           |
| TIER 2:           | Practical defaults, timing | • Respiration timing  | Expose as configurable    |
| Design Proposals  | presets, and spring dials  |   (3.8s, 1:1.7 ratio) | defaults in character and |
| & Heuristics      | derived from craft or eye. | • Feix grasp mappings | prop component templates. |
| (Config Defaults) | NOT rigid dogma.           | • Settling spring     |                           |
|                   |                            |   parameters (c, k)   |                           |
| TIER 3:           | Operational rules requiring| • The Norling Eye-Line| Require operator review   |
| Candidate         | 5-episode benchmarking     |   Theorem horizon lock| across test cuts before   |
| Doctrine Rules    | before repository          | • Dual-Component AO   | promoting to GATES-MOTION |
| (Under Review)    | codification.              |   contact slit model  | or DOCTRINE-CORE.         |
|                   |                            | • Pre-lift APA recoil |                           |
+-------------------+----------------------------+-----------------------+---------------------------+
```
