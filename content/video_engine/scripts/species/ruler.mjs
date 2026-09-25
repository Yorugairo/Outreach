/* SPACE: stage */
/* species/ruler.mjs - THE DECADE RULER (P71 T14, was P69 T55; RESCOPED by the BOOM frame verification, VERIFY.md row
   T32). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN ruler and
   KINETICS:END, AFTER ease (it reads hermite) - its region sits after the stage registry's declaration, with the other
   stage species.

   WHAT THE FRAMES SHOW (jx3Ll-GJtMY 05:50.5-06:10, verify/T32_epoch_ruler/): a full-width tick ruler enters at the
   stage's right edge over the blurred chart and SCROLLS left - 1980 below its ticks and 1990 above at 05:51.0 - and
   settles by 05:52.0 with 2000 / 2010 / 2020 framed (2000 at 0.19 of the width, 2020 at 0.85). The numerals are large,
   bold and faded, the even decades below the ticks and the odd above. The chips of the sentence then pop in a ROW ABOVE
   it. There are no year labels on the chips, no pins and no tick alignment: "cards pinned at their years" was Gemini's,
   and is retired. So this is a GROUND for time passing, and it pins nothing.

   WHEN (`SPECIES_WHEN["ruler"]`, build_scene_timeline_f.py): the sentence SPANS a lag of years between a cause and its
   payoff ("it took more than a decade") - never a single date (an axis tag or a stamp), and it never dates a chip.

   THE LAW, all of it a pure function of t:
     the strip   the years `from` .. `to` at ONE scale: ppy = (SETTLE_R - SETTLE_L) * W / (last - first settle decade),
                 so the settle window fills the same share of the width whatever it names (a portrait stage frames
                 it tighter: SETTLE_L_PORTRAIT / SETTLE_R_PORTRAIT). A tick every year, SUB - 1
                 finer marks between two years, a taller one each five and the tallest each decade, each on its own
                 TRUE year (Bravos's own tick rhythm is decorative and its numerals ride a parallax; ours is a ruler).
     the entry   at `at` the strip's first year stands at the stage's right edge (x = W): the strip wipes on from there
                 by its own translation (A67), never by a camera move.
     the scroll  the origin (the x of `from`) runs from W to its REST - where the first settle decade stands at SETTLE_L
                 * W and the last at SETTLE_R * W, exactly - over SCROLL_S on hermite(0, 1, LEAD, 0): with LEAD 2 the
                 ease-out quad 2u - u^2, front-loaded and landing at rest (BOOM: past half the travel at a third of the
                 time). One way only: time passes right to left.
     the hold    after SCROLL_S it stands; an authored `idle` (a named kind, the engine's, on the life clock) offsets
                 the whole ground by its walk. Absent, declared stillness.
     the numerals  every decade the strip holds, its own year's text, centred on its decade tick; even decades below
                 the ticks, odd above (the witness: 1980 / 2000 / 2020 below, 1990 / 2010 above). Faded: the ground.
     the leave   the whole ruler fades over OUT_S at the end of `dur`.
     the line    the authored `y`, else Y (16:9) / Y_PORTRAIT (9:16): each clear of that aspect's stage caption home.
     the ink     chalk on a dark ground, charcoal on a light one - picked by the MEASURED ground under the band
                 (P70 T1c's helper, handed in as ctx.groundLum), never by the world's kind.
   Nothing is stored. The dials below are ours to tune (42 s42.5); the ones tagged DERIVED were read off the frames. */
import { hermite } from "../kinetics/ease.mjs";

export const RULER = Object.freeze({
  SCROLL_S: 1.5,          /* [DERIVED: BOOM 05:50.5 (the left end at the right edge) -> 05:52.0 (settled)] */
  LEAD: 2.0,              /* the entry speed as a multiple of the mean: 2 makes hermite the ease-out quad (BOOM 51 % / 94 % of the travel at 1/3 / 2/3; this 56 % / 89 %) */
  SETTLE_L: 0.19,         /* [DERIVED: BOOM 05:52.0 - "2000" centred at 0.188 of the width] the first settle decade's x */
  SETTLE_R: 0.85,         /* [DERIVED: ... "2020" at 0.854] the last settle decade's x */
  SETTLE_L_PORTRAIT: 0.22,   /* 9:16: the same numerals on a 1080-wide stage - at 0.19 / 0.85 the outer two ran off its edges */
  SETTLE_R_PORTRAIT: 0.78,   /* (frames/draft/portrait-011.00.png, the first read), so the window is framed tighter */
  Y: 0.74,                /* 16:9: the line BELOW our stage caption's home (432-575 px, build_scene_timeline_f.caption_home_box):
                             the band (BAND_HALF each side) starts at 621. BOOM's own line is 0.646 (465 / 720), where our
                             caption would sit on the "2010" numeral - frames/draft/d1-11.0.png */
  Y_PORTRAIT: 0.56,       /* 9:16: the line ABOVE the caption's home (1297-1440 px): the band ends at 1253; below it the
                             short's own UI owns the foot of the frame (the 9:16 probe had the caption on the ticks) */
  SUB: 4,                 /* marks per year (quarters): the fine texture the witness ruler carries, every mark a true quarter */
  TICK_DECADE_H: 138,     /* [DERIVED: BOOM's tall tick, 92 / 720 of the height] stage px, centred on the line */
  TICK_HALF_H: 104,       /* each five years */
  TICK_YEAR_H: 72,        /* each year */
  TICK_SUB_H: 30,         /* each quarter */
  TICK_DECADE_W: 4.5,
  TICK_HALF_W: 3.5,
  TICK_YEAR_W: 2.6,
  TICK_SUB_W: 1.6,
  TICK_ALPHA: 0.82,       /* the ticks: chalk on the dark ground, not white-hot */
  TICK_SUB_ALPHA: 0.42,
  INK: "#F4E6C7",         /* the chalk the phone chips and the flow already write in on a dark ground ... */
  INK_DARK: "#25313C",    /* ... and the charcoal on a light one (a cream page or plate): the template's --charcoal */
  GROUND_SAMPLES: 24,     /* where the ground is measured: this many points across the width, on the line and at the band's two edges */
  NUM_SIZE: 132,          /* [DERIVED: BOOM's numeral cap height 60 / 720 of the height] stage px - far past the s90 floor */
  NUM_WEIGHT: 800,
  NUM_FONT: "Inter, Arial, sans-serif",
  NUM_ALPHA: 0.16,        /* faded: the numerals are the ground the chips stand over, never the subject */
  NUM_GAP: 14,            /* between the decade tick's end and the numeral */
  NUM_CAP: 0.72,          /* Inter's cap height as a share of its size - where a numeral BELOW the ticks puts its baseline */
  OUT_S: 0.4,             /* the leave at the end of dur */
  PAD_PX: 240,            /* what is drawn past the stage's edges: a numeral half off the edge is still drawn whole */
  SETTLE_MIN: 2,          /* a window is two decades at least ... */
  SETTLE_MAX: 4,          /* ... and four at most: five decades across a stage leaves a year 25 px wide */
});

const ru01 = (v) => Math.min(1, Math.max(0, v));

/* THE FRAMING: the shares of the width the first and the last settle decade land at - the witness's on a landscape
   stage, a tighter pair on a portrait one (H > W), where the outer numerals would run off the edges. */
export const rulerFrame = (W, H) => (H > W ? [RULER.SETTLE_L_PORTRAIT, RULER.SETTLE_R_PORTRAIT] : [RULER.SETTLE_L, RULER.SETTLE_R]);

/* THE SCALE: stage px per year - the settle window over the framing's share of the width. */
export const rulerScale = (sp, W, H) => {
  const s = sp.settle || [], [l, r] = rulerFrame(W, H);
  return (r - l) * W / Math.max(1e-9, s[s.length - 1] - s[0]);
};

/* THE REST: the x of the strip's first year once it has landed - the first settle decade at the framing's left share. */
export const rulerRest = (sp, W, H) => rulerFrame(W, H)[0] * W - (sp.settle[0] - sp.from) * rulerScale(sp, W, H);

/* THE SCROLL's share of the travel at u in [0, 1]: hermite(0, 1, LEAD, 0) over a unit time, clamped. */
export const rulerScroll = (u) => hermite(0, 1, RULER.LEAD, 0, ru01(u), 1);

/* THE ORIGIN at t: the x of `from` - the right edge until its word, then the scroll to its rest, then the rest. */
export const rulerOrigin = (sp, t, W, H) => {
  const rest = rulerRest(sp, W, H), u = ru01((t - sp.at) / RULER.SCROLL_S);
  if (u >= 1) return rest;
  return W + (rest - W) * rulerScroll(u);
};

/* a year's x for a strip whose first year stands at `origin` */
export const rulerYearX = (origin, ppy, from, year) => origin + (year - from) * ppy;

const rulerLevel = (y) => (y % 10 === 0 ? "decade" : y % 5 === 0 ? "half" : "year");

/* THE TICKS the stage can show: {year, level, x} - every year from..to and SUB - 1 marks between two, only those within
   PAD_PX of the stage. A year is an integer, a mark a fraction of one; nothing past `to`. */
export const rulerTicks = (sp, origin, ppy, W) => {
  const out = [], lo = -RULER.PAD_PX, hi = W + RULER.PAD_PX;
  const y0 = Math.max(sp.from, Math.floor(sp.from + (lo - origin) / ppy));
  const y1 = Math.min(sp.to, Math.ceil(sp.from + (hi - origin) / ppy));
  for (let y = y0; y <= y1; y++) {
    const x = rulerYearX(origin, ppy, sp.from, y);
    if (x >= lo && x <= hi) out.push({ year: y, level: rulerLevel(y), x });
    if (y === sp.to) break;
    for (let q = 1; q < RULER.SUB; q++) {
      const yq = y + q / RULER.SUB, xq = rulerYearX(origin, ppy, sp.from, yq);
      if (xq >= lo && xq <= hi) out.push({ year: yq, level: "sub", x: xq });
    }
  }
  return out;
};

/* THE NUMERALS the stage can show: {year, text, side, x} - every decade from..to, even decades below, odd above. */
export const rulerNumerals = (sp, origin, ppy, W) => {
  const out = [], lo = -RULER.PAD_PX, hi = W + RULER.PAD_PX;
  for (let d = Math.ceil(sp.from / 10) * 10; d <= sp.to; d += 10) {
    const x = rulerYearX(origin, ppy, sp.from, d);
    if (x >= lo && x <= hi) out.push({ year: d, text: String(d), side: (d / 10) % 2 === 0 ? "below" : "above", x });
  }
  return out;
};

/* THE LEAVE: 1 from the word through the hold, down to 0 over the last OUT_S of dur; 0 outside the window. */
export const rulerFade = (sp, t) => {
  const end = sp.at + sp.dur;
  if (t < sp.at || t > end) return 0;
  return ru01((end - t) / RULER.OUT_S);
};

/* THE LINE: the authored `y`, else the aspect's default clear of the stage caption's home (the compiler WARNs an
   authored line whose band meets it). */
export const rulerY = (sp, W, H) => (typeof sp.y === "number" ? sp.y : (H > W ? RULER.Y_PORTRAIT : RULER.Y));

/* THE BAND's half-height in stage px: the decade tick, the gap and a numeral's cap height - what the ruler covers
   above and below its line (the compiler mirrors it to test the caption's strip). */
export const rulerBandHalf = () => RULER.TICK_DECADE_H / 2 + RULER.NUM_GAP + RULER.NUM_CAP * RULER.NUM_SIZE;

/* WHERE THE GROUND IS READ: GROUND_SAMPLES points across the width at the line and at the band's top and bottom. */
export const rulerGroundSamples = (y, W) => {
  const out = [], h = rulerBandHalf();
  for (let i = 0; i < RULER.GROUND_SAMPLES; i++) {
    const x = (i + 0.5) * W / RULER.GROUND_SAMPLES;
    out.push([x, y - h], [x, y], [x, y + h]);
  }
  return out;
};

const ruLum = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
  .map((c) => (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)))
  .reduce((a, c, i) => a + c * [0.2126, 0.7152, 0.0722][i], 0);
const ruContrast = (l1, l2) => (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);

/* THE INK on the measured ground: chalk or charcoal, whichever holds the more WCAG contrast on the ground's median
   luminance (the engine's measured-ground helper, P70 T1c's, hands it in as ctx.groundLum); nothing measured (null) is
   the dark ground the ruler was drawn for - chalk. */
export const rulerInk = (lum) => {
  if (lum == null || !Number.isFinite(+lum)) return RULER.INK;
  return ruContrast(ruLum(RULER.INK), +lum) >= ruContrast(ruLum(RULER.INK_DARK), +lum) ? RULER.INK : RULER.INK_DARK;
};

/* THE POSE at t, stage px: the line's y, the scale, the origin and the fade - everything the painter draws from. */
export const rulerPose = (sp, t, W, H) => ({
  y: rulerY(sp, W, H) * H,
  ppy: rulerScale(sp, W, H),
  origin: rulerOrigin(sp, t, W, H),
  fade: rulerFade(sp, t),
});

const RULER_LEVELS = [["sub", "TICK_SUB"], ["year", "TICK_YEAR"], ["half", "TICK_HALF"], ["decade", "TICK_DECADE"]];

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player). One group: a path per tick level
   (finest first, so the taller ticks draw over it) and the numerals; the group fades by the leave and walks by the
   authored idle. No pin, no card, no marker: the ground. */
export function paintRuler(ctx) {
  const { sp, t, svg, el, idle, hash, seed, si, STAGE_W, STAGE_H, groundLum } = ctx;
  const pose = rulerPose(sp, t, STAGE_W, STAGE_H);
  if (!(pose.fade > 0)) return;
  const ink = rulerInk(typeof groundLum === "function" ? groundLum(rulerGroundSamples(pose.y, STAGE_W)) : null);
  const attrs = { opacity: pose.fade.toFixed(3) };
  if (sp.idle && sp.idle !== "none") {
    const ix = idle(sp.idle, t, hash(seed | 0, si | 0, 991));
    attrs.transform = "translate(" + ix.dx.toFixed(2) + " " + ix.dy.toFixed(2) + ")";
  }
  const g = el("g", "ruler", svg, attrs);
  const ticks = rulerTicks(sp, pose.origin, pose.ppy, STAGE_W);
  for (const [level, key] of RULER_LEVELS) {
    const h = RULER[key + "_H"] / 2;
    const d = ticks.filter((k) => k.level === level)
      .map((k) => "M" + k.x.toFixed(2) + " " + (pose.y - h).toFixed(2) + "V" + (pose.y + h).toFixed(2)).join("");
    el("path", "", g, { d: d || "M0 0", fill: "none", stroke: ink, "stroke-width": RULER[key + "_W"],
                        "stroke-linecap": "round", opacity: level === "sub" ? RULER.TICK_SUB_ALPHA : RULER.TICK_ALPHA });
  }
  const face = "font: " + RULER.NUM_WEIGHT + " " + RULER.NUM_SIZE + "px " + RULER.NUM_FONT + "; fill: " + ink;
  const half = RULER.TICK_DECADE_H / 2;
  for (const n of rulerNumerals(sp, pose.origin, pose.ppy, STAGE_W)) {
    const y = n.side === "above" ? pose.y - half - RULER.NUM_GAP : pose.y + half + RULER.NUM_GAP + RULER.NUM_CAP * RULER.NUM_SIZE;
    const tx = el("text", "", g, { x: n.x.toFixed(2), y: y.toFixed(2), "text-anchor": "middle", style: face,
                                   opacity: RULER.NUM_ALPHA });
    tx.textContent = n.text;
  }
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can import this
   file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.ruler = paintRuler;
