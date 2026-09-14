/* kinetics/contour.mjs - THE CONTOUR (P57 T12c; BACKLOG R26-70; E76 s5). SOURCE OF TRUTH, inlined into the
   scene-evidence player by sync_kinetics.py between KINETICS:BEGIN contour and KINETICS:END, AFTER arap - it
   imports arap.mjs's shoelace area and area centroid, and the import order IS the region order. Its region sits
   beside morph_a's, because it exists to FEED morph_a: rings in, a morph out.

   WHY IT EXISTS - the operator, 2026-09-14 (E76 s5): *"the entire point of having our math and engine is that even
   for complex/difficult things we should be able to create solutions. it's just math."* P57 T12 had refused the
   glyph-outline morph on the grounds that an SVG <text> has no outlines to resample and a font-to-path library
   would be a second type engine. Both halves of that were wrong: the outlines do not have to be FETCHED from the
   font, they can be MEASURED off the ink the page already draws. Draw the text once on an offscreen canvas at a
   working scale, threshold its alpha, and walk the 0.5 level with MARCHING SQUARES: the rings that come back are
   the glyphs, to a fraction of a page pixel, in the page's own face, at the page's own size and weight. No font
   file is parsed and no second type engine stands beside the browser's.

   BITMAP IN, RINGS OUT - and nothing else. This module knows nothing of canvases, glyphs, figures or morphs:
     contourBitmap(alpha, w, h, level, stride, offset)  a typed array of samples -> { w, h, data } of 0/1
     contourRings(bmp)                                  the bitmap -> closed rings, each with its hole/parent
     simplifyRing(pts, tol)                             Douglas-Peucker on a CLOSED ring
     pointInRing(p, ring)                               the even-odd crossing test the parenting is built on

   SAMPLE SPACE: a ring's coordinates are in SAMPLE space - sample (i, j) is the CENTRE of bitmap pixel (i, j), so a
   solid 3x3 block of pixels at (1..3, 1..3) comes back as the square (0.5, 0.5) - (3.5, 3.5), area 9. The grid is
   padded with one ring of zero samples before the walk, so ink that touches the bitmap's edge still closes.

   THE AMBIGUOUS SADDLE, stated. Each cell's four corners give a 4-bit code; twelve of the sixteen cases carry one
   segment and are unambiguous. The two SADDLES - code 5 (the top-right and bottom-left corners are ink) and code 10
   (the top-left and bottom-right are) - carry two segments, and which two is a choice about topology, not about
   geometry: either the two ink corners are joined through the cell's centre or the two background corners are.
   THE RULE HERE: THE FOREGROUND IS 8-CONNECTED (and therefore the background is 4-connected). The two segments cut
   the two BACKGROUND corners off, and the ink runs through the middle - so code 5 emits L-T and B-R, code 10 emits
   T-R and L-B. A glyph is one connected stroke of ink and the paper around it is one connected field; the other
   choice splits a hairline join - the thin waist of an "8" at a small raster - into two rings that the morph would
   then have to pair as two glyphs. Chosen once, here, so every caller gets the same rings from the same bitmap.

   EVERY RING IS CLOSED and wound so its shoelace area is POSITIVE; `hole` and `parent` carry the topology instead
   of the winding, because a caller that fills with even-odd does not care about winding and a caller that fills
   with nonzero (species/compare.mjs does) reverses the holes itself, at the moment it emits them. All of it is a
   pure function of the bitmap: the same samples give the same rings, vertex for vertex, so a cold seek that
   re-rasterises lands exactly where a play did.
   The dials below are ours to tune (42 s42.5), not findings. */
import { polyArea, centroid } from "./arap.mjs";

export const CONTOUR = Object.freeze({
  EPS: 1e-9,      /* a degenerate segment: two ring vertices closer than this are one vertex */
  LEVEL: 0.5,     /* the threshold a sample is ink AT or above, as a share of the sample's full value */
});

/* ---- the bitmap --------------------------------------------------------------------------------------------- */
/* A typed array of samples (canvas RGBA's alpha channel: stride 4, offset 3) thresholded at `level` of `max` into
   a bitmap of 0 and 1. `w * h` samples are read in row-major order, the order a canvas hands them back. */
export const contourBitmap = (src, w, h, level = CONTOUR.LEVEL, stride = 4, offset = 3, max = 255) => {
  const W = Math.max(0, w | 0), H = Math.max(0, h | 0), cut = Math.max(0, Math.min(1, +level)) * max;
  const data = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) data[i] = src[i * stride + offset] >= cut ? 1 : 0;
  return { w: W, h: H, data };
};

/* ---- the walk ----------------------------------------------------------------------------------------------- */
/* the padded sample: (x, y) runs over [0, w + 1] x [0, h + 1] and everything outside the bitmap is paper */
const cSample = (bmp, x, y) =>
  (x <= 0 || y <= 0 || x > bmp.w || y > bmp.h) ? 0 : (bmp.data[(y - 1) * bmp.w + (x - 1)] ? 1 : 0);

/* the four edge midpoints of a cell whose top-left sample is (x, y), keyed on doubled coordinates so a midpoint is
   an integer key and two cells that share an edge chain through the same one */
const cMid = { T: [0.5, 0], R: [1, 0.5], B: [0.5, 1], L: [0, 0.5] };
const cKey = (x, y) => Math.round(x * 2) + "," + Math.round(y * 2);

/* THE CASE TABLE: code = tl*8 + tr*4 + br*2 + bl, the segments as pairs of edge names. The two saddles carry the
   FOREGROUND-8-CONNECTED choice stated in the header (5 -> L-T and B-R; 10 -> T-R and L-B). */
const CONTOUR_CASES = [
  [], [["L", "B"]], [["B", "R"]], [["L", "R"]],
  [["T", "R"]], [["L", "T"], ["B", "R"]], [["T", "B"]], [["L", "T"]],
  [["T", "L"]], [["T", "B"]], [["T", "R"], ["L", "B"]], [["T", "R"]],
  [["L", "R"]], [["B", "R"]], [["L", "B"]], [],
];

/* every segment the bitmap's 0.5 level carries, as pairs of midpoint keys, with the points they name */
export const contourSegments = (bmp) => {
  const segs = [], pts = new Map();
  for (let y = 0; y <= bmp.h; y++) {
    for (let x = 0; x <= bmp.w; x++) {
      const code = cSample(bmp, x, y) * 8 + cSample(bmp, x + 1, y) * 4
                 + cSample(bmp, x + 1, y + 1) * 2 + cSample(bmp, x, y + 1);
      for (const [a, b] of CONTOUR_CASES[code]) {
        const pa = [x + cMid[a][0], y + cMid[a][1]], pb = [x + cMid[b][0], y + cMid[b][1]];
        const ka = cKey(pa[0], pa[1]), kb = cKey(pb[0], pb[1]);
        pts.set(ka, pa); pts.set(kb, pb);
        segs.push([ka, kb]);
      }
    }
  }
  return { segs, pts };
};

/* the segments chained into closed rings. Every midpoint is shared by exactly two cells and each of them puts
   exactly one segment end on it, so every key has degree two and the walk is forced - no nearest-point search,
   no tolerance, and a bitmap whose rings touch at a saddle is resolved by the case table above, never here. */
export const contourWalk = (bmp) => {
  const { segs, pts } = contourSegments(bmp), at = new Map(), used = new Array(segs.length).fill(false);
  segs.forEach(([a, b], i) => {
    if (!at.has(a)) at.set(a, []);
    if (!at.has(b)) at.set(b, []);
    at.get(a).push(i); at.get(b).push(i);
  });
  const rings = [];
  for (let s = 0; s < segs.length; s++) {
    if (used[s]) continue;
    used[s] = true;
    const start = segs[s][0];
    let key = segs[s][1];
    const ring = [pts.get(start), pts.get(key)];
    while (key !== start) {
      const next = (at.get(key) || []).find((i) => !used[i]);
      if (next === undefined) break;            /* an open chain cannot happen on a padded bitmap; a broken one is not walked twice */
      used[next] = true;
      key = segs[next][0] === key ? segs[next][1] : segs[next][0];
      ring.push(pts.get(key));
    }
    if (key === start) ring.pop();               /* the walk closes on its own start: a ring is not given that vertex twice */
    if (ring.length >= 3) rings.push(ring.map((p) => [p[0] - 1, p[1] - 1]));   /* the padded grid -> sample space */
  }
  return rings;
};

/* ---- the topology ------------------------------------------------------------------------------------------- */
/* the even-odd crossing test (Franklin's), on a ring given as [x, y] pairs */
export const pointInRing = (p, ring) => {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const a = ring[i], b = ring[j];
    if ((a[1] > p[1]) !== (b[1] > p[1])
        && p[0] < (b[0] - a[0]) * (p[1] - a[1]) / ((b[1] - a[1]) || CONTOUR.EPS) + a[0]) inside = !inside;
  }
  return inside;
};

/* THE RINGS: walked, wound positive, and told apart. A ring is a HOLE when it sits inside an ODD number of the
   others (a counter island inside a hole - the dot inside a hollow "i" - is ink again), and its `parent` is the
   smallest ring that contains it. Sorted largest area first, so a parent is always found before its children. */
export const contourRings = (bmp) => {
  const walked = contourWalk(bmp).map((pts) => {
    const a = polyArea(pts);
    return { pts: a < 0 ? pts.slice().reverse() : pts, area: Math.abs(a), c: centroid(pts) };
  }).sort((p, q) => q.area - p.area);
  return walked.map((r, i) => {
    let parent = -1, depth = 0;
    for (let j = 0; j < i; j++) {
      if (!pointInRing(r.pts[0], walked[j].pts)) continue;
      depth++;
      if (parent < 0 || walked[j].area < walked[parent].area) parent = j;
    }
    return { pts: r.pts, area: r.area, c: r.c, hole: depth % 2 === 1, parent };
  });
};

/* ---- the simplify ------------------------------------------------------------------------------------------- */
/* the perpendicular distance from p to the segment ab (to a, where the segment is a point) */
const cPerp = (p, a, b) => {
  const dx = b[0] - a[0], dy = b[1] - a[1], L = dx * dx + dy * dy;
  if (L < CONTOUR.EPS) return Math.hypot(p[0] - a[0], p[1] - a[1]);
  const t = Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L));
  return Math.hypot(p[0] - (a[0] + dx * t), p[1] - (a[1] + dy * t));
};
const cDP = (pts, i, j, tol, keep) => {
  let worst = -1, at = -1;
  for (let k = i + 1; k < j; k++) { const d = cPerp(pts[k], pts[i], pts[j]); if (d > worst) { worst = d; at = k; } }
  if (worst <= tol || at < 0) return;
  keep[at] = true;
  cDP(pts, i, at, tol, keep); cDP(pts, at, j, tol, keep);
};
/* DOUGLAS-PEUCKER ON A CLOSED RING: split it at its first vertex and the vertex FARTHEST from that one - two open
   polylines that share both ends - so neither anchor of the simplification is arbitrary, and the staircase a
   threshold leaves on a raster comes off without the ring's own corners coming with it. `tol` is in the ring's
   own units, and a ring that would simplify below three vertices is handed back whole. */
export const simplifyRing = (pts, tol) => {
  const n = pts.length;
  if (n < 4 || !(tol > 0)) return pts.slice();
  let far = 0, best = -1;
  for (let i = 1; i < n; i++) {
    const d = Math.hypot(pts[i][0] - pts[0][0], pts[i][1] - pts[0][1]);
    if (d > best) { best = d; far = i; }
  }
  const keep = new Array(n).fill(false);
  keep[0] = true; keep[far] = true;
  cDP(pts, 0, far, tol, keep);
  const tail = pts.slice(far).concat([pts[0]]), tk = new Array(tail.length).fill(false);
  tk[0] = true; tk[tail.length - 1] = true;
  cDP(tail, 0, tail.length - 1, tol, tk);
  for (let k = 1; k < tail.length - 1; k++) if (tk[k]) keep[far + k] = true;
  const out = pts.filter((_p, i) => keep[i]);
  return out.length >= 3 ? out : pts.slice();
};

/* THE ONE CALL A RASTER MAKES: the rings of a bitmap, simplified and carried out of sample space by one affine
   step. `map` takes a sample point to the caller's own units (page px, viewBox units) and is applied AFTER the
   simplification, so the tolerance is always stated in the units the bitmap was measured in. */
export const contourShape = (bmp, o = {}) => {
  const tol = +o.tol || 0, map = typeof o.map === "function" ? o.map : null;
  return contourRings(bmp).map((r) => {
    const pts = simplifyRing(r.pts, tol);
    return { pts: map ? pts.map(map) : pts, hole: r.hole, parent: r.parent };
  });
};
