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

/* the CSS a painter appends: translate, the tumble, the area-preserving squash - fixed decimals. A negative alpha is a
   clamp (compress along the axis, stretch across it) and goes through the same tensor with the axis turned. */
export const stopCss = (s) => {
  const a = Math.abs(s.alpha || 0), th = (s.alpha || 0) < 0 ? (s.theta || 0) + Math.PI / 2 : (s.theta || 0);
  const m = a > 1e-6 ? " matrix(" + squashMatrix(th, a).map((v) => v.toFixed(4)).join(",") + ",0,0)" : "";
  return " translate(" + (s.x || 0).toFixed(2) + "px," + (s.y || 0).toFixed(2) + "px)" + ((s.rot || 0) ? " rotate(" + s.rot.toFixed(2) + "deg)" : "") + m;
};
