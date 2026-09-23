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

   THE FOUR FORMS. T12 shipped a counter and called the glyph-outline morph impossible - a figure is an SVG <text>
   with one <tspan> per character, morph_a morphs OUTLINES, and a font-to-path library would stand a second type
   engine beside the browser's. The operator corrected that twice. First (2026-09-14, E76 s4): *"I don't understand
   why we can't do the full morph - just collapse or melt then re-draw."* Then, on reading T12b (E76 s5): *"the
   entire point of having our math and engine is that even for complex/difficult things we should be able to create
   solutions. it's just math"*, and, on what the melt should do: *"melt it into a ball, then we either throw it off
   the page, splatter it back on to the canvas and build the chart/graph from that, or morph it from the ball into
   the chart."* Both corrections stand in the four forms below, and the outlines are neither fetched nor vendored:
   they are MEASURED off the ink the page already draws (kinetics/contour.mjs - draw the string on an offscreen
   canvas at the figure's own face, threshold the alpha, walk the 0.5 level with marching squares).
     melt      THE DEFAULT (P57 T12c). The figure's own outlines SAG on melt.mjs's law - the box's top sinking, its
               foot hanging in seeded drips - and then BALL UP into one dense disc that holds the ink's own area.
               What becomes of the ball is the row's `then`:
                 morph   THE DEFAULT ENDING: the ball's ONE ring is carried by morph_a into the comparator's glyph
                         rings (the pairing rule below: one ring into N, every surplus born from the ball's centre),
                         and the figure's own <text> is the thing on screen again at u = 1 exactly.
                 splash  the ball bursts onto the page (melt.mjs's own splatter, seeded rays and landing drops) and
                         the hand writes the comparator through the drying ink.
                 throw   the ball sits in its own weight and is thrown off the page (melt.mjs's flight), and the
                         hand writes the comparator once it has gone.
     streak    P57 T12b's form, kept whole and byte-identical on its golden: the glyphs melt as ink where they stand,
               each one a drip opening in the hand's reading order, running down on melt.mjs's own run under its
               words' STREAK filter, and gone by the end of the take-away; then the hand re-writes the comparator.
     collapse  The hand TAKES THE INK BACK: species/figure.mjs's own write, run backwards, the LAST glyph first - the
               undraw law (the line unwinds) on a number.
     count     E60's counter, the form T12 shipped: the numeral runs to the comparator's on min-jerk and the words
               cross THROUGH ZERO at the swap, so no character ever cuts. Kept whole as the `form: "count"` setting -
               a number becoming another number by counting is still the honest form where the two are the same KIND
               of number - and byte-identical on its golden.
   `form` and `then` are refused by name, here and in the compiler (build_scene_timeline_f.py's
   _validate_metric_comparator), so a typo in a shot table is a refusal and never a silent default.

   THE MORPH'S LAW (`streak` and `collapse`), a pure function of t (u = (t - at) / dur, clamped):
     take-away  over TAKE_SHARE of the window the quoted figure LEAVES - `streak` on melt.mjs's own stepped clock
                (MELT.HOLD on 2s: stop-action ink), `collapse` on the hand's own smooth clock. The last drop falls
                exactly at TAKE_SHARE, which is where the write begins: the take-away ends before the hand starts.
     re-draw    over the rest the comparator is written at the SAME DATUM by figure.mjs's hand - its `text` over
                FIGURE.WRITE of the re-draw, its `label` beneath as the SUB over the rest - figureGlyph and the
                figure's own WRITE/SUB split, not a clock of ours (the label's own glyphs ride T12's compareGlyph,
                which lands the last letter exactly as the window ends: see compareMorphFrame's `sub`).
     hold       `hold: "metric"` ghosts the quoted figure small beside the comparator once the write has LANDED
                (T12's ghost, GHOST_A / GHOST_F); `hold: "gone"` gives the comparator the stage.

   THE COUNT FORM'S LAW, a pure function of t, unchanged from T12:
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
import { stepped } from "../kinetics/stopaction.mjs";
import { polyArea, centroid } from "../kinetics/arap.mjs";
import { MORPH_A, morphAPrepare, morphAAt, morphAPath } from "../kinetics/morph_a.mjs";
import { contourBitmap, contourShape } from "../kinetics/contour.mjs";
import { FIGURE, figureGlyph } from "./figure.mjs";
import { MELT, meltRun, meltTextAlpha, meltTextStreak, meltTextFilterMarkup, meltPhase, meltRelease, meltDrips, meltDepth, meltTop, meltSettle, meltThrowAt, ballCircle, ballFlat, splashDrops, splashSats, meltSplatPath } from "./melt.mjs";   /* ONE LINE on purpose: sync_kinetics' inliner drops a line that BEGINS with `import`, so a wrapped import statement would leave its continuation in the engine */

export const COMPARE = Object.freeze({
  TAKE_SHARE: 0.55, /* `melt` / `collapse`: the share of the window the TAKE-AWAY owns - the melt's sag, the collapse's unwind. The hand's re-draw owns the rest, and the two never overlap: the last drop falls as the first glyph of the comparator arrives */
  MELT_BOX: 3.2,    /* ... and the ROOM that melt's run is measured on, in the figure's own glyph-box heights: MELT.RUN is a share of a PAGE's ink box (hundreds of px), and a figure's box is one line tall, so a run measured on it alone would be a sag of a few px. The ink falls into the room under the number - where the label is about to be written */
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
  /* P57 T12c - THE RASTER (E76 s5, "it's just math"): how the engine gets a glyph's outline without a font file */
  RASTER_S: 4,      /* the working scale: the string is drawn at this many device pixels to the page pixel, so the contour's staircase is a quarter of a page pixel before it is simplified at all (1 read as a jagged number at the stage's size; 8 quadruples the raster for a contour no eye can tell from this one) */
  RASTER_A: 0.5,    /* ... and the alpha the raster is ink AT or above: the half-covered pixel is the glyph's own edge, which is where the browser itself puts it */
  RASTER_PAD: 4,    /* the clear border round the drawn string, in device px: ink that touches the bitmap's edge would close its ring on that edge */
  SIMPLIFY: 1.2,    /* the Douglas-Peucker tolerance, in the RASTER's own px (0.3 of a page px at RASTER_S 4): the staircase comes off and the glyph's corners stay, and morph_a gets a ring it can resample */
  DEGEN_R: 0.6,     /* a degenerate ring's radius in page px - a shape that is BORN or DIES is a circle of nothing at a point, never a vertex count of nothing (a ring of no length cannot be resampled by arc length) */
  BALL_SWELL: 1.0,  /* the ball's radius as a share of the disc that holds the ink's OWN area: 1 conserves the ink exactly (see compareBallR - MELT.BALL_R is a share of a PAGE's height and would ball a number up into a speck) */
  BALL_MIN: 0.34,   /* ... and its floor, in figure sizes: a ball smaller than a third of the number it came from reads as the number blinking out, not as ink gathering */
  SAG_GAIN: 3.2,    /* the sag's own gain, and MELT_BOX's twin for exactly MELT_BOX's reason: melt.mjs's SAG and TOP_SAG are shares of the melting box's HEIGHT, which on a page is hundreds of px and on a one-line figure is forty - at gain 1 the drips are two pixels and the number just stands there. The ink falls into the room under it, where the label is about to be written */
  SEED: 7,          /* the salt on the figure's own seeded hash: a page species is handed no scene hash, so the drips and the droplets are seeded by the figure's datum (see compareRnd) */
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

/* ---- THE MORPH (the operator's first correction, P57 T12b): the take-away, then the hand ------------------------- */
/* THE MORPH'S FRAME at u, for `streak` and `collapse` - the whole state as two clocks and one string:
     take   the take-away's own progress, 1 exactly at TAKE_SHARE (`streak` reads it off melt's STEPPED clock, so the
            ink leaves in stop-action poses on 2s, the clock its own drops and its ball already run on)
     write  the hand's progress over the rest of the window, 0 until the take-away has ended
     text   the metric AS QUOTED until the write begins, the comparator AS AUTHORED from there (u <= 0 is the metric,
            u >= 1 the comparator - the ends are the authored strings, as they are for the counter)
     sub    how far the comparator's LABEL has been written beneath: the re-draw splits into the number and its label
            on figure.mjs's own share (FIGURE.WRITE), and the label is then written on T12's own hand (compareGlyph),
            which lands its last letter exactly as the window ends - figureSubGlyph's OVERLAP slack overruns the
            figure's window and leaves its last glyph at 0.625, which on a label beside a 0.62 ghost is not a label
     ghost  the held metric's opacity: it arrives only once the hand has LANDED the comparator's own text (FIGURE.WRITE
            of the re-draw), so the two numbers are never both half-written */
export const compareMorphFrame = (sp, u, form) => {
  const S = sp || {}, uu = cmp01(u), dur = Math.max(0.001, +S.dur || 1);
  const uq = form === "collapse" ? uu : cmp01(stepped(Math.max(0, uu * dur), MELT.HOLD, MELT.FPS) / dur);
  const take = cmp01(uq / COMPARE.TAKE_SHARE);
  const write = cmp01((uu - COMPARE.TAKE_SHARE) / (1 - COMPARE.TAKE_SHARE));
  const metric = String((S.metric || {}).text == null ? "" : (S.metric || {}).text);
  const comparator = String((S.comparator || {}).text == null ? "" : (S.comparator || {}).text);
  const sub = cmp01((write - FIGURE.WRITE) / (1 - FIGURE.WRITE));
  return { form, metric, comparator, take, write, sub, u: uu, text: write > 0 ? comparator : metric,
           ghost: sub * COMPARE.GHOST_A };
};

/* the glyph's own delay: the drips open in the hand's READING ORDER over MELT.DRIP_DELAY - melt's own dial ("the last
   drop starts this far into the melt phase"), with melt's seeded order replaced by the one the hand wrote them in
   (a page species is handed no seeded hash, and a number that melted out of order would read as a glitch) */
const cmpDrip = (take, j, n) => {
  const d = MELT.DRIP_DELAY * ((j | 0) / Math.max(1, (n | 0) - 1));
  return cmp01((cmp01(take) - d) / Math.max(1e-6, 1 - d));
};
/* ONE GLYPH OF THE TAKE-AWAY. streak: melt.mjs's own words-alpha on that glyph's drip. collapse: figure.mjs's own write
   run BACKWARDS, the last glyph first - the hand takes the ink back the way it laid it down. */
export const compareTakeGlyph = (form, take, j, n) => {
  const m = Math.max(1, n | 0);
  if (form === "collapse") return 1 - figureGlyph(cmp01(take), m - 1 - (j | 0), m);
  return meltTextAlpha(cmpDrip(take, j, m));
};
/* ... and how far that glyph has RUN, in the chart's own viewBox units: melt.mjs's run on the room under the number */
export const compareTakeFall = (form, take, j, n, h) =>
  form === "streak" ? meltRun("melt", cmpDrip(take, j, Math.max(1, n | 0)), { h: h }) : 0;
/* the room the ink falls into, off the figure's OWN box law (species/figure.mjs) and the dial above */
export const compareMeltBox = (fs) => (FIGURE.FIGURE_UP + FIGURE.FIGURE_DOWN) * (+fs || 0) * COMPARE.MELT_BOX;

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
/* the figure's text-anchor as the page wrote it: `middle` where the builder CENTRED it (P69 T6 / R26-190: a figure on
   a bars page stands over its bar's top), else the side the room test chose - `end` where there was no room to the
   right. A figure record that names no anchor is read exactly as before, so every line page is unchanged. */
export const compareAnchor = (fg) => (fg && fg.anchor === "middle") ? "middle" : (fg && fg.fits === false ? "end" : "start");

export const compareEnsure = (fg, sp, ctx, want) => {
  const el = (ctx || {}).el;
  let P = fg.__compare;
  if (!P) {
    const fs = +fg.fs || 28, fss = +fg.fss || fs * 0.6, anchor = compareAnchor(fg);
    const col = compareFill(fg);
    const ghost = el ? el("text", "bksub", fg.g, { x: 0, y: 0, "text-anchor": anchor === "middle" ? "start" : anchor, opacity: 0,
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

/* THE STREAK'S FILTER, mounted ONCE beside the figure: melt.mjs's own words filter (meltTextFilterMarkup), under an id
   built from the figure's own datum - the page writes one figure per metric text, and the compiler refuses a compare
   whose metric no figure on the page carries, so two melts on one page can never collide. A caller with no DOM parser
   (node, a probe) gets the bundle with no primitives and paints the law without the pixels. */
export const compareMeltEnsure = (fg, P, ctx) => {
  if (P.melt) return P.melt;
  const el = (ctx || {}).el, id = "cmpmelt" + (fg.si | 0) + "-" + (fg.idx | 0);
  const host = el ? el("defs", "", fg.g, {}) : null;
  let tblur = null, toff = null;
  if (host && typeof host.querySelector === "function") {
    host.innerHTML = meltTextFilterMarkup(id);
    tblur = host.querySelector("feGaussianBlur"); toff = host.querySelector("feOffset");
  }
  P.melt = { id, host, tblur, toff };
  return P.melt;
};

/* WHAT STANDS BESIDE AND BENEATH the morphing number, for every form: the held metric on the figure's own baseline
   (the side the figure itself took), and the comparator's label written beneath it glyph by glyph. `subInk` is the
   form's own hand - the counter's own write for `count`, the figure's SUB write for the two morph forms. A figure
   CENTRED on its datum (P69 T6: a bar's top) holds the metric to its right and centres the label under it. */
const compareBeside = (fg, P, sp, text, before, ghost, subInk) => {
  const fits = fg.fits !== false, mid = compareAnchor(fg) === "middle", x = +fg.x || 0, y = +fg.y || 0;
  if (P.ghost) {
    const w = compareWidth(fg.label, text, P.fs), gx = x + (fits ? 1 : -1) * ((mid ? w / 2 : w) + COMPARE.GAP);
    P.ghost.setAttribute("x", gx.toFixed(1)); P.ghost.setAttribute("y", y.toFixed(1));
    P.ghost.setAttribute("text-anchor", fits ? "start" : "end");
    compareInk(P.ghost, before || sp.hold === "gone" ? 0 : ghost);
  }
  if (P.sub) {
    const step = P.fss * COMPARE.SUB_DY;
    P.sub.setAttribute("x", x.toFixed(1)); P.sub.setAttribute("y", (y + step * (fg.sub ? 2 : 1)).toFixed(1));
    P.sub.setAttribute("text-anchor", mid ? "middle" : fits ? "start" : "end");
    compareInk(P.sub, 1);   /* the class's own .85 would dim the label the hand is writing; its glyphs carry the write */
    P.sg.forEach((ts, j) => ts.setAttribute("opacity", (before ? 0 : subInk(j, P.sg.length)).toFixed(3)));
  }
};

/* THE COUNT FORM'S PAINT (T12, unchanged to the digit - its golden is byte-identical): every cell's character and
   opacity from the frame, the numeral at full ink while the words around it cross through zero. */
const paintCompareCount = (fg, sp, u, before, ctx) => {
  const F = compareFrame(sp, u);
  const P = compareEnsure(fg, sp, ctx, Math.max(compareCapacity(sp), F.text.length));
  const chars = [...F.text];
  P.cells.forEach((ts, j) => {
    const ch = j < chars.length ? chars[j] : "";
    ts.textContent = ch === " " ? " " : ch;
    if (before) { if (j >= (fg.lg || []).length) ts.setAttribute("opacity", 0); return; }   /* before the word the figure's own hand owns its glyphs; the cells this module added are not its business */
    ts.setAttribute("opacity", (j >= chars.length ? 0 : (j >= F.i0 && j < F.i1 ? 1 : F.affix)).toFixed(3));
  });
  compareBeside(fg, P, sp, F.text, before, F.ghost, (j, n) => compareGlyph(F.sub, j, n));
};

/* THE MORPH'S PAINT (`streak`, `collapse`): the metric's cells are TAKEN AWAY - each glyph on its own drip, running down
   by melt's own run (a <tspan>'s `dy` is CUMULATIVE, so each cell carries the DELTA and the row reads as absolute
   offsets) under melt's streak filter - and then the SAME cells are written back as the comparator by the figure's own
   hand. Every attribute is written from u on every frame, including the frames before the word, so a cold seek into
   the middle of the melt paints exactly what playing into it paints and a seek back is the page as it stood. */
const paintCompareMorph = (fg, sp, u, before, ctx, form) => {
  const F = compareMorphFrame(sp, u, form);
  const P = compareEnsure(fg, sp, ctx, Math.max(compareCapacity(sp), F.text.length));
  const M = form === "streak" ? compareMeltEnsure(fg, P, ctx) : null;
  const chars = [...F.text], n = chars.length, h = compareMeltBox(P.fs), taking = !before && F.write <= 0;
  let off = 0;
  P.cells.forEach((ts, j) => {
    const ch = j < n ? chars[j] : "";
    ts.textContent = ch === " " ? " " : ch;
    const fall = taking && j < n ? compareTakeFall(form, F.take, j, n, h) : 0;
    ts.setAttribute("dy", (fall - off).toFixed(2));
    off = fall;
    if (before) { if (j >= (fg.lg || []).length) ts.setAttribute("opacity", 0); return; }
    const ink = j >= n ? 0 : (taking ? compareTakeGlyph(form, F.take, j, n) : figureGlyph(F.write, j, n));
    ts.setAttribute("opacity", ink.toFixed(3));
  });
  if (M) {
    const streak = meltTextStreak(taking ? meltRun("melt", F.take, { h: h }) : 0);
    if (M.tblur) M.tblur.setAttribute("stdDeviation", streak.blur);
    if (M.toff) M.toff.setAttribute("dy", streak.dy);
    const use = taking && F.take > 0 ? "url(#" + M.id + ")" : "none";
    fg.label.setAttribute("filter", use);
    if (fg.label.style) fg.label.style.filter = use === "none" ? "" : use;
  }
  compareBeside(fg, P, sp, F.text, before, F.ghost, (j, n2) => compareGlyph(F.sub, j, n2));
};

/* ---- P57 T12c: THE BALL (E76 s5, the operator's second correction) ------------------------------------------------ */
/* THE FORM, by name. `melt` is the default because that is the correction: the quoted figure melts into a BALL and the
   ending says what becomes of it. Anything else throws - the compiler refuses it first, and a painter that silently
   picked a form would be a claim nobody made. */
export const COMPARE_FORMS = Object.freeze(["melt", "streak", "collapse", "count"]);
export const COMPARE_THENS = Object.freeze(["morph", "splash", "throw"]);
export const compareForm = (sp) => {
  const f = ((sp || {}).form) == null ? COMPARE_FORMS[0] : String((sp || {}).form);
  if (COMPARE_FORMS.indexOf(f) < 0) {
    throw new Error("compare: form " + f + " is not one of " + COMPARE_FORMS.join(" | ")
      + " - melt (the default: the quoted figure sags and BALLS UP, then the ending says what becomes of the ball), "
      + "streak (P57 T12b's text melt: the glyphs drip under their own streak filter and the hand re-writes), collapse "
      + "(the hand takes the ink back first), count (E60's counter, T12's form)");
  }
  return f;
};
/* THE ENDING, by name, and only on the ball. `then` on a form that never makes a ball is a row about nothing - the
   compiler says so first, and the painter says so here rather than painting something nobody authored. */
export const compareThen = (sp) => {
  const S = sp || {}, t = S.then == null ? COMPARE_THENS[0] : String(S.then);
  if (COMPARE_THENS.indexOf(t) < 0) {
    throw new Error("compare: then " + t + " is not one of " + COMPARE_THENS.join(" | ")
      + " - morph (the default: the ball becomes the comparator's own glyphs), splash (it bursts onto the page and the "
      + "hand writes through the splatter), throw (it is thrown off the page and the hand writes after it)");
  }
  return t;
};

/* THE SEEDED HASH a figure's own melt runs on: the drips, the droplets and their rays. A page species is handed no
   scene hash, so it is seeded by the figure's OWN datum (its series and its index) - two figures on one page melt
   differently, and the same figure melts identically on every frame, every seek and every render. */
export const compareRnd = (fg) => {
  const seed = (Math.imul((fg && fg.si) | 0, 131) + Math.imul((fg && fg.idx) | 0, 17) + COMPARE.SEED) >>> 0;
  return (k) => {
    let h = (seed + Math.imul((k | 0) + 1, 2654435761)) >>> 0;
    h ^= h >>> 15; h = Math.imul(h, 2246822519) >>> 0;
    h ^= h >>> 13; h = Math.imul(h, 3266489917) >>> 0;
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
  };
};

/* ---- the raster: the page's own ink, measured ---------------------------------------------------------------- */
/* THE FACE the page is writing in, read off the element the page wrote - never a face of ours. A caller with no CSSOM
   (node, a probe) gets null and the morph paints no outlines at all; it never guesses a font. */
export const compareFace = (el, fs) => {
  const cs = (typeof getComputedStyle === "function" && el && el.nodeType) ? getComputedStyle(el) : null;
  if (!cs || !cs.fontFamily) return null;
  return { style: cs.fontStyle || "normal", weight: String(cs.fontWeight || "400"),
           family: cs.fontFamily, size: parseFloat(cs.fontSize) || +fs || 0 };
};
/* ... as one canvas font string, at a working scale: the raster is RASTER_S device pixels to the page pixel, so the
   contour's staircase is a quarter of a page pixel before it is simplified at all */
export const compareFontString = (face, scale = 1) =>
  face.style + " " + face.weight + " " + (face.size * scale).toFixed(2) + "px " + face.family;

const CMP_SHAPES = new Map();   /* (text, face, scale) -> the rings. Computed ONCE per state: a cold seek into the
   middle of a morph re-uses exactly the rings a play built, and the browser rasterises one string once per page. */

/* THE GLYPHS OF A STRING AS RINGS, in PAGE units relative to the text's pen origin (x = 0 is where the first glyph
   starts, y = 0 is the baseline). The whole of E76 s5 is these fourteen lines: draw the string on an offscreen
   canvas at the figure's own face, size and weight; threshold the alpha; walk the 0.5 level (kinetics/contour.mjs);
   simplify the staircase off; divide by the working scale. No font file is parsed.
     `rings` the outlines, each with its `hole` and its `parent`   `box`  their bounding box (the INK box the melt sags)
     `adv`   the string's advance, for an `end`-anchored figure    `area` the ink's own area, which sizes the ball */
export const compareShape = (text, face, o = {}) => {
  const doc = (o.document !== undefined) ? o.document : (typeof document !== "undefined" ? document : null);
  const str = String(text == null ? "" : text);
  if (!doc || typeof doc.createElement !== "function" || !face || !str) return null;
  const S = +o.scale || COMPARE.RASTER_S, font = compareFontString(face, S), key = str + "\x00" + font;
  if (CMP_SHAPES.has(key)) return CMP_SHAPES.get(key);
  const cv = doc.createElement("canvas"), c2 = cv.getContext && cv.getContext("2d");
  if (!c2) return null;
  c2.font = font;
  const m = c2.measureText(str), pad = COMPARE.RASTER_PAD;
  const left = Math.ceil(Math.abs(m.actualBoundingBoxLeft || 0)), right = Math.ceil(Math.abs(m.actualBoundingBoxRight || 0));
  const asc = Math.ceil(Math.abs(m.actualBoundingBoxAscent || 0)), desc = Math.ceil(Math.abs(m.actualBoundingBoxDescent || 0));
  if (!(right + left > 0) || !(asc + desc > 0)) return null;
  cv.width = left + right + 2 * pad; cv.height = asc + desc + 2 * pad;
  c2.font = font;   /* sizing the canvas resets its context: the face is set again, after the box is known */
  c2.textAlign = "left"; c2.textBaseline = "alphabetic"; c2.fillStyle = "#000";
  const ox = pad + left, oy = pad + asc;
  c2.fillText(str, ox, oy);
  const img = c2.getImageData(0, 0, cv.width, cv.height).data;
  const bmp = contourBitmap(img, cv.width, cv.height, COMPARE.RASTER_A);
  const rings = contourShape(bmp, { tol: COMPARE.SIMPLIFY, map: (p) => [(p[0] + 0.5 - ox) / S, (p[1] + 0.5 - oy) / S] });
  if (!rings.length) return null;
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity, area = 0;
  for (const r of rings) {
    area += (r.hole ? -1 : 1) * Math.abs(polyArea(r.pts));
    for (const p of r.pts) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]); }
  }
  const shape = { rings, adv: m.width / S, area: Math.abs(area), box: { x: x0, y: y0, w: x1 - x0, h: y1 - y0 } };
  /* the face loads over the network: a raster taken before it landed is the FALLBACK face's, and caching that would
     freeze the wrong glyphs into the whole morph. It is used for this frame and computed again on the next one. */
  if (!doc.fonts || typeof doc.fonts.check !== "function" || doc.fonts.check(font)) CMP_SHAPES.set(key, shape);
  return shape;
};

/* the rings at the figure's own datum: the pen is the figure's x (its advance back from it where the page had no room
   to the right and the text is anchored `end`, half of it where the figure is centred), and its y is the baseline the
   hand wrote on */
export const compareAtPen = (shape, fg) => {
  const a = compareAnchor(fg), x0 = +fg.x || 0;
  const px = a === "end" ? x0 - shape.adv : a === "middle" ? x0 - shape.adv / 2 : x0, py = +fg.y || 0;
  return { rings: shape.rings.map((r) => ({ hole: r.hole, parent: r.parent, pts: r.pts.map((p) => [px + p[0], py + p[1]]) })),
           box: { x: px + shape.box.x, y: py + shape.box.y, w: shape.box.w, h: shape.box.h }, area: shape.area, adv: shape.adv };
};

/* ---- the pairing rule ---------------------------------------------------------------------------------------- */
/* A GLYPH is an outer ring and the holes inside it. A hole's `parent` is the ring it sits in, which may itself be a
   hole (a counter island), so the walk up the parents ends at the ink the hole belongs to. */
export const compareGroups = (rings) => {
  const groups = [], of = new Array(rings.length).fill(-1);
  rings.forEach((r, i) => { if (!r.hole) { of[i] = groups.length; groups.push({ outer: r.pts, holes: [], c: centroid(r.pts) }); } });
  rings.forEach((r, i) => {
    if (!r.hole) return;
    let p = r.parent;
    while (p >= 0 && rings[p].hole) p = rings[p].parent;
    if (p >= 0 && of[p] >= 0) groups[of[p]].holes.push(r.pts);
  });
  for (const g of groups) g.holes.sort((a, b) => centroid(a)[0] - centroid(b)[0]);
  return groups.sort((a, b) => a.c[0] - b.c[0]);
};

/* a DEGENERATE ring - the morph's own law for a shape that appears or disappears: a circle of nothing at a point */
export const compareSeed = (c, r) => ballCircle(c, Math.max(1e-3, r), MELT.CIRCLE_N);

/* THE PAIRING RULE, stated once and used both ways round.
     1. Both sets are sorted by their glyphs' CENTROID X - reading order, which is the order the hand wrote them in.
     2. Outer rings pair with outer rings BY RANK: the i-th glyph of one becomes the i-th glyph of the other.
     3. A SURPLUS glyph on either side has no rank to pair with. It collapses into - or is born from - a degenerate
        ring at the centroid of its NEAREST paired neighbour's counterpart: the glyph beside it is where it goes.
     4. HOLES pair with holes, inside a paired glyph, by the same rank rule on the same sorted order; a surplus hole
        dies into (or is born from) a degenerate ring at its own glyph's counterpart centroid - a hole is a gap in
        ONE glyph and has nowhere else to go.
   `24.8x` -> `15 %` is the case the node test pins: five glyphs to three, so three pair by rank and the last two
   collapse into the third's destination. The SAME rule carries one ring into many - which is exactly what the ball
   becoming the comparator is: one glyph to N, every surplus born from the ball's own centre. */
export const comparePairGroups = (A, B, degenR) => {
  const As = (A || []).slice(), Bs = (B || []).slice(), n = Math.min(As.length, Bs.length), out = [];
  const near = (from, i, to) => {   /* the nearest PAIRED neighbour's counterpart, by centroid x */
    let best = 0, d = Infinity;
    for (let k = 0; k < n; k++) { const dd = Math.abs(from[i].c[0] - from[k].c[0]); if (dd < d) { d = dd; best = k; } }
    return to[best];
  };
  const holes = (a, b, cA, cB) => {
    const m = Math.min(a.length, b.length);
    for (let j = 0; j < m; j++) out.push({ src: a[j], dst: b[j], hole: true });
    for (let j = m; j < a.length; j++) out.push({ src: a[j], dst: compareSeed(cB, degenR), hole: true, dies: true });
    for (let j = m; j < b.length; j++) out.push({ src: compareSeed(cA, degenR), dst: b[j], hole: true, born: true });
  };
  for (let i = 0; i < n; i++) {
    out.push({ src: As[i].outer, dst: Bs[i].outer, hole: false });
    holes(As[i].holes, Bs[i].holes, As[i].c, Bs[i].c);
  }
  for (let i = n; i < As.length; i++) {
    const to = near(As, i, Bs);
    out.push({ src: As[i].outer, dst: compareSeed(to.c, degenR), hole: false, dies: true });
    holes(As[i].holes, [], As[i].c, to.c);
  }
  for (let i = n; i < Bs.length; i++) {
    const from = near(Bs, i, As);
    out.push({ src: compareSeed(from.c, degenR), dst: Bs[i].outer, hole: false, born: true });
    holes([], Bs[i].holes, from.c, Bs[i].c);
  }
  return out;
};

/* THE MORPH of a pair set, prepared once (Method A: ring-normalise, resample by arc length, rotational alignment) and
   read at m every frame. morph_a refuses only a pair it is told not to resample (rings of different vertex counts);
   every pair here is resampled to MORPH_A.N, which is what makes a five-ring set and a three-ring set commensurable. */
export const comparePrepare = (pairs) => pairs.map((p) => ({ hole: p.hole, prep: morphAPrepare(p.src, p.dst, { n: MORPH_A.N }) }));
/* ... and the path they paint: ONE `d` for the whole set, one subpath per pair, holes WOUND THE OTHER WAY. The fill
   is nonzero, so a hole subtracts from the glyph it sits in - which it can only do inside ONE fill, which is why this
   is one <path> and not one per pair - and two glyphs that land on the same disc (every ring at the ball) make one
   solid ball rather than cancelling each other out, which is what even-odd would have done. */
export const comparePath = (preps, m) => preps.map((p) => {
  const ring = morphAAt(p.prep, m).outline;
  return morphAPath(p.hole ? ring.slice().reverse() : ring);
}).join(" ");

/* ---- the sag and the ball -------------------------------------------------------------------------------------- */
/* THE SAG on an outline, melt.mjs's own law applied to the INK rather than to a mask over it: the box's top sinks
   (meltTop) and its foot hangs in seeded drips (meltDepth), and every point of the ink is carried between the two in
   the share of the box it stands at. A page melts its pixels through a mask; a figure has its outlines, so the same
   law moves the vertices themselves - the ink runs down and the drips are where it runs. */
export const compareSagAt = (pts, k, box, drips) => {
  const h = Math.max(1e-6, box.h), g = COMPARE.SAG_GAIN;
  return pts.map((p) => {
    const top = meltTop(p[0], k, box, drips), foot = box.y + box.h + meltDepth(p[0], k, box, drips);
    const to = top + (foot - top) * ((p[1] - box.y) / h);
    return [p[0], p[1] + (to - p[1]) * g];   /* the DISPLACEMENT is what the gain scales: at k = 0 melt's law moves nothing, and nothing times a gain is still nothing */
  });
};
/* THE BALL'S RADIUS, and the one number of this slice that is NOT melt's. MELT.BALL_R is a share of the melting
   box's HEIGHT, which on a page is hundreds of px and on a one-line figure is forty - it would ball a number up into
   a speck of three pixels. The figure's ball is the disc that holds THE INK'S OWN AREA (the rings' area, holes taken
   out), swelled by a dial, and never smaller than BALL_MIN of the figure's own size: the ink is conserved, which is
   what "melt it into a ball" says. COMPARE.MELT_BOX made the same correction for the streak's run. */
export const compareBallR = (area, fs) =>
  Math.max(COMPARE.BALL_MIN * (+fs || 0), COMPARE.BALL_SWELL * Math.sqrt(Math.max(0, area) / Math.PI));
/* the ball's CENTRE: the sagged ink's own area-weighted centroid - where the mass ended up, not where it started */
export const compareBallC = (groups) => {
  let wx = 0, wy = 0, w = 0;
  for (const g of groups) { const a = Math.abs(polyArea(g.outer)), c = centroid(g.outer); wx += c[0] * a; wy += c[1] * a; w += a; }
  return w > 0 ? [wx / w, wy / w] : [0, 0];
};

/* THE BALL FORM'S FRAME at u - the whole state as melt's own phases and two clocks, a pure function of u:
     phase  melt.mjs's own share of the window: `melt` the SAG [0, MELT_END), `ball` the ball [MELT_END, BALL_END),
            `fly` the ENDING [BALL_END, 1), `gone` at u >= 1. The shares are melt's dials, not ours.
     sag    the sag's progress, 1 from the ball on          ball  the ball's, 0 through the sag and 1 from the ending
     morph  `then: morph` only - the ball into the comparator's glyphs, on min-jerk over the ending
     write  when the HAND writes the comparator's own text: never on a morph (the outlines ARE the glyphs, and the
            text takes over at u = 1 exactly), from melt's RELEASE on a throw (the ball is gone), from the burst's
            end on a splash (the hand writes through the drying splatter)
     text   the metric AS QUOTED until the ending begins, the comparator AS AUTHORED from there - so the element the
            ghost is measured against carries the comparator through the whole ending and never jumps at the landing
   The ball and the ending run on melt's STEPPED clock (on 2s, stop-action), each on its own phase-local seconds -
   a pure quantisation of t, so a cold seek into the middle of the ball lands on the pose a play was holding. */
export const compareBallFrame = (sp, u, then_) => {
  const S = sp || {}, uu = cmp01(u), dur = Math.max(0.001, +S.dur || 1), ph = meltPhase(uu);
  const span = Math.max(1e-6, ph.span * dur), tl = Math.max(0, uu * dur - ph.from * dur);
  const kq = (ph.name === "melt" || ph.name === "gone") ? ph.k : cmp01(stepped(tl, MELT.HOLD, MELT.FPS) / span);
  const kEnd = ph.name === "fly" ? kq : (ph.name === "gone" ? 1 : 0);
  const release = meltRelease();
  const write = then_ === "morph" ? (uu >= 1 ? 1 : 0)
    : then_ === "throw" ? cmp01((uu - release) / Math.max(1e-6, 1 - release))
    : cmp01((kEnd - MELT.BURST_END) / Math.max(1e-6, 1 - MELT.BURST_END));
  const sub = cmp01((uu - COMPARE.LABEL_AT) / (1 - COMPARE.LABEL_AT));
  return { then: then_, phase: ph.name, k: kq, kEnd, write, u: uu, sub, ghost: sub * COMPARE.GHOST_A,
           sag: ph.name === "melt" ? ph.k : 1, ball: ph.name === "melt" ? 0 : (ph.name === "ball" ? minJerk(kq) : 1),
           morph: then_ === "morph" ? minJerk(kEnd) : 0,
           burst: then_ === "splash" ? cmp01(kEnd / Math.max(1e-6, MELT.BURST_END)) : 0,
           fly: then_ === "throw" ? cmp01((kEnd - MELT.ANTIC) / Math.max(1e-6, 1 - MELT.ANTIC)) : 0,
           text: uu >= MELT.BALL_END ? String((S.comparator || {}).text == null ? "" : (S.comparator || {}).text)
                                     : String((S.metric || {}).text == null ? "" : (S.metric || {}).text) };
};

/* the squash tensor as a transform about a point: stretched along theta by a, pressed across it by the same - the
   shape stopaction's impactSquash names, written out rather than mounted through squash.mjs's matrix */
export const compareSquashXf = (c, a, theta) => {
  if (!(Math.abs(a) > 1e-4)) return "";
  const d = (theta || 0) * 180 / Math.PI;
  return "translate(" + c[0].toFixed(2) + " " + c[1].toFixed(2) + ") rotate(" + d.toFixed(2) + ") scale("
    + (1 + a).toFixed(4) + " " + (1 - a).toFixed(4) + ") rotate(" + (-d).toFixed(2) + ") translate("
    + (-c[0]).toFixed(2) + " " + (-c[1]).toFixed(2) + ")";
};

/* THE BALL FORM'S OWN ELEMENTS, built once and never rebuilt: one <path> for the ink (the glyphs, the ball, the
   comparator's glyphs - all of it one fill) and one for the splatter, inside a <g> the throw's flight transforms. */
export const compareBallEnsure = (fg, P, ctx) => {
  if (P.ball) return P.ball;
  const el = (ctx || {}).el, col = compareFill(fg);
  const g = el ? el("g", "", fg.g, {}) : null;
  const ink = el && g ? el("path", "", g, { d: "", fill: col, "fill-rule": "nonzero", stroke: "none", opacity: 0 }) : null;
  const drop = el && g ? el("path", "", g, { d: "", fill: col, "fill-rule": "nonzero", stroke: "none", opacity: 0 }) : null;
  P.ball = { g, ink, drop, col, shape: null, key: "" };
  return P.ball;
};

/* THE RINGS THIS FIGURE MORPHS, prepared once per (metric, comparator, face) and read every frame. Everything
   expensive is here: two rasters, two contours, two pairings and their morph_a preparations. A page that lost its
   face, a node caller and a probe all get null - and then the morph paints NO OUTLINES, which is not another form:
   the ends are still the authored strings, and nothing between them is invented. */
export const compareBallRings = (fg, P, sp, then_) => {
  const B = P.ball;
  const face = compareFace(fg.label, fg.fs);
  if (!face) return null;
  const key = compareFontString(face, 1) + "\x00" + String((sp.metric || {}).text) + "\x00" + String((sp.comparator || {}).text);
  if (B.shape && B.key === key) return B.shape;
  const M = compareShape((sp.metric || {}).text, face), C = compareShape((sp.comparator || {}).text, face);
  if (!M) return null;
  const mAt = compareAtPen(M, fg), rnd = compareRnd(fg), drips = meltDrips(mAt.box, rnd);
  const sagged = compareGroups(mAt.rings).map((g) => ({
    outer: compareSagAt(g.outer, 1, mAt.box, drips), holes: g.holes.map((h) => compareSagAt(h, 1, mAt.box, drips)), c: [0, 0] }));
  sagged.forEach((g) => { g.c = centroid(g.outer); });
  const r = compareBallR(mAt.area, fg.fs), c = compareBallC(sagged);
  const ballG = [{ outer: ballCircle(c, r, MELT.CIRCLE_N), holes: [], c: c }];
  const shape = { rings: mAt.rings, box: mAt.box, drips, rnd, r, c, groups: compareGroups(mAt.rings),
                  toBall: comparePrepare(comparePairGroups(sagged, ballG, COMPARE.DEGEN_R)), toText: null };
  if (then_ === "morph" && C) {
    const cAt = compareAtPen(C, fg);
    shape.toText = comparePrepare(comparePairGroups(ballG, compareGroups(cAt.rings), COMPARE.DEGEN_R));
  }
  B.shape = shape; B.key = key;
  return shape;
};

/* THE BALL FORM'S PAINT (E76 s5). The quoted figure's own outlines SAG on melt's law, BALL UP into one disc that
   holds the ink's area, and then the ending happens to the ball: `morph` carries it into the comparator's glyphs
   (the pairing rule, one ring into N), `splash` bursts it onto the page, `throw` throws it off. The figure's own
   <text> is dark while the outlines are on stage and is the thing on screen again at u = 1 exactly - so the landed
   frame is the page's own type, and `hold: metric` ghosts beside it as it always did. */
const paintCompareBall = (fg, sp, u, before, ctx, then_) => {
  const F = compareBallFrame(sp, u, then_);
  const P = compareEnsure(fg, sp, ctx, Math.max(compareCapacity(sp), F.text.length));
  const B = compareBallEnsure(fg, P, ctx);
  const R = before ? null : compareBallRings(fg, P, sp, then_);
  const chars = [...F.text], n = chars.length;
  P.cells.forEach((ts, j) => {
    const ch = j < n ? chars[j] : "";
    ts.textContent = ch === " " ? " " : ch;
    ts.setAttribute("dy", "0.00");   /* the ball never runs the glyphs themselves: the ink left the cells entirely */
    if (before) { if (j >= (fg.lg || []).length) ts.setAttribute("opacity", 0); return; }
    ts.setAttribute("opacity", (j >= n ? 0 : figureGlyph(F.write, j, n)).toFixed(3));
  });
  if (B.g) {
    const on = !before && !!R && F.u > 0 && F.u < 1;
    /* the SAG is painted from the rings themselves (the ball's own morph starts where it ends), the ball and the
       ending from morph_a's prepared pairs - one law, three stages, every one of them a pure function of u */
    let path = "";
    if (on && F.phase === "melt") {
      path = R.groups.map((g) => {
        const outer = morphAPath(compareSagAt(g.outer, F.sag, R.box, R.drips));
        return outer + " " + g.holes.map((h) => morphAPath(compareSagAt(h, F.sag, R.box, R.drips).slice().reverse())).join(" ");
      }).join(" ");
    } else if (on && F.phase === "ball") {
      path = comparePath(R.toBall, F.ball);
    } else if (on && then_ === "morph" && R.toText) {
      path = comparePath(R.toText, F.morph);
    } else if (on) {
      const circle = ballCircle(R.c, R.r, MELT.CIRCLE_N);
      path = morphAPath(then_ === "splash" ? ballFlat(circle, R.c, F.burst) : circle);
    }
    B.ink.setAttribute("d", path);
    compareInk(B.ink, on && path ? 1 : 0);
    let xf = "";
    if (on && then_ === "throw" && F.phase === "fly") {
      const to = { x: (+fg.W || 0) * MELT.TO[0] - R.c[0], y: (+fg.H || 0) * MELT.TO[1] - R.c[1] };
      const span = Math.max(0.05, (+sp.dur || 1) * (1 - MELT.BALL_END));
      if (F.kEnd < MELT.ANTIC) xf = compareSquashXf(R.c, meltSettle(F.kEnd * span), 0);
      else {
        const x = meltThrowAt(F.fly, to, span * (1 - MELT.ANTIC));
        xf = "translate(" + (x.x || 0).toFixed(2) + " " + (x.y || 0).toFixed(2) + ") "
           + compareSquashXf(R.c, x.alpha || 0, x.theta || 0);
      }
    }
    B.g.setAttribute("transform", xf);
    let drops = "";
    if (on && then_ === "splash" && F.phase === "fly") {
      const dd = splashDrops(R.c, R.box, F.burst, R.rnd);
      drops = dd.map((p, i) => meltSplatPath(p.x, p.y, p.r, p.a, p.tail, R.rnd, i + 1)).join(" ")
        + " " + splashSats(dd).map((s) => morphAPath(ballCircle([s.x, s.y], s.r, 16))).join(" ");
    }
    B.drop.setAttribute("d", drops);
    compareInk(B.drop, drops ? 1 - minJerk(F.write) : 0);
  }
  compareBeside(fg, P, sp, F.text, before, F.ghost, (j, n2) => compareGlyph(F.sub, j, n2));
};

/* THE PAINTER (the module rule's page half). Every number of it is the law above; this is the DOM. `sd` is what
   the engine's chart_to dispatch hands it - the row `sp` and the page's built figures - `st` the page state, and
   `ctx` the PAGE species context every page painter reaches the engine through (`el` is lpEl), so `node --test`
   can call this with recorders and no DOM. The FORM is read first: an unnamed one is `melt` - the ball - and an
   unknown one throws; `then` is read on the ball alone, because a form that makes no ball has nothing to end. */
export const paintCompare = (sd, t, st, ctx) => {
  const sp = (sd || {}).sp || {}, fg = compareFigure((sd || {}).figures, sp);
  if (!fg || !fg.label) return;
  const form = compareForm(sp);
  const at = +sp.at || 0, u = cmp01((t - at) / Math.max(0.001, +sp.dur || 1)), before = t < at;
  if (form === "count") { paintCompareCount(fg, sp, u, before, ctx); return; }
  if (form === "melt") { paintCompareBall(fg, sp, u, before, ctx, compareThen(sp)); return; }
  paintCompareMorph(fg, sp, u, before, ctx, form);
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment, so
   inlining keeps it and node - where no registry exists - still imports the file for the math. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.compare = paintCompare;
