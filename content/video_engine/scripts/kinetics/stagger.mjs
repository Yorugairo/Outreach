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
import { springPop } from "./spring.mjs";

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

/* ---- E90: THE CAPTION'S LIFE - the pop LEADS, the stagger's envelope rides UNDER it (P57 T14) ----

   E90 (the operator, P52 human gate 4): "caption pop looks beter than stagger, i think the blend of both makes
   sense, maybe add more pop effect ... what we shipped on steel and paper is still the best we've produced".
   So the base is not replaced and nothing here is a switch: `life` is a caption option with three NAMED settings,
   and its absence is the shipped caption to the bit (no golden and neither approved short authors one).

     pop       the shipped stage pop, one notch stronger - scale POP_LEAD -> 1 on the spring, the word's
               alternating tilt settling to 0. ONE number is different and it is stated: POP_LEAD 1.22
               against the base's 1.16 (E90 s2 "a little stronger").
     stagger   P52 T10's envelope ALONE (fadeUpAt): y RISE_PX -> 0, scale FROM_SCALE -> 1, blur BLUR_PX -> 0
               off one minimum-jerk progress; no tilt, because the tilt is punctuation and this register
               exists to remove punctuation.
     blend     BOTH, composed: the pop's SCALE rides on top of the stagger's Y - the word enters big
               (POP_LEAD) and shrinking on the spring while the envelope's rise carries it up into place, lit
               on the pop's clock. The pop LEADS by construction: it opens ANTICIP_S before the spoken onset
               the stagger starts on (the same 0.05 s anticipation the shipped pop has), so its whole clock is
               spent before the stagger reaches its middle.

               TWO channels of the envelope the blend does NOT take, and the frames are why (the T10 instants
               on Tokyo's private build, 2026-09-14):
                 the stagger's SCALE - two scales multiplied put the word below rest at the onset
                 (1.055 x 0.92 = 0.97), which reads as the quiet register arriving, not as a pop leading;
                 the stagger's BLUR - a 5 px blur at u = 0 is the word unreadable at the instant it is spoken,
                 and on a short the caption IS the read (E21, E62). The blur stays where P52 T10 put it: in
                 the `stagger` setting, which is renderable beside this one so the operator's eye can rule.

   Why springPop and not the engine's back-ease: the composition is the MODULE's, so its pop is the house
   spring (kinetics/spring.mjs, Mp 4 %) - the law the shipped builds already turn on (`analytic_spring`).

   What is NOT here, on purpose (the caption-energy lessons, 2026-09-05: "energy = continuous voice-timed
   motion"): no cursor, no flash, no per-word highlight. Every channel is a continuous function of the word's
   own voice time, and the HELD page's life is E49's - the engine's `idle` kind `breath` on the caption strip,
   reused, never reinvented.

   A pure function of t like everything else in this file: a cold seek lands where a play does. */

export const LIFE = Object.freeze({
  POP_LEAD: 1.22,     /* ours (E90 s2): the pop's start scale under a life setting - the base's 1.16 plus one notch */
  POP_S: 0.20,        /* the shipped stage pop's window, unchanged (the engine's STAGE_POP_S) */
  ANTICIP_S: 0.05,    /* the shipped pop's anticipation - it opens this much before the onset, which is HOW the pop leads */
  OPACITY_K: 2,       /* the shipped opacity ramp: opaque by the pop's half - min(1, e * K) */
  MP: 0.04,           /* the house overshoot (kinetics/spring.mjs SPRING.MP), named here so the caption's pop is readable in one file */
});

export const LIVES = Object.freeze(["pop", "stagger", "blend"]);

/* the dials as ONE preset, overridden whole - the same rule fadeUpDials has */
export const lifeDials = (o) => Object.freeze(Object.assign({}, LIFE, o || {}));

/* the POP alone at t, for a word whose spoken onset is `start`: the base's scale, opacity and settling tilt.
   `e` is the arrival's CLOCK (0 -> 1 over POP_S from the anticipation), never the spring's value - the spring
   passes 1 at its overshoot and "landed" has to mean landed. */
export const popAt = (t, start, P = LIFE) => {
  const u = Math.min(1, Math.max(0, (t + P.ANTICIP_S - start) / P.POP_S));
  const k = springPop(u, P.MP);
  return { e: u, o: Math.min(1, k * P.OPACITY_K), y: 0, s: u >= 1 ? 1 : P.POP_LEAD + (1 - P.POP_LEAD) * k,
           b: 0, tilt: 1 - k };
};

/* THE COMPOSITION: one word's life at t under a named setting. Returns the five channels the caption paints
   (opacity, y px, scale, blur px, tilt factor) plus `e`, the arrival's clock - 1 means landed, and only a
   landed word takes the spoken lift and the boil. An unknown setting THROWS: a typo must never silently
   paint the base (the compiler refuses it by name first; this is the second door). */
export const lifeAt = (t, start, kind = "blend", P = LIFE, F = FADE_UP) => {
  if (kind === "pop") return popAt(t, start, P);
  const f = fadeUpAt(t, start, F);
  if (kind === "stagger") return { e: f.e, o: f.o, y: f.y, s: f.s, b: f.b, tilt: 0 };
  if (kind !== "blend") throw new RangeError(`caption life ${kind} is not one of ${LIVES.join(", ")}`);
  const p = popAt(t, start, P);
  /* the pop on top of the stagger: the SCALE and the tilt are the pop's, the RISE is the stagger's, no blur
     (see above), and the word is lit on whichever clock is further on - which is the pop, because it opened
     first. `e` (landed) is the later of the two: a word is not landed while either is still moving it. */
  return { e: Math.min(p.e, f.e), o: Math.max(p.o, f.o), y: f.y, s: p.s, b: 0, tilt: p.tilt };
};

/* the whole page at t, in word order - the same shape fadeUpPage has */
export const lifePage = (t, starts, kind = "blend", P = LIFE, F = FADE_UP) =>
  (starts || []).map((s) => lifeAt(t, s, kind, P, F));
