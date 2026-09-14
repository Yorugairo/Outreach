/* SPACE: page */
/* species/compare.mjs - THE COMPARE (P57 T12; BACKLOG R26-70b; the grammar is P57 T11's sixth `chart_to` verb).
   SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN compare and
   KINETICS:END. It imports the ease law only, and its region sits with the kinetics laws rather than in the species
   block at the foot of the file - span.mjs's reason: a PAGE species' math is called by the page's PERFORM layer,
   which is written hundreds of lines above that block, and a const has to exist before the function that closes
   over it is built.

   WHEN: the sentence quotes the market's own figure and then says what it MEANS. E76 (the operator, 2026-09-13):
   *"never p/e multiples isn't the rule, the rule should be to explore various display mechanisms, and that
   comparators (like dollar per share or change per $) show immediate narrative value. In fact, showing the P/E and
   then morphing it to a more visual number would be a great repeatable mechanism"*. The page has already WRITTEN
   the quoted figure at its datum (a `figure` species - E50, and the compiler refuses a compare whose metric text no
   figure on the page carries); this verb turns that written number into the one the viewer feels.

   THE FORM BUILT HERE IS THE COUNTER (E60), NOT THE GLYPH MORPH - and why. Method A (kinetics/morph_a.mjs: ring-
   normalise, resample by arc length, rotational alignment, vertex lerp) morphs OUTLINES, and a figure on a ledger
   page is not an outline: paintFigure writes it as an SVG <text> with one <tspan> per character, laid out by the
   browser's own font engine. There are no glyph paths to resample, and the only way to get them is to vendor a
   font-to-path library and re-implement the page's type - which the slice refuses (a second type engine would
   drift from the one that draws every other word on the page). The doctrine already names the honest form for a
   number becoming another number: E60's counter, the breakthrough's pill counting to its exact string while the
   scale rewrites under it. So the number COUNTS, on min-jerk, and the words around it cross THROUGH ZERO at the
   swap - no character ever cuts.

   THE LAW, a pure function of t (u = (t - at) / dur, clamped):
     count   - the quoted numeral runs to the comparator's numeral on min-jerk over COUNT of the window. It counts
               between the two TEXTS' own numerals ("24.8x" -> "15 % dearer" counts 24.8 -> 15), never between the
               authored `value`s: those are the ARITHMETIC the compiler checks (E77 - `inputs` + `derive` + `source`,
               a comparator the row cannot reproduce is refused), and they may be in another scale entirely
               (0.1535 IS "15 % dearer"). Nothing reaches the screen that the row did not author.
     swap    - the metric's clothes (the text either side of its numeral, and its decimals) become the comparator's
               at SWAP, at the instant the affix glyphs are at zero opacity: the swap is invisible because there is
               nothing on screen to swap.
     label   - the comparator's `label` - what the number MEANS, the thing a multiple never says - is written
               BENEATH by the hand from LABEL_AT, glyph after glyph at the figure's own overlap.
     hold    - `hold: "metric"` (the default) stands the quoted figure beside the comparator at GHOST_A from the
               swap on, at GHOST_F of its size, so the two can be read against each other; `hold: "gone"` gives the
               comparator the stage alone.
   A SEEK IS THE PLAY: every cell's character and opacity is written from u each frame, so a cold seek into the
   middle of the morph paints exactly what playing into it paints. The cells, the ghost and the sub are created
   idempotently (the painter grows them and never rebuilds them), and a frame before `at` restores the figure's own
   text and leaves its glyphs' opacity to the figure's own hand - so the page before the word is the page.
   The dials below are ours to tune (42 s42.5), not findings. */
import { minJerk } from "../kinetics/ease.mjs";

export const COMPARE = Object.freeze({
  COUNT: 0.72,      /* the share of the window the numeral counts over, on min-jerk: it lands before the window does, so the comparator is STILL while its label is read */
  SWAP: 0.5,        /* where the metric's words become the comparator's - the affix crosses through zero exactly here, so no character is ever cut */
  CROSS: 0.2,       /* ... and the share of the window the crossing itself takes, centred on the swap: the words stand while the number counts and dissolve only where they change, so the page never looks like it is fading out */
  LABEL_AT: 0.55,   /* when the comparator's label starts being written beneath (just after the swap: the number is already the new one when it is named) */
  GHOST_A: 0.62,    /* the held metric's opacity beside the comparator (hold: "metric") - present, and plainly the quieter of the two */
  GHOST_F: 0.74,    /* ... and its size, as a share of the figure's own: the quoted figure is where the number started, not what the sentence is about now */
  GAP: 14,          /* the room between the comparator and the held metric, in the chart's viewBox units (the figure's own 14 px offset from its datum) */
  SUB_DY: 1.3,      /* the label's baseline beneath the figure, in sub sizes - paintFigure's own step for a figure's sub */
  WIDTH_EM: 0.56,   /* a glyph's width as a share of its size, for a caller with no text metrics (node, a probe): the browser's own getComputedTextLength is used wherever there is one */
  PAD: 4,           /* spare glyph cells beyond what either end needs - a count between them is never wider than this allows, and the painter still grows on demand */
  OVERLAP: 1.6,     /* the hand's glyph overlap, the figure's and the span's own: a run that stops exactly at n leaves its last letters half-inked */
});

const cmp01 = (v) => Math.min(1, Math.max(0, v));

/* THE TEXT, split at its FIRST numeral: what is written before it, the numeral as quoted, what is written after,
   how many decimals it carries and whether it is grouped by thousands. A partition - pre + num + post is the
   string it came from, exactly - so the two ends of the morph are the authored strings and nothing else. */
export const compareSplit = (text) => {
  const s = text == null ? "" : String(text);
  const m = /-?\d[\d,]*(?:\.\d+)?/.exec(s);
  if (!m) return { pre: s, num: "", post: "", dec: 0, group: false, value: NaN };
  const num = m[0], dot = num.indexOf(".");
  return { pre: s.slice(0, m.index), num, post: s.slice(m.index + num.length),
           dec: dot < 0 ? 0 : num.length - dot - 1, group: num.indexOf(",") >= 0,
           value: parseFloat(num.replace(/,/g, "")) };
};

/* a counted value in one end's own clothes: its decimals, its thousands grouping, and a sign only when the
   rounded number actually is one (a count that passes through -0.004 must not flash a minus) */
export const compareFmt = (v, dec, group) => {
  if (!Number.isFinite(v)) return "";
  const s = Math.abs(v).toFixed(Math.max(0, Math.min(6, dec | 0)));
  const cut = s.indexOf("."), whole = cut < 0 ? s : s.slice(0, cut), frac = cut < 0 ? "" : s.slice(cut);
  return (v < 0 && parseFloat(s) !== 0 ? "-" : "")
    + (group ? whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",") : whole) + frac;
};

/* THE FRAME at u: the whole state of the morph as numbers and one string, and the only place the law lives.
     text   what is written this frame (u <= 0 is the metric AS QUOTED, u >= 1 the comparator AS AUTHORED)
     value  the numeral this frame, min-jerk between the two quoted numerals - monotone in u, and null when
            either end quotes no number at all (then the whole string cross-fades and nothing counts)
     i0/i1  the numeral's span in `text`: those cells hold at full ink while the ones around them cross over
     affix  the opacity of every cell outside the numeral - 1 at both ends, 0 exactly at the swap, and the
            crossing itself only CROSS of the window wide, so the words stand while the number counts
     sub    how far the comparator's label has been written; ghost: the held metric's opacity */
export const compareFrame = (sp, u) => {
  const S = sp || {}, M = compareSplit((S.metric || {}).text), C = compareSplit((S.comparator || {}).text);
  const uu = cmp01(u), counts = Number.isFinite(M.value) && Number.isFinite(C.value);
  const value = counts ? M.value + (C.value - M.value) * minJerk(cmp01(uu / COMPARE.COUNT)) : null;
  const end = uu <= 0 ? M : uu >= 1 ? C : null, dress = end || (uu < COMPARE.SWAP ? M : C);
  const num = end ? end.num : (counts ? compareFmt(value, dress.dec, dress.group || M.group) : dress.num);
  const affix = end ? 1 : (uu < COMPARE.SWAP ? 1 - minJerk(cmp01((uu - (COMPARE.SWAP - COMPARE.CROSS)) / COMPARE.CROSS))
                                             : minJerk(cmp01((uu - COMPARE.SWAP) / COMPARE.CROSS)));
  return { text: dress.pre + num + dress.post, value, i0: dress.pre.length, i1: dress.pre.length + num.length,
           affix, counts, u: uu,
           sub: cmp01((uu - COMPARE.LABEL_AT) / (1 - COMPARE.LABEL_AT)),
           ghost: cmp01((uu - COMPARE.SWAP) / (1 - COMPARE.SWAP)) * COMPARE.GHOST_A };
};

/* how many glyph cells the label needs for the whole morph: both authored strings, and the widest a counted
   number in either end's clothes can be (the integer part of the larger magnitude, the deeper decimals, a point,
   a sign and a comma group). The painter still grows on demand, so this is the room, never the limit. */
export const compareCapacity = (sp) => {
  const S = sp || {}, mt = (S.metric || {}).text == null ? "" : String((S.metric || {}).text);
  const ct = (S.comparator || {}).text == null ? "" : String((S.comparator || {}).text);
  const M = compareSplit(mt), C = compareSplit(ct);
  const big = Math.max(Math.abs(M.value) || 0, Math.abs(C.value) || 0);
  const digits = Number.isFinite(M.value) && Number.isFinite(C.value)
    ? String(Math.floor(big)).length + Math.max(M.dec, C.dec) + 3
    : Math.max(M.num.length, C.num.length);
  const around = Math.max(M.pre.length + M.post.length, C.pre.length + C.post.length);
  return Math.max(mt.length, ct.length, around + digits) + COMPARE.PAD;
};

/* one glyph of the label as the hand writes it - the figure's and the span's own share, with OVERLAP's slack so
   the last letter is fully in exactly when the write ends */
export const compareGlyph = (write, j, n) => {
  const per = 1 / (Math.max(1, n | 0) + COMPARE.OVERLAP - 1);
  return cmp01((write - j * per) / (per * COMPARE.OVERLAP));
};

/* the FIGURE this row morphs: the one the page wrote with the metric's own text (paintFigure's records carry
   `sp.text`). The compiler has already refused a row with no such figure - here, a page that lost it paints
   nothing rather than inventing a place to write. */
export const compareFigure = (figures, sp) => {
  const want = String((((sp || {}).metric) || {}).text == null ? "" : ((sp || {}).metric || {}).text).trim();
  if (!want) return null;
  return (figures || []).find((f) => f && f.sp && String(f.sp.text == null ? "" : f.sp.text).trim() === want) || null;
};

/* the written width of the label, for placing the held metric BESIDE it: the browser's own metrics where there
   are any, the estimate where there are none (node, a probe) - both pure functions of the string on screen */
export const compareWidth = (el, text, fs) =>
  (el && typeof el.getComputedTextLength === "function" ? el.getComputedTextLength() : 0)
  || String(text == null ? "" : text).length * fs * COMPARE.WIDTH_EM;

/* THE INK on one element: the attribute AND the inline style. The page's own class CSS carries an opacity for the
   sub's class (`.lp-chart .bksub { opacity: .85 }`) and a class rule outranks a presentation ATTRIBUTE - the lesson
   the bracket's inline `fill` was already written for (scene-evidence-engine.mjs: "the chart's class CSS outranks a
   fill attribute"). The attribute is written too, so a caller with no CSSOM - node, a probe - still reads the law
   off the element. Measured 2026-09-14: the held metric came back at .85 on every frame of the first render. */
export const compareInk = (el, v) => {
  if (!el) return;
  const a = Math.min(1, Math.max(0, +v || 0)).toFixed(3);
  el.setAttribute("opacity", a);
  if (el.style) el.style.opacity = a;
};

/* the figure's OWN colour, read off the inline style paintFigure wrote it with (`font-size:NNpx;fill:COL`), so the
   held metric and the comparator's label are the same ink as the number they belong to - never a colour of ours */
export const compareFill = (fg) => {
  const m = /fill:\s*([^;]+)/.exec(String((fg && fg.label && fg.label.getAttribute && fg.label.getAttribute("style")) || ""));
  return m ? m[1].trim() : "var(--lp-chalk)";
};

/* THE MORPH'S OWN ELEMENTS, built once and grown, never rebuilt: the extra glyph cells the count needs beyond the
   figure's own, the held metric beside it, and the comparator's label beneath. Idempotent on purpose - a cold seek
   builds exactly what a play built, and a page whose figure was re-drawn gets them back on the next frame. */
export const compareEnsure = (fg, sp, ctx, want) => {
  const el = (ctx || {}).el;
  let P = fg.__compare;
  if (!P) {
    const fs = +fg.fs || 28, fss = +fg.fss || fs * 0.6, anchor = fg.fits === false ? "end" : "start";
    const col = compareFill(fg);
    const ghost = el ? el("text", "bksub", fg.g, { x: 0, y: 0, "text-anchor": anchor, opacity: 0,
      style: "font-size:" + (fs * COMPARE.GHOST_F).toFixed(1) + "px;fill:" + col + ";opacity:0" }) : null;
    if (ghost) ghost.textContent = String(((sp.metric || {}).text) == null ? "" : (sp.metric || {}).text);
    const sub = el ? el("text", "bksub", fg.g, { x: 0, y: 0, "text-anchor": anchor,
      style: "font-size:" + fss.toFixed(1) + "px;fill:" + col + ";opacity:1" }) : null;
    const lab = String(((sp.comparator || {}).label) == null ? "" : (sp.comparator || {}).label);
    const sg = sub && el ? [...lab].map((ch) => { const ts = el("tspan", "", sub, { opacity: 0 });
      ts.textContent = ch === " " ? " " : ch; return ts; }) : [];
    P = fg.__compare = { cells: (fg.lg || []).slice(), ghost, sub, sg, fs, fss, anchor };
  }
  while (el && fg.label && P.cells.length < (want | 0)) {
    const ts = el("tspan", "", fg.label, { opacity: 0 }); ts.textContent = ""; P.cells.push(ts);
  }
  return P;
};

/* THE PAINTER (the module rule's page half). Every number of it is the law above; this is the DOM. `sd` is what
   the engine's chart_to dispatch hands it - the row `sp` and the page's built figures - `st` the page state, and
   `ctx` the PAGE species context every page painter reaches the engine through (`el` is lpEl), so `node --test`
   can call this with recorders and no DOM. */
export const paintCompare = (sd, t, st, ctx) => {
  const sp = (sd || {}).sp || {}, fg = compareFigure((sd || {}).figures, sp);
  if (!fg || !fg.label) return;
  const at = +sp.at || 0, u = cmp01((t - at) / Math.max(0.001, +sp.dur || 1)), F = compareFrame(sp, u);
  const P = compareEnsure(fg, sp, ctx, Math.max(compareCapacity(sp), F.text.length));
  const chars = [...F.text], before = t < at;
  P.cells.forEach((ts, j) => {
    const ch = j < chars.length ? chars[j] : "";
    ts.textContent = ch === " " ? " " : ch;
    if (before) { if (j >= (fg.lg || []).length) ts.setAttribute("opacity", 0); return; }   /* before the word the figure's own hand owns its glyphs; the cells this module added are not its business */
    ts.setAttribute("opacity", (j >= chars.length ? 0 : (j >= F.i0 && j < F.i1 ? 1 : F.affix)).toFixed(3));
  });
  const fits = fg.fits !== false, x = +fg.x || 0, y = +fg.y || 0;
  if (P.ghost) {
    const w = compareWidth(fg.label, F.text, P.fs), gx = x + (fits ? 1 : -1) * (w + COMPARE.GAP);
    P.ghost.setAttribute("x", gx.toFixed(1)); P.ghost.setAttribute("y", y.toFixed(1));
    P.ghost.setAttribute("text-anchor", fits ? "start" : "end");
    compareInk(P.ghost, before || sp.hold === "gone" ? 0 : F.ghost);
  }
  if (P.sub) {
    const step = P.fss * COMPARE.SUB_DY;
    P.sub.setAttribute("x", x.toFixed(1)); P.sub.setAttribute("y", (y + step * (fg.sub ? 2 : 1)).toFixed(1));
    P.sub.setAttribute("text-anchor", fits ? "start" : "end");
    compareInk(P.sub, 1);   /* the class's own .85 would dim the label the hand is writing; its glyphs carry the write */
    P.sg.forEach((ts, j) => ts.setAttribute("opacity", (before ? 0 : compareGlyph(F.sub, j, P.sg.length)).toFixed(3)));
  }
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment, so
   inlining keeps it and node - where no registry exists - still imports the file for the math. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.compare = paintCompare;
