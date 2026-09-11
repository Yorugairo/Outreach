/* kinetics/clothoid.mjs - THE CLOTHOID FITTER for GENERATED geometry (P50 T14; doc 42 s42.4). SOURCE OF TRUTH,
   inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN clothoid and KINETICS:END,
   AFTER stroke and before the species regions - it imports nothing, so its region may sit anywhere after the
   laws it is drawn by; it sits beside the stroke because the stroke is its one consumer.

   THE LAW (42 s42.4, as written): "Cubic Bezier curvature is a degree-3-over-degree-6 rational function: it
   ripples, throws parasitic inflections and flat spots. Euler spirals (clothoids) hold dk/ds = const, giving
   G2 continuity and minimising E_MVS = integral (dk/ds)^2 ds (Levien 2009; Moreton & Sequin 1992). Applies to
   geometry the engine GENERATES - arrows, balance arms, connectors, axes. Hand-authored art is unaffected."
   So: a segment here is theta(s) = theta0 + k0 s + dk s^2 / 2, and its curvature is a straight line in s. It
   is fitted to a G1 Hermite problem - two points and the tangent angle at each - which is the shape every
   generated connector is actually given (a chip's edge to the next chip's edge, a centroid to a centroid).

   THE FIT (Bertolazzi & Frego 2015, "G1 fitting with clothoids", the same reduction; the arithmetic here is
   ours and tested against brute-force quadrature). Put tau = s / L. With phi the chord's angle, phi0 =
   wrap(theta0 - phi) and phi1 = wrap(theta1 - phi), delta = phi1 - phi0:
     theta(tau) - phi = phi0 + B tau + A tau^2,  B = delta - A
   The end point is ON the chord exactly when the component across the chord vanishes:
     g(A) = integral_0^1 sin(A tau^2 + (delta - A) tau + phi0) dtau = 0      <- one equation, one unknown
   and then L = r / integral_0^1 cos(...) dtau with r the chord's length. A = 0 is the circular arc (a
   symmetric problem, phi1 = -phi0, solves at A = 0 - the fitter's own sanity check, pinned in the tests).
   g is found by an expanding bracket around A = 3 (phi0 + phi1) and bisected to the last bit: deterministic,
   and it cannot walk off a Newton cliff on a near-straight pair where g is almost flat.

   THE FRESNEL INTEGRALS. Those two integrals are the generalised Fresnel momenta X(a, b, c), Y(a, b, c) =
   integral_0^1 cos|sin(a tau^2 + b tau + c) dtau, which complete the square onto C(x) = integral_0^x
   cos(pi t^2 / 2) dt and S(x) its sine. C and S are the POWER SERIES inside |x| <= SERIES_R and THE
   ASYMPTOTIC FORM outside it - the two the doc's law is worth having, and the seam between them sits where
   their two error curves cross (measured: ~1e-9 at x = 3.4; the series is 1e-15 at x = 2 and the asymptotic
   form 1e-12 by x = 4). A fixed-step Simpson was tried in that band and is the reason the seam is where it
   is: to hold 1e-12 at x = 4 it wants some 25 000 samples per call, and this arithmetic sits INSIDE the
   fit's own bisection, a hundred and thirty calls deep, on every frame that draws an arrow.
   The one place completing the square cannot be used is |a| -> 0, where its two Fresnel arguments run off
   as 1 / sqrt(a) and their difference is multiplied back by sqrt(1 / a): there the momenta are integrated
   directly by a composite 8-point Gauss-Legendre, a couple of dozen cosines at machine precision.

   Nothing is stored: every export is a pure function of its arguments, so the same declaration draws the same
   polyline on a scrub as on a play. The dials below are ours to tune (42 s42.5), not findings. */

export const CLOTHOID = Object.freeze({
  SERIES_R: 3.4,        /* |x| the Fresnel POWER SERIES is trusted to. The series is exact arithmetic on paper and pure cancellation in a double: its largest term grows like (pi x^2 / 2)^n / n!, so at x = 3.4 it peaks near 1e7 against a result of ~0.5 (seven digits gone, ~1e-9 left) - and that is exactly where the asymptotic form below has come down to the same 1e-9. The seam is the crossing of the two error curves, measured, not guessed. */
  SERIES_MAX: 64,       /* ... and the term count that ends the sum if the epsilon never does */
  SERIES_EPS: 1e-17,    /* the term below which the sum has converged against a result of order 0.5 */
  ASYMP_MAX: 64,        /* the asymptotic form's term cap; it stops on its own at its smallest term, which is what an asymptotic series' accuracy IS */
  SMALL_A: 0.5,         /* |a| under which the momenta are integrated DIRECTLY instead of by completing the square: below it the square's two Fresnel arguments run off as 1 / sqrt(a) and their difference is multiplied back by sqrt(1 / a) - the one place this arithmetic loses everything */
  GL_PHASE: 2.0,        /* ... on panels of about this many radians of phase each, 8-point Gauss-Legendre per panel: machine precision for a couple of dozen cosines, which matters because this branch sits INSIDE the fit's bisection */
  GL_PANELS_MAX: 64,    /* ... and a panel cap, so a wild phase cannot hang the frame */
  GUESS_K: 3,           /* the bracket's centre, A0 = GUESS_K (phi0 + phi1): exactly right for the symmetric arc (A = 0) and within a step of the root for everything we draw */
  BRACKET_STEP: 0.5,    /* the first step out from the guess, in units of A (A is the turn in radians per unit tau^2) */
  BRACKET_GROW: 1.6,    /* ... growing geometrically, so a hard pair is bracketed in a few dozen probes rather than a few thousand */
  BRACKET_MAX: 64,      /* ... for at most this many probes each way */
  A_MAX: 4000,          /* the widest |A| a fit may claim: past it the "curve" is a coil, not a connector */
  BISECT: 80,           /* bisections after the bracket: 80 halvings take any bracket to the last bit of a double */
  SAMPLES: 48,          /* the default polyline length: the stroke engine resamples by arclength anyway, so this only has to be dense enough that its chords hide (42 s42.1's SAMPLE_PX at our sizes) */
  BEZ_HANDLE: 0.5,      /* the reference cubic's handle as a share of the chord - half of it, what a hand-rolled connector is usually given. It is a DIAL because the cubic's defect depends on it: at a half the parasitic inflection 42 s42.4 names is there to be measured, at a third the cubic is tamer and its curvature still ripples. The clothoid has no such dial. */
  JOIN_SWEEP: 2.4,      /* radians either side of the chord the S-fit sweeps its join tangent through, looking for the curvature match */
  JOIN_STEPS: 48,       /* ... in this many probes: fine enough that a sign change inside the sweep is not stepped over */
  JOIN_AT: 0.5,         /* ... with the join itself at the chord's midpoint: one free parameter, one equation (the curvature at the join, read from both sides) */
});

const clTAU = Math.PI * 2;
const clPI2 = Math.PI / 2;

/* an angle folded into (-pi, pi] - every phase in the fit is a difference of two headings */
export const wrapPi = (a) => {
  let v = (a + Math.PI) % clTAU;
  if (v <= 0) v += clTAU;
  return v - Math.PI;
};

/* a tangent given as a heading in radians, as [x, y] or as {x, y} -> the heading in radians */
export const angleOf = (t) => {
  if (typeof t === "number") return t;
  if (Array.isArray(t)) return Math.atan2(t[1], t[0]);
  if (t && typeof t === "object") return Math.atan2(t.y, t.x);
  return 0;
};

const clPt = (p) => (Array.isArray(p) ? { x: +p[0], y: +p[1] } : { x: +p.x, y: +p.y });

/* C(x), S(x) by the power series: C = sum (-1)^n (pi/2)^2n x^(4n+1) / ((2n)! (4n+1)), S its sine twin. */
const clFresnelSeries = (x) => {
  const x2 = x * x, q = clPI2 * clPI2 * x2 * x2;   /* the factor that carries each term to the next */
  let tc = x, ts = clPI2 * x2 * x, C = tc, S = ts / 3;
  for (let n = 1; n < CLOTHOID.SERIES_MAX; n++) {
    tc *= -q / ((2 * n) * (2 * n - 1));
    ts *= -q / ((2 * n + 1) * (2 * n));
    C += tc / (4 * n + 1);
    S += ts / (4 * n + 3);
    if (Math.abs(tc) + Math.abs(ts) < CLOTHOID.SERIES_EPS) break;
  }
  return { C, S };
};

/* ... and past SERIES_R by THE ASYMPTOTIC FORM (the option 42 s42.4's fitter is given). Repeated integration
   by parts of I(x) = integral_x^inf exp(i pi t^2 / 2) dt gives I ~ exp(i z) sum c_n, z = pi x^2 / 2, with
   c_0 = i / (pi x) and c_(n+1) = c_n (-i (2n+1) / (pi x^2)); C = 1/2 - Re I, S = 1/2 - Im I. The series
   diverges eventually - it is asymptotic - so it is summed to its SMALLEST term, which is its accuracy:
   about exp(-z) / (pi x), i.e. 1e-9 at x = 3.4 and 1e-12 by x = 4. */
const clFresnelAsym = (x) => {
  const z = clPI2 * x * x, cz = Math.cos(z), sz = Math.sin(z), px2 = Math.PI * x * x;
  let cr = 0, ci = 1 / (Math.PI * x), sr = 0, si = 0, prev = Infinity;
  for (let n = 0; n < CLOTHOID.ASYMP_MAX; n++) {
    const mag = Math.hypot(cr, ci);
    if (mag > prev) break;            /* past the smallest term the asymptotic series only gets worse */
    prev = mag;
    sr += cr; si += ci;
    const k = (2 * n + 1) / px2, nr = k * ci, ni = -k * cr;   /* c *= -i k */
    cr = nr; ci = ni;
  }
  return { C: 0.5 - (cz * sr - sz * si), S: 0.5 - (cz * si + sz * sr) };
};

/* THE FRESNEL INTEGRALS, odd in x: the series inside SERIES_R, the asymptotic form outside it. */
export const fresnel = (x) => {
  const a = Math.abs(x), sg = x < 0 ? -1 : 1;
  const f = a <= CLOTHOID.SERIES_R ? clFresnelSeries(a) : clFresnelAsym(a);
  return { C: sg * f.C, S: sg * f.S };
};

/* 8-point Gauss-Legendre on [-1, 1] (Abramowitz & Stegun 25.4.30): eight cosines buy ~1e-15 on a panel
   holding a couple of radians of phase, where a fixed-step Simpson would want thousands. */
const CL_GL_X = Object.freeze([-0.9602898564975363, -0.7966664774136267, -0.5255324099163290, -0.1834346424956498,
                               0.1834346424956498, 0.5255324099163290, 0.7966664774136267, 0.9602898564975363]);
const CL_GL_W = Object.freeze([0.1012285362903763, 0.2223810344533745, 0.3137066458778873, 0.3626837833783620,
                               0.3626837833783620, 0.3137066458778873, 0.2223810344533745, 0.1012285362903763]);

/* the momenta integrated directly - the |a| ~ 0 branch, where completing the square divides by a */
const clMomentsDirect = (a, b, c) => {
  const span = Math.abs(a) + Math.abs(b);
  const m = Math.min(CLOTHOID.GL_PANELS_MAX, Math.max(1, Math.ceil(span / CLOTHOID.GL_PHASE)));
  const h = 1 / m;
  let X = 0, Y = 0;
  for (let p = 0; p < m; p++) {
    const mid = (p + 0.5) * h, half = h / 2;
    for (let i = 0; i < 8; i++) {
      const t = mid + half * CL_GL_X[i], ph = a * t * t + b * t + c, w = CL_GL_W[i] * half;
      X += w * Math.cos(ph);
      Y += w * Math.sin(ph);
    }
  }
  return { X, Y };
};

/* THE GENERALISED FRESNEL MOMENTA: X, Y = integral_0^1 cos|sin(a tau^2 + b tau + c) dtau, by completing the
   square onto C and S. a < 0 is the mirror (cos is even in the whole phase, sin odd). */
export const fresnelMoments = (a, b, c) => {
  if (Math.abs(a) < CLOTHOID.SMALL_A) return clMomentsDirect(a, b, c);
  if (a < 0) { const m = fresnelMoments(-a, -b, -c); return { X: m.X, Y: -m.Y }; }
  const k = Math.sqrt(2 * a / Math.PI), scale = Math.sqrt(Math.PI / (2 * a));
  const u0 = k * (b / (2 * a)), u1 = k * (1 + b / (2 * a)), psi = c - b * b / (4 * a);
  const f1 = fresnel(u1), f0 = fresnel(u0), dC = f1.C - f0.C, dS = f1.S - f0.S;
  const cp = Math.cos(psi), sp = Math.sin(psi);
  return { X: scale * (cp * dC - sp * dS), Y: scale * (cp * dS + sp * dC) };
};

/* THE FIT of one segment to a G1 Hermite problem. Returns the segment as the player draws it:
   { x0, y0, theta0, k0, dk, L } with theta(s) = theta0 + k0 s + dk s^2 / 2, plus the fit's own A / B
   (the turn in tau) and `ok` - false when the pair is degenerate (coincident points, or a phase that
   brackets no root inside A_MAX), in which case the caller draws the straight chord and nothing lies. */
export const clothoidFit = (p0, t0, p1, t1) => {
  const a = clPt(p0), b = clPt(p1), th0 = angleOf(t0), th1 = angleOf(t1);
  const dx = b.x - a.x, dy = b.y - a.y, r = Math.hypot(dx, dy), phi = Math.atan2(dy, dx);
  const bad = { x0: a.x, y0: a.y, theta0: th0, k0: 0, dk: 0, L: r, A: 0, B: 0, phi, ok: false };
  if (!(r > 0)) return bad;
  const phi0 = wrapPi(th0 - phi), phi1 = wrapPi(th1 - phi), delta = phi1 - phi0;
  const g = (A) => fresnelMoments(A, delta - A, phi0).Y;
  const A0 = CLOTHOID.GUESS_K * (phi0 + phi1), f0 = g(A0);
  let lo = A0, hi = A0, flo = f0;
  if (f0 !== 0) {
    let step = CLOTHOID.BRACKET_STEP, found = false;
    for (let i = 0; i < CLOTHOID.BRACKET_MAX && !found; i++) {
      const dn = A0 - step, up = A0 + step, fdn = g(dn), fup = g(up);
      if (fdn * f0 <= 0) { lo = dn; flo = fdn; hi = A0; found = true; }
      else if (fup * f0 <= 0) { lo = A0; flo = f0; hi = up; found = true; }
      else { step *= CLOTHOID.BRACKET_GROW; if (step > CLOTHOID.A_MAX) break; }
    }
    if (!found) return bad;
  }
  for (let i = 0; i < CLOTHOID.BISECT; i++) {
    const mid = 0.5 * (lo + hi), fm = g(mid);
    if (fm === 0) { lo = mid; hi = mid; break; }
    if (fm * flo <= 0) { hi = mid; } else { lo = mid; flo = fm; }
  }
  const A = 0.5 * (lo + hi), B = delta - A, X = fresnelMoments(A, B, phi0).X;
  if (!(X > 0)) return bad;
  const L = r / X;
  return { x0: a.x, y0: a.y, theta0: th0, k0: B / L, dk: 2 * A / (L * L), L, A, B, phi, ok: true };
};

/* THE SEGMENT AT tau in [0, 1]: the point, the arclength, the heading and the SIGNED curvature there. The
   point is the momenta of the PARTIAL interval (exact), never a running sum - a sample is the same value
   whether it is asked for first or last. */
export const clothoidAt = (fit, tau) => {
  const u = Math.min(1, Math.max(0, tau)), A = fit.A, B = fit.B, th0 = fit.theta0;
  const m = fresnelMoments(A * u * u, B * u, th0);
  return { x: fit.x0 + fit.L * u * m.X, y: fit.y0 + fit.L * u * m.Y,
           s: fit.L * u, k: fit.k0 + fit.dk * fit.L * u, theta: th0 + B * u + A * u * u };
};

/* THE POLYLINE the stroke engine draws BY LENGTH: n samples of the fitted segment, each carrying its own
   arclength and curvature so 42 s42.1's profile can be read straight off it. */
export const clothoid = (p0, t0, p1, t1, n = CLOTHOID.SAMPLES) => {
  const fit = clothoidFit(p0, t0, p1, t1), N = Math.max(2, n | 0), out = new Array(N);
  for (let i = 0; i < N; i++) out[i] = clothoidAt(fit, i / (N - 1));
  return out;
};

/* THE TWO-SEGMENT G2 FIT (the S-curve). Two clothoids meet at the chord's midpoint; the ONE free parameter
   is the heading there, and it is chosen so the curvature the first segment ARRIVES with is the curvature
   the second LEAVES with - G2 at the join by construction, not by luck. The sweep is bracketed either side
   of the chord's own direction and bisected, exactly as the single fit's A is. `ok` false = no match inside
   JOIN_SWEEP; the caller then has two G1 segments and knows it. */
export const clothoidS = (p0, t0, p1, t1, n = CLOTHOID.SAMPLES) => {
  const a = clPt(p0), b = clPt(p1);
  const m = { x: a.x + (b.x - a.x) * CLOTHOID.JOIN_AT, y: a.y + (b.y - a.y) * CLOTHOID.JOIN_AT };
  const chord = Math.atan2(b.y - a.y, b.x - a.x);
  /* the curvature gap at the join, as a function of the join's heading */
  const gap = (th) => {
    const f1 = clothoidFit(a, t0, m, th), f2 = clothoidFit(m, th, b, t1);
    if (!f1.ok || !f2.ok) return null;
    return { d: f2.k0 - (f1.k0 + f1.dk * f1.L), f1, f2 };
  };
  const g0 = gap(chord);
  let lo = chord, hi = chord, glo = g0, found = !!g0 && g0.d === 0;
  if (g0 && !found) {
    const h = CLOTHOID.JOIN_SWEEP / CLOTHOID.JOIN_STEPS;
    for (let i = 1; i <= CLOTHOID.JOIN_STEPS && !found; i++) {
      const dn = gap(chord - i * h), up = gap(chord + i * h);
      if (dn && dn.d * g0.d <= 0) { lo = chord - i * h; glo = dn; hi = chord - (i - 1) * h; found = true; }
      else if (up && up.d * g0.d <= 0) { lo = chord + (i - 1) * h; glo = gap(lo) || g0; hi = chord + i * h; found = true; }
    }
  }
  let thm = chord, best = g0;
  if (found && glo) {
    for (let i = 0; i < CLOTHOID.BISECT; i++) {
      const mid = 0.5 * (lo + hi), gm = gap(mid);
      if (!gm) break;
      if (gm.d === 0) { lo = mid; hi = mid; glo = gm; break; }
      if (gm.d * glo.d <= 0) { hi = mid; } else { lo = mid; glo = gm; }
    }
    thm = 0.5 * (lo + hi);
    best = gap(thm) || g0;
  }
  if (!best) return { ok: false, theta_m: thm, gap: null, join: null, fits: [], pts: [] };
  const N = Math.max(4, n | 0), n1 = Math.max(2, N >> 1), n2 = Math.max(2, N - n1 + 1);
  const pts = [];
  for (let i = 0; i < n1; i++) pts.push(clothoidAt(best.f1, i / (n1 - 1)));
  const s1 = best.f1.L;
  for (let i = 1; i < n2; i++) { const q = clothoidAt(best.f2, i / (n2 - 1)); q.s += s1; pts.push(q); }
  const end = clothoidAt(best.f1, 1);
  return { ok: found, theta_m: thm, gap: best.d,
           join: { x: end.x, y: end.y, theta: thm, k_in: end.k, k_out: best.f2.k0 },
           fits: [best.f1, best.f2], pts };
};

/* THE REFERENCE the doc names: the textbook G1 Hermite CUBIC over the same ends. It is here so a test can
   show the parasitic inflection - a curvature that changes SIGN where the clothoid's does not - and so no
   one has to take 42 s42.4 on faith. Nothing draws it. */
export const bezierOf = (p0, t0, p1, t1, n = CLOTHOID.SAMPLES, handle = CLOTHOID.BEZ_HANDLE) => {
  const a = clPt(p0), b = clPt(p1), th0 = angleOf(t0), th1 = angleOf(t1);
  const r = Math.hypot(b.x - a.x, b.y - a.y) * handle;
  const c1 = { x: a.x + r * Math.cos(th0), y: a.y + r * Math.sin(th0) };
  const c2 = { x: b.x - r * Math.cos(th1), y: b.y - r * Math.sin(th1) };
  const N = Math.max(2, n | 0), out = new Array(N);
  for (let i = 0; i < N; i++) {
    const u = i / (N - 1), v = 1 - u, w0 = v * v * v, w1 = 3 * v * v * u, w2 = 3 * v * u * u, w3 = u * u * u;
    out[i] = { x: w0 * a.x + w1 * c1.x + w2 * c2.x + w3 * b.x, y: w0 * a.y + w1 * c1.y + w2 * c2.y + w3 * b.y };
  }
  return out;
};

/* THE MEASURED curvature of a polyline: Menger's 1 / circumradius, SIGNED by the turn (left positive), so a
   ripple in a generated curve shows up as what it is. The ends copy their neighbours (three points are the
   smallest thing a curvature can be read from). */
export const curvatureOf = (pts) => {
  const n = pts.length, k = new Array(n).fill(0);
  for (let i = 1; i < n - 1; i++) {
    const a = pts[i - 1], b = pts[i], c = pts[i + 1];
    const abx = b.x - a.x, aby = b.y - a.y, bcx = c.x - b.x, bcy = c.y - b.y;
    const cross = abx * bcy - aby * bcx;
    const den = Math.hypot(abx, aby) * Math.hypot(bcx, bcy) * Math.hypot(c.x - a.x, c.y - a.y);
    k[i] = den > 0 ? 2 * cross / den : 0;
  }
  if (n > 2) { k[0] = k[1]; k[n - 1] = k[n - 2]; }
  return k;
};

/* the polyline as an SVG path the nib can be handed: the caller draws it BY LENGTH (42 s42.1). */
export const clothoidPath = (pts) => pts.map((p, i) => (i ? "L" : "M") + p.x.toFixed(2) + " " + p.y.toFixed(2)).join(" ");
