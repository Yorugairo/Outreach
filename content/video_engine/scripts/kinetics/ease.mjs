/* kinetics/ease.mjs - the timing module, part 1 (FINDING-the-animation-math s2; wired 2026-09-05 behind
   kinetics.min_jerk). This file is the SOURCE OF TRUTH: sync_kinetics.py inlines it into the scene-evidence
   player between the KINETICS:BEGIN ease and KINETICS:END markers, so the template stays standalone and
   `node --test` reaches the math (P43 T1). Self-contained on purpose: nothing here reads a template symbol.
   minJerk - Flash & Hogan 1985, the jerk-minimising quintic 10t^3 - 15t^4 + 6t^5: zero velocity AND zero
             acceleration at both ends, so a spatial transition neither snaps nor sags. */
export const minJerk = (u) => { u = Math.min(1, Math.max(0, u)); return u * u * u * (10 - 15 * u + 6 * u * u); };

/* part 2 (P69 T26d, the parent's find): a PATH THROUGH KEYS that does not stop at each one.
   hermite - the cubic Hermite with EXPLICIT end velocities, ported from the rig foundation's `hermite`
             (content/video_engine/projects/martial-matters/.../rig-foundation/rig_math.py:104, d154278 on main,
             test_rig_foundation.py): p(u) = h00 p0 + h10 (v0 T) + h01 p1 + h11 (v1 T), u in [0,1] over T seconds,
             v0 / v1 in units per second. Scalar - one channel; the caller runs one per axis. "The velocity at p1 is
             intentionally allowed to be non-zero."
   hermiteChain - a whole chain of keys: values ps[0..n] at times ts[0..n] (ascending), velocity 0 at the first and
             the last knot (the thing starts from rest and settles), and at each MIDDLE knot the Catmull-Rom velocity
             (p[i+1] - p[i-1]) / (t[i+1] - t[i-1]) - so it passes THROUGH a middle key at speed instead of stopping dead
             (minJerk on every key stops at each waypoint). Clamped to the first / last value outside [t0, tn]. */
export const hermite = (p0, p1, v0, v1, u, T) => {
  u = Math.min(1, Math.max(0, u));
  const u2 = u * u, u3 = u2 * u;
  return (2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * v0 * T + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * v1 * T;
};
export const hermiteChain = (ps, ts, t) => {
  const n = ps.length - 1;
  if (n < 1 || !(t > ts[0])) return ps[0];
  if (t >= ts[n]) return ps[n];
  const vel = (i) => (i <= 0 || i >= n) ? 0 : (ps[i + 1] - ps[i - 1]) / Math.max(1e-9, ts[i + 1] - ts[i - 1]);
  let i = 0;
  while (i < n - 1 && t >= ts[i + 1]) i++;
  const T = Math.max(1e-9, ts[i + 1] - ts[i]);
  return hermite(ps[i], ps[i + 1], vel(i), vel(i + 1), (t - ts[i]) / T, T);
};
