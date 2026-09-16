/* kinetics/morph_a.mjs - THE MORPH, METHOD A (P50 T12; doc 43 s43.5 "Method A - vertex-based"). SOURCE OF TRUTH,
   inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN morph_a and KINETICS:END, AFTER
   arap - it imports arap.mjs's ring tools (the resample, the rotational alignment, the triangle Jacobian).
   Doc 43's four steps, in order:
     1. RING-NORMALISE - one orientation (counter-clockwise by the shoelace) and one start vertex (the lowest-then-
        leftmost), so two rings that describe the same outline are described the same way. Without it the lerp
        crosses the ring against itself and the shape turns inside out.
     2. RESAMPLE both rings to N vertices by ARC LENGTH (arap.resample).
     3. ROTATIONAL ALIGNMENT - argmin_k sum ||v_A,i - v_B,(i+k)||^2 (arap.alignOffset, through arap.correspond):
        the step that stops the path twisting. It is a SHAPE alignment: both centroids are moved to the origin first.
     4. A direct vertex lerp per frame, reconstructed as CUBIC Beziers (centripetal Catmull-Rom, alpha = 0.5) - the
        interpolated ring is drawn as a curve, not as 96 straight chords.
   Method A is cheap and exact at both ends, and it collapses when the morph carries real rotation (past 90 deg the
   vertex lerp crosses the centre and the area goes to zero) - which is why the compiler refuses a pair whose
   principal axes turn more than ARAP.AXIS_MAX_DEG, and why METHOD B (arap.mjs) exists for the rest.
   Everything here is a pure function of the two rings and t. */
import { polyArea, resample, alignOffset, rotate, triJacobian, det2x2 } from "./arap.mjs";

export const MORPH_A = Object.freeze({
  N: 96,        /* the resample count - ARAP.N, so a pair can be rendered by BOTH methods and read side by side */
  ALPHA: 0.5,   /* the Catmull-Rom knot parameterisation: 0.5 is centripetal, the only alpha that can neither cusp nor
                   self-intersect between two knots (Yuksel, Schaefer & Keyser 2011) - the ring is unevenly spaced the
                   moment it is lerped, so uniform (alpha 0) would loop where the vertices bunch */
  EPS: 1e-9,    /* a degenerate knot gap: below this the Bezier handle sits on the knot rather than dividing by nothing */
});

/* ---- step 1: ring-normalise ------------------------------------------------------------------------------------- */
/* one orientation and one start vertex. Consecutive duplicates are dropped first (a resample divides by the segment
   length). The start vertex is the lowest, then leftmost - a total order, so it is the SAME vertex on any description
   of the ring, and two rings of one shape normalise to one description. */
export const ringNormalise = (pts) => {
  const P = [];
  for (const p of pts) {
    const q = P[P.length - 1];
    if (!q || Math.hypot(p[0] - q[0], p[1] - q[1]) > MORPH_A.EPS) P.push([+p[0], +p[1]]);
  }
  if (P.length > 1) { const a = P[0], z = P[P.length - 1]; if (Math.hypot(a[0] - z[0], a[1] - z[1]) <= MORPH_A.EPS) P.pop(); }
  if (P.length < 3) return P;
  if (polyArea(P) < 0) P.reverse();
  let k = 0;
  for (let i = 1; i < P.length; i++) if (P[i][1] < P[k][1] || (P[i][1] === P[k][1] && P[i][0] < P[k][0])) k = i;
  return rotate(P, k);
};

/* ---- steps 2 + 3: the correspondence ---------------------------------------------------------------------------- */
/* the prepared morph for a pair of rings: both normalised, resampled to n by arc length (unless they already share a
   vertex count that IS the correspondence - a strip built column by column does), then B rotated onto A by the
   alignment. `offset` is the k that won, kept so a test and the gate can read which rotation was chosen.
   `normalise: false` keeps the rings' own vertex order (a caller that built both rings itself, column by column, has
   already made them one description; re-normalising would rotate each ring to its own topmost vertex and hand the
   alignment a puzzle it had solved). Step 3 still runs: on such a pair the offset it returns should be 0, and that IS
   the check that the two descriptions correspond. */
export const morphAPrepare = (src, dst, o = {}) => {
  const resampleRings = o.resample !== false, n = o.n || MORPH_A.N, norm = o.normalise !== false;
  let A = norm ? ringNormalise(src) : src.map((p) => [+p[0], +p[1]]), B = norm ? ringNormalise(dst) : dst.map((p) => [+p[0], +p[1]]);
  if (resampleRings) { A = resample(A, n); B = resample(B, n); }
  else if (A.length !== B.length) throw new Error(`morph_a: ${A.length} and ${B.length} vertices - rings of different counts must be resampled`);
  const offset = alignOffset(A, B);
  return { A, B: rotate(B, offset), offset, n: A.length };
};

/* ---- step 4: the frame ------------------------------------------------------------------------------------------- */
/* the ring at t: the direct vertex lerp. Exact at both ends by construction (t = 0 is A, t = 1 is B). */
export const morphAAt = (prep, t) => {
  const u = t <= 0 ? 0 : (t >= 1 ? 1 : t), { A, B } = prep;
  return { outline: A.map((a, i) => [a[0] + (B[i][0] - a[0]) * u, a[1] + (B[i][1] - a[1]) * u]), u };
};

/* the cubic reconstruction: a closed centripetal Catmull-Rom through every vertex, as Bezier segments. The curve
   INTERPOLATES the ring (each knot is on it), so the shape is the lerp's shape - the cubics only remove the faceting
   96 chords would show at the stage's size. Non-uniform Catmull-Rom -> Bezier (Barry & Goldman 1988's recurrence,
   solved for the two control points), guarded where two knots meet. */
export const morphAPath = (pts, o = {}) => {
  const P = pts, n = P.length, a = o.alpha == null ? MORPH_A.ALPHA : o.alpha;
  if (n < 3) return n ? "M" + P[0][0].toFixed(1) + " " + P[0][1].toFixed(1) : "";
  const d = (p, q) => Math.pow(Math.max(MORPH_A.EPS, Math.hypot(q[0] - p[0], q[1] - p[1])), a);
  let out = "M" + P[0][0].toFixed(1) + " " + P[0][1].toFixed(1);
  for (let i = 0; i < n; i++) {
    const p0 = P[(i - 1 + n) % n], p1 = P[i], p2 = P[(i + 1) % n], p3 = P[(i + 2) % n];
    const d1 = d(p0, p1), d2 = d(p1, p2), d3 = d(p2, p3);
    const b1 = [0, 1].map((k) => {
      const den = 3 * d1 * (d1 + d2);
      return den < MORPH_A.EPS ? p1[k] : (d1 * d1 * p2[k] - d2 * d2 * p0[k] + (2 * d1 * d1 + 3 * d1 * d2 + d2 * d2) * p1[k]) / den;
    });
    const b2 = [0, 1].map((k) => {
      const den = 3 * d3 * (d3 + d2);
      return den < MORPH_A.EPS ? p2[k] : (d3 * d3 * p1[k] - d2 * d2 * p3[k] + (2 * d3 * d3 + 3 * d3 * d2 + d2 * d2) * p2[k]) / den;
    });
    out += " C" + b1[0].toFixed(1) + " " + b1[1].toFixed(1) + " " + b2[0].toFixed(1) + " " + b2[1].toFixed(1)
        + " " + p2[0].toFixed(1) + " " + p2[1].toFixed(1);
  }
  return out + " Z";
};

/* ---- the measurement ------------------------------------------------------------------------------------------- */
/* the smallest triangle determinant between a REST mesh and a frame's vertices, over a shared topology (the strip the
   page's morph is built on, or any mesh whose triangles index both). Method A carries no Jacobian of its own - this is
   what tells you whether its lerp has folded the shape, and it is the same number METHOD B guarantees positive. */
export const morphAMinDet = (rest, verts, tris) => {
  let worst = Infinity;
  for (const [i, j, k] of tris) worst = Math.min(worst, det2x2(triJacobian(rest[i], rest[j], rest[k], verts[i], verts[j], verts[k])));
  return worst;
};

/* the ring's area, for a caller reporting a frame without re-deriving it (the centroid is arap.mjs's `centroid`) */
export const morphAArea = (pts) => Math.abs(polyArea(pts));
