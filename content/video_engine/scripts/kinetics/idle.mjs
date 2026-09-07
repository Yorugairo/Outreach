/* kinetics/idle.mjs - THE IDLE (ruling E49, 2026-09-06: "nothing ever goes truly still"; P47 T5). SOURCE OF TRUTH,
   inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN idle and KINETICS:END. Behind
   kinetics.idle.
   The defect it answers: a held thing - a page under a sentence, a parked dock, a pill, a caption, a plate - was
   bit-identical from frame to frame, and the cure reached for was a whole plate moving (Ken Burns, the parallax push).
   The operator: "we let things be completely still instead of being at a subtle idle." A camera move is a camera
   move (29 s9.27, 45); a hold holds - at its idle.
   The law: every idle is a NAMED kind, sized by a dial, a pure function of t (a scrubbed frame is the played frame),
   phased per element so two pills never breathe in step, and never an event for the motion gate (M01 / M10 / M16
   count events; the frozen-frames row M18 is the idle's own check).
   Kinds: breath - a scale that inhales ABOVE rest and never below it (a plate shrinking under its box shows its
   edge); drift - a bounded Lissajous walk of a few px; pulse - a luminance dip; figure - the asymmetric breath doc 48
   s48.4 prescribes for a standing figure (inspiratory:expiratory 1:1.5-1:2, a post-expiratory pause) with its two-rate
   sway; none - explicit stillness, declared.
   Every number below is a starting reference, tagged where it came from; the operator's eye moves them (42 s42.5). */

export const IDLE_KINDS = Object.freeze(["none", "breath", "drift", "pulse", "figure"]);

export const IDLE = Object.freeze({
  BREATH_AMP: 0.012,        /* [DERIVED: HyperFrames /prompting/motion "1-2 %", verified 2026-09-06; measure on ours] - a 1.2 % inhale */
  BREATH_HZ: 0.25,          /* doc 48 s48.4: breath 0.20-0.30 Hz (12-18 / min) */
  DRIFT_PX: 2.0,            /* dial (42 s42.5): the bounded drift's half-width, stage px */
  DRIFT_HZ: [0.11, 0.17],   /* two rates whose common period (100 s) never closes inside a short: the walk never reads as a loop */
  PULSE_AMP: 0.03,          /* dial: the luminance dips 3 % at most */
  PULSE_HZ: 0.2,
  FIGURE_IE: 1.75,          /* doc 48 s48.4: inspiratory:expiratory 1:1.5 to 1:2 - "never a sine" */
  FIGURE_PAUSE_S: 0.7,      /* doc 48 s48.4: the post-expiratory pause, 0.5-1.0 s */
  SWAY_PX: 1.5,             /* doc 48 s48.4: head excursion, scaled to a cutout - a dial */
  SWAY_HZ: [0.15, 0.25],    /* doc 48 s48.4: "two oscillators at 0.15 and 0.25 Hz so it never loops visibly" */
  SWAY_WANDER: 0.12,        /* the pink-noise stand-in: each oscillator's phase wanders by this fraction of a cycle ... */
  SWAY_WANDER_HZ: [0.031, 0.047],   /* ... at two slow rates, so the two 20 s-periodic sines never return to one pose inside a short */
  STEP_FPS: 0,              /* 0 = continuous; > 0 quantises the idle's clock to the INTEGER frame index (HyperFrames HF-1: never elapsed seconds) */
});

const IDLE_TAU = Math.PI * 2;
const idle01 = (v) => Math.min(1, Math.max(0, v));
const idleSmooth = (u) => { u = idle01(u); return u * u * (3 - 2 * u); };
const idleFrac = (v) => v - Math.floor(v);

/* the idle's clock: t itself, or t on the frame grid when STEP_FPS > 0 - floor(t * fps) is the frame index, and every
   pose below is derived from the index, never from the elapsed seconds between frames */
export const idleClock = (t, fps = IDLE.STEP_FPS) => (fps > 0 ? Math.floor(t * fps + 1e-9) / fps : t);

/* BREATH: scale in [1, 1 + AMP], exactly 1 at rest (t = 0, phase = 0), period 1 / HZ. Above rest only. */
export const breath = (t, phase = 0, o = {}) => {
  const P = Object.assign({}, IDLE, o);
  return 1 + P.BREATH_AMP * (1 - Math.cos(IDLE_TAU * (P.BREATH_HZ * t + phase))) / 2;
};

/* DRIFT: [dx, dy] px, a Lissajous walk inside +-DRIFT_PX x +-0.6 DRIFT_PX, the two axes on their own rates. */
export const drift = (t, phase = 0, o = {}) => {
  const P = Object.assign({}, IDLE, o);
  return [P.DRIFT_PX * Math.sin(IDLE_TAU * (P.DRIFT_HZ[0] * t + phase)),
          P.DRIFT_PX * 0.6 * Math.sin(IDLE_TAU * (P.DRIFT_HZ[1] * t + phase * 1.7))];
};

/* PULSE: a luminance multiplier in [1 - AMP, 1], exactly 1 at rest. */
export const pulse = (t, phase = 0, o = {}) => {
  const P = Object.assign({}, IDLE, o);
  return 1 - P.PULSE_AMP * (1 - Math.cos(IDLE_TAU * (P.PULSE_HZ * t + phase))) / 2;
};

/* THE FIGURE'S BREATH (48 s48.4): one cycle of period 1 / BREATH_HZ is an inhale over Ti, an exhale over Te = IE * Ti,
   then a pause of FIGURE_PAUSE_S at rest. Returns the lung's fill in [0, 1]; the caller scales it. Never a sine: the
   inhale is the short leg, the exhale the long one, and the rest is a real hold. */
export const figureBreath = (t, phase = 0, o = {}) => {
  const P = Object.assign({}, IDLE, o), T = 1 / P.BREATH_HZ, pause = Math.min(P.FIGURE_PAUSE_S, T * 0.5);
  const active = T - pause, Ti = active / (1 + P.FIGURE_IE), Te = active - Ti;
  const u = idleFrac(t / T + phase) * T;
  if (u < Ti) return idleSmooth(u / Ti);
  if (u < Ti + Te) return 1 - idleSmooth((u - Ti) / Te);
  return 0;
};
export const figurePhases = (o = {}) => {
  const P = Object.assign({}, IDLE, o), T = 1 / P.BREATH_HZ, pause = Math.min(P.FIGURE_PAUSE_S, T * 0.5);
  const active = T - pause, Ti = active / (1 + P.FIGURE_IE);
  return { period: T, inhale: Ti, exhale: active - Ti, pause };
};

/* SWAY (48 s48.4): two oscillators at 0.15 and 0.25 Hz, the A-P axis the larger, in px. */
export const sway = (t, phase = 0, o = {}) => {
  const P = Object.assign({}, IDLE, o);
  const w0 = P.SWAY_WANDER * Math.sin(IDLE_TAU * (P.SWAY_WANDER_HZ[0] * t + phase * 0.7));   /* the wandering phases */
  const w1 = P.SWAY_WANDER * Math.sin(IDLE_TAU * (P.SWAY_WANDER_HZ[1] * t + phase * 1.9));
  return [P.SWAY_PX * 0.4 * Math.sin(IDLE_TAU * (P.SWAY_HZ[0] * t + phase + w0)),
          P.SWAY_PX * (0.5 * Math.sin(IDLE_TAU * (P.SWAY_HZ[1] * t + phase * 1.3 + w1)) + 0.5 * Math.sin(IDLE_TAU * (P.SWAY_HZ[0] * t + phase * 0.6 + w0)))];
};

/* ONE ENTRY: the transform of a held thing of `kind` at t. {scale, dx, dy, lum}; `none` is the identity. */
export const idleXf = (kind, t, phase = 0, o = {}) => {
  const P = Object.assign({}, IDLE, o), tq = idleClock(t, P.STEP_FPS);
  const id = { scale: 1, dx: 0, dy: 0, lum: 1 };
  if (kind === "breath") return Object.assign(id, { scale: breath(tq, phase, P) });
  if (kind === "drift") { const d = drift(tq, phase, P); return Object.assign(id, { dx: d[0], dy: d[1] }); }
  if (kind === "pulse") return Object.assign(id, { lum: pulse(tq, phase, P) });
  if (kind === "figure") { const s = sway(tq, phase, P); return Object.assign(id, { scale: 1 + P.BREATH_AMP * figureBreath(tq, phase, P), dx: s[0], dy: s[1] }); }
  return id;
};

/* the CSS suffix a painter appends to the element's own transform - fixed decimals, so two seeks to one t write one
   string. The identity writes an explicit no-op so a flagged-off render and a `none` render differ by nothing. */
export const idleCss = (x) => (x.scale === 1 && x.dx === 0 && x.dy === 0) ? ""
  : " translate(" + x.dx.toFixed(2) + "px," + x.dy.toFixed(2) + "px) scale(" + x.scale.toFixed(4) + ")";
