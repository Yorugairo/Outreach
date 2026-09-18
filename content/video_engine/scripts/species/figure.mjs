/* SPACE: page */
/* species/figure.mjs - THE FIGURE (P57 T20 / R26-98). SOURCE OF TRUTH, inlined into the scene-evidence player
   by sync_kinetics.py between KINETICS:BEGIN figure and KINETICS:END. It imports nothing, and its region sits
   with the kinetics laws rather than in the species block at the foot of the file, for the reason span.mjs
   gives: a PAGE species' math is called by the page's PERFORM layer, written hundreds of lines above the
   species block, and a const has to exist before the function that closes over it is built.

   THIS IS A PAGE PAINTER - the one way this promotion differs from T17-T19 (`trace`, `spotlight` and the
   stage species before them). A page species is painted in a different space: inside the chart's viewBox, on
   the page state `st`, under the active state's park transform, off the page's perform clock. So the last
   statement registers it into PAGE_PAINTERS, never SPECIES_PAINTERS - which hands its painters the stage-px
   overlay and the scene's clock - and the `SPACE: page` line above, the module's first line in a comment of
   its own, is that declaration. `sync_kinetics --check` holds the module to it by name (:122).

   WHEN (`SPECIES_WHEN["figure"]`, build_scene_timeline_f.py:331, verbatim): "the sentence TURNS on a number -
   the hand writes it at its datum's spot (a note when the datum has no room)".

   THE LAW - E50 (P47 T6, the chart's next thing): THE NUMBER THE SENTENCE TURNS TO, WRITTEN BY THE HAND AT
   ITS DATUM. Not stamped, not typed: written glyph after glyph in the page's own hand, in its series' ink
   (E67), at the place the line was - no pin dot, because the third watch found lingering dots read as strange.
   R26-71 (2026-09-14) is the second half of the law: THE BOX STEPS OFF ITS OWN SERIES' INK. The bridge short
   printed `31% of GDP` straight through the debt line it named; a number written across the line it names is
   unreadable, and a figure that has to move moves in NAMED QUANTA - never a search, never a solver.

   THE FORM, all of it a pure function of the datum, the live points and t:
     the place  beside the datum: to the RIGHT when the chart has room there (`fits` - the bracket's own room
                test), else LEFTWARD from it, anchored `end`, which is what a peak at the right edge takes.
                The baseline is the datum plus BASE_DY of the figure's size, plus the authored `dy` in LINEs
                of that size (negative lifts it), and the sub hangs SUB_DY of its own size beneath.
     the step   R26-71: the authored place STANDS unless the figure's box meets the stroke of its own series.
                Then it steps in quanta of FIGURE_STEP * fs - the side the authored `dy` already chose FIRST,
                then the other - capped at FIGURE_STEPS and at the chart's own box. Nowhere clear leaves the
                authored place (and the collision gate still says so). The advance is MEASURED off the written
                glyphs where they are on the page, arithmetic (FIGURE_CHAR_W) where nothing can measure.
     the write  the figure writes glyph by glyph over the first WRITE of its word, the sub over the rest, each
                glyph over its share with the OVERLAP the bracket and the span use - so it reads as a hand and
                not as a ticker.
     the state  P48 T7: on a page with chart STATES the figure follows the ACTIVE state's datum every frame -
                a datum the window dropped shows nothing - and the step-off is re-run on that state's own live
                points, so a cold seek lands exactly where a play does (R26-28).
   The dials below are ours to tune (42 s42.5), not findings. Promoted from inline engine code (`paintFigure`
   + R26-71's `segMeetsBox` / `figBox` / `figClearY` and the `PS.FIGURE_*` dials) with every golden byte-
   identical: each literal below is the value the inline code carried, to the digit, and no expression was
   re-associated. The six R26-71 dials KEEP their inline names inside this object, because R26-71's own test
   (`tests/test_figure_placement.py`) reads `FIGURE_STEP:` and `FIGURE_STEPS:` off the engine's text by name -
   a rename there would be a silent claim about a number nobody changed. */

export const FIGURE = Object.freeze({
  FIGURE_STEP: 0.6,    /* R26-71: one step off the ink, as a share of the figure's size ... */
  FIGURE_STEPS: 4,     /* ... and the cap either side of the authored place: past this, nothing is clear */
  FIGURE_PAD: 5,       /* the daylight kept from the stroke (half the widest series line, and a hair) */
  FIGURE_UP: 1.08,     /* the glyph box above the baseline, in sizes (measured on the hand at 40: 1.075) ... */
  FIGURE_DOWN: 0.53,   /* ... and below it (0.525) - the box the EYE reads, not the font's own metrics */
  FIGURE_CHAR_W: 0.62, /* the advance per character when nothing can measure the text (no glyphs on a page yet) */
  X_PAD: 14,           /* the daylight between the datum and the first glyph, either side */
  BASE_DY: 0.35,       /* the baseline's own drop from the datum, in figure sizes (the type sits ON the point) */
  LINE: 1.2,           /* one authored `dy` line, in figure sizes: `dy: -0.9` lifts it nine tenths of a line */
  SUB_DY: 1.3,         /* the sub's baseline beneath the figure's, in SUB sizes */
  WRITE: 0.6,          /* the share of the word the figure's own hand takes ... */
  SUB_WRITE: 0.4,      /* ... and the share the sub takes after it (the two are the whole word) */
  OVERLAP: 1.6,        /* each glyph fades over this many of its own shares - the hand's overlap, not a ticker's */
});

const fig01 = (v) => Math.min(1, Math.max(0, v));   /* the engine's clamp01, verbatim */

/* R26-71: does a segment meet a box grown by `pad`? Liang-Barsky - exact, allocation-free, and asked once per
   segment of one series, so a page of figures costs the points it already holds. */
export const segMeetsBox = (p0, p1, b, pad) => {
  const x0 = b[0] - pad, y0 = b[1] - pad, x1 = b[0] + b[2] + pad, y1 = b[1] + b[3] + pad;
  const dx = p1[0] - p0[0], dy = p1[1] - p0[1];
  const P = [-dx, dx, -dy, dy], Q = [p0[0] - x0, x1 - p0[0], p0[1] - y0, y1 - p0[1]];
  let t0 = 0, t1 = 1;
  for (let i = 0; i < 4; i++) {
    if (P[i] === 0) { if (Q[i] < 0) return false; continue; }
    const r = Q[i] / P[i];
    if (P[i] < 0) { if (r > t1) return false; if (r > t0) t0 = r; }
    else { if (r < t0) return false; if (r < t1) t1 = r; }
  }
  return true;
};

/* R26-191: do two boxes MEET, with `pad` of daylight between them? The step-off asks this of the page's own
   labels exactly as segMeetsBox asks it of the series' stroke - the same daylight, no second dial. */
export const boxMeetsBox = (a, b, pad) => (a[0] - pad < b[0] + b[2] && b[0] - pad < a[0] + a[2]
                                        && a[1] - pad < b[1] + b[3] && b[1] - pad < a[1] + a[3]);

/* the figure's text box for a baseline at (x, y): the advance, and the glyph box either side of the baseline
   (a sub hangs under it by its own line) - the box the eye reads, in the chart's own viewBox units */
export const figBox = (x, y, w, fs, anchor, subH) => [anchor === "end" ? x - w : x, y - FIGURE.FIGURE_UP * fs, w,
                                                      (FIGURE.FIGURE_UP + FIGURE.FIGURE_DOWN) * fs + (subH || 0)];

export const figWidth = (el, text, fs) => {   /* measured when the glyphs are on the page; arithmetic when nothing can measure */
  const n = el && el.getComputedTextLength ? el.getComputedTextLength() : 0;
  return n > 0 ? n : String(text || "").length * fs * FIGURE.FIGURE_CHAR_W;
};

/* R26-71: THE STEP-OFF. The authored place stands unless the box meets the stroke of its own series; then the
   figure steps away in quanta of FIGURE.FIGURE_STEP * fs - the side the authored `dy` already chose FIRST, then
   the other - capped at FIGURE.FIGURE_STEPS and at the chart's own box. A pure function of the datum, the
   series' live points, `dy` and the measured width: a re-read frame on a changed chart state lands identically
   and a cold seek lands where a play does (R26-28). Nowhere clear = the authored place, and the gate still says so.

   R26-191 (the operator, 2026-09-17: *"our labels were clean until we rebuilt in the last few days"*). The step
   off the ink walked onto the page's OWN LABELS, because the chart's box (`inBox`) was the only other thing it
   asked: on Tokyo's customs page the figure "$1,116.7B" took all four steps DOWN - 4 x 0.6 x 40 = 96 px - clear
   of its line's ink and straight onto the month tick "Jun '26" (1,550 px of overlap, M28) and the series name
   (340 px), where the approved 2026-09-11 cut had it clear at the authored place. So a candidate must clear the
   page's labels TOO: `avoid` carries their boxes in the chart's own units (the engine measures them once, at
   build, and hands the same list to the painter). Nothing else moves - only INK triggers a step, a label never
   pushes a figure, and when no candidate is clear of both the figure keeps the AUTHORED place, which is exactly
   where it stood before R26-71. */
export const figClearY = (x, yA, w, fs, anchor, dy, ptsNow, subH, H, avoid) => {
  const pts = ptsNow || [], keep = Array.isArray(avoid) ? avoid : [];
  if (pts.length < 2 || !(w > 0)) return yA;
  const onInk = (yy) => {
    const b = figBox(x, yy, w, fs, anchor, subH);
    for (let i = 1; i < pts.length; i++) if (segMeetsBox(pts[i - 1], pts[i], b, FIGURE.FIGURE_PAD)) return true;
    return false;
  };
  if (!onInk(yA)) return yA;   /* the authored place is only ever left for ink - never for the chart's edge */
  /* R26-191: ... and a step never lands ON one of the page's own labels */
  const onLabel = (yy) => {
    if (!keep.length) return false;
    const b = figBox(x, yy, w, fs, anchor, subH);
    for (const q of keep) if (q && q.length === 4 && boxMeetsBox(b, q, FIGURE.FIGURE_PAD)) return true;
    return false;
  };
  const inBox = (yy) => { const b = figBox(x, yy, w, fs, anchor, subH); return b[1] >= 0 && b[1] + b[3] <= (H || Infinity); };
  const first = (Number(dy) || 0) <= 0 ? -1 : 1;   /* `dy` lifted it off the datum: it keeps lifting */
  for (const side of [first, -first]) for (let k = 1; k <= FIGURE.FIGURE_STEPS; k++) {
    const yy = yA + side * k * FIGURE.FIGURE_STEP * fs;
    if (inBox(yy) && !onInk(yy) && !onLabel(yy)) return yy;
  }
  return yA;
};

/* THE AUTHORED PLACE, from the datum alone: which side the number is written on (the bracket's own room test -
   `gap` and `room` are PS.BRACKET_GAP and PS.BRACKET_ROOM, handed in so this module owns no bracket dial), and
   the baseline before R26-71 has had its say. The BUILDER and the PAINTER both come through here, which is what
   makes a re-read frame land on the built one to the digit. */
export const figurePlace = (D, fs, dy, W, gap, room) => {
  const fits = D[0] + gap + room <= W, x = fits ? D[0] + FIGURE.X_PAD : D[0] - FIGURE.X_PAD;
  return { fits, x, anchor: fits ? "start" : "end",
           yA: D[1] + fs * FIGURE.BASE_DY + (Number(dy) || 0) * fs * FIGURE.LINE };
};

/* one glyph of the FIGURE as the hand writes it: each glyph over its share of WRITE, fading over OVERLAP
   shares, so the last glyph is still arriving as the word ends and the line never reads as a ticker */
export const figureGlyph = (u, j, n) => {
  const per = FIGURE.WRITE / Math.max(1, n);
  return fig01((u - j * per) / (per * FIGURE.OVERLAP));
};

/* one glyph of the SUB: the same hand, over SUB_WRITE, starting where the figure's own write ended */
export const figureSubGlyph = (u, j, n) => {
  const per = FIGURE.SUB_WRITE / Math.max(1, n);
  return fig01((u - FIGURE.WRITE - j * per) / (per * FIGURE.OVERLAP));
};

/* THE PAINTER (P47 T6; P48 T7; R26-71). `fg` is the perform layer's BUILT figure - the declaration `sp`, its
   datum `D`, its glyphs `lg` / `sg`, the measured advance `tw`, the sizes and the chart's box - `st` the page
   state, and `ctx` the PAGE species context the engine hands every page painter (PAGE_PAINTERS in the engine):
   the engine's helpers arrive BY NAME - `markDatum` is lpMarkDatum, `pointsNow` lpPointsNow, `PS` the page
   species dials the bracket owns - never as free identifiers, so `node --test` can call this with recorders
   and no DOM. The BUILDER stays in the engine's buildPerform, where the DOM it makes belongs; it calls this
   module's `figurePlace`, `figWidth` and `figClearY` by name, so the place is authored in one law only. */
export const paintFigure = (fg, t, st, ctx) => {
  const sp = fg.sp, dur = Math.max(0.001, sp.dur || 1), u = fig01((t - sp.at) / dur);
  fg.g.setAttribute("opacity", t >= sp.at ? 1 : 0);
  if (st && (st.states || []).length > 1) {   /* P48 T7: the figure stands at its datum on the ACTIVE state - a datum the window dropped shows nothing */
    const D = ctx.markDatum(st, fg.si, fg.idx);
    if (!D) { fg.g.setAttribute("opacity", 0); return; }
    const q = figurePlace(D, fg.fs, sp.dy, fg.W, ctx.PS.BRACKET_GAP, ctx.PS.BRACKET_ROOM);
    const y = figClearY(q.x, q.yA, fg.tw, fg.fs, q.anchor, sp.dy, ctx.pointsNow(st, fg.si).map((e) => e.p), fg.subH || 0, fg.H, st.labBoxes);   /* R26-71: the same step-off on the ACTIVE state's own points - and R26-191's labels, the list the BUILD measured (pure in t) */
    fg.label.setAttribute("x", q.x.toFixed(1)); fg.label.setAttribute("y", y.toFixed(1)); fg.label.setAttribute("text-anchor", q.anchor);
    if (fg.sub) { fg.sub.setAttribute("x", q.x.toFixed(1)); fg.sub.setAttribute("y", (y + fg.fss * FIGURE.SUB_DY).toFixed(1)); fg.sub.setAttribute("text-anchor", q.anchor); }
    fg.D = D; fg.x = q.x; fg.y = y; fg.fits = q.fits;   /* the record species/compare.mjs reads (PF.figures) - the same fields, in the same place */
  }
  fg.lg.forEach((ts, j) => ts.setAttribute("opacity", figureGlyph(u, j, fg.lg.length).toFixed(3)));
  fg.sg.forEach((ts, j) => ts.setAttribute("opacity", figureSubGlyph(u, j, fg.sg.length).toFixed(3)));
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment,
   so inlining keeps it and node - where no registry exists - still imports the file for the math. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.figure = paintFigure;
