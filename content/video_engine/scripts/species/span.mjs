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
  ALPHA: 0.16,      /* ... and what it settles at: enough to read as a region behind the line, never enough to fight it (the spread bleeds to 0.51 - D40's measured brightness, P72 T49 - because the gap IS its argument; a span is only the room the argument happens in) */
  WRITE: 0.5,       /* the share of the word the label's hand takes, after the shade is in */
  PAD_T: 44,        /* the band's reach above the highest point of the drawn data, in the chart's viewBox units ... */
  PAD_B: 44,        /* ... and below the lowest: it is a band behind the chart, not a box around the line */
  LABEL_DY: 16,     /* the label's baseline above the band's top edge, where the band has room above it ... */
  LABEL_IN: 2.1,    /* ... and, where it does not, inside the top edge by this many of the label's own sizes: two lines down, clear of the plot's own top furniture (the unit caption sits on the first line inside the plot - read in the frame, 2026-09-11) */
  LABEL_ROOM: 1.3,  /* "room above" means this many label sizes clear of the chart's top - otherwise the name is written inside the band */
  MIN_W: 6,         /* a band narrower than this is not a period - it is two adjacent data, which is a bracket's job */
  LABEL_CLEAR: 0.55,/* R26-68: how far short of a page label's baseline the shade's top stops, in the span's own label sizes - a page's series tag is the DATA's name and reads on the ground, never inside a wash */
  DARK: "#000",     /* E99 s7: the DARK tone's ground. The shade and its name part company - the name keeps the span's own colour, the ground goes to this at ALPHA. Black and not a palette token on purpose: a shade must DARKEN whatever it stands on and tint it with nothing, and the palette's only dark (`--lp-char`) IS the charcoal page, so on the page the operator was reading it is invisible. On a cream page it is the same shade, read the other way up. */
  TONE: "dark",     /* E99 s46, the operator on `r26-68-span-darker`: "yes" - the DEFAULT tone of a span whose build names none. A span is a darker region behind the line; `light` (the chalk-at-ALPHA every frame before 2026-09-15 carried) stays authorable by name on the `span_tone` dial, and the approved cuts keep it because they render through their own FROZEN players (E45). */
  ALPHA_DARK: 0.30, /* ... and the depth ruled WITH it: the dark ground settles here, where ALPHA (0.16) stays the light tone's law. Measured on the operator's own frame (build-short-axes 38.0 s): the band reads 21 L DARKER than the page, the gridlines and both figures still reading through it. */
});

const span01 = (v) => Math.min(1, Math.max(0, v));

/* P72 T46g (R26-407; Bravos A56, BOOM 17:55.5-17:58.5 - VERIFY.md's rescope) - THE FORMS. A span is a SHADE (the
   default, every span before this slice): the stretch's ground darkened behind every line, its name above. Or a BOX: a
   dashed rectangle round the NAMED series' own ink over the stretch - the box names the latest actual MOVE ("could
   continue until June of 2027": the box round the upswing, then the dated rule) - drawn round by length on its word,
   standing for its `dur`, then leaving so the date can be named. The compiler mirrors SPAN_FORMS
   (build_scene_timeline_f.SPAN_FORMS) and refuses anything else by name: an option accepted and silently dropped is
   R26-307's class (E99 s106). */
export const SPAN_FORMS = Object.freeze(["shade", "box"]);
export const SPAN_BOX = Object.freeze({
  PAD: 14,          /* the daylight round the stretch's own ink, in the chart's viewBox units (~ stage px on a 16:9 page: 1.08-1.33 px a unit) - Bravos keeps 11-20 px at 1920 (BOOM 17:56.5) */
  WIDTH: 3,         /* the dashed outline's weight - Bravos's ~4 px at 1920, under the series' own 4 */
  DASH: "12 8",     /* the dash and its gap - Bravos's ~14 / 8 px at 1920: a box that is plainly drawn, never a second line */
  DRAW_S: 0.5,      /* the pen goes round the box over this, from the span's `at` */
  LEAVE_S: 0.35,    /* ... and the box leaves over the last of its own `dur` (A56: gone before the dated rule lands) */
  LABEL_GAP: 4,     /* the box's right edge stops this short of a page label standing past the stretch's end (the end tag's column - R26-219's lesson for the shade: the memory-makers' tag stands 12 units past its last datum, inside the box's pad) */
});
export const spanIsBox = (sp) => !!sp && sp.form === "box";

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

/* THE TONE a span is grounded in (E99 s7 -> s46). ONE PLACE, and this is it: the `span_tone` dial names `dark`
   (SPAN.DARK under the span's own name) or `light` (the span's own colour, the chalk); anything else, and ABSENCE,
   is SPAN.TONE - and E99 s46 made that DARK. The engine hands the dial's raw value straight in, so a timeline that
   says nothing gets the ruled default and one that says `light` keeps the wash it always had. */
export const spanToneIsDark = (tone) => {
  const v = tone === null || tone === undefined || tone === "" ? SPAN.TONE : String(tone);
  return (v === "light" || v === "dark" ? v : SPAN.TONE) === "dark";
};

/* THE GROUND the shade is painted in: the dark tone darkens whatever it stands on and tints it with nothing, the
   light tone is the span's own colour. The NAME never comes here - it keeps `col` either way (E99 s7: the shade and
   its name part company), which is why the caller passes the colour in rather than the painter reaching for it. */
export const spanGround = (tone, col) => (spanToneIsDark(tone) ? SPAN.DARK : col);

/* THE SHADE'S SETTLED DEPTH for a BUILT span (E99 s7, the operator: "that light of gray makes it read washed
   out"; E99 s46, "yes" to the dark span at 0.30). A build that wants its own wash hands the number down ON the
   built span as `sd.alpha`, which the engine fills from the `span_alpha` kinetics dial; absent, the depth is the
   TONE's own law - ALPHA_DARK (0.30) for the dark ground the ruling made the default, ALPHA (0.16) for the light
   one, because chalk at 0.30 over a charcoal page is the washed-out region s7 refused. Both arrive BY NAME on `sd`,
   never as free identifiers, so `node --test` still calls the painter with no engine around it. A zero, a negative
   or a nonsense value is not a darker shade but a missing one, so it falls back to the law; 1 is an opacity's ceiling. */
export const spanAlphaOf = (sd) => {
  const a = +(sd && sd.alpha);
  if (Number.isFinite(a) && a > 0) return Math.min(1, a);
  return spanToneIsDark(sd && sd.tone) ? SPAN.ALPHA_DARK : SPAN.ALPHA;
};

/* A56 - THE STRETCH'S OWN BOX: x from..to, y the NAMED series' own min..max over it (the line's own value at an edge
   that falls between two data - the ink the eye sees there), both padded by `pad`, clipped to the chart's box. One series
   only: a box names ONE move, and another line far above it never widens it. null when an edge has left the window
   (R26-28: nothing to name, nothing drawn) or the stretch is narrower than MIN_W (two adjacent data are a bracket's).
   `labels` (spanPageLabels: the page's own direct labels, {x, y} baselines) and `fs` their size: a label standing past
   the stretch's end at the box's height pulls the box's right edge back to LABEL_GAP before its first glyph - never
   inside the stretch itself - so a box round the last move never runs into the series' own end tag. */
export const spanStretch = (entries, from, to, pad, H, labels, fs) => {
  const a = spanEdgeX(entries, from), b = spanEdgeX(entries, to);
  if (a === null || b === null) return null;
  const x0 = Math.min(a, b), x1 = Math.max(a, b);
  if (!(x1 - x0 >= SPAN.MIN_W)) return null;
  const at = (x) => {   /* the line's own y at x: a datum, or the segment that crosses x */
    for (let k = 1; k < entries.length; k++) { const p = entries[k - 1].p, q = entries[k].p;
      if (x >= p[0] && x <= q[0]) return q[0] === p[0] ? p[1] : p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0]); }
    return null;
  };
  const ys = [at(x0), at(x1)].filter((v) => v !== null);
  for (const e of entries) if (e.p[0] >= x0 && e.p[0] <= x1) ys.push(e.p[1]);
  if (!ys.length) return null;
  const d = +pad || 0, lo = Math.min(...ys) - d, hi = Math.max(...ys) + d;
  const y = Number.isFinite(H) ? Math.max(0, lo) : lo, yb = Number.isFinite(H) ? Math.min(H, hi) : hi;
  if (!(yb > y)) return null;
  let xr = x1 + d;
  const up = +fs > 0 ? +fs : 0;
  for (const L of labels || []) {   /* the label's own line: its baseline, a size of ascent above it, a third below */
    if (!L || !(L.x >= x1) || !(L.y + up / 3 >= y && L.y - up <= yb)) continue;
    xr = Math.min(xr, Math.max(x1, L.x - SPAN_BOX.LABEL_GAP));
  }
  return { x: x0 - d, y, w: xr - (x0 - d), h: yb - y };
};

/* the box's POSE at t: up from its word, the pen round it over DRAW_S, and its leave over the last LEAVE_S of `dur`
   (a box shorter than the two together still draws and leaves - it simply never stands whole). The name, if the box
   carries one, is written after the pen has gone round, over WRITE of the word, the shade's own hand. */
export const spanBoxPose = (sp, t) => {
  const at = +sp.at, dur = Math.max(0.001, +sp.dur || 1), d = t - at;
  const fade = 1 - span01((d - (dur - SPAN_BOX.LEAVE_S)) / SPAN_BOX.LEAVE_S);
  return { on: d >= 0 && fade > 0, draw: span01(d / SPAN_BOX.DRAW_S), fade: d >= 0 ? fade : 0,
           write: span01((d - SPAN_BOX.DRAW_S) / (dur * SPAN.WRITE)) };
};

/* the outline drawn ROUND BY LENGTH, from the top-left corner clockwise - the top, the right, the bottom, the left - `u`
   of its perimeter: a pen's path, not a fade, and closed (Z) once whole so the last corner joins. A pure string of t. */
export const spanBoxPath = (r, u) => {
  if (!r || !(u > 0)) return "";
  const P = [[r.x, r.y], [r.x + r.w, r.y], [r.x + r.w, r.y + r.h], [r.x, r.y + r.h], [r.x, r.y]];
  const f = (p) => p[0].toFixed(1) + " " + p[1].toFixed(1);
  let left = Math.min(1, u) * 2 * (r.w + r.h), d = "M" + f(P[0]);
  for (let k = 1; k < P.length && left > 1e-9; k++) {
    const a = P[k - 1], b = P[k], len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (left >= len - 1e-9) { d += " L" + f(b); left -= len; continue; }
    const s = left / len; d += " L" + f([a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s]); left = 0;
  }
  return u >= 1 ? d + " Z" : d;
};

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

/* A56 - THE BOX'S PAINTER. Ink ON the page, in the perform layer the builder put it in - never sunk to the ground as a
   shade is, and the shade's rect stays empty. Re-read on the live points every frame, so a box follows a re-fit and
   hides with an edge the window drops. A name, if the box carries one, stands over the box's own top. */
export const paintSpanBox = (sd, t, st, ctx) => {
  const pose = spanBoxPose(sd.sp, t);
  sd.rect.setAttribute("fill-opacity", 0);
  const hide = () => { if (sd.box) sd.box.setAttribute("opacity", 0); sd.label.setAttribute("opacity", 0); };
  if (!pose.on || !sd.box) { hide(); return; }
  const r = spanStretch(ctx.pointsNow(st, sd.si) || [], sd.sp.from, sd.sp.to, SPAN_BOX.PAD, (st.geom || {}).H,
                        spanPageLabels(st), sd.fs);   /* the box stops short of the series' own end tag */
  if (!r) { hide(); return; }   /* R26-28: an edge the window dropped names nothing */
  sd.box.setAttribute("d", spanBoxPath(r, pose.draw));
  sd.box.setAttribute("opacity", pose.fade.toFixed(3));
  if (!sd.lg.length) { sd.label.setAttribute("opacity", 0); return; }
  sd.label.setAttribute("opacity", pose.fade.toFixed(3));
  sd.label.setAttribute("x", (r.x + r.w / 2).toFixed(1));
  sd.label.setAttribute("y", spanLabelY({ yTop: r.y, y: r.y }, sd.fs).toFixed(1));
  sd.lg.forEach((ts, j) => ts.setAttribute("opacity", spanGlyph(pose.write, j, sd.lg.length).toFixed(3)));
};

/* THE PAINTER (P52 T5; R26-41). The band re-read on the LIVE scale every frame, the shade fading in under the
   lines, the name written above it by the hand - every number of it is the law above; this is the DOM.
   `sd` is the perform layer's built span (rect, label, the label's glyphs `lg`, its size `fs`, the series `si`
   and the declaration `sp`), `st` the page state, and `ctx` the PAGE species context the engine hands every page
   painter (see PAGE_PAINTERS in the engine): the engine's helpers arrive BY NAME - `pointsNow` is the perform
   layer's lpPointsNow - never as a free identifier, so `node --test` can call this with recorders and no DOM. */
export const paintSpan = (sd, t, st, ctx) => {
  if (spanIsBox(sd.sp)) { paintSpanBox(sd, t, st, ctx); return; }   /* P72 T46g (R26-407): the box form, A56 */
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
  sd.rect.setAttribute("fill-opacity", (spanAlphaOf(sd) * pose.shade).toFixed(3));   /* E99 s7: the SETTLED depth is the build's (span_alpha) or the law's; the fade-in is the pose's either way */
  sd.label.setAttribute("opacity", 1);
  sd.label.setAttribute("x", band.cx.toFixed(1));
  sd.label.setAttribute("y", spanLabelY(band, sd.fs).toFixed(1));
  sd.lg.forEach((ts, j) => ts.setAttribute("opacity", spanGlyph(pose.write, j, sd.lg.length).toFixed(3)));
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment,
   so inlining keeps it and node - where no registry exists - still imports the file for the math. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.span = paintSpan;
