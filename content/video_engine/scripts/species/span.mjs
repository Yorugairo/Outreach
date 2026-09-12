/* SPACE: page */
/* species/span.mjs - THE SPAN (P50 T4; BACKLOG R26-25, the intake's Archetype 5; Bravos shots 107-110's
   "Decades" bracket). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between
   KINETICS:BEGIN span and KINETICS:END. It imports nothing, and its region sits with the kinetics laws
   rather than in the species block at the foot of the file - on purpose: a PAGE species' math is called by
   the page's PERFORM layer, which is written hundreds of lines above the species block, and a const has to
   exist before the function that closes over it is built.

   WHEN: the sentence SPANS a period on a chart - a regime, an epoch, "the decade" - shaded behind the line
   with its name. A BRACKET measures two data; a SPAN names a stretch of time. That is the whole difference,
   and it is why this is a second species and not a bracket option: a bracket's label is a NUMBER it measured,
   a span's label is a NAME it gives.

   THE LAW, a pure function of t:
     shade  - the band between the two declared edges fades in over IN_S to ALPHA, behind every line (it is
              ground, not ink on top - the same rule the spread follows), and it is SUNK into the ground
              layer to prove it: the bottom of the active chart state's own svg, never the annotation layer
              (R26-68; spanGroundLayer below).
     label  - written above the band BY THE HAND, glyph after glyph, over WRITE of the word, starting when
              the shade is in. Above the band where there is room for it, inside its top edge where there
              is not (a chart that fills its box has nothing over it).
   R26-68 (the one-shot's frames, 2026-09-12: "the grey block covers the line it is measuring, and the page's
   own series label sits inside the shade"). Two halves, both here:
     the LAYER - a page with chart STATES gets a perform svg stacked ABOVE every state, and a shade built into
                 it washes the very line it stands behind. A shade is ground: the painter sinks the rect to the
                 bottom of the ACTIVE state's own svg every frame (idempotent, so a seek is the play, and a
                 rebuilt state gets its shade back). A one-state page already drew it there - nothing moves.
     the LABEL - the band's PAD is room, not an edge, so the pad YIELDS: where one of the page's own direct
                 labels (a series' terminal tag, a printed value - read off the engine's MARK MODEL) stands
                 inside the band's x range and above the ink's highest point, the shade's top stops LABEL_CLEAR
                 short of its baseline and the label is left on the ground. The EDGES never move (they are the
                 stretch of time the span names), and the span's own name keeps the raw top (`band.yTop`), so it
                 stands exactly where it stood and the text-on-text gate M28 reads the same geometry.
   THE EDGES. `from` and `to` are each either a DATUM INDEX (an integer: the page's own index, the one a
   bracket and a figure use) or an X-FRACTION (a number in 0..1 along the drawn series' own x extent, for a
   period that falls between two data). Both are resolved on the ACTIVE chart state every frame, from the
   same live points a bracket reads (R26-28): a rescale moves the band with the data, and a window that has
   dropped one of the two edges hides it rather than drawing it in the wrong place.

   THE PAINTER IS HERE NOW (P52 T5, R26-41; it was engine code until then, and that WAS the finding): a PAGE
   species is painted in a different space from a stage species - inside the chart's viewBox, on the page state
   `st`, under the active state's park transform, off the page's perform clock - so it registers into the page
   registry, PAGE_PAINTERS, and not into SPECIES_PAINTERS, which hands its painters the stage-px overlay and the
   scene's clock. The `SPACE: page` line above - the module's first line, in a comment of its own - is that
   declaration, and sync_kinetics --check is what holds the module to it: a page module that registers into the
   stage registry fails by name, and so does a stage module that registers into the page one.
   The dials below are ours to tune (42 s42.5), not findings. */

export const SPAN = Object.freeze({
  IN_S: 0.45,       /* the shade's fade-in: a period ARRIVES, it does not cut in - slower than a bracket's tick, because nothing is being measured */
  ALPHA: 0.16,      /* ... and what it settles at: enough to read as a region behind the line, never enough to fight it (the spread bleeds to 0.30 because the gap IS its argument; a span is only the room the argument happens in) */
  WRITE: 0.5,       /* the share of the word the label's hand takes, after the shade is in */
  PAD_T: 44,        /* the band's reach above the highest point of the drawn data, in the chart's viewBox units ... */
  PAD_B: 44,        /* ... and below the lowest: it is a band behind the chart, not a box around the line */
  LABEL_DY: 16,     /* the label's baseline above the band's top edge, where the band has room above it ... */
  LABEL_IN: 2.1,    /* ... and, where it does not, inside the top edge by this many of the label's own sizes: two lines down, clear of the plot's own top furniture (the unit caption sits on the first line inside the plot - read in the frame, 2026-09-11) */
  LABEL_ROOM: 1.3,  /* "room above" means this many label sizes clear of the chart's top - otherwise the name is written inside the band */
  MIN_W: 6,         /* a band narrower than this is not a period - it is two adjacent data, which is a bracket's job */
  LABEL_CLEAR: 0.55,/* R26-68: how far short of a page label's baseline the shade's top stops, in the span's own label sizes - a page's series tag is the DATA's name and reads on the ground, never inside a wash */
});

const span01 = (v) => Math.min(1, Math.max(0, v));

/* is this edge a DATUM INDEX (an integer) or an X-FRACTION? */
export const spanIsIndex = (v) => Number.isInteger(v);

/* ONE EDGE -> x in the chart's viewBox. `entries` is the series' live points in lpPointsNow's shape,
   [{i, p: [x, y]}]: an index resolves to the point that CARRIES it (a window that dropped it -> null), a
   fraction to that position along the drawn series' own x extent. */
export const spanEdgeX = (entries, v) => {
  if (!Array.isArray(entries) || entries.length < 2) return null;
  if (spanIsIndex(v)) { const e = entries.find((q) => q.i === v); return e ? e.p[0] : null; }
  const f = +v;
  if (!Number.isFinite(f)) return null;
  const a = entries[0].p[0], b = entries[entries.length - 1].p[0];
  return a + span01(f) * (b - a);
};

/* the band's vertical reach: every drawn series' points, padded - so the shade stands behind the whole
   chart and moves with it, and never has to be told where the plot box is */
export const spanExtent = (lists) => {
  let y0 = Infinity, y1 = -Infinity;
  for (const l of lists || []) for (const q of (l || [])) { y0 = Math.min(y0, q.p[1]); y1 = Math.max(y1, q.p[1]); }
  return Number.isFinite(y0) && Number.isFinite(y1) ? { y0: y0 - SPAN.PAD_T, y1: y1 + SPAN.PAD_B } : null;
};

/* THE PAGE'S LAYERS, as the page publishes them - on its own STATE, which is what a page painter is handed
   (there is no layer field in the page species context: it carries the engine's helpers, not its DOM). Every
   chart state owns a `chart` svg and draws its whole world into it - ground, grid, lines, marks, the page's own
   labels, in that order - and `st.performSvg`, on a page with states, is the ANNOTATION layer stacked above all
   of them. The active state is the one a datum resolves against, so it is the one a shade belongs under. */
export const spanActiveState = (st) => ((st && st.states && st.states.length ? st.states[st.active | 0] : null) || st || null);
export const spanGroundLayer = (st) => { const S = spanActiveState(st); return (S && S.chart) || (st && st.chart) || null; };

/* the shade to the BOTTOM of that layer - under the first thing the chart draws, which is where the spread puts
   its own fill for the same reason. Idempotent: it moves nothing once the rect is there, so a cold seek lands it
   exactly where a play does, and a state whose svg was rebuilt gets its shade back on the next frame. */
export const spanSink = (rect, layer) => {
  if (!rect || !layer || typeof layer.insertBefore !== "function") return false;
  if (layer.firstChild === rect) return false;
  layer.insertBefore(rect, layer.firstChild || null);
  return true;
};

/* THE PAGE'S OWN DIRECT LABELS, off the engine's MARK MODEL (every builder registers what it drew under a role
   and the geom that placed it): the series' terminal tag and a printed value - the two labels that belong to the
   DATA, and so the two that can end up standing inside a stretch of it. The plot's furniture is deliberately not
   read: the ticks, the axis captions and the source line live at the plot's edges, and the basis caption read
   over a 0.16 wash is the very thing LABEL_IN was tuned against (the golden `span-decade`). */
export const SPAN_LABEL_ROLES = Object.freeze(["name", "value"]);
export const spanPageLabels = (st) => {
  const S = spanActiveState(st), out = [];
  for (const m of (S && S.marks) || []) {
    if (!m || SPAN_LABEL_ROLES.indexOf(m.role) < 0) continue;
    const g = m.geom || {}, x = +g.x, y = +g.y;
    if (!Number.isFinite(x) || !Number.isFinite(y)) continue;
    if (m.el && typeof m.el.textContent === "string" && !m.el.textContent.trim()) continue;   /* a muted history's empty tag names nothing */
    out.push({ x, y });
  }
  return out;
};

/* THE SHADE'S TOP (R26-68): the pad yields to a label, the ink never does. A label inside the band's x range
   whose baseline sits in the HEADROOM - between the padded top and the highest drawn point - pushes the shade's
   top to `clear` below itself; the top never falls past the data it stands behind, so the shade still reaches
   the ink it is the room for. `top0` is the band's raw (clipped) top, `dataTop` the highest drawn point. */
export const spanTop = (top0, dataTop, x0, x1, labels, clear) => {
  let y = top0;
  for (const L of labels || []) {
    if (!L || !(L.x >= x0 && L.x <= x1)) continue;
    if (!(L.y >= top0 && L.y <= dataTop)) continue;
    y = Math.max(y, L.y + (clear || 0));
  }
  return Math.min(Math.max(y, top0), Math.max(top0, dataTop));
};

/* THE BAND this frame, or null when either edge has left the window (the bracket's rule: nothing to name,
   nothing drawn). `entries` is the named series' live points, `lists` every series', `H` the chart's viewBox
   height when the caller knows it - the band is clipped to the page rather than drawn off it. `labels` are the
   page's own direct labels (spanPageLabels) and `clear` the room to leave under one: given neither, the band is
   exactly the pad's, which is how a caller with no page to read - a test, a probe - gets the raw law. */
export const spanBand = (entries, lists, from, to, H, labels, clear) => {
  const a = spanEdgeX(entries, from), b = spanEdgeX(entries, to), ext = spanExtent(lists);
  if (a === null || b === null || !ext) return null;
  const x0 = Math.min(a, b), x1 = Math.max(a, b);
  if (!(x1 - x0 >= SPAN.MIN_W)) return null;
  const top = Number.isFinite(H) ? Math.max(0, ext.y0) : ext.y0;
  const bot = Number.isFinite(H) ? Math.min(H, ext.y1) : ext.y1;
  if (!(bot > top)) return null;
  const cut = spanTop(top, ext.y0 + SPAN.PAD_T, x0, x1, labels, clear);   /* R26-68: the shade stops short of a label in its headroom ... */
  const y = cut < bot ? cut : top;                                        /* ... unless that would leave no band at all */
  return { x: x0, w: x1 - x0, y, h: bot - y, yTop: top, cx: (x0 + x1) / 2 };
};

/* where the name is written: above the band when the chart leaves room over it, inside its top edge when
   the chart fills its box (the bracket's own rule for a label with nowhere to stand). R26-68: off the band's
   RAW top (`yTop`), never the top the shade gave up to a label - the name stands where it always stood, so
   M28's text-on-text geometry is the one it already passed, and the name can never drop onto the very label
   the shade just cleared. */
export const spanLabelY = (band, fs) => { const y = band.yTop != null ? band.yTop : band.y;
  return y >= fs * SPAN.LABEL_ROOM ? y - SPAN.LABEL_DY : y + fs * SPAN.LABEL_IN; };

/* THE POSE at t: is it up, how deep is the shade, how far has the hand written. */
export const spanPose = (sp, t) => {
  const at = +sp.at, dur = Math.max(0.001, +sp.dur || 1), d = t - at;
  const shade = span01(d / SPAN.IN_S);
  return { on: d >= 0, shade, alpha: SPAN.ALPHA * shade, write: span01((d - SPAN.IN_S) / (dur * SPAN.WRITE)) };
};

/* one glyph's opacity as the hand writes the label: each glyph over its share of the write, with the 1.6
   overlap the bracket and the figure use, so the line reads as a hand and not as a ticker. The share is
   1 / (n + 0.6), not 1 / n, so the LAST glyph is fully in exactly when the write ends - at 1 / n the tail
   of the name would still be at 0.625 when the word was over (the bracket buys the same slack by writing
   its label over only part of its own window). */
export const spanGlyph = (write, j, n) => {
  const per = 1 / (Math.max(1, n | 0) + 1.6 - 1);
  return span01((write - j * per) / (per * 1.6));
};

/* THE PAINTER (P52 T5; R26-41). The band re-read on the LIVE scale every frame, the shade fading in under the
   lines, the name written above it by the hand - every number of it is the law above; this is the DOM.
   `sd` is the perform layer's built span (rect, label, the label's glyphs `lg`, its size `fs`, the series `si`
   and the declaration `sp`), `st` the page state, and `ctx` the PAGE species context the engine hands every page
   painter (see PAGE_PAINTERS in the engine): the engine's helpers arrive BY NAME - `pointsNow` is the perform
   layer's lpPointsNow - never as a free identifier, so `node --test` can call this with recorders and no DOM. */
export const paintSpan = (sd, t, st, ctx) => {
  const pose = spanPose(sd.sp, t);
  const hide = () => { sd.rect.setAttribute("fill-opacity", 0); sd.label.setAttribute("opacity", 0); };
  if (!pose.on) { hide(); return; }
  const lists = [];
  for (let i = 0; i < Math.max(1, (st.linePts || []).length); i++) lists.push(ctx.pointsNow(st, i));
  const band = spanBand(lists[sd.si] || [], lists, sd.sp.from, sd.sp.to, (st.geom || {}).H,
                        spanPageLabels(st), SPAN.LABEL_CLEAR * sd.fs);
  if (!band) { hide(); return; }   /* R26-28: an edge the window dropped names nothing - nothing is drawn */
  spanSink(sd.rect, spanGroundLayer(st));   /* R26-68: a shade is GROUND - under the state's own ink every frame, or it is not a shade */
  sd.rect.setAttribute("x", band.x.toFixed(1)); sd.rect.setAttribute("y", band.y.toFixed(1));
  sd.rect.setAttribute("width", band.w.toFixed(1)); sd.rect.setAttribute("height", band.h.toFixed(1));
  sd.rect.setAttribute("fill-opacity", pose.alpha.toFixed(3));
  sd.label.setAttribute("opacity", 1);
  sd.label.setAttribute("x", band.cx.toFixed(1));
  sd.label.setAttribute("y", spanLabelY(band, sd.fs).toFixed(1));
  sd.lg.forEach((ts, j) => ts.setAttribute("opacity", spanGlyph(pose.write, j, sd.lg.length).toFixed(3)));
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment,
   so inlining keeps it and node - where no registry exists - still imports the file for the math. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.span = paintSpan;
