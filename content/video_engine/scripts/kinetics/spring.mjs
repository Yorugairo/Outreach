/* kinetics/spring.mjs - the settle (42 s42.2; FINDING-the-animation-math s3; 47 s1 row 4). SOURCE OF TRUTH, inlined into
   the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN spring and KINETICS:END (P43 T1, T5). Behind
   kinetics.analytic_spring.
   The closed-form second-order step response x(0) = 0, v(0) = 0 -> 1, in all three damping regimes, with velocity and
   acceleration - stateless, so frame N evaluated directly IS frames 0..N (the seek test); an integrator cannot say that.
     underdamped  z < 1 : x = 1 - e^(-z w t)(cos wd t + z w / wd sin wd t),  wd = w sqrt(1 - z^2)
     critical     z = 1 : x = 1 - e^(-w t)(1 + w t)
     overdamped   z > 1 : x = 1 - (s2 e^(s1 t) - s1 e^(s2 t)) / (s2 - s1),  s1,2 = -w (z -+ sqrt(z^2 - 1))
   The INVERSE model is the one entry point (springParams): the overshoot you want, Mp, gives z = -ln Mp / sqrt(pi^2 +
   ln^2 Mp) (Mp = 0 asks for critical damping); the settle you want - the envelope at 0.25% by u = 1, e^-6 - gives
   w = 6 / z. The peak lands at t_p = pi / wd and is exactly 1 + Mp. springPop is the thin caller at Mp = 0.04, unchanged
   to the bit from the 2026-09-05 shipping version. The dials - Mp per material, the settle - are ours (42 s42.5). */

export const SPRING = Object.freeze({ MP: 0.04, SETTLE: 6 });

/* overshoot + settle -> the model's parameters */
export const springParams = (Mp = SPRING.MP, settle = SPRING.SETTLE) => {
  if (!(Mp > 0)) return { z: 1, w: settle, wd: 0 };
  const L = Math.log(Math.min(Mp, 0.999)), z = -L / Math.sqrt(Math.PI * Math.PI + L * L), w = settle / z;
  return { z, w, wd: w * Math.sqrt(1 - z * z) };
};

/* position, velocity and acceleration at t >= 0 */
export const springEval = (t, p) => {
  if (!(t > 0)) return { x: 0, v: 0, a: 0 };
  const { z, w } = p;
  if (z < 1) {
    const wd = p.wd || w * Math.sqrt(1 - z * z), e = Math.exp(-z * w * t), sn = Math.sin(wd * t), cs = Math.cos(wd * t);
    return { x: 1 - e * (cs + (z * w / wd) * sn), v: e * (w * w / wd) * sn, a: (w * w / wd) * e * (wd * cs - z * w * sn) };
  }
  if (z === 1) { const e = Math.exp(-w * t); return { x: 1 - e * (1 + w * t), v: w * w * t * e, a: w * w * e * (1 - w * t) }; }
  const q = Math.sqrt(z * z - 1), s1 = -w * (z - q), s2 = -w * (z + q), e1 = Math.exp(s1 * t), e2 = Math.exp(s2 * t);
  return { x: 1 - (s2 * e1 - s1 * e2) / (s2 - s1), v: w * w * (e1 - e2) / (s1 - s2), a: w * w * (s1 * e1 - s2 * e2) / (s1 - s2) };
};

/* the shipping pop: overshoot Mp, lands on exactly 1 */
export const POP = springParams(SPRING.MP);
export const springPop = (u, Mp = 0.04) => {
  if (u >= 1) return 1; if (u <= 0) return 0;
  return springEval(u, Mp === SPRING.MP ? POP : springParams(Mp)).x;
};
