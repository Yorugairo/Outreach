/* kinetics/spring.mjs - the settle (42 s42.2; FINDING-the-animation-math s3). SOURCE OF TRUTH, inlined into the
   scene-evidence player by sync_kinetics.py between KINETICS:BEGIN spring and KINETICS:END (P43 T1). T1 moves
   the shipping springPop here at identical output; P43 T5 adds the three damping regimes, the velocity and the
   seek contract around it.
   springPop - the closed-form underdamped mass-spring-damper, x(t) = 1 - e^(-z w t)(cos wd t + z w/wd sin wd t),
               with the INVERSE model: the overshoot you want (Mp) gives z = -ln Mp / sqrt(pi^2 + ln^2 Mp), and the
               settle you want (0.25% by u = 1) gives w = 6 / z; peaks at pi / wd. Exact at every seek, lands on 1
               (kinetics.analytic_spring). */
export const springPop = (u, Mp = 0.04) => {
  if (u >= 1) return 1; if (u <= 0) return 0;
  const L = Math.log(Mp), z = -L / Math.sqrt(Math.PI * Math.PI + L * L), w = 6 / z, wd = w * Math.sqrt(1 - z * z);   /* envelope e^-6 = 0.25% at u = 1: lands, never snaps */
  return 1 - Math.exp(-z * w * u) * (Math.cos(wd * u) + (z * w / wd) * Math.sin(wd * u));
};
