# Track 5: Real-Time WebGL, glTF 2.0 Skinning Limits & GPU Vertex Cache Budgeting

## 1. Executive Summary & Hardware Constraints

Deploying rigged, animated 3D characters to real-time WebGL / WebGPU runtimes (such as Three.js, Babylon.js, PlayCanvas) via the Khronos glTF 2.0 specification exposes severe architectural constraints not present in desktop DCC tools:
1. **GPU Uniform Vector Limits:** OpenGL ES 3.0 / WebGL 2.0 hardware guarantees as few as `MAX_VERTEX_UNIFORM_VECTORS = 128` on mobile chipsets, restricting matrix palette storage.
2. **Skinning Influence Limits:** Standard glTF pipelines bind a maximum of 4 bone influences per vertex (`JOINTS_0`, `WEIGHTS_0`), dropping secondary weights unless 8-influence extensions are explicitly wired.
3. **Post-Transform Vertex Cache (PTVC) Stalls:** Inefficient triangle index ordering forces the GPU vertex shader to execute repeatedly for the same vertex, doubling or tripling transformation overhead.
4. **Draw Call Dominance:** In single-threaded JavaScript runtimes, CPU driver overhead from state changes and draw calls (`gl.drawElements`) bottlenecks frame delivery long before raw polygon rasterization limits are reached.

```
       UNOPTIMIZED GLTF PIPELINE                         OPTIMIZED MESHOPT / WEBGL PIPELINE
   +---------------------------------+               +--------------------------------------+
   |  Mesh with 16 Bone Weights/Vert |               |  Clamped to 4 Weights / Vert         |
   |  (glTF drops weights >4)        |               |  (Normalized: sum(w) = 1.0)          |
   +----------------+----------------+               +------------------+-------------------+
                    |                                                   |
                    v                                                   v
   +---------------------------------+               +--------------------------------------+
   |  Random Triangle Index Order    |               |  Forsyth / Tipsify Cache Reordered   |
   |  (ATVR ~ 2.6 - 3.0)             |               |  (ATVR ~ 0.65 - 0.75, 4x shader save)|
   +----------------+----------------+               +------------------+-------------------+
                    |                                                   |
                    v                                                   v
   +---------------------------------+               +--------------------------------------+
   |  42 Separate Sub-Meshes/Draws   |               |  Consolidated Uber-Mesh              |
   |  (42 gl.drawElements, CPU Bound)|               |  (1 Skinned Draw Call, Texture Array)|
   +---------------------------------+               +--------------------------------------+
```

---

## 2. glTF 2.0 Skinning Architecture & WebGL Shader Limits

### 2.1 The Khronos glTF 2.0 Skinning Specification
Under the Khronos glTF 2.0 standard, skeletal deformation is defined via accessor pairs:
- **`JOINTS_0`:** 4-component vector of joint indices (encoded as `UNSIGNED_BYTE` $[0, 255]$ or `UNSIGNED_SHORT` $[0, 65535]$).
- **`WEIGHTS_0`:** 4-component vector of normalized weights (encoded as `FLOAT`, or normalized `UNSIGNED_BYTE` / `UNSIGNED_SHORT`).

#### The 4-Weight Constraint vs. 8-Weight Extension:
Standard glTF exporters and web loaders evaluate a single set of 4 joint influences per vertex:
$$v' = \sum_{j=0}^{3} \text{WEIGHTS\_0}[j] \cdot \left( \text{JointMatrix}[\text{JOINTS\_0}[j]] \cdot \text{InverseBindMatrix}[\text{JOINTS\_0}[j]] \right) \cdot v$$
- **8-Weight Skinning:** Requires a secondary set of accessors: `JOINTS_1` and `WEIGHTS_1`. 
- **WebGL Shader Penalty:** Supporting 8 weights doubles the matrix multiplications in the vertex shader from 4 to 8 per vertex:
  $$W_{\text{skin8}} = 8 \times 16 \text{ Multiplies} = 128 \text{ scalar operations per vertex}$$
- In Three.js, 8-influence skinning requires enabling `#define NUM_BONE_INFLUENCES 8` (available in r151+). If an asset authored in Blender with 6 or 8 bone influences is exported to a 4-influence pipeline without normalization, glTF exporters truncate the 5th through 8th weights. This results in **unnormalized weights** ($\sum_{j=0}^3 w_j < 1.0$), causing vertices to collapse toward the world origin during animation.

### 2.2 GPU Uniform Limits & Bone Matrix Textures
In WebGL vertex shaders, bone matrices are accessed via one of two mechanisms:

#### Mechanism 1: Uniform Array of $4 \times 4$ Matrices
```glsl
uniform mat4 u_boneMatrices[MAX_BONES];
```
- **Hardware Constraint:** WebGL 1.0 / 2.0 specifications guarantee only:
  $$\text{GL\_MAX\_VERTEX\_UNIFORM\_VECTORS} \ge 128 \text{ (mobile)}, \quad 1024 \text{ (desktop)}$$
- A single $4 \times 4$ float matrix consumes 4 uniform vectors (`vec4`). If 16 uniform vectors are reserved for model-view-projection matrices, lighting, and material parameters:
  $$\text{Available Vectors} = 128 - 16 = 112 \implies \text{Max Bones} = \left\lfloor \frac{112}{4} \right\rfloor = \mathbf{28 \text{ bones}}$$
  *(Even using $3 \times 4$ affine matrices, max bones is limited to $\lfloor 112 / 3 \rfloor = 37$ bones).*
- **Failure Mode:** Attempting to render an 80-bone human skeleton on a low-end mobile browser using uniform arrays results in a shader compilation crash (`GL_OUT_OF_RESOURCES`).

#### Mechanism 2: Floating-Point Data Texture (Three.js Standard)
Three.js bypasses uniform limits by serializing bone matrices into a floating-point `DataTexture` (`RGBA / FLOAT` or `RGBA / HALF_FLOAT`):
- Texture width: 4 pixels per bone (each pixel encodes one row of the $4 \times 4$ matrix).
- Vertex shader fetches matrices via `texelFetch`:
```glsl
mat4 getBoneMatrix(const in float i) {
  int j = int(i) * 4;
  vec4 row0 = texelFetch(boneTexture, ivec2(j, 0), 0);
  vec4 row1 = texelFetch(boneTexture, ivec2(j + 1, 0), 0);
  vec4 row2 = texelFetch(boneTexture, ivec2(j + 2, 0), 0);
  vec4 row3 = texelFetch(boneTexture, ivec2(j + 3, 0), 0);
  return mat4(row0, row1, row2, row3);
}
```
- **Capacity:** Can store hundreds of bones ($>1024$) in a single $256 \times 256$ texture.
- **Performance Trade-Off:** Introduces vertex texture fetch (VTF) latency. On mobile GPUs with weak texture units, 4 texture fetches per vertex can stall the vertex shader pipeline.

---

## 3. GPU Post-Transform Vertex Cache (PTVC) Optimization

### 3.1 Hardware Architecture of the Post-Transform Cache
Modern GPU rasterizers include a small First-In, First-Out (FIFO) or Least-Recently-Used (LRU) cache that stores the output of the vertex shader (clip-space position, transformed normals, UVs).
- **Cache Size:** Typically **$16$ to $32$ entries** on mobile GPUs (Qualcomm Adreno, ARM Mali, Apple Silicon); up to $64$ entries on desktop GPUs (NVIDIA Ada Lovelace, AMD RDNA3).
- **Cache Hit Mechanics:** When the GPU processes triangle indices $(i_1, i_2, i_3)$, it queries the PTVC for index $i_k$. If $i_k$ is present in the cache, the vertex shader invocation is completely skipped, and transformed attributes are fetched from the fast cache.

### 3.2 Average Transform to Vertex Ratio (ATVR)
The efficiency of triangle indexing is quantified by the Average Transform to Vertex Ratio:
$$\text{ATVR} = \frac{\text{Total Vertex Shader Invocations}}{\text{Total Unique Vertices}}$$
- **Theoretical Worst Case:** Disconnected triangles (no index sharing) $\implies \mathbf{\text{ATVR} = 3.0}$.
- **Unoptimized Random Indexing:** Typical raw DCC export $\implies \mathbf{\text{ATVR} \approx 2.2 - 2.8}$.
- **Theoretical Lower Bound for Manifold Quad/Triangle Meshes:** $\mathbf{\text{ATVR} \approx 0.5 - 0.7}$ (since each vertex in a regular manifold is shared by approximately 6 triangles).

```
   VERTEX SHADER WORKLOAD AS A FUNCTION OF ATVR (50,000 Vertex Character)
   +--------------------------------------------------------------------+
   | Unoptimized Mesh (ATVR = 2.6):  130,000 Vertex Shader Invocations  |
   | Optimized Mesh   (ATVR = 0.65):  32,500 Vertex Shader Invocations  |
   +--------------------------------------------------------------------+
   [SAVINGS: 75% Reduction in GPU Vertex Processing Workload]
```

### 3.3 Re-Indexing Algorithms: Forsyth vs. Tipsify

#### 1. Forsyth Algorithm (Tom Forsyth, 2006)
Calculates a dynamic score for each vertex $v$ based on its position in the simulated cache and its remaining unused valence:
$$\text{Score}(v) = \text{CacheScore}(v) + \text{ValenceScore}(v)$$
Where:
- $\text{CacheScore}(v)$:
  $$\text{CacheScore}(v) = \begin{cases} 
  0.75, & \text{if position in cache } \le 3 \\
  (1.0 - \frac{\text{pos} - 3}{\text{CacheSize} - 3})^{1.5}, & \text{if } 3 < \text{pos} < \text{CacheSize} \\
  0.0, & \text{if not in cache}
  \end{cases}$$
- $\text{ValenceScore}(v)$: Favors vertices with few remaining un-drawn triangles to clear them from memory:
  $$\text{ValenceScore}(v) = 2.0 \times (\text{UnusedTriangles}(v))^{-0.5}$$
The algorithm iteratively picks the triangle with the highest sum of vertex scores, pushes it to the output index buffer, and updates the simulated cache state.

#### 2. Tipsify Algorithm (Sander, Nehab, Barczak, SIGGRAPH 2007)
Seminal Literature: *"Fast Triangle Reordering for Vertex Locality and Overdraw"*, ACM TOG / SIGGRAPH 2007 (`doi:10.1145/1276377.1276439`).
- Uses a linear-time ($O(V + T)$) depth-first traversal of the dual triangle adjacency graph.
- Generates vertex clusters matching the exact hardware cache size $K = 32$.
- **Performance:** Faster to compute than Forsyth; ideal for large-scale procedural geometry or runtime asset ingestion.

#### 3. Modern Implementation: `meshoptimizer` & `EXT_meshopt_compression`
Arseny Kapoulkine's open-source `meshoptimizer` library implements an industrial-grade variant of Forsyth's algorithm:
- `meshopt_optimizeVertexCache(indices, indices, index_count, vertex_count)`: Re-indexes triangles for PTVC.
- `meshopt_optimizeVertexFetch(destination, indices, index_count, vertices, vertex_count, vertex_size)`: Reorders the vertex buffer itself so that vertices appear in memory in the exact sequential order they are first referenced by indices, maximizing CPU/GPU **Pre-Transform Cache (L1/L2)** locality.

---

## 4. Draw Call Batching vs. Polygon Count

### 4.1 The JavaScript WebGL CPU Overhead Equation
In WebGL / Three.js, rendering performance is predominantly CPU-bound due to the single-threaded JavaScript execution context and browser GPU driver validation overhead.

Total frame execution time $T_{\text{frame}}$ is modeled as:
$$T_{\text{frame}} = T_{\text{JS\_Update}} + N_{\text{draw}} \cdot \tau_{\text{driver}} + \sum_{k=1}^{N_{\text{draw}}} \left( V_k \cdot \tau_{\text{vertex}} + P_k \cdot \tau_{\text{frag}} \right)$$
Where:
- $N_{\text{draw}}$ is the total number of draw calls.
- $\tau_{\text{driver}}$ is the browser driver state-switch overhead per draw call (typically $0.02 - 0.05\text{ ms}$ on mobile Chromium / Safari).
- $V_k$ is the vertex count of batch $k$.

#### The Draw Call Cliff:
- A scene with **1 draw call of 200,000 polygons** takes $\sim 2.1\text{ ms}$ total frame time ($\mathbf{60\text{ FPS}}$).
- A scene with **200 draw calls of 1,000 polygons** ($200,000$ total polygons) takes $200 \times 0.04\text{ ms} = 8.0\text{ ms}$ in CPU driver validation alone, leading to frame drops ($\mathbf{\sim 35 - 45\text{ FPS}}$).

```
   SCENARIO A: MODULAR CHARACTER SPLIT (40 Draw Calls)
   [Head Mesh]   -> Bind Material -> Set Bone Texture -> gl.drawElements (0.04 ms)
   [Eyes Mesh]   -> Bind Material -> Set Bone Texture -> gl.drawElements (0.04 ms)
   [Jacket Mesh] -> Bind Material -> Set Bone Texture -> gl.drawElements (0.04 ms)
   [Pants Mesh]  -> Bind Material -> Set Bone Texture -> gl.drawElements (0.04 ms)
   ... [Total Driver Overhead: ~1.6 ms CPU stall per frame]

   SCENARIO B: CONSOLIDATED UBER-MESH (1 Draw Call)
   [Merged Body] -> Bind Uber-Material -> Set Bone Texture -> gl.drawElements (0.04 ms)
   ... [Total Driver Overhead: 0.04 ms]
```

### 4.2 Three.js / WebGL Character Optimization Rules
1. **Material Atlas Consolidation:** Merge diffuse, roughness, and normal maps into a unified texture atlas, allowing separate body parts (head, limbs, torso, clothes) to be combined into a single `SkinnedMesh`.
2. **2D Texture Arrays (`TEXTURE_2D_ARRAY` in WebGL 2.0):** If resolution cannot be compromised by an atlas, bind textures as layers in a 2D texture array and pass a vertex attribute `material_layer_id` to sample in the fragment shader.
3. **Instanced Skinned Meshes:** For background crowds, use instanced matrix palette skinning (`InstancedMesh` with custom bone transform buffers) rather than individual animated `SkinnedMesh` objects.

---

## 5. WebGL / glTF Asset Budgeting & Optimization Rubric

| Budget Category | Mobile WebGL Target | Desktop WebGL Target | Failure Symptom if Exceeded |
| :--- | :--- | :--- | :--- |
| **Max Triangles (Hero Character)** | $15,000 - 25,000$ | $50,000 - 100,000$ | Thermal throttling, battery drain, low fill-rate |
| **Max Bone Count** | $40 - 64$ bones | $90 - 128$ bones | Shader uniform exhaustion / VTF stall |
| **Max Influences per Vertex** | Exactly 4 (`JOINTS_0`) | Exactly 4 (`JOINTS_0`) | Unnormalized weight collapse on export |
| **Draw Calls per Character** | 1 (Merged SkinnedMesh) | $2 - 4$ (Translucent hair/eyes) | JavaScript event loop frame stall ($<30\text{ FPS}$) |
| **Target ATVR (Vertex Cache)** | $\le 0.75$ | $\le 0.70$ | Vertex shader bound; low fill performance |
| **Vertex Attributes** | 32-byte stride (Interleaved) | 32-48 byte stride | Cache misses during GPU attribute fetch |
| **Texture Format** | KTX2 / Basis Universal UASTC | KTX2 UASTC or BC7 | Out-of-Memory (OOM) tab crash on iOS Safari |

---

## 6. Primary Sources & Industry Standards

1. **Khronos Group.** (2017-2024). *glTF™ 2.0 Specification: § 3.7.4 Skins*. `https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#skins`.
   - *Key Contribution:* Standard specification for `JOINTS_0`, `WEIGHTS_0`, inverse bind matrices, and skeletal skinning evaluation in WebGL.
2. **Forsyth, T.** (2006). *Linear-Speed Vertex Cache Optimisation*. Official Technical Blog: `https://tomforsyth1000.github.io/papers/fast_vert_cache_opt.html`.
   - *Key Contribution:* Algorithmic formulation of scoring heuristics for post-transform vertex cache optimization.
3. **Sander, P. V., Nehab, D., & Barczak, J.** (2007). *Fast triangle reordering for vertex locality and overdraw*. In Proceedings of the 2007 ACM SIGGRAPH symposium on Interactive 3D graphics and games (I3D '07), 157–164. `doi:10.1145/1276377.1276439`.
   - *Key Contribution:* Tipsify algorithm for linear-time vertex cache and overdraw optimization.
4. **Kapoulkine, A.** (2018-2024). *meshoptimizer: High-performance mesh processing library*. GitHub Repository: `https://github.com/zeux/meshoptimizer`.
   - *Key Contribution:* Authoritative implementation of vertex cache, vertex fetch, and overdraw re-indexing used in `EXT_meshopt_compression`.
5. **Cabello, R. (mrdoob) et al.** (2010-2024). *Three.js Source Code: `src/objects/SkinnedMesh.js` and `src/renderers/shaders/ShaderChunk/skinning_vertex.glsl.js`*. GitHub Repository: `https://github.com/mrdoob/three.js`.
