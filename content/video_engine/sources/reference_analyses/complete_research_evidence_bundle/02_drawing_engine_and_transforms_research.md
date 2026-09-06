# Deep Research Report: Drawing Engines, Animation Mechanics, Object Management, and Transform Architectures for Faceless Video Production

*Generated: 2026-09-04 | Status: Authoritative Technical Architecture | Scope: Video Engine Rendering & Compositing*

---

## Executive Summary

State-of-the-art programmatic video generation systems (such as *Remotion*, *Motion Canvas*, *Figma Motion*, and *Rive*) achieve institutional polish not by generating monolithic raster frames, but by decoupling rendering into a **deterministic 2.5D Scene Graph**. In high-performing financial channels like *Wealth Logic*, every frame is a composite of three decoupled layers: a quiet ground, a persistent rigged host character, and an active vector evidence layer (interactive balance scales, live data charts, dynamic counters, and physicalized metaphor props).

This research investigates the mathematical and architectural foundations of 2D/2.5D drawing engines, frame-deterministic animation clocks, hierarchical object management, and character slot-rigging. We translate these foundational graphics principles into concrete, production-ready improvements for our **Outreach Video Engine** (`content/video_engine`, Doc 24, Doc 29, Remotion/HyperFrames), replacing ad-hoc CSS positioning and static image cuts with an affine matrix hierarchy, closed-form analytic spring physics, and slot-swapped vector cutout rigs.

---

## Architecture Diagram & The 4 Core Mechanical Pillars

```
                     ┌───────────────────────────────────────────────┐
                     │          DETERMINISTIC VIDEO CLOCK            │
                     │         Frame f ──> Time t = f / fps          │
                     └───────────────────────┬───────────────────────┘
                                             │
               ┌─────────────────────────────┴─────────────────────────────┐
               ▼                                                           ▼
┌──────────────────────────────┐                            ┌──────────────────────────────┐
│  RETAINED 2.5D SCENE GRAPH   │                            │    CLOSED-FORM DYNAMICS      │
│  M_world = M_parent x M_node │                            │  x(t) = 1 - e^(-ζωt)(cos...) │
│  Z0: Ground / Baseline       │                            │  • O(1) Seek-Safe Evaluation │
│  Z1: Env / Wall Props        │                            │  • Stamp Impacts & Bounces   │
│  Z2: Interactive Evidence    │                            │  • Dynamic Balance Tilts     │
│  Z3: Persistent Host Rig     │                            │  • Live Metric Counters      │
│  Z4: Kinetic Overlays        │                            └──────────────────────────────┘
│  Z5: Floating Captions       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   SLOT-SWAP CUTOUT RIGGING   │
│   Torso + Head + Hand Slots  │
│   • 0% Character Drift       │
│   • Forward Kinematics (FK)  │
│   • Programmatic Tag Triggers│
└──────────────────────────────┘
```

### Pillar 1: The Coordinate Transform Pipeline & Anchor Normalization
- Elements live in local coordinate space and transform to screen space via affine matrix multiplication: $\mathbf{p}_{screen} = \mathbf{M}_{camera} \times \mathbf{M}_{world} \times \mathbf{p}_{local}$.
- Transformations around an arbitrary pivot point $\mathbf{A} = (a_x, a_y)$ must be normalized: $\mathbf{M}_{local} = \mathbf{T}(a_x, a_y) \times \mathbf{R}(\theta) \times \mathbf{S}(s_x, s_y) \times \mathbf{T}(-a_x, -a_y)$.
- Without this sandwich, scaling causes diagonal drift and rotating limbs disconnects joints.

### Pillar 2: Deterministic Clocking & Closed-Form Spring Physics
- Video renderers do not run at real-time speeds; iterative physics loops (Euler/Verlet) or wall-clock timers (`Date.now()`, CSS transitions) cause jitter and scrub lag.
- State at frame $f$ is a pure mathematical function $\text{Render}(f) = \mathcal{F}(f, \frac{f}{\text{fps}})$.
- Dynamics (stamps slamming down, scales tipping) evaluate the closed-form damped harmonic oscillator in $O(1)$ time:
  $$x(t) = 1 - e^{-\zeta \omega_n t} \left( \cos(\omega_d t) + \frac{\zeta \omega_n}{\omega_d} \sin(\omega_d t) \right)$$

### Pillar 3: Retained 2.5D Scene Graph & Dirty Flags
- Scene objects are managed in a parent-child hierarchy with dirty flag propagation (avoiding redundant matrix multiplications).
- Stacking follows 6 strict layers ($Z_0$ ground to $Z_5$ captions) with subtle camera parallax to create high-end visual depth without 3D bloat.

### Pillar 4: Modular Vector Cutout Rigging (The Host Solution)
- Skeletal mesh deformation produces rubbery distortions; generating full-body images per frame causes severe AI face/style drift.
- The institutional standard is a vector cutout rig with discrete sprite slots (`HeadSlot`, `HandSlot`, `TorsoSlot`) driven by Forward Kinematics (FK) and storyboard tags.
- With 1 torso, 3 heads, and 6 hands, the host executes 18 distinct presenter actions using just 10 transparent SVG files.

---

## 5 Actionable Upgrades for Our Pipeline

| Area | Current Approach | Target Upgrade (From Research) | Impact |
|---|---|---|---|
| **Transform Engine** | Ad-hoc CSS `left/top` & `translate(-50%, -50%)` | Structured `SceneNode.ts` with explicit anchor normalization (`anchorX`, `anchorY`) and matrix3d output | Eliminates diagonal drifting during scale/rotations |
| **Motion Physics** | Static keyframes or CSS eases | `useAnalyticSpring.ts` closed-form harmonic oscillator ($O(1)$ seekable) | Realistic stamp slams, scale tipping, and bounce dynamics with zero simulation lag |
| **Host Presenter** | Full-body static images per scene | `HostCutoutRig.tsx` with swappable `HeadSlot` and `HandSlot` SVGs | 100% identity lock across 16 minutes; programmatic emotion triggers |
| **Interactive Evidence** | Static image docks | Parameterized `DynamicBalanceScale.tsx` (rotating beam + counter-rotating pans) | Visualizes "The Spread" equation dynamically as live numbers change |
| **Audio-Visual Sync** | Arbitrary scene cuts | Automatic snapping to Whisper breath pauses ($\Delta t \ge 0.45\text{s}$) in `storyboard_generator.py` | Eliminates visual-speech collisions; plates settle before words land |

---

## 1. Mechanics of 2D/2.5D Drawing Engines

### 1.1 Immediate Mode vs. Retained Mode
Drawing architectures fall into two paradigms:
1. **Immediate Mode (Canvas 2D / WebGL / Skia):**
   - The engine does not maintain a persistent object model. On every tick or frame request, the application issues direct draw commands (`ctx.beginPath()`, `ctx.arc()`, `ctx.fill()`).
   - *Advantages:* High throughput for millions of particles; minimal memory footprint.
   - *Failure Mode for Video:* Impossible to declaratively track object lifecycles, hit-test, or perform structural transitions without manually recalculating every frame's draw calls in application code.
2. **Retained Mode (DOM / SVG / Scene Graphs / Motion Canvas / Remotion):**
   - The engine maintains an in-memory tree of nodes (a Scene Graph). Each node encapsulates properties (position, scale, rotation, opacity, stroke, children).
   - The drawing engine traverses the tree, evaluates visibility and transforms, and emits a flattened **Display List** to the GPU rasterizer.
   - *Why Video Engines Require Retained Mode:* Video creation requires programmatic control over layout, layer re-ordering, path morphing, and declarative tweening across time. Retained scene graphs allow declarative queries like `actor.hand.rotateTo(45)` without redrawing the entire screen manually.

### 1.2 The Coordinate Transform Pipeline
Every visual element lives in a cascade of coordinate spaces. The drawing engine transforms a local vector point $\mathbf{p}_{local} = \begin{bmatrix} x & y & 1 \end{bmatrix}^T$ into viewport screen coordinates $\mathbf{p}_{screen}$ via homogeneous matrix multiplication:

$$\mathbf{p}_{screen} = \mathbf{M}_{camera} \times \mathbf{M}_{world} \times \mathbf{p}_{local}$$

#### The 2D Affine Transformation Matrix (Homogeneous $3 \times 3$)
In 2D space, translation, rotation, scale, and shear are unified into a single $3 \times 3$ matrix:

$$\mathbf{M} = \begin{bmatrix} a & c & e \\ b & d & f \\ 0 & 0 & 1 \end{bmatrix} = \begin{bmatrix} s_x \cos\theta - k_y \sin\theta & -s_y \sin\theta + k_x \cos\theta & t_x \\ s_x \sin\theta + k_y \cos\theta & s_y \cos\theta + k_x \sin\theta & t_y \\ 0 & 0 & 1 \end{bmatrix}$$

- $a, d$: Scale factors along X and Y ($s_x, s_y$).
- $b, c$: Rotation ($\theta$) and skew/shear ($k_x, k_y$).
- $e, f$: Translation along X and Y ($t_x, t_y$).

#### The Transform Origin / Anchor Point Problem
The single most common defect in amateur CSS/web animations is improper rotation or scaling around an incorrect pivot. In graphics mathematics, transformation around an arbitrary anchor point $\mathbf{A} = (a_x, a_y)$ requires sandwiching the affine operation between negative and positive translations:

$$\mathbf{M}_{local} = \mathbf{T}(a_x, a_y) \times \mathbf{R}(\theta) \times \mathbf{S}(s_x, s_y) \times \mathbf{T}(-a_x, -a_y)$$

Without explicit anchor normalization, scaling a balance scale causes it to translate diagonally, and rotating an arm disconnects the hand from the wrist.

---

## 2. Animation Mechanics & Deterministic Clocking

### 2.1 The Deadly Flaw of Wall-Clock Animations in Headless Video
In interactive web browsers, animations rely on `requestAnimationFrame(timestamp)` or `setInterval`. If the CPU stutters, $\Delta t$ spikes, skipping frames.

In headless video production (Puppeteer, Remotion, HyperFrames, ffmpeg):
- **Video is not real-time.** Frame 1,200 might take 450ms to render on disk, while Frame 1,201 takes 80ms.
- Any dependency on `performance.now()`, `Date.now()`, standard CSS transitions, or non-seekable delta-time tick loops results in **jitter, dropped frames, and audio de-sync**.
- **The Golden Rule of Programmatic Video:**
  $$\text{Render}(f) = \mathcal{F}\left(f, \frac{f}{\text{fps}}, \text{props}\right)$$
  The visual state of the entire universe at frame $f$ must be a **pure, deterministic mathematical function** of the frame index $f$.

### 2.2 Closed-Form Analytic Spring Physics (O(1) Seekable Dynamics)
Game engines simulate springs iteratively using Euler or Verlet integration ($\mathbf{v}_{t+1} = \mathbf{v}_t + \mathbf{a}\Delta t$). If a video renderer needs to preview frame 500, an iterative loop must simulate frames 0 through 499 sequentially, destroying scrub performance.

Modern video engines (pioneered by *Remotion* and *Motion Canvas*) solve this using the **analytic closed-form solution of the Damped Harmonic Oscillator**:

$$m \ddot{x} + c \dot{x} + k x = 0$$

Given mass $m$, damping $c$, stiffness $k$, the damping ratio $\zeta$ and natural frequency $\omega_n$ are:
$$\omega_n = \sqrt{\frac{k}{m}}, \quad \zeta = \frac{c}{2\sqrt{m k}}$$

For an underdamped spring ($\zeta < 1$), the exact position $x(t)$ at any arbitrary time $t \ge 0$ without iteration is:

$$x(t) = 1 - e^{-\zeta \omega_n t} \left( \cos(\omega_d t) + \frac{\zeta \omega_n}{\omega_d} \sin(\omega_d t) \right)$$

where $\omega_d = \omega_n \sqrt{1 - \zeta^2}$ is the damped angular frequency.

*Application in Outreach Engine:* When rubber stamps (`"NOT YET"`, `"LOOPHOLE"`) slam down or balance scales tip when coins drop, evaluating this closed-form equation at frame $f$ delivers instantaneous, bit-for-bit reproducible, realistic physical overshoot with zero simulation lag.

### 2.3 Vector Path Morphing Algorithms (Flubber & d3-interpolate-path)
Transitioning between two arbitrary vector shapes (e.g., morphing an arrow into a currency symbol, or transitioning a line graph between two quarterly datasets) fails with naive interpolation because:
1. Shape A and Shape B have different numbers of control vertices.
2. The winding order (clockwise vs. counterclockwise) or vertex starting index differs, causing the path to twist inside-out.

**State-of-the-Art Pipeline (Flubber / D3 algorithm):**
1. **Ring Normalization:** Decompose complex SVG paths into exterior rings and interior holes.
2. **Vertex Resampling:** Subdivide segments along path perimeters so both Shape A and Shape B contain an identical vertex count $N$ (equidistant sampling).
3. **Rotational Alignment (Minimum Distance Matching):** Rotate the index offset of Shape B to minimize the sum of squared Euclidean distances between corresponding vertices:
   $$\arg\min_{k} \sum_{i=0}^{N-1} \|\mathbf{v}_{A, i} - \mathbf{v}_{B, (i+k) \pmod N}\|^2$$
4. **Cubic Bezier Reconstruction:** Interpolate the aligned vertex loops linearly or via spring dynamics, converting back to SVG `d="M... C... Z"` strings per frame.

---

## 3. Object Management & 2.5D Scene Graphs

### 3.1 Hierarchical Scene Graph Structure
To manage complex explainers with dozens of interacting elements (analyst, scale, coins, text, background), objects must be organized in a tree:

```
Root Scene (1920x1080)
├── Camera2D (Pan, Push, Tilt, Shake)
├── GroundLayer (Layer 0: Off-white canvas, baseline shadow)
├── EnvironmentLayer (Layer 1: Chalkboard, factory poster, desk)
├── EvidenceGroup (Layer 2: Interactive Mechanism)
│   ├── BalanceScaleBase
│   │   ├── BeamNode (Rotates around Pivot Point)
│   │   │   ├── LeftPan (Counter-rotates to stay upright)
│   │   │   │   └── CoinStack (Children follow Pan position)
│   │   │   └── RightPan (Counter-rotates)
│   │   │       └── WeightProp
│   └── FormulaBoard (SVG Math Text + Highlighting)
├── CastLayer (Layer 3: Host Rig)
│   └── HostNode (Root positioned at Floor Baseline)
│       ├── BodyTorso
│       ├── HeadSlot (Expressive Head Asset)
│       └── RightArmHierarchy
│           ├── ShoulderJoint
│           └── ForearmHandSlot (Swappable: Point, Open, Grip)
└── OverlayLayer (Layer 4: Kinetic Floating Captions, Rubber Stamps)
```

### 3.2 Matrix Concatenation & The Dirty Flag Pattern
In a hierarchical tree, calculating world transforms on every frame for 100 static nodes is wasteful. Production engines implement the **Dirty Flag Pattern**:
1. Each node maintains `localMatrix`, `worldMatrix`, and a boolean `isDirty`.
2. When a property changes (e.g., `beamNode.rotation = 15°`), `isDirty = true` is set on that node and propagated recursively down to all its descendants.
3. During the render pass, if `isDirty == true`:
   $$\mathbf{M}_{world}^{(\text{child})} = \mathbf{M}_{world}^{(\text{parent})} \times \mathbf{M}_{local}^{(\text{child})}$$
   `isDirty` is then cleared. Nodes whose ancestors did not move reuse their cached `worldMatrix`.

### 3.3 2.5D Perspective Projection & Z-Stacking
While our videos are 2D explainers, viewers perceive high production value through **2.5D parallax and depth cues**:
- **Layer Stacking (Painter's Algorithm):** Strictly enforce rendering order from back to front ($Z_0 \to Z_5$) to prevent transparent assets from clipping incorrectly.
- **Isometric / Perspective Camera Model:**
  $$X_{proj} = \frac{X \cdot f}{Z + d} + C_x, \quad Y_{proj} = \frac{Y \cdot f}{Z + d} + C_y$$
  By assigning a slight depth $Z$ to background props ($Z=200$) vs. the evidence dock ($Z=50$) vs. the host ($Z=0$), a subtle camera pan (`Camera.x += sin(t) * 10`) creates cinematic parallax without requiring full 3D rendering.

---

## 4. Character Rigging & Vector Cutout Systems

### 4.1 Why Skeletal Mesh Deformation is Wrong for Faceless Finance
In 3D games, characters use skinned meshes with bone vertex weights. In 2D editorial finance videos (like *Wealth Logic*), skeletal mesh deformation produces an uncanny, rubbery look that erodes viewer trust.

### 4.2 The Winning Standard: Vector Cutout + Slot-Swapping
The institutional standard (used in *South Park*, *Vyond*, *Moho*, and *Wealth Logic*) is **Modular Vector Cutout Rigging**:
- **Rig Structure:** Rigid vector parts connected by rotational pivots (Forward Kinematics).
- **Slot Swapping:** Rather than animating fingers individually, limbs terminate in discrete, professionally drawn **Sprite Slots**:
  - `HandSlot` $\in$ `['point_up', 'point_side', 'open_presenting', 'grip_tool', 'flat_desk', 'stop_palm']`
  - `HeadSlot` $\in$ `['neutral_talk', 'explaining_smile', 'skeptical_frown', 'focused_down']`
  - `TorsoSlot` $\in$ `['standing_labcoat', 'seated_desk']`

#### Advantages of Slot-Swapping for Outreach Video Engine:
1. **Zero Aesthetic Drift:** Every hand and face is pre-rendered and verified against our style guide. No AI warping.
2. **Combinatorial Expressiveness:** With 1 torso, 3 head states, and 6 hand states, the host can execute $1 \times 3 \times 6 = 18$ distinct presenter actions using just 10 transparent SVG/PNG files.
3. **Automated Script Triggers:** In our pipeline, storyboard tags automatically switch slots:
   - `[TAG: HOOK_REVEAL]` $\to$ `Head: neutral_talk`, `Hand: point_up` (Matches `frame_0001.jpg`)
   - `[TAG: WARNING_MARGIN]` $\to$ `Head: skeptical_frown`, `Hand: stop_palm` (Matches `frame_0080.jpg`)
   - `[TAG: FORMULA_EVIDENCE]` $\to$ `Head: explaining_smile`, `Hand: open_presenting` (Matches `frame_0014.jpg`)

---

## 5. Architectural Blueprint for Outreach Video Engine

To elevate our current Remotion / HyperFrames / HTML player to institutional standards, we outline five concrete improvements:

### Improvement 1: Unified Affine Scene Node Interface
Replace ad-hoc CSS positioning (`top: 45%; left: 32%; transform: translate(-50%, -50%)`) with a structured `SceneNode` component that guarantees mathematically sound anchor-point transformations.

```typescript
// Proposed src/engine/SceneNode.ts
export interface Transform2D {
  x: number;          // Position in 1920x1080 canvas
  y: number;
  scaleX?: number;    // Normalized scale (1.0 = 100%)
  scaleY?: number;
  rotation?: number;  // Degrees
  anchorX?: number;   // 0.0 (left) to 1.0 (right), default 0.5 (center)
  anchorY?: number;   // 0.0 (top) to 1.0 (bottom), default 0.5 (center)
  opacity?: number;
  zIndex?: number;
}

export function computeTransformMatrix(t: Transform2D): string {
  const ax = (t.anchorX ?? 0.5) * 100;
  const ay = (t.anchorY ?? 0.5) * 100;
  const sx = t.scaleX ?? 1;
  const sy = t.scaleY ?? 1;
  const rot = t.rotation ?? 0;

  // Emits deterministic matrix3d for hardware-accelerated GPU compositing
  return `translate(${t.x}px, ${t.y}px) rotate(${rot}deg) scale(${sx}, ${sy}) translate(-${ax}%, -${ay}%)`;
}
```

### Improvement 2: The Analytic Spring Damper Hook
Implement seek-safe closed-form spring physics for stamps, scale tipping, and metric counters:

```typescript
// Proposed src/engine/useAnalyticSpring.ts
export function analyticSpring({
  frame,
  fps,
  startFrame,
  stiffness = 120,
  damping = 14,
  mass = 1,
  from = 0,
  to = 1,
}: SpringConfig): number {
  if (frame < startFrame) return from;
  const t = (frame - startFrame) / fps;
  
  const omegaN = Math.sqrt(stiffness / mass);
  const zeta = damping / (2 * Math.sqrt(stiffness * mass));
  
  let progress: number;
  if (zeta < 1) {
    // Underdamped (Overshoot & bounce)
    const omegaD = omegaN * Math.sqrt(1 - zeta * zeta);
    progress = 1 - Math.exp(-zeta * omegaN * t) * 
      (Math.cos(omegaD * t) + (zeta * omegaN / omegaD) * Math.sin(omegaD * t));
  } else {
    // Critically damped / Overdamped
    progress = 1 - (1 + omegaN * t) * Math.exp(-omegaN * t);
  }
  
  return from + (to - from) * progress;
}
```

### Improvement 3: The Modular Host Cutout Rig Component
Create a reusable, deterministic Host Cutout component that binds directly to the scene graph:

```tsx
// Proposed src/components/HostCutoutRig.tsx
export interface HostRigProps {
  x: number;
  baselineY: number; // Stamped to ground horizon (e.g., 960px)
  scale: number;     // Standardized to Doc 24 cast_figure_height
  pose: 'pointing' | 'presenting' | 'warning' | 'desk_seated';
  headEmotion: 'neutral' | 'skeptical' | 'smiling';
}

export const HostCutoutRig: React.FC<HostRigProps> = ({
  x,
  baselineY,
  scale,
  pose,
  headEmotion,
}) => {
  return (
    <div 
      style={{
        position: 'absolute',
        left: x,
        top: baselineY,
        transform: `translate(-50%, -100%) scale(${scale})`, // Anchor at feet
        transformOrigin: 'bottom center',
        zIndex: 30, // Doc 29 Layer 3
      }}
    >
      <img src={`/assets/host/torso_${pose === 'desk_seated' ? 'desk' : 'standing'}.svg`} alt="torso" />
      <img 
        src={`/assets/host/head_${headEmotion}.svg`} 
        style={{ position: 'absolute', top: '-180px', left: '45px' }} 
        alt="head" 
      />
      <img 
        src={`/assets/host/arm_${pose}.svg`} 
        style={{ position: 'absolute', top: '-60px', left: '120px' }} 
        alt="active_arm" 
      />
    </div>
  );
};
```

### Improvement 4: Dynamic SVG Balance Scale Component
The iconic *Wealth Logic* visual is the dynamic balance scale balancing **EARNS** vs. **COSTS / RENT**. We build this as a parameterized vector component:

```tsx
// Proposed src/components/DynamicBalanceScale.tsx
export const DynamicBalanceScale: React.FC<{
  tiltDegrees: number; // Driven by analyticSpring based on (Return - Cost)
  leftWeightLabel: string;
  rightWeightLabel: string;
}> = ({ tiltDegrees, leftWeightLabel, rightWeightLabel }) => {
  return (
    <div className="scale-container" style={{ position: 'relative', width: 600, height: 400 }}>
      {/* Pillar base remains vertical */}
      <img src="/assets/props/scale_pillar.svg" className="scale-pillar" />
      
      {/* Beam rotates around center fulcrum */}
      <div 
        className="scale-beam" 
        style={{ 
          transform: `rotate(${tiltDegrees}deg)`, 
          transformOrigin: '300px 80px' 
        }}
      >
        <img src="/assets/props/scale_beam.svg" />
        
        {/* Left Pan counter-rotates so it stays perpendicular to ground */}
        <div 
          className="left-pan" 
          style={{ 
            position: 'absolute', left: 40, top: 80, 
            transform: `rotate(${-tiltDegrees}deg)` 
          }}
        >
          <img src="/assets/props/scale_pan.svg" />
          <span className="weight-tag">{leftWeightLabel}</span>
        </div>
        
        {/* Right Pan counter-rotates */}
        <div 
          className="right-pan" 
          style={{ 
            position: 'absolute', right: 40, top: 80, 
            transform: `rotate(${-tiltDegrees}deg)` 
          }}
        >
          <img src="/assets/props/scale_pan.svg" />
          <span className="weight-tag">{rightWeightLabel}</span>
        </div>
      </div>
    </div>
  );
};
```

### Improvement 5: Word-Gap Boundary Snapping Engine
Integrate the acoustic transition finding directly into the script-to-storyboard compiler (`src/services/storyboard_generator.py`):
- Parse `words.json` emitted by Whisper.
- Search for inter-word silence:
  $$\Delta t = w_{i+1}.\text{start} - w_i.\text{end} \ge 0.45\text{s}$$
- Automatically snap storyboard scene cuts and entrance springs to land within $[\text{start} + 0.05\text{s}, \text{end} - 0.05\text{s}]$, ensuring visual elements are completely settled before the speaker utters the next word.

---

## 6. Implementation Roadmap for Outreach Video Engine

| Phase | Milestone | Deliverables | Target Architecture |
|---|---|---|---|
| **Phase 1** | **Math & Clock Primitives** | Add `SceneNode.ts` & `useAnalyticSpring.ts` to `content/video_engine` | Pure mathematical transforms; eliminate time-drift |
| **Phase 2** | **Cutout Host Rig** | Register `actor: host_analyst` vector pieces (Torso, 3 Heads, 6 Hands) | Zero AI drift; persistent presenter identity |
| **Phase 3** | **Interactive Evidence Library** | Build `DynamicBalanceScale`, `StampOverlay`, and `LiveCounter` components | Institutional financial evidence mechanics |
| **Phase 4** | **Audio-Gap Storyboarder** | Update pipeline compiler to snap scene transitions to Whisper breath silences | Eliminate speech-visual collisions |

---

## Sources & Reference Material

1. **The Scene Graph & Transform Hierarchy** — Vulkan Documentation Project (`docs.vulkan.org`)
2. **Scene Graph Architectures in Modern Game Engines** — GitConnected Engine Design Review
3. **Motion Canvas Architecture & Generator Timelines** — Slama & Motion Canvas Core (`motioncanvas.io/docs/time-events`)
4. **Remotion API & Deterministic Interpolation** — Remotion Documentation (`remotion.dev/docs/interpolate`)
5. **Tools for Smoother Shape Animations (Flubber)** — Noah Veltman (`github.com/veltman/flubber`)
6. **2D Skeletal & Cutout Animation Systems** — Godot Engine & Unity 2D Animation Architecture
7. **Outreach Repository Doctrine** — `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` & `24-COMPOSITION-AND-SCALE-SPEC.md`
