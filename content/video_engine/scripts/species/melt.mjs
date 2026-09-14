/* SPACE: stage */
/* species/melt.mjs - THE MELT EXIT (P52 T9; BACKLOG R26-15, reworked to E88 by R26-76). SOURCE OF TRUTH, inlined into
   the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN melt and KINETICS:END, AFTER ink, squash,
   stopaction, arap and morph_a - it imports all five, and the import order IS the region order.

   E88 (the operator, 2026-09-13): "i envisioned melting only the chart information on the page, and compiling that into
   a dense heavy ball akin to the reference, and then either throwing it off of the screen, and drawing a new chart or
   splattering that back onto the page to either form a new chart or a narrative plate springs up, reading as having been
   \"painted\" - i didn't imagine melting the whole charcoal board". P52 T9 melted the WORLD's area polygon, so the board
   left with the chart. Now THE CHART'S INK melts and the BOARD STAYS:
     the INK   a clone of the outgoing world with its board hidden (`.meltink`: the page's cream, grain, roll edge, field
               and field plate invisible) - the title, the series, the bars, the marks, the labels, the rail. It wears
               the melt's mask, its pixel filter and its squeeze.
     the BOARD the outgoing world itself with its ink hidden (`.meltboard`) - the cream ground, the deckle, the charcoal.
               It never moves; under a splash it wears the REVEAL mask the painting grows through.

   It registers NO painter: a melt is not a species kind, it is an EXIT law the engine's scene loop calls by name where
   it handles the suck. `exit` names the transition INTO the scene it sits on (E47), so `s05.exit = "melt"` melts s04's
   chart as s05 begins.

   FOUR PHASES over the exit's window u = clamp01((t - t_boundary) / secs), the shares fixed dials that sum to 1:
     melt   u 0    - 0.30   the ink SAGS and RUNS: its own pixels smear downward (RUN_COPIES offset copies merged) under
                            the GOOEY THRESHOLD (a Gaussian blur re-steepened by a linear alpha ramp - HyperFrames'
                            morph-text trick, our K-M chain's `feFuncA slope`), so neighbouring marks FUSE into one liquid
                            body; the ink box's outline sags over seeded drips as its mask.
     ball   u 0.30 - 0.55   the ink SQUEEZES toward its centroid while the outline MORPHS to a circle of BALL_R (morph_a,
                            the vertex method) on the STEPPED clock (stopaction `stepped`, hold 2 - on 2s), and a DENSE
                            ink body - the marks' own colours mixed by Kubelka-Munk and concentrated DENSITY times - comes
                            up opaque over it: the chart compiles into a heavy ball.
     end    u 0.55 - 1      one of three AUTHORED endings:
       throw          the ball lands in its own weight (stopaction impactSquash on MASS, SQUASH, on 2s) for ANTIC of the
                      phase, then is THROWN off the stage (throwXf run backwards: a landing played in reverse IS a launch),
                      a low arc and little tumble because it is heavy. The board is up until the launch; the next scene's
                      chart then draws on the same board (the engine delays that page's clock by meltDrawDelay).
       splash:chart   the ball SLAMS onto the board (the same squash), flattens, and bursts into droplets that LAND on the
                      board (soakStepped's staircase); the landed drops then grow as seeded stains through the board's
                      REVEAL mask with a wet ink rim, and the next page's chart - already built beneath - is what shows
                      through them: the chart arrives out of the splatter, not by its build.
       splash:plate   the same splatter, and what grows through the stains is the next scene's NARRATIVE PLATE, springing
                      up (a small scale settle) as if painted by that ink; the board is painted over from the drops out.
     gone   u >= 1          the outgoing world, its ink and the overlay are hidden, exactly as the suck ends.

   Everything above the painter is a pure function of (t0, t, the rect, the dials, rnd): the same t twice is the same
   object, so a scrubbed frame is the played frame and a cold render is the warm one. `rnd(k)` is the caller's seeded
   hash in [0, 1) - the engine passes lpHash bound to the scene, never Math.random.

   The AUTHORED FORM: `melt` | `melt:throw` | `melt:splash:chart` | `melt:splash:plate`, with `:<s>` (the length) and, on a
   throw only, `:<x>,<y>` (the exit point in STAGE fractions), in any order after the name. A bare `melt:splash` is
   REFUSED: since E88 a splash has two endings that need two different incoming worlds (a chart page, a plate), and an
   alias would pick one silently. build_scene_timeline_f.py's parse_exit reads the same grammar and refuses anything
   else, naming the row. Every number here is a starting dial (doc 42 s42.5); HG2 tunes them by eye on the proof frames. */
import { hexToLin, linToHex, ksFromR, soakStepped } from "../kinetics/ink.mjs";
import { squashMatrix } from "../kinetics/squash.mjs";
import { CADENCE, stepped, throwXf, impactSquash } from "../kinetics/stopaction.mjs";
import { centroid } from "../kinetics/arap.mjs";
import { morphAPrepare, morphAAt, morphAPath } from "../kinetics/morph_a.mjs";

export const MELT = Object.freeze({
  S: 1.6,            /* the exit's default length [DERIVED: the suck's 0.3 s is one phase of collapse; a melt is three
                        (the sag, the ball, the ending) plus a throw's FLIGHT_S 0.45 - 3 x 0.38 + 0.45 ~ 1.6] */
  MELT_END: 0.30,    /* the phase shares as CUTS of u: melt [0, 0.30), ball [0.30, 0.55), ending [0.55, 1] */
  BALL_END: 0.55,
  /* THE SAG (the ink box's outline, the mask the melting ink wears) */
  DRIPS: 7,          /* how many drips the box's foot grows */
  SAG: 0.40,         /* the deepest drip's reach, as a share of the box's height */
  TOP_SAG: 0.42,     /* how far the TOP edge sinks by the end of the sag: a melting body loses height, its mass goes down */
  BASE_SAG: 0.10,    /* the whole foot slumps this much besides */
  DRIP_W: 0.11,      /* a drip's half-width as a share of the box's width */
  DRIP_JIT: 0.55,    /* how far a drip's centre wanders from its even place, as a share of the even spacing */
  DRIP_DELAY: 0.40,  /* the last drip starts this far into the melt phase: the drips open in a seeded order */
  N: 33, TOP_N: 13, SIDE_N: 7,   /* the ring's samples: foot, top, each side (even-ish spacing - see meltOutline) */
  /* THE GOOEY THRESHOLD */
  BLUR: 26,          /* the outline's blur at the melt's peak, px at 1920 */
  EDGE_SLOPE: 24,    /* the alpha ramp that re-steepens the outline's blur into a liquid edge */
  /* THE RUN (E88: the MARKS melt, not a rectangle) - the ink's own pixels, smeared down and fused */
  RUN: 0.22,         /* how far the ink runs at the sag's end, as a share of the ink box's height [DERIVED, HG2] */
  RUN_COPIES: 6,     /* offset copies merged into the run: enough that the gooey blur joins them into one trail (3 read as
                        stacked parallel copies of each line on the proof frames) */
  INK_BLUR: 4,       /* the marks' own blur at the melt's peak, px - a 3 px line blurred to 7 px and ramped by INK_SLOPE
                        comes back ~2.5x as thick, which is the swell of a wet line [DERIVED, HG2] */
  BALL_FUSE: 40,     /* the squeezed ink's extra blur through the ball phase, in the ink's OWN px (the squeeze shrinks it ~10x
                        on screen): without it the compacting chart read as stacked orange hatching, not one mass */
  INK_SLOPE: 9,      /* the marks' alpha ramp (the outline's EDGE_SLOPE is 24: a mark is thinner than a body) */
  /* THE BALL - dense and heavy (E88): smaller than P52 T9's 0.15, opaque, darker than its own marks */
  BALL_R: 0.085,     /* the ball's radius as a share of the ink box's height [was 0.15 of the whole PAGE's height] */
  CIRCLE_N: 96,      /* vertices on the circle = RING_N, so the morph's resample lands ON them (radius exact at the end) */
  RING_N: 96,
  HOLD: 2,           /* the stepped clock's hold: on 2s (stop-action, doc 42) */
  FPS: CADENCE.FPS,
  SQUEEZE: 1.15,     /* the ink box is squeezed until its longer side is SQUEEZE ball-diameters: the chart compiles INTO the
                        ball instead of being cropped by it */
  BODY_FROM: 0,      /* the ball is a CRISP opaque disc from the first frame of its phase (a ramp over the whole box read as
                        a jelly slab; one that waited for the squeeze read as a soft chart silhouette at 045 - the parent's
                        two reads, 2026-09-13) ... */
  BODY_TO: 0.15,     /* ... fully opaque from here */
  BODY_GROW: 0.4,    /* it GROWS from BODY_SEED of its radius to all of it by here of the ball phase, while ... */
  BODY_SEED: 0.25,
  INK_OUT: 0.45,     /* ... the squeezed ink fades into it, gone by here: at 045 there is only the round ball */
  TINT_MELT: 0,      /* how far the marks have turned to the ink by the sag's end (all the way by the ball's middle). 0: through
                        the sag every mark runs in its OWN colour - 0.6 turned the pale series and the grid salmon-pink */
  INK_DEEP: 3,       /* THE INK: the chart's DOMINANT stroke (its first series) concentrated this many times by K-M - the
                        same hue, deeper. Never a mix of every series: the golden page's four mixed land on green */
  CORE: 12,          /* the ball's shaded side, the same ink at this concentration (the weight read in the shading) */
  LIGHT: 1,          /* the ball's lit side: the stroke itself */
  TEXT_STREAK: 1.6,  /* the words' streak: its vertical blur is half the run, it hangs 0.6 of the run below the glyph, and its
                        spread alpha is lifted this much so it reads as ink trailing, not a haze */
  SHEEN: 0.5,        /* its ONE highlight: the stroke taken this far toward white, a small spot up and to the left */
  SPLAT_OUT: 3.5,    /* splash:chart - the landed splats fade this many times faster than the paint clock and ... */
  SPLAT_SHRINK: 0.5, /* ... shrink by this much as the chart shows through: they resolve INTO it and never sit over its
                        labels at full ink (they covered "Mega-cap" at 075 - the parent's read, 2026-09-13) */
  /* THE WEIGHT (stopaction's dials, named): the ball lands in its own weight before it goes anywhere */
  MASS: "liquid",    /* stopaction MASS for the squash: liquid holds its squash TWO frames (ink holds one) - a heavy wet body */
  SQUASH: 0.30,      /* impactSquash's IMPACT_SQUASH for the ball (stopaction's card default is 0.22) */
  ANTIC: 0.22,       /* the share of the throw phase the ball sits in that squash before the launch */
  /* THE THROW - heavy: a low arc, little tumble, out the bottom */
  TO: [1.02, 1.32],  /* the default exit point in STAGE fractions: off the bottom right [was 1.16, 1.22] */
  ARC: 0.06,         /* throwXf's ARC for the ball (stopaction 0.22: a card lifts; a heavy ball barely does) */
  SPIN_DEG: 4,       /* throwXf's SPIN_DEG for the ball (stopaction 9) */
  /* THE SPLASH */
  DROPS: 14,         /* droplets in the splatter */
  BURST_END: 0.40,   /* the share of the ending the burst takes; the rest is the PAINT (the stains growing) */
  SPLASH_SPREAD: 0.30,   /* the angular jitter (radians) on each droplet's ray */
  LAND_MIN: 0.25,    /* where a droplet lands along its ray, as a share of the distance to the ink box's edge ... */
  LAND_MAX: 0.92,    /* ... so the whole splatter lands ON the board */
  DROP_R: 0.035,     /* a droplet's radius as a share of the box's height */
  FLAT: 0.62,        /* how far the ball flattens as it bursts (1 - FLAT of its height) */
  REVEAL_R: 0.75,    /* a stain's reach as a share of the box's height (seeded 0.6x - 1.4x) */
  CORE_R: 0.70,      /* the stain under the ball's own impact */
  FLOOD_FROM: 0.70,  /* the board's last cover fades out from here of the paint clock, so the reveal is whole at u = 1 */
  TAIL: 2.2,         /* a landed splat's tail toward the impact, in its own radii (in flight it is longer: speed) */
  LOBES: 14,         /* a splat's seeded lobes */
  SPLAT_RAG: 16,     /* a splat's torn edge: the K-M soak's noise displacement, px */
  STAIN_RAG: 70,     /* a paint stain's torn edge, px - the ink-bloom's ragged front (INTAKE-INK-BLOOM-2026-09-08) */
  STAIN_BLUR: 6,     /* the stains' own gooey threshold: blur px ... */
  STAIN_SLOPE: 12,   /* ... and ramp */
  SPRING: 0.09,      /* splash:plate - the plate SPRINGS UP: from 1 - SPRING of its size, over its rest by ~2.5 %, settled at
                        the end (a damped cosine; 0.05 settling one way was invisible). 1 - 0.09 of a world that overhangs
                        the stage by 5 % still covers it */
  INK_HEX: "#E9E2D2",    /* the marks' colour when the chart carries no stroke to read (a page of words) */
});

export const MELT_ENDINGS = Object.freeze(["throw", "splash:chart", "splash:plate"]);

const mc01 = (v) => (v <= 0 ? 0 : v >= 1 ? 1 : v);   /* the engine inlines every module into ONE scope, so a
   private helper carries the module's own prefix - `c01` is ink.mjs's */
const mSlump = (u) => { const k = mc01(u); return k * k; };
const mEase = (u) => { const k = mc01(u); return k * k * (3 - 2 * k); };

/* ---- the authored form ------------------------------------------------------------------------------------------ */
/* `melt` | `melt:throw` | `melt:splash:chart` | `melt:splash:plate`, `:<s>`, and on a throw `:<x>,<y>`, in any order after
   the name. Throws on anything else, so a typo in a shot table is a refusal and not a silent default. */
export const meltOpts = (exit, o = {}) => {
  const P = Object.assign({}, MELT, o), bits = String(exit == null ? "" : exit).split(":");
  const out = { name: bits[0] || "", secs: P.S, ending: null, to: null };
  const setEnding = (e) => {
    if (out.ending) throw new Error("melt: two endings (" + out.ending + " and " + e + ") - a melt ends one way");
    out.ending = e;
  };
  for (let i = 1; i < bits.length; i++) {
    const b = bits[i].trim();
    if (b === "") continue;
    if (b === "throw") { setEnding("throw"); continue; }
    if (b === "splash") {
      const nx = (bits[i + 1] || "").trim();
      if (nx !== "chart" && nx !== "plate") {
        throw new Error("melt: splash names no ending since E88 - say splash:chart (the splatter forms the next chart) or splash:plate (a narrative plate springs up out of it)");
      }
      setEnding("splash:" + nx); i++; continue;
    }
    if (b === "chart" || b === "plate") throw new Error("melt: " + b + " is a splash's ending - say splash:" + b);
    if (b.indexOf(",") >= 0) {
      const xy = b.split(",").map(Number);
      if (xy.length !== 2 || !xy.every((v) => Number.isFinite(v))) throw new Error("melt: " + b + " is not an x,y point in stage fractions");
      out.to = xy; continue;
    }
    const v = Number(b);
    if (!(Number.isFinite(v) && v > 0)) throw new Error("melt: " + b + " is neither a length in seconds, nor an ending (throw, splash:chart, splash:plate), nor an x,y point");
    out.secs = v;
  }
  out.ending = out.ending || "throw";
  if (out.to && out.ending !== "throw") throw new Error("melt: an x,y point is where a THROW goes - a splash lands on the board");
  out.to = out.to || [P.TO[0], P.TO[1]];
  return out;
};

/* ---- the phases ------------------------------------------------------------------------------------------------- */
export const meltShares = (o = {}) => {
  const P = Object.assign({}, MELT, o);
  return [P.MELT_END, P.BALL_END - P.MELT_END, 1 - P.BALL_END];
};
export const meltPhase = (u, o = {}) => {
  const P = Object.assign({}, MELT, o), k = mc01(u);
  /* GONE takes the boundary itself: (t - t0) / secs cannot be trusted to reach exactly 1 in floating point */
  if (u >= 1 - 1e-9) return { name: "gone", k: 1, from: 1, span: 0 };
  if (k < P.MELT_END) return { name: "melt", k: k / P.MELT_END, from: 0, span: P.MELT_END };
  if (k < P.BALL_END) return { name: "ball", k: (k - P.MELT_END) / (P.BALL_END - P.MELT_END), from: P.MELT_END, span: P.BALL_END - P.MELT_END };
  return { name: "fly", k: (k - P.BALL_END) / (1 - P.BALL_END), from: P.BALL_END, span: 1 - P.BALL_END };
};
/* the outline's blur in px: up over the melt, back to 0 by the end of the ball (a ball is solid, not a cloud) */
export const meltBlur = (u, o = {}) => {
  const P = Object.assign({}, MELT, o), ph = meltPhase(u, P);
  if (ph.name === "melt") return P.BLUR * mEase(ph.k);
  if (ph.name === "ball") return P.BLUR * (1 - mEase(ph.k));
  return 0;
};
/* the throw's launch as a share of the window: the board is up until here, and the next chart's clock starts here */
export const meltRelease = (o = {}) => {
  const P = Object.assign({}, MELT, o);
  return P.BALL_END + P.ANTIC * (1 - P.BALL_END);
};
/* how long the engine holds the NEXT page's clock under a throw: the new chart draws once the board is clear. A splash
   holds nothing (the chart arrives built, through the stains) and no melt holds a world that is not a page. */
export const meltDrawDelay = (opts, incomingIsPage, o = {}) =>
  (opts && opts.ending === "throw" && incomingIsPage) ? meltRelease(o) * Math.max(0.05, +opts.secs || MELT.S) : 0;

/* ---- the sag ---------------------------------------------------------------------------------------------------- */
const dripBump = (dx, w) => { const k = mc01(Math.abs(dx) / Math.max(1e-6, w)); const c = Math.cos(k * Math.PI / 2); return c * c; };
export const meltDrips = (rect, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), n = Math.max(1, P.DRIPS | 0), step = rect.w / n, out = [];
  for (let i = 0; i < n; i++) {
    out.push({ c: rect.x + step * (i + 0.5) + P.DRIP_JIT * step * (rnd(i) - 0.5),
               amp: 0.45 + 0.55 * rnd(40 + i), delay: P.DRIP_DELAY * rnd(70 + i), w: P.DRIP_W * rect.w });
  }
  return out;
};
export const meltDepth = (x, k, rect, drips, o = {}) => {
  const P = Object.assign({}, MELT, o), u = mc01(k);
  let deepest = 0;
  for (const d of drips) {
    const own = mSlump(mc01((u - d.delay) / Math.max(1e-6, 1 - d.delay)));
    deepest = Math.max(deepest, dripBump(x - d.c, d.w) * d.amp * own);
  }
  return rect.h * (P.SAG * deepest + P.BASE_SAG * mSlump(u));
};
export const meltTop = (x, k, rect, drips, o = {}) => {
  const P = Object.assign({}, MELT, o), u = mc01(k);
  let over = 0;
  for (const d of drips) over = Math.max(over, dripBump(x - d.c, d.w * 1.15) * d.amp);
  return rect.y + rect.h * P.TOP_SAG * mSlump(u) * (0.55 + 0.45 * over);
};
/* THE MELTING OUTLINE: a closed ring walked clockwise from the top-left - the top edge, the right side, the foot sampled
   right to left with the drips hung from it, the left side back up. Sampled even-ish all the way round: the closed
   centripetal Catmull-Rom (morphAPath) bulges between two knots far apart next to two that are not. */
export const meltOutline = (rect, k, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), n = Math.max(3, P.N | 0), drips = meltDrips(rect, rnd, P);
  const top = Math.max(2, P.TOP_N | 0), side = Math.max(1, P.SIDE_N | 0), foot = rect.y + rect.h, pts = [];
  for (let j = 0; j < top; j++) { const x = rect.x + rect.w * (j / (top - 1)); pts.push([x, meltTop(x, k, rect, drips, P)]); }
  const tR = meltTop(rect.x + rect.w, k, rect, drips, P), tL = meltTop(rect.x, k, rect, drips, P);
  for (let j = 1; j <= side; j++) pts.push([rect.x + rect.w, tR + (foot - tR) * (j / (side + 1))]);
  for (let j = n - 1; j >= 0; j--) {
    const x = rect.x + rect.w * (j / (n - 1));
    pts.push([x, foot + meltDepth(x, k, rect, drips, P)]);
  }
  for (let j = side; j >= 1; j--) pts.push([rect.x, tL + (foot - tL) * (j / (side + 1))]);
  return pts;
};
/* THE RUN: how far the ink's pixels smear down (px). It grows with the sag and drains back into the ball as it forms. */
export const meltRun = (phase, k, rect, o = {}) => {
  const P = Object.assign({}, MELT, o);
  if (phase === "melt") return P.RUN * rect.h * mSlump(k);
  if (phase === "ball") return P.RUN * rect.h * (1 - mEase(k));
  return 0;
};

/* ---- the ball --------------------------------------------------------------------------------------------------- */
export const ballCircle = (c, r, n) => {
  const out = [];
  for (let i = 0; i < n; i++) { const a = 2 * Math.PI * (i / n); out.push([c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)]); }
  return out;
};
export const ballAt = (rect, k, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), src = meltOutline(rect, 1, rnd, P);
  const c = centroid(src), r = P.BALL_R * rect.h;
  const prep = morphAPrepare(src, ballCircle(c, r, P.CIRCLE_N), { n: P.RING_N });
  return { outline: morphAAt(prep, mEase(k)).outline, centre: c, r, k: mc01(k) };
};
/* THE SQUEEZE: the ink's scale about the ball's centre at ball-phase progress k - 1 at the start, and at the end the ink
   box's longer side is SQUEEZE ball-diameters. Monotone in k. */
export const meltSqueeze = (rect, r, k, o = {}) => {
  const P = Object.assign({}, MELT, o), end = Math.min(1, P.SQUEEZE * 2 * r / Math.max(1e-6, rect.w, rect.h));
  return 1 + (end - 1) * mEase(k);
};
/* the ink body's opacity at ball-phase progress k: none, then up to solid before the ball moves */
export const meltBodyAlpha = (k, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return mEase(mc01((k - P.BODY_FROM) / Math.max(1e-6, P.BODY_TO - P.BODY_FROM)));
};
/* the ball's radius as a share of BALL_R at ball-phase progress k: from a seed to whole, monotone */
export const meltBodyGrow = (k, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return P.BODY_SEED + (1 - P.BODY_SEED) * mEase(mc01(k / Math.max(1e-6, P.BODY_GROW)));
};
export const ballFlat = (outline, c, k, o = {}) => {
  const P = Object.assign({}, MELT, o), f = 1 - P.FLAT * mEase(k), g = 1 + (1 / Math.max(0.05, f) - 1) * 0.5;
  return outline.map((p) => [c[0] + (p[0] - c[0]) * g, c[1] + (p[1] - c[1]) * f]);
};
/* THE WEIGHT: the ball's squash `ts` seconds after it has formed (or hit the board) - stopaction's impactSquash on the
   melt's material, on the melt's hold. 0 on the contact frame, SQUASH on the next hold, released by the material. */
export const meltSettle = (ts, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return impactSquash(ts, P.MASS, P.HOLD, P.FPS, { IMPACT_SQUASH: P.SQUASH });
};

/* ---- the colour ------------------------------------------------------------------------------------------------- */
const meltRFromKs = (ks) => { const k = Math.max(0, ks); return 1 + k - Math.sqrt(k * k + 2 * k); };
/* THE INK THE BALL IS MADE OF: the marks' colours mixed by Kubelka-Munk (the mean K/S per channel - a subtractive mix, not
   an average of lights) and concentrated `density` times. density 1 is the marks' own mix; above it, darker and deeper. */
export const meltMixInk = (hexes, density = 1) => {
  const list = (hexes || []).filter((h) => /^#[0-9a-fA-F]{6}$/.test(h));
  const use = list.length ? list : [MELT.INK_HEX], ks = [0, 0, 0];
  for (const h of use) hexToLin(h).forEach((v, i) => { ks[i] += ksFromR(v) / use.length; });
  return linToHex(ks.map((k) => meltRFromKs(k * Math.max(0.01, density))));
};

/* THE INK the marks become and the ball is made of: the dominant stroke, concentrated */
export const meltInkOf = (hexes, density = 1) => meltMixInk(((hexes || []).filter((h) => /^#[0-9a-fA-F]{6}$/.test(h))).slice(0, 1), density);
/* how far the marks have turned into that ink */
export const meltTint = (phase, k, o = {}) => {
  const P = Object.assign({}, MELT, o);
  if (phase === "melt") return P.TINT_MELT * mEase(k);
  if (phase === "ball") return P.TINT_MELT + (1 - P.TINT_MELT) * mEase(mc01(2 * k));
  return 1;
};

/* ---- the splash ------------------------------------------------------------------------------------------------- */
/* A SPLAT: a seeded lobed blob with a tail pointing BACK along its ray to the impact (`back`, radians), drawn as a closed
   centripetal Catmull-Rom - the shape an ink drop makes when it hits paper at an angle */
export const meltSplatPath = (x, y, r, back, tail, rnd, salt, o = {}) => {
  const P = Object.assign({}, MELT, o), n = Math.max(6, P.LOBES | 0), pts = [];
  for (let j = 0; j < n; j++) {
    const f = 2 * Math.PI * (j / n), c = Math.cos(f), rr = r * (0.72 + 0.5 * rnd(salt * 31 + j)) + (c > 0 ? Math.pow(c, 8) * tail : 0);
    pts.push([x + Math.cos(back + f) * rr, y + Math.sin(back + f) * rr]);
  }
  return morphAPath(pts);
};
/* the satellite droplets thrown off behind each splat, along its ray */
export const splashSats = (drops) => {
  const out = [];
  for (const d of drops) {
    if (!(d.d > 0)) continue;
    const cx = Math.cos(d.a), cy = Math.sin(d.a), ox = d.x - cx * d.d, oy = d.y - cy * d.d;
    out.push({ x: ox + cx * d.d * 0.62, y: oy + cy * d.d * 0.62, r: d.r * 0.32 }, { x: ox + cx * d.d * 0.83, y: oy + cy * d.d * 0.83, r: d.r * 0.2 });
  }
  return out;
};
/* the plate's spring over the paint clock: up from 1 - SPRING, over its rest, settled at g = 1 (exactly 1 there) */
export const meltSpring = (g, o = {}) => {
  const P = Object.assign({}, MELT, o), k = mc01(g);
  return k >= 1 ? 1 : 1 - P.SPRING * Math.exp(-3 * k) * Math.cos(2.5 * Math.PI * k);
};
/* the distance from c along the unit ray (cx, cy) to the box's edge */
const meltRayToEdge = (c, cx, cy, rect) => {
  const tx = cx > 1e-9 ? (rect.x + rect.w - c[0]) / cx : cx < -1e-9 ? (rect.x - c[0]) / cx : Infinity;
  const ty = cy > 1e-9 ? (rect.y + rect.h - c[1]) / cy : cy < -1e-9 ? (rect.y - c[1]) / cy : Infinity;
  return Math.max(0, Math.min(tx, ty));
};
/* THE SPLATTER: DROPS droplets thrown out along seeded rays on the soak's own STEPPED clock (never contracting), each
   LANDING on the board - a share of the way to the ink box's edge - and spreading a little as it lands. `d` is the
   distance travelled along its ray: monotone in k and never past `land`. */
export const splashDrops = (c, rect, k, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), p = soakStepped(mc01(k), rnd), out = [];
  for (let i = 0; i < Math.max(0, P.DROPS | 0); i++) {
    const a = 2 * Math.PI * (i / P.DROPS) + P.SPLASH_SPREAD * (2 * rnd(300 + i) - 1), cx = Math.cos(a), cy = Math.sin(a);
    const land = meltRayToEdge(c, cx, cy, rect) * (P.LAND_MIN + (P.LAND_MAX - P.LAND_MIN) * rnd(400 + i)), d = land * p;
    const r = P.DROP_R * rect.h * (0.6 + 0.8 * rnd(500 + i)) * (1 + 0.6 * p);
    out.push({ x: c[0] + cx * d, y: c[1] + cy * d, r, d, a, land, tail: p > 0 ? r * (P.TAIL + 3 * (1 - p)) : 0 });
  }
  return out;
};
/* THE PAINT: every landed drop grows as a seeded stain (its own stepped staircase), and one grows under the ball's own
   impact. Radii are monotone in g. `cover` is the board's remaining opacity (whole until FLOOD_FROM, then out to exactly
   0), `rim` the wet ink at the fronts (drying as they spread). */
export const splashStains = (drops, c, r, rect, g, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), h = rect.h, gg = mc01(g);
  const grow = (salt) => (gg <= 0 ? 0 : soakStepped(gg, (k) => rnd(1000 + 37 * salt + k)));
  const stains = drops.map((d, i) => ({ x: d.x, y: d.y, r: d.r + (P.REVEAL_R * h * (0.6 + 0.8 * rnd(600 + i)) - d.r) * grow(i + 1) }));
  stains.push({ x: c[0], y: c[1], r: r + (P.CORE_R * h - r) * grow(0) });
  return { stains, cover: 1 - mEase(mc01((gg - P.FLOOD_FROM) / Math.max(1e-6, 1 - P.FLOOD_FROM))), rim: 1 - mEase(gg) };
};

/* ---- the throw -------------------------------------------------------------------------------------------------- */
/* THE FLIGHT, BACKWARDS: throwXf brings a thing FROM an offset TO its rest; a launch is that landing in reverse. t' = F(1 - k):
   at k = 0 the ball sits at rest and at k = 1 it is at `from`. The ball's ARC and SPIN_DEG are its own (heavy). */
export const meltThrowAt = (k, from, secs, o = {}) => {
  const P = Object.assign({}, MELT, o), F = Math.max(0.05, secs), kk = mc01(k);
  if (kk <= 0) return { x: 0, y: 0, rot: 0, alpha: 0, theta: Math.PI / 2, phase: "flight", u: 1, hold: 1, h: 0, ground: 0, shake: { x: 0, y: 0 } };
  return throwXf(from, P.MASS, F * (1 - kk), { FLIGHT_S: F, ARC: P.ARC, SPIN_DEG: P.SPIN_DEG });
};

/* ---- the frame -------------------------------------------------------------------------------------------------- */
/* EVERYTHING THE PAINTER NEEDS, in one object, from (t0, t, o, rnd) alone. o carries the geometry as well as any dial:
   `rect` (the INK box, in the outgoing world's own px), `stagebox` (the stage's box in those px), `secs`, `ending`, `to`.
     path     the ink's mask, in the ink's own (unsqueezed) px     body      the ball, in world px (null: no ball)
     scale    the ink's squeeze about `centre`                     bodyAlpha the ball's opacity
     run      the ink's smear, px; inkBlur its blur                 squash    { a, theta } on the ball, stopaction's tensor
     xf       the throw's offset and tumble                        drops     the splatter; stains / cover / rim the paint
     boardUp  the outgoing board is on screen                      reveal    it wears the reveal mask; spring the plate's scale */
export const meltState = (t0, t, o = {}, rnd) => {
  const P = Object.assign({}, MELT, o), rect = P.rect, sb = P.stagebox || rect, to = P.to || P.TO;
  const ending = MELT_ENDINGS.indexOf(P.ending) >= 0 ? P.ending : "throw";
  const secs = Math.max(0.05, +P.secs || P.S), u = mc01((t - t0) / secs), ph = meltPhase(u, P);
  const st = { u, secs, ending, phase: ph.name, k: ph.k, blur: meltBlur(u, P), inkBlur: 0, run: 0, scale: 1,
               inkOpacity: 1, path: "", outline: null, body: "", bodyOutline: null, bodyAlpha: 0, centre: null, r: 0,
               squash: { a: 0, theta: 0 }, xf: null, drops: [], stains: [], cover: 1, rim: 0, reveal: false,
               spring: 1, dropAlpha: 1, dropScale: 1, tint: 0, sats: [], textOpacity: 0, boardUp: true, gone: false };
  st.inkBlur = P.INK_BLUR * st.blur / Math.max(1e-6, P.BLUR);
  if (ph.name === "gone") { st.gone = true; st.boardUp = false; st.inkOpacity = 0; st.cover = 0; return st; }
  if (ph.name === "melt") {
    st.outline = meltOutline(rect, ph.k, rnd, P);
    st.path = morphAPath(st.outline);
    st.run = meltRun("melt", ph.k, rect, P);
    st.tint = meltTint("melt", ph.k, P);
    st.textOpacity = meltTextAlpha(ph.k);   /* the words run down as their own glyphs and are gone by the ball */
    return st;
  }
  /* the ball and the ending run on the STEPPED clock, each on its own phase-local seconds (a pure quantisation of t) */
  const tl = t - t0 - ph.from * secs, span = ph.span * secs, tq = stepped(Math.max(0, tl), P.HOLD, P.FPS);
  const kq = mc01(tq / Math.max(1e-6, span));
  if (ph.name === "ball") {
    const b = ballAt(rect, kq, rnd, P), s = meltSqueeze(rect, b.r, kq, P);
    st.k = kq; st.centre = b.centre; st.r = b.r; st.scale = s;
    st.bodyOutline = b.outline; st.bodyAlpha = meltBodyAlpha(kq, P);
    st.body = morphAPath(ballCircle(b.centre, b.r * meltBodyGrow(kq, P), P.CIRCLE_N));   /* the SOLID ball: a crisp circle, never the box */
    st.tint = meltTint("ball", kq, P);
    st.inkBlur = st.inkBlur + P.BALL_FUSE * mEase(kq);   /* the marks FUSE into one body as they compact */
    /* the mask is in the ink's own px, and the ink is squeezed by s about the centre: the same body, unsqueezed */
    st.outline = b.outline.map((p) => [b.centre[0] + (p[0] - b.centre[0]) / s, b.centre[1] + (p[1] - b.centre[1]) / s]);
    st.path = morphAPath(st.outline);
    st.run = meltRun("ball", kq, rect, P);
    st.inkOpacity = 1 - mEase(mc01(kq / Math.max(1e-6, P.INK_OUT)));
    return st;
  }
  const b = ballAt(rect, 1, rnd, P), circle = ballCircle(b.centre, b.r, P.CIRCLE_N);
  st.k = kq; st.centre = b.centre; st.r = b.r; st.inkOpacity = 0; st.bodyAlpha = 1;
  if (ending === "throw") {
    st.bodyOutline = circle; st.body = morphAPath(circle);
    if (kq < P.ANTIC) {
      st.squash = { a: meltSettle(tq, P), theta: 0 };   /* stretched ACROSS, pressed down: the ball has weight before it moves */
      st.xf = meltThrowAt(0, { x: 0, y: 0 }, span, P);
    } else {
      const from = { x: sb.x + to[0] * sb.w - b.centre[0], y: sb.y + to[1] * sb.h - b.centre[1] };
      st.xf = meltThrowAt((kq - P.ANTIC) / Math.max(1e-6, 1 - P.ANTIC), from, span * (1 - P.ANTIC), P);
      st.squash = { a: st.xf.alpha || 0, theta: st.xf.theta || 0 };   /* stretched along the flight */
    }
    st.boardUp = u < meltRelease(P);
    return st;
  }
  /* a SPLASH: the burst, then the paint. Its clock is measured to ONE HOLD before the window ends: the stepped clock's last
     pose lands a hold early, and a paint that was 0.8 done on that pose would pop the board's last cover at `gone`. */
  const ks = mc01(tq / Math.max(1e-6, span - P.HOLD / P.FPS));
  const kb = mc01(ks / Math.max(1e-6, P.BURST_END)), g = mc01((ks - P.BURST_END) / Math.max(1e-6, 1 - P.BURST_END));
  st.bodyOutline = ballFlat(circle, b.centre, kb, P); st.body = morphAPath(st.bodyOutline);
  st.bodyAlpha = 1 - mEase(mc01((kb - 0.5) / 0.5));   /* the ball holds its mass through the hit, then IS the splatter */
  st.squash = { a: meltSettle(tq, P), theta: 0 };
  st.drops = splashDrops(b.centre, rect, kb, rnd, P);
  st.sats = splashSats(st.drops);
  if (kq >= P.BURST_END) {
    const paint = splashStains(st.drops, b.centre, b.r, rect, g, rnd, P);
    st.stains = paint.stains; st.cover = paint.cover; st.rim = paint.rim; st.reveal = true;
    const rate = ending === "splash:chart" ? P.SPLAT_OUT : 2.5;
    st.dropAlpha = 1 - mEase(mc01(g * rate));   /* a drop IS its stain's first ink: it soaks away as the stain opens */
    if (ending === "splash:chart") st.dropScale = 1 - P.SPLAT_SHRINK * mEase(mc01(g * 2));
    if (ending === "splash:plate") st.spring = meltSpring(g, P);
  }
  return st;
};

/* ---- the markup the painter mounts once ------------------------------------------------------------------------- */
/* THE GOOEY THRESHOLD as SVG primitives: blur, then re-steepen the alpha. Blur FIRST, then the ramp - the other way round
   is a fade. The K-M colour stages are deliberately not here: they would flatten what they filter to one ink. */
export const meltFilterMarkup = (id, u, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<filter id="' + id + '" x="-40%" y="-40%" width="180%" height="180%" color-interpolation-filters="sRGB">'
    + '<feGaussianBlur stdDeviation="' + meltBlur(u, P).toFixed(2) + '"/>'
    + '<feComponentTransfer><feFuncA type="linear" slope="' + P.EDGE_SLOPE + '" intercept="0"/></feComponentTransfer>'
    + '</filter>';
};
/* the mask the melting ink wears: one path, filtered */
export const meltMaskMarkup = (id, filterId) =>
  '<mask id="' + id + '" maskUnits="objectBoundingBox" x="-0.4" y="-0.4" width="1.8" height="1.8">'
  + '<g filter="url(#' + filterId + ')"><path fill="#fff" d=""/></g></mask>';
/* THE RUN on the marks' own pixels: RUN_COPIES copies offset downward and merged over the original, then the gooey
   threshold - the lines swell, trail down and fuse. The region opens downward, where the ink goes. */
export const meltInkFilterMarkup = (id, o = {}) => {
  const P = Object.assign({}, MELT, o);
  /* the marks first lose every FAINT pixel (alpha under a quarter): a near-transparent wash on the page - a grain, a plot
     ground - would otherwise be ramped INK_SLOPE times into an opaque grey slab over the board (measured on the first
     proof frame, 2026-09-13). A mark's own core is opaque and passes untouched. */
  let offs = "", merge = '<feMergeNode in="' + id + 'k"/>';
  for (let j = 1; j <= Math.max(1, P.RUN_COPIES | 0); j++) {
    offs += '<feOffset in="' + id + 'k" dx="0" dy="0" result="' + id + "r" + j + '"/>';
    merge += '<feMergeNode in="' + id + "r" + j + '"/>';
  }
  return '<filter id="' + id + '" x="-5%" y="-5%" width="110%" height="150%" color-interpolation-filters="sRGB">'
    + '<feComponentTransfer in="SourceGraphic" result="' + id + 'k"><feFuncA type="table" tableValues="0 0 1 1 1"/></feComponentTransfer>'
    + offs + "<feMerge>" + merge + "</feMerge>"
    + '<feGaussianBlur stdDeviation="0"/>'
    + '<feComponentTransfer result="' + id + 'o"><feFuncA type="linear" slope="' + P.INK_SLOPE + '" intercept="0"/></feComponentTransfer>'
    /* THE TINT: the fused marks turned toward THE INK by k2 (the painter writes k2 = tint, k3 = 1 - tint each frame) */
    + '<feFlood flood-color="#000" result="' + id + 'c"/><feComposite in="' + id + 'c" in2="' + id + 'o" operator="in" result="' + id + 't"/>'
    + '<feComposite in="' + id + 't" in2="' + id + 'o" operator="arithmetic" k1="0" k2="0" k3="1" k4="0"/></filter>';
};
/* THE REVEAL: a luminance mask the BOARD wears under a splash - white everywhere, and the stains cut black through it,
   under their own gooey threshold, so two stains that meet run together */
export const meltRevealMarkup = (id, filterId) =>
  '<mask id="' + id + '" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="-10000" y="-10000" width="20000" height="20000">'
  + '<rect x="-10000" y="-10000" width="20000" height="20000" fill="#fff"/><g filter="url(#' + filterId + ')"></g></mask>';
export const meltStainFilterMarkup = (id, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<filter id="' + id + '" x="-50%" y="-50%" width="200%" height="200%" color-interpolation-filters="sRGB">'
    + '<feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="3" seed="11" result="' + id + 'n"/>'
    + '<feDisplacementMap in="SourceGraphic" in2="' + id + 'n" scale="' + P.STAIN_RAG + '" xChannelSelector="R" yChannelSelector="G"/>'
    + '<feGaussianBlur stdDeviation="' + P.STAIN_BLUR + '"/>'
    + '<feComponentTransfer><feFuncA type="linear" slope="' + P.STAIN_SLOPE + '" intercept="0"/></feComponentTransfer></filter>';
};
/* a SPLAT's torn edge: the soak's noise displacement and nothing else - no blur, so the ink stays opaque and crisp */
export const meltSplatFilterMarkup = (id, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<filter id="' + id + '" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
    + '<feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="5" result="' + id + 'n"/>'
    + '<feDisplacementMap in="SourceGraphic" in2="' + id + 'n" scale="' + P.SPLAT_RAG + '" xChannelSelector="R" yChannelSelector="G"/></filter>';
};
/* a colour taken toward white by `k` (linear light) - the ball's one sheen */
export const meltSheen = (hex, k) => linToHex(hexToLin(hex).map((v) => v + (1 - v) * mc01(k)));
/* the ball's body: THE INK, one small highlight up and to the left, the stroke, then concentrated toward its shaded side */
export const meltBodyGradientMarkup = (id, hexes, o = {}) => {
  const P = Object.assign({}, MELT, o), lit = meltInkOf(hexes, P.LIGHT);
  return '<radialGradient id="' + id + '" cx="0.34" cy="0.3" r="0.8" fx="0.32" fy="0.26">'
    + '<stop offset="0" stop-color="' + meltSheen(lit, P.SHEEN) + '"/>'
    + '<stop offset="0.14" stop-color="' + lit + '"/>'
    + '<stop offset="0.55" stop-color="' + meltInkOf(hexes, P.INK_DEEP) + '"/>'
    + '<stop offset="1" stop-color="' + meltInkOf(hexes, P.CORE) + '"/></radialGradient>';
};
/* a SPLAT's wet ink: the stroke at its core, the ball's ink, and a dark wet rim at its edge (per splat, its own box) */
export const meltSplatGradientMarkup = (id, hexes, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<radialGradient id="' + id + '" cx="0.5" cy="0.5" r="0.5">'
    + '<stop offset="0" stop-color="' + meltInkOf(hexes, P.LIGHT) + '"/>'
    + '<stop offset="0.55" stop-color="' + meltInkOf(hexes, P.INK_DEEP) + '"/>'
    + '<stop offset="0.85" stop-color="' + meltInkOf(hexes, P.CORE) + '"/>'
    + '<stop offset="1" stop-color="' + meltInkOf(hexes, P.CORE) + '"/></radialGradient>';
};
/* THE WORDS' RUN: ONE continuous streak under each glyph - its own ink blurred VERTICALLY only (stdDeviation "0 s", so a
   letter's columns stay apart and never swell sideways into its box), pushed down by the run and a little denser, with the
   crisp glyph drawn over it so its top edge stays legible. Merged offset copies read as six stacked echoes of each word
   (the parent's read of 015, 2026-09-13); a one-axis blur has no copies to count. */
export const meltTextFilterMarkup = (id, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<filter id="' + id + '" x="-5%" y="-10%" width="110%" height="160%" color-interpolation-filters="sRGB">'
    + '<feGaussianBlur in="SourceGraphic" stdDeviation="0 0" result="' + id + 'b"/>'
    + '<feOffset in="' + id + 'b" dx="0" dy="0" result="' + id + 'd"/>'
    + '<feComponentTransfer in="' + id + 'd" result="' + id + 't"><feFuncA type="linear" slope="' + P.TEXT_STREAK + '" intercept="0"/></feComponentTransfer>'
    + '<feMerge><feMergeNode in="' + id + 't"/><feMergeNode in="SourceGraphic"/></feMerge></filter>';
};
/* THE TWO NUMBERS that filter is DRIVEN by, exactly as paintMelt has always written them: the vertical blur (half the
   run - "0 s", so a letter's columns stay apart) and how far the streak hangs below the glyph (0.6 of it). Exported for
   a caller that melts ONE text rather than a page of them - species/compare.mjs's `melt` form - so the streak is read
   off this module and never copied into another. paintMelt writes what it wrote before, to the character. */
export const meltTextStreak = (run) => ({ blur: "0 " + (Math.max(0, run) * 0.5).toFixed(2), dy: (Math.max(0, run) * 0.6).toFixed(1) });
/* THE WORDS' OWN INK over the sag: they run down as their own glyphs and are gone by the ball. meltState's
   `textOpacity` IS this, and calls it. */
export const meltTextAlpha = (k) => 1 - mEase(k);
/* the SVG transform of the ball: the flight's offset and tumble, and stopaction's area-preserving squash, about its centre */
export const meltBodyTransform = (st) => {
  if (!st.centre) return "";
  const cx = st.centre[0], cy = st.centre[1], xf = st.xf || { x: 0, y: 0, rot: 0 }, a = Math.abs(st.squash.a || 0);
  const th = (st.squash.a || 0) < 0 ? (st.squash.theta || 0) + Math.PI / 2 : (st.squash.theta || 0);
  const m = a > 1e-6 ? squashMatrix(th, a) : [1, 0, 0, 1];
  return "translate(" + (cx + (xf.x || 0)).toFixed(2) + " " + (cy + (xf.y || 0)).toFixed(2) + ") rotate(" + (xf.rot || 0).toFixed(2) + ") "
    + "matrix(" + m.map((v) => v.toFixed(4)).join(" ") + " 0 0) translate(" + (-cx).toFixed(2) + " " + (-cy).toFixed(2) + ")";
};

/* ---- the painter ------------------------------------------------------------------------------------------------ */
const MELT_BOARD_CLASSES = ["lp-grain", "lp-edge", "lp-field", "lp-fieldplate"];
export const meltIsBoard = (node) => !!(node && node.classList) && MELT_BOARD_CLASSES.some((c) => node.classList.contains(c));
/* the two halves of one page, by class: the INK clone hides the board, the BOARD world hides the ink */
export const MELT_CSS = ".world.meltink{background:transparent!important;pointer-events:none}"
  + ".meltink .lp-page{background:transparent!important}"
  + MELT_BOARD_CLASSES.map((c) => ".meltink ." + c).join(",") + "{visibility:hidden!important}"
  + ".meltboard .lp-page>" + MELT_BOARD_CLASSES.map((c) => ":not(." + c + ")").join("") + "{visibility:hidden!important}"
  /* the WORDS are not marks: the marks clone never draws them, and the text clone draws nothing else */
  + ".meltink .lp-ink,.meltink .lp-rail,.meltink .lp-chart line,.meltink .lp-chart text{visibility:hidden!important}"
  + ".world.melttext{background:transparent!important;pointer-events:none}"
  + ".melttext .lp-page{background:transparent!important}"
  + ".melttext .lp-page *{visibility:hidden!important}"
  + ".melttext .lp-ink,.melttext .lp-ink *,.melttext .lp-rail,.melttext .lp-rail *,.melttext .lp-chart line,.melttext .lp-chart text,.melttext .lp-chart text *{visibility:visible!important}";

/* the stage's box in the world's own px: `.world` overhangs the stage by 5% on every side */
export const meltStageBox = (wA) => ({ x: wA.offsetWidth / 22, y: wA.offsetHeight / 22,
                                       w: wA.offsetWidth * 10 / 11, h: wA.offsetHeight * 10 / 11 });
/* THE INK BOX in the world's own px: the union of the page's non-board children as laid out, clamped to the charcoal
   field (the ink lives on the board). Read through client rects so the punch's transform is in it, and mapped back into
   the world's px by the world's own scale. null when the world holds no page. */
export const meltInkRect = (wA) => {
  const page = wA.querySelector(".lp-page");
  if (!page) return null;
  const wr = wA.getBoundingClientRect(), kx = wA.offsetWidth / Math.max(1e-6, wr.width), ky = wA.offsetHeight / Math.max(1e-6, wr.height);
  const field = page.querySelector(".lp-field"), fr = field && field.getBoundingClientRect(), pr = page.getBoundingClientRect();
  const clip = fr && fr.width > 1 && fr.height > 1 ? fr : pr;
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const c of page.children) {
    if (meltIsBoard(c)) continue;
    const r = c.getBoundingClientRect();
    if (!(r.width >= 1 && r.height >= 1)) continue;
    x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom);
  }
  if (!(x1 > x0 && y1 > y0)) { x0 = clip.left; y0 = clip.top; x1 = clip.right; y1 = clip.bottom; }
  x0 = Math.max(x0, clip.left); y0 = Math.max(y0, clip.top); x1 = Math.min(x1, clip.right); y1 = Math.min(y1, clip.bottom);
  return { x: (x0 - wr.left) * kx, y: (y0 - wr.top) * ky, w: Math.max(1, (x1 - x0) * kx), h: Math.max(1, (y1 - y0) * ky) };
};
/* the marks' colours, as #rrggbb: every series stroke on the page's charts, as the browser computed it */
const meltHex = (css) => {
  const m = /rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)/.exec(String(css || ""));
  return m ? "#" + [m[1], m[2], m[3]].map((v) => (+v).toString(16).padStart(2, "0")).join("") : (/^#[0-9a-fA-F]{6}$/.test(css) ? css : null);
};
export const meltInkColours = (wA) => {
  const out = [];
  wA.querySelectorAll(".lp-chart .ser, .lp-chart rect[fill]").forEach((n) => {
    const cs = getComputedStyle(n), hx = meltHex(n.classList.contains("ser") ? cs.stroke : cs.fill);
    if (hx && out.indexOf(hx) < 0) out.push(hx);
  });
  return out;
};

/* the overlay, mounted ONCE and kept on wA.__melt: the ink clone (a sibling right after the board, so it rides above
   it), and an svg sibling holding the filters, the masks, the stains' rims, the droplets and the ball. Nothing here reads
   time; the ink box and the colours are read once, from the page as it stands at the boundary. */
const meltMount = (wA, el, id) => {
  const doc = wA.ownerDocument;
  if (!doc.getElementById("meltcss")) { const s = doc.createElement("style"); s.id = "meltcss"; s.textContent = MELT_CSS; doc.head.appendChild(s); }
  const rect = meltInkRect(wA), hexes = meltInkColours(wA);
  const ink = wA.cloneNode(true);
  ink.removeAttribute("id"); ink.classList.add("meltink");
  ink.querySelectorAll("video").forEach((v) => v.remove());
  wA.parentNode.insertBefore(ink, wA.nextSibling);
  const txt = wA.cloneNode(true);
  txt.removeAttribute("id"); txt.classList.add("melttext");
  txt.querySelectorAll("video").forEach((v) => v.remove());
  wA.parentNode.insertBefore(txt, ink.nextSibling);
  wA.classList.add("meltboard");
  const svg = el("svg", "meltov", wA.parentNode, { "pointer-events": "none" });
  const defs = el("defs", "", svg, {});
  defs.innerHTML = meltFilterMarkup(id + "f", 0) + meltMaskMarkup(id + "m", id + "f") + meltInkFilterMarkup(id + "i")
    + meltStainFilterMarkup(id + "s") + meltRevealMarkup(id + "r", id + "s") + meltSplatFilterMarkup(id + "p") + meltBodyGradientMarkup(id + "g", hexes)
    + meltSplatGradientMarkup(id + "w", hexes) + meltTextFilterMarkup(id + "x");
  const ink0 = meltInkOf(hexes, MELT.INK_DEEP);
  defs.querySelector("#" + id + "i feFlood").setAttribute("flood-color", ink0);
  const comps = defs.querySelectorAll("#" + id + "i feComposite");
  const m = { id, svg, defs, ink, txt, rect, hexes, ink0, tintC: comps[comps.length - 1], toff: defs.querySelector("#" + id + "x feOffset"), tblur: defs.querySelector("#" + id + "x feGaussianBlur"),
              blur: defs.querySelector("#" + id + "f feGaussianBlur"), path: defs.querySelector("mask path"),
              iblur: defs.querySelector("#" + id + "i feGaussianBlur"), ioffs: [...defs.querySelectorAll("#" + id + "i feOffset")],
              stainG: defs.querySelector("#" + id + "r g"),
              drops: el("g", "meltdrops", svg, { filter: "url(#" + id + "p)" }),
              bodyG: el("g", "meltbody", svg, {}), splats: [], sats: [], holes: [], sprung: null };
  m.body = el("path", "", m.bodyG, { fill: "url(#" + id + "g)", d: "" });
  svg.style.position = "absolute"; svg.style.overflow = "visible"; svg.style.pointerEvents = "none"; svg.style.zIndex = "4";
  wA.__melt = m;
  return m;
};
/* keep n circles (or paths) in a group, created once and moved after that */
const meltDots = (pool, n, el, parent, attrs, tag = "circle") => { while (pool.length < n) pool.push(el(tag, "", parent, attrs)); return pool; };
const meltCircle = (dot, c) => {
  if (!c || c.r <= 0.2) { dot.setAttribute("r", "0"); return; }
  dot.setAttribute("cx", c.x.toFixed(1)); dot.setAttribute("cy", c.y.toFixed(1)); dot.setAttribute("r", c.r.toFixed(1));
};

/* PAINT ONE FRAME. ctx: { wA, wB, t, t0, opts, rnd, el, id }. The state is meltState's; this only writes it down. A world
   that holds no page is not melted (E88: the melt takes a chart's ink - there is no whole-world melt left to fall back
   to); the engine cuts instead, and so does this. */
export const paintMelt = (ctx) => {
  const { wA, wB, el, rnd } = ctx, id = ctx.id || "melt";
  if (!wA.__melt && !wA.querySelector(".lp-page")) return null;
  if (wA.__melt && !(wA.__melt.svg && wA.__melt.svg.isConnected)) clearMelt(wA);   /* a stale mount: its clone and classes go first */
  const m = wA.__melt ? wA.__melt : meltMount(wA, el, id);
  const st = meltState(ctx.t0, ctx.t, Object.assign({ rect: m.rect, stagebox: meltStageBox(wA) }, ctx.opts), rnd);
  m.svg.style.left = wA.offsetLeft + "px"; m.svg.style.top = wA.offsetTop + "px";
  m.svg.style.width = wA.offsetWidth + "px"; m.svg.style.height = wA.offsetHeight + "px";
  m.svg.setAttribute("viewBox", "0 0 " + wA.offsetWidth + " " + wA.offsetHeight);
  m.svg.style.opacity = st.gone ? "0" : "1";
  /* THE INK: masked, run, squeezed about the ball's centre - hidden once the ball is solid */
  const ink = m.ink, showInk = !st.gone && st.inkOpacity > 0 && st.path;
  ink.style.visibility = showInk ? "" : "hidden";
  ink.style.zIndex = "3";
  if (showInk) {
    m.blur.setAttribute("stdDeviation", st.blur.toFixed(2));
    m.path.setAttribute("d", st.path);
    ink.style.mask = "url(#" + id + "m)"; ink.style.webkitMaskImage = "url(#" + id + "m)";
    m.iblur.setAttribute("stdDeviation", st.inkBlur.toFixed(2));   /* on for every frame the ink shows: its faint-pixel cut is part of the ink */
    m.ioffs.forEach((o, j) => o.setAttribute("dy", (st.run * (j + 1) / m.ioffs.length).toFixed(1)));
    ink.style.filter = "url(#" + id + "i)";
    m.tintC.setAttribute("k2", st.tint.toFixed(4)); m.tintC.setAttribute("k3", (1 - st.tint).toFixed(4));
    ink.style.transformOrigin = st.centre ? st.centre[0].toFixed(1) + "px " + st.centre[1].toFixed(1) + "px" : "";
    ink.style.transform = (st.scale !== 1 ? "scale(" + st.scale.toFixed(4) + ") " : "") + wA.style.transform;
  }
  /* THE WORDS: their own glyphs running down, fading out over the sag */
  const txt = m.txt, showTxt = !st.gone && st.textOpacity > 0.002;
  txt.style.display = showTxt ? "" : "none";   /* never `visibility`: the words' own !important visible would outrank it */
  txt.style.zIndex = "3";
  if (showTxt) {
    const streak = meltTextStreak(st.run);
    m.tblur.setAttribute("stdDeviation", streak.blur);
    m.toff.setAttribute("dy", streak.dy);
    txt.style.filter = "url(#" + id + "x)";
    txt.style.opacity = st.textOpacity.toFixed(4);
    txt.style.transform = wA.style.transform;
  }
  ink.style.opacity = showInk ? st.inkOpacity.toFixed(4) : "0";
  /* THE BALL */
  m.body.setAttribute("d", st.body || "");
  m.body.setAttribute("opacity", (st.body ? st.bodyAlpha : 0).toFixed(3));
  m.bodyG.setAttribute("transform", meltBodyTransform(st));
  /* THE SPLATTER: opaque ink splats with their tails and satellites, and the torn stains cut through the board */
  meltDots(m.splats, st.drops.length, el, m.drops, { fill: "url(#" + id + "w)" }, "path").forEach((p, i) => {
    const d = st.drops[i], k = st.dropScale;
    p.setAttribute("d", d && d.d > 0 ? meltSplatPath(d.x, d.y, d.r * k, d.a + Math.PI, d.tail * k, rnd, 500 + i) : "");
  });
  meltDots(m.sats, st.sats.length, el, m.drops, { fill: "url(#" + id + "w)" }).forEach((dot, i) => {
    const s = st.sats[i];
    meltCircle(dot, s ? { x: s.x, y: s.y, r: s.r * st.dropScale } : null);
  });
  m.sats.slice(st.sats.length).forEach((dot) => dot.setAttribute("r", "0"));
  meltDots(m.holes, st.stains.length, el, m.stainG, { fill: "#000" }, "path").forEach((p, i) => {
    const s = st.stains[i];
    p.setAttribute("d", s && s.r > 0.2 ? meltSplatPath(s.x, s.y, s.r, 0, 0, rnd, 700 + i) : "");
  });
  m.drops.setAttribute("opacity", st.dropAlpha.toFixed(3));
  /* THE BOARD: the outgoing world, its ink hidden - up, then painted through, then gone */
  wA.style.zIndex = 3;
  wA.style.opacity = st.boardUp ? st.cover.toFixed(4) : "0";
  const rev = st.reveal ? "url(#" + id + "r)" : "";
  wA.style.mask = rev; wA.style.webkitMaskImage = rev;
  /* THE PLATE springs up as it is painted */
  if (wB && st.spring !== 1) {
    wB.style.transformOrigin = "50% 50%";
    wB.style.transform = "scale(" + st.spring.toFixed(4) + ") " + wB.style.transform;
    m.sprung = wB;
  }
  return st;
};

/* the reset, called on every frame that is NOT a melt - it touches only what the painter set */
export const clearMelt = (wA) => {
  if (!wA.__melt) return;
  const m = wA.__melt;
  if (m.svg && m.svg.parentNode) m.svg.parentNode.removeChild(m.svg);
  if (m.ink && m.ink.parentNode) m.ink.parentNode.removeChild(m.ink);
  if (m.txt && m.txt.parentNode) m.txt.parentNode.removeChild(m.txt);
  if (m.sprung && m.sprung.style.transformOrigin) m.sprung.style.transformOrigin = "";
  wA.__melt = null;
  wA.classList.remove("meltboard");
  wA.style.mask = ""; wA.style.webkitMaskImage = "";
  if (wA.style.zIndex) wA.style.zIndex = "";
  if (wA.style.opacity !== "") wA.style.opacity = "";
  if (wA.style.transformOrigin) wA.style.transformOrigin = "";
};
