# Research Plan: Blender Mesh Deformity, Vertex & Polygon Optimization

**Run Slug**: `blender-deformity-vertex-polygon-optimization-2026-09`  
**Date**: 2026-09-23  
**Domain**: `motion` / `tech`  
**Target Blueprint**: `docs/research/motion/BLENDER_DEFORMITY_VERTEX_POLYGON_OPTIMIZATION_RESEARCH_BLUEPRINT.md`  

---

## 1. Problem Statement & Scope

In high-performance character animation, WebGL/Three.js export, and offline rendering, mesh deformity quality is directly constrained by vertex budget, edge flow topology, and Blender modifier stack execution. Sub-optimal topology creates pinching, volume loss, self-intersecting folds, and massive CPU/GPU evaluation overhead in Blender's dependency graph (Depsgraph).

We need rigorous, benchmarked research on:
1. **Deformity Edge Flow & Topology Engineering**: Optimal loop distribution for hinges (knees/elbows), ball-and-socket joints (shoulders/hips), and facial expressions; pole management (3-poles, 5-poles/E-poles, avoiding N-poles on deformation zones).
2. **Corrective Deformation Systems in Blender**: Corrective Shape Keys (driven by bone rotations / Pose Space Deformation), Corrective Smooth Modifier (Laplacian smooth vs Scale-Preserving), Surface Deform modifier, and Lattice binding.
3. **Vertex & Polygon Optimization Algorithms**: Quad vs Triangulation trade-offs for deformation, Decimate modifier mechanics (Quadric Error Metric / Garland-Heckbert 1997 vs Unsubdivide), Remesh topologies, normal/tangent space displacement baking.
4. **Blender Viewport & Depsgraph Performance**: Modifier stack evaluation order (Armature vs Subsurf), GPU OpenSubdiv compute shaders, vertex cache locality optimization (Forsyth / Tipsify algorithms), and zero-weight vertex pruning from vertex groups.
5. **Real-Time / Export Budgeting (Three.js / WebGL / Game Engines)**: Deformer limits (max bones per vertex / 4-weight limit, uniform vs non-uniform joint scaling), vertex attribute packing, draw call batching, and glTF/USD export fidelity.

---

## 2. Research Tracks & Hypotheses

### Track 1: Deformable Mesh Topology, Edge Loops & Pole Placement
- **Focus**: Minimum edge loop count for 90° and 135° flexion without self-intersection (3-loop span vs 5-loop span), spans over articular joints, positioning of 5-poles (E-poles) into neutral non-bending flesh, avoiding 6+ star poles.
- **Authority**: Computer graphics topology literature (Hippydrome, Bay Raitt, Pixar subdivision surfaces), Blender Foundation animation guides.

### Track 2: Corrective Deformation Techniques (PSD & Smooth Modifiers)
- **Focus**: Pose Space Deformation (Lewis et al. SIGGRAPH 2000), Corrective Smooth modifier (factor, repeat, bind coords), Laplacian mesh deformation (Sorkine et al. 2004), driver configuration for bone transforms.

### Track 3: Vertex/Poly Decimation & Geometric Simplification Algorithms
- **Focus**: Quadric Error Metric (QEM, Garland & Heckbert 1997), edge collapse with boundary and volume preservation constraints, Unsubdivide modifier on even quad grids, LOD generation.

### Track 4: Blender Depsgraph & Viewport Acceleration
- **Focus**: Blender Dependency Graph evaluation architecture, multithreaded modifier evaluation, GPU Subsurf acceleration (compute shaders), memory layout of mesh runtime buffers (`Mesh`, `BKE_mesh`), pruning unused vertex groups and zero-weight vertex tables.

### Track 5: WebGL / Real-time Deformer Constraints (Three.js & glTF Export)
- **Focus**: 4-weights per vertex standard (`SKIN_WEIGHTS_0`, `SKIN_JOINTS_0`), GPU matrix palette skinning limits, draw call overhead vs vertex count, attribute interleaving.

---

## 3. Evidence Collection & Provenance Hierarchy
- **Tier 1-A (Alexandria Academic)**: SIGGRAPH, IEEE TVCG, ACM TOG papers on QEM simplification, dual quaternion and implicit skinning, subdivision surfaces.
- **Tier 1-B (Official Blender & Industry Standards)**: Blender C++ source code (`source/blender/blenkernel/intern/modifier.c`, `armature.cc`, `depsgraph`), Khronos glTF 2.0 Skinning specification.
- **Tier 2 (Squeezed Evidence)**: Persist to `docs/research/runs/blender-deformity-vertex-polygon-optimization-2026-09/findings_<track>.md`.
- **Tier 3 (Master Blueprint)**: Synthesize in `docs/research/motion/BLENDER_DEFORMITY_VERTEX_POLYGON_OPTIMIZATION_RESEARCH_BLUEPRINT.md`.
