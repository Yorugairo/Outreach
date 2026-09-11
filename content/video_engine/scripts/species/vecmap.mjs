/* species/vecmap.mjs - THE VECTOR MAP (P50 T5; the Bravos world map, shots 57-80: Iran lights, an arc leaves
   the Gulf and crosses to the US, "1996" stamps, China lights and takes "1.4 Billion Barrels"). SOURCE OF
   TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN vecmap and
   KINETICS:END, AFTER spring, idle, clothoid and chip - it imports all four, and the import order IS the
   region order.

   TWO THINGS LIVE HERE, and the template's world branch is three lines because of it:
     THE WORLD - `world.kind === "vecmap"`: 177 country outlines (assets/maps/world-110m.paths.json, Natural
                 Earth 110m, public domain) drawn in the MUTED INK on the stage's own dark ground, the focus
                 set's outlines a shade stronger. The register is the CHARCOAL one (doc 29 s9.28: a world is
                 the stage's ground, species over it) - the cream is the ledger PAGE's register, and a page is
                 a document, not a stage. The projection is the map's own: the file is already equirectangular
                 on a 1000 x 500 box, so the player's whole job is ONE SIMILARITY per composition (mapFit) -
                 never a stretch, which would lie about distances.
     THE SPECIES - `light` (a country's fill rises to the accent and holds, breathing on its idle: the
                 spotlight's cousin, a FILL, never a ring - E56), `arc` (a clothoid from one centroid to
                 another, drawn by length with the nib, an X at its midpoint when the flow is CUT) and
                 `stamp` (a figure, or a year at the smaller size, written at a centroid or a declared point).

   THE FRAME. Every one of them paints in the SAME coordinates - the map box through `fit` - and then rides
   the SAME two transforms as the world beneath it: the scene's CAMERA (screen = at + s (p - look), exactly
   camCssFor's mapping, because the world is a div carrying that CSS and a species is an svg group that is
   not) and the world's IDLE (E49: the map holds at its breath, never dead still). vmGroupXf builds both from
   one place, so a light cannot drift off its country while the camera moves between focal points (E59 reason
   2: one move per composition, then still).
   Nothing is stored: every visual reads from t and the declaration, so a scrubbed frame is the played frame.
   The outlines are SOURCED data, never invented geometry. The dials below are ours to tune (42 s42.5). */
import { springPop } from "../kinetics/spring.mjs";
import { idleXf } from "../kinetics/idle.mjs";
import { clothoid, clothoidPath } from "../kinetics/clothoid.mjs";
import { chipStrokes } from "./chip.mjs";

export const VECMAP = Object.freeze({
  MARGIN: 0.055,     /* the air around the framed box, as a share of the stage's SHORT side - the map never touches the frame */
  PAD: 18,           /* ... plus this much air in MAP units around the focus set's own box, so a lit country is never cut by the margin */
  ZOOM_MAX: 4.2,     /* the most the fit may magnify the 1000 x 500 box: past it one country is a blob and the rest of the world is off screen */
  IDLE: "breath",    /* the world's idle when the row names none (the template's IDLE_CLASS.plate, named here so the species agree with it) */
});

export const LIGHT = Object.freeze({
  IN_S: 0.3,         /* the plan's number: the country's fill rises to the accent over this and HOLDS (dur 'hold' resolves in the compiler, as the spotlight's does) */
  OUT_S: 0.35,       /* ... and leaves a touch slower than it arrived, so the last frame of a sentence is not a blink */
  MAX: 0.78,         /* the lit fill's opacity: the accent reads as a light ON the land, never as a solid shape replacing it */
  BREATH_K: 7,       /* the idle's scale deviation (1.2 % at the breath's peak) mapped onto the FILL - a country cannot scale without leaving its outline, so its light breathes instead */
});

export const ARC = Object.freeze({
  DRAW_S: 0.9,       /* the flow crosses in this long, drawn BY LENGTH with the nib (42 s42.1) */
  BOW: 0.5,          /* the exit tangent's turn off the chord, radians: a flight path lifts, it does not hoop */
  ENTER_K: 0.45,     /* ... and the entry tangent's as a share of it. UNEQUAL, like the flow diagram's arrows: equal turns give a circular arc and waste the fitter's ramp */
  SAMPLES: 48,       /* the clothoid's polyline: dense enough that its chords hide at our sizes */
  HEAD: 26,          /* the arrowhead's stroke length in stage px ... */
  HEAD_A: 0.42,      /* ... and its half-angle in radians (the flow's arrow, so two arrows in one episode are one hand) */
  HEAD_F: 0.74,      /* ... landing over the last of the arc's own clock, after the shaft has arrived */
  CROSS_S: 0.45,     /* the X at the midpoint: two strokes, the chip's cross (chipStrokes) on a shorter clock */
  CROSS_ARM: 26,     /* ... each arm this long in stage px */
  DIM: 0.42,         /* what a CUT arc dims to: the flow was real, and then it was cut - it does not vanish */
});

export const STAMP = Object.freeze({
  IN_S: 0.45,        /* the figure lands on the badge spring (springPop), the same landing a chip and the flow's year stamp take */
  FADE_S: 0.16,      /* ... never a pop out of nothing */
  RISE: 0.5,         /* the share of its own size it falls from, so it arrives ON the place rather than beside it */
  POP_FROM: 0.72,    /* ... and the size it springs UP from (the callout label's 0.7, the chip's POP_FROM): never a pop out of nothing */
  FIGURE_PX: 46,     /* a FIGURE's type: the sentence's number, read at phone size */
  EDGE: 28,          /* ... and the stage inset it is kept inside: a figure that runs off the frame is not evidence (doc 49 s49.1) */
  CHAR_W: 0.56,      /* the estimated width of one character as a share of the size, Inter 700 - an ESTIMATE, not a measurement: the player measures nothing at paint time (a scrubbed frame is the played frame), and the only thing it buys is the clamp below */
  YEAR_PX: 32,       /* ... and a YEAR's, which is furniture: a date, not a title (the flow's TAG_SIZE, one notch down) */
  DY: -18,           /* the baseline's lift off the centroid: the figure sits ON the place, not under it */
});

export const STAMP_SIZES = Object.freeze({ figure: STAMP.FIGURE_PX, year: STAMP.YEAR_PX });

const vm01 = (v) => Math.min(1, Math.max(0, v));

/* ---------------------------------------------------------------- THE MAP

   The asset map carries the whole file under one key (`map:<name>`, 187 KB, put there once by the compiler
   however many scenes use it). Parsing 177 countries every frame would be the one expensive thing in this
   module, so the parse is memoised by the STRING ITSELF: the same asset parses once for the whole render. */
const VM_CACHE = new Map();
export const mapData = (raw) => {
  if (typeof raw !== "string" || !raw) return null;
  let d = VM_CACHE.get(raw);
  if (d === undefined) {
    try { d = JSON.parse(raw); } catch (e) { d = null; }
    if (!d || !d.countries || !Array.isArray(d.box)) d = null;
    if (VM_CACHE.size > 4) VM_CACHE.clear();
    VM_CACHE.set(raw, d);
  }
  return d;
};

/* the framed box in MAP units: the focus set's bboxes unioned and padded, or the whole map when none is named */
export const focusBox = (box, bboxes, pad = VECMAP.PAD) => {
  const bs = (bboxes || []).filter((b) => Array.isArray(b) && b.length === 4);
  if (!bs.length) return { x: 0, y: 0, w: box[0], h: box[1] };
  const x0 = Math.min(...bs.map((b) => b[0])), y0 = Math.min(...bs.map((b) => b[1]));
  const x1 = Math.max(...bs.map((b) => b[2])), y1 = Math.max(...bs.map((b) => b[3]));
  return { x: x0 - pad, y: y0 - pad, w: (x1 - x0) + 2 * pad, h: (y1 - y0) + 2 * pad };
};

/* THE FIT: ONE SIMILARITY from map units to stage px, stage = (sx * x + tx, sy * y + ty) with sx === sy.
   The framed box is CONTAINED in the stage less its margin - on 16:9 that is the whole world (or the focus
   set's box) letterboxed; on 9:16, where a focus set is always wider than it is tall, it is that box fit to
   the WIDTH. One rule, read off the geometry rather than off the aspect, exactly as the flow diagram picks
   its row or its column. ZOOM_MAX caps a focus set of one small country, which would otherwise magnify the
   world past reading. */
export const mapFit = (box, bboxes, stageW, stageH, margin = VECMAP.MARGIN) => {
  const m = margin * Math.min(stageW, stageH), f = focusBox(box, bboxes);
  const k = Math.min(VECMAP.ZOOM_MAX, (stageW - 2 * m) / Math.max(1e-6, f.w), (stageH - 2 * m) / Math.max(1e-6, f.h));
  return { sx: k, sy: k,
           tx: stageW / 2 - k * (f.x + f.w / 2),
           ty: stageH / 2 - k * (f.y + f.h / 2), box: f };
};

/* a point in MAP units -> stage px, and back: the two are each other's inverse to the bit (the fit is one
   similarity, not a projection - the projection was done once, on disk, by build_world_map.py) */
export const mapPoint = (fit, p) => ({ x: fit.sx * p[0] + fit.tx, y: fit.sy * p[1] + fit.ty });
export const mapInvert = (fit, q) => [(q.x - fit.tx) / fit.sx, (q.y - fit.ty) / fit.sy];
/* the SVG transform that puts a raw map path (its own units, untouched) on the stage */
export const fitXf = (fit) => "translate(" + fit.tx.toFixed(2) + " " + fit.ty.toFixed(2) + ") scale(" + fit.sx.toFixed(5) + ")";

/* the TARGET of a light, an arc's end or a stamp, in MAP units: a country resolves to its centroid, a
   declared map point to itself. A name that is not in the data resolves to nothing and nothing is painted -
   the compiler refuses it by name long before here (the targeting law, s9.27). */
export const vmTarget = (data, tg) => {
  if (!tg || !data) return null;
  if (tg.kind === "country") { const c = data.countries[tg.id]; return c && c.centroid ? c.centroid : null; }
  if (tg.kind === "mappoint") return [+tg.x, +tg.y];
  return null;
};

/* ---------------------------------------------------------------- THE FRAME EVERY PAINTER RIDES */

/* the world's idle transform, about the STAGE's centre - the same pose the world's own group takes, so a
   species over it never slides against the land beneath it. `kindOf` is the player's idleOf (which carries
   the kinetics flag and the class default); node passes its own. */
export const vmIdle = (scene, world, t, idle, hash, kindOf) => {
  const kind = kindOf ? kindOf("plate", (world || {}).idle) : ((world || {}).idle || VECMAP.IDLE);
  if (!kind || kind === "none") return { scale: 1, dx: 0, dy: 0 };
  const span = (scene && scene.span) ? scene.span[0] : 0;
  return (idle || idleXf)(kind, t, (hash || (() => 0))(Math.round(span * 100), 0, 977));
};

/* the two transforms as ONE string, in the order the world applies them: the camera's
   screen = at + s (p - look) (camCssFor's mapping, so the species and the div agree to the pixel), then the
   idle about the stage's centre. Either one absent is the identity and writes nothing. */
export const vmGroupXf = (cam, ix, stageW, stageH) => {
  let out = "";
  if (cam && (cam.s !== 1 || cam.ax !== cam.ox || cam.ay !== cam.oy)) {
    const s = cam.s, ax = cam.ax == null ? cam.ox : cam.ax, ay = cam.ay == null ? cam.oy : cam.ay;
    out += "translate(" + (ax - s * cam.ox).toFixed(2) + " " + (ay - s * cam.oy).toFixed(2) + ") scale(" + s.toFixed(5) + ") ";
  }
  if (ix && (ix.scale !== 1 || ix.dx !== 0 || ix.dy !== 0)) {
    const cx = stageW / 2, cy = stageH / 2;
    out += "translate(" + (cx + ix.dx).toFixed(2) + " " + (cy + ix.dy).toFixed(2) + ") scale(" + ix.scale.toFixed(5)
         + ") translate(" + (-cx).toFixed(2) + " " + (-cy).toFixed(2) + ") ";
  }
  return out.trim();
};

/* ---------------------------------------------------------------- THE LAWS, each a pure function of t */

/* THE LIGHT at t: 0 before its word, up to MAX over IN_S, held for its window, out over OUT_S. The idle
   breathes the FILL, not the shape - a country that scaled would leave its own outline behind. */
export const lightAlpha = (t, at, dur, ixScale = 1) => {
  const d = t - at;
  if (d < 0 || d > dur) return 0;
  const up = vm01(d / LIGHT.IN_S), down = vm01((at + dur - t) / LIGHT.OUT_S);
  return LIGHT.MAX * Math.min(up, down) * (1 + (ixScale - 1) * LIGHT.BREATH_K);
};

/* THE ARC at t: how much of it is drawn (0..1), how far its X has been struck, and what it has dimmed to. */
export const arcFrac = (sp, t) => vm01((t - +sp.at) / ARC.DRAW_S);
export const arcCrossF = (sp, t) => (Number.isFinite(+sp.crossed) ? vm01((t - +sp.crossed) / ARC.CROSS_S) : 0);
export const arcDim = (f) => 1 - (1 - ARC.DIM) * f;

/* THE ARC's geometry in STAGE px: a clothoid (kinetics/clothoid.mjs, 42 s42.4) from one centroid to the
   other, its two tangents turned UNEQUALLY off the chord so the pen ramps out of one place and settles into
   the next. The bow lifts toward the POLE the two places share - a Gulf -> US arc rises over the Atlantic
   rather than sagging into it.
   WHICH WAY THAT IS depends on where the arc is GOING, not only on which hemisphere it is in (read in the
   frame, 2026-09-11: a westward flow bowed with a fixed sign sagged into the Atlantic). Leaving at the
   heading th + s * BOW veers to the side whose y-component is s * cos(th), so for a lift of sign w (-1 in
   the north, +1 in the south) the turn is s = w * sign(dx): eastward and westward arcs take opposite signs
   and both rise. A chord with no x-run has no lift to give and keeps w. */
export const arcBowSign = (box, a, b) => {
  const w = ((a[1] + b[1]) / 2) < box[1] / 2 ? -1 : 1;
  return b[0] - a[0] >= 0 ? w : -w;
};

export const arcPath = (fit, from, to, bow = ARC.BOW, sign = -1) => {
  const p0 = mapPoint(fit, from), p1 = mapPoint(fit, to);
  const chord = Math.atan2(p1.y - p0.y, p1.x - p0.x);
  const t0 = chord + sign * bow, t1 = chord - sign * bow * ARC.ENTER_K;
  const pts = clothoid(p0, t0, p1, t1, ARC.SAMPLES);
  return { pts, d: clothoidPath(pts), p0, p1, mid: pts[pts.length >> 1] };
};

/* the arrowhead's two strokes at the far end, along the tangent it arrives on (the flow diagram's head) */
export const arcHead = (pts) => {
  const n = pts.length;
  if (n < 2) return "";
  const tip = pts[n - 1], prev = pts[n - 2], th = Math.atan2(tip.y - prev.y, tip.x - prev.x);
  const arm = (s) => ({ x: tip.x - ARC.HEAD * Math.cos(th + s * ARC.HEAD_A), y: tip.y - ARC.HEAD * Math.sin(th + s * ARC.HEAD_A) });
  const l = arm(1), r = arm(-1);
  return "M" + l.x.toFixed(2) + " " + l.y.toFixed(2) + " L" + tip.x.toFixed(2) + " " + tip.y.toFixed(2)
       + " L" + r.x.toFixed(2) + " " + r.y.toFixed(2);
};

/* the X at a cut arc's midpoint: the chip's two-stroke cross, on the arc's own clock */
export const arcCrossPaths = (mid, arm = ARC.CROSS_ARM) =>
  ["M" + (mid.x - arm).toFixed(1) + " " + (mid.y - arm).toFixed(1) + " L" + (mid.x + arm).toFixed(1) + " " + (mid.y + arm).toFixed(1),
   "M" + (mid.x + arm).toFixed(1) + " " + (mid.y - arm).toFixed(1) + " L" + (mid.x - arm).toFixed(1) + " " + (mid.y + arm).toFixed(1)];

/* THE STAMP at t: the badge spring's landing, its fade and the size its `size` field names. The page's own
   figure law (the hand writing at a datum) is NOT reachable from here - it is a mask wipe over .lp-ink spans
   inside the ledger page's DOM, and this overlay is an svg on the stage - so a stamp lands the way the flow
   diagram's year stamp and the callout's label land: the type popping on springPop. Said plainly because the
   two are different hands, and a cut that wants the written figure wants a ledger page under it. */
export const stampPose = (sp, t) => {
  const u = vm01((t - +sp.at) / STAMP.IN_S), e = springPop(u), px = STAMP_SIZES[sp.size] || STAMP.FIGURE_PX;
  return { u, px, fade: vm01((t - +sp.at) / STAMP.FADE_S), dy: STAMP.DY + px * STAMP.RISE * (1 - e),
           scale: STAMP.POP_FROM + (1 - STAMP.POP_FROM) * e };
};

/* the stamp's place in STAGE px: the centroid (or the declared point), lifted off it by the pose */
export const stampAt = (fit, p) => mapPoint(fit, p);

/* a point through the SAME two transforms vmGroupXf writes, as numbers: the idle about the stage's centre,
   then the camera (screen = at + s (p - look)). The string is for geometry that rides the map; this is for
   the one thing that must NOT - the type. */
export const vmScreen = (cam, ix, p, stageW, stageH) => {
  let x = p.x, y = p.y;
  if (ix) { const cx = stageW / 2, cy = stageH / 2; x = cx + ix.dx + (x - cx) * ix.scale; y = cy + ix.dy + (y - cy) * ix.scale; }
  if (cam) { const ax = cam.ax == null ? cam.ox : cam.ax, ay = cam.ay == null ? cam.oy : cam.ay;
             x = ax + cam.s * (x - cam.ox); y = ay + cam.s * (y - cam.oy); }
  return { x, y };
};

/* ... and the type kept ON the stage. A centroid near the frame's edge (China's, on a 9:16 stage framing
   three continents - read in the frame, 2026-09-11) put half the figure outside it. The anchor is pushed in
   by the text's estimated half width; a figure wider than the stage stays centred and the author is the one
   who wrote too long a number. */
export const stampClamp = (q, text, px, stageW, stageH) => {
  const half = String(text || "").length * px * STAMP.CHAR_W / 2, m = STAMP.EDGE;
  const lo = m + half, hi = stageW - m - half;
  return { x: lo > hi ? stageW / 2 : Math.min(Math.max(q.x, lo), hi),
           y: Math.min(Math.max(q.y, m + px), stageH - m) };
};

/* ---------------------------------------------------------------- THE PAINTERS */

/* the fit this composition uses, from the world's own declaration - the one place the world branch and the
   three species agree, so they cannot disagree about where a country is */
export const worldFit = (data, world, stageW, stageH) => {
  if (!data) return null;
  const ids = (world && world.focus) || [];
  return mapFit(data.box, ids.map((id) => (data.countries[id] || {}).bbox).filter(Boolean), stageW, stageH);
};

/* THE WORLD (the template's branch is: mount an svg, call this). Every country's paths drawn once in the
   muted ink, the focus set's a shade stronger (the classes carry the register; this file carries no colour),
   the whole thing riding the world's idle so the map is never a still image. */
export function paintVecmapWorld(ctx) {
  const { el, scene, world, t, A, root, idle, hash, idleOf, STAGE_W, STAGE_H } = ctx;
  const data = mapData(A ? A["map:" + (world.map || "world-110m")] : null);
  root.replaceChildren();
  if (!data) return null;
  const fit = worldFit(data, world, STAGE_W, STAGE_H);
  const ix = vmIdle(scene, world, t, idle, hash, idleOf);
  const g = el("g", "", root, { transform: vmGroupXf(null, ix, STAGE_W, STAGE_H) });
  const inner = el("g", "vmland", g, { transform: fitXf(fit) });
  const focus = new Set(world.focus || []);
  for (const id of Object.keys(data.countries)) {
    const c = data.countries[id];
    for (const d of c.paths || []) el("path", focus.has(id) ? "vmc vmfocus" : "vmc", inner, { d });
  }
  return fit;
}

/* the frame a species paints in: the camera, the world's idle, and the fit the world used */
const vmFrame = (ctx) => {
  const { sc, t, A, camNow, idle, hash, idleOf, STAGE_W, STAGE_H } = ctx;
  const world = (sc && sc.world) || {};
  const data = mapData(A ? A["map:" + (world.map || "world-110m")] : null);
  if (!data) return null;
  const fit = worldFit(data, world, STAGE_W, STAGE_H);
  const ix = vmIdle(sc, world, t, idle, hash, idleOf);
  const cam = camNow ? camNow(sc, t) : null;
  return { data, fit, ix, cam, xf: vmGroupXf(cam, ix, STAGE_W, STAGE_H) };
};

/* THE LIGHT: the country's own outline filled to the accent (E56 - a picture's focus is a LIGHT; the
   spotlight's cousin, never a ring), rising over IN_S and holding, its fill breathing on the idle. */
export function paintLight(ctx) {
  const { sp, t, svg, el, idle, hash, seed, si } = ctx;
  const F = vmFrame(ctx); if (!F) return;
  const c = F.data.countries[(sp.target || {}).id]; if (!c) return;
  /* the light's own breath, declared on the species exactly as the spotlight and the chip declare theirs
     (E49; the same seeded phase, salt 991) - the WORLD's idle above moves the map, this one moves the
     light, and a lit country is alive even where the map itself is declared still. */
  const lx = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 991)) : { scale: 1, dx: 0, dy: 0 };
  const a = lightAlpha(t, +sp.at, +sp.dur, lx.scale);
  if (a <= 0) return;
  const g = el("g", "", svg, { transform: F.xf });
  const inner = el("g", "", g, { transform: fitXf(F.fit), "fill-opacity": a.toFixed(3) });
  for (const d of c.paths || []) el("path", "vmlit", inner, { d });
}

/* THE ARC: the clothoid drawn by length with the nib from one centroid to the other, the head landing last,
   an X struck at its midpoint on `crossed` and the whole flow dimming under it. */
export function paintArc(ctx) {
  const { sp, t, svg, el, drawOn } = ctx;
  const F = vmFrame(ctx); if (!F) return;
  const from = vmTarget(F.data, sp.from), to = vmTarget(F.data, sp.to);
  if (!from || !to) return;
  const f = arcFrac(sp, t); if (f <= 0) return;
  const arc = arcPath(F.fit, from, to, ARC.BOW, arcBowSign(F.data.box, from, to));
  const cross = arcCrossF(sp, t);
  const g = el("g", "", svg, { transform: F.xf, opacity: arcDim(cross).toFixed(3) });
  drawOn(el("path", "vmarc", g, { d: arc.d }), Math.min(1, f / ARC.HEAD_F));
  if (f > ARC.HEAD_F) drawOn(el("path", "vmarc", g, { d: arcHead(arc.pts) }), (f - ARC.HEAD_F) / (1 - ARC.HEAD_F));
  if (cross > 0) {
    const strokes = chipStrokes(cross), paths = arcCrossPaths(arc.mid);
    const x = el("g", "", svg, { transform: F.xf });   /* the X is struck ON the arc and does not dim with it */
    paths.forEach((d, i) => { if (strokes[i] > 0) drawOn(el("path", "vmx", x, { d }), strokes[i]); });
  }
}

/* THE STAMP: the figure (or the year, at the smaller size) landing on the badge spring at the place it
   belongs to - a country's centroid, or a declared point on the map. */
export function paintStamp(ctx) {
  const { sp, t, svg, el, STAGE_W, STAGE_H } = ctx;
  const F = vmFrame(ctx); if (!F) return;
  const p = vmTarget(F.data, sp.target); if (!p) return;
  const pose = stampPose(sp, t); if (pose.fade <= 0) return;
  /* the place goes through the map's frame; the TYPE does not - it is drawn in plain stage px at its own
     size, so a camera zoom moves the figure with its place and never magnifies the number (doc 50's type
     floors are stage px), and the clamp above keeps it on the frame. */
  const q = stampClamp(vmScreen(F.cam, F.ix, stampAt(F.fit, p), STAGE_W, STAGE_H), sp.text, pose.px, STAGE_W, STAGE_H);
  const y = q.y + pose.dy;
  const tx = el("text", "vmstamp", svg, { x: q.x.toFixed(1), y: y.toFixed(1), opacity: pose.fade.toFixed(3),
                                          style: "font-size:" + pose.px + "px",
                                          transform: "translate(" + q.x.toFixed(1) + " " + y.toFixed(1) + ") scale(" + pose.scale.toFixed(4)
                                                   + ") translate(" + (-q.x).toFixed(1) + " " + (-y).toFixed(1) + ")" });
  tx.textContent = sp.text || "";
}

/* the module rule's registration: plain assignments (inline_text keeps them), guarded so `node --test` can
   import this file for the math above without the template's registry */
if (typeof SPECIES_PAINTERS !== "undefined") {
  SPECIES_PAINTERS.light = paintLight;
  SPECIES_PAINTERS.arc = paintArc;
  SPECIES_PAINTERS.stamp = paintStamp;
}
