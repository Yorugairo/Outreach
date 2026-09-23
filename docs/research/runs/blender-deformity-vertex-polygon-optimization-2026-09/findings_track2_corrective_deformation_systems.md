# Track 2: Corrective Deformation Systems (PSD, Smooth & Cage Modifiers)

## 1. Executive Summary & Algorithmic Motivation

Standard Linear Blend Skinning (LBS) computes the deformed position of each vertex as a linear combination of bone transformation matrices. While computationally inexpensive ($O(V \cdot B)$ complexity, easily parallelized on GPU vertex shaders), LBS suffers from two classical geometric failure modes:
1. **Volume Loss on Flexion ("Collapsing Elbow"):** As a joint bends, opposing skin surfaces interpolate linearly, shrinking the cross-sectional area of the limb.
2. **Candy-Wrapper Artifact on Axial Twist:** When a bone twists along its longitudinal axis by $180^\circ$, vertices interpolate across the center line, collapsing the cross-section to a singularity.

While Dual Quaternion Skinning (DQS; Kavan et al. 2007) mitigates twisting collapse, it introduces severe bulging artifacts ("joint pinching" or "bicep ballooning") under extreme flexion. To achieve hero-level anatomical fidelity without full finite element biomechanical muscle simulation, production pipelines rely on **Corrective Deformation Systems**:
- **Pose Space Deformation (PSD) / Corrective Shape Keys:** Non-linear delta offsets mapped directly to skeletal pose configurations.
- **Blender Corrective Smooth Modifier (Delta Mush):** Post-skinning Laplacian relaxation with rest-frame delta reconstruction.
- **Harmonic Cage Deformers (Mesh Deform):** Volumetric coordinate systems that insulate high-resolution geometry from direct skeletal shearing.

```
       CONVENTIONAL LBS                   POSE SPACE DEFORMATION (PSD)            CORRECTIVE SMOOTH (DELTA MUSH)
   +-----------------------+              +---------------------------+              +---------------------------+
   |  Skeletal Skinning    |              | Skeletal Skinning (LBS)   |              | Skeletal Skinning (LBS)   |
   |      (LBS / DQS)      |              +-------------+-------------+              +-------------+-------------+
   +-----------+-----------+                            |                                          |
               |                                        v                                          v
               v                          +-------------+-------------+              +-------------+-------------+
      [Collapsing Elbow &                 |  RBF Pose Driver Query    |              | Iterative Laplacian Smooth|
       Pinching Folds]                    |  (Eval $\Delta x(p)$ deltas)              | ($k$ passes, factor $\lambda$)            |
                                          +-------------+-------------+              +-------------+-------------+
                                                        |                                          |
                                                        v                                          v
                                          +-------------+-------------+              +-------------+-------------+
                                          | Additive Delta Injection  |              | Rest Delta Re-projection  |
                                          | (Anatomical Sculpt / Keys)|              | (Preserves high-freq mesh)|
                                          +---------------------------+              +---------------------------+
```

---

## 2. Pose Space Deformation (PSD) & Corrective Shape Keys

### 2.1 Theoretical Foundation: Lewis et al. (SIGGRAPH 2000)
Pose Space Deformation (PSD), formulated by J.P. Lewis, Matt Cordner, and Nickson Fong (ACM SIGGRAPH 2000), unifies shape interpolation (blendshapes/morph targets) and skeleton-driven skinning into a generalized scattered data interpolation framework.

#### The Problem Formulation:
Let $\mathbf{p} \in \mathcal{P}$ denote a skeletal pose vector representing joint angles, rotation quaternions, or coordinate transform parameters:
$$\mathbf{p} = [\theta_1, \theta_2, \dots, \theta_D]^T \in \mathbb{R}^D$$
Let $v_i^{(0)}$ be the rest-pose position of vertex $i$. Linear blend skinning deforms vertex $i$ according to:
$$v_i^{\text{LBS}}(\mathbf{p}) = \sum_{j=1}^{M} w_{i,j} T_j(\mathbf{p}) v_i^{(0)}$$
Where $w_{i,j}$ is the skinning weight of vertex $i$ with respect to bone $j$, and $T_j(\mathbf{p})$ is the world transform matrix of bone $j$.

PSD defines the final position as the sum of the base skinning deformation and a pose-dependent corrective displacement field $\delta v_i(\mathbf{p})$ defined in the local coordinate space of the driving bone:
$$v_i^{\text{PSD}}(\mathbf{p}) = \sum_{j=1}^{M} w_{i,j} T_j(\mathbf{p}) \left( v_i^{(0)} + \delta v_i(\mathbf{p}) \right)$$

### 2.2 Radial Basis Function (RBF) Interpolation vs. Linear Drivers

#### Radial Basis Function (RBF) Formulation:
Given a set of $K$ sculpt examples sculpted at specific key poses $\mathbf{p}_k$ ($k = 1, \dots, K$), the continuous corrective displacement $\delta v_i(\mathbf{p})$ is reconstructed using Radial Basis Functions:
$$\delta v_i(\mathbf{p}) = \sum_{k=1}^{K} \mathbf{w}_{i,k} \phi(\|\mathbf{p} - \mathbf{p}_k\|) + \mathbf{P}(\mathbf{p})$$
Where:
- $\phi(r)$ is a radial basis kernel. Common choices include:
  - **Gaussian Kernel:** $\phi(r) = \exp\left( -(\epsilon r)^2 \right)$ (localized activation).
  - **Multiquadric Kernel:** $\phi(r) = \sqrt{1 + (\epsilon r)^2}$.
  - **Thin Plate Spline (TPS):** $\phi(r) = r^2 \ln(r)$ (for 2D/3D pose spaces, optimal smoothness).
- $\mathbf{P}(\mathbf{p})$ is a low-order polynomial term ensuring affine invariance.
- $\mathbf{w}_{i,k}$ are weight vectors solved via the linear system:
  $$\begin{bmatrix}
  \Phi & \mathbf{P} \\
  \mathbf{P}^T & \mathbf{0}
  \end{bmatrix}
  \begin{bmatrix}
  \mathbf{W} \\
  \mathbf{C}
  \end{bmatrix} =
  \begin{bmatrix}
  \mathbf{D} \\
  \mathbf{0}
  \end{bmatrix}$$
  Where $\Phi_{jk} = \phi(\|\mathbf{p}_j - \mathbf{p}_k\|)$ is the kernel Gram matrix, and $\mathbf{D}$ contains the sculpted target offsets.

#### Comparison: RBF Pose Drivers vs. Native Blender Linear Drivers
In vanilla Blender, Corrective Shape Keys are typically driven by bone transform channels (e.g., `rotation_euler`, `rotation_quaternion`) using the **Driver Graph Editor**:

| Feature / Property | Native Blender Linear / Curve Driver | Radial Basis Function (RBF) Driver |
| :--- | :--- | :--- |
| **Mathematical Basis** | 1D scalar function: $f(\theta) = a\theta + b$ or Bézier curve | High-dimensional scattered interpolation: $\mathbb{R}^D \to \mathbb{R}^3$ |
| **Multi-Axis Coupling** | Fails on gimbal lock / diagonal swing (e.g., shoulder flex + abduct) | Naturally solves spherical coupling ($S^2 / SO(3)$ pose space) |
| **Interpolation Artifacts** | Over-additive ballooning when two 1D drivers fire simultaneously | Controlled metric distance; partition of unity prevents over-extension |
| **Authoring Complexity** | High manual tuning of curve tangents and driver math expressions | Low: artist poses character, sculpts correction, hits "Add RBF Sample" |
| **Runtime Performance** | Extremely fast ($O(1)$ per driver curve) | Fast matrix-vector product ($O(K)$ per vertex, $K \le 20$ samples) |
| **Blender Production Tooling**| Built-in (`bpy.types.Driver`) | Third-party / pipeline add-on (e.g., *RBF Drivers*, *B-Shape*) |

---

## 3. Blender Corrective Smooth Modifier (Delta Mush Algorithm)

### 3.1 Historical Evolution & Seminal Literature
The Corrective Smooth modifier in Blender (`source/blender/modifiers/intern/MOD_correctivesmooth.c`) is an open-source implementation of the **Delta Mush** algorithm developed by Rhythm & Hues Studios:
- **Primary Literature:** Joe Mancewicz, Matt L. Derksen, Cyrus A. Wilson, *"Delta Mush: Smoothing Deformations While Preserving Detail"*, ACM SIGGRAPH 2014 Talks (`doi:10.1145/2614028.2615435`).
- **Direct Extension:** Binh Huy Le & J.P. Lewis, *"Direct Delta Mush: Rapid Host-Side and GPU-Side Skinning"*, ACM Transactions on Graphics (SIGGRAPH 2019), `doi:10.1145/3306346.3322977`.

### 3.2 Mathematical Formulation of Delta Mush
The algorithm operates in two phases: an offline precomputation (Bind phase) and a per-frame deformation (Evaluation phase).

#### Phase 1: Precomputation at Rest Pose
1. Let $\mathbf{X}_{\text{rest}} \in \mathbb{R}^{V \times 3}$ be the rest mesh vertex coordinates.
2. An iterative discrete Laplacian smoothing operator $\mathbf{S}$ is applied for $m$ iterations with relaxation factor $\lambda \in (0, 1]$:
   $$\mathbf{X}_{\text{smooth}}^{(0)} = \mathbf{X}_{\text{rest}}$$
   $$\mathbf{X}_{\text{smooth}}^{(t+1)} = (1 - \lambda)\mathbf{X}_{\text{smooth}}^{(t)} + \lambda \mathbf{L} \mathbf{X}_{\text{smooth}}^{(t)}$$
   Where $\mathbf{L}$ is the normalized umbrella matrix:
   $$\mathbf{L}_{ij} = \begin{cases} 
   \frac{1}{|\mathcal{N}(i)|}, & \text{if } j \in \mathcal{N}(i) \\ 
   0, & \text{otherwise} 
   \end{cases}$$
3. For each vertex $i$, establish a local orthonormal tangent frame (Darboux frame) on the smoothed rest surface $\mathbf{X}_{\text{smooth}}^{(m)}$:
   $$\mathbf{F}_i^{(0)} = \begin{bmatrix} \mathbf{t}_i^{(0)} & \mathbf{b}_i^{(0)} & \mathbf{n}_i^{(0)} \end{bmatrix} \in SO(3)$$
4. Compute the coordinate difference ("Delta vector") in the rest global space:
   $$\Delta \mathbf{x}_i = \mathbf{X}_{\text{rest}, i} - \mathbf{X}_{\text{smooth}, i}^{(m)}$$
5. Project the delta vector into the local frame $\mathbf{F}_i^{(0)}$ to store invariant local offsets:
   $$\mathbf{d}_i = \left( \mathbf{F}_i^{(0)} \right)^T \Delta \mathbf{x}_i \in \mathbb{R}^3$$

#### Phase 2: Per-Frame Evaluation Under Armature Deformation
1. The deformed mesh $\mathbf{X}_{\text{deform}}$ is computed via standard skinning (LBS).
2. The identical Laplacian smoothing operator $\mathbf{S}$ is applied to the deformed mesh for $m$ iterations:
   $$\mathbf{X}_{\text{deform\_smooth}} = \mathbf{S}^m \mathbf{X}_{\text{deform}}$$
3. Construct the updated local tangent frames $\mathbf{F}_i(\mathbf{p})$ on the deformed smooth mesh $\mathbf{X}_{\text{deform\_smooth}}$.
4. Re-apply the stored rest deltas $\mathbf{d}_i$ transformed by the current local frame:
   $$\mathbf{X}_{\text{final}, i} = \mathbf{X}_{\text{deform\_smooth}, i} + \mathbf{F}_i(\mathbf{p}) \mathbf{d}_i$$

### 3.3 Blender Parameter Architecture & Trade-Offs

In Blender's `Corrective Smooth` modifier interface, parameters map directly to the algorithmic terms:
- **Smooth Type:**
  - `Simple`: Standard cotangent or umbrella Laplacian. Computationally cheaper, but exhibits volume shrinkage around high-curvature sharp edges (noses, claws, knuckles).
  - `Scale-Preserving`: Rescales edge vectors after each smoothing iteration to preserve original rest-edge lengths. Prevents shrinkage at the cost of additional normalization passes.
- **Factor ($\lambda$):** Range $[0.0, 1.0]$. Controls the step size per Laplacian iteration. Values $>0.5$ risk numerical instability on irregular meshes.
- **Repeat ($m$):** Iteration count. 
  - $m = 5 - 10$: Cleans up minor skinning wrinkles and vertex stepping.
  - $m = 25 - 40$: Produces full volume-preserving muscular sliding around bending joints.
  - $m > 50$: Diminishing returns; severely impacts CPU modifier evaluation time ($O(m \cdot E)$).
- **Bind Coords:** Serializes $\mathbf{X}_{\text{smooth}}^{(m)}$ and $\mathbf{d}_i$ into the modifier's internal data cache (`ModifierData`).

---

## 4. Cage-Based Deformation: Mesh Deform vs. Surface Deform

### 4.1 Mesh Deform: Harmonic Coordinates (Pixar, SIGGRAPH 2007)
Blender's **Mesh Deform** modifier (`source/blender/modifiers/intern/MOD_meshdeform.c`) wraps a high-resolution target mesh in a simplified, closed low-poly cage. The mathematical core is **Harmonic Coordinates**, developed by Pushkar Joshi, Mark Meyer, Tony DeRose, Brian Green, and Tom Sanocki at Pixar Animation Studios (*ACM TOG / SIGGRAPH 2007*, `doi:10.1145/1276377.1276466`).

#### Why Classical Coordinates Fail:
- **Mean Value Coordinates (Floater 2003):** Can take negative values in non-convex regions, causing geometry inside limb crevices (armpits, groin) to move in the opposite direction of the controlling cage vertices.
- **Harmonic Coordinates:** Defined as the solution to Laplace's equation over the bounded interior domain $\Omega$:
  $$\nabla^2 \phi_j(\mathbf{x}) = 0 \quad \forall \mathbf{x} \in \Omega$$
  Subject to Dirichlet boundary conditions:
  $$\phi_j(\mathbf{v}_k) = \delta_{jk} = \begin{cases} 1, & j = k \\ 0, & j \ne k \end{cases} \quad \text{on } \partial \Omega$$
  By the maximum principle of elliptic PDEs:
  $$0 \le \phi_j(\mathbf{x}) \le 1 \quad \forall \mathbf{x} \in \Omega, \quad \sum_{j=1}^{C} \phi_j(\mathbf{x}) = 1$$
  Harmonic coordinates are **strictly non-negative** and form a smooth partition of unity, guaranteeing non-intersecting, smooth interior volumetric deformation.

```
                    HARMONIC CAGE VOLUMETRIC GRID BINDING
                               Cage Vertex C_j
                                      o
                                     / \
                        +-----------+---+-----------+
                        |  Grid Cell (i, j, k)      |
                        |     \nabla^2 \phi = 0     |
                        |      o Target Vertex v_i  |
                        |                           |
                        +---------------------------+
```

#### Binding Process & Octree Grid:
During the `Bind` phase in Blender:
1. The cage boundary $\partial \Omega$ is voxelized into a regular octree grid (`Grid Resolution` parameter: typically 5 to 8, yielding $2^5 = 32$ to $2^8 = 256$ volumetric subdivisions).
2. Laplace's equation is solved iteratively using Successive Over-Relaxation (SOR) or multigrid methods to calculate $\phi_j$ at each grid cell corner.
3. Target mesh vertices $v_i$ evaluate their cage weights by trilinear interpolation within their bounding grid cell.

### 4.2 Surface Deform: Barycentric Target Binding
While Mesh Deform binds volumetric interiors to a closed cage, the **Surface Deform** modifier (`source/blender/modifiers/intern/MOD_surfacedeform.c`) binds arbitrary geometry (such as secondary cloth, armor plates, eyebrows, bandages) directly to the 2D surface of a deforming driver mesh.

#### Algorithmic Formulation:
1. For each target vertex $v_t$, locate the nearest polygon (triangle or quad) on the source surface.
2. Compute the barycentric coordinates $(u, v, w)$ of the projected point on that polygon.
3. Compute the orthogonal distance offset along the interpolated surface normal:
   $$h_t = (v_t - p_{\text{proj}}) \cdot \mathbf{n}_{\text{source}}$$
4. During deformation, evaluate the new polygon vertex positions, compute the updated tangent frame, and reconstruct $v_t$:
   $$v_t' = u A' + v B' + w C' + h_t \mathbf{n}_{\text{source}}'$$

### 4.3 Structural Comparison: Armature vs. Corrective Smooth vs. Cage Deformers

| System / Modifier | Evaluation Complexity | Memory Footprint | Runtime Viewport FPS (100k Verts) | Primary Production Role |
| :--- | :--- | :--- | :--- | :--- |
| **Armature Modifier (Direct LBS)** | $O(V \cdot B)$ (Vectorized CPU/GPU) | Minimal (Bone weights array: $V \times 4$ floats) | $60+$ FPS | Primary skeletal articulation |
| **Corrective Shape Keys (Linear Driver)** | $O(V_{\text{active}})$ | $O(K \cdot V)$ (Delta tables per key) | $55 - 60$ FPS | Local facial expressions, isolated joint fixes |
| **RBF Driven Shape Keys** | $O(K^2 + K \cdot V)$ | $O(K \cdot V + K \cdot D)$ | $45 - 55$ FPS | Anatomical muscle bulge, shoulder complex |
| **Corrective Smooth (Delta Mush)** | $O(m \cdot E)$ ($m$ Laplacian passes) | Moderate (Rest smooth cache $\sim 12\text{ MB}$) | $18 - 30$ FPS (CPU bottleneck) | Hero character organic joints without manual skin weighting |
| **Mesh Deform (Harmonic Cage)** | $O(V \cdot C_{\text{active}})$ (Grid lookup) | Heavy (Octree grid weights: $50 - 200\text{ MB}$) | $25 - 40$ FPS | Stylized character body rigs, cartoon squash/stretch |
| **Surface Deform** | $O(V_{\text{target}})$ | Light ($V_{\text{target}} \times$ barycentric coords) | $50 - 60$ FPS | Secondary garments, buckles, eyebrows, hair cards |

---

## 5. Production Rigging Recipes & Execution Protocols

### 5.1 The Zero-Pinch Elbow/Knee Recipe
1. **Topology:** Base mesh with 5-loop diamond span over the joint (Track 1).
2. **Skinning:** Standard Linear Blend Skinning with smooth 2-bone influence falloff across the 5 loops.
3. **Corrective Smooth Modifier Configuration:**
   - Stack Placement: Immediately below `Armature` modifier.
   - Smooth Type: `Scale-Preserving`.
   - Factor: `0.65`.
   - Repeat: `15 - 20`.
   - Bind: Executed in pristine rest T-pose / A-pose.
4. **Result:** Completely eliminates flexor pinching up to $135^\circ$ without authoring a single corrective shape key.

### 5.2 RBF Shoulder Joint Decoupling
1. Isolate the humerus ball-and-socket joint ($3\text{ DOF}$: pitch, yaw, roll).
2. Define a 3D RBF pose driver on bone rotational swing angles $[\theta_{\text{swing}}, \phi_{\text{twist}}]$.
3. Sculpt 4 primary corrective targets:
   - Arm forward ($90^\circ$ flexion): Pectoralis compression + anterior deltoid swell.
   - Arm lateral ($90^\circ$ abduction): Clavicular lift + medial deltoid contraction.
   - Arm backward ($45^\circ$ extension): Latissimus stretch + posterior deltoid activation.
   - Arm overhead ($180^\circ$ elevation): Trapezius rotation + scapular glide.
4. Solve RBF weights using Thin Plate Spline kernel $\phi(r) = r^2 \ln(r)$.
5. Output delivers artifact-free anatomical deformation across all compound diagonal arm gestures.

---

## 6. Primary Sources & Academic Literature

1. **Lewis, J. P., Cordner, M., & Fong, N.** (2000). *Pose space deformation: a unified approach to shape interpolation and skeleton-driven deformation*. In Proceedings of the 27th annual conference on Computer graphics and interactive techniques (SIGGRAPH '00), 165–172. `doi:10.1145/344779.344862`.
   - *Key Contribution:* Foundational paper introducing scattered data interpolation and RBFs for skeleton-driven facial and limb deformations.
2. **Mancewicz, J., Derksen, M. L., & Wilson, C. A.** (2014). *Delta Mush: Smoothing Deformations While Preserving Detail*. In ACM SIGGRAPH 2014 Talks (SIGGRAPH '14), Article 56. `doi:10.1145/2614028.2615435`.
   - *Key Contribution:* Original formulation of the Delta Mush algorithm used as the baseline for Blender's Corrective Smooth modifier.
3. **Le, B. H., & Lewis, J. P.** (2019). *Direct Delta Mush: Rapid Host-Side and GPU-Side Skinning*. ACM Transactions on Graphics (TOG), 38(4), Article 59. `doi:10.1145/3306346.3322977`.
   - *Key Contribution:* Proves that iterative Laplacian smoothing and delta reconstruction can be pre-factored into a non-iterative direct matrix-weight skinning formulation compatible with standard GPU vertex shaders.
4. **Joshi, P., Meyer, M., DeRose, T., Green, B., & Sanocki, T.** (2007). *Harmonic coordinates for character articulation*. ACM Transactions on Graphics (TOG), 26(3), Article 71. `doi:10.1145/1276377.1276466`.
   - *Key Contribution:* Introduction of Harmonic Coordinates for cage-based character articulation; theoretical basis of Blender's `Mesh Deform` modifier.
5. **Kavan, L., Collins, S., Žára, J., & O'Sullivan, C.** (2007). *Skinning with dual quaternions*. In Proceedings of the 2007 symposium on Interactive 3D graphics and games (I3D '07), 39–46. `doi:10.1145/1230100.1230107`.
   - *Key Contribution:* Eliminates candy-wrapper artifacts via dual quaternion algebra, highlighting the trade-offs between linear blend skinning and non-linear blend systems.
6. **Blender Foundation Source Code.** (2024). *`source/blender/modifiers/intern/MOD_correctivesmooth.c`* and *`MOD_meshdeform.c`*. Git commit history and algorithm comments.
