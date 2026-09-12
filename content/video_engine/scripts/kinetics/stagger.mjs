/* kinetics/stagger.mjs - THE CAPTION'S ARRIVAL AS ONE ENVELOPE (P52 T10). SOURCE OF TRUTH, inlined into the
   scene-evidence player by sync_kinetics.py between KINETICS:BEGIN stagger and KINETICS:END, AFTER ease (it uses
   minJerk) and BEFORE the caption block that calls it. Registers no painter: this is a law, not a species.

   [DERIVED: HyperFrames staggered-fade-up] (content/video_engine/hyperframes/HARVEST-2026-09-07.md:27 - "each word is
   a span; ONE timeline drives --hf-word-y 22 px -> 0, scale 0.92 -> 1 and a 5 px blur -> 0 together, stagger 0.055 s").
   The operator on it: "incorporating this might be a solution for how we can have more caption motion without
   overcrowding". That is the whole design brief. Today a stage caption POPS per word (springPop over STAGE_POP_S from
   1.10 with a 6 px rise and a tilt): motion by punctuation, and eight punctuations a page is the crowding. The fade-up
   is the other register - one envelope, per-word offsets, three channels moving together, nothing overshooting.

   TWO laws, and they are separable on purpose:

     staggerStarts(onsets, origin, stagger)   WHEN each word arrives.
         A word arrives on its own spoken onset (E21: captions ARE the motion; the word clock is doctrine and a
         measured take's onsets are the truth) - unless that onset sits closer than `stagger` to the word before it,
         in which case it takes the stagger. So a measured page keeps its voice, and a crowded or estimated page is
         spread into overlapping action: no two words share a start frame (the HyperFrames research blueprint's Rule
         3, docs/research/motion/HYPERFRAMES_MOTION_TRANSITIONS_RESEARCH_BLUEPRINT.md:53). A missing onset falls to the
         previous word plus the stagger; nothing arrives before the page does.

     fadeUpAt(t, start, P)                    WHAT arriving looks like: y RISE_PX -> 0, scale FROM_SCALE -> 1,
         blur BLUR_PX -> 0 px and opacity 0 -> 1, all read off ONE progress e = minJerk((t - start) / DUR_S). Because
         it is one progress, the page cannot desynchronise; because minJerk has zero velocity AND zero acceleration at
         both ends, the word neither snaps in nor sags to a stop. A pure function of t: frame N evaluated cold is the
         frame the scrub gives (the seek test), which is what makes two renders of one second identical.

   The blur is a FILTER ON THE WORD SPAN - never on the strip. A filter on the strip would blur the whole caption
   (and force one composited layer for all of it); per word it is the word's own arrival and it is gone by e = 1.

   The dials: RISE_PX / FROM_SCALE / BLUR_PX / STAGGER_S are the harvest's numbers, unchanged. DUR_S is OURS - the
   envelope has to be longer than the pop (0.2 s) for this to read as an arrival instead of a flash, and longer than
   the stagger so neighbours overlap into one wave rather than a queue of separate events. */

import { minJerk } from "./ease.mjs";

export const FADE_UP = Object.freeze({
  RISE_PX: 22,       /* [DERIVED: HyperFrames staggered-fade-up] --hf-word-y 22 px -> 0 */
  FROM_SCALE: 0.92,  /* [DERIVED: HyperFrames staggered-fade-up] scale 0.92 -> 1 */
  BLUR_PX: 5,        /* [DERIVED: HyperFrames staggered-fade-up] a 5 px blur -> 0, on the word's own span */
  STAGGER_S: 0.055,  /* [DERIVED: HyperFrames staggered-fade-up] stagger 0.055 s = 3.3 frames at 60 fps */
  DUR_S: 0.34,       /* ours: one word's envelope - longer than the pop (0.2 s) and than the stagger, so the page arrives as a wave */
});

/* one preset, overridden as a whole - a caller never passes a half-filled dials object */
export const fadeUpDials = (o) => Object.freeze(Object.assign({}, FADE_UP, o || {}));

/* WHEN: the per-word arrival times. `onsets` is the page's word clock (null / undefined / NaN = unmeasured),
   `origin` the page's own start. Monotone by construction, gaps >= stagger, pure. */
export const staggerStarts = (onsets, origin, stagger = FADE_UP.STAGGER_S) => {
  const out = [];
  for (let j = 0; j < (onsets || []).length; j++) {
    const o = Number(onsets[j]), prev = j ? out[j - 1] : null;
    let s = Number.isFinite(o) && onsets[j] !== null ? o : (prev === null ? origin : prev + stagger);
    if (prev === null) { if (Number.isFinite(origin) && s < origin) s = origin; }
    else if (s < prev + stagger) s = prev + stagger;
    out.push(s);
  }
  return out;
};

/* WHAT: the envelope at t for a word that started at `start` - the four channels off one progress */
export const fadeUpAt = (t, start, P = FADE_UP) => {
  /* e is CLAMPED on top of minJerk: the quintic's binary evaluation overshoots 1 by 4e-16 just under u = 1
     (10 - 15u + 6u^2 at u = 0.9999999999999999), and an envelope whose end is not exactly rest leaves a word
     at y = -9e-15 px and opacity 1.0000000000000004 forever - so the arrival's end is pinned to rest */
  const e = Math.min(1, minJerk((t - start) / P.DUR_S));
  /* the scale is written so BOTH ends are exact - FROM_SCALE at rest and exactly 1 when it has landed
     (0.92 + 0.08 * 1 is 1.0000000000000002 in binary; springPop's "lands on exactly 1" is the house rule) */
  const s = e >= 1 ? 1 : P.FROM_SCALE + (1 - P.FROM_SCALE) * e;
  return { e, o: e, y: P.RISE_PX * (1 - e), s, b: P.BLUR_PX * (1 - e) };
};

/* the whole page at t, in word order */
export const fadeUpPage = (t, starts, P = FADE_UP) => (starts || []).map((s) => fadeUpAt(t, s, P));

/* how long the page spends arriving: the last word's offset plus one envelope (0 when there are no words) */
export const staggerSpan = (starts, P = FADE_UP) =>
  (starts && starts.length ? starts[starts.length - 1] - starts[0] + P.DUR_S : 0);
