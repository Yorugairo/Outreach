/* SPACE: stage */
/* species/equation.mjs - THE EQUATION ROW (P70 T6, was P69 T56; the Bravos harvest v2's T38 "Equation row: inputs,
   relation, signed result", DOM 09:30-09:39, and A60 "Equation built in spoken order"). SOURCE OF TRUTH, inlined into
   the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN equation and KINETICS:END, AFTER spring (it uses
   springPop) and figure (it writes each term with figureGlyph, the hand's glyph-by-glyph law), and after the engine's
   SPECIES_PAINTERS declaration, which the registration reaches. Its region sits immediately after freeze's.

   WHEN (`SPECIES_WHEN["equation"]`, build_scene_timeline_f.py): the arithmetic IS the claim ("real yield = coupon -
   inflation"; H row 18's "at a fifth of the index, if the AI names fall by half, that erases ten percent").

   THE FORM, all of it a pure function of the declaration and t:
     the row    the terms, the operators between them, "=" and the result, in the order they are SPOKEN, laid out once
                in the declared region: centred, one type size for every item (the region's height, shrunk to fit its
                width, never under the s90 floor FLOOR_PX), the baseline BASE_DY of that size under the region's middle
                (the figure's own drop). Every slot stands from the first frame, so a later term never moves an earlier
                one: the row is read left to right as it is heard, and a seek lands exactly where a play does.
     a term     written by the hand on its OWN word (`at`): glyph after glyph over WRITE_S by figureGlyph - the page
                figure's law, so a number written on the stage and one written at a datum are one hand.
     operator   springs in between (springPop, POP_MP) OP_LEAD before the NEXT term's word - "minus" is heard just
                before the thing subtracted, so the sign is already there when the eye goes to it; `=` the same way
                before the result.
     result     written on its word like a term; a negative one in the page's `neg` token (E28: a fall is written with
                its minus, in red). Its truth is the compiler's (it computes the row left to right and refuses a
                written result that disagrees beyond its text's precision); this painter writes what it is given.
     the leave  the whole row fades over the window's last OUT_S; the compiler keeps the result's write inside it.
     a label    (review F7) an optional caption under a term or the result, naming the number (Bravos DOM 09:35's
                "Treasury Bonds" / "Real Yield"): Inter at the floor in the page's quiet ink, centred on its item's
                slot, arriving with its item's write. Round 3: the numbers stand a MEASURED step above their captions
                (the numbers' cap STEP x the caption's) - a tight region gives up its gaps, never the numbers.
     the signs  the operators and "=" are SET in the sans (review F8: Kalam's x reads as a letter x); a number's typed
                hyphen is written as the true minus, and the result's red is its TEXT's sign (review F4).
   Our hand: chalk on the charcoal board (the template's --lp-chalk), the halo the agenda's rows wear, in the bracket's
   handwriting (Kalam). The stage layer sits OUTSIDE the page's `.lp`, where the --lp-* tokens are declared, so this
   module carries their hex; tests/test_equation_row.py pins NEG and CHALK to the template's literals. */
import { springPop } from "../kinetics/spring.mjs";
import { FIGURE, figureGlyph } from "./figure.mjs";

export const EQUATION = Object.freeze({
  FLOOR_PX: 59.08,     /* the s90 floor (ledger_page.CARD_TYPE_PX): no item is ever written smaller, in stage px */
  FS_K: 0.62,          /* the type as a share of the region's height, before the width has its say */
  GAP_K: 0.3,          /* the daylight between two items, in type sizes */
  WRITE_S: 0.6,        /* a term's (and the result's) write window: figureGlyph over it, the last glyph whole at 0.6 (n + 0.6) / n of it */
  OP_LEAD: 0.12,       /* an operator (and "=") springs this long BEFORE the next term's word ... */
  OP_S: 0.34,          /* ... over one word's pitch at 178 WPM (the count array's STEP) */
  POP_MP: 0.08,        /* its overshoot: a mark landing on a word pops one notch past the standing pop (SPRING.MP 0.04) - our dial */
  OUT_S: 0.25,         /* the row fades over the window's last quarter second: nothing on the stage pops out */
  CHAR_W: FIGURE.FIGURE_CHAR_W,   /* the advance per character when nothing can measure (node, no glyphs yet) - the figure's */
  BASE_DY: FIGURE.BASE_DY,        /* the baseline's drop below the region's middle, in type sizes - the figure's */
  CHALK: "#F2F2F2",    /* the template's --lp-chalk */
  NEG: "#FF4D4D",      /* the template's --lp-neg (E28, E67's electric red) */
  HALO: "rgba(27,30,35,.85)",   /* the agenda's row halo, so the row reads over a bar or a line */
  HALO_PX: 8,
  FACE: "Kalam, Inter, Arial, sans-serif",   /* the bracket's hand (.bklab): the numbers are written */
  WEIGHT: "700",
  OP_FACE: "Inter, Arial, sans-serif",       /* the operators and "=" are SET, in the sans: Kalam's x reads as a letter x (review F8) */
  /* THE LABELS (review F7, E28: the label is data): an optional caption under each term and the result, naming what the
     number is - Bravos DOM 09:35's "Treasury Bonds" / "Inflation" / "Real Yield" - in the page's quiet ink */
  LABEL_PX: 59.08,     /* the s90 floor: a caption is never written smaller */
  LABEL_INK: "#b8c4d0",   /* the engine's LP_INK.deemph (7.5:1 on the board) - the page's quiet ink */
  LABEL_FACE: "Inter, Arial, sans-serif",
  LABEL_WEIGHT: "400",   /* quieter than the numbers it names: the caption is read second (round 3: 500 read heavier than the row) */
  LABEL_CHAR_W: 0.55,  /* the caption's advance per character when nothing can measure */
  LABEL_DROP: 0.85,    /* the caption's baseline under the row's glyph bottom, in label sizes: close enough to belong ... */
  DROP_MIN: 0.5,       /* ... and as close as a tight region may pull it (the region gives up daylight, never the numbers) */
  LABEL_DESC: 0.25,    /* the caption's descender under its baseline, in label sizes (the g of "weight") */
  GAP_MIN: 0.15,       /* the least daylight between two items a tight region may leave, in type sizes */
  /* THE STEP over the captions (round 3): each face's cap height per em, MEASURED in the served player with canvas
     measureText at 1000 px (scratchpad p70-t6/logs/r3-cap-heights.json) - Kalam 700 digits 765.625, the caption face's
     "HIE" 671.875 - and the step the numbers' cap stands at over the caption's (the parent asked >= 1.4; 1.5 is ours) */
  TERM_CAP_K: 0.7656,
  LABEL_CAP_K: 0.6719,
  STEP: 1.5,
});

/* the operators the grammar takes, as the hand writes them: an author may type the ASCII x or - */
export const EQUATION_OPS = Object.freeze({ "×": "×", x: "×", "−": "−", "-": "−", "+": "+", "÷": "÷" });

const eq01 = (v) => Math.min(1, Math.max(0, v));

/* a number as the hand writes it: a typed hyphen is the true minus (review F4) */
export const equationSigned = (text) => String(text ?? "").replace(/-/g, "−");
/* E28: a result is red when its TEXT falls - the minus before the first digit (after a currency too), never a value */
export const equationFalls = (text) => /^[^0-9.½¼¾⅓⅔⅕⅛]*−/.test(equationSigned(text));
const eqLabel = (it) => (it && typeof it.label === "string" && it.label.trim() ? it.label : undefined);

/* THE ROW IN SPOKEN ORDER: term, operator, term[, operator, term], "=", result - each with the instant it arrives */
export const equationItems = (sp) => {
  const terms = (sp && sp.terms) || [], ops = (sp && sp.ops) || [], out = [];
  terms.forEach((tm, i) => {
    if (i > 0) out.push({ role: "op", text: EQUATION_OPS[ops[i - 1]] || String(ops[i - 1] ?? ""), at: +tm.at - EQUATION.OP_LEAD });
    out.push({ role: "term", text: equationSigned(tm.text), at: +tm.at, label: eqLabel(tm) });
  });
  const r = (sp && sp.result) || {};
  out.push({ role: "eq", text: "=", at: +r.at - EQUATION.OP_LEAD });
  out.push({ role: "result", text: equationSigned(r.text), at: +r.at, neg: equationFalls(r.text), label: eqLabel(r) });
  return out;
};

/* one item at t: a written item's glyph opacities (the hand), an operator's spring scale (0 before its instant) */
export const equationItemAt = (it, t) => {
  const glyphs = Array.from(it.text);
  if (it.role === "op" || it.role === "eq") {
    const u = eq01((t - it.at) / EQUATION.OP_S);
    return { on: t >= it.at, scale: t >= it.at ? springPop(u, EQUATION.POP_MP) : 0, glyphs: glyphs.map(() => (t >= it.at ? 1 : 0)) };
  }
  const u = eq01((t - it.at) / EQUATION.WRITE_S);
  return { on: t >= it.at, scale: 1, glyphs: glyphs.map((_, j) => (t >= it.at ? figureGlyph(u, j, glyphs.length) : 0)) };
};

/* the whole row's opacity: 1, then down over the window's last OUT_S */
export const equationOut = (sp, t) => eq01((+sp.at + (+sp.dur || 0) - t) / EQUATION.OUT_S);

/* THE STEP (round 3, the parent's frame read: the captions read larger than the numbers they name): a named row's
   numbers stand a clear step above their captions - the numbers' cap at STEP times the caption's cap, the two faces'
   caps MEASURED in the served player (TERM_CAP_K, LABEL_CAP_K) - so the numbers are never smaller than this */
export const EQUATION_TERM_MIN = EQUATION.STEP * EQUATION.LABEL_PX * EQUATION.LABEL_CAP_K / EQUATION.TERM_CAP_K;

/* THE LAYOUT, from the region, each item's advance at a type size of 1 (measured, or CHAR_W per character) and each
   item's caption width in px at LABEL_PX (0 = none). Each item stands centred in a SLOT as wide as it or its caption.
     no caption   one size for every item - the region's height times FS_K, shrunk so the row fits the width, never
                  under FLOOR_PX (a row the floor pushes past its region overflows it evenly; the author decides).
     captioned    the numbers as large as the region holds with their captions under them, never under
                  EQUATION_TERM_MIN (the step above the captions); a region too small for that gives up its DAYLIGHT
                  first - the gaps between items down to GAP_MIN, the caption's drop down to DROP_MIN - never the
                  numbers, and past that the row overflows evenly (`over`; the compiler WARNs with the numbers, s106).
                  The row and its caption line are centred together in the region. */
export const equationLayout = (b, adv, lab) => {
  const n = adv.length, L = adv.map((_, i) => Math.max(0, +((lab || [])[i]) || 0)), named = L.some((v) => v > 0);
  const nGap = Math.max(0, n - 1), slotsAt = (fs) => adv.map((a, i) => Math.max(a * fs, L[i]));
  const width = (fs, gap) => slotsAt(fs).reduce((s, w) => s + w, 0) + gap * fs * nGap;
  const place = (fs, gap, W) => {
    let x = b.x + (b.w - W) / 2;
    const xs = [], cxs = [], slots = slotsAt(fs);
    slots.forEach((w, i) => { cxs.push(x + w / 2); xs.push(x + (w - adv[i] * fs) / 2); x += w + gap * fs; });
    return { xs, cxs, slots };
  };
  if (!named) {   /* no captions: the row's width is linear in its size - solved exactly */
    const fsH = b.h * EQUATION.FS_K, span = adv.reduce((s, a) => s + a, 0) + EQUATION.GAP_K * nGap;
    const fs = Math.max(EQUATION.FLOOR_PX, Math.min(fsH, span > 0 ? b.w / span : fsH)), W = width(fs, EQUATION.GAP_K);
    return Object.assign(place(fs, EQUATION.GAP_K, W), { fs, ws: adv.map((a) => a * fs), y: b.y + b.h / 2 + fs * EQUATION.BASE_DY,
                         w: W, h: null, gap: EQUATION.GAP_K, drop: null, over: W > b.w + 1e-6, labelY: null });
  }
  const LP = EQUATION.LABEL_PX, UPDN = FIGURE.FIGURE_UP + FIGURE.FIGURE_DOWN;
  const block = (fs, drop) => UPDN * fs + (drop + EQUATION.LABEL_DESC) * LP;
  let fit = Math.max(0, (b.h - (EQUATION.LABEL_DROP + EQUATION.LABEL_DESC) * LP) / UPDN);
  if (width(fit, EQUATION.GAP_K) > b.w) {   /* a caption's slot does not shrink with the type: bisect the largest size that fits */
    let lo = 0, hi = fit;
    for (let k = 0; k < 48; k++) { const mid = (lo + hi) / 2; if (width(mid, EQUATION.GAP_K) > b.w) hi = mid; else lo = mid; }
    fit = lo;
  }
  const fs = Math.max(EQUATION_TERM_MIN, fit);
  let gap = EQUATION.GAP_K, drop = EQUATION.LABEL_DROP;
  if (width(fs, gap) > b.w && nGap > 0) gap = Math.max(EQUATION.GAP_MIN, (b.w - width(fs, 0)) / (fs * nGap));
  if (block(fs, drop) > b.h) drop = Math.max(EQUATION.DROP_MIN, (b.h - UPDN * fs) / LP - EQUATION.LABEL_DESC);
  const W = width(fs, gap), H = block(fs, drop), y = b.y + (b.h - H) / 2 + FIGURE.FIGURE_UP * fs;
  return Object.assign(place(fs, gap, W), { fs, ws: adv.map((a) => a * fs), y, w: W, h: H, gap, drop,
                       over: W > b.w + 1e-6 || H > b.h + 1e-6, labelY: y + fs * FIGURE.FIGURE_DOWN + LP * drop });
};

/* an item's advance at type size 1: measured off its glyphs when they are on the page, arithmetic when nothing can measure */
export const equationAdvance = (node, text, fs) => {
  const n = node && node.getComputedTextLength ? node.getComputedTextLength() : 0;
  return n > 0 ? n / fs : Array.from(String(text || "")).length * EQUATION.CHAR_W;
};

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player): the declaration, the clock, the
   layer and the shared helpers by name. Every item is written every frame at its slot (the glyphs that are not yet
   written at opacity 0), so its advance is measured before the row is laid out and the layout never depends on t. */
export function paintEquation(ctx) {
  const { sp, t, svg, el, resolveTarget, idle, hash, seed, si } = ctx;
  const b = resolveTarget(sp.target);
  if (!b || !(b.w > 0) || !(b.h > 0)) return;   /* the targeting law: no resolved region, nothing painted */
  const fade = equationOut(sp, t);
  if (fade <= 0) return;
  const items = equationItems(sp);
  const fs0 = Math.max(EQUATION.FLOOR_PX, b.h * EQUATION.FS_K);
  const kind = sp.idle === "none" ? "none" : (sp.idle || "breath");
  const ix = kind === "none" || !idle ? { scale: 1, dx: 0, dy: 0 } : idle(kind, t, hash ? hash(seed | 0, (si | 0) * 17, 993) : 0);
  const cx = b.x + b.w / 2, cy = b.y + b.h / 2;
  const g = el("g", "eqrow", svg, { opacity: fade.toFixed(3), transform: "translate(" + (cx + ix.dx).toFixed(2) + " " + (cy + ix.dy).toFixed(2)
                                    + ") scale(" + (+ix.scale || 1).toFixed(4) + ") translate(" + (-cx).toFixed(2) + " " + (-cy).toFixed(2) + ")" });
  const nodes = items.map((it) => {
    const pose = equationItemAt(it, t), mark = it.role === "op" || it.role === "eq";
    const tx = el("text", "", g, { "data-role": it.role, "font-size": fs0.toFixed(2), "font-family": mark ? EQUATION.OP_FACE : EQUATION.FACE,
                                   "font-weight": EQUATION.WEIGHT, fill: it.neg ? EQUATION.NEG : EQUATION.CHALK,
                                   "paint-order": "stroke", stroke: EQUATION.HALO, "stroke-width": EQUATION.HALO_PX,
                                   "stroke-linejoin": "round" });
    Array.from(it.text).forEach((ch, j) => { el("tspan", "", tx, { opacity: pose.glyphs[j].toFixed(3) }).textContent = ch; });
    return { it, pose, tx };
  });
  /* the captions (review F7): written with their item - its write's own progress - measured before the row is laid out */
  const labels = nodes.map(({ it }) => {
    if (!it.label) return null;
    const on = t >= it.at ? eq01((t - it.at) / EQUATION.WRITE_S) : 0;
    const lt = el("text", "", g, { "data-role": "label", "font-size": EQUATION.LABEL_PX.toFixed(2), "font-family": EQUATION.LABEL_FACE,
                                   "font-weight": EQUATION.LABEL_WEIGHT, fill: EQUATION.LABEL_INK, "text-anchor": "middle",
                                   "paint-order": "stroke", stroke: EQUATION.HALO, "stroke-width": EQUATION.HALO_PX * 0.75,
                                   "stroke-linejoin": "round", opacity: on.toFixed(3) });
    lt.textContent = it.label;
    const n = lt.getComputedTextLength ? lt.getComputedTextLength() : 0;
    return { lt, w: n > 0 ? n : Array.from(it.label).length * EQUATION.LABEL_CHAR_W * EQUATION.LABEL_PX };
  });
  const lay = equationLayout(b, nodes.map((n) => equationAdvance(n.tx, n.it.text, fs0)), labels.map((l) => (l ? l.w : 0)));
  labels.forEach((l, i) => { if (l) { l.lt.setAttribute("x", lay.cxs[i].toFixed(1)); l.lt.setAttribute("y", lay.labelY.toFixed(1)); } });
  nodes.forEach(({ it, pose, tx }, i) => {
    tx.setAttribute("font-size", lay.fs.toFixed(2));
    tx.setAttribute("x", lay.xs[i].toFixed(1));
    tx.setAttribute("y", lay.y.toFixed(1));
    if (it.role === "op" || it.role === "eq") {   /* the spring about the mark's own middle, never about the row's */
      const mx = lay.xs[i] + lay.ws[i] / 2, my = lay.y - lay.fs * FIGURE.FIGURE_UP / 2;
      tx.setAttribute("transform", "translate(" + mx.toFixed(1) + " " + my.toFixed(1) + ") scale(" + pose.scale.toFixed(4)
                                   + ") translate(" + (-mx).toFixed(1) + " " + (-my).toFixed(1) + ")");
    }
  });
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can import this
   file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.equation = paintEquation;
