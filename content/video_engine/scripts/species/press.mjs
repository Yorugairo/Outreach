/* species/press.mjs - THE PRESS CARD STACK (P50 T3; doc 29 §9.27 rows "Push hand-off" and "Squiggle marks";
   Bravos shots 5-10: their claims arrive as cards, and each new one pushes the last back into a lit pile).
   SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN press
   and KINETICS:END, AFTER ease and spring - it imports both, and the import order IS the region order.

   THE MODULE RULE (the operator, 2026-09-11) applies, with one difference from chip.mjs: a press card is a
   DOCK kind, not a species kind, so this module registers NO painter. The dock loop owns the card (a card is
   a card: the frame, the masthead, the lifecycle) and reads its whole pose from the pure functions here; the
   only thing new to the SPECIES grammar is the `phrase` target and the `underline` form of a callout, whose
   clock is underlineFrac below.

   WHEN: the sentence QUOTES someone (SPECIES-BY-SENTENCE row 1). One card is a quotation; a STACK is a
   sequence of them - three claims on three words, the newest lit and the older ones fanned behind it.

   THE LAW, all of it a pure function of t through uNew (the NEWEST card's landing fraction):
     land   - the newest card lands on the badge spring (kinetics/spring.mjs springPop, the POP preset,
              Mp = 4 %) over LAND_S, from POP_FROM and DROP_PX above its place - the dock's own arrival.
     push   - every OLDER card moves from the pose it held one step forward to the pose of its new depth,
              on Flash & Hogan's minimum-jerk quintic over PUSH_S (shorter than LAND_S: the pile has taken
              the push before the newest has finished overshooting - cause, then effect, never in step).
              The hand-off itself is §9.27's push: x (PUSH_DX), scaleX (SQUEEZE) and skewX (SKEW_DEG) on a
              sin(pi p) pulse, zero at both ends - the shove reads on the card being pushed, and leaves
              nothing behind. Never a fade between two cards: a fade is a dissolve, and a dissolve is the
              thing E45 refuses.
     settle - the pile is a FAN: each step behind sits STEP_PX higher (so every masthead stays readable),
              STEP_SCALE smaller and DIM dimmer, floored at BACK_SCALE and DIM_MIN - deep in the pile a card
              is still a card, never a grey rectangle.
     gone   - a card off its span is not in the stack at all; the painter passes the LIVE count as n, so a
              card that has left closes the gap instead of leaving a hole.
   Nothing is stored: every visual reads from t, the dock's enter and the live count, so a scrubbed frame is
   the played frame. The dials below are ours to tune (42 §42.5), not findings. */
import { minJerk } from "../kinetics/ease.mjs";
import { springPop } from "../kinetics/spring.mjs";

export const PRESS = Object.freeze({
  LAND_S: 0.5,      /* the newest card's landing clock - the dock's own DOCK_POP_S 0.45 plus a beat, this card being pushed in rather than popped up */
  POP_FROM: 0.88,   /* the scale it springs from: nearer its size than the dock's 0.85, because the ARRIVAL here is the push, not the pop */
  DROP_PX: 22,      /* ... and how far above its place it falls from, on the same spring */
  FADE_S: 0.12,     /* the opacity ramp - the dock's DOCK_FADE_S, so a press card enters like every other card */
  PUSH_S: 0.38,     /* the older cards' slide back: shorter than LAND_S so the pile has settled while the newest is still overshooting */
  STEP_PX: 30,      /* the floor on how much higher each step behind sits (a small card still fans) */
  STEP_H: 0.22,     /* ... and the step as a share of the CARD'S OWN height, which is what actually keeps every masthead
                       strip readable: the painter passes max(STEP_PX, H * STEP_H), so the fan reads the same on a
                       headline crop of any depth instead of being a number tuned to one card */
  STEP_SCALE: 0.05, /* ... and this much smaller: a step of depth the eye reads without a perspective (it eats into the
                       reveal above - the card shrinks about its bottom edge, so its top comes DOWN as it goes back) */
  BACK_SCALE: 0.78, /* the floor on that shrink: deep in the pile a card is still legible as a card */
  DIM: 0.22,        /* what each step behind dims by - the newest is the lit one (Bravos 5-10) */
  DIM_MIN: 0.34,    /* the floor on that dim: a card the sentence may come back to never goes to nothing */
  PUSH_DX: 26,      /* §9.27's push: how far the shoved card is carried sideways at the peak of the shove */
  SQUEEZE: 0.035,   /* ... how much it compresses on x there (scaleX: the shove hits its edge) */
  SKEW_DEG: 2.4,    /* ... and how far it leans (skewX) - small: a lean, never a tumble */
  UNDERLINE_EASE: 3,/* the underline's draw curve: the hand decelerates into the end of the phrase (1 - (1 - u)^3) */
  /* R26-55 - THE PULLED PHRASE AS LIVE TYPE: the dials of the fit below. The FACE is the one the OPERATOR rules on. */
  FACE: "house",    /* the stand-in display face until the operator reads the three off their proof frames (gate 7) */
  TYPE_MIN: 12,     /* the fit's floor in stage px: under this the phrase is a smudge whatever the surface */
  TYPE_MAX: 220,    /* ... and its ceiling: a pulled phrase is a headline, never a title card */
  TYPE_Q: 0.25,     /* the quantum the size is quantised to, so ONE box always gives exactly one size */
  LINE_H: 1.08,     /* the leading of a display line: tight, the way a masthead sets a headline */
  WORD_AIR: 0.012,  /* the share of the width kept clear, so a line measured here never takes a second one in the DOM */
  PROV_SHARE: 0.3,  /* the provenance strip's share of the paper left under the type rows (the raster, still cited) */
  PROV_GAP: 0.04,   /* ... and the air between the phrase and that strip, on the same paper */
  PHONE_FLOOR: 17,  /* E62's quiet-caption floor in CSS px on a phone - what a proof frame is READ against, never clamped to */
});

/* ================= THE FACES OFFERED (human gate 7 - the operator's choice, never ours) =================
   Three candidates for the stand-in display face a pulled phrase is set in, and all three are already on the
   page: the template downloads exactly ONE webfont (Kalam, the ledger's hand) and nothing here adds a second -
   every family below resolves against the faces the renderer already has. The operator reads them off the proof
   frames (`press-stack@face-serif`, `press-stack@face-condensed`, against the default in `press-stack`) and
   rules; until then the DEFAULT stands and no cut changes.
   A face is a DIAL on the timeline (`kinetics.press_face`), not a capability flag: it turns nothing on or off,
   it names which of the three is in the frame. */
export const PRESS_FACES = Object.freeze({
  house: Object.freeze({ id: "house", weight: 800, track: "-0.012em",
    family: 'Inter, "Segoe UI", system-ui, sans-serif',
    label: "the house display face - the template's own stack at the caption's display weight" }),
  serif: Object.freeze({ id: "serif", weight: 700, track: "0em",
    family: 'Georgia, "Times New Roman", serif',
    label: "a masthead serif - the quoted headline set the way the paper set it" }),
  condensed: Object.freeze({ id: "condensed", weight: 700, track: "0.004em",
    family: '"Arial Narrow", "Bahnschrift Condensed", "Roboto Condensed", "Segoe UI", sans-serif',
    label: "a condensed grotesque - more words to a line, the tabloid's own pull" }),
});

/* the face a name asks for; an unknown name (or none at all) is the house face, so a typo can never blank a card */
export const pressFace = (name) => PRESS_FACES[String(name == null ? "" : name).toLowerCase()] || PRESS_FACES[PRESS.FACE];

const p01 = (v) => Math.min(1, Math.max(0, v));

/* THE RESTING POSE of the card d steps behind the newest: the fan, with its two floors. */
export const pressRest = (d, o = {}) => {
  const P = Object.assign({}, PRESS, o), k = Math.max(0, d | 0);
  return { dy: k ? -P.STEP_PX * k : 0, scale: Math.max(P.BACK_SCALE, 1 - P.STEP_SCALE * k),
           opacity: Math.max(P.DIM_MIN, 1 - P.DIM * k) };
};

/* THE STACK at t: the pose of the i-th card of n LIVE cards while the newest (i = n - 1) arrives with
   uNew in [0, 1] over LAND_S. The newest springs; everything behind it is pushed one step back. */
export const pressStack = (i, n, uNew, o = {}) => {
  const P = Object.assign({}, PRESS, o);
  const total = Math.max(1, n | 0), idx = Math.min(Math.max(0, i | 0), total - 1);
  const d = total - 1 - idx, u = p01(uNew);
  if (d === 0) {                                    /* the newest: the badge spring, and no push of its own */
    const s = springPop(u);
    return { depth: 0, push: 0, dx: 0, dy: (s - 1) * P.DROP_PX, scale: P.POP_FROM + (1 - P.POP_FROM) * s,
             sx: 1, skew: 0, opacity: 1, fade: p01(u * P.LAND_S / P.FADE_S) };
  }
  const p = minJerk(p01(u * P.LAND_S / P.PUSH_S));  /* the push's own, shorter clock, read off the newest's */
  const a = pressRest(d - 1, P), b = pressRest(d, P);
  const pulse = Math.sin(Math.PI * p);              /* zero at both ends: the shove leaves nothing behind */
  return { depth: d, push: p,
           dx: -P.PUSH_DX * pulse, dy: a.dy + (b.dy - a.dy) * p,
           scale: a.scale + (b.scale - a.scale) * p, sx: 1 - P.SQUEEZE * pulse,
           skew: P.SKEW_DEG * pulse, opacity: a.opacity + (b.opacity - a.opacity) * p, fade: 1 };
};

/* THE UNDERLINE's draw fraction at u (its elapsed clock over the stroke's window): the hand runs out fast
   and decelerates into the last letter, exactly as the squiggle's stroke does under a stressed word. */
export const underlineFrac = (u, o = {}) => {
  const P = Object.assign({}, PRESS, o);
  return 1 - Math.pow(1 - p01(u), P.UNDERLINE_EASE);
};

/* THE CARD'S LIVE GEOMETRY: the element box {x, y, w, h} in stage px with the pose applied, and any box
   INSIDE it (the phrase) carried through the same transform - so the underline rides the card wherever the
   stack has put it. The transform is written about the card's bottom centre, the pile's own hinge:
     x' = ox + scale * sx * ((x - ox) + tan(skew) * (y - oy)) + dx
     y' = oy + scale * (y - oy) + dy
   The CSS the painter writes must be the same composition, in the same order, about the same origin. */
export const pressXf = (box, pose) => {
  const ox = box.x + box.w / 2, oy = box.y + box.h, tan = Math.tan((pose.skew || 0) * Math.PI / 180);
  const s = pose.scale, sx = s * (pose.sx == null ? 1 : pose.sx);
  const at = (x, y) => [ox + sx * ((x - ox) + tan * (y - oy)) + (pose.dx || 0), oy + s * (y - oy) + (pose.dy || 0)];
  return (q) => {
    const pts = [at(q.x, q.y), at(q.x + q.w, q.y), at(q.x, q.y + q.h), at(q.x + q.w, q.y + q.h)];
    const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
    return { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) };
  };
};

/* the phrase box the compiler wrote as FRACTIONS of the card (press_card.py), in the card image's own px */
export const pressPhraseBox = (img, phrase) => {
  if (!img || !phrase) return null;
  const f = ["x0", "y0", "x1", "y1"].map((k) => +phrase[k]);
  if (f.some((v) => !Number.isFinite(v))) return null;
  return { x: img.x + f[0] * img.w, y: img.y + f[1] * img.h, w: (f[2] - f[0]) * img.w, h: (f[3] - f[1]) * img.h };
};

/* ================= THE EMBEDDED CARD'S REFLOW (P50 T7 second watch; the operator, 2026-09-12: "isn't the whole
   point of the TV to use it as the entire surface?") =================
   A card that lands on a declared surface FILLS it: its unprojected box is the quad's WHOLE rectangle, so the box
   carries the SURFACE'S aspect, never the card's. The card therefore reflows into that box - its masthead at the
   top, its pulled phrase in the middle, its by-line at the foot - and two pure laws decide the reflow:

     TYPE    - every px the card is authored at (its frame, its padding, its masthead, its by-line) multiplies by
               ONE number: the box's width over the width the card's CSS is written at. One number on both axes, so
               no glyph is ever squeezed - a letter has the same aspect on a wide TV as on a tall poster, and the
               surface gives ground in SIZE only (E62 / E65: the box gives ground in scale, never in legibility).
               No floor is imposed here: type floored above its own card would overrun the surface it is read on.
               The compiler's floor (a quarter of the stage wide) is what keeps a surface big enough to read, and
               `phoneCssPx` states what the result reads as in the hand, against E62's 17 CSS px.
     PICTURE - the pulled phrase keeps its OWN aspect. It takes the box's full inner width unless the height left
               between the masthead and the by-line binds, and then it takes that height and centres in the width.
               Never both: a picture fitted on two axes is a stretch, and a stretched headline is a lie.
   Both are closed form in the box, so a card on a surface is a pure function of t like everything else. */
export const pressTypeScale = (boxW, designW) => (boxW > 0 && designW > 0 ? boxW / designW : 1);

/* the picture's box inside the paper left for it: {w, h} at the picture's own aspect (h / w), or null when the
   aspect is unknown - the caller then leaves the picture's CSS alone rather than guessing a height. */
export const pressPictureFit = (availW, availH, aspect) => {
  const a = +aspect > 0 ? +aspect : 0;
  if (!a || !(availW > 0) || !(availH > 0)) return null;
  const h = a * availW;
  return h <= availH ? { w: availW, h } : { w: availH / a, h: availH };
};

/* WHAT A STAGE PX READS AS IN THE HAND. E62's own arithmetic: 48 px of a 1080-wide short is 17 CSS px on a phone,
   which is the quiet caption's floor - so a phone is 1080 * 17 / 48 CSS px wide. The STAGE'S width is passed in
   (the player speaks in STAGE_W, and neither stage size is written here); a stage with no width reads as nothing.
   The reflow does not clamp to the floor - this is what a proof frame is measured against. */
export const PHONE_CSS_W = 382.5;
export const phoneCssPx = (stagePx, stageW) => (+stageW > 0 ? (+stagePx || 0) * PHONE_CSS_W / +stageW : 0);

/* ================= THE PULLED PHRASE IS LIVE TYPE (R26-55; the limit E66 found) =================
   E66 gave a card the whole surface, and the reflow above scaled the card's ONE picture into it. That picture
   carries the pulled phrase - `press_card.py` cuts it out of the source screenshot - and a raster cannot RE-LINE:
   on a tall poster the phrase takes the surface's width, keeps the crop's own line breaks, and reads at 13.4 CSS
   px in the hand against E62's 17. Type can re-line. So:

   THE LAW. The phrase's WORDS travel beside the raster as data (`phrase_text` on the card's meta, through the
   press dock onto the timeline), and the card sets them as LIVE TYPE, re-lined to the box it was given:
     size    - the LARGEST size at which the words wrap into lines that all fit the paper's width and whose
               total height fits the paper's height. One size for the whole phrase (a headline is one size), found
               by bisection between TYPE_MIN and TYPE_MAX and quantised to TYPE_Q, so one box gives exactly one
               size and a seek paints the frame the play-through paints.
     lines   - the greedy wrap at that size, WRITTEN OUT: the card paints one element per line, so the DOM never
               re-wraps what was measured here and a line can never take a second one behind our back.
     face    - PRESS_FACES above, by the `press_face` dial; the house face until the operator rules (gate 7).
     floor   - NOTHING is clamped. `phoneCssPx(size, stageW)` states what the fit reads as in the hand and
               PHONE_FLOOR is what a proof frame is judged against - type forced above the surface it is read on
               would overrun the surface, which is the mistake in the other direction.
   THE RASTER STAYS. It is the PROVENANCE strip under the words: the crop the phrase was pulled from, still on the
   card, still the file `press_card.py` recorded the sha256 of, with the masthead and the date citing it. It takes
   PROV_SHARE of the paper (fitted on one axis by pressPictureFit, so it is never stretched) and the phrase takes
   the rest - which is why a card's total height does not move when the words arrive.
   Everything here is a pure function of the box and the measured words: a card with no `phrase_text` gets no live
   type at all, and every build that has none renders exactly as it did. */

/* the phrase's words, in order: whitespace collapsed, nothing else touched (the operator's own text) */
export const pressWords = (text) => String(text == null ? "" : text).replace(/\s+/g, " ").trim().split(" ").filter(Boolean);

/* THE GREEDY WRAP at `size`: `w1[i]` is word i's width per px of font size and `space1` the space's, both measured
   in the face ONCE at a reference size (widths are linear in the size; WORD_AIR is the slack that keeps them so).
   Returns one entry per line - the words' indices and the line's width in px. A word wider than the paper takes a
   line of its own and overruns it, which is what makes the fit below reject that size rather than hide it. */
export const pressWrap = (w1, space1, size, availW) => {
  const s = +size > 0 ? +size : 0, sp = (+space1 || 0) * s, lines = [];
  let words = [], w = 0;
  for (let i = 0; i < (w1 || []).length; i++) {
    const ww = (+w1[i] || 0) * s;
    if (words.length && w + sp + ww > availW) { lines.push({ words, w }); words = [i]; w = ww; }
    else { w += (words.length ? sp : 0) + ww; words.push(i); }
  }
  if (words.length) lines.push({ words, w });
  return lines;
};

/* THE FIT: the largest quantised size whose wrap fits the paper on both axes, with the lines it gives.
   `fits` false means even TYPE_MIN overruns the paper - the caller then sets TYPE_MIN and the build says so,
   rather than a card silently dropping words. */
export const pressPhraseFit = (w1, space1, availW, availH, o = {}) => {
  const P = Object.assign({}, PRESS, o);
  const paper = (+availW > 0 ? +availW : 0) * (1 - P.WORD_AIR), h = +availH > 0 ? +availH : 0;
  const at = (s) => {
    const lines = pressWrap(w1, space1, s, paper);
    const widest = lines.reduce((m, l) => Math.max(m, l.w), 0);
    return { lines, ok: widest <= paper && lines.length * s * P.LINE_H <= h };
  };
  if (!(w1 || []).length || !(paper > 0) || !(h > 0)) return null;
  const top = at(P.TYPE_MAX);
  if (top.ok) return { size: P.TYPE_MAX, lines: top.lines, lineH: P.TYPE_MAX * P.LINE_H,
                       h: top.lines.length * P.TYPE_MAX * P.LINE_H, fits: true };
  let lo = P.TYPE_MIN, hi = P.TYPE_MAX;
  const floor = at(lo);
  if (!floor.ok) return { size: P.TYPE_MIN, lines: floor.lines, lineH: P.TYPE_MIN * P.LINE_H,
                          h: floor.lines.length * P.TYPE_MIN * P.LINE_H, fits: false };
  while (hi - lo > P.TYPE_Q) {
    const mid = (lo + hi) / 2;
    if (at(mid).ok) lo = mid; else hi = mid;
  }
  const size = Math.max(P.TYPE_MIN, Math.floor(lo / P.TYPE_Q) * P.TYPE_Q), got = at(size);
  return { size, lines: got.lines, lineH: size * P.LINE_H, h: got.lines.length * size * P.LINE_H, fits: got.ok };
};

/* THE CARD'S COLUMN: how the paper left under the type rows (the masthead, the by-line) is split between the
   phrase and the provenance strip. The strip is the raster fitted on ONE axis inside PROV_SHARE of that paper, so
   its height is the picture's own - a wide crop takes less than its share and hands the difference to the words.
   `null` when there is no paper to split; `prov` null when the picture's aspect is not on record, and the caller
   then leaves the picture's CSS alone (the reflow's own rule). */
export const pressColumn = (paperH, availW, aspect, o = {}) => {
  const P = Object.assign({}, PRESS, o);
  const paper = +paperH > 0 ? +paperH : 0, w = +availW > 0 ? +availW : 0;
  if (!(paper > 0) || !(w > 0)) return null;
  const prov = pressPictureFit(w, paper * P.PROV_SHARE, aspect);
  const provH = prov ? prov.h : paper * P.PROV_SHARE, gap = paper * P.PROV_GAP;
  return { prov, provH, gap, phraseH: Math.max(0, paper - provH - gap) };
};

/* WHAT THE UNDERLINE RIDES (E56's one exception). With live type the phrase is the TYPE's box, not a rectangle of
   the raster: the words moved, so the mark under them moves with them. A card with no live type falls back to the
   phrase box the compiler wrote as fractions of the crop, which is what every card did before R26-55. */
export const pressPhraseTarget = (live, img, phrase) =>
  (live && +live.w > 2 && +live.h > 2 ? { x: +live.x, y: +live.y, w: +live.w, h: +live.h } : pressPhraseBox(img, phrase));

/* WHAT A FIT READS AS IN THE HAND, and whether it clears E62's floor. Reported, never enforced (see THE LAW). */
export const pressPhoneRead = (stagePx, stageW, o = {}) => {
  const P = Object.assign({}, PRESS, o), css = phoneCssPx(stagePx, stageW);
  return { css: Math.round(css * 100) / 100, floor: P.PHONE_FLOOR, clears: css >= P.PHONE_FLOOR };
};
