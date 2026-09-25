/* SPACE: stage */
/* species/balance.mjs - THE BALANCE SCALE, AND THE BALANCE TIPS (P70 T7, was P69 T59; the Bravos harvest v2's T27
   "Balance scale", CHN 19:10 / JPN 06:41, and its A40 "The balance tips", CHN 19:10). SOURCE OF TRUTH, inlined into the
   scene-evidence player by sync_kinetics.py between KINETICS:BEGIN balance and KINETICS:END, AFTER ease, spring,
   clothoid, squash, stopaction and chip - it imports all six, and the import order IS the region order. Its region
   sits immediately before ring's.
   THE MODULE RULE (the operator, 2026-09-11): a species is a module here, never a branch in the engine's body. The last
   statement registers the painter in SPECIES_PAINTERS; node, where no such registry exists, still imports the file for
   the pure math below.

   WHEN (BRAVOS-USE-WHEN :589 / :643): two forces are WEIGHED ('threat' against 'opportunity', the moat against the
   paper) and the sentence says which way it tips - or that it does not. Never when one side is unnamed or unweighed,
   and never for a real balance of figures (:646 - that is two bars; the compiler refuses a label with a digit).

   E99 s128 DECIDES WHAT IT IS: "the prop is an object that is meant to live in the world, a stamp is us just saying
   'hey we're applying this thing here'". A balance is an OBJECT - it stands in the page's room, it is solid (the base is
   filled, so only the part it does not cover shows its shadow), and it carries the stage light's RESTING SHADOW: T6b's
   cross-hatch, laid by the engine's own `propHatchLines` (handed to this painter through its ctx) at PROP_SHADOW's
   dials, cut to the base's silhouette thrown along the light's fall - the bars' soft layer's SVG adapter (the
   engine's lpHatchSvg), not a copy of its math. A prop loaded on a pan carries the same hatch, cut to its own alpha.

   THE LAW, all of it a pure function of t:
     draw    - on `at` the fulcrum (a tapered post on a domed foot), then the beam's two ARMS (from the pivot outward),
               then each pan's two HANGERS and its BOWL, each by length with the hand's drawOn; a filled part's fill
               follows its outline. Every curve is GENERATED, so every curve is a clothoid (doc 42 s42.4, quoted by the
               engine at the clothoid region: "Applies to geometry the engine GENERATES - arrows, balance arms,
               connectors, axes"): each arm is a G1 fit from the pivot to its end, rising off the pivot at ARM_BOW_DEG and
               coming down into the end at the same angle (a symmetric fit IS the circular arc, A = 0); a hanger is the
               fit with both tangents along its chord (k = 0, a string under load is straight); the bowl is the arc
               under its rim; the foot's dome the arc over its sole.
     load    - each side's load lands on ITS word by stopaction's landXf (the anticipation, the drop easing in, the
               impact, the material's settle; `mass` per side, `ink` by default), fading in on the chip's own FADE_S
               (chipLand) - a sourced glyph (`icon`, chipGeometry), a catalogued prop (`prop`), or, with neither, the
               NAME itself as the load. A named picture's name hangs under its pan.
     weigh   - the beam's angle is the LINEAR response of a spring to a piecewise-constant target, summed over its
               steps: theta(t) = sum_i d_i x_i((t - t_i) / S_i), x the closed-form step (kinetics/spring.mjs
               springEval). A load's contact adds LEAN_DEG toward its side on the lean spring, so one pan loaded LEANS
               to it and both loaded settle LEVEL (the two steps cancel, whatever their order or gap). Stateless, so a
               seek is the play.
     tip     - `tip: {at, to}` adds TIP_DEG toward `to` on its word, on an underdamped spring (TIP_MP) with ONE visible
               overshoot: the first swing past the rest is TIP_MP x TIP_DEG, the swing back TIP_MP^2 x TIP_DEG, under a
               degree. A mass, never a fade.
     plumb   - a pan hangs from its arm's end and never turns: its group is TRANSLATED to the end, never rotated.
     hold    - an opt-in `idle` (E49, one of IDLE_KINDS), about the foot; absent = declared stillness.
     leave   - the last EXIT_S of the window takes the whole object down in opacity (the species owes its exit, E50).
   Nothing is stored: every visual reads from t and the declaration. The dials below are ours to tune (42 s42.5), not
   findings; the one reference measured is Bravos's rest angle, ~13 deg (CHN shot 114, 19:14.8). */
import { minJerk } from "../kinetics/ease.mjs";
import { springParams, springEval } from "../kinetics/spring.mjs";
import { clothoid, clothoidPath } from "../kinetics/clothoid.mjs";
import { squashMatrix } from "../kinetics/squash.mjs";
import { STOP, PROP_SHADOW, landXf } from "../kinetics/stopaction.mjs";
import { CHIP_STAMP, chipLand, chipGeometry } from "./chip.mjs";

export const BALANCE = Object.freeze({
  DRAW_S: 0.9,          /* the fulcrum, the beam and the pans draw on `at` over this; a load lands on a DRAWN pan (the compiler: BALANCE_DRAW_S) */
  BASE_END: 0.4,        /* ... the fulcrum's outline over the first 0.4 of it ... */
  BEAM_FROM: 0.25,      /* ... the arms from 0.25 ... */
  BEAM_END: 0.65,       /* ... to 0.65, from the pivot outward ... */
  PAN_FROM: 0.5,        /* ... and the hangers and bowls from 0.5 to the end */
  FILL_S: 0.18,         /* a filled part's fill follows its outline over this */
  LEAN_DEG: 7,          /* one pan loaded: the beam leans this far to it [DERIVED: Bravos's gentle rock reads ~3-5 deg; a lean has to read as weight] */
  LEAN_MP: 0.1,         /* ... on a spring with this overshoot ... */
  LEAN_S: 0.9,          /* ... settled (the envelope at 0.25 %) this long after the contact */
  TIP_DEG: 12,          /* the tip's rest angle [DERIVED: Bravos CHN shot 114 rests at ~13 deg, ends 110 vs 177 px over 292 px] */
  TIP_MP: 0.2,          /* ONE visible overshoot: 0.2 x 12 = 2.4 deg past the rest, the swing back 0.2^2 x 12 = 0.48 deg - under 1 */
  TIP_S: 1.2,           /* ... settled this long after the word; the overshoot peaks at 0.32 s, the swing back at 0.64 s */
  TIP_SEEN_S: 0.7,      /* the window a tip needs after its word - past the overshoot and the swing back (the compiler: BALANCE_TIP_SEEN_S) */
  LAND_SEEN_S: 0.62,    /* ... and a load after its word - the contact (STOP.ANTIC_S + STOP.DROP_S) and the settle's first 0.3 s (BALANCE_LAND_S) */
  LOAD_DROP_PX: 90,     /* how far a load falls into its pan (landXf's DROP_PX, for a thing dropped onto a scale) */
  MASS: "ink",          /* the default material of a load (stopaction MASS) */
  ARM_K: 0.33,          /* each arm's length as a share of the room's width */
  ARM_BOW_DEG: 7,       /* the arm rises off the pivot at this angle and comes down into its end at it: the arch */
  BEAM_W: 11,           /* the arm's stroke, stage px */
  KNOB_R: 11,           /* the pivot's pin ... */
  END_R: 7,             /* ... and the ring at each arm's end the hangers hang from */
  PIVOT_F: 0.22,        /* the pivot's height in the room, from its top */
  HANG_K: 0.34,         /* a hanger's drop as a share of the room's height */
  PAN_K: 0.9,           /* a pan's width as a share of the arm */
  PAN_DEPTH_K: 0.2,     /* the bowl's depth as a share of its width */
  LOAD_K: 0.62,         /* a load's box as a share of the pan's width */
  POST_TOP: 14,         /* the post's width under the pin ... */
  POST_BOT: 44,         /* ... and on the foot */
  FOOT_K: 0.7,          /* the foot's width as a share of the arm */
  FOOT_H: 26,           /* the foot's dome */
  FOOT_F: 0.96,         /* the foot's sole, from the room's top */
  STROKE_W: 4,          /* an outline's stroke */
  HANGER_W: 3,          /* a hanger's stroke */
  GLYPH_W: 2,           /* a sourced glyph's stroke, in its own 24-unit box (the phone chip's) */
  LABEL_PX: 60,         /* a name's size - the s90 phone floor, 59.08 stage px (ledger_page.CARD_TYPE_PX), rounded up */
  LABEL_FLOOR: 59.08,   /* ... and the size a name too wide for its half may be FITTED down to, never below (the text floor) */
  LABEL_GAP: 22,        /* a named picture's name under its pan's bowl */
  LABEL_EM: 0.55,       /* [DERIVED: Kalam 700's mean advance] - the width estimate when the text cannot be measured */
  LABEL_STROKE: 6,      /* the name's ground-coloured halo (the stamp label's paint-order stroke) */
  POST_CLEAR: 22,       /* a name keeps this far off the post's centre line - the post's widest half (POST_BOT / 2): its own HALF of
                           the room (the compiler: BALANCE_POST_CLEAR_PX) */
  NAME_PAD: 8,          /* a name's PAINTED width over its advance: the 6 px halo (3 a side) and the hand face's slant overhang,
                           measured on the served frame (OPPORTUNITY: 365.5 px painted against 361.6 advance at 59.08 px) */
  NAME_SLANT: 3,        /* ... and the hand face's slant carries the painted box this far RIGHT of its anchor (measured on the served
                           frames: +2.8 px at 59.66 px, +3.9 px at 59.08 px), so a name is anchored this far left of its fitted centre */
  STAGE_MARGIN: 12,     /* ... and never nearer the stage's edge than this, whatever else gives (a cut name is unreadable) */
  RIM_LIFT: 8,          /* a name that IS its load stands this far above its pan's rim (the bowl is solid ink: text in it would vanish) */
  HATCH_S: 0.35,        /* the base's resting hatch rises over this once its outline is down (T6b's handover, on the base's own clock) */
  EXIT_S: 0.35,         /* the last this-much of the window takes the whole object down */
  INK: CHIP_STAMP.INK,  /* `ink`: cream (the default: on the charcoal page) or charcoal (on a light ground) - the stamp's own pair */
  HATCH_GROUND: Object.freeze({ cream: "page", charcoal: "ground" }),   /* ... and PROP_SHADOW's ground for the hatch under it */
  /* A SIDE'S SIGN INK (P72 T41, R26-334; Bravos CHN shots 113 / 114 - a coloured pill on each pan, threat red, opportunity
     green): an opt-in `tone: neg | pos | neutral` on a side draws its NAME as a PILL in the palette's sign inks. Absent,
     the name paints exactly as it did. The pill's sizes are the chip tab's (species/chip.mjs TAB_H over TAB_TYPE, TAB_PAD),
     so a balance's pill and a chip's tab are one family. */
  TONE: Object.freeze({
    FORM: "filled",     /* THE PILL'S FORM - one of BALANCE_TONE_FORMS, the three candidates on the operator's sheet (P72-HG1 item 6); provisional until that pick sets it */
    INK: Object.freeze({ neg: "#FF4D4D", pos: "#3DDC84", neutral: "#b8c4d0" }),   /* the template's --lp-neg / --lp-pos (E28's sign pair, the chip tab's TAB_INK) and LP_INK.deemph (the palette's explicit de-emphasis) - never a new ink (test_balance_tone pins all three) */
    TEXT: "#25313C",    /* the word on a FILLED pill: charcoal, the chip tab's TAB_TEXT (>= 4.5:1 on every fill, pinned) */
    H_K: 70 / 59.08,    /* the pill's height over its word's size: the chip tab's TAB_H over TAB_TYPE */
    PAD_PX: 14,         /* the room each side of the word: the chip tab's TAB_PAD */
    OUTLINE_W: 4,       /* the `outline` form's ring, drawn INSIDE the pill's box (the box is what the fit places) - the balance's own STROKE_W */
    CAP_EM: Object.freeze({ kalam: 0.77, inter: 0.73 }),   /* the caps' height in em at weight 700 [MEASURED: canvas actualBoundingBoxAscent of "HTEOPRAMW" in the golden's own page, scratchpad/p72-t41/logs/measure-caps.json] - centres the word in its pill */
  }),
});

const bal01 = (v) => Math.min(1, Math.max(0, v));
const balRad = (deg) => deg * Math.PI / 180;
const balSign = (side) => (side === "left" ? -1 : 1);   /* theta > 0 turns the beam clockwise on the stage: the RIGHT end goes down */
export const BALANCE_SIDES = Object.freeze(["left", "right"]);
const BAL_LEAN = springParams(BALANCE.LEAN_MP);
const BAL_TIP = springParams(BALANCE.TIP_MP);

/* the instant a load TOUCHES its pan: landXf's anticipation and drop */
export const balanceContactS = () => STOP.ANTIC_S + STOP.DROP_S;

/* the beam's steps: one per weighed side (at its load's contact) and one for the tip (on its word) */
export const balanceSteps = (sp) => {
  const out = [];
  for (const side of BALANCE_SIDES) {
    const L = (sp || {})[side];
    if (L && Number.isFinite(+L.at)) out.push({ t: +L.at + balanceContactS(), d: balSign(side) * BALANCE.LEAN_DEG, p: BAL_LEAN, s: BALANCE.LEAN_S, why: side });
  }
  const tip = (sp || {}).tip;
  if (tip && Number.isFinite(+tip.at) && BALANCE_SIDES.includes(tip.to))
    out.push({ t: +tip.at, d: balSign(tip.to) * BALANCE.TIP_DEG, p: BAL_TIP, s: BALANCE.TIP_S, why: "tip" });
  return out;
};

/* THE BEAM'S ANGLE at t, in degrees (> 0: the right end down): the spring's step response summed over the steps */
export const balanceAngle = (sp, t) => balanceSteps(sp)
  .reduce((a, e) => (t > e.t ? a + e.d * springEval((t - e.t) / e.s, e.p).x : a), 0);

/* where every part stands in a room b = {x, y, w, h} (stage px), level - the beam turns about `pivot` */
export const balanceGeom = (b) => {
  const B = BALANCE, cx = b.x + b.w / 2, A = B.ARM_K * b.w, pw = B.PAN_K * A;
  return { cx, py: b.y + B.PIVOT_F * b.h, A, H: B.HANG_K * b.h, pw, pd: B.PAN_DEPTH_K * pw, load: B.LOAD_K * pw,
           fy: b.y + B.FOOT_F * b.h, fw: B.FOOT_K * A };
};

/* an arm in the BEAM's frame (the pivot at 0, 0; x along the beam, y down): the G1 clothoid fit from the pivot to
   (side x A, 0), rising off the pivot at ARM_BOW_DEG and coming down into the end at it - the symmetric fit, which is
   the circular arc (A = 0) */
export const balanceArm = (A, side, n = 24) => {
  const s = balSign(side), bow = balRad(BALANCE.ARM_BOW_DEG);
  const h0 = s > 0 ? -bow : Math.PI + bow, h1 = s > 0 ? bow : Math.PI - bow;
  return clothoid({ x: 0, y: 0 }, h0, { x: s * A, y: 0 }, h1, n);
};

/* ... turned by theta degrees about the pivot and placed on the stage */
export const balanceTurn = (p, deg, pivot) => {
  const r = balRad(deg), c = Math.cos(r), s = Math.sin(r);
  return { x: pivot.x + c * p.x - s * p.y, y: pivot.y + s * p.x + c * p.y };
};

/* THE ARM'S END on the stage at theta: where its pan hangs from */
export const balanceEnd = (g, side, deg) => balanceTurn({ x: balSign(side) * g.A, y: 0 }, deg, { x: g.cx, y: g.py });

/* a hanger, from the arm's end (0, 0 in the pan's frame) to the rim: the fit with both tangents along the chord */
export const balanceHanger = (dx, dy, n = 2) => {
  const h = Math.atan2(dy, dx);
  return clothoid({ x: 0, y: 0 }, h, { x: dx, y: dy }, h, n);
};

/* the bowl under a rim of width w at depth d below it: the arc (a symmetric fit) from the left rim to the right */
export const balanceBowl = (w, d, y, n = 24) => {
  const phi = 2 * Math.atan(2 * d / Math.max(1e-6, w));
  return clothoid({ x: -w / 2, y }, phi, { x: w / 2, y }, -phi, n);
};

/* the foot's dome over its sole: the arc (a symmetric fit) from the left of the sole to the right */
export const balanceDome = (cx, fy, fw, fh, n = 24) => {
  const phi = 2 * Math.atan(2 * fh / Math.max(1e-6, fw));
  return clothoid({ x: cx - fw / 2, y: fy }, -phi, { x: cx + fw / 2, y: fy }, phi, n);
};

/* A LOAD's pose at t: landXf's drop (y, and its squash on the travel axis) and the chip's fade; null before its word */
export const balanceLoadPose = (L, t) => {
  if (!L || !Number.isFinite(+L.at) || t < +L.at) return null;
  const x = landXf(L.mass || BALANCE.MASS, t - +L.at, { DROP_PX: BALANCE.LOAD_DROP_PX });
  return { y: x.y, alpha: x.alpha, theta: x.theta, phase: x.phase, fade: chipLand(t, +L.at).fade };
};

/* the draw's shares at t: the fulcrum, the arms, the pans (0..1 each) */
export const balanceDraw = (sp, t) => {
  const B = BALANCE, u = (t - +sp.at) / B.DRAW_S;
  const f = (a, z) => bal01((u - a) / Math.max(1e-6, z - a));
  return { base: f(0, B.BASE_END), beam: f(B.BEAM_FROM, B.BEAM_END), pan: f(B.PAN_FROM, 1),
           baseFill: bal01((t - +sp.at - B.DRAW_S * B.BASE_END) / B.FILL_S),
           panFill: bal01((t - +sp.at - B.DRAW_S) / B.FILL_S),
           hatch: minJerk((t - +sp.at - B.DRAW_S * B.BASE_END) / B.HATCH_S) };
};

/* the whole object's opacity: 1 until the last EXIT_S of the window, then down */
export const balanceLeave = (sp, t) => 1 - bal01((t - (+sp.at + +sp.dur - BALANCE.EXIT_S)) / BALANCE.EXIT_S);

/* A NAME'S FIT - its size, its x (its centre) and the STEP that placed it - in the order the parent set (round 3):
     "fit"      it fits its OWN HALF of the room (the room's outer edge to POST_CLEAR off the post) at LABEL_PX, and stands
                under its pan, held inside that half;
     "shrunk"   1. too wide: its SIZE is fitted to the half, down to LABEL_FLOOR (never its letter spacing);
     "overhang" 2. still too wide at the floor: centred under its OWN pan, pushed OUTWARD only as far as it must be to keep
                off the post's guard - past the room's outer edge, toward the stage margin;
     "pinned"   3. the stage margin blocks even that: no placement satisfies both rules, so it is pinned AT the margin -
                inside the stage, across the post's guard - the least-bad frame; the compiler WARNs it with its numbers
                and the fix (E99 s106: the engine advises, the author decides). Every fallback is a WARN, never a refusal.
   `w` is the width measured at LABEL_PX; widths scale with the size (one face, no tracking). `side` left | right, `px` the
   pan's x (the arm's end), `b` the room, `cx` the post, `stageW` the stage. */
export const balanceNameFit = (side, px, w, b, cx, stageW) => {
  const B = BALANCE, left = side === "left";
  const inner = left ? cx - B.POST_CLEAR : cx + B.POST_CLEAR, outer = left ? b.x : b.x + b.w;
  const edge = left ? B.STAGE_MARGIN : stageW - B.STAGE_MARGIN, half = Math.abs(inner - outer);
  const inHalf = (ww) => { const h = ww / 2, lo = left ? outer + h : inner + h, hi = left ? inner - h : outer - h;
    return Math.min(hi, Math.max(lo, px)); };
  if (w <= half) return { size: B.LABEL_PX, w, x: inHalf(w), step: "fit" };
  const size = Math.max(B.LABEL_FLOOR, B.LABEL_PX * half / w), ws = w * size / B.LABEL_PX;
  if (ws <= half + 1e-9) return { size, w: ws, x: inHalf(ws), step: "shrunk" };
  const h = ws / 2, lo = left ? edge + h : inner + h, hi = left ? inner - h : edge - h;   /* the guard to the stage margin */
  if (lo <= hi + 1e-9) return { size, w: ws, x: Math.min(hi, Math.max(lo, px)), step: "overhang" };   /* under its pan as near as it can */
  return { size, w: ws, x: left ? edge + h : edge - h, step: "pinned" };
};

/* A NAME'S ROW, in its pan's frame (y down from the arm's end): a bare name (the load itself) stands on the rim and rides
   its load's drop; a pictured load's name hangs under the bowl. */
export const balanceNameRow = (g, pictured, loadY) => (pictured
  ? g.H + g.pd + BALANCE.LABEL_GAP + 0.8 * BALANCE.LABEL_PX : g.H - BALANCE.RIM_LIFT + loadY);

export const balanceInk = (sp) => (sp && sp.ink === "charcoal" ? "charcoal" : "cream");

/* A SIDE'S SIGN INK (R26-334): the three tones a side may declare (the compiler refuses any other BY NAME), and the
   pill's three candidate forms for the operator's pick:
     filled   the pill in the tone's ink, the word in charcoal in the hand's face (Kalam 700) - ours, in Bravos's shape;
     outline  the pill in the ground's ink ringed in the tone's, the word in the tone's ink - the s118 inked name, held;
     sans     the pill in the tone's ink, the word in charcoal in the chip tab's face (Inter 700) - Bravos's own. */
export const BALANCE_TONES = Object.freeze(["neg", "pos", "neutral"]);
export const BALANCE_TONE_FORMS = Object.freeze(["filled", "outline", "sans"]);
export const balanceTone = (L) => (L && BALANCE_TONES.includes(L.tone) ? L.tone : null);

/* a name's PAINTED width over its advance `adv` (at LABEL_PX): the halo's NAME_PAD untoned, the pill's two pads toned */
export const balanceNameWidth = (adv, tone) => adv + (tone ? 2 * BALANCE.TONE.PAD_PX : BALANCE.NAME_PAD);

/* A TONED NAME'S ROW in its pan's frame, for a word of `size` px in `face`: a bare name's pill STANDS on its rim (its foot
   RIM_LIFT above it, riding the load's drop - never in the solid bowl), a pictured load's pill hangs LABEL_GAP under the
   bowl; the word's caps are centred in the pill. {top, h, baseline} */
export const balanceToneRow = (g, pictured, loadY, size, face = "kalam") => {
  const T = BALANCE.TONE, h = T.H_K * size, cap = T.CAP_EM[face] * size;
  const top = pictured ? g.H + g.pd + BALANCE.LABEL_GAP : g.H - BALANCE.RIM_LIFT + loadY - h;
  return { top, h, baseline: top + h / 2 + cap / 2 };
};

/* the pill's PAINT in a form, on the balance's other ink `ground` (the page's, under the cream balance) */
export const balanceTonePaint = (tone, form, ground) => {
  const T = BALANCE.TONE, ink = T.INK[tone];
  if (form === "outline") return { fill: ground, stroke: ink, strokeW: T.OUTLINE_W, text: ink, face: "kalam" };
  return { fill: ink, stroke: "none", strokeW: 0, text: T.TEXT, face: form === "sans" ? "inter" : "kalam" };
};

/* one POSE for the whole object at t, from the declaration alone - what the painter draws and a test reads */
export const balancePose = (sp, t, b) => {
  const g = balanceGeom(b), deg = balanceAngle(sp, t);
  return { g, deg, draw: balanceDraw(sp, t), leave: balanceLeave(sp, t),
           ends: { left: balanceEnd(g, "left", deg), right: balanceEnd(g, "right", deg) },
           loads: { left: balanceLoadPose(sp.left, t), right: balanceLoadPose(sp.right, t) } };
};

const balD = (pts) => clothoidPath(pts);
/* every name: the hand's face at the floor, in the ink, on a halo of the other ink (the stamp label's paint-order stroke) */
const balLabelStyle = (ink, other, size = BALANCE.LABEL_PX) => "font-family:Kalam,cursive;font-size:" + +size.toFixed(2) + "px;font-weight:700;fill:" + ink
  + ";paint-order:stroke;stroke:" + other + ";stroke-width:" + BALANCE.LABEL_STROKE + "px";
const balPoly = (pts) => pts.map((p, i) => (i ? "L" : "M") + p.x.toFixed(2) + " " + p.y.toFixed(2)).join(" ") + " Z";

/* THE RESTING HATCH (T6b; E99 s92 / s128) under a silhouette: `sil(parent)` writes the silhouette (filled shapes, or a
   prop's image) into a mask; the lines are the engine's propHatchLines through the SVG adapter (each fillRect one line,
   setTransform the family's frame), laid in stage px over the silhouette's reach, cut to it thrown along the light's
   fall (a sharp mask) and tapered toward its rim (the same silhouette blurred), in PROP_SHADOW's ink per ground. No
   propHatchLines in the ctx: no hatch (the reviewer's decision, acceptance 4). */
const balHatch = (ctx, parent, id, box, sil, ground, opacity) => {
  const { el, propHatchLines } = ctx;
  if (typeof propHatchLines !== "function" || !(opacity > 0)) return null;
  const P = PROP_SHADOW, H8 = P.HATCH, th = balRad(P.LIGHT_DEG + 180);
  const dx = P.OFFSET_PX * Math.cos(th), dy = P.OFFSET_PX * Math.sin(th), pad = P.OFFSET_PX + 4 * H8.TAPER_PX;
  const x0 = Math.floor(box.x - pad), y0 = Math.floor(box.y - pad);
  const W = Math.ceil(box.w + 2 * pad), H = Math.ceil(box.h + 2 * pad);
  const R = { x: x0, y: y0, width: W, height: H };
  const defs = el("defs", "", parent);
  const mk = (suffix, blur) => {
    const m = el("mask", "", defs, Object.assign({ id: id + suffix, maskUnits: "userSpaceOnUse", maskContentUnits: "userSpaceOnUse",
                                                   style: "mask-type:alpha" }, R));
    let host = m;
    if (blur > 0) {
      const f = el("filter", "", defs, Object.assign({ id: id + suffix + "-blur", filterUnits: "userSpaceOnUse" }, R));
      el("feGaussianBlur", "", f, { stdDeviation: blur });
      host = el("g", "", m, { filter: "url(#" + id + suffix + "-blur)" });
    }
    sil(el("g", "", host, { transform: "translate(" + dx.toFixed(3) + " " + dy.toFixed(3) + ")", fill: "#fff" }));
  };
  mk("-cut", 0);
  if (H8.TAPER_PX > 0) mk("-taper", H8.TAPER_PX);
  const outer = el("g", "bal-hatch", parent, { opacity: (P.ALPHA[ground] * opacity).toFixed(3), mask: "url(#" + id + "-cut)" });
  const g = H8.TAPER_PX > 0 ? el("g", "", outer, { mask: "url(#" + id + "-taper)" }) : outer;
  const sg = el("g", "", g, { fill: "rgb(" + P.INK[ground].join(",") + ")", transform: "translate(" + x0 + " " + y0 + ")" });
  [["primary", P.LIGHT_DEG, H8.PITCH_PX, H8.WIDTH_PX], ["cross", P.LIGHT_DEG + H8.CROSS_DEG, H8.CROSS_PITCH_PX, H8.CROSS_WIDTH_PX]]
    .forEach(([fam, deg, pitch, width]) => {
      let m = null; const d = [];
      propHatchLines({ setTransform: (...a) => { m = a; },
                       fillRect: (x, y, w, h) => d.push("M" + x + " " + +y.toFixed(4) + "h" + w + "v" + +h.toFixed(4) + "h" + -w + "z") },
                     x0, y0, W, H, deg, pitch, width);
      const e = el("path", "", sg, { d: d.join(""), transform: "matrix(" + m.map((v) => +v.toFixed(6)).join(",") + ")" });
      e.dataset.family = fam;
    });
  return outer;
};

/* the fulcrum's two filled shapes on the stage: the tapered post and the domed foot (their outlines drawn by length) */
export const balanceBase = (g) => {
  const B = BALANCE, top = g.py, sole = g.fy, dome = sole - B.FOOT_H;
  const post = [{ x: g.cx - B.POST_TOP / 2, y: top }, { x: g.cx + B.POST_TOP / 2, y: top },
                { x: g.cx + B.POST_BOT / 2, y: dome + 4 }, { x: g.cx - B.POST_BOT / 2, y: dome + 4 }];
  const arc = balanceDome(g.cx, sole, g.fw, B.FOOT_H);
  return { post, foot: arc, box: { x: g.cx - g.fw / 2, y: top, w: g.fw, h: sole - top } };
};

/* a name's width, measured where the text can be (the browser), estimated where it cannot (node) */
const balNameW = (lab, label) => (typeof lab.getComputedTextLength === "function" ? lab.getComputedTextLength()
  : BALANCE.LABEL_EM * BALANCE.LABEL_PX * String(label).length);

/* a toned name's style: the form's face at `size`, in the form's word ink, no halo (the pill is its ground) */
const balToneLabelStyle = (paint, size = BALANCE.LABEL_PX) => "font-family:" + (paint.face === "inter" ? "Inter,Arial,sans-serif" : "Kalam,cursive")
  + ";font-size:" + +size.toFixed(2) + "px;font-weight:700;fill:" + paint.text + ";stroke:none";

/* A TONED NAME (R26-334): the pill first, so the word paints over it; the word measured at LABEL_PX in the form's face,
   fitted by the PILL's width (balanceNameWidth) through the same four steps, the pill centred where the fit put it and
   the word centred in the pill (the hand face's slant carried as the untoned name carries it). Both take the name's
   own fade. */
const balTonedName = (ctx, side, L, pose, pan, E, b, g, other) => {
  const { el, t } = ctx, B = BALANCE, tone = balanceTone(L), stageW = ctx.STAGE_W || 1920;
  const paint = balanceTonePaint(tone, B.TONE.FORM, other);
  const pill = el("rect", "bal-tone", pan.g, { fill: paint.fill, stroke: paint.stroke, "stroke-width": paint.strokeW });
  const lab = el("text", "bal-label", pan.g, { x: 0, y: 0, "text-anchor": "middle", style: balToneLabelStyle(paint) });
  lab.textContent = L.label;
  const fit = balanceNameFit(side, E.x, balanceNameWidth(balNameW(lab, L.label), tone), b, g.cx, stageW);
  if (fit.size !== B.LABEL_PX) lab.setAttribute("style", balToneLabelStyle(paint, fit.size));
  const row = balanceToneRow(g, pan.pictured, pose.y, fit.size, paint.face), inset = paint.strokeW / 2;
  const f2 = (v) => v.toFixed(2), ph = row.h - 2 * inset;
  lab.setAttribute("x", f2(fit.x - (paint.face === "kalam" ? B.NAME_SLANT : 0) - E.x));
  lab.setAttribute("y", f2(row.baseline));
  Object.entries({ x: f2(fit.x - E.x - fit.w / 2 + inset), y: f2(row.top + inset), width: f2(fit.w - 2 * inset), height: f2(ph),
                   rx: f2(ph / 2) }).forEach(([k, v]) => pill.setAttribute(k, v));
  const op = (pan.pictured ? chipLand(t, +L.at + balanceContactS()).fade : pose.fade).toFixed(3);
  lab.setAttribute("opacity", op);
  pill.setAttribute("opacity", op);
  lab.dataset.row = pan.pictured ? "pictured" : "bare";
  lab.dataset.fit = fit.step;
  lab.dataset.tone = pill.dataset.tone = tone;
  pill.dataset.form = B.TONE.FORM;
};

/* THE NAMES, one pass after the pans: each is measured at LABEL_PX, fitted (balanceNameFit: fit, shrunk, overhang,
   pinned) and given its row (balanceNameRow) - a bare name fades in with its load, a pictured load's as the load touches.
   A side with a `tone` wears its pill instead (balTonedName). */
const balNames = (ctx, P, b, pans, inkKey) => {
  const { el, sp, t } = ctx, B = BALANCE, g = P.g, stageW = ctx.STAGE_W || 1920;
  const ink = B.INK[inkKey], other = B.INK[inkKey === "cream" ? "charcoal" : "cream"];
  for (const side of BALANCE_SIDES) {
    const L = sp[side] || {}, pose = P.loads[side], pan = pans[side];
    if (!pose || !pan || !(typeof L.label === "string" && L.label)) continue;
    const E = P.ends[side];
    if (balanceTone(L)) { balTonedName(ctx, side, L, pose, pan, E, b, g, other); continue; }
    const lab = el("text", "bal-label", pan.g, { x: 0, y: 0, "text-anchor": "middle", style: balLabelStyle(ink, other) });
    lab.textContent = L.label;
    const fit = balanceNameFit(side, E.x, balanceNameWidth(balNameW(lab, L.label), null), b, g.cx, stageW);   /* by its PAINTED width */
    if (fit.size !== B.LABEL_PX) lab.setAttribute("style", balLabelStyle(ink, other, fit.size));
    lab.setAttribute("x", (fit.x - B.NAME_SLANT - E.x).toFixed(2));   /* its PAINTED box centred where the fit put it */
    lab.setAttribute("y", balanceNameRow(g, pan.pictured, pose.y).toFixed(2));
    lab.setAttribute("opacity", (pan.pictured ? chipLand(t, +L.at + balanceContactS()).fade : pose.fade).toFixed(3));
    lab.dataset.row = pan.pictured ? "pictured" : "bare";
    lab.dataset.fit = fit.step;
  }
};

const balLoad = (ctx, pg, L, pose, g, inkKey, id) => {
  const { el, A } = ctx, B = BALANCE, s = g.load;
  const ink = B.INK[inkKey];
  const m = squashMatrix(pose.theta, pose.alpha), base = g.H + g.pd * 0.5;   /* the load's foot sits in the bowl */
  const lg = el("g", "bal-load", pg, { opacity: pose.fade.toFixed(3),
    transform: "translate(0 " + (base + pose.y).toFixed(2) + ") matrix(" + m.map((v) => v.toFixed(5)).join(" ") + " 0 0)" });
  const geo = L.icon ? chipGeometry(A ? A["icon:" + L.icon] : null) : null;
  const src = L.prop && A ? A["prop:" + L.prop] : null;
  if (geo) {
    const vb = geo.vb || [0, 0, 24, 24], k = s / Math.max(vb[2] || 1, vb[3] || 1);
    const gg = el("g", "bal-glyph", lg, { transform: "translate(" + (-s / 2).toFixed(2) + " " + (-s).toFixed(2) + ") scale(" + k.toFixed(4) + ") translate(" + (-vb[0]) + " " + (-vb[1]) + ")",
      style: "fill:none;stroke:" + ink + ";stroke-width:" + B.GLYPH_W + ";stroke-linecap:round;stroke-linejoin:round" });
    geo.el.forEach((n) => el(n.t, "", gg, Object.assign({}, n.a, { style: "fill:none;stroke:" + ink + ";stroke-width:" + B.GLYPH_W + ";stroke-linecap:round;stroke-linejoin:round" })));
    return true;
  }
  if (src) {
    const im = { href: src, x: (-s / 2).toFixed(2), y: (-s).toFixed(2), width: s.toFixed(2), height: s.toFixed(2), preserveAspectRatio: "xMidYMax meet" };
    balHatch(ctx, lg, id, { x: -s / 2, y: -s, w: s, h: s }, (host) => el("image", "", host, im), B.HATCH_GROUND[inkKey], 1);
    el("image", "bal-prop", lg, im);
    return true;
  }
  return false;   /* no picture: the NAME is the load (balNames stands it on the rim, never in the solid bowl) */
};

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player): the declaration, the clock, the
   layer and the shared helpers by name - `propHatchLines` among them (P70 T7), the prop's own hatch. */
export function paintBalance(ctx) {
  const { sp, t, svg, el, resolveTarget, drawOn, idle, hash, seed, si } = ctx;
  const b = resolveTarget(sp.target);
  if (!b || !(b.w > 0 && b.h > 0)) return;   /* the targeting law: a balance needs its ROOM */
  const B = BALANCE, P = balancePose(sp, t, b), g = P.g, D = P.draw;
  const inkKey = balanceInk(sp), ink = B.INK[inkKey], other = B.INK[inkKey === "cream" ? "charcoal" : "cream"];
  const ix = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 997)) : { scale: 1, dx: 0, dy: 0 };
  const id = "bal" + ((seed >>> 0).toString(36)) + "-" + (si | 0);
  const root = el("g", "balance", svg, { opacity: P.leave.toFixed(3),
    transform: "translate(" + (g.cx + ix.dx).toFixed(2) + " " + (g.fy + ix.dy).toFixed(2) + ") scale(" + ix.scale.toFixed(5) + ") translate(" + (-g.cx).toFixed(2) + " " + (-g.fy).toFixed(2) + ")" });
  const stroke = { fill: "none", stroke: ink, "stroke-width": B.STROKE_W, "stroke-linejoin": "round", "stroke-linecap": "round" };
  /* THE FULCRUM, on its resting hatch */
  const base = balanceBase(g);
  const shapes = [balPoly(base.post), balD(base.foot) + " Z"];
  balHatch(ctx, root, id + "-base", base.box, (host) => shapes.forEach((d) => el("path", "", host, { d })), B.HATCH_GROUND[inkKey], D.hatch);
  if (D.baseFill > 0) shapes.forEach((d) => el("path", "bal-base-fill", root, { d, fill: ink, opacity: D.baseFill.toFixed(3) }));
  if (D.base > 0) shapes.forEach((d) => drawOn(el("path", "bal-base", root, Object.assign({ d }, stroke)), D.base));
  /* THE BEAM: two arms out of the pivot, turned by theta about it; its angle is written where a test reads it */
  const beam = el("g", "bal-beam", root, { transform: "rotate(" + P.deg.toFixed(4) + " " + g.cx.toFixed(2) + " " + g.py.toFixed(2) + ")" });
  beam.dataset.deg = P.deg.toFixed(4);
  if (D.beam > 0) {
    for (const side of BALANCE_SIDES) {
      const pts = balanceArm(g.A, side).map((p) => ({ x: p.x + g.cx, y: p.y + g.py }));
      drawOn(el("path", "bal-arm", beam, { d: balD(pts), fill: "none", stroke: ink, "stroke-width": B.BEAM_W, "stroke-linecap": "round" }), D.beam);
    }
    if (D.beam >= 1) for (const side of BALANCE_SIDES)
      el("circle", "bal-ring", beam, { cx: (g.cx + balSign(side) * g.A).toFixed(2), cy: g.py.toFixed(2), r: B.END_R, fill: other, stroke: ink, "stroke-width": B.STROKE_W });
    el("circle", "bal-pin", beam, { cx: g.cx.toFixed(2), cy: g.py.toFixed(2), r: (B.KNOB_R * Math.min(1, D.beam * 2)).toFixed(2), fill: ink });
  }
  /* THE PANS, plumb: each group is TRANSLATED to its arm's end, never turned */
  const pans = {};
  if (D.pan > 0) for (const side of BALANCE_SIDES) {
    const E = P.ends[side], L = sp[side] || {};
    const pg = el("g", "bal-pan", root, { transform: "translate(" + E.x.toFixed(2) + " " + E.y.toFixed(2) + ")" });
    pg.dataset.side = side;
    for (const sx of [-1, 1]) drawOn(el("path", "bal-hanger", pg, { d: balD(balanceHanger(sx * g.pw / 2, g.H)), fill: "none", stroke: ink, "stroke-width": B.HANGER_W }), D.pan);
    const bowl = balD(balanceBowl(g.pw, g.pd, g.H));
    if (D.panFill > 0) el("path", "bal-bowl-fill", pg, { d: bowl + " Z", fill: ink, opacity: D.panFill.toFixed(3) });
    drawOn(el("path", "bal-bowl", pg, Object.assign({ d: bowl + " Z" }, stroke)), D.pan);
    const pose = P.loads[side];
    if (!pose) continue;
    pans[side] = { g: pg, pictured: balLoad(ctx, pg, L, pose, g, inkKey, id + "-" + side) };
  }
  balNames(ctx, P, b, pans, inkKey);
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can import this
   file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.balance = paintBalance;
