# Track 3: MRI & CT Tomographic Mathematics & Volumetric Integration — Tier 2 Evidence Extract

*Run: `human-anatomical-volume-proportions-2026-09` · Date: 2026-09-23 · Track: 3 · Primary Authorities: Cavalieri (1635), Lorensen & Cline (1987), Chernyaev (1995), Schneider et al. (1996), Gundersen & Jensen (1987), Cruz-Orive (1993), Hounsfield (1973)*

---

## 1. Stereology and the Cavalieri Principle for Volume Estimation

The mathematical extraction of physical anatomical volumes from cross-sectional tomographic imaging (Magnetic Resonance Imaging [MRI] and Computed Tomography [CT]) relies upon stereological integration, grounded historically in the Cavalieri Principle.

### 1.1 The Cavalieri Formulation
Bonaventura Cavalieri (1635) established that if two solids have equal cross-sectional areas at all heights parallel to a given base plane, they possess identical volumes. In modern stereology (Gundersen & Jensen 1987), this is formalized as an unbiased estimator for an arbitrary 3D volume $\Omega$:
Let the volume be systematically sectioned by a stack of parallel planes spaced at a constant distance (slice thickness / slice interval) $T$. The first section plane position is chosen with a uniform random start $z_0 \sim \mathcal{U}[0, T)$.
The Cavalieri volume estimator $\hat{V}_{\text{Cav}}$ is:
$$\boxed{\hat{V}_{\text{Cav}} = T \cdot \sum_{i=1}^{n} A_i}$$
where:
- $T$ is the distance between consecutive section planes (slice interval in $\text{mm}$ or $\text{cm}$).
- $n$ is the total number of sections traversing the anatomical region.
- $A_i$ is the segmented 2D cross-sectional area of the anatomical structure on slice $i$ ($\text{mm}^2$ or $\text{cm}^2$).

### 1.2 Higher-Order Numerical Quadrature Variations
When cross-sectional areas vary rapidly along the axial trajectory (e.g. at the apex of the skull or the distal ends of phalanges), higher-order interpolations yield reduced truncation error:
1. **Simpson's Rule Formulation (Parabolic Profile):**
   $$V_{\text{Simp}} = \frac{T}{3} \left[ A_1 + 4A_2 + 2A_3 + 4A_4 + \dots + 4A_{n-1} + A_n \right]$$
2. **Frustum / Truncated Cone Quadrature (Between Adjacent Slices):**
   $$V_{\text{Frustum}} = \sum_{i=1}^{n-1} \frac{T}{3} \left( A_i + \sqrt{A_i A_{i+1}} + A_{i+1} \right)$$

### 1.3 Error Estimation: Gundersen-Jensen Coefficient of Error (CE)
Because consecutive serial slices are not statistically independent, the variance $\operatorname{Var}(\hat{V})$ cannot be evaluated using independent random sampling formulas. Gundersen and Jensen (1987), with refinements by Cruz-Orive (1993), derived the unbiased Coefficient of Error ($\text{CE}$):
$$\text{CE}(\hat{V}) = \frac{\sqrt{\operatorname{Var}(\hat{V})}}{\hat{V}}$$
The variance estimator is decomposed into the systematic sectioning noise $\text{Var}_{\text{syst}}$ and the area estimation variance $\text{Var}_{\text{area}}$:
$$\operatorname{Var}(\hat{V}) = T^2 \left[ \frac{3(A - \text{Var}_S) - 4B + C}{12} + \sum_{i=1}^n \operatorname{Var}(A_i) \right]$$
where:
$$A = \sum_{i=1}^n A_i^2, \quad B = \sum_{i=1}^{n-1} A_i A_{i+1}, \quad C = \sum_{i=1}^{n-2} A_i A_{i+2}$$
- **Clinical & Anthropometric Precision Rule:** For human body segments (thigh, trunk, brain, forearm), choosing $n \approx 10 \text{ to } 15$ slices with $T = 5 \text{ to } 10\text{ mm}$ systematically achieves a $\text{CE} \le 1.5\% - 3.0\%$, exceeding the accuracy requirements for character physics calibration.

### 1.4 Partial Volume Effect (PVE) Correction
In clinical CT/MRI, voxels have finite volume ($\Delta x \cdot \Delta y \cdot T$, typically $0.5 \times 0.5 \times 2.0\text{ mm}^3$). When an anatomical boundary passes through a voxel:
- The measured voxel signal $I_{\text{meas}}$ is an area-weighted linear mixture of two or more tissues:
  $$I_{\text{meas}} = f_{\text{tissue}} I_{\text{tissue}} + (1 - f_{\text{tissue}}) I_{\text{background}}$$
  where $f_{\text{tissue}} \in [0, 1]$ is the true tissue volume fraction.
- **Correction Algorithms:**
  1. *Sub-Voxel Gaussian Mixture Modeling (GMM):* Fits probability distributions $p(I | c_k)$ for each tissue class $k$, computing soft assignment weights $w_{ik} = P(c_k | I_i)$. The Cavalieri area on slice $j$ is integrated as:
     $$A_j = (\Delta x \cdot \Delta y) \sum_{p \in \text{slice } j} w_{p, \text{tissue}}$$
  2. *Isosurface Sub-Voxel Tracing:* Instead of binary voxel thresholding, the zero-crossing contour is interpolated linearly along voxel edges, preventing discrete staircase over-estimation of perimeter and area.

---

## 2. Marching Cubes Algorithm: From Volumetric Tomography to Watertight 2-Manifolds

To convert discrete 3D scalar tomography fields $S(x,y,z)$ into continuous polygonal boundary surfaces for graphics engines, the Marching Cubes algorithm is employed.

```
       v7 +--------+ v6
         /|       /|
        / |      / |
    v4 +--------+ v5|
       |  |     |  |
       | v3+----+---+ v2
       | /      | /
       |/       |/
    v0 +--------+ v1
```

### 2.1 The Lorensen & Cline (1987) Formulation
- **Authority:** Lorensen, W. E., and Cline, H. E. (1987). "Marching Cubes: A High Resolution 3D Surface Construction Algorithm." *ACM SIGGRAPH Computer Graphics*, 21(4): 163–169.
- **Algorithm Pipeline:**
  1. Divide the 3D tomography volume into a uniform grid of elementary cubic cells defined by 8 adjacent voxel values $(v_0, \dots, v_7)$.
  2. For a specified threshold isovalue $\sigma_{\text{iso}}$, evaluate the 8-bit index:
     $$\text{Index} = \sum_{k=0}^{7} b_k 2^k, \quad \text{where } b_k = \begin{cases} 1 & \text{if } S(v_k) \ge \sigma_{\text{iso}} \\ 0 & \text{if } S(v_k) < \sigma_{\text{iso}} \end{cases}$$
  3. The 8-bit index spans $2^8 = 256$ possible topological configurations. By rotation and inversion symmetry, Lorensen & Cline reduced these to **14 canonical base cases**.
  4. For edges that intersect the isosurface, calculate vertex positions via linear interpolation:
     $$\mathbf{p}_{\text{edge}} = \mathbf{p}_A + \frac{\sigma_{\text{iso}} - S(\mathbf{p}_A)}{S(\mathbf{p}_B) - S(\mathbf{p}_A)} (\mathbf{p}_B - \mathbf{p}_A)$$
  5. Compute outward normals via central difference gradient:
     $$\mathbf{n}(\mathbf{p}) = -\frac{\nabla S(\mathbf{p})}{\|\nabla S(\mathbf{p})\|}, \quad \nabla S = \left[ \frac{S_{x+1} - S_{x-1}}{2 \Delta x}, \frac{S_{y+1} - S_{y-1}}{2 \Delta y}, \frac{S_{z+1} - S_{z-1}}{2 \Delta z} \right]^T$$

### 2.2 Topological Ambiguities and the Chernyaev (1995) MC33 Resolution
- **The Defect of Classic Marching Cubes:** Lorensen & Cline's original 14 cases suffered from **facial ambiguities** (where adjacent cubes share a face with alternating signs) and **internal ambiguities**. Under standard lookup tables, adjacent cubes make inconsistent topological choices, generating non-manifold edges, T-junctions, and literal holes in the extracted mesh, destroying the watertight 2-manifold requirement!
- **Chernyaev MC33 Resolution:**
  - **Authority:** Chernyaev, E. (1995). "Marching Cubes 33: Construction of Topologically Correct Isosurfaces." *Technical Report CN/95-17*, CERN, Geneva.
  - Chernyaev demonstrated that 33 extended topological configurations are required, utilizing bilinear face deciders and trilinear interior deciders.
  - **Guaranteed Manifold Property:** Modern implementations of MC33 (e.g. Lewiner et al. 2003, VTK `vtkFlyingEdges3D`, CGAL) guarantee that every generated edge is incident to exactly two triangles, boundary edge count is identically 0, and the resulting mesh satisfies $\chi = V - E + F = 2(1-g)$.

---

## 3. Computed Tomography Hounsfield Units (HU) to Physical Density Mapping

Computed Tomography measures the linear X-ray attenuation coefficient $\mu(x,y,z)$ of materials relative to water.

### 3.1 The Hounsfield Unit (HU) Definition
Sir Godfrey Hounsfield (1973) standardized the CT number scale:
$$\text{HU} = 1000 \times \frac{\mu - \mu_{\text{water}}}{\mu_{\text{water}}}$$
where $\mu_{\text{water}}$ is the linear attenuation coefficient of pure water at the effective photon energy of the CT X-ray beam ($\approx 70\text{ keV}$ for a $120\text{ kVp}$ tube potential), and $\mu_{\text{air}} \approx 0 \implies \text{HU}_{\text{air}} = -1000$.

### 3.2 Canonical Reference Hounsfield Values of Human Tissues

| Tissue / Material | Hounsfield Unit (HU) Range | Typical Mean HU | Physical Density $\rho$ ($\text{g/cm}^3$) | Density ($\text{kg/m}^3$) |
| :--- | :--- | :--- | :--- | :--- |
| **Air** | $-1000$ | $-1000$ | $0.0012$ | $1.2$ |
| **Lung Tissue (Inflated)** | $-850 \text{ to } -600$ | $-700$ | $0.25 - 0.40$ | $250 - 400$ |
| **Adipose / Subcutaneous Fat**| $-120 \text{ to } -80$ | $-100$ | $0.92 - 0.94$ | $920 - 940$ |
| **Water** | $0 \pm 5$ | $0$ | $1.000$ | $1,000$ |
| **Cerebrospinal Fluid (CSF)** | $+10 \text{ to } +20$ | $+15$ | $1.005 - 1.010$ | $1,005 - 1,010$ |
| **Blood (Venous / Arterial)** | $+30 \text{ to } +45$ | $+38$ | $1.050 - 1.060$ | $1,050 - 1,060$ |
| **Skeletal Muscle / Lean Tissue**| $+35 \text{ to } +55$ | $+45$ | $1.055 - 1.065$ | $1,055 - 1,065$ |
| **Parenchymal Organs (Liver/Kidney)**| $+40 \text{ to } +65$ | $+55$ | $1.050 - 1.070$ | $1,050 - 1,070$ |
| **Trabecular / Cancellous Bone**| $+150 \text{ to } +400$ | $+250$ | $1.15 - 1.30$ | $1,150 - 1,300$ |
| **Cortical Bone** | $+1000 \text{ to } +3000$| $+1600$ | $1.70 - 1.95$ | $1,700 - 1,950$ |

### 3.3 Stoichiometric Calibration (Schneider et al. 1996)
In clinical radiation physics and patient-specific biomechanics, converting CT Hounsfield Units to true physical mass density $\rho$ requires stoichiometric calibration to account for photoelectric and Compton scattering differences.
- **Reference:** Schneider, U., Pedroni, E., and Lomax, A. (1996). "The calibration of CT Hounsfield units for radiotherapy treatment planning." *Physics in Medicine and Biology*, 41(1): 111–124. [DOI: 10.1088/0031-9155/41/1/009](https://doi.org/10.1088/0031-9155/41/1/009)

The calibrated relationship is modeled as a piecewise linear function:
$$\rho(\text{HU}) = a_k \cdot \text{HU} + b_k \quad (\text{in g/cm}^3)$$

```
Density (g/cm^3)
   ^
2.0|                                                / (Cortical Bone)
   |                                               /
1.5|                                              /
   |                                 .-----------'
1.0|               .----------------' (Soft tissue/muscle: ~1.06)
   |              / (Fat: ~0.92)
0.5|             / (Lung: ~0.35)
   |            /
0.0+-----------+--------------------+--------------------+--------> HU
 -1000        -100                  0                  +1000   +2000
```

#### Piecewise Calibration Coefficients (Diagnostic 120 kVp Beam):
1. **Air to Lung / Soft Tissue Interval ($-1000 \le \text{HU} < -100$):**
   $$\rho = 1.000 + 0.00100 \times \text{HU}$$
   *(At $\text{HU} = -1000$, $\rho = 0.000\text{ g/cm}^3$; at $\text{HU} = -100$, $\rho = 0.900\text{ g/cm}^3$)*
2. **Fat to Muscle / Soft Tissue Interval ($-100 \le \text{HU} \le +100$):**
   $$\rho = 1.018 + 0.00055 \times \text{HU}$$
   *(At $\text{HU} = 0$, $\rho = 1.018\text{ g/cm}^3$; at $\text{HU} = +45$ [muscle], $\rho \approx 1.043 - 1.055\text{ g/cm}^3$)*
3. **Bone and Dense Matrix Interval ($\text{HU} > +100$):**
   $$\rho = 1.018 + 0.00048 \times \text{HU}$$
   *(At $\text{HU} = +1000$, $\rho \approx 1.498\text{ g/cm}^3$; at $\text{HU} = +1800$, $\rho \approx 1.882\text{ g/cm}^3$)*

---

## 4. Volumetric Mass & Inertial Integration

With the continuous density field $\rho(x,y,z)$ calibrated across the 3D voxel lattice $\mathcal{V}_{\text{grid}}$, segment physical mass $M$, center of mass $\mathbf{r}_{\text{CoM}}$, and the 6-component inertia tensor $\mathbf{I}$ are evaluated directly by discrete Riemann summation over voxels:

### 4.1 Segment Mass Integration
$$M = \iiint_{\Omega} \rho(x,y,z) \, dx \, dy \, dz \approx \sum_{i,j,k \in \Omega} \rho(\text{HU}_{i,j,k}) \cdot (\Delta x \cdot \Delta y \cdot \Delta z)$$
where $V_{\text{voxel}} = \Delta x \cdot \Delta y \cdot \Delta z$ is the invariant voxel volume.

### 4.2 Segment Center of Mass (CoM)
$$\mathbf{r}_{\text{CoM}} = \frac{1}{M} \iiint_{\Omega} \mathbf{x} \, \rho(\mathbf{x}) \, dV \approx \frac{\sum_{i,j,k \in \Omega} \mathbf{x}_{i,j,k} \cdot \rho(\text{HU}_{i,j,k}) \cdot V_{\text{voxel}}}{M}$$

### 4.3 Segment Inertia Tensor
$$\mathbf{I} = \begin{bmatrix} I_{xx} & I_{xy} & I_{xz} \\ I_{yx} & I_{yy} & I_{yz} \\ I_{zx} & I_{zy} & I_{zz} \end{bmatrix}$$
where:
$$I_{xx} = \sum_{i,j,k \in \Omega} \left[ (y - y_{\text{CoM}})^2 + (z - z_{\text{CoM}})^2 \right] \rho_{i,j,k} V_{\text{voxel}}$$
$$I_{xy} = -\sum_{i,j,k \in \Omega} (x - x_{\text{CoM}})(y - y_{\text{CoM}}) \rho_{i,j,k} V_{\text{voxel}}$$
This computational tomography integration establishes the ground truth physical benchmark against which all boundary-mesh and skinning approximations must be verified.

---

## 5. Primary Literature & Citation Standards

1. **Cavalieri, Bonaventura** (1635). *Geometria indivisibilibus continuorum nova quadam ratione promota*. Typis Ferronii, Bononiae.
2. **Gundersen, H. J. G., and Jensen, E. B.** (1987). "The efficiency of systematic sampling in stereology and its prediction." *Journal of Microscopy*, 147(3): 229–263. [DOI: 10.1111/j.1365-2818.1987.tb02837.x](https://doi.org/10.1111/j.1365-2818.1987.tb02837.x)
3. **Cruz-Orive, L. M.** (1993). "Systematic sampling in stereology." *Bulletin of the International Statistical Institute*, 55: 451–468.
4. **Lorensen, W. E., and Cline, H. E.** (1987). "Marching Cubes: A High Resolution 3D Surface Construction Algorithm." *Computer Graphics (ACM SIGGRAPH 87)*, 21(4): 163–169. [DOI: 10.1145/37401.37422](https://doi.org/10.1145/37401.37422)
5. **Chernyaev, Evgeni** (1995). "Marching Cubes 33: Construction of Topologically Correct Isosurfaces." *Technical Report CERN CN/95-17*, CERN. [URL: https://cds.cern.ch/record/292837](https://cds.cern.ch/record/292837)
6. **Schneider, U., Pedroni, E., and Lomax, A.** (1996). "The calibration of CT Hounsfield units for radiotherapy treatment planning." *Physics in Medicine and Biology*, 41(1): 111–124. [DOI: 10.1088/0031-9155/41/1/009](https://doi.org/10.1088/0031-9155/41/1/009)
7. **Hounsfield, G. N.** (1973). "Computerized transverse axial scanning (tomography): Part 1. Description of system." *British Journal of Radiology*, 46(552): 1016–1022. [DOI: 10.1259/0007-1285-46-552-1016](https://doi.org/10.1259/0007-1285-46-552-1016)
