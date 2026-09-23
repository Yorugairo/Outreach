# Track 4: 3D Skinning Deformation & Volume Preservation (LBS vs DQS) — Tier 2 Evidence Extract

*Run: `human-anatomical-volume-proportions-2026-09` · Date: 2026-09-23 · Track: 4 · Primary Authorities: Magnenat-Thalmann et al. (1988), Kavan et al. (2007, 2008), Vaillant et al. (2013, 2014), Müller et al. (2007), Macklin et al. (2014), Blender Foundation (Armature Modifier Source)*

---

## 1. Mathematical Formulation: Linear Blend Skinning (LBS) vs Dual Quaternion Skinning (DQS)

Skeletal subspace deformation algorithms transform rest-pose mesh vertices $\mathbf{v} \in \mathbb{R}^3$ into animated world coordinates $\mathbf{v}'$ driven by an articulated hierarchy of $m$ bones.

```
Linear Blend Skinning (LBS):           v' = SUM( w_j * T_j * v )
                                       [Linear combination in R^(4x4); NOT a Lie group; yields non-rigid shear/scaling]

Dual Quaternion Skinning (DQS):        q_hat_blend = Normalize( SUM( w_j * q_hat_j ) )
                                       v' = q_hat_blend * v * (q_hat_blend)*
                                       [Convex combination projected onto SE(3); ALWAYS a rigid isometry; zero scaling]
```

### 1.1 Linear Blend Skinning (LBS / Skeletal Subspace Deformation)
Introduced by Magnenat-Thalmann et al. (1988), LBS evaluates deformed positions via linear matrix interpolation:
$$\mathbf{v}'_{\text{LBS}} = \sum_{j=1}^{m} w_j \mathbf{T}_j \mathbf{v}$$
where:
- $\mathbf{T}_j = \mathbf{M}_j \mathbf{B}_j^{-1} \in \text{SE}(3)$ is the transformation matrix for joint $j$, formed by multiplying current joint world matrix $\mathbf{M}_j$ by inverse bind pose matrix $\mathbf{B}_j^{-1}$.
- $w_j \ge 0$ is the scalar vertex skinning weight for joint $j$, subject to partition of unity: $\sum_{j=1}^m w_j = 1$.

### 1.2 Dual Quaternion Representation and DLB (Kavan et al. 2007, 2008)
Dual quaternions $\hat{q} = q_0 + \epsilon q_\epsilon$ reside in the Clifford algebra $\mathcal{C}\ell(0, 3, 1)$, where:
- $\epsilon$ is the dual unit satisfying $\epsilon^2 = 0, \epsilon \neq 0$.
- $q_0 = [s_0, \mathbf{v}_0] = [\cos(\theta/2), \mathbf{n}\sin(\theta/2)]$ is a unit quaternion representing 3D rotation by angle $\theta$ around axis $\mathbf{n}$.
- $q_\epsilon = \frac{1}{2} \mathbf{t} q_0$ is the dual quaternion encoding translation $\mathbf{t} \in \mathbb{R}^3$.
- Unit norm constraint: $\|\hat{q}\| = \hat{q} \hat{q}^* = 1 \iff \|q_0\| = 1 \text{ and } q_0 \cdot q_\epsilon = 0$.

#### Dual Quaternion Linear Blending (DLB):
Given $m$ unit dual quaternions $\hat{q}_1, \dots, \hat{q}_m$ and weights $w_1, \dots, w_m$:
$$\hat{b} = \sum_{j=1}^m w_j \hat{q}_j = \sum_{j=1}^m w_j q_{0,j} + \epsilon \sum_{j=1}^m w_j q_{\epsilon,j}$$
$$\hat{q}_{\text{blend}} = \frac{\hat{b}}{\|\hat{b}\|} = \frac{b_0}{\|b_0\|} + \epsilon \left( \frac{b_\epsilon}{\|b_0\|} - \frac{b_0 (b_0 \cdot b_\epsilon)}{\|b_0\|^3} \right)$$
The deformed vertex is transformed directly via dual quaternion sandwiching:
$$\mathbf{v}'_{\text{DQS}} = \hat{q}_{\text{blend}} \mathbf{v} \hat{q}_{\text{blend}}^*$$

Because $\hat{q}_{\text{blend}}$ is normalized, it maps strictly to a rigid transformation matrix $\mathbf{R} \in \text{SO}(3)$ and translation vector $\mathbf{t} \in \mathbb{R}^3$. The determinant of the rotational part is **identically 1**: $\det(\mathbf{R}) \equiv 1$.

---

## 2. Mathematical Proof of LBS Volume Collapse Under Axial Torsion and Flexion

The failure of LBS arises because the set of affine transformations $\text{GL}(3, \mathbb{R})$ is a vector space, but the special Euclidean group $\text{SE}(3)$ is a curved Lie group manifold. Linearly averaging two rotation matrices does not yield a rotation matrix: $\sum w_j \mathbf{R}_j \notin \text{SO}(3)$.

### 2.1 The "Candy-Wrapper" Axial Torsion Collapse (100% Cross-Sectional Annihilation)
Consider a cylindrical anatomical limb (e.g. forearm or thigh) aligned along the $z$-axis with cross-sectional radius $R$.
Let bone 1 be fixed: $\mathbf{T}_1 = \mathbf{I}_{4 \times 4}$.
Let bone 2 rotate axially around the $z$-axis by twist angle $\theta$:
$$\mathbf{T}_2 = \begin{bmatrix} \cos\theta & -\sin\theta & 0 & 0 \\ \sin\theta & \cos\theta & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$
At the midpoint of the twist region, the skinning weights are equal: $w_1 = w_2 = 0.5$.
The blended transformation matrix $\mathbf{M}_{\text{mid}}$ evaluated by LBS is:
$$\mathbf{M}_{\text{mid}} = 0.5 \mathbf{T}_1 + 0.5 \mathbf{T}_2 = \begin{bmatrix} \frac{1 + \cos\theta}{2} & -\frac{\sin\theta}{2} & 0 & 0 \\ \frac{\sin\theta}{2} & \frac{1 + \cos\theta}{2} & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

Applying trigonometric half-angle identities: $\frac{1 + \cos\theta}{2} = \cos^2(\theta/2)$ and $\frac{\sin\theta}{2} = \sin(\theta/2)\cos(\theta/2)$:
$$\mathbf{M}_{\text{mid}} = \cos(\theta/2) \begin{bmatrix} \cos(\theta/2) & -\sin(\theta/2) & 0 & 0 \\ \sin(\theta/2) & \cos(\theta/2) & 0 & 0 \\ 0 & 0 & \sec(\theta/2) & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$
The transformation in the transverse $xy$-plane is a pure rotation by $\theta/2$ scaled by the scalar factor:
$$s(\theta) = \cos\left(\frac{\theta}{2}\right)$$

#### Radius and Cross-Sectional Area Degradation:
The deformed radius of the limb at the midpoint is:
$$r'(\theta) = R \cdot \cos\left(\frac{\theta}{2}\right)$$
The deformed cross-sectional area $A'(\theta)$ is:
$$\boxed{A'(\theta) = \pi [r'(\theta)]^2 = \pi R^2 \cos^2\left(\frac{\theta}{2}\right) = A_0 \cos^2\left(\frac{\theta}{2}\right)}$$

```
Relative Cross-Section Area (A' / A0)
1.0 |====================\
    |                     \
0.8 |                      \
    |                       \
0.6 |                        \
    |                         \
0.4 |                          \
    |                           \
0.2 |                            \
    |                             \
0.0 +------+-------+-------+-------+-----> Twist Angle (theta)
    0     45      90      135     180 degrees
```

- At $\theta = 0^\circ$: $A' = A_0$ ($0\%$ loss).
- At $\theta = 90^\circ$: $A' = A_0 \cos^2(45^\circ) = 0.500 A_0$ (**$50.0\%$ cross-sectional area loss**).
- At $\theta = 120^\circ$: $A' = A_0 \cos^2(60^\circ) = 0.250 A_0$ (**$75.0\%$ cross-sectional area loss**).
- At $\theta = 180^\circ$: $A' = A_0 \cos^2(90^\circ) \equiv 0$ (**$100.0\%$ total structural collapse / singularity**).

Under extreme axial forearm pronation/supination or martial arts torso twisting, LBS pinches the limb into an infinitesimal thread (the classic "candy-wrapper" artifact).

### 2.2 Joint Pinching Under Flexion
When a joint (knee, elbow) flexes by angle $\alpha$, the inner surface vertices are interpolated along a straight line chord connecting the two bone ends rather than curving along an arc. The inner crease collapses inward, reducing local volume by up to **$35\% \text{ to } 48\%$** at $\alpha = 120^\circ$ flexion.

---

## 3. Dual Quaternion Skinning Artifacts: Joint Bulging & Collision Inelasticity

While DQS mathematically guarantees that no local volume collapse or candy-wrapper thinning occurs, it introduces two distinct artifacts:

```
+---------------------------------------------------------------------------------------------------+
|                                  DQS DEFECT PROFILE & LIMITATIONS                                 |
+---------------------------------------------------------------------------------------------------+
| 1. "Joint Bulging" Artifact:       Rigid isometry forces exterior skin outward during sharp       |
|                                    flexion (>90 deg), creating an unphysical inflated collar.     |
| 2. Zero Flesh Compression:         DQS cannot simulate soft tissue flattening or volume-          |
|                                    conserving muscular displacement upon limb contact.            |
| 3. Inability to Handle Shearing:   Dual quaternions represent only SE(3) isometries; non-uniform   |
|                                    bone scaling or shearing cannot be represented algebraically.  |
+---------------------------------------------------------------------------------------------------+
```

### 3.1 The Joint Bulging Artifact
Because DQS treats every blended transformation as a pure rigid rotation around an interpolated screw axis:
- On the exterior of a flexing elbow or knee ($>90^\circ$), the distance between the skin vertices and the screw axis is preserved rigidly.
- In living human anatomy, joint flexion stretches the skin taut against bone/tendon, flattening the joint exterior. DQS instead causes the skin to bulge outward like a rigid rubber cuff or inner tube.

### 3.2 Lack of Contact Soft-Tissue Dynamics
When the calf collides with the posterior thigh during deep knee flexion ($140^\circ$), DQS simply permits the meshes to interpenetrate without resistive volume reaction forces.

---

## 4. Blender Armature Modifier "Preserve Volume" Mechanics & The Zero-Weight Vertex Mask Vulnerability

### 4.1 Internal Implementation in Blender Engine (`armature.cc`)
In Blender's C/C++ deformation pipeline:
- When the **"Preserve Volume"** checkbox is disabled, Blender executes `armature_deform_verts` using standard LBS matrix multiplication (`mul_v3_m4v3`).
- When **"Preserve Volume"** is enabled, Blender switches the execution path to `armature_deform_verts_dqs`, converting bone matrices to dual quaternions and evaluating DLB per vertex.

### 4.2 The Zero-Weight Vertex Mask Vulnerability
A widespread defect occurs when pipelines apply a **Vertex Group mask** (such as `mhmask-preserve-volume`) to the Armature modifier or use Blender's Multi-Modifier blend stack:

```
                      [Full 3D Character Mesh]
                                 |
           +---------------------+---------------------+
           |                                           |
[Torso / Clavicle Vertices]                  [Arm & Leg Patches]
(Weight in mhmask = 1.0)                    (Weight in mhmask = 0.0)
           |                                           |
           v                                           v
[DQS Execution Active]                       [Zero Mask Influence: Fallback]
Preserve Volume evaluated.                   Modifier skipped OR falls back
No candy-wrapper collapse.                   to unmasked baseline -> STRICT LBS!
                                             Volume collapses under twist!
```

#### Mathematical Vulnerability Analysis:
1. When an Armature Modifier in Blender has a Vertex Group specified:
   $$\mathbf{v}'_{\text{final}} = (1 - w_{\text{mask}}) \mathbf{v}_{\text{base}} + w_{\text{mask}} \mathbf{v}'_{\text{mod}}$$
   If $w_{\text{mask}} = 0$, the modifier has **zero influence** ($\mathbf{v}'_{\text{final}} \equiv \mathbf{v}_{\text{base}}$).
2. If two Armature modifiers are stacked with `Multi Modifier` (Modifier 1: base deform without Preserve Volume; Modifier 2: Preserve Volume enabled with `mhmask-preserve-volume`):
   - For all vertices where $w_{\text{mask}} > 0$ (e.g. the 2,880 torso/shoulder vertices), DQS deformation is blended in.
   - For all vertices where $w_{\text{mask}} == 0$ (the arm and leg patches), Modifier 2 contributes 0.0 weight.
   - **Result:** The arm and leg patches are deformed **exclusively by Modifier 1 under pure Linear Blend Skinning (LBS)**!
3. **Evaluation Fallacy:** Any pipeline benchmark claiming to measure "DQS volume preservation" or "preserved limb volume" while evaluating arm or leg geometry with zero weights in `mhmask-preserve-volume` is in reality measuring unmitigated LBS candy-wrapper collapse.

---

## 5. Advanced Volume-Preserving Alternatives: Implicit Skinning & PBD

To resolve both LBS candy-wrapper collapse and DQS joint bulging without expensive offline FEM simulation:

### 5.1 Implicit Skinning (Vaillant et al. 2013, 2014)
- **Authority:** Vaillant, R., Barthe, L., Guennebaud, G., Cani, M. P., Rohmer, D., Wyvill, B., Gourmel, O., and Paulin, M. (2013). "Implicit Skinning: Real-Time Skin Deformation with Contact Modeling." *ACM Transactions on Graphics (SIGGRAPH 2013)*, 32(4): 125:1–125:11. [DOI: 10.1145/2461912.2461960](https://doi.org/10.1145/2461912.2461960)
- **Method:**
  1. Approximate the character's flesh volume as a union of 3D scalar field functions $\phi_j(\mathbf{x})$ (Hermite Radial Basis Functions or convolution surfaces) associated with each rigid bone.
  2. Compute coarse kinematic deformation using standard skinning (LBS or DQS) to yield candidate position $\tilde{\mathbf{v}}$.
  3. In a GPU compute shader, project $\tilde{\mathbf{v}}$ onto the target contact-aware isosurface $\{\mathbf{x} \in \mathbb{R}^3 \mid \sum_j \phi_j(\mathbf{x}) = \text{iso}\}$ using gradient descent:
     $$\mathbf{v}_{k+1} = \mathbf{v}_k - \frac{\Phi(\mathbf{v}_k) - \sigma_{\text{iso}}}{\|\nabla \Phi(\mathbf{v}_k)\|^2} \nabla \Phi(\mathbf{v}_k)$$
  4. Automatically models skin contact, muscle bulging, and eliminates both candy-wrapper collapse and joint pinching in $<5\text{ ms}$ per frame.

### 5.2 Position-Based Dynamics (PBD) Volume Constraints
- **Authority:** Müller, M., Heidelberger, B., Hennix, M., and Ratcliff, J. (2007). "Position Based Dynamics." *Journal of Virtual Reality and Broadcasting*, 4(3): 1–14; Macklin, M. et al. (2014). "Unified Particle Physics for Real-Time Applications." *ACM TOG*, 33(4).
- **Formulation:** For an internal tetrahedral mesh discretization with vertices $(\mathbf{x}_1, \mathbf{x}_2, \mathbf{x}_3, \mathbf{x}_4)$, define the volumetric equality constraint:
  $$C(\mathbf{x}_1, \mathbf{x}_2, \mathbf{x}_3, \mathbf{x}_4) = \frac{1}{6} (\mathbf{x}_2 - \mathbf{x}_1) \cdot \left( (\mathbf{x}_3 - \mathbf{x}_1) \times (\mathbf{x}_4 - \mathbf{x}_1) \right) - V_0 = 0$$
- In each PBD projection step, vertex position corrections $\Delta \mathbf{x}_i$ are projected along $\nabla_{\mathbf{x}_i} C$:
  $$\Delta \mathbf{x}_i = -\frac{w_i C(\mathbf{x})}{\sum_j w_j \|\nabla_{\mathbf{x}_j} C\|^2} \nabla_{\mathbf{x}_i} C$$
  guaranteeing exact volume preservation throughout extreme combat motions and impacts.

---

## 6. Primary Literature & Citation Standards

1. **Magnenat-Thalmann, N., Laperrière, R., and Thalmann, D.** (1988). "Joint-Dependent Local Deformations for Hand Animation and Object Grasping." *Proceedings of Graphics Interface '88*, pp. 26–33.
2. **Kavan, L., Collins, S., Žára, J., and O'Sullivan, C.** (2007). "Skinning with Dual Quaternions." *Proceedings of the 2007 ACM SIGGRAPH Symposium on Interactive 3D Graphics and Games (I3D '07)*, pp. 39–46. [DOI: 10.1145/1230100.1230107](https://doi.org/10.1145/1230100.1230107)
3. **Kavan, L., Collins, S., Žára, J., and O'Sullivan, C.** (2008). "Geometric Skinning with Dual Quaternions." *IEEE Transactions on Visualization and Computer Graphics*, 14(5): 1051–1061. [DOI: 10.1109/TVCG.2008.45](https://doi.org/10.1109/TVCG.2008.45)
4. **Vaillant, R., Barthe, L., Guennebaud, G., Cani, M. P., Rohmer, D., Wyvill, B., Gourmel, O., and Paulin, M.** (2013). "Implicit Skinning: Real-Time Skin Deformation with Contact Modeling." *ACM Transactions on Graphics*, 32(4): 125:1–125:11. [DOI: 10.1145/2461912.2461960](https://doi.org/10.1145/2461912.2461960)
5. **Müller, M., Heidelberger, B., Hennix, M., and Ratcliff, J.** (2007). "Position Based Dynamics." *Journal of Virtual Reality and Broadcasting*, 4(3): 1–14. [DOI: 10.20385/1860-2037/4.2007.3](https://doi.org/10.20385/1860-2037/4.2007.3)
6. **Macklin, M., Müller, M., Chentanez, N., and Kim, T. Y.** (2014). "Unified particle physics for real-time applications." *ACM Transactions on Graphics*, 33(4): 1–12. [DOI: 10.1145/2601097.2601152](https://doi.org/10.1145/2601097.2601152)
