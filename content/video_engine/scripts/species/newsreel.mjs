/* SPACE: stage */
/* species/newsreel.mjs - THE NEWSREEL BAND (P52 T6; the operator, 2026-09-12: "run the newsreel and then above it
   we can have either a talking news head, actual news footage, or a narrative plate, we don't always have to fill
   the whole thing with text"). SOURCE OF TRUTH, inlined into the scene-evidence engine by sync_kinetics.py between
   KINETICS:BEGIN newsreel and KINETICS:END, AFTER spring (it uses springPop) and after the SPECIES_PAINTERS
   registry it registers into - the import order IS the region order.

   WHEN: the sentence reports WHAT WAS SAID OR PRINTED - the wire, the headlines, the tape. The band crawls the
   episode's OWN sourced headlines under a surface that shows who said it (a head cutout, a clip, the plate
   itself). It is never the whole frame as text: the band is a strip, and the surface above it is the picture.

   THE THREE MECHANISMS TAKEN from RU-4 (remotion-ui/HARVEST-2026-09-07.md:289; licence [UNVERIFIED], so the
   MECHANISMS are taken and no line of that code is quoted - and none of its look: no broadcast-dark chrome, no
   flag block, no Inter-as-brand; our tokens - cream, charcoal, coral - and our type):
     1. the SEAM-FREE WRAP - two copies of one run chasing each other against a STABLE upper-bound width, modulo
        (`crawlX`): the run is measured ONCE per paint and the second copy sits exactly `width` to its right, so
        the instant the first copy's tail leaves the band the second is already under the eye. No seam, ever.
     2. the GRADIENT DISSOLVE at the crawl's RIGHT edge (`edgeStops`, a mask): a headline does not get cut off by
        a hard line, it goes out of the light. The LEFT edge is hard - it is the column the head / clip stands in.
     3. `hold` as a LIFE on a standing element: the band stands for the window the author gives it and then
        RETREATS over BEATS.EXIT_FOR (`reelPose`), instead of being up for the species' whole `dur`.

   THE LAW, all of it a pure function of t (a scrubbed frame IS the played frame - nothing is stored, nothing
   reads a clock, nothing reads the DOM for time):
     open   - the band opens from a hairline at its own BOTTOM edge over BEATS.BAR_FOR on the house spring
              (kinetics/spring.mjs springPop) - a strip that grows out of the frame's edge, never a fade-in.
     crawl  - from BEATS.CRAWL on, the run moves left at `speed_px_s` (NEWSREEL.SPEED by default) and wraps by
              the modulo above. The crawl IS the band's life: nothing here ever goes still (E49).
     strap  - the strapline WRITES left to right over BEATS.STRAP_FOR from BEATS.STRAP (a reveal, our hand's
              direction), under the crawl, one size down.
     date   - the dateline the AUTHOR wrote, pinned right in the de-emphasised ink. No clock is ever invented.
     exit   - when `hold` ends the band retreats over BEATS.EXIT_FOR the way it opened, and is gone.
   The headlines are the episode's own SOURCED titles (the dossier's Sources, or the clips' on-screen headlines in
   candidates.json) - this module never invents a headline, and the compiler refuses an empty one. The dials below
   are ours to tune (doc 42 s42.5), not findings. */
import { springPop } from "../kinetics/spring.mjs";

export const NEWSREEL = Object.freeze({
  SPEED: 140,        /* px per second of the STAGE [DERIVED: RU-4's default, re-read on our 1920 stage: a 60-char headline crosses in ~8 s, which is a read, not a tease] */
  BAND_H: 0.14,      /* the band's height as a share of the STAGE height - the recommended region; the author's declared region is the truth */
  GAP: 88,           /* the air between the run's last item and its own repeat, in stage px */
  BULLET: "•",  /* the house bullet between headlines (the middot is the docs' mark; the bullet is the tape's) */
  EDGE: 0.12,        /* the gradient dissolve at the RIGHT edge, as a share of the band's width */
  PAD_X: 34,         /* the crawl's inset from the band's left edge (the hard edge under the head's column) */
  TAB_W: 12,         /* the coral tab on that hard left edge - our token, in place of RU-4's flag block */
  CRAWL_ROW: 0.56,   /* the crawl's baseline, as a share of the band's height */
  STRAP_ROW: 0.88,   /* ... and the strapline's, under it */
  TYPE: 0.7,         /* the crawl's type as a share of the caption's stage size (64 px -> 45): the tape is read at a glance, the caption is the voice */
  STRAP_TYPE: 0.56,  /* ... and the strap one size down */
  DEEMPH: 0.62,      /* what the dateline and the strap dim to - present, never competing with the headline */
  HAIRLINE: 0.04,    /* the share of its height the band opens FROM (a line of ink on the frame's edge, not nothing) */
  EST_PX_PER_CHAR: 0.52,   /* the measure-free estimate: a share of the type size per character, for node and for a caller with no text metrics [DERIVED: Inter's average advance] */
  BEATS: Object.freeze({   /* RU-4's beat plan as a named table in seconds, ours to re-time */
    BAR: 0,            /* the band starts opening on the species' own `at` */
    BAR_FOR: 0.42,     /* ... and is open this long after */
    CRAWL: 0.4,        /* the run starts moving here - inside the open, so the band is never a still strip */
    STRAP: 0.46,       /* the strapline starts writing here - after the band is open */
    STRAP_FOR: 0.5,    /* ... and takes this long to write */
    EXIT_FOR: 0.38,    /* the retreat, when `hold` ends */
  }),
  COL: Object.freeze({     /* the tokens the template already defines, each with its own value as the fallback so the
                              band paints the same inside a page's scope as on a plate (the module names no new token) */
    BAND: "var(--cream, #F4E6C7)",
    INK: "var(--charcoal, #25313C)",
    TAB: "var(--coral, #ED6A4A)",
  }),
});

const nr01 = (v) => Math.min(1, Math.max(0, v));

/* THE RUN: the author's headlines with the house bullet between them. A non-string or an empty headline never
   reaches here - the compiler refuses the row (validate_species) - and this filters anyway. */
export const reelItems = (sp) => (Array.isArray(sp && sp.headlines) ? sp.headlines : [])
  .filter((h) => typeof h === "string" && h.trim()).map((h) => h.trim());
export const reelRun = (items, o = {}) => {
  const P = Object.assign({}, NEWSREEL, o);
  return items.join("   " + P.BULLET + "   ");
};

/* THE STABLE UPPER BOUND the wrap runs against: the run's own measured width plus one GAP, so the repeat starts a
   gap after the run ends. `measure` is the caller's text metric (the painter hands it getComputedTextLength);
   without one the estimate is used, which is what node and a metric-less caller get - and it is an upper bound on
   the run, never a fraction of it, so two copies can only ever be further apart than they need to be. */
export const reelWidth = (items, measure, o = {}) => {
  const P = Object.assign({}, NEWSREEL, o), run = reelRun(items, P);
  if (!run) return 0;
  const w = typeof measure === "function" ? measure(run) : null;
  const est = run.length * P.EST_PX_PER_CHAR * (P.SIZE || Math.round(64 * P.TYPE));
  return (Number.isFinite(w) && w > 0 ? w : est) + P.GAP;
};

/* THE MODULO WRAP: where the run's first copy sits at the crawl's own clock `tc`. The second copy is drawn at this
   + width, so the tape is seamless - `crawlX(tc + width / speed) === crawlX(tc)` (to the float, sub-pixel). */
export const crawlX = (tc, width, speed) => {
  if (!(width > 0)) return 0;
  const v = Number.isFinite(speed) && speed > 0 ? speed : NEWSREEL.SPEED;
  return -((((tc * v) % width) + width) % width);
};

/* THE SPEED the row runs at: the author's `speed_px_s`, else the dial. Never zero (a still tape is not a tape). */
export const reelSpeed = (sp, o = {}) => {
  const P = Object.assign({}, NEWSREEL, o), v = +(sp && sp.speed_px_s);
  return Number.isFinite(v) && v > 0 ? v : P.SPEED;
};

/* THE WINDOW the band stands for: its `hold` when the author gave it one (the LIFE), else the species' `dur`. */
export const reelStand = (sp) => {
  const hold = +(sp && sp.hold);
  return Number.isFinite(hold) && hold > 0 ? hold : Math.max(0, +(sp && sp.dur) || 0);
};

/* ONE ENTRY: everything the painter draws at t, from the declaration alone.
   `open` is the band's vertical scale about its own bottom edge, `crawl` the crawl's clock in seconds, `strap` the
   write's fraction, `exit` the retreat's fraction, `on` whether the band is up at all. */
export const reelPose = (sp, t, o = {}) => {
  const P = Object.assign({}, NEWSREEL, o), B = P.BEATS;
  const rel = t - +sp.at, stand = reelStand(sp);
  const exit = nr01((rel - stand) / B.EXIT_FOR);
  const grow = springPop(nr01((rel - B.BAR) / B.BAR_FOR));
  const open = P.HAIRLINE + (1 - P.HAIRLINE) * grow * (1 - exit);
  return {
    rel,
    on: rel >= 0 && exit < 1,
    open: rel < 0 ? 0 : open,
    crawl: Math.max(0, rel - B.CRAWL),
    strap: nr01((rel - B.STRAP) / B.STRAP_FOR) * (1 - exit),
    exit,
    alpha: rel < 0 ? 0 : 1 - exit,
  };
};

/* the right edge's dissolve, as mask stops: opaque until 1 - EDGE, gone at the band's right edge. A stable id per
   species index, so two bands in one window never share a mask (and a seek re-creates the same one). */
export const edgeId = (si) => "nredge" + (si | 0);
export const edgeStops = (o = {}) => {
  const P = Object.assign({}, NEWSREEL, o);
  return [{ offset: 0, stop: 1 }, { offset: 1 - P.EDGE, stop: 1 }, { offset: 1, stop: 0 }];
};

/* THE PAINTER. ctx is the engine's species context (see SPECIES_PAINTERS in the player): the declaration, the
   clock, the layer and the shared helpers by name. One group at the declared region: a cream strip on the world's
   charcoal, charcoal type, the dissolve a mask on the crawl alone, the whole band scaled about its own foot. */
export function paintNewsreel(ctx) {
  const { sp, t, svg, el, resolveTarget, si } = ctx;
  const b = resolveTarget(sp.target);
  if (!b || b.w <= 0 || b.h <= 0) return;   /* the targeting law: no resolved region, nothing painted */
  const pose = reelPose(sp, t);
  if (!pose.on) return;
  const items = reelItems(sp);
  if (!items.length) return;                /* the compiler refuses this row; the painter draws no empty band */
  const size = Math.round(64 * NEWSREEL.TYPE), strapSize = Math.round(64 * NEWSREEL.STRAP_TYPE);
  const run = reelRun(items);
  const id = edgeId(si), clip = id + "clip";
  const foot = b.y + b.h;
  const g = el("g", "nreel", svg, {
    opacity: pose.alpha.toFixed(3),
    transform: "translate(0 " + foot.toFixed(1) + ") scale(1 " + pose.open.toFixed(4) + ") translate(0 " + (-foot).toFixed(1) + ")",
  });
  const defs = el("defs", "", g);
  const mask = el("mask", "", defs, { id, maskUnits: "userSpaceOnUse", x: b.x.toFixed(1), y: b.y.toFixed(1), width: b.w.toFixed(1), height: b.h.toFixed(1) });
  const lg = el("linearGradient", "", mask, { id: id + "g", x1: b.x.toFixed(1), y1: 0, x2: (b.x + b.w).toFixed(1), y2: 0, gradientUnits: "userSpaceOnUse" });
  edgeStops().forEach((s) => el("stop", "", lg, { offset: s.offset.toFixed(3), "stop-color": "#fff", "stop-opacity": s.stop }));
  el("rect", "", mask, { x: b.x.toFixed(1), y: b.y.toFixed(1), width: b.w.toFixed(1), height: b.h.toFixed(1), fill: "url(#" + id + "g)" });
  const cp = el("clipPath", "", defs, { id: clip, clipPathUnits: "userSpaceOnUse" });
  el("rect", "", cp, { x: (b.x + NEWSREEL.PAD_X).toFixed(1), y: b.y.toFixed(1), width: Math.max(1, b.w - NEWSREEL.PAD_X).toFixed(1), height: b.h.toFixed(1) });
  /* the band itself: cream paper on the world, a charcoal hairline at its head, the coral tab on its hard left edge */
  el("rect", "nrband", g, { x: b.x.toFixed(1), y: b.y.toFixed(1), width: b.w.toFixed(1), height: b.h.toFixed(1), style: "fill: " + NEWSREEL.COL.BAND });
  el("rect", "nrrule", g, { x: b.x.toFixed(1), y: b.y.toFixed(1), width: b.w.toFixed(1), height: 3, style: "fill: " + NEWSREEL.COL.INK + "; opacity: .34" });
  el("rect", "nrtab", g, { x: b.x.toFixed(1), y: b.y.toFixed(1), width: NEWSREEL.TAB_W, height: b.h.toFixed(1), style: "fill: " + NEWSREEL.COL.TAB });
  /* the crawl: one measured run, two copies a width apart, the whole thing masked at the right edge */
  const crawl = el("g", "nrcrawl", g, { mask: "url(#" + id + ")", "clip-path": "url(#" + clip + ")" });
  const y = (b.y + b.h * NEWSREEL.CRAWL_ROW).toFixed(1);
  const face = "font: 700 " + size + "px Inter, Arial, sans-serif; fill: " + NEWSREEL.COL.INK;
  const first = el("text", "nrrun", crawl, { x: 0, y, style: face, "xml:space": "preserve" });
  first.textContent = run;
  const measured = typeof first.getComputedTextLength === "function" ? first.getComputedTextLength() : null;
  const width = reelWidth(items, () => measured, { SIZE: size });
  const x0 = crawlX(pose.crawl, width, reelSpeed(sp));
  const left = b.x + NEWSREEL.PAD_X;
  first.setAttribute("x", (left + x0).toFixed(2));
  const second = el("text", "nrrun", crawl, { x: (left + x0 + width).toFixed(2), y, style: face, "xml:space": "preserve" });
  second.textContent = run;
  if (crawl.setAttribute) crawl.setAttribute("data-reelw", width.toFixed(2));   /* the probe's handle: the wrap's period is width / speed */
  /* the strapline WRITES from the left under the crawl; the dateline is pinned right in the de-emphasised ink */
  if (sp.strap && pose.strap > 0) {
    const wid = Math.max(1, (b.w - NEWSREEL.PAD_X * 2) * pose.strap);
    const scp = el("clipPath", "", defs, { id: id + "strap", clipPathUnits: "userSpaceOnUse" });
    el("rect", "", scp, { x: left.toFixed(1), y: b.y.toFixed(1), width: wid.toFixed(1), height: b.h.toFixed(1) });
    const st = el("text", "nrstrap", el("g", "", g, { "clip-path": "url(#" + id + "strap)" }), {
      x: left.toFixed(1), y: (b.y + b.h * NEWSREEL.STRAP_ROW).toFixed(1),
      style: "font: 700 " + strapSize + "px Inter, Arial, sans-serif; fill: " + NEWSREEL.COL.INK + "; opacity: " + NEWSREEL.DEEMPH,
    });
    st.textContent = sp.strap;
  }
  if (sp.dateline) {
    const dl = el("text", "nrdate", g, {
      x: (b.x + b.w - NEWSREEL.PAD_X).toFixed(1), y: (b.y + b.h * NEWSREEL.STRAP_ROW).toFixed(1), "text-anchor": "end",
      style: "font: 700 " + strapSize + "px Inter, Arial, sans-serif; fill: " + NEWSREEL.COL.INK + "; opacity: " + NEWSREEL.DEEMPH,
    });
    dl.textContent = sp.dateline;
  }
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can import
   this file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.newsreel = paintNewsreel;
