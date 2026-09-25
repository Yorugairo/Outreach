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
   sway; live - breath + drift; none - explicit stillness, declared. And one CARD kind outside IDLE_KINDS (the kinds a
   plate, a page or a species may name): hold - the drift-hold of a held card (P70 T13, below; `holdGradeOf`).
   Every number below is a starting reference, tagged where it came from; the operator's eye moves them (42 s42.5). */

export const IDLE_KINDS = Object.freeze(["none", "breath", "drift", "pulse", "figure", "live"]);

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

/* THE DRIFT-HOLD (P70 T13; the operator, 2026-09-24: "npx hyperframes add drift-hold i think this becomes an interesting
   reference to hold charts/evidence docks with"; E99 s124 as amended: a hovering dock holds on it). A held CARD - a chart
   card or an evidence dock - turns under a degree, breathes and carries one soft light sweep, each ONE whole sine cycle
   across its held span, the endpoint phase wrapped to a literal 0 so the pose at the span's start IS the pose at its end
   (the reference's own seam). Every number is read off `content/video_engine/hyperframes/compositions/components/
   drift-hold.html` (harvested fc71e49, a reference only), its `amplitudes` table and its `renderPose` phases, never
   invented. Two differences from the reference, both forced by the card being a dock and not a whole composition:
     (1) the reference's `cqw` are fractions of its 1920-wide FRAME and its card is 68 cqw wide, so the sweep's travel
         and the band's width are re-expressed as fractions of the CARD's own width (42 / 68, 20 / 68): a dock is any size;
     (2) the cycle is anchored to the dock's held span [t0, t1] (the caller's), never to a mounted duration; outside it
         the pose holds the seam pose, so a card that arrives or retracts carries it continuously. A caller that passes
         no span cycles on the reference's own mounted duration, FREE_S.
   `whisper` for a card carrying a chart (it must stay readable), `standard` for a picture. The light is painted by the
   caller from `holdLightCss`: the pose's transform half goes through idleCss like every other kind. */
export const IDLE_HOLD = Object.freeze({
  whisper: Object.freeze({
    ROT_DEG: 0.24,          /* [DERIVED: drift-hold.html amplitudes.whisper.rotation 0.24 deg] */
    SCALE: 0.006,           /* [DERIVED: drift-hold.html amplitudes.whisper.scale 0.006] */
    SWEEP: 30 / 68,         /* [DERIVED: drift-hold.html amplitudes.whisper.sweep 30 cqw over its 68 cqw card] - card widths */
    LIGHT: 0.04,            /* [DERIVED: drift-hold.html amplitudes.whisper.light 0.04] - the band's opacity swing */
  }),
  standard: Object.freeze({
    ROT_DEG: 0.6,           /* [DERIVED: drift-hold.html amplitudes.standard.rotation 0.6 deg] */
    SCALE: 0.015,           /* [DERIVED: drift-hold.html amplitudes.standard.scale 0.015] */
    SWEEP: 42 / 68,         /* [DERIVED: drift-hold.html amplitudes.standard.sweep 42 cqw over its 68 cqw card] - card widths */
    LIGHT: 0.08,            /* [DERIVED: drift-hold.html amplitudes.standard.light 0.08] */
  }),
  PH_ROT: Math.PI / 6,      /* [DERIVED: drift-hold.html renderPose, rotation = sin(phase + PI / 6)] */
  PH_SCALE: Math.PI / 2,    /* [DERIVED: drift-hold.html renderPose, scale = 1 + sin(phase + PI / 2)] */
  PH_SWEEP: -Math.PI / 2,   /* [DERIVED: drift-hold.html renderPose, sweepX = sin(phase - PI / 2)] */
  PH_LIGHT: Math.PI / 3,    /* [DERIVED: drift-hold.html renderPose, sweepOpacity = 0.12 + sin(phase + PI / 3)] */
  LIGHT_BASE: 0.12,         /* [DERIVED: drift-hold.html renderPose, the 0.12 the light swings about] */
  BAND_LEFT: 0.42,          /* [DERIVED: drift-hold.html .dh-sweep left 42 % of the card] */
  BAND_W: 20 / 68,          /* [DERIVED: drift-hold.html .dh-sweep width 20 cqw over its 68 cqw card] - card widths */
  BAND_TILT_DEG: 14,        /* [DERIVED: drift-hold.html gsap.set(sweep, {rotation: 14})] - the band leans 14 deg off the vertical */
  BAND_PEAK: 0.28,          /* [DERIVED: drift-hold.html .dh-sweep gradient 50 % stop, fg at 28 %] */
  BAND_EDGE: 0.10,          /* [DERIVED: drift-hold.html .dh-sweep gradient 25 % / 75 % stops, accent at 10 %] */
  INK: [242, 242, 242],     /* [DERIVED: the template's --lp-chalk #F2F2F2 (STAMP_RING_INK.CHALK) - the reference's light is its theme's fg
                               #f8fafc and sky accent; ours is the stage's one white] */
  FREE_S: 4,                /* [DERIVED: drift-hold.html data-duration="4", the reference's mounted duration] - a span-less cycle */
});
export const IDLE_HOLD_GRADES = Object.freeze(["whisper", "standard"]);
/* the CARD kinds: a dock names one of these (the compiler's DOCK_IDLES); none of them is a plate's or a species' kind */
export const IDLE_CARD_KINDS = Object.freeze(["hold", "hold:whisper", "hold:standard"]);
const IDLE_HOLD_KIND = /^hold(?::(whisper|standard))?$/;

/* `hold`, `hold:whisper`, `hold:standard` -> the grade; anything else -> null (not a hold) */
export const holdGradeOf = (kind) => {
  const m = typeof kind === "string" ? IDLE_HOLD_KIND.exec(kind) : null;
  return m ? (m[1] || "standard") : null;
};

/* the hold's PHASE at t in [0, 2 PI): one whole cycle across [t0, t1], the endpoint wrapped to a literal 0 (the
   reference's own "Literal phase zero at the endpoint removes floating point residue"); held at 0 outside the span */
export const holdPhase = (t, span, phase0 = 0, o = {}) => {
  const P = Object.assign({}, IDLE_HOLD, o);
  const a = span ? +span[0] : NaN, b = span ? +span[1] : NaN;
  if (!(Number.isFinite(a) && Number.isFinite(b) && b > a)) return IDLE_TAU * idleFrac(t / P.FREE_S + phase0);
  const u = (t - a) / (b - a);
  return u <= 0 || u >= 1 ? 0 : IDLE_TAU * u;
};

/* THE POSE at a phase: {rot deg, scale, sweep (card widths from the band's rest), light (the band's opacity)} */
export const holdPose = (phase, grade = "standard", o = {}) => {
  const P = Object.assign({}, IDLE_HOLD, o), A = P[grade] || P.standard;
  const p = phase === IDLE_TAU ? 0 : phase;
  return { rot: Math.sin(p + P.PH_ROT) * A.ROT_DEG, scale: 1 + Math.sin(p + P.PH_SCALE) * A.SCALE,
           sweep: Math.sin(p + P.PH_SWEEP) * A.SWEEP, light: P.LIGHT_BASE + Math.sin(p + P.PH_LIGHT) * A.LIGHT };
};

/* the band's PEAK alpha over the card - the brightest the light ever lays on the card's text (E28's check) */
export const holdPeakAlpha = (grade = "standard", o = {}) => {
  const P = Object.assign({}, IDLE_HOLD, o), A = P[grade] || P.standard;
  return P.BAND_PEAK * (P.LIGHT_BASE + A.LIGHT);
};

/* THE LIGHT as a CSS background for an overlay the size of the card's box (w x h px): the reference's band - its
   tent of edge / peak / edge stops, leaning BAND_TILT_DEG - as one linear-gradient across the box. The band's centre
   is at (BAND_LEFT + BAND_W / 2 + sweep) card widths on the card's middle line; its stops are placed on the gradient
   line (CSS: through the box's centre, length w cos + h sin of the lean), so the band keeps its own width at any
   aspect. "" when the box has no size. Fixed decimals: two seeks to one t write one string. */
export const holdLightCss = (pose, w, h, o = {}) => {
  const P = Object.assign({}, IDLE_HOLD, o);
  if (!(w > 0 && h > 0) || !pose) return "";
  const th = P.BAND_TILT_DEG * Math.PI / 180, L = w * Math.cos(th) + h * Math.sin(th);
  const c = 50 + ((P.BAND_LEFT + P.BAND_W / 2 + pose.sweep) * w - w / 2) * Math.cos(th) / L * 100;
  const hw = (P.BAND_W * w / 2) / L * 100, a = Math.max(0, pose.light);
  const ink = (k) => "rgba(" + P.INK.join(",") + "," + (k * a).toFixed(4) + ")";
  const at = (x) => x.toFixed(2) + "%";
  return "linear-gradient(" + (90 + P.BAND_TILT_DEG) + "deg, rgba(" + P.INK.join(",") + ",0) " + at(c - hw) + ", "
    + ink(P.BAND_EDGE) + " " + at(c - hw / 2) + ", " + ink(P.BAND_PEAK) + " " + at(c) + ", "
    + ink(P.BAND_EDGE) + " " + at(c + hw / 2) + ", rgba(" + P.INK.join(",") + ",0) " + at(c + hw) + ")";
};

/* ONE ENTRY: the transform of a held thing of `kind` at t. {scale, dx, dy, lum}; `none` is the identity. A `hold`
   (or `hold:<grade>`) adds {rot, light} - the turn idleCss writes, and the band the caller paints (holdLightCss) - on
   the span `o.HOLD_SPAN` = [t0, t1] (the caller's, on the same clock as t); `phase` only seeds a span-less cycle. */
export const idleXf = (kind, t, phase = 0, o = {}) => {
  const P = Object.assign({}, IDLE, o), tq = idleClock(t, P.STEP_FPS);
  const id = { scale: 1, dx: 0, dy: 0, lum: 1 };
  const grade = holdGradeOf(kind);
  if (grade) {
    const x = holdPose(holdPhase(tq, P.HOLD_SPAN, phase), grade);
    return Object.assign(id, { scale: x.scale, rot: x.rot, sweep: x.sweep, light: x.light });
  }
  if (kind === "breath") return Object.assign(id, { scale: breath(tq, phase, P) });
  if (kind === "drift") { const d = drift(tq, phase, P); return Object.assign(id, { dx: d[0], dy: d[1] }); }
  if (kind === "pulse") return Object.assign(id, { lum: pulse(tq, phase, P) });
  if (kind === "figure") { const s = sway(tq, phase, P); return Object.assign(id, { scale: 1 + P.BREATH_AMP * figureBreath(tq, phase, P), dx: s[0], dy: s[1] }); }
    if (kind === "live") {   /* breath + drift (2026-09-08): a breath is a scale with a fixed point at the centre, so a chart at the page centre
                                stayed bit-identical while the page "breathed" (operator: "even our charts need some sort of life, even if it's
                                just 1 pixel shifts"); the drift moves every pixel by the same 1-2 px walk, so nothing on the page is ever still */
      const d = drift(tq, phase, P); return Object.assign(id, { scale: breath(tq, phase, P), dx: d[0], dy: d[1] }); }
  return id;
};

/* the CSS suffix a painter appends to the element's own transform - fixed decimals, so two seeks to one t write one
   string. The identity writes an explicit no-op so a flagged-off render and a `none` render differ by nothing. A pose
   that TURNS (the hold's `rot`, deg) appends its rotate; a pose with no `rot` writes exactly the string it always has. */
export const idleCss = (x) => (x.scale === 1 && x.dx === 0 && x.dy === 0 && !x.rot) ? ""
  : " translate(" + x.dx.toFixed(2) + "px," + x.dy.toFixed(2) + "px) scale(" + x.scale.toFixed(4) + ")"
    + (x.rot ? " rotate(" + x.rot.toFixed(3) + "deg)" : "");

const IDLE_K = Object.freeze({ MIN: 0, MAX: 4 });   /* kinetics/camera.mjs PARALLAX.K_MIN / K_MAX, mirrored - a module imports nothing */

/* R26-133 (E49; the operator, 2026-09-14: "Plate idle should probably paint, but would have to see what it looks
   like"): the TRANSLATION half of an idle, alone, as the CSS a WORLD's rest term takes. The scale is deliberately
   not here - a plate world's scale is already the world's own `z`, and it was by reading the idle for its `.scale`
   alone that the player made `drift` ({scale: 1, dx, dy}) a no-op: the plate held perfectly still.
   A PLANE of a layered plate takes the SHARE k of the same walk, the way camLayerState shares the camera's own
   translation, so the near plane drifts further than the far wall off ONE idle and no second motion is invented
   (E49: a camera move is a camera move; a hold holds at its idle). k is clamped to the compiler's own depth range,
   as the camera clamps it, so a sidecar with nonsense cannot invert a plane. Fixed decimals, so two seeks to one t
   write one string; "" for a pose that moves nothing, so a caller concatenates unconditionally and a breath - or a
   dial that is off - writes exactly the string it has always written. */
export const idleDriftCss = (x, k = 1) => {
  const kk = Math.min(IDLE_K.MAX, Math.max(IDLE_K.MIN, +k));
  const s = Number.isFinite(kk) ? kk : 1;
  const px = (+(x && x.dx) || 0) * s, py = (+(x && x.dy) || 0) * s;
  return (px === 0 && py === 0) ? "" : " translate(" + px.toFixed(2) + "px," + py.toFixed(2) + "px)";
};

/* R26-133 / E99 s55 (the operator, 2026-09-16: "maybe we need a slightly smaller drift (maybe 30 px?) AND the alive
   water ... for youtube the 40 px drift would be too much motion for a long form, but it looks like it might work
   really well for shorts and certain scenes"): the drift's AMPLITUDE, resolved for ONE plate. E99 s38 closed the 2 px
   walk as a motion nobody can see - "8 frames to move 1 pixel is probably not even enough to realy register" - so the
   amplitude is AUTHORED, and authored per scene: the row's own `;drift=<px>` first, then the timeline's
   `plate_idle_drift_px` dial, then DRIFT_PX itself. There is NO global default on purpose (E45: the approved cuts
   render through their frozen players and must not move under this), and DRIFT_PX 2.0 is the FLOOR, never a setting
   to go under - it is E49's "nothing ever goes truly still", which no dial may switch off. A value under the floor is
   refused by the compiler by name; here it is raised to the floor, so the two sides can never disagree about what a
   too-small number means. 20 px is the named long-form setting (E99 s64 / s65 amended s55's 30), 30-40 the shorts one; PLATE_DRIFT_LONG 20. */
export const idleDriftPx = (...asked) => {
  for (const a of asked) {
    const n = +a;
    if (a !== null && a !== undefined && a !== "" && Number.isFinite(n) && n > 0) return Math.max(IDLE.DRIFT_PX, n);
  }
  return IDLE.DRIFT_PX;
};
