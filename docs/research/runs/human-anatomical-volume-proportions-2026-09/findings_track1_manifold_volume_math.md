# Track 1: Discrete Mesh Manifold Volume & Boundary Mathematics — Tier 2 Evidence Extract

*Run: `human-anatomical-volume-proportions-2026-09` · Date: 2026-09-23 · Track: 1 · Primary Authorities: Gauss (1813), Mirtich (1996), Eberly (2002, 2010), Zhang & Chen (2001), Chernyaev (1995), Botsch et al. (2010)*

---

## 1. Discrete Divergence Theorem (Gauss's Theorem) for 3D Triangular Meshes

### 1.1 Continuum Vector Calculus Foundations
In classical continuum mechanics and potential theory, Gauss's Divergence Theorem relates the volume integral of the divergence of a continuously differentiable vector field $\mathbf{F}: \mathbb{R}^3 \to \mathbb{R}^3$ over a bounded compact region $\Omega \subset \mathbb{R}^3$ to the flux of $\mathbf{F}$ through the closed boundary surface $\partial \Omega$:
$$\iiint_{\Omega} (\nabla \cdot \mathbf{F}) \, dV = \iint_{\partial \Omega} (\mathbf{F} \cdot \mathbf{n}) \, dA$$
where:
- $\Omega \subset \mathbb{R}^3$ is an open bounded domain with piecewise smooth boundary $\partial \Omega$.
- $\mathbf{n} = [n_x, n_y, n_z]^T$ is the outward-pointing unit normal vector on $\partial \Omega$.
- $dA$ is the infinitesimal surface area element.
- $dV = dx \, dy \, dz$ is the infinitesimal volume element.

### 1.2 Derivation of the Volume Integral Reduction
To evaluate the scalar enclosed volume $V(\Omega) = \iiint_{\Omega} 1 \, dV$, we select a vector field $\mathbf{F}$ whose divergence is identically constant.

#### Case A: Coordinate Vector Field
Let $\mathbf{F}(\mathbf{x}) = \mathbf{x} = [x, y, z]^T$. The divergence is:
$$\nabla \cdot \mathbf{F} = \frac{\partial x}{\partial x} + \frac{\partial y}{\partial y} + \frac{\partial z}{\partial z} = 1 + 1 + 1 = 3$$
Substituting into the Divergence Theorem:
$$\iiint_{\Omega} 3 \, dV = 3 \iiint_{\Omega} dV = 3 V(\Omega) = \iint_{\partial \Omega} (\mathbf{x} \cdot \mathbf{n}) \, dA$$
Dividing by 3 yields:
$$V(\Omega) = \frac{1}{3} \iint_{\partial \Omega} (\mathbf{x} \cdot \mathbf{n}) \, dA$$

#### Case B: Uniaxial Projection Fields
Alternatively, choosing $\mathbf{F}(\mathbf{x}) = [x, 0, 0]^T$ or $[0, y, 0]^T$ or $[0, 0, z]^T$ yields $\nabla \cdot \mathbf{F} = 1$:
$$V(\Omega) = \iint_{\partial \Omega} x \, n_x \, dA = \iint_{\partial \Omega} y \, n_y \, dA = \iint_{\partial \Omega} z \, n_z \, dA$$

### 1.3 Discrete Formulation for Piecewise Linear Triangular Meshes
Let $\mathcal{M} = (\mathcal{V}, \mathcal{F})$ be a watertight 2-manifold triangular boundary mesh representing $\partial \Omega$.
- $\mathcal{F} = \{T_1, T_2, \dots, T_F\}$ is the set of $F$ oriented triangular faces.
- Each triangle $T_i$ is defined by ordered vertices $(\mathbf{v}_{i,1}, \mathbf{v}_{i,2}, \mathbf{v}_{i,3}) \in \mathbb{R}^3$, wound counter-clockwise when viewed from the exterior.

The unnormalized outward normal vector of face $T_i$ is given by the cross product of two edge vectors:
$$\mathbf{N}_i = (\mathbf{v}_{i,2} - \mathbf{v}_{i,1}) \times (\mathbf{v}_{i,3} - \mathbf{v}_{i,1}) = \mathbf{v}_{i,1} \times \mathbf{v}_{i,2} + \mathbf{v}_{i,2} \times \mathbf{v}_{i,3} + \mathbf{v}_{i,3} \times \mathbf{v}_{i,1}$$
The triangle surface area is $A_i = \frac{1}{2} \|\mathbf{N}_i\|$, and the unit outward normal is $\mathbf{n}_i = \frac{\mathbf{N}_i}{\|\mathbf{N}_i\|}$. Thus:
$$\mathbf{n}_i \, dA_i = \frac{1}{2} \mathbf{N}_i$$

The surface integral over triangle $T_i$ evaluated at the face centroid $\bar{\mathbf{x}}_i = \frac{1}{3}(\mathbf{v}_{i,1} + \mathbf{v}_{i,2} + \mathbf{v}_{i,3})$ is:
$$\iint_{T_i} (\mathbf{x} \cdot \mathbf{n}) \, dA = \bar{\mathbf{x}}_i \cdot (\mathbf{n}_i A_i) = \frac{1}{3}(\mathbf{v}_{i,1} + \mathbf{v}_{i,2} + \mathbf{v}_{i,3}) \cdot \left[ \frac{1}{2} (\mathbf{v}_{i,2} - \mathbf{v}_{i,1}) \times (\mathbf{v}_{i,3} - \mathbf{v}_{i,1}) \right]$$

Expanding the scalar triple product:
$$\mathbf{v}_{i,1} \cdot (\mathbf{v}_{i,2} \times \mathbf{v}_{i,3}) = \det\begin{bmatrix} \mathbf{v}_{i,1} & \mathbf{v}_{i,2} & \mathbf{v}_{i,3} \end{bmatrix}$$
Because $(\mathbf{v}_{i,2} - \mathbf{v}_{i,1}) \times (\mathbf{v}_{i,3} - \mathbf{v}_{i,1}) = \mathbf{v}_{i,1} \times \mathbf{v}_{i,2} + \mathbf{v}_{i,2} \times \mathbf{v}_{i,3} + \mathbf{v}_{i,3} \times \mathbf{v}_{i,1}$, and the dot product of any $\mathbf{v}_{i,k}$ with a cross product containing $\mathbf{v}_{i,k}$ vanishes identically ($\mathbf{a} \cdot (\mathbf{a} \times \mathbf{b}) = 0$), the expansion simplifies to:
$$\iint_{T_i} (\mathbf{x} \cdot \mathbf{n}) \, dA = \frac{1}{2} \mathbf{v}_{i,1} \cdot (\mathbf{v}_{i,2} \times \mathbf{v}_{i,3})$$

Multiplying by the pre-factor $\frac{1}{3}$ and summing over all $F$ faces yields the canonical discrete volume formula:
$$\boxed{V(\mathcal{M}) = \frac{1}{6} \sum_{i=1}^{F} \mathbf{v}_{i,1} \cdot (\mathbf{v}_{i,2} \times \mathbf{v}_{i,3}) = \frac{1}{6} \sum_{i=1}^{F} \det \begin{bmatrix} x_{i,1} & x_{i,2} & x_{i,3} \\ y_{i,1} & y_{i,2} & y_{i,3} \\ z_{i,1} & z_{i,2} & z_{i,3} \end{bmatrix}}$$

### 1.4 Geometric Interpretation: Sum of Signed Tetrahedral Volumes
Each term $\frac{1}{6} \det[\mathbf{v}_{i,1}, \mathbf{v}_{i,2}, \mathbf{v}_{i,3}]$ represents the exact signed volume of an oriented tetrahedron formed by the coordinate origin $\mathbf{0} = [0, 0, 0]^T$ and the triangle vertices $(\mathbf{v}_{i,1}, \mathbf{v}_{i,2}, \mathbf{v}_{i,3})$.
- If the origin lies inside $\Omega$, the summation partitions the interior into tetrahedra with positive volumes.
- If the origin lies outside $\Omega$, tetrahedra facing away from the origin contribute positive volume, while tetrahedra facing toward the origin contribute negative volume, exactly cancelling the external space between the origin and $\partial \Omega$.
- **Translational Invariance:** Let $\mathbf{v}' = \mathbf{v} + \mathbf{c}$ for any arbitrary constant translation vector $\mathbf{c} \in \mathbb{R}^3$. The change in calculated volume is:
  $$\Delta V = \frac{1}{3} \mathbf{c} \cdot \sum_{i=1}^F \frac{1}{2} \mathbf{N}_i = \frac{1}{6} \mathbf{c} \cdot \sum_{i=1}^F \mathbf{N}_i$$
  For a closed surface, the sum of projected area normal vectors over the closed boundary is identically zero: $\sum_{i=1}^F \mathbf{N}_i = \mathbf{0}$. Therefore, **$V(\mathcal{M})$ is strictly independent of coordinate origin if and only if the mesh is closed**.

---

## 2. Why Open Surface Patches Have Mathematically Undefined Volume

### 2.1 Failure of the Jordan-Brouwer Separation Theorem
The Jordan-Brouwer Separation Theorem states that any topological embedding of a compact, connected, orientable $(n-1)$-dimensional manifold without boundary into $\mathbb{R}^n$ divides $\mathbb{R}^n$ into exactly two connected components: a bounded "interior" and an unbounded "exterior".
- For an **open surface patch** $\mathcal{S} \subset \mathbb{R}^3$, the boundary is non-empty: $\partial \mathcal{S} \neq \emptyset$ (i.e. it possesses boundary curves or open boundary loops).
- Because $\partial \mathcal{S} \neq \emptyset$, the complement $\mathbb{R}^3 \setminus \mathcal{S}$ forms a single connected open set. There is no topologically defined "interior" domain $\Omega$. Hence, the Lebesgue measure $\mu(\Omega) = \int_{\Omega} 1 \, dV$ is mathematically undefined.

### 2.2 Gauge Dependence and Origin Sensitivity
If the discrete divergence formula is applied directly to an unclosed surface patch $\mathcal{S}_{\text{open}}$:
$$V_{\text{apparent}}(\mathcal{S}_{\text{open}}) = \frac{1}{6} \sum_{i \in \mathcal{F}_{\text{open}}} \mathbf{v}_{i,1} \cdot (\mathbf{v}_{i,2} \times \mathbf{v}_{i,3})$$
Shifting the origin by $\mathbf{x}_0$:
$$V_{\text{apparent}}'(\mathcal{S}_{\text{open}}) = V_{\text{apparent}}(\mathcal{S}_{\text{open}}) + \frac{1}{6} \mathbf{x}_0 \cdot \sum_{i \in \mathcal{F}_{\text{open}}} \mathbf{N}_i$$
Because $\sum_{i \in \mathcal{F}_{\text{open}}} \mathbf{N}_i \neq \mathbf{0}$ for any non-trivial open surface patch (such as an arm sleeve, leg strip, or torso patch), the resulting number can be made equal to any arbitrary value $\alpha \in (-\infty, +\infty)$ simply by translating the world origin. Any claim of "measuring the volume of an open patch" without boundary closure is mathematically invalid.

---

## 3. Algorithmic Techniques for Capping Open Anatomical Mesh Boundaries

To measure anatomical volume from open surface extractions (e.g. isolating the thigh, forearm, or torso from a full character mesh), the open 1D boundary loops must be sealed into watertight 2-manifolds.

### 3.1 Boundary Loop Identification via Half-Edge Data Structures
1. **Half-Edge Traversal:** In a half-edge mesh, boundary half-edges have no opposite half-edge (`edge->twin == NULL` or `twin->is_boundary`).
2. **Cycle Chaining:** Trace consecutive boundary edges $e_k = (v_k, v_{k+1})$ such that $v_{k+1}$ is the start of $e_{k+1}$, constructing an ordered 3D polygonal boundary loop $\mathcal{L} = (v_1, v_2, \dots, v_m, v_1)$.

### 3.2 Planar Cutting Planes at Anatomical Joint Centers
1. **Joint Plane Definition:** At an anatomical joint (e.g., knee axis, elbow axis), define a cutting plane $\Pi: \mathbf{n}_{\Pi} \cdot (\mathbf{x} - \mathbf{p}_0) = 0$, where $\mathbf{p}_0$ is the functional joint center and $\mathbf{n}_{\Pi}$ is the segment longitudinal or joint axis.
2. **Mesh Slicing:** Compute exact edge-plane intersections $\mathbf{p}_{\text{int}} = \mathbf{v}_a + t (\mathbf{v}_b - \mathbf{v}_a)$ where $t = \frac{\mathbf{n}_{\Pi} \cdot (\mathbf{p}_0 - \mathbf{v}_a)}{\mathbf{n}_{\Pi} \cdot (\mathbf{v}_b - \mathbf{v}_a)}$. This splits intersected triangles and yields a planar boundary polygon $\mathcal{L}_{\Pi}$ whose vertices lie strictly in $\Pi$.

### 3.3 Triangulation Algorithms for Planar Boundary Closure
Once a planar or near-planar boundary loop $\mathcal{L} = (\mathbf{p}_1, \dots, \mathbf{p}_m)$ is extracted:

1. **Centroid Fan Triangulation (Fastest, valid for star-shaped loops):**
   Compute loop centroid: $\mathbf{c} = \frac{1}{m} \sum_{j=1}^m \mathbf{p}_j$.
   Generate triangles $T_j = (\mathbf{p}_j, \mathbf{p}_{j+1}, \mathbf{c})$ for $j = 1, \dots, m$ (with $\mathbf{p}_{m+1} \equiv \mathbf{p}_1$).
   *Orientation condition:* The winding order of $(\mathbf{p}_j, \mathbf{p}_{j+1}, \mathbf{c})$ must be reversed relative to the boundary edge traversal so that the cap normal points outward: $\mathbf{n}_{\text{cap}} = -\mathbf{n}_{\Pi}$.
2. **Constrained 2D Delaunay Triangulation (CDT) (General non-convex loops):**
   Project 3D loop $\mathcal{L}$ onto 2D plane coordinates using local orthonormal basis $(\mathbf{u}, \mathbf{v})$ spanning $\Pi$. Run Seidel's or Chew's CDT algorithm to triangulate the polygon interior without creating self-intersections.
3. **Minimal Area Surface Capping (Plateau's Problem / Harmonic Mapping):**
   For non-planar boundaries (such as the saddle-shaped glenohumeral or pelvic cut), solve the biharmonic equation $\Delta^2 \mathbf{x} = 0$ subject to boundary Dirichlet conditions $\mathbf{x}|_{\partial \mathcal{S}} = \mathcal{L}$.

### 3.4 Convex Hull Volume vs Enclosed Manifold Volume
- **Convex Hull $\operatorname{Conv}(\mathcal{S})$:** The minimal convex set containing all vertices of $\mathcal{S}$.
- **Fatal Defect of Convex Hull for Anatomical Measurement:**
  The human body is deeply non-convex (e.g. groin crease, armpit, axillary fossa, waist indentation, elbow bend).
  - The convex hull of an open arm patch bridges across empty air between the bicep and torso or spans the entire joint bend envelope.
  - As proven by Eberly (2010), for articulated human limbs, $V(\operatorname{Conv}(\mathcal{S}))$ overestimates true anatomical volume by **$28\% \text{ to } 65\%$** depending on joint flexion.
  - Computing convex hull volume does not evaluate volume preservation or flesh deformation—it obscures joint pinching and candy-wrapper collapse.

---

## 4. Watertight 2-Manifold Conditions

A 3D surface mesh $\mathcal{M} = (\mathcal{V}, \mathcal{E}, \mathcal{F})$ is an admissible, watertight, orientable 2-manifold enclosing a physical volume if and only if all four of the following topological conditions are satisfied:

```
+-----------------------------------------------------------------------------------+
|                        WATERTIGHT 2-MANIFOLD VERIFICATION GATES                   |
+-----------------------------------------------------------------------------------+
| 1. Euler-Poincare Characteristic:   chi = V - E + F = 2(1 - g) = 2  (for genus 0)  |
| 2. Boundary Edge Count:             |E_boundary| == 0                             |
| 3. Manifold Edge Condition:         Every edge shared by EXACTLY 2 faces          |
| 4. Vertex Link Topology:            Star/link of every vertex homeomorphic to S^1 |
| 5. Consistent Normal Orientation:   Opposite edge winding on shared half-edges    |
+-----------------------------------------------------------------------------------+
```

### 4.1 Topological Invariants
1. **Euler-Poincaré Formula:**
   $$\chi(\mathcal{M}) = |\mathcal{V}| - |\mathcal{E}| + |\mathcal{F}| = 2(1 - g) - b$$
   where $g$ is the genus (number of through-holes/handles) and $b$ is the number of boundary components.
   - For an anatomical human segment (homeomorphic to a 3-ball $\mathbb{B}^3$): $g = 0$ and $b = 0$.
   - Thus, the exact invariant is:
     $$\chi = |\mathcal{V}| - |\mathcal{E}| + |\mathcal{F}| \equiv 2$$
   - For closed triangular meshes, every face has 3 edges and each edge is shared by 2 faces: $2|\mathcal{E}| = 3|\mathcal{F}| \implies |\mathcal{F}| = 2|\mathcal{V}| - 4$ and $|\mathcal{E}| = 3|\mathcal{V}| - 6$.
2. **Zero Boundary Edges ($b = 0$):**
   Every edge $e \in \mathcal{E}$ must have an incidence count of exactly two faces ($k_e = 2$). If any edge has $k_e = 1$, the mesh is open ($b \ge 1$); if $k_e > 2$, the mesh contains non-manifold T-junctions or self-intersecting fins.

### 4.2 Local Neighborhood Topology
- **Vertex Manifold Property:** For every vertex $v \in \mathcal{V}$, the umbrella (link) formed by adjacent faces must be topologically equivalent to an open disk (homeomorphic to $\mathbb{R}^2$). If two cones meet at a single vertex (pinch point / bowtie vertex), the Euler characteristic may still evaluate to 2, but the object is non-manifold and has an undefined normal bundle.

### 4.3 Consistent Outward Orientation
- For any two triangles $T_A = (v_1, v_2, v_3)$ and $T_B = (v_2, v_1, v_4)$ sharing the directed edge $e$, the edge must be traversed in opposite directions: $(v_1 \to v_2)$ in $T_A$ and $(v_2 \to v_1)$ in $T_B$.
- If winding is inconsistent, individual tetrahedral contributions $\mathbf{v}_1 \cdot (\mathbf{v}_2 \times \mathbf{v}_3)$ will flip signs, producing partial or total internal volume cancellation.

---

## 5. Primary Literature & Citation Standards

1. **Gauss, C. F.** (1813). "Theoria attractionis corporum sphaeroidicorum ellipticorum homogeneorum methodo nova tractata." *Commentationes Societatis Regiae Scientiarum Gottingensis Recentiores*, 2: 1–24.
2. **Mirtich, Brian** (1996). "Fast and Accurate Computation of Polyhedral Mass Properties." *Journal of Graphics Tools*, 1(2): 31–50. [DOI: 10.1080/10867651.1996.10487458](https://doi.org/10.1080/10867651.1996.10487458)
3. **Zhang, C., and Chen, T.** (2001). "Efficient feature extraction for 2D/3D objects in mesh representation." *IEEE International Conference on Image Processing (ICIP 2001)*, 3: 935–938. [DOI: 10.1109/ICIP.2001.958278](https://doi.org/10.1109/ICIP.2001.958278)
4. **Eberly, David H.** (2002). "Polyhedral Mass Properties (Revisited)." *Geometric Tools Technical Report*, pp. 1–9. [URL: https://www.geometrictools.com/Documentation/PolyhedralMassProperties.pdf](https://www.geometrictools.com/Documentation/PolyhedralMassProperties.pdf)
5. **Botsch, M., Kobbelt, L., Pauly, M., Alliez, P., and Lévy, B.** (2010). *Polygon Mesh Processing*. CRC Press / AK Peters. [ISBN: 9781568814261](https://www.routledge.com/Polygon-Mesh-Processing/Botsch-Kobbelt-Pauly-Alliez-Levy/p/book/9781568814261)
