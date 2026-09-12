/* SPACE: stage */
/* species/melt.mjs - THE MELT EXIT (P52 T9; BACKLOG R26-15, the HyperFrames harvest's morph-text row; the operator,
   2026-09-07: "it would be cool to be able to melt the chart, turn it into a stop motion ink ball, then splash it
   everywhere or toss it off the page"). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py
   between KINETICS:BEGIN melt and KINETICS:END, AFTER ink, stopaction, arap and morph_a - it imports all four, and
   the import order IS the region order.

   It registers NO painter: a melt is not a species kind (nothing targets it), it is an EXIT law the engine's scene
   loop calls by name where it handles the suck. `exit` names the transition INTO the scene it sits on (the player's
   law), so `s05.exit = "melt"` melts s04's world as s05 begins; the incoming world is untouched beneath throughout.

   FOUR PHASES over the exit's window u = clamp01((t - t_boundary) / secs), the shares fixed dials that sum to 1:
     melt   u 0    - 0.30   the world's area polygon SAGS: its bottom edge grows N seeded drips, and the silhouette
                            runs through the GOOEY THRESHOLD (a Gaussian blur re-steepened by a linear alpha ramp -
                            HyperFrames' morph-text trick, which is our own K-M chain's `feFuncA slope` (ink.mjs
                            kmFilterMarkup) pointed at a silhouette instead of at summed stain coverage), so two
                            drips that touch FUSE into one liquid body instead of crossing as two edges.
     ball   u 0.30 - 0.55   that dripped outline MORPHS to a circle of BALL_R about its own centroid (morph_a, the
                            vertex method) on the STEPPED clock (stopaction `stepped`, hold 2 - on 2s), the blur
                            falling to 0 so the blob lands as a solid ink ball. The world's pixels ride inside it.
     throw  u 0.55 - 1      the ball is THROWN off the stage: stopaction's `throwXf` on the ink material, its
       or splash            ballistic chord run BACKWARDS (a landing played in reverse IS a launch: the chord is
                            constant-speed, the arc symmetric, and the tumble that unwinds into a landing winds up
                            out of a rest) - or, with `melt:splash`, the ball FLATTENS on the same stepped clock and
                            soakStepped (ink.mjs's seeded staircase of bursts) drives a ring of droplets outward,
                            each an ink drop by kmHex, fading to nothing at u = 1.
     gone   u >= 1          the outgoing world is hidden, exactly as the suck ends.

   Everything above the painter is a pure function of (t0, t, the rect, the dials, rnd): the same t twice is the same
   object, so a scrubbed frame is the played frame and a cold render is the warm one. `rnd(k)` is the caller's seeded
   hash in [0, 1) - the engine passes lpHash bound to the scene, never Math.random.

   The AUTHORED FORM: `melt` | `melt:<s>` | `melt:splash` | `melt:<x>,<y>` (the exit point in STAGE fractions, the
   mirror of the suck's declared point) in any order after the name: `melt:1.2:splash`. build_scene_timeline_f.py's
   parse_exit reads the same grammar and refuses anything else, naming the row.
   Every number here is a starting dial (doc 42 s42.5); HG2 tunes them by eye on the four proof frames. */
import { kmHex, soakStepped } from "../kinetics/ink.mjs";
import { CADENCE, stepped, throwXf } from "../kinetics/stopaction.mjs";
import { centroid } from "../kinetics/arap.mjs";
import { morphAPrepare, morphAAt, morphAPath } from "../kinetics/morph_a.mjs";

export const MELT = Object.freeze({
  S: 1.6,            /* the exit's default length [DERIVED: the suck's 0.3 s is one phase of collapse; a melt is three
                        (the sag, the ball, the flight) plus a throw's FLIGHT_S 0.45 - 3 x 0.38 + 0.45 ~ 1.6] */
  MELT_END: 0.30,    /* the phase shares as CUTS of u: melt [0, 0.30), ball [0.30, 0.55), throw|splash [0.55, 1] */
  BALL_END: 0.55,    /* [DERIVED: the sag has to be read as a sag before it balls, and the flight is the longest
                        phase because it is the one that carries the eye off the page] */
  /* THE SAG */
  DRIPS: 7,          /* how many drips the bottom edge grows [DERIVED: at 1745 px of page width, one drip per ~250 px
                        reads as a run of drips rather than as a scallop] */
  SAG: 0.40,         /* the deepest drip's reach, as a share of the rect's height */
  TOP_SAG: 0.42,     /* how far the TOP edge sinks by the end of the sag, as a share of the height. A melting body
                        loses height - its mass goes downward - and on a page that fills the stage this is the half
                        of the melt the viewer can actually SEE: the drips below its foot hang off the frame. It
                        sinks FURTHEST above a drip, because that is where the mass went. */
  BASE_SAG: 0.10,    /* the whole bottom edge slumps this much besides (a share of the height): a melting thing loses
                        its edge everywhere, not only under the drips */
  DRIP_W: 0.11,      /* a drip's half-width as a share of the rect's width */
  DRIP_JIT: 0.55,    /* how far a drip's centre wanders from its even place, as a share of the even spacing */
  DRIP_DELAY: 0.40,  /* the last drip starts this far into the melt phase: the drips open in a seeded order */
  N: 33,             /* samples across the bottom edge (odd, so a drip can sit on the centre) */
  TOP_N: 13,         /* samples across the TOP edge, and SIDE_N down each side. The ring is drawn as a closed
                        centripetal Catmull-Rom (morphAPath), which INTERPOLATES its knots but bulges between two that
                        sit far apart next to two that do not: sampled at two corners only, the top edge of a 1745 px
                        page arched 220 px ABOVE the page. Even-ish spacing all the way round is the cure, and the
                        bottom stays the densest because it is the edge that has to read as liquid. */
  SIDE_N: 7,
  /* THE GOOEY THRESHOLD */
  BLUR: 26,          /* the silhouette's blur at the melt's peak, px at 1920 [DERIVED: the fuse gap - two drips
                        within ~2 sigma of each other join; tuned on the proof frames] */
  EDGE_SLOPE: 24,    /* the alpha ramp that re-steepens the blur into a liquid EDGE. INK.ALPHA_SLOPE (8) is the
                        stain's ramp - a stain wants a gradient at its front; a melting body wants a wet edge, so
                        this is three of them [DERIVED: measured on the proof frames] */
  /* THE BALL */
  BALL_R: 0.15,      /* the ball's radius as a share of the rect's height */
  CIRCLE_N: 96,      /* vertices on the circle. It is RING_N so the morph's arc-length resample lands ON them and
                        the ball's radius is exactly BALL_R at the end - a coarser circle resamples onto its CHORDS
                        and the ball ends a fraction of a percent small */
  RING_N: 96,        /* the morph's resample count (MORPH_A.N) */
  HOLD: 2,           /* the stepped clock's hold: on 2s (stop-action, doc 42) */
  FPS: CADENCE.FPS,  /* the frame rate the hold is counted in */
  /* THE THROW */
  TO: [1.16, 1.22],  /* the default exit point in STAGE fractions: off the lower right corner */
  MASS: "ink",       /* the material the flight and its tumble are read in (stopaction MASS) */
  /* THE SPLASH */
  DROPS: 14,         /* droplets in the ring */
  SPLASH_R: 0.85,    /* the ring's reach as a share of the rect's height */
  SPLASH_SPREAD: 0.30,   /* the angular jitter (radians) on each droplet's ray */
  SPLASH_FALL: 0.22,     /* how far gravity pulls a droplet below its ray by the end (a share of the height) */
  DROP_R: 0.045,     /* a droplet's radius as a share of the rect's height */
  DROP_SX: 0.20,     /* a droplet's optical thickness through the K-M model - INK.S1 (0.03) is ONE stain, so a drop
                        is ~7 of them: measured, kmHex(cream, charcoal, 0.20) = #253240, the ink itself rather than
                        the grey wash one stain gives (#7a9a99) - which is what a DROP is, thick enough to hide paper */
  FADE_FROM: 0.55,   /* the splash holds its ink for this much of its own clock and only then fades out. Ink does not
                        thin as it flies; it has to be GONE by the end (the next scene owns the frame), so the fade is
                        the last of the phase, not all of it - faded from the first frame it read as grey, not ink. */
  FLAT: 0.55,        /* how far the ball flattens as it bursts (1 - FLAT of its height) */
  PAPER: "#F4E6C7",  /* the cream ground and the charcoal the droplets are mixed over (E22; the page's own two) */
  INK_HEX: "#25313C",
});

const mc01 = (v) => (v <= 0 ? 0 : v >= 1 ? 1 : v);   /* the engine inlines every module into ONE scope, so a
   private helper carries the module's own prefix - `c01` is ink.mjs's */
/* the melt's own two easings: a SLUMP accelerates (it is gravity), everything else is smooth at both ends */
const mSlump = (u) => { const k = mc01(u); return k * k; };
const mEase = (u) => { const k = mc01(u); return k * k * (3 - 2 * k); };

/* ---- the authored form ------------------------------------------------------------------------------------------ */
/* `melt` | `melt:<s>` | `melt:splash` | `melt:<x>,<y>`, in any order after the name. Throws on anything else, so a
   typo in a shot table is a refusal and not a silent default. The engine's own exitSecs cannot read this: it takes
   the first suffix as a number, and `melt:0.92,1.18` would be 0.92 SECONDS of melt to a point nobody declared. */
export const meltOpts = (exit, o = {}) => {
  const P = Object.assign({}, MELT, o), bits = String(exit == null ? "" : exit).split(":");
  const out = { name: bits[0] || "", secs: P.S, splash: false, to: [P.TO[0], P.TO[1]] };
  for (let i = 1; i < bits.length; i++) {
    const b = bits[i].trim();
    if (b === "") continue;
    if (b === "splash") { out.splash = true; continue; }
    if (b.indexOf(",") >= 0) {
      const xy = b.split(",").map(Number);
      if (xy.length !== 2 || !xy.every((v) => Number.isFinite(v))) throw new Error("melt: " + b + " is not an x,y point in stage fractions");
      out.to = xy; continue;
    }
    const v = Number(b);
    if (!(Number.isFinite(v) && v > 0)) throw new Error("melt: " + b + " is neither a length in seconds, nor splash, nor an x,y point");
    out.secs = v;
  }
  return out;
};

/* ---- the phases ------------------------------------------------------------------------------------------------- */
/* the three shares, as shares of the window - they sum to 1 by construction */
export const meltShares = (o = {}) => {
  const P = Object.assign({}, MELT, o);
  return [P.MELT_END, P.BALL_END - P.MELT_END, 1 - P.BALL_END];
};
/* which phase u is in, and how far through THAT phase it is */
export const meltPhase = (u, o = {}) => {
  const P = Object.assign({}, MELT, o), k = mc01(u);
  /* GONE takes the boundary itself: (t - t0) / secs cannot be trusted to reach exactly 1 in floating point (4.0 +
     1.6 - 4.0 is 1.5999999999999996), and a frame that lands on the end of a melt must be gone, not mid-flight. */
  if (u >= 1 - 1e-9) return { name: "gone", k: 1, from: 1, span: 0 };
  if (k < P.MELT_END) return { name: "melt", k: k / P.MELT_END, from: 0, span: P.MELT_END };
  if (k < P.BALL_END) return { name: "ball", k: (k - P.MELT_END) / (P.BALL_END - P.MELT_END), from: P.MELT_END, span: P.BALL_END - P.MELT_END };
  return { name: "fly", k: (k - P.BALL_END) / (1 - P.BALL_END), from: P.BALL_END, span: 1 - P.BALL_END };
};
/* the silhouette's blur in px: up over the melt, back to 0 by the end of the ball (a ball is solid, not a cloud) */
export const meltBlur = (u, o = {}) => {
  const P = Object.assign({}, MELT, o), ph = meltPhase(u, P);
  if (ph.name === "melt") return P.BLUR * mEase(ph.k);
  if (ph.name === "ball") return P.BLUR * (1 - mEase(ph.k));
  return 0;
};

/* ---- the sag ---------------------------------------------------------------------------------------------------- */
/* a drip's window: 1 at its centre, 0 at DRIP_W, cos^2 between - so drips that overlap ADD nothing (the deepest wins)
   and the gooey threshold, not the arithmetic, is what fuses them */
const dripBump = (dx, w) => { const k = mc01(Math.abs(dx) / Math.max(1e-6, w)); const c = Math.cos(k * Math.PI / 2); return c * c; };
/* the drips of a rect, as {c, amp, delay, w} - seeded once, read at every u */
export const meltDrips = (rect, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), n = Math.max(1, P.DRIPS | 0), step = rect.w / n, out = [];
  for (let i = 0; i < n; i++) {
    out.push({ c: rect.x + step * (i + 0.5) + P.DRIP_JIT * step * (rnd(i) - 0.5),
               amp: 0.45 + 0.55 * rnd(40 + i), delay: P.DRIP_DELAY * rnd(70 + i), w: P.DRIP_W * rect.w });
  }
  return out;
};
/* how deep the edge hangs below the rect's foot at x, at melt-phase progress k. Monotone in k by construction: every
   drip's own clock is monotone, and the edge takes the DEEPEST of them plus the whole edge's slump. */
export const meltDepth = (x, k, rect, drips, o = {}) => {
  const P = Object.assign({}, MELT, o), u = mc01(k);
  let deepest = 0;
  for (const d of drips) {
    const own = mSlump(mc01((u - d.delay) / Math.max(1e-6, 1 - d.delay)));
    deepest = Math.max(deepest, dripBump(x - d.c, d.w) * d.amp * own);
  }
  return rect.h * (P.SAG * deepest + P.BASE_SAG * mSlump(u));
};
/* where the TOP edge has sunk to at x, at melt-phase progress k: down by TOP_SAG of the height, deepest over a drip.
   Monotone in k for the same reason the foot is - every term is. */
export const meltTop = (x, k, rect, drips, o = {}) => {
  const P = Object.assign({}, MELT, o), u = mc01(k);
  let over = 0;
  for (const d of drips) over = Math.max(over, dripBump(x - d.c, d.w * 1.15) * d.amp);   /* a touch wider than the drip itself: the hollow above it is broader than its neck */
  return rect.y + rect.h * P.TOP_SAG * mSlump(u) * (0.55 + 0.45 * over);
};
/* THE MELTING OUTLINE: a closed ring walked clockwise from the top-left - the top edge, the right side, the foot
   sampled right to left with the drips hung from it, the left side back up. Passed to morphAPath for the path string
   the mask carries, and to morphAPrepare as the shape the ball comes from. */
export const meltOutline = (rect, k, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), n = Math.max(3, P.N | 0), drips = meltDrips(rect, rnd, P);
  const top = Math.max(2, P.TOP_N | 0), side = Math.max(1, P.SIDE_N | 0), foot = rect.y + rect.h, pts = [];
  for (let j = 0; j < top; j++) { const x = rect.x + rect.w * (j / (top - 1)); pts.push([x, meltTop(x, k, rect, drips, P)]); }
  const tR = meltTop(rect.x + rect.w, k, rect, drips, P), tL = meltTop(rect.x, k, rect, drips, P);
  for (let j = 1; j <= side; j++) pts.push([rect.x + rect.w, tR + (foot - tR) * (j / (side + 1))]);   /* down the right */
  for (let j = n - 1; j >= 0; j--) {                                                             /* the foot, right to left, dripping */
    const x = rect.x + rect.w * (j / (n - 1));
    pts.push([x, foot + meltDepth(x, k, rect, drips, P)]);
  }
  for (let j = side; j >= 1; j--) pts.push([rect.x, tL + (foot - tL) * (j / (side + 1))]);        /* up the left */
  return pts;
};

/* ---- the ball --------------------------------------------------------------------------------------------------- */
export const ballCircle = (c, r, n) => {
  const out = [];
  for (let i = 0; i < n; i++) { const a = 2 * Math.PI * (i / n); out.push([c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)]); }
  return out;
};
/* the dripped outline BECOMES a circle of BALL_R about its own centroid: morph_a's vertex method, exact at both ends.
   k is the ball phase's progress, already quantised to the stepped clock by meltState. */
export const ballAt = (rect, k, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), src = meltOutline(rect, 1, rnd, P);
  const c = centroid(src), r = P.BALL_R * rect.h;
  const prep = morphAPrepare(src, ballCircle(c, r, P.CIRCLE_N), { n: P.RING_N });
  return { outline: morphAAt(prep, mEase(k)).outline, centre: c, r, k: mc01(k) };
};
/* the ball FLATTENS as it bursts: what it loses in height it gains across, about its own centre */
export const ballFlat = (outline, c, k, o = {}) => {
  const P = Object.assign({}, MELT, o), f = 1 - P.FLAT * mEase(k), g = 1 + (1 / Math.max(0.05, f) - 1) * 0.5;
  return outline.map((p) => [c[0] + (p[0] - c[0]) * g, c[1] + (p[1] - c[1]) * f]);
};

/* ---- the splash ------------------------------------------------------------------------------------------------- */
/* a ring of DROPS droplets thrown outward on the soak's own STEPPED clock (ink.mjs soakStepped: a seeded staircase of
   bursts, never contracting), each falling a little as it goes and fading to nothing at k = 1. `d` is the distance
   travelled along the droplet's own ray - monotone in k, which is what the test pins. */
/* the ink's own fade: 1 until FADE_FROM of the burst's clock, then out to exactly 0 at the end */
export const splashFade = (p, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return 1 - mEase(mc01((mc01(p) - P.FADE_FROM) / Math.max(1e-6, 1 - P.FADE_FROM)));
};
export const splashDrops = (c, h, k, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), p = soakStepped(mc01(k), rnd), out = [];
  for (let i = 0; i < Math.max(0, P.DROPS | 0); i++) {
    const a = 2 * Math.PI * (i / P.DROPS) + P.SPLASH_SPREAD * (2 * rnd(300 + i) - 1);
    const reach = P.SPLASH_R * h * (0.55 + 0.9 * rnd(400 + i)), d = reach * p;
    out.push({ x: c[0] + Math.cos(a) * d, y: c[1] + Math.sin(a) * d + P.SPLASH_FALL * h * p * p,
               r: P.DROP_R * h * (0.6 + 0.8 * rnd(500 + i)) * (1 - 0.35 * p), d, a, alpha: splashFade(p, P) });
  }
  return out;
};

/* ---- the throw -------------------------------------------------------------------------------------------------- */
/* THE FLIGHT, BACKWARDS. stopaction's throwXf brings a thing FROM an offset TO its rest; a launch is that landing run
   in reverse - the chord is covered at constant speed, the arc's lift is symmetric about the middle, and the tumble
   that unwinds into a landing winds up out of a rest. So t' = F(1 - k): at k = 0 the ball sits at rest (0, 0) and at
   k = 1 it is at `from`, which is the declared exit point. The flight fills the phase exactly (FLIGHT_S = F), so the
   stepped cadence throwXf picks is the phase's own. */
export const meltThrowAt = (k, from, secs, o = {}) => {
  const P = Object.assign({}, MELT, o), F = Math.max(0.05, secs), kk = mc01(k);
  /* k = 0 is REST, said here rather than left to the reversal: t' = F is the instant throwXf has already landed, and
     a landing is a settle (a 4 px ground dip), not the pose of a ball that has not moved yet. */
  if (kk <= 0) return { x: 0, y: 0, rot: 0, alpha: 0, theta: Math.PI / 2, phase: "flight", u: 1, hold: 1, h: 0, ground: 0, shake: { x: 0, y: 0 } };
  return throwXf(from, P.MASS, F * (1 - kk), { FLIGHT_S: F });
};

/* ---- the frame -------------------------------------------------------------------------------------------------- */
/* EVERYTHING THE PAINTER NEEDS, in one object, from (t0, t, o, rnd) alone.
   o carries the geometry as well as any dial: `rect` (the melting box, in the outgoing world's own px), `stagebox`
   (the stage's box in those same px - what a declared x,y fraction is measured in), `secs`, `splash`, `to`. */
export const meltState = (t0, t, o = {}, rnd) => {
  const P = Object.assign({}, MELT, o), rect = P.rect, sb = P.stagebox || rect, to = P.to || P.TO;
  const secs = Math.max(0.05, +P.secs || P.S), u = mc01((t - t0) / secs), ph = meltPhase(u, P);
  const st = { u, secs, phase: ph.name, k: ph.k, blur: meltBlur(u, P), splash: !!P.splash,
               opacity: 1, outline: null, path: "", centre: null, r: 0, drops: [], xf: null, flat: 1, gone: false };
  if (ph.name === "gone") { st.gone = true; st.opacity = 0; return st; }
  if (ph.name === "melt") {
    st.outline = meltOutline(rect, ph.k, rnd, P);
    st.path = morphAPath(st.outline);
    return st;
  }
  /* the ball and the flight run on the STEPPED clock, each on its own phase-local seconds (a pure quantisation of t) */
  const tl = t - t0 - ph.from * secs, span = ph.span * secs;
  const kq = mc01(stepped(Math.max(0, tl), P.HOLD, P.FPS) / Math.max(1e-6, span));
  if (ph.name === "ball") {
    const b = ballAt(rect, kq, rnd, P);
    st.outline = b.outline; st.centre = b.centre; st.r = b.r; st.k = kq;
    st.path = morphAPath(st.outline);
    return st;
  }
  const b = ballAt(rect, 1, rnd, P);
  st.centre = b.centre; st.r = b.r; st.k = kq;
  if (st.splash) {
    st.flat = 1 - P.FLAT * mEase(kq);
    st.outline = ballFlat(b.outline, b.centre, kq, P);
    st.drops = splashDrops(b.centre, rect.h, kq, rnd, P);
    st.opacity = splashFade(kq, P);
  } else {
    st.outline = b.outline;
    st.xf = meltThrowAt(kq, { x: sb.x + to[0] * sb.w - b.centre[0], y: sb.y + to[1] * sb.h - b.centre[1] }, span, P);
  }
  st.path = morphAPath(st.outline);
  return st;
};

/* ---- the markup the painter mounts once ------------------------------------------------------------------------- */
/* THE GOOEY THRESHOLD as SVG primitives: blur the silhouette, then re-steepen its alpha. Two drips whose blurs
   overlap cross the ramp together and come out as ONE body with a concave neck - HyperFrames' morph-text trick,
   which is ink.mjs's kmFilterMarkup `feFuncA slope` applied to a shape instead of to summed coverage. The COLOUR
   stages of the K-M chain are deliberately not here: they take alpha into the colour channels, which would flatten
   the melting world to an ink silhouette and throw away the chart the viewer is watching melt. The droplets, which
   ARE ink and carry no picture, take the K-M model instead - through kmHex, per drop. */
export const meltFilterMarkup = (id, u, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<filter id="' + id + '" x="-40%" y="-40%" width="180%" height="180%" color-interpolation-filters="sRGB">'
    + '<feGaussianBlur stdDeviation="' + meltBlur(u, P).toFixed(2) + '"/>'
    + '<feComponentTransfer><feFuncA type="linear" slope="' + P.EDGE_SLOPE + '" intercept="0"/></feComponentTransfer>'
    + '</filter>';
};
/* the mask the outgoing world wears: one path, filtered. The mask's region is opened well past the element's own box
   so neither the blur nor a drip is clipped by it. */
export const meltMaskMarkup = (id, filterId) =>
  '<mask id="' + id + '" maskUnits="objectBoundingBox" x="-0.4" y="-0.4" width="1.8" height="1.8">'
  + '<g filter="url(#' + filterId + ')"><path fill="#fff" d=""/></g></mask>';

/* ---- the painter ------------------------------------------------------------------------------------------------ */
/* THE MELTING BOX in the outgoing world's own pixels: a ledger world melts its PAGE (the card box `.lp-page`, whose
   LAYOUT box is where the page stands whatever transform it carries - the same reading the camera arrival takes);
   any other world melts the stage. `.world` overhangs the stage by 5% on every side, so the stage sits at 1/22 of
   the world's box and takes 10/11 of it. */
export const meltStageBox = (wA) => ({ x: wA.offsetWidth / 22, y: wA.offsetHeight / 22,
                                       w: wA.offsetWidth * 10 / 11, h: wA.offsetHeight * 10 / 11 });
export const meltRect = (wA) => {
  const page = wA.querySelector(".lp-page");
  if (page && page.offsetWidth > 0 && page.offsetHeight > 0) {
    const host = page.offsetParent && page.offsetParent !== wA ? page.offsetParent : null;
    return { x: page.offsetLeft + (host ? host.offsetLeft : 0), y: page.offsetTop + (host ? host.offsetTop : 0),
             w: page.offsetWidth, h: page.offsetHeight };
  }
  return meltStageBox(wA);
};

/* the overlay, mounted ONCE and kept on wA.__melt: an svg SIBLING of the outgoing world (never a child - a child
   would wear the mask its own defs define, and the droplets would be cut to the ball), holding the filter, the mask
   and the droplet group. Nothing here reads time. */
const meltMount = (wA, el, id) => {
  const svg = el("svg", "meltov", wA.parentNode, { "pointer-events": "none" });
  const defs = el("defs", "", svg, {});
  defs.innerHTML = meltFilterMarkup(id + "f", 0) + meltMaskMarkup(id + "m", id + "f");
  const m = { id, svg, defs, blur: defs.querySelector("feGaussianBlur"), path: defs.querySelector("mask path"),
              drops: el("g", "meltdrops", svg, {}), dots: [] };
  svg.style.position = "absolute"; svg.style.overflow = "visible"; svg.style.pointerEvents = "none"; svg.style.zIndex = "4";
  wA.__melt = m;
  return m;
};

/* PAINT ONE FRAME. ctx: { wA, t, t0, opts, rnd, el, id }. The state is meltState's; this only writes it down - the
   mask's path and blur, the world's mask / transform / opacity, and the droplets. */
export const paintMelt = (ctx) => {
  const { wA, el, rnd } = ctx, id = ctx.id || "melt";
  const m = (wA.__melt && wA.__melt.svg && wA.__melt.svg.isConnected) ? wA.__melt : meltMount(wA, el, id);
  const st = meltState(ctx.t0, ctx.t, ctx.opts, rnd);
  m.svg.style.left = wA.offsetLeft + "px"; m.svg.style.top = wA.offsetTop + "px";
  m.svg.style.width = wA.offsetWidth + "px"; m.svg.style.height = wA.offsetHeight + "px";
  m.svg.setAttribute("viewBox", "0 0 " + wA.offsetWidth + " " + wA.offsetHeight);
  m.blur.setAttribute("stdDeviation", st.blur.toFixed(2));
  m.path.setAttribute("d", st.path);
  wA.style.mask = "url(#" + id + "m)"; wA.style.webkitMaskImage = "url(#" + id + "m)";
  wA.style.zIndex = 3;                          /* the outgoing world rides above the incoming plate, as the suck's does */
  wA.style.opacity = st.gone ? "0" : st.opacity.toFixed(4);
  m.svg.style.opacity = st.gone ? "0" : "1";
  if (st.xf) {   /* the flight: the whole world travels, mask and all, about the ball's own centre */
    wA.style.transformOrigin = st.centre[0].toFixed(1) + "px " + st.centre[1].toFixed(1) + "px";
    wA.style.transform = "translate(" + st.xf.x.toFixed(2) + "px," + st.xf.y.toFixed(2) + "px) rotate("
      + st.xf.rot.toFixed(2) + "deg) " + wA.style.transform;
  }
  /* the droplets: one circle per drop, created once and moved after that (ink by the K-M model, over the cream) */
  while (m.dots.length < st.drops.length) m.dots.push(el("circle", "", m.drops, { fill: kmHex(MELT.PAPER, MELT.INK_HEX, MELT.DROP_SX) }));
  m.dots.forEach((dot, i) => {
    const d = st.drops[i];
    if (!d || d.r <= 0.2 || d.alpha <= 0.002) { dot.setAttribute("r", "0"); dot.setAttribute("opacity", "0"); return; }
    dot.setAttribute("cx", d.x.toFixed(1)); dot.setAttribute("cy", d.y.toFixed(1));
    dot.setAttribute("r", d.r.toFixed(1)); dot.setAttribute("opacity", d.alpha.toFixed(3));
  });
  return st;
};

/* the reset, called on every frame that is NOT a melt - the same shape as the suck's, and it touches only what the
   painter set (a world that never melted is never written to). */
export const clearMelt = (wA) => {
  if (!wA.__melt) return;
  const m = wA.__melt;
  if (m.svg && m.svg.parentNode) m.svg.parentNode.removeChild(m.svg);
  wA.__melt = null;
  wA.style.mask = ""; wA.style.webkitMaskImage = "";
  if (wA.style.zIndex) wA.style.zIndex = "";
  if (wA.style.opacity !== "") wA.style.opacity = "";
  if (wA.style.transformOrigin) wA.style.transformOrigin = "";
};
