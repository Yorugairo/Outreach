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
import { cadence, stepped } from "../kinetics/stopaction.mjs";

export const BREAK = Object.freeze({
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
export const breakPlaceholder = (secs, o = {}) => {
  const P = Object.assign({}, BREAK, o);
  const k = secs < 0 ? 1 : bt01(1 - secs / Math.max(1e-6, P.PH_OUT_S));
  return { on: secs < 0, k, alpha: P.PH_ALPHA * k, text: P.PH_TEXT };
};

/* the grey track BEHIND the breaking bar: the comparator's height at the bar's own x, never more.
   `yComp` is the comparator's level in the chart's viewBox (my(comp)), `base` the zero baseline. */
export const breakTrack = (x, bw, base, yComp) => ({
  x, w: bw, y: Math.min(base, yComp), h: Math.max(3, Math.abs(base - yComp)),
});

/* THE MARK. The track alone shows nothing - the bar builds to exactly its height and covers it within a
   fifth of a second - so the placeholder's "?" is written where the NUMBER will be: centred over the
   track's top edge, at the value label's own offset `dy`. The count that would otherwise stand there is
   held back until the number is spoken, so the page carries one mark, not two. */
export const breakStamp = (track, dy) => ({ x: track.x + track.w / 2, y: track.y - dy });

/* ---- THE AXIS CAPSULE -----------------------------------------------------------------------
   ON THE AXIS under the bar's end: its x is the bar's centre (the caller's), its y the zero
   baseline plus a pad. `capH` is the pill's own height - the x-label it displaces goes under it. */
export const breakCapsule = (base, capH, o = {}) => {
  const P = Object.assign({}, BREAK, o);
  return { y: base + P.CAP_PAD, h: capH, labY: base - P.CAP_LAB_UP };
};

/* THE AXIS MOUNT'S BOX. The capsule has only the band between the zero line and the bottom of the chart's
   own box to live in; below that is the page's source line. So it SHRINKS to its band - the box, the
   baseline inside it and the type all by the same factor `k` - and never below CAP_MIN_H. On a landscape
   page the band is 110 units against a 42-unit pill: k is 1 and nothing changes. `cap` is the builder's
   own pill box { w, h, ty, rx }; `chartH` the chart's viewBox height. */
export const breakCapsuleFit = (base, chartH, cap, o = {}) => {
  const P = Object.assign({}, BREAK, o);
  const band = Math.max(0, chartH - P.CAP_FLOOR - (base + P.CAP_PAD));
  /* the floor RAISES a capsule the band would crush; it never enlarges one the page asked to be small
     (a landscape pill is 42 units by design and its band is 110 - the fit must leave it alone) */
  const h = Math.min(cap.h, Math.max(P.CAP_MIN_H, band));
  const k = h / Math.max(1e-6, cap.h);
  return { y: base + P.CAP_PAD, h, k, ty: cap.ty * k, rx: Math.min(cap.rx, h / 2), labY: base - P.CAP_LAB_UP };
};

/* where the leader runs: clear of the bar, on the side that has room inside the plot */
export const breakLeaderX = (bx, bw, x0, o = {}) => {
  const P = Object.assign({}, BREAK, o);
  return bx - P.CAP_LEAD_DX >= x0 ? bx - P.CAP_LEAD_DX : bx + bw + P.CAP_LEAD_DX;
};

/* the dotted leader from the bar's END down to the capsule, or null when there is no room for one
   (a bar whose tip has not cleared the capsule would be pointing at itself) */
export const breakLeader = (cx, tipY, capY, o = {}) => {
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
export const burstSpeed = (plot, lo, hi0, hi1, comp, v, run_s) => {
  const y = (val, hi) => (val - lo) / ((hi - lo) || 1) * plot;
  return Math.abs(y(v, hi1) - y(comp, hi0)) / Math.max(1e-6, run_s);
};

export const burstCadence = (plot, lo, hi0, hi1, comp, v, run_s, o = {}) =>
  cadence(burstSpeed(plot, lo, hi0, hi1, comp, v, run_s), "translate", o);

/* THE STEPPED CLOCK. stopaction's `stepped` short-circuits hold <= 1 and returns t unchanged,
   because it assumes the renderer's own clock IS the cadence clock (a 24 fps renderer seeking at
   frame / fps is already on 1s). Ours is not: render_episode.py delivers 30 fps, so an on-1s burst
   left unquantised is the continuous one. The frame index is therefore taken here (HF-1:
   frame = round(t * fps), step = floor(frame / hold)) and `stepped` is used verbatim for hold > 1,
   where the two are the same formula. */
export const breakStep = (t, hold = 1, fps = BREAK.STEP_FPS) => {
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
export const burstClock = (run, run_s, settle_s, cad = null) => {
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
