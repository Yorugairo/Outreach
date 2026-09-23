# Research Plan: Human Anatomical Proportions, Segment Volume & Mass, MRI Tomography Math, and 3D Skinning Deformation

**Run Slug**: `human-anatomical-volume-proportions-2026-09`  
**Date**: 2026-09-23  
**Domain**: `motion` / `tech`  
**Target Blueprint**: `docs/research/motion/HUMAN_ANATOMICAL_PROPORTIONS_VOLUME_3D_MODELING_RESEARCH_BLUEPRINT.md`  

---

## 1. Problem Statement & Background

A critical measurement gap was identified in 3D character pipeline evaluation:
> *"The `mhmask-preserve-volume` group has 2,880 positive source vertices, all retained by the evaluated mask stage... Both measured arm/leg patches have zero positive mask weights, so these saved-stack arm/leg measurements evaluate LBS there. No LBS-vs-DQS A/B was performed, and no DQS or preserve-volume benefit is claimed. Volume is **not measured**: each anatomical selection is an open surface patch rather than a justified closed manifold. This is regional geometry evidence only; it does not establish fighter likeness, character art approval, combat impact/choreography quality, T5b, HG2, or readiness for the custom player."*

To solve this, we must establish rigorous anatomical proportions, volumetric measurements, tomographic (MRI/CT) mathematics, closed-manifold boundary mathematics, and 3D skinning deformation standards.

---

## 2. Research Tracks & Hypotheses

### Track 1: Discrete Mesh Manifold Volume & Boundary Math
- **Hypothesis**: An open surface patch has mathematically undefined volume. By constructing planar virtual cutting caps at joint centers or using boundary projection, an open patch can be converted into a watertight 2-manifold where volume is computed deterministically via the discrete divergence theorem:
  $$V = \frac{1}{6} \sum_{i=1}^{F} \mathbf{v}_{i,1} \cdot (\mathbf{v}_{i,2} \times \mathbf{v}_{i,3})$$
- **Focus**: Divergence theorem on triangular meshes, 2-manifold Euler condition ($\chi = V - E + F = 2(1-g)$, boundary edges = 0), virtual capping algorithms, signed volume orientation.

### Track 2: Anthropometric Segment Inertial Parameters (BSIP) & Volume Ratios
- **Hypothesis**: The human body distributes mass and volume across anatomical segments according to validated anthropometric ratios (Dempster 1955, Zatsiorsky-Seluyanov 1983, de Leva 1996 adjustments).
- **Focus**: Segment mass and volume percentages relative to total body mass ($M_{tot}$) and stature ($H$), segment densities ($\text{g/cm}^3$), joint center landmarks, and gender differences.

### Track 3: MRI & CT Tomographic Math & Mass Integration
- **Hypothesis**: Medical imaging calculates true segment volumes and densities using stereological integration (Cavalieri principle) and Marching Cubes, which can directly map Hounsfield Units (HU) to physical density ($\rho$) and mass ($M$).
- **Focus**: Cavalieri principle ($V = T \cdot \sum A_i$), Marching Cubes 33 lookup topology, partial volume effect (PVE) correction, Hounsfield Unit density linear mapping ($\rho = a \cdot \text{HU} + b$).

### Track 4: 3D Skinning Deformation & Volume Preservation (LBS vs DQS)
- **Hypothesis**: Linear Blend Skinning (LBS) suffers from catastrophic candy-wrapper volume collapse at high torsion angles and joint pinching at flexion > 90°. Dual Quaternion Skinning (DQS) preserves cross-sectional volume and area, but vertex groups with zero weights fall back to unmitigated LBS collapse.
- **Focus**: Mathematical formulation of LBS vs DQS (Kavan et al. 2007, 2008), candy-wrapper collapse derivation, Blender Armature modifier "Preserve Volume" mechanics, vertex-mask boundary behavior, implicit skinning (Vaillant et al. 2013).

### Track 5: Stylized & Anime Proportions vs Realistic Volumetric Extrapolation
- **Hypothesis**: Anime and stylized character art alter classical 7.5/8-head proportions (Loomis/Bammes) by compressing torso volume and exaggerating distal limb silhouettes; realistic 3D volumetric reconstruction requires non-uniform scaling laws to preserve mass balance and prevent ballooning.
- **Focus**: Heroic vs Anime head ratios, distal limb silhouette magnification, volumetric scaling laws ($V \propto s_x s_y s_z$), impact physics translation.

---

## 3. Evidence Collection & Provenance Hierarchy
- **Tier 1-A (Alexandria Academic)**: Search peer-reviewed literature in arXiv (`cs.GR`, `cs.CV`), IEEE TVCG, ACM TOG, Journal of Biomechanics, Radiology.
- **Tier 1-B (Official Engineering & Gov Specs)**: Blender source code / manuals, W3C, NIH / NLM Visible Human Project.
- **Tier 2 (Squeezed Evidence)**: Persist to `docs/research/runs/human-anatomical-volume-proportions-2026-09/findings_<track>.md`.
- **Tier 3 (Master Blueprint)**: Synthesize in `docs/research/motion/HUMAN_ANATOMICAL_PROPORTIONS_VOLUME_3D_MODELING_RESEARCH_BLUEPRINT.md`.
