/* kinetics/arap.mjs - THE MORPH (P47 T3 / P38 T5; 43 s43.5; the brief B4). SOURCE OF TRUTH, inlined into the scene-evidence
   player by sync_kinetics.py between KINETICS:BEGIN arap and KINETICS:END. Self-contained (no template symbol).
   Two methods, per doc 43's decision rule:
     METHOD A - vertex-based, for outline-to-outline with modest rotation: resample both closed outlines to one vertex
       count by arc length, ROTATIONALLY ALIGN (argmin_k sum |vA_i - vB_(i+k)|^2 - the step that stops the path twisting
       inside-out), then lerp. Cheap, and it collapses when the morph carries rotation past 90 degrees.
     METHOD B - triangle-based ARAP (Alexa, Cohen-Or & Levin 2000, "As-rigid-as-possible shape interpolation"; the
       cotangent weights after Sorkine & Alexa 2007 - neither on file): one triangulation of the SOURCE outline (a fan from
       the centroid: the outlines we morph are star-shaped about it - a receipt, a plate, the area under a series) is carried
       to the target by the vertex correspondence; per triangle the Jacobian J = D' D^-1 is polar-decomposed IN CLOSED FORM
       (theta = atan2(j21 - j12, j11 + j22), R = rot(theta), S = R^T J); R is interpolated on SO(2) (the angle), S on Sym+(2)
       (its eigenvalues on the log scale, its eigenvector frame by angle), so det J(t) = det R(t) det S(t) = (l1 l2)^t > 0 for
       every t - inversion is impossible, not merely unlikely; the vertices that realise the interpolated Jacobians as well as
       a mesh can are the least-squares solution of the rest mesh's cotangent Laplacian, factored ONCE (dense Cholesky - our
       outlines are a few hundred vertices at most) and back-substituted per frame with the centroid pinned.
   MATCH-CUT INVARIANTS (the brief B4, [DERIVED: :390-396]): centroid shift <= 0.06 W, dominant-axis turn <= 15 deg, bounding
   area min/max >= 0.60 over the window - computed by morphInvariants for the gate (M17), never assumed.
   Everything is a pure function of the two outlines and t. */

export const ARAP = Object.freeze({ N: 96, CENTROID_MAX: 0.06, AXIS_MAX_DEG: 15, AREA_MIN_RATIO: 0.60 });   /* N: the resample count; the three invariants [DERIVED: brief B4] */

const ARAP_TAU = Math.PI * 2;
const arapSub = (a, b) => [a[0] - b[0], a[1] - b[1]];
const arapDot = (a, b) => a[0] * b[0] + a[1] * b[1];

/* ---- outlines -------------------------------------------------------------------------------------------------- */
export const polyArea = (pts) => { let a = 0; for (let i = 0, n = pts.length; i < n; i++) { const p = pts[i], q = pts[(i + 1) % n]; a += p[0] * q[1] - q[0] * p[1]; } return a / 2; };
/* the AREA centroid (the shoelace form) - the shape's mass, not its vertex density; the vertex mean when the area is nil */
export const centroid = (pts) => {
  const n = pts.length; let a = 0, cx = 0, cy = 0, mx = 0, my = 0;
  for (let i = 0; i < n; i++) { const p = pts[i], q = pts[(i + 1) % n], w = p[0] * q[1] - q[0] * p[1]; a += w; cx += (p[0] + q[0]) * w; cy += (p[1] + q[1]) * w; mx += p[0]; my += p[1]; }
  return Math.abs(a) < 1e-9 ? [mx / n, my / n] : [cx / (3 * a), cy / (3 * a)];
};
/* a closed outline resampled to n vertices at equal arc length, starting at its first vertex, wound counter-clockwise */
export const resample = (pts, n = ARAP.N) => {
  let P = pts.slice();
  if (polyArea(P) < 0) P.reverse();
  const m = P.length, seg = [], cum = [0];
  for (let i = 0; i < m; i++) { const L = Math.hypot(...arapSub(P[(i + 1) % m], P[i])); seg.push(L); cum.push(cum[i] + L); }
  const total = cum[m], out = [];
  for (let k = 0; k < n; k++) {
    const s = (k / n) * total; let i = 0;
    while (i < m - 1 && cum[i + 1] < s) i++;
    const u = seg[i] > 0 ? (s - cum[i]) / seg[i] : 0, a = P[i], b = P[(i + 1) % m];
    out.push([a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u]);
  }
  return out;
};
/* the rotational alignment: the cyclic offset k that minimises the summed squared distance, after both centroids are moved to
   the origin (so the alignment is about SHAPE, not position) */
export const alignOffset = (A, B) => {
  const n = A.length, ca = centroid(A), cb = centroid(B); let best = 0, bestD = Infinity;
  for (let k = 0; k < n; k++) {
    let d = 0;
    for (let i = 0; i < n; i++) { const a = A[i], b = B[(i + k) % n]; const dx = (a[0] - ca[0]) - (b[0] - cb[0]), dy = (a[1] - ca[1]) - (b[1] - cb[1]); d += dx * dx + dy * dy; }
    if (d < bestD) { bestD = d; best = k; }
  }
  return best;
};
export const rotate = (B, k) => B.map((_, i) => B[(i + k) % B.length]);
/* METHOD A: the correspondence (resampled, aligned) and the per-vertex lerp */
export const correspond = (src, dst, n = ARAP.N) => { const A = resample(src, n), B0 = resample(dst, n); return { A, B: rotate(B0, alignOffset(A, B0)) }; };
export const lerpShape = (A, B, t) => A.map((a, i) => [a[0] + (B[i][0] - a[0]) * t, a[1] + (B[i][1] - a[1]) * t]);

/* ---- the triangle mesh ------------------------------------------------------------------------------------------ */
/* a fan from the centroid: vertex n is the centre; triangle i = (i, i+1, n). The source and the target share this topology. */
export const fanMesh = (A) => { const n = A.length, tris = []; for (let i = 0; i < n; i++) tris.push([i, (i + 1) % n, n]); return { verts: [...A, centroid(A)], tris }; };
/* the 2x2 Jacobian of a triangle's map from rest (p) to deformed (q): J = D' D^-1 with D = [p1-p0 | p2-p0] */
export const triJacobian = (p0, p1, p2, q0, q1, q2) => {
  const d = [[p1[0] - p0[0], p2[0] - p0[0]], [p1[1] - p0[1], p2[1] - p0[1]]], e = [[q1[0] - q0[0], q2[0] - q0[0]], [q1[1] - q0[1], q2[1] - q0[1]]];
  const det = d[0][0] * d[1][1] - d[0][1] * d[1][0], inv = [[d[1][1] / det, -d[0][1] / det], [-d[1][0] / det, d[0][0] / det]];
  return [[e[0][0] * inv[0][0] + e[0][1] * inv[1][0], e[0][0] * inv[0][1] + e[0][1] * inv[1][1]],
          [e[1][0] * inv[0][0] + e[1][1] * inv[1][0], e[1][0] * inv[0][1] + e[1][1] * inv[1][1]]];
};
export const det2x2 = (J) => J[0][0] * J[1][1] - J[0][1] * J[1][0];
/* the closed-form polar decomposition: J = R S, R a rotation by theta, S symmetric positive-definite (when det J > 0) */
export const polar = (J) => {
  const th = Math.atan2(J[1][0] - J[0][1], J[0][0] + J[1][1]), c = Math.cos(th), s = Math.sin(th);
  /* S = R^T J */
  const S = [[c * J[0][0] + s * J[1][0], c * J[0][1] + s * J[1][1]], [-s * J[0][0] + c * J[1][0], -s * J[0][1] + c * J[1][1]]];
  return { theta: th, S };
};
/* S on Sym+(2): eigen-decompose S = Q diag(l1, l2) Q^T; interpolate log l and the frame angle from the identity */
const arapSymEig = (S) => {
  const a = S[0][0], b = (S[0][1] + S[1][0]) / 2, d = S[1][1], tr = a + d, dt = a * d - b * b, disc = Math.sqrt(Math.max(0, tr * tr / 4 - dt));
  const l1 = tr / 2 + disc, l2 = tr / 2 - disc, phi = Math.abs(b) < 1e-12 && Math.abs(a - d) < 1e-12 ? 0 : 0.5 * Math.atan2(2 * b, a - d);
  return { l1, l2, phi };
};
const arapSymFrom = (l1, l2, phi) => { const c = Math.cos(phi), s = Math.sin(phi); return [[c * c * l1 + s * s * l2, c * s * (l1 - l2)], [c * s * (l1 - l2), s * s * l1 + c * c * l2]]; };
/* the interpolated Jacobian at t: R(t) = rot(t theta), S(t) = Q diag(l1^t, l2^t) Q^T (the frame's angle scaled with t) */
export const jacobianAt = (J, t) => {
  const { theta, S } = polar(J), e = arapSymEig(S);
  const St = arapSymFrom(Math.pow(Math.max(1e-9, e.l1), t), Math.pow(Math.max(1e-9, e.l2), t), e.phi * t);
  const c = Math.cos(theta * t), s = Math.sin(theta * t);
  return [[c * St[0][0] - s * St[1][0], c * St[0][1] - s * St[1][1]], [s * St[0][0] + c * St[1][0], s * St[0][1] + c * St[1][1]]];
};

/* ---- the global step: the cotangent Laplacian of the rest mesh, factored once ------------------------------------- */
const arapCot = (a, b) => arapDot(a, b) / Math.max(1e-12, Math.abs(a[0] * b[1] - a[1] * b[0]));
const arapChol = (M) => {   /* dense, symmetric positive-definite (the pinned Laplacian is) */
  const n = M.length, L = Array.from({ length: n }, () => new Float64Array(n));
  for (let i = 0; i < n; i++) for (let j = 0; j <= i; j++) {
    let s = M[i][j]; for (let k = 0; k < j; k++) s -= L[i][k] * L[j][k];
    if (i === j) { if (s <= 0) throw new Error("the Laplacian is not positive definite (a degenerate triangle?)"); L[i][i] = Math.sqrt(s); }
    else L[i][j] = s / L[j][j];
  }
  return L;
};
const arapSolve = (L, b) => {
  const n = L.length, y = new Float64Array(n), x = new Float64Array(n);
  for (let i = 0; i < n; i++) { let s = b[i]; for (let k = 0; k < i; k++) s -= L[i][k] * y[k]; y[i] = s / L[i][i]; }
  for (let i = n - 1; i >= 0; i--) { let s = y[i]; for (let k = i + 1; k < n; k++) s -= L[k][i] * x[k]; x[i] = s / L[i][i]; }
  return x;
};
/* METHOD B, prepared once for a pair of corresponded outlines: the mesh, each triangle's target Jacobian, the factored
   system. The vertex with index `pin` (the centroid) is fixed; its position is interpolated between the two centroids. */
/* THE STRIP MESH - for a prop that becomes the AREA UNDER A SERIES. A fan from one centre inverts on a jagged series (the
   area under a line with deep dips is not star-shaped about any one point - measured on the holdings page: 12 of 96 fan
   triangles flipped). A strip is the right topology: n columns, each a top vertex over a bottom vertex; two triangles per
   column; every triangle keeps its orientation as long as both shapes are x-monotone strips - a till-roll tab and the area
   under a time series both are, whatever the series does. The outline is the top edge left to right, the bottom edge back. */
export const stripMesh = (top, bot) => {
  const n = top.length, tris = [];
  for (let i = 0; i + 1 < n; i++) tris.push([i, n + i, i + 1], [i + 1, n + i, n + i + 1]);
  return { verts: [...top, ...bot], tris, n };
};
export const stripOutline = (verts, n) => [...verts.slice(0, n), ...verts.slice(n, 2 * n).reverse()];
/* the prepared morph for ANY shared-topology mesh: rest verts in `mesh`, target verts `Bv`, one pinned vertex that travels the chord */
export const arapPrepareMesh = (mesh, Bv, pin) => {
  const V = mesh.verts, n = V.length;
  const J = mesh.tris.map(([i, j, k]) => triJacobian(V[i], V[j], V[k], Bv[i], Bv[j], Bv[k]));
  const W = Array.from({ length: n }, () => new Float64Array(n));
  const edges = [];
  mesh.tris.forEach(([i, j, k], ti) => {
    const P = [V[i], V[j], V[k]], id = [i, j, k];
    for (let e = 0; e < 3; e++) {
      const a = id[e], b = id[(e + 1) % 3], o = P[(e + 2) % 3];
      const w = 0.5 * arapCot(arapSub(P[e], o), arapSub(P[(e + 1) % 3], o)), wc = Math.max(1e-4, w);
      W[a][b] += wc; W[b][a] += wc; edges.push({ a, b, w: wc, tri: ti });
    }
  });
  const M = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? W[i].reduce((s, v) => s + v, 0) : -W[i][j])));
  const keep = [...Array(n).keys()].filter((i) => i !== pin);
  const Lc = arapChol(keep.map((i) => keep.map((j) => M[i][j])));
  return { mesh, J, edges, keep, pin, Lc, M, cA: V[pin], cB: Bv[pin], n, strip: mesh.n || 0, Bv };
};
export const arapPrepare = (A, B, o = {}) => {
  /* o.centre: the target's fan centre when its area centroid does not see the whole outline; the rest mesh keeps the source's centroid */
  const mesh = fanMesh(A), V = mesh.verts, n = V.length, pin = n - 1, Bv = [...B, o.centre || centroid(B)];
  const J = mesh.tris.map(([i, j, k]) => triJacobian(V[i], V[j], V[k], Bv[i], Bv[j], Bv[k]));
  /* the cotangent weights on the rest mesh; the least-squares energy sum_t w_ij |(q_j - q_i) - J_t (p_j - p_i)|^2 over the
     triangle's three edges gives L q = b with L the weighted Laplacian */
  const W = Array.from({ length: n }, () => new Float64Array(n));
  const edges = [];
  mesh.tris.forEach(([i, j, k], ti) => {
    const P = [V[i], V[j], V[k]], id = [i, j, k];
    for (let e = 0; e < 3; e++) {
      const a = id[e], b = id[(e + 1) % 3], o = P[(e + 2) % 3];   /* the edge a-b, the opposite vertex o */
      const w = 0.5 * arapCot(arapSub(P[e], o), arapSub(P[(e + 1) % 3], o));
      const wc = Math.max(1e-4, w);   /* a clamp keeps the system positive definite on a thin fan */
      W[a][b] += wc; W[b][a] += wc; edges.push({ a, b, w: wc, tri: ti });
    }
  });
  const M = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? W[i].reduce((s, v) => s + v, 0) : -W[i][j])));
  /* pin the centroid: strike its row and column, keep the reduced system */
  const keep = [...Array(n).keys()].filter((i) => i !== pin);
  const Mr = keep.map((i) => keep.map((j) => M[i][j]));
  const Lc = arapChol(Mr);
  return { mesh, J, edges, keep, pin, Lc, M, cA: V[pin], cB: Bv[pin], n };
};
/* the vertices at t: solve for the outline (the pinned centroid moves on the chord between the two centroids) */
export const arapAt = (prep, t) => {
  const { mesh, J, edges, keep, pin, Lc, M, cA, cB, n } = prep, V = mesh.verts;
  const Jt = J.map((Jk) => jacobianAt(Jk, t));
  const cx = cA[0] + (cB[0] - cA[0]) * t, cy = cA[1] + (cB[1] - cA[1]) * t;
  const bx = new Float64Array(n), by = new Float64Array(n);
  for (const e of edges) {   /* each edge's target vector J_t (p_b - p_a), weighted, into both endpoints' rows */
    const d = arapSub(V[e.b], V[e.a]), Jk = Jt[e.tri], tx = Jk[0][0] * d[0] + Jk[0][1] * d[1], ty = Jk[1][0] * d[0] + Jk[1][1] * d[1];
    bx[e.b] += e.w * tx; by[e.b] += e.w * ty; bx[e.a] -= e.w * tx; by[e.a] -= e.w * ty;
  }
  /* move the pinned vertex's known position to the right-hand side */
  const rx = keep.map((i) => bx[i] - M[i][pin] * cx), ry = keep.map((i) => by[i] - M[i][pin] * cy);
  const sx = arapSolve(Lc, rx), sy = arapSolve(Lc, ry);
  const out = new Array(n);
  keep.forEach((i, r) => { out[i] = [sx[r], sy[r]]; }); out[pin] = [cx, cy];
  return { verts: out, outline: prep.strip ? stripOutline(out, prep.strip) : out.slice(0, n - 1), jacobians: Jt };
};
/* the smallest det J(t) over the triangles (> 0 is the guarantee) and the smallest det of the SOLVED mesh's triangles */
export const minDet = (prep, t) => {
  const s = arapAt(prep, t), V = prep.mesh.verts;
  let target = Infinity, solved = Infinity;
  prep.mesh.tris.forEach(([i, j, k], ti) => { target = Math.min(target, det2x2(s.jacobians[ti])); solved = Math.min(solved, det2x2(triJacobian(V[i], V[j], V[k], s.verts[i], s.verts[j], s.verts[k]))); });
  return { target, solved };
};

/* ---- the invariants (the brief B4) ------------------------------------------------------------------------------ */
/* the polygon's second moments about its area centroid (the shoelace forms) - the SHAPE's inertia, not its vertices' spread
   (a strip's two rows of vertices would read as a vertical axis by vertex covariance; by area it is the strip's length) */
export const inertia = (pts) => {
  const c = centroid(pts), n = pts.length; let ixx = 0, iyy = 0, ixy = 0, a = 0;
  for (let i = 0; i < n; i++) {
    const p = pts[i], q = pts[(i + 1) % n], x0 = p[0] - c[0], y0 = p[1] - c[1], x1 = q[0] - c[0], y1 = q[1] - c[1], w = x0 * y1 - x1 * y0;
    a += w; ixx += w * (x0 * x0 + x0 * x1 + x1 * x1); iyy += w * (y0 * y0 + y0 * y1 + y1 * y1); ixy += w * (x0 * y1 + 2 * x0 * y0 + 2 * x1 * y1 + x1 * y0);
  }
  const sgn = a < 0 ? -1 : 1;   /* orientation-free */
  return { xx: sgn * ixx / 12, yy: sgn * iyy / 12, xy: sgn * ixy / 24, area: Math.abs(a) / 2 };
};
export const dominantAxis = (pts) => {   /* the angle of the area's major principal axis, in [-pi/2, pi/2) */
  const I = inertia(pts);
  let ang = 0.5 * Math.atan2(2 * I.xy, I.xx - I.yy); if (ang >= Math.PI / 2) ang -= Math.PI; if (ang < -Math.PI / 2) ang += Math.PI; return ang;
};
/* the extent of an outline along a direction (radians): max - min of the projection */
export const extentAlong = (pts, ang) => { const c = Math.cos(ang), s = Math.sin(ang); let lo = Infinity, hi = -Infinity; for (const p of pts) { const v = p[0] * c + p[1] * s; lo = Math.min(lo, v); hi = Math.max(hi, v); } return hi - lo; };
export const bbox = (pts) => { let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity; for (const p of pts) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]); } return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 }; };
/* over sampled frames of an outline (t = 0..1): the three invariants and their verdicts against the dials */
/* the bounding area in a given frame: the oriented box along `ang` (a prop turned to the chart's axis must not be charged for the
   screen-axis box its tilt inflates - the brief's "bounding area" is the shape's extent, read in the target's principal frame) */
export const orientedArea = (pts, ang) => extentAlong(pts, ang) * extentAlong(pts, ang + Math.PI / 2);
export const morphInvariants = (frames, W, o = {}) => {
  const P = Object.assign({}, ARAP, o), first = frames[0], last = frames[frames.length - 1];
  const c0 = centroid(first), c1 = centroid(last), shift = Math.hypot(c1[0] - c0[0], c1[1] - c0[1]) / Math.max(1, W);
  let da = Math.abs(dominantAxis(last) - dominantAxis(first)); if (da > Math.PI / 2) da = Math.PI - da;
  const ang = dominantAxis(last), areas = frames.map((f) => orientedArea(f, ang)), ratio = Math.min(...areas) / Math.max(1e-9, Math.max(...areas));
  return { centroid_shift: shift, centroid_ok: shift <= P.CENTROID_MAX, axis_deg: da * 180 / Math.PI, axis_ok: da * 180 / Math.PI <= P.AXIS_MAX_DEG,
           area_ratio: ratio, area_ok: ratio >= P.AREA_MIN_RATIO };
};
/* the SVG path of an outline */
export const outlinePath = (pts) => pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ") + " Z";
