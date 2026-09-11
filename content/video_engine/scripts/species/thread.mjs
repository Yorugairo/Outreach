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

export const THREAD = Object.freeze({
  ALPHA: 0.34,      /* what the carried mark settles at: present enough to be the same line, faint enough that the new page's ink is the subject */
  FROM: 0.85,       /* ... and what it starts at on the page's first frame - it was the SUBJECT one frame ago, so it does not appear already dimmed */
  FADE_S: 0.9,      /* the recede, over the new page's cream: the wire is handed over, not cut away */
  WIDTH: 0.62,      /* its stroke, as a share of the width the source drew it at: a ground line is thinner than an argument */
  MIN_PTS: 2,       /* fewer than two points is not a line, and nothing is carried */
});

const th01 = (v) => Math.min(1, Math.max(0, v));

/* THE FIT of one chart: its viewBox (vw x vh) contained in its stage box, uniform scale, centred. */
export const threadFit = (box, vw, vh) => {
  const s = Math.min(box.w / Math.max(1e-6, vw), box.h / Math.max(1e-6, vh));
  return { s, tx: box.x + (box.w - vw * s) / 2, ty: box.y + (box.h - vh * s) / 2 };
};

/* a point in a chart's own units -> stage px, and back: each other's inverse to the bit */
export const threadToStage = (fit, p) => [fit.s * p[0] + fit.tx, fit.s * p[1] + fit.ty];
export const threadToLocal = (fit, q) => [(q[0] - fit.tx) / fit.s, (q[1] - fit.ty) / fit.s];

/* THE CARRY: the outgoing page's polyline, in the incoming page's units, standing on the same pixels. */
export const threadCarry = (pts, srcFit, dstFit) => {
  if (!Array.isArray(pts) || pts.length < THREAD.MIN_PTS) return null;
  return pts.map((p) => threadToLocal(dstFit, threadToStage(srcFit, p)));
};

/* the stroke width that carries with it: the source's width through both fits, thinned to a ground line */
export const threadWidth = (w, srcFit, dstFit) => Math.max(1, (+w || 4) * (srcFit.s / Math.max(1e-6, dstFit.s)) * THREAD.WIDTH);

/* THE POSE at the page's own clock: already drawn at the first frame, receding to a ground line. */
export const threadPose = (tr) => {
  const k = th01((+tr || 0) / THREAD.FADE_S);
  return { drawn: 1, alpha: THREAD.FROM + (THREAD.ALPHA - THREAD.FROM) * k };
};

/* the path data for a carried polyline - a plain polyline, because it IS the line that was drawn, not a new curve */
export const threadPath = (pts) => (!pts || pts.length < THREAD.MIN_PTS) ? ""
  : pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(2) + " " + p[1].toFixed(2)).join(" ");
