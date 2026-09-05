/* kinetics/squash.mjs - area-preserving, motion-driven squash and stretch (42 s42.3; FINDING-the-animation-math s4;
   47 s1 row 5). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN
   squash and KINETICS:END (P43 T4), after spring - it reads the spring's velocity and acceleration. The vortex's
   inline stretch routes through scaleBy at identical output; the pops apply the tensor behind kinetics.area_squash.
     A = R(theta) diag(1 + alpha, 1 / (1 + alpha)) R(-theta)     det(A) = 1 by construction
     alpha = kappa_v |v| + kappa_a max(0, -v_hat . a)               stretch along the velocity, compress across it
   alpha is driven by speed and by deceleration, so squash emerges from the motion rather than being keyframed.
   kappa_v, kappa_a and the clamp are ours to tune (42 s42.5). */
import { springEval } from "./spring.mjs";

export const SQUASH = Object.freeze({ KV: 0.0004, KA: 0.00002, MAX: 0.25 });   /* per px/s and px/s^2; MAX keeps a pop a pop */

/* the amount, from a velocity and an acceleration (2-vectors) */
export const squashAlpha = (v, a, o = {}) => {
  const P = Object.assign({}, SQUASH, o), speed = Math.hypot(v[0], v[1]);
  if (!(speed > 0)) return 0;
  const decel = Math.max(0, -(v[0] * a[0] + v[1] * a[1]) / speed);
  return Math.min(P.MAX, P.KV * speed + P.KA * decel);
};

/* the tensor as [a, b, c, d] for matrix(a b c d 0 0): stretch 1 + alpha along theta, 1 / (1 + alpha) across it */
export const squashMatrix = (theta, alpha) => {
  const sx = 1 + alpha, sy = 1 / (1 + alpha), c = Math.cos(theta), s = Math.sin(theta), cs = c * s * (sx - sy);
  return [c * c * sx + s * s * sy, cs, cs, s * s * sx + c * c * sy];
};
export const det2 = (m) => m[0] * m[3] - m[1] * m[2];

/* the vortex's form: a uniform scale s with the area-preserving stretch along the tangent - the exact expressions the
   vortex shipped with (s * (1 + a), s / (1 + a)), so its output is unchanged to the bit */
export const scaleBy = (s, alpha) => ({ sx: s * (1 + alpha), sy: s / (1 + alpha) });

/* a 1-D pop's alpha from its spring: travel px over dur seconds along one axis */
export const springSquash = (u, params, travel, dur, o = {}) => {
  const p = springEval(u, params), v = travel * p.v / dur, a = travel * p.a / (dur * dur);
  return squashAlpha([0, v], [0, a], o);
};
