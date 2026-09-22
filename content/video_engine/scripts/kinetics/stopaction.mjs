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
import { springEval } from "./spring.mjs";
import { squashAlpha, squashMatrix } from "./squash.mjs";

export const CADENCE = Object.freeze({
  ON1_PX_S: 154,     /* the on-1s threshold = the CINEMA-PARITY reference: RED's pan rule, 1/7 picture width per second = 154 px/s
                        on the 1080 stage at 24 fps with a 180-degree shutter (CONFIRMED in
                        docs/research/runs/strobe_stop_motion/VERIFICATION-2026-09-13.md). Chosen by the evidence and set 2026-09-14
                        (E99 s30, R26-64 / R26-85, P53 T5), pending review on real motion. It replaces 250, which came from the
                        stop-motion brief, not the operator - the brief's derivation does not hold (its 15-arcmin limit is Braddick
                        1974's random-dot limit misattributed to Baker & Braddick 1985; Watson, Ahumada & Farrell 1986 removes a px/s
                        ceiling at 12/8 fps). Every shipped throw runs 1188-2479 px/s, so no shipped hold changes */
  STROBE_PX_S: 300,  /* the on-2s strobe ceiling - NOT operator-set: the number came from a derivation the verification found unsound
                        (VERIFICATION-2026-09-13.md). READ BY NOTHING - `cadence()` consults ON1_PX_S only; only a future
                        declared-cadence gate (a `break_cadence` burst, a boil on 3s, an authored hold; R26-85's space) would read it.
                        No evidence-backed value exists yet: the law is speed x edge sharpness (Watson 1986), so that gate needs a
                        sharpness term before it can state a ceiling */
  FPS: 24,           /* the base frame rate the holds are counted in (on-1s = 24, on-2s = 12, on-3s = 8) */
});
/* MATERIALS. m, k, c [DERIVED: the brief :226-232] -> the spring's zeta and w0 (the report Q4: dense = critically damped, no
   overshoot - metal 0.88 and ink 0.98 sit there; paper 0.67 flutters; liquid 1.34 is overdamped). impact: how hard the hit reads on
   the RECEIVER (the dip, the shadow's spread) [DERIVED, HG2]. squash_frames: the hit's squash in frames at 24 fps - 1 for a deformable
   inanimate thing, 0 for a rigid one, the contact frame itself uncompressed [source on file: Williams pp. 93-94, 263; Lasseter 1987
   s2.2; Whitaker & Halas 1981 p. 42 - WEIGHT_DENSITY_MASS_RESEARCH_BLUEPRINT.md Q1]. e: restitution, the rebound height h1 = e^2 h0
   [UNVERIFIED: the report's Warren 1987 is not on disk; lead ~0, wood ~0.35 - ours kept small until the ear says]. */
export const MASS = Object.freeze({
  paper:  { m: 1.0, k: 180, c: 18.0, impact: 0.7, squash_frames: 1, e: 0.15 },   /* a card: one squash frame, a low hop, a flutter */
  metal:  { m: 3.5, k: 520, c: 75.0, impact: 1.5, squash_frames: 0, e: 0.0 },    /* a heavy rigid thing: "it does not squash", dead stop, the ground takes it */
  liquid: { m: 1.0, k: 45,  c: 18.0, impact: 0.5, squash_frames: 2, e: 0.0 },    /* a spread, no rebound [DERIVED] */
  ink:    { m: 0.5, k: 240, c: 21.5, impact: 1.0, squash_frames: 1, e: 0.1 },    /* our standard */
});
export const STOP = Object.freeze({
  FLIGHT_S: 0.45,    /* a throw's time in the air */
  ARC: 0.22,         /* the arc's lift as a share of the chord */
  SPIN_DEG: 9,       /* the tumble over the flight */
  ANTIC_S: 0.18,     /* [DERIVED: 48 s48.6 APA 100-150 ms + the loading phase; E44's 100-250 ms window] */
  ANTIC_PX: 6,       /* the lift before the drop */
  ANTIC_SQUASH: 0.05,/* the clamp: a little compression before anything moves */
  DROP_S: 0.14,      /* the drop itself, easing in */
  DROP_PX: 48,       /* how far a landing thing falls onto its spot */
  SETTLE_S: 1.2,     /* the material's spring is evaluated this long after the impact, then the thing is at rest */
  /* IMPACT_S (0.08 s) DELETED 2026-09-12 (R26-64, P53 T5): the time constant was the vestige of the formulation the
     5-step ENVELOPE below replaced - `impactSquash` decays the squash off the MATERIAL, counting frames on the stepped
     clock (`IMPACT_SQUASH * (1 - (f - 1) / squash_frames)`; paper 1 frame, liquid 2, metal 0), not off a time decay.
     Nothing read it - not this module, not the player, not a test. A time decay returns only if a hit needs a length
     the material's own frame count cannot state. */
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
  PRESS_PX: 6,          /* THE PICK-UP's press (E99 s51): how far a thing sinks into the surface as its weight is sold, before
                           it is lifted off [DERIVED: the top of the report's own 2-6 px surface-dip range (Q3), because the
                           thing being picked up here is the densest on the board; `pickUpXf` reads it through `o`] */
  SHAKE_PX: [[6, -3], [-4, 2], [0, 0]],   /* the violent hit's three-frame stage shake (opt-in: `violent`) */
  G_PX_S2: 2400,        /* the rebound's gravity in px/s^2 [DERIVED: a 48 px drop over 0.14 s] */
  LAG_FRAMES: 1,     /* [DERIVED: HyperFrames /prompting/motion, verified 2026-09-06; measure on ours] */
});

const sa01 = (v) => Math.min(1, Math.max(0, v));
const saMinJerk = (u) => { u = sa01(u); return u * u * u * (10 - 15 * u + 6 * u * u); };
const saEaseIn = (u) => { u = sa01(u); return u * u * u; };

/* THE CADENCE RULE: which hold a motion piece steps on. kind: "camera" | "boil" | anything else (a translation). */
export const cadence = (v_px_s, kind = "translate", o = {}) => {
  const P = Object.assign({}, CADENCE, o);
  if (kind === "camera") return { hold: 1, fps: P.FPS, why: "a camera move steps every frame" };
  if (kind === "boil") return { hold: 3, fps: P.FPS / 3, why: "a background boil steps on 3s" };
  if (v_px_s > P.ON1_PX_S) return { hold: 1, fps: P.FPS, why: `${Math.round(v_px_s)} px/s > ${P.ON1_PX_S}: on 1s` };
  return { hold: 2, fps: P.FPS / 2, why: `${Math.round(v_px_s)} px/s <= ${P.ON1_PX_S}: on 2s` };
};
/* the stepped clock on the INTEGER frame index (HF-1): frame = round(t * fps), step = floor(frame / hold) */
export const stepped = (t, hold = 2, fps = CADENCE.FPS) => {
  if (!(hold > 1)) return t;
  const frame = Math.round(t * fps), step = Math.floor(frame / hold);
  return step * hold / fps;
};
/* the material's spring: zeta and w0 from m, k, c */
export const massParams = (name) => {
  const M = MASS[name] || MASS.paper, z = M.c / (2 * Math.sqrt(M.k * M.m)), w = Math.sqrt(M.k / M.m);
  return { z, w, wd: z < 1 ? w * Math.sqrt(1 - z * z) : 0, name: MASS[name] ? name : "paper" };
};
/* what a thing drags settles LAG_FRAMES after it */
export const lag = (t, frames = STOP.LAG_FRAMES, fps = CADENCE.FPS) => t - frames / fps;

/* the material's impact weight */
export const massImpact = (name) => (MASS[name] || MASS.paper).impact;
/* THE HIT'S SQUASH (Q1): frame 0 after the contact is the contact drawing, uncompressed; the squash lives on the next
   `squash_frames` frames (1 for a card, 0 for a rigid thing) and releases at once - never a hold */
export const impactSquash = (ts, mass, hold = 1, fps = CADENCE.FPS, o = {}) => {
  const P = Object.assign({}, STOP, o), M = MASS[mass] || MASS.paper;
  if (ts < 0 || !(M.squash_frames > 0)) return 0;
  const f = Math.floor(Math.round(ts * fps) / Math.max(1, hold));
  if (f < 1 || f > M.squash_frames) return 0;
  return Math.min(0.5, P.IMPACT_SQUASH * (1 - (f - 1) / M.squash_frames));
};
/* THE CONTACT SHADOW at a height h (px above rest, >= 0): pinned to the landing spot (its offset from the thing IS the height),
   its blur the depth (16 -> 0.8 px), its alpha narrow; on the hit it takes the squash's spread (scaleX) */
export const contactShadow = (h, alpha = 0, o = {}) => {
  const P = Object.assign({}, STOP, o), k = Math.min(1, Math.max(0, h) / P.SHADOW_H_PX), mix = (a, b) => a + (b - a) * k;
  return { scale: mix(P.SHADOW_NEAR.scale, P.SHADOW_FAR.scale) * (1 + Math.max(0, alpha)), alpha: mix(P.SHADOW_NEAR.alpha, P.SHADOW_FAR.alpha),
           blur: mix(P.SHADOW_NEAR.blur, P.SHADOW_FAR.blur) };
};
/* THE RECEIVER'S DIP (Q3): the surface deflects DIP_PX x impact at the contact and the material's spring brings it back - a
   dense thing's ground recovers dead (metal, ~7 frames), a light thing's flutters */
export const groundDip = (ts, mass, o = {}) => {
  const P = Object.assign({}, STOP, o);
  if (ts < 0) return 0;
  const s = springEval(ts, massParams(mass));
  return P.DIP_PX * massImpact(mass) * (1 - s.x);
};
/* THE REBOUND (Q4, rank 1): the hop after the hit, h1 = e^2 h0, a parabola under G; a rigid dense thing has none */
export const rebound = (ts, mass, h0, o = {}) => {
  const P = Object.assign({}, STOP, o), e = (MASS[mass] || MASS.paper).e || 0, h1 = e * e * Math.max(0, h0);
  if (ts < 0 || h1 < 0.05) return 0;
  const T = 2 * Math.sqrt(2 * h1 / P.G_PX_S2), u = ts / T;
  return u >= 1 ? 0 : -4 * h1 * u * (1 - u);
};
/* THE GROUND'S ANSWER: three frames of shake from the hit, scaled by the material, then exactly zero */
export const groundShake = (ts, mass, fps = CADENCE.FPS, o = {}) => {
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
export const throwXf = (from, mass, t, o = {}) => {
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
export const landXf = (mass, t, o = {}) => {
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

/* THE ROLL (R26-118, E88 s6: "roll it around ... to show that it has real mass & gravity"): a body rolling on a
   surface with NO SLIP - the turn angle IS the distance over the radius - decelerated by a CONSTANT friction (px/s^2),
   so it stops exactly where the math says: a roll of D px needs v0 = sqrt(2 a D) and takes T = v0 / a. Pure, and it
   paints nothing by itself: the only caller is species/melt.mjs's weight phase, which steps it on the melt's own
   clock. Added 2026-09-14 with NO change to anything this module already painted. */
export const rollXf = (dist, radius, decel, ts) => {
  const D = Math.max(0, dist), a = Math.max(1e-6, decel), r = Math.max(1e-6, radius);
  const v0 = Math.sqrt(2 * a * D), T = v0 / a;
  if (!(ts > 0)) return { s: 0, v: v0, turn: 0, T, done: !(D > 0) };
  const t = Math.min(ts, T), s = v0 * t - 0.5 * a * t * t;
  return { s, v: Math.max(0, v0 - a * t), turn: s / r, T, done: ts >= T };
};

/* THE PICK-UP (E99 s51, P61 T6b: "the ball actually picked up and then thrown forward to splat on the canvas"): a
   LANDING RUN BACKWARDS, with the anticipation moved to the FRONT, because the weight is sold before the thing moves
   either way (48 s48.6) and on a pick-up what is sold is the PRESS - the thing settles INTO the surface a moment
   before it is lifted off it. Two beats, in landXf's own proportions (ANTIC_S : DROP_S) so the module states the
   split once:
     PRESS   the thing sinks `PRESS_PX` into the surface and takes the clamp (a negative alpha: compressed along the
             axis, stretched across it), a half-sine out and back - the receiver's own dip, doc 48's 2-6 px [Q3]
     LIFT    `landXf`'s drop read at t' = ANTIC_S + DROP_S * (1 - u): the drop eases IN, so read backwards it leaves
             the surface fast and slows as it comes off - which is a launch, exactly as `throwXf` run backwards is
     the one the melt's `throw` ending already uses. `DROP_PX` (through `o`) is how far it is lifted.
   `t` is seconds into the pick-up and `S` its whole length. Pure; it paints nothing. Added 2026-09-16 with NO change
   to anything this module already painted - `landXf` itself is called, not copied. */
export const pickUpXf = (mass, t, S, o = {}) => {
  const P = Object.assign({}, STOP, o), T = Math.max(0.05, S);
  const press = T * P.ANTIC_S / Math.max(1e-6, P.ANTIC_S + P.DROP_S);
  if (t < press) {
    const u = sa01(t / Math.max(1e-6, press)), bump = Math.sin(Math.PI * u), dip = (P.PRESS_PX || 0) * bump;
    return { x: 0, y: dip, rot: 0, alpha: -P.ANTIC_SQUASH * bump, theta: Math.PI / 2, phase: "press", u,
             h: 0, ground: dip, shake: { x: 0, y: 0 } };
  }
  const u = sa01((t - press) / Math.max(1e-6, T - press));
  const st = landXf(mass, P.ANTIC_S + P.DROP_S * (1 - u), o);
  return { x: 0, y: st.y, rot: 0, alpha: st.alpha, theta: st.theta, phase: "lift", u, h: Math.max(0, -st.y),
           ground: 0, shake: { x: 0, y: 0 } };
};

/* ================= THE STAMP (R26-20's other half; E99 s87) =================
   PORTED, not invented, from remotion-ui's own primitive, which is on disk at
   content/video_engine/remotion-ui/src/remotion/primitives/badge-stamp.tsx (its curves are quoted per dial below,
   by line). The intake triaged it into "Priority integration" and named the gap in our vocabulary exactly
   (REMOTION-UI-INTAKE-2026-09-07.md:41): "(ii) the TWO-SPRING OFFSET: a clamped scale spring landing while a free
   rotation spring is still unwinding ... The offset is the weight cue our single-spring landings lack", plus "the
   split shock curves (linear life, eased expansion to 2x radius) fix a failure the source names - an impact ring
   nobody sees", plus "exitAtInFrames ships the E50 shape: a landed mark owes an exit", and the boundary: "Look
   does not port: charcoal-on-cream, drawn in our hand, not a gold ring."
   WHAT THE SOURCE'S OWN COMMENT SAYS IT IS (badge-stamp.tsx:43-49): "it comes in oversized and over-rotated, hits
   its mark, and settles back with the rotation still unwinding after the scale has stopped - the offset between the
   two is what sells the weight. The shockwave is thrown from the impact frame, not from the start, so it cannot
   arrive before the thing that caused it."
   THE PORT, three things and no more:
     THE TWO SPRINGS   Remotion's spring({config:{damping, stiffness, mass}}) is this module's own mass-spring-damper
       in the same variables (zeta = c / (2 sqrt(k m)), w0 = sqrt(k / m)), so the source's two configs come across as
       numbers and spring.mjs's closed form evaluates them - stateless, so a seek IS the play. The SCALE spring
       carries overshootClamping: true (:72-74: "an overshoot past 1 dips the settled seal under its own size, which
       reads as a wobble rather than as weight"), which Remotion implements by ENDING the spring at its target: here
       the crossing time is solved in closed form (tc) and the value is exactly 1 from it on. The ROTATION spring is
       free (:80-81: "the seal is still turning fractionally after it has stopped moving toward the page").
     THE IMPACT RING   two curves, never one (:98-113): life LINEAR over SHOCK_S (it fades and thins evenly) and the
       EXPANSION eased out on the source's entrance curve to RING_TO x the mark's own radius, "because a shockwave
       leaves the impact fast and decelerates ... a ring that only grows to 1.55x is under it the whole time it is
       worth seeing". Drawn only while 0 < life < 1 (:152), so it can never be held: this is an IMPACT cue, not E56's
       annotation ring (which circles a number or a point on a chart and is the compiler's own `ring` species).
     THE EXIT          exitAtInFrames / exitInFrames (:61-62, :119-125) on the source's exit curve, ease-IN cubic
       (lib/timing.ts:9 EASING_EXIT = Easing.in(Easing.cubic), "Never ease-out an exit"): E50's shape, a landed mark
       owes an exit, authored from the first build.
   WHAT DOES NOT PORT: the seal's gold ring, its two curved texts, its double border - a look. Ours is charcoal on
   cream drawn in our hand, and the PAYLOAD is whatever the mark is: E99 s87 (3) puts a PROP CUTOUT under it (a
   docked card that keeps its RGBA), so the ink strength is a PRESSURE cue under the picture, never a wash over it.
   WHAT THIS MODULE KEEPS OF OURS: the receiver. A stamp's contact is at its own t = 0 (the mark is already on its
   spot; the scale over 1 is the height), so the page DIPS by the material's own spring and takes the hit's squash
   frame - groundDip / impactSquash, the same two the throw and the landing answer with. Pure in t; it paints
   nothing. Added with NO change to anything this module already painted. */
/* NAMED `STAMP_ARRIVAL`, not `STAMP`: the engine inlines every module into ONE name space and the VECTOR
   MAP's own species dials already own that identifier (species/vecmap.mjs:60). E99 s87 (4) keeps `stamp` the
   vector map's SPECIES and makes this an `arrive:` value; the two never meet, and this name says so. */
export const STAMP_ARRIVAL = Object.freeze({
  FROM: 2.1,          /* badge-stamp.tsx:88-91 interpolate(land, [0, 1], [2.1, 1], { output: "perceptual-scale" }) - the mark arrives oversized,
                         at the scale it was thrown from, and comes down in AREA space (see stampSprings) */
  LAND_DEG: -9,       /* :58 rotation - the angle it lands at (ours to author per mark; this is the source's default) */
  WIND_DEG: 16,       /* :59 windUp - "how much further round it starts", in degrees */
  LAND: { m: 0.9, k: 220, c: 14 },   /* :78 the CLAMPED scale spring: damping 14, stiffness 220, mass 0.9 -> zeta 0.4975, w0 15.635 rad/s */
  TURN: { m: 1.0, k: 120, c: 11 },   /* :85 the FREE trailing rotation spring: damping 11, stiffness 120, mass 1 -> zeta 0.5021, w0 10.954 rad/s - slower, so it is still ringing when the scale is done */
  FADE: 0.35,         /* :93 opacity = interpolate(land, [0, 0.35], [0, 1]) - never a cut and never a dissolve: the fade rides the scale spring's own first third */
  INK: [1, 0.86],     /* :96 "Ink strength: heavy on impact, easing back as the pressure comes off", over land 0.35 -> 1 */
  SHOCK_S: 14 / 30,   /* :106 [delayInFrames, delayInFrames + 14] at the source's DEFAULT_FPS 30 (lib/timing.ts:3) = 0.4667 s of ring */
  RING_TO: 2.0,       /* :156 r * (1 + shock): the ring reaches TWICE the mark's own radius - the number the source's comment defends */
  RING_W_PX: 4.8,     /* :159 strokeWidth 2.6 of a 120-unit viewBox drawn at size 220 = 4.77 px of real stroke */
  RING_W_FADE: 0.7,   /* :159 2.6 * (1 - shockLife * 0.7) - it thins on the LINEAR curve, not the eased one */
  RING_A: 0.55,       /* :160 0.55 * (1 - shockLife) - and fades on the linear curve too */
  EXIT_S: 16 / 30,    /* :62 exitInFrames = 16 at DEFAULT_FPS 30 = 0.5333 s */
  SETTLE_Z: 6,        /* SPRING.SETTLE's own convention (spring.mjs:11): the envelope at e^-6 is rest, so a stamp is
                         settled at 6 / (zeta w0) of its SLOWEST spring - the rotation's, which is the whole point */
});

/* a mass-spring-damper config -> the closed form's parameters, plus tc, the first instant a 0 -> 1 step response
   reaches 1 (x = 1 when cos(wd t) + (z w / wd) sin(wd t) = 0, i.e. wd t = pi - atan(wd / (z w))). tc is how
   overshootClamping is honoured exactly rather than by watching a value go past its target. */
const stampSpring = (g) => {
  const z = g.c / (2 * Math.sqrt(g.k * g.m)), w = Math.sqrt(g.k / g.m);
  const wd = z < 1 ? w * Math.sqrt(1 - z * z) : 0;
  return { z, w, wd, tc: wd > 0 ? (Math.PI - Math.atan2(wd, z * w)) / wd : Infinity, ts: STAMP_ARRIVAL.SETTLE_Z / (z * w) };
};
export const STAMP_LAND = stampSpring(STAMP_ARRIVAL.LAND);
export const STAMP_TURN = stampSpring(STAMP_ARRIVAL.TURN);

/* the source's ENTRANCE curve, cubic-bezier(0.16, 1, 0.3, 1) (lib/timing.ts:6 EASING_ENTER, reached as
   motion-tokens.ts:44 EASING.enter): the standard CSS form - x solved by Newton, then y. Local on purpose; this
   module is self-contained (it carries its own min-jerk and ease-in for the same reason). */
const saBez = (x1, y1, x2, y2) => {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const fx = (u) => ((ax * u + bx) * u + cx) * u, dfx = (u) => (3 * ax * u + 2 * bx) * u + cx;
  return (x) => {
    x = sa01(x);
    let u = x;
    for (let i = 0; i < 10; i++) {
      const e = fx(u) - x, d = dfx(u);
      if (Math.abs(e) < 1e-9 || !(Math.abs(d) > 1e-12)) break;
      u = Math.min(1, Math.max(0, u - e / d));
    }
    return ((ay * u + by) * u + cy) * u;
  };
};
const saEnter = saBez(0.16, 1, 0.3, 1);

/* THE TWO-SPRING OFFSET, on its own: land is the CLAMPED scale spring (exactly 1 from tc), turn the FREE one.
   off_deg is what the offset IS - how far the mark is still off the angle it lands at, at an instant when scale
   may already be 1.0000. Everything else here is read off those two. */
export const stampSprings = (t, o = {}) => {
  const P = Object.assign({}, STAMP_ARRIVAL, o);
  const L = P.LAND === STAMP_ARRIVAL.LAND ? STAMP_LAND : stampSpring(P.LAND);
  const R = P.TURN === STAMP_ARRIVAL.TURN ? STAMP_TURN : stampSpring(P.TURN);
  const ts = Math.max(0, t);
  const land = ts >= L.tc ? 1 : Math.min(1, springEval(ts, L).x);
  const turn = springEval(ts, R).x;
  /* PERCEPTUAL SCALE (badge-stamp.tsx:90 `output: "perceptual-scale"`): Remotion 4.0.502 interpolates it in SIGNED
     AREA, not in scale - `toSignedArea(s) = sign(s) s^2`, the mix, then `fromSignedArea(a) = sign(a) sqrt|a|`
     (remotion/dist/cjs/interpolate.js:272-283, :327-330, read in the main checkout's remotion-kit/node_modules; the
     harvest pinned no node_modules of its own). Both ends are 2.1 and 1 as before; mid-approach the area eases, so at
     land 0.5 the mark is sqrt((2.1^2 + 1) / 2) = 1.645 where a linear mix read 1.55. */
  const scale = Math.sqrt(P.FROM * P.FROM + (1 - P.FROM * P.FROM) * land);
  return { land, turn, scale, deg: P.LAND_DEG + P.WIND_DEG * (1 - turn),
           off_deg: P.WIND_DEG * (1 - turn), opacity: sa01(land / Math.max(1e-6, P.FADE)),
           ink: P.INK[0] + (P.INK[1] - P.INK[0]) * sa01((land - P.FADE) / Math.max(1e-6, 1 - P.FADE)),
           settled: ts >= R.ts, land_at: L.tc, rest_at: R.ts };
};

/* THE IMPACT RING on its SPLIT curves: life linear (the fade and the thinning), the expansion eased out to RING_TO
   x the mark's own radius. r is a MULTIPLIER of that radius, so the painter supplies the mark's own geometry.
   null before the contact and once the life is spent - the source draws it only while 0 < life < 1 (:152). */
export const stampRing = (ts, o = {}) => {
  const P = Object.assign({}, STAMP_ARRIVAL, o), S = Math.max(1e-6, P.SHOCK_S);
  if (!(ts > 0)) return null;
  const life = ts / S;
  if (life >= 1) return null;
  const k = saEnter(life);
  return { life, k, r: 1 + (P.RING_TO - 1) * k, width: P.RING_W_PX * (1 - life * P.RING_W_FADE),
           alpha: P.RING_A * (1 - life) };
};

/* THE EXIT the landed mark owes (E50; the source's exitAtInFrames): 0 -> 1 on the ease-IN cubic, over EXIT_S from
   the instant the mark is told to leave. 1 - stampExit is the opacity, as :134 / :169 have it. */
export const stampExit = (ts, o = {}) => {
  const P = Object.assign({}, STAMP_ARRIVAL, o);
  return saEaseIn(sa01(Math.max(0, ts) / Math.max(1e-6, P.EXIT_S)));
};

/* STAMP: the whole arrival as one pure function of t (seconds from the CONTACT - a stamp is already on its spot, so
   its contact is its own zero and the ring is thrown from it). scale, rot, ink and opacity are the mark's;
   y / ground / alpha are the RECEIVER's answer in this module's own vocabulary (the surface dips by the material's
   spring, the hit takes its squash frame); h is the height the contact shadow reads, taken off the scale still to
   come [DERIVED: the mark's oversize IS its distance from the page - the source has no shadow at all]. */
export const stampXf = (mass, t, o = {}) => {
  const P = Object.assign({}, STAMP_ARRIVAL, o);
  const sp = stampSprings(t, o), still = { x: 0, y: 0 };
  /* the contact shadow's height dial is STOP's (SHADOW_H_PX), not the stamp's: P is STAMP_ARRIVAL + o, and reading
     P.SHADOW_H_PX made h NaN on every call, so the shadow stood in its at-contact state before the mark had arrived
     (R26-20 review H2). An `o` may still override it, as every other STOP dial can be. */
  const H = P.SHADOW_H_PX != null ? P.SHADOW_H_PX : STOP.SHADOW_H_PX;
  const h = H * sa01((sp.scale - 1) / Math.max(1e-6, P.FROM - 1));
  if (t < 0) return { x: 0, y: 0, rot: P.LAND_DEG + P.WIND_DEG, scale: P.FROM, off_deg: P.WIND_DEG, ink: P.INK[0],
                      opacity: 0, alpha: 0, theta: Math.PI / 2, phase: "waiting", u: 0, h, ground: 0, shake: still, ring: null };
  const st = settle(t, 0, mass, P, 1);   /* h0 = 0: a stamp does not fall and does not hop - the source clamps the scale so the seal never dips under its own size */
  return { x: 0, y: st.y, rot: sp.deg, scale: sp.scale, off_deg: sp.off_deg, ink: sp.ink, opacity: sp.opacity,
           alpha: st.alpha, theta: Math.PI / 2, phase: sp.settled ? "settled" : "stamp", u: sp.land, h,
           ground: st.ground, shake: P.violent ? groundShake(t, mass) : still, ring: stampRing(t, o) };
};

/* the CSS a painter appends: translate, the tumble, the area-preserving squash - fixed decimals. A negative alpha is a
   clamp (compress along the axis, stretch across it) and goes through the same tensor with the axis turned. */
export const stopCss = (s) => {
  const a = Math.abs(s.alpha || 0), th = (s.alpha || 0) < 0 ? (s.theta || 0) + Math.PI / 2 : (s.theta || 0);
  const m = a > 1e-6 ? " matrix(" + squashMatrix(th, a).map((v) => v.toFixed(4)).join(",") + ",0,0)" : "";
  /* the STAMP's scale (R26-20 / E99 s87), written ONLY when the state carries one - every throwXf / landXf /
     pickUpXf state there has ever been carries none, so their CSS is byte-for-byte what it was */
  const sc = s.scale != null && Math.abs(s.scale - 1) > 1e-6 ? " scale(" + s.scale.toFixed(4) + ")" : "";
  return " translate(" + (s.x || 0).toFixed(2) + "px," + (s.y || 0).toFixed(2) + "px)" + ((s.rot || 0) ? " rotate(" + s.rot.toFixed(2) + "deg)" : "") + sc + m;
};
