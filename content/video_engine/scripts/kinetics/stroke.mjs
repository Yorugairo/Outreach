/* kinetics/stroke.mjs - the curvature-reparameterised stroke (42 s42.1; FINDING-the-animation-math s1; 47 s1 rows
   1-3). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN stroke
   and KINETICS:END (P43 T2), after ease - it uses minJerk. Behind kinetics.curvature_stroke.
   The defect: stroke-dashoffset linear in time is a constant-velocity pen - a sliding mask, not a hand. The law
   (Viviani & Terzuolo 1982; Lacquaniti, Terzuolo & Viviani 1983): v = gamma * (|kappa| + kappa0)^(-1/3), the
   two-thirds power law, with kappa0 = (v_max / gamma)^-3 so a straight line (kappa -> 0) keeps a finite speed.
   Width and ink density couple to the same profile (nib pooling): w = 1 + lambda_w * (v_max / v)^alpha_w.
   The endpoint envelope psi is realised on the clock as Flash & Hogan's quintic (minJerk): ds/du = v(s) * minJerk'(u)
   is zero at both ends with zero acceleration, so the stroke starts and stops from rest - the variational result
   rather than a hand-shaped ramp. t(s) = integral ds / v is tabulated by the trapezoid rule and s(t) is its inverse
   per table segment (Newton on a piecewise-linear t(s) lands in one step). The dials - gamma, kappa0, lambda_w,
   alpha_w, the smoothing window, the sample pitch - are ours to tune (42 s42.5), not findings.
   DOM-free: the caller samples the path at equal arclength (getPointAtLength) and hands the points in. */
import { minJerk } from "./ease.mjs";

export const STROKE = Object.freeze({ KAPPA0: 1 / 300, GAMMA: 1, LAMBDA_W: 0.12, ALPHA_W: 1, SMOOTH: 2, SAMPLE_PX: 6, MIN_N: 24, MAX_N: 240 });

/* Menger curvature of three points, 1 / circumradius: 0 on a straight, finite on a collapsed triple. */
export const menger = (a, b, c) => {
  const abx = b.x - a.x, aby = b.y - a.y, bcx = c.x - b.x, bcy = c.y - b.y, acx = c.x - a.x, acy = c.y - a.y;
  const cross = Math.abs(abx * bcy - aby * bcx);
  const den = Math.hypot(abx, aby) * Math.hypot(bcx, bcy) * Math.hypot(acx, acy);
  return den > 0 ? 2 * cross / den : 0;
};

/* The profile of one stroke from its samples along the path: arclength s, curvature kappa (box-smoothed - a flattened
   curve is noisy at the sample pitch), speed v, width factor w, and the clock t(s) normalised to [0, 1]. */
export const strokeProfile = (pts, o = {}) => {
  const P = Object.assign({}, STROKE, o), n = pts.length;
  const s = new Float64Array(n), raw = new Float64Array(n), kappa = new Float64Array(n), v = new Float64Array(n), w = new Float64Array(n), t = new Float64Array(n);
  for (let i = 1; i < n; i++) s[i] = s[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y);
  for (let i = 1; i < n - 1; i++) raw[i] = menger(pts[i - 1], pts[i], pts[i + 1]);
  if (n > 2) { raw[0] = raw[1]; raw[n - 1] = raw[n - 2]; }
  for (let i = 0; i < n; i++) {
    let acc = 0, cnt = 0;
    for (let j = Math.max(0, i - P.SMOOTH); j <= Math.min(n - 1, i + P.SMOOTH); j++) { acc += raw[j]; cnt++; }
    kappa[i] = cnt ? acc / cnt : 0;
  }
  const vMax = P.GAMMA * Math.pow(P.KAPPA0, -1 / 3);
  for (let i = 0; i < n; i++) { v[i] = P.GAMMA * Math.pow(kappa[i] + P.KAPPA0, -1 / 3); w[i] = 1 + P.LAMBDA_W * Math.pow(vMax / v[i], P.ALPHA_W); }
  for (let i = 1; i < n; i++) t[i] = t[i - 1] + (s[i] - s[i - 1]) * 0.5 * (1 / v[i - 1] + 1 / v[i]);
  const T = n > 1 && t[n - 1] > 0 ? t[n - 1] : 1;
  for (let i = 0; i < n; i++) t[i] /= T;
  let wArea = 0;   /* P72 T46b: the width's arclength-weighted mean - the stroke's own weight, which the brush holds at its authored width */
  for (let i = 1; i < n; i++) wArea += (s[i] - s[i - 1]) * 0.5 * (w[i - 1] + w[i]);
  const L = n ? s[n - 1] : 0, wMean = L > 0 ? wArea / L : (n ? w[0] : 1);
  return { n, L, s, kappa, v, w, t, vMax, wMean };
};

const bracket = (arr, x, n) => { let lo = 0, hi = n - 1; while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (arr[mid] <= x) lo = mid; else hi = mid; } return [lo, hi]; };

/* The arclength drawn at normalised time u in [0, 1]: the quintic clock, then the inverse of the tabulated t(s). */
export const strokeS = (prof, u) => {
  const tau = minJerk(u), { t, s, n } = prof;
  if (n < 2 || tau <= 0) return 0;
  if (tau >= 1) return prof.L;
  const [lo, hi] = bracket(t, tau, n), dt = t[hi] - t[lo];
  return dt > 0 ? s[lo] + (tau - t[lo]) * (s[hi] - s[lo]) / dt : s[lo];
};

/* A profile column (prof.v, prof.w, prof.kappa) at arclength x, linear between samples. */
export const strokeAt = (prof, arr, x) => {
  const { s, n } = prof;
  if (n < 2 || x <= 0) return n ? arr[0] : 0;
  if (x >= s[n - 1]) return arr[n - 1];
  const [lo, hi] = bracket(s, x, n), ds = s[hi] - s[lo];
  return ds > 0 ? arr[lo] + (x - s[lo]) * (arr[hi] - arr[lo]) / ds : arr[lo];
};

/* P72 T46b (R26-106 (a) / R26-365 (a), grill Q4 (a)) - THE WIDTH THE PEN DRAWS. `pts` the profile's own samples along the
   path (the caller's equal-arclength points, strokeProfile's input), `s1` the arclength drawn so far, `sw` the stroke's
   authored width, `tip` the path's own point at s1 (else the chord between the two samples about it). The drawn prefix is
   every sample short of s1 and the tip; each carries a HALF-width sw / 2 x w(s) / wMean - prof.w (the same profile the
   pen's speed comes from, read at the sample by strokeAt) about its arclength-weighted mean, so the WHOLE stroke carries
   the authored weight (its ink area is the constant-width stroke's) and the profile only moves ink out of the fast
   straights into the slow curves, where the nib pools. DOM-free. */
export const strokeWidths = (prof, pts, s1, sw, tip = null) => {
  const L = prof.L, x = Math.max(0, Math.min(L, +s1 || 0)), out = [], hw = [], half = (+sw || 0) / 2, wm = prof.wMean || 1;
  if (!(x > 0) || prof.n < 2) return { pts: out, s: 0, hw };
  for (let i = 0; i < prof.n && prof.s[i] < x - 1e-9; i++) { out.push({ x: pts[i].x, y: pts[i].y }); hw.push(half * strokeAt(prof, prof.w, prof.s[i]) / wm); }
  let q = tip;
  if (!q) {
    const [lo, hi] = bracket(prof.s, x, prof.n), ds = prof.s[hi] - prof.s[lo], u = ds > 0 ? (x - prof.s[lo]) / ds : 0;
    q = { x: pts[lo].x + u * (pts[hi].x - pts[lo].x), y: pts[lo].y + u * (pts[hi].y - pts[lo].y) };
  }
  out.push({ x: q.x, y: q.y }); hw.push(half * strokeAt(prof, prof.w, x) / wm);
  return { pts: out, s: x, hw };
};

/* ... and its OUTLINE: each point offset along its normal by its half-width, out along one side and back along the other
   (the tangent a central difference, one-sided at the ends; a repeated point keeps the tangent before it). The caller
   closes it with a round cap at each end - the marker's nib. */
export const strokeOutline = (pts, hw) => {
  const n = pts.length, left = [], right = [];
  let tx = 1, ty = 0;
  for (let i = 0; i < n; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)], dx = b.x - a.x, dy = b.y - a.y, m = Math.hypot(dx, dy);
    if (m > 1e-9) { tx = dx / m; ty = dy / m; }
    left.push({ x: pts[i].x - ty * hw[i], y: pts[i].y + tx * hw[i] });
    right.push({ x: pts[i].x + ty * hw[i], y: pts[i].y - tx * hw[i] });
  }
  return left.concat(right.reverse());
};
