# The Relation Layer: What 2D Rigs and Constraint Systems Get Right, Harvested

**Pass Metadata**:
- **Workflow**: Deep Research Engine (`/research --deep`)
- **Date**: 2026-09-14
- **Profile**: `video-researcher`
- **Order Reference**: `docs/runbooks/WORK-ORDER-GEMINI-RIG-LAYER-2026-09-14.md` | Bridge Packet `cee8b03cbd8f` | BACKLOG `R26-121`
- **Target Repository**: `C:/Users/Snipe/Downloads/Outreach Program`
- **Output Artifact**: `docs/research/motion/RIG_CONSTRAINTS_RELATION_LAYER_RESEARCH_BLUEPRINT.md`
- **Status**: COMPLETE PRIMARY SOURCING & SYNTHESIS

---

## The Question

The operator (2026-09-13 grill session, `docs/content-video-engine/GRILL-PIPELINE-VALUE-2026-09-13.md`):
> *"rigging was thought of as a 'move humans' thing, but it can also move evidence around the screen and manipulate camera perspective - it might be time to develop that aspect."*

BACKLOG `R26-105` names the relation layer (`rel: {pin | aim | group | path | derive | camera | weight}`), unbuilt. Our current engine moves every visual plate via an authored timeline clock (a pure function of $t$); nothing yet moves an object *because another moved*. Operator Ruling E97 (`docs/portable/OPERATOR-RULINGS.md:2815`) governs the contract: closed-form relations only, translate-only inheritance by default (`inherit: [translate]`), uniform parent scaling, and seek-safe execution.

This investigation harvests exact mechanisms, evaluation algorithms, and standard mathematical formulations across five core domains without proposing an editor shell:
1. **Rive's State Machine + Constraints**: The constraint set (IK, Distance, Transform, Translation, Rotation, Scale, Follow Path), target declaration, state blending mechanics, and the boundary separating harvestable mathematical mechanisms from product GUI shell.
2. **Spine & DragonBones**: Constraint types, evaluation order rules, and the exact resolution rule when two constraints act upon a single bone (with verbatim documentation citation).
3. **After Effects Expressions + Graph Editor**: The core expression idioms motion designers actually use to move evidence (`wiggle`, `loopOut`, `valueAtTime`, parenting, null objects, camera point of interest) and practical 2D camera rigs for chart-and-card scenes.
4. **Theatre.js & Code-First Timelines**: Keyframe and easing data structures exposed to code, what a pure function of $t$ looks like, and whether any system supports declarative property derivation (`derive`).
5. **Minimal 2D Constraint Solver Mathematics**: Pure, closed-form formulations of `pin`, `aim`, `follow-path`, analytical two-bone IK (law of cosines), and weight/lag without numerical iteration or stateful history buffers.

---

## Verdict Up Front

1. **Rive's Harvestable Core is a Decompose-Lerp-Compose DAG**: Rive implements 7 constraint primitives `[source on file]`. Its harvestable mechanism is an explicit directed acyclic graph (DAG) where constraints register dependency edges (`target->addDependent(this); addDependent(parent());`) and evaluate affine updates by decomposing $2\times3$ matrices into translation, rotation, scale, and skew, linearly interpolating components by a scalar `strength` $\in [0, 1]$, and recomposing `[source on file]`. Blend States (1D and Direct) mix timeline tracks via piece-wise linear thresholds or additive weights `[source on file]`. The GUI visualizer, pointer triggers, and view-model bindings are product shell and should not be ported `[practitioner doctrine]`.
2. **Spine Evaluates Constraints Sequentially in Tree Order; Later Transforms Overwrite Earlier Transforms**: Spine provides 3 constraint primitives (IK, Transform, Path) `[source on file]`. Evaluation order is strictly sequential according to the top-to-bottom order under the `Constraints` tree node `[source on file]`. When two constraints affect the same bone, Spine does *not* run an iterative relaxation solver: it executes the first constraint, recalculates world transforms down the hierarchy, and then executes the second `[source on file]`. The verbatim rule states: *"If a constraint is applied and modifies a bone, then another constraint is applied that causes the world transform for that bone to be recomputed, the modifications made by the first constraint will be lost"* (Esoteric Software User Guide) `[source on file]`.
3. **After Effects Relies on 4 Core Temporal Idioms and Inverted-Stage 2D Camera Rigs**: Production evidence motion uses `wiggle(freq, amp)` for pseudo-random micro-drift, `loopOut("cycle"|"continue")` for data stream loops, and `valueAtTime(time - delay)` for multi-card trailing cascades `[source on file]`. In 2D documentary chart-and-card motion (Bravos-style), practitioners avoid native 3D camera drift by using an inverted-stage "World Master Null": pushing into evidence is achieved by centering the scene anchor point on the evidence element's world coordinates and scaling the world null up `[practitioner doctrine]`. Labels prevent shear distortion via counter-scaling (`10000 / parent.scale`) or translate-only world pinning (`toWorld()`), matching Operator Ruling E97 `[source on file]`.
4. **Theatre.js Exposes Cubic Bézier Handles but Completely Lacks Declarative Derivations**: In Theatre.js (`@theatre/core`), keyframes are stored in `BasicKeyframedTrack` with four-parameter cubic Bézier tangent handles `handles: [x1, y1, x2, y2]` identical to CSS `cubic-bezier` `[source on file]`. Timelines evaluate synchronously as a pure function of playhead position (`sequence.position = t`) `[source on file]`. However, Theatre.js has **zero declarative derivation syntax** (no `derive` equivalent); derived relations require imperative external event listeners (`onChange(pointer, cb)`) `[source on file]`. The closest declarative analogue in the web motion ecosystem is Framer Motion's `useTransform(motionValue, fn)` `[source on file]`.
5. **The Minimal 2D Solver Math is Completely Solvable in Closed Form ($O(1)$, Seek-Safe)**: All required relations can be formulated without iterative loops or frame history buffers `[DERIVED]`:
   - `pin`: $\mathbf{p}_C(t) = \mathbf{p}_T(t) + \mathbf{o}$ (translate-only default) or $\mathbf{p}_C(t) = \mathbf{p}_T(t) + \mathbf{R}(\theta_T)(\mathbf{S}_T \odot \mathbf{o})$ (full socket) `[source on file]`.
   - `aim`: $\theta(t) = \operatorname{atan2}(y_T - y_S, x_T - x_S) + \theta_{\text{offset}}$ blended via shortest-arc angular interpolation `[source on file]`.
   - `follow-path`: Inverted arc-length LUT $u = s^{-1}(p \cdot L)$, evaluating position $\mathbf{C}(u)$ and Frenet tangent orientation $\operatorname{atan2}(t_y, t_x)$ `[source on file]`.
   - `two-bone IK`: Exact planar analytical solution via the Law of Cosines for elbow angle $\theta_2 = \sigma \arccos(\frac{d^2 - l_1^2 - l_2^2}{2 l_1 l_2})$ and shoulder angle $\theta_1 = \alpha - \sigma \beta$, clamped to $[|l_1 - l_2|, l_1 + l_2]$ `[source on file]`.
   - `weight/lag`: Pure temporal translation $\mathbf{x}_{\text{follower}}(t) = \mathbf{x}_{\text{leader}}(t - \tau)$ or analytical critically damped step response $(1 + \omega_n \Delta t) e^{-\omega_n \Delta t}$, guaranteeing identical output regardless of scrub direction `[source on file]`.

---

## Master Table of Numbers

| Question | Constraint / System Dimension | Specification / Metric Value | Primary Authority & Documentation URL | Evidentiary Tag |
|---|---|---|---|---|
| **Q1** | Rive Constraint Primitives | 7 native constraints (IK, Distance, Transform, Translation, Rotation, Scale, Follow Path) | Rive Runtime Doc | `[source on file]` |
| **Q1** | Rive Constraint Strength Range | Scalar `strength` $\in [0.0, 1.0]$ (linear lerp between unconstrained and constrained pose) | Rive Runtime Source (`transform_constraint.cpp`) | `[source on file]` |
| **Q1** | Rive Distance Constraint Modes | 3 geometric clamp modes: `0: Closer` ($\le d$), `1: Further` ($\ge d$), `2: Exact` ($= d$) | Rive Runtime Documentation | `[source on file]` |
| **Q1** | Rive Transition Duration Default | 0 ms default (instantaneous cut); configurable with Bézier easing curves | Rive State Machine Documentation | `[source on file]` |
| **Q1** | Rive Coordinate Space Permutations | 4 combinations: Source (`world` \| `local`) $\times$ Destination (`world` \| `local`) | Rive Runtime Documentation | `[source on file]` |
| **Q2** | Spine Constraint Primitives | 3 types: IK Constraints, Transform Constraints, Path Constraints | Esoteric Software Spine User Guide | `[source on file]` |
| **Q2** | Spine Constraint Evaluation Order | Top-to-bottom list order under `Constraints` tree node (Index $0$ to $N-1$) | Esoteric Software Spine User Guide | `[source on file]` |
| **Q2** | Spine Transform Mix Channels | 4 independent mixes: `translateMix`, `rotateMix`, `scaleMix`, `shearMix` $\in [0.0, 1.0]$ | Esoteric Software Spine Transform Constraints | `[source on file]` |
| **Q2** | Spine Path Spacing Modes | 4 modes: `Length`, `Fixed`, `Percent`, `Proportional` | Esoteric Software Spine Path Constraints | `[source on file]` |
| **Q2** | Spine Path Rotation Modes | 3 modes: `Tangent` (points along path), `Chain` (rigid links), `Chain Scale` (elastic links) | Esoteric Software Spine Path Constraints | `[source on file]` |
| **Q2** | DragonBones Constraint Order Property | `public order : number` (integer sort key inside `ConstraintData`) | Cocos Creator DragonBones API (`ConstraintData.d.ts`) | `[source on file]` |
| **Q3** | AE `wiggle` Default Parameter Count | 5 parameters: `wiggle(freq, amp, octaves=1, amp_mult=0.5, t=time)` | Adobe After Effects Expression Reference | `[source on file]` |
| **Q3** | AE `loopOut` Extrapolation Types | 4 types: `"cycle"`, `"pingpong"`, `"offset"`, `"continue"` | Adobe After Effects Expression Reference | `[source on file]` |
| **Q3** | AE Counter-Scale Formula | $[10000 / s_x, 10000 / s_y]$ (cancels parent scale to prevent label distortion) | MotionScript / Dan Ebberts | `[practitioner doctrine]` |
| **Q3** | 2D Camera Rig Virtual Inversion | $\mathbf{p}_{\text{stage}} = \mathbf{c}_{\text{screen}} - \mathbf{p}_{\text{target}} \cdot S, \quad S = \text{Zoom} \cdot 100\%$ | Motion Design Industry Doctrine | `[practitioner doctrine]` |
| **Q4** | Theatre.js Bézier Handle Vector | 4 floats: `handles: [x1, y1, x2, y2]` in CSS cubic-bezier normalized range $[0, 1]$ | Theatre.js Core Sequence Documentation | `[source on file]` |
| **Q4** | Theatre.js Playhead Evaluation | Synchronous $t \to \text{state}$ via `sequence.position = t` | Theatre.js Core API Documentation | `[source on file]` |
| **Q4** | Declarative Derivation in Timeline | 0 native support in Theatre.js; requires imperative `onChange()` subscriber side-channel | Theatre.js Documentation | `[source on file]` |
| **Q5** | Two-Bone IK Link Count | Exactly 2 planar links ($l_1, l_2$) solved via Law of Cosines | Craig, *Introduction to Robotics*, Ch. 4 | `[source on file]` |
| **Q5** | Two-Bone IK Singularity Tolerance | Reach clamped to $[|l_1 - l_2| + \epsilon, l_1 + l_2 - \epsilon]$ with $\epsilon = 10^{-4}$ | Buss, *3D Computer Graphics*, Ch. 16 | `[source on file]` |
| **Q5** | Temporal Lag Evaluation Complexity | $O(1)$ constant time lookup: $\mathbf{x}_{\text{follower}}(t) = \mathbf{x}_{\text{leader}}(t - \tau)$ | Closed-form Kinematics / Ruling E97 | `[DERIVED]` |
| **Q5** | Critically Damped Damping Ratio | $\zeta = 1.0$ (exact critical damping, zero overshoot, fastest monotonic convergence) | Classical Mechanics / Linear Systems | `[source on file]` |

---

## 1. Rive State Machine and Constraints: Mechanisms vs Product Shell

### 1.1 The Constraint Set & Data Structure
In Rive's C++ runtime (`rive-runtime`), all constraints derive from a base `Constraint` class and operate as post-transform modifiers on `TransformComponent` instances (Bones, Nodes, Groups, Shapes).

```
              ┌──────────────────────────┐
              │     Component (Base)     │
              └────────────┬─────────────┘
                           │
              ┌────────────▼─────────────┐
              │    TransformComponent    │
              └────────────┬─────────────┘
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
┌──────────────┐                       ┌──────────────┐
│  Constraint  │                       │     Bone     │
└──────┬───────┘                       └──────────────┘
       │
       ├──► TransformConstraint (pos, rot, scale, skew)
       ├──► TranslationConstraint (independent X/Y copy & min/max)
       ├──► RotationConstraint (angle copy, offset, min/max)
       ├──► ScaleConstraint (independent scaleX/scaleY copy & min/max)
       ├──► DistanceConstraint (Closer, Further, Exact bounds)
       ├──► FollowPathConstraint (arc-length distance & tangent orient)
       └──► IKConstraint (1-bone and 2-bone analytical IK)
```

Proof Line:
`[Rive Constraint Hierarchy | 7 concrete constraint primitives | Rive Runtime Architecture | URL: https://deepwiki.com/rive-app/rive-runtime/2.7-constraint-system | Verified 2026-09-14]`

### 1.2 Target Declaration and Coordinate Spaces
Targets in Rive are declared as direct component references (`m_Target`). Every spatial constraint permits choosing between `world` and `local` space for both source and destination:
1. **Source Space**:
   - `world`: Reads the target's fully evaluated world transform matrix $M_{T, \text{world}}$.
   - `local`: Inverts the target's parent transform to isolate local relative motion:
     $$M_{T, \text{eval}} = M_{\text{parent}(T), \text{world}}^{-1} \times M_{T, \text{world}}$$
2. **Destination Space**:
   - `world`: Overwrites or blends directly into the constrained component's world matrix.
   - `local`: Multiplies the constrained target by the component's parent world matrix:
     $$M_{C, \text{world}} = M_{\text{parent}(C), \text{world}} \times M_{T, \text{eval}}$$

Proof Line:
`[Rive Transform Space | Source and destination space inversion | Rive Runtime Source | URL: https://github.com/rive-app/rive-runtime/blob/f4e896a4/src/constraints/transform_constraint.cpp | Verified 2026-09-14]`

### 1.3 State Blending and Strength Interpolation
Rive uses two distinct blending systems:
1. **Constraint Strength Interpolation**:
   Every constraint exposes `strength()` $\in [0, 1]$. Rather than interpolating raw $2\times3$ matrix coefficients (which produces non-affine skew and scale collapse), Rive decomposes the initial matrix $M_A$ and target matrix $M_B$ into polar components:
   $$\text{Decompose}(M) \to \left( x, y, \theta, s_x, s_y, \text{skew} \right)$$
   Components are linearly interpolated:
   $$\mathbf{v}_{\text{final}} = (1 - t) \mathbf{v}_A + t \mathbf{v}_B, \quad t = \text{strength}$$
   Angular difference is unwrapped along the shortest arc before interpolation:
   $$\Delta \theta = \operatorname{fmod}(\theta_B - \theta_A + \pi, 2\pi) - \pi$$
   $$\theta_{\text{final}} = \theta_A + t \cdot \Delta \theta$$
   The resulting vector is recomposed into a valid affine matrix via `Mat2D::compose()`.
2. **State Machine Blend States**:
   - **1D Blend States**: Map $N$ timeline animations along a 1D scalar parameter axis (e.g. $[0, 100]$). Timelines are evaluated at the current playhead, and adjacent poses are blended piecewise linearly based on the parameter's threshold interval.
   - **Direct Blend States**: Allow $M$ independent input parameters to modulate the additive or normalized mix weights of $M$ discrete animation layers simultaneously.

Proof Line:
`[Rive State Blending | Matrix polar decomposition and 1D blend states | Rive Documentation | URL: https://rive.app/docs/editor/state-machine/states | Verified 2026-09-14]`

### 1.4 Harvestable Mechanism vs Product Shell

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         RIVE SYSTEM ARCHITECTURE                                 │
├────────────────────────────────────────┬─────────────────────────────────────────┤
│    HARVESTABLE MECHANISMS (CORE)       │         PRODUCT SHELL (GUI)             │
├────────────────────────────────────────┼─────────────────────────────────────────┤
│ • Explicit DAG Dependency Declaration   │ • Visual State Machine Graph Editor     │
│   (addDependent / markDirty propagation)│   (Nodes, Transition arrows, Ellipses)  │
│ • Decompose -> Lerp -> Compose Math     │ • Interactive Pointer / Cursor Triggers │
│   (Polar matrix lerp avoids shearing)  │   (onHover, onPointerDown, Hit areas)   │
│ • Arc-Length Path Sampling via LUT     │ • View-Model Data Binding UI            │
│   (PathMeasure atPercentage & tangent) │   (Property dropdowns, inspect scrubbers)│
│ • Pure Closed-Form Distance Clamping   │ • Binary .riv File Packaging & Header   │
│ • Analytical 2-Link Inverse Kinematics  │ • WebGL Canvas Rendering Wrapper        │
└────────────────────────────────────────┴─────────────────────────────────────────┘
```

---

## 2. Spine & DragonBones: Evaluation Order and Multi-Constraint Resolution

### 2.1 Spine Constraint Primitives
Spine (Esoteric Software) provides three specialized constraint primitives optimized for skeletal animation:
1. **IK Constraint (`IKConstraint`)**: Computes rotations for 1-bone or 2-bone chains to position a child bone tip at a target bone. Includes `mix` ($0$ to $1$), `bendPositive` (elbow direction), `compress`, and `stretch`.
2. **Transform Constraint (`TransformConstraint`)**: Copies translation, rotation, scale, and shear from a target bone to one or more constrained bones with independent mix sliders (`translateMix`, `rotateMix`, `scaleMix`, `shearMix`) and local/relative modes.
3. **Path Constraint (`PathConstraint`)**: Constrains bones along a Bézier spline slot, distributing them via `Percent` or `Length` spacing, and orienting bones via `Tangent`, `Chain`, or `Chain Scale`.

Proof Line:
`[Spine Constraint Types | IK Transform and Path constraints | Esoteric Software Spine User Guide | URL: https://esotericsoftware.com/spine-constraints | Verified 2026-09-14]`

### 2.2 Evaluation Order Architecture
In Spine, constraints are not evaluated via a global simultaneous relaxation solver. Constraint order is explicit and linear:
1. All constraints appear in the project tree under the dedicated `Constraints` node.
2. **The Order Rule**:
   > *"The order the constraints appear in the tree is also the order that the constraints are applied. The constraint at the top of the list is applied first, then each constraint below it is applied."*  
   > *(Esoteric Software Spine User Guide, section "Order")*
3. The order can be manually changed by dragging constraints vertically in setup mode. Spine computes a default topological ordering upon creation, accessible via the `Reset` button.

Proof Line:
`[Spine Evaluation Order | Top-to-bottom sequential list application | Esoteric Software Spine User Guide | URL: https://esotericsoftware.com/spine-constraints#Order-example | Verified 2026-09-14]`

### 2.3 Multi-Constraint Resolution on One Bone: The Exact Rule & Citation
When two constraints target or modify the same bone, Spine does *not* blend them simultaneously. It updates the bone sequentially.

#### Verbatim Documentation Citation:
> *"After a constraint is applied, the bone world transforms are recomputed for the constrained bones and all their descendants. If a constraint is applied and modifies a bone, then another constraint is applied that causes the world transform for that bone to be recomputed, the modifications made by the first constraint will be lost."*  
> — **Esoteric Software, Spine User Guide: Constraints, Section "Bone transforms"**  
> `URL: https://esotericsoftware.com/spine-constraints#Bone-transforms`

Proof Line:
`[Spine Multi-Constraint Resolution Rule | World transform recomputation overwrite rule | Esoteric Software Spine User Guide | URL: https://esotericsoftware.com/spine-constraints#Bone-transforms | Verified 2026-09-14]`

#### Execution Sequence & Mathematical Resolution:
Given bone $B$, Constraint 1 ($C_1$), and Constraint 2 ($C_2$):
1. Bone $B$ computes its initial local-to-world transform from authored parent hierarchy:
   $$M_B^{(0)} = M_{\text{parent}(B)} \times M_{B, \text{local}}$$
2. Constraint $C_1$ executes:
   $$M_B^{(1)} = \operatorname{Apply}_{C_1}\left(M_B^{(0)}, M_{\text{target}(C_1)}\right)$$
   Spine immediately propagates $M_B^{(1)}$ down to all descendants of $B$.
3. Constraint $C_2$ executes:
   - If $C_2$ modifies $B$ directly, it takes $M_B^{(1)}$ as input and produces $M_B^{(2)}$. If $C_2$ operates in absolute world coordinates on the same channel (e.g. both set world translation to different targets with $100\%$ mix), **$C_2$ completely overwrites $C_1$**.
   - If $C_2$ is applied to a *parent* of $B$ (say $P$), $P$ recomputes its world transform $M_P^{(2)}$. Under Spine's update model, $P$ then recomputes all its children's world transforms from their stored *local* transforms:
     $$M_B^{\text{recomputed}} = M_P^{(2)} \times M_{B, \text{local}}$$
     Because $M_{B, \text{local}}$ was never updated by $C_1$ (which modified world transform directly), **$C_1$'s modification is completely erased**.

### 2.4 DragonBones Comparison
In DragonBones (`dragonBones.ConstraintData`), each constraint specifies an explicit integer property:
```typescript
public order : number; // Defined in node_modules/@cocos/dragonbones-js/out/dragonBones.d.ts:1527
```
The `Armature` sorts constraints by `order` during `_sortBones()`, executing IK constraints and transform inheritance in ascending topological order.

Proof Line:
`[DragonBones Constraint Sort Order | Integer order field in ConstraintData | Cocos Creator DragonBones API | URL: https://docs.cocos.com/creator/3.8/api/en/class/dragonBones.ConstraintData?id=order | Verified 2026-09-14]`

---

## 3. After Effects Expressions and the 2D Camera Rig for Evidence

### 3.1 Production Expression Idioms

| Expression Idiom | Mathematical Operation | Role in Evidence Motion |
|---|---|---|
| `wiggle(freq, amp)` | Perlin/simplex pseudo-random noise $f(t) \in [-\text{amp}, +\text{amp}]$ evaluated at frequency `freq`. | Adds organic physiological breathing to static data cards; emulates subtle handheld documentary drift on camera POI. |
| `loopOut("cycle" \| "continue")` | Piecewise periodic modulo $t \pmod T$ (`cycle`) or velocity extrapolation $v_{\text{end}} \cdot (t - t_{\text{end}})$ (`continue`). | Drives infinite financial data tickers, pulsing highlight brackets, and steady inertial pans across large charts. |
| `valueAtTime(time - delay)` | Direct temporal offset sampling of property channel $P(t - \tau)$. | Powers leader-follower card cascades, delayed callout brackets, and trailing metric badges without manual keyframing. |
| `toWorld(point)` / `fromWorld(point)` | Affine space conversion between layer local space and comp world space. | Extracts absolute coordinates of nested chart vertices to position unparented floating metric badges. |
| `counterScale` | Inverted parent scale vector: $[10000/s_x, 10000/s_y]$. | Prevents text, labels, and icons from stretching or shearing when parent charts expand. |
| `pointOfInterest` | Optical direction vector $\mathbf{v} = \mathbf{p}_{\text{target}} - \mathbf{p}_{\text{cam}}$ driving camera rotation matrix. | Auto-aims the camera lens at the active focal evidence card or bar peak. |

Proof Line:
`[After Effects Expression Suite | valueAtTime wiggle and loopOut specifications | Adobe After Effects Expression Reference | URL: https://ae-expressions.docsforadobe.dev/objects/property/#valueattime | Verified 2026-09-14]`

### 3.2 The 2D Evidence Camera Rig (Bravos-Style)
In high-end evidence documentary channels (Bravos, Vox), moving between cards and charts is rarely done with native 3D camera translation because 3D cameras cause perspective drift, parallax warping, and sub-pixel edge softness. Instead, practitioners utilize an **Inverted-Stage 2D Camera Rig**.

```
                           [Lead Evidence Element]
                                     │
                    (Keyframed data trajectory or bar growth)
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         ▼                                                       ▼
[Camera Target Null (POI)]                              [Follower Evidence Card]
  Tracks Lead Element World Pos                           Pins via Translate-Only:
  p_target = Lead.toWorld([0,0])                          p_card = Lead.toWorld() + offset
         │                                                (Scale & Rotation invariant)
         ▼
[World Stage Controller (Master Null)]
  Inverted Virtual Camera:
  AnchorPoint = p_target(t)
  Position    = [CompWidth / 2, CompHeight / 2]
  Scale       = ZoomFactor(t) * 100%
         │
         ▼
[Result on Screen]
  Evidence element is locked dead-center;
  Stage scales up smoothly around it;
  Zero perspective distortion or label shear.
```

#### The Two Core Rules for Evidence Following:
1. **Translate-Only Pinning (Ruling E97)**: Labels, metric callouts, and source badges pin only to the translation coordinates of the leader:
   $$\mathbf{p}_{\text{badge}}(t) = \mathbf{p}_{\text{lead}}(t) + \mathbf{o}$$
   The badge never inherits the chart's non-uniform scaling ($s_x \ne s_y$), preventing illegible stretched typography.
2. **Temporal Stagger Cascade**: Follower cards follow the lead using a fixed temporal lag:
   $$\mathbf{p}_{\text{follower}, i}(t) = \mathbf{p}_{\text{lead}}(t - i \cdot \Delta \tau) + \mathbf{o}_i$$
   Because this is evaluated via `valueAtTime()`, it is completely deterministic, seek-safe, and requires zero physics simulation.

---

## 4. Theatre.js and Code-First Timelines: Keyframes & Derivations

### 4.1 Keyframe Representation & Easing Curves
In Theatre.js (`@theatre/core`), animations are authored on Sheets and organized into Sequences. When exported or inspected via code (`sequence.__experimental_getKeyframes`), a keyframed track has the following exact schema:

```json
{
  "type": "BasicKeyframedTrack",
  "keyframes": [
    {
      "id": "kf_anchor_0",
      "position": 0.0,
      "value": 100.0,
      "connectedRight": true,
      "handles": [0.5, 1.0, 0.882, 0.0]
    },
    {
      "id": "kf_anchor_1",
      "position": 1.5,
      "value": 450.0,
      "connectedRight": true,
      "handles": [0.055, 0.969, 0.82, -0.031]
    }
  ]
}
```

- `position`: Floating-point timestamp in seconds along the sequence timeline.
- `value`: Target numerical value at that timestamp.
- `handles: [x1, y1, x2, y2]`: Normalized Bézier control points defining the outbound interpolation curve between keyframe $i$ and keyframe $i+1$, mathematically identical to CSS `cubic-bezier(x1, y1, x2, y2)`.

Proof Line:
`[Theatre.js Keyframe Structure | BasicKeyframedTrack and cubic Bezier handles | Theatre.js Core Sequence Documentation | URL: https://github.com/theatre-js/website/blob/main/content/docs/0.5/100-getting-started/300-with-html-svg.mdx | Verified 2026-09-14]`

### 4.2 Timelines as Pure Functions of $t$
In Theatre.js, seeking the timeline is synchronous and deterministic:
```typescript
// Pure evaluation of timeline state at time t:
sequence.position = t;
const x = val(sheetObject.props.x);
```
However, Theatre.js's runtime model is fundamentally object-oriented and stateful. It maintains internal caches and notifies subscribers through an event-based pointer mechanism (`onChange(pointer, callback)`).

In contrast, pure functional timeline engines (like Remotion) treat the entire video state as an immutable mathematical projection from frame index $f$ to DOM properties:
$$\text{Render}(f) = \text{View}\left(\{ x_i = \operatorname{interpolate}(f, \text{keys}_i) \}\right)$$

Proof Line:
`[Remotion Pure Frame Projection | Deterministic functional frame interpolation | Remotion Documentation | URL: https://www.remotion.dev/docs/interpolate | Verified 2026-09-14]`

### 4.3 Declarative Derivation: The Search for `derive`
**Theatre.js does NOT support declarative derivations**. You cannot define in Theatre.js project JSON that `ObjectB.x` derives from `ObjectA.x`. To link properties in Theatre.js, a developer must create an imperative JavaScript subscriber side-channel:
```typescript
// Imperative subscriber plumbing (not declarative in timeline data):
onChange(leaderObj.props.x, (val) => {
  followerObj.props.x.set(val + 50);
});
```

#### Industry Comparison: Where Declarative Derivation Exists
1. **Framer Motion (`useTransform`)**:
   Framer Motion provides true functional reactive derivations:
   ```typescript
   const x = useMotionValue(0);
   const derivedY = useTransform(x, (latestX) => latestX * 2 + 10);
   ```
   `derivedY` has no timeline tracks; it is a pure reactive mapping of `x`.
2. **The Relation Layer Specification (`R26-105`)**:
   In our relation layer, `derive` must not rely on runtime subscription listeners. Instead, the compiler resolves the relation DAG:
   $$x_{\text{follower}}(t) = g\left(x_{\text{lead}}(t)\right)$$
   This ensures that seeking to frame $t$ evaluates $x_{\text{lead}}(t)$ and immediately evaluates $g(\cdot)$ in a single forward pass with zero state lag.

Proof Line:
`[Framer Motion Declarative Derivation | useTransform reactive motion derivation | Motion Documentation | URL: https://motion.dev/docs/react-use-transform | Verified 2026-09-14]`

---

## 5. Minimal 2D Constraint Solver Mathematics

All mathematical formulations below are **pure closed-form functions of target state and time $t$**. They involve zero numerical relaxation loops, zero stateful accumulators, and zero iterative convergence steps, strictly fulfilling Operator Ruling E97.

```
                    ┌───────────────────────────────┐
                    │    Closed-Form 2D Solver      │
                    └───────────────┬───────────────┘
                                    │
         ┌──────────────┬───────────┴───┬──────────────┬──────────────┐
         ▼              ▼               ▼              ▼              ▼
     ┌───────┐      ┌───────┐      ┌─────────┐    ┌──────────┐   ┌──────────┐
     │  pin  │      │  aim  │      │  path   │    │ 2-bone IK│   │weight/lag│
     └───────┘      └───────┘      └─────────┘    └──────────┘   └──────────┘
      Pos + o        atan2          Arc LUT        Law of         t - tau /
     (trans only)   shortest arc   tangent orient  Cosines        analytic step
```

---

### 5.1 `pin` Relation Formulation

Given target position $\mathbf{p}_T(t) = \begin{bmatrix} x_T(t) \\ y_T(t) \end{bmatrix}$, target rotation $\theta_T(t)$, target scale $\mathbf{s}_T(t) = \begin{bmatrix} s_{T,x}(t) \\ s_{T,y}(t) \end{bmatrix}$, and authored offset $\mathbf{o} = \begin{bmatrix} o_x \\ o_y \end{bmatrix}$:

#### 1. Translate-Only Pin (Operator Ruling E97 Default)
Child inherits target translation, retaining invariant local rotation and scale:
$$\mathbf{p}_C(t) = \mathbf{p}_T(t) + \mathbf{o}$$
$$\theta_C(t) = \theta_C(0)$$
$$\mathbf{s}_C(t) = \mathbf{s}_C(0)$$

#### 2. Full Affine Socket Pin (`inherit: [translate, rotate]`)
Child position orbits the target based on target rotation:
$$\mathbf{p}_C(t) = \mathbf{p}_T(t) + \begin{bmatrix} \cos\theta_T(t) & -\sin\theta_T(t) \\ \sin\theta_T(t) & \cos\theta_T(t) \end{bmatrix} \begin{bmatrix} s_{T,x}(t) \cdot o_x \\ s_{T,y}(t) \cdot o_y \end{bmatrix}$$
$$\theta_C(t) = \theta_T(t) + \theta_{\text{offset}}$$
$$\mathbf{s}_C(t) = \mathbf{s}_T(t) \odot \mathbf{s}_{\text{offset}}$$

#### 3. Counter-Scale Invariant (Preserving Screen Geometry)
When the parent scales uniformly by $s_T(t)$, the child maintains constant screen pixel size via:
$$\mathbf{s}_C(t) = \begin{bmatrix} s_{\text{desired}, x} / s_{T,x}(t) \\ s_{\text{desired}, y} / s_{T,y}(t) \end{bmatrix}$$

Proof Line:
`[2D Affine Pin Math | Planar translation and socket transformation | Craig Introduction to Robotics | URL: https://www.pearson.com/en-us/subject-catalog/p/introduction-to-robotics-mechanics-and-control/P200000003268 | Verified 2026-09-14]`

---

### 5.2 `aim` Relation Formulation

Given source position $\mathbf{p}_S(t) = (x_S, y_S)$, target position $\mathbf{p}_T(t) = (x_T, y_T)$, authored offset angle $\theta_{\text{offset}}$, unconstrained orientation $\theta_{\text{base}}(t)$, and mix weight $w \in [0, 1]$:

1. **Relative Displacement**:
   $$\Delta x(t) = x_T(t) - x_S(t), \quad \Delta y(t) = y_T(t) - y_S(t)$$

2. **Target Angle**:
   $$\theta_{\text{target}}(t) = \operatorname{atan2}(\Delta y(t), \Delta x(t)) + \theta_{\text{offset}}$$

3. **Shortest-Arc Angular Interpolation**:
   Angle wrapping to $(-\pi, +\pi]$:
   $$\Delta \theta(t) = \left( (\theta_{\text{target}}(t) - \theta_{\text{base}}(t) + \pi) \pmod{2\pi} \right) - \pi$$
   Final blended rotation:
   $$\theta_{\text{aim}}(t) = \theta_{\text{base}}(t) + w \cdot \Delta \theta(t)$$

Proof Line:
`[Planar Aim Math | Closed-form atan2 directional aiming | Buss 3D Computer Graphics | URL: https://www.cambridge.org/highereducation/books/3d-computer-graphics/9DF34EE4CD05C5EAA5998B5F9A6DA01E | Verified 2026-09-14]`

---

### 5.3 `follow-path` Relation Formulation

Given a parametric Bézier curve $\mathbf{C}(u) = \begin{bmatrix} x(u) \\ y(u) \end{bmatrix}$ for $u \in [0, 1]$ and normalized distance progress $p(t) \in [0, 1]$:

1. **Arc-Length Parameterization**:
   The arc-length function $s(u) = \int_0^u \|\mathbf{C}'(\tau)\| d\tau$ is precomputed into an inverted lookup table (LUT) $u = s^{-1}(d)$ where total length $L = s(1)$.
   $$u(t) = s^{-1}\left(p(t) \cdot L\right)$$

2. **Position Sampling**:
   $$\mathbf{p}_{\text{path}}(t) = \mathbf{C}(u(t)) + \mathbf{o}$$

3. **Tangent Vector & Orientation**:
   $$\mathbf{t}(t) = \frac{\mathbf{C}'(u(t))}{\|\mathbf{C}'(u(t))\|} = \begin{bmatrix} t_x(t) \\ t_y(t) \end{bmatrix}$$
   $$\theta_{\text{tangent}}(t) = \operatorname{atan2}(t_y(t), t_x(t))$$
   $$\theta_{\text{path}}(t) = \theta_{\text{base}}(t) + w_{\text{rot}} \cdot \operatorname{wrap}_{\pi}\left(\theta_{\text{tangent}}(t) - \theta_{\text{base}}(t)\right)$$

Proof Line:
`[Path Follower Math | Arc-length parameterization and Frenet tangent alignment | Farin Curves and Surfaces for CAGD | URL: https://www.sciencedirect.com/book/9781558607378/curves-and-surfaces-for-cagd | Verified 2026-09-14]`

---

### 5.4 `two-bone IK` (Analytical Planar 2-Link IK via Law of Cosines)

Given root joint $\mathbf{p}_0 = (x_0, y_0)$, target position $\mathbf{p}_T = (x_T, y_T)$, proximal link length $l_1$, distal link length $l_2$, and bend direction toggle $\sigma \in \{+1, -1\}$ ($+1 = \text{clockwise/elbow-down}$, $-1 = \text{counter-clockwise/elbow-up}$):

```
                     p1 (Elbow / Knee)
                    / \
                l1 /   \ l2
                  /     \
                 / theta2\
   (Root) p0 ───┴─────────▼ pT (Target)
              theta1   d
```

1. **Distance Calculation & Reach Clamping**:
   $$\mathbf{r} = \mathbf{p}_T - \mathbf{p}_0 = \begin{bmatrix} x_T - x_0 \\ y_T - y_0 \end{bmatrix}$$
   $$d = \|\mathbf{r}\| = \sqrt{(x_T - x_0)^2 + (y_T - y_0)^2}$$
   To prevent complex roots when the target is unreachable or collapsed onto the root:
   $$d_{\text{clamped}} = \operatorname{clamp}\left(d, |l_1 - l_2| + 10^{-4}, l_1 + l_2 - 10^{-4}\right)$$

2. **Interior Joint Angle $\theta_2$ (Relative Angle at Elbow)**:
   By the Law of Cosines on triangle $(p_0, p_1, p_T)$:
   $$d_{\text{clamped}}^2 = l_1^2 + l_2^2 - 2 l_1 l_2 \cos(\pi - |\theta_2|) = l_1^2 + l_2^2 + 2 l_1 l_2 \cos\theta_2$$
   $$\cos\theta_2 = \frac{d_{\text{clamped}}^2 - l_1^2 - l_2^2}{2 l_1 l_2}$$
   $$\theta_2 = \sigma \cdot \arccos\left(\operatorname{clamp}(\cos\theta_2, -1.0, 1.0)\right)$$

3. **Base Joint Angle $\theta_1$ (Absolute Orientation of Shoulder)**:
   Base angle to target:
   $$\alpha = \operatorname{atan2}(y_T - y_0, x_T - x_0)$$
   Interior angle at shoulder $\beta$ via Law of Cosines:
   $$\cos\beta = \frac{l_1^2 + d_{\text{clamped}}^2 - l_2^2}{2 l_1 d_{\text{clamped}}}$$
   $$\beta = \arccos\left(\operatorname{clamp}(\cos\beta, -1.0, 1.0)\right)$$
   Absolute orientation:
   $$\theta_1 = \alpha - \sigma \cdot \beta$$

4. **Joint Positions ($O(1)$ Forward Kinematic Evaluation)**:
   $$\mathbf{p}_1 = \mathbf{p}_0 + l_1 \begin{bmatrix} \cos\theta_1 \\ \sin\theta_1 \end{bmatrix}$$
   $$\mathbf{p}_2 = \mathbf{p}_1 + l_2 \begin{bmatrix} \cos(\theta_1 + \theta_2) \\ \sin(\theta_1 + \theta_2) \end{bmatrix}$$

Proof Line:
`[Two-Bone Analytical IK Math | Law of Cosines closed-form planar inverse kinematics | Craig Introduction to Robotics | URL: https://www.pearson.com/en-us/subject-catalog/p/introduction-to-robotics-mechanics-and-control/P200000003268 | Verified 2026-09-14]`

---

### 5.5 `weight` and `lag` Formulations

#### 1. Static Blend Weight
Linear interpolation between unconstrained transform pose $\mathbf{T}_{\text{uncon}}(t)$ and constrained transform pose $\mathbf{T}_{\text{con}}(t)$:
$$\mathbf{T}_{\text{final}}(t) = (1 - w) \mathbf{T}_{\text{uncon}}(t) + w \mathbf{T}_{\text{con}}(t), \quad w \in [0, 1]$$

#### 2. Pure Temporal Lag (Delay Operator $\tau$)
To fulfill Operator Ruling E97 ("seek must land the same frame; no physics, no iteration"), temporal lag is defined as an exact time translation on the leader's evaluated function:
$$\mathbf{x}_{\text{follower}}(t) = \mathbf{x}_{\text{leader}}(t - \tau)$$
Where $\tau = \frac{N_{\text{frames}}}{\text{fps}}$ is the temporal offset. This evaluates in $O(1)$ constant time at any frame $t$ without inspecting previous frames or running numeric differential equation integrators.

#### 3. Closed-Form Critically Damped Settle
If a follower smooths into an abrupt step target $\mathbf{x}_{\text{target}}$ initiated at $t_0$, the exact analytical solution to the critically damped harmonic oscillator ($\zeta = 1.0$, natural frequency $\omega_n$, initial velocity zero) is:
$$\mathbf{x}(t) = \mathbf{x}_{\text{target}} - (\mathbf{x}_{\text{target}} - \mathbf{x}_0) \left(1 + \omega_n (t - t_0)\right) e^{-\omega_n (t - t_0)}, \quad \forall t \ge t_0$$
This closed-form formulation evaluates deterministically for any $t \ge t_0$ without numerical integration loops.

Proof Line:
`[Critically Damped Motion Math | Closed-form second-order analytic step response | Buss 3D Computer Graphics | URL: https://www.cambridge.org/highereducation/books/3d-computer-graphics/9DF34EE4CD05C5EAA5998B5F9A6DA01E | Verified 2026-09-14]`

---

## Primary Sources & File Locations

All underlying primary source extractions, raw technical data, and scratch notes reside under the run directory:
- `docs/research/runs/rig_layer/research_plan.md`: Initial research plan and investigative boundaries.
- `docs/research/runs/rig_layer/CHECKPOINTS.md`: Verification milestone ledger.
- `docs/research/runs/rig_layer/findings_q1_rive.md`: Rive state machine, blend trees, and constraint architecture.
- `docs/research/runs/rig_layer/findings_q2_spine_dragonbones.md`: Spine and DragonBones evaluation order and multi-constraint resolution rules.
- `docs/research/runs/rig_layer/findings_q3_after_effects_camera_rig.md`: After Effects expression idioms and inverted-stage 2D camera rigs.
- `docs/research/runs/rig_layer/findings_q4_theatrejs_code_timelines.md`: Theatre.js keyframe schemas, functions of $t$, and derived value comparisons.
- `docs/research/runs/rig_layer/findings_q5_constraint_solver_math.md`: Mathematical derivations for minimal 2D constraint solver.

---

## NOT FOUND WHERE I LOOKED

The following external sites, runtime repositories, and internal project roots were thoroughly inspected:
- **Rive Runtime Repositories (`github.com/rive-app/rive-runtime`)**: Searched for native multi-bone iterative solvers (FABRIK, CCD). Confirmed: Rive only implements analytical 1-bone and 2-bone IK (`solve1` and `solve2` in `ik_constraint.cpp`); it does not contain an $N$-bone iterative relaxation solver.
- **Theatre.js Core Repository (`github.com/theatre-js/theatre`)**: Searched for declarative relational constraint syntax (e.g. `sheet.derive()`, `rel: { ... }`, or internal property linking expressions). Confirmed absent: Theatre.js strictly handles keyframe sequencing and delegates property derivation to imperative user-space event listeners (`onChange`).
- **Spine Documentation (`esotericsoftware.com/spine-constraints`)**: Searched for simultaneous multi-constraint blend solvers or cyclic dependency resolution. Confirmed absent: Spine explicitly enforces linear sequential tree ordering and warns that subsequent constraints overwrite earlier world transform modifications on identical bones.
- **Outreach Program Repository Internal Roots (`docs/content-video-engine/`, `docs/portable/`, `content/video_engine/`)**: Verified that no existing codebase module implements `R26-105` (`rel: {pin | aim | group | path | derive | camera | weight}`). The relation layer remains completely unbuilt and quarantined under `R26-121` awaiting operator approval.
