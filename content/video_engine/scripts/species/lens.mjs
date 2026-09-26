/* SPACE: page */
/* species/lens.mjs - THE LENS (P71 T32, was P69 T80; the Bravos harvest v2's A57 "magnifier lens over the chart", n=2 -
   STK 4AkB4c0tTfU 9:16-9:18, BOOM jx3Ll-GJtMY 06:28). SOURCE OF TRUTH, inlined into the scene-evidence player by
   sync_kinetics.py between KINETICS:BEGIN lens and KINETICS:END, AFTER ease, span and lit_stretch (it reads minJerk, the
   span's active state and the lit stretch's stretch law). Its region sits with the page species, before paintPerform
   closes over it.

   WHEN (`SPECIES_WHEN["lens"]`, build_scene_timeline_f.py; BRAVOS-USE-WHEN.md A57): "a small region of a long line must be
   read without losing the rest"; don't: "invent zoomed values".

   WHAT BRAVOS DOES, MEASURED (E38; scratchpad p71-t32 NOTES): a magnifier GLASS - a grey ring on a crimson handle - rises
   from below onto the line (STK 555.75 s), TRAVELS the stretch the sentence names (the dashed fall, 556.0-558.0) and
   leaves to the right (558.0-558.3). Inside the ring the line is the page's own line at the same scale: mapped about the
   glass's centre, k = 1.0 explains 84 % of the ink inside the ring (k 0.9 / 1.1: 33 % / 29 %). So the glass POINTS; the
   magnification is ours, and it is the AUTHOR'S dial (`zoom`, default LENS.ZOOM = 1, Bravos's).

   THE LAW, a pure function of t:
     the pose   - up on `at`; it rises over IN_S from RISE_K radii below its stand, travels over the middle of the word,
                  and leaves over OUT_S, EXIT_K radii to the right (the lit stretch's min-jerk clock, the same ease).
     the stand  - the glass's centre is ON the named series: the datum `from`, or - with a `to` - the head of the stretch
                  from -> to at the travel's share of its LENGTH (the lit stretch's own law, litStretchPts / litCut, so a
                  rescale moves the glass with the data and an edge the window dropped hides it).
     inside     - every DRAWN series of the page, redrawn at `zoom` about the glass's centre c: p' = c + zoom (p - c) - the
                  page's OWN points (lpPointsNow), each one a datum; the vertices stop at the last one the pen has drawn
                  (never an interpolated edge), and the ring clips them. Nothing is resampled between two data: a
                  magnified segment is the same straight segment the page draws, longer. No value is invented.
     the ground - a disc of the plot's own ground under the magnified ink, so the page's line beneath does not double it.
   The look is the reference's (STK 557.5, 1280 px): ring outer R 86.5 px (0.0676 of the width -> R_PX 130 stage px),
   its stroke 11 px (RING_K 0.127 R), a grey neck 19 px (NECK_K), a crimson handle 43 x 107 px (HANDLE_K) straight down. */
import { minJerk } from "../kinetics/ease.mjs";
import { spanActiveState } from "./span.mjs";
import { litStretchPts, litLength, litCut, litDrawnX, litPathD } from "./lit_stretch.mjs";

export const LENS = Object.freeze({
  R_PX: 130,               /* the ring's outer radius, stage px (STK 557.5: 86.5 of 1280 px) */
  RING_K: 0.127,           /* the ring's stroke, a share of R (11 of 86.5 px) */
  NECK_K: [0.36, 0.22],    /* the grey neck under the ring: width, height as shares of R (19 px tall) */
  HANDLE_K: [0.5, 1.24],   /* the crimson handle: width, length as shares of R (43 x 107 px) - straight down, as STK's */
  RING_INK: "#6E747C",     /* rgb(110, 116, 124), measured */
  HANDLE_INK: "#C91D3C",   /* rgb(201, 29, 60), measured */
  IN_S: 0.25,              /* the glass rises onto the line (STK 555.75 -> 556.0) */
  OUT_S: 0.3,              /* ... and leaves (558.0 -> 558.3) */
  EDGE_MAX: 0.3,           /* a short word: the rise and the leave each take at most this share of it */
  RISE_K: 1.2,             /* it rises from this many radii below its stand */
  EXIT_K: 1.6,             /* it leaves this many radii to the right (STK exits right) */
  ZOOM: 1,                 /* the default magnification: Bravos's glass, measured, magnifies nothing */
  ZOOM_MAX: 4,             /* the compiler's ceiling (LENS_ZOOM_MAX), mirrored as a clamp */
  REACH_K: 1.25,           /* the magnified ink keeps the data within this many (R / zoom) of the centre, and one past each edge */
});

const lens01 = (v) => Math.min(1, Math.max(0, v));

/* the author's zoom, clamped to the grammar's range (the compiler refuses the rest by name) */
export const lensZoom = (sp) => Math.min(LENS.ZOOM_MAX, Math.max(1, Number.isFinite(+sp.zoom) && +sp.zoom > 0 ? +sp.zoom : LENS.ZOOM));

/* THE POSE at t: up, how far along its stretch (0..1, eased), its alpha, and the rise / leave shares (0..1) */
export const lensPose = (sp, t) => {
  const at = +sp.at, dur = Math.max(0.001, +sp.dur || 1), d = t - at;
  if (!(d >= 0) || d > dur) return { on: false, u: 0, a: 0, rise: 1, exit: 0 };
  const inS = Math.min(LENS.IN_S, dur * LENS.EDGE_MAX), outS = Math.min(LENS.OUT_S, dur * LENS.EDGE_MAX);
  const ai = minJerk(lens01(d / inS)), ao = d <= dur - outS ? 0 : minJerk(lens01((d - (dur - outS)) / outS));
  const u = lens01(minJerk(lens01((d - inS) / Math.max(0.001, dur - inS - outS))));
  return { on: true, u, a: lens01(ai * (1 - ao)), rise: 1 - ai, exit: ao };
};

/* THE STAND: the glass's centre on the series - the datum `from`, or the head of the stretch from -> to at share u of its
   length. `entries` is lpPointsNow's shape, [{i, p: [x, y]}] in index order. null: the page does not have it now. */
export const lensStand = (entries, from, to, u) => {
  if (to === undefined || to === null) {
    const q = (entries || []).find((e) => e.i === from);
    return q ? [q.p[0], q.p[1]] : null;
  }
  const full = litStretchPts(entries, from, to);
  if (!full) return null;
  const head = litCut(full, lens01(u) * litLength(full));
  const h = head[head.length - 1];
  return [h[0], h[1]];
};

/* INSIDE THE GLASS: the series' own data near the centre c (by x: within `reach`, plus one datum past each edge so the
   line runs out of the ring), no datum past the pen (`xMax`, null = all drawn), each mapped c + k (p - c). The result's
   every vertex IS a datum of the page, magnified. null when nothing of the series is near the glass. */
export const lensMagnify = (entries, c, k, reach, xMax) => {
  const E = (entries || []).filter((q) => xMax === null || xMax === undefined || q.p[0] <= xMax + 1e-6);
  let lo = -1, hi = -1;
  for (let j = 0; j < E.length; j++) {
    const x = E[j].p[0];
    if (lo < 0 && x >= c[0] - reach) lo = j;
    if (x <= c[0] + reach) hi = j;
  }
  if (lo < 0 || hi < 0) return null;
  lo = Math.max(0, lo - 1); hi = Math.min(E.length - 1, hi + 1);
  if (hi <= lo) return null;
  return E.slice(lo, hi + 1).map((q) => [c[0] + k * (q.p[0] - c[0]), c[1] + k * (q.p[1] - c[1])]);
};

/* the glass's parts about its centre c at outer radius R (chart units): the clip and ground radius, the ring's circle
   and stroke, the neck's and the handle's rectangles (straight down) */
export const lensParts = (c, R) => {
  const sw = R * LENS.RING_K, inner = R - sw, nw = R * LENS.NECK_K[0], nh = R * LENS.NECK_K[1];
  const hw = R * LENS.HANDLE_K[0], hl = R * LENS.HANDLE_K[1];
  return { inner, ringR: R - sw / 2, sw,
           neck: { x: c[0] - nw / 2, y: c[1] + R - sw * 0.25, w: nw, h: nh },
           handle: { x: c[0] - hw / 2, y: c[1] + R - sw * 0.25 + nh, w: hw, h: hl, rx: hw / 2 } };
};

const setAll = (el, o) => { for (const k of Object.keys(o)) el.setAttribute(k, typeof o[k] === "number" ? o[k].toFixed(2) : o[k]); };

/* THE PAINTER (P71 T32). `ld` is the perform layer's built lens (`g`, the `clip` and `disc` circles, the `ring`, the
   `neck` and `handle` rects, the magnified `lines` [{si, path}], the series `si`, the declaration `sp`, its `zoom` and
   its outer radius `r` in chart units); `st` the page state; `ctx` the PAGE species context (`pointsNow`), handed in by
   name, so `node --test` calls this with recorders and no DOM. */
export const paintLens = (ld, t, st, ctx) => {
  const pose = lensPose(ld.sp, t);
  const hide = () => ld.g.setAttribute("opacity", 0);
  if (!pose.on || pose.a <= 0) { hide(); return; }
  const stand = lensStand(ctx.pointsNow(st, ld.si), ld.sp.from, ld.sp.to, pose.u);
  if (!stand) { hide(); return; }   /* R26-28: a datum the window dropped - the glass stands on nothing, so it is not up */
  const R = ld.r, c = [stand[0] + pose.exit * LENS.EXIT_K * R, stand[1] + pose.rise * LENS.RISE_K * R];
  const P = lensParts(c, R);
  setAll(ld.clip, { cx: c[0], cy: c[1], r: P.inner });
  setAll(ld.disc, { cx: c[0], cy: c[1], r: P.inner });
  setAll(ld.ring, { cx: c[0], cy: c[1], r: P.ringR, "stroke-width": P.sw });
  setAll(ld.neck, { x: P.neck.x, y: P.neck.y, width: P.neck.w, height: P.neck.h });
  setAll(ld.handle, { x: P.handle.x, y: P.handle.y, width: P.handle.w, height: P.handle.h, rx: P.handle.rx });
  const S = spanActiveState(st), paths = (S && S.paths) || [];
  for (const ln of ld.lines) {
    const m = lensMagnify(ctx.pointsNow(st, ln.si), c, ld.zoom, (R * LENS.REACH_K) / ld.zoom, litDrawnX(paths, ln.si));
    ln.path.setAttribute("d", m ? litPathD(m) : "");
  }
  ld.g.setAttribute("opacity", pose.a.toFixed(3));
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.lens = paintLens;
