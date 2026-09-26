/* species/flow.mjs - THE FLOW DIAGRAM (P50 T4; the Bravos flow diagram, shots 82-86: a three-node diagram
   draws on a word, and on a LATER word one node swaps while the rest stands - the rhyme). SOURCE OF TRUTH,
   inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN flow and KINETICS:END,
   AFTER spring, idle, clothoid and chip - it imports all four, and the import order IS the region order.

   WHEN: the sentence EXPLAINS a mechanism - A causes B via C - as named things and the arrows between them;
   a later word SWAPS one node and the rest stands (Bravos's rhyme).

   THE LAW, all of it a pure function of t:
     box    - the dashed frame draws ON, dash by dash, by the curvature stroke (42 s42.1): the nib runs round
              the rectangle and leaves DASH-long marks with GAP between them, so the diagram arrives as a
              drawn thing and not as a rectangle that appeared. A dash already passed is simply there.
     nodes  - each node is a CHIP (species/chip.mjs): the same card, the same sourced glyph, the same badge
              spring, landing NODE_STEP after the one before, once the box is BOX_LEAD of the way round.
              The chip's own painter is not called - a chip resolves its own target and owns its own cross -
              but its dials (CHIP) and its landing law (chipLand) are, so a node and a lone chip land alike.
     arrows - between named nodes, one per EDGE_S after the last node lands, drawn BY LENGTH with the nib:
              a CLOTHOID (kinetics/clothoid.mjs, 42 s42.4), leaving one chip's edge on a tangent turned BOW
              off the chord and entering the next's turned BOW * ENTER_K back into it. The two turns are
              UNEQUAL on purpose: equal ones give a circular arc, and the point of the fitter is the RAMP -
              dk/ds constant, the pen accelerating out of one card and settling into the next.
     swap   - on swap.at the standing node UN-DRAWS - its own landing run backward, exactly as chart_to's
              recast runs a build law backward - and the new glyph and label draw on IN THE SAME SPOT. The
              arrows stand: the mechanism did not change, one of its parts did. ONE event at swap.at.
     tag    - a year stamp in the box's corner, written last (the diagram is dated, not captioned).
     ring   - P71 T11 (`layout: "ring"`, the Bravos loop, BUB frame_0058 / RST 9:30): the chain CLOSES on itself, so
              the n nodes stand on the ellipse inscribed in the box, the first at 12 o'clock and the rest
              clockwise, and each arrow leaves its card along the ring's own tangent - the loop reads as a
              loop, not as a polygon. Absent `layout` is the row, byte for byte.
     tokens - P71 T11 (`tokens: {from_at, n?, speed?, glyph?}`, A27 "money moving on the arrows", DOM 03:30,
              BOOM 08:19): from `from_at` n tokens ride EVERY drawn arrow by ARC LENGTH, one after another from
              its tail, at ONE speed per unit of arc across the diagram - never so fast that its shortest arrow
              is crossed in under TOKEN_MIN_CROSS_S - fading in off the tail and out into the head. A token is
              a plain DOT (A2a: never a generated coin), but a dot that reads as a THING riding the arrow, not
              a joint in it: a chalk core, the arrow's ink as its rim, lpBloom's halo round it, six arrow
              strokes across. The sourced glyph rides only when the row names it. No token moves on an arrow
              before that arrow is drawn.
     hub    - P71 T17 (`layout: "hub"`, v2 T31, Bravos DOM 04:22-04:30 - the IMF with dashed spokes to six governments):
              ONE institution to many. Node 0 stands at the box's centre and the other 3-8 on T11's ellipse round it
              (the first at 12 o'clock, clockwise); every edge is a SPOKE between the hub and one rim node, drawn
              STRAIGHT (no bow - a bowed set reads as a pinwheel; Bravos's spokes are straight). A rim node's own `at`
              is the word that names it: an outward spoke draws on it and its node lands as it arrives (DOM: the
              spoke ~0.35 s = EDGE_S, the tile popping at its end); an inward one lands its node on it and draws its
              spoke EDGE_S later - tail, arrow, head. Unnamed rim nodes take Bravos's default: every spoke together,
              EDGE_LAG after the hub lands.
     fail   - P71 T17 (`fail: {edge, at}`, A26, BOOM 04:41 "Investors X Utility Companies"): the LINK breaks, not the
              node. On `at` a disc in the neg ink springs in at the edge's arc midpoint on BOOM's measured pop and its
              white X is struck in the chip's two strokes; over the same CROSS_S the edge reddens to the neg ink and
              its two halves retract FAIL_RETRACT of their own length from the middle. Its nodes stay; its tokens
              fade out with the retract and ride it no more.
   Nothing is stored: every visual reads from t, sp.at and sp.swap.at, so a scrubbed frame is the played
   frame. The glyphs are SOURCED icons (assets/icons, A2a provenance) carried in the asset map as
   `icon:<name>`; this module never invents geometry. The dials below are ours to tune (42 s42.5). */
import { springPop } from "../kinetics/spring.mjs";
import { idleXf } from "../kinetics/idle.mjs";
import { clothoid, clothoidPath } from "../kinetics/clothoid.mjs";
import { CHIP, chipLand, chipGeometry, chipStrokes } from "./chip.mjs";

export const FLOW = Object.freeze({
  BOX_S: 0.9,        /* the dashed frame's own draw: long enough that the nib is seen going round, short enough that the first chip is not kept waiting */
  BOX_LEAD: 0.55,    /* ... and the share of it that is done when the first chip lands - the frame is still drawing under the diagram, the way a hand works */
  DASH: 26,          /* the dash's length in STAGE px ... */
  DASH_GAP: 15,      /* ... and the air between two dashes: a 2:1 rhythm reads as "a frame", never as a solid box */
  NODE_STEP: 0.2,    /* one node after the last: a beat under the eye's own saccade, so three read as a sequence and not a flash */
  EDGE_LAG: 0.1,     /* the breath between the last chip landing and the first arrow leaving it */
  EDGE_S: 0.34,      /* one arrow, drawn by length; arrows go one at a time - the mechanism is read in its order */
  EDGE_RETRACT_S: 0.30, /* an authored edge-state change retracts its standing arrows before drawing the replacement */
  STATE_RETRACT_S: 0.30, /* named alias for the schema's state-fit clock; kept equal to EDGE_RETRACT_S */
  BOW: 0.42,         /* the exit tangent's turn off the chord, in radians: enough curve to read as a hand's arrow, not a hoop */
  ENTER_K: 0.45,     /* ... and the entry tangent's turn as a share of it. UNEQUAL: equal angles are a circular arc and waste the fitter */
  EDGE_GAP: 16,      /* the air between a card's edge and the arrow that leaves it */
  HEAD: 28,          /* the arrowhead's stroke length in stage px ... */
  HEAD_A: 0.42,      /* ... and its half-angle in radians */
  HEAD_F: 0.72,      /* ... landing over the last of the arrow's own clock, after the shaft has arrived */
  SAMPLES: 40,       /* the clothoid's polyline per arrow: dense enough that its chords hide at our sizes */
  SWAP_OUT_S: 0.3,   /* the standing node's landing, run BACKWARD */
  SWAP_IN_S: 0.45,   /* ... and the new one's, run forward: in is slower than out, so the eye lands on what arrived */
  TAG_LAG: 0.12,     /* the breath before the year stamps ... */
  TAG_S: 0.5,        /* ... and its own write */
  TAG_PAD: 26,       /* the stamp's inset from the box's top-right corner */
  TAG_SIZE: 34,      /* ... at this size: a date, not a title */
  PITCH_K: 1.5,      /* a node's room ALONG the row as a multiple of the card: the card plus the arrow between it and the next */
  CROSS_K: 1.15,     /* ... and ACROSS it, over card + label: a breath above and below */
  MIN_K: 0.4,        /* the smallest the diagram may be scaled to before it stops being read - under it the author gave it too small a box */
  LABEL_H: 34,       /* the label's own line, for the block's height (the chip writes it at CHIP.LABEL_DY below the card) */
  PHONE_LABEL_SIZE: 45, /* opt-in landscape-phone text; explicit because inherited CSS is too small at phone scale */
  PHONE_LABEL_DY: 52, /* the gap below a card before a phone-profile label starts */
  PHONE_LABEL_LINE_H: 48, /* baseline step for newline-separated phone labels */
  PHONE_TAG_SIZE: 48, /* opt-in landscape-phone tag size */
  PHONE_TAG_PAD: 32,
  OPERATOR_SIZE: 30, /* connector-minus length in stage px */
  PHONE_OPERATOR_SIZE: 36,
  RING_START: -Math.PI / 2, /* P71 T11: the ring's first node stands at 12 o'clock, the rest clockwise (screen y runs down, so + is clockwise) */
  RING_LABEL_CLEAR: 8, /* on a ring an arrow leaves or enters a card THROUGH ITS LABEL when the ring runs vertically there (the 3 and 9 o'clock nodes): its anchor drops below the label's baseline by this much more than EDGE_GAP (read in the frame, 2026-09-24) */
  RING_FIT_STEPS: 40,  /* the bisection that finds the largest diagram scale whose ring still clears every card - deterministic, no tolerance chase */
  TOKEN_N: 2,          /* P71 T11: tokens on each arrow when the row names none - two read as a stream, one as a parcel */
  TOKEN_SPEED: 240,    /* ... their speed along the arc in STAGE px per second when the row names none - capped by TOKEN_MIN_CROSS_S below */
  TOKEN_MIN_CROSS_S: 0.49, /* [DERIVED: Bravos DOM 03:27 (PWMhM2_dj3s), the notes tracked at 30 fps - ~20 px/frame at 720p = ~900 stage px/s; the loop's top edge (443 stage px) crossed in 0.49 s, its left edge (651 px) in 0.72 s; notes ~52 x 30 stage px, ~390 px apart on a ~3 px edge] the reference's FASTEST per-edge crossing: no token crosses the diagram's SHORTEST arrow in less - the one speed is min(speed, shortest arc / this) */
  TOKEN_R: 16,         /* [DERIVED: the parent's frame read - an 11 px dot in the arrow's ink read as a joint] the dot's radius in stage px (x the diagram's scale): 32 px across = 6.4 arrow strokes (the read asked >= 2.5); Bravos DOM's notes are ~52 x 30 stage px on a ~3 px edge */
  TOKEN_RIM: 5,        /* the rim: the arrow's own ink at the arrow's own stroke width, so the token is visibly OF the arrow */
  TOKEN_CORE: "#F2F2F2",      /* the core: the page chalk (--lp-chalk) - lighter than the arrow ink, so the token reads as a separate object over it */
  TOKEN_BLOOM_PX: 10,  /* lpBloom's form (E67 / s117): a drop-shadow halo in the arrow ink round the token - its radius in stage px (x k) ... */
  TOKEN_BLOOM_A: 0.55, /* ... and its alpha: above a line's 0.35 (LINE_BLOOM) because the token is the moving thing the beat is about */
  PHONE_TOKEN_CORE: "#F4E6C7", /* the landscape-phone page's cream; its rim is PHONE_TOKEN_INK and it carries no halo (a dark halo on cream is a shadow) */
  TOKEN_FADE: 0.12,    /* the share of an arrow's arc over which a token fades in off the tail and out into the head - no pop at either card */
  TOKEN_GLYPH: 44,     /* a named glyph token's size in stage px (x the diagram's scale) - only when the row names one */
  TOKEN_INK: "#F5B72E",       /* the arrow's own ink: the template's `.flowarrow` stroke (test_flow_loop pins the two together) */
  PHONE_TOKEN_INK: "#25313C", /* ... and the landscape-phone arrow's */
  /* P71 T17: THE FAILED LINK - the disc [MEASURED: Bravos BOOM 04:39-04:42, scratch/jx3Ll_full.mp4 at 1920x1080 = stage px,
     p71-t17/logs/measure-boom-fail.json] */
  FAIL_D: 0.198,       /* the disc's diameter in card sides: 46 px on BOOM's 232 px tile (T12's HIS tick badge measured 0.224) */
  FAIL_X: 0.53,        /* the X's reach along x and along y in the disc's radii: +-12 px on its 23 px radius */
  FAIL_X_W: 0.12,      /* the X's stroke in the disc's radii: ~2.5-2.75 px on 23 */
  FAIL_INK: "#FF4D4D", /* the disc and the reddened edge: the template's --lp-neg (chip.mjs's TAB_INK.sell, E28's sign ink) */
  FAIL_MARK: "#FFFFFF", /* the X on the disc: BOOM's white (255,247,255) - 3.27:1 on the neg ink, over WCAG 1.4.11's 3:1 for a mark */
  FAIL_POP_FROM: 0.3,  /* the disc's first-seen size: 13.7 px area-diameter on its settled 42.8 (0.32) */
  FAIL_MP: 0.3,        /* its overshoot: the peak 1.21 x its settled size (bbox 55 / 46 px) = 0.3 + 0.7 x (1 + Mp) */
  FAIL_POP_S: 0.83,    /* its spring's clock: at Mp 0.3 springPop peaks at u 0.201, so 0.83 s puts the peak at 0.167 s, BOOM's */
  HUB_REACH: 2.56,     /* [MEASURED: Bravos DOM 04:30 (PWMhM2_dj3s), six tiles round the IMF - centre-to-hub 271-391 px on tiles 79-117 px,
                          2.56-4.95 sides, mean 3.56 - p71-t17/logs/measure-dom-hub.json] a rim node stands at least Bravos's SHORTEST
                          reach from the hub, in card sides, so every spoke has room to be seen (the one scale shrinks to keep it) */
  FAIL_RETRACT: 0.12,  /* [the plan's, P71 T17] each half of the failed edge retracts this share of its own length from the middle -
                          BOOM keeps its dashed edge whole and white under the disc (a finding for the parent) */
  /* P72 T46d (R26-384): the failed link's disc sized by the STAGE, not the card - at our card size (CHIP.SIZE 168 x the
     layout's k) FAIL_D made a 25-33 px dot where BOOM's badge is 46 px on its 1920 stage whatever its tiles */
  FAIL_PX: 46,         /* [MEASURED: BOOM 04:41, the settled disc's bbox, 1920 x 1080 = stage px - p71-t17/logs/measure-boom-fail.json] */
  /* P72 T46d (R26-384) - THE SEAL HUB (`look: "seal"` on a `layout: "hub"` flow), DOM 04:30 (PWMhM2_dj3s, measured at 1280
     x 720 off p71-t17/frames/bravos-DOM-270.png, stage px = x 1.5): the hub is a SEAL - no card, its emblem larger than
     the rim's tiles and glowing in its own ink - and the spokes are thin straight DASHES with no heads. */
  SEAL_K: 1.43,        /* [MEASURED: the seal 134 px on tiles of 79-117 (mean ~94) - T17's read; this frame: 135 px] the hub's side over a card's */
  SEAL_INK: "#0D7DF4", /* [MEASURED: the seal's own blue, mean of its 6038 px with b > 200: rgb(13, 125, 244)] the emblem and its glow */
  SEAL_GLOW: 0.2,      /* [MEASURED: the blue excess falls from ~50 at the seal's edge (r 67 px) to ~13 by r 100-105: a halo ~35 px past a
                          135 px seal] the glow's radius as a share of the hub's side */
  SEAL_GLOW_A: 0.85,   /* its alpha - the halo reads as the seal's own light, not a shadow */
  SPOKE_DASH: 18,      /* [MEASURED: the right spoke's runs 12 on / 11 off at 720 px -> 18 / 16.5 stage px] a spoke's dash ... */
  SPOKE_GAP: 16,       /* ... and its gap, stage px (x the layout's k) */
  SPOKE_W: 2,          /* [MEASURED: ~1.3 px at 720 -> 2 stage px] its width */
  SPOKE_INK: "#F2F2F2",   /* [MEASURED: the dashes peak at 194 grey on the dark ground] the page chalk (--lp-chalk) */
});
export const FLOW_LOOKS = Object.freeze(["seal"]);   /* P72 T46d: the hub's looks (build_scene_timeline_f.FLOW_LOOKS mirrors it) */

/* THE SEAL'S SPOKE at draw fraction f: the straight spoke's polyline cut into SPOKE_DASH / SPOKE_GAP dashes (x k), each
   dash drawn as far as the pen has reached - [[a, b], ...] stage points, empty before the pen starts. */
export const flowSealDashes = (pts, f, k = 1) => {
  const cum = flowArc(pts), L = cum[cum.length - 1], reach = flow01(f) * L, D = FLOW.SPOKE_DASH * k, G = FLOW.SPOKE_GAP * k, out = [];
  if (!(L > 0) || !(reach > 0)) return out;
  for (let s0 = 0; s0 < reach; s0 += D + G) {
    const s1 = Math.min(s0 + D, reach, L), a = flowAlong(pts, cum, s0), b = flowAlong(pts, cum, s1);
    if (s1 > s0) out.push([a, b]);
  }
  return out;
};

const flow01 = (v) => Math.min(1, Math.max(0, v));

/* THE RING (P71 T11): the point of node i on the ellipse (cx, cy, rx, ry) - the first at RING_START, the rest
   clockwise at equal angles - and the ring's own tangent there, as an angle. */
export const flowRingPoint = (ring, i, N) => {
  const th = FLOW.RING_START + 2 * Math.PI * i / N;
  return { x: ring.cx + ring.rx * Math.cos(th), y: ring.cy + ring.ry * Math.sin(th),
           tangent: Math.atan2(ring.ry * Math.cos(th), -ring.rx * Math.sin(th)) };
};

/* the ring at diagram scale k: the ellipse inscribed in the box, pulled in by half a node's block (card + label,
   with CROSS_K's breath) so every node stands INSIDE the box it was given */
const flowRingAt = (box, k, block) => ({
  cx: box.x + box.w / 2, cy: box.y + box.h / 2,
  rx: box.w / 2 - CHIP.SIZE * k * FLOW.CROSS_K / 2, ry: box.h / 2 - block * k * FLOW.CROSS_K / 2,
});

/* does the ring at scale k leave every node its room? Adjacent nodes a PITCH_K card apart along their chord (the
   card plus the arrow between them, the row's own rule), and no two node blocks overlapping at all. */
const flowRingClears = (box, N, k, block) => {
  const ring = flowRingAt(box, k, block);
  if (!(ring.rx > 0 && ring.ry > 0)) return false;
  const pts = [];
  for (let i = 0; i < N; i++) pts.push(flowRingPoint(ring, i, N));
  const w = CHIP.SIZE * k * FLOW.CROSS_K, h = block * k * FLOW.CROSS_K;
  for (let i = 0; i < N; i++) {
    const a = pts[i], b = pts[(i + 1) % N];
    if (N > 1 && Math.hypot(b.x - a.x, b.y - a.y) < CHIP.SIZE * k * FLOW.PITCH_K) return false;
    for (let j = i + 1; j < N; j++) if (Math.abs(pts[j].x - a.x) < w && Math.abs(pts[j].y - a.y) < h) return false;
  }
  return true;
};

/* the ring's layout: the largest scale in [MIN_K, 1] that clears (bisected - deterministic), the cells on the
   ellipse with the card lifted so card + label centre on it, and each arrow's BOW - the angle between its chord
   and the ring's tangent at its tail, so the arrow leaves its card along the loop. */
const flowRingLayout = (box, N, block, below, labelDy) => {
  let k = 1;
  if (!flowRingClears(box, N, 1, block)) {
    let lo = FLOW.MIN_K, hi = 1;
    if (flowRingClears(box, N, lo, block)) {
      for (let s = 0; s < FLOW.RING_FIT_STEPS; s++) {
        const mid = 0.5 * (lo + hi);
        if (flowRingClears(box, N, mid, block)) lo = mid; else hi = mid;
      }
    }
    k = lo;
  }
  const ring = flowRingAt(box, k, block), lift = below * k / 2, cells = [], tangents = [];
  for (let i = 0; i < N; i++) {
    const p = flowRingPoint(ring, i, N);
    cells.push({ x: p.x, y: p.y - lift });
    tangents.push(p.tangent);
  }
  const bows = cells.map((a, i) => {
    const b = cells[(i + 1) % N], chord = Math.atan2(b.y - a.y, b.x - a.x);
    return Math.atan2(Math.sin(chord - tangents[i]), Math.cos(chord - tangents[i]));
  });
  return { k, column: false, ring: true, cells, bows, half: CHIP.SIZE * k / 2,
           below: (labelDy + FLOW.RING_LABEL_CLEAR) * k,   /* the label under each card, which a ring arrow must clear */
           cx: ring.cx, cy: ring.cy, rx: ring.rx, ry: ring.ry };
};

/* THE HUB (P71 T17): does the rim at scale k (R nodes on T11's ring) clear itself - the ring's own rule - AND the hub at
   the centre? Every rim node HUB_REACH cards from the hub (Bravos's shortest spoke), no rim block over the hub's. */
const flowHubClears = (box, R, k, block) => {
  if (!flowRingClears(box, R, k, block)) return false;
  const ring = flowRingAt(box, k, block), w = CHIP.SIZE * k * FLOW.CROSS_K, h = block * k * FLOW.CROSS_K;
  for (let i = 0; i < R; i++) {
    const p = flowRingPoint(ring, i, R), dx = p.x - ring.cx, dy = p.y - ring.cy;
    if (Math.hypot(dx, dy) < CHIP.SIZE * k * FLOW.HUB_REACH || (Math.abs(dx) < w && Math.abs(dy) < h)) return false;
  }
  return true;
};

/* the hub's layout: the largest scale in [MIN_K, 1] that clears (bisected, as the ring's), node 0 at the centre and the
   R = N - 1 rim nodes on the ring, every card lifted so card + label centre on its point. Spokes are straight (no bows). */
const flowHubLayout = (box, N, block, below, labelDy) => {
  const R = Math.max(1, N - 1);
  let k = 1;
  if (!flowHubClears(box, R, 1, block)) {
    let lo = FLOW.MIN_K, hi = 1;
    if (flowHubClears(box, R, lo, block)) {
      for (let s = 0; s < FLOW.RING_FIT_STEPS; s++) {
        const mid = 0.5 * (lo + hi);
        if (flowHubClears(box, R, mid, block)) lo = mid; else hi = mid;
      }
    }
    k = lo;
  }
  const ring = flowRingAt(box, k, block), lift = below * k / 2, cells = [{ x: ring.cx, y: ring.cy - lift }];
  for (let i = 0; i < R; i++) {
    const p = flowRingPoint(ring, i, R);
    cells.push({ x: p.x, y: p.y - lift });
  }
  return { k, column: false, hub: true, cells, half: CHIP.SIZE * k / 2,
           below: (labelDy + FLOW.RING_LABEL_CLEAR) * k,   /* the label under each card, which a spoke must clear */
           cx: ring.cx, cy: ring.cy, rx: ring.rx, ry: ring.ry };
};

/* THE LAYOUT: where each node stands inside the declared box, and how big the whole diagram is drawn.
   A row inside the box; a COLUMN when the box is taller than it is wide (a portrait build's box is), which
   is the same rule read from the geometry rather than from the aspect. P71 T11: `options.layout === "ring"`
   lays them on the ring instead (flowRingLayout), and P71 T17's `"hub"` the hub at the centre with the rest on that
   ring (flowHubLayout); absent, the row is byte for byte what it was. */
export const flowLayout = (box, n, options = null) => {
  const N = Math.max(1, n | 0), column = box.h > box.w;
  const pitch = (column ? box.h : box.w) / N, across = column ? box.w : box.h;
  const phone = !!(options && options.readability === "landscape-phone");
  let labelLines = 1;
  if (phone && Array.isArray(options.labels)) {
    for (const label of options.labels) labelLines = Math.max(labelLines, String(label == null ? "" : label).split(/\r?\n/).length);
  }
  const labelDy = phone ? FLOW.PHONE_LABEL_DY : CHIP.LABEL_DY;
  const labelH = phone ? FLOW.PHONE_LABEL_LINE_H * labelLines : FLOW.LABEL_H;
  const block = CHIP.SIZE + labelDy + labelH;
  if (options && (options.layout === "ring" || options.layout === "hub")) {   /* P71 T17: the hub beside T11's ring */
    const out = (options.layout === "hub" ? flowHubLayout : flowRingLayout)(box, N, block, labelDy + labelH, labelDy);
    if (phone) Object.assign(out, { phone: true, labelDy, labelH, labelLines, labelLineH: FLOW.PHONE_LABEL_LINE_H });
    return out;
  }
  const k =Math.max(FLOW.MIN_K, Math.min(1, pitch / (CHIP.SIZE * FLOW.PITCH_K), across / (block * FLOW.CROSS_K)));
  const lift = (labelDy + labelH) * k / 2;   /* the card sits above centre so card + label are centred together */
  const cells = [];
  for (let i = 0; i < N; i++) {
    cells.push(column ? { x: box.x + box.w / 2, y: box.y + pitch * (i + 0.5) - lift }
                       : { x: box.x + pitch * (i + 0.5), y: box.y + box.h / 2 - lift });
  }
  const out = { k, column, cells, half: CHIP.SIZE * k / 2 };
  if (phone) Object.assign(out, { phone: true, labelDy, labelH, labelLines, labelLineH: FLOW.PHONE_LABEL_LINE_H });
  return out;
};

/* THE CLOCK: every instant the declaration implies, in episode seconds. One place, so the painter, the tests
   and the gate all read the same schedule. */
export const flowClock = (sp) => {
  if (sp && sp.layout === "hub") return flowHubClock(sp);   /* P71 T17; every other flow reads the lines below, unchanged */
  const at = +sp.at, nodes = sp.nodes || [], edges = sp.edges || [];
  const first = at + FLOW.BOX_S * FLOW.BOX_LEAD;
  const nodeAt = nodes.map((_, i) => first + i * FLOW.NODE_STEP);
  const landed = (nodeAt.length ? nodeAt[nodeAt.length - 1] : first) + CHIP.LAND_S;
  const edgeAt = edges.map((_, j) => landed + FLOW.EDGE_LAG + j * FLOW.EDGE_S);
  const tagAt = (edgeAt.length ? edgeAt[edgeAt.length - 1] + FLOW.EDGE_S : landed) + FLOW.TAG_LAG;
  return { box: [at, at + FLOW.BOX_S], nodeAt, landed, edgeAt, tagAt, tagEnd: tagAt + FLOW.TAG_S };
};

/* P71 T17: THE HUB'S CLOCK. The hub (node 0) lands where a row's first node does. Each spoke joins the hub and ONE rim
   node, and runs on that rim node's word - its own `at`, or D (EDGE_LAG after the hub has landed: Bravos draws every
   unnamed spoke together). OUT (hub -> rim): the spoke draws on the word and the node lands as it arrives, EDGE_S later.
   IN (rim -> hub): the node lands on the word and its spoke draws EDGE_S later. The tag follows the last spoke drawn.
   The compiler mirrors this (build_scene_timeline_f.flow_hub_clock; test_hub_and_spoke pins the two). */
export const flowHubClock = (sp) => {
  const at = +sp.at, nodes = sp.nodes || [], edges = sp.edges || [];
  const ids = nodes.map((n) => n && n.id), hubId = ids[0];
  const first = at + FLOW.BOX_S * FLOW.BOX_LEAD, D = first + CHIP.LAND_S + FLOW.EDGE_LAG;
  const word = (i) => (nodes[i] && typeof nodes[i].at === "number" && Number.isFinite(nodes[i].at) ? nodes[i].at : D);
  const nodeAt = nodes.map((_, i) => (i === 0 ? first : word(i)));
  const edgeAt = edges.map((e) => {
    const out = !!e && e[0] === hubId, r = ids.indexOf(e && (out ? e[1] : e[0]));
    if (r <= 0) return D;   /* not a spoke: the compiler refuses it; drawn on the default word, never on a made-up one */
    const w = word(r);
    if (out) { nodeAt[r] = w + FLOW.EDGE_S; return w; }
    nodeAt[r] = w;
    return w + FLOW.EDGE_S;
  });
  const landed = Math.max(first, ...nodeAt) + CHIP.LAND_S;
  const tagAt = (edgeAt.length ? Math.max(...edgeAt) + FLOW.EDGE_S : landed) + FLOW.TAG_LAG;
  return { box: [at, at + FLOW.BOX_S], nodeAt, landed, edgeAt, tagAt, tagEnd: tagAt + FLOW.TAG_S, hub: true };
};

/* the box's draw at t, 0..1 - and, from it, the dash that is under the nib */
export const flowBoxF = (sp, t) => flow01((t - +sp.at) / FLOW.BOX_S);

/* the rectangle's perimeter cut into dashes, each with the fraction of the whole draw it owns. The nib starts
   at the top-left and runs clockwise - the way the box would be drawn by a hand. */
export const flowDashes = (box) => {
  const per = 2 * (box.w + box.h), n = Math.max(4, Math.round(per / (FLOW.DASH + FLOW.DASH_GAP)));
  const step = per / n, out = [];
  const at = (d) => {   /* a distance round the perimeter -> a point on it, clockwise from the top-left */
    let s = ((d % per) + per) % per;
    if (s < box.w) return { x: box.x + s, y: box.y };
    s -= box.w;
    if (s < box.h) return { x: box.x + box.w, y: box.y + s };
    s -= box.h;
    if (s < box.w) return { x: box.x + box.w - s, y: box.y + box.h };
    return { x: box.x, y: box.y + box.h - (s - box.w) };
  };
  const corners = [box.w, box.w + box.h, 2 * box.w + box.h, per];
  for (let i = 0; i < n; i++) {
    const d0 = i * step;
    let len = Math.min(FLOW.DASH, step * 0.72);
    /* a dash that ran past a CORNER used to be drawn as its chord, which cut the corner off the box (read in
       the frame, 2026-09-11). A dash stops at the corner it reaches; the next one starts the new side. */
    for (const c of corners) if (c > d0 && c < d0 + len) len = c - d0;
    out.push({ a: at(d0), b: at(d0 + len), t0: i / n, t1: (i + 1) / n });
  }
  return out;
};

/* THE SWAP at t: which node is changing, and how far through which half of its change. `phase` is "none"
   before the word, "out" while the standing node un-draws, "in" while the new one draws, "done" after. */
export const flowSwapPhase = (sp, t) => {
  const sw = sp.swap;
  if (!sw || !Number.isFinite(+sw.at)) return { phase: "none", u: 1 };
  const d = t - +sw.at;
  if (d < 0) return { phase: "none", u: 1 };
  if (d < FLOW.SWAP_OUT_S) return { phase: "out", u: 1 - d / FLOW.SWAP_OUT_S };   /* the landing, run backward */
  const uIn = flow01((d - FLOW.SWAP_OUT_S) / FLOW.SWAP_IN_S);
  return { phase: uIn >= 1 ? "done" : "in", u: uIn };
};

/* ONE NODE at t: what it shows (a swap changes the glyph and the label, never the place) and how far its
   landing has run. u is the landing's normalised clock, which is all chipLand needs. */
export const flowNodeAt = (sp, i, t) => {
  const node = (sp.nodes || [])[i] || {}, sw = sp.swap;
  const C = flowClock(sp), u0 = flow01((t - C.nodeAt[i]) / CHIP.LAND_S);
  if (!sw || sw.node !== node.id) return { icon: node.icon, label: node.label, u: u0, alpha: 1, swapping: false };
  const ph = flowSwapPhase(sp, t);
  if (ph.phase === "none") return { icon: node.icon, label: node.label, u: u0, alpha: 1, swapping: false };
  /* OUT: the landing run backward - and the card's own opacity on the OUT clock. The chip's fade is 0.14 s
     of a 0.55 s landing; reversed into SWAP_OUT_S it would be a blink at the very end rather than an
     un-draw (read in the frame, 2026-09-11), so the ink leaves on the clock the un-draw was given, the way
     an `undraw` retracts a stroke on its own clock and not on the build's. */
  if (ph.phase === "out") return { icon: node.icon, label: node.label, u: Math.min(u0, ph.u), alpha: ph.u, swapping: true };
  return { icon: sw.icon, label: sw.label, u: ph.u, alpha: 1, swapping: ph.phase === "in" };
};

/* the pose of a node at a landing clock u: the chip's own law, on the flow's clock */
export const flowPose = (u) => chipLand(flow01(u) * CHIP.LAND_S, 0);

/* ONE ARROW's draw at t, 0..1 */
export const flowEdgeF = (sp, j, t) => {
  const C = flowClock(sp);
  return C.edgeAt[j] === undefined ? 0 : flow01((t - C.edgeAt[j]) / FLOW.EDGE_S);
};

/* THE ANCHORS of one arrow: the point on each card's square edge that faces the other, pushed out by
   EDGE_GAP, and the two tangents the clothoid is fitted to. `bow` and `below` are P71 T11's ring: the bow is the
   ring's tangent, and `below` extends the card's box DOWN over its label, so an arrow that leaves or enters
   downward clears the words. Both absent: the square and FLOW.BOW, byte for byte. */
export const flowAnchors = (a, b, half, bow = FLOW.BOW, below = 0) => {
  const dx = b.x - a.x, dy = b.y - a.y, chord = Math.atan2(dy, dx);
  const edge = (c, th) => {   /* the square's boundary in direction th, plus the air */
    const cs = Math.cos(th), sn = Math.sin(th);
    if (below > 0) {          /* the card + label box: the ray leaves by whichever side it meets first */
      const ax = Math.abs(cs), ay = Math.abs(sn);
      const r = Math.min(ax > 0 ? half / ax : Infinity, ay > 0 ? (sn > 0 ? half + below : half) / ay : Infinity) + FLOW.EDGE_GAP;
      return { x: c.x + r * cs, y: c.y + r * sn };
    }
    const m = Math.max(Math.abs(cs), Math.abs(sn)) || 1;
    const r = half / m + FLOW.EDGE_GAP;
    return { x: c.x + r * cs, y: c.y + r * sn };
  };
  const t0 = chord - bow, t1 = chord + bow * FLOW.ENTER_K;
  return { p0: edge(a, t0), t0, p1: edge(b, t1 + Math.PI), t1, chord };
};

/* ONE ARROW's polyline in a laid-out diagram: the clothoid between the two cards' anchors. On a ring (P71 T11) an
   arrow from a node to the NEXT one bows by the ring's own tangent at its tail (lay.bows); every other arrow, and
   every arrow of a row, bows by FLOW.BOW exactly as before. */
export const flowEdgePts = (lay, ia, ib) => {
  if (lay.hub) {   /* P71 T17: a SPOKE is straight (bow 0) and clears the label under either card, as a ring arrow does */
    const an = flowAnchors(lay.cells[ia], lay.cells[ib], lay.half, 0, lay.below);
    return clothoid(an.p0, an.t0, an.p1, an.t1, FLOW.SAMPLES);
  }
  const N = lay.cells.length, around = lay.ring && ib === (ia + 1) % N;
  const an = around ? flowAnchors(lay.cells[ia], lay.cells[ib], lay.half, lay.bows[ia], lay.below)
                    : flowAnchors(lay.cells[ia], lay.cells[ib], lay.half);
  return clothoid(an.p0, an.t0, an.p1, an.t1, FLOW.SAMPLES);
};

/* the arrowhead's two strokes at the polyline's far end, along the tangent it arrives on */
export const flowHead = (pts) => {
  const n = pts.length;
  if (n < 2) return "";
  const tip = pts[n - 1], prev = pts[n - 2], th = Math.atan2(tip.y - prev.y, tip.x - prev.x);
  const arm = (s) => ({ x: tip.x - FLOW.HEAD * Math.cos(th + s * FLOW.HEAD_A), y: tip.y - FLOW.HEAD * Math.sin(th + s * FLOW.HEAD_A) });
  const l = arm(1), r = arm(-1);
  return "M" + l.x.toFixed(2) + " " + l.y.toFixed(2) + " L" + tip.x.toFixed(2) + " " + tip.y.toFixed(2)
       + " L" + r.x.toFixed(2) + " " + r.y.toFixed(2);
};

/* the edges as index pairs into the node list (a name that is not a node is dropped, not drawn wrong) */
export const flowEdgeIndex = (sp) => {
  const ids = (sp.nodes || []).map((n) => n && n.id);
  return (sp.edges || []).map((e) => [ids.indexOf(e && e[0]), ids.indexOf(e && e[1])]);
};

/* A validated edge row for the pure edge clock. Invalid declarations are left for the compiler to report and are
   omitted here so a diagnostic painter cannot draw an arrow to a made-up node. `index` remains the declaration index
   because the initial legacy clock is indexed by the original `edges` array, not by the filtered rows. */
const flowEdgeRows = (sp, edges) => {
  const ids = (sp.nodes || []).map((n) => n && n.id);
  if (!Array.isArray(edges)) return [];
  return edges.map((edge, index) => {
    if (!Array.isArray(edge) || edge.length !== 2) return null;
    const fromIndex = ids.indexOf(edge[0]), toIndex = ids.indexOf(edge[1]);
    if (fromIndex < 0 || toIndex < 0 || fromIndex === toIndex) return null;
    return { edge: [edge[0], edge[1]], from: edge[0], to: edge[1], fromIndex, toIndex, index };
  }).filter(Boolean);
};

const flowEdgeRecord = (sp, row, fraction, phase, stateIndex = -1) => ({
  edge: row.edge.slice(), from: row.from, to: row.to,
  fromIndex: row.fromIndex, toIndex: row.toIndex, index: row.index,
  fraction: flow01(fraction), phase, stateIndex,
  kind: Array.isArray(sp.operators) ? "operator" : "arrow",
  operator: Array.isArray(sp.operators) ? sp.operators[row.index] : undefined,
});

/* Build the absolute, non-overlapping windows that the compiler's state-fit rule describes. The first window starts
   after the existing diagram's tagEnd; a bad/partial declaration is a compiler concern, so the pure helper falls
   back to the legacy edge clock rather than inventing a recovery schedule. */
const flowStateWindows = (sp) => {
  const states = Array.isArray(sp.edge_states) && sp.edge_states.length ? sp.edge_states : [];
  const initial = flowEdgeRows(sp, sp.edges);
  if (!states.length) return { initial, windows: [], final: initial, valid: true };
  let previous = initial, previousEnd = flowClock(sp).tagEnd;
  const windows = [];
  for (let i = 0; i < states.length; i++) {
    const state = states[i];
    const at = state && +state.at, rows = state && flowEdgeRows(sp, state.edges);
    if (!Number.isFinite(at) || at < previousEnd || !Array.isArray(state && state.edges) || !state.edges.length || rows.length !== state.edges.length) {
      return { initial, windows: [], final: initial, valid: false };
    }
    const retractEnd = at + FLOW.EDGE_RETRACT_S;
    const drawEnd = retractEnd + rows.length * FLOW.EDGE_S;
    windows.push({ stateIndex: i, at, retractEnd, drawEnd, old: previous, next: rows });
    previous = rows;
    previousEnd = drawEnd;
  }
  return { initial, windows, final: previous, valid: true };
};

const flowInitialEdgesAt = (sp, t, rows) => ({
  phase: "initial", stateIndex: -1,
  edges: rows.map((row) => flowEdgeRecord(sp, row, flowEdgeF(sp, row.index, t), "initial", -1)),
});

const flowSteadyEdges = (sp, rows, stateIndex) => ({
  phase: "steady", stateIndex,
  edges: rows.map((row) => flowEdgeRecord(sp, row, 1, "steady", stateIndex)),
});

/* The complete edge state at episode time t. This is deliberately data-only: no DOM, clock, random source or
   retained transition state. During retraction the old set runs backwards as a whole; during drawing the new set
   appears one edge at a time at EDGE_S. Absolute `state.at` values are never offset by the row's own `at`. */
export const flowEdgesAt = (sp, t) => {
  const raw = +t, now = Number.isFinite(raw) ? raw : -Infinity, schedule = flowStateWindows(sp || {});
  if (!Number.isFinite(now) || !schedule.valid || !schedule.windows.length) return flowInitialEdgesAt(sp || {}, now, schedule.initial);
  let previous = null;
  for (const win of schedule.windows) {
    if (now < win.at) return previous ? flowSteadyEdges(sp, previous.next, previous.stateIndex) : flowInitialEdgesAt(sp, now, schedule.initial);
    if (now < win.retractEnd) {
      const f = 1 - flow01((now - win.at) / FLOW.EDGE_RETRACT_S);
      return { phase: "retract", stateIndex: win.stateIndex, at: win.at, retractEnd: win.retractEnd, drawEnd: win.drawEnd,
        edges: win.old.map((row) => flowEdgeRecord(sp, row, f, "retract", win.stateIndex)) };
    }
    if (now < win.drawEnd) {
      const elapsed = now - win.retractEnd;
      return { phase: "draw", stateIndex: win.stateIndex, at: win.at, retractEnd: win.retractEnd, drawEnd: win.drawEnd,
        edges: win.next.map((row, j) => flowEdgeRecord(sp, row, (elapsed - j * FLOW.EDGE_S) / FLOW.EDGE_S, "draw", win.stateIndex)) };
    }
    previous = win;
  }
  return flowSteadyEdges(sp, schedule.final, previous ? previous.stateIndex : -1);
};

/* THE TOKENS (P71 T11, A27). `sp.tokens = {from_at, n?, speed?, glyph?}`; everything below is a pure function of
   t, sp and the laid-out diagram. */

/* the instant tokens start on arrow j: `from_at`, but never before that arrow is drawn, head and all. Infinity =
   never (no tokens, no from_at, or no such arrow). */
export const flowTokenStart = (sp, j) => {
  const tk = sp && sp.tokens, C = flowClock(sp || {});
  if (!tk || !Number.isFinite(+tk.from_at) || C.edgeAt[j] === undefined) return Infinity;
  return Math.max(+tk.from_at, C.edgeAt[j] + FLOW.EDGE_S);
};

/* the polyline's cumulative arc length, and the point (with its heading) at arc s along it */
const flowArc = (pts) => {
  const cum = [0];
  for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y));
  return cum;
};
const flowAlong = (pts, cum, s) => {
  let i = 1;
  while (i < pts.length - 1 && cum[i] < s) i++;
  const a = pts[i - 1], b = pts[i], seg = cum[i] - cum[i - 1], u = seg > 0 ? flow01((s - cum[i - 1]) / seg) : 0;
  return { x: a.x + (b.x - a.x) * u, y: a.y + (b.y - a.y) * u, heading: Math.atan2(b.y - a.y, b.x - a.x) };
};

/* every arrow a token can ride: its index, polyline, cumulative arc and length (a name that is not a node drops) */
const flowTokenArcs = (sp, lay) => {
  const out = [];
  flowEdgeIndex(sp).forEach(([ia, ib], j) => {
    if (ia < 0 || ib < 0 || ia === ib || !lay.cells[ia] || !lay.cells[ib]) return;
    const pts = flowEdgePts(lay, ia, ib), cum = flowArc(pts), L = cum[cum.length - 1];
    if (L > 0) out.push({ j, pts, cum, L });
  });
  return out;
};

/* THE ONE SPEED the tokens ride at, in stage px per second of arc: the row's (or TOKEN_SPEED), capped so the
   diagram's SHORTEST arrow takes at least TOKEN_MIN_CROSS_S - one speed for every arrow, so a token never
   changes pace between two of them. */
export const flowTokenSpeed = (sp, lay) => {
  const tk = (sp && sp.tokens) || {};
  const asked = Number.isFinite(+tk.speed) && +tk.speed > 0 ? +tk.speed : FLOW.TOKEN_SPEED;
  const arcs = lay && Array.isArray(lay.cells) ? flowTokenArcs(sp, lay) : [];
  if (!arcs.length) return asked;
  return Math.min(asked, Math.min(...arcs.map((a) => a.L)) / FLOW.TOKEN_MIN_CROSS_S);
};

/* EVERY TOKEN at t: on each drawn arrow, n tokens leave its tail one after another (token i a 1/n lap behind
   token i-1) and ride it at `speed` stage px per second of arc, back to the tail when they reach the head - the
   money keeps moving. `u` is the token's share of its arrow, `lap` how many times it has crossed it, `alpha` its
   fade in off the tail and out into the head. Operators and edge_states carry no tokens (the compiler refuses the
   pair by name). */
export const flowTokens = (sp, t, lay) => {
  const tk = sp && sp.tokens;
  if (!tk || !lay || !Array.isArray(lay.cells)) return [];
  if ((Array.isArray(sp.edge_states) && sp.edge_states.length) || (Array.isArray(sp.operators) && sp.operators.length)) return [];
  const n = Number.isInteger(tk.n) && tk.n > 0 ? tk.n : FLOW.TOKEN_N;
  const speed = flowTokenSpeed(sp, lay), failed = flowFailIndex(sp);
  const out = [];
  flowTokenArcs(sp, lay).forEach(({ j, pts, cum, L }) => {
    const t0 = flowTokenStart(sp, j);
    if (!(t >= t0)) return;
    const run = speed * (t - t0);
    const cut = j === failed ? flowFailAt(sp, t) : null;   /* P71 T17: a failing link's money fades on its retract */
    if (cut && cut.u >= 1) return;
    for (let i = 0; i < n; i++) {
      const travel = run - i * L / n;
      if (travel < 0) continue;
      const lap = Math.floor(travel / L), s = travel - lap * L, u = s / L;
      const p = flowAlong(pts, cum, s), alpha = flow01(Math.min(u, 1 - u) / FLOW.TOKEN_FADE);
      out.push({ edge: j, i, s, u, lap, L, x: p.x, y: p.y, heading: p.heading, alpha: cut ? alpha * (1 - cut.u) : alpha });
    }
  });
  return out;
};

/* P71 T17: THE FAILED LINK (A26). `sp.fail = {edge: [from, to], at}` names one DECLARED edge; everything below is a pure
   function of t and sp. */

/* the failed edge's index in sp.edges (as declared), or -1: no fail, or an edge the diagram does not draw */
export const flowFailIndex = (sp) => {
  const f = sp && sp.fail;
  if (!f || !Array.isArray(f.edge) || f.edge.length !== 2) return -1;
  return (sp.edges || []).findIndex((e) => Array.isArray(e) && e[0] === f.edge[0] && e[1] === f.edge[1]);
};

/* the failure at t, or null before its word: `u` runs the X's two strokes (the chip's law, over CHIP.CROSS_S) and, on
   the same clock, the edge's reddening and retract; the disc springs in on BOOM's measured pop (scale) and fades up on
   the chip's FADE_S */
export const flowFailAt = (sp, t) => {
  const j = flowFailIndex(sp), at = j >= 0 ? sp.fail.at : NaN;
  if (typeof at !== "number" || !Number.isFinite(at) || !(t >= at)) return null;
  const d = t - at, u = flow01(d / CHIP.CROSS_S);
  return { j, at, u, strokes: chipStrokes(u), fade: flow01(d / CHIP.FADE_S),
           scale: FLOW.FAIL_POP_FROM + (1 - FLOW.FAIL_POP_FROM) * springPop(flow01(d / FLOW.FAIL_POP_S), FLOW.FAIL_MP) };
};

/* the part of a polyline between arc lengths s0 and s1 (cum = its cumulative arc) */
const flowSub = (pts, cum, s0, s1) => {
  const out = [flowAlong(pts, cum, s0)];
  for (let i = 1; i < pts.length - 1; i++) if (cum[i] > s0 && cum[i] < s1) out.push({ x: pts[i].x, y: pts[i].y });
  out.push(flowAlong(pts, cum, s1));
  return out.map((p) => ({ x: p.x, y: p.y }));
};

/* THE SEVERED EDGE at retract u: its two halves, each shortened by FAIL_RETRACT x u of its own length from the middle
   (the ends stay at their cards), and the arc's midpoint - where the disc sits, in the gap */
export const flowFailSplit = (pts, u) => {
  const cum = flowArc(pts), L = cum[cum.length - 1], r = FLOW.FAIL_RETRACT * flow01(u) * L / 2, m = flowAlong(pts, cum, L / 2);
  return { a: flowSub(pts, cum, 0, L / 2 - r), b: flowSub(pts, cum, L / 2 + r, L), mid: { x: m.x, y: m.y } };
};

/* the failing edge's ink at u: the arrow's own ink (the phone's charcoal) mixed toward the neg ink, "#rrggbb" */
export const flowFailInk = (phone, u) => {
  const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  const a = rgb(phone ? FLOW.PHONE_TOKEN_INK : FLOW.TOKEN_INK), b = rgb(FLOW.FAIL_INK), k = flow01(u);
  return "#" + a.map((v, i) => Math.round(v + (b[i] - v) * k).toString(16).padStart(2, "0")).join("");
};

/* the failed edge's paint: the two halves and the head, whole (the compiler refuses a fail before its edge is drawn), in
   the reddening ink */
const paintFlowFailedEdge = (el, g, pts, cut, phone, drawOn) => {
  const ink = flowFailInk(phone, cut.u), cutp = flowFailSplit(pts, cut.u);
  const style = "fill:none;stroke:" + ink + ";stroke-width:5;stroke-linecap:round;stroke-linejoin:round";
  for (const half of [cutp.a, cutp.b]) drawOn(el("path", "flowarrow", g, { d: clothoidPath(half), style }), 1);
  drawOn(el("path", "flowarrow", g, { d: flowHead(pts), style }), 1);
};

/* the disc and its X at the failed edge's midpoint, OVER the world (after the cards): a neg-ink disc springing in about
   its centre, and the white X struck in two strokes */
const paintFlowFail = (el, g, at, cut, lay, drawOn) => {
  const r = FLOW.FAIL_PX / 2, a = FLOW.FAIL_X * r, f = (v) => v.toFixed(2);   /* a: each arm's x and y reach; R26-384: the stage's size, not the card's */
  const fg = el("g", "flowfail", g, { opacity: cut.fade.toFixed(3),
    transform: "translate(" + f(at.x) + " " + f(at.y) + ") scale(" + cut.scale.toFixed(4) + ")" });
  el("circle", "flowfaildisc", fg, { cx: 0, cy: 0, r: f(r), style: "fill:" + FLOW.FAIL_INK + ";stroke:none" });
  const style = "fill:none;stroke:" + FLOW.FAIL_MARK + ";stroke-width:" + f(FLOW.FAIL_X_W * r) + ";stroke-linecap:round";
  [["M" + f(-a) + " " + f(-a) + " L" + f(a) + " " + f(a), cut.strokes[0]],
   ["M" + f(a) + " " + f(-a) + " L" + f(-a) + " " + f(a), cut.strokes[1]]]
    .forEach(([d, k]) => { if (k > 0) drawOn(el("path", "flowfailmark", fg, { d, style }), k); });
};

/* "#RRGGBB" at alpha a -> "rgba(r,g,b,a)" (the halo's colour, as lpBloom writes lpInkA) */
const flowInkA = (hex, a) => {
  const h = String(hex).replace("#", ""), v = (i) => parseInt(h.slice(i, i + 2), 16);
  return "rgba(" + v(0) + "," + v(2) + "," + v(4) + "," + a + ")";
};

/* the plain token's style: the chalk core, the arrow-ink rim at the arrow's width, and lpBloom's halo (dark page only) */
export const flowTokenStyle = (k, phone) => phone
  ? "fill:" + FLOW.PHONE_TOKEN_CORE + ";stroke:" + FLOW.PHONE_TOKEN_INK + ";stroke-width:" + (FLOW.TOKEN_RIM * k).toFixed(2)
  : "fill:" + FLOW.TOKEN_CORE + ";stroke:" + FLOW.TOKEN_INK + ";stroke-width:" + (FLOW.TOKEN_RIM * k).toFixed(2)
    + ";filter:drop-shadow(0 0 " + (FLOW.TOKEN_BLOOM_PX * k).toFixed(2) + "px " + flowInkA(FLOW.TOKEN_INK, FLOW.TOKEN_BLOOM_A) + ")";

/* the tokens' paint: a plain dot that reads as a thing riding the arrow, or - only when the row names it - the
   sourced glyph */
const paintFlowTokens = (ctx, g, lay, phone) => {
  const { sp, t, el, A } = ctx;
  const ink = phone ? FLOW.PHONE_TOKEN_INK : FLOW.TOKEN_INK;
  const geo = sp.tokens.glyph ? chipGeometry(A ? A["icon:" + sp.tokens.glyph] : null) : null;
  const dotStyle = flowTokenStyle(lay.k, phone);
  for (const tok of flowTokens(sp, t, lay)) {
    if (!(tok.alpha > 0)) continue;
    if (!geo) {
      el("circle", "flowtoken", g, { cx: tok.x.toFixed(2), cy: tok.y.toFixed(2), r: (FLOW.TOKEN_R * lay.k).toFixed(2),
                                     style: dotStyle, opacity: tok.alpha.toFixed(3) });
      continue;
    }
    const size = FLOW.TOKEN_GLYPH * lay.k, vb = geo.vb || [0, 0, 24, 24], gk = size / Math.max(vb[2] || 1, vb[3] || 1);
    const gg = el("g", "flowtoken", g, { opacity: tok.alpha.toFixed(3),
      transform: "translate(" + (tok.x - size / 2).toFixed(2) + " " + (tok.y - size / 2).toFixed(2) + ") scale(" + gk.toFixed(4) + ") translate(" + (-vb[0]) + " " + (-vb[1]) + ")",
      style: "fill:none;stroke:" + ink + ";stroke-width:2;stroke-linecap:round;stroke-linejoin:round" });
    geo.el.forEach((q) => el(q.t, "", gg, q.a));   /* the sourced geometry verbatim */
  }
};

/* THE PAINTER. ctx is the template's species context (see SPECIES_PAINTERS in the player). Everything is
   drawn in STAGE px into one group, in reading order: the frame, the arrows (under the cards, so their ends
   tuck beneath), the cards, the stamp. */
export function paintFlow(ctx) {
  const { sp, t, svg, el, A, resolveTarget, drawOn, hash, idle, seed, si } = ctx;
  const box = resolveTarget(sp.target);
  if (!box || !(box.w > 0 && box.h > 0)) return;   /* the targeting law: a flow needs its room declared */
  const nodes = sp.nodes || [], phone = sp.readability === "landscape-phone";
  const labels = phone ? nodes.map((node) => node && node.label).concat(sp.swap && sp.swap.label ? [sp.swap.label] : []) : null;
  const laid = sp.layout === "ring" || sp.layout === "hub";   /* P71 T11 / T17: absent layout passes the same options the row always had */
  const layOpts = phone ? Object.assign({ readability: "landscape-phone", labels }, laid ? { layout: sp.layout } : {}) : (laid ? { layout: sp.layout } : null);
  const lay = flowLayout(box, nodes.length, layOpts), C = flowClock(sp);
  const g = el("g", "flow", svg, {});
  const phoneBoxStyle = "fill:none;stroke:#25313C;stroke-width:3;stroke-linecap:round";
  const phoneArrowStyle = "fill:none;stroke:#25313C;stroke-width:5;stroke-linecap:round;stroke-linejoin:round";
  const pathAttrs = (d, style) => phone ? { d, style: style || phoneArrowStyle } : { d };
  /* the frame, dash by dash, under the nib */
  const bf = flowBoxF(sp, t);
  if (bf > 0) {
    for (const d of flowDashes(box)) {
      const f = flow01((bf - d.t0) / Math.max(1e-6, d.t1 - d.t0));
      if (f <= 0) continue;
       const p = el("path", "flowbox", g, pathAttrs("M" + d.a.x.toFixed(1) + " " + d.a.y.toFixed(1) + " L" + d.b.x.toFixed(1) + " " + d.b.y.toFixed(1), phoneBoxStyle));
      if (f < 1) drawOn(p, f);
    }
  }
  /* The absent-extension branch is intentionally the old loop: legacy declarations keep the same element order,
     classes, paths and draw fractions. Opt-in states reverse the fitted polyline from its head, then draw the new
     set in declaration order. Operators are a separate short minus at the connector midpoint - no arrow path/head. */
  const stateMode = Array.isArray(sp.edge_states) && sp.edge_states.length;
  const operatorMode = !stateMode && Array.isArray(sp.operators) && sp.operators.length;
  /* P71 T17: the failed link, from its word (never beside edge_states / operators - the compiler refuses the pair) */
  const failCut = stateMode || operatorMode ? null : flowFailAt(sp, t);
  const seal = !!lay.hub && sp.look === "seal" && !phone;   /* P72 T46d (R26-384): DOM's hub look - opt-in, a hub's only */
  let failMid = null;
  if (stateMode || operatorMode) {
    const state = flowEdgesAt(sp, t);
    state.edges.forEach((entry) => {
      const f = entry.fraction, ia = entry.fromIndex, ib = entry.toIndex;
      if (!(f > 0) || ia < 0 || ib < 0 || ia === ib || !lay.cells[ia] || !lay.cells[ib]) return;
      if (operatorMode) {
        // Arithmetic uses the terms' shared centerline, not a transfer arrow's bowed path.
        const mid = { x: (lay.cells[ia].x + lay.cells[ib].x) / 2, y: (lay.cells[ia].y + lay.cells[ib].y) / 2 };
        const size = (phone ? FLOW.PHONE_OPERATOR_SIZE : FLOW.OPERATOR_SIZE) * lay.k;
        const style = "fill:none;stroke:" + (phone ? "#25313C" : "#F5B72E") + ";stroke-width:5;stroke-linecap:round;stroke-linejoin:round";
        const p = el("path", "flowoperator", g, { d: "M" + (mid.x - size / 2).toFixed(2) + " " + mid.y.toFixed(2)
          + " L" + (mid.x + size / 2).toFixed(2) + " " + mid.y.toFixed(2), style });
        drawOn(p, f);
        return;
      }
      const pts = flowEdgePts(lay, ia, ib);   /* FLOW.BOW off a ring: the same anchors and fit as before */
      if (entry.phase === "retract") {
        drawOn(el("path", "flowarrow", g, pathAttrs(clothoidPath(pts.slice().reverse()))), f);
        const head = flowHead(pts);
        if (head) {
          const hp = el("path", "flowarrow", g, Object.assign(pathAttrs(head), { opacity: f.toFixed(3) }));
          drawOn(hp, 1);
        }
      } else {
        drawOn(el("path", "flowarrow", g, pathAttrs(clothoidPath(pts))), Math.min(1, f / FLOW.HEAD_F));
        if (f > FLOW.HEAD_F) drawOn(el("path", "flowarrow", g, pathAttrs(flowHead(pts))), (f - FLOW.HEAD_F) / (1 - FLOW.HEAD_F));
      }
    });
  } else {
    flowEdgeIndex(sp).forEach(([ia, ib], j) => {
      if (ia < 0 || ib < 0 || ia === ib) return;
      const f = flowEdgeF(sp, j, t);
      if (f <= 0) return;
      const pts = flowEdgePts(lay, ia, ib);   /* FLOW.BOW off a ring: the same anchors and fit as before */
      if (failCut && j === failCut.j) {       /* P71 T17: from its word the failed link reddens and severs */
        failMid = flowFailSplit(pts, failCut.u).mid;
        paintFlowFailedEdge(el, g, pts, failCut, phone, drawOn);
        return;
      }
      if (seal) {   /* R26-384: DOM's spoke - thin straight dashes, drawn out along the spoke, no head */
        const style = "fill:none;stroke:" + FLOW.SPOKE_INK + ";stroke-width:" + (FLOW.SPOKE_W * lay.k).toFixed(2) + ";stroke-linecap:butt";
        for (const [a, b] of flowSealDashes(pts, f, lay.k)) el("path", "flowspoke", g, { d: "M" + a.x.toFixed(2) + " " + a.y.toFixed(2) + " L" + b.x.toFixed(2) + " " + b.y.toFixed(2), style });
        return;
      }
      drawOn(el("path", "flowarrow", g, pathAttrs(clothoidPath(pts))), Math.min(1, f / FLOW.HEAD_F));
      if (f > FLOW.HEAD_F) drawOn(el("path", "flowarrow", g, pathAttrs(flowHead(pts))), (f - FLOW.HEAD_F) / (1 - FLOW.HEAD_F));
    });
  }
  /* P71 T11: the tokens ride the arrows, under the cards so they leave and enter beneath them */
  if (sp.tokens && !stateMode && !operatorMode) paintFlowTokens(ctx, g, lay, phone);
  /* the cards */
  nodes.forEach((node, i) => {
    const st = flowNodeAt(sp, i, t);
    if (st.u <= 0 || st.alpha <= 0) return;
    const pose = flowPose(st.u), c = lay.cells[i];
    const ix = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 907 + i)) : { scale: 1, dx: 0, dy: 0 };
    const s = pose.scale * ix.scale * lay.k;
    const ng = el("g", "", g, { opacity: (pose.fade * st.alpha).toFixed(3),
                                transform: "translate(" + (c.x + ix.dx).toFixed(1) + " " + (c.y + (pose.dy + ix.dy) * lay.k).toFixed(1) + ") scale(" + s.toFixed(4) + ")" });
    const h = CHIP.SIZE / 2, sealHub = seal && i === 0;   /* R26-384: the seal hub stands with no card, its emblem larger and glowing */
    const cardAttrs = { x: (-h).toFixed(1), y: (-h).toFixed(1), width: CHIP.SIZE, height: CHIP.SIZE, rx: CHIP.RX };
    if (phone) cardAttrs.style = "fill:#F4E6C7;stroke:#25313C;stroke-width:3";
    if (!sealHub) el("rect", "chipcard", ng, cardAttrs);
    const geo = chipGeometry(A ? A["icon:" + st.icon] : null);
    if (geo) {
      const vb = geo.vb || [0, 0, 24, 24], GL = sealHub ? CHIP.SIZE * FLOW.SEAL_K : CHIP.GLYPH, gk = GL / Math.max(vb[2] || 1, vb[3] || 1);
      const glyphAttrs = { transform: "translate(" + (-GL / 2).toFixed(1) + " " + (-GL / 2).toFixed(1) + ") scale(" + gk.toFixed(4) + ") translate(" + (-vb[0]) + " " + (-vb[1]) + ")" };
      if (sealHub) glyphAttrs.style = "fill:none;stroke:" + FLOW.SEAL_INK + ";stroke-width:" + (2 * Math.max(vb[2] || 1, vb[3] || 1) / 24).toFixed(2)
        + ";stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 " + (FLOW.SEAL_GLOW * GL / gk).toFixed(2) + "px " + flowInkA(FLOW.SEAL_INK, FLOW.SEAL_GLOW_A) + ")";
      if (phone) glyphAttrs.style = "fill:none;stroke:#25313C;stroke-width:2;stroke-linecap:round;stroke-linejoin:round";
      const gg = el("g", "chipglyph", ng, glyphAttrs);
      geo.el.forEach((q) => el(q.t, "", gg, phone ? Object.assign({}, q.a, { style: "fill:none;stroke:#25313C;stroke-width:2;stroke-linecap:round;stroke-linejoin:round" }) : q.a));   /* the sourced geometry verbatim */
    }
    if (st.label) {
      const labelDy = lay.labelDy || CHIP.LABEL_DY;
      const attrs = { x: 0, y: (h + labelDy).toFixed(1) };
      if (phone) attrs.style = "font-size:" + FLOW.PHONE_LABEL_SIZE + "px;font-weight:700;font-family:Inter,Arial,sans-serif;fill:#25313C;paint-order:stroke;stroke:#F4E6C7;stroke-width:5px";
      const lab = el("text", "chiplab", ng, attrs), lines = phone ? String(st.label).split(/\r?\n/) : [st.label];
      if (phone && lines.length > 1) {
        const lineH = lay.labelLineH || FLOW.PHONE_LABEL_LINE_H;
        lines.forEach((line, j) => { const ts = el("tspan", "", lab, { x: 0, dy: j ? lineH : 0 }); ts.textContent = line; });
      } else lab.textContent = st.label;
    }
  });
  /* P71 T17: the failed link's disc and X, over the world */
  if (failCut && failMid) paintFlowFail(el, g, failMid, failCut, lay, drawOn);
  /* the year stamp in the box's corner */
  if (sp.tag && t >= C.tagAt) {
    const u = flow01((t - C.tagAt) / FLOW.TAG_S), e = springPop(u);
    const tagSize = phone ? FLOW.PHONE_TAG_SIZE : FLOW.TAG_SIZE, tagPad = phone ? FLOW.PHONE_TAG_PAD : FLOW.TAG_PAD;
    const attrs = { x: (box.x + box.w - tagPad).toFixed(1),
      y: (box.y + tagPad + tagSize * (1.4 - 0.4 * e)).toFixed(1),
      opacity: flow01(u / 0.4).toFixed(3), style: "font-size:" + tagSize + "px" };
    if (phone) attrs.style += ";font-weight:700;font-family:Inter,Arial,sans-serif;fill:#25313C;paint-order:stroke;stroke:#F4E6C7;stroke-width:6px";
    const tx = el("text", "flowtag", g, attrs);
    tx.textContent = sp.tag;
  }
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
   import this file for the math above without the template's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.flow = paintFlow;
