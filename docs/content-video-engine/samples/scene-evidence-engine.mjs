/* THE ENGINE (P51 T1). This file is the scene-evidence player's whole runtime: the kinetics
   and species regions inlined by sync_kinetics.py, the registry, the painters, the probes and
   the filmstrip export. It serves BOTH forms of the page from one text:
     - split   (a build): scene-evidence-player.template.html is a shell that imports this
               module, and mount() fetches the timeline and the asset map beside it;
     - single  (the goldens, the tests, any old committed player): the shell inlines this text
               with its module syntax stripped (sync_kinetics.inline_text) and mount() reads
               the two <script type="application/json"> slots the shell already carries.
   The loader below is the only branch between the two. Everything under it is the body the
   template carried before the split, unchanged. `export { mount }` sits at the foot because
   inline_text drops an `export {...}` list, and `"use strict"` stays the body's first
   statement (a default parameter would make that directive a SyntaxError), so the inlined
   copy is strict exactly where the old IIFE was. */

/* P51 T4 - THE HOT-RELOAD STATE, module level so mount() can be run a second time on the same
   page. `reload(timeline)` at the foot puts the shell's own DOM back and calls mount() again -
   the same code path mount runs after the data arrives, no page load, the scrub position kept.
     __shellHTML  the body exactly as the shell delivered it, taken on the FIRST mount and only
                  when the page is watched (?watch=1): a single-file page carries its whole asset
                  bundle in that string, so a golden render never pays for the snapshot;
     __assets     the asset map, parsed once - a reload changes the timeline, never the assets;
     __mountGen   the live mount's token: the play loop of a mount that has been replaced sees a
                  moved token and stops instead of painting a dead DOM;
     __onResize   the live fitStage, so the window carries one resize listener, not one per mount. */
let __shellHTML = null, __assets = null, __mountGen = 0, __onResize = null;

async function mount(doc) {
  "use strict";
  /* $ is declared FIRST. It used to sit below the title/scrub lines that
     call it, so the whole IIFE threw ReferenceError on load and the stage
     rendered black - passing every structural check while showing nothing. */
  const $ = (id) => document.getElementById(id);
  const D = doc || document;   /* the only doc-scoped reads in the body - everything below keeps `document` */
  const MY = ++__mountGen;     /* P51 T4: this mount's token - a reload moves it and the old play loop stops */
  const WATCH = typeof location !== "undefined" && /[?&]watch=1/.test(location.search);
  if (WATCH && __shellHTML === null) __shellHTML = D.body.innerHTML;   /* taken before one node of this mount exists */
  const slot = (id) => { const el = D.getElementById(id); return { el, text: el.textContent.trim() }; };
  const tlSlot = slot("timeline-data"), aSlot = slot("asset-data");
  const TL = tlSlot.text ? JSON.parse(tlSlot.text) : await (await fetch(tlSlot.el.dataset.src, { cache: "no-store" })).json();
  const A  = __assets || (aSlot.text ? JSON.parse(aSlot.text) : await (await fetch(aSlot.el.dataset.src,  { cache: "no-store" })).json());
  if (WATCH) __assets = A;     /* a reload re-mounts on the SAME assets - never a second fetch of a 31 MB map */
  /* P39 T4 - THE KILL SWITCH. Every capability that changes rendered output reads a flag
     from timeline.kinetics and DEFAULTS TO FALSE, which means the behaviour tagged at
     player-baseline-2026-09-04. A bad result is one timeline field away from the old
     render, never a debugging session. Unknown names are ignored with a warning, so a
     typo cannot turn anything on. The six names are doc 47 s1 / P38; add a name here and
     in test_kinetics_flags.py in the same commit, default false, or the test fails. */
  const KINETICS_DEFAULTS = Object.freeze({
    curvature_stroke: false,   // 42.1 two-thirds power law on drawOn
    analytic_spring:  false,   // 42.2 closed-form spring evaluator
    area_squash:      false,   // 42.3 det=1 squash matrix
    arap_morph:       false,   // 43.5B polar-decomposition morph
    dqs_skinning:     false,   // 48.3 SE(2) geodesic joint blend
    prop_attach:      false,   // 48.5 cached-offset prop attachment
    min_jerk:         false,   // FINDING-the-animation-math s2: minimum-jerk quintic on spatial transitions (the wipe front, the suck)
    km_ink:           false,   // 44.1 Kubelka-Munk where two ink passes overlap (the soak's stains, the highlighter band)
    idle:             false,   // E49 the named subtle idle on every held thing - page, plate, dock, pill, caption (P47 T5)
    camera:           false,   // P49 T2 the persistent camera: the three species through kinetics/camera.mjs (pixel-identical), authored keys per scene, the __camera probe
    stop_action:      false,   // P47 T1 the arrivals: a dock or a pill declared arrive: throw | land with a mass
  });
  const KIN = Object.assign({}, KINETICS_DEFAULTS,
    (TL.kinetics && typeof TL.kinetics === "object") ? TL.kinetics : {});
  for (const k of Object.keys(TL.kinetics || {}))
    if (!(k in KINETICS_DEFAULTS)) console.warn("kinetics: unknown flag ignored: " + k);
  const kin = (name) => KIN[name] === true;
  /* Runtime comes from the TIMELINE, never hardcoded. A template that
     carries the sample's duration clamps every episode to it. */
  if (TL.title) { document.title = TL.title; $("eptitle").textContent = TL.title;
    $("epsub").textContent = TL.subtitle || ""; }
  const scrub = $("scrub");
  const DUR = TL.runtime_s || (TL.scenes.length ? TL.scenes[TL.scenes.length-1].span[1] : 0);
  scrub.max = DUR;
  const stage = $("stage"), fit = $("fit");
  /* Read once from the CSS variables so the JS and the layout can never disagree. */
  /* The timeline declares its own frame. Set the attribute BEFORE the constants
     below read the CSS variables, or the JS and the layout disagree by one frame.
     Absent or "16:9" keeps the original geometry exactly. */
  if (String(TL.aspect || "16:9") === "9:16") document.documentElement.setAttribute("data-aspect", "9:16");
  const STAGE_W = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--stage-w")) || 1920;
  const STAGE_H = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--stage-h")) || 1080;
  const PORTRAIT = STAGE_H > STAGE_W;   /* 9:16 (P41, doc 49 s49.1 amended 2026-09-05): the chart IS the world */
  $("species").setAttribute("viewBox", `0 0 ${STAGE_W} ${STAGE_H}`);
  $("species-under").setAttribute("viewBox", `0 0 ${STAGE_W} ${STAGE_H}`);   /* the under layer shares the stage frame - left on the landscape default it placed a portrait spotlight at the axis corner (2026-09-08) */
  const fitStage = () => { stage.style.transform = `scale(${fit.clientWidth / STAGE_W})`; };
  if (__onResize) removeEventListener("resize", __onResize);   /* P51 T4: one live listener, not one per mount */
  __onResize = fitStage;
  addEventListener("resize", fitStage); fitStage();

  const clamp01 = (v) => Math.min(1, Math.max(0, v));
  const io = (k) => k < 0.5 ? 2*k*k : 1 - Math.pow(-2*k+2, 2)/2;
  /* cubic-bezier(.16,1,.3,1) ~ expo-out: a long soft settle, the reference's
     signature. cubic-bezier(.77,0,.175,1) ~ quart-in-out for the scene wipe:
     snappy, not sluggish. */
  const expoOut = (k) => (k >= 1 ? 1 : 1 - Math.pow(2, -10 * k));
  const quartIO = (k) => (k < 0.5 ? 8*k*k*k*k : 1 - Math.pow(-2*k+2, 4)/2);
  /* THE TIMING MODULE (FINDING-the-animation-math, build order 2; wired 2026-09-05 behind kinetics flags). The
     math below is INLINED from content/video_engine/scripts/kinetics/*.mjs by sync_kinetics.py (P43 T1): edit the
     module, run `python sync_kinetics.py --write`; `--check` fails the tests on drift. The template stays standalone. */
  /* KINETICS:BEGIN ease */
  /* kinetics/ease.mjs - the timing module, part 1 (FINDING-the-animation-math s2; wired 2026-09-05 behind
     kinetics.min_jerk). This file is the SOURCE OF TRUTH: sync_kinetics.py inlines it into the scene-evidence
     player between the KINETICS:BEGIN ease and KINETICS:END markers, so the template stays standalone and
     `node --test` reaches the math (P43 T1). Self-contained on purpose: nothing here reads a template symbol.
     minJerk - Flash & Hogan 1985, the jerk-minimising quintic 10t^3 - 15t^4 + 6t^5: zero velocity AND zero
               acceleration at both ends, so a spatial transition neither snaps nor sags. */
  const minJerk = (u) => { u = Math.min(1, Math.max(0, u)); return u * u * u * (10 - 15 * u + 6 * u * u); };
  /* KINETICS:END */
  /* KINETICS:BEGIN spring */
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

  const SPRING = Object.freeze({ MP: 0.04, SETTLE: 6 });

  /* overshoot + settle -> the model's parameters */
  const springParams = (Mp = SPRING.MP, settle = SPRING.SETTLE) => {
    if (!(Mp > 0)) return { z: 1, w: settle, wd: 0 };
    const L = Math.log(Math.min(Mp, 0.999)), z = -L / Math.sqrt(Math.PI * Math.PI + L * L), w = settle / z;
    return { z, w, wd: w * Math.sqrt(1 - z * z) };
  };

  /* position, velocity and acceleration at t >= 0 */
  const springEval = (t, p) => {
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
  const POP = springParams(SPRING.MP);
  const springPop = (u, Mp = 0.04) => {
    if (u >= 1) return 1; if (u <= 0) return 0;
    return springEval(u, Mp === SPRING.MP ? POP : springParams(Mp)).x;
  };
  /* KINETICS:END */
  /* KINETICS:BEGIN stroke */
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

  const STROKE = Object.freeze({ KAPPA0: 1 / 300, GAMMA: 1, LAMBDA_W: 0.12, ALPHA_W: 1, SMOOTH: 2, SAMPLE_PX: 6, MIN_N: 24, MAX_N: 240 });

  /* Menger curvature of three points, 1 / circumradius: 0 on a straight, finite on a collapsed triple. */
  const menger = (a, b, c) => {
    const abx = b.x - a.x, aby = b.y - a.y, bcx = c.x - b.x, bcy = c.y - b.y, acx = c.x - a.x, acy = c.y - a.y;
    const cross = Math.abs(abx * bcy - aby * bcx);
    const den = Math.hypot(abx, aby) * Math.hypot(bcx, bcy) * Math.hypot(acx, acy);
    return den > 0 ? 2 * cross / den : 0;
  };

  /* The profile of one stroke from its samples along the path: arclength s, curvature kappa (box-smoothed - a flattened
     curve is noisy at the sample pitch), speed v, width factor w, and the clock t(s) normalised to [0, 1]. */
  const strokeProfile = (pts, o = {}) => {
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
    return { n, L: n ? s[n - 1] : 0, s, kappa, v, w, t, vMax };
  };

  const bracket = (arr, x, n) => { let lo = 0, hi = n - 1; while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (arr[mid] <= x) lo = mid; else hi = mid; } return [lo, hi]; };

  /* The arclength drawn at normalised time u in [0, 1]: the quintic clock, then the inverse of the tabulated t(s). */
  const strokeS = (prof, u) => {
    const tau = minJerk(u), { t, s, n } = prof;
    if (n < 2 || tau <= 0) return 0;
    if (tau >= 1) return prof.L;
    const [lo, hi] = bracket(t, tau, n), dt = t[hi] - t[lo];
    return dt > 0 ? s[lo] + (tau - t[lo]) * (s[hi] - s[lo]) / dt : s[lo];
  };

  /* A profile column (prof.v, prof.w, prof.kappa) at arclength x, linear between samples. */
  const strokeAt = (prof, arr, x) => {
    const { s, n } = prof;
    if (n < 2 || x <= 0) return n ? arr[0] : 0;
    if (x >= s[n - 1]) return arr[n - 1];
    const [lo, hi] = bracket(s, x, n), ds = s[hi] - s[lo];
    return ds > 0 ? arr[lo] + (x - s[lo]) * (arr[hi] - arr[lo]) / ds : arr[lo];
  };
  /* KINETICS:END */
  /* KINETICS:BEGIN clothoid */
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

  const CLOTHOID = Object.freeze({
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
  const wrapPi = (a) => {
    let v = (a + Math.PI) % clTAU;
    if (v <= 0) v += clTAU;
    return v - Math.PI;
  };

  /* a tangent given as a heading in radians, as [x, y] or as {x, y} -> the heading in radians */
  const angleOf = (t) => {
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
  const fresnel = (x) => {
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
  const fresnelMoments = (a, b, c) => {
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
  const clothoidFit = (p0, t0, p1, t1) => {
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
  const clothoidAt = (fit, tau) => {
    const u = Math.min(1, Math.max(0, tau)), A = fit.A, B = fit.B, th0 = fit.theta0;
    const m = fresnelMoments(A * u * u, B * u, th0);
    return { x: fit.x0 + fit.L * u * m.X, y: fit.y0 + fit.L * u * m.Y,
             s: fit.L * u, k: fit.k0 + fit.dk * fit.L * u, theta: th0 + B * u + A * u * u };
  };

  /* THE POLYLINE the stroke engine draws BY LENGTH: n samples of the fitted segment, each carrying its own
     arclength and curvature so 42 s42.1's profile can be read straight off it. */
  const clothoid = (p0, t0, p1, t1, n = CLOTHOID.SAMPLES) => {
    const fit = clothoidFit(p0, t0, p1, t1), N = Math.max(2, n | 0), out = new Array(N);
    for (let i = 0; i < N; i++) out[i] = clothoidAt(fit, i / (N - 1));
    return out;
  };

  /* THE TWO-SEGMENT G2 FIT (the S-curve). Two clothoids meet at the chord's midpoint; the ONE free parameter
     is the heading there, and it is chosen so the curvature the first segment ARRIVES with is the curvature
     the second LEAVES with - G2 at the join by construction, not by luck. The sweep is bracketed either side
     of the chord's own direction and bisected, exactly as the single fit's A is. `ok` false = no match inside
     JOIN_SWEEP; the caller then has two G1 segments and knows it. */
  const clothoidS = (p0, t0, p1, t1, n = CLOTHOID.SAMPLES) => {
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
  const bezierOf = (p0, t0, p1, t1, n = CLOTHOID.SAMPLES, handle = CLOTHOID.BEZ_HANDLE) => {
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
  const curvatureOf = (pts) => {
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
  const clothoidPath = (pts) => pts.map((p, i) => (i ? "L" : "M") + p.x.toFixed(2) + " " + p.y.toFixed(2)).join(" ");
  /* KINETICS:END */
  /* KINETICS:BEGIN span */
  /* species/span.mjs - THE SPAN (P50 T4; BACKLOG R26-25, the intake's Archetype 5; Bravos shots 107-110's
     "Decades" bracket). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between
     KINETICS:BEGIN span and KINETICS:END. It imports nothing, and its region sits with the kinetics laws
     rather than in the species block at the foot of the file - on purpose: a PAGE species' math is called by
     the page's PERFORM layer, which is written hundreds of lines above the species block, and a const has to
     exist before the function that closes over it is built.

     WHEN: the sentence SPANS a period on a chart - a regime, an epoch, "the decade" - shaded behind the line
     with its name. A BRACKET measures two data; a SPAN names a stretch of time. That is the whole difference,
     and it is why this is a second species and not a bracket option: a bracket's label is a NUMBER it measured,
     a span's label is a NAME it gives.

     THE LAW, a pure function of t:
       shade  - the band between the two declared edges fades in over IN_S to ALPHA, behind every line (it is
                ground, not ink on top - the same rule the spread follows).
       label  - written above the band BY THE HAND, glyph after glyph, over WRITE of the word, starting when
                the shade is in. Above the band where there is room for it, inside its top edge where there
                is not (a chart that fills its box has nothing over it).
     THE EDGES. `from` and `to` are each either a DATUM INDEX (an integer: the page's own index, the one a
     bracket and a figure use) or an X-FRACTION (a number in 0..1 along the drawn series' own x extent, for a
     period that falls between two data). Both are resolved on the ACTIVE chart state every frame, from the
     same live points a bracket reads (R26-28): a rescale moves the band with the data, and a window that has
     dropped one of the two edges hides it rather than drawing it in the wrong place.

     THE PAINTER IS NOT HERE, and that is a finding, not an omission (P50 T4, 2026-09-11): a PAGE species is
     built and painted by the page's own perform layer - inside the chart's viewBox, on the page state `st`,
     under the active state's park transform - while SPECIES_PAINTERS hands a painter the stage-px overlay and
     the scene's clock. Registering a page species in that registry would paint it in the wrong space and leave
     the perform layer none the wiser. So the MATH is here, pure and tested, and the perform layer calls it in
     a dozen lines. Closing that gap - one registry both layers can route through - is P51 T1's business.
     The dials below are ours to tune (42 s42.5), not findings. */

  const SPAN = Object.freeze({
    IN_S: 0.45,       /* the shade's fade-in: a period ARRIVES, it does not cut in - slower than a bracket's tick, because nothing is being measured */
    ALPHA: 0.16,      /* ... and what it settles at: enough to read as a region behind the line, never enough to fight it (the spread bleeds to 0.30 because the gap IS its argument; a span is only the room the argument happens in) */
    WRITE: 0.5,       /* the share of the word the label's hand takes, after the shade is in */
    PAD_T: 44,        /* the band's reach above the highest point of the drawn data, in the chart's viewBox units ... */
    PAD_B: 44,        /* ... and below the lowest: it is a band behind the chart, not a box around the line */
    LABEL_DY: 16,     /* the label's baseline above the band's top edge, where the band has room above it ... */
    LABEL_IN: 2.1,    /* ... and, where it does not, inside the top edge by this many of the label's own sizes: two lines down, clear of the plot's own top furniture (the unit caption sits on the first line inside the plot - read in the frame, 2026-09-11) */
    LABEL_ROOM: 1.3,  /* "room above" means this many label sizes clear of the chart's top - otherwise the name is written inside the band */
    MIN_W: 6,         /* a band narrower than this is not a period - it is two adjacent data, which is a bracket's job */
  });

  const span01 = (v) => Math.min(1, Math.max(0, v));

  /* is this edge a DATUM INDEX (an integer) or an X-FRACTION? */
  const spanIsIndex = (v) => Number.isInteger(v);

  /* ONE EDGE -> x in the chart's viewBox. `entries` is the series' live points in lpPointsNow's shape,
     [{i, p: [x, y]}]: an index resolves to the point that CARRIES it (a window that dropped it -> null), a
     fraction to that position along the drawn series' own x extent. */
  const spanEdgeX = (entries, v) => {
    if (!Array.isArray(entries) || entries.length < 2) return null;
    if (spanIsIndex(v)) { const e = entries.find((q) => q.i === v); return e ? e.p[0] : null; }
    const f = +v;
    if (!Number.isFinite(f)) return null;
    const a = entries[0].p[0], b = entries[entries.length - 1].p[0];
    return a + span01(f) * (b - a);
  };

  /* the band's vertical reach: every drawn series' points, padded - so the shade stands behind the whole
     chart and moves with it, and never has to be told where the plot box is */
  const spanExtent = (lists) => {
    let y0 = Infinity, y1 = -Infinity;
    for (const l of lists || []) for (const q of (l || [])) { y0 = Math.min(y0, q.p[1]); y1 = Math.max(y1, q.p[1]); }
    return Number.isFinite(y0) && Number.isFinite(y1) ? { y0: y0 - SPAN.PAD_T, y1: y1 + SPAN.PAD_B } : null;
  };

  /* THE BAND this frame, or null when either edge has left the window (the bracket's rule: nothing to name,
     nothing drawn). `entries` is the named series' live points, `lists` every series', `H` the chart's viewBox
     height when the caller knows it - the band is clipped to the page rather than drawn off it. */
  const spanBand = (entries, lists, from, to, H) => {
    const a = spanEdgeX(entries, from), b = spanEdgeX(entries, to), ext = spanExtent(lists);
    if (a === null || b === null || !ext) return null;
    const x0 = Math.min(a, b), x1 = Math.max(a, b);
    if (!(x1 - x0 >= SPAN.MIN_W)) return null;
    const top = Number.isFinite(H) ? Math.max(0, ext.y0) : ext.y0;
    const bot = Number.isFinite(H) ? Math.min(H, ext.y1) : ext.y1;
    if (!(bot > top)) return null;
    return { x: x0, w: x1 - x0, y: top, h: bot - top, cx: (x0 + x1) / 2 };
  };

  /* where the name is written: above the band when the chart leaves room over it, inside its top edge when
     the chart fills its box (the bracket's own rule for a label with nowhere to stand) */
  const spanLabelY = (band, fs) => (band.y >= fs * SPAN.LABEL_ROOM ? band.y - SPAN.LABEL_DY : band.y + fs * SPAN.LABEL_IN);

  /* THE POSE at t: is it up, how deep is the shade, how far has the hand written. */
  const spanPose = (sp, t) => {
    const at = +sp.at, dur = Math.max(0.001, +sp.dur || 1), d = t - at;
    const shade = span01(d / SPAN.IN_S);
    return { on: d >= 0, shade, alpha: SPAN.ALPHA * shade, write: span01((d - SPAN.IN_S) / (dur * SPAN.WRITE)) };
  };

  /* one glyph's opacity as the hand writes the label: each glyph over its share of the write, with the 1.6
     overlap the bracket and the figure use, so the line reads as a hand and not as a ticker. The share is
     1 / (n + 0.6), not 1 / n, so the LAST glyph is fully in exactly when the write ends - at 1 / n the tail
     of the name would still be at 0.625 when the word was over (the bracket buys the same slack by writing
     its label over only part of its own window). */
  const spanGlyph = (write, j, n) => {
    const per = 1 / (Math.max(1, n | 0) + 1.6 - 1);
    return span01((write - j * per) / (per * 1.6));
  };
  /* KINETICS:END */
  /* KINETICS:BEGIN thread */
  /* species/thread.mjs - THE WIRE (P50 T15, HF-16: "the three threads - the wire, the ruler, the protagonist chip -
     one continuous line as the film's spine"). SOURCE OF TRUTH, inlined into the scene-evidence player by
     sync_kinetics.py between KINETICS:BEGIN thread and KINETICS:END. It imports nothing, and its region sits with the
     kinetics laws rather than in the species block at the foot of the file, for span.mjs's reason: a PAGE species'
     math is called by the page's build, which is written hundreds of lines above the species block.

     WHEN: two pages in a row are the same argument, and ONE element of the first belongs under the second - the
     holdings baseline still lying under the Meta bars. Our pages already persist a topic (s9.15); what HF-16 names
     is a single element that persists across a CUT, so the second world reads as the first one continued rather
     than as a new subject.

     THE GRAMMAR, and why it is the plate id's. A `chart_to extend` cannot do this: a species lives on ONE scene and
     addresses that scene's own `world.page_states`, which are built from the SAME series file - it has no way to name
     a mark on the world before it. Crossing the boundary inside `extend` would mean teaching species to reach into
     another scene, which is a far bigger mechanism than the thing it buys. So the thread is declared where the page
     itself is declared, on the ARRIVING page's plate id: `;thread=<mark key>` - "this page starts with that mark
     already on it". It needs no new species, it survives every entry the page can make (cut, mount, spiral), and it
     reads in the shot table as what it is: a property of the page, not an event in it.

     THE CARRY, and why it is a similarity. The mark survives the cut by staying WHERE IT WAS ON THE STAGE. Both
     pages draw inside an <svg> whose viewBox is fitted into the page's chart box, so each page is one similarity
     from its own drawing units to stage pixels (`threadFit` - the browser's own preserveAspectRatio="xMidYMid meet":
     uniform scale, centred). The carry is therefore source-fit -> stage -> target-fit-inverse, one composition of two
     similarities (`threadCarry`), and the points it returns are the SAME PIXELS the outgoing page drew, expressed in
     the incoming page's units so that everything the page does afterwards - the park, a rescale's transform, the
     camera - carries the wire with it.

     THE POSE is a pure function of t and has one job: the wire is ALREADY DRAWN when the page arrives (that is the
     whole point - it did not come from anywhere), and it recedes to a ground line over FADE_S so the new page's own
     ink reads on top of it. Nothing draws on and nothing is re-timed: `threadPose` runs on the page's own clock, not
     a second one. The dials below are ours to tune (42 s42.5), not findings. */

  const THREAD = Object.freeze({
    ALPHA: 0.34,      /* what the carried mark settles at: present enough to be the same line, faint enough that the new page's ink is the subject */
    FROM: 0.85,       /* ... and what it starts at on the page's first frame - it was the SUBJECT one frame ago, so it does not appear already dimmed */
    FADE_S: 0.9,      /* the recede, over the new page's cream: the wire is handed over, not cut away */
    WIDTH: 0.62,      /* its stroke, as a share of the width the source drew it at: a ground line is thinner than an argument */
    MIN_PTS: 2,       /* fewer than two points is not a line, and nothing is carried */
  });

  const th01 = (v) => Math.min(1, Math.max(0, v));

  /* THE FIT of one chart: its viewBox (vw x vh) contained in its stage box, uniform scale, centred. */
  const threadFit = (box, vw, vh) => {
    const s = Math.min(box.w / Math.max(1e-6, vw), box.h / Math.max(1e-6, vh));
    return { s, tx: box.x + (box.w - vw * s) / 2, ty: box.y + (box.h - vh * s) / 2 };
  };

  /* a point in a chart's own units -> stage px, and back: each other's inverse to the bit */
  const threadToStage = (fit, p) => [fit.s * p[0] + fit.tx, fit.s * p[1] + fit.ty];
  const threadToLocal = (fit, q) => [(q[0] - fit.tx) / fit.s, (q[1] - fit.ty) / fit.s];

  /* THE CARRY: the outgoing page's polyline, in the incoming page's units, standing on the same pixels. */
  const threadCarry = (pts, srcFit, dstFit) => {
    if (!Array.isArray(pts) || pts.length < THREAD.MIN_PTS) return null;
    return pts.map((p) => threadToLocal(dstFit, threadToStage(srcFit, p)));
  };

  /* the stroke width that carries with it: the source's width through both fits, thinned to a ground line */
  const threadWidth = (w, srcFit, dstFit) => Math.max(1, (+w || 4) * (srcFit.s / Math.max(1e-6, dstFit.s)) * THREAD.WIDTH);

  /* THE POSE at the page's own clock: already drawn at the first frame, receding to a ground line. */
  const threadPose = (tr) => {
    const k = th01((+tr || 0) / THREAD.FADE_S);
    return { drawn: 1, alpha: THREAD.FROM + (THREAD.ALPHA - THREAD.FROM) * k };
  };

  /* the path data for a carried polyline - a plain polyline, because it IS the line that was drawn, not a new curve */
  const threadPath = (pts) => (!pts || pts.length < THREAD.MIN_PTS) ? ""
    : pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(2) + " " + p[1].toFixed(2)).join(" ");
  /* KINETICS:END */
  /* KINETICS:BEGIN tiers */
  /* species/tiers.mjs - N-TIER PAGES (P50 T9; BACKLOG R26-24; Bravos shots 35-36's two-panel SPR).
     SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between
     KINETICS:BEGIN tiers and KINETICS:END, AFTER ease (it uses minJerk). Its region sits with the
     kinetics laws rather than in the species block at the foot of the file, for the reason span.mjs
     gives: a PAGE's math is called by builders and by the perform layer, both written hundreds of
     lines above the species block, and a const has to exist before the function that closes over it.

     WHEN: the sentence compares the SAME quantity across two, three or four subjects over the same
     period - Japan's reserve and America's, one unit, one decade. That is a small multiple: N bands
     stacked, each with its own y-scale and its own honest zero (E53 s4), sharing ONE x. It is NOT the
     overlay: when two series must be read AGAINST each other, E53 s4 says they belong on one plot with
     the bars keeping the zero and the line riding over them (`tiers: true` on a combo page, the
     macro-chart intake's Archetype 1). Separating those would throw away the comparison. Separate
     bands are for the comparison that is made by SHAPE, band against band, on a shared time axis.

     THE LAW, all of it a pure function of the page's geometry and the build fraction c:
       bands   - the plot is cut into N equal bands with a gutter of GAP of a band's height between
                 them. The MIRROR of ledger_page.tier_bands (python, the compiler's dock placement):
                 one law in two languages, the same two dials, pinned on both sides.
       domain  - each band's own y-scale, from an HONEST ZERO by default: a band whose zero is dropped
                 exaggerates its own shape, and a page of small multiples is read shape against shape.
                 A band may opt out (`from_zero: false` in its axes) and the page's judge row says so.
       ticks   - TICKS gridlines a band, and the unit written once per band beside its own top tick:
                 a band is a chart, and a chart with no unit is a number with no meaning.
       draw    - the bands draw IN TURN: band i starts at its own share of the build clock, and a
                 `build_to` per tier (a tier IS a series index on this page) puts each band on its own
                 WORD instead. The drop of one band is measured by the bracket in its `form: "bar"`.
     The dials are ours to tune (42 s42.5), not findings. */

  const TIERS = Object.freeze({
    GAP: 0.20,        /* the gutter between two bands, as a share of a band's own height - ledger_page.TIER_GAP is the same number in python [DERIVED, read off the first frame: at 0.10 a band's name sat on the floor tick label of the band above] */
    PAD: 0.08,        /* headroom over a band's tallest value, as a share of its own span: a line that touches its band's ceiling reads as clipped */
    TICKS: 2,         /* gridlines a band (the combo's tiered case uses 2-3 for the same reason: a short band wants fewer ticks) */
    NAME_DY: 6,       /* the band's NAME sits this far above the band's top edge, in the chart's viewBox units - inside the gutter, clear of the band above's floor label */
    STAGGER: 0.34,    /* the share of the build clock between one band's start and the next one's */
    MIN_H: 46,        /* a band shorter than this in viewBox units cannot carry a scale and a name; the compiler's ceiling of 4 is what keeps it from happening */
  });

  const tier01 = (v) => Math.min(1, Math.max(0, v));

  /* THE BANDS: N boxes between `top` and `bot`, top to bottom, each {y0, y1, h}. */
  const tierBands = (top, bot, n, gap = TIERS.GAP) => {
    const k = Math.max(0, n | 0);
    if (!k) return [];
    const h = (bot - top) / (k + (k - 1) * gap);
    return Array.from({ length: k }, (_, i) => {
      const y0 = top + i * h * (1 + gap);
      return { y0, y1: y0 + h, h };
    });
  };

  /* THE DOMAIN of one band: its own values, with the zero kept honest unless the band drops it. The
     pad is one-sided on a from-zero band (the floor IS the claim) and two-sided when it is not. */
  const tierDomain = (vals, fromZero = true) => {
    /* a null or empty datum is NOT a zero (Number(null) is 0, which would put a floor under a band that has none) */
    const nums = (vals || []).filter((v) => v !== null && v !== undefined && v !== "" && Number.isFinite(+v)).map(Number);
    if (!nums.length) return [0, 1];
    let lo = Math.min(...nums), hi = Math.max(...nums);
    if (fromZero) { lo = Math.min(0, lo); hi = Math.max(0, hi); }
    const span = hi - lo || Math.abs(hi) || 1;
    hi += span * TIERS.PAD;
    if (!fromZero) lo -= span * TIERS.PAD;
    return [lo, hi];
  };

  /* a value's y inside its band */
  const tierY = (band, lo, hi, v) => band.y1 - (Number(v) - lo) / ((hi - lo) || 1) * band.h;

  /* the nice gridline values of a band: TICKS of them inside the domain, the zero always among them
     when the domain holds it (an honest zero that is not drawn is not read) */
  const tierTicks = (lo, hi, n = TIERS.TICKS) => {
    const raw = (hi - lo) / Math.max(1, n);
    const e = Math.pow(10, Math.floor(Math.log10(Math.max(1e-12, raw)))), f = raw / e;
    const step = e * (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10);
    const out = [];
    for (let v = Math.ceil(lo / step - 1e-9) * step; v <= hi + 1e-9; v += step) out.push(Math.abs(v) < step * 1e-6 ? 0 : v);
    return out;
  };

  /* THE BUILD: band i starts at i * STAGGER of the clock and draws over what is left of it, so the
     bands arrive in turn even before a word is put on them. A `build_to` per tier overrides this by
     capping the band's own stroke - the caps machinery is the page's, not ours. */
  const tierStagger = (i, n) => (n <= 1 ? 0 : Math.min(0.9, (i | 0) * TIERS.STAGGER));
  const tierBuildK = (c, i, n) => minJerk(tier01((c - tierStagger(i, n)) / Math.max(0.05, 1 - tierStagger(n - 1, n))));
  /* KINETICS:END */
  /* KINETICS:BEGIN treemap */
  /* species/treemap.mjs - THE CENSUS PAGE and its X MARKS (P50 T6; E53 s1's second amendment, the
     census exception, ruled 2026-09-10; Bravos shots 89-91). SOURCE OF TRUTH, inlined into the
     scene-evidence player by sync_kinetics.py between KINETICS:BEGIN treemap and KINETICS:END, AFTER
     ease. Its region sits with the kinetics laws for span.mjs's reason: the page's builder and the
     page's PERFORM layer both call it, and both are written far above the species block.

     WHERE THE LAYOUT IS. Not here. The squarified rectangles (Bruls, Huizing & van Wijk 2000, tuned
     toward 3:2 rather than the paper's square - Heer & Bostock 2010) are computed by ledger_page.py at
     BUILD time, inside page_boxes' own plot, and ride the spec as fractions of that plot. This module
     maps a cell's fractions into the rect it is drawn in and owns the CLOCK. That split is the point:
     a layout computed at paint time is a re-layout waiting to happen, and E58 (with Sondag 2018) says
     the shrink afterwards is ONE affine transform - cells never hop. `treemapRect` is linear in the
     plot rect, which is what makes the park free: scaling the rect scales every cell exactly.

     WHEN: the sentence takes a CENSUS - "China sells to everyone", "three partners, 41 % of exports".
     Never a size comparison between two cells: that is a bar's job, and `ledger_page.py` refuses the
     file whose own words make one.

     THE LAW, a pure function of the build fraction c and of t:
       cells  - they land in LAYOUT order (largest first), each over CELL_IN of the clock, staggered
                across STAGGER of it - the bars' law, on a mosaic; the label writes once its own cell
                is nearly in, and only on the cells the compiler said had room (the research's floors).
       cross  - the named cells take a two-stroke X over CROSS_S (the chip's cross, the same dial: one
                cross law on the page) and dim to DIM while it is struck. The X is the mark; the DIM is
                what keeps a crossed cell part of the census instead of deleting it.
       share  - and the crossed share is WRITTEN by the hand over WRITE of the word - E53 s1's second
                amendment (b), which is why the species carries both halves and the compiler refuses
                one without the other.
     The dials are ours to tune (42 s42.5), not findings. */

  const TREEMAP = Object.freeze({
    CELL_IN: 0.30,      /* one cell's own landing, as a share of the build clock */
    STAGGER: 0.70,      /* ... and the share of the clock spent handing from the first cell to the last */
    LABEL_AT: 0.55,     /* a cell's label writes from this much of its own landing: the tile first, its name after */
    RISE: 0.35,         /* the cell grows from this share of its own size as it lands (the bar's scale, in two dimensions) */
    CROSS_S: 0.5,       /* the X's two strokes together - the chip's own dial (species/chip.mjs CROSS_S), deliberately */
    CROSS_INSET: 0.12,  /* the X's inset from the cell's corners, as a share of the cell's SHORTER side */
    DIM: 0.55,          /* what a crossed cell dims to: struck, still legible, still counted (the census does not delete) */
    WRITE: 0.45,        /* the share of the word the hand takes to write the crossed share, once the X's are struck */
    WRITE_AT: 0.35,     /* ... starting here, so the number arrives while the last X is still being drawn */
  });

  const tm01 = (v) => Math.min(1, Math.max(0, v));

  /* A CELL'S RECT inside the plot it is drawn in. Linear in the plot: scale or translate the plot and
     every cell follows exactly, which is the park (E58: one affine transform, never a re-layout). */
  const treemapRect = (cell, plot) => ({
    x: plot.x + (+cell.fx || 0) * plot.w,
    y: plot.y + (+cell.fy || 0) * plot.h,
    w: (+cell.fw || 0) * plot.w,
    h: (+cell.fh || 0) * plot.h,
  });

  /* the landing of cell i of n at build fraction c: layout order, the bars' stagger */
  const treemapCellK = (c, i, n) => {
    const span = n > 1 ? TREEMAP.STAGGER / (n - 1) : 0;
    return tm01((c - (i | 0) * span) / TREEMAP.CELL_IN);
  };

  /* the cell's own scale as it lands, about its centre, and its label's opacity */
  const treemapCellScale = (k) => TREEMAP.RISE + (1 - TREEMAP.RISE) * k;
  const treemapLabelK = (k) => tm01((k - TREEMAP.LABEL_AT) / (1 - TREEMAP.LABEL_AT));

  /* WHICH CELLS a cross names, by label, in the page's own order. A name the page does not carry
     resolves to nothing here and is refused at build time by the compiler - the player never guesses. */
  const treemapNamed = (cells, names) => {
    const want = new Set((names || []).map(String));
    return (cells || []).map((c, i) => (want.has(String(c.label)) ? i : -1)).filter((i) => i >= 0);
  };

  /* THE CROSS at t: 0 until the species' word, 1 CROSS_S later. */
  const treemapCrossF = (sp, t) => tm01((t - +sp.at) / TREEMAP.CROSS_S);

  /* the two strokes of the X from the cross's fraction: the first over its first half, the second over
     the second - the chip's law, so one X on the page is drawn like every other */
  const treemapStrokes = (cross) => [tm01(cross * 2), tm01(cross * 2 - 1)];

  /* the two diagonals of a cell's X, inset from its corners by a share of its shorter side */
  const treemapCrossLines = (r, inset = TREEMAP.CROSS_INSET) => {
    const d = Math.min(r.w, r.h) * inset;
    const x0 = r.x + d, x1 = r.x + r.w - d, y0 = r.y + d, y1 = r.y + r.h - d;
    return [{ x1: x0, y1: y0, x2: x1, y2: y1 }, { x1: x1, y1: y0, x2: x0, y2: y1 }];
  };

  /* a crossed cell dims while it is struck, and holds there: it is still one of the parts */
  const treemapDim = (cross) => 1 - (1 - TREEMAP.DIM) * tm01(cross);

  /* the hand writing the crossed share, and one glyph of it (the span's and the figure's own law: the
     share is 1 / (n + 0.6) so the last glyph lands exactly as the write ends) */
  const treemapWrite = (sp, t) => {
    const dur = Math.max(0.001, +sp.dur || 1);
    return tm01((t - +sp.at - TREEMAP.WRITE_AT) / (dur * TREEMAP.WRITE));
  };
  const treemapGlyph = (write, j, n) => {
    const per = 1 / (Math.max(1, n | 0) + 0.6);
    return tm01((write - j * per) / (per * 1.6));
  };
  /* KINETICS:END */
  /* KINETICS:BEGIN ink */
  /* kinetics/ink.mjs - Kubelka-Munk ink (44 s44.1; FINDING-the-animation-math s6; 47 s5b). SOURCE OF TRUTH, inlined into
     the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN ink and KINETICS:END (P43 T3). Behind
     kinetics.km_ink.
     The defect: alpha compositing (dst (1 - a) + src a) models an opaque film over a background. Layered translucent
     pigment obeys two-flux radiative transfer (Kubelka & Munk 1931): dI/dz = -(K + S) I + S J, -dJ/dz = -(K + S) J + S I,
     K absorption, S scattering. Two ink passes by alpha give a dull desaturated grey; by K-M they DEEPEN, and two
     different inks mix subtractively (a yellow over a blue-grey goes green, never grey).
     The model, per channel in LINEAR reflectance: an ink's full-coverage colour is its R_inf, so K/S = (1 - R_inf)^2 /
     (2 R_inf) (the K-M inversion); a layer of optical thickness SX over a ground Rg reflects
         R = (1 - Rg (a - b coth(b S X))) / (a - Rg + b coth(b S X)),  a = 1 + K/S,  b = sqrt(a^2 - 1).
     Layers of one ink compose: a layer of X1 over a layer of X2 IS a layer of X1 + X2 - which is why coverage can be
     summed in a buffer and converted once (kmFilterMarkup: the stains add their coverage with plus-lighter, the filter
     moves that coverage into the colour channels and a per-channel table maps it through this curve).
     The dials - S1 (the optical thickness of one full stain), the table resolution, the alpha slope, the coverage
     that means one full stain - are ours to tune (42 s42.5 / 44); the two-flux model is the finding. */

  const INK = Object.freeze({ S1: 0.03, TABLE_N: 33, ALPHA_SLOPE: 8, COVERAGE: 0.5, HIGHLIGHT_X: 0.4, WASH_NEUTRAL: 0.8 });
  /* S1: a full stain is thin - carbon hides fast (44), and 0.03 keeps the first wash LIGHT (operator: 'start out more as a lighter gray');
     HIGHLIGHT_X: the band as a layer; WASH_NEUTRAL: how far a THIN layer's per-channel K/S is pulled to their mean - a thin charcoal
     layer is bluish by the model (its blue channel absorbs least), the operator wants grey, and the blend relaxes to the exact
     ink at full coverage so the flood still ends on #25313C (operator, 2026-09-05: 'less blue tinge') */

  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const srgbToLin = (c) => c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  const linToSrgb = (v) => { v = clamp(v, 0, 1); return v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055; };
  const hexToLin = (hex) => { const h = hex.replace("#", ""); return [0, 2, 4].map((i) => srgbToLin(parseInt(h.slice(i, i + 2), 16) / 255)); };
  const linToHex = (rgb) => "#" + rgb.map((v) => Math.round(linToSrgb(v) * 255).toString(16).padStart(2, "0")).join("");

  /* K/S of a pigment from its full-coverage (infinite-thickness) reflectance - the K-M inversion, one channel. */
  const ksFromR = (Rinf) => { const R = clamp(Rinf, 0.005, 0.995); return (1 - R) * (1 - R) / (2 * R); };

  /* One channel from its K/S: a layer of optical thickness SX over a ground Rg. */
  const kmChannelKS = (Rg, ks, SX) => {
    if (!(SX > 0)) return Rg;
    const a = 1 + ks, b = Math.sqrt(a * a - 1);
    if (b === 0) return Rg;                                       /* K = 0: a non-absorbing ink - see the tests */
    const x = b * SX, coth = x > 20 ? 1 : 1 / Math.tanh(x);
    return (1 - Rg * (a - b * coth)) / (a - Rg + b * coth);
  };
  /* One channel of an ink with full-coverage reflectance Rinf. */
  const kmChannel = (Rg, Rinf, SX) => kmChannelKS(Rg, ksFromR(Rinf), SX);

  /* Three channels of linear reflectance. */
  const kmLayer = (Rg, Rinf, SX) => [0, 1, 2].map((i) => kmChannel(Rg[i], Rinf[i], SX));

  /* Layers from the paper up: [{ ink: [r,g,b] linear, X }]. */
  const kmStack = (paper, layers) => layers.reduce((Rg, l) => kmLayer(Rg, l.ink, l.X), paper);

  /* The wrong operator, kept as the else branch and the tests' reference: an opaque film at coverage a. */
  const alphaOver = (Rg, Rinf, a) => [0, 1, 2].map((i) => Rg[i] * (1 - a) + Rinf[i] * a);

  const chroma = (rgb) => Math.max(...rgb) - Math.min(...rgb);

  /* The hex of one ink layer over a known ground - the highlighter band over the chart's dark ground is exactly this,
     a flat fill at opacity 1 instead of a translucent rect. */
  const kmHex = (groundHex, inkHex, SX) => linToHex(kmLayer(hexToLin(groundHex), hexToLin(inkHex), SX));

  /* The coverage -> sRGB table for a filter: coverage c in [0, 1] (the summed stain alpha), c = COVERAGE is one full stain of
     thickness S1, so thickness = c / COVERAGE * S1; at and past a full stain the entry IS the ink (the field's final state is
     the charcoal by definition - hiding is complete, no residual from a finite S1). */
  const kmTable = (paperHex, inkHex, o = {}) => {
    const P = Object.assign({}, INK, o), paper = hexToLin(paperHex), ink = hexToLin(inkHex), n = P.TABLE_N;
    const cols = [[], [], []];
    for (let i = 0; i < n; i++) {
      const c = i / (n - 1), full = c >= P.COVERAGE - 1e-9, f = Math.min(1, c / P.COVERAGE);
      const ks = ink.map(ksFromR), mean = (ks[0] + ks[1] + ks[2]) / 3, w = (P.WASH_NEUTRAL || 0) * (1 - f * f * f * f);   /* neutral while thin and mid, the ink's own at full */
      const R = full ? ink : [0, 1, 2].map((k) => kmChannelKS(paper[k], ks[k] * (1 - w) + mean * w, f * P.S1));
      for (let k = 0; k < 3; k++) cols[k].push(full ? srgbTo8(inkHex, k) : linToSrgb(R[k]));
    }
    return { r: cols[0], g: cols[1], b: cols[2], n };
  };
  const srgbTo8 = (hex, k) => parseInt(hex.replace("#", "").slice(k * 2, k * 2 + 2), 16) / 255;

  /* SVG filter primitives that turn summed white coverage (the stains drawn white, mix-blend-mode: plus-lighter) into K-M
     ink: alpha into the colour channels, the table per channel, alpha steepened so a stain's body is opaque and its edge
     is the table's own gradient rather than a fade. Appended after the soak's displacement and blur. */
  const kmFilterMarkup = (paperHex, inkHex, o = {}) => {
    const P = Object.assign({}, INK, o), t = kmTable(paperHex, inkHex, P), f = (a) => a.map((v) => v.toFixed(4)).join(" ");
    return '<feColorMatrix type="matrix" values="0 0 0 1 0  0 0 0 1 0  0 0 0 1 0  0 0 0 1 0"/>'
      + '<feComponentTransfer><feFuncR type="table" tableValues="' + f(t.r) + '"/><feFuncG type="table" tableValues="' + f(t.g) + '"/>'
      + '<feFuncB type="table" tableValues="' + f(t.b) + '"/><feFuncA type="linear" slope="' + P.ALPHA_SLOPE + '" intercept="0"/></feComponentTransfer>';
  };

  /* THE ERRATIC SOAK (operator, 2026-09-05: "more erratic ... the variance spread throughout, almost like a mesh with some
     spots having higher attraction than others"; 44 s44.3 - wicking through a random permeability field). The paper carries
     a fixed ATTRACTION field (feTurbulence type "turbulence": the |noise| sum is a mesh of ridges between bright spots).
     Each stain is SOFT coverage (a radial gradient, soakGradientMarkup) that grows outward; the filter multiplies the summed
     coverage by (BASE + GAIN * attraction) and the K-M stage's alpha ramp then decides where ink has arrived - a high-attraction
     spot lights up ahead of the front, the front travels along the ridges, low spots stay dry inside a stain until the
     coverage is heavy, and the K-M table deepens everything that overlaps. WOBBLE is the macro displacement the soak already
     had; BLUR wets the result. All dials (42 s42.5). */
  /* round 3 (operator, 2026-09-05: "more wobble ... a higher grain"): WOBBLE_SCALE up and its field a little busier; GRAIN is a second,
     fine attraction field multiplied in after the mesh - the speckle inside and along the front */
  /* MESH (operator, 2026-09-05, after seeing it in motion: "it absolutely looks like a burn-in because of the boil ... tempted to just
     revert to the original kubelka munk, i also don't like how the spiral looks now when it soaks back up the layer"): OFF by default -
     the K-M soak is the original chain (the soak's own wobble and blur, flat white stains, the table) and the retract drags clean
     stains down the drain. The attraction field, the grain and the motion below only exist behind MESH: true. */
  /* PLAIN_* (operator: "more wobble without causing the issues"): a deeper, busier outline displacement than the alpha soak's 110,
     and a slow CREEP of that low-frequency noise through the soak (PLAIN_DRIFT px per unit soak, PLAIN_BREATH on the scale) -
     smooth and slow reads as ink moving; the fast fine grain that read as a burn-in is not part of it */
  const SOAK = Object.freeze({ MESH: false, PLAIN_FREQ: "0.007 0.011", PLAIN_SCALE: 170, PLAIN_BLUR: 12, PLAIN_DRIFT: 90, PLAIN_BREATH: 0.15,
                                      WOBBLE_FREQ: "0.008 0.012", WOBBLE_OCT: 3, WOBBLE_SCALE: 180, ATTR_FREQ: "0.008 0.011", ATTR_OCT: 4,
                                      ATTR_BASE: 0.25, ATTR_GAIN: 1.8, GRAIN_FREQ: "0.055 0.07", GRAIN_OCT: 2, GRAIN_BASE: 0.65, GRAIN_GAIN: 0.7,
                                      BLUR: 5, GRAD_MID: 0.55, GRAD_MID_A: 0.85,
                                      /* the MOTION (operator: 'wriggling / morphing / creeping / crawling'): drifts in field px per unit soak, the breath
                                         as a share of WOBBLE_SCALE; every drift stays inside the filter's 25% margin (1690 * 0.25 = 422 px at fk 1) */
                                      WOBBLE_DRIFT: 150, WOBBLE_BREATH: 0.3, WOBBLE_CYCLES: 2.5, ATTR_DRIFT: 60, GRAIN_DRIFT: 260 });

  const soakGradientMarkup = (id, o = {}) => {
    const P = Object.assign({}, SOAK, o);
    return '<radialGradient id="' + id + '"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="' + P.GRAD_MID + '" stop-color="#fff" stop-opacity="' + P.GRAD_MID_A + '"/>'
      + '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>';
  };

  const soakFilterMarkup = (seed, fk, paperHex, inkHex, o = {}) => {
    const P = Object.assign({}, INK, SOAK, o), s = seed & 255;
    if (!P.MESH) return '<feTurbulence type="fractalNoise" baseFrequency="' + P.PLAIN_FREQ + '" numOctaves="3" seed="' + s + '" result="n0"/>'
      + '<feOffset in="n0" dx="0" dy="0" result="n" id="lpsoakw' + s + '"/>'
      + '<feDisplacementMap in="SourceGraphic" in2="n" scale="' + Math.round(P.PLAIN_SCALE * fk) + '" xChannelSelector="R" yChannelSelector="G" id="lpsoakd' + s + '"/>'
      + '<feGaussianBlur stdDeviation="' + P.PLAIN_BLUR + '"/>' + kmFilterMarkup(paperHex, inkHex, P);
    return '<feTurbulence type="fractalNoise" baseFrequency="' + P.WOBBLE_FREQ + '" numOctaves="' + P.WOBBLE_OCT + '" seed="' + s + '" result="n0"/>'
      + '<feOffset in="n0" dx="0" dy="0" result="n" id="lpsoakw' + s + '"/>'
      + '<feDisplacementMap in="SourceGraphic" in2="n" scale="' + Math.round(P.WOBBLE_SCALE * fk) + '" xChannelSelector="R" yChannelSelector="G" result="d" id="lpsoakd' + s + '"/>'
      + '<feTurbulence type="turbulence" baseFrequency="' + P.ATTR_FREQ + '" numOctaves="' + P.ATTR_OCT + '" seed="' + ((s + 13) & 255) + '" result="att0"/>'
      + '<feOffset in="att0" dx="0" dy="0" result="att" id="lpsoaka' + s + '"/>'
      + '<feComposite in="d" in2="att" operator="arithmetic" k1="' + P.ATTR_GAIN + '" k2="' + P.ATTR_BASE + '" k3="0" k4="0" result="c"/>'
      + '<feTurbulence type="fractalNoise" baseFrequency="' + P.GRAIN_FREQ + '" numOctaves="' + P.GRAIN_OCT + '" seed="' + ((s + 29) & 255) + '" result="grain0"/>'
      + '<feOffset in="grain0" dx="0" dy="0" result="grain" id="lpsoakg' + s + '"/>'
      + '<feComposite in="c" in2="grain" operator="arithmetic" k1="' + P.GRAIN_GAIN + '" k2="' + P.GRAIN_BASE + '" k3="0" k4="0" result="cg"/>'
      + '<feGaussianBlur in="cg" stdDeviation="' + P.BLUR + '"/>'
      + kmFilterMarkup(paperHex, inkHex, P);
  };

  /* the fields' motion at soak progress u in [0, 1] - a pure function, so a scrubbed frame is the played one: the wobble noise
     slides and its displacement breathes (the outline wriggles and morphs), the attraction mesh creeps (the dark spots migrate
     and the front crawls after them), the grain boils. Offsets in field px (fk scales a portrait field). */
  const soakAnim = (u, fk = 1, o = {}) => {
    const P = Object.assign({}, SOAK, o), tp = Math.PI * 2, k = Math.min(1, Math.max(0, u));
    if (!P.MESH) return {   /* the plain chain: only the outline noise creeps, slowly, and its depth breathes a little */
      wob: [P.PLAIN_DRIFT * fk * k, P.PLAIN_DRIFT * fk * 0.5 * Math.sin(k * tp * 0.75)], att: [0, 0], grain: [0, 0],
      scale: P.PLAIN_SCALE * fk * (1 + P.PLAIN_BREATH * Math.sin(k * tp * 2)),
    };
    return {
      wob: [P.WOBBLE_DRIFT * fk * k, P.WOBBLE_DRIFT * fk * 0.6 * Math.sin(k * tp * 0.75)],
      att: [P.ATTR_DRIFT * fk * Math.sin(k * tp * 0.5), -(P.ATTR_DRIFT * fk * k) || 0],
      grain: [P.GRAIN_DRIFT * fk * k, P.GRAIN_DRIFT * fk * 0.5 * Math.sin(k * tp)],
      scale: P.WOBBLE_SCALE * fk * (1 + P.WOBBLE_BREATH * Math.sin(k * tp * P.WOBBLE_CYCLES)),
    };
  };
  /* STEP MOTION (operator, 2026-09-05: "it's too smooth, it needs more step-motion / jitter / delay / time variance"): the soak
     runs on a quantised clock at FPS; each stain's progress is a seeded staircase of BURSTS bursts whose sizes vary by BURST_VAR
     (surges and dwells, never contracting, exactly 1 at the flood) with its own PHASE_S of delay; the outline wobble jitters
     by WOB_JITTER px per tick. rnd(k) is the caller's seeded hash in [0, 1) - the template passes lpHash, so a scrubbed frame is
     the played frame. FIELD_S mirrors LP.FIELD (the soak's seconds); the dials are ours. */
  const SOAK_STEP = Object.freeze({ FPS: 8, FIELD_S: 2.4, BURSTS: 20, BURST_VAR: 0.85, WOB_JITTER: 8, PHASE_S: 0.3 });
  const c01 = (v) => Math.min(1, Math.max(0, v));
  const stepClock = (u, o = {}) => { const P = Object.assign({}, SOAK_STEP, o); return c01(Math.floor(c01(u) * P.FIELD_S * P.FPS) / P.FPS / P.FIELD_S); };
  const soakStepped = (u, rnd, o = {}) => {
    const P = Object.assign({}, SOAK_STEP, o);
    if (u >= 1) return 1;
    const phase = rnd(90) * P.PHASE_S, span = Math.max(0.2, P.FIELD_S - phase);
    const uq = c01(Math.floor(Math.max(0, c01(u) * P.FIELD_S - phase) * P.FPS) / P.FPS / span);
    const n = P.BURSTS, w = []; let tot = 0;
    for (let k = 0; k < n; k++) { const v = Math.max(0.1, 1 + P.BURST_VAR * (2 * rnd(k) - 1)); w.push(v); tot += v; }
    const idx = Math.min(n, Math.floor(uq * n)); let acc = 0;
    for (let k = 0; k < idx; k++) acc += w[k];
    return acc / tot;
  };
  const soakJitter = (u, rnd, fk = 1, o = {}) => {
    const P = Object.assign({}, SOAK_STEP, o), tick = Math.floor(c01(u) * P.FIELD_S * P.FPS);
    return [P.WOB_JITTER * fk * (2 * rnd(1000 + tick) - 1), P.WOB_JITTER * fk * (2 * rnd(2000 + tick) - 1)];
  };
  const soakAnimIds = (seed) => { const s = seed & 255; return { wob: "lpsoakw" + s, att: "lpsoaka" + s, grain: "lpsoakg" + s, disp: "lpsoakd" + s }; };
  /* KINETICS:END */
  /* KINETICS:BEGIN squash */
  /* kinetics/squash.mjs - area-preserving, motion-driven squash and stretch (42 s42.3; FINDING-the-animation-math s4;
     47 s1 row 5). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN
     squash and KINETICS:END (P43 T4), after spring - it reads the spring's velocity and acceleration. The vortex's
     inline stretch routes through scaleBy at identical output; the pops apply the tensor behind kinetics.area_squash.
       A = R(theta) diag(1 + alpha, 1 / (1 + alpha)) R(-theta)     det(A) = 1 by construction
       alpha = kappa_v |v| + kappa_a max(0, -v_hat . a)               stretch along the velocity, compress across it
     alpha is driven by speed and by deceleration, so squash emerges from the motion rather than being keyframed.
     kappa_v, kappa_a and the clamp are ours to tune (42 s42.5). */

  const SQUASH = Object.freeze({ KV: 0.0004, KA: 0.00002, MAX: 0.25 });   /* per px/s and px/s^2; MAX keeps a pop a pop */

  /* the amount, from a velocity and an acceleration (2-vectors) */
  const squashAlpha = (v, a, o = {}) => {
    const P = Object.assign({}, SQUASH, o), speed = Math.hypot(v[0], v[1]);
    if (!(speed > 0)) return 0;
    const decel = Math.max(0, -(v[0] * a[0] + v[1] * a[1]) / speed);
    return Math.min(P.MAX, P.KV * speed + P.KA * decel);
  };

  /* the tensor as [a, b, c, d] for matrix(a b c d 0 0): stretch 1 + alpha along theta, 1 / (1 + alpha) across it */
  const squashMatrix = (theta, alpha) => {
    const sx = 1 + alpha, sy = 1 / (1 + alpha), c = Math.cos(theta), s = Math.sin(theta), cs = c * s * (sx - sy);
    return [c * c * sx + s * s * sy, cs, cs, s * s * sx + c * c * sy];
  };
  const det2 = (m) => m[0] * m[3] - m[1] * m[2];

  /* the vortex's form: a uniform scale s with the area-preserving stretch along the tangent - the exact expressions the
     vortex shipped with (s * (1 + a), s / (1 + a)), so its output is unchanged to the bit */
  const scaleBy = (s, alpha) => ({ sx: s * (1 + alpha), sy: s / (1 + alpha) });

  /* a 1-D pop's alpha from its spring: travel px over dur seconds along one axis */
  const springSquash = (u, params, travel, dur, o = {}) => {
    const p = springEval(u, params), v = travel * p.v / dur, a = travel * p.a / (dur * dur);
    return squashAlpha([0, v], [0, a], o);
  };
  /* KINETICS:END */

  /* KINETICS:BEGIN idle */
  /* kinetics/idle.mjs - THE IDLE (ruling E49, 2026-09-06: "nothing ever goes truly still"; P47 T5). SOURCE OF TRUTH,
     inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN idle and KINETICS:END. Behind
     kinetics.idle.
     The defect it answers: a held thing - a page under a sentence, a parked dock, a pill, a caption, a plate - was
     bit-identical from frame to frame, and the cure reached for was a whole plate moving (Ken Burns, the parallax push).
     The operator: "we let things be completely still instead of being at a subtle idle." A camera move is a camera
     move (29 s9.27, 45); a hold holds - at its idle.
     The law: every idle is a NAMED kind, sized by a dial, a pure function of t (a scrubbed frame is the played frame),
     phased per element so two pills never breathe in step, and never an event for the motion gate (M01 / M10 / M16
     count events; the frozen-frames row M18 is the idle's own check).
     Kinds: breath - a scale that inhales ABOVE rest and never below it (a plate shrinking under its box shows its
     edge); drift - a bounded Lissajous walk of a few px; pulse - a luminance dip; figure - the asymmetric breath doc 48
     s48.4 prescribes for a standing figure (inspiratory:expiratory 1:1.5-1:2, a post-expiratory pause) with its two-rate
     sway; none - explicit stillness, declared.
     Every number below is a starting reference, tagged where it came from; the operator's eye moves them (42 s42.5). */

  const IDLE_KINDS = Object.freeze(["none", "breath", "drift", "pulse", "figure"]);

  const IDLE = Object.freeze({
    BREATH_AMP: 0.012,        /* [DERIVED: HyperFrames /prompting/motion "1-2 %", verified 2026-09-06; measure on ours] - a 1.2 % inhale */
    BREATH_HZ: 0.25,          /* doc 48 s48.4: breath 0.20-0.30 Hz (12-18 / min) */
    DRIFT_PX: 2.0,            /* dial (42 s42.5): the bounded drift's half-width, stage px */
    DRIFT_HZ: [0.11, 0.17],   /* two rates whose common period (100 s) never closes inside a short: the walk never reads as a loop */
    PULSE_AMP: 0.03,          /* dial: the luminance dips 3 % at most */
    PULSE_HZ: 0.2,
    FIGURE_IE: 1.75,          /* doc 48 s48.4: inspiratory:expiratory 1:1.5 to 1:2 - "never a sine" */
    FIGURE_PAUSE_S: 0.7,      /* doc 48 s48.4: the post-expiratory pause, 0.5-1.0 s */
    SWAY_PX: 1.5,             /* doc 48 s48.4: head excursion, scaled to a cutout - a dial */
    SWAY_HZ: [0.15, 0.25],    /* doc 48 s48.4: "two oscillators at 0.15 and 0.25 Hz so it never loops visibly" */
    SWAY_WANDER: 0.12,        /* the pink-noise stand-in: each oscillator's phase wanders by this fraction of a cycle ... */
    SWAY_WANDER_HZ: [0.031, 0.047],   /* ... at two slow rates, so the two 20 s-periodic sines never return to one pose inside a short */
    STEP_FPS: 0,              /* 0 = continuous; > 0 quantises the idle's clock to the INTEGER frame index (HyperFrames HF-1: never elapsed seconds) */
  });

  const IDLE_TAU = Math.PI * 2;
  const idle01 = (v) => Math.min(1, Math.max(0, v));
  const idleSmooth = (u) => { u = idle01(u); return u * u * (3 - 2 * u); };
  const idleFrac = (v) => v - Math.floor(v);

  /* the idle's clock: t itself, or t on the frame grid when STEP_FPS > 0 - floor(t * fps) is the frame index, and every
     pose below is derived from the index, never from the elapsed seconds between frames */
  const idleClock = (t, fps = IDLE.STEP_FPS) => (fps > 0 ? Math.floor(t * fps + 1e-9) / fps : t);

  /* BREATH: scale in [1, 1 + AMP], exactly 1 at rest (t = 0, phase = 0), period 1 / HZ. Above rest only. */
  const breath = (t, phase = 0, o = {}) => {
    const P = Object.assign({}, IDLE, o);
    return 1 + P.BREATH_AMP * (1 - Math.cos(IDLE_TAU * (P.BREATH_HZ * t + phase))) / 2;
  };

  /* DRIFT: [dx, dy] px, a Lissajous walk inside +-DRIFT_PX x +-0.6 DRIFT_PX, the two axes on their own rates. */
  const drift = (t, phase = 0, o = {}) => {
    const P = Object.assign({}, IDLE, o);
    return [P.DRIFT_PX * Math.sin(IDLE_TAU * (P.DRIFT_HZ[0] * t + phase)),
            P.DRIFT_PX * 0.6 * Math.sin(IDLE_TAU * (P.DRIFT_HZ[1] * t + phase * 1.7))];
  };

  /* PULSE: a luminance multiplier in [1 - AMP, 1], exactly 1 at rest. */
  const pulse = (t, phase = 0, o = {}) => {
    const P = Object.assign({}, IDLE, o);
    return 1 - P.PULSE_AMP * (1 - Math.cos(IDLE_TAU * (P.PULSE_HZ * t + phase))) / 2;
  };

  /* THE FIGURE'S BREATH (48 s48.4): one cycle of period 1 / BREATH_HZ is an inhale over Ti, an exhale over Te = IE * Ti,
     then a pause of FIGURE_PAUSE_S at rest. Returns the lung's fill in [0, 1]; the caller scales it. Never a sine: the
     inhale is the short leg, the exhale the long one, and the rest is a real hold. */
  const figureBreath = (t, phase = 0, o = {}) => {
    const P = Object.assign({}, IDLE, o), T = 1 / P.BREATH_HZ, pause = Math.min(P.FIGURE_PAUSE_S, T * 0.5);
    const active = T - pause, Ti = active / (1 + P.FIGURE_IE), Te = active - Ti;
    const u = idleFrac(t / T + phase) * T;
    if (u < Ti) return idleSmooth(u / Ti);
    if (u < Ti + Te) return 1 - idleSmooth((u - Ti) / Te);
    return 0;
  };
  const figurePhases = (o = {}) => {
    const P = Object.assign({}, IDLE, o), T = 1 / P.BREATH_HZ, pause = Math.min(P.FIGURE_PAUSE_S, T * 0.5);
    const active = T - pause, Ti = active / (1 + P.FIGURE_IE);
    return { period: T, inhale: Ti, exhale: active - Ti, pause };
  };

  /* SWAY (48 s48.4): two oscillators at 0.15 and 0.25 Hz, the A-P axis the larger, in px. */
  const sway = (t, phase = 0, o = {}) => {
    const P = Object.assign({}, IDLE, o);
    const w0 = P.SWAY_WANDER * Math.sin(IDLE_TAU * (P.SWAY_WANDER_HZ[0] * t + phase * 0.7));   /* the wandering phases */
    const w1 = P.SWAY_WANDER * Math.sin(IDLE_TAU * (P.SWAY_WANDER_HZ[1] * t + phase * 1.9));
    return [P.SWAY_PX * 0.4 * Math.sin(IDLE_TAU * (P.SWAY_HZ[0] * t + phase + w0)),
            P.SWAY_PX * (0.5 * Math.sin(IDLE_TAU * (P.SWAY_HZ[1] * t + phase * 1.3 + w1)) + 0.5 * Math.sin(IDLE_TAU * (P.SWAY_HZ[0] * t + phase * 0.6 + w0)))];
  };

  /* ONE ENTRY: the transform of a held thing of `kind` at t. {scale, dx, dy, lum}; `none` is the identity. */
  const idleXf = (kind, t, phase = 0, o = {}) => {
    const P = Object.assign({}, IDLE, o), tq = idleClock(t, P.STEP_FPS);
    const id = { scale: 1, dx: 0, dy: 0, lum: 1 };
    if (kind === "breath") return Object.assign(id, { scale: breath(tq, phase, P) });
    if (kind === "drift") { const d = drift(tq, phase, P); return Object.assign(id, { dx: d[0], dy: d[1] }); }
    if (kind === "pulse") return Object.assign(id, { lum: pulse(tq, phase, P) });
    if (kind === "figure") { const s = sway(tq, phase, P); return Object.assign(id, { scale: 1 + P.BREATH_AMP * figureBreath(tq, phase, P), dx: s[0], dy: s[1] }); }
    return id;
  };

  /* the CSS suffix a painter appends to the element's own transform - fixed decimals, so two seeks to one t write one
     string. The identity writes an explicit no-op so a flagged-off render and a `none` render differ by nothing. */
  const idleCss = (x) => (x.scale === 1 && x.dx === 0 && x.dy === 0) ? ""
    : " translate(" + x.dx.toFixed(2) + "px," + x.dy.toFixed(2) + "px) scale(" + x.scale.toFixed(4) + ")";
  /* KINETICS:END */

  /* KINETICS:BEGIN stopaction */
  /* kinetics/stopaction.mjs - STOP-ACTION MECHANICS (P47 T1; operator 2026-09-06, three times: "we need to operationalize
     stop-action mechanics to be able to throw things on page or land things with weight"). SOURCE OF TRUTH, inlined into the
     scene-evidence player by sync_kinetics.py between KINETICS:BEGIN stopaction and KINETICS:END, AFTER spring and squash
     (it reads both). Behind the arrivals: a dock, a badge or a prop declared `arrive: throw | land` with a `mass`.
     Three things, each a pure function of t:
       the CADENCE RULE - on-1s / on-2s / on-3s by the speed of the translation (the brief, :185-193): a thing translating
         faster than ON1_PX_S, or a camera move, steps every frame; slower, every second frame; a background boil every
         third. `stepped(t, hold, fps)` quantises on the INTEGER frame index (frame = round(t * fps), step = floor(frame /
         hold) - HyperFrames HF-1, never on elapsed seconds), so a renderer seeking at frame / fps never lands a ulp short.
       THROW - a ballistic arc from an offset onto the page: the chord is covered by min-jerk (release and catch), the arc
         lifts by ARC share of the chord, the prop tumbles SPIN degrees, the flight is stepped by the cadence rule; the
         landing is an IMPACT: the surface DIPS under the thing and the material's spring brings it back (the thing itself never sinks -
         back with its own overshoot) and the squash tensor (42 s42.3, area-preserving) stretches along the travel.
       LAND - weight sold BEFORE the drop (48 s48.6: postural muscles fire 100-150 ms before lift-off; fingers clamp and
         flesh squashes before the prop moves a pixel): an anticipation lift of ANTIC_PX over ANTIC_S with a pre-squash,
         then the drop, easing IN (HyperFrames HF-6: impacts ease in), the impact squash, the material's settle.
       LAG - what a thing drags (its shadow, a tick, a housing) settles LAG_FRAMES after it (HF-2: one frame).
     MATERIALS are the brief's mass-spring-damper presets (:226-232, [DERIVED: m / k / c chosen for the stated overshoot and
     settle; sources not on file]); zeta = c / (2 sqrt(k m)), w0 = sqrt(k / m), evaluated by spring.mjs's closed form in
     real seconds - a seek is the play. Every dial here is a starting reference (42 s42.5); HG2 tunes them by eye. */

  const CADENCE = Object.freeze({
    ON1_PX_S: 250,     /* [DERIVED: the brief :185-193 - on-1s above 250 px/s; its E2 s7 says 100 px/s: the two disagree, measure on ours] */
    STROBE_PX_S: 300,  /* [DERIVED: the brief - on-2s above 300 px/s strobes (Watson et al. 1986, not on file)] */
    FPS: 24,           /* the base frame rate the holds are counted in (on-1s = 24, on-2s = 12, on-3s = 8) */
  });
  /* MATERIALS. m, k, c [DERIVED: the brief :226-232] -> the spring's zeta and w0 (the report Q4: dense = critically damped, no
     overshoot - metal 0.88 and ink 0.98 sit there; paper 0.67 flutters; liquid 1.34 is overdamped). impact: how hard the hit reads on
     the RECEIVER (the dip, the shadow's spread) [DERIVED, HG2]. squash_frames: the hit's squash in frames at 24 fps - 1 for a deformable
     inanimate thing, 0 for a rigid one, the contact frame itself uncompressed [source on file: Williams pp. 93-94, 263; Lasseter 1987
     s2.2; Whitaker & Halas 1981 p. 42 - WEIGHT_DENSITY_MASS_RESEARCH_BLUEPRINT.md Q1]. e: restitution, the rebound height h1 = e^2 h0
     [UNVERIFIED: the report's Warren 1987 is not on disk; lead ~0, wood ~0.35 - ours kept small until the ear says]. */
  const MASS = Object.freeze({
    paper:  { m: 1.0, k: 180, c: 18.0, impact: 0.7, squash_frames: 1, e: 0.15 },   /* a card: one squash frame, a low hop, a flutter */
    metal:  { m: 3.5, k: 520, c: 75.0, impact: 1.5, squash_frames: 0, e: 0.0 },    /* a heavy rigid thing: "it does not squash", dead stop, the ground takes it */
    liquid: { m: 1.0, k: 45,  c: 18.0, impact: 0.5, squash_frames: 2, e: 0.0 },    /* a spread, no rebound [DERIVED] */
    ink:    { m: 0.5, k: 240, c: 21.5, impact: 1.0, squash_frames: 1, e: 0.1 },    /* our standard */
  });
  const STOP = Object.freeze({
    FLIGHT_S: 0.45,    /* a throw's time in the air */
    ARC: 0.22,         /* the arc's lift as a share of the chord */
    SPIN_DEG: 9,       /* the tumble over the flight */
    ANTIC_S: 0.18,     /* [DERIVED: 48 s48.6 APA 100-150 ms + the loading phase; E44's 100-250 ms window] */
    ANTIC_PX: 6,       /* the lift before the drop */
    ANTIC_SQUASH: 0.05,/* the clamp: a little compression before anything moves */
    DROP_S: 0.14,      /* the drop itself, easing in */
    DROP_PX: 48,       /* how far a landing thing falls onto its spot */
    SETTLE_S: 1.2,     /* the material's spring is evaluated this long after the impact, then the thing is at rest */
    IMPACT_S: 0.08,    /* the impact squash's speed-driven part decays over two frames; the material's own motion takes over from there */
    /* THE HIT (HG2): the impact squash is a 5-step ENVELOPE on the stepped clock [DERIVED: HyperFrames stop-motion-cadence SQUASH_ENV, verified
       2026-09-07], about the ground contact, scaled by the material's `impact`; the CONTACT SHADOW is pinned to the landing spot and grows and
       darkens as the thing nears the floor [DERIVED: the same reference: scale 1.05 -> 0.55, alpha 0.25 -> 0.85; 48 s48 "the floating sticker":
       a tight AO slit + a cast shadow]; the ground ANSWERS with a three-frame shake [DERIVED: HyperFrames headline-slam: 0.55 cqw / -0.3 cqh, then
       -0.38 / 0.2, then 0], scaled by the impact. Dials, all of them. */
    IMPACT_SQUASH: 0.22,  /* the squash on the ONE squash frame (a 22 % stretch across / compression along the drop) - a card; a rigid thing has none */
    /* THE CONTACT SHADOW: its offset from the thing is the height itself (the trajectory cue, primary) and its BLUR carries the
       depth - sigma 16 px high, 0.8 px at contact [source on file: Kersten, Mamassian & Knill 1997 Dem. 6; the report Q2]; the
       alpha ramp is the weakest cue and is kept narrow [DERIVED]; on the floor it is the AO slit (alpha 0.80-0.95, doc 48) */
    SHADOW_FAR: { scale: 0.55, alpha: 0.55, blur: 16 },
    SHADOW_NEAR: { scale: 1.05, alpha: 0.85, blur: 0.8 },
    SHADOW_H_PX: 160,     /* the height (px above rest) at which the shadow is 'far' (the report's H) */
    /* THE RECEIVER: mass reads as the SURFACE dipping and settling - 2-6 px, 4-8 frames [DERIVED in the report, Q3] - never as a
       stage shake, which reads as violence [source on file, Q3]; the shake stays as an opt-in for a hit that IS violent */
    DIP_PX: 4,            /* the dip at impact 1.0 (metal 6, paper 2.8, liquid 2, ink 4) */
    SHAKE_PX: [[6, -3], [-4, 2], [0, 0]],   /* the violent hit's three-frame stage shake (opt-in: `violent`) */
    G_PX_S2: 2400,        /* the rebound's gravity in px/s^2 [DERIVED: a 48 px drop over 0.14 s] */
    LAG_FRAMES: 1,     /* [DERIVED: HyperFrames /prompting/motion, verified 2026-09-06; measure on ours] */
  });

  const sa01 = (v) => Math.min(1, Math.max(0, v));
  const saMinJerk = (u) => { u = sa01(u); return u * u * u * (10 - 15 * u + 6 * u * u); };
  const saEaseIn = (u) => { u = sa01(u); return u * u * u; };

  /* THE CADENCE RULE: which hold a motion piece steps on. kind: "camera" | "boil" | anything else (a translation). */
  const cadence = (v_px_s, kind = "translate", o = {}) => {
    const P = Object.assign({}, CADENCE, o);
    if (kind === "camera") return { hold: 1, fps: P.FPS, why: "a camera move steps every frame" };
    if (kind === "boil") return { hold: 3, fps: P.FPS / 3, why: "a background boil steps on 3s" };
    if (v_px_s > P.ON1_PX_S) return { hold: 1, fps: P.FPS, why: `${Math.round(v_px_s)} px/s > ${P.ON1_PX_S}: on 1s` };
    return { hold: 2, fps: P.FPS / 2, why: `${Math.round(v_px_s)} px/s <= ${P.ON1_PX_S}: on 2s` };
  };
  /* the stepped clock on the INTEGER frame index (HF-1): frame = round(t * fps), step = floor(frame / hold) */
  const stepped = (t, hold = 2, fps = CADENCE.FPS) => {
    if (!(hold > 1)) return t;
    const frame = Math.round(t * fps), step = Math.floor(frame / hold);
    return step * hold / fps;
  };
  /* the material's spring: zeta and w0 from m, k, c */
  const massParams = (name) => {
    const M = MASS[name] || MASS.paper, z = M.c / (2 * Math.sqrt(M.k * M.m)), w = Math.sqrt(M.k / M.m);
    return { z, w, wd: z < 1 ? w * Math.sqrt(1 - z * z) : 0, name: MASS[name] ? name : "paper" };
  };
  /* what a thing drags settles LAG_FRAMES after it */
  const lag = (t, frames = STOP.LAG_FRAMES, fps = CADENCE.FPS) => t - frames / fps;

  /* the material's impact weight */
  const massImpact = (name) => (MASS[name] || MASS.paper).impact;
  /* THE HIT'S SQUASH (Q1): frame 0 after the contact is the contact drawing, uncompressed; the squash lives on the next
     `squash_frames` frames (1 for a card, 0 for a rigid thing) and releases at once - never a hold */
  const impactSquash = (ts, mass, hold = 1, fps = CADENCE.FPS, o = {}) => {
    const P = Object.assign({}, STOP, o), M = MASS[mass] || MASS.paper;
    if (ts < 0 || !(M.squash_frames > 0)) return 0;
    const f = Math.floor(Math.round(ts * fps) / Math.max(1, hold));
    if (f < 1 || f > M.squash_frames) return 0;
    return Math.min(0.5, P.IMPACT_SQUASH * (1 - (f - 1) / M.squash_frames));
  };
  /* THE CONTACT SHADOW at a height h (px above rest, >= 0): pinned to the landing spot (its offset from the thing IS the height),
     its blur the depth (16 -> 0.8 px), its alpha narrow; on the hit it takes the squash's spread (scaleX) */
  const contactShadow = (h, alpha = 0, o = {}) => {
    const P = Object.assign({}, STOP, o), k = Math.min(1, Math.max(0, h) / P.SHADOW_H_PX), mix = (a, b) => a + (b - a) * k;
    return { scale: mix(P.SHADOW_NEAR.scale, P.SHADOW_FAR.scale) * (1 + Math.max(0, alpha)), alpha: mix(P.SHADOW_NEAR.alpha, P.SHADOW_FAR.alpha),
             blur: mix(P.SHADOW_NEAR.blur, P.SHADOW_FAR.blur) };
  };
  /* THE RECEIVER'S DIP (Q3): the surface deflects DIP_PX x impact at the contact and the material's spring brings it back - a
     dense thing's ground recovers dead (metal, ~7 frames), a light thing's flutters */
  const groundDip = (ts, mass, o = {}) => {
    const P = Object.assign({}, STOP, o);
    if (ts < 0) return 0;
    const s = springEval(ts, massParams(mass));
    return P.DIP_PX * massImpact(mass) * (1 - s.x);
  };
  /* THE REBOUND (Q4, rank 1): the hop after the hit, h1 = e^2 h0, a parabola under G; a rigid dense thing has none */
  const rebound = (ts, mass, h0, o = {}) => {
    const P = Object.assign({}, STOP, o), e = (MASS[mass] || MASS.paper).e || 0, h1 = e * e * Math.max(0, h0);
    if (ts < 0 || h1 < 0.05) return 0;
    const T = 2 * Math.sqrt(2 * h1 / P.G_PX_S2), u = ts / T;
    return u >= 1 ? 0 : -4 * h1 * u * (1 - u);
  };
  /* THE GROUND'S ANSWER: three frames of shake from the hit, scaled by the material, then exactly zero */
  const groundShake = (ts, mass, fps = CADENCE.FPS, o = {}) => {
    const P = Object.assign({}, STOP, o);
    if (ts < 0) return { x: 0, y: 0 };
    const f = Math.floor(ts * fps + 1e-9), k = massImpact(mass);
    if (f >= P.SHAKE_PX.length) return { x: 0, y: 0 };
    return { x: P.SHAKE_PX[f][0] * k, y: P.SHAKE_PX[f][1] * k };
  };
  /* after the contact: the thing RIDES the ground's dip and hops by its restitution; the squash is the hit's frame(s) only. The
     thing never sinks into the surface (that was invented; a rigid body stops in one frame - Q4) */
  const settle = (ts, h0, mass, P, hold = 1) => {
    const dip = groundDip(ts, mass, P);
    return { y: dip + rebound(ts, mass, h0, P), alpha: impactSquash(ts, mass, hold, CADENCE.FPS, P), ground: dip };
  };

  /* THROW: offsets (px) relative to the resting spot. `from` is where the flight starts (an offset), the rest is 0,0.
     Returns { x, y, rot, alpha, theta, phase, u, hold } - theta is the squash axis (radians, vertical = pi/2). */
  const throwXf = (from, mass, t, o = {}) => {
    const P = Object.assign({}, STOP, o), F = Math.max(0.05, P.FLIGHT_S);
    const chord = Math.hypot(from.x, from.y), v = chord / F, cad = cadence(v, "translate");
    const tq = stepped(Math.max(0, t), cad.hold, cad.fps), u = sa01(tq / F);
    if (t < 0) return { x: from.x, y: from.y, rot: 0, alpha: 0, theta: Math.PI / 2, phase: "waiting", u: 0, hold: cad.hold, h: -from.y, ground: 0, shake: { x: 0, y: 0 } };
    if (u < 1) {
      /* a BALLISTIC chord: constant speed along it and the arc's lift - no deceleration into the contact (Q4: a heavy mass has none;
         it snaps to rest in one frame). The tumble unwinds with the flight. */
      const lift = -P.ARC * chord * 4 * u * (1 - u);
      const x = from.x * (1 - u), y = from.y * (1 - u) + lift, rot = P.SPIN_DEG * (1 - u);
      const dt = 1 / cad.fps, u2 = sa01((tq + dt) / F), lift2 = -P.ARC * chord * 4 * u2 * (1 - u2);
      const vx = (from.x * (1 - u2) - x) / dt, vy = (from.y * (1 - u2) + lift2 - y) / dt;
      const theta = Math.atan2(vy, vx), alpha = squashAlpha([vx, vy], [0, 0]);
      return { x, y, rot, alpha, theta, phase: "flight", u, hold: cad.hold, h: Math.max(0, -y), ground: 0, shake: { x: 0, y: 0 } };
    }
    const ts = t - F, h0 = Math.max(0, -from.y) + P.ARC * chord;   /* the height it came down from: the release plus the arc */
    const st = settle(ts, h0, mass, P, cad.hold);
    return { x: 0, y: st.y, rot: 0, alpha: st.alpha, theta: Math.PI / 2, phase: ts < P.SETTLE_S ? "land" : "settled", u: 1, hold: cad.hold, h: 0,
             ground: st.ground, shake: P.violent ? groundShake(ts, mass) : { x: 0, y: 0 } };
  };

  /* LAND: the thing is already where it will rest (x = 0); weight first, then the drop, the impact, the settle. */
  const landXf = (mass, t, o = {}) => {
    const P = Object.assign({}, STOP, o);
    const id = { x: 0, rot: 0, theta: Math.PI / 2 };
    const still = { x: 0, y: 0 };
    if (t < 0) return { ...id, y: -P.DROP_PX, alpha: 0, phase: "waiting", u: 0, h: P.DROP_PX, ground: 0, shake: still };
    if (t < P.ANTIC_S) {   /* the anticipation: a lift and a clamp, easing out and back (weight sold before the lift) */
      const u = t / P.ANTIC_S, bump = Math.sin(Math.PI * u), y = -P.DROP_PX - P.ANTIC_PX * bump;
      return { ...id, y, alpha: -P.ANTIC_SQUASH * bump, phase: "anticipation", u, h: -y, ground: 0, shake: still };
    }
    const td = t - P.ANTIC_S;
    if (td < P.DROP_S) {   /* the drop eases IN: impacts ease in */
      const u = td / P.DROP_S, y = -P.DROP_PX * (1 - saEaseIn(u));
      const vy = P.DROP_PX * 3 * u * u / P.DROP_S;
      return { ...id, y, alpha: squashAlpha([0, vy], [0, 0]), phase: "drop", u, h: -y, ground: 0, shake: still };
    }
    const ts = td - P.DROP_S;
    const st = settle(ts, P.DROP_PX, mass, P, 1);
    return { ...id, y: st.y, alpha: st.alpha, phase: ts < P.SETTLE_S ? "land" : "settled", u: 1, h: 0, ground: st.ground,
             shake: P.violent ? groundShake(ts, mass) : { x: 0, y: 0 } };
  };

  /* the CSS a painter appends: translate, the tumble, the area-preserving squash - fixed decimals. A negative alpha is a
     clamp (compress along the axis, stretch across it) and goes through the same tensor with the axis turned. */
  const stopCss = (s) => {
    const a = Math.abs(s.alpha || 0), th = (s.alpha || 0) < 0 ? (s.theta || 0) + Math.PI / 2 : (s.theta || 0);
    const m = a > 1e-6 ? " matrix(" + squashMatrix(th, a).map((v) => v.toFixed(4)).join(",") + ",0,0)" : "";
    return " translate(" + (s.x || 0).toFixed(2) + "px," + (s.y || 0).toFixed(2) + "px)" + ((s.rot || 0) ? " rotate(" + s.rot.toFixed(2) + "deg)" : "") + m;
  };
  /* KINETICS:END */

  /* KINETICS:BEGIN arap */
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

  const ARAP = Object.freeze({ N: 96, CENTROID_MAX: 0.06, AXIS_MAX_DEG: 15, AREA_MIN_RATIO: 0.60 });   /* N: the resample count; the three invariants [DERIVED: brief B4] */

  const ARAP_TAU = Math.PI * 2;
  const arapSub = (a, b) => [a[0] - b[0], a[1] - b[1]];
  const arapDot = (a, b) => a[0] * b[0] + a[1] * b[1];

  /* ---- outlines -------------------------------------------------------------------------------------------------- */
  const polyArea = (pts) => { let a = 0; for (let i = 0, n = pts.length; i < n; i++) { const p = pts[i], q = pts[(i + 1) % n]; a += p[0] * q[1] - q[0] * p[1]; } return a / 2; };
  /* the AREA centroid (the shoelace form) - the shape's mass, not its vertex density; the vertex mean when the area is nil */
  const centroid = (pts) => {
    const n = pts.length; let a = 0, cx = 0, cy = 0, mx = 0, my = 0;
    for (let i = 0; i < n; i++) { const p = pts[i], q = pts[(i + 1) % n], w = p[0] * q[1] - q[0] * p[1]; a += w; cx += (p[0] + q[0]) * w; cy += (p[1] + q[1]) * w; mx += p[0]; my += p[1]; }
    return Math.abs(a) < 1e-9 ? [mx / n, my / n] : [cx / (3 * a), cy / (3 * a)];
  };
  /* a closed outline resampled to n vertices at equal arc length, starting at its first vertex, wound counter-clockwise */
  const resample = (pts, n = ARAP.N) => {
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
  const alignOffset = (A, B) => {
    const n = A.length, ca = centroid(A), cb = centroid(B); let best = 0, bestD = Infinity;
    for (let k = 0; k < n; k++) {
      let d = 0;
      for (let i = 0; i < n; i++) { const a = A[i], b = B[(i + k) % n]; const dx = (a[0] - ca[0]) - (b[0] - cb[0]), dy = (a[1] - ca[1]) - (b[1] - cb[1]); d += dx * dx + dy * dy; }
      if (d < bestD) { bestD = d; best = k; }
    }
    return best;
  };
  const rotate = (B, k) => B.map((_, i) => B[(i + k) % B.length]);
  /* METHOD A: the correspondence (resampled, aligned) and the per-vertex lerp */
  const correspond = (src, dst, n = ARAP.N) => { const A = resample(src, n), B0 = resample(dst, n); return { A, B: rotate(B0, alignOffset(A, B0)) }; };
  const lerpShape = (A, B, t) => A.map((a, i) => [a[0] + (B[i][0] - a[0]) * t, a[1] + (B[i][1] - a[1]) * t]);

  /* ---- the triangle mesh ------------------------------------------------------------------------------------------ */
  /* a fan from the centroid: vertex n is the centre; triangle i = (i, i+1, n). The source and the target share this topology. */
  const fanMesh = (A) => { const n = A.length, tris = []; for (let i = 0; i < n; i++) tris.push([i, (i + 1) % n, n]); return { verts: [...A, centroid(A)], tris }; };
  /* the 2x2 Jacobian of a triangle's map from rest (p) to deformed (q): J = D' D^-1 with D = [p1-p0 | p2-p0] */
  const triJacobian = (p0, p1, p2, q0, q1, q2) => {
    const d = [[p1[0] - p0[0], p2[0] - p0[0]], [p1[1] - p0[1], p2[1] - p0[1]]], e = [[q1[0] - q0[0], q2[0] - q0[0]], [q1[1] - q0[1], q2[1] - q0[1]]];
    const det = d[0][0] * d[1][1] - d[0][1] * d[1][0], inv = [[d[1][1] / det, -d[0][1] / det], [-d[1][0] / det, d[0][0] / det]];
    return [[e[0][0] * inv[0][0] + e[0][1] * inv[1][0], e[0][0] * inv[0][1] + e[0][1] * inv[1][1]],
            [e[1][0] * inv[0][0] + e[1][1] * inv[1][0], e[1][0] * inv[0][1] + e[1][1] * inv[1][1]]];
  };
  const det2x2 = (J) => J[0][0] * J[1][1] - J[0][1] * J[1][0];
  /* the closed-form polar decomposition: J = R S, R a rotation by theta, S symmetric positive-definite (when det J > 0) */
  const polar = (J) => {
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
  const jacobianAt = (J, t) => {
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
  const stripMesh = (top, bot) => {
    const n = top.length, tris = [];
    for (let i = 0; i + 1 < n; i++) tris.push([i, n + i, i + 1], [i + 1, n + i, n + i + 1]);
    return { verts: [...top, ...bot], tris, n };
  };
  const stripOutline = (verts, n) => [...verts.slice(0, n), ...verts.slice(n, 2 * n).reverse()];
  /* the prepared morph for ANY shared-topology mesh: rest verts in `mesh`, target verts `Bv`, one pinned vertex that travels the chord */
  const arapPrepareMesh = (mesh, Bv, pin) => {
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
  const arapPrepare = (A, B, o = {}) => {
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
  const arapAt = (prep, t) => {
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
  const minDet = (prep, t) => {
    const s = arapAt(prep, t), V = prep.mesh.verts;
    let target = Infinity, solved = Infinity;
    prep.mesh.tris.forEach(([i, j, k], ti) => { target = Math.min(target, det2x2(s.jacobians[ti])); solved = Math.min(solved, det2x2(triJacobian(V[i], V[j], V[k], s.verts[i], s.verts[j], s.verts[k]))); });
    return { target, solved };
  };

  /* ---- the invariants (the brief B4) ------------------------------------------------------------------------------ */
  /* the polygon's second moments about its area centroid (the shoelace forms) - the SHAPE's inertia, not its vertices' spread
     (a strip's two rows of vertices would read as a vertical axis by vertex covariance; by area it is the strip's length) */
  const inertia = (pts) => {
    const c = centroid(pts), n = pts.length; let ixx = 0, iyy = 0, ixy = 0, a = 0;
    for (let i = 0; i < n; i++) {
      const p = pts[i], q = pts[(i + 1) % n], x0 = p[0] - c[0], y0 = p[1] - c[1], x1 = q[0] - c[0], y1 = q[1] - c[1], w = x0 * y1 - x1 * y0;
      a += w; ixx += w * (x0 * x0 + x0 * x1 + x1 * x1); iyy += w * (y0 * y0 + y0 * y1 + y1 * y1); ixy += w * (x0 * y1 + 2 * x0 * y0 + 2 * x1 * y1 + x1 * y0);
    }
    const sgn = a < 0 ? -1 : 1;   /* orientation-free */
    return { xx: sgn * ixx / 12, yy: sgn * iyy / 12, xy: sgn * ixy / 24, area: Math.abs(a) / 2 };
  };
  const dominantAxis = (pts) => {   /* the angle of the area's major principal axis, in [-pi/2, pi/2) */
    const I = inertia(pts);
    let ang = 0.5 * Math.atan2(2 * I.xy, I.xx - I.yy); if (ang >= Math.PI / 2) ang -= Math.PI; if (ang < -Math.PI / 2) ang += Math.PI; return ang;
  };
  /* the extent of an outline along a direction (radians): max - min of the projection */
  const extentAlong = (pts, ang) => { const c = Math.cos(ang), s = Math.sin(ang); let lo = Infinity, hi = -Infinity; for (const p of pts) { const v = p[0] * c + p[1] * s; lo = Math.min(lo, v); hi = Math.max(hi, v); } return hi - lo; };
  const bbox = (pts) => { let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity; for (const p of pts) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]); } return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 }; };
  /* over sampled frames of an outline (t = 0..1): the three invariants and their verdicts against the dials */
  /* the bounding area in a given frame: the oriented box along `ang` (a prop turned to the chart's axis must not be charged for the
     screen-axis box its tilt inflates - the brief's "bounding area" is the shape's extent, read in the target's principal frame) */
  const orientedArea = (pts, ang) => extentAlong(pts, ang) * extentAlong(pts, ang + Math.PI / 2);
  const morphInvariants = (frames, W, o = {}) => {
    const P = Object.assign({}, ARAP, o), first = frames[0], last = frames[frames.length - 1];
    const c0 = centroid(first), c1 = centroid(last), shift = Math.hypot(c1[0] - c0[0], c1[1] - c0[1]) / Math.max(1, W);
    let da = Math.abs(dominantAxis(last) - dominantAxis(first)); if (da > Math.PI / 2) da = Math.PI - da;
    const ang = dominantAxis(last), areas = frames.map((f) => orientedArea(f, ang)), ratio = Math.min(...areas) / Math.max(1e-9, Math.max(...areas));
    return { centroid_shift: shift, centroid_ok: shift <= P.CENTROID_MAX, axis_deg: da * 180 / Math.PI, axis_ok: da * 180 / Math.PI <= P.AXIS_MAX_DEG,
             area_ratio: ratio, area_ok: ratio >= P.AREA_MIN_RATIO };
  };
  /* the SVG path of an outline */
  const outlinePath = (pts) => pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ") + " Z";
  /* KINETICS:END */
  /* KINETICS:BEGIN morph_a */
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

  const MORPH_A = Object.freeze({
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
  const ringNormalise = (pts) => {
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
  const morphAPrepare = (src, dst, o = {}) => {
    const resampleRings = o.resample !== false, n = o.n || MORPH_A.N, norm = o.normalise !== false;
    let A = norm ? ringNormalise(src) : src.map((p) => [+p[0], +p[1]]), B = norm ? ringNormalise(dst) : dst.map((p) => [+p[0], +p[1]]);
    if (resampleRings) { A = resample(A, n); B = resample(B, n); }
    else if (A.length !== B.length) throw new Error(`morph_a: ${A.length} and ${B.length} vertices - rings of different counts must be resampled`);
    const offset = alignOffset(A, B);
    return { A, B: rotate(B, offset), offset, n: A.length };
  };

  /* ---- step 4: the frame ------------------------------------------------------------------------------------------- */
  /* the ring at t: the direct vertex lerp. Exact at both ends by construction (t = 0 is A, t = 1 is B). */
  const morphAAt = (prep, t) => {
    const u = t <= 0 ? 0 : (t >= 1 ? 1 : t), { A, B } = prep;
    return { outline: A.map((a, i) => [a[0] + (B[i][0] - a[0]) * u, a[1] + (B[i][1] - a[1]) * u]), u };
  };

  /* the cubic reconstruction: a closed centripetal Catmull-Rom through every vertex, as Bezier segments. The curve
     INTERPOLATES the ring (each knot is on it), so the shape is the lerp's shape - the cubics only remove the faceting
     96 chords would show at the stage's size. Non-uniform Catmull-Rom -> Bezier (Barry & Goldman 1988's recurrence,
     solved for the two control points), guarded where two knots meet. */
  const morphAPath = (pts, o = {}) => {
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
  const morphAMinDet = (rest, verts, tris) => {
    let worst = Infinity;
    for (const [i, j, k] of tris) worst = Math.min(worst, det2x2(triJacobian(rest[i], rest[j], rest[k], verts[i], verts[j], verts[k])));
    return worst;
  };

  /* the ring's area, for a caller reporting a frame without re-deriving it (the centroid is arap.mjs's `centroid`) */
  const morphAArea = (pts) => Math.abs(polyArea(pts));
  /* KINETICS:END */
  /* KINETICS:BEGIN chartxf */
  /* kinetics/chartxf.mjs - CHART TRANSITIONS (P48 T2, 2026-09-10): the interpolators a chart changes STATE by.
     SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN chartxf and
     KINETICS:END. Self-contained on purpose: nothing here reads a template symbol; the clock (minJerk, ease.mjs) is
     applied by the caller.
     The law (P48): a transition is a pure interpolation between two states that were both BUILT at load. A rescale
     moves every shared mark from its position under scale A to its position under scale B on one clock; a mark whose
     value leaves the target domain fades as it goes; a mark the target adds fades in where it will stand. Nothing is
     rebuilt per frame - the caller writes attributes from the numbers these functions return, so a seek is the play.
     Bravos (46 s46.7): the picture changes six times a minute, the composition two and a half - a rescale is one of
     the builds inside a held frame that make that possible. */

  /* xfLerp - the one blend. u is already on the clock (0..1); outside it clamps, so a transition that has not started
     returns a and one that has ended returns b, exactly (the goldens' contract at both ends). */
  const xfLerp = (a, b, u) => { u = Math.min(1, Math.max(0, u)); return a + (b - a) * u; };

  /* xfPoint - a datum's screen position between two scales. mapA / mapB take the DATUM (x, v) and return [px, py]; the
     datum never changes, only where the scale puts it - so a point outside B's window still has a position under B
     (past the plot's edge), which is where it travels to while it fades. */
  const xfPoint = (x, v, mapA, mapB, u) => {
    const a = mapA(x, v), b = mapB(x, v);
    return [xfLerp(a[0], b[0], u), xfLerp(a[1], b[1], u)];
  };

  /* xfPath - a series' whole path between two scales, as the point list and the SVG `d` the caller writes. */
  const xfPath = (pts, mapA, mapB, u) => {
    const out = pts.map(([x, v]) => xfPoint(x, v, mapA, mapB, u));
    return { pts: out, d: out.map(([px, py], k) => (k ? "L" : "M") + px.toFixed(1) + " " + py.toFixed(1)).join(" ") };
  };

  /* xfFade - the opacity of a mark keyed by VALUE as the domain moves. A mark whose value is inside the target domain
     holds; one leaving fades over the first LEAVE share of the clock; one arriving (present only in B) fades in over the
     last ARRIVE share. Both edges clamp so the ends are exact: at u=0 an arriving mark is invisible, at u=1 a leaving
     one is. */
  const XF = Object.freeze({
    LEAVE: 0.5,    /* a leaving tick is gone by half the clock - it should not travel the whole way as a ghost [DERIVED: E28, the axis must read at every t] */
    ARRIVE: 0.5,   /* an arriving tick appears over the second half, at its settled place */
  });
  const xfFade = (inside, arriving, u) => {
    u = Math.min(1, Math.max(0, u));
    if (arriving) return inside ? Math.min(1, Math.max(0, (u - (1 - XF.ARRIVE)) / XF.ARRIVE)) : 0;
    return inside ? 1 : Math.max(0, 1 - u / XF.LEAVE);
  };

  /* xfInside - is a value within a domain [lo, hi] (either order), with a hair of tolerance for the tick that sits on
     the edge (a nice-step tick at exactly the domain's end is part of the axis, not outside it). */
  const xfInside = (v, lo, hi) => {
    const a = Math.min(lo, hi), b = Math.max(lo, hi), eps = (b - a) * 1e-6;
    return v >= a - eps && v <= b + eps;
  };

  /* xfRect - a bar between two states: every edge lerps, so a bar that grows keeps its baseline and a bar that moves keeps
     its width law. geom is {x, y, w, h}. */
  const xfRect = (ga, gb, u) => ({ x: xfLerp(ga.x, gb.x, u), y: xfLerp(ga.y, gb.y, u), w: xfLerp(ga.w, gb.w, u), h: xfLerp(ga.h, gb.h, u) });
  /* KINETICS:END */
  /* KINETICS:BEGIN camera */
  /* kinetics/camera.mjs - THE CAMERA (P49 T1-T3): one persistent 2D similarity per timeline - a zoom s, the world point it
     LOOKS at, and the screen point that look-point lands AT - as a pure function of t. SOURCE OF TRUTH, inlined into the
     scene-evidence player by sync_kinetics.py between KINETICS:BEGIN camera and KINETICS:END, after chartxf. Self-contained:
     nothing here reads a template symbol (its clamp is its own).
       screen = at + s * (p - look)          (43 s43.2: p_screen = M_camera x M_world x p_local)
     at == look is a zoom IN PLACE about the target (the punch, the focus zoom, the pull-back - the three species the player
     shipped with, whose envelopes are factored here UNCHANGED so the frames are pixel-identical); at != look is a PAN.
     Bravos, measured 2026-09-10 (P49's amendment): 37 of 45 held compositions are camera-still - LOCKED is the default;
     the camera moves for a stage wider than the frame or tied to a landing (E51), never as a drift on a held chart. */

  const CAM = Object.freeze({
    PUNCH_IN: 0.42, PUNCH_OUT: 0.5, PUNCH_SCALE: 1.14,   /* the punch: in - hold - out, cubic ease (yt-camera-move) */
    FOCUS_SCALE: 1.32,                                     /* the focus zoom: zoom + pan to the anchor, then dead still (the servo law) */
    PULL_FROM: 1.9,                                        /* the pull-back: opens ON the number, one decelerating pull */
  });
  const camClamp = (k) => Math.min(1, Math.max(0, k));
  const camEase = Object.freeze({
    cubic: (k) => 1 - Math.pow(1 - camClamp(k), 3),                                                 /* the species' spEase */
    inout: (k) => { k = camClamp(k); return k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; },   /* the species' spIO */
    linear: (k) => camClamp(k),
    hold: (k) => (camClamp(k) >= 1 ? 1 : 0),                                                        /* the previous key holds, then steps */
  });
  const CAM_EASES = Object.freeze(Object.keys(camEase));

  /* the identity: the stage, unmoved */
  const camIdentity = (W, H) => ({ s: 1, look: [W / 2, H / 2], at: [W / 2, H / 2] });

  /* a camera SPECIES window (punch | focus_zoom | pull_back) at fraction k of its clock, about the target's centre c -
     the exact envelopes camXf drew (P35 T6), so a flag flip changes no pixel; null outside the window */
  const camSpeciesState = (kind, k, c, dur, P = CAM) => {
    if (k < 0 || k > 1) return null;
    let s = 1;
    if (kind === "punch") {
      const tin = P.PUNCH_IN / (dur || 1), tout = P.PUNCH_OUT / (dur || 1);
      const a = k < tin ? camEase.cubic(k / tin) : k > 1 - tout ? 1 - camEase.cubic((k - (1 - tout)) / tout) : 1;
      s = 1 + (P.PUNCH_SCALE - 1) * a;
    } else if (kind === "focus_zoom") s = 1 + (P.FOCUS_SCALE - 1) * camEase.inout(Math.min(1, k * 1.8));
    else if (kind === "pull_back") s = P.PULL_FROM + (1 - P.PULL_FROM) * camEase.cubic(k);
    else return null;
    return { s, look: [c[0], c[1]], at: [c[0], c[1]] };
  };

  /* AUTHORED KEYS: [{t, zoom, look:[x,y], at:[x,y]|undefined, ease}] in stage px, sorted by t. Before the first key the
     camera is identity; between keys s, look and at lerp by the segment's ease (named on the key the segment ARRIVES at);
     after the last key it holds. A key with no `at` looks in place (at = look). */
  const camKeyState = (keys, t, W, H) => {
    if (!keys || !keys.length) return camIdentity(W, H);
    const norm = (k) => ({ t: +k.t, s: +k.zoom > 0 ? +k.zoom : 1, look: k.look ? [+k.look[0], +k.look[1]] : [W / 2, H / 2],
                           at: k.at ? [+k.at[0], +k.at[1]] : (k.look ? [+k.look[0], +k.look[1]] : [W / 2, H / 2]), ease: camEase[k.ease] || camEase.cubic });
    const K = keys.map(norm);
    if (t <= K[0].t) return t < K[0].t ? camIdentity(W, H) : { s: K[0].s, look: K[0].look, at: K[0].at };
    let i = 1; while (i < K.length && t > K[i].t) i++;
    if (i >= K.length) { const L = K[K.length - 1]; return { s: L.s, look: L.look, at: L.at }; }
    const a = K[i - 1], b = K[i], u = b.ease(camClamp((t - a.t) / Math.max(1e-6, b.t - a.t)));
    const L = (p, q) => p + (q - p) * u;
    return { s: L(a.s, b.s), look: [L(a.look[0], b.look[0]), L(a.look[1], b.look[1])], at: [L(a.at[0], b.at[0]), L(a.at[1], b.at[1])] };
  };

  /* the CSS for a state, about a transform-origin at the stage's centre. at == look keeps the string the player has always
     written (byte-identical -> pixel-identical); a pan takes the general form: translate(t) scale(s) with
     t = at - s*look - (1 - s)*O, which is the same mapping screen = at + s (p - look) under that origin. */
  const camCssFor = (st, W, H) => {
    const [lx, ly] = st.look, [ax, ay] = st.at, s = st.s;
    if (ax === lx && ay === ly) {
      return s === 1 ? "" : "translate(" + (lx - W / 2).toFixed(1) + "px, " + (ly - H / 2).toFixed(1) + "px) scale(" + s.toFixed(4)
        + ") translate(" + (W / 2 - lx).toFixed(1) + "px, " + (H / 2 - ly).toFixed(1) + "px)";
    }
    const tx = ax - s * lx - (1 - s) * W / 2, ty = ay - s * ly - (1 - s) * H / 2;
    return "translate(" + tx.toFixed(2) + "px, " + ty.toFixed(2) + "px) scale(" + s.toFixed(4) + ")";
  };

  /* the FRUSTUM: the stage rectangle in world (pre-camera) coordinates - p = look + (screen - at) / s */
  const camFrustum = (st, W, H) => {
    const [lx, ly] = st.look, [ax, ay] = st.at, s = st.s;
    return { x0: lx + (0 - ax) / s, y0: ly + (0 - ay) / s, x1: lx + (W - ax) / s, y1: ly + (H - ay) / s };
  };
  /* a world box {x, y, w, h} against the frustum: fully inside, the visible share of its area, and its on-screen scale */
  const camInFrame = (fr, box, s = 1) => {
    const x0 = Math.max(fr.x0, box.x), y0 = Math.max(fr.y0, box.y), x1 = Math.min(fr.x1, box.x + box.w), y1 = Math.min(fr.y1, box.y + box.h);
    const area = Math.max(0, box.w) * Math.max(0, box.h);
    const vis = area > 0 ? Math.max(0, x1 - x0) * Math.max(0, y1 - y0) / area : (x0 <= x1 && y0 <= y1 ? 1 : 0);   /* a point: in or out */
    return { inside: box.x >= fr.x0 && box.y >= fr.y0 && box.x + box.w <= fr.x1 && box.y + box.h <= fr.y1, visible: vis, scale: s };
  };
  /* T4 - THE ATTENTION LAW (P49), locked by default (Bravos). With `attention: "landings"` a dock that ARRIVES (throw | land)
     pulls the eye: a zoom in place of ATTN.SCALE about the card's parked box, in over ATTN.IN from the CONTACT frame (E51: a
     push is tied to a landing - never to a thing that just sits there), held while the card is up, released over ATTN.OUT
     before it leaves. contactOf(dock) is the player's (the stop-action clock: a throw's FLIGHT_S, a landing's ANTIC_S + DROP_S).
     [DERIVED: Bravos #68's map push ~6 % between countries, then still; D1's 15 deg cone] - HG1 tunes the three by eye. */
  const ATTN = Object.freeze({ SCALE: 1.06, IN: 0.5, OUT: 0.6 });
  const camAttentionState = (docks, t, contactOf, P = ATTN) => {
    let st = null;
    for (const d of docks || []) {
      if (!d || !d.place || !(d.arrive === "throw" || d.arrive === "land")) continue;
      const tc = contactOf(d), exit = +d.exit, out = exit - P.OUT;
      if (!(t >= tc && t <= exit)) continue;
      const a = camEase.inout(camClamp((t - tc) / P.IN)) * (1 - camEase.inout(camClamp((t - out) / P.OUT)));
      const c = [d.place.x + d.place.w / 2, d.place.y + d.place.h / 2];
      st = { s: 1 + (P.SCALE - 1) * a, look: c, at: c };   /* the last landing wins, as the last species window does */
    }
    return st;
  };
  /* T5 - THE CAMERA ARRIVAL (P49): the eye goes to a landed card. Over the arrival's clock u (0..1, eased by the caller)
     the camera looks at the card's centre and carries it to the stage's centre while zooming to the FILL scale - the
     scale at which the card's box (stage px) fills the stage; at u = 1 the frustum IS the card, so the world can switch
     to the page the card is a picture of with no seam. */
  const camArrivalState = (box, u, W, H) => {
    const fill = Math.min(W / Math.max(1, box.w), H / Math.max(1, box.h));
    const c = [box.x + box.w / 2, box.y + box.h / 2], O = [W / 2, H / 2];
    return { s: 1 + (fill - 1) * u, look: c, at: [c[0] + (O[0] - c[0]) * u, c[1] + (O[1] - c[1]) * u], fill };
  };
  /* where a world point lands on screen */
  const camProject = (st, p) => [st.at[0] + st.s * (p[0] - st.look[0]), st.at[1] + st.s * (p[1] - st.look[1])];
  /* KINETICS:END */
  /* KINETICS:BEGIN breakthrough */
  /* species/breakthrough.mjs - THE BREAKTHROUGH's FURNITURE and its STOP-MOTION cadence (P50 T10 + T13;
     ruling E60; BACKLOG R26-30). SOURCE OF TRUTH, inlined into the scene-evidence player by
     sync_kinetics.py between KINETICS:BEGIN breakthrough and KINETICS:END, AFTER stopaction (it reads
     the cadence rule and the stepped clock from it).

     IT REGISTERS NO PAINTER, and that is deliberate rather than an omission - the same finding
     span.mjs records. The burst is a PAGE mechanic: it is painted by `lpPaintBreakthrough` inside the
     chart's own viewBox, under the page's park transform, off the page's build clock - while
     SPECIES_PAINTERS hands a painter the stage-px overlay and the scene's clock. The burst also
     PREDATES the module rule (E60 shipped it in the template's body on 2026-09-10), so what lives here
     is the NEW math only - the placeholder's clock, the axis capsule's geometry and the stepped
     cadence - and `lpPaintBreakthrough` calls it thinly and keeps the DOM. Closing that gap (one
     registry both layers route through) is P51 T1's business.

     WHAT BRAVOS DOES, measured at 8:01.8-8:03.2 of the SPR chart (the CAPABILITIES row): the row holds
     a grey "?" TRACK with a pink stamp; the bar shoots to the frame's edge WHILE the axis rescales
     under it; a pink value CAPSULE counts up ON THE AXIS under the bar's end with a dotted leader; the
     frame is never broken. E60 built the shoot and the rescale; this is the furniture around them.

     THE THREE LAWS, each a pure function of the page's own clock:
       THE PLACEHOLDER (`placeholder` on the object) - the breaking bar's number is not known to the
         viewer until it is SPOKEN, and "spoken" is the start of the hold (secs 0: the ordinary build
         has ended, the bar stands at the comparator's level). Until then the bar's value label or pill
         prints the placeholder's mark instead of a count, and a light grey TRACK of the comparator's
         height stands behind the bar - furniture, not data: it is exactly the height the bar builds
         to, so no frame of the page shows a scale the page did not state (E28).
       THE AXIS CAPSULE (`overflow_capsule: "axis"`) - the value capsule mounted ON THE AXIS under the
         bar's end rather than riding the tip, with a DOTTED leader from the tip down to it. Dotted on
         purpose: a solid rule across a chart is a comparator (E53 s6) and would be read as one.
       THE STEPPED CADENCE (`break_cadence: "stop"`, the operator's blend - E60: "a stop-motion version
         of what bravos does. essentially blending our stop motion + break through + counter
         mechanics") - the shoot, the counter, the rescale and the ticks' crossing all read off ONE
         stepped clock, so they step TOGETHER; the glow lands on the landing step alone; and the run is
         clamped to its own end so the settled frame is the continuous burst's, exactly.

     The dials below are ours to tune (doc 42 s42.5), not findings. */

  const BREAK = Object.freeze({
    PH_TEXT: "?",         /* what the breaking bar prints while its number is unspoken (Bravos: the grey "?" track) */
    PH_ALPHA: 0.18,       /* the track's grey behind the bar: enough to read as a slot waiting to be filled, never enough to read as a second bar */
    PH_OUT_S: 0.18,       /* the track leaves over this much of the HOLD - the number is spoken, the slot is no longer empty. Shorter than BT_HOLD (0.5) so the track is gone before the shoot */
    CAP_PAD: 6,           /* the axis capsule's top below the zero baseline, in the chart's viewBox units. Small on purpose: the band between the axis and the bottom of the chart's box is 70 units on a portrait page and the pill is 84 (measured) */
    CAP_FLOOR: 4,         /* ... and the capsule keeps this much of the band clear at the bottom, so it never reaches the chart box's edge and the page's source line beneath it (E52: the citation is not ours to move) */
    CAP_MIN_H: 44,        /* the floor the fit will not go under: a capsule that cannot be read is not a capsule (44 units is 16 CSS px on a phone at this page's scale, above doc 49's 11) */
    CAP_LEAD_GAP: 6,      /* the leader stops this far short of the bar's end and of the capsule: it points, it does not touch */
    CAP_LEAD_DASH: "3 7", /* ... and it is DOTTED (a solid rule across a chart is a comparator, E53 s6) */
    CAP_LEAD_W: 2,        /* the leader's weight: thinner than a bar's edge, heavier than a gridline */
    CAP_LEAD_DX: 10,      /* ... and it runs this far OUTSIDE the bar's edge. A vertical bar's end is its top and the capsule is on the axis below it, so a leader drawn between them crosses the bar and reads as a seam in it (measured on the frame). Bravos' bars are horizontal, where below the tip is empty air; ours routes beside the bar instead */
    CAP_LAB_UP: 12,       /* the capsule TAKES the x-label's row (84 units of capsule do not fit in the 70 the portrait page leaves below its axis), so the bar's name is written this far ABOVE the zero line, inside its own column: the callout owns its place and the labels around it yield (s9.23b) */
    STEP_FPS: 24,         /* the stop-motion clock's frame rate - stopaction's CADENCE.FPS, the rate the holds are counted in */
  });

  const bt01 = (v) => Math.min(1, Math.max(0, v));

  /* ---- THE PLACEHOLDER ------------------------------------------------------------------------
     `secs` is the breakthrough's own clock: seconds since the ordinary build ended, so secs < 0 is
     the build and secs 0 is the start of the hold - the instant the number is spoken. */
  const breakPlaceholder = (secs, o = {}) => {
    const P = Object.assign({}, BREAK, o);
    const k = secs < 0 ? 1 : bt01(1 - secs / Math.max(1e-6, P.PH_OUT_S));
    return { on: secs < 0, k, alpha: P.PH_ALPHA * k, text: P.PH_TEXT };
  };

  /* the grey track BEHIND the breaking bar: the comparator's height at the bar's own x, never more.
     `yComp` is the comparator's level in the chart's viewBox (my(comp)), `base` the zero baseline. */
  const breakTrack = (x, bw, base, yComp) => ({
    x, w: bw, y: Math.min(base, yComp), h: Math.max(3, Math.abs(base - yComp)),
  });

  /* THE MARK. The track alone shows nothing - the bar builds to exactly its height and covers it within a
     fifth of a second - so the placeholder's "?" is written where the NUMBER will be: centred over the
     track's top edge, at the value label's own offset `dy`. The count that would otherwise stand there is
     held back until the number is spoken, so the page carries one mark, not two. */
  const breakStamp = (track, dy) => ({ x: track.x + track.w / 2, y: track.y - dy });

  /* ---- THE AXIS CAPSULE -----------------------------------------------------------------------
     ON THE AXIS under the bar's end: its x is the bar's centre (the caller's), its y the zero
     baseline plus a pad. `capH` is the pill's own height - the x-label it displaces goes under it. */
  const breakCapsule = (base, capH, o = {}) => {
    const P = Object.assign({}, BREAK, o);
    return { y: base + P.CAP_PAD, h: capH, labY: base - P.CAP_LAB_UP };
  };

  /* THE AXIS MOUNT'S BOX. The capsule has only the band between the zero line and the bottom of the chart's
     own box to live in; below that is the page's source line. So it SHRINKS to its band - the box, the
     baseline inside it and the type all by the same factor `k` - and never below CAP_MIN_H. On a landscape
     page the band is 110 units against a 42-unit pill: k is 1 and nothing changes. `cap` is the builder's
     own pill box { w, h, ty, rx }; `chartH` the chart's viewBox height. */
  const breakCapsuleFit = (base, chartH, cap, o = {}) => {
    const P = Object.assign({}, BREAK, o);
    const band = Math.max(0, chartH - P.CAP_FLOOR - (base + P.CAP_PAD));
    /* the floor RAISES a capsule the band would crush; it never enlarges one the page asked to be small
       (a landscape pill is 42 units by design and its band is 110 - the fit must leave it alone) */
    const h = Math.min(cap.h, Math.max(P.CAP_MIN_H, band));
    const k = h / Math.max(1e-6, cap.h);
    return { y: base + P.CAP_PAD, h, k, ty: cap.ty * k, rx: Math.min(cap.rx, h / 2), labY: base - P.CAP_LAB_UP };
  };

  /* where the leader runs: clear of the bar, on the side that has room inside the plot */
  const breakLeaderX = (bx, bw, x0, o = {}) => {
    const P = Object.assign({}, BREAK, o);
    return bx - P.CAP_LEAD_DX >= x0 ? bx - P.CAP_LEAD_DX : bx + bw + P.CAP_LEAD_DX;
  };

  /* the dotted leader from the bar's END down to the capsule, or null when there is no room for one
     (a bar whose tip has not cleared the capsule would be pointing at itself) */
  const breakLeader = (cx, tipY, capY, o = {}) => {
    const P = Object.assign({}, BREAK, o);
    const y1 = tipY + P.CAP_LEAD_GAP, y2 = capY - P.CAP_LEAD_GAP;
    return y2 - y1 > P.CAP_LEAD_GAP ? { x: cx, y1, y2 } : null;
  };

  /* ---- THE STEPPED CADENCE --------------------------------------------------------------------
     THE SPEED the cadence rule is read on: the TIP's travel - from the comparator's level on the
     stated scale to the true height on the rewritten one - over the run, in the chart's own viewBox
     units per second. (The page may be PARKED when the burst fires, which halves the travel on
     screen; the cadence is read on the page's own units so the same page steps the same way wherever
     it stands. If a parked burst ever reads too smooth, pass the park's scale in.) */
  const burstSpeed = (plot, lo, hi0, hi1, comp, v, run_s) => {
    const y = (val, hi) => (val - lo) / ((hi - lo) || 1) * plot;
    return Math.abs(y(v, hi1) - y(comp, hi0)) / Math.max(1e-6, run_s);
  };

  const burstCadence = (plot, lo, hi0, hi1, comp, v, run_s, o = {}) =>
    cadence(burstSpeed(plot, lo, hi0, hi1, comp, v, run_s), "translate", o);

  /* THE STEPPED CLOCK. stopaction's `stepped` short-circuits hold <= 1 and returns t unchanged,
     because it assumes the renderer's own clock IS the cadence clock (a 24 fps renderer seeking at
     frame / fps is already on 1s). Ours is not: render_episode.py delivers 30 fps, so an on-1s burst
     left unquantised is the continuous one. The frame index is therefore taken here (HF-1:
     frame = round(t * fps), step = floor(frame / hold)) and `stepped` is used verbatim for hold > 1,
     where the two are the same formula. */
  const breakStep = (t, hold = 1, fps = BREAK.STEP_FPS) => {
    if (!(t > 0)) return 0;
    const h = Math.max(1, hold | 0);
    return h > 1 ? stepped(t, h, fps) : Math.round(t * fps) / fps;
  };

  /* THE RUN'S CLOCK, both mechanics in one function. `run` is seconds since the hold ended; `cad` is
     null for the continuous burst (u1 and u2 are exactly what they always were) or the cadence object
     for the blend, where BOTH clocks are read off a stepped run - so the shoot, the counter, the
     rescale and the ticks' crossing step together rather than sliding past each other.
     The stepped run is CLAMPED to run_s + settle_s: without the clamp the last step would land past
     the settle and the stepped burst's resting frame would differ from the continuous one's. With it,
     the two are identical at and after the settle, which is the acceptance.
     `landed` is the landing step and only the landing step - the glow rides it (the continuous glow
     law stays with its caller, which is where it has always been). */
  const burstClock = (run, run_s, settle_s, cad = null) => {
    const R = Math.max(1e-6, run_s), S = Math.max(1e-6, settle_s);
    /* the continuous burst is left EXACTLY as it was - the two clamps on the raw run, no epsilon, no
       short-circuit - so a page that names no cadence renders the frame it always did, bit for bit */
    if (!cad) return { t: run, u1: bt01(run / R), u2: bt01((run - R) / S), step: -1, landed: false };
    const end = R + S, h = Math.max(1, cad.hold | 0);
    const t = Math.min(breakStep(run, h, cad.fps), end);
    const done = t >= end - 1e-9;   /* (R + S) - R is not S in floating point: the last step lands 2e-16 short of rest without this */
    const step = run > 0 ? Math.floor(Math.round(run * cad.fps) / h) : 0;
    return { t, u1: done ? 1 : bt01(t / R), u2: done ? 1 : bt01((t - R) / S), step,
             landed: step === Math.ceil(R * cad.fps / h - 1e-9) };
  };
  /* KINETICS:END */
  /* Pills draw TEXT, so they take the text tier - never the graphic tier. */
  const ACCENT = { sunflower: "var(--t-sunflower)", coral: "var(--t-coral)", teal: "var(--t-teal)", cobalt: "var(--t-cobalt)", ink: "#d7dee6" };

  const vo = $("vo"); vo.src = A["__audio__"];
  const wA = $("wA"), wB = $("wB"), wash = $("wash"), seam = $("seam"), cap = $("caption");
  const docks = [$("dock-1"), $("dock-2")];
  const bzveil = $("bzveil"), dipveil = $("dipveil");   /* E47: the blur-zoom's softness and the dip's black */
  const WIPE = 0.62, DISSOLVE_S = 0.8, MOUNT_STEPS = 5;   /* DISSOLVE_S: the cross-fade a row declares with exit dissolve (the outro card); MOUNT_STEPS: the DANCE - a mounting page fades in this many steps over its soak, the charcoal growing between them */
  const SUCK_S = 0.3, SUCK_TURN = 240;   /* the suck transition: 0.3 s, two thirds of a turn into the point */
  /* THE TWO WORLD-CHANGE TRANSITIONS (ruling E47, operator 2026-09-06), taken off the measured reference
     (doc 46 s46.5; docs/research/motion/WEALTH_LOGIC_TRANSITIONS_MEASURED.md). Both straddle the boundary:
     half in the outgoing scene, the switch on the boundary frame, half in the incoming scene.
       DIP_S 0.47            [DERIVED: the reference, 14 frames at 30 fps, measured on all 35 of its dips,
                              2026-09-06 - wealth_logic_transitions_measured.csv]. A fade to black and back,
                              a plain LINEAR ramp (the reference's dip is linear to the frame), the cut in the black.
       BLURZOOM_S 0.27       [DERIVED: the MEDIAN duration_frames of the reference's 28 blur-zooms, 8 frames at 30 fps]
       BLURZOOM_SCALE 1.35   [DERIVED: the reference's detail loss - a starting reference, tune by eye]. The outgoing
                              world magnifies 1 -> 1.35 on min-jerk while the frame softens.
       BLURZOOM_BLUR 18      [DERIVED: with the scale, the point where the plate's detail is gone - tune by eye], px.
       BLURZOOM_IN 1.10      [DERIVED: the .world layer's -5% inset - the widest crop a `cover` plate affords]. The
                              incoming world rises 1/BLURZOOM_IN -> 1 (the ruling's shape: both plates magnify, the
                              incoming is NOT the outgoing inverted). It rises from 1/1.10 and not from
                              1/BLURZOOM_SCALE because a cover plate shown under 1/1.10 cannot fill the stage and
                              would open a black border for four frames; the reference's plates escape that only
                              because they are figures on an unbounded cream field. Flagged to the operator.
     The blur is a BACKDROP-FILTER on a veil over the stage, never `filter` on the world: a filter on the world
     fades its own edge inward by ~2 sigma, and at 18 px that reaches inside the frame once the world is not
     magnified. The veil samples with edge clamping, so the frame stays filled, and it softens the docks, the
     stage captions and the species with the plate - a world change takes the whole frame. */
  const DIP_S = 0.47, BLURZOOM_S = 0.27, BLURZOOM_SCALE = 1.35, BLURZOOM_BLUR = 18, BLURZOOM_IN = 1.10;
  /* `dip`, `dip:<s>`, `blurzoom`, `blurzoom:<s>`, `suck:<x>,<y>` - the name, and the seconds when the row declares them */
  const exitName = (e) => (typeof e === "string" ? e.split(":")[0] : "");
  const exitSecs = (e, dflt) => {
    const v = parseFloat(typeof e === "string" ? (e.split(":")[1] || "") : "");
    return v > 0 ? v : dflt;
  };
  /* remotion-ui directional-wipe port (2026-08-30): FEATHER is the soft
     edge as a share of the frame (their edgeSoftness); DEPTH is the
     parallax the pages carry under the wipe. The mask edge travels from
     past the far side to past the near side so the feather never clips
     short - their formula, kept exactly. */
  /* FEATHER / DEPTH / maskEdge (the remotion-ui directional-wipe port,
     dd9e476) were RETIRED 2026-09-01: the feathered parallax cross-reveal
     read as a two-direction fade on review and mirrored the carried light.
     The scene wipe is the hard inset() front again - see LAYER 1. */

  const EXIT = 0.72, CARD_IN = 0.75;

  /* THE TWO-PHASE DOCK ON A LEDGER PAGE (ruling E45, 2026-09-06: "drawing on the heading,
     springing the dock, then shrinking it while we slide it to the corner or over the title, so
     that the graph gains its readability back" / "you're just cutting the docks in instead of
     using our strong maths/springs").

     PHASE A - READ. On its word the card SPRINGS in at reading size (its own CSS solo geometry,
     800px centred in the mobile safe box at 9:16): scale DOCK_POP_FROM -> 1 by the analytic
     spring's POP preset (42 s42.2 - overshoot Mp = 4%, settle at u = 1; the same preset that
     lands the page's badge rail), opacity 0 -> 1 over DOCK_FADE_S. It holds there for `read_s`.
     PHASE B - PARK. Over `park_s` the card shrinks to `place.w` and slides to `place.x/y` along
     Flash & Hogan's minimum-jerk quintic (minJerk above) - width, x and y on ONE clock, so the
     shrink and the slide are one move - and then holds at `place` until `exit`, live, with the
     chart fully readable beside it. RETRACT: the spring in reverse over DOCK_RETRACT_S.

     PURE IN t. The geometry is the card's LAYOUT (width/left/top), interpolated per frame, not a
     transform: at the end of the park the element's box IS `place` to the pixel, and the spring's
     scale is exactly 1 there, so a seek to any t lands on the same frame the play-through does.
     NO KILL-SWITCH FLAG: the whole choreography hangs off the compiler's `place`, which only a
     ledger scene carries - a build without it renders the tagged baseline, which is what P39's
     switch is for. A dock on a plain plate keeps the 0.75s expo-out rise below untouched (that
     rise is a lift and a scale, not a plain fade, so E45's "never a dissolve" is already met). */
  const DOCK_READ_S = 1.2, DOCK_PARK_S = 0.7;   /* the compiler's defaults, mirrored for an entry that predates them */
  /* DIALS, ours to tune (42 s42.5), not findings: DOCK_POP_S is the wall clock the spring's own
     settle (u = 1) is spent over - a quarter longer than the badge rail's LP_BADGE_IN = 0.36, the
     card being the heavier object; DOCK_POP_FROM the arrival scale; DOCK_FADE_S the opacity ramp
     the ruling names; DOCK_RETRACT_S the fast settle out. */
  const DOCK_POP_S = 0.45, DOCK_POP_FROM = 0.85, DOCK_FADE_S = 0.12, DOCK_RETRACT_S = 0.35;
  /* P47 T1 (stop-action): a THROWN card flies in from off its side, STOP_THROW_DX past its own width and STOP_THROW_DY
     above; a LANDED card drops onto its spot (STOP.DROP_PX) after selling its weight. Both behind kinetics.stop_action
     and only when the dock entry declares `arrive`; the shadow of either reads the clock one frame late (HF-2). */
  const STOP_THROW_DX = 240, STOP_THROW_DY = 160;
  const arriveOf = (o) => (kin("stop_action") && o && (o.arrive === "throw" || o.arrive === "land")) ? o.arrive : "spring";

  /* the READING rectangle: the card's own CSS geometry, measured with no placement forced on it.
     Content-independent (width, left and top are all CSS), so it is measured once per dock. */
  const dockReadRect = (el, d) => {
    if (d.read_place) return { x: d.read_place.x, y: d.read_place.y, w: d.read_place.w };   /* the row named the box the card pops at (2026-09-10) */
    if (d._read) return d._read;
    const w = el.style.width, l = el.style.left, tp = el.style.top;
    el.style.width = ""; el.style.left = ""; el.style.top = "";
    const r = { x: el.offsetLeft, y: el.offsetTop, w: el.offsetWidth };
    el.style.width = w; el.style.left = l; el.style.top = tp;
    return (d._read = r);
  };

  /* the placed card's layout box at t: reading size, then the minimum-jerk park. `parks` is
     recomputed from the LIVE span because the coalescer above can extend a dock's exit. */
  const dockGeom = (el, d, t) => {
    if (!d.place) return null;
    const R = dockReadRect(el, d), P = d.place;
    if (d.centre && !d.read_place) return { x: P.x, y: P.y, w: P.w };   /* a CENTRED card (the design pass): its box from the first frame, whatever its life - unless the row named a reading box it pops at first */
    const readS = d.read_s != null ? d.read_s : DOCK_READ_S;
    const parkS = d.park_s != null ? d.park_s : DOCK_PARK_S;
    if (d.exit - d.enter < readS + parkS) return { x: R.x, y: R.y, w: R.w };   /* too short to park */
    const j = minJerk(clamp01((t - d.enter - readS) / parkS));
    return { x: R.x + (P.x - R.x) * j, y: R.y + (P.y - R.y) * j, w: R.w + (P.w - R.w) * j };
  };

  /* ================= THE PRESS CARD STACK (P50 T3; doc 29 s9.27 "Push hand-off") =================
     A press dock is a DOCK KIND, not a species: it has a card, a lifecycle, a source line and a quoted phrase.
     It is painted HERE rather than in the two-slot loop below for one reason - a stack is three cards on stage at
     once and the player has two slots. Each press dock mounts its OWN .dock.press element keyed by its slide, and
     the pile's pose comes whole from species/press.mjs: pressStack(i, n, uNew), a pure function of the card's
     place in the pile and the newest card's landing clock. Membership is read from DOCKS at the instant asked, so
     a scrubbed frame is the played frame and a card that has LEFT the stack is simply not in it.
     Nothing above or below changes for a build with no press dock: the two-slot loop skips this kind, and every
     existing golden renders byte-identically. */
  const PRESS_EL = Object.create(null);     /* the mounted card, per slide id */
  const PRESS_POSE = Object.create(null);   /* its live stage geometry and the phrase box in stage px - what resolveTarget reads for a `phrase` target */
  const PRESS_KIND = "press", PHRASE_KIND = "phrase";
  const isPressDock = (d) => !!d && d.kind === PRESS_KIND;

  const pressMount = (d) => {
    if (PRESS_EL[d.slide]) return PRESS_EL[d.slide];
    const el = document.createElement("div");
    el.className = "dock press";
    el.id = "press-" + d.slide;
    el.innerHTML = '<div class="pmast"><span></span></div><div class="slide-frame"><img alt="evidence" /></div>';
    el.querySelector(".pmast span").textContent = d.source || "";   /* B1: the card says whose claim it is */
    el.querySelector("img").src = (A && A[d.slide]) || "";
    const seam = $("seam");
    seam.parentNode.insertBefore(el, seam);   /* the dock layer, under #species: the underline is drawn ABOVE the card */
    return (PRESS_EL[d.slide] = el);
  };

  /* the stacked press docks live at t, oldest first. A press dock with no stack bookkeeping is its own pile of one:
     a lone quotation lands and holds, and two unrelated cards never push each other. */
  const pressPile = (d, t) => (d.stack_n > 1
    ? DOCKS.filter((x) => isPressDock(x) && x.stack_n > 1 && t >= x.enter && t < x.exit)
           .sort((a, b) => a.enter - b.enter || (a.stack_index | 0) - (b.stack_index | 0))
    : [d]);

  /* the card's pose at t: its place in the pile, the newest card's landing clock, and the fades its own span owns.
     A card past its exit holds the pose it LEFT in (the pile read one instant before it went) and retracts on the
     dock's own spring - never a dissolve. */
  const pressPose = (d, t) => {
    const tp = t < d.exit ? t : d.exit - 1e-3;
    const pile = pressPile(d, tp), i = pile.indexOf(d);
    if (i < 0) return null;
    const newest = pile[pile.length - 1];
    const el = PRESS_EL[d.slide];   /* the fan's step is the CARD'S own height, so a pile of any card reads the same */
    const step = el && el.offsetHeight > 2 ? { STEP_PX: Math.max(PRESS.STEP_PX, el.offsetHeight * PRESS.STEP_H) } : {};
    const pose = pressStack(i, pile.length, clamp01((tp - newest.enter) / PRESS.LAND_S), step);
    const rk = t > d.exit ? springPop(clamp01((t - d.exit) / DOCK_RETRACT_S)) : 0;
    pose.i = i; pose.n = pile.length;
    pose.alpha = pose.opacity * clamp01((t - d.enter) / PRESS.FADE_S) * clamp01(1 - rk);
    return pose;
  };

  const paintPressCard = (d, t) => {
    const el = pressMount(d), pose = t >= d.enter && t < d.exit + EXIT ? pressPose(d, t) : null;
    if (!pose) { el.style.opacity = 0; delete PRESS_POSE[d.slide]; return; }
    /* NO z-index: the pile's order is DOM order - each card mounts on its enter, so the newest is the last press
       element before #seam and paints in front of the others AND under #species, where the underline is drawn.
       A positive z-index here would lift the card above the species layer and swallow its own underline. */
    el.style.opacity = pose.alpha.toFixed(3);
    /* the SAME composition, in the same order, about the same origin as pressXf below: translate, then scale
       (x carrying the squeeze), then the lean. Written to the element, so the card's own layout box is untouched. */
    el.style.transform = "translate(" + pose.dx.toFixed(2) + "px," + pose.dy.toFixed(2) + "px) scale("
      + (pose.scale * pose.sx).toFixed(5) + "," + pose.scale.toFixed(5) + ") skewX(" + pose.skew.toFixed(3) + "deg)";
    const sh = 12 * expoOut(clamp01((t - d.enter) / CARD_IN));
    el.style.boxShadow = sh.toFixed(1) + "px " + sh.toFixed(1) + "px 0 rgba(37,49,60,.82)";
    /* THE LIVE GEOMETRY the underline rides: the card's LAYOUT box (offsets - transform-free) carried through the
       pose by pressXf, and the phrase box inside the card image carried through the same transform. The image's
       offsets are read from the dock's padding edge, so the card may be re-laid out at any aspect without a number
       here changing. */
    const im = el.querySelector("img");
    const box = { x: el.offsetLeft, y: el.offsetTop, w: el.offsetWidth, h: el.offsetHeight };
    const bl = el.clientLeft || 0, bt = el.clientTop || 0;
    const img = im && im.offsetWidth > 2 && im.offsetHeight > 2   /* an image still decoding has a width but no height: no box, no underline */
      ? { x: box.x + bl + im.offsetLeft, y: box.y + bt + im.offsetTop, w: im.offsetWidth, h: im.offsetHeight } : null;
    const xf = pressXf(box, pose), q = pressPhraseBox(img, d.phrase);
    PRESS_POSE[d.slide] = { card: xf(box), phrase: q ? xf(q) : null, depth: pose.depth, i: pose.i, n: pose.n };
  };

  /* every press card live at t, and nothing else on stage: a card off its span takes its geometry with it, so a
     species pointing into it resolves to nothing and paints nothing (the targeting law). */
  const paintPress = (live, t) => {
    const on = Object.create(null);
    for (const d of live) if (isPressDock(d)) { on[d.slide] = 1; paintPressCard(d, t); }
    for (const k in PRESS_EL) if (!on[k]) { PRESS_EL[k].style.opacity = 0; delete PRESS_POSE[k]; }
  };

  /* every dock carries its own lifetime: enter -> hand-led reveal -> hold
     (7s cap) -> exit. Nothing lives to the end of a scene. */
  const DOCKS = [];
  /* SNAP (the third watch): a page that enters by `snap` grows from a landed card. The dock loop records that card's LAYOUT box
     (offsets, transform-free - the same at every t the card is on the stage) and hides the card once the page has taken over;
     the page reads the box here. Sequential rendering (frame N-1's dock loop before frame N's page) makes it exact; a cold seek
     into the 0.45 s snap window shows the page full for one frame before the box is known - stated in the T7 evidence. */
  const SNAP_FROM = {}, SNAP_RECT = {};
  window.__lpSnap = () => ({ rect: SNAP_RECT, from: Object.keys(SNAP_FROM) });   /* P47 T7: the snap's recorded card box, for the tests */
  TL.scenes.forEach((sc, si) => (sc.docks || []).forEach((d) => DOCKS.push({ ...d, si, scene: sc })));
  TL.scenes.forEach((sc) => { const pg = sc.world && sc.world.page; if (pg && (pg.enter === "snap" || pg.enter === "camera") && pg.snap_from) SNAP_FROM[pg.snap_from] = sc; });   /* P49 T5: a camera page's card is registered the same way */
  /* COALESCE. A document that holds through three scenes is authored as one
     dock per scene, so it used to exit and re-enter at every boundary - the
     entrance re-running on a card that never left. Evidence that persists
     must persist: merge same-slide, same-slot docks separated by less than
     DOCK_JOIN into a single span. The world wipes underneath it; the card
     does not move. */
  const DOCK_JOIN = 2.5;
  /* GROUP BY SLIDE, then merge - consecutive-only merging breaks when a
     DIFFERENT slide interleaves the time sort (pairing a card between two
     rows of the same document made it "re-enter"; the choreography gate
     caught it). Same algorithm as emit_choreography.py - mirrored. */
  {
    const bySlide = new Map();
    for (const d of DOCKS) {
      if (!bySlide.has(d.slide)) bySlide.set(d.slide, []);
      bySlide.get(d.slide).push(d);
    }
    const merged = [];
    for (const ds of bySlide.values()) {
      ds.sort((a, b) => a.enter - b.enter);
      let cur = null;
      for (const d of ds) {
        if (cur && d.enter - cur.exit <= DOCK_JOIN) {
          cur.exit = Math.max(cur.exit, d.exit);
          cur.badge_at = [...new Set([...(cur.badge_at || []), ...(d.badge_at || [])])];
        } else { cur = d; merged.push(d); }
      }
    }
    DOCKS.length = 0;
    for (const d of merged) DOCKS.push(d);
    DOCKS.sort((a, b) => a.enter - b.enter);
  }
  /* EACH DOCK OWNS ITS PRESENTATION STATE. Solo side alternates by dock
     order (so the world is not always cropped the same way) and NEVER
     changes during a dock's life - deriving it from the current scene
     index teleported a persisting card at every boundary it crossed and
     flipped the lit wash's direction mid-hold. Paired docks (overlapping
     another) take their authored slot geometry and a bottom-up wash. */
  {
    let flip = 0;
    for (const d of DOCKS) {
      const paired = DOCKS.some((o) => o !== d &&
        o.enter < d.exit && o.exit > d.enter);
      d.side = paired ? "pair" : (flip++ % 2 === 0 ? "r" : "l");
    }
  }
  /* THE WASH IS AN INTERVAL TRACK, not a per-frame toggle. Consecutive
     docks separated by a sub-1.2s turnover share one wash - the gap used
     to pulse it off and back on (two of the six flashes at s06's open). */
  const WASHES = [];
  for (const d of [...DOCKS].sort((a, b) => a.enter - b.enter)) {
    const last = WASHES[WASHES.length - 1];
    if (last && d.enter - last[1] < 1.2) last[1] = Math.max(last[1], d.exit);
    else WASHES.push([d.enter, d.exit]);
  }

  /* SNAP NEAR-BOUNDARY EXITS TO THE BOUNDARY. A card exiting moments before
     a scene turn fires three light events in under a second - fade-exit,
     wash-off (the bare plate flashes fully bright), then the wipe - and the
     scene appears to repaste itself before turning. Snap those exits to the
     boundary so the turn carries card, wash and shadow in ONE motion. An
     exit more than ~1.4s out is a deliberate early clear and still fades. */
  const BOUNDS = TL.scenes.map((x) => x.span[0]);
  for (const d of DOCKS)
    for (const b of BOUNDS)
      if (d.enter < b && b - d.exit > 0.05 && b - d.exit <= 1.4) { d.exit = b; break; }

  /* P50 T3: every press card mounts HERE, at load, not on the frame it first paints. A card's image must be
     decoded before the first frame asks how tall it is - the fan's step and the phrase box are both read off the
     card's live layout, and a zero-height image would put the underline at the card's top edge on a cold seek. */
  for (const d of DOCKS) if (isPressDock(d)) pressMount(d);

  const chips = $("scenes");
  TL.scenes.forEach((sc, i) => {
    const c = document.createElement("button");
    c.className = "chip"; c.textContent = `${sc.scene_id} ${sc.span[0].toFixed(0)}s`;
    c.addEventListener("click", () => seek(sc.span[0] + 0.05));
    chips.appendChild(c);
  });

  const fillDock = (slot, aid) => {
    const ev = TL.evidence[aid]; if (!ev) return;
    const n = slot + 1;
    /* NO TITLE ON STAGE. The card IS the document - a label above it spends
       25px of the most valuable real estate on the frame restating what the
       viewer is already looking at. `title` stays in the timeline for
       manifests and QA; it is never drawn. */
    const dockEl = docks[slot];
    dockEl.classList.toggle("record", !!ev.record);
    let old = dockEl.querySelector(".paper"); if (old) old.remove();
    recState[slot] = null;
    if (ev.record) {
      const r = ev.record, pp = document.createElement("div");
      pp.className = "paper";
      pp.innerHTML = `<div class="phdr"><span></span><span></span></div>` +
        `<div class="prule"></div><div class="pkick"></div><blockquote></blockquote>` +
        `<div class="pattr"></div><div class="psrc"></div>`;
      const hs = pp.querySelectorAll(".phdr span");
      hs[0].textContent = r.hdr[0]; hs[1].textContent = r.hdr[1];
      pp.querySelector(".pkick").textContent = r.kicker;
      pp.querySelector(".pattr").textContent = r.attr;
      pp.querySelector(".psrc").textContent = r.src;
      dockEl.appendChild(pp);
      recState[slot] = { r, q: pp.querySelector("blockquote"),
                         attr: pp.querySelector(".pattr"), src: pp.querySelector(".psrc") };
    }
    /* STACK species (operator, s68 verdict beat): the episode's best
       evidence PILES UP, word-matched - cards fly in from depth
       (transform3d-showcase vocabulary), hold as a mosaic, then burst
       clear on the pivot line. Members reference the asset-data map -
       every stacked card is a document already docked elsewhere. */
    const oldS = document.querySelector(".stackbox"); if (oldS) oldS.remove();
    stackState[slot] = null;
    dockEl.classList.toggle("stack", !!ev.stack);
    if (ev.stack) {
      /* operator correction: the stack DANCES AROUND THE WORLD PLATE -
         it mounts on the STAGE, full-frame, not inside the dock card
         (the dock stays as an invisible lifecycle anchor). Scattered
         asymmetric placement keeps the plate breathing through the
         gaps; the burst throws each card radially off its position. */
      /* nine rail spots: four across the top, mid-frame flanks, three
         along the bottom - the center stays open for the active card */
      const SPOTS = [
        [2, 5, 24], [27, 3, 22], [51, 4, 22], [74, 5, 24],
        [1, 40, 22], [77, 40, 22],
        [4, 62, 26], [37, 66, 24], [68, 62, 26]];
      const sb = document.createElement("div");
      sb.className = "stackbox";
      const items = ev.stack.items.map((it, i) => {
        const [L, T, W] = SPOTS[i % SPOTS.length];
        const card = document.createElement("div");
        card.className = "stackcard";
        card.style.left = L + "%"; card.style.top = T + "%";
        card.style.width = W + "%";
        const img = document.createElement("img");
        img.src = A[it.id] || "";
        card.appendChild(img);
        sb.appendChild(card);
        /* hyperframes geometry (operator: "the evidence is actually
           dancing" in that cut): the base CSS rect is the card's RAIL
           spot; the ACTIVE pose (large, near stage center, where the
           card lives WHILE ITS LINE IS SPOKEN) is a transform relative
           to it. Stage is 1920x1080. */
        const wpx = W / 100 * STAGE_W, hpx = wpx * 480 / 1056;
        const cx = L / 100 * STAGE_W + wpx / 2, cy = T / 100 * STAGE_H + hpx / 2;
        const acx = 930 + (i % 2 ? 70 : -70), acy = 400 + (i % 3) * 26;
        return { card, at: it.at,
                 tilt: [-3, 2, -2, 3, -2.5, 2.5][i % 6],
                 dir: i % 2 ? 1 : -1,
                 adx: acx - cx, ady: acy - cy, asc: 840 / wpx,
                 bx: (cx - STAGE_W / 2) / (STAGE_W * 700 / 1920), by: (cy - STAGE_H / 2) / (STAGE_H * 460 / 1080) };   /* the burst's normalised offset from the STAGE centre; the 700/460 divisors were landscape px, kept as fractions so landscape is identical (2026-09-08) */
      });
      document.getElementById("stage").appendChild(sb);
      stackState[slot] = { sb, items, clear_at: ev.stack.clear_at };
    }
    let oldC = dockEl.querySelector(".chartbox"); if (oldC) oldC.remove();
    // (chartbox lives inside .slide-frame; querySelector reaches it there)
    chartState[slot] = null;
    dockEl.classList.toggle("chart", !!ev.chart && !ev.record);
    if (ev.chart && !ev.record) {
      const C = ev.chart, NS = "http://www.w3.org/2000/svg";
      const CW = 1056, CH = 480, PL = 64, PR = 120, PT = 96;
      /* chart hygiene (doc 29 s9.22): the x-axis labels get their own
         band; the source line never collides with them */
      const PB = C.xticks ? 70 : 44;
      const svg = document.createElementNS(NS, "svg");
      svg.setAttribute("viewBox", `0 0 ${CW} ${CH}`);
      svg.setAttribute("class", "chartbox");
      const mk = (tag, at, txt, parent) => {
        const e = document.createElementNS(NS, tag);
        for (const k in at) e.setAttribute(k, at[k]);
        if (txt) e.textContent = txt;
        (parent || svg).appendChild(e); return e;
      };
      /* QC 2026-08-30: header/src lines clamp to the canvas - a long
         subtitle ran off the card edge mid-word ("Strong prints ar").
         Squeezed via textLength at first tick (needs the DOM). */
      const hdrFit = [
        [mk("text", { class: "ct", x: 28, y: 44 }, C.title), CW - 56],
        [mk("text", { class: "cs", x: 28, y: 74 }, C.sub), CW - 56],
        [mk("text", { class: "csr", x: 28, y: CH - 14 }, C.src), CW - 56],
      ];
      if (C.ylabel && !C.panels)
        /* floats inside the plot, top-left - FT convention; never on
           the subtitle line. Paneled charts skip it: that corner
           belongs to the panel title and the yunit ticks carry units */
        mk("text", { class: "csr", x: PL + 10, y: PT + 20,
           opacity: 0.85 }, C.ylabel);
      const PAL = { crimson: "#e5484d", teal: "#1fa892", cobalt: "#4a7fd6",
                    amber: "#c98500", deemph: "#8b8f98" };
      /* graphic tier draws; TEXT tier reads. Same hue, lifted for contrast. */
      const TPAL = { crimson: "#ff8a8c", teal: "#3bc9b0", cobalt: "#8fb3f0",
                     amber: "#f5b72e", deemph: "#b8c4d0" };
      const st = { paths: [], labels: [], bars: [], marks: [], areas: [],
                   fitTexts: hdrFit };
      let clipN = 0;

      /* one panel = one mapped plot region; a plain chart is one panel */
      const panels = C.panels
        ? C.panels.map((p, i) => ({ ...p, i, n: C.panels.length }))
        : [{ series: C.series || [], sub: null, i: 0, n: 1 }];
      /* ONE scale across every panel - "same scale, side by side" must be
         true in the pixels, not just the subtitle. Per-panel ranges drew
         4.7% ABOVE 5.0% (operator catch, 2026-08-30). */
      const Y = (v) => C.log ? Math.log10(v) : v;
      let gy0 = 1e9, gy1 = -1e9;
      for (const pn0 of panels)
        for (const sr of pn0.series) for (const [, v] of sr.pts) {
          gy0 = Math.min(gy0, Y(v)); gy1 = Math.max(gy1, Y(v));
        }
      const HL = C.hlines || (C.hline ? [C.hline] : []);
      for (const h of HL) { gy0 = Math.min(gy0, Y(h.y)); gy1 = Math.max(gy1, Y(h.y)); }
      if (C.ymin != null) gy0 = Math.min(gy0, Y(C.ymin));
      if (C.ymax != null) gy1 = Math.max(gy1, Y(C.ymax));
      { const pad = (gy1 - gy0) * 0.06 || 1; gy0 -= C.ymin != null ? 0 : pad; gy1 += pad; }
      for (const pn of panels) {
        const gap = 44;
        const pw = (CW - PL - PR - gap * (pn.n - 1)) / pn.n;
        const px0 = PL + pn.i * (pw + gap);
        let x0 = 1e9, x1 = -1e9;
        for (const sr of pn.series) for (const [x] of sr.pts) {
          x0 = Math.min(x0, x); x1 = Math.max(x1, x);
        }
        const y0 = gy0, y1 = gy1;
        const mx = (x) => px0 + (x - x0) / (x1 - x0 || 1) * pw;
        const my = (v) => PT + (1 - (Y(v) - y0) / (y1 - y0)) * (CH - PT - PB);
        /* QC 2026-08-30 (two-eras "butchered"): a panel label at PT-10
           crashed into the card subtitle. It is a PANEL TITLE - it
           lives INSIDE its panel, top-left, FT-style. */
        if (pn.sub) mk("text", { class: "cs", x: px0 + 10, y: PT + 24 },
                       pn.sub);
        if (pn.i > 0)
          mk("line", { x1: px0 - gap / 2, x2: px0 - gap / 2, y1: PT - 24,
             y2: CH - PB, stroke: "#24262b", "stroke-width": 2 });
        /* Y GRIDLINES + TICKS - without an axis nothing on the document is
           verifiable (operator: "it stops before its stated 6.5%"). Log
           charts tick at doublings; linear at nice steps. */
        const ticks = [];
        if (C.log) { for (let v = 100; Y(v) <= y1; v *= 2) if (Y(v) >= y0) ticks.push(v); }
        else {
          const span = y1 - y0;
          const step = span > 4000 ? 2000 : span > 400 ? 500 : span > 40 ? 20
                     : span > 12 ? 5 : span > 4 ? 2 : 1;
          for (let v = Math.ceil(y0 / step) * step; v <= y1; v += step) ticks.push(v);
        }
        for (const v of ticks) {
          /* the zero line carries the baseline, so it reads heavier
             (remotion-ui line-chart-draw convention) */
          mk("line", { x1: px0, x2: px0 + pw, y1: my(v), y2: my(v),
             stroke: v === 0 ? "#3a3e46" : "#24262b",
             "stroke-width": v === 0 ? 2.5 : 1.5 });
          if (pn.i === 0) {
            let lab = C.yfmt === "usd"
              ? (v >= 1000 ? "$" + Math.round(v / 1000) + "k" : "$" + v)
              : (C.log || Number.isInteger(v)
                 ? String(v >= 1000 ? v.toLocaleString("en-US") : v)
                 : v.toFixed(1));
            if (C.yunit) lab += C.yunit;
            mk("text", { class: "csr", x: px0 - 10, y: my(v) + 5,
               "text-anchor": "end" }, lab);
          }
        }
        /* QC 2026-08-30: the baseline is the PLOT BOTTOM, a pixel
           constant - my(y0) re-applies the log transform to an already
           log-space value and threw log charts' date ticks off-canvas
           (the monitor rendered dateless) */
        const XB = CH - PB;
        for (const [xv, xl] of (C.xticks || [])) {
          if (xv < x0 || xv > x1) continue;
          mk("line", { x1: mx(xv), x2: mx(xv), y1: XB, y2: XB + 6,
             stroke: "#33363d", "stroke-width": 1.5 });
          mk("text", { class: "csr", x: mx(xv), y: XB + 22,
             "text-anchor": "middle" }, xl);
        }
        /* hline labels sit RIGHT-ALIGNED at the line's end (the panel's
           top-left belongs to the panel title / ylabel); stacked lines
           alternate above/below so 1%-apart tripwires never collide */
        const hlY = [];
        HL.forEach((h, hi) => {
          const hcol = PAL[h.color] || "#94a3b2";
          const htcol = TPAL[h.color] || "#b8c4d0";
          const hl = mk("line", { x1: px0, x2: px0 + pw,
            y1: my(h.y), y2: my(h.y), stroke: hcol,
            "stroke-width": 2, "stroke-dasharray": "7 6", opacity: 0 });
          st.marks.push({ el: hl, at: 0.15 + hi * 0.08 });
          if (h.label && pn.i === 0) {
            let ly = my(h.y) - 9;
            if (hlY.some((o) => Math.abs(o - ly) < 24)) ly = my(h.y) + 22;
            hlY.push(ly);
            st.marks.push({ el: mk("text", { class: "csr",
              x: px0 + pw - 8, y: ly, "text-anchor": "end",
              fill: htcol, opacity: 0 }, h.label),
              at: 0.15 + hi * 0.08 });
          }
        });
        const order = [...pn.series.keys()].reverse();
        /* INLINE SERIES NAMES (operator, 2026-08-31: "a source citation
           is not a chart key"). Placement is COLLISION-AWARE against
           the actual data ink (operator round 2: "the labels are all
           crashing with the lines"): candidate slots walk up then down
           from the line's start, and each is scored against EVERY
           series' path over the label's x-span; first clear slot wins. */
        const lineYat = (sr2, xq) => {
          const p = sr2.pts;
          if (xq <= p[0][0]) return my(p[0][1]);
          for (let i = 1; i < p.length; i++)
            if (p[i][0] >= xq) {
              const f = (xq - p[i-1][0]) / (p[i][0] - p[i-1][0] || 1);
              return my(p[i-1][1] + f * (p[i][1] - p[i-1][1]));
            }
          return my(p[p.length - 1][1]);
        };
        const placed = [];
        if (C.ylabel && !C.panels)
          placed.push({ x0: PL + 10, x1: PL + 10 + C.ylabel.length * 8.2,
                        y: PT + 20 });
        const clearAt = (x0q, x1q, yq) => {
          for (const sr2 of pn.series)
            for (let k = 0; k <= 4; k++) {
              const xq = x0q + (x1q - x0q) * k / 4;
              const xv = x0 + (xq - px0) / pw * (x1 - x0);
              if (Math.abs(lineYat(sr2, xv) - yq) < 13) return false;
            }
          return !placed.some((r) => x0q < r.x1 && x1q > r.x0 &&
                                     Math.abs(r.y - yq) < 18);
        };
        order.forEach((si, oi) => {
          const sr = pn.series[si];
          const col = PAL[sr.color] || "#f2f2ef";
          if (sr.name) {
            const w = sr.name.length * 8.2;
            const lx = mx(sr.pts[0][0]) + 6;
            const base = my(sr.pts[0][1]);
            let ny = null, nx = lx;
            for (const dyy of [-16, -34, 20, -52, 38, -70, 56, -88]) {
              const cand = base + dyy;
              if (cand < PT + 12 || cand > CH - PB - 6) continue;
              if (clearAt(lx, lx + w, cand)) { ny = cand; break; }
            }
            if (ny === null) {
              /* no clear air near the line start: fall back to a tidy
                 KEY BLOCK stacked top-left inside the plot - overlap-
                 tracked like every other label, never freeform */
              nx = px0 + 12;
              ny = PT + 40;
              while (placed.some((r) => nx < r.x1 && nx + w > r.x0 &&
                                        Math.abs(r.y - ny) < 18)) ny += 19;
            }
            placed.push({ x0: nx, x1: nx + w, y: ny });
            st.marks.push({ el: mk("text", { class: "csr",
              x: nx, y: ny, fill: TPAL[sr.color] || col,
              opacity: 0 }, sr.name), at: 0.08 + oi * 0.05 });
          }
          const d = sr.pts.map(([x, v], i) =>
            (i ? "L" : "M") + mx(x).toFixed(1) + " " + my(v).toFixed(1)).join(" ");
          if (sr.fill) {
            /* area under the line, revealed by a clip that grows with the
               draw - the prototype's grammar */
            const cid = "cclip" + (clipN++) + slot;
            const cp = mk("clipPath", { id: cid });
            const cr = mk("rect", { x: px0, y: 0, width: 0, height: CH }, null, cp);
            const base = my(Math.max(y0, Math.min(y1, HL.length ? HL[0].y : y0)));
            mk("path", { d: d + ` L ${mx(sr.pts[sr.pts.length-1][0]).toFixed(1)} ${base}`
                 + ` L ${mx(sr.pts[0][0]).toFixed(1)} ${base} Z`,
               fill: col, "fill-opacity": 0.10, "clip-path": `url(#${cid})` });
            st.areas.push({ rect: cr, w: pw });
          }
          const path = mk("path", { d, fill: "none", stroke: col,
            "stroke-width": sr.dash ? 2.5 : (si === 0 ? 5 : 3.5),
            "stroke-linecap": "round", "stroke-linejoin": "round" });
          /* a DASHED series (reference/trigger lines) cannot use the
             dashoffset draw trick - it fades in on its delay instead */
          const len = path.getTotalLength();
          if (sr.dash) {
            path.setAttribute("stroke-dasharray", sr.dash);
            path.setAttribute("opacity", 0);
            path.dataset.fadein = "1";
          } else {
            path.setAttribute("stroke-dasharray", len);
            path.setAttribute("stroke-dashoffset", len);
          }
          const last = sr.pts[sr.pts.length - 1];
          const lbl = mk("text", { class: "cl", x: mx(last[0]) + 12,
            y: my(last[1]) + 8, fill: TPAL[sr.color] || "#f4f6f8",
            opacity: 0 }, sr.label);
          /* TIP HEAD + DEPOSITED DOTS (harvested from remotion-ui
             line-chart-draw, 2026-08-31): a glowing head rides the
             draw's tip - read off the REAL path via getPointAtLength so
             it tracks the curve on steep segments - and on sparse
             series (<=16 pts) the data dots grow in as the tip passes:
             "the line depositing them rather than a blink". */
          let tip = null, dots = [];
          if (!sr.dash) {
            const halo = mk("circle", { r: sr.dash ? 0 : 9, fill: col,
              opacity: 0 });
            const core = mk("circle", { r: 4.2, fill: col, opacity: 0 });
            tip = { halo, core };
            if (sr.pts.length <= 16)
              dots = sr.pts.map(([x, v]) => mk("circle", { cx: mx(x),
                cy: my(v), r: 0, fill: col, stroke: "#16181c",
                "stroke-width": 2 }));
          }
          st.paths.push({ path, len, stagger: oi / Math.max(1, order.length),
                          delay: sr.delay || 0, tip, dots });
          st.labels.push(lbl);
        });
        /* EVENT BARS (doc 29 s9.22 combo convention): the print series
           as a volume-style histogram in the bottom band of the plot -
           teal up, crimson down; each bar lands as the draw reaches it */
        for (const eb of (C.eventbars || [])) {
          const bh = Math.abs(eb.v) / Math.max(...C.eventbars.map(
            (e) => Math.abs(e.v))) * (CH - PT - PB) * 0.22;
          const bx = mx(eb.x);
          const g2 = mk("g", { opacity: 0 });
          mk("rect", { x: bx - 9, y: my(y0) - bh, width: 18, height: bh,
             rx: 3, fill: eb.v >= 0 ? "#1fa892" : "#e5484d",
             "fill-opacity": 0.85 }, null, g2);
          mk("text", { class: "csr", x: bx, y: my(y0) - bh - 8,
             "text-anchor": "middle",
             fill: eb.v >= 0 ? "#3bc9b0" : "#ff8a8c" },
             (eb.v > 0 ? "+" : "") + eb.v.toFixed(1) + "%", g2);
          if (eb.label)
            mk("text", { class: "csr", x: bx, y: my(y0) - bh - 26,
               "text-anchor": "middle" }, eb.label, g2);
          st.marks.push({ el: g2, at: (eb.x - x0) / (x1 - x0 || 1) });
        }
        for (const m of (C.marks || [])) {
          const g = mk("g", { opacity: 0 });
          mk("circle", { cx: mx(m.x), cy: my(m.y), r: 9, fill: "#e5484d",
             stroke: "#16181c", "stroke-width": 4 }, null, g);
          const tx = mx(m.x) + (mx(m.x) > px0 + pw * 0.75 ? -14 : 14);
          const anch = mx(m.x) > px0 + pw * 0.75 ? "end" : "start";
          const mdy = m.dy || 0;
          /* QC 2026-08-30: annotation text was drawn bare over the data
             ink ("$27B quarter" across the price line). A backing chip
             sits behind the label pair - sized at first tick */
          /* a mark pushed clear of the data (big dy) gets a LEADER
             from its dot to its chip - an offset label with no leader
             reads as an accident (operator, monitor June mark) */
          if (Math.abs(mdy) > 40)
            mk("line", { x1: mx(m.x), y1: my(m.y) + Math.sign(mdy) * 12,
               x2: mx(m.x), y2: my(m.y) + mdy - Math.sign(mdy) * 26,
               stroke: "#8b95a3", "stroke-width": 1.5,
               "stroke-dasharray": "2 4" }, null, g);
          const chip = mk("rect", { x: tx, y: my(m.y) - 34 + mdy,
             height: 0, width: 0, rx: 6, fill: "#16181c",
             opacity: 0.78 }, null, g);
          const t1 = mk("text", { class: "cl", x: tx, y: my(m.y) - 12 + mdy,
             fill: "#f4f6f8", "text-anchor": anch }, m.label, g);
          const t2 = mk("text", { class: "csr", x: tx, y: my(m.y) + 12 + mdy,
             "text-anchor": anch }, m.sub || "", g);
          st.marks.push({ el: g, at: (m.x - x0) / (x1 - x0 || 1),
                          chip, t1, t2, anchX: tx, anch,
                          hasSub: !!m.sub });
        }
      }

      /* SHARES: horizontal proportion bars - the fill IS the claim. Built
         because a stat TILE (text on a rectangle) is a banned species
         (doc 29 s9.3, "fill-in paper toys") and proportions deserve to be
         SEEN: half of every pound Britain invested went into one
         technology. Row: label - track - fill to frac - numeral lands at
         the fill's edge - note beyond it. */
      /* CHECKLIST v2 - typewriter + marker-highlight (technique ported
         from remotion-ui: cap-height band, chisel-tilt leading edge,
         ~0.3 ink over dark ground; question cells TYPE on, answer cells
         get the highlighter swept through them). Optional per-row
         cell colors (r.colors) for status boards. */
      if (C.checklist) {
        /* QC 2026-08-30: fixed cols [PL,+300,+640,+990] put col 4 at
           x=1054 on a 1056 canvas (whole column clipped) and let long
           cells run into their neighbours. Columns now AUTO-FIT: text
           is measured at the first animation tick (needs the DOM),
           widths distribute across the usable span, and any cell still
           over its allotment squeezes via textLength. */
        const defCol = ["#f4f6f8", "#dce3ea", "#3bc9b0", "#ff8a8c"];
        const headEls = C.checklist.head.map((h) =>
          mk("text", { class: "csr", x: PL, y: PT + 18 }, h));
        st.rowEls = [];
        C.checklist.rows.forEach((r, i) => {
          const y = PT + 64 + i * 58;
          const colr = r.colors || defCol;
          const cells = [];
          r.cells.forEach((cell, ci) => {
            const g2 = mk("g", { opacity: 0 });
            let sweep = null, band = null;
            if (ci >= 2 && cell) {
              /* the band: cap-height, behind the text, clipped by a
                 chisel-tilted wipe. The skew pivots about the BAND'S
                 OWN corner - a bare skewX(-7) pivots about the SVG
                 origin and slides the clip tan(7deg)*y (~20-50px)
                 left, amputating the highlight's right end (the
                 "incomplete highlighter" QC class). */
              const cid2 = "hl" + slot + i + ci;
              const cp2 = mk("clipPath", { id: cid2 }, null,
                             mk("defs", {}, null, g2));
              sweep = mk("rect", { x: PL - 8, y: y - 21,
                width: 0, height: 30 }, null, cp2);
              const kmBand = kin("km_ink") && /^#[0-9a-f]{6}$/i.test(colr[ci]);   /* K-M (44 s44.1): the band IS a layer of ink over #16181c */
              band = mk("rect", { x: PL - 8, y: y - 21, width: 10,
                 height: 30, rx: 4, fill: kmBand ? kmHex("#16181c", colr[ci], INK.HIGHLIGHT_X) : colr[ci], opacity: kmBand ? 1 : 0.28,
                 "clip-path": `url(#${cid2})`, class: "hlband" + slot + i + ci }, null, g2);
            }
            const tx = mk("text", { class: "cs", x: PL, y,
               fill: colr[ci] }, ci === 0 ? "" : cell, g2);
            cells.push({ el: g2, tx, txt: cell, ci, sweep, band, y,
                         bandCls: "hlband" + slot + i + ci });
          });
          mk("line", { x1: PL, x2: CW - PR, y1: y + 18, y2: y + 18,
             stroke: "#24262b", "stroke-width": 1.5 });
          st.rowEls.push({ d: r.delay || i * 3, cells, y });
        });
        st.chkFit = { headEls, done: false, usable: CW - PL - 28 };
      }
      if (C.shares) {
        const rows = C.shares, rh = 46, gap2 = 30;
        const top = PT + 26;
        const trackW = CW - PL - PR - 150;
        rows.forEach((r, i) => {
          const y = top + i * (rh + gap2);
          const col = PAL[r.color] || "#e5484d";
          mk("text", { class: "cs", x: PL, y: y - 10 }, r.label);
          mk("rect", { x: PL, y, width: trackW, height: rh, rx: 9,
             fill: "#24262b" });
          const fill = mk("rect", { x: PL, y, width: 0, height: rh, rx: 9,
             fill: col });
          const num = mk("text", { class: "cl", x: PL, y: y + rh / 2 + 9,
             fill: "#f4f6f8", opacity: 0 }, r.value);
          const note = r.note ? mk("text", { class: "csr",
             x: PL + trackW + 14, y: y + rh / 2 + 5, opacity: 0 }, r.note)
             : null;
          st.bars.push({ rect: fill, note: num, note2: note,
             h: null, share: { w: trackW * r.frac, numEl: num, x0: PL,
                               trackW },
             stagger: i / Math.max(1, rows.length) });
        });
        if (C.foot)
          mk("text", { class: "cs", x: PL,
             y: top + rows.length * (rh + gap2) + 8 }, C.foot);
      }

      /* BARS: grow from the baseline, staggered, note landing with the bar */
      if (C.bars) {
        const n = C.bars.length, plot = CW - PL - PR;
        const bw = Math.min(150, plot / (n * 1.9));
        const vmax = Math.max(...C.bars.map((b) => b.value)) * 1.18;
        const baseY = CH - PB - 26;
        C.bars.forEach((b, i) => {
          const cx = PL + plot * (i + 0.5) / n;
          const col = PAL[b.color] || "#8b8f98";
          const h = (b.value / vmax) * (baseY - PT);
          const rect = mk("rect", { x: cx - bw / 2, y: baseY, width: bw,
            height: 0, rx: 7, fill: col });
          const note = mk("text", { class: "cl", x: cx, y: baseY - h - 12,
            fill: "#f4f6f8", "text-anchor": "middle", opacity: 0 }, b.note);
          mk("text", { class: "csr", x: cx, y: baseY + 24,
             "text-anchor": "middle" }, b.label);
          st.bars.push({ rect, note, h, baseY, stagger: i / n });
        });
        mk("line", { x1: PL, x2: CW - PR, y1: baseY, y2: baseY,
           stroke: "#33363d", "stroke-width": 2 });
      }
      /* into the slide-frame, so the rail (pills) stays BENEATH the chart
         exactly as with a static document */
      /* de-overlap end labels: two series ending within 26px stack their
         labels (MAMAA +20% on S&P +21%); push later ones down */
      const ys = [];
      for (const l of st.labels) {
        let y = +l.getAttribute("y");
        while (ys.some((o) => Math.abs(o - y) < 26)) y += 26;
        l.setAttribute("y", y); ys.push(y);
      }
      dockEl.querySelector(".slide-frame").appendChild(svg);
      chartState[slot] = st;
    }
    /* VIDEO DOCK (E44): the slide is a clip, so the card mounts a <video> (paintDockClip, on the
       clip world's own seek) and the <img> stands down. A slide that is NOT a clip parks whatever
       clip the previous slide left in this card's frame. */
    const isVideo = dockIsVideo(aid);
    dockEl.classList.toggle("video", isVideo);
    if (!isVideo) parkDockClips(dockEl);
    $("i" + n).src = (ev.record || ev.chart || isVideo) ? "" : (A[aid] || "");
    const rail = $("r" + n); rail.innerHTML = "";
    rail.classList.toggle("single", ev.badges.length === 1);
    ev.badges.forEach((bd, bi) => {
      const el = document.createElement("div");
      el.className = "pill"; el.id = `p${n}${bi}`;
      el.innerHTML = `<span class="pill-label">${bd.label}</span><span class="pill-row">` +
        `<span class="pill-num" style="color:${ACCENT[bd.accent] || "var(--sunflower)"}">${bd.value}</span>` +
        `<span class="pill-tag" style="color:${ACCENT[bd.accent] || "var(--sunflower)"}">${bd.tag}</span></span>`;
      rail.appendChild(el);
    });
  };

  let shown = ["", ""];
  const recState = [null, null];
  const chartState = [null, null];
  const stackState = [null, null];
  /* the verdict stack: fly-in from depth on each item's word beat,
     idle float while holding, stagger-burst on the clear beat */
  const drawStack = (slot, t, d) => {
    const st = stackState[slot]; if (!st) return;
    if (t > st.clear_at + 1.4 || t < d.enter - 0.5) {
      st.sb.remove(); stackState[slot] = null; return;
    }
    st.items.forEach((it, i) => {
      if (t >= st.clear_at) {
        /* radial burst: each card is thrown outward from stage center
           along its own bearing, spinning as it goes */
        const cb = clamp01((t - st.clear_at - i * 0.06) / 0.5);
        const cbe = cb * cb;
        it.card.style.opacity = (1 - cb).toFixed(2);
        it.card.style.transform =
          `translate(${cbe * 560 * it.bx}px, ${cbe * 420 * it.by}px)` +
          ` translateZ(${cbe * 340}px)` +
          ` rotate(${it.tilt + cbe * 24 * it.dir}deg)` +
          ` scale(${1 + cbe * 0.22})`;
        return;
      }
      /* hyperframes focus hand-off: enter LARGE at stage center while
         the phrase is spoken; when the NEXT proof's beat lands, recede
         to the rail spot; drift the whole time. Pure function of t -
         scrub-safe. */
      const nextAt = i + 1 < st.items.length
        ? st.items[i + 1].at : st.clear_at - 0.9;
      const e = clamp01((t - it.at) / 0.9);
      const ee = 1 - Math.pow(1 - e, 3);
      const r = clamp01((t - nextAt) / 1.0);
      const rr = r < 0.5 ? 4 * r * r * r
                         : 1 - Math.pow(-2 * r + 2, 3) / 2;
      // pose blend: 0 = rail, 1 = active
      const a = ee * (1 - rr);
      const drift = Math.sin(t * 0.55 + i * 1.7);
      const dx = it.adx * a + drift * (8 + 26 * a);
      const dy = it.ady * a + Math.cos(t * 0.7 + i * 2.1) * (5 + 14 * a);
      const sc = 1 + (it.asc - 1) * a + drift * 0.008 * a;
      it.card.style.opacity = ee.toFixed(2);
      it.card.style.zIndex = a > 0.5 ? 9 : 7;
      it.card.style.transform =
        `translate(${(dx + (1 - ee) * 460 * it.dir).toFixed(1)}px,` +
        ` ${(dy + (1 - ee) * -90).toFixed(1)}px)` +
        ` translateZ(${(1 - ee) * -700}px)` +
        ` rotateY(${(1 - ee) * 30 * it.dir}deg)` +
        ` rotate(${(it.tilt * (1 - a) + drift * 0.6 * a).toFixed(2)}deg)` +
        ` scale(${sc.toFixed(3)})`;
    });
  };
  /* the line is drawn over the first stretch of the hold - eased, series
     staggered so the base layers exist before the star lands on top */
  const drawChart = (slot, t, d) => {
    const st = chartState[slot]; if (!st) return;
    const DUR = Math.min(6, Math.max(2.5, (d.exit - d.enter) * 0.38));
    const p = clamp01((t - d.enter - CARD_IN * 0.6) / DUR);
    const tRel = t - d.enter - CARD_IN * 0.6;
    st.doneAt = d.enter + CARD_IN * 0.6 + DUR;   // badge floor: conclusions land after the draw
    st.paths.forEach((pp, i) => {
      if (pp.path.dataset && pp.path.dataset.fadein) {
        const fo = clamp01((tRel - pp.delay) / 0.8);
        pp.path.setAttribute("opacity", fo.toFixed(2));
        /* QC 2026-08-30: this early return orphaned the reference
           series' END LABEL - the dashed 12-mo trigger line rendered
           unnamed ("what IS the white dotted line?"). The label fades
           with its line. */
        if (st.labels[i]) st.labels[i].setAttribute("opacity", fo.toFixed(2));
        return;
      }
      /* a series may hold back (sidecar `delay`, seconds): the source's own
         chart draws first, the added layers erupt through it */
      const lp = clamp01(((tRel - pp.delay) / DUR - pp.stagger * 0.35) / 0.65);
      const frac = strokeFrac(pp.path, pp.len, lp) ?? expoOut(lp);   /* a hand's progress under curvature_stroke */
      pp.path.setAttribute("stroke-dashoffset",
        (pp.len * (1 - frac)).toFixed(1));
      st.labels[i].setAttribute("opacity",
        clamp01((lp - 0.92) / 0.08).toFixed(2));
      if (pp.tip) {
        const drawing = frac > 0.01 && frac < 0.995;
        let tx2 = Infinity;
        if (drawing) {
          const p2 = pp.path.getPointAtLength(pp.len * frac);
          tx2 = p2.x;
          pp.tip.core.setAttribute("cx", p2.x); pp.tip.core.setAttribute("cy", p2.y);
          pp.tip.halo.setAttribute("cx", p2.x); pp.tip.halo.setAttribute("cy", p2.y);
        }
        pp.tip.core.setAttribute("opacity", drawing ? 1 : 0);
        pp.tip.halo.setAttribute("opacity", drawing ? 0.18 : 0);
        for (const dot of pp.dots) {
          const reveal = frac <= 0.01 ? 0 : frac >= 0.995 ? 1
            : clamp01((tx2 - (+dot.getAttribute("cx")) + 26) / 26);
          dot.setAttribute("r", (4.6 * reveal).toFixed(1));
        }
      }
    });
    /* area fills reveal with the primary line's progress */
    for (const a of st.areas)
      a.rect.setAttribute("width", (a.w * expoOut(p)).toFixed(1));
    if (st.fitTexts) {
      for (const [el2, maxW] of st.fitTexts) {
        if (!el2.textContent || !el2.getComputedTextLength) continue;
        const len = el2.getComputedTextLength();
        if (len <= maxW) continue;
        const ratio = maxW / len;
        if (ratio < 0.93) {   /* big overflow: shrink the type instead
                                 of crushing glyph spacing */
          const fs = parseFloat(getComputedStyle(el2).fontSize) || 19;
          el2.style.fontSize = Math.max(13, fs * ratio).toFixed(1) + "px";
        }
        if (el2.getComputedTextLength() > maxW) {
          el2.setAttribute("textLength", maxW);
          el2.setAttribute("lengthAdjust", "spacingAndGlyphs");
        }
      }
      st.fitTexts = null;
    }
    /* marks land when the line reaches them; hlines early */
    for (const m of st.marks) {
      if (m.chip && !m.sized && m.t1.getComputedTextLength) {
        const w = Math.max(m.t1.getComputedTextLength(),
                           m.hasSub ? m.t2.getComputedTextLength() : 0) + 16;
        if (w > 16) {
          m.chip.setAttribute("width", w.toFixed(0));
          m.chip.setAttribute("height", m.hasSub ? 56 : 32);
          if (m.anch === "end")
            m.chip.setAttribute("x", (m.anchX - w + 8).toFixed(0));
          else m.chip.setAttribute("x", (m.anchX - 8).toFixed(0));
          m.sized = true;
        }
      }
      const on = p >= m.at;
      m.el.setAttribute("opacity", on
        ? clamp01((p - m.at) / 0.06).toFixed(2) : 0);
    }
    /* bars grow staggered from the baseline; the note lands with the bar */
    if (st.chkFit && !st.chkFit.done && st.rowEls && st.rowEls.length) {
      /* one-time column fit - measurement needs the DOM. Natural width
         per column (headers + cells, col-0 measured with its full text
         restored after), distributed across the usable span; slack
         spreads evenly, deficit squeezes columns proportionally and
         over-long cells compress via textLength. */
      const F = st.chkFit, NC = F.headEls.length, PAD = 26;
      const natW = new Array(NC).fill(40);
      const meas = (el) => el.getComputedTextLength
        ? el.getComputedTextLength() : (el.textContent.length * 10);
      F.headEls.forEach((h, ci) => natW[ci] = Math.max(natW[ci], meas(h)));
      for (const r of st.rowEls) for (const c of r.cells) {
        const keep = c.tx.textContent;
        if (c.ci === 0) c.tx.textContent = c.txt;
        natW[c.ci] = Math.max(natW[c.ci], meas(c.tx));
        if (c.ci === 0) c.tx.textContent = keep;
      }
      const alloc = natW.map((w) => w + PAD);
      const total = alloc.reduce((a, b) => a + b, 0);
      const scale2 = total > F.usable ? F.usable / total : 1;
      const extra = total < F.usable ? (F.usable - total) / NC : 0;
      const xs = []; let acc = 64;
      for (let ci = 0; ci < NC; ci++) {
        xs.push(acc); acc += alloc[ci] * scale2 + extra;
      }
      F.headEls.forEach((h, ci) => h.setAttribute("x", xs[ci]));
      for (const r of st.rowEls) for (const c of r.cells) {
        c.tx.setAttribute("x", xs[c.ci]);
        const room = alloc[c.ci] * scale2 + extra - PAD + 8;
        if (c.ci > 0 && natW[c.ci] >= room && meas(c.tx) > room) {
          c.tx.setAttribute("textLength", room.toFixed(0));
          c.tx.setAttribute("lengthAdjust", "spacingAndGlyphs");
        }
        c.room = room;
        if (c.sweep) {
          const x0 = xs[c.ci] - 8, y0 = c.y - 21;
          for (const el of [c.sweep, c.band]) {
            el.setAttribute("x", x0); el.setAttribute("y", y0);
          }
          c.sweep.setAttribute("transform",
            `translate(${x0} ${y0}) skewX(-7) translate(${-x0} ${-y0})`);
        }
      }
      F.done = true;
    }
    /* QC 2026-08-30 (the s73 scorecard showed EMPTY): row delays are
       resolved against the FIRST showing's narration and shared across
       instances - on a short re-dock every row landed past the exit.
       A checklist on a short hold is a RECAP: it fills fast. */
    const recap = (d.exit - d.enter) < 12;
    (st.rowEls || []).forEach((r, ri) => {
      const rowDelay = recap ? ri * 0.8 : r.d;
      /* cell choreography inside a row: question TYPES at +0, where
         fades at +0.6, steel sweep at +1.0, paper sweep at +1.6 */
      const offs = recap ? [0, 0.25, 0.45, 0.7] : [0, 0.6, 1.0, 1.6];
      r.cells.forEach((c, k) => {
        const ct = tRel - rowDelay - offs[Math.min(k, 3)];
        const o = clamp01(ct / 0.35);
        c.el.setAttribute("opacity", o.toFixed(2));
        if (c.ci === 0) {
          const nch = Math.max(0, Math.floor(ct / 0.045));
          const want = c.txt.slice(0, nch);
          if (c.tx.textContent !== want) c.tx.textContent = want;
        }
        if (c.sweep) {
          const p = clamp01(ct / 0.55);
          const ease = 1 - Math.pow(1 - p, 3);
          const w = Math.min((c.tx.getComputedTextLength
            ? c.tx.getComputedTextLength() : 300) + 18,
            (c.room || 300) + 12);
          c.sweep.setAttribute("width", (ease * w).toFixed(1));
          const band = c.el.querySelector("." + c.bandCls);
          if (band) band.setAttribute("width", (w).toFixed(1));
        }
      });
    });
    for (const b of st.bars) {
      const bp = expoOut(clamp01((p - b.stagger * 0.4) / 0.6));
      if (b.share) {           /* proportion row: fill grows rightward */
        const w = b.share.w * bp;
        b.rect.setAttribute("width", Math.max(0, w).toFixed(1));
        /* QC 2026-08-30 ("3x" on "silicon, same gigabyte"): a
           near-full fill leaves no room outside it - the numeral
           moves INSIDE the fill's right end, clear of the note */
        if (b.share.w > b.share.trackW - 96) {
          b.share.numEl.setAttribute("text-anchor", "end");
          b.share.numEl.setAttribute("x", (b.share.x0 + w - 12).toFixed(1));
        } else
          b.share.numEl.setAttribute("x", (b.share.x0 + w + 12).toFixed(1));
        b.note.setAttribute("opacity", clamp01((bp - 0.85) / 0.15).toFixed(2));
        if (b.note2) b.note2.setAttribute("opacity",
          clamp01((bp - 0.85) / 0.15).toFixed(2));
        continue;
      }
      const h = b.h * bp;
      b.rect.setAttribute("height", Math.max(0, h).toFixed(1));
      b.rect.setAttribute("y", (b.baseY - h).toFixed(1));
      b.note.setAttribute("opacity", clamp01((bp - 0.9) / 0.1).toFixed(2));
    }
  };
  const drawRecord = (slot, t) => {
    const st = recState[slot]; if (!st) return;
    const { r, q } = st, W = r.words;
    let i = -1;
    while (i + 1 < W.length && W[i + 1][1] <= t) i++;
    const frag = document.createDocumentFragment();
    for (let k = 0; k <= i; k++) {
      const [w, ts] = W[k];
      const next = W[k + 1] ? W[k + 1][1] : r.end;
      let txt = w;
      if (k === i) {          // string slicing, never per-character opacity
        const span = Math.max(0.08, (next - ts) * 0.72);
        const p = Math.max(0, Math.min(1, (t - ts) / span));
        txt = w.slice(0, Math.round(w.length * p));
      }
      if (k >= r.hl[0] && k <= r.hl[1]) {
        const sp = document.createElement("span");
        sp.className = "hw";
        sp.textContent = (k < i && k < r.hl[1]) ? txt + " " : txt;
        const swept = Math.max(0, Math.min(1, (t - ts) / 0.2));
        sp.style.backgroundSize = ((1 - Math.pow(1 - swept, 3)) * 100) + "% 100%";
        frag.append(sp);
        if (k === r.hl[1] && k < i) frag.append(document.createTextNode(" "));   /* the space after the phrase, outside the stroke (Tokyo 2026-09-10: "yen($65 billion)") */
      } else {
        frag.append(document.createTextNode(txt));
        if (k < i) frag.append(document.createTextNode(" "));
      }
    }
    const cur = document.createElement("span");
    cur.className = "pcur"; frag.append(cur);
    q.replaceChildren(frag);
    st.attr.classList.toggle("shown", t > r.end + 0.15);
    st.src.classList.toggle("shown", t > r.end + 0.45);
  };
  /* ================= LEDGER PAGE species (doc 29 s9.26 / P35 T3) =================
     Four beats, all from t (seconds since the scene opened):
       roll-out 0..ROLL          the page unrolls left->right, rolled-edge light on the front
       bleed    ROLL..+BLEED     seeded ink blobs bloom, merge (goo filter) and contract while the
                                 crisp charcoal field resolves beneath - a stained page, cream margin
       ink      +INK             ink writes title/source in the handwriting face as the punch begins
       build    +BUILD           the chart lands crisp on the exact value strings (story bars or
                                 the dense line with tip head and inline series names, s9.23b)
     Surface x builder are independent axes (s9.28): the page spec names the builder. */
  /* E22 addendum 2: unravel -> half savor -> the field (SOAK: ink absorbed by the paper, or
     SCRIBBLE: strokes accumulating with a nib - the operator's original idea; page.field picks)
     -> ink writes -> the build. E22 addendum 7: the outline is RETIRED - the deckle is the edge. */
  /* E22 addendum 6 (operator, 2026-09-03): "draw the line -> punch/zoom in (we have the line we drew + the deckle we
     don't even care about as room) -> draw the chart -> perform the focus action on the data we want to call out."
     PUNCH: the page zooms about the board's centre by PUNCH_SCALE, cropping the line and the deckle margin out;
     the build runs on the punched page; FOCUS: the page's declared focus species fires at the build's end. */
  /* STAGE caption pop (s9.25 #2): scale 1.16 -> 1.0 with a back-ease over STAGE_POP_S, the tilt
     settling to 0 - a function of (t - word.s), painted inline by the caption pass */
  const STAGE_POP_S = 0.2;
  const PHRASE = TL.caption_style === "phrase", PHRASE_STAGGER_S = 0.03, PHRASE_KPOP = 1.18;   /* shorts: the page lands as one phrase; only k-words are punctuated */
  /* the MARKER (hyperframes caption-highlight): the box sweeps in over SWEEP_S from the left (power2.out), lets go over BOX_FADE_S;
     keywords take the accent box, other words the charcoal box (brand tokens, never the reference's red) */
  /* knobs turned down (operator, 2026-09-05: 'it starts out WAY too busy ... a lot of flashes, not a lot of motion - an old lesson'):
     no flash; the phrase SETTLES over LAND_S from a small scale and rise; the keyword's pop is slight and its box sweeps slowly */
  /* toned down (operator, 2026-09-05: 'better, just tone it down now'): the captions' own dials - the pop, the lift on the spoken word, the
     rise, the keyword's extra pop, and a boil of their own at about half the plates' */
  const MARK = { RED: [[255, 23, 69], [223, 18, 56]], POP: 1.10, LIFT: 1.03, RISE_PX: 6, SWEEP_S: 0.2, KPOP: 1.06, BOIL_PX: 0.7, BOIL_DEG: 0.4 };
  const markBox = (c, a) => "linear-gradient(135deg, rgba(" + c[0].join(",") + "," + a.toFixed(3) + ") 0%, rgba(" + c[1].join(",") + "," + a.toFixed(3) + ") 100%)";
  const stagePop = (u) => { const c1 = 1.70158, c3 = c1 + 1; const x = u - 1; return 1 + c3 * x * x * x + c1 * x * x; };
  const LP = { ROLL: 0.7, SAVOR: 0.8, FIELD: 2.4, PUNCH: 0.5, INK: 2.0, BUILD: 3.0, SEEPS: 9, STROKES: 14, KB_MAX: 0.03,
               PUNCH_SCALE: 1.16, FOCUS_DUR: 3.0 };
  const LP_FOCUS_AT = LP.ROLL + LP.SAVOR + LP.FIELD + LP.PUNCH + LP.BUILD;   /* 7.4s: the focus action fires here */
  /* BADGES on the page (operator, 2026-09-03: 'we need the badges back'): the dock's own pills - verbatim label /
     value / tag with the series' accent as the key - spring in one at a time AFTER the build (the callout is the
     conclusion), in the page's quiet zone, painted as a function of t (never a CSS transition) */
  const LP_BADGE0 = 0.4, LP_BADGE_STEP = 0.9, LP_BADGE_IN = 0.36;
  const SNAP_S = 0.45, SNAP_BLUR = 6, CARD_SCALE = 1;   /* CARD_SCALE: a card page's rest size - the FRAME (operator, 2026-09-08: 'the holding page isn't supposed to show around it, it's supposed to land as the card/dock size, then zoom to fill' - the snap IS the punch-in to fill; the rounded corners survive at the frame's own corners) */   /* the third watch: the card snaps up to the full stage - a push tied to a landing [DERIVED: E45's spring-in span]; SNAP_BLUR: the whoosh's peak blur, px [DERIVED: zoom-through's blurPeak 8 at 1080p, scaled] */
  /* THE THROW (enter=throw, 2026-09-08): a full page is a card too - the Tokyo dock's throw at page size. The operator on the first
     damped draft (arc 0.12, "a page-sized card at the pill's arc would leave the frame"): "I actually think it would be cool if it DID
     leave the frame mid arc ... it 'wobbles' out of screen, before flopping back down." So the arc is tall enough that the page clears
     the top edge at the apex (lift = ARC x chord at u = 0.5; from below the chord is ~1.12 H, so ARC 0.8 puts the apex ~0.9 H above the
     rest and the page is off the top of the frame for the middle of the flight), the tumble is the pill's 9 deg, the flight a little
     longer than the pill's for the height, and the landing is the paper material's own: the receiver's dip on an underdamped spring
     (zeta 0.67 - that is the wobble) and the restitution hop h1 = e^2 h0, which the tall arc makes visible - the flop. Dials. */
  const THROW_S = 1.1, THROW_ARC = 1.5, THROW_SPIN = 9, THROW_SETTLE_S = 1.2, THROW_CARD = 0.62;   /* THROW_S: 0.7 was 'way too fast' on the watch (operator, 2026-09-08) - a card that leaves the frame and comes back as the world needs more air than the dock's 0.45; per page via throw_s */   /* THROW_CARD: the flat-growth law's card size (throw_grow: snap) [DERIVED: the dock's reading size] */
  /* the DEPTH ARC's dials [DERIVED, HG2 tunes by eye]: Z0 0.55 = 1.8x the stage as the card passes the camera; Z_LIFT 0.6 = the apex
     at z ~1.35 (0.74x); PITCH 55 deg seen from below as it passes, flat at the contact; BEND 35 deg per unit of motion squash; the
     camera follows 35 % of the card's height; the perspective is a phone held at arm's length (1600 px on a 1080 stage) */
  /* THROW_GROW_AT: the card starts growing into the world at this fraction of the flight. 0.5 grew it through the whole descent, so
     it was nearly stage-sized while still high and its title could not be in frame until it landed ("it is cut off", operator
     2026-09-08); at 0.8 the card comes back WHOLE at card size and snaps up to the stage over the last fifth of the flight - the
     snap on the landing. The ARC (1.5 x the chord, THROW_ARC above) carries a 0.62 card clear of the top edge with the camera
     following a quarter of its height. */
  const DROP_S = 0.55, DROP_FROM_H = 1.1;   /* the DROP (enter=drop): from just above the frame, easing in over 0.55 s [DERIVED: a page-height fall under the stop-action drop law] */
  const THROW_GROW_AT = 0.8, THROW_PITCH = 45, THROW_BEND = 35, THROW_FOLLOW = 0.25, THROW_PERSP = 1600, THROW_SQUASH = 0.15;   /* THROW_SQUASH: the page's share of the motion squash - 0.25 x 0.15 ~ 4 % at top speed */
  const THROW_FROM = { below: { x: STAGE_W * 0.06, y: STAGE_H * 1.1 }, above: { x: -STAGE_W * 0.06, y: -STAGE_H * 1.1 },
                       right: { x: STAGE_W * 1.1, y: STAGE_H * 0.06 }, left: { x: -STAGE_W * 1.1, y: STAGE_H * 0.06 } };
  const LP_BADGE_COL = { coral: "crimson", teal: "teal", cobalt: "cobalt", ink: "deemph", sunflower: "amber" };   /* badge accent -> series colour (the key) */
  /* THE IDLE (E49, P47 T5): every held thing carries a NAMED subtle idle - a pure function of t, behind kinetics.idle.
     The class defaults below; a scene's world.idle overrides its page or plate ("none" is explicit stillness, declared);
     the phase is the element's own (lpHash), so two pills never breathe in step. Never an event for the motion gate
     (M01 / M10 / M16 count events); the frozen-frames row M18 is the idle's own check (measure_frozen_frames.py). */
  const IDLE_CLASS = Object.freeze({ page: "breath", plate: "breath", dock: "breath", pill: "breath", caption: "breath" });
  const idleOf = (cls, override) => (kin("idle") ? (override || IDLE_CLASS[cls] || "none") : "none");
  const idleCssFor = (cls, override, t, seed, salt) => { const k = idleOf(cls, override); return k === "none" ? "" : idleCss(idleXf(k, t, lpHash(seed | 0, salt | 0, 977))); };
  /* pure hash of (seed, index, salt) -> [0,1): the only source of jitter (handwriting-text rule 2) */
  const lpHash = (seed, i, salt) => {
    let h = (seed ^ Math.imul(i + 1, 0x9E3779B1) ^ Math.imul(salt + 1, 0x85EBCA77)) >>> 0;
    h = Math.imul(h ^ (h >>> 15), 0x2C1B3C6D); h = Math.imul(h ^ (h >>> 12), 0x297A2D39);
    return ((h ^ (h >>> 15)) >>> 0) / 4294967296;
  };
  const ledgerState = new Map();
  /* the handwriting face is fetched on FIRST USE, so document.fonts.ready can resolve before any Kalam glyph exists; the
     portrait layout MEASURES its ink (P41), so the faces are fetched up front and every page is rebuilt once they land */
  const LP_FACES = ["700 68px Kalam", "400 40px Kalam", "500 40px Kalam", "700 34px Kalam"];
  if (document.fonts && document.fonts.load) Promise.all(LP_FACES.map((f) => document.fonts.load(f))).then(() => { if (PORTRAIT) ledgerState.clear(); }).catch(() => {});   /* landscape pages are laid out in %, never measured: a rebuild there only shifts chart text a sub-pixel against the goldens */
  /* PORTRAIT LAYOUT (P41): one column in stage px, measured top-down inside doc 49's zones - the title from y=140
     (zone 1), the chart in zone 2, the caption strip from 1340 (two 64px caption lines reach up to ~1290, so the page
     ends at 1280); x inside the safe box 80..880 (G-l). FIELD is the charcoal's box: a 3.5% / 2% cream margin IS the deckle. */
  const LP_PORTRAIT = { FIELD: { x: 0.035, y: 0.02, w: 0.93, h: 0.96 }, TOP: 150, X: 80, W: 800, TITLE_W: 920, BOTTOM: 1280, GAP: 24, CHART_MIN: 320 };   /* TITLE_W: the Shorts right-hand column starts below y~900, so the title band may run to x=1000 */
  const lpPortraitLayout = (E) => {
    const P = LP_PORTRAIT, px = (v) => v.toFixed(0) + "px";
    for (const el of [E.title, E.subEl, E.src, E.rail]) { el.style.left = px(P.X); el.style.width = px(P.W); el.style.maxWidth = px(P.W); }
    E.title.style.top = px(P.TOP); E.title.style.width = px(P.TITLE_W); E.title.style.maxWidth = px(P.TITLE_W);
    const h1 = E.title.offsetHeight, subTop = P.TOP + h1 + 16;
    E.subEl.style.top = px(subTop);
    const h2 = E.subEl.textContent.trim() ? E.subEl.offsetHeight : 0, chartTop = subTop + h2 + P.GAP + 8;
    const hs = E.src.textContent.trim() ? E.src.offsetHeight : 0, hr = E.rail.children.length ? E.rail.offsetHeight : 0;
    const chartH = Math.round(Math.max(P.CHART_MIN, P.BOTTOM - chartTop - (hs ? hs + P.GAP : 0) - (hr ? hr + P.GAP : 0)));
    E.chart.style.left = px(P.X); E.chart.style.top = px(chartTop); E.chart.style.width = px(P.W); E.chart.style.height = px(chartH);
    E.chart.setAttribute("viewBox", "0 0 " + P.W + " " + chartH);   /* the viewBox IS the pixel box: builders draw in stage px */
    E.src.style.top = px(chartTop + chartH + P.GAP);
    E.rail.style.top = px(chartTop + chartH + P.GAP + (hs ? hs + P.GAP : 0));
    return { W: P.W, H: chartH };
  };
  /* portrait copy: the sub keeps its first clause (to ";" or the first sentence end), the source its first clause (to ";") -
     one column has no room for the rest, and the selected-date rule moves to the axis ticks (E28) */
  const lpFirstClause = (str, sentence) => {
    const s = String(str || ""), cuts = [s.indexOf(";"), sentence ? s.indexOf(". ") : -1].filter((i) => i > 0);
    if (!cuts.length) return s;
    const i = Math.min(...cuts); return s.slice(0, i + (s[i] === "." ? 1 : 0)).trim();
  };
  /* a currency unit is a prefix ("$577", "-$40"); every other unit is a suffix ("12%") */
  const lpWithUnit = (str, unit) => unit === "$" ? (String(str).startsWith("-") ? "-$" + String(str).slice(1) : "$" + str) : str + (unit || "");
  const NSV = "http://www.w3.org/2000/svg";
  const lpEl = (tag, cls, parent, at) => {
    const e = tag === "svg" || (parent && parent.namespaceURI === NSV && tag !== "div" && tag !== "span")
      ? document.createElementNS(NSV, tag) : document.createElement(tag);
    if (cls) e.setAttribute("class", cls);
    for (const k in (at || {})) e.setAttribute(k, at[k]);
    if (parent) parent.appendChild(e); return e;
  };
  const lpGlyphs = (parent, text, seed) => {
    const out = [];
    [...text].forEach((ch, i) => {
      const g = lpEl("span", "g", parent); g.textContent = ch === " " ? " " : ch;   /* NBSP as an escape: an inline-block span with a plain space collapses to nothing */
      g.style.setProperty("--tilt", ((lpHash(seed, i, 3) - 0.5) * 3.2).toFixed(2) + "deg");
      out.push(g);
    });
    return out;
  };
  /* word-wrapped ink: each word is an inline-block of glyph spans, words separated by real spaces so the line breaks */
  const lpGlyphsWrap = (parent, text, seed) => {
    const out = []; let i = 0;
    String(text).split(" ").forEach((word, k) => {
      if (k) parent.appendChild(document.createTextNode(" "));
      const w = lpEl("span", "w", parent);
      [...word].forEach((ch) => { const g = lpEl("span", "g", w); g.textContent = ch;
        g.style.setProperty("--tilt", ((lpHash(seed, i++, 3) - 0.5) * 3.2).toFixed(2) + "deg"); out.push(g); });
    });
    return out;
  };
  const lpFmt = (v) => Math.abs(v) >= 100 ? v.toFixed(0) : Math.abs(v) >= 10 ? v.toFixed(1) : v.toFixed(2);
  const buildLedger = (el, scene) => {
    const pg = scene.world.page || {}, seed = 0x1B1EEDCA ^ (scene.scene_id || "").length;
    el.querySelectorAll(".lp").forEach((x) => x.remove());
    const root = lpEl("div", "lp", el);
    const page = lpEl("div", "lp-page", root);
    /* the page ground is a GENERATED world plate (operator, 2026-09-03: "the background needs to be a plate
       that GPT generates, it doesn't look like our world plates"); page.plate names it in the asset map.
       The CSS cream is the fallback only while no plate is approved. */
    if (pg.plate && A[pg.plate]) { page.style.backgroundImage = 'url("' + A[pg.plate] + '")'; page.style.backgroundSize = ((pg.plate_zoom || 1) * 100).toFixed(1) + "% " + ((pg.plate_zoom || 1) * 100).toFixed(1) + "%"; page.style.backgroundPosition = "center"; }
    /* the BOARD box: measured from the inked plate when one exists (page.board, fractions of the frame), else the
       s9.26 default 6% / 8% / 88% x 84%; the field fallback and the chart take the same box */
    const bd = pg.board || (PORTRAIT ? LP_PORTRAIT.FIELD : { x: 0.06, y: 0.08, w: 0.88, h: 0.84 });   /* portrait: the charcoal runs to the deckle */
    const boardCentre = { x: (bd.x + bd.w / 2) * 100, y: (bd.y + bd.h / 2) * 100 };
    /* the punch (E22 addendum 6) crops the page to 1/PUNCH_SCALE around the board centre: title, source and the
       chart box are placed inside that region from the first frame so nothing written is ever cut off */
    const ps = PORTRAIT ? 1 : LP.PUNCH_SCALE;   /* no punch in portrait (P41): the whole frame is the visible region */
    const vis = { x: bd.x + bd.w / 2 - 0.5 / ps, y: bd.y + bd.h / 2 - 0.5 / ps, w: 1 / ps, h: 1 / ps };
    const boxCss = (el) => { el.style.left = (bd.x * 100).toFixed(2) + "%"; el.style.top = (bd.y * 100).toFixed(2) + "%"; el.style.width = (bd.w * 100).toFixed(2) + "%"; el.style.height = (bd.h * 100).toFixed(2) + "%"; };
    const grain = lpEl("svg", "lp-grain", page, { width: "100%", height: "100%" });
    grain.innerHTML = '<filter id="lpg' + seed + '"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" stitchTiles="stitch"/>'
      + '<feColorMatrix values="0 0 0 0 .15 0 0 0 0 .13 0 0 0 0 .10 0 0 0 .35 0"/></filter><rect width="100%" height="100%" filter="url(#lpg' + seed + ')"/>';
    const edge = lpEl("div", "lp-edge", page);
    /* the field: SOAK (feathered seeps spreading and saturating, never contracting) or
       SCRIBBLE (seeded strokes drawn one at a time, nib at the front); the crisp rect
       resolves under either so the ink ends at a definite edge. Clipped by .lp-field. */
    const field = lpEl("div", "lp-field", page);
    boxCss(field);
    /* the field's own pixel box: 1690x907 is the landscape board (s9.26); portrait takes the board's stage-px size so the
       seeps stay round and the strokes run the page's width (fk scales the seeded jitter and radii with it) */
    const fw = PORTRAIT ? Math.round(bd.w * STAGE_W) : 1690, fh = PORTRAIT ? Math.round(bd.h * STAGE_H) : 907, fk = PORTRAIT ? Math.max(fw, fh) / 1690 : 1;
    const fsvg = lpEl("svg", "", field, { viewBox: "0 0 " + fw + " " + fh, preserveAspectRatio: "none" });
    /* the soak's edge (operator, 2026-09-05: "splotchy, expanding, staining to cover the canvas, like coffee staining into
       the page - not round"): seeded noise displaces every stain's outline, then a soft blur wets it */
    /* K-M INK (44 s44.1, P43 T3, kinetics.km_ink): the stains are drawn WHITE and add their coverage (plus-lighter); after the
       displacement and blur the filter moves that coverage into the colour channels and maps it through the Kubelka-Munk
       curve of charcoal over cream (kmFilterMarkup) - overlaps deepen instead of greying, and one full stain IS the ink */
    /* ... and ERRATIC (operator, 2026-09-05, "a mesh with some spots having higher attraction than others"): under km_ink the
       stains are soft radial coverage growing through the paper's attraction field (soakFilterMarkup) - fingers, islands
       ahead of the front, dry holes that fill late, everything deepening by K-M where it overlaps */
    fsvg.innerHTML = kin("km_ink")
      ? '<defs>' + soakGradientMarkup("lpsoakgr" + seed) + '<filter id="lpsoak' + seed + '" x="-25%" y="-25%" width="150%" height="150%" color-interpolation-filters="sRGB">'
        + soakFilterMarkup(seed, fk, "#F4E6C7", "#25313C") + '</filter></defs>'
      : '<defs><filter id="lpsoak' + seed + '" x="-25%" y="-25%" width="150%" height="150%">'
        + '<feTurbulence type="fractalNoise" baseFrequency="0.006 0.009" numOctaves="3" seed="' + (seed & 255) + '" result="n"/>'
        + '<feDisplacementMap in="SourceGraphic" in2="n" scale="' + Math.round(110 * fk) + '" xChannelSelector="R" yChannelSelector="G"/>'
        + '<feGaussianBlur stdDeviation="12"/></filter></defs>';
    const mode = pg.field === "scribble" ? "scribble" : "soak";
    /* the moving fields (soakAnim): the feOffsets and the displacement the paint loop drives while the soak runs */
    const soakFx = kin("km_ink") && mode === "soak" ? (() => { const ids = soakAnimIds(seed), q = (id) => fsvg.querySelector("#" + id);   /* mesh off: only the wobble and its depth exist */
      return { wob: q(ids.wob), att: q(ids.att), grain: q(ids.grain), disp: q(ids.disp) }; })() : null;
    const goo = lpEl("g", "", fsvg, mode === "soak" ? { filter: "url(#lpsoak" + seed + ")" } : {});
    const blobs = [], strokes = [];
    if (mode === "soak") {
      for (let i = 0; i < LP.SEEPS; i++) {
        const col = i % 3, row = Math.floor(i / 3);
        const cx = (PORTRAIT ? fw / 6 + col * fw / 3 : 282 + col * 563) + (lpHash(seed, i, 1) - 0.5) * 300 * fk;
        const cy = (PORTRAIT ? fh / 6 + row * fh / 3 : 150 + row * 303) + (lpHash(seed, i, 2) - 0.5) * 160 * fk;
        /* a STAIN, not a circle: a seeded lumpy outline of unit radius (16 lobes, radii 0.55..1.15) scaled up by t */
        const N = 16, P = [];
        for (let k = 0; k < N; k++) { const a = k / N * Math.PI * 2, r = 0.55 + 0.6 * lpHash(seed, i * 64 + k, 8); P.push([Math.cos(a) * r, Math.sin(a) * r]); }
        /* a smooth closed outline through the lobes (Catmull-Rom -> cubic), so the stain has no corners before the noise takes it */
        let d = "M" + P[0][0].toFixed(3) + " " + P[0][1].toFixed(3);
        for (let k = 0; k < N; k++) {
          const p0 = P[(k - 1 + N) % N], p1 = P[k], p2 = P[(k + 1) % N], p3 = P[(k + 2) % N];
          d += " C" + (p1[0] + (p2[0] - p0[0]) / 6).toFixed(3) + " " + (p1[1] + (p2[1] - p0[1]) / 6).toFixed(3) + " " + (p2[0] - (p3[0] - p1[0]) / 6).toFixed(3) + " " + (p2[1] - (p3[1] - p1[1]) / 6).toFixed(3) + " " + p2[0].toFixed(3) + " " + p2[1].toFixed(3);
        }
        const c = lpEl("path", "", goo, Object.assign({ d: d + " Z", fill: "#25313C", transform: "translate(" + cx.toFixed(1) + " " + cy.toFixed(1) + ") scale(0)" },
                                                    kin("km_ink") ? { fill: SOAK.MESH ? "url(#lpsoakgr" + seed + ")" : "#fff", style: "mix-blend-mode:plus-lighter" } : {}));
        blobs.push({ c, cx, cy, R: (620 + lpHash(seed, i, 4) * 420) * fk, lag: lpHash(seed, i, 5) * 0.35, i });
      }
    } else {
      for (let r = 0; r < LP.STROKES; r++) {
        const y = 40 + (fh - 80) * r / (LP.STROKES - 1), pts = [];
        for (let k = 0; k < 9; k++) {
          const u = k / 8, x = 60 + (fw - 120) * (r % 2 ? 1 - u : u) + (lpHash(seed, r * 9 + k, 6) - 0.5) * 40;
          pts.push([x, y + (lpHash(seed, r * 9 + k, 7) - 0.5) * 44]);
        }
        const d = pts.map(([x, yy], k) => (k ? "L" : "M") + x.toFixed(1) + " " + yy.toFixed(1)).join(" ");
        const p = lpEl("path", "", goo, { d, stroke: "#25313C", "stroke-width": Math.round(76 * fk), "stroke-linecap": "round", "stroke-linejoin": "round", fill: "none" });
        const len = p.getTotalLength ? p.getTotalLength() : 1700;
        p.setAttribute("stroke-dasharray", len); p.setAttribute("stroke-dashoffset", len);
        strokes.push({ p, len });
      }
    }
    const nib = lpEl("circle", "", fsvg, { r: 9, fill: "#25313C", opacity: 0 });
    const rect = lpEl("rect", "", fsvg, { x: 0, y: 0, width: fw, height: fh, fill: "#25313C", opacity: 0 });
    /* TWO-PLATE path (operator, 2026-09-03: "have GPT generate a cream plate and a charcoal-filled cream plate,
       then fade the charcoal plate in over the top, then draw the line"): page.field_plate names the inked
       plate; it cross-fades over the cream page in beat 3 and the procedural field stays hidden. */
    const fieldPlate = pg.field_plate && A[pg.field_plate] ? lpEl("div", "lp-fieldplate", page) : null;
    if (fieldPlate) { fieldPlate.style.backgroundImage = 'url("' + A[pg.field_plate] + '")'; field.style.display = "none"; }
    const title = lpEl("div", "lp-ink lp-title", page);
    const subEl = lpEl("div", "lp-ink lp-sub", page);
    const src = lpEl("div", "lp-ink lp-src" + (pg.src_style === "compact" ? " compact" : ""), page);   /* the design pass: a citation takes minimal space */
    const subText = PORTRAIT ? lpFirstClause(pg.sub || "", true) : (pg.sub || ""), srcText = PORTRAIT ? lpFirstClause(pg.source || "", false) : (pg.source || "");
    const glyphs = PORTRAIT
      ? [...lpGlyphsWrap(title, pg.title || "", seed), ...lpGlyphsWrap(subEl, subText, seed + 2), ...lpGlyphsWrap(src, srcText, seed + 1)]
      : [...lpGlyphs(title, pg.title || "", seed), ...lpGlyphsWrap(subEl, subText, seed + 2), ...lpGlyphs(src, srcText, seed + 1)];
    /* chart area inside the field, leaving the declared quiet zone for docks (s9.28 B3/C2) */
    const qz = pg.quiet_zone || null;
    const chart = lpEl("svg", "lp-chart", page, { viewBox: "0 0 1000 560" });
    /* the badge rail: ALWAYS a row grouped under the chart and its source (operator, 2026-09-03: the quiet zone is the
       caption's; a badge that keys a line is that line's dynamic label instead - see buildLedgerLine) */
    const rail = lpEl("div", "lp-rail", page);
    const badges = (pg.badges || []).filter((bd) => !bd.inline).map((bd, bi) => {
      const el = lpEl("div", "pill lp-pill", rail);
      el.innerHTML = '<span class="pill-label">' + bd.label + '</span><span class="pill-row">' +
        '<span class="pill-num" style="color:' + (ACCENT[bd.accent] || "var(--sunflower)") + '">' + bd.value + '</span>' +
        '<span class="pill-tag" style="color:' + (ACCENT[bd.accent] || "var(--sunflower)") + '">' + bd.tag + '</span></span>';
      return { el, at: LP_BADGE0 + LP_BADGE_STEP * bi };
    });
    let geom = { W: 1000, H: 560 };
    if (PORTRAIT) {
      geom = lpPortraitLayout({ title, subEl, src, chart, rail });
    } else {
      title.style.left = (Math.max(bd.x + 0.027, vis.x + 0.03) * 100).toFixed(2) + "%"; title.style.top = (Math.max(bd.y + 0.024, vis.y + 0.035) * 100).toFixed(2) + "%";
      subEl.style.left = title.style.left; subEl.style.top = (parseFloat(title.style.top) + 5.6).toFixed(2) + "%";
      src.style.left = (Math.max(0.06, vis.x + 0.03) * 100).toFixed(2) + "%";
      /* the chart box lives inside the punched region (with room for the title above and the source below) */
      /* the chart box is the BOARD clipped to the punched region (a host plate's board is only part of the page) */
      const reg = pg.punch === false ? bd : { x: Math.max(bd.x, vis.x), y: Math.max(bd.y, vis.y), w: Math.min(bd.x + bd.w, vis.x + vis.w) - Math.max(bd.x, vis.x), h: Math.min(bd.y + bd.h, vis.y + vis.h) - Math.max(bd.y, vis.y) };
      /* a host plate may declare the chart box outright (page.chart_box, measured clear of the host's hand) */
      const cb = pg.chart_box ? { x: pg.chart_box.x + 0.02 * pg.chart_box.w, y: pg.chart_box.y + 0.15 * pg.chart_box.h, w: 0.96 * pg.chart_box.w, h: 0.74 * pg.chart_box.h }
                              : { x: reg.x + 0.03 * reg.w, y: reg.y + 0.15 * reg.h, w: 0.94 * reg.w, h: 0.74 * reg.h };
      /* a page whose captions are pinned to the anchor (a host plate, C5) keeps its chart and source above the
         caption band: the chart ends at 79% of the frame so the source line under it never meets a caption */
      if (pg.caption === "anchor") cb.h = Math.max(0.2, Math.min(cb.h, 0.79 - cb.y));
      chart.style.width = ((qz ? 0.6 : 0.9) * cb.w * 100).toFixed(2) + "%"; chart.style.height = (cb.h * 100).toFixed(2) + "%";
      chart.style.left = ((cb.x + (qz === "left" ? 0.4 : 0.05) * cb.w) * 100).toFixed(2) + "%"; chart.style.top = (cb.y * 100).toFixed(2) + "%";
      /* the sub wraps inside the chart's width; the source writes directly under the chart box (never in the caption band) */
      subEl.style.width = chart.style.width; subEl.style.left = chart.style.left;
      src.style.top = ((cb.y + cb.h) * 100 + 1.2).toFixed(2) + "%"; src.style.left = chart.style.left;
      rail.style.left = chart.style.left; rail.style.top = ((cb.y + cb.h) * 100 + 4.4).toFixed(2) + "%"; rail.style.maxWidth = chart.style.width;
    }
    const inlineBadges = {}; (pg.badges || []).forEach((bd) => { if (bd.inline) inlineBadges[LP_BADGE_COL[bd.accent]] = bd; });
    const st = { root, page, edge, blobs, strokes, nib, rect, goo, soakFx, soakFk: fk, seed, glyphs, chart, fieldPlate, boardCentre, badges, inlineBadges, field, rail, inkEls: [title, subEl, src], kind: pg.builder || "story",
                 bars: [], paths: [], labels: [], callout: null, cval: null, vals: pg.values || [],
                 vstr: pg.value_strings || [], emph: Number.isInteger(pg.emphasize) ? pg.emphasize : -1,
                 marks: [], markBy: {}, geom, portrait: PORTRAIT, linePts: [], titleEl: title, titleGlyphs: [...title.querySelectorAll(".g")], rtGlyphs: [], perform: null };   /* geom: the chart's drawing box (viewBox units); linePts: each series' points in it, for exact datum targets */   /* no emphasis declared = no datum styled (spec emits null) */
    st.subGlyphs = [...subEl.querySelectorAll(".g")]; st.srcGlyphs = [...src.querySelectorAll(".g")];   /* P48 T4: a recast erases the words that described the chart that left */
    lpMark(st, "title", "title", title, {}); lpMark(st, "sub", "sub", subEl, {}); lpMark(st, "src", "src", src, {});   /* P48 T1: the page's own ink is a mark too - a retitle and a recast both move it */
    /* one builder per treatment (s9.28; P35 Builder Architecture) - each harvested from its own component, never merged */
    const builders = { "dense-line": buildLedgerLine, race: buildLedgerRace, decline: buildLedgerDecline, combo: buildLedgerCombo, share: buildLedgerShare,
                       tiers: buildLedgerTiers, treemap: buildLedgerTreemap };   /* P50 T9 / T6 */
    (builders[st.kind] || buildLedgerBars)(st, pg);
    /* A page may declare its own BUILD length (operator, 2026-09-08: "the fix is to draw out the charts in a
       slower/more animated fashion"). Measured on the tariff short, M21 puts the deployed lives at 0.0-6.1 s
       against a 10-13 s span - the chart is not being HELD too long, it finishes drawing early and then waits.
       Spending more of the span on the draw is motion where there was a wait. Opt-in: a page that declares
       nothing keeps LP.BUILD, so no existing frame moves. Builders with their own envelope (race, decline,
       combo, share) already set buildDur and are left alone. */
    if (Number.isFinite(+pg.build_s) && +pg.build_s > 0 && !st.buildDur) st.buildDur = +pg.build_s;
    /* P48 T4: the OTHER charts this page can become (`;then=<series>:<variant>` on the plate id). Each gets its own
       <svg> in the same box, hidden until a chart_to reaches it; the deckle, the title, the badges and the rail are
       shared, because it is the same page. Built at load - nothing is constructed per frame. */
    st.states = [st];
    for (const pg2 of (scene.world.page_states || []).slice(0, LP_STATE_MAX - 1)) {
      const ch2 = lpEl("svg", "lp-chart", page, { viewBox: chart.getAttribute("viewBox") });
      ch2.style.cssText = chart.style.cssText; ch2.style.opacity = 0;
      const s2 = { root, page, chart: ch2, geom, portrait: PORTRAIT, seed, edge, field, rail,
                   bars: [], paths: [], labels: [], callout: null, cval: null, inlineBadges: {}, linePts: [],
                   marks: [], markBy: {}, badges: [], inkEls: [],
                   vals: pg2.values || [], vstr: pg2.value_strings || [],
                   emph: Number.isInteger(pg2.emphasize) ? pg2.emphasize : -1, kind: pg2.builder || "story",
                   windowOffsets: pg2.window_offsets || null };   /* P48 T2: a derived (windowed) state maps the page's datum indices */
      (builders[s2.kind] || buildLedgerBars)(s2, pg2);
      /* ... and its own SUB and SOURCE. A caption that goes on describing the chart that left is a lie on the page, so a
         recast rewrites them with the same hand that rewrites the title: the old run erases glyph by glyph, the new one
         writes. They sit exactly where the page's own sit, and carry nothing until the recast reaches them. */
      const mkInk = (cls, from, text) => {
        const d = lpEl("div", cls, page);
        if (from.getAttribute("style")) d.setAttribute("style", from.getAttribute("style"));
        const gs = PORTRAIT ? lpGlyphsWrap(d, text, seed + 60 + st.states.length) : lpGlyphs(d, text, seed + 60 + st.states.length);
        for (const g of gs) g.style.setProperty("--w", "0");
        return { div: d, glyphs: gs };
      };
      s2.subInk = mkInk("lp-ink lp-sub", subEl, PORTRAIT ? lpFirstClause(pg2.sub || "", true) : (pg2.sub || ""));
      s2.srcInk = mkInk("lp-ink lp-src" + (pg2.src_style === "compact" ? " compact" : ""), src,
                        PORTRAIT ? lpFirstClause(pg2.source || "", false) : (pg2.source || ""));
      st.states.push(s2);
    }
    /* keyed per world element: the wipe paints the same scene into wA and wB */
    ledgerState.set(el.id + "|" + scene.scene_id, st);
    el.__lp = st;   /* resolveTarget reads the active page's points from its world element */
    return st;
  };
  const buildLedgerBars = (st, pg) => {
    /* E28 (operator, 2026-09-03): a chart reads right at a glance - a drop is a bar going DOWN from a
       zero baseline. Values are SIGNED; the baseline sits at zero wherever the range puts it, bars hang
       below it for negatives, value labels ride the bar's far end, category labels stay along the bottom. */
    const n = Math.max(1, st.vals.length);
    const lo0 = Math.min(0, ...st.vals), hi0 = Math.max(0, ...st.vals);
    /* THE BREAKTHROUGH (2026-09-10): a bars page may STATE its scale (`axes.domain`) that one value cannot fit. That bar builds
       to the COMPARATOR's level (the tallest honest bar) with the others, holds, then runs by one of two mechanics (LPX.BT_*):
         burst (Bravos 8:02): it shoots to its true height WHILE the scale rewrites to the nice ceiling above it - the honest
               bar shrinks to a sliver, the old ticks slide and fade, the new ones fade in, an overshoot settles, the bar glows;
         stack (the operator): the scale HOLDS and the bar grows in comparator-sized steps until its true number - out of the
               plot, through the title, off the page (the page clips it), the top gridline snapping as it passes.
       The scale is printed and the value is printed at every instant, so nothing is a lie (E28/E53). */
    const dom = Array.isArray((pg.axes || {}).domain) && (pg.axes.domain.length === 2) ? pg.axes.domain.map(Number) : null;
    const ovf = (pg.axes || {}).overflow, btMode = (ovf === "burst" || ovf === "break") ? "burst" : ovf === "stack" ? "stack" : null;
    const brk = !!btMode && !!dom;
    /* P50 T10 / T13 - THE BURST'S FURNITURE (Bravos 8:01.8-8:03.2), every piece OFF unless the object names it, so a
       page that names none builds byte-identically: `overflow_placeholder` (a grey track of the comparator's height behind the
       bar and the mark in the number's place until the number is SPOKEN), `overflow_capsule: "axis"` (the value
       capsule mounted on the axis under the bar's end with a dotted leader, in place of the pill riding the tip),
       `break_cadence: "stop"` (the operator's blend, E60: the shoot stepped on stopaction's cadence rule). */
    const bfx = pg.axes || {};
    const phMark = !btMode ? null : bfx.overflow_placeholder === true ? BREAK.PH_TEXT
      : (typeof bfx.overflow_placeholder === "string" && bfx.overflow_placeholder.trim()) ? bfx.overflow_placeholder.trim() : null;
    const capAxis = !!btMode && bfx.overflow_capsule === "axis";
    const stopCad = !!btMode && bfx.break_cadence === "stop";
    const pad = Math.max(1e-9, (hi0 - lo0) * 0.14);
    const lo = dom ? Math.min(dom[0], lo0) : lo0 - (lo0 < 0 ? pad : 0), hi = dom ? dom[1] : hi0 + (hi0 > 0 ? pad : 0);
    const G = st.geom || { W: 1000, H: 560 }, P = !!st.portrait;   /* portrait (P41): stage px, 40px labels below, 59px values and pill above */
    const bottom = P ? G.H - 70 : 440, top = P ? 150 : 90, x0 = P ? 150 : 60, x1 = P ? G.W - 30 : 980, gap = 0.34, unit = pg.unit || "";
    const my = (v) => bottom - (v - lo) / (hi - lo || 1) * (bottom - top);
    const base = my(0);
    st.scale = { kind: "bars", my, yv: (v) => v, y0: lo, y1: hi, x0, x1 };   /* P48 T2 */
    const bw = (x1 - x0) / n * (1 - gap);
    /* both axes, always (operator, 2026-09-03): y ticks with the unit from the shared helper, the zero line as the axis */
    /* six divisions, not the default five: lpNiceStep's 1-2-5 ladder rounds 21.8 up to 50, which left the tariff
       short's monthly page with only two tick labels ($0 and -$50) and NO reference above zero for its one
       positive bar. Asking for six lands step 20 and five labelled ticks. */
    const ticks0 = lpYTicks(st, lo, hi, my, x0 - 20, x1 + 20, unit, x0 - 26, 6);
    /* the comparator: the tallest bar the stated scale holds - the breaking bar first stands at ITS level, a bar like the others */
    const honest = st.vals.filter((v) => !(brk && v > hi)), comp = honest.length ? Math.max(...honest) : hi;
    st.vals.forEach((v, i) => {
      const over = brk && v > hi, x = x0 + (x1 - x0) / n * (i + gap / 2), yv = my(over ? comp : v), neg = v < 0;
      const h = Math.max(3, Math.abs(yv - base)), y = neg ? base : base - h;
      /* P50 T10: the placeholder's TRACK is laid in BEFORE the bar, so the bar grows in front of it. It is exactly
         the height the bar builds to - the comparator's level - because it is furniture, not data (E28: no frame of
         the page may show a scale the page did not state). */
      let track = null, stamp = null;
      if (over && phMark) { const T = breakTrack(x, bw, base, my(comp)), S = breakStamp(T, P ? 22 : 14);
        track = lpEl("rect", "btrack", st.chart, { x: T.x.toFixed(1), y: T.y.toFixed(1), width: T.w.toFixed(1),
          height: T.h.toFixed(1), rx: 6, fill: "var(--lp-chalk)", opacity: 0 });
        /* the MARK stands where the number will - the track alone is covered by the bar it stands behind */
        stamp = lpText(st.chart, "val bstamp", S.x, S.y, "middle", phMark, { opacity: 0, style: "fill:var(--lp-chalk)" }); }
      const bar = lpEl("rect", "bar" + (neg ? " neg" : " pos") + (i === st.emph ? " emph" : ""), st.chart,
        { x: x.toFixed(1), y: y.toFixed(1), width: bw.toFixed(1), height: h.toFixed(1), rx: 6 });   /* grows from the zero baseline, up or down */
      /* E53 s7: a DECLARED colour outranks the sign default. Without this the builder read only the value's sign,
         so a page of COSTS came out green - three duty bills and a tariff receipt on the tariff short, all reading
         as good news because the numbers were positive. A rise is not always a gain. The stylesheet beats a
         presentation attribute, so the declared fill goes through style. */
      const dcol = LP_PAL[(pg.colors || [])[i]];
      if (dcol) bar.style.fill = dcol;
      bar.style.transformOrigin = "0 " + base.toFixed(1) + "px"; bar.style.transform = "scaleY(0)";
      const lab = lpEl("text", "lab", st.chart, { x: (x + bw / 2).toFixed(1), y: bottom + (P ? 52 : 34), "text-anchor": "middle", opacity: 0 });
      lab.textContent = (pg.labels || [])[i] || "";
      const vy = neg ? base + h + (P ? 62 : 26) : base - h - (P ? 22 : 14);
      const val = lpEl("text", "val", st.chart, { x: (x + bw / 2).toFixed(1), y: vy.toFixed(1), "text-anchor": "middle", opacity: 0 });
      val.textContent = lpWithUnit(st.vstr[i] != null ? String(st.vstr[i]) : lpFmt(v), unit);
      const rec = { bar, lab, val, h, x: x + bw / 2, i, neg, end: neg ? base + h : base - h, over, v, bx: x, bw, track, stamp };
      if (over && btMode === "stack") {   /* the top gridline SNAPS as the bar passes: its two broken ends kick up beside the bar */
        const mk = (ax, bx2) => lpEl("line", "grid snap", st.chart, { x1: ax.toFixed(1), y1: top.toFixed(1), x2: bx2.toFixed(1), y2: (top - 16).toFixed(1), stroke: "var(--lp-chalk)", "stroke-width": 3, "stroke-linecap": "round", opacity: 0 });
        rec.snap = [mk(x - 4, x - 24), mk(x + bw + 4, x + bw + 24)];
      }
      st.bars.push(rec);
      lpMark(st, "b:" + i, "bar", bar, { x, y, w: bw, h, base, cx: x + bw / 2, end: rec.end, neg, v }, rec);
      lpMark(st, "xlab:" + i, "xlabel", lab, { x: x + bw / 2, y: bottom + (P ? 52 : 34) });
      lpMark(st, "val:b:" + i, "value", val, { x: x + bw / 2, y: vy, v });
    });
    if (brk && st.bars.some((b) => b.over)) {
      const vmax = Math.max(...st.vals), niceCeil = (v) => { const s = lpNiceStep(v / 4); return Math.ceil(v / s - 1e-9) * s; };
      const hi1 = btMode === "burst" ? niceCeil(vmax) : hi, my1 = (v) => bottom - (v - lo) / (hi1 - lo || 1) * (bottom - top);
      const step0 = lpNiceStep(Math.max(1e-9, (hi - lo) / 6)), vals0 = [];
      for (let tv = Math.ceil(lo / step0 - 1e-9) * step0; tv <= hi + 1e-9; tv += step0) vals0.push(Math.abs(tv) < step0 * 1e-6 ? 0 : tv);
      const ticks1 = [];
      if (btMode === "burst") {   /* the scale the number needs, built now and hidden: it fades in as the old one slides away */
        const step1 = lpNiceStep(Math.max(1e-9, (hi1 - lo) / 5));
        for (let tv = Math.ceil(lo / step1 - 1e-9) * step1; tv <= hi1 + 1e-9; tv += step1) {
          const v = Math.abs(tv) < step1 * 1e-6 ? 0 : tv, y = my1(v);
          if (v === 0) continue;   /* the zero line is the axis, shared */
          ticks1.push(lpEl("line", "grid", st.chart, { x1: x0 - 20, x2: x1 + 20, y1: y.toFixed(1), y2: y.toFixed(1), opacity: 0 }));
          ticks1.push(lpText(st.chart, "lab", x0 - 26, y + (P ? 14 : 8), "end", lpWithUnit(lpTick(v), unit), { opacity: 0 }));
        }
      }
      st.bt = { mode: btMode, hi0: hi, hi1, lo, top, bottom, base, plot: bottom - top, comp, ticks0, vals0, ticks1,
        /* P50 T10 / T13 - all three null unless the object asked. `cad` is the cadence the burst's OWN SPEED asks for
           (species/breakthrough.mjs reads stopaction's rule on the tip's travel over BT_RUN); null is the continuous
           burst, unchanged to the bit. */
        ph: phMark ? { text: phMark, track: (st.bars.find((b) => b.over) || {}).track || null,
                       stamp: (st.bars.find((b) => b.over) || {}).stamp || null } : null, cap: null,
        cad: (btMode === "burst" && stopCad) ? burstCadence(bottom - top, lo, hi, hi1, comp, vmax, LPX.BT_RUN) : null };
      st.btBase = (Number.isFinite(+pg.build_s) && +pg.build_s > 0) ? +pg.build_s : LP.BUILD;   /* the ordinary build's own length (a page may declare build_s) */
      st.buildDur = st.btBase + LPX.BT_HOLD + (btMode === "burst" ? LPX.BT_RUN + LPX.BT_SETTLE : LPX.BT_STEP_S * (Math.ceil(vmax / comp - 1e-9) + 1));
      st.chart.style.overflow = "visible";   /* the stack leaves the plot; the page's edge is what clips it */
      if (btMode === "stack") [st.titleEl, st.page.querySelector(".lp-sub"), st.page.querySelector(".lp-src")].forEach((el) => {   /* the bar runs BEHIND the words: the claim stays legible */
        if (el) { el.style.position = "relative"; el.style.zIndex = 3; } });
    }
    /* COMPARATOR RULE on a bars page (operator, 2026-09-08: "it needs some type of comparator line"). The line page
       has had `axes.hlines` since the fifth watch; a bars page needs it more, because a comparison between two bars
       is exactly where a viewer is asked to subtract. The rule is drawn across the plot at its value and named at
       its right end, so the gap between it and a taller bar IS the argument (E53 s6). */
    const HLB = ((pg.axes || {}).hlines || []).filter((h) => h && Number.isFinite(+h.y));
    st.hlines = HLB.map((h, hi) => {
      const col = LP_PAL[h.color] || h.color || "#8fb3f0", hy = my(+h.y);
      const line = lpEl("line", "hrule", st.chart, { x1: x0, x2: x1, y1: hy.toFixed(1), y2: hy.toFixed(1), stroke: col });
      const lab = h.label ? lpText(st.chart, "sname", x1, hy - (P ? 16 : 10), "end", String(h.label),
        { opacity: 0, style: LP_HALO + "fill:" + col + (P ? ";font-size:34px" : "") }) : null;
      lpMark(st, "rule:" + hi, "rule", line, { y: hy, v: +h.y, x1: x0, x2: x1 });
      return { h, y: hy, line, lab, col };
    });
    const e = st.bars[Math.min(st.emph, st.bars.length - 1)];
    if (e) {
      const cg = lpEl("g", "", st.chart, { opacity: 0 });
      let CP = P ? { w: 160, h: 84, ty: 61, up: 128, dn: 40, rx: 14 } : { w: 128, h: 42, ty: 30, up: 66, dn: 24, rx: 8 };   /* portrait pill: 59px type, narrower than a bar pitch so the neighbours' values stay clear */
      /* the pill sits past the bar's far end - but NEVER in the x-label band. A negative bar that reaches the
         plot floor put its own pill straight over its own month name (measured on the tariff short: the pill at
         y 424-508, "May" at 429-473, fully buried). If there is no room below, the pill flips ABOVE the zero
         line at the same x, where a negative bar leaves the plot empty. s9.23b: a label never overprints. */
      const labTop = bottom + (P ? 52 : 34) - (P ? 40 : 26);   /* the top of the month-label row */
      let py = e.neg ? e.end + CP.dn : e.end - CP.up;
      if (e.neg && py + CP.h > labTop) {
        /* The bar reaches the plot floor, so there is no room past its end. Above the zero line is not free either:
           the y-rescale puts a small positive bar's own value up there. So the pill goes INSIDE its own bar - the
           emphasised bar is the tallest mark on the page and sunflower on crimson is unmistakable - and any
           NEIGHBOUR's value that it clips slides sideways to make room. The callout owns its position; the labels
           around it yield. (Measured on the tariff short: -$66.8 sat squarely over "May".) */
        const barH = Math.abs(e.end - base);
        py = barH > CP.h * 1.3 ? base + (barH - CP.h) / 2 : Math.max(top, base - CP.up - CP.h * 0.15);
        const px0 = e.x - CP.w / 2, px1 = e.x + CP.w / 2;
        for (const o of st.bars) {
          if (o === e || !o.val) continue;
          const ox0 = o.x - CP.w / 2, ox1 = o.x + CP.w / 2;   /* a value is centred on its bar and is pill-wide at this type */
          const oy = o.neg ? o.end + (P ? 62 : 26) : o.end - (P ? 22 : 14);
          if (ox1 <= px0 || px1 <= ox0 || oy < py || oy > py + CP.h + (P ? 40 : 18)) continue;
          const push = (o.x > e.x ? px1 - ox0 : ox1 - px0) + 8;
          const nx = Math.max(x0 + CP.w / 2, Math.min(x1 + 20, o.x + (o.x > e.x ? push : -push)));
          o.val.setAttribute("x", nx.toFixed(1));
        }
      }
      /* a breaking bar's pill rides its tip (the paint moves it) - unless the page mounted the capsule ON THE AXIS
         (Bravos 8:02.6: a pink value capsule counts up on the axis under the bar's end, a dotted leader between them).
         The axis mount fits the band between the zero line and the bottom of the chart's box - box, baseline and type
         together - because the page's source line sits below that band and is not ours to move (E52). */
      let CAP = null;
      if (e.over && st.bt) {
        if (capAxis) { CAP = breakCapsuleFit(base, (st.geom || {}).H || bottom, CP); CP = { ...CP, h: CAP.h, ty: CAP.ty, rx: CAP.rx }; py = CAP.y; }
        else py = e.end - CP.up;
      }
      const pr = lpEl("rect", "cpill", cg, { x: (e.x - CP.w / 2).toFixed(1), y: py.toFixed(1), width: CP.w, height: CP.h, rx: CP.rx });
      const ct = lpEl("text", "callout", cg, { x: e.x.toFixed(1), y: (py + CP.ty).toFixed(1), "text-anchor": "middle" });
      /* the pill fits its number: a six-glyph value ("36.59%", the breakthrough page) overran the fixed width and lost its
         first digit at the edge (measured 2026-09-10). Measured on the final string; a page not yet laid out measures 0 and keeps the dial. */
      ct.textContent = e.val.textContent;
      if (CAP && CAP.k < 1) {   /* the type shrinks with the box, and BEFORE the fit below measures the number */
        const fs0 = parseFloat(getComputedStyle(ct).fontSize) || (P ? 59 : 30);
        ct.style.fontSize = (fs0 * CAP.k).toFixed(1) + "px";
      }
      const need = (ct.getComputedTextLength ? ct.getComputedTextLength() : 0) + (P ? 34 : 18);
      if (need > CP.w) { pr.setAttribute("x", (e.x - need / 2).toFixed(1)); pr.setAttribute("width", need.toFixed(1)); }
      if (e.over && st.bt && capAxis) {   /* the leader lives INSIDE the callout group, so it arrives and leaves with the capsule */
        const C = CAP, lx = breakLeaderX(e.bx, e.bw, x0), L = breakLeader(lx, e.end, C.y);
        const lead = lpEl("line", "blead", cg, { x1: lx.toFixed(1), x2: lx.toFixed(1),
          y1: (L ? L.y1 : C.y).toFixed(1), y2: (L ? L.y2 : C.y).toFixed(1), stroke: "var(--lp-acc)",
          "stroke-width": BREAK.CAP_LEAD_W, "stroke-linecap": "round", "stroke-dasharray": BREAK.CAP_LEAD_DASH, opacity: L ? 1 : 0 });
        /* the capsule TAKES the x-label's row, so the bar's own name is written just above the zero line inside its
           own column - the callout owns its place and the labels around it yield (s9.23b: a label never overprints) */
        e.lab.setAttribute("y", C.labY.toFixed(1));
        st.bt.cap = { lead, lx, y: C.y, h: CP.h };
      }
      e.val.setAttribute("opacity", 0); e.val.style.display = "none";
      st.callout = cg; st.cval = ct; st.cfinal = e.val.textContent; st.cnum = st.vals[e.i]; st.cunit = unit;
      if (e.over && st.bt) { st.cfinalTrue = e.val.textContent; st.cnum = st.bt.comp; st.cfinal = lpWithUnit(lpFmt(st.bt.comp), unit); st.cpill = pr; st.cp = CP; }
      lpMark(st, "callout", "callout", cg, { x: e.x, y: py });
    }
  };
  const buildLedgerLine = (st, pg) => {
    const ax = pg.axes || {}, series = pg.series || [];
    const PAL = { crimson: "#ED6A4A", teal: "#178C83", cobalt: "#8fb3f0", amber: "#F5B72E", deemph: "#b8c4d0" };
    const G = st.geom || { W: 1000, H: 560 }, P = !!st.portrait;   /* portrait (P41): stage px; no right margin for an inline name - it sits above the line's end */
    const L = P ? 150 : 70, R = P ? 70 : 220, T = P ? 90 : 40, B = P ? G.H - 80 : 470, W = G.W;
    const Y = (v) => ax.log ? Math.log10(v) : v;
    /* REFERENCE RULES (the fifth watch, 2026-09-07). A POLICY rate is a constant, not a series: drawn as a line it is a step,
       and a step at this scale reads as a fault. `axes.hlines: [{y, label, color}]` draws it as what it is - a labelled rule
       across the plot, in its own colour, named at its right end - and it takes part in the scale so the series never hides it. */
    const HL = (ax.hlines || (ax.hline ? [ax.hline] : [])).filter((h) => h && Number.isFinite(+h.y));
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    for (const s of series) for (const [x, v] of s.pts) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, Y(v)); y1 = Math.max(y1, Y(v)); }
    for (const h of HL) { y0 = Math.min(y0, Y(+h.y)); y1 = Math.max(y1, Y(+h.y)); }
    const pad = (y1 - y0) * 0.06 || 1; y0 -= pad; y1 += pad;
    if (ax.from_zero && !ax.log) y0 = 0;   /* E28 (operator, 2026-09-05): a truncated axis made a tenth look like a fall to nothing - the series declares its zero */
    /* P48 T2: a DERIVED rescale state names its exact domain - the y bounds (`axes.domain`) and the x window (`axes.xdomain`) -
       so a transition lands on a scale the page itself declared. Opt-in: a page naming neither draws exactly as it always has. */
    if (Array.isArray(ax.domain)) {
      if (ax.domain[0] !== null && ax.domain[0] !== undefined && Number.isFinite(+ax.domain[0])) y0 = Y(+ax.domain[0]);
      if (ax.domain[1] !== null && ax.domain[1] !== undefined && Number.isFinite(+ax.domain[1])) y1 = Y(+ax.domain[1]);
    }
    if (Array.isArray(ax.xdomain) && ax.xdomain.length === 2 && Number.isFinite(+ax.xdomain[0]) && Number.isFinite(+ax.xdomain[1])) { x0 = +ax.xdomain[0]; x1 = +ax.xdomain[1]; }
    const mx = (x) => L + (x - x0) / (x1 - x0 || 1) * (W - L - R), my = (v) => T + (1 - (Y(v) - y0) / (y1 - y0)) * (B - T);
    st.scale = { kind: "line", mx, my, yv: Y, x0, x1, y0, y1 };   /* P48 T2: the scale a rescale interpolates - both states keep theirs */
    /* P48 (operator, 2026-09-10, on the rescale's over-draw: "how do we prevent the over-draw during the transform? some type of
       pin-and-pivot"): the PLOT BOX is the pin. While a transition re-projects the standing line, the points that leave the target
       window are drawn on their way out - the history off the left, a falling tail below the axis, across the labels and off the
       page. A chart never draws outside its plot: this clip, padded by the stroke so a cap at the edge survives, is referenced by
       the series paths only while a rescale is on (lpPaintRescale) and dropped after (lpRestoreState), so nothing else moves. */
    { const defs = lpEl("defs", "", st.chart), cid = "plotclip-" + (st.seed | 0) + "-" + (++lpClipN);   /* deterministic: the build order names it, never a random */
      const cp = lpEl("clipPath", "", defs, { id: cid, clipPathUnits: "userSpaceOnUse" });
      lpEl("rect", "", cp, { x: (L - 14).toFixed(1), y: (T - 14).toFixed(1), width: (W - L - R + 28).toFixed(1), height: (B - T + 28).toFixed(1) });
      st.plotClip = cid; }
    st.axisB = B;   /* P47 T3: the morph closes its target along the axis */
    st.plot = { L, R, T, B, W, x0, x1, y0, y1, log: !!ax.log };   /* P48 T1: the scale a transition interpolates */
    lpMark(st, "axis", "axis", lpEl("line", "ax", st.chart, { x1: L, x2: W - R, y1: B, y2: B }), { x1: L, x2: W - R, y: B });
    st.hlines = HL.map((h, hix) => {
      const col = PAL[h.color] || h.color || "#8fb3f0", y = my(+h.y);
      const line = lpEl("line", "hrule", st.chart, { x1: L, x2: W - R, y1: y.toFixed(1), y2: y.toFixed(1), stroke: col });
      const lab = h.label ? lpText(st.chart, "sname", W - R, y - (P ? 18 : 12), "end", String(h.label), { opacity: 0, style: LP_HALO + "fill:" + col + (P ? ";font-size:34px" : "") }) : null;
      lpMark(st, "rule:" + hix, "rule", line, { y, v: +h.y, x1: L, x2: W - R });
      if (lab) lpMark(st, "rulelab:" + hix, "rulelabel", lab, { x: W - R, y: y - (P ? 18 : 12) });
      return { h, y, line, lab, col };
    });
    /* both axes, always (operator, 2026-09-03): y ticks - on a log axis at doublings of a power of ten, else the nice-step helper */
    if (ax.log) {
      const lo = Math.pow(10, y0), hi = Math.pow(10, y1); let tv = Math.pow(10, Math.floor(y0));
      let n = 0;
      while (tv <= hi) { if (tv >= lo) { const y = my(tv);
        lpMark(st, "tick:" + n, "tick", lpEl("line", "grid", st.chart, { x1: L, x2: W - R, y1: y.toFixed(1), y2: y.toFixed(1) }), { v: tv, y, x1: L, x2: W - R });
        lpMark(st, "ylab:" + n, "ylabel", lpText(st.chart, "lab", L - 10, y + 8, "end", lpTick(tv) + (ax.unit || "")), { v: tv, x: L - 10, y: y + 8 }); n++; } tv *= 2; }
    } else lpYTicks(st, y0, y1, my, L, W - R, ax.unit || "", L - 10);
    lpYLabel(st, pg, L, T - 12);
    (ax.xticks || []).forEach(([x, lab], i) => { const tx = lpEl("text", "lab", st.chart, { x: mx(x).toFixed(1), y: B + (P ? 52 : 32), "text-anchor": "middle" }); tx.textContent = lab;
      lpMark(st, "xtick:" + i, "xtick", tx, { v: x, x: mx(x), y: B + (P ? 52 : 32) }); });
    /* HIGHLIGHT (operator, 2026-09-05, the since-2000 holdings page): axes.highlight_from = an x; the points from there
       are the STORY'S window and take the sign colour, the history before it is drawn muted and thinner beneath - a
       26-year line that is up overall must not paint the last four months' selling green, nor the history red */
    const hfrom = Number.isFinite(+ax.highlight_from) && ax.highlight_from !== null && ax.highlight_from !== "" ? +ax.highlight_from : null;   /* the spec keeps tokens verbatim (strings) */
    const drawn = [];
    series.forEach((s, si) => {
      if (hfrom !== null && series.length === 1) {
        const k0 = Math.max(0, s.pts.findIndex(([x]) => +x >= hfrom) - 1);
        drawn.push({ ...s, pts: s.pts, muted: true, si, k0: 0 });
        drawn.push({ ...s, pts: s.pts.slice(k0), muted: false, si, k0 });
      } else drawn.push({ ...s, muted: false, si, k0: 0 });
    });
    drawn.forEach((s, i) => {
      const d = s.pts.map(([x, v], k) => (k ? "L" : "M") + mx(x).toFixed(1) + " " + my(v).toFixed(1)).join(" ");
      /* a single-metric line takes its SIGN colour (blood red down, green up); multi-line pages keep their series key */
      const endsDown = s.pts.length > 1 && +s.pts[s.pts.length - 1][1] < +s.pts[0][1];   /* numbers, never a string compare ('1116.7' < '325.8' is true) */
      /* the sign colour (a rise is green, a fall blood red) is the DEFAULT for a lone series, not a law over it: a series that
         declares its own colour keeps it. A COST that rises is not good news, and the page said so - the fifth watch. */
      const col = s.muted ? "rgba(184,196,208,.55)" : (PAL[s.color] || (series.length === 1 ? (endsDown ? "var(--lp-neg)" : "var(--lp-pos)") : PAL.deemph));
      const p = lpEl("path", "ser" + (s.muted ? " muted" : ""), st.chart, { d, stroke: col });
      const len = p.getTotalLength ? p.getTotalLength() : 2000;
      p.setAttribute("stroke-dasharray", len); p.setAttribute("stroke-dashoffset", len);
      const tip = lpEl("circle", "", st.chart, { r: 6, fill: col, opacity: 0 });
      const last = s.pts[s.pts.length - 1];
      const prev = s.pts.length > 1 ? s.pts[s.pts.length - 2] : last;   /* portrait: the name ends left of the last segment so a steep drop never runs through it */
      /* a line ending high takes its name in the empty lower right - but only when it is the ONLY line. With two, both would
         land in the same corner and stack onto the axis (the fourth watch); each is named at its own end instead. */
      /* ... and never when a reference RULE already owns the lower right for its own label (the fifth watch) */
      /* s9.23b / E53 s8: the name lives at the line's END - but anchored "end" it is written LEFTWARD, across
         whatever the line already drew. On the tariff short's holdings page that put "-9.9% Japan" straight over the
         muted history. Lift it clear of every point it would span. */
      const nameBelow = P && drawn.length === 1 && !HL.length && my(last[1]) < T + 0.35 * (B - T);
      /* OPT-IN (`axes.name_clear`): lifting the name changes where it sits on every page that already draws one,
         and the goldens are the contract - four moved when this was unconditional. A page asks for it. */
      const spanX = P ? 330 : 210, xEnd = mx(last[0]);
      let clearY = my(last[1]);
      if (ax.name_clear) for (const q of drawn) for (const [qx, qv] of q.pts) { const px2 = mx(qx);
        if (px2 >= xEnd - spanX && px2 <= xEnd) clearY = Math.min(clearY, my(qv)); }
      const name = lpEl("text", "sname", st.chart, P ? { x: (nameBelow ? W - R : Math.min(mx(last[0]), mx(prev[0])) - 8).toFixed(1), y: (nameBelow ? B - 28 : my(last[1]) - 30).toFixed(1), "text-anchor": "end", fill: col, opacity: 0 }
                                                     : { x: (mx(last[0]) + 12).toFixed(1), y: (my(last[1]) + 8).toFixed(1), fill: col, opacity: 0 });
      st.linePts.push(s.pts.map(([x, v]) => [mx(x), my(v)]));   /* the exact datum positions, for the species' targets */
      name.textContent = s.muted ? "" : (s.label ? s.label + " " : "") + (s.name || "");   /* the muted history carries no name */
      /* DYNAMIC LABEL: the badge that keys this line rides its inline name as the tag, in the accent - one
         reveal, one real estate (operator, 2026-09-03) */
      const ib = (st.inlineBadges || {})[s.color];
      if (ib && ib.tag) { const tg = lpEl("tspan", "tagchip", name, { dx: 12, fill: col }); tg.textContent = ib.tag; }
      const rec = { p, len, tip, name, stagger: i / Math.max(1, drawn.length), ny: nameBelow ? B - 28 : my(last[1]) + (P ? -30 : 8),
                     pts: s.pts.map(([x, v]) => [mx(x), my(v)]), si: s.si | 0, k0: s.k0 | 0, muted: !!s.muted,
                     data: s.pts.map(([x, v]) => [+x, +v]), d0: d, len0: len };   /* P47 T2: the path knows its data, so a build_to can cap it at a datum; P48 T2: and its DATA, so a rescale re-projects it */
      if (ax.name_clear && !nameBelow) rec.ny = Math.min(rec.ny, clearY - (P ? 34 : 20));
      st.paths.push(rec);
      lpMark(st, "s" + rec.si + (rec.muted ? ":h" : ""), "line", p, { pts: rec.pts, vals: s.pts.map(([, v]) => +v), len, k0: rec.k0, muted: rec.muted, col }, rec);
    });
    /* s9.23b inline names never overprint: push apart any two ends closer than one line */
    const order = [...st.paths].sort((a, b) => a.ny - b.ny), gap = P ? 50 : 28;   /* one line = the face's own size (44 px portrait), not the landscape 24 */
    for (let i = 1; i < order.length; i++)
      if (order[i].ny - order[i - 1].ny < gap) order[i].ny = order[i - 1].ny + gap;
    const over = order.length ? order[order.length - 1].ny - (B - 12) : 0;   /* a name never sits on the axis line: lift the group */
    if (over > 0) for (const pp of order) pp.ny -= over;
    for (const pp of order) { pp.name.setAttribute("y", pp.ny.toFixed(1));
      lpMark(st, "name:s" + pp.si + (pp.muted ? ":h" : ""), "name", pp.name, { x: +pp.name.getAttribute("x"), y: pp.ny }, pp); }   /* the name's geom is its SETTLED y, after the push-apart */
    /* P50 T11 / R26-34 - THE TIP-RIDING PILL, opt-in per page (`;pill=yes|<datum>` on the plate id). A drawing line
       says nothing until it stops; the pill is what it says while it is still being drawn, and at the end of the draw
       it settles onto the terminal tag's place and the TAG takes over (E53 s8 unchanged - one name, in one place).
       Built only when the page asks: a page without it carries not one extra element, which is what keeps every
       golden byte-identical. The math is species/tippill.mjs; this is its furniture. */
    if (pg.tip_pill) {
      const ms = pg.tip_pill === true ? null : (pg.tip_pill.milestone | 0);
      for (const pp of st.paths) {
        if (pp.muted || !pp.pts || pp.pts.length < 2 || !String(pp.name.textContent || "").trim()) continue;
        const col = pp.p.getAttribute("stroke"), anchor = pp.name.getAttribute("text-anchor") || "start";
        const g = lpEl("g", "lp-tippill", st.chart, { opacity: 0 });
        const lead = lpEl("line", "", g, { stroke: col, "stroke-width": 2, "stroke-linecap": "round", "stroke-dasharray": "6 6" });
        const box = lpEl("rect", "", g, { fill: "rgba(27,30,35,.90)", stroke: col, "stroke-width": 2 });
        /* a CLONE of the tag, so the pill says exactly what the tag will say - the badge chip's tspan and its gap
           included (a flat textContent ran the chip into the name: read off the first frame, 2026-09-11) */
        const tx = pp.name.cloneNode(true);
        tx.setAttribute("opacity", 1); tx.setAttribute("x", 0); tx.setAttribute("y", 0);
        g.appendChild(tx);
        /* the milestone is a DATUM of this path, in the path's own points (a highlighted tail starts at k0) */
        pp.pill = { g, lead, box, tx, anchor, span: null, fixed: false, bounds: [8, W - 8],
                    milestone: ms == null ? 0 : fracAtIndex(pp.pts, ms - (pp.k0 | 0)) };
      }
    }
  };
  /* ---- the other builders (P35 T5): race / decline / combo, each ported from ITS OWN hyperframes
     component (bar-chart-race, decline-chart, data-chart - mechanism only: no runtime, no gsap;
     the verbatim components sit in content/video_engine/hyperframes/compositions/components/).
     A builder sets st.paint (its build step, driven by c in 0..1 and the build clock in seconds)
     and st.buildDur (its own envelope; LP.BUILD stays the story/dense-line default). Everything is
     a pure function of t; the race bakes its ranks once from the data, never from the clock. */
  const LPX = {
    /* THE BREAKTHROUGH (2026-09-10) - a bars page that states a scale one value cannot fit. Both mechanics start at the
       COMPARATOR's level (the tallest honest bar) once the page has built, hold, then run - on the page's own build clock. */
    BT_HOLD: 0.5,        /* seconds the breaking bar stands at the comparator's level, a bar like the others, before it runs */
    BT_RUN: 0.6,         /* burst: the shoot + the rescale [DERIVED: Bravos 8:02.0-8:02.6, the SPR bar fills the frame in ~0.6 s] */
    BT_SETTLE: 0.3,      /* burst: the overshoot settles back [DERIVED: Bravos 8:02.4 -> 8:02.6] */
    BT_OVER: 0.05,       /* burst: the overshoot past the true height, as a share of it */
    BT_GLOW: 18,         /* burst: the bar's glow at the peak, px; it holds at half after [DERIVED: Bravos, the pink bloom] */
    BT_STEP_S: 0.06,     /* stack: seconds per comparator-sized step ("stacks each frame that same amount") */
    RACE_IN: 0.6,        /* bars grow into period 0 first: the page builds from empty, the component opens full */
    RACE_PERIOD: 1.2,    /* seconds per period (bar-chart-race defaults 2): a beat on the page, not a film */
    RACE_SWAP: 0.7,      /* fraction of a period one row swap takes when the crossing is mid-period, centred on it (operator: "smoother") */
    RACE_SWAP_MIN: 0.4,  /* a crossing near a period's end swaps over at least this much - narrower so it stays near the crossing */
    RACE_SETTLE: 0.01,   /* within this of a period (in period units) the exact value strings show; between, interpolations */
    RACE_TICKS: 14,      /* tick pool: the coarse set plus the finer set that fades out as the axis glides (never pops) */
    DECLINE_BUILD: 3.6, DECLINE_IN: 0.15, DECLINE_OUT: 0.08,   /* decline-chart: IN settles, HOLD draws + counts + darkens, OUT locks */
    COMBO_BUILD: 4.5, COMBO_BARS: 0.5, COMBO_LINE: 0.42,        /* data-chart: bars in reading order, then the line at one speed */
    COMBO_LABEL_SHARE: 0.55,   /* [DERIVED, the fourth watch]: a combo prints a bar's value only for the emphasised bar or one at this share of the biggest move */
    SHARE_BUILD: 3.2, SHARE_SWEEP: 0.78, SHARE_LABEL: 0.12,   /* [DERIVED, P48 T4] the pie's own envelope: the sweep takes most of it, each name writing as its slice completes */
    SHARE_PEEL_OUT: 0.17,   /* [DERIVED] how far the piece slides from the pie, as a share of the radius: clear of its neighbours, still obviously OF the circle */
    TIERS_BUILD: 4.5,       /* [DERIVED, P50 T9] N bands in turn: the combo's envelope, because it is the same amount of ink - a page that wants a band per WORD puts a build_to on each tier instead */
    TREEMAP_BUILD: 3.6,     /* [DERIVED, P50 T6] the mosaic lands in layout order over this; longer reads as a loading screen, shorter and the eye cannot follow the biggest cells arriving first */
  };
  const LP_PAL = { crimson: "#ED6A4A", teal: "#178C83", cobalt: "#8fb3f0", amber: "#F5B72E", deemph: "#b8c4d0" };   /* the field's own tokens (cobalt lifted for the charcoal, as dense-line) */
  const pow2out = (x) => 1 - (1 - x) * (1 - x);
  const smoothstep = (x) => x * x * (3 - 2 * x);
  const lpInvSmooth = (s) => 0.5 - Math.sin(Math.asin(1 - 2 * clamp01(s)) / 3);   /* smoothstep's inverse, closed form: the period fraction at which an eased value reaches s */
  const lpNiceStep = (x) => { const e = Math.pow(10, Math.floor(Math.log10(x))), f = x / e; return e * (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10); };
  const lpTick = (v) => String(Math.round(v * 100) / 100);
  const LP_HALO = "paint-order:stroke;stroke:#25313C;stroke-width:7px;stroke-linejoin:round;";   /* a field-coloured halo: a direct label stays legible where a line crosses it */
  /* ---- THE MARK MODEL (P48 T1) ------------------------------------------------------------------
     Every builder registers each thing it draws as a KEYED MARK: the ELEMENT it created and the GEOM
     (the numbers that placed it), under a key that is stable across chart states - `b:<i>` for the i-th
     bar datum, `s<si>` for a series' stroke (its geom.pts carrying datum `s<si>:<k>`), `r:<j>` for a race
     row, and a role name for furniture (axis, tick, ylabel, rule, xtick, name, value, src).
     A mark changes NOTHING about what is drawn - it is an index over geometry the builder already
     computed - and it is what a transition matches on (P48 T2-T5): shared keys tween, new keys enter by
     the stroke or spring law, dropped keys exit. Keys are unique per state; a collision would silently
     drop a mark, so one is disambiguated rather than overwritten. */
  let lpClipN = 0;   /* P48: plot clips, numbered in build order */
  const lpMark = (st, key, role, el, geom, rec) => {
    if (!st.marks) { st.marks = []; st.markBy = {}; }
    let k = key, n = 2; while (st.markBy[k]) k = key + "#" + n++;
    const m = { key: k, role, el, geom: geom || {}, rec: rec || null };
    st.marks.push(m); st.markBy[k] = m; return m;
  };
  /* a datum's position, from whichever mark owns it: its own mark (a bar) or its series' stroke (a line) */
  const lpMarkDatumOn = (S, si, i) => {   /* a datum's position on ONE chart state, by the PAGE's datum index */
    const off = (S.windowOffsets || [])[si] | 0, j = i - off;
    if (j < 0) return null;
    const B = S.markBy || {}, own = B["s" + si + ":" + j] || (si === 0 ? B["b:" + j] : null);
    if (own) return [own.geom.cx != null ? own.geom.cx : own.geom.x, own.geom.end != null ? own.geom.end : own.geom.y];
    const str = B["s" + si], hit = str && str.geom.pts ? str.geom.pts[j - (str.geom.k0 | 0)] : null;
    if (hit) return hit;
    const pts = (S.linePts || [])[si];   /* R26-28: a datum in the muted HISTORY of a highlighted line - the stroke mark carries the tail (k0 > 0); the state's own points carry every index */
    return pts && pts[j] ? pts[j] : null;
  };
  /* R26-28 (2026-09-10): a datum's position THIS FRAME - the active state's, LERPED from the leaving state to the arriving
     one while a rescale or extend moves the scale (the same eased clock the marks move on); null while either side lacks
     it. Brackets and spreads read their anchors here every frame, so they travel with the data instead of jumping at the
     switch, and hide while the data they measure is off the window. */
  const lpDatumNow = (st, si, i) => {
    const xf = st.xfNow;
    if (xf && !xf.keyed && !xf.morph && st.states) {
      const a = lpMarkDatumOn(st.states[xf.from], si, i), b = lpMarkDatumOn(st.states[xf.to], si, i);
      if (!a || !b) return null;
      const u = xf.extend ? segEase(clamp01(xf.u / XF_EXTEND.RESCALE)) : xf.u;
      return [xfLerp(a[0], b[0], u), xfLerp(a[1], b[1], u)];
    }
    return lpMarkDatum(st, si, i);
  };
  /* a series' points this frame, by the page's datum index: [{i, p}] in index order - the active state's, or the lerp of
     the two states across a rescale / extend for every index both carry */
  const lpPointsNow = (st, si) => {
    const idx = (S) => { const B = S.markBy || {}, str = B["s" + si]; if (!str || !str.geom.pts) return [];
      const off = (S.windowOffsets || [])[si] | 0, k0 = str.geom.k0 | 0; return str.geom.pts.map((p, j) => ({ i: off + k0 + j, p })); };
    const xf = st.xfNow;
    if (xf && !xf.keyed && !xf.morph && st.states) {
      const A = new Map(idx(st.states[xf.from]).map((q) => [q.i, q.p])), out = [];
      const u = xf.extend ? segEase(clamp01(xf.u / XF_EXTEND.RESCALE)) : xf.u;
      for (const q of idx(st.states[xf.to])) { const a = A.get(q.i); if (a) out.push({ i: q.i, p: [xfLerp(a[0], q.p[0], u), xfLerp(a[1], q.p[1], u)] }); }
      return out;
    }
    return idx((st.states && st.states[st.active | 0]) || st);
  };
  const lpRuleYNow = (st, k) => {   /* a reference rule's y this frame (its value re-projected by the active state; lerped across a rescale) */
    const S0 = (st.states && st.states[st.active | 0]) || st, xf = st.xfNow;
    const on = (S) => { const r = (S.hlines || [])[k]; return r ? r.y : null; };
    if (xf && !xf.keyed && !xf.morph && st.states) { const a = on(st.states[xf.from]), b = on(st.states[xf.to]); if (a == null || b == null) return null;
      return xfLerp(a, b, xf.extend ? segEase(clamp01(xf.u / XF_EXTEND.RESCALE)) : xf.u); }
    return on(S0);
  };
  const lpMarkDatum = (st, si, i) => {
    /* P48 T2: a datum resolves against the ACTIVE chart state - after a rescale the page's chart is the derived one, whose
       series is a window of the page's own, so the page's datum index maps by the window's offset; a datum the window
       dropped resolves to nothing (a species on it does not fire), never to the wrong point */
    return lpMarkDatumOn((st.states && st.states[st.active | 0]) || st, si, i);
  };
  /* stylesheet rules beat SVG presentation attributes, so colour/size overrides on text go through `style` */
  const lpText = (parent, cls, x, y, anchor, text, at) => {
    const e = lpEl("text", cls, parent, { x: (+x).toFixed(1), y: (+y).toFixed(1), "text-anchor": anchor, ...(at || {}) });
    e.textContent = text; return e;
  };
  /* chart hygiene shared by the page builders (s9.22-9.23b, operator review of T5: "we lost our labelling/charting
     best practices"): y gridlines carry TICK LABELS with the unit (nice step, 4-6 ticks, the zero line heavier), the
     unit comes from page.unit or axes.yunit, the basis (axes.ylabel) floats top-left inside the plot. */
  const lpUnit = (pg) => String(pg.unit || (pg.axes || {}).yunit || "");
  const lpYTicks = (st, lo, hi, my, xa, xb, unit, labX, divs) => {
    const step = lpNiceStep(Math.max(1e-9, (hi - lo) / (divs || 5))), out = [];
    let n = 0;
    for (let tv = Math.ceil(lo / step - 1e-9) * step; tv <= hi + 1e-9; tv += step) {
      const v = Math.abs(tv) < step * 1e-6 ? 0 : tv, y = my(v);
      const gl = lpEl("line", v === 0 ? "ax" : "grid", st.chart, { x1: xa, x2: xb, y1: y.toFixed(1), y2: y.toFixed(1) });
      const tl = lpText(st.chart, "lab", labX, y + (st.portrait ? 14 : 8), "end", lpWithUnit(lpTick(v), unit));
      out.push(gl); out.push(tl);
      lpMark(st, "tick:" + n, "tick", gl, { v, y, x1: xa, x2: xb });   /* P48 T1: a rescale retargets ticks by value, so the value rides with the mark */
      lpMark(st, "ylab:" + n, "ylabel", tl, { v, x: labX, y: y + (st.portrait ? 14 : 8) });
      n++;
    }
    return out;
  };
  const lpYLabel = (st, pg, x, y, at) => { const t = (pg.axes || {}).ylabel; if (!t) return null;
    const e = lpText(st.chart, "lab", x, y, "start", String(t), { style: "font-size:" + (st.portrait ? 40 : 22) + "px;fill:#aeb6be", ...(at || {}) });
    lpMark(st, "axislabel", "axislabel", e, { x, y }); return e; };
  /* RACE (bar-chart-race): ranked horizontal bars per period. EVERYTHING is a smooth function of u (period units):
     a value eases (smoothstep) between consecutive period values over the WHOLE period - exact at every period,
     still at both ends of each; the rank order is read from those values every frame, and a row SWAP is a pair's
     crossing, solved from the four period values, eased over RACE_SWAP of the period and centred on it (clamped
     inside the period so the integers stay settled). A row's position is its period rank plus the swaps in
     flight: continuous, no keyframes, no clock, no state - a seek lands the identical frame. The axis max glides
     on the same values (a coarsening tick set fades, never pops); the accent is binary - this bar leads now - and
     hands over where the values cross (the bars are the same length there). Settled periods show value_strings
     verbatim; mid-move values are interpolations. */
  const buildLedgerRace = (st, pg) => {
    const periods = pg.periods || [], rows = st.vals, T = periods.length, N = rows.length, unit = lpUnit(pg);
    const G = { NAME_X: 150, TRACK_X: 172, TRACK_W: 690, TOP: 70, H: 400 };
    G.PITCH = G.H / Math.max(1, N); G.BAR_H = Math.max(12, G.PITCH * 0.62);
    const valueAt = (u, j) => {
      if (T < 2) return rows[j][0];
      const uu = Math.min(Math.max(u, 0), T - 1), i = Math.min(Math.floor(uu), T - 2);
      return rows[j][i] + (rows[j][i + 1] - rows[j][i]) * smoothstep(uu - i);
    };
    /* descending by value, index breaks ties: a total order, identical every evaluation */
    const rankAt = (i) => rows.map((_, j) => ({ j, v: rows[j][i] })).sort((a, b) => b.v - a.v || a.j - b.j)
      .reduce((acc, o, r) => { acc[o.j] = r; return acc; }, new Array(N));
    const ranks = Array.from({ length: Math.max(1, T) }, (_, i) => rankAt(i));
    const swaps = [];   /* per period: every pair whose order flips, with the crossing's period fraction */
    for (let i = 0; i + 1 < T; i++) {
      const list = [];
      for (let j = 0; j < N; j++) for (let k = j + 1; k < N; k++) {
        const jAbove = ranks[i][j] < ranks[i][k];
        if (jAbove === (ranks[i + 1][j] < ranks[i + 1][k])) continue;   /* same order at both ends: no crossing (the eased difference is monotone) */
        const den = (rows[j][i + 1] - rows[j][i]) - (rows[k][i + 1] - rows[k][i]);
        const f = den ? lpInvSmooth((rows[k][i] - rows[j][i]) / den) : 0;
        const h = Math.max(LPX.RACE_SWAP_MIN / 2, Math.min(LPX.RACE_SWAP / 2, f, 1 - f));   /* half-window: full mid-period, tighter at the ends */
        list.push({ down: jAbove ? j : k, up: jAbove ? k : j, c: Math.min(Math.max(f, h), 1 - h), w: 2 * h });
      }
      swaps.push(list);
    }
    const ticks = [];
    for (let k = 0; k < LPX.RACE_TICKS; k++)
      ticks.push({ line: lpEl("line", "grid", st.chart, { y1: G.TOP - 6, y2: G.TOP + G.H, opacity: 0 }), lab: lpText(st.chart, "lab", 0, G.TOP - 18, "middle", "", { opacity: 0 }) });
    const items = rows.map((_, j) => {   /* a row: the name at the left of the track, the bar, the exact value at its end */
      const g = lpEl("g", "", st.chart);
      lpText(g, "lab", G.NAME_X, G.PITCH / 2 + 9, "end", String((pg.labels || [])[j] ?? ""), { style: "font-weight:700;fill:#F2F2F2" });
      const bar = lpEl("rect", "bar", g, { x: G.TRACK_X, y: ((G.PITCH - G.BAR_H) / 2).toFixed(1), width: 0, height: G.BAR_H.toFixed(1), rx: 4 });
      const val = lpText(g, "val", G.TRACK_X, G.PITCH / 2 + 9, "start", "");
      const rec = { g, bar, val };
      lpMark(st, "r:" + j, "row", bar, { x: G.TRACK_X, h: G.BAR_H, pitch: G.PITCH, j }, rec);
      return rec;
    });
    const period = lpText(st.chart, "callout", 985, 548, "end", "", { style: "fill:#F2F2F2;font-size:60px", opacity: 0 });   /* below the rows, clear of every bar */
    st.race = { G, periods, rows, T, N, unit, valueAt, ranks, swaps, ticks, items, period };
    st.buildDur = LPX.RACE_IN + Math.max(0, T - 1) * LPX.RACE_PERIOD;
    /* rank-settled per period, seconds from the scene's open: period 0 when the grow-in lands, period i at u = i,
       where its values and ranks are exact (the parent reads st.sync to cue a caption or a sound on the settle) */
    const T0 = LP.ROLL + LP.SAVOR + LP.FIELD + LPX.RACE_IN;
    st.sync = periods.map((p, i) => ({ period: p, at: +(T0 + i * LPX.RACE_PERIOD).toFixed(3) }));
    st.paint = paintLedgerRace;
  };
  const lpRankPos = (R, u, j) => {   /* period rank plus the swaps in flight: continuous, exact at every integer u */
    if (R.T < 2) return R.ranks[0][j];
    const uu = Math.min(Math.max(u, 0), R.T - 1), i = Math.min(Math.floor(uu), R.T - 2), f = uu - i;
    let pos = R.ranks[i][j];
    for (const sw of R.swaps[i]) {
      if (sw.up !== j && sw.down !== j) continue;
      const e = smoothstep(clamp01((f - sw.c) / sw.w + 0.5));
      pos += sw.down === j ? e : -e;
    }
    return pos;
  };
  const paintLedgerRace = (st, c, secs) => {
    const R = st.race, G = R.G, u = Math.max(0, secs - LPX.RACE_IN) / LPX.RACE_PERIOD;
    const grow = expoOut(clamp01(secs / LPX.RACE_IN));
    const vals = R.items.map((_, j) => R.valueAt(u, j));
    const byV = vals.map((_, j) => j).sort((a, b) => vals[b] - vals[a] || a - b), leader = byV[0];
    const scaleMax = Math.max(vals[leader] * 1.06, 1e-6), step = lpNiceStep(scaleMax / 5);
    /* the axis glides: every tick slides with the scale; when the nice step coarsens (1-2-5), the finer set fades
       over the first half of the new band instead of popping, and a tick fades in over the last 4% of the scale */
    const mant = Math.round(step / Math.pow(10, Math.floor(Math.log10(step)))), fine = step / (mant === 5 ? 2.5 : 2);
    const rho = scaleMax / 5 / step, rmin = fine / step, fineOn = 1 - clamp01((rho - rmin) / (0.5 * (1 - rmin)));
    const axisOn = clamp01((grow - 0.5) / 0.3);
    let k = 0;
    for (let tv = 0; tv <= scaleMax + 1e-9 && k < R.ticks.length; tv += fine, k++) {
      const tk = R.ticks[k], coarse = Math.abs(tv / step - Math.round(tv / step)) < 1e-6;
      const on = (coarse ? 1 : fineOn) * clamp01((scaleMax - tv) / (0.04 * scaleMax)) * axisOn, x = (G.TRACK_X + tv / scaleMax * G.TRACK_W).toFixed(1);
      tk.line.setAttribute("x1", x); tk.line.setAttribute("x2", x); tk.line.setAttribute("opacity", on.toFixed(3));
      tk.lab.setAttribute("x", x); tk.lab.setAttribute("opacity", on.toFixed(3)); tk.lab.textContent = lpTick(tv) + R.unit;
    }
    for (; k < R.ticks.length; k++) { R.ticks[k].line.setAttribute("opacity", 0); R.ticks[k].lab.setAttribute("opacity", 0); R.ticks[k].lab.textContent = ""; }
    const uu = Math.min(Math.max(u, 0), Math.max(0, R.T - 1)), near = Math.round(uu), settled = Math.abs(uu - near) < LPX.RACE_SETTLE;
    R.period.textContent = String(R.periods[near] ?? "");   /* the period label hands over at the midpoint of the move */
    R.period.setAttribute("opacity", (0.85 * grow).toFixed(2));
    for (const j of [...byV].reverse()) st.chart.appendChild(R.items[j].g);   /* paint order follows value: the overtaker comes forward */
    R.items.forEach((it, j) => {
      const w = vals[j] / scaleMax * G.TRACK_W * grow;
      it.g.setAttribute("transform", "translate(0 " + (G.TOP + lpRankPos(R, u, j) * G.PITCH).toFixed(2) + ")");
      it.bar.setAttribute("width", w.toFixed(2));
      it.bar.setAttribute("class", "bar" + (j === leader ? " emph" : ""));
      it.val.setAttribute("x", (G.TRACK_X + w + 12).toFixed(1));
      it.val.setAttribute("opacity", clamp01((grow - 0.85) / 0.15).toFixed(2));
      it.val.textContent = settled ? String((st.vstr[j] || [])[near] ?? lpFmt(vals[j])) : lpFmt(vals[j]);
    });
  };
  /* DECLINE (decline-chart): one metric. The line draws downward from start to end while the value
     counts down to the exact end string and the ground darkens from the same progress; the endpoint
     locks in with no recovery. The start value stays on the page as a ghost so the fall has a from.
     Hygiene: y ticks with the unit, the zero line heavier; x labels are DISPLAY strings - the series'
     own date ticks (axes.xticks) when it has them, else the two endpoints' display_labels (never a raw
     float); the basis (axes.ylabel) top-left; the metric named inline at the line's start (s9.23b). */
  const buildLedgerDecline = (st, pg) => {
    const vals = st.vals, n = Math.max(1, vals.length), ax = pg.axes || {}, unit = lpUnit(pg), dl = pg.display_labels || {};
    const L = 96, R = 40, T = 120, B = 470, W = 1000;
    let y0 = Math.min(...vals), y1 = Math.max(...vals); const pad = (y1 - y0) * 0.08 || 1; y0 -= pad; y1 += pad;
    const xn = (pg.labels || []).map((l) => parseFloat(l)), numeric = xn.length === n && xn.every(Number.isFinite);   /* a dense series' own x, else the index */
    const xs = numeric ? xn : vals.map((_, i) => i), xa = Math.min(...xs), xb = Math.max(...xs);
    const mx = (x) => L + (xb > xa ? (x - xa) / (xb - xa) : 0.5) * (W - L - R), my = (v) => T + (1 - (v - y0) / (y1 - y0)) * (B - T);
    const gid = "lpgnd" + n;
    lpEl("defs", "", st.chart).innerHTML = '<linearGradient id="' + gid + '" x1="0" y1="0" x2="0" y2="1">'
      + '<stop offset="0" stop-color="#05131E" stop-opacity="0"/><stop offset="1" stop-color="#05131E" stop-opacity="1"/></linearGradient>';
    const ground = lpEl("rect", "", st.chart, { x: 0, y: T, width: W, height: B - T + 30, fill: "url(#" + gid + ")", opacity: 0 });
    lpEl("line", "ax", st.chart, { x1: L, x2: W - R, y1: B, y2: B });
    lpYTicks(st, y0, y1, my, L, W - R, unit, L - 12);
    const s = pg.start || {}, e = pg.end || {};
    const xt = numeric ? (ax.xticks || []).filter((t) => Array.isArray(t) && +t[0] >= xa && +t[0] <= xb) : [];
    const labels = xt.length
      ? xt.map(([x, lab]) => lpText(st.chart, "lab", mx(+x), B + 32, "middle", String(lab), { opacity: 0 }))
      : [lpText(st.chart, "lab", mx(xs[0]), B + 32, "start", String(dl.start ?? s.label ?? ""), { opacity: 0 }),
         lpText(st.chart, "lab", mx(xs[n - 1]), B + 32, "end", String(dl.end ?? e.label ?? ""), { opacity: 0 })];
    const ylab = lpYLabel(st, pg, L, 64, { opacity: 0 }); if (ylab) labels.push(ylab);   /* top-left, on the callout's row, clear of the ghost */
    const d = vals.map((v, i) => (i ? "L" : "M") + mx(xs[i]).toFixed(1) + " " + my(v).toFixed(1)).join(" ");
    const p = lpEl("path", "ser", st.chart, { d, style: "stroke:#ED6A4A" });   /* a fall is the negative token */
    const len = p.getTotalLength ? p.getTotalLength() : 2000;
    p.setAttribute("stroke-dasharray", len); p.setAttribute("stroke-dashoffset", len);
    const tip = lpEl("circle", "", st.chart, { r: 6, fill: "#ED6A4A", opacity: 0 });
    const end = lpEl("circle", "", st.chart, { cx: mx(xs[n - 1]).toFixed(1), cy: my(vals[n - 1]).toFixed(1), r: 6, fill: "#F5B72E", opacity: 0 });
    const ghost = lpText(st.chart, "val", mx(xs[0]) + 14, my(vals[0]) - 16, "start", String(s.value_string ?? lpFmt(vals[0])), { opacity: 0 });
    const name = dl.series ? lpText(st.chart, "sname", mx(xs[0]) + 14, my(vals[0]) + 34, "start", String(dl.series), { opacity: 0, style: LP_HALO + "fill:#ED6A4A" }) : null;   /* named at the line's start, revealed with it */
    const big = lpText(st.chart, "callout", W - R, 70, "end", "", { style: "fill:#F2F2F2;font-size:64px", opacity: 0 });
    st.dec = { p, len, tip, end, ground, ghost, name, big, labels, start: vals[0], last: vals[n - 1], endStr: String(e.value_string ?? lpFmt(vals[n - 1])) };
    st.plot = { L, R, T, B, W, x0: xa, x1: xb, y0, y1, log: false };
    lpMark(st, "s0", "line", p, { pts: vals.map((v, i) => [mx(xs[i]), my(v)]), vals: vals.map((v) => +v), len, k0: 0, muted: false, col: "#ED6A4A" }, st.dec);
    if (name) lpMark(st, "name:s0", "name", name, { x: mx(xs[0]) + 14, y: my(vals[0]) + 34 });
    labels.forEach((l, i) => lpMark(st, "xlab:" + i, "xlabel", l, { x: +l.getAttribute("x"), y: +l.getAttribute("y") }));
    st.buildDur = LPX.DECLINE_BUILD; st.paint = paintLedgerDecline;
  };
  const paintLedgerDecline = (st, c) => {
    const D = st.dec, k = clamp01(c / LPX.DECLINE_IN);                                                /* IN: the frame settles */
    const prRaw = clamp01((c - LPX.DECLINE_IN) / (1 - LPX.DECLINE_IN - LPX.DECLINE_OUT));
    const pr = strokeFrac(D.p, D.len, prRaw) ?? pow2out(prRaw);      /* HOLD: draw, countdown, gloom - one progress (a hand's under curvature_stroke) */
    const lock = clamp01((c - 1 + LPX.DECLINE_OUT) / LPX.DECLINE_OUT);                                /* OUT: the bottom locks in, no recovery */
    D.ghost.setAttribute("opacity", (0.5 * k).toFixed(2)); D.labels.forEach((l) => l.setAttribute("opacity", k.toFixed(2)));
    D.p.setAttribute("stroke-dashoffset", (D.len * (1 - pr)).toFixed(1));
    const drawing = pr > 0.01 && pr < 0.995;
    if (drawing && D.p.getPointAtLength) { const q = D.p.getPointAtLength(D.len * pr); D.tip.setAttribute("cx", q.x.toFixed(1)); D.tip.setAttribute("cy", q.y.toFixed(1)); }
    D.tip.setAttribute("opacity", drawing ? 1 : 0);
    if (D.name) D.name.setAttribute("opacity", clamp01(pr / 0.08).toFixed(2));
    D.ground.setAttribute("opacity", (0.55 * pr).toFixed(3));
    D.end.setAttribute("opacity", clamp01((pr - 0.94) / 0.06).toFixed(2));
    D.end.setAttribute("r", (6 + 3 * expoOut(lock)).toFixed(2));
    D.big.setAttribute("opacity", k.toFixed(2));
    D.big.textContent = pr >= 1 ? D.endStr : lpFmt(D.start + (D.last - D.start) * pr);
  };
  /* COMBO (data-chart): bars and a line on one plot, each on its own scale, a staggered reveal - bars
     in reading order with each value landing as its bar does, then the line draws at one speed with a
     travelling dot and NYT-style direct labels that count to the exact tokens and stay by the points.
     Hygiene: the bars' scale carries y ticks with the unit and the basis top-left; the line is named
     inline at its end and its values are direct labels in its own colour (the halo keeps every label
     legible where the line crosses it; a label that would land on a bar's value stacks above it). */
  const buildLedgerCombo = (st, pg) => {
    /* P47 T9 (the fourth watch: "a bar chart laid against the lines as a combo chart"): the bars are SIGNED - a drop goes down
       from a zero line and is blood red, a rise goes up and is green (E28) - and a bar that carries its own x sits on the
       lines' time axis; the lines take their OWN scale on a right axis with unit ticks; their points are registered so a
       bracket can measure them (the +80 bp on the ring). */
    const n = Math.max(1, st.vals.length), unit = lpUnit(pg), P = !!st.portrait;
    const vmax = Math.max(0, ...st.vals.map((v) => +v)), vmin = Math.min(0, ...st.vals.map((v) => +v)), span = Math.max(1e-9, vmax - vmin) * 1.12;
    const top = 110, bot = 470, x0 = 96;
    let x1 = (pg.series || []).some((q) => q.pts && q.pts.length) ? 806 : 880;   /* the lines' right axis needs its own margin */
    /* TIERS (the macro-chart intake, 2026-09-07 - Cleveland & McGill's common-scale rule and the Economist's shared-x
       subplots): when the lines are a LEVEL whose zero is meaningless (a 4 % yield) and the bars are a signed FLOW whose zero
       is the story, one plot forces a false zero on one of them. Two bands sharing the x instead: the lines above, the bars
       below, each on its own scale, each owning its own gridlines. `tiers` is the page's key; without it nothing changes. */
    const TIER = { LINE: 0.58 };   /* [DERIVED] the share of the plot the LINE's scale maps into, from the top - it overlays the bars */
    const H = bot - top, tiers = !!pg.tiers && (pg.series || []).some((q) => q.pts && q.pts.length) && st.vals.length;
    if (tiers) x1 = 700;   /* the tiered plot reserves a right GUTTER for the terminal labels - the Economist layout: the label replaces the axis */
    const lineTop = top, lineBot = tiers ? top + H * TIER.LINE : bot;
    const barTop = top, barBot = bot;   /* the operator, 2026-09-07: "the line needs to overlay the bars, that's the whole point" - the bars keep the WHOLE plot and their own zero; the line rides over them on its own scale (the intake's Archetype 1), owning no axis and no gridline */
    const bmy = (v) => barBot - (v - vmin * 1.12) / span * (barBot - barTop), base = bmy(0);   /* the bars' own zero, inside their band */
    const series = (pg.series || []).filter((s) => s.pts && s.pts.length), barsIn = pg.bars || [];
    let lo = Infinity, hi = -Infinity, xa = Infinity, xb = -Infinity;
    for (const s of series) for (const [x, v] of s.pts) { lo = Math.min(lo, +v); hi = Math.max(hi, +v); xa = Math.min(xa, +x); xb = Math.max(xb, +x); }
    for (const b of barsIn) if (b && b.x != null) { xa = Math.min(xa, +b.x); xb = Math.max(xb, +b.x); }
    const slotW = (x1 - x0) / n, bw = Math.min(slotW * 0.62, barsIn.length && barsIn[0] && barsIn[0].x != null ? (x1 - x0) / Math.max(1, (xb - xa) * 12) * 0.62 : slotW * 0.62);
    const cx = (i) => (barsIn[i] && barsIn[i].x != null && xb > xa) ? x0 + (+barsIn[i].x - xa) / (xb - xa) * (x1 - x0) : x0 + slotW * (i + 0.5);
    lpYTicks(st, vmin * 1.12, vmax * 1.12, bmy, x0 - 20, x1 + 20, unit, x0 - 30, tiers ? 3 : 5);   /* a short band wants fewer ticks */
    lpYLabel(st, pg, x0 - 20, (tiers ? barTop : top) - 16);   /* the unit belongs to the band it measures */
    const bars = st.vals.map((v, i) => {
      const h = Math.max(3, Math.abs(+v) / span * (barBot - barTop)), emph = i === st.emph, neg = +v < 0;
      const bar = lpEl("rect", "bar" + (neg ? " neg" : " pos") + (emph ? " emph" : ""), st.chart, { x: (cx(i) - bw / 2).toFixed(1), y: (neg ? base : base - h).toFixed(1), width: bw.toFixed(1), height: h.toFixed(1), rx: 5 });
      bar.style.transformOrigin = "0 " + base + "px"; bar.style.transform = "scaleY(0)";
      const lab = lpText(st.chart, "lab", cx(i), barBot + 34, "middle", String((pg.labels || [])[i] ?? ""), { opacity: 0 });
      const valY = neg ? Math.min(base + h + (P ? 30 : 26), barBot - 8) : base - h - 14;   /* a drop's value sits under its bar, never on the month labels */
      const tells = emph || Math.abs(+v) >= LPX.COMBO_LABEL_SHARE * Math.max(1e-9, ...st.vals.map((q) => Math.abs(+q)));   /* E52: the chart reads without printing every number */
      const val = tells ? lpText(st.chart, "val", cx(i), valY, "middle", st.vstr[i] != null ? String(st.vstr[i]) : lpFmt(v),
        { opacity: 0, style: LP_HALO + (emph ? "fill:#F5B72E;font-size:30px;font-weight:700" : "") }) : null;
      const rec = { bar, lab, val, valY: tells ? valY : -1e9, cx: cx(i) };
      lpMark(st, "b:" + i, "bar", bar, { x: cx(i) - bw / 2, y: neg ? base : base - h, w: bw, h, base, cx: cx(i), end: neg ? base + h : base - h, neg, v: +v }, rec);
      lpMark(st, "xlab:" + i, "xlabel", lab, { x: cx(i), y: barBot + 34 });
      if (val) lpMark(st, "val:b:" + i, "value", val, { x: cx(i), y: valY, v: +v });
      return rec;
    });
    const cxOf = (b) => b.cx;
    const pad = (hi - lo) * 0.12 || 1; lo -= pad; hi += pad;
    const ly = (v) => lineBot - (+v - lo) / (hi - lo) * (lineBot - lineTop);   /* the lines' own band: no zero is faked, no gridline is fought */
    /* the lines' own axis, on the right, with the unit (pg.line_unit, else the first line's unit, else none) */
    const lunit = pg.line_unit != null ? pg.line_unit : "";
    { const step = lpNiceStep(Math.max(1e-9, (hi - lo) / (tiers ? 2 : 4)));
      for (let tv = Math.ceil(lo / step - 1e-9) * step; tv <= hi + 1e-9; tv += step) {
        const v = Math.abs(tv) < step * 1e-6 ? 0 : tv;
        if (tiers) lpEl("line", "grid", st.chart, { x1: x0 - 20, x2: x1 + 20, y1: ly(v).toFixed(1), y2: ly(v).toFixed(1) });   /* its own band, its own grid: the bands never overlap, so no prison bars */
        else lpText(st.chart, "lab", x1 + 14, ly(v) + (P ? 14 : 8), "start", lpWithUnit(lpTick(v), lunit), { style: "fill:#aeb6be" });
      }
      /* the tier's scale is written ONCE, on its top gridline, instead of a whole second axis - the terminal labels carry the rest */
      if (tiers) lpText(st.chart, "lab", x0 - 30, ly(Math.floor(hi / step) * step) + (P ? 14 : 8), "end", lpWithUnit(lpTick(Math.floor(hi / step) * step), lunit), { style: "fill:#aeb6be" }); }
    const lines = series.map((s, si) => {
      const aligned = s.pts.length === n, lx = (x, k) => aligned ? cx(k) : x0 + (+x - xa) / (xb - xa || 1) * (x1 - x0);   /* one point per bar sits on the bar */
      const pts = s.pts.map(([x, v], k) => [lx(x, k), ly(v), v]), col = LP_PAL[s.color] || LP_PAL.cobalt;
      const p = lpEl("path", "ser", st.chart, { d: pts.map(([x, y], k) => (k ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" "), style: "stroke:" + col });
      const len = p.getTotalLength ? p.getTotalLength() : 2000;
      p.setAttribute("stroke-dasharray", len); p.setAttribute("stroke-dashoffset", len);
      const dot = lpEl("circle", "", st.chart, { r: 7, fill: col, opacity: 0 });
      /* s9.23b: direct labels never overprint - a label that would land on its bar's value stacks above it instead */
      const labels = pts.map(([x, y], k) => {
        const by = aligned ? bars[k].valY : -1e9, ly0 = y - 18, yy = Math.abs(ly0 - by) < 32 ? by - (k === st.emph ? 38 : 30) : ly0;
        return lpText(st.chart, "val", x, yy, "middle", "", { opacity: 0, style: LP_HALO + "fill:" + col + ";font-size:24px" });
      });
      const last = pts[pts.length - 1];   /* the inline name: right of the last point when there is room, else above it, ending at it.
         A combo whose SUB names the lines by colour carries no inline name at all - it would repeat the sub and land in the bars
         (the fourth watch: "we need better handling on text/labels"); the sub is the legend and a bracket carries the number. */
      /* the intake (Economist / Axios): a DETACHED legend is the sin, a TERMINAL label is the cure. In tiers the line band has
         no right axis, so the label sits just past the line's end; on one plot it keeps the old rule. */
      const room = tiers || x1 + 200 <= (st.geom ? st.geom.W : 1000), quiet = !!pg.legend_in_sub;
      const name = lpText(st.chart, "sname", room ? last[0] + (tiers ? 12 : 44) : last[0], room ? last[1] + 8 : last[1] - 26, room ? "start" : "end", quiet ? "" : (s.label ? s.label + " " : "") + (s.name || ""),
        { opacity: 0, style: LP_HALO + "fill:" + col + (tiers ? ";font-size:" + (P ? 30 : 19) + "px" : "") });   /* the gutter's label is a tag, not a headline */
      st.linePts.push(pts.map(([x, y]) => [x, y]));   /* the species' targets (a bracket on a line) */
      const rec = { p, len, dot, labels, name, pts, ny: room ? last[1] + 8 : last[1] - 26 };
      lpMark(st, "s" + si, "line", p, { pts: pts.map(([x, y]) => [x, y]), vals: pts.map(([, , v]) => +v), len, k0: 0, muted: false, col }, rec);
      return rec;
    });
    /* s9.23b: a name never overprints another name OR a bar's printed value. Each name lifts above every value within
       NAME_CLEAR_X of its own x, then the names push apart; the group is clamped inside the plot. */
    const ngap = P ? 50 : 28, clearX = P ? 150 : 90;
    for (const ln of lines) {
      const nx = ln.name.getAttribute("text-anchor") === "end" ? +ln.name.getAttribute("x") - clearX : +ln.name.getAttribute("x");
      for (const b of bars) if (b.val && Math.abs(cxOf(b) - nx) < clearX && Math.abs(b.valY - ln.ny) < ngap) ln.ny = Math.min(ln.ny, b.valY - ngap);
    }
    const ord = [...lines].sort((a, b) => a.ny - b.ny);
    for (let i = 1; i < ord.length; i++) if (ord[i].ny - ord[i - 1].ny < ngap) ord[i].ny = ord[i - 1].ny + ngap;
    const lift = ord.length ? Math.max(0, ord[ord.length - 1].ny - (lineBot - 8)) : 0;
    for (const ln of ord) { ln.ny -= lift; ln.name.setAttribute("y", Math.max(lineTop + ngap * 0.6, ln.ny).toFixed(1));
      lpMark(st, "name:s" + lines.indexOf(ln), "name", ln.name, { x: +ln.name.getAttribute("x"), y: Math.max(lineTop + ngap * 0.6, ln.ny) }, ln); }
    /* the lines' daily labels would be a wall of numbers on a dense series: only a sparse series (one point per bar) labels its points */
    for (const ln of lines) if (ln.pts.length > 2 * n) for (const lb of ln.labels) lb.remove(), ln.labels = [];
    st.combo = { bars, lines }; st.buildDur = LPX.COMBO_BUILD; st.paint = paintLedgerCombo;
    st.plot = { L: x0, R: st.geom ? st.geom.W - x1 : 1000 - x1, T: top, B: bot, W: st.geom ? st.geom.W : 1000, x0: xa, x1: xb, y0: lo, y1: hi, log: false };
  };
  const paintLedgerCombo = (st, c) => {
    const C = st.combo, nb = C.bars.length;
    C.bars.forEach((b, i) => {
      const k = expoOut(clamp01((c - i * LPX.COMBO_BARS / nb) / 0.18));   /* reading order: each bar starts as the one before settles */
      b.bar.style.transform = "scaleY(" + k.toFixed(4) + ")";
      b.lab.setAttribute("opacity", clamp01((k - 0.5) / 0.3).toFixed(2));
      if (b.val) b.val.setAttribute("opacity", clamp01((k - 0.9) / 0.1).toFixed(2));
    });
    C.lines.forEach((ln, si) => {
      const g = (c - LPX.COMBO_BARS - si * 0.1) / LPX.COMBO_LINE, f = strokeFrac(ln.p, ln.len, clamp01(g)) ?? clamp01(g);   /* ease none: one speed (a hand's under curvature_stroke); g runs on so the last label lands */
      ln.p.setAttribute("stroke-dashoffset", (ln.len * (1 - f)).toFixed(1));
      const drawing = f > 0 && f < 1;
      if (drawing && ln.p.getPointAtLength) { const q = ln.p.getPointAtLength(ln.len * f); ln.dot.setAttribute("cx", q.x.toFixed(1)); ln.dot.setAttribute("cy", q.y.toFixed(1)); }
      ln.dot.setAttribute("opacity", drawing ? 1 : 0);
      const m = Math.max(1, ln.pts.length - 1);
      ln.labels.forEach((lb, k) => {
        const r = clamp01((g - k / m) / 0.12);   /* appears as the dot arrives, counts to the token */
        lb.setAttribute("opacity", clamp01(r / 0.2).toFixed(2));
        lb.textContent = r >= 1 ? String(ln.pts[k][2]) : lpFmt(+ln.pts[k][2] * pow2out(r));
      });
      ln.name.setAttribute("opacity", clamp01((g - 1) / 0.05).toFixed(2));
    });
  };
  /* ---- SHARE (P48 T4): a PIE, and the piece of it that leaves --------------------------------------
     `ledger_page.py` refuses a donut by name for every other variant. E53 s1's amendment (2026-09-07)
     allows it here inside four bounds, which the compiler enforces: the claim is about ONE named slice,
     that slice is the only coloured one and the rest are muted context, the figure the claim turns on is
     WRITTEN so no angle has to be estimated, and there are five slices or fewer.
     The page's payoff is the PEEL. The named slice is drawn as TWO adjacent wedges in one colour - what
     stays and the piece the sentence is about - so at rest it reads as one wedge; on its word the piece
     slides out along its own bisector and goes blood red (E28: the loss is geometry AND colour), and what
     is left is exactly the figure the next sentence uses. The sweep starts at twelve o'clock with the
     claim's slice, because the eye starts where the story is. */
  const LP_TAU = Math.PI * 2;
  const S_OUT = (R) => R * LPX.SHARE_PEEL_OUT;   /* how far the piece slides from the pie */
  const pw_band = (P) => (P ? 132 : 82);   /* [DERIVED, P48 T4] the figure band under the circle: two lines of the claim */
  /* a wedge from a0 to a1 (radians, 0 = twelve o'clock, clockwise), about (cx, cy) */
  const lpWedge = (cx, cy, r, a0, a1) => {
    const f = (v) => v.toFixed(1);
    if (a1 - a0 >= LP_TAU - 1e-6)   /* a full turn has no chord: two half arcs */
      return "M" + f(cx) + " " + f(cy - r) + " A" + f(r) + " " + f(r) + " 0 1 1 " + f(cx) + " " + f(cy + r)
           + " A" + f(r) + " " + f(r) + " 0 1 1 " + f(cx) + " " + f(cy - r) + " Z";
    const px = (a) => cx + r * Math.sin(a), py = (a) => cy - r * Math.cos(a);
    return "M" + f(cx) + " " + f(cy) + " L" + f(px(a0)) + " " + f(py(a0))
         + " A" + f(r) + " " + f(r) + " 0 " + (a1 - a0 > Math.PI ? 1 : 0) + " 1 " + f(px(a1)) + " " + f(py(a1)) + " Z";
  };
  const buildLedgerShare = (st, pg) => {
    const G = st.geom || { W: 1000, H: 560 }, P = !!st.portrait;
    const vals = (st.vals || []).map((v) => Math.abs(+v) || 0), n = vals.length;
    const total = vals.reduce((a, b) => a + b, 0) || 1;
    const labels = pg.labels || [], cols = pg.colors || [];
    const peel = (pg.peel && Number.isFinite(+pg.peel.value)) ? pg.peel : null;
    const pi = peel && Number.isInteger(peel.index) ? peel.index : -1;
    const cx = G.W * 0.5, top = P ? 96 : 34, bot = G.H - (P ? 30 : 18);
    /* a band at the FOOT of the box belongs to the peel's figure. Written past the rim it landed on a neighbour's name
       (s9.23b), and a pie has no margin to spare: the claim gets its own line under the circle instead, on the side the
       piece leaves towards, so the red wedge points at its own number. */
    const figH = pw_band(P);
    const cy = (top + bot - figH) / 2;
    const R = Math.max(60, Math.min(G.W * 0.5, (bot - figH - top) / 2) * 0.94);
    /* the claim's slice opens the sweep at twelve o'clock: the emphasised index is drawn first, the rest in their order */
    const order = []; if (st.emph >= 0 && st.emph < n) order.push(st.emph);
    for (let i = 0; i < n; i++) if (i !== st.emph) order.push(i);
    const wedges = []; let a = 0;
    for (const i of order) {
      const share = vals[i] / total, full = share * LP_TAU, emph = i === st.emph;
      /* the claim's slice keeps its declared colour; the piece that LEAVES is what goes blood red (E28) - a wedge
         already red could not then show a loss. Every other slice is muted, on a ramp so neighbours stay apart. */
      const col = emph ? (LP_PAL[cols[i]] || cols[i] || LP_PAL.teal)
                       : (cols[i] && cols[i] !== "deemph" ? (LP_PAL[cols[i]] || cols[i]) : LP_SHARE_GREY[Math.max(0, order.indexOf(i) - 1) % LP_SHARE_GREY.length]);
      /* the named slice is TWO wedges of one colour: what stays, then the piece that will leave */
      const cut = (i === pi && peel) ? Math.min(full, Math.abs(+peel.value) / total * LP_TAU) : 0;
      const keep = lpEl("path", "wedge" + (emph ? " emph" : ""), st.chart, { d: lpWedge(cx, cy, R, a, a + full - cut), fill: col, opacity: 0 });
      const w = { i, a0: a, a1: a + full, cut, keep, col, v: vals[i], emph };
      lpMark(st, "w:" + i, "wedge", keep, { a0: a, a1: a + full - cut, cx, cy, r: R, v: vals[i] }, w);
      if (cut > 0) {
        w.piece = lpEl("path", "wedge peel", st.chart, { d: lpWedge(cx, cy, R, a + full - cut, a + full), fill: col, opacity: 0 });
        w.pa = a + full - cut / 2;   /* the piece's own bisector: it leaves along it */
        lpMark(st, "peel", "peel", w.piece, { a0: a + full - cut, a1: a + full, cx, cy, r: R, v: +peel.value, bisector: w.pa }, w);
      }
      /* the name lives ON its slice (E53 s8: never in a legend box), on the bisector; only the claim's slice
         carries a figure, because printing five figures would make the page the ranking E53 s1 refuses */
      const mid = a + full / 2, lx = cx + R * 0.60 * Math.sin(mid), ly = cy - R * 0.60 * Math.cos(mid);
      /* every name is written in LIGHT ink with the charcoal halo the class carries: dark ink on a muted wedge was
         unreadable, and a name a viewer has to hunt for is the same failure as no name. A slice may declare a `short`
         name; a wedge is narrow and "China, Mainland" does not fit in one. */
      const fs = (P ? 40 : 24) * (emph ? 1 : 0.86), ink = emph ? "#FDF6E3" : "#dfe6ec";
      w.lab = lpText(st.chart, "wlab", lx, ly + (emph ? -fs * 0.2 : fs * 0.3), "middle", String((pg.short_labels || [])[i] ?? labels[i] ?? ""),
        { opacity: 0, style: "fill:" + ink + ";font-size:" + fs.toFixed(0) + "px;font-weight:700" });
      if (emph) w.val = lpText(st.chart, "wlab", lx, ly + fs * 0.95, "middle", String((pg.value_strings || [])[i] ?? lpFmt(vals[i])),
        { opacity: 0, style: "fill:" + ink + ";font-size:" + (fs * 0.82).toFixed(0) + "px" });
      lpMark(st, "wlab:" + i, "wedgelabel", w.lab, { x: lx, y: ly });
      wedges.push(w); a += full;
    }
    /* the peel's own figure, written where the piece lands - the claim, in ink, so no angle is estimated (E53 s1c) */
    const pw = wedges.find((w) => w.piece);
    let ptext = null, psub = null;
    if (pw) {
      const fs = P ? 46 : 28, WID = fs * 3.4, pad = P ? 20 : 14;   /* the figure's own half-room, so the clamp knows what it places */
      const ex = Math.max(WID + pad, Math.min(G.W - WID - pad, cx + R * 0.62 * Math.sin(pw.pa)));
      const ey = bot - figH + fs * 0.92, anch = "middle";
      ptext = lpText(st.chart, "callout", ex, ey, anch, String(peel.value_string ?? ""), { opacity: 0, style: LP_HALO + "fill:var(--lp-neg);font-size:" + fs + "px;font-weight:700" });
      psub = lpText(st.chart, "lab", ex, ey + fs * 0.82, anch, String(peel.label ?? ""), { opacity: 0, style: LP_HALO + "fill:#aeb6be;font-size:" + (fs * 0.62).toFixed(0) + "px" });
      lpMark(st, "peelfig", "value", ptext, { x: ex, y: ey, v: +peel.value });
    }
    st.share = { wedges, cx, cy, R, peel: pw || null, ptext, psub, out: S_OUT(R) };
    st.buildDur = LPX.SHARE_BUILD; st.paint = paintLedgerShare;
    st.plot = { L: cx - R, R: G.W - (cx + R), T: cy - R, B: cy + R, W: G.W, x0: 0, x1: 1, y0: 0, y1: total, log: false };
  };
  const LP_SHARE_GREY = ["rgba(184,196,208,.50)", "rgba(184,196,208,.41)", "rgba(184,196,208,.33)", "rgba(184,196,208,.26)"];   /* [DERIVED] muted context: light enough that the claim's slice is the only colour on the page, stepped so neighbours stay apart */
  const paintLedgerShare = (st, c) => {
    const S = st.share, sw = clamp01(c / LPX.SHARE_SWEEP);
    const front = (sw >= 1 ? 1 : expoOut(sw)) * LP_TAU;   /* the sweep, clockwise from twelve; pinned at a closed circle so the last wedge has no hairline */
    for (const w of S.wedges) {
      const a1 = Math.min(w.a1, front), on = a1 > w.a0 + 1e-4;
      const kEnd = Math.min(w.a1 - w.cut, a1);
      w.keep.setAttribute("opacity", on ? 1 : 0);
      if (on) w.keep.setAttribute("d", lpWedge(S.cx, S.cy, S.R, w.a0, Math.max(w.a0, kEnd)));
      if (w.piece) { const p0 = w.a1 - w.cut, pOn = a1 > p0 + 1e-4;
        w.piece.setAttribute("opacity", pOn ? 1 : 0);
        if (pOn) w.piece.setAttribute("d", lpWedge(S.cx, S.cy, S.R, p0, a1)); }
      /* the name writes AS its own slice completes, never before: a label over a wedge that is not there yet is a lie,
         and one that waits for the sweep to pass its end never writes at all for the last slice (the sweep ends there). */
      const fade = LPX.SHARE_LABEL * LP_TAU;
      const o = clamp01((front - w.a1 + fade) / fade).toFixed(2);
      w.lab.setAttribute("opacity", o);
      if (w.val) w.val.setAttribute("opacity", o);
    }
  };
  /* ---- TIERS (P50 T9; BACKLOG R26-24; Bravos shots 35-36's two-panel SPR) ------------------------
     N SMALL MULTIPLES on one page: N bands stacked, each with its own y-scale and its own honest zero
     (E53 s4), sharing ONE x, the tier titles the series' own names. species/tiers.mjs owns every
     number (the bands, the domains, the in-turn clock); this is the DOM.
     The bands draw in turn: a line band is a path in st.paths like any other, so a `build_to` per
     tier (a tier IS a series index on this page) puts each band on its own WORD - which is how the
     page is meant to be authored, and how the golden does it. The drop of one band is measured by
     the bracket in its `form: "bar"`: the same two data, drawn as a bar in the accent (shot 36). */
  const buildLedgerTiers = (st, pg) => {
    const G = st.geom || { W: 1000, H: 560 }, P = !!st.portrait, ax = pg.axes || {};
    const L = P ? 150 : 96, R = P ? 70 : 150, T = P ? 130 : 66, B = P ? G.H - 90 : 468, W = G.W;
    const trs = (pg.tiers || []).filter(Boolean), n = trs.length;
    const bands = tierBands(T, B, n);
    const fs = P ? 34 : 22, ns = P ? 38 : 25;
    /* the ONE x every band shares: the page's own extent, read from every band's data */
    let x0 = Infinity, x1 = -Infinity;
    for (const tr of trs) {
      for (const s of tr.series || []) for (const q of s.pts || []) { x0 = Math.min(x0, +q[0]); x1 = Math.max(x1, +q[0]); }
      if (Array.isArray(tr.x)) { x0 = Math.min(x0, +tr.x[0]); x1 = Math.max(x1, +tr.x[1]); }
    }
    const cats = (trs[0] || {}).x_labels || null;   /* category bands (bars) share one label list instead of one number line */
    const nCat = cats ? cats.length : 0;
    const mx = cats ? (i) => L + (W - L - R) * ((i + 0.5) / Math.max(1, nCat))
                    : (x) => L + (+x - x0) / ((x1 - x0) || 1) * (W - L - R);
    st.tiers = { bands: [], n };
    trs.forEach((tr, ti) => {
      const band = bands[ti]; if (!band) return;
      const tax = tr.axes || {}, lines = (tr.series || []).filter((s) => s.pts && s.pts.length);
      const vals = tr.kind === "bars" ? (tr.values || []) : lines.flatMap((s) => (s.pts || []).map((q) => +q[1]));
      const dom = tierDomain(vals, tax.from_zero !== false);
      const my = (v) => tierY(band, dom[0], dom[1], v);
      /* the band's own gridlines and its own unit: a band is a chart, and every chart says what it measures */
      for (const v of tierTicks(dom[0], dom[1])) {
        const y = my(v);
        lpEl("line", "grid", st.chart, { x1: L, x2: W - R, y1: y.toFixed(1), y2: y.toFixed(1) });
        lpText(st.chart, "lab", L - 10, y + (P ? 12 : 7), "end", lpWithUnit(lpTick(v), tr.unit || ""), { style: "fill:#aeb6be" + (P ? ";font-size:30px" : "") });
      }
      /* the tier's TITLE, over its own band's top-left corner (the page's title stays the argument) */
      const nameEl = lpText(st.chart, "sname", L, band.y0 - TIERS.NAME_DY, "start", String(tr.name || ""),
        { opacity: 0, style: LP_HALO + "fill:var(--lp-chalk);font-size:" + ns + "px" });
      const rec = { name: nameEl, bars: [], ti };
      st.tiers.bands.push(rec);
      if (tr.kind === "bars") {
        const bw = (W - L - R) / Math.max(1, nCat) * 0.62, base = my(Math.max(dom[0], 0));
        (tr.values || []).forEach((v, i) => {
          const h = Math.max(2, Math.abs(+v) / ((dom[1] - dom[0]) || 1) * band.h), neg = +v < 0;
          const bar = lpEl("rect", "bar" + (neg ? " neg" : " pos"), st.chart,
            { x: (mx(i) - bw / 2).toFixed(1), y: (neg ? base : base - h).toFixed(1), width: bw.toFixed(1), height: h.toFixed(1), rx: 4 });
          bar.style.transformOrigin = "0 " + base.toFixed(1) + "px"; bar.style.transform = "scaleY(0)";
          const val = lpText(st.chart, "val", mx(i), (neg ? base + h + (P ? 34 : 20) : base - h - 10).toFixed(1), "middle",
            String((tr.value_strings || [])[i] ?? lpFmt(+v)), { opacity: 0, style: LP_HALO + (P ? "font-size:30px" : "") });
          rec.bars.push({ bar, val });
          lpMark(st, "b:" + ti + ":" + i, "bar", bar, { x: mx(i) - bw / 2, y: neg ? base : base - h, w: bw, h, base, cx: mx(i), end: neg ? base + h : base - h, neg, v: +v });
        });
        st.linePts.push((tr.values || []).map((v, i) => [mx(i), my(+v)]));   /* a bar's top is a datum too: a bracket can measure it */
      } else {
        lines.forEach((s, k) => {
          const pts = s.pts.map(([x, v], i) => [cats ? mx(i) : mx(x), my(v)]);
          const col = LP_PAL[s.color] || LP_PAL[tr.color] || (n > 1 ? LP_PAL.cobalt : LP_PAL.crimson);
          const d = pts.map(([x, y], i) => (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ");
          const p = lpEl("path", "ser", st.chart, { d, stroke: col });
          const len = p.getTotalLength ? p.getTotalLength() : 2000;
          p.setAttribute("stroke-dasharray", len); p.setAttribute("stroke-dashoffset", len);
          const tip = lpEl("circle", "", st.chart, { r: 6, fill: col, opacity: 0 });
          /* the band's name IS this line's name (the line page's law): it writes as the band finishes drawing */
          const prec = { p, len, tip, name: k ? lpText(st.chart, "sname", L, band.y0 - TIERS.NAME_DY, "start", "", { opacity: 0 }) : nameEl,
                         stagger: ti / Math.max(1, n), ny: band.y0 - TIERS.NAME_DY, pts, si: ti, k0: 0, muted: false,
                         data: s.pts.map(([x, v]) => [+x, +v]), d0: d, len0: len };
          st.paths.push(prec);
          lpMark(st, "s" + ti + (k ? ":" + k : ""), "line", p, { pts, vals: s.pts.map((q) => +q[1]), len, k0: 0, muted: false, col }, prec);
          if (!k) st.linePts.push(pts);   /* the tier's own datum positions: series index === tier index */
        });
      }
    });
    /* ONE shared x under the last band - the axis line and its ticks, drawn once for the whole page */
    lpMark(st, "axis", "axis", lpEl("line", "ax", st.chart, { x1: L, x2: W - R, y1: B, y2: B }), { x1: L, x2: W - R, y: B });
    if (cats) cats.forEach((lab, i) => {
      const tx = lpText(st.chart, "lab", mx(i), B + (P ? 52 : 32), "middle", String(lab));
      lpMark(st, "xtick:" + i, "xtick", tx, { v: i, x: mx(i), y: B + (P ? 52 : 32) });
    });
    else (ax.xticks || []).forEach(([x, lab], i) => {
      const tx = lpText(st.chart, "lab", mx(x), B + (P ? 52 : 32), "middle", String(lab));
      lpMark(st, "xtick:" + i, "xtick", tx, { v: +x, x: mx(x), y: B + (P ? 52 : 32) });
    });
    st.buildDur = LPX.TIERS_BUILD; st.paint = paintLedgerTiers;
    st.plot = { L, R, T, B, W: G.W, x0, x1, y0: 0, y1: 1, log: false };
  };
  /* the bands' own build step: the tier titles of the bars bands and their bars, in turn. A LINE
     band needs nothing here - its path is in st.paths, so the page's own build beat and every
     `build_to` on it are the line page's, unchanged. */
  const paintLedgerTiers = (st, c) => {
    const TT = st.tiers; if (!TT) return;
    for (const bd of TT.bands) {
      if (!bd.bars.length) continue;   /* a line band's name rides its line (lpPaintChart) */
      const k = tierBuildK(c, bd.ti, TT.n);
      bd.name.setAttribute("opacity", clamp01((k - 0.1) / 0.25).toFixed(2));
      bd.bars.forEach((bb, i) => {
        const kk = expoOut(clamp01((k - i * 0.08) / 0.55));
        bb.bar.style.transform = "scaleY(" + kk.toFixed(4) + ")";
        bb.val.setAttribute("opacity", clamp01((kk - 0.9) / 0.1).toFixed(2));
      });
    }
  };
  /* ---- TREEMAP (P50 T6; E53 s1's second amendment - the CENSUS exception; Bravos shots 89-91) ----
     The squarified layout is the COMPILER's (ledger_page.squarify, inside page_boxes' own plot, both
     aspects, at build time) and rides the spec as fractions; species/treemap.mjs maps a cell into
     the rect it is drawn in and owns the clock. Nothing is laid out per frame - which is what makes
     the shrink afterwards a park (E58: one affine transform, never a re-layout).
     The labels are the compiler's decision too: it wrote each cell's tier and font from the research
     floors on the cell's real size in stage pixels, so a cell either carries a label that FITS or
     carries none and is counted in the legend line ("and 12 others"). */
  const LP_TREE_RAMP = ["rgba(23,140,131,.86)", "rgba(23,140,131,.68)", "rgba(143,179,240,.55)", "rgba(184,196,208,.42)", "rgba(184,196,208,.30)"];
  const buildLedgerTreemap = (st, pg) => {
    const G = st.geom || { W: 1000, H: 560 }, P = !!st.portrait;
    /* the page's OWN plot margins - the line builder's, which is what ledger_page.treemap_plot mirrors */
    const L = P ? 150 : 70, R = P ? 70 : 220, T = P ? 90 : 40, B = P ? G.H - 80 : 470;
    const lay = (pg.layout || {})[P ? "9:16" : "16:9"] || (pg.layout || {})["16:9"] || { cells: [] };
    const avail = { x: L, y: T, w: G.W - L - R, h: B - T };
    /* the cells were squarified for page_boxes' plot: keep that plot's ASPECT exactly, centred in the
       room the page gives, so no cell is stretched out of the 3:2 the layout was tuned to (and so the
       label sizes the compiler chose off the research's floors scale by ONE ratio, isotropically) */
    const want = ((lay.plot || {}).w || avail.w) / Math.max(1, (lay.plot || {}).h || avail.h);
    let pw = avail.w, ph = pw / want;
    if (ph > avail.h) { ph = avail.h; pw = ph * want; }
    const plot = { x: avail.x + (avail.w - pw) / 2, y: avail.y + (avail.h - ph) / 2, w: pw, h: ph };
    /* the compiler decided each label's size in STAGE pixels against its own plot; this viewBox is not
       that plot, so the sizes ride in on the same ratio the cells do - one scale, no second decision */
    const sc = plot.w / Math.max(1, ((lay.plot || {}).w || plot.w));
    const cells = (lay.cells || []).map((c, i) => {
      const r = treemapRect(c, plot), pad = 6 * sc;
      const g = lpEl("g", "lp-cell", st.chart, { opacity: 0 });
      const fill = LP_PAL[(pg.colors || [])[c.index]] || LP_TREE_RAMP[Math.min(i, LP_TREE_RAMP.length - 1)];
      const box = lpEl("rect", "", g, { x: r.x.toFixed(1), y: r.y.toFixed(1), width: Math.max(0, r.w - 2).toFixed(1), height: Math.max(0, r.h - 2).toFixed(1), fill, rx: 3 });
      let lab = null, val = null;
      if (c.tier >= 1) {
        const f = c.font * sc;
        lab = lpText(g, "lab", r.x + pad, r.y + pad + f, "start", String(c.label),
          { opacity: 0, style: "fill:#F5EFE2;font-size:" + f.toFixed(1) + "px;font-weight:700" });
        if (c.tier >= 2) {
          const vf = c.value_font * sc;
          val = lpText(g, "lab", r.x + pad, r.y + pad + f + vf * 1.15, "start", String(c.value_string || ""),
            { opacity: 0, style: "fill:#F5EFE2;font-size:" + vf.toFixed(1) + "px" });
        }
      }
      return { i, index: c.index, label: String(c.label), rect: r, g, box, lab, val, cx: r.x + r.w / 2, cy: r.y + r.h / 2 };
    });
    /* the parts the page could not name are COUNTED, never dropped: a census says how many there were */
    const legend = lay.legend ? lpText(st.chart, "lab", plot.x, plot.y + plot.h + (P ? 46 : 28), "start", String(lay.legend),
      { opacity: 0, style: "fill:#aeb6be" + (P ? ";font-size:30px" : "") }) : null;
    st.treemap = { cells, plot, sc, legend };
    st.buildDur = LPX.TREEMAP_BUILD; st.paint = paintLedgerTreemap;
    st.plot = { L: plot.x, R: G.W - (plot.x + plot.w), T: plot.y, B: plot.y + plot.h, W: G.W, x0: 0, x1: 1, y0: 0, y1: 1, log: false };
  };
  const paintLedgerTreemap = (st, c) => {
    const TM = st.treemap; if (!TM) return;
    const n = TM.cells.length;
    TM.cells.forEach((cc, i) => {
      const k = treemapCellK(c, i, n), s = treemapCellScale(k);
      cc.g.setAttribute("opacity", clamp01(k / 0.3).toFixed(3));
      cc.g.style.transformOrigin = cc.cx.toFixed(1) + "px " + cc.cy.toFixed(1) + "px";
      cc.g.style.transform = "scale(" + s.toFixed(4) + ")";
      const lk = treemapLabelK(k).toFixed(3);
      if (cc.lab) cc.lab.setAttribute("opacity", lk);
      if (cc.val) cc.val.setAttribute("opacity", lk);
    });
    if (TM.legend) TM.legend.setAttribute("opacity", clamp01((c - 0.85) / 0.15).toFixed(3));
  };
  /* the piece leaves on its word (the `peel` species): it slides out along its own bisector, goes blood red, and its
     figure writes beside it. u is a pure function of t, so a seek lands the identical frame. */
  const lpPeelTo = (st, u) => {
    const S = st.share; if (!S || !S.peel) return;
    const w = S.peel, k = expoOut(clamp01(u)), d = S.out * k;
    w.piece.style.transform = "translate(" + (d * Math.sin(w.pa)).toFixed(2) + "px," + (-d * Math.cos(w.pa)).toFixed(2) + "px)";
    w.piece.setAttribute("fill", k > 0.001 ? "var(--lp-neg)" : w.col);
    if (S.ptext) S.ptext.setAttribute("opacity", clamp01((k - 0.35) / 0.3).toFixed(2));
    if (S.psub) S.psub.setAttribute("opacity", clamp01((k - 0.6) / 0.3).toFixed(2));
  };
  /* RETRACT as a VORTEX (operator, 2026-09-05: "a true spiral of everything getting sucked back into the cream as if a
     vortex / whirlpool"): every colour on the page is a PARTICLE - each ink glyph, each bar, value, tick and label, each
     pill, each point of the series line - with a home position and a distance r from the drain (the board centre).
     The map is analytic in u (FINDING-the-animation-math s3: a seek renderer may only use closed forms):
       the drain takes the centre first     ui  = clamp((u - LAG*rn) / (1 - LAG)),  rn = r / Rmax
       the radius falls slowly, then fast   r'  = r * (1 - ui^1.7)
       differential rotation (the whirl)    th  = TURNS * 2pi * ui * (0.6 + 0.9 * (1 - rn))   - the centre spins faster
       stretch along the flow, area kept    diag(1+a, 1/(1+a)) about the tangent (s4), a = ALPHA * 4ui(1-ui)
       the particle shrinks                 s   = (1 - ui)^0.7
     The series line is re-drawn from its mapped points, so it curls into the drain like a noodle. Phase two: the crisp
     charcoal fades and the STAINS it settled over are sucked down the same drain. A page declared enter:"spiral"
     ARRIVES by the same map run backwards (E25: a returning chart is not drawn like new); exit:"cut" skips the retract
     (a punch that must land on the last line, E40 #5: no species over a spiral out). Idle frames touch nothing. */
  const LP_STATE_MAX = 3;   /* P48: charts on one page. A fourth is a new page or a card - the player's size and the reader's memory both say so */
  const LP_MOUNT_RISE = 28;   /* px a mounting page rises while it dissolves in (enter=mount) */
  const LP_RETRACT = { COLOURS: 1.0, CHARCOAL: 1.0, IN: 1.6, TURNS: 3.0, LAG: 0.25, ALPHA: 0.85, RECT_FADE: 0.3 };   /* operator: "a way tighter vortex, almost celestial" - three turns, the core spinning four times the rim */
  const lpVortex = (x, y, c, Rmax, u) => {
    const dx = x - c.x, dy = y - c.y, r = Math.hypot(dx, dy) || 1e-6, phi = Math.atan2(dy, dx), rn = Math.min(1, r / Rmax);
    const ui = clamp01((u - LP_RETRACT.LAG * rn) / (1 - LP_RETRACT.LAG));
    const rr = r * (1 - Math.pow(ui, 1.7)), th = LP_RETRACT.TURNS * 2 * Math.PI * ui * (0.4 + 1.6 * Math.pow(1 - rn, 1.5));   /* the core spins ~4x the rim: spiral arms, not a wheel */
    const a = LP_RETRACT.ALPHA * 4 * ui * (1 - ui), s = Math.pow(1 - ui, 0.7);
    const ang = phi + th;
    const q = scaleBy(s, a);   /* the area-preserving stretch along the tangent (42 s42.3 helper, P43 T4) */
    return { x: c.x + rr * Math.cos(ang), y: c.y + rr * Math.sin(ang), th: th * 180 / Math.PI, tan: ang * 180 / Math.PI + 90, sx: q.sx, sy: q.sy, ui };
  };
  /* a CSS transform (HTML particle, its own centre as origin) and an SVG one (user units) for the same map */
  const lpVortexCss = (v, hx, hy) => "translate(" + (v.x - hx).toFixed(2) + "px," + (v.y - hy).toFixed(2) + "px) rotate(" + v.tan.toFixed(2) + "deg) scale(" + v.sx.toFixed(4) + "," + v.sy.toFixed(4) + ") rotate(" + (v.th - v.tan).toFixed(2) + "deg)";
  const lpVortexSvg = (v, hx, hy) => "translate(" + v.x.toFixed(2) + " " + v.y.toFixed(2) + ") rotate(" + v.tan.toFixed(2) + ") scale(" + v.sx.toFixed(4) + " " + v.sy.toFixed(4) + ") rotate(" + (v.th - v.tan).toFixed(2) + ") translate(" + (-hx).toFixed(2) + " " + (-hy).toFixed(2) + ")";
  const lpHome = (page, el) => {   /* an element's untransformed centre in page px (SVG has no offsetLeft) */
    const pr = page.getBoundingClientRect(), r = el.getBoundingClientRect();
    if (!pr.width || !pr.height) return { x: 0, y: 0 };
    return { x: (r.left - pr.left + r.width / 2) / pr.width * page.offsetWidth, y: (r.top - pr.top + r.height / 2) / pr.height * page.offsetHeight };
  };
  /* the particles, measured once at build (untransformed): page-px ones (glyphs, pills), chart ones (viewBox units),
     and the drain in each space - the chart's meet mapping and the field's stretch mapping are inverted from the page */
  /* P48 (operator, 2026-09-10: "the swirl should take the whole drawn chart with it; the swirl leads to a clean plate"): the
     vortex drains the ACTIVE chart state - after a rescale or an extend that is the derived state, not the page's own - while
     the glyphs and pills it drains are the page's (shared by every state). Particles are cached per state. */
  const lpParticles = (st, page, S) => {
    S = S || st;
    const glyphs = [...st.glyphs, ...(st.rtGlyphs || [])].map((g) => ({ el: g, ...lpHome(page, g) }));   /* P47 T2: a retitle's glyphs ride the vortex too */
    const pills = (st.badges || []).map((b) => ({ el: b.el, ...lpHome(page, b.el) }));
    const skip = new Set([...S.paths.map((p) => p.p), ...S.paths.map((p) => p.tip)]);
    const svg = [...S.chart.children].filter((e) => !skip.has(e) && e.tagName !== "defs").map((e) => {
      let b; try { b = e.getBBox(); } catch (x) { b = { x: 0, y: 0, width: 0, height: 0 }; }
      return { el: e, x: b.x + b.width / 2, y: b.y + b.height / 2 };
    });
    const c = { x: page.offsetWidth * st.boardCentre.x / 100, y: page.offsetHeight * st.boardCentre.y / 100 };
    const pr = page.getBoundingClientRect(), cr = S.chart.getBoundingClientRect(), vb = S.chart.viewBox.baseVal;
    const cw = cr.width / pr.width * page.offsetWidth, ch = cr.height / pr.height * page.offsetHeight;
    const cx0 = (cr.left - pr.left) / pr.width * page.offsetWidth, cy0 = (cr.top - pr.top) / pr.height * page.offsetHeight;
    const k = Math.min(cw / (vb.width || 1), ch / (vb.height || 1)) || 1;   /* xMidYMid meet */
    const cChart = { x: (c.x - cx0 - (cw - vb.width * k) / 2) / k, y: (c.y - cy0 - (ch - vb.height * k) / 2) / k };
    const fr = st.field.getBoundingClientRect(), fsvg = st.field.querySelector("svg"), fvb = fsvg ? fsvg.viewBox.baseVal : { width: 1690, height: 907 };
    const cField = { x: (c.x - (fr.left - pr.left) / pr.width * page.offsetWidth) / (fr.width / pr.width * page.offsetWidth || 1) * fvb.width,
                     y: (c.y - (fr.top - pr.top) / pr.height * page.offsetHeight) / (fr.height / pr.height * page.offsetHeight || 1) * fvb.height };
    const Rpage = Math.hypot(page.offsetWidth, page.offsetHeight) / 2;
    return { glyphs, pills, svg, c, cChart, cField, Rpage, Rchart: Rpage / k, Rfield: Math.hypot(fvb.width, fvb.height) / 2 };
  };
  const lpSpiral = (st, scene, t, pg) => {
    const a = scene.span ? scene.span[0] : 0, z = scene.span ? scene.span[1] : Infinity;
    let uc = 0, uf = 0;   /* how far the colours, the field, are down the drain */
    const to = t - (z - LP_RETRACT.COLOURS - LP_RETRACT.CHARCOAL);
    if (pg.exit !== "cut" && to > 0) { uc = clamp01(to / LP_RETRACT.COLOURS); uf = clamp01((to - LP_RETRACT.COLOURS) / LP_RETRACT.CHARCOAL); }
    if (pg.enter === "spiral") {   /* the field surfaces first, the colours follow */
      const ui = clamp01((t - a) / LP_RETRACT.IN);
      uf = Math.max(uf, 1 - clamp01(ui / 0.55)); uc = Math.max(uc, 1 - clamp01((ui - 0.4) / 0.6));   /* the stains surface over the first 0.9 s, the colours unwind over the last 1 s */
    }
    const on = uc > 0 || uf > 0;
    const S = (st.states && st.states[st.active | 0]) || st;   /* the chart the drain takes: the active state's */
    if (!on && !S.spiralOn) return;   /* idle: touch no style, read no layout (either re-snaps text a sub-pixel on the punched page) */
    S.spiralOn = on;
    if (!S.parts) S.parts = lpParticles(st, st.page, S);
    const P = S.parts;
    for (const g of P.glyphs) g.el.style.transform = uc > 0 ? lpVortexCss(lpVortex(g.x, g.y, P.c, P.Rpage, uc), g.x, g.y) + " rotate(var(--tilt))" : "";
    for (const p of P.pills) if (uc > 0) p.el.style.transform = lpVortexCss(lpVortex(p.x, p.y, P.c, P.Rpage, uc), p.x, p.y);
    for (const q of P.svg) {
      if (uc > 0) { const v = lpVortex(q.x, q.y, P.cChart, P.Rchart, uc); q.el.style.transformOrigin = ""; q.el.style.transform = ""; q.el.setAttribute("transform", lpVortexSvg(v, q.x, q.y)); }
      else q.el.removeAttribute("transform");
    }
    /* the series line curls in point by point; the tips hide */
    S.paths.forEach((pp, i) => {
      const pts = (S.linePts || [])[i];
      if (!pts) return;
      if (uc > 0) {
        const d = pts.map(([x, y], k) => { const v = lpVortex(x, y, P.cChart, P.Rchart, uc); return (k ? "L" : "M") + v.x.toFixed(1) + " " + v.y.toFixed(1); }).join(" ");
        pp.p.setAttribute("d", d); pp.p.setAttribute("stroke-dashoffset", 0); pp.p.style.strokeWidth = (8 * Math.pow(1 - Math.min(1, uc * 1.15), 0.7) + 0.5).toFixed(2) + "px"; pp.tip.style.display = "none";
      } else { pp.p.setAttribute("d", pts.map(([x, y], k) => (k ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ")); pp.p.style.strokeWidth = ""; pp.tip.style.display = ""; }
    });
    /* phase two: the crisp charcoal fades to the stains beneath, and the stains go down the drain */
    st.rect.style.opacity = uf > 0 ? (1 - clamp01(uf / LP_RETRACT.RECT_FADE)).toFixed(3) : "";
    if (st.fieldPlate) st.fieldPlate.style.opacity = uf > 0 ? (1 - clamp01(uf / LP_RETRACT.RECT_FADE)).toFixed(3) : st.fieldPlate.style.opacity;
    for (const bl of st.blobs) {
      if (uf > 0) { const v = lpVortex(bl.cx, bl.cy, P.cField, P.Rfield, uf); bl.c.setAttribute("transform", "translate(" + v.x.toFixed(1) + " " + v.y.toFixed(1) + ") rotate(" + v.th.toFixed(1) + ") scale(" + (bl.R * v.sx).toFixed(2) + " " + (bl.R * v.sy).toFixed(2) + ")"); }
      /* else: the soak beat has already painted the blob's home transform this frame */
    }
    for (const sk of st.strokes || []) sk.p.style.opacity = uf > 0 ? (1 - uf).toFixed(3) : "";
  };
  /* ================= BUILD-ON (P47 T2; operator 2026-09-06: "we're being a bit too lazy with the world plates ... perform some
     transformations on the chart"; SHOT-TABLE-V3-PROPOSAL part B). The page performs on a WORD: three PAGE species authored in the
     scene's species list, painted here on the page's own surfaces (never in the overlay), every one a pure function of t.
       build_to {at, dur, target: datum}  - the drawn series is CAPPED at the datum: the build beat is spent on the first cap
                                            (the line draws to the February peak and stops), and each later build_to draws
                                            from the previous cap to its own on its word, the same stroke, the nib visible.
       bracket  {at, dur, from, to, label, sub?, series?, color?} - a measured vertical span between two data, beside them in
                                            the plot's own room (the infographic's bracket): the span line draws by min-jerk,
                                            the ticks land by the spring, the label writes in the hand, glyph by glyph.
       retitle  {at, dur, text}           - the title erases glyph by glyph over PS.ERASE_S, then the new title writes per
                                            glyph as the build did. A page may retitle more than once.
       relight  {at, dur, ref: bracket|title, index?} - re-fires a bracket (or the title) in the sunflower on a word: a
                                            sunflower twin beneath it rises and falls on a sine, the base never moves.
     Dials, ours (42 s42.5): ERASE_S the title's wipe; BRACKET_DRAW / TICK / LABEL the bracket's phases as shares of its dur;
     BRACKET_GAP the room between the data and the span, viewBox units. */
  const PS = { SPREAD_A: 0.30, SPREAD_BLEED: 0.55,   /* the fifth watch: the gap between two lines, bled full of ink - the alpha it lands at, and the share of the word the bleed takes to cross */
               ERASE_S: 0.4, BRACKET_DRAW: 0.5, BRACKET_TICK: 0.15, BRACKET_LABEL: 0.55, BRACKET_GAP: 34, BRACKET_TICK_W: 14,
               BRACKET_BAR_W: 26,   /* P50 T9: `form: "bar"` - the SAME span, drawn as a bar in the accent instead of a hairline (Bravos shot 36: the drop of one tier). The law is the bracket's: the bar grows from the first datum's level to the second as the span draws, so a fall goes DOWN (E28) */
               BRACKET_ROOM: 200, RELIGHT_COL: "#F5B72E" };
  const PS_PAL = { crimson: "#ED6A4A", teal: "#178C83", cobalt: "#8fb3f0", amber: "#F5B72E", deemph: "#b8c4d0", neg: "var(--lp-neg)", pos: "var(--lp-pos)" };
  const pageSpecies = (scene, kind) => (scene.species || []).filter((sp) => sp && sp.kind === kind).sort((a, b) => a.at - b.at);
  const polyLenTo = (pts, i) => { let L = 0; for (let k = 1; k <= i && k < pts.length; k++) L += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]); return L; };
  /* the length fraction of a drawn path up to a series datum index (a highlighted tail is offset by its k0; an index before
     the tail's first point caps it at nothing) */
  const capFrac = (pp, index) => {
    const pts = pp.pts || []; if (pts.length < 2) return 1;
    const i = Math.max(0, Math.min(pts.length - 1, (index | 0) - (pp.k0 || 0))), tot = polyLenTo(pts, pts.length - 1);
    return tot > 0 ? polyLenTo(pts, i) / tot : 1;
  };
  const segEase = (u) => (kin("min_jerk") ? minJerk(u) : expoOut(clamp01(u)));
  const buildPerform = (st, scene, pg) => {
    const P = !!st.portrait, fs = P ? 40 : 26, fss = P ? 32 : 20, G = st.geom || { W: 1000, H: 560 };
    /* P48 T7: on a page with chart STATES the perform layer (brackets, figures, spreads) draws on its OWN svg above every
       state - inside state 0's svg it vanished with it the moment a rescale made the derived state active (the Tokyo cut's
       two treasury figures). A figure then follows the ACTIVE state's datum (paintFigure); a bracket or spread is built on
       the page's own geometry and waits while a derived state stands. A page with one chart draws exactly as it did. */
    if ((st.states || []).length > 1 && !st.performSvg) {
      st.performSvg = lpEl("svg", "lp-chart lp-perform", st.page, { viewBox: st.chart.getAttribute("viewBox") });
      st.performSvg.style.cssText = st.chart.style.cssText; st.performSvg.style.pointerEvents = "none";
      st.performSvg.style.opacity = ""; st.performSvg.style.transform = ""; st.performSvg.style.transformOrigin = "";   /* the box, not the chart's current state (a cold seek past a rescale copied opacity 0) */
    }
    const surf = st.performSvg || st.chart;
    const brackets = pageSpecies(scene, "bracket").map((sp, bi) => {
      const pts = (st.linePts || [])[sp.series | 0] || [];
      if (pts.length < 2) return null;
      const A = pts[Math.max(0, Math.min(pts.length - 1, sp.from | 0))], B = pts[Math.max(0, Math.min(pts.length - 1, sp.to | 0))];
      /* the span stands to the RIGHT of the two data (the ticks point back at them); when the chart's room there is too
         narrow for the label (a series ending at the right edge - the holdings page), the label writes ABOVE the span,
         anchored to it, where a peak has nothing over it - never over the line's own history to the left */
      /* the span stands to the RIGHT of the two data (the ticks point back at them); when the chart's room there is too
         narrow for the label, the label writes ABOVE the span. The geometry is a FUNCTION of the two anchors and the
         series' points, so it can be re-read every frame on a page whose chart changes state (R26-28) */
      const geomOf = (Ap, Bp, ptsNow) => {
        const xr = Math.max(Ap[0], Bp[0]) + PS.BRACKET_GAP, fits = xr + PS.BRACKET_ROOM <= G.W, inMargin = xr <= G.W;
        const x = inMargin ? xr : Math.min(Ap[0], Bp[0]) - PS.BRACKET_GAP, dir = inMargin ? -1 : 1;
        const y0 = Math.min(Ap[1], Bp[1]), y1 = Math.max(Ap[1], Bp[1]), ym = (y0 + y1) / 2;
        const yClear = Math.min(y0, ...ptsNow.map((q) => q[1]));   /* a stacked label clears the WHOLE series - a record before the span can stand higher than the span's top */
        const half = sp.form === "bar" ? PS.BRACKET_BAR_W / 2 : 0;   /* P50 T9: a bar has width, and its label is written clear of it, not on it */
        const lx = fits ? x + 12 + half : x - 4 - half, ly = fits ? ym + fs * 0.35 : yClear - (sp.sub ? fss * 1.3 : 0) - 10;   /* beside, or stacked above the whole line */
        return { x, dir, fits, anchor: fits ? "start" : "end", y0, y1, lx, ly, sy: fits ? ly + fss * 1.3 : yClear - 10 };
      };
      const g0 = geomOf(A, B, pts);
      const base = st.paths.filter((pp) => (pp.si | 0) === (sp.series | 0) && !pp.muted).map((pp) => pp.p.getAttribute("stroke"))[0] || "var(--lp-chalk)";
      const col = sp.color ? (PS_PAL[sp.color] || sp.color) : base;
      const applyGeom = (side, q) => {   /* write a geometry onto a side's elements (the build's and every re-read frame's) */
        side.line.setAttribute("d", "M" + q.x.toFixed(1) + " " + q.y0.toFixed(1) + " L" + q.x.toFixed(1) + " " + q.y1.toFixed(1));
        side.len = side.line.getTotalLength ? side.line.getTotalLength() : (q.y1 - q.y0);
        side.line.setAttribute("stroke-dasharray", side.len);
        side.t0.setAttribute("d", "M" + q.x.toFixed(1) + " " + q.y0.toFixed(1) + " l" + (q.dir * PS.BRACKET_TICK_W).toFixed(1) + " 0"); side.t0.setAttribute("transform-origin", q.x.toFixed(1) + "px " + q.y0.toFixed(1) + "px");
        side.t1.setAttribute("d", "M" + q.x.toFixed(1) + " " + q.y1.toFixed(1) + " l" + (q.dir * PS.BRACKET_TICK_W).toFixed(1) + " 0"); side.t1.setAttribute("transform-origin", q.x.toFixed(1) + "px " + q.y1.toFixed(1) + "px");
        side.label.setAttribute("x", q.lx.toFixed(1)); side.label.setAttribute("y", q.ly.toFixed(1)); side.label.setAttribute("text-anchor", q.anchor);
        if (side.sub) { side.sub.setAttribute("x", q.lx.toFixed(1)); side.sub.setAttribute("y", q.sy.toFixed(1)); side.sub.setAttribute("text-anchor", q.anchor); }
      };
      const mk = (cls, stroke, op) => {
        const g = lpEl("g", "lp-bracket " + cls, surf, { opacity: op });
        const line = lpEl("path", "bk", g, { d: "M" + g0.x.toFixed(1) + " " + g0.y0.toFixed(1) + " L" + g0.x.toFixed(1) + " " + g0.y1.toFixed(1), stroke });
        if (sp.form === "bar") { line.style.strokeWidth = (P ? PS.BRACKET_BAR_W * 1.7 : PS.BRACKET_BAR_W) + "px"; line.style.strokeLinecap = "butt"; line.style.opacity = "0.92"; }
        const len = line.getTotalLength ? line.getTotalLength() : (g0.y1 - g0.y0);
        line.setAttribute("stroke-dasharray", len); line.setAttribute("stroke-dashoffset", len);
        const tick = (y) => lpEl("path", "bk", g, { d: "M" + g0.x.toFixed(1) + " " + y.toFixed(1) + " l" + (g0.dir * PS.BRACKET_TICK_W).toFixed(1) + " 0", stroke, "transform-origin": g0.x.toFixed(1) + "px " + y.toFixed(1) + "px" });
        const t0 = tick(g0.y0), t1 = tick(g0.y1);
        const label = lpEl("text", "bklab", g, { x: g0.lx.toFixed(1), y: g0.ly.toFixed(1), "text-anchor": g0.anchor, style: "font-size:" + fs + "px;fill:" + stroke });   /* inline fill: the chart's class CSS outranks a fill attribute */
        const lg = [...String(sp.label || "")].map((ch) => { const ts = lpEl("tspan", "", label, { opacity: 0 }); ts.textContent = ch === " " ? "\u00a0" : ch; return ts; });
        let sub = null, sg = [];
        if (sp.sub) { sub = lpEl("text", "bksub", g, { x: g0.lx.toFixed(1), y: g0.sy.toFixed(1), "text-anchor": g0.anchor, style: "font-size:" + fss + "px;fill:" + stroke });
          sg = [...String(sp.sub)].map((ch) => { const ts = lpEl("tspan", "", sub, { opacity: 0 }); ts.textContent = ch === " " ? "\u00a0" : ch; return ts; }); }
        return { g, line, len, t0, t1, label, lg, sub, sg };
      };
      const main = mk("main", col, 0), glow = mk("glow", PS.RELIGHT_COL, 0);   /* the sunflower twin ABOVE the base: at full it covers span and label alike */
      return { sp, x: g0.x, y0: g0.y0, y1: g0.y1, A, B, fits: g0.fits, main, glow, bi, si: sp.series | 0, geomOf, applyGeom, key: "" };
    }).filter(Boolean);
    const retitles = pageSpecies(scene, "retitle").map((sp, ri) => {
      const div = lpEl("div", "lp-ink lp-title lp-retitle", st.page);
      if (st.titleEl && st.titleEl.getAttribute("style")) div.setAttribute("style", st.titleEl.getAttribute("style"));   /* the title's inline geometry (portrait sets it): the rewrite sits exactly where the title sat */
      const glyphs = P ? lpGlyphsWrap(div, String(sp.text || ""), st.seed + 40 + ri) : lpGlyphs(div, String(sp.text || ""), st.seed + 40 + ri);
      (st.rtGlyphs || (st.rtGlyphs = [])).push(...glyphs);
      return { sp, div, glyphs };
    });
    /* E50 (P47 T6): a FIGURE - the number the sentence turns to, pinned to its datum by a dot and written by the hand beside
       it (to the right when the chart has room there, else to the left - a peak at the right edge writes leftward); `dy` moves
       it by lines of its own size; `sub` writes under it at the small size. The chart's next thing after an undraw. */
    const figures = pageSpecies(scene, "figure").map((sp, fi) => {
      const pts = (st.linePts || [])[sp.series | 0] || [];
      if (!pts.length) return null;
      const i = Math.max(0, Math.min(pts.length - 1, ((sp.target || {}).index | 0))), D = pts[i];
      /* a figure is ink on the page: the chalk unless a colour is named (an emphasised page's unmuted stroke is its coral tail) */
      const col = sp.color ? (PS_PAL[sp.color] || sp.color) : "var(--lp-chalk)";
      const fits = D[0] + PS.BRACKET_GAP + PS.BRACKET_ROOM <= G.W;
      const x = fits ? D[0] + 14 : D[0] - 14, anchor = fits ? "start" : "end";
      const y = D[1] + fs * 0.35 + (Number(sp.dy) || 0) * fs * 1.2;
      const g = lpEl("g", "lp-figure", surf, { opacity: 0 });   /* no pin dot: the figure stands where the line was (the third watch: lingering dots read as strange) */
      const label = lpEl("text", "bklab", g, { x: x.toFixed(1), y: y.toFixed(1), "text-anchor": anchor, style: "font-size:" + fs + "px;fill:" + col });
      const lg = [...String(sp.text || "")].map((ch) => { const ts = lpEl("tspan", "", label, { opacity: 0 }); ts.textContent = ch === " " ? "\u00a0" : ch; return ts; });
      let sub = null, sg = [];
      if (sp.sub) { sub = lpEl("text", "bksub", g, { x: x.toFixed(1), y: (y + fss * 1.3).toFixed(1), "text-anchor": anchor, style: "font-size:" + fss + "px;fill:" + col });
        sg = [...String(sp.sub)].map((ch) => { const ts = lpEl("tspan", "", sub, { opacity: 0 }); ts.textContent = ch === " " ? "\u00a0" : ch; return ts; }); }
      return { sp, D, x, y, fits, g, label, lg, sub, sg, fi, fs, fss, W: G.W, si: sp.series | 0, idx: i };
    }).filter(Boolean);
    /* NOTES (the third watch: "the page has plenty of space on the side to write things"): a line of handwriting in the page's
       QUIET ZONE beside the chart - the column the chart leaves free (the dock's band) - stacked in order, each written on its
       word by the hand at the sub's size; when the chart has no free column the notes stack under the source line */
    const notes = pageSpecies(scene, "note").map((sp, ni) => {
      const div = lpEl("div", "lp-ink lp-sub lp-note", st.page);
      const pr = st.page.getBoundingClientRect(), cr = st.chart.getBoundingClientRect();   /* the chart's box as % of the page (an SVG has no offsets; the ratios survive any transform) */
      const cl = (cr.x - pr.x) / pr.width * 100, cw = cr.width / pr.width * 100, ct = (cr.y - pr.y) / pr.height * 100, chh = cr.height / pr.height * 100;
      const right = 100 - (cl + cw), left = cl;
      const step = P ? 7.0 : 8.5;   /* % of the page per note (one wrapped line and a breath) */
      if (right >= 22) { div.style.left = (cl + cw + 3).toFixed(2) + "%"; div.style.width = (right - 7).toFixed(2) + "%"; div.style.top = (ct + 2 + ni * step).toFixed(2) + "%"; }
      else if (left >= 22) { div.style.left = "4%"; div.style.width = (left - 7).toFixed(2) + "%"; div.style.top = (ct + 2 + ni * step).toFixed(2) + "%"; }
      else { div.style.left = cl.toFixed(2) + "%"; div.style.width = cw.toFixed(2) + "%"; div.style.top = (ct + chh + (P ? 17 : 12) + ni * step * 0.75).toFixed(2) + "%"; }   /* no free column: under the source line and the caption band */
      const glyphs = P ? lpGlyphsWrap(div, String(sp.text || ""), st.seed + 70 + ni) : lpGlyphs(div, String(sp.text || ""), st.seed + 70 + ni);
      return { sp, div, glyphs };
    });
    /* THE SPREAD (the fifth watch, 2026-09-07 - the operator: "bleed the chart fill to red beneath the 10 year line and the
       fed rate"). The region between two drawn series, filled with the page's ink on a word: what the Fed charges against what
       America pays, and the gap between them made visible. The polygon is rebuilt per frame from the two series' own points,
       so the fill BLEEDS left to right at the pen's pace and a seek is still the play. */
    const spreads = pageSpecies(scene, "spread").map((sp) => {
      const A = (st.linePts || [])[sp.from | 0];
      /* `to` is a second series; `to_rule` is a REFERENCE RULE's index (a policy rate is a constant, so the gap is the area
         between the drawn line and the rule) - the fifth watch */
      const rule = Number.isInteger(sp.to_rule) ? (st.hlines || [])[sp.to_rule] : null;
      const B = rule ? [[-1e9, rule.y], [1e9, rule.y]] : (st.linePts || [])[sp.to | 0];
      if (!A || !B || A.length < 2 || B.length < 2) return null;
      const hi0 = A.length >= B.length ? A : B, lo = hi0 === A ? B : A;   /* walk the denser series; read the other at its x */
      const hi = Number.isInteger(sp.from_index) ? hi0.slice(Math.max(0, Math.min(hi0.length - 2, sp.from_index))) : hi0;   /* the fill may BEGIN at a datum - where the argument does */
      const yAt = (pts, x) => { let i = 1; while (i < pts.length - 1 && pts[i][0] < x) i++;
        const [x0, y0] = pts[i - 1], [x1, y1] = pts[i]; return x1 === x0 ? y1 : y0 + (y1 - y0) * ((x - x0) / (x1 - x0)); };
      const col = PS_PAL[sp.color] || sp.color || "var(--lp-neg)";
      const path = lpEl("path", "lp-spread", surf, { fill: col, "fill-opacity": 0, stroke: "none" });
      surf.insertBefore(path, surf.firstChild);   /* under every line and label: it is ground, not ink on top */
      return { sp, hi, lo, path };
    }).filter(Boolean);
    /* THE SPAN (P50 T4; R26-25, the intake's Archetype 5; Bravos 107-110's "Decades"). A shaded stretch of TIME
       behind the chart with its NAME above it. The geometry is not built here: species/span.mjs rebuilds the band
       from the LIVE points every frame (spanBand), so the span follows a rescale and hides when a window drops one
       of its edges - the same clock and the same live scale a bracket follows (R26-28). The shade is ground, under
       every line; the name is ink, on top, written glyph by glyph by the hand. */
    const spans = pageSpecies(scene, "span").map((sp) => {
      const col = sp.color ? (PS_PAL[sp.color] || sp.color) : "var(--lp-chalk)";
      const rect = lpEl("rect", "lp-span", surf, { x: 0, y: 0, width: 0, height: 0, fill: col, "fill-opacity": 0 });
      surf.insertBefore(rect, surf.firstChild);
      const label = lpEl("text", "spanlab", surf, { x: 0, y: 0, "text-anchor": "middle", opacity: 0, style: "font-size:" + fs + "px;fill:" + col });
      const lg = [...String(sp.label || "")].map((ch) => { const ts = lpEl("tspan", "", label, { opacity: 0 }); ts.textContent = ch === " " ? "\u00a0" : ch; return ts; });
      return { sp, si: sp.series | 0, rect, label, lg, fs };
    });
    /* THE CENSUS'S X MARKS (P50 T6; E53 s1's second amendment, 2026-09-10; Bravos shots 89-91). The
       named cells take an X and dim; the crossed SHARE is written by the hand above the map. Both halves
       are ONE species because the exception is one act: (a) the subset is marked AND (b) its share is
       written as a number. species/treemap.mjs owns the geometry and the clock. */
    const crosses = pageSpecies(scene, "cross").map((sp) => {
      const TM = st.treemap; if (!TM) return null;   /* the compiler refuses a cross off a treemap page; a page that lost its map draws nothing */
      const col = sp.color ? (PS_PAL[sp.color] || sp.color) : PS.RELIGHT_COL;   /* sunflower, the chip's own cross */
      const marks = treemapNamed(TM.cells, sp.cells).map((ci) => {
        const cell = TM.cells[ci];
        const strokes = treemapCrossLines(cell.rect).map((ln) => {
          const p = lpEl("path", "bk", surf, { d: "M" + ln.x1.toFixed(1) + " " + ln.y1.toFixed(1) + " L" + ln.x2.toFixed(1) + " " + ln.y2.toFixed(1),
                                               stroke: col, opacity: 0 });
          p.style.strokeWidth = (st.portrait ? 11 : 7) + "px"; p.style.strokeLinecap = "round";
          const len = p.getTotalLength ? p.getTotalLength() : Math.hypot(ln.x2 - ln.x1, ln.y2 - ln.y1);
          p.setAttribute("stroke-dasharray", len); p.setAttribute("stroke-dashoffset", len);
          return { p, len };
        });
        return { cell, strokes };
      });
      const label = lpText(surf, "bklab", TM.plot.x, TM.plot.y - (P ? 26 : 16), "start", "",
        { opacity: 0, style: "font-size:" + fs + "px;fill:" + col });
      const lg = [...String(sp.text || "")].map((ch) => { const ts = lpEl("tspan", "", label, { opacity: 0 }); ts.textContent = ch === " " ? "\u00a0" : ch; return ts; });
      return { sp, marks, label, lg };
    }).filter(Boolean);
    return { brackets, retitles, relights: pageSpecies(scene, "relight"), figures, notes, spreads, spans, crosses };
  };
  /* the X's two strokes over the named cells, the cells dimming under them, and the share written by
     the hand: every number is species/treemap.mjs's, this is the call */
  const paintCross = (cr, t) => {
    const f = treemapCrossF(cr.sp, t), sk = treemapStrokes(f), dim = treemapDim(f);
    for (const m of cr.marks) {
      m.strokes.forEach((s, j) => {
        s.p.setAttribute("opacity", sk[j] > 0 ? 1 : 0);
        s.p.setAttribute("stroke-dashoffset", (s.len * (1 - sk[j])).toFixed(1));
      });
      m.cell.box.style.opacity = f > 0 ? dim.toFixed(3) : "";   /* the FILL dims, never the name: E53 s1's census (c) says the crossed cell is read, and a struck cell is still counted */
    }
    cr.label.setAttribute("opacity", t >= cr.sp.at ? 1 : 0);
    const w = treemapWrite(cr.sp, t);
    cr.lg.forEach((ts, j) => ts.setAttribute("opacity", treemapGlyph(w, j, cr.lg.length).toFixed(3)));
  };
  /* the bleed: the region grows left to right over SPREAD_BLEED of the word, the ink deepens over the rest */
  const paintSpread = (sd, t, st) => {
    const sp = sd.sp, dur = Math.max(0.001, sp.dur || 1), u = clamp01((t - sp.at) / dur);
    if (u <= 0) { sd.path.setAttribute("fill-opacity", 0); return; }
    let hi = sd.hi, lo = sd.lo;
    if (st && (st.states || []).length > 1) {   /* R26-28: the two edges this frame - the active state's points (lerped across a rescale / extend), the rule's y re-projected */
      const A0 = lpPointsNow(st, sp.from | 0), fromI = Number.isInteger(sp.from_index) ? sp.from_index : -Infinity;
      const A = A0.filter((e) => e.i >= fromI).map((e) => e.p);
      const rule = Number.isInteger(sp.to_rule) ? lpRuleYNow(st, sp.to_rule) : null;
      const B = Number.isInteger(sp.to_rule) ? (rule == null ? null : [[-1e9, rule], [1e9, rule]]) : lpPointsNow(st, sp.to | 0).map((e) => e.p);
      if (!A || !B || A.length < 2 || B.length < 2) { sd.path.setAttribute("fill-opacity", 0); return; }
      const dense = A.length >= B.length ? A : B; hi = dense === A ? A : B; lo = dense === A ? B : A;   /* walk the denser edge; read the other at its x */
      if (Number.isInteger(sp.to_rule)) { hi = A; lo = B; }
    }
    const k = minJerk(clamp01(u / PS.SPREAD_BLEED)), n = hi.length, m = Math.max(2, Math.round(k * n));
    const yAt = (pts, x) => { let i = 1; while (i < pts.length - 1 && pts[i][0] < x) i++;
      const [x0, y0] = pts[i - 1], [x1, y1] = pts[i]; return x1 === x0 ? y1 : y0 + (y1 - y0) * ((x - x0) / (x1 - x0)); };
    const top = [], bot = [];
    for (let i = 0; i < m; i++) { const [x, y] = hi[i]; top.push([x, y]); bot.push([x, yAt(lo, x)]); }
    const d = top.map(([x, y], i) => (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ")
      + bot.reverse().map(([x, y]) => "L" + x.toFixed(1) + " " + y.toFixed(1)).join(" ") + " Z";
    sd.path.setAttribute("d", d);
    sd.path.setAttribute("fill-opacity", (PS.SPREAD_A * clamp01(u / 0.35)).toFixed(3));
  };
  /* the span: the band re-read on the LIVE scale every frame, the shade fading in under the lines, the name written
     above it by the hand (species/span.mjs owns every number; this is the call) */
  const paintSpan = (sd, t, st) => {
    const pose = spanPose(sd.sp, t);
    const hide = () => { sd.rect.setAttribute("fill-opacity", 0); sd.label.setAttribute("opacity", 0); };
    if (!pose.on) { hide(); return; }
    const lists = [];
    for (let i = 0; i < Math.max(1, (st.linePts || []).length); i++) lists.push(lpPointsNow(st, i));
    const band = spanBand(lists[sd.si] || [], lists, sd.sp.from, sd.sp.to, (st.geom || {}).H);
    if (!band) { hide(); return; }   /* R26-28: an edge the window dropped names nothing - nothing is drawn */
    sd.rect.setAttribute("x", band.x.toFixed(1)); sd.rect.setAttribute("y", band.y.toFixed(1));
    sd.rect.setAttribute("width", band.w.toFixed(1)); sd.rect.setAttribute("height", band.h.toFixed(1));
    sd.rect.setAttribute("fill-opacity", pose.alpha.toFixed(3));
    sd.label.setAttribute("opacity", 1);
    sd.label.setAttribute("x", band.cx.toFixed(1));
    sd.label.setAttribute("y", spanLabelY(band, sd.fs).toFixed(1));
    sd.lg.forEach((ts, j) => ts.setAttribute("opacity", spanGlyph(pose.write, j, sd.lg.length).toFixed(3)));
  };
  /* the figure's write: the figure writes glyph by glyph over the first 0.6 of its word, the sub over the rest */
  const paintFigure = (fg, t, st) => {
    const sp = fg.sp, dur = Math.max(0.001, sp.dur || 1), u = clamp01((t - sp.at) / dur);
    fg.g.setAttribute("opacity", t >= sp.at ? 1 : 0);
    if (st && (st.states || []).length > 1) {   /* P48 T7: the figure stands at its datum on the ACTIVE state - a datum the window dropped shows nothing */
      const D = lpMarkDatum(st, fg.si, fg.idx);
      if (!D) { fg.g.setAttribute("opacity", 0); return; }
      const fits = D[0] + PS.BRACKET_GAP + PS.BRACKET_ROOM <= fg.W, x = fits ? D[0] + 14 : D[0] - 14, anchor = fits ? "start" : "end";
      const y = D[1] + fg.fs * 0.35 + (Number(sp.dy) || 0) * fg.fs * 1.2;
      fg.label.setAttribute("x", x.toFixed(1)); fg.label.setAttribute("y", y.toFixed(1)); fg.label.setAttribute("text-anchor", anchor);
      if (fg.sub) { fg.sub.setAttribute("x", x.toFixed(1)); fg.sub.setAttribute("y", (y + fg.fss * 1.3).toFixed(1)); fg.sub.setAttribute("text-anchor", anchor); }
      fg.D = D; fg.x = x; fg.y = y; fg.fits = fits;
    }
    const nl = Math.max(1, fg.lg.length), perL = 0.6 / nl, uL = u;
    fg.lg.forEach((ts, j) => ts.setAttribute("opacity", clamp01((uL - j * perL) / (perL * 1.6)).toFixed(3)));
    const ns = Math.max(1, fg.sg.length), perS = 0.4 / ns, uS = u - 0.6;
    fg.sg.forEach((ts, j) => ts.setAttribute("opacity", clamp01((uS - j * perS) / (perS * 1.6)).toFixed(3)));
  };
  const paintBracket = (b, t, ud, st) => {
    const sp = b.sp, dur = Math.max(0.001, sp.dur || 1);
    if (st && (st.states || []).length > 1) {   /* R26-28: the two anchors and the series' points, this frame, on the active state (lerped across a rescale / extend) */
      const Ap = lpDatumNow(st, b.si, sp.from | 0), Bp = lpDatumNow(st, b.si, sp.to | 0);
      if (!Ap || !Bp) { b.main.g.setAttribute("opacity", 0); b.glow.g.setAttribute("opacity", 0); b.hidden = true; return; }   /* a datum the window dropped: nothing to measure */
      b.hidden = false;
      const q = b.geomOf(Ap, Bp, lpPointsNow(st, b.si).map((e) => e.p)), key = [q.x, q.y0, q.y1, q.lx, q.ly, q.anchor].map((v) => typeof v === "number" ? v.toFixed(1) : v).join("|");
      if (key !== b.key) { b.applyGeom(b.main, q); b.applyGeom(b.glow, q); b.key = key; b.x = q.x; b.y0 = q.y0; b.y1 = q.y1; b.fits = q.fits; }
    }
    let u = clamp01((t - sp.at) / dur);
    /* E50: an UNDRAW (no series named) after the bracket's word takes the bracket with the line - the label un-writes,
       the ticks shrink, the span retracts, on the undraw's own clock */
    if (ud && t >= ud.at && ud.at >= sp.at) u = Math.min(u, 1 - segEase(clamp01((t - ud.at) / Math.max(0.001, ud.dur || 1))));
    for (const side of [b.main, b.glow]) {
      const draw = segEase(u / PS.BRACKET_DRAW);
      side.line.setAttribute("stroke-dashoffset", (side.len * (1 - draw)).toFixed(1));
      const tk = (kin("analytic_spring") ? springPop : stagePop)(clamp01((u - PS.BRACKET_DRAW) / PS.BRACKET_TICK));
      for (const tp of [side.t0, side.t1]) tp.setAttribute("transform", "scale(" + tk.toFixed(4) + " 1)");
      const nl = Math.max(1, side.lg.length), perL = (1 - PS.BRACKET_LABEL) * 0.7 / nl, uL = u - PS.BRACKET_LABEL;
      side.lg.forEach((ts, j) => ts.setAttribute("opacity", clamp01((uL - j * perL) / (perL * 1.6)).toFixed(3)));
      const ns = Math.max(1, side.sg.length), perS = (1 - PS.BRACKET_LABEL) * 0.3 / ns, uS = u - PS.BRACKET_LABEL - (1 - PS.BRACKET_LABEL) * 0.7;
      side.sg.forEach((ts, j) => ts.setAttribute("opacity", clamp01((uS - j * perS) / (perS * 1.6)).toFixed(3)));
    }
    b.main.g.setAttribute("opacity", t >= sp.at ? 1 : 0);
  };
  /* the title glyphs' write-on: --w per glyph on a clock, the build's own stagger (per = share of the write per glyph) */
  const writeGlyphs = (glyphs, tw, span) => { const n = Math.max(1, glyphs.length), per = span / n; glyphs.forEach((g, j) => g.style.setProperty("--w", clamp01((tw - j * per) / (per * 1.6)).toFixed(3))); };
  /* an erase runs the wipe backwards, glyph after glyph, over ERASE_S: the factor each glyph's --w is multiplied by */
  const eraseFactor = (n, j, ue) => 1 - clamp01((ue * (n + 3) - j) / 3);
  const paintPerform = (st, scene, t, pg) => {
    if (!st.perform) st.perform = buildPerform(st, scene, pg);
    const PF = st.perform;
    if (st.performSvg && st.states) {   /* P48 T7: the perform layer rides the active chart's park - copied HERE, after the layer exists, so a cold seek into a park paints it parked on its first frame */
      const A = st.states[st.active | 0]; st.performSvg.style.transformOrigin = A.chart.style.transformOrigin; st.performSvg.style.transform = A.chart.style.transform;
    }
    const undrawAll = [...pageSpecies(scene, "undraw").filter((sp) => (sp.series ?? (sp.target || {}).series) == null),
                       ...pageSpecies(scene, "chart_to").filter((sp) => sp.to === "recast" || sp.to === "morph")];   /* P48 T7: a recast or morph takes the line - the bracket leaves with it, on the same clock */
    for (const b of PF.brackets) paintBracket(b, t, undrawAll.find((sp) => sp.at >= b.sp.at), st);
    for (const sd of PF.spreads || []) paintSpread(sd, t, st);   /* the fifth watch: the gap between the lines, bled full; R26-28: on the active state */
    for (const sd of PF.spans || []) paintSpan(sd, t, st);       /* P50 T4: the named stretch of time, shaded behind the chart on the live scale */
    for (const fg of PF.figures || []) paintFigure(fg, t, st);   /* E50: the chart's next thing */
    for (const cr of PF.crosses || []) paintCross(cr, t);        /* P50 T6: the census's X marks and the share they cross */
    for (const nt of PF.notes || []) { nt.div.style.opacity = t >= nt.sp.at ? "" : "0"; writeGlyphs(nt.glyphs, t - nt.sp.at, Math.max(0.05, nt.sp.dur || 1)); }
    /* RELIGHT: the sunflower twin rises and falls on a sine over dur */
    for (const b of PF.brackets) b.glow.g.setAttribute("opacity", "0");
    for (const rl of PF.relights) {
      const u = (t - rl.at) / Math.max(0.001, rl.dur || 1); if (u < 0 || u > 1) continue;
      const e = Math.sin(Math.PI * u);
      if (rl.ref === "bracket") { const b = PF.brackets[rl.index | 0]; if (b) b.glow.g.setAttribute("opacity", e.toFixed(3)); }
      else if (rl.ref === "title") { const tg = PF.retitles.length ? PF.retitles[PF.retitles.length - 1].glyphs : (st.titleGlyphs || []); for (const g of tg) g.style.color = e > 0.02 ? PS.RELIGHT_COL : ""; }
    }
    for (const b of PF.brackets) if (b.hidden) { b.main.g.setAttribute("opacity", 0); b.glow.g.setAttribute("opacity", 0); }   /* R26-28: a bracket whose data left the window stays hidden through the relight */
    if (PF.retitles.length) {
      const chain = [{ glyphs: st.titleGlyphs || [], at: -Infinity }, ...PF.retitles.map((r) => ({ glyphs: r.glyphs, at: r.sp.at, dur: Math.max(PS.ERASE_S + 0.01, r.sp.dur || 1) }))];
      chain.forEach((c, k) => {
        const next = chain[k + 1];
        if (k > 0) writeGlyphs(c.glyphs, t - c.at - PS.ERASE_S, c.dur - PS.ERASE_S);   /* a retitle writes after its erase of the one before */
        if (next && t >= next.at) {   /* and is erased, glyph by glyph, when the next one fires */
          const ue = clamp01((t - next.at) / PS.ERASE_S), n = c.glyphs.length;
          c.glyphs.forEach((g, j) => g.style.setProperty("--w", (parseFloat(g.style.getPropertyValue("--w") || "0") * eraseFactor(n, j, ue)).toFixed(3)));
        }
      });
    }
  };
  /* ================= THE MORPH (P47 T3; 43 s43.5 method B; E48 s4: the tab as the protagonist) =================
     A page that ENTERS by `morph` carries a named prop outline (world.morph: tab | plate | card) drawn on the board, and over
     MORPH.S the outline BECOMES the area under the series line by ARAP (kinetics/arap.mjs - det J(t) > 0 at every frame),
     on a min-jerk clock; the build then strokes the line along the morphed area's top edge and the fill fades with the
     build. Behind kinetics.arap_morph: with the flag off a morph page behaves as a mount of the same length, so an old
     render is one flag away. The three match-cut invariants (the brief B4) are computed by __morphInvariants for M17. */
  const MORPH = { S: 2.0, FILL_A: 0.28, COLS: 48, TEAR: 14, TAB_W: 0.92, TAB_H: 0.85 };   /* dials (42 s42.5): the morph's seconds, the fill, the strip's columns, the tab's tear (viewBox px) and its size as a share of the target's box */
  /* the two shapes as STRIPS of MORPH.COLS columns (arap.mjs stripMesh): the target is the series sampled at n x-positions over
     its baseline; the prop is a strip of the same columns placed on the target's area centroid and turned to its dominant
     axis, so the centroid and axis invariants hold by construction and the morph is a change of SHAPE, not a move. A fan
     from one centre flips on a jagged series (measured: 12 of 96 on the holdings page); a strip never does. */
  const morphProp = (name, n, w, h) => {   /* local coords about the origin: [top, bottom] rows of n columns */
    const top = [], bot = [];
    for (let i = 0; i < n; i++) {
      const x = -w / 2 + (i / (n - 1)) * w; let dy = 0;
      if (name === "plate" || name === "card") {   /* eased corners: a quarter-circle profile over the first and last columns */
        const r = Math.min(w, h) * 0.12, k = Math.min(i, n - 1 - i), d = (k / (n - 1)) * w;
        if (d < r) dy = r - Math.sqrt(Math.max(0, r * r - (r - d) * (r - d)));
      } else if (i >= n - 3) dy = MORPH.TEAR * ((i % 2) ? 1 : 0.4);   /* the tab: a torn right edge */
      top.push([x, -h / 2 + dy]); bot.push([x, h / 2 - dy]);
    }
    return { top, bot };
  };
  const buildMorph = (st, pg, world) => {
    const line = (st.linePts || [])[0]; if (!line || line.length < 2 || !(st.axisB > 0)) return null;
    const G = st.geom || { W: 1000, H: 560 }, n = MORPH.COLS, xL = line[0][0], xR = line[line.length - 1][0];
    const yAt = (x) => { for (let i = 0; i + 1 < line.length; i++) { const a = line[i], q = line[i + 1]; if (x >= a[0] - 1e-9 && x <= q[0] + 1e-9) { const u = (x - a[0]) / Math.max(1e-9, q[0] - a[0]); return a[1] + (q[1] - a[1]) * clamp01(u); } } return line[line.length - 1][1]; };
    const xs = [...Array(n).keys()].map((i) => xL + (i / (n - 1)) * (xR - xL));
    const topB = xs.map((x) => [x, yAt(x)]), botB = xs.map((x) => [x, st.axisB]);
    const B = stripOutline([...topB, ...botB], n), c = centroid(B), th = dominantAxis(B);
    const w = extentAlong(B, th) * MORPH.TAB_W, h = extentAlong(B, th + Math.PI / 2) * MORPH.TAB_H, cs = Math.cos(th), sn = Math.sin(th);   /* sized in the target's principal frame */
    const place = ([x, y]) => [c[0] + x * cs - y * sn, c[1] + x * sn + y * cs];
    const prop = morphProp(world.morph || "tab", n, w, h), topA = prop.top.map(place), botA = prop.bot.map(place);
    const mesh = stripMesh(topA, botA), prep = arapPrepareMesh(mesh, [...topB, ...botB], n + (n >> 1));   /* the pinned vertex: the bottom middle, on the chord */
    const A = stripOutline(mesh.verts, n);
    const svg = lpEl("svg", "lp-chart lp-morph", st.page, { viewBox: st.chart.getAttribute("viewBox") });
    svg.setAttribute("style", st.chart.getAttribute("style") || "");
    const col = (st.paths.filter((pp) => !pp.muted)[0] || {}).p; const stroke = col ? col.getAttribute("stroke") : "var(--lp-chalk)";
    const path = lpEl("path", "morph", svg, { d: outlinePath(A), fill: stroke, "fill-opacity": MORPH.FILL_A, stroke: "var(--lp-chalk)", "stroke-width": 3 });
    return { svg, path, prep, A, B, W: G.W, stroke };
  };
  const paintMorph = (st, pg, world, u, c) => {
    if (st.morph === undefined) st.morph = buildMorph(st, pg, world);
    const M = st.morph; if (!M) return;
    const k = kin("min_jerk") ? minJerk(u) : expoOut(clamp01(u));
    const pts = u >= 1 ? M.B : arapAt(M.prep, k).outline;
    M.path.setAttribute("d", outlinePath(pts));
    M.path.setAttribute("stroke", u >= 1 ? M.stroke : "var(--lp-chalk)");
    M.path.setAttribute("fill-opacity", (MORPH.FILL_A * (u < 1 ? 1 : 1 - clamp01(c))).toFixed(3));   /* the fill leaves as the line draws */
    M.svg.style.opacity = (u < 1 || c < 1) ? "1" : "0";
    M.u = u;
  };
  /* ---- THE BREAKTHROUGH's run (2026-09-10): seconds since the ordinary build ended, a pure function of them ------------
     burst: the bar shoots from the comparator's level to its true height while the scale rewrites (hi0 -> hi1) under every
            bar; the old ticks slide with the stretching scale and fade, the new ones fade in; the bar overshoots and settles;
            the pill rides the tip and counts to the exact string; the bar glows.
     stack: the scale holds; the bar grows one comparator per BT_STEP_S until the true number, past the plot, off the page. */
  const lpPaintBreakthrough = (cs, secs) => {
    const B = cs.bt, e = cs.bars.find((b) => b.over); if (!B || !e) return;
    const run = secs - LPX.BT_HOLD, P = !!cs.portrait, plot = B.plot;
    let V = B.comp, hiU = B.hi0, u1 = 0, u2 = 0, overshoot = 0, K = null;
    if (B.mode === "burst") {
      /* P50 T13: ONE clock drives the shoot, the counter, the rescale and the ticks' crossing, so the blend steps
         them TOGETHER. With no cadence named it is the two clamps it always was (species/breakthrough.mjs keeps that
         path arithmetically untouched); with `break_cadence: "stop"` it is those clamps read off a stepped run. */
      K = burstClock(run, LPX.BT_RUN, LPX.BT_SETTLE, B.cad);
      u1 = K.u1; u2 = K.u2;
      const u = minJerk(u1);
      hiU = B.hi0 + (B.hi1 - B.hi0) * u;
      V = B.comp + (e.v - B.comp) * u;
      overshoot = LPX.BT_OVER * (u1 < 1 ? Math.sin(Math.PI / 2 * u1) : 1 - minJerk(u2));
    } else {
      const steps = run < 0 ? 0 : Math.floor(run / LPX.BT_STEP_S) + 1;
      V = Math.min(e.v, B.comp * (1 + steps));
    }
    const myU = (v) => B.bottom - (v - B.lo) / (hiU - B.lo || 1) * plot;
    cs.scale.my = myU; cs.scale.y1 = hiU;   /* figures and brackets on the page follow the live scale (R26-28) */
    cs.bars.forEach((bb) => {
      const shown = bb === e ? V : bb.v, h = Math.max(3, (B.base - myU(shown)) * (bb === e ? 1 + overshoot : 1));
      bb.bar.setAttribute("y", (B.base - h).toFixed(1)); bb.bar.setAttribute("height", h.toFixed(1)); bb.h = h; bb.end = B.base - h;
      if (bb !== e) bb.val.setAttribute("y", (bb.end - (P ? 22 : 14)).toFixed(1));
      else if (!cs.callout) { bb.val.setAttribute("y", (bb.end - (P ? 22 : 14)).toFixed(1)); if (secs >= 0) bb.val.textContent = V >= e.v - 1e-9 ? lpWithUnit(cs.vstr[e.i] != null ? String(cs.vstr[e.i]) : lpFmt(e.v), cs.cunit || "") : lpWithUnit(lpFmt(V), cs.cunit || ""); }
      if (bb.snap) bb.snap.forEach((s) => s.setAttribute("opacity", V > B.hi0 ? 1 : 0));
    });
    if (B.mode === "burst") {
      const fade = minJerk(u1);
      B.ticks0.forEach((el, j) => {   /* [grid, label] pairs, in vals0's order: they slide with the stretching scale and leave */
        const v = B.vals0[j >> 1], y = myU(v), isLab = (j & 1) === 1;
        if (isLab) el.setAttribute("y", (y + (P ? 14 : 8)).toFixed(1)); else { el.setAttribute("y1", y.toFixed(1)); el.setAttribute("y2", y.toFixed(1)); }
        if (v !== 0) el.setAttribute("opacity", (1 - fade).toFixed(3));
      });
      B.ticks1.forEach((el) => el.setAttribute("opacity", fade.toFixed(3)));
      /* the continuous burst's glow RAMPS with the shoot and holds at half after it. The STEPPED one does not ramp -
         it HITS on the landing step, because in stop motion an impact is a frame, not a fade - and from the next step
         it holds at exactly the half the continuous one holds at, so the two rest on the same frame (P50 T13). */
      const glow = B.cad ? (K && K.landed ? 1 : u1 < 1 ? 0 : 1 - 0.5 * minJerk(u2))
                         : (run < 0 ? 0 : u1 < 1 ? u1 : 1 - 0.5 * minJerk(u2));
      e.bar.style.filter = glow > 0 ? "drop-shadow(0 0 " + (LPX.BT_GLOW * glow).toFixed(1) + "px " + (e.bar.style.fill || "var(--lp-pos)") + ")" : "";
    }
    if (cs.callout && cs.cpill) {   /* the pill rides the tip; once the tip has left the page it sits inside its own bar */
      const CP = cs.cp;
      if (B.cap) {   /* ... unless the capsule is mounted on the AXIS: it stands still and the dotted leader grows up to the tip */
        const L = breakLeader(B.cap.lx, e.end, B.cap.y);
        B.cap.lead.setAttribute("y1", (L ? L.y1 : B.cap.y).toFixed(1));
        B.cap.lead.setAttribute("y2", (L ? L.y2 : B.cap.y).toFixed(1));
        B.cap.lead.setAttribute("opacity", L ? 1 : 0);
      } else {
        const py = Math.max(24, e.end - CP.up);
        cs.cpill.setAttribute("y", py.toFixed(1)); cs.cval.setAttribute("y", (py + CP.ty).toFixed(1));
      }
      if (secs >= 0) cs.cval.textContent = V >= e.v - 1e-9 ? cs.cfinalTrue : lpWithUnit(lpFmt(V), cs.cunit || "");   /* R26-39: the build's count to comp is lpPaintChart's */
    }
    /* P50 T10 - THE PLACEHOLDER. The breaking bar's number is not the viewer's until it is SPOKEN, and "spoken" is
       the start of the hold (secs 0): until then the grey track stands behind the bar and the mark holds the number's
       place, so the page never prints a figure the narration has not reached. */
    if (B.ph) {
      const H = breakPlaceholder(secs);
      if (B.ph.track) B.ph.track.setAttribute("opacity", H.alpha.toFixed(3));
      if (B.ph.stamp) B.ph.stamp.setAttribute("opacity", H.k.toFixed(3));
      /* ONE mark, never two: while the "?" stands, the count that would sit in the same place is held back, and it
         arrives exactly as the mark leaves (the page's own cross-fade, over PH_OUT_S of the hold) */
      if (H.k > 0) { if (cs.callout) cs.callout.setAttribute("opacity", (1 - H.k).toFixed(2));
                     else if (e.val) e.val.setAttribute("opacity", (1 - H.k).toFixed(2)); }
    }
  };
  /* ---- ONE chart's build beat (P48 T4, lifted verbatim out of paintLedger) -------------------------
     `cs` is a CHART STATE: the page's own (st) or one of the others it can become. Everything here was
     already a pure function of the state's fraction c and the scene's species - lifting it changed no
     law - and that purity is what makes a recast free: c running back to zero un-draws any builder. */
  /* the pill at the drawn fraction f: the module says where it is, this hangs the furniture on the answer. The
     leader is drawn from the TIP (the real path's point, so a re-projected line keeps it), the pill's box from the
     measured type, and the whole group leaves as the terminal tag fades in - they never both stand. */
  const lpPaintPill = (pp, f, drawing) => {
    const P = pp.pill;
    if (!drawing) { P.g.setAttribute("opacity", 0); return; }
    /* THE CAPSULE IS THE TEXT'S OWN BOX, measured every paint until the webfont reports in (measured once, against the
       fallback face, it stayed at that width while the real type grew past it - read off the first frame, 2026-09-11).
       getBBox, not a character count: the tag may be written from its end and may carry a badge chip of its own. */
    if (!P.fixed && P.tx.getBBox) {
      const bb = P.tx.getBBox();
      if (bb && bb.width > 0) {
        const b = pillBox(bb.width, bb.height);
        P.box.setAttribute("x", (bb.x - TIPPILL.PAD_X).toFixed(1)); P.box.setAttribute("y", (bb.y - TIPPILL.PAD_Y).toFixed(1));
        P.box.setAttribute("width", b.w.toFixed(1)); P.box.setAttribute("height", b.h.toFixed(1));
        P.box.setAttribute("rx", b.r.toFixed(1));
        P.span = [bb.x - TIPPILL.PAD_X, bb.x + bb.width + TIPPILL.PAD_X];   /* the pill's ink about its anchor - what the clamp reads */
        P.fixed = typeof document !== "undefined" && document.fonts ? document.fonts.status === "loaded" : true;
      }
    }
    /* a tag wider than the chart cannot ride it: the clamp has nowhere to put it (measured: 1070 units of name on an
       800-unit chart hung half off the stage). The pill is a decoration on the draw - it is simply not drawn, and the
       line takes its terminal tag at the end as any page's does. */
    if (P.span && P.bounds && P.span[1] - P.span[0] > P.bounds[1] - P.bounds[0]) { P.g.setAttribute("opacity", 0); return; }
    const s = pillAt(pp.pts, f, { milestone: P.milestone, tag: [+pp.name.getAttribute("x"), pp.ny],
                                  span: P.span, bounds: P.bounds });
    if (!s || !s.on || s.scale <= 0.001) { P.g.setAttribute("opacity", 0); return; }
    const k = s.scale, px = s.pill[0], py = s.pill[1];
    P.g.setAttribute("transform", "translate(" + (px * (1 - k)).toFixed(2) + " " + (py * (1 - k)).toFixed(2) + ") scale(" + k.toFixed(4) + ")");
    P.tx.setAttribute("x", px.toFixed(1)); P.tx.setAttribute("y", py.toFixed(1));
    P.box.setAttribute("transform", "translate(" + px.toFixed(1) + " " + py.toFixed(1) + ")");
    P.lead.setAttribute("x1", s.leader[0][0].toFixed(1)); P.lead.setAttribute("y1", s.leader[0][1].toFixed(1));
    P.lead.setAttribute("x2", s.leader[1][0].toFixed(1)); P.lead.setAttribute("y2", s.leader[1][1].toFixed(1));
    P.lead.setAttribute("opacity", s.leaderOpacity.toFixed(2));
    P.g.setAttribute("opacity", Math.min(1, Math.max(0, 1 - s.handover)).toFixed(2));
  };
  const lpPaintChart = (cs, c, t3, scene, t, leaving) => {
      cs.chart.style.opacity = c > 0 ? 1 : 0;   /* axes and grid belong to the build, not the bleed */
      /* a breakthrough page's build is longer than LP.BUILD: the ordinary bars law runs on the first LP.BUILD seconds of it (cb),
         the run on the seconds after (bts); a page without one is exactly what it was (cb === c) */
      const cb = cs.bt ? clamp01(c * cs.buildDur / cs.btBase) : c, bts = cs.bt ? c * cs.buildDur - cs.btBase : -1;
      cs.bars.forEach((bb, i) => {
        const k = expoOut(clamp01((cb - i * 0.1) / 0.55));
        bb.bar.style.transform = "scaleY(" + k.toFixed(4) + ")";
        bb.lab.setAttribute("opacity", clamp01((cb - i * 0.1 - 0.3) / 0.2).toFixed(2));
        bb.val.setAttribute("opacity", clamp01((k - 0.9) / 0.1).toFixed(2));
      });
      if (cs.callout) {
        const ck = cb >= 1 ? 1 : clamp01((cb - 0.55) / 0.45);   /* (1 - 0.55) / 0.45 is 0.999... in floating point: the count must LAND on the exact string (s9.23b), never one unit short forever */
        cs.callout.setAttribute("opacity", clamp01(ck / 0.3).toFixed(2));
        cs.cval.textContent = ck >= 1 ? cs.cfinal : lpWithUnit(lpFmt(cs.cnum * expoOut(ck)), cs.cunit || "");
      }
      if (cs.bt) lpPaintBreakthrough(cs, bts);   /* R26-39: negative secs = the BUILD phase - the bar's rest is the comparator's level, so the
                                                bars law above scales a bar like the others (E60); the laid-out rect is the value on the stated scale */
      const caps = pageSpecies(scene, "build_to");   /* P47 T2: the line draws to a datum on a word, the rest on the next word */
      cs.paths.forEach((pp) => {
        const fr = clamp01((c - pp.stagger * 0.3) / 0.7);
        /* DRAWING runs on the pen (strokeFrac, the two-thirds law): the hand hurries through a smooth stretch and slows
           through a jagged one. LEAVING must not - on a dense series the pen is already deep in the jagged tail at
           two-thirds of the clock, so a backwards pen looks like a line that stands still and then disappears. A line
           retreats by LENGTH, which is what the undraw species does. */
        /* ... and it leaves in the REVERSE order it arrived: the last stroke drawn is the first to go, or a highlighted
           tail retreats beside its own history and reads as a stray mark floating off the end of the line. */
        let f = leaving ? clamp01((c - pp.stagger) / Math.max(0.2, 1 - pp.stagger))
                        : (strokeFrac(pp.p, pp.len, fr) ?? expoOut(fr));
        /* P47 T2 / T6 / T9: the caps and the undraws are ONE sequence in time per path. The build beat is spent on the first cap;
           every later event moves the level from the previous event's target to its own over its word - a build_to draws forward
           (never below what stands), an undraw unwinds (index 0 = to nothing), and a build_to AFTER an undraw RE-DRAWS. `paths`
           picks which strokes an event touches: all (default) | tail (the highlighted strokes, k0 > 0) | history (k0 = 0) - so a
           page can un-draw everything and then draw back only the months the sentence is about. */
        /* P50 T9: on a tiers page a TIER is a series index - one resolution, not two; `tier` is the word the
           author writes and the compiler refuses it beside a disagreeing `series` */
        const forMe = (sp) => { const ss = sp.series ?? sp.tier ?? (sp.target || {}).series, pk = sp.paths || "all";
          return pp.pts && (ss == null || (ss | 0) === (pp.si | 0)) && (pk === "all" || (pk === "tail" ? (pp.k0 | 0) > 0 : (pp.k0 | 0) === 0)); };
        const evs = [...caps.filter((sp) => forMe(sp) && !!sp.target).map((sp) => ({ sp, kind: "build" })), ...pageSpecies(scene, "undraw").filter(forMe).map((sp) => ({ sp, kind: "undraw" }))].sort((a, b) => a.sp.at - b.sp.at);
        let prev = 1;
        if (evs.length && evs[0].kind === "build") { prev = capFrac(pp, evs[0].sp.target.index); f = f * prev; evs.shift(); }   /* the build beat is spent on the first cap */
        for (const ev of evs) {
          const u = (t - ev.sp.at) / Math.max(0.001, ev.sp.dur || 1); if (u <= 0) break;
          const to = capFrac(pp, (ev.sp.target || {}).index | 0), lvl = prev + (to - prev) * segEase(clamp01(u));
          f = ev.kind === "build" ? Math.max(Math.min(f, prev), lvl) : Math.min(f, lvl);
          if (u >= 1) prev = to;
        }
        if (cs.extendCap && (!cs.extendCap.bySeries || (pp.si | 0) === (cs.extendCap.si | 0))) {   /* P48 T3: a window that grows grows for EVERY series (the golden's four lines caught a cap on the first alone); a later series caps itself. The muted history and the highlighted tail alike are drawn to the pen: the shared part stands, the new part follows the nib */
          const c0 = cs.extendCap.bySeries ? 0 : capFrac(pp, cs.extendCap.idx), pen = strokeFrac(pp.p, pp.len, cs.extendCap.u2);
          f = Math.min(f, c0 + (1 - c0) * (pen == null ? expoOut(cs.extendCap.u2) : pen));
        }
        pp.p.setAttribute("stroke-dashoffset", (pp.len * (1 - f)).toFixed(1));
        pp.p.style.opacity = f > 0.004 ? "" : "0";   /* E50 (the third watch: "dots that linger"): a zero-length round-capped dash paints a dot at the path's start - an un-drawn line shows nothing */
        const drawing = f > 0.01 && f < 0.995;
        if (drawing && pp.p.getPointAtLength) { const q = pp.p.getPointAtLength(pp.len * f); pp.tip.setAttribute("cx", q.x); pp.tip.setAttribute("cy", q.y); }
        pp.tip.setAttribute("opacity", drawing ? 1 : 0);
        pp.name.setAttribute("opacity", clamp01((f - 0.9) / 0.1).toFixed(2));
        if (pp.pill) lpPaintPill(pp, f, drawing);   /* P50 T11: the pill rides this same f - one clock, no second state */
      });
      for (const hr of cs.hlines || []) { const k = clamp01(c / 0.25); hr.line.setAttribute("opacity", (0.9 * k).toFixed(3)); if (hr.lab) hr.lab.setAttribute("opacity", clamp01((c - 0.25) / 0.2).toFixed(2)); }
      if (cs.paint) cs.paint(cs, c, t3);   /* the builder's own build step (race / decline / combo / share) */
      if (cs.share) {   /* P48 T4: the piece the sentence is about leaves the pie on its word */
        let pu = 0;
        for (const sp of pageSpecies(scene, "peel")) pu = Math.max(pu, (t - sp.at) / Math.max(0.001, sp.dur || 1));
        lpPeelTo(cs, pu);
      }
  };
  /* P48 T2 - RESCALE. The standing chart never leaves: on one min-jerk clock every mark that exists under both scales moves
     from its place under A to its place under B (a line's path is re-projected from its DATA, a bar's rect and every tick,
     label, rule and name lerp by value), a tick whose value leaves the target domain fades as it travels, a tick the target
     adds fades in at its settled place, and at the clock's end the target state stands exactly as it was built at load. The
     blend WRITES attributes onto the standing state's elements; lpRestoreState puts them back the moment no rescale is on,
     so a seek to any t paints the same frame (the seek test). Bravos 46 s46.7: a build inside a held frame, not a cut. */
  const lpRestoreState = (S) => {
    if (!S || !S.xfDirty) return;
    for (const pp of S.paths || []) {
      if (pp.d0 && pp.p.getAttribute("d") !== pp.d0) { pp.p.setAttribute("d", pp.d0); pp.p.setAttribute("stroke-dasharray", pp.len0); pp.len = pp.len0; }
      if (pp.p.hasAttribute("clip-path")) pp.p.removeAttribute("clip-path");
      if (pp.p.hasAttribute("transform")) pp.p.removeAttribute("transform");
    }
    for (const m of S.marks || []) if (m.el && ["axis", "axislabel"].includes(m.role)) m.el.style.opacity = "";
    for (const m of S.marks || []) {
      const g = m.geom || {}, e = m.el; if (!e) continue;
      if (m.role === "tick" || m.role === "rule") { e.setAttribute("y1", g.y.toFixed(1)); e.setAttribute("y2", g.y.toFixed(1)); e.style.opacity = ""; }
      else if (m.role === "ylabel" || m.role === "rulelabel" || m.role === "name") { e.setAttribute("x", (+g.x).toFixed(1)); e.setAttribute("y", (+g.y).toFixed(1)); e.style.opacity = "";
        if (e.hasAttribute("transform")) e.removeAttribute("transform"); }   /* P50 T11: a tag that grew into a bar shrinks back on a seek */
      else if (m.role === "xtick" || m.role === "xlabel" || m.role === "value") { e.setAttribute("x", (+g.x).toFixed(1)); e.setAttribute("y", (+g.y).toFixed(1)); e.style.opacity = ""; }
      else if (m.role === "bar") { e.setAttribute("x", g.x.toFixed(1)); e.setAttribute("y", g.y.toFixed(1)); e.setAttribute("width", g.w.toFixed(1)); e.setAttribute("height", g.h.toFixed(1)); e.style.transformOrigin = "0 " + g.base.toFixed(1) + "px"; }
    }
    S.xfDirty = false;
  };
  const lpPaintRescale = (states, xf, t3, scene, t) => {
    const A = states[xf.from], Bs = states[xf.to], u = xf.u;
    for (let i = 0; i < states.length; i++) if (i !== xf.from && i !== xf.to) lpPaintChart(states[i], 0, t3, scene, t);
    lpPaintChart(A, 1, t3, scene, t);        /* the standing chart, fully built: the transition moves its marks */
    lpPaintChart(Bs, 0, t3, scene, t);       /* the target's furniture only - its series stay undrawn until the clock ends */
    const sa = A.scale, sb = Bs.scale; if (!sa || !sb) return;
    A.xfDirty = true; Bs.xfDirty = true;
    const vIn = (v) => xfInside(sa.yv(v), sb.y0, sb.y1), xIn = (x) => sb.x0 === undefined || xfInside(x, sb.x0, sb.x1);
    const aVals = new Set((A.marks || []).filter((m) => m.role === "tick").map((m) => m.geom.v));
    if (sa.kind === "line" && sb.kind === "line") {
      const mapA = (x, v) => [sa.mx(x), sa.my(v)], mapB = (x, v) => [sb.mx(x), sb.my(v)];
      for (const pp of A.paths || []) {
        if (!pp.data) continue;
        if (A.plotClip) pp.p.setAttribute("clip-path", "url(#" + A.plotClip + ")");   /* the pin: nothing draws outside the plot while the line moves */
        const f = 1 - parseFloat(pp.p.getAttribute("stroke-dashoffset") || "0") / (pp.len || 1);   /* how much is drawn, before the path moves */
        const { d } = xfPath(pp.data, mapA, mapB, u);
        pp.p.setAttribute("d", d);
        const len2 = pp.p.getTotalLength ? pp.p.getTotalLength() : pp.len; pp.len = len2;
        pp.p.setAttribute("stroke-dasharray", len2); pp.p.setAttribute("stroke-dashoffset", (len2 * (1 - f)).toFixed(1));
      }
    }
    const nameB = (k) => (Bs.markBy || {})[k];
    for (const m of A.marks || []) {
      const g = m.geom || {}, e = m.el; if (!e) continue;
      if (m.role === "tick" || m.role === "rule") { const y = xfLerp(g.y, sb.my(g.v), u); e.setAttribute("y1", y.toFixed(1)); e.setAttribute("y2", y.toFixed(1)); e.style.opacity = xfFade(vIn(g.v), false, u).toFixed(3); }
      else if (m.role === "ylabel" || m.role === "rulelabel") { const y = xfLerp(g.y, sb.my(g.v) + (g.y - sa.my(g.v)), u); e.setAttribute("y", y.toFixed(1)); e.style.opacity = xfFade(vIn(g.v), false, u).toFixed(3); }
      else if (m.role === "xtick" && sb.mx) { const x = xfLerp(g.x, sb.mx(g.v), u); e.setAttribute("x", x.toFixed(1)); e.style.opacity = xfFade(xIn(g.v), false, u).toFixed(3); }
      else if (m.role === "name") { const nb = nameB(m.key); if (nb) { e.setAttribute("x", xfLerp(g.x, nb.geom.x, u).toFixed(1)); e.setAttribute("y", xfLerp(g.y, nb.geom.y, u).toFixed(1)); } }
      else if (m.role === "bar" && sa.kind === "bars") { const nb = nameB(m.key); if (nb) { const r = xfRect(g, nb.geom, u); e.setAttribute("x", r.x.toFixed(1)); e.setAttribute("y", r.y.toFixed(1)); e.setAttribute("width", r.w.toFixed(1)); e.setAttribute("height", r.h.toFixed(1)); e.style.transformOrigin = "0 " + xfLerp(g.base, nb.geom.base, u).toFixed(1) + "px"; } }
      else if ((m.role === "value" || m.role === "xlabel") && sa.kind === "bars") { const nb = nameB(m.key); if (nb) { e.setAttribute("x", xfLerp(g.x, nb.geom.x, u).toFixed(1)); e.setAttribute("y", xfLerp(g.y, nb.geom.y, u).toFixed(1)); } }
    }
    /* the target's furniture: a tick the standing chart already has stays hidden (its twin is travelling); a NEW one arrives */
    Bs.chart.style.opacity = u > 0 ? 1 : 0;
    for (const m of Bs.marks || []) {
      const e = m.el; if (!e) continue;
      if (m.role === "tick" || m.role === "ylabel") e.style.opacity = xfFade(true, true, aVals.has(m.geom.v) ? 0 : u).toFixed(3);
      else if (m.role === "xtick" || m.role === "rule" || m.role === "rulelabel" || m.role === "axislabel") e.style.opacity = xfFade(true, true, u).toFixed(3);
      else if (m.role === "name" || m.role === "line" || m.role === "bar" || m.role === "value" || m.role === "xlabel") e.style.opacity = "0";
    }
  };
  /* P48 T3 - EXTEND. Two phases on one clock: the shared marks RESCALE to the target's scale over the first XF_EXTEND.RESCALE
     share (the standing line moves, the target's furniture arrives), then the target stands with its shared points drawn and
     the NEW segment draws from the last shared datum at the pen's speed (strokeFrac, the two-thirds law) with the nib visible
     - or, for a later series, that series draws from its first point. Nothing pops: at the phase boundary the standing line's
     re-projected geometry IS the target's, so the hand-over is invisible. Bravos 29-30: production first, consumption on its word. */
  const XF_EXTEND = Object.freeze({ RESCALE: 0.45 });   /* the share of an extend's clock spent retargeting the axes before the pen moves [DERIVED: the axis settles before the eye follows the nib] */
  const lpPaintExtend = (states, xf, t3, scene, t) => {
    const A = states[xf.from], Bs = states[xf.to], R = XF_EXTEND.RESCALE;
    if (xf.u < R) { lpPaintRescale(states, { from: xf.from, to: xf.to, u: segEase(xf.u / R) }, t3, scene, t); Bs.extendCap = null; return; }
    for (const S of states) lpRestoreState(S);
    const u2 = clamp01((xf.u - R) / (1 - R));
    const bySeries = xf.sp.from_series != null, si = bySeries ? xf.sp.from_series | 0 : 0;
    Bs.extendCap = { si, bySeries, idx: (xf.sp.from_index | 0) - ((Bs.windowOffsets || [])[0] | 0), u2 };   /* each path of the series caps itself at its own shared datum (lpPaintChart) */
    for (let i = 0; i < states.length; i++) lpPaintChart(states[i], i === xf.to ? 1 : 0, t3, scene, t);
  };
  /* P48 T2b - PARK. The active chart shrinks toward one corner of its own box by ONE affine transform on a min-jerk clock and
     stays there: every mark, tick, ring and X keeps its place inside the chart (the stability rule - a re-laid-out chart flickers,
     Sondag 2018), the title stays where it is, and the rest of the chart's box is free for what the sentence turns to next
     (Bravos shot 91). The transform is the SVG's own; datum targets map through it because stageBox reads the transformed
     rectangle, and the vortex reads the same rectangle. Idle-clean: the transform is written only while a park is on. */
  /* P48 T4b - the KEYED recast (n lines -> n bars, by series; Bravos 99-105). Two phases on ONE clock. Phase 1 (the first
     KEYED.TAG): each line's terminal VALUE appears at its end - the number its bar will be (Bravos 99: "value bars at the
     ends"). Phase 2: the line leaves by its HISTORY (the dash window slides toward the tail: what stays is the last value),
     its end and its value travel to the bar's top, and the bar grows from the common baseline beneath them; A's furniture
     leaves over the first half of the phase and B's arrives over the second; the bar's name comes up under it. The line's
     NAME gives way to its value in phase 1 - the value is born at the name's settled (pushed-apart) y, so four values never
     overprint each other or the tag chips (the first cut had 120.8 over 121.5 and 712.5 over "our layer"). At the clock's end
     the target stands exactly as built. The correspondence is by index - series i <-> bar i -
     which the compiler admitted (RECAST_PAIRS). */
  const KEYED = Object.freeze({ TAG: 0.3 });   /* the share of the clock the terminal values take to appear before anything moves */
  const FURNITURE = ["tick", "ylabel", "rule", "rulelabel", "xtick", "axis", "axislabel"];
  /* P50 T11 - the TAG form (`keyed: "tags"`, Bravos 104-105). The same hand-over keyed on the other mark: each
     series' TERMINAL TAG is what becomes its bar. The tag does not give way to a number - it IS the number: it slides
     and GROWS into the bar's own value type while the line un-draws by length beneath it, and in the last breath of
     the clock the bar's value takes over at exactly the tag's place, with the same string. So no value is ever drawn
     twice and nothing is re-written: phase 1 (the value being born at the name) has nothing left to do and the whole
     clock is the slide. */
  const KEYED_TAG_HAND = 0.92;   /* the share of the CLOCK after which the bar's own value takes the tag's place - the clock, not the eased slide, which is 97 % done at half the clock (read off the first frame, 2026-09-11: the two strings stood ghosted over each other for two thirds of the transition) [DERIVED: 0.16 s of a 2 s clock, ~5 frames at 30 fps] */
  const lpPaintRecastKeyed = (states, xf, t3, scene, t) => {
    const A = states[xf.from], Bs = states[xf.to], u = xf.u, tags = xf.keyed === "tags";
    const u1 = tags ? 1 : expoOut(clamp01(u / KEYED.TAG)), v = tags ? segEase(u) : segEase(clamp01((u - KEYED.TAG) / (1 - KEYED.TAG)));
    const hand = clamp01((u - KEYED_TAG_HAND) / (1 - KEYED_TAG_HAND));
    for (let i = 0; i < states.length; i++) if (i !== xf.from && i !== xf.to) lpPaintChart(states[i], 0, t3, scene, t);
    lpPaintChart(A, 1, t3, scene, t);
    lpPaintChart(Bs, 0, t3, scene, t);   /* the base: bars at scaleY(0), names and values at 0; the keyed paint writes over it */
    Bs.chart.style.opacity = 1;
    A.xfDirty = true; Bs.xfDirty = true;
    const bars = (Bs.marks || []).filter((m) => m.role === "bar");
    for (const pp of A.paths || []) {
      if (pp.muted || !pp.pts || !pp.pts.length) continue;
      const bar = bars[pp.si | 0]; if (!bar) continue;
      const end = pp.pts[pp.pts.length - 1], top = [bar.geom.cx, bar.geom.end];
      const dx = (top[0] - end[0]) * v, dy = (top[1] - end[1]) * v;
      pp.p.setAttribute("stroke-dashoffset", (-(pp.len * v)).toFixed(1));   /* the dash window slides toward the tail: the history leaves first */
      pp.p.setAttribute("transform", "translate(" + dx.toFixed(1) + " " + dy.toFixed(1) + ")");
      pp.tip.setAttribute("opacity", 0);
      if (pp.pill) pp.pill.g.setAttribute("opacity", 0);   /* the pill's work ended with the draw; the tag carries the hand-over */
      const rec = bar.rec || {};
      if (rec.bar) rec.bar.style.transform = "scaleY(" + v.toFixed(4) + ")";
      const vm = Bs.markBy["val:b:" + (pp.si | 0)], nm = A.markBy["name:s" + (pp.si | 0)];
      if (tags) {
        /* the TAG travels, and grows into the value's own type; the bar's value is not drawn until it takes over */
        if (rec.val && Bs.tagFS == null) Bs.tagFS = parseFloat(getComputedStyle(rec.val).fontSize) || 0;
        if (A.nameFS == null) A.nameFS = parseFloat(getComputedStyle(pp.name).fontSize) || 0;
        const grow = A.nameFS > 0 && Bs.tagFS > 0 ? 1 + (Bs.tagFS / A.nameFS - 1) * v : 1;
        /* the bar's number is CENTRED over its bar and the tag is written from its own end, so the tag's landing x is
           the number's x pulled back by half the tag's (grown) width - land the string, not its anchor */
        A.tagW = A.tagW || {};
        if (A.tagW[pp.si | 0] == null) A.tagW[pp.si | 0] = pp.name.getComputedTextLength ? pp.name.getComputedTextLength() : 0;
        const half = A.tagW[pp.si | 0] * grow / 2, lead = (pp.name.getAttribute("text-anchor") === "end" ? half : -half);
        const p0 = [nm ? +nm.geom.x : end[0], nm ? +nm.geom.y : end[1] - 14], p1 = vm ? [vm.geom.x + lead, vm.geom.y] : [top[0], top[1] - 14];
        const x = xfLerp(p0[0], p1[0], v), y = xfLerp(p0[1], p1[1], v);
        pp.name.setAttribute("x", x.toFixed(1)); pp.name.setAttribute("y", y.toFixed(1));
        pp.name.setAttribute("transform", "translate(" + (x * (1 - grow)).toFixed(2) + " " + (y * (1 - grow)).toFixed(2) + ") scale(" + grow.toFixed(4) + ")");
        pp.name.setAttribute("opacity", (1 - hand).toFixed(2));
        if (rec.val) { rec.val.setAttribute("opacity", hand.toFixed(2)); }
      } else {
      pp.name.setAttribute("opacity", (1 - u1).toFixed(2));   /* the name gives way to the number */
      if (rec.val) {   /* the value: born where the name stood (its settled y), travels with the line's end to the bar's top */
        const p0 = [end[0], nm ? +nm.geom.y : end[1] - 14], p1 = vm ? [vm.geom.x, vm.geom.y] : [top[0], top[1] - 14];
        rec.val.setAttribute("x", xfLerp(p0[0], p1[0], v).toFixed(1)); rec.val.setAttribute("y", xfLerp(p0[1], p1[1], v).toFixed(1));
        rec.val.setAttribute("opacity", u1.toFixed(2));
      }
      }
      if (rec.lab) rec.lab.setAttribute("opacity", clamp01((v - 0.6) / 0.4).toFixed(2));   /* the bar's name comes up as the line's goes */
    }
    for (const m of A.marks || []) if (m.el && FURNITURE.includes(m.role)) m.el.style.opacity = xfFade(false, false, v).toFixed(3);
    for (const m of Bs.marks || []) if (m.el && FURNITURE.includes(m.role)) m.el.style.opacity = xfFade(true, true, v).toFixed(3);
  };
  /* P48 T5 - morph_to: the AREA UNDER THE STANDING LINE becomes the area under the target's line by ARAP (kinetics/arap.mjs,
     the strip mesh of P47 T3's page-enter morph), mid-page, on one clock. The first XF_MORPH.LEAVE of it the standing line
     un-draws by length, in reverse (E50: a line leaves by length) while its area fills in the series' own colour; the rest
     of the clock the filled strip morphs (min-jerk, det J > 0 at every frame) into the target's area as the standing axes
     leave and the target's arrive; then the target BUILDS on its own law - the line strokes along the morphed area's top
     edge - and the fill leaves with the build, as the page-enter morph's does. No key correspondence is pretended: it is a
     change of SHAPE (the plan's row 37: "morph on page - the geometry, with no key correspondence"). Behind
     kinetics.arap_morph: with the flag off a morph_to IS the recast hand-over of the same length, byte for byte. */
  const XF_MORPH = Object.freeze({ LEAVE: 0.3 });   /* the share of the clock the standing line takes to leave before the shape moves */
  const lpStrip = (S, n) => {   /* a state's area under its first drawn line as a strip: n columns, top on the line, bottom on the axis */
    const line = (S.linePts || [])[0]; if (!line || line.length < 2 || !(S.axisB > 0)) return null;
    const xL = line[0][0], xR = line[line.length - 1][0];
    const yAt = (x) => { for (let i = 0; i + 1 < line.length; i++) { const a = line[i], q = line[i + 1]; if (x >= a[0] - 1e-9 && x <= q[0] + 1e-9) { const u = (x - a[0]) / Math.max(1e-9, q[0] - a[0]); return a[1] + (q[1] - a[1]) * clamp01(u); } } return line[line.length - 1][1]; };
    const xs = [...Array(n).keys()].map((i) => xL + (i / (n - 1)) * (xR - xL));
    return { top: xs.map((x) => [x, yAt(x)]), bot: xs.map((x) => [x, S.axisB]) };
  };
  const lpMorphFor = (st, from, to, method) => {   /* built once per pair, at first need; the states' geometry is fixed at load, so it is pure */
    const key = from + ">" + to; st.morphTo = st.morphTo || {};
    if (key in st.morphTo) return st.morphTo[key];
    const A = st.states[from], Bs = st.states[to], n = MORPH.COLS, sa = lpStrip(A, n), sb = lpStrip(Bs, n);
    if (!sa || !sb) return (st.morphTo[key] = null);
    const mesh = stripMesh(sa.top, sa.bot), Bv = [...sb.top, ...sb.bot], prep = arapPrepareMesh(mesh, Bv, n + (n >> 1));   /* the pinned vertex: the bottom middle */
    const svg = lpEl("svg", "lp-chart lp-morph", st.page, { viewBox: A.chart.getAttribute("viewBox") });
    svg.setAttribute("style", A.chart.getAttribute("style") || ""); svg.style.opacity = "0";
    const col = ((A.paths || []).filter((pp) => !pp.muted)[0] || {}).p, stroke = col ? col.getAttribute("stroke") : "var(--lp-chalk)";
    const Ao = stripOutline(mesh.verts, n);
    const path = lpEl("path", "morph", svg, { d: outlinePath(Ao), fill: stroke, "fill-opacity": 0, stroke: "var(--lp-chalk)", "stroke-width": 3 });
    /* P50 T12 - METHOD A (doc 43 s43.5), when the compiler chose it: lpStrip has already done steps 1-2 (both rings are
       built from the same n columns, one orientation, one start vertex), so morphAPrepare runs step 3 on the two outlines
       with the strip's own order kept - the offset it returns is 0 when the columns correspond, which is the claim the
       method rests on and `morph_a_offset` carries to the gate. The frame is then the vertex lerp of the strip's rows,
       drawn as cubics (step 4). The ARAP prep is built either way: it costs one factorisation at first need and it is
       what M17's det leg reads when the method is B. */
    const aPrep = method === "a" ? { A: mesh.verts, B: Bv, n: mesh.verts.length,
                                     offset: morphAPrepare(Ao, stripOutline(Bv, n), { resample: false, normalise: false }).offset } : null;
    return (st.morphTo[key] = { svg, path, prep, aPrep, method: method === "a" ? "a" : "arap", mesh, Bv, cols: n,
                                A: Ao, B: stripOutline(Bv, n), W: (A.geom || { W: 1000 }).W, stroke, u: 0 });
  };
  const lpHideMorphs = (st, keep) => { for (const k in (st.morphTo || {})) { const M = st.morphTo[k]; if (M && M !== keep) M.svg.style.opacity = "0"; } };
  /* the ring at t, and the d it is drawn with, BY METHOD: A lerps the strip's corresponded vertices and reconstructs
     cubics; B solves the ARAP mesh and draws the polyline it has always drawn. A missing method is B, byte for byte. */
  const lpMorphRing = (M, k) => (M.method === "a" ? stripOutline(morphAAt(M.aPrep, k).outline, M.cols) : arapAt(M.prep, k).outline);
  const lpMorphD = (M, pts) => (M.method === "a" ? morphAPath(pts) : outlinePath(pts));
  const lpPaintMorphTo = (st, states, xf, t3, scene, t) => {
    const A = states[xf.from], Bs = states[xf.to], u = xf.u, M = lpMorphFor(st, xf.from, xf.to, xf.method);
    const uL = clamp01(u / XF_MORPH.LEAVE), uM = clamp01((u - XF_MORPH.LEAVE) / (1 - XF_MORPH.LEAVE)), kL = segEase(uL), kM = segEase(uM);
    for (let i = 0; i < states.length; i++) if (i !== xf.from && i !== xf.to) lpPaintChart(states[i], 0, t3, scene, t);
    lpPaintChart(A, 1 - kL, t3, scene, t, true);   /* the standing line leaves by length, in reverse */
    A.chart.style.opacity = uM > 0 ? xfFade(false, false, uM).toFixed(3) : "1";   /* its axes stand through the leave, then go over the morph's first half */
    lpPaintChart(Bs, 0, t3, scene, t);
    Bs.chart.style.opacity = xfFade(true, true, uM).toFixed(3);   /* the target's axes arrive over the morph's second half; its line waits for the build */
    lpHideMorphs(st, M); if (!M) return;
    const pts = uM <= 0 ? M.A : (uM >= 1 ? M.B : lpMorphRing(M, kM));
    M.path.setAttribute("d", lpMorphD(M, pts));
    M.path.setAttribute("fill-opacity", (MORPH.FILL_A * kL).toFixed(3));   /* the area fills as its line leaves */
    M.svg.style.opacity = "1"; M.u = u;
  };
  const lpPaintMorphHold = (st, hold, c) => {   /* after the clock: the fill leaves as the target's line draws over the morphed area's top edge */
    const M = lpMorphFor(st, hold.from, hold.to, hold.method); lpHideMorphs(st, M); if (!M) return;
    M.path.setAttribute("d", lpMorphD(M, M.B));
    M.path.setAttribute("fill-opacity", (MORPH.FILL_A * (1 - clamp01(c))).toFixed(3));
    M.svg.style.opacity = c < 1 ? "1" : "0"; M.u = 1;
  };
  const PARK_ORIGIN = Object.freeze({ top: "0 0", bottom: "0 100%", left: "0 0", right: "100% 0" });
  const lpPaintPark = (S, sp, t, fromScale) => {
    /* a park moves the chart from where it STANDS: from full size, or from the previous park's scale - so a park to scale 1 is an
       UN-PARK that grows the chart back (the operator, 2026-09-10: "the chart should re-take center stage" when the cards leave) */
    const from = Number.isFinite(+fromScale) ? +fromScale : 1;
    const d = Math.max(0.001, sp.dur || 1), u = segEase(clamp01((t - sp.at) / d)), sc = from + ((+sp.scale || 0.72) - from) * u;
    S.chart.style.transformOrigin = PARK_ORIGIN[sp.anchor || "top"] || PARK_ORIGIN.top;
    S.chart.style.transform = "scale(" + sc.toFixed(4) + ")";
    /* the citation rides the park with the chart (E52: the page cites - it was left full-size under the cards the park made room
       for, measured on the Tokyo cut 2026-09-10): the source line moves to where the parked chart's foot now is, at the park's scale */
    if (S.page && (sp.anchor || "top") === "top") {
      const pH = S.page.clientHeight || 0, toPx = (v) => { const q = String(v || "").trim(), n = parseFloat(q); return Number.isFinite(n) ? (q.endsWith("%") ? n / 100 * pH : n) : NaN; };   /* a page lays out in px (portrait) or % (landscape) */
      const cT = toPx(S.chart.style.top) || 0;
      S.page.querySelectorAll(".lp-src").forEach((el) => {
        const sT = toPx(el.style.top); const dy = (Number.isFinite(sT) ? (sT - cT) : 0) * (sc - 1);
        el.style.transformOrigin = "0 0"; el.style.transform = "translate(0px," + dy.toFixed(1) + "px) scale(" + sc.toFixed(4) + ")";
      });
    }
    S.parked = { u, scale: sc, anchor: sp.anchor || "top" };
  };
  const lpUnpark = (S) => { if (S && S.parked) { S.chart.style.transform = ""; S.chart.style.transformOrigin = ""; S.parked = null;
    if (S.page) S.page.querySelectorAll(".lp-src").forEach((el) => { el.style.transform = ""; el.style.transformOrigin = ""; }); } };
  /* the page's chart states over time. A `chart_to` is not a cut: the standing state runs its law BACKWARDS over the
     transition's own clock, then the named state draws on by its own envelope. Before the first chart_to, and on a page
     that declares none, this is exactly the single-chart behaviour it replaced. */
  const lpPaintStates = (st, scene, cBase, t3, t) => {
    const states = st.states || [st];
    if (states.length < 2) {   /* a page with one chart is exactly what it was - plus a park, if the row names one (P48 T2b) */
      lpPaintChart(st, cBase, t3, scene, t);
      let pk = null, pkFrom = 1; for (const sp of pageSpecies(scene, "chart_to")) { if (t < sp.at) break; if (sp.to === "park") { pkFrom = pk ? (+pk.scale || 0.72) : 1; pk = sp; } }   /* a park stands until the next park (E60 Tokyo: the burst plays in the parked slot; a park to scale 1 un-parks) */
      if (pk) lpPaintPark(st, pk, t, pkFrom); else lpUnpark(st);
      st.active = 0; return;
    }
    let cur = 0, cCur = cBase, leaving = false, xf = null, park = null, parkFrom = 1, hold = null;
    for (const sp of pageSpecies(scene, "chart_to")) {
      if (t < sp.at) break;
      if (sp.to === "park") { parkFrom = park ? (+park.scale || 0.72) : 1; park = sp; continue; }   /* P48 T2b: a transform on whichever state is active, never a state change; a later park moves from the standing one */
      hold = null;   /* a later transition to another state ends a morph's hold; the standing PARK stays - the new state stands where the old one did
                        (E60 Tokyo, 2026-09-10: the ten-year bars recast into the parked monthly bars' slot and burst there, the plant beneath them; a park to scale 1 un-parks) */
      const d = Math.max(0.001, sp.dur || 1), k = Math.max(0, Math.min(states.length - 1, sp.state | 0));
      if (sp.to === "rescale") {   /* P48 T2: the axes retarget on one clock; the chart never leaves, and the target stands built */
        if (t < sp.at + d) { xf = { from: cur, to: k, u: segEase(clamp01((t - sp.at) / d)) }; break; }
        cur = k; cCur = 1; continue;
      }
      if (sp.to === "extend") {   /* P48 T3: the axes retarget, then the new points draw on at the pen */
        if (t < sp.at + d) { xf = { from: cur, to: k, u: clamp01((t - sp.at) / d), extend: true, sp }; break; }
        cur = k; cCur = 1; continue;
      }
      if (sp.to === "morph" && kin("arap_morph")) {   /* P48 T5: the area under the line morphs into the target's; then the target builds - with the flag off this falls through to the recast hand-over of the same length */
        if (t < sp.at + d) { xf = { from: cur, to: k, u: clamp01((t - sp.at) / d), morph: true, method: sp.method }; break; }
        hold = { from: cur, to: k, method: sp.method }; cur = k; cCur = clamp01((t - (sp.at + d)) / (states[k].buildDur || LP.BUILD)); continue;
      }
      if (sp.keyed) {   /* P48 T4b: the keyed tween - one clock, both states painted by lpPaintRecastKeyed, the target built at its end */
        if (t < sp.at + d) { xf = { from: cur, to: k, u: clamp01((t - sp.at) / d), keyed: sp.keyed }; break; }   /* P50 T11: true = the datum hands over, "tags" = the terminal tag does */
        cur = k; cCur = 1; continue;
      }
      if (t < sp.at + d) { cCur = 1 - segEase(clamp01((t - sp.at) / d)); leaving = true; break; }   /* the standing chart is leaving */
      cur = k; cCur = clamp01((t - (sp.at + d)) / (states[k].buildDur || LP.BUILD));
    }
    st.active = xf ? ((xf.extend && xf.u >= XF_EXTEND.RESCALE) || (xf.morph && xf.u >= XF_MORPH.LEAVE) ? xf.to : xf.from) : cur;   /* the state a species target resolves against (P48 T2) */
    st.xfNow = xf ? { from: xf.from, to: xf.to, u: xf.u, extend: !!xf.extend, keyed: !!xf.keyed, morph: !!xf.morph } : null;   /* R26-28: the perform layer lerps its anchors on this clock */
    if (!(xf && xf.morph) && !(!xf && hold)) lpHideMorphs(st, null);   /* P48 T5: a morph's strip shows only while it morphs or holds under the target's build */
    if (xf && xf.extend) { lpPaintExtend(states, xf, t3, scene, t); }
    else if (xf && xf.morph) { for (const S of states) { lpRestoreState(S); S.extendCap = null; } lpPaintMorphTo(st, states, xf, t3, scene, t); }
    else if (xf && xf.keyed) { for (const S of states) lpRestoreState(S); lpPaintRecastKeyed(states, xf, t3, scene, t); }
    else if (xf) { lpPaintRescale(states, xf, t3, scene, t); }
    else {
      for (const S of states) { lpRestoreState(S); S.extendCap = null; }   /* no transition on: every state exactly as built (a seek is the play) */
      for (let i = 0; i < states.length; i++) lpPaintChart(states[i], i === cur ? cCur : 0, t3, scene, t, i === cur && leaving);
      if (hold) lpPaintMorphHold(st, hold, cCur);
    }
    for (let i = 0; i < states.length; i++) if (!park || i !== (st.active | 0)) lpUnpark(states[i]);
    if (park && !xf) lpPaintPark(states[st.active | 0], park, t, parkFrom);
    /* the words that describe the chart move with it: the standing sub and source erase over the transition's first
       PS.ERASE_S, the arriving state's write over the rest. State 0's are the page's own, written by the page's build. */
    let ink = 0, ue = 0, uw = 1;
    for (const sp of pageSpecies(scene, "chart_to")) {
      if (t < sp.at) break;
      if (sp.to === "rescale" || sp.to === "extend" || sp.to === "park") continue;   /* P48 T2/T3/T2b: the words stay - it is the same chart */
      const d = Math.max(PS.ERASE_S + 0.01, sp.dur || 1);
      ue = clamp01((t - sp.at) / PS.ERASE_S);
      uw = clamp01((t - sp.at - PS.ERASE_S) / (d - PS.ERASE_S));
      ink = Math.max(0, Math.min(states.length - 1, sp.state | 0));
    }
    for (let i = 1; i < states.length; i++) {
      const on = i === ink;
      /* the write runs PAST the last glyph (writeGlyphs gives each one 1.6 slots): a run that stops exactly at n leaves
         its final letters half-inked, which reads as a typo rather than as handwriting */
      for (const r of [states[i].subInk, states[i].srcInk]) if (r) writeGlyphs(r.glyphs, on ? uw * (r.glyphs.length + 2) : -1, r.glyphs.length);
    }
    if (ink > 0) for (const r of [{ glyphs: st.subGlyphs || [] }, { glyphs: st.srcGlyphs || [] }]) {
      const n = r.glyphs.length;
      r.glyphs.forEach((g, j) => g.style.setProperty("--w", eraseFactor(n, j, ue).toFixed(3)));
    }
  };
  /* HF-16 (P50 T15) - THE WIRE, in the player. The arriving page's plate id named a mark on the page BEFORE it
     (`;thread=<mark key>`); this builds that mark into the new page's own chart, standing on the pixels it already
     stood on, as GROUND under everything the page is about to draw. It runs ONCE per page state - the carry is a
     similarity, not a per-frame decision - and after that the wire is an ordinary keyed mark on this page, riding
     its park, its rescale and the camera with the rest of it. A source the player cannot find (a thread named
     across a non-page, a mark that page never drew) leaves the page exactly as it would have been: the compiler
     refuses those at build time, and the player never guesses. */
  /* an <svg> has no offsetLeft: the chart's box is its CSS box, which both layouts set explicitly (portrait in px,
     landscape in %) and which getComputedStyle resolves to used pixels against the stage-sized .lp. It carries NO
     transform, so the carry is the same number whatever the page happens to be doing when it is computed. */
  const lpChartBox = (ch) => { const cs = getComputedStyle(ch);
    return { x: parseFloat(cs.left) || 0, y: parseFloat(cs.top) || 0, w: parseFloat(cs.width) || 0, h: parseFloat(cs.height) || 0 }; };
  const lpThreadSource = (from) => {
    for (const id of ["wA", "wB"]) { const s = ledgerState.get(id + "|" + from); if (s && s.chart && s.chart.isConnected) return s; }
    return null;
  };
  const lpThread = (st, scene) => {
    st.thread = { el: null };   /* set FIRST: a page whose source is not there tries once, not every frame */
    const th = (scene.world.page || {}).thread;
    if (!th || !th.key) return;
    const src = lpThreadSource(th.from);
    const mk = src && src.markBy ? src.markBy[th.key] : null;
    if (!mk || !mk.geom || !Array.isArray(mk.geom.pts) || !src.geom || !st.geom) return;
    const sb = lpChartBox(src.chart), db = lpChartBox(st.chart);
    if (!(sb.w > 0 && sb.h > 0 && db.w > 0 && db.h > 0)) { st.thread = null; return; }   /* not laid out yet: try again next frame */
    const sf = threadFit(sb, src.geom.W, src.geom.H);
    const df = threadFit(db, st.geom.W, st.geom.H);
    const pts = threadCarry(mk.geom.pts, sf, df);
    if (!pts) return;
    const sw = parseFloat(getComputedStyle(mk.el).strokeWidth) || 4;
    const p = lpEl("path", "ser thread", st.chart, { d: threadPath(pts), fill: "none", stroke: mk.geom.col || "#aeb6be",
      "stroke-width": threadWidth(sw, sf, df).toFixed(2), "stroke-linecap": "round", "stroke-linejoin": "round", opacity: 0 });
    st.chart.insertBefore(p, st.chart.firstChild);   /* the wire is GROUND: the new page's ink reads on top of it */
    lpMark(st, "thread:" + th.key, "line", p, { pts, vals: mk.geom.vals || [], len: 0, k0: 0, muted: true, col: mk.geom.col, thread: true });
    st.thread.el = p;
  };
  const paintLedger = (el, scene, t) => {
    const st = ledgerState.get(el.id + "|" + scene.scene_id) || buildLedger(el, scene);
    const pg = scene.world.page || {};
    if (!st.root.isConnected) { el.querySelectorAll(".lp").forEach((x) => x.remove()); el.appendChild(st.root); }
    if (!st.thread) lpThread(st, scene);   /* HF-16: after the page is in the DOM, so both charts have a layout box */
    const morphOn = pg.enter === "morph" && kin("arap_morph"), morphS = morphOn ? (pg.morph_s || MORPH.S) : 0;   /* P47 T3: the prop becomes the chart */
    const built = pg.enter === "built";   /* arrives with its chart drawn: the span is all deployed life, the idle keeps it alive */
    const snap = pg.enter === "snap";   /* the third watch: the thrown card BECOMES the world - the page arrives built and grows from the card's rectangle to the stage over SNAP_S */
    const camIn = pg.enter === "camera";   /* P49 T5: the page arrives built and the EYE went to the card - it shows at the match, at identity */
    const card = pg.card === true || (pg.card !== false && (pg.enter === "snap" || camIn));   /* a snapped (or camera-arrived) page is a card unless told otherwise */
    st.page.classList.toggle("card", card);
    el.classList.toggle("cardworld", card);
    const dropped = pg.enter === "drop";   /* operator, 2026-09-08: "is falling down into the frame easier?" - yes: the dock's landXf (weight first,
       the drop easing in, the impact, the settle) with the drop from above the frame; a full-size page falls onto the world and lands as it. No
       leaving the frame, no growth, nothing to clip. */
    const thrown = pg.enter === "throw";   /* operator, 2026-09-08: "throw the chart onto the plate ... the transition is literally the plate entering the world" -
       the whole page flies in on the pills' own kinetics (throwXf: a ballistic chord, the tumble, the material's squash and settle) and arrives built */
    const mount = pg.enter === "mount" || (pg.enter === "morph" && !morphOn);   /* a morph with its flag off is a mount of the same length */
    const mountS = mount ? (pg.mount_s || pg.morph_s || LP.FIELD) : 0;   /* the mount phase: the world fades, the cream builds; then the page's clock starts at ROLL + SAVOR (no roll, no savor) */
    const tr = t - scene.span[0] + ((pg.enter === "spiral" || snap || camIn || built || thrown || dropped) ? LP_FOCUS_AT + LP_BADGE0 + LP_BADGE_STEP * ((st.badges || []).length + 1) : mount ? LP.ROLL - mountS : morphOn ? (LP.ROLL + LP.SAVOR + LP.FIELD + LP.PUNCH) - morphS : 0);   /* a spiral entry ARRIVES built: its beats are all past; a MOUNT is the roll-out (E45 s2): its cream builds over mount_s, then the SAVOR holds the empty page before the ink; a MORPH skips the roll, the savor and the soak - the board is there, the prop morphs, the build starts as it ends */
    /* beat 1: roll-out */
    const rk = (mount || morphOn || snap) ? 1 : expoOut(clamp01(tr / LP.ROLL));   /* a mounting page is in place from its first frame; it RISES (below) with the cream steps */
    /* HF-16: the wire recedes from the instant the CHART layer comes up - the build drives that layer's opacity, so a
       recede timed from the scene's first frame would be over before any of it had been seen. `tr` is the page's own
       clock with every entry already folded into it, so this stays a pure function of t. */
    if (st.thread && st.thread.el) st.thread.el.setAttribute("opacity", threadPose(tr - (LP.ROLL + LP.SAVOR + LP.FIELD + LP.PUNCH)).alpha.toFixed(3));
    const mu = mount ? clamp01((t - scene.span[0]) / mountS) : 1;
    const lpDance = (u) => { if (u >= 1) return 1; const k = Math.floor(u * MOUNT_STEPS), f = u * MOUNT_STEPS - k; return (k + clamp01((f - 0.5) / 0.5)) / MOUNT_STEPS; };
    const mk = mount ? Math.floor(mu * MOUNT_STEPS) / MOUNT_STEPS : 1;
    if (mount) { st.page.style.opacity = lpDance(mu).toFixed(4); }   /* the CREAM builds beneath the fading world, in the other half of each step */
    /* (the roll-out translate is composed with the punch below) */
    st.edge.style.opacity = (mount ? 0 : 1 - clamp01((tr - LP.ROLL) / 0.25)).toFixed(2);   /* no roll edge on a mount */
    /* beat 2: the half savor - the textured page holds, empty (E22 addendum 2) */
    /* beat 3: the field. SOAK: seeps spread and saturate, never contract - paper taking ink;
       SCRIBBLE: strokes accumulate one at a time with the nib at the front. Either ends on the
       crisp rect. */
    const b = morphOn ? 1 : clamp01((tr - LP.ROLL - LP.SAVOR) / LP.FIELD);   /* a mount's soak begins a savor after its cream is full (tr reaches ROLL at mount_s; E45 s2: the savor stays); a morph page's board is soaked from its first frame */
    for (const bl of st.blobs) {
      /* STEP MOTION under km_ink (operator: "too smooth"): a stain's progress is a seeded staircase on the stepped clock, its own phase */
      const u = kin("km_ink") ? soakStepped(clamp01((b - bl.lag) / (1 - bl.lag)), (k) => lpHash(st.seed, bl.i + 1, 200 + k)) : clamp01((b - bl.lag) / (1 - bl.lag));
      bl.c.setAttribute("transform", "translate(" + bl.cx.toFixed(1) + " " + bl.cy.toFixed(1) + ") scale(" + (bl.R * Math.pow(u, 1.5)).toFixed(2) + ")");   /* stains creep, then flood */
      bl.c.setAttribute("opacity", ((0.55 + 0.45 * u) * (kin("km_ink") ? INK.COVERAGE : 1)).toFixed(2));
    }
    if (st.soakFx && b > 0 && b < 1) {   /* the fields move only while the soak runs: idle frames touch nothing */
      const bq = stepClock(b), a = soakAnim(bq, st.soakFk), j = soakJitter(bq, (k) => lpHash(st.seed, 7, k), st.soakFk), fx = st.soakFx;
      const set = (el, v) => { if (el) { el.setAttribute("dx", v[0].toFixed(1)); el.setAttribute("dy", v[1].toFixed(1)); } };
      set(fx.wob, [a.wob[0] + j[0], a.wob[1] + j[1]]); set(fx.att, a.att); set(fx.grain, a.grain);
      if (fx.disp) fx.disp.setAttribute("scale", a.scale.toFixed(1));
    }
    if (st.strokes.length) {
      const n = st.strokes.length, per = 1 / n;
      let nibAt = null;
      st.strokes.forEach((sk, i) => {
        const fr = clamp01((b - i * per) / (per * 1.15)), f = strokeFrac(sk.p, sk.len, fr) ?? fr;
        sk.p.setAttribute("stroke-dashoffset", (sk.len * (1 - f)).toFixed(1));
        sk.p.setAttribute("opacity", f > 0 ? 1 : 0);   /* a round cap shows even at full offset */
        if (f > 0 && f < 1 && sk.p.getPointAtLength) nibAt = sk.p.getPointAtLength(sk.len * f);
      });
      st.nib.setAttribute("opacity", nibAt ? 1 : 0);
      if (nibAt) { st.nib.setAttribute("cx", nibAt.x.toFixed(1)); st.nib.setAttribute("cy", nibAt.y.toFixed(1)); }
    }
    st.rect.setAttribute("opacity", clamp01((b - 0.78) / 0.22).toFixed(2));
    if (st.fieldPlate) st.fieldPlate.style.opacity = expoOut(b).toFixed(3);   /* the inked plate arrives over the cream */
    /* beat 4: ink writes title/source once the field has soaked - no outline (E22 addendum 7: the deckle is the edge) */
    const t3 = tr - LP.ROLL - LP.SAVOR - LP.FIELD;
    const n = Math.max(1, st.glyphs.length), per = LP.INK / n;
    st.glyphs.forEach((g, j) => g.style.setProperty("--w", clamp01((t3 - j * per) / (per * 1.6)).toFixed(3)));
    /* beat 5: PUNCH IN on the board - the line and the deckle margin are the room we spend (E22 addendum 6) */
    const pk = (pg.punch === false || PORTRAIT) ? 0 : expoOut(clamp01(t3 / LP.PUNCH));   /* a host plate skips the punch: his gesture is the direction; portrait has no margin to spend (P41) */
    const bdc = st.boardCentre || { x: 50, y: 50 };
    st.page.style.transformOrigin = bdc.x.toFixed(2) + "% " + bdc.y.toFixed(2) + "%";
    let snapCss = "";
    if (snap) {   /* the page's own charcoal board (measured once, untransformed) onto the card's box (from the dock loop): board -> card at u = 0, the page itself at u = 1 */
      if (!st.snapBoard) {
        const stage = document.getElementById("stage").getBoundingClientRect(), k = stage.width / (PORTRAIT ? 1080 : 1920);
        const saved = st.page.style.transform; st.page.style.transform = "none";
        const bd = st.field.getBoundingClientRect(); st.page.style.transform = saved;
        st.snapBoard = { x: (bd.x - stage.x) / k, y: (bd.y - stage.y) / k, w: bd.width / k, h: bd.height / k };
      }
      const S = { board: st.snapBoard, card: SNAP_RECT[pg.snap_from] || null }, u = minJerk(clamp01((t - scene.span[0]) / SNAP_S));
      if (S.card && S.board.w > 0 && S.board.h > 0) {
        const sx0 = S.card.w / S.board.w, sy0 = S.card.h / S.board.h;
        const sx = sx0 + (1 - sx0) * u, sy = sy0 + (1 - sy0) * u;
        const tx = (S.card.x - S.board.x * sx0) * (1 - u), ty = (S.card.y - S.board.y * sy0) * (1 - u);
        st.page.style.transformOrigin = "0 0";
        snapCss = "translate(" + tx.toFixed(2) + "px," + ty.toFixed(2) + "px) scale(" + sx.toFixed(5) + "," + sy.toFixed(5) + ") ";
        /* THE WHOOSH (operator, 2026-09-08: "zoom pan frame would work if the zoom is fast with a woosh to full size"): a motion blur
           on a VELOCITY envelope - 4u(1-u), exactly 0 at both ends and peaking where the snap moves fastest - the mechanism ported from
           remotion-ui's zoom-through (a blur taken linearly off displacement is at full strength where the card is arriving, so the
           landing reads soft; on the speed it lands crisp). SNAP_BLUR px at the peak, a dial. */
        const speed = 4 * u * (1 - u), blur = SNAP_BLUR * speed;
        st.page.style.filter = blur > 0.2 ? "blur(" + blur.toFixed(2) + "px)" : "";
      } else st.page.style.filter = "";
    }
    let throwCss = "";
    if (dropped) {   /* THE DROP: landXf from DROP_FROM_H above the rest, the drop easing in (gravity) over drop_s, the paper landing */
      const tt = t - scene.span[0], Ds = +pg.drop_s > 0 ? +pg.drop_s : DROP_S;
      const sx = landXf(scene.world.mass || "paper", tt, { DROP_PX: STAGE_H * DROP_FROM_H, DROP_S: Ds, ANTIC_S: 0 });
      const sxPage = Object.assign({}, sx, { alpha: (sx.alpha || 0) * THROW_SQUASH });
      st.page.style.transformOrigin = "50% 100%";   /* the squash on the hit is about the contact edge */
      throwCss = stopCss(sxPage).trim() + " ";
      const h = Math.max(0, -(sx.y || 0));
      st.throw = { h, u: clamp01(tt / Ds), phase: sx.phase, landed: tt >= Ds, ground: sx.ground || 0, shake: sx.shake || { x: 0, y: 0 }, follow: 0 };
    } else if (thrown) {   /* THROW_FROM is where the flight starts, as an offset from the page's rest (px); the arc lifts against it */
      const from = THROW_FROM[pg.throw_from] || THROW_FROM.below, F = +pg.throw_s > 0 ? +pg.throw_s : THROW_S, tt = t - scene.span[0];
      const sx = throwXf(from, scene.world.mass || "paper", tt, { FLIGHT_S: F, ARC: THROW_ARC, SPIN_DEG: THROW_SPIN });
      const u = clamp01(tt / F), landed = tt >= F;
      /* THE CARD LEAVES THE FRAME (operator, 2026-09-08, on the depth-arc draft that passed the camera at 1.8x: "it shouldn't cut and
         clip like that ... what it's supposed to do is LEAVE the frame, not cut and clip ON the frame"). So the page is a CARD for the
         whole rise - THROW_CARD of the stage, the dock's size, seen whole - thrown up on an arc tall enough that it goes out of the
         top of the frame entirely, and it GROWS into the world only on the way back down (z from 1/THROW_CARD to 1 by min-jerk over
         the descent, apparent size 1/z), so that at the contact it is the stage. It pitches under a real perspective - steep as it
         leaves the bottom edge, flat at the landing - and the motion squash (42 s42.3) reads as paper flex. `throw_grow: "snap"`
         keeps the earlier flat growth timed to SNAP_S for comparison. */
      let scaleK, pitch = 0;
      if (pg.throw_grow === "snap") {
        scaleK = landed ? 1 : THROW_CARD + (1 - THROW_CARD) * minJerk(clamp01((tt - (F - SNAP_S)) / SNAP_S));
      } else {
        /* the card is card-sized for the WHOLE flight and grows to the stage AFTER the contact, in place, over SNAP_S - the snap on
           the landing. Growing any earlier puts its top out of the frame while it is still above its rest (0.5 and 0.8 both did,
           "it is cut off"); a card that lands whole and then becomes the world is the only version that never clips. */
        const g = landed ? minJerk(clamp01((tt - F) / SNAP_S)) : 0;
        const z = (1 / THROW_CARD) * (1 - g) + 1 * g;
        scaleK = 1 / z;
        pitch = landed ? 0 : -THROW_PITCH * Math.pow(1 - u, 1.5);
      }
      const bend = landed ? 0 : (sx.alpha || 0) * THROW_BEND;
      st.page.style.transformOrigin = "50% 50%";
      /* the motion squash is DAMPED for a page: at page speed (thousands of px/s) squashAlpha reaches ~0.25, which stretched the
         page to 120 % of the stage and pushed its title out of the top of the frame ("it is cut off", operator 2026-09-08,
         measured: page 2969 px tall in a 2485 px stage at u 0.94). A card the size of the stage flexes a few percent, not a quarter. */
      const sxPage = Object.assign({}, sx, { alpha: (sx.alpha || 0) * THROW_SQUASH });
      throwCss = "perspective(" + THROW_PERSP + "px) " + stopCss(sxPage).trim() + " rotateX(" + (pitch + bend).toFixed(2) + "deg) scale(" + scaleK.toFixed(4) + ") ";
      /* what the WORLD does about it, read by the transition block: the camera FOLLOWS the card (the worlds ride THROW_FOLLOW of its
         height, so the frame tilts up with the throw and settles with the landing), the ground takes the dip and any shake, and the
         contact shadow darkens the world beneath as the card comes down */
      const h = Math.max(0, -(sx.y || 0));
      st.throw = { h, u, phase: sx.phase, landed, ground: sx.ground || 0, shake: sx.shake || { x: 0, y: 0 },
                   follow: landed ? 0 : THROW_FOLLOW * h };
    } else st.throw = null;
    const cardCss = card ? "scale(" + CARD_SCALE + ") " : "";   /* the card's rest size: a little smaller than the stage, the world around it */
    st.page.style.transform = snapCss + throwCss + cardCss + "translateX(" + ((rk - 1) * 100).toFixed(2) + "%) " + (mount ? "translateY(" + ((1 - mk) * LP_MOUNT_RISE).toFixed(1) + "px) " : "") + "scale(" + (1 + (LP.PUNCH_SCALE - 1) * pk).toFixed(4) + ")"
      + idleCssFor("page", pg.idle, t, st.seed, 1);   /* E49: the page breathes while it holds under a sentence */
    /* beat 6: the build - crisp, landing on the exact strings - on the punched page */
    const c = clamp01((t3 - LP.PUNCH) / (st.buildDur || LP.BUILD));   /* race/decline/combo declare their own envelope */
    /* P48 T4: a page may carry more than one chart. `lpPaintChart` is the build beat for ONE of them, at its own
       fraction c - and because every builder's law is written as "at c the chart is this far drawn", running c back
       to zero IS an un-draw, whatever the builder. That is what a recast leaves on. */
    lpPaintStates(st, scene, c, t3, t);
    if (morphOn) paintMorph(st, pg, scene.world, clamp01((t - scene.span[0]) / morphS), c);   /* P47 T3: the prop becomes the area under the line, then the line draws over it */
    /* badges: floored at the build's end, each springs in over LP_BADGE_IN with the dock's back-out overshoot */
    const tb = t3 - LP.PUNCH - (st.buildDur || LP.BUILD);
    const arrP = arriveOf(scene.world), massP = scene.world.mass || "paper";   /* P47 T1: the page's pills may ARRIVE by a throw or a landing (`;arrive=land;mass=metal` on the plate id - the compiler writes it on the world) */
    for (const bd of st.badges || []) {
      if (arrP !== "spring") {
        const tp = tb - bd.at, bi = (st.badges || []).indexOf(bd);
        const sx = arrP === "throw" ? throwXf({ x: -(STOP_THROW_DX + 80 * bi), y: -STOP_THROW_DY }, massP, tp) : landXf(massP, tp);
        bd.el.style.opacity = tp >= 0 ? "1" : "0";
        bd.el.style.transform = stopCss(sx) + idleCssFor("pill", pg.idle === "none" ? "none" : undefined, t, st.seed, 20 + bi);
        continue;
      }
      const ub = clamp01((tb - bd.at) / LP_BADGE_IN), e = (kin("analytic_spring") ? springPop : stagePop)(ub);
      bd.el.style.opacity = Math.min(1, e * 1.4).toFixed(3);
      /* SQUASH (42 s42.3, P43 T4, kinetics.area_squash + analytic_spring): the badge travels 18 px up; its spring's velocity and
         deceleration set alpha, the tensor stretches along the travel and compresses across it, area kept */
      const sq = kin("area_squash") && kin("analytic_spring") && ub > 0 && ub < 1
        ? " matrix(" + squashMatrix(Math.PI / 2, springSquash(ub, POP, 18, LP_BADGE_IN)).map((v) => v.toFixed(4)).join(",") + ",0,0)" : "";
      bd.el.style.transform = "translateY(" + (18 * (1 - e)).toFixed(1) + "px) scale(" + (0.94 + 0.06 * e).toFixed(4) + ")" + sq
        + idleCssFor("pill", pg.idle === "none" ? "none" : undefined, t, st.seed, 20 + (st.badges || []).indexOf(bd));   /* E49: each pill at its own phase */
    }
    paintPerform(st, scene, t, pg);   /* P47 T2: the bracket, the retitle, the relight - on the page, on the word */
    lpSpiral(st, scene, t, pg);   /* the retract at the scene's end; the spiral entry at its start */
  };

  /* ================= MOTION MENU species (doc 29 s9.27; P35 T6 / T7) =================
     The targeting law as code: every species takes a DECLARED target and resolveTarget maps it to
     stage pixels at render time (a datum on a ledger page, a point/region of the frame, a caption
     word span). Camera moves (punch / focus_zoom / pull_back) are ONE transform on the world layer -
     docks stay fixed in screen space (this lane's drawing surface) - and are exclusive per window
     (build validate_species + gate M09). Plate life quantizes t to 10 fps FIRST and derives every
     pose from the step (stop-motion law). Everything from t; jitter only via lpHash. */
  const SP = { PUNCH_IN: 0.42, PUNCH_OUT: 0.5, PUNCH_SCALE: 1.14, FOCUS_SCALE: 1.32, PULL_FROM: 1.9,
               CALLOUT_DRAW: 0.7, SQUIG_DRAW: 0.45, LIFE_FPS: 10, LIFE_LAND: 0.6, BOIL_PX: 1.2, BOIL_DEG: 0.7,
               SPOT_DIM: 0.49,   /* operator 2026-09-03: 0.55 was 'way too dark', 0.44 too light - settled at 0.49 */
               STEAM_PERIOD: 2.6, TRACE_PERIOD: 3.2, TRACE_DRAW: 1.1, TICK_STEP: 0.5 };   /* STILL LIFE (2026-09-05): steam, trace, ticker */
  const CAMERA = new Set(["punch", "focus_zoom", "pull_back"]);
  const SPOT_R_PORTRAIT = 960;   /* PORTRAIT ? the spotlight's gradient radius keeps its landscape size (a round hole the width of the short side), userSpaceOnUse - the one landscape number kept on purpose */
  const spTop = $("species"), spUnder = $("species-under"), plife = $("plife");
  let spSvg = spTop;   /* the layer the species painter draws into - chosen per species in paintSpecies */
  const spEase = (k) => 1 - Math.pow(1 - clamp01(k), 3);
  const spIO = (k) => { k = clamp01(k); return k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; };
  /* an element's box in STAGE px (the stage is scaled to fit the pane) */
  const stageBox = (el) => { const r = el.getBoundingClientRect(), sb = $("stage").getBoundingClientRect(); const k = STAGE_W / Math.max(1, sb.width); return { x: (r.left - sb.left) * k, y: (r.top - sb.top) * k, w: r.width * k, h: r.height * k }; };
  const resolveTarget = (tg) => {
    if (!tg) return null;
    if (tg.kind === "point") return { x: tg.x * STAGE_W, y: tg.y * STAGE_H, w: 0, h: 0 };
    if (tg.kind === "region") return { x: tg.x0 * STAGE_W, y: tg.y0 * STAGE_H, w: (tg.x1 - tg.x0) * STAGE_W, h: (tg.y1 - tg.y0) * STAGE_H };
    if (tg.kind === "datum") {   /* the ledger page's bar, or a point on its dense line */
      const world = wB.classList.contains("ledger") ? wB : wA;
      const bars = world.querySelectorAll(".lp-chart .bar");
      if (bars.length) return stageBox(bars[Math.min(tg.index | 0, bars.length - 1)]);
      /* viewBox -> stage px under the default xMidYMid meet (the landscape chart is letterboxed in its box) */
      const vbMap = (svg, q) => { const b = stageBox(svg), vb = svg.viewBox.baseVal, k = Math.min(b.w / vb.width, b.h / vb.height);
        return { x: b.x + (b.w - vb.width * k) / 2 + q.x * k, y: b.y + (b.h - vb.height * k) / 2 + q.y * k, w: 0, h: 0 }; };
      const lpst = world.__lp, pts = lpst && lpst.linePts ? lpst.linePts[tg.series | 0] : null;
      if (pts && pts.length) {   /* the exact datum (P41): the builder's own point, never a length fraction */
        const q = pts[Math.max(0, Math.min(tg.index | 0, pts.length - 1))]; return vbMap(lpst.chart, { x: q[0], y: q[1] });
      }
      const ser = world.querySelectorAll(".lp-chart .ser")[tg.series | 0];
      if (ser && ser.getPointAtLength) {
        const q = ser.getPointAtLength(ser.getTotalLength() * clamp01((tg.index | 0) / Math.max(1, (tg.count || 100) - 1)));
        return vbMap(ser.ownerSVGElement, q);
      }
      return null;
    }
    if (tg.kind === PHRASE_KIND) {   /* P50 T3: a region INSIDE a press card, resolved through that card's LIVE
         geometry - a parked or stacked card moves, and what points at it moves with it. Off stage: nothing. */
      const p = PRESS_POSE[tg.dock];
      return p && p.phrase ? p.phrase : null;
    }
    if (tg.kind === "span") {
      const ws = [...cap.querySelectorAll(".cw")].slice(tg.from_word | 0, (tg.to_word | 0) + 1);
      if (!ws.length) return null;
      const bs = ws.map(stageBox);
      const x0 = Math.min(...bs.map((b) => b.x)), x1 = Math.max(...bs.map((b) => b.x + b.w));
      const y0 = Math.min(...bs.map((b) => b.y)), y1 = Math.max(...bs.map((b) => b.y + b.h));
      return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
    }
    return null;
  };
  const centre = (b) => ({ cx: b.x + b.w / 2, cy: b.y + b.h / 2 });
  /* the camera: one world transform for this window, about the resolved target */
  const camXf = (sc, t) => {
    let xf = { s: 1, ox: STAGE_W / 2, oy: STAGE_H / 2 };   /* the stage's centre, not the landscape's (2026-09-08: 960/540 zoomed a portrait short about the wrong point) */
    for (const sp of (sc.species || [])) {
      if (!CAMERA.has(sp.kind)) continue;
      const k = (t - sp.at) / Math.max(0.001, sp.dur || 1);
      if (k < 0 || k > 1) continue;
      const b = resolveTarget(sp.target); if (!b) continue;
      const { cx, cy } = centre(b);
      if (sp.kind === "punch") {           /* in - hold - out, cubic ease (yt-camera-move) */
        const tin = SP.PUNCH_IN / (sp.dur || 1), tout = SP.PUNCH_OUT / (sp.dur || 1);
        const a = k < tin ? spEase(k / tin) : k > 1 - tout ? 1 - spEase((k - (1 - tout)) / tout) : 1;
        xf = { s: 1 + (SP.PUNCH_SCALE - 1) * a, ox: cx, oy: cy };
      } else if (sp.kind === "focus_zoom") { /* zoom + pan to the anchor, then dead still (servo law) */
        xf = { s: 1 + (SP.FOCUS_SCALE - 1) * spIO(Math.min(1, k * 1.8)), ox: cx, oy: cy };
      } else {                             /* pull-back: opens ON the number, one decelerating pull */
        xf = { s: SP.PULL_FROM + (1 - SP.PULL_FROM) * spEase(k), ox: cx, oy: cy };
      }
    }
    return xf;
  };
  /* P49 T2: the persistent camera. Behind kinetics.camera the three species run through kinetics/camera.mjs (their
     envelopes factored, the CSS byte-identical) and a scene's authored `camera.keys` drive a pan or a zoom; the state is
     {s, ox, oy, ax, ay}: the world point looked at and the screen point it lands on (ax == ox: a zoom in place, as every
     species is). With the flag off camXf paints exactly as it always has. */
  const camLook = (v) => {   /* a key's look / at: [x, y] stage fractions, or a declared target's centre */
    if (Array.isArray(v)) return [v[0] * STAGE_W, v[1] * STAGE_H];
    const b = resolveTarget(v); if (!b) return null; const { cx, cy } = centre(b); return [cx, cy];
  };
  let camArr = null;   /* P49 T5: this frame's camera arrival, when one is on - set by render, read by camNow for the outgoing scene */
  const camNow = (sc, t) => {
    if (camArr && camArr.scene === sc) return camArr.state;   /* the eye is going to the card: the outgoing world rides the arrival */
    if (!kin("camera")) return camXf(sc, t);
    const keys = ((sc.camera || {}).keys || []);
    let st = null;
    if (keys.length) {
      const K = keys.map((k) => ({ t: k.t, zoom: k.zoom, ease: k.ease, look: camLook(k.look) || [STAGE_W / 2, STAGE_H / 2], at: k.at != null ? (camLook(k.at) || undefined) : undefined }));
      st = camKeyState(K, t, STAGE_W, STAGE_H);
    } else if ((sc.camera || {}).attention === "landings") {   /* P49 T4: a landing pulls the eye; the contact frame is the stop-action clock's */
      st = camAttentionState(sc.docks, t, (d) => +d.enter + (d.arrive === "throw" ? STOP.FLIGHT_S : STOP.ANTIC_S + STOP.DROP_S), ATTN) || camIdentity(STAGE_W, STAGE_H);
    } else {
      for (const sp of (sc.species || [])) {
        if (!CAMERA.has(sp.kind)) continue;
        const k = (t - sp.at) / Math.max(0.001, sp.dur || 1); if (k < 0 || k > 1) continue;
        const b = resolveTarget(sp.target); if (!b) continue; const { cx, cy } = centre(b);
        const s2 = camSpeciesState(sp.kind, k, [cx, cy], sp.dur || 1, SP); if (s2) st = s2;
      }
      if (!st) st = camIdentity(STAGE_W, STAGE_H);
    }
    return { s: st.s, ox: st.look[0], oy: st.look[1], ax: st.at[0], ay: st.at[1] };
  };
  const camCss = (xf) => (xf.ax != null && (xf.ax !== xf.ox || xf.ay !== xf.oy)) ? camCssFor({ s: xf.s, look: [xf.ox, xf.oy], at: [xf.ax, xf.ay] }, STAGE_W, STAGE_H) : xf.s === 1 ? "" :
    "translate(" + (xf.ox - STAGE_W / 2).toFixed(1) + "px, " + (xf.oy - STAGE_H / 2).toFixed(1) + "px) scale(" + xf.s.toFixed(4) + ") translate(" + (STAGE_W / 2 - xf.ox).toFixed(1) + "px, " + (STAGE_H / 2 - xf.oy).toFixed(1) + "px) ";
  /* a wobbled ellipse around a box (hw-callout-circle): seeded, drawn by dash-offset */
  const calloutPath = (b, seed, pad) => {
    const pd = Number.isFinite(+pad) ? +pad : 0;   /* a datum resolves to a point: `pad` is how wide the hand rings it (the fifth watch) */
    const cx = b.x + b.w / 2, cy = b.y + b.h / 2, rx = b.w / 2 + 22 + pd, ry = b.h / 2 + 18 + pd, n = 28, pts = [];
    for (let i = 0; i <= n; i++) { const a = -Math.PI * 0.6 + i / n * Math.PI * 2.08; const j = 1 + (lpHash(seed, i, 21) - 0.5) * 0.12;
      pts.push([cx + Math.cos(a) * rx * j, cy + Math.sin(a) * ry * j]); }
    return pts.map(([x, y], i) => (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ");
  };
  const squigglePath = (b, seed) => {
    const y = b.y + b.h + 6, n = Math.max(6, Math.round(b.w / 22)), pts = [];
    for (let i = 0; i <= n; i++) pts.push([b.x + b.w * i / n, y + (i % 2 ? 4 : -4) + (lpHash(seed, i, 23) - 0.5) * 3]);
    return pts.map(([x, yy], i) => (i ? "L" : "M") + x.toFixed(1) + " " + yy.toFixed(1)).join(" ");
  };
  /* THE STROKE (42 s42.1, P43 T2): under kinetics.curvature_stroke every dash-drawn path is a HAND - the pen slows into
     curvature and starts and stops from rest. The profile is sampled once per path geometry (the species layer is rebuilt
     every frame, so the cache is keyed by the d attribute) and inverted per frame. strokeFrac returns the drawn fraction of
     the path, or null when the flag is off so each caller keeps its own ease as the else branch - byte-identical goldens. */
  const STROKE_PROFILES = new Map();
  const strokeProf = (path, len) => {
    const key = path.getAttribute("d") + "|" + len.toFixed(2);
    let prof = STROKE_PROFILES.get(key);
    if (!prof) {
      if (STROKE_PROFILES.size > 96) STROKE_PROFILES.clear();
      const n = Math.max(STROKE.MIN_N, Math.min(STROKE.MAX_N, Math.round(len / STROKE.SAMPLE_PX))), pts = [];
      for (let i = 0; i < n; i++) { const q = path.getPointAtLength(len * i / (n - 1)); pts.push({ x: q.x, y: q.y }); }
      STROKE_PROFILES.set(key, prof = strokeProfile(pts));
    }
    return prof;
  };
  const strokeFrac = (path, len, u) => { if (!kin("curvature_stroke") || !path.getPointAtLength || !(len > 0)) return null;
    const prof = strokeProf(path, len); return prof.L > 0 ? strokeS(prof, u) / prof.L : u; };
  const drawOn = (path, k) => { const len = path.getTotalLength ? path.getTotalLength() : 1000; path.setAttribute("stroke-dasharray", len);
    const f = strokeFrac(path, len, clamp01(k)); path.setAttribute("stroke-dashoffset", (len * (1 - (f === null ? spEase(k) : f))).toFixed(1)); };
  /* THE SPECIES PAINTER REGISTRY (P50 T2; the operator's module rule, 2026-09-11: "no new species is written into
     the template's body"). Every species from T2 on is a module under content/video_engine/scripts/species/, inlined
     below exactly as a kinetics module is, registering its painter here as its last statement. paintSpecies looks the
     kind up before its own if/else chain, so every kind that shipped before this rule keeps its branch untouched and
     the goldens are byte-identical. The regions sit HERE - after lpEl, resolveTarget, spEase and drawOn, which a
     painter reaches by name through its context object - and before the first frame paints. P51 T1 (the runtime apart
     from the document) changes only how these modules are LOADED. Object.create(null): a kind name can never reach a
     prototype member and be called as a painter. */
  const SPECIES_PAINTERS = Object.create(null);
  /* KINETICS:BEGIN chip */
  /* species/chip.mjs - THE ICON CHIP (P50 T2; doc 29 s9.27's motion menu; the Bravos icon board, shots 26-28:
     predictions land as chips and are crossed out one by one). SOURCE OF TRUTH, inlined into the scene-evidence
     player by sync_kinetics.py between KINETICS:BEGIN chip and KINETICS:END, AFTER spring and idle - it imports
     both, and the import order IS the region order.
     THE MODULE RULE (the operator, 2026-09-11): a species is a module here, never a branch in the template's
     body. The last statement registers the painter in the template's SPECIES_PAINTERS registry; node, where no
     such registry exists, still imports the file for the pure math below.

     WHEN: the sentence names a THING as one of a SET (a prediction, an actor, a plant) - a chip lands on its
     word; a RETRACTS sentence ("none of this happened") crosses it out on a later word.

     THE LAW, all of it a pure function of t:
       land   - the badge spring (kinetics/spring.mjs springPop, the POP preset, Mp = 4 %) over LAND_S, from
                POP_FROM and DROP_PX above its place: R26-20's two-spring landing rides this one clock - the
                scale overshoots by Mp and settles, the drop rides the same x so the card never lands twice.
       hold   - opt-in `idle` (E49, one of IDLE_KINDS), applied exactly as the spotlight applies it: the idle's
                scale multiplies the landed scale, its offset moves the card, phased off the seed so two chips
                never breathe in step. Absent = declared stillness.
       cross  - `cross_at` draws a two-stroke X over the card by the template's drawOn (kinetics/stroke.mjs's
                curvature law when the flag is on, the species ease otherwise): the first stroke over the first
                half of CROSS_S, the second over the second, and the card dims to DIM as the X completes.
                `state: "crossed"` with no `cross_at` means the chip LANDS already crossed (the board is read
                back after the fact).
     Nothing is stored: every visual reads from t, sp.at and sp.cross_at, so a scrubbed frame is the played
     frame. The glyph is a SOURCED icon (assets/icons, A2a provenance) carried in the asset map as `icon:<name>`;
     this module never invents geometry. The dials below are ours to tune (42 s42.5), not findings. */

  const CHIP = Object.freeze({
    SIZE: 168,        /* the card's side in STAGE px - a chip is read at a glance beside its neighbours, not studied */
    RX: 22,           /* the rounded corner (the dock card's 14px radius, scaled to the smaller card) */
    GLYPH: 92,        /* the glyph's box inside the card: a little over half the side, so the card reads as a card */
    LABEL_DY: 46,     /* the label's baseline below the card's bottom edge */
    LAND_S: 0.55,     /* the landing's wall clock - the dock's DOCK_POP_S 0.45 plus a beat: a chip is lighter than a card and travels further */
    POP_FROM: 0.82,   /* the scale it springs from (the dock's DOCK_POP_FROM is 0.85) */
    DROP_PX: 34,      /* ... and how far above its place it falls from, on the same spring */
    FADE_S: 0.14,     /* the opacity ramp, the dock's DOCK_FADE_S 0.12 - never a pop out of nothing */
    CROSS_S: 0.5,     /* the X's two strokes together */
    DIM: 0.55,        /* what a crossed chip dims to - struck through, still legible (it is still one of the set) */
  });

  const chip01 = (v) => Math.min(1, Math.max(0, v));

  /* THE LANDING at t: the spring's normalised clock u, the scale it drives, the drop it rides and the fade. */
  const chipLand = (t, at, o = {}) => {
    const P = Object.assign({}, CHIP, o), u = chip01((t - at) / P.LAND_S), s = springPop(u);
    return { u, scale: P.POP_FROM + (1 - P.POP_FROM) * s, dy: (s - 1) * P.DROP_PX, fade: chip01((t - at) / P.FADE_S) };
  };

  /* THE CROSS at t in [0, 1]: 0 until cross_at, 1 CROSS_S later; a chip declared crossed is 1 from its landing. */
  const chipCrossF = (sp, t, o = {}) => {
    const P = Object.assign({}, CHIP, o);
    if (!Number.isFinite(+sp.cross_at)) return sp.state === "crossed" ? 1 : 0;
    return chip01((t - +sp.cross_at) / P.CROSS_S);
  };

  /* the two strokes of the X from the cross's fraction: the first over its first half, the second over the second */
  const chipStrokes = (f) => [chip01(f * 2), chip01(f * 2 - 1)];

  /* ONE ENTRY: everything the painter draws at t, from the declaration alone. */
  const chipPose = (sp, t, o = {}) => {
    const P = Object.assign({}, CHIP, o), land = chipLand(t, +sp.at, P), cross = chipCrossF(sp, t, P);
    return { u: land.u, scale: land.scale, dy: land.dy, fade: land.fade,
             cross, strokes: chipStrokes(cross), dim: 1 - (1 - P.DIM) * cross };
  };

  /* the sourced icon's geometry as the compiler embedded it: {vb: [x, y, w, h], el: [{t, a}]}, or null. */
  const chipGeometry = (raw) => {
    if (typeof raw !== "string" || !raw) return null;
    try { const g = JSON.parse(raw); return Array.isArray(g && g.el) && g.el.length ? g : null; } catch (e) { return null; }
  };

  /* THE PAINTER. ctx is the template's species context (see SPECIES_PAINTERS in the player): the declaration,
     the clock, the layer and the shared helpers by name. Draws into one group whose transform carries the
     landing and the idle, so every child is written in the card's own centred coordinates. */
  function paintChip(ctx) {
    const { sp, t, svg, el, A, resolveTarget, drawOn, hash, idle, seed, si } = ctx;
    const b = resolveTarget(sp.target);
    if (!b) return;   /* the targeting law: no resolved target, nothing painted */
    const pose = chipPose(sp, t);
    const ix = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 991)) : { scale: 1, dx: 0, dy: 0 };
    const cx = b.x + b.w / 2, cy = b.y + b.h / 2;   /* a point resolves to w = h = 0; a region centres the chip in it */
    const s = pose.scale * ix.scale;
    const g = el("g", "", svg, { opacity: pose.fade.toFixed(3),
                                 transform: "translate(" + (cx + ix.dx).toFixed(1) + " " + (cy + pose.dy + ix.dy).toFixed(1) + ") scale(" + s.toFixed(4) + ")" });
    const body = el("g", "", g, { opacity: pose.dim.toFixed(3) });   /* the card dims under its own X; the X does not */
    const h = CHIP.SIZE / 2;
    el("rect", "chipcard", body, { x: (-h).toFixed(1), y: (-h).toFixed(1), width: CHIP.SIZE, height: CHIP.SIZE, rx: CHIP.RX });
    const geo = chipGeometry(A ? A["icon:" + sp.icon] : null);
    if (geo) {
      const vb = geo.vb || [0, 0, 24, 24], k = CHIP.GLYPH / Math.max(vb[2] || 1, vb[3] || 1);
      const gg = el("g", "chipglyph", body, { transform: "translate(" + (-CHIP.GLYPH / 2).toFixed(1) + " " + (-CHIP.GLYPH / 2).toFixed(1) + ") scale(" + k.toFixed(4) + ") translate(" + (-vb[0]) + " " + (-vb[1]) + ")" });
      geo.el.forEach((n) => el(n.t, "", gg, n.a));   /* the sourced geometry verbatim - the compiler already kept only shapes */
    }
    if (sp.label) {
      const lab = el("text", "chiplab", body, { x: 0, y: (h + CHIP.LABEL_DY).toFixed(1) });
      lab.textContent = sp.label;
    }
    if (pose.cross > 0) {   /* the two-stroke X, drawn by the curvature stroke over the card's diagonals */
      const a = CHIP.SIZE * 0.34;
      [["M" + (-a).toFixed(1) + " " + (-a).toFixed(1) + " L" + a.toFixed(1) + " " + a.toFixed(1), pose.strokes[0]],
       ["M" + a.toFixed(1) + " " + (-a).toFixed(1) + " L" + (-a).toFixed(1) + " " + a.toFixed(1), pose.strokes[1]]]
        .forEach(([d, f]) => { if (f > 0) drawOn(el("path", "sq", g, { d }), f); });
    }
  }

  /* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
     import this file for the math above without the template's registry */
  if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.chip = paintChip;
  /* KINETICS:END */
  /* KINETICS:BEGIN press */
  /* species/press.mjs - THE PRESS CARD STACK (P50 T3; doc 29 §9.27 rows "Push hand-off" and "Squiggle marks";
     Bravos shots 5-10: their claims arrive as cards, and each new one pushes the last back into a lit pile).
     SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN press
     and KINETICS:END, AFTER ease and spring - it imports both, and the import order IS the region order.

     THE MODULE RULE (the operator, 2026-09-11) applies, with one difference from chip.mjs: a press card is a
     DOCK kind, not a species kind, so this module registers NO painter. The dock loop owns the card (a card is
     a card: the frame, the masthead, the lifecycle) and reads its whole pose from the pure functions here; the
     only thing new to the SPECIES grammar is the `phrase` target and the `underline` form of a callout, whose
     clock is underlineFrac below.

     WHEN: the sentence QUOTES someone (SPECIES-BY-SENTENCE row 1). One card is a quotation; a STACK is a
     sequence of them - three claims on three words, the newest lit and the older ones fanned behind it.

     THE LAW, all of it a pure function of t through uNew (the NEWEST card's landing fraction):
       land   - the newest card lands on the badge spring (kinetics/spring.mjs springPop, the POP preset,
                Mp = 4 %) over LAND_S, from POP_FROM and DROP_PX above its place - the dock's own arrival.
       push   - every OLDER card moves from the pose it held one step forward to the pose of its new depth,
                on Flash & Hogan's minimum-jerk quintic over PUSH_S (shorter than LAND_S: the pile has taken
                the push before the newest has finished overshooting - cause, then effect, never in step).
                The hand-off itself is §9.27's push: x (PUSH_DX), scaleX (SQUEEZE) and skewX (SKEW_DEG) on a
                sin(pi p) pulse, zero at both ends - the shove reads on the card being pushed, and leaves
                nothing behind. Never a fade between two cards: a fade is a dissolve, and a dissolve is the
                thing E45 refuses.
       settle - the pile is a FAN: each step behind sits STEP_PX higher (so every masthead stays readable),
                STEP_SCALE smaller and DIM dimmer, floored at BACK_SCALE and DIM_MIN - deep in the pile a card
                is still a card, never a grey rectangle.
       gone   - a card off its span is not in the stack at all; the painter passes the LIVE count as n, so a
                card that has left closes the gap instead of leaving a hole.
     Nothing is stored: every visual reads from t, the dock's enter and the live count, so a scrubbed frame is
     the played frame. The dials below are ours to tune (42 §42.5), not findings. */

  const PRESS = Object.freeze({
    LAND_S: 0.5,      /* the newest card's landing clock - the dock's own DOCK_POP_S 0.45 plus a beat, this card being pushed in rather than popped up */
    POP_FROM: 0.88,   /* the scale it springs from: nearer its size than the dock's 0.85, because the ARRIVAL here is the push, not the pop */
    DROP_PX: 22,      /* ... and how far above its place it falls from, on the same spring */
    FADE_S: 0.12,     /* the opacity ramp - the dock's DOCK_FADE_S, so a press card enters like every other card */
    PUSH_S: 0.38,     /* the older cards' slide back: shorter than LAND_S so the pile has settled while the newest is still overshooting */
    STEP_PX: 30,      /* the floor on how much higher each step behind sits (a small card still fans) */
    STEP_H: 0.22,     /* ... and the step as a share of the CARD'S OWN height, which is what actually keeps every masthead
                         strip readable: the painter passes max(STEP_PX, H * STEP_H), so the fan reads the same on a
                         headline crop of any depth instead of being a number tuned to one card */
    STEP_SCALE: 0.05, /* ... and this much smaller: a step of depth the eye reads without a perspective (it eats into the
                         reveal above - the card shrinks about its bottom edge, so its top comes DOWN as it goes back) */
    BACK_SCALE: 0.78, /* the floor on that shrink: deep in the pile a card is still legible as a card */
    DIM: 0.22,        /* what each step behind dims by - the newest is the lit one (Bravos 5-10) */
    DIM_MIN: 0.34,    /* the floor on that dim: a card the sentence may come back to never goes to nothing */
    PUSH_DX: 26,      /* §9.27's push: how far the shoved card is carried sideways at the peak of the shove */
    SQUEEZE: 0.035,   /* ... how much it compresses on x there (scaleX: the shove hits its edge) */
    SKEW_DEG: 2.4,    /* ... and how far it leans (skewX) - small: a lean, never a tumble */
    UNDERLINE_EASE: 3,/* the underline's draw curve: the hand decelerates into the end of the phrase (1 - (1 - u)^3) */
  });

  const p01 = (v) => Math.min(1, Math.max(0, v));

  /* THE RESTING POSE of the card d steps behind the newest: the fan, with its two floors. */
  const pressRest = (d, o = {}) => {
    const P = Object.assign({}, PRESS, o), k = Math.max(0, d | 0);
    return { dy: k ? -P.STEP_PX * k : 0, scale: Math.max(P.BACK_SCALE, 1 - P.STEP_SCALE * k),
             opacity: Math.max(P.DIM_MIN, 1 - P.DIM * k) };
  };

  /* THE STACK at t: the pose of the i-th card of n LIVE cards while the newest (i = n - 1) arrives with
     uNew in [0, 1] over LAND_S. The newest springs; everything behind it is pushed one step back. */
  const pressStack = (i, n, uNew, o = {}) => {
    const P = Object.assign({}, PRESS, o);
    const total = Math.max(1, n | 0), idx = Math.min(Math.max(0, i | 0), total - 1);
    const d = total - 1 - idx, u = p01(uNew);
    if (d === 0) {                                    /* the newest: the badge spring, and no push of its own */
      const s = springPop(u);
      return { depth: 0, push: 0, dx: 0, dy: (s - 1) * P.DROP_PX, scale: P.POP_FROM + (1 - P.POP_FROM) * s,
               sx: 1, skew: 0, opacity: 1, fade: p01(u * P.LAND_S / P.FADE_S) };
    }
    const p = minJerk(p01(u * P.LAND_S / P.PUSH_S));  /* the push's own, shorter clock, read off the newest's */
    const a = pressRest(d - 1, P), b = pressRest(d, P);
    const pulse = Math.sin(Math.PI * p);              /* zero at both ends: the shove leaves nothing behind */
    return { depth: d, push: p,
             dx: -P.PUSH_DX * pulse, dy: a.dy + (b.dy - a.dy) * p,
             scale: a.scale + (b.scale - a.scale) * p, sx: 1 - P.SQUEEZE * pulse,
             skew: P.SKEW_DEG * pulse, opacity: a.opacity + (b.opacity - a.opacity) * p, fade: 1 };
  };

  /* THE UNDERLINE's draw fraction at u (its elapsed clock over the stroke's window): the hand runs out fast
     and decelerates into the last letter, exactly as the squiggle's stroke does under a stressed word. */
  const underlineFrac = (u, o = {}) => {
    const P = Object.assign({}, PRESS, o);
    return 1 - Math.pow(1 - p01(u), P.UNDERLINE_EASE);
  };

  /* THE CARD'S LIVE GEOMETRY: the element box {x, y, w, h} in stage px with the pose applied, and any box
     INSIDE it (the phrase) carried through the same transform - so the underline rides the card wherever the
     stack has put it. The transform is written about the card's bottom centre, the pile's own hinge:
       x' = ox + scale * sx * ((x - ox) + tan(skew) * (y - oy)) + dx
       y' = oy + scale * (y - oy) + dy
     The CSS the painter writes must be the same composition, in the same order, about the same origin. */
  const pressXf = (box, pose) => {
    const ox = box.x + box.w / 2, oy = box.y + box.h, tan = Math.tan((pose.skew || 0) * Math.PI / 180);
    const s = pose.scale, sx = s * (pose.sx == null ? 1 : pose.sx);
    const at = (x, y) => [ox + sx * ((x - ox) + tan * (y - oy)) + (pose.dx || 0), oy + s * (y - oy) + (pose.dy || 0)];
    return (q) => {
      const pts = [at(q.x, q.y), at(q.x + q.w, q.y), at(q.x, q.y + q.h), at(q.x + q.w, q.y + q.h)];
      const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
      return { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) };
    };
  };

  /* the phrase box the compiler wrote as FRACTIONS of the card (press_card.py), in the card image's own px */
  const pressPhraseBox = (img, phrase) => {
    if (!img || !phrase) return null;
    const f = ["x0", "y0", "x1", "y1"].map((k) => +phrase[k]);
    if (f.some((v) => !Number.isFinite(v))) return null;
    return { x: img.x + f[0] * img.w, y: img.y + f[1] * img.h, w: (f[2] - f[0]) * img.w, h: (f[3] - f[1]) * img.h };
  };
  /* KINETICS:END */
  /* KINETICS:BEGIN flow */
  /* species/flow.mjs - THE FLOW DIAGRAM (P50 T4; the Bravos flow diagram, shots 82-86: a three-node diagram
     draws on a word, and on a LATER word one node swaps while the rest stands - the rhyme). SOURCE OF TRUTH,
     inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN flow and KINETICS:END,
     AFTER spring, idle, clothoid and chip - it imports all four, and the import order IS the region order.

     WHEN: the sentence EXPLAINS a mechanism - A causes B via C - as named things and the arrows between them;
     a later word SWAPS one node and the rest stands (Bravos's rhyme).

     THE LAW, all of it a pure function of t:
       box    - the dashed frame draws ON, dash by dash, by the curvature stroke (42 s42.1): the nib runs round
                the rectangle and leaves DASH-long marks with GAP between them, so the diagram arrives as a
                drawn thing and not as a rectangle that appeared. A dash already passed is simply there.
       nodes  - each node is a CHIP (species/chip.mjs): the same card, the same sourced glyph, the same badge
                spring, landing NODE_STEP after the one before, once the box is BOX_LEAD of the way round.
                The chip's own painter is not called - a chip resolves its own target and owns its own cross -
                but its dials (CHIP) and its landing law (chipLand) are, so a node and a lone chip land alike.
       arrows - between named nodes, one per EDGE_S after the last node lands, drawn BY LENGTH with the nib:
                a CLOTHOID (kinetics/clothoid.mjs, 42 s42.4), leaving one chip's edge on a tangent turned BOW
                off the chord and entering the next's turned BOW * ENTER_K back into it. The two turns are
                UNEQUAL on purpose: equal ones give a circular arc, and the point of the fitter is the RAMP -
                dk/ds constant, the pen accelerating out of one card and settling into the next.
       swap   - on swap.at the standing node UN-DRAWS - its own landing run backward, exactly as chart_to's
                recast runs a build law backward - and the new glyph and label draw on IN THE SAME SPOT. The
                arrows stand: the mechanism did not change, one of its parts did. ONE event at swap.at.
       tag    - a year stamp in the box's corner, written last (the diagram is dated, not captioned).
     Nothing is stored: every visual reads from t, sp.at and sp.swap.at, so a scrubbed frame is the played
     frame. The glyphs are SOURCED icons (assets/icons, A2a provenance) carried in the asset map as
     `icon:<name>`; this module never invents geometry. The dials below are ours to tune (42 s42.5). */

  const FLOW = Object.freeze({
    BOX_S: 0.9,        /* the dashed frame's own draw: long enough that the nib is seen going round, short enough that the first chip is not kept waiting */
    BOX_LEAD: 0.55,    /* ... and the share of it that is done when the first chip lands - the frame is still drawing under the diagram, the way a hand works */
    DASH: 26,          /* the dash's length in STAGE px ... */
    DASH_GAP: 15,      /* ... and the air between two dashes: a 2:1 rhythm reads as "a frame", never as a solid box */
    NODE_STEP: 0.2,    /* one node after the last: a beat under the eye's own saccade, so three read as a sequence and not a flash */
    EDGE_LAG: 0.1,     /* the breath between the last chip landing and the first arrow leaving it */
    EDGE_S: 0.34,      /* one arrow, drawn by length; arrows go one at a time - the mechanism is read in its order */
    BOW: 0.42,         /* the exit tangent's turn off the chord, in radians: enough curve to read as a hand's arrow, not a hoop */
    ENTER_K: 0.45,     /* ... and the entry tangent's turn as a share of it. UNEQUAL: equal angles are a circular arc and waste the fitter */
    EDGE_GAP: 16,      /* the air between a card's edge and the arrow that leaves it */
    HEAD: 28,          /* the arrowhead's stroke length in stage px ... */
    HEAD_A: 0.42,      /* ... and its half-angle in radians */
    HEAD_F: 0.72,      /* ... landing over the last of the arrow's own clock, after the shaft has arrived */
    SAMPLES: 40,       /* the clothoid's polyline per arrow: dense enough that its chords hide at our sizes */
    SWAP_OUT_S: 0.3,   /* the standing node's landing, run BACKWARD */
    SWAP_IN_S: 0.45,   /* ... and the new one's, run forward: in is slower than out, so the eye lands on what arrived */
    TAG_LAG: 0.12,     /* the breath before the year stamps ... */
    TAG_S: 0.5,        /* ... and its own write */
    TAG_PAD: 26,       /* the stamp's inset from the box's top-right corner */
    TAG_SIZE: 34,      /* ... at this size: a date, not a title */
    PITCH_K: 1.5,      /* a node's room ALONG the row as a multiple of the card: the card plus the arrow between it and the next */
    CROSS_K: 1.15,     /* ... and ACROSS it, over card + label: a breath above and below */
    MIN_K: 0.4,        /* the smallest the diagram may be scaled to before it stops being read - under it the author gave it too small a box */
    LABEL_H: 34,       /* the label's own line, for the block's height (the chip writes it at CHIP.LABEL_DY below the card) */
  });

  const flow01 = (v) => Math.min(1, Math.max(0, v));

  /* THE LAYOUT: where each node stands inside the declared box, and how big the whole diagram is drawn.
     A row inside the box; a COLUMN when the box is taller than it is wide (a portrait build's box is), which
     is the same rule read from the geometry rather than from the aspect. */
  const flowLayout = (box, n) => {
    const N = Math.max(1, n | 0), column = box.h > box.w;
    const pitch = (column ? box.h : box.w) / N, across = column ? box.w : box.h;
    const block = CHIP.SIZE + CHIP.LABEL_DY + FLOW.LABEL_H;
    const k = Math.max(FLOW.MIN_K, Math.min(1, pitch / (CHIP.SIZE * FLOW.PITCH_K), across / (block * FLOW.CROSS_K)));
    const lift = (CHIP.LABEL_DY + FLOW.LABEL_H) * k / 2;   /* the card sits above centre so card + label are centred together */
    const cells = [];
    for (let i = 0; i < N; i++) {
      cells.push(column ? { x: box.x + box.w / 2, y: box.y + pitch * (i + 0.5) - lift }
                        : { x: box.x + pitch * (i + 0.5), y: box.y + box.h / 2 - lift });
    }
    return { k, column, cells, half: CHIP.SIZE * k / 2 };
  };

  /* THE CLOCK: every instant the declaration implies, in episode seconds. One place, so the painter, the tests
     and the gate all read the same schedule. */
  const flowClock = (sp) => {
    const at = +sp.at, nodes = sp.nodes || [], edges = sp.edges || [];
    const first = at + FLOW.BOX_S * FLOW.BOX_LEAD;
    const nodeAt = nodes.map((_, i) => first + i * FLOW.NODE_STEP);
    const landed = (nodeAt.length ? nodeAt[nodeAt.length - 1] : first) + CHIP.LAND_S;
    const edgeAt = edges.map((_, j) => landed + FLOW.EDGE_LAG + j * FLOW.EDGE_S);
    const tagAt = (edgeAt.length ? edgeAt[edgeAt.length - 1] + FLOW.EDGE_S : landed) + FLOW.TAG_LAG;
    return { box: [at, at + FLOW.BOX_S], nodeAt, landed, edgeAt, tagAt, tagEnd: tagAt + FLOW.TAG_S };
  };

  /* the box's draw at t, 0..1 - and, from it, the dash that is under the nib */
  const flowBoxF = (sp, t) => flow01((t - +sp.at) / FLOW.BOX_S);

  /* the rectangle's perimeter cut into dashes, each with the fraction of the whole draw it owns. The nib starts
     at the top-left and runs clockwise - the way the box would be drawn by a hand. */
  const flowDashes = (box) => {
    const per = 2 * (box.w + box.h), n = Math.max(4, Math.round(per / (FLOW.DASH + FLOW.DASH_GAP)));
    const step = per / n, out = [];
    const at = (d) => {   /* a distance round the perimeter -> a point on it, clockwise from the top-left */
      let s = ((d % per) + per) % per;
      if (s < box.w) return { x: box.x + s, y: box.y };
      s -= box.w;
      if (s < box.h) return { x: box.x + box.w, y: box.y + s };
      s -= box.h;
      if (s < box.w) return { x: box.x + box.w - s, y: box.y + box.h };
      return { x: box.x, y: box.y + box.h - (s - box.w) };
    };
    const corners = [box.w, box.w + box.h, 2 * box.w + box.h, per];
    for (let i = 0; i < n; i++) {
      const d0 = i * step;
      let len = Math.min(FLOW.DASH, step * 0.72);
      /* a dash that ran past a CORNER used to be drawn as its chord, which cut the corner off the box (read in
         the frame, 2026-09-11). A dash stops at the corner it reaches; the next one starts the new side. */
      for (const c of corners) if (c > d0 && c < d0 + len) len = c - d0;
      out.push({ a: at(d0), b: at(d0 + len), t0: i / n, t1: (i + 1) / n });
    }
    return out;
  };

  /* THE SWAP at t: which node is changing, and how far through which half of its change. `phase` is "none"
     before the word, "out" while the standing node un-draws, "in" while the new one draws, "done" after. */
  const flowSwapPhase = (sp, t) => {
    const sw = sp.swap;
    if (!sw || !Number.isFinite(+sw.at)) return { phase: "none", u: 1 };
    const d = t - +sw.at;
    if (d < 0) return { phase: "none", u: 1 };
    if (d < FLOW.SWAP_OUT_S) return { phase: "out", u: 1 - d / FLOW.SWAP_OUT_S };   /* the landing, run backward */
    const uIn = flow01((d - FLOW.SWAP_OUT_S) / FLOW.SWAP_IN_S);
    return { phase: uIn >= 1 ? "done" : "in", u: uIn };
  };

  /* ONE NODE at t: what it shows (a swap changes the glyph and the label, never the place) and how far its
     landing has run. u is the landing's normalised clock, which is all chipLand needs. */
  const flowNodeAt = (sp, i, t) => {
    const node = (sp.nodes || [])[i] || {}, sw = sp.swap;
    const C = flowClock(sp), u0 = flow01((t - C.nodeAt[i]) / CHIP.LAND_S);
    if (!sw || sw.node !== node.id) return { icon: node.icon, label: node.label, u: u0, alpha: 1, swapping: false };
    const ph = flowSwapPhase(sp, t);
    if (ph.phase === "none") return { icon: node.icon, label: node.label, u: u0, alpha: 1, swapping: false };
    /* OUT: the landing run backward - and the card's own opacity on the OUT clock. The chip's fade is 0.14 s
       of a 0.55 s landing; reversed into SWAP_OUT_S it would be a blink at the very end rather than an
       un-draw (read in the frame, 2026-09-11), so the ink leaves on the clock the un-draw was given, the way
       an `undraw` retracts a stroke on its own clock and not on the build's. */
    if (ph.phase === "out") return { icon: node.icon, label: node.label, u: Math.min(u0, ph.u), alpha: ph.u, swapping: true };
    return { icon: sw.icon, label: sw.label, u: ph.u, alpha: 1, swapping: ph.phase === "in" };
  };

  /* the pose of a node at a landing clock u: the chip's own law, on the flow's clock */
  const flowPose = (u) => chipLand(flow01(u) * CHIP.LAND_S, 0);

  /* ONE ARROW's draw at t, 0..1 */
  const flowEdgeF = (sp, j, t) => {
    const C = flowClock(sp);
    return C.edgeAt[j] === undefined ? 0 : flow01((t - C.edgeAt[j]) / FLOW.EDGE_S);
  };

  /* THE ANCHORS of one arrow: the point on each card's square edge that faces the other, pushed out by
     EDGE_GAP, and the two tangents the clothoid is fitted to. */
  const flowAnchors = (a, b, half) => {
    const dx = b.x - a.x, dy = b.y - a.y, chord = Math.atan2(dy, dx);
    const edge = (c, th) => {   /* the square's boundary in direction th, plus the air */
      const cs = Math.cos(th), sn = Math.sin(th), m = Math.max(Math.abs(cs), Math.abs(sn)) || 1;
      const r = half / m + FLOW.EDGE_GAP;
      return { x: c.x + r * cs, y: c.y + r * sn };
    };
    const t0 = chord - FLOW.BOW, t1 = chord + FLOW.BOW * FLOW.ENTER_K;
    return { p0: edge(a, t0), t0, p1: edge(b, t1 + Math.PI), t1, chord };
  };

  /* the arrowhead's two strokes at the polyline's far end, along the tangent it arrives on */
  const flowHead = (pts) => {
    const n = pts.length;
    if (n < 2) return "";
    const tip = pts[n - 1], prev = pts[n - 2], th = Math.atan2(tip.y - prev.y, tip.x - prev.x);
    const arm = (s) => ({ x: tip.x - FLOW.HEAD * Math.cos(th + s * FLOW.HEAD_A), y: tip.y - FLOW.HEAD * Math.sin(th + s * FLOW.HEAD_A) });
    const l = arm(1), r = arm(-1);
    return "M" + l.x.toFixed(2) + " " + l.y.toFixed(2) + " L" + tip.x.toFixed(2) + " " + tip.y.toFixed(2)
         + " L" + r.x.toFixed(2) + " " + r.y.toFixed(2);
  };

  /* the edges as index pairs into the node list (a name that is not a node is dropped, not drawn wrong) */
  const flowEdgeIndex = (sp) => {
    const ids = (sp.nodes || []).map((n) => n && n.id);
    return (sp.edges || []).map((e) => [ids.indexOf(e && e[0]), ids.indexOf(e && e[1])]);
  };

  /* THE PAINTER. ctx is the template's species context (see SPECIES_PAINTERS in the player). Everything is
     drawn in STAGE px into one group, in reading order: the frame, the arrows (under the cards, so their ends
     tuck beneath), the cards, the stamp. */
  function paintFlow(ctx) {
    const { sp, t, svg, el, A, resolveTarget, drawOn, hash, idle, seed, si } = ctx;
    const box = resolveTarget(sp.target);
    if (!box || !(box.w > 0 && box.h > 0)) return;   /* the targeting law: a flow needs its room declared */
    const nodes = sp.nodes || [], lay = flowLayout(box, nodes.length), C = flowClock(sp);
    const g = el("g", "flow", svg, {});
    /* the frame, dash by dash, under the nib */
    const bf = flowBoxF(sp, t);
    if (bf > 0) {
      for (const d of flowDashes(box)) {
        const f = flow01((bf - d.t0) / Math.max(1e-6, d.t1 - d.t0));
        if (f <= 0) continue;
        const p = el("path", "flowbox", g, { d: "M" + d.a.x.toFixed(1) + " " + d.a.y.toFixed(1) + " L" + d.b.x.toFixed(1) + " " + d.b.y.toFixed(1) });
        if (f < 1) drawOn(p, f);
      }
    }
    /* the arrows, drawn by length with the nib */
    flowEdgeIndex(sp).forEach(([ia, ib], j) => {
      if (ia < 0 || ib < 0 || ia === ib) return;
      const f = flowEdgeF(sp, j, t);
      if (f <= 0) return;
      const an = flowAnchors(lay.cells[ia], lay.cells[ib], lay.half);
      const pts = clothoid(an.p0, an.t0, an.p1, an.t1, FLOW.SAMPLES);
      drawOn(el("path", "flowarrow", g, { d: clothoidPath(pts) }), Math.min(1, f / FLOW.HEAD_F));
      if (f > FLOW.HEAD_F) drawOn(el("path", "flowarrow", g, { d: flowHead(pts) }), (f - FLOW.HEAD_F) / (1 - FLOW.HEAD_F));
    });
    /* the cards */
    nodes.forEach((node, i) => {
      const st = flowNodeAt(sp, i, t);
      if (st.u <= 0 || st.alpha <= 0) return;
      const pose = flowPose(st.u), c = lay.cells[i];
      const ix = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 907 + i)) : { scale: 1, dx: 0, dy: 0 };
      const s = pose.scale * ix.scale * lay.k;
      const ng = el("g", "", g, { opacity: (pose.fade * st.alpha).toFixed(3),
                                  transform: "translate(" + (c.x + ix.dx).toFixed(1) + " " + (c.y + (pose.dy + ix.dy) * lay.k).toFixed(1) + ") scale(" + s.toFixed(4) + ")" });
      const h = CHIP.SIZE / 2;
      el("rect", "chipcard", ng, { x: (-h).toFixed(1), y: (-h).toFixed(1), width: CHIP.SIZE, height: CHIP.SIZE, rx: CHIP.RX });
      const geo = chipGeometry(A ? A["icon:" + st.icon] : null);
      if (geo) {
        const vb = geo.vb || [0, 0, 24, 24], gk = CHIP.GLYPH / Math.max(vb[2] || 1, vb[3] || 1);
        const gg = el("g", "chipglyph", ng, { transform: "translate(" + (-CHIP.GLYPH / 2).toFixed(1) + " " + (-CHIP.GLYPH / 2).toFixed(1) + ") scale(" + gk.toFixed(4) + ") translate(" + (-vb[0]) + " " + (-vb[1]) + ")" });
        geo.el.forEach((q) => el(q.t, "", gg, q.a));   /* the sourced geometry verbatim */
      }
      if (st.label) { const lab = el("text", "chiplab", ng, { x: 0, y: (h + CHIP.LABEL_DY).toFixed(1) }); lab.textContent = st.label; }
    });
    /* the year stamp in the box's corner */
    if (sp.tag && t >= C.tagAt) {
      const u = flow01((t - C.tagAt) / FLOW.TAG_S), e = springPop(u);
      const tx = el("text", "flowtag", g, { x: (box.x + box.w - FLOW.TAG_PAD).toFixed(1),
                                            y: (box.y + FLOW.TAG_PAD + FLOW.TAG_SIZE * (1.4 - 0.4 * e)).toFixed(1),
                                            opacity: flow01(u / 0.4).toFixed(3), style: "font-size:" + FLOW.TAG_SIZE + "px" });
      tx.textContent = sp.tag;
    }
  }

  /* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
     import this file for the math above without the template's registry */
  if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.flow = paintFlow;
  /* KINETICS:END */
  /* KINETICS:BEGIN vecmap */
  /* species/vecmap.mjs - THE VECTOR MAP (P50 T5; the Bravos world map, shots 57-80: Iran lights, an arc leaves
     the Gulf and crosses to the US, "1996" stamps, China lights and takes "1.4 Billion Barrels"). SOURCE OF
     TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN vecmap and
     KINETICS:END, AFTER spring, idle, clothoid and chip - it imports all four, and the import order IS the
     region order.

     TWO THINGS LIVE HERE, and the template's world branch is three lines because of it:
       THE WORLD - `world.kind === "vecmap"`: 177 country outlines (assets/maps/world-110m.paths.json, Natural
                   Earth 110m, public domain) drawn in the MUTED INK on the stage's own dark ground, the focus
                   set's outlines a shade stronger. The register is the CHARCOAL one (doc 29 s9.28: a world is
                   the stage's ground, species over it) - the cream is the ledger PAGE's register, and a page is
                   a document, not a stage. The projection is the map's own: the file is already equirectangular
                   on a 1000 x 500 box, so the player's whole job is ONE SIMILARITY per composition (mapFit) -
                   never a stretch, which would lie about distances.
       THE SPECIES - `light` (a country's fill rises to the accent and holds, breathing on its idle: the
                   spotlight's cousin, a FILL, never a ring - E56), `arc` (a clothoid from one centroid to
                   another, drawn by length with the nib, an X at its midpoint when the flow is CUT) and
                   `stamp` (a figure, or a year at the smaller size, written at a centroid or a declared point).

     THE FRAME. Every one of them paints in the SAME coordinates - the map box through `fit` - and then rides
     the SAME two transforms as the world beneath it: the scene's CAMERA (screen = at + s (p - look), exactly
     camCssFor's mapping, because the world is a div carrying that CSS and a species is an svg group that is
     not) and the world's IDLE (E49: the map holds at its breath, never dead still). vmGroupXf builds both from
     one place, so a light cannot drift off its country while the camera moves between focal points (E59 reason
     2: one move per composition, then still).
     Nothing is stored: every visual reads from t and the declaration, so a scrubbed frame is the played frame.
     The outlines are SOURCED data, never invented geometry. The dials below are ours to tune (42 s42.5). */

  const VECMAP = Object.freeze({
    MARGIN: 0.055,     /* the air around the framed box, as a share of the stage's SHORT side - the map never touches the frame */
    PAD: 18,           /* ... plus this much air in MAP units around the focus set's own box, so a lit country is never cut by the margin */
    ZOOM_MAX: 4.2,     /* the most the fit may magnify the 1000 x 500 box: past it one country is a blob and the rest of the world is off screen */
    IDLE: "breath",    /* the world's idle when the row names none (the template's IDLE_CLASS.plate, named here so the species agree with it) */
  });

  const LIGHT = Object.freeze({
    IN_S: 0.3,         /* the plan's number: the country's fill rises to the accent over this and HOLDS (dur 'hold' resolves in the compiler, as the spotlight's does) */
    OUT_S: 0.35,       /* ... and leaves a touch slower than it arrived, so the last frame of a sentence is not a blink */
    MAX: 0.78,         /* the lit fill's opacity: the accent reads as a light ON the land, never as a solid shape replacing it */
    BREATH_K: 7,       /* the idle's scale deviation (1.2 % at the breath's peak) mapped onto the FILL - a country cannot scale without leaving its outline, so its light breathes instead */
  });

  const ARC = Object.freeze({
    DRAW_S: 0.9,       /* the flow crosses in this long, drawn BY LENGTH with the nib (42 s42.1) */
    BOW: 0.5,          /* the exit tangent's turn off the chord, radians: a flight path lifts, it does not hoop */
    ENTER_K: 0.45,     /* ... and the entry tangent's as a share of it. UNEQUAL, like the flow diagram's arrows: equal turns give a circular arc and waste the fitter's ramp */
    SAMPLES: 48,       /* the clothoid's polyline: dense enough that its chords hide at our sizes */
    HEAD: 26,          /* the arrowhead's stroke length in stage px ... */
    HEAD_A: 0.42,      /* ... and its half-angle in radians (the flow's arrow, so two arrows in one episode are one hand) */
    HEAD_F: 0.74,      /* ... landing over the last of the arc's own clock, after the shaft has arrived */
    CROSS_S: 0.45,     /* the X at the midpoint: two strokes, the chip's cross (chipStrokes) on a shorter clock */
    CROSS_ARM: 26,     /* ... each arm this long in stage px */
    DIM: 0.42,         /* what a CUT arc dims to: the flow was real, and then it was cut - it does not vanish */
  });

  const STAMP = Object.freeze({
    IN_S: 0.45,        /* the figure lands on the badge spring (springPop), the same landing a chip and the flow's year stamp take */
    FADE_S: 0.16,      /* ... never a pop out of nothing */
    RISE: 0.5,         /* the share of its own size it falls from, so it arrives ON the place rather than beside it */
    POP_FROM: 0.72,    /* ... and the size it springs UP from (the callout label's 0.7, the chip's POP_FROM): never a pop out of nothing */
    FIGURE_PX: 46,     /* a FIGURE's type: the sentence's number, read at phone size */
    EDGE: 28,          /* ... and the stage inset it is kept inside: a figure that runs off the frame is not evidence (doc 49 s49.1) */
    CHAR_W: 0.56,      /* the estimated width of one character as a share of the size, Inter 700 - an ESTIMATE, not a measurement: the player measures nothing at paint time (a scrubbed frame is the played frame), and the only thing it buys is the clamp below */
    YEAR_PX: 32,       /* ... and a YEAR's, which is furniture: a date, not a title (the flow's TAG_SIZE, one notch down) */
    DY: -18,           /* the baseline's lift off the centroid: the figure sits ON the place, not under it */
  });

  const STAMP_SIZES = Object.freeze({ figure: STAMP.FIGURE_PX, year: STAMP.YEAR_PX });

  const vm01 = (v) => Math.min(1, Math.max(0, v));

  /* ---------------------------------------------------------------- THE MAP

     The asset map carries the whole file under one key (`map:<name>`, 187 KB, put there once by the compiler
     however many scenes use it). Parsing 177 countries every frame would be the one expensive thing in this
     module, so the parse is memoised by the STRING ITSELF: the same asset parses once for the whole render. */
  const VM_CACHE = new Map();
  const mapData = (raw) => {
    if (typeof raw !== "string" || !raw) return null;
    let d = VM_CACHE.get(raw);
    if (d === undefined) {
      try { d = JSON.parse(raw); } catch (e) { d = null; }
      if (!d || !d.countries || !Array.isArray(d.box)) d = null;
      if (VM_CACHE.size > 4) VM_CACHE.clear();
      VM_CACHE.set(raw, d);
    }
    return d;
  };

  /* the framed box in MAP units: the focus set's bboxes unioned and padded, or the whole map when none is named */
  const focusBox = (box, bboxes, pad = VECMAP.PAD) => {
    const bs = (bboxes || []).filter((b) => Array.isArray(b) && b.length === 4);
    if (!bs.length) return { x: 0, y: 0, w: box[0], h: box[1] };
    const x0 = Math.min(...bs.map((b) => b[0])), y0 = Math.min(...bs.map((b) => b[1]));
    const x1 = Math.max(...bs.map((b) => b[2])), y1 = Math.max(...bs.map((b) => b[3]));
    return { x: x0 - pad, y: y0 - pad, w: (x1 - x0) + 2 * pad, h: (y1 - y0) + 2 * pad };
  };

  /* THE FIT: ONE SIMILARITY from map units to stage px, stage = (sx * x + tx, sy * y + ty) with sx === sy.
     The framed box is CONTAINED in the stage less its margin - on 16:9 that is the whole world (or the focus
     set's box) letterboxed; on 9:16, where a focus set is always wider than it is tall, it is that box fit to
     the WIDTH. One rule, read off the geometry rather than off the aspect, exactly as the flow diagram picks
     its row or its column. ZOOM_MAX caps a focus set of one small country, which would otherwise magnify the
     world past reading. */
  const mapFit = (box, bboxes, stageW, stageH, margin = VECMAP.MARGIN) => {
    const m = margin * Math.min(stageW, stageH), f = focusBox(box, bboxes);
    const k = Math.min(VECMAP.ZOOM_MAX, (stageW - 2 * m) / Math.max(1e-6, f.w), (stageH - 2 * m) / Math.max(1e-6, f.h));
    return { sx: k, sy: k,
             tx: stageW / 2 - k * (f.x + f.w / 2),
             ty: stageH / 2 - k * (f.y + f.h / 2), box: f };
  };

  /* a point in MAP units -> stage px, and back: the two are each other's inverse to the bit (the fit is one
     similarity, not a projection - the projection was done once, on disk, by build_world_map.py) */
  const mapPoint = (fit, p) => ({ x: fit.sx * p[0] + fit.tx, y: fit.sy * p[1] + fit.ty });
  const mapInvert = (fit, q) => [(q.x - fit.tx) / fit.sx, (q.y - fit.ty) / fit.sy];
  /* the SVG transform that puts a raw map path (its own units, untouched) on the stage */
  const fitXf = (fit) => "translate(" + fit.tx.toFixed(2) + " " + fit.ty.toFixed(2) + ") scale(" + fit.sx.toFixed(5) + ")";

  /* the TARGET of a light, an arc's end or a stamp, in MAP units: a country resolves to its centroid, a
     declared map point to itself. A name that is not in the data resolves to nothing and nothing is painted -
     the compiler refuses it by name long before here (the targeting law, s9.27). */
  const vmTarget = (data, tg) => {
    if (!tg || !data) return null;
    if (tg.kind === "country") { const c = data.countries[tg.id]; return c && c.centroid ? c.centroid : null; }
    if (tg.kind === "mappoint") return [+tg.x, +tg.y];
    return null;
  };

  /* ---------------------------------------------------------------- THE FRAME EVERY PAINTER RIDES */

  /* the world's idle transform, about the STAGE's centre - the same pose the world's own group takes, so a
     species over it never slides against the land beneath it. `kindOf` is the player's idleOf (which carries
     the kinetics flag and the class default); node passes its own. */
  const vmIdle = (scene, world, t, idle, hash, kindOf) => {
    const kind = kindOf ? kindOf("plate", (world || {}).idle) : ((world || {}).idle || VECMAP.IDLE);
    if (!kind || kind === "none") return { scale: 1, dx: 0, dy: 0 };
    const span = (scene && scene.span) ? scene.span[0] : 0;
    return (idle || idleXf)(kind, t, (hash || (() => 0))(Math.round(span * 100), 0, 977));
  };

  /* the two transforms as ONE string, in the order the world applies them: the camera's
     screen = at + s (p - look) (camCssFor's mapping, so the species and the div agree to the pixel), then the
     idle about the stage's centre. Either one absent is the identity and writes nothing. */
  const vmGroupXf = (cam, ix, stageW, stageH) => {
    let out = "";
    if (cam && (cam.s !== 1 || cam.ax !== cam.ox || cam.ay !== cam.oy)) {
      const s = cam.s, ax = cam.ax == null ? cam.ox : cam.ax, ay = cam.ay == null ? cam.oy : cam.ay;
      out += "translate(" + (ax - s * cam.ox).toFixed(2) + " " + (ay - s * cam.oy).toFixed(2) + ") scale(" + s.toFixed(5) + ") ";
    }
    if (ix && (ix.scale !== 1 || ix.dx !== 0 || ix.dy !== 0)) {
      const cx = stageW / 2, cy = stageH / 2;
      out += "translate(" + (cx + ix.dx).toFixed(2) + " " + (cy + ix.dy).toFixed(2) + ") scale(" + ix.scale.toFixed(5)
           + ") translate(" + (-cx).toFixed(2) + " " + (-cy).toFixed(2) + ") ";
    }
    return out.trim();
  };

  /* ---------------------------------------------------------------- THE LAWS, each a pure function of t */

  /* THE LIGHT at t: 0 before its word, up to MAX over IN_S, held for its window, out over OUT_S. The idle
     breathes the FILL, not the shape - a country that scaled would leave its own outline behind. */
  const lightAlpha = (t, at, dur, ixScale = 1) => {
    const d = t - at;
    if (d < 0 || d > dur) return 0;
    const up = vm01(d / LIGHT.IN_S), down = vm01((at + dur - t) / LIGHT.OUT_S);
    return LIGHT.MAX * Math.min(up, down) * (1 + (ixScale - 1) * LIGHT.BREATH_K);
  };

  /* THE ARC at t: how much of it is drawn (0..1), how far its X has been struck, and what it has dimmed to. */
  const arcFrac = (sp, t) => vm01((t - +sp.at) / ARC.DRAW_S);
  const arcCrossF = (sp, t) => (Number.isFinite(+sp.crossed) ? vm01((t - +sp.crossed) / ARC.CROSS_S) : 0);
  const arcDim = (f) => 1 - (1 - ARC.DIM) * f;

  /* THE ARC's geometry in STAGE px: a clothoid (kinetics/clothoid.mjs, 42 s42.4) from one centroid to the
     other, its two tangents turned UNEQUALLY off the chord so the pen ramps out of one place and settles into
     the next. The bow lifts toward the POLE the two places share - a Gulf -> US arc rises over the Atlantic
     rather than sagging into it.
     WHICH WAY THAT IS depends on where the arc is GOING, not only on which hemisphere it is in (read in the
     frame, 2026-09-11: a westward flow bowed with a fixed sign sagged into the Atlantic). Leaving at the
     heading th + s * BOW veers to the side whose y-component is s * cos(th), so for a lift of sign w (-1 in
     the north, +1 in the south) the turn is s = w * sign(dx): eastward and westward arcs take opposite signs
     and both rise. A chord with no x-run has no lift to give and keeps w. */
  const arcBowSign = (box, a, b) => {
    const w = ((a[1] + b[1]) / 2) < box[1] / 2 ? -1 : 1;
    return b[0] - a[0] >= 0 ? w : -w;
  };

  const arcPath = (fit, from, to, bow = ARC.BOW, sign = -1) => {
    const p0 = mapPoint(fit, from), p1 = mapPoint(fit, to);
    const chord = Math.atan2(p1.y - p0.y, p1.x - p0.x);
    const t0 = chord + sign * bow, t1 = chord - sign * bow * ARC.ENTER_K;
    const pts = clothoid(p0, t0, p1, t1, ARC.SAMPLES);
    return { pts, d: clothoidPath(pts), p0, p1, mid: pts[pts.length >> 1] };
  };

  /* the arrowhead's two strokes at the far end, along the tangent it arrives on (the flow diagram's head) */
  const arcHead = (pts) => {
    const n = pts.length;
    if (n < 2) return "";
    const tip = pts[n - 1], prev = pts[n - 2], th = Math.atan2(tip.y - prev.y, tip.x - prev.x);
    const arm = (s) => ({ x: tip.x - ARC.HEAD * Math.cos(th + s * ARC.HEAD_A), y: tip.y - ARC.HEAD * Math.sin(th + s * ARC.HEAD_A) });
    const l = arm(1), r = arm(-1);
    return "M" + l.x.toFixed(2) + " " + l.y.toFixed(2) + " L" + tip.x.toFixed(2) + " " + tip.y.toFixed(2)
         + " L" + r.x.toFixed(2) + " " + r.y.toFixed(2);
  };

  /* the X at a cut arc's midpoint: the chip's two-stroke cross, on the arc's own clock */
  const arcCrossPaths = (mid, arm = ARC.CROSS_ARM) =>
    ["M" + (mid.x - arm).toFixed(1) + " " + (mid.y - arm).toFixed(1) + " L" + (mid.x + arm).toFixed(1) + " " + (mid.y + arm).toFixed(1),
     "M" + (mid.x + arm).toFixed(1) + " " + (mid.y - arm).toFixed(1) + " L" + (mid.x - arm).toFixed(1) + " " + (mid.y + arm).toFixed(1)];

  /* THE STAMP at t: the badge spring's landing, its fade and the size its `size` field names. The page's own
     figure law (the hand writing at a datum) is NOT reachable from here - it is a mask wipe over .lp-ink spans
     inside the ledger page's DOM, and this overlay is an svg on the stage - so a stamp lands the way the flow
     diagram's year stamp and the callout's label land: the type popping on springPop. Said plainly because the
     two are different hands, and a cut that wants the written figure wants a ledger page under it. */
  const stampPose = (sp, t) => {
    const u = vm01((t - +sp.at) / STAMP.IN_S), e = springPop(u), px = STAMP_SIZES[sp.size] || STAMP.FIGURE_PX;
    return { u, px, fade: vm01((t - +sp.at) / STAMP.FADE_S), dy: STAMP.DY + px * STAMP.RISE * (1 - e),
             scale: STAMP.POP_FROM + (1 - STAMP.POP_FROM) * e };
  };

  /* the stamp's place in STAGE px: the centroid (or the declared point), lifted off it by the pose */
  const stampAt = (fit, p) => mapPoint(fit, p);

  /* a point through the SAME two transforms vmGroupXf writes, as numbers: the idle about the stage's centre,
     then the camera (screen = at + s (p - look)). The string is for geometry that rides the map; this is for
     the one thing that must NOT - the type. */
  const vmScreen = (cam, ix, p, stageW, stageH) => {
    let x = p.x, y = p.y;
    if (ix) { const cx = stageW / 2, cy = stageH / 2; x = cx + ix.dx + (x - cx) * ix.scale; y = cy + ix.dy + (y - cy) * ix.scale; }
    if (cam) { const ax = cam.ax == null ? cam.ox : cam.ax, ay = cam.ay == null ? cam.oy : cam.ay;
               x = ax + cam.s * (x - cam.ox); y = ay + cam.s * (y - cam.oy); }
    return { x, y };
  };

  /* ... and the type kept ON the stage. A centroid near the frame's edge (China's, on a 9:16 stage framing
     three continents - read in the frame, 2026-09-11) put half the figure outside it. The anchor is pushed in
     by the text's estimated half width; a figure wider than the stage stays centred and the author is the one
     who wrote too long a number. */
  const stampClamp = (q, text, px, stageW, stageH) => {
    const half = String(text || "").length * px * STAMP.CHAR_W / 2, m = STAMP.EDGE;
    const lo = m + half, hi = stageW - m - half;
    return { x: lo > hi ? stageW / 2 : Math.min(Math.max(q.x, lo), hi),
             y: Math.min(Math.max(q.y, m + px), stageH - m) };
  };

  /* ---------------------------------------------------------------- THE PAINTERS */

  /* the fit this composition uses, from the world's own declaration - the one place the world branch and the
     three species agree, so they cannot disagree about where a country is */
  const worldFit = (data, world, stageW, stageH) => {
    if (!data) return null;
    const ids = (world && world.focus) || [];
    return mapFit(data.box, ids.map((id) => (data.countries[id] || {}).bbox).filter(Boolean), stageW, stageH);
  };

  /* THE WORLD (the template's branch is: mount an svg, call this). Every country's paths drawn once in the
     muted ink, the focus set's a shade stronger (the classes carry the register; this file carries no colour),
     the whole thing riding the world's idle so the map is never a still image. */
  function paintVecmapWorld(ctx) {
    const { el, scene, world, t, A, root, idle, hash, idleOf, STAGE_W, STAGE_H } = ctx;
    const data = mapData(A ? A["map:" + (world.map || "world-110m")] : null);
    root.replaceChildren();
    if (!data) return null;
    const fit = worldFit(data, world, STAGE_W, STAGE_H);
    const ix = vmIdle(scene, world, t, idle, hash, idleOf);
    const g = el("g", "", root, { transform: vmGroupXf(null, ix, STAGE_W, STAGE_H) });
    const inner = el("g", "vmland", g, { transform: fitXf(fit) });
    const focus = new Set(world.focus || []);
    for (const id of Object.keys(data.countries)) {
      const c = data.countries[id];
      for (const d of c.paths || []) el("path", focus.has(id) ? "vmc vmfocus" : "vmc", inner, { d });
    }
    return fit;
  }

  /* the frame a species paints in: the camera, the world's idle, and the fit the world used */
  const vmFrame = (ctx) => {
    const { sc, t, A, camNow, idle, hash, idleOf, STAGE_W, STAGE_H } = ctx;
    const world = (sc && sc.world) || {};
    const data = mapData(A ? A["map:" + (world.map || "world-110m")] : null);
    if (!data) return null;
    const fit = worldFit(data, world, STAGE_W, STAGE_H);
    const ix = vmIdle(sc, world, t, idle, hash, idleOf);
    const cam = camNow ? camNow(sc, t) : null;
    return { data, fit, ix, cam, xf: vmGroupXf(cam, ix, STAGE_W, STAGE_H) };
  };

  /* THE LIGHT: the country's own outline filled to the accent (E56 - a picture's focus is a LIGHT; the
     spotlight's cousin, never a ring), rising over IN_S and holding, its fill breathing on the idle. */
  function paintLight(ctx) {
    const { sp, t, svg, el, idle, hash, seed, si } = ctx;
    const F = vmFrame(ctx); if (!F) return;
    const c = F.data.countries[(sp.target || {}).id]; if (!c) return;
    /* the light's own breath, declared on the species exactly as the spotlight and the chip declare theirs
       (E49; the same seeded phase, salt 991) - the WORLD's idle above moves the map, this one moves the
       light, and a lit country is alive even where the map itself is declared still. */
    const lx = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 991)) : { scale: 1, dx: 0, dy: 0 };
    const a = lightAlpha(t, +sp.at, +sp.dur, lx.scale);
    if (a <= 0) return;
    const g = el("g", "", svg, { transform: F.xf });
    const inner = el("g", "", g, { transform: fitXf(F.fit), "fill-opacity": a.toFixed(3) });
    for (const d of c.paths || []) el("path", "vmlit", inner, { d });
  }

  /* THE ARC: the clothoid drawn by length with the nib from one centroid to the other, the head landing last,
     an X struck at its midpoint on `crossed` and the whole flow dimming under it. */
  function paintArc(ctx) {
    const { sp, t, svg, el, drawOn } = ctx;
    const F = vmFrame(ctx); if (!F) return;
    const from = vmTarget(F.data, sp.from), to = vmTarget(F.data, sp.to);
    if (!from || !to) return;
    const f = arcFrac(sp, t); if (f <= 0) return;
    const arc = arcPath(F.fit, from, to, ARC.BOW, arcBowSign(F.data.box, from, to));
    const cross = arcCrossF(sp, t);
    const g = el("g", "", svg, { transform: F.xf, opacity: arcDim(cross).toFixed(3) });
    drawOn(el("path", "vmarc", g, { d: arc.d }), Math.min(1, f / ARC.HEAD_F));
    if (f > ARC.HEAD_F) drawOn(el("path", "vmarc", g, { d: arcHead(arc.pts) }), (f - ARC.HEAD_F) / (1 - ARC.HEAD_F));
    if (cross > 0) {
      const strokes = chipStrokes(cross), paths = arcCrossPaths(arc.mid);
      const x = el("g", "", svg, { transform: F.xf });   /* the X is struck ON the arc and does not dim with it */
      paths.forEach((d, i) => { if (strokes[i] > 0) drawOn(el("path", "vmx", x, { d }), strokes[i]); });
    }
  }

  /* THE STAMP: the figure (or the year, at the smaller size) landing on the badge spring at the place it
     belongs to - a country's centroid, or a declared point on the map. */
  function paintStamp(ctx) {
    const { sp, t, svg, el, STAGE_W, STAGE_H } = ctx;
    const F = vmFrame(ctx); if (!F) return;
    const p = vmTarget(F.data, sp.target); if (!p) return;
    const pose = stampPose(sp, t); if (pose.fade <= 0) return;
    /* the place goes through the map's frame; the TYPE does not - it is drawn in plain stage px at its own
       size, so a camera zoom moves the figure with its place and never magnifies the number (doc 50's type
       floors are stage px), and the clamp above keeps it on the frame. */
    const q = stampClamp(vmScreen(F.cam, F.ix, stampAt(F.fit, p), STAGE_W, STAGE_H), sp.text, pose.px, STAGE_W, STAGE_H);
    const y = q.y + pose.dy;
    const tx = el("text", "vmstamp", svg, { x: q.x.toFixed(1), y: y.toFixed(1), opacity: pose.fade.toFixed(3),
                                            style: "font-size:" + pose.px + "px",
                                            transform: "translate(" + q.x.toFixed(1) + " " + y.toFixed(1) + ") scale(" + pose.scale.toFixed(4)
                                                     + ") translate(" + (-q.x).toFixed(1) + " " + (-y).toFixed(1) + ")" });
    tx.textContent = sp.text || "";
  }

  /* the module rule's registration: plain assignments (inline_text keeps them), guarded so `node --test` can
     import this file for the math above without the template's registry */
  if (typeof SPECIES_PAINTERS !== "undefined") {
    SPECIES_PAINTERS.light = paintLight;
    SPECIES_PAINTERS.arc = paintArc;
    SPECIES_PAINTERS.stamp = paintStamp;
  }
  /* KINETICS:END */
  /* KINETICS:BEGIN tippill */
  /* species/tippill.mjs - THE TIP-RIDING PILL (P50 T11; R26-34; E53 s8). SOURCE OF TRUTH, inlined into the scene-evidence
     player by sync_kinetics.py between KINETICS:BEGIN tippill and KINETICS:END, AFTER spring (it uses springPop).
     A dense line that is drawing has a tip and nothing else; the pill is the tip's LIFE - the thing that says which line
     this is while it is still being drawn, instead of a label that appears once it stops.
       X_pill(u) = P_tip(u) + D_offset, a LEADER from the tip to the pill, the pill popping in on springPop(Mp = 0.05) at
       a declared milestone (the datum the sentence turns on), and at the end of the draw the pill settles onto the
       terminal tag's place and the TAG takes over - E53 s8 is unchanged, the pill is what happens before it.
     It carries no painter: it is not a species kind (nothing targets it), it is a line page's option (`;pill=` on the
     plate id -> `page.tip_pill`), so the module is the math and the page's builder is the only caller.
     Every value here is a pure function of the line's points and the fraction of it that is drawn: the pop runs in the
     LINE's own progress rather than in seconds, so a seek to any t paints exactly what playing to it would. */

  const TIPPILL = Object.freeze({
    DX: 30,          /* D_offset, x: the pill rides AHEAD of the tip by half a pill's height, so the nib is never covered and the eye reads pill-then-tip [DERIVED: the 6 px tip circle plus the 24 px the leader needs to be seen as a leader] */
    DY: -40,         /* D_offset, y: above the tip - a line that falls has its own space below it, and a pill under the tip would sit on the axis labels */
    POP_MP: 0.05,    /* R26-34's named overshoot: springPop(Mp = 0.05) - one notch past the standing pop (SPRING.MP 0.04) because the pill arrives on a WORD */
    POP_F: 0.06,     /* the pop's span as a share of the line's length: at the pen's speed (E50's two-thirds law) that is ~0.3 s on our pages, and it must end while the tip is still at the milestone */
    SETTLE: 0.10,    /* the last share of the draw: the pill leaves the tip and lands on the tag's place. It is 0.10 because the terminal tag fades IN over exactly the last tenth of the draw (lpPaintChart) - one place, one string, no double label */
    LEAD_GAP: 7,     /* the leader stops this far short of the tip and of the pill: a line that touches either reads as a stem, not a leader */
    PAD_X: 14, PAD_Y: 9,   /* the pill's padding around its type [DERIVED: the rail pill's own 2px/6px at 13px scaled to the chart's 19-34px name] */
  });

  /* ---- the line's arc length ------------------------------------------------------------------------------------- */
  const polyCum = (pts) => {
    const cum = [0];
    for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    return cum;
  };
  /* P_tip(u): the point at fraction u of the polyline's ARC LENGTH (what a dash offset draws to), and the unit tangent
     there - the pill's offset is applied in the page's frame, but the leader is drawn from the tip itself. */
  const tipAt = (pts, u) => {
    const n = pts.length;
    if (!n) return null;
    if (n === 1) return { p: [pts[0][0], pts[0][1]], t: [1, 0], i: 0 };
    const cum = polyCum(pts), L = cum[n - 1], s = Math.max(0, Math.min(1, u)) * L;
    let i = 0;
    while (i < n - 2 && cum[i + 1] < s) i++;
    const a = pts[i], b = pts[i + 1], seg = Math.max(1e-9, cum[i + 1] - cum[i]), k = Math.max(0, Math.min(1, (s - cum[i]) / seg));
    const p = [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k], d = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
    return { p, t: [(b[0] - a[0]) / d, (b[1] - a[1]) / d], i };
  };
  /* the fraction of the line's length at which a DATUM sits - how a milestone index becomes a milestone in u */
  const fracAtIndex = (pts, index) => {
    const cum = polyCum(pts), L = cum[cum.length - 1] || 1, i = Math.max(0, Math.min(pts.length - 1, index | 0));
    return cum[i] / L;
  };

  /* the pill kept ON the stage. X_pill = P_tip + D_offset is where it WANTS to be; a long tag riding a line that ends
     at the right edge would put half its string off the page (read off the first frame, 2026-09-11). The law is the
     offset, then the clamp - stated here so the caller cannot forget it and a test can pin it.
     `span` is the pill's own ink relative to its anchor point, [left, right] - the caller measures its box (a tag is
     written from its end, or its middle, and may carry a badge chip of its own; no character count gets that right). */
  const pillSpan = (x, span) => [x + span[0], x + span[1]];
  const pillClamp = (x, span, x0, x1) => {
    const [lo, hi] = pillSpan(x, span);
    if (hi - lo >= x1 - x0) return x;            /* wider than the stage: leave it where it is, the author wrote it */
    if (lo < x0) return x + (x0 - lo);
    if (hi > x1) return x - (hi - x1);
    return x;
  };

  /* ---- the pill ---------------------------------------------------------------------------------------------------- */
  /* the whole state at a drawn fraction u. `o.milestone` is the fraction the pill pops at (0 = with the first ink),
     `o.tag` the terminal tag's settled [x, y] - the place the pill hands over at. Nothing here reads the DOM. */
  const pillAt = (pts, u, o = {}) => {
    const P = Object.assign({}, TIPPILL, o.dials || {});
    const tip = tipAt(pts, u);
    if (!tip) return null;
    const m = Math.max(0, Math.min(1, o.milestone == null ? 0 : o.milestone));
    const pop = springPop(Math.max(0, Math.min(1, (u - m) / Math.max(1e-6, P.POP_F))), P.POP_MP);
    /* the settle: over the last SETTLE of the draw the pill leaves the tip for the tag's place, and the tag takes over
       as it lands - `handover` is what the caller cross-fades on (1 = the tag owns the name) */
    const s0 = 1 - P.SETTLE;
    const k = u >= 1 ? 1 : (P.SETTLE > 0 ? Math.max(0, Math.min(1, (u - s0) / P.SETTLE)) : 0);   /* the draw's end IS the hand-over, whatever the float says about 1 - 0.1 + 0.1 */
    const b = o.bounds, span = o.span;
    const rideX = b && span ? pillClamp(tip.p[0] + P.DX, span, b[0], b[1]) : tip.p[0] + P.DX;
    const ride = [rideX, tip.p[1] + P.DY];
    const land = o.tag ? [o.tag[0], o.tag[1]] : ride;
    /* at k = 1 the pill IS the tag's place - exactly, not within a float - because the tag is drawn there next frame */
    const pill = k >= 1 ? [land[0], land[1]] : [ride[0] + (land[0] - ride[0]) * k, ride[1] + (land[1] - ride[1]) * k];
    /* the leader, short of both ends; it fades with the settle (the pill is no longer the tip's) */
    const dx = pill[0] - tip.p[0], dy = pill[1] - tip.p[1], d = Math.hypot(dx, dy) || 1;
    const gap = Math.min(P.LEAD_GAP, d / 3), ux = dx / d, uy = dy / d;
    return {
      on: u > m && u < 1,
      tip: tip.p,
      pill,
      scale: pop,
      pop,
      settle: k,
      handover: k,
      leader: [[tip.p[0] + ux * gap, tip.p[1] + uy * gap], [pill[0] - ux * gap, pill[1] - uy * gap]],
      leaderOpacity: 1 - k,
    };
  };

  /* the pill's box for a measured text width - the caller measures its own type, the shape is the module's */
  const pillBox = (w, h, o = {}) => {
    const P = Object.assign({}, TIPPILL, o.dials || {});
    const bw = w + 2 * P.PAD_X, bh = h + 2 * P.PAD_Y;
    return { w: bw, h: bh, x: -bw / 2, y: -bh / 2, r: Math.min(bh / 2, 12) };
  };
  /* KINETICS:END */
  /* a ledger page's declared focus (page.focus = {kind, target?, label?}) is an implicit species at LP_FOCUS_AT;
     the target defaults to the emphasized datum (E22 addendum 6) */
  const pageFocus = (sc) => {
    const pg = sc.world && sc.world.kind === "ledger" ? sc.world.page : null;
    if (!pg || !pg.focus) return [];
    const f = pg.focus;
    return [{ kind: f.kind || "callout", at: sc.span[0] + LP_FOCUS_AT, dur: f.dur || LP.FOCUS_DUR, label: f.label,
              target: f.target || { kind: "datum", index: Number.isInteger(pg.emphasize) ? pg.emphasize : 0 }, target2: f.target2 }];
  };
  const paintSpecies = (sc, t) => {
    spTop.replaceChildren(); spUnder.replaceChildren(); plife.replaceChildren();
    const hasDocks = (sc.docks || []).length > 0;
    plife.style.transformOrigin = (STAGE_W / 2) + "px " + (STAGE_H / 2) + "px"; plife.style.transform = camCss(camNow(sc, t));   /* plate life lives in the world: the camera carries it */
    [...(sc.species || []), ...pageFocus(sc)].forEach((sp, si) => {
      const dur = sp.dur || 1, k = (t - sp.at) / Math.max(0.001, dur);
      if (k < 0 || k > 1) return;
      /* WHICH LAYER (operator, 2026-09-08: "the drawn circles should be on the layer beneath the card"): a species on a DATUM annotates
         the page's chart and paints beneath any card parked or thrown over it; a species on a point / region / span annotates whatever
         is there - the card itself, in the chart-callout golden - and paints above. Time is not the test: on the tariff parts page the
         ring began after the card arrived and still belonged to the bar beneath it. */
      spSvg = hasDocks && sp.target && sp.target.kind === "datum" ? spUnder : spTop;
      const seed = 0x51EC1E5 ^ ((sc.scene_id || "").length * 131 + si);
      /* the module rule: a registered painter OWNS its kind - it gets the declaration, the clock, the layer already
         chosen above and the shared helpers by name, and nothing in the chain below runs for it */
      const painter = SPECIES_PAINTERS[sp.kind];
      if (painter) {
        painter({ sp, k, dur, t, sc, si, seed, svg: spSvg, el: lpEl, A, resolveTarget, centre, stageBox,
                  ease: spEase, io: spIO, clamp: clamp01, drawOn, springPop, idle: idleXf, hash: lpHash,
                  camNow, idleOf,   /* P50 T5: a species ON A WORLD (the map's light, arc and stamp) rides the world's own camera and idle - the species layer is not the world div and carries neither by itself */
                  STAGE_W, STAGE_H, PORTRAIT });
        return;
      }
      if (sp.kind === "callout") {
        const b = resolveTarget(sp.target); if (!b) return;
        if (sp.form === "underline") {   /* P50 T3 / E56's ONE exception: a ring circles a number or a point on a chart,
             but an underline under a QUOTED PHRASE is the squiggle law (s9.27) - the same hand, the same .sq stroke,
             drawn from `at` over SQUIG_DRAW on the underline's own clock, riding the card's live geometry. */
          drawOn(lpEl("path", "sq", spSvg, { d: squigglePath(b, seed) }), underlineFrac(k * dur / SP.SQUIG_DRAW));
          return;
        }
        const pd = Number.isFinite(+sp.pad) ? +sp.pad : 0;
        drawOn(lpEl("path", "co", spSvg, { d: calloutPath(b, seed, pd) }), k * dur / SP.CALLOUT_DRAW);
        if (sp.label && k * dur > SP.CALLOUT_DRAW * 0.8) {
          const lx = b.x + b.w + 34 + pd, ly = b.y - 10 - pd * 0.4, pop = spEase((k * dur - SP.CALLOUT_DRAW * 0.8) / 0.25);
          const ls = Number.isFinite(+sp.label_scale) && +sp.label_scale > 0 ? +sp.label_scale : 1;   /* opt-in (2026-09-08): a stamp on a plate reads at phone size */
          const tx = lpEl("text", "lab", spSvg, { x: lx.toFixed(1), y: ly.toFixed(1) }); tx.textContent = sp.label;
          tx.setAttribute("transform", "translate(" + lx.toFixed(1) + " " + ly.toFixed(1) + ") scale(" + ((0.7 + 0.3 * pop) * ls).toFixed(3) + ") translate(" + (-lx).toFixed(1) + " " + (-ly).toFixed(1) + ")");
        }
      } else if (sp.kind === "spotlight") { /* dim the frame except a feathered hole gliding between two declared targets */
        const a = resolveTarget(sp.target), z = resolveTarget(sp.target2) || a; if (!a) return;
        const g = spIO((t - sp.at - (sp.glide_at || 0)) / 0.6);
        const ca = centre(a), cz = centre(z);
        /* E49 on the light itself (operator, 2026-09-09: "make sure all of the new additions pass the life check with the pixels
           shifting"): `idle` on a spotlight names one of IDLE_KINDS for the HOLE - its radius breathes by the idle's scale and its
           centre drifts by the idle's offset, the same seeded pure-function-of-t kinetics every held thing carries. Absent = still. */
        const ix = sp.idle && sp.idle !== "none" ? idleXf(sp.idle, t, lpHash(seed | 0, si | 0, 991)) : { scale: 1, dx: 0, dy: 0 };
        const cx = ca.cx + (cz.cx - ca.cx) * g + ix.dx, cy = ca.cy + (cz.cy - ca.cy) * g + ix.dy;
        const r0 = ((Math.max(a.w, 240) / 2 + 60) * ix.scale) / (PORTRAIT ? SPOT_R_PORTRAIT : STAGE_W / 2), id = "spot" + si;   /* the hole as a fraction of the gradient radius: the landscape half-width, kept on purpose in portrait (below) */
        const defs = lpEl("defs", "", spSvg);
        const rg = lpEl("radialGradient", "", defs, PORTRAIT ? { id, gradientUnits: "userSpaceOnUse", cx: cx.toFixed(1), cy: cy.toFixed(1), r: 960 }   /* portrait: a round hole, the offsets below keep their landscape size (960 = half the landscape width) */
                                                            : { id, cx: (cx / STAGE_W).toFixed(4), cy: (cy / STAGE_H).toFixed(4), r: 0.5 });
        lpEl("stop", "", rg, { offset: 0, "stop-color": "#000", "stop-opacity": 0 });
        lpEl("stop", "", rg, { offset: r0.toFixed(3), "stop-color": "#000", "stop-opacity": 0 });
        lpEl("stop", "", rg, { offset: (r0 + 0.12).toFixed(3), "stop-color": "#000", "stop-opacity": SP.SPOT_DIM });
        lpEl("stop", "", rg, { offset: 1, "stop-color": "#000", "stop-opacity": SP.SPOT_DIM });
        const fade = Math.min(spEase(k * dur / 0.4), spEase((1 - k) * dur / 0.4));
        lpEl("rect", "", spSvg, { x: 0, y: 0, width: STAGE_W, height: STAGE_H, fill: "url(#" + id + ")", opacity: fade.toFixed(2) });
      } else if (sp.kind === "squiggle") {   /* a hand-drawn underline under a declared caption word span (stage mode only) */
        const b = resolveTarget(sp.target); if (!b || !cap.classList.contains("stage")) return;
        drawOn(lpEl("path", "sq", spSvg, { d: squigglePath(b, seed) }), k * dur / SP.SQUIG_DRAW);
      } else if (sp.kind === "steam") {   /* STILL LIFE (operator, 2026-09-05): wisps rising off a declared region's top edge - three seeded
           curls, each a pure function of t (a period of STEAM_PERIOD), fading with height. Never a particle system. */
        const b = resolveTarget(sp.target); if (!b) return;
        const g = lpEl("g", "", spSvg, { fill: "none", "stroke-linecap": "round" });
        const ph = (t - sp.at) / SP.STEAM_PERIOD, rise = Math.max(160, b.w * 2.2), col = sp.color || "rgba(255,248,236,.42)";
        for (let w = 0; w < 3; w++) {
          const u = ((ph + w / 3) % 1 + 1) % 1;                        /* this wisp's own phase */
          const x0 = b.x + b.w * (0.25 + 0.25 * w) + (lpHash(seed, w, 41) - 0.5) * b.w * 0.2, y0 = b.y + 6;
          const amp = 10 + 14 * lpHash(seed, w, 42), turns = 1.5 + lpHash(seed, w, 43);
          let d = "M" + x0.toFixed(1) + " " + y0.toFixed(1);
          for (let k = 1; k <= 8; k++) {
            const s2 = k / 8, y = y0 - rise * s2 * (0.6 + 0.4 * u), x = x0 + Math.sin((s2 * turns + u) * Math.PI * 2) * amp * (0.4 + s2);
            d += " L" + x.toFixed(1) + " " + y.toFixed(1);
          }
          const op = (0.35 + 0.65 * Math.sin(u * Math.PI)) * clamp01(Math.min(k * dur / 0.6, (1 - k) * dur / 0.6));
          lpEl("path", "", g, { d, stroke: col, "stroke-width": (3 + 3 * u).toFixed(1), opacity: op.toFixed(3), filter: "blur(4px)" });
        }
      } else if (sp.kind === "trace") {   /* the arrow on the phone redraws: a seeded zigzag down the region's diagonal, drawn by dash over
           TRACE_DRAW, held, faded, again every TRACE_PERIOD */
        const b = resolveTarget(sp.target); if (!b) return;
        const hop = sp.hop && sp.hop.from && sp.hop.to ? sp.hop : null;   /* opt-in (2026-09-08, the crossings map): ONE bowed hop from a
           point to a point, drawn once over hop.draw_s (default TRACE_DRAW) and HELD to the end of dur - a crossing, not a still-life
           redraw. The plain trace is untouched when `hop` is absent. Coordinates are stage fractions; bow is the arc's height as a
           fraction of the chord, signed for the side. */
        const ph = hop ? 0 : (((t - sp.at) / SP.TRACE_PERIOD) % 1 + 1) % 1;
        const drawK = hop ? clamp01((t - sp.at) / Math.max(0.05, +hop.draw_s || SP.TRACE_DRAW)) : clamp01(ph * SP.TRACE_PERIOD / SP.TRACE_DRAW);
        const n = 7, pts = [];
        if (hop) {   /* a quadratic bow sampled to the same n points, so the arrowhead law below is shared */
          const x0 = hop.from[0] * STAGE_W, y0 = hop.from[1] * STAGE_H, x1 = hop.to[0] * STAGE_W, y1 = hop.to[1] * STAGE_H;
          const mx = (x0 + x1) / 2, my = (y0 + y1) / 2, dx = x1 - x0, dy = y1 - y0, L0 = Math.hypot(dx, dy) || 1;
          const bow = Number.isFinite(+hop.bow) ? +hop.bow : 0.18, cx2 = mx - dy / L0 * bow * L0 * 2, cy2 = my + dx / L0 * bow * L0 * 2;
          for (let i = 0; i <= n; i++) { const u = i / n, v = 1 - u;
            pts.push([v * v * x0 + 2 * v * u * cx2 + u * u * x1, v * v * y0 + 2 * v * u * cy2 + u * u * y1]); }
        } else {
          for (let i = 0; i <= n; i++) {
            const s2 = i / n, jag = i && i < n ? (lpHash(seed, i, 44) - 0.5) * b.h * 0.35 : 0;
            pts.push([b.x + b.w * (0.08 + 0.84 * s2), b.y + b.h * (0.12 + 0.76 * s2) + jag]);
          }
        }
        const d = pts.map(([x, y], i) => (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ");
        const sw = hop ? (Number.isFinite(+hop.width) ? +hop.width : 7) : Math.max(3, b.w * 0.045);
        const p = lpEl("path", "", spSvg, { d, stroke: sp.color || "#B0201F", "stroke-width": sw.toFixed(1), fill: "none", "stroke-linejoin": "round", "stroke-linecap": "round" });
        const fade = hop ? 1 : (ph > 0.82 ? 1 - (ph - 0.82) / 0.18 : 1);
        p.setAttribute("opacity", (fade * clamp01(Math.min(k * dur / 0.4, hop ? 1 : (1 - k) * dur / 0.4))).toFixed(3));
        drawOn(p, drawK);
        if (drawK >= 1) {   /* the arrowhead lands when the line does */
          const [ax, ay] = pts[n], [bx2, by2] = pts[n - 1], ang = Math.atan2(ay - by2, ax - bx2), L2 = hop ? sw * 3 : Math.max(8, b.w * 0.12);
          lpEl("path", "", spSvg, { d: "M" + (ax - L2 * Math.cos(ang - 0.5)).toFixed(1) + " " + (ay - L2 * Math.sin(ang - 0.5)).toFixed(1) + " L" + ax.toFixed(1) + " " + ay.toFixed(1) + " L" + (ax - L2 * Math.cos(ang + 0.5)).toFixed(1) + " " + (ay - L2 * Math.sin(ang + 0.5)).toFixed(1),
                                     stroke: sp.color || "#B0201F", "stroke-width": sw.toFixed(1), fill: "none", "stroke-linejoin": "round", "stroke-linecap": "round", opacity: p.getAttribute("opacity") });
        }
      } else if (sp.kind === "ticker") {   /* the numbers on the laptop tick: a rows x cols grid over the region; each cell flips on its own
           seeded clock (every TICK_STEP, phase per cell) - a paper patch (sp.paper) covers the drawn digit and a new one is
           written in the hand face. Stepped time: each flip is an event (gate: stepping at TICK_STEP). */
        const b = resolveTarget(sp.target); if (!b) return;
        /* the cells: the drawn grid's own lines when the author measured them (sp.col_lines / sp.row_lines, fractions of
           the frame - a still's grid is never uniform), else rows x cols over the region */
        const xs = sp.col_lines ? sp.col_lines.map((f) => f * STAGE_W) : [...Array((sp.cols || 6) + 1)].map((_, i) => b.x + b.w * i / (sp.cols || 6));
        const ys = sp.row_lines ? sp.row_lines.map((f) => f * STAGE_H) : [...Array((sp.rows || 6) + 1)].map((_, i) => b.y + b.h * i / (sp.rows || 6));
        const rows = ys.length - 1, cols = xs.length - 1, step = SP.TICK_STEP;
        const g = lpEl("g", "", spSvg, sp.tilt ? { transform: "rotate(" + sp.tilt + " " + (b.x + b.w / 2).toFixed(1) + " " + (b.y + b.h / 2).toFixed(1) + ")" } : {});
        for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
          const ci = r * cols + c, phase = lpHash(seed, ci, 45) * step, tick = Math.floor((t - sp.at - phase) / step);
          if (tick < 0) continue;
          const on = lpHash(seed, ci * 131 + tick, 46) < (sp.density || 0.35);   /* most cells rest on any given tick */
          if (!on) continue;
          const x = xs[c], y = ys[r], cw = xs[c + 1] - xs[c], chh = ys[r + 1] - ys[r], val = String(Math.floor(100 + lpHash(seed, ci * 977 + tick, 47) * 4900));
          const born = clamp01((t - sp.at - phase - tick * step) / 0.12);
          lpEl("rect", "", g, { x: (x + cw * 0.07).toFixed(1), y: (y + chh * 0.1).toFixed(1), width: (cw * 0.86).toFixed(1), height: (chh * 0.8).toFixed(1), rx: 3, fill: sp.paper || "#EFE8D5", opacity: born.toFixed(2) });   /* the patch covers the drawn digit inside its lines - a flip card, not an overprint */
          const tx = lpEl("text", "", g, { x: (x + cw / 2).toFixed(1), y: (y + chh * 0.74).toFixed(1), "text-anchor": "middle", fill: sp.ink || "#25313C", opacity: born.toFixed(2),
                                          style: "font-family:Kalam,Inter,sans-serif;font-weight:700;font-size:" + (chh * 0.6).toFixed(1) + "px" });
          tx.textContent = val;
        }
      } else if (sp.kind === "plate_life") { /* our cutouts on a bare plate: stepped time, throw-and-land with squash, two-frame boil */
        const step = Math.floor((t - sp.at) * SP.LIFE_FPS) / SP.LIFE_FPS;
        (sp.cutouts || []).forEach((c, ci) => {
          if (!A[c.asset]) return;
          const img = lpEl("img", "", plife); img.src = A[c.asset];
          const w = (c.w || 0.18) * STAGE_W, x = c.x * STAGE_W, y = c.y * STAGE_H, delay = (c.delay || 0) + ci * 0.15;
          const land = clamp01((step - delay) / SP.LIFE_LAND);
          const drop = (1 - spEase(land)) * -220;
          const squash = land >= 1 ? 1 : land > 0.85 ? 1 + (1 - land) * 1.2 : 1;
          const frame = Math.floor(step * SP.LIFE_FPS) % 2;
          const bx = (lpHash(seed, ci * 2 + frame, 31) - 0.5) * 2 * SP.BOIL_PX, by = (lpHash(seed, ci * 2 + frame, 32) - 0.5) * 2 * SP.BOIL_PX;
          const rot = (lpHash(seed, ci * 2 + frame, 33) - 0.5) * 2 * SP.BOIL_DEG;
          img.style.width = w.toFixed(1) + "px"; img.style.left = (x - w / 2).toFixed(1) + "px"; img.style.bottom = (STAGE_H - y).toFixed(1) + "px";
          img.style.opacity = step >= delay ? 1 : 0;
          img.style.transform = "translate(" + bx.toFixed(1) + "px, " + (drop + by).toFixed(1) + "px) rotate(" + rot.toFixed(2) + "deg) scale(" + (1 / squash).toFixed(3) + ", " + squash.toFixed(3) + ")";
        });
      }
    });
  };

  /* CLIP world: one <video> per world element, sourced from the asset map, seeked to the scene clock.
     A clip shorter than its scene holds its last frame (no loop - a loop is a visible seam). */
  const clipSeeks = new Set();
  let clipLive = false;   /* true while the transport is playing: clip worlds play instead of seeking */
  /* THE CLIP POOL (operator, 2026-09-05: "as soon as the scene change happens there's a black flash, THEN the page
     wipes"): a <video> created at the boundary has no decoded frame yet and paints black under the wipe's first
     frames. Every clip world's video is created at load, buffered, and parked in a hidden holder; a scene change
     MOVES the element into the world - its first frame is already there. Nothing is ever destroyed. */
  const clipPool = new Map(), clipHold = document.createElement("div");
  clipHold.id = "clippool"; clipHold.style.display = "none"; document.body.appendChild(clipHold);
  const clipFor = (asset) => {
    let v = clipPool.get(asset);
    if (!v) {
      v = document.createElement("video");
      v.className = "clipv"; v.muted = true; v.playsInline = true; v.preload = "auto";
      v.dataset.asset = asset; v.src = A[asset];
      clipPool.set(asset, v); clipHold.appendChild(v);
      try { v.load(); } catch (e) {}
    }
    return v;
  };
  (TL.scenes || []).forEach((sc) => { if (sc.world && sc.world.kind === "clip" && A[sc.world.asset_id]) clipFor(sc.world.asset_id); });
  /* a VIDEO DOCK's clip is pooled at load for the same reason a world clip is: a <video> created at
     the mount has no decoded frame and paints black under the card's 0.75s rise */
  const dockIsVideo = (aid) => ((TL.evidence || {})[aid] || {}).kind === "video";
  (TL.scenes || []).forEach((sc) => (sc.docks || []).forEach((d) => {
    if (dockIsVideo(d.slide) && A[d.slide]) clipFor(d.slide).loop = true;
  }));
  const parkClips = (el) => el.querySelectorAll("video.clipv").forEach((x) => { x.pause(); clipHold.appendChild(x); });
  /* THE ONE SEEK. Every <video> in this player - the world clip and the VIDEO DOCK alike - lands on
     its frame through this function. render(t) resolves fully from t, so there is exactly one answer
     to "which frame is on screen at t" and exactly one thing the renderer waits on (__clipsSeeked).
     LIVE playback (operator, 2026-09-05: "after ~2 seconds every flow video just holds"): a seek per
     frame on a clip with one keyframe decodes from frame 0 every time and falls behind; while the
     transport runs the video PLAYS on its own clock and is only corrected when it drifts. Scrubbing
     and the renderer still seek exactly (a pure function of t). */
  const seekVideo = (v, want) => {
    if (clipLive) {
      if (v.paused && (v.loop || want < (v.duration || Infinity) - 0.1)) v.play().catch(() => {});
      if (Math.abs((v.currentTime || 0) - want) > 0.15) { try { v.currentTime = want; } catch (e) {} }
      return;
    }
    if (!v.paused) v.pause();
    if (Math.abs((v.currentTime || 0) - want) > 0.04) {
      const p = new Promise((res) => {
        const done = () => { v.removeEventListener("seeked", done); clipSeeks.delete(p); res(); };
        v.addEventListener("seeked", done);
        setTimeout(done, 1500);   /* a seek that never fires (no metadata yet) must not hang a render */
      });
      clipSeeks.add(p);
      try { v.currentTime = want; } catch (e) { clipSeeks.delete(p); }
    }
  };
  const paintClip = (el, scene, t) => {
    let v = el.querySelector("video.clipv");
    if (!v || v.dataset.asset !== scene.world.asset_id) {
      parkClips(el);
      v = clipFor(scene.world.asset_id); v.pause(); v.loop = false; el.appendChild(v);
    }
    const local = Math.max(0, t - scene.span[0]);
    const want = Number.isFinite(v.duration) && v.duration > 0 ? Math.min(local, Math.max(0, v.duration - 0.05)) : local;
    seekVideo(v, want);
  };

  /* THE VIDEO DOCK (ruling E44 / backlog R26-7, operator 2026-09-06: "use the chart plate/ledger AND
     THEN DOCK the animation videos"). The dock's asset is a clip: the same pooled <video>, the same
     seek, mounted inside the card's slide-frame instead of the world. Its clock is the DOCK's -
     the clip starts at its own 0 when the card mounts (t - d.enter) and LOOPS if the card outlives
     it, because a card holding a frozen last frame is the still card this ruling exists to remove.
     The mount/retract choreography above is untouched: the <video> only replaces the <img>. */
  const parkDockClips = (el) => el.querySelectorAll(".slide-frame video.clipv")
    .forEach((x) => { x.pause(); clipHold.appendChild(x); });
  const paintDockClip = (el, d, t) => {
    const frame = el.querySelector(".slide-frame"); if (!frame) return;
    let v = frame.querySelector("video.clipv");
    if (!v || v.dataset.asset !== d.slide) {
      parkDockClips(el);
      v = clipFor(d.slide); v.pause(); v.loop = true; frame.appendChild(v);
    }
    const local = Math.max(0, t - d.enter);
    const dur = Number.isFinite(v.duration) && v.duration > 0 ? v.duration : 0;
    seekVideo(v, dur ? Math.min(local % dur, Math.max(0, dur - 0.05)) : local);
  };
  /* the renderer awaits this after scrubbing to t (render_baseline.frame_png) */
  window.__clipsSeeked = () => Promise.all([...clipSeeks]);

  const render = (t) => {
    let si = 0;
    for (let i = 0; i < TL.scenes.length; i++) if (t >= TL.scenes[i].span[0]) si = i;
    const sc = TL.scenes[si];

    /* LAYER 1 — one continuous ken-burns per scene; incoming world wipes in */
    /* The skill's camera lock does NOT apply here. In a whiteboard
       composition the camera moves the drawing surface, so travelling during
       a stroke breaks the illusion. In this lane the drawing surface is the
       dock — already fixed in screen space — and the world plate is a
       separate layer behind it. Its parallax never moves the paper, so it
       runs continuously and independently of any reveal. */
    const paint = (el, scene, dx = 0) => {
      /* LEDGER PAGE species: the world is drawn, not an image. The page
         paints itself from t; the authored Ken Burns still applies below,
         capped to a slow push (s9.26 rules). */
      const isLedger = scene.world.kind === "ledger";
      const isClip = scene.world.kind === "clip";
      /* P50 T5: the VECTOR MAP world. The branch stays thin on purpose (the operator's module rule): mount one
         svg fitted to the stage and hand it to species/vecmap.mjs, which owns the fit, the paths and the idle.
         A world that is not a map drops a stale one, the way the other branches drop a stale page. */
      const isVecmap = scene.world.kind === "vecmap";
      el.classList.toggle("ledger", isLedger);
      el.classList.toggle("vecmap", isVecmap);
      if (!isVecmap) el.querySelectorAll("svg.vm").forEach((x) => x.remove());
      if (isLedger) { el.style.backgroundImage = "none"; paintLedger(el, scene, t); }
      else if (isClip) {
        el.style.backgroundImage = "none";
        el.querySelectorAll(".lp").forEach((x) => x.remove());
        paintClip(el, scene, t);
      }
      else if (isVecmap) {
        el.style.backgroundImage = "none";
        el.querySelectorAll(".lp").forEach((x) => x.remove());
        const vm = el.querySelector("svg.vm") || lpEl("svg", "vm", el, {});
        vm.setAttribute("viewBox", `0 0 ${STAGE_W} ${STAGE_H}`);
        paintVecmapWorld({ scene, world: scene.world, t, A, root: vm, el: lpEl, idle: idleXf, hash: lpHash, idleOf, STAGE_W, STAGE_H });
      }
      else {
        el.style.backgroundImage = `url("${A[scene.world.asset_id]}")`;
        el.querySelectorAll(".lp").forEach((x) => x.remove());
      }
      if (!isClip) parkClips(el);   /* back to the pool, never destroyed */
      const kb0 = scene.world.ken_burns || { scale: 0, x: 0, y: 0 };
      const kb = isLedger ? { scale: Math.min(kb0.scale, LP.KB_MAX), x: 0, y: 0 } : kb0;
      const p = clamp01((t - scene.span[0]) / Math.max(0.1, scene.span[1] - scene.span[0]));
      /* THE WORLD LEANS IN WITH THE ARGUMENT (Gemini showcase: worldScale
         steps 1.02 -> 1.08 across a build). Each evidence event in this
         scene - a card landing, a badge stamping - eases the plate in one
         more notch on top of the authored drift. The world reacts to the
         evidence (doc 29 s2.4); drift alone reads as weather. */
      /* The lean-in is CUT until proven (operator, 2026-08-29): it ships
         nothing this episode and returns, if ever, as a side-by-side A/B
         of one scene judged in isolation. The authored Ken Burns is the
         only world motion. */
      /* E49: an IMAGE plate that holds, holds at its idle - a ledger page and a clip carry their own motion */
      const zi = (isLedger || isClip || isVecmap) ? 1 : idleXf(idleOf("plate", scene.world.idle), t, lpHash(Math.round(scene.span[0] * 100), 0, 977)).scale;   /* a vecmap breathes INSIDE its svg (vmIdle), so a species over it can ride the same pose */
      const z = (1 + p * kb.scale) * zi;
      el.style.transform = camCss(camNow(scene, t)) + `translateX(${dx.toFixed(1)}px) scale(${z.toFixed(4)}) `
        + `translate(${(p*kb.x).toFixed(1)}px, ${(p*kb.y).toFixed(1)}px)`;
    };
    const prev = TL.scenes[si - 1];
    wA.style.display = "";
    /* a page that ARRIVES by spiral is its own transition (operator, 2026-09-05: "we can't do a page wipe AND a spiral back
       in - the transition should BE the spiral"): no seam, the cream is there on the cut and the page surfaces out of it */
    const spiralIn = sc.world && sc.world.kind === "ledger" && sc.world.page && sc.world.page.enter === "spiral";
    /* SUCK (operator, 2026-09-05: "it needs to land as near to instantly on the next page as possible ... suck it in from all
       corners into a single point"): a row whose exit reads suck:<x>,<y> arrives on the cut, and the OUTGOING world collapses
       into that point of the new plate over SUCK_S, spinning - no wipe front, no seam */
    const suck = prev && typeof sc.exit === "string" && sc.exit.startsWith("suck") ? sc.exit : null;
    const su = suck ? clamp01((t - sc.span[0]) / SUCK_S) : 1;
    /* E47 (operator 2026-09-06): DIP and BLURZOOM straddle the boundary, so a scene reads its OWN exit for the
       half after its start and the NEXT scene's exit for the half before its end. `exit` names the transition INTO
       the scene it sits on - the same law the wipe, the suck and the dissolve above already follow. The switch
       itself is a cut: no wipe front, no seam (wk = 1 below), because the boundary frame is black (dip) or past
       the plate's detail (blur-zoom). */
    const nxt = TL.scenes[si + 1];
    const dipIn  = prev && exitName(sc.exit) === "dip" ? exitSecs(sc.exit, DIP_S) : 0;
    const dipOut = nxt && exitName(nxt.exit) === "dip" ? exitSecs(nxt.exit, DIP_S) : 0;
    const bzIn   = prev && exitName(sc.exit) === "blurzoom" ? exitSecs(sc.exit, BLURZOOM_S) : 0;
    const bzOut  = nxt && exitName(nxt.exit) === "blurzoom" ? exitSecs(nxt.exit, BLURZOOM_S) : 0;
    /* DISSOLVE (operator, 2026-09-05, on the wipe into the outro card - "what is this madness?"): a row whose exit reads dissolve
       arrives by a plain cross-fade over DISSOLVE_S - no front, no seam, the outgoing world keeps playing underneath */
    const snapIn = prev && sc.world && sc.world.kind === "ledger" && sc.world.page && sc.world.page.enter === "snap";   /* the card becomes the world: the page grows over the outgoing scene, which stays until covered */
    /* P49 T5: THE CAMERA ARRIVAL - over SNAP_S the eye goes to the landed card: the outgoing world and the card zoom together
       until the card's parked box (the dock's `place`, pure) fills the stage; the page waits hidden and shows at the match */
    const camInSc = prev && sc.world && sc.world.kind === "ledger" && sc.world.page && sc.world.page.enter === "camera";
    camArr = null;
    if (camInSc && t - sc.span[0] < SNAP_S) {
      const d = (prev.docks || []).find((x) => x.slide === sc.world.page.snap_from), del = d ? docks[d.slot | 0] : null;
      /* the card's box at rest: its parked `place`, else its LAYOUT box (left/top/width from the solo CSS, the height from the
         image - layout is untouched by transforms, so a cold seek reads the same box a played frame does), else the recorded rect */
      /* the LAYOUT box first: a card thrown onto a page carries a parked `place` it may never reach (a one-second card holds its
         reading size - the ring's Fed card, whose arrival zoomed past it); the element's layout IS where the card stands */
      const body = del && del.querySelector("img,video"), hasBody = !!body && (((body.naturalHeight | 0) > 0) || ((body.videoHeight | 0) > 0));   /* a card with no body has no layout to speak of: its parked place stands for it */
      const box = (hasBody && del.offsetWidth > 0 && del.offsetHeight > 40) ? { x: del.offsetLeft, y: del.offsetTop, w: del.offsetWidth, h: del.offsetHeight } : (d && d.place ? d.place : SNAP_RECT[sc.world.page.snap_from]);
      if (box && box.w > 0 && box.h > 0) {
        const u = minJerk(clamp01((t - sc.span[0]) / SNAP_S)), st = camArrivalState(box, u, STAGE_W, STAGE_H);
        camArr = { scene: prev, slide: sc.world.page.snap_from, u, box, state: { s: st.s, ox: st.look[0], oy: st.look[1], ax: st.at[0], ay: st.at[1] } };
      }
    }
    const throwIn = prev && sc.world && sc.world.kind === "ledger" && sc.world.page && (sc.world.page.enter === "throw" || sc.world.page.enter === "drop");   /* the plate is thrown onto the world: the world stays beneath until it has landed */
    wB.classList.toggle("snapping", (!!snapIn && t - sc.span[0] < SNAP_S) || !!camArr || (!!throwIn && t - sc.span[0] < (sc.world.page.enter === "drop" ? DROP_S : THROW_S) + THROW_SETTLE_S));
    const mountIn = prev && sc.world && sc.world.kind === "ledger" && sc.world.page && (sc.world.page.enter === "mount" || sc.world.page.enter === "morph");   /* MOUNT (operator, 2026-09-05): the outgoing scene fades while the cream plate mounts over it - no page turn; a MORPH page arrives the same way (P47 T3).
       NEVER a built page (operator, 2026-09-08: "when we're launching the chart already built we NEVER mount. Mounting is reserved for cream coming
       through over the scene, and then drawing") - enter=built takes the row's own transition, like a plate, and arrives with the chart standing */
    const dissolve = prev && (sc.exit === "dissolve" || mountIn);
    /* THE DANCE (operator, 2026-09-05, corrected: "the fades should be the WORLD fading, beneath it the CREAM should be building,
       and by the time we reach the actual transition time the full cream should be built and the chart should start drawing"):
       over the page's mount_s the OUTGOING world rides above and fades in MOUNT_STEPS steps while the page's cream plate builds
       beneath it in the other half of each step (paintLedger); at mount_s the world is gone, the cream is full, the page's own
       clock begins. The hand-off itself is no wipe (wk = 1) and no cross-fade of the page (dk = 1). */
    const mountS = mountIn ? (sc.world.page.mount_s || sc.world.page.morph_s || LP.FIELD) : 0, mu = mountIn ? clamp01((t - sc.span[0]) / mountS) : 1;
    const dk = dissolve && !mountIn ? (kin("min_jerk") ? minJerk : quartIO)(clamp01((t - sc.span[0]) / DISSOLVE_S)) : 1;
    /* E47 s3 (2026-09-06): the wipe is RETIRED as the world-change default and is reached by name only (wipe / wipe_right);
       a row that says `cut` is a cut - one frame, both plates steady, the reference's own most common boundary. Until
       2026-09-08 a `cut` row fell through to the wipe here, which is why two built pages arrived by a wipe nobody declared. */
    const hardCut = prev && exitName(sc.exit) === "cut";
    const wk = prev && !hardCut && !spiralIn && !snapIn && !throwIn && !suck && !dissolve && !dipIn && !bzIn ? (kin("min_jerk") ? minJerk : quartIO)(clamp01((t - sc.span[0]) / WIPE)) : 1;
    const seaming = prev && wk > 0 && wk < 1;
    /* THE HARD-EDGE CLIP WIPE (restored 2026-09-01). The remotion-ui
       directional-wipe port (dd9e476, 2026-08-30) replaced this with a
       feathered gradient mask plus DEPTH parallax. On review the feather
       read as a fade and the two moving pages read as a wipe going both
       directions; the port also flipped the reveal direction and mirrored
       the carried light. This is the reviewed form (doc 29 s9.15 ruling 1):
       ONE hard front, the incoming plate revealed by inset() at wk, nothing
       sliding, the ink seam riding the front at full strength. At wk=0 the
       inset hides wB completely, so the old plate holds and there is no
       destination-plate flash at the boundary. */
    wB.style.maskImage = "none"; wB.style.webkitMaskImage = "none";
    wB.style.opacity = camArr ? 0 : dissolve ? dk.toFixed(4) : 1;   /* P49 T5: the page waits for the eye to arrive */
    wB.style.clipPath = sc.exit === "wipe_right"
      ? `inset(0 0 0 ${(1-wk)*100}%)` : `inset(0 ${(1-wk)*100}% 0 0)`;
    paint(wA, prev || sc);
    paint(wB, sc);
    /* HF-17: the plate's foreground, over the cards. One layer per scene - a plate has one front - and it is up
       exactly while the dock that declared it is up, so a scene with no occluded dock costs nothing. */
    { const fgEl = document.getElementById("fgover");
      const fgD = (sc.docks || []).find((d) => d && d.fg && A[d.fg] && t >= +d.enter && t <= +d.exit);
      if (fgD) { if (fgEl.dataset.src !== fgD.fg) { fgEl.style.backgroundImage = 'url("' + A[fgD.fg] + '")'; fgEl.dataset.src = fgD.fg; }
                 fgEl.style.transform = wB.style.transform; fgEl.style.opacity = "1"; }
      else fgEl.style.opacity = "0"; }
    { const blur = camArr ? SNAP_BLUR * 4 * camArr.u * (1 - camArr.u) : 0;   /* the whoosh rides the arrival's speed (the snap's own envelope) */
      wA.style.filter = blur > 0.2 ? "blur(" + blur.toFixed(2) + "px)" : ""; }
    /* THE BLURZOOM (E47 #1). wB always carries the scene the frame is showing, so the outgoing magnification and
       the incoming rise are the same element on two clocks. min-jerk on the zoom (the ruling: the reference's
       zoom neither snaps nor sags); the softness rides the same u, an explicit numeric radius per frame - no
       random, no wall clock, so the frame stays a pure function of t. A scene shorter than the transition takes
       its outgoing half first (no shot in the reference is under 1.7 s, so the two never fight in practice). */
    let bzBlur = 0, bzScale = 1;
    if (bzOut) {
      const u = minJerk(clamp01((t - (nxt.span[0] - bzOut / 2)) / (bzOut / 2)));
      bzScale = 1 + (BLURZOOM_SCALE - 1) * u; bzBlur = BLURZOOM_BLUR * u;
    } else if (bzIn) {
      const u = minJerk(clamp01((t - sc.span[0]) / (bzIn / 2))), from = 1 / BLURZOOM_IN;
      bzScale = from + (1 - from) * u; bzBlur = BLURZOOM_BLUR * (1 - u);
    }
    if (bzScale !== 1) {
      wB.style.transformOrigin = "50% 50%";
      wB.style.transform = `scale(${bzScale.toFixed(4)}) ` + wB.style.transform;
    } else if (wB.style.transformOrigin) wB.style.transformOrigin = "";
    const bzCss = bzBlur > 0.001 ? `blur(${bzBlur.toFixed(2)}px)` : "none";
    bzveil.style.backdropFilter = bzCss; bzveil.style.webkitBackdropFilter = bzCss;
    /* THE DIP (E47 #1): a plain LINEAR ramp to black over the last DIP_S/2 of the outgoing scene and back over the
       first DIP_S/2 of the incoming one. Both halves reach 1 at the boundary, so the boundary frame IS black and
       the cut happens inside it. The veil sits above every layer, so the docks, the stage captions and the
       species ride the ramp down with the world and rise with the next one. */
    let dipA = 0;
    if (dipOut) dipA = Math.max(dipA, 1 - clamp01((nxt.span[0] - t) / (dipOut / 2)));
    if (dipIn)  dipA = Math.max(dipA, 1 - clamp01((t - sc.span[0]) / (dipIn / 2)));
    dipveil.style.opacity = dipA.toFixed(4);
    if (suck && su < 1) {
      const [px, py] = (suck.split(":")[1] || "0.5,0.5").split(",").map(Number);
      const ox = px * STAGE_W - wA.offsetLeft, oy = py * STAGE_H - wA.offsetTop;   /* the point in wA's own box (the world overhangs the stage 5%) */
      wA.style.transformOrigin = ox.toFixed(1) + "px " + oy.toFixed(1) + "px";
      const sk = kin("min_jerk") ? 1 - minJerk(su) : Math.pow(1 - su, 1.6);   /* the collapse: minimum-jerk when the build declares it */
      wA.style.transform = "rotate(" + (SUCK_TURN * (kin("min_jerk") ? minJerk(su) : su)).toFixed(1) + "deg) scale(" + sk.toFixed(4) + ") " + wA.style.transform;
      wA.style.zIndex = 3;   /* the outgoing world rides above the incoming plate while it collapses */
    } else if (mountIn && mu < 1) {   /* the dance: the outgoing world above the mounting page, fading in steps */
      wA.style.opacity = (1 - Math.floor(mu * MOUNT_STEPS) / MOUNT_STEPS).toFixed(4); wA.style.zIndex = 3;
    } else { if (wA.style.zIndex) wA.style.zIndex = ""; if (wA.style.opacity !== "") wA.style.opacity = ""; }
    seam.style.opacity = seaming ? 1 : 0;
    seam.style.transform = `translateX(${(sc.exit === "wipe_right" ? (1-wk) : wk) * STAGE_W}px)`;

    /* LAYER 2/3 — docks live on their own schedule */
    const live = DOCKS.filter((d) => t >= d.enter && t < d.exit + EXIT);
    const washOn = WASHES.some(([a, b]) => t >= a && t < b + EXIT);
    wash.classList.toggle("on", washOn);
    spot.classList.toggle("on", washOn);

    /* THE PAGE TURN CARRIES ITS OWN LIGHT. When every live card ends at
       the boundary being wiped, the wash and spotlight belong to the
       OUTGOING page - they clip with the same front, so the incoming world
       arrives clean and takes its own wash only when its own evidence
       lands. */
    const boundary = sc.span[0];
    const allOut = seaming && live.length > 0 &&
      live.every((x) => Math.abs(x.exit - boundary) < 0.35);
    /* the outgoing page's light leaves under the SAME hard front (doc 29
       s9.15 ruling 1). The incoming plate is visible on [0, wk] (spreading
       from the left), so the outgoing wash/spot must be visible on
       [wk, 100] - the inset that hides the left wk%. Same front, same
       progress; an inset cannot be mirrored the way the port's gradient
       (100-edge) was. */
    const frontClip = sc.exit === "wipe_right"
      ? `inset(0 ${wk * 100}% 0 0)` : `inset(0 0 0 ${wk * 100}%)`;
    for (const el2 of [wash, spot]) {
      el2.style.maskImage = "none"; el2.style.webkitMaskImage = "none";
      el2.style.clipPath = allOut ? frontClip : "none";
    }

    /* Which side does the evidence occupy? A solo card alternates sides by
       scene so the world is not always cropped the same way; a pair spans
       the frame, so the gradient runs bottom-up instead of sideways. */
    if (live.length === 1 && live[0].side !== "pair") {
      const right = live[0].side === "r";
      wash.style.setProperty("--wdir", right ? "90deg" : "270deg");
      spot.style.setProperty("--sx", right ? "72%" : "28%");
      spot.style.setProperty("--sy", "46%");
    } else if (live.length > 0) {
      wash.style.setProperty("--wdir", "180deg");
      spot.style.setProperty("--sx", "50%");
      spot.style.setProperty("--sy", "44%");
    }

    const worldAnswer = { x: 0, y: 0 };   /* HG2: the sum of this frame's landings (the dip, and a violent hit's shake), applied to the world layer below */
    /* a THROWN PAGE (enter=throw): the camera follows it up and settles with it, the ground takes its dip and shake, and its contact
       shadow darkens the outgoing world beneath as it comes down - the dock's landing at page size */
    const thr = wB.__lp && wB.__lp.throw;
    let pageContact = wA.querySelector(".page-contact");
    if (thr && thr.phase !== "settled") {
      if (!pageContact) { pageContact = document.createElement("div"); pageContact.className = "page-contact"; wA.appendChild(pageContact); }
      const cs = contactShadow(thr.h, thr.phase === "land" ? 0.1 : 0);
      pageContact.style.opacity = (cs.alpha * (thr.landed ? 0.6 : 0.9)).toFixed(3);
      pageContact.style.transform = "scale(" + cs.scale.toFixed(3) + ")";
      pageContact.style.filter = "blur(" + (cs.blur * 3).toFixed(1) + "px)";
      worldAnswer.y += thr.ground + thr.follow; worldAnswer.x += thr.shake.x; worldAnswer.y += thr.shake.y;
    } else if (pageContact) pageContact.style.opacity = "0";
    for (let s = 0; s < 2; s++) {
      const d = live.find((x) => x.slot === s && !isPressDock(x));   /* P50 T3: a press card is mounted by paintPress, not by a slot */
      const el = docks[s];
      if (!d) { el.style.opacity = 0; el.style.clipPath = "inset(0 100% 0 0)"; parkDockClips(el);
        const c0 = el.parentNode && el.parentNode.querySelector("#dock-contact-" + s); if (c0) c0.style.opacity = 0;   /* P47 T9: a card off its span takes its contact shadow with it (it lingered after the ring's snap) */
        continue; }
      if (d.slide !== shown[s]) { fillDock(s, d.slide); shown[s] = d.slide; }
      drawRecord(s, t);
      drawChart(s, t, d);
      drawStack(s, t, d);
      if (dockIsVideo(d.slide)) paintDockClip(el, d, t);   /* E44: the card's clip, on the dock's clock */
      const solo = d.side !== "pair" && s === 0;
      el.classList.toggle("solo", solo);
      el.classList.toggle("side-r", solo && d.side === "r");
      el.classList.toggle("side-l", solo && d.side === "l");
      /* E45 s1 (2026-09-06): a dock on a LEDGER PAGE parks in a rectangle the COMPILER computed
         from the page's own geometry - `d.place` in stage pixels {x, y, w, h}: a small card (about
         half the stage width) in the page's quiet space, never over the plot, the title, the source
         line or the caption's anchor. Inline width/left/top outrank the .solo defaults; the card's
         height stays its content's (the video slide-frame keeps aspect-ratio 16/9 and an image keeps
         its intrinsic height), so `place.h` is the compiler's prediction, never a forced box. A dock
         with no `place` - every dock on a plain plate - is left exactly as it was, and the mount /
         retract choreography below reads the card's own box either way.
         The card does not CUT to that rectangle: dockGeom above springs it in at reading size,
         holds it for `read_s`, then shrinks and slides it here over `park_s` on the minimum-jerk
         path. At the end of the park this box is `place` exactly. */
      const G = dockGeom(el, d, t);
      el.style.width = G ? G.w.toFixed(2) + "px" : "";
      el.style.left = G ? G.x.toFixed(2) + "px" : "";
      el.style.top = G ? G.y.toFixed(2) + "px" : "";

      /* Card settle — the whole entrance. The document is simply present on
         the card; no mask, no drawing hand. Reference timing: a 0.75s
         expo-out rise with the hard-edge shadow growing alongside, so the
         card reads as a physical object landing on the plate. */
      const ck = expoOut(clamp01((t - d.enter) / CARD_IN));
      const xk = t > d.exit ? clamp01((t - d.exit) / EXIT) : 0;
      const xe = expoOut(xk);
      /* THE PAGE WIPE CLEARS THE PAGE. A card whose life ends at a scene
         boundary is part of the outgoing page, so the wipe front takes it -
         same edge, same progress. Fading it on its own schedule while the
         world slides underneath is what read as clipping. A card that
         SURVIVES the boundary is not on the outgoing page and is never
         clipped: it holds while the world changes behind it. */
      /* A card ending at the boundary (d.exit ~ sc.span[0], the seam being
         wiped) is carried off by the front - same edge, same progress, its
         shadow easing out beneath it. A card that survives the boundary is
         never touched: it holds while the world changes behind it. */
      const swept = seaming && Math.abs(d.exit - boundary) < 0.35;
      if (swept) {
        /* THE FRONT IS A STAGE POSITION; the card clip must be computed in
           the CARD's own space. inset(0 wk% 0 0) hides wk% OF THE CARD -
           whether that lines up with the seam depends on where the card
           happens to sit, which is how a card got severed mid-air with the
           front nowhere near it (operator screenshot, 0:41). Map the
           front's stage X into element coordinates. */
        const fx = (sc.exit === "wipe_right" ? (1 - wk) : wk) * STAGE_W;
        const L = el.offsetLeft, W2 = el.offsetWidth || 1;
        /* the stage front mapped into the CARD's space as a HARD inset: the
           card is severed at the same hard edge the page turns on, same
           progress (restored 2026-09-01 - the port's feathered mask made
           the card dissolve, which read as a fade on review). */
        if (sc.exit === "wipe_right") {   // incoming spreads from the right
          const hide = clamp01(((L + W2) - fx) / W2);
          el.style.clipPath = `inset(0 ${(hide * 100).toFixed(2)}% 0 0)`;
        } else {                          // incoming spreads from the left
          const hide = clamp01((fx - L) / W2);
          el.style.clipPath = `inset(0 0 0 ${(hide * 100).toFixed(2)}%)`;
        }
        el.style.maskImage = "none"; el.style.webkitMaskImage = "none";
        el.style.opacity = clamp01((t - d.enter) / (CARD_IN * 0.55));
      } else {
        el.style.clipPath = "none";
        el.style.maskImage = "none"; el.style.webkitMaskImage = "none";
        el.style.opacity = (1 - xe) * clamp01((t - d.enter) / (CARD_IN * 0.55));
      }
      /* E45: a PLACED card arrives and leaves on the spring - it never cuts and never dissolves.
         The arrival is the POP preset (Mp = 4%) on scale, DOCK_POP_FROM -> 1, landing on exactly
         1 at u = 1 so the parked box is `place` to the pixel; the retract is the same spring run
         backwards over DOCK_RETRACT_S, a fast settle rather than a fade. Everything else - a dock
         on a plain plate - keeps the 0.75s expo-out lift it has always had. */
      const arr = arriveOf(d);
      el.dataset.slide = d.slide;
      el.style.visibility = "";
      const snapSc = SNAP_FROM[d.slide];   /* the card a snapping page grows from: record its layout box, hide it once the page has it */
      el.classList.toggle("card-page", !!snapSc);   /* a card the page will become: rounded, no frame, the cream is the edge */
      if (snapSc) {
        const im = el.querySelector("img, video") || el;
        if (im.offsetHeight > 2) SNAP_RECT[d.slide] = { x: el.offsetLeft + (im === el ? 0 : im.offsetLeft), y: el.offsetTop + (im === el ? 0 : im.offsetTop), w: im.offsetWidth, h: im.offsetHeight };   /* an image still loading has no height yet */
        const byEye = snapSc.world.page.enter === "camera";   /* P49 T5: the card stays through the arrival and hides at the match - on the SAME predicate the page shows on (camArr), never a second clock (a 10 ms scrub step put one bare frame between the card and the page) */
        if (t >= snapSc.span[0] && !(byEye && camArr && camArr.slide === d.slide)) el.style.visibility = "hidden";
      }
      el.classList.toggle("arriving", arr !== "spring");
      let contact = el.parentNode ? el.parentNode.querySelector("#dock-contact-" + s) : null;
      if (arr !== "spring") {   /* P47 T1: the card ARRIVES by a throw or a landing, then the park choreography (dockGeom) is untouched */
        const rk = t > d.exit ? springPop(clamp01((t - d.exit) / DOCK_RETRACT_S)) : 0;   /* P49 T5: a camera page's card carries an exit past the match - the compiler extends it (extend_camera_cards) */
        const from = { x: (d.side === "l" ? -1 : 1) * ((el.offsetWidth || 800) + STOP_THROW_DX), y: -STOP_THROW_DY };
        const opts = d.violent ? { violent: true } : {};   /* a stage shake reads as violence, not mass - opt-in per dock (the report Q3) */
        const sx = arr === "throw" ? throwXf(from, d.mass || "paper", t - d.enter, opts) : landXf(d.mass || "paper", t - d.enter, opts);
        el.style.transform = stopCss(sx) + " scale(" + (1 - (1 - DOCK_POP_FROM) * rk).toFixed(4) + ")"
          + idleCssFor("dock", d.idle, t, Math.round(d.enter * 100) + s, 3);
        if (!swept) el.style.opacity = clamp01(1 - rk) * (t >= d.enter ? 1 : 0);
        /* HG2: the CONTACT SHADOW on the landing spot - far and faint while the card is high, tight and dark on the floor, spread by the
           hit's squash; it lives beneath the card in the dock layer and dies with the card */
        if (!contact) { contact = document.createElement("div"); contact.className = "dock-contact"; contact.id = "dock-contact-" + s; el.parentNode.insertBefore(contact, el); }
        const cs = contactShadow(sx.h || 0, sx.phase === "land" ? sx.alpha * 0.5 : 0);   /* the hit spreads the shadow by half the squash: a footprint, not a floor */
        const Wd = G ? G.w : (el.offsetWidth || 800), Hd = el.offsetHeight || 450;   /* the PLACED width (the reading rect, then the park), never the .dock CSS default */
        const L = parseFloat(el.style.left) || el.offsetLeft, T0 = parseFloat(el.style.top) || el.offsetTop;
        contact.style.left = (L + Wd * 0.06).toFixed(1) + "px"; contact.style.width = (Wd * 0.88).toFixed(1) + "px"; contact.style.top = (T0 + Hd - 6).toFixed(1) + "px";
        contact.style.transform = "scale(" + cs.scale.toFixed(3) + ", " + (cs.scale * 0.9).toFixed(3) + ")";
        contact.style.filter = "blur(" + cs.blur.toFixed(2) + "px)";   /* the depth cue: wide high up, a slit at contact */
        contact.style.opacity = (t >= d.enter && sx.phase !== "settled" ? cs.alpha * clamp01(1 - rk) : 0).toFixed(3);
        contact.style.visibility = el.style.visibility;   /* a card hidden for a snap takes its shadow with it */
        /* the ground ANSWERS with a DIP the card rides (mass), and only a violent hit shakes it */
        if (sx.ground) worldAnswer.y += sx.ground;
        if (sx.shake && (sx.shake.x || sx.shake.y)) { worldAnswer.x += sx.shake.x; worldAnswer.y += sx.shake.y; }
      } else if (G) {
        if (contact) contact.style.opacity = "0";
        const pk = springPop(clamp01((t - d.enter) / DOCK_POP_S));
        const rk = t > d.exit ? springPop(clamp01((t - d.exit) / DOCK_RETRACT_S)) : 0;
        el.style.transform = "scale(" + (DOCK_POP_FROM + (1 - DOCK_POP_FROM) * (pk - rk)).toFixed(4) + ")"
          + idleCssFor("dock", d.idle, t, Math.round(d.enter * 100) + s, 3);   /* E49: the parked card breathes */
        if (!swept) el.style.opacity = clamp01(1 - rk) * clamp01((t - d.enter) / DOCK_FADE_S);
      } else if (camArr && camArr.slide === d.slide) {   /* P49 T5: the landed card rides the arrival - screen = at + s (p - look), written about the card's own top-left */
        const st = camArr.state, L = el.offsetLeft, Tp = el.offsetTop;
        el.style.transformOrigin = "0 0";
        el.style.transform = "translate(" + (st.ax + st.s * (L - st.ox) - L).toFixed(2) + "px, " + (st.ay + st.s * (Tp - st.oy) - Tp).toFixed(2) + "px) scale(" + st.s.toFixed(5) + ")";
        const blur = SNAP_BLUR * 4 * camArr.u * (1 - camArr.u); el.style.filter = blur > 0.2 ? "blur(" + blur.toFixed(2) + "px)" : "";
      } else el.style.transform = ((xk && !swept)
        ? "translateY(" + (-22 * xe) + "px) scale(" + (1 - 0.05 * xe) + ")"
        : "translateY(" + (32 * (1 - ck)) + "px) scale(" + (0.96 + 0.04 * ck) + ")")
        + idleCssFor("dock", d.idle, t, Math.round(d.enter * 100) + s, 3);
      if (camArr && camArr.slide === d.slide) {   /* P49 T5: the landed card rides the arrival - screen = at + s (p - look), composed BEFORE the card's own transform about the card's own centre (its origin) */
        /* the prefix composes about the card's OWN transform-origin (a thrown card's is its bottom edge, the squash's contact
           edge - the first cut scaled about the centre and the card climbed 250 px off the top at the match) */
        const st = camArr.state, org = (getComputedStyle(el).transformOrigin || "").split(" ").map(parseFloat);
        const Cx = el.offsetLeft + (Number.isFinite(org[0]) ? org[0] : (el.offsetWidth || 0) / 2), Cy = el.offsetTop + (Number.isFinite(org[1]) ? org[1] : (el.offsetHeight || 0) / 2);
        el.style.transform = "translate(" + (st.ax + st.s * (Cx - st.ox) - Cx).toFixed(2) + "px, " + (st.ay + st.s * (Cy - st.oy) - Cy).toFixed(2) + "px) scale(" + st.s.toFixed(5) + ") " + el.style.transform;
        const blur = SNAP_BLUR * 4 * camArr.u * (1 - camArr.u); el.style.filter = blur > 0.2 ? "blur(" + blur.toFixed(2) + "px)" : "";
      } else if (el.style.filter) el.style.filter = "";
      const shk = arr !== "spring" ? expoOut(clamp01((lag(t) - d.enter) / CARD_IN)) : ck;   /* HF-2: a thrown or landed card's shadow settles one frame after it */
      const sh = 12 * shk * (swept ? (1 - wk) : 1);   // light leaves with the page
      el.style.boxShadow = sh.toFixed(1) + "px " + sh.toFixed(1) + "px 0 rgba(37,49,60,.82)";

      const badges = (TL.evidence[d.slide] || {}).badges || [];
      /* THE CALLOUT IS THE CONCLUSION (remotion-ui comparison-bars,
         2026-08-31): a badge stating a chart's conclusion lands only
         after the draw finishes - its reveal is floored at the chart's
         draw-complete time */
      const chartDone = (chartState[s] && chartState[s].doneAt) || 0;
      badges.forEach((_, bi) => {
        const pill = document.getElementById(`p${s+1}${bi}`);
        const at = (d.badge_at || [])[bi];
        if (pill) pill.classList.toggle("on",
          at != null && t >= Math.max(at, chartDone) && t < d.exit);
      });
    }
    paintPress(live, t);   /* P50 T3: the press stack, outside the two slots - a pile can be three cards deep */
    if (worldAnswer.x || worldAnswer.y) {   /* the ground takes the weight: the dip (and a violent hit's shake) on the world, on top of its own transform */
      for (const wl of [wA, wB]) if (wl.style.display !== "none") {
        /* the OUTGOING world (wA) is a plate that must keep the frame covered while it rides down: a downward answer of y px also
           scales it by 1 + y / H about its bottom edge, so its top edge stays at 0 (a thrown page's camera follow exposed a black band
           above the podium, 2026-09-08). The incoming world (wB) rides plainly - it is the thing being thrown or is already the stage. */
        const comp = wl === wA && worldAnswer.y > 0 ? " scale(" + (1 + worldAnswer.y / STAGE_H).toFixed(5) + ")" : "";
        if (comp) wl.style.transformOrigin = "50% 100%";
        wl.style.transform = (wl.style.transform || "") + " translate(" + worldAnswer.x.toFixed(2) + "px," + worldAnswer.y.toFixed(2) + "px)" + comp;
      }
    }
    const active = live;

    /* LAYER 5 — canonical caption track: resolved by time at its own
       timings, never resampled onto beat boundaries (doc 29 Part 5). */
    const quiet = active.length > 0;
    /* STAGE (s9.25 #2): the timeline declares it; the anchor is the shared-stage position only */
    /* a ledger page may pin its captions to the anchor (page.caption === "anchor"): a host plate's quiet zone is the host's (C5 addendum) */
    const capPinned = sc.world.kind === "ledger" && sc.world.page && sc.world.page.caption === "anchor";
    const stage = !quiet && !capPinned && (TL.caption_modes || []).includes("stage");
    const PG = TL.caption_pages, CAP_LAST_HOLD_S = 0.4;
    if (PG) {
      /* KINETIC (doc 29 Part 5): 2-4 word groups punch into the fixed anchor,
         power3.out, scale 1.14 -> 1.0, y 12 -> 0; keywords in the accent.
         Active token by fromMs <= now < toMs (remotion page/token model).
         QUIET (4.2): while a document holds the stage the group is static -
         single fade, keywords still coloured, no punch-in. */
      let pi = -1;
      for (let i = 0; i < PG.length; i++) if (PG[i].s <= t) pi = i;
      /* a page holds the strip until the next page - except the LAST one: it clears CAP_LAST_HOLD_S after its own end, so a
         rendered outro after the last word (the Remotion kit card, 2026-09-05) shows nothing but itself */
      if (pi >= 0 && pi === PG.length - 1 && PG[pi].e != null && t > PG[pi].e + CAP_LAST_HOLD_S) pi = -1;   /* an EMPTY page list (a bare-hold build) left pi = -1 = length - 1 and threw on PG[-1] - the throw at load skipped every later definition (P47 T2) */
      const pg = pi >= 0 ? PG[pi] : null;
      if (pi !== cap._pi) {
        cap._pi = pi;
        cap.innerHTML = pg ? '<span class="cg">' + pg.t.map((x, j) =>
          '<span class="cw' + (x.k ? " ck" : "") + '" style="--tilt:' + (j % 2 ? "-2.5deg" : "2.5deg") + '">' + x.w + "</span>").join(" ")
          + "</span>" : "";
        const g = cap.firstChild;
        if (g && !quiet && !stage) {
          g.style.transition = "none";
          g.style.opacity = 0; g.style.transform = "translateY(12px) scale(1.14)";
          requestAnimationFrame(() => {
            g.style.transition = "opacity .28s cubic-bezier(.215,.61,.355,1)," +
                                 "transform .34s cubic-bezier(.215,.61,.355,1)";
            g.style.opacity = 1; g.style.transform = "translateY(0) scale(1)";
          });
        }
      }
      if (pg) { const ws = cap.querySelectorAll(".cw");
        pg.t.forEach((x, j) => { if (ws[j]) { const on = x.s <= t && t < x.e; ws[j].classList.toggle("on", on);
          /* stage: each word pops in at its own spoken time (words.json), never at the page boundary.
             The pop is a pure function of t painted inline (see stagePop) so a scrubbed render
             captures mid-pop frames and two renders of one second are identical. */
          if (stage && PHRASE) {   /* KINETIC (operator, 2026-09-05: 'we need more kinetic activity ... back to dynamic captions, 4-7 words per
             sentence'): the golden set's word pops - each word lands on its own spoken time with the explosive spring and a rise -
             on a page that holds a sentence; a keyword takes the red box as it lands and stays gold on it */
            const pop = kin("analytic_spring") ? springPop : stagePop;
            const e = pop(clamp01((t + 0.05 - x.s) / STAGE_POP_S));                       /* this word's own pop and rise */
            const ke = e, kOn = x.k && t >= x.s;
            const hk = x.k ? pow2out(clamp01((t - x.s) / MARK.SWEEP_S)) : 0;            /* the keyword's box sweeps in when spoken, stays */
            ws[j].style.opacity = Math.min(1, e * 2).toFixed(3);
            /* ALIVE (operator, 2026-09-05: 'the words shifting slightly to stay alive, like the golden set'): the spoken word lifts 6% as the
               voice passes it, and every landed word BOILS - the engine's two-frame boil (SP.BOIL_PX / BOIL_DEG at LIFE_FPS), seeded per word */
            const sc = (MARK.POP + (1 - MARK.POP) * e) * (kOn ? (MARK.KPOP + (1 - MARK.KPOP) * ke) : 1) * (on && e >= 1 ? MARK.LIFT : 1);
            const tick = Math.floor(t * SP.LIFE_FPS), bseed = Math.round(pg.s * 100) + j * 97, boil = e >= 1;
            const bx = boil ? (lpHash(bseed, tick, 61) - 0.5) * 2 * MARK.BOIL_PX : 0, by = boil ? (lpHash(bseed, tick, 62) - 0.5) * 2 * MARK.BOIL_PX : 0;
            const bdeg = boil ? (lpHash(bseed, tick, 63) - 0.5) * 2 * MARK.BOIL_DEG : 0;
            ws[j].style.transform = "translate(" + bx.toFixed(2) + "px," + (MARK.RISE_PX * (1 - e) + by).toFixed(2) + "px) scale(" + sc.toFixed(4) + ") rotate(calc(var(--tilt, 0deg) * " + (1 - e).toFixed(3) + " + " + bdeg.toFixed(2) + "deg))";
            ws[j].style.backgroundImage = hk > 0 ? markBox(MARK.RED, 1) : "";
            ws[j].style.backgroundSize = hk > 0 ? (hk * 100).toFixed(1) + "% 100%" : "";
            ws[j].classList.toggle("lit", hk > 0.5); }
          else if (stage) { const e = (kin("analytic_spring") ? springPop : stagePop)(clamp01((t + 0.05 - x.s) / STAGE_POP_S));
            ws[j].style.opacity = Math.min(1, e * 2).toFixed(3);
            const sc = (1.16 + (1 - 1.16) * e) * (on && e >= 1 ? 1.06 : 1);
            ws[j].style.transform = "scale(" + sc.toFixed(4) + ") rotate(calc(var(--tilt, 0deg) * " + (1 - e).toFixed(3) + "))"; }
          else { ws[j].style.opacity = ""; ws[j].style.transform = ""; } } }); }
      cap.style.transform = (pg && !(stage && PHRASE)) ? idleCssFor("caption", undefined, t, Math.round(pg.s * 100), 5) : "";   /* E49: the strip at its idle beneath the words' own pops (phrase mode boils already) */
      cap.style.opacity = pg ? 1 : 0;
    } else {
      let line = null;
      for (const c of TL.captions) { if (t >= c.at && t < c.until) { line = c; break; } }
      cap.textContent = line ? line.text : "";
      cap.style.transform = line ? idleCssFor("caption", undefined, t, Math.round(line.at * 100), 5) : "";
      cap.style.opacity = line
        ? Math.min(clamp01((t - line.at) / 0.22), clamp01((line.until - t) / 0.18)) : 0;
    }
    cap.classList.toggle("quiet", quiet || capPinned);
    cap.classList.toggle("stage", stage);
    cap.classList.toggle("phrase", stage && PHRASE);
    paintSpecies(sc, t);
    /* on a LEDGER PAGE the stage caption sits in the page's declared quiet zone (s9.25 #2, s9.28 C2:
       never over the emphasized datum); elsewhere it is centred */
    const qz = stage && sc.world.kind === "ledger" && sc.world.page ? sc.world.page.quiet_zone : null;
    cap.style.left = qz === "right" ? "58%" : qz === "left" ? "120px" : "";
    cap.style.right = qz === "left" ? "58%" : qz === "right" ? "120px" : "";
    /* PORTRAIT (P41): a ledger page fills the frame, so its stage caption takes the caption strip (y 1340-1440, G-l), never the chart */
    const onPage = PORTRAIT && stage;   /* portrait: the caption strip on every world - the 40% band is where a plate's subject lives (the promise plate's laptop, 2026-09-05) */
    cap.classList.toggle("onpage", onPage);
    if (onPage) { cap.style.left = ""; cap.style.right = ""; }

    [...chips.children].forEach((c, i) => c.classList.toggle("on", i === si));
  };

  /* transport — audio is the clock while playing */
  let t = 0, playing = false, raf = 0;
  const clock = $("clock"), playBtn = $("play");
  const fmt = (s) => `${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,"0")}`;
  /* SOUND ENGINE: cues from TL.sound scheduled on the master clock.
     Each cue owns per-variant <audio> elements built from the embedded
     data URIs; the review strip switches variants LIVE. */
  const SND = (TL.sound || []).map((c) => {
    const els = {};
    for (const [vk, key] of Object.entries(c.variants)) {
      const a = new Audio(A[key]); a.preload = "auto"; els[vk] = a;
    }
    return { ...c, els, sel: Object.keys(c.variants)[0], vol: c.gain };
  });
  /* a cue's ENVELOPE: `env` = [[t, dB], ...] against the cue's own gain, linear between keys, flat outside them - the bed
     breathes with the structure (the research blueprint, rule 3: it rises under scene transitions - a thrown card's landing
     and snap; operator, 2026-09-08: the landing "sounds much better" with the bed up). A pure function of t: seek-exact. */
  const envGain = (c, tt) => {
    const e = c.env; if (!e || !e.length) return 1;
    if (tt <= e[0][0]) return Math.pow(10, e[0][1] / 20);
    for (let i = 1; i < e.length; i++) if (tt <= e[i][0]) {
      const [t0, d0] = e[i - 1], [t1, d1] = e[i]; const k = t1 > t0 ? (tt - t0) / (t1 - t0) : 1;
      return Math.pow(10, (d0 + (d1 - d0) * k) / 20);
    }
    return Math.pow(10, e[e.length - 1][1] / 20);
  };
  const syncSound = (tt, isPlaying) => {
    for (const c of SND) {
      for (const [vk, el] of Object.entries(c.els)) {
        const active = isPlaying && vk === c.sel && c.sel !== "off";
        const dur = el.duration || 0;
        const off = tt - c.at;
        if (active && off >= 0 && dur && off < dur) {
          const fade = c.fade_in > 0 ? Math.min(1, off / c.fade_in) : 1;
          el.volume = Math.min(1, c.vol * fade * envGain(c, tt));
          if (el.paused) { el.currentTime = off; el.play().catch(() => {}); }
          else if (Math.abs(el.currentTime - off) > 0.3) el.currentTime = off;
        } else if (!el.paused) el.pause();
      }
    }
  };
  {
    const bar = document.getElementById("sndbar");
    const fmtC = (s) => `${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,"0")}`;
    for (const c of SND) {
      const d = document.createElement("div"); d.className = "sndcue";
      d.innerHTML = `<span class="lbl">${c.slot}</span>`;
      /* jump-to-cue: sound is judged AT its moment - land 2s early so
         the enter is heard in context (operator: "doesn't show me where
         the sounds are actually playing") */
      const j = document.createElement("button");
      j.textContent = "▸ " + fmtC(c.at);
      j.title = "jump to this cue";
      j.addEventListener("click", () => {
        seek(Math.max(0, c.at - 2));
        if (!playing) playBtn.click();
      });
      d.appendChild(j);
      const keys = [...Object.keys(c.els), "off"];
      for (const vk of keys) {
        const b = document.createElement("button");
        b.textContent = vk.toUpperCase();
        if (vk === c.sel) b.classList.add("on");
        b.addEventListener("click", () => {
          c.sel = vk;
          d.querySelectorAll("button").forEach(x => x.classList.remove("on"));
          b.classList.add("on");
          syncSound(t, playing);
        });
        d.appendChild(b);
      }
      /* the level slider reads in dB AGAINST THE PLAN (operator, 2026-09-08: a linear 0-1 slider in 0.05 steps could not show a
         -26 LU bed (gain 0.0188 sits below its first notch) and its first touch jumped the bed 8-15 dB). Centre = the plan's gain,
         +-12 dB to audition, the number on screen; the plan itself is changed in the build (BED_LU), never here. */
      const r = document.createElement("input");
      r.type = "range"; r.min = -12; r.max = 12; r.step = 1; r.value = 0; r.title = "dB against the plan's gain";
      const ro = document.createElement("span"); ro.className = "dbro"; ro.textContent = "plan";
      r.addEventListener("input", () => { const db = +r.value; c.vol = c.gain * Math.pow(10, db / 20); ro.textContent = db === 0 ? "plan" : (db > 0 ? "+" : "") + db + " dB"; });
      d.appendChild(r); d.appendChild(ro);
      bar.appendChild(d);
    }
  }
  const sync = () => { scrub.value = t; clock.textContent = `${fmt(t)} / ${fmt(DUR)}`; render(t); syncSound(t, playing); };
  const seek = (v) => { t = Math.min(DUR, Math.max(0, v)); vo.currentTime = t; sync(); };
  const tick = () => {
    if (!playing || MY !== __mountGen) return;   /* P51 T4: a replaced mount's play loop stops here */
    t = Math.min(DUR, vo.currentTime);
    if (t >= DUR) { playing = false; clipLive = false; vo.pause(); playBtn.innerHTML = "&#9654; Replay"; }
    sync();
    if (playing) raf = requestAnimationFrame(tick);
  };
  playBtn.addEventListener("click", () => {
    if (playing) { playing = false; clipLive = false; vo.pause(); cancelAnimationFrame(raf); playBtn.innerHTML = "&#9654; Play with narration"; syncSound(t, false); }
    else {
      if (t >= DUR) seek(0);
      playing = true; clipLive = true; vo.currentTime = t; vo.play().catch(() => {});
      playBtn.textContent = "Pause"; raf = requestAnimationFrame(tick);
    }
  });
  $("mute").addEventListener("click", () => { vo.muted = !vo.muted; $("mute").textContent = vo.muted ? "Unmute" : "Mute"; });
  scrub.addEventListener("input", () => { seek(+scrub.value); });
  sync();
  /* P51 T4: ?t=<seconds> opens the page AT that instant - the same scrub input every probe and
     every test seeks with, so a report can link the frame it is talking about. */
  if (typeof location !== "undefined") {
    const T0 = new URLSearchParams(location.search).get("t");
    if (T0 !== null && T0 !== "" && isFinite(+T0)) { scrub.value = +T0; scrub.dispatchEvent(new Event("input", { bubbles: true })); }
  }
  /* P47 T3: the morph's match-cut invariants on the active page (25 frames of the ARAP outline), for measure_morph.py / M17 */
  /* P49 T3: what the eye sees at t - the camera's state, its frustum in world (pre-camera) stage px, and for a declared
     target whether it is in frame, how much of it, at what on-screen scale, and where it lands on screen. Seek to t
     first (a datum resolves against the painted page). */
  window.__camArr = () => camArr && { u: camArr.u, slide: camArr.slide, box: camArr.box, state: camArr.state };   /* P49 T5: the arrival this frame, for the probes */
  window.__lpDatum = (k, si, i) => { const w = [wA, wB].find((e) => e.__lp && e.classList.contains("ledger")); if (!w) return null; const st = w.__lp; return k == null ? lpDatumNow(st, si, i) : lpMarkDatumOn((st.states || [st])[k], si, i); };   /* R26-28: a datum on state k, or this frame's (lerped) position */
  window.__camera = (t, tg) => {
    let si = 0; for (let i = 0; i < TL.scenes.length; i++) if (t >= TL.scenes[i].span[0]) si = i;
    const sc = TL.scenes[si], xf = camArr ? camArr.state : camNow(sc, t);   /* P49 T5: an arrival in progress is the camera this frame */
    const st = { s: xf.s, look: [xf.ox, xf.oy], at: [xf.ax != null ? xf.ax : xf.ox, xf.ay != null ? xf.ay : xf.oy] };
    const fr = camFrustum(st, STAGE_W, STAGE_H);
    let target = null;
    if (tg) { const b = resolveTarget(tg); if (b) target = Object.assign(camInFrame(fr, b, st.s), { box: b, screen: camProject(st, [b.x, b.y]) }); }
    return { scene: sc.scene_id, on: kin("camera"), zoom: st.s, look: st.look, at: st.at, frustum: fr, target };
  };
  window.__morphInvariants = (key) => {   /* no key: the page-enter morph; "from>to": a morph_to between two states (P48 T5) */
    const world = [wA, wB].find((e) => e.__lp && e.classList.contains("ledger")); if (!world) return null;
    const M = key == null ? world.__lp.morph : (world.__lp.morphTo || {})[key]; if (!M) return null;
    const frames = [];
    for (let i = 0; i <= 24; i++) frames.push(i === 24 ? M.B : lpMorphRing(M, i / 24));
    const inv = morphInvariants(frames, M.W), last = frames[24];
    const endErr = Math.max(...last.map((p, i) => Math.hypot(p[0] - M.B[i][0], p[1] - M.B[i][1])));
    /* the det leg: METHOD B guarantees it positive per triangle, METHOD A has no such guarantee - so for A it is
       measured on the strip's own triangles (morphAMinDet), which is exactly where a vertex lerp would fold. */
    let worst = Infinity;
    for (let i = 0; i <= 24; i++) {
      if (M.method === "a") worst = Math.min(worst, morphAMinDet(M.mesh.verts, morphAAt(M.aPrep, i / 24).outline, M.mesh.tris));
      else { const d = minDet(M.prep, i / 24); worst = Math.min(worst, d.target, d.solved); }
    }
    return { ...inv, end_error: endErr, min_det: worst, n: M.A.length, u: M.u, method: M.method || "arap", morph_a_offset: M.aPrep ? M.aPrep.offset : null };
  };
}

  /* ---- FILMSTRIP MODE (doc 29 s9.16) - true PLAYED frames -----------
     __filmstrip(t0, dur, n, name): for each sample, PLAYS INTO the
     moment (state derives from the live RAF loop), pauses, rasterizes
     a cleaned stage clone (hidden scenes stripped - a raw outerHTML of
     the full stage is ~100MB of data URIs and OOMs the tab), and
     assembles one labeled strip PNG POSTed to :8732. */
  /* P47 T2 test probe (read-only): the active ledger page's drawn state, in the chart's own units */
  window.__lpProbe = () => {
    const world = [wA, wB].find((e) => e.__lp && e.classList.contains("ledger")); if (!world) return null;
    const st = world.__lp, PF = st.perform || { brackets: [], retitles: [], figures: [], spreads: [] };
    const paths = st.paths.map((pp) => { const off = parseFloat(pp.p.getAttribute("stroke-dashoffset") || "0"), drawn = pp.len - off;
      const q = pp.p.getPointAtLength ? pp.p.getPointAtLength(Math.max(0, Math.min(pp.len, drawn))) : { x: 0, y: 0 };
      return { si: pp.si | 0, k0: pp.k0 | 0, muted: !!pp.muted, len: pp.len, drawn, frac: pp.len ? drawn / pp.len : 1, tip: [q.x, q.y], pts: pp.pts || [], hidden: pp.p.style.opacity === "0" }; });
    const brackets = PF.brackets.map((b) => { const bb = b.main.g.getBBox(); return { x: b.x, y0: b.y0, y1: b.y1, A: b.A, B: b.B, fits: b.fits,
      opacity: parseFloat(b.main.g.getAttribute("opacity") || "0"), glow: parseFloat(b.glow.g.getAttribute("opacity") || "0"),
      offset: parseFloat(b.main.line.getAttribute("stroke-dashoffset") || "0"), len: b.main.len,
      label: b.main.lg.map((ts) => parseFloat(ts.getAttribute("opacity") || "0")), bbox: [bb.x, bb.y, bb.width, bb.height] }; });
    const w = (gs) => gs.map((g) => parseFloat(g.style.getPropertyValue("--w") || "0"));
    const M = st.morph; const mb = M ? M.path.getBBox() : null;
    const spreads = (PF.spreads || []).map((sd) => ({ alpha: parseFloat(sd.path.getAttribute("fill-opacity") || "0"), d: (sd.path.getAttribute("d") || "").length, pts: sd.hi.length }));
    const figures = (PF.figures || []).map((fg) => ({ D: fg.D, x: fg.x, fits: fg.fits, opacity: parseFloat(fg.g.getAttribute("opacity") || "0"),
      label: fg.lg.map((ts) => parseFloat(ts.getAttribute("opacity") || "0")) }));
    const marks = (st.marks || []).map((m) => ({ key: m.key, role: m.role, geom: m.geom }));   /* P48 T1: the keyed model, for the transition tests */
    return { marks, linePts: st.linePts, paths, brackets, figures, spreads, title: w(st.titleGlyphs || []), retitles: PF.retitles.map((r) => w(r.glyphs)),
             morph: M ? { u: M.u, bbox: [mb.x, mb.y, mb.width, mb.height], fill: parseFloat(M.path.getAttribute("fill-opacity")), on: M.svg.style.opacity } : null };
  };
  window.__filmstrip = async (t0, dur, n, name) => {
    const g = (id) => document.getElementById(id);
    const stage = g("stage"), vo = g("vo"), scrub = g("scrub"),
          playBtn = g("play");
    const seekTo = (t) => { scrub.value = t;
      scrub.dispatchEvent(new Event("input", { bubbles: true })); };
    const playing = () => playBtn.textContent.includes("Pause");
    const setPlay = (on) => { if (playing() !== on) playBtn.click(); };
    const css = [...document.querySelectorAll("style")]
      .map(x => x.textContent).join(String.fromCharCode(10));
    const FW = 480, FH = Math.round(FW * 9 / 16), PAD = 22;
    const cv = document.createElement("canvas");
    cv.width = FW * n; cv.height = FH + PAD;
    const cx = cv.getContext("2d");
    cx.fillStyle = "#0d0f12"; cx.fillRect(0, 0, cv.width, cv.height);
    for (let i = 0; i < n; i++) {
      const tt = t0 + (i + 0.5) * (dur / n);
      /* visibility-proof: RAF suspends in hidden panes and a MUTED
         audio clock freezes - poll on a timer at whisper volume */
      vo.muted = false; vo.volume = 0.01;
      seekTo(Math.max(0, tt - 0.35));
      setPlay(true);
      await new Promise((res, rej) => {
        const t1 = Date.now();
        const iv = setInterval(() => {
          if (vo.currentTime >= tt) { clearInterval(iv); res(); }
          else if (Date.now() - t1 > 15000) {
            clearInterval(iv); rej(new Error("stall at " + tt)); }
        }, 40);
      });
      setPlay(false);
      seekTo(vo.currentTime);
      const at = vo.currentTime;
      const cl = stage.cloneNode(true);
      cl.querySelectorAll("img").forEach(im => {
        let e = im, vis = true;
        while (e && e !== cl) {
          const st = e.style;
          if (st && (st.opacity === "0" || st.display === "none"))
            vis = false;
          e = e.parentElement;
        }
        const r = im.getBoundingClientRect ? null : null;
        if (!vis) im.removeAttribute("src");
      });
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${STAGE_W}" height="${STAGE_H}">` +
        `<foreignObject width="${STAGE_W}" height="${STAGE_H}">` +
        `<div xmlns="http://www.w3.org/1999/xhtml">` +
        `<style>${css.replace(/]]>/g, "")}</style>` +
        new XMLSerializer().serializeToString(cl) +
        `</div></foreignObject></svg>`;
      /* data: URL, not blob: - this Chromium taints canvases drawn
         from blob-loaded foreignObject SVGs, but not data:-loaded */
      const img = new Image();
      img.src = "data:image/svg+xml;charset=utf-8,"
              + encodeURIComponent(svg);
      await new Promise((res, rej) => {
        img.onload = res; img.onerror = rej; });
      cx.drawImage(img, i * FW, PAD, FW, FH);
      cx.fillStyle = "#dce3ea"; cx.font = "600 13px Consolas, monospace";
      cx.fillText(at.toFixed(2) + "s", i * FW + 8, 15);
      cx.strokeStyle = "#33363d";
      cx.strokeRect(i * FW + 0.5, PAD + 0.5, FW - 1, FH - 1);
    }
    const png = cv.toDataURL("image/png");
    await fetch("http://127.0.0.1:8732/", { method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name, png }) });
    return name + ": " + n + " played frames";
  };

/* P51 T4 - RELOAD: a new timeline on a page that is already open. The shell's own DOM comes back
   (which is what kills every node and every listener the last mount made), the new timeline goes
   into the slot the loader reads, and mount() runs the same path it runs after a fetch. The assets
   are not read again, the scrub position is kept, and the page is left seeking at it - so what is
   on screen after a reload is what a cold load at that t paints. The snapshot only exists on a
   watched page (?watch=1), which is what makes this cost a served build nothing. */
async function reload(timeline) {
  if (__shellHTML === null)
    throw new Error("reload: this page was not opened with ?watch=1, so no shell snapshot was taken");
  const before = document.getElementById("scrub");
  const at = before ? +before.value : 0;
  window.__mounted = false;
  document.body.innerHTML = __shellHTML;
  document.getElementById("timeline-data").textContent = JSON.stringify(timeline);
  await mount();
  const scrub = document.getElementById("scrub");
  if (scrub) { scrub.value = at; scrub.dispatchEvent(new Event("input", { bubbles: true })); }
  window.__mounted = true;
  window.__reloads = (window.__reloads || 0) + 1;
  return at;
}

export { mount, reload };
