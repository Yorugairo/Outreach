/* kinetics/drop.mjs - THE LIVING DROP: a heavy ball's boundary as RAYLEIGH SURFACE MODES (P57 R26-118; the operator
   2026-09-14, E88 s7: "a more living ball, that is wriggling to contain itself, and has real, metallic mass and
   density"). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN drop
   and KINETICS:END, BEFORE melt (species/melt.mjs imports it). It imports nothing: this is arithmetic.

   THE LAW'S SHAPE (ours are the numbers, not the form):
     r(theta, t) = R * (1 + sum over l of a_l(t) * cos(l * theta + phi_l))
     a_l(t)      = sum over the impulses i of a_li * exp(-dt_i / tau_l) * cos(omega_l * dt_i)  +  FLOOR_l * cos(omega_l * t)
     omega_l^2   = l (l - 1)(l + 2) * SIGMA / (RHO * R^3)        [Rayleigh 1879, Proc. R. Soc. Lond. 29, 71-97]
     tau_l       = R^2 / ((l - 1)(2l + 1) * NU) * DAMP           [Lamb, Hydrodynamics 6th ed. 1932, s355 p. 640]
   Modes l = 2, 3, 4 (l = 0 is the breathing an incompressible drop cannot do, l = 1 is a translation). Every frame the
   ring's AREA is renormalised to pi R^2 on its own shoelace: the drop wobbles, it never grows.

   THE NUMBERS, and what they are worth. SIGMA, RHO and NU come from `docs/research/runs/living_drop/` (the run is
   QUARANTINED, unapproved, and no doctrine file cites it). The parent's gate on it, 2026-09-14: PLAUSIBLE at best -
   the run fetched no pages to disk, so nothing here is CONFIRMED.
     metal   MERCURY at 20 C [research run living_drop, unapproved: PLAUSIBLE - Rayleigh 1879 / Lamb 1932 / CRC 97th
             ed. / Jasper 1972]. The run's other liquid metal, galinstan, is NOT dialled: its 0.535 N/m is CONTESTED
             (Morley 2008 is usually cited near 0.718 N/m), and a contested number is not a default.
     liquid  WATER at 20 C [research run living_drop, unapproved: PLAUSIBLE - IAPWS 2008 / 2014].
     ink     [UNSOURCED]: the run's ink row carries no author, year or URL. Ours, by eye, until one does.
   And they are only half of any dial: what a page px IS in metres is OURS (`PX_PER_M`) - a 60 px ball at 8500 px/m is
   a 7.1 mm bead, ringing mode 2 at 4.5 Hz, which is the craft's own band for a wobble (a period of 167-250 ms, two to
   three drawings on 2s). So is `DAMP`: the ideal bead rings for ~90 s at this size (Lamb) and a melt is seconds long,
   so the decay is the stop-motion craft's - tau_2 = 0.25 s, about three visible cycles before the floor takes over,
   inside the 80-220 ms settle the craft sells an impact with. Every one of these is a dial (42 s42.5), tuned by eye.

   E49, never still: FLOOR is an amplitude the decay cannot take away, so the drop is always wriggling to contain
   itself. Pure functions of (t, R, the material, the impulses): the same t twice is the same ring, so a scrubbed
   frame is the played frame. */

export const DROP = Object.freeze({
  MODES: [2, 3, 4],       /* the Rayleigh modes we carry: l lobes each, l = 2 the squeeze the eye reads */
  N: 96,                  /* the ring's samples (MELT.RING_N: the melt's morph lands on the same count) */
  PX_PER_M: 8500,         /* OURS: how big the ball really is - a 60 px ball is a 7.1 mm bead (mode 2 at 4.5 Hz, a
                             223 ms period: the craft's two-to-three drawings on 2s) */
  DAMP: 0.0028,           /* OURS: Lamb's modulus of decay is ~90 s at this size; ours is tau_2 = 0.25 s - three visible
                             cycles, the craft's 80-220 ms settle after an impact */
  A: [0.10, 0.055, 0.022],    /* the COMPILE's excitation per mode, as a share of R: the squeeze's own asymmetry */
  PHI: [0.0, 1.10, 2.30],     /* each mode's spatial phase (radians): where its lobes sit on the ball */
  FLOOR: [0.012, 0.007, 0.003],  /* E49: the amplitude the decay never takes - the drop is never at rest */
  KICK: [0.085, 0.030, 0.010],   /* a LANDING or a NUDGE re-excites the modes by this, scaled by the material's impact */
  /* the fluids, at 20 C. SIGMA N/m, RHO kg/m^3, NU m^2/s [research run living_drop, unapproved] */
  MAT: {
    metal:  { SIGMA: 0.4865, RHO: 13546, NU: 1.1265e-7 },   /* MERCURY: dense, taut, and it rings for ever [PLAUSIBLE] */
    ink:    { SIGMA: 0.0500, RHO: 1050,  NU: 3.0476e-6 },   /* india ink, a carbon-black dispersion [UNSOURCED - ours] */
    liquid: { SIGMA: 0.0728, RHO: 998.2, NU: 1.0038e-6 },   /* water [PLAUSIBLE] */
    paper:  { SIGMA: 0.0500, RHO: 1050,  NU: 3.0476e-6 },   /* a card is not a fluid: it borrows the ink's surface */
  },
  /* THE SPECULAR HIGHLIGHT (E88 s7: "so the metal reads as metal") - a lit spot offset toward the stage light. It is
     pinned to the LIGHT, not to the surface, so under a roll it counter-rotates against the ink's mark. */
  LIGHT_DEG: -125,        /* where the stage light is, degrees from +x with y DOWN (SVG): up and to the left */
  HL_AT: 0.46,            /* how far out the spot sits, as a share of the local radius. The geometry behind it: the
                             mirror seat of a light at theta_L sits at R sin(theta_L / 2) - 0.383 R at 45 degrees */
  HL_R: 0.20,             /* its own radius, as a share of R [DERIVED, tuned by eye: the run's 0.15-0.20 R is
                             MISATTRIBUTED to Cook & Torrance 1982 and is not a source] */
});

const dp01 = (v) => (v <= 0 ? 0 : v >= 1 ? 1 : v);   /* the engine inlines every module into ONE scope, so a private
   helper carries the module's own prefix */
const dpMat = (name, P) => (P.MAT && P.MAT[name]) || DROP.MAT.metal;

/* omega_l in rad/s for a ball of R page px of `mat` (Rayleigh 1879), through PX_PER_M */
export const dropOmega = (l, rPx, mat = "metal", o = {}) => {
  const P = Object.assign({}, DROP, o), M = dpMat(mat, P), R = Math.max(1e-6, rPx) / P.PX_PER_M;
  return Math.sqrt(l * (l - 1) * (l + 2) * M.SIGMA / (M.RHO * R * R * R));
};
/* tau_l in seconds (Lamb 1932), scaled by DAMP - the craft's decay, not the fluid's */
export const dropTau = (l, rPx, mat = "metal", o = {}) => {
  const P = Object.assign({}, DROP, o), M = dpMat(mat, P), R = Math.max(1e-6, rPx) / P.PX_PER_M;
  return P.DAMP * R * R / ((l - 1) * (2 * l + 1) * M.NU);
};
/* ONE impulse's contribution to mode l at `dt` seconds after it: the decaying ring */
export const dropAmp = (l, a0, dt, rPx, mat = "metal", o = {}) => {
  if (!(dt >= 0)) return 0;
  const P = Object.assign({}, DROP, o);
  return a0 * Math.exp(-dt / dropTau(l, rPx, mat, P)) * Math.cos(dropOmega(l, rPx, mat, P) * dt);
};
/* EVERY LIVE MODE at t: the impulses' sum and the floor that never dies. `excite` is a list of { at, a } - `at` in the
   same seconds as t, `a` an array per mode (or a scalar, taken through KICK's own shape). `spin` (an option) turns the
   lobes with the surface: a rolling ball's ink turns, and its light does not. */
export const dropModes = (t, rPx, mat = "metal", excite = [], o = {}) => {
  const P = Object.assign({}, DROP, o), spin = +P.spin || 0;
  return (P.MODES || DROP.MODES).map((l, i) => {
    let a = (P.FLOOR[i] || 0) * Math.cos(dropOmega(l, rPx, mat, P) * t);
    for (const e of excite || []) {
      const dt = t - (+e.at || 0);
      if (!(dt >= 0)) continue;
      const av = Array.isArray(e.a) ? (e.a[i] || 0) : (+e.a || 0) * ((P.KICK[i] || 0) / Math.max(1e-9, P.KICK[0] || 1));
      a += dropAmp(l, av, dt, rPx, mat, P);
    }
    return { l, a, phi: (P.PHI[i] || 0) - l * spin };   /* -l*spin turns the pattern BY +spin: r_spun(th) = r(th - spin) */
  });
};
/* the radius at theta as a SHARE of R (1 is the circle) */
export const dropRadius = (theta, modes) => {
  let k = 1;
  for (const m of modes || []) k += m.a * Math.cos(m.l * theta + m.phi);
  return k;
};
/* a closed polygon's area, by its own shoelace - positive whichever way it is walked */
export const dropArea = (pts) => {
  let a = 0;
  for (let i = 0, n = pts.length; i < n; i++) { const p = pts[i], q = pts[(i + 1) % n]; a += p[0] * q[1] - q[0] * p[1]; }
  return Math.abs(a) / 2;
};
/* THE RING, area-renormalised to pi R^2 (incompressible): N points about `c`, walked the way a circle is walked. */
export const dropRing = (c, rPx, t, mat = "metal", excite = [], o = {}) => {
  const P = Object.assign({}, DROP, o), n = Math.max(8, P.N | 0), modes = dropModes(t, rPx, mat, excite, P), pts = [];
  for (let i = 0; i < n; i++) {
    const th = 2 * Math.PI * (i / n), k = Math.max(0.05, dropRadius(th, modes));
    pts.push([c[0] + rPx * k * Math.cos(th), c[1] + rPx * k * Math.sin(th)]);
  }
  const want = Math.PI * rPx * rPx, got = dropArea(pts), s = Math.sqrt(want / Math.max(1e-9, got));
  return pts.map((p) => [c[0] + (p[0] - c[0]) * s, c[1] + (p[1] - c[1]) * s]);
};
/* THE HIGHLIGHT: the lit spot in the ball's own px, offset toward the stage light and DIMPLING with the modes (it
   rides the local radius). It never turns with the surface - that is what makes the roll read as a roll. */
export const dropSpecular = (c, rPx, modes, o = {}) => {
  const P = Object.assign({}, DROP, o), th = P.LIGHT_DEG * Math.PI / 180;
  const k = Math.max(0.05, dropRadius(th, modes));
  return { x: c[0] + rPx * k * P.HL_AT * Math.cos(th), y: c[1] + rPx * k * P.HL_AT * Math.sin(th),
           r: rPx * P.HL_R * (0.85 + 0.15 * k), k: dp01(k / 1.5) };
};
