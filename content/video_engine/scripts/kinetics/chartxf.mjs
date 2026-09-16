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
export const xfLerp = (a, b, u) => { u = Math.min(1, Math.max(0, u)); return a + (b - a) * u; };

/* xfPoint - a datum's screen position between two scales. mapA / mapB take the DATUM (x, v) and return [px, py]; the
   datum never changes, only where the scale puts it - so a point outside B's window still has a position under B
   (past the plot's edge), which is where it travels to while it fades. */
export const xfPoint = (x, v, mapA, mapB, u) => {
  const a = mapA(x, v), b = mapB(x, v);
  return [xfLerp(a[0], b[0], u), xfLerp(a[1], b[1], u)];
};

/* xfPath - a series' whole path between two scales, as the point list and the SVG `d` the caller writes. */
export const xfPath = (pts, mapA, mapB, u) => {
  const out = pts.map(([x, v]) => xfPoint(x, v, mapA, mapB, u));
  return { pts: out, d: out.map(([px, py], k) => (k ? "L" : "M") + px.toFixed(1) + " " + py.toFixed(1)).join(" ") };
};

/* xfFade - the opacity of a mark keyed by VALUE as the domain moves. A mark whose value is inside the target domain
   holds; one leaving fades over the first LEAVE share of the clock; one arriving (present only in B) fades in over the
   last ARRIVE share. Both edges clamp so the ends are exact: at u=0 an arriving mark is invisible, at u=1 a leaving
   one is. */
export const XF = Object.freeze({
  LEAVE: 0.5,    /* a leaving tick is gone by half the clock - it should not travel the whole way as a ghost [DERIVED: E28, the axis must read at every t] */
  ARRIVE: 0.5,   /* an arriving tick appears over the second half, at its settled place */
});
export const xfFade = (inside, arriving, u) => {
  u = Math.min(1, Math.max(0, u));
  if (arriving) return inside ? Math.min(1, Math.max(0, (u - (1 - XF.ARRIVE)) / XF.ARRIVE)) : 0;
  return inside ? 1 : Math.max(0, 1 - u / XF.LEAVE);
};

/* xfInside - is a value within a domain [lo, hi] (either order), with a hair of tolerance for the tick that sits on
   the edge (a nice-step tick at exactly the domain's end is part of the axis, not outside it). */
export const xfInside = (v, lo, hi) => {
  const a = Math.min(lo, hi), b = Math.max(lo, hi), eps = (b - a) * 1e-6;
  return v >= a - eps && v <= b + eps;
};

/* xfRect - a bar between two states: every edge lerps, so a bar that grows keeps its baseline and a bar that moves keeps
   its width law. geom is {x, y, w, h}. */
export const xfRect = (ga, gb, u) => ({ x: xfLerp(ga.x, gb.x, u), y: xfLerp(ga.y, gb.y, u), w: xfLerp(ga.w, gb.w, u), h: xfLerp(ga.h, gb.h, u) });

/* ---- P61 T2 - THE WHOLE-CHART REMAKE -----------------------------------------------------------------------------
   A full chart becomes a full chart on one clock. The law: every KEYED datum of the source owns a share of the source's
   own ink, and that share becomes its counterpart's - a datum's column of the area under a line becomes its bar, a bar
   becomes its datum's column. Both shares are described as ONE ring, built column by column in one order (lpStrip's own
   shape, E:9761), so morph_a corresponds them with `resample: false, normalise: false` and returns offset 0 - the
   remake adds no pairing law of its own, it hands morph_a two descriptions that already correspond.
   E99 s34, the bar: a viewer sees ONE thing becoming the next, and sees it as meant. Nothing here fades. */
export const REMAKE = Object.freeze({
  COLS: 8,        /* the columns a datum's share is described by: 8 per side is 16 vertices a bar's rectangle is still exactly a rectangle at, and the line's own leg inside one datum's share is straight [DERIVED: MORPH.COLS 48 describes a WHOLE line; a column of it needs the corner, not the curve] */
  LEAVE: 0.28,    /* the share of the clock the source's own ink takes to leave into its area (XF_MORPH.LEAVE 0.3's law, one notch earlier because the travel is longer here) */
  TRAVEL: 0.9,    /* every ring has landed on its counterpart by here - the clock's last tenth belongs to the target's own ink (KEYED_TAG_HAND 0.92's law: hand over on the CLOCK, not on the eased travel) */
});

/* xfSpanTop - n points along a POLYLINE between two x, at the polyline's own y (lpStrip's yAt, sampled over a span
   rather than the whole line). Outside the polyline the end value holds: a datum's share may reach past the last
   datum, and a straight continuation invents a number the page never drew. */
export const xfSpanTop = (pts, x0, x1, n) => {
  const P = (pts || []).filter((q) => q && q.length >= 2);
  const yAt = (x) => {
    if (!P.length) return 0;
    if (x <= P[0][0]) return P[0][1];
    for (let i = 0; i + 1 < P.length; i++) {
      const a = P[i], b = P[i + 1];
      if (x >= a[0] - 1e-9 && x <= b[0] + 1e-9) {
        const u = (x - a[0]) / Math.max(1e-9, b[0] - a[0]);
        return a[1] + (b[1] - a[1]) * Math.min(1, Math.max(0, u));
      }
    }
    return P[P.length - 1][1];
  };
  const m = Math.max(2, n | 0);
  return [...Array(m).keys()].map((i) => { const x = x0 + (i / (m - 1)) * (x1 - x0); return [x, yAt(x)]; });
};

/* xfStripRing - the closed ring of a strip: its top row left to right, then its bottom row right to left. The two rows
   share their x, so the ring's i-th vertex is the i-th column on both sides of any pair built this way. */
export const xfStripRing = (top, bot) => [...top, ...bot.slice().reverse()];

/* xfBarRing - a bar described as the same ring: n points along its VALUE edge, n along its base. A negative bar's
   value edge is the one BELOW its base (geom.neg), so the ring is the same description upside down and the morph
   carries the sign instead of flipping it. */
export const xfBarRing = (g, n) => {
  const m = Math.max(2, n | 0), x0 = +g.x, x1 = +g.x + +g.w;
  const base = g.base != null ? +g.base : +g.y + +g.h;
  const edge = g.end != null ? +g.end : (g.neg ? base + Math.abs(+g.h) : base - Math.abs(+g.h));
  const xs = [...Array(m).keys()].map((i) => x0 + (i / (m - 1)) * (x1 - x0));
  return xfStripRing(xs.map((x) => [x, edge]), xs.map((x) => [x, base]));
};

/* xfRingPath - the ring as a closed POLYLINE. Deliberately not morph_a's cubic reconstruction: a bar's rectangle
   drawn as a centripetal Catmull-Rom is a rectangle with rounded corners, and the remake hands the landed ring over
   to the page's own <rect> - the two must be the same shape or the hand-over is the cut this verb exists to avoid. */
export const xfRingPath = (pts) => (!pts || !pts.length ? ""
  : pts.map((p, i) => (i ? "L" : "M") + (+p[0]).toFixed(1) + " " + (+p[1]).toFixed(1)).join(" ") + " Z");

/* xfRemakeClock - ONE clock, three shares of it, for the LINE -> BARS run. `leave`: the source's own ink into its
   area. `travel`: every ring onto its counterpart, ending at REMAKE.TRAVEL where the target's own bars take over.
   `hand`: the target's own ink taking the rings' place. Exact at both ends by construction, and every phase is a pure
   function of u - the caller eases each one. The other run has its own clock (xfRemakeLineClock): E99 s39 ruled that
   bars -> line is NOT this travel read backwards. */
export const xfRemakeClock = (u) => {
  const c = Math.min(1, Math.max(0, u)), cl = (v) => Math.min(1, Math.max(0, v));
  return {
    leave: cl(c / REMAKE.LEAVE),
    travel: cl((c - REMAKE.LEAVE) / (REMAKE.TRAVEL - REMAKE.LEAVE)),
    hand: cl((c - REMAKE.TRAVEL) / (1 - REMAKE.TRAVEL)),
  };
};

/* the two beats INSIDE the travel, so the ink is never in two places at once: `ink` is the share of the travel over
   which the source's own stroke drops into its columns (the tail leaves as they fill), and `move` is the share after
   which the shapes have any distance to cover. They overlap - nothing waits, which is E64's own word for it. */
export const REMAKE_BEAT = Object.freeze({ INK: 0.35, MOVE: 0.2 });
export const xfRemakeTravel = (travel) => ({
  ink: Math.min(1, Math.max(0, travel / REMAKE_BEAT.INK)),
  move: Math.min(1, Math.max(0, (travel - REMAKE_BEAT.MOVE) / (1 - REMAKE_BEAT.MOVE))),
});

/* ---- P61 T2b - BARS -> LINE: COLLAPSE TO THE APEX, THEN DRAW BACK TO THE ROOT (E99 s39) --------------------------
   The operator, on T2's first build: *"for bars-> line I'd like to see it all collapse to the single apex point and
   then draw the line back to the root instead of sliding and snapping together and the whole line is formed -- if the
   whole thing is magically formed that is basically a snap/cut, and not the morph we're looking for. A morph should be
   proof of form/function to the audience, that we're really manipulating the world they're watching, not tricking
   them."* So this run does NOT read the line -> bars travel backwards. It has its own clock and three beats: every
   bar's ring GATHERS into one point at the apex (the highest bar's top), that point SETTLES where the arriving line's
   own apex datum stands, and the page's own stroke DRAWS from there back to the root.
   WHY NOT morph_a, which carries the other run: a correspondence machine needs two rings, and the destination here is
   one POINT - an ARAP fit onto a zero-area ring is undefined (its polar decomposition divides by a vanishing area),
   while a ring's own vertices lerping to a point is exact, pure and free. The ring machinery still says WHAT collapses
   (xfBarRing describes the bar exactly as it does on the other run); only the destination is not another ring. */
export const REMAKE_LINE = Object.freeze({
  GATHER: 0.24,   /* the share of the clock every bar's ink takes to reach the apex [DERIVED: 0.58 s of the goldens' 2.4 s row - one decisive gather, and the clock's REST belongs to the draw, which is what the ruling is about] */
  SETTLE: 0.32,   /* by here the gathered point has carried itself from the highest bar's top to the arriving line's own apex datum - the two are not the same place (135 px apart on the golden's pages), and the line must start where IT stands */
  SPREAD: 0.25,   /* the stagger across the rings: the one FARTHEST from the apex leaves first and every ring lands together, so the gather has a direction rather than five independent shrinks [DERIVED: E99 s34, "it reads as intentional"] */
  HOLD: 0.86,     /* the apex point stands until here - it is what the line came out of - and leaves over the last share as the target's own ink takes the frame (KEYED_TAG_HAND 0.92's law, one notch earlier because a dot is larger than a glyph) */
});

/* xfRemakeLineClock - the bars -> line clock: `gather`, `settle`, `draw`, `hand`. Exact at both ends, pure in u. */
export const xfRemakeLineClock = (u) => {
  const c = Math.min(1, Math.max(0, u)), cl = (v) => Math.min(1, Math.max(0, v));
  return {
    gather: cl(c / REMAKE_LINE.GATHER),
    settle: cl((c - REMAKE_LINE.GATHER) / (REMAKE_LINE.SETTLE - REMAKE_LINE.GATHER)),
    draw: cl((c - REMAKE_LINE.SETTLE) / (1 - REMAKE_LINE.SETTLE)),
    hand: cl((c - REMAKE_LINE.HOLD) / (1 - REMAKE_LINE.HOLD)),
  };
};

/* xfGatherK - one ring's own share of the gather. `rank` 0 is the ring FARTHEST from the apex: it starts first because
   it has the farthest to travel, and every ring lands exactly together at the gather's end (so the collapse ends as ONE
   point, not as a queue). spread 0 is every ring on the same clock. */
export const xfGatherK = (k, rank, n, spread) => {
  const s = Math.min(0.9, Math.max(0, spread == null ? REMAKE_LINE.SPREAD : spread));
  const d = n > 1 ? s * (Math.min(n - 1, Math.max(0, rank)) / (n - 1)) : 0;
  return Math.min(1, Math.max(0, (k - d) / (1 - d)));
};

/* xfRingTo - every vertex of a ring to ONE point. At k = 1 the ring IS that point: zero area, so it carries no ink -
   nothing is faded out and nothing is left behind, which is the difference between a collapse and a dissolve. */
export const xfRingTo = (pts, p, k) => (pts || []).map((q) => [xfLerp(q[0], p[0], k), xfLerp(q[1], p[1], k)]);

/* xfDrawWindow - the stroke's visible interval as SHARES of the path's length, growing out of the apex: the root side
   (the ruling's own direction) and, when the apex is not the last datum, the far side with it, so the ends are exact -
   k = 0 is the bare point at `apex`, k = 1 is the whole path. The caller writes it with the page's own dash pair
   (dasharray from the path's length, a negative dashoffset starting the window: the engine's own window form). */
export const xfDrawWindow = (apex, k) => {
  const a = Math.min(1, Math.max(0, apex)), c = Math.min(1, Math.max(0, k));
  return { s: a * (1 - c), e: a + (1 - a) * c };
};
